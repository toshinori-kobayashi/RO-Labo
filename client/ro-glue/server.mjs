/**
 * ro-glue/server.mjs
 *
 * One local process for the roBrowserLegacy prototype:
 *   1. static file server        -> serves the roBrowserLegacy web build (Config.local.js etc.)
 *   2. GRF asset server (/client/) -> serves files straight out of locally owned GRFs
 *                                    (GRF 0x200 / 0x300, standard Gravity DES entry flags) plus
 *                                    loose folders (data/, System/, BGM/, AI/) read-only
 *   3. WebSocket -> TCP relay     -> ws://host:port/<ip>:<port> as roBrowserLegacy expects
 *                                    (allow-listed targets only)
 *
 * DES entry decoding reuses roBrowserLegacy's own GPL-3.0 module (src/Loaders/GameFileDecrypt.js).
 * Nothing is written to the GRFs or the original client folder; everything is opened read-only.
 *
 * Usage:
 *   node server.mjs --port 8000 --static <dir> --grf <file.grf> [--grf ...] --loose <dir> [--loose ...]
 *                   --allow 54.65.172.5:6900,54.65.172.5:6121,54.65.172.5:5121
 *                   [--decrypt <path to GameFileDecrypt.js>]
 */

import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import net from 'node:net';
import zlib from 'node:zlib';
import { pathToFileURL } from 'node:url';
import { WebSocketServer } from 'ws';

// ---------------------------------------------------------------- args
const args = process.argv.slice(2);
const opt = { port: 8000, static: null, grf: [], loose: [], allow: [], decrypt: null, verbose: false };
for (let i = 0; i < args.length; i++) {
    const a = args[i];
    const v = () => args[++i];
    if (a === '--port') opt.port = parseInt(v(), 10);
    else if (a === '--static') opt.static = v();
    else if (a === '--grf') opt.grf.push(v());
    else if (a === '--loose') opt.loose.push(v());
    else if (a === '--allow') opt.allow.push(...v().split(',').map(s => s.trim()).filter(Boolean));
    else if (a === '--decrypt') opt.decrypt = v();
    else if (a === '--verbose') opt.verbose = true;
    else if (a === '--dump-rx') opt.dumpRx = v();   // hex dump of SERVER->CLIENT bytes only (never client->server: no credentials)
}
if (!opt.static) { console.error('--static <dir> is required'); process.exit(2); }
const allowSet = new Set(opt.allow);

const decryptPath = opt.decrypt || path.resolve('..', 'roBrowserLegacy-src', 'src', 'Loaders', 'GameFileDecrypt.js');
const { default: GameFileDecrypt } = await import(pathToFileURL(decryptPath).href);

// ---------------------------------------------------------------- GRF
const SIG_MAGIC = 'Master of Magic';
const SIG_EH3 = 'Event Horizon';
const TYPE_FILE = 0x01;
const TYPE_ENCRYPT_MIXED = 0x02;
const TYPE_ENCRYPT_HEADER = 0x04;
const SKIP_EXTENSIONS = /\.(gnd|gat|act|str)$/i;   // same as roBrowserLegacy GameFile.js

function asciiLower(s) {
    // ASCII-only lowercase so that bytes >= 0x80 (EUC-KR / CP932) are never altered
    return s.replace(/[A-Z]/g, c => c.toLowerCase());
}

let eucDecoder = null;
try { eucDecoder = new TextDecoder('euc-kr'); } catch { eucDecoder = null; }

class Grf {
    constructor(file) {
        this.path = file;
        this.fd = fs.openSync(file, 'r');
        this.size = fs.fstatSync(this.fd).size;
        this.byLatin1 = new Map();   // key: raw bytes as latin1 (ascii-lowercased) -> entry
        this.byEucKr = new Map();    // key: bytes decoded as EUC-KR -> entry
        this.names = [];             // latin1 names (for regex search)
        this.#load();
    }

    #read(pos, len) {
        const buf = Buffer.alloc(len);
        let done = 0;
        while (done < len) {
            const n = fs.readSync(this.fd, buf, done, len - done, pos + done);
            if (n <= 0) break;
            done += n;
        }
        return buf;
    }

    #load() {
        const h = this.#read(0, 46);
        let sig = h.toString('latin1', 0, 15);
        const nul = sig.indexOf('\0');
        if (nul >= 0) sig = sig.slice(0, nul);
        if (sig !== SIG_MAGIC && sig !== SIG_EH3) throw new Error(`bad GRF signature '${sig}'`);
        const version = h.readUInt32LE(42);
        let fileCount, tableStart;
        if (version === 0x300) {
            const tableOffset = Number(h.readBigUInt64LE(30));
            fileCount = h.readUInt32LE(38);
            tableStart = tableOffset + 46 + 4;
        } else if (version === 0x200) {
            const tableOffset = h.readUInt32LE(30);
            const skip = h.readUInt32LE(34);
            fileCount = h.readUInt32LE(38) - skip - 7;
            tableStart = tableOffset + 46;
        } else {
            throw new Error(`unsupported GRF version 0x${version.toString(16)}`);
        }
        this.version = version;
        const t = this.#read(tableStart, 8);
        const packSize = t.readUInt32LE(0);
        const realSize = t.readUInt32LE(4);
        const packed = this.#read(tableStart + 8, packSize);
        const table = zlib.inflateSync(packed);
        if (table.length !== realSize) throw new Error('table size mismatch');

        let pos = 0;
        for (let i = 0; i < fileCount; i++) {
            const start = pos;
            while (table[pos] !== 0) pos++;
            const nameBytes = table.subarray(start, pos);
            pos++;
            const e = {
                packSize: table.readUInt32LE(pos),
                lengthAligned: table.readUInt32LE(pos + 4),
                realSize: table.readUInt32LE(pos + 8),
                type: table[pos + 12],
                offset: 0
            };
            pos += 13;
            if (version === 0x300) { e.offset = Number(table.readBigUInt64LE(pos)); pos += 8; }
            else { e.offset = table.readUInt32LE(pos); pos += 4; }

            if (!(e.type & TYPE_FILE)) continue;
            const latin1 = nameBytes.toString('latin1');
            this.names.push(latin1);
            this.byLatin1.set(asciiLower(latin1), e);
            if (eucDecoder) {
                try { this.byEucKr.set(asciiLower(eucDecoder.decode(nameBytes)), e); } catch { /* ignore */ }
            }
        }
    }

    find(latin1Key, unicodeKey) {
        return this.byLatin1.get(latin1Key) || (unicodeKey ? this.byEucKr.get(unicodeKey) : undefined) || null;
    }

    extract(e, name) {
        const data = new Uint8Array(this.#read(e.offset + 46, e.lengthAligned));
        if (e.type & TYPE_ENCRYPT_MIXED) {
            if (SKIP_EXTENSIONS.test(name)) GameFileDecrypt.decodeHeader(data, e.lengthAligned);
            else GameFileDecrypt.decodeFull(data, e.lengthAligned, e.packSize);
        } else if (e.type & TYPE_ENCRYPT_HEADER) {
            GameFileDecrypt.decodeHeader(data, e.lengthAligned);
        }
        if (data[0] !== 0x78) {
            throw new Error(`entry is not zlib after decode (first byte 0x${data[0].toString(16)})`);
        }
        return zlib.inflateSync(Buffer.from(data.buffer, data.byteOffset, e.packSize));
    }
}

const grfs = [];
for (const g of opt.grf) {
    const t0 = Date.now();
    try {
        const grf = new Grf(g);
        grfs.push(grf);
        console.log(`[grf] loaded ${g} (v0x${grf.version.toString(16)}, ${grf.byLatin1.size} files, ${Date.now() - t0} ms)`);
    } catch (err) {
        console.error(`[grf] FAILED ${g}: ${err.message}`);
    }
}

// windows-1252 0x80..0x9F block reverse map (roBrowser decodes GRF names as windows-1252 in the worker)
const CP1252_REV = new Map([
    [0x20AC, 0x80], [0x201A, 0x82], [0x0192, 0x83], [0x201E, 0x84], [0x2026, 0x85], [0x2020, 0x86], [0x2021, 0x87],
    [0x02C6, 0x88], [0x2030, 0x89], [0x0160, 0x8A], [0x2039, 0x8B], [0x0152, 0x8C], [0x017D, 0x8E], [0x2018, 0x91],
    [0x2019, 0x92], [0x201C, 0x93], [0x201D, 0x94], [0x2022, 0x95], [0x2013, 0x96], [0x2014, 0x97], [0x02DC, 0x98],
    [0x2122, 0x99], [0x0161, 0x9A], [0x203A, 0x9B], [0x0153, 0x9C], [0x017E, 0x9E], [0x0178, 0x9F]
]);

function toRawBytes(unicodeStr) {
    // Interpret the request string as "bytes that were decoded as windows-1252/latin1" -> original bytes
    const bytes = [];
    for (const ch of unicodeStr) {
        const cp = ch.codePointAt(0);
        if (cp < 0x100) bytes.push(cp);
        else if (CP1252_REV.has(cp)) bytes.push(CP1252_REV.get(cp));
        else return null;
    }
    return Buffer.from(bytes);
}
function toLatin1Key(unicodeStr) {
    const b = toRawBytes(unicodeStr);
    return b ? asciiLower(b.toString('latin1')) : null;
}

// ---------------------------------------------------------------- MIME
const MIME = {
    '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8',
    '.css': 'text/css; charset=utf-8', '.json': 'application/json', '.webmanifest': 'application/manifest+json',
    '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.bmp': 'image/bmp',
    '.tga': 'image/x-tga', '.svg': 'image/svg+xml', '.ico': 'image/x-icon',
    '.wav': 'audio/wav', '.mp3': 'audio/mpeg', '.ogg': 'audio/ogg',
    '.xml': 'text/xml; charset=ISO-8859-1', '.txt': 'text/plain; charset=ISO-8859-1', '.ini': 'text/plain; charset=ISO-8859-1',
    '.lua': 'application/octet-stream', '.lub': 'application/octet-stream',
    '.wasm': 'application/wasm'
};
function mimeOf(name) { return MIME[path.extname(name).toLowerCase()] || 'application/octet-stream'; }

// ---------------------------------------------------------------- asset lookup
function safeJoin(root, rel) {
    const p = path.normalize(path.join(root, rel));
    if (!p.toLowerCase().startsWith(path.normalize(root).toLowerCase())) return null;
    return p;
}

function getAsset(relUnicode) {
    // relUnicode: "data/texture/.../x.bmp" (forward slashes, already URL-decoded, UTF-8 string)
    const win = relUnicode.replace(/\//g, '\\');
    const latin1Key = toLatin1Key(win);
    const unicodeKey = asciiLower(win);

    // the browser sends windows-1252-decoded GRF names; on disk (NTFS) Korean folders are real Unicode,
    // so also try the EUC-KR interpretation of the same bytes for loose lookups
    const candidates = [win];
    const rawBytes = toRawBytes(win);
    if (rawBytes && eucDecoder) {
        try {
            const eucPath = eucDecoder.decode(rawBytes);
            if (eucPath !== win) candidates.push(eucPath);
        } catch { /* ignore */ }
    }

    // 1. loose folders (first hit wins)
    for (const root of opt.loose) {
        for (const cand of candidates) {
            const p = safeJoin(root, cand);
            if (p && fs.existsSync(p) && fs.statSync(p).isFile()) {
                return { buf: fs.readFileSync(p), source: `loose:${root}` };
            }
        }
    }

    // 2. GRFs in order
    for (const grf of grfs) {
        const e = grf.find(latin1Key, unicodeKey);
        if (e) {
            return { buf: grf.extract(e, win), source: `grf:${path.basename(grf.path)}` };
        }
    }
    return null;
}

function searchAssets(regexSource) {
    let re;
    try { re = new RegExp(regexSource, 'gi'); } catch { return []; }
    const out = new Set();
    for (const grf of grfs) {
        for (const n of grf.names) {
            if (re.test(n)) out.add(n);
            re.lastIndex = 0;
        }
    }
    return [...out];
}

// ---------------------------------------------------------------- HTTP
const stats = { hits: 0, misses: 0 };
const missLog = new Map();

function send(res, code, body, type, extra = {}) {
    res.writeHead(code, { 'Content-Type': type, 'Content-Length': Buffer.byteLength(body), 'Cache-Control': 'no-cache', 'Access-Control-Allow-Origin': '*', ...extra });
    res.end(body);
}

function readBody(req) {
    return new Promise(resolve => { const c = []; req.on('data', d => c.push(d)); req.on('end', () => resolve(Buffer.concat(c))); });
}

const server = http.createServer(async (req, res) => {
    try {
        const url = new URL(req.url, 'http://localhost');
        let pathname;
        try {
            pathname = decodeURIComponent(url.pathname);
        } catch {
            // raw (non UTF-8) percent-escapes, e.g. EUC-KR bytes -> treat bytes as latin1 chars
            pathname = url.pathname.replace(/%([0-9a-fA-F]{2})/g, (_, h) => String.fromCharCode(parseInt(h, 16)));
        }

        // ---- asset endpoint
        if (pathname === '/client' || pathname.startsWith('/client/')) {
            const rel = pathname.replace(/^\/client\/?/, '');

            if (req.method === 'POST' && (rel === '' || rel === 'batch')) {
                const body = await readBody(req);
                if (rel === 'batch') {
                    let files = [];
                    try { files = JSON.parse(body.toString('utf8')).files || []; } catch { /* ignore */ }
                    const out = {};
                    for (const f of files) {
                        try { const a = getAsset(f); if (a) { out[f] = a.buf.toString('base64'); stats.hits++; } else { stats.misses++; } } catch { stats.misses++; }
                    }
                    return send(res, 200, JSON.stringify(out), 'application/json');
                }
                const params = new URLSearchParams(body.toString('latin1'));
                const filter = params.get('filter') || '';
                return send(res, 200, searchAssets(filter).join('\n'), 'text/plain; charset=ISO-8859-1');
            }

            if (!rel) return send(res, 400, 'missing path', 'text/plain');
            let asset = null;
            try { asset = getAsset(rel); } catch (err) { console.error(`[asset] extract error ${rel}: ${err.message}`); return send(res, 500, err.message, 'text/plain'); }
            if (!asset) {
                stats.misses++;
                missLog.set(rel, (missLog.get(rel) || 0) + 1);
                if (opt.verbose || missLog.get(rel) === 1) console.log(`[asset] 404 ${rel}`);
                return send(res, 404, 'not found', 'text/plain');
            }
            stats.hits++;
            if (opt.verbose) console.log(`[asset] 200 ${rel} (${asset.source}, ${asset.buf.length} B)`);
            return send(res, 200, asset.buf, mimeOf(rel));
        }

        // ---- status
        if (pathname === '/__status') {
            return send(res, 200, JSON.stringify({ stats, grfs: grfs.map(g => ({ path: g.path, version: g.version, files: g.byLatin1.size })), misses: [...missLog.entries()].slice(0, 200) }, null, 2), 'application/json');
        }

        // ---- static
        if (pathname === '/') pathname = '/api.html';
        const file = safeJoin(opt.static, pathname);
        if (!file || !fs.existsSync(file) || !fs.statSync(file).isFile()) return send(res, 404, 'not found', 'text/plain');
        return send(res, 200, fs.readFileSync(file), mimeOf(file));
    } catch (err) {
        console.error('[http] error', err);
        send(res, 500, 'internal error', 'text/plain');
    }
});

// ---------------------------------------------------------------- WebSocket -> TCP relay
const wss = new WebSocketServer({ noServer: true });
server.on('upgrade', (req, socket, head) => {
    const m = (req.url || '').match(/^\/([^/:]+):(\d+)\/?$/);
    const target = m ? `${m[1]}:${m[2]}` : null;
    if (!target || (allowSet.size && !allowSet.has(target))) {
        console.warn(`[ws] refused target ${req.url}`);
        socket.write('HTTP/1.1 403 Forbidden\r\n\r\n');
        socket.destroy();
        return;
    }
    wss.handleUpgrade(req, socket, head, ws => {
        const tcp = net.connect(parseInt(m[2], 10), m[1]);
        let rx = 0, tx = 0;
        console.log(`[ws] -> tcp ${target} connecting`);
        tcp.on('connect', () => console.log(`[ws] -> tcp ${target} connected`));
        tcp.on('data', d => {
            rx += d.length;
            if (opt.dumpRx) {
                // raw bytes as received; NO transformation is applied to the relayed payload itself
                const hex = d.toString('hex').replace(/(..)/g, '$1 ').trim();
                const latin1 = d.toString('latin1').replace(/[^\x20-\x7e]/g, '.');
                fs.appendFileSync(opt.dumpRx, `${new Date().toISOString()} ${target} len=${d.length}\n${hex}\n${latin1}\n\n`);
            }
            if (ws.readyState === ws.OPEN) ws.send(d);
        });
        tcp.on('close', () => { console.log(`[ws] tcp ${target} closed (rx=${rx} tx=${tx})`); try { ws.close(); } catch { /* ignore */ } });
        tcp.on('error', err => { console.warn(`[ws] tcp ${target} error ${err.message}`); try { ws.close(); } catch { /* ignore */ } });
        ws.on('message', d => { const b = Buffer.isBuffer(d) ? d : Buffer.from(d); tx += b.length; tcp.write(b); });
        ws.on('close', () => { console.log(`[ws] client closed (${target})`); tcp.destroy(); });
        ws.on('error', () => tcp.destroy());
    });
});

server.listen(opt.port, '127.0.0.1', () => {
    console.log(`[glue] listening on http://127.0.0.1:${opt.port}/  static=${opt.static}`);
    console.log(`[glue] loose roots: ${opt.loose.join(' | ') || '(none)'}`);
    console.log(`[glue] ws relay allow-list: ${[...allowSet].join(', ') || '(any)'}`);
});

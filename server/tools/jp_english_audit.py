#!/usr/bin/env python3
"""翻訳済み NPC スクリプトに残っている「英語表示文字列」を機械的に洗い出す。

jp_structure_check.py が「構造が壊れていないか」を見るのに対し、こちらは
「プレイヤーに見える文字列が日本語になっているか」だけを見る。
訳し漏れの候補を挙げるだけで、ファイルは一切変更しない。

使い方:
    tools/jp_english_audit.py                             # MANIFEST 全件
    tools/jp_english_audit.py --file app/rathena/overlay-utf8/npc/custom/jp/...
    tools/jp_english_audit.py --out docs/jp-english-audit-20260924.tsv
    tools/jp_english_audit.py --strict                    # 許容リストを無視して全件

対象にする文字列（プレイヤーに直接表示されるものだけ）:
    mes / select / prompt / menu の選択肢 / next の引数 / dispbottom /
    message の第 2 引数 / announce の第 1 引数 / mapannounce の第 2 引数 /
    npctalk / unittalk のメッセージ / showscript / waitingroom のタイトル
対象にしないもの:
    callfunc / callsub に渡す文字列（関数側で判断する）、マップ名・イベント名・
    NPC 名などの識別子、比較値、コメント、ヘッダ行。

判定（色コード ^RRGGBB と %d / %s 等を除去したあと）:
    a) 英字 3 文字以上の単語が 2 語以上連続している
    b) 英字のみの単語が 8 文字以上ある
    のどちらかに当たると「英語残り候補」。

許容リスト docs/jp-english-allowlist.tsv（TAB 区切り 3 列）:
    <file><TAB><pattern><TAB><reason>
      file    … 対象ファイル。空 または * なら全ファイル。
                overlay 相対パス / ファイル名のどちらにも glob で当てる。
      pattern … 正規表現。マッチした部分を判定前に取り除く（=許容する）。
      reason  … 許容する理由（レポート用。判定には使わない）。
"""

import argparse
import fnmatch
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jp_common import (  # noqa: E402
    MANIFEST_PATH, OVERLAY_DIR, REPO_ROOT,
    ToolError, parse_manifest, die,
)
from jp_structure_check import (  # noqa: E402
    COLOR_CODE_RE, FORMAT_SPEC_RE, MENU_COMMANDS, tokenize,
)

# ---------------------------------------------------------------- 定数

ALLOWLIST_PATH = os.path.join(REPO_ROOT, "docs", "jp-english-allowlist.tsv")

#: 表示文字列を取る引数の位置。None は「全引数」、tuple は該当する引数番号だけ。
#: （引数番号は 0 始まり。`;` で終わる非括弧形式でも同じ数え方）
VISIBLE_COMMANDS = {
    "mes": None,
    "next": None,           # 引数は取らないが、あれば拾う
    "select": None,
    "prompt": None,
    "menu": "even",         # "選択肢",ラベル,"選択肢",ラベル … の偶数番
    "dispbottom": (0,),
    "message": (1,),        # message "<player>","<message>"
    "announce": (0,),
    "mapannounce": (1,),    # 第 1 引数はマップ名なので除外
    "npctalk": (0,),
    "unittalk": (1,),       # unittalk <GID>,"<message>"
    "showscript": (0,),
    "waitingroom": (0,),
}

#: 中の文字列を一切対象にしないコマンド（関数側で判断する）
OPAQUE_CALLS = frozenset(["callfunc", "callsub"])

#: 選択肢を `:` で割るコマンド
SPLIT_BY_COLON = MENU_COMMANDS

#: ASCII 印字可能文字の連なり（非 ASCII で分断する）
ASCII_SEG_RE = re.compile(r"[\x20-\x7e]+")

#: 英単語（アポストロフィ・ハイフンを内部に含んでよい）
WORD_RE = re.compile(r"[A-Za-z]+(?:['’\-][A-Za-z]+)*")

#: `\xHH` 形式のバイトエスケープ（韓国語ファイル名など）
HEX_ESCAPE_RE = re.compile(r"\\x[0-9A-Fa-f]{2}")

MIN_WORD_LEN = 3        # 「単語」とみなす英字数
MIN_RUN_WORDS = 2       # 連続する単語数
MIN_SOLO_LEN = 8        # 単独でも候補にする英字数


# ---------------------------------------------------------------- 許容リスト

class AllowRule(object):
    __slots__ = ("lineno", "file_pat", "pattern", "regex", "reason", "hits")

    def __init__(self, lineno, file_pat, pattern, reason):
        self.lineno = lineno
        self.file_pat = file_pat
        self.pattern = pattern
        self.reason = reason
        self.hits = 0
        try:
            self.regex = re.compile(pattern)
        except re.error as exc:
            raise ToolError("許容リスト %s:%d: 正規表現が不正です: %r (%s)"
                            % (ALLOWLIST_PATH, lineno, pattern, exc))

    def applies_to(self, relpath):
        if not self.file_pat or self.file_pat == "*":
            return True
        base = os.path.basename(relpath)
        return (fnmatch.fnmatch(relpath, self.file_pat)
                or fnmatch.fnmatch(base, self.file_pat)
                or self.file_pat in relpath)


def load_allowlist(path=ALLOWLIST_PATH):
    """許容リストを読む。ファイルが無ければ空リスト（警告は呼び出し側で）。"""
    if not os.path.isfile(path):
        return None
    rules = []
    with open(path, encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, 1):
            line = raw.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            fields = line.split("\t")
            if len(fields) < 2:
                raise ToolError("許容リスト %s:%d: TAB 区切り 2〜3 列である必要があります: %r"
                                % (path, lineno, line))
            file_pat = fields[0].strip()
            pattern = fields[1]
            reason = fields[2].strip() if len(fields) > 2 else ""
            rules.append(AllowRule(lineno, file_pat, pattern, reason))
    return rules


# ---------------------------------------------------------------- 文字列の抽出

def _call_args(tokens, i):
    """tokens[i] のコマンドの引数を [[(token index, 入れ子の深さ), ...], ...] で返す。

    戻り値: (args, end_index)
      括弧形式 `cmd(a,b)` と非括弧形式 `cmd a,b;` の両方を扱う。
      深さ 0 は「そのコマンドの引数そのもの」。`mes "…"+getmapusers("arena_room")`
      の "arena_room" のように入れ子の関数へ渡る文字列は深さ 1 以上になる。
    """
    n = len(tokens)
    j = i + 1
    paren = False
    if j < n and tokens[j].kind == "op" and tokens[j].value == "(":
        paren = True
        j += 1
    args = [[]]
    depth = 0
    while j < n:
        t = tokens[j]
        if t.kind == "op":
            if t.value in ("(", "[", "{"):
                args[-1].append((j, depth))
                depth += 1
                j += 1
                continue
            if t.value in (")", "]", "}"):
                if depth == 0:
                    if paren and t.value == ")":
                        j += 1
                    break
                depth -= 1
                args[-1].append((j, depth))
                j += 1
                continue
            if t.value == "," and depth == 0:
                args.append([])
                j += 1
                continue
            if t.value == ";" and depth == 0:
                break
        args[-1].append((j, depth))
        j += 1
    if len(args) == 1 and not args[0]:
        args = []
    return args, j


def _opaque_indices(tokens):
    """callfunc / callsub の呼び出しに含まれる文字列トークンの添字集合。"""
    marked = set()
    for i, t in enumerate(tokens):
        if t.kind != "word" or t.value not in OPAQUE_CALLS:
            continue
        args, _end = _call_args(tokens, i)
        for arg in args:
            for k, _d in arg:
                if tokens[k].kind == "str":
                    marked.add(k)
    return marked


class Hit(object):
    __slots__ = ("line", "command", "text", "raw")

    def __init__(self, line, command, text, raw):
        self.line = line
        self.command = command
        self.text = text      # 判定にかける単位（選択肢は 1 項目ずつ）
        self.raw = raw        # 元の文字列リテラル


def extract_visible(tokens):
    """プレイヤーに表示される文字列を (line, command, text, raw) で列挙する。"""
    opaque = _opaque_indices(tokens)
    out = []
    n = len(tokens)
    for i, t in enumerate(tokens):
        if t.kind != "word" or t.value not in VISIBLE_COMMANDS:
            continue
        # 変数名や関数定義ではなくコマンド呼び出しであることの最低限の確認
        if i + 1 >= n:
            continue
        nxt = tokens[i + 1]
        if nxt.kind == "op" and nxt.value in (":", "::", "."):
            continue
        spec = VISIBLE_COMMANDS[t.value]
        args, _end = _call_args(tokens, i)
        for idx, arg in enumerate(args):
            if spec == "even":
                if idx % 2 != 0:
                    continue
            elif isinstance(spec, tuple) and idx not in spec:
                continue
            for k, d in arg:
                tok = tokens[k]
                if tok.kind != "str" or k in opaque:
                    continue
                if d > 0:
                    # getmapusers("arena_room") のような入れ子関数の引数は
                    # 識別子であることが多いので対象外
                    continue
                raw = tok.value
                if t.value in SPLIT_BY_COLON:
                    parts = raw.split(":")
                else:
                    parts = [raw]
                for part in parts:
                    if part.strip():
                        out.append(Hit(tok.line, t.value, part, raw))
    out.sort(key=lambda h: (h.line, h.command))
    return out


# ---------------------------------------------------------------- 判定

def clean(text):
    """色コード・書式指定子・エスケープを落として素の見た目に近づける。"""
    s = HEX_ESCAPE_RE.sub(" ", text)
    s = COLOR_CODE_RE.sub(" ", s)
    s = FORMAT_SPEC_RE.sub(" ", s)
    s = re.sub(r"\\[nrt]", " ", s)
    s = re.sub(r"\\(.)", r"\1", s)
    return s


def apply_allowlist(text, rules, relpath, counters=None):
    """許容リストにマッチした部分を空白へ置き換える。"""
    s = text
    for rule in rules:
        if not rule.applies_to(relpath):
            continue
        s, cnt = rule.regex.subn(" ", s)
        if cnt:
            rule.hits += cnt
            if counters is not None:
                counters.append(rule)
    return s


def detect(text):
    """英語残り候補なら (reason_guess, 抜き出した英語) を返す。そうでなければ None。"""
    best = None
    for seg in ASCII_SEG_RE.findall(text):
        words = [m for m in WORD_RE.finditer(seg)]
        # a) 3 文字以上の単語が 2 語以上連続
        run = []
        for m in words:
            if len(m.group().replace("-", "").replace("'", "")) >= MIN_WORD_LEN:
                run.append(m)
                if len(run) >= MIN_RUN_WORDS:
                    frag = seg[run[0].start():run[-1].end()]
                    return ("英単語%d語以上の連続" % MIN_RUN_WORDS, frag.strip())
            else:
                run = []
        # b) 英字のみで 8 文字以上
        for m in words:
            w = m.group()
            if len(w) >= MIN_SOLO_LEN and w.isalpha():
                if best is None:
                    best = ("英字%d文字以上の単語" % MIN_SOLO_LEN, w)
    return best


# ---------------------------------------------------------------- 監査本体

class Candidate(object):
    __slots__ = ("relpath", "line", "command", "text", "reason", "fragment")

    def __init__(self, relpath, line, command, text, reason, fragment):
        self.relpath = relpath
        self.line = line
        self.command = command
        self.text = text
        self.reason = reason
        self.fragment = fragment

    def row(self):
        return "\t".join([
            self.relpath,
            str(self.line),
            self.command,
            self.text.replace("\t", " "),
            "%s: %s" % (self.reason, self.fragment),
        ])


def audit_file(abspath, relpath, rules, strict):
    """1 ファイルを監査して Candidate のリストを返す。"""
    with open(abspath, encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    tokens, _headers = tokenize(text)
    out = []
    for hit in extract_visible(tokens):
        s = clean(hit.text)
        if not strict:
            s = apply_allowlist(s, rules, relpath)
        found = detect(s)
        if found:
            out.append(Candidate(relpath, hit.line, hit.command,
                                 hit.text, found[0], found[1]))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="翻訳済み NPC スクリプトに残る英語表示文字列の監査（読むだけ・変更しない）")
    ap.add_argument("--manifest", default=MANIFEST_PATH, help="MANIFEST.tsv のパス")
    ap.add_argument("--file", default=None, help="単体監査: 翻訳版ファイル")
    ap.add_argument("--allowlist", default=ALLOWLIST_PATH, help="許容リスト TSV")
    ap.add_argument("--out", default=None, help="候補一覧を TSV で保存するパス")
    ap.add_argument("--strict", action="store_true", help="許容リストを無視して全件出す")
    ap.add_argument("--quiet", action="store_true", help="候補の一覧を標準出力に出さない")
    ap.add_argument("--unused-allow", action="store_true",
                    help="一度もマッチしなかった許容リスト行を表示する")
    args = ap.parse_args(argv)

    try:
        rules = load_allowlist(args.allowlist)
    except ToolError as exc:
        die("jp_english_audit: %s" % exc)
    if rules is None:
        if not args.strict:
            die("jp_english_audit: 許容リストがありません: %s" % args.allowlist)
        rules = []

    targets = []   # (abspath, relpath)
    if args.file:
        abspath = os.path.abspath(args.file)
        rel = abspath
        for base in (OVERLAY_DIR, REPO_ROOT):
            try:
                r = os.path.relpath(abspath, base)
            except ValueError:
                continue
            if not r.startswith(".."):
                rel = r
                break
        targets.append((abspath, rel))
    else:
        try:
            entries = parse_manifest(args.manifest)
        except ToolError as exc:
            die("jp_english_audit: %s" % exc)
        for ent in entries:
            targets.append((ent.translated_abspath, ent.translated))

    cands = []
    missing = []
    for abspath, rel in targets:
        if not os.path.isfile(abspath):
            missing.append(rel)
            continue
        cands.extend(audit_file(abspath, rel, rules, args.strict))

    cands.sort(key=lambda c: (c.relpath, c.line))

    print("対象: %d ファイル%s" % (len(targets) - len(missing),
                                  "（%s モード）" % ("strict" if args.strict else "許容リスト適用")))
    print("許容リスト: %s（%d 行）" % (args.allowlist, len(rules)))
    for rel in missing:
        print("WARN 翻訳版ファイルがありません: %s" % rel)
    print()

    if not args.quiet and cands:
        print("file\tline\tcommand\tstring\treason_guess")
        for c in cands:
            print(c.row())
        print()

    by_file = {}
    by_cmd = {}
    for c in cands:
        by_file[c.relpath] = by_file.get(c.relpath, 0) + 1
        by_cmd[c.command] = by_cmd.get(c.command, 0) + 1

    print("=================================================================")
    print("英語残り候補: %d 件 / %d ファイル" % (len(cands), len(by_file)))
    print("=================================================================")
    if by_file:
        print("-- ファイル別 --")
        for rel, cnt in sorted(by_file.items(), key=lambda kv: (-kv[1], kv[0])):
            print("  %4d  %s" % (cnt, rel))
        print("-- コマンド別 --")
        for cmd, cnt in sorted(by_cmd.items(), key=lambda kv: (-kv[1], kv[0])):
            print("  %4d  %s" % (cnt, cmd))

    if args.unused_allow and not args.strict:
        unused = [r for r in rules if r.hits == 0]
        print("-- 未使用の許容リスト行: %d --" % len(unused))
        for r in unused:
            print("  L%-4d %s\t%s" % (r.lineno, r.file_pat or "*", r.pattern))

    if args.out:
        d = os.path.dirname(os.path.abspath(args.out))
        if d:
            os.makedirs(d, exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write("file\tline\tcommand\tstring\treason_guess\n")
            for c in cands:
                fh.write(c.row() + "\n")
        print("TSV: %s" % args.out)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ToolError as exc:
        die("jp_english_audit: %s" % exc)

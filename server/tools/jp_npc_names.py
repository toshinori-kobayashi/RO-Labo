#!/usr/bin/env python3
"""NPC の頭上表示名（display name）を日本語化するための棚卸し・適用・検査ツール。

rAthena の NPC 名前解決はすべて **exname（`表示名::ユニーク名` の後半）** で行われる
（src/map/npc.cpp `npc_parsename` が `npcname_db` に exname をキーとして登録し、
`npc_name2id()` は exname でしか引かない）。したがって

    上流 `Kafra Employee#prt`            → 翻訳版 `カプラ職員#prt::Kafra Employee#prt`
    上流 `Guide#gef::GefGuide`           → 翻訳版 `案内係#gef::GefGuide`

のように「表示名だけを日本語にし、exname は上流のまま残す」と
doevent / donpcevent / enablenpc / disablenpc / hideonnpc / hideoffnpc /
cloakonnpc / cloakoffnpc / getvariableofnpc / getnpcid / setnpcdisplay /
npcshopitem / npcshopattach / `"名前::OnEvent"` / duplicate(名前) の解決は一切壊れない。

`#suffix` を新しい表示名にも引き継ぐのは `strnpcinfo(2)`（`nd->name` の `#` 以降）を
分岐に使うスクリプトがあるため（src/map/script.cpp `BUILDIN_FUNC(strnpcinfo)`）。
これで strnpcinfo(1)=日本語 / (2)=suffix / (3)=旧 exname / (4)=マップ名 が全て維持される。

使い方:
    tools/jp_npc_names.py inventory --out docs/jp-npc-names.tsv
    tools/jp_npc_names.py apply --map docs/jp-npc-names.tsv --dry-run
    tools/jp_npc_names.py apply --map docs/jp-npc-names.tsv
    tools/jp_npc_names.py check --map docs/jp-npc-names.tsv

inventory は MANIFEST の全翻訳ファイルのヘッダを棚卸しして TSV を出す。
人間は `apply_jp` 列（可視部分の日本語だけ。`#suffix` はツールが引き継ぐ）を埋める。
apply は `apply_jp` が空でない行のヘッダ行だけを書き換える（他の行は 1 バイトも触らない）。

適用後は必ず以下が通ること:
    scripts/check-jp-structure.sh          # PASS 117 / FAIL 0
    scripts/check-overlay.sh               # BOM / LF / CP932
    tools/gen-jp-conf.py --check           # 差分なし
"""

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jp_common import (  # noqa: E402
    JP_DIR, MANIFEST_PATH, OVERLAY_DIR, REPO_ROOT,
    ToolError, Upstream, iter_jp_files, parse_manifest, die,
)
import jp_structure_check as jsc  # noqa: E402  （トークナイザ / ヘッダ検出を流用）


# ---------------------------------------------------------------- 定数

#: src/common/mmo.hpp:157 `#define NPC_NAME_LENGTH 50`
#: npc_parsename は `len > NPC_NAME_LENGTH` で警告つき切り詰めを行う。
#: 表示名は CP932（クライアントに届くバイト列）で数える。
NPC_NAME_LENGTH = 50

#: 頭上に名前が出ないスプライト。src/map/npc.hpp の e_job_types より
#:   JT_WARPNPC = 45 / JT_HIDDEN_NPC = 111 / JT_HIDDEN_WARP_NPC = 139
#: -1 は FAKE_NPC（浮動 NPC・OnInit 専用 NPC）。
INVISIBLE_SPRITES = frozenset([
    "-1", "45", "111", "139", "32767",
    "FAKE_NPC", "WARPNPC", "HIDDEN_NPC", "HIDDEN_WARP_NPC", "INVISIBLE_CLASS",
    "JT_WARPNPC", "JT_HIDDEN_NPC", "JT_HIDDEN_WARP_NPC", "JT_INVISIBLE",
])

#: 売店系のヘッダ種別。本文は無いが頭上に名前が出るので日本語化の対象。
#:   `<map>,<x>,<y>,<dir>\tshop\t<名前>\t<sprite>,<itemid>:<price>,...`
SHOP_KINDS = frozenset(["shop", "cashshop", "itemshop", "pointshop", "marketshop"])

#: ワープポータル。頭上名は出ないので対象外。
#:   `<map>,<x>,<y>\twarp\t<名前>\t<xs>,<ys>,<到達マップ>,<x>,<y>`（sprite 欄が無い）
WARP_KINDS = frozenset(["warp", "warp2"])

#: script 以外のヘッダ種別
NON_SCRIPT_KINDS = SHOP_KINDS | WARP_KINDS

#: 引数の文字列が NPC 名（exname）として解決されるコマンド。
#: 文字列引数は exname と完全一致したときだけ参照として数えるので、
#: メッセージ側の引数（npctalk の第 1 引数など）が混ざっても実害はない。
#: なお npctalk の NPC 名引数は npc_name2id() 解決なので exname 参照である
#: （src/map/script.cpp BUILDIN_FUNC(npctalk)）。
NPC_NAME_ARG_COMMANDS = frozenset("""
doevent donpcevent enablenpc disablenpc hideonnpc hideoffnpc
cloakonnpc cloakoffnpc getvariableofnpc getnpcid setnpcdisplay
npcshopitem npcshopattach npcshopadditem npcshopdelitem npcshopupdate
npctalk unittalk npcspeed npcwalkto npcstop
""".split())

#: 話者タグ `mes "[名前]"`
SPEAKER_TAG_RE = re.compile(r"^\[(.+)\]$")

#: 話者タグとして採用しないもの（正体不明・伏せ字）
TAG_BLOCKLIST = frozenset(["?", "??", "???", "????", "!", "...", "…", "-", "--"])

ASCII_WORD_RE = re.compile(r"[A-Za-z0-9]+")

#: apply_jp に入れてはいけない文字
CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")

TSV_COLUMNS = [
    "file", "line", "kind", "upstream_name", "current_name", "display", "hidden",
    "exname", "visible", "speaker_tags", "first_tag", "dup_source", "dup_source_file",
    "refs_exname", "refs_exname_at", "refs_display_text", "refs_display_at",
    "strnpcinfo_use", "category", "proposed_jp", "apply_jp", "note",
]

TSV_HEADER_COMMENT = """\
# NPC 頭上表示名 対応表（tools/jp_npc_names.py の Source of Truth）
#
# 生成: tools/jp_npc_names.py inventory --out docs/jp-npc-names.tsv
# 適用: tools/jp_npc_names.py apply --map docs/jp-npc-names.tsv [--dry-run]
# 検査: tools/jp_npc_names.py check --map docs/jp-npc-names.tsv
#
# 人間が編集するのは `apply_jp` 列だけ。**可視部分の日本語だけ**を書く
# （`#suffix` と `::exname` はツールが上流ヘッダから機械的に引き継ぐ）。
# 空欄の行は変更されない。`::` `#` タブ・制御文字は使用不可、CP932 で
# 表せない文字も不可、`#suffix` 込みの CP932 バイト長は 50 以内（NPC_NAME_LENGTH）。
#
# 列の意味:
#   file/line          翻訳版ファイルとヘッダ行（1 始まり）
#   kind               script / duplicate / shop / warp / function
#   upstream_name      上流ファイルの同じヘッダのフル名（`-` = 追加のみで上流なし）
#   current_name       現在の翻訳版のフル名
#   display/hidden/exname  現在名の分解（display = `::` の前、hidden = `#` の後、exname = `::` の後）
#   visible            頭上に名前が出るか（no = 浮動 `-` / function / warp /
#                      sprite -1・45・111・139 / 表示名が `#` 始まり）
#                      shop 系（道具屋・武器屋など）は本文が無いだけで頭上名は出るので yes
#   speaker_tags       本文の `mes "[…]"` を出現順・重複除去で `|` 区切り
#   first_tag          その先頭（`[?]` 等と文字列連結のタグは除外）
#   dup_source         duplicate(...) の参照元 exname
#   dup_source_file    参照元 NPC を定義しているファイル（翻訳版 or 上流）
#   refs_exname        exname を参照している箇所数（Pre-RE 実ロード構成での全文走査）
#   refs_exname_at     その例（最大 3 件）
#   refs_display_text  可視表示名が他ファイルの文字列リテラルに出る箇所数（参考情報）
#   refs_display_at    その例（最大 3 件）
#   strnpcinfo_use     実行される本文の strnpcinfo 使用（例 `1:cmp` `1:tag` `2:arg`）
#   category           A=上流に `::` あり / B=`::` を足せば安全 / C=要個別判断 / D=対象外
#                      （shop 系は本文が無いので speaker_tags / first_tag は空になる）
#   proposed_jp        自動提案（話者タグ・用語集から。ベストエフォート）
#   apply_jp           ★人間が確定した日本語（可視部分のみ）
#   note               判断理由・注意
"""


# ---------------------------------------------------------------- 名前の分解

def rel_to_repo(path):
    """表示用のパス（リポジトリ外なら絶対パスのまま）。"""
    try:
        rel = os.path.relpath(path, REPO_ROOT)
    except ValueError:
        return path
    return path if rel.startswith("..") else rel


def split_name(name):
    """ヘッダの名前フィールドを (display, exname) に分ける。"""
    if "::" in name:
        disp, uniq = name.split("::", 1)
        return disp, uniq
    return name, name


def split_display(display):
    """表示名を (可視部分, `#` 以降を含む suffix) に分ける。"""
    idx = display.find("#")
    if idx < 0:
        return display, ""
    return display[:idx], display[idx:]


def cp932_len(text):
    """CP932 でのバイト長。表せない文字があれば None。"""
    try:
        return len(text.encode("cp932"))
    except (UnicodeEncodeError, LookupError):
        return None


def build_name(apply_jp, upstream_name):
    """`apply_jp` と上流フル名から新しい名前フィールドを組み立てる。

    上流に `::` が無い  → `apply_jp{#suffix}::上流フル名`
    上流に `::` がある  → `apply_jp{#suffix}::上流ユニーク名`
    `#suffix` は上流の表示名側のものをそのまま引き継ぐ（strnpcinfo(2) 用）。
    """
    u_disp, u_uniq = split_name(upstream_name)
    _visible, hidden = split_display(u_disp)
    return "%s%s::%s" % (apply_jp, hidden, u_uniq)


def validate_apply_jp(apply_jp, upstream_name):
    """apply_jp の妥当性を検査する。問題メッセージのリストを返す（空なら OK）。"""
    problems = []
    if apply_jp != apply_jp.strip():
        problems.append("前後に空白があります: %r" % apply_jp)
    if not apply_jp.strip():
        problems.append("空です")
        return problems
    if "::" in apply_jp:
        problems.append("`::` は使えません（exname と混ざります）: %r" % apply_jp)
    if "#" in apply_jp:
        problems.append("`#` は使えません（suffix はツールが引き継ぎます）: %r" % apply_jp)
    if "\t" in apply_jp:
        problems.append("タブは使えません: %r" % apply_jp)
    if CONTROL_RE.search(apply_jp):
        problems.append("制御文字が含まれています: %r" % apply_jp)
    if "//" in apply_jp:
        problems.append("`//` はコメント開始として解釈されます: %r" % apply_jp)
    for ch, why in jsc.FORBIDDEN_CHARS.items():
        if ch in apply_jp:
            problems.append("使用禁止文字 %s: %s" % (ch, why))
    bad = [c for c in apply_jp if cp932_len(c) is None]
    if bad:
        problems.append("CP932 に無い文字: %s" % " ".join("%r(U+%04X)" % (c, ord(c))
                                                          for c in sorted(set(bad))))
        return problems
    u_disp, _u_uniq = split_name(upstream_name)
    _visible, hidden = split_display(u_disp)
    new_display = apply_jp + hidden
    nbytes = cp932_len(new_display)
    if nbytes is not None and nbytes > NPC_NAME_LENGTH:
        problems.append("表示名が長すぎます: %r は CP932 %d バイト（上限 %d）"
                        % (new_display, nbytes, NPC_NAME_LENGTH))
    return problems


# ---------------------------------------------------------------- ヘッダ情報

class NpcRow(object):
    """1 ヘッダぶんの棚卸し結果。"""

    def __init__(self, jp_file, header, index):
        self.file = jp_file
        self.index = index                  # ファイル内のヘッダ通番
        self.line = header.line
        self.raw = header.raw
        self.kind_raw = header.kind
        fields = header.raw.split("\t")
        self.first_field = fields[0].strip() if fields else ""
        self.rest = fields[3] if len(fields) > 3 else ""
        m = jsc.DUPLICATE_KIND_RE.match(header.kind) if hasattr(jsc, "DUPLICATE_KIND_RE") else None
        if m is None:
            m = re.match(r"^duplicate\((.*)\)$", header.kind)
        self.dup_source = m.group(1) if m else ""
        if m:
            self.kind = "duplicate"
        elif self.first_field == "function":
            self.kind = "function"
        elif header.kind in NON_SCRIPT_KINDS:
            self.kind = header.kind
        else:
            self.kind = "script"
        self.current_name = header.name
        self.display, self.exname = split_name(header.name)
        self.visible_name, self.hidden = split_display(self.display)
        self.sprite = self.rest.split(",")[0].strip() if self.rest else ""
        self.upstream_name = None           # 後から埋める
        self.speaker_tags = []
        self.first_tag = ""
        self.dup_source_file = ""
        self.refs_exname = []
        self.refs_display = []
        self.strnpcinfo_use = []
        self.category = ""
        self.proposed_jp = ""
        self.notes = []

    @property
    def is_visible(self):
        # warp は頭上名が出ない。shop 系は sprite を持つので script と同じ扱い。
        if self.kind in WARP_KINDS or self.kind == "function":
            return False
        if self.first_field in ("-", "function"):
            return False
        if not self.visible_name:
            return False
        if self.sprite in INVISIBLE_SPRITES:
            return False
        return True

    @property
    def upstream_base(self):
        """新しい名前を組み立てる土台になるフル名（上流優先、無ければ現在名）。"""
        return self.upstream_name if self.upstream_name else self.current_name


# ---------------------------------------------------------------- 本文解析

def body_ranges(headers, total_lines):
    """ヘッダごとの本文行範囲 [start, end] を返す。"""
    out = []
    for i, h in enumerate(headers):
        start = h.line
        end = headers[i + 1].line - 1 if i + 1 < len(headers) else total_lines
        out.append((start, end))
    return out


def tokens_in_range(tokens, start, end):
    return [t for t in tokens if start <= t.line <= end]


def speaker_tags(tokens):
    """本文の `mes "[…]"` を出現順・重複除去で返す。"""
    out, seen = [], set()
    for i, t in enumerate(tokens):
        if t.kind != "word" or t.value not in ("mes", "mesf", "npctalk", "unittalk"):
            continue
        j = i + 1
        while j < len(tokens) and tokens[j].kind == "op" and tokens[j].value == "(":
            j += 1
        if j >= len(tokens) or tokens[j].kind != "str":
            continue
        # 文字列連結（"[" + strnpcinfo(1) + "]" 等）はタグ名が取れないので除外
        if j + 1 < len(tokens) and tokens[j + 1].kind == "op" and tokens[j + 1].value == "+":
            continue
        m = SPEAKER_TAG_RE.match(tokens[j].value)
        if not m:
            continue
        tag = m.group(1).strip()
        if not tag or tag in TAG_BLOCKLIST or "%" in tag:
            continue
        if tag not in seen:
            seen.add(tag)
            out.append(tag)
    return out


def pick_first_tag(tags):
    """自動提案に使える先頭タグ（日本語を含むもの）。"""
    for tag in tags:
        if any(ord(c) > 0x7F for c in tag):
            return tag
    return tags[0] if tags else ""


# ---------------------------------------------------------------- コーパス

class EffectiveCorpus(object):
    """Pre-RE で実際にロードされる構成（上流 → 翻訳版に差し替え済み）のコーパス。

    `npc/pre-re/scripts_main.conf` を再帰展開した npc: 集合のうち MANIFEST に
    載っているものは翻訳版へ差し替え、追加のみのエントリを末尾に足す。
    上流と翻訳版の両方を数えると参照が二重になるため、実ロード構成で数える。
    """

    def __init__(self, upstream, entries):
        self.upstream = upstream
        self.by_upstream = dict((e.upstream, e) for e in entries if e.upstream)
        self.labels = []                 # ロード順のラベル
        self.is_translated = {}          # label -> bool
        self.abspath = {}                # label -> 実ファイルパス（翻訳版のみ）
        self.upstream_rel = {}           # label -> 上流パス（翻訳版なら差し替え元）
        self._text = {}

        replaced = set()
        for rel in upstream.prere_npc_paths():
            ent = self.by_upstream.get(rel)
            if ent is not None:
                if ent.translated in self.is_translated:
                    continue
                replaced.add(rel)
                self.labels.append(ent.translated)
                self.is_translated[ent.translated] = True
                self.abspath[ent.translated] = ent.translated_abspath
                self.upstream_rel[ent.translated] = rel
            else:
                if rel in self.is_translated:
                    continue
                self.labels.append(rel)
                self.is_translated[rel] = False
                self.upstream_rel[rel] = rel
        for ent in entries:
            if ent.translated in self.is_translated:
                continue
            self.labels.append(ent.translated)
            self.is_translated[ent.translated] = True
            self.abspath[ent.translated] = ent.translated_abspath
            self.upstream_rel[ent.translated] = ent.upstream

    def text(self, label):
        if label in self._text:
            return self._text[label]
        if self.is_translated[label]:
            with open(self.abspath[label], "rb") as fh:
                data = fh.read()
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                text = data.decode("latin-1")
        else:
            text = self.upstream.read_text(label)
        self._text[label] = text
        return text


def collect_refs(tokens, headers, label, ref_hits, setnpcdisplay_hits):
    """1 ファイルから exname 参照を拾って ref_hits に足す。

    対象:
      - duplicate(<exname>) ヘッダ
      - `"<exname>::On…"` 形式の文字列（イベント参照）
      - NPC_NAME_ARG_COMMANDS の文字列引数
    """
    for h in headers:
        m = re.match(r"^duplicate\((.*)\)$", h.kind)
        if m and m.group(1):
            ref_hits.setdefault(m.group(1), []).append((label, h.line, "duplicate"))

    n = len(tokens)
    for i, t in enumerate(tokens):
        if t.kind == "str" and "::" in t.value:
            name = t.value.split("::", 1)[0]
            if name:
                ref_hits.setdefault(name, []).append((label, t.line, "event"))
        if t.kind != "word" or t.value not in NPC_NAME_ARG_COMMANDS:
            continue
        # コマンドの引数（`;` まで、または括弧の対応が閉じるまで）の文字列を拾う
        args = []
        depth = 0
        j = i + 1
        while j < n:
            tk = tokens[j]
            if tk.kind == "op":
                if tk.value == "(":
                    depth += 1
                elif tk.value == ")":
                    depth -= 1
                    if depth <= 0:
                        break
                elif tk.value == ";" and depth <= 0:
                    break
                elif tk.value in ("{", "}"):
                    break
            elif tk.kind == "str":
                args.append(tk)
            j += 1
        for k, tk in enumerate(args):
            name = tk.value.split("::", 1)[0] if "::" in tk.value else tk.value
            if name:
                ref_hits.setdefault(name, []).append((label, tk.line, t.value))
            if t.value == "setnpcdisplay" and k == 0 and len(args) > 1:
                setnpcdisplay_hits.setdefault(name, []).append(
                    (label, tk.line, args[1].value))


def collect_display_hits(tokens, label, word_to_names, jp_regex, display_hits):
    """文字列リテラルに可視表示名がそのまま出てくる箇所を拾う（参考情報）。"""
    for t in tokens:
        if t.kind != "str":
            continue
        value = t.value
        seen = set()
        for word in ASCII_WORD_RE.findall(value):
            for name in word_to_names.get(word, ()):
                if name in seen:
                    continue
                if name in value:
                    seen.add(name)
                    display_hits.setdefault(name, []).append((label, t.line))
        if jp_regex is not None:
            for m in jp_regex.finditer(value):
                name = m.group(0)
                if name not in seen:
                    seen.add(name)
                    display_hits.setdefault(name, []).append((label, t.line))


# ---------------------------------------------------------------- 用語集

GLOSSARY_SECTION = "## NPC 固有名詞の扱い"
GLOSSARY_PAIR_RE = re.compile(
    r"(?P<key>[A-Za-z][A-Za-z0-9 .'’/&#_\-]*[A-Za-z0-9.#_)]|[A-Za-z])"
    r"(?:（(?P<alt>[^）]*)）)?"
    r"\s*(?:→|->)\s*"
    r"(?P<val>[^、。（）()\[\]\s|/]+)")


def load_glossary(path=None):
    """docs/JP_GLOSSARY.md の「NPC 固有名詞の扱い」節から 英語名→日本語名 を拾う。

    ベストエフォート（提案用）。取りこぼしても apply には影響しない。
    """
    if path is None:
        path = os.path.join(REPO_ROOT, "docs", "JP_GLOSSARY.md")
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    inside = False
    table = {}
    for line in lines:
        if line.startswith("## "):
            inside = (line.strip() == GLOSSARY_SECTION)
            continue
        if not inside or not line.strip():
            continue
        for m in GLOSSARY_PAIR_RE.finditer(line):
            key = m.group("key").strip()
            val = m.group("val").strip()
            if not key or not val:
                continue
            if not any(ord(c) > 0x7F for c in val):
                continue            # 日本語でない = 訳ではない
            if len(key) < 2:
                continue
            table.setdefault(key, val)
            alt = (m.group("alt") or "").strip()
            if alt and all(ord(c) < 0x80 for c in alt) and len(alt) >= 2:
                table.setdefault(alt, val)
    return table


def glossary_lookup(table, row):
    for key in (row.display, row.visible_name):
        if key and key in table:
            return table[key]
    return ""


# ---------------------------------------------------------------- inventory

def build_rows(entries, upstream, corpus):
    """MANIFEST の全翻訳ファイルを棚卸しして NpcRow のリストを返す。"""
    rows = []
    by_file = {}
    parse_problems = []

    for ent in entries:
        label = ent.translated
        text = corpus.text(label)
        tokens, headers = jsc.tokenize(text)
        total = text.count("\n") + 1
        ranges = body_ranges(headers, total)
        file_rows = []
        for i, h in enumerate(headers):
            row = NpcRow(label, h, i)
            start, end = ranges[i]
            body = tokens_in_range(tokens, start, end)
            row._body = body
            row.speaker_tags = speaker_tags(body)
            row.first_tag = pick_first_tag(row.speaker_tags)
            file_rows.append(row)
        if ent.upstream:
            try:
                u_text = upstream.read_text(ent.upstream)
            except ToolError as exc:
                parse_problems.append("%s: 上流を読めません: %s" % (label, exc))
                u_heads = []
            else:
                _u_tokens, u_heads = jsc.tokenize(u_text)
            if u_heads and len(u_heads) != len(file_rows):
                parse_problems.append(
                    "%s: ヘッダ数が上流と違います（上流 %d / 翻訳 %d）。upstream_name は `?` にします"
                    % (label, len(u_heads), len(file_rows)))
                u_heads = []
            for i, row in enumerate(file_rows):
                row.upstream_name = u_heads[i].name if i < len(u_heads) else None
        rows.extend(file_rows)
        by_file[label] = file_rows
    return rows, by_file, parse_problems


def analyse(rows, corpus, upstream):
    """参照・strnpcinfo・分類・提案を埋める。"""
    # --- exname を定義しているファイル（ロード順で最初）---------------
    owner = {}
    owner_row = {}
    for row in rows:
        owner.setdefault(row.exname, row.file)
        owner_row.setdefault(row.exname, row)

    ref_hits = {}
    setnpcdisplay_hits = {}
    display_hits = {}
    upstream_owner = {}
    upstream_defs = {}          # label -> [(exname, line)]

    # --- 可視表示名の索引（英語名は先頭 ASCII 語、日本語名は正規表現）---
    word_to_names = {}
    jp_names = set()
    for row in rows:
        name = row.visible_name
        if not name or len(name) < 3:
            continue
        words = ASCII_WORD_RE.findall(name)
        if words:
            word_to_names.setdefault(words[0], [])
            if name not in word_to_names[words[0]]:
                word_to_names[words[0]].append(name)
        else:
            jp_names.add(name)
    jp_regex = None
    if jp_names:
        jp_regex = re.compile("|".join(re.escape(n) for n in
                                       sorted(jp_names, key=len, reverse=True)))

    # --- コーパス全走査 -----------------------------------------------
    for label in corpus.labels:
        text = corpus.text(label)
        try:
            tokens, headers = jsc.tokenize(text)
        except Exception:
            continue
        collect_refs(tokens, headers, label, ref_hits, setnpcdisplay_hits)
        collect_display_hits(tokens, label, word_to_names, jp_regex, display_hits)
        if not corpus.is_translated[label]:
            defs = []
            for h in headers:
                _d, ex = split_name(h.name)
                if ex:
                    upstream_owner.setdefault(ex, label)
                    defs.append((ex, h.line))
            upstream_defs[label] = defs
        # メモリを抑えるため翻訳版以外の本文は保持しない
        if not corpus.is_translated[label]:
            corpus._text.pop(label, None)

    # --- duplicate の参照元解決 ---------------------------------------
    need_upstream_body = {}
    for row in rows:
        if row.kind != "duplicate" or not row.dup_source:
            continue
        if row.dup_source in owner:
            row.dup_source_file = owner[row.dup_source]
        elif row.dup_source in upstream_owner:
            row.dup_source_file = upstream_owner[row.dup_source]
            need_upstream_body.setdefault(row.dup_source_file, set()).add(row.dup_source)
        else:
            row.dup_source_file = "?"
            row.notes.append("duplicate 元 %r が見つかりません" % row.dup_source)

    # --- 上流側にある duplicate 元の本文を解析（strnpcinfo 判定用）-----
    upstream_body_use = {}
    for label, wanted in need_upstream_body.items():
        text = corpus.text(label)
        try:
            tokens, headers = jsc.tokenize(text)
        except Exception:
            corpus._text.pop(label, None)
            continue
        ranges = body_ranges(headers, text.count("\n") + 1)
        for i, h in enumerate(headers):
            _d, ex = split_name(h.name)
            if ex not in wanted:
                continue
            start, end = ranges[i]
            body = tokens_in_range(tokens, start, end)
            upstream_body_use[ex] = jsc.strnpcinfo_usages(body)
        corpus._text.pop(label, None)

    # --- 行ごとの仕上げ ------------------------------------------------
    for row in rows:
        hits = ref_hits.get(row.exname, [])
        row.refs_exname = hits
        row.refs_display = display_hits.get(row.visible_name, []) if row.visible_name else []

        # 実行される本文 = script は自分、duplicate は参照元
        if row.kind == "duplicate":
            src_row = owner_row.get(row.dup_source)
            if src_row is not None:
                row.strnpcinfo_use = jsc.strnpcinfo_usages(src_row._body)
                if not row.speaker_tags:
                    row.speaker_tags = src_row.speaker_tags
                    row.first_tag = src_row.first_tag
            elif row.dup_source in upstream_body_use:
                row.strnpcinfo_use = upstream_body_use[row.dup_source]
        else:
            row.strnpcinfo_use = jsc.strnpcinfo_usages(row._body)

    classify(rows, owner_row, setnpcdisplay_hits)
    return ref_hits, display_hits, setnpcdisplay_hits


def classify(rows, owner_row, setnpcdisplay_hits):
    glossary = load_glossary()
    for row in rows:
        # ---- D: 対象外 ------------------------------------------------
        if not row.is_visible:
            row.category = "D"
            if row.kind in WARP_KINDS:
                row.notes.append("%s は頭上名の対象外" % row.kind)
            elif row.kind == "function":
                row.notes.append("function（NPC ではない）")
            elif row.first_field == "-":
                row.notes.append("浮動 NPC（マップに出ない）")
            elif not row.visible_name:
                row.notes.append("表示名が `#` 始まりで可視部分が空")
            elif row.sprite in INVISIBLE_SPRITES:
                row.notes.append("sprite %s は頭上名が出ない" % row.sprite)
            continue

        # ---- C: 表示名そのものに依存 -----------------------------------
        reasons = []
        for arg, use, line in row.strnpcinfo_use:
            if arg in (0, 1) and use in ("cmp", "concat", "ident", "assign"):
                reasons.append("strnpcinfo(%d) を %s に使用（%d 行目）" % (arg, use, line))
        sd = setnpcdisplay_hits.get(row.exname, [])
        for label, line, newname in sd:
            reasons.append("setnpcdisplay で表示名を %r に上書き（%s:%d）" % (newname, label, line))
        if reasons:
            row.category = "C"
            row.notes.extend(reasons)
            continue

        for arg, use, line in row.strnpcinfo_use:
            if arg in (0, 1) and use == "tag":
                row.notes.append("strnpcinfo(%d) は話者タグ生成のみ（%d 行目）。"
                                 "表示名変更でタグも日本語になる" % (arg, line))

        # ---- A / B ------------------------------------------------------
        base = row.upstream_base
        if row.upstream_name is None:
            row.notes.append("上流なし（追加のみ）。現在名を土台にする")
        if "::" in base:
            row.category = "A"
        else:
            row.category = "B"
            row.notes.append("`::%s` を足して exname を保全する" % base)

    # ---- 提案 ------------------------------------------------------------
    for row in rows:
        if row.category == "D":
            continue
        if row.kind == "duplicate":
            continue
        row.proposed_jp = propose(row, glossary)
    for row in rows:
        if row.category == "D" or row.kind != "duplicate":
            continue
        # 1) 既に日本語ならそのまま
        if any(ord(c) > 0x7F for c in row.visible_name):
            row.proposed_jp = row.visible_name
            continue
        # 2) 用語集に自分の名前があればそれ
        hit = glossary_lookup(glossary, row)
        if hit:
            row.proposed_jp = hit
            continue
        src = owner_row.get(row.dup_source)
        if src is None:
            continue
        src_choice = src.proposed_jp or (src.visible_name
                                         if any(ord(c) > 0x7F for c in src.visible_name) else "")
        if not src_choice:
            continue
        # 3) 英語名が参照元と同じなら「同じ NPC の複製」とみなして踏襲する
        if upstream_visible(row) == upstream_visible(src):
            if any(a == 2 and u in ("cmp", "ident", "concat")
                   for a, u, _ln in row.strnpcinfo_use):
                row.notes.append(
                    "duplicate 元 %s は strnpcinfo(2) で個体を識別しているので、"
                    "個体ごとに名前が違う可能性がある（参照元の提案は %r）"
                    % (row.dup_source, src_choice))
                continue
            row.proposed_jp = src_choice
            row.notes.append("duplicate 元 %s と同じ表示名" % row.dup_source)
        else:
            row.notes.append("英語名が duplicate 元 %s（%r）と違う個体なので個別に決めること"
                             "（参照元の提案は %r）"
                             % (row.dup_source, upstream_visible(src), src_choice))


def upstream_visible(row):
    """上流ヘッダ（無ければ現在名）の表示名の可視部分。"""
    disp, _ex = split_name(row.upstream_base)
    vis, _hidden = split_display(disp)
    return vis


def propose(row, glossary):
    """自動提案。無ければ空欄（人が埋める）。"""
    if any(ord(c) > 0x7F for c in row.visible_name):
        return row.visible_name          # 既に日本語（そのまま維持を提案）
    tag = row.first_tag
    if tag and any(ord(c) > 0x7F for c in tag):
        return tag
    return glossary_lookup(glossary, row)


# ---------------------------------------------------------------- TSV 入出力

def tsv_escape(value):
    if value is None:
        return ""
    text = str(value)
    return text.replace("\t", " ").replace("\n", " ").replace("\r", " ")


def fmt_hits(hits, limit=3):
    out = []
    for hit in hits[:limit]:
        out.append("%s:%d" % (hit[0], hit[1]))
    if len(hits) > limit:
        out.append("...(+%d)" % (len(hits) - limit))
    return " ".join(out)


def row_to_tsv(row):
    values = {
        "file": row.file,
        "line": row.line,
        "kind": row.kind,
        "upstream_name": row.upstream_name if row.upstream_name is not None else "-",
        "current_name": row.current_name,
        "display": row.display,
        "hidden": row.hidden,
        "exname": row.exname,
        "visible": "yes" if row.is_visible else "no",
        "speaker_tags": "|".join(row.speaker_tags),
        "first_tag": row.first_tag,
        "dup_source": row.dup_source,
        "dup_source_file": row.dup_source_file,
        "refs_exname": len(row.refs_exname),
        "refs_exname_at": fmt_hits(row.refs_exname),
        "refs_display_text": len([h for h in row.refs_display if h[0] != row.file]),
        "refs_display_at": fmt_hits([h for h in row.refs_display if h[0] != row.file]),
        "strnpcinfo_use": ";".join("%d:%s@%d" % (a, u, ln) for a, u, ln in row.strnpcinfo_use),
        "category": row.category,
        "proposed_jp": row.proposed_jp,
        "apply_jp": "",
        "note": "; ".join(row.notes),
    }
    return "\t".join(tsv_escape(values[c]) for c in TSV_COLUMNS)


def write_tsv(path, rows):
    d = os.path.dirname(os.path.abspath(path))
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(TSV_HEADER_COMMENT)
        fh.write("\t".join(TSV_COLUMNS) + "\n")
        for row in rows:
            fh.write(row_to_tsv(row) + "\n")


def read_tsv(path):
    """対応表を読む。(列名リスト, [dict]) を返す。"""
    if not os.path.isfile(path):
        raise ToolError("対応表がありません: %s" % path)
    cols, out = None, []
    with open(path, encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, 1):
            line = raw.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            fields = line.split("\t")
            if cols is None:
                cols = [f.strip() for f in fields]
                missing = [c for c in ("file", "line", "exname", "upstream_name", "apply_jp")
                           if c not in cols]
                if missing:
                    raise ToolError("対応表に必要な列がありません: %s" % ", ".join(missing))
                continue
            if len(fields) < len(cols):
                fields = fields + [""] * (len(cols) - len(fields))
            rec = dict(zip(cols, fields[:len(cols)]))
            rec["_lineno"] = lineno
            out.append(rec)
    if cols is None:
        raise ToolError("対応表にヘッダ行がありません: %s" % path)
    return cols, out


# ---------------------------------------------------------------- apply

def load_file_headers(abspath):
    with open(abspath, "rb") as fh:
        data = fh.read()
    text = data.decode("utf-8")
    _tokens, headers = jsc.tokenize(text)
    return data, text, headers


def resolve_abspath(jp_file):
    if os.path.isabs(jp_file):
        return jp_file
    cand = os.path.join(OVERLAY_DIR, jp_file)
    if os.path.isfile(cand):
        return cand
    return os.path.join(REPO_ROOT, jp_file)


def plan_apply(records, only_file=None):
    """レコードを (ファイル -> [(行, 旧行, 新行, rec)]) にまとめる。問題も返す。"""
    problems = []
    by_file = {}
    for rec in records:
        apply_jp = rec.get("apply_jp", "").strip()
        if not apply_jp:
            continue
        jp_file = rec["file"]
        if only_file and os.path.abspath(resolve_abspath(jp_file)) != os.path.abspath(
                resolve_abspath(only_file)):
            continue
        by_file.setdefault(jp_file, []).append(rec)

    plan = {}
    for jp_file, recs in sorted(by_file.items()):
        abspath = resolve_abspath(jp_file)
        if not os.path.isfile(abspath):
            problems.append("%s: ファイルがありません" % jp_file)
            continue
        try:
            _data, text, headers = load_file_headers(abspath)
        except Exception as exc:
            problems.append("%s: 読めません: %r" % (jp_file, exc))
            continue
        by_line = dict((h.line, h) for h in headers)
        lines = text.split("\n")
        edits = []
        for rec in sorted(recs, key=lambda r: int(r["line"])):
            lineno = int(rec["line"])
            apply_jp = rec["apply_jp"].strip()
            head = by_line.get(lineno)
            if head is None:
                problems.append("%s:%d: ヘッダ行がありません（行ずれ。inventory をやり直してください）"
                                % (jp_file, lineno))
                continue
            _disp, cur_ex = split_name(head.name)
            if rec.get("exname") and cur_ex != rec["exname"]:
                problems.append("%s:%d: exname が対応表と違います（表 %r / 現物 %r）"
                                % (jp_file, lineno, rec["exname"], cur_ex))
                continue
            upstream_name = rec.get("upstream_name", "").strip()
            if not upstream_name or upstream_name == "-":
                upstream_name = head.name
            elif upstream_name == "?":
                problems.append("%s:%d: upstream_name が `?` です（上流と突き合わせできません）"
                                % (jp_file, lineno))
                continue
            bad = validate_apply_jp(apply_jp, upstream_name)
            if bad:
                for b in bad:
                    problems.append("%s:%d: %s" % (jp_file, lineno, b))
                continue
            new_name = build_name(apply_jp, upstream_name)
            old_line = lines[lineno - 1]
            fields = old_line.split("\t")
            if len(fields) < 4 or fields[2] != head.name:
                problems.append("%s:%d: ヘッダ行を解釈できません: %r"
                                % (jp_file, lineno, old_line[:80]))
                continue
            if new_name == head.name:
                continue                     # 変更なし（冪等）
            fields[2] = new_name
            new_line = "\t".join(fields)
            edits.append((lineno, old_line, new_line, rec))
        if edits:
            plan[jp_file] = (abspath, text, edits)
    return plan, problems


def do_apply(args):
    try:
        _cols, records = read_tsv(args.map)
    except ToolError as exc:
        die("jp_npc_names apply: %s" % exc)

    plan, problems = plan_apply(records, args.only_file)

    filled = sum(1 for r in records if r.get("apply_jp", "").strip())
    print("対応表 : %s（%d 行、apply_jp 記入済み %d 行）"
          % (rel_to_repo(args.map), len(records), filled))
    if problems:
        print()
        print("NG: %d 件（1 件でもあれば何も書き換えません）" % len(problems))
        for p in problems:
            print("  - %s" % p)
        return 1

    n_edit = sum(len(v[2]) for v in plan.values())
    if not n_edit:
        print("変更するヘッダはありません（apply_jp が空、または既に適用済み）")
        return 0

    print("対象   : %d ファイル / %d ヘッダ" % (len(plan), n_edit))
    print()
    for jp_file, (abspath, text, edits) in sorted(plan.items()):
        print("--- %s" % jp_file)
        for lineno, old_line, new_line, _rec in edits:
            print("  @%d" % lineno)
            print("  - %s" % old_line)
            print("  + %s" % new_line)
        print()

    if args.dry_run:
        print("--dry-run: 書き換えていません")
        return 0

    for jp_file, (abspath, text, edits) in sorted(plan.items()):
        lines = text.split("\n")
        for lineno, old_line, new_line, _rec in edits:
            if lines[lineno - 1] != old_line:
                die("jp_npc_names apply: %s:%d が読み込み後に変わりました（中止）"
                    % (jp_file, lineno))
            lines[lineno - 1] = new_line
        with open(abspath, "wb") as fh:
            fh.write("\n".join(lines).encode("utf-8"))
    print("書き換えました: %d ファイル / %d ヘッダ" % (len(plan), n_edit))
    print("次に scripts/check-jp-structure.sh と scripts/check-overlay.sh を実行してください。")
    return 0


# ---------------------------------------------------------------- check

def do_check(args):
    try:
        _cols, records = read_tsv(args.map)
    except ToolError as exc:
        die("jp_npc_names check: %s" % exc)

    problems, warns = [], []

    # --- 現ファイルとの整合 ------------------------------------------
    cache = {}
    for rec in records:
        jp_file = rec["file"]
        if jp_file not in cache:
            abspath = resolve_abspath(jp_file)
            if not os.path.isfile(abspath):
                problems.append("%s: ファイルがありません（表 %d 行目）"
                                % (jp_file, rec["_lineno"]))
                cache[jp_file] = None
                continue
            try:
                _data, text, headers = load_file_headers(abspath)
            except Exception as exc:
                problems.append("%s: 読めません: %r" % (jp_file, exc))
                cache[jp_file] = None
                continue
            cache[jp_file] = dict((h.line, h) for h in headers)
        by_line = cache[jp_file]
        if by_line is None:
            continue
        try:
            lineno = int(rec["line"])
        except ValueError:
            problems.append("表 %d 行目: line が数値ではありません: %r"
                            % (rec["_lineno"], rec["line"]))
            continue
        head = by_line.get(lineno)
        if head is None:
            problems.append("%s:%d: ヘッダ行がありません（行ずれ）" % (jp_file, lineno))
            continue
        cur_disp, cur_ex = split_name(head.name)
        if rec.get("exname") and cur_ex != rec["exname"]:
            problems.append("%s:%d: exname 不一致（表 %r / 現物 %r）"
                            % (jp_file, lineno, rec["exname"], cur_ex))
            continue
        apply_jp = rec.get("apply_jp", "").strip()
        if not apply_jp:
            if rec.get("current_name") and head.name != rec["current_name"]:
                warns.append("%s:%d: 名前が対応表と違います（表 %r / 現物 %r）。"
                             "inventory をやり直してください"
                             % (jp_file, lineno, rec["current_name"], head.name))
            continue
        upstream_name = rec.get("upstream_name", "").strip()
        if not upstream_name or upstream_name == "-":
            upstream_name = head.name
        bad = validate_apply_jp(apply_jp, upstream_name)
        for b in bad:
            problems.append("%s:%d: %s" % (jp_file, lineno, b))
        if bad:
            continue
        expect = build_name(apply_jp, upstream_name)
        if head.name not in (expect, rec.get("current_name", "")):
            warns.append("%s:%d: 現物 %r は apply 前 %r とも apply 後 %r とも違います"
                         % (jp_file, lineno, head.name, rec.get("current_name", ""), expect))
        rec["_expect"] = expect
        rec["_applied"] = (head.name == expect)

    # --- 訳ゆれ（同じ英語表示名に違う apply_jp）-----------------------
    by_english = {}
    for rec in records:
        apply_jp = rec.get("apply_jp", "").strip()
        if not apply_jp:
            continue
        upstream_name = rec.get("upstream_name", "").strip()
        if not upstream_name or upstream_name in ("-", "?"):
            continue
        u_disp, _u_uniq = split_name(upstream_name)
        visible, _hidden = split_display(u_disp)
        if not visible:
            continue
        by_english.setdefault(visible, {}).setdefault(apply_jp, []).append(rec)
    for english, variants in sorted(by_english.items()):
        if len(variants) > 1:
            detail = " / ".join(
                "%r(%s)" % (jp, ", ".join("%s:%s" % (r["file"], r["line"]) for r in recs[:2]))
                for jp, recs in sorted(variants.items()))
            problems.append("訳ゆれ: 英語表示名 %r に %d 通りの訳: %s"
                            % (english, len(variants), detail))

    # --- duplicate と参照元の表示名一致 --------------------------------
    # 片方でも apply_jp が入っている（＝訳を決めた）ペアだけを見る。
    # まだ英語のままの duplicate 同士は当然名前が違うので対象外。
    by_exname = {}
    for rec in records:
        ex = rec.get("exname", "")
        if ex:
            by_exname.setdefault(ex, rec)

    def final_visible(rec):
        apply_jp = rec.get("apply_jp", "").strip()
        if apply_jp:
            return apply_jp
        vis, _h = split_display(rec.get("display", ""))
        return vis

    for rec in records:
        if rec.get("kind") != "duplicate" or rec.get("category") == "D":
            continue
        src = by_exname.get(rec.get("dup_source", ""))
        if src is None or src.get("category") == "D":
            continue
        if not (rec.get("apply_jp", "").strip() or src.get("apply_jp", "").strip()):
            continue
        mine, theirs = final_visible(rec), final_visible(src)
        if mine != theirs:
            warns.append("%s:%s: duplicate の表示名 %r が参照元 %s（%s:%s）の %r と違います"
                         % (rec["file"], rec["line"], mine, rec["dup_source"],
                            src["file"], src["line"], theirs))

    # --- 集計 -----------------------------------------------------------
    filled = sum(1 for r in records if r.get("apply_jp", "").strip())
    applied = sum(1 for r in records if r.get("_applied"))
    print("対応表 : %s" % rel_to_repo(args.map))
    print("行数   : %d（apply_jp 記入済み %d / 適用済み %d）" % (len(records), filled, applied))
    print()
    if problems:
        print("NG: %d 件" % len(problems))
        for p in problems:
            print("  - %s" % p)
    else:
        print("NG: 0 件")
    if warns:
        print()
        print("WARN: %d 件" % len(warns))
        for w in warns:
            print("  - %s" % w)
    return 1 if problems else 0


# ---------------------------------------------------------------- inventory

def do_inventory(args):
    try:
        entries = parse_manifest(args.manifest)
        upstream = Upstream(root=args.upstream_root, commit=args.commit)
    except ToolError as exc:
        die("jp_npc_names inventory: %s" % exc)

    if not upstream.has_full_tree:
        die("jp_npc_names inventory: 上流 checkout が必要です（--upstream-root）。\n"
            "  Pre-RE のロード対象と外部参照を走査するため、npc/ 全体が要ります。")

    print("MANIFEST : %s（%d エントリ）"
          % (rel_to_repo(args.manifest), len(entries)))
    print("上流     : %s" % upstream.describe())

    corpus = EffectiveCorpus(upstream, entries)
    print("コーパス : %d ファイル（Pre-RE 実ロード構成。うち翻訳版 %d）"
          % (len(corpus.labels), sum(1 for v in corpus.is_translated.values() if v)))

    rows, _by_file, parse_problems = build_rows(entries, upstream, corpus)
    analyse(rows, corpus, upstream)

    write_tsv(args.out, rows)
    print("出力     : %s（%d ヘッダ）" % (rel_to_repo(args.out), len(rows)))
    print()

    # ---- 集計 --------------------------------------------------------
    from collections import Counter
    cat = Counter(r.category for r in rows)
    kind = Counter(r.kind for r in rows)
    vis = Counter("yes" if r.is_visible else "no" for r in rows)
    proposed = sum(1 for r in rows if r.proposed_jp)
    proposed_target = sum(1 for r in rows if r.category != "D" and r.proposed_jp)
    target = sum(1 for r in rows if r.category != "D")

    print("種別     : %s" % ", ".join("%s %d" % (k, v) for k, v in sorted(kind.items())))
    print("可視     : yes %d / no %d" % (vis["yes"], vis["no"]))
    print("分類     : %s" % ", ".join("%s %d" % (k, v) for k, v in sorted(cat.items())))
    print("対象     : %d 件（A/B/C）、うち proposed_jp 記入 %d 件（全体 %d 件）"
          % (target, proposed_target, proposed))
    print()
    print("  A = 上流ヘッダに既に `::` がある（表示名だけ変更可）")
    print("  B = `::` 無し。`日本語#suffix::上流フル名` にすれば exname 保全で安全")
    print("  C = strnpcinfo(0|1) や setnpcdisplay が表示名に依存する。要個別判断")
    print("  D = 不可視 / warp / function（対象外。shop 系は頭上名が出るので対象）")

    if cat["C"]:
        print()
        print("=== C 分類（要個別判断）%d 件 ===" % cat["C"])
        for r in rows:
            if r.category != "C":
                continue
            print("  %s:%d  %s" % (r.file, r.line, r.current_name))
            print("      %s" % "; ".join(r.notes))

    if parse_problems:
        print()
        print("注意: %d 件" % len(parse_problems))
        for p in parse_problems:
            print("  - %s" % p)

    orphans = [rel for rel in iter_jp_files(JP_DIR)
               if rel not in set(e.translated for e in entries)]
    if orphans:
        print()
        print("MANIFEST に載っていない翻訳ファイル: %s" % ", ".join(orphans))
    return 0


# ---------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(
        description="NPC の頭上表示名を日本語化するための棚卸し / 適用 / 検査")
    sub = ap.add_subparsers(dest="cmd")

    p_inv = sub.add_parser("inventory", help="ヘッダを棚卸しして対応表 TSV を出力する")
    p_inv.add_argument("--out", default=os.path.join(REPO_ROOT, "docs", "jp-npc-names.tsv"),
                       help="出力先 TSV（既定: docs/jp-npc-names.tsv）")
    p_inv.add_argument("--manifest", default=MANIFEST_PATH, help="MANIFEST.tsv のパス")
    p_inv.add_argument("--upstream-root", default=None, help="上流 rAthena の checkout")
    p_inv.add_argument("--commit", default=None, help="上流コミット（既定: app/config.env）")
    p_inv.set_defaults(func=do_inventory)

    p_app = sub.add_parser("apply", help="対応表の apply_jp に従ってヘッダ行を書き換える")
    p_app.add_argument("--map", required=True, help="対応表 TSV")
    p_app.add_argument("--dry-run", action="store_true", help="差分だけ表示して書き換えない")
    p_app.add_argument("--only-file", default=None, help="このファイルだけ処理する")
    p_app.set_defaults(func=do_apply)

    p_chk = sub.add_parser("check", help="対応表と現ファイルの整合を検査する")
    p_chk.add_argument("--map", required=True, help="対応表 TSV")
    p_chk.set_defaults(func=do_check)

    args = ap.parse_args(argv)
    if not getattr(args, "func", None):
        ap.print_help()
        return 2
    try:
        return args.func(args)
    except ToolError as exc:
        die("jp_npc_names: %s" % exc)


if __name__ == "__main__":
    sys.exit(main())

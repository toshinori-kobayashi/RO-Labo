#!/usr/bin/env python3
"""翻訳版 NPC スクリプトが上流と「文字列リテラル以外は同一」であることを検証する。

rAthena のスクリプトを簡易トークナイザで読み、上流と翻訳版のトークン列
（文字列は "STR" プレースホルダ、コメント除去、空白正規化）が完全一致するかを見る。
そのうえで、文字列リテラルの対応関係（マップ名・イベント名・比較値・select の項目数・
書式指定子など、翻訳してはいけない / 崩してはいけないもの）を個別に検査する。

使い方:
    tools/jp_structure_check.py                       # MANIFEST 全件
    tools/jp_structure_check.py --file app/... --upstream npc/cities/prontera.txt
    tools/jp_structure_check.py --report /tmp/jp-structure.txt

検査項目（ファイルごとに PASS / FAIL / WARN）:
    1. エンコーディング   UTF-8 厳密 / BOM なし / CR なし / CP932 変換可 / 禁止文字なし
                          （U+301C 波ダッシュ・U+2212・半角カナ・U+FFFD・BMP 外）
                          加えて「非 ASCII 文字の直後の \\」を FAIL
    1b. エスケープ        文字列リテラル内の `\\` の直後が非 ASCII / rAthena が解釈
                          できないエスケープ（sv_unescape_c: empty escape sequence の原因）
    1c. 添字走査         添字式 var[...] 内の文字列に CP932 2 バイト目が [ ] の文字（ー ゼ ゾ ‐ 等）が無いか
                          （parse_variable の生バイト走査がファイル末尾を越えて SIGSEGV になる）
                          を FAIL。上流にも同じものがある場合は除外
    2. トークン構造       上流と完全一致（不一致なら最初の相違位置を表示）
    3. ヘッダ             表示名は `日本語#suffix::旧フル名` の形でのみ変更可
                          （exname・`#suffix`・座標・種別・sprite は不変。CP932 50 バイト以内）
    4. 文字列リテラル     同一必須の引数 / :: を含むイベント参照 / 比較値の一意性 /
                          select の項目数 / 書式指定子 / 色コード
    5. 外部参照           exname が不変で、他ファイルからの参照が壊れないこと
                          （旧表示名の文面上の引用は WARN）
    5b. 表示名依存        表示名を変えた NPC が strnpcinfo(0|1) を比較 / キーに使っていないか（WARN）
    6. 件数               mes / select / 文字列数（2 の結果から算出。参考表示）

FAIL が 1 つでもあれば終了コード 1。
"""

import argparse
import bisect
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jp_common import (  # noqa: E402
    JP_DIR, MANIFEST_PATH, OVERLAY_DIR, REPO_ROOT,
    ToolError, Upstream, iter_jp_files, parse_manifest, die,
)

# ---------------------------------------------------------------- 定数

#: 第 1 引数（マップ名・関数名・イベント名・NPC 名）が識別子として使われるコマンド。
#: これらの直後の文字列は翻訳してはいけない。
SAME_REQUIRED_COMMANDS = frozenset("""
warp warp2 savepoint areawarp callfunc callsub doevent donpcevent
getvariableofnpc enablenpc disablenpc hideonnpc hideoffnpc setnpcdisplay
cloakonnpc cloakoffnpc npcshopitem npcshopattach mapannounce monster
areamonster killmonster setmapflag removemapflag getmapflag mapwarp
setcell unitwarp instance_create bg_monster
""".split())

#: 選択肢を作るコマンド（`:` の数が選択肢数）
MENU_COMMANDS = frozenset(["select", "prompt", "menu"])

#: NPC ヘッダ行の 2 番目のフィールド
HEADER_KIND_RE = re.compile(
    r"^(warp|warp2|shop|cashshop|itemshop|pointshop|marketshop|script|duplicate\(.*\))$")

#: `duplicate(<exname>)` ヘッダ
DUPLICATE_KIND_RE = re.compile(r"^duplicate\((.*)\)$")

#: src/common/mmo.hpp:157 `#define NPC_NAME_LENGTH 50`
#: npc_parsename は表示名・ユニーク名それぞれで `len > NPC_NAME_LENGTH` を
#: 警告つき切り詰めにする。表示名はクライアントに届く CP932 バイト長で数える。
NPC_NAME_LENGTH = 50

#: CP932 に無い / 使ってはいけない文字
#
#  Python の cp932 コーデックは「Unicode 側に 2 通りの表記がある文字」を
#  どちらも通してしまうが、macOS (libiconv) の CP932 は片方しか受け付けない。
#  Docker ビルドは glibc の iconv なのでさらに挙動が違う（U+301C は通ってしまう）。
#  環境によってビルド結果が変わらないよう、ここで表記を 1 つに固定して弾く。
#  （scripts/check-overlay.sh の iconv 判定と結果が食い違わないようにするため）
FORBIDDEN_CHARS = {
    "〜": "U+301C 波ダッシュ（U+FF5E 全角チルダを使う）",
    "−": "U+2212 マイナス記号（U+FF0D 全角ハイフンまたは ASCII '-' を使う）",
    "‖": "U+2016 双柱記号（U+2225 平行記号を使う）",
    "¢": "U+00A2 セント記号（U+FFE0 全角セントを使う）",
    "£": "U+00A3 ポンド記号（U+FFE1 全角ポンドを使う）",
    "¬": "U+00AC 否定記号（U+FFE2 全角否定を使う）",
    "�": "U+FFFD 置換文字（文字化けの残骸）",
}

# sprintf 系（buildin sprintf / logmes 等）で意味を持つ変換指定子だけを数える。
# "F#%k" のような伏せ字の % は指定子ではないので対象外。
FORMAT_SPEC_RE = re.compile(r"%[-+0#]*[0-9*]*(?:\.[0-9*]+)?(?:hh|h|ll|l|z)?[diouxXcsfeEgGp%]")
COLOR_CODE_RE = re.compile(r"\^[0-9A-Fa-f]{6}")

#: 非 ASCII 文字の直後の `\`（CP932 で 2 バイト目 0x5C と衝突してエスケープが壊れる）
BACKSLASH_AFTER_NONASCII_RE = re.compile(r"([^\x00-\x7f])\\")

PASS, WARN, FAIL = "PASS", "WARN", "FAIL"


# ---------------------------------------------------------------- トークナイザ

class Token(object):
    __slots__ = ("kind", "value", "line")

    def __init__(self, kind, value, line):
        self.kind = kind    # 'str' / 'name' / 'word' / 'num' / 'op' / 'dupsrc'
        self.value = value
        self.line = line

    def display(self):
        if self.kind == "str":
            return '"STR"'
        if self.kind == "name":
            return "<name:%s>" % self.value
        return self.value

    def __repr__(self):
        return "Token(%s,%r,L%d)" % (self.kind, self.value, self.line)


TOKEN_RE = re.compile(r"""
    (?P<nl>\n)
  | (?P<ws>[ \t\r]+)
  | (?P<bc>/\*.*?\*/)
  | (?P<bco>/\*.*\Z)
  | (?P<lc>//[^\n]*)
  | (?P<str>"(?:\\.|[^"\\\n])*")
  | (?P<ustr>"(?:\\.|[^"\\\n])*\Z)
  | (?P<num>0[xX][0-9A-Fa-f]+|\d+)
  | (?P<id>(?:\#\#|\$@|\.@|\$|\.|'|\#|@)?[A-Za-z_][A-Za-z0-9_]*\$?)
  | (?P<op2>==|!=|<=|>=|&&|\|\||<<|>>|\+\+|--|\+=|-=|\*=|/=|%=|&=|\|=|\^=|::)
  | (?P<op>.)
""", re.VERBOSE | re.DOTALL)


def _line_starts(text):
    starts = [0]
    idx = text.find("\n")
    while idx != -1:
        starts.append(idx + 1)
        idx = text.find("\n", idx + 1)
    return starts


def strip_line_comment(line):
    """行末の `//` コメントを落とす（文字列の中の // は残す）。"""
    i, n, in_str = 0, len(line), False
    while i < n:
        c = line[i]
        if in_str:
            if c == "\\":
                i += 2
                continue
            if c == '"':
                in_str = False
        else:
            if c == '"':
                in_str = True
            elif c == "/" and i + 1 < n and line[i + 1] == "/":
                return line[:i]
        i += 1
    return line


class Header(object):
    __slots__ = ("line", "kind", "name", "raw")

    def __init__(self, line, kind, name, raw):
        self.line = line
        self.kind = kind
        self.name = name
        self.raw = raw

    @property
    def display_name(self):
        return self.name.split("::", 1)[0]

    @property
    def unique_name(self):
        parts = self.name.split("::", 1)
        return parts[1] if len(parts) > 1 else None


def _header_fields(line_text):
    """ヘッダ行なら TAB 区切りのフィールド列、そうでなければ None。"""
    if not line_text or line_text[0] in ("/", " ", "\t", "\n"):
        return None
    body = strip_line_comment(line_text)
    if body.count("\t") < 3:
        return None
    fields = body.split("\t")
    if len(fields) < 4:
        return None
    if not HEADER_KIND_RE.match(fields[1].strip()):
        return None
    return fields


def tokenize(text):
    """rAthena スクリプトをトークン列にする。

    戻り値: (tokens, headers)
      tokens  … Token のリスト（コメントと空白は含まない）
      headers … Header のリスト（ブレース深さ 0 の NPC ヘッダ行）
    """
    tokens = []
    headers = []
    starts = _line_starts(text)
    depth = 0
    pos, n = 0, len(text)

    def lineno(p):
        return bisect.bisect_right(starts, p)

    def emit_chunk(chunk, line):
        """ヘッダ行のフィールドなど、通常トークナイズしたいひとかたまり。"""
        for m in TOKEN_RE.finditer(chunk):
            kind = m.lastgroup
            if kind in ("nl", "ws", "bc", "bco", "lc"):
                continue
            val = m.group()
            if kind in ("str", "ustr"):
                tokens.append(Token("str", val[1:-1] if kind == "str" else val[1:], line))
            elif kind == "num":
                tokens.append(Token("num", val, line))
            elif kind == "id":
                tokens.append(Token("word", val, line))
            else:
                tokens.append(Token("op", val, line))

    while pos < n:
        at_line_start = (pos == 0 or text[pos - 1] == "\n")
        if at_line_start and depth == 0:
            eol = text.find("\n", pos)
            line_text = text[pos:eol if eol != -1 else n]
            fields = _header_fields(line_text)
            if fields is not None:
                line = lineno(pos)
                kind = fields[1].strip()
                name = fields[2]
                headers.append(Header(line, kind, name, line_text))
                # 座標など
                emit_chunk(fields[0], line)
                # 種別（duplicate(src) の src は exname 参照なので厳密比較する）
                dup = re.match(r"^duplicate\((.*)\)$", kind)
                if dup:
                    tokens.append(Token("word", "duplicate", line))
                    tokens.append(Token("op", "(", line))
                    tokens.append(Token("dupsrc", dup.group(1), line))
                    tokens.append(Token("op", ")", line))
                else:
                    tokens.append(Token("word", kind, line))
                # 名前フィールド（表示名の扱いだけ特別）
                tokens.append(Token("name", name, line))
                # 残りのフィールド（sprite・座標・そのまま続く本体）
                rest = "\t".join(fields[3:])
                before = len(tokens)
                emit_chunk(rest, line)
                for t in tokens[before:]:
                    if t.kind == "op" and t.value == "{":
                        depth += 1
                    elif t.kind == "op" and t.value == "}":
                        depth -= 1
                pos = eol + 1 if eol != -1 else n
                continue

        m = TOKEN_RE.match(text, pos)
        if m is None:  # 起こらないはずだが安全のため
            pos += 1
            continue
        kind = m.lastgroup
        val = m.group()
        if kind not in ("nl", "ws", "bc", "bco", "lc"):
            line = lineno(pos)
            if kind in ("str", "ustr"):
                tokens.append(Token("str", val[1:-1] if kind == "str" else val[1:], line))
            elif kind == "num":
                tokens.append(Token("num", val, line))
            elif kind == "id":
                tokens.append(Token("word", val, line))
            else:
                tokens.append(Token("op", val, line))
                if val == "{":
                    depth += 1
                elif val == "}":
                    depth -= 1
        pos = m.end()
        if m.end() == m.start():  # 念のため無限ループ防止
            pos += 1

    return tokens, headers


# ---------------------------------------------------------------- 文脈の解析

def prev_significant(tokens, i):
    """`(` と `,` を読み飛ばした直前のトークン。"""
    j = i - 1
    while j >= 0:
        t = tokens[j]
        if t.kind == "op" and t.value in ("(", ","):
            j -= 1
            continue
        return t
    return None


def menu_option_indices(tokens):
    """select / prompt / menu の選択肢になる文字列トークンの添字集合。"""
    marked = set()
    n = len(tokens)
    for i, t in enumerate(tokens):
        if t.kind != "word" or t.value not in MENU_COMMANDS:
            continue
        if t.value in ("select", "prompt"):
            j = i + 1
            if j >= n or not (tokens[j].kind == "op" and tokens[j].value == "("):
                continue
            depth = 0
            while j < n:
                tk = tokens[j]
                if tk.kind == "op" and tk.value == "(":
                    depth += 1
                elif tk.kind == "op" and tk.value == ")":
                    depth -= 1
                    if depth == 0:
                        break
                elif tk.kind == "str":
                    marked.add(j)
                j += 1
        else:  # menu "opt",Label,"opt",Label...
            j = i + 1
            depth = 0
            while j < n:
                tk = tokens[j]
                if tk.kind == "op" and tk.value == "(":
                    depth += 1
                elif tk.kind == "op" and tk.value == ")":
                    depth -= 1
                elif tk.kind == "op" and tk.value == ";" and depth <= 0:
                    break
                elif tk.kind == "str":
                    marked.add(j)
                j += 1
    return marked


#: 文字列比較を行う関数（引数の文字列は比較値なので訳語が一意である必要がある）
COMPARE_FUNCS = frozenset(["compare", "strcmp", "strpos"])


def comparison_indices(tokens):
    """比較に使われる文字列トークンの添字集合。

    - `== ` / `!=` の直前か直後にあるもの
    - compare() / strcmp() / strpos() の引数
    """
    marked = set()
    n = len(tokens)
    for i, t in enumerate(tokens):
        if t.kind != "str":
            continue
        if i > 0 and tokens[i - 1].kind == "op" and tokens[i - 1].value in ("==", "!="):
            marked.add(i)
        elif i + 1 < n and tokens[i + 1].kind == "op" and tokens[i + 1].value in ("==", "!="):
            marked.add(i)

    for i, t in enumerate(tokens):
        if t.kind != "word" or t.value not in COMPARE_FUNCS:
            continue
        j = i + 1
        if j >= n or not (tokens[j].kind == "op" and tokens[j].value == "("):
            continue
        depth = 0
        while j < n:
            tk = tokens[j]
            if tk.kind == "op" and tk.value == "(":
                depth += 1
            elif tk.kind == "op" and tk.value == ")":
                depth -= 1
                if depth == 0:
                    break
            elif tk.kind == "str":
                marked.add(j)
            j += 1
    return marked


# ---------------------------------------------------------------- strnpcinfo

#: 表示用（結果をそのまま画面に出すだけ）のコマンド
STRNPCINFO_DISPLAY_CMDS = frozenset("""
mes mesf npctalk unittalk dispbottom message announce mapannounce areaannounce
showscript select prompt menu title logmes debugmes
""".split())

#: 結果を識別子・キーとして使うコマンド（表示名を変えると壊れる）
STRNPCINFO_IDENT_CMDS = frozenset("""
getd setd callfunc callsub doevent donpcevent getvariableofnpc getnpcid
enablenpc disablenpc hideonnpc hideoffnpc cloakonnpc cloakoffnpc
setnpcdisplay npcshopitem npcshopattach query_sql escape_sql instance_create
""".split()) | SAME_REQUIRED_COMMANDS


def _statement_head(tokens, i):
    """tokens[i] を含む文の先頭コマンド語。見つからなければ None。"""
    j = i - 1
    head = None
    while j >= 0:
        t = tokens[j]
        if t.kind == "op" and t.value in (";", "{", "}"):
            break
        if t.kind == "word":
            head = t.value
        j -= 1
    return head


def _enclosing_call(tokens, i):
    """tokens[i] を囲む関数呼び出しの名前（`word (` の word）。無ければ None。"""
    depth = 0
    j = i - 1
    while j >= 0:
        t = tokens[j]
        if t.kind == "op":
            if t.value == ")":
                depth += 1
            elif t.value == "(":
                if depth == 0:
                    if j > 0 and tokens[j - 1].kind == "word":
                        return tokens[j - 1].value
                    return None
                depth -= 1
            elif t.value in (";", "{", "}") and depth == 0:
                return None
        j -= 1
    return None


def strnpcinfo_usages(tokens):
    """本文の `strnpcinfo(<n>)` の使われ方を [(引数, 用途, 行), ...] で返す。

    用途:
      cmp    … `==` / `!=` / compare() 等の比較（表示名を変えると分岐が壊れる）
      tag    … `"[" + strnpcinfo(1) + "]"` の話者タグ生成（表示名を変えると
               タグも日本語になるだけで安全）
      concat … タグ以外の文字列連結（キー生成の可能性がある）
      ident  … 識別子として使うコマンドの引数
      assign … 変数への代入（追跡していないので保守的に拾う）
      disp   … mes / npctalk などの表示専用
      other  … 判定できなかったもの
    引数 0/1 は可視名なので表示名の変更で値が変わる。2（`#` 以降）/ 3（exname）/
    4（マップ名）は `日本語#suffix::旧フル名` 形式なら値が変わらないので安全だが、
    「その NPC が個体ごとに分岐しているか」を知るために用途は同じように記録する。
    """
    out = []
    n = len(tokens)
    for i, t in enumerate(tokens):
        if t.kind != "word" or t.value != "strnpcinfo":
            continue
        if i + 1 >= n or not (tokens[i + 1].kind == "op" and tokens[i + 1].value == "("):
            continue
        depth, k, arg = 0, i + 1, None
        while k < n:
            tk = tokens[k]
            if tk.kind == "op" and tk.value == "(":
                depth += 1
            elif tk.kind == "op" and tk.value == ")":
                depth -= 1
                if depth == 0:
                    break
            elif arg is None and depth == 1 and tk.kind == "num":
                try:
                    arg = int(tk.value, 0)
                except ValueError:
                    arg = None
            k += 1
        close = k
        if arg is None:
            arg = -1

        before = tokens[i - 1] if i > 0 else None
        after = tokens[close + 1] if close + 1 < n else None
        b_is = lambda v: before is not None and before.kind == "op" and before.value == v
        a_is = lambda v: after is not None and after.kind == "op" and after.value == v

        if b_is("==") or b_is("!=") or a_is("==") or a_is("!="):
            use = "cmp"
        elif b_is("+") or a_is("+"):
            lhs = tokens[i - 2] if i >= 2 else None
            rhs = tokens[close + 2] if close + 2 < n else None
            is_tag = (b_is("+") and lhs is not None and lhs.kind == "str"
                      and lhs.value.endswith("[")
                      and a_is("+") and rhs is not None and rhs.kind == "str"
                      and rhs.value.startswith("]"))
            use = "tag" if is_tag else "concat"
        else:
            call = _enclosing_call(tokens, i)
            head = _statement_head(tokens, i)
            if call in COMPARE_FUNCS:
                use = "cmp"
            elif call in STRNPCINFO_IDENT_CMDS or head in STRNPCINFO_IDENT_CMDS:
                use = "ident"
            elif call in STRNPCINFO_DISPLAY_CMDS or head in STRNPCINFO_DISPLAY_CMDS:
                use = "disp"
            elif b_is("=") or b_is(","):
                use = "assign"
            else:
                use = "other"
        out.append((arg, use, t.line))
    return out


#: 表示名を変えると挙動が変わりうる用途
STRNPCINFO_RISKY = frozenset(["cmp", "concat", "ident", "assign", "other"])


# ---------------------------------------------------------------- 検査結果

class Result(object):
    def __init__(self, title):
        self.title = title
        self.items = []      # (severity, item, message)

    def add(self, severity, item, message):
        self.items.append((severity, item, message))

    @property
    def status(self):
        if any(s == FAIL for s, _, _ in self.items):
            return FAIL
        return PASS

    @property
    def warn_count(self):
        return sum(1 for s, _, _ in self.items if s == WARN)

    def render(self):
        out = ["=== %s ===" % self.title]
        for sev, item, msg in self.items:
            first = True
            for line in msg.split("\n"):
                if first:
                    out.append("  %-4s %-16s %s" % (sev, item, line))
                    first = False
                else:
                    out.append("  %-4s %-16s %s" % ("", "", line))
        out.append("  => %s" % self.status)
        return "\n".join(out)


# ---------------------------------------------------------------- 個別検査

def check_encoding(res, raw_bytes, path_label):
    problems = []
    if raw_bytes.startswith(b"\xef\xbb\xbf"):
        problems.append("UTF-8 BOM があります")
    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        res.add(FAIL, "1.エンコーディング", "UTF-8 として読めません: %s" % exc)
        return None
    if "\r" in text:
        n = text.count("\r")
        problems.append("CR を含みます（%d 個。LF に揃えること）" % n)
    try:
        text.encode("cp932")
    except UnicodeEncodeError as exc:
        bad = text[exc.start:exc.end]
        line = text.count("\n", 0, exc.start) + 1
        problems.append("CP932 に変換できない文字 %r（%d 行目, U+%04X）"
                        % (bad, line, ord(bad[0]) if bad else 0))
    for ch, why in FORBIDDEN_CHARS.items():
        if ch in text:
            line = text.count("\n", 0, text.index(ch)) + 1
            problems.append("%s（%d 行目）" % (why, line))
    kana = [c for c in text if "｡" <= c <= "ﾟ"]
    if kana:
        problems.append("半角カナ U+FF61-FF9F を含みます（%d 文字）" % len(kana))
    astral = [c for c in text if ord(c) > 0xFFFF]
    if astral:
        problems.append("BMP 外の文字を含みます（%d 文字: %s）"
                        % (len(astral), " ".join("U+%05X" % ord(c) for c in astral[:5])))
    m = BACKSLASH_AFTER_NONASCII_RE.search(text)
    if m:
        line = text.count("\n", 0, m.start()) + 1
        ctx = text[max(0, m.start() - 20):m.end() + 20].replace("\n", "\\n")
        problems.append("非 ASCII 文字の直後に `\\` があります（%d 行目）: ...%s..."
                        % (line, ctx))

    if problems:
        res.add(FAIL, "1.エンコーディング", "\n".join(problems))
    else:
        res.add(PASS, "1.エンコーディング",
                "UTF-8 / BOM なし / CR なし / CP932 変換可 / 禁止文字なし（%d バイト）"
                % len(raw_bytes))
    return text


# ---------------------------------------------------------------- エスケープ検査
#
# rAthena の文字列パーサ（src/map/script.cpp:1342-1352）は
#   直前バイトが 0x7E 以下のときだけ 0x5C を「エスケープ」として扱い、
#   skip_escaped_c()（src/common/strlib.cpp:857-）で長さを測って sv_unescape_c() に渡す。
# skip_escaped_c は `\` の次が SV_ESCAPE_C_SUPPORTED（"abtnvfr?\"'\\"）/ x / 0-3 の
# いずれでもないとき `\` の 1 バイトしか返さないため、sv_unescape_c は
#   ShowWarning("sv_unescape_c: empty escape sequence")
# を出したうえで**未初期化バイト**を文字列に混ぜる（strlib.cpp:774-776 と
# script.cpp:1347-1350 の n != 1 経路）。`\「` のように `\` の直後が
# マルチバイト文字の場合もこれに該当する。
SV_ESCAPE_C_SUPPORTED = set(b"abtnvfr?\"'\\")
_HEXDIGITS = set(b"0123456789abcdefABCDEF")


def bad_escapes(literal):
    """文字列リテラル 1 個の中の不正なエスケープを [(理由, 該当文字列), ...] で返す。

    rAthena と同じく CP932 バイト列の上で、直前バイト <= 0x7E のときだけ
    エスケープとして解釈する（日本語の 2 バイト目 0x5C を誤検出しないため）。
    """
    try:
        raw = literal.encode("cp932")
    except UnicodeEncodeError:
        return []          # CP932 に変換できない時点で別項目が FAIL 済み
    out = []
    i = 0
    prev = 0x22            # 文字列の開始クォート
    n = len(raw)
    while i < n:
        if prev > 0x7E or raw[i] != 0x5C:
            prev = raw[i]
            i += 1
            continue
        if i + 1 >= n:
            out.append(("文字列末尾の `\\`（sv_unescape_c: empty escape sequence）", "\\"))
            break
        c = raw[i + 1]
        if c == 0x78:                       # \x<hex>
            j = i + 2
            while j < n and raw[j] in _HEXDIGITS:
                j += 1
            if j == i + 2:
                out.append(("`\\x` に 16 進数が続いていない", "\\x"))
                prev = 0x78
                i += 2
                continue
            prev = raw[j - 1]
            i = j
            continue
        if 0x30 <= c <= 0x33:               # \0 - \3 （8 進）
            j = i + 2
            while j < n and j < i + 4 and 0x30 <= raw[j] <= 0x37:
                j += 1
            prev = raw[j - 1]
            i = j
            continue
        if c in SV_ESCAPE_C_SUPPORTED:
            prev = c
            i += 2
            continue
        # ここに来るものは skip_escaped_c が長さ 1 を返す = empty escape sequence
        if c > 0x7F:
            try:
                shown = raw[i + 1:i + 3].decode("cp932")
            except Exception:
                shown = "\\x%02X" % c
            why = ("`\\` の直後が非 ASCII 文字 %r（sv_unescape_c: empty escape sequence "
                   "になり文字列に未初期化バイトが混ざる）" % shown)
        else:
            shown = chr(c)
            why = ("未対応のエスケープ `\\%s`（sv_unescape_c: empty escape sequence）"
                   % shown)
        out.append((why, "\\" + shown))
        prev = 0x5C
        i += 1
    return out



# ---------------------------------------------------------------- 1c. parse_variable の生バイト括弧走査
# src/map/script.cpp parse_variable(): 変数名の直後が '[' のとき、対応する ']' を
#     for( p2 = p, i = 0, j = 1; p; ++ i ) {
#         if( *p ++ == ']' && --(j) == 0 ) break;
#         if( *p == '[' ) ++ j;
#     }
# という「文字列リテラルも 2 バイト文字も見ない生バイト走査」で探す（終了条件は p が非 NULL =
# 事実上なし）。CP932 で 2 バイト目が 0x5B '[' / 0x5D ']' になる文字（ー ゼ ゾ ‐ など計 104 字）が
# 添字式 `var[ ... ]` の中の文字列に入ると数が合わなくなり、走査がファイル末尾を越えて
# ヒープを読み進む。運が悪いと map-server が「Loading NPCs...」直後に SIGSEGV で落ちる
# （落ちるかどうかはヒープ配置次第で不定。2026-09-23 に merchants/elemental_trader.txt の
# `.@Items[select("ミスティックフローズン:...")]` で実際に発生）。
# parse_variable は文頭だけでなく parse_simpleexpr からも呼ばれるため、右辺の添字式も対象。

def _is_lead(b):
    return 0x81 <= b <= 0x9F or 0xE0 <= b <= 0xFC


def _walk_code(cp):
    """CP932 バイト列を rAthena のスクリプト字句規則で歩き、文字列/コメントの外にある
    バイトの位置だけを yield する。

    parse_variable() が走るのはスクリプト本体（`{` 〜 `}`）の中だけなので、波括弧の
    深さが 0 の位置（NPC ヘッダ行など）は yield しない。ヘッダの表示名に `[Thomas]` の
    ような角括弧や「ー」が含まれても、それは npc_parsesrcfile が sscanf で読むだけで
    スクリプトパーサには渡らない。"""
    n, i, depth = len(cp), 0, 0
    while i < n:
        b = cp[i]
        if b == 0x22:                                   # 文字列
            i += 1
            while i < n and cp[i] != 0x22:
                if _is_lead(cp[i]):
                    i += 2
                elif cp[i] == 0x5C and cp[i - 1] <= 0x7E:
                    i += 2
                else:
                    i += 1
            i += 1
            continue
        if b == 0x2F and i + 1 < n and cp[i + 1] == 0x2F:    # // コメント
            while i < n and cp[i] != 0x0A:
                i += 1
            continue
        if b == 0x2F and i + 1 < n and cp[i + 1] == 0x2A:    # /* */ コメント
            j = cp.find(b"*/", i + 2)
            i = n if j < 0 else j + 2
            continue
        if _is_lead(b):
            i += 2
            continue
        if b == 0x7B:                                   # {
            depth += 1
        elif b == 0x7D:                                 # }
            depth = max(0, depth - 1)
        if depth > 0:
            yield i
        i += 1


def _raw_bracket_scan(cp, pos):
    """parse_variable と同じ生バイト走査。pos は '[' の位置。止まった ']' の位置か、
    ファイル末尾まで釣り合わなければ None。"""
    n, p, j = len(cp), pos, 1
    while p < n:
        c = cp[p]
        p += 1
        if c == 0x5D:
            j -= 1
            if j == 0:
                return p - 1
        if p < n and cp[p] == 0x5B:
            j += 1
    return None


def scan_index_brackets(cp):
    """文字列/コメント外の各 '[' について (pos, raw_end, true_end) を返す。"""
    code_pos = list(_walk_code(cp))
    code_set = set(code_pos)
    out = []
    for k, i in enumerate(code_pos):
        if cp[i] != 0x5B:
            continue
        depth, true_end = 1, None
        for q in code_pos[k + 1:]:
            if cp[q] == 0x5B:
                depth += 1
            elif cp[q] == 0x5D:
                depth -= 1
                if depth == 0:
                    true_end = q
                    break
        out.append((i, _raw_bracket_scan(cp, i), true_end))
    return out


def _offending_bytes(cp, start, end):
    """[start, end] の範囲で生走査を狂わせるバイト（文字列内の '[' ']' と、2 バイト目が
    0x5B/0x5D の文字）を列挙する。"""
    found = []
    i = start
    while i <= end and i < len(cp):
        b = cp[i]
        if _is_lead(b) and i + 1 < len(cp):
            if cp[i + 1] in (0x5B, 0x5D):
                found.append(cp[i:i + 2].decode("cp932", "replace"))
            i += 2
            continue
        i += 1
    return found


def check_index_brackets(res, u_text, j_text, max_detail=8):
    """1c. 添字式 `var[...]` に対する parse_variable の生バイト走査が本来の ']' で止まるか。"""
    cp = j_text.encode("cp932")
    j_scan = scan_index_brackets(cp)
    u_scan = None
    if u_text is not None:
        u_cp = u_text.encode("latin-1", "replace")
        u_scan = scan_index_brackets(u_cp)
    problems, warns = [], []
    for idx, (pos, raw_end, true_end) in enumerate(j_scan):
        if raw_end == true_end:
            continue
        line = cp.count(b"\n", 0, pos) + 1
        bad = _offending_bytes(cp, pos, true_end if true_end is not None else len(cp) - 1)
        # 文字列外の '[' なので添字。上流でも同じ場所で同じズレなら上流由来（WARN）
        same_in_upstream = (u_scan is not None and idx < len(u_scan)
                            and u_scan[idx][1] != u_scan[idx][2])
        if raw_end is None:
            why = "走査がファイル末尾を越える（map-server が SIGSEGV で落ちる可能性）"
        else:
            raw_line = cp.count(b"\n", 0, raw_end) + 1
            why = "走査が本来の ']' ではなく %d 行目の ']' で止まる（直後が = だと誤って代入扱い）" % raw_line
        msg = "%d 行目の添字 `[`: %s。原因文字: %s" % (
            line, why, " ".join(repr(c) for c in bad) if bad else "（文字列内の [ ] など）")
        (warns if same_in_upstream else problems).append(msg)
    if problems:
        shown = problems[:max_detail]
        more = "" if len(problems) <= max_detail else "\n  …他 %d 件" % (len(problems) - max_detail)
        res.add(FAIL, "1c.添字走査",
                "添字式の中の文字列に CP932 2 バイト目が [ ] になる文字（ー ゼ ゾ ‐ など）があります。"
                "言い換えるか、その select/文字列を添字の外へ出せない場合は英語表記にすること:\n  "
                + "\n  ".join(shown) + more)
    elif warns:
        res.add(WARN, "1c.添字走査", "上流由来のズレ %d 件（翻訳による悪化なし）" % len(warns))
    else:
        res.add(PASS, "1c.添字走査", "添字 %d 箇所すべて生走査が本来の ']' で止まります" % len(j_scan))


def check_escapes(res, u_toks, j_toks, max_detail=10):
    """翻訳版の文字列リテラル内のエスケープを検査する（上流由来のものは除外）。"""
    upstream_bad = set()
    for t in u_toks:
        if t.kind == "str":
            for _why, seq in bad_escapes(t.value):
                upstream_bad.add(seq)

    problems = []
    inherited = 0
    checked = 0
    for t in j_toks:
        if t.kind != "str":
            continue
        checked += 1
        for why, seq in bad_escapes(t.value):
            if seq in upstream_bad:
                inherited += 1
                continue
            problems.append("%d 行目: %s\n    -> %r" % (t.line, why, t.value[:70]))

    if problems:
        body = problems[:max_detail]
        if len(problems) > max_detail:
            body.append("他 %d 件" % (len(problems) - max_detail))
        res.add(FAIL, "1b.エスケープ", "\n".join(body))
        return
    msg = "文字列 %d 個に不正なエスケープなし" % checked
    if inherited:
        msg += "（上流にも同じものがある %d 件は除外）" % inherited
    res.add(PASS, "1b.エスケープ", msg)


def split_npc_name(name):
    """ヘッダの名前フィールドを (表示名, exname) に分ける。"""
    if "::" in name:
        disp, uniq = name.split("::", 1)
        return disp, uniq
    return name, name


def split_display_name(display):
    """表示名を (可視部分, `#` 以降を含む suffix) に分ける。"""
    idx = display.find("#")
    if idx < 0:
        return display, ""
    return display[:idx], display[idx:]


def check_display_name(u_disp, j_disp):
    """新しい表示名の妥当性。(ok, 理由) を返す。

    - 可視部分が空でない
    - `::` / タブ / 制御文字 / `//` を含まない
    - `#suffix` は上流と完全一致（`strnpcinfo(2)` が変わらないようにするため。
      src/map/script.cpp BUILDIN_FUNC(strnpcinfo) の case 2 は nd->name の `#` 以降）
    - CP932 に変換でき、CP932 バイト長が NPC_NAME_LENGTH（50）以内
    """
    if not j_disp:
        return False, "表示名が空です"
    if "::" in j_disp:
        return False, "表示名に `::` は使えません: %r" % j_disp
    if "\t" in j_disp or any(ord(c) < 0x20 or ord(c) == 0x7F for c in j_disp):
        return False, "表示名にタブ / 制御文字が含まれています: %r" % j_disp
    if "//" in j_disp:
        return False, "表示名に `//`（コメント開始）は使えません: %r" % j_disp
    u_vis, u_hidden = split_display_name(u_disp)
    j_vis, j_hidden = split_display_name(j_disp)
    if not j_vis:
        return False, "表示名の可視部分（`#` の前）が空です: %r" % j_disp
    if u_hidden != j_hidden:
        return False, ("表示名の `#` 以降は上流と同じにしてください"
                       "（strnpcinfo(2) が変わります。上流 %r / 翻訳 %r）"
                       % (u_hidden or "(なし)", j_hidden or "(なし)"))
    for ch, why in FORBIDDEN_CHARS.items():
        if ch in j_disp:
            return False, "表示名に使用禁止文字 %s: %s" % (ch, why)
    try:
        nbytes = len(j_disp.encode("cp932"))
    except UnicodeEncodeError:
        return False, "表示名に CP932 で表せない文字があります: %r" % j_disp
    if nbytes > NPC_NAME_LENGTH:
        return False, ("表示名が長すぎます: %r は CP932 %d バイト（NPC_NAME_LENGTH=%d）"
                       % (j_disp, nbytes, NPC_NAME_LENGTH))
    return True, None


def name_tokens_equal(u_name, j_name):
    """ヘッダ名フィールドの許容判定。(ok, 理由) を返す。

    許容するのは「表示名だけを変え、exname を上流のまま残す」形だけ:
        上流 `D::U`  → 翻訳 `X::U`          （従来どおり）
        上流 `U`     → 翻訳 `X::U`          （`::` を新設。U は上流フル名と完全一致）
    `X` の `#suffix` は上流の表示名側と一致していること。
    """
    if u_name == j_name:
        return True, None
    u_disp, u_uniq = split_npc_name(u_name)
    if "::" not in j_name:
        if "::" in u_name:
            return False, "翻訳版に ::ユニーク名 がありません（%r -> %r）" % (u_name, j_name)
        return False, ("::ユニーク名が無いヘッダの名前は変更できません"
                       "（他ファイルからの参照名を兼ねるため）。"
                       "日本語化するなら `新表示名::%s` の形にしてください: %r -> %r"
                       % (u_name, u_name, j_name))
    j_disp, j_uniq = j_name.split("::", 1)
    if u_uniq != j_uniq:
        if "::" in u_name:
            return False, ("::以降のユニーク名は変更できません（%r -> %r）"
                           % (u_uniq, j_uniq))
        return False, ("`::` を足すときのユニーク名は上流のフル名（`#suffix` 込み）と"
                       "完全一致させてください（期待 %r / 実際 %r）" % (u_uniq, j_uniq))
    ok, why = check_display_name(u_disp, j_disp)
    if not ok:
        return False, why
    return True, ("rename", u_disp, j_disp, "::" not in u_name)


def check_tokens(res, u_toks, j_toks, u_label, j_label):
    """トークン列の完全一致。戻り値: (ok, renames, exname_renames)

    renames        … 表示名の変更（旧表示名 -> 新表示名）。exname は変わっていない。
    exname_renames … exname そのものが変わった分（上流名が非 ASCII で再現不可な場合のみ）。
                     文字列リテラル側の書き換えを許容してよいのはこちらだけ。
    """
    renames = {}
    exname_renames = {}
    problems = []
    limit = min(len(u_toks), len(j_toks))
    mismatch = None
    for i in range(limit):
        ut, jt = u_toks[i], j_toks[i]
        if ut.kind != jt.kind:
            mismatch = (i, "種別が違います（%s / %s）" % (ut.kind, jt.kind))
            break
        if ut.kind == "str":
            continue
        if ut.kind == "name":
            ok, info = name_tokens_equal(ut.value, jt.value)
            if not ok:
                # 上流 NPC 名が非 ASCII バイト（韓国語 EUC-KR の残骸など）を含み
                # UTF-8 の翻訳版では同じバイト列を再現できない場合の改名は許容する。
                # 3.ヘッダ の同じ例外と揃える（他ファイルからの参照は 5.外部参照 で確認）。
                if "::" not in ut.value and any(ord(c) >= 0x80 for c in ut.value):
                    renames[ut.value] = jt.value
                    exname_renames[ut.value] = jt.value
                    continue
                mismatch = (i, info)
                break
            if isinstance(info, tuple) and info[0] == "rename":
                renames[info[1]] = info[2]
            continue
        if ut.value != jt.value:
            mismatch = (i, "トークンが違います（%r / %r）" % (ut.value, jt.value))
            break

    if mismatch is None and len(u_toks) != len(j_toks):
        i = limit
        extra_u = u_toks[i].display() if i < len(u_toks) else "(なし)"
        extra_j = j_toks[i].display() if i < len(j_toks) else "(なし)"
        u_line = u_toks[i].line if i < len(u_toks) else u_toks[-1].line
        j_line = j_toks[i].line if i < len(j_toks) else j_toks[-1].line
        mismatch = (i, "トークン数が違います（上流 %d / 翻訳 %d）: 上流 %s / 翻訳 %s"
                    % (len(u_toks), len(j_toks), extra_u, extra_j))
        problems.append(_context_text(u_toks, j_toks, i, u_label, j_label, u_line, j_line))

    if mismatch is not None:
        i, why = mismatch
        u_line = u_toks[i].line if i < len(u_toks) else (u_toks[-1].line if u_toks else 0)
        j_line = j_toks[i].line if i < len(j_toks) else (j_toks[-1].line if j_toks else 0)
        msg = ["最初の相違: 上流 %s:%d / 翻訳 %s:%d" % (u_label, u_line, j_label, j_line),
               "  %s" % why]
        if not problems:
            problems.append(_context_text(u_toks, j_toks, i, u_label, j_label, u_line, j_line))
        msg.extend(problems)
        res.add(FAIL, "2.トークン構造", "\n".join(msg))
        return False, renames, exname_renames

    res.add(PASS, "2.トークン構造",
            "%d トークン一致（文字列は \"STR\" に置換・コメント除去・空白正規化）"
            % len(u_toks))
    return True, renames, exname_renames


def _context_text(u_toks, j_toks, i, u_label, j_label, u_line, j_line):
    lo, hi = max(0, i - 4), i + 5
    u_ctx = " ".join(t.display() for t in u_toks[lo:hi])
    j_ctx = " ".join(t.display() for t in j_toks[lo:hi])
    return ("  前後トークン（上流）: %s\n"
            "  前後トークン（翻訳）: %s" % (u_ctx, j_ctx))


def check_headers(res, u_heads, j_heads, renames):
    if len(u_heads) != len(j_heads):
        res.add(FAIL, "3.ヘッダ",
                "ヘッダ行数が違います（上流 %d / 翻訳 %d）" % (len(u_heads), len(j_heads)))
        return
    changed, fixed, added = 0, 0, 0
    problems, nonascii = [], []
    for uh, jh in zip(u_heads, j_heads):
        if uh.kind != jh.kind:
            problems.append("%d 行目: 種別が違います（%s -> %s）" % (uh.line, uh.kind, jh.kind))
            continue
        if uh.name == jh.name:
            fixed += 1
            continue
        ok, info = name_tokens_equal(uh.name, jh.name)
        if ok and isinstance(info, tuple) and len(info) > 3 and info[3]:
            added += 1
        if not ok:
            # 上流の NPC 名に非 ASCII バイト（韓国語 EUC-KR の残骸。例 assassin_skills.txt の
            # "\xa1\xa1#crypt"）が含まれる場合、UTF-8 の翻訳版では同じバイト列を書けないので
            # 改名を許容する（WARN）。他ファイルから参照されていないことは 5.外部参照で確認する。
            if any(ord(c) >= 0x80 for c in uh.name):
                nonascii.append("%d 行目: 上流名 %r は非 ASCII バイトを含むため再現不可 → %r に改名"
                                % (uh.line, uh.name, jh.name))
                changed += 1
            else:
                problems.append("%d 行目: %s" % (uh.line, info))
        else:
            changed += 1
    if problems:
        res.add(FAIL, "3.ヘッダ", "\n".join(problems))
    else:
        res.add(PASS, "3.ヘッダ",
                "%d 件（表示名を変更 %d［うち `::exname` 新設 %d］/ 不変 %d）。"
                "exname・`#suffix`・座標・種別・sprite は不変"
                % (len(u_heads), changed, added, fixed))
        if nonascii:
            res.add(WARN, "3.ヘッダ", "\n".join(nonascii)
                    + "\n  ※ 改名した NPC が他ファイルから doevent/enablenpc 等で参照されていないことを確認すること")


def _rename_ok(u_str, j_str, exname_renames):
    """exname が実際に変わった NPC を指す文字列だけ、追随した書き換えを許容する。

    表示名だけを変えた場合（`日本語::旧フル名`）は exname が変わらないので、
    `"旧フル名"` / `"旧フル名::OnEvent"` という参照は**そのままでなければならない**。
    許容するのは上流名が非 ASCII バイトで再現できず、やむなく exname ごと
    改名した場合（check_tokens の例外）だけ。
    """
    if u_str == j_str:
        return True
    if not exname_renames:
        return False
    if "::" in u_str:
        u_disp, u_rest = u_str.split("::", 1)
        if u_disp in exname_renames and j_str == "%s::%s" % (exname_renames[u_disp], u_rest):
            return True
        return False
    return u_str in exname_renames and j_str == exname_renames[u_str]


def check_strings(res, u_toks, j_toks, exname_renames, max_detail=8):
    pairs = [(i, u_toks[i], j_toks[i]) for i in range(len(u_toks)) if u_toks[i].kind == "str"]
    menu_idx = menu_option_indices(u_toks)
    cmp_idx = comparison_indices(u_toks)

    fails, warns = [], []
    n_same_required = n_event = n_cmp = n_menu = n_fmt = 0

    for i, ut, jt in pairs:
        u, j = ut.value, jt.value

        prev = prev_significant(u_toks, i)
        if prev is not None and prev.kind == "word" and prev.value in SAME_REQUIRED_COMMANDS:
            n_same_required += 1
            if not _rename_ok(u, j, exname_renames):
                fails.append("%d 行目: `%s` の第 1 引数は識別子なので翻訳できません: %r -> %r"
                             % (ut.line, prev.value, u, j))

        # select/prompt/menu の選択肢文字列は、連続する ':' 区切りの中に空の項目が
        # あると（例: "...A!::Cancel" の A と Cancel の間）偶然 "::" を含むことが
        # あるが、これは NPC::Event 参照ではない。選択肢と分かっている文字列は
        # ここでは対象から除外し、選択肢個数チェック（下の i in menu_idx）に任せる。
        if "::" in u and i not in menu_idx:
            n_event += 1
            if not _rename_ok(u, j, exname_renames):
                fails.append("%d 行目: イベント / NPC 参照（:: を含む）は変更できません: %r -> %r"
                             % (ut.line, u, j))

        if i in menu_idx:
            n_menu += 1
            if u.count(":") != j.count(":"):
                fails.append("%d 行目: 選択肢の `:` の数が違います（上流 %d / 翻訳 %d）: %r -> %r"
                             % (ut.line, u.count(":"), j.count(":"), u, j))

        u_fmt = FORMAT_SPEC_RE.findall(u)
        j_fmt = FORMAT_SPEC_RE.findall(j)
        if u_fmt or j_fmt:
            n_fmt += 1
            if u_fmt != j_fmt:
                fails.append("%d 行目: 書式指定子の並びが違います（上流 %s / 翻訳 %s）: %r -> %r"
                             % (ut.line, u_fmt, j_fmt, u, j))

        u_col = COLOR_CODE_RE.findall(u)
        j_col = COLOR_CODE_RE.findall(j)
        if len(u_col) != len(j_col):
            warns.append("%d 行目: 色コード ^RRGGBB の数が違います（上流 %d / 翻訳 %d）: %r -> %r"
                         % (ut.line, len(u_col), len(j_col), u, j))

    # 比較文脈の訳語の一意性
    cmp_map, cmp_rev = {}, {}
    other_map = {}
    for i, ut, jt in pairs:
        if i in cmp_idx:
            n_cmp += 1
            cmp_map.setdefault(ut.value, {}).setdefault(jt.value, ut.line)
            cmp_rev.setdefault(jt.value, {}).setdefault(ut.value, ut.line)
        else:
            other_map.setdefault(ut.value, {}).setdefault(jt.value, ut.line)

    for u, js in cmp_map.items():
        if len(js) > 1:
            fails.append("比較に使われる文字列 %r の訳が %d 通りあります（分岐が壊れます）: %s"
                         % (u, len(js),
                            " / ".join("%r(%d 行目)" % (j, ln) for j, ln in js.items())))
    for j, us in cmp_rev.items():
        if len(us) > 1:
            warns.append("比較に使われる訳 %r に上流の複数文字列が集約されています: %s"
                         % (j, " / ".join("%r(%d 行目)" % (u, ln) for u, ln in us.items())))
    drift = [(u, js) for u, js in other_map.items() if len(js) > 1]
    for u, js in drift[:max_detail]:
        warns.append("訳ゆれ（比較文脈ではない）: %r -> %s"
                     % (u, " / ".join("%r(%d 行目)" % (j, ln) for j, ln in js.items())))
    if len(drift) > max_detail:
        warns.append("訳ゆれ 他 %d 件（--verbose で全件）" % (len(drift) - max_detail))

    summary = ("%d 対（同一必須 %d / イベント参照 %d / 比較 %d / 選択肢 %d / 書式 %d）"
               % (len(pairs), n_same_required, n_event, n_cmp, n_menu, n_fmt))
    if fails:
        body = [summary]
        body.extend(fails[:max_detail * 3])
        if len(fails) > max_detail * 3:
            body.append("他 %d 件" % (len(fails) - max_detail * 3))
        res.add(FAIL, "4.文字列", "\n".join(body))
    else:
        res.add(PASS, "4.文字列", summary)
    for w in warns:
        res.add(WARN, "4.文字列", w)
    return pairs


#: exname が識別子として書かれる形（コーパス全文からの素朴な検索）
def _exname_ref_hits(corpus, exname, skip_rel, limit=None):
    """コーパス中で exname を識別子として参照している箇所を返す。"""
    pats = ('"%s"' % exname, '"%s::' % exname, "duplicate(%s)" % exname)
    hits = []
    for path, text in corpus:
        if path == skip_rel:
            continue
        for pat in pats:
            if pat not in text:
                continue
            start = 0
            while True:
                idx = text.find(pat, start)
                if idx < 0:
                    break
                hits.append((path, text.count("\n", 0, idx) + 1, pat))
                start = idx + len(pat)
                if limit and len(hits) >= limit:
                    return hits
    return hits


def check_external_refs(res, renames, upstream, upstream_rel, strict, corpus,
                        u_heads=None, j_heads=None):
    """5.外部参照

    rAthena の NPC 解決はすべて exname（`表示名::ユニーク名` の後半）で行われる。
    表示名だけを変えるなら exname は不変なので、外部からの
    doevent / donpcevent / enablenpc / duplicate() / "名前::OnEvent" は壊れない。
    ここでは (a) 本当に exname が不変であること、(b) その exname が実際に
    何箇所から参照されているか、(c) 旧表示名が他ファイルの文面に出ていないか
    （こちらは参考の WARN）を見る。
    """
    # (a) exname の不変性（ヘッダ単位で厳密に確認する）
    exname_changed = []
    exname_excepted = []
    renamed_exnames = []
    if u_heads and j_heads and len(u_heads) == len(j_heads):
        for uh, jh in zip(u_heads, j_heads):
            if uh.name == jh.name:
                continue
            u_disp, u_ex = split_npc_name(uh.name)
            _j_disp, j_ex = split_npc_name(jh.name)
            if u_ex == j_ex:
                renamed_exnames.append((uh.line, u_ex, u_disp))
            elif any(ord(c) >= 0x80 for c in u_ex):
                # 上流 exname が非 ASCII バイト（韓国語 EUC-KR の残骸）で UTF-8 では
                # 同じバイト列を書けない。3.ヘッダ の例外と揃えて許容するが、
                # 旧 exname が他ファイルから参照されていたら本当に壊れるので FAIL。
                exname_excepted.append((uh.line, u_ex, j_ex))
            else:
                exname_changed.append("%d 行目: exname が変わっています（%r -> %r）"
                                      % (uh.line, u_ex, j_ex))
    for line, u_ex, j_ex in exname_excepted:
        hits = (_exname_ref_hits(corpus, u_ex, upstream_rel, limit=5)
                if corpus is not None else [])
        if hits:
            exname_changed.append(
                "%d 行目: exname %r は他ファイルから %d 件以上参照されているので改名できません: %s"
                % (line, u_ex, len(hits),
                   ", ".join("%s:%d" % (p, ln) for p, ln, _ in hits[:3])))
    if exname_changed:
        res.add(FAIL, "5.外部参照",
                "\n".join(exname_changed)
                + "\n  ※ exname は npcname_db のキー（src/map/npc.cpp npc_parsename）。"
                  "変えると doevent / enablenpc / duplicate() の解決が壊れます。")
        return
    if exname_excepted:
        res.add(WARN, "5.外部参照",
                "\n".join("%d 行目: 上流 exname %r は非 ASCII バイトで再現できないため %r に改名"
                          "（他ファイルからの参照 0 件を確認済み）" % (ln, u, j)
                          for ln, u, j in exname_excepted))

    if not renames:
        res.add(PASS, "5.外部参照", "表示名の変更なし")
        return
    if corpus is None:
        res.add(WARN, "5.外部参照",
                "外部参照未検証（上流 checkout が無いため npc/ 全体を検索できません）。"
                "--upstream-root を指定してください。対象: %s"
                % ", ".join(sorted(renames)))
        return

    # (b) exname 参照の件数（不変なので壊れないことの裏づけ）
    n_refs = 0
    ref_lines = []
    for line, exname, _u_disp in renamed_exnames:
        hits = _exname_ref_hits(corpus, exname, upstream_rel)
        n_refs += len(hits)
        if hits:
            shown = ", ".join("%s:%d" % (p, ln) for p, ln, _ in hits[:3])
            more = "" if len(hits) <= 3 else "（他 %d 件）" % (len(hits) - 3)
            ref_lines.append("  %d 行目 exname %r: %d 件 -> %s%s"
                             % (line, exname, len(hits), shown, more))

    # (c) 旧表示名が他ファイルの文字列に出ていないか（文面の食い違い。参考）
    hits_total = []
    for old in sorted(renames):
        pats = ['"%s"' % old, '"%s::' % old, '"%s#' % old]
        hits = []
        for path, text in corpus:
            if path == upstream_rel:
                continue
            for pat in pats:
                if pat in text:
                    line = text.count("\n", 0, text.index(pat)) + 1
                    hits.append((path, line, pat))
                    break
        if hits:
            hits_total.append((old, hits))

    summary = ("表示名を変更 %d 件。exname は全て不変で、他ファイルからの参照 %d 件は"
               "解決先が変わりません" % (len(renamed_exnames), n_refs))
    if ref_lines:
        summary += "\n" + "\n".join(ref_lines[:8])
        if len(ref_lines) > 8:
            summary += "\n  他 %d 件" % (len(ref_lines) - 8)
    res.add(PASS, "5.外部参照", summary)

    if not hits_total:
        return
    lines = []
    for old, hits in hits_total:
        shown = ", ".join("%s:%d %s" % (p, ln, pat) for p, ln, pat in hits[:3])
        more = "" if len(hits) <= 3 else "（他 %d 件）" % (len(hits) - 3)
        lines.append("旧表示名 %r を文字列に含む他ファイル: %s%s" % (old, shown, more))
    if strict:
        res.add(FAIL, "5.外部参照", "\n".join(lines))
    else:
        lines.append("※ NPC の解決は exname で行われる（src/map/npc.cpp npc_parsename / "
                     "npc_name2id）ので参照は壊れない。")
        lines.append("   文面（他 NPC のセリフが旧英語名を指している等）の食い違いだけ"
                     "確認すること（--strict-external-refs で FAIL にできる）。")
        res.add(WARN, "5.外部参照", "\n".join(lines))


def check_display_dependency(res, u_heads, j_heads, j_toks, j_text):
    """5b.表示名依存

    表示名を変えた NPC の本文が strnpcinfo(0)/(1)（＝可視名）を比較やキーに
    使っていると、表示名の変更で分岐が変わる。strnpcinfo(2)/(3)/(4) は
    `日本語#suffix::旧フル名` 形式なら値が変わらないので対象外。
    """
    if not u_heads or not j_heads or len(u_heads) != len(j_heads):
        return
    renamed = [i for i, (uh, jh) in enumerate(zip(u_heads, j_heads)) if uh.name != jh.name]
    if not renamed:
        return
    total_lines = j_text.count("\n") + 1

    def body_of(idx):
        start = j_heads[idx].line
        end = j_heads[idx + 1].line - 1 if idx + 1 < len(j_heads) else total_lines
        return [t for t in j_toks if start <= t.line <= end]

    # duplicate は参照元のスクリプトを実行するので、同じファイル内に元があれば
    # そちらの本文を見る（別ファイルの場合は tools/jp_npc_names.py の棚卸しで拾う）。
    index_by_exname = {}
    for idx, jh in enumerate(j_heads):
        _d, ex = split_npc_name(jh.name)
        if ex:
            index_by_exname.setdefault(ex, idx)

    warns = []
    for i in renamed:
        jh = j_heads[i]
        src_idx = i
        note = ""
        m = DUPLICATE_KIND_RE.match(jh.kind)
        if m:
            found = index_by_exname.get(m.group(1))
            if found is None:
                continue        # 参照元が別ファイル（棚卸しツール側で判定する）
            src_idx = found
            note = "（duplicate 元 %s の本文）" % m.group(1)
        for arg, use, line in strnpcinfo_usages(body_of(src_idx)):
            if arg in (0, 1) and use in STRNPCINFO_RISKY:
                warns.append("%d 行目: 表示名を変えた %r の本文%s が strnpcinfo(%d) を %s に"
                             "使っています" % (line, jh.name, note, arg, use))
    if warns:
        warns.append("※ 可視名を分岐やキーに使っている NPC は表示名を英語のまま残すか、"
                     "比較値も同時に直すこと（tools/jp_npc_names.py の分類 C）。")
        res.add(WARN, "5b.表示名依存", "\n".join(warns))


def check_counts(res, u_toks, j_toks):
    def counts(toks):
        mes = sum(1 for t in toks if t.kind == "word" and t.value == "mes")
        sel = sum(1 for t in toks
                  if t.kind == "word" and t.value in ("select", "prompt", "menu"))
        strs = sum(1 for t in toks if t.kind == "str")
        return mes, sel, strs

    um, us, ustr = counts(u_toks)
    jm, js, jstr = counts(j_toks)
    msg = ("mes %d / select 系 %d / 文字列 %d" % (jm, js, jstr))
    if (um, us, ustr) != (jm, js, jstr):
        res.add(FAIL, "6.件数",
                "件数が一致しません（上流 mes %d/select %d/文字列 %d、翻訳 %s）"
                % (um, us, ustr, msg))
    else:
        res.add(PASS, "6.件数", msg)


# ---------------------------------------------------------------- コーパス

def load_npc_corpus(upstream):
    """上流 npc/ 以下の全テキストを読み込む（外部参照チェック用）。"""
    if not upstream.has_full_tree:
        return None
    root = os.path.join(upstream.root, "npc")
    corpus = []
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            if not name.endswith(".txt"):
                continue
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, upstream.root)
            try:
                with open(full, "rb") as fh:
                    data = fh.read()
            except OSError:
                continue
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                text = data.decode("latin-1")
            corpus.append((rel, text))
    return corpus


# ---------------------------------------------------------------- 1 ファイル検証

def check_pair(jp_abspath, jp_label, upstream_rel, upstream, corpus, strict):
    title = jp_label if upstream_rel is None else "%s  ←  %s" % (jp_label, upstream_rel)
    res = Result(title)

    try:
        with open(jp_abspath, "rb") as fh:
            raw = fh.read()
    except OSError as exc:
        res.add(FAIL, "0.読み込み", "翻訳版を読めません: %s" % exc)
        return res

    j_text = check_encoding(res, raw, jp_label)
    if j_text is None:
        return res

    if upstream_rel is None:
        try:
            j_toks, _j_heads = tokenize(j_text)
        except Exception as exc:
            res.add(FAIL, "1b.エスケープ", "解析できません: %r" % (exc,))
            return res
        check_escapes(res, [], j_toks)
        check_index_brackets(res, None, j_text)
        res.add(PASS, "2.トークン構造", "追加のみのファイル（上流なし）のため構造比較は対象外")
        return res

    # 非 ASCII 直後の `\` があるとトークナイズ自体が信用できないので打ち切る
    if any(sev == FAIL and item == "1.エンコーディング" for sev, item, _ in res.items):
        res.add(FAIL, "2.トークン構造", "エンコーディング NG のため構造比較を中止しました")
        return res

    try:
        u_text = upstream.read_text(upstream_rel)
    except ToolError as exc:
        res.add(FAIL, "0.読み込み", "上流を読めません: %s" % exc)
        return res

    u_toks, u_heads = tokenize(u_text)
    j_toks, j_heads = tokenize(j_text)

    # トークン構造が一致しなくても実施できるので先に見る
    check_escapes(res, u_toks, j_toks)
    check_index_brackets(res, u_text, j_text)

    ok, renames, exname_renames = check_tokens(res, u_toks, j_toks, upstream_rel, jp_label)
    check_headers(res, u_heads, j_heads, renames)
    if ok:
        check_strings(res, u_toks, j_toks, exname_renames)
        check_external_refs(res, renames, upstream, upstream_rel, strict, corpus,
                            u_heads, j_heads)
        check_display_dependency(res, u_heads, j_heads, j_toks, j_text)
        check_counts(res, u_toks, j_toks)
    else:
        res.add(WARN, "4.文字列", "トークン構造が一致しないため未実施")
        res.add(WARN, "5.外部参照", "トークン構造が一致しないため未実施")
        res.add(WARN, "6.件数", "トークン構造が一致しないため未実施")
    return res


# ---------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(
        description="翻訳版 NPC スクリプトの構造検証（文字列リテラル以外は上流と同一か）")
    ap.add_argument("--manifest", default=MANIFEST_PATH, help="MANIFEST.tsv のパス")
    ap.add_argument("--file", default=None, help="単体検証: 翻訳版ファイル")
    ap.add_argument("--upstream", default=None, help="単体検証: 上流パス（npc/... 形式）")
    ap.add_argument("--upstream-root", default=None,
                    help="上流 rAthena の checkout（既定: scratchpad → ~/.cache/rathena-<commit>）")
    ap.add_argument("--commit", default=None, help="上流コミット（既定: app/config.env）")
    ap.add_argument("--report", default=None, help="結果を UTF-8 で保存するパス")
    ap.add_argument("--strict-external-refs", action="store_true",
                    help="改名した表示名が他ファイルから引用されていたら（::付きでも）FAIL にする")
    args = ap.parse_args(argv)

    if bool(args.file) != bool(args.upstream):
        if args.file and not args.upstream:
            pass  # 追加のみのファイルとして扱う
        else:
            die("jp_structure_check: --upstream は --file と一緒に指定してください")

    out = []

    def emit(line=""):
        out.append(line)
        print(line)

    try:
        upstream = Upstream(root=args.upstream_root, commit=args.commit)
    except ToolError as exc:
        die("jp_structure_check: %s" % exc)

    emit("上流: %s" % upstream.describe())
    corpus = load_npc_corpus(upstream)
    if corpus is None:
        emit("外部参照チェック: 上流 checkout が無いためスキップ（WARN 扱い）")
    else:
        emit("外部参照チェック用に上流 npc/ の %d ファイルを読み込みました" % len(corpus))
    emit()

    targets = []   # (jp_abspath, jp_label, upstream_rel)
    pre_problems = []

    if args.file:
        jp_abspath = os.path.abspath(args.file)
        label = jp_abspath
        for base in (OVERLAY_DIR, REPO_ROOT):
            try:
                rel = os.path.relpath(jp_abspath, base)
            except ValueError:
                continue
            if not rel.startswith(".."):
                label = rel
                break
        targets.append((jp_abspath, label, args.upstream))
    else:
        try:
            entries = parse_manifest(args.manifest)
        except ToolError as exc:
            die("jp_structure_check: %s" % exc)
        listed = set()
        for ent in entries:
            listed.add(ent.translated)
            targets.append((ent.translated_abspath, ent.translated, ent.upstream))
        for rel in iter_jp_files(JP_DIR):
            if rel not in listed:
                pre_problems.append((WARN, "MANIFEST に載っていないファイルがあります（孤児）: %s" % rel))

    n_pass = n_fail = n_warn = 0
    for jp_abspath, label, upstream_rel in targets:
        if not os.path.isfile(jp_abspath):
            res = Result("%s  ←  %s" % (label, upstream_rel or "(追加のみ)"))
            res.add(FAIL, "0.読み込み", "翻訳版ファイルがありません: %s" % jp_abspath)
        else:
            res = check_pair(jp_abspath, label, upstream_rel, upstream, corpus,
                             args.strict_external_refs)
        emit(res.render())
        emit()
        if res.status == FAIL:
            n_fail += 1
        else:
            n_pass += 1
        n_warn += res.warn_count

    for sev, msg in pre_problems:
        emit("%-4s %s" % (sev, msg))
        if sev == WARN:
            n_warn += 1
    if pre_problems:
        emit()

    emit("=================================================================")
    emit("総括: PASS %d / FAIL %d / WARN %d" % (n_pass, n_fail, n_warn))
    emit("=================================================================")

    if args.report:
        d = os.path.dirname(os.path.abspath(args.report))
        if d:
            os.makedirs(d, exist_ok=True)
        with open(args.report, "w", encoding="utf-8") as fh:
            fh.write("\n".join(out) + "\n")
        print("レポート: %s" % args.report)

    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())

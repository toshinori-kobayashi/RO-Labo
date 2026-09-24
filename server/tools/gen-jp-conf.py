#!/usr/bin/env python3
"""MANIFEST.tsv から scripts_custom.conf の JP ブロックを生成する。

  app/rathena/overlay-utf8/npc/custom/jp/MANIFEST.tsv   … Source of Truth
        ↓
  app/rathena/overlay-utf8/npc/scripts_custom.conf の
        // ---- BEGIN JP OVERLAY ... ----  〜  // ---- END JP OVERLAY ----

使い方:
    tools/gen-jp-conf.py                 # 生成して書き込む
    tools/gen-jp-conf.py --check         # 生成せず差分の有無だけ返す（差分あり = 終了コード 1）
    tools/gen-jp-conf.py --upstream-root /path/to/rathena

生成前に以下を検証し、1 つでも失敗したら生成せず非 0 で終了する:
    (a) 翻訳版ファイルが overlay-utf8 に存在する
    (b) 上流パスが上流 checkout に存在する
    (c) 上流パスが Pre-RE のロード対象（npc/pre-re/scripts_main.conf を再帰展開した
        npc: 集合）に文字列として完全一致で含まれる  ※delnpc は文字列一致で効くため
    (d) 上流パス・翻訳版パスに重複が無い
生成計画そのものも検証する（verify_plan）:
    (e) 同じ上流パスを 2 度登録していない（再登録候補が MANIFEST 入りしても二重にしない）
    (f) duplicate 元より後ろに並んでいる
"""

import argparse
import difflib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jp_common import (  # noqa: E402
    MANIFEST_PATH, OVERLAY_DIR, SCRIPTS_CUSTOM_CONF, REPO_ROOT,
    ToolError, Upstream, parse_manifest, die,
)
import jp_structure_check as jsc  # noqa: E402  （トークナイザ / ヘッダ検出を流用）

BEGIN_MARKER = ("// ---- BEGIN JP OVERLAY (generated from MANIFEST.tsv; "
                "do not edit by hand) ----")
END_MARKER = "// ---- END JP OVERLAY ----"
# 生成方式に移行する前の手書きブロックの目印（見つかったらそこ以降を置き換える）
LEGACY_MARKER = "// ---- Japanese overlay (built from app/rathena/overlay-utf8) ----"

HEADER_COMMENT = """\
// 生成元: npc/custom/jp/MANIFEST.tsv   生成コマンド: tools/gen-jp-conf.py
// このブロックは手で編集しないこと（次の生成で上書きされる）。
// 差し替えを増やすときは MANIFEST.tsv に 1 行足して gen-jp-conf.py を実行する。
//
// このファイルは npc/pre-re/scripts_main.conf の最後で import される
// （import: npc/scripts_custom.conf）。
// "delnpc" は上流エントリをソースファイル一覧から取り除く（src/map/map.cpp:4245-4250 ->
// src/map/npc.cpp:3632-3641）。上流ファイルはディスク上では無改変のまま、
// 下の日本語版だけがパースされる。
// delnpc に渡すパスは上流 conf に書かれている文字列と完全一致していること:
//   npc/scripts_athena.conf / npc/pre-re/scripts_athena.conf / npc/pre-re/scripts_jobs.conf
// 差し替え先ファイルが overlay-utf8 に無い場合、map-server は
// "npc_parsesrcfile: File not found"（src/map/npc.cpp:5656）を出して起動は続行する。
//
// "re-added after ..." の行は翻訳ではなく「ロード順の復元」。
// 差し替えでファイルが末尾へ移ると、その NPC を duplicate(<ユニーク名>) している
// 上流ファイルのほうが先にロードされ、
//   npc_parse_script: original npc not found for duplicate ...
// で NPC がまるごと欠ける。そこで duplicate 側も delnpc: -> npc: で末尾へ動かす
// （npc_addsrcfile は既にリストにあるファイルを追加しないので delnpc: が必須。
//  src/map/npc.cpp:3620-3626）。この並びは gen-jp-conf.py が自動計算する。"""


# ---------------------------------------------------------------- duplicate 依存
#
# delnpc: で上流ファイルをリストから外し、翻訳版を末尾（scripts_custom.conf）に足すと
# ロード順が変わる。上流で「翻訳対象ファイルが定義する NPC」を duplicate(<ユニーク名>) して
# いるファイルは、翻訳版より先にロードされてしまい
#   npc_parse_script: original npc not found for duplicate in file '...' : <名前>
# になって NPC が丸ごと欠ける（実害: NPC 総数が減る）。
# そこで、そのファイルも delnpc: -> npc: で末尾へ移して順序を復元する。

DUPLICATE_KIND_RE = re.compile(r"^duplicate\((.*)\)$")


class DuplicateGraph(object):
    """Pre-RE ロード対象から duplicate の依存関係を作る。"""

    def __init__(self, upstream):
        self.paths = upstream.prere_npc_paths()
        self.index = dict((p, i) for i, p in enumerate(self.paths))
        self.defines = {}      # path -> そのファイルが定義するユニーク名の集合
        self.dup_src = {}      # path -> そのファイルが duplicate 元として参照する名前
        self.owner = {}        # ユニーク名 -> 定義しているファイル（ロード順で最初）
        self.dependents = {}   # path -> そのファイルの NPC を duplicate しているファイル
        self.unresolved = []   # duplicate 元が見つからなかった (file, name)
        self._build(upstream)

    def _build(self, upstream):
        for path in self.paths:
            try:
                text = upstream.read_text(path)
            except ToolError:
                self.defines[path] = set()
                self.dup_src[path] = set()
                continue
            try:
                _tokens, headers = jsc.tokenize(text)
            except Exception:       # 解析できない上流ファイルは依存なしとして扱う
                self.defines[path] = set()
                self.dup_src[path] = set()
                continue
            defines, dups = set(), set()
            for h in headers:
                # ユニーク名 = `表示名::ユニーク名` の後半。`::` が無ければ名前全体。
                # `-\tscript\t::name\t-1,{`（表示名なし）も拾える。
                uniq = h.name.split("::", 1)[1] if "::" in h.name else h.name
                if uniq:
                    defines.add(uniq)
                m = DUPLICATE_KIND_RE.match(h.kind)
                if m:
                    dups.add(m.group(1))
            self.defines[path] = defines
            self.dup_src[path] = dups

        for path in self.paths:                 # ロード順で最初の定義を採用
            for name in self.defines[path]:
                self.owner.setdefault(name, path)

        for dep in self.paths:
            for name in self.dup_src[dep]:
                src = self.owner.get(name)
                if src is None:
                    self.unresolved.append((dep, name))
                    continue
                if src == dep:
                    continue
                if self.index[dep] <= self.index[src]:
                    continue                    # 上流時点で前方参照（本来ありえない）
                lst = self.dependents.setdefault(src, [])
                if dep not in lst:
                    lst.append(dep)

    def closure(self, roots):
        """roots（差し替える上流ファイル）から再登録が必要なファイルまで広げる。"""
        seen = set(roots)
        queue = list(roots)
        while queue:
            f = queue.pop()
            for dep in self.dependents.get(f, []):
                if dep not in seen:
                    seen.add(dep)
                    queue.append(dep)
        return seen

    def causes(self, path, within):
        """path を末尾へ動かす原因になったファイル（= duplicate 元）。"""
        return [f for f in within if path in self.dependents.get(f, [])]


ADD_PREFIX = "\0add:"


def plan_order(entries, graph):
    """JP ブロックに出す順序を決める。

    戻り値: [("entry", ManifestEntry) | ("readd", 上流パス, [原因パス])]
    """
    by_upstream = {}
    nodes = []          # MANIFEST 記載順のノードキー
    for ent in entries:
        key = ent.upstream if ent.upstream else (ADD_PREFIX + ent.translated)
        if ent.upstream:
            by_upstream[ent.upstream] = ent
        nodes.append(key)
    entry_by_key = {}
    for ent in entries:
        entry_by_key[ent.upstream if ent.upstream else (ADD_PREFIX + ent.translated)] = ent

    replaced = [e.upstream for e in entries if e.upstream]
    moved = graph.closure(replaced)              # 末尾へ動かすファイル全部

    # 先に来てほしい順（MANIFEST 順 → その依存を直後に差し込む）
    preferred = []
    seen = set()

    def push(key):
        if key in seen:
            return
        seen.add(key)
        preferred.append(key)
        if key.startswith(ADD_PREFIX):
            return
        for dep in graph.dependents.get(key, []):
            if dep in moved:
                push(dep)

    for key in nodes:
        push(key)
    for path in graph.paths:                     # 取りこぼし（念のため）
        if path in moved:
            push(path)

    rank = dict((k, i) for i, k in enumerate(preferred))

    # 先行条件（p が先、n が後）
    prereq = {}
    for key in preferred:
        prereq[key] = set()
    for src in moved:
        for dep in graph.dependents.get(src, []):
            if dep in moved and dep in prereq:
                prereq[dep].add(src)

    state = {}
    order = []

    def visit(key, stack):
        st = state.get(key, 0)
        if st == 2:
            return
        if st == 1:
            cycle = stack[stack.index(key):] + [key]
            raise ToolError("duplicate 依存が循環しています: %s" % " -> ".join(cycle))
        state[key] = 1
        for p in sorted(prereq.get(key, ()), key=lambda x: rank.get(x, 1 << 30)):
            visit(p, stack + [key])
        state[key] = 2
        order.append(key)

    for key in preferred:
        visit(key, [])

    plan = []
    for key in order:
        ent = entry_by_key.get(key)
        if ent is not None:
            plan.append(("entry", ent, None))
        else:
            plan.append(("readd", key, graph.causes(key, moved)))
    return plan


def verify_plan(entries, plan, graph):
    """生成計画そのものを検証する。問題のメッセージ一覧を返す（空なら OK）。

    (1) 同じ上流パスを 2 度登録していない
        （再登録候補が将来 MANIFEST のエントリになったとき、
         `delnpc:`/`npc:` が二重に出ると npc_addsrcfile が 2 回走って NPC が重複する）
    (2) 翻訳版パスの重複が無い
    (3) duplicate 元より後ろに並んでいる
        （前に来ると npc_parse_script: original npc not found で NPC が丸ごと欠ける）
    """
    problems = []

    manifest_upstream = set(e.upstream for e in entries if e.upstream)

    pos = {}          # 上流パス -> 生成ブロック内の位置
    seen_del = {}
    seen_npc = {}
    for i, item in enumerate(plan):
        if item[0] == "entry":
            ent = item[1]
            if ent.upstream:
                if ent.upstream in seen_del:
                    problems.append("上流パスを 2 度 delnpc しています: %s" % ent.upstream)
                seen_del[ent.upstream] = i
                pos[ent.upstream] = i
            key = ent.translated
        else:
            path = item[1]
            if path in manifest_upstream:
                problems.append(
                    "再登録候補 %s は MANIFEST のエントリでもあります（二重登録）。"
                    "plan_order が entry として扱うはずなので、計画の作り方がおかしいです" % path)
            if path in seen_del:
                problems.append("上流パスを 2 度 delnpc しています: %s" % path)
            seen_del[path] = i
            pos[path] = i
            key = path
        if key in seen_npc:
            problems.append("同じパスを 2 度 npc: 登録しています: %s" % key)
        seen_npc[key] = i

    # (3) duplicate 元より後ろか
    for src, deps in graph.dependents.items():
        if src not in pos:
            continue
        for dep in deps:
            if dep not in pos:
                problems.append(
                    "%s は %s の NPC を duplicate していますが、再登録されていません"
                    "（上流の元の位置に残るとロード順が逆転します）" % (dep, src))
                continue
            if pos[dep] <= pos[src]:
                problems.append(
                    "ロード順が逆転しています: %s（%d 番目）は duplicate 元 %s（%d 番目）より"
                    "後ろに置く必要があります" % (dep, pos[dep], src, pos[src]))
    return problems


def build_block(entries, plan):
    """JP ブロックの文字列を作る。"""
    lines = [BEGIN_MARKER]
    lines.extend(HEADER_COMMENT.splitlines())
    for item in plan:
        if item[0] == "entry":
            ent = item[1]
            if ent.upstream:
                lines.append("delnpc: %s" % ent.upstream)
            lines.append("npc: %s" % ent.translated)
        else:
            path, causes = item[1], item[2]
            who = ", ".join(sorted(causes)) if causes else "(不明)"
            lines.append("// re-added after %s (duplicate dependency)" % who)
            lines.append("delnpc: %s" % path)
            lines.append("npc: %s" % path)
    lines.append(END_MARKER)
    return "\n".join(lines) + "\n"


def validate(entries, upstream):
    """生成前の検証。問題のメッセージ一覧を返す（空なら OK）。"""
    problems = []

    # (d) 重複
    seen_up, seen_tr = {}, {}
    for ent in entries:
        if ent.upstream:
            if ent.upstream in seen_up:
                problems.append(
                    "MANIFEST %d 行目: 上流パスが重複しています（%d 行目と同じ）: %s"
                    % (ent.lineno, seen_up[ent.upstream], ent.upstream))
            else:
                seen_up[ent.upstream] = ent.lineno
        if ent.translated in seen_tr:
            problems.append(
                "MANIFEST %d 行目: 翻訳版パスが重複しています（%d 行目と同じ）: %s"
                % (ent.lineno, seen_tr[ent.translated], ent.translated))
        else:
            seen_tr[ent.translated] = ent.lineno

    # (a) 翻訳版の存在
    for ent in entries:
        if not os.path.isfile(ent.translated_abspath):
            problems.append(
                "MANIFEST %d 行目: 翻訳版ファイルがありません: %s"
                % (ent.lineno, os.path.relpath(ent.translated_abspath, REPO_ROOT)))

    # (b)(c) 上流の存在とロード対象かどうか
    upstream_entries = [e for e in entries if e.upstream]
    if upstream_entries:
        try:
            loaded = set(upstream.prere_npc_paths())
        except ToolError as exc:
            problems.append("Pre-RE のロード対象を取得できません: %s" % exc)
            loaded = None
        for ent in upstream_entries:
            try:
                exists = upstream.exists(ent.upstream)
            except ToolError as exc:
                problems.append("MANIFEST %d 行目: %s" % (ent.lineno, exc))
                continue
            if not exists:
                problems.append(
                    "MANIFEST %d 行目: 上流にファイルがありません: %s"
                    % (ent.lineno, ent.upstream))
                continue
            if loaded is not None and ent.upstream not in loaded:
                problems.append(
                    "MANIFEST %d 行目: Pre-RE のロード対象ではありません（delnpc が効きません）: %s\n"
                    "    npc/pre-re/scripts_main.conf から辿れる npc: 行と文字列が完全一致している"
                    "必要があります（re/ 専用ファイルや表記ゆれに注意）"
                    % (ent.lineno, ent.upstream))
    return problems


def splice(conf_text, block):
    """conf の JP ブロックを差し替えた全文を返す。"""
    lines = conf_text.split("\n")
    begin = end = None
    legacy = None
    for i, line in enumerate(lines):
        if line.rstrip() == BEGIN_MARKER and begin is None:
            begin = i
        elif line.rstrip() == END_MARKER:
            end = i
        elif line.rstrip() == LEGACY_MARKER and legacy is None:
            legacy = i

    if begin is not None and end is not None and end > begin:
        head = lines[:begin]
        tail = lines[end + 1:]
    elif begin is not None:
        raise ToolError("BEGIN マーカーはあるのに END マーカーがありません: %s" % END_MARKER)
    elif legacy is not None:
        # 旧・手書きブロック。そこから末尾までを生成結果で置き換える。
        head = lines[:legacy]
        tail = []
    else:
        head = lines
        tail = []

    while head and head[-1].strip() == "":
        head.pop()
    while tail and tail[0].strip() == "":
        tail.pop(0)
    while tail and tail[-1].strip() == "":
        tail.pop()

    out = []
    if head:
        out.extend(head)
        out.append("")
    out.extend(block.rstrip("\n").split("\n"))
    if tail:
        out.append("")
        out.extend(tail)
    return "\n".join(out) + "\n"


def stray_directives(conf_text):
    """生成ブロックの外に手書きの delnpc:/npc: が残っていないか調べる。

    MANIFEST を通さずに conf を直接編集すると、次の生成で消えるか二重定義になる。
    """
    lines = conf_text.split("\n")
    inside = False
    stray = []
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if s == BEGIN_MARKER:
            inside = True
            continue
        if s == END_MARKER:
            inside = False
            continue
        if inside or s.startswith("//"):
            continue
        if s.startswith("npc:") or s.startswith("delnpc:"):
            stray.append((i, s))
    return stray


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="MANIFEST.tsv から scripts_custom.conf の JP ブロックを生成する")
    ap.add_argument("--manifest", default=MANIFEST_PATH, help="MANIFEST.tsv のパス")
    ap.add_argument("--conf", default=SCRIPTS_CUSTOM_CONF, help="scripts_custom.conf のパス")
    ap.add_argument("--upstream-root", default=None,
                    help="上流 rAthena の checkout（既定: scratchpad → ~/.cache/rathena-<commit>）")
    ap.add_argument("--commit", default=None, help="上流コミット（既定: app/config.env）")
    ap.add_argument("--check", action="store_true",
                    help="生成せず差分の有無だけ返す（差分あり = 終了コード 1）")
    args = ap.parse_args(argv)

    try:
        entries = parse_manifest(args.manifest)
        upstream = Upstream(root=args.upstream_root, commit=args.commit)
    except ToolError as exc:
        die("gen-jp-conf: %s" % exc)

    print("MANIFEST : %s（%d エントリ）" % (
        os.path.relpath(args.manifest, REPO_ROOT), len(entries)))
    print("上流     : %s" % upstream.describe())
    print("conf     : %s" % os.path.relpath(args.conf, REPO_ROOT))
    print("overlay  : %s" % os.path.relpath(OVERLAY_DIR, REPO_ROOT))
    print()

    problems = validate(entries, upstream)
    if problems:
        print("検証 NG: %d 件" % len(problems))
        for p in problems:
            print("  - %s" % p)
        return 1
    print("検証 OK: 翻訳版の存在 / 上流の存在 / Pre-RE ロード対象 / 重複なし")

    # ---- duplicate 依存の解決 -------------------------------------------
    try:
        graph = DuplicateGraph(upstream)
        plan = plan_order(entries, graph)
    except ToolError as exc:
        die("gen-jp-conf: %s" % exc)
    plan_problems = verify_plan(entries, plan, graph)
    if plan_problems:
        print("生成計画 NG: %d 件" % len(plan_problems))
        for p in plan_problems:
            print("  - %s" % p)
        return 1

    readds = [item for item in plan if item[0] == "readd"]
    print("duplicate 依存: 上流 %d ファイルを走査 / 再登録 %d 件"
          % (len(graph.paths), len(readds)))
    for _kind, path, causes in readds:
        print("    + %s  （%s の NPC を duplicate しているため末尾へ）"
              % (path, ", ".join(sorted(causes))))
    if graph.unresolved:
        print("  注意: duplicate 元が見つからない参照が %d 件あります（上流由来）"
              % len(graph.unresolved))
        for dep, name in graph.unresolved[:5]:
            print("    ? %s : %s" % (dep, name))

    try:
        with open(args.conf, encoding="utf-8") as fh:
            current = fh.read()
    except OSError as exc:
        die("gen-jp-conf: conf を読めません: %s (%s)" % (args.conf, exc))

    block = build_block(entries, plan)
    try:
        new_text = splice(current, block)
    except ToolError as exc:
        die("gen-jp-conf: %s" % exc)

    stray = stray_directives(new_text)
    if stray:
        print("警告: 生成ブロックの外に手書きの delnpc:/npc: が %d 行あります。" % len(stray))
        print("      MANIFEST.tsv に移してください（このままだと管理外になります）:")
        for lineno, s in stray[:20]:
            print("        %s:%d  %s" % (os.path.relpath(args.conf, REPO_ROOT), lineno, s))
        print()

    if args.check:
        if new_text == current:
            print("--check: 差分なし（conf は MANIFEST と一致しています）")
            return 0
        print("--check: 差分あり（tools/gen-jp-conf.py を実行してください）")
        diff = difflib.unified_diff(
            current.splitlines(True), new_text.splitlines(True),
            fromfile="current", tofile="generated")
        sys.stdout.writelines(diff)
        return 1

    if new_text == current:
        print("変更なし（conf は既に MANIFEST と一致しています）")
        return 0

    with open(args.conf, "w", encoding="utf-8") as fh:
        fh.write(new_text)
    n_del = sum(1 for e in entries if e.upstream) + len(readds)
    n_npc = len(entries) + len(readds)
    print("生成しました: delnpc %d 行 / npc %d 行（うち再登録 %d ファイル）"
          % (n_del, n_npc, len(readds)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

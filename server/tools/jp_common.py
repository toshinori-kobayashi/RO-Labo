#!/usr/bin/env python3
"""NPC 日本語オーバーレイ用ツールの共通部品（標準ライブラリのみ）。

gen-jp-conf.py と jp_structure_check.py の両方から import する。

提供するもの:
  - リポジトリ内の固定パス（overlay / MANIFEST / scripts_custom.conf）
  - app/config.env からの RATHENA_COMMIT 取得
  - MANIFEST.tsv のパース
  - 上流 rAthena（固定コミット）のファイル取得（ローカル checkout もしくは
    GitHub raw を ~/.cache/rathena-<commit>/ にキャッシュ）
  - Pre-RE でロードされる npc: パス集合の算出
"""

import os
import re
import sys

# ---------------------------------------------------------------- パス
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(TOOLS_DIR)
OVERLAY_DIR = os.path.join(REPO_ROOT, "app", "rathena", "overlay-utf8")
JP_DIR = os.path.join(OVERLAY_DIR, "npc", "custom", "jp")
MANIFEST_PATH = os.path.join(JP_DIR, "MANIFEST.tsv")
SCRIPTS_CUSTOM_CONF = os.path.join(OVERLAY_DIR, "npc", "scripts_custom.conf")
CONFIG_ENV = os.path.join(REPO_ROOT, "app", "config.env")

# 既定の上流 checkout 候補（先に見つかったものを使う）。
# 環境変数 RATHENA_UPSTREAM_ROOT でも上書きできる。
DEFAULT_UPSTREAM_CANDIDATES = [
    "/private/tmp/claude-502/-Users-toshinori-kobayashi-Documents-m3dc-work/"
    "6af29f81-7b6f-4726-9bec-f12d4c83ed82/scratchpad/rathena",
]

RAW_BASE = "https://raw.githubusercontent.com/rathena/rathena"

# 上流 checkout だと判定するための目印
UPSTREAM_MARKER = os.path.join("npc", "pre-re", "scripts_main.conf")


class ToolError(Exception):
    """利用者に見せるエラー（トレースバックなしで表示する）。"""


# ---------------------------------------------------------------- config.env
def read_rathena_commit(path=CONFIG_ENV):
    """app/config.env の RATHENA_COMMIT を返す。"""
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line.startswith("RATHENA_COMMIT="):
                    return line.split("=", 1)[1].strip()
    except OSError as exc:
        raise ToolError("config.env を読めません: %s (%s)" % (path, exc))
    raise ToolError("config.env に RATHENA_COMMIT がありません: %s" % path)


# ---------------------------------------------------------------- MANIFEST
class ManifestEntry(object):
    __slots__ = ("lineno", "upstream", "translated")

    def __init__(self, lineno, upstream, translated):
        self.lineno = lineno
        self.upstream = upstream          # 上流パス、または None（追加のみ）
        self.translated = translated      # overlay-utf8 からの相対パス

    @property
    def is_addition(self):
        return self.upstream is None

    @property
    def translated_abspath(self):
        return os.path.join(OVERLAY_DIR, self.translated)


def parse_manifest(path=MANIFEST_PATH):
    """MANIFEST.tsv を読み ManifestEntry のリストを返す。"""
    if not os.path.isfile(path):
        raise ToolError("MANIFEST がありません: %s" % path)
    entries = []
    with open(path, encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, 1):
            line = raw.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            fields = line.split("\t")
            fields = [f for f in fields if f != ""]
            if len(fields) != 2:
                raise ToolError(
                    "MANIFEST %s:%d: TAB 区切り 2 列である必要があります: %r"
                    % (path, lineno, line))
            upstream, translated = fields[0].strip(), fields[1].strip()
            entries.append(ManifestEntry(
                lineno,
                None if upstream == "-" else upstream,
                translated))
    if not entries:
        raise ToolError("MANIFEST にエントリがありません: %s" % path)
    return entries


# ---------------------------------------------------------------- 上流の取得
class Upstream(object):
    """上流 rAthena（固定コミット）のファイルを読むためのアクセサ。

    root が与えられて（もしくは既定候補が見つかって）いればそこから読む。
    無ければ ~/.cache/rathena-<commit>/ にキャッシュしつつ GitHub raw から取得する。
    """

    def __init__(self, root=None, commit=None, allow_download=True):
        self.commit = commit or read_rathena_commit()
        self.allow_download = allow_download
        self.cache_dir = os.path.expanduser("~/.cache/rathena-%s" % self.commit)
        self.root = self._resolve_root(root)
        self._text_cache = {}

    def _resolve_root(self, root):
        cands = []
        if root:
            cands.append(root)
        else:
            env = os.environ.get("RATHENA_UPSTREAM_ROOT")
            if env:
                cands.append(env)
            cands.extend(DEFAULT_UPSTREAM_CANDIDATES)
            cands.append(self.cache_dir)
        for cand in cands:
            cand = os.path.expanduser(cand)
            if os.path.isfile(os.path.join(cand, UPSTREAM_MARKER)):
                return cand
        if root:
            # 明示指定が外れているのは利用者のミスなので黙らない
            raise ToolError(
                "--upstream-root に rAthena の checkout がありません: %s "
                "(%s が見つからない)" % (root, UPSTREAM_MARKER))
        return None

    @property
    def has_full_tree(self):
        """npc/ 全体を走査できる（= ローカル checkout がある）か。"""
        return self.root is not None and os.path.isdir(os.path.join(self.root, "npc"))

    def describe(self):
        if self.root:
            return "%s (commit %s)" % (self.root, self.commit[:12])
        return "GitHub raw キャッシュ %s (commit %s)" % (self.cache_dir, self.commit[:12])

    # -- 低レベル ------------------------------------------------------
    def local_path(self, relpath):
        """ローカルに実体があるならそのパス、無ければ None。"""
        if self.root:
            p = os.path.join(self.root, relpath)
            if os.path.isfile(p):
                return p
        cached = os.path.join(self.cache_dir, relpath)
        if os.path.isfile(cached):
            return cached
        return None

    def _download(self, relpath):
        import urllib.error
        import urllib.request

        url = "%s/%s/%s" % (RAW_BASE, self.commit, relpath)
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                data = resp.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return None
            raise ToolError("上流ファイルの取得に失敗: %s (%s)" % (url, exc))
        except Exception as exc:  # URLError / socket.timeout など
            raise ToolError(
                "上流ファイルの取得に失敗（ネットワーク不通？）: %s (%s)\n"
                "  --upstream-root で rAthena の checkout を指定してください。"
                % (url, exc))
        dest = os.path.join(self.cache_dir, relpath)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as fh:
            fh.write(data)
        return data

    def exists(self, relpath):
        if self.local_path(relpath):
            return True
        if not self.allow_download:
            return False
        return self._download(relpath) is not None

    def read_bytes(self, relpath):
        p = self.local_path(relpath)
        if p:
            with open(p, "rb") as fh:
                return fh.read()
        if not self.allow_download:
            raise ToolError("上流ファイルがありません: %s" % relpath)
        data = self._download(relpath)
        if data is None:
            raise ToolError("上流ファイルがありません: %s" % relpath)
        return data

    def read_text(self, relpath):
        """上流スクリプトを読む。上流は ASCII / Latin-1 混在なので置換なしで読む。"""
        if relpath in self._text_cache:
            return self._text_cache[relpath]
        data = self.read_bytes(relpath)
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            # 上流には稀に Latin-1 の文字が混ざる（コメント中のアクセント記号など）
            text = data.decode("latin-1")
        self._text_cache[relpath] = text
        return text

    # -- Pre-RE のロード対象 -------------------------------------------
    def prere_npc_paths(self, main_conf="npc/pre-re/scripts_main.conf"):
        """npc/pre-re/scripts_main.conf を再帰展開して npc: のパス集合を返す。

        delnpc: は「conf に書かれた文字列」との一致で効くので、
        ここで集めるのも文字列のまま（正規化しない）。
        """
        seen_conf = set()
        npc_paths = []

        def walk(conf_rel):
            if conf_rel in seen_conf:
                return
            seen_conf.add(conf_rel)
            try:
                text = self.read_text(conf_rel)
            except ToolError:
                return
            for line in text.splitlines():
                line = line.strip()
                if not line or line.startswith("//"):
                    continue
                if line.startswith("npc:"):
                    npc_paths.append(line[4:].strip())
                elif line.startswith("import:"):
                    walk(line[7:].strip())

        walk(main_conf)
        return npc_paths


def iter_jp_files(jp_dir=JP_DIR):
    """npc/custom/jp/ 以下の翻訳ファイル（*.txt）を overlay 相対パスで列挙する。"""
    out = []
    for dirpath, _dirnames, filenames in os.walk(jp_dir):
        for name in sorted(filenames):
            if not name.endswith(".txt"):
                continue
            full = os.path.join(dirpath, name)
            out.append(os.path.relpath(full, OVERLAY_DIR))
    return sorted(out)


def die(msg):
    sys.stderr.write("%s\n" % msg)
    sys.exit(2)

# rAthena Pre-Renewal 用イメージ（multi-stage）
# build args は docker-compose.yml が .env から補間する。
#   RATHENA_COMMIT : 固定する rAthena のコミット SHA
#   PACKETVER      : 対応クライアントのパケットバージョン

# ---------------------------------------------------------------- builder
FROM ubuntu:24.04 AS builder

ARG DEBIAN_FRONTEND=noninteractive
# libmariadb-dev-compat が mysql_config を提供する（configure.ac:1237 AC_PATH_PROG mysql_config）
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      git \
      ca-certificates \
      zlib1g-dev \
      libpcre3-dev \
      libmariadb-dev \
      libmariadb-dev-compat \
 && rm -rf /var/lib/apt/lists/*

ARG RATHENA_COMMIT
ARG PACKETVER

WORKDIR /src
# コミットを直接 fetch する shallow clone（タグ/ブランチに依存しない）
RUN test -n "${RATHENA_COMMIT}" \
 && git init -q . \
 && git remote add origin https://github.com/rathena/rathena.git \
 && git fetch --depth 1 origin "${RATHENA_COMMIT}" \
 && git checkout -q FETCH_HEAD \
 && git --no-pager log -1 --format='rAthena commit: %H %s'

# 公式 CI (.github/workflows/build_servers_modes.yml) と同じ手順
RUN test -n "${PACKETVER}" \
 && ./configure --enable-prere=yes --enable-packetver=${PACKETVER}
RUN make -j"$(nproc)" server

# ビルド成果物の存在確認（ここで落ちればイメージは作られない）
RUN test -x login-server && test -x char-server && test -x map-server

# ---------------------------------------------------------------- runtime
FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive
# envsubst は gettext-base、healthcheck の </dev/tcp に bash が必要
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      libmariadb3 \
      zlib1g \
      libpcre3 \
      gettext-base \
      ca-certificates \
      tzdata \
      bash \
 && rm -rf /var/lib/apt/lists/*

# ubuntu:24.04 には既定で uid/gid 1000 の ubuntu ユーザーがいるので削除してから作る
RUN userdel -r ubuntu 2>/dev/null || true \
 && groupdel ubuntu 2>/dev/null || true \
 && groupadd -g 1000 rathena \
 && useradd -u 1000 -g 1000 -M -d /opt/rathena -s /usr/sbin/nologin rathena

WORKDIR /opt/rathena

COPY --from=builder /src/login-server /src/char-server /src/map-server ./
COPY --from=builder /src/conf ./conf
COPY --from=builder /src/db   ./db
COPY --from=builder /src/npc  ./npc

# conf/import は make server の import ターゲットで import-tmpl から作られるが、
# yml 系の空テンプレートを確実に揃えるため明示的に上書きコピーしておく。
RUN mkdir -p conf/import log \
 && cp -a conf/import-tmpl/. conf/import/

# ------------------------------- 日本語オーバーレイ（UTF-8 -> CP932）
# overlay-utf8/ は rAthena のディレクトリツリーを UTF-8 で持つオーバーレイ。
# Git 上は UTF-8 が正とし、ここで CP932（Shift_JIS 系）へ変換して同じ相対パスに配置する。
# クライアント（kRO 2021-11-03 RagexeRE / 日本語 Windows）は文字列を CP932 として解釈し、
# rAthena は文字列をバイト列として素通しするため、サーバ上のファイルは CP932 である必要がある。
#
# iconv は glibc 同梱（libc-bin）。追加パッケージは不要だが存在と CP932 対応を先に確認する。
# 変換できない文字（絵文字・ラテン文字のアクセント付きなど）があればここでビルドを落とす。
# UTF-8 BOM も拒否する（rAthena は npc.cpp:5673-5679 で BOM 付きスクリプトを明示的に弾く）。
# U+301C（波ダッシュ）は glibc の iconv が 0x8160 へ通してしまうが、
# macOS の iconv は弾くためソースの表記を揃える目的で明示的に拒否する。全角チルダ U+FF5E を使うこと。
COPY overlay-utf8/ /tmp/overlay-utf8/
RUN set -eu; \
    command -v iconv >/dev/null || { echo "overlay: iconv が見つかりません" >&2; exit 1; }; \
    iconv -l | grep -qi '^CP932' || { echo "overlay: iconv が CP932 に対応していません" >&2; exit 1; }; \
    wavedash="$(printf '\343\200\234')"; \
    : > /tmp/overlay-errors; \
    cd /tmp/overlay-utf8; \
    find . -type f | LC_ALL=C sort > /tmp/overlay-files; \
    while IFS= read -r src; do \
      rel="${src#./}"; \
      if [ "$(od -An -N3 -tx1 "$src" | tr -d ' \n')" = "efbbbf" ]; then \
        echo "  UTF-8 BOM があります: overlay-utf8/${rel}" >> /tmp/overlay-errors; \
        continue; \
      fi; \
      if LC_ALL=C grep -q "$wavedash" "$src"; then \
        echo "  U+301C 波ダッシュが含まれます（U+FF5E 全角チルダを使ってください）: overlay-utf8/${rel}" >> /tmp/overlay-errors; \
        continue; \
      fi; \
      dst="/opt/rathena/${rel}"; \
      mkdir -p "$(dirname "$dst")"; \
      if iconv -f UTF-8 -t CP932 "$src" > "${dst}.cp932.tmp" 2>/tmp/overlay-iconv-err; then \
        mv "${dst}.cp932.tmp" "$dst"; \
        chmod 0644 "$dst"; \
        echo "overlay: ${rel} -> /opt/rathena/${rel}"; \
      else \
        rm -f "${dst}.cp932.tmp"; \
        { echo "  CP932 に変換できない文字があります: overlay-utf8/${rel}"; \
          sed 's/^/    /' /tmp/overlay-iconv-err; } >> /tmp/overlay-errors; \
      fi; \
    done < /tmp/overlay-files; \
    if [ -s /tmp/overlay-errors ]; then \
      echo "overlay: 変換に失敗したファイルがあります" >&2; \
      cat /tmp/overlay-errors >&2; \
      exit 1; \
    fi; \
    rm -rf /tmp/overlay-utf8 /tmp/overlay-files /tmp/overlay-errors /tmp/overlay-iconv-err

# 本リポジトリの設定で上書き（*.tmpl は entrypoint が描画する）
COPY conf/import/ ./conf/import/
COPY entrypoint.sh ./entrypoint.sh

RUN chmod +x ./entrypoint.sh \
 && chown -R rathena:rathena conf/import log

USER rathena
ENTRYPOINT ["/opt/rathena/entrypoint.sh"]

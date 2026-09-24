# tests/cp932_roundtrip.c

rAthena と同じ経路で **CP932 接続 → MariaDB（utf8mb4 テーブル）→ utf8mb4 接続で読み戻し**
の往復が壊れないことを確認する小さな C プログラム。

確認しているのは次の 2 点。

1. `mysql_real_escape_string()` が CP932 の 2 バイト目 `0x5C`（ソ / 表 / 能）を
   `\` と誤認して二重化しないこと。
2. cp932 で書いたものを utf8mb4 接続で読むと正しい UTF-8 になること
   （= MariaDB 側が変換していること）。

rAthena 本体は `SET NAMES <codepage>` を SQL で送るだけ（`src/common/sql.cpp` `Sql_SetEncoding`）で、
`mysql_set_character_set()` は呼ばない。`--no-set-charset` を付けるとその rAthena と同じ経路になる。

**実測結果（2026-09-23、MariaDB 11.4 + Ubuntu 24.04 libmariadb）: どちらのモードも PASS。**
MariaDB サーバはセッション変数の変更（`character_set_client` 等）をクライアントへ通知し、
MariaDB Connector/C はそれを受けて `mysql->charset` を更新するため、`SET NAMES` だけでも
`mysql_real_escape_string()` は cp932 として動く。したがって rAthena へのパッチは不要と判断し、
ソースは無改変で運用している。MariaDB のバージョンやクライアントライブラリを変えたときは
このテストを再実行して確認すること。

## 前提

- ローカル compose が起動していること。

  ```sh
  cd app
  cp .env.local.example .env      # 初回のみ
  docker compose -f docker-compose.yml -f docker-compose.local.yml up -d --build
  ```

- compose の `mariadb` はホストにポートを公開していないので、
  **同じ compose ネットワークに参加したコンテナから**実行する。

## 手順

すべて `app/` ディレクトリで実行する。

### 1. builder イメージを用意する（`libmariadb-dev` と gcc 入り）

```sh
docker build --target builder \
  --build-arg RATHENA_COMMIT="$(sed -n 's/^RATHENA_COMMIT=//p' config.env)" \
  --build-arg PACKETVER="$(sed -n 's/^PACKETVER=//p' config.env)" \
  -t rathena-builder:local rathena
```

（`up -d --build` 済みならビルドキャッシュが効くので数秒で終わる）

### 2. compose ネットワーク名を確認する

```sh
docker network ls --format '{{.Name}}' | grep _default
# 例: ro-server-local_default
```

### 3. コンパイルして実行する

```sh
NET="$(docker network ls --format '{{.Name}}' | grep -m1 '_default$')"
DB_PASS="$(sed -n 's/^MARIADB_PASSWORD=//p' .env)"

docker run --rm --network "$NET" \
  -v "$PWD/rathena/tests:/tests:ro" \
  -e DB_HOST=mariadb \
  -e DB_USER="$(sed -n 's/^MARIADB_USER=//p' .env)" \
  -e DB_NAME="$(sed -n 's/^MARIADB_DATABASE=//p' .env)" \
  -e DB_PASS="$DB_PASS" \
  rathena-builder:local \
  sh -c 'gcc -O2 -Wall -o /tmp/cp932_roundtrip /tests/cp932_roundtrip.c $(mysql_config --cflags --libs) && /tmp/cp932_roundtrip'
```

終了コード 0 / 出力末尾が `結果: PASS` なら成功。

### 4. rAthena と同じ経路（SET NAMES のみ）で実行する

同じコマンドの末尾を `&& /tmp/cp932_roundtrip --no-set-charset` に変えて実行する。
これが rAthena 本体と同じ経路。`writer character set: cp932` と表示され PASS になれば、
セッショントラッキングによりクライアント側 charset が追随している。

## 後片付け

テーブル `cp932_roundtrip` はプログラムの最後に `DROP TABLE` している。
異常終了して残った場合は手動で消す。

```sh
docker compose -f docker-compose.yml -f docker-compose.local.yml exec -T mariadb \
  sh -c 'MYSQL_PWD="$MARIADB_ROOT_PASSWORD" mariadb --default-character-set=utf8mb4 -u root "$MARIADB_DATABASE" -e "DROP TABLE IF EXISTS cp932_roundtrip"'
```

## 注意

- 環境変数 `DB_HOST` / `DB_PORT` / `DB_USER` / `DB_PASS` / `DB_NAME` で接続先を変えられる
  （既定は `mariadb:3306` / `ragnarok`）。
- テーブルは `CREATE TABLE ... ENGINE=InnoDB` で作るだけで `CHARSET` を指定していない。
  rAthena の `sql-files/main.sql` と同じく DB 既定（= `docker-compose.yml` の
  `--character-set-server=utf8mb4`）に従わせるため。

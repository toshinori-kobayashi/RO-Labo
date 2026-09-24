# sql-init/ のコピー元

`sql-init/01-main.sql` 〜 `04-web.sql` は rAthena の `sql-files/` をそのままコピーしたもの
（内容は無改変。ファイル名の連番だけ MariaDB の初期化順を固定するために付けている）。

- リポジトリ: https://github.com/rathena/rathena
- コミット: `e985006171d2eb320ee512a653f4c83aea3d81b6`（`app/config.env` の `RATHENA_COMMIT` と同じ）

| このリポジトリ | コピー元 |
|---|---|
| `sql-init/01-main.sql` | `sql-files/main.sql` |
| `sql-init/02-logs.sql` | `sql-files/logs.sql` |
| `sql-init/03-roulette_default_data.sql` | `sql-files/roulette_default_data.sql` |
| `sql-init/04-web.sql` | `sql-files/web.sql` |

`item_db*.sql` / `mob_db*.sql` は `conf/inter_athena.conf` の `use_sql_db: no`（既定）のため不要。

## 再取得手順

```sh
COMMIT=e985006171d2eb320ee512a653f4c83aea3d81b6
git clone --filter=blob:none --no-checkout https://github.com/rathena/rathena.git /tmp/rathena
git -C /tmp/rathena checkout "$COMMIT"
cp /tmp/rathena/sql-files/main.sql                  app/rathena/sql-init/01-main.sql
cp /tmp/rathena/sql-files/logs.sql                  app/rathena/sql-init/02-logs.sql
cp /tmp/rathena/sql-files/roulette_default_data.sql app/rathena/sql-init/03-roulette_default_data.sql
cp /tmp/rathena/sql-files/web.sql                   app/rathena/sql-init/04-web.sql
```

`RATHENA_COMMIT` を更新したら、この 4 ファイルも同じコミットのものへ入れ替えること。
なお `/docker-entrypoint-initdb.d` は **MariaDB データディレクトリが空のときだけ**実行される。
既存 DB のスキーマ更新には `sql-files/upgrades/` を手動適用する必要がある。

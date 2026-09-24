/*
 * cp932_roundtrip.c
 *
 * 目的:
 *   rAthena と同じ経路（libmariadb の mysql_set_character_set("cp932") →
 *   mysql_real_escape_string() → INSERT）で CP932 の文字列を保存し、
 *   utf8mb4 接続で読み戻して UTF-8 として正しいかを確認する。
 *
 *   特に CP932 の 2 バイト目が 0x5C になる文字（ソ 0x83 0x5C / 表 0x95 0x5C /
 *   能 0x94 0x5C など）が、エスケープで壊れないことを見る。
 *   rAthena 本体と同じ経路（SET NAMES だけ）は --no-set-charset で再現できる。
 *   MariaDB 11.4 + libmariadb ではセッショントラッキングにより両モードとも PASS する。
 *
 * ビルド・実行手順は tests/README.md を参照。
 *
 * 終了コード: 0 = 一致（成功） / 1 = 不一致または失敗
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <mysql.h>

/* テストする文字列。
 *   CP932: ソ(0x83 0x5C) ラ(0x83 0x89) 0(0x30) n(0x6E)
 *   UTF-8: ソ(E3 82 BD) ラ(E3 83 A9) 0(30) n(6E)
 * 2 バイト目 0x5C のあとに ASCII が続くケースを含める。 */
static const unsigned char CP932_SAMPLE[] = {
    0x83, 0x5C,             /* ソ */
    0x83, 0x89,             /* ラ */
    0x30,                   /* 0  */
    0x6E,                   /* n  */
    0x95, 0x5C,             /* 表 */
    0x94, 0x5C,             /* 能 */
    0x00
};
static const unsigned char UTF8_EXPECTED[] = {
    0xE3, 0x82, 0xBD,       /* ソ */
    0xE3, 0x83, 0xA9,       /* ラ */
    0x30,                   /* 0  */
    0x6E,                   /* n  */
    0xE8, 0xA1, 0xA8,       /* 表 */
    0xE8, 0x83, 0xBD,       /* 能 */
    0x00
};

static void hexdump(const char *label, const unsigned char *p, size_t len)
{
    size_t i;
    printf("  %-16s (%2zu bytes):", label, len);
    for (i = 0; i < len; i++)
        printf(" %02X", p[i]);
    printf("\n");
}

static void die(MYSQL *c, const char *what)
{
    fprintf(stderr, "FAIL: %s: %s\n", what, c ? mysql_error(c) : "(no connection)");
    if (c) mysql_close(c);
    exit(1);
}

int main(int argc, char **argv)
{
    const char *host = getenv("DB_HOST") ? getenv("DB_HOST") : "mariadb";
    const char *user = getenv("DB_USER") ? getenv("DB_USER") : "ragnarok";
    const char *pass = getenv("DB_PASS") ? getenv("DB_PASS") : "";
    const char *name = getenv("DB_NAME") ? getenv("DB_NAME") : "ragnarok";
    unsigned int port = getenv("DB_PORT") ? (unsigned int)atoi(getenv("DB_PORT")) : 3306;

    /* 1 なら mysql_set_character_set() を使わず "SET NAMES cp932" だけ送る
     * （パッチ前の rAthena の挙動の再現）。 */
    int no_set_charset = 0;
    int i;
    for (i = 1; i < argc; i++)
        if (strcmp(argv[i], "--no-set-charset") == 0)
            no_set_charset = 1;

    printf("接続先: %s:%u db=%s user=%s\n", host, port, name, user);
    printf("モード: %s\n\n",
           no_set_charset ? "SET NAMES cp932 のみ（rAthena 本体と同じ経路）"
                          : "mysql_set_character_set(\"cp932\")（明示 API）");

    /* ---------------- 書き込み側: rAthena と同じ cp932 接続 ---------------- */
    MYSQL *w = mysql_init(NULL);
    if (!w) die(NULL, "mysql_init");
    if (!mysql_real_connect(w, host, user, pass, name, port, NULL, 0))
        die(w, "mysql_real_connect (writer)");

    if (no_set_charset) {
        if (mysql_query(w, "SET NAMES cp932") != 0)
            die(w, "SET NAMES cp932");
    } else {
        if (mysql_set_character_set(w, "cp932") != 0)
            die(w, "mysql_set_character_set(cp932)");
    }
    printf("writer character set: %s\n", mysql_character_set_name(w));

    if (mysql_query(w, "DROP TEMPORARY TABLE IF EXISTS cp932_roundtrip") != 0)
        die(w, "drop temp table");
    /* TEMPORARY だと別接続から読めないので通常テーブルを使い、最後に消す */
    if (mysql_query(w,
            "CREATE TABLE IF NOT EXISTS cp932_roundtrip ("
            "  id INT PRIMARY KEY,"
            "  name VARCHAR(24) NOT NULL"
            ") ENGINE=InnoDB") != 0)
        die(w, "create table");
    if (mysql_query(w, "DELETE FROM cp932_roundtrip") != 0)
        die(w, "delete");

    size_t src_len = strlen((const char *)CP932_SAMPLE);
    char escaped[sizeof(CP932_SAMPLE) * 2 + 1];
    unsigned long esc_len =
        mysql_real_escape_string(w, escaped, (const char *)CP932_SAMPLE, (unsigned long)src_len);

    printf("\n[1] エスケープ結果\n");
    hexdump("CP932 入力", CP932_SAMPLE, src_len);
    hexdump("escape 後", (const unsigned char *)escaped, (size_t)esc_len);
    if (esc_len != src_len)
        printf("  !! エスケープでバイト数が増えています（2 バイト目 0x5C が \\ 扱いされた疑い）\n");

    char sql[512];
    snprintf(sql, sizeof(sql),
             "INSERT INTO cp932_roundtrip (id, name) VALUES (1, '%s')", escaped);
    if (mysql_query(w, sql) != 0)
        die(w, "insert");

    /* ---------------- 読み出し側: utf8mb4 接続 ---------------- */
    MYSQL *r = mysql_init(NULL);
    if (!r) die(NULL, "mysql_init (reader)");
    if (!mysql_real_connect(r, host, user, pass, name, port, NULL, 0))
        die(r, "mysql_real_connect (reader)");
    if (mysql_set_character_set(r, "utf8mb4") != 0)
        die(r, "mysql_set_character_set(utf8mb4)");
    printf("\nreader character set: %s\n", mysql_character_set_name(r));

    if (mysql_query(r, "SELECT name FROM cp932_roundtrip WHERE id = 1") != 0)
        die(r, "select");
    MYSQL_RES *res = mysql_store_result(r);
    if (!res) die(r, "store_result");
    MYSQL_ROW row = mysql_fetch_row(res);
    if (!row || !row[0]) {
        fprintf(stderr, "FAIL: 行が取得できませんでした\n");
        mysql_free_result(res);
        mysql_close(r); mysql_close(w);
        return 1;
    }
    unsigned long *lengths = mysql_fetch_lengths(res);
    size_t got_len = (size_t)lengths[0];

    printf("\n[2] 読み戻し結果（utf8mb4 接続）\n");
    hexdump("期待 UTF-8", UTF8_EXPECTED, strlen((const char *)UTF8_EXPECTED));
    hexdump("実際 UTF-8", (const unsigned char *)row[0], got_len);
    printf("  文字列        : %s\n", row[0]);

    int ok = (got_len == strlen((const char *)UTF8_EXPECTED)) &&
             (memcmp(row[0], UTF8_EXPECTED, got_len) == 0);

    mysql_free_result(res);

    /* 後片付け */
    if (mysql_query(w, "DROP TABLE IF EXISTS cp932_roundtrip") != 0)
        fprintf(stderr, "warning: drop table: %s\n", mysql_error(w));

    mysql_close(r);
    mysql_close(w);

    printf("\n結果: %s\n", ok ? "PASS（CP932 -> utf8mb4 の往復が一致）"
                              : "FAIL（一致しませんでした）");
    return ok ? 0 : 1;
}

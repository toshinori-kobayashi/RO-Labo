# JAPANESE_CLIENT_TODO

作成日: 2026-09-23
前提: E2E（login → char → map）成功後に 1 項目ずつ追加・起動確認する。
注意: CLIENT_HANDOFF.md が手元に無いため、本 TODO はタスク指示と一般的な rAthena/kRO クライアント構成知識に基づく。
　　  サーバ側で既に日本語化済みの範囲は SRE に確認し、クライアント側で重複実装しない。

凡例: [S] サーバ側で完結する可能性が高い / [C] クライアント側必須 / [S/C] 両方の整合が必要

---

## 0. 先に SRE へ確認すること（重複実装防止）

- [ ] サーバ送信文字列（MOTD, NPC ダイアログ, Mob 名, Item 名, Skill 名, map 表示名）はどこまで CP932 で日本語化済みか
- [ ] `conf/char_athena.conf` の `char_name_option` / `char_name_letters` で日本語キャラ名を許可しているか
- [ ] Party / Guild 名のバイト長・文字種制限（23 バイト以内、CP932 で日本語約 11 文字）
- [ ] `login_athena.conf` の `new_account` (`_M/_F`) 有効可否

---

## 1. 日本語フォント [C]

- [ ] WARP `Customize Font name` で CP932 対応フォント（例: MS UI Gothic / Meiryo UI）を指定
- [ ] langtype=2 でフォントの文字セットが SHIFTJIS_CHARSET になっているか確認
- [ ] 起動確認: 英語 UI が崩れないこと

## 2. サーバ送信 MOTD [S]

- [ ] `conf/motd.txt` が CP932 で日本語化済みか SRE に確認
- [ ] クライアント側は 1. のフォントのみで表示可能なはず。文字化け時は langtype / フォント charset を疑う

## 3. 日本語 NPC [S]

- [ ] NPC スクリプト側の日本語（CP932）が表示されるか
- [ ] 表示崩れがあれば「G. encoding / display failure」として切り分け

## 4. Mob 日本語名 [S]

- [ ] `mob_db` の日本語名がサーバ送信されるか（クライアント側テーブル不要）

## 5. 日本語チャット表示 [C]

- [ ] 他プレイヤー/NPC/GM からの日本語チャットが表示されること（受信側）
- [ ] フォント指定のみで足りるはず

## 6. 日本語 IME 入力 [C]

- [ ] チャット欄で IME が有効になるか（langtype=2 で有効化されるのが通例だが実機確認）
- [ ] 変換候補ウィンドウの表示位置
- [ ] 失敗時は「H. IME failure」として記録

## 7. 日本語キャラクター名作成 [S/C]

- [ ] サーバ側 `char_name_option` 確認（0. 参照）
- [ ] クライアント側で入力・送信できるか。文字数制限（23 バイト）の挙動

## 8. Party / Guild 日本語名 [S/C]

- [ ] 作成・表示・検索の 3 点で確認

## 9. clientinfo の日本語 display [C]

- [ ] 段階1 の ASCII 構成で E2E 成功後に `<display>` / `<desc>` / `<balloon>` を CP932 化
- [ ] ファイルの実バイト列が CP932 であること（エディタの保存エンコーディングに注意、BOM 無し維持）
- [ ] XML declaration の encoding 値は変更しない（実バイト列と langtype が判定要素）

## 10. msgstringtable.txt [C]

- [ ] `data\msgstringtable.txt` を CP932 で用意（行数は exe 世代に厳密一致が必要。2021-11-03 用）
- [ ] 行数ズレは UI 文言の全体シフトとして現れる → 起動して即確認

## 11. mapnametable.txt [C]

- [ ] `data\mapnametable.txt` を CP932 で用意（`prontera.rsw#プロンテラ#` 形式）
- [ ] Pre-Renewal 対象マップのみで可

## 12. itemInfo (System\itemInfo.lub) [C]

- [ ] Pre-Renewal 用 `itemInfo.lub`（identifiedDisplayName / identifiedDescriptionName を CP932 化）
- [ ] サーバ `item_db` の名前と整合させる（表示名はクライアント側テーブルが優先される項目）
- [ ] ファイル読込パス: `System\itemInfo.lub`（2021 世代。`itemInfo_Sak.lub` を読む場合あり → 実機確認）

## 13. skillinfoz [C]

- [ ] `data\luafiles514\lua files\skillinfoz\skillinfolist.lub` / `skilldescript.lub` の CP932 化
- [ ] Pre-Renewal スキルのみ対象

## 14. Quest UI [C]

- [ ] `data\questid2display.txt`（CP932）
- [ ] 2021 世代では `System\OngoingQuestInfoList_True.lub` / `RecommendedQuestInfoList_True.lub` を読む可能性 → 実機確認
- [ ] `data\cardprefixnametable.txt`（CP932、カード接頭辞）

## 15. その他 UI [C]

- [ ] `data\texture\유저인터페이스\` 系の画像差し替え（ログイン画面・ローディング画像は最低優先）
- [ ] `data\luafiles514\lua files\` の各種 lub（jobname, npcidentity 等）の日本語化
- [ ] `data\texture\effect\` 等は不要

---

## 参考: 資産の出所ルール

- 上記ファイルはすべて **自分で作成する** か **正規入手した kRO 資産を自分で翻訳・編集** して用意する
- jRO 公式 GRF（`C:\Gravity\Ragnarok\data.grf`）からの抽出・流用は禁止
- 公式 / 第三者サーバの GRF・patch を無断取得しない

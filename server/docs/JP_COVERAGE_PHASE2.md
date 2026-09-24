# NPC 日本語化 第 2 フェーズ: 通常プレイ導線の未翻訳ファイル棚卸し

作成日: 2026-09-24 / 対象コミット: `e985006171d2`（`app/config.env` の `RATHENA_COMMIT`）

## 1. 調べ方と母数

- ロード対象は `npc/pre-re/scripts_main.conf` から `import:` を再帰展開して集めた `npc:` パス。
  重複を除いて **527 ファイル**。
- そのうち `app/rathena/overlay-utf8/npc/custom/jp/MANIFEST.tsv` に載っている上流パスが
  **116 ファイル**（MANIFEST 全 117 エントリのうち 1 件は追加のみの `support.txt`）。
- 残り **411 ファイルが未翻訳**。合計 `mes` 行は 141,038。
- 各ファイルの `mes` 数 / `select` 系（`select`/`prompt`/`menu`）数 /
  ヘッダ行の `map` 名は `tools/jp_structure_check.py` のトークナイザで数えた。
  「主な出現マップ」はヘッダ行の第 1 フィールドのマップ名を出現数順に並べたもの
  （`-` は浮動 NPC、`function` は関数スクリプト）。

### 優先度の割り当て規則

依頼の優先度 1〜12 をそのまま使う。判定は次の順序。

1. 範囲外パターン（飛行船・結婚・ミニゲーム・図書館・拡張職・WoE 城・Ep.10 以降の街クエスト・
   BG・インスタンス・イベント・ワープ・湧き設定・マップフラグ）に当たれば範囲外。
2. `npc/jobs/**`・`npc/pre-re/jobs/**`・`npc/quests/first_class/**` → 優先度 11（転職導線）。
3. `npc/{merchants,kafras,other,guides}/**`（`pre-re` 版含む）→ 優先度 12（日常利用 NPC）。
4. ヘッダの 40% 以上が優先度 1〜10 のマップにあれば、最も多いマップの街。
5. どれにも当たらなければ「横断・優先度マップ外」（第 4 節）。

## 2. 集計結果

| 優先度 | 区分 | ファイル数 | mes 合計 |
|---|---|---|---|
| 1 | 初心者修練場（`new_*`） | 0 | 0 |
| 2 | プロンテラ | 5 | 1,050 |
| 3 | イズルード | 5 | 0 |
| 4 | ゲフェン | 2 | 822 |
| 5 | フェイヨン | 5 | 5,281 |
| 6 | アルベルタ | 3 | 544 |
| 7 | モロク | 2 | 1,739 |
| 8 | アルデバラン | 1 | 0 |
| 9 | コモド | 0 | 0 |
| 10 | ジュノー | 2 | 1,766 |
| 11 | 転職導線 | 23 | 6,188 |
| 12 | 日常利用 NPC | 18 | 1,007 |
| **合計** | | **66** | **18,397** |

未翻訳 411 ファイル・141,038 mes のうち、**通常プレイ導線に当たるのは 66 ファイル・18,397 mes（13%）**。
残りは Ep.10 以降のクエスト（70,638 mes）を筆頭に、拡張職・ミニゲーム・WoE 等の範囲外。

> 優先度 1（初心者修練場）が 0 件なのは `npc/pre-re/jobs/novice/novice.txt` が翻訳済みのため。
> 優先度 9（コモド）が 0 件なのは `npc/cities/comodo.txt` が翻訳済みのため。

## 3. 優先度別の一覧

`mes` = 台詞行数、`sel` = `select`/`prompt`/`menu` の数。

### 優先度 2: プロンテラ（5 ファイル / mes 1,050）

| ファイル | mes | sel | 主な出現マップ | 備考 |
|---|---|---|---|---|
| `npc/quests/doomed_swords.txt` | 847 | 8 | prontera, prt_in, morocc, izlude_in, pay_fild08 | 呪われた剣クエスト。主要街に 1 体ずつ配置 |
| `npc/quests/juice_maker.txt` | 150 | 9 | prt_in(2), payon_in03 | ジュース屋。低 Lv 帯の常用 NPC |
| `npc/quests/mrsmile.txt` | 53 | 1 | alberta, aldebaran, geffen, moc_ruins, payon, prontera | **ミスターサイル（お面屋）。主要 6 街に duplicate で配置**（イズルード分は `npc/pre-re/quests/mrsmile.txt`） |
| `npc/pre-re/cities/prontera.txt` | 0 | 0 | prontera(1) | `duplicate(prtguard) Guard#5pront` のみ。台詞なし・**頭上名は英語** |
| `npc/pre-re/quests/cooking_quest.txt` | 0 | 0 | prt_castle(4) | Pre-RE 用の配置差し替え（ヘッダのみ） |

### 優先度 3: イズルード（5 ファイル / mes 0）

すべて Pre-RE 用の配置差し替え（`duplicate` / ヘッダのみ）で台詞は持たない。
ただし **頭上名は英語のまま**なので、第 2 フェーズ（`docs/jp-npc-names.tsv`）の対象になる。

| ファイル | mes | sel | 主な出現マップ | 備考 |
|---|---|---|---|---|
| `npc/pre-re/cities/izlude.txt` | 0 | 0 | izlude(9) | `Sailor#izlude` 等 9 体の duplicate。翻訳済み `npc/cities/izlude.txt` の参照元に依存（conf で再追加済み） |
| `npc/pre-re/quests/monstertamers.txt` | 0 | 0 | izlude_in(1) | ヘッダのみ |
| `npc/pre-re/quests/mrsmile.txt` | 0 | 0 | izlude(1) | ヘッダのみ |
| `npc/pre-re/quests/quests_izlude.txt` | 0 | 0 | izlude(1) | ヘッダのみ |
| `npc/pre-re/quests/skills/swordman_skills.txt` | 0 | 0 | izlude_in(1) | ヘッダのみ |

### 優先度 4: ゲフェン（2 ファイル / mes 822）

| ファイル | mes | sel | 主な出現マップ | 備考 |
|---|---|---|---|---|
| `npc/quests/newgears/2008_headgears.txt` | 436 | 18 | gef_fild05, morocc_in, in_orcs01 | 2008 年頭防具クエ。複数街に分散 |
| `npc/quests/counteragent_mixture.txt` | 386 | 13 | geffen, geffen_in, alberta_in | **中和剤／混合剤の作成 NPC。アルケミスト導線で常用** |

### 優先度 5: フェイヨン（5 ファイル / mes 5,281）

| ファイル | mes | sel | 主な出現マップ | 備考 |
|---|---|---|---|---|
| `npc/quests/newgears/2004_headgears.txt` | 2,024 | 39 | alde_alche, geffen, pay_dun03, yuno | 2004 年頭防具クエ。街をまたぐ |
| `npc/quests/eye_of_hellion.txt` | 1,707 | 19 | payon(6), prontera(3), morocc_in | ヘリオンの目クエスト |
| `npc/quests/doomed_swords_quest.txt` | 795 | 0 | mjolnir_02, payon, morocc | 呪われた剣クエストの本体（`doomed_swords.txt` と対） |
| `npc/quests/newgears/2006_headgears.txt` | 755 | 11 | rachel, hugel, payon, payon_in03 | 2006 年頭防具クエ |
| `npc/pre-re/quests/quest_payon.txt` | 0 | 0 | payon_in01(1) | ヘッダのみ |

### 優先度 6: アルベルタ（3 ファイル / mes 544）

| ファイル | mes | sel | 主な出現マップ | 備考 |
|---|---|---|---|---|
| `npc/quests/monstertamers.txt` | 464 | 5 | alberta_in, aldeba_in, comodo | モンスターテイマー（ペット用テイミングアイテム） |
| `npc/quests/bunnyband.txt` | 80 | 2 | alberta(1) | **バニーバンド作成。依頼書の `bunny_band.txt` は上流に無く、実際のファイル名は `bunnyband.txt`** |
| `npc/pre-re/cities/alberta.txt` | 0 | 0 | alberta(8) | duplicate 8 体。台詞なし・頭上名は英語 |

### 優先度 7: モロク（2 ファイル / mes 1,739）

| ファイル | mes | sel | 主な出現マップ | 備考 |
|---|---|---|---|---|
| `npc/quests/obb_quest.txt` | 1,313 | 13 | moc_ruins, alberta, comodo | 古い青い箱クエスト |
| `npc/cities/morocc.txt` | 426 | 8 | moc_ruins(14), moc_fild16(10), morocc(9) | **街 NPC ファイルとして存在する。主要 8 街のうちモロクだけ未翻訳**（prontera / izlude / alberta / aldebaran / comodo / geffen / payon / yuno は翻訳済み）。`npc/pre-re/cities/morocc.txt` は上流に存在しない |

### 優先度 8: アルデバラン（1 ファイル / mes 0）

| ファイル | mes | sel | 主な出現マップ | 備考 |
|---|---|---|---|---|
| `npc/pre-re/cities/lutie.txt` | 0 | 0 | aldebaran(1) | ルティエ行きの配置差し替え。ヘッダのみ |

### 優先度 9: コモド

未翻訳ファイルなし（`npc/cities/comodo.txt` と `npc/pre-re/guides/guides_comodo.txt` は翻訳済み）。

### 優先度 10: ジュノー（2 ファイル / mes 1,766）

| ファイル | mes | sel | 主な出現マップ | 備考 |
|---|---|---|---|---|
| `npc/quests/bard_quest.txt` | 1,766 | 25 | yuno_in01(5), yuno_in04, morocc, geffen | バードのリングクエスト |
| `npc/pre-re/cities/yuno.txt` | 0 | 0 | yuno(7) | duplicate 7 体。台詞なし・頭上名は英語 |

### 優先度 11: 転職導線（23 ファイル / mes 6,188）

| ファイル | mes | sel | 主な出現マップ | 備考 |
|---|---|---|---|---|
| `npc/quests/first_class/tu_sword.txt` | 1,560 | 25 | morocc, morocc_in, izlude_in, geffen | **1 次職チュートリアル（剣士）** |
| `npc/quests/first_class/tu_archer.txt` | 1,116 | 21 | pay_arche(5), prontera(3), payon_in02 | **1 次職チュートリアル（アーチャー）** |
| `npc/quests/first_class/tu_acolyte.txt` | 1,059 | 16 | prt_monk(11), monk_in, prt_church | **1 次職チュートリアル（アコライト）** |
| `npc/quests/first_class/tu_magician01.txt` | 543 | 5 | geffen(2) | **1 次職チュートリアル（マジシャン）** |
| `npc/quests/first_class/tu_merchant.txt` | 442 | 6 | prontera(3), prt_in(2), alberta_in | **1 次職チュートリアル（商人）** |
| `npc/quests/first_class/tu_ma_th01.txt` | 425 | 4 | moc_fild18/11/12/17 | 1 次職チュートリアル（マジシャン・シーフ共通のフィールド側） |
| `npc/quests/first_class/tu_thief01.txt` | 412 | 8 | moc_ruins(1) | **1 次職チュートリアル（シーフ）** |
| `npc/jobs/2-2a/Creator.txt` | 81 | 2 | valkyrie(1) | 転生 2 次職転職（ヴァルキリー）。以下 12 ファイルも同構成 |
| `npc/jobs/2-1a/AssassinCross.txt` | 53 | 1 | valkyrie(1) | 転生 2 次職転職 |
| `npc/jobs/2-2a/Stalker.txt` | 51 | 1 | valkyrie(1) | 転生 2 次職転職 |
| `npc/jobs/2-2a/Professor.txt` | 50 | 1 | valkyrie(1) | 転生 2 次職転職 |
| `npc/jobs/2-1a/WhiteSmith.txt` | 46 | 1 | valkyrie(1) | 転生 2 次職転職 |
| `npc/jobs/2-2a/Champion.txt` | 45 | 1 | valkyrie(1) | 転生 2 次職転職 |
| `npc/jobs/2-1a/HighWizard.txt` | 44 | 1 | valkyrie(1) | 転生 2 次職転職 |
| `npc/jobs/2-2a/Paladin.txt` | 44 | 1 | valkyrie(1) | 転生 2 次職転職 |
| `npc/jobs/2-1a/LordKnight.txt` | 42 | 1 | valkyrie(1) | 転生 2 次職転職 |
| `npc/jobs/2-1a/Sniper.txt` | 42 | 1 | valkyrie(1) | 転生 2 次職転職 |
| `npc/jobs/2-2a/Gypsy.txt` | 42 | 1 | valkyrie(1) | 転生 2 次職転職 |
| `npc/jobs/2-1a/HighPriest.txt` | 41 | 1 | valkyrie(1) | 転生 2 次職転職 |
| `npc/jobs/2-2a/Clown.txt` | 40 | 1 | valkyrie(1) | 転生 2 次職転職 |
| `npc/quests/mage_solution.txt` | 10 | 2 | pay_arche, moc_ruins | マジシャン関連の小 NPC |
| `npc/pre-re/quests/first_class/tu_archer.txt` | 0 | 0 | prt_castle(2), mjolnir_11 | Pre-RE 用の配置差し替え |
| `npc/pre-re/jobs/2-2/crusader.txt` | 0 | 0 | prt_castle(3), job_cru(2) | Pre-RE 用の配置差し替え |

### 優先度 12: 日常利用 NPC（18 ファイル / mes 1,007）

| ファイル | mes | sel | 主な出現マップ | 備考 |
|---|---|---|---|---|
| `npc/kafras/dts_warper.txt` | 422 | 12 | einbroch, yuno, prontera, moc_ruins | DTS（ダンジョン転送）。カプラ系の転送 NPC |
| `npc/other/mercenary_rent.txt` | 180 | 6 | prontera(3), pay_arche(3), izlude | 傭兵レンタル |
| `npc/merchants/buying_shops.txt` | 128 | 5 | que_job01, alberta_in | 買取露店ライセンス |
| `npc/pre-re/other/resetskill.txt` | 89 | 2 | prontera(1) | **Pre-RE のステータス／スキルリセット NPC** |
| `npc/kafras/cool_event_corp.txt` | 62 | 3 | lighthalzen, hugel, rachel | クールイベント社（Ep.10 以降の街のみ） |
| `npc/other/auction.txt` | 32 | 2 | auction_01/02, moc_ruins, prontera | オークション受付 |
| `npc/merchants/cashheadgear_dye.txt` | 29 | 3 | prt_in(1) | 頭防具の染色 |
| `npc/merchants/wander_pet_food.txt` | 26 | 2 | prontera(2) | ペットフード |
| `npc/other/guildpvp.txt` | 22 | 3 | pvp_y_room(1) | ギルド PvP 受付 |
| `npc/other/CashShop_Functions.txt` | 13 | 17 | function(11) | キャッシュショップ用関数。翻訳済み 117 ファイルからの呼び出しは無い（将来キャッシュショップを使うなら対象） |
| `npc/pre-re/other/msg_boards.txt` | 4 | 0 | izlude(2) | 掲示板（Pre-RE 版） |
| `npc/other/Global_Functions.txt` | 0 | 0 | function(28) | **最重要。第 5 節参照** |
| `npc/merchants/shops.txt` | 0 | 0 | 全街（lhz_in02 12 / moc_ruins 8 / prontera 8 / geffen_in 7 …） | **shop ヘッダ 156 個。会話は無いが頭上名が英語**（`Tool Dealer#alb`, `Weapon Dealer#alde`, `Armor Dealer#ama` …） |
| `npc/pre-re/merchants/shops.txt` | 0 | 0 | moc_ruins(6), izlude(4), que_ng(3) | **shop ヘッダ 27 個。同上**（`Trading Merchant#alb`, `Butcher#iz`, `Tool Dealer#iz` …） |
| `npc/other/gm_npcs.txt` | 0 | 0 | function(1) | `F_GM_NPC`。GM レベル判定だけで表示文字列なし → **翻訳不要** |
| `npc/pre-re/merchants/socket_enchant2.txt` | 0 | 0 | moc_ruins(1) | ヘッダのみ（本体 `npc/merchants/socket_enchant2.txt` は翻訳済み） |
| `npc/pre-re/other/mercenary_rent.txt` | 0 | 0 | izlude(2) | ヘッダのみ |
| `npc/pre-re/other/pvp.txt` | 0 | 0 | pvp_y_room, pvp_n_room | ヘッダのみ（本体 `npc/other/pvp.txt` は翻訳済み） |

## 4. 範囲外の内訳（参考）

| 区分 | ファイル数 | mes 合計 |
|---|---|---|
| Ep.10 以降の街クエスト（`quests_ein*` / `quests_lighthalzen` / `quests_hugel` / `quests_rachel` / `quests_veins` / `quests_moscovia` / `quests_13_*` / `quests_14_*` / `quests_nameless` / `kiel_hyre` / `okolnir` / `the_sign_quest` / `seals/*`） | 27 | 70,638 |
| 横断・優先度マップ外（Ep.9 以前だが主要 10 街の外。`quests_louyang` 2,748 / `cities/lighthalzen` 2,112 / `partyrelay` 2,088 / `lvl4_weapon_quest` 1,791 / `quests_ayothaya` 1,774 / `quests_gonryun` 1,681 / `quests_juperos` 1,606 / `cooking_quest` 1,515 ほか） | 31 | 27,120 |
| 拡張職（ガンスリンガー・忍者・テコン・ソウルリンカー・スパノビ・星帝） | 12 | 4,741 |
| ミニゲーム（`turbo_track` / `poring_war` / `monster_race` / `hugel_bingo` / `comodo_gambling` / `fortune` / `gympass` / `monster_museum` / `powernpc`） | 10 | 4,694 |
| WoE 城（`guild*` / `agit*` / `guildrelay`） | 36 | 3,178 |
| 飛行船（`airports/*` / `quests_airship`） | 10 | 2,914 |
| 図書館（`other/books.txt`） | 1 | 2,829 |
| `quests_morocc.txt`（共通側の Satan Morroc） | 1 | 1,737 |
| インスタンス | 4 | 1,445 |
| 結婚（`marriage` / `divorce` / `jawaii`） | 5 | 1,419 |
| バトルグラウンド | 12 | 911 |
| イベント | 2 | 879 |
| ワープ（会話なし） | 96 | 136 |
| マップフラグ / 湧き設定 | 98 | 0 |

> 「横断」に落ちたもののうち `npc/quests/cooking_quest.txt`（1,515 mes、浮動 NPC）と
> `npc/quests/partyrelay.txt`（2,088 mes、主要街とエインブロック／フィゲル）は、
> 通常プレイで踏む可能性がある。第 2 波以降で拾い直す候補。

## 5. `npc/other/Global_Functions.txt` は最優先（mes 0 でも影響が大きい）

このファイル自体に `mes` は 1 行も無いが、**翻訳済み NPC が呼ぶ共通関数の定義元**であり、
返り値の英語がそのまま日本語の `mes` / `select` に埋め込まれて表示される。

翻訳済み 117 ファイルからの呼び出し実績（`callfunc` / `callsub` の静的集計）:

| 関数 | 呼出回数 | 表示への影響 |
|---|---|---|
| `Job_Change` | 20 | 表示文字列なし（転職処理のみ） |
| `F_ClearJobVar` | 20 | 表示文字列なし |
| `F_CanChangeJob` | 13 | 表示文字列なし |
| `F_IsEquipIDHack` / `F_IsEquipCardHack` / `F_IsEquipRefineHack` | 各 3 | `logmes` のみ（プレイヤーには出ない） |
| `F_ClearGarbage` / `F_CanOpenStorage` | 各 1 | 表示文字列なし |
| `F_InsertPlural` | 1 | **英語が出る**（`jobs/2-2/alchemist.txt:292`） |

さらに `callfunc` を介さない直接呼び出しで次が使われている。

- `npc/custom/jp/merchants/refine.txt:645` と `npc/custom/jp/merchants/advanced_refiner.txt:33`
  が `F_getpositionname()` の返り値で `select` のメニューを組み立てている。
  この関数は `"Accessory 1"` `"Shoes"` `"Robe"` `"Head"` `"Body"` `"Left hand"` `"Right hand"` …
  を返すので、**精錬 NPC の装備選択メニューは日本語化済みの NPC なのに英語で表示される**。

その他 `F_Hi` / `F_Bye`（英語の挨拶をランダムで返す）、`F_GetWeaponType` / `F_GetArmorType`、
`Time2Str`、`F_GetPlural` / `F_GetArticle` / `F_GetNumSuffix` も英語を返す。

→ `Global_Functions.txt` は `mes` 0 だが**最優先で翻訳すべき**。
　 ただし `F_GetPlural` / `F_GetArticle` / `F_InsertArticle` は英語の複数形・冠詞処理そのものなので、
　 日本語では「関数を訳す」のではなく「呼び出し側の文面を作り直す」判断が必要（要相談）。

## 6. 結論: まずやるべき 12 ファイル

通常プレイ導線（優先度 1〜12）の合計は **66 ファイル / mes 18,397**。
そのうち費用対効果が高い順に以下を推奨する（合計 mes 約 6,900）。

| # | ファイル | mes | 推す理由 |
|---|---|---|---|
| 1 | `npc/other/Global_Functions.txt` | 0 | 翻訳済み NPC（精錬・アルケミスト）の表示が英語のまま。mes 0 なので作業量も小さい |
| 2 | `npc/merchants/shops.txt` + `npc/pre-re/merchants/shops.txt` | 0 | shop ヘッダ 183 個の頭上名。全街で常時見える。第 2 フェーズ（頭上名）の枠組みでまとめて処理できる |
| 3 | `npc/cities/morocc.txt` | 426 | 主要 8 街で唯一未翻訳の街 NPC ファイル |
| 4 | `npc/quests/first_class/tu_sword.txt` | 1,560 | 剣士チュートリアル。転職直後に全員が通る |
| 5 | `npc/quests/first_class/tu_archer.txt` | 1,116 | アーチャーチュートリアル |
| 6 | `npc/quests/first_class/tu_acolyte.txt` | 1,059 | アコライトチュートリアル |
| 7 | `npc/quests/first_class/tu_magician01.txt` | 543 | マジシャンチュートリアル |
| 8 | `npc/quests/first_class/tu_merchant.txt` | 442 | 商人チュートリアル |
| 9 | `npc/quests/first_class/tu_thief01.txt` | 412 | シーフチュートリアル |
| 10 | `npc/kafras/dts_warper.txt` | 422 | ダンジョン転送。カプラ導線の一部で常用 |
| 11 | `npc/quests/counteragent_mixture.txt` | 386 | 中和剤／混合剤。アルケミスト導線で常用（`blacksmith_skills.txt` と用語を揃える） |
| 12 | `npc/other/mercenary_rent.txt` + `npc/pre-re/other/resetskill.txt` + `npc/quests/juice_maker.txt` + `npc/quests/mrsmile.txt` + `npc/quests/bunnyband.txt` | 552 | いずれも 200 mes 未満の小物だが、主要街に常駐していて目に付く |

補足:

- 4〜9 の `tu_*.txt` は合計 5,132 mes（`tu_ma_th01.txt` 425 を足すと 5,557）。まとめて 1 バッチにすると
  用語（ステータス・スキル・チュートリアル報酬）が揃えやすい。
- 転生 2 次職の `npc/jobs/2-{1a,2a}/*.txt` 13 ファイル（合計 621 mes）は中身がほぼ同型なので、
  余力ができたら一括で処理するとよい。ただし Pre-RE の通常プレイでは到達が遅い。
- `npc/pre-re/cities/{prontera,izlude,alberta,yuno,lutie}.txt` は台詞 0 だが頭上名が英語。
  `docs/jp-npc-names.tsv` 側で扱う（本文の翻訳対象ではない）。
- `npc/other/gm_npcs.txt` は表示文字列が無いので翻訳不要。

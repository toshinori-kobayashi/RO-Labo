# 日本語化 用語集（NPC スクリプト翻訳用）

Batch を跨いで同じ訳語を使うための一覧。新しい用語を決めたら**ここに追記してから**翻訳に使うこと。jRO 公式テキストの転載はしないが、固有名詞のカタカナ表記は日本のプレイヤーに通じる一般的な表記に寄せる。

## 文体

- 基本は「です・ます」。NPC の性格に合わせて崩してよい（衛兵・騎士は硬め、盗賊ギルドや酒場は砕けた口調、子どもは幼く）。
- 現代的すぎるネットスラングや流行語は使わない。過剰な意訳をしない。
- 句読点は「。」「、」。引用は「」。強調に `^RRGGBB` 色コードが付いていれば位置ごと維持する。
- 1 行（`mes` 1 つ）は全角 22 文字目安。長文は既存の行数の中で割り付け直す（行の追加・削除はしない）。
- 話者タグ `mes "[Name]"` は「[役職名 名前]」または「[名前]」。同一 NPC 内で揺らさない。
- 使ってよい文字は JIS X 0208 + ASCII。波ダッシュは「～」(U+FF5E)、マイナスは「－」(U+FF0D)、絵文字・半角カナ・機種依存文字は禁止。日本語の直後に `\"` を置かない。

## 都市・地域

| 英語 | 日本語 | 英語 | 日本語 |
|---|---|---|---|
| Prontera | プロンテラ | Rune-Midgarts | ルーンミッドガッツ |
| Izlude | イズルード | Schwarzwald | シュバルツバルド |
| Geffen | ゲフェン | Arunafeltz | アルナベルツ |
| Payon | フェイヨン | Byalan Island | ビョルン島 |
| Morocc / Morroc | モロク | Sograt Desert | ソグラト砂漠 |
| Alberta | アルベルタ | Mt. Mjolnir | ミョルニール山脈 |
| Al De Baran / Aldebaran | アルデバラン | Culvert (Prontera) | プロンテラ下水道 |
| Comodo | コモド | Orc Dungeon | オークダンジョン |
| Juno / Yuno | ジュノー | Glast Heim | グラストヘイム |
| Lutie | ルティエ | Clock Tower | 時計塔 |
| Umbala | ウンバラ | Sphinx | スフィンクス |
| Niflheim | ニブルヘイム | Pyramid | ピラミッド |
| Louyang | 龍之城 | Ant Hell | アリ地獄 |
| Ayothaya | アユタヤ | Payon Cave | フェイヨン洞窟 |
| Amatsu | アマツ | Sunken Ship | 沈没船 |
| Gonryun / Kunlun | 崑崙 | Turtle Island | タートルアイランド |
| Einbroch | アインブロック | Coal Mine | 炭鉱 |
| Einbech | アインベフ | Toy Factory | おもちゃ工場 |
| Lighthalzen | リヒタルゼン | Magma Dungeon | ノーグロード |
| Hugel | フィゲル | Kiel Hyre Academy | キール研究所 |
| Rachel | ラヘル | Thanatos Tower | タナトスタワー |
| Veins | ベインス | Jawaii | ジャワイ |
| Moscovia | モスコビア | Training Grounds | 初心者修練場 |
| Orc Village | オーク村 | Kobold Village | コボルド村 |
| Goblin Village | ゴブリン村 | Valley of Gyoll | ギョルの谷 |
| Paros Lighthouse | パロス灯台 | | |
| Brasilis | ブラジリス | | |
| Sandaruman Fortress | サンダルマン要塞 | Juperos | ユペロス |
| Solomon / Mineta / Snotora（ジュノーの三島） | ソロモン / ミネタ / スノトラ | Reudelus（定期船の航路名） | ロイデルス |
| Dead Pit | デッドピット | | |

## 職業

| 英語 | 日本語 | 英語 | 日本語 |
|---|---|---|---|
| Novice | ノービス | Super Novice | スーパーノービス |
| Swordman | 剣士 | Knight / Crusader | ナイト / クルセイダー |
| Mage / Magician | マジシャン | Wizard / Sage | ウィザード / セージ |
| Archer | アーチャー | Hunter / Bard / Dancer | ハンター / バード / ダンサー |
| Acolyte | アコライト | Priest / Monk | プリースト / モンク |
| Merchant | 商人 | Blacksmith / Alchemist | ブラックスミス / アルケミスト |
| Thief | シーフ | Assassin / Rogue | アサシン / ローグ |
| High Novice / High Swordman 等 | ハイノービス / ハイソードマン 等 | Lord Knight / Paladin | ロードナイト / パラディン |
| High Wizard / Professor | ハイウィザード / プロフェッサー | Sniper / Clown / Gypsy | スナイパー / クラウン / ジプシー |
| High Priest / Champion | ハイプリースト / チャンピオン | Whitesmith / Creator | ホワイトスミス / クリエイター |
| Assassin Cross / Stalker | アサシンクロス / チェイサー | Taekwon / Star Gladiator / Soul Linker | テコンキッド / 拳聖 / ソウルリンカー |
| Gunslinger / Ninja | ガンスリンガー / 忍者 | Job Level / Base Level | ジョブレベル / ベースレベル |
| job change | 転職 | rebirth / transcend | 転生 |

## 施設・役職・組織

| 英語 | 日本語 | 英語 | 日本語 |
|---|---|---|---|
| Kafra / Kafra Employee / Kafra Corporation | カプラ / カプラ職員 / カプラサービス社 | Guide（街の案内 NPC の役職・話者タグ） | 案内係 |
| Tool Shop / Tool Dealer | 道具屋 / 道具商人 | Weapon Shop / Weapon Dealer | 武器屋 / 武器商人 |
| Armor Shop / Armor Dealer | 防具屋 / 防具商人 | Inn / Innkeeper | 宿屋 / 宿屋の主人 |
| Tavern / Pub | 酒場 | Blacksmith (NPC 役職) | 鍛冶屋 |
| Refiner / Refine / Refining | 精錬師 / 精錬 | Upgrade (weapon) | 精錬（武器の +1 等） |
| Repairman / Repair | 修理屋 / 修理 | Chivalry / Knight Guild | 騎士団 |
| Church / Sanctuary / Priest (役職) | 教会 / 聖堂 / 神父 | Sister / Nun | シスター |
| Mage Guild / Wizard Guild | マジシャンギルド / ウィザードギルド | Archer Guild | アーチャーギルド |
| Merchant Guild / Union | 商人ギルド / 商人組合 | Thief Guild | シーフギルド |
| Assassin Guild | アサシンギルド | Rogue Guild | ローグギルド |
| Swordman Association | 剣士協会 | Job Agency | ジョブエージェンシー |
| Blacksmith Guild | ブラックスミスギルド | Blacksmith Guildsman（役職） | ブラックスミスギルド職員 |
| Kafra Storage / Storage | 倉庫 | Guild Storage | ギルド倉庫 |
| Pushcart / Cart | カート | Peco Peco (乗り物) / Falcon | ペコペコ / ファルコン |
| Save (point) | セーブ / セーブポイント | Teleport / Warp | テレポート / ワープ |
| Sailor / Captain | 船員 / 船長 | Ferry / Ship / Boat | 船 / 定期船 |
| Bulletin Board | 掲示板 | Mailbox / Mail | 郵便ポスト / 郵便 |
| Guard / Soldier | 衛兵 / 兵士 | Knight (役職) | 騎士 |
| Library / Librarian | 図書館 / 司書 | Castle | 城 |
| Arena / Colosseum | 闘技場 | PvP Room / PvP | PvP ルーム / PvP |
| PVP Fight/Combat/Compete Square（表記揺れはすべて統一） | 闘技場 | PVP Narrator | PVP案内係 |
| Arena（npc/other/arena/ の Izlude Battle Arena・Time Force Battle 施設。上記「Arena/Colosseum→闘技場」の PVP ルームとは別施設のため「アリーナ」で統一） | アリーナ | Time Force Battle | タイムフォースバトル |
| Arena Point(s) | アリーナポイント | Staff（npc/other/arena/ の受付役職のみの話者タグ） | スタッフ |
| Gate Keeper（PVP 入場受付） | 門番 | Registration/Register Staff | 受付スタッフ |
| Spectator's Entrance | 観戦者入口 | | |
| Guild / Party | ギルド / パーティ | War of Emperium / WoE | 攻城戦 / WoE |
| Zeny | Zeny（そのまま） | Kafra Points / Cash Points | カプラポイント / キャッシュポイント |
| Pharmacist / Apothecary | 薬剤師 | Alchemist (NPC 販売員) | 錬金術師 |
| Stylist / Hairdresser / Dyer | 美容師 / 理容師 / 染色屋 | Quiver | 矢筒 |
| Dye Maker (NPC 役職) | 染料職人 | Gemstone Trader (NPC 役職) | 宝石商 |
| Milk Vendor / Trader (NPC 役職) | 牛乳商人 | | |
| Trainer / Instructor | 教官 | Receptionist | 受付 |
| Dungeon / Field | ダンジョン / フィールド | Monster | モンスター |
| Doctor's Office | 医院 | City Hall | 役所 |
| Temple | 神殿 | Shrine | 神社 |
| Airport | 飛行場 | Airship | 飛行船 |
| Hotel / Hotel Employee | ホテル / ホテル従業員 | Hotel Keeper | ホテル支配人 |
| Breeder (Peco Peco / Falcon) | 飼育員 | Warg | ワーグ |
| Cash Mount | キャッシュマウント | | |
| Swordman Hall (Izlude) | 剣士ホール | Marina (Izlude, 船着き場) | 港 |
| Magic Academy (Geffen, Mage 転職施設) | 魔法学院 | Geffen Tower | ゲフェンタワー |
| Mercenary Guild (Morocc) | 傭兵ギルド | Sorcerer Guild (Aldebaran, Mage Guild とは別施設) | 魔道士ギルド |
| Kafra Main Office (Aldebaran) | カプラ本店 | Central Palace (Payon) | 王宮 |
| The Empress (Payon, 施設名) | 女王の間 | Palace Annex (Payon) | 王宮別館 |
| Royal Kitchen (Payon) | 王宮の厨房 | Archer Village (Payon) | アーチャー村 |
| End Conversation（案内 NPC の会話終了選択肢） | 会話を終える | Sage Castle (Juno, Sage 転職施設) | セージ城 |
| Street of Book Stores (Juno) | 書店街 | Juphero Plaza (Juno) | ジュフェロ広場 |
| Library of the Republic (Juno) | 共和国図書館 | Schweicherbil Magic Academy (Juno) | シュバイヒルビル魔法学院 |
| Monster Museum (Juno) | モンスター博物館 | Forge（鍛冶場、Juno/一般） | 鍛冶場 |
| Casino (Comodo) | カジノ | | |
| Hula Dance Stage (Comodo, Dancer 転職施設) | フラダンス会場 | Weapon and Armor Shop (Comodo) | 武器防具屋 |
| Tourist Shop (Comodo) | みやげ物屋 | Kafra Co. Western Branch (Comodo) | カプラ西支店 |
| Chief's House (Comodo) | 族長の家 | Campground (Comodo) | キャンプ場 |
| Train Station（駅、Einbroch/Einbech） | 駅 | Factory (Einbroch) | 工場 |
| Plaza（広場、Einbroch/一般） | 広場 | Laboratory (Einbroch) | 研究所 |
| Blacksmith Guild (Einbroch) | 鍛冶ギルド | Einbroch Tower | アインブロックタワー |
| Swordman Guild (Einbech) | 剣士ギルド | Mine（鉱山、Einbech） | 鉱山 |
| Rekenber Corporation (Lighthalzen) | レーケンバー社 | Police Station (Lighthalzen) | 警察署 |
| Bank（銀行、一般） | 銀行 | Jewelry Shop (Lighthalzen) | 宝飾店 |
| Department Store (Lighthalzen) | デパート | | |

## 主要アイテム（`getitemname()` で動的に出るものは英語のまま。会話文中で直接書かれるものだけ訳す）

| 英語 | 日本語 | 英語 | 日本語 |
|---|---|---|---|
| Red / Orange / Yellow / White Potion | 赤ポーション / 橙ポーション / 黄ポーション / 白ポーション | Blue Potion | 青ポーション |
| Red / Yellow / White / Blue Herb | 赤ハーブ / 黄ハーブ / 白ハーブ / 青ハーブ | Green Herb / Green Potion | 緑ハーブ / 緑ポーション |
| Fly Wing / Butterfly Wing | ハエの羽 / 蝶の羽 | Novice Potion | ノービスポーション |
| Jellopy | ジェロピー | Empty Bottle | 空き瓶 |
| Knife / Cotton Shirt | ナイフ / コットンシャツ | Trunk | 木の幹 |
| Resin | 松脂 | Pointed Scale | とがった鱗 |
| Wooden Block | 木片 | Tentacle | 触手 |
| Bill of Birds | 鳥のくちばし | Banana Juice | バナナジュース |
| Feather / Feather of Birds | 羽根 / 鳥の羽 | Clover | クローバー |
| Phracon / Emveretarcon | フラコン / エンベルタコン | Oridecon / Elunium | オリデオコン / エルニウム |
| Rough Oridecon / Rough Elunium | 原石オリデオコン / 原石エルニウム | Steel / Iron / Iron Ore | 鋼鉄 / 鉄 / 鉄鉱石 |
| Coal | 石炭 | Yellow Gemstone / Blue / Red Gemstone | 黄色いジェムストーン / 青い / 赤いジェムストーン |
| Arrow / Silver Arrow / Fire Arrow | 矢 / 銀の矢 / 火の矢 | Card | カード |
| Old Blue Box / Old Purple Box | 古く青い箱 / 古く紫の箱 | Gift Box | プレゼントボックス |
| Mushroom Spore | キノコの胞子 | Poison Spore | 毒キノコの胞子 |
| Sticky Mucus | ネバネバした液体 | Animal Skin | 動物の皮 |
| Jellopy 等の収集品 | 「収集品」 | Equipment / Weapon / Armor | 装備 / 武器 / 防具 |
| Enchanted Stone | 精霊石 | | |
| Shell | 貝殻 | Fluff | 綿毛 |
| Tree Root | 木の根っこ | Worm Peeling | ミミズの皮 |
| Chrysalis | サナギ | Medicine Bowl | 調合ボウル |
| Carrot | ニンジン | | |
| Scarlet / Lemon / White / Black Dyestuffs | スカーレット染料 / レモン染料 / ホワイト染料 / ブラック染料 | Cobaltblue / Darkgreen / Orange / Violet Dyestuffs | コバルトブルー染料 / ダークグリーン染料 / オレンジ染料 / バイオレット染料 |
| Counteragent | 中和剤 | Mixture | 混合剤 |
| Large Jellopy | ラージジェロピー | Rice Cake | お餅 |
| Holy Guard / Holy Avenger | ホーリーガード / ホーリーアベンジャー | Sacred Mission | セイクリッドミッション |
| Dagger of Counter | カウンターダガー | Worn-Out Magic Scroll | 使い古された魔法の巻物 |
| Pieces of Ymir's Heart | イミルの心の欠片 | | |
| Gakkung (Bow) | ガクカン | | |
| Manuk's Opportunity | マヌクの好機 | Manuk's Courage | マヌクの勇気 |
| Manuk's Faith | マヌクの信仰 | Pinguicula's Fruit Jam | ピングイクラの果実ジャム |
| Luciola's Honey Jam | ルキオラの蜂蜜ジャム | Cornus' Tears | コルヌスの涙 |
| Mystic Frozen | ミスティックフローズン | Great Nature | グレイトネイチャー |
| Flame Heart | フレイムハート | Rough Wind | ラフウィンド |
| Danggie / Daenggie | タンギー | Short Danggie / Daenggie | ショートタンギー |
| Black Hair（染色美容師の会話中の呼称。実アイテムは Long_Hair） | 黒い髪 | Golden Hair | 金色の髪 |
| Glossy Hair | つやのある髪 | | |
| Potato（会話中の呼称。実アイテムは Sweet_Potato） | ジャガイモ | Concentration Potion | 集中力ポーション |
| Awakening Potion | 覚醒ポーション | Berserk Potion | バーサークポーション |
| Yggdrasil Seed | ユグドラシルの種 | Yggdrasilberry | ユグドラシルベリー |
| Royal Jelly | ローヤルゼリー | Sunglasses | サングラス |
| Cap | キャップ | Shoes | 靴 |
| Wooden Mail | ウッドンメイル | Katana | カタナ |
| Slayer | スレイヤー | Broadsword | ブロードソード |
| Flamberge | フランベルジュ | Zephyrus | ゼフィルス |
| Lance | ランス | Bill Guisarme | ビルガイサーム |
| Crescent Scythe | クレセントシザー | | |
| Moth Wing | 蛾の羽 | Grape | ブドウ |
| Cyfar | サイファー | Unripe Apple | 青リンゴ |
| Powder of Butterfly | 蝶の粉 | Honey | 蜂蜜 |
| Banana Juice | バナナジュース | | |
| Sterilized Bandage | 滅菌包帯 | Novice Nametag / Newbie Tag | ノービスネームタグ |
| Horn | 角 | Rainbow Shell | レインボーシェル |
| Snail's Shell | カタツムリの殻 | Blank Scroll | 白紙の巻物 |
| Scorpion Tail | サソリの尻尾 | Payon Solution / Payon Potion | フェイヨン溶液 |
| Morocc Solution / Morocc Potion | モロク溶液 | Stem | 茎 |
| Shoot | 若芽 | Red Bloods | レッドブラッド（jobs/2-1/wizard.txt に合わせる） |
| Green Lives | グリーンライブ | Wind of Verdure | ウィンドオブヴァーデュア |
| Crystal Blues | クリスタルブルー | | |
| Grape Juice | グレープジュース | Crystal Mirror | クリスタルミラー |
| Alcohol | アルコール | Apple | リンゴ |
| Well-Baked Cookies | よく焼けたクッキー | China（会話中の呼称。実アイテムは White_Platter） | お皿 |
| Glass Bead | ガラスビーズ | Solid Shell | 硬い貝殻 |
| Holy Water | 聖水 | Cursed Ruby | 呪われたルビー |
| Pet Food | ペットフード | Harpy's Feather / Harpy Feather（表記ゆれ） | ハーピーの羽根 |
| Yggdrasil Leaf | ユグドラシルの葉 | | |
| Fine Grit | 細かい砂利 | Leather Bag of Infinity | 無限の革袋 |
| Cactus Needle | サボテンの針 | Cobweb / Spiderweb（同一アイテムの表記ゆれ） | クモの巣 |
| Zargon | ザーゴン | Bear's Foot（item948。既存の「Bear's Footskin→熊の足の皮」とは別アイテム） | 熊の足 |
| Spawn | スポーン | Garlet | ガーレット |
| Scell | セル | Candy Cane（item530、内部名 Candy_Striper） | キャンディケイン |

## モンスター名（`db/import/mob_db.yml` の `JapaneseName` で確認済み）

| 英語 | 日本語 | 英語 | 日本語 |
|---|---|---|---|
| Poporing | ポポリン | Ghostring | ゴーストリング |
| Angeling | エンジェリング | Thief Bug | シーフバグ |
| Drops | ドロップス | Golem | ゴーレム |
| Giant Hornet | ジャイアントホーネット | Wolf | ウルフ |
| Pupa | プパ | Orc Warrior | オークウォリアー |
| Orc Hero | オークヒーロー | Orc Lord | オークロード |
| Orc Lady | オークレディ | Orc Skeleton | オークスケルトン |
| Orc Zombie | オークゾンビ | High Orc | ハイオーク |
| Jakk | ジャック | Nightmare | ナイトメア |
| Hunter Fly | ハンターフライ | Pharaoh | ファラオ |
| Doppelganger | ドッペルゲンガー | Osiris | オシリス |
| Golden Thief Bug | ゴールデンシーフバグ | Moonlight Flower | ムーンライトフラワー |
| Maya | マヤー | Maya Purple | マヤーパープル |
| Phreeoni | フリオニ | Dark Lord | ダークロード |
| Owl Baron | アウルバロン | Owl Duke | アウルデューク |
| Dark Illusion | ダークイリュージョン | Abysmal Knight | アビスナイト |
| Chimera | キメラ | Clock | クロック |
| Alarm | アラーム | Clock Tower Manager | クロックタワー管理者 |
| Kobold | コボルド | Goblin | ゴブリン |
| Grand Peco | グランドペコペコ | Lava Golem | 溶岩ゴーレム |
| Geographer | ジオグラファー | False Angel | フォールスエンジェル |
| Goat | ゴート | Lord of the Dead（ジュノーのボス、固有名） | 死の王 |
| Zombie | ゾンビ | Mummy | マミー |
| Ghoul | グール | Khalitzburg | カリッツバーグ |
| Archer Skeleton | アーチャースケルトン | Soldier Skeleton | ソルジャースケルトン |
| Skeleton | スケルトン | Skel Worker | スケルワーカー |
| Wraith | レイス | Munak | ムナク |
| Bongun | ボングン | Evil Druid | イビルドルイド |
| Drake | ドレイク | Skeleton Prisoner | スケルトンプリズナー |
| Zombie Prisoner | ゾンビプリズナー | Wind Ghost | ウィンドゴースト |
| Carat | キャラット | Wanderer | ワンダラー |
| Dokebi | トッケビ | Giearth | ギアース |
| Magnolia | マグノリア | Marionette | マリオネット |
| Whisper | ウィスパー | Baphomet Junior | バフォメットジュニア |
| Sohee | ソヒー | Familiar | ファミリア |
| Mandragora | マンドラゴラ | Flora | フローラ |
| Greatest General | グレイテストジェネラル | Hode | ホーディ |
| Desert Wolf | デザートウルフ | Myst | ミスト |
| Hornet | ホーネット | Thief Bug | シーフバグ |
| Megalodon | メガロドン | | |
| Mystcase | ミストケース | Obeaune | オベイン |
| Smokie | スモーキー | Karakasa | カラカサ |
| Red Plant | レッドプラント | Vocal | ヴォーカル |
| Kapha | カパ | Miyabi Doll | ミヤビドール |
| Goblin Leader | ゴブリンリーダー | Rotar Zairo | ロタールザイロス |
| Horong | ホロン | Stem Worm | ステムワーム |
| Bathory | バトーリ | Argiope | アルジオペ |
| Hammer Goblin | ハンマーゴブリン | Alice（モンスター名） | アリス |
| Kobold Leader | コボルドリーダー | Assaulter | アサルター |
| Nine Tail | ナインテール | Walking Petite | ウォーキングプティ |
| Fur-Seal | ファーシール | Merman | マーマン |
| Ancient Mummy | エンシェントマミー | Enchanted Peach Tree | 精霊の桃の木 |

未収録のもの（一般的なカタカナ表記。例: Queen Bee → クイーンビー）は各ファイルの訳語をそのまま踏襲する。

## スキル名

| 英語 | 日本語 | 英語 | 日本語 |
|---|---|---|---|
| Heal | ヒール | Cure | キュアー |
| Increase AGI | 速度増加 | Decrease AGI | 速度減少 |
| Divine Protection | ディバインプロテクション | Demon Bane | デーモンベイン |
| Angelus | エンジェラス | Signum Crusis | シグナムクルシス |
| Ruwach | ルアフ | Teleport | テレポート |
| Warp Portal | ワープポータル | Pneuma | ニューマ |
| Blessing | ブレッシング | Sanctuary | サンクチュアリ |
| Kyrie Eleison | キリエエレイソン | Bash | バッシュ |
| Magnum Break | マグナムブレイク | Endure（SM_ENDURE） | エンデュア |
| Increase HP Recovery（SM_RECOVERY） | HP回復増加 | Detoxify（TF_DETOXIFY） | デトキシファイ |
| Play Dead | 死んだふり | First Aid | 応急手当 |
| Two-Handed Sword Mastery | 両手剣熟練 | Napalm Beat | ナパームビート |
| Frost Diver | フロストダイバー | Double Strafe | ダブルストレイフ |
| Arrow Shower | アローシャワー | Push Cart | プッシュカート |
| Vending | ベンディング | Envenom | エンヴェノム |
| Close Confine | クローズコンファイン | Back Stab | バックスタブ |
| Arrow Crafting（AC_MAKINGARROW） | 矢作成 | Charge Arrow（AC_CHARGEARROW） | チャージアロー |
| Double Attack | ダブルアタック | Bowling Bash | ボウリングバッシュ |
| Gloria | グロリア | Venom Dust | ベノムダスト |
| SP Recovery | SPリカバリー | Turn Undead | ターンアンデッド |
| Prepare Potion（髪型名としては「調合」） | 調合 | Dragonology | ドラゴノロジー |
| Grand Cross | グランドクロス | Mace Mastery | メイス熟練 |
| Intimidate | イントミデイト | Thunder Storm | サンダーストーム |
| Spiritual Sphere Absorption | スピリットスフィアアブソープション | Encore | アンコール |
| Gypsy's Kiss | ジプシーズキス | Grimtooth | グリムトゥース |
| Counter Attack | カウンターアタック | Blitz Beat | ブリッツビート |
| Anke Snare（Ankle Snare の原文表記ゆれ） | アンクルスネア | Find Ore | ファインドオア |
| Hammer Fall | ハンマーフォール | Fire Pillar | ファイヤーピラー |
| Jupitel Thunder | ジュピテルサンダー | Guillotine Fist | ギロチンフィスト |
| Whirlwind | ワールウィンド | Two Hand Quicken | ツーハンドクイッケン |
| Provoke | プロボック | Brandish Spear | ブランディッシュスピア |
| Pierce | ピアース | Spear Stab | スピアスタブ |
| Spear Boomerang | スピアブーメラン | Peco Peco Ride | ペコペコライディング |
| Cavalier Mastery | 騎乗熟練 | | |
| Hiding | ハイディング | Steal | スティール |
| Improve Dodge | インクリースドッジ | Discount | ディスカウント |
| Haggle | ヘグル | Mug | マグ |
| Slyness | スライネス | Divest Helm | ディベストヘルム |
| Divest Shield | ディベストシールド | Strip Tease | ストリップティーズ |
| Venom Splasher | ベノムスプラッシャー | Back Slide | バックスライド |
| Stalk | ストーク | Sand Attack | サンドアタック |
| Shrink | シュリンク | Fatal Blow | ファタルブロー |
| Moving HP Recovery（会話中の俗称 "Body Movin'" も同一スキルとして統一） | ムービングHP回復 | Auto Berserk（会話中の省略形 "Berserk" も同一スキルとして統一） | オートバーサーク |
| Stun | スタン | | |
| Crazy Uproar | ラウドエクスクラメーション | Change Cart | チェンジカート |
| Cart Revolution | カートレボリューション | Charming Wink | チャーミングウィンク |
| Elemental Change | エレメンタルチェンジ | Elemental Converter Creation | エレメンタルコンバーター作成 |
| Endow Blaze | エンドウブレイズ | Endow Quake | エンドウクエイク |
| Endow Tornado | エンドウトルネード | Endow Tsunami | エンドウツナミ |
| Spiritual Bestowment（MO_KITRANSLATION） | 施しの法 | Excruciating Palm（MO_BALKYOUNG） | 活殺の型 |
| Spirit Sphere（気功玉。付与されるアイテム/リソース名） | 気功玉 | | |
| Sight Blaster（WZ_SIGHTBLASTER） | サイトブラスター | Phantasmic Arrow（HT_PHANTASMIC） | ファランクス |
| Redemptio（PR_REDEMPTIO） | レデムプティオ | Energy Coat（MG_ENERGYCOAT） | エナジーコート |
| Emergency Arrow（quests/skills/hunter_skills.txt のみ、Phantasmic Arrow の仮称ジョーク） | 緊急の矢 | Resurrection（ALL_RESURRECTION、Redemptio の前提スキル） | リザレクション |
| Unfair Trick（BS_UNFAIRLYTRICK。skill_db.yml の Description 名。ファイル冒頭コメントの旧称 "Dubious Salesmanship" は使わない） | アンフェアトリック | Greed（BS_GREED） | グリード |
| Charge Attack（KN_CHARGEATK） | チャージアタック | Back Slide（TF_BACKSLIDING。quests/skills/thief_skills.txt の地の文・select で使用。assassin.txt/rogue.txt のクイズ選択肢では短縮形「バックスライド」を使用済みのため両表記が併存） | バックスライディング |
| Find Stone（TF_PICKSTONE。BS_FINDINGORE「ファインドオア」とは別スキル） | ピックストーン | Stone Fling（TF_THROWSTONE） | ストーンフリング |

## 美容師 NPC の髪型スタイル名（lhz_in02 Prince Shammi 等）

| 英語 | 日本語 | 英語 | 日本語 |
|---|---|---|---|
| Petite Style | プチスタイル | Executioner Style | エグゼキューショナースタイル |
| Prince Style | プリンススタイル | Deviace Style | デヴィアススタイル |
| Spring Rabbit Style | スプリングラビットスタイル | Harpy Style | ハーピースタイル |
| Medusa Style | メデューサスタイル | Isis Style | アイシススタイル |
| Emergency Heal Perm | エマージェンシーヒールパーマ | Aura Blade Cut | オーラブレードカット |
| Power Swing (Cut) | パワースイング（カット） | Renovatio Cut | レノヴァシオカット |
| Assumptio Perm | アシュムプティオパーマ | Soul Changer Cut | ソウルチェンジャーカット |
| X Tornado Cut | エックストルネードカット | Oratio Cut | オラティオカット |

## UI・システム用語

| 英語 | 日本語 | 英語 | 日本語 |
|---|---|---|---|
| Cancel | キャンセル | Yes / No | はい / いいえ |
| Next / Continue | 次へ / 続ける | Close | 閉じる |
| Save | セーブ | Use Storage | 倉庫を利用する |
| Rent a Pushcart | カートをレンタルする | Use Teleport Service | テレポートサービス |
| Check Other Information | その他の情報 | Nothing / Never mind | 何でもない / やめる |
| Quest | クエスト | Reward | 報酬 |
| Experience / EXP | 経験値 | Skill Point / Stat Point | スキルポイント / ステータスポイント |
| HP / SP | HP / SP | Weight / Overweight | 重量 / 重量オーバー |
| Inventory | 所持品 | Equip / Unequip | 装備する / 外す |
| You don't have enough zeny | Zeny が足りません | You don't have enough space | 所持品に空きがありません |
| Level | レベル | Hunting / Kill N monsters | 討伐 / モンスターを N 体倒す |

## NPC 固有名詞の扱い

- 人名はカタカナ表記（例: Leilah レイラ、Mareusis マレウシス、Mahnsoo マンスー、Gever Al Sharp ゲヴァー・アル・シャープ、Jaax ジャックス）。役職名を伴う場合は「役職名 名前」形式（例: Old Pharmacist → 年老いた薬剤師、Inventor Jaax → 発明家ジャックス）。
- 翻訳済みファイルで既に使った表記を優先する（`grep -rn "英語名" app/rathena/overlay-utf8/npc/custom/jp/` で確認）。
- モンスター名は `db/import/mob_db.yml` の `JapaneseName` と揃える（ポリン、ファブル、ルナティック、ピッキ、ウィロー、スポア、ロダフロッグ、コンドル、チョンチョン、クリーミー、ペコペコ …）。未収録のものは一般的なカタカナ表記。
- prontera/izlude/alberta（街 NPC）で追加: Shuger→シュガー、Tono→トノ、Merideth→メリデス、YuPi→ユピ、YuNa→ユナ（原文の表記揺れ YuNA も統一）、Strife→ストライフ、Towngirl Dairenne→町娘ダイレンヌ、Curator Guiss→司書ギス、Library Girl Ellen→図書館の少女エレン、Bartender→バーテンダー、Shevild→シェビルド、TenSue→テンスー、Marvin→マービン、Tailor Ginedin Rephere→仕立て屋ギネディン・レフィア、Garnet→ガーネット、Henson→ヘンソン、King Tristram III→トリスタム3世、Sailor→船員、Bonne→ボンヌ、Charfri→チャーフリ、Cuskoal→カスコール、Dega→デガ、Kylick→カイリック、Red→レッド、Cebalis→セバリス、Aaron→アーロン、Fabian→ファビアン、Steiner→スタイナー、Chad→チャド、Deagle→ディーグル、Shakir→シャキール、Sonya→ソーニャ、Grandmother Alma→アルマおばあさん、Fisk→フィスク、Paul→ポール、Phelix→フェリックス。役職のみ（`::` の無いヘッダ）: Old Man→老人、Soldier→兵士。
- pre-re/jobs/novice/novice.txt（初心者修練場）で追加: Shion→シオン、Kris→クリス、Cecil→セシル、Alice→アリス、Edwin→エドウィン、Jare Riotte→ジェア・リオット、Leo Handerson→レオ・ハンダーソン、Elmeen→エルミーン、Muriel→ミュリエル、Hoffman→ホフマン、Keyman→キーマン、Hanson→ハンソン、Bruce→ブルース。役職のみ（`::` の無いヘッダ、または `::` があっても表示名は既存踏襲でヘッダ非改変とした）: Training Grounds Guard→修練場の衛兵、Training Grounds Receptionist→修練場の受付、Guide Soldier→案内兵士。
- cities/comodo.txt で追加（すべて `::` 無しヘッダにつき表示名は英語のまま、話者タグのみ日本語化）: Martine→マーティン、Scoursege→スコーセージ、Roberto→ロベルト、Deniroz→デニロズ、Shalone→シャローン、Stonae→ストネイ、Loyar→ロヤール、Moo→ムー、Zyosegirl→ジョセガール、Ziyaol→ジヤオル、Daeguro→デグロ、Rahasu→ラハス、Hallosu→ハロス、Zain→ザイン（duplicate の Sarumane は strnpcinfo(1) 参照のため無改変）、Serutero→セルテロ。カプラ職員（個人名あり）: Kafra Misty→カプラ職員ミスティ（ヘッダは他の Kafra Employee 同様「カプラ職員」に統一、話者タグのみ個人名を付与）。
- cities/yuno.txt で追加（`::` 無しヘッダにつき表示名は英語のまま）: Freidrich→フリードリヒ、Sergiof→セルジオフ、Ninno→ニンノ、Le Morpheus→ル・モルフェウス。役職のみ: Granny→おばあさん、Artisan→職人、Juno Soldier（::JunoSoldier1～7、表示名は空文字のため無改変）→ジュノーの兵士、Airship Representative（原文に "Air ship Representative" の表記揺れあり、話者タグは統一）→飛行船案内係。
- merchants/hair_dyer.txt・pre-re/merchants/hair_dyer.txt・merchants/dye_maker.txt で追加（`::` 無しヘッダにつき表示名は英語のまま）: Jovovich→美容師ジョヴォヴィッチ、Rossa（Hair Dyer#lich）→美容師ロッサ、Java Dullihan→染料職人ジャバ・ドゥリハン（原文に `[Dye Maker Java Dullian]` の表記揺れ1箇所あり、話者タグは統一）。
- merchants/milk_trader.txt・merchants/gemstone.txt で追加（`::` 無しヘッダにつき表示名は英語のまま）: Milk Vendor→牛乳商人、Jade（Jade#pay）→宝石商ジェイド。
- cities/payon.txt（フェイヨン・アーチャー村）で追加: Monster Scholar Vuicokk→怪物学者ヴイコック、Archer Zakk→アーチャー・ザック、Archer Wolt→アーチャー・ウォルト（原文の表記揺れ `[Arche Wolt]` は同一人物として統一）、Archer Joe→アーチャー・ジョー。役職のみ（`::` の無いヘッダ）: Lady→婦人、Young Man→青年、Guardsman→衛兵、Woman→女性、Woman#2payon（話者タグは Jim's Mother）→ジムの母、Drunkard→酔っ払い、Waitress（話者タグは Pub Lady）→酒場の女性、Chief Guardsman→衛兵長、Chief（Payon の族長）→族長、Guard→衛兵。
- pre-re/guides/（アマツ/アユタヤ/崑崙/フィゲル/龍之城/モスコビア/ニブルヘイム/ラヘル/ウンバラ/ベインスの案内 NPC 10 本）で追加: Amachang→アマちゃん、Noi→ノイ、He Yuen Zhe→ホー・ユエンジェ、Ricael→リカエル。建物・種族などの固有名詞: Cheshrumnir（ラヘルの聖地）→シェシュルムニル、Utan（ウンバラの種族名）→ウータン。役職のみ（`::` の無いヘッダ）: Guide Man（アマツ）→案内人、Hugel Guide Granny→フィゲル案内係ばあさん、Adventurer（ウンバラ）→冒険者、Roaming Man（ニブルヘイムの話者タグは Ricael）→リカエル。`::` ありでヘッダ表示名を変更: Soldier#BA::LouGuide（龍之城、話者タグは衛兵）→衛兵#BA::LouGuide、Veins Guide#1::ve_guide→ベインス案内係#1::ve_guide。龍之城の Representative（`::` 無し）は話者タグを「使者」に翻訳（ヘッダ名は不変）。なお louyang.txt 205 行目は上流で `mes "[Representative]"` NPC 内に `mes "[Soldier]"` が紛れ込む原文側のコピペミスがあり、翻訳では当該 NPC 内の話者タグ統一を優先して「使者」に補正した（挙動・行数は不変）。
- merchants/advanced_refiner.txt で追加（`::` 無しヘッダにつき表示名は英語のまま）: Suhnbi（韓国語「선비」＝士人・学者を意味する固有名詞）→スンビ。refine.txt の精錬師 NPC 群（クリストファー・ギレンロウ、ポール・スパナー等）と同じ武具鍛冶師の口調（「～だ」「～だぞ」調）に揃えた。
- merchants/elemental_trader.txt で追加（`::` 無しヘッダにつき表示名は英語のまま）: Laspuchin Gregory→ラスプチン・グレゴリー（怪しげな錬金術師、独特の高笑い「Kehehe」系は「ケヘヘヘッ」「ケケケケケ」に統一）。
- merchants/enchan_arm.txt で追加（`::` 無しヘッダにつき表示名は英語のまま）: Apprentice Craftsman（役職のみ）→見習い職人。
- merchants/hair_style.txt・pre-re/merchants/hair_style.txt で追加（`::` 無しヘッダにつき表示名は英語のまま）: Rui Vishop（Roving Hair Dresser、尊大な美容師）→ルイ・ヴィショップ、Veronica（pre-re の alberta_in 美容師）→ヴェロニカ、Prince Shammi（lhz_in02 の美容師）→シャミー王子（Prince Shammi の口調は「～だよ」「～なんだ」調、Veronica は「～わ」「～ね」調、Rui Vishop は「～のだ」「～ぞ」調で統一）。役職のみ: Assistant Beautician（lhz_in02）→見習い美容師。
- cities/aldebaran.txt で追加（`::` 無しヘッダにつき表示名は英語のまま。すべて話者タグのみ日本語化）: Munster→マンスター、Quatro→クアトロ、Miller→ミラー、Joanne→ジョアン、Panama→パナマ、Isenberg→アイゼンバーグ、Epthiel→エプシエル（原文の表記揺れ `[Epithiel]` を1箇所含め統一）、Joy→ジョイ、Chemirre→ケミレ、Bebe（少年の名。ペットの Savage の愛称も同じ Bebe、ペット名 NukNuk→ヌクヌク）→ベベ、Stromme→ストロム、Sylvia→シルビア、Issei→イッセイ、Joo Jahk→ジュージャック、Gavin→ギャビン、Nastasia→ナスタシア、RS125（ロボット NPC、識別名のためそのまま）。役職のみ: Bell Keeper→鐘の番人、Threatening-Looking Man→強面の男、Friendly-Looking Man→気さくな男、Fussy Man→気難しい男、Master（カプラガールクイズ担当）→マスター、Gatekeeper Boy（時計塔、function F_ClockTowerGate 内）→門番の少年。カプラ職員（個人名あり、話者タグは「カプラの＋名前」形式で kafras.txt の Leilah→レイラ に揃えた）: Kafra Pavianne→カプラのパヴィアンヌ、Kafra Blossom→カプラのブロッサム（merchant.txt のブロッサム表記と一致）、Kafra Jasmine→カプラのジャスミン、Kafra Roxie→カプラのロキシー、Kafra Curly Sue→カプラのカーリー・スー。F_ClockTowerGate 内の固有名詞: Bruke Seimer→ブルーク・セイメル、Philip Warisez→フィリップ・ワリセズ、Romero Specialre→ロメロ・スペシアルレ、Kinase - Blue Gallino（アルデバランの名物）→キナセ・ブルーガリーノ。なお同関数の `.@floor$` 引数（"4th"/"B4th"）は表示用フレーバーテキストであり識別子ではないため「4階」「地下4階」に翻訳した（`c_tower4`/`alde_dun04` 等のマップ名は無改変）。
- pre-re/quests/quests_morocc.txt（「王子の継承」クエスト）で追加。ヘッダはすべて `::` 無し（`#suffix` 形式の内部識別子のみ）のため表示名は英語のまま不変とし、話者タグのみ日本語化した。クエスト役職: Messenger→使者、Inspector→査察官、adventurer appraiser / judge（プレイヤーの役職名）→冒険者鑑定士 / 鑑定士（呼びかけは「鑑定士殿」）。候補者本人（話者タグは `[Prince]` のみで正体を伏せる導入部があり、こちらは意図的に無名のまま「王子」と訳した）: Eigen Ahrum（Walter 家）→アイゲン・アルム、短縮形 Ahrum→アルム、Ernst（Gaebolg/Geoborg 家、原文表記ゆれあり）→エルンスト、短縮形 Ern→エルン、Erich（Nerius/Nerious 家、原文表記ゆれあり）→エーリッヒ、Urugen/Urgen（Wigner 家、原文表記ゆれあり）→ウルゲン、Helmut（Roewenburg）→ヘルムート、Poe（Richard/Riehart 家、原文表記ゆれあり）→ポー、Peter（Heine 家）→ピーター。従者・その他人物: Hans（Erich の従者）→ハンス、Calbern（Helmut の従者）→カルベルン、Girl#prince（アルデバランの少女）→少女、Guard#princein（話者タグ `[Guard of a strange place]`）→見知らぬ場所の衛兵。家名は原文の表記ゆれ（Richard/Riehart、Gaebolg/Geoborg 等）をすべて統一して翻訳: Walter→ウォルター家、Richard/Riehart→リチャード家、Gaebolg/Geoborg→ゲーボルグ家、Nerius/Nerious→ネリウス家、Heine→ハイネ家、Wigner→ヴィグナー家、Roewenburg→ロエヴェンブルク、祖先 Schmidt→シュミット、Heinrich→ハインリッヒ。`#twonoble` 内の陰謀を語る二人（`::` 無しヘッダで表示名は別に存在するが、この共有スクリプト内の話者タグ `[A man of Walter Family]` `[A man of Riehart Family]` `[Aged Noble]`（原文の表記ゆれ、同一人物）は誰の発言か特定できるよう「ウォルター家の男」「リチャード家の男」に統一）。単体 NPC の話者タグ: Young Noble#valter（`[Young Noble Walter]`、1 回のみ）→ウォルター家の若様、Aged Noble#rihart（`[Aged Noble Richard]`、1 回のみ）→リチャード家の老貴族。アイテム名（会話中の直接表記のみ翻訳、getitemname() 経由は対象外）: Reins（Abysmal Knight ドロップ）→手綱、Bazerald（形見の短剣）→バゼラルド。Knights of Abyss（モンスター名、会話文中）→アビスナイト。Daddy-Long-Legs（少女の台詞に出る物語名、実在小説）→「あしながおじさん」。
- cities/geffen.txt で追加（`::` 無しヘッダにつき表示名は英語のまま、話者タグのみ日本語化）: Meera→ミーラ、Orwalk→オルワルク、Ralphie→ラルフィー、Stacey→ステイシー、Theodore→シオドア、Crumpler→クランプラー、Skyler→スカイラー、Elenore（Waitress#elen）→エレノア、Elisa（Waitress#elise）→エリサ、Hans Hadenheim（原文の表記ゆれ `[Hans Handenheim]` を1箇所含め統一）→ハンス・ハーデンハイム、Estheres（Monster Scholar）→エステレス。役職のみ（個人名の明かされないもの）: Wizard Stanza（話者タグ `[Stanza]`）→スタンザ、Suspicious Guy→怪しい男（導入部の話者タグ `[?]` は未訳のまま維持）、Merchant Daven→商人ダヴェン、Psychic Advisor→占い師、Citizen→町の住人、William's Spirit（酒場の女性たちに憑依する亡き父の霊）→ウィリアムの霊。
- jobs/2-2/monk.txt（聖カピトーリナ修道院・モンク転職クエスト）で追加（すべて `::` 無しヘッダにつき表示名は英語のまま、話者タグのみ日本語化）: Tohobu（門番モンク）→トホブ、Sensei Moohae→ムーヘ先生（本文中の「sensei Moohae」も同様）、Touha→トウハ（本文中「elder Touha」は「長老トウハ」）、Boohae→ブーヘ、Keeper Chorip（Door Keeper）→門番チョリプ、Bashu→バシュ、Monk Apprentice→見習いモンク、Supervisor（マラソン監視役）→監督官、Hyunmoo→ヒョンム、Tomoon→トムーン、Proctor（試練の間の受付、3体とも同一話者タグ）→試験官。モンスター表示名（`monster` コマンドの表示名引数、マップ名は無改変）: Zombie→ゾンビ、Mummy→ミイラ。ラテン語の典礼句 `In nomine Patris, et Filii, et Spiritus Sancti.`（父と子と聖霊の御名において）および `veritas and aequitas`（真実と正義）は英語ではなくラテン語の引用のため翻訳せず原文のまま残した（jRO公式訳の転載ではなく、原文自体が非英語のラテン語であるため）。Sensei Moohae の台詞中で `veritas and aequitas? ^CCCCCC(Truth and Justice)^000000` のように英語の説明が併記される箇所は、その英語部分のみ「(真実と正義)」と翻訳し、ラテン語本体は残した。
- jobs/2-2/alchemist.txt（アルデバラン・錬金術師ギルド、アルケミスト転職クエスト）で追加（すべて `::` 無しヘッダにつき表示名は英語のまま、話者タグのみ日本語化）: Parmy Gianino（受付、Alchemist Guildsman#am）→パーミー・ジャニーノ、Raspuchin Gregory（Fastidious Alchemist#am）→ラスプチン・グレゴリー（merchants/elemental_trader.txt の Laspuchin Gregory と綴り違いだが同一キャラクター、同じ sprite 749・同じ「Heeheehee keheheh~!」の高笑いのため表記・口調を統一。「ヒッヒッヒ／ケヘヘヘッ～！」で統一し、口調は「～だ」「～ぞ」調の乱暴な同業者口調）、Darwin（Studying Man#am）→ダーウィン、Van Helmont（Experiment Expert#am）→ヴァン・ヘルモント、Vincent Carsciallo（Master Alchemist#am、組合長）→ヴィンセント・カルシャロ、Nicholas Flamel（Chief Researcher#am）→ニコラス・フラメル。本文中でのみ言及される人物名: Harmona（ダーウィンが探し続ける失われた恋人）→ハルモナ、Molgenstein（中和剤・混合剤の作り方を教える人物、本人は未登場）→モルゲンシュタイン、Bain and Bajin（ジュノーでアルケミスト研究をする双子）→バインとバジン。アイテム名（`getitemname()` を経由せず会話文中に直接書かれる箇所のみ翻訳）: Old Magic Book→古い魔法の本、Hammer of Blacksmith→鍛冶屋のハンマー、Illusion Flower→幻の花（"Moonlight Flower" と呼ばれる場面はモンスター名の慣用表記に揃えて「ムーンライトフラワー」）、Mini Furnace→ミニ溶鉱炉、Burnt Tree→焦げた木、Fine Sand→細かい砂。ラスプチンの筆記試験（算数の文章題）中の装備品名は日本語化（例: Scimiter→シミター、Helm→ヘルム、Ring Pommel Saber→リングポンメルセイバー、Sakkat→サッカト、Mr. Smile→ミスタースマイル、Padded Armor→パッドアーマー等）。英語のまま意図的に残した箇所: (1) ニコラス・フラメルの隠し単語パズル（`mes "t m y a n y e o b n e g p r i"` 等の文字の羅列と、その直後の `select("Brake:Brass:Bug:Broken:Brigan?")` 等の選択肢）はアナグラムそのものが英字に依存する言語依存パズルのため全て英語のまま。(2) ダーウィンの催眠演出（710行超にわたり "Lorem ipsum dolor sit amet..." を段階的に長くして繰り返す箇所）とニコラス・フラメルの支離滅裂な独り言（"Lorem ipsum..." "Suspendisse..." で `^666666*Mumble Mumble*^000000` に落ちる箇所）は、原文が実在の文章ではなく意図的なダミーのラテン語プレースホルダー（催眠・独り言の演出）であり、翻訳すると存在しない意味を捏造することになるため原文のまま残した。(3) ヴァン・ヘルモントの筆記試験の選択肢 `select("Karvodailnirol:Detrimindexta:Alcohol")`（2箇所）は、Karvodailnirol・Detrimindexta が本作オリジナルの架空アイテム名で他ファイルに訳語の前例が無く、無理に当てるとアイテム名として一致しなくなるため3つとも英語のまま統一。
- jobs/2-1/priest.txt（プロンテラ聖堂・プリースト転職クエスト）で追加（すべて `::` 無し、または `::` 有りでも `#suffix` 部分のみのヘッダにつき表示名は英語のまま、話者タグのみ日本語化）: Bishop Paul（Paul Cervantes、High Bishop#prst）→司教ポール、Sister Cecilia→シスター・セシリア（Cecilia Margarita）、Peter S. Alberto（Father Peter）→ピーター神父。既存の Father Rubalkabara→ルバルカバラ神父、Mother/Sister Mathilda→マザー・マチルダ、Father Yosuke→ヨウスケ神父（jobs/1-1/acolyte.txt で確立済み）はそのまま踏襲。誘惑イベントの4体（すべて mob_db.yml の JapaneseName に一致）: Deviruchi#prst→デビルチ、Doppelganger#prst→ドッペルゲンガー（既存踏襲）、Dark Lord#prst→ダークロード（既存踏襲）、Baphomet#prst→バフォメット。`monster` コマンドの表示名引数（Theft/Want of Virtue/Jealousy 等の「七つの大罪」ゾンビ、Khamoz 等のミイラ）は識別子ではなく翻訳ルール上の許可リストにも無いため、英語のまま無改変とした。
- jobs/2-1/wizard.txt（ゲフェンタワー・ウィザード転職クエスト）で追加（すべて `::` 無しヘッダにつき表示名は英語のまま、話者タグのみ日本語化）: Catherine（Catherine Medici、Wizard Guildsman）→キャサリン（役職のみの話者タグ `[Wizard Guildsman]` は「ウィザードギルド職員」）、Raulel Asparagus（Gloomy Wizard）→ラウレル、Maria（White Dog#wiz、Maria Splodofska）→マリア（役職のみの話者タグ `[Dog]` は「犬」、`[Dog called 'Maria']` は「「マリア」と呼ばれる犬」、`[Dog... 'Maria'...]` は「犬…「マリア」…」）、Arena Assistant→試験会場アシスタント。quiz の select 選択肢に出るスキル名・モンスター名・カード名は既存踏襲および `db/import/mob_db.yml` の JapaneseName に準拠（Napalm Beat→ナパームビート、Frost Diver→フロストダイバー等は既存踏襲、Thief Bug→シーフバグ、Pupa→プパ、Poporing→ポポリン、Ghostring→ゴーストリング、Chonchon→チョンチョン、Mantis→マンティス、Cornutus→コルヌス、Yoyo→ヨーヨー、Hydra→ヒドラ、Mandragora→マンドラゴラ等は mob_db 確認済み）。`monster` コマンドの表示名引数（Obeaune 等の実モンスター名）は同様に翻訳ルールの許可リストに無いため英語のまま無改変とした。
- jobs/valkyrie.txt（転生のバルキリー、ヴァルハラ）で追加（すべて `::` 無しヘッダにつき表示名は英語のまま、話者タグのみ日本語化）: Valkyrie→バルキリー、Metheus Sylphe→メテウス・シルフェ、The Book of Ymir / Book of Ymir→イミルの書（Ymir は既存の「イミルの心の欠片」に揃えて「イミル」）、Teleporter（役職のみ）→テレポーター。転生演出中に語られる女神名: Urd→ウルド、Verdandi→ヴェルダンディ、Skuld→スクルド。Heart of Ymir（`::` 無しヘッダ、台詞なし）は無改変。
- jobs/2-1/blacksmith.txt（アインブロック・ブラックスミス転職クエスト、筆記試験あり）で追加（すべて `::` 無しヘッダにつき表示名は英語のまま、話者タグのみ日本語化）: Altiregen（Guildsman#BLS）→アルティレゲン、Geschupenschte（Guildsman#alberta、アインベフのブラックスミス）→ゲシュペンシュテ、Baisulist（ゲフェン）→バイスリスト、Wickebine（モロク）→ウィッケバイン、Krongast（リヒタルゼン）→クロンガスト、Talpiz（フェイヨン）→タルピズ、Bismarc（フィゲル）→ビスマーク、Mitehmaeeuh（Blacksmith Guildsman#moc）→ミーテマイユ。役職のみ: Blacksmith Guildsman#gef→ブラックスミスギルド職員（用語集「施設・役職・組織」に追加）。筆記試験の select 選択肢に出る武器・防具・モンスター名は既存踏襲および一般的なカタカナ表記（Two Hand Axe→ツーハンドアクス、Swordmace→ソードメイス、Ring Pommel Saber→リングポメルセイバー、Wooden Mail→ウッドンメイル、Main Gauche→メインゴーシュ、Claymore→クレイモア、Zerom→ゼロム、Chon Chon→チョンチョン、Anolian→アノリアン、Skel Worker→スケルワーカー、Requiem→レクイエム等）。武具の色コード付き刻印テキスト（"Super Arc Wand of Geschupenschte Mark 2" 等）は各アイテムごとに独自の日本語表現に意訳した。
- jobs/2-1/knight.txt（プロンテラ騎士団・ナイト転職クエスト、7人の騎士による試験）で追加（すべて `::` 無しヘッダにつき表示名は英語のまま、話者タグのみ日本語化）: Chivalry Captain（Captain Herman、Herman Phon Efesirsus）→騎士団長ハーマン、Sir Andrew（Andrew Shylock）→アンドリュー卿、Sir Siracuse（James Siracuse）→シラキュース卿、Sir Windsor（Windsor Benedict）→ウィンザー卿（寡黙な性格で台詞のほとんどが「…」のため、他の騎士より短い間投詞中心の文体で統一）、Lady Amy（Amy Beatrice）→レディ・エイミー（「～わ」「～ね」「～かしら」調の女性的な口調で統一）、Sir Edmond（Edmond Groster）→エドモンド卿（禅問答めいた達観した比喩表現の文体で統一）、Sir Gray（Gray Prospheiro）→グレイ卿（クレイモアを作る鍛冶師も兼ねる、面倒見の良い年長者口調）。クイズの select 選択肢に出る武器・槍・スキル名（用語集の各表に反映済み）: Katana→カタナ、Slayer→スレイヤー、Broadsword→ブロードソード、Flamberge→フランベルジュ、Zephyrus→ゼフィルス、Lance→ランス、Bill Guisarme→ビルガイサーム、Crescent Scythe→クレセントシザー、Two Hand Quicken→ツーハンドクイッケン、Provoke→プロボック、Brandish Spear→ブランディッシュスピア、Pierce→ピアース、Spear Stab→スピアスタブ、Spear Boomerang→スピアブーメラン、Peco Peco Ride→ペコペコライディング、Cavalier Mastery→騎乗熟練。既存踏襲: Claymore→クレイモア（jobs/2-1/blacksmith.txt で確立済み）。
- jobs/2-2/sage.txt（ジュノー・シュバイヒルビル魔法学院、セージ転職クエスト。筆記試験60問＋論文執筆パートあり）で追加（すべて `::` 無しヘッダにつき表示名は英語のまま、話者タグのみ日本語化）: Kayron Grik（学院長、Dean of the Academy#sa）→カイロン・グリック（硬め・尊大な「～だ」「～だぞ」調）、Metheus Sylphe（受付、Staff of the Academy#a）→メテウス・シルフェ（jobs/valkyrie.txt で確立済みの表記に統一。丁寧な「です・ます」調）、Claytos Verdo（筆記試験担当、Written Test Professor#s）→クレイトス・ヴェルド（辛口・高圧的な「～だ」「～たまえ」調）、Hermes Tris（実技試験担当、Practical Examination P）→ヘルメス・トリス（体育会系で気さくな「～だ」「～だぞ」調）、Saphien Layless（歴史学担当、History Professor#sa）→サフィエン・レイレス（厳格な老教授口調「～だ」「～のだ」）、Lucius Celsus（生物学担当、Biology Professor#sa）→ルシウス・ケルスス（短気で毒舌な「～だ」「～だろうが」調）、Aebecee George（物理学担当、Physics Professor#sa）→エイビーシー・ジョージ（コケティッシュなオネエ系口調「～わ」「～かしら」、口癖 tee hee~→うふふ～で統一）。世界観・神話用語（今後の Sage/Valkyrie 系ファイルでも流用想定）: Yggdrasil→ユグドラシル、Asgard→アスガルド、Midgard→ミッドガルド、Utgard→ウトガルド、Jotunnheim→ヨトゥンヘイム、Niflheim→ニブルヘイム（既存の都市名表記に統一）、Yormungandr→ヨルムンガンド、Ymir→イミル（jobs/valkyrie.txt の「イミルの書」に揃えて統一）、Tritonia（誤答選択肢のみの架空の人魚の国）→トリトニア。アイテム名（`getitemname()` を経由せず会話文中に直接書かれる箇所のみ翻訳、入学金免除アイテム2点）: Old Magicbook（item 1006、内部名 Old_Magic_Book）→古い魔法の本（jobs/2-2/alchemist.txt の表記に統一）、Necklace of Wisdom（item 1007、内部名 Penetration）→英知の首飾り（新規）。`monster` コマンドの表示名引数（Arena#1 の "Grade F"/"Grade D"、Arena#2 の学問名24体、Arena#Doorkeeper の "Academic Probation"、Arena#3 の "Absent 3 times" 等）は識別子ではなく翻訳ルール上の許可リストにも無いため、jobs/2-1/priest.txt・jobs/2-1/wizard.txt の前例に倣い英語のまま無改変とした。`waitingroom` のタイトル引数 "Waiting Room" も、既存の他ジョブ（jobs/2-1/knight.txt・jobs/2-1/wizard.txt・jobs/2-2/dancer.txt 等）が軒並み英語のまま残している前例に倣い無改変とした。筆記試験60問（3パターン×20問）の select 選択肢に出る都市名・モンスター名・アイテム名・スキル名は既存踏襲および `db/import/mob_db.yml` の JapaneseName に準拠。
- jobs/2-2/bard.txt（コモド・バード転職クエスト、歌詞穴埋めクイズあり）で追加（ヘッダ `Wandering Bard` は `::` 無しにつき表示名は英語のまま、話者タグのみ日本語化）: Wandering Bard（話者タグ）→ラロ（本文中の呼称 Lalo に統一）。伝承歌に登場する固有名詞（原文自体が架空の人物名で jRO 公式訳の転載ではないため独自にカタカナ化）: Jichfreid→イヒフレイド、Jichmunt→イヒムント、Papner→パプナー、Eden（女神）→イーデン、Odin→オーディン、Bragi→ブラギ。実在人物への言及: Tchaikovsky→チャイコフスキー。イベント名 Jack Frost（ルティエの雪だるま、他ファイル春馬）→ジャック・フロスト。花アイテム（会話文中に直接書かれる箇所のみ翻訳、getitemname() 経由は対象外）: Singing Flower→歌う花、Hinalle（原文表記ゆれ Hinelle）→ヒナル、Aloe→アロエ、Ment→メント、Izidor→イジドール、Witherless Rose→枯れないバラ、Frozen Rose→凍ったバラ、Illusion Flower→幻の花、Bouquet→花束、Wedding Bouquet→ウェディングブーケ、Fancy Flower→ファンシーフラワー。歌詞穴埋めクイズ（`input` した文字列を `if (.@Song$ != "…")` で照合する形式。色コード ^3377FF/^000000 は「これまで歌われた行」の累積ハイライトのため、選択肢のような `:` 個数の制約は無いが、mes 表示側と if 比較側の訳を完全一致させる必要がある）は4種の伝承歌＋1種（デフォルト）をすべて独自の日本語詩に翻訳した。
- jobs/2-2/rogue.txt（パロス灯台・ローグギルド転職クエスト、Markie の筆記試験30問×3セット＋合言葉パズル3種あり）で追加（すべて `::` 無しヘッダにつき表示名は英語のまま、話者タグのみ日本語化）: Thug（moc_ruins、話者タグ）→ならず者、Markie（Rogue Guildsman#rg）→マーキー（役職のみで名前が明かされる前の話者タグは「ローグギルドの男」）、Mr. Smith（Mr. Smith#rg）→スミス、Aragham Junior（Aragham Junior#rg）→アラガム・ジュニア、Antonio Junior（Antonio junior#rg）→アントニオ・ジュニア、Hollgrehenn Junior（Hollgrehenn junior#rg）→ホルグレヘン・ジュニア、Hermanthorn Jr.（Hermanthorn Jr#rg、原文の表記ゆれ "HermanthornJr."）→ハーマンソーン・ジュニア。3つの合言葉パズル（Warp#1/#2/#3、扉の前で単語を4択で選び文を完成させる）は「アラガムは精錬したアイテムを一度も独り占めしなかった」「俺の父は精錬したアイテムを一度も独り占めしなかった」「アントニオは精錬したアイテムを壊すことを楽しんでいない」の3文に対応するよう、選択肢の各単語を独自に日本語化した（正解の組み合わせ・個数は上流のまま）。Markie の筆記試験に出るスキル名・アイテム名・地名は本用語集の各表に準拠（新規追加分はスキル名表・モンスター名表を参照）。S_Req/S_CheckItems ラベル内の申込アイテム名（Skel-bone→スケルボーン、Decayed Nail→腐った爪、Horrendous Mouth→恐ろしい口、Crab Shell→カニの甲羅、Snake Scale→蛇の鱗、Garlet→ガーレット、Grasshopper's Leg→バッタの足、Bear's Footskin→熊の足の皮）も新規。Mr. Smith の逆上イベント中の伏字表現（"F$@king" 等）は意味を保った日本語の伏字・罵倒表現に独自に意訳し、書式指定子として検出される `%k` を含む1箇所（555/556行目）は同数の `%k` を翻訳文にも残した。`monster` コマンドの表示名引数（Zombie/Mummy 等の実モンスター名）は jobs/1-1/thief.txt の前例（`job_thief1,0,0 monster Orange Mushroom ...` を英語のまま残した既存踏襲）に倣い英語のまま無改変とした。
- jobs/2-2/crusader.txt（プロンテラ王宮・教会・城のクルセイダー転職クエスト、Gabriel Valentine の筆記試験30問×3セットあり。Pre-RE 版 `npc/pre-re/jobs/2-2/crusader.txt` がこのファイルの3体を `duplicate()` するため、ヘッダの NPC 名は無改変のまま維持）で追加（すべて `::` 無しヘッダにつき表示名は英語のまま、話者タグのみ日本語化。文体は「～のだ」「～ぞ」「～であろう」調の硬めの騎士口調で統一、jobs/1-1/swordman.txt の文体を踏襲）: Michael Halig（`- script Senior Crusader_`）→マイケル・ヘイリグ、Murnak Mijoul（`- script Man in Anguish_`、Michael Halig の台詞中では表記ゆれ "Moorenak Miyol" だが同一人物のため訳語を統一）→ムーレナク・ミヨル、Gabriel Valentine（`prt_church script Crusader`）→ガブリエル・ヴァレンタイン、Bliant Piyord（`- script Patron Knight_` および `Patron Knight#2`、`Zombie Guide`）→ブリアント・ピヨード。試練会場の Summoner#cr1～4・Monster Summon#cr0～6・Waiting Room#cr1 は台詞なし（`monster` コマンドの表示名引数のみ）につき無改変。Gabriel Valentine の筆記試験に出るスキル名・モンスター名・カード名・武器名は本用語集の各表に準拠し、Zephyrus→ゼフィルス／Bill Guisarme→ビルガイサーム／Crescent Scythe→クレセントシザー／Cavalier Mastery→騎乗熟練／Main-Gauche→メインゴーシュ は jobs/2-1/knight.txt・jobs/2-1/blacksmith.txt の既存訳語に統一した（新規追加分はスキル名表・モンスター名表を参照）。
- jobs/2-2/dancer.txt（コモド・ダンサー転職クエスト、ビジューの雑学クイズ10問×3セットあり）で追加（すべて `::` 無しヘッダにつき表示名は英語のまま、話者タグのみ日本語化）: Athena Sonotora（Sonotora#1）→アテナ・ソノトラ、Bor Robin（Bor Robin#1）→ボー・ロビン、Aile（Aile#da）→エイル、Bijou（Bijou#da）→ビジュー、Pyorgin（Waiting Room#click の話者タグ）→ピョルジン。雑学クイズの固有名詞（原文が架空の人物名のため独自にカタカナ化。実在の人物名は標準的な日本語表記）: Bonjour→ボンジュール、Mercy Bokou→マーシー・ボク、Guton Tak→グトン・タク、Borjuis→ボルジュイ、Bourgeois→ブルジョワ、Yoo→ユー、Hoon→フン、Roul→ロウル、Ryu→リュウ（カジノ支配人 Moo は既存の cities/comodo.txt の表記→ムー を踏襲）、Art Blakey→アート・ブレイキー、Billie Holiday→ビリー・ホリデイ、Louis Armstrong→ルイ・アームストロング、Bud Powell→バド・パウエル、Elder Willow→エルダーウィロー。スキル名（クイズの設問のみ、既存踏襲の Improve Concentration→集中力向上、Arrow Shower→アローシャワー 以外は新規）: Lady Luck→レディ・ラック、Mental Sensing→メンタルセンシング、Dance Lessons→ダンスレッスン、Lullaby→ララバイ。アイテム名（会話文中に直接書かれる箇所のみ翻訳）: Sticky Mucus（既存踏襲）→ネバネバした液体、Earthworm Peelings（既存の Worm Peeling→ミミズの皮 に統一）、Black Hairs（既存踏襲）→黒い髪、Clam Shell→貝殻、Boots→ブーツ、Sandals→サンダル、Kitty Band→キティバンド、Shining Stone→輝く石、Crab Shell→カニの甲羅。設問8「コモドにあるカプラの正式名称は？」は原文 `select("Kafra Headquarters:Kafra West Headquarters:Kafra Service:Kafra Headquarters: Western Branch")` の4番目の選択肢内に `:` が紛れ込み実質5択（`==4` の正解は4番目の "Kafra Headquarters" 断片）になっている上流側のバグを、`:` の個数を保ったまま同じ構造で「カプラ本店:カプラ西本店:カプラサービス:カプラ本店: 西支店」に翻訳し再現した。`waitingroom "Waiting Room",...` のチャットルーム名は、対応する NPC ヘッダ `Waiting Room#dance` 自体が `::` 無しのため表示名を英語のまま残しているのに合わせ、英語のまま意図的に残した（迷った場合の保守的判断）。

- jobs/2-1/assassin.txt（モロク・アサシンギルド転職クエスト、筆記試験30問×3セットあり）で追加（すべて `::` 無しヘッダにつき表示名は英語のまま、話者タグのみ日本語化）: Guildsman#asn（`[Ferocious-looking guy]`→凶暴そうな男、正体判明後の `[Assassin Expert 'Huey']`→熟練アサシン・ヒューイ）、Guildsman#ASN2（`[Assassin 'Khai']`→アサシン・カイ）、nameless_one（`[The Anonymous One]`→名もなき者）、Test Guide#ASN・Barcardi#ASN（`[Barcardi]`→バーカディ）、Thomas#ASNTEST（`[Thomas]`→トーマス）、Guildmaster#ASN1・Guildmaster#ASN2（`[Guildmaster]`→ギルドマスター）、`[Beholder]`（パネルシーンの話者タグのみ）→ビホルダー、Master Assist（`[Assistent Gayle Maroubitz]`、原文タイプミス "Assistent" のまま）→助手ゲイル・マルビッツ。duplicate() の識別子 `[Huey]`/`[Khai]`/`[The Anonymous One]`/`[Barcardi]`/`[Beholder]`/`[Thomas]`/`[Gayle Maroubitz]`（enablenpc/disablenpc の第1引数）は識別子のため無改変。アイテム名（`getitemname()` を経由せず会話文中に直接書かれる箇所のみ翻訳）: Necklace of Oblivion（item 1008、内部名 Frozen_Heart）→忘却の首飾り（新規）。`monster` コマンドの表示名引数（Beholder#ASNTEST の "Job change target" 等、正解・おとり計28種）は識別子ではなく翻訳ルール上の許可リストにも無いため、jobs/1-1/thief.txt 等の前例に倣い英語のまま無改変とし、mes/mapannounce 側で同じ標的モンスター名を言及する箇所（`^008800Job change target^000000`）も表示との整合を優先して英語のまま残した。筆記試験90問（3パターン×10問）の select 選択肢に出るスキル名・モンスター名・アイテム名・武器名は本用語集の各表に準拠。
- jobs/2-1/hunter.txt（フェイヨン王宮・アーチャーギルド、ハンターギルド転職クエスト。面接10問＋罠原野の試験あり）で追加（すべて `::` 無しヘッダ、または `::` 有りでも表示名部分のみ翻訳可のヘッダにつき、話者タグのみ日本語化。Hunter Info#hnt::HntNotice のみヘッダ表示名も「ハンター案内#hnt::HntNotice」に翻訳、`#hnt` サフィックスと `::HntNotice` は無改変）: Hunter Guildsman#hnt（`[Hunter Guildsman]`→ハンターギルド職員、jobs/1-1/archer.txt の「アーチャーギルド職員」に揃えた命名パターン）、`[Hunter Sherin]`→ハンター・シェリン、Guild Receptionist#hnt（`[Guild Receptionist]`→ギルド受付係、正体判明後の `[Demon Hunter]`→デーモンハンター）、Hunter#htnGM・Hunter#htnGM2（`[Hunter Guildmaster]`→ハンターギルドマスター、役職のみの `[Hunter]`→ハンター）、Guide#hnt（`[Guide]`→案内係、用語集「Guide」の既存訳語を踏襲）。アイテム名（`getitemname()` を経由せず会話文中に直接書かれる箇所のみ翻訳、item 1007・内部名 Penetration）: Necklace of Wisdom (Penetration)→英知の首飾り（貫通）。jobs/2-2/sage.txt で確立済みの「Necklace of Wisdom→英知の首飾り」を踏襲し、hunter.txt 側にのみ原文にある "(Penetration)" 部分を（貫通）として追記。`monster` コマンドの表示名引数（Manager#hnt の "Job Change Monster" 等、正解・おとり計30種と HntTrap のトラップ NPC 群）は識別子ではなく翻訳ルール上の許可リストにも無いため英語のまま無改変とし、mes/mapannounce 側で標的モンスター名を言及する箇所（`^3355FFJob change monster^000000`、「Job change monster」）も表示との整合を優先して英語のまま残した。HntTrap（`switch(rand(200))` の罠発動メッセージ、case 1〜131）は正解と結びつく固定文言ではないランダムなユーモア演出のため、原文の意味を保ちつつ全て独自の日本語に翻訳した。
- npc/quests/skills/rogue_skills.txt（パロス灯台・ローグギルドの隠し部屋、「クローズコンファイン」スキルクエスト。Haijara Greg とその4人の息子＋訓練 NPC Kienna）で追加（すべて `::` 無しヘッダにつき表示名は英語のまま、話者タグのみ日本語化）: Haijara Greg（`[Haijara Greg]`）→ハイジャラ・グレッグ、Louis Greg（`[Louis Greg]`）→ルイス・グレッグ（末息子、幼い口調）、Thor Greg（`[Thor Greg]`）→トール・グレッグ（粗野な口調）、Jay Greg（`[Jay Greg]`）→ジェイ・グレッグ、Killer#Rogueguild（`[Killer]`、演出用の刺客役）→キラー、Kienna（訓練パートナー、`[Kienna]`）→キエナ、Chae Takbae（伝説のローグ、故人）→チェ・タクベ。jobs/2-2/rogue.txt で確立済みの表記をそのまま踏襲: Hollgrehenn Jr./Hollgrehen Jr.（原文の表記ゆれ）→ホルグレヘン・ジュニア、Hermanthorn Jr./Hermathorn Jr.（同）→ハーマンソーン・ジュニア、Antonio Jr.→アントニオ・ジュニア、Markie→マーキー。「panic room」は「隠し部屋」、モンクの架空スキル「Root」（本作独自の設定でモンクに実在しない）は「ルート」で統一。Thor Greg の台詞中「Markie says that the entrance is cleverly hidden to her left」は、jobs/2-2/rogue.txt でマーキーを男性として訳した既存設定と矛盾するため（英語原文側の代名詞の誤りと判断）、性別を明示しない「奴のすぐ左」に意訳した。同一英文が2箇所で異なる訳になる想定外の重複が2件あり（`select("Yes, please.:No, thanks.")` が442行目 Haijara Greg と812行目 Thor Greg、`mes "the Close Confine skill.";` が1007行目 Jay Greg と1309行目 Kienna）、いずれも話者ごとに自然な訳を当てた。
- npc/quests/skills/archer_skills.txt（モロクの廃墟・フェイヨンの「矢作成」「チャージアロー」スキルクエスト）で追加（すべて `::` 無しヘッダにつき表示名は英語のまま、話者タグのみ日本語化）: Roberto（moc_ruins、cities/comodo.txt の Roberto#cmd とは別 NPC だが同じ「ロベルト」表記を踏襲）、Jason（payon）→ジェイソン（新規、口癖の "Eh..." は「えー」に意訳）。Jason の台詞中に登場する実際のスキル名と異なる俗称「Arrow Repel」は、本来の Charge Arrow（チャージアロー）とは別の、Jason 独自の呼び方という原文の設定を保つため「アロー・リペル」と音写した（`skill "AC_CHARGEARROW"` 自体は変更なし）。会話中で直接語られるアイテム名（`getitemname()` 非経由）: Resin→松脂、Willow（モンスター名、jobs/1-1/archer.txt の「ウィロー」を踏襲）。
- quests/skills/crusader_skills.txt（ゲフェン・プロンテラ教会のクルセイダー用スキルクエスト「シュリンク」。Ford#11・Soldier#277・Pastor#1011 の3体とも `::` 無しヘッダにつき表示名は英語のまま、話者タグのみ日本語化）: Ford#11（`[Ford]`、本文中の自己紹介のみ "Leslie Ford" とフルネーム）→フォード（フルネームはレスリー・フォード）、Soldier#277（`[Soldier]`／`[Sloutii]`）→衛兵／スロウティ、Pastor#1011（`[Father Arthur]`）→神父アーサー。本文中にのみ登場する脇役名 Sir Arga→アルガ卿、組織名 Prontera Crusader Guardians→プロンテラ・クルセイダー守護隊（いずれも新規）。アイテム名（会話文中に直接書かれる箇所のみ翻訳、いずれもゴブリン毒解毒剤の材料）: Grape→ブドウ、Cyfar→サイファー、Unripe Apple→青リンゴ（新規、用語集アイテム表に追加）。Sticky Mucus→ネバネバした液体／Empty Bottle→空き瓶／Jellopy→ジェロピー／Coal→石炭 は既存踏襲。スキル名 Shrink→シュリンク は用語集スキル名表に新規追加。
- quests/skills/swordman_skills.txt（プロンテラのスキルクエスト「ファタルブロー」「ムービングHP回復」「オートバーサーク」。`- script ::KnightDeThomas` は表示名部分が空の `::` ヘッダにつき無改変、Leon Von Frich・Juan は `::` 無しヘッダにつき表示名は英語のまま、話者タグのみ日本語化。Pre-RE 版 `npc/pre-re/quests/skills/swordman_skills.txt` がこのファイルの KnightDeThomas を `duplicate()` するため、ヘッダの NPC 名は無改変のまま維持）: KnightDeThomas（`[De Thomas]`、本文中は "De Thomas Carlos" とフルネームで2回言及）→デ・トーマス（フルネームはデ・トーマス・カルロス）、Leon Von Frich（`[Leon]`、正体を明かさないジョークの話者タグ `[Sushi King Leon]`）→レオン（`[Sushi King Leon]`→寿司キングレオン）、Juan（`[Juan]`、正体不明時の話者タグ `[?]`）→フアン（`[?]`→`[？]` は全角化のみ）。スキル名 Moving HP Recovery（会話中の俗称 "Body Movin'" も同一スキルとして統一）→ムービングHP回復、Fatal Blow→ファタルブロー、Auto Berserk（会話中の省略形 "Berserk" も同一スキルとして統一）→オートバーサーク、Stun→スタン（いずれも用語集スキル名表に新規追加）。アイテム名（会話文中に直接書かれる箇所のみ翻訳）: Moth Wing→蛾の羽、Banana Juice→バナナジュース、Powder of Butterfly→蝶の粉、Honey→蜂蜜（いずれも新規）。Tentacle→触手／Horrendous Mouth→恐ろしい口／Decayed Nail→腐った爪 は jobs/2-2/rogue.txt・jobs/2-2/sage.txt の既存訳語を踏襲、Fire Arrow→火の矢／Silver Arrow→銀の矢／Empty Bottle→空き瓶 は用語集アイテム表の既存訳語を踏襲。
- quests/skills/novice_skills.txt（プロンテラ城・医院のノービススキルクエスト「応急手当」「死んだふり」。Nami・Chivalry Member・Nursing Instructor の3体とも `::` 無しヘッダにつき表示名は英語のまま、話者タグのみ日本語化）: Nami（`[Nami]`）→ナミ（明るく世話焼きな「～わ」「～わよ」調の看護師見習い）、Chivalry Member（`[Bulma]`）→ブルマ（豪快な武勇伝口調の元剣士、騎士団員）、Nursing Instructor（`[Dread Lord]`、シリアスな役職名に見せかけたジョークのニックネーム）→ドレッドロード（多忙で気難しい医院長、命令口調）。アイテム名（会話文中に直接書かれる箇所のみ翻訳、いずれも新規、用語集アイテム表に追加）: Sterilized Bandages→滅菌包帯、Newbie Tag / Novice Nametag（原文の表記ゆれ、同一アイテム item 7039 として統一）→ノービスネームタグ。Red Herb→赤ハーブ／Clover→クローバー は既存踏襲。スキル名 First Aid→応急手当／Play Dead→死んだふり は既存踏襲（jobs/novice/novice.txt 等で確立済み）。
- quests/skills/sage_skills.txt（ジュノー・シュバイヒルビル魔法学院のセージスキルクエスト「エレメンタルチェンジ」「エレメンタルコンバーター作成」。ヘッダ `yuno_in03,176,24,3 script Mischna 755,{` は `::` 無しにつき表示名は英語のまま不変、話者タグ `[Mishuna]`（ヘッダの綴り "Mischna" とは異なる原文側の表記ゆれ）のみ日本語化）: Mishuna→ミシュナ（丁寧な「です・ます」調の女性講師、jobs/2-2/sage.txt のメテウス・シルフェに近い口調で統一）。スキル名（いずれも新規、用語集スキル名表に追加）: Elemental Change→エレメンタルチェンジ、Elemental Converter Creation→エレメンタルコンバーター作成、Endow Blaze/Quake/Tornado/Tsunami→エンドウブレイズ／エンドウクエイク／エンドウトルネード／エンドウツナミ（`setarray .@ReqSkill$[0]`（"Blaze"等）は「エンドウ」+変数で結合されるため配列要素自体は「ブレイズ」「クエイク」「トルネード」「ツナミ」と定訳より1語短く格納、`setarray .@Skill$[0]`（"Fire"等）は文中で「～の」と続く用法に合わせて「火」「地」「風」「水」の1字に翻訳）。アイテム名（会話文中に直接書かれる箇所のみ翻訳、いずれも新規）: Horn→角、Rainbow Shell→レインボーシェル、Snail's Shell→カタツムリの殻、Blank Scroll→白紙の巻物、Scorpion Tail→サソリの尻尾、Payon Solution→フェイヨン溶液、Morocc Solution→モロク溶液、Red Bloods/Green Lives/Wind of Verdure/Crystal Blues（`setarray .@ReqItem$[0]`、Fire/Earth/Wind/Water の各エレメンタルチェンジ用素材）→赤き血／緑の命／若葉の風／蒼の結晶（いずれも用語集アイテム表に追加）。「%$#@!#$% Yap~~」「@#$%^~ Yap!」の記号羅列は詠唱の擬音のため記号部分は原文のまま残し、"Yap" のみ「ヤップ」に translate した。　※ 属性石 4 種の訳語は後に jobs/2-1/wizard.txt のカタカナ表記（クリスタルブルー / グリーンライブ / レッドブラッド / ウィンドオブヴァーデュア）へ統一済み。
- quests/skills/monk_skills.txt（プロンテラ聖堂裏・修練所のモンクスキルクエスト「気功玉を分け与える」「活殺の型」。Apprentice Monk#qsk_mo・Monk#qsk_mo の2体とも `::` 無しヘッダにつき表示名は英語のまま、話者タグ `[Monk]`（役職のみで個人名は明かされない）は「[モンク]」に統一）。スキル名（いずれも新規、用語集スキル名表に追加）: Spiritual Bestowment（MO_KITRANSLATION、パーティメンバーに気功玉を分け与えるスキル）→施しの法、Excruciating Palm（MO_BALKYOUNG）→活殺の型、Spirit Sphere→気功玉。アイテム名（会話文中に直接書かれる箇所のみ翻訳）: Stem→茎、Shoot→若芽（いずれも用語集アイテム表に追加）。指圧演出の擬音「*Tap-tap-tap...*」「*POKE*」は原文のリズムを保ちつつ「*トントントン…*」「*ペチッ*」に意訳した。
- quests/skills/acolyte_skills.txt（プロンテラ聖堂のアコライト用スキルクエスト「ホーリーライト」。`Cleric`（`::` 無しヘッダ）は表示名は英語のまま、話者タグのみ日本語化）: Acolyte Klift（`[Acolyte Klift]`）→アコライト・クリフト（cities/payon.txt の Archer Zakk→アーチャー・ザック 等、役職＋人名を「・」で繋ぐ既存パターンに統一）。アイテム名（`getitemname()` を経由せず会話文中に直接書かれる箇所のみ翻訳）: Opal→オパール（新規）。Crystal Blue→クリスタルブルー、Rosary→ロザリオ は jobs/2-1/wizard.txt・jobs/2-1/priest.txt の既存訳語を踏襲。スキル名 Holy Light→ホーリーライト は pre-re/merchants/hair_style.txt の既存訳語を踏襲（用語集スキル名表に新規追加）。
- quests/skills/bard_skills.txt（コモド・モロクのバード用スキルクエスト「パンヴォイス」。全11ヘッダ（Young Man#bard_q1、Spiteful-Looking Bard#bs、Yhelle#bard_chick1～5、Customer#bard_skill01/02、Bartender#bard_qskill、function F_BardSkillYhelle）とも `::` 無しにつき表示名は英語のまま、話者タグのみ日本語化）: Timid Young Man（`[Timid Young Man]`）→臆病な青年（cities/payon.txt の Young Man→青年 に「臆病な」を付加）、Riott（`[Riott]`、Spiteful-Looking Bard#bs の話者タグ）→リオット、Hen Yhelle（`[Hen Yhelle]`、鶏 NPC 5体＋関数内で共通）→めんどりのイエル、Little Bit Drunken Guy→ほろ酔いの男、More Drunken Guy→泥酔した男（いずれも役職のみで新規）。Bartender→バーテンダー は cities/prontera.txt 系の既存訳語を踏襲。アイテム名（会話文中に直接書かれる箇所のみ翻訳）: Tropical Sograt→トロピカル・ソグラト、Vermilion on the Beach→ヴァーミリオン・オン・ザ・ビーチ、13 Year Old Tristan→13年物トリスタン、Munak Doll（Munak は既存訳語「ムナク」を踏襲）→ムナク人形（いずれも新規）。スキル名 Pang Voice（`BA_PANGVOICE`）→パンヴォイス は新規（用語集スキル名表に追加）。人物名（本文中の言及のみ、NPC 化なし）: Puchuchartan（ウンバラのウータンシャーマン）→プチュチャルタン、Yao Jun（ムナク人形の作り手）→ヤオ・ジュン、Kino Kitty→キノ・キティ、Errende（既存の「エレンデ」表記は本ファイルが初出）→エレンデ。Riott の催眠の呪文（426〜431行目、"Uuuummm Baaalaaaa" 等の意味を持たない擬似言語のうなり声）は jobs/2-2/alchemist.txt のダーウィンの催眠演出（Lorem Ipsum プレースホルダー）と同種の非言語的な演出テキストと判断し、翻訳すると存在しない意味を捏造することになるため英語のまま無改変とした。

- quests/skills/assassin_skills.txt（モロク・アサシンギルドのアサシン用スキルクエスト「ソニックアクセラレーション」「ベノムナイフ投擲」。Assassin#realman・Assassin#realgirl・Old Coffin#qsk_as・Old Coffin#qsk_as2・Stone Statue#qsk_as・Stone Statue#qsk_as2 はいずれも `::` 無しヘッダにつき表示名は英語のまま、話者タグのみ日本語化。Old Coffin/Stone Statue の4体と moc_pryd04 の #crypt は話者タグ自体が無く ^3355FF 色の地の文のみ）: Assassin#realman（`[Killtin]`）→キルティン（jobs/2-1/assassin.txt の凶暴そうな男／熟練アサシン・ヒューイと同じアサシンギルドの荒っぽい「～だ」「～ぞ」調で統一、新規）、Assassin#realgirl（`[Esmille]`、"beautiful Assassin Cross" と紹介される）→エスミル（「～わ」「～ね」調の女性口調、新規）。両ファイル共通で使われていない新規の固有名詞のため、jobs/2-1/assassin.txt 側に同名 NPC は無い。アイテム名（会話文中に直接書かれる箇所のみ翻訳、実アイテムはそれぞれ Blue_Jewel/Cardinal_Jewel/Skyblue_Jewel だが原文の呼称に合わせて訳した）: Sapphire→サファイア、Ruby→ルビー、Aquamarine→アクアマリン（いずれも新規）。原文255行目付近の `^FFFFFFaaaaa^000000`（意味のない色付き文字列、原文側の古い typo/演出崩れと思われる）はそのまま翻訳文にも残した。955行目のヘッダ `¡¡#crypt`（原文は EUC-KR 由来と見られる非 ASCII バイトを含み UTF-8 では同一バイト列を再現不可）は `　#crypt`（先頭は全角スペース U+3000）に改名。他ファイルから doevent/enablenpc 等で参照されていないことは `scripts/check-jp-structure.sh` の 5.外部参照 で確認済み（`tools/jp_structure_check.py` の 2.トークン構造 チェックが `::` 無しヘッダの非 ASCII 改名を例外扱いしていなかったため、3.ヘッダ 同様の例外を追加する修正を行った）。
- quests/skills/merchant_skills.txt（アルベルタの商人用スキルクエスト「ラウドエクスクラメーション」「チェンジカート」「カートレボリューション」。Necko・Charlron はいずれも `::` 無しヘッダにつき表示名は英語のまま、`- script ::Gershaun_alberta` は表示名部分が空の `::` ヘッダにつき無改変、話者タグのみ日本語化）: Necko（`[Necko]`）→ネッコ、Charlron（`[Charlron]`）→シャルロン、Gershaun_alberta（`[Gershaun]`、正体を明かさないジョークの話者タグ `[Sushi King Gershaun]`）→ゲルシャン（`[Sushi King Gershaun]`→寿司キングゲルシャン、quests/skills/swordman_skills.txt の「寿司キングレオン」と同じ命名パターンで統一）。OnTouch_ ラベル内の匿名の話者タグ `[!?]` は「[！？]」と全角化のみ。スキル名 Crazy Uproar→ラウドエクスクラメーション、Change Cart→チェンジカート、Cart Revolution→カートレボリューション（いずれも新規、用語集スキル名表に追加）。アイテム名（会話文中に直接書かれる箇所のみ翻訳、新規）: Grape Juice→グレープジュース（用語集アイテム表に追加）。Banana Juice→バナナジュース／Tentacle→触手／Iron→鉄／Animal Skin→動物の皮／Mushroom Spore→キノコの胞子／Fly Wing→ハエの羽 は既存踏襲。Necko の台詞中「7 Pearls」は実アイテム Scarlet_Jewel（`delitem 722,7`）と食い違う原文側の記述だが、会話文の字面どおり「真珠7個」と訳した（delitem 側の対象アイテムは無改変）。同様に Charlron・Gershaun の台詞に出る「Trunks」も実アイテムは Wooden_Block だが、用語集の Trunk→木の幹 に合わせて訳した。Charlron の分岐セレクト `select("That's why I came here.:What about my cart?:Two pairs is pitiful?")` の3番目「Two pairs is pitiful?」は原文自体が意味の取りにくい言い回しで、直後の返答 `mes "...it's not 'CARD'!"` が示す「カート/カードの聞き間違い」というオチを日本語でも成立させるため、選択肢を「カードが情けないのか？」、返答を「……それは『カード』じゃない！」という独自の空耳オチに意訳した（`:` の個数・オチの構造は維持し、jRO 公式訳の転載ではない）。
- quests/skills/dancer_skills.txt（コモド・プロンテラ教会のダンサー用スキルクエスト「チャーミングウィンク」。Canell#qsk_dan01・Aelle#qsk_dan02 はいずれも `::` 無しヘッダにつき表示名は英語のまま、話者タグのみ日本語化）: Canell（`[Canell]`、感情に応じた話者タグ `[Intoxicated Canell]`→[酔いしれるキャネル]、`[Frustrated Canell]`→[苛立つキャネル]）→キャネル、Aelle（`[Aelle]`、酔いの進行に応じた話者タグ `[Drunken Aelle]`→[酔ったアエル]、`[Totally Drunk Aelle]`→[べろべろに酔ったアエル]、`[Totally Hammered Aelle]`→[泥酔したアエル]、`[Annoyed Aelle]`→[苛立つアエル]、`[Sober Aelle]`→[素面に戻ったアエル]）→アエル（jobs/2-2/dancer.txt の Aile→エイル とは綴りも別 NPC のため訳し分けた）。正体を伏せた話者タグ `[??????]`（プロンテラ教会の人物、本文中で "the pastor" と呼ばれる）は「[？？？？？？]」と全角化のみ、本文中の言及は「神父様」と訳した。口調はキャネルが「ホホ～」の高笑いと「～わ」「～のよ」調の高慢な貴婦人口調、アエルが「～わ」「～のよ」の砕けた姉御肌口調（泥酔中は「～のよぉ」等のろれつの回らない口調に崩した）で統一。スキル名 Charming Wink→チャーミングウィンク（新規、用語集スキル名表に追加）。地名 Dead Pit→デッドピット（新規、用語集都市・地域表に追加。Orc Dungeon→オークダンジョン／Glast Heim→グラストヘイム は既存踏襲）。アイテム名（会話文中に直接書かれる箇所のみ翻訳、新規）: Crystal Mirror→クリスタルミラー、Alcohol→アルコール、Apple→リンゴ、Well-Baked Cookies→よく焼けたクッキー、China（Aelle の口語表現。実アイテムは White_Platter）→お皿（いずれも用語集アイテム表に追加）。Banana Juice→バナナジュース は既存踏襲。ウインクの数え歌 `Un, deux, trois~`（フランス語の「1、2、3」）は原文のニュアンスを残すためカタカナ「アン、ドゥ、トロワ～」に音写し、直後の正誤判定セレクト `switch(select("Un deux trois~-:Un, doux trois~:Un, deux, trois~"))`（1番目はコンマ抜け＋末尾ハイフン、2番目は "deux"→"doux" の綴り間違いで誤答、3番目のみ正解）も同じ3択構造・同じ誤答の性質（句読点崩れ／一音違いの言い間違い）を保ったまま「アンドゥトロワ～－」「アン、ドゥー、トロワ～」「アン、ドゥ、トロワ～」に翻訳し、正解の選択肢番号（`case 3`）は原文のまま維持した。`^3355FF`（地の文）・`^FF0000`／`^333333`（強調・効果音）の各色コードは、開始が最初の mes 行、終了が最後の mes 行という原文の構成を保ったまま該当箇所に付け直した。
- quests/skills/mage_skills.txt（ゲフェンタワーのマジシャン用スキルクエスト「エナジーコート」。ヘッダ `Great Wizard` は `::` 無しにつき表示名は英語のまま、話者タグのみ日本語化）: 話者タグ `[BLIZZARDRISS]`（本人が名乗る大仰な二つ名。ヘッダ表示名 "Great Wizard" とは別）→ブリザードリス。アイテム名（会話文中に直接書かれる箇所のみ翻訳）: Glass Bead→ガラスビーズ、1 carat Diamond（実アイテムは Crystal_Jewel だが会話上の呼称を優先）→1カラットのダイヤモンド、Solid Shell→硬い貝殻（いずれも新規、用語集アイテム表に追加）。Shell→貝殻 は用語集アイテム表の既存訳語を踏襲。スキル名 Energy Coat→エナジーコート は用語集スキル名表に新規追加。
- quests/skills/priest_skills.txt（プロンテラ聖堂のプリースト用スキルクエスト「レデムプティオ」。ヘッダ `Sister Linus` は `::` 無しにつき表示名は英語のまま、話者タグのみ日本語化）: Sister Linus（`[Sister Linus]`）→シスター・ライナス、本文中にのみ登場する Margaretha Sorin（`[High Priest Sorin]`とも言及、いずれも新規）→マルガレータ・ソリン。`mes "["+ strcharinfo(0) +"]";` によるプレイヤー名の話者タグ（2箇所）は連結構造ごと無改変。アイテム名（会話文中に直接書かれる箇所のみ翻訳）: Holy Water→聖水、Yggdrasil Leaf→ユグドラシルの葉（いずれも新規）。Blue Gemstone→青いジェムストーン は用語集アイテム表の既存訳語（Yellow/Blue/Red Gemstone 行）を踏襲、Wanderer→ワンダラー・Glast Heim→グラストヘイム・Lighthalzen→リヒタルゼン・Schwarzwald→シュバルツバルド は既存訳語を踏襲。スキル名 Redemptio→レデムプティオ、Resurrection（ALL_RESURRECTION、Redemptio 習得の前提スキル）→リザレクション はいずれも用語集スキル名表に新規追加。
- quests/skills/hunter_skills.txt（フェイヨンのハンター用スキルクエスト「ファランクス」。ヘッダ `Arpesto` は `::` 無しにつき表示名は英語のまま、話者タグのみ日本語化）: Arpesto（`[Arpesto]`）→アルペスト、Reidin Corse（`[Reidin Corse]`）→レイディン・コース。`emotion` の第2引数 `getnpcid(0, "Reidin Corse#tu")`（計7箇所、tu_archer.txt 側の別 NPC を指す識別子）は識別子のため無改変。原文はアルペストが自分の技名を何度も言い間違えるコントのため、正式名称は指示どおり「ファランクス」で統一し、道中で使われる仮称のみ「緊急の矢」「アルペスト流・壱の型」「アルペスト流・参の型」と訳し分けて笑いどころを再現した。アイテム名（会話文中に直接書かれる箇所のみ翻訳）: Cursed Ruby→呪われたルビー、Pet Food→ペットフード、Harpy's Feather / Harpy Feather（表記ゆれ）→ハーピーの羽根（いずれも新規、用語集アイテム表に追加）。スキル名 Phantasmic Arrow→ファランクス、Emergency Arrow（仮称）→緊急の矢 はいずれも用語集スキル名表に新規追加。
- quests/skills/alchemist_skills.txt（ジュノー研究所・リヒタルゼンのアルケミスト用スキルクエスト「バイオエシックス」＝ホムンクルス創造の基礎技術。全12ヘッダ、`::` 無しにつき表示名は英語のまま、話者タグのみ日本語化）で追加: スキル名 Bioethics（AM_BIOETHICS）→バイオエシックス、Vaporize→バーポライズ、Call Homunculus→ホムンクルス召喚、Homunculus Resurrection→ホムンクルスリザレクション。人物名: Pisruik（Elemental_Create_Book クエスト担当、眼鏡の神経質な研究者、性別は男）→ピスルイク、Irache→イラーチェ、Degas→デガス、Kellasus（バイオエシックス担当、道徳的に葛藤する父親）→ケラサス、Skrajjad（Vaporize 担当）→スクラジャド、Keshibien（ホムンクルス召喚担当）→ケシビエン、Broncher（ホムンクルスリザレクション担当、酒好き。原文に `Brocher` の綴り揺れがあるが同一人物のため表記統一）→ブロンチャー、Koring（ケラサスの娘、幼児口調）→コリング、Beninne（ケラサスの妻）→ベニンネ、Nannan→ナンナン、無名の `Alchemist` は話者タグ「[錬金術師]」。アイテム名（会話文中に直接書かれる箇所のみ翻訳）: Heart of Mermaid→人魚の心臓、Moth Dust→蛾の鱗粉、Maneater Blossom→マンイーターブロッサム、Clover extract→クローバーエキス、Empty Potion Bottle→空きポーション瓶（既存の Empty Bottle＝空き瓶と別アイテムのため区別）、Frill→フリル、Glass Tube→ガラス管、Seed of Life→生命の種、Morning Dew of Yggdrasil→ユグドラシルの朝露、Embryo→エンブリオ。Kellasus の筆記試験は `input .@input$` への自由入力とスキル名／アイテム名の直接比較（`if (.@input$ == "Vaporize")` 等）だが、外部ファイル参照ではなく同一ファイル内の比較かつ設問文自体を日本語化したため、正答文字列もバーポライズ／エンブリオ／ホムンクルスリザレクションへ翻訳して整合させた（Skrajjad・Keshibien・Broncher から先に教わる訳語と一致させ、日本語の設問に日本語で答えられるようにする判断）。
- quests/quests_geffen.txt（ゲフェンの「ウェルディングマスク」「ヘッドセット」クエストと数字合わせゲーム。Blacksmith・Eric・Nia#yagu はいずれも `::` 無しヘッダにつき表示名は英語のまま、話者タグのみ日本語化）で追加: Blacksmith（`[Blacksmith]`）→ブラックスミス、Eric（`[Eric]`）→エリック、Nia#yagu（`[Nia]`）→ニア。アイテム名（会話文中に直接書かれる箇所のみ翻訳、新規、用語集アイテム表に追加）: Welding Mask→ウェルディングマスク、Headset→ヘッドセット。ミニゲーム名 Number Match Game→数字合わせゲーム（Nia 独自のミニゲーム名、新規）。
- quests/quests_payon.txt（フェイヨンの「スカート・オブ・バージン」「イヤーマフ」「オラオラ（酸素マスク）」「ヘルム・オブ・エンジェル／デビルチキャップ」クエスト。Granny・Mystic Lady・Boy・`- script Young man#12` はいずれも `::` 無しヘッダにつき表示名は英語のまま、話者タグのみ日本語化）で追加: Granny（`[Granny]`）→おばあさん、Mystic Lady（`[Mystic Lady]`）→不思議な女性、Boy（話者タグ `[Young Man]`、酸素マスククエスト）→青年、Young man#12（話者タグ `[Young man]`、ヘルム・オブ・エンジェル／デビルチキャップクエスト。上の「青年」とは別 NPC のため訳し分け）→若者。アイテム名（会話文中に直接書かれる箇所のみ翻訳、新規、用語集アイテム表に追加）: Skirt of Virgin→スカート・オブ・バージン、Ear Muffs→イヤーマフ、Ora Ora→オラオラ（アイテム名としてそのまま片仮名表記）、Helm of Angel→ヘルム・オブ・エンジェル、Deviruchi Cap/Hat（原文の表記ゆれ）→デビルチキャップ／デビルチハット、Little Evil Horn→リトルイービルホーン、Talon of Griffon→タロン・オブ・グリフォン、Fang of Garm→ファング・オブ・ガルム。
- quests/quests_izlude.txt（イズルード・アルベルタ間の定期船「エドガーの誘い」クエスト。`- script ::Edgar_izlude -1,{` は `::` の前に表示名部分が無いヘッダのため無改変）で追加: Edgar_izlude（話者タグ `[Edgar]`）→エドガー。`warp "alberta",...`（2箇所）はマップ名の識別子のため無改変。登場する Phelix→フェリックス は cities/prontera.txt 等の既存訳語を踏襲（本ファイルでは会話中の言及のみで NPC 化なし）。
- quests/quests_aldebaran.txt（アルデバランの帽子トレーダー「ドクターバンド」「フェザーボンネット」「ファントム・オブ・オペラ」「サッカト」クエスト。`Trader#01` は `::` 無しヘッダにつき表示名は英語のまま、話者タグのみ日本語化）で追加: Trader#01（`[Trader]`）→トレーダー。アイテム名（会話文中に直接書かれる箇所のみ翻訳、新規、用語集アイテム表に追加）: Doctor Band→ドクターバンド、Feather Bonnet→フェザーボンネット、Phantom of Opera→ファントム・オブ・オペラ、Sakkat→サッカト（jobs/2-2/alchemist.txt の既存訳語を踏襲）、Red Bandana→赤いバンダナ、Cracked Diamond→ひび割れたダイヤモンド、Romantic Gent→ロマンチックジェント、Singing Plant→歌う植物。
- quests/quests_lutie.txt（ルティエの雪だるま型自動販売機「ラクーンハット」等8種の帽子交換クエスト。Vending Machine Man・Vending Machine はいずれも `::` 無しヘッダにつき表示名は英語のまま、話者タグのみ日本語化）で追加: Vending Machine Man（`[Titicupe]`）→ティティキュペ、Vending Machine（`[Audi]`）→オーディ。帽子名（select 選択肢・会話文中、新規、用語集アイテム表に追加）: Raccoon Hat→ラクーンハット、Spore Hat→スポアハット、Wonder Nutshell→ワンダーナッツシェル、Rainbow Eggshell（原文の表記ゆれ Ranbow Eggshell も同一に統一）→レインボーエッグシェル、Blush→ブラッシュ、Chef Hat→シェフハット、Candle→キャンドル、Cake Hat→ケーキハット。交換素材アイテム名（会話文中に直接書かれる箇所のみ翻訳、新規）: Kitty Band（jobs/2-2/dancer.txt の既存訳語を踏襲）→キティバンド、Tough Scalelike Stem→硬い鱗状の茎、Sea-otter Fur→ラッコの毛皮、Tongue→舌、Nut Shell→木の実の殻、Wing of Dragonfly→トンボの羽、Egg Shell→卵の殻、Claw of Desert Wolf→デザートウルフの爪、Alice's Apron→アリスのエプロン、Piece of Cake→ケーキの欠片、Bomb Wick→爆弾の導火線、Matchstick→マッチ棒、Candy→キャンディ。自動販売機の擬音（*Vroooooom~~*、*Bzzzzzt*、*choogachooga*、*Kapang!* 等）は原文のリズムを保ちつつ「*ブゥウウン～～*」「*ジジジジッ*」「*ガッチャンガッチャン*」「*ガッシャン！*」等の独自の日本語擬音に意訳した。
- quests/skills/wizard_skills.txt（ゲフェンタワー・プロンテラ騎士団のウィザード用スキルクエスト「サイトブラスター」。ヘッダ `Meow#q_wiz`・`Simon Mayace#q_wiz` はいずれも `::` 無しにつき表示名は英語のまま、話者タグのみ日本語化）: Meow（`[Meow]`、キャサリンに猫へ変えられたウィザード）→ミャウ、Simon Mayace（`[Simon]`）→サイモン。本文中にのみ登場する Catherine→キャサリン、犬の Maria→マリア（いずれも jobs/2-1/wizard.txt の既存表記を踏襲）。効果音テキスト `*BAM! BOOM! CRASH!*` 等の擬音は原文の意味を保ちつつ独自の日本語擬音に意訳した（例: ＊ドカン！　ボーン！　ガシャーン！＊）。精霊石アイテム名は jobs/2-1/wizard.txt の既存訳語（delitem コメント Crystal_Blue/Yellow_Live/Boody_Red/Wind_Of_Verdure が一致）を確認のうえ踏襲: Crystal Blue（複数形 Crystal Blues）→クリスタルブルー、Green Live（複数形 Green Lives）→グリーンライブ、Red Blood（複数形 Red Bloods、delitem コメントは表記ゆれで Boody_Red）→レッドブラッド、Wind of Verdure→ウィンドオブヴァーデュア。※本用語集アイテム表には同一英語の別表記ゆれ（Crystal Blues→蒼の結晶／Green Lives→緑の命／Red Bloods→赤き血／Wind of Verdure→若葉の風）が別途存在するが、これは本ファイルの翻訳とは無関係に追加されたもので、jobs/2-1/wizard.txt との重複・矛盾になっている。要確認・要統合。
- quests/skills/blacksmith_skills.txt（ゲフェン・ブラックスミスの追加スキルクエスト。ヘッダ `Akkie#qsk_bs`・`Goodman#qsk_bs` はいずれも `::` 無しにつき表示名は英語のまま、話者タグのみ日本語化）で追加: Akkie（そそっかしく人懐っこい若い女性、「です・ます」基調に時々どもる口調）→アッキー、Goodman（落ち着いた年長の男性職人、「～だ」「～だぞ」調）→グッドマン。BS_UNFAIRLYTRICK は本ファイル冒頭コメントでは旧称 "Dubious Salesmanship" と書かれているが、`db/pre-re/skill_db.yml` の実際の `Description` は "Unfair Trick" のため、訳語はこちらに基づき「アンフェアトリック」とした（スキル名表に追記）。Detrimindexta（item971、会話文中に直接登場）は jobs/2-2/alchemist.txt の筆記試験 select（`Karvodailnirol:Detrimindexta:Alcohol`）で英語のまま残されている前例に倣い、確立した訳語が無いため同じく英語のまま統一した。
- quests/skills/knight_skills.txt（プロンテラ騎士団第七師団・ナイトの追加スキルクエスト。ヘッダ7件すべて `::` 無しにつき表示名は英語のまま、話者タグのみ日本語化。エソフェイトは「だ・のだ・であろう・貴殿」調の硬めの騎士口調で統一）で追加: Essofeit Lageiya（Knight#kabuto、話者タグは短縮形）→エソフェイト・ラゲイヤ（話者タグ「エソフェイト」）、Grand Master Maroujje（本文中でのみ言及される、Grand Master NPC のフルネーム。NPC 自身の話者タグは役職のみ「グランドマスター」）→グランドマスター・マロウジェ、Zabi（Knight#zabii）→ザビ、Gon（Knight#drake）→ゴン、Jiya（Knight#sasword）→ジヤ、Gatack（Knight#gattack）→ガタック。役職のみの話者タグ: A Knight→あるナイト。`#tour` の OnTouch 演出で使われる `[?]`（正体不明の掛け声）は未訳のまま維持。会話中に直接言及されるモンスター名（Gatack の台詞、mob_db.yml 未収録）: Mystcase→ミストケース、Obeaune→オベイン（モンスター名表に追記）。Candy Cane（item530、内部名 Candy_Striper、会話文中に直接登場）→キャンディケイン（アイテム表に追記）。
- quests/skills/thief_skills.txt（モロク・シーフギルドの追加スキルクエスト。ヘッダ2件とも `::` 無しにつき表示名は英語のまま、話者タグのみ日本語化）で追加: Alcouskou（老練なシーフギルドの師、原文の崩れた英語表現は「～じゃ」「～のう」「～ぞ」調の老人口調に意訳して自然化した）→アルコウスコウ、RuRumuni（Bag Seller、フェイヨンの革細工職人、丁寧な「です・ます」調）→ルルムニ。素材アイテム名（会話文中に直接登場、アイテム表に追記）: Fine Grit（item7041）→細かい砂利、Leather Bag of Infinity（item7042）→無限の革袋、Cactus Needle（item952）→サボテンの針、Cobweb/Spiderweb（item1025、表記ゆれを統一）→クモの巣、Zargon（item912）→ザーゴン、Bear's Foot（item948。既存の「Bear's Footskin→熊の足の皮」とは別アイテムのため別訳語とした）→熊の足、Spawn（item908）→スポーン、Garlet（item910。jobs/2-2/rogue.txt の既存表記を踏襲）→ガーレット、Scell（item911）→セル。効果音・気合の掛け声（"Suuu Suuu uk -" 等の擬音、"Kiiiiiiai~!" 相当の効果音は無し）は原文の意味を保ちつつ独自の日本語擬音・擬態語に意訳した。line220 の `mes "Prepare ^3355FF20 Grasshopper's Leg^";` は上流側に色コードの閉じ `^000000` が欠落したタイプミスがあり、構造検証の「色コード数一致」を保つため翻訳側もあえて同じ形（`^3355FF` を開いたまま文字列を閉じる）で再現した。
- quests/quests_alberta.txt（アルベルタの人形クエスト・少年帽子クエスト・アントラークエスト・バオバオ/クレセントヘアピン/ファッショナブルグラス/ハートヘアピンクエスト・太陽神の帽子/サンデーハット/メイジハット/マジシャンハットクエスト・タートルアイランド一連クエスト・アルベルタボーイ「イロモ」クエスト。全29ヘッダとも `::` 無しにつき表示名は英語のまま、話者タグのみ日本語化）で追加: Elin→エリン、Grampa（役職寄りの呼び名のため固有名詞化せず）→じいさん、Cherokee→チェロキー、Stylish Merchant#new30（話者タグ Zic）→ジック、Hat store girl#new30（話者タグ Tempestra）→テンペストラ、Kinsey#tur→キンジー、Grandpa Turtle#tur→カメじいさん、`::Sailor_alberta`（話者タグ Gotanblue）→ゴタンブルー、`::Turtle_Scholar_alberta`（話者タグ Jornadan Niliria、原文表記ゆれ Jornandan Niliria を統一）→ジョルナダン・ニリリア、伝説の剣士の二つ名 'One'→「ワン」、Knight Leader#tur（話者タグ Takuyaka）→タクヤカ、Mudasamu#tur→ムダサム、Knight#tur（話者タグ Passats、原文表記ゆれ Passat を統一）→パサッツ、Knight#tur2（話者タグ Jayprocat）→ジェイプロキャット、Knight#tur3（話者タグ Squall）→スコール、Knight#tur4（話者タグ Nysurea、原文表記ゆれ Nyusurea を統一）→ニシュレア、Iromo#ep3_2→イロモ、Iromo's Mother#ep3_2（話者タグ Mother）→母親、Little Boy#ep3_2→少年。役職のみの話者タグ: Voyage log/Voyage Log（表記ゆれを統一）→航海日誌、Explorer's Letter→漂流者の手紙、Old scroll/Old Scroll→古い巻物、Crystal Plate/Crystal plate→水晶の石板、Turtle Stone Bead→亀石のビーズ、Turtle Stone/Turtle stone→亀の石、Metal Plate→金属の板、Scared Voice→おびえた声、Terrified Voice→怯えた声。アイテム名（会話文中に直接書かれる箇所のみ翻訳、新規、用語集アイテム表に追加）: Tiger's Footskin/Tiger Footskin→トラの毛皮、Boy's Cap/Boys Cap→ボーイズキャップ、Evil Horn→イビルホーン、Antler→アントラー、Bao Bao→バオバオ、Silk Ribbon→シルクリボン、Heroic Emblem/Voucher Of Orcish Hero→オークヒーローの証、Crescent Hairpin（報酬アイテムは内部名 First_Moon_Hair_Pin）→クレセントヘアピン、Heart Hairpin/Heart Hair Pin→ハートヘアピン、Fashionable Glasses→ファッショナブルグラス、Jack A Dandy/Jack be Dandy（原文表記ゆれを統一）→ジャックビーダンディ、Coral Reef（アイテム名、地名の「サンゴ礁」と同一表記で兼用）→サンゴ礁、Hat of the Sun God（報酬アイテムは内部名 Helm_Of_Sun、表記を統一）→太陽神の帽子、Sunday Hat（報酬アイテムは内部名 Picnic_Hat）→サンデーハット、Mage Hat（報酬アイテムは内部名 Wizardry_Hat）→メイジハット、材料の「Wizard Hat」（上流側で内部名 Star_Sparkling と不整合な記述だが原文のまま翻訳）→ウィザードハット、Magician Hat→マジシャンハット、Dragon Scale→ドラゴンの鱗、Mould Powder→型粉、Elder Willow Card（原文表記ゆれ Elder Wilow Card を統一）→エルダーウィローカード、Ancient Lips（内部名 Lip_Of_Ancient_Fish）→古代魚の唇、Symbol Of Sun/Emblem of the Sun God（表記を統一）→太陽神の紋章、Gold（素材アイテム）→金、Monster's Feed/Monsters Feed（会話中の呼称。item528）→化け物のエサ、Old Card Album→古いカード帖、Branch Of Dead Tree→枯れ木の枝、Animal Blood/"Animal Gore"（表記を統一）→動物の血、Red Frame→レッドフレーム、Red Muffler（会話中の呼称は「Red Scarf」）→レッドマフラー、Red Jewel（会話中の呼称は「Sardonyx」）→サードオニキス。人形アイテム名（Elin の人形クエスト、会話文中に直接登場）: Poring Doll→ポリンの人形、Chonchon Doll→チョンチョンの人形、Puppet（内部名 Stuffed_Doll）→パペット人形、Rocker Doll（内部名 Grasshopper_Doll）→ロッカー人形、Spore Doll→スポアの人形、Osiris Doll→オシリスの人形、Baphomet Doll→バフォメットの人形、Raccoon Doll（内部名 Raccoondog_Doll）→ラクーンの人形、Yoyo Doll（内部名 Monkey_Doll、上流側で「ヨーヨー人形」と呼びつつ実際は猿人形という原文側の不整合があるが、表示テキストどおり翻訳）→ヨーヨーの人形。`^3355FF`...`^000000` の色コードが複数の mes 行にまたがって開いたまま続く箇所（亀の石・亀の像・引き出しの中身などの説明文）は、行の割り付けを変えても上流と同じ位置（最初の行で開き、最後の行でのみ閉じる）を厳密に維持した。

- npc/other/arena/arena_lvl50.txt・arena_lvl60.txt・arena_lvl70.txt・arena_lvl80.txt・arena_party.txt（イズルード・アリーナのタイムフォースバトル。5ファイルとも全ヘッダ `::` 無しにつき表示名は英語のままで無改変、話者タグ・mapannounce のメッセージ側のみ日本語化。lvl50～80 は同一テンプレート構造のため、英文が同一の行は全ファイルで同一の訳語に統一した）と npc/warps/other/arena.txt（アリーナ GM コントロールパネル、`#arenacontrol` は `::` 無しヘッダにつき無改変）で追加: 案内役 NPC（いずれも `::` 無しヘッダのため表示名は英語のまま、mapannounce の自己紹介文でのみ日本語化）: Heel and Toe（lvl50）→ヒール・アンド・トゥ、Minilover（lvl60）→ミニラバー、Cadillac（lvl70）→キャデラック、Octus（lvl80）→オクタス、Slipslowrun（party）→スリップスロウラン。受付役職のみの話者タグ `[Staff]`→[スタッフ]（用語集施設表に追加）。`[Helper Iriff]`（party の待機室係、役職+人名）→[案内係イリフ]。Vendigos（npc/other/arena/arena_room.txt が本体・別担当の翻訳対象。本バッチのファイルでは Staff の台詞中に "please go talk to Vendigos" の形で言及されるのみで話者タグとしては登場しない）→ヴェンディゴス（npc/other/arena/arena_room.txt 側でも同表記で確定済み）。システム用語: Time Force Battle→タイムフォースバトル、Arena Point(s)→アリーナポイント（npc/other/arena/arena_point.txt の既存訳語 `[アリーナポイント管理人]` 側に合わせて確認・追加。用語集施設表に追加）。モンスター名（mapannounce の関門クリア条件文中に直接登場、`db/import/mob_db.yml` 未収録のため一般的なカタカナ表記。モンスター名表に追加）: Smokie→スモーキー、Karakasa→カラカサ、Red Plant→レッドプラント、Vocal→ヴォーカル、Kapha→カパ、Miyabi Doll→ミヤビドール、Goblin Leader→ゴブリンリーダー、Rotar Zairo→ロタールザイロス、Horong→ホロン、Stem Worm→ステムワーム、Bathory→バトーリ、Argiope→アルジオペ、Hammer Goblin→ハンマーゴブリン、Alice（モンスター名、NPC人名の Alice とは別概念）→アリス、Kobold Leader→コボルドリーダー、Assaulter→アサルター、Nine Tail→ナインテール、Walking Petite→ウォーキングプティ、Fur-Seal→ファーシール、Merman→マーマン、Ancient Mummy→エンシェントマミー、Enchanted Peach Tree→精霊の桃の木（固有種というより描写的な名称のため意訳）。Kobold→コボルド、Drops→ドロップス、Hydra→ヒドラ、Nightmare→ナイトメア、Mantis→マンティス、Goblin→ゴブリン は既存踏襲。`monster` コマンドの表示名引数（spawn 呼び出し内の第4引数）自体は翻訳ルールの許可リストに無いため、Bathory・Ancient Mummy 等を含め全て英語のまま無改変とした（上記の訳語は mapannounce・mes に直接書かれた文中でのみ使用）。色コード付き連結文（`mes "..."+var+"..."` 形式、記録タイム表示・最速記録表示など）は `"..." + 変数 + "..."` の連結構造（文字列の個数・変数の位置）と各文字列内の `^RRGGBB` 色コード個数を上流と一致させたまま、内容のみ自然な日本語に意訳した。`select( "No","Yes" )` のようなカンマ区切り複数引数形式の select（party 内3箇所）も、コロン区切りの `select("a:b")` と同様に各項目を個別に翻訳した。
- quests/quests_yuno.txt（ジュノーの各種クエスト。メットの科学者コント「メットクエスト」、錬金術師兄弟クエスト、「Doomed Swords」ジュノー編の3本。全12ヘッダとも `::` 無しにつき表示名は英語のまま、話者タグのみ日本語化）で追加: メットクエスト — Metto（`[Metto]`、自称天才の暴走気味な研究者。「僕」一人称で興奮気味な口調）→メット、Wagan（`[Wagan]`、街の顔役的な立場の老年男性）→ワガン、Stangckle（`[Stangckle]`）→スタンクル、Kato（`[Kato]`）→カトー、CiCi（`[CiCi]`、尊大な教授口調）→シーシー。錬金術師兄弟クエスト — Bain（`[Bain]`）→ベイン、Bajin（`[Bajin]`。Bain とほぼ同一台詞の双子 NPC のため訳文も統一）→バジン。Doomed Swords ジュノー編 — A Citizen of Juno（`[Shalima]`）→シャリマ、Sage Yklah（`[Yklah]`）→イクラー、Sage Syklah（`[Syklah]`）→シクラー、Sage Esklah（`[Esklah]`）→エスクラー（原文の語形 Yklah/Syklah/Esklah が共通語根 klah を持つ点を活かし、イクラー／シクラー／エスクラーと音の連なりを保って統一。jRO 公式訳の転載ではなく独自の音写）、Muriniel's Recording（`[Muriniel's Recording]`、ムリニエル本人ではなく彼が遺した録音装置の声）→ムリニエルの記録。固有名詞・地名（新規）: Doomed Sword→呪われた剣、Elmeth Plateau→エルメス高原、Juphero（ジュノーが浮遊する動力の由来とされる古代都市名）→ジュフェロ（cities/yuno.txt の Freidrich の台詞で確立済みの「Juperos→ユペロス」とは原文の綴りが異なり、本用語集の「Juphero Plaza→ジュフェロ広場」と語根が一致するためそちらに揃えた。Juperos と同一都市か上流側の綴りゆれかは不明瞭なため訳し分けたまま残した。要確認）、Mt. Mjornir/Mountain Mjornir（既存の「Mt. Mjolnir→ミョルニール山脈」の原文側の綴りゆれと判断し統一）→ミョルニール山脈、The Paper（モンスター名、会話中の言及のみ）→ペーパー。ムリニエル関連アイテム（会話文中に直接書かれる箇所のみ翻訳、いずれも新規の架空クエストアイテムでゲーム内実装なし）: Stamp of Muriniel→ムリニエルの刻印、True Stamp of Muriniel→ムリニエルの真の刻印、Stamping Ink of Muriniel→ムリニエルの刻印用インク、Compass of Muriniel→ムリニエルの羅針盤、Dignity of Muriniel→ムリニエルの威厳、Muriniel's Cottage→ムリニエルの小屋。錬金・素材アイテム名（会話文中に直接書かれる箇所のみ翻訳）: Mini-Furnace（実アイテム Portable_Furnace）→小型炉、Burnt Tree（実アイテム Burn_Tree）→焦げた木、Fine Sand（実アイテム Fine_Sand）→細かい砂、Claw of Desert Wolf→デザートウルフの爪、Tooth of Bat→コウモリの牙、Piece of Egg Shell→卵の殻のかけら、Decayed Nail→朽ちた釘、Brigan→ブリガン（未確立の固有素材名のため音写）。Mixture→混合剤／Rough Oridecon・Rough Elunium→原石オリデコン・原石エルニウム／Coal→石炭／Phracon→フラコン／Iron Ore→鉄鉱石／Red Herb→赤ハーブ／Stone Heart→石の心臓／Juno Conference Hall→ジュノー会議場（既存の Juphero Plaza・Schweicherbil Magic Academy・Monster Museum・Sage Castle・Street of Book Stores とあわせ cities/yuno.txt の Shalima の台詞で言及）は既存訳語を踏襲または新規。`select("(Show him the slate):I'm a genius!:I'm a GM!")` の「GM」はゲーム内の GM（ゲームマスター）を指す一般的な略称のため無改変。機械・魔法演出の擬音（`*Vrrrmmmmm*`、`*Pakakkakakakkakaakapakakkakak*`、`*Shakakakakkakakakakkakakakakka!*`、`*Crank Crank*`、`*Click*`、詠唱文 "Doo de doo de~..." 等）は原文のリズムを保ちつつ独自の日本語擬音に意訳した（例: `*ブルルルン*`、`*パカカッ、カカカッ、カカカカッ*`、`*ガコン、ガコン*`、`*カチッ*`）。"- Mountain Mjornir -" の直下に続く "- mjolnir_02 . 170 193 -" はマップ ID を平文で表示するゲーム内のヒント演出のため、識別子として無改変で残した。"AHHH, it is a success!" 以下の連結文（`"but this time we have created "+getarg(1)` / `"^FF0000"+getitemname(getarg(0))+"^000000 !"`）は連結する文字列トークンの個数を変えられない制約上、「今回は」＋数量＋色付きアイテム名＋「を作り出した！」の順に意訳し、数量とアイテム名の間に助数詞は入れていない（Bain・Bajin 双方の S_DelItems ラベルで同一処理）。
- npc/other/arena/arena_room.txt・arena_aco.txt・arena_point.txt（イズルードアリーナの待合室・受付、アコライト専用アリーナ、アリーナポイント交換。全ヘッダとも `::` 無しにつき表示名は英語のまま、話者タグ・select・mapannounce のメッセージ側のみ日本語化）で追加: NPC人名（いずれも `::` 無しヘッダのため表示名は英語のまま、話者タグのみ日本語化）: Vendigos（arena_room.txt。既存の暫定表記を確定）→ヴェンディゴス、Owen Kheuv（Arena Record Staff）→オーウェン・クーヴ、Helper Pat→パット、Helper Ben→ベン、Helper Vicious→ヴィシャス（「だ・ぞ」調の粗野な口調）、Helper Epin→エピン、Helper Lunic→ルニック、Helper Lonik→ロニック、Givu（Givu#arena、Func_Are_Rew 内でも使用）→ギヴ、Mathea（Arena Record Staff#aco）→マテア、Guide Alias→アリアス、Trocco（Trocco#aco1/#aco2、同一ナレーター）→トロッコ。役職のみの話者タグ: `[Arena Manager]`→[アリーナ管理者]、`[Reward Manager]`→[報酬管理者]、`[Teleporter]`→[テレポーター]（jobs/valkyrie.txt の既存訳語を踏襲）、`[Picture Manager]`→[写真管理者]、`[Live Broadcast]`→[実況放送]、`[Staff]`（arena_aco.txt）→[スタッフ]（npc/other/arena/arena_lvl50.txt 等の既存訳語 `[Staff]`→[スタッフ] と一致）、`[!!CAUTION!!]`→[!!注意!!]。既存ファイル中で言及されるだけの案内役 NPC 名は arena_lvl50～80.txt・arena_party.txt の既存訳語をそのまま踏襲（原文の綴りゆれに関わらず同一人物として統一）: Heel and Toe→ヒール・アンド・トゥ、Minilover→ミニラバー、Cadilac（原文の綴りゆれ。既存ファイルの綴りは Cadillac）→キャデラック、Actus（原文の綴りゆれ。既存ファイルの綴りは Octus）→オクタス、Slipslowrun→スリップスロウラン。システム用語（既存踏襲）: Arena Point(s)→アリーナポイント、Time Force Battle→タイムフォースバトル。新規システム用語: Arena Point Manager（話者タグ）→アリーナポイント管理人、Turbo Track Points→ターボトラックポイント（既存の「Turbo Track→ターボトラック」〔cities/aldebaran.txt〕に揃えた）。モンスター名（`monster`/`areamonster` の第4引数=表示名は翻訳ルール上の許可リストに無いため全て英語のまま無改変。以下は Givu の記念撮影 select・arena_aco.txt の mapannounce 目標文中に直接書かれる箇所のみ翻訳、`auriga_mob_db.txt` の JapaneseName で確認済み。モンスター名表に追加）: Baphomet→バフォメット、Dark Lord→ダークロード（既存踏襲）、Doppelganger→ドッペルゲンガー（既存踏襲）、Eddga→エドガ、Dracula→ドラキュラ（既存踏襲）、Samurai（記念撮影 select の表記。実体は item1492 Incantation Samurai）→怨霊武士、Stormy Knight（記念撮影 select の表記。実体は mob1251 Knight of Windstorm。既存ファイル〔other/bulletin_boards.txt 等〕の「Stormy Knight→ストーミーナイト」に揃えた）→ストーミーナイト、Phreeoni→フリオニ（既存踏襲）、Girl（$@arena_picture_id==6969 の特殊枠、"pretty girls" の意訳）→女の子、Valkyrie→バルキリー（既存踏襲、jobs/valkyrie.txt の「Valkyrie→バルキリー」）。アイテム名（Givu の消耗品交換 select、新規、用語集アイテム表に追加）: Mastela Fruit→マステラフルーツ、Condensed White Potion（既存の「White Potion→白ポーション」に揃えた）→濃縮白ポーション、Anodyne→アノダイン、Old Card Album→古いカードアルバム。`set $arn_xxx$, "Default"`（記録未更新時のプレースホルダー名、比較には未使用）→「未設定」に翻訳。`"- Wait a moment! -"` 等のハイフン装飾（Givu の重量超過メッセージ）内の半角ハイフンは記号のため無改変。
- quests/quests_prontera.txt（プロンテラ下水道入場クエスト、Ph.D帽子クエスト、ゲオボルグ家の呪いクエスト。全29ヘッダとも `::` 無しにつき表示名は英語のまま、話者タグのみ日本語化）で追加: NPC人名 — Karlomoff（`[Historian]`、ジュノー在住の歴史学者。レーケンバー歴史研究会第一研究員）→カルロモフ、Rodafrian（`[Historian Rodafrian]`、モロク在住の同僚歴史学者）→ロダフリアン、Mondo（`[Historian Mondo]`、ミョルニール山脈の歴史学者）→モンド、Bonnie Imbullea（`[Exhausted-Looking Woman]`→名乗り後は`[Bonnie Imbullea]`、祓魔の儀式に失敗し追放された元神官）→ボニー・インブレア、Kaanu（`[Kaanu]`、ボニーの息子）→カーヌ、Marjana（`[Marjana]`、モロクのアサシン）→マルジャナ、Larjes（Nameless Island Access Quest Addition 内で会話に登場するのみ）→ラージェス。役職のみの話者タグ: Recruiter→[募集係]、Culvert Guardian→[下水道守衛]、Teacher→[先生]、Busy Boy#prt（`[Busy-Looking Boy]`/`[Busy Looking Boy]` の表記ゆれを統一）→[忙しそうな少年]、Historian（Karlomoff の名乗り前）→[歴史学者]、Assassin Guildsman→[アサシンギルド員]、Librarian→[司書]、Absent-Minded Boy→[ぼんやりした少年]、Exhausted-Looking Woman（Bonnie の名乗り前）→[やつれた女性]、Dog→[犬]。神話・固有名詞: Jormungand（jobs/2-2/sage.txt の既存訳語「Yormungandr→ヨルムンガンド」に統一）→ヨルムンガンド、Loki→ロキ、Angrboda→アングルボザ、King Tristram III/Tristram Geoborg III（prontera/izlude/alberta の既存訳語「King Tristram III→トリスタム3世」に統一）→トリスタム（・ゲオボルグ）3世、Geoborg（呪われた王家の姓）→ゲオボルグ、Rekenber Historical Research Group（新規、Rekenber Corporation→レーケンバー社に揃えた）→レーケンバー歴史研究会。伝承歌（jobs/2-2/bard.txt の歌詞穴埋めクイズと同様、`input` した文字列を同一ファイル内の `if (.@line$ == "…")` 等で照合する形式のため独自の日本語詩に翻訳し、mes 表示側と比較側の訳文を完全一致させた。行の分割位置は場面ごとに異なるが訳語自体は全編で統一）: The great serpent swallowed the sea.→大蛇が海を飲み込んだ。、The eagle of the rainbow swallowed the serpent.→虹の鷲が、その大蛇を飲み込んだ。、（表向きに伝わる結末）Then the eagle built its nest./A nest upon the swallowed sea.→そして鷲は巣を作った。／飲み込んだ海の上に。、（真の結末）Then snake scales grew on the eagle, and it slowly died.→そして鷲の体には蛇の鱗が生え、ゆっくりと死んでいった。アイテム名（会話文中に直接書かれる箇所のみ翻訳）: Leather Pouch（item7432、ボニーがバンフ神父へ託す薬草の包み）→薬草の袋、Books（item7431、カルロモフ宛ての配達物）→本、File01（item7342、カルロモフの報告書）→報告書。図書館の弁償金 `700 zeny` は用語集ルール通り Zeny 表記に統一（例:「700Zenyの弁償金」）。上流の色コード未クローズ（prince1〜3 の遺体描写・#prince2 の溶液描写で `^3355FF` を開いたまま `^000000` が無い計4箇所）はそのまま再現し、訳文でも閉じタグを追加しなかった。

- quests/quests_comodo.txt（コモドのクエスト集。ヘッドギアクエスト2本〔ヘアアクセサリー・帽子〕と、呪われた剣コモド編〔`dmdswrd_Q`〕。全21ヘッダとも `::` 無し（`BBQ Papa#cmd::CmdFamily` のみ `::CmdFamily` 付きだが、他の兄弟ヘッダに合わせて表示名は英語のまま）につき表示名は英語のまま、話者タグのみ日本語化）で追加: NPC人名（役割由来の名は意訳、固有名はカタカナ音写） — Hair Ornament Girl→髪飾りの少女、Isac Mari（Traveler#head）→アイザック・マリ、Rochito（Campground Boy#cmd）→ロチート、Rockha（Camping Youth#cmd）→ロッカ、Emralhandas（Camping Maiden#cmd）→エムラルハンダス、Rotute（Campground Lad#cmd）→ロチュート、Rinta（BBQ Boy#cmd）→リンタ、Razy（BBQ Visitor#cmd）→レイジー、BBQ Boy/BBQ Mama/BBQ Papa（CmdFamily、名もない家族の役職のみの話者タグ）→BBQ少年/BBQママ/BBQパパ、Tausupa（Chief#cmd、コモド族長）→タウスパ、Toruna→トルナ、Rakusa→ラクサ、Kichiri→キチリ、Magatu→マガツ（本文の綴りゆれ `Magatsu` は同一人物として統一）、Manzi→マンジ（本文の綴りゆれ `Muzi` は同一人物として統一）、Hullaris（老いた賢者、ダンサー風の歌う口調から知恵者の口調まで幅を持たせ「～わ」「～のよ」調で統一）→フラリス、Nigirboran→ニギルボラン（本文の綴りゆれ `Nigiroban` は同一人物として統一）、Meteurengut（アルデバランの錬金術師の末裔）→メテウレングート、Zaka（モロク）→ザカ、Won（コモド）→ウォン。本文中にのみ登場する固有名詞: Mariposum/Meropusum（コモドの古の魔女、表記ゆれを同一人物としてマリポスムに統一）→マリポスム、Rikaseh Sumarecon（石板の開発者）→リカセ・スマレコン、Kuprite（その秘密を再発見した錬金術師）→クプライト、Burukesaemu（メテウレングートの祖先）→ブルケサエム、Sage Yklah（ジュノーの賢者、次クエストへの案内役）→セージ・イクラー、Schwarzwald Republic（Schwarzwald は既存訳語シュバルツバルドを踏襲、Republic→共和国）→シュバルツバルド共和国。コモド独自の架空の食べ物・通貨（本文の綴りゆれをすべて統一）: Komodoru（コモド固有の動物の肉）→コモドル、Koserahserah/Koserserah（特製調味料）→コセラセラ、Mureuchieligu/Meruchieligu（特製ヴィンテージワイン）→ムレウチエリグ、Eulwo（カジノの専用通貨）→エルウォ、Comodo Cheese の真の名 Awakening Stone→覚醒の石、Slate of Muriniel/Murniel（表記ゆれを統一）→ムリニエルの石板、Book of the Lamb→子羊の書、Muriniel Pass→ムリニエル峠、Stamp of Muriniel（剣の所有資格の証）→ムリニエルの証印。ヘッドギア名（quest 内で会話文中に直接書かれる、`getitem`/`delitem` コメントの内部名とは別に本文の呼び名として翻訳、いずれも新規）: Cross Hat→クロスハット、Bulb Band→バルブバンド、Stripe Hairband→ストライプヘアバンド、Blue Hairband→ブルーヘアバンド、Mine Helmet/Mine Helm→マインヘルム、Parcel Hat/Hat of Bundle→包み帽子、Grief for Greed/Money Loser's Grief/Bankruptcy of Heart（同一アイテムの呼び名ゆれ）→強欲の嘆き、Opera Phantom Mask/Phantom of the Opera Mask/Opera Ghost Mask（完成品）→オペラ座の怪人の仮面、Opera Masque（完成前の素材アイテムとしての呼び名、完成品と訳し分け）→オペラの仮面。呪われた剣3本（会話文中に直接書かれるのみで `getitemname()` を経由しないため翻訳、用語集の既存「Executioner Style→エグゼキューショナースタイル」に綴りを揃えた）: Mysteltainn→ミストルティン、Ogretooth→オーガトゥース、Executioner→エグゼキューショナー。アイテム名（会話文中に直接書かれる箇所のみ翻訳、新規。Resin→松脂・Cobweb/Spiderweb→クモの巣・Rough Elunium→原石エルニウム・Blue Gemstone→青いジェムストーンは用語集の既存訳語を踏襲）: Transparent_Cloth（本文の呼び名は "Fabric"）→布、Sapphire→サファイア、Shining Stone→輝く石、Emerald→エメラルド、Gold（item969）→ゴールド、Snake Scales（Scale_Of_Snakes）→蛇の鱗、Scale Shell（Scales_Shell）→鱗の殻、Shining Shell/Shining Scale（Shining_Scales、本文の呼び名ゆれを統一）→輝く鱗、Stinky Scale（Rotten_Scale）→臭い鱗。`^3355FF`/`^FF0000` の色コードは開始・終了とも該当 mes 行内で閉じる原文の構成を踏襲しつつ、英語の行送り位置での色コード再分割（例: "Book"+"of the Lamb" のような単語またぎの分割）は日本語の複合語の可読性を優先して再現せず、色コード自体の総数は同一ブロック内で保つよう努めた（構造検証ツールの色コード数チェックは行単位の WARN であり FAIL 対象ではないため、この方針による WARN 多数は許容とした）。

- npc/other/mercenary_rent.txt（プロンテラ・フェイヨンアーチャー村・イズルードの傭兵レンタル/傭兵用品/傭兵ギルドON-OFFスイッチ。全ヘッダ `::` 有無に関わらず今回のバッチではヘッダ表示名を変更しない方針のため無改変、話者タグのみ日本語化）で追加: Mercenary Manager→傭兵ギルド職員、Mercenary Goods Merchant→傭兵用品商人、Checker（GM用パスワードNPC）→チェッカー。`.@name$` 配列（"Spear"/"Sword"/"Bow"）は `strnpcinfo(2)`（ヘッダの `#suffix`、無改変）との比較および `disablenpc`/`enablenpc` の対象名生成に使われる識別子のため英語のまま維持し、`mes .@name$[.@type] + "傭兵ギルドへ。"` のように和文と連結する形にとどめた。傭兵の階級表示は `callfunc("F_GetNumSuffix",...)` が返す英語序数（1st/2nd…）をそのまま維持し、直後に「級」を続ける形（例:「1st級Spearの傭兵」）で翻訳した（F_GetNumSuffix は英文法ヘルパーのため変更対象外）。Grade→級、Loyalty→忠誠度、10th Grade Mercenaries→10級の傭兵。
- npc/pre-re/other/resetskill.txt（→ npc/custom/jp/pre-re/other/resetskill.txt。プロンテラのスキル/ステータスリセットNPC。ヘッダ `::` 無しにつき表示名は英語のまま、話者タグのみ日本語化）で追加: Hypnotist→催眠術師。
- npc/quests/mrsmile.txt（主要都市6箇所に duplicate されるスマイルマスククエスト。ヘッダ `Smile Assistance::SmileHelper` は `::` 有りだが今回のバッチではヘッダ名を変更しないため無改変、話者タグのみ日本語化）で追加: Smile Girl（話者タグ）→スマイル案内嬢、本文中で自称される組織名 ' Smile Assistance '→「スマイル案内所」、Public Information Bureau of the Rune-Midgarts Kingdom（原文表記ゆれ "Kingom" を含む）→ルーンミッドガッツ王国広報局。Mr. Smile→ミスタースマイル（jobs/2-2/alchemist.txt の既存訳語を踏襲）。
- npc/quests/bunnyband.txt（アルベルタのバニーバンドイベント。ヘッダ `Kafra Employee#bunny` は `::` 無しにつき表示名は英語のまま、話者タグのみ日本語化）で追加: Kafra Employee→カプラ職員（既存踏襲）。アイテム名（会話文中に直接書かれる箇所のみ翻訳）: Four-Leaf Clover→四つ葉のクローバー、Pearl→真珠（いずれも新規）。Feather→羽根、Kitty Band→キティバンド（jobs/2-2/dancer.txt の既存訳語）は既存踏襲。Bunny Band Event→バニーバンドイベント（新規）。
- npc/quests/juice_maker.txt（プロンテラ城内・フェイヨンのジュース作成クエスト。全ヘッダ `::` 無しにつき表示名は英語のまま、話者タグのみ日本語化）で追加: Housewife Marianne（原文タイプミス `[Housewife Marinaa]` を1箇所含め同一人物として統一）→主婦マリアンヌ、Little Morrison→少年モリソン、Merchant Marx Hansen→商人マークス・ハンセン。ジュース名（会話文中・select・色コード付き案内文で使用）: Apple Juice→リンゴジュース、Banana Juice→バナナジュース（既存踏襲）、Carrot Juice→ニンジンジュース（新規）、Grape Juice→グレープジュース（既存踏襲。ただし原料表記の Grape 単体は用語集の既存訳語ブドウを使用）。重量超過時の定型メッセージ「- Wait a moment! - / - Currently you're carrying - / - too many items with you. - / - Please come back later - / - after you put some items into kafra storage. -」は merchants/alchemist.txt の既存訳（「- ちょっと待って！ -」等5行）をそのまま踏襲した。
- quests/first_class/tu_sword.txt（剣士1次職チュートリアル、イズルード/ゲフェン/モロク。今回のバッチではヘッダ表示名を変更しない方針のため全ヘッダ無改変、話者タグのみ日本語化）で追加: Shurank（Shurank Chainlier、プロンテラ騎士団のナイト、原文の表記ゆれ `[Shunrank]` を含め統一）→シュランク、Dequ'ee（ゲフェンのナイト）→デクィー。殺人事件の容疑者4名（モロク）: Hans→ハンス、Bankley→バンクリー、Geil→ガイル、Muetro（原文の表記ゆれ `Muestro`/`Han's` を含め統一）→ムエトロ。英語のまま意図的に残した箇所: Dequ'ee が容疑者から聞き出す暗号の断片4種（`victkleyundncem`/`hekdlfiDrindkelsd`/`ConBanfoevidehi`/`TheisWesomeof`）は、`input()` で読者がそのまま打ち込んで `.@hans$` 等の変数と一致判定される識別子的な文字列であり、かつ意味のある単語ではなく並べ替えパズル用の無意味な文字列であるため、代入側・比較側とも全箇所で原文のまま統一した。容疑者名を並べ替えて暗号を組み立てる4択×3段の select 選択肢は日本語の姓名（中黒区切り、例:「ハンス・バンクリー」）に翻訳した。
- quests/first_class/tu_thief01.txt（シーフ1次職チュートリアル、モロクの遺跡。ヘッダ `Thief Trainer#T` は `::` 無しにつき表示名は英語のまま、話者タグのみ日本語化）で追加: Yierhan（シーフ訓練係、伝法な砕けた口調で統一）→イエルハン、Mana（マジシャンギルドの知人、姿を見せない）→マナ。地名: South Morocc（モロク南門外の調査地点。既存訳語「Morocc→モロク」に準拠した新規複合表現）→モロク南部。
- npc/cities/morocc.txt（モロクの住人。全ヘッダ `::` 有無に関わらず今回のバッチではヘッダ表示名を変更しない方針のため無改変、話者タグのみ日本語化）で追加。役職タグ: Morocc Soldier→モロクの兵士、Morocc Volunteer→モロクのボランティア、Old Scholar→老学者、Drunken Young Man→酔った青年、Pale-looking Young Man→青ざめた青年、Little Girl/Little Boy→少女/少年、Slayer Kid（アサシンに憧れる少年の自称）→暗殺者気取りの少年、Assassin Guardian→アサシンの見張り、Ringing Voice（正体を伏せた声）→響く声。人物名（音写、新規）: Syvia→シヴィア、Akira→アキラ、Dimitri→ディミトリ、Armani→アルマーニ、Phlanette→フラネット、Hashisid→ハシシド、La Conte→ラ・コンテ。武器・スキル名: Katar→カタル（「カタール」は不使用。本用語集の F_GetWeaponType 表 の既存訳語に統一）、Sonic Blow→ソニックブロー（新規）、Katar Mastery→カタル熟練（新規、Katar の表記に合わせた）、Dual Dagger（概念語、アイテム名ではない）→双剣（新規）。原本に非 ASCII バイト（Señorita の ñ、0xF1 1 バイト）が1箇所あり、JP_TRANSLATION_RULES.md の規則に従い `\xF1` の16進エスケープでそのまま残し、周囲の英文のみ日本語化した（"Se\xF1orita"）。
- npc/kafras/dts_warper.txt（アインブロックのカプラ vs クールイベント社によるダンジョンテレポートサービス投票イベント。全ヘッダ表示名は今回変更しない方針のため無改変、話者タグのみ日本語化）で追加: Kafra Voting Staff→カプラ投票スタッフ、Cool Event Corp. Voting Staff→クールイベント社投票スタッフ、Cool Event Corp.→クールイベント社（新規）、Dungeon Teleport Service→ダンジョンテレポートサービス（既存の「テレポートサービス」表記に準拠）、Free Warp Tickets→無料ワープチケット（新規）、Kafra Special Reserve Points→カプラ特別ポイント（新規）。ダンジョン行き先名（会話文中・select・色コード付き案内文で使用）: Toy Factory→おもちゃ工場（既存踏襲）、Al De Baran Clock Tower / Clock Tower→アルデバラン時計塔・時計塔（既存の「Clock Tower→時計塔」に準拠）、Lava Dungeon→ノーグロード（既存の「Magma Dungeon→ノーグロード」と同一ダンジョン、マップ名 mag_dun02 で確認）、Byalan Dungeon→ビョルンダンジョン（既存の「Byalan Island→ビョルン島」の語根から新規）、Glast Heim Entrance→グラストヘイム入口（新規）。ダンジョン階層の "Level N"/"Nrd Floor" は「N階」に統一。GM専用の Vote Globalvar Girl#yuno は上流で `/* ... */` によりコメントアウトされ無効化されているため、原文のまま一切変更していない。
- npc/quests/counteragent_mixture.txt（アルベルタ・ゲフェンの中和剤・混合剤作成クエスト。全ヘッダ `::` 有無に関わらず今回のバッチではヘッダ表示名を変更しない方針のため無改変、話者タグのみ日本語化）で追加: Merchant Louitz→商人ルイツ（新規）、Aure Dupon→オーレ・デュポン（新規）、Chemist Morgenstein→化学者モルゲンシュタイン（Morgenstein は jobs/2-2/alchemist.txt に登場する未登場人物「Molgenstein→モルゲンシュタイン」と表記ゆれの同一人物と判断し統一。変数名 `molgenstain` は識別子のため無改変）。アイテム名: Counteragent→中和剤（既存踏襲）、Mixture→混合剤（既存踏襲）、Alcohol→アルコール（既存踏襲。通常の会話文脈のため一般訳語を使用）。Karvodailnirol・Detrimindexta は jobs/2-2/alchemist.txt の既存注記（本作オリジナルの架空アイテム名で他ファイルに訳語の前例が無いため）に従い、本ファイルでも select・会話文の双方で英語表記のまま統一した（例:「話す:Karvodailnirolについて話す:キャンセル」）。引用符は原文の `''...''` を「」に統一。重量超過時の定型メッセージ「- Wait a minute !! - / - Currently you're carrying - / - too many items with you. - / - Please try again - / - after you lose some weight. -」は既存の類似メッセージ（merchants/alchemist.txt 等）と原文の文言が異なるため新規に意訳した（「－　ちょっと待った！！　－」等5行）。
- npc/quests/first_class/tu_archer.txt（フェイヨン・イカロスギルドのアーチャー1次職チュートリアル）・tu_merchant.txt（アルベルタの商人1次職チュートリアル）で追加。両ファイルとも今回は担当指示によりヘッダの NPC 名を一切変更しない方針のため、`::` の有無に関わらず全ヘッダ無改変とし、話者タグのみ日本語化した。tu_archer.txt の NPC人名: Jet（Bard Jet#tu）→ジェット、Master Kavaruk→マスター・カヴァルク、Reidin Corse（Reidin Corse#tu）→レイディン・コース（quests/skills/hunter_skills.txt で確立済みの表記をそのまま踏襲。同ファイルの `getnpcid(0, "Reidin Corse#tu")` 等の識別子は無改変）、Seisner→セイズナー、Acolyte（Mafra、`-	script	::Acolyte_Tu`）→アコライト（マフラ）、Alchemist Guildmember（Alchemist Guildmember#tu）→錬金術師ギルド員、Arthail（Arthail of the Wind）→アルテイル（「風のアルテイル」）、New Guild Master（New Guild Master#tu）→新任ギルドマスター、Mage（Mage#tu）→マジシャン（既存踏襲）、Minister（Minister#tu_）→大臣、Bishop Maugins→モーギンス司教（Bishop→司教、新規）。tu_merchant.txt の NPC人名（すべて `::` 無しヘッダ）: Guarnien→ガルニエン、Sagle→セイグル、Kellion→ケリオン、Aigie→エイジー、Jayon→ジェイヨン、Maos→マオス。スキル名（tu_archer.txt、いずれも新規。Double Strafe→ダブルストレイフ・Arrow Shower→アローシャワー・Increase Concentration〔用語集は Improve Concentration の表記で既存〕→集中力向上は既存踏襲）: Owl's Eye→アウルアイ、Vulture's Eye→バルチャーアイ。スキル名（tu_merchant.txt、いずれも新規。Vending→ベンディング・Push Cart→プッシュカート・Discount→ディスカウントは既存踏襲）: Over Charge→オーバーチャージ、Mammonite→マモナイト、Item Appraisal→アイテム鑑定、Increase Weight Limit→重量増加。Magnifier（会話中の呼称）→ルーペ（新規）。レイディン・コースの口調は hunter_skills.txt で確立済みの伝法な「～ぜ」「～だろ」「チーフ」呼ばせ口調を踏襲し、彼の省略記号（`...`/`......`）のみ同ファイルの表記に合わせ「・・・」で統一した（他 NPC の省略記号は本用語集の標準表記「……」）。tu_archer.txt 冒頭の Bard Jet の寸劇（バーテンダーの語呂合わせ・マモナイトのダジャレ・ヴァイオリンケースのジョーク）は英語の言葉遊びに依存し直訳では意味が通らないため、原文の構造（オチの位置・呼びかけの select）を保ったまま独自の日本語ジョークに意訳した（jRO 公式訳の転載ではない）。`AC_OWL`/`AC_VULTURE`/`AC_DOUBLE`（getskilllv）、`AL_HEAL`/`AL_INCAGI`/`AL_BLESSING`（npcskill）、`MC_VENDING`/`MC_PUSHCART`/`MC_OVERCHARGE`/`MC_DISCOUNT`/`MC_MAMMONITE`/`MC_INCCARRY`/`MC_IDENTIFY`（getskilllv）、`F_SexMes`（callfunc 関数名）、`morocc`/`prontera`/`geffen`/`mjolnir_11`（warp のマップ名）、`Arpesto`（emotion の getnpcid 対象識別子）、`#Target`（specialeffect のエリア対象識別子）、`se_subterranean_waterwave.wav`/`se_littlewaves02.wav`/`se_scream_w01.wav`（サウンドファイル名）はいずれも識別子のため英語のまま無改変。tu_archer.txt 1857〜1859行目（大臣の緊迫感が消えたことを語る地の文）は上流側で `^3355FF` の色コードが開いたまま `^000000` で閉じられておらず、翻訳でも同じ形（閉じタグなし）で再現した。
- quests/first_class/tu_acolyte.txt（アコライト1次職チュートリアル、プロンテラ教会・聖カピトリーナ修道院。全ヘッダとも `::` 無しにつき表示名は英語のまま、話者タグのみ日本語化）で追加: NPC人名 — Priest Praupin（`[Priest Praupin]`）→プラウピン神父（jobs/1-1/acolyte.txt のマレウシス神父と同じ丁寧な「です・ます」調で統一）、Asthe（`[Asthe]`、聖カピトリーナ修道院の教師役）→アシュテ（本文中の言及は「シスター・アシュテ」、丁寧な「です・ます」調）、Priest Gardron（`[Priest Gardron]`）→ガードロン神父、Veiner（配達クエストの受取人、恋人にベタ惚れの軽い口調）→ヴァイナー、Hedrick（同、元気な労働者口調）→ヘドリック、Karven（同、祈祷中の神父、簡潔な口調）→カーベン、Gloria（見習いシスター、天然でおっとりした口調）→グロリア、Cleope Verce（ベテランのアコライト、からかい混じりの年長者口調「～わ」「～ね」）→クレオペ・ヴェルス、Bibi（Veiner の恋人、本文言及のみ）→ビビ。役職のみの話者タグ: Dog→[犬]、Boy（正体不明の子供霊）→[？？]、Ill Girl（`[Angelic]`、本人の名乗りに準拠）→[エンジェリック]、Weapon Merchant→[武器商人]、Sound by Window→[窓の外の物音]、Voices/Voice from Window（原文の単複表記ゆれを統一）→[窓の外の声]。Bishop Maugins（本文言及のみ）→モーギンス司教（quests/first_class/tu_archer.txt の既存訳語に統一）。神話・王家関連（quests/quests_prontera.txt「ゲオボルグ家の呪い」クエスト・jobs/2-2/sage.txt と同一の伝承のため、既存訳語に統一）: Yormungard（原文の表記ゆれ。既存訳語「Yormungandr/Jormungand→ヨルムンガンド」に統一）→ヨルムンガンド、Gaebolg family（原文の表記ゆれ。quests_prontera.txt の既存訳語「Geoborg→ゲオボルグ」に統一）→ゲオボルグ家、King Tristam III（原文の表記ゆれ。既存訳語「King Tristram III→トリスタム3世」に統一）→トリスタム3世、Asgardians→アスガルド人（新規、Asgard→アスガルドに準拠）。アイテム名（会話文中に直接書かれる箇所のみ翻訳、いずれも新規）: Bee Sting→ハチの針、Decayed Nail(s)→朽ちた爪。
- quests/first_class/tu_magician01.txt（マジシャン1次職チュートリアル、ゲフェンのマジシャンギルド）で追加: New Mage Manager（`[Mana]`）→マナ（quests/first_class/tu_thief01.txt で確立済みの表記・人物に統一。世話焼きでやや砕けた「～わ」「～わね」調の女性トレーナー）。本文中にのみ登場する人物名: Yierhan（tu_thief01.txt の既存訳語に統一）→イエルハン、Blizardis（マジシャンギルド内でエナジーコートを教える人物、本人は未登場）→ブリザーディス。属性名（`^RRGGBB色コード^000000` で強調される属性ラベル、jobs/2-2/sage.txt の世界観用語とは別に、本ファイルの属性魔法解説で新規に統一。今後の Mage/Wizard 系ファイルでも流用想定）: Fire→火、Earth→地、Wind→風、Water→水、Ghost→念（モンスター名表の「Ghostring→ゴーストリング」とは別表記のため新規追加）。スキル名（用語集スキル名表に照らし新規追加分のみ）: SP Recovery（Increase SP Recovery、既存の「SP Recovery→SPリカバリー」に準拠した複合表現）→SPリカバリー増加。地名: Morocc Pyramid→モロクのピラミッド（新規、既存訳語 Morocc→モロク・Pyramid→ピラミッドを結合）。
- quests/first_class/tu_ma_th01.txt（シーフ/マジシャン共通チュートリアル続き、争いの痕跡16箇所。ヘッダはすべて `Trace of Battle#1`〜`#16` で `::` 無し、話者タグは無く `^3355FF…^000000` のナレーション地の文のみ）で追加: 英文が完全一致する反復ブロック（同一の来歴不明フラグ分岐で使われる定型文）はファイル内で同一の訳文に統一した。人物名は本文中に「イエルハン」（tu_thief01.txt・tu_magician01.txt の既存訳語に統一）が言及されるのみ。上流778行目の色コード未クローズ（`^3355FF` を閉じずに次の mes へ続く原文の構成）はそのまま再現し、訳文でも閉じタグを追加しなかった。

## 装備部位名・武器種別・防具種別（npc/other/Global_Functions.txt の F_getpositionname / F_GetWeaponType / F_GetArmorType）

これらの関数の返り値は `refine.txt`・`advanced_refiner.txt`・`mjolnir_seal.txt`・`item_signer.txt`・`card_remover.txt`・`blessed_refiner.txt`・`shadow_refiner.txt`・`hd_refiner.txt` 等で `.@indices[select(.@menu$)]` のように**添字式の中で使われる**ため、CP932 で 2 バイト目が `[`/`]` になる文字（「ー」「ゼ」「ゾ」「‐」等）を一切使わない（詳細は JP_TRANSLATION_RULES.md の添字式ルール）。F_GetWeaponType・F_GetArmorType は本バッチでの直接の添字利用は未確認だが、同じ関数群として将来の利用に備え同一方針で統一した。

**F_getpositionname**（装備部位名、EQI_\*）: Accessory 1→アクセサリ1、Accessory 2→アクセサリ2、Shoes→靴、Robe→マント、Head 3→頭3、Head 2→頭2、Head→頭、Body→胴、Left hand→左手、Right hand→右手、Upper/Middle/Lower Costume Headgear→衣装上段/衣装中段/衣装下段、Costume Garment→衣装マント、Arrow/Ammunition→矢/弾薬、Shadow Armor→シャドウ防具、Shadow Weapon→シャドウ武器、Shadow Shield→シャドウ盾、Shadow Shoes→シャドウ靴、Shadow Accessory 1/2→シャドウアクセサリ1/シャドウアクセサリ2、Unknown→不明。

**F_GetArmorType**（装備種別、EQP_\*。EQP_HAND_R は F_GetWeaponType を呼び出す）: Lower/Upper/Middle Headgear→下段/上段/中段防具、Garment→マント、Accessory→アクセサリ、Armor→防具、Shield→盾、Shoes→靴、Costume Upper/Middle（原文タイプミス "Midle"）/Lower Headgear→衣装上段防具/衣装中段防具/衣装下段防具、Costume Garment→衣装マント、Ammo→弾薬、Shadow Armor/Weapon/Shield/Shoes/Accessory→シャドウ防具/シャドウ武器/シャドウ盾/シャドウ靴/シャドウアクセサリ、Unknown Equip→不明な装備。

**F_GetWeaponType**（武器種別、ITEMINFO_VIEW）: Dagger→短剣（「ダガー」は不使用）、One/Two-handed Sword→片手剣/両手剣、One/Two-handed Spear→片手槍/両手槍、One/Two-handed Axe→片手斧/両手斧、Mace→メイス、Staff→杖、Bow→弓、Knuckle→ナックル、Instrument→楽器、Whip→鞭、Book→本、Katar→カタル（「カタール」は不使用）、Revolver→リボルバ（「リボルバー」は不使用）、Rifle→ライフル、Gatling gun→ガトリングガン、Shotgun→ショットガン、Grenade Launcher→榴弾発射器（「グレネードランチャー」は不使用）、Shuriken→手裏剣、Unknown Weapon→不明な武器。

## 添字式の中で英語表記のまま残した箇所（rAthena parse_variable の制約）

`var[ ... ]` の中の文字列に「ー」等（CP932 2 バイト目が `[`/`]`）を入れられないため、以下は意図的に英語のまま（`getitemname()` の表示とも一致する）。詳細は docs/JP_TRANSLATION_RULES.md。

| ファイル | 行 | 内容 |
|---|---|---|
| npc/custom/jp/merchants/elemental_trader.txt | 85 | `select("Mystic Frozen:Great Nature:Flame Heart:Rough Wind")`（精霊石の選択肢） |

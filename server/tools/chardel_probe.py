#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rAthena の正規クライアント経路を実証する検証用ミニクライアント。

できること:
  * キャラクターの作成 / 削除予約 / 削除確定 (--create / --delete)
  * map まで入って即ログアウト (--enter-map)
  * 修練場の NPC「冒険者支援員」と会話して一次職に転職 (--npc-skip)
    npc/custom/jp/training_skip.txt の会話 (mes / next / select / close2 +
    savepoint + warp) を、実クライアントと同じパケット列で自動操作する。


対象サーバ:
    Pre-Renewal (--enable-prere) / PACKETVER 20211103 / パケット難読化キー 0x0,0x0,0x0
    (= clif_parse() の cmd ^ 0 となり暗号化なし)

パケット番号・レイアウトはすべて rAthena 本体ソースから確認した値のみを使う。
根拠は各定数のコメントを参照 (ファイル:行は本番と同一コミット e985006 のもの)。

パスワードは環境変数 RO_PROBE_PASSWORD からのみ取得し、
ログ・例外・JSON のいずれにも出力しない。
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import socket
import struct
import sys
import time

# ---------------------------------------------------------------------------
# 定数 (すべて rAthena ソース由来)
# ---------------------------------------------------------------------------

PACKETVER = 20211103
# src/config/packets.hpp:22 -- 20200902 <= 20211103 <= 20211118 なので PACKETVER_RE 有効
# src/common/mmo.hpp:154  -- NAME_LENGTH = 23 + 1
NAME_LENGTH = 24
# src/common/mmo.hpp:66-73 -- PACKETVER >= 20180124 なので MAX_CHARS = 15
MAX_CHARS = 15

# --- login-server (src/common/packets.hpp) ---------------------------------
CA_LOGIN = 0x0064               # packets.hpp:126  sizeof=55
AC_ACCEPT_LOGIN = 0x0AC4        # packets.hpp:210  PACKETVER >= 20170315 / 可変長
AC_REFUSE_LOGIN = 0x083E        # packets.hpp:239  PACKETVER >= 20120000 / sizeof=26
SC_NOTIFY_BAN = 0x0081          # packets.hpp:325  sizeof=3

# --- char-server (src/common/packets.hpp) ----------------------------------
CH_ENTER = 0x0065               # char_clif.cpp:1703 -> chclif_parse_reqtoconnect (固定 17 バイト)
HC_ACCEPT_ENTER = 0x006B        # packets.hpp:262  可変長 (CHARACTER_INFO の配列)
HC_REFUSE_ENTER = 0x006C        # packets.hpp:268  sizeof=3
HC_ACCEPT_ENTER2 = 0x082D       # packets.hpp:530  sizeof=29
HC_BLOCK_CHARACTER = 0x020D     # packets.hpp:383  可変長
HC_SECOND_PASSWD_LOGIN = 0x08B9  # packets.hpp:564  sizeof=12 (PIN 無効なら state=PINCODE_OK=0)
HC_CHARLIST_NOTIFY = 0x09A0     # packets.hpp:636  sizeof=6
CH_CHARLIST_REQ = 0x09A1        # packets.hpp:641  sizeof=2
# packets.hpp:613-619 -- PACKETVER_RE_NUM >= 20211103 の分岐なので 0x099d ではなく 0x0b72
HC_ACK_CHARINFO_PER_PAGE = 0x0B72
CH_MAKE_CHAR = 0x0A39           # packets.hpp:145  PACKETVER >= 20151001 / sizeof=36
# packets.hpp:270-276 -- PACKETVER_RE_NUM >= 20211103 の分岐なので 0x006d ではなく 0x0b6f
HC_ACCEPT_MAKECHAR = 0x0B6F     # sizeof = 2 + sizeof(CHARACTER_INFO) = 177
HC_REFUSE_MAKECHAR = 0x006E     # packets.hpp:288  sizeof=3
CH_DELETE_CHAR3_RESERVED = 0x0827  # packets.hpp:483  sizeof=6
HC_DELETE_CHAR3_RESERVED = 0x0828  # packets.hpp:491  sizeof=14
CH_DELETE_CHAR3 = 0x0829        # packets.hpp:498  sizeof=12
HC_DELETE_CHAR3 = 0x082A        # packets.hpp:505  sizeof=10
CH_DELETE_CHAR3_CANCEL = 0x082B  # packets.hpp:511  sizeof=6
HC_DELETE_CHAR3_CANCEL = 0x082C  # packets.hpp:518  sizeof=10
CH_SELECT_CHAR = 0x0066         # packets.hpp:131  sizeof=3
HC_NOTIFY_ZONESVR = 0x0AC5      # packets.hpp:308  PACKETVER >= 20170315 / sizeof=156
HC_NOTIFY_ACCESSIBLE_MAPNAME = 0x0840  # packets.hpp:542  可変長

# --- map-server (src/map/*) ------------------------------------------------
# src/map/clif_shuffle.hpp:4745 (PACKETVER > 20180307 のブロック内、
#   PACKETVER_RE_NUM >= 20211103 分岐) :
#   parseable_packet( 0x0436, 23, clif_parse_WantToConnection, 2, 6, 10, 14, 22 );
CZ_ENTER = 0x0436
CZ_ENTER_LEN = 23
CZ_ENTER_POS = (2, 6, 10, 14, 22)  # aid, cid, login_id1, client_tick, sex
ZC_AID = 0x0283                 # clif.cpp:10730 (PACKETVER >= 20070521) / 6 バイト
# src/map/packets.hpp:571 -- PACKETVER < 20141022 || PACKETVER >= 20160330 なので 0x0a18 ではなく 0x02eb
ZC_ACCEPT_ENTER = 0x02EB        # sizeof=13
ZC_REFUSE_ENTER = 0x0074        # src/map/packets.hpp:589  sizeof=3
CZ_NOTIFY_ACTORINIT = 0x007D    # clif_packetdb.hpp:32  clif_parse_LoadEndAck / 2 バイト
CZ_REQUEST_QUIT = 0x018A        # clif_packetdb.hpp:177 clif_parse_QuitGame / 4 バイト
ZC_ACK_REQ_DISCONNECT = 0x018B  # clif_packetdb.hpp:178 / 4 バイト

# --- map-server: 周囲のユニット (src/map/packets_struct.hpp の enum packet_headers) ---
# PACKETVER 20211103 は「PACKETVER >= 20150513」の分岐に入るので 0x09fd〜0x09ff。
ZC_NOTIFY_STANDENTRY = 0x09FF   # packets_struct.hpp:36  idle_unitType  (clif_set_unit_idle)
ZC_NOTIFY_NEWENTRY = 0x09FE     # packets_struct.hpp:75  spawn_unitType (clif_spawn)
ZC_NOTIFY_MOVEENTRY = 0x09FD    # packets_struct.hpp:107 unit_walkingType

# --- map-server: NPC 会話 ---
# clif_packetdb.hpp:43  parseable_packet(HEADER_CZ_CONTACTNPC, sizeof(PACKET_CZ_CONTACTNPC), ...)
# packets_struct.hpp:5412-5417  PACKET_CZ_CONTACTNPC { W PacketType; L AID; B type; } = 7 バイト
CZ_CONTACTNPC = 0x0090
# packets_struct.hpp:5486-5492  PACKET_ZC_SAY_DIALOG { W type; W len; L NpcID; char message[]; }
ZC_SAY_DIALOG = 0x00B4
# packets_struct.hpp:5513-5517  PACKET_ZC_WAIT_DIALOG { W type; L NpcID; } = 6 バイト
ZC_WAIT_DIALOG = 0x00B5
# packets.hpp:755-759  PACKET_ZC_CLOSE_DIALOG { W type; L npcId; } = 6 バイト
ZC_CLOSE_DIALOG = 0x00B6
# packets.hpp:761-767  PACKET_ZC_MENU_LIST { W type; W len; L npcId; char menu[]; }
ZC_MENU_LIST = 0x00B7
# clif_packetdb.hpp:62  parseable_packet(0x00b8,7,clif_parse_NpcSelectMenu,2,6)
#   -> naid.L @2 / select.B @6 (1 始まり。0xff = キャンセル)
CZ_CHOOSE_MENU = 0x00B8
# clif_packetdb.hpp:63  parseable_packet(0x00b9,6,clif_parse_NpcNextClicked,2)
CZ_REQ_NEXT_SCRIPT = 0x00B9
# packets.hpp:1852-1856  PACKET_CZ_CLOSE_DIALOG { W type; L GID; } = 6 バイト
# close2 は clif_scriptclose() を送ったところで script を止めるので、
# これを返さないと後続の savepoint / warp が実行されない
# (src/map/clif.cpp clif_parse_NpcCloseClicked -> npc_scriptcont)。
CZ_CLOSE_DIALOG = 0x0146
# packets.hpp:696-702  PACKET_ZC_NPCACK_MAPMOVE { W type; char mapName[16]; W x; W y; } = 22
ZC_NPCACK_MAPMOVE = 0x0091

# --- map-server: ステータス更新 (src/map/clif.cpp clif_updatestatus) ---
ZC_PAR_CHANGE = 0x00B0          # packets_struct.hpp:354-359  W varID; L count;   = 8
ZC_LONGPAR_CHANGE = 0x00B1      # packets_struct.hpp:361-366  W varID; L amount;  = 8
ZC_STATUS_CHANGE = 0x00BE       # packets_struct.hpp:368-373  W statusID; B value = 5
ZC_LONGLONGPAR_CHANGE = 0x0ACB  # packets_struct.hpp:399-404  W varID; q amount;  = 12
#   PACKETVER_RE_NUM(20211103) >= 20170830 なので BaseExp/JobExp は 0x0acb 側
ZC_SPRITE_CHANGE = 0x01D7       # packets_struct.hpp:317 sendLookType / 2591-2603

# src/map/map.hpp:497-514 enum _sp (0-60 のぶんだけ)
SP_NAMES = {
    0: "SP_SPEED", 1: "SP_BASEEXP", 2: "SP_JOBEXP", 3: "SP_KARMA",
    4: "SP_MANNER", 5: "SP_HP", 6: "SP_MAXHP", 7: "SP_SP", 8: "SP_MAXSP",
    9: "SP_STATUSPOINT", 11: "SP_BASELEVEL", 12: "SP_SKILLPOINT",
    13: "SP_STR", 14: "SP_AGI", 15: "SP_VIT", 16: "SP_INT", 17: "SP_DEX",
    18: "SP_LUK", 19: "SP_CLASS", 20: "SP_ZENY", 21: "SP_SEX",
    22: "SP_NEXTBASEEXP", 23: "SP_NEXTJOBEXP", 24: "SP_WEIGHT",
    25: "SP_MAXWEIGHT", 32: "SP_USTR", 33: "SP_UAGI", 34: "SP_UVIT",
    35: "SP_UINT", 36: "SP_UDEX", 37: "SP_ULUK", 41: "SP_ATK1", 42: "SP_ATK2",
    43: "SP_MATK1", 44: "SP_MATK2", 45: "SP_DEF1", 46: "SP_DEF2",
    47: "SP_MDEF1", 48: "SP_MDEF2", 49: "SP_HIT", 50: "SP_FLEE1",
    51: "SP_FLEE2", 52: "SP_CRITICAL", 53: "SP_ASPD", 55: "SP_JOBLEVEL",
    56: "SP_UPPER", 57: "SP_PARTNER", 58: "SP_CART", 59: "SP_FAME",
    60: "SP_UNBREAKABLE",
}
# src/map/map.hpp:594-609 enum _look
LOOK_BASE = 0

# src/common/mmo.hpp:888-895 enum e_job
SEX_FEMALE, SEX_MALE = 0, 1
JOB_NOVICE = 0
JOB_NAMES = {0: "Novice", 1: "Swordman", 2: "Mage", 3: "Archer", 4: "Acolyte",
             5: "Merchant", 6: "Thief"}

# 冒険者支援員 (npc/custom/jp/training_skip.txt) の 7 択と Job_xxx の対応。
# select() は 1 始まりで、7 番目が「まだ修練場を続ける」。
TRAINING_SKIP_JOBS = {
    "swordman": (1, 1, "剣士"),
    "archer":   (2, 3, "アーチャー"),
    "mage":     (3, 2, "マジシャン"),
    "acolyte":  (4, 4, "アコライト"),
    "merchant": (5, 5, "商人"),
    "thief":    (6, 6, "シーフ"),
}
TRAINING_SKIP_DECLINE = 7
TRAINING_SKIP_NPC_NAME = "冒険者支援員"
NOVICE_POTION = 569             # db/pre-re/item_db.yml  Novice_Potion
NV_BASIC = 1                    # db/skill_db.yml  NV_BASIC

# src/char/char.hpp:291 + src/common/packets.hpp:31-
#   MAX_CHAR_BUF = sizeof(struct CHARACTER_INFO)
# PACKETVER 20211103 (PACKETVER_RE) で有効な分岐を積み上げると 175 バイト。
CHARACTER_INFO_FMT = (
    "<"
    "I"    # GID                     @0    char_id
    "q"    # exp                     @4    PACKETVER >= 20170830 で int64
    "i"    # money                   @12
    "q"    # jobexp                  @16   PACKETVER >= 20170830 で int64
    "i"    # joblevel                @24
    "i"    # bodystate               @28
    "i"    # healthstate             @32
    "i"    # effectstate             @36
    "i"    # virtue                  @40
    "i"    # honor                   @44
    "h"    # jobpoint                @48
    "q"    # hp                      @50   PACKETVER_RE_NUM >= 20211103 で int64
    "q"    # maxhp                   @58
    "q"    # sp                      @66
    "q"    # maxsp                   @74
    "h"    # speed                   @82
    "h"    # job                     @84
    "h"    # head                    @86
    "h"    # body                    @88   PACKETVER >= 20141022
    "h"    # weapon                  @90
    "h"    # level                   @92
    "h"    # sppoint                 @94
    "h"    # accessory               @96
    "h"    # shield                  @98
    "h"    # accessory2              @100
    "h"    # accessory3              @102
    "h"    # headpalette             @104
    "h"    # bodypalette             @106
    "24s"  # name                    @108
    "6B"   # Str/Agi/Vit/Int/Dex/Luk @132
    "B"    # CharNum (= slot)        @138  PACKETVER >= 20081217
    "B"    # hairColor               @139
    "h"    # bIsChangedCharName      @140
    "16s"  # mapName                 @142  PACKETVER >= 20100803
    "i"    # DelRevDate              @158  PACKETVER_CHAR_DELETEDATE なので「削除確定までの残り秒」
    "i"    # robePalette             @162
    "i"    # chr_slot_changeCnt      @166
    "i"    # chr_name_changeCnt      @170
    "B"    # sex                     @174  PACKETVER >= 20141016
)
CHARACTER_INFO_SIZE = struct.calcsize(CHARACTER_INFO_FMT)
assert CHARACTER_INFO_SIZE == 175, CHARACTER_INFO_SIZE

# CHARACTER_INFO_FMT と 1:1 で対応するフィールド名 ("6B" は 6 個に展開される)。
CHARACTER_INFO_FIELDS = (
    "GID", "exp", "money", "jobexp", "joblevel", "bodystate", "healthstate",
    "effectstate", "virtue", "honor", "jobpoint", "hp", "maxhp", "sp", "maxsp",
    "speed", "job", "head", "body", "weapon", "level", "sppoint", "accessory",
    "shield", "accessory2", "accessory3", "headpalette", "bodypalette", "name",
    "Str", "Agi", "Vit", "Int", "Dex", "Luk", "CharNum", "hairColor",
    "bIsChangedCharName", "mapName", "DelRevDate", "robePalette",
    "chr_slot_changeCnt", "chr_name_changeCnt", "sex",
)
assert len(CHARACTER_INFO_FIELDS) == len(struct.unpack(
    CHARACTER_INFO_FMT, b"\x00" * CHARACTER_INFO_SIZE))

# login / char サーバが使う共通パケット長テーブル。
#   値 > 0 : 固定長 (sizeof(PACKET_xxx))
#   値 = -1: 可変長 (3-4 バイト目の packetLength を読む)
# src/common/packets.hpp の DEFINE_PACKET_HEADER / 構造体サイズを
# PACKETVER=20211103 で評価して機械的に取り出したもの。
COMMON_PACKET_LEN = {
    0x0064: 55,    # CA_LOGIN
    0x0066: 3,     # CH_SELECT_CHAR
    0x006B: -1,    # HC_ACCEPT_ENTER
    0x006C: 3,     # HC_REFUSE_ENTER
    0x006E: 3,     # HC_REFUSE_MAKECHAR
    0x006F: 2,     # HC_ACCEPT_DELETECHAR
    0x0070: 3,     # HC_REFUSE_DELETECHAR
    0x0081: 3,     # SC_NOTIFY_BAN
    0x0187: 6,     # PING
    0x01DB: 2,     # CA_REQ_HASH
    0x01DC: -1,    # AC_ACK_HASH
    0x01DD: 47,    # CA_LOGIN2
    0x01FA: 48,    # CA_LOGIN3
    0x01FB: 56,    # CH_DELETE_CHAR
    0x0200: 26,    # CA_CONNECT_INFO_CHANGED
    0x0204: 18,    # CA_EXE_HASHCHECK
    0x020D: -1,    # HC_BLOCK_CHARACTER
    0x0277: 84,    # CA_LOGIN_PCBANG
    0x027C: 60,    # CA_LOGIN4
    0x028D: 34,    # CH_REQ_IS_VALID_CHARNAME
    0x028E: 4,     # HC_ACK_IS_VALID_CHARNAME
    0x02B0: 85,    # CA_LOGIN_CHANNEL
    0x0825: -1,    # CA_SSO_LOGIN_REQ
    0x0827: 6,     # CH_DELETE_CHAR3_RESERVED
    0x0828: 14,    # HC_DELETE_CHAR3_RESERVED
    0x0829: 12,    # CH_DELETE_CHAR3
    0x082A: 10,    # HC_DELETE_CHAR3
    0x082B: 6,     # CH_DELETE_CHAR3_CANCEL
    0x082C: 10,    # HC_DELETE_CHAR3_CANCEL
    0x082D: -1,    # HC_ACCEPT_ENTER2 (packetLength を持つので実長は wire 参照)
    0x083E: 26,    # AC_REFUSE_LOGIN
    0x0840: -1,    # HC_NOTIFY_ACCESSIBLE_MAPNAME
    0x0841: 4,     # CH_SELECT_ACCESSIBLE_MAPNAME
    0x08B8: 10,    # CH_SECOND_PASSWD_ACK
    0x08B9: 12,    # HC_SECOND_PASSWD_LOGIN
    0x08BA: 10,    # CH_MAKE_SECOND_PASSWD
    0x08BE: 14,    # CH_EDIT_SECOND_PASSWD
    0x08C5: 6,     # CH_AVAILABLE_SECOND_PASSWD
    0x08D4: 8,     # CH_REQ_CHANGE_CHARACTER_SLOT
    0x08FC: 30,    # CH_REQ_CHANGE_CHARNAME
    0x08FD: 6,     # HC_ACK_CHANGE_CHARNAME
    0x09A0: 6,     # HC_CHARLIST_NOTIFY
    0x09A1: 2,     # CH_CHARLIST_REQ
    0x0A39: 36,    # CH_MAKE_CHAR
    0x0AC4: -1,    # AC_ACCEPT_LOGIN
    0x0AC5: 156,   # HC_NOTIFY_ZONESVR
    0x0ACF: 68,    # CT_AUTH
    0x0AE3: -1,    # TC_RESULT
    0x0B6F: 177,   # HC_ACCEPT_MAKECHAR
    0x0B70: -1,    # HC_ACK_CHANGE_CHARACTER_SLOT
    0x0B72: -1,    # HC_ACK_CHARINFO_PER_PAGE
}

PACKET_NAMES = {
    CA_LOGIN: "CA_LOGIN", AC_ACCEPT_LOGIN: "AC_ACCEPT_LOGIN",
    AC_REFUSE_LOGIN: "AC_REFUSE_LOGIN", SC_NOTIFY_BAN: "SC_NOTIFY_BAN",
    CH_ENTER: "CH_ENTER", HC_ACCEPT_ENTER: "HC_ACCEPT_ENTER",
    HC_REFUSE_ENTER: "HC_REFUSE_ENTER", HC_ACCEPT_ENTER2: "HC_ACCEPT_ENTER2",
    HC_BLOCK_CHARACTER: "HC_BLOCK_CHARACTER",
    HC_SECOND_PASSWD_LOGIN: "HC_SECOND_PASSWD_LOGIN",
    HC_CHARLIST_NOTIFY: "HC_CHARLIST_NOTIFY", CH_CHARLIST_REQ: "CH_CHARLIST_REQ",
    HC_ACK_CHARINFO_PER_PAGE: "HC_ACK_CHARINFO_PER_PAGE",
    CH_MAKE_CHAR: "CH_MAKE_CHAR", HC_ACCEPT_MAKECHAR: "HC_ACCEPT_MAKECHAR",
    HC_REFUSE_MAKECHAR: "HC_REFUSE_MAKECHAR",
    CH_DELETE_CHAR3_RESERVED: "CH_DELETE_CHAR3_RESERVED",
    HC_DELETE_CHAR3_RESERVED: "HC_DELETE_CHAR3_RESERVED",
    CH_DELETE_CHAR3: "CH_DELETE_CHAR3", HC_DELETE_CHAR3: "HC_DELETE_CHAR3",
    CH_DELETE_CHAR3_CANCEL: "CH_DELETE_CHAR3_CANCEL",
    HC_DELETE_CHAR3_CANCEL: "HC_DELETE_CHAR3_CANCEL",
    CH_SELECT_CHAR: "CH_SELECT_CHAR", HC_NOTIFY_ZONESVR: "HC_NOTIFY_ZONESVR",
    HC_NOTIFY_ACCESSIBLE_MAPNAME: "HC_NOTIFY_ACCESSIBLE_MAPNAME",
    CZ_ENTER: "CZ_ENTER", ZC_AID: "ZC_AID", ZC_ACCEPT_ENTER: "ZC_ACCEPT_ENTER",
    ZC_REFUSE_ENTER: "ZC_REFUSE_ENTER",
    CZ_NOTIFY_ACTORINIT: "CZ_NOTIFY_ACTORINIT",
    CZ_REQUEST_QUIT: "CZ_REQUEST_QUIT",
    ZC_ACK_REQ_DISCONNECT: "ZC_ACK_REQ_DISCONNECT",
    ZC_NOTIFY_STANDENTRY: "ZC_NOTIFY_STANDENTRY",
    ZC_NOTIFY_NEWENTRY: "ZC_NOTIFY_NEWENTRY",
    ZC_NOTIFY_MOVEENTRY: "ZC_NOTIFY_MOVEENTRY",
    CZ_CONTACTNPC: "CZ_CONTACTNPC", ZC_SAY_DIALOG: "ZC_SAY_DIALOG",
    ZC_WAIT_DIALOG: "ZC_WAIT_DIALOG", ZC_CLOSE_DIALOG: "ZC_CLOSE_DIALOG",
    ZC_MENU_LIST: "ZC_MENU_LIST", CZ_CHOOSE_MENU: "CZ_CHOOSE_MENU",
    CZ_REQ_NEXT_SCRIPT: "CZ_REQ_NEXT_SCRIPT", CZ_CLOSE_DIALOG: "CZ_CLOSE_DIALOG",
    ZC_NPCACK_MAPMOVE: "ZC_NPCACK_MAPMOVE", ZC_PAR_CHANGE: "ZC_PAR_CHANGE",
    ZC_LONGPAR_CHANGE: "ZC_LONGPAR_CHANGE", ZC_STATUS_CHANGE: "ZC_STATUS_CHANGE",
    ZC_LONGLONGPAR_CHANGE: "ZC_LONGLONGPAR_CHANGE",
    ZC_SPRITE_CHANGE: "ZC_SPRITE_CHANGE",
}

# ZC_NOTIFY_STANDENTRY / NEWENTRY / MOVEENTRY のレイアウト。
# src/map/packets_struct.hpp の packet_idle_unit / packet_spawn_unit /
# packet_unit_walking を PACKETVER=20211103 (PACKETVER_RE_NUM=20211103) で展開したもの。
# 3 つとも先頭は
#   PacketType.W(@0) PacketLength.W(@2) objecttype.B(@4) AID.L(@5) GID.L(@9)
# で共通 (PACKETVER >= 20091103 かつ >= 20131223 の分岐)。
# 末尾は PACKETVER >= 20131223 の char name[NAME_LENGTH]。
# clif_set_unit_idle() / clif_spawn() は sizeof(p) をそのまま送るので長さは固定。
#   "size" : 展開後の sizeof、"pos" : WBUFPOS された PosDir[3] の先頭オフセット
#            (packet_unit_walking は MoveData[6] なので座標は取らない)
UNIT_PACKET_LAYOUT = {
    ZC_NOTIFY_STANDENTRY: {"kind": "idle", "size": 108, "pos": 63},
    ZC_NOTIFY_NEWENTRY:   {"kind": "spawn", "size": 107, "pos": 63},
    ZC_NOTIFY_MOVEENTRY:  {"kind": "walk", "size": 114, "pos": None},
}
# job (= vd->look[LOOK_BASE]) は 3 つとも @23
UNIT_PACKET_JOB_OFFSET = 23
# src/map/clif.cpp:345-384 clif_bl_type()
UNIT_OBJECT_TYPES = {
    0x0: "PC", 0x1: "NPC", 0x2: "ITEM", 0x3: "SKILL", 0x4: "UNKNOWN",
    0x5: "NPC_MOB", 0x6: "NPC_EVT", 0x7: "NPC_PET", 0x8: "NPC_HOM",
    0x9: "NPC_MERSOL", 0xA: "NPC_ELEMENTAL", 0xC: "NPC_MOB_AI",
    0xD: "NPC_ABR", 0xE: "NPC_BIONIC",
}

# map-server のパケット長テーブル。
# src/map/clif_packetdb.hpp + src/map/clif_shuffle.hpp の packetdb_addpacket() 登録
# (後勝ち) に、src/map/packets.hpp / packets_struct.hpp の
# DEFINE_PACKET_HEADER + sizeof(PACKET_xxx) を PACKETVER=20211103 で評価して
# 補完したもの。"cmd:len" を並べた文字列で、len = -1 は可変長。
_MAP_PACKET_LEN_RAW = (
    "0064:55,0065:17,0066:3,0067:37,0068:46,0069:-1,006a:23,006b:-1,006c:3,"
    "006d:149,006e:3,006f:2,0070:3,0071:28,0072:22,0074:3,0075:-1,0076:9,"
    "0077:5,0079:53,007a:58,007b:60,007c:44,007d:2,007e:105,007f:6,0080:7,"
    "0081:3,0082:2,0083:2,0084:2,0085:10,0087:12,0088:10,0089:11,008b:2,"
    "008c:14,008d:-1,008e:-1,0090:7,0091:22,0093:2,0094:19,0096:-1,0099:-1,"
    "009a:-1,009b:34,009c:9,009d:19,009e:17,009f:20,00a1:6,00a2:14,00a7:9,"
    "00ab:4,00ae:-1,00af:6,00b0:8,00b1:8,00b2:3,00b3:3,00b4:-1,00b5:6,00b6:6,"
    "00b7:-1,00b8:7,00b9:6,00ba:2,00bb:5,00bc:6,00bd:44,00be:5,00bf:3,00c0:7,"
    "00c1:2,00c2:6,00c3:8,00c4:6,00c5:7,00c6:-1,00c7:-1,00c8:-1,00c9:-1,"
    "00ca:3,00cb:3,00cc:6,00cd:3,00ce:2,00cf:27,00d0:3,00d1:4,00d2:4,00d3:2,"
    "00d4:4,00d5:-1,00d6:3,00d7:17,00d8:6,00d9:14,00da:3,00db:8,00dc:28,"
    "00dd:29,00de:-1,00df:17,00e0:30,00e1:30,00e2:26,00e3:2,00e4:6,00e5:26,"
    "00e6:3,00e8:8,00ea:5,00eb:2,00ec:3,00ed:2,00ee:2,00ef:2,00f0:3,00f1:2,"
    "00f2:6,00f3:-1,00f5:11,00f6:8,00f7:17,00f8:2,00f9:26,00fa:3,00fb:-1,"
    "00fc:6,00fd:27,00ff:10,0100:2,0101:6,0102:6,0103:30,0104:79,0105:31,"
    "0107:10,0108:-1,0109:-1,010a:6,010b:6,010c:6,010d:2,010e:11,0110:14,"
    "0112:4,0113:25,0114:31,0115:35,0116:17,0117:18,0118:2,0119:13,011b:20,"
    "011d:2,011e:3,011f:16,0120:6,0121:14,0125:8,0126:8,0127:8,0128:8,0129:8,"
    "012a:2,012b:2,012c:3,012d:4,012e:2,012f:-1,0130:6,0131:86,0132:6,0134:-1,"
    "0135:7,0138:3,0139:16,013a:4,013b:4,013c:4,013f:26,0140:22,0141:14,"
    "0142:6,0143:10,0144:23,0145:19,0146:6,0147:39,0148:8,0149:9,014a:6,"
    "014b:27,014c:-1,014d:2,014e:6,014f:6,0150:110,0151:6,0152:-1,0153:-1,"
    "0154:-1,0155:-1,0156:-1,0157:6,0158:-1,0159:54,015b:54,015d:42,015e:6,"
    "015f:42,0160:-1,0161:-1,0162:-1,0164:-1,0165:30,0166:-1,0167:3,0168:14,"
    "0169:3,016a:30,016b:10,016c:43,016e:186,016f:182,0170:14,0171:30,0172:10,"
    "0173:3,0174:-1,0175:6,0176:106,0177:-1,0178:4,0179:5,017a:4,017b:-1,"
    "017c:6,017d:7,017e:-1,017f:-1,0180:6,0181:3,0182:106,0183:10,0184:10,"
    "0185:34,0187:6,0188:8,0189:4,018a:4,018b:4,018c:29,018d:-1,018e:18,"
    "018f:8,0190:23,0191:27,0192:24,0193:2,0196:9,0197:4,0198:8,0199:4,"
    "019a:14,019b:10,019c:-1,019d:6,019e:2,019f:6,01a0:3,01a1:3,01a2:37,"
    "01a3:7,01a4:11,01a5:26,01a6:-1,01a7:4,01a8:4,01a9:6,01aa:10,01ab:12,"
    "01ac:6,01ad:-1,01ae:6,01af:4,01b0:11,01b1:7,01b2:-1,01b3:67,01b5:18,"
    "01b6:114,01b7:6,01b8:3,01b9:6,01ba:26,01bb:26,01bc:26,01bd:26,01be:2,"
    "01bf:3,01c0:2,01c1:14,01c2:10,01c3:-1,01c6:4,01c7:2,01c8:15,01ca:3,"
    "01cb:9,01cc:9,01ce:6,01cf:28,01d0:8,01d1:14,01d2:10,01d3:35,01d4:6,"
    "01d5:-1,01d6:4,01d7:11,01d8:54,01d9:53,01da:60,01db:2,01dc:-1,01dd:47,"
    "01de:33,01df:6,01e0:30,01e1:8,01e2:34,01e3:14,01e4:2,01e5:6,01e6:26,"
    "01e7:2,01e8:28,01ea:6,01eb:10,01ec:26,01ed:2,01f0:-1,01f1:-1,01f2:20,"
    "01f3:10,01f4:32,01f5:9,01f6:34,01f7:14,01f8:2,01f9:6,01fa:48,01fb:56,"
    "01fc:-1,01fd:25,01fe:5,01ff:10,0200:26,0201:-1,0202:26,0203:10,0204:18,"
    "0205:26,0206:35,0207:34,0208:14,0209:36,020a:10,020d:-1,020e:32,020f:10,"
    "0210:22,0212:26,0213:26,0214:42,0215:6,0216:6,0217:2,0218:2,0219:282,"
    "021a:282,021b:10,021c:10,021d:6,021e:6,021f:66,0220:10,0221:-1,0222:6,"
    "0223:10,0224:10,0225:2,0226:282,0227:18,0228:18,0229:15,022a:58,022b:57,"
    "022c:65,022d:5,022e:71,022f:7,0230:12,0231:26,0232:9,0233:11,0234:6,"
    "0235:-1,0236:10,0237:2,0238:282,0239:11,023a:4,023b:36,023c:6,023d:-1,"
    "023e:8,023f:2,0240:-1,0241:6,0242:-1,0243:6,0244:6,0245:3,0246:4,0247:8,"
    "0248:-1,0249:3,024a:70,024b:4,024c:8,024d:12,024e:6,024f:10,0250:3,"
    "0251:34,0252:-1,0253:3,0254:3,0255:5,0256:5,0257:8,0258:2,0259:3,025a:-1,"
    "025b:8,025c:4,025d:6,025e:4,025f:6,0260:6,0261:11,0262:11,0263:11,"
    "0264:20,0265:20,0266:30,0267:4,0268:4,0269:4,026a:4,026b:4,026c:4,026d:4,"
    "026f:2,0270:2,0271:40,0272:44,0273:30,0274:8,0277:84,0278:2,0279:2,"
    "027a:-1,027b:14,027c:60,027d:62,027e:-1,027f:8,0280:12,0281:-1,0282:284,"
    "0283:6,0284:14,0285:6,0286:4,0287:-1,0288:-1,0289:12,028a:18,028b:-1,"
    "028c:46,028d:34,028e:4,028f:6,0290:4,0291:4,0292:2,0293:70,0294:10,"
    "0298:10,0299:8,029b:80,029c:66,029d:-1,029e:11,029f:3,02a0:-1,02a1:-1,"
    "02a2:8,02a3:-1,02a4:-1,02a5:8,02a6:-1,02a7:-1,02a8:162,02a9:58,02aa:4,"
    "02ab:36,02ac:6,02ad:8,02b0:85,02b1:-1,02b2:-1,02b3:107,02b4:6,02b5:-1,"
    "02b6:7,02b7:7,02b9:191,02ba:11,02bb:8,02bc:6,02bf:-1,02c0:-1,02c1:-1,"
    "02c2:-1,02c4:26,02c5:30,02c6:30,02c7:7,02c8:3,02c9:3,02ca:3,02cb:65,"
    "02cc:4,02cd:71,02ce:10,02cf:6,02d3:4,02d5:2,02d6:6,02d8:10,02d9:10,"
    "02da:3,02db:-1,02dc:-1,02dd:32,02de:6,02df:36,02e0:34,02e2:20,02e3:22,"
    "02e4:11,02e5:9,02e6:6,02e7:-1,02eb:13,02ec:67,02ed:59,02ee:60,02ef:8,"
    "02f0:10,02f1:2,02f2:2,02f3:-1,02f4:-1,02f5:-1,02f6:-1,02f7:-1,02f8:-1,"
    "02f9:-1,02fa:-1,02fb:-1,02fc:-1,02fd:-1,02fe:-1,02ff:-1,0300:-1,0301:-1,"
    "0302:-1,0303:-1,0304:-1,0305:-1,0306:-1,0307:-1,0308:-1,0309:-1,030a:-1,"
    "030b:-1,030c:-1,030d:-1,030e:-1,030f:-1,0310:-1,0311:-1,0312:-1,0313:-1,"
    "0314:-1,0315:-1,0316:-1,0317:-1,0318:-1,0319:-1,031a:-1,031b:-1,031c:-1,"
    "031d:-1,031e:-1,031f:-1,0320:-1,0321:-1,0322:-1,0323:-1,0324:-1,0325:-1,"
    "0326:-1,0327:-1,0328:-1,0329:-1,032a:-1,032b:-1,032c:-1,032d:-1,032e:-1,"
    "032f:-1,0330:-1,0331:-1,0332:-1,0333:-1,0334:-1,0335:-1,0336:-1,0337:-1,"
    "0338:-1,0339:-1,033a:-1,033b:-1,033c:-1,033d:-1,033e:-1,033f:-1,0340:-1,"
    "0341:-1,0342:-1,0343:-1,0344:-1,0345:-1,0346:-1,0347:-1,0348:-1,0349:-1,"
    "034a:-1,034b:-1,034c:-1,034d:-1,034e:-1,034f:-1,0350:-1,0351:-1,0352:-1,"
    "0353:-1,0354:-1,0355:-1,0356:-1,0357:-1,0358:-1,0359:-1,035a:-1,035b:-1,"
    "035c:2,035d:-1,035e:2,035f:5,0360:6,0361:5,0362:6,0363:6,0364:8,0365:8,"
    "0366:10,0367:31,0368:6,0369:6,0389:-1,040c:-1,040d:-1,040e:-1,040f:-1,"
    "0410:-1,0411:-1,0412:-1,0413:-1,0414:-1,0415:-1,0416:-1,0417:-1,0418:-1,"
    "0419:-1,041a:-1,041b:-1,041c:-1,041d:-1,041e:-1,041f:-1,0420:-1,0421:-1,"
    "0422:-1,0423:-1,0424:-1,0425:-1,0426:-1,0427:-1,0428:-1,0429:-1,042a:-1,"
    "042b:-1,042c:-1,042d:-1,042e:-1,042f:-1,0430:-1,0431:-1,0432:-1,0433:-1,"
    "0434:-1,0435:-1,0436:23,0437:7,0438:10,0439:8,043d:8,043e:-1,043f:25,"
    "0440:10,0441:4,0442:-1,0443:8,0444:-1,0445:10,0446:14,0447:2,0448:-1,"
    "0449:4,044a:6,07d7:8,07d8:8,07d9:268,07da:6,07e2:8,07e3:6,07e4:-1,07e5:8,"
    "07e6:8,07e7:32,07e8:-1,07e9:5,07ec:8,07f5:6,07f6:14,07f7:-1,07f8:-1,"
    "07f9:-1,07fa:8,07fc:10,07fd:-1,07fe:-1,0801:-1,0802:18,0803:4,0804:14,"
    "0805:-1,0806:2,0807:4,0808:14,0809:50,080a:18,080b:6,080e:14,0810:3,"
    "0811:-1,0812:8,0813:-1,0814:86,0815:2,0816:6,0817:6,0818:-1,0819:-1,"
    "081a:4,081b:10,081c:10,081d:22,081e:8,0820:11,0824:8,0835:-1,0837:3,"
    "0838:2,083a:5,083b:2,083c:14,083d:6,0842:6,0843:6,0844:2,0846:4,0848:-1,"
    "0849:16,084a:2,084b:19,0856:-1,0857:-1,0858:-1,085a:90,085d:18,0861:8,"
    "0862:10,0863:10,0865:6,0868:-1,086a:19,086c:8,086d:26,086f:26,0870:-1,"
    "0871:5,0874:8,0879:41,0881:5,0884:6,0885:5,0886:2,0887:6,0888:19,0889:90,"
    "088a:6,088b:2,088d:26,088e:7,0890:5,0891:6,0893:8,0897:5,0898:6,089b:10,"
    "089c:26,089e:6,089f:6,08a0:8,08a1:6,08a2:14,08a5:18,08a6:8,08a8:36,"
    "08aa:7,08ab:-1,08ac:8,08ad:90,08b3:-1,08c0:-1,08c7:20,08c8:34,08c9:2,"
    "08ca:-1,08cf:10,08d2:10,08d6:6,08d7:28,08d8:27,08d9:30,08da:26,08db:27,"
    "08dc:26,08dd:27,08de:27,08df:50,08e0:51,08e1:51,08e2:27,08e3:149,08e5:41,"
    "08e6:4,08e7:10,08e8:-1,08e9:2,08ea:4,08eb:39,08ec:73,08ed:43,08ee:6,"
    "08ef:6,08f0:6,08f1:6,08f2:36,08f3:-1,08f4:6,08f5:-1,08f6:22,08f7:3,"
    "08f8:7,08f9:6,08fa:6,08fb:6,08fe:-1,0907:5,0908:5,090a:26,090e:2,090f:-1,"
    "0914:-1,0915:-1,0916:26,091c:26,091d:41,0922:-1,0929:26,0933:6,0938:-1,"
    "093b:8,093f:5,0945:-1,0947:36,094a:6,094b:19,094c:6,094e:-1,0953:5,"
    "0959:10,0960:5,0961:36,0963:8,096a:6,096d:4,096e:-1,096f:7,0974:2,"
    "0977:14,0978:6,0979:50,097a:-1,097b:16,097c:4,097d:288,097e:12,097f:-1,"
    "0980:7,0983:29,0984:28,0988:6,0989:2,098a:-1,098d:-1,098e:-1,0998:8,"
    "0999:11,099a:9,099b:8,099f:22,09a6:12,09a7:10,09a8:16,09a9:10,09aa:16,"
    "09ab:6,09ac:-1,09ad:12,09ae:20,09af:4,09b0:10,09b1:4,09b2:10,09b3:6,"
    "09b4:6,09b5:2,09b6:6,09b7:4,09b8:6,09b9:4,09bc:6,09bd:2,09c1:10,09c3:8,"
    "09c4:10,09ca:23,09cb:17,09cd:8,09ce:102,09d1:14,09d4:2,09d6:-1,09d7:-1,"
    "09d8:2,09da:-1,09db:-1,09dc:-1,09dd:-1,09de:-1,09df:7,09e5:18,09e6:22,"
    "09e7:3,09e8:11,09e9:2,09ea:11,09ec:-1,09ed:3,09ee:11,09ef:11,09f0:-1,"
    "09f1:11,09f2:12,09f3:11,09f4:12,09f5:11,09f6:11,09f7:75,09f8:-1,09f9:143,"
    "09fa:-1,09fb:-1,09fc:6,09fd:-1,09fe:-1,09ff:-1,0a00:269,0a01:3,0a02:4,"
    "0a03:2,0a04:6,0a06:6,0a07:9,0a08:26,0a0e:14,0a12:27,0a13:26,0a14:10,"
    "0a15:12,0a16:26,0a17:6,0a19:2,0a1a:23,0a1b:2,0a1c:-1,0a1d:2,0a1e:3,"
    "0a1f:2,0a20:23,0a21:3,0a22:5,0a23:-1,0a24:66,0a25:6,0a26:7,0a27:8,0a28:3,"
    "0a2e:6,0a2f:7,0a30:106,0a32:2,0a35:4,0a3b:-1,0a3d:20,0a3f:11,0a44:-1,"
    "0a46:14,0a47:3,0a48:2,0a49:22,0a4a:6,0a4b:22,0a4c:28,0a4e:6,0a4f:-1,"
    "0a50:4,0a51:34,0a52:20,0a53:10,0a54:-1,0a55:2,0a56:6,0a57:6,0a58:8,"
    "0a59:-1,0a5a:2,0a5b:7,0a5c:18,0a5d:6,0a68:3,0a69:6,0a6a:12,0a6b:-1,"
    "0a6c:7,0a6d:-1,0a6e:-1,0a70:2,0a77:15,0a78:15,0a7d:-1,0a88:2,0a97:8,"
    "0a98:10,0a99:4,0a9a:10,0a9b:-1,0a9c:2,0a9d:4,0aa0:2,0aa1:4,0aa2:-1,"
    "0aa3:9,0aa4:2,0aa5:-1,0aa7:6,0ab2:7,0ab4:6,0ab5:2,0ab6:8,0ab7:4,0abd:10,"
    "0abe:-1,0ac0:26,0ac1:26,0ac7:156,0acb:12,0acc:18,0ace:4,0ada:32,0adb:-1,"
    "0add:22,0ade:6,0adf:58,0ae2:7,0ae6:10,0ae7:38,0ae8:2,0aef:2,0af0:10,"
    "0af4:11,0af6:88,0af7:32,0af8:11,0afa:58,0afb:-1,0afc:16,0afd:-1,0b08:-1,"
    "0b09:-1,0b0b:4,0b0d:10,0b0f:-1,0b10:10,0b11:4,0b12:2,0b14:2,0b15:7,"
    "0b16:2,0b17:3,0b18:4,0b19:2,0b1a:29,0b1b:2,0b1c:2,0b1d:2,0b1e:14,"
    "0b20:271,0b21:13,0b22:5,0b24:6,0b27:-1,0b28:3,0b2c:3,0b2d:11,0b2e:4,"
    "0b31:17,0b32:-1,0b33:17,0b35:3,0b36:-1,0b37:-1,0b39:-1,0b3d:-1,0b3f:64,"
    "0b40:-1,0b41:70,0b42:62,0b43:48,0b44:58,0b45:58,0b46:10,0b47:14,0b4c:2,"
    "0b4e:-1,0b57:-1,0b58:2,0b59:4,0b5a:-1,0b5b:14,0b5c:2,0b5d:10,0b5e:33,"
    "0b63:-1,0b64:-1,0b65:-1,0b66:26,0b67:33,0b68:12,0b69:18,0b6b:14,0b6c:12,"
    "0b6d:6,0b6e:14,0b73:8,0b77:-1,0b78:-1,0b79:-1,0b7a:-1,0b7b:118,0b7c:4,"
    "0b7d:-1,0b8d:-1,0b8e:18,0b8f:6,0b90:2,0b91:8,0b92:5,0b93:12,0b97:27,"
    "0b98:6,0b9a:11,0b9b:12,0b9c:16,0b9d:14,0b9e:12,0b9f:10,0ba0:2,0ba1:3,"
    "0ba4:85,0ba5:12,0ba8:7,0bad:2,0bae:3,0bb1:3,0bdd:-1,0be2:137,0be9:6,"
    "0bf3:-1,0c0b:18,0c0c:4,0c22:12,"
)


def _parse_len_table(raw: str) -> dict:
    table = {}
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        cmd, length = item.split(":")
        table[int(cmd, 16)] = int(length)
    return table


MAP_PACKET_LEN = _parse_len_table(_MAP_PACKET_LEN_RAW)

# packet_db の登録値が実際の送信サイズと食い違うもの (手で裏取りした分だけ)。
# rAthena は構造体を sizeof() で送るので、送信側の構造体サイズが正となる。
_MAP_PACKET_LEN_FIXUP = {
    # src/map/clif.cpp:3950-3959 clif_sprite_change() は
    # PACKET_ZC_SPRITE_CHANGE を sizeof() で送る。
    # src/map/packets_struct.hpp:2591-2603 の
    #   PACKETVER_RE_NUM >= 20180704 分岐では val/val2 が uint32 なので
    #   2 + 4 + 1 + 4 + 4 = 15 バイト。
    # clif_packetdb.hpp:226 の packet(0x01d7,11) は旧クライアント用で古い。
    0x01D7: 15,
}
MAP_PACKET_LEN.update(_MAP_PACKET_LEN_FIXUP)

RECV_TIMEOUT = 10.0


# ---------------------------------------------------------------------------
# 例外
# ---------------------------------------------------------------------------

class ProbeError(Exception):
    """検証の失敗 (プロトコル上の拒否を含む)。"""


class UnknownPacket(ProbeError):
    def __init__(self, cmd: int, label: str):
        super().__init__(
            "%s: 長さ不明のパケット 0x%04x を受信したためフレーミングを継続できません"
            % (label, cmd)
        )
        self.cmd = cmd


def pname(cmd: int) -> str:
    name = PACKET_NAMES.get(cmd)
    return "0x%04x(%s)" % (cmd, name) if name else "0x%04x" % cmd


# ---------------------------------------------------------------------------
# パケットストリーム
# ---------------------------------------------------------------------------

class PacketStream:
    """1 本の TCP 接続。複数パケットの連結受信に備えてバッファリングする。"""

    def __init__(self, host: str, port: int, table: dict, label: str,
                 verbose: bool = False, timeout: float = RECV_TIMEOUT):
        self.label = label
        self.table = table
        self.verbose = verbose
        self.timeout = timeout
        self.buf = bytearray()
        self.trace: list[str] = []
        self.recv_calls = 0
        self.recv_bytes = 0
        self.sent_bytes = 0
        self.waiting = None       # いま何を待っているか (タイムアウト時の診断用)
        # 受信したパケットを 1 個ずつ横から覗くフック (cmd, body) -> None。
        # expect() でも drain() でも read_packet() を通るので、
        # 「読み捨てた」パケットの中身も取りこぼさずに記録できる。
        self.observer = None
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.sock.settimeout(timeout)
        # 2〜36 バイトの小さな要求を投げて応答を待つ往復なので、
        # Nagle で送信を溜められると RTT のぶん素直に遅くなる。
        try:
            self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except OSError:
            pass
        self.peer = "%s:%d" % (host, port)
        self.t0 = time.monotonic()

    def _elapsed(self) -> float:
        return time.monotonic() - self.t0

    # -- 送信 ---------------------------------------------------------------
    def send(self, data: bytes, what: str = "") -> None:
        cmd = struct.unpack_from("<H", data, 0)[0]
        self.log("send %s len=%d%s" % (pname(cmd), len(data),
                                       (" " + what) if what else ""))
        self.sock.sendall(data)
        self.sent_bytes += len(data)

    # -- 受信 ---------------------------------------------------------------
    def _stall_report(self, waited: float) -> str:
        """タイムアウト時に「何を待っていて何が届いていたか」を残す。"""
        parts = ["%s: %s からの応答が %.1f 秒以内に届きませんでした"
                 % (self.label, self.peer, waited)]
        if self.waiting:
            parts.append("待っていたもの=%s" % self.waiting)
        if self.buf:
            parts.append("未処理バッファ=%d バイト (先頭 %s)"
                         % (len(self.buf), bytes(self.buf[:16]).hex(" ")))
        else:
            parts.append("未処理バッファ=0 バイト")
        parts.append("この接続の累計: 送信 %d バイト / 受信 %d バイト (recv %d 回) / 接続後 %.1f 秒"
                     % (self.sent_bytes, self.recv_bytes, self.recv_calls,
                        self._elapsed()))
        return " / ".join(parts)

    def _recv_more(self) -> None:
        """最低 1 バイト受信してバッファに足す。TCP は境界を保たないので
        呼び出し側は必要バイト数が揃うまでこれを繰り返す。"""
        started = time.monotonic()
        try:
            chunk = self.sock.recv(65536)
        except socket.timeout:
            raise ProbeError(self._stall_report(time.monotonic() - started))
        if not chunk:
            raise ProbeError(
                "%s: %s に接続を切断されました (%s)"
                % (self.label, self.peer,
                   self._stall_report(time.monotonic() - started)
                   .split(" / ", 1)[1] if self.waiting else "切断"))
        self.recv_calls += 1
        self.recv_bytes += len(chunk)
        self.log("recv raw %d バイト (recv %d 回目 / 累計 %d バイト / 待ち %.3f 秒 / "
                 "バッファ %d バイト)"
                 % (len(chunk), self.recv_calls, self.recv_bytes,
                    time.monotonic() - started, len(self.buf) + len(chunk)))
        self.buf.extend(chunk)

    def _need(self, n: int, what: str) -> None:
        while len(self.buf) < n:
            self.waiting = "%s (必要 %d バイト / 受信済み %d バイト)" % (what, n, len(self.buf))
            self._recv_more()
        self.waiting = None

    def read_raw(self, n: int) -> bytes:
        """パケットヘッダを持たない生バイト列を読む (char-server の aid 4 バイト)。"""
        self._need(n, "ヘッダ無しの生データ")
        data = bytes(self.buf[:n])
        del self.buf[:n]
        return data

    def read_packet(self) -> tuple:
        self._need(2, "次のパケットのヘッダ")
        cmd = struct.unpack_from("<H", self.buf, 0)[0]
        length = self.table.get(cmd)
        if length is None:
            raise UnknownPacket(cmd, self.label)
        if length == -1:
            self._need(4, "%s の packetLength" % pname(cmd))
            length = struct.unpack_from("<H", self.buf, 2)[0]
            if length < 4 or length > 32768:
                raise ProbeError("%s: %s の packetLength が不正です (%d)"
                                 % (self.label, pname(cmd), length))
        self._need(length, "%s の本体" % pname(cmd))
        body = bytes(self.buf[:length])
        del self.buf[:length]
        self.log("recv %s len=%d" % (pname(cmd), length))
        if self.observer is not None:
            self.observer(cmd, body)
        return cmd, body

    def expect(self, wanted, fatal=(SC_NOTIFY_BAN, HC_REFUSE_ENTER,
                                    ZC_REFUSE_ENTER), limit: int = 1024) -> tuple:
        """wanted のいずれかが来るまで読み飛ばす。"""
        if isinstance(wanted, int):
            wanted = (wanted,)
        label = "/".join(pname(w) for w in wanted)
        seen = []
        for _ in range(limit):
            self.waiting = "%s" % label
            cmd, body = self.read_packet()
            if cmd in wanted:
                self.waiting = None
                return cmd, body
            seen.append(pname(cmd))
            self.log("skip %s (%s を待機中)" % (pname(cmd), label))
            if cmd in fatal:
                raise ProbeError(
                    "%s: サーバが %s を返しました (result=%d)。期待した %s は来ませんでした"
                    % (self.label, pname(cmd), body[2] if len(body) > 2 else -1,
                       label))
        raise ProbeError("%s: %s を待っている間に %d パケット読み飛ばしました (%s)"
                         % (self.label, label, limit, ", ".join(seen)))

    def drain(self, seconds: float = 0.6) -> int:
        """指定秒だけ受信しつづけてフレーミングを進める (捨てる)。

        「いつ止まるか分からない流れ」を読み捨てる用途にだけ使う。
        届く数が決まっているものは read_packet()/expect() で確定的に読むこと
        (時間任せにすると RTT の大きい回線で取りこぼす)。
        """
        deadline = time.monotonic() + seconds
        count = 0
        try:
            while time.monotonic() < deadline:
                remaining = deadline - time.monotonic()
                self.sock.settimeout(max(0.05, min(remaining, self.timeout)))
                try:
                    if len(self.buf) < 2:
                        self._recv_more()
                    self.read_packet()
                    count += 1
                except socket.timeout:
                    break
                except ProbeError:
                    break
        finally:
            self.sock.settimeout(self.timeout)
            self.waiting = None
        return count

    def drain_until_idle(self, idle: float = 0.6, max_seconds: float = 20.0) -> int:
        """流れが止まるまで読み捨てる。

        map に入った直後のパケット群は「何個来るか」が決まっていないので、
        経過時間ではなく「idle 秒だけ何も届かなくなったら終わり」で判定する。
        固定の待ち時間にすると、RTT の大きい回線ではまだ流れている途中で
        打ち切ってしまう。
        """
        hard_deadline = time.monotonic() + max_seconds
        count = 0
        try:
            while time.monotonic() < hard_deadline:
                self.sock.settimeout(min(idle, max(0.05,
                                                   hard_deadline - time.monotonic())))
                try:
                    if len(self.buf) < 2:
                        self._recv_more()
                    self.read_packet()
                    count += 1
                except socket.timeout:
                    break
                except ProbeError:
                    break
        finally:
            self.sock.settimeout(self.timeout)
            self.waiting = None
        self.log("drain_until_idle: %d パケット読み捨てました" % count)
        return count

    def log(self, msg: str) -> None:
        line = "[%s] %s" % (self.label, msg)
        self.trace.append(line)
        if self.verbose:
            print("    " + line, file=sys.stderr)

    def close(self) -> None:
        try:
            self.sock.close()
        except OSError:
            pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


# ---------------------------------------------------------------------------
# 文字列ヘルパ
# ---------------------------------------------------------------------------

def encode_name(name: str) -> bytes:
    """キャラクター名を CP932 の NUL 埋め 24 バイトにする。"""
    try:
        raw = name.encode("cp932")
    except UnicodeEncodeError as exc:
        raise ProbeError("キャラクター名 %r は CP932 に変換できません (%s)"
                         % (name, exc))
    if len(raw) > NAME_LENGTH - 1:
        raise ProbeError("キャラクター名が長すぎます: %d バイト (CP932 で最大 %d バイト)"
                         % (len(raw), NAME_LENGTH - 1))
    return raw.ljust(NAME_LENGTH, b"\x00")


def decode_name(raw: bytes) -> str:
    return raw.split(b"\x00", 1)[0].decode("cp932", errors="replace")


def decode_cstr(raw: bytes) -> str:
    return raw.split(b"\x00", 1)[0].decode("ascii", errors="replace")


def decode_cp932(raw: bytes) -> str:
    """サーバが CP932 のバイト列として素通ししている文字列を UTF-8 の str にする。

    rAthena はスクリプトのバイト列をそのまま載せるだけなので、
    overlay-utf8/ を CP932 に変換して配置したこのサーバでは CP932 で読める。
    """
    return raw.split(b"\x00", 1)[0].decode("cp932", errors="replace")


# ---------------------------------------------------------------------------
# 周囲のユニット (ZC_NOTIFY_STANDENTRY / NEWENTRY / MOVEENTRY)
# ---------------------------------------------------------------------------

def parse_unit_packet(cmd: int, body: bytes) -> dict:
    """スポーン系パケットから AID / 名前 / 座標を取り出す。

    レイアウトが想定と違う (= PACKETVER の解釈がずれている) 場合は
    {"error": ...} を返して呼び出し側に判断させる。長さで気付けるようにするため
    ここでは例外にしない。
    """
    layout = UNIT_PACKET_LAYOUT[cmd]
    if len(body) != layout["size"]:
        return {"error": "%s の長さが %d バイトでした (PACKETVER %d での想定は %d)"
                         % (pname(cmd), len(body), PACKETVER, layout["size"]),
                "packet": pname(cmd), "length": len(body)}
    objecttype = body[4]
    aid, gid = struct.unpack_from("<II", body, 5)
    job = struct.unpack_from("<h", body, UNIT_PACKET_JOB_OFFSET)[0]
    name_raw = body[layout["size"] - NAME_LENGTH:].split(b"\x00", 1)[0]
    unit = {
        "kind": layout["kind"],
        "objecttype": objecttype,
        "objecttype_name": UNIT_OBJECT_TYPES.get(objecttype, "?"),
        # clif_set_unit_idle(): p.AID = bl->id / p.GID = sd ? char_id : 0
        # なので NPC を指すのは AID 側 (= CZ_CONTACTNPC に載せる値)
        "aid": aid,
        "gid": gid,
        "job": job,
        "name": name_raw.decode("cp932", errors="replace"),
        "name_cp932_hex": name_raw.hex(),
    }
    pos = layout["pos"]
    if pos is not None:
        # src/common/socket.hpp WBUFPOS(): x を 10bit, y を 10bit, dir を 4bit
        b0, b1, b2 = body[pos], body[pos + 1], body[pos + 2]
        unit["x"] = (b0 << 2) | (b1 >> 6)
        unit["y"] = ((b1 & 0x3F) << 4) | (b2 >> 4)
        unit["dir"] = b2 & 0x0F
    return unit


# ---------------------------------------------------------------------------
# CHARACTER_INFO
# ---------------------------------------------------------------------------

def parse_character_info(raw: bytes) -> dict:
    v = dict(zip(CHARACTER_INFO_FIELDS, struct.unpack(CHARACTER_INFO_FMT, raw)))
    return {
        "char_id": v["GID"],
        "base_exp": v["exp"],
        "zeny": v["money"],
        "job": v["job"],
        "job_level": v["joblevel"],
        "base_level": v["level"],
        "hp": v["hp"],
        "max_hp": v["maxhp"],
        "name": decode_name(v["name"]),
        "slot": v["CharNum"],
        "map": decode_cstr(v["mapName"]),
        # PACKETVER_CHAR_DELETEDATE が真なので「削除確定までの残り秒」。0 = 予約なし。
        "delete_date": v["DelRevDate"],
        "sex": v["sex"],
    }


def parse_character_list(body: bytes, base_offset: int) -> list:
    payload = body[base_offset:]
    if len(payload) % CHARACTER_INFO_SIZE != 0:
        raise ProbeError(
            "CHARACTER_INFO の長さが合いません: 残り %d バイトは %d で割り切れません。"
            "サーバの PACKETVER がクライアント側の想定 (%d) と違う可能性があります"
            % (len(payload), CHARACTER_INFO_SIZE, PACKETVER))
    out = []
    for off in range(0, len(payload), CHARACTER_INFO_SIZE):
        out.append(parse_character_info(payload[off:off + CHARACTER_INFO_SIZE]))
    out.sort(key=lambda c: c["slot"])
    return out


# ---------------------------------------------------------------------------
# login-server
# ---------------------------------------------------------------------------

# src/login/loginclif.cpp:171- の result コード
AC_REFUSE_REASON = {
    0: "未登録の ID", 1: "パスワード不一致", 2: "ID の有効期限切れ",
    3: "サーバから拒否", 4: "GM チームによるブロック", 5: "クライアントのバージョン不一致",
    6: "一時 BAN", 7: "サーバ過密", 8: "同一company からの接続数超過",
    99: "ID が完全に削除済み",
}


def do_login(host: str, port: int, userid: str, password: str,
             verbose: bool, timeout: float = RECV_TIMEOUT) -> dict:
    stream = PacketStream(host, port, COMMON_PACKET_LEN, "login", verbose, timeout)
    with stream:
        # CA_LOGIN 0x0064 <version>.L <id>.24B <passwd>.24B <clienttype>.B
        # src/common/packets.hpp:119-126
        pkt = struct.pack("<HI24s24sB", CA_LOGIN, PACKETVER,
                          userid.encode("ascii").ljust(NAME_LENGTH, b"\x00"),
                          password.encode("ascii").ljust(NAME_LENGTH, b"\x00"),
                          0)
        assert len(pkt) == 55
        stream.send(pkt, "user=%s" % userid)

        cmd, body = stream.expect((AC_ACCEPT_LOGIN, AC_REFUSE_LOGIN, SC_NOTIFY_BAN),
                                  fatal=())
        if cmd == AC_REFUSE_LOGIN:
            err = struct.unpack_from("<I", body, 2)[0]
            raise ProbeError("login 拒否 AC_REFUSE_LOGIN(0x083e) error=%d (%s)"
                             % (err, AC_REFUSE_REASON.get(err, "不明")))
        if cmd == SC_NOTIFY_BAN:
            raise ProbeError("login 拒否 SC_NOTIFY_BAN(0x0081) result=%d" % body[2])

        # AC_ACCEPT_LOGIN 0x0ac4 (PACKETVER >= 20170315) -- src/common/packets.hpp:186-210
        #   packetType.W packetLength.W login_id1.L AID.L login_id2.L last_ip.L
        #   last_login.26B sex.B token.17B  (= 64 バイト) + char_servers[]
        #   sub = ip.L port.W name.20B users.W type.W new.W unknown.128B (= 160 バイト)
        base = 64
        sub = 160
        length = struct.unpack_from("<H", body, 2)[0]
        login_id1, aid, login_id2 = struct.unpack_from("<III", body, 4)
        sex = body[46]
        servers = []
        rest = length - base
        if rest < 0 or rest % sub != 0:
            raise ProbeError("AC_ACCEPT_LOGIN の長さが不正です (len=%d, base=%d, sub=%d)"
                             % (length, base, sub))
        for i in range(rest // sub):
            off = base + i * sub
            ip_raw = body[off:off + 4]
            # loginclif.cpp:137-138 -- ip は htonl(), port は ntows(htons()) なので
            # ip はネットワークバイト順のまま、port はホスト値 (LE) がそのまま入る。
            srv_port = struct.unpack_from("<H", body, off + 4)[0]
            name = decode_cstr(body[off + 6:off + 26])
            users, stype, new_ = struct.unpack_from("<HHH", body, off + 26)
            servers.append({
                "ip": socket.inet_ntoa(ip_raw), "port": srv_port, "name": name,
                "users": users, "type": stype, "new": new_,
            })
        if not servers:
            raise ProbeError("AC_ACCEPT_LOGIN に char-server が 1 件も含まれていません")
        return {
            "account_id": aid, "login_id1": login_id1, "login_id2": login_id2,
            "sex": sex, "char_servers": servers, "trace": stream.trace,
        }


# ---------------------------------------------------------------------------
# char-server
# ---------------------------------------------------------------------------

# src/char/char_clif.cpp:520-527 (chclif_char_delete2_accept_ack のコメント)
HC_DELETE_CHAR3_RESULT = {
    0: "不明なエラー", 1: "成功", 2: "システム設定により削除不可 (パーティ/ギルド/レベル制限)",
    3: "DB エラー、またはキャラクターが見つからない", 4: "削除待ち時間が未経過",
    5: "生年月日が一致しない", 6: "名前が一致しない", 7: "メールアドレスが一致しない",
}
# src/char/char_clif.cpp:508-514 のコメントと chclif_parse_char_delete2_req の実装。
# result=0 は「既に削除予約済み」でも返る (同関数の `if( delete_date )` 分岐)。
HC_DELETE_CHAR3_RESERVED_RESULT = {
    0: "不明なエラー、または既に削除予約済み", 1: "予約成功", 3: "DB エラー",
    4: "ギルド脱退が必要", 5: "パーティ脱退が必要",
}
# src/char/char_clif.cpp:1528- (chclif_createnewchar_refuse)
HC_REFUSE_MAKECHAR_ERROR = {
    0x00: "同名のキャラクターが既に存在する",
    0x01: "年齢制限",
    0x02: "名前に使用できない記号が含まれる",
    0x03: "そのキャラクタースロットは使用できない",
    0xFF: "キャラクター作成が禁止されている",
}


class CharSession:
    """char-server への接続 (0x0065 認証済み)。"""

    def __init__(self, host: str, port: int, login: dict, verbose: bool,
                 timeout: float = RECV_TIMEOUT):
        self.stream = PacketStream(host, port, COMMON_PACKET_LEN, "char", verbose,
                                   timeout)
        self.login = login
        self.char_slots = None
        self.pincode_state = None
        self.chars = []
        self.verbose = verbose

    def close(self) -> None:
        self.stream.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    # -- 0x0065 -------------------------------------------------------------
    def enter(self) -> None:
        s = self.stream
        # CH_ENTER 0x0065 <aid>.L <login_id1>.L <login_id2>.L <unknown>.W <sex>.B
        # src/char/char_clif.cpp:821-828 (chclif_parse_reqtoconnect, 固定 17 バイト)
        pkt = struct.pack("<HIIIHB", CH_ENTER, self.login["account_id"],
                          self.login["login_id1"], self.login["login_id2"],
                          0, self.login["sex"])
        assert len(pkt) == 17
        s.send(pkt)

        # char-server はまず生の account_id 4 バイトを返す
        # (src/char/char_clif.cpp:850-853)
        raw_aid = struct.unpack("<I", s.read_raw(4))[0]
        if raw_aid != self.login["account_id"]:
            raise ProbeError("char-server が返した account_id が一致しません (%d != %d)"
                             % (raw_aid, self.login["account_id"]))
        s.log("recv raw account_id=%d" % raw_aid)

        # 続けて 0x082d -> 0x006b -> 0x09a0 -> 0x020d -> 0x08b9 の順に届く
        # (char_logif.cpp:363-366 -> char_clif.cpp:477-489)
        got_accept = False
        for _ in range(16):
            cmd, body = s.read_packet()
            if cmd == HC_ACCEPT_ENTER2:
                self.char_slots = body[7]  # producible_slot
            elif cmd == HC_ACCEPT_ENTER:
                # base = 27 (packetType.W packetLength.W total.B premium_start.B
                #            premium_end.B extension.20B) -- packets.hpp:252-262
                self.chars = parse_character_list(body, 27)
                got_accept = True
            elif cmd == HC_SECOND_PASSWD_LOGIN:
                self.pincode_state = struct.unpack_from("<H", body, 10)[0]
                break
            elif cmd in (HC_REFUSE_ENTER, SC_NOTIFY_BAN):
                raise ProbeError("char-server に拒否されました %s result=%d"
                                 % (pname(cmd), body[2]))
        if not got_accept:
            raise ProbeError("char-server から HC_ACCEPT_ENTER(0x006b) が届きませんでした")
        if self.pincode_state not in (None, 0):
            raise ProbeError(
                "PIN コードが要求されました (HC_SECOND_PASSWD_LOGIN state=%d)。"
                "char_conf の pincode_enabled を確認してください" % self.pincode_state)

    # -- 0x09a1 -> 0x0b72 ---------------------------------------------------
    def charlist(self) -> list:
        s = self.stream
        s.send(struct.pack("<H", CH_CHARLIST_REQ))
        _, body = s.expect(HC_ACK_CHARINFO_PER_PAGE)
        # packets.hpp:613-619: packetType.W packetLength.W characters[] (base = 4)
        chars = parse_character_list(body, 4)
        # chclif_mmo_send099d() は count == 3 のときだけ、同じパケットを
        # キャラクター 0 件で「もう 1 回」送る (src/char/char_clif.cpp:459-465)。
        # 必ず来ると分かっているので、時間任せに読み捨てるのではなく
        # 通常のタイムアウトで確定的に 1 個読む。
        # (時間任せにすると RTT の大きい回線で取りこぼし、その残骸が
        #  次の 0x09a1 の応答として読まれて「0 体」に化ける。)
        if len(chars) == 3:
            _, extra = s.expect(HC_ACK_CHARINFO_PER_PAGE)
            if len(extra) != 4:
                raise ProbeError(
                    "3 体時に再送される 0x0b72 が空ではありません (len=%d)" % len(extra))
            s.log("3 体時の再送 0x0b72 (空) を読み捨てました")
        self.chars = chars
        return self.chars

    # -- 0x0a39 -> 0x0b6f / 0x006e -----------------------------------------
    def make_char(self, name: str, slot: int, hair_style: int = 1,
                  hair_color: int = 1) -> dict:
        s = self.stream
        # CH_MAKE_CHAR 0x0a39 (PACKETVER >= 20151001) -- packets.hpp:133-145
        #   name.24B slot.B hair_color.W hair_style.W job.L sex.B
        pkt = struct.pack("<H24sBHHIB", CH_MAKE_CHAR, encode_name(name), slot,
                          hair_color, hair_style, JOB_NOVICE,
                          SEX_MALE if self.login["sex"] == SEX_MALE else SEX_FEMALE)
        assert len(pkt) == 36
        s.send(pkt, "name=%r slot=%d" % (name, slot))
        cmd, body = s.expect((HC_ACCEPT_MAKECHAR, HC_REFUSE_MAKECHAR))
        if cmd == HC_REFUSE_MAKECHAR:
            err = body[2]
            raise ProbeError("キャラクター作成を拒否されました "
                             "HC_REFUSE_MAKECHAR(0x006e) error=0x%02x (%s)"
                             % (err, HC_REFUSE_MAKECHAR_ERROR.get(err, "不明")))
        return parse_character_info(body[2:2 + CHARACTER_INFO_SIZE])

    # -- 0x0827 -> 0x0828 ---------------------------------------------------
    def delete_reserve(self, char_id: int) -> dict:
        s = self.stream
        s.send(struct.pack("<HI", CH_DELETE_CHAR3_RESERVED, char_id),
               "char_id=%d" % char_id)
        _, body = s.expect(HC_DELETE_CHAR3_RESERVED)
        cid, result, date = struct.unpack_from("<IiI", body, 2)
        if cid != char_id:
            raise ProbeError("0x0828 の char_id が一致しません (%d != %d)" % (cid, char_id))
        return {
            "char_id": cid, "result": result, "date": date,
            "result_text": HC_DELETE_CHAR3_RESERVED_RESULT.get(result, "不明"),
        }

    # -- 0x082b -> 0x082c ---------------------------------------------------
    def delete_cancel(self, char_id: int) -> dict:
        s = self.stream
        s.send(struct.pack("<HI", CH_DELETE_CHAR3_CANCEL, char_id),
               "char_id=%d" % char_id)
        _, body = s.expect(HC_DELETE_CHAR3_CANCEL)
        cid, result = struct.unpack_from("<Ii", body, 2)
        return {"char_id": cid, "result": result}

    # -- 0x0829 -> 0x082a ---------------------------------------------------
    def delete_commit(self, char_id: int, birthdate: str) -> dict:
        s = self.stream
        # CH_DELETE_CHAR3 0x0829 <char id>.L <birthdate>.6B ("YYMMDD" の ASCII)
        # 受け側は "YY-MM-DD" を組み立てて login.birthdate の 3 文字目以降と比較する
        # (src/char/char_clif.cpp:1180-1200 / chclif_delchar_check)
        yymmdd = birthdate[2:].encode("ascii")
        assert len(yymmdd) == 6
        s.send(struct.pack("<HI6s", CH_DELETE_CHAR3, char_id, yymmdd),
               "char_id=%d birthdate=%s" % (char_id, birthdate))
        # 成功時は 0x082a より先に chclif_mmo_char_send() の一式が飛んでくる
        # (src/char/char_clif.cpp:552-560)
        _, body = s.expect(HC_DELETE_CHAR3)
        cid, result = struct.unpack_from("<Ii", body, 2)
        if cid != char_id:
            raise ProbeError("0x082a の char_id が一致しません (%d != %d)" % (cid, char_id))
        return {
            "char_id": cid, "result": result,
            "result_text": HC_DELETE_CHAR3_RESULT.get(result, "不明"),
        }

    # -- 0x0066 -> 0x0ac5 ---------------------------------------------------
    def select_char(self, slot: int) -> dict:
        s = self.stream
        s.send(struct.pack("<HB", CH_SELECT_CHAR, slot), "slot=%d" % slot)
        cmd, body = s.expect((HC_NOTIFY_ZONESVR, HC_NOTIFY_ACCESSIBLE_MAPNAME))
        if cmd == HC_NOTIFY_ACCESSIBLE_MAPNAME:
            raise ProbeError("マップサーバが見つからず 0x0840 "
                             "(HC_NOTIFY_ACCESSIBLE_MAPNAME) が返りました")
        # HC_NOTIFY_ZONESVR 0x0ac5 (PACKETVER >= 20170315) -- packets.hpp:299-308
        #   CID.L mapname.16B ip.L port.W domain.128B
        cid = struct.unpack_from("<I", body, 2)[0]
        mapname = decode_cstr(body[6:22])
        ip = socket.inet_ntoa(body[22:26])
        port = struct.unpack_from("<H", body, 26)[0]
        return {"char_id": cid, "map": mapname, "ip": ip, "port": port}


# ---------------------------------------------------------------------------
# map-server
# ---------------------------------------------------------------------------

class MapSession:
    """map-server への接続。入場から NPC 会話・ログアウトまでを面倒みる。

    受信したパケットは PacketStream.observer 経由で全部横から覗いて、
    ユニット一覧 / 会話文 / ステータス更新 / マップ移動を記録していく。
    """

    def __init__(self, zone: dict, login: dict, fallback_host: str,
                 verbose: bool, timeout: float = RECV_TIMEOUT):
        self.login = login
        self.zone = dict(zone)
        self.timeout = timeout
        self.info = {"zone": dict(zone), "connected_to": None}
        host, port = zone["ip"], zone["port"]
        try:
            self.stream = PacketStream(host, port, MAP_PACKET_LEN, "map", verbose,
                                       timeout)
        except OSError as exc:
            if host == fallback_host:
                raise ProbeError("map-server %s:%d に接続できません (%s)"
                                 % (host, port, exc))
            self.stream = PacketStream(fallback_host, port, MAP_PACKET_LEN, "map",
                                       verbose, timeout)
            host = fallback_host
            self.info["fallback"] = ("0x0ac5 の ip %s に繋がらなかったので --host を使用"
                                     % zone["ip"])
        self.info["connected_to"] = "%s:%d" % (host, port)

        self.units = {}            # AID -> parse_unit_packet() の結果
        self.unit_errors = []      # レイアウトが合わなかったスポーン系パケット
        self.dialog = []           # 会話ログ (UTF-8 にデコード済み)
        self.stat_updates = []     # ZC_PAR_CHANGE 系
        self.map_moves = []        # ZC_NPCACK_MAPMOVE
        self.units_at_entry = {}   # enter() 完了時点のユニット一覧のスナップショット
        self.phase = "enter"
        self.stream.observer = self._observe

    # -- 観測 ---------------------------------------------------------------
    def _observe(self, cmd: int, body: bytes) -> None:
        if cmd in UNIT_PACKET_LAYOUT:
            unit = parse_unit_packet(cmd, body)
            if "error" in unit:
                self.unit_errors.append(unit)
            else:
                self.units[unit["aid"]] = unit
            return
        if cmd == ZC_SAY_DIALOG:
            self.dialog.append({"phase": self.phase, "type": "mes",
                                "npc_id": struct.unpack_from("<I", body, 4)[0],
                                "text": decode_cp932(body[8:])})
            return
        if cmd == ZC_WAIT_DIALOG:
            self.dialog.append({"phase": self.phase, "type": "next",
                                "npc_id": struct.unpack_from("<I", body, 2)[0]})
            return
        if cmd == ZC_CLOSE_DIALOG:
            self.dialog.append({"phase": self.phase, "type": "close",
                                "npc_id": struct.unpack_from("<I", body, 2)[0]})
            return
        if cmd == ZC_MENU_LIST:
            # menu は ':' 区切りの CP932 文字列。CP932 の 2 バイト目は 0x40 以上なので
            # ':' (0x3a) と衝突しないが、念のためデコードしてから分割する。
            self.dialog.append({"phase": self.phase, "type": "menu",
                                "npc_id": struct.unpack_from("<I", body, 4)[0],
                                "options": decode_cp932(body[8:]).split(":")})
            return
        if cmd == ZC_NPCACK_MAPMOVE:
            self.map_moves.append({
                "phase": self.phase,
                "map": decode_cstr(body[2:18]),
                "x": struct.unpack_from("<H", body, 18)[0],
                "y": struct.unpack_from("<H", body, 20)[0],
            })
            return
        if cmd in (ZC_PAR_CHANGE, ZC_LONGPAR_CHANGE):
            var, val = struct.unpack_from("<Hi", body, 2)
            self._add_stat(cmd, var, val)
            return
        if cmd == ZC_LONGLONGPAR_CHANGE:
            var, val = struct.unpack_from("<Hq", body, 2)
            self._add_stat(cmd, var, val)
            return
        if cmd == ZC_STATUS_CHANGE:
            var = struct.unpack_from("<H", body, 2)[0]
            self._add_stat(cmd, var, body[4])
            return
        if cmd == ZC_SPRITE_CHANGE:
            aid, look = struct.unpack_from("<IB", body, 2)
            val = struct.unpack_from("<I", body, 7)[0]
            if look == LOOK_BASE:
                # 転職すると clif_changelook(LOOK_BASE) で新しい job が飛んでくる
                self.stat_updates.append({
                    "phase": self.phase, "packet": pname(cmd),
                    "name": "LOOK_BASE(class)", "aid": aid, "value": val,
                    "job_name": JOB_NAMES.get(val),
                })
            return

    def _add_stat(self, cmd: int, var: int, val: int) -> None:
        self.stat_updates.append({
            "phase": self.phase, "packet": pname(cmd),
            "sp": var, "name": SP_NAMES.get(var, "SP_%d" % var), "value": val,
        })

    def stat_summary(self) -> dict:
        """SP ごとに「最後に届いた値」だけを残した要約。"""
        out = {}
        for ev in self.stat_updates:
            out[ev["name"]] = ev["value"]
        return out

    # -- 接続の後始末 --------------------------------------------------------
    def close(self) -> None:
        self.stream.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    # -- 0x0436 -> 0x0283 -> 0x02eb -> 0x007d -------------------------------
    def enter(self) -> dict:
        s = self.stream
        # CZ_ENTER 0x0436 (23 バイト, pos=2,6,10,14,22)
        # clif_parse_WantToConnection_sub() は RFIFOREST(fd) == packet_db[cmd].len を
        # 要求するので、この 23 バイトだけを単独で送る (先頭に aid は付けない)。
        buf = bytearray(CZ_ENTER_LEN)
        struct.pack_into("<H", buf, 0, CZ_ENTER)
        struct.pack_into("<I", buf, CZ_ENTER_POS[0], self.login["account_id"])
        struct.pack_into("<I", buf, CZ_ENTER_POS[1], self.zone["char_id"])
        struct.pack_into("<I", buf, CZ_ENTER_POS[2], self.login["login_id1"])
        struct.pack_into("<I", buf, CZ_ENTER_POS[3],
                         int(time.time() * 1000) & 0xFFFFFFFF)
        struct.pack_into("<B", buf, CZ_ENTER_POS[4], self.login["sex"])
        s.send(bytes(buf), "char_id=%d" % self.zone["char_id"])

        cmd, body = s.expect((ZC_AID, ZC_REFUSE_ENTER))
        if cmd == ZC_REFUSE_ENTER:
            raise ProbeError("map-server に拒否されました ZC_REFUSE_ENTER(0x0074) error=%d"
                             % body[2])
        self.info["zc_aid"] = struct.unpack_from("<I", body, 2)[0]

        _, body = s.expect(ZC_ACCEPT_ENTER)
        # ZC_ACCEPT_ENTER 0x02eb <start time>.L <position>.3B <x size>.B <y size>.B <font>.W
        pos = body[6:9]
        x = (pos[0] << 2) | (pos[1] >> 6)
        y = ((pos[1] & 0x3F) << 4) | (pos[2] >> 4)
        self.info["accept_enter"] = {"x": x, "y": y, "map": self.zone["map"]}

        self.info["drained_after_loadend"] = self.loadend()
        # warp した後は prontera のユニットも self.units に混ざるので、
        # 「入場時に見えていたユニット」をここで固定しておく。
        self.units_at_entry = dict(self.units)
        return self.info

    def loadend(self) -> int:
        """CZ_NOTIFY_ACTORINIT を送って、入場直後の奔流を読み切る。

        送らないと sd->prev が nullptr のままで他のパケットが一切処理されない
        (src/map/clif.cpp clif_parse_LoadEndAck は sd->prev != nullptr で早期 return
        するので、warp で map_delblock された後はもう一度送る必要がある)。
        流れてくる数は決まっていないので「idle 秒だけ何も来なくなったら終わり」で待つ。
        """
        self.stream.send(struct.pack("<H", CZ_NOTIFY_ACTORINIT))
        return self.stream.drain_until_idle(
            idle=max(0.6, self.timeout / 10.0), max_seconds=self.timeout * 2)

    # -- NPC 探索 -----------------------------------------------------------
    def find_npc(self, name_prefix: str) -> dict:
        """名前が name_prefix で始まるユニットを 1 体返す (CP932 のバイト列で比較)。

        視界外にいると 1 体も届かない。その場合は CZ_REQNAME を撃って探しに行ったり
        せず、素直にエラーにする。
        """
        prefix = name_prefix.encode("cp932")

        def hit_list():
            return [u for u in self.units.values()
                    if bytes.fromhex(u["name_cp932_hex"]).startswith(prefix)]

        hits = hit_list()
        if not hits:
            # マップのロードが遅いとスポーン系パケットが drain_until_idle の
            # idle 判定より後に届くことがある。もう一度だけ長めに待つ。
            self.stream.drain_until_idle(idle=max(2.0, self.timeout / 4.0),
                                         max_seconds=self.timeout * 2)
            self.units_at_entry = dict(self.units)
            hits = hit_list()
        if not hits:
            seen = sorted({u["name"] for u in self.units.values() if u["name"]})
            raise ProbeError(
                "スポーン系パケットに %r で始まるユニットがいませんでした "
                "(受信したユニット %d 体: %s)"
                % (name_prefix, len(self.units), ", ".join(seen) or "なし"))
        if len(hits) > 1:
            hits.sort(key=lambda u: u["aid"])
        return hits[0]

    # -- 会話 ---------------------------------------------------------------
    def talk_training_skip(self, npc_aid: int, mode: str,
                           cancel_job: str = "swordman") -> dict:
        """冒険者支援員の会話を最後まで進める。

        mode: swordman/archer/mage/acolyte/merchant/thief = その職に転職する
              decline = 7 番「まだ修練場を続ける」を選ぶ
              cancel  = 職を選んだあと確認で「いいえ」を選ぶ
        """
        s = self.stream
        self.phase = "talk"
        outcome = {"npc_aid": npc_aid, "mode": mode, "menus": [], "choices": []}
        # 既存キャラで入り直すと入場時にも ZC_NPCACK_MAPMOVE が飛んでくる
        # (clif_parse_LoadEndAck の connect_new でない側で clif_changemap を呼ぶため)。
        # 会話が起こした warp だけを見たいので、ここまでの分は数えない。
        moves_before = len(self.map_moves)

        # CZ_CONTACTNPC 0x0090 <naid>.L <type>.B  (type=1: クライアントが送る値)
        s.send(struct.pack("<HIB", CZ_CONTACTNPC, npc_aid, 1),
               "naid=%d" % npc_aid)

        menu_no = 0
        for _ in range(200):
            cmd, body = s.expect(
                (ZC_SAY_DIALOG, ZC_WAIT_DIALOG, ZC_MENU_LIST, ZC_CLOSE_DIALOG),
                fatal=(ZC_REFUSE_ENTER,))
            if cmd == ZC_SAY_DIALOG:
                continue
            if cmd == ZC_WAIT_DIALOG:
                naid = struct.unpack_from("<I", body, 2)[0]
                # CZ_REQ_NEXT_SCRIPT 0x00b9 <naid>.L
                s.send(struct.pack("<HI", CZ_REQ_NEXT_SCRIPT, naid), "next")
                self.dialog[-1]["replied"] = "CZ_REQ_NEXT_SCRIPT(0x00b9)"
                continue
            if cmd == ZC_MENU_LIST:
                naid = struct.unpack_from("<I", body, 4)[0]
                options = decode_cp932(body[8:]).split(":")
                menu_no += 1
                pick = self._pick_menu(menu_no, mode, options, cancel_job)
                outcome["menus"].append({"no": menu_no, "options": options})
                outcome["choices"].append({
                    "menu_no": menu_no, "selected": pick,
                    "label": options[pick - 1] if pick <= len(options) else None,
                })
                # CZ_CHOOSE_MENU 0x00b8 <naid>.L <num>.B (1 始まり)
                s.send(struct.pack("<HIB", CZ_CHOOSE_MENU, naid, pick),
                       "menu%d=%d" % (menu_no, pick))
                self.dialog[-1]["replied"] = "CZ_CHOOSE_MENU(0x00b8) num=%d" % pick
                continue
            # ZC_CLOSE_DIALOG: close / close2 のどちらでも来る。
            # close2 の場合はここで返す 0x0146 がスクリプトの続き
            # (savepoint / warp) を動かすトリガーになる。
            naid = struct.unpack_from("<I", body, 2)[0]
            s.send(struct.pack("<HI", CZ_CLOSE_DIALOG, naid), "close")
            self.dialog[-1]["replied"] = "CZ_CLOSE_DIALOG(0x0146)"
            break
        else:
            raise ProbeError("会話が 200 パケット進んでも終わりませんでした")

        self.phase = "after_close"
        outcome["drained_after_close"] = self.stream.drain_until_idle(
            idle=max(0.8, self.timeout / 8.0), max_seconds=self.timeout * 2)
        # warp されたらクライアントは新しいマップを読み込み直して
        # もう一度 CZ_NOTIFY_ACTORINIT を送る
        moves = self.map_moves[moves_before:]
        if moves:
            outcome["map_move"] = moves[-1]
            self.phase = "after_warp"
            outcome["drained_after_warp"] = self.loadend()
        else:
            outcome["map_move"] = None
        outcome["dialog"] = [d for d in self.dialog if d["phase"] != "enter"]
        return outcome

    @staticmethod
    def _pick_menu(menu_no: int, mode: str, options: list, cancel_job: str) -> int:
        if menu_no == 1:
            if mode == "decline":
                pick = TRAINING_SKIP_DECLINE
            elif mode == "cancel":
                pick = TRAINING_SKIP_JOBS[cancel_job][0]
            else:
                pick = TRAINING_SKIP_JOBS[mode][0]
        elif menu_no == 2:
            pick = 2 if mode == "cancel" else 1
        else:
            raise ProbeError("想定外の %d 個目の選択肢が出ました: %s"
                             % (menu_no, " / ".join(options)))
        if pick > len(options):
            raise ProbeError("選択肢 %d 番を選ぼうとしましたが %d 個しかありません (%s)"
                             % (pick, len(options), " / ".join(options)))
        return pick

    # -- 0x018a -> 0x018b ---------------------------------------------------
    def quit(self) -> int:
        """CZ_REQUEST_QUIT でログアウトする。

        map-server はここで初めて char-server 経由で DB に書き戻す
        (map_quit -> chrif_save -> char_save)。DB を読むのは必ずこの後。
        """
        self.phase = "quit"
        quit_result = None
        for _ in range(6):
            self.stream.send(struct.pack("<HH", CZ_REQUEST_QUIT, 0))
            _, body = self.stream.expect(ZC_ACK_REQ_DISCONNECT)
            quit_result = struct.unpack_from("<H", body, 2)[0]
            if quit_result == 0:
                break
            # result 1 = prevent_logout により今は落とせない (既定 10 秒)
            time.sleep(2.0)
        self.info["quit_result"] = quit_result
        if quit_result != 0:
            raise ProbeError("CZ_REQUEST_QUIT に対する 0x018b が result=%s でした"
                             % quit_result)
        return quit_result


def enter_map(zone: dict, login: dict, fallback_host: str,
              verbose: bool, timeout: float = RECV_TIMEOUT) -> dict:
    """map に入って即 quit する (--enter-map 用)。"""
    session = MapSession(zone, login, fallback_host, verbose, timeout)
    with session:
        session.enter()
        session.quit()
    return session.info


# ---------------------------------------------------------------------------
# 出力ヘルパ
# ---------------------------------------------------------------------------

def fmt_delete_date(seconds: int) -> str:
    """CHARACTER_INFO.DelRevDate の表示。

    PACKETVER_CHAR_DELETEDATE が有効なので、この値は「削除確定までの残り秒」
    (char.cpp:1845 `p.delete_date ? TOL(p.delete_date - time(nullptr)) : 0`)。
    char_del_delay: 0 のサーバでは予約した瞬間から 0 以下になるため、
    0 は「未予約」と「予約済みで確定可能」の区別がつかない点に注意。
    """
    if seconds == 0:
        return "-"
    return "予約済み (%s)" % fmt_reservation(seconds)


def fmt_reservation(seconds: int) -> str:
    """削除予約の「確定できる時刻」だけを表す文字列。"""
    if seconds < 0:
        return "%d 秒前に確定可能" % (-seconds)
    if seconds == 0:
        return "確定可能"
    when = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
    return "あと %d 秒 / %s" % (seconds, when.strftime("%Y-%m-%d %H:%M:%S"))


def print_charlist(title: str, chars: list) -> None:
    print("  %s: %d 体" % (title, len(chars)))
    if not chars:
        print("    (キャラクターなし)")
        return
    print("    %-9s %-5s %-24s %-10s %s"
          % ("char_id", "slot", "name", "level", "delete_date"))
    for c in chars:
        print("    %-9d %-5d %-24s %-10d %s"
              % (c["char_id"], c["slot"], c["name"], c["base_level"],
                 fmt_delete_date(c["delete_date"])))


def pick_free_slot(chars: list, char_slots: int) -> int:
    used = {c["slot"] for c in chars}
    for slot in range(char_slots or MAX_CHARS):
        if slot not in used:
            return slot
    raise ProbeError("空きスロットがありません (使用中: %s)" % sorted(used))


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="rAthena のキャラクター削除 / NPC 会話が正規経路で動くかを"
                    "検証する最小クライアント",
        epilog="パスワードは環境変数 RO_PROBE_PASSWORD から読み込みます "
               "(引数・ログ・JSON には出力しません)。")
    p.add_argument("--host", required=True, help="login-server のホスト/IP")
    p.add_argument("--login-port", type=int, default=6900, help="login-server のポート (既定 6900)")
    p.add_argument("--user", required=True, help="アカウント名 (login.userid)")
    p.add_argument("--birthdate", required=True,
                   help="login.birthdate を YYYYMMDD で指定 (0x0829 に YYMMDD を載せる)")
    p.add_argument("--name", help="作成/削除の対象キャラクター名")
    p.add_argument("--slot", type=int, help="作成先スロット (省略時は空きスロット)")
    p.add_argument("--create", action="store_true", help="--name のキャラクターを作成する")
    p.add_argument("--delete", action="store_true",
                   help="対象キャラクターを 0x0827 -> 0x0829 で削除する")
    p.add_argument("--cancel-reservation", action="store_true",
                   help="--name のキャラクターの削除予約を 0x082b で取り消して結果を表示する")
    p.add_argument("--enter-map", action="store_true",
                   help="残っているキャラクター 1 体で map まで入って即 quit する")
    p.add_argument("--npc-skip", metavar="MODE",
                   choices=sorted(TRAINING_SKIP_JOBS) + ["decline", "cancel"],
                   help="修練場の NPC「冒険者支援員」に話しかけて一次職転職を検証する。"
                        "MODE = %s / decline (7 番『まだ修練場を続ける』) / "
                        "cancel (確認で『いいえ』)"
                        % " | ".join(sorted(TRAINING_SKIP_JOBS)))
    p.add_argument("--npc-skip-cancel-job", metavar="JOB", default="swordman",
                   choices=sorted(TRAINING_SKIP_JOBS),
                   help="--npc-skip cancel のときに 7 択で選ぶ職 (既定 swordman)")
    p.add_argument("--keep", action="store_true", help="削除を行わない (--delete を無効化)")
    p.add_argument("--timeout", type=float, default=RECV_TIMEOUT,
                   help="各 recv のタイムアウト秒 (既定 %.0f)。RTT の大きい回線では増やす"
                        % RECV_TIMEOUT)
    p.add_argument("--json", metavar="PATH", help="結果を JSON で書き出す")
    p.add_argument("--verbose", "-v", action="store_true", help="パケットトレースを stderr に出す")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    password = os.environ.get("RO_PROBE_PASSWORD")
    if not password:
        print("エラー: 環境変数 RO_PROBE_PASSWORD が設定されていません", file=sys.stderr)
        return 2
    if len(args.birthdate) != 8 or not args.birthdate.isdigit():
        print("エラー: --birthdate は YYYYMMDD の 8 桁で指定してください", file=sys.stderr)
        return 2
    if args.create and not args.name:
        print("エラー: --create には --name が必要です", file=sys.stderr)
        return 2
    if args.cancel_reservation and not args.name:
        print("エラー: --cancel-reservation には --name が必要です", file=sys.stderr)
        return 2
    if args.npc_skip and args.enter_map:
        print("エラー: --npc-skip と --enter-map は同時に指定できません "
              "(--npc-skip 自身が map まで入ります)", file=sys.stderr)
        return 2
    if args.npc_skip and args.delete and not args.keep:
        print("エラー: --npc-skip と --delete は同時に指定できません", file=sys.stderr)
        return 2
    if args.timeout <= 0:
        print("エラー: --timeout は正の秒数で指定してください", file=sys.stderr)
        return 2

    report = {
        "started_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "packetver": PACKETVER,
        "target": {"host": args.host, "login_port": args.login_port,
                   "user": args.user, "birthdate": args.birthdate},
        "options": {"create": args.create, "delete": args.delete,
                    "enter_map": args.enter_map, "keep": args.keep,
                    "cancel_reservation": args.cancel_reservation,
                    "npc_skip": args.npc_skip,
                    "npc_skip_cancel_job": args.npc_skip_cancel_job,
                    "name": args.name, "slot": args.slot,
                    "timeout": args.timeout},
        "steps": [],
        "ok": False,
    }

    def step(name: str, ok: bool, **detail) -> None:
        entry = {"step": name, "ok": ok}
        entry.update(detail)
        report["steps"].append(entry)

    exit_code = 0
    try:
        # --- 1. login ------------------------------------------------------
        print("[1] login-server %s:%d に CA_LOGIN(0x0064) を送ります (user=%s)"
              % (args.host, args.login_port, args.user))
        login = do_login(args.host, args.login_port, args.user, password,
                         args.verbose, args.timeout)
        srv = login["char_servers"][0]
        print("  AC_ACCEPT_LOGIN(0x0ac4) 受信: account_id=%d sex=%d char-server=%s (%s:%d)"
              % (login["account_id"], login["sex"], srv["name"], srv["ip"], srv["port"]))
        step("login", True, account_id=login["account_id"], sex=login["sex"],
             char_servers=login["char_servers"])

        # char-server の IP はサーバ設定由来なので、届かない場合は --host を使う
        char_host, char_port = srv["ip"], srv["port"]

        # --- 2. char-server 接続 & 一覧 ------------------------------------
        print("[2] char-server %s:%d に CH_ENTER(0x0065) を送ります" % (char_host, char_port))
        try:
            session = CharSession(char_host, char_port, login, args.verbose,
                                  args.timeout)
        except OSError:
            if char_host == args.host:
                raise
            print("  %s に接続できないので --host (%s) を使います" % (char_host, args.host))
            char_host = args.host
            session = CharSession(char_host, char_port, login, args.verbose,
                                  args.timeout)

        with session:
            session.enter()
            print("  HC_ACCEPT_ENTER(0x006b) 受信 / "
                  "HC_SECOND_PASSWD_LOGIN(0x08b9) state=%s (0=PIN 無効)"
                  % session.pincode_state)
            chars = session.charlist()
            print("  CH_CHARLIST_REQ(0x09a1) -> HC_ACK_CHARINFO_PER_PAGE(0x0b72)")
            print_charlist("初期キャラクター一覧", chars)
            step("charlist_initial", True, pincode_state=session.pincode_state,
                 char_slots=session.char_slots, chars=chars)

            target = None
            if args.name:
                target = next((c for c in chars if c["name"] == args.name), None)

            # --- 2.5 削除予約の取り消し -------------------------------------
            if args.cancel_reservation:
                if target is None:
                    raise ProbeError("--cancel-reservation には既存キャラクターの "
                                     "--name が必要です")
                print("[2.5] CH_DELETE_CHAR3_CANCEL(0x082b) で削除予約を取り消します "
                      "(char_id=%d name=%r 現在の予約=%s)"
                      % (target["char_id"], target["name"],
                         fmt_delete_date(target["delete_date"])))
                cancel = session.delete_cancel(target["char_id"])
                print("  HC_DELETE_CHAR3_CANCEL(0x082c): result=%d (1=成功 / 2=DB エラー"
                      "・キャラクター未検出)" % cancel["result"])
                step("cancel_reservation", cancel["result"] == 1, **cancel)
                if cancel["result"] != 1:
                    raise ProbeError("削除予約の取り消しに失敗しました (result=%d)"
                                     % cancel["result"])
                chars = session.charlist()
                print_charlist("取り消し後のキャラクター一覧", chars)
                step("charlist_after_cancel", True, chars=chars)
                target = next((c for c in chars if c["name"] == args.name), None)

            # --- 3. 作成 ---------------------------------------------------
            if args.create:
                if target is not None:
                    raise ProbeError("キャラクター %r は既に存在します (char_id=%d)。"
                                     "--create をやめるか別名を指定してください"
                                     % (args.name, target["char_id"]))
                slot = args.slot if args.slot is not None else \
                    pick_free_slot(chars, session.char_slots)
                print("[3] CH_MAKE_CHAR(0x0a39) でキャラクターを作成します "
                      "(name=%r slot=%d, CP932 %d バイト)"
                      % (args.name, slot, len(args.name.encode("cp932"))))
                created = session.make_char(args.name, slot)
                print("  HC_ACCEPT_MAKECHAR(0x0b6f) 受信: char_id=%d slot=%d name=%r map=%s"
                      % (created["char_id"], created["slot"], created["name"],
                         created["map"]))
                step("create", True, character=created)
                chars = session.charlist()
                print_charlist("作成後のキャラクター一覧", chars)
                step("charlist_after_create", True, chars=chars)
                target = next((c for c in chars if c["char_id"] == created["char_id"]), None)

            # --- 4. 削除 ---------------------------------------------------
            do_delete = args.delete and not args.keep
            if args.delete and args.keep:
                print("[4] --keep が指定されたので削除は行いません")
                step("delete", True, skipped="--keep")
            elif do_delete:
                if target is None:
                    raise ProbeError("削除対象が決まりません。"
                                     "--name に既存キャラクター名を指定するか "
                                     "--create を併用してください")
                cid = target["char_id"]
                if target["delete_date"] != 0:
                    # 実クライアントも予約済みのキャラには 0x0827 を送らない。
                    # 送ると chclif_parse_char_delete2_req の `if( delete_date )`
                    # 分岐で result=0 が返るだけ (char_clif.cpp)。
                    print("[4] 既に削除予約済み（予約日時 %s）なので 0x0827 を省略して "
                          "0x0829 を送ります (char_id=%d name=%r)"
                          % (fmt_reservation(target["delete_date"]), cid, target["name"]))
                    step("delete_reserve", True, char_id=cid,
                         skipped="既に削除予約済みのため 0x0827 を省略",
                         delete_date=target["delete_date"])
                else:
                    print("[4] CH_DELETE_CHAR3_RESERVED(0x0827) で削除予約します "
                          "(char_id=%d name=%r)" % (cid, target["name"]))
                    reserved = session.delete_reserve(cid)
                    print("  HC_DELETE_CHAR3_RESERVED(0x0828): result=%d (%s) date=%d"
                          % (reserved["result"], reserved["result_text"],
                             reserved["date"]))
                    if reserved["result"] == 0:
                        # char_del_delay: 0 のサーバでは一覧の delete_date が
                        # 0 に見えるので、ここで初めて予約済みと分かることがある。
                        print("  result=0 は「既に削除予約済み」なので、"
                              "そのまま 0x0829 に進みます")
                        step("delete_reserve", True, already_reserved=True, **reserved)
                    elif reserved["result"] != 1:
                        step("delete_reserve", False, **reserved)
                        raise ProbeError("削除予約が失敗しました (result=%d %s)"
                                         % (reserved["result"], reserved["result_text"]))
                    else:
                        step("delete_reserve", True, **reserved)

                print("  CH_DELETE_CHAR3(0x0829) で削除を確定します (birthdate=%s -> %s)"
                      % (args.birthdate, args.birthdate[2:]))
                committed = session.delete_commit(cid, args.birthdate)
                print("  HC_DELETE_CHAR3(0x082a): result=%d (%s)"
                      % (committed["result"], committed["result_text"]))
                step("delete_commit", committed["result"] == 1, **committed)
                if committed["result"] != 1:
                    # 予約したままだと後続の検証がややこしいのでキャンセルしておく
                    cancel = session.delete_cancel(cid)
                    print("  削除予約を CH_DELETE_CHAR3_CANCEL(0x082b) で取り消しました "
                          "(result=%d)" % cancel["result"])
                    step("delete_cancel", True, **cancel)
                    raise ProbeError("削除が拒否されました (result=%d %s)"
                                     % (committed["result"], committed["result_text"]))

                chars = session.charlist()
                print_charlist("削除後のキャラクター一覧", chars)
                gone = all(c["char_id"] != cid for c in chars)
                print("  char_id=%d が一覧から消えたか: %s" % (cid, "YES" if gone else "NO"))
                step("charlist_after_delete", gone, chars=chars, deleted_char_id=cid)
                if not gone:
                    raise ProbeError("削除したはずの char_id=%d がまだ一覧に残っています" % cid)
                target = None

            # --- 5. NPC 会話 (--npc-skip) -----------------------------------
            if args.npc_skip:
                alive = [c for c in chars if c["delete_date"] == 0]
                if args.name:
                    pick = next((c for c in alive if c["name"] == args.name), None)
                    if pick is None:
                        raise ProbeError("--npc-skip の対象 %r が一覧にいません" % args.name)
                elif target is not None:
                    pick = target
                elif alive:
                    pick = alive[0]
                else:
                    raise ProbeError("--npc-skip に使えるキャラクターがいません")

                print("[5] CH_SELECT_CHAR(0x0066) slot=%d (name=%r) で map に入り、"
                      "NPC %r に話しかけます (mode=%s)"
                      % (pick["slot"], pick["name"], TRAINING_SKIP_NPC_NAME,
                         args.npc_skip))
                zone = session.select_char(pick["slot"])
                print("  HC_NOTIFY_ZONESVR(0x0ac5): char_id=%d map=%s -> %s:%d"
                      % (zone["char_id"], zone["map"], zone["ip"], zone["port"]))

                msession = MapSession(zone, login, args.host, args.verbose,
                                      args.timeout)
                with msession:
                    msession.enter()
                    print("  ZC_ACCEPT_ENTER(0x02eb) 受信: map=%s (x=%d, y=%d) / "
                          "スポーン系パケットで %d ユニット観測"
                          % (msession.info["accept_enter"]["map"],
                             msession.info["accept_enter"]["x"],
                             msession.info["accept_enter"]["y"],
                             len(msession.units_at_entry)))
                    if msession.unit_errors:
                        for err in msession.unit_errors[:3]:
                            print("  警告: %s" % err["error"])
                    npc = msession.find_npc(TRAINING_SKIP_NPC_NAME)
                    print("  NPC を発見: AID=%d name=%r objecttype=0x%x(%s) "
                          "job=%d pos=(%s,%s)"
                          % (npc["aid"], npc["name"], npc["objecttype"],
                             npc["objecttype_name"], npc["job"],
                             npc.get("x"), npc.get("y")))

                    talk = msession.talk_training_skip(
                        npc["aid"], args.npc_skip, args.npc_skip_cancel_job)
                    print("  --- 受信した会話 (CP932 -> UTF-8) ---")
                    for ev in talk["dialog"]:
                        reply = ("  -> %s を返しました" % ev["replied"]
                                 if ev.get("replied") else "")
                        if ev["type"] == "mes":
                            print("    mes  : %s" % ev["text"])
                        elif ev["type"] == "next":
                            print("    next : ZC_WAIT_DIALOG(0x00b5)%s" % reply)
                        elif ev["type"] == "menu":
                            print("    menu : %s%s" % (" / ".join(
                                "%d.%s" % (i + 1, o)
                                for i, o in enumerate(ev["options"])), reply))
                        else:
                            print("    close: ZC_CLOSE_DIALOG(0x00b6)%s" % reply)
                    for ch in talk["choices"]:
                        print("  選択 %d 個目: %d 番 (%s)"
                              % (ch["menu_no"], ch["selected"], ch["label"]))
                    if talk["map_move"]:
                        print("  ZC_NPCACK_MAPMOVE(0x0091): %s (%d,%d)"
                              % (talk["map_move"]["map"], talk["map_move"]["x"],
                                 talk["map_move"]["y"]))
                    else:
                        print("  ZC_NPCACK_MAPMOVE(0x0091) は届きませんでした "
                              "(転職しなかった場合はこれが正常)")
                    summary = msession.stat_summary()
                    interesting = {k: summary[k] for k in (
                        "LOOK_BASE(class)", "SP_JOBLEVEL", "SP_BASELEVEL",
                        "SP_JOBEXP", "SP_BASEEXP", "SP_SKILLPOINT", "SP_HP",
                        "SP_MAXHP", "SP_SP", "SP_MAXSP") if k in summary}
                    print("  ステータス更新の最終値: %s"
                          % (", ".join("%s=%s" % kv for kv in interesting.items())
                             or "なし"))
                    msession.quit()
                    print("  CZ_REQUEST_QUIT(0x018a) -> ZC_ACK_REQ_DISCONNECT(0x018b) "
                          "result=%s (0=切断。ここで map-server が DB に保存する)"
                          % msession.info["quit_result"])

                step("npc_skip", True, character=pick, npc=npc, talk=talk,
                     map_session=msession.info,
                     map_moves=msession.map_moves,
                     stat_updates=msession.stat_updates,
                     stat_summary=summary,
                     units_at_entry=sorted(msession.units_at_entry.values(),
                                           key=lambda u: u["aid"]),
                     units=sorted(msession.units.values(),
                                  key=lambda u: u["aid"]),
                     unit_errors=msession.unit_errors)

            # --- 6. map ----------------------------------------------------
            if args.enter_map:
                alive = [c for c in chars if c["delete_date"] == 0]
                if not alive:
                    print("[6] map 接続はスキップします (接続可能なキャラクターがいません)")
                    step("enter_map", True, skipped="接続可能なキャラクターがいません")
                else:
                    # --name のキャラクターがまだ生きていればそれを、いなければ先頭を使う
                    pick = next((c for c in alive
                                 if target and c["char_id"] == target["char_id"]),
                                alive[0])
                    print("[6] CH_SELECT_CHAR(0x0066) slot=%d (name=%r) で map に入ります"
                          % (pick["slot"], pick["name"]))
                    zone = session.select_char(pick["slot"])
                    print("  HC_NOTIFY_ZONESVR(0x0ac5): char_id=%d map=%s -> %s:%d"
                          % (zone["char_id"], zone["map"], zone["ip"], zone["port"]))
                    map_result = enter_map(zone, login, args.host, args.verbose,
                                           args.timeout)
                    print("  ZC_ACCEPT_ENTER(0x02eb) 受信: map=%s (x=%d, y=%d)"
                          % (map_result["accept_enter"]["map"],
                             map_result["accept_enter"]["x"],
                             map_result["accept_enter"]["y"]))
                    print("  CZ_REQUEST_QUIT(0x018a) -> ZC_ACK_REQ_DISCONNECT(0x018b) "
                          "result=%s (0=切断)" % map_result["quit_result"])
                    map_result["character"] = pick
                    step("enter_map", True, **map_result)

        report["ok"] = True
        print("\n=== 結果: すべての段階が成功しました ===")

    except ProbeError as exc:
        print("\n=== 結果: 失敗 ===", file=sys.stderr)
        print("エラー: %s" % exc, file=sys.stderr)
        report["error"] = str(exc)
        step("failed", False, error=str(exc))
        exit_code = 1
    except OSError as exc:
        print("\n=== 結果: 失敗 (接続エラー) ===", file=sys.stderr)
        print("エラー: %s" % exc, file=sys.stderr)
        report["error"] = "接続エラー: %s" % exc
        step("failed", False, error=report["error"])
        exit_code = 1

    report["finished_at"] = datetime.datetime.now().isoformat(timespec="seconds")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2)
        print("JSON を書き出しました: %s" % args.json)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

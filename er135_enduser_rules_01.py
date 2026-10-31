# -*- coding: utf-8 -*-
"""END-USER-LISTENING-PAGE-PRODUCTION-WIRING-01 委任_02B: End Userページの禁止語・許可値・schemaの規則(データのみ。処理なし)。

er135_enduser_page_01.py(本体)とtestが共通に参照する。禁止語のリストをここへ分離しているのは、本体が
『DEV/Trial資産のpath・語を一切参照しない』ことを静的testで検査できるようにするため(本体ソースに禁止語を書かない)。
"""

SCHEMA_ARTICLE = "enduser_article_v1"
SCHEMA_SYNC_IN = "enduser_sync_v1"            # 02A(同期module)の出力契約
SCHEMA_SYNC_PUBLIC = "enduser_sync_public_v1"  # enduser/data/sync_<lv>.json
SCHEMA_BUILD_INFO = "enduser_build_info_v1"
ASSET_BUILD_ID = "rev01-i"

# 承認済みの日本語訳の出所は2値のみ(それ以外はSTOP)
JA_SOURCES = ("approved_ja_manuscript", "approved_ja_original_in_dev_page")
# 訳が無い部分だけをEnd User build内で文ID単位に新規生成した訳(委任_03A: コード・mock試験まで。実生成は委任_03B)。承認済み原稿の出所とは別に扱う
JA_SOURCE_GENERATED = "generated"
JA_SOURCES_ALL = JA_SOURCES + (JA_SOURCE_GENERATED,)
# 現行asset(app.js)が日本語訳ブロックを描画するpart種別。生成はこの種別だけに行う(描画できない種別に訳を生成してもAPI費用が無駄になり、page_verifyのJ2で不合格になる)。
# rev01-fのPreviewカードは`trHtml`を呼ばない。Adv Previewの訳表示には asset rev01-g(DEV rev01-e + derive EDIT J26: Previewカードに trHtml(p) を追加。
# docs/research/ENDUSER-EN-JA-LINKED-HIGHLIGHT-01/INTEGRATION_03_02.md)が必要で、assetの更新は全End Userページの再produceを伴うため委任_03Bで行う。
ASSET_TRANSLATION_KINDS = {"rev01-i": ("preview", "story", "comment", "oneline"), "rev01-h": ("preview", "story", "comment", "oneline"), "rev01-g": ("preview", "story", "comment", "oneline"), "rev01-f": ("story", "comment", "oneline"), "rev01-e": ("story", "comment", "oneline")}

# 出力(JSON値・HTML/JS/CSS)に現れてはならない語。開発者向け専用要素・DEV仮データ・内部情報。
FORBIDDEN_OUTPUT = (
    "placeholder_for_layout_check", "dev_translation_unapproved", "DEV訳", "仮データ", "未承認", "[DEV]", "phnote",
    "=====", "⏸", "chunk-mark", "rpt-", "Traceback", "confirmation_id", "PASS_WITH_WARNING", "pass-with-warning",
    "制作情報", "ASR警告", "Local Rewrite", "Fallback 適用", "TTS 1回",
)
# Windows/POSIXの絶対path(run/内部dirの露出)
FORBIDDEN_PATH_PATTERNS = (r"[A-Za-z]:[\\/]",r"(?<![A-Za-z0-9_.-])/(?:Users|home|tmp|var)/", r"er\d{3}_output")

# production assetに現れてはならない語(DEV試作由来の確認用機能・他記事参照)
FORBIDDEN_ASSET = (
    "sync=dummy", "dummy", "Q.get('a')", "dev_enduser_page_01", "PROTOTYPE-01", "[DEV]", "DEV訳", "DEV試作", "devbar",
    "placeholder_for_layout_check", "dev_translation_unapproved", "phnote", "syncState", "sync_index", "ai_island", "moon",
    "仮データ", "family_x_", "family_y_", "family_z_",
)
# er135本体ソースにも現れてはならないDEV/Trial資産のpath語(静的testで検査)
FORBIDDEN_MODULE_REFERENCES = ("dev_enduser_page_01", "PROTOTYPE-01", "END-USER-LISTENING-PAGE-PROTOTYPE")

# row label -> kind
LEVEL_IDS = {"std": "std", "standard": "std", "adv": "adv", "advanced": "adv"}
TEXT_KINDS = ("topic", "jtitle", "preview", "comment", "story", "oneline")

# 学習コーナー見出し(厳密判定。未知はSTOP)。『ニュアンス解説』は廃止(2026-10-30)=ここに無い。devページに見出しがあればadapterがENDUSER_NUANCE_CORNER_ABOLISHEDでSTOP
NUANCE_ABOLISHED_HEADING = "ニュアンス解説"
STUDY_HEADINGS = {
    "Vocabulary & Expressions": "vocab",
    "Grammar & Sentence Structure": "grammar",
}

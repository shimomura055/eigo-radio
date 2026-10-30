# ============================================================
# er006_model_routing_contract_01.py
# ER-006-MODEL-ROUTING-CONTRACT-01: Production Model RoutingのSingle Source of Truth
# ============================================================
# 各Production工程が使用してよいModel/Providerをここに集約する。
# 各工程は自身でmodel名を決められず、必ずここから取得する。
#
# 決定の経緯(2026-08-22、ユーザー承認済み):
# Writer(B1/A2)・Writer Fact Check・Support(B1/A2)・Support Fact Checkは、
# コード上は元々(ER-002/003時代から一貫して)gpt-5.6-solを使う設計だった
# (er002_ja_free_markdown_restore.WRITER_MODEL = "gpt-5.6-sol"という単一の
# hardcoded literalに、Writer/Support/Key Phrase Selector等の全チェーンが
# 連鎖的に依存していた)。ER-005での実験検証(未検証の試験提案)を受けて、
# これら4工程をLunaへ正式に固定する、というユーザーの明示的な意思決定に
# 基づき、本モジュールでLunaをApproved Modelとして確定させる。
# Research系(Evidence Pack/VFL/Verification)は元々Luna(ER-006で新規構築)、
# Query Planning/Topic Selectionも元々Luna(gather_topic.py等、ER-005以前
# から)であり、今回の変更対象ではない。
#
# 2026-10-08(ユーザー判断7、PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01
# 委任_03 Phase 2): 全7定数をgpt-5.6-lunaからgpt-6-lunaへ変更した
# (「全6-luna化をProduction方針として進めてOK」)。上位互換かつ単価が安い
# (Input $0.10/Cached $0.01/Output $0.50 per 1M)ことが理由。切り戻しは
# このPhase 2 commitのrevertのみ(単価登録・fail-closed化=Phase 1は戻さない)。
# 旧Trial scriptの再実行は require_model_or_override(process,
# "gpt-5.6-luna", override_reason=...) で5.6を明示指定すること。
from __future__ import annotations


class ModelContractViolation(Exception):
    """規定外Model/Providerが指定された場合に送出する。API call実行前に
    必ず送出されなければならない(fail-closed)。"""


class PricingNotFoundError(RuntimeError):
    """Production経路のコスト/予算ガード計算で、使用modelの単価が
    pricing_snapshot.jsonに無い場合に送出する(fail-closed、単価未登録を
    0円扱いにしない。PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01 Phase 1、
    Opus条件C M1)。メッセージにprovider/model/meterを含める。"""


# ------------------------------------------------------------
# Approved Model(OpenAI系)
# ------------------------------------------------------------
QUERY_PLANNER_MODEL = "gpt-6-luna"
TOPIC_SELECTOR_MODEL = "gpt-6-luna"
RESEARCH_MODEL = "gpt-6-luna"          # Evidence Pack / VFL / Verification
WRITER_MODEL = "gpt-6-luna"            # B1 Writer / A2 Writer(Deviation Check含む)
WRITER_FACT_CHECK_MODEL = "gpt-6-luna"
SUPPORT_MODEL = "gpt-6-luna"           # B1 Support / A2 Support(Key Phrase選定・正規化含む)
SUPPORT_FACT_CHECK_MODEL = "gpt-6-luna"
# ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 PN(OPEN-472、ユーザー正式採用UDR #168): Run Entity Table(本文固有名詞の実体抽出NER)。X/Z run内のTTS段入口で使う(er103_run_entity_table_01)。
RUN_ENTITY_TABLE_MODEL = "gpt-6-luna"

# ------------------------------------------------------------
# Approved Provider(非OpenAI)
# ------------------------------------------------------------
EXCEPTION_SEARCH_PROVIDER = "perplexity"
# ER-006-AUDIO-COST-SPEC-FIX-01(2026-08-22)以降: Gemini TTS呼び出し方式は
# Batch API(client.batches.create())がApproved Production方式として確定
# している(50%コスト減、Human Review試聴でStandardとの品質差なしを確認済み)。
# ただしTTS_MODEL定数自体はmodel名(gemini-2.5-pro-preview-tts)のみを表し、
# Standard(client.models.generate_content())/Batch(client.batches.create())
# のどちらで呼ぶかは表現していない。実際のProduction call site(6箇所、
# er003_v1_crosslevel_audio_02_common.py等)は現時点で全てStandard呼び出し
# のままであり、Batchへの配線は未実装(詳細はCURRENT_SPEC.md「Audio
# Production Pipeline」節、OPEN_ITEMS.mdのOPEN-50を参照)。
TTS_MODEL = "gemini-2.5-pro-preview-tts"
# ER-006-AUDIO-COST-PILOT-02(2026-08-22)以降: 日本語ASRはAzureのまま
# だが、英語ASRはPilotとしてOpenAI gpt-4o-mini-transcribeへ切り替えた
# (require_provider("ASR", ...)はこのモジュール内では単一値の汎用チェック
# であり、言語別の使い分けをモデル化していない。かつ実際の本番ASR呼び出し
# 経路からrequire_provider("ASR", ...)は呼ばれていない=このチェック自体
# 未配線のままである)。実際に配線済みで言語別routingをFail-closedに強制
# するSSOTは er006_asr_provider_routing_01.py::ASR_ROUTING / require_asr_
# route() であり、ASRのrouting判断はそちらを正とする。ASR_PROVIDER定数は
# 既存test(er006_model_routing_contract_01_test.py)との後方互換のため
# "azure"のまま残す。
ASR_PROVIDER = "azure"

# 監査用: 工程名 -> Approved Model/Providerの対応表(regression/static audit testが使う)
PROCESS_MODEL_MAP = {
    "QUERY_PLANNING": QUERY_PLANNER_MODEL,
    "TOPIC_SELECTION": TOPIC_SELECTOR_MODEL,
    "EVIDENCE_PACK": RESEARCH_MODEL,
    "VFL": RESEARCH_MODEL,
    "VERIFICATION": RESEARCH_MODEL,
    "B1_WRITER": WRITER_MODEL,
    "A2_WRITER": WRITER_MODEL,
    "WRITER_FACT_CHECK": WRITER_FACT_CHECK_MODEL,
    "B1_SUPPORT": SUPPORT_MODEL,
    "A2_SUPPORT": SUPPORT_MODEL,
    "SUPPORT_FACT_CHECK": SUPPORT_FACT_CHECK_MODEL,
    # ER-006-PRONUNCIATION-LEDGER-SECONDARY-ASR-01(2026-08-22)で追加。
    # Writer完成後の記事本文/Support/Key Phraseから、発音が自明でない
    # 固有名詞を抽出する工程。既存工程と同じLunaを使う(新規モデル追加なし)。
    "PROPER_NOUN_EXTRACTION": WRITER_MODEL,
    # A2/B1 Point Structure Semantic Alignment(2026-08-25)で追加。Verified
    # Fact LedgerからA2/B1 Writer呼び出し前にShared Point Blueprintを
    # 生成する工程。B1/A2 Writerと同じ信頼度・同じLunaを使う(新規モデル
    # 追加なし)。
    "SHARED_POINT_BLUEPRINT": WRITER_MODEL,
    # NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-PRODUCTION-WIRING-01(2026-09-25)で
    # 追加。Advanced(Natural English Adaptation、CEFR B1)からStandard
    # (CEFR A2、v5 6,000語ライン+自然さ優先Prompt)を生成する工程。
    # B1/A2 Writerと同じ信頼度・同じLunaを使う(新規モデル追加なし)。
    "STANDARD_A2_ADAPTATION": WRITER_MODEL,
    # NEWS-ADVANCED-A2-PRODUCTION-E2E-WIRING-01(2026-09-25)で追加。日本語
    # 完成Entertainment記事(R2)からAdvanced(Natural English Adaptation、
    # CEFR B1)を生成する工程。B1/A2 Writerと同じ信頼度・同じLunaを使う
    # (新規モデル追加なし)。
    "NATURAL_ENGLISH_ADAPTATION": WRITER_MODEL,
    # TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01(2026-09-27)
    # Phase 1で追加。既存TTS_MODEL/PROCESS_PROVIDER_MAP["TTS"]の汎用単一値
    # 契約は変更しない(Family別モデルを許容する構造変更はしない、設計書
    # §(g))。Family Xランナーがtts_backend="speech_metadata_flash_lite"を
    # 明示的に選択した場合のみ、この専用processキー経由でfail-closedに
    # model_idを検証する(er033_tts_flash_lite_backend_wiring_01.
    # make_speech_metadata_call_fn)。Family A/B/C(legacy)はこのキーを
    # 一切参照しない。
    "FAMILY_X_FLASH_LITE_TTS": "gemini-3.8-flash-lite-tts",
    # FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W4、2026-09-29)で追加。
    # Advanced(B1B)Key Phrase英語解説(explanation_en)のtext生成工程。
    # 既存Key Phrase選定(B1_SUPPORT/A2_SUPPORT)と同じSUPPORT_MODELを使う
    # (新規モデル追加なし)。
    "KEY_PHRASE_ADVANCED_EXPLANATION": SUPPORT_MODEL,
    # FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_14(2026-10-25、ユーザー正式承認APPROVED_FOR_PRODUCTION 案α)で追加(追加のみ、既存キー不変)。
    # 学習テキスト Part 1「Vocabulary & Expressions」の日本語一般解説(入力=確定KPの英語表現のみ)。KEY_PHRASE_ADVANCED_EXPLANATION
    # (音声用の英語短文解説)とは別processにして原価・routing監査を分離する。SUPPORT_MODELを参照(Trial-04と同一、新規モデルなし)。
    "KEY_PHRASE_GENERAL_EXPLANATION": SUPPORT_MODEL,
    # FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_16(2026-10-25、ユーザーT1正式承認)で追加(追加のみ、既存キー不変)。Part 1の本文引用英文の日本語訳
    # (入力=引用英文のみ、解説LLMとは独立call)。SUPPORT_MODELを参照(新規モデルなし)。
    "KEY_PHRASE_SOURCE_SENTENCE_JA": SUPPORT_MODEL,
    # ENDUSER-EN-JA-LINKED-HIGHLIGHT-01 委任_03T(2026-10-30)で追加(追加のみ、既存キー不変)。End Userページ用の英日対訳の新規生成
    # (ENDUSER_JA_TRANSLATE=文脈付き翻訳、ENDUSER_JA_VERIFY=対訳照合)。SUPPORT_MODELを参照(新規モデルなし)。未配線(standalone)。
    "ENDUSER_JA_TRANSLATE": SUPPORT_MODEL,
    "ENDUSER_JA_VERIFY": SUPPORT_MODEL,
    # PART2-GRAMMAR-PRODUCTION-WIRING-01 委任_03(2026-10-25、Part 2 Grammar & Sentence Structure、ユーザーAPPROVED_FOR_PRODUCTION)で追加(追加のみ、既存キー不変)。
    # 候補抽出(Step A'')と解説生成(Step B)。SUPPORT_MODEL=gpt-6-luna(Trial-07/08と同一、新規モデルなし)。
    "STUDY_TEXT_GRAMMAR_EXTRACT": SUPPORT_MODEL,
    "STUDY_TEXT_GRAMMAR_EXPLAIN": SUPPORT_MODEL,
    # NUANCE-EXPLANATION-PRODUCTION-WIRING-01 委任_02A(2026-10-29、ニュアンス解説、ユーザーAPPROVED_FOR_PRODUCTION)で追加(追加のみ、既存キー不変)。
    # DEPRECATED(2026-10-30 NUANCE-CORNER-ABOLITION-01 ユーザー決定): ニュアンス解説コーナー廃止につき呼出元0(er134撤去済み)。過去usage logと閉集合testの整合のため定義のみ残置。新規利用禁止(OSFは別名の別processを使う)。
    "NUANCE_EXPLANATION": SUPPORT_MODEL,
    "NUANCE_OVERLAP_JUDGE": SUPPORT_MODEL,
    # RISK-FLAGGER-PRODUCTION-WIRING-01 Phase 2 C1(2026-10-10、ユーザーGo)で追加(追加のみ、既存キー不変)。
    # model名はリテラル固定(WRITER_MODEL等の他定数を経由しない=他定数の変更に連動しない)。環境変数での上書きなし。
    #   FAMILY_X_RF_LUNA / FAMILY_X_RF_GEMINI : Risk Flagger 4条件(Luna A3/A4・Gemini A3/A4)
    #   FAMILY_X_FACTLOCK_R0     : 新Writer W-1 の R0(Fact Lock、effort=high)
    #   FAMILY_X_FACTLOCK_REVISE : 新Writer W-1 の R1/R2(effort=high)。返却model不一致はSTOP
    # FAMILY-X-JA-MODEL-ALLOCATION-SOL61-PRODUCTION-WIRING-01(2026-10-11、ユーザー正式決定=E案
    # APPROVED_FOR_PRODUCTION): 日本語記事のB3/R0/R1/R2をすべてgpt-6.1-solへ。FAMILY_X_STORYLINE_B3を
    # 新設(従来B3はvfl01.MODEL=WRITER_MODEL=Lunaを暗黙参照していた)。リテラル固定、他定数に連動しない。
    # (旧: R0=gpt-6-luna / REVISE=gpt-6-astra。Rollbackはこの値の差戻し。)
    "FAMILY_X_STORYLINE_B3": "gpt-6.1-sol",
    "FAMILY_X_RF_LUNA": "gpt-6-luna",
    "FAMILY_X_RF_GEMINI": "gemini-3.5-flash-lite",
    "FAMILY_X_FACTLOCK_R0": "gpt-6.1-sol",
    "FAMILY_X_FACTLOCK_REVISE": "gpt-6.1-sol",
    # FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01 委任_06 C-2(2026-10-22、ユーザー正式採用APPROVED_FOR_PRODUCTION): Family X中核数値の
    # 概数可否判断(1記事1call、reasoning effort=low)。追加のみ・既存キー不変・リテラル固定・環境変数上書きなし。Family Zは参照しない。
    "FAMILY_X_B3_CORE_NUMBER_ROUNDING": "gpt-6-luna",
    # FAMILY-Z-STORY-POOL-SCREENING-TRIAL-01 委任_02(2026-10-11、ユーザー指示: Trial基本モデルをgpt-6-lunaへ固定)で
    # 追加(追加のみ、既存Production keyは不変)。**Trial専用**(er054 family_z story pool trial driverのみが参照)。
    # Production採用を意味しない。リテラル固定(他定数に連動しない)。Astra/Sol等は提案候補でありここへは入れない。
    "FAMILY_Z_TRIAL_STORY_QUALITY_EVAL": "gpt-6-luna",
    "FAMILY_Z_TRIAL_RIGHTS_INTERPRET": "gpt-6-luna",
    # FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_03(2026-10-12、ユーザー正式決定①〜⑤
    # [APPROVED_FOR_PRODUCTION]+Opus独立レビューM7): Family Z Production用routing key追加
    # (追加のみ、既存keyは不変、リテラル固定、環境変数上書きなし)。
    #   FAMILY_Z_WRITER_ADV_R0/R1/R2 : Advanced英語Writer(R0/R1/R2各段、gpt-6.1-sol)
    #   FAMILY_Z_STD_ADJUST          : Advanced最終稿からStandardへのレベル調整(gpt-6.1-sol)
    #   FAMILY_Z_SEMANTIC_JUDGE      : 意味保持Validator第2層(gpt-6-luna、執筆Solと別系統)
    #   FAMILY_Z_STORY_SPLIT         : Story 3分割境界の選択(gpt-6-luna)
    #   FAMILY_Z_DIALOGUE_ATTRIBUTION: 全引用の話者判定(gpt-6-luna)
    # M7: 判定用keyと共用しない(用途別にkeyを分離し、後からモデルを個別に変更できるようにする)。
    "FAMILY_Z_WRITER_ADV_R0": "gpt-6.1-sol",
    "FAMILY_Z_WRITER_ADV_R1": "gpt-6.1-sol",
    "FAMILY_Z_WRITER_ADV_R2": "gpt-6.1-sol",
    "FAMILY_Z_STD_ADJUST": "gpt-6.1-sol",
    "FAMILY_Z_SEMANTIC_JUDGE": "gpt-6-luna",
    "FAMILY_Z_STORY_SPLIT": "gpt-6-luna",
    "FAMILY_Z_DIALOGUE_ATTRIBUTION": "gpt-6-luna",
    # FAMILY-Y-PRODUCTION-LAUNCH-01 委任_02B(2026-10-25、ユーザー正式決定[Y Production立上げ・Closing一般化Prompt 02・案B個別採用]+Opus条件Aレビュー):
    # Family Y Production用routing key(追加のみ、既存keyは不変、リテラル/定数参照固定、環境変数上書きなし)。Family別に分離し費用集計が混ざらない
    # (stage tagはer121_family_y_runner_01が `FAMILY_Y_PRODUCTION_<slug>` で記録)。DESIGN_02 §routingの表と突合(02A)。
    #   FAMILY_Y_CLOSING_GENERATE : Closing一般化(Prompt 02、reasoning effort=high。承認原文=gpt-6.1-sol effort high)
    #   FAMILY_Y_CLOSING_REWRITE  : Closing local rewrite on Leakage Gate FAIL (judgements<=3, effort=medium)
    #   FAMILY_Y_LEAK_JUDGE       : Leakage Gate判定(Voice 7項目/Tension 6項目。執筆Solと別系統=gpt-6-luna)
    #   FAMILY_Y_VOICE_GENERATE   : Voice R0生成(実在意見ベース方式)
    #   FAMILY_Y_VOICE_REWRITE    : Voice局所書換え(Leakage Gate FAIL時、判定<=3)
    #   FAMILY_Y_LEAD_GENERATE    : リード生成
    #   FAMILY_Y_PERSONA_INTRO    : 人物紹介ナレーション(3本1 call)
    #   FAMILY_Y_TRANSLATE_ADV/STD: 英訳(X承認済み関数の既存routing=NATURAL_ENGLISH_ADAPTATION/STANDARD_A2_ADAPTATIONと同値。定数WRITER_MODEL参照)
    # Comment/Preview/KP等のsupport系は既存のB1_SUPPORT/A2_SUPPORT/KEY_PHRASE_*をそのまま使う(新規model追加なし)。
    "FAMILY_Y_CLOSING_GENERATE": "gpt-6.1-sol",
    "FAMILY_Y_CLOSING_REWRITE": "gpt-6.1-sol",
    "FAMILY_Y_LEAK_JUDGE": "gpt-6-luna",
    "FAMILY_Y_VOICE_GENERATE": "gpt-6.1-sol",
    "FAMILY_Y_VOICE_REWRITE": "gpt-6.1-sol",
    "FAMILY_Y_LEAD_GENERATE": "gpt-6.1-sol",
    "FAMILY_Y_PERSONA_INTRO": "gpt-6.1-sol",
    # 委任_03: Voice出典付番(provenance map)・構造タグの補助判定(gpt-6-luna、effort=medium。text coreのROUTE_AUXから統合)
    "FAMILY_Y_VOICE_PROVENANCE_MAP": "gpt-6-luna",
    "FAMILY_Y_VOICE_STRUCTURE_TAG": "gpt-6-luna",
    "FAMILY_Y_TRANSLATE_ADV": WRITER_MODEL,
    "FAMILY_Y_TRANSLATE_STD": WRITER_MODEL,
}
PROCESS_PROVIDER_MAP = {
    "EXCEPTION_SEARCH": EXCEPTION_SEARCH_PROVIDER,
    "TTS": TTS_MODEL,
    "ASR": ASR_PROVIDER,
}


def require_model(process: str, model: str | None) -> str:
    """API call実行**前**に呼ぶ。processの規定Modelと一致しなければ
    ModelContractViolationを送出する。modelがNone/空文字(未指定)も
    fail-closedで拒否する。一致すればmodelをそのまま返す
    (`model=require_model("B1_WRITER", candidate)`という形で呼び出し箇所に
    直接埋め込める)。"""
    if process not in PROCESS_MODEL_MAP:
        raise ModelContractViolation(
            f"未知のprocess '{process}' はModel Routing Contractに定義されていません。")
    approved = PROCESS_MODEL_MAP[process]
    if not model:
        raise ModelContractViolation(
            f"process '{process}' へmodelが指定されていません(SDK defaultへの"
            f"暗黙フォールバックは禁止)。Approved Model: {approved}")
    if model != approved:
        raise ModelContractViolation(
            f"process '{process}' はApproved Model '{approved}' を使用する契約ですが、"
            f"'{model}' が指定されました。fallbackとして高価なmodelへ自動昇格すること、"
            f"またmodel未指定のままSDK defaultへ落ちることは禁止されています。")
    return model


# ------------------------------------------------------------
# ER-009-N1-POINT-RETRY-ROUTING-GOVERNANCE-10: DEV/Trial向けRuntime Guard
# ------------------------------------------------------------
# require_model()はProduction call site(er003_v1_n3_01_articles_generate.py
# 等)がinlineで直接埋め込む、無条件fail-closedの検証。DEV/Trialスクリプトは
# 実験のため意図的に別modelを使いたい場合があるため、その場合だけ明示的な
# override_reason(空文字列不可)を渡すことを条件に許可する薄いラッパーを
# 別関数として用意する。requireModel自体の挙動(Production側)は変更しない。
def require_model_or_override(process: str, model: str | None, override_reason: str | None = None) -> str:
    """DEV/Trialスクリプト用。override_reasonを渡さない場合はrequire_model()と
    完全に同じ(Approved Modelと不一致ならfail-closedでModelContractViolation)。
    override_reasonへ空でない理由文字列を渡した場合のみ、Approved Model以外の
    modelでも許可する(ただしmodel自体は必須で、Noneや空文字は許可しない)。
    「DEV/Trialも正式Routingをデフォルトとし、別modelを使う実験をする場合のみ
    明示的なoverrideを必要とする」という方針を実装したもの。"""
    if process not in PROCESS_MODEL_MAP:
        raise ModelContractViolation(
            f"未知のprocess '{process}' はModel Routing Contractに定義されていません。")
    if not model:
        raise ModelContractViolation(
            f"process '{process}' へmodelが指定されていません(override時も必須)。")
    if not override_reason or not override_reason.strip():
        return require_model(process, model)
    approved = PROCESS_MODEL_MAP[process]
    if model != approved:
        print(f"[ModelRoutingContract][OVERRIDE] process '{process}': Approved Model '{approved}' "
              f"の代わりに '{model}' を明示override(理由: {override_reason})で使用します。")
    return model


def require_provider(process: str, provider: str | None) -> str:
    """Provider(Perplexity/Gemini TTS/Azure ASR)版のrequire_model。"""
    if process not in PROCESS_PROVIDER_MAP:
        raise ModelContractViolation(
            f"未知のprocess '{process}' はModel Routing Contractに定義されていません。")
    approved = PROCESS_PROVIDER_MAP[process]
    if not provider:
        raise ModelContractViolation(f"process '{process}' へproviderが指定されていません。")
    if provider != approved:
        raise ModelContractViolation(
            f"process '{process}' はApproved Provider '{approved}' を使用する契約ですが、"
            f"'{provider}' が指定されました。")
    return provider

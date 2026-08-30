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
from __future__ import annotations


class ModelContractViolation(Exception):
    """規定外Model/Providerが指定された場合に送出する。API call実行前に
    必ず送出されなければならない(fail-closed)。"""


# ------------------------------------------------------------
# Approved Model(OpenAI系)
# ------------------------------------------------------------
QUERY_PLANNER_MODEL = "gpt-5.6-luna"
TOPIC_SELECTOR_MODEL = "gpt-5.6-luna"
RESEARCH_MODEL = "gpt-5.6-luna"          # Evidence Pack / VFL / Verification
WRITER_MODEL = "gpt-5.6-luna"            # B1 Writer / A2 Writer(Deviation Check含む)
WRITER_FACT_CHECK_MODEL = "gpt-5.6-luna"
SUPPORT_MODEL = "gpt-5.6-luna"           # B1 Support / A2 Support(Key Phrase選定・正規化含む)
SUPPORT_FACT_CHECK_MODEL = "gpt-5.6-luna"

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

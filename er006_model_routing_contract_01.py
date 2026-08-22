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

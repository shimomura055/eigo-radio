# ============================================================
# er030_key_phrase_db_hybrid_selector_01.py
# KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01
# ============================================================
# DB Hybrid方式(Primary)のSelector層: er030_key_phrase_db_hybrid_core_01
# (Stage1候補生成+shortlist組み立て、ロジック無変更で昇格)が返す
# compact shortlistから、既存Production Strategy L選定gate
# (`er003_key_words_production.run_production_selection_gate`、
# schema/model/validator一切無変更)を1回だけ呼び出す軽量prompt経由の
# 選定を行う。
#
# Fallback設計(ユーザー正式決定、2026-09-27。修正1回目[Opus L2所見
# B3/S3/S4/S5]で条件を改訂): 以下のいずれかに該当する場合、
# `DbHybridFailure`を送出する。`fallback_allowed`(既定True)がTrueの
# 場合のみ、呼び出し元`er003_v1_n3_01_scaffold_generate.run_key_phrase_
# selection`が捕捉し、既存Strategy L全文方式[本文全体をprompt送信する
# 既存経路]へfallbackする。
#   - SHORTLIST_TOO_SMALL(fallback可): shortlist総数<12、または
#     phrase_included_count+important_noun_included_count<5
#     (機械screeningが実質的に機能していない記事)
#   - TECHNICAL_GENERATION_FAILED/PARSE_FAILED/KEY_WORDS_STRUCTURE_INVALID
#     (fallback可): 既存run_production_selection_gate()自体が返すstatus
#     (P2G/P2Iの既存validatorが不合格と判定、コード変更なし)
#   - SELECTOR_EXCEPTION(fallback可): Stage1/shortlist構築自体が例外を
#     送出(DB読込失敗・Wiktionary API異常等)
#   - SOURCE_SPAN_NOT_IN_RAW_ARTICLE(fallback可): 選定PASS直後、item の
#     source_span/source_sentenceが生article_textに実在しない
#     (`er003_key_phrase_source_gate_01.normalize_text`基準)
#   - MODEL_CONTRACT_VIOLATION(fallback不可、STOP): 応答モデルが
#     承認済みモデルと不一致(fallback先でも同じ契約違反が再発しうる
#     ため、fallbackで隠蔽しない)
#   - 1呼び出しあたりのcost guard(¥5.0)超過は、PASS済み結果の場合は
#     もはや失敗condition化しない(`cost_guard_exceeded=true`を結果へ
#     記録するのみ、より高価な全文方式への再課金を避ける)。記事単位の
#     累積コスト上限超過(`KP_ARTICLE_COST_CAP_EXCEEDED`、fallback不可・
#     STOP)は呼び出し元`run_key_phrases`が管理する。
#
# 費用計測(cost_jpy)はProduction共有pricing module
# (er009_n1_routing_governance_10_actual_model_cost)を再利用する
# (新しい価格表は作らない)。SELECTION_GUIDANCE/extract_static_
# instructions/extract_article_title/assert_no_full_article_body/
# _compact_evidence_stringは、修正1回目(Opus L2所見S6(a))でTrial run
# script(`er028_key_phrase_db_hybrid_trial_03_run.py`)から本ファイルへ
# 移設した(Trial側は無変更のまま残し、byte一致testで乖離を防ぐ。
# Production moduleからTrial run scriptへのimportをゼロにする)。
# ============================================================

from __future__ import annotations

import json
import os
import re
import time
from collections import Counter

import er003_b1_p2_keywords as bk
import er003_key_phrase_source_gate_01 as source_gate
import er003_key_words_production as prod
import er006_model_routing_contract_01 as routing
import er009_n1_routing_governance_10_actual_model_cost as pricing
import er030_key_phrase_db_hybrid_core_01 as core
import er030_key_phrase_db_hybrid_source_reference_contract_01 as src_ref_contract

# Trial-04実測(12本文合計¥12.8159、最大¥2.0284/記事)の約2.5倍を安全域と
# する(runaway reasoning token検知、通常記事はこの閾値に到達しない)。
# 修正1回目(Opus L2所見S4、Fable決定): 定数名・意味論を
# 「1呼び出しあたりのrunaway検知(per-call runaway detection)」に限定
# する。PASS済みの選定結果は破棄せず採用し(より高価な全文方式へ
# 再課金しない)、telemetry/per-article metadataに
# `cost_guard_exceeded=true`のみ記録する。記事単位の累積JPY上限は
# 別途`KP_ARTICLE_COST_CAP_JPY`(STOP、fallbackしない)で管理する。
DEFAULT_COST_GUARD_JPY = 5.0

# 修正1回目(Opus L2所見S4、Fable決定、新設): 1記事あたりの累積コスト
# (db_hybrid選定+fallback選定+Key Phrase Set Redundancy QA retryを
# 含む、`run_key_phrases`スコープで積算)がこの閾値を超えた場合は
# fallbackではなく`KP_ARTICLE_COST_CAP_EXCEEDED`でSTOPする(Trial-04
# 実測合計¥12.8159/12本文、1記事あたり実測最大¥2.03の約7倍を安全域とする)。
KP_ARTICLE_COST_CAP_JPY = 15.0

# 修正1回目(Opus L2所見S5、Fable決定): Trial-04実測12本文の
# shortlist_total_countは全件20〜24件(最小20)、
# phrase_included_count+important_noun_included_countは最小7件
# (twins_b1)であった(実測根拠は
# `KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01_REPORT.md`§8の
# 実測表を参照)。総数のみの閾値(旧8件)は「機械screeningが機能して
# いるか」の実質的なチェックになっていなかったため、(1)総数12件以上
# かつ(2)phrase_included_count+important_noun_included_count合計5件
# 以上の両方を満たさない場合にDB Hybrid方式の前提(十分な候補プールから
# モデルが5件選ぶ)が崩れているとみなし、Strategy L全文方式へ委ねる。
MIN_SHORTLIST_COUNT = 12
MIN_SHORTLIST_PHRASE_PLUS_IMPORTANT_COUNT = 5


class DbHybridFailure(Exception):
    """DB Hybrid selectorが失敗したことを示す。既定(`fallback_allowed=
    True`)では呼び出し元がStrategy L全文方式へfallbackすべきことを示す。
    telemetryには可能な限りcost_jpy/model_id等実測情報を含める(fallback
    発火の観測可能性を確保する)。

    fallback_allowed(修正1回目、Opus L2所見B3、2026-09-27新設):
    `False`の場合、呼び出し元(`_run_key_phrase_selection_db_hybrid_
    with_fallback`)はStrategy Lへfallbackせず、このまま再raiseして
    処理をSTOPする(fail-closed)。モデルルーティング契約違反
    [`MODEL_CONTRACT_VIOLATION`、応答モデルが承認済みモデルと不一致]・
    記事単位累積コスト上限超過[`KP_ARTICLE_COST_CAP_EXCEEDED`]は、
    fallback先でも同じ問題が再発しうる、またはfallback自体がさらなる
    課金を招くため、fallback_allowed=Falseとする。"""

    def __init__(self, reason_code: str, message: str, telemetry: dict = None,
                 fallback_allowed: bool = True):
        super().__init__(message)
        self.reason_code = reason_code
        self.telemetry = telemetry or {}
        self.fallback_allowed = fallback_allowed


# ============================================================
# 修正1回目(Opus L2所見S6(a)、2026-09-27): SELECTION_GUIDANCEと
# util 4関数(extract_static_instructions/extract_article_title/
# assert_no_full_article_body/_compact_evidence_string)を、
# 「Trial run script」(`er028_key_phrase_db_hybrid_trial_03_run.py`、
# ARTICLES辞書・COST_STOP_THRESHOLD_JPY等Trial固有の実行設定を含む
# CLIスクリプト)からProduction module本体(本ファイル)へ移設する。
# Trial側の定義は無変更のまま残し(Trial記録としての再現性を保つ)、
# 本ファイルの複製がbyte-for-byte同一であることを
# `er030_key_phrase_db_hybrid_family_x_production_wiring_01_test.py`
# の`Er028UtilByteParityTests`でsha256照合により固定回帰化する。これに
# より、Production module(`er030_*`)からTrial run script
# (`er028_key_phrase_db_hybrid_trial_03_run.py`等の`_run`接尾辞スクリプト)
# へのimportをゼロにする(er023/er027/er028の`_stage1`接尾辞モジュール
# [純粋関数の候補生成アルゴリズム、Trial固有の実行設定を含まない]は
# 既存資産として引き続き無変更のまま共有依存する、Core変更禁止原則の
# 対象外)。
# ============================================================

_ARTICLE_PLACEHOLDER_MARKERS = ("{approved_b1_article}", "{approved_b2_article}")


def extract_static_instructions(template: str) -> str:
    """production prompt templateから、article本文placeholder以降(本文
    ラベル行含む)を取り除いた静的instructions部分だけを返す(instructions
    自体の文言は一切変更しない、article差し込み部分だけを取り除く)。
    `er028_key_phrase_db_hybrid_trial_03_run.extract_static_instructions`
    と同一実装(byte一致test対象)。"""
    text = template
    for marker in _ARTICLE_PLACEHOLDER_MARKERS:
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx]
    # placeholder直前のラベル行(例:【B1 Article】)を取り除く
    lines = text.rstrip().splitlines()
    while lines and (lines[-1].strip().startswith("【") or not lines[-1].strip()):
        lines.pop()
    return "\n".join(lines).rstrip() + "\n"


def extract_article_title(article_text: str) -> str:
    """article.mdの最初のH1見出し行のみを再利用する(新しいLLM callでの
    Topic抽出は行わない、既存Writer成果物の一部を読み取るだけ)。
    `er028_key_phrase_db_hybrid_trial_03_run.extract_article_title`と
    同一実装(byte一致test対象)。"""
    for line in article_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return ""


def _compact_evidence_string(c: dict) -> str:
    """`er028_key_phrase_db_hybrid_trial_03_run._compact_evidence_string`
    と同一実装(byte一致test対象)。"""
    if c.get("important_noun_phrase_candidate") and "repeated_compound_noun_heuristic" in (c.get("matched_dbs") or []):
        return "repeated_compound_noun"
    if c.get("important_noun_phrase_candidate") and c.get("matched_dbs") == ["wiktionary"] and \
            c.get("db_categories") == ["multiword_term"]:
        return "wiktionary_multiword"
    parts = list(c.get("matched_dbs") or [])
    cats = list(c.get("db_categories") or [])
    s = "+".join(parts) if parts else "heuristic"
    if cats:
        s += f"[{','.join(cats)}]"
    if c.get("irregular_verb_rescue"):
        s += "+irregular_rescue"
    if c.get("possessive_noise_stripped"):
        s += "+possessive_stripped"
    return s


SELECTION_GUIDANCE = """
【選定方針】
- 最終的に選ぶ5件は、必ず下記の候補一覧の中から選んでください。候補に
  無い新しい表現を作らないでください。
- 5個のうち少なくとも1個は、[重要な単語・単語群候補]区分から選んで
  ください(記事理解・再利用価値の高い重要な名詞・専門用語・複合語)。
- 残りは、[phrase / idiom / phrasal verb候補]区分を優先してください。
  良い候補が不足する場合のみ[word候補]区分で補ってください。
- CEFR難易度・語彙レベルを主要な判断軸にしないでください。
- 各itemのsource_sentenceは、必ず【SENTENCE REFERENCE】に列挙されている
  文をそのまま(一字一句、改変せず)使用してください。新しい文を作らない
  でください。source_spanは、そのsource_sentence内に実際に現れる形
  (元の活用形・大文字小文字を含む)の一部分にしてください。
"""


def assert_no_full_article_body(user_message: str, article_text: str) -> None:
    """article全文がLLM inputへ混入していないことの構造的チェック(連続
    100語一致が無いこと)。regressionテストでも同内容を検証する。
    `er028_key_phrase_db_hybrid_trial_03_run.assert_no_full_article_body`
    と同一実装(byte一致test対象)。"""
    article_words = re.findall(r"[A-Za-z']+", article_text)
    if len(article_words) < 100:
        return
    for i in range(0, len(article_words) - 100, 20):
        window = " ".join(article_words[i:i + 100]).lower()
        if window in re.sub(r"\s+", " ", user_message.lower()):
            raise AssertionError("article全文相当の連続100語がuser_messageに含まれています")


def _usage_dict(usage) -> dict:
    if usage is None:
        return {}
    d = {"input_tokens": getattr(usage, "input_tokens", None),
         "output_tokens": getattr(usage, "output_tokens", None),
         "total_tokens": getattr(usage, "total_tokens", None)}
    in_details = getattr(usage, "input_tokens_details", None)
    if in_details is not None:
        d["cached_input_tokens"] = getattr(in_details, "cached_tokens", None)
    out_details = getattr(usage, "output_tokens_details", None)
    if out_details is not None:
        d["reasoning_tokens"] = getattr(out_details, "reasoning_tokens", None)
    return d


def _make_instrumented_selector_factory(user_message: str, model: str, usage_sink: list,
                                         contract_violation_sink: list = None, client=None):
    """既存Trial cost tracking(er028_key_phrase_db_hybrid_trial_03_run.
    make_instrumented_selector_factory)と同じ計測パターンを、Production
    定数(prod.*)のみを使って再構成したもの(選定ロジック自体は
    prod.run_production_selection_gate/prod.SELECTOR_JSON_SCHEMA等の
    既存Production資産をそのまま呼び出すだけで、新しい判定ロジックは
    含まない)。`contract_violation_sink`(修正1回目、Opus L2所見B3)は
    モデルルーティング契約違反の検知用(下記fn()参照)。"""
    def factory():
        nonlocal client
        if client is None:
            from dotenv import load_dotenv
            load_dotenv()
            from openai import OpenAI
            client = OpenAI()

        def fn():
            t0 = time.time()
            response = client.responses.create(
                model=model,
                reasoning={"effort": prod.SELECTOR_REASONING_EFFORT},
                text={"format": {"type": "json_schema", **prod.SELECTOR_JSON_SCHEMA}},
                input=[
                    {"role": "developer", "content": prod.SELECTOR_DEVELOPER_MESSAGE},
                    {"role": "user", "content": user_message},
                ],
            )
            elapsed = time.time() - t0
            if response.model != model:
                # 修正1回目(Opus L2所見B3): モデルルーティング契約違反は
                # `prod.run_production_selection_gate`内部の広範な
                # `except Exception`(既存Production、無変更)で
                # `TECHNICAL_GENERATION_FAILED`へ吸収されてしまい、この
                # 例外自体は呼び出し元まで伝播しない(Strategy L経路でも
                # 元々同じ挙動)。fail-closedを維持するため、
                # `contract_violation_sink`(run_db_hybrid_selection側で
                # 用意する可変list)に発生事実を記録し、gate呼び出し完了後に
                # run_db_hybrid_selection側で独立検知してDbHybridFailure
                # (fallback_allowed=False)を送出する。
                if contract_violation_sink is not None:
                    contract_violation_sink.append(
                        {"expected_model": model, "actual_model": response.model})
                raise prod.SelectorModelMismatchError(
                    f"応答モデルが不一致です(期待: {model}, 実際: {response.model})")
            text = getattr(response, "output_text", None)
            usage_sink.append({
                "response_id": response.id, "model": response.model,
                "usage": _usage_dict(getattr(response, "usage", None)),
                "elapsed_sec": round(elapsed, 3),
            })
            if not text or not text.strip():
                import er003_ja_to_en_translation as er003
                raise er003.restore.GenerationEmptyOrBrokenError("selector応答が空です")
            return text, response.model, response.id

        fn.model = model
        fn.reasoning_effort = prod.SELECTOR_REASONING_EFFORT
        fn.uses_web_search_tool = False
        fn.uses_structured_output = True
        return fn

    return factory


def _display_type(c: dict) -> str:
    if c.get("important_noun_phrase_candidate"):
        if c.get("unit_type") == "word":
            return "important_word"
        return "noun_phrase"
    return c["unit_type"]


def format_candidate_line(c: dict) -> str:
    sid = c.get("context_sentence_id") or "?"
    return (f"- candidate: \"{c['surface_form']}\" | type: {_display_type(c)} | "
            f"occ: {c.get('occurrence_count_in_article', '?')} | "
            f"evidence: {_compact_evidence_string(c)} | sentence: {sid}")


def build_lightweight_user_message(article_title: str, shortlist_info: dict,
                                    sentence_reference: dict, static_instructions: str) -> str:
    """KEY-PHRASE-DB-HYBRID-TRIAL-04(er029_key_phrase_db_hybrid_trial_04_
    run.build_lightweight_user_message_v4)と同一のprompt構成(Fix Bの
    important_word表示区別を含む)。article全文は一切含まない。"""
    important = [c for c in shortlist_info["shortlist"] if c.get("important_noun_phrase_candidate")]
    phrase = [c for c in shortlist_info["shortlist"]
              if not c.get("important_noun_phrase_candidate") and c["unit_type"] != "word"]
    word = [c for c in shortlist_info["shortlist"]
            if not c.get("important_noun_phrase_candidate") and c["unit_type"] == "word"]

    lines = [static_instructions.rstrip(), ""]
    lines.append(f"【Topic】title: {article_title}")
    lines.append("")
    lines.append("【重要な単語・単語群候補】")
    if important:
        lines.extend(format_candidate_line(c) for c in important)
    else:
        lines.append("(なし)")
    lines.append("")
    lines.append("【phrase / idiom / phrasal verb候補】")
    if phrase:
        lines.extend(format_candidate_line(c) for c in phrase)
    else:
        lines.append("(なし)")
    lines.append("")
    lines.append("【word候補】")
    if word:
        lines.extend(format_candidate_line(c) for c in word)
    else:
        lines.append("(なし)")
    lines.append("")
    lines.append("【SENTENCE REFERENCE】")
    for sid in sorted(sentence_reference, key=lambda s: int(s[1:])):
        lines.append(f'{sid}: "{sentence_reference[sid]}"')
    lines.append(SELECTION_GUIDANCE.rstrip())
    return "\n".join(lines) + "\n"


def _serializable_stage1(st: dict) -> dict:
    keys_to_drop = {"sentence_units"}
    return {k: v for k, v in st.items() if k not in keys_to_drop}


def _shortlist_cache_key(article_text: str) -> str:
    import hashlib
    return hashlib.sha256(article_text.encode("utf-8")).hexdigest()


def _verify_source_spans_against_raw_article(items: list, article_text: str) -> list:
    """修正1回目(Opus L2所見S3): 選定gate PASS直後に、各itemの
    `source_span`(無ければ`source_sentence`)が、
    `er003_key_phrase_source_gate_01.normalize_text`と同一の正規化基準で
    生article_text(canonicalization前)に実在するかを機械確認する
    (`check_key_phrase_source_presence`は既にjsonファイルを前提とした
    シグネチャのため、同じnormalize_text基準をここではitemリストへ直接
    適用する軽量版として実装、正規化ロジック自体は共有・複製しない)。
    戻り値: 不一致item(rank/source_span等)のlist(空なら全件一致)。"""
    normalized_article = source_gate.normalize_text(article_text)
    missing = []
    for item in items:
        raw_value = item.get("source_span") or item.get("source_sentence")
        if not raw_value:
            missing.append({"rank": item.get("rank"), "reason": "NO_SOURCE_FIELD_AVAILABLE"})
            continue
        if source_gate.normalize_text(raw_value) not in normalized_article:
            missing.append({"rank": item.get("rank"), "source_span": item.get("source_span"),
                             "source_sentence": item.get("source_sentence"),
                             "reason": "SOURCE_SPAN_NOT_FOUND_IN_RAW_ARTICLE"})
    return missing


def run_db_hybrid_selection(article_text: str, out_dir: str, article_id: str, source_level: str,
                             process: str = None, diagnostic_note: str = None,
                             dbs: dict = None, cost_guard_jpy: float = None,
                             shortlist_cache: dict = None, family_profile: str = "family_x") -> dict:
    """DB Hybrid方式でKey Phrase選定gateを1回実行する。戻り値は既存
    `run_key_phrase_selection`(Strategy L全文方式)と同じ最小契約
    (`status`/`parsed`/`original_items`)を満たし、追加でtelemetry用の
    `cost_jpy`/`model_id`/`shortlist_total_count`/`kp_backend`を含む。

    失敗時(shortlist過少・validator不合格・例外・モデルルーティング契約
    違反・source span不整合)は`DbHybridFailure`を送出する。
    `fallback_allowed`(既定True)がFalseの場合、呼び出し元はStrategy L
    へfallbackせずSTOPする(修正1回目、Opus L2所見B3)。

    `cost_guard_jpy`(既定`DEFAULT_COST_GUARD_JPY`)は1呼び出しあたりの
    runaway検知のみに用いる(修正1回目、Opus L2所見S4、Fable決定:
    PASS済みの結果は破棄せず採用し、`cost_guard_exceeded=true`を結果へ
    記録するのみ。記事単位の累積コスト上限は呼び出し元
    `er003_v1_n3_01_scaffold_generate.run_key_phrases`が
    `KP_ARTICLE_COST_CAP_JPY`で別途管理する)。fallback実発火の
    runtime evidence取得時にのみ、evidence/testスクリプトが明示的に
    小さい値へ上書きするための引数(通常のProduction配線からは渡さない、
    既定値のまま使う)。

    `shortlist_cache`(修正1回目、Opus L2所見S8、既定None):
    `run_key_phrases`のKey Phrase Set Redundancy QA retryループが
    渡す、呼び出し元スコープで保持する可変dict(article_textの
    sha256をkeyとする)。指定された場合、同一article_textに対する
    2回目以降の呼び出しはStage1/Wiktionary lookupを再実行せず
    キャッシュされたshortlistを再利用する(retryはprompt[diagnostic_
    note]再生成のみ、候補生成をやり直さない)。

    `family_profile`(KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-
    PRODUCTION-WIRING-01、既定"family_x"): Source Reference Contract
    (候補ID方式、`er030_key_phrase_db_hybrid_source_reference_
    contract_01`)のFamily別最終選定ルール差込点。現時点で実装済みなのは
    "family_x"のみ(既存呼び出し元は全てFamily Xのため既定値のまま
    影響を受けない)。"family_z"を指定した場合は明示的にNotImplemented
    Errorになる(Family Z DB Hybrid Core v2全体の採用は本管理IDの対象
    外、未配線のまま)。

    Source Reference Contract(候補ID方式、KEY-PHRASE-DB-HYBRID-SOURCE-
    REFERENCE-CONTRACT-PRODUCTION-WIRING-01、2026-09-28ユーザー正式
    採用): 本関数のselector呼び出しは、LLMに`source_sentence`/
    `source_span`を自由記述させず、shortlist候補ID(`source_candidate_
    id`、enum制約)のみを選ばせ、Python側でStage 1候補データから
    `source_sentence`/`source_span`を決定論的に復元する
    (`src_ref_contract.restore_source_fields`)。これによりLLMが
    表示delimiter付きの引用符を誤ってコピーする等の書式ゆらぎに
    よる`KEY_WORDS_STRUCTURE_INVALID`が構造的に発生しなくなる
    (詳細はTrial-06 REPORT参照)。既存Production validator
    (`p2g.validate_min_unit_selection`)・canonicalization・Source
    Consistency Gateはいずれも無変更のまま通す。"""
    # SF-7(Opus L2所見、修正1回目、2026-09-28): family_profileの妥当性を
    # 冒頭(Stage1/Wiktionary lookup前)でfail-closed確認する。未サポート値
    # (例: "family_z")は、Stage1候補生成・Wiktionary API呼び出し等の
    # 無駄な処理を発生させる前に即座にNotImplementedErrorで停止する。
    src_ref_contract._check_family_profile_supported(family_profile)
    os.makedirs(out_dir, exist_ok=True)
    guard = cost_guard_jpy if cost_guard_jpy is not None else DEFAULT_COST_GUARD_JPY
    dbs = dbs if dbs is not None else core.load_group1_dbs()
    title = extract_article_title(article_text)

    cache_key = _shortlist_cache_key(article_text) if shortlist_cache is not None else None
    if cache_key is not None and cache_key in shortlist_cache:
        s1r = shortlist_cache[cache_key]
    else:
        try:
            s1r = core.run_stage1_and_shortlist(article_text, dbs, title)
        except Exception as e:
            raise DbHybridFailure(
                "SELECTOR_EXCEPTION", f"stage1/shortlist構築に失敗しました: {type(e).__name__}: {e}",
                telemetry={"reason_code": "SELECTOR_EXCEPTION", "error": f"{type(e).__name__}: {e}"}) from e
        if cache_key is not None:
            shortlist_cache[cache_key] = s1r

    stage1, shortlist_info = s1r["stage1"], s1r["shortlist_info"]
    shortlist_count = shortlist_info["shortlist_total_count"]
    phrase_plus_important_count = (shortlist_info["phrase_included_count"] +
                                    shortlist_info["important_noun_included_count"])

    with open(os.path.join(out_dir, "db_hybrid_stage1_debug.json"), "w", encoding="utf-8") as f:
        json.dump(_serializable_stage1(stage1), f, ensure_ascii=False, indent=2)

    # 修正1回目(Opus L2所見S5、Fable決定): 総数閾値のみでは機械screening
    # の実質的な健全性チェックになっていなかったため、総数と
    # phrase+important_noun合計の両方を条件化する。
    if shortlist_count < MIN_SHORTLIST_COUNT or \
            phrase_plus_important_count < MIN_SHORTLIST_PHRASE_PLUS_IMPORTANT_COUNT:
        raise DbHybridFailure(
            "SHORTLIST_TOO_SMALL",
            f"shortlist件数(total={shortlist_count}, phrase+important={phrase_plus_important_count})"
            f"が閾値(total>={MIN_SHORTLIST_COUNT}, phrase+important>="
            f"{MIN_SHORTLIST_PHRASE_PLUS_IMPORTANT_COUNT})未満です",
            telemetry={"reason_code": "SHORTLIST_TOO_SMALL", "shortlist_total_count": shortlist_count,
                       "phrase_plus_important_count": phrase_plus_important_count})

    static_instructions = extract_static_instructions(bk.load_prompt_template())

    # KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-PRODUCTION-WIRING-01
    # (2026-09-28、ユーザー正式採用): shortlistの各候補へ一意なcandidate_id
    # (C1, C2, ...)を付与し、LLMには本文文字列(source_sentence/
    # source_span)を一切書かせず、選んだ候補のcandidate_idのみを返させる
    # (schema enum制約)。source_sentence/source_spanはPython側でStage 1
    # 候補データから決定論的に復元する(旧来の自由記述契約で発生していた
    # 表示delimiter付き引用符の誤コピー等の書式ゆらぎが構造的に発生しなく
    # なる、詳細はTrial-06 REPORT参照)。
    ids_result = src_ref_contract.assign_candidate_ids(shortlist_info["shortlist"])
    shortlist_with_ids = ids_result["shortlist_with_ids"]
    id_to_candidate = ids_result["id_to_candidate"]
    candidate_ids = ids_result["candidate_ids"]

    # SF-1(b)(Opus L2所見、修正1回目、2026-09-28): API呼び出し前にsource_span
    # 整合性を機械監査・補正する(surface_form/context_sentence_idの独立
    # 決定に起因する不整合の是正、詳細はsrc_ref_contract側docstring参照)。
    span_consistency_result = src_ref_contract.correct_shortlist_source_span_consistency(
        shortlist_with_ids, shortlist_info["sentence_reference"])
    shortlist_with_ids = span_consistency_result["shortlist_with_ids"]
    id_to_candidate = span_consistency_result["id_to_candidate"]
    candidate_ids = span_consistency_result["candidate_ids"]

    lightweight_message = src_ref_contract.build_lightweight_user_message(
        title, shortlist_with_ids, shortlist_info["sentence_reference"], static_instructions,
        family_profile=family_profile)
    if diagnostic_note:
        lightweight_message = lightweight_message + "\n\n" + diagnostic_note
    assert_no_full_article_body(lightweight_message, article_text)
    with open(os.path.join(out_dir, "keywords_selector_prompt.txt"), "w", encoding="utf-8") as f:
        f.write(lightweight_message)

    model = routing.require_model(process, routing.SUPPORT_MODEL) if process else prod.SELECTOR_MODEL
    usage_sink = []
    contract_violation_sink = []
    factory = src_ref_contract.make_instrumented_selector_factory(
        lightweight_message, model, candidate_ids, usage_sink,
        contract_violation_sink=contract_violation_sink)
    gate_result = src_ref_contract.run_source_reference_contract_gate(
        article_id, factory, article_text, id_to_candidate, shortlist_info["sentence_reference"],
        strategy_id=prod.STANDARD_STRATEGY_ID, family_profile=family_profile)
    status = gate_result["status"]
    parsed = gate_result["parsed"]
    model_id = gate_result["model_id"]
    response_id = gate_result["response_id"]
    restore_telemetry = gate_result.get("restore_telemetry", {})
    # KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01 修正1回目(2026-09-28、
    # ユーザー既決事項): topic欠損/単独無効をbackup_itemで機械的に置換
    # できた場合、statusは既にgate側でPASSへ更新済み(parsedも置換後の
    # 構成)。ここではobservability用にフラグ・理由のみ取り出す。
    topic_slot_filled_by_backup = gate_result.get("topic_slot_filled_by_backup", False)
    backup_substitution_reason = gate_result.get("backup_substitution_reason")
    attempts = [{
        "attempt": 1, "status": status,
        "validation_reasons": gate_result.get("validation_reasons", []),
        "item_reasons": gate_result.get("item_reasons", []),
        "raw_text": gate_result.get("raw_text"),
        "parsed": parsed, "model": model_id, "response_id": response_id,
        "restore_telemetry": {k: v for k, v in restore_telemetry.items() if k != "mismatch_details"},
        "topic_slot_filled_by_backup": topic_slot_filled_by_backup,
        "backup_substitution_reason": backup_substitution_reason,
    }]

    # 修正1回目(Opus L2所見B3): モデルルーティング契約違反は
    # gate内部で既にTECHNICAL_GENERATION_FAILEDへ吸収されているため、
    # ここで独立に検知しfallback不可のDbHybridFailureを送出する
    # (fallback先でも同じ契約違反が再発しうるため、fallbackで隠蔽しない)。
    if contract_violation_sink:
        violation = contract_violation_sink[0]
        raise DbHybridFailure(
            "MODEL_CONTRACT_VIOLATION",
            f"応答モデルが承認済みモデルと不一致です(期待: {violation['expected_model']}, "
            f"実際: {violation['actual_model']})。安全のためfallbackせず処理を停止します。",
            telemetry={"reason_code": "MODEL_CONTRACT_VIOLATION", **violation},
            fallback_allowed=False)

    usage_entry = usage_sink[0] if usage_sink else {"usage": {}}
    usage = usage_entry.get("usage", {})
    cost_jpy = pricing.cost_jpy_for_call(
        "openai", model_id or model, usage.get("input_tokens"),
        usage.get("cached_input_tokens"), usage.get("output_tokens"))
    cost_guard_exceeded = cost_jpy > guard

    # KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01(2026-09-28): 4+1構成
    # (key_phrase_role: important|topic)のcontract表示と、選定itemの役割
    # 内訳(role_counts、observability用。件数検証そのものはvalidatorが
    # 既に行っている)。parsed["items"]はPASS/INVALID問わず存在する
    # (schema上必須フィールドのため、モデルが値を返している限りenumの
    # 妥当性に関わらずカウント可能)。
    role_counts = dict(Counter(
        it.get("key_phrase_role") for it in ((parsed or {}).get("items") or []) if isinstance(it, dict)))

    runtime_metadata = {
        "article_id": article_id, "strategy_id": prod.STANDARD_STRATEGY_ID, "source_level": source_level,
        "kp_backend": "db_hybrid", "final_status": status, "model_id": model_id, "response_id": response_id,
        "cost_jpy": round(cost_jpy, 4), "cost_guard_exceeded": cost_guard_exceeded, "usage": usage,
        "selection_contract": "4plus1_v1", "role_counts": role_counts,
        "shortlist_total_count": shortlist_count,
        "shortlist_info": {
            "phrase_included_count": shortlist_info["phrase_included_count"],
            "important_noun_included_count": shortlist_info["important_noun_included_count"],
            "word_included_count": shortlist_info["word_included_count"],
        },
        # KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-PRODUCTION-WIRING-01
        "source_reference_contract": src_ref_contract.SOURCE_REFERENCE_CONTRACT_ID,
        "family_profile": family_profile,
        "candidate_count": len(candidate_ids),
        "candidate_mismatch_suspected_count": restore_telemetry.get("mismatch_count", 0),
        "candidate_mismatch_details": restore_telemetry.get("mismatch_details", []),
        "unresolved_candidate_id_count": len(restore_telemetry.get("unresolved", []) or []),
        # SF-1(b)(修正1回目、Opus L2所見): API呼び出し前のsource_span整合性
        # 監査・補正結果(corrected/excludedの内訳、非ブロッキング)。
        "source_span_consistency_audit": {
            "inconsistent_count": span_consistency_result["inconsistent_count"],
            "corrected_count": len(span_consistency_result["corrected"]),
            "excluded_count": len(span_consistency_result["excluded"]),
            "corrected": span_consistency_result["corrected"],
            "excluded": span_consistency_result["excluded"],
        },
        # SF-1(a)/SF-6(修正1回目、Opus L2所見): restore時点の防御的補正件数・
        # 同一candidate_id重複選択件数(いずれも非ブロッキング)。
        "span_corrected_in_restore_count": restore_telemetry.get("span_corrected_in_restore_count", 0),
        "duplicate_candidate_id_selection_count":
            restore_telemetry.get("duplicate_candidate_id_selection_count", 0),
        "attempts_detail": [{k: v for k, v in a.items() if k != "raw_text"} for a in attempts],
        # KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01 修正1回目(2026-09-28、
        # ユーザー既決事項): topic欠損/単独無効をbackup_item(important役割の
        # 予備候補)で機械的に補完した場合の観測用フラグ・理由。
        "topic_slot_filled_by_backup": topic_slot_filled_by_backup,
        "backup_substitution_reason": backup_substitution_reason,
    }
    with open(os.path.join(out_dir, "keywords_runtime_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(runtime_metadata, f, ensure_ascii=False, indent=2)

    if status != "KEY_WORDS_STRUCTURE_PASS":
        # KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01(2026-09-28、Fable
        # 判断F-3): 分岐先(status/fallback_allowed=True既定)は既存の
        # KEY_WORDS_STRUCTURE_INVALID経路と完全に同一のまま変更しない
        # (新しい分岐点を作らない)。telemetry識別のためのタグとして
        # `role_structure_invalid`のみ追加する(4+1件数不成立がreasonsに
        # 含まれるかをgrepするだけの非侵襲的な観測フラグ)。
        #
        # 修正1回目(Opus L2所見N1、2026-09-28): トップレベルreasons
        # (validation_reasons)だけでなく、per-itemのenum不正
        # (item_reasonsに入る、線423-424)も参照する(取りこぼし是正)。
        validation_reasons = gate_result.get("validation_reasons", []) or []
        item_reasons = gate_result.get("item_reasons", []) or []
        role_structure_invalid = (
            any("key_phrase_role" in r for r in validation_reasons)
            or any("key_phrase_role" in x for r in item_reasons for x in (r.get("reasons") or [])))
        raise DbHybridFailure(
            status, f"DB Hybrid selector gateがPASSしませんでした(status={status})",
            telemetry={"reason_code": status, "cost_jpy": round(cost_jpy, 4), "model_id": model_id,
                       "shortlist_total_count": shortlist_count,
                       "detail_reason_code": "ROLE_STRUCTURE_INVALID" if role_structure_invalid else None,
                       "topic_slot_filled_by_backup": topic_slot_filled_by_backup,
                       "backup_substitution_reason": backup_substitution_reason})

    # 修正1回目(Opus L2所見S3): source_span/source_sentenceの生article_text
    # 照合(canonicalization前、machine screeningのみ)。
    source_span_missing = _verify_source_spans_against_raw_article(parsed["items"], article_text)
    if source_span_missing:
        raise DbHybridFailure(
            "SOURCE_SPAN_NOT_IN_RAW_ARTICLE",
            f"選定item{len(source_span_missing)}件のsource_span/source_sentenceが"
            f"生article_textに見つかりませんでした: {source_span_missing}",
            telemetry={"reason_code": "SOURCE_SPAN_NOT_IN_RAW_ARTICLE",
                       "missing": source_span_missing, "cost_jpy": round(cost_jpy, 4),
                       "model_id": model_id})

    # 修正1回目(Opus L2所見S4、Fable決定): PASS済み結果はcost guard超過でも
    # 破棄・fallbackしない(より高価な全文方式への再課金を避ける)。
    # cost_guard_exceededは観測用フラグとしてのみ結果へ残す。

    # KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01(2026-09-28、Fable判断
    # F-4): 「5枠に入らなかった重要語・重要フレーズ」の後段UI向け構造化
    # データを、db_hybrid_stage1_debug.jsonと同じ母集団(shortlist_with_ids)
    # から、選ばれなかった候補を件数上限なし・既存shortlist順のまま
    # 保持する。validator/canonicalization/source gateを一切通過していない
    # 未検証の生候補であるため、verification_statusで明示する(表示件数・
    # UI配置はユーザー判断、ここでは決めない)。
    selected_candidate_ids = {
        it.get("source_candidate_id") for it in parsed["items"] if isinstance(it, dict)}
    auxiliary_candidates = [
        {**c, "verification_status": "unverified_reference_candidate"}
        for c in shortlist_with_ids if c.get("candidate_id") not in selected_candidate_ids
    ]
    with open(os.path.join(out_dir, "kp_auxiliary_candidates.json"), "w", encoding="utf-8") as f:
        json.dump({
            "selection_contract": "4plus1_v1",
            "source_reference_contract": src_ref_contract.SOURCE_REFERENCE_CONTRACT_ID,
            "note": ("Stage1/shortlistの候補のうち、最終5件に選ばれなかったもの。validator/"
                      "canonicalization/source consistency gateを一切通過していない未検証の"
                      "参考候補(件数上限なし、順序は既存shortlist出現順)。表示件数・UI配置は未定。"),
            "auxiliary_candidate_count": len(auxiliary_candidates),
            "candidates": auxiliary_candidates,
        }, f, ensure_ascii=False, indent=2)

    result = {
        "status": status, "parsed": parsed, "original_items": parsed["items"],
        "model_id": model_id, "response_id": response_id, "cost_jpy": round(cost_jpy, 4),
        "cost_guard_exceeded": cost_guard_exceeded,
        "shortlist_total_count": shortlist_count, "kp_backend": "db_hybrid",
        "source_reference_contract": src_ref_contract.SOURCE_REFERENCE_CONTRACT_ID,
        "selection_contract": "4plus1_v1", "role_counts": role_counts,
        "candidate_mismatch_suspected_count": restore_telemetry.get("mismatch_count", 0),
        "auxiliary_candidate_count": len(auxiliary_candidates),
        "attempts_detail": [{k: v for k, v in a.items() if k != "raw_text"} for a in attempts],
        "topic_slot_filled_by_backup": topic_slot_filled_by_backup,
        "backup_substitution_reason": backup_substitution_reason,
    }
    return result

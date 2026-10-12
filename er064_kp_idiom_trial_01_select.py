# ============================================================
# er064_kp_idiom_trial_01_select.py
# FAMILY-X-KP-IDIOM-EXTRACTION-SELECTION-TRIAL-01 / Phase B5 (d) + Phase C 実行ラッパ(Trial専用)
# - 共有Template(b1_p2_keywords_l_prompt_template.txt)は変更しない。
# - Family X DB Hybrid専用guidance(src_ref_contract._FAMILY_X_SOURCE_REFERENCE_SELECTION_GUIDANCE)の
#   「残りは[phrase/idiom/phrasal verb候補]区分を優先」行を、Trial用コピーで『置換』する(追記ではない)。
# - 選定gate/schema/validator/canonicalization/Redundancy QAはProduction関数をそのまま呼ぶ。
# - Production経路(run_db_hybrid_selection等)には何も配線しない。
# ============================================================
from __future__ import annotations

import difflib
import hashlib
import json
import os
import time

import er003_b1_p2_keywords as bk
import er003_key_words_canonicalization as kc
import er003_key_words_production as prod
import er006_model_routing_contract_01 as routing
import er009_n1_routing_governance_10_actual_model_cost as pricing
import er011_key_phrase_set_redundancy_qa_01 as redundancy_qa
import er030_key_phrase_db_hybrid_selector_01 as selector01
import er030_key_phrase_db_hybrid_source_reference_contract_01 as src_ref

MODEL = routing.SUPPORT_MODEL  # gpt-6-luna(Productionの Family X KP選定と同一。PM_GOVERNANCE 25節『Production比較可能性』例外)

# --- (d) guidance ------------------------------------------------------------------
_OLD_LINES = """- 残りは、[phrase / idiom / phrasal verb候補]区分を優先してください。
  良い候補が不足する場合のみ[word候補]区分で補ってください。
"""

_NEW_LINES_TMPL = """- 残りの枠は、[phrase / idiom / phrasal verb候補]と[word候補]を、区分名ではなく次の基準で比較して選んでください。
  最優先は、本文中で字義どおりではなく非字義的に使われている表現(慣用句・比喩・擬人化・組み合わさると特別な意味になる語句)のうち、
  初回のリスニングで意味を取りにくいものです。区分名(idiom等)やevidenceラベルがあるだけでは選ばないでください。
  構成語から意味を容易に推測できる透明な表現や、学習者がすでに知っている可能性が高い高頻度の定型表現は、区分がphrase/idiomでも優先度を下げてください。
  {level_line}
  evidenceが llm_noncompositional または placeholder_title の候補は、辞書の完全一致以外の方法で見つけた補助候補です。
  他の候補と同じ基準で評価し、本文中で非字義的でない、または意味を推測しやすい場合は選ばないでください。
  [phrase / idiom / phrasal verb候補]に適切な候補が少ない場合のみ、[word候補]区分で補ってください。
"""

LEVEL_LINE = {
    "std": "対象はA2相当の学習者です。日常で頻出する基本的な句は既知として扱い、優先度を下げてください。",
    "adv": "対象はB1相当の学習者です。慣用句・比喩・文脈で意味が変わるコロケーションは初見で難しい可能性が高いものとして扱ってください。句動詞でも、本文中で基本義と異なる意味(抽象的な主語や数値が主語など)で使われ、構成語から意味を推測しにくいものは、非字義的表現として同列に評価してください。構成語どおりの意味で使われている基本的な句動詞や高頻度コロケーションは既知とみなして構いません。",
}


def prod_guidance() -> str:
    return src_ref._FAMILY_X_SOURCE_REFERENCE_SELECTION_GUIDANCE


def trial_guidance(level: str) -> str:
    base = prod_guidance()
    assert base.count(_OLD_LINES) == 1, "Production guidanceの置換対象行が変わっています"
    return base.replace(_OLD_LINES, _NEW_LINES_TMPL.format(level_line=LEVEL_LINE[level]))


def guidance_diff(level: str) -> str:
    a = prod_guidance().splitlines(keepends=True)
    b = trial_guidance(level).splitlines(keepends=True)
    return "".join(difflib.unified_diff(a, b, "production_guidance(Before)", f"trial_guidance_{level}(After)"))


def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# --- 費用計測つきclient ---------------------------------------------------------------
class UsageClient:
    """openai clientのresponses.createをラップし、全callのusageを記録する(コスト実測用)。
    リトライ(gate内の技術的再試行)を含めて全件記録する。"""

    def __init__(self, label: str = ""):
        from dotenv import load_dotenv
        load_dotenv()
        from openai import OpenAI
        self._real = OpenAI()
        self.log = []
        self.label = label
        outer = self

        class _Resp:
            def create(self, **kw):
                t0 = time.time()
                started_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")
                r = outer._real.responses.create(**kw)
                u = getattr(r, "usage", None)
                usage = {}
                if u is not None:
                    usage = {"input_tokens": getattr(u, "input_tokens", None),
                             "output_tokens": getattr(u, "output_tokens", None),
                             "cached_input_tokens": getattr(getattr(u, "input_tokens_details", None),
                                                            "cached_tokens", 0) or 0}
                outer.log.append({"label": outer.label, "started_at": started_at, "model": r.model, "response_id": r.id, "usage": usage,
                                  "elapsed_sec": round(time.time() - t0, 3),
                                  "cost_jpy": pricing.cost_jpy_for_call(
                                      "openai", r.model, usage.get("input_tokens"),
                                      usage.get("cached_input_tokens"), usage.get("output_tokens"))})
                return r
        self.responses = _Resp()

    def total_cost(self) -> float:
        return round(sum(x["cost_jpy"] for x in self.log), 4)


# --- メッセージ構築(Trial用) ------------------------------------------------------------------
def trial_display_type(c: dict) -> str:
    # M2: LLM由来候補はidiom固定にせず中立のphraseで表示する(区分名による誘導を避ける)
    if c.get("evidence") == "llm_noncompositional":
        return "phrase"
    return selector01._display_type(c)


def trial_evidence(c: dict) -> str:
    ev = c.get("evidence")
    if ev == "llm_noncompositional":
        return "llm_noncompositional"
    if ev == "placeholder_title":
        return f"placeholder_title[{c.get('matched_title')}]"
    return selector01._compact_evidence_string(c)


def build_message(article_title: str, shortlist_with_ids: list, sentence_reference: dict,
                  static_instructions: str, guidance: str) -> str:
    """src_ref.build_lightweight_user_message と同一構成。違いはguidance文字列と
    evidence表示関数を差し替えられる点のみ(Production関数はguidanceを内部固定のため、
    Trialではコピーを持つ)。guidance=prod_guidance() を渡したとき、Production出力と
    完全一致することをtestで固定する。"""
    important = [c for c in shortlist_with_ids if c.get("important_noun_phrase_candidate")]
    phrase = [c for c in shortlist_with_ids
              if not c.get("important_noun_phrase_candidate") and c["unit_type"] != "word"]
    word = [c for c in shortlist_with_ids
            if not c.get("important_noun_phrase_candidate") and c["unit_type"] == "word"]
    lines = [static_instructions.rstrip(), ""]
    lines.append(f"【Topic】title: {article_title}")
    lines.append("")
    lines.append("【重要な単語・単語群候補】")
    lines.extend([src_ref.format_candidate_line_with_id(c, trial_display_type, trial_evidence) for c in important]
                 or ["(なし)"])
    lines.append("")
    lines.append("【phrase / idiom / phrasal verb候補】")
    lines.extend([src_ref.format_candidate_line_with_id(c, trial_display_type, trial_evidence) for c in phrase]
                 or ["(なし)"])
    lines.append("")
    lines.append("【word候補】")
    lines.extend([src_ref.format_candidate_line_with_id(c, trial_display_type, trial_evidence) for c in word]
                 or ["(なし)"])
    lines.append("")
    lines.append("【SENTENCE REFERENCE】(文脈参照専用。この表の文字列をそのままitemへ書かないでください)")
    for sid in sorted(sentence_reference, key=lambda s: int(s[1:])):
        lines.append(f'{sid}: "{sentence_reference[sid]}"')
    lines.append(guidance.rstrip())
    return "\n".join(lines) + "\n"


# --- 選定(1回) -----------------------------------------------------------------------------
def run_selection(article_text: str, shortlist_info: dict, guidance: str, client: UsageClient,
                  article_id: str = "kp_idiom_trial", out_dir: str = None, diagnostic_note: str = None) -> dict:
    """Production関数(assign ids / correct span / selector factory / source reference gate /
    raw article照合)をそのまま呼ぶ。API call 1回(gate内の技術的再試行を除く)。"""
    title = selector01.extract_article_title(article_text)
    static = selector01.extract_static_instructions(bk.load_prompt_template())
    ids = src_ref.assign_candidate_ids(shortlist_info["shortlist"])
    corr = src_ref.correct_shortlist_source_span_consistency(
        ids["shortlist_with_ids"], shortlist_info["sentence_reference"])
    swi, id2c, cids = corr["shortlist_with_ids"], corr["id_to_candidate"], corr["candidate_ids"]
    msg = build_message(title, swi, shortlist_info["sentence_reference"], static, guidance)
    if diagnostic_note:  # Productionのredundancy retryと同じ方式(message末尾へ追記)
        msg = msg + chr(10) * 2 + diagnostic_note
    selector01.assert_no_full_article_body(msg, article_text)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        open(os.path.join(out_dir, "selector_prompt.txt"), "w", encoding="utf-8").write(msg)
    usage_sink, viol = [], []
    # UsageClient経由でProductionのselector factoryを呼ぶ(usage/費用を全call記録)
    factory = src_ref.make_instrumented_selector_factory(msg, MODEL, cids, usage_sink,
                                                         contract_violation_sink=viol, client=client)
    gate = src_ref.run_source_reference_contract_gate(
        article_id, factory, article_text, id2c, shortlist_info["sentence_reference"],
        strategy_id=prod.STANDARD_STRATEGY_ID, family_profile="family_x")
    out = {"status": gate["status"], "parsed": gate["parsed"], "validation_reasons": gate.get("validation_reasons"),
           "item_reasons": gate.get("item_reasons"), "model_id": gate.get("model_id"),
           "topic_slot_filled_by_backup": gate.get("topic_slot_filled_by_backup"),
           "backup_substitution_reason": gate.get("backup_substitution_reason"),
           "candidates": [{k: c.get(k) for k in ("candidate_id", "surface_form", "canonical_form", "unit_type",
                                                 "evidence", "matched_title", "matched_dbs", "db_categories",
                                                 "context_sentence_id", "important_noun_phrase_candidate")}
                          for c in swi],
           "excluded_by_span_consistency": corr["excluded"], "prompt_sha256": sha(msg),
           "contract_violation": viol}
    if gate["status"] == "KEY_WORDS_STRUCTURE_PASS":
        out["source_span_missing"] = selector01._verify_source_spans_against_raw_article(
            gate["parsed"]["items"], article_text)
        out["original_items"] = gate["parsed"]["items"]
    return out


def run_canonicalization_and_qa(article_text: str, original_items: list, client: UsageClient) -> dict:
    """Production関数(kc.run_canonicalization_gate / merge / redundancy_qa gate)を使用。
    経路: Productionの run_key_phrase_canonicalization / run_key_phrase_redundancy_qa と同等。"""
    template = kc.load_prompt_template()
    um = kc.build_user_message(original_items, article_text, template=template)

    def make_factory():
        return kc.make_canonicalization_fn(um, client=client, model=MODEL)

    parsed, status, attempts, model_id, response_id = kc.run_canonicalization_gate(make_factory, original_items)
    out = {"canonicalization_status": status,
           "canonicalization_attempts": [{k: v for k, v in a.items() if k not in ("raw_text",)} for a in attempts]}
    if status not in ("CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"):
        return out
    merged = kc.merge_canonicalization_result(original_items, parsed["items"])
    out["merged"] = merged
    qm = redundancy_qa.build_user_message(merged["items"], article_text)

    def make_qa():
        return redundancy_qa.make_redundancy_qa_fn(qm, client=client, model=MODEL)

    ranks = [it["rank"] for it in merged["items"]]
    qparsed, qstatus, qattempts, qmodel, qresp = redundancy_qa.run_redundancy_qa_gate(make_qa, ranks)
    out["redundancy_status"] = qstatus
    out["redundancy_duplicate_pairs"] = qattempts[-1].get("duplicate_pairs", []) if qattempts else []
    return out


def run_vl(article_text: str, client: UsageClient, article_id: str = "kp_idiom_trial_vl") -> dict:
    """VL: 既存Strategy L全文方式(Production関数をそのまま呼ぶ。本文全文をpromptへ送る既存経路)。"""
    template = bk.load_prompt_template()
    um = bk.build_user_message(article_text, template=template)

    def factory():
        return bk.make_selector_fn(um, client=client, model=MODEL)

    parsed, status, attempts, model_id, response_id = prod.run_production_selection_gate(
        article_id, factory, article_text, strategy_id=prod.STANDARD_STRATEGY_ID,
        max_attempts=prod.MAX_PRODUCTION_RETRY_ATTEMPTS)
    return {"status": status, "parsed": parsed, "model_id": model_id, "response_id": response_id,
            "attempts": len(attempts), "prompt_sha256": sha(um)}

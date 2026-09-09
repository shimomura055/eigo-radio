# ============================================================
# er011_household_unified_final_candidate_01_run.py
# 管理ID: HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01(Trial扱い、Production配線なし)
# ============================================================
# 目的(ユーザー決定 2026-09-09、背景はFable委任文参照): Household
# (Discovery/Why、Ledger v5)の最終候補を一本化する。Primary= Discovery
# Focus Module軽微改善(FAMILY-A-DISCOVERY-STAGE4-CAUTIONARY-LANGUAGE-
# TRIAL-10の`cautionary_constrained`条件[Part B案1、未承認候補だがユーザー
# がHousehold一本化の主軸として使うことを決定済み])を使い、A2/B1Bの記事→
# Support(Preview/Comment/Key Phrase/日本語タイトル)→Audio(TTS+ASR検証→
# Assembly+SFX)→試聴artifactまでを、既存Production関数のみ(無変更で直接
# 呼ぶ)で作る。**Trial(Production実装ではない)**。Production/Prompt/
# 共有module/registry/SSOT編集・Git操作は一切行わない。
#
# 再利用(import・無変更、read-onlyでの参照のみ):
#   - er011_discovery_stage4_cautionary_language_trial_10(t10):
#     CAUTIONARY_FOCUS_BLOCK(Part B案1の最小制約文言、Gate 4済み)/
#     HOUSEHOLD_TOPIC_JA / HOUSEHOLD_LEDGER_PATH。t10自身のOUT_DIR
#     (`er011_output/discovery_stage4_cautionary_language_trial_10/`)や
#     そのREPORTへは一切書き込まない(並列稼働中の別担当領域のため)。
#   - er003_v1_n3_01_articles_generate(prod_gen): build_common_block/
#     build_prompt/run_one_pattern(Point Role Planning/Value QA/Point
#     Overlap QA/Diagnostic Full Retry[Loop Budget 2]/Fact Checker/
#     Ledger Deviation Checker/Evidence Compression含む既存Production
#     経路そのもの)。無変更。
#   - er003_v1_n3_01_scaffold_generate(sc): split_article_text/
#     run_a2_scaffold/run_b1_scaffold/run_key_phrases。無変更。
#   - er003_v1_n3_01_tts_generate(tts_gen): generate_a2_segments/
#     generate_b1_segments/JAPANESE_TITLES。無変更(JAPANESE_TITLESへの
#     .update()はA2のtheme_id gap用の人手供給、既存前例[FAMILY-A-
#     COMPLETION-A2-TREND-END-TO-END-01]と同一パターン)。
#   - er003_v1_n3_01_assemble(asm): stage_assemble_a2/stage_assemble_b1/
#     derive_a_family_required_structure/verify_episode_audio_
#     validation_gate。無変更。
#   - audio_review_player(arp): 標準player部品(Source列なし、
#     min-width 360px、PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-STANDARD-
#     FORMAT-11)。無変更。
#
# 費用上限: 合計¥300(外部呼び出し費用別掲、cost_stage()で都度実測確認)。
# 同期実行のみ。バックグラウンド待機・二重起動禁止。
#
# 実行方法(root直下から):
#   .venv/Scripts/python.exe er011_household_unified_final_candidate_01_run.py [stage ...]
#   省略時は全stageを順に同期実行する。
from __future__ import annotations

import difflib
import hashlib
import json
import os
import re
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

# PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-01: 正式リリース前はStandard同期を使う。
os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

import audio_review_player as arp
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as prod_gen
import er003_v1_n3_01_assemble as asm
import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_n3_01_tts_generate as tts_gen
import er005_cost_logger as cl
import er011_discovery_stage4_cautionary_language_trial_10 as t10  # 読み取り専用の再利用(t10のOUT_DIRへは書き込まない)

THEME_ID = "household_unified_final_candidate_01"
OUT_DIR = f"er011_output/{THEME_ID}"
BUDGET_JPY_CAP = 300.0

HOUSEHOLD_TOPIC_JA = t10.HOUSEHOLD_TOPIC_JA
HOUSEHOLD_LEDGER_PATH = t10.HOUSEHOLD_LEDGER_PATH  # v5(無変更、read-only)
CAUTIONARY_FOCUS_BLOCK = t10.CAUTIONARY_FOCUS_BLOCK  # Part B案1、未承認候補(Gate 4済み、無変更のまま流用)

LEVELS = {
    "a2": {"label": "A2", "instruction": prod_gen.A2_KAI1_INSTRUCTION, "stage_tag": "writer_a2", "gate_level": "A2"},
    "b1b": {"label": "B1B", "instruction": prod_gen.B1_B_DIRECT_INSTRUCTION, "stage_tag": "writer_b1", "gate_level": "B1"},
}

# 既存Household完成版(旧A2、JAPANESE_TITLES["household"])のタイトルをそのまま
# 流用する(本Trialのtheme_idはJAPANESE_TITLESに未登録のためgapが生じる。
# 既存前例[FAMILY-A-COMPLETION-A2-TREND-END-TO-END-01継続]と同一パターン、
# 新しい主張・数字を追加しない)。
EXISTING_HOUSEHOLD_A2_JAPANESE_TITLE = tts_gen.JAPANESE_TITLES["household"]

# ------------------------------------------------------------
# Part A保険文検出regex(FAMILY-A-DISCOVERY-STAGE4-CAUTIONARY-LANGUAGE-
# TRIAL-10のcomparisonスクリプトと同一定義、read-onlyで転記して再利用)。
# ------------------------------------------------------------
_VERB = r"(?:check|consult|ask|see|refer to|look at|read|follow)"
_SOURCE = r"(?:instructions?|manuals?|guides?|guidelines?|manufacturers?|makers?|professionals?|experts?|labels?|packagings?|packages?)"
INSURANCE_RE = re.compile(_VERB + r"[^.!?]{0,80}" + _SOURCE, re.IGNORECASE)


def sha(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def save_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def detect_insurance_sentences(article_text: str) -> list:
    return [m.group(0) for m in INSURANCE_RE.finditer(article_text or "")]


# ============================================================
# 費用実測(全provider対応の汎用版、er012_b_family_production_runner_01の
# compute_cost_jpy_so_farと同一ロジックをベースに、openaiのweb_search_call
# [Fact Checker]も加算するよう拡張。単価は既存OFFICIAL_SOURCEをそのまま
# 参照、独自の単価は一切定義しない)。
# ============================================================
USD_JPY = 160.0
_PRICING = json.load(open("er005_output/cost_baseline_01/pricing_snapshot.json", encoding="utf-8"))["prices"]


def _price(provider, model, meter, tier="Standard"):
    for p in _PRICING:
        if p["provider"] == provider and p["model"] == model and p["meter"] == meter and p.get("tier", "Standard") == tier:
            return p["price"]
    raise KeyError((provider, model, meter, tier))


def _call_cost_usd(r: dict) -> tuple:
    """(cost_usd, unpriced: bool)を返す。既存OFFICIAL_SOURCE
    (pricing_snapshot.json)に無い組み合わせはunpriced=Trueとして0円計上し、
    cost_summary.jsonのunpriced_recordsへ記録する(黙って無視しない)。"""
    provider = r.get("provider")
    model = r.get("model_id") or r.get("model")
    it, ot = r.get("input_tokens") or 0, r.get("output_tokens") or 0
    ct = r.get("cached_input_tokens") or 0
    try:
        if provider == "openai":
            billable_in = max(it - ct, 0)
            cost = (billable_in / 1e6) * _price("openai", model, "input_tokens") \
                + (ct / 1e6) * _price("openai", model, "cached_input_tokens") \
                + (ot / 1e6) * _price("openai", model, "output_tokens")
            wsc = r.get("web_search_call_count") or 0
            cost += (wsc / 1000) * _price("openai", "N/A (tool, all models)", "web_search_call")
            return cost, False
        if provider == "gemini":
            return (it / 1e6) * _price("gemini", model, "input_tokens") \
                + (ot / 1e6) * _price("gemini", model, "output_tokens"), False
        if provider == "openai_asr":
            return (it / 1e6) * _price("openai_asr", model, "input_tokens") \
                + (ot / 1e6) * _price("openai_asr", model, "output_tokens"), False
        return 0.0, True
    except KeyError:
        return 0.0, True


def compute_cost_jpy_so_far() -> dict:
    log_path = f"{OUT_DIR}/raw_usage_log.jsonl"
    if not os.path.exists(log_path):
        return {"total_jpy": 0.0, "by_provider_jpy": {}, "unpriced_records": 0, "total_records": 0}
    total_usd, by_provider, unpriced = 0.0, {}, 0
    n = 0
    with open(log_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            cost, up = _call_cost_usd(rec)
            total_usd += cost
            by_provider[rec.get("provider")] = by_provider.get(rec.get("provider"), 0.0) + cost
            unpriced += int(up)
            n += 1
    return {
        "total_jpy": round(total_usd * USD_JPY, 2),
        "by_provider_jpy": {k: round(v * USD_JPY, 2) for k, v in by_provider.items()},
        "unpriced_records": unpriced, "total_records": n,
    }


def cost_stage() -> dict:
    result = compute_cost_jpy_so_far()
    save_json(f"{OUT_DIR}/cost_summary.json", result)
    print(f"[{THEME_ID}][cost] 実測合計={result['total_jpy']} JPY (上限{BUDGET_JPY_CAP}) "
          f"by_provider={result['by_provider_jpy']} unpriced_records={result['unpriced_records']}")
    if result["total_jpy"] > BUDGET_JPY_CAP:
        raise RuntimeError(f"費用上限超過(実測{result['total_jpy']}円 > 上限{BUDGET_JPY_CAP}円)。STOP。")
    return result


# ============================================================
# Gate 4相当の静的確認(t10自身が既にimport時のassertで検証済みだが、
# 本タスク独自の出力先へも記録として再確認・保存する。Production関数の
# 再定義・monkeypatchは行っていない)。
# ============================================================
def gate4_check_stage() -> dict:
    used_names = ["THEMES", "build_common_block", "build_prompt", "A2_KAI1_INSTRUCTION",
                  "B1_B_DIRECT_INSTRUCTION", "run_one_pattern", "POINT_OVERLAP_ARTICLE_RETRY_MAX"]
    not_reassigned = all(name in vars(prod_gen) for name in used_names)
    placeholder_present = "{editorial_type_module_block}" in prod_gen.COMMON_BLOCK_TEMPLATE

    master_full_text = ab01.load_master_full_text()
    verified_ledger_text = open(HOUSEHOLD_LEDGER_PATH, encoding="utf-8").read()
    baseline_common_block = prod_gen.build_common_block(
        master_full_text, HOUSEHOLD_TOPIC_JA, verified_ledger_text, editorial_type_module_block="")
    cautionary_common_block = prod_gen.build_common_block(
        master_full_text, HOUSEHOLD_TOPIC_JA, verified_ledger_text,
        editorial_type_module_block=CAUTIONARY_FOCUS_BLOCK)
    ops = [op for op in difflib.SequenceMatcher(
        a=baseline_common_block, b=cautionary_common_block, autojunk=False).get_opcodes() if op[0] != "equal"]
    single_clean_insert = len(ops) == 1 and ops[0][0] == "insert"
    ledger_has_v5_marker = "v5" in verified_ledger_text
    point_overlap_retry_max = prod_gen.POINT_OVERLAP_ARTICLE_RETRY_MAX

    result = {
        "prod_gen_used_names_present_and_not_reassigned": not_reassigned,
        "common_block_template_has_editorial_type_module_block_placeholder": placeholder_present,
        "cautionary_vs_baseline_diff_is_single_clean_insert": single_clean_insert,
        "ledger_has_v5_marker": ledger_has_v5_marker,
        "point_overlap_article_retry_max_loop_budget": point_overlap_retry_max,
        "cautionary_focus_block_source": ("er011_discovery_stage4_cautionary_language_trial_10.CAUTIONARY_FOCUS_"
                                          "BLOCK(read-only reuse, unmodified, Gate 4 already PASSed there)"),
        "conclusion": "PASS" if (not_reassigned and placeholder_present and single_clean_insert
                                  and ledger_has_v5_marker) else "FAIL_NEEDS_REVIEW",
    }
    save_json(f"{OUT_DIR}/audit/gate4_check.json", result)
    print(f"[{THEME_ID}] gate4_check_stage: {result['conclusion']}")
    if result["conclusion"] != "PASS":
        raise RuntimeError(f"Gate 4静的確認失敗: {result}")
    return result


# ============================================================
# Step 1: 記事生成(cautionary_constrained条件、A2/B1B各1本、Loop Budget等
# 既存経路のまま。再抽選[N追加]は行わない)。
# ============================================================
def generate_article_stage(level: str) -> dict:
    meta = LEVELS[level]
    out_dir = f"{OUT_DIR}/{level}"
    client = vfl01.get_client()
    master_full_text = ab01.load_master_full_text()
    verified_ledger_text = open(HOUSEHOLD_LEDGER_PATH, encoding="utf-8").read()
    common_block = prod_gen.build_common_block(
        master_full_text, HOUSEHOLD_TOPIC_JA, verified_ledger_text,
        editorial_type_module_block=CAUTIONARY_FOCUS_BLOCK)
    prompt = prod_gen.build_prompt(common_block, meta["instruction"])

    t0 = time.time()
    with cl.logging_context(THEME_ID, meta["stage_tag"]):
        result = prod_gen.run_one_pattern(
            client, THEME_ID, meta["label"], prompt, verified_ledger_text, HOUSEHOLD_TOPIC_JA, out_dir)
    elapsed = round(time.time() - t0, 2)

    article_text = result.get("article_text")
    insurance_hits = detect_insurance_sentences(article_text) if article_text else []
    summary = {k: v for k, v in result.items() if k != "article_text"}
    summary["elapsed_seconds"] = elapsed
    summary["word_count"] = len((article_text or "").split())
    summary["insurance_sentence_hits_broad_regex"] = insurance_hits
    summary["insurance_sentence_hit_count"] = len(insurance_hits)
    save_json(f"{out_dir}/run_summary.json", summary)
    print(f"[{THEME_ID}][{level}] article: status={result.get('status')} "
          f"fact_verdict={result.get('fact_verdict')} ledger_status={result.get('ledger_status')} "
          f"word_count={summary['word_count']} insurance_hits={len(insurance_hits)} elapsed={elapsed}s")
    return summary


# ============================================================
# Step 2: Scaffold(Preview/Comment、Production関数を無変更で直接呼ぶ)
# ============================================================
def scaffold_stage(level: str) -> dict:
    out_dir = f"{OUT_DIR}/{level}"
    with open(f"{out_dir}/article.md", encoding="utf-8") as f:
        article_text = f.read()
    parts = sc.split_article_text(article_text)
    save_json(f"{out_dir}/parts.json", parts)
    client = sc.get_client()
    run_fn = sc.run_a2_scaffold if level == "a2" else sc.run_b1_scaffold
    with cl.logging_context(THEME_ID, f"scaffold_{level}"):
        support = run_fn(client, parts, out_dir, article_text)
    status = {k: v.get("status") for k, v in support.items()}
    print(f"[{THEME_ID}][{level}] scaffold(Preview/Comment)完了。status={status}")
    return {"support_status": status}


# ============================================================
# Step 3: Key Phrase(Selection→Canonicalization→Redundancy QA、
# Production関数sc.run_key_phrasesを無変更で直接呼ぶ)
# ============================================================
def keyphrase_stage(level: str) -> dict:
    meta = LEVELS[level]
    out_dir = f"{OUT_DIR}/{level}"
    kp_dir = f"{out_dir}/key_phrases"
    with open(f"{out_dir}/article.md", encoding="utf-8") as f:
        article_text = f.read()
    article_id = f"HOUSEHOLD_UNIFIED_FINAL_CANDIDATE_01_{meta['label']}"
    source_level = "B1-B(N3-01, direct generation)" if level == "b1b" else "A2(V2改1, N3-01)"
    process = "B1_SUPPORT" if level == "b1b" else "A2_SUPPORT"
    with cl.logging_context(THEME_ID, f"keyphrase_{level}"):
        kp = sc.run_key_phrases(article_text, kp_dir, article_id, source_level, process=process)
    sel_status = kp["selection"]["status"]
    canon_status = (kp.get("canonicalization") or {}).get("status")
    redundancy_status = (kp.get("redundancy_qa") or {}).get("status")
    summary = {"selection_status": sel_status, "canonicalization_status": canon_status,
               "redundancy_qa_status": redundancy_status, "redundancy_retry_log": kp.get("redundancy_retry_log")}
    save_json(f"{out_dir}/audit/run_key_phrases_result_summary.json", summary)
    print(f"[{THEME_ID}][{level}] key phrase: selection={sel_status} canonicalization={canon_status} "
          f"redundancy={redundancy_status}")
    if kp.get("canonicalization") is None or canon_status not in (
            "CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"):
        raise RuntimeError(f"[{level}] Key Phraseパイプライン失敗、STOP。selection={sel_status} "
                            f"canonicalization={canon_status}")
    if redundancy_status == "REDUNDANCY_NG":
        raise RuntimeError(f"[{level}] Key Phrase Redundancy QAがretry上限到達後もNG_REVIEW_REQUIRED、STOP。"
                            "既存Loop Budgetを独自判断で回避しない。")
    return summary


# ============================================================
# Step 4: 日本語タイトルgap fill(A2のみ、既存Householdタイトルを流用)
# ============================================================
def japanese_title_stage() -> dict:
    tts_gen.JAPANESE_TITLES.update({THEME_ID: EXISTING_HOUSEHOLD_A2_JAPANESE_TITLE})
    note = {
        "gap": "JAPANESE_TITLES辞書にtheme_id(household_unified_final_candidate_01)未登録のためKeyErrorが"
               "発生する(既存前例[FAMILY-A-COMPLETION-A2-TREND-END-TO-END-01継続]と同一の既知gap)。",
        "resolution": "既存Householdの日本語タイトルをそのまま流用(新しい主張・数字は追加しない)。",
        "reused_title": EXISTING_HOUSEHOLD_A2_JAPANESE_TITLE,
        "reused_from": "er003_v1_n3_01_tts_generate.JAPANESE_TITLES['household']",
    }
    save_json(f"{OUT_DIR}/audit/a2_japanese_title_gap_note.json", note)
    print(f"[{THEME_ID}][a2] JAPANESE_TITLES登録(gap fill・既存Household流用): "
          f"{EXISTING_HOUSEHOLD_A2_JAPANESE_TITLE!r}")
    return note


# ============================================================
# Step 5: TTS(Production関数を無変更で直接呼ぶ)
# ============================================================
def tts_stage(level: str) -> dict:
    theme = {"theme_id": THEME_ID, "out_dir": OUT_DIR}
    with cl.logging_context(THEME_ID, f"tts_{level}"):
        result = tts_gen.generate_a2_segments(theme) if level == "a2" else tts_gen.generate_b1_segments(theme)
    print(f"[{THEME_ID}][{level}] TTS完了。segment_status/key_phrase_statusを確認してください。")
    return result


# ============================================================
# Step 6: Assembly(Gate OFF経路[内部で自動実行]) + Gate opt-in ON経路
# (OPEN-129、read-only)
# ============================================================
def assembly_stage(level: str) -> dict:
    theme = {"theme_id": THEME_ID, "out_dir": OUT_DIR}
    out_dir = f"{OUT_DIR}/{level}"
    assemble_fn = asm.stage_assemble_a2 if level == "a2" else asm.stage_assemble_b1
    with cl.logging_context(THEME_ID, f"assemble_{level}"):
        try:
            result = assemble_fn(theme)
            result["gate_off_result"] = "PASS"
        except RuntimeError as e:
            result = {"status": "GATE_BLOCKED", "gate_off_result": "BLOCKED", "error": str(e)}
    print(f"[{THEME_ID}][{level}] Assembly(Gate OFF経路)結果: {result.get('gate_off_result')}")

    gate_on = {"gate_on_result": "SKIPPED_ASSEMBLE_NOT_PASS"}
    if result.get("gate_off_result") == "PASS":
        rs = asm.derive_a_family_required_structure(LEVELS[level]["gate_level"])
        try:
            asm.verify_episode_audio_validation_gate(out_dir, LEVELS[level]["gate_level"], required_structure=rs)
            gate_on = {"gate_on_result": "PASS"}
        except RuntimeError as e:
            gate_on = {"gate_on_result": "BLOCKED", "gate_on_message": str(e)[:1200]}
    print(f"[{THEME_ID}][{level}] Gate opt-in ON経路結果: {gate_on.get('gate_on_result')}")
    result["gate_opt_in_result"] = gate_on
    save_json(f"{out_dir}/audit/assembly_and_gate_summary.json", result)
    return result


# ============================================================
# Level単位オーケストレーション
# ============================================================
def run_level(level: str) -> dict:
    print(f"===== [{THEME_ID}] level={level} 開始 =====")
    article_summary = generate_article_stage(level)
    if article_summary.get("status") != "OK":
        print(f"[{THEME_ID}][{level}] 記事status={article_summary.get('status')}(OKではない)。"
              "このレベルの追加生成(再抽選)は行わず、Support/Audioには進みません。")
        return {"level": level, "article": article_summary, "stopped_at": "article_generation"}

    scaffold_summary = scaffold_stage(level)
    kp_summary = keyphrase_stage(level)
    if level == "a2":
        japanese_title_stage()
    tts_result = tts_stage(level)
    assembly_result = assembly_stage(level)

    return {
        "level": level, "article": article_summary, "scaffold": scaffold_summary,
        "key_phrase": kp_summary, "tts": tts_result, "assembly": assembly_result,
    }


def main() -> dict:
    stages = sys.argv[1:] or ["all"]
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")

    if stages == ["all"]:
        gate4_check_stage()
        results = {}
        for level in ("a2", "b1b"):
            try:
                results[level] = run_level(level)
            except (RuntimeError, AssertionError) as e:
                results[level] = {"level": level, "status": "STOP", "error": str(e)}
                print(f"[{THEME_ID}][{level}] STOP: {e}")
            cost_stage()
        save_json(f"{OUT_DIR}/e2e_run_summary.json", results)
        print(f"[{THEME_ID}] 完了。")
        return results

    result = {}
    for s in stages:
        if s == "gate4":
            result["gate4"] = gate4_check_stage()
        elif s in ("a2", "b1b"):
            result[s] = run_level(s)
        elif s == "cost":
            result["cost"] = cost_stage()
        else:
            print(f"unknown stage: {s}")
    save_json(f"{OUT_DIR}/e2e_run_summary_partial_{'_'.join(stages)}.json", result)
    return result


if __name__ == "__main__":
    main()

# ============================================================
# er014_output/user_test_news_convenience_ai_01/convenience_ai/fix_01_pipeline.py
# 管理ID: USER-TEST-NEWS-CONVENIENCE-AI-01-FIX-01
#
# 目的: Fable受入照合で発見した3点(時制/未発売事実の誤り、A2文長超過、
# B1 parts.json見出し混入)を、正式Local Rewrite経路(er010_ledger_
# local_rewrite_09)がMAJOR-deviation専用でありFact Checker指摘[時制]や
# 文分割には使えないため、委任文の指示どおり最小限の手動編集+
# 同経路のdiff QA相当(Ledger Deviation Checker全文再実行+Fact Checker
# 全文再実行)で対応する。新Factは追加しない(既存Verified Fact Ledgerの
# 範囲内でのtense fix・文分割のみ)。
#
# 実行方法(root直下から、stageを指定):
#   .venv/Scripts/python.exe er014_output/user_test_news_convenience_ai_01/convenience_ai/fix_01_pipeline.py edit
#   .venv/Scripts/python.exe er014_output/user_test_news_convenience_ai_01/convenience_ai/fix_01_pipeline.py recheck
#   .venv/Scripts/python.exe er014_output/user_test_news_convenience_ai_01/convenience_ai/fix_01_pipeline.py ledger_register
#   .venv/Scripts/python.exe er014_output/user_test_news_convenience_ai_01/convenience_ai/fix_01_pipeline.py retts_a2
#   .venv/Scripts/python.exe er014_output/user_test_news_convenience_ai_01/convenience_ai/fix_01_pipeline.py retts_b1
#   .venv/Scripts/python.exe er014_output/user_test_news_convenience_ai_01/convenience_ai/fix_01_pipeline.py assemble
#   .venv/Scripts/python.exe er014_output/user_test_news_convenience_ai_01/convenience_ai/fix_01_pipeline.py player
#   .venv/Scripts/python.exe er014_output/user_test_news_convenience_ai_01/convenience_ai/fix_01_pipeline.py density
# ============================================================
from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.getcwd())

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as prod_gen
import er003_v1_n3_01_assemble as asm
import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_n3_01_tts_generate as ttsgen
import er003_v1_crosslevel_audio_02_common as crosslevel_common
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er006_pronunciation_ledger_01 as pronun_ledger
import er006_pronunciation_research_01 as pron_research

THEME_ID = "user_test_news_convenience_ai_01_convenience_ai"
BASE_DIR = "er014_output/user_test_news_convenience_ai_01/convenience_ai"
A2_DIR = f"{BASE_DIR}/a2"
B1_DIR = f"{BASE_DIR}/b1b"
FIX_AUDIT_DIR = f"{BASE_DIR}/audit_fix_01"
TOPIC_JA = "コンビニのAI商品開発"


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def load_verified_ledger_text() -> str:
    with open(f"{BASE_DIR}/research/verified_fact_ledger.txt", encoding="utf-8") as f:
        return f.read()


# ============================================================
# Stage: edit (手動最小編集、backup保存、parts.json再構築)
# ============================================================
A2_EDITS = [
    (
        "Lawson scheduled the product for September 29, 2026. It was planned for about "
        "4,700 stores in Tokyo and nearby prefectures, with some areas of Niigata and "
        "Nagano excluded. Natural Lawson was also excluded. The price was 270 yen, "
        "including tax.",
        "Lawson is scheduled to sell the product from September 29, 2026. It will be "
        "sold at about 4,700 stores in Tokyo and nearby prefectures. Some areas of "
        "Niigata and Nagano are excluded. Natural Lawson stores are also excluded. The "
        "price will be 270 yen, including tax.",
    ),
    (
        "So this was a regional launch, not a nationwide or permanent product. But it "
        "shows one way some major Japanese convenience-store chains are using AI "
        "around food: a computer can suggest a starting idea, while people decide "
        "whether it belongs on the shelf.",
        "So this will be a regional launch, not a nationwide product. But it shows one "
        "way some major Japanese convenience-store chains are using AI around food. A "
        "computer can suggest a starting idea. Then people decide whether it belongs "
        "on the shelf.",
    ),
    (
        "The product launched across Japan in September 2026, but it was "
        "quantity-limited.",
        "The product is scheduled to go on sale across Japan in September 2026, but it "
        "will be quantity-limited.",
    ),
]

B1_EDITS = [
    (
        "It was a regional launch, not evidence of a permanent nationwide product.",
        "This will be a regional launch, not evidence of a nationwide product.",
    ),
    (
        "“Oimo no Canele — with Caramel Sauce” launched nationwide on "
        "September 22, 2026, as a limited-quantity product.",
        "“Oimo no Canele — with Caramel Sauce” is scheduled to go on sale "
        "nationwide on September 22, 2026, as a limited-quantity product.",
    ),
]


def _apply_edits(text: str, edits: list) -> tuple:
    applied = []
    for old, new in edits:
        cnt = text.count(old)
        if cnt != 1:
            raise RuntimeError(f"編集対象が一意に見つかりません(count={cnt}): {old[:80]!r}")
        text = text.replace(old, new, 1)
        applied.append({"before": old, "after": new})
    return text, applied


def edit_stage() -> dict:
    a2_path = f"{A2_DIR}/article.md"
    b1_path = f"{B1_DIR}/article.md"
    a2_text = open(a2_path, encoding="utf-8").read()
    b1_text = open(b1_path, encoding="utf-8").read()

    # backup(既存の.pre_*.bak命名慣行に合わせる)
    with open(f"{a2_path}.pre_fix_01.bak", "w", encoding="utf-8") as f:
        f.write(a2_text)
    with open(f"{b1_path}.pre_fix_01.bak", "w", encoding="utf-8") as f:
        f.write(b1_text)

    new_a2_text, a2_applied = _apply_edits(a2_text, A2_EDITS)
    new_b1_text, b1_applied = _apply_edits(b1_text, B1_EDITS)

    with open(a2_path, "w", encoding="utf-8") as f:
        f.write(new_a2_text)
    with open(b1_path, "w", encoding="utf-8") as f:
        f.write(new_b1_text)

    # parts.json再構築(共通経路sc.split_article_text()をそのまま使う。
    # B1のみ、split結果のpart1先頭に混入する"## Main Story"見出しを
    # canonicalから除去する[OPEN-165、artifact側対応のみ、Production関数
    # 自体は無変更]。他のkeyは無変更のはず、diffで確認する)。
    old_a2_parts = load_json(f"{A2_DIR}/parts.json")
    old_b1_parts = load_json(f"{B1_DIR}/parts.json")

    new_a2_parts = sc.split_article_text(new_a2_text)
    new_b1_parts_raw = sc.split_article_text(new_b1_text)
    new_b1_parts = dict(new_b1_parts_raw)
    heading_prefix = "## Main Story\n\n"
    if new_b1_parts["part1"].startswith(heading_prefix):
        new_b1_parts["part1"] = new_b1_parts["part1"][len(heading_prefix):]
        b1_heading_removed = True
    else:
        b1_heading_removed = False

    a2_parts_diff = {k: {"old": old_a2_parts.get(k), "new": new_a2_parts.get(k)}
                      for k in set(old_a2_parts) | set(new_a2_parts)
                      if old_a2_parts.get(k) != new_a2_parts.get(k)}
    b1_parts_diff = {k: {"old": old_b1_parts.get(k), "new": new_b1_parts.get(k)}
                      for k in set(old_b1_parts) | set(new_b1_parts)
                      if old_b1_parts.get(k) != new_b1_parts.get(k)}

    with open(f"{A2_DIR}/parts.json.pre_fix_01.bak", "w", encoding="utf-8") as f:
        json.dump(old_a2_parts, f, ensure_ascii=False, indent=2)
    with open(f"{B1_DIR}/parts.json.pre_fix_01.bak", "w", encoding="utf-8") as f:
        json.dump(old_b1_parts, f, ensure_ascii=False, indent=2)
    save_json(f"{A2_DIR}/parts.json", new_a2_parts)
    save_json(f"{B1_DIR}/parts.json", new_b1_parts)

    result = {
        "a2_edits_applied": a2_applied,
        "b1_edits_applied": b1_applied,
        "a2_parts_diff_keys": list(a2_parts_diff.keys()),
        "b1_parts_diff_keys": list(b1_parts_diff.keys()),
        "a2_parts_diff": a2_parts_diff,
        "b1_parts_diff": b1_parts_diff,
        "b1_main_story_heading_removed_from_canonical": b1_heading_removed,
    }
    save_json(f"{FIX_AUDIT_DIR}/edit_result.json", result)
    print(f"[FIX-01][edit] A2 edits={len(a2_applied)} B1 edits={len(b1_applied)}")
    print(f"[FIX-01][edit] A2 parts changed keys={list(a2_parts_diff.keys())}")
    print(f"[FIX-01][edit] B1 parts changed keys={list(b1_parts_diff.keys())} "
          f"(heading_removed={b1_heading_removed})")
    return result


# ============================================================
# Stage: recheck (Ledger Deviation Checker全文再実行 + Fact Checker全文
# 再実行、diff QA[OPEN-141]相当。新しいLLM判定基準・promptは作らず既存
# Production関数をそのまま呼ぶ)
# ============================================================
def recheck_level(level: str) -> dict:
    out_dir = A2_DIR if level == "a2" else B1_DIR
    label = "A2" if level == "a2" else "B1B"
    article_text = open(f"{out_dir}/article.md", encoding="utf-8").read()
    verified_ledger_text = load_verified_ledger_text()
    client = vfl01.get_client()

    ledger_model = routing.require_model(
        "A2_WRITER" if level == "a2" else "B1_WRITER", routing.WRITER_MODEL)
    print(f"[FIX-01][recheck/{level}] Ledger Deviation Checker(Hook-aware)実行...")
    deviation_result = vfl01.run_deviation_check(
        client, verified_ledger_text, article_text, model=ledger_model, hook_aware=True)
    deviation_status = deviation_result["parsed"]["overall_status"]
    major_count = len([d for d in deviation_result["parsed"]["deviations"] if d["severity"] == "MAJOR"])
    print(f"[FIX-01][recheck/{level}] deviation overall_status={deviation_status} MAJOR={major_count}")

    fc_prompt = r3.build_fact_check_prompt(TOPIC_JA, article_text, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(
            fc_prompt, model=routing.require_model("WRITER_FACT_CHECK", routing.WRITER_FACT_CHECK_MODEL))

    print(f"[FIX-01][recheck/{level}] Fact Checker(全文再実行)...")
    fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = \
        r3.run_fact_checker_with_gates(make_fc_fn, sleep_fn=time.sleep)
    fc_verdict = fc_result.get("verdict") if fc_result else None
    print(f"[FIX-01][recheck/{level}] fact_check status={fc_status} verdict={fc_verdict}")

    result = {
        "label": label,
        "ledger_deviation": {
            "overall_status": deviation_status,
            "major_count": major_count,
            "parsed": deviation_result["parsed"],
        },
        "fact_check": {
            "final_status": fc_status, "model": fc_model, "response_id": fc_response_id,
            "web_search_call_count": fc_search_usage["web_search_call_count"] if fc_search_usage else None,
            "attempts": len(fc_attempts), "result": fc_result,
        },
    }
    save_json(f"{FIX_AUDIT_DIR}/recheck_{level}.json", result)
    # 既存fact_qa.json/ledger_deviation.jsonも新結果へ更新(下流互換のため)
    save_json(f"{out_dir}/fact_qa.json", {
        "label": label, "final_status": fc_status, "model": fc_model, "response_id": fc_response_id,
        "web_search_call_count": fc_search_usage["web_search_call_count"] if fc_search_usage else None,
        "attempts": len(fc_attempts), "result": fc_result,
    })
    save_json(f"{out_dir}/ledger_deviation.json", deviation_result["parsed"])
    return result


def recheck_stage() -> dict:
    return {"a2": recheck_level("a2"), "b1b": recheck_level("b1b")}


# ============================================================
# Stage: ledger_register ("Oimo no Canele"をPronunciation Ledger正式経路
# [Perplexity research]で登録。cache hit時は再調査しない)
# ============================================================
def ledger_register_stage() -> dict:
    surface = "Oimo no Canele"
    entity_type = "product"
    key = pronun_ledger.LedgerKey(surface=surface, entity_type=entity_type)
    cached = pronun_ledger.lookup(key)
    if cached is not None:
        print(f"[FIX-01][ledger_register] cache hit: {cached}")
        save_json(f"{FIX_AUDIT_DIR}/ledger_register_result.json", {"cache_hit": True, "entry": cached})
        return {"cache_hit": True, "entry": cached}

    entities = [{
        "surface": surface, "entity_type": entity_type,
        "risk_reason": (
            "Japanese product name combining 'Oimo' (おいも, sweet potato, "
            "honorific o- + imo) with the French loanword pastry 'canelé'. Previous "
            "TTS/ASR cascade for this convenience-store news article showed ASR "
            "mishearing (Primary='Kanele', Secondary='OEMO No Canele')."
        ),
    }]
    print(f"[FIX-01][ledger_register] Perplexity研究呼び出し...")
    research_result = pron_research.research_pronunciations(entities)
    save_json(f"{FIX_AUDIT_DIR}/ledger_register_research_raw.json", research_result)
    if research_result.get("status") != "OK":
        raise RuntimeError(f"Pronunciation research失敗: {research_result}")

    ids = pronun_ledger.upsert_research_result(entities, research_result["items"], research_result.get("citations", []))
    registered = [pronun_ledger.lookup(pronun_ledger.LedgerKey(surface=surface, entity_type=entity_type))]
    result = {"cache_hit": False, "ledger_ids": ids, "registered_entries": registered,
               "research_items": research_result["items"]}
    save_json(f"{FIX_AUDIT_DIR}/ledger_register_result.json", result)
    print(f"[FIX-01][ledger_register] 登録完了: ids={ids} entries={registered}")
    return result


# ============================================================
# Stage: retts (影響segmentのみ再TTS。正式cascade[Secondary ASR+Phrase
# List]経由。無関係segmentは一切呼ばない)
# ============================================================
def _update_tts_audit(out_dir: str, seg_name: str, result: dict) -> None:
    tts_results = load_json(f"{out_dir}/audit/tts_generation_results.json")
    tts_results["segments"][seg_name] = result
    save_json(f"{out_dir}/audit/tts_generation_results.json", tts_results)
    run_summary_tts = load_json(f"{out_dir}/run_summary_tts.json")
    run_summary_tts["segment_status"][seg_name] = result.get("status")
    save_json(f"{out_dir}/run_summary_tts.json", run_summary_tts)


def retts_a2_stage() -> dict:
    out_dir = A2_DIR
    narration_dir = f"{out_dir}/narration"
    parts = load_json(f"{out_dir}/parts.json")
    results = {}
    for name, text in (
        ("full_story_part2", parts["part2"]),
        ("point_two", parts["point_two_body"]),
    ):
        sub = ttsgen.first_words(text)
        if name == "point_two":
            sc.assert_no_point_number_label(text, name)
        tts_input = ttsgen.tts_safe_news_en(text)
        print(f"[FIX-01][retts/a2] {name}生成: {tts_input!r}")
        with cl.segment_context(name):
            r = ttsgen.generate_a2_segment_with_slowdown(
                tts_input, f"{narration_dir}/{name}.wav", sub,
                style_prefix_override=ttsgen.A2_ENGLISH_STYLE_PREFIX_SLOWER,
                disfluency_qa=False,
                enable_connected_speech_equivalence_layer=True,
                enable_repetition_qa=True)
        r["canonical_text"] = text
        results[name] = r
        _update_tts_audit(out_dir, name, r)
        print(f"[FIX-01][retts/a2] {name} status={r.get('status')} "
              f"classification={r.get('audio_classification')} asr={r.get('asr_text')!r}")
    save_json(f"{FIX_AUDIT_DIR}/retts_a2_result.json", results)
    return results


def retts_b1_stage() -> dict:
    out_dir = B1_DIR
    narration_dir = f"{out_dir}/narration"
    parts = load_json(f"{out_dir}/parts.json")
    results = {}
    for name, text in (
        ("full_story_part1", parts["part1"]),
        ("point_one", parts["point_one_body"]),
        ("point_two", parts["point_two_body"]),
    ):
        if name in ("point_one", "point_two"):
            sc.assert_no_point_number_label(text, name)
        tts_input = ttsgen.tts_safe_news_en(text)
        print(f"[FIX-01][retts/b1] {name}生成: {tts_input!r}")
        with cl.segment_context(name):
            r = news_tail_fix.generate_news_narration_wide_margin(
                tts_input, f"{narration_dir}/{name}.wav",
                disfluency_qa=False,
                enable_connected_speech_equivalence_layer=True,
                enable_repetition_qa=True)
        r["canonical_text"] = text
        results[name] = r
        _update_tts_audit(out_dir, name, r)
        print(f"[FIX-01][retts/b1] {name} status={r.get('status')} "
              f"classification={r.get('audio_classification')} asr={r.get('asr_text')!r}")
    save_json(f"{FIX_AUDIT_DIR}/retts_b1_result.json", results)
    return results


# ============================================================
# Stage: assemble (Assembly + Audio Validation Gate、override無し)
# ============================================================
def assemble_level(level: str) -> dict:
    theme = {"theme_id": THEME_ID, "out_dir": BASE_DIR}
    out_dir = A2_DIR if level == "a2" else B1_DIR
    assemble_fn = asm.stage_assemble_a2 if level == "a2" else asm.stage_assemble_b1
    try:
        result = assemble_fn(theme)
        result["gate_off_result"] = "PASS"
    except RuntimeError as e:
        result = {"status": "GATE_BLOCKED", "gate_off_result": "BLOCKED", "error": str(e)}
    print(f"[FIX-01][assemble/{level}] Assembly(Gate OFF経路)結果: {result.get('gate_off_result')}")

    gate_on = {"gate_on_result": "SKIPPED_ASSEMBLE_NOT_PASS"}
    if result.get("gate_off_result") == "PASS":
        gate_level = "A2" if level == "a2" else "B1"
        rs = asm.derive_a_family_required_structure(gate_level)
        try:
            asm.verify_episode_audio_validation_gate(out_dir, gate_level, required_structure=rs)
            gate_on = {"gate_on_result": "PASS"}
        except RuntimeError as e:
            gate_on = {"gate_on_result": "BLOCKED", "gate_on_message": str(e)[:1500]}
    print(f"[FIX-01][assemble/{level}] Gate opt-in ON経路結果: {gate_on.get('gate_on_result')}")
    result["gate_opt_in_result"] = gate_on
    save_json(f"{out_dir}/audit/assembly_and_gate_summary.json", result)
    return result


def assemble_stage() -> dict:
    return {"a2": assemble_level("a2"), "b1b": assemble_level("b1b")}


# ============================================================
# Stage: player (build_web_player_common、無変更で呼ぶ)
# ============================================================
def player_level(level: str, title: str) -> str:
    sys.path.insert(0, "er014_output/user_test_news_2ep_01")
    import build_web_player_common as bwpc  # noqa: E402

    out_dir = A2_DIR if level == "a2" else B1_DIR
    narration_dir = f"{out_dir}/narration"
    assemble_result = load_json(f"{out_dir}/audit/assembly_and_gate_summary.json")
    seg_names = sorted(f[:-4] for f in os.listdir(narration_dir) if f.endswith(".wav"))
    web_delivery = bwpc.build_web_delivery(out_dir, out_dir, narration_dir, assemble_result["out_path"], seg_names)
    build_rows_fn = bwpc.build_a2_rows if level == "a2" else bwpc.build_b1b_rows
    rows, kp_table_html, parts = build_rows_fn(out_dir, "web/segments")
    label = "A2 (Beginner)" if level == "a2" else "B1 (Advanced)"
    note_html = (f"USER-TEST(AI Product Development at Japanese Convenience Stores)。"
                 f"{THEME_ID}。FIX-01(日付・事実修正+B1見出し"
                 f"除去)適用済み。")
    out_path = bwpc.render_player_page(
        f"{title} - {label}", note_html, web_delivery["episode_mp3"],
        assemble_result["duration_seconds"], assemble_result["peak"], assemble_result["clipping_detected"],
        rows, kp_table_html, f"{out_dir}/player.html")
    print(f"[FIX-01][player/{level}] player.html生成: {out_path}")
    return out_path


def player_stage() -> dict:
    parts_a2 = load_json(f"{A2_DIR}/parts.json")
    parts_b1 = load_json(f"{B1_DIR}/parts.json")
    return {
        "a2": player_level("a2", parts_a2["title"]),
        "b1b": player_level("b1b", parts_b1["title"]),
    }


# ============================================================
# Stage: density (情報密度再計測、既存density_check.pyのロジックをそのまま
# 再実行するだけ、read-only)
# ============================================================
def density_stage() -> dict:
    sys.path.insert(0, BASE_DIR)
    import density_check as dc
    out = {}
    for level, sub in (("a2", "a2"), ("b1", "b1b")):
        r = dc.check(f"{BASE_DIR}/{sub}/article.md", level)
        out[level] = r
        print(f"[FIX-01][density][{level}] word_count={r['word_count']} avg={r['avg_sentence_length']}"
              f"(limit{r['avg_limit_diagnostic']}) max={r['max_sentence_length']}"
              f"(limit{r['max_limit_diagnostic']}) numbers={r['number_occurrences']} "
              f"avoided_words={r['avoided_word_hits']} points={r['point_heading_count']}")
    save_json(f"{BASE_DIR}/audit/density_check_result_fix_01.json", out)
    return out


def cost_stage() -> dict:
    log_path = f"{BASE_DIR}/raw_usage_log.jsonl"
    sys.path.insert(0, BASE_DIR)
    import run_pipeline as rp
    result = rp.compute_cost_jpy_so_far()
    print(f"[FIX-01][cost] 実測合計(累計)={result['total_jpy']} JPY by_provider={result['by_provider_jpy']}")
    save_json(f"{FIX_AUDIT_DIR}/cost_so_far.json", result)
    return result


STAGE_FUNCS = {
    "edit": edit_stage,
    "recheck": recheck_stage,
    "ledger_register": ledger_register_stage,
    "retts_a2": retts_a2_stage,
    "retts_b1": retts_b1_stage,
    "assemble": assemble_stage,
    "player": player_stage,
    "density": density_stage,
    "cost": cost_stage,
}


def main():
    cl.install(f"{BASE_DIR}/raw_usage_log.jsonl")
    stages = sys.argv[1:] or list(STAGE_FUNCS.keys())
    results = {}
    for s in stages:
        if s not in STAGE_FUNCS:
            raise SystemExit(f"unknown stage: {s} (choices={list(STAGE_FUNCS.keys())})")
        results[s] = STAGE_FUNCS[s]()
    return results


if __name__ == "__main__":
    main()

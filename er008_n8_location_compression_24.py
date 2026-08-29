# ============================================================
# er008_n8_location_compression_24.py
# ER-008-N8-FINAL-CLOSEOUT-24 Item 1:
# No.8(pool_n8_airport_line)へ、ER-23で正式承認された地名・施設名
# Evidence Compressionルールを実際に反映する。
#
# 適用する編集(A2/B1共通、1箇所のみの機械的な文字列置換):
#   "Dallas Fort Worth International Airport" -> "Dallas Fort Worth"
#
# 対象箇所:
#   A2: part2(1箇所)
#   B1: part2(1箇所)、in_one_line(1箇所)
# Point One/Two・Title・その他segmentは無変更(本文がずれていないため
# 再TTS/ASRの必要が無い)。
#
# ユーザー正式判断(2026-08-29、ER-24): ER-23で発見した「編集後の
# Fact Check再実行がREVIEW_REQUIREDを返す」問題は、地名圧縮そのものが
# 引き起こしたものではなく(flagged項目は全て編集箇所と無関係な既存の
# 記述だった)、ライブ検索を伴うFact Checkの非決定性(OPEN-92)による
# ものと整理する。したがって、無関係なFact Check結果だけでこの地名
# 圧縮をblockしない。ただし、編集箇所自体に新たな実質的Fact問題が
# 無いことは今回も確認する。
from __future__ import annotations

import json
import os
import shutil

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as gen
import er003_v1_n3_01_assemble as asm
import er003_v1_n3_01_tts_generate as tg
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing

BASE = "er006_output/pool_pilot_01/pool_n8_airport_line"
THEME_ID = "pool_n8_airport_line"

OLD_STR = "Dallas Fort Worth International Airport"
NEW_STR = "Dallas Fort Worth"

TOPIC_JA_TEXT = (
    "空港の搭乗ゲートでは、自分の搭乗グループがまだ呼ばれていないのに、多くの乗客が"
    "早くからゲート前に並んでしまう。この行動は客室乗務員の間で「gate lice」と呼ばれ、"
    "広く知られている。心理学者は、この行動を単なる非合理な行動としてではなく、"
    "リスクの非対称性(乗り遅れる小さな可能性の代償が、無駄に立って待つことの代償より"
    "はるかに大きい)への合理的な反応として説明する。また、頭上の荷物棚の空き容量を"
    "めぐる競争、周囲の人が並び始めると自分も並んでしまう同調行動、順番を守らないと"
    "恥をかくという社会的なプレッシャーも背景にある。一方で航空会社側もこの問題への"
    "対応を強めており、American Airlinesは2026年夏からダラス・フォートワース空港で、"
    "搭乗券を自動確認し乗客の流れを規制する電子搭乗ゲートの本格導入を始める。"
)


def backup(path: str, tag: str) -> None:
    if os.path.exists(path):
        shutil.copy(path, f"{path}.{tag}.bak")


def replace_and_count(text: str) -> tuple[str, int]:
    count = text.count(OLD_STR)
    return text.replace(OLD_STR, NEW_STR), count


def apply_text_edit(level_dir: str, fields: list[str], expected_total_occurrences: int) -> dict:
    parts_path = f"{level_dir}/parts.json"
    article_path = f"{level_dir}/article.md"
    backup(parts_path, "pre_location_compression_24")
    backup(article_path, "pre_location_compression_24")

    with open(parts_path, encoding="utf-8") as f:
        parts = json.load(f)
    total = 0
    changed_fields = {}
    for field in fields:
        new_text, n = replace_and_count(parts[field])
        if n:
            changed_fields[field] = {"old": parts[field], "new": new_text}
            parts[field] = new_text
            total += n
    with open(parts_path, "w", encoding="utf-8") as f:
        json.dump(parts, f, ensure_ascii=False, indent=2)

    with open(article_path, encoding="utf-8") as f:
        article_text = f.read()
    new_article_text, article_count = replace_and_count(article_text)
    with open(article_path, "w", encoding="utf-8") as f:
        f.write(new_article_text)

    assert total == expected_total_occurrences, (
        f"{parts_path}: 想定した置換件数と一致しません(想定{expected_total_occurrences}, 実際{total})")
    assert article_count == expected_total_occurrences, (
        f"{article_path}: 想定した置換件数と一致しません(想定{expected_total_occurrences}, 実際{article_count})")

    return {"changed_fields": changed_fields, "new_article_text": new_article_text,
            "parts_replacements": total, "article_replacements": article_count}


def update_segment_result(out_dir: str, name: str, new_result: dict) -> None:
    audit_path = f"{out_dir}/audit/tts_generation_results.json"
    with open(audit_path, encoding="utf-8") as f:
        data = json.load(f)
    data["segments"][name] = new_result
    with open(audit_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def regen_a2_full_story_part2(new_part2_text: str) -> dict:
    out_dir = f"{BASE}/a2"
    narration_dir = f"{out_dir}/narration"
    tts_input = tg.tts_safe_news_en(new_part2_text)
    print("[N8-LOC-24][A2] full_story_part2 再生成開始...")
    result = tg.generate_a2_segment_with_slowdown(
        tts_input, f"{narration_dir}/full_story_part2.wav", tg.first_words(new_part2_text),
        style_prefix_override=tg.A2_ENGLISH_STYLE_PREFIX_SLOWER, disfluency_qa=False)
    result["canonical_text"] = new_part2_text
    print(f"[N8-LOC-24][A2] full_story_part2 status={result.get('status')} "
          f"asr_verified={result.get('asr_verified')} asr_text={result.get('asr_text')!r}")
    update_segment_result(out_dir, "full_story_part2", result)
    return result


def regen_b1_segment(name: str, new_text: str) -> dict:
    out_dir = f"{BASE}/b1b"
    narration_dir = f"{out_dir}/narration"
    tts_input = tg.tts_safe_news_en(new_text)
    print(f"[N8-LOC-24][B1] {name} 再生成開始...")
    result = tg.news_tail_fix.generate_news_narration_wide_margin(
        tts_input, f"{narration_dir}/{name}.wav", disfluency_qa=(name == "in_one_line"))
    result["canonical_text"] = new_text
    print(f"[N8-LOC-24][B1] {name} status={result.get('status')} "
          f"asr_verified={result.get('asr_verified')} asr_text={result.get('asr_text')!r}")
    update_segment_result(out_dir, name, result)
    return result


def run_fact_and_deviation_check(label: str, article_text: str) -> dict:
    ledger_text = open(f"{BASE}/research/verified_fact_ledger.txt", encoding="utf-8").read()

    fc_prompt = r3.build_fact_check_prompt(TOPIC_JA_TEXT, article_text, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(
            fc_prompt, model=routing.require_model("WRITER_FACT_CHECK", routing.WRITER_FACT_CHECK_MODEL))

    fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = \
        r3.run_fact_checker_with_gates(make_fc_fn)
    verdict = fc_result.get("verdict") if fc_result else None
    print(f"[N8-LOC-24][{label}] fact_check(post-edit) status={fc_status} verdict={verdict}")

    writer_process = "B1_WRITER" if label == "B1B" else "A2_WRITER"
    deviation_result = vfl01.run_deviation_check(
        vfl01.get_client(), ledger_text, article_text,
        model=routing.require_model(writer_process, routing.WRITER_MODEL))
    dev_parsed = deviation_result["parsed"]
    print(f"[N8-LOC-24][{label}] deviation(post-edit) overall_status={dev_parsed['overall_status']} "
          f"deviations={len(dev_parsed['deviations'])}")

    return {
        "fact_status": fc_status, "fact_verdict": verdict, "fact_result": fc_result,
        "fact_model": fc_model, "fact_response_id": fc_response_id,
        "deviation_overall_status": dev_parsed["overall_status"], "deviations": dev_parsed["deviations"],
    }


def _mentions_edit(check_result: dict) -> list[str]:
    """flagged/deviation項目のうち、テキスト中に'Dallas Fort Worth'または
    'airport'を含むもの(=編集箇所に言及している可能性がある項目)を返す。
    人間が最終確認するための一次スクリーニングであり、これが空でも
    完全な安全性を機械的に保証するものではない。"""
    hits = []
    fr = check_result.get("fact_result") or {}
    for key in ("unsupported_specific_claims", "contradictions"):
        for item in (fr.get(key) or []):
            blob = json.dumps(item, ensure_ascii=False).lower()
            if "dallas" in blob or "fort worth" in blob or "airport" in blob:
                hits.append({"source": f"fact_check.{key}", "item": item})
    for item in check_result.get("deviations") or []:
        blob = json.dumps(item, ensure_ascii=False).lower()
        if "dallas" in blob or "fort worth" in blob or "airport" in blob:
            hits.append({"source": "ledger_deviation", "item": item})
    return hits


def main():
    cl.install(f"{BASE}/raw_usage_log.jsonl")
    theme = {"theme_id": THEME_ID, "out_dir": BASE}
    summary = {}

    # --- 1. テキスト編集 ---
    a2_edit = apply_text_edit(f"{BASE}/a2", ["part2"], expected_total_occurrences=1)
    b1_edit = apply_text_edit(f"{BASE}/b1b", ["part2", "in_one_line"], expected_total_occurrences=2)
    summary["text_edit"] = {"a2": a2_edit["changed_fields"], "b1": b1_edit["changed_fields"]}

    with open(f"{BASE}/a2/parts.json", encoding="utf-8") as f:
        a2_parts = json.load(f)
    with open(f"{BASE}/b1b/parts.json", encoding="utf-8") as f:
        b1_parts = json.load(f)

    # --- 2. 該当segmentのみ再TTS/ASR ---
    a2_tts = {"full_story_part2": regen_a2_full_story_part2(a2_parts["part2"])}
    b1_tts = {
        "full_story_part2": regen_b1_segment("full_story_part2", b1_parts["part2"]),
        "in_one_line": regen_b1_segment("in_one_line", b1_parts["in_one_line"]),
    }
    summary["tts"] = {
        "a2": {k: {"status": v.get("status"), "asr_verified": v.get("asr_verified"),
                    "asr_text": v.get("asr_text"), "sha256": v.get("sha256")} for k, v in a2_tts.items()},
        "b1": {k: {"status": v.get("status"), "asr_verified": v.get("asr_verified"),
                    "asr_text": v.get("asr_text"), "sha256": v.get("sha256")} for k, v in b1_tts.items()},
    }

    # --- 3. Fact Check / Ledger Deviation(編集後の記事全文を対象に1回) ---
    with open(f"{BASE}/a2/article.md", encoding="utf-8") as f:
        a2_article_text = f.read()
    with open(f"{BASE}/b1b/article.md", encoding="utf-8") as f:
        b1_article_text = f.read()

    a2_check = run_fact_and_deviation_check("A2", a2_article_text)
    b1_check = run_fact_and_deviation_check("B1B", b1_article_text)
    a2_check["edit_related_hits"] = _mentions_edit(a2_check)
    b1_check["edit_related_hits"] = _mentions_edit(b1_check)
    summary["fact_and_deviation_recheck"] = {"a2": a2_check, "b1": b1_check}

    with open(f"{BASE}/a2/audit/location_compression_24_fact_recheck.json", "w", encoding="utf-8") as f:
        json.dump(a2_check, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{BASE}/b1b/audit/location_compression_24_fact_recheck.json", "w", encoding="utf-8") as f:
        json.dump(b1_check, f, ensure_ascii=False, indent=2, default=str)

    # --- 4. 判定(編集箇所への言及が無ければ、ユーザー方針に従いblockしない) ---
    blocked = bool(a2_check["edit_related_hits"] or b1_check["edit_related_hits"])
    summary["adoption_decision"] = "BLOCKED_EDIT_RELATED_ISSUE_FOUND" if blocked else "ADOPTED"

    with open("er008_output/n8_location_compression_24_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)

    if blocked:
        print("[N8-LOC-24] 編集箇所に言及するFact/Deviation指摘が見つかりました。Assembleを中止します。")
        print(json.dumps(summary["fact_and_deviation_recheck"], ensure_ascii=False, indent=2, default=str))
        return summary

    # --- 5. 再Assemble(Audio Validation Gateが内部で自動検証) ---
    print("[N8-LOC-24] B1再Assemble開始...")
    b1_assemble = asm.stage_assemble_b1(theme)
    print("[N8-LOC-24] A2再Assemble開始...")
    a2_assemble = asm.stage_assemble_a2(theme)
    summary["assemble"] = {"b1": b1_assemble, "a2": a2_assemble}

    with open("er008_output/n8_location_compression_24_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)

    print("[N8-LOC-24] 完了。")
    print(json.dumps({k: v for k, v in summary.items() if k != "text_edit"}, ensure_ascii=False, indent=2, default=str))
    return summary


if __name__ == "__main__":
    main()

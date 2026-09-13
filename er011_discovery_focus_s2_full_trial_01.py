# ============================================================
# er011_discovery_focus_s2_full_trial_01.py
# 管理ID: FAMILY-A-DISCOVERY-FOCUS-S2-FULL-QA-PARITY-TRIAL-01
# ============================================================
# 目的(ユーザー確定判断、2026-09-13): S2(Focusを先に決める→Main Storyを
# 確定する→そのMain Story本文を見てPoint Role Planning→Point生成)を軸に、
# 前回未実装だった既存Production QAとの同等性確認まで進める完全版Trial。
# **Trial(Article-only)。Production配線・CURRENT_SPEC正式化・
# APPROVED_FOR_PRODUCTIONへの変更は一切行わない**。到達上限は
# VALIDATED(判定語の最終確定はFableに委ねる)。Production関数は無編集
# (r3/vfl01/prod_gen/point_planning/local_rewrite/dfp/ec_editor/
# overlap_qaはすべてimportのみ、本ファイル内で再定義・monkeypatchしない)。
#
# 【前回(PART-A-STANDALONE-TRIAL-01)からの差分】
# 前回はStage 1(Main Story)を既存Trialのarticle.mdから再利用し、Stage 1
# QA(Fact Checker/Ledger Deviation/Directional Precheck)・Local Rewrite・
# Point Overlap/Value QA retry・Evidence Compressionのいずれも実行して
# いなかった(未実装として明記)。本Trialは以下を新規に実装する:
#   (1) Stage 1: 新規にMain Storyを生成する(Focus Module Part A適用、
#       Title+Main Storyのみを書かせる新規Trial専用prompt。Point One/Two
#       は一切書かせない)。
#   (2) Stage 1 QA: Main Story単体に対しFact Checker A' → Ledger
#       Deviation Check(MAJORならLocal Rewrite、既存関数を無変更で再利用)
#       → Directional Fact Precheck(non-blocking)を実行する。
#   (3) Stage 2: 前回同様、確定したMain Story本文を実際に読ませてPoint
#       Role Planningを行う(前回Trialのrun_stage2_role_planningをそのまま
#       import・再利用、コピーしない)。
#   (4) Stage 3: Point One/Two生成(前回のSTAGE3プロンプトをそのまま
#       import・再利用)→ Evidence Compression(既存Lossless Editorを
#       Points本文のみに適用、新規適用範囲)→ Main Story(Stage 1で確定・
#       以後不変)と結合。
#   (5) 結合後の記事全体に対し、Point Overlap QA・Point Value QA
#       (既存Production関数を無変更で再利用)を実行し、NGの場合は
#       Stage 2-3のみ再実行する(Main Storyは固定したまま)。これが
#       ユーザー確定判断の「第一候補」retry単位。
#   (6) 結合後の記事全体に対し、Fact Checker A'・Ledger Deviation Check
#       (+Local Rewrite、既存関数を無変更で再利用)を再度実行する
#       (Stage 1のMain Story単体チェックとは別に、Points追加後の記事
#       全体としての整合性を確認するため)。Ledger MAJORのclaim_in_article
#       がMain Story側かPoints側かを、既存のlocal_rewrite.locate_target_
#       sentence(無変更)で判定し、Main Story側に位置する場合のみStage 1
#       からの再生成へ分岐する(それ以外はStage 2-3再実行、または
#       Local Rewriteで解決を試みる)。
#   (7) Directional Fact Precheck(non-blocking)を記事全体に対して実行。
#
# 【retry単位(ユーザー確定判断の第一候補を実装)】
#   通常: Stage 1(Main Story)は固定し、Stage 2-3(Point Role Planning→
#   Point生成)のみ再実行する(POINT_OVERLAP_ARTICLE_RETRY_MAX=2回まで、
#   既存Production値と同一)。
#   例外: Main Story自体に重大な問題がある場合のみStage 1から再生成する。
#   「重大な問題」は本Trialでは次の2条件のいずれかと定義する(Trial限定の
#   新規しきい値、Production値の流用ではない。Gate 1判定材料として明記):
#     (a) 記事全体Ledger Deviation Checkで検出されたMAJORのclaim_in_
#         articleが、Main Story本文(Stage 1で確定した範囲)内に位置する
#         場合(Local Rewrite cycle上限[MAX_REWRITE_CYCLES=3、既存値]を
#         尽くしても解決しない場合)。
#     (b) Stage 2-3再実行がPOINT_OVERLAP_ARTICLE_RETRY_MAX(=2)回を尽くし
#         てもPoint Overlap/Value QAまたはFact CheckerがNG/FAILのままの
#         場合(Main Story側原因の切り分けができないための最終フォール
#         バックとして、Stage 1再生成を1回だけ許可する)。
#   Stage 1再生成の上限はSTAGE1_MAX_REGENERATIONS=1回(新規Trialしきい値、
#   合計2回まで生成)。これも尽きた場合はNG_REVIEW_REQUIREDとして停止する
#   (fail-closed、無限ループ・黙示的PASSを行わない)。
#
# 【新規に書いたもの(Trial限定、Productionコピーではない)】
#   - STAGE1_MAIN_STORY_ONLY_OVERRIDE_BLOCK / run_stage1_main_story_writer:
#     Main Story+draft In One Lineのみを書かせる新規prompt override。
#     基礎となるcommon_block/instruction文字列はprod_gen.build_common_block/
#     build_prompt/A2_KAI1_INSTRUCTION/B1_B_DIRECT_INSTRUCTIONを無変更で
#     呼び出した結果にこのoverrideを追記するだけ(Production定数は無編集)。
#   - extract_stage1_main_story: Stage 1出力から Title/Main Story/draft
#     In One Lineを分離する新規parser(prod_gen.split_common_sections_for_
#     point_qaは「###見出しちょうど2つ」を要求するためStage 1単体では
#     使えない。Stage 1はPoint見出しを含まないため新規に書いた)。
#   - run_ledger_local_rewrite_loop: run_one_pattern L1040-1198の
#     Ledger Deviation Check+Local Rewriteループを、(i)Stage 1(Main Story
#     単体)と(ii)Stage 2-3後の記事全体の両方から共通で呼べるよう関数化した
#     もの。ループ内で呼ぶ個々の関数(vfl01.run_deviation_check/
#     local_rewrite.split_sentences/locate_target_sentence/
#     extract_point_context/rewrite_ng_item/apply_diff_qa_to_resolved_
#     rewrite/apply_rewrites、prod_gen.normalize_article_formatting)は
#     全てimportした関数オブジェクトをそのまま呼ぶ(コピー・再実装しない、
#     テストでidentity確認)。ループの外形(cycle上限・human_review判定)は
#     run_one_patternと同じ設計だが、新たにmain_story向けlocus分類
#     (Stage 1 escalation判定)を追加している点が新規部分。
#   - run_stage2_3_with_retry: Stage 2(Role Planning)→Stage 3(Point
#     生成)→Evidence Compression→結合→Point Overlap/Value QAを1単位とし、
#     NG時はStage 2から再実行するretryループ(新規。Production
#     run_one_patternはこの単位を「記事全体[Main Story含む]を1単位」として
#     re-generateするため、ここが本Trialの中心的な検証対象)。
#
# 実行方法(root直下から):
#   .venv/Scripts/python.exe er011_discovery_focus_s2_full_trial_01.py [stage ...]
#   stage: a2 | b1b | cost | all(省略時)
# ============================================================
from __future__ import annotations

import json
import os
import re
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as prod_gen
import er003_v1_n3_01_evidence_compression_editor as ec_editor
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er008_directional_fact_precheck_08 as dfp
import er008_shared_point_blueprint_01 as blueprint_mod
import er010_ledger_local_rewrite_09 as local_rewrite
import er011_discovery_focus_part_a_standalone_trial_01_run as s2_prev
import er011_discovery_stage3_rule_adjustment_trial_09 as t9
import er011_open146_ledger_canonical_en_spelling_production_01 as canon_spelling
import er011_point_role_value_planning_01 as point_planning

THEME_ID = "discovery_focus_s2_full_trial_01"
OUT_DIR = f"er011_output/{THEME_ID}"
BUDGET_JPY_CAP = 90.0  # ユーザー指定上限目安(Discovery残額¥219.59以内)。

# Ledger/topicはwake-before-alarm Trial-12のresearch成果物をread-only再利用
# (新規research実施なし)。Stage 1は今回新規に生成する(前回trialの限界だった
# 「S1固定によりStage1 QA/再生成分岐が未検証」を解消するため)。
SOURCE_TRIAL_DIR = "er011_output/discovery_generalization_wake_before_alarm_trial_12"
SOURCE_LEDGER_PATH = f"{SOURCE_TRIAL_DIR}/research/verified_fact_ledger.txt"
SOURCE_TOPIC_PATH = f"{SOURCE_TRIAL_DIR}/research/writer_topic.json"
SOURCE_VFL_PATH = f"{SOURCE_TRIAL_DIR}/research/stage_b3_vfl.json"

# Focus Module Part A本体(t9.CURRENT_FOCUS_BLOCKを無変更で再利用、Part B
# [cautionary_clause]は追加しない=Part A単独条件、前回revalidation Trialと
# 同じ条件)。
DISCOVERY_FOCUS_MODULE_PART_A_BLOCK = t9.CURRENT_FOCUS_BLOCK

LEVELS = {
    "a2": {"label": "A2", "instruction": prod_gen.A2_KAI1_INSTRUCTION, "stage_tag": "writer_a2"},
    "b1b": {"label": "B1B", "instruction": prod_gen.B1_B_DIRECT_INSTRUCTION, "stage_tag": "writer_b1"},
}

STAGE1_MAX_REGENERATIONS = 1  # 新規Trialしきい値(上記ヘッダー参照、合計2回まで生成)


def save_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_reused_ledger_and_topic() -> tuple:
    verified_ledger_text = open(SOURCE_LEDGER_PATH, encoding="utf-8").read()
    topic_ja = load_json(SOURCE_TOPIC_PATH)["topic_ja"]
    return verified_ledger_text, topic_ja


# ============================================================
# Stage 1: Main Story(+In One Line案)のみを書かせる(新規Trial prompt)。
# 基礎となるcommon_block/instructionはProduction定数を無変更で使う。
# ============================================================
STAGE1_MAIN_STORY_ONLY_OVERRIDE_BLOCK = """
【今回の出力に関する重要な追加指示(このセクションが上記の記事構成指示より優先されます)】
今回はMain Storyだけを書いてください。上記「記事構成」のうち、1(Title)と2
(Main Story)だけを出力し、3(Markdownの「###」見出しをちょうど2つ置く
Point One相当・Point Two相当の部分)は今回は一切書かないでください。Point One・
Point Twoは、この後の別の工程で、今回確定するMain Story本文を実際に読んだ上で
別途計画・執筆されます(あなたはこの工程を担当しません)。

Main Storyの本文の後に、"## In one line (draft)"という見出しを置き、その後に
この記事を将来的にどう静かに一言で結べそうか、現時点での案を1〜2文の英語で
書いてください。これはあくまで草案であり、Point One・Point Twoの内容が決まった
後の別工程で書き直される可能性があります(この草案は最終記事にそのまま使われる
とは限りません)。
"""

STAGE1_REGENERATION_FEEDBACK_TEMPLATE = """
【前回生成のMain Storyに問題があったため、再生成をお願いします】
前回生成したMain Storyには、以下の理由で承認できない問題がありました:
{reason}

Verified Fact Ledgerに厳密に従い、上記の問題を避けて、Main Storyを新しい
組み立て・表現で書き直してください(前回と同じ問題を繰り返さないでください)。
"""


def extract_stage1_main_story(raw_text: str):
    """Stage 1出力(Title+Main Story+draft In One Line、###見出しなし)を
    分解する。想定外構造(###見出しが混入、In one line見出しが無い、Main
    Story本文が極端に短い)の場合はNoneを返す(呼び出し側はSTRUCTURE_
    INVALIDとして扱う)。"""
    title_match = re.match(r"^#\s+.+?\s*\n", raw_text)
    if not title_match:
        return None
    if re.search(r"^###\s+", raw_text, flags=re.MULTILINE):
        return None
    draft_match = re.search(r"^##\s+In one line", raw_text, flags=re.MULTILINE)
    if not draft_match:
        return None
    title_line = raw_text[:title_match.end()].strip()
    main_story_text = raw_text[title_match.end():draft_match.start()].strip()
    draft_in_one_line = raw_text[draft_match.end():].strip()
    if len(main_story_text.split()) < 50:
        return None
    return {"title_line": title_line, "main_story_text": main_story_text,
            "draft_in_one_line": draft_in_one_line}


def run_stage1_main_story_writer(client, level: str, topic_ja: str, verified_ledger_text: str,
                                  writer_model: str, out_dir: str, feedback_block: str = "",
                                  max_attempts: int = 2) -> dict:
    meta = LEVELS[level]
    master_full_text = ab01.load_master_full_text()
    common_block = prod_gen.build_common_block(
        master_full_text, topic_ja, verified_ledger_text,
        editorial_type_module_block=DISCOVERY_FOCUS_MODULE_PART_A_BLOCK)
    base_prompt = prod_gen.build_prompt(common_block, meta["instruction"])
    prompt = base_prompt + "\n" + STAGE1_MAIN_STORY_ONLY_OVERRIDE_BLOCK
    if feedback_block:
        prompt = prompt + "\n" + feedback_block

    attempts = []
    for attempt in range(1, max_attempts + 1):
        writer_result = vfl01.run_writer_no_search(client, prompt, model=writer_model)
        parsed = extract_stage1_main_story(writer_result["raw_text"])
        attempts.append({
            "attempt": attempt, "model": writer_result["model"],
            "response_id": writer_result["response_id"],
            "structure_valid": parsed is not None, "raw_text": writer_result["raw_text"],
        })
        if parsed is not None:
            save_json(f"{out_dir}/audit/stage1_writer_attempts.json", attempts)
            return {"status": "STRUCTURE_PASS", "attempts": attempts, "prompt": prompt, **parsed}
        if attempt < max_attempts:
            continue
    save_json(f"{out_dir}/audit/stage1_writer_attempts.json", attempts)
    return {"status": "STRUCTURE_INVALID", "attempts": attempts, "prompt": prompt}


# ============================================================
# Ledger Deviation Check + Local Rewrite(run_one_pattern L1040-1198相当を
# 共通関数化。呼ばれる個々の関数は全てimportした関数オブジェクトをそのまま
# 使う)。main_story_text_for_locusを渡した場合のみ、残存MAJORの
# claim_in_articleがMain Story側かPoints側かを判定する(Stage 1
# escalation判定用、Stage 1単体呼び出し時はNoneのまま=判定不要)。
# ============================================================
def run_ledger_local_rewrite_loop(client, topic_ja: str, verified_ledger_text: str, article_text: str,
                                   ledger_model: str, out_dir: str, tag: str,
                                   main_story_text_for_locus: str | None = None) -> dict:
    def _run_check_window(window_text: str) -> dict:
        r = vfl01.run_deviation_check(client, verified_ledger_text, window_text,
                                       model=ledger_model, hook_aware=True)
        return r["parsed"]

    deviation_result = vfl01.run_deviation_check(client, verified_ledger_text, article_text,
                                                  model=ledger_model, hook_aware=True)
    major_items = [d for d in deviation_result["parsed"]["deviations"] if d["severity"] == "MAJOR"]

    local_rewrite_results = []
    local_rewrite_cycles = []
    cycle = 0
    previously_seen_claims = set()

    while major_items and cycle < local_rewrite.MAX_REWRITE_CYCLES:
        cycle += 1
        newly_discovered_claims = [d["claim_in_article"] for d in major_items
                                    if d["claim_in_article"] not in previously_seen_claims]
        sentences = local_rewrite.split_sentences(article_text)
        cycle_results = []
        for idx, deviation in enumerate(major_items, start=1):
            target, location_method = local_rewrite.locate_target_sentence(
                deviation["claim_in_article"], article_text)
            if target is None:
                cycle_results.append({
                    "cycle": cycle, "item_idx": idx, "original_ng_sentence": deviation["claim_in_article"],
                    "issue": deviation["issue"], "explanation": deviation["explanation"],
                    "attempts": [], "final_text": None, "resolved": False,
                    "human_review_required": True, "location_method": "not_found",
                })
                continue
            try:
                sidx = sentences.index(target)
            except ValueError:
                sidx = -1
            before_ctx = sentences[sidx - 1] if 0 <= sidx - 1 else ""
            after_ctx = sentences[sidx + 1] if 0 <= sidx and sidx + 1 < len(sentences) else ""
            point_context = local_rewrite.extract_point_context(article_text, target)
            point_context_found = point_context is not None
            if point_context is None:
                point_context = f"{before_ctx} {target} {after_ctx}".strip()
            r = local_rewrite.rewrite_ng_item(client, ledger_model, prod_gen.REASONING_EFFORT,
                                               verified_ledger_text, point_context, target,
                                               deviation, before_ctx, after_ctx, _run_check_window,
                                               use_target_sentence_matching=True)
            diff_qa_fc_model = routing.require_model("WRITER_FACT_CHECK", routing.WRITER_FACT_CHECK_MODEL)
            r = local_rewrite.apply_diff_qa_to_resolved_rewrite(
                r, client, topic_ja, before_ctx, after_ctx, verified_ledger_text, ledger_model,
                diff_qa_fc_model)
            r["cycle"] = cycle
            r["item_idx"] = idx
            r["location_method"] = location_method
            r["point_context_found"] = point_context_found
            if main_story_text_for_locus is not None:
                target_in_main_story, _ = local_rewrite.locate_target_sentence(
                    deviation["claim_in_article"], main_story_text_for_locus)
                r["locus"] = "main_story" if target_in_main_story is not None else "points"
            cycle_results.append(r)

        article_text = local_rewrite.apply_rewrites(article_text, cycle_results)
        article_text = prod_gen.normalize_article_formatting(article_text)
        with open(f"{out_dir}/audit/{tag}_article_after_cycle{cycle}.md", "w", encoding="utf-8") as f:
            f.write(article_text)

        deviation_result = vfl01.run_deviation_check(client, verified_ledger_text, article_text,
                                                      model=ledger_model, hook_aware=True)
        recheck_major = [d for d in deviation_result["parsed"]["deviations"] if d["severity"] == "MAJOR"]
        previously_seen_claims |= {d["claim_in_article"] for d in major_items}
        local_rewrite_results.extend(cycle_results)
        local_rewrite_cycles.append({
            "cycle": cycle, "targeted_major_count": len(major_items),
            "newly_discovered_claims": newly_discovered_claims, "results": cycle_results,
            "full_recheck_overall_status": deviation_result["parsed"]["overall_status"],
            "full_recheck_major_count": len(recheck_major),
            "full_recheck_remaining_major_claims": [d["claim_in_article"] for d in recheck_major],
        })
        major_items = recheck_major

    cycle_exhausted = bool(major_items) and cycle >= local_rewrite.MAX_REWRITE_CYCLES
    any_human_review = any(r.get("human_review_required") for r in local_rewrite_results)
    main_story_locus_unresolved = any(
        (r.get("locus") == "main_story") and not r.get("resolved") for r in local_rewrite_results)

    save_json(f"{out_dir}/{tag}_ledger_deviation.json", deviation_result["parsed"])
    save_json(f"{out_dir}/audit/{tag}_local_rewrite_cycles.json", local_rewrite_cycles)

    blocking = bool(major_items) or any_human_review
    return {
        "blocking": blocking, "article_text": article_text,
        "ledger_status": deviation_result["parsed"]["overall_status"],
        "major_count": len(major_items), "cycle_exhausted": cycle_exhausted,
        "local_rewrite_cycles": local_rewrite_cycles, "local_rewrite_results": local_rewrite_results,
        "main_story_locus_unresolved": main_story_locus_unresolved,
        "remaining_major_claims": [d["claim_in_article"] for d in major_items],
    }


# ============================================================
# Stage 1 QA一式: Fact Checker A' -> Ledger Deviation+Local Rewrite ->
# Directional Fact Precheck(Main Story単体、###見出しなしテキストに対して
# 実行する)。
# ============================================================
def run_stage1_qa(client, topic_ja: str, verified_ledger_text: str, writer_model: str,
                   title_line: str, main_story_text: str, out_dir: str) -> dict:
    stage1_article_text = f"{title_line}\n\n{main_story_text}\n"

    canonical_spelling_block = canon_spelling.build_canonical_spelling_fact_check_block(verified_ledger_text)
    fc_prompt = r3.build_fact_check_prompt(topic_ja, stage1_article_text, [],
                                            canonical_spelling_block=canonical_spelling_block)

    def make_fc_fn():
        return r3.make_fact_checker_fn(
            fc_prompt, model=routing.require_model("WRITER_FACT_CHECK", routing.WRITER_FACT_CHECK_MODEL))

    fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = \
        r3.run_fact_checker_with_gates(make_fc_fn, sleep_fn=time.sleep)
    fact_verdict = fc_result.get("verdict") if fc_result else None
    save_json(f"{out_dir}/stage1_fact_qa.json", {
        "final_status": fc_status, "model": fc_model, "response_id": fc_response_id,
        "attempts": len(fc_attempts), "result": fc_result,
    })

    if fact_verdict == "FAIL":
        return {"blocking": True, "reason": "stage1_fact_checker_fail", "fact_status": fc_status,
                "fact_verdict": fact_verdict, "article_text": stage1_article_text,
                "title_line": title_line, "main_story_text": main_story_text}

    ledger_model = writer_model
    ledger_loop = run_ledger_local_rewrite_loop(
        client, topic_ja, verified_ledger_text, stage1_article_text, ledger_model, out_dir, tag="stage1")

    if ledger_loop["blocking"]:
        return {"blocking": True, "reason": "stage1_ledger_major_unresolved", "fact_status": fc_status,
                "fact_verdict": fact_verdict, "ledger_status": ledger_loop["ledger_status"],
                "article_text": ledger_loop["article_text"], "title_line": title_line,
                "main_story_text": main_story_text, "local_rewrite_cycles": ledger_loop["local_rewrite_cycles"]}

    # Local Rewriteで本文が変わった可能性があるため、Title/Main Storyを再分離する。
    article_text = ledger_loop["article_text"]
    title_match = re.match(r"^#\s+.+?\s*\n", article_text)
    final_title_line = article_text[:title_match.end()].strip()
    final_main_story_text = article_text[title_match.end():].strip()

    directional_result = dfp.audit_article_directional_facts(
        article_text, verified_ledger_text, vfl_path=SOURCE_VFL_PATH)
    save_json(f"{out_dir}/stage1_directional_fact_precheck.json", directional_result)

    return {
        "blocking": False, "fact_status": fc_status, "fact_verdict": fact_verdict,
        "ledger_status": ledger_loop["ledger_status"], "local_rewrite_cycles": ledger_loop["local_rewrite_cycles"],
        "directional_status": directional_result["overall_status"],
        "title_line": final_title_line, "main_story_text": final_main_story_text,
        "article_text": article_text,
    }


# ============================================================
# Stage 2-3(Point Role Planning -> Point生成 -> Evidence Compression ->
# 結合 -> Point Overlap/Value QA)。NG時はStage 2からのみ再実行する
# (Main Storyは固定のまま、POINT_OVERLAP_ARTICLE_RETRY_MAX回まで)。
# ============================================================
def apply_evidence_compression_to_points(client, points_raw_text: str, writer_model: str, out_dir: str,
                                          attempt: int) -> dict:
    points_text_stripped, fact_usage_report = blueprint_mod.extract_trailing_metadata_block(
        points_raw_text.strip())
    ec_result = ec_editor.run_lossless_editor(client, points_text_stripped, model=writer_model)
    save_json(f"{out_dir}/audit/stage3_evidence_compression_attempt{attempt}.json",
              {k: v for k, v in ec_result.items() if k != "prompt"})
    candidate = (ec_result.get("raw_text") or "").strip()
    applied = False
    final_points_text = points_text_stripped
    if candidate and candidate.count("###") >= 2 and not re.search(r"^#\s+", candidate, flags=re.MULTILINE):
        final_points_text = candidate
        applied = True
    return {"points_text": final_points_text, "applied": applied, "fact_usage_report": fact_usage_report,
            "pre_ec_points_text": points_text_stripped}


def run_stage2_3_with_retry(client, topic_ja: str, verified_ledger_text: str, main_story_text: str,
                             title_line: str, writer_model: str, out_dir: str) -> dict:
    retry_attempt = 0
    overlap_retry_log = []

    stage2 = s2_prev.run_stage2_role_planning(
        client, topic_ja, verified_ledger_text, main_story_text, model=writer_model,
        reasoning_effort=prod_gen.REASONING_EFFORT)
    save_json(f"{out_dir}/audit/stage2_role_planning_attempt0.json", stage2)
    stage3 = s2_prev.run_stage3_points_writer(
        client, topic_ja, verified_ledger_text, main_story_text, stage2["parsed"], model=writer_model)

    while True:
        save_json(f"{out_dir}/audit/stage3_points_writer_attempt{retry_attempt}.json",
                  {k: v for k, v in stage3.items() if k != "prompt"})
        if stage3["status"] != "STRUCTURE_PASS" or not stage3.get("raw_text"):
            return {"status": stage3["status"], "article_text": None, "stage": "stage3_writer",
                    "retry_attempt": retry_attempt, "overlap_retry_log": overlap_retry_log}

        ec = apply_evidence_compression_to_points(client, stage3["raw_text"], writer_model, out_dir, retry_attempt)
        article_text, _ = s2_prev.assemble_article(title_line, main_story_text, ec["points_text"])

        sections = prod_gen.split_common_sections_for_point_qa(article_text)
        if sections is None:
            return {"status": "STRUCTURE_INVALID_AFTER_MERGE", "article_text": article_text,
                     "stage": "merge", "retry_attempt": retry_attempt, "overlap_retry_log": overlap_retry_log}
        main_story_reproduced_exactly = sections["full_story"] == main_story_text

        overlap_out_dir = f"{out_dir}/stage23_attempt{retry_attempt}"
        os.makedirs(overlap_out_dir, exist_ok=True)
        overlap_result = prod_gen.run_point_overlap_qa_and_regenerate(
            client, article_text, verified_ledger_text, model=writer_model,
            reasoning_effort=prod_gen.REASONING_EFFORT, out_dir=overlap_out_dir)
        overlap_report = overlap_result.get("report") or {}
        lexical_flagged = overlap_result["status"] == "OK" and any(
            overlap_report.get(key, {}).get("before_overlap", {}).get("flagged")
            for key in ("point_one", "point_two")
        ) or overlap_report.get("point_one_vs_point_two", {}).get("flagged") \
            or overlap_report.get("point_two_vs_point_one", {}).get("flagged")

        value_qa_result = point_planning.run_point_value_qa(
            client, sections["full_story"], sections["point_one_body"], sections["point_two_body"],
            model=writer_model, reasoning_effort=prod_gen.REASONING_EFFORT)
        save_json(f"{out_dir}/audit/stage3_point_value_qa_attempt{retry_attempt}.json", value_qa_result)
        value_qa_flagged = value_qa_result["status"] == "NG"

        still_flagged = lexical_flagged or value_qa_flagged
        overlap_retry_log.append({
            "attempt": retry_attempt, "lexical_flagged": lexical_flagged, "value_qa_flagged": value_qa_flagged,
            "evidence_compression_applied": ec["applied"], "main_story_reproduced_exactly": main_story_reproduced_exactly,
            "report": overlap_report, "value_qa_status": value_qa_result["status"],
        })
        if not still_flagged or retry_attempt >= prod_gen.POINT_OVERLAP_ARTICLE_RETRY_MAX:
            break

        retry_attempt += 1
        point_overlap_result = {
            "point_one": overlap_report["point_one"]["before_overlap"],
            "point_two": overlap_report["point_two"]["before_overlap"],
        }
        diagnostic_prompt = prod_gen.build_diagnostic_retry_prompt(
            stage3["prompt"], article_text, point_overlap_result)
        if value_qa_flagged:
            diagnostic_prompt = diagnostic_prompt + "\n\n" + point_planning.build_value_qa_diagnostic_note(
                value_qa_result)
        stage2 = s2_prev.run_stage2_role_planning(
            client, topic_ja, verified_ledger_text, main_story_text, model=writer_model,
            reasoning_effort=prod_gen.REASONING_EFFORT)
        save_json(f"{out_dir}/audit/stage2_role_planning_attempt{retry_attempt}.json", stage2)
        diagnostic_prompt = diagnostic_prompt + "\n" + point_planning.build_role_planning_block(stage2["parsed"])

        writer_result = vfl01.run_writer_with_technical_retry(client, diagnostic_prompt, model=writer_model)
        stage3 = {"status": writer_result["status"], "raw_text": writer_result.get("raw_text"),
                  "prompt": diagnostic_prompt, "attempts": writer_result["attempts"]}

    save_json(f"{out_dir}/stage23_overlap_retry_log.json", overlap_retry_log)

    if overlap_retry_log[-1]["lexical_flagged"] or overlap_retry_log[-1]["value_qa_flagged"]:
        return {"status": "NG_REVIEW_REQUIRED", "article_text": article_text, "stage": "overlap_value_qa",
                "retry_attempt": retry_attempt, "overlap_retry_log": overlap_retry_log, "sections": sections}

    return {"status": "OK", "article_text": article_text, "sections": sections,
            "retry_attempt": retry_attempt, "overlap_retry_log": overlap_retry_log,
            "stage2": stage2, "stage3": stage3}


# ============================================================
# 1記事分のオーケストレーション(Stage 1 <-> Stage 2-3の分岐を含む)。
# ============================================================
def generate_article_stage(level: str) -> dict:
    label = LEVELS[level]["label"]
    out_dir = f"{OUT_DIR}/{level}"
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    client = vfl01.get_client()
    verified_ledger_text, topic_ja = load_reused_ledger_and_topic()
    writer_model = routing.require_model(prod_gen._writer_process(label), routing.WRITER_MODEL)

    theme_tag = f"{THEME_ID}_{level}"
    t0 = time.time()
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    stage_trace = []

    with cl.logging_context(theme_tag, f"stage_split_{level}"):
        stage1_regen_attempt = 0
        feedback_block = ""
        while True:
            stage1 = run_stage1_main_story_writer(
                client, level, topic_ja, verified_ledger_text, writer_model, out_dir,
                feedback_block=feedback_block)
            if stage1["status"] != "STRUCTURE_PASS":
                result = {"label": label, "level": level, "status": stage1["status"],
                          "article_text": None, "stage": "stage1_writer",
                          "stage1_regen_attempt": stage1_regen_attempt}
                save_json(f"{out_dir}/run_summary.json", result)
                save_json(f"{out_dir}/audit/stage_trace.json", stage_trace)
                return result

            stage1_qa = run_stage1_qa(client, topic_ja, verified_ledger_text, writer_model,
                                       stage1["title_line"], stage1["main_story_text"], out_dir)
            stage_trace.append({"phase": "stage1", "attempt": stage1_regen_attempt,
                                 "blocking": stage1_qa["blocking"], "reason": stage1_qa.get("reason")})
            if not stage1_qa["blocking"] or stage1_regen_attempt >= STAGE1_MAX_REGENERATIONS:
                break
            stage1_regen_attempt += 1
            feedback_block = STAGE1_REGENERATION_FEEDBACK_TEMPLATE.format(reason=stage1_qa.get("reason"))

        if stage1_qa["blocking"]:
            result = {"label": label, "level": level, "status": "NG_REVIEW_REQUIRED",
                      "article_text": stage1_qa.get("article_text"), "stage": "stage1_qa_exhausted",
                      "reason": stage1_qa.get("reason"), "stage1_regen_attempt": stage1_regen_attempt}
            save_json(f"{out_dir}/run_summary.json", result)
            save_json(f"{out_dir}/audit/stage_trace.json", stage_trace)
            return result

        main_story_text = stage1_qa["main_story_text"]
        title_line = stage1_qa["title_line"]

        while True:
            stage23 = run_stage2_3_with_retry(
                client, topic_ja, verified_ledger_text, main_story_text, title_line, writer_model, out_dir)
            stage_trace.append({"phase": "stage2_3", "stage1_regen_attempt": stage1_regen_attempt,
                                 "status": stage23["status"], "retry_attempt": stage23.get("retry_attempt")})

            if stage23["status"] != "OK":
                if stage1_regen_attempt < STAGE1_MAX_REGENERATIONS:
                    # フォールバック分岐(b): Stage 2-3を尽くしてもNGのため、
                    # Main Story側原因の切り分けができない最終手段として
                    # Stage 1を1回だけ再生成する。
                    stage1_regen_attempt += 1
                    feedback_block = STAGE1_REGENERATION_FEEDBACK_TEMPLATE.format(
                        reason=f"Stage 2-3を{prod_gen.POINT_OVERLAP_ARTICLE_RETRY_MAX}回再実行しても"
                               f"Point Overlap/Value QAが解消しませんでした(status={stage23['status']})。"
                               f"Main Story側に、Pointとして展開しにくい要因がある可能性があります。")
                    stage1 = run_stage1_main_story_writer(
                        client, level, topic_ja, verified_ledger_text, writer_model, out_dir,
                        feedback_block=feedback_block)
                    if stage1["status"] != "STRUCTURE_PASS":
                        break
                    stage1_qa = run_stage1_qa(client, topic_ja, verified_ledger_text, writer_model,
                                               stage1["title_line"], stage1["main_story_text"], out_dir)
                    stage_trace.append({"phase": "stage1_escalated", "attempt": stage1_regen_attempt,
                                         "blocking": stage1_qa["blocking"], "reason": stage1_qa.get("reason")})
                    if stage1_qa["blocking"]:
                        break
                    main_story_text = stage1_qa["main_story_text"]
                    title_line = stage1_qa["title_line"]
                    continue
                break

            # Stage 2-3 OK: 記事全体に対しFact Checker A' + Ledger Deviation
            # (+Local Rewrite)+ Directional Precheckを再実行する。
            article_text = stage23["article_text"]
            canonical_spelling_block = canon_spelling.build_canonical_spelling_fact_check_block(verified_ledger_text)
            fc_prompt = r3.build_fact_check_prompt(topic_ja, article_text, [],
                                                    canonical_spelling_block=canonical_spelling_block)

            def make_fc_fn():
                return r3.make_fact_checker_fn(
                    fc_prompt, model=routing.require_model("WRITER_FACT_CHECK", routing.WRITER_FACT_CHECK_MODEL))

            fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = \
                r3.run_fact_checker_with_gates(make_fc_fn, sleep_fn=time.sleep)
            fact_verdict = fc_result.get("verdict") if fc_result else None
            save_json(f"{out_dir}/fact_qa.json", {
                "label": label, "final_status": fc_status, "model": fc_model, "response_id": fc_response_id,
                "attempts": len(fc_attempts), "result": fc_result,
            })

            if fact_verdict == "FAIL":
                stage_trace.append({"phase": "final_fact_checker", "verdict": "FAIL"})
                if stage1_regen_attempt < STAGE1_MAX_REGENERATIONS:
                    stage1_regen_attempt += 1
                    feedback_block = STAGE1_REGENERATION_FEEDBACK_TEMPLATE.format(
                        reason="記事全体のFact CheckerがFAIL(信頼できる情報と明確に矛盾)と判定しました。")
                    stage1 = run_stage1_main_story_writer(
                        client, level, topic_ja, verified_ledger_text, writer_model, out_dir,
                        feedback_block=feedback_block)
                    if stage1["status"] != "STRUCTURE_PASS":
                        break
                    stage1_qa = run_stage1_qa(client, topic_ja, verified_ledger_text, writer_model,
                                               stage1["title_line"], stage1["main_story_text"], out_dir)
                    if stage1_qa["blocking"]:
                        break
                    main_story_text = stage1_qa["main_story_text"]
                    title_line = stage1_qa["title_line"]
                    continue
                result = {"label": label, "level": level, "status": "NG_REVIEW_REQUIRED",
                          "article_text": article_text, "stage": "final_fact_checker_fail",
                          "fact_status": fc_status, "fact_verdict": fact_verdict}
                save_json(f"{out_dir}/run_summary.json", result)
                save_json(f"{out_dir}/audit/stage_trace.json", stage_trace)
                return result

            ledger_loop = run_ledger_local_rewrite_loop(
                client, topic_ja, verified_ledger_text, article_text, writer_model, out_dir,
                tag="final", main_story_text_for_locus=main_story_text)
            stage_trace.append({"phase": "final_ledger", "blocking": ledger_loop["blocking"],
                                 "main_story_locus_unresolved": ledger_loop["main_story_locus_unresolved"]})

            if ledger_loop["blocking"] and ledger_loop["main_story_locus_unresolved"] \
                    and stage1_regen_attempt < STAGE1_MAX_REGENERATIONS:
                # 分岐(a): Main Story側に位置するMAJORが解決しない -> Stage 1再生成
                stage1_regen_attempt += 1
                feedback_block = STAGE1_REGENERATION_FEEDBACK_TEMPLATE.format(
                    reason="記事全体のLedger Deviation Checkで、Main Story本文側に位置するMAJORが"
                           "Local Rewriteでも解消しませんでした。")
                stage1 = run_stage1_main_story_writer(
                    client, level, topic_ja, verified_ledger_text, writer_model, out_dir,
                    feedback_block=feedback_block)
                if stage1["status"] != "STRUCTURE_PASS":
                    break
                stage1_qa = run_stage1_qa(client, topic_ja, verified_ledger_text, writer_model,
                                           stage1["title_line"], stage1["main_story_text"], out_dir)
                if stage1_qa["blocking"]:
                    break
                main_story_text = stage1_qa["main_story_text"]
                title_line = stage1_qa["title_line"]
                continue

            if ledger_loop["blocking"]:
                result = {"label": label, "level": level, "status": "NG_REVIEW_REQUIRED",
                          "article_text": ledger_loop["article_text"], "stage": "final_ledger_major_unresolved",
                          "ledger_status": ledger_loop["ledger_status"]}
                save_json(f"{out_dir}/run_summary.json", result)
                save_json(f"{out_dir}/audit/stage_trace.json", stage_trace)
                return result

            article_text = ledger_loop["article_text"]
            directional_result = dfp.audit_article_directional_facts(
                article_text, verified_ledger_text, vfl_path=SOURCE_VFL_PATH)
            save_json(f"{out_dir}/audit/final_directional_fact_precheck.json", directional_result)

            sections = prod_gen.split_common_sections_for_point_qa(article_text)
            metrics = prod_gen.compute_metrics(article_text)
            with open(f"{out_dir}/article.md", "w", encoding="utf-8") as f:
                f.write(article_text)

            elapsed = round(time.time() - t0, 2)
            result = {
                "label": label, "level": level, "status": "OK", "article_text": article_text,
                "word_count": metrics["word_count"],
                "section_word_counts": {"point_one": len(sections["point_one_body"].split()),
                                          "point_two": len(sections["point_two_body"].split())},
                "fact_status": fc_status, "fact_verdict": fact_verdict,
                "ledger_status": ledger_loop["ledger_status"],
                "directional_fact_precheck_status": directional_result["overall_status"],
                "stage1_regen_attempts": stage1_regen_attempt,
                "stage2_3_retry_attempts": stage23["retry_attempt"],
                "overlap_retry_log": stage23["overlap_retry_log"],
                "final_local_rewrite_cycles": ledger_loop["local_rewrite_cycles"],
                "elapsed_seconds": elapsed,
            }
            save_json(f"{out_dir}/run_summary.json", {k: v for k, v in result.items() if k != "article_text"})
            save_json(f"{out_dir}/audit/stage_trace.json", stage_trace)
            print(f"[{THEME_ID}][{level}] status=OK fact_verdict={fact_verdict} "
                  f"ledger_status={result['ledger_status']} stage1_regen={stage1_regen_attempt} "
                  f"stage2_3_retry={stage23['retry_attempt']} elapsed={elapsed}s")
            return result

        # ループを抜けた(全ての分岐を尽くしてもNG)場合
        result = {"label": label, "level": level, "status": "NG_REVIEW_REQUIRED",
                  "article_text": None, "stage": "all_branches_exhausted",
                  "stage1_regen_attempts": stage1_regen_attempt}
        save_json(f"{out_dir}/run_summary.json", result)
        save_json(f"{out_dir}/audit/stage_trace.json", stage_trace)
        print(f"[{THEME_ID}][{level}] STOP: all_branches_exhausted")
        return result


# ============================================================
# 費用実測(前回Trialと同一ロジック、read-onlyで転記して再利用)。
# ============================================================
USD_JPY = 160.0
_PRICING = json.load(open("er005_output/cost_baseline_01/pricing_snapshot.json", encoding="utf-8"))["prices"]


def _price(provider, model, meter, tier="Standard"):
    for p in _PRICING:
        if p["provider"] == provider and p["model"] == model and p["meter"] == meter and p.get("tier", "Standard") == tier:
            return p["price"]
    raise KeyError((provider, model, meter, tier))


def _call_cost_usd(r: dict) -> tuple:
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
        return 0.0, True
    except KeyError:
        return 0.0, True


def compute_cost_jpy_so_far() -> dict:
    log_path = f"{OUT_DIR}/raw_usage_log.jsonl"
    if not os.path.exists(log_path):
        return {"total_jpy": 0.0, "by_provider_jpy": {}, "by_stage_jpy": {}, "unpriced_records": 0, "total_records": 0}
    total_usd, by_provider, by_stage, unpriced = 0.0, {}, {}, 0
    n = 0
    with open(log_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            cost, up = _call_cost_usd(rec)
            total_usd += cost
            by_provider[rec.get("provider")] = by_provider.get(rec.get("provider"), 0.0) + cost * USD_JPY
            stage_key = rec.get("theme_id") or rec.get("stage")
            by_stage[stage_key] = by_stage.get(stage_key, 0.0) + cost * USD_JPY
            unpriced += int(up)
            n += 1
    return {
        "total_jpy": round(total_usd * USD_JPY, 2),
        "by_provider_jpy": {k: round(v, 2) for k, v in by_provider.items()},
        "by_stage_jpy": {k: round(v, 2) for k, v in by_stage.items()},
        "unpriced_records": unpriced, "total_records": n,
    }


def cost_stage() -> dict:
    result = compute_cost_jpy_so_far()
    save_json(f"{OUT_DIR}/cost_summary.json", result)
    print(f"[{THEME_ID}][cost] 実測合計={result['total_jpy']} JPY (上限{BUDGET_JPY_CAP}) "
          f"by_provider={result['by_provider_jpy']}")
    if result["total_jpy"] > BUDGET_JPY_CAP:
        raise RuntimeError(f"費用上限超過(実測{result['total_jpy']}円 > 上限{BUDGET_JPY_CAP}円)。STOP。")
    return result


def main() -> dict:
    stages = sys.argv[1:] or ["all"]
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")

    if stages == ["all"]:
        results = {}
        for level in ("a2", "b1b"):
            try:
                results[level] = generate_article_stage(level)
            except (RuntimeError, AssertionError) as e:
                results[level] = {"level": level, "status": "STOP", "error": str(e)}
                print(f"[{THEME_ID}][{level}] STOP: {e}")
            cost_stage()
        save_json(f"{OUT_DIR}/e2e_run_summary.json",
                  {k: ({kk: vv for kk, vv in v.items() if kk != "article_text"} if isinstance(v, dict) else v)
                   for k, v in results.items()})
        print(f"[{THEME_ID}] 完了。")
        return results

    result = {}
    for s in stages:
        if s in ("a2", "b1b"):
            result[s] = generate_article_stage(s)
        elif s == "cost":
            result["cost"] = cost_stage()
        else:
            print(f"unknown stage: {s}")
    save_json(f"{OUT_DIR}/e2e_run_summary_partial_{'_'.join(stages)}.json",
              {k: ({kk: vv for kk, vv in v.items() if kk != "article_text"} if isinstance(v, dict) else v)
               for k, v in result.items()})
    return result


if __name__ == "__main__":
    main()

# ============================================================
# er003_discovery_focus_staged_production_01.py
# 管理ID: FAMILY-A-DISCOVERY-S2-PRODUCTION-WIRING-01
# ============================================================
# 目的: Discovery Focus S2(Focusを先に決める→Main Storyを確定する→その
# Main Story本文を見てPoint Role Planning→Point生成)のProduction配線。
# ユーザー正式承認(APPROVED_FOR_PRODUCTION、2026-09-13、
# `FAMILY-A-DISCOVERY-S2-PRODUCTION-DESIGN-01_REPORT.md`推奨案=P1)に基づく。
#
# 【分割方式P1(採用)】
# 既存`er003_v1_n3_01_articles_generate.run_one_pattern`は無変更のまま
# 残す。本モジュールはDiscovery専用のopt-in新経路であり、呼び出し側が
# `editorial_mode="discovery_focus_staged"`を明示的に指定した場合のみ
# `run_one_pattern_staged_discovery_focus()`が呼ばれる。News Major/Daily/
# Trend Synthesis/現行Discovery非staged(`run_one_pattern`直接呼び出し)の
# 挙動には一切影響しない。
#
# 【正式処理順(ユーザー確定、変更不可)】
# Focus解決(`prod_gen.EDITORIAL_TYPE_MODULE_BLOCKS["discovery_focus_staged"]`)
#   → Stage 1: Main Story Writer(Title+Main Story+draft In One Line)
#   → Stage 1 QA: Fact Checker A' → Ledger Deviation+Local Rewrite →
#     Directional Fact Precheck(non-blocking)
#   → [blocking時、STAGE1_MAX_REGENERATIONSまでStage 1再生成]
#   → Stage 2: Point Role Planning(確定Main Story本文を入力、角度hintなし)
#   → Stage 3: Point One/Two Writer → Evidence Compression(Points本文のみ)
#     → Main Story(固定)と結合
#   → Point Overlap QA / Point Value QA(NG時はStage 2-3のみ再実行、
#     POINT_OVERLAP_ARTICLE_RETRY_MAX回まで。Stage2-3 exhaustion後の
#     フォールバックとして、Main Story側原因切り分け不能時のみStage 1へ
#     escalateする余地あり=Fact Checker FAIL locus案(ii)簡略ルールと同型)
#   → 記事全体Fact Checker A'(FAILはblocking。Stage2-3 exhaustion後の
#     フォールバックとしてのみStage 1へescalate、案(ii)簡略ルール)
#   → 記事全体Ledger Deviation Check + Local Rewrite(+差分QA、OPEN-141
#     既定ON)。MAJOR残存時、`locate_target_sentence`でlocus判定→Main
#     Story側ならStage 1再生成へescalate、Points側/不明ならNG_REVIEW_REQUIRED
#   → Directional Fact Precheck(記事全体、non-blocking)
#   → OK/NG_REVIEW_REQUIRED確定。
#
# `STAGE1_MAX_REGENERATIONS=1`(ユーザー確定案1)。通常retryはStage 2-3のみ
# (`POINT_OVERLAP_ARTICLE_RETRY_MAX`、既存Production値2をそのまま流用)。
# Main Story固定原則: Stage 2からStage 3を通じてMain Story本文(Stage 1で
# 確定した範囲)は原則不変。ただし既存の安全装置(Ledger Deviation Check+
# Local Rewrite、差分QA)がMain Story側1文にMAJOR逸脱を検出し局所修正する
# 場合は例外として許容する(Stage 1再生成[全文書き直し]とLocal Rewrite
# [局所修正]は区別し、後者は既存安全装置の通常動作として扱う。設計REPORT
# 4節仕様文案どおり)。
#
# 【移設(Trial専用実装からの正式移設、暫定importを残さない)】
# 以下はTrial専用ファイルからProduction側(本ファイル)へ移設したもの
# (移設後、本ファイルはTrialファイルを一切importしない):
#   - extract_stage1_main_story / run_stage1_main_story_writer /
#     run_ledger_local_rewrite_loop / run_stage1_qa / STAGE1_*定数:
#     移設元 `er011_discovery_focus_s2_full_trial_01.py`
#   - run_stage2_role_planning / STAGE2_ROLE_PLANNING_PROMPT_TEMPLATE /
#     run_stage3_points_writer / STAGE3_POINTS_ONLY_PROMPT_TEMPLATE /
#     assemble_article:
#     移設元 `er011_discovery_focus_part_a_standalone_trial_01_run.py`
#   - apply_evidence_compression_to_points / run_stage2_3_with_retry /
#     オーケストレーション本体:
#     移設元 `er011_discovery_focus_s2_full_trial_01.py`
#   - Focus Module Part A本文: `er003_v1_n3_01_articles_generate.
#     DISCOVERY_FOCUS_MODULE_PART_A_BLOCK`(正式登録済み、移設元は
#     `er011_discovery_stage3_rule_adjustment_trial_09.CURRENT_FOCUS_BLOCK`)。
# 上記Trial専用ファイル自体はarchive目的でGitに残置するが、本ファイルは
# それらを一切importしない(Gate 4 Dangling Reference Check該当ゼロ)。
# 既存Production関数(vfl01/r3/dfp/local_rewrite/point_planning/ec_editor/
# canon_spelling/routing/cl/blueprint_mod配下)はすべてimportした関数
# オブジェクトをそのまま呼ぶ(コピー・再実装しない)。
# ============================================================
from __future__ import annotations

import json
import os
import re
import time

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
import er011_open146_ledger_canonical_en_spelling_production_01 as canon_spelling
import er011_point_role_value_planning_01 as point_planning

EDITORIAL_MODE = "discovery_focus_staged"

LEVELS = {
    "a2": {"label": "A2", "instruction": prod_gen.A2_KAI1_INSTRUCTION},
    "b1b": {"label": "B1B", "instruction": prod_gen.B1_B_DIRECT_INSTRUCTION},
}

STAGE1_MAX_REGENERATIONS = 1  # ユーザー確定案1(設計REPORT3節)


def save_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


# ============================================================
# Stage 1: Main Story(+In One Line案)のみを書かせる。
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
        editorial_type_module_block=prod_gen.DISCOVERY_FOCUS_MODULE_PART_A_BLOCK)
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
# Ledger Deviation Check + Local Rewrite(既存run_one_patternのLedger
# Deviation+Local Rewriteループを、Stage 1単体/記事全体の両方から共通で
# 呼べるよう関数化。呼ぶ個々の関数は全てimportした関数オブジェクトを
# そのまま使う)。main_story_text_for_locusを渡した場合のみ、残存MAJORの
# claim_in_articleがMain Story側かPoints側かを判定する(Stage 1
# escalation判定用)。
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
                   title_line: str, main_story_text: str, out_dir: str, vfl_path: str | None = None) -> dict:
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
        article_text, verified_ledger_text, vfl_path=vfl_path)
    save_json(f"{out_dir}/stage1_directional_fact_precheck.json", directional_result)

    return {
        "blocking": False, "fact_status": fc_status, "fact_verdict": fact_verdict,
        "ledger_status": ledger_loop["ledger_status"], "local_rewrite_cycles": ledger_loop["local_rewrite_cycles"],
        "directional_status": directional_result["overall_status"],
        "title_line": final_title_line, "main_story_text": final_main_story_text,
        "article_text": article_text,
    }


# ============================================================
# Stage 2: Point Role Planning(確定Main Story本文を実際に読ませる)。
# 移設元: er011_discovery_focus_part_a_standalone_trial_01_run.py
# ============================================================
STAGE2_ROLE_PLANNING_PROMPT_TEMPLATE = """これから、以下のVerified Fact Ledgerと、既に確定済みのMain Story本文に基づいて、
英語ニュースpodcast記事のPoint One・Point Twoを設計します。Main Storyは既に
別の工程で完成しており、この後変更されません。

【今回のテーマ】
{topic}

【Verified Fact Ledger】
{verified_ledger_text}

【既に確定済みのMain Story本文(実際にこの内容が記事に使われます)】
{main_story_text}

Point One・Point Twoそれぞれについて、以下を具体的に(このLedgerとこの確定済み
Main Story固有の内容で、どんな記事にも当てはまるテンプレート的な一般論に
ならないように)決めてください。must_not_overlap_with_full_storyは、上記
Main Story本文を実際に読んだ上で、その具体的な記述内容に基づいて答えてください
(まだ書かれていない一般的な予測ではなく、実際の文面に基づく判断にしてください)。

- role: このPointが記事の中で担う具体的な役割(例: 意外な詳細、方法論上の
  ニュアンス、歴史的な対比、心理的な理由。固定テンプレートではなく、この
  Ledger・このMain Storyに合わせて決めること)
- new_listener_takeaway: 聞き手がこのPointを聞いて新しく持ち帰る、具体的な
  理解・示唆・視点(上記Main Storyを聞いただけでは得られないもの)
- evidence_anchor: このPointの内容が、Verified Fact Ledgerのどの事実・
  データに基づくか
- why_it_matters: このPointが「だから何なのか」に対して与える具体的な答え
  (単なる一般的な留保・免責事項ではなく、聞き手にとっての意味)
- must_not_overlap_with_full_story: 上記Main Story本文で既に説明されている
  内容のうち、このPointで繰り返してはいけない具体的な内容
- must_not_overlap_with_other_point: もう一方のPointが担う内容のうち、
  このPointで重複させてはいけない具体的な内容

【禁止(重要)】
以下のようなPointは、たとえPoint OneとPoint Twoの文字列が違っていても
価値が無いとみなされます。計画段階でこれらを避けてください:
- 研究上の限界・一般化上の注意・免責事項だけで構成されるPoint
- 上記Main Storyの要約・言い換えに留まるPoint
- もう一方のPointの要約・言い換えになっているPoint
- 「だから何なのか」を説明できないPoint
- 他のどんな記事にもほぼそのまま流用できる一般論
- 新しい理解・解釈・意外性・具体的示唆のいずれも加えていないPoint

必要な留保・注意書き自体を書くこと自体は禁止されていませんが、それだけで
Point枠全体を使わないでください(留保は、新しい価値を含む内容に添える
補足として書いてください)。

【出力】
point_one/point_twoそれぞれについて、上記6項目を1〜2文の英語で簡潔に
記述してください(内部設計用であり、リスナーには見せません)。
"""


def run_stage2_role_planning(client, topic: str, verified_ledger_text: str, main_story_text: str,
                              model: str, reasoning_effort: str) -> dict:
    prompt = STAGE2_ROLE_PLANNING_PROMPT_TEMPLATE.format(
        topic=topic, verified_ledger_text=verified_ledger_text, main_story_text=main_story_text)
    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        text={"format": {"type": "json_schema", **point_planning.ROLE_PLANNING_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": point_planning.ROLE_PLANNING_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    if response.model != model:
        raise point_planning.RolePlanningModelMismatchError(
            f"応答モデルが不一致です(期待: {model}, 実際: {response.model})")
    text = getattr(response, "output_text", None)
    if not text or not text.strip():
        raise RuntimeError("Stage 2 Point Role Planning応答が空です")
    parsed = json.loads(text)
    return {"parsed": parsed, "model": response.model, "response_id": response.id, "prompt": prompt}


# ============================================================
# Stage 3: Point One/Two/In One Lineのみを書かせる(Main Storyは書かせない)
# 移設元: er011_discovery_focus_part_a_standalone_trial_01_run.py
# ============================================================
STAGE3_POINTS_ONLY_PROMPT_TEMPLATE = """あなたはこれから、英語ニュースpodcast記事のPoint One・Point Two・
In One Lineだけを書きます。Main Storyは既に別の工程で完成しており、
あなたはMain Storyを書きません(参考として下に示すだけです)。

【今回のテーマ】
{topic}

【Verified Fact Ledger】
{verified_ledger_text}

【既に確定済みのMain Story本文(そのまま使われます。書き直したり、要約・
言い換えとして繰り返したりしないでください)】
{main_story_text}

{role_planning_block}

【出力形式(重要、厳守してください)】
- タイトルやMain Storyは一切出力しないでください。あなたの出力はPoint One
  相当・Point Two相当・In One Lineの3つの部分だけにしてください。
- Markdownの「###」見出しをちょうど2つ、Point One相当・Point Two相当として
  出力してください。見出し文自体に"Point One"・"Point Two"・"Point 1"・
  "Point 2"・「第一に」・「第二に」という文字列を使わないでください
  (短く、内容を示す見出しにしてください)。
- Point One・Point Twoの本文は、それぞれ英語で{target_lower}〜{target_upper}語
  程度にしてください(許容範囲{tolerance_lower}〜{tolerance_upper}語)。
- 最後に"## In one line"という見出しを置き、その後に記事全体を静かに一言で
  結ぶ英語1〜2文を書いてください。単なる要約にはしないでください。
- Point One・Point Twoは、上記Main Storyの言い換え・要約であってはいけません。
  互いの言い換えであってもいけません。上記のPoint Role Planningで計画した
  役割・新しい価値に厳密に従ってください。
"""


def run_stage3_points_writer(client, topic: str, verified_ledger_text: str, main_story_text: str,
                              role_plan_parsed: dict, model: str) -> dict:
    role_block = point_planning.build_role_planning_block(role_plan_parsed)
    prompt = STAGE3_POINTS_ONLY_PROMPT_TEMPLATE.format(
        topic=topic, verified_ledger_text=verified_ledger_text, main_story_text=main_story_text,
        role_planning_block=role_block,
        target_lower=prod_gen.POINT_TARGET_LOWER, target_upper=prod_gen.POINT_TARGET_UPPER,
        tolerance_lower=prod_gen.POINT_TOLERANCE_LOWER, tolerance_upper=prod_gen.POINT_TOLERANCE_UPPER,
    )
    writer_result = vfl01.run_writer_with_technical_retry(client, prompt, model=model)
    writer_result["prompt"] = prompt
    return writer_result


def assemble_article(title_line: str, main_story_text: str, points_raw_text: str) -> tuple:
    points_text, fact_usage_report = blueprint_mod.extract_trailing_metadata_block(points_raw_text.strip())
    merged = f"{title_line}\n\n{main_story_text}\n\n{points_text}\n"
    merged = prod_gen.normalize_article_formatting(merged)
    return merged, fact_usage_report


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

    stage2 = run_stage2_role_planning(
        client, topic_ja, verified_ledger_text, main_story_text, model=writer_model,
        reasoning_effort=prod_gen.REASONING_EFFORT)
    save_json(f"{out_dir}/audit/stage2_role_planning_attempt0.json", stage2)
    stage3 = run_stage3_points_writer(
        client, topic_ja, verified_ledger_text, main_story_text, stage2["parsed"], model=writer_model)

    while True:
        save_json(f"{out_dir}/audit/stage3_points_writer_attempt{retry_attempt}.json",
                  {k: v for k, v in stage3.items() if k != "prompt"})
        if stage3["status"] != "STRUCTURE_PASS" or not stage3.get("raw_text"):
            return {"status": stage3["status"], "article_text": None, "stage": "stage3_writer",
                    "retry_attempt": retry_attempt, "overlap_retry_log": overlap_retry_log}

        ec = apply_evidence_compression_to_points(client, stage3["raw_text"], writer_model, out_dir, retry_attempt)
        article_text, _ = assemble_article(title_line, main_story_text, ec["points_text"])

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
        stage2 = run_stage2_role_planning(
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
# 1記事分のオーケストレーション(Discovery専用opt-in経路。
# `editorial_mode="discovery_focus_staged"`明示指定時のみ呼ばれる。
# 既存`run_one_pattern`とは独立した別関数であり、`run_one_pattern`は
# 一切変更・呼び出ししない)。
# ============================================================
def run_one_pattern_staged_discovery_focus(client, level: str, topic_ja: str, verified_ledger_text: str,
                                            out_dir: str, theme_tag: str | None = None,
                                            vfl_path: str | None = None) -> dict:
    label = LEVELS[level]["label"]
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    writer_model = routing.require_model(prod_gen._writer_process(label), routing.WRITER_MODEL)
    theme_tag = theme_tag or f"discovery_focus_staged_{level}"
    t0 = time.time()
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
                                       stage1["title_line"], stage1["main_story_text"], out_dir,
                                       vfl_path=vfl_path)
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
                                               stage1["title_line"], stage1["main_story_text"], out_dir,
                                               vfl_path=vfl_path)
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
                                               stage1["title_line"], stage1["main_story_text"], out_dir,
                                               vfl_path=vfl_path)
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
                                           stage1["title_line"], stage1["main_story_text"], out_dir,
                                           vfl_path=vfl_path)
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
                article_text, verified_ledger_text, vfl_path=vfl_path)
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
            print(f"[{theme_tag}][{level}] status=OK fact_verdict={fact_verdict} "
                  f"ledger_status={result['ledger_status']} stage1_regen={stage1_regen_attempt} "
                  f"stage2_3_retry={stage23['retry_attempt']} elapsed={elapsed}s")
            return result

        # ループを抜けた(全ての分岐を尽くしてもNG)場合
        result = {"label": label, "level": level, "status": "NG_REVIEW_REQUIRED",
                  "article_text": None, "stage": "all_branches_exhausted",
                  "stage1_regen_attempts": stage1_regen_attempt}
        save_json(f"{out_dir}/run_summary.json", result)
        save_json(f"{out_dir}/audit/stage_trace.json", stage_trace)
        print(f"[{theme_tag}][{level}] STOP: all_branches_exhausted")
        return result

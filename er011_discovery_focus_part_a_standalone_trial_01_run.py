# ============================================================
# er011_discovery_focus_part_a_standalone_trial_01_run.py
# 管理ID: FAMILY-A-DISCOVERY-FOCUS-PART-A-STANDALONE-DESIGN-TRIAL-01
# ============================================================
# 目的(ユーザー基本設計、2026-09-13): 「Focusを先に決める→Main StoryはFocusに
# 従う→Point Role PlanningはMain Story成立後→Pointはその後で新しい価値を
# 探す」という順序(案S2)を、現行Production run_one_pattern(Point Role
# PlanningがWriter呼び出しより前に実行される順序)とは別に、最小Trialとして
# 検証する。**Trial(Production実装ではない)。Production採用はしない**
# (Gate 1=VALIDATED相当までが上限)。Production registry登録・Production
# run_one_patternの改変・QA判定ロジックの変更は一切行わない。
#
# 【設計の要点(何が新しいか)】
# Stage 1 (Main Story): 新規生成しない。既存Trial
#   `discovery_focus_module_revalidation_01`のfocus腕(Focus Module Part A
#   有効、現行Production run_one_patternで生成済み、Fact Checker PASS・
#   Ledger Deviation LEDGER_COMPLIANT確認済み)のarticle.mdからMain Story
#   本文をread-onlyで抽出し、そのまま「既に確定済みのMain Story」として
#   固定する(再生成しない=既存結果の再利用、無駄なコストを払わない)。
# Stage 2 (Point Role Planning): 新規LLM呼び出し。現行Production
#   `run_point_role_planning`(topic+ledgerのみ)とは異なり、Stage 1の実際の
#   Main Story本文をpromptへ渡す。案2(hint注入)のような具体的な角度
#   (mechanism/limitation/different angle等)は一切追加しない(既存
#   `ROLE_PLANNING_PROMPT_TEMPLATE`のrole例示[意外な詳細/方法論上の
#   ニュアンス/歴史的な対比/心理的な理由]をそのまま踏襲するのみ)。
# Stage 3 (Point生成): 新規LLM呼び出し。Main Storyは書かせず(既に確定済み
#   として渡すのみ)、Point One/Point Two/In One Lineだけを、Stage 2の
#   Role Planning結果に従って書かせる。
# 結合: title行 + Stage 1のMain Story本文(無変更) + Stage 3の出力を単純
#   連結する(Main Story自体は一切書き直さない)。
#
# 【再利用(import・無変更、コピーしない)】
#   - er003_v1_n3_01_articles_generate(prod_gen): split_common_sections_
#     for_point_qa/run_point_overlap_qa_and_regenerate/normalize_article_
#     formatting/POINT_TARGET_*/POINT_TOLERANCE_*/_writer_process/
#     REASONING_EFFORTをそのままprod_gen.NAMEで呼び出す。
#   - er011_point_role_value_planning_01(point_planning): build_role_
#     planning_block/run_point_value_qa/ROLE_PLANNING_JSON_SCHEMA/
#     ROLE_PLANNING_DEVELOPER_MESSAGE/RolePlanningModelMismatchErrorを
#     そのまま再利用。
#   - er002_ja_web_research_r3(r3)/er003_v1_en_direct_vfl_01_generate
#     (vfl01)/er011_open146_ledger_canonical_en_spelling_production_01
#     (canon_spelling)/er006_model_routing_contract_01(routing)/
#     er008_shared_point_blueprint_01(blueprint_mod)/er005_cost_logger
#     (cl)も全てimportのみ、無変更。
#
# 【新規に書いたもの(Trial限定)】
#   - STAGE2_ROLE_PLANNING_PROMPT_TEMPLATE / run_stage2_role_planning:
#     Main Story本文を実際に読ませたうえでRole Planningを行わせる新しい
#     prompt(Production `run_point_role_planning`のコピー・改変ではなく、
#     新規テンプレート。JSON schema/developer message/例外クラスは
#     point_planningモジュールのものをそのまま再利用)。
#   - STAGE3_POINTS_ONLY_PROMPT_TEMPLATE / run_stage3_points_writer:
#     Point One/Two/In One Lineのみを書かせる新しいprompt(Main Story
#     生成部分を含まないため、Production `run_one_pattern`の分割コピーでは
#     ない。構造検証はvfl01.run_writer_with_technical_retryをそのまま
#     再利用[「###」見出し2件+本文の有無のみを見る決定的チェックで、
#     Title/Main Story/In One Lineの有無は見ない=無改変のまま安全に
#     再利用可能])。
#
# 【本Trialが再現しないもの(限界、正直に記録する)】
#   - Point Overlap/Value QA retry(POINT_OVERLAP_ARTICLE_RETRY_MAX、
#     Diagnostic Full Retry): 本Trialは単発実行のみ。NGが出た場合は
#     Productionのように全体を再生成せず、NG_REVIEW_REQUIREDとして記録・
#     停止する(fail-closed、安全側)。
#   - Local Rewrite(Ledger MAJOR検出時の局所書き換えループ): 本Trialでは
#     未実装。Ledger Deviationで新たなMAJORが検出された場合は、Local
#     Rewriteを試みずNG_REVIEW_REQUIREDとして記録・停止する(fail-closed)。
#   - Directional Fact Precheck: 未実施(スコープ外)。
#   - Evidence Compression: Stage 3では未適用(Main Story側は既にStage 1
#     生成時[revalidation_01]でapply_evidence_compression=True適用済み)。
#   これらは全て「Production retry/安全装置を回避した」のではなく、
#   「本Trialでは実行しておらず、S2をProduction化する場合は別途配線が
#   必要」という未解決事項としてREPORTへ明記する。
#
# 実行方法(root直下から):
#   .venv/Scripts/python.exe er011_discovery_focus_part_a_standalone_trial_01_run.py [stage ...]
#   stage: a2 | b1b | evaluate | cost | all(省略時)
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
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as prod_gen
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er008_shared_point_blueprint_01 as blueprint_mod
import er011_open146_ledger_canonical_en_spelling_production_01 as canon_spelling
import er011_point_role_value_planning_01 as point_planning

THEME_ID = "discovery_focus_part_a_standalone_trial_01"
OUT_DIR = f"er011_output/{THEME_ID}"
BUDGET_JPY_CAP = 150.0  # 実行前見積(下記参照)に対し十分な余裕を取った上限。
# Discovery Trial残額(¥253.53)以内。

# 既存Trial(discovery_focus_module_revalidation_01)のfocus腕をMain Storyの
# 確定済み出典として再利用する(再生成しない)。同Ledger/topicも同一Trialの
# research成果物をread-onlyで再利用する。
MAIN_STORY_SOURCE = {
    "a2": "er011_output/discovery_focus_module_revalidation_01/a2_focus/article.md",
    "b1b": "er011_output/discovery_focus_module_revalidation_01/b1b_focus/article.md",
}
SOURCE_LEDGER_PATH = "er011_output/discovery_generalization_wake_before_alarm_trial_12/research/verified_fact_ledger.txt"
SOURCE_TOPIC_PATH = "er011_output/discovery_generalization_wake_before_alarm_trial_12/research/writer_topic.json"

LEVEL_LABELS = {"a2": "A2", "b1b": "B1B"}


def save_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def load_reused_ledger_and_topic() -> tuple:
    verified_ledger_text = load_text(SOURCE_LEDGER_PATH)
    topic_ja = load_json(SOURCE_TOPIC_PATH)["topic_ja"]
    return verified_ledger_text, topic_ja


def load_fixed_main_story(level: str) -> dict:
    """既存focus腕article.mdからMain Story本文をread-onlyで抽出する。
    prod_gen.split_common_sections_for_point_qa(既存Production関数、
    無変更)を再利用するのみで、新しいparsingロジックは書かない。"""
    source_path = MAIN_STORY_SOURCE[level]
    article_text = load_text(source_path)
    sections = prod_gen.split_common_sections_for_point_qa(article_text)
    if sections is None:
        raise RuntimeError(f"{source_path}: 想定構造(###見出し2つ)が見つかりません")
    title_match = re.match(r"^#\s+.+?\s*$", article_text, flags=re.MULTILINE)
    title_line = title_match.group(0).strip() if title_match else ""
    return {
        "source_path": source_path,
        "title_line": title_line,
        "main_story_text": sections["full_story"],
        "source_point_one_body_discarded": sections["point_one_body"],
        "source_point_two_body_discarded": sections["point_two_body"],
    }


# ============================================================
# Stage 2: Point Role Planning(Main Story本文を実際に読ませる新規prompt)
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
# 1記事分の全体オーケストレーション(Stage 2 -> Stage 3 -> 結合 ->
# 既存QA一式を単発実行[retry/Local Rewriteは実施しない、上記限界参照])
# ============================================================
def generate_article_stage(level: str) -> dict:
    label = LEVEL_LABELS[level]
    out_dir = f"{OUT_DIR}/{level}"
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    client = vfl01.get_client()
    verified_ledger_text, topic_ja = load_reused_ledger_and_topic()
    fixed_main_story = load_fixed_main_story(level)
    save_json(f"{out_dir}/audit/fixed_main_story_source.json", fixed_main_story)

    writer_model = routing.require_model(prod_gen._writer_process(label), routing.WRITER_MODEL)

    theme_tag = f"{THEME_ID}_{level}"
    t0 = time.time()
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    with cl.logging_context(theme_tag, f"stage_split_{level}"):
        stage2 = run_stage2_role_planning(
            client, topic_ja, verified_ledger_text, fixed_main_story["main_story_text"],
            model=writer_model, reasoning_effort=prod_gen.REASONING_EFFORT)
        save_json(f"{out_dir}/audit/stage2_role_planning.json", stage2)

        stage3 = run_stage3_points_writer(
            client, topic_ja, verified_ledger_text, fixed_main_story["main_story_text"],
            stage2["parsed"], model=writer_model)
        save_json(f"{out_dir}/audit/stage3_points_writer_attempts.json",
                  {k: v for k, v in stage3.items() if k != "prompt"})

        if stage3["status"] != "STRUCTURE_PASS" or not stage3.get("raw_text"):
            result = {"label": label, "level": level, "status": stage3["status"], "article_text": None,
                      "stage": "stage3_writer"}
            save_json(f"{out_dir}/run_summary.json", result)
            return result

        article_text, fact_usage_report = assemble_article(
            fixed_main_story["title_line"], fixed_main_story["main_story_text"], stage3["raw_text"])
        with open(f"{out_dir}/article.md", "w", encoding="utf-8") as f:
            f.write(article_text)

        sections = prod_gen.split_common_sections_for_point_qa(article_text)
        if sections is None:
            result = {"label": label, "level": level, "status": "STRUCTURE_INVALID_AFTER_MERGE",
                      "article_text": article_text, "stage": "merge"}
            save_json(f"{out_dir}/run_summary.json", result)
            return result

        main_story_reproduced_exactly = sections["full_story"] == fixed_main_story["main_story_text"]

        # Point Overlap QA(既存Production関数を無変更で再利用。
        # POINT_ONLY_REGENERATION_ENABLED=Falseのため本文は書き換えず、
        # flagのみ記録する)。
        overlap_result = prod_gen.run_point_overlap_qa_and_regenerate(
            client, article_text, verified_ledger_text, model=writer_model,
            reasoning_effort=prod_gen.REASONING_EFFORT, out_dir=out_dir)
        overlap_report = overlap_result.get("report") or {}
        lexical_flagged = any(
            overlap_report.get(key, {}).get("before_overlap", {}).get("flagged")
            for key in ("point_one", "point_two")
        ) or overlap_report.get("point_one_vs_point_two", {}).get("flagged") \
            or overlap_report.get("point_two_vs_point_one", {}).get("flagged")

        # Point Value QA(既存Production関数を無変更で再利用)
        value_qa_result = point_planning.run_point_value_qa(
            client, sections["full_story"], sections["point_one_body"], sections["point_two_body"],
            model=writer_model, reasoning_effort=prod_gen.REASONING_EFFORT)
        save_json(f"{out_dir}/audit/point_value_qa.json", value_qa_result)
        value_qa_flagged = value_qa_result["status"] == "NG"

        # Fact Checker(既存Production関数を無変更で再利用)
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

        # Ledger Deviation Check(既存Production関数を無変更で再利用、
        # Local Rewriteは実施しない=上記限界参照)
        ledger_model = routing.require_model(prod_gen._writer_process(label), routing.WRITER_MODEL)
        deviation_result = vfl01.run_deviation_check(
            client, verified_ledger_text, article_text, model=ledger_model, hook_aware=True)
        save_json(f"{out_dir}/ledger_deviation.json", deviation_result["parsed"])
        major_count = len([d for d in deviation_result["parsed"]["deviations"] if d["severity"] == "MAJOR"])
        minor_count = len([d for d in deviation_result["parsed"]["deviations"] if d["severity"] == "MINOR"])

    elapsed = round(time.time() - t0, 2)

    overall_status = "OK" if (not lexical_flagged and not value_qa_flagged
                               and fact_verdict != "FAIL" and major_count == 0) else "NG_REVIEW_REQUIRED"

    metrics = prod_gen.compute_metrics(article_text)
    section_wc = {"point_one": len(sections["point_one_body"].split()),
                  "point_two": len(sections["point_two_body"].split())}

    result = {
        "label": label, "level": level, "status": overall_status,
        "article_text": article_text,
        "word_count": metrics["word_count"], "section_word_counts": section_wc,
        "fact_status": fc_status, "fact_verdict": fact_verdict,
        "ledger_status": deviation_result["parsed"]["overall_status"],
        "ledger_major_count": major_count, "ledger_minor_count": minor_count,
        "lexical_overlap_flagged": lexical_flagged, "value_qa_flagged": value_qa_flagged,
        "main_story_reproduced_exactly": main_story_reproduced_exactly,
        "main_story_source": fixed_main_story["source_path"],
        "elapsed_seconds": elapsed,
        "known_limitations": [
            "no_point_overlap_or_value_qa_retry_single_pass_only",
            "no_local_rewrite_ledger_major_causes_ng_review_required",
            "no_directional_fact_precheck",
            "stage3_evidence_compression_not_applied",
        ],
    }
    save_json(f"{out_dir}/run_summary.json", {k: v for k, v in result.items() if k != "article_text"})
    print(f"[{THEME_ID}][{level}] status={overall_status} fact_verdict={fact_verdict} "
          f"ledger_status={result['ledger_status']} lexical_flagged={lexical_flagged} "
          f"value_qa_flagged={value_qa_flagged} elapsed={elapsed}s")
    return result


# ============================================================
# 費用実測(既存Trial[revalidation_01/towels_11/wake_12]と同一ロジック、
# read-onlyで転記して再利用)。
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
            by_provider[rec.get("provider")] = by_provider.get(rec.get("provider"), 0.0) + cost
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

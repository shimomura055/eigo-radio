# ============================================================
# er008_n7_pilot_run_01.py
# ER-008-N7-SHARED-POINT-BLUEPRINT-3LEVEL-PILOT-01
# ============================================================
# No.7("Assigned Desks Are Back in Some Offices")を対象に、正式Production
# 相当Pipeline(Research -> Evidence Pack/VFL -> Shared Point Blueprint ->
# B1/A2 Writer -> Fact Check/Ledger Deviation -> Support -> TTS/ASR)を
# 実行するPilot専用runner。
#
# 【今回だけの例外】TTS呼び出し方式のみ、Gemini Batch APIではなく同期
# (client.models.generate_content)を明示的に使う(DEV/VALIDATION用、
# タスク仕様「1. 今回のTTS実行モード」)。er006_batch_tts_wiring_01.
# make_batch_tts_call_fnをこのプロセス内でのみ同期版アダプタへ差し替える
# (Production側の各ファイルは一切変更しない、CURRENT_SPECのBatch標準は
# 無変更)。

from __future__ import annotations

import json
import os
import re
import time

import er005_cost_logger as cl

THEME_ID = "pool_n7_assigned_desks"
OUT_DIR = f"er006_output/pool_pilot_01/{THEME_ID}"
TITLE_EN = "Assigned Desks Are Back in Some Offices"
TOPIC_JA = (
    "一部の職場で「固定席(assigned desk)」が戻ってきている。パンデミック後に広まった"
    "hot-desking(固定の机を割り当てず、空いている机を早い者勝ちで使う方式)に対し、"
    "従業員から不満の声が上がっており、Scotiabank・iCapital Network等の企業が、"
    "静かに固定席への回帰を進めている。背景には、固定席のある従業員の方が「職場への"
    "帰属感」や「集中して働けている感覚」が高いという調査結果や、hot-deskingが従業員の"
    "満足度・職場品質の認識を一貫して下げるという複数の研究レビューがある。一方、"
    "企業全体としては机の共有比率(1人1台の割合)は依然として低下傾向にあり、固定席"
    "回帰は一部の企業・部署にとどまる動きである。"
)


def enable_sync_tts_mode():
    """今回のPilotに限り、Batch TTS call_fn factoryを同期版へ差し替える。
    Production側のファイル(er006_batch_tts_wiring_01.py等)は一切変更
    しない(このプロセス内でのモジュール属性差し替えのみ、かつ復元関数
    disable_sync_tts_modeを対で提供する)。"""
    import er006_batch_tts_wiring_01 as batch_wiring
    import er003_b1_p7a_audio as p7a

    def _sync_call_fn_adapter(model_name, voice_name, client=None, output_path=None, **_ignored):
        return p7a.make_tts_call_fn_for_model(model_name, voice_name, client=client)

    if not hasattr(batch_wiring, "_er008_original_make_batch_tts_call_fn"):
        batch_wiring._er008_original_make_batch_tts_call_fn = batch_wiring.make_batch_tts_call_fn
    batch_wiring.make_batch_tts_call_fn = _sync_call_fn_adapter
    print("[ER-008-N7-PILOT] 同期TTSモードへ切替済み(Batch APIは使用しない、DEV/VALIDATION限定)")


def disable_sync_tts_mode():
    import er006_batch_tts_wiring_01 as batch_wiring
    if hasattr(batch_wiring, "_er008_original_make_batch_tts_call_fn"):
        batch_wiring.make_batch_tts_call_fn = batch_wiring._er008_original_make_batch_tts_call_fn
        print("[ER-008-N7-PILOT] Batch TTSモードへ復元済み")


# ============================================================
# Stage 1: Research(Evidence Pack -> VFL -> Verification)
# ============================================================
def run_research_stage() -> dict:
    import er006_pool_pilot_01_research as research_mod
    import er006_pool_pilot_01_ledger as ledger_mod

    sources = json.load(open(f"{OUT_DIR}/research/raw_sources.json", encoding="utf-8"))["sources"]
    t0 = time.time()
    result = research_mod.run_research_for_theme(THEME_ID, f"{OUT_DIR}/research", TITLE_EN, sources)
    ledger_text = ledger_mod.build_ledger_text_from_vfl(
        result["vfl"]["parsed"], result["evidence_pack"]["parsed"], TITLE_EN)
    ledger_path = f"{OUT_DIR}/research/verified_fact_ledger.txt"
    with open(ledger_path, "w", encoding="utf-8") as f:
        f.write(ledger_text)
    elapsed = round(time.time() - t0, 1)
    print(f"[{THEME_ID}] Research+Ledger完了。elapsed={elapsed}s ledger_path={ledger_path}")
    return {"ledger_path": ledger_path, "elapsed": elapsed, "research_result": result}


# ============================================================
# Stage 2: Shared Point Blueprint(実LLM初回生成)
# ============================================================
def run_blueprint_stage() -> dict:
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er006_model_routing_contract_01 as routing
    import er008_shared_point_blueprint_01 as blueprint_mod
    import er008_point_blueprint_validator_01 as validator_mod

    ledger_path = f"{OUT_DIR}/research/verified_fact_ledger.txt"
    verified_ledger_text = open(ledger_path, encoding="utf-8").read()
    client = vfl01.get_client()

    t0 = time.time()
    with cl.logging_context(THEME_ID, "shared_point_blueprint"):
        model = routing.require_model("SHARED_POINT_BLUEPRINT", routing.WRITER_MODEL)
        result = blueprint_mod.run_blueprint_generation(client, TOPIC_JA, verified_ledger_text, model=model)
    elapsed = round(time.time() - t0, 1)

    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    with open(f"{OUT_DIR}/audit/shared_point_blueprint_raw.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

    parsed = dict(result["parsed"])
    parsed["topic_id"] = THEME_ID
    blueprint = blueprint_mod.blueprint_from_dict(parsed)
    with open(f"{OUT_DIR}/shared_point_blueprint.json", "w", encoding="utf-8") as f:
        json.dump(blueprint_mod.blueprint_to_dict(blueprint), f, ensure_ascii=False, indent=2)

    schema_result = validator_mod.validate_blueprint_schema(blueprint)
    with open(f"{OUT_DIR}/audit/shared_point_blueprint_schema_validation.json", "w", encoding="utf-8") as f:
        json.dump({"ok": schema_result.ok,
                    "violations": [v.__dict__ for v in schema_result.violations]}, f, ensure_ascii=False, indent=2)

    print(f"[{THEME_ID}] Blueprint生成完了。elapsed={elapsed}s schema_ok={schema_result.ok} "
          f"input_tokens={result['input_tokens']} output_tokens={result['output_tokens']}")
    if not schema_result.ok:
        for v in schema_result.violations:
            print(f"  [SCHEMA FAIL] {v.check}: {v.message}")
    return {"blueprint": blueprint, "schema_result": schema_result, "elapsed": elapsed,
            "input_tokens": result["input_tokens"], "output_tokens": result["output_tokens"],
            "model": result["model"]}


# ============================================================
# Stage 3: A2/B1 Writer(Shared Point Blueprintを共通入力として渡す)
# ============================================================
def load_blueprint():
    import er008_shared_point_blueprint_01 as blueprint_mod
    parsed = json.load(open(f"{OUT_DIR}/shared_point_blueprint.json", encoding="utf-8"))
    return blueprint_mod.blueprint_from_dict(parsed)


def run_writer_stage() -> dict:
    import er003_v1_en_direct_ab_01_generate as ab01
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er006_pool_pilot_01_writer as writer_mod

    blueprint = load_blueprint()
    client = vfl01.get_client()
    master_full_text = ab01.load_master_full_text()
    ledger_path = f"{OUT_DIR}/research/verified_fact_ledger.txt"

    t0 = time.time()
    result = writer_mod.run_writer_for_theme(
        client, master_full_text, THEME_ID, TOPIC_JA, ledger_path, OUT_DIR, blueprint=blueprint)
    elapsed = round(time.time() - t0, 1)
    print(f"[{THEME_ID}] Writer完了。elapsed={elapsed}s")
    for label, r in result["results"].items():
        print(f"  {label}: status={r.get('status')} fact_verdict={r.get('fact_verdict')} "
              f"ledger_status={r.get('ledger_status')} fact_usage_report={r.get('fact_usage_report')}")
    return result


# ============================================================
# Stage 4: Structural Validator(A2/B1のfact利用申告をBlueprintと突き合わせる)
# ============================================================
def run_structural_validation_stage() -> dict:
    import er008_point_blueprint_validator_01 as validator_mod

    blueprint = load_blueprint()
    a2_usage = json.load(open(f"{OUT_DIR}/a2/audit/fact_usage_report.json", encoding="utf-8"))
    b1_usage = json.load(open(f"{OUT_DIR}/b1b/audit/fact_usage_report.json", encoding="utf-8"))

    result = validator_mod.validate_topic(blueprint, a2_writer_usage=a2_usage, b1_writer_usage=b1_usage)
    print(f"[{THEME_ID}] Structural Validation(Writer段階): ok={result.ok}")
    for v in result.violations:
        print(f"  [FAIL] {v.check}: {v.message}")
    with open(f"{OUT_DIR}/audit/structural_validation_writer_stage.json", "w", encoding="utf-8") as f:
        json.dump({"ok": result.ok, "violations": [v.__dict__ for v in result.violations]},
                    f, ensure_ascii=False, indent=2)
    return result


# ============================================================
# Stage 5: Support(Preview/Comment1-4)。B1のComment3/4はBlueprintの
# comment_anchorを使う(er003_v1_n3_01_scaffold_generate.run_b1_scaffold
# のblueprint引数経由)。
# ============================================================
def run_support_stage() -> dict:
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er006_pool_pilot_01_support as support_mod

    blueprint = load_blueprint()
    client = vfl01.get_client()
    ledger_text = open(f"{OUT_DIR}/research/verified_fact_ledger.txt", encoding="utf-8").read()

    t0 = time.time()
    result = support_mod.run_support_for_theme(client, THEME_ID, OUT_DIR, ledger_text, blueprint=blueprint)
    elapsed = round(time.time() - t0, 1)
    print(f"[{THEME_ID}] Support完了。elapsed={elapsed}s")
    return result


def run_structural_validation_comments_stage() -> dict:
    import er008_point_blueprint_validator_01 as validator_mod

    blueprint = load_blueprint()
    b1_dir = f"{OUT_DIR}/b1b"
    b1_gen = json.load(open(f"{b1_dir}/audit/b1_support_generation.json", encoding="utf-8"))
    c3_refs = (b1_gen.get("comment_3") or {}).get("referenced_fact_ids")
    c4_refs = (b1_gen.get("comment_4") or {}).get("referenced_fact_ids")
    print(f"[{THEME_ID}] Comment 3 referenced_fact_ids={c3_refs}")
    print(f"[{THEME_ID}] Comment 4 referenced_fact_ids={c4_refs}")

    result = validator_mod.check_comment_fact_reference(blueprint, "point_1", c3_refs or [])
    result2 = validator_mod.check_comment_fact_reference(blueprint, "point_2", c4_refs or [])
    ok = result.ok and result2.ok
    print(f"[{THEME_ID}] Structural Validation(Comment段階): ok={ok}")
    for v in result.violations + result2.violations:
        print(f"  [FAIL] {v.check}: {v.message}")
    with open(f"{OUT_DIR}/audit/structural_validation_comment_stage.json", "w", encoding="utf-8") as f:
        json.dump({"ok": ok, "comment_3_refs": c3_refs, "comment_4_refs": c4_refs,
                    "violations": [v.__dict__ for v in (result.violations + result2.violations)]},
                    f, ensure_ascii=False, indent=2)
    return {"ok": ok}


JAPANESE_TITLE_JA = "一部の職場で「固定席」が戻ってきている"


# ============================================================
# Stage 6.5: A2 Full Story Part1/2の長さ補正(ER-008-N7-MIDDLE-SPEC-
# STORY-BALANCE-KEYPHRASE-AUDIT-01 Part B)。No.4-7 Audit結果、A2の
# Full Story総語数はNo.4=224語・No.5=300語・No.6=212語に対しNo.7=102語
# (Part1=38語)と明確な外れ値だった。Evidence detailを増やすのではなく、
# 状況説明・narrative transition・listener orientationで自然に補う
# (Evidence Compression方針は維持、新しいFactは追加しない)。
# ============================================================
A2_STORY_EXPANSION_DEVELOPER_MESSAGE = (
    "あなたはeigo-radioのA2記事Editorです。既存のA2記事のFull Story"
    "Part 1・Part 2だけを、より自然な分量へ書き直します。新しいFactの"
    "追加は禁止です。"
)

A2_STORY_EXPANSION_PROMPT_TEMPLATE = """【現在のA2記事全文(参考、書き換えるのはPart 1・Part 2のみ)】
{article_text}

【Verified Fact Ledger(これ以外のFactを追加しないこと)】
{verified_ledger_text}

【問題】
上記記事のFull Story Part 1が38語、Part 2が64語と、他の同種トピック
(通常Part 1・Part 2それぞれ100語前後、合計200語前後)と比べて明確に
短すぎます。特にPart 1が短いため、日本語のPreview・Comment 1の存在感に
対して英語本文が薄く感じられます。

【あなたのタスク】
Full Story Part 1・Part 2を書き直してください。目安として、Part 1は
80〜110語程度、Part 2は80〜110語程度(合計160〜220語程度)を目指して
ください(厳密な制約ではありません、自然さを優先してください)。

【重要な制約】
- 新しいFact(数字・固有名詞・調査結果等)をVerified Fact Ledgerの範囲
  外から追加しないでください
- 分量を増やす手段は、状況説明・具体的な情景描写・自然な話の展開
  (narrative transition)・聞き手が話についていくための文脈提示に
  限定してください。Evidence detailを水増しする(数字を繰り返す、
  Ledgerの詳細を無理に増やす)のは禁止です
- Title・Point One・Point Two・In One Lineの内容とは重複させないで
  ください(Point One/TwoはFull Storyの後に別の切り口を提示する構成の
  ため、Full Story側でPointの内容を先取りしないこと)
- A2として平易な語彙・文構造を維持してください(既存のA2記事の難易度を
  保つ)
- Part 1とPart 2の意味の区切りは、現在のPart 1/Part 2の境界(パンデ
  ミック後の状況説明がPart 1、一部企業が方針転換している具体的な動きが
  Part 2)を維持してください

【出力形式】
以下の形式のJSONのみを出力してください。
{{"full_story_part1": "...", "full_story_part2": "..."}}"""


def run_a2_story_expansion_stage() -> dict:
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er006_model_routing_contract_01 as routing
    import er003_v1_n3_01_scaffold_generate as sc

    article_text = open(f"{OUT_DIR}/a2/article.md", encoding="utf-8").read()
    ledger_text = open(f"{OUT_DIR}/research/verified_fact_ledger.txt", encoding="utf-8").read()
    client = vfl01.get_client()
    prompt = A2_STORY_EXPANSION_PROMPT_TEMPLATE.format(article_text=article_text, verified_ledger_text=ledger_text)

    t0 = time.time()
    with cl.logging_context(THEME_ID, "a2_story_expansion"):
        response = client.responses.create(
            model=routing.require_model("A2_WRITER", routing.WRITER_MODEL),
            reasoning={"effort": "medium"},
            text={"format": {"type": "json_schema", "name": "a2_story_expansion", "schema": {
                "type": "object",
                "properties": {"full_story_part1": {"type": "string"}, "full_story_part2": {"type": "string"}},
                "required": ["full_story_part1", "full_story_part2"], "additionalProperties": False,
            }, "strict": True}},
            input=[{"role": "developer", "content": A2_STORY_EXPANSION_DEVELOPER_MESSAGE},
                   {"role": "user", "content": prompt}],
        )
    elapsed = round(time.time() - t0, 1)
    revised = json.loads(response.output_text)
    print(f"[{THEME_ID}] A2 Story expansion完了。elapsed={elapsed}s "
          f"input_tokens={response.usage.input_tokens} output_tokens={response.usage.output_tokens}")

    os.makedirs(f"{OUT_DIR}/a2/audit", exist_ok=True)
    with open(f"{OUT_DIR}/a2/audit/story_expansion_raw.json", "w", encoding="utf-8") as f:
        json.dump({"prompt": prompt, "raw_text": response.output_text, "parsed": revised,
                    "model": response.model, "response_id": response.id,
                    "input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens},
                   f, ensure_ascii=False, indent=2)

    # article.md内のMain Story部分(Title直後から最初の###見出しの直前
    # まで)をまるごと置き換える(split_article_text()内部の抽出ロジックと
    # 同じ境界を使うことで、bold記号除去等による文字列不一致を避ける)。
    parts = sc.split_article_text(article_text)  # 事前に構造(見出し2つ等)が正しいことを確認
    title_match = sc.re.match(r"^#\s+(.+?)\s*\n", article_text)
    h3_matches = list(sc.re.finditer(r"^###\s+(.+?)\s*$", article_text, flags=sc.re.MULTILINE))
    intro_start = title_match.end() if title_match else 0
    intro_end = h3_matches[0].start()
    old_intro_text = article_text[intro_start:intro_end]
    new_intro_text = f"\n{revised['full_story_part1'].strip()}\n\n{revised['full_story_part2'].strip()}\n\n"
    new_article_text = article_text[:intro_start] + new_intro_text + article_text[intro_end:]
    old_part1, old_part2 = parts["part1"], parts["part2"]

    with open(f"{OUT_DIR}/a2/article.md", "w", encoding="utf-8") as f:
        f.write(new_article_text)
    new_parts = sc.split_article_text(new_article_text)
    with open(f"{OUT_DIR}/a2/parts.json", "w", encoding="utf-8") as f:
        json.dump(new_parts, f, ensure_ascii=False, indent=2)

    def wc(t):
        return len(re.findall(r"[A-Za-z][A-Za-z'’-]*", t))
    print(f"  Part1: {wc(old_part1)}words -> {wc(new_parts['part1'])}words")
    print(f"  Part2: {wc(old_part2)}words -> {wc(new_parts['part2'])}words")
    return {"old_part1": old_part1, "old_part2": old_part2, "new_parts": new_parts,
            "input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens,
            "elapsed": elapsed}


A2_STORY_FIX_DEVELOPER_MESSAGE = (
    "あなたはeigo-radioのA2記事Editorです。Deviation Checkが指摘した"
    "問題箇所だけを最小限修正します。分量(語数)はできるだけ維持して"
    "ください。"
)

A2_STORY_FIX_PROMPT_TEMPLATE = """【現在のFull Story Part 1・Part 2】
Part 1: {part1}

Part 2: {part2}

【Verified Fact Ledger】
{verified_ledger_text}

【Deviation Checkが指摘した問題(この箇所だけを修正する)】
{deviation_issues}

【あなたのタスク】
指摘された箇所を、Ledgerの範囲内に収まるよう最小限修正してください。
具体的には:
- 「ホットデスキングが柔軟性を高める」「働く場所の感覚を変える」
  「多くの労働者にとって」というような、Ledgerにない効果・一般化の
  主張を削除するか、状況の描写(効果の主張ではなく、単に机が毎日
  変わりうるという運用上の事実の描写)へ言い換えてください
- 「オフィスの一部は割り当て席、別の一部は空席のまま」「企業ごとに
  異なる方針を選んでいる」という一般化も、Ledgerが示す具体的な2社の
  事例(Scotiabank、iCapital Network)の範囲を超えない表現へ言い換えて
  ください
- それ以外の文はそのまま維持してください(変更は最小限に)
- 分量はPart1・Part2ともおおよそ現在の語数(Part1約100語、Part2約94語)
  を維持してください

【出力形式】
{{"full_story_part1": "...", "full_story_part2": "..."}}"""


def run_a2_story_fix_stage() -> dict:
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er006_model_routing_contract_01 as routing
    import er003_v1_n3_01_scaffold_generate as sc

    parts = json.load(open(f"{OUT_DIR}/a2/parts.json", encoding="utf-8"))
    ledger_text = open(f"{OUT_DIR}/research/verified_fact_ledger.txt", encoding="utf-8").read()
    deviations = json.load(open(f"{OUT_DIR}/a2/audit/story_expansion_deviation_recheck.json", encoding="utf-8"))
    # Part1/2に該当する2件の指摘のみ抜粋する(Point One/Twoの既存指摘は対象外、無変更のまま)
    target_quotes = ("This plan can make the office more flexible",
                      "One part of an office may use assigned desks")
    issues = [d for d in deviations["deviations"] if any(q in d["claim_in_article"] for q in target_quotes)]
    issues_text = "\n".join(f"- {d['issue']} (該当箇所: {d['claim_in_article']})" for d in issues)

    client = vfl01.get_client()
    prompt = A2_STORY_FIX_PROMPT_TEMPLATE.format(
        part1=parts["part1"], part2=parts["part2"], verified_ledger_text=ledger_text, deviation_issues=issues_text)

    with cl.logging_context(THEME_ID, "a2_story_fix"):
        response = vfl01.get_client().responses.create(
            model=routing.require_model("A2_WRITER", routing.WRITER_MODEL),
            reasoning={"effort": "medium"},
            text={"format": {"type": "json_schema", "name": "a2_story_fix", "schema": {
                "type": "object",
                "properties": {"full_story_part1": {"type": "string"}, "full_story_part2": {"type": "string"}},
                "required": ["full_story_part1", "full_story_part2"], "additionalProperties": False,
            }, "strict": True}},
            input=[{"role": "developer", "content": A2_STORY_FIX_DEVELOPER_MESSAGE},
                   {"role": "user", "content": prompt}],
        )
    fixed = json.loads(response.output_text)
    print(f"[{THEME_ID}] A2 Story fix完了。input_tokens={response.usage.input_tokens} "
          f"output_tokens={response.usage.output_tokens}")

    with open(f"{OUT_DIR}/a2/audit/story_fix_raw.json", "w", encoding="utf-8") as f:
        json.dump({"prompt": prompt, "raw_text": response.output_text, "parsed": fixed,
                    "model": response.model, "response_id": response.id}, f, ensure_ascii=False, indent=2)

    article_text = open(f"{OUT_DIR}/a2/article.md", encoding="utf-8").read()
    title_match = re.match(r"^#\s+(.+?)\s*\n", article_text)
    h3_matches = list(re.finditer(r"^###\s+(.+?)\s*$", article_text, flags=re.MULTILINE))
    intro_start = title_match.end() if title_match else 0
    intro_end = h3_matches[0].start()
    new_intro_text = f"\n{fixed['full_story_part1'].strip()}\n\n{fixed['full_story_part2'].strip()}\n\n"
    new_article_text = article_text[:intro_start] + new_intro_text + article_text[intro_end:]
    with open(f"{OUT_DIR}/a2/article.md", "w", encoding="utf-8") as f:
        f.write(new_article_text)
    new_parts = sc.split_article_text(new_article_text)
    with open(f"{OUT_DIR}/a2/parts.json", "w", encoding="utf-8") as f:
        json.dump(new_parts, f, ensure_ascii=False, indent=2)

    def wc(t):
        return len(re.findall(r"[A-Za-z][A-Za-z'’-]*", t))
    print(f"  Part1: {wc(new_parts['part1'])}words  Part2: {wc(new_parts['part2'])}words")
    return {"new_parts": new_parts}


def run_a2_story_deviation_recheck_stage() -> dict:
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er006_model_routing_contract_01 as routing

    article_text = open(f"{OUT_DIR}/a2/article.md", encoding="utf-8").read()
    ledger_text = open(f"{OUT_DIR}/research/verified_fact_ledger.txt", encoding="utf-8").read()
    client = vfl01.get_client()
    with cl.logging_context(THEME_ID, "a2_story_deviation_recheck"):
        result = vfl01.run_deviation_check(client, ledger_text, article_text,
                                            model=routing.require_model("A2_WRITER", routing.WRITER_MODEL))
    print(f"[{THEME_ID}] A2 Story修正後Deviation Recheck: "
          f"overall_status={result['parsed']['overall_status']} deviations={len(result['parsed']['deviations'])}")
    with open(f"{OUT_DIR}/a2/audit/story_expansion_deviation_recheck.json", "w", encoding="utf-8") as f:
        json.dump(result["parsed"], f, ensure_ascii=False, indent=2)
    return result["parsed"]


def run_a2_story_tts_regenerate_stage() -> dict:
    """full_story_part1/2のみを再生成する(既存segmentは変更しない、
    同期TTSモード限定)。"""
    import er003_v1_n3_01_tts_generate as tts_gen
    import er003_v1_crosslevel_audio_02_common as c

    parts = json.load(open(f"{OUT_DIR}/a2/parts.json", encoding="utf-8"))
    narration_dir = f"{OUT_DIR}/a2/narration"
    results = {}
    enable_sync_tts_mode()
    try:
        for name, text in (("full_story_part1", parts["part1"]), ("full_story_part2", parts["part2"])):
            sub = tts_gen.first_words(text)
            print(f"[{THEME_ID}] a2/{name} 再生成開始(同期TTS)...")
            with cl.logging_context(THEME_ID, "a2_story_retts_sync"), cl.segment_context(name):
                results[name] = c.generate_english_segment_with_fallback(
                    tts_gen.tts_safe_news_en(text), f"{narration_dir}/{name}.wav", sub)
            results[name]["canonical_text"] = text
            print(f"  {name}: status={results[name].get('status')}")
    finally:
        disable_sync_tts_mode()

    tts_results = json.load(open(f"{OUT_DIR}/a2/audit/tts_generation_results.json", encoding="utf-8"))
    for name in ("full_story_part1", "full_story_part2"):
        tts_results["segments"][name] = results[name]
    with open(f"{OUT_DIR}/a2/audit/tts_generation_results.json", "w", encoding="utf-8") as f:
        json.dump(tts_results, f, ensure_ascii=False, indent=2, default=str)
    return results


# ============================================================
# Stage 6: TTS(同期モード、DEV/VALIDATION限定) + Assembly(B1/A2)
# ============================================================
def run_audio_stage() -> dict:
    import er003_v1_n3_01_tts_generate as tts_gen
    import er003_v1_n3_01_assemble as asm

    tts_gen.JAPANESE_TITLES.update({THEME_ID: JAPANESE_TITLE_JA})
    theme = {"theme_id": THEME_ID, "out_dir": OUT_DIR}
    timing = {}

    enable_sync_tts_mode()
    try:
        t0 = time.time()
        with cl.logging_context(THEME_ID, "tts_b1_sync"):
            b1_tts_summary = tts_gen.generate_b1_segments(theme)
        timing["tts_b1_sync"] = round(time.time() - t0, 2)

        t1 = time.time()
        with cl.logging_context(THEME_ID, "tts_a2_sync"):
            a2_tts_summary = tts_gen.generate_a2_segments(theme)
        timing["tts_a2_sync"] = round(time.time() - t1, 2)
    finally:
        disable_sync_tts_mode()

    t2 = time.time()
    with cl.logging_context(THEME_ID, "assemble_b1"):
        b1_assemble_summary = asm.stage_assemble_b1(theme)
    timing["assemble_b1"] = round(time.time() - t2, 2)

    t3 = time.time()
    with cl.logging_context(THEME_ID, "assemble_a2"):
        a2_assemble_summary = asm.stage_assemble_a2(theme)
    timing["assemble_a2"] = round(time.time() - t3, 2)

    with open(f"{OUT_DIR}/audio_timing_sync.json", "w", encoding="utf-8") as f:
        json.dump(timing, f, ensure_ascii=False, indent=2)
    print(f"[{THEME_ID}] Audio完了(同期TTS)。timing={timing}")
    print(f"  B1 TTS: {b1_tts_summary['segment_status']}")
    print(f"  A2 TTS: {a2_tts_summary['segment_status']}")
    print(f"  B1 Assemble: {b1_assemble_summary}")
    print(f"  A2 Assemble: {a2_assemble_summary}")
    return {"b1_tts": b1_tts_summary, "a2_tts": a2_tts_summary,
            "b1_assemble": b1_assemble_summary, "a2_assemble": a2_assemble_summary, "timing": timing}


# ============================================================
# Stage 7: Middle/Bridge組み立て(ER-008-N7-MIDDLE-SPEC-STORY-BALANCE-
# KEYPHRASE-AUDIT-01 Part Aで再定義: Middleは「基本B1、英語ニュース
# 本文系[Full Story Part1/2・Point One/Two・In One Line]のみA2」)。
# B1のtimeline構造(build_b1_timeline、既存pause値)・shell segment
# (Welcome/Topic intro/Preview/Preview intro/Key phrases intro/Key
# Phrase[B1側の英語phrase+日本語gloss]/Comment1-4/Outro)をそのまま
# 全て使い、"b1_segments"辞書の7箇所(full_story_part1/2・point_one/two・
# point_one/two_heading・in_one_line)だけをA2の同期TTS済み音声へ差し
# 替える。新規TTS無し。Japanese titleはMiddleでは使わない(Middleで
# 日本語が出るのはKey Phrase日本語glossのみ)。Production側の
# er003_v1_n3_01_assemble.py自体は変更しない(Pilot専用関数)。
# ============================================================
MIDDLE_STORY_SEGMENT_NAMES = ("full_story_part1", "full_story_part2",
                               "point_one_heading", "point_one", "point_two_heading", "point_two",
                               "in_one_line")


def build_middle_timeline_and_assemble(theme: dict) -> dict:
    import er002_common as common
    import er003_b1_p9a_audio as p9a
    import er003_v1_n3_01_assemble as asm

    out_dir_mid = f"{theme['out_dir']}/middle"
    os.makedirs(f"{out_dir_mid}/assembled", exist_ok=True)
    os.makedirs(f"{out_dir_mid}/audit", exist_ok=True)

    b1_sources = asm.load_b1_sources(theme)
    b1_parts = asm.apply_b1_gain(b1_sources)  # Middleは「基本B1」なので、B1の既存gain値をそのまま土台にする
    a2_sources = asm.load_a2_sources(theme)   # A2のraw(gain前)音源からStory系7箇所だけを使う

    target_rms = b1_parts["gain_report"]["target_rms"]
    for name in MIDDLE_STORY_SEGMENT_NAMES:
        mono = a2_sources["a2_segments"][name]
        gain = p9a.compute_gain_for_target_rms(mono, target_rms)
        # B1の既存b1_parts["b1_segments"]を、A2音声(B1のtarget_rmsへ
        # 合わせ直したもの)で上書きする。それ以外のkey(preview・
        # comment_1-4)はB1の値のまま変更しない。
        b1_parts["b1_segments"][name] = p9a.mono_24k_to_stereo_target(mono * gain)

    seq = asm.build_b1_timeline(b1_parts)  # B1のtimeline構造・pause値をそのまま使う(Part C修正も反映)
    # Japanese titleはB1のtimelineに元々存在しないため、追加の除去処理は不要。

    result = asm.assemble_with_timeline(seq)
    assembled = result["assembled"]
    out_path = f"{out_dir_mid}/assembled/English_Your_Way_MIDDLE_{THEME_ID.upper()}.wav"
    common.write_wav_float(out_path, assembled, asm.SR, 2)
    metrics = common.measure_metrics(assembled[:, 0], asm.SR)

    with open(f"{out_dir_mid}/audit/timeline.json", "w", encoding="utf-8") as f:
        json.dump(result["timeline"], f, ensure_ascii=False, indent=2)

    summary = {
        "status": "OK", "out_path": out_path, "duration_seconds": result["total_duration_seconds"],
        "clipping_detected": metrics["clipping_detected"], "peak": round(p9a.peak(assembled), 5),
        "sample_rate": asm.SR, "channels": 2, "new_tts_calls": 0, "new_asr_calls": 0,
        "a2_sourced_segments": list(MIDDLE_STORY_SEGMENT_NAMES),
        "b1_sourced_segments": ["intro", "welcome", "topic_intro", "notification", "preview_intro",
                                  "preview", "key_phrases_intro", "key_phrase_1-5(en+ja)", "full_story_intro",
                                  "comment_1", "comment_2", "comment_3", "point_notification",
                                  "comment_4", "outro"],
    }
    with open(f"{out_dir_mid}/run_summary_assemble.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(f"[N7-MIDDLE-ASSEMBLE] status={summary['status']} duration={summary['duration_seconds']} "
          f"peak={summary['peak']} clipping={summary['clipping_detected']} out_path={out_path}")
    return summary


if __name__ == "__main__":
    import sys
    stage = sys.argv[1] if len(sys.argv) > 1 else "research"
    if stage == "research":
        run_research_stage()
    elif stage == "blueprint":
        run_blueprint_stage()
    elif stage == "writer":
        run_writer_stage()
    elif stage == "validate_writer":
        run_structural_validation_stage()
    elif stage == "support":
        run_support_stage()
    elif stage == "validate_comments":
        run_structural_validation_comments_stage()
    elif stage == "audio":
        run_audio_stage()
    elif stage == "middle":
        theme = {"theme_id": THEME_ID, "out_dir": OUT_DIR}
        build_middle_timeline_and_assemble(theme)
    elif stage == "story_expand":
        run_a2_story_expansion_stage()
    elif stage == "story_fix":
        run_a2_story_fix_stage()
    elif stage == "story_deviation_recheck":
        run_a2_story_deviation_recheck_stage()
    elif stage == "story_retts":
        run_a2_story_tts_regenerate_stage()
    else:
        print(f"unknown stage: {stage}")

# ============================================================
# er011_point_role_planning_focus_connection_trial_03.py
# FAMILY-A-POINT-ROLE-PLANNING-FOCUS-MODULE-CONNECTION-TRIAL-03 (Lane A)
# ============================================================
# 目的(ユーザー決定 2026-09-09、A-UDR-11承認): FAMILY-A-DAILY-NEWS-FOCUS-
# LAYER-COMPARISON-TRIAL-02_REPORT.mdで判明した「editorial_type_module_
# blockがPoint Role Planning(er003_v1_n3_01_articles_generate.run_one_
# pattern内)へ届いておらず、Focus ModuleがPoint役割設計へ直接作用しない」
# 問題を解消できる接続設計を検証する。**Trial(Production実装ではない)**。
# Production/Prompt/SSOT編集・Git操作は一切行わない。monkeypatch・
# グローバル書き換えは行わない。
#
# ------------------------------------------------------------
# 0. 経路の途切れ箇所(呼び出しチェーン、Gate 4根拠)
# ------------------------------------------------------------
# run_writer_for_theme(er006_pool_pilot_01_writer.py 28-111行)
#   -> gen.resolve_editorial_type_module_block(editorial_mode)
#        editorial_type_module_block(以下EB)を解決する
#   -> gen.build_common_block(..., editorial_type_module_block=EB)
#        EBをCOMMON_BLOCK_TEMPLATE内の{editorial_type_module_block}
#        placeholder(【Spoken-first原則】直前)へ挿入する
#   -> gen.build_prompt(common_block, instruction) -> prompt (EBを含む)
#   -> gen.run_one_pattern(client, theme_id, label, prompt, ...)
#        (注意: run_one_patternのシグネチャにEBを渡す引数は存在しない。
#        promptという「もう焼き込まれた文字列」としてのみEBは渡る)
#        -> point_planning.run_point_role_planning(client, topic,
#           verified_ledger_text, model, reasoning_effort)
#             **ここが途切れ箇所**。この関数はtopicとverified_ledger_
#             textしか受け取らず、EBを一切参照しない
#             (er011_point_role_value_planning_01.py 124-145行、
#             ROLE_PLANNING_PROMPT_TEMPLATE 72-117行にEB用の
#             placeholderが存在しない)
#        -> point_planning.build_role_planning_block(role_plan_result)
#             role_plan_result(role/evidence_anchor等)をテキスト化し、
#             promptの後ろに追記する (prompt_with_plan)
#        -> gen._generate_and_compress_article(..., prompt_with_plan, ...)
#             実際のWriter LLM呼び出し。ここでは既にEBを含むprompt本体と、
#             EBを全く知らない状態で計画されたrole_planning_blockの両方が
#             混在した状態で入力される。
#
# 結論: EB自体は最終的なWriter本文生成promptには届いている(promptに
# 焼き込み済み)が、Point One/Twoの「役割(role)」を計画する専用LLM呼び出し
# (Point Role Planning)は、EBの内容を一切知らないまま独立に役割を決めて
# しまう。その後に生成されるrole_planning_block(build_role_planning_block
# の出力)が「この設計に厳密に従ってください」という強い指示としてWriterへ
# 追記されるため、EBが要求する役割の優先順位(例: major_daily_newsの
# mechanism / beyond-the-headline factor / limitation)がPoint Role
# Planningの決定に反映されず、Focus ModuleがPoint役割設計へ直接作用しない。
#
# Diagnostic Full Retry(run_one_pattern内、Point Overlap/Value QA NG時、
# 最大POINT_OVERLAP_ARTICLE_RETRY_MAX=2回)は、Point Role Planningを
# 「記事全体と同じ生成単位」として毎回再実行する(924-925行付近、前回の
# 計画を使い回さない)ため、この経路も同じ接続が必要。Local Rewrite Loop
# (1032-1183行付近)はLedger Deviation MAJOR検出時の局所文修正のみで、
# Point Role Planningを再実行しない(記事全体を再生成しないため対象外、
# 接続不要)。Human Review再生成(Reviewキュー経由で記事を最初から生成し
# 直す運用)は、内部的にはrun_one_patternを最初から再度呼ぶだけであり、
# 既存のPoint Role Planning呼び出し経路(初回)がそのまま再実行されるため、
# 初回経路の接続修正が適用されればHuman Review再生成にも自動的に及ぶ
# (独立した別経路は存在しない)。
#
# ------------------------------------------------------------
# 1. 設計案(詳細比較はレポート本体・末尾DESIGN_COMPARISON参照)
# ------------------------------------------------------------
# 単一の接続メカニズム(Point Role Planningのpromptへ、新規optional引数
# point_role_hint_blockとして任意テキストブロックを挿入し、既定""では
# 既存promptとバイト単位で完全同一)を実装し、そこへ渡す内容を変えることで
# 案(a)/(b)/(c)を再現する:
#   (a) 案A(Focus Module直接注入): point_role_hint_block =
#       editorial_type_module_block(build_common_blockへ渡すのと全く
#       同一のテキスト)をそのまま渡す
#   (b) 案B(Mode別Point Role候補リスト、推奨): point_role_hint_blockへ、
#       Focus Moduleより短い、Point Role Planning専用の候補リスト
#       (MAJOR_DAILY_NEWS_POINT_ROLE_HINT_BLOCK、Trial-02の
#       MAJOR_DAILY_NEWS_FOCUS_MODULE_BLOCK本文が言及するmechanism/
#       beyond-the-headline factor/limitationをそのまま転記した短い
#       テキスト)を渡す
#   (c) 案C(併用): (a)+(b)を連結して渡す
# 引数名・挿入位置・デフォルト挙動はいずれも共通(下記run_point_role_
# planning_connected参照)。本Trialは(b)を推奨案として選び、runtime検証は
# (b)のみ実施する(理由はレポート本体参照、費用上限考慮)。
#
# ------------------------------------------------------------
# 2. Production関数の再利用/コピーの内訳(Gate 4)
# ------------------------------------------------------------
# 【再利用(import・無変更)】
#   - er003_v1_n3_01_articles_generate(prod_genとしてimport): 全ての
#     内部helper関数(_generate_and_compress_article, compute_metrics,
#     run_point_overlap_qa_and_regenerate, split_common_sections_for_
#     point_qa, build_diagnostic_retry_prompt, normalize_article_
#     formatting, _writer_process等)とモジュール定数(REASONING_EFFORT,
#     POINT_OVERLAP_ARTICLE_RETRY_MAX, POINT_TARGET_*, POINT_TOLERANCE_*,
#     TOTAL_SOFT_*)は、prod_gen.NAMEの形でそのまま呼び出す(コピーしない、
#     内容の変更なし)。build_common_block/build_prompt/resolve_editorial_
#     type_module_block/EDITORIAL_TYPE_MODULE_BLOCKSも無変更のまま
#     import・呼び出しのみ。
#   - er011_point_role_value_planning_01(point_planningとしてimport):
#     build_role_planning_block/run_point_value_qa/build_value_qa_
#     diagnostic_note/ROLE_PLANNING_JSON_SCHEMA/ROLE_PLANNING_DEVELOPER_
#     MESSAGE/RolePlanningModelMismatchErrorは無変更のままpoint_planning.
#     NAMEで呼び出す。
#   - 他の全依存モジュール(r3, vfl01, sf1r1, routing, dfp, local_rewrite)
#     もimportのみ、無変更。
#   - er011_daily_news_focus_layer_comparison_trial_02(既存Trialスクリプト、
#     Lane A-1、A-UDR-8で既にVALIDATED済み): MAJOR_DAILY_NEWS_FOCUS_
#     MODULE_BLOCKの文言をそのままimportして再利用する(再入力による転記
#     ミスを避けるため、内容は無改変)。
#
# 【コピー・改変(Trial限定、理由: 呼び出しチェーンの中間に新しい引数を
#  通す接続点が必要で、Production関数のシグネチャ自体を変更せずには
#  実現できないため)】
#   - run_one_pattern_connected: er003_v1_n3_01_articles_generate.py
#     run_one_pattern()(809-1214行、406行)のコピー。変更点は (i) 関数名
#     run_one_pattern -> run_one_pattern_connected、(ii) 新規引数
#     point_role_hint_block: str = "" の追加、(iii) 2箇所のpoint_planning.
#     run_point_role_planning(...)呼び出しをrun_point_role_planning_
#     connected(..., point_role_hint_block=point_role_hint_block)へ置換
#     (833-834行、924-925行相当)、(iv) 元は同一module内のbare参照だった
#     ヘルパー関数・定数をprod_gen.NAMEへ明示的に修飾。ロジック・分岐・
#     文言・print文・出力ファイル名・retry上限は一切変更していない。
#   - run_point_role_planning_connected / ROLE_PLANNING_PROMPT_TEMPLATE_
#     CONNECTED: er011_point_role_value_planning_01.py run_point_role_
#     planning()(124-145行)+ROLE_PLANNING_PROMPT_TEMPLATE(72-117行)の
#     コピー。変更点は、テンプレートの「【Verified Fact Ledger】
#     {verified_ledger_text}」と「Point One・Point Twoそれぞれについて」
#     の間に新規{point_role_hint_block}placeholderを追加し、関数へ
#     point_role_hint_block: str = "" 引数を追加しただけ。schema/
#     developer message/JSON parse/model一致チェックは無変更
#     (point_planning.ROLE_PLANNING_JSON_SCHEMA/ROLE_PLANNING_DEVELOPER_
#     MESSAGE/RolePlanningModelMismatchErrorをそのまま再利用)。
#
# monkeypatch・グローバル書き換えは一切行っていない(既存モジュールの
# 属性を書き換えるコードは本ファイルに存在しない)。
# ============================================================
from __future__ import annotations

import json
import os
import time

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as prod_gen
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er008_directional_fact_precheck_08 as dfp
import er003_v1_spoken_first_01_r1_generate as sf1r1
import er010_ledger_local_rewrite_09 as local_rewrite
import er011_point_role_value_planning_01 as point_planning
from er011_daily_news_focus_layer_comparison_trial_02 import MAJOR_DAILY_NEWS_FOCUS_MODULE_BLOCK

HANSHIN_LEDGER_PATH = "er003_output/n3_01/hanshin/research/verified_fact_ledger.txt"
HANSHIN_TOPIC_JA = (
    "2026年8月16日、マツダスタジアムで行われた広島東洋カープ対阪神タイガース戦。"
    "阪神は初回の佐藤輝明の2ランホームランで先制し、先発伊原陵人が5回2安打1失点と"
    "試合を作り、7回・8回にも加点して8-1で完勝した。広島の得点は5回のモンテロの"
    "ソロホームラン1点のみだった。"
)
THEME_ID = "point_role_planning_focus_connection_trial_03"
OUT_DIR = f"er011_output/{THEME_ID}"


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


# ============================================================
# 案(b): Major/Daily News固有のPoint Role候補リスト(推奨案)。
# Trial-02のMAJOR_DAILY_NEWS_FOCUS_MODULE_BLOCK本文(上記でimportした
# ものと同一文面、124-127行相当: "the mechanism that decided the outcome,
# why this matters, who is affected, an additional contributing factor
# beyond the headline fact, or what remains unconfirmed")が既に言及して
# いる役割候補を、Point Role Planning専用の短い候補リストとしてそのまま
# 転記しただけで、新しい語彙・新しい仕様を創作していない。Production未
# 採用・未実装、Focus Module最終文言は本Trial検証後に確定するというユーザー
# 決定に基づき、ここでも確定させない(Trialの検証用ドラフト)。
# ============================================================
MAJOR_DAILY_NEWS_POINT_ROLE_HINT_BLOCK = """This is a Major/Daily News article (single, dateable event). When planning \
Point One and Point Two, prefer roles the Ledger actually supports from among: the mechanism that decided the outcome, \
an additional contributing factor beyond the headline fact, or a limitation / what remains unconfirmed. Do not force \
a role the Ledger does not support, and do not let either Point simply restate a fact already given in Main Story."""


# ============================================================
# Trend Synthesis比較用: Trial内では既存Production挙動を変えない(不変
# 維持)ことを示すため、point_role_hint_block=""(空)をTrend Synthesis
# 条件へ用いる。新しいhint文言は作成しない(A-UDR-11付随決定)。
# ============================================================
TREND_SYNTHESIS_POINT_ROLE_HINT_BLOCK = ""


# ============================================================
# Point Role Planning接続版 (er011_point_role_value_planning_01.py
# ROLE_PLANNING_PROMPT_TEMPLATE 72-117行のコピー。挿入箇所のみ変更、
# 他は一切変更していない)
# ============================================================
ROLE_PLANNING_PROMPT_TEMPLATE_CONNECTED = """これから、以下のVerified Fact Ledgerに基づいて、英語ニュースpodcast記事の
Point One・Point Twoを書きます。本文を書く前に、まず両方の設計を計画して
ください。

【今回のテーマ】
{topic}

【Verified Fact Ledger】
{verified_ledger_text}

{point_role_hint_block}Point One・Point Twoそれぞれについて、以下を具体的に(このLedger固有の
内容で、どんな記事にも当てはまるテンプレート的な一般論にならないように)
決めてください:

- role: このPointが記事の中で担う具体的な役割(例: 意外な詳細、方法論上の
  ニュアンス、歴史的な対比、心理的な理由。固定テンプレートではなく、この
  Ledgerに合わせて決めること)
- new_listener_takeaway: 聞き手がこのPointを聞いて新しく持ち帰る、具体的な
  理解・示唆・視点(Full Storyを聞いただけでは得られないもの)
- evidence_anchor: このPointの内容が、Verified Fact Ledgerのどの事実・
  データに基づくか
- why_it_matters: このPointが「だから何なのか」に対して与える具体的な答え
  (単なる一般的な留保・免責事項ではなく、聞き手にとっての意味)
- must_not_overlap_with_full_story: Full Storyで既に説明される意味のうち、
  このPointで繰り返してはいけない具体的な内容
- must_not_overlap_with_other_point: もう一方のPointが担う内容のうち、
  このPointで重複させてはいけない具体的な内容

【禁止(重要)】
以下のようなPointは、たとえPoint OneとPoint Twoの文字列が違っていても
価値が無いとみなされます。計画段階でこれらを避けてください:
- 研究上の限界・一般化上の注意・免責事項だけで構成されるPoint
- Full Storyの要約・言い換えに留まるPoint
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


def run_point_role_planning_connected(client, topic: str, verified_ledger_text: str, model: str,
                                       reasoning_effort: str, point_role_hint_block: str = "") -> dict:
    """er011_point_role_value_planning_01.run_point_role_planning(124-145行)
    のコピー+改変。point_role_hint_block(既定"")が空の場合、生成される
    promptはproduction版ROLE_PLANNING_PROMPT_TEMPLATE.format(...)とバイト
    単位で完全同一になる(下記単体テストで確認)。JSON schema/developer
    message/model一致チェック/例外クラスはpoint_planningモジュールの
    ものをそのまま再利用し、コピーしていない。"""
    hint_section = f"{point_role_hint_block}\n\n" if point_role_hint_block else ""
    prompt = ROLE_PLANNING_PROMPT_TEMPLATE_CONNECTED.format(
        topic=topic, verified_ledger_text=verified_ledger_text, point_role_hint_block=hint_section)
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
        raise RuntimeError("Point Role Planning応答が空です")
    parsed = json.loads(text)
    return {"parsed": parsed, "model": response.model, "response_id": response.id, "prompt": prompt}


# ============================================================
# run_one_pattern_connected: er003_v1_n3_01_articles_generate.py
# run_one_pattern()(809-1214行、406行)のコピー。変更点はヘッダーコメント
# 2節に記載の4点のみ(関数名変更、新規引数追加、Point Role Planning呼び
# 出し2箇所の置換、bareヘルパー参照へのprod_gen.修飾)。
# ============================================================
def run_one_pattern_connected(client, theme_id: str, label: str, prompt: str, verified_ledger_text: str,
                     topic: str, out_dir: str, apply_evidence_compression: bool = True,
                     apply_directional_fact_precheck: bool = True,
                     point_role_hint_block: str = "") -> dict:
    """apply_evidence_compression(既定True、ER-008-EVIDENCE-COMPRESSION-
    PROD-AND-N7-AUDIO-06でProduction既定へ昇格): WriterがFact-safeな記事
    を生成した直後、Lossless Editor(方式C、er003_v1_n3_01_evidence_
    compression_editor.py)でspoken layerだけを軽量化する。Research/
    Evidence Pack/VFL/Fact Ledger自体は変更しない。EditorはWriterでは
    なく、意味を保ったまま聴取負荷を下げるだけの工程(禁止事項は
    er003_v1_n3_01_evidence_compression_editor.py参照)。Editor適用後の
    テキストに対してmetrics/Fact Check/Ledger Deviationを実行するため、
    既存の安全確認プロセスがそのままEditor出力にも適用される。DEV/test
    でOFFにしたい場合はFalseを渡す(Production既定はTrue)。"""
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    with open(f"{out_dir}/audit/prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)

    writer_model = routing.require_model(prod_gen._writer_process(label), routing.WRITER_MODEL)

    # ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01: Point One/Twoの本文を書く
    # 前に、Verified Fact Ledgerに基づいてrole/new_listener_takeaway/
    # evidence_anchor/why_it_matters/重複禁止事項を明示的に計画させ、その
    # 計画をWriter promptへ挿入する(Point Role Planning)。
    role_plan_result = run_point_role_planning_connected(
        client, topic, verified_ledger_text, model=writer_model, reasoning_effort=prod_gen.REASONING_EFFORT,
        point_role_hint_block=point_role_hint_block)
    with open(f"{out_dir}/audit/point_role_planning_initial.json", "w", encoding="utf-8") as f:
        json.dump(role_plan_result, f, ensure_ascii=False, indent=2, default=str)
    prompt_with_plan = prompt + "\n" + point_planning.build_role_planning_block(role_plan_result["parsed"])

    gen = prod_gen._generate_and_compress_article(client, theme_id, label, prompt_with_plan, out_dir,
                                          apply_evidence_compression, writer_model)
    if gen["status"] != "OK":
        return {"label": label, "status": gen["status"], "article_text": None}
    article_text = gen["article_text"]
    fact_usage_report = gen["fact_usage_report"]
    evidence_compression_applied = gen["evidence_compression_applied"]

    # ER-22 + ER-009-N1-DIAGNOSTIC-FULL-RETRY-PRODUCTION-WIRING-13:
    # Point overlap NG時は記事全体をWriterから再生成する(最大
    # POINT_OVERLAP_ARTICLE_RETRY_MAX回)。Diagnostic Full Retry により、
    # retry時は前回の記事・overlap score・shared words・簡易診断を
    # NG例として prompt へ追加し、Evidence/VFL固定で全文再生成させる。
    # retry対象はWriter+Evidence Compression+overlap再チェックのみで、
    # Fact Checker/Ledger Deviationはループの外(最終確定後)で一度だけ実行。
    overlap_retry_log = []
    retry_attempt = 0
    while True:
        print(f"[N3-01][{theme_id}] {label}: Point-Full Story/Point-Point重複QA開始"
              f"(retry {retry_attempt}/{prod_gen.POINT_OVERLAP_ARTICLE_RETRY_MAX})...")
        point_qa_result = prod_gen.run_point_overlap_qa_and_regenerate(
            client, article_text, verified_ledger_text, model=writer_model,
            reasoning_effort=prod_gen.REASONING_EFFORT, out_dir=out_dir)
        overlap_report = point_qa_result.get("report") or {}
        lexical_flagged = point_qa_result["status"] == "OK" and any(
            overlap_report.get(key, {}).get("before_overlap", {}).get("flagged")
            for key in ("point_one", "point_two"))

        # ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01: Point Value QA
        # (No.18 A2で発見された「重複はしていないが新しい価値も無い」
        # Pointを検知する。lexical overlapとは独立した意味判定)。
        # split_common_sections_for_point_qaが構造を認識できた場合のみ実行
        # する(想定外構造の場合は既存のoverlap QA同様スキップし、後段の
        # 構造検証[restore_r2.validate_point_structure]に委ねる)。
        sections_for_value_qa = prod_gen.split_common_sections_for_point_qa(article_text)
        value_qa_result = None
        value_qa_flagged = False
        if sections_for_value_qa is not None:
            value_qa_result = point_planning.run_point_value_qa(
                client, sections_for_value_qa["full_story"], sections_for_value_qa["point_one_body"],
                sections_for_value_qa["point_two_body"], model=writer_model,
                reasoning_effort=prod_gen.REASONING_EFFORT)
            with open(f"{out_dir}/audit/point_value_qa_attempt{retry_attempt}.json", "w",
                      encoding="utf-8") as f:
                json.dump(value_qa_result, f, ensure_ascii=False, indent=2, default=str)
            value_qa_flagged = value_qa_result["status"] == "NG"

        still_flagged = lexical_flagged or value_qa_flagged
        log_entry = {
            "attempt": retry_attempt, "qa_status": point_qa_result["status"], "flagged": still_flagged,
            "lexical_flagged": lexical_flagged, "value_qa_flagged": value_qa_flagged,
            "report": overlap_report,
            "value_qa_status": value_qa_result["status"] if value_qa_result else None,
        }
        overlap_retry_log.append(log_entry)
        if not still_flagged or retry_attempt >= prod_gen.POINT_OVERLAP_ARTICLE_RETRY_MAX:
            break
        retry_attempt += 1
        print(f"[N3-01][{theme_id}] {label}: Point overlap/value QA NG"
              f"(lexical={lexical_flagged}, value_qa={value_qa_flagged})。"
              f"Point Role Planningを再計画し、Diagnostic Full Retryで全文再生成します"
              f"(article retry {retry_attempt}/{prod_gen.POINT_OVERLAP_ARTICLE_RETRY_MAX})...")

        # Diagnostic section を build(lexical overlap診断は既存機構をそのまま使用)
        point_overlap_result = {
            "point_one": overlap_report["point_one"]["before_overlap"],
            "point_two": overlap_report["point_two"]["before_overlap"],
        }
        diagnostic_prompt = prod_gen.build_diagnostic_retry_prompt(prompt, article_text, point_overlap_result)
        if value_qa_flagged:
            diagnostic_prompt = diagnostic_prompt + "\n\n" + point_planning.build_value_qa_diagnostic_note(
                value_qa_result)
        log_entry["diagnostic_used"] = {
            "point_one_score": point_overlap_result["point_one"]["overlap_ratio"],
            "point_one_flagged": point_overlap_result["point_one"]["flagged"],
            "point_two_score": point_overlap_result["point_two"]["overlap_ratio"],
            "point_two_flagged": point_overlap_result["point_two"]["flagged"],
            "point_one_vs_point_two_flagged": overlap_report.get("point_one_vs_point_two", {}).get("flagged"),
            "value_qa_flagged": value_qa_flagged,
        }

        # ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01: Diagnostic Full Retryは
        # 「必要な生成単位全体をLedgerから再生成する」既存方針に従い、Point
        # Role Planningも記事全体と同じ単位として毎回再計画する(前回の計画を
        # 使い回さない)。
        role_plan_result = run_point_role_planning_connected(
            client, topic, verified_ledger_text, model=writer_model, reasoning_effort=prod_gen.REASONING_EFFORT,
            point_role_hint_block=point_role_hint_block)
        with open(f"{out_dir}/audit/point_role_planning_retry{retry_attempt}.json", "w",
                  encoding="utf-8") as f:
            json.dump(role_plan_result, f, ensure_ascii=False, indent=2, default=str)
        diagnostic_prompt = diagnostic_prompt + "\n" + point_planning.build_role_planning_block(
            role_plan_result["parsed"])

        gen = prod_gen._generate_and_compress_article(client, theme_id, label, diagnostic_prompt, out_dir,
                                              apply_evidence_compression, writer_model)
        if gen["status"] != "OK":
            print(f"[N3-01][{theme_id}] {label}: article retry中にwriterが失敗しました status={gen['status']}")
            overlap_retry_log.append({"attempt": retry_attempt, "qa_status": "WRITER_FAILED_DURING_RETRY"})
            break
        article_text = gen["article_text"]
        fact_usage_report = gen["fact_usage_report"]
        evidence_compression_applied = gen["evidence_compression_applied"]

    with open(f"{out_dir}/point_overlap_article_retry_log.json", "w", encoding="utf-8") as f:
        json.dump(overlap_retry_log, f, ensure_ascii=False, indent=2, default=str)

    point_overlap_qa_applied = False  # Point-only regeneration自体は撤去済み(常にFalse)
    if overlap_retry_log[-1].get("flagged"):
        print(f"[N3-01][{theme_id}] {label}: Point overlapが{prod_gen.POINT_OVERLAP_ARTICLE_RETRY_MAX}回の記事全体"
              f"再生成後もNGのままでした。自動続行せずNG_REVIEW_REQUIREDとして報告します"
              f"(Fact Checker以降は実行しません)。")
        return {
            "label": label, "status": "NG_REVIEW_REQUIRED", "article_text": article_text,
            "point_overlap_article_retry_attempts": retry_attempt,
            "point_overlap_final_report": overlap_retry_log[-1].get("report"),
            "evidence_compression_applied": evidence_compression_applied,
            "fact_usage_report": fact_usage_report,
            "point_overlap_qa_applied": point_overlap_qa_applied,
        }
    print(f"[N3-01][{theme_id}] {label}: Point-Full Story重複QA完了(overlapなし、"
          f"記事全体retry {retry_attempt}回で解消)。")

    metrics = prod_gen.compute_metrics(article_text)
    section_wc = sf1r1.section_word_counts(article_text)
    length_report = {
        **section_wc, "total": metrics["word_count"],
        "point_one_within_target": prod_gen.POINT_TARGET_LOWER <= section_wc["point_one"] <= prod_gen.POINT_TARGET_UPPER,
        "point_one_within_tolerance": prod_gen.POINT_TOLERANCE_LOWER <= section_wc["point_one"] <= prod_gen.POINT_TOLERANCE_UPPER,
        "point_two_within_target": prod_gen.POINT_TARGET_LOWER <= section_wc["point_two"] <= prod_gen.POINT_TARGET_UPPER,
        "point_two_within_tolerance": prod_gen.POINT_TOLERANCE_LOWER <= section_wc["point_two"] <= prod_gen.POINT_TOLERANCE_UPPER,
        "total_within_soft_range": prod_gen.TOTAL_SOFT_LOWER <= metrics["word_count"] <= prod_gen.TOTAL_SOFT_UPPER,
    }
    with open(f"{out_dir}/metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/length_report.json", "w", encoding="utf-8") as f:
        json.dump(length_report, f, ensure_ascii=False, indent=2)
    print(f"[N3-01][{theme_id}] {label}: metrics={metrics} sections={section_wc}")

    print(f"[N3-01][{theme_id}] {label}: fact checker呼び出し開始...")
    fc_prompt = r3.build_fact_check_prompt(topic, article_text, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(
            fc_prompt, model=routing.require_model("WRITER_FACT_CHECK", routing.WRITER_FACT_CHECK_MODEL))

    fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = \
        r3.run_fact_checker_with_gates(make_fc_fn, sleep_fn=time.sleep)
    verdict = fc_result.get("verdict") if fc_result else None
    print(f"[N3-01][{theme_id}] {label}: fact_check status={fc_status} verdict={verdict}")
    fact_qa_record = {
        "label": label, "final_status": fc_status, "model": fc_model, "response_id": fc_response_id,
        "web_search_call_count": fc_search_usage["web_search_call_count"] if fc_search_usage else None,
        "attempts": len(fc_attempts), "result": fc_result,
    }
    with open(f"{out_dir}/fact_qa.json", "w", encoding="utf-8") as f:
        json.dump(fact_qa_record, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/fact_check_attempts.json", "w", encoding="utf-8") as f:
        json.dump(fc_attempts, f, ensure_ascii=False, indent=2, default=str)

    # ER-010-NO9-FACTCHECK-POLICY-AND-POINT-COMPRESSION-DIAGNOSTIC-12(ユーザー正式Decision):
    # Fact Checkerのverdict="REVIEW_REQUIRED"(確認できない具体的主張・解釈・
    # certainty nuance等、fact_checker_prompt_template_r3.txt参照)は、原則
    # non-blocking advisoryとして扱い、記事生成・QA工程を継続する(status=OKの
    # 判定材料にしない)。指摘は最終artifact提示時に「Fact Checker参考指摘」
    # として別途ユーザーへ提示する(fact_qa.jsonのcontradictions/
    # unsupported_specific_claims/notesがその内容)。一方、verdict="FAIL"
    # (信頼できる情報と明確に矛盾する場合のみ付与される)は、Ledger Deviation
    # MAJORや Point overlap未解消と同様にblockingとして扱い、それ以降の
    # 工程(Ledger逸脱チェック・Directional Fact Precheck)は実行せず
    # NG_REVIEW_REQUIREDを返す。役割はLedger Deviation Checkerとは異なる
    # (Ledgerは記事とVerified Fact Ledgerの整合性、Fact Checkerは独立Web
    # 検索によるexternal factとの整合性)ため、判定を混同しない。
    if verdict == "FAIL":
        print(f"[N3-01][{theme_id}] {label}: fact checkerがFAIL(信頼できる情報と明確に矛盾)と"
              f"判定しました。自動続行せずNG_REVIEW_REQUIREDとして報告します"
              f"(ledger逸脱チェック以降は実行しません)。")
        return {
            "label": label, "status": "NG_REVIEW_REQUIRED", "article_text": article_text,
            "metrics": metrics, "section_word_counts": section_wc, "length_report": length_report,
            "fact_status": fc_status, "fact_verdict": verdict, "fact_check_result": fc_result,
            "fact_usage_report": fact_usage_report,
            "evidence_compression_applied": evidence_compression_applied,
            "point_overlap_qa_applied": point_overlap_qa_applied,
            "point_overlap_article_retry_attempts": retry_attempt,
        }

    print(f"[N3-01][{theme_id}] {label}: ledger逸脱チェック開始(Hook-aware)...")
    ledger_model = routing.require_model(prod_gen._writer_process(label), routing.WRITER_MODEL)
    deviation_result = vfl01.run_deviation_check(
        client, verified_ledger_text, article_text, model=ledger_model, hook_aware=True)
    print(f"[N3-01][{theme_id}] {label}: deviation overall_status={deviation_result['parsed']['overall_status']} "
          f"deviations={len(deviation_result['parsed']['deviations'])}")

    # ER-010-NO9-LOCAL-REWRITE-LOOP-FINAL-10: MAJOR検出時は記事全体を再生成
    # せず、局所Rewriteのみを行う。局所Rewrite後は記事全体をLedger Deviation
    # Checkerへ再投入し(Hook-aware)、そこで新たなMAJORが見つかった場合も
    # 「一度直したから終了」とはせず、MAX_REWRITE_CYCLES回まで同じ局所
    # Rewriteを繰り返す(cycle上限の根拠はer010_ledger_local_rewrite_09.py
    # のMAX_REWRITE_CYCLES定義を参照)。対象はMAJORのみ、MINORは記録のみで
    # 対象外。上限まで繰り返してもMAJORが残る場合はNG_REVIEW_REQUIREDとし、
    # 無限ループや黙示的PASSは行わない。
    local_rewrite_results = []
    local_rewrite_cycles = []
    cycle = 0
    previously_seen_claims = set()

    def _run_check_window(window_text: str) -> dict:
        r = vfl01.run_deviation_check(client, verified_ledger_text, window_text,
                                       model=ledger_model, hook_aware=True)
        return r["parsed"]

    major_items = [d for d in deviation_result["parsed"]["deviations"] if d["severity"] == "MAJOR"]

    while major_items and cycle < local_rewrite.MAX_REWRITE_CYCLES:
        cycle += 1
        newly_discovered_claims = [d["claim_in_article"] for d in major_items
                                    if d["claim_in_article"] not in previously_seen_claims]
        print(f"[N3-01][{theme_id}] {label}: Local Rewrite cycle {cycle}/"
              f"{local_rewrite.MAX_REWRITE_CYCLES} - Ledger MAJOR {len(major_items)}件を検出"
              f"({len(newly_discovered_claims)}件は前cycleまでに未出現の新規MAJOR)。局所Rewrite開始...")

        cycle_results = []
        sentences = local_rewrite.split_sentences(article_text)
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
                print(f"[N3-01][{theme_id}] {label}: cycle {cycle} NG item {idx}: 対象文が特定できず"
                      f"human_review_required=Trueとして記録します。")
                continue
            try:
                sidx = sentences.index(target)
            except ValueError:
                sidx = -1
            before_ctx = sentences[sidx - 1] if 0 <= sidx - 1 else ""
            after_ctx = sentences[sidx + 1] if 0 <= sidx and sidx + 1 < len(sentences) else ""
            # OPEN-113-POINT-CONTEXT-PRODUCTION-WIRING-04(ユーザー正式採用、
            # OPEN-113 Trial-03でVALIDATED): 対象文が属するPoint(またはsection)
            # 全文をRewriteモデルへ参考contextとして渡す。既存のbefore/after
            # context(check windowの範囲)・System Prompt・attempt escalation
            # 文言・Retry上限・Ledger再チェック方法は一切変更しない。対象文の
            # 所属section特定に失敗した稀なケースのみ、追加前の挙動(前後1文)へ
            # fallbackする。
            point_context = local_rewrite.extract_point_context(article_text, target)
            point_context_found = point_context is not None
            if point_context is None:
                point_context = f"{before_ctx} {target} {after_ctx}".strip()
            r = local_rewrite.rewrite_ng_item(client, ledger_model, prod_gen.REASONING_EFFORT,
                                               verified_ledger_text, point_context, target,
                                               deviation, before_ctx, after_ctx, _run_check_window)
            r["cycle"] = cycle
            r["item_idx"] = idx
            r["location_method"] = location_method
            r["point_context_found"] = point_context_found
            r["point_context"] = point_context
            cycle_results.append(r)
            print(f"[N3-01][{theme_id}] {label}: cycle {cycle} NG item {idx}: resolved={r['resolved']} "
                  f"human_review={r['human_review_required']} attempts={len(r['attempts'])}")

        article_text = local_rewrite.apply_rewrites(article_text, cycle_results)

        # Formatting normalization (emoji・unnecessary bold削除)
        article_text = prod_gen.normalize_article_formatting(article_text)

        with open(f"{out_dir}/article.md", "w", encoding="utf-8") as f:
            f.write(article_text)

        # 局所Rewriteで本文が変わったため、metrics/length_reportを再計算し
        # 上書きする(Rewrite前のword countがそのまま記録され続けるのを防ぐ)。
        metrics = prod_gen.compute_metrics(article_text)
        section_wc = sf1r1.section_word_counts(article_text)
        length_report = {
            **section_wc, "total": metrics["word_count"],
            "point_one_within_target": prod_gen.POINT_TARGET_LOWER <= section_wc["point_one"] <= prod_gen.POINT_TARGET_UPPER,
            "point_one_within_tolerance": prod_gen.POINT_TOLERANCE_LOWER <= section_wc["point_one"] <= prod_gen.POINT_TOLERANCE_UPPER,
            "point_two_within_target": prod_gen.POINT_TARGET_LOWER <= section_wc["point_two"] <= prod_gen.POINT_TARGET_UPPER,
            "point_two_within_tolerance": prod_gen.POINT_TOLERANCE_LOWER <= section_wc["point_two"] <= prod_gen.POINT_TOLERANCE_UPPER,
            "total_within_soft_range": prod_gen.TOTAL_SOFT_LOWER <= metrics["word_count"] <= prod_gen.TOTAL_SOFT_UPPER,
        }
        with open(f"{out_dir}/metrics.json", "w", encoding="utf-8") as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)
        with open(f"{out_dir}/length_report.json", "w", encoding="utf-8") as f:
            json.dump(length_report, f, ensure_ascii=False, indent=2)

        print(f"[N3-01][{theme_id}] {label}: cycle {cycle} Local Rewrite後、Ledger全体を再判定...")
        deviation_result = vfl01.run_deviation_check(
            client, verified_ledger_text, article_text, model=ledger_model, hook_aware=True)
        recheck_major = [d for d in deviation_result["parsed"]["deviations"] if d["severity"] == "MAJOR"]
        print(f"[N3-01][{theme_id}] {label}: cycle {cycle} 再判定 overall_status="
              f"{deviation_result['parsed']['overall_status']} MAJOR={len(recheck_major)}件")

        previously_seen_claims |= {d["claim_in_article"] for d in major_items}
        local_rewrite_results.extend(cycle_results)
        local_rewrite_cycles.append({
            "cycle": cycle,
            "targeted_major_count": len(major_items),
            "newly_discovered_claims": newly_discovered_claims,
            "results": cycle_results,
            "full_recheck_overall_status": deviation_result["parsed"]["overall_status"],
            "full_recheck_major_count": len(recheck_major),
            "full_recheck_remaining_major_claims": [d["claim_in_article"] for d in recheck_major],
        })

        major_items = recheck_major

    cycle_exhausted = bool(major_items) and cycle >= local_rewrite.MAX_REWRITE_CYCLES
    if cycle_exhausted:
        print(f"[N3-01][{theme_id}] {label}: Local Rewrite cycle上限"
              f"({local_rewrite.MAX_REWRITE_CYCLES}回)に達してもMAJORが残存しています。")

    with open(f"{out_dir}/ledger_deviation.json", "w", encoding="utf-8") as f:
        json.dump(deviation_result["parsed"], f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/deviation_full_record.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in deviation_result.items() if k != "parsed"}, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{out_dir}/audit/local_rewrite_results.json", "w", encoding="utf-8") as f:
        json.dump(local_rewrite_results, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{out_dir}/audit/local_rewrite_cycles.json", "w", encoding="utf-8") as f:
        json.dump(local_rewrite_cycles, f, ensure_ascii=False, indent=2, default=str)

    remaining_major = major_items
    any_human_review = any(r.get("human_review_required") for r in local_rewrite_results)
    if remaining_major or any_human_review:
        print(f"[N3-01][{theme_id}] {label}: Local Rewrite cycleを尽くしてもLedger MAJORが残存、"
              f"またはhuman_review_requiredな項目があります。自動続行せずNG_REVIEW_REQUIREDとして"
              f"報告します(Directional Fact Precheck以降は実行しません)。")
        return {
            "label": label, "status": "NG_REVIEW_REQUIRED", "article_text": article_text,
            "metrics": prod_gen.compute_metrics(article_text),
            "fact_status": fc_status, "fact_verdict": verdict,
            "ledger_status": deviation_result["parsed"]["overall_status"],
            "ledger_deviation_count": len(deviation_result["parsed"]["deviations"]),
            "local_rewrite_results": local_rewrite_results,
            "local_rewrite_cycles": local_rewrite_cycles,
            "local_rewrite_cycle_exhausted": cycle_exhausted,
            "fact_usage_report": fact_usage_report,
            "evidence_compression_applied": evidence_compression_applied,
            "point_overlap_qa_applied": point_overlap_qa_applied,
            "point_overlap_article_retry_attempts": retry_attempt,
        }

    directional_precheck_status = None
    if apply_directional_fact_precheck:
        print(f"[N3-01][{theme_id}] {label}: 比較方向Fact事前チェック(暫定、"
              f"ER-008-DIRECTIONAL-FACT-PRECHECK-08)開始...")
        vfl_path = f"{os.path.dirname(out_dir)}/research/stage_b3_vfl.json"
        directional_result = dfp.audit_article_directional_facts(
            article_text, verified_ledger_text, vfl_path=vfl_path)
        directional_precheck_status = directional_result["overall_status"]
        with open(f"{out_dir}/audit/directional_fact_precheck.json", "w", encoding="utf-8") as f:
            json.dump(directional_result, f, ensure_ascii=False, indent=2, default=str)
        print(f"[N3-01][{theme_id}] {label}: 比較方向Fact事前チェック完了。"
              f"overall_status={directional_precheck_status}"
              + ("(POTENTIAL_DIRECTION_REVERSALあり、詳細はdirectional_fact_precheck.jsonを確認)"
                 if directional_precheck_status == "POTENTIAL_DIRECTION_REVERSAL" else ""))

    return {
        "label": label, "status": "OK", "article_text": article_text,
        "metrics": metrics, "section_word_counts": section_wc, "length_report": length_report,
        "fact_status": fc_status, "fact_verdict": verdict,
        "ledger_status": deviation_result["parsed"]["overall_status"],
        "ledger_deviation_count": len(deviation_result["parsed"]["deviations"]),
        "local_rewrite_results": local_rewrite_results,
        "local_rewrite_cycles": local_rewrite_cycles,
        "local_rewrite_cycle_exhausted": cycle_exhausted,
        "fact_usage_report": fact_usage_report,
        "evidence_compression_applied": evidence_compression_applied,
        "point_overlap_qa_applied": point_overlap_qa_applied,
        "point_overlap_article_retry_attempts": retry_attempt,
        "directional_fact_precheck_status": directional_precheck_status,
    }


# ============================================================
# 単体テスト(APIを呼ばない、Prompt文字列のバイト一致のみを確認)
# ============================================================
def test_default_hint_is_byte_identical_to_production():
    """point_role_hint_block=""(既定)の場合、Trial版テンプレートの出力が
    production版point_planning.ROLE_PLANNING_PROMPT_TEMPLATEの出力と
    バイト単位で完全一致することを確認する(後方互換の核心)。"""
    topic = "テストテーマ"
    ledger = "verified fact ledger fixture text"
    trial_prompt = ROLE_PLANNING_PROMPT_TEMPLATE_CONNECTED.format(
        topic=topic, verified_ledger_text=ledger, point_role_hint_block="")
    prod_prompt = point_planning.ROLE_PLANNING_PROMPT_TEMPLATE.format(
        topic=topic, verified_ledger_text=ledger)
    assert trial_prompt == prod_prompt, "既定値(空)でproduction版と1バイトも一致しない差分がある"
    assert trial_prompt.encode("utf-8") == prod_prompt.encode("utf-8")
    return {"status": "PASS", "trial_len": len(trial_prompt), "prod_len": len(prod_prompt)}


def test_trend_synthesis_unaffected_when_hint_empty():
    """A-UDR-11付随決定: Trend Synthesis側は本Trialで不変維持。
    editorial_mode="trend_synthesis"相当でも、point_role_hint_block=""を
    使う限りRole Planning promptはproduction既存Trend Synthesis運用時の
    ものとバイト一致する(Role Planning自体はeditorial_modeを引数に取ら
    ないため、この一致はbuild_common_block側のFocus Module挿入位置とは
    独立)。"""
    topic = "Trend Synthesisテストテーマ"
    ledger = "trend synthesis verified fact ledger fixture text"
    hint = f"{TREND_SYNTHESIS_POINT_ROLE_HINT_BLOCK}\n\n" if TREND_SYNTHESIS_POINT_ROLE_HINT_BLOCK else ""
    trial_prompt = ROLE_PLANNING_PROMPT_TEMPLATE_CONNECTED.format(
        topic=topic, verified_ledger_text=ledger, point_role_hint_block=hint)
    prod_prompt = point_planning.ROLE_PLANNING_PROMPT_TEMPLATE.format(
        topic=topic, verified_ledger_text=ledger)
    assert trial_prompt == prod_prompt
    # build_common_block/build_prompt自体も無変更であることの副次確認
    common_default = prod_gen.build_common_block("master text fixture", topic, ledger)
    common_trend = prod_gen.build_common_block(
        "master text fixture", topic, ledger,
        editorial_type_module_block=prod_gen.resolve_editorial_type_module_block("trend_synthesis"))
    assert common_default != common_trend, "Trend Synthesis指定時はEBがcommon_blockへ挿入される既存挙動のはず"
    return {"status": "PASS"}


def test_option_a_hint_equals_editorial_type_module_block():
    """案(a)の実現方法確認: 案(a)はpoint_role_hint_blockへEBをそのまま
    渡すだけであり、追加のコード変更なしに同じ接続メカニズムで実現できる
    ことを示す(このテストはprompt生成にAPIを呼ばない)。"""
    topic = "テストテーマ"
    ledger = "verified fact ledger fixture text"
    hint = f"{MAJOR_DAILY_NEWS_FOCUS_MODULE_BLOCK}\n\n"
    trial_prompt = ROLE_PLANNING_PROMPT_TEMPLATE_CONNECTED.format(
        topic=topic, verified_ledger_text=ledger, point_role_hint_block=hint)
    assert MAJOR_DAILY_NEWS_FOCUS_MODULE_BLOCK in trial_prompt
    assert "Point One・Point Twoそれぞれについて" in trial_prompt
    return {"status": "PASS"}


def run_all_unit_tests() -> dict:
    results = {
        "test_default_hint_is_byte_identical_to_production": test_default_hint_is_byte_identical_to_production(),
        "test_trend_synthesis_unaffected_when_hint_empty": test_trend_synthesis_unaffected_when_hint_empty(),
        "test_option_a_hint_equals_editorial_type_module_block": test_option_a_hint_equals_editorial_type_module_block(),
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(f"{OUT_DIR}/unit_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return results


# ============================================================
# 最小runtime検証(案(b)推奨案、major_daily_news相当、Hanshin Ledger固定)
# A2/B1B各1本のみ生成する(baseline再比較はTrial-02で完了済みのため、
# 本Trialでは接続の動作確認に限定し、追加生成は行わない)。
# ============================================================
def run_connected_condition():
    client = vfl01.get_client()
    master_full_text = ab01.load_master_full_text()
    verified_ledger_text = load_text(HANSHIN_LEDGER_PATH)

    results = {}
    timing = {}
    for label, instruction, level_dir, stage_tag in [
        ("B1B", prod_gen.B1_B_DIRECT_INSTRUCTION, "b1b", "writer_b1"),
        ("A2", prod_gen.A2_KAI1_INSTRUCTION, "a2", "writer_a2"),
    ]:
        level_out_dir = f"{OUT_DIR}/connected/{level_dir}"
        common_block = prod_gen.build_common_block(
            master_full_text, HANSHIN_TOPIC_JA, verified_ledger_text,
            editorial_type_module_block=MAJOR_DAILY_NEWS_FOCUS_MODULE_BLOCK)
        prompt = prod_gen.build_prompt(common_block, instruction)
        theme_tag = f"{THEME_ID}_connected"
        t0 = time.time()
        with cl.logging_context(theme_tag, stage_tag):
            result = run_one_pattern_connected(
                client, theme_tag, label, prompt, verified_ledger_text, HANSHIN_TOPIC_JA, level_out_dir,
                point_role_hint_block=MAJOR_DAILY_NEWS_POINT_ROLE_HINT_BLOCK)
        timing[stage_tag] = round(time.time() - t0, 2)
        results[label] = result
        print(f"[{THEME_ID}][connected] {label}: status={result.get('status')} "
              f"fact_verdict={result.get('fact_verdict')} ledger_status={result.get('ledger_status')} "
              f"point_overlap_article_retry_attempts={result.get('point_overlap_article_retry_attempts')}")

    os.makedirs(f"{OUT_DIR}/connected", exist_ok=True)
    with open(f"{OUT_DIR}/connected/articles_run_summary.json", "w", encoding="utf-8") as f:
        json.dump({k: {kk: vv for kk, vv in v.items() if kk != "article_text"} for k, v in results.items()},
                   f, ensure_ascii=False, indent=2, default=str)
    with open(f"{OUT_DIR}/connected/writer_timing.json", "w", encoding="utf-8") as f:
        json.dump(timing, f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/connected/point_role_hint_block_used.txt", "w", encoding="utf-8") as f:
        f.write(MAJOR_DAILY_NEWS_POINT_ROLE_HINT_BLOCK)
    return results


if __name__ == "__main__":
    import sys

    which = sys.argv[1] if len(sys.argv) > 1 else "test"
    if which == "test":
        run_all_unit_tests()
    elif which == "runtime":
        run_all_unit_tests()
        cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
        run_connected_condition()
    else:
        print("usage: python er011_point_role_planning_focus_connection_trial_03.py [test|runtime]")


# ============================================================
# DESIGN_COMPARISON (レポート本体に詳細表あり、ここでは要点のみ):
#
# | 観点 | (a) Focus Module直接注入 | (b) Mode別Point Role候補リスト(推奨) | (c) 併用 |
# |---|---|---|---|
# | 後方互換(既定値でバイト不変) | Yes(point_role_hint_block=""で不変) | Yes(同左) | Yes(同左) |
# | Trend Synthesis非影響 | Yes(hint=""のまま不変維持可能) | Yes(同左) | Yes(同左) |
# | Diagnostic Full Retryでの引き継ぎ | Yes(同じ引数をretry呼び出しにも渡すだけ) | Yes(同左) | Yes(同左) |
# | Dangling Reference | なし(既存EB変数を再利用するのみ) | なし(新規定数のみ、EDITORIAL_TYPE_MODULE_BLOCKS辞書と独立) | なし |
# | 実装規模 | 最小(既存変数を渡すだけ) | 最小+新規hint定数1個 | 最小+新規hint定数1個 |
# | Role Planning promptの長さ/ノイズ | 大(Focus Module全文、Main Story文体寄りの長い指示がJSON専用callへ混入) | 小(役割候補のみの短い一文、schema呼び出しの性質に合う) | 最大(重複気味) |
# | 意味的整合性 | Main Storyと完全同一の文言で一貫はするが、Role Planningが必要とする情報(役割候補)以外(entertainment/engagement等)も混入し得る | Role Planningの出力項目(role)に直接対応する情報だけを渡せる、ノイズが少ない | 両方の利点を持つが呼び出しごとのprompt長が増え費用微増 |
#
# 推奨: (b)。理由: Role Planningは6項目のJSON schema出力に特化した小さい
# 呼び出しであり、Main Story向けの長いnarrative指示(Focus Module全文)を
# そのまま混入させるより、役割候補という直接対応する情報だけを渡す方が
# ノイズが少なく、意味的にも「Role Planningが選ぶべき役割の候補」という
# この呼び出しの目的に合致する。(a)は実装は最も簡単だが、Focus Module本文
# 中のPoint Balance以外の指示(counter-signal/limitation以外の話法指示等)
# が計画段階のJSON出力を不必要に複雑化させるリスクがある。(c)は(a)+(b)の
# 併用でさらに安全側に振れるが、費用・prompt長が増えるため、まずは(b)単独
# で効果を確認し、不十分な場合の拡張候補として温存する。
# ============================================================

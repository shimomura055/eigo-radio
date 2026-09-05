# ============================================================
# er011_open112_trend_engagement_reference_ab_trial_10.py
# OPEN-112-TREND-ENGAGEMENT-REFERENCE-AB-TRIAL-10
# ============================================================
# 目的: Trial-09で確認された「Trend Synthesisは構造としては成立するが、
# Main Storyが時系列の出来事列挙に寄り、面白さ・意外性・エンターテインメント性が
# 弱い」という問題に対し、
#   施策1: Writer根底指示へ「面白さ・意外性・エンターテインメント性」を明示追加
#   施策2: Fact Ledgerとは別にReference Digest(構成・切り口のみ、Fact禁止)を
#          Writerへ渡す
# の2施策を、B1レベルのA/B比較で検証する。
#
# A = 施策1のみ(Entertainment/Engagement根底指示を追加、Reference Digestなし)
# B = 施策1 + 施策2(Aと完全同条件 + Reference Digestを追加)
#
# 同一に保つもの: Topic(TREND_TOPIC_JA、Trial-09と同一テーマ)・Verified Fact
# Ledger(Trial-09のLedger入力ミス[F-005機雷個数、F-009曜日/日付]を修正した
# verified版)・Trend Synthesis Focus Module本体(Trial-09と同一文面)・
# Article-specific Inputs・model/routing・CEFR(B1)・既存QA・Trend Gate。
#
# Research/Writer責務の分離(重要、§0):
#   Research(このスクリプト実行前に本ファイル内で完結する手作業): 何が
#   事実かを決め、Verified Fact Ledgerを作る。Reference Articlesはこの
#   Ledgerのfact sourceとして使用しない。
#   Writer: Fact Ledgerの範囲内で、切り口・順序・見せ方を決める。
#   Reference Articles/Reference DigestはWriterへの「構成・切り口・見せ方の
#   参考」としてのみ渡し、Referenceにしかない事実・数字・因果関係・固有情報を
#   記事へ持ち込ませない(§12で生成後に検証する)。
#
# Production変更: なし。既存ファイル(er003_v1_n3_01_articles_generate.py等)は
# 一切変更しない。gen.run_one_pattern()を無変更のまま呼び出す。新Validator・
# 新Fact Checker・新LLM QA・Overlap閾値変更は追加しない(既存QAのみで評価)。
#
# 今回禁止: Production Prompt/code変更、Overlap閾値変更、severity正式変更、
# Reference Digest Production実装、Topic Master変更、Trend Memory実装、
# APPROVED_FOR_PRODUCTION、PRODUCTION_WIRED。
#
# 到達してよいStatus: REJECTED / VALIDATED / USER_DECISION_REQUIRED のみ。
from __future__ import annotations

import difflib
import json
import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as gen
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er011_no18_specfix_v2_production_run_01 as driver
import er011_open112_trend_synthesis_minimal_prompt_trial_09 as trial09

PHASE_A_BASELINE_DIR = "er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2_ec_a_precision_21r"
PHASE_A_TOPIC_JA = driver.TOPIC_JA

NEW_THEME_ID = "open112_trend_engagement_reference_ab_trial_10"
OUT_DIR = f"er011_output/{NEW_THEME_ID}"
TRIAL_RESEARCH_DIR = f"{OUT_DIR}/research"

# Trial-09と同一テーマ文面をそのまま再利用する(比較可能性を最大化するため、
# §2の指示どおり。テーマ記述自体にはLedger入力ミスは無かったため変更不要)。
TREND_TOPIC_JA = trial09.TREND_TOPIC_JA

with open(f"{TRIAL_RESEARCH_DIR}/verified_fact_ledger.txt", encoding="utf-8") as _f:
    TREND_VERIFIED_LEDGER_TEXT = _f.read()

ANCHOR = trial09.ANCHOR  # 【Spoken-first原則(数字の扱い)】(既存Trialと同一Anchor)
TREND_SYNTHESIS_FOCUS_MODULE_BLOCK = trial09.TREND_SYNTHESIS_FOCUS_MODULE_BLOCK

LEVELS = {"b1b": {"label": "B1B", "instruction_attr": "B1_B_DIRECT_INSTRUCTION"}}
MAX_RUNS_PER_LEVEL = 2  # Loop Budget(§10。初回1回、判別困難な場合のみ+1回まで)

# ------------------------------------------------------------
# 施策1: Entertainment / Engagement 根底原則(A・B共通)
# ------------------------------------------------------------
ENTERTAINMENT_ENGAGEMENT_BLOCK = """【Interesting/Engaging/Entertaining原則(今回のTrialで追加する根底品質原則。\
OPEN-112-TREND-ENGAGEMENT-REFERENCE-AB-TRIAL-10、Production未採用)】
記事は、正確でよく整理されているだけでは十分ではありません。聞き手が

- 続きを知りたくなる
- 「そういう見方があるのか」と感じる
- 意外な関係や対比に気づく
- 話として面白いと感じる
- 誰かに話したくなる

と感じられることを目指してください。ただし、面白さを作るためにVerified Fact
Ledgerの範囲を超えてはいけません。以下は禁止です:
- 事実の創作
- Ledgerが支持しない因果関係の主張(unsupported causality)
- 誇張(exaggeration)・扇情的な表現(sensationalism)
- Ledgerにない具体例の追加
- 根拠のない心理描写
- 根拠のない未来予測

目標は「正確 + 面白い + (裏付けがある場合の)意外性 + 聞いていて楽しい」の
組み合わせであり、面白さが正確さより優先されるという意味ではありません。
面白くする余地とFact Ledgerの制約が衝突する場合は、常にFact Ledgerの制約を
優先してください。

【Storytelling原則(時系列の出来事列挙にしない)】
Main Storyを、"A happened. Then B happened. Then C happened. Meanwhile D
happened."のような時系列ニュースダイジェストにしないでください。まず、
「この複数のSignalを一緒に見ると、何が興味深いのか」を先に見つけてください。
そのうえで、それを伝えるために本当に必要なEvidenceだけを選び、ひとつの
Story(throughline)として展開してください。個々の出来事を、起きた順番に
律儀になぞる必要はありません。

Main Storyの冒頭では、Verified Fact Ledgerの範囲内で成立する場合に限り、
以下のいずれかの技法を使うことを検討してください:
- contradiction(矛盾)
- surprising contrast(意外な対比)
- tension(緊張関係)
- reversal(見方の逆転)
- unexpected consequence(意外な結果)
- unanswered question(まだ答えの出ていない問い)
- gap between appearance and reality(見かけと実態のずれ)

これらの技法を無理に使う必要はありません。Ledgerが支持しない「意外性」を
発明することは禁止します。技法を使うかどうかより、記事全体がひとつの
throughlineを持つことを優先してください。"""


# ------------------------------------------------------------
# 施策2: Reference Digest(Bのみ)。Fact source使用禁止。
# ------------------------------------------------------------
# Reference Articles(2026-09-05、実際にWebSearch/WebFetchで収集・構成/技法のみ
# 観察。本文中の具体的な数字・日付・固有名詞・引用は、このDigest本文にも、
# 生成記事にも一切持ち込まない):
#   R1) Yahoo Finance, "The divide between energy trackers and the White House
#       deepened this week over how much oil is getting through the Strait of
#       Hormuz" (2026-09-XX)
#   R2) Al Jazeera, "Why Hormuz remains high risk for ships despite US claims
#       of mine-clearing" (2026-08-26)
#   R3) Fortune, "The Iran war could last 'deep into 2027' as the Strait of
#       Hormuz isn't that closed..." (2026-08-23)
#   R4) NPR, "Tanker sailors still face danger in the Strait of Hormuz"
#       (2026-08-08)
# 以下はこの4本について、構成・切り口・見せ方だけを人間(Research/Trial担当)が
# 観察してまとめた、事実を含まない生の観察メモ。この生メモ自体をWriterへは
# 渡さず、build_reference_digest()がLLM 1回呼び出しでWriter向けに整形した
# ものをREFERENCE_DIGEST_BLOCKとして使う(§13のコスト計測対象)。
REFERENCE_OBSERVATION_NOTES = """
Reference 1(経済系メディア、対立するデータ発表を扱った記事):
- Opening technique: ある1日の出来事について、「見方によって全く逆の一日になる」
  という逆説を提示して始まる。どちらが正しいかは明かさない。
- Central angle: 同じ日について、信頼できる二つの側が、大きく異なる主張をする。
- Interesting contrast: 小さく具体的な数字と、大きく劇的な数字を並べ、
  「両方とも本当なのか」という違和感を生む。
- Structural technique: どちらが正しいかを判定せず、対立そのものに記事を
  進めさせる「言い分対言い分」の構成。最後に、一見単純に見える計測が
  実際には難しい理由を、易しく種明かしする。
- Why it feels engaging: 読み手は「結局どちらが正しいのか」を知りたくなり、
  記事はその答えを少しずつ、信頼できる材料を足しながら遅らせる。

Reference 2(中東情勢を扱う国際メディアの記事):
- Opening technique: まず自信に満ちた「解決した」という発表を提示し、
  直後にそれを覆す。
- Central angle: 「公式には解決した」 vs 「実際にはまだ危険」という対比。
- Interesting contrast: 発表された成功の範囲は狭いのに、実際の脅威の
  範囲ははるかに広い。
- Structural technique: 権威ある側が成果を主張する → 直接利害を持つ側が
  正反対の懸念を述べる → 専門家がその論点自体をより大きな問いへ広げる、
  という三段構成。
- Why it feels engaging: 「もう終わった話」だと思っていた読み手ほど、
  裏切られる感覚を持つ。

Reference 3(経済誌の分析記事):
- Opening technique: 現在進行中の「よくある論争」を最初の一文で名指しし、
  そこへ読み手を引き込む。
- Central angle: 直感に反する逆転の発想。「普通ならこうなるはず」という
  読み手の予想を、途中で覆す。
- Interesting contrast: 「圧力が抜けている(＝解決に向かっているはず)」
  という前提を、「だからこそ長引く」という結論へ反転させる。
- Structural technique: 「何が起きているか」と「それが何を意味するか」を
  交互に行き来しながら、最後にある種の時間的な見通しへ着地する。
- Why it feels engaging: 読み手がすでに知っている事実(圧力が緩んでいる)を、
  読み手が予想していなかった結論(だから長引く)へつなげ直す。

Reference 4(公共ラジオ系メディアのインタビュー形式記事):
- Opening technique: 統計ではなく、一人の人物の言葉から始まる。
- Central angle: 地政学の話を、その渦中にいる人々の視点まで一気にズームインする。
- Interesting contrast: 「公式には前進している」という響きの言葉と、
  実際に足止めされ、危険にさらされ続けている人々の現実との落差。
- Structural technique: インタビュー形式で、一人の証言が記事全体の感情的な
  軸になる。
- Why it feels engaging: 統計だけでは伝わらない「宙ぶらりん」の感覚を、
  一つの具体的な人物像に凝縮する。
"""

REFERENCE_DIGEST_PROMPT = """あなたはeigo-radioのニュース記事Writerを補助する、構成・切り口専門の
編集アシスタントです。以下は、今回のTrendテーマと同じ/近いテーマを扱った、
質の高い4本の記事について、人間の編集者が「構成・切り口・見せ方」だけを
観察してまとめた生メモです。

このメモには、意図的に具体的な事実(数字・日付・固有名詞・引用・因果関係の
主張)は一切含まれていません。あなたの仕事は、このメモを土台に、今回の
Writer(別の記事を書くAI)へ渡す「Reference Digest」を整形することです。

【生メモ】
{notes}

【出力ルール(絶対厳守)】
- 出力は日本語で構いません。Reference 1〜4それぞれについて、
  Opening technique / Central angle / Interesting contrast /
  Structural technique / Why it feels engaging の5項目を簡潔に書いてください。
- 最後に、統合Digestとして以下を書いてください:
  useful opening patterns / useful contrasts / useful story structures /
  possible angles(ただし今回のFact Ledgerの範囲内でも使えそうな、
  抽象的な切り口の型のみ。具体的なFactを提案しないこと) /
  techniques to avoid chronological listing
- 具体的な数字・日付・固有名詞(社名・人名・メディア名・地名の追加)・
  引用・出来事は、一切新しく書き加えないでください。生メモに無い具体的な
  Factを絶対に作り出さないでください。
- 表現・文章そのものの模倣・転載はしないでください(技法の説明であって、
  文章のコピーではありません)。
- 冒頭に必ず次の警告文をそのまま含めてください:
  「これはFact Ledgerではありません。数字・日付・出来事・引用・行為者・
  因果説明・予測など、具体的Factは一切含みません。Reference Articlesの
  表現・文章のコピーもしないでください。ここにあるのは構成・切り口・
  見せ方のヒントだけです。事実は必ずVerified Fact Ledgerだけを根拠に
  してください。」
"""


def build_reference_digest(client) -> dict:
    """Reference Digest生成(Bのみ・§13のコスト計測対象の実LLM呼び出し)。
    新しいProduction routing processは追加せず、既存の承認済みcontract
    (B1_WRITERプロセス、routing.WRITER_MODEL)を再利用する(Production
    routing fileへの変更なし)。"""
    model = routing.require_model("B1_WRITER", routing.WRITER_MODEL)
    prompt = REFERENCE_DIGEST_PROMPT.format(notes=REFERENCE_OBSERVATION_NOTES)
    with cl.logging_context(f"{NEW_THEME_ID}_b", "reference_digest_generation"):
        response = client.responses.create(model=model, input=prompt)
    text = getattr(response, "output_text", None)
    if not text:
        # SDK差異対策(output_textが無いバージョン用のフォールバック抽出)
        chunks = []
        for item in getattr(response, "output", []) or []:
            for c in getattr(item, "content", []) or []:
                if getattr(c, "text", None):
                    chunks.append(c.text)
        text = "\n".join(chunks)
    return {"text": text.strip(), "model": model, "response_id": getattr(response, "id", None)}


def build_reference_digest_block(digest_text: str) -> str:
    return ("【Reference Digest(構成・切り口の参考。Fact sourceではない。"
            "OPEN-112-TREND-ENGAGEMENT-REFERENCE-AB-TRIAL-10、Production未採用)】\n"
            + digest_text)


# ------------------------------------------------------------
# Template構築(A/B 2バリアント)
# ------------------------------------------------------------
def build_candidate_template(variant: str, reference_digest_block: str | None = None) -> str:
    assert ANCHOR in gen.COMMON_BLOCK_TEMPLATE, (
        "アンカー文字列がgen.COMMON_BLOCK_TEMPLATE内に見つかりません。Production側のtemplateが"
        "本Trial設計時から変更されている可能性があるため中断してください(STOP条件)。")
    blocks = [TREND_SYNTHESIS_FOCUS_MODULE_BLOCK, ENTERTAINMENT_ENGAGEMENT_BLOCK]
    if variant == "B":
        assert reference_digest_block is not None
        blocks.append(reference_digest_block)
    insertion = "\n\n".join(blocks)
    return gen.COMMON_BLOCK_TEMPLATE.replace(ANCHOR, insertion + "\n\n" + ANCHOR, 1)


def build_candidate_prompt(candidate_template: str, master_full_text: str, topic: str,
                            verified_ledger_text: str, instruction: str) -> str:
    common_block = candidate_template.format(
        hanshin_master_full_text=master_full_text, topic=topic,
        verified_ledger_text=verified_ledger_text,
        shared_point_blueprint_block="", evidence_compression_block="")
    return gen.build_prompt(common_block, instruction)


# ------------------------------------------------------------
# Phase A: 静的差分確認(A/B両バリアント、テーマ非依存の機械的検証)
# ------------------------------------------------------------
def run_phase_a(master_full_text: str, phase_a_ledger_text: str, reference_digest_block: str) -> dict:
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    templates = {
        "A": build_candidate_template("A"),
        "B": build_candidate_template("B", reference_digest_block),
    }
    for variant, tpl in templates.items():
        with open(f"{OUT_DIR}/audit/candidate_template_{variant}.txt", "w", encoding="utf-8") as f:
            f.write(tpl)

    results = {}
    for variant, candidate_template in templates.items():
        for level, meta in LEVELS.items():
            instruction = getattr(gen, meta["instruction_attr"])
            candidate_prompt = build_candidate_prompt(
                candidate_template, master_full_text, PHASE_A_TOPIC_JA, phase_a_ledger_text, instruction)
            baseline_path = f"{PHASE_A_BASELINE_DIR}/{level}/audit/prompt.txt"
            with open(baseline_path, encoding="utf-8") as f:
                baseline_prompt = f.read()

            key = f"{variant}_{level}"
            with open(f"{OUT_DIR}/audit/phase_a_candidate_prompt_{key}.txt", "w", encoding="utf-8") as f:
                f.write(candidate_prompt)

            insertion = ("\n\n".join(
                [TREND_SYNTHESIS_FOCUS_MODULE_BLOCK, ENTERTAINMENT_ENGAGEMENT_BLOCK]
                + ([reference_digest_block] if variant == "B" else [])))
            reconstructed = baseline_prompt.replace(ANCHOR, insertion + "\n\n" + ANCHOR, 1)

            sm = difflib.SequenceMatcher(a=baseline_prompt, b=candidate_prompt, autojunk=False)
            opcodes = sm.get_opcodes()
            non_equal = [op for op in opcodes if op[0] != "equal"]
            unexpected = [op for op in non_equal if op[0] != "insert"]
            insert_ops = [op for op in non_equal if op[0] == "insert"]
            clean_single_insert = (len(unexpected) == 0 and len(insert_ops) == 1
                                    and reconstructed == candidate_prompt)

            results[key] = {
                "baseline_len": len(baseline_prompt), "candidate_len": len(candidate_prompt),
                "op_counts": {tag: sum(1 for o in opcodes if o[0] == tag) for tag in
                              ("equal", "insert", "delete", "replace")},
                "unexpected_op_count": len(unexpected),
                "clean_single_insert_confirmed": clean_single_insert,
            }
            print(f"[TRIAL-10][Phase A][{key}] op_counts={results[key]['op_counts']} "
                  f"clean_single_insert_confirmed={clean_single_insert}")

    phase_a_pass = all(r["clean_single_insert_confirmed"] for r in results.values())
    with open(f"{OUT_DIR}/audit/phase_a_result.json", "w", encoding="utf-8") as f:
        json.dump({"results": results, "phase_a_pass": phase_a_pass}, f, ensure_ascii=False, indent=2)
    print(f"[TRIAL-10][Phase A] phase_a_pass={phase_a_pass}")
    return {"results": results, "phase_a_pass": phase_a_pass, "templates": templates}


# ------------------------------------------------------------
# Phase B: A/B実生成(実Production関数を無変更のまま使用)
# ------------------------------------------------------------
def run_pattern(client, candidate_template: str, master_full_text: str, level: str, variant: str,
                 run_idx: int) -> dict:
    meta = LEVELS[level]
    instruction = getattr(gen, meta["instruction_attr"])
    candidate_prompt = build_candidate_prompt(
        candidate_template, master_full_text, TREND_TOPIC_JA, TREND_VERIFIED_LEDGER_TEXT, instruction)
    theme_id_variant = f"{NEW_THEME_ID}_{variant.lower()}"
    level_out_dir = f"{OUT_DIR}/{variant}_{level}_run{run_idx:02d}"

    print(f"[TRIAL-10][Phase B] variant={variant} {meta['label']} run{run_idx}: "
          f"gen.run_one_pattern()(実Production関数、無変更)開始...")
    t0 = time.time()
    with cl.logging_context(theme_id_variant, f"writer_{level}_run{run_idx:02d}"):
        result = gen.run_one_pattern(
            client, theme_id_variant, meta["label"], candidate_prompt, TREND_VERIFIED_LEDGER_TEXT,
            TREND_TOPIC_JA, level_out_dir)
    elapsed = time.time() - t0
    result["elapsed_seconds"] = round(elapsed, 1)
    result["variant"] = variant

    with open(f"{level_out_dir}/audit/candidate_prompt_used.txt", "w", encoding="utf-8") as f:
        f.write(candidate_prompt)

    writer_model = None
    try:
        with open(f"{level_out_dir}/audit/writer_attempts.json", encoding="utf-8") as f:
            attempts = json.load(f)
        pass_attempt = next((a for a in attempts if a["status"] == "STRUCTURE_PASS"), None)
        writer_model = pass_attempt.get("model") if pass_attempt else None
    except FileNotFoundError:
        pass
    result["writer_model_actual"] = writer_model

    print(f"[TRIAL-10][Phase B] variant={variant} {meta['label']} run{run_idx}: 完了。"
          f"status={result.get('status')} fact_verdict={result.get('fact_verdict')} "
          f"ledger_status={result.get('ledger_status')} writer_model={writer_model} "
          f"elapsed={result['elapsed_seconds']}s")
    return result


def main() -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    master_full_text = ab01.load_master_full_text()
    with open(f"{PHASE_A_BASELINE_DIR}/research/verified_fact_ledger.txt", encoding="utf-8") as f:
        phase_a_ledger_text = f.read()

    client = vfl01.get_client()
    cl.install(f"{OUT_DIR}/raw_usage_log_trial10.jsonl")

    print("[TRIAL-10] Reference Digest生成(Bのみ、実LLM呼び出し)開始...")
    digest_result = build_reference_digest(client)
    with open(f"{TRIAL_RESEARCH_DIR}/reference_digest_raw.json", "w", encoding="utf-8") as f:
        json.dump(digest_result, f, ensure_ascii=False, indent=2, default=str)
    reference_digest_block = build_reference_digest_block(digest_result["text"])
    with open(f"{TRIAL_RESEARCH_DIR}/reference_digest_block_used.txt", "w", encoding="utf-8") as f:
        f.write(reference_digest_block)
    print(f"[TRIAL-10] Reference Digest生成完了。model={digest_result['model']} "
          f"response_id={digest_result['response_id']}")

    phase_a = run_phase_a(master_full_text, phase_a_ledger_text, reference_digest_block)
    if not phase_a["phase_a_pass"]:
        print("[TRIAL-10] Phase Aで意図しない差分を検出したため、Phase Bへ進まずSTOPします。")
        return {"phase_a": phase_a, "phase_b": None, "status": "STOP_PHASE_A_UNEXPECTED_DIFF"}

    phase_b = {}
    for variant in ["A", "B"]:
        phase_b[variant] = run_pattern(client, phase_a["templates"][variant], master_full_text,
                                        "b1b", variant, 1)

    with open(f"{OUT_DIR}/trial10_summary.json", "w", encoding="utf-8") as f:
        json.dump({
            "phase_a": phase_a["results"],
            "phase_b": {v: {k: val for k, val in r.items() if k != "article_text"}
                        for v, r in phase_b.items()},
        }, f, ensure_ascii=False, indent=2, default=str)

    print(f"[TRIAL-10] 完了。summary -> {OUT_DIR}/trial10_summary.json")
    return {"phase_a": phase_a, "phase_b": phase_b, "status": "DONE"}


if __name__ == "__main__":
    main()

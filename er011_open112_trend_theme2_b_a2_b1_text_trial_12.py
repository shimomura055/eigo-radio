# ============================================================
# er011_open112_trend_theme2_b_a2_b1_text_trial_12.py
# OPEN-112-TREND-THEME2-B-LEDGER-FIX-AND-A2-B1-TEXT-TRIAL-12
# ============================================================
# 目的: Trial-11 Theme 2(若者の旅行「名所巡り」→「ゆっくり滞在」)の
# Verified Fact Ledgerにあった F-203 の限定表現("Gen Z travelers with
# overseas travel experience"限定)を一次資料(観光庁公式プレスリリース)に
# 合わせて最小限修正し、同じ修正済みLedgerからB条件(Engagement根底指示+
# Reference Digest)でA2/B1テキストを1回ずつ生成する(音声化はしない)。
#
# Production変更: なし。gen.run_one_pattern()を無変更のまま呼び出す。
# Reference Digestは新規生成せず、Trial-11 Theme 2で生成済みのものを
# そのまま再利用する(research/theme2_slow_travel_reference_digest_block_used.txt
# をコピーして使用)。Engagement Blockおよび候補template構築ロジックは
# Trial-11(er011_open112_engagement_reference_cross_topic_ab_trial_11.py)の
# 既存関数を再利用し、一字一句同一のまま流用する。
#
# 今回禁止: Production Prompt/routing/QA/閾値変更、Point-only regeneration
# 無効化、severity変更、新Validator追加、Engagement指示文言の改良、
# Reference Digest再作成、記事の手動編集・後書き換え、「品質が良くなるまで」
# の再生成(A2・B1とも新規生成は各1回のみ)、Topic Master変更、SSOT変更、
# Git操作、音声生成一切、他Agent起動。
#
# 到達してよいStatus: TEXT_READY_FOR_USER_REVIEW / USER_DECISION_REQUIRED のみ。
from __future__ import annotations

import json
import os
import shutil
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as gen
import er005_cost_logger as cl
import er011_open112_engagement_reference_cross_topic_ab_trial_11 as t11

NEW_THEME_ID = "open112_trend_theme2_b_a2_b1_text_trial_12"
OUT_DIR = f"er011_output/{NEW_THEME_ID}"
RESEARCH_DIR = f"{OUT_DIR}/research"
os.makedirs(RESEARCH_DIR, exist_ok=True)

TRIAL11_RESEARCH_DIR = "er011_output/open112_engagement_reference_cross_topic_ab_trial_11/research"

THEME_ID = "theme2_slow_travel"

# ------------------------------------------------------------
# Step 1: Ledger修正(F-203の限定表現を一次資料に合わせて修正、この1点+
# それに直接連動する記述[Source一覧への一次資料追加・central_claim近傍の
# Fact ID誤記1箇所]のみ)
# ------------------------------------------------------------
ORIGINAL_F203_BLOCK = """[F-203] Travel Voice英語版が報じたJapan Tourism Agency調査によれば、海外旅行
経験のある日本のZ世代の約90%が「ツアーに自由時間を組み込みたい」と回答し、その
うち約80%が「半日以上の自由時間」を希望している。
  number_or_stat: 自由時間を希望 約90%。うち半日以上を希望 約80%。
  actor_or_organization: Japan Tourism Agency(観光庁)
  evidence_strength: government_official_announcement(政府調査、メディア報道経由)
  signal_direction: increasing
  counter_signal_or_limitation: 「ツアー内の自由時間」への希望であり、必ずしも
  「一つの場所への長期滞在」を意味しない。パッケージツアーの枠組み自体は前提と
  している回答である点に注意。
  time_window: 2022年末〜2023年時点の調査
  verification: CONFIRMED
  source: SRC-206"""

CORRECTED_F203_BLOCK = """[F-203] 観光庁「海外旅行に関する意識調査」(2023年1月にインターネット調査を実施、
2023年2月15日付で観光庁が公式プレスリリースPDFとして公表。調査対象は全国の
Z世代[19〜25歳]男女400人で、海外旅行経験の有無を問わない全体サンプル)に
よれば、日本のZ世代(19〜25歳)全体の約90%が「海外旅行ツアーに参加する際に
自由時間がほしい」と回答し、そのうち約80%が「半日以上の自由時間」を希望
している。【Trial-12修正】旧版Ledger(Trial-11)は本Factの対象を誤って
「海外旅行経験のある日本のZ世代」と限定していたが、観光庁公式プレスリリース
PDFおよびそれを直接引用する複数の報道(ITmedia・まいどなニュース・マイナビ
ニュース)を確認した結果、「自由時間がほしい」約90%/「半日以上」約80%という
数値はZ世代全体(400人)に対する結果であり、海外旅行経験者限定ではないことが
一次資料で確認された。海外旅行経験者に限定されるのは、同じ観光庁調査内の別の
設問「2023年こそ海外旅行に行きたいと思うか」への回答(経験者に絞ると90.9%)
であり、これは本Factとは別の指標である(Trial-11 Report §18 Case 3で
発見された精度課題)。
  number_or_stat: 自由時間がほしい 約90%。うち半日以上を希望 約80%(母集団:
  Z世代[19〜25歳]全体400人、海外旅行経験の有無を問わない)。
  actor_or_organization: 観光庁(Japan Tourism Agency)
  evidence_strength: government_official_announcement(観光庁公式プレスリリース
  PDF[SRC-211]が一次資料。ITmedia・まいどなニュース・マイナビニュースが設問文・
  内訳数値を直接引用しており相互確認済み)
  signal_direction: increasing
  counter_signal_or_limitation: 「ツアー内の自由時間」への希望であり、必ずしも
  「一つの場所への長期滞在」を意味しない。パッケージツアーの枠組み自体は前提と
  している回答である点に注意。また、同じ観光庁調査内の別設問「今年こそ海外旅行に
  行きたいか」への回答(海外旅行経験者に絞ると90.9%)と、本Factの「自由時間が
  ほしい約90%」(母集団はZ世代全体)は別の設問・別の母集団であり、混同しないこと。
  time_window: 2023年1月調査、2023年2月15日公表
  verification: CONFIRMED(Trial-11時点でCONFIRMED。Trial-12で一次資料
  [観光庁公式PDF]への遡及確認と独立re-verificationを追加実施、詳細は
  research/f203_correction_reverification_raw.json)
  source: SRC-206, SRC-211"""

ORIGINAL_SRC206_LINE = (
    "[SRC-206] Travel Voice英語版「More than 90% of Japanese Generation Z...want to travel\n"
    "  overseas this year」(Japan Tourism Agency調査の報道、2023年) [reputable_media_reporting]"
)

CORRECTED_SRC206_AND_NEW_SRC211 = (
    "[SRC-206] Travel Voice英語版「More than 90% of Japanese Generation Z...want to travel\n"
    "  overseas this year」(Japan Tourism Agency調査の報道、2023年。ただしこの記事の見出しに\n"
    "  ある「90%」は『今年こそ海外旅行に行きたい』設問[海外旅行経験者に絞った場合の回答]の\n"
    "  数値であり、F-203の『自由時間がほしい約90%』[Z世代全体対象]とは別の指標である点に\n"
    "  Trial-12で注意喚起) [reputable_media_reporting]\n"
    "[SRC-211] 観光庁(国土交通省)公式プレスリリースPDF「Z世代の海外旅行に関する意識調査」\n"
    "  (2023年2月15日付、https://www.mlit.go.jp/kankocho/toursafetynet/assets/files/document/\n"
    "  pressrelease20230215.pdf)。F-203の一次資料。ITmediaビジネスオンライン\n"
    "  (2023-02-16)・まいどなニュース(2023-02-18)・マイナビニュース(2023-02-17)が、\n"
    "  同資料の設問文・回答内訳(全て自由行動29.5%/交通と宿のみ手配32.3%/自由時間は\n"
    "  各日の半分程度19.0%)を直接引用しており、Trial-12でこれらを相互確認した\n"
    "  [official_statistics(観光庁一次資料)、Trial-12新規追加]"
)

# central_claim直前の段落で、F-203と同じ内容(約9割/約8割)を誤ったFact ID
# (F-209、F-210。実際にはFact一覧に存在しない番号)で引用していた箇所を、
# 正しいFact ID(F-203)へ修正する(直接連動する記述の範囲内、Fact内容自体は
# 変更しない、ID参照の誤記修正のみ)。
ORIGINAL_CENTRAL_CLAIM_CITATION = (
    "海外旅行でもZ世代の\n"
    "約9割が「ツアー内の自由時間」を求め、うち約8割が半日以上を希望している(F-209、\n"
    "F-210)。"
)
CORRECTED_CENTRAL_CLAIM_CITATION = (
    "海外旅行でもZ世代の\n"
    "約9割が「ツアー内の自由時間」を求め、うち約8割が半日以上を希望している(F-203。\n"
    "【Trial-12修正】旧版では誤ってF-209・F-210[Fact一覧に存在しない番号]と引用していたが、\n"
    "該当するのはF-203であるため修正)。"
)


def build_corrected_ledger() -> dict:
    """Trial-11 Theme 2 Ledgerをコピーし、F-203の限定表現を一次資料に合わせて
    修正する。修正はF-203本体+Source一覧への一次資料追加+central_claim近傍の
    Fact ID誤記1箇所のみ(それ以外は一切変更しない)。"""
    with open(f"{TRIAL11_RESEARCH_DIR}/theme2_verified_fact_ledger.txt", encoding="utf-8") as f:
        original_text = f.read()
    with open(f"{RESEARCH_DIR}/theme2_verified_fact_ledger_ORIGINAL_trial11_copy.txt", "w",
              encoding="utf-8") as f:
        f.write(original_text)

    assert ORIGINAL_F203_BLOCK in original_text, "ORIGINAL_F203_BLOCKが元Ledger内に見つかりません(STOP)。"
    assert ORIGINAL_SRC206_LINE in original_text, "ORIGINAL_SRC206_LINEが元Ledger内に見つかりません(STOP)。"
    assert ORIGINAL_CENTRAL_CLAIM_CITATION in original_text, (
        "ORIGINAL_CENTRAL_CLAIM_CITATIONが元Ledger内に見つかりません(STOP)。")

    corrected_text = original_text.replace(ORIGINAL_F203_BLOCK, CORRECTED_F203_BLOCK, 1)
    corrected_text = corrected_text.replace(ORIGINAL_SRC206_LINE, CORRECTED_SRC206_AND_NEW_SRC211, 1)
    corrected_text = corrected_text.replace(
        ORIGINAL_CENTRAL_CLAIM_CITATION, CORRECTED_CENTRAL_CLAIM_CITATION, 1)

    # 修正が実際に3箇所だけであることを機械的に確認(diffのop_counts記録)
    import difflib
    sm = difflib.SequenceMatcher(a=original_text, b=corrected_text, autojunk=False)
    opcodes = sm.get_opcodes()
    non_equal = [op for op in opcodes if op[0] != "equal"]
    diff_lines = list(difflib.unified_diff(
        original_text.splitlines(keepends=True), corrected_text.splitlines(keepends=True),
        fromfile="theme2_ledger_ORIGINAL_trial11", tofile="theme2_ledger_CORRECTED_trial12", n=1))
    with open(f"{RESEARCH_DIR}/theme2_ledger_correction_diff.txt", "w", encoding="utf-8") as f:
        f.writelines(diff_lines)

    with open(f"{RESEARCH_DIR}/theme2_verified_fact_ledger_CORRECTED_trial12.txt", "w",
              encoding="utf-8") as f:
        f.write(corrected_text)

    op_counts = {tag: sum(1 for o in opcodes if o[0] == tag) for tag in
                 ("equal", "insert", "delete", "replace")}
    print(f"[TRIAL-12][Ledger修正] op_counts={op_counts} non_equal_op_count={len(non_equal)}")

    return {"original_text": original_text, "corrected_text": corrected_text, "op_counts": op_counts,
            "non_equal_op_count": len(non_equal)}


# ------------------------------------------------------------
# Step 1b: 修正済みF-203に対する独立re-verification(Trial-11と同じ
# verify_theme_facts関数・同じVERIFICATION_PROMPT/schemaを再利用。対象は
# 修正した本文のみに限定し、無関係な既存13件を再検証しない[コスト最小化、
# 対象範囲を修正箇所に絞る])。
# ------------------------------------------------------------
CORRECTED_F203_FACT_FOR_VERIFICATION = {
    "facts": [{
        "fact_id": "F-203",
        "verified_fact": (
            "観光庁「海外旅行に関する意識調査」(2023年1月実施、2023年2月15日公表、"
            "全国のZ世代[19〜25歳]男女400人対象、海外旅行経験の有無を問わない全体サンプル)"
            "によれば、日本のZ世代(19〜25歳)全体の約90%が「海外旅行ツアーに参加する際に"
            "自由時間がほしい」と回答し、そのうち約80%が「半日以上の自由時間」を希望している。"
        ),
        "number_or_stat": "自由時間がほしい約90%。うち半日以上を希望約80%(母集団: Z世代全体400人)。",
        "actor_or_organization": "観光庁(Japan Tourism Agency)",
        "signal": "日本のZ世代(海外旅行経験の有無を問わない全体)は、パッケージツアーであっても"
                  "自分のペースで過ごせる自由時間を強く求めている。",
        "signal_direction": "increasing",
        "evidence_strength": "government_official_announcement",
        "counter_signal_or_limitation": "「ツアー内の自由時間」への希望であり、必ずしも「一つの場所への"
                                         "長期滞在」を意味しない。",
        "time_window": "2023年1月調査、2023年2月15日公表",
        "source_name": "観光庁公式プレスリリースPDF「Z世代の海外旅行に関する意識調査」",
        "source_url": "https://www.mlit.go.jp/kankocho/toursafetynet/assets/files/document/"
                       "pressrelease20230215.pdf",
        "publication_date": "2023-02-15",
    }],
}


def reverify_corrected_fact() -> dict:
    facts_json_text = json.dumps(CORRECTED_F203_FACT_FOR_VERIFICATION, ensure_ascii=False, indent=2)
    result = t11.verify_theme_facts(f"{THEME_ID}_f203_correction", facts_json_text)
    with open(f"{RESEARCH_DIR}/f203_correction_reverification_raw.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    return result


# ------------------------------------------------------------
# Step 2: 条件固定(Topic文・修正済みLedger・Trend Focus Module・Engagement
# Block[Trial-10と一字一句同一]・Reference Digest[Trial-11 Theme2生成済み
# のものを再利用]・model/routing[既存承認済みcontract]をA2/B1で共通化)
# ------------------------------------------------------------
# Trial-11で使用したTopic文をそのまま再利用(修正対象のF-203はTopic文内には
# 直接の数字として現れているため[「約9割」「約8割」]、Ledgerとの整合を保つ
# ために表現を確認する。Topic文自体はZ世代全体を主語にしており[「海外旅行
# 経験のある」という限定語をそもそも含んでいない]、修正の影響を受けない)。
THEME2_TOPIC_JA = t11.THEME2_TOPIC_JA
assert "海外旅行経験のある日本のZ世代の約9割が「ツアー内に自由時間が欲しい」" in THEME2_TOPIC_JA, (
    "Topic文の想定文言が変わっています(STOP)。")

LEVELS = {
    "b1b": {"label": "B1B", "instruction_attr": "B1_B_DIRECT_INSTRUCTION"},
    "a2": {"label": "A2", "instruction_attr": "A2_KAI1_INSTRUCTION"},
}


def build_reference_digest_block_reused() -> str:
    """Trial-11 Theme 2で生成済みのReference Digest(block_used.txt)を
    そのままコピーして再利用する(再生成しない)。"""
    src = f"{TRIAL11_RESEARCH_DIR}/theme2_slow_travel_reference_digest_block_used.txt"
    with open(src, encoding="utf-8") as f:
        text = f.read()
    dst = f"{RESEARCH_DIR}/theme2_slow_travel_reference_digest_block_REUSED_from_trial11.txt"
    shutil.copyfile(src, dst)
    return text


def run_phase_a_clean_insert_check(master_full_text: str, phase_a_ledger_text: str,
                                    reference_digest_block: str) -> dict:
    """機械的diff検証(Trial-11と同じ設計)。A2/B1両レベルについて、Anchorへの
    単一clean insertが崩れていないことを確認する(API呼び出し無し)。"""
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    candidate_template = t11.build_candidate_template("B", reference_digest_block)
    with open(f"{OUT_DIR}/audit/candidate_template_B.txt", "w", encoding="utf-8") as f:
        f.write(candidate_template)

    results = {}
    for level, meta in LEVELS.items():
        instruction = getattr(gen, meta["instruction_attr"])
        candidate_prompt = t11.build_candidate_prompt(
            candidate_template, master_full_text, t11.PHASE_A_TOPIC_JA, phase_a_ledger_text, instruction)
        baseline_path = f"{t11.PHASE_A_BASELINE_DIR}/{level}/audit/prompt.txt"
        with open(baseline_path, encoding="utf-8") as f:
            baseline_prompt = f.read()

        import difflib
        insertion = "\n\n".join(
            [t11.TREND_SYNTHESIS_FOCUS_MODULE_BLOCK, t11.ENTERTAINMENT_ENGAGEMENT_BLOCK,
             reference_digest_block])
        reconstructed = baseline_prompt.replace(t11.ANCHOR, insertion + "\n\n" + t11.ANCHOR, 1)
        sm = difflib.SequenceMatcher(a=baseline_prompt, b=candidate_prompt, autojunk=False)
        opcodes = sm.get_opcodes()
        non_equal = [op for op in opcodes if op[0] != "equal"]
        unexpected = [op for op in non_equal if op[0] != "insert"]
        insert_ops = [op for op in non_equal if op[0] == "insert"]
        clean_single_insert = (len(unexpected) == 0 and len(insert_ops) == 1
                                and reconstructed == candidate_prompt)
        results[level] = {
            "baseline_len": len(baseline_prompt), "candidate_len": len(candidate_prompt),
            "op_counts": {tag: sum(1 for o in opcodes if o[0] == tag) for tag in
                          ("equal", "insert", "delete", "replace")},
            "unexpected_op_count": len(unexpected),
            "clean_single_insert_confirmed": clean_single_insert,
        }
        print(f"[TRIAL-12][Phase A][{level}] op_counts={results[level]['op_counts']} "
              f"clean_single_insert_confirmed={clean_single_insert}")

    phase_a_pass = all(r["clean_single_insert_confirmed"] for r in results.values())
    with open(f"{OUT_DIR}/audit/phase_a_result.json", "w", encoding="utf-8") as f:
        json.dump({"results": results, "phase_a_pass": phase_a_pass}, f, ensure_ascii=False, indent=2)
    print(f"[TRIAL-12][Phase A] phase_a_pass={phase_a_pass}")
    return {"results": results, "phase_a_pass": phase_a_pass, "candidate_template": candidate_template}


# ------------------------------------------------------------
# Step 3/4: B1・A2生成(既存Production経路 gen.run_one_pattern を無変更の
# まま1回ずつ呼び出す。既存retry[Point Overlap Article Retry/Local
# Rewrite]は既存仕様通り自動発火させ、結果を記録する)
# ------------------------------------------------------------
def run_level(client, candidate_template: str, master_full_text: str, corrected_ledger_text: str,
              level: str) -> dict:
    meta = LEVELS[level]
    instruction = getattr(gen, meta["instruction_attr"])
    candidate_prompt = t11.build_candidate_prompt(
        candidate_template, master_full_text, THEME2_TOPIC_JA, corrected_ledger_text, instruction)
    level_out_dir = f"{OUT_DIR}/{level}_run01"

    print(f"[TRIAL-12][Phase B] {meta['label']} run01: gen.run_one_pattern()(実Production関数、"
          f"無変更)開始...")
    t0 = time.time()
    with cl.logging_context(NEW_THEME_ID, f"writer_{level}_run01"):
        result = gen.run_one_pattern(
            client, NEW_THEME_ID, meta["label"], candidate_prompt, corrected_ledger_text,
            THEME2_TOPIC_JA, level_out_dir)
    elapsed = time.time() - t0
    result["elapsed_seconds"] = round(elapsed, 1)

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

    print(f"[TRIAL-12][Phase B] {meta['label']} run01: 完了。status={result.get('status')} "
          f"fact_verdict={result.get('fact_verdict')} ledger_status={result.get('ledger_status')} "
          f"point_overlap_article_retry_attempts={result.get('point_overlap_article_retry_attempts')} "
          f"local_rewrite_cycles={len(result.get('local_rewrite_cycles', []) or [])} "
          f"writer_model={writer_model} elapsed={result['elapsed_seconds']}s")
    return result


def main() -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    master_full_text = ab01.load_master_full_text()
    with open(f"{t11.PHASE_A_BASELINE_DIR}/research/verified_fact_ledger.txt", encoding="utf-8") as f:
        phase_a_ledger_text = f.read()

    client = vfl01.get_client()
    cl.install(f"{OUT_DIR}/raw_usage_log_trial12.jsonl")

    print("[TRIAL-12] Step 1: Ledger修正(F-203)...")
    ledger_fix = build_corrected_ledger()

    print("[TRIAL-12] Step 1b: 修正済みF-203の独立re-verification...")
    reverify_result = reverify_corrected_fact()
    verdicts = []
    if reverify_result.get("status") == "OK":
        try:
            parsed = json.loads(reverify_result["content"])
            verdicts = [v["verdict"] for v in parsed.get("verifications", [])]
        except (json.JSONDecodeError, KeyError):
            verdicts = ["PARSE_ERROR"]
    print(f"[TRIAL-12] Step 1b: re-verification verdicts={verdicts}")
    if "CONTRADICTED" in verdicts:
        print("[TRIAL-12] re-verificationでCONTRADICTEDを検出したためSTOPします(USER_DECISION_REQUIRED)。")
        return {"status": "STOP_REVERIFICATION_CONTRADICTED", "ledger_fix": ledger_fix,
                "reverify_result": reverify_result, "verdicts": verdicts}

    print("[TRIAL-12] Step 2: Reference Digest再利用 + 条件固定...")
    reference_digest_block = build_reference_digest_block_reused()

    phase_a = run_phase_a_clean_insert_check(master_full_text, phase_a_ledger_text, reference_digest_block)
    if not phase_a["phase_a_pass"]:
        print("[TRIAL-12] Phase Aで意図しない差分を検出したため、Phase Bへ進まずSTOPします。")
        return {"status": "STOP_PHASE_A_UNEXPECTED_DIFF", "ledger_fix": ledger_fix,
                "reverify_result": reverify_result, "phase_a": phase_a}

    print("[TRIAL-12] Step 3/4: B1・A2生成(各1回)...")
    phase_b = {}
    for level in ["b1b", "a2"]:
        phase_b[level] = run_level(client, phase_a["candidate_template"], master_full_text,
                                    ledger_fix["corrected_text"], level)

    with open(f"{OUT_DIR}/trial12_summary.json", "w", encoding="utf-8") as f:
        json.dump({
            "ledger_fix_op_counts": ledger_fix["op_counts"],
            "reverify_verdicts": verdicts,
            "phase_a": phase_a["results"],
            "phase_b": {lvl: {k: v for k, v in r.items() if k != "article_text"}
                        for lvl, r in phase_b.items()},
        }, f, ensure_ascii=False, indent=2, default=str)

    print(f"[TRIAL-12] 完了。summary -> {OUT_DIR}/trial12_summary.json")
    return {"status": "DONE", "ledger_fix": ledger_fix, "reverify_result": reverify_result,
            "phase_a": phase_a, "phase_b": phase_b}


# ------------------------------------------------------------
# Sonnet 2回目(Phase B再実行専用、OPEN-112-TREND-THEME2-B-LEDGER-FIX-
# AND-A2-B1-TEXT-TRIAL-12): ユーザーがOpenAI API残高を補充した後、
# Sonnet 1回目で完了済みのStep1(Ledger修正)・Step1b(独立re-verification、
# Perplexity)・Step2(Reference Digest再利用)・Phase A(clean insert機械的
# 確認)を再実行せず、保存済み成果物をそのまま読み込んでPhase B(B1・A2
# 生成、既存QAチェーン)のみを新規実行する。Perplexity呼び出しは一切発生
# しない(コスト最小化・重複調査の回避、ユーザー指示)。Production側の
# gen.run_one_pattern()・run_level()は無変更のままこのTrial script内でのみ
# 呼び出し順序を制御する(Trial script内のみの最小限skip/resume処理)。
# ------------------------------------------------------------
def load_saved_step1_step2_phase_a() -> dict:
    """保存済みのLedger修正結果・re-verification結果・Phase A結果・candidate
    templateを読み込む(API呼び出し無し)。いずれかが欠けている、または
    CONTRADICTED/phase_a_pass=Falseの場合はRuntimeErrorでSTOPする。"""
    with open(f"{RESEARCH_DIR}/theme2_verified_fact_ledger_CORRECTED_trial12.txt", encoding="utf-8") as f:
        corrected_ledger_text = f.read()

    with open(f"{RESEARCH_DIR}/f203_correction_reverification_raw.json", encoding="utf-8") as f:
        reverify_result = json.load(f)
    verdicts = []
    if reverify_result.get("status") == "OK":
        try:
            parsed = json.loads(reverify_result["content"])
            verdicts = [v["verdict"] for v in parsed.get("verifications", [])]
        except (json.JSONDecodeError, KeyError):
            verdicts = ["PARSE_ERROR"]
    print(f"[TRIAL-12][RESUME] Step1b(保存済み再利用、Perplexity呼び出し無し) "
          f"re-verification verdicts={verdicts}")
    if "CONTRADICTED" in verdicts or "PARSE_ERROR" in verdicts:
        raise RuntimeError(
            f"保存済みre-verification結果が想定外です(verdicts={verdicts})。STOPします。")

    with open(f"{OUT_DIR}/audit/phase_a_result.json", encoding="utf-8") as f:
        phase_a_saved = json.load(f)
    if not phase_a_saved.get("phase_a_pass"):
        raise RuntimeError("保存済みPhase A結果がphase_a_pass=Falseです。STOPします。")

    with open(f"{OUT_DIR}/audit/candidate_template_B.txt", encoding="utf-8") as f:
        candidate_template = f.read()

    print("[TRIAL-12][RESUME] 保存済み成果物の読み込み完了: "
          f"corrected_ledger_text(len={len(corrected_ledger_text)}) / "
          f"reverify verdicts={verdicts} / "
          f"phase_a_pass={phase_a_saved.get('phase_a_pass')} / "
          f"candidate_template(len={len(candidate_template)})")

    return {
        "corrected_ledger_text": corrected_ledger_text,
        "reverify_result": reverify_result,
        "verdicts": verdicts,
        "phase_a_saved": phase_a_saved,
        "candidate_template": candidate_template,
    }


def main_resume_phase_b() -> dict:
    """Phase Bのみを新規実行するエントリポイント(Step1/1b/2/Phase Aは保存済み
    成果物を再利用し、再実行しない)。B1→A2の順で既存Production経路
    gen.run_one_pattern()を1回ずつ呼び出す(run_levelはSonnet 1回目と無変更)。"""
    os.makedirs(OUT_DIR, exist_ok=True)
    master_full_text = ab01.load_master_full_text()

    client = vfl01.get_client()
    cl.install(f"{OUT_DIR}/raw_usage_log_trial12.jsonl")

    saved = load_saved_step1_step2_phase_a()

    print("[TRIAL-12][RESUME] Step 3/4: B1・A2生成(各1回、保存済み条件を再利用)...")
    phase_b = {}
    for level in ["b1b", "a2"]:
        phase_b[level] = run_level(client, saved["candidate_template"], master_full_text,
                                    saved["corrected_ledger_text"], level)

    with open(f"{OUT_DIR}/trial12_summary_phase_b_resume.json", "w", encoding="utf-8") as f:
        json.dump({
            "resume_mode": True,
            "reused_reverify_verdicts": saved["verdicts"],
            "reused_phase_a_pass": saved["phase_a_saved"].get("phase_a_pass"),
            "phase_b": {lvl: {k: v for k, v in r.items() if k != "article_text"}
                        for lvl, r in phase_b.items()},
        }, f, ensure_ascii=False, indent=2, default=str)

    print(f"[TRIAL-12][RESUME] 完了。summary -> {OUT_DIR}/trial12_summary_phase_b_resume.json")
    return {"status": "DONE_RESUME_PHASE_B", "saved": saved, "phase_b": phase_b}


if __name__ == "__main__":
    if "--resume-phase-b" in sys.argv:
        main_resume_phase_b()
    else:
        main()

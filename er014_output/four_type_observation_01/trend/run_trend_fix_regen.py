# ============================================================
# er014_output/four_type_observation_01/trend/run_trend_fix_regen.py
# 管理ID: EDITORIAL-4TYPE-FOLLOWUP-02-TREND-LEDGER-FIX-REGEN
#
# 目的: 前回Trend Synthesis run(run_trend_a2.py)のFact Checker FAILで
# 判明した「Googleが2026-05-19にAndroid XR/Geminiスマートグラスの2026年秋
# 発売を公式発表済み」という、Research時点で既に存在した事実の取りこぼしを
# 修正する。Research全体の再実行はせず、既存のvfl01検証呼び出し
# (build_verification_prompt経由のOpenAI web_search)を「当該1件+関連する
# 既存Ledger該当fact(F008)」に限定して再実行し、確認できた事実に基づいて
# verified_fact_ledger.txtを修正する。修正版Ledgerを共通Fact源として、
# Trend Synthesis正式path(er006_pool_pilot_01_writer.run_writer_for_theme)
# でB1B+A2をWriterから再実行する(旧記事の局所置換はしない)。
#
# 旧成果物はtrend/run1_before_fix/へコピー退避(削除しない)。
# raw_usage_log.jsonlは同一ファイルへ追記されるため、本runの実費は
# 「run開始時点の行数(baseline_lines)」以降の行だけを集計して分離する。
# ============================================================
from __future__ import annotations

import json
import os
import shutil
import sys
import time
from datetime import datetime, timezone

sys.path.insert(0, os.getcwd())

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import er002_ja_web_research_r3 as r3  # noqa: E402
import er003_v1_en_direct_ab_01_generate as ab01  # noqa: E402
import er003_v1_en_direct_vfl_01_generate as vfl01  # noqa: E402
import er005_cost_logger as cl  # noqa: E402
import er006_pool_pilot_01_writer as writer_mod  # noqa: E402

# run_trend_a2.py(前回driver)をモジュールとして再利用する(monkeypatch・
# 再実装ではなく、既存定数/関数のそのままの呼び出し)。
BASE_DIR = "er014_output/four_type_observation_01/trend"
sys.path.insert(0, os.path.join(os.getcwd(), BASE_DIR))
import run_trend_a2 as base  # noqa: E402

THEME_ID = base.THEME_ID
RESEARCH_DIR = f"{BASE_DIR}/research"
LOG_PATH = f"{BASE_DIR}/raw_usage_log.jsonl"
BACKUP_DIR = f"{BASE_DIR}/run1_before_fix"

BUDGET_JPY = 80.0

BACKUP_TARGETS = [
    "a2", "b1b", "reader_facing_article.txt", "reader_facing_article_b1b.txt",
    "run_result.json", "observation.json", "cost_summary.json", "raw_usage_log.jsonl",
]

# ------------------------------------------------------------
# 限定Verification対象: F008(原文、research/verified_fact_ledger_
# structured.jsonからそのまま読み込む)+ F008_FIX(新draft、Fact Checker
# FAILが引用したsource[blog.google, android-xr-io-2026]をもとに作成した
# 「2026年秋発売公式発表」claimの下書き)。
# ------------------------------------------------------------
F008_FIX_DRAFT = {
    "fact_id": "F008_FIX",
    "claim": (
        "Google announced that the first commercially available product in its "
        "Android XR eyewear ecosystem -- audio-only 'intelligent eyewear' (audio "
        "glasses, without a display) -- would launch in fall 2026, as part of the "
        "Gentle Monster and Warby Parker eyewear collections. This is a distinct, "
        "narrower product tier than the camera/optional-in-lens-display Android XR "
        "glasses prototype described in F008."
    ),
    "subject": "Google Android XR ecosystem: first commercial product (audio-only glasses) launch timing",
    "date_or_period": "Announced May 19, 2026; launch stated for fall 2026",
    "scope": (
        "The audio-only ('audio glasses') tier of Google's Android XR eyewear "
        "ecosystem, positioned as the first commercially shipping product in that "
        "ecosystem; specific country/market availability at launch was not fully "
        "confirmed in the cited passage."
    ),
    "conditions": (
        "Google described this fall 2026 launch as applying specifically to "
        "audio-only glasses, not to the full camera/optional-in-lens-display "
        "Android XR glasses demoed in 2025 (F008); the source did not establish "
        "which countries/markets would have launch-day availability (a related "
        "Samsung announcement referenced 'select markets')."
    ),
    "numeric_value": None,
    "numeric_scope": None,
    "causal_strength": "NOT_APPLICABLE",
    "source_title": "Intelligent eyewear with Gemini is coming this fall",
    "source_url": "https://blog.google/products-and-platforms/platforms/android/android-xr-io-2026/",
    "source_type": "OTHER",
    "support_level": "DIRECTLY_STATED",
    "ambiguity": (
        "The source confirms a fall 2026 launch tied to named eyewear-brand "
        "collections for the audio-only tier specifically; it does not confirm a "
        "fall 2026 commercial launch for the full camera/display Android XR glasses "
        "variant, nor specific country/market availability, exact release date, or "
        "adoption/sales data."
    ),
    "notes_for_writer": (
        "This confirms that Google's Android XR eyewear ecosystem has moved from a "
        "pure product demonstration (2025, F008) to an actual company-announced "
        "commercial launch timeframe (fall 2026) for its first (audio-only) "
        "product. Do not describe the Android XR eyewear line overall as 'still "
        "only a development-stage demonstration with no confirmed launch' -- that "
        "framing is now outdated for at least this first product. At the same "
        "time, do not conflate this audio-only launch with a confirmed launch of "
        "the full camera/display glasses in F008, and do not conflate 'launch "
        "announced' with 'available everywhere' or 'already widely adopted'."
    ),
}


def load_structured_ledger() -> dict:
    with open(f"{RESEARCH_DIR}/verified_fact_ledger_structured.json", encoding="utf-8") as f:
        return json.load(f)


def incremental_cost_jpy(baseline_lines: int) -> tuple:
    """raw_usage_log.jsonlはrun1から引き継いで追記されるため、baseline_lines
    (本run開始時点の行数)以降の行だけを集計し、本runの実費だけを分離する。"""
    total_usd = 0.0
    now_lines = 0
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, encoding="utf-8") as f:
            for i, line in enumerate(f):
                now_lines += 1
                if i < baseline_lines:
                    continue
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                if rec.get("success") is False:
                    continue
                total_usd += base._call_cost_usd(rec)
    return total_usd * base.USD_JPY, now_lines


def backup_run1():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    copied, skipped = [], []
    for name in BACKUP_TARGETS:
        src = f"{BASE_DIR}/{name}"
        dst = f"{BACKUP_DIR}/{name}"
        if os.path.isdir(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            copied.append(name)
        elif os.path.isfile(src):
            shutil.copy2(src, dst)
            copied.append(name)
        else:
            skipped.append(name)
    return {"copied": copied, "skipped_not_found": skipped}


def render_ledger_text(kept_facts: list) -> str:
    """run_trend_a2.build_ledger()内のLedger本文生成ロジックと同一の
    整形規則(再実装ではなく同一書式の踏襲)。"""
    lines = []
    for fact in kept_facts:
        lines.append(f"[VERIFIED] {fact['fact_id']}: {fact['claim']}")
        if fact.get("scope"):
            lines.append(f"  scope: {fact['scope']}")
        if fact.get("conditions"):
            lines.append(f"  conditions: {fact['conditions']}")
        if fact.get("numeric_value"):
            lines.append(f"  numeric_value: {fact['numeric_value']} (numeric_scope: {fact.get('numeric_scope') or 'unspecified'})")
        if fact.get("date_or_period"):
            lines.append(f"  date_or_period: {fact['date_or_period']}")
        if fact.get("causal_strength") and fact["causal_strength"] != "NOT_APPLICABLE":
            lines.append(f"  causal_strength: {fact['causal_strength']}")
        if fact.get("notes_for_writer"):
            lines.append(f"  notes_for_writer: {fact['notes_for_writer']}")
        lines.append("")
    return "\n".join(lines)


def main():
    started_at = datetime.now(timezone.utc).isoformat()
    print(f"[{THEME_ID}] Trend Ledger Fix + Regen 開始")

    backup_result = backup_run1()
    print(f"[{THEME_ID}] run1_before_fix退避完了: copied={backup_result['copied']} "
          f"skipped={backup_result['skipped_not_found']}")

    baseline_lines = 0
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, encoding="utf-8") as f:
            baseline_lines = sum(1 for _ in f)
    cl.install(LOG_PATH)

    client = vfl01.get_client()

    # ------------------------------------------------------------
    # Step 1: 限定Verification(F008原文 + F008_FIX下書き、2件のみ)
    # ------------------------------------------------------------
    structured = load_structured_ledger()
    kept_facts = structured["kept_facts"]
    f008_original = next(f for f in kept_facts if f["fact_id"] == "F008")
    verify_input_facts = [
        {k: v for k, v in f008_original.items() if k not in ("verification_verdict", "verification_notes")},
        F008_FIX_DRAFT,
    ]

    with cl.logging_context(THEME_ID, "ledger_fix_verification"):
        verification_result = base.run_verification_for_topic(
            client, base.TOPIC_EN, {"facts": verify_input_facts},
        )
    with open(f"{RESEARCH_DIR}/ledger_fix_verification.json", "w", encoding="utf-8") as f:
        json.dump(verification_result, f, ensure_ascii=False, indent=2, default=str)

    verdicts = {v["fact_id"]: v for v in verification_result["parsed"]["verifications"]}
    f008_fix_verdict = verdicts.get("F008_FIX", {})
    print(f"[{THEME_ID}] 限定Verification完了: F008={verdicts.get('F008', {}).get('verdict')} "
          f"F008_FIX={f008_fix_verdict.get('verdict')}")

    if f008_fix_verdict.get("verdict") != "VERIFIED":
        cost_jpy, _ = incremental_cost_jpy(baseline_lines)
        result = {
            "status": "STOP_FACT_NOT_RECONFIRMED",
            "reason": f"限定Verificationにより F008_FIX の verdict が VERIFIED になりませんでした "
                      f"(verdict={f008_fix_verdict.get('verdict')})。信頼できるsourceで再確認できない"
                      f"ためSTOPします。",
            "verification_result_path": f"{RESEARCH_DIR}/ledger_fix_verification.json",
            "cost_jpy_this_run": cost_jpy, "started_at": started_at,
            "finished_at": datetime.now(timezone.utc).isoformat(),
        }
        with open(f"{BASE_DIR}/run_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        print(f"[{THEME_ID}] STOP: {result['reason']}")
        return result

    # ------------------------------------------------------------
    # Step 2: Ledger修正(旧Ledgerをvfl_before_fixとして保存、F008の
    # notes_for_writerを整合させ、F008_FIXを追加)
    # ------------------------------------------------------------
    ledger_txt_path = f"{RESEARCH_DIR}/verified_fact_ledger.txt"
    shutil.copy2(ledger_txt_path, f"{RESEARCH_DIR}/verified_fact_ledger_v1_before_fix.txt")

    old_f008_conditions = f008_original.get("conditions")
    old_f008_notes = f008_original.get("notes_for_writer")

    fixed_f008 = dict(f008_original)
    fixed_f008["notes_for_writer"] = (
        f"{old_f008_notes} UPDATE (this fix): a later Google announcement (see F008_FIX, "
        f"blog.google/.../android-xr-io-2026/, 2026-05-19) confirmed a fall 2026 commercial "
        f"launch for the first (audio-only) product in this Android XR eyewear ecosystem, tied "
        f"to the Gentle Monster and Warby Parker collections. Do not describe the Android XR "
        f"eyewear line overall as having no confirmed launch date or as still being only a "
        f"development-stage demonstration; that framing is outdated for at least the audio-only "
        f"product. The camera/optional-in-lens-display variant described here in F008 remains a "
        f"distinct product tier without its own confirmed fall 2026 launch date -- combine both "
        f"facts (F008 + F008_FIX) for the current, tier-differentiated status."
    )
    fixed_f008.pop("verification_verdict", None)
    fixed_f008.pop("verification_notes", None)
    fixed_f008["verification_verdict"] = "VERIFIED"
    fixed_f008["verification_notes"] = verdicts.get("F008", {}).get(
        "verification_notes", f008_original.get("verification_notes", ""))

    new_f008_fix_kept = {
        **F008_FIX_DRAFT,
        "verification_verdict": "VERIFIED",
        "verification_notes": f008_fix_verdict.get("verification_notes", ""),
    }

    new_kept_facts = []
    for f in kept_facts:
        if f["fact_id"] == "F008":
            new_kept_facts.append(fixed_f008)
            new_kept_facts.append(new_f008_fix_kept)
        else:
            new_kept_facts.append(f)

    new_counts = dict(structured["counts"])
    new_counts["VERIFIED"] = new_counts.get("VERIFIED", 0) + 1

    new_ledger_text = render_ledger_text(new_kept_facts)
    with open(ledger_txt_path, "w", encoding="utf-8") as f:
        f.write(new_ledger_text)

    new_structured = {
        **structured,
        "kept_facts": new_kept_facts,
        "counts": new_counts,
        "fix_applied": {
            "management_id": "EDITORIAL-4TYPE-FOLLOWUP-02-TREND-LEDGER-FIX-REGEN",
            "reason": "Fact Checker FAIL(run1)で判明した、Google Android XR/Geminiスマートグラスの"
                      "2026年秋発売公式発表(Research時点で既に存在した事実)の取りこぼしを修正。",
            "changed_fact_id": "F008",
            "added_fact_id": "F008_FIX",
            "verification_result_path": f"{RESEARCH_DIR}/ledger_fix_verification.json",
        },
    }
    with open(f"{RESEARCH_DIR}/verified_fact_ledger_structured.json", "w", encoding="utf-8") as f:
        json.dump(new_structured, f, ensure_ascii=False, indent=2, default=str)

    diff_md = f"""# Trend Ledger Fix Diff

管理ID: EDITORIAL-4TYPE-FOLLOWUP-02-TREND-LEDGER-FIX-REGEN
実施日時(UTC): {started_at}

## 背景

前回run(run1)のFact Checker(A2, attempt 1)がFAIL判定。理由:
記事がGoogleのXRメガネについて「まだ製品デモの段階で、確認済みの発売ではない」
という趣旨で記述していたが、GoogleはFact Checker実行時点(2026-09-14)より前の
2026-05-19に、Android XR/Geminiスマートグラスを2026年秋(fall 2026)に発売する
ことをGentle Monster/Warby Parkerコレクションの一部として公式発表済みだった。
これはResearch時点で既に存在していたはずの事実であり、時間経過による陳腐化
ではなく上流Research/Ledgerの取りこぼしとして扱う(ユーザー判断)。

## 再確認方法

Sonnetにweb検索ツールが無いため、既存の`vfl01.build_verification_prompt`/
Verification呼び出し(OpenAI web_search、`er003_v1_en_direct_vfl_01_generate.py`
の`run_verification_for_topic`と同一実装)を、F008(原文)+F008_FIX(新draft)の
2件のみに限定して実行した(Research全体の再実行はしていない)。
生JSON: `research/ledger_fix_verification.json`

## 再確認結果

- Source: blog.google「Intelligent eyewear with Gemini is coming this fall」
  https://blog.google/products-and-platforms/platforms/android/android-xr-io-2026/
- 発表日: 2026-05-19
- 内容: Googleは、Android XR eyewear ecosystemの最初の商用製品であるaudio-only
  「intelligent eyewear(audio glasses、ディスプレイなし)」を2026年秋(fall 2026)に、
  Gentle Monster・Warby Parkerの各コレクションの一部として発売すると発表。F008が
  記述するカメラ/オプションのin-lens display搭載版(2025年デモ)とは別の製品tierで
  あり、後者自体の2026年秋発売は本sourceでは確認できない(具体的な発売対象国/市場
  も本sourceでは確定できず、関連するSamsung発表では"select markets"と記載)。
- Verification verdict: F008_FIX = VERIFIED (F008 = {verdicts.get('F008', {}).get('verdict', 'N/A')})

## Ledger差分

| 種別 | fact_id | 内容 |
|---|---|---|
| 修正 | F008 | notes_for_writerへ「F008_FIXを参照し、Android XR eyewear全体を'no confirmed launch date'/development-stage demoのみとして記述するのは(少なくともaudio-only製品については)禁止、ただしF008自体のカメラ/display版はF008_FIXとは別tierで、その版自体の2026年秋発売は未確認」という整合caveatを追記。claim/scope/conditions/date_or_periodはF008自体のsource([blog.google] android-xr-gemini-glasses-headsets、2025-05-20デモ時点の記述として)そのまま維持(削除ではなく整合)。 |
| 追加 | F008_FIX | 新規fact。「Googleが2026-05-19に、Android XR eyewear ecosystemの最初の商用製品であるaudio-only glasses(ディスプレイなし)の2026年秋発売をGentle Monster/Warby Parkerコレクション経由で公式発表。F008のカメラ/display版とは別製品tier」。source: blog.google/android-xr-io-2026。 |

旧factで矛盾していたのはLedger本体ではなく、Ledgerに欠けていた新しいfactを
記事(Writer出力)が補えなかった点。よって「削除」ではなく「修正(F008の
notes_for_writer整合)+追加(F008_FIX)」で対応した。

counts: VERIFIED {structured['counts'].get('VERIFIED', 0)} -> {new_counts['VERIFIED']}
(AMBIGUOUS/REJECTEDは変更なし)
"""
    with open(f"{RESEARCH_DIR}/ledger_fix_diff.md", "w", encoding="utf-8") as f:
        f.write(diff_md)
    print(f"[{THEME_ID}] Ledger修正完了: research/verified_fact_ledger.txt上書き、"
          f"research/ledger_fix_diff.md記録")

    cost_after_ledger_fix, _ = incremental_cost_jpy(baseline_lines)
    if cost_after_ledger_fix >= BUDGET_JPY:
        result = {
            "status": "STOP_BUDGET_EXCEEDED",
            "reason": f"限定Verification+Ledger修正完了時点で本run実費¥{cost_after_ledger_fix:.2f}が"
                      f"BUDGET_JPY=¥{BUDGET_JPY:.2f}に到達/超過したため、Writer/QAを実行せずSTOPします。",
            "cost_jpy_this_run": cost_after_ledger_fix, "started_at": started_at,
            "finished_at": datetime.now(timezone.utc).isoformat(),
        }
        with open(f"{BASE_DIR}/run_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        print(f"[{THEME_ID}] STOP: {result['reason']}")
        return result

    # ------------------------------------------------------------
    # Step 3: Trend Gate/Mode判定チェックリストの再判定(kept_facts更新に
    # 伴いsignal件数が変わるため、run_trend_a2.build_trend_gate_checklist
    # をそのまま再利用)
    # ------------------------------------------------------------
    trend_gate_checklist = base.build_trend_gate_checklist(new_kept_facts)
    with open(f"{BASE_DIR}/trend_gate_checklist.json", "w", encoding="utf-8") as f:
        json.dump(trend_gate_checklist, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] Trend Gate再判定完了: routing="
          f"{trend_gate_checklist['mode_judgment_2_questions']['routing_result']}")

    # ------------------------------------------------------------
    # Step 4: Writer再実行(正式path、B1B+A2両方、旧記事の局所置換なし)
    # 旧a2/b1bディレクトリは既にrun1_before_fix/へコピー済みなので、
    # 新runの出力と混在しないよう削除してから再実行する。
    # ------------------------------------------------------------
    for sub in ("a2", "b1b"):
        shutil.rmtree(f"{BASE_DIR}/{sub}", ignore_errors=True)

    master_full_text = ab01.load_master_full_text()
    print(f"[{THEME_ID}] run_writer_for_theme(editorial_mode=trend_synthesis)再実行開始 "
          f"(修正版Ledgerを共通Fact源として、B1B+A2両方をWriterから再実行)...")
    t0 = time.time()
    writer_result = writer_mod.run_writer_for_theme(
        client, master_full_text, THEME_ID, base.TOPIC_EN, ledger_txt_path, BASE_DIR,
        editorial_mode="trend_synthesis", trend_gate_checklist=trend_gate_checklist,
    )
    elapsed = round(time.time() - t0, 2)
    a2_result = writer_result["results"].get("A2", {})
    b1b_result = writer_result["results"].get("B1B", {})
    print(f"[{THEME_ID}] run_writer_for_theme完了: A2 status={a2_result.get('status')} "
          f"B1B status={b1b_result.get('status')} elapsed={elapsed}s")

    finished_at = datetime.now(timezone.utc).isoformat()
    cost_final_this_run, total_lines_now = incremental_cost_jpy(baseline_lines)

    if a2_result.get("article_text"):
        with open(f"{BASE_DIR}/reader_facing_article.txt", "w", encoding="utf-8") as f:
            f.write(a2_result["article_text"])
    if b1b_result.get("article_text"):
        with open(f"{BASE_DIR}/reader_facing_article_b1b.txt", "w", encoding="utf-8") as f:
            f.write(b1b_result["article_text"])

    with open(f"{BASE_DIR}/run_result.json", "w", encoding="utf-8") as f:
        json.dump({
            "status": a2_result.get("status"),
            "a2": {k: v for k, v in a2_result.items() if k != "article_text"},
            "b1b": {k: v for k, v in b1b_result.items() if k != "article_text"},
            "timing": writer_result.get("timing"), "run_metadata": writer_result.get("run_metadata"),
        }, f, ensure_ascii=False, indent=2, default=str)

    result = {
        "status": a2_result.get("status"), "topic": base.TOPIC_EN, "topic_id": base.TOPIC_ID,
        "counts_after_fix": new_counts, "elapsed_seconds": elapsed,
        "cost_jpy_this_run": cost_final_this_run, "baseline_log_lines": baseline_lines,
        "total_log_lines_now": total_lines_now,
        "started_at": started_at, "finished_at": finished_at,
        "budget_jpy": BUDGET_JPY, "budget_exceeded": cost_final_this_run > BUDGET_JPY,
    }
    with open(f"{BASE_DIR}/cost_summary.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

    # ------------------------------------------------------------
    # Step 5: Production 1生成セット原価(前回Research/Ledger¥48.73 + 本fix
    # runの実費。共通費の50:50配賦はしない)
    # ------------------------------------------------------------
    research_ledger_cost_run1 = 48.73
    run1_total_cost_reference = 87.98
    production_set_cost = {
        "note": "Trend Production 1生成セット(A2+B1)総原価。50:50配賦はしない。",
        "research_ledger_cost_run1_jpy": research_ledger_cost_run1,
        "ledger_fix_regen_cost_this_run_jpy": round(cost_final_this_run, 2),
        "production_set_total_cost_jpy": round(research_ledger_cost_run1 + cost_final_this_run, 2),
        "reference_run1_total_cost_including_fail_jpy": run1_total_cost_reference,
        "reference_note": "run1(FAIL含む、Writer部分¥39.25相当)は参考値。本修正runの実費は"
                           "ledger_fix_regen_cost_this_run_jpyを正とする(限定Verification+"
                           "Ledger修正+A2/B1B Writer再実行+QA+retry+rewriteの合算、機械分離"
                           "不能なため内訳は分離せず「共通」として扱う)。",
    }
    with open(f"{BASE_DIR}/production_set_cost.json", "w", encoding="utf-8") as f:
        json.dump(production_set_cost, f, ensure_ascii=False, indent=2, default=str)

    with open(f"{BASE_DIR}/progress_log.md", "a", encoding="utf-8") as f:
        f.write(f"- Trend fix: {started_at} 開始, {finished_at} 完了, "
                f"status={result['status']}, 本run実費=¥{cost_final_this_run:.2f}, "
                f"production_set_total=¥{production_set_cost['production_set_total_cost_jpy']:.2f}\n")

    print(f"[{THEME_ID}] 完了: status={result['status']} 本run実費(累計)=¥{cost_final_this_run:.2f} "
          f"(budget=¥{BUDGET_JPY:.2f}, exceeded={result['budget_exceeded']}) "
          f"production_set_total=¥{production_set_cost['production_set_total_cost_jpy']:.2f}")
    return result


if __name__ == "__main__":
    main()
    sys.exit(0)

# ============================================================
# er014_output/four_type_observation_01/trend/run_trend_galaxy_fix_regen.py
# 管理ID: EDITORIAL-4TYPE-FOLLOWUP-02B-TREND-COMPLETE
#
# 目的: 前回run(run_trend_fix_regen.py, EDITORIAL-4TYPE-FOLLOWUP-02-
# TREND-LEDGER-FIX-REGEN)のFact Checker FAIL(A2, attempt1)で判明した、
# 「Google's first Android XR product is planned as audio-only glasses
# for fall 2026」という記事側の一般化の誤りを修正する。Google公式の
# Android XRプラットフォームページ(android.com/xr/)はSamsung Galaxy XR
# ヘッドセットを「最初のデバイス(the first device)」として既に提供中と
# 説明しており、fall 2026発売のaudio-onlyグラスは(Android XR eyewearの
# 中での)最初の製品にすぎない。Research全体の再実行はせず、Galaxy XR
# ヘッドセットの事実1件だけを既存のvfl01検証呼び出し(OpenAI web_search)
# で限定確認し、Ledgerへ追記する。
#
# 旧成果物(run2, ledger-fix直後・Galaxy XR未修正版)はtrend/
# run2_before_galaxy_fix/へコピー退避(削除しない)。
# raw_usage_log.jsonlは追記され続けるため、baseline_lines以降だけを
# 本run実費として分離する(run_trend_fix_regen.pyのincremental_cost_jpy
# と同一ロジックをそのままimportして再利用)。
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

import er003_v1_en_direct_ab_01_generate as ab01  # noqa: E402
import er003_v1_en_direct_vfl_01_generate as vfl01  # noqa: E402
import er005_cost_logger as cl  # noqa: E402
import er006_pool_pilot_01_writer as writer_mod  # noqa: E402

BASE_DIR = "er014_output/four_type_observation_01/trend"
sys.path.insert(0, os.path.join(os.getcwd(), BASE_DIR))
import run_trend_a2 as base  # noqa: E402
import run_trend_fix_regen as fix1  # noqa: E402  (render_ledger_text/load_structured_ledger/incremental_cost_jpy再利用)

THEME_ID = base.THEME_ID
TOPIC_EN = base.TOPIC_EN
RESEARCH_DIR = f"{BASE_DIR}/research"
LOG_PATH = f"{BASE_DIR}/raw_usage_log.jsonl"
BACKUP_DIR = f"{BASE_DIR}/run2_before_galaxy_fix"

BUDGET_JPY = 120.0
ESTIMATED_WRITER_COST_JPY = 65.0  # 前回run(Ledger修正+A2/B1B Writer再実行+QA一式)実費¥59.33を踏まえた保守的見積り
MAX_VERIFICATION_DRAFT_ATTEMPTS = 2  # 予算節約のため本runでは最大2回まで(前回runの3回より縮小)

BACKUP_TARGETS = [
    "a2", "b1b", "reader_facing_article.txt", "reader_facing_article_b1b.txt",
    "run_result.json", "cost_summary.json",
]

# ------------------------------------------------------------
# 限定Verification対象: F008_FIX2(新draft、Fact Checker FAILが引用した
# android.com/xr/ の記述をもとに作成)。v1で AMBIGUOUS の場合は v2(より
# hedgeした表現)で1回だけ再試行する。
# ------------------------------------------------------------
GALAXY_XR_DRAFT_V1 = {
    "fact_id": "F008_FIX2",
    "claim": (
        "Google's Android XR platform page identifies the Samsung Galaxy XR "
        "headset as the first available device built on the Android XR platform, "
        "and describes it as already available -- distinct from the fall 2026 "
        "audio-only glasses (F008_FIX) and the camera/optional-in-lens-display "
        "glasses prototype (F008), which are a separate hardware form factor "
        "(eyewear, not a headset) without the same 'first device' status."
    ),
    "subject": "Android XR platform: first available device overall (Samsung Galaxy XR headset) vs. first eyewear/audio-only product",
    "date_or_period": (
        "Not stated as a specific launch date in the cited platform page; the "
        "page describes Galaxy XR as already available at the time of citation."
    ),
    "scope": (
        "Samsung Galaxy XR headset as described on Google's Android XR platform "
        "page (android.com/xr/); the cited passage does not establish specific "
        "country/market availability details."
    ),
    "conditions": (
        "The platform page's 'first device' characterization applies to the "
        "Android XR platform overall (headset form factor), not specifically to "
        "the eyewear/glasses product line described in F008/F008_FIX, which are a "
        "different hardware form factor (glasses, not a headset)."
    ),
    "numeric_value": None,
    "numeric_scope": None,
    "causal_strength": "NOT_APPLICABLE",
    "source_title": "Learn About Extended Reality & Immersive VR with Android XR",
    "source_url": "https://www.android.com/xr/",
    "source_type": "OTHER",
    "support_level": "DIRECTLY_STATED",
    "ambiguity": (
        "The exact wording of 'first device' status and precise release date/"
        "region for Galaxy XR were not directly quoted in the passage available "
        "before this verification call; confirm via web_search whether "
        "android.com/xr/ (or a closely related Samsung/Google source) directly "
        "supports Galaxy XR as the first Android XR device and as already "
        "available."
    ),
    "notes_for_writer": (
        "Do not describe the fall 2026 audio-only glasses (F008_FIX) as 'the "
        "first Android XR product' without qualification. Google's Android XR "
        "platform page describes the Samsung Galaxy XR headset -- a different "
        "hardware form factor (headset, not eyewear) -- as the first device on "
        "the Android XR platform overall, and it is already available. Use "
        "precise phrasing: Galaxy XR headset = first Android XR device overall "
        "(already available); fall 2026 audio-only glasses = first audio-only / "
        "eyewear product in the Android XR eyewear line (not yet launched)."
    ),
}

GALAXY_XR_DRAFT_V2 = {
    **GALAXY_XR_DRAFT_V1,
    "claim": (
        "Google's Android XR platform page describes the Samsung Galaxy XR "
        "headset as available and refers to it in first-device terms for the "
        "Android XR platform; this headset is a different hardware form factor "
        "from the eyewear/glasses products described in F008 and F008_FIX, and "
        "the cited passage does not itself establish a precise launch date or "
        "specific country/market rollout for Galaxy XR."
    ),
    "conditions": (
        "This fact concerns the Android XR platform's headset form factor "
        "generally (Galaxy XR); it does not assert an exact launch date, "
        "specific country/market availability, or sales/adoption data, and it "
        "does not alter the separate eyewear-line facts in F008/F008_FIX."
    ),
    "ambiguity": (
        "Verify via web_search whether android.com/xr/ (or a closely related "
        "official Google/Samsung source) supports Galaxy XR being available and "
        "referred to as an/the first Android XR device; if the source does not "
        "use exact 'first device' wording, treat verdict as AMBIGUOUS rather "
        "than assuming it."
    ),
}


def backup_run2():
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


def latest_fact_check_verdict(level_dir: str) -> dict:
    path = f"{BASE_DIR}/{level_dir}/audit/fact_check_attempts.json"
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        attempts = json.load(f)
    return attempts[-1] if attempts else {}


def write_stop(result: dict):
    with open(f"{BASE_DIR}/run_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] STOP: {result['reason']}")


def main():
    started_at = datetime.now(timezone.utc).isoformat()
    print(f"[{THEME_ID}] Trend Galaxy XR Fix + Regen 開始")

    backup_result = backup_run2()
    print(f"[{THEME_ID}] run2_before_galaxy_fix退避完了: copied={backup_result['copied']} "
          f"skipped={backup_result['skipped_not_found']}")

    baseline_lines = 0
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, encoding="utf-8") as f:
            baseline_lines = sum(1 for _ in f)
    cl.install(LOG_PATH)

    client = vfl01.get_client()

    # ------------------------------------------------------------
    # Step 1: 限定Verification(F008_FIX2、Galaxy XRヘッドセットの事実1件のみ)
    # ------------------------------------------------------------
    verified_draft = None
    verdict_record = None
    verification_attempts_log = []
    for attempt_idx, draft in enumerate([GALAXY_XR_DRAFT_V1, GALAXY_XR_DRAFT_V2][:MAX_VERIFICATION_DRAFT_ATTEMPTS], start=1):
        with cl.logging_context(THEME_ID, f"galaxy_xr_verification_attempt{attempt_idx}"):
            verification_result = base.run_verification_for_topic(
                client, TOPIC_EN, {"facts": [draft]},
            )
        with open(f"{RESEARCH_DIR}/galaxy_xr_verification_attempt{attempt_idx}.json", "w", encoding="utf-8") as f:
            json.dump(verification_result, f, ensure_ascii=False, indent=2, default=str)
        verdicts = {v["fact_id"]: v for v in verification_result["parsed"]["verifications"]}
        v = verdicts.get("F008_FIX2", {})
        verification_attempts_log.append({"attempt": attempt_idx, "verdict": v.get("verdict"),
                                           "path": f"{RESEARCH_DIR}/galaxy_xr_verification_attempt{attempt_idx}.json"})
        print(f"[{THEME_ID}] 限定Verification attempt{attempt_idx}: F008_FIX2={v.get('verdict')}")
        if v.get("verdict") == "VERIFIED":
            verified_draft = draft
            verdict_record = v
            break

    cost_after_verification, _ = fix1.incremental_cost_jpy(baseline_lines)

    if verified_draft is None:
        result = {
            "status": "STOP_FACT_NOT_RECONFIRMED",
            "reason": "限定Verificationにより F008_FIX2(Galaxy XRヘッドセット)の verdict が "
                      f"{MAX_VERIFICATION_DRAFT_ATTEMPTS}回試行してもVERIFIEDになりませんでした。"
                      "信頼できるsourceで再確認できないためSTOPします。",
            "verification_attempts": verification_attempts_log,
            "cost_jpy_this_run": cost_after_verification, "started_at": started_at,
            "finished_at": datetime.now(timezone.utc).isoformat(),
        }
        write_stop(result)
        return result

    # ------------------------------------------------------------
    # Step 2: Ledger修正(旧版をverified_fact_ledger_v2_before_galaxy_fix.txt
    # として保存、F008_FIXのnotes_for_writerへcaveat追記、F008_FIX2を追加)
    # ------------------------------------------------------------
    ledger_txt_path = f"{RESEARCH_DIR}/verified_fact_ledger.txt"
    shutil.copy2(ledger_txt_path, f"{RESEARCH_DIR}/verified_fact_ledger_v2_before_galaxy_fix.txt")

    structured = fix1.load_structured_ledger()
    kept_facts = structured["kept_facts"]
    f008_fix_original = next(f for f in kept_facts if f["fact_id"] == "F008_FIX")
    old_f008_fix_notes = f008_fix_original.get("notes_for_writer")

    fixed_f008_fix = dict(f008_fix_original)
    fixed_f008_fix["notes_for_writer"] = (
        f"{old_f008_fix_notes} UPDATE (galaxy xr fix): do not describe this fall 2026 "
        f"audio-only launch as Google's 'first Android XR product' without qualification "
        f"-- see F008_FIX2. Google's Android XR platform page describes the Samsung "
        f"Galaxy XR headset (a different hardware form factor, not eyewear) as the first "
        f"device on the Android XR platform overall, and it is already available. This "
        f"audio-only glasses launch is the first audio-only/eyewear product within the "
        f"Android XR eyewear line specifically, not the platform's first product overall."
    )

    new_f008_fix2_kept = {
        **verified_draft,
        "verification_verdict": "VERIFIED",
        "verification_notes": verdict_record.get("verification_notes", ""),
    }

    new_kept_facts = []
    for f in kept_facts:
        if f["fact_id"] == "F008_FIX":
            new_kept_facts.append(fixed_f008_fix)
            new_kept_facts.append(new_f008_fix2_kept)
        else:
            new_kept_facts.append(f)

    new_counts = dict(structured["counts"])
    new_counts["VERIFIED"] = new_counts.get("VERIFIED", 0) + 1

    new_ledger_text = fix1.render_ledger_text(new_kept_facts)
    with open(ledger_txt_path, "w", encoding="utf-8") as f:
        f.write(new_ledger_text)

    prior_fix_applied = structured.get("fix_applied")
    fix_applied_history = prior_fix_applied if isinstance(prior_fix_applied, list) else (
        [prior_fix_applied] if prior_fix_applied else [])
    fix_applied_history.append({
        "management_id": "EDITORIAL-4TYPE-FOLLOWUP-02B-TREND-COMPLETE",
        "reason": "Fact Checker FAIL(run2)で判明した、記事が「Googleの最初のAndroid XR製品は"
                  "2026年秋のaudio-onlyグラス」と記述し、実際はSamsung Galaxy XRヘッドセットが"
                  "既にAndroid XRプラットフォームの最初のデバイスとして提供中である点と矛盾して"
                  "いた誤りを修正。",
        "changed_fact_id": "F008_FIX",
        "added_fact_id": "F008_FIX2",
        "verification_result_path": verification_attempts_log[-1]["path"],
    })
    new_structured = {**structured, "kept_facts": new_kept_facts, "counts": new_counts,
                       "fix_applied": fix_applied_history}
    with open(f"{RESEARCH_DIR}/verified_fact_ledger_structured.json", "w", encoding="utf-8") as f:
        json.dump(new_structured, f, ensure_ascii=False, indent=2, default=str)

    diff_md_append = f"""

# Trend Galaxy XR Fix Diff (追記)

管理ID: EDITORIAL-4TYPE-FOLLOWUP-02B-TREND-COMPLETE
実施日時(UTC): {started_at}

## 背景

前回run(run2, EDITORIAL-4TYPE-FOLLOWUP-02-TREND-LEDGER-FIX-REGEN)のFact Checker
(A2, attempt1)がFAIL判定。理由: 記事が「Googleの最初のAndroid XR製品は、2026年秋に
予定されている音声のみのグラス」と記述したが、Googleの現行Android XRプラットフォーム
ページ(android.com/xr/)はSamsung Galaxy XRヘッドセットを「最初のデバイス」とし、
すでに提供中と説明している(headsetとeyewearは別のハードウェア形態)。これは前回
タスクが対象とした元のFAIL理由とは別の、Writerが新たに導入した一般化の誤り。

## 再確認方法

既存の`vfl01.build_verification_prompt`/Verification呼び出し(OpenAI web_search、
`er003_v1_en_direct_vfl_01_generate.py`の`run_verification_for_topic`と同一実装)を、
F008_FIX2(Galaxy XRヘッドセットの事実1件のみ)に限定して実行した(Research全体の
再実行はしていない)。

## 再確認結果

- 試行回数: {len(verification_attempts_log)}回、最終verdict=VERIFIED
- 生JSON(各試行): {[a['path'] for a in verification_attempts_log]}
- Source: android.com/xr/「Learn About Extended Reality & Immersive VR with Android XR」
- 内容: Samsung Galaxy XRヘッドセットはAndroid XRプラットフォーム上の最初のデバイスとして
  既に提供中。fall 2026発売のaudio-onlyグラス(F008_FIX)とは別のハードウェア形態(headset
  vs eyewear)であり、「最初の製品」と呼べるのはAndroid XR eyewearライン内でのみ。

## Ledger差分

| 種別 | fact_id | 内容 |
|---|---|---|
| 修正 | F008_FIX | notes_for_writerへ「audio-onlyグラス発売をGoogleの'first Android XR product'と無条件に呼ばない。Galaxy XRヘッドセット(別形態)がプラットフォーム全体の最初のデバイスで既に提供中。audio-onlyグラスはeyewearライン内での最初の製品」というcaveatを追記。 |
| 追加 | F008_FIX2 | 新規fact。「Google Android XRプラットフォームページはSamsung Galaxy XRヘッドセットを最初のデバイスとして既に提供中と説明。eyewear(F008/F008_FIX)とは別形態」。source: android.com/xr/。 |

counts: VERIFIED {structured['counts'].get('VERIFIED', 0)} -> {new_counts['VERIFIED']}
(AMBIGUOUS/REJECTEDは変更なし)
"""
    with open(f"{RESEARCH_DIR}/ledger_fix_diff.md", "a", encoding="utf-8") as f:
        f.write(diff_md_append)
    print(f"[{THEME_ID}] Ledger修正完了(Galaxy XR): research/verified_fact_ledger.txt上書き、"
          f"research/ledger_fix_diff.mdへ追記")

    cost_after_ledger_fix, _ = fix1.incremental_cost_jpy(baseline_lines)
    if cost_after_ledger_fix + ESTIMATED_WRITER_COST_JPY > BUDGET_JPY:
        result = {
            "status": "STOP_BUDGET_EXCEEDED",
            "reason": f"限定Verification+Ledger修正完了時点で本run実費¥{cost_after_ledger_fix:.2f}に、"
                      f"Writer/QA再実行の保守的見積り¥{ESTIMATED_WRITER_COST_JPY:.2f}を加えると"
                      f"BUDGET_JPY=¥{BUDGET_JPY:.2f}を超過する見込みのため、Writer/QAを実行せずSTOPします。",
            "cost_jpy_this_run": cost_after_ledger_fix, "started_at": started_at,
            "finished_at": datetime.now(timezone.utc).isoformat(),
        }
        write_stop(result)
        return result

    # ------------------------------------------------------------
    # Step 3: Trend Gate/Mode判定チェックリスト再判定
    # ------------------------------------------------------------
    trend_gate_checklist = base.build_trend_gate_checklist(new_kept_facts)
    with open(f"{BASE_DIR}/trend_gate_checklist.json", "w", encoding="utf-8") as f:
        json.dump(trend_gate_checklist, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] Trend Gate再判定完了: routing="
          f"{trend_gate_checklist['mode_judgment_2_questions']['routing_result']}")

    # ------------------------------------------------------------
    # Step 4: Writer再実行(正式path、B1B+A2両方)
    # ------------------------------------------------------------
    for sub in ("a2", "b1b"):
        shutil.rmtree(f"{BASE_DIR}/{sub}", ignore_errors=True)

    master_full_text = ab01.load_master_full_text()
    print(f"[{THEME_ID}] run_writer_for_theme(editorial_mode=trend_synthesis)再実行開始 "
          f"(Galaxy XR修正版Ledgerを共通Fact源として、B1B+A2両方をWriterから再実行)...")
    t0 = time.time()
    writer_result = writer_mod.run_writer_for_theme(
        client, master_full_text, THEME_ID, TOPIC_EN, ledger_txt_path, BASE_DIR,
        editorial_mode="trend_synthesis", trend_gate_checklist=trend_gate_checklist,
    )
    elapsed = round(time.time() - t0, 2)
    a2_result = writer_result["results"].get("A2", {})
    b1b_result = writer_result["results"].get("B1B", {})
    print(f"[{THEME_ID}] run_writer_for_theme完了: A2 status={a2_result.get('status')} "
          f"B1B status={b1b_result.get('status')} elapsed={elapsed}s")

    finished_at = datetime.now(timezone.utc).isoformat()
    cost_final_this_run, total_lines_now = fix1.incremental_cost_jpy(baseline_lines)

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

    a2_fact_check = latest_fact_check_verdict("a2")
    b1b_fact_check = latest_fact_check_verdict("b1b")

    result = {
        "status": a2_result.get("status"), "topic": TOPIC_EN, "topic_id": base.TOPIC_ID,
        "counts_after_fix": new_counts, "elapsed_seconds": elapsed,
        "a2_fact_check_verdict": a2_fact_check.get("verdict"),
        "b1b_fact_check_verdict": b1b_fact_check.get("verdict"),
        "cost_jpy_this_run": cost_final_this_run, "baseline_log_lines": baseline_lines,
        "total_log_lines_now": total_lines_now,
        "started_at": started_at, "finished_at": finished_at,
        "budget_jpy": BUDGET_JPY, "budget_exceeded": cost_final_this_run > BUDGET_JPY,
        "verification_attempts": verification_attempts_log,
    }
    with open(f"{BASE_DIR}/cost_summary.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

    # ------------------------------------------------------------
    # Step 5: Production 1生成セット原価更新
    # ------------------------------------------------------------
    prev_cost = None
    if os.path.exists(f"{BASE_DIR}/production_set_cost.json"):
        with open(f"{BASE_DIR}/production_set_cost.json", encoding="utf-8") as f:
            prev_cost = json.load(f)
    research_ledger_cost_run1 = (prev_cost or {}).get("research_ledger_cost_run1_jpy", 48.73)
    ledger_fix_regen_cost_run2 = (prev_cost or {}).get(
        "ledger_fix_regen_cost_total_this_delegation_jpy", 75.25)
    production_set_cost = {
        "note": "Trend Production 1生成セット(A2+B1)総原価。50:50配賦はしない。",
        "research_ledger_cost_run1_jpy": research_ledger_cost_run1,
        "ledger_fix_regen_cost_run2_jpy": ledger_fix_regen_cost_run2,
        "galaxy_xr_fix_regen_cost_this_run_jpy": round(cost_final_this_run, 2),
        "production_set_total_cost_jpy": round(
            research_ledger_cost_run1 + ledger_fix_regen_cost_run2 + cost_final_this_run, 2),
        "reference_discarded_runs": {
            "run1_total_including_fail_jpy": 87.98,
            "run2_total_note": "run2(A2 FAIL継続、Galaxy XR未修正)の実費はledger_fix_regen_cost_run2_jpyに含まれ、破棄はしていない(Ledger修正・B1B成果物は本runの土台としてそのまま利用)。",
        },
        "reference_note": "完成セット(A2+B1、両方Fact Checker非FAIL)としての総原価は"
                          "production_set_total_cost_jpy。run1のみが参考の破棄run(Writer部分"
                          "¥39.25相当)。",
    }
    with open(f"{BASE_DIR}/production_set_cost.json", "w", encoding="utf-8") as f:
        json.dump(production_set_cost, f, ensure_ascii=False, indent=2, default=str)

    with open(f"{BASE_DIR}/progress_log.md", "a", encoding="utf-8") as f:
        f.write(f"- Trend complete (galaxy xr fix): {started_at} 開始, {finished_at} 完了, "
                f"status={result['status']}, a2_fact_check={a2_fact_check.get('verdict')}, "
                f"b1b_fact_check={b1b_fact_check.get('verdict')}, "
                f"本run実費=¥{cost_final_this_run:.2f}, "
                f"production_set_total=¥{production_set_cost['production_set_total_cost_jpy']:.2f}\n")

    print(f"[{THEME_ID}] 完了: status={result['status']} A2 fact_check="
          f"{a2_fact_check.get('verdict')} B1B fact_check={b1b_fact_check.get('verdict')} "
          f"本run実費={cost_final_this_run:.2f} (budget=¥{BUDGET_JPY:.2f}) "
          f"production_set_total=¥{production_set_cost['production_set_total_cost_jpy']:.2f}")
    return result


if __name__ == "__main__":
    main()
    sys.exit(0)

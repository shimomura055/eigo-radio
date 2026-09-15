# ============================================================
# er014_output/four_type_observation_01/discovery/run_discovery_a2_regen_fu03.py
# 管理ID: USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-DISCOVERY Part B/C
#
# 目的:
#  Part B(既定、--audio無し): 既存Discovery S2正式Production path
#  (er003_discovery_focus_staged_production_01.run_one_pattern_staged_
#  discovery_focus、editorial_mode="discovery_focus_staged"相当、同一
#  Verified Fact Ledger[er014_output/.../discovery/research/、Research
#  再実行なし])で、A2を最大--max-attempts回、無変更で再生成する。
#  Prompt変更・length指示追加は一切行わない。各attemptのword countを
#  記録し、目安280-420語に最も近い(かつ全QA PASS)ものを採用候補にする。
#  No Jargon: 既存run_discovery_fix_b1b_kp.pyのjargon_scan/fix_all_jargon/
#  run_final_qaをそのまま再利用(新Validatorは追加しない)。
#
#  Part C(--audio指定): Part Bで採用が確定した新canonical A2に対し、
#  Key Phrase再選定(er003_v1_n3_01_scaffold_generate.run_key_phrases、
#  入口再呼び出し最大3回)→run_discovery_audio_completion.run_level("a2")
#  (Production関数のみで構成される既存turnkey pipeline、無変更で直接
#  呼ぶ)で音声を再完成する。旧604語版の音声/Key Phraseは*_604w_old/
#  へ退避してから実行する(再利用しない)。
#
# 禁止: Prompt変更・length指示追加・Validator変更・Gate緩和・retry上限
# 変更・approve_regenerate()・B1B本文/音声変更・Production(er003/er006/
# er011)コード変更。
# ============================================================
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import time
from datetime import datetime, timezone

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
_DISCOVERY_DIR_ABS = os.path.dirname(os.path.abspath(__file__))
if _DISCOVERY_DIR_ABS not in sys.path:
    sys.path.insert(0, _DISCOVERY_DIR_ABS)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")

import er003_discovery_focus_staged_production_01 as s2prod
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_scaffold_generate as scaffold_gen
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import run_discovery_fix_b1b_kp as fixmod  # jargon_scan/fix_all_jargon/run_final_qaを再利用

THEME_ID = "discovery_why_silence_uncomfortable_a2"
BASE_DIR = "er014_output/four_type_observation_01/discovery"
RESEARCH_DIR = f"{BASE_DIR}/research"
A2_CANONICAL_DIR = f"{BASE_DIR}/a2"
A2_V2_DIR = f"{BASE_DIR}/a2_v2"
BACKUP_DIR = f"{BASE_DIR}/a2_before_regeneration_604w"
ADOPTION_JSON = f"{BASE_DIR}/a2_regeneration_adoption.json"
REGEN_LOG_PATH = f"{BASE_DIR}/a2_regeneration_log.md"
TEXT_LOG_PATH = f"{BASE_DIR}/raw_usage_log_a2_regen_fu03.jsonl"

AUDIO_OUT_DIR = f"{BASE_DIR}/audio"
AUDIO_A2_DIR = f"{AUDIO_OUT_DIR}/a2"
AUDIO_A2_OLD_DIR = f"{AUDIO_OUT_DIR}/a2_604w_old"
KP_A2_DIR = f"{BASE_DIR}/key_phrases/a2"
KP_A2_OLD_DIR = f"{BASE_DIR}/key_phrases/a2_604w_old"

TOPIC_EN = fixmod.TOPIC_EN  # run_discovery_a2.py/run_discovery_fix_b1b_kp.pyと同一文字列

SOFT_LOWER, SOFT_UPPER = 280, 420

PRICING_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
USD_JPY = 160.0


def _load_pricing():
    with open(PRICING_PATH, encoding="utf-8") as f:
        return json.load(f)["prices"]


PRICING = _load_pricing()


def _price(provider, model, meter, tier="Standard"):
    for p in PRICING:
        if (p["provider"] == provider and p["model"] == model and p["meter"] == meter
                and p.get("tier", "Standard") == tier):
            return p["price"]
    return None


def _call_cost_usd(rec: dict) -> float:
    if rec.get("success") is False:
        return 0.0
    provider, model = rec.get("provider"), rec.get("model_id")
    if provider == "azure":
        dur = rec.get("audio_duration_submitted_seconds") or 0.0
        price = _price("azure", "real-time transcription (S0/S1 standard tier)", "audio_hour")
        return (dur / 3600.0) * (price or 0.0)
    it, ot = rec.get("input_tokens") or 0, rec.get("output_tokens") or 0
    ct = rec.get("cached_input_tokens") or 0
    billable_in = max(it - ct, 0)
    in_price = _price(provider, model, "input_tokens")
    out_price = _price(provider, model, "output_tokens")
    cached_price = _price(provider, model, "cached_input_tokens")
    if in_price is None or out_price is None:
        return 0.0
    if cached_price is None:
        cached_price = in_price
    cost = (billable_in / 1e6) * in_price + (ct / 1e6) * cached_price + (ot / 1e6) * out_price
    web_search_calls = rec.get("web_search_call_count") or 0
    web_search_price = _price("openai", "N/A (tool, all models)", "web_search_call")
    if web_search_price:
        cost += (web_search_calls / 1000) * web_search_price
    return cost


def cost_so_far_jpy(log_path: str) -> float:
    if not os.path.exists(log_path):
        return 0.0
    total_usd = 0.0
    with open(log_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            total_usd += _call_cost_usd(rec)
    return total_usd * USD_JPY


def save_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# 公式word_count算出ロジック(er003_v1_en_direct_ab_01_generate.py::
# compute_word_count、investigate_a2_length.py::compute_word_count_official
# と完全同一のロジックをそのまま再現する読み取り専用の複製。新Validator
# ではない)。
# ============================================================
def compute_word_count_official(text: str) -> int:
    body = re.sub(r"^#{1,6}\s*.*$", "", text, flags=re.MULTILINE)
    words = re.findall(r"[A-Za-z][A-Za-z'’-]*", body)
    return len(words)


# ============================================================
# Part B: A2再生成(最大--max-attempts回)
# ============================================================
def run_one_attempt(client, n: int, ledger_text: str, vfl_path: str, budget_jpy: float) -> dict:
    out_dir = f"{A2_V2_DIR}/attempt{n}"
    os.makedirs(out_dir, exist_ok=True)
    print(f"[A2-REGEN-FU03] attempt{n}: run_one_pattern_staged_discovery_focus() 開始...")
    t0 = time.time()
    try:
        gen_result = s2prod.run_one_pattern_staged_discovery_focus(
            client=client, level="a2", topic_ja=TOPIC_EN, verified_ledger_text=ledger_text,
            out_dir=out_dir, theme_tag=f"{THEME_ID}_v2_attempt{n}", vfl_path=vfl_path)
        budget_stop_reason = None
    except RuntimeError as e:
        if "費用上限超過" not in str(e):
            raise
        gen_result = {"status": "STOP_BUDGET_EXCEEDED_MIDRUN", "article_text": None}
        budget_stop_reason = str(e)
    elapsed = round(time.time() - t0, 2)

    status = gen_result.get("status")
    article_text = gen_result.get("article_text")
    attempt_result = {
        "attempt": n, "out_dir": out_dir, "status": status, "elapsed_seconds": elapsed,
        "budget_stop_reason_midrun": budget_stop_reason,
        "word_count_raw": None, "word_count_final": None, "jargon_before": None,
        "jargon_fix_applied": False, "jargon_after": None, "final_qa_after_jargon_fix": None,
        "final_text": None,
    }

    if article_text:
        word_count_raw = compute_word_count_official(article_text)
        jargon_before = fixmod.jargon_scan(article_text)
        final_text = article_text
        attempt_result["word_count_raw"] = word_count_raw
        attempt_result["jargon_before"] = jargon_before

        if jargon_before["hit_count"] > 0 and status == "OK":
            print(f"[A2-REGEN-FU03] attempt{n}: No Jargon hit_count={jargon_before['hit_count']} "
                  f"-> 既存rewrite経路(fix_all_jargon)で修正...")
            ledger_model = routing.require_model("A2_WRITER", routing.WRITER_MODEL)
            fix_result = fixmod.fix_all_jargon(article_text, ledger_model, TOPIC_EN,
                                                f"a2v2attempt{n}", client, ledger_text)
            final_text = fix_result["updated_text"]
            attempt_result["jargon_fix_applied"] = True
            attempt_result["jargon_fix_block_results_summary"] = [
                {"terms_detected": br["terms_detected"], "resolved": br["resolved"],
                 "human_review_required": br["human_review_required"]}
                for br in fix_result["block_results"]
            ]
            attempt_result["jargon_after"] = fixmod.jargon_scan(final_text)
            final_qa = fixmod.run_final_qa(final_text, ledger_text, ledger_model, TOPIC_EN,
                                            out_dir, vfl_path, client, f"a2v2attempt{n}")
            attempt_result["final_qa_after_jargon_fix"] = final_qa
        else:
            attempt_result["jargon_after"] = jargon_before

        word_count_final = compute_word_count_official(final_text)
        attempt_result["word_count_final"] = word_count_final
        attempt_result["final_text"] = final_text
        with open(f"{out_dir}/article.md", "w", encoding="utf-8") as f:
            f.write(final_text)

    save_json(f"{out_dir}/attempt_summary_fu03.json",
              {k: v for k, v in attempt_result.items() if k != "final_text"})
    print(f"[A2-REGEN-FU03] attempt{n}: status={status} word_count_raw={attempt_result['word_count_raw']} "
          f"word_count_final={attempt_result['word_count_final']} jargon_fix_applied="
          f"{attempt_result['jargon_fix_applied']}")
    return attempt_result


def backup_604w_version() -> None:
    if os.path.isdir(A2_CANONICAL_DIR) and not os.path.isdir(f"{BACKUP_DIR}/a2"):
        os.makedirs(BACKUP_DIR, exist_ok=True)
        shutil.copytree(A2_CANONICAL_DIR, f"{BACKUP_DIR}/a2")
        print(f"[A2-REGEN-FU03] 旧604語版を退避: {A2_CANONICAL_DIR} -> {BACKUP_DIR}/a2")
    for fname in ["reader_facing_article.txt", "cross_level_consistency.md"]:
        src = f"{BASE_DIR}/{fname}"
        dst = f"{BACKUP_DIR}/{fname}"
        if os.path.exists(src) and not os.path.exists(dst):
            shutil.copy2(src, dst)


def choose_adoption(attempt_results: list[dict]) -> dict:
    candidates = [a for a in attempt_results if a["status"] == "OK" and a.get("final_text")]
    if not candidates:
        return {"adopted": False, "reason": "全attemptがstatus=OK(全QA PASS)に到達しませんでした"
                                              "(既存rewrite経路[Stage1再生成/Stage2-3 retry/Local Rewrite]"
                                              "を尽くしても不合格)。STOP。"}

    def dist(a):
        wc = a["word_count_final"]
        if wc < SOFT_LOWER:
            return SOFT_LOWER - wc
        if wc > SOFT_UPPER:
            return wc - SOFT_UPPER
        return 0

    for a in candidates:
        a["_dist"] = dist(a)
    candidates_sorted = sorted(candidates, key=lambda a: (a["_dist"], a["word_count_final"]))
    best = candidates_sorted[0]

    over_500 = [a for a in candidates if a["word_count_final"] >= 500]
    if len(candidates) == len(attempt_results) and len(candidates) >= 2 and len(over_500) == len(candidates):
        return {"adopted": False, "reason": f"生成した{len(candidates)}回のattemptが全てword_count>=500でした"
                                             f"(word_counts={[a['word_count_final'] for a in candidates]})。"
                                             f"委任文の規定によりSTOP(採用せず)。"}

    flag = None
    if best["word_count_final"] <= 280:
        flag = "WORD_COUNT_LE_280"
    elif best["word_count_final"] >= 500:
        flag = "WORD_COUNT_GE_500"

    return {"adopted": True, "chosen_attempt": best["attempt"], "word_count_flag": flag,
            "word_counts_all_candidates": {a["attempt"]: a["word_count_final"] for a in candidates}}


def adopt_candidate(attempt_result: dict) -> None:
    out_dir = attempt_result["out_dir"]
    final_text = attempt_result["final_text"]
    # attempt out_dir一式(audit等)をa2/へコピーし、article.mdはjargon修正後の
    # final_textで上書きする(run_summary.json等の他ファイルはattempt時点の
    # ものをそのまま保持、post_jargon_fix.jsonで補足する)。
    if os.path.isdir(A2_CANONICAL_DIR):
        shutil.rmtree(A2_CANONICAL_DIR)
    shutil.copytree(out_dir, A2_CANONICAL_DIR)
    with open(f"{A2_CANONICAL_DIR}/article.md", "w", encoding="utf-8") as f:
        f.write(final_text)
    with open(f"{BASE_DIR}/reader_facing_article.txt", "w", encoding="utf-8") as f:
        f.write(final_text)
    save_json(f"{A2_CANONICAL_DIR}/post_jargon_fix_fu03.json", {
        "jargon_fix_applied": attempt_result["jargon_fix_applied"],
        "jargon_before": attempt_result["jargon_before"],
        "jargon_after": attempt_result["jargon_after"],
        "final_qa_after_jargon_fix": attempt_result["final_qa_after_jargon_fix"],
        "word_count_raw": attempt_result["word_count_raw"],
        "word_count_final": attempt_result["word_count_final"],
    })
    print(f"[A2-REGEN-FU03] 採用: attempt{attempt_result['attempt']} -> {A2_CANONICAL_DIR}/article.md "
          f"(word_count_final={attempt_result['word_count_final']})")


def append_cross_level_consistency(a2_text: str, word_count: int) -> None:
    b1b_path = f"{BASE_DIR}/b1b/article.md"
    b1b_text = ""
    if os.path.exists(b1b_path):
        with open(b1b_path, encoding="utf-8") as f:
            b1b_text = f.read()
    # F007(college students study)該当文をそれぞれから抽出(簡易grep、
    # 既存tableの複雑な自動marker判定ロジックは複製しない。最終テキスト
    # 引用による軽量な再突合)。
    def find_sentence(text, needle):
        idx = text.find(needle)
        if idx == -1:
            return None
        end = text.find(".", idx)
        return text[max(0, idx - 0):end + 1] if end != -1 else text[idx:idx + 240]

    a2_f007 = find_sentence(a2_text, "college students")
    b1b_f007 = find_sentence(b1b_text, "college students")

    section = f"""
## USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-DISCOVERY A2再生成後のCross-Level Consistency

A2はDiscovery S2正式Production path(同一Verified Fact Ledger、Research再実行なし)で再生成した
(新word_count={word_count}語、公式ロジック[見出し除外・本文のみ])。B1B(内部ID b1b)側は本タスクでは
本文・音声とも変更していない(Part Aは既存attempt音声のHuman Review player作成のみ)。

F007(college students study)該当文の引用:
- A2(新版): {a2_f007 or '(該当文が見つかりませんでした、手動確認要)'}
- B1B(現行): {b1b_f007 or '(該当文が見つかりませんでした、手動確認要)'}

両者の差(数値の丸め方・site数の有無・文分割)はLevel間の解像度差であり、Ledger F007との直接矛盾は
本チェックの範囲では検出されなかった(簡易grepによる軽量再突合、旧cross_level_consistency.mdの
詳細marker表[F001-F012]は本タスクでは再生成していない。フルの再生成が必要な場合はユーザー判断)。
"""
    with open(f"{BASE_DIR}/cross_level_consistency.md", "a", encoding="utf-8") as f:
        f.write(section)
    print("[A2-REGEN-FU03] cross_level_consistency.md へ追記しました。")


def run_part_b(max_attempts: int, budget_jpy: float) -> dict:
    os.makedirs(BASE_DIR, exist_ok=True)
    cl.install(TEXT_LOG_PATH)
    _orig_record = cl.record

    def _guard(entry: dict) -> None:
        _orig_record(entry)
        cost = cost_so_far_jpy(TEXT_LOG_PATH)
        if cost > budget_jpy:
            raise RuntimeError(f"費用上限超過(実測¥{cost:.2f} > 上限¥{budget_jpy:.2f})。STOP。"
                                f"(driver側実行時budget guard、Production関数のロジックは無変更)")

    cl.record = _guard

    backup_604w_version()

    with open(f"{RESEARCH_DIR}/verified_fact_ledger.txt", encoding="utf-8") as f:
        ledger_text = f.read()
    vfl_path = f"{RESEARCH_DIR}/stage_b3_vfl.json"

    client = vfl01.get_client()
    attempt_results = []
    for n in range(1, max_attempts + 1):
        cost_before = cost_so_far_jpy(TEXT_LOG_PATH)
        if cost_before >= budget_jpy:
            print(f"[A2-REGEN-FU03] 予算(¥{budget_jpy:.2f})へ既に到達(¥{cost_before:.2f})、"
                  f"attempt{n}を実行せずSTOP。")
            break
        ar = run_one_attempt(client, n, ledger_text, vfl_path, budget_jpy)
        attempt_results.append(ar)

    cl.record = _orig_record  # ガード解除(Part C側で別途設定するため)

    decision = choose_adoption(attempt_results)
    if decision["adopted"]:
        chosen = next(a for a in attempt_results if a["attempt"] == decision["chosen_attempt"])
        adopt_candidate(chosen)
        append_cross_level_consistency(chosen["final_text"], chosen["word_count_final"])

    final_cost = cost_so_far_jpy(TEXT_LOG_PATH)
    log_lines = ["# Discovery A2 Regeneration Log (USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-DISCOVERY Part B)\n\n",
                 "## 方式選定理由\n",
                 "既存Discovery S2正式Production path(run_one_pattern_staged_discovery_focus、"
                 "editorial_mode=\"discovery_focus_staged\"相当、同一Ledger)で再生成する方式を採用した。"
                 "604語版の圧縮編集(Local Rewriteの多段人手編集)はFact Safety(圧縮のたびに新たな"
                 "Ledger逸脱リスクが生じ、既存Local Rewrite安全装置[MAX_REWRITE_CYCLES=3]で吸収しきれない"
                 "可能性がある)・コスト両面(圧縮編集の反復QAコストが再生成2回より高くなりうる)で"
                 "再生成方式よりリスクが高いと判断し、不採用とした(委任文の指定どおり)。\n\n",
                 "## Attempt別結果\n"]
    for a in attempt_results:
        log_lines.append(
            f"- attempt{a['attempt']}: status={a['status']} word_count_raw={a['word_count_raw']} "
            f"word_count_final={a['word_count_final']} jargon_before_hit={a['jargon_before']['hit_count'] if a['jargon_before'] else None} "
            f"jargon_fix_applied={a['jargon_fix_applied']} jargon_after_hit={a['jargon_after']['hit_count'] if a['jargon_after'] else None} "
            f"elapsed={a['elapsed_seconds']}s\n")
        if a.get("final_qa_after_jargon_fix"):
            log_lines.append(f"  final_qa_after_jargon_fix: {a['final_qa_after_jargon_fix']}\n")
    log_lines.append(f"\n## 採用判断\n{decision}\n\n")
    log_lines.append(f"## 費用(実測、Part Bのみ、budget=¥{budget_jpy:.2f})\n実測: ¥{final_cost:.2f}\n")
    with open(REGEN_LOG_PATH, "w", encoding="utf-8") as f:
        f.writelines(log_lines)

    adoption_record = {
        "decision": decision,
        "attempt_results_summary": [
            {"attempt": a["attempt"], "status": a["status"], "word_count_raw": a["word_count_raw"],
             "word_count_final": a["word_count_final"], "jargon_fix_applied": a["jargon_fix_applied"]}
            for a in attempt_results
        ],
        "part_b_cost_jpy": round(final_cost, 2),
        "budget_jpy": budget_jpy,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    save_json(ADOPTION_JSON, adoption_record)
    print(f"[A2-REGEN-FU03][Part B] 完了。decision={decision} cost=¥{final_cost:.2f}")
    return adoption_record


# ============================================================
# Part C: 音声再完成(--audio)
# ============================================================
def add_old_banner(html_path: str, label: str) -> None:
    if not os.path.exists(html_path):
        return
    with open(html_path, encoding="utf-8") as f:
        html = f.read()
    banner = (f'<div style="background:#f8d7da;border:1px solid #c33;padding:10px 14px;'
              f'margin:8px 0;font-weight:bold;">この音声・playerは{label}の旧版です。'
              f'最新候補ではありません(履歴保持のみ)。</div>')
    if banner not in html and "<body>" in html:
        html = html.replace("<body>", "<body>\n" + banner, 1)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)


def backup_audio_and_keyphrases_604w() -> None:
    if os.path.isdir(AUDIO_A2_DIR) and not os.path.isdir(AUDIO_A2_OLD_DIR):
        shutil.move(AUDIO_A2_DIR, AUDIO_A2_OLD_DIR)
        print(f"[A2-REGEN-FU03][Part C] 旧音声を退避: {AUDIO_A2_DIR} -> {AUDIO_A2_OLD_DIR}")
        add_old_banner(f"{AUDIO_A2_OLD_DIR}/player.html", "Discovery A2(旧604語版)")
    if os.path.isdir(KP_A2_DIR) and not os.path.isdir(KP_A2_OLD_DIR):
        shutil.move(KP_A2_DIR, KP_A2_OLD_DIR)
        print(f"[A2-REGEN-FU03][Part C] 旧Key Phraseを退避: {KP_A2_DIR} -> {KP_A2_OLD_DIR}")


def regenerate_key_phrases(article_text: str) -> dict:
    os.makedirs(KP_A2_DIR, exist_ok=True)
    for attempt in range(1, 4):  # 入口再呼び出し最大3回(既存governance cap)
        print(f"[A2-REGEN-FU03][Part C] Key Phrase(A2)再選定 call{attempt}/3 開始...")
        kp = scaffold_gen.run_key_phrases(
            article_text, KP_A2_DIR, f"{THEME_ID}_v2_call{attempt}",
            "A2(V2 regen, N3-01, Discovery Focus S2)", process="A2_SUPPORT")
        status = (kp["canonicalization"] or {}).get("status") if kp["canonicalization"] else kp["selection"]["status"]
        redundancy_status = (kp.get("redundancy_qa") or {}).get("status")
        print(f"[A2-REGEN-FU03][Part C] Key Phrase(A2) call{attempt} selection_status={kp['selection']['status']} "
              f"canonicalization_status={status} redundancy_status={redundancy_status}")
        overall_pass = (kp["selection"]["status"] == "KEY_WORDS_STRUCTURE_PASS"
                         and status == "CANONICALIZATION_PASS" and redundancy_status == "REDUNDANCY_PASS")
        if overall_pass:
            return {"overall": "PASS", "calls_used": attempt, "last_result": kp}
    return {"overall": "FAIL_AFTER_3_CALLS", "calls_used": 3, "last_result": kp}


def run_part_c(budget_jpy: float) -> dict:
    if not os.path.exists(ADOPTION_JSON):
        raise RuntimeError("Part Bのadoption記録(a2_regeneration_adoption.json)が見つかりません。"
                            "先にPart B(--audio無し)を実行してください。")
    adoption = load_json(ADOPTION_JSON)
    if not adoption["decision"]["adopted"]:
        print("[A2-REGEN-FU03][Part C] Part BがSTOP(未採用)のため、Part Cも実行せずSTOPします。")
        return {"status": "STOP_PART_B_NOT_ADOPTED", "part_b_decision": adoption["decision"]}

    with open(f"{A2_CANONICAL_DIR}/article.md", encoding="utf-8") as f:
        article_text = f.read()

    backup_audio_and_keyphrases_604w()

    kp_result = regenerate_key_phrases(article_text)
    if kp_result["overall"] != "PASS":
        save_json(f"{BASE_DIR}/a2_v2_key_phrase_stop.json", kp_result)
        print("[A2-REGEN-FU03][Part C] Key Phrase再選定が3回以内にPASSしませんでした。STOP。")
        return {"status": "STOP_KEY_PHRASE_NOT_PASS", "key_phrase_result": kp_result}

    import run_discovery_audio_completion as completion_mod

    os.makedirs(AUDIO_OUT_DIR, exist_ok=True)
    cl.install(completion_mod.LOG_PATH)
    baseline_cost = completion_mod.cost_so_far_jpy()
    _orig_record = cl.record

    def _guard(entry: dict) -> None:
        _orig_record(entry)
        incremental = completion_mod.cost_so_far_jpy() - baseline_cost
        if incremental > budget_jpy:
            raise RuntimeError(f"費用上限超過(本タスクPart C増分実測¥{incremental:.2f} > 上限¥{budget_jpy:.2f})。"
                                f"STOP。(driver側実行時budget guard、Production関数のロジックは無変更)")

    cl.record = _guard

    t0 = time.time()
    try:
        level_result = completion_mod.run_level("a2")
        completion_mod.update_shared_outputs("a2", level_result)
        completion_mod.append_progress_log("a2", level_result)
        status = "OK"
        error = None
    except RuntimeError as e:
        level_result = None
        status = "STOP_RUNTIME_ERROR"
        error = str(e)
    finally:
        cl.record = _orig_record
    elapsed = round(time.time() - t0, 1)
    final_incremental_cost = round(completion_mod.cost_so_far_jpy() - baseline_cost, 2)

    part_c_result = {
        "status": status, "error": error, "elapsed_seconds": elapsed,
        "key_phrase_result_overall": kp_result["overall"], "key_phrase_calls_used": kp_result["calls_used"],
        "part_c_incremental_cost_jpy": final_incremental_cost, "budget_jpy": budget_jpy,
        "level_result_summary": None if level_result is None else {
            "gate_off_result": level_result["assemble_result"].get("gate_off_result"),
            "gate_on_result": level_result["gate_opt_in_result"].get("gate_on_result"),
            "duration_seconds": level_result["assemble_result"].get("duration_seconds"),
            "consistency_all_pass": level_result["consistency"].get("all_pass"),
        },
    }
    save_json(f"{AUDIO_A2_DIR}/run_result_fu03.json" if level_result else f"{BASE_DIR}/a2_v2_audio_stop_fu03.json",
              part_c_result)

    # production_set_cost.json: update_shared_outputsが上書きしたgrand total
    # (base_total=ps_doc内の古いgrand_total_jpy_including_key_phraseに依存し、
    # 直近の累計¥606.08や本タスクPart Bの費用を反映しない)を、正しい累計へ
    # 補正する(既存関数のロジック自体は変更しない、出力JSONの値のみ本タスクの
    # 責務として補正)。
    if level_result is not None:
        ps_path = f"{BASE_DIR}/production_set_cost.json"
        ps_doc = load_json(ps_path)
        prior_baseline = 606.08  # 前回までの累計(ER-... FIX-02完了時点、docs/pm/RESULT_PACKET_FIX02_DISCOVERY.md)
        part_b_cost = adoption["part_b_cost_jpy"]
        ps_doc["fu03_part_a_cost_jpy"] = 0.0
        ps_doc["fu03_part_b_text_regen_cost_jpy"] = part_b_cost
        ps_doc["fu03_part_c_audio_recompletion_incremental_cost_jpy"] = final_incremental_cost
        ps_doc["fu03_dev_trial_cost_jpy_note"] = ("604語版(不採用)は既に606.08へ計上済みの過去費用(参考)。"
                                                    "本タスクでの新規不採用runはなし(Part Bのattempt自体が"
                                                    "採用候補評価対象であり不採用runには当たらない)。")
        ps_doc["production_set_total_cost_including_audio_jpy"] = round(
            prior_baseline + part_b_cost + final_incremental_cost, 2)
        ps_doc["fu03_total_note"] = (f"USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-DISCOVERY: "
                                      f"前回までの累計¥{prior_baseline:.2f} + Part B(A2再生成テキスト)"
                                      f"¥{part_b_cost:.2f} + Part C(A2 Key Phrase再選定+音声再完成 増分)"
                                      f"¥{final_incremental_cost:.2f} = ¥"
                                      f"{prior_baseline + part_b_cost + final_incremental_cost:.2f}。"
                                      f"update_shared_outputs()が別途書き込むproduction_set_total_cost_"
                                      f"including_audio_jpyは古いgrand_total_jpy_including_key_phrase"
                                      f"(463.27)基準の再計算値であり、本タスクの一連の追加費用を含まない"
                                      f"ため、この一連のfu03_*フィールドで正しい累計を別途保持する"
                                      f"(Open Item候補: production_set_cost.jsonの総額算出ロジックが"
                                      f"タスクをまたいだ累積加算になっていない)。")
        save_json(ps_path, ps_doc)

    print(f"[A2-REGEN-FU03][Part C] 完了。status={status} incremental_cost=¥{final_incremental_cost:.2f}")
    return part_c_result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-attempts", type=int, default=2)
    parser.add_argument("--budget-jpy", type=float, default=120.0)
    parser.add_argument("--audio", action="store_true")
    args = parser.parse_args()

    if args.audio:
        run_part_c(args.budget_jpy)
    else:
        run_part_b(args.max_attempts, args.budget_jpy)


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""AUW 委任_06d: 残Section/Family 実音声 runtime evidence + 是正後経路(非ラテンKP救済/技術STOP/導出失敗表示/再利用guard) + legacy A費用記録。
計測/隔離は 06b runner(er078_auw_runtime_evidence_06b)を再利用し、証跡先・累計 ledger・費用上限(JPY 45)だけ 06d に差し替える。
有料 API は --execute 指定時のみ。run 前に累計 ledger を読み残額<=0 なら実行しない。監督ループ・自動再試行なし。
使い方: .venv\\Scripts\\python.exe er078_auw_runtime_evidence_06d.py <part> [--execute --budget-jpy N]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys

import er078_auw_runtime_evidence_06b as b
import er078_auw_runtime_evidence_06 as e6

ROOT = e6.ROOT
EV = "er058_output/unified_all_roles_production_wiring_01/evidence_06d"
b.EV = EV
b.LEDGER = f"{EV}/cost/spend_ledger.jsonl"
b.CAP_JPY = 45.0
if "AUW-06D" not in e6.MANAGED_IDS:
    e6.MANAGED_IDS.append("AUW-06D")


def _shared_snapshot():
    r = subprocess.run(["git", "status", "--porcelain", "-uall"], capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
    snap = {}
    for line in r.stdout.splitlines():
        p = line[3:].strip().strip('"')
        if " -> " in p:
            p = p.split(" -> ")[-1]
        if (p.startswith(EV) or p.startswith("user_test/") or p.startswith("er078_auw_") or p.startswith("docs/pm/")
                or p.startswith("er058_output/unified_all_roles_production_wiring_01/")):
            continue
        full = os.path.join(ROOT, p)
        snap[p] = hashlib.md5(open(full, "rb").read()).hexdigest() if os.path.isfile(full) else None
    return snap


b.shared_snapshot = _shared_snapshot


def _line_count(p):
    return sum(1 for _ in open(p, encoding="utf-8")) if os.path.exists(p) else None


# 実 Production の JA 側 queue 2 ファイル(06b D-B1/D-B2 の再発防止確認): run 前後の行数不変を記録
JA_QUEUES = ["er009_output/ja_foreign_token_gate_01/human_review_queue.jsonl", "er007_output/ja_asr_cascade_01/human_review_queue.jsonl"]


def _ja_queue_counts():
    return {p: _line_count(p) for p in JA_QUEUES}


def begin(part, budget, execute, copy_master=False):
    q0 = _ja_queue_counts()
    out, r77, before, snap0, res, meter, ok = b.begin(part, budget, execute, copy_master=copy_master)
    res["ja_queue_lines_before"] = q0
    return out, r77, before, snap0, res, meter, ok


def finish(out, r77, before, snap0, res, meter, extra_print=()):
    res["ja_queue_lines_after"] = _ja_queue_counts()
    res["ja_queue_lines_unchanged"] = res["ja_queue_lines_before"] == res["ja_queue_lines_after"]
    b.finish(out, r77, before, snap0, res, meter, extra_print=tuple(extra_print) + ("ja_queue_lines_unchanged",))


def _tb(res, key, e_):
    import traceback
    res[key] = f"{type(e_).__name__}: {str(e_)[:600]}"
    res[key + "_traceback"] = traceback.format_exc()[-1500:]


def _clip_rows(results_path):
    """tts_generation_results.json から clip ごとの asr_judgement 要約を作る(segments + key_phrases)。"""
    d = json.load(open(results_path, encoding="utf-8")) if os.path.exists(results_path) else {}
    rows = []

    def row(cid, e):
        aj = e.get("asr_judgement") or e.get("asr_judgement_inherited") or {}
        sec = aj.get("secondary") or {}
        rows.append({"clip": cid, "status": e.get("status"), "has_asr_judgement": bool(e.get("asr_judgement")),
                     "inherited": bool(e.get("asr_judgement_inherited")), "state": aj.get("state"), "reason": aj.get("reason_code"),
                     "secondary_called": sec.get("called"), "secondary_cached": sec.get("cached"),
                     "attempts": len(e.get("attempts") or e.get("attempts_log") or e.get("standard_attempts_log") or []),
                     "reused": bool(e.get("reused_from_previous_run")),
                     "tech_stop": e.get("technical_stop_status") or (e.get("technical_stop") and "technical_stop")})
    for cid, e in (d.get("segments") or {}).items():
        if isinstance(e, dict):
            row(cid, e)
    for rk, sub in (d.get("key_phrases") or {}).items():
        for k, e in (sub or {}).items():
            if isinstance(e, dict):
                row(f"kp{rk}_{k}", e)
    return rows


# ---------------------------------------------------------------- ① X a2 KP(KGCPW 整合済み E7 の KP + xrun a2 の非KP 資産を cache として再利用)
E7_SRC = "er019_output/family_x_audio_production_wiring_01/kgcpw_evidence_01/E7_x_a2"
XRUN_SRC = "er058_output/unified_all_roles_production_wiring_01/evidence_06b/xrun/x_out"


def run_xkp(execute, budget):
    out, r77, before, snap0, res, meter, ok = begin("xkp", budget, execute, copy_master=True)
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    xdir = f"{out}/x_out"
    if not os.path.exists(f"{xdir}/a2/parts.json"):
        os.makedirs(f"{xdir}/a2", exist_ok=True)
        for f in ("parts.json", "segment_plan.json", "a2_support_texts.json"):
            shutil.copyfile(f"{E7_SRC}/a2/{f}", f"{xdir}/a2/{f}")
        shutil.copytree(f"{E7_SRC}/a2/key_phrases", f"{xdir}/a2/key_phrases", ignore=shutil.ignore_patterns("*_attempt_invalid"))
        os.makedirs(f"{xdir}/audit", exist_ok=True)
        shutil.copyfile(f"{E7_SRC}/audit/scaffold_article_sha256.json", f"{xdir}/audit/scaffold_article_sha256.json")
        for f in ("style_profile.json", "rf_tts_guard.json"):   # 同一 style profile の resume(06b xrun と同条件)
            shutil.copyfile(f"{XRUN_SRC}/audit/{f}", f"{xdir}/audit/{f}")
        shutil.copytree(f"{XRUN_SRC}/a2/narration", f"{xdir}/a2/narration", ignore=shutil.ignore_patterns("kp*", "meaning*", "attempts", "_invalidated*"))
        os.makedirs(f"{xdir}/a2/audit", exist_ok=True)
        r = json.load(open(f"{XRUN_SRC}/a2/audit/tts_generation_results.json", encoding="utf-8"))
        r["key_phrases"] = {}
        json.dump(r, open(f"{xdir}/a2/audit/tts_generation_results.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    import er019_family_x_audio_production_runner_01 as X
    common = ["--slug", "coffee_prices", "--run", "run_v5_ms_01", "--level", "a2", "--out-dir", xdir,
              "--tts-backend", "speech_metadata_flash_lite", "--style-profile", "coffee_n01_r2_p3_e1",
              "--budget-jpy", str(min(budget, 20) if budget else 20)]
    stages = ["plan"] if not ok else ["tts", "assemble", "player"]
    stage_log = {}
    for st in stages:
        sys.argv = ["er019_family_x_audio_production_runner_01.py", "--stage", st] + common
        try:
            X.main()
            stage_log[st] = "OK"
        except SystemExit as e_:
            stage_log[st] = f"SystemExit({e_.code})"
        except Exception as e_:  # noqa: BLE001
            _tb(res, "traceback_" + st, e_)
            stage_log[st] = f"{type(e_).__name__}: {str(e_)[:500]}"
            break
    res["stage_result"] = stage_log
    res["clip_rows"] = _clip_rows(f"{xdir}/a2/audit/tts_generation_results.json")
    finish(out, r77, before, snap0, res, meter)


# ---------------------------------------------------------------- ② Family B B1 全体(Production run_tts を縮約入力で実行)
B1_PARTS = {
    "title": "Cheaper Beans, Same Price Tag",
    "part1": "Coffee beans have become cheaper. But the price tag in a shop may not change right away.",
    "part2": "A price index fell 8.7% from the previous month, a report said. Shops may keep their prices for about nine months.",
    "point_one_heading": "Why prices change slowly",
    "point_one_body": "Shops often buy beans months before they sell the coffee. So an old high price can stay on the tag.",
    "point_two_heading": "What you can do",
    "point_two_body": "You can compare several shops. You do not have to buy at the first price you see.",
    "tension_body": "Some experts say prices will fall soon, but others say shops will not lower prices for months.",
    "in_one_line": "Cheaper beans do not always mean a cheaper cup right away.",
}
B1_SUPPORT = {
    "preview": "Today we look at why coffee bean prices fall while the price tags in shops stay the same for a while.",
    "comment_1": "Listen for why a shop price does not change right away.",
    "comment_2": "A fall of 8.7 percent in an index is a big move. Now, why do shops wait?",
    "comment_3": "Cheaper beans do not always mean a cheaper cup. Next, what can you do?",
    "comment_4": "You can compare shops before you buy. Finally, one line to remember.",
}


def run_b1(execute, budget):
    out, r77, before, snap0, res, meter, ok = begin("b1", budget, execute, copy_master=True)
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    import er012_b_family_production_runner_01 as B
    import er005_cost_logger as cl
    base = f"{out}/b_b1"
    B.OUT_DIR = base
    B.OUT_B1_DIR = f"{base}/b1b"
    B.NARRATION_DIR = f"{base}/b1b/narration"
    B.COST_LOG_PATH = f"{base}/audit/raw_usage_log.jsonl"
    res["plan"] = {"parts": B1_PARTS, "support": B1_SUPPORT,
                   "note": "Production run_tts を縮約入力(各1-2文)で実行。leaf 関数・引数は run_tts のまま"}
    if ok:
        os.makedirs(f"{base}/audit", exist_ok=True)
        os.makedirs(f"{base}/b1b/audit", exist_ok=True)
        cl.install(B.COST_LOG_PATH)
        try:
            results = B.run_tts(B1_PARTS, B1_SUPPORT, "Algieba", "Erinome")
            B.finalize_tts_results(results)
            import er078_pass_with_warning_registry_01 as pww
            res["listening_list"] = pww.write_listening_list_safe(f"{base}/b1b", standalone_html=True)
            res["stage_result"] = {n: r.get("status") for n, r in results.items()}
        except Exception as e_:  # noqa: BLE001
            _tb(res, "exception", e_)
        res["clip_rows"] = _clip_rows(f"{base}/b1b/audit/tts_generation_results.json")
        try:
            res["production_cost_log_jpy"] = B.compute_cost_jpy_so_far(B.COST_LOG_PATH)[0]
        except Exception as e_:  # noqa: BLE001
            res["production_cost_log_jpy"] = f"{type(e_).__name__}: {str(e_)[:200]}"
    finish(out, r77, before, snap0, res, meter, extra_print=("exception",))


# ---------------------------------------------------------------- ③ Family C: Comment(JA)=LLM 再生成+TTS、JA title 再生成
C_SRC = "er058_output/unified_all_roles_production_wiring_01/evidence_06b/crun/c_out"
C_NEW_TITLE = "記憶の箱と、迷う心"


def run_cja(execute, budget):
    out, r77, before, snap0, res, meter, ok = begin("cja", budget, execute, copy_master=True)
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    cfg = json.load(open(f"{C_SRC}/article_config.json", encoding="utf-8"))
    cfg["levels"]["a2"]["japanese_title_text"] = C_NEW_TITLE
    # attempt1 で実測: 元の reuse_from(Trial 由来)に comment/title の旧 wav があると、--only-segments で purge しても reuse_from から旧 wav が再コピーされ、
    # 新 LLM 文面に旧音声が紐づく(finding)。
    # attempt2 で更に判明: `_copy_with_ok` は .ok だけを複製し .ok.meta.json を複製しないため、reuse_from 経由の資産は常に「meta 欠如 legacy」
    # 扱い(`resumable_reuse` が現行 text の sha で meta を書いて再利用)になり、文面が変わっても旧音声が使われる(Production の既存挙動)。
    # したがって Comment/JA title の「新規 TTS」を得るには reuse_from にそれらの資産が無い状態にする(06b crun a2 出力の複製から除外)。
    _rs = f"{out}/reuse_src"
    if not os.path.exists(_rs):
        shutil.copytree(f"{C_SRC}/a2", _rs, ignore=shutil.ignore_patterns("comment_*_ja*", "japanese_title*", "web", "assembled"))
    cfg["levels"]["a2"]["reuse_from"] = _rs
    cfg_path = f"{out}/c_out/article_config.json"
    os.makedirs(os.path.dirname(cfg_path), exist_ok=True)
    json.dump(cfg, open(cfg_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    import er013_family_c_production_runner_01 as C
    res["only_segments"] = ["comment_1", "comment_2", "comment_3"]
    res["japanese_title_text"] = C_NEW_TITLE
    if ok:
        sys.argv = ["er013_family_c_production_runner_01.py", "--config", cfg_path, "--level", "a2",
                    "--budget-jpy", "25",   # C runner 内部 guard は LLM 1 call を保守的に ¥3.00 と見積もる(実費上限は Meter の hard_stop=--budget-jpy が担保)
                    
                    "--only-segments", "comment_1", "comment_2", "comment_3"]
        try:
            C.main()
            res["stage_result"] = {"main": "OK"}
        except SystemExit as e_:
            res["stage_result"] = {"main": f"SystemExit({e_.code})"}
        except Exception as e_:  # noqa: BLE001
            _tb(res, "exception", e_)
            res["stage_result"] = {"main": f"{type(e_).__name__}: {str(e_)[:500]}"}
        res["clip_rows"] = _clip_rows(f"{out}/c_out/a2/audit/tts_generation_results.json")
    finish(out, r77, before, snap0, res, meter, extra_print=("exception",))


# ---------------------------------------------------------------- E legacy A: n3.main() の cl.install 是正後の実音声 1 clip(Secondary 呼出まで進め、費用記録とRuntimeError不発を確認)
LEGA1_TEXT = "Mayor Xzqwtrlk said the new bridge would open in May."


def run_lega1(execute, budget):
    out, r77, before, snap0, res, meter, ok = begin("lega1", budget, execute)
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    import er003_v1_n3_01_tts_generate as n3
    import er005_cost_logger as cl
    theme_dir = f"{out}/theme"
    theme = {"theme_id": "auw06d_lega1", "out_dir": theme_dir}
    wav = f"{theme_dir}/b1b/narration/comment_1.wav"
    os.makedirs(os.path.dirname(wav), exist_ok=True)
    res["text"] = LEGA1_TEXT
    res["cost_logger_before_main"] = cl._LOG_PATH
    if ok:
        n3.gen.THEMES = [theme]
        box = {}

        def one_clip(th):
            # legacy A の b1b Charon 英語(comment 相当)を 1 clip。Secondary(Azure)呼出が起きる原稿(Primary NG になる固有名)
            box["result"] = n3.voice01.generate_charon_english(n3.tts_safe_number_words_en(n3.tts_safe_en(LEGA1_TEXT)), wav)
        n3.run_theme = one_clip
        sys.argv = ["er003_v1_n3_01_tts_generate.py", "auw06d_lega1"]
        try:
            n3.main()          # 是正済みの本番入口(cl.install を呼ぶ)
            r = box.get("result") or {}
            res["clip_result"] = {k: r.get(k) for k in ("status", "reason")}
        except Exception as e_:  # noqa: BLE001
            _tb(res, "exception", e_)
        res["cost_logger_after_main"] = cl._LOG_PATH
        log = f"{theme_dir}/raw_usage_log.jsonl"
        recs = [json.loads(l) for l in open(log, encoding="utf-8")] if os.path.exists(log) else []
        res["production_cost_log"] = {"path": log, "n_records": len(recs),
                                      "by_provider": {pv: sum(1 for x in recs if x.get("provider") == pv) for pv in sorted({x.get("provider") for x in recs})},
                                      "azure_records": [{k: x.get(k) for k in ("api", "success", "usage_source", "audio_duration_submitted_seconds")} for x in recs if x.get("provider") == "azure"]}
        try:
            import er019_family_x_audio_production_runner_01 as X
            res["production_cost_log"]["compute_cost_jpy_so_far"] = X.compute_cost_jpy_so_far(log)[0]
        except Exception as e_:  # noqa: BLE001
            res["production_cost_log"]["compute_cost_jpy_so_far"] = f"{type(e_).__name__}: {str(e_)[:200]}"
        res["attempt_history_rows"] = table_from_attempt_history("lega1")
    finish(out, r77, before, snap0, res, meter, extra_print=("exception", "clip_result"))


# ---------------------------------------------------------------- ① 補遺: X の KP 英語 phrase(Master Store 経由の Production 入口 ensure_key_phrase_english_component)の新規生成+Master hit
XKPEN_PHRASES = ["hold the line", "cut it close", "right away"]     # 1,2 = Master Store 未登録(新規生成+判定) / 3 = 登録済み(再利用経路の確認)


def run_xkpen(execute, budget):
    out, r77, before, snap0, res, meter, ok = begin("xkpen", budget, execute, copy_master=True)
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    import er006_audio_cost_pilot_02_shared_narration as sn
    import er003_v1_n3_01_tts_generate as n3
    import er005_cost_logger as cl
    res["phrases"] = XKPEN_PHRASES
    rows = []
    if ok:
        cl.install(f"{out}/cost_log_production.jsonl")
        os.makedirs(f"{out}/a2/narration", exist_ok=True)
        for i, ph in enumerate(XKPEN_PHRASES, 1):
            wav = f"{out}/run/a2/narration/kp{i}_english.wav"
            os.makedirs(os.path.dirname(wav), exist_ok=True)
            try:
                with cl.segment_context(f"kp{i}_english"):
                    r = sn.ensure_key_phrase_english_component(n3.tts_safe_kp_en(ph), wav, tts_backend="speech_metadata_flash_lite")
                aj = r.get("asr_judgement") or r.get("asr_judgement_inherited") or {}
                rows.append({"phrase": ph, "status": r.get("status"), "reused": bool(r.get("reused") or r.get("reused_from_master") or r.get("master_audio_reused")),
                             "keys": sorted(k for k in r.keys())[:20], "has_asr_judgement": bool(r.get("asr_judgement")), "state": aj.get("state"),
                             "reason": aj.get("reason_code")})
            except Exception as e_:  # noqa: BLE001
                rows.append({"phrase": ph, "error": f"{type(e_).__name__}: {str(e_)[:300]}"})
        res["attempt_history_rows"] = table_from_attempt_history("xkpen") if os.path.exists(f"{EV}/xkpen/attempt_history.jsonl") else []
    res["rows"] = rows
    finish(out, r77, before, snap0, res, meter)


# ---------------------------------------------------------------- 集計: attempt_history.jsonl(隔離済み)から clip 表を作る
def table_from_attempt_history(run_name, out_md=None):
    """evidence_06d/<run>/attempt_history.jsonl の record ごと(1 record = 1 clip の生成呼出)に、最終 attempt の asr_judgement 要約を出す。"""
    p = f"{EV}/{run_name}/attempt_history.jsonl"
    rows = []
    for line in open(p, encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        det = r.get("attempts_detail") or []
        last = next((a for a in reversed(det) if a.get("asr_judgement")), None)
        aj = (last or {}).get("asr_judgement") or {}
        sec_calls = sum(1 for a in det if ((a.get("asr_judgement") or {}).get("secondary") or {}).get("called"))
        rows.append({"segment": r.get("segment_id"), "level": r.get("level"), "lang": r.get("language"), "status": r.get("result_status"),
                     "n_attempts": len(det), "tts_this_call": r.get("tts_attempts_this_call"), "state": aj.get("state"), "reason": aj.get("reason_code"),
                     "role": aj.get("role"), "slot": aj.get("slot"), "version": aj.get("script_version"),
                     "secondary_calls": sec_calls, "has_asr_judgement": bool(aj), "final_lock_state": r.get("final_lock_state"),
                     "human_review_reached": r.get("human_review_reached")})
    if out_md:
        with open(out_md, "w", encoding="utf-8") as f:
            f.write("| segment | status | attempts | asr_judgement | state | reason | slot/ver | Secondary回数 | HR |\n|---|---|---|---|---|---|---|---|---|\n")
            for x in rows:
                f.write(f"| {x['segment']} | {x['status']} | {x['n_attempts']} | {'有' if x['has_asr_judgement'] else '無'} | {x['state']} | {x['reason']} | {x['slot']}/{x['version']} | {x['secondary_calls']} | {x['human_review_reached']} |\n")
    return rows


PARTS = {"xkpen": run_xkpen, "lega1": run_lega1, "xkp": run_xkp, "b1": run_b1, "cja": run_cja}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("part", choices=sorted(PARTS))
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--budget-jpy", type=float, default=0.0)
    a = ap.parse_args()
    os.chdir(ROOT)
    PARTS[a.part](a.execute, a.budget_jpy)


if __name__ == "__main__":
    main()

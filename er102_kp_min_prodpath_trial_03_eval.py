# -*- coding: utf-8 -*-
r"""KPMP3 独立評価(有料、評価者=claude-sonnet-5-5 のみ)。TRIAL-02と同一rubric(V/E/N + 最小化C/U/S/X)をArm A/Bへ同一バッチ(匿名セット)で適用。
kind=span: source_span(本文連続の実表現。TRIAL-02 Trial①と同形の対象) / kind=final: key_phrase(canonicalization後の最終KP)。
使い方: .venv\Scripts\python.exe er102_kp_min_prodpath_trial_03_eval.py --cap-jpy 60 [--dry-run]"""
import argparse, json, random, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import er098_kp_six_model_trial_01_common as C
import er101_kp_prompt_min_gen_trial_02_eval as E2
OUT = C.ROOT / "er102_output" / "kp_min_prodpath_trial_03"
C.OUT = OUT; C.LEDGER = OUT / "paid_calls.jsonl"
EV = dict(provider="anthropic", model_id="claude-sonnet-5-5")
RUBRIC = E2.RUBRIC_T1
RUBRIC_FINAL = RUBRIC.replace("1. 本文中の連続した語句だけを抜き出す(変更・言い換え・追加・創作は禁止。原形化や一般化は行わない)。",
    "1. 本文中の語句に基づく(今回の評価対象は原形化後の見出し形: 動詞の時制・人称・one's等への標準的な原形化は許容。言い換え・追加・創作は禁止)。")
assert RUBRIC_FINAL != RUBRIC

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--cap-jpy", type=float, default=60.0); ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--workers", type=int, default=6); a = ap.parse_args()
    val = json.loads((OUT / "validation.json").read_text(encoding="utf-8"))
    man = json.loads(C.ROOT.joinpath("er098_output/kp_six_model_trial_01/inputs/manifest.json").read_text(encoding="utf-8"))
    if C.stop_present(OUT): print("STOP"); return 3
    (OUT / "eval").mkdir(exist_ok=True)
    bm = OUT / "eval" / "blind_map.json"; bmap = json.loads(bm.read_text(encoding="utf-8")) if bm.exists() else {}
    jobs = []
    for u in man["units"]:
        uid = u["unit_id"]; art = (C.ROOT / u["copy_path"]).read_text(encoding="utf-8"); d = val["units"][uid]
        for kind, field, rub in (("span", "source_span", RUBRIC), ("final", "key_phrase", RUBRIC_FINAL)):
            if not d["A"]["rows"] or not d["B"]["rows"]: continue
            k = uid + ":" + kind
            if k not in bmap:
                order = ["A", "B"]; random.Random("er102:" + k).shuffle(order); bmap[k] = {"S1": order[0], "S2": order[1]}
            lines = [rub, "\n【記事】\n", art, "\n\n【匿名の選定結果】\n"]
            for sid, arm in bmap[k].items():
                lines.append("%s:" % sid)
                for i, r in enumerate(d[arm]["rows"]): lines.append("  %d. %s" % (i + 1, r[field]))
                lines.append("")
            rp = OUT / "eval" / kind / ("%s.json" % uid)
            if not rp.exists(): jobs.append((kind, uid, "\n".join(lines), rp))
    bm.write_text(json.dumps(bmap, ensure_ascii=False, indent=1), encoding="utf-8")
    print("eval jobs", len(jobs))
    if a.dry_run: print(jobs[0][2][-900:]); return 0
    def run(job):
        kind, uid, user, rp = job
        if C.stop_present(OUT): return (kind, uid, "STOPPED", 0)
        if C.ledger_total_jpy() >= a.cap_jpy: return (kind, uid, "CAP_REACHED", 0)
        body = C.build_body(EV["provider"], EV["model_id"], user); t0 = time.time()
        r = C.call_with_retry(EV["provider"], EV["model_id"], body)
        rec = dict(kind=kind, evaluator=EV["model_id"], unit_id=uid, user_message_sha256=C.sha_text(user), user_message=user, request_body=body, attempts=r["attempts"], ok=r["ok"], elapsed_s_total=round(time.time() - t0, 2))
        cost = 0.0
        if r["ok"]:
            cost = C.cost_usd(EV["model_id"], r["usage"]) * C.USD_JPY
            try: parsed = E2.extract_json(r["text"])
            except Exception as ex: parsed = None; rec["parse_error"] = str(ex)
            rec.update(response_text=r["text"], parsed=parsed, usage=r["usage"], response_id=r["response_id"], model_returned=r["model_returned"], finish=r["finish"], cost_jpy=round(cost, 5), raw_response=r["raw"])
            C.ledger_add(dict(phase="eval_" + kind, unit_id=uid, requested=EV["model_id"], returned=r["model_returned"], usage=r["usage"], cost_jpy=round(cost, 5), response_id=r["response_id"], ts=time.strftime("%Y-%m-%dT%H:%M:%S")))
        rp.parent.mkdir(parents=True, exist_ok=True); rp.write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
        return (kind, uid, "OK" if r["ok"] else "TECH_FAIL", cost)
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        for f in as_completed([ex.submit(run, j) for j in jobs]): print(f.result(), "cum_jpy=%.3f" % C.ledger_total_jpy(), flush=True)
    return 0
if __name__ == "__main__": sys.exit(main())

# -*- coding: utf-8 -*-
"""FAMILY-X-KP-SELECTION-SIX-MODEL-COMPARISON-TRIAL-01 委任_01: 選定実行(有料)。Trial専用。
6モデル x 14本文、初回生成1回。品質理由の再生成なし(技術的失敗のみ同一入力で最大2回再試行)。
使い方: .venv\\Scripts\\python.exe er098_kp_six_model_trial_01_run.py --out er098_output/kp_six_model_trial_01 \\
        --manifest er098_output/kp_six_model_trial_01/inputs/manifest.json --cap-jpy 300 [--units A_Standard,...] [--models m1,...] [--dry-run]
既に runs/<model>/<unit>.json が存在する組はスキップ(再実行=再課金の防止)。"""
import argparse, json, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import er098_kp_six_model_trial_01_common as C

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(C.OUT)); ap.add_argument("--manifest", default=str(C.OUT / "inputs" / "manifest.json"))
    ap.add_argument("--cap-jpy", type=float, default=300.0)
    ap.add_argument("--units", default=""); ap.add_argument("--models", default="")
    ap.add_argument("--workers", type=int, default=4); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    out = Path(a.out); man = json.loads(Path(a.manifest).read_text(encoding="utf8"))
    prompt = (out / "inputs" / "prompt_fixed.txt").read_text(encoding="utf8")
    units = [u for u in man["units"] if u.get("copy_path") and (not a.units or u["unit_id"] in a.units.split(","))]
    models = {k: v for k, v in C.MODELS.items() if (not a.models or any(k.startswith(x) or k == x for x in a.models.split(",")))}
    stop = C.stop_present(out)
    if stop: print("STOPセンチネルあり:", stop); return 3
    jobs = []
    for u in units:
        for mk, m in models.items():
            rp = out / "runs" / mk / ("%s.json" % u["unit_id"])
            if rp.exists(): continue
            art = (C.ROOT / u["copy_path"]).read_text(encoding="utf8")
            user = prompt + "\n\n---\n\n【記事本文】\n" + art      # Promptは無改変。データ受け渡しの区切りと見出しのみ追加(TRIAL_DESIGN_01.md 4節)
            jobs.append((mk, m, u, user, rp))
    print("jobs", len(jobs), "models", list(models), "units", [u["unit_id"] for u in units])
    if a.dry_run:
        for mk, m, u, user, rp in jobs[:2]: print(mk, u["unit_id"], len(user), json.dumps(C.build_body(m["provider"], m["model_id"], user), ensure_ascii=False)[:200])
        return 0
    def run(job):
        mk, m, u, user, rp = job
        if C.stop_present(out): return (mk, u["unit_id"], "STOPPED", 0.0)
        if C.ledger_total_jpy() >= a.cap_jpy: return (mk, u["unit_id"], "CAP_REACHED", 0.0)
        body = C.build_body(m["provider"], m["model_id"], user)
        t0 = time.time(); r = C.call_with_retry(m["provider"], m["model_id"], body)
        rec = dict(model_key=mk, requested_model_id=m["model_id"], provider=m["provider"], unit_id=u["unit_id"], article_id=u["article_id"], level=u["level"],
                   article_sha256=u["copy_sha256"], prompt_sha256=C.sha_text(prompt), user_message_sha256=C.sha_text(user), request_body=body,
                   settings=dict(temperature="provider_default(未送信)", reasoning_thinking="provider_default(未送信)", max_tokens=C.MAX_OUT, system="なし"),
                   attempts=r["attempts"], ok=r["ok"], elapsed_s_total=round(time.time() - t0, 2))
        cost = 0.0
        if r["ok"]:
            usage = r["usage"]; cost = C.cost_usd(m["model_id"], usage) * C.USD_JPY
            rec.update(response_text=r["text"], usage=usage, response_id=r["response_id"], model_returned=r["model_returned"], finish=r["finish"], cost_jpy=round(cost, 5),
                       raw_response=r["raw"])
            C.ledger_add(dict(phase="selection", model_key=mk, unit_id=u["unit_id"], requested=m["model_id"], returned=r["model_returned"], usage=usage, cost_jpy=round(cost, 5),
                              response_id=r["response_id"], ts=time.strftime("%Y-%m-%dT%H:%M:%S")))
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf8")
        return (mk, u["unit_id"], "OK" if r["ok"] else "TECH_FAIL", cost)
    # provider別に並列(rate limit配慮: provider内workers、providerは同時)
    res = []
    with ThreadPoolExecutor(max_workers=a.workers * 3) as ex:
        futs = [ex.submit(run, j) for j in jobs]
        for f in as_completed(futs):
            r = f.result(); res.append(r); print(r, "cum_jpy=%.3f" % C.ledger_total_jpy(), flush=True)
    print("done", len(res), "tech_fail", [r for r in res if r[2] != "OK"], "total_jpy=%.3f" % C.ledger_total_jpy())
    return 0

if __name__ == "__main__":
    sys.exit(main())

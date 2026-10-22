# -*- coding: utf-8 -*-
r"""KPMG Trial①: 最小化Prompt x 5モデル x 14本文 = 70選定(有料)。Trial専用。初回生成1回、品質理由の再生成なし(技術的失敗のみ同一入力で最大2回再試行)。
使い方: .venv\Scripts\python.exe er101_kp_prompt_min_gen_trial_02_run.py --out er101_output/kp_prompt_min_gen_trial_02 --manifest er098_output/kp_six_model_trial_01/inputs/manifest.json --cap-jpy 300 [--dry-run]
既存runs/<model>/<unit>.jsonはスキップ(再課金防止)。"""
import argparse, json, sys, time, hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import er101_kp_prompt_min_gen_trial_02_common as K
C = K.C

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(K.OUT)); ap.add_argument("--manifest", default=str(K.MANIFEST_PREV))
    ap.add_argument("--cap-jpy", type=float, default=300.0); ap.add_argument("--units", default=""); ap.add_argument("--models", default="")
    ap.add_argument("--workers", type=int, default=4); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    out = Path(a.out); man = json.loads(Path(a.manifest).read_text(encoding="utf8"))
    prompt = (out / "inputs" / "prompt_fixed.txt").read_text(encoding="utf8")
    units = [u for u in man["units"] if u.get("copy_path") and (not a.units or u["unit_id"] in a.units.split(","))]
    models = {k: v for k, v in K.MODELS.items() if (not a.models or any(k.startswith(x) for x in a.models.split(",")))}
    if K.stop_present(): print("STOPセンチネルあり"); return 3
    jobs = []
    for u in units:
        raw = (C.ROOT / u["copy_path"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == u["copy_sha256"], "本文sha不一致 " + u["unit_id"]
        art = raw.decode("utf8")
        for mk, m in models.items():
            rp = out / "runs" / mk / ("%s.json" % u["unit_id"])
            if rp.exists(): continue
            user = prompt + "\n\n---\n\n【記事本文】\n" + art      # KP6Mと同一の受け渡し(Prompt無改変)
            jobs.append((mk, m, u, user, rp))
    print("jobs", len(jobs), "models", list(models), "units", len(units))
    if a.dry_run:
        for mk, m, u, user, rp in jobs[:2]: print(mk, u["unit_id"], len(user), json.dumps(C.build_body(m["provider"], m["model_id"], user), ensure_ascii=False)[:200])
        return 0
    def run(job):
        mk, m, u, user, rp = job
        if K.stop_present(): return (mk, u["unit_id"], "STOPPED", 0.0)
        if C.ledger_total_jpy() >= a.cap_jpy: return (mk, u["unit_id"], "CAP_REACHED", 0.0)
        body = C.build_body(m["provider"], m["model_id"], user)
        t0 = time.time(); r = C.call_with_retry(m["provider"], m["model_id"], body)
        rec = dict(model_key=mk, requested_model_id=m["model_id"], provider=m["provider"], unit_id=u["unit_id"], article_id=u["article_id"], level=u["level"],
                   article_sha256=u["copy_sha256"], prompt_sha256=C.sha_text(prompt), user_message_sha256=C.sha_text(user), request_body=body,
                   settings=dict(temperature="provider_default(未送信)", reasoning_thinking="provider_default(未送信)", max_tokens=C.MAX_OUT, system="なし"),
                   attempts=r["attempts"], ok=r["ok"], elapsed_s_total=round(time.time() - t0, 2))
        cost = 0.0
        if r["ok"]:
            cost = C.cost_usd(m["model_id"], r["usage"]) * C.USD_JPY
            rec.update(response_text=r["text"], usage=r["usage"], response_id=r["response_id"], model_returned=r["model_returned"], finish=r["finish"], cost_jpy=round(cost, 5), raw_response=r["raw"])
            C.ledger_add(dict(phase="selection", model_key=mk, unit_id=u["unit_id"], requested=m["model_id"], returned=r["model_returned"], usage=r["usage"], cost_jpy=round(cost, 5),
                              response_id=r["response_id"], ts=time.strftime("%Y-%m-%dT%H:%M:%S")))
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf8")
        return (mk, u["unit_id"], "OK" if r["ok"] else "TECH_FAIL", cost)
    res = []
    with ThreadPoolExecutor(max_workers=a.workers * 3) as ex:
        for f in as_completed([ex.submit(run, j) for j in jobs]):
            r = f.result(); res.append(r); print(r, "cum_jpy=%.3f" % C.ledger_total_jpy(), flush=True)
    print("done", len(res), "not_ok", [r for r in res if r[2] != "OK"], "total_jpy=%.3f" % C.ledger_total_jpy())
    return 0

if __name__ == "__main__":
    sys.exit(main())

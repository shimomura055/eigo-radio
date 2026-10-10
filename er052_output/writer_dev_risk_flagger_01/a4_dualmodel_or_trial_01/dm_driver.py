# -*- coding: utf-8 -*-
"""A4-DUALMODEL-OR-TRIAL-01: POST-EN 11本 x A3/A4 x {Luna, Gemini 3.5 Flash-Lite}。
入力構築=post_en_common.build_unit(POST-EN-TRIAL-01と同一)、Provider adapter=meta_rollback_crossmodel_01/xm_driver.py(import流用、変更なし)。
usage:
  dm_driver.py dry                          44 request payloadを dry_run/ へ保存し、既存Sol rawとprompt完全一致をassert(API非呼び出し)
  dm_driver.py run <luna|gemini35fl> --execute   11記事 x A3,A4 を実行(既存結果があれば上書きせず停止)
"""
import json, os, sys, time
sys.dont_write_bytecode = True
DHERE = os.path.dirname(os.path.abspath(__file__))
XM = os.path.join(DHERE, "..", "meta_rollback_crossmodel_01"); sys.path.insert(0, XM)
import xm_driver as X            # chdir(REPO), dotenv, post_en_common の名前を内包
from xm_driver import C, L, R, P, A, REPO, sha_b, EFFORT, MAX_OUT, CONDS, PRICES, build_request, call_adapter, RAW_HTTP
PE = os.path.join(DHERE, "..", "post_en_trial_01")
EXPECT_SHA = {3: "9d9950428419c3af824cc5b8676a4b564f96aeb87657c547d418cc86ef3538e9", 4: "c87b95e5bcf1b5c266b8978c5688849eb339a6087efbcaf56bb7399ed128ef01"}
MODELS = ["luna", "gemini35fl"]
CAP_TOTAL = 100.0; MAX_CELL = 8.0
LEDGER_DM = os.path.join(DHERE, "cost_ledger_dm_01.jsonl")
man = C.load_manifest()
UNITS = man["units"]

def prev_req(level, u):
    p = os.path.join(PE, "logs", "d2_gpt-6.1-sol_pe_A%d_%s_%s_raw.jsonl" % (level, u["unit"], u["theme"]))
    return json.loads(open(p, encoding="utf-8").readline())["request"], p

def system_for(level):
    s = A.antenna_system(level); assert A.sha(s) == EXPECT_SHA[level], "prompt sha mismatch A%d" % level; return s

def cmd_dry():
    out = os.path.join(DHERE, "dry_run"); os.makedirs(out, exist_ok=True)
    rep = dict(n_payloads=0, articles={}, models=MODELS)
    for u in UNITS:
        unit, facts, ss = C.build_unit(u, man)
        for lv in (3, 4):
            sysm = system_for(lv); user = P.build_user(unit)
            pr, ppath = prev_req(lv, u)
            assert sysm == pr["system"] and user == pr["user"], "request differs from existing post_en raw: %s A%d" % (u["unit"], lv)
            rep["articles"].setdefault(u["unit"], {})["A%d" % lv] = dict(system_sha=A.sha(sysm), user_sha=sha_b(user.encode("utf-8")), prev_raw=ppath.replace("\\", "/"),
                                                                       system_equal=True, user_equal=True, n_sentences=len(ss), n_facts=len(facts))
            for k in MODELS:
                url, hdr, body = build_request(CONDS[k], sysm, user)
                d = os.path.join(out, k, u["unit"]); os.makedirs(d, exist_ok=True)
                json.dump(dict(model_key=k, level=lv, unit=u["unit"], endpoint=url, extra_headers=hdr, auth="(鍵は記録しない)", body=body),
                          open(os.path.join(d, "A%d_request.json" % lv), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
                rep["n_payloads"] += 1
    json.dump(rep, open(os.path.join(out, "dry_run_report_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("dry OK payloads=%d (all A3/A4 system+user == existing post_en raw)" % rep["n_payloads"])

def run_cell(model_key, level, u):
    cond = CONDS[model_key]; mid = cond["model_id"]; pr = PRICES[mid]
    unit, facts, ss = C.build_unit(u, man); sysm = system_for(level)
    run_dir = os.path.join(DHERE, "runs", model_key, u["unit"]); os.makedirs(run_dir, exist_ok=True)
    out_json = os.path.join(run_dir, "A%d.json" % level)
    assert not os.path.exists(out_json), "既存結果あり(上書き禁止): " + out_json
    L.LEDGER_PATH = LEDGER_DM
    L.MODELS[model_key] = dict(provider="xm", env_key="-", max_out=MAX_OUT)
    L.load_prices = lambda m: (pr["in"], pr["cached"], pr["out"]) if m == model_key else None
    L.client_for = lambda cfg: None
    L.call_model = lambda client, model, system, user, max_out=None, effort="medium", cache_key=None: call_adapter(model_key, level, system, user)
    P.d2_system = lambda: A.antenna_system(level)
    R.RESULTS_DIR = run_dir; R.LOGS_DIR = run_dir
    cell = "dm_A%d_%s" % (level, u["unit"])
    t0 = time.time(); ts = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    rc = R.run_llm([unit], "d2", model_key, cell, MAX_CELL, CAP_TOTAL, None, EFFORT, None, False)
    el = time.time() - t0
    rp = R.result_paths("d2", model_key, cell)
    if not os.path.exists(rp[0]):
        print("STOP rc=%s (結果なし)" % rc); return rc
    d2 = json.loads(open(rp[0], encoding="utf-8").readline())
    raw = [json.loads(x) for x in open(rp[1], encoding="utf-8") if x.strip()]
    out = dict(level=level, unit=u["unit"], theme=u["theme"], model_key=model_key, label=cond["label"], model_id_requested=mid,
               model_ids_returned=sorted({str(r.get("model_id")) for r in raw if r.get("model_id")}), provider=cond["provider"],
               thinking_setting="provider_default", started=ts, system_prompt_sha256=A.sha(sysm), user_sha256=sha_b(P.build_user(unit).encode("utf-8")),
               input_sha256=u["input_sha256"], max_out=MAX_OUT, effort=(EFFORT if cond["provider"] == "openai" else None),
               rc=rc, valid_json=d2["valid_json"], attempts=d2["attempts"], cost_jpy=d2["cost_jpy"], elapsed_s=round(el, 2),
               usage=[r.get("usage") for r in raw if r.get("usage")], errors=[r["error"] for r in raw if r.get("error")],
               violations=[r.get("violations") for r in raw if "violations" in r],
               flags=d2["flags"], sentences={s["sid"]: s["text"] for s in ss}, facts={f["fact_id"]: f["text"] for f in facts},
               raw_http=RAW_HTTP.pop((model_key, level), []))
    json.dump(out, open(out_json, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(model_key, "A%d" % level, u["unit"], "flags=%d cost=%.3f valid=%s attempts=%s rc=%s" % (len(d2["flags"]), d2["cost_jpy"], d2["valid_json"], d2["attempts"], rc), flush=True)
    return rc

def cmd_run(model_key):
    assert "--execute" in sys.argv and model_key in MODELS
    for u in UNITS:
        for lv in (3, 4):
            rc = run_cell(model_key, lv, u)
            if rc not in (0, None):
                print("STOP: rc=%s" % rc); sys.exit(2)
    print(model_key, "DONE ledger_total=%.3f" % L.ledger_total(LEDGER_DM))

if __name__ == "__main__":
    a = sys.argv[1]
    if a == "dry": cmd_dry()
    elif a == "run": cmd_run(sys.argv[2])
    else: sys.exit("unknown")

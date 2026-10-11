# Trial専用: Azure Secondary(Phrase Listなし)を保存wavへ1回ずつ。累計費用をcall前に確認。
import sys, json, time, math, os
sys.path.insert(0, "er053_output/open258_phase0_trial_01")
from open258_phase0_common import *
import er003_b1_p4_audio as p4
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
load_dotenv()
region = os.getenv("SPEECH_REGION")
sel = json.load(open(OUT + "/manifest_selected_01.json", encoding="utf8"))
order = {"A_meta": 0, "C_negative": 1, "C_negative_in_rescue_group": 1, "B_rescue_candidate": 2, "P_exclusion_probe": 3}
calls = sorted([r for r in sel if r.get("plan_call")], key=lambda r: (order.get(r["role_run"], 9)))
rp = OUT + "/results_01.jsonl"
done = set()
if os.path.exists(rp):
    for l in open(rp, encoding="utf8"):
        done.add(json.loads(l)["key"])
cum = sum(math.ceil(json.loads(l)["duration_s"]) for l in open(rp, encoding="utf8")) * JPY_PER_SEC if os.path.exists(rp) else 0.0
stop = False
for r in calls:
    key = f'g{r["group"]}_{r["seg"]}_a{r["attempt"]}'
    if key in done: continue
    cost = math.ceil(r["duration_s"]) * JPY_PER_SEC
    if cum + cost > BUDGET_JPY:
        print("STOP budget", cum, cost); break
    t0 = time.time()
    text, err = p4.get_full_text_via_azure_stt_continuous(r["wav"], language="ja-JP")
    wall = time.time() - t0
    cum += cost
    rec = {"key": key, "group": r["group"], "role": r["role_run"], "seg": r["seg"], "attempt": r["attempt"], "wav": r["wav"], "sha256": r["sha256"],
           "duration_s": r["duration_s"], "canonical": r["canonical"], "primary_asr": r["primary_asr"],
           "service": "Azure Speech STT (SDK recognizer start_continuous_recognition, standard, no Phrase List)", "azure_region": region,
           "speech_sdk_version": speechsdk.__version__, "language": "ja-JP", "phrase_list": False,
           "secondary_text": text, "error": err, "wall_seconds": round(wall, 2),
           "est_cost_jpy": round(cost, 4), "cum_est_cost_jpy": round(cum, 4),
           "existing_exclusions": r["existing_exclusions"], "extra_exclusions": r["extra_exclusions"],
           "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
    rec.update(secondary_judge(r["canonical"], text) if text is not None else {"sec_cls": "UNAVAILABLE", "sec_pass": False, "basis": "Secondary取得不能(従来どおり再生成扱い)", "sec_diff_ops": []})
    open(rp, "a", encoding="utf8").write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(key, r["role_run"], "|", text, "| pass" if rec["sec_pass"] else "| NG", rec["sec_cls"], f"{wall:.1f}s cum¥{cum:.2f}", flush=True)
    if r["role_run"].startswith("C_") and rec["sec_pass"]:
        print("!!! 誤PASS候補検出 -> STOP"); stop = True; break
print("done cum", round(cum, 3))

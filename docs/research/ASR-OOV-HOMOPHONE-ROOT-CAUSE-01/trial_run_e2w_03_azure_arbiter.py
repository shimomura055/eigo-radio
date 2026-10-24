# trial_run_e2w_03_azure_arbiter.py -- 委任_03 OF-OOV-11: E2Wが誤受理した負例3clip(scold/spool/cull)を第3エンジン(Azure STT、PhraseListなし)で聞き直す。上限2円・1起動。cl.install で実コスト記録。
import json, os, subprocess, sys, wave
sys.path.insert(0, "."); from dotenv import load_dotenv; load_dotenv()
D = "docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01"; OUT = D + "/work/trial03_azure_arbiter"; os.makedirs(OUT, exist_ok=True)
if os.path.exists(OUT + "/azure_arbiter_result.json"): raise SystemExit("already ran")
if subprocess.run([sys.executable, "tools/stop_scope_check_01.py", "--managed-id", "ASR-OOV-HOMOPHONE-ROOT-CAUSE-01", "--run-dir", D, "--out", OUT + "/stop_check_paid.json"]).returncode != 0:
    raise SystemExit("stop")
import er005_cost_logger as cl; cl.install(OUT + "/cost/usage_log.jsonl")
import er006_secondary_asr_01 as S
clips = [(f"{n}", D + f"/work/trial03/clips/{n}.wav") for n in ("n_skool_scold", "n_skool_spool", "n_kewl_cull")]
rows = []
for label, pth in clips:
    with wave.open(pth) as w: sec = w.getnframes() / w.getframerate()
    txt, err = S.get_full_text_via_azure_stt_with_phrase_list(pth, language="en-US", phrases=None)
    rows.append({"label": label, "azure": txt, "err": err, "sec": round(sec, 2)}); print(label, "->", txt or err, flush=True)
json.dump(rows, open(OUT + "/azure_arbiter_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# trial_run_e2_02_azure_arbiter.py -- 音声負例のうちPrimary/ローカルWhisperが『同音語側』に揃った3clip(loft/left/stool)を第3エンジン(Azure STT、PhraseListなし)で聞き直し、
# 『音声は本当に別語だったがASRが文脈で寄せた』のか『TTSが実際に同音語を読んだ(負例として無効)』のかを切り分ける。上限2円・1起動。cl.install で実コスト記録。
import json, os, subprocess, sys, wave
sys.path.insert(0, "."); from dotenv import load_dotenv; load_dotenv()
D = "docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01"; OUT = D + "/work/trial02_azure_arbiter"; os.makedirs(OUT, exist_ok=True)
if subprocess.run([sys.executable, "tools/stop_scope_check_01.py", "--managed-id", "ASR-OOV-HOMOPHONE-ROOT-CAUSE-01", "--run-dir", D, "--out", OUT + "/stop_check_paid.json"]).returncode != 0:
    raise SystemExit("stop")
import er005_cost_logger as cl; cl.install(OUT + "/cost/usage_log.jsonl")
import er006_secondary_asr_01 as S
clips = [("neg_lyft_loft(spoken=loft)", D + "/work/trial02/clips/neg_lyft_loft.wav"), ("n2_lyft_left(spoken=left)", D + "/work/trial02_neg2/clips/n2_lyft_left.wav"),
         ("n2_skool_stool(spoken=stool)", D + "/work/trial02_neg2/clips/n2_skool_stool.wav"), ("neg_kewl_coal(spoken=coal)", D + "/work/trial02/clips/neg_kewl_coal.wav")]
rows = []
for label, pth in clips:
    with wave.open(pth) as w: sec = w.getnframes() / w.getframerate()
    txt, err = S.get_full_text_via_azure_stt_with_phrase_list(pth, language="en-US", phrases=None)
    rows.append({"label": label, "azure": txt, "err": err, "sec": round(sec, 2)}); print(label, "->", txt or err, flush=True)
json.dump(rows, open(OUT + "/azure_arbiter_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# azure_window_arm_01.py -- 候補C(Primary NG時のSecondaryを発話窓だけに絞る/PhraseListの効果)の実測。Trial専用。上限: 約5円。
# 窓(約6秒)8本 x {PhraseListなし, PhraseList=[gacha]} と、masking対照(別語を言っている音声)x PhraseList=[gacha]。
import json, os, sys, time
sys.path.insert(0, ".")
import soundfile as sf
import er006_secondary_asr_01 as S
import er005_cost_logger as CL
CL.init_logger('docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/work/raw_usage_log_trial.jsonl')
W = "docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/work"; log = []
def az(path, label, phrases):
    t = time.time(); txt, err = S.get_full_text_via_azure_stt_with_phrase_list(path, language="en-US", phrases=phrases)
    d = sf.info(path).duration
    log.append({"label": label, "phrases": phrases, "text": txt, "err": err, "audio_sec": round(d, 2)}); print(label, phrases, "->", txt or err, flush=True)
for n in range(1, 9):
    for ph in (None, ["gacha"]): az(f"{W}/windows/att{n}_win.wav", f"real_att{n}", ph)
os.makedirs(f"{W}/ctrl_wav", exist_ok=True)
for w in ["gaycha", "catcher", "gadget", "gutter", "gotcha", "gacha"]:
    y, sr = sf.read(f"{W}/ctrl/{w}.mp3"); p = f"{W}/ctrl_wav/{w}.wav"; sf.write(p, y, sr)
    az(p, f"ctrl_{w}", ["gacha"])
json.dump(log, open(f"{W}/azure_window_arm_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("calls", len(log), "audio_sec", round(sum(x["audio_sec"] for x in log), 1), "est_yen", round(sum(x["audio_sec"] for x in log) * 0.0444, 2))

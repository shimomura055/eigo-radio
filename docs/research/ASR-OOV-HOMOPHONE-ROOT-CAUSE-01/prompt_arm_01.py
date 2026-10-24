# prompt_arm_01.py -- 候補A(Primary ASR promptへ語彙ヒント)の効果と誤PASSリスクの実測。Trial専用(Production無変更)。
# 呼出は Production の routing.transcribe(prompt=...) をそのまま使う(言語 en)。上限: 本スクリプト合計 約5円(委任上限15円内)。
# (i) 実音声: 保存wavの gacha 発話窓(約6秒) 8本 x {prompt無/prompt有}
# (ii) masking対照: 『音声が別語を実際に言っている』クリップに prompt='gacha' を渡しても gacha と書き起こされないか(=誤PASS検査)
import json, os, sys, time
sys.path.insert(0, ".")
import er006_asr_provider_routing_01 as routing
from dotenv import load_dotenv; load_dotenv()
W = "docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/work"
PROMPTS = {"none": None, "word": "gacha", "sentence": "The transcript may contain the word gacha."}
log = []
def asr(path, label, pk):
    t = time.time(); txt, err = routing.transcribe(path, language="en-US", prompt=PROMPTS[pk])
    log.append({"label": label, "prompt": pk, "text": txt, "err": err, "sec": round(time.time() - t, 2)}); print(label, pk, "->", txt or err, flush=True)
for n in range(1, 9):
    for pk in PROMPTS: asr(f"{W}/windows/att{n}_win.wav", f"real_att{n}", pk)
# (ii) 対照音声: OpenAI TTS(別系統)で『本当にその語を言っている』音声を作る
from openai import OpenAI
cli = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
os.makedirs(f"{W}/ctrl", exist_ok=True)
words = ["gacha", "gotcha", "catcher", "gadget", "gutter", "gotta", "got you", "gaycha"]
for w in words:
    p = f"{W}/ctrl/{w.replace(' ', '_')}.mp3"
    if not os.path.exists(p):
        r = cli.audio.speech.create(model="tts-1", voice="alloy", input=f"It's unexpected to find a {w} at the entrance, though.")
        open(p, "wb").write(r.content)
    for pk in PROMPTS: asr(p, f"ctrl_{w}", pk)
json.dump(log, open(f"{W}/prompt_arm_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("calls", len(log))

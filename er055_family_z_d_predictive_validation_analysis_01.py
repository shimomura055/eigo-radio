# er055 分析(machine check、LLM評価なし、費用0)。Trial専用。Production非参照。
import json, re, os, statistics as st
B = "er055_output/family_z_d_predictive_validation_trial_01"
SCENES = {
 "L13": [("S1 極楽の蓮池で釈迦が下を見る", r"lotus pond.*Buddha|Buddha.*lotus pond"),
         ("S2 地獄で苦しむ陀多(血の池/針の山は省略可)", r"hell"),
         ("S3 陀多は大泥坊(殺人・放火の悪人)という背景", r"thie|murder|kill|crime|evil|bad man|robber"),
         ("S4 生前、蜘蛛を踏まず助けた一善", r"spider.*(crawl|stepped|foot)|stepped.*spider"),
         ("S5 釈迦が蜘蛛の糸を下ろす", r"lowered|thread"),
         ("S6 陀多が糸を登る", r"climb"),
         ("S7 下から無数の罪人が登ってくる(蟻の行列)", r"prisoners.*climbing|climbing after"),
         ("S8 「この糸は己のものだ」と叫ぶ", r"mine|escape alone"),
         ("S9 糸が切れ地獄へ落ちる", r"snapped|fell"),
         ("S10 釈迦の悲しみ(無慈悲な心への浅ましさ)", r"sad"),
         ("S11 蓮は無頓着に咲く(余韻)", r"lotus flowers|pond stayed calm")],
 "L11": [("S1 京都をさまよう病・借金の不吉な塊を抱える私", r"cough|money|heavy feeling"),
         ("S2 みすぼらしい美しいものを好む", r"old things|faded|worn"),
         ("S3 寺町の果物屋", r"Teramachi|fruit shop"),
         ("S4 檸檬を一つ買う", r"one lemon|bought"),
         ("S5 檸檬の冷たさ・色・匂いで気分が晴れる", r"cool|smell|yellow"),
         ("S6 丸善(かつて好きだったが今は重苦しい)", r"Maruzen"),
         ("S7 画集を積み上げ城を作る", r"pile|tower"),
         ("S8 檸檬を頂上に置く", r"set it on|on the tower|on the highest"),
         ("S9 檸檬=爆弾と想像(丸善が大爆発)", r"bomb|burst"),
         ("S10 何食わぬ顔で出て行く/くすぐったい微笑", r"walked out|laugh|smil"),
         ("S11 店を出た後に爆発を想像し続ける(10分後の大爆発)", r"ten minutes|explod|burst.*after|after.*left")],
}
def sents(t):
    t = re.sub(r"\s+", " ", t)
    return [s for s in re.split(r"(?<=[.!?])[\"”’]?\s+", t) if s.strip()]
out = {}
for w in ("L13", "L11"):
    raw = open(f"{B}/{w}/story_en.md", encoding="utf-8").read()
    body = re.sub(r"^###.*\n+", "", raw)
    words = re.findall(r"[A-Za-z']+", body)
    ss = sents(body); sl = [len(re.findall(r"[A-Za-z']+", s)) for s in ss]
    long_ = sorted({x.lower() for x in words if len(x) >= 9})
    caps = sorted({m for m in re.findall(r"(?<![.!?”\"]\s)(?<!^)\b([A-Z][a-z]+)\b", body)} - {"I"})
    paras = [p for p in body.split("\n\n") if p.strip()]
    nums = re.findall(r"\b\d+\b", body)
    scene = [(n, bool(re.search(p, body, re.I | re.S))) for n, p in SCENES[w]]
    out[w] = {"words": len(words), "sentences": len(ss), "sent_len_mean": round(st.mean(sl), 1),
              "sent_len_median": st.median(sl), "sent_len_max": max(sl), "sent_len_gt20": sum(1 for x in sl if x > 20),
              "sent_len_le8": sum(1 for x in sl if x <= 8), "long_words_ge9": long_, "types": len({x.lower() for x in words}),
              "type_token": round(len({x.lower() for x in words}) / len(words), 3), "paragraphs": len(paras),
              "capitalized_tokens": caps, "numbers": nums, "title_line": raw.startswith("###"),
              "scenes": [{"scene": n, "present_by_keyword": p} for n, p in scene],
              "scene_hit": f"{sum(p for _, p in scene)}/{len(scene)}"}
json.dump(out, open(f"{B}/analysis_machine_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(json.dumps(out, ensure_ascii=False, indent=1))

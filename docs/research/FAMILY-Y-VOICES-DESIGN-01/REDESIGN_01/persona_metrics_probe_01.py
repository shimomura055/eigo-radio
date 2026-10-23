# -*- coding: utf-8 -*-
"""REDESIGN_01 probe(API 0): 日本語Voice段落の簡易定量指標。評価基準(DESIGN_PROPOSAL_03 §7)の数値化可能項目の素案と既存Trialのbaseline測定用。
判定器ではない(目視評価の補助)。語彙リストは素案で、Phase B前にOpus/Fableが見直す。"""
import re, sys, json, statistics as st
ABSTRACT = ["責任","判断","根拠","優先","基準","価値","尊厳","余地","視点","観点","目的","方針","配分","効果","学力","環境","仕組み","重さ","納得","立場","意味","自分","他者","必要","理由","大切","守り"]
EMOTION = ["怖","こわ","嫌","いや","腹が立","むかつ","悔し","うれし","嬉し","ほっと","不安","つらい","辛い","しんどい","情けな","恥ずかし","寂し","さみし","悲し","安心","焦","イライラ","ありがた","助か","申し訳","罪悪","笑","泣","くやし","心配","疲れ"]
HEDGE = ["だろう","かもしれ","のかな","ではないか","だろうか","かな。","のか。","と思う","気がする","とは限ら"]
ASSERT = ["べきだ","してほしい","ほしい。","てくれ","やめて","ない。","だ。","んだ。","ません"]
def split_sents(t): return [s for s in re.split(r"(?<=[。！？!?])", t) if s.strip()]
def metrics(t):
    s = split_sents(t); L = [len(x) for x in s]; n = max(1, len(t))
    return {"chars": len(t), "sentences": len(s), "mean_sent_len": round(st.mean(L),1) if L else 0, "sd_sent_len": round(st.pstdev(L),1) if len(L)>1 else 0,
            "abstract_per_100": round(100*sum(t.count(w) for w in ABSTRACT)/n,2), "emotion_hits": sum(t.count(w) for w in EMOTION),
            "hedge_hits": sum(t.count(w) for w in HEDGE), "assert_hits": sum(t.count(w) for w in ASSERT),
            "question_marks": t.count("？")+t.count("?"), "ends_with_nda": sum(1 for x in s if re.search(r"んだ。$", x.strip()))}
if __name__ == "__main__":
    txt = open(sys.argv[1], encoding="utf-8").read().strip()
    paras = [p for p in re.split(r"\n\s*\n", txt) if p.strip()]
    title, body = paras[0], paras[1:]
    names = ["lead","voice_1","voice_2","voice_3","final"] if len(body)==5 else [f"p{i}" for i in range(len(body))]
    out = {n: metrics(p) for n, p in zip(names, body)}
    v = [out[k] for k in out if k.startswith("voice")]
    if len(v)==3:
        out["_voice_spread"] = {"mean_sent_len_range": round(max(x["mean_sent_len"] for x in v)-min(x["mean_sent_len"] for x in v),1),
                                 "ends_with_nda_total": sum(x["ends_with_nda"] for x in v)}
    print(json.dumps(out, ensure_ascii=False, indent=1))

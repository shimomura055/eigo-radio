# ukus_sim_01.py -- 設計の実現性確認(API 0・DEV/Trial相当の机上シミュレーション。Production未配線・er109本体は変更しない)。
# 方式: er109._units が返すword unitの key を『US正規形』に写像(語彙=VarCon+breame、AMB対は canonical=UK→ASR=US の一方向のみ、
#       制限規則 ise/ize,yse/yze,our/or は辞書外でも stem>=4 かつ 目標語がwordfreq実在のときのみ)してから er109.evaluate を呼ぶ。
import sys, os, re, json
sys.path.insert(0, "."); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import er109_asr_orthographic_equivalence_01 as e
import ukus_lexicon_01 as lex
from wordfreq import zipf_frequency
UK2US, US2UK, AMB = lex.build_pair_index()
R2 = [("isation","ization"),("isations","izations"),("ise","ize"),("ised","ized"),("ises","izes"),("ising","izing"),("iser","izer"),("isers","izers"),
      ("yse","yze"),("ysed","yzed"),("yses","yzes"),("ysing","yzing"),("our","or"),("ours","ors"),("oured","ored"),("ouring","oring"),("ourful","orful"),("ourite","orite")]
def rule_us(w):
    for u, a in R2:
        if w.endswith(u) and len(w) - len(u) >= 4:
            t = w[:-len(u)] + a
            if zipf_frequency(t, "en") >= 1.5: return t
    return None
def to_us(w, side):
    lw = w.lower()
    if lw in UK2US:
        c = sorted(UK2US[lw])
        if any((lw, u) in AMB for u in c) and side != "c": return None      # AMB: UK形はcanonical側のみUS化(ASR側のUK形は同値化しない)
        return c[0]
    r = rule_us(lw)
    return r
_orig = e._units
_calls = {"n": 0}
def patched(text, entity_tokens):
    units = _orig(text, entity_tokens)
    side = "c" if _calls["n"] % 2 == 0 else "a"
    _calls["n"] += 1
    for u in units:
        if u.kind == "word":
            us = to_us(u.surface.rstrip("."), side)
            if us: u.key = us; u.prons = u.prons or {("UKUS",)}     # 辞書外(CMU未登録)でも bad に落とさない
    return units
def ev(c, a, on):
    _calls["n"] = 0
    e._units = patched if on else _orig
    try: return e.evaluate(c, a)
    finally: e._units = _orig
if __name__ == "__main__":
    out = {}
    c12c = "Inventing convincing stories at a moment's notice was Vera's speciality."
    c12a = "Inventing convincing stories at a moment's notice was Vera's specialty."
    r0, r1 = ev(c12c, c12a, False), ev(c12c, c12a, True)
    out["c12"] = {"er109_now": r0.verdict + ":" + r0.reason, "ukus_on": r1.verdict + ":" + r1.reason}
    print(out["c12"])
    POS = "speciality/specialty colour/color favour/favor honour/honor neighbour/neighbor organise/organize realise/realize analyse/analyze centre/center theatre/theater metre/meter litre/liter fibre/fiber defence/defense offence/offense catalogue/catalog travelled/traveled cancelled/canceled jewellery/jewelry aluminium/aluminum grey/gray plough/plow mould/mold moustache/mustache pyjamas/pajamas sceptic/skeptic aeroplane/airplane ageing/aging judgement/judgment acknowledgement/acknowledgment artefact/artifact manoeuvre/maneuver paediatric/pediatric encyclopaedia/encyclopedia fulfil/fulfill enrol/enroll skilful/skillful behaviour/behavior labour/labor humour/humor rumour/rumor vapour/vapor sulphur/sulfur learnt/learned dreamt/dreamed organisation/organization recognised/recognized apologising/apologizing civilisation/civilization colourful/colorful flavour/flavor harbour/harbor armour/armor savour/savor endeavoured/endeavored".split()
    pos_res = []
    for p in POS:
        x, y = p.split("/")
        for (cw, aw, d) in ((x, y, "uk->us"), (y, x, "us->uk")):
            c = f"She said the {cw} was very important to them."; a = f"She said the {aw} was very important to them."
            r0, r1 = ev(c, a, False), ev(c, a, True)
            pos_res.append({"pair": p, "dir": d, "base_eq": r0.equivalent, "on_eq": r1.equivalent, "on_verdict": r1.verdict})
    out["positives"] = pos_res
    NEG = "advice/advise ensure/insure complement/compliment principal/principle stationary/stationery affect/effect discreet/discrete canon/cannon device/devise prophecy/prophesy practical/practise specialty/special speciality/specially colour/collar grey/great centre/central hour/our four/for pour/poor tour/tore flour/floor story/stir program/progress jewellery/jewel cheque/cheek surprise/surprize licence/lioness honour/hammer organise/organs realise/relies analyse/analysis storey/story metre/mother tire/tyre".split()
    neg_res = []
    for p in NEG:
        x, y = p.split("/")
        for (cw, aw) in ((x, y), (y, x)):
            c = f"She said the {cw} was very important to them."; a = f"She said the {aw} was very important to them."
            r0, r1 = ev(c, a, False), ev(c, a, True)
            neg_res.append({"pair": f"{cw}->{aw}", "base_eq": r0.equivalent, "on_eq": r1.equivalent})
    out["negatives"] = neg_res
    p_ok = sum(1 for r in pos_res if r["on_eq"]); p_new = sum(1 for r in pos_res if r["on_eq"] and not r["base_eq"])
    n_new = [r["pair"] for r in neg_res if r["on_eq"] and not r["base_eq"]]
    print("positives", len(pos_res), "on_eq", p_ok, "newly passed", p_new, "base_eq", sum(1 for r in pos_res if r["base_eq"]))
    print("negatives", len(neg_res), "newly PASS (must be 0):", n_new, "| base already eq:", [r["pair"] for r in neg_res if r["base_eq"]])
    print("pos failing:", [(r["pair"], r["dir"]) for r in pos_res if not r["on_eq"]])
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ukus_sim_01.json"), "w"), indent=1)

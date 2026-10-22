# -*- coding: utf-8 -*-
"""推定(E2=G2P決定論, E3=低コストLLM gpt-6-luna(web無し))。Trial専用。ESTIMATEDは判定側基準としてのみ使う(TTSヒント/M1/Phrase Listへ供給しない)。
paid_calls.jsonl は er100_output/pnps_stage2_trial_01/paid_calls.jsonl に追記(鍵は出力しない)。"""
import json, os, re, sys, time
sys.path.insert(0, os.getcwd())
from pathlib import Path
from er100_pnps_stage2_trial_01_common import *
import er098_kp_six_model_trial_01_common as C
from er006_m1_multi_candidate_01 import ipa_to_arpa

C.LEDGER = Path(OUT) / "paid_calls.jsonl"
C.OUT = Path(OUT)
MODEL = "gpt-6-luna"
SYS = ("You are a phonetics assistant for an English-learning radio program. Given an English-language sentence and one term from it "
       "(a brand, person name, place or foreign loanword), list the 1 to 3 most plausible pronunciations that a well-informed native "
       "English (US) newsreader would use for that term in this sentence. Give IPA (US) for each. State whether the first one is the "
       "official/ established pronunciation you actually know (official=true) or only a reasonable estimate from spelling and origin (official=false). "
       "Do not invent sources. Output JSON only: {\"pronunciations\":[{\"ipa\":\"...\",\"respelling\":\"...\"}],\"official\":true|false,\"origin\":\"...\"}")


def strip_stress(seq):
    return tuple(re.sub(r"\d", "", p) for p in seq)


def e2_g2p(word):
    from g2p_en import G2p
    g = _G2P[0] if _G2P else _G2P.append(G2p()) or _G2P[0]
    return strip_stress([p for p in g(word) if re.match(r"[A-Z]+\d?$", p)])


_G2P = []


def sentence_with(canon, word):
    for s in re.split(r"(?<=[.!?])\s+", canon):
        if word in norm_tokens(s):
            return s.strip()
    return canon[:300]


def e3_llm(word, spelled, sentence):
    user = f"Sentence: {sentence}\nTerm: {spelled}"
    body = C.build_body("openai", MODEL, user, system=SYS, extra={"max_output_tokens": 2000})
    r = C.call_with_retry("openai", MODEL, body)
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "kind": "e3_luna_estimate", "word": word, "model": MODEL, "ok": r["ok"]}
    if not r["ok"]:
        rec["attempts"] = r["attempts"]; C.ledger_add(rec); return None
    usd = C.cost_usd(MODEL, r["usage"]); rec.update(usage=r["usage"], cost_jpy=round(usd * C.USD_JPY, 4), response_id=r["response_id"], model_returned=r["model_returned"], fx="USD_JPY=160(project default, er009:20)")
    C.ledger_add(rec)
    txt = r["text"].strip()
    m = re.search(r"\{.*\}", txt, re.S)
    try:
        j = json.loads(m.group(0))
    except Exception:
        j = None
    return {"raw": txt, "json": j, "cost_jpy": rec["cost_jpy"]}


def main():
    rows = load_rows()
    spelled = {"toteme": "Toteme", "khaite": "Khaite", "altuzarra": "Altuzarra", "zabelina": "Zabelina", "canele": "Canelé", "meink": "Meink", "melos": "Melos"}
    out = {}
    for w in TARGETS:
        # 文脈=その語を含む最初のHR行のcanonical文
        ctx = next(sentence_with(r["canonical_text"], w) for r in rows if w in (r.get("pronunciation_lookups") or {}))
        e2 = e2_g2p(w)
        e3 = e3_llm(w, spelled[w], ctx)
        cands, bad = [], []
        if e3 and e3["json"]:
            for p in e3["json"].get("pronunciations", []):
                a = ipa_to_arpa(p.get("ipa", ""))
                (cands if a else bad).append({"ipa": p.get("ipa"), "respelling": p.get("respelling"), "arpa": strip_stress(a) if a else None})
        out[w] = {"sentence": ctx, "E1": "N/A(明示的境界なし)", "E2_g2p_en": list(e2), "E3_llm": e3, "E3_candidates": cands, "E3_ipa_unconvertible": bad}
        print(w, "E2", " ".join(e2), "| E3", [" ".join(c["arpa"]) for c in cands], "bad", [b["ipa"] for b in bad], flush=True)
    json.dump(out, open(f"{OUT}/est_e2_e3.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("ledger total jpy", C.ledger_total_jpy())


if __name__ == "__main__":
    main()

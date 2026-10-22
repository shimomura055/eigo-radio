# -*- coding: utf-8 -*-
"""第2巡 E3b: gpt-6-luna(web無し)のN-best(最大3)推定。S2R-04(b)。7語x1呼出(約0.3円)。再実行しない。
official自己申告は記録するが判定には一切使わない(S2R-08)。費用は r2/paid_calls.jsonl。"""
import json, os, re, sys, time
sys.path.insert(0, os.getcwd())
from pathlib import Path
import er100_pnps_stage2_trial_01_est as E1
from er100_pnps_stage2_trial_01_common import OUT, TARGETS
import er098_kp_six_model_trial_01_common as C
from er006_m1_multi_candidate_01 import ipa_to_arpa

R2 = Path(OUT) / "r2"
C.LEDGER = R2 / "paid_calls.jsonl"
C.OUT = R2
SYS = ("You are a phonetics assistant for an English-learning radio program. Given an English-language sentence and one term from it "
       "(a brand, person name, place or foreign loanword), list up to 3 DISTINCT plausible US-English pronunciations that a well-informed "
       "newsreader might use for that term in this sentence, most likely first. Give IPA (US) for each, with stress marks. "
       "Output JSON only: {\"pronunciations\":[{\"ipa\":\"...\",\"respelling\":\"...\"}],\"official\":true|false}")


def main():
    est = json.load(open(f"{OUT}/est_e2_e3.json", encoding="utf-8"))
    spelled = {"toteme": "Toteme", "khaite": "Khaite", "altuzarra": "Altuzarra", "zabelina": "Zabelina", "canele": "Canelé", "meink": "Meink", "melos": "Melos"}
    out = {}
    for w in TARGETS:
        user = f"Sentence: {est[w]['sentence']}\nTerm: {spelled[w]}"
        body = C.build_body("openai", E1.MODEL, user, system=SYS, extra={"max_output_tokens": 2000})
        r = C.call_with_retry("openai", E1.MODEL, body)
        rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "kind": "r2_e3b_nbest", "word": w, "model": E1.MODEL, "ok": r["ok"]}
        cands = []
        if r["ok"]:
            usd = C.cost_usd(E1.MODEL, r["usage"]); rec.update(usage=r["usage"], cost_jpy=round(usd * C.USD_JPY, 4), response_id=r["response_id"], model_returned=r["model_returned"], fx="USD_JPY=160(project default)")
            m = re.search(r"\{.*\}", r["text"], re.S)
            try:
                j = json.loads(m.group(0))
            except Exception:
                j = None
            for p in (j or {}).get("pronunciations", [])[:3]:
                a = ipa_to_arpa(p.get("ipa", ""))
                cands.append({"ipa": p.get("ipa"), "respelling": p.get("respelling"), "arpa": list(E1.strip_stress(a)) if a else None})
            out[w] = {"candidates": cands, "official_selfreport_IGNORED": (j or {}).get("official"), "raw": r["text"]}
        else:
            out[w] = {"candidates": [], "error": str(r.get("attempts"))}
        C.ledger_add(rec)
        print(w, [(c["ipa"], c["arpa"]) for c in cands], flush=True)
    json.dump(out, open(R2 / "est_nbest.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("ledger total jpy", C.ledger_total_jpy())


if __name__ == "__main__":
    main()

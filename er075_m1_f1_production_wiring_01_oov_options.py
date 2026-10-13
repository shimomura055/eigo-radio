# -*- coding: utf-8 -*-
"""ASR-PHONETIC-EQUIVALENCE-M1-F1-PRODUCTION-WIRING-01 委任_02: OOV(CMU未収録)語の扱い選択肢別 Melos said 12件 read-only 再判定。
入力=既存転写(er069 results_02.json)のみ。API 0 / JPY0 / telemetry no-op(er068 import 時に適用)。Production code 無変更。
 (0) legacy      : Production 現行(design_judge の EXACT/PROD_PASS_UNCHANGED)
 (i) no_oov      : OOV fallback 非移行(canonical が CMU 未収録なら M1 は適用しない=CMU 収録語のみ)
 (ii-a)ledger_high: Ledger の confidence=high かつ expected_pronunciation_ipa がある発音のみ音素基準
 (ii-b)ledger_any_primary: confidence 不問、Ledger の主発音(米国英語の先頭 IPA)のみ
 (ii-c)ledger_incl_alt  : Ledger の別読み(alternate)も含む(感度分析。信頼度 low の別読みを使うため推奨外)
 (iii) trial_oov_fallback: Trial 現行(OOV の canonical を語幹綴りから推定)=新基準の承認申請が必要な案
"""
import argparse, json, os, re, sys
sys.path.insert(0, os.getcwd())
import er068_asr_phonetic_equivalence_generalization_01_offline as O

LEDGER = "er006_output/pronunciation_ledger_01/ledger.json"
IPA = [("tʃ", "CH"), ("dʒ", "JH"), ("aɪ", "AY"), ("aʊ", "AW"), ("eɪ", "EY"), ("oʊ", "OW"), ("əʊ", "OW"), ("ɔɪ", "OY"),
       ("iː", "IY"), ("uː", "UW"), ("ɑː", "AA"), ("ɔː", "AO"), ("ɜː", "ER"), ("ɒ", "AA"), ("ɛ", "EH"), ("æ", "AE"), ("ɪ", "IH"),
       ("ʊ", "UH"), ("ʌ", "AH"), ("ə", "AH"), ("ɔ", "AO"), ("ɑ", "AA"), ("i", "IY"), ("u", "UW"), ("θ", "TH"), ("ð", "DH"),
       ("ʃ", "SH"), ("ʒ", "ZH"), ("ŋ", "NG"), ("j", "Y"), ("r", "R"), ("ɹ", "R"), ("l", "L"), ("m", "M"), ("n", "N"), ("p", "P"),
       ("b", "B"), ("t", "T"), ("d", "D"), ("k", "K"), ("g", "G"), ("f", "F"), ("v", "V"), ("s", "S"), ("z", "Z"), ("h", "HH"), ("w", "W")]


def ipa_to_arpa(ipa: str):
    s = re.sub(r"[ˈˌ.\s/]", "", ipa)
    out = []
    i = 0
    while i < len(s):
        for k, v in IPA:
            if s.startswith(k, i):
                out.append(v); i += len(k); break
        else:
            return None  # 未知の記号は変換不能=発音確証なし
    return tuple(out)


def ledger_prons(word: str, mode: str):
    d = json.load(open(LEDGER, encoding="utf-8"))
    prons = []
    for v in d.values():
        if v.get("surface", "").lower() != word.lower():
            continue
        ipa = v.get("expected_pronunciation_ipa") or ""
        conf = v.get("confidence", "")
        if not ipa:
            continue
        if mode == "high" and conf != "high":
            continue
        cands = [x for x in re.findall(r"/[^/]+/", ipa)]
        if mode in ("any_primary", "high"):
            cands = cands[:1]  # 先頭=米国英語の暫定候補
        if mode == "incl_alt":
            for a in v.get("alternate_pronunciations") or []:
                cands += re.findall(r"/[^/]+/", a)
        for c in cands:
            p = ipa_to_arpa(c)
            if p:
                prons.append(p)
    return prons


def make_phoneme_ok(mode):
    orig = O.phoneme_ok

    def f(c, cand, entity_like):
        forms = O.derived_phone_forms(c, entity_like)
        if forms:
            return orig(c, cand, entity_like)
        if mode == "no_oov":
            return False, "oov_not_migrated", None
        if mode == "trial":
            return orig(c, cand, entity_like)
        lm = {"ledger_high": "high", "ledger_any_primary": "any_primary", "ledger_incl_alt": "incl_alt"}[mode]
        lf = {}
        for p in ledger_prons(c, lm):
            lf.setdefault(p, "exact")
            if p and p[-1] in ("S", "Z"):
                lf.setdefault(p[:-1], "drop_final_S_or_Z")
        if not lf:
            return False, "oov_no_ledger_pron", None
        for v in O.phone_variants(cand, entity_like):
            if v in lf:
                return True, "ledger_phoneme", lf[v]
        return False, "ledger_phoneme", None
    return f


MODES = ["legacy", "no_oov", "ledger_high", "ledger_any_primary", "ledger_incl_alt", "trial"]
ORIG = O.phoneme_ok


def judge(mode, canon, asr):
    O.phoneme_ok = ORIG if mode in ("legacy", "trial") else make_phoneme_ok(mode)
    d = O.design_judge(canon, asr)
    if mode == "legacy":
        return d["verdict"] in ("EXACT", "PROD_PASS_UNCHANGED"), d
    return d["verdict"] in ("EXACT", "PROD_PASS_UNCHANGED", "ACCEPT_M1"), d


PROBES = [  # 汎化・安全側反例(canonical, asr, 期待=許容してはならない/してよい)
    ("Melos said.", "Melos said.", "same"), ("Melos said.", "Melos sad.", "must_not"), ("Melos said.", "Mellon said.", "must_not"),
    ("Melos said.", "Melas said.", "must_not"), ("Melos said.", "Milo said.", "must_not"), ("Melos said.", "Mellow said.", "oov_case"),
    ("Polos said.", "Polo said.", "pattern_a"), ("Polos said.", "Pollo said.", "oov_case"), ("Halos said.", "Halo said.", "pattern_a"),
    ("Kratos said.", "Krato said.", "oov_case"), ("Kratos said.", "Crato said.", "oov_case"), ("Pandoros said.", "Pandoro said.", "oov_case"),
    ("Cleos said.", "Clio said.", "oov_case"), ("Sirius said.", "Serious said.", "must_not_entity"), ("Thebes said.", "Thebe said.", "pattern_a"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-telemetry", action="store_true", required=True)
    a = ap.parse_args()
    rows = json.load(open(os.path.join(a.split_dir, "results_02.json"), encoding="utf-8"))["rows"]
    rows = [r for r in rows if r["name"] == "Melos" and r["verb"] == "said"]
    rows.sort(key=lambda r: (["std", "adv"].index(r["level"]), r["target"] != "raw", r["take"]))
    out, S = [], {m: {"openai": 0, "azure": 0, "or": 0} for m in MODES}
    for r in rows:
        e = {"job": r["job"], "level": r["level"], "target": r["target"], "take": r["take"], "canonical": r["text"]}
        for m in MODES:
            res = {}
            for eng in ("openai", "azure"):
                ok, d = judge(m, r["text"], r[eng]["text"])
                res[eng] = {"asr": r[eng]["text"], "pass": ok, "verdict": d["verdict"],
                            "audit": [(s["from"], s["to"], s.get("basis"), s.get("phoneme_rule")) for s in (d.get("m1") or {}).get("subs", [])]}
                S[m][eng] += ok
            res["or"] = res["openai"]["pass"] or res["azure"]["pass"]
            S[m]["or"] += res["or"]
            e[m] = res
        out.append(e)
    probes = []
    for c, asr, kind in PROBES:
        p = {"canonical": c, "asr": asr, "kind": kind, "oov_canonical_words": [w for w in O.P.tokens(c) if not O._cmu_variants(w)]}
        for m in MODES:
            p[m] = judge(m, c, asr)[0]
        probes.append(p)
    O.phoneme_ok = ORIG
    led = {m: [list(p) for p in ledger_prons("melos", k)] for m, k in (("high", "high"), ("any_primary", "any_primary"), ("incl_alt", "incl_alt"))}
    json.dump({"summary": S, "ledger_melos_arpabet": led, "melos_cmu": O._cmu_variants("melos"), "mello_cmu": O._cmu_variants("mello"),
               "mellow_cmu": O._cmu_variants("mellow"), "melo_cmu": O._cmu_variants("melo"), "rows": out, "probes": probes, "api_calls": 0},
              open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print(json.dumps(S, ensure_ascii=False)); print(json.dumps(led)); print("cmu melos/mello/mellow/melo", O._cmu_variants("melos"), O._cmu_variants("mello"), O._cmu_variants("mellow"), O._cmu_variants("melo"))
    for p in probes:
        print(p["canonical"], "|", p["asr"], p["kind"], p["oov_canonical_words"], {m: p[m] for m in MODES})


if __name__ == "__main__":
    main()

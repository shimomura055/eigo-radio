# -*- coding: utf-8 -*-
"""R0抽出器(0円・HTTP GETのみ): ページ本文から対象語の近傍にある(1)IPA (2)ハイフン区切りの英語綴り読み(respelling) (3)引用符つき単語読み を機械抽出し、
決定論変換器でARPAbet化する。出典URL・引用(本文抜粋)・取得日時を保存。識別(identity)判定はこのscriptではしない(人手の根拠付き注記=identity_notes)。"""
import json, os, re, sys, time, hashlib
sys.path.insert(0, os.getcwd())
from er100_pnps_stage2_trial_01_common import *
import er097_pronunciation_supply_stage1_01 as S1
from er006_m1_multi_candidate_01 import ipa_to_arpa, default_cmu

# 綴り読み(respelling)音節 -> ARPAbet。未知の綴りがあれば None(近似しない)。
VOW = [("eye", "AY"), ("air", "EH R"), ("ahr", "AA R"), ("ar", "AA R"), ("ah", "AA"), ("aw", "AO"), ("ay", "EY"), ("eh", "EH"), ("ee", "IY"),
       ("ih", "IH"), ("oh", "OW"), ("oo", "UW"), ("ow", "AW"), ("uh", "AH"), ("ur", "ER"), ("ai", "EY"), ("ie", "AY"), ("ey", "EY"), ("a", "AE"), ("e", "EH"),
       ("i", "IH"), ("o", "AA"), ("u", "AH")]
CON = [("ng", "NG"), ("nk", "NG K"), ("sh", "SH"), ("ch", "CH"), ("th", "TH"), ("zh", "ZH"), ("kw", "K W"), ("b", "B"), ("d", "D"), ("f", "F"), ("g", "G"), ("h", "HH"),
       ("j", "JH"), ("k", "K"), ("l", "L"), ("m", "M"), ("n", "N"), ("p", "P"), ("r", "R"), ("s", "S"), ("t", "T"), ("v", "V"), ("w", "W"), ("y", "Y"), ("z", "Z")]


def respell_to_arpa(s):
    out = []
    for syl in re.split(r"[-\s]+", s.strip().lower()):
        i = 0
        if not syl:
            continue
        while i < len(syl):
            for k, v in VOW + CON:
                if syl.startswith(k, i):
                    out.extend(v.split()); i += len(k); break
            else:
                return None
    return tuple(out) or None


IPA_BLOCK = re.compile(r"/\s*([^/]{2,40}?)\s*/")
RESPELL = re.compile(r"(?<![A-Za-z])((?:[A-Za-z]{1,6}-){1,4}[A-Za-z]{1,6})(?![A-Za-z-])")
QWORD = re.compile(r"(?:pronounc\w*|simple|say|said|as so)\W{0,12}[\"“]([a-z]{3,8})[.\"”,]", re.I)
MARK = re.compile(r"(right way|pronounce[sd]?|as so|say it|said|pronunciation)\W{0,8}$", re.I)
WRONG = re.compile(r"wrong\W{0,10}way\W{0,3}$|incorrect", re.I)


def extract(word, text, spelled):
    out = []
    for m in re.finditer(re.escape(spelled), text, re.I):
        win = text[m.end(): m.end() + 320]
        pre = text[max(0, m.start() - 20): m.start()]
        ctx = (pre + text[m.start():m.end() + 160])[:200]
        for ib in IPA_BLOCK.finditer(win[:90]):
            body = re.sub(r"\s+", "", ib.group(1))
            if re.search(r"[a-zˈˌːɑɒæɛəɜɪʊʌɔθðʃʒŋɹɡ]", body) and len(body) <= 24:
                out.append({"type": "ipa", "raw": ib.group(0)[:60], "arpa": ipa_to_arpa(body), "context": ctx})
        for rm in RESPELL.finditer(win):
            r = rm.group(1)
            before = win[:rm.start()]
            near = before[-24:]
            immediate = re.fullmatch(r"[\s–—:\-(\"“‘']{0,6}", before[-6:] if len(before) <= 6 else before[-6:]) is not None and len(before) <= 8
            marked = bool(MARK.search(before.rstrip("\"“‘' ")[-30:] + " ")) or bool(MARK.search(before[-30:]))
            if WRONG.search(before[-24:]) or r.lower().replace("-", "") == word:
                continue
            if immediate or marked:
                out.append({"type": "respelling", "raw": r, "arpa": respell_to_arpa(r), "context": ctx, "position_rule": "immediate" if immediate else "marker"})
                break
        qm = QWORD.search(win[:130])
        if qm:
            cm = default_cmu(qm.group(1))
            out.append({"type": "quoted_word", "raw": qm.group(1), "arpa": cm[0] if cm else None, "arpa_all": [list(c) for c in cm], "context": ctx})
        mm = re.search(r"\(\s*/[^/]{1,30}/\s+([A-Z]{3,8})\s*\)", win[:70])
        if mm:
            out.append({"type": "caps_respelling", "raw": mm.group(1), "arpa": respell_to_arpa(mm.group(1).lower()), "context": ctx})
    return out


TARGET_URLS = {
    "altuzarra": ["https://www.businessinsider.com/correct-way-pronounce-fashion-brand-designer-names-2019-1", "https://www.nylon.com/fashion/fashion-designer-pronunciation-guide",
                  "https://www.elle.com.au/fashion/fashion-news/the-fashion-dictionary-77-brands-and-names-and-how-to-pronounce-them-12372/",
                  "https://www.herworld.com/style/fashion/busy-girls-guide-pronouncing-designer-name-labels", "https://www.bustle.com/articles/61905-how-to-correctly-pronounce-designer-names-so-you-wont-get-the-stank-eye-talking-about-fashion"],
    "khaite": ["https://www.nylon.com/fashion/fashion-designer-pronunciation-guide", "https://itscosmicclementine.substack.com/p/behind-the-brand-khaite",
               "https://www.farfetch.com/style-guide/brands/khaite-brand-everything-you-need-to-know", "https://www.elle.com.au/fashion/fashion-news/the-fashion-dictionary-77-brands-and-names-and-how-to-pronounce-them-12372/"],
    "toteme": ["https://www.nylon.com/fashion/fashion-designer-pronunciation-guide", "https://www.elle.com.au/fashion/fashion-news/the-fashion-dictionary-77-brands-and-names-and-how-to-pronounce-them-12372/",
               "https://www.vogue.co.uk/article/toteme-interview", "https://www.highsnobiety.com/p/toteme-menswear-interview/", "https://www.culturedmag.com/article/2026/01/22/fashion-toteme-swedish-style-interview/",
               "https://coveti.com/who-is-toteme/", "https://ashleykane.com/an-ode-to-toteme/"],
    "meink": ["https://en.wikipedia.org/wiki/Troy_Meink", "https://www.airandspaceforces.com/article/meet-troy-meink/", "https://www.airandspaceforces.com/article/meink-reflects-on-first-year-as-secaf/"],
    "canele": ["https://youpronounce.it/french-food/canele/", "https://en.wikipedia.org/wiki/Canel%C3%A9", "https://pronouncebee.com/canele/", "https://www.webstaurantstore.com/blog/3972/french-pastries.html"],
    "zabelina": ["https://english.nv.ua/nation/nv-observer-notes-zelenskyy-s-tense-mood-50635363.html", "https://istoriya-familii.com/zabela-zabelina/"],
    "melos": ["https://dictionary.cambridge.org/pronunciation/english/melos", "https://en.wikipedia.org/wiki/Run%2C_Melos%21", "https://en.wikipedia.org/wiki/Milos", "https://www.dictionary.com/browse/melos"],
}
SPELLED = {"toteme": "Toteme", "khaite": "Khaite", "altuzarra": "Altuzarra", "zabelina": "Zabelina", "canele": "Canel", "meink": "Meink", "melos": "Melos"}
if __name__ == "__main__":
    res = {}
    for w, urls in TARGET_URLS.items():
        res[w] = []
        for u in urls:
            try:
                raw = S1.default_fetch(u, timeout=8, max_bytes=900_000)
            except Exception as ex:
                raw = None
            time.sleep(0.3)
            if not raw:
                res[w].append({"url": u, "fetched": False}); continue
            text = S1.html_to_text(raw)
            ex = extract(w, text, SPELLED[w])
            seen = set(); ex2 = []
            for e in ex:
                k = (e["type"], e["raw"])
                if k not in seen:
                    seen.add(k); ex2.append(e)
            res[w].append({"url": u, "fetched": True, "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(), "text_len": len(text), "extractions": ex2[:8]})
            print(w, u[:70], [(e["type"], e["raw"], e["arpa"] and " ".join(e["arpa"])) for e in ex2[:4]], flush=True)
    json.dump(res, open(f"{OUT}/r0_extractions.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# -*- coding: utf-8 -*-
"""ASR-M1-OOV-MULTI-PRONUNCIATION-PRODUCTION-01 委任_01: M1 OOV 複数発音候補方式の設計+offline評価。
DEV/Trial 専用。Production py は import して呼ぶだけ(無変更)。API 0 / JPY0。Ledger は読取のみ。
設計(DESIGN_01.md): 候補集合は canonical 語のみから事前固定(ASR 非依存)。
  C1 = CMU 全異読(辞書収録語)  C2 = Pronunciation Ledger の全発音(confidence 不問・CMU 未収録語のみ・英語 IPA のみ)
  C3(綴りからの規則 G2P)は採用しない。候補上限 CAP(=6)。1 候補でも既存 M1(音素正規化→Pattern A/B/C→F1 全差分点検)が成立すれば受理。
"""
from __future__ import annotations

import argparse
import collections
import contextlib
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.getcwd())
import er068_asr_phonetic_equivalence_generalization_01_offline as O  # noqa: E402  (telemetry no-op 化を含む)
import er065_short_clip_asr_context_trial_01_p2_phon as P  # noqa: E402

LEDGER_PATH = "er006_output/pronunciation_ledger_01/ledger.json"
CAP = 6
ACCEPT_REASON = "M1_MULTI_CANDIDATE_ACCEPT"

# ---------------------------------------------------------------------------
# IPA -> ARPAbet 決定論変換表(新設。長い記号を先に照合)。変換不能な記号を含む発音は『候補不成立』として記録する。
# ---------------------------------------------------------------------------
IPA_TABLE = [
    ("tʃ", "CH"), ("t͡ʃ", "CH"), ("ʧ", "CH"), ("dʒ", "JH"), ("d͡ʒ", "JH"), ("ʤ", "JH"), ("t͡s", "T S"), ("ts", "T S"),
    ("aɪ", "AY"), ("aʊ", "AW"), ("eɪ", "EY"), ("oʊ", "OW"), ("əʊ", "OW"), ("ɔɪ", "OY"),
    ("ɜːr", "ER"), ("ɜr", "ER"), ("ɜː", "ER"), ("ɝ", "ER"), ("ɚ", "ER"), ("ər", "ER"),
    ("iː", "IY"), ("uː", "UW"), ("ɑː", "AA"), ("ɔː", "AO"), ("ɒ", "AA"), ("ɛ", "EH"), ("æ", "AE"), ("ɪ", "IH"), ("ʊ", "UH"),
    ("ʌ", "AH"), ("ə", "AH"), ("ɔ", "AO"), ("ɑ", "AA"), ("i", "IY"), ("u", "UW"),
    ("θ", "TH"), ("ð", "DH"), ("ʃ", "SH"), ("ʒ", "ZH"), ("ŋ", "NG"), ("j", "Y"), ("ɹ", "R"), ("r", "R"), ("l", "L"), ("m", "M"),
    ("n", "N"), ("p", "P"), ("b", "B"), ("t", "T"), ("d", "D"), ("k", "K"), ("ɡ", "G"), ("g", "G"), ("f", "F"), ("v", "V"),
    ("s", "S"), ("z", "Z"), ("h", "HH"), ("w", "W"),
]
_IPA_STRIP = re.compile(r"[ˈˌ.\s/\[\]²]")
_IPA_CHARS = re.compile(r"[ˈˌːɑɒæɛəɜɪʊʌɔθðʃʒŋɹɡɝɚ͡]")


def ipa_to_arpa(ipa: str):
    """決定論的 IPA→ARPAbet(ストレス除去)。未知記号があれば None(=候補不成立)。"""
    s = _IPA_STRIP.sub("", ipa or "")
    out, i = [], 0
    while i < len(s):
        for k, v in IPA_TABLE:
            if s.startswith(k, i):
                out.extend(v.split()); i += len(k); break
        else:
            return None
    return tuple(out) if out else None


def _segments(raw: str):
    """Ledger 文字列から IPA らしき断片を (断片, 除外理由|None) で返す。
    スラッシュ区切り断片を優先し、無ければ IPA 固有文字を含む全体のみ採る(英単語の綴りや『oh-TOH-nee』型の
    綴り読みは IPA ではないので候補にしない=G2P を新設しない)。『native』『Swedish』等の非英語ラベル直後の断片は除外。"""
    raw = raw or ""
    segs = []
    for m in re.finditer(r"/([^/]+)/", raw):
        ctx = raw[max(0, m.start() - 24):m.start()]
        excl = "non_english_label" if re.search(r"native|Swedish|Italian|French|German|Spanish|Japanese|Chinese|Korean|Russian|Greek", ctx, re.I) else None
        segs.append((m.group(1), excl))
    if not segs:
        m = re.search(r"\[([^\]]+)\]", raw)
        body = m.group(1) if m else raw.split("（")[0].split("(")[0]
        if _IPA_CHARS.search(body):
            segs.append((body.strip(), None))
    return segs


def load_ledger(path: str = LEDGER_PATH) -> dict:
    return json.load(open(path, encoding="utf-8"))


def _cmu(word: str):
    return O._cmu_variants(word)


def candidates_for(word: str, ledger: dict | None, cap: int = CAP, c1_primary_only: bool = False) -> dict:
    """語 word(canonical 側)の発音候補集合。入力は word と Ledger/CMU のみ=ASR 非依存(事前固定)。
    順序: C1(CMU 全異読)→C2(Ledger expected 断片→alternate 断片)。同一音素列は統合(出典は also_from に併記)。
    C2 は CMU 未収録語にのみ適用(CMU 収録語は信頼できる辞書発音を使い、Ledger の誤エントリ[例: surface 'us' の IPA が 'unknown']の影響を避ける)。"""
    w = word.lower().strip("'")
    cands, seen = [], {}
    unconv, excluded = [], []

    def add(pron, src, conf, key, raw):
        if pron in seen:
            seen[pron]["also_from"].append(src)
            return
        c = {"pron": list(pron), "source": src, "confidence": conf, "ledger_key": key, "ipa_raw": raw, "also_from": []}
        seen[pron] = c
        cands.append(c)

    vs = _cmu(w)
    for v in (vs[:1] if c1_primary_only else vs):
        add(v, "C1_cmu_variant", "dictionary", None, None)
    if not vs and ledger:
        for key, e in ledger.items():
            if e.get("surface", "").lower().strip() != w or " " in e.get("surface", "").strip():
                continue
            if e.get("entity_type") == "ja_reading_katakana":
                continue
            conf = e.get("confidence", "")
            for src, raw in [("C2_ledger_expected", e.get("expected_pronunciation_ipa") or "")] + \
                            [("C2_ledger_alt", a) for a in (e.get("alternate_pronunciations") or [])]:
                for seg, why in _segments(raw):
                    if why:
                        excluded.append({"ipa": seg, "reason": why, "ledger_key": key}); continue
                    p = ipa_to_arpa(seg)
                    if p is None:
                        unconv.append({"ipa": seg, "ledger_key": key, "reason": "unconvertible_symbol"}); continue
                    add(p, src, conf, key, seg)
    overflow = max(0, len(cands) - cap)
    return {"word": w, "candidates": cands[:cap], "overflow_dropped": overflow, "unconvertible": unconv, "excluded": excluded,
            "n_before_cap": len(cands)}


def cset_hash(cs: dict) -> str:
    return hashlib.sha1(json.dumps([cs["word"], cs["candidates"]], ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:12]


def fix_candidates(canonical: str, ledger, c1_primary_only=False) -> dict:
    """canonical 文の全トークンの候補集合を ASR を見る前に確定し、ログ化可能な dict で返す(candidates_fixed_before_asr)。"""
    return {t: candidates_for(t, ledger, c1_primary_only=c1_primary_only) for t in dict.fromkeys(P.tokens(canonical))}


def forms_from(c: str, cands: list) -> dict:
    """候補ごとに Pattern(厳密/A/B/C)が受理側として期待する音素列を導く。{音素列: [(rule, cand_index)]}"""
    out = collections.defaultdict(list)
    cl = c.lower().strip("'")
    for i, cd in enumerate(cands):
        v = tuple(cd["pron"])
        out[v].append(("exact", i))
        if v and v[-1] in O._SIB:
            out[v[:-1]].append(("drop_final_S_or_Z", i))
        if cl.endswith("ed"):
            if v and v[-1] in ("T", "D"):
                out[v[:-1]].append(("drop_ed", i))
            if len(v) >= 2 and v[-2:] == ("IH", "D"):
                out[v[:-2]].append(("drop_ed", i))
        out[v + ("S",)].append(("add_s", i)); out[v + ("Z",)].append(("add_s", i)); out[v + ("IH", "Z")].append(("add_s", i))
    return out


class Ctx:
    ledger = None
    c1_primary_only_for_entity = True  # 既存 M1(F2 保守基準)を維持: 固有名詞らしき語の CMU は代表発音のみ
    match_log: list = []


def multi_phoneme_ok(c: str, cand: str, entity_like: bool):
    """O.phoneme_ok の置換版(canonical 語 c の発音候補を複数にし、ASR 側同音綴り cand が 1 候補でも一致すれば受理)。"""
    cs = candidates_for(c, Ctx.ledger, c1_primary_only=(entity_like and Ctx.c1_primary_only_for_entity))
    if not cs["candidates"]:
        return False, "oov_no_candidates", None
    forms = forms_from(c, cs["candidates"])
    for v in O.phone_variants(cand, entity_like):
        if v in forms:
            hits = [(rule, cs["candidates"][i]) for rule, i in forms[v]]
            rule, cd = hits[0]
            Ctx.match_log.append({"canonical_word": c, "asr_homophone": cand, "all_hits": [(r, h["source"], tuple(h["pron"])) for r, h in hits]})
            basis = f"multi_candidate|{cd['source']}|conf={cd['confidence']}|pron={' '.join(cd['pron'])}|ledger_key={cd['ledger_key']}"
            return True, basis, rule
    return False, "multi_candidate_no_match", None


@contextlib.contextmanager
def multi_mode(ledger, c1_primary_only_for_entity=True):
    orig = O.phoneme_ok
    Ctx.ledger, Ctx.c1_primary_only_for_entity, Ctx.match_log = ledger, c1_primary_only_for_entity, []
    O.phoneme_ok = multi_phoneme_ok
    try:
        yield
    finally:
        O.phoneme_ok = orig


def judge_multi(canonical: str, asr: str, ledger, c1_primary_only_for_entity=True) -> dict:
    """候補を ASR 閲覧前に確定→判定→候補集合が不変であることを確認して結果を返す。"""
    fixed = fix_candidates(canonical, ledger, c1_primary_only=False)
    h0 = {t: cset_hash(c) for t, c in fixed.items()}
    with multi_mode(ledger, c1_primary_only_for_entity):
        d = O.design_judge(canonical, asr)
    h1 = {t: cset_hash(c) for t, c in fix_candidates(canonical, ledger).items()}
    return {"design": d, "candidates_fixed_before_asr": h0 == h1, "cand_hashes": h0,
            "pass": d["verdict"] in ("EXACT", "PROD_PASS_UNCHANGED", "ACCEPT_M1"),
            "new_m1": d["verdict"] == "ACCEPT_M1"}


def subs_of(res: dict):
    return [(s["from"], s["to"], s.get("canonical_word"), s.get("basis"), s.get("phoneme_rule")) for s in ((res["design"].get("m1") or {}).get("subs", []))]


def matched_pairs(res: dict, ledger, engine_asr_token_phones=None) -> set:
    """Secondary 同意判定用: M1 が置換した (canonical_word, 候補音素列) の集合(全一致候補)。"""
    out = set()
    for s in ((res["design"].get("m1") or {}).get("subs", [])):
        cw, to = s.get("canonical_word"), s.get("to")
        cs = candidates_for(cw, ledger)
        forms = forms_from(cw, cs["candidates"])
        for v in O.phone_variants(to, False):
            for rule, i in forms.get(v, []):
                out.add((cw, tuple(cs["candidates"][i]["pron"])))
    return out


def secondary_agree(res_a: dict, res_b: dict, ledger) -> bool:
    """fallback/forced-secondary 同意: 両エンジンが M1 で受理され、同一 canonical 語について共通の候補音素列で成立すること。"""
    if not (res_a["new_m1"] and res_b["new_m1"]):
        return False
    return bool(matched_pairs(res_a, ledger) & matched_pairs(res_b, ledger))


# ---------------------------------------------------------------------------
# 評価
# ---------------------------------------------------------------------------
def legacy_pass(canonical, asr, f1=True):
    import er011_b1_connected_speech_validator_01 as csv3
    import er006_preprod_hardening_01_validation as val
    cur = csv3.classify_connected_speech
    old = getattr(csv3, "_classify_first_diff", None)
    try:
        if not f1 and old is not None:
            csv3.classify_connected_speech = old
        pj = O.prod_judge(canonical, asr)
    finally:
        csv3.classify_connected_speech = cur
    return pj["pass"]


def melos12(ledger):
    rows = json.load(open("er069_output/attribution_clip_split_trial_01/results_02.json", encoding="utf-8"))["rows"]
    rows = [r for r in rows if r["name"] == "Melos" and r["verb"] == "said"]
    rows.sort(key=lambda r: (["std", "adv"].index(r["level"]), r["target"] != "raw", r["take"]))
    out = []
    for r in rows:
        c = r["text"]
        e = {"job": r["job"], "level": r["level"], "target": r["target"], "take": r["take"], "canonical": c,
             "candidates": fix_candidates(c, ledger)}
        res = {}
        for eng in ("openai", "azure"):
            a = r[eng]["text"]
            rm = judge_multi(c, a, ledger)
            res[eng] = rm
            e[eng] = {"asr": a, "before": legacy_pass(c, a, f1=False), "f1_only": legacy_pass(c, a, f1=True), "multi": rm["pass"],
                      "verdict": rm["design"]["verdict"], "subs": subs_of(rm), "fixed_before_asr": rm["candidates_fixed_before_asr"],
                      "prod_classification": rm["design"].get("prod_classification"), "phon_verdict": rm["design"].get("phon_verdict")}
        e["before_or"] = e["openai"]["before"] or e["azure"]["before"]
        e["f1_or"] = e["openai"]["f1_only"] or e["azure"]["f1_only"]
        e["multi_or"] = e["openai"]["multi"] or e["azure"]["multi"]
        e["multi_secondary_same_candidate"] = (e["openai"]["multi"] and e["azure"]["multi"] and
                                               (e["openai"]["verdict"] in ("EXACT", "PROD_PASS_UNCHANGED") or e["azure"]["verdict"] in ("EXACT", "PROD_PASS_UNCHANGED") or
                                                secondary_agree(res["openai"], res["azure"], ledger)))
        out.append(e)
    return out


SYNTH = [  # (類型, canonical, asr, 期待, 備考, fake_ledger_entries|None)
    ("T1 複数候補のうち1つ一致(Ledger別読み)", "Melos said.", "Mello said.", "PASS", "別読み /ˈmɛloʊs/ が一致(Ledger 低信頼・自動生成)", None),
    ("T1 複数候補のうち1つ一致(Ledger別読み)", "Melos said.", "Mellow said.", "PASS", "同上", None),
    ("T1 複数候補のうち1つ一致(主発音)", "Melos said.", "Melos said.", "PASS", "綴り一致(EXACT)", None),
    ("T1 複数候補のうち1つ一致(CMU異読)", "The tomatoes were red.", "The tomatoes were red.", "PASS", "EXACT", None),
    ("T1b 一般化(fake Ledger・別語)", "Cleos said.", "Clio said.", "PASS", "fake Ledger /ˈkliːoʊs/(K L IY OW S)なら Clio(K L IY OW)と音素一致→受理。Ledger に根拠がある場合のみ",
     {"surface": "cleos", "entity_type": "cascade_unresolved_entity", "confidence": "low", "expected_pronunciation_ipa": "/ˈkliːoʊs/", "alternate_pronunciations": []}),
    ("T1c 一般化の限界(fake Ledger・語幹がCMU未収録)", "Zabelinas said.", "Zabellina said.", "NONPASS", "ASR 側が CMU 未収録語→音素を持たず不成立(誤PASSではなく取りこぼし側)",
     {"surface": "zabelinas", "entity_type": "cascade_unresolved_entity", "confidence": "low", "expected_pronunciation_ipa": "/zəˈbɛlɪnəz/", "alternate_pronunciations": []}),
    ("T2 どの候補も不一致", "Melos said.", "Milo said.", "NONPASS", "Milo=M IY L OW は候補に無い", None),
    ("T2 どの候補も不一致", "Melos said.", "Mellon said.", "NONPASS", "", None),
    ("T2 どの候補も不一致", "Melos said.", "Melas said.", "NONPASS", "Melas は CMU 未収録", None),
    ("T3 綴り近いが発音異なる(候補なし)", "Cleos said.", "Clio said.", "NONPASS", "Cleos は Ledger 無し→候補0→C3 不採用で非PASS(Trial fallback なら PASS だった)", None),
    ("T3 綴り近いが発音異なる(fake Ledger)", "Cleos said.", "Clio said.", "NONPASS", "fake Ledger /ˈkliːəs/(K L IY AH S): Clio=K L IY OW と不一致",
     {"surface": "cleos", "entity_type": "cascade_unresolved_entity", "confidence": "low", "expected_pronunciation_ipa": "/ˈkliːəs/", "alternate_pronunciations": []}),
    ("T3 綴り近いが発音異なる(既存Pattern A・M1非関与)", "Brontes said.", "Bronte said.", "PASS", "既存 Production Pattern A(綴り基準、OPEN-330)が PROD_PASS_UNCHANGED で受理。M1/本設計とは無関係の既存挙動(参考)",
     {"surface": "brontes", "entity_type": "cascade_unresolved_entity", "confidence": "low", "expected_pronunciation_ipa": "/ˈbrɒntiːz/", "alternate_pronunciations": []}),
    ("T4 ASRが別の実在語へ誤転写", "Melos said.", "Mellow said.", "PASS(論点)", "実在語 mellow へ誤転写でも、候補 /ˈmɛloʊs/ と音素一致なら受理される。真の発音は ASR だけでは判別不能=Ledger 候補の質に依存(要論点)", None),
    ("T4 ASRが別の実在語へ誤転写", "Melos said.", "Sad.", "NONPASS", "", None),
    ("T5 連結発音 vs 語句欠落", "The studies suggest cats today.", "The study suggests cats today.", "PASS", "正常な連結発音(F1維持)", None),
    ("T5 連結発音 vs 語句欠落", "He planned a US sea blockade.", "He planned a U S blockade.", "NONPASS", "sea 欠落(F1是正の維持)", None),
    ("T5 連結発音 vs 語句欠落", "Melos said he left.", "Mello said.", "NONPASS", "Melos 以外の語句欠落", None),
    ("T6 後半に別差分", "Melos said cats sleep.", "Mello said dogs sleep.", "NONPASS", "M1成立でも dogs/cats でF1非PASS", None),
    ("T6 後半に別差分", "Melos said he did not go.", "Mello said he did go.", "NONPASS", "否定不一致", None),
    ("T6 後半に別差分", "Melos said 5 cats sleep.", "Mello said 6 cats sleep.", "NONPASS", "数値不一致", None),
    ("T6 後半に別差分", "Melos said cats slept.", "Mello said cats sleep.", "NONPASS", "時制不一致", None),
    ("T7 M1成立+後半同一", "Melos said cats sleep.", "Mello said cats sleep.", "PASS", "M1成立+残差0", None),
    ("T8 同一語が文中に2回", "Melos said Melos left.", "Mello said Mellow left.", "PASS", "両出現とも候補一致", None),
    ("T8 2回のうち片方が別語", "Melos said Melos left.", "Mello said Milo left.", "NONPASS", "片方不一致", None),
]


def synth_eval(ledger):
    out = []
    for kind, c, a, exp, note, fake in SYNTH:
        led = dict(ledger)
        if fake:
            led["_fake_" + fake["surface"]] = fake
        r = judge_multi(c, a, led)
        got = "PASS" if r["pass"] else "NONPASS"
        # 受理理由の抽出
        out.append({"kind": kind, "canonical": c, "asr": a, "expected": exp, "got": got, "verdict": r["design"]["verdict"],
                    "prod_classification": r["design"].get("prod_classification"), "subs": subs_of(r), "note": note,
                    "match": (exp.startswith(got) or (exp.startswith("PASS") and got == "PASS")),
                    "fixed_before_asr": r["candidates_fixed_before_asr"], "fake_ledger": bool(fake)})
    return out


def pairs_eval(ledger):
    import er075_m1_f1_production_wiring_01_census as C
    pairs, meta = C.load_pairs()
    new_rows, cnt, errs = [], collections.Counter(), 0
    for (c, a), src in pairs.items():
        try:
            lp = legacy_pass(c, a, f1=True)
            r = judge_multi(c, a, ledger)
            r_all = judge_multi(c, a, ledger, c1_primary_only_for_entity=False)
        except Exception:
            errs += 1; continue
        cnt[f"legacy_pass={lp}|multi_pass={r['pass']}"] += 1
        if lp and not r["pass"]:
            cnt["REGRESSION_pass_to_nonpass"] += 1
        if r["pass"] and not lp and not r["new_m1"]:
            cnt["harness_EXACT_artifact_not_m1"] += 1  # design_judge の EXACT はトークン等価ショートカット($/%が落ちる)。M1 ではなく Production も非PASS
        if r["new_m1"] and not lp:
            cnt["new_m1_accept"] += 1
            new_rows.append({"src": src, "canonical": c, "asr": a, "subs": subs_of(r)})
        if r_all["new_m1"] and not lp and not r["new_m1"]:
            cnt["c1_all_variants_sensitivity_extra_pass"] += 1
            new_rows.append({"src": src, "canonical": c, "asr": a, "subs": subs_of(r_all), "only_with_c1_all_variants_for_entity": True})
    return {"n_pairs": len(pairs), "counts": dict(cnt), "errors": errs, "new_pass": new_rows, "load_meta": meta}


def counter_eval(ledger):
    import er075_m1_f1_production_wiring_01_census as C
    out = []
    for c, a, exp in C.COUNTER:
        r = judge_multi(c, a, ledger)
        out.append({"canonical": c, "asr": a, "expected": exp, "multi_pass": r["pass"], "legacy_f1_pass": legacy_pass(c, a, True),
                    "ok": (r["pass"] if exp.startswith("pass") else not r["pass"])})
    return out


def ledger_stats(ledger):
    conf = collections.Counter(e.get("confidence") for e in ledger.values())
    n_oov_single, per_word = 0, []
    for k, e in ledger.items():
        s = e.get("surface", "").strip()
        if " " in s or e.get("entity_type") == "ja_reading_katakana":
            continue
        cs = candidates_for(s, ledger)
        if cs["candidates"] and cs["candidates"][0]["source"].startswith("C2"):
            n_oov_single += 1
            per_word.append({"word": s, "n_candidates": len(cs["candidates"]), "n_before_cap": cs["n_before_cap"],
                             "unconvertible": len(cs["unconvertible"]), "excluded": len(cs["excluded"]), "confidence": e.get("confidence")})
    return {"entries": len(ledger), "confidence": dict(conf), "usable_oov_single_token_words": n_oov_single,
            "max_candidates_per_word": max([p["n_before_cap"] for p in per_word] or [0]), "per_word": per_word}


def render_md(res, path):
    L = ["# EVAL_01 M1 OOV 複数発音候補方式 offline評価(API 0 / JPY0 / Production無変更 / Ledger読取のみ)", "",
         f"- Ledger md5 前後一致: {res['ledger_md5_before'] == res['ledger_md5_after']} / 候補上限 CAP={res['cap']} / 評価=既存転写の再判定のみ", "",
         "## 1. Melos said 12件 Before / F1のみ / 本設計(C1+C2)", "",
         "候補(事前固定・ASR非依存): " + "; ".join(f"[{c['source']} conf={c['confidence']}] {' '.join(c['pron'])}" for c in res["melos_candidates"]["candidates"]), "",
         "| # | level/target/take | OpenAI転写 | Azure転写 | Before(OR) | F1のみ(OR) | 本設計(OR) | 本設計(両エンジン同一候補) | 一致候補(出典) | 残差/判定理由 |", "|---|---|---|---|---|---|---|---|---|---|"]
    for i, e in enumerate(res["melos12"], 1):
        mt = []
        for eng in ("openai", "azure"):
            for s in e[eng]["subs"]:
                mt.append(f"{eng[:2]}:{s[0]}->{s[1]}[{s[3].split('|')[1]},conf={s[3].split('|')[2].split('=')[1]},{s[3].split('|')[3].split('=')[1]}]")
        reason = "; ".join(f"{eng[:2]}={e[eng]['verdict']}" + (f"({e[eng]['phon_verdict']})" if e[eng]["phon_verdict"] else "") for eng in ("openai", "azure"))
        L.append(f"| {i} | {e['level']}/{e['target']}/t{e['take']} | {e['openai']['asr']} | {e['azure']['asr']} | {'PASS' if e['before_or'] else 'NG'} | {'PASS' if e['f1_or'] else 'NG'} | {'PASS' if e['multi_or'] else 'NG'} | {'PASS' if e['multi_secondary_same_candidate'] else 'NG'} | {'<br>'.join(mt) or '(綴り一致/既存PASS)'} | {reason} |")
    m = res["melos12"]
    L += ["", f"集計: Before {sum(x['before_or'] for x in m)}/12、F1のみ {sum(x['f1_or'] for x in m)}/12、本設計(OR) {sum(x['multi_or'] for x in m)}/12、本設計(両エンジン同一候補で同意) {sum(bool(x['multi_secondary_same_candidate']) for x in m)}/12。",
          "注: 12件の実際の発音は独立に確認されていない(同一12音声・既存ASR転写)。一致した候補は全て `C2_ledger_alt`(confidence=low、Tier3が自動生成した『音楽用語としての別読み』)であり、システムが書いた低信頼推測である。ユーザー承認(複数の合理的候補のいずれか1つで可)の下で評価対象にしているが、高信頼へ書き換えてはいない。", "",
          "## 2. 674ペア(HR queue / er021 telemetry / er069 results_02)への適用", "", json.dumps(res["pairs"]["counts"], ensure_ascii=False),
          f"新規PASS={len(res['pairs']['new_pass'])}件(全件):", "", "| src | canonical | ASR | 置換 | 一致候補(出典) |", "|---|---|---|---|---|"]
    for r in res["pairs"]["new_pass"]:
        for s in r["subs"] or [("", "", "", "", "")]:
            L.append(f"| {r['src']} | {r['canonical'][:80]} | {r['asr'][:80]} | {s[0]}->{s[1]} ({s[2]}) | {s[3]} |")
    L += ["", "## 3. F1反例19件(COUNTER: 非PASS11/PASS維持6+参考2)", "", f"期待どおり: {sum(x['ok'] for x in res['counter_f1'])}/{len(res['counter_f1'])}", "",
          "## 4. 合成ケース", "", "| 類型 | canonical | ASR | 期待 | 結果 | verdict | 備考 |", "|---|---|---|---|---|---|---|"]
    for s in res["synthetic"]:
        L.append(f"| {s['kind']} | {s['canonical']} | {s['asr']} | {s['expected']} | {s['got']}{'' if s['match'] else ' (期待と相違)'} | {s['verdict']} | {s['note']}{' [fake Ledger]' if s['fake_ledger'] else ''} |")
    L += ["", "## 5. Ledger規模(候補が無制限にならない根拠)", "", json.dumps({k: v for k, v in res["ledger_stats"].items() if k != "per_word"}, ensure_ascii=False),
          "", "候補が使える単一語(CMU未収録・IPA変換可)の一覧: " + ", ".join(f"{p['word']}({p['n_candidates']}候補/{p['confidence']})" for p in res["ledger_stats"]["per_word"])]
    open(path, "w", encoding="utf-8").write(chr(10).join(L) + chr(10))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    md5_before = hashlib.md5(open(LEDGER_PATH, "rb").read()).hexdigest()
    ledger = load_ledger()
    res = {"ledger_md5_before": md5_before, "api_calls": 0, "cap": CAP}
    res["melos_candidates"] = candidates_for("melos", ledger)
    res["ledger_stats"] = ledger_stats(ledger)
    res["melos12"] = melos12(ledger)
    res["counter_f1"] = counter_eval(ledger)
    res["synthetic"] = synth_eval(ledger)
    res["pairs"] = pairs_eval(ledger)
    res["ledger_md5_after"] = hashlib.md5(open(LEDGER_PATH, "rb").read()).hexdigest()
    json.dump(res, open(os.path.join(a.out, "eval_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    render_md(res, os.path.join(a.out, "EVAL_01.md"))
    m = res["melos12"]
    print("melos12 before/f1/multi OR:", sum(x["before_or"] for x in m), sum(x["f1_or"] for x in m), sum(x["multi_or"] for x in m),
          "secondary-same-candidate:", sum(bool(x["multi_secondary_same_candidate"]) for x in m))
    print("pairs:", json.dumps({k: v for k, v in res["pairs"].items() if k != "new_pass"}, ensure_ascii=False))
    for r in res["pairs"]["new_pass"]:
        print("NEW", r["src"], "|", r["canonical"][:100], "|", r["asr"][:100], "|", r["subs"])
    print("counter ok:", sum(x["ok"] for x in res["counter_f1"]), "/", len(res["counter_f1"]))
    for x in res["counter_f1"]:
        if not x["ok"]:
            print("COUNTER_NG", x)
    for s in res["synthetic"]:
        print(("OK " if s["match"] else "NG "), s["kind"], "|", s["canonical"], "|", s["asr"], "|", s["expected"], "->", s["got"], s["verdict"], s["subs"])
    print("ledger unchanged:", md5_before == res["ledger_md5_after"])


if __name__ == "__main__":
    main()

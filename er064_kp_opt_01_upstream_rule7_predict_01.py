# KP-OPT-01 Phase1-A 項目4: Rule7(person表)とcanonicalization Promptの不一致から「正規化INVALIDの予測リスト」を作る(修正はしない、費用0)。
# Production関数 er003_key_words_canonicalization.validate_canonicalization_item を呼ぶだけ。
import glob, json, os, re, sys
sys.path.insert(0, os.getcwd())
import er003_key_words_canonicalization as kc
import er064_kp_opt_01_upstream_core as U

GEN = "generalize_person_dependent_reference"
PROMPT_TARGETS = {  # canonicalization Prompt 3.(一般形: one's/someone's/somebody's、someone/somebody/one、oneself)
    "poss": ["one's", "someone's", "somebody's"], "subj": ["someone", "somebody", "one"], "obj": ["someone", "somebody"], "refl": ["oneself"]}
TOKENS = {
    "poss": ["my", "your", "his", "her", "its", "their", "our", "yours", "theirs"],
    "subj": ["you", "they", "he", "she", "we", "i", "it"],
    "obj": ["me", "you", "him", "her", "them", "us", "it"],
    "refl": ["myself", "yourself", "himself", "herself", "itself", "themselves", "ourselves", "yourselves"],
}
TEMPLATE = {"poss": "take {t} place", "subj": "when {t} wait", "obj": "give {t} a hand", "refl": "pull {t} together"}

def check(cls, tok, tgt):
    disp = TEMPLATE[cls].format(t=tok)
    key = TEMPLATE[cls].format(t=tgt)
    v = kc.validate_canonicalization_item(key, disp, disp, GEN)
    return v["ok"]

matrix = []
for cls, toks in TOKENS.items():
    for tok in toks:
        for tgt in PROMPT_TARGETS[cls]:
            ok = check(cls, tok, tgt)
            matrix.append({"class": cls, "display_token": tok, "prompt_suggested_generic": tgt, "validator_ok": ok})
invalid_cells = [m for m in matrix if not m["validator_ok"]]

# 実記事候補への適用: improved/currentのshortlist + extractor span + DB placeholder見出し(記事に出現するもの)
person_tokens = {t for v in TOKENS.values() for t in v} - {"i", "it", "you", "her", "us", "me", "him"}  # 曖昧すぎる語(i/it/you/her/us/me/him)は別集計
amb_tokens = {"it", "you", "her", "us", "me", "him"}
def person_hits(surface):
    toks = re.findall(r"[A-Za-z']+", surface.lower())
    return [t for t in toks if t in person_tokens], [t for t in toks if t in amb_tokens]

risk = []
fixed = json.load(open(U.OUT_DIR + "/shortlists_improved_01.json", encoding="utf8"))
for key, ent in fixed["articles"].items():
    for cfg in ("current", "improved"):
        for c in ent[cfg]["candidates"]:
            ph, am = person_hits(c["surface_form"])
            if ph or am:
                risk.append({"source": f"{key}/{cfg}", "candidate": c["surface_form"], "strong_person_tokens": ph, "ambiguous_tokens": am})
spans = set()
for f in glob.glob("er064_output/kp_idiom_trial_01/**/extractor_raw.json", recursive=True):
    d = json.load(open(f, encoding="utf8"))
    for it in (d.get("parsed") or {}).get("items", []):
        spans.add(it.get("span", "").strip().lower())
span_risk = []
for s in sorted(spans):
    ph, am = person_hits(s)
    if ph or am:
        # Promptが提案しうる一般化を実際にvalidatorへ
        preds = []
        toks = s.split()
        for t in ph:
            cls = "poss" if t in TOKENS["poss"] else ("refl" if t in TOKENS["refl"] else "subj")
            for tgt in PROMPT_TARGETS[cls]:
                key_phrase = " ".join(tgt if x == t else x for x in toks)
                v = kc.validate_canonicalization_item(key_phrase, s, s, GEN)
                preds.append({"generic": tgt, "key_phrase": key_phrase, "ok": v["ok"]})
        span_risk.append({"span": s, "person_tokens": ph, "ambiguous": am, "predicted": preds,
                          "predicted_invalid": [p["key_phrase"] for p in preds if not p["ok"]]})

# 活用形戻しとの同時発生(person置換 + 動詞の屈折戻し): Rule7の1対1置換は語数同一・他token不変が条件
infl = []
for s in sorted(spans):
    ph, _ = person_hits(s)
    toks = s.split()
    if ph and toks and toks[0] not in person_tokens and toks[0] not in amb_tokens and re.search(r"(s|ed|ing)$", toks[0]):
        base = re.sub(r"(ing|ed|es|s)$", "", toks[0])
        k = " ".join([base] + ["one's" if x in TOKENS["poss"] else x for x in toks[1:]])
        v = kc.validate_canonicalization_item(k, s, s, GEN)
        infl.append({"span": s, "dict_form_key": k, "ok": v["ok"]})

out = {
    "cost_jpy": 0, "note": "予測のみ。Production(person表・Prompt)は修正していない。Phase 2のQA失敗(INVALID)を選定能力と切り分けるための事前リスト。",
    "table_vs_prompt_matrix_n": len(matrix), "predicted_invalid_cells": invalid_cells,
    "predicted_invalid_summary": sorted({f"{m['display_token']}->{m['prompt_suggested_generic']}" for m in invalid_cells}),
    "article_candidates_with_person_tokens": risk,
    "extractor_span_person_candidates": span_risk,
    "inflection_plus_person_double_change(Rule7語数同一・他token不変に抵触)": infl,
    "other_known_invalid_types_not_from_person_table": [
        "活用形戻し(been->be): `been behind price increases` -> `be behind price increases` (OPEN-310/336 Pkg R)",
        "辞書形の語追加(loan against the future 等): source_span外のtoken追加 (OPEN-325 b4)",
        "記事内固有語の過剰一般化(`one's own hidden clock` 等): OPEN-325 b4"],
    "remediation_candidates_NOT_APPLIED": [
        "(i) validatorの表をPromptに合わせて拡張: my/our/its/yours/theirs->someone's/somebody's、目的格(me/him/her/them/us/it)->someone/somebody、1人称/it系の再帰(myself/itself/ourselves/yourselves)->oneself を追加",
        "(ii) Promptを表に合わせて縮小: its/my/our/yours/theirs は one's のみ、目的格・myself/itself/ourselves は一般化対象から外す",
        "(iii) 折衷: 表拡張は人称(my/our)のみ、its->someone's は意味的に不自然なので許可しない(Prompt側で「its は one's のみ」と明記)"],
}
json.dump(out, open(U.OUT_DIR + "/rule7_predicted_invalid_01.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
print("invalid cells", len(invalid_cells), "of", len(matrix), "|", out["predicted_invalid_summary"])
print("article cands", len(risk), "span cands", len(span_risk), "infl", len(infl))

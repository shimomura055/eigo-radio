# -*- coding: utf-8 -*-
"""委任_22 held-out選定(API 0、gloss出力は一切見ない)。基準(事前固定):
 母集団=Production run由来の keywords_canonicalized.json (er112_kp_gm_kpset_03.candidates と同じ走査範囲・除外規則)で、本文が復元できるKP。
 (a) all_kps()(Trial_02〜04の115KP)・Trial_02のPRE_A1_DROPに含まれない
 (b) R 4KPを含まない
 (c) canonicalizationのfree-text reasoningが 比喩|慣用|イディオム|熟語|figurative|idiom を含む(canon_reasoning_census.pyの比喩認識と同一基準)
 (d) 3語以上、または具体名詞を含む(字義読み可能)は判定せず(結果非依存のため): 追加の絞りは掛けない
 選択: 家族別に key名ソート後 random.Random(22) でZ全数(<=6)+X(合計<=14になるまで)。1KPにつき最初に見つかったrun。"""
import glob, json, os, random, re, sys, collections
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')
import er112_kp_gm_kpset_02 as K2
import er112_kp_gm_kpset_03 as K3
import er112_kp_gm_trial_04 as X
import er112_kp_gm_trial_02 as T
ROOT = K3.ROOT
A = X.all_kps()
used = set(A) | set(T.PRE_A1_DROP) | {"draw a line", "an unseen clock", "question shaped like a trophy", "greener grass"}
pat = re.compile(r'比喩|慣用|イディオム|熟語|figurative|idiom')
out = {}
for p in sorted(glob.glob(str(ROOT / "**" / "keywords_canonicalized.json"), recursive=True)):
    pp = p.replace(chr(92), "/")
    rel = pp.split("eigo-radio/", 1)[-1]
    if not rel.startswith(K3.RECENT) or any(x in rel.lower() for x in K3.EXCL):
        continue
    d = os.path.dirname(pp)
    art = None
    for fn, mk in (("gloss_alignment_prompt.txt", K2.A_MARK1), ("canonicalization_prompt.txt", K2.A_MARK2)):
        f = os.path.join(d, fn)
        if os.path.exists(f):
            t = open(f, encoding="utf-8").read()
            if mk in t:
                art = t.split(mk, 1)[1].split("\n\n【Key Phrase候補", 1)[0]
                break
    if not art:
        continue
    try:
        its = json.load(open(p, encoding="utf-8")).get("items") or []
    except Exception:
        continue
    for it in its:
        k = (it.get("used_form") or it.get("key_phrase") or "").strip()
        s = it.get("source_sentence") or ""
        if not k or k.lower() in used or k.lower() in out or not s:
            continue
        if not (s[:40] in art.replace(K3.APOS, "'") or s[:40] in art):
            continue
        if not pat.search(it.get("reasoning") or ""):
            continue
        fam = "Z" if any(x in rel.lower() for x in ("er026", "family_z", "er073", "melos", "lemon", "open_window")) else "X"
        out[k.lower()] = dict(key=k, display=it.get("display_phrase") or k, sent=s, article=art, family=fam, run=rel.rsplit("/key_phrases/", 1)[0], src="heldout05", tier="held")
print("candidates", len(out), collections.Counter(v["family"] for v in out.values()))
Z = sorted(k for k, v in out.items() if v["family"] == "Z")
Xk = sorted(k for k, v in out.items() if v["family"] == "X")
rnd = random.Random(22)
selZ = Z if len(Z) <= 6 else sorted(rnd.sample(Z, 6))
selX = rnd.sample(Xk, min(len(Xk), 14 - len(selZ)))   # 抽出順を保持(先頭からN件で打切る)
sel = selZ + selX
for k in sel:
    print(out[k]["family"], k, "|", out[k]["sent"][:80], "|", out[k]["run"])
json.dump({k: out[k] for k in sel}, open("er112_output/kp_gm_trial_05/heldout_set_05.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(dict(all_candidates=sorted(out), Z=Z, X=Xk, selected=sel, seed=22), open("er112_output/kp_gm_trial_05/heldout_selection_log_05.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

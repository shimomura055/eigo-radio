"""Trial専用(非Production, API 0): 辞書(WordNet多語見出し)による決定論的な候補発見の再現性・ノイズ確認。
本文を語形還元し、(a)連続2-4語窓が WordNet の多語見出し(lemma に '_' を含む)に一致、(b)動詞+0〜3語を挟む小辞(分離形)が句動詞見出し 'verb_particle' に一致、を列挙する。
usage: python dict_seed_probe_01.py <repo_root> [out_json]"""
import sys, os, json, re
ROOT = os.path.abspath(sys.argv[1]); sys.path.insert(0, ROOT)
import er138_kp_n5_generalization_01 as n5
wn = n5._wn()
fx = json.load(open(f"{ROOT}/docs/research/KP-GENERALIZATION-N5-PRODUCTION-WIRING-01/fixtures/n5_trial_replay_fixture_01.json", encoding="utf-8"))
PARTS = {"away", "out", "up", "down", "off", "on", "in", "over", "back", "through", "around", "along", "aside", "apart", "forward", "together", "across", "by", "with", "for", "into", "to", "from", "at", "of", "about"}
MULTI = set()
for l in wn.all_lemma_names():
    if "_" in l: MULTI.add(l.lower())
def lem_v(w):
    return wn.morphy(w, "v") or w
def lem_n(w):
    return wn.morphy(w, "n") or w
def tokens(text):
    return [t for t in re.findall(r"[A-Za-z]+(?:'[a-z]+)?", text)]
def find(text):
    tk = tokens(text); low = [t.lower() for t in tk]; hits = {}
    for n in (2, 3, 4):
        for i in range(len(tk) - n + 1):
            win = low[i:i + n]
            forms = {"_".join(win), "_".join([lem_v(win[0])] + win[1:]), "_".join([lem_n(w) for w in win])}
            for f in forms:
                if f in MULTI:
                    hits.setdefault(" ".join(tk[i:i + n]), set()).add(f)
    for i, w in enumerate(low):
        v = lem_v(w)
        for gap in (1, 2, 3):
            j = i + gap + 1
            if j < len(low) and low[j] in PARTS and f"{v}_{low[j]}" in MULTI and (gap == 1 or low[i + 1] in {"it", "that", "this", "them", "something", "everything", "things", "thing", "the", "a", "your", "my", "his", "her", "their", "its"} ):
                hits.setdefault(" ".join(tk[i:j + 1]), set()).add(f"{v}_{low[j]}(sep)")
    return {k: sorted(v) for k, v in hits.items()}
out = {}
for cid, c in fx["cases"].items():
    out[cid] = find(c["text"])
    print(cid, len(out[cid]))
json.dump(out, open(sys.argv[2] if len(sys.argv) > 2 else os.devnull, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k in ("untidi_b1b", "untidi_a2"):
    print(k, json.dumps(out[k], ensure_ascii=False))

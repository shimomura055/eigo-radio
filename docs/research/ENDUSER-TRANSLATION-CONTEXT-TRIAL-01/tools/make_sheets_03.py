# ブラインド裁定シート作成(TRIAL_PLAN_02 §4)。各文について全条件の最終訳+verify前の1回目の訳+公開版訳の「重複を除いた全異なる訳」を匿名文字で提示。
# 出力: <ev dir>/sheet_<split>.json(裁定者に見せる。方式名なし)と sheet_key_<split>.json(対応表。裁定者は読まない)。
# 使い方: make_sheets_03.py --evdir ev05_dev --split dev --conds A,Ap,C,... --sets eval_sets_03.json --pool ev03/pool_all_generated_03.json [--seed N]
import json, os, sys, random, re, argparse, glob
ap = argparse.ArgumentParser()
ap.add_argument("--evdir", required=True); ap.add_argument("--split", required=True); ap.add_argument("--conds", required=True)
ap.add_argument("--sets", required=True); ap.add_argument("--pool", required=True); ap.add_argument("--seed", type=int, default=20261031)
ap.add_argument("--only", default="", help="glob-like prefix list of file tags to use, default=all parts_<cond>.jsonl")
a = ap.parse_args()
sets = json.load(open(a.sets, encoding="utf-8"))[a.split]
pool = json.load(open(a.pool, encoding="utf-8"))
pub = {}
for r in pool:
    pub[r["sid"]] = r["ja"]
sent = {}   # sid -> {en, slug, level, part, kind, stratum, idx, prev, next}
for e in sets:
    S = e["sentences"]
    for i, s in enumerate(S):
        sent[s["sid"]] = {"en": s["en"], "slug": e["slug"], "level": e["level"], "part": e["part"], "kind": e["kind"], "stratum": e["stratum"], "family": e["family"],
                          "prev": [x["en"] for x in S[max(0, i - 2):i]], "next": [x["en"] for x in S[i + 1:i + 3]]}

def first_translation(calls_log, unit_sents):
    """最初のtranslate応答から {sid: ja} を復元(parse不能ならNone)。unit_sents=その単位の文順(sidのlist)。"""
    for c in calls_log:
        if c["kind"] != "translate":
            continue
        try:
            t = (c["response"] or "").strip()
            m = re.match(r"^```(?:json)?\s*(.*?)\s*```$", t, re.S)
            d = json.loads(m.group(1) if m else t)
            tr = d["translations"]
            if [x["id"] for x in tr] != list(range(1, len(unit_sents) + 1)):
                return None
            return {sid: x["ja"].strip() for sid, x in zip(unit_sents, tr)}
        except Exception:
            return None
        break
    return None

variants = {}   # sid -> {text: set(of source labels)}
def add(sid, text, label):
    if text is None:
        return
    variants.setdefault(sid, {}).setdefault(text, set()).add(label)
final = {}      # (cond, sid) -> text|None
firstp = {}
for cond in a.conds.split(","):
    pf = os.path.join(a.evdir, f"parts_{cond}.jsonl"); cf = os.path.join(a.evdir, f"calls_{cond}.jsonl")
    if not os.path.exists(pf):
        print("missing", pf); continue
    calls = {}
    for ln in open(cf, encoding="utf-8"):
        d = json.loads(ln); calls[d["unit"]] = d["log"]
    for ln in open(pf, encoding="utf-8"):
        r = json.loads(ln)
        order = [sid for p in r["parts"] for sid in p["sids"]]
        ft = first_translation(calls.get(r["unit"], []), order)
        for sid in order:
            final[(cond, sid)] = r["ja"].get(sid)
            add(sid, r["ja"].get(sid), f"{cond}:final")
            if ft:
                firstp[(cond, sid)] = ft.get(sid)
                add(sid, ft.get(sid), f"{cond}:first")
for sid in sent:
    if sid in pub:
        add(sid, pub[sid], "PUB:final")
rng = random.Random(a.seed)
sheet, key = [], {}
sids = sorted(variants)
rng.shuffle(sids)
for n, sid in enumerate(sids, 1):
    texts = list(variants[sid]); rng.shuffle(texts)
    if len(texts) < 2:
        # 1種類のみ(全条件同一訳): 採点は必要(絶対評価のため)。提示する。
        pass
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:len(texts)]
    sheet.append({"row": n, "en": sent[sid]["en"], "prev": sent[sid]["prev"], "next": sent[sid]["next"], "variants": {L: t for L, t in zip(letters, texts)}})
    key[str(n)] = {"sid": sid, "map": {L: sorted(variants[sid][t]) for L, t in zip(letters, texts)}}
json.dump(sheet, open(os.path.join(a.evdir, f"sheet_{a.split}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
json.dump(key, open(os.path.join(a.evdir, f"sheet_key_{a.split}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("rows", len(sheet), "variants total", sum(len(r["variants"]) for r in sheet))

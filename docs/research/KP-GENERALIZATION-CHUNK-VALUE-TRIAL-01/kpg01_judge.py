# -*- coding: utf-8 -*-
"""独立判定(別系列: deepseek-v4-pro)。方式名を伏せ、Before/各方式の候補を重複排除して1 caseにつき1 callで判定。"""
import json, os, sys, random, glob
import kpg01_llm as L
HERE = os.path.dirname(os.path.abspath(__file__))
JUDGE_MODEL = os.environ.get("KPG_JUDGE", "deepseek-flash")
RES = os.path.join(HERE, "kpg01_work", "results")
JD = os.path.join(HERE, "kpg01_work", "judge"); os.makedirs(JD, exist_ok=True)
corpus = {c["id"]: c for c in json.load(open(os.path.join(HERE, "kpg01_work", "corpus.json"), encoding="utf-8"))}
RUBRIC = """あなたは英語学習教材の厳格な査読者です。ユーザー(教材責任者)は、AIが提示した『Key Phrase候補』を修正せずにそのまま選びたい。各候補が「そのまま選択可能」かを判定してください。
各候補は『表示形(英語)』『日本語の意味』『本文の語句』『本文の文』の組です。

## 判定基準(すべて満たすときだけ selectable=true)
1. 一般化の適切さ: 表示形は、学習者が別の文脈でも使える辞書の見出し語に近い形か。本文固有の目的語・修飾語・人称・後続名詞句が残っていない(自由に入れ替わる部分はsomething/someone/one's、核は保持。前置詞で終わる固定表現の後ろの名詞句は不要)。一方で、必要な前置詞・補語・固定語は欠けていない。
2. 意味保持: 一般化・原型化後の表示形が、本文での意味(語義)を変えていない。別の表現になっていない。
3. 日本語の意味との整合: 日本語の意味が表示形と本文での語義の両方に合っている(具体的すぎ/別語義/誤訳でない)。
4. 塊の学習価値: 次の3区分で C(まとまりとして覚える価値がある: 慣用表現・句動詞・強いコロケーション・固定表現・定着した名詞句) であること。W=個々の単語が難しいだけ、F=単語の自由な組合せ(各語の意味から明らか。例: confirm a clear fall は F で原則NG)。 C の例: make room for / blow a whistle / sales pitch。
5. 難易度: 上級者でも学ぶ価値がある水準(易しすぎる表現=TOO_EASYは不可)。
6. 英語として自然で、辞書にありそうな形であること。

## 出力(JSONのみ)
{"judgements":[{"id":番号,"cls":"W|F|C","selectable":true|false,"code":"OK|NOT_GENERALIZED|OVER_GENERALIZED|FREE_COMBINATION|WORD_ONLY|GLOSS_MISMATCH|MEANING_CHANGED|UNNATURAL|TOO_EASY|OTHER","note":"20字以内の理由"}]}
selectable=trueのときcodeはOK。不合格のときは最も主要な理由を1つcodeに。"""


def collect(cid):
    items = {}
    b = corpus[cid]["before"]
    if cid in ("ignobel_a2", "tesla_b1b"):
        p = os.path.join(HERE, "kpg01_work", "before_replica", cid, "before_replica.json")
        b = {"candidates": json.load(open(p, encoding="utf-8"))["items"]} if os.path.exists(p) else None
    srcs = {}
    if b:
        for c in b["candidates"]:
            if c.get("kind") == "word": continue
            srcs.setdefault("Before", []).append(dict(disp=c["used_form"], span=c["selection_phrase"], gloss=c["gloss"], sent=c.get("sentence") or ""))
    for p in glob.glob(os.path.join(RES, f"{cid}__*.json")):
        m = os.path.basename(p).split("__")[1][:-5]
        r = json.load(open(p, encoding="utf-8"))
        for i in r["items"]:
            srcs.setdefault(m, []).append(dict(disp=i["display_form"], span=i["source_span"], gloss=i["gloss_ja"], sent=i.get("source_sentence") or ""))
    return srcs


def judge_case(cid, methods=None):
    srcs = collect(cid)
    if methods: srcs = {k: v for k, v in srcs.items() if k in methods or k == "Before"}
    uniq = {}
    for m, lst in srcs.items():
        for it in lst:
            uniq.setdefault((it["disp"].lower(), it["span"].lower(), it["gloss"]), it)
    keys = list(uniq)
    random.Random(7).shuffle(keys)
    lines = [f"{n}. 表示形: {uniq[k]['disp']} / 意味: {uniq[k]['gloss']} / 本文の語句: {uniq[k]['span']} / 本文の文: {uniq[k]['sent']}" for n, k in enumerate(keys, 1)]
    o, meta = L.call_deepseek(JUDGE_MODEL, RUBRIC + "\n\n【候補】\n" + "\n".join(lines), tag=f"judge:{cid}", no_think=True)
    jm = {x["id"]: x for x in o["judgements"]}
    out = {"case": cid, "cost": meta["cost_jpy"], "by_method": {}, "unique": []}
    for n, k in enumerate(keys, 1):
        out["unique"].append(dict(uniq[k], **{"j": jm.get(n)}))
    for m, lst in srcs.items():
        rows = []
        for it in lst:
            k = (it["disp"].lower(), it["span"].lower(), it["gloss"])
            n = keys.index(k) + 1
            rows.append(dict(it, j=jm.get(n)))
        out["by_method"][m] = rows
    json.dump(out, open(os.path.join(JD, f"{cid}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return out


if __name__ == "__main__":
    for cid in sys.argv[1:]:
        o = judge_case(cid)
        print(cid, "¥", o["cost"])
        for m, rows in o["by_method"].items():
            ok = sum(1 for r in rows if r["j"] and r["j"]["selectable"])
            print(f"   {m:10s} {ok}/{len(rows)} selectable :", "; ".join(f"{r['disp']}[{(r['j'] or {}).get('code')}]" for r in rows))

# 文脈付与方式 A〜E の決定論ビルダ(Trial専用。Production経路へは接続しない)。
# 入力: 公開End User article.json(levels[lv].parts[].paragraphs[][].{sid,text}、topic_en)。出力: 翻訳Promptの「文脈」欄に入れる [{sid,en}]。
# 別AI検査・LLM抽出は使わない(完全に決定論)。Production Prompt本文は一切変更しない(文脈欄に入る文のlistが変わるだけ)。
import math, re
STOP = set("""this that with from have were would there their they them then than when what which while where will your about after again also because before being could does doing down each even ever first
from here into just like made make many more most much must never next only other over said same should some such take than that these they those through under until upon very want well were what whom
without would year years yours itself himself herself themselves still back came come going gone good great know known long might only people really right think though thought time today
""".split())
def level_sents(art, lv):
    out = []
    for pi, p in enumerate(art["levels"][lv]["parts"]):
        for pa in p.get("paragraphs") or []:
            for s in pa:
                if re.search(r"[぀-ヿ㐀-鿿]", s["text"]): continue   # 日本語文(Stdの日本語Preview等)は文脈に入れない
                out.append({"sid": s["sid"], "en": s["text"], "part": p["key"], "pi": pi})
    return out
def _toks(t):
    return {w for w in re.findall(r"[a-z]+", t.lower().replace("’", "'")) if len(w) >= 4 and w not in STOP}
def build_context(method, art, lv, part_key, extra=None):
    S = level_sents(art, lv); tgt = [s for s in S if s["part"] == part_key]
    if not tgt: raise KeyError(part_key)
    first = S.index(tgt[0]); last = S.index(tgt[-1]); title = {"sid": "TITLE", "en": art.get("topic_en", "")}
    others = [s for s in S if s["part"] != part_key]
    if method == "A": return []
    if method == "B":
        prev_pi = max((s["pi"] for s in S[:first]), default=None)
        return [s for s in S[:first] if s["pi"] == prev_pi] if prev_pi is not None else []
    if method == "C": return S[max(0, first - 3):first] + S[last + 1:last + 3]
    if method == "D": return [title] + others
    if method in ("E", "F"):
        N = len(S); df = {}
        toks = {s["sid"]: _toks(s["en"]) for s in S}
        for t in toks.values():
            for w in t: df[w] = df.get(w, 0) + 1
        qt = set().union(*[toks[s["sid"]] for s in tgt])
        scored = []
        for s in others:
            sh = [w for w in toks[s["sid"]] & qt if df[w] <= 8]
            if sh: scored.append((sum(math.log(N / df[w]) for w in sh), -abs(S.index(s) - first), s))
        top = sorted(scored, key=lambda x: (x[0], x[1]), reverse=True)[:6]
        sel = {s["sid"]: s for _, _, s in top}
        for s in S[max(0, first - 2):first]: sel.setdefault(s["sid"], s)
        ordered = sorted(sel.values(), key=lambda s: S.index(s))
        return [title] + ordered
    raise ValueError(method)

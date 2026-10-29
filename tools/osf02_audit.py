# OSF02 独立監査(gpt-6.1-sol・匿名・順序シャッフル、1 call)。DEV/Trial専用。使い方: OSF_PAID=1 py osf02_audit.py
import sys, os, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import osf02_gen as g2   # USAGE/CAP切替を含む
import osf01_gen as g
from osf01_audit import render
def L(n): return json.load(open(os.path.join(g.OUT, n + ".json"), encoding="utf-8"))
def collect():
    D = {}   # cell -> list of (src, item)
    for cell in g.CELLS:
        D[cell] = []
        for it in L(f"{cell}__v2__s1")["result"]["items"]: D[cell].append(("sol_v2_primary(委任_01)", it))
        for i, it in enumerate(L(f"{cell}__v3__l1")["result"]["items"], 1): D[cell].append((f"luna_v3/{i}", it))
    for cell, nm in (("x_adv", "have something to show for"), ("z_std", "let something show")):
        D[cell].append(("sol_v2_primary+pointfix(委任_02)", L(f"{cell}__pointfix__s1")["after"]))
    for i, it in enumerate(L("y_adv__v2__s2")["result"]["items"], 1): D["y_adv"].append((f"sol_v2_regen/{i}", it))
    for c in ("y_std", "y_adv"):
        for t, nm in (("s1", "sol_c3"), ("l1", "luna_c3_run1"), ("l2", "luna_c3_run2")):
            for it in L(f"{c}__c3__{t}")["result"]["items"]: D[c].append((f"{nm}/rank{it.get('rank')}", it))
    return D
def audit():
    D = collect(); mp = {}; blocks = []; n = 0
    for fam, fn in (("y", "夫が妻の姓を選ぶ(姓記事)"), ("x", "AIの島"), ("z", "告げ口心臓")):
        for lv, ln in (("std", "Standard(A2目標、学習者A2〜B1)"), ("adv", "Advanced(B1目標、学習者B1〜B2)")):
            cell = f"{fam}_{lv}"; inp = g.inputs_for(cell); items = D[cell][:]; random.Random(23).shuffle(items)
            blocks.append(f"## 記事: {fn} / レベル: {ln}\n### 本文\n{inp['body']}\n### 既存の学習項目(Key Phrase/Word): " + "; ".join(k[0] for k in inp["kp"]) + "\n### 文法: " + ("; ".join(inp["grammar"]) or "なし") + "\n")
            for src, it in items:
                n += 1; k = f"C{n:02d}"; mp[k] = {"cell": cell, "src": src, "core": it["core_expression"]}; blocks.append(f"#### {k}\n" + render(it))
    prompt = f"""あなたは日本語話者向け英語教育の専門家(ネイティブ水準の英語力を持つ査読者)です。下の記事(3記事×2レベル)に基づく学習コーナー「One Step Further」の案を、匿名で厳しく採点してください。各案は、記事の話題から学習者の表現の引き出しを増やす表現です。
狙いの学習体験: 学習者が「聞いたことはあるけど自分では使えない」「こんな言い方があるのか、覚えたい」と感じること。難語・単なる言い換え・辞書的な語義説明は低評価。
{chr(10).join(blocks)}
# 採点(各案、1〜5、整数)
- learning_value: 日本人学習者が「覚えたい・自分でも使ってみたい」と感じるか。
- accuracy: 英語の用法・例文・日本語訳・説明の正確さ(誇張を含む)。
- example_natural: 発展の英文が、ネイティブが日常で実際に言う自然な文か(硬い・不自然なら低い)。
- naturalness_ja: 日本語解説の簡潔さ・分かりやすさ。
- relevance: 記事の話題・気持ちとの関連の明確さ。
- level_fit: 当該レベルへの適合(Standardに難しすぎる/Advancedに易しすぎるなら低い)。
- fabrication: 本文にない事実・人物の心理を本文の内容として述べていればtrue。
- kp_overlap: Key Phrase/Word・文法と不必要に重複していればtrue。
- known_to_most: 当該レベルの日本人学習者の多くが既に知っている(新味が薄い)ならtrue。
- issues: 具体的な問題点(英文や記述を引用。無ければ空配列)。最大2件、各40字以内。
# 出力(JSONのみ。キーは全案C01〜C{n:02d})
{{"scores": {{"C01": {{"learning_value": 0, "accuracy": 0, "example_natural": 0, "naturalness_ja": 0, "relevance": 0, "level_fit": 0, "fabrication": false, "kp_overlap": false, "known_to_most": false, "issues": []}}}}, "top": {{"y_std": ["C??"], "y_adv": ["C??"], "x_std": ["C??"], "x_adv": ["C??"], "z_std": ["C??"], "z_adv": ["C??"]}}, "comment": "全体所見を3文以内"}}"""
    client = g.get_client(); text, m, ud, c, el = g.call(client, "gpt-6.1-sol", prompt, "osf02__AUDIT", max_out=20000)
    json.dump({"map": mp, "model": m, "usage": ud, "cost_jpy": c, "elapsed_sec": el, "raw": text}, open(os.path.join(g.OUT, "osf02__AUDIT.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(n, "items", m, ud, c, el, "spent", round(g.spent(), 3))
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "dry":
        D = collect(); print({k: len(v) for k, v in D.items()}, sum(len(v) for v in D.values()))
    else: audit()

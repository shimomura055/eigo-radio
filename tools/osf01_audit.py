# OSF01 独立監査(gpt-6.1-sol・匿名・順序シャッフル)。DEV/Trial専用。使い方: OSF_PAID=1 py osf01_audit.py <family: y|x|z>...
# 1 familyにつき1 call。Std/Adv両方の全候補(v1/v2 × sol/luna)+現行ニュアンス解説(比較用)を混ぜて匿名採点する。
import sys, os, json, random, time, threading
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import osf01_gen as g
AUD = "gpt-6.1-sol"
SRC = [("v1", "s1"), ("v1", "l1"), ("v2", "s1"), ("v2", "l1"), ("v2", "l2")]   # (ver, tag)。v1/l2は費用配分で監査対象外(人手評価のみ)
NQT = os.path.join(g.ROOT, "docs/research/NUANCE-QUALITY-IMPROVEMENT-TRIAL-01/out")
def nuance_items(fam, lv):
    if fam == "y":
        sd = f"{g.YB}/a2/study_text" if lv == "std" else f"{g.YB}/study_text"; c = g._rj(f"{sd}/confirmed_nuance.json")["candidate"]; tag = "現行Production採用文"
    else:
        c = json.load(open(os.path.join(NQT, f"{'ai_island' if fam == 'x' else 'tth'}_{lv}_NEW3.json"), encoding="utf-8"))["candidate"]; tag = "ニュアンス改善Trial v3"
    if not c: return None
    s = f"[ニュアンス解説] 表現: {c['expression']}\n焦点: {c['focus']}\n本文引用: {c['quote_en']} / {c['quote_ja']}\n"
    for x in c.get("comparisons") or []: s += f"  比較: {x['en']} / {x['ja']} / {x['note_ja']}\n"
    return (f"nuance:{tag}", s + f"解説: {c['explanation_ja']}\n", c["expression"])
def render(it):
    return (f"[One Step Further] 着想: {it['topic_hook_ja']}\n基本: {it['basic_en']} / {it['basic_ja']}\n発展: {it['further_en']} / {it['further_ja']}\n核: {it['core_expression']}\n"
            f"ポイント: {it['point_ja']}\n選定理由: {it['why_ja']}\n意味の違い: {it['meaning_shift_note']}\n")
def audit(fam):
    levels = {}
    for lv in ("std", "adv"):
        cell = f"{fam}_{lv}"; inp = g.inputs_for(cell); items = []
        for ver, tag in SRC:
            d = json.load(open(os.path.join(g.OUT, f"{cell}__{ver}__{tag}.json"), encoding="utf-8"))
            for i, it in enumerate(d["result"]["items"]): items.append((f"{ver}/{tag}/{i+1}", render(it), it["core_expression"]))
        n = nuance_items(fam, lv)
        if n: items.append(n)
        random.Random(11).shuffle(items); levels[lv] = (inp, items)
    mp = {}; blocks = []
    for lv, ln in (("std", "Standard(A2目標、学習者A2〜B1)"), ("adv", "Advanced(B1目標、学習者B1〜B2)")):
        inp, items = levels[lv]; blocks.append(f"## レベル: {ln}\n### 本文\n{inp['body']}\n### 既存の学習項目(Key Phrase/Word): " + "; ".join(k[0] for k in inp["kp"]) + "\n### 文法: " + ("; ".join(inp["grammar"]) or "なし") + "\n")
        for j, (src, txt, core) in enumerate(items, 1):
            k = f"{lv[0].upper()}{j}"; mp[k] = {"src": src, "core": core}; blocks.append(f"#### {k}\n{txt}")
    prompt = f"""あなたは日本語話者向け英語教育の専門家(ネイティブ水準の英語力を持つ査読者)です。下の記事(2レベル)に基づく学習コーナーの案を、匿名で厳しく採点してください。各案は「記事の話題から、学習者の表現の引き出しを増やす表現」または「従来のニュアンス解説」です。
狙いの学習体験: 学習者が「聞いたことはあるけど自分では使えない」「こんな言い方があるのか、覚えたい」と感じること。難語・単なる言い換え・辞書的な語義説明は低評価。
{chr(10).join(blocks)}
# 採点(各案、1〜5、整数)
- learning_value: 日本人学習者が「覚えたい・自分でも使ってみたい」と感じるか(新しい発見、他場面への応用、言い換えでない)。
- accuracy: 英語の用法・例文の自然さ・日本語訳の正確さ・意味や場面の説明の正確さ。
- naturalness_ja: 日本語解説の簡潔さ・分かりやすさ。
- relevance: 記事の話題・気持ちとの関連の明確さ。
- level_fit: 当該レベルへの適合。
- fabrication: 本文にない事実・人物の心理を本文の内容として述べていればtrue。
- kp_overlap: Key Phrase/Word・文法と不必要に重複していればtrue。
- known_to_most: 当該レベルの日本人学習者の多くが既に知っている(新味が薄い)ならtrue。
- issues: 具体的な問題点(英文や記述を引用。無ければ空配列)。1案につき最大2件、各40字以内。
# 出力(JSONのみ)
{{"scores": {{"S1": {{"learning_value": 0, "accuracy": 0, "naturalness_ja": 0, "relevance": 0, "level_fit": 0, "fabrication": false, "kp_overlap": false, "known_to_most": false, "issues": []}}, "...": {{}}}}, "top3": {{"std": ["S?"], "adv": ["A?"]}}, "comment": "全体所見を3文以内"}}"""
    client = g.get_client(); t0 = time.time(); text, m, ud, c, el = g.call(client, AUD, prompt, f"{fam}__AUDIT", max_out=14000)
    json.dump({"family": fam, "map": mp, "model": m, "usage": ud, "cost_jpy": c, "elapsed_sec": el, "raw": text}, open(os.path.join(g.OUT, f"{fam}__AUDIT.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(fam, m, ud, c, el)
os.environ.setdefault("OSF_PAID", "0")
if __name__ == "__main__":
    ths = [threading.Thread(target=audit, args=(f,)) for f in sys.argv[1:]]; [t.start() for t in ths]; [t.join() for t in ths]; print("spent", round(g.spent(), 3))

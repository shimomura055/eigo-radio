# 独立監査(上位モデル gpt-6.1-sol): 生成物を匿名化・順序シャッフルして、学習価値/正確性/自然さ/本文逸脱/レベル適合を採点。DEV/Trial専用。
import sys, os, json, random, time, threading
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nqt01 as q
AUD = "gpt-6.1-sol"
CELLS = [a for a in sys.argv[1:] if not a.startswith("--")]
ONLY = dict(a[2:].split("=",1) for a in sys.argv[1:] if a.startswith("--")).get("only")
ONLY = set(ONLY.split(",")) if ONLY else None
TAG = "AUDIT" if not ONLY else "AUDITV3"
T = q.v02a.trial.load_targets(); client = q.v02a.get_client()
def render(c):
    s = f"表現: {c['expression']}\n焦点: {c['focus']}\n本文引用: {c['quote_en']}\n引用訳: {c['quote_ja']}\n"
    if c.get("point_ja"): s += f"ポイント: {c['point_ja']}\n"
    for x in c.get("comparisons") or []: s += f"  比較 {x['label']}{'(本文)' if x.get('is_text') else ''}: {x['en']} / {x['ja']} / {x['note_ja']}\n"
    s += f"解説: {c['explanation_ja']}\n"; return s
def audit(cell):
    inputs = q.build_inputs_for(cell, T); level = inputs["level"]
    conds = [f[:-5].split("_", 2) for f in []]
    items = []
    for f in sorted(os.listdir(q.ODIR)):
        if f.startswith(cell + "_") and f.endswith(".json") and "summary" not in f:
            cond = f[len(cell) + 1:-5]; d = json.load(open(os.path.join(q.ODIR, f), encoding="utf-8"))
            if d.get("candidate") and (ONLY is None or cond in ONLY): items.append((cond, d["candidate"]))
    random.Random(7).shuffle(items); mp = {f"X{i+1}": cond for i, (cond, _) in enumerate(items)}
    body = "\n\n".join(inputs["paragraphs"])
    lv = "Standard(A2目標英文、学習者A2〜B1)" if level == "a2" else "Advanced(B1目標英文、学習者B1〜B2)"
    prompt = f"""あなたは日本語話者向け英語教育の専門家(ネイティブ水準の英語力を持つ査読者)です。下の本文に基づく『ニュアンス解説』の複数の案{len(items)}件を独立に審査してください。案の作成方法は不明です。
# 対象レベル: {lv}
# 本文
{body}

# 審査対象
""" + "\n".join(f"## {k}\n{render(c)}" for k, (cond, c) in zip(mp, items)) + """
# 審査基準(各案ごとに)
- learning_value(1-5): 学習者が新しい発見をし、使い分け・文脈による意味変化を具体的に理解できるか。単なる言い換えなら低い。
- accuracy(1-5): 英語の用法・比較文の自然さ・日本語訳の正確さ。誤り・不自然な英文・訳が差を反映しない場合は低くする。
- naturalness_ja(1-5): 日本語解説の自然さ・読みやすさ。
- deviation(true/false): 本文にない事実・人物・状況を本文の内容として述べている、または文脈から逸脱している場合true。
- level_fit(1-5): 上記レベルに語彙・長さ・難度が適切か。
- issues: 具体的な問題点(英文・訳・記述を引用して指摘。無ければ空)。
# 出力(JSONのみ)
{"scores": {"X1": {"learning_value": 0, "accuracy": 0, "naturalness_ja": 0, "deviation": false, "level_fit": 0, "issues": ["..."]}, ...}, "ranking_by_learning_value": ["X?", ...], "comment": "全体所見を2〜3文"}
"""
    base = q.er._default_call_fn_factory(client, AUD, 8000); t0 = time.time()
    text, model, usage, rid = base(prompt); el = round(time.time() - t0, 2); cost = q.er._cost_jpy(model, usage or {})
    with open(q.USAGE_LOG, "a", encoding="utf-8") as f: f.write(json.dumps({"tag": f"{cell}_{TAG}", "model": model, "usage": usage, "cost_jpy": cost, "elapsed_sec": el}, ensure_ascii=False) + "\n")
    json.dump({"cell": cell, "map": mp, "model": model, "usage": usage, "cost_jpy": cost, "elapsed_sec": el, "raw": text}, open(os.path.join(q.ODIR, f"{cell}_{TAG}.audit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(cell, model, usage, cost, el)
os.environ["NQT_PAID"] = "1"
ths = [threading.Thread(target=audit, args=(c,)) for c in CELLS]; [t.start() for t in ths]; [t.join() for t in ths]
print("spent", round(q.spent(), 3))

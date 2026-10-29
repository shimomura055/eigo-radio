# 比較ページ生成(DEV/Trial)。out/*.json(生成物)と out/*.audit.json(独立監査)から user_test/nuance_quality_trial_01/index.html を作る。
import json, os, glob, html, re, sys
BASE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(BASE, "..", "out"); ROOT = os.path.abspath(os.path.join(BASE, "..", "..", "..", ".."))
DEST = os.path.join(ROOT, "user_test", "nuance_quality_trial_01"); os.makedirs(DEST, exist_ok=True)
E = html.escape
TITLES = {"y_surname": "Family Y「夫が妻の姓を選ぶとき、それぞれの声」", "ai_island": "Family X「AIの島」", "tth": "Family Z「告げ口心臓(The Tell-Tale Heart)」", "y_redelivery": "Family Y「再配達料」"}
VER = {"CUR": ("現行Prompt(現行Production形)", "cur"), "CURFIX": ("現行Prompt・表現固定", "cur"), "CURFIXAT": ("現行Prompt・表現固定(at least)", "cur"),
       "NEW": ("改善v1・自由選定", "new1"), "NEWFIX": ("改善v1・同一表現", "new1"), "NEWFIXAT": ("改善v1・同一表現(at least)", "new1"),
       "NEW2": ("改善v2・自由選定", "new2"), "NEW2FIX": ("改善v2・同一表現", "new2"), "NEW2FIXAT": ("改善v2・同一表現(at least)", "new2"),
       "NEW3": ("改善v3(推奨案)・自由選定", "new3"), "NEW3FIX": ("改善v3(推奨案)・同一表現", "new3"), "NEW3FIXAT": ("改善v3(推奨案)・同一表現(at least)", "new3")}
def vinfo(cond):
    m = re.match(r"^([A-Z0-9]+?)(_r(\d))?$", cond); b = m.group(1); lab, fam = VER[b]
    return lab + (f"・再生成{m.group(3)}回目" if m.group(2) else ""), fam
ORDER = ["CUR", "CURFIX", "CURFIXAT", "NEW3", "NEW3FIX", "NEW3FIXAT", "NEW2", "NEW2FIX", "NEW2FIXAT", "NEW", "NEWFIX", "NEWFIXAT"]
def okey(cond):
    m = re.match(r"^([A-Z0-9]+?)(_r(\d))?$", cond); return (ORDER.index(m.group(1)), int(m.group(3) or 0))
# 監査スコア(匿名・順序シャッフルでsolが採点)
AUD = {}
for p in sorted(glob.glob(os.path.join(OUT, "*.audit.json"))):   # AUDIT -> AUDITV3 の順(後勝ち)
    a = json.load(open(p, encoding="utf-8")); r = json.loads(a["raw"][a["raw"].index("{"):a["raw"].rindex("}") + 1])
    for k, v in r["scores"].items(): AUD.setdefault(a["cell"], {})[a["map"][k]] = (v, os.path.basename(p))
def render_cand(c):
    s = f"<p><b>表現:</b> {E(c['expression'])}　<span class=sec>焦点: {E(c['focus'])}</span></p>"
    s += f"<div class=q><b>本文の英文</b><br>{E(c['quote_en'])}<br><b>日本語訳</b><br>{E(c['quote_ja'])}</div>"
    if c.get("point_ja"): s += f"<p><b>ポイント</b><br>{E(c['point_ja'])}</p>"
    if c.get("comparisons"):
        s += "<p><b>比較</b></p>"
        for x in c["comparisons"]:
            s += f"<div class='cmp{' txt' if x.get('is_text') else ''}'><b>{E(x['label'])}.{'(本文)' if x.get('is_text') else ''}</b> {E(x['en'])}<br>{E(x['ja'])}<br><span class=sec>{E(x['note_ja'])}</span></div>"
    s += f"<p><b>{'ここが重要 / 解説' if c.get('comparisons') is not None else '解説'}</b><br>{E(c['explanation_ja'])} <span class=sec>({len(c['explanation_ja'])}字)</span></p>"
    return s
def block(cell, cond, d):
    lab, fam = vinfo(cond); c = d.get("candidate"); u = d["usage"]
    h = f"<div class='blk {fam}'><h4>{E(lab)} <span class=sec>[{E(cond)}]</span></h4>"
    if not c:
        r = (d.get("generation") or {}).get("model_reason_ja") or d.get("no_candidate_reason")
        return h + f"<p>0件(該当なし): {E(str(r))}</p><p class=sec>費用 ¥{u['cost_jpy']}</p></div>"
    ov = (c.get("overlap_check") or {}).get("verdict")
    h += render_cand(c)
    el = sum((x.get("elapsed_sec") or 0) for x in u["calls"])
    h += f"<p class=sec>既存QA Gate(重複判定): <b>{E(str(ov))}</b>　機械チェック(比較構造): {E(str(d.get('trial_extra_issues') if d.get('trial_extra_issues') is not None else '現行形のため対象外'))}　生成+判定 {el:.0f}秒・¥{u['cost_jpy']}・{u['input_tokens']}/{u['output_tokens']} tokens</p>"
    a = AUD.get(cell, {}).get(cond)
    if a:
        v = a[0]; h += f"<table class=sc><tr><th colspan=5>独立監査(gpt-6.1-sol・匿名採点、1〜5)</th></tr><tr><td>学習価値 {v['learning_value']}</td><td>正確性 {v['accuracy']}</td><td>自然さ {v['naturalness_ja']}</td><td>レベル適合 {v['level_fit']}</td><td>本文逸脱 {'あり' if v['deviation'] else 'なし'}</td></tr></table>"
        if v.get("issues"): h += "<ul class=iss>" + "".join(f"<li>{E(i)}</li>" for i in v["issues"]) + "</ul>"
    else: h += "<p class=sec>独立監査: 未実施(費用配分上、対象は一部のみ)</p>"
    h += "<table class=ev><tr><th>あなたの評価</th><td>学習価値 ○△× ／ 正確性 ○△× ／ 自然さ ○△× ／ 文脈逸脱 なし・あり ／ レベル差 ○△×　メモ: ____________</td></tr></table></div>"
    return h
def prod_block():   # 現行Production公開候補(Y姓記事・run_02)
    out = ""
    for lv, p in (("Standard", "er121_output/family_y_production_01/surname_choice/run_02/a2/study_text/nuance_candidate.json"), ("Advanced", "er121_output/family_y_production_01/surname_choice/run_02/study_text/nuance_candidate.json")):
        d = json.load(open(os.path.join(ROOT, p), encoding="utf-8")); out += f"<div class='blk cur'><h4>参考: 現行Production候補({lv}・{E(d['model'])}・最初に生成されたもの)</h4>{render_cand(d['candidate'])}</div>"
    return out
cells = {}
for f in sorted(os.listdir(OUT)):
    m = re.match(r"^(y_surname|ai_island|tth|y_redelivery)_(std|adv)_([A-Z0-9]+(?:_r\d)?)\.json$", f)
    if m and m.group(3) in {x for x in ORDER} | {f"{x}_r{i}" for x in ORDER for i in (2, 3)}:
        cells.setdefault((m.group(1), m.group(2)), {})[m.group(3)] = json.load(open(os.path.join(OUT, f), encoding="utf-8"))
css = """body{font-family:sans-serif;max-width:1180px;margin:1em auto;padding:0 1em;line-height:1.6}h2{border-bottom:2px solid #468;padding-bottom:4px;margin-top:2em}h3{margin-top:1.5em;background:#eef;padding:4px 8px}
.note{background:#fff8e0;padding:10px;border:1px solid #cb8;margin:1em 0}.blk{border:1px solid #ccc;border-radius:6px;padding:6px 12px;margin:10px 0}.cur{background:#fafafa;border-left:5px solid #999}.new1,.new2{background:#f4fbf4;border-left:5px solid #9c9}.new3{background:#eefaff;border-left:5px solid #38c}
.q{background:#f1f1f1;padding:6px;margin:4px 0}.cmp{margin:4px 0 4px 1em;padding:4px 8px;border-left:3px solid #aaa;background:#fff}.cmp.txt{border-left-color:#c60;background:#fff7ec}.sec{color:#666;font-size:.85em}table.sc,table.ev{border-collapse:collapse;margin:4px 0;font-size:.9em}table.sc td,table.sc th,table.ev td,table.ev th{border:1px solid #ccc;padding:3px 8px}.iss{font-size:.85em;color:#a33}
details{margin:6px 0}summary{cursor:pointer;color:#036}"""
H = [f"<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><title>ニュアンス解説 品質改善Trial 比較(現行版/改善版)</title><meta name='viewport' content='width=device-width, initial-scale=1'><meta name='robots' content='noindex'><style>{css}</style></head><body>",
     "<h1>ニュアンス解説 品質改善Trial(NUANCE-QUALITY-IMPROVEMENT-TRIAL-01)比較ページ</h1>",
     "<div class=note><b>Trialの結果であり、Production採用ではありません。</b>方式の採否はユーザー判断です(Production Prompt・生成経路は一切変更していません)。使用モデル: 生成=gpt-6-luna(現行Production routeと同一)、独立監査=gpt-6.1-sol。『現行Prompt』は現行Productionと同一のPrompt/検証/重複判定(er134)をそのまま実行したもの、『改善v1〜v3』はTrial専用Promptです。v3が推奨案(v1→v2→v3は、独立監査で見つかった『比較が二項に偏る』『断定しすぎ』への1段ずつの対処)。「同一表現」=現行版が選んだ表現(Y姓記事は現行Production候補と同じ表現)に固定して、解説の作り方だけを比べたものです。全ての解説は本文の引用に基づきます。</div>",
     "<p>見方: 灰=現行版、青=改善v3(推奨案)、緑=改善v1/v2(折りたたみ)。オレンジ枠=本文の文そのもの。評価欄はあなたの所見を記入するための目安です(保存機能はありません)。</p>"]
for t in ("y_surname", "ai_island", "tth", "y_redelivery"):
    H.append(f"<h2>{E(TITLES[t])}</h2>")
    if t == "y_surname": H.append(prod_block())
    for lv, ln in (("std", "Standard"), ("adv", "Advanced")):
        cs = cells.get((t, lv)) or {}
        H.append(f"<h3>{ln}</h3>")
        for cond in sorted(cs, key=okey):
            fam = vinfo(cond)[1]; b = block(f"{t}_{lv}", cond, cs[cond])
            if fam in ("new1", "new2"): H.append(f"<details><summary>{E(vinfo(cond)[0])} [{E(cond)}] を開く</summary>{b}</details>")
            else: H.append(b)
H.append("<p class=sec>生成物・Prompt・費用ログ: docs/research/NUANCE-QUALITY-IMPROVEMENT-TRIAL-01/(TRIAL_DESIGN_01.md / RESULT_01.md / out/)</p></body></html>")
open(os.path.join(DEST, "index.html"), "w", encoding="utf-8", newline="\n").write("\n".join(H))
print("written", os.path.join(DEST, "index.html"), sum(len(v) for v in cells.values()), "blocks")

# OSF01 比較ページ生成(DEV/Trial専用)。index.html=学習コンテンツ本体(主候補=gpt-6.1-sol v2)+参考(本番ライン luna v2/現行ニュアンス)。dev_log.html=開発ログ・内部評価(分離)。
import sys, os, json, html, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import osf01_gen as g
E = html.escape
DEST = os.path.join(g.ROOT, "user_test", "one_step_further_trial_01"); os.makedirs(DEST, exist_ok=True)
NQT = os.path.join(g.ROOT, "docs/research/NUANCE-QUALITY-IMPROVEMENT-TRIAL-01/out")
ARTICLE = {"y": "Family Y「夫が妻の姓を選ぶとき、それぞれの声」(姓記事)", "x": "Family X「AIの島」(The Island Resets! But AI Has “Strategy Notes”)", "z": "Family Z「告げ口心臓」(The Tell-Tale Heart)"}
LV = {"std": "Standard", "adv": "Advanced"}
def load(cell, ver, tag): return json.load(open(os.path.join(g.OUT, f"{cell}__{ver}__{tag}.json"), encoding="utf-8"))
def item_html(it, n, total):
    s = f"<div class=item><div class=num>表現 {n}/{total}</div>"
    s += f"<p class=hook><b>着想した記事の話題</b><br>{E(it['topic_hook_ja'])}</p>"
    s += f"<div class=pair><div class=base><span class=lab>基本の表現</span><div class=en>{E(it['basic_en'])}</div><div class=ja>{E(it['basic_ja'])}</div></div>"
    s += f"<div class=arrow>→</div><div class=further><span class=lab>One Step Further</span><div class=en>{E(it['further_en'])}</div><div class=ja>{E(it['further_ja'])}</div><div class=core>覚える形: <b>{E(it['core_expression'])}</b></div></div></div>"
    s += f"<p><b>学習ポイント</b><br>{E(it['point_ja'])}</p>"
    if it.get("meaning_shift_note", "").strip(): s += f"<p class=shift><b>基本表現との違い</b><br>{E(it['meaning_shift_note'])}</p>"
    s += f"<p class=why><b>なぜこの表現を選んだか</b><br>{E(it['why_ja'])}</p></div>"
    return s
def nuance_html(fam, lv):
    if fam == "y":
        sd = f"{g.YB}/a2/study_text" if lv == "std" else f"{g.YB}/study_text"; c = g._rj(f"{sd}/confirmed_nuance.json")["candidate"]; lab = "現行のニュアンス解説(この記事で採用済みの文)"
    else:
        c = json.load(open(os.path.join(NQT, f"{'ai_island' if fam == 'x' else 'tth'}_{lv}_CUR.json"), encoding="utf-8"))["candidate"]; lab = "現行のニュアンス解説(現行方式で生成した例)"
    return f"<p class=sec>{lab}</p><p><b>表現:</b> {E(c['expression'])}　<span class=sec>焦点: {E(c['focus'])}</span></p><div class=q>{E(c['quote_en'])}<br>{E(c['quote_ja'])}</div><p>{E(c['explanation_ja'])}</p>"
CSS = """body{font-family:'Hiragino Sans','Yu Gothic',sans-serif;max-width:980px;margin:1em auto;padding:0 1em;line-height:1.7;color:#222}h1{font-size:1.4em}h2{border-bottom:3px solid #35a;padding-bottom:4px;margin-top:2.2em}h3{background:#eef;padding:6px 10px;margin-top:1.6em}
.note{background:#fff8e0;border:1px solid #cb8;padding:10px;margin:1em 0}.item{border:1px solid #ccd;border-radius:8px;padding:8px 14px;margin:12px 0;background:#fcfcff}.num{color:#35a;font-weight:bold;font-size:.9em}
.pair{display:flex;gap:10px;align-items:stretch;flex-wrap:wrap}.base,.further{flex:1;min-width:250px;padding:8px 12px;border-radius:6px}.base{background:#f2f2f2}.further{background:#e6f4e6;border:2px solid #4a4}.arrow{align-self:center;font-size:1.6em;color:#35a}
.lab{font-size:.8em;color:#555;font-weight:bold}.en{font-size:1.1em;margin:.2em 0}.ja{color:#444}.core{margin-top:.4em;font-size:.95em}.hook{background:#f7f7ff;padding:6px 10px;border-left:4px solid #88a}.shift{color:#333;background:#fff7e8;padding:6px 10px}.why{color:#444}
.sec{color:#666;font-size:.9em}.q{background:#f1f1f1;padding:6px 10px;margin:4px 0}details{margin:8px 0}summary{cursor:pointer;color:#036}table{border-collapse:collapse}td,th{border:1px solid #bbb;padding:3px 8px;font-size:.9em}"""
def page_index():
    H = [f"<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>One Step Further 品質検証Trial 比較ページ</title><style>{CSS}</style></head><body>",
         "<h1>One Step Further｜もう一歩進んだ英語表現(新コーナー案) 品質検証Trial</h1>",
         "<div class=note><b>これはTrialの試作です。正式採用ではありません。</b>採用するか、現行の「ニュアンス解説」とどう扱うかは、読んだうえでユーザーが判断します。既存の本文・音声・Key Phrase・文法解説は変更していません。<br>各記事のStandard／Advancedごとに、記事の話題から着想した表現を1〜2件ずつ載せています。評価の内部データ・開発ログは別ページ(<a href='dev_log.html'>開発ログ・内部評価</a>)に分けています。</div>",
         "<p class=sec>見方: 灰色=基本の表現(平易な言い方)、緑=One Step Further(もう一歩進んだ表現)。基本と発展が同義でない場合は「基本表現との違い」を明記しています。基本・発展の英文は、学習者が自分の状況で使える一般的な文で、記事の出来事そのものではありません。</p>",
         "<ul>" + "".join(f"<li><a href='#{f}'>{E(ARTICLE[f])}</a></li>" for f in "yxz") + "</ul>"]
    for f in "yxz":
        H.append(f"<h2 id='{f}'>{E(ARTICLE[f])}</h2>")
        for lv in ("std", "adv"):
            d = load(f"{f}_{lv}", "v2", "s1"); items = d["result"]["items"]
            H.append(f"<h3>{LV[lv]}</h3>")
            for i, it in enumerate(items, 1): H.append(item_html(it, i, len(items)))
            dl = load(f"{f}_{lv}", "v2", "l1")
            H.append(f"<details><summary>参考: 同じ条件を本番で使っているモデル(gpt-6-luna)で生成した場合({LV[lv]})</summary><p class=sec>量産の費用を抑えられるモデルでの生成結果です。上の候補との品質差を見るための参考です。</p>" + "".join(item_html(it, i, len(dl['result']['items'])) for i, it in enumerate(dl["result"]["items"], 1)) + "</details>")
            H.append(f"<details><summary>参考: 現行のニュアンス解説({LV[lv]})</summary>{nuance_html(f, lv)}</details>")
    H.append("<p class=sec>Trial ID: ONE-STEP-FURTHER-CORNER-TRIAL-01 / 生成物・費用ログ: docs/research/ONE-STEP-FURTHER-CORNER-TRIAL-01/</p></body></html>")
    open(os.path.join(DEST, "index.html"), "w", encoding="utf-8", newline="\n").write("\n".join(H))
def page_dev():
    u = [json.loads(l) for l in open(g.USAGE, encoding="utf-8")]
    aud = []
    for f in "yxz":
        a = json.load(open(os.path.join(g.OUT, f"{f}__AUDIT.json"), encoding="utf-8")); r = json.loads(a["raw"][a["raw"].index("{"):a["raw"].rindex("}") + 1])
        for k, v in r["scores"].items(): aud.append((f, k, a["map"][k], v))
    H = [f"<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>One Step Further Trial 開発ログ・内部評価</title><style>{CSS}</style></head><body>",
         "<h1>開発ログ・内部評価(学習コンテンツ本体ではありません)</h1><p><a href='index.html'>← 比較ページ(学習コンテンツ)へ</a></p>"]
    H.append("<h2>1. 独立監査の集計(gpt-6.1-sol・匿名・順序シャッフル、1〜5点)</h2><table><tr><th>条件</th><th>n</th><th>学習価値</th><th>正確性</th><th>日本語</th><th>関連性</th><th>レベル適合</th><th>捏造</th><th>KP重複</th><th>既知で新味薄</th></tr>")
    ag = collections.defaultdict(list)
    for f, k, m, v in aud: ag[m["src"].rsplit("/", 1)[0] if not m["src"].startswith("nuance") else m["src"]].append(v)
    names = {"v1/s1": "v1 sol", "v1/l1": "v1 luna", "v2/s1": "v2 sol(主候補)", "v2/l1": "v2 luna(1回目)", "v2/l2": "v2 luna(2回目)", "nuance:現行Production採用文": "現行ニュアンス解説(Y採用文)", "nuance:ニュアンス改善Trial v3": "ニュアンス改善Trial v3(X/Z)"}
    for k in ("v2/s1", "v1/s1", "v2/l1", "v2/l2", "v1/l1", "nuance:現行Production採用文", "nuance:ニュアンス改善Trial v3"):
        l = ag[k]; n = len(l); av = lambda m: round(sum(x[m] for x in l) / n, 2)
        H.append(f"<tr><td>{E(names[k])}</td><td>{n}</td><td>{av('learning_value')}</td><td>{av('accuracy')}</td><td>{av('naturalness_ja')}</td><td>{av('relevance')}</td><td>{av('level_fit')}</td><td>{sum(x['fabrication'] for x in l)}</td><td>{sum(x['kp_overlap'] for x in l)}</td><td>{sum(x['known_to_most'] for x in l)}</td></tr>")
    H.append("</table><p class=sec>監査者はsol。sol生成物をsolが採点するため自己評価の甘さが入りうる(luna生成物も同じ基準で採点されている)。最終判断はユーザー・Fable。</p>")
    H.append("<h2>2. 全案の個別スコア</h2><table><tr><th>記事</th><th>ID</th><th>由来</th><th>核の表現</th><th>学習</th><th>正確</th><th>日本語</th><th>関連</th><th>Lv適合</th><th>指摘</th></tr>")
    for f, k, m, v in aud: H.append(f"<tr><td>{f}</td><td>{k}</td><td>{E(m['src'])}</td><td>{E(m['core'])}</td><td>{v['learning_value']}</td><td>{v['accuracy']}</td><td>{v['naturalness_ja']}</td><td>{v['relevance']}</td><td>{v['level_fit']}</td><td>{E(' / '.join(v.get('issues') or []))}</td></tr>")
    H.append("</table>")
    H.append("<h2>3. 再現性(同条件の生成ごとの選定表現)</h2><table><tr><th>セル</th><th>v1 sol</th><th>v1 luna1</th><th>v1 luna2</th><th>v2 sol</th><th>v2 luna1</th><th>v2 luna2</th></tr>")
    for f in "yxz":
        for lv in ("std", "adv"):
            row = "".join("<td>" + E(" / ".join(i["core_expression"] for i in load(f"{f}_{lv}", v, t)["result"]["items"])) + "</td>" for v, t in [("v1", "s1"), ("v1", "l1"), ("v1", "l2"), ("v2", "s1"), ("v2", "l1"), ("v2", "l2")])
            H.append(f"<tr><td>{f}_{lv}</td>{row}</tr>")
    H.append("</table><h2>4. 費用・時間(1セル=1記事×1レベルの生成1回)</h2><table><tr><th>条件</th><th>1セル平均費用</th><th>1記事セット(2レベル)</th><th>平均秒</th><th>入力tok</th><th>出力tok</th></tr>")
    for v, t, nm in (("v1", "s1", "v1 sol"), ("v1", "l1", "v1 luna1"), ("v1", "l2", "v1 luna2"), ("v2", "s1", "v2 sol"), ("v2", "l1", "v2 luna1"), ("v2", "l2", "v2 luna2")):
        x = [a for a in u if a["tag"].endswith(f"__{v}__{t}")]; c = sum(a["cost_jpy"] for a in x) / len(x)
        H.append(f"<tr><td>{nm}</td><td>¥{c:.3f}</td><td>¥{2*c:.2f}</td><td>{sum(a['elapsed_sec'] for a in x)/len(x):.1f}</td><td>{sum(a['usage']['input_tokens'] for a in x)//len(x)}</td><td>{sum(a['usage']['output_tokens'] for a in x)//len(x)}</td></tr>")
    ax = [a for a in u if "AUDIT" in a["tag"]]
    H.append(f"</table><p>独立監査 {len(ax)}回 ¥{sum(a['cost_jpy'] for a in ax):.2f}。Trial総費用 ¥{sum(a['cost_jpy'] for a in u):.2f}(呼出{len(u)}回)。</p></body></html>")
    open(os.path.join(DEST, "dev_log.html"), "w", encoding="utf-8", newline="\n").write("\n".join(H))
page_index(); page_dev(); print("written", DEST)

# OSF02(委任_02で更新) 比較ページ生成(osf01_page.pyのhead部を流用)(DEV/Trial専用)。index.html=学習コンテンツ本体(主候補=gpt-6.1-sol v2)+参考(本番ライン luna v2/現行ニュアンス)。dev_log.html=開発ログ・内部評価(分離)。
import sys, os, json, html, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import osf02_gen as g2
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

DEST = os.path.join(g.ROOT, "user_test", "one_step_further_trial_01")
def L2(n): return json.load(open(os.path.join(g.OUT, n + ".json"), encoding="utf-8"))
def primary(cell):
    """主候補(各セル)。委任_01のsol v2を基本に、Y Advは再生成(自然な例文)、X Adv/Z Stdは学習ポイント修正版へ差替え。"""
    items = L2(f"{cell}__v2__s1")["result"]["items"]
    if cell == "y_adv": return [L2("y_adv__v2__s2")["result"]["items"][0]]
    if cell in ("x_adv", "z_std"):
        fx = L2(f"{cell}__pointfix__s1")["after"]; key = fx["core_expression"]
        return [fx if key in i["core_expression"] else i for i in items]
    return items
def audit_rows():
    a = L2("osf02__AUDIT"); r = json.loads(a["raw"][a["raw"].index("{"):a["raw"].rindex("}") + 1]); return a, [(a["map"][k], v) for k, v in r["scores"].items()]
def page_index():
    H = [f"<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>One Step Further 品質検証Trial 比較ページ(委任_02更新)</title><style>{CSS}</style></head><body>",
         "<h1>One Step Further｜もう一歩進んだ英語表現(新コーナー案) 品質検証Trial</h1>",
         "<div class=note><b>これはTrialの試作です。正式採用ではありません。</b>採用するか、どのモデルで作るか、表示位置・分量をどうするかは、読んだうえでユーザーが判断します。既存の本文・音声・Key Phrase・文法解説は変更していません。<br>各記事のStandard／Advancedごとに、記事の話題から着想した表現を1〜2件ずつ載せています(主候補)。評価の内部データ・開発ログは別ページ(<a href='dev_log.html'>開発ログ・内部評価</a>)に分けています。</div>",
         "<div class=note><b>現行の「ニュアンス解説」は廃止が決定済み</b>です。各ケースに併置している現行ニュアンス解説は、<b>廃止決定(比較参考)</b>であり、採否の対象ではありません。新コーナーの内容を、これまでの解説と比べて学習価値が違うかを見るためだけに残しています。</div>",
         "<p class=sec>見方: 灰色=基本の表現(平易な言い方)、緑=One Step Further(もう一歩進んだ表現)。基本と発展が同義でない場合は「基本表現との違い」を明記しています。基本・発展の英文は、学習者が自分の状況で使える一般的な文で、記事の出来事そのものではありません。主候補は gpt-6.1-sol(最新上位モデル)で生成。折りたたみ内は、現行の本番ラインのモデル gpt-6-luna(Standardの難度規則を追加した版v3)での生成結果です。</p>",
         "<ul>" + "".join(f"<li><a href='#{f}'>{E(ARTICLE[f])}</a></li>" for f in "yxz") + "</ul>"]
    for f in "yxz":
        H.append(f"<h2 id='{f}'>{E(ARTICLE[f])}</h2>")
        for lv in ("std", "adv"):
            cell = f"{f}_{lv}"; items = primary(cell)
            H.append(f"<h3>{LV[lv]}(主候補: gpt-6.1-sol)</h3>")
            for i, it in enumerate(items, 1): H.append(item_html(it, i, len(items)))
            dl = L2(f"{cell}__v3__l1")["result"]["items"]
            H.append(f"<details><summary>参考: 本番ラインのモデル(gpt-6-luna、Standard難度規則つきv3)で生成した場合({LV[lv]})</summary><p class=sec>量産費用を抑えられるモデルでの生成結果です。主候補との品質差を見るための参考です(独立監査の結果は開発ログ参照)。</p>" + "".join(item_html(it, i, len(dl)) for i, it in enumerate(dl, 1)) + "</details>")
            if f == "y":
                c3 = L2(f"{cell}__c3__s1")["result"]["items"]
                H.append(f"<details><summary>参考: 同じ記事・レベルで「候補を3件出して選ぶ」方式(gpt-6.1-sol)の3候補({LV[lv]})</summary><p class=sec>Human Reviewで人が選ぶ方式の見本です。上位から順に並べています。</p>" + "".join(item_html(it, i, 3) for i, it in enumerate(c3, 1)) + "</details>")
            H.append(f"<details><summary>参考: 現行のニュアンス解説({LV[lv]}) ※廃止決定(比較参考)</summary><p class=sec>廃止が決定している機能です。新コーナーとの内容比較のためだけに残しています。</p>{nuance_html(f, lv)}</details>")
    H.append("<p class=sec>Trial ID: ONE-STEP-FURTHER-CORNER-TRIAL-01(委任_01・委任_02) / 生成物・費用ログ: docs/research/ONE-STEP-FURTHER-CORNER-TRIAL-01/out/</p></body></html>")
    open(os.path.join(DEST, "index.html"), "w", encoding="utf-8", newline="\n").write("\n".join(H))
def agg(rows, f):
    l = [v for m, v in rows if f(m)]; n = len(l)
    if not n: return None
    ms = ["learning_value", "accuracy", "example_natural", "naturalness_ja", "relevance", "level_fit"]
    return n, {m: round(sum(x[m] for x in l) / n, 2) for m in ms}, sum(1 for x in l if min(x["learning_value"], x["accuracy"], x["level_fit"]) <= 3), sum(x["fabrication"] for x in l), sum(x["kp_overlap"] for x in l)
def page_dev():
    P = os.path.join(g.ROOT, "docs/research/ONE-STEP-FURTHER-CORNER-TRIAL-01/out/dev_log_01_backup.html")   # 委任_01版(固定)に委任_02節を毎回付け直す(冪等)
    s = open(P, encoding="utf-8").read(); s = s[:s.rindex("</body>")]
    a, rows = audit_rows(); u = [json.loads(l) for l in open(g.USAGE, encoding="utf-8")]
    H = ["<!--OSF02-->", "<hr><h1 id='osf02'>委任_02 の生成・監査(上は委任_01の記録そのまま)</h1>"]
    H.append("<h2>A. 条件別の独立監査(gpt-6.1-sol・匿名・順序シャッフル、38案を1回で採点)</h2><table><tr><th>条件</th><th>n</th><th>学習価値</th><th>正確性</th><th>例文の自然さ</th><th>日本語</th><th>関連性</th><th>レベル適合</th><th>3点以下(学習/正確/Lv)</th><th>捏造</th><th>KP重複</th></tr>")
    for nm, fn in (("luna v3 全6セル", lambda m: m["src"].startswith("luna_v3")), ("luna v3 Standard", lambda m: m["src"].startswith("luna_v3") and m["cell"].endswith("std")), ("luna v3 Advanced", lambda m: m["src"].startswith("luna_v3") and m["cell"].endswith("adv")),
                   ("sol v2 主候補(委任_01)", lambda m: m["src"].startswith("sol_v2_primary(")), ("sol 3候補方式(Y)", lambda m: m["src"].startswith("sol_c3")), ("luna 3候補方式(Y、2回)", lambda m: m["src"].startswith("luna_c3")), ("sol v2 Y Adv再生成", lambda m: m["src"].startswith("sol_v2_regen")), ("学習ポイント修正版(X Adv/Z Std)", lambda m: "pointfix" in m["src"])):
        r = agg(rows, fn)
        if r:
            n, av, low, fab, kp = r; H.append(f"<tr><td>{E(nm)}</td><td>{n}</td><td>{av['learning_value']}</td><td>{av['accuracy']}</td><td>{av['example_natural']}</td><td>{av['naturalness_ja']}</td><td>{av['relevance']}</td><td>{av['level_fit']}</td><td>{low}</td><td>{fab}</td><td>{kp}</td></tr>")
    H.append("</table><p class=sec>監査者はsol(sol生成物は自己評価の甘さがありうる)。luna v2(委任_01)のStandardレベル適合は3.7で、v3で上がったかを見るのが主目的。nが小さいので傾向として読む。</p>")
    H.append("<h2>B. 全案の個別スコア(38案)</h2><table><tr><th>セル</th><th>由来</th><th>核の表現</th><th>学習</th><th>正確</th><th>例文自然</th><th>日本語</th><th>関連</th><th>Lv適合</th><th>KP重複</th><th>既知</th><th>指摘</th></tr>")
    for m, v in sorted(rows, key=lambda x: (x[0]["cell"], x[0]["src"])):
        H.append(f"<tr><td>{m['cell']}</td><td>{E(m['src'])}</td><td>{E(m['core'])}</td><td>{v['learning_value']}</td><td>{v['accuracy']}</td><td>{v['example_natural']}</td><td>{v['naturalness_ja']}</td><td>{v['relevance']}</td><td>{v['level_fit']}</td><td>{'○' if v['kp_overlap'] else ''}</td><td>{'○' if v['known_to_most'] else ''}</td><td>{E(' / '.join(v.get('issues') or []))}</td></tr>")
    H.append("</table>")
    old = L2("y_adv__v2__s1")["result"]["items"][0]; new = L2("y_adv__v2__s2")["result"]["items"]
    H.append("<h2>C. Y Advanced 例文の自然さ(差替え前後)</h2><p>差替え前(委任_01の主候補、sol v2 1回目): <b>" + E(old["further_en"]) + "</b> / " + E(old["further_ja"]) + "<br>再生成(sol v2、同一Prompt、2回目の生成): " + "".join(f"<br>・<b>{E(i['core_expression'])}</b>: {E(i['further_en'])} / {E(i['further_ja'])}" for i in new) + "<br>→ 再生成1件目(I'm sad, but I don't want to make this about me.)は監査で全項目5(例文自然さ5)。比較ページの主候補をこれに差し替えた。</p>")
    H.append("<h2>D. 学習ポイント文のみ再生成(X Adv / Z Std、各1回)</h2>")
    for c in ("x_adv", "z_std"):
        d = L2(f"{c}__pointfix__s1"); H.append(f"<h3>{c}: {E(d['after']['core_expression'])}</h3><p><b>修正前</b>: {E(d['before']['point_ja'])}<br><b>修正後</b>: {E(d['after']['point_ja'])}</p>")
    H.append("<h2>E. 表現固定の方式検証(Y、候補3件+選別)</h2><table><tr><th>セル</th><th>生成</th><th>rank1</th><th>rank2</th><th>rank3</th></tr>")
    for c in ("y_std", "y_adv"):
        for t, nm in (("s1", "sol 1回"), ("l1", "luna 1回目"), ("l2", "luna 2回目")):
            it = L2(f"{c}__c3__{t}")["result"]["items"]; H.append(f"<tr><td>{c}</td><td>{nm}</td>" + "".join(f"<td>{E(i['core_expression'])}<br><span class=sec>{E(i['further_en'])}<br>自己採点{E(str(i.get('self_scores')))}</span></td>" for i in it) + "</tr>")
    H.append("</table>")
    H.append("<h2>F. 費用・時間(委任_02、usage_log_02.jsonl)</h2><table><tr><th>呼出</th><th>費用</th><th>秒</th><th>入力tok</th><th>出力tok</th></tr>")
    for x in u: H.append(f"<tr><td>{E(x['tag'])}</td><td>¥{x['cost_jpy']:.3f}</td><td>{x['elapsed_sec']:.1f}</td><td>{x['usage']['input_tokens']}</td><td>{x['usage']['output_tokens']}</td></tr>")
    H.append(f"</table><p>委任_02の費用合計 ¥{sum(x['cost_jpy'] for x in u):.2f}(呼出{len(u)}回)。Trial累計(委任_01 ¥59.93 + 委任_02) = ¥{59.93 + sum(x['cost_jpy'] for x in u):.2f}。</p></body></html>")
    open(os.path.join(DEST, "dev_log.html"), "w", encoding="utf-8", newline="\n").write(s + "\n".join(H))
if __name__ == "__main__":
    page_index(); page_dev(); print("written", DEST)

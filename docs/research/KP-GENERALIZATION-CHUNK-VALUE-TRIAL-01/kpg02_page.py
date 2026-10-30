# -*- coding: utf-8 -*-
"""比較ページ生成: user_test/kp_generalization_trial_01/index.html(Trial専用・Production無関係)。"""
import glob, html, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kpg01_stats as S, kpg01_manual as M, kpg02_stats as S2, kpg02_manual as M2
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "user_test", "kp_generalization_trial_01", "index.html")
e = html.escape
TITLE = {"untidi_a2": "② 散らかり『出しっぱなし裁判』 / Standard", "untidi_b1b": "② 散らかり『出しっぱなし裁判』 / Advanced",
         "ai_cha_a2": "④ AI説得広告 / Standard", "ai_cha_b1b": "④ AI説得広告 / Advanced",
         "jwst_m_a2": "⑭ JWST謎の輝線 / Standard", "jwst_m_b1b": "⑭ JWST謎の輝線 / Advanced",
         "meta_w_a2": "⑨ Meta Waddle World / Standard", "meta_w_b1b": "⑨ Meta Waddle World / Advanced",
         "aiisland_b1b": "AI島(Family X) / Advanced", "surname_b1b": "夫が妻の姓を選ぶとき(Family Y) / Advanced", "melos_a2": "走れメロス(Family Z) / Standard",
         "ignobel_a2": "【未使用記事】イグ・ノーベル賞『ゴキブリミルク』(Family X形式) / Standard", "ignobel_b1b": "【未使用記事】イグ・ノーベル賞『ゴキブリミルク』 / Advanced",
         "tesla_b1b": "【未使用記事】Tesla×SpaceX合併協議 / Advanced"}
GL = {"REQ": "必須検証(Family X選定4記事)", "GEN": "汎化確認(既存別記事・Family X/Y/Z)", "UNUSED": "未使用記事(過学習チェック)"}
MN = {"Before": "Before: 現行Production(P7→canonicalization)", "A_luna": "After 方式A: 統合(1 call, gpt-6-luna)", "D_luna": "After 方式D: 工程分離", "D2_luna": "After 方式D': D+意味修飾語ガード+塊判定2回和集合+人称/受動規則(REQ 8ケースのみ実行)"}


def cell(r):
    ok = r["ok"]
    j = r.get("judge") or {}
    jt = ""
    if j:
        jt = f'<span class="jd">別系列判定: {"可" if j.get("selectable") else "不可"}({e(str(j.get("code")))})</span>'
    low = ' <span class="low">難易度低め</span>' if r.get("low") else ""
    reason = "" if ok else f'<div class="why">不可の理由: {e(r["reason"])}</div>'
    return (f'<li class="{"ok" if ok else "ng"}"><div class="d"><b>{e(r["disp"])}</b>{low}</div><div class="g">{e(r["gloss"] or "")}</div>'
            f'<div class="s">本文: {e(r["span"])}</div><div class="v">{"✔ そのまま選べる" if ok else "✘ 修正が必要/不可"} {jt}</div>{reason}</li>')


def main():
    css = """body{font-family:system-ui,"Yu Gothic",sans-serif;margin:0;padding:12px;max-width:1280px;background:#fafafa;color:#222;line-height:1.5}
h1{font-size:1.4rem}h2{font-size:1.15rem;margin-top:28px;border-bottom:2px solid #345;padding-bottom:4px}h3{font-size:1rem;margin:16px 0 4px}
table{border-collapse:collapse;width:100%;font-size:.88rem;background:#fff}th,td{border:1px solid #bbb;padding:4px 6px;vertical-align:top}th{background:#eef}
.cols{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}@media(max-width:900px){.cols{grid-template-columns:1fr}}
.col{background:#fff;border:1px solid #ccc;border-radius:6px;padding:6px}.col h4{margin:2px 0 6px;font-size:.9rem}
ul{list-style:none;padding:0;margin:0}li{border-left:5px solid #999;margin:4px 0;padding:3px 6px;background:#f6f6f6;font-size:.85rem}
li.ok{border-color:#2a8a3a}li.ng{border-color:#c33;background:#fff2f2}.g{color:#444}.s{color:#777;font-size:.78rem}.v{font-size:.78rem}.why{color:#b00;font-size:.8rem}
.jd{color:#555}.low{background:#fe9;font-size:.7rem;padding:0 4px;border-radius:3px}.note{background:#fff8e0;border:1px solid #ec9;padding:6px 10px;border-radius:6px;font-size:.88rem}
.ok-t{color:#1a7a2a;font-weight:bold}.ng-t{color:#c22;font-weight:bold}details{margin:8px 0}summary{cursor:pointer;font-weight:bold}code{background:#eee;padding:0 3px}"""
    h = [f'<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Key Phrase 一般化・塊価値 品質改善Trial 比較</title><style>{css}</style></head><body>']
    h.append("<h1>Key Phrase候補の一般化・塊としての学習価値 品質改善Trial(比較ページ)</h1>")
    h.append('<p class="note"><b>これはTrial(検証)の比較ページです。Production(本番)は変更していません。</b>結果が良好でも自動採用はされません(採用はユーザー判断)。管理ID=KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01 / OPEN-619。委任_02で方式D2列(改善ループ1回)を追加しました。</p>')
    # summary
    tot = {m: [0, 0] for m in MN}
    agg = {}
    ge3 = {m: [0, 0] for m in MN}
    rows_all = {}
    for cid in S.CASES:
        rs = S.rows(cid)
        d2 = S2.d2rows(cid) if cid in S2.CASES else None
        rs["D2_luna"] = d2["main"] if d2 else []
        rs["D2_alt"] = d2["alt"] if d2 else []
        rows_all[cid] = rs
        for m in MN:
            if m == "D2_luna": continue
            n = len(rs[m]); k = sum(1 for r in rs[m] if r["ok"])
            if n:
                tot[m][0] += k; tot[m][1] += n
                ge3[m][1] += 1; ge3[m][0] += 1 if k >= 3 else 0
                a = agg.setdefault((S.GROUP[cid], m), [0, 0]); a[0] += k; a[1] += n
    h.append("<h2>1. 結論(要約)</h2>")
    d, a, b = tot["D_luna"], tot["A_luna"], tot["Before"]
    h.append(f"<p>【方式A/D(委任_01、14ケース)】『提示された候補のうち、修正せずにそのまま選べる候補の割合』(Sonnet実読): 現行 {b[0]}/{b[1]}件({round(100*b[0]/b[1])}%) → 統合方式A {a[0]}/{a[1]}件({round(100*a[0]/a[1])}%) → 工程分離方式D {d[0]}/{d[1]}件({round(100*d[0]/d[1])}%)。</p>")
    # like-for-like REQ8
    lfl = {m: [0, 0, 0] for m in ("Before", "A_luna", "D_luna", "D2_luna")}
    lv = {}
    for cid in S2.CASES:
        for m in lfl:
            lst = rows_all[cid][m]; k = sum(1 for r in lst if r["ok"])
            lfl[m][0] += k; lfl[m][1] += len(lst); lfl[m][2] += 1 if k >= 3 else 0
            x = lv.setdefault((m, cid.split("_")[-1]), [0, 0]); x[0] += k; x[1] += len(lst)
    pct = lambda v: f"{v[0]}/{v[1]}({round(100*v[0]/v[1])}%)"
    h.append("<p><b>【委任_02: 方式D'との同一8ケース(必須検証の記事)での比較】</b></p><table><tr><th></th>" + "".join(f"<th>{e(MN[m].split(':')[0])}</th>" for m in lfl) + "</tr>")
    h.append("<tr><td>そのまま選べる/提示</td>" + "".join(f"<td>{pct(lfl[m])}</td>" for m in lfl) + "</tr>")
    h.append("<tr><td>Standard</td>" + "".join(f"<td>{pct(lv[(m,'a2')])}</td>" for m in lfl) + "</tr>")
    h.append("<tr><td>Advanced</td>" + "".join(f"<td>{pct(lv[(m,'b1b')])}</td>" for m in lfl) + "</tr>")
    h.append("<tr><td>3件以上選べるケース(8中)</td>" + "".join(f"<td>{lfl[m][2]}/8</td>" for m in lfl) + "</tr></table>")
    h.append("<p class='note'><b>委任_02の結果(正直な評価)</b>: 方式D'は必須9例のうちG1(1/2)・G2を取り込み、blow a whistleとsales pitchの脱落を解消した一方、そのまま選べる率はDより低下(64% vs 79%)。主因は塊判定(luna)が<b>易しい表現(rely on・turn something into)や自由な組合せ(deep image・need an instruction manual・early step toward)を2回とも『塊』と判定</b>すること(2回和集合で追加された候補の精度は通常候補と同等で、和集合自体は悪化原因ではない)。run間のばらつきも大きく、8ケース・約40件では率の差(64%/79%)は誤差の範囲を含みます。残り6ケース+moon・Z追加分は費用上限(¥20)に達したため未実行です。</p>")
    h.append('<p class="note">注意: ①記事ごとに「塊として価値のある表現」の供給が限られるため、品質を下げて7件を埋めていません。②Before列の一部記事(未使用記事)は現行方式の簡易再現のため参考値です。③判定は同一本文・同一基準でSonnetが実読判定した一次判定で、最終の独立受入はFableが行います。</p>')
    h.append("<table><tr><th>区分</th>" + "".join(f"<th>{e(MN[m])}</th>" for m in MN) + "</tr>")
    for g in ("REQ", "GEN", "UNUSED"):
        h.append(f"<tr><td>{e(GL[g])}</td>" + "".join(
            f"<td>{agg.get((g, m), [0, 0])[0]}/{agg.get((g, m), [0, 0])[1]}件</td>" if agg.get((g, m), [0, 0])[1] else "<td>-(再現不可)</td>" for m in MN) + "</tr>")
    h.append("</table>")
    # required 9
    h.append("<h2>2. 必須検証9例(ユーザー提示)の結果</h2><table><tr><th>#</th><th>種別</th><th>元の表現</th><th>望ましい方向</th><th>Before(現行)</th><th>方式A(統合)</th><th>方式D(工程分離)</th><th>方式D'(委任_02)</th></tr>")
    for r in M.REQUIRED:
        def c2(i):
            x = M2.REQUIRED2[i]
            return f'<td><span class="{"ok-t" if x[1] else "ng-t"}">{"○" if x[1] else "×"}</span> {e(x[0])}<br><small>{e(x[2])}</small></td>'

        def c(k):
            x = r[k]
            return f'<td><span class="{"ok-t" if x[1] else "ng-t"}">{"○" if x[1] else "×"}</span> {e(x[0])}<br><small>{e(x[2])}</small></td>'
        h.append(f"<tr><td>{r['id']}</td><td>{r['kind']}</td><td>{e(r['input'])}</td><td>{e(r['target'])}</td>{c('Before')}{c('A_luna')}{c('D_luna')}{c2(r['id'])}</tr>")
    h.append("</table>")
    h.append("<p>集計: 一般化5例のうちDは3例を達成(G3 at the time of・G4 narrow down・G5 turn something around)、G2は一般化単体では達成するが選定段でF(自由な組合せ)として不採用、G1(take points away from)は未達。学習価値4例は D が4/4、A は blow a whistle が脱落して3/4。</p>")
    # per case
    cur = None
    for cid in S.CASES:
        g = S.GROUP[cid]
        if g != cur:
            h.append(f"<h2>3. 記事別 Before / After — {e(GL[g])}</h2>")
            cur = g
        rs = rows_all[cid]
        h.append(f"<h3>{e(TITLE[cid])}</h3><div class='cols'>")
        for m in MN:
            lst = rs[m]
            k = sum(1 for r in lst if r["ok"])
            h.append(f"<div class='col'><h4>{e(MN[m])}<br>そのまま選べる {k}/{len(lst)}件</h4>")
            if not lst:
                h.append("<p><small>(" + ("委任_02では費用上限のため未実行" if m == "D2_luna" else "現行方式のBeforeを再現できなかったため比較なし。Production Gate連鎖の簡易再現でcanonicalizationが不合格") + ")</small></p>")
            else:
                h.append("<ul>" + "".join(cell(r) for r in lst) + "</ul>")
            h.append("</div>")
        h.append("</div>")
    # G1/G2 併記
    h.append("<h2>3b. G1/G2型(動詞+一般名詞目的語)の併記: 方針未決のため両方の出力を並べます(採否はユーザー判断材料)</h2>")
    h.append("<p>【方針F(現行どおり『自由な組合せ』として不採用)】= 委任_01の方式Dの出力: G1・G2とも提示されない。【方針G(『一般化すれば塊』として採用)】= 下表のD'出力。D'では塊判定の2回判定のうち1回でも『塊(C)』と判定されれば採用される設計のため、untidi_a2ではG1・G2がともに提示されました(再実行でどちらの判定になるかは不安定: 塊判定ログを併記)。</p><table><tr><th>記事</th><th>元の表現</th><th>塊判定2回(cls,難易度,keep,受動断片,一般化すれば塊)</th><th>方針F</th><th>方針G(D'の出力)</th></tr>")
    for cid in ("untidi_a2", "untidi_b1b"):
        r2 = S2.load(cid)
        for j in r2["log"]["judged"]:
            if any(k in j["span"] for k in ("take points away", "make life work")):
                outs = [i for i in r2["items"] + r2["alt_items"] if i["source_span"] == j["span"]]
                h.append(f"<tr><td>{e(TITLE[cid])}</td><td>{e(j['span'])}</td><td><small>{e(str(j['votes']))}</small></td><td>提示されない(F判定)</td><td>" + (", ".join(f"<b>{e(i['display_form'])}</b> ({e(i['gloss_ja'])})" for i in outs) or "-") + "</td></tr>")
    h.append("</table>")
    # residual
    h.append("<h2>4. 残ったNG(方式D / D')と原因</h2><ul>")
    for cid in S.CASES:
        for r in rows_all[cid]["D_luna"]:
            if not r["ok"]:
                h.append(f"<li class='ng'><b>{e(r['disp'])}</b>(本文: {e(r['span'])}) — {e(TITLE[cid])}: {e(r['reason'])}</li>")
    for cid in S2.CASES:
        for r in rows_all[cid]["D2_luna"] + rows_all[cid]["D2_alt"]:
            if not r["ok"]:
                h.append(f"<li class='ng'>[D'{' alt' if r['track']=='alt' else ''}] <b>{e(r['disp'])}</b>(本文: {e(r['span'])}) — {e(TITLE[cid])}: {e(r['reason'])}</li>")
    h.append("</ul>")
    # dev
    h.append("<details><summary>5. 開発・内部評価(費用・時間・探索した方式・別系列判定の信頼度)</summary>")
    res = {}
    for p in glob.glob(os.path.join(HERE, "kpg01_work", "results", "*.json")):
        r = json.load(open(p, encoding="utf-8"))
        res.setdefault(r["method"], []).append(r)
    h.append("<table><tr><th>方式</th><th>構成・モデル</th><th>実行ケース数</th><th>平均費用/ケース(円)</th><th>平均時間(秒)</th><th>備考</th></tr>")
    DESC = {"A_luna": ("統合1 call: 選定+塊判定+一般化 / gpt-6-luna", "最終Prompt版"), "D_luna": ("候補源=現行P7+過剰生成(luna)→選定(luna)→トークン分類一般化(luna)→別系列検証(gemini-3.8-flash)→決定論検査", "最終Prompt版(最終設計案)"),
            "B_luna": ("工程分離(抽出→塊判定→一般化→検証)全luna / 一般化は文章生成", "旧版Prompt。一般化の安定性が低く廃止"), "B_mix": ("B のうち塊判定・一般化を gpt-6.1-sol(low)", "旧版・1ケースのみ。費用が高い(3.7円)ため不採用"),
            "C1_luna": ("現行P7候補→塊判定→一般化→検証(luna)", "旧版。現行P7の候補源だけでは候補不足(1〜4件)"), "C1_mix": ("C1 の塊判定・一般化を sol", "旧版・1ケースのみ"),
            "C2_luna": ("現行P7候補→(塊判定+一般化を1 call)→検証(luna)", "旧版"), "C2_sol": ("C2 を gpt-6.1-sol(low)", "旧版・2ケース。費用2〜2.7円、結果はDと同等〜やや少数"),
            "C3_luna": ("現行P7候補+過剰生成→(塊判定+一般化1 call)→検証(luna)", "旧版"), "A_sol": ("統合1 call / gpt-6.1-sol(low)", "旧版・1ケース。厳しすぎて1件のみ提示"),
            "A2_sol": ("統合1 call+内部screening / gpt-6.1-sol(low)", "旧版・2ケース。2件ずつ(厳しすぎ)")}
    for m in ("A_luna", "D_luna", "B_luna", "C1_luna", "C2_luna", "C3_luna", "B_mix", "C1_mix", "C2_sol", "A_sol", "A2_sol"):
        rr = res.get(m, [])
        if not rr:
            continue
        h.append(f"<tr><td>{m}</td><td>{e(DESC[m][0])}</td><td>{len(rr)}</td><td>{round(sum(x['cost_jpy'] for x in rr)/len(rr),2)}</td><td>{round(sum(x['sec'] for x in rr)/len(rr))}</td><td>{e(DESC[m][1])}</td></tr>")
    h.append("</table>")
    h.append("<p>別系列判定(deepseek-flash、非thinking)とSonnet実読の一致率は約8割(判定が寛容で、ユーザー指定の一般化形『at the time of』を過一般化と判定する等の乖離あり)。判定は参考値で、主判定はSonnet実読(Fableが再読)。使用モデルと最新原則の適合は RESULT_01.md を参照。</p></details>")
    h.append("</body></html>")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write("\n".join(h))
    print("written", OUT, len("\n".join(h)))


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""比較ページ(D vs 改善版E、記事×レベル、混入率・成功率表)のテンプレート。
既定: kpg03_work/page_preview/index.html に出力(非公開)。--publish で user_test/kp_generalization_trial_02/index.html(公開は委任_02でFable確認後)。
--mock: mock結果で体裁確認(内容は無意味)。Trial専用。Production無関係。"""
import os, sys, html, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kpg03_stats as S
import kpg03_manual as MAN3
e = html.escape
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TITLE = {"untidi_a2": "② 散らかり / Standard", "untidi_b1b": "② 散らかり / Advanced", "ai_cha_a2": "④ AI説得広告 / Standard", "ai_cha_b1b": "④ AI説得広告 / Advanced",
         "jwst_m_a2": "⑭ JWST謎の輝線 / Standard", "jwst_m_b1b": "⑭ JWST謎の輝線 / Advanced", "meta_w_a2": "⑨ Meta Waddle World / Standard", "meta_w_b1b": "⑨ Meta Waddle World / Advanced",
         "aiisland_b1b": "AI島 / Advanced", "surname_b1b": "夫が妻の姓を選ぶとき(Y) / Advanced", "melos_a2": "走れメロス(Z) / Standard", "melos_b1b": "走れメロス(Z) / Advanced",
         "moon_a2": "月のしわ(X) / Standard", "moon_b1b": "月のしわ(X) / Advanced",
         "ignobel_a2": "【未使用】イグ・ノーベル賞 / Standard", "ignobel_b1b": "【未使用】イグ・ノーベル賞 / Advanced", "tesla_b1b": "【未使用】Tesla×SpaceX / Advanced"}
ARMNAME = {"D": "D: 前回(Before基準)", "E1L": "E1L: Dの順序+塊判定強化(luna)", "E1S": "E1S: 同(塊判定sol)", "E2": "E2: 一般化→塊判定(luna)",
           "E3": "E3: E2+別系列ゲート", "E4": "E4: E2(sol)+別系列ゲート"}
CSS = """body{font-family:system-ui,"Yu Gothic",sans-serif;margin:0;padding:12px;max-width:1400px;background:#fafafa;color:#222;line-height:1.5}
h1{font-size:1.4rem}h2{font-size:1.1rem;margin-top:26px;border-bottom:2px solid #345}table{border-collapse:collapse;width:100%;font-size:.85rem;background:#fff}
th,td{border:1px solid #bbb;padding:4px 6px;vertical-align:top}th{background:#eef}.cols{display:grid;gap:8px}.col{background:#fff;border:1px solid #ccc;border-radius:6px;padding:5px}
ul{list-style:none;padding:0;margin:0}li{border-left:5px solid #999;margin:3px 0;padding:2px 6px;background:#f6f6f6;font-size:.82rem}li.ok{border-color:#2a8a3a}li.ng{border-color:#c33;background:#fff2f2}
.s{color:#777;font-size:.74rem}.why{color:#b00;font-size:.75rem}.note{background:#fff8e0;border:1px solid #ec9;padding:6px 10px;border-radius:6px;font-size:.85rem}"""


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--mock", action="store_true"); ap.add_argument("--publish", action="store_true")
    ap.add_argument("--arms", default="D,E1L,E1S,E2,E3,E4"); ap.add_argument("--cases", default="ALL14")
    a = ap.parse_args()
    arms = a.arms.split(",")
    cases = S.ALL14 if a.cases == "ALL14" else a.cases.split(",")
    h = [f'<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>KP選定品質 追加Trial 比較</title><style>{CSS}</style></head><body>']
    h.append("<h1>Key Phrase選定・一般化 追加Trial(D vs 改善版) 比較ページ</h1>")
    h.append('<p class="note"><b>Trial(検証)です。Production(本番)は変更していません。採用はユーザー判断です。</b> 管理ID=KP-GENERALIZATION-CHUNK-VALUE-TRIAL-02。'
             + ('<b>【MOCKデータ=体裁確認用。内容は無意味】</b>' if a.mock else '') + '</p>')
    ss = {m: S.stats(m, cases, a.mock) for m in arms}
    h.append("<h2>1. 主評価(自由な組合せ混入率・一般化成功率・意味正確性・修正せず選べる率)</h2><table><tr><th>方式</th><th>ケース数</th><th>提示数</th><th>修正せず選べる</th><th>自由な組合せ混入</th><th>一般化成功(適用分)</th><th>意味・用法正確</th><th>3件以上(参考)</th><th>平均提示数(参考)</th><th>未判定</th></tr>")
    for m in arms:
        t, nc = ss[m]["t"], len(ss[m]["cases"])
        if not nc: continue
        h.append(f"<tr><td>{e(ARMNAME.get(m, m))}</td><td>{nc}</td><td>{t['n']}</td><td>{S.pct(t['ok'], t['n'])}</td><td>{S.pct(t['FREE'], t['n'])}</td><td>{S.pct(t['applied']-t['applied_gen_fail'], t['applied'])}</td>"
                 f"<td>{S.pct(t['n']-t['MEAN'], t['n'])}</td><td>{S.pct(t['ge3'], nc)}</td><td>{t['n']/nc:.1f}</td><td>{t['unj']}</td></tr>")
    h.append("</table><p class='s'>母集団差: 方式ごとに実行済みのケース集合が異なる場合があります(ケース数列)。厳密比較は共通ケースの集計(kpg03_stats.pyの出力)を参照。易しい表現(rely on等)は不可の理由にしていません。</p>")
    h.append("<h2>2. 記事×レベル別</h2>")
    for cid in cases:
        h.append(f"<h3>{e(TITLE.get(cid, cid))}</h3><div class='cols' style='grid-template-columns:repeat({len(arms)},1fr)'>")
        for m in arms:
            r = S.load_arm(m, cid, a.mock)
            h.append(f"<div class='col'><b>{e(ARMNAME.get(m, m))}</b><ul>")
            if r is None:
                h.append("<li>(未実行)</li>")
            else:
                for it in r["items"]:
                    code, judged = S.code_of(m, cid, it, a.mock)
                    cls = "ok" if code is None else "ng"
                    why = "" if code is None else f"<div class='why'>{e(code)}</div>"
                    ev = "" if S.norm_core(it["source_span"]) == S.norm_core(it["display_form"]) else f"<div class='s'>本文の根拠: {e(it['source_span'])}</div>"
                    h.append(f"<li class='{cls}'><b>{e(it['display_form'])}</b> <span class='s'>[{e(str(it.get('difficulty')))}]</span><div>{e(it.get('gloss_ja') or '')}</div>{ev}{why}</li>")
            h.append("</ul></div>")
        h.append("</div>")
    h.append("</body></html>")
    out = os.path.join(ROOT, "user_test", "kp_generalization_trial_02", "index.html") if a.publish else os.path.join(S.L.WORK, "page_preview", "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write("\n".join(h))
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()

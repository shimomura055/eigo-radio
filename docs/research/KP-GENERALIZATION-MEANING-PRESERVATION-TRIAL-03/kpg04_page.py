# -*- coding: utf-8 -*-
"""End User向け Before/After比較ページ(最終版)。記事別・Standard/Advanced別に 現行Production / D / E1L / E4 / 新N2 / 新N5 を横並び。
ラベルは kpg04_stats.label(Sonnet実読)。別系列AI(ds-v4-pro)が指摘した候補には注記。Trial専用(Production無変更)。
使い方: python kpg04_page.py [--publish]  (既定=kpg04_work/page_preview/index.html / --publish=user_test/kp_generalization_trial_03/index.html)"""
import os, sys, json, html, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kpg04_llm as L, kpg04_stats as S, kpg04_run as R, kpg04_manual as MAN, kpg04_eval as E
e = html.escape
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ARTICLE = {"untidi": "② 散らかり", "ai_cha": "④ AI説得広告", "jwst_m": "⑭ JWST謎の輝線", "meta_w": "⑨ Meta Waddle World", "aiisland": "AI島", "surname": "夫が妻の姓を選ぶとき(Y)",
           "melos": "走れメロス(Z)", "ignobel": "イグ・ノーベル賞", "tesla": "Tesla×SpaceX", "moon": "月のしわ"}
LEVEL = {"a2": "Standard", "b1b": "Advanced"}
ARMS = ["PROD", "D", "E1L", "E4", "N2", "N5"]
ARMNAME = {"PROD": "現行Production", "D": "D方式", "E1L": "E1L方式", "E4": "E4方式", "N2": "新方式A(N2: 意味優先の一般化+確認)", "N5": "新方式B(N5: A+全候補を別AIで再確認)"}
CSS = """body{font-family:system-ui,"Yu Gothic",sans-serif;margin:0;padding:12px;max-width:1700px;background:#fafafa;color:#222;line-height:1.5}
h1{font-size:1.4rem}h2{font-size:1.1rem;margin-top:26px;border-bottom:2px solid #345}h3{font-size:1rem}table.t{border-collapse:collapse;font-size:.85rem;background:#fff;margin:6px 0}
th,td{border:1px solid #bbb;padding:4px 7px;vertical-align:top}th{background:#eef}.cols{display:grid;gap:6px}.col{background:#fff;border:1px solid #ccc;border-radius:6px;padding:5px;min-width:0}
ul{list-style:none;padding:0;margin:0}li{border-left:6px solid #999;margin:4px 0;padding:3px 6px;background:#f6f6f6;font-size:.82rem;word-break:break-word}li.ok{border-color:#2a8a3a}li.ng{border-color:#c33;background:#fff2f2}li.bd{border-color:#d80;background:#fff8ec}
.mk{font-weight:bold;font-size:1rem}.ok .mk{color:#2a8a3a}.ng .mk{color:#c33}.bd .mk{color:#d80}.s{color:#666;font-size:.74rem}.why{color:#b00;font-size:.76rem}.rv{background:#def;border-radius:3px;padding:0 4px;font-size:.72rem}.ai{color:#06c;font-size:.74rem}
.note{background:#fff8e0;border:1px solid #ec9;padding:6px 10px;border-radius:6px;font-size:.88rem}.sum{background:#eef7ee;border:1px solid #9c9;padding:8px 12px;border-radius:6px}"""
SERIOUS = set(["SENSE_SHIFT", "ARG_TYPE", "FRAME_SHIFT", "MOD_SHIFT", "GLOSS_MISMATCH", "GLOSS_SENSE"])


def ds_map():
    p = os.path.join(E.EVAL_DIR, "all_items.json")
    d = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    return {(x["case"], S.nkey(x["span"]), S.nkey(x["display_form"]), (x["gloss"] or "").strip()): x for x in d.values()}


def mark(arm, cid, it):
    code, lv, rs = S.label(arm, cid, it)
    if not code:
        return "○", "ok", None
    if code in SERIOUS or code == "GLOSS_SENSE":
        k = "【意味・用法の誤り】" if lv == "strict" else "【意味・用法に疑義(境界)】" if lv == "boundary" else "【日本語訳が一般形と合わない(軽微)】"
        return ("×" if lv == "strict" else "△"), ("ng" if lv == "strict" else "bd"), f"{k}{MAN.LABEL_JA.get(code, code)}: {rs}"
    return "×", "ng", f"【候補として不適】{MAN.LABEL_JA.get(code, code)}: {rs}"


def col_html(arm, cid, corpus, ds):
    items = S.items_of(arm, cid)
    if items is None:
        return "<li>(未実行)</li>"
    out = []
    for it in items:
        mk, cls, why = mark(arm, cid, it)
        sp = it.get("source_span") or ""
        ev = "" if sp.lower() == (it.get("display_form") or "").lower() else f"<div class='s'>本文中の根拠表現: {e(sp)}</div>"
        rv = "<span class='rv'>戻し(本文の形に復元)</span> " if it.get("reverted") else ""
        x = ds.get((cid, S.nkey(sp), S.nkey(it.get("display_form") or ""), (it.get("gloss_ja") or "").strip()))
        vv = [v for v in (x or {}).get("verdicts", {}).values() if v != "OK"]
        aiq = f"<div class='ai'>別系列AIも指摘: {e(' / '.join((x or {}).get('reasons', {}).values()))}</div>" if vv else ""
        out.append(f"<li class='{cls}'><span class='mk'>{mk}</span> {rv}<b>{e(it.get('display_form') or '')}</b><div>{e(it.get('gloss_ja') or '')}</div>{ev}"
                   + (f"<div class='why'>{e(why)}</div>" if why else "") + aiq + "</li>")
    return "".join(out)


def metrics_table(cases, arms, title):
    ss = {a: S.summarize(a, cases) for a in arms}
    h = [f"<h3>{e(title)}</h3><table class='t'><tr><th>方式</th><th>提示件数</th><th>意味・用法の誤り(確定)</th><th>境界例</th><th>自由組合せ混入</th><th>そのまま選べる率</th><th>戻し</th><th>1記事セット費用(2レベル)</th></tr>"]
    for a in arms:
        s = ss[a]; n = s["n"]; sel = sum(1 for r in s["rows"] if not r["code"])
        c = f"¥{2 * sum(s['costs']) / len(s['costs']):.2f}" if s["costs"] else "-"
        h.append(f"<tr><td>{e(ARMNAME.get(a, a))}</td><td>{n}</td><td>{S.frac(len(s['s_strict']), n)}</td><td>{len(s['s_bound'])}</td><td>{S.frac(len(s['free']), n)}</td><td>{S.frac(sel, n)}</td><td>{S.frac(len(s['rev']), n)}</td><td>{c}</td></tr>")
    h.append("</table>")
    return "".join(h)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--publish", action="store_true"); a = ap.parse_args()
    corpus, ds = S.corpus(), ds_map()
    h = [f'<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Key Phrase一般化 意味保存 Before/After</title><style>{CSS}</style></head><body>',
         "<h1>Key Phrase候補の一般化: 本文と意味・用法が違う候補を出さなくなったか(Before/After)</h1>",
         '<p class="note"><b>Trial(検証)です。Productionは変更していません。採用はユーザー判断です。</b> ○=本文と同じ意味・用法の自然な表現としてそのまま選べる / △=意味・用法に疑義(境界)または日本語訳が軽微にずれる / ×=修正が必要、またはそのまま選ぶと誤った英語・意味を覚えるおそれ。'
         '「戻し」=一般化すると意味が変わるおそれがあるため、本文の形に戻した候補。「本文中の根拠表現」は記事に出てくる形です(例: hear it out)。評価はAI(Sonnet)が本文と照合して実読したものに、別系列AIの独立評価(ds-v4-pro)を併記しています(別系列AIの指摘は参考情報で、最終ラベルは実読)。</p>']
    st = open(os.path.join(L.WORK, "stats_summary.html"), encoding="utf-8").read() if os.path.exists(os.path.join(L.WORK, "stats_summary.html")) else ""
    h.append(st)
    h.append(metrics_table(R.ALL14, ["PROD", "D", "E1L", "E4", "N1", "N2", "N4", "N5"], "指標: 14記事レベル(開発に使った記事)"))
    h.append(metrics_table(R.HELDOUT, ["E1L", "N2", "N4", "N5"], "指標: 未見6記事レベル(方式を固定してから1回だけ実行)"))
    for title, cases in (("記事別比較(開発に使った14記事レベル)", R.ALL14), ("記事別比較(未見6記事レベル)", R.HELDOUT)):
        h.append(f"<h2>{title}</h2>")
        for cid in cases:
            art, lv = cid.rsplit("_", 1)
            h.append(f"<h3>{e(ARTICLE.get(art, art))} / {LEVEL.get(lv, lv)}</h3><div class='cols' style='grid-template-columns:repeat({len(ARMS)},1fr)'>")
            for arm in ARMS:
                if arm in ("PROD", "D", "E4") and cid in R.HELDOUT:
                    h.append(f"<div class='col'><b>{e(ARMNAME[arm])}</b><ul><li>(未見記事のため未実行)</li></ul></div>"); continue
                h.append(f"<div class='col'><b>{e(ARMNAME[arm])}</b><ul>{col_html(arm, cid, corpus, ds)}</ul></div>")
            h.append("</div>")
    h.append("</body></html>")
    out = os.path.join(ROOT, "user_test", "kp_generalization_trial_03", "index.html") if a.publish else os.path.join(L.WORK, "page_preview", "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write("\n".join(h))
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()

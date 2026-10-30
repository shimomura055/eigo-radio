# -*- coding: utf-8 -*-
"""End User向け Before/After比較ページ(記事別・Standard/Advanced別)。現行Production / D / E1L / E4 / 今回の改善方式 を横並び。
候補ごとに 英語表現 / 日本語意味 / 本文中の根拠表現 / 評価(○/×) / ×の具体的理由 を表示。技術ログ不要で採用判断できる形。
データ: Production=corpus.jsonのbefore(保存済み候補doc)、D/E1L/E4=kpg03_work/results、新方式=kpg04_work/results。評価=kpg04_manual.MAN(Sonnet実読)。
既定=kpg04_work/page_preview/index.html(非公開)。--publishは委任_02以降でFable確認後(user_test/kp_meaning_preservation_trial_03/)。--mock=体裁確認(内容は無意味)。Trial専用。"""
import os, sys, json, html, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kpg04_llm as L
import kpg04_manual as MAN
e = html.escape
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OLD1 = os.path.join(HERE, "..", "KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01")
OLD2 = os.path.join(HERE, "..", "KP-GENERALIZATION-CHUNK-VALUE-TRIAL-02")
ARTICLE = {"untidi": "② 散らかり", "ai_cha": "④ AI説得広告", "jwst_m": "⑭ JWST謎の輝線", "meta_w": "⑨ Meta Waddle World", "aiisland": "AI島", "surname": "夫が妻の姓を選ぶとき(Y)",
           "melos": "走れメロス(Z)", "ignobel": "イグ・ノーベル賞", "tesla": "Tesla×SpaceX", "moon": "月のしわ"}
LEVEL = {"a2": "Standard", "b1b": "Advanced"}
ARMNAME = {"PROD": "現行Production", "D": "D方式", "E1L": "E1L方式", "E4": "E4方式", "N1": "新N1", "N2": "新N2", "N4": "新N4", "N1a": "新N1a", "N5": "新N5"}
CSS = """body{font-family:system-ui,"Yu Gothic",sans-serif;margin:0;padding:12px;max-width:1500px;background:#fafafa;color:#222;line-height:1.5}
h1{font-size:1.4rem}h2{font-size:1.15rem;margin-top:30px;border-bottom:2px solid #345}table.t{border-collapse:collapse;width:100%;font-size:.85rem;background:#fff}
th,td{border:1px solid #bbb;padding:4px 6px;vertical-align:top}th{background:#eef}.cols{display:grid;gap:8px}.col{background:#fff;border:1px solid #ccc;border-radius:6px;padding:5px}
ul{list-style:none;padding:0;margin:0}li{border-left:6px solid #999;margin:4px 0;padding:3px 6px;background:#f6f6f6;font-size:.84rem}li.ok{border-color:#2a8a3a}li.ng{border-color:#c33;background:#fff2f2}
.mk{font-weight:bold;font-size:1rem}.ok .mk{color:#2a8a3a}.ng .mk{color:#c33}.s{color:#666;font-size:.76rem}.why{color:#b00;font-size:.78rem}.note{background:#fff8e0;border:1px solid #ec9;padding:6px 10px;border-radius:6px;font-size:.88rem}"""


def load_prod(corpus, cid):
    b = (corpus[cid].get("before") or {}).get("candidates") or []
    return [dict(display_form=c.get("used_form") or c.get("selection_phrase"), gloss_ja=c.get("gloss"), source_span=c.get("selection_phrase"))
            for c in b if c.get("kind") == "phrase"]


def load_arm(arm, cid, mock):
    new = arm.startswith("N")
    for base in ([os.path.join(L.WORK, "mock_results")] if (mock and new) else [os.path.join(L.WORK, "results")] if new else [os.path.join(OLD2, "kpg03_work", "results")]):
        p = os.path.join(base, f"{cid}__{arm}.json")
        if os.path.exists(p):
            return json.load(open(p, encoding="utf-8"))["items"]
    return None


def legacy_verdict(arm, cid, it):
    """TRIAL-02のSonnet実読ラベル(kpg03_manual/kpg01_manual)を、新定義(2軸)のコードへ読み替えて表示する(D/E1L/E4のBefore用。API 0)。"""
    sys.path.insert(0, OLD2); sys.path.insert(0, OLD1)
    import kpg03_stats as S3
    code, judged = S3.code_of(arm, cid, it, False)
    if not judged:
        return "－", None, False
    d = it["display_form"]
    if d == "hear something out":
        return "×", f"{MAN.LABEL_JA['ARG_TYPE']}: hear ... outの標準は人を取る(hear someone out)。本文のitは擬人化されたサプリ", True
    if d == "take away from":
        return "×", f"{MAN.LABEL_JA['SENSE_SHIFT']}: 本文は『減点する』、一般形は『損なう』という別の見出し", True
    if d in ("take a turn", "set a limit"):
        return "○", None, True        # 原文§2-C: 意味を損なわない修飾語除去は許容
    if not code:
        return "○", None, True
    new = {"FREE": "FREE", "GEN": "UNDER_GEN", "NAT": "NAT", "MEAN": "OTHER"}.get(code, "OTHER")
    if "can't help think" in d:
        new = "NAT"
    return "×", f"{MAN.LABEL_JA[new]}(TRIAL-02の実読判定)", True


def verdict(arm, cid, it):
    """returns (記号, 理由|None, 判定済みか)"""
    if arm in ("D", "E1L", "E4") and (arm, cid) not in MAN.JUDGED:
        return legacy_verdict(arm, cid, it)
    if (arm, cid) not in MAN.JUDGED:
        return "－", None, False
    rec = MAN.MAN.get(arm, {}).get(cid, {}).get(it["display_form"])
    if not rec:
        return "○", None, True
    return "×", f"{MAN.LABEL_JA.get(rec[0], rec[0])}: {rec[1]}", True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true"); ap.add_argument("--publish", action="store_true")
    ap.add_argument("--new", default="N4", help="今回の改善方式(複数可: N2,N4)"); ap.add_argument("--cases", default="untidi_a2,untidi_b1b")
    a = ap.parse_args()
    arms = ["PROD", "D", "E1L", "E4"] + [x for x in a.new.split(",") if x]
    corpus = {c["id"]: c for c in json.load(open(os.path.join(OLD1, "kpg01_work", "corpus.json"), encoding="utf-8"))}
    h = [f'<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Key Phrase一般化 Before/After</title><style>{CSS}</style></head><body>',
         "<h1>Key Phrase候補の一般化: 現行 / D / E1L / E4 / 今回の改善方式 の比較</h1>",
         '<p class="note"><b>Trial(検証)です。Productionは変更していません。採用はユーザー判断です。</b> '
         "各候補の ○=本文と同じ意味・用法の自然な表現として、そのまま選べる / ×=修正が必要、またはそのまま選ぶと誤った英語・意味を覚えるおそれ。"
         "『本文中の根拠表現』は記事に実際に出てくる形です(例: hear it out)。学習用の表示形(例: hear someone out)との違いは意図した一般化で、意味・用法が本文と合っているかを評価しています。"
         + ("<b>【MOCKデータ=体裁確認用。内容は無意味】</b>" if a.mock else "") + "</p>"]
    for cid in a.cases.split(","):
        art, lv = cid.rsplit("_", 1)
        h.append(f"<h2>{e(ARTICLE.get(art, art))} / {LEVEL.get(lv, lv)}</h2><div class='cols' style='grid-template-columns:repeat({len(arms)},1fr)'>")
        for arm in arms:
            items = load_prod(corpus, cid) if arm == "PROD" else load_arm(arm, cid, a.mock)
            h.append(f"<div class='col'><b>{e(ARMNAME.get(arm, arm))}</b><ul>")
            if items is None:
                h.append("<li>(未実行)</li>")
            for it in (items or []):
                mk, why, judged = verdict(arm, cid, it)
                cls = "ok" if mk == "○" else ("ng" if mk == "×" else "")
                ev = "" if (it.get("source_span") or "").lower() == (it.get("display_form") or "").lower() else f"<div class='s'>本文中の根拠表現: {e(it.get('source_span') or '')}</div>"
                h.append(f"<li class='{cls}'><span class='mk'>{mk}</span> <b>{e(it.get('display_form') or '')}</b><div>{e(it.get('gloss_ja') or '')}</div>{ev}"
                         + (f"<div class='why'>理由: {e(why)}</div>" if why else "") + "</li>")
            h.append("</ul></div>")
        h.append("</div>")
    h.append("</body></html>")
    out = os.path.join(ROOT, "user_test", "kp_meaning_preservation_trial_03", "index.html") if a.publish else os.path.join(L.WORK, "page_preview", "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write("\n".join(h))
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()

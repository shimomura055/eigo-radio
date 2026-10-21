# -*- coding: utf-8 -*-
"""FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01 委任_06: 最終試聴ページ(正式完成候補・ユーザー試聴待ち)生成(有料APIなし)。
er019_pp_page_01.py の level_block/seg_html を流用し、開発者向け情報(Style sha等)を除いたユーザー向けUI(Standard/Advanced切替)にする。
入力はProduction runner --stage assemble の正式出力のみ。出力: user_test/paycheck_personality_e2e_01/{index.html, audio/*.mp3}"""
from __future__ import annotations
import argparse, os, re
import er019_pp_page_01 as pp

esc = pp.esc
NOSCRIPT = {"intro": "オープニング(効果音・導入)", "welcome": "ウェルカム(定型)", "notification": "通知音(効果音)", "outro": "エンディング(定型)",
            "key phrases intro": "Key Phrasesの導入(定型)", "full story intro": "Full Storyの導入(定型)", "preview intro": "Previewの導入(定型)"}


def clean(h, part):
    h = re.sub(r"<div class='sec'>.*?</div>", "", h, flags=re.S)
    if h:
        return h
    return "<span class='sec'>" + esc(NOSCRIPT.get(part.lower().split(" (")[0].rstrip("0123456789 ").strip(), "(定型音声・効果音)")) + "</span>"


def rows_html(rows):
    return ("<table><thead><tr><th>パート</th><th>音声</th><th>Script / Key Phrase</th></tr></thead><tbody>"
            + "".join(f"<tr><td><b>{esc(p)}</b><br><span class='sec'>{s:.1f}秒〜 ({d:.1f}秒)</span></td><td class='play'>"
                      f"<audio controls preload='none' src='audio/{fn}'></audio></td><td>{clean(b, p)}</td></tr>" for p, s, d, fn, b in rows)
            + "</tbody></table>")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--audio-dir", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
    pp.RUN = os.path.abspath(a.audio_dir); pp.WEB = os.path.abspath(a.out); pp.AUD = os.path.join(pp.WEB, "audio")
    os.makedirs(pp.AUD, exist_ok=True)
    adv = pp.level_block("adv", "b1b", "Advanced", "Family_X_Audio_B1_PAYCHECK_PERSONALITY.wav")
    std = pp.level_block("std", "a2", "Standard", "Family_X_Audio_A2_PAYCHECK_PERSONALITY.wav")
    pa = pp.rj(os.path.join(pp.RUN, "a2", "parts.json")); pb = pp.rj(os.path.join(pp.RUN, "b1b", "parts.json"))

    def sect(sid, lab, full, dur, rows, iol, extra=""):
        return (f"<section id='{sid}' class='lv'><h2>{lab}(通し再生 約{dur / 60:.1f}分 / {dur:.0f}秒)</h2>{extra}"
                f"<div class='combo'><b>通し再生</b><audio id='main_{sid}' controls preload='none' src='audio/{full}'></audio></div>"
                f"<div class='note'><b>In One Line</b>: {esc(iol)}</div>"
                "<details open><summary>パート別再生・全スクリプト・Key Phrase(英語と意味/解説)</summary>" + rows_html(rows) + "</details></section>")

    std_extra = ("<div class='note2'>第2部(Full Story Part 2)は、ユーザー承認済みの別Take(落ち着いた自然な調子)を使用しています。"
                 "第1・第3部と声の調子が少し違って聞こえるかを確認してください。</div>")
    pw = []
    for lvl, lab in (("a2", "Standard"), ("b1b", "Advanced")):
        pth = os.path.join(pp.RUN, lvl, "audit", "pass_with_warning_listening_list.json")
        lst = pp.rj(pth) if os.path.exists(pth) else {"count": 0, "entries": []}
        pw.append(f"<p>{lab}: {lst['count']}件" + ("" if not lst["count"] else " — " + " / ".join(esc(e["segment_id"]) + "(数字などの読み方の揺れ)" for e in lst["entries"])) + "</p>")
    css = ("<style>body{font-family:sans-serif;max-width:1100px;margin:1em auto;padding:0 1em;line-height:1.5}table{border-collapse:collapse;width:100%;margin:.5em 0 1.5em}"
           "th,td{border:1px solid #ccc;padding:6px;vertical-align:top;text-align:left}td.play{min-width:340px}audio{width:100%}.sec{color:#666;font-size:.85em}"
           ".script{background:#f6f6f6;padding:4px;margin:3px 0;font-size:.95em}.kp td,.kp th{border:1px solid #ccc;padding:4px 10px;width:50%}"
           ".combo{background:#eef6ff;padding:10px;border:1px solid #99c;margin-bottom:1em}.note{background:#fff8e0;padding:8px;border:1px solid #cb8;margin-bottom:1em}"
           ".note2{background:#eef9ee;padding:8px;border:1px solid #8b8;margin-bottom:1em}.tabs button{font-size:1.1em;padding:.5em 1.5em;margin-right:.5em;cursor:pointer}"
           ".tabs button.on{background:#336;color:#fff}.hidden{display:none}</style>")
    js = ("<script>function show(id){for(const s of ['std','adv']){document.getElementById(s).classList.toggle('hidden',s!==id);"
          "document.getElementById('tab_'+s).classList.toggle('on',s===id);}history.replaceState(null,'','#'+id);}"
          "show(location.hash==='#adv'?'adv':'std');</script>")
    pg = (f"<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><title>「給料が上がると、性格も変わる?」最終試聴(正式完成候補)</title>"
          f"<meta name='viewport' content='width=device-width, initial-scale=1'>{css}</head><body>"
          f"<h1>「給料が上がると、性格も変わる?」 最終試聴ページ</h1>"
          "<div class='note'><b>状態: 正式完成候補・ユーザー試聴待ち</b>(試聴PASSは未取得です)。Standard/Advancedとも、承認済みProduction仕様"
          "(効果音・無音間隔・音量正規化・Style・必須QA)で組み立てた最終音声です。上のボタンでレベルを切り替えられます。<br>"
          f"<b>タイトル</b>: {esc(pb.get('title') or '')}</div>"
          "<div class='tabs'><button id='tab_std' onclick=\"show('std')\">Standard</button><button id='tab_adv' onclick=\"show('adv')\">Advanced</button></div>"
          + sect("std", "Standard", std[0], std[1], std[2], pa["in_one_line"], std_extra)
          + sect("adv", "Advanced", adv[0], adv[1], adv[2], pb["in_one_line"])
          + "<details><summary>事後試聴の参考(読み方の揺れが検出された箇所、非ブロッキング)</summary>" + "".join(pw) + "</details>" + js + "</body></html>")
    assert "file:///" not in pg and "C:\\" not in pg and "C:/" not in pg
    with open(os.path.join(pp.WEB, "index.html"), "w", encoding="utf-8") as f:
        f.write(pg)
    print("page written", len(std[2]), len(adv[2]), round(std[1], 2), round(adv[1], 2))


if __name__ == "__main__":
    main()

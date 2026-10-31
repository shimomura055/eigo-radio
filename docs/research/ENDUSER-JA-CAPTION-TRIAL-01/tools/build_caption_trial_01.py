"""ENDUSER-JA-CAPTION-TRIAL-01: rev01-h assetをコピーしキャプション機能を追加したTrial asset/ページを生成する(API 0)。
rev01-h本体・既存公開dirは読むだけ。出力=user_test/enduser_caption_trial_01/。
使い方: py -3.12 build_caption_trial_01.py [--verify-tree DIR]  (verify-tree: er135検証用に enduser/ 構造の複製を作る)"""
import argparse, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / "enduser_page_assets" / "rev01-h"
OUT = ROOT / "user_test" / "enduser_caption_trial_01"
BUILD = "cap-trial-01"
PAGES = [("family_x_meta_waddle_world_01", "x"), ("family_y_production_surname_choice_01", "y"), ("family_z_melos_kphr_evidence_r3", "z")]
PAGE_HTML = '''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="build-id" content="%(build)s">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex">
<title>[Trial] English Your Way · 日本語キャプション</title>
<link rel="stylesheet" href="%(assets)sstyle.css?v=%(build)s">
</head>
<body data-build="%(build)s" data-src="%(src)s" data-lv="%(lv)s" data-prod="%(prod)s" class="capon">
%(body)s
<script src="%(assets)sapp.js?v=%(build)s"></script>
</body>
</html>
'''

CAP_JS = r'''
  /* ===== cap-trial-01: 点灯中の日本語1文をプレイヤー直下に小さく表示(補助表示のみ。再生・点灯ロジックは無変更) ===== */
  var capText = null;
  function capUpdate() {   // activeG(点灯中の日本語群)の本文だけを表示。群なし/null/日本語なしは空(誤表示しない)
    var el = $('jcapT'); if (!el) return;
    var t = (activeG && jgEls[activeG]) ? jgEls[activeG].map(function (e) { return e.textContent; }).join('') : '';
    if (t === capText) return;
    capText = t; el.textContent = t; $('jcap').classList.toggle('empty', !t); $('jcap').scrollTop = 0;
  }
  function capSetOn(on, keepUrl) {
    document.body.classList.toggle('capon', on); document.body.classList.toggle('capoff', !on);
    var b = $('capToggle'); if (b) { b.textContent = 'キャプション: ' + (on ? 'ON' : 'OFF'); b.setAttribute('aria-pressed', on ? 'true' : 'false'); }
    if (!keepUrl) { var u = new URL(location.href); u.searchParams.set('caption', on ? '1' : '0'); history.replaceState(null, '', u); }
  }
  (function capInit() {
    var row2 = document.querySelector('.row2'), top = document.querySelector('.top');
    var c = document.createElement('div'); c.className = 'jcap empty'; c.id = 'jcap'; c.setAttribute('lang', 'ja');
    c.innerHTML = '<span class="jtag">日本語</span><span class="jt" id="jcapT"></span>';
    row2.parentNode.insertBefore(c, row2.nextSibling);
    var n = document.createElement('div'); n.className = 'trialbar';
    var prod = document.body.dataset.prod;
    n.innerHTML = '<b>Trial(未採用・比較用)</b> 再生中/選択中の日本語1文を、再生バー直下にキャプション表示します。 ' +
      '<button type="button" id="capToggle"></button>' + (prod ? ' <a id="prodLink" href="#">現行版(Production)を開く</a>' : '');
    top.parentNode.insertBefore(n, top);
    $('capToggle').addEventListener('click', function () { capSetOn(!document.body.classList.contains('capon')); });
    var pl = $('prodLink'); if (pl) pl.href = new URL(prod, location.href).href + '?lv=' + (document.body.dataset.lv || '');
    capSetOn(Q.get('caption') !== '0', true);
  })();
'''

CSS = '''
/* ===== cap-trial-01 ===== */
.trialbar{margin:0 0 10px;padding:8px 12px;border:1px dashed #f79009;background:#fffaeb;color:#7a2e0e;border-radius:10px;font-size:13px;line-height:1.6}
.trialbar button{font:inherit;font-size:12px;font-weight:700;border:1px solid #f79009;background:#fff;color:#7a2e0e;border-radius:999px;padding:3px 10px;cursor:pointer;margin:0 4px}
.trialbar a{color:#315efb;font-weight:700}
.jcap{display:none;margin-top:6px;padding:6px 10px;background:#fffdf0;border:1px solid #f0e2a0;border-radius:8px;font-size:14px;line-height:1.55;min-height:3.1em;max-height:5.4em;overflow-y:auto;-webkit-overflow-scrolling:touch;overflow-wrap:anywhere}
.jcap .jtag{display:inline-block;margin-right:6px;padding:0 6px;border-radius:4px;background:#f0e2a0;color:#5b4a00;font-size:11px;font-weight:700;vertical-align:1px}
.jcap.empty .jtag{visibility:hidden}
body.capon .jcap{display:block}
body.capon{--bar-h:176px}
@media(max-width:640px){.jcap{font-size:13.5px;padding:5px 8px}body.capon{--bar-h:168px}}
'''


def patch_js(js):
    def rep(a, b):
        nonlocal js
        assert js.count(a) == 1, (a, js.count(a))
        js = js.replace(a, b)
    rep("var A = $('aud'), Q = new URLSearchParams(location.search);",
        "var A = $('aud'), Q = new URLSearchParams(location.search);\n  var SRC = document.body.dataset.src || '', BASE = new URL(SRC || '.', location.href).href;   // cap-trial: 記事data/audioは既公開dirを参照")
    rep("new URL(art.audio_base + p, location.href).href", "new URL(art.audio_base + p, BASE).href")
    rep("new URL(au.file, location.href).href", "new URL(au.file, BASE).href")
    rep("fetchJson('data/sync_' + lv", "fetchJson(SRC + 'data/sync_' + lv")
    rep("fetchJson('data/article.json')", "fetchJson(SRC + 'data/article.json')")
    rep("var want = Q.get('lv');", "var want = Q.get('lv') || document.body.dataset.lv;")
    rep("  function gapGroup(g) {", CAP_JS + "  function gapGroup(g) {")
    rep("if (g && jgEls[g]) jgEls[g].forEach(function (e) { e.classList.add('on'); });\n  }",
        "if (g && jgEls[g]) jgEls[g].forEach(function (e) { e.classList.add('on'); });\n    capUpdate();\n  }")
    rep("g.sids.forEach(function (s) { sidToG[s] = p.idx + ':' + g.g; }); }); });\n  }",
        "g.sids.forEach(function (s) { sidToG[s] = p.idx + ':' + g.g; }); }); });\n    capText = null; capUpdate();\n  }")
    rep("var u = new URL(location.href); u.searchParams.set('lv', lv); history.replaceState(null, '', u);",
        "var u = new URL(location.href); u.searchParams.set('lv', lv); history.replaceState(null, '', u);\n    var pl = $('prodLink'); if (pl) pl.href = new URL(document.body.dataset.prod, location.href).href + '?lv=' + lv;")
    return js


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify-tree")
    a = ap.parse_args()
    assets = OUT / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    js = patch_js((SRC / "app.js").read_text(encoding="utf-8"))
    (assets / "app.js").write_text(js, encoding="utf-8", newline="\n")
    css = (SRC / "style.css").read_text(encoding="utf-8") + CSS
    (assets / "style.css").write_text(css, encoding="utf-8", newline="\n")
    html = (SRC / "index.html").read_text(encoding="utf-8")
    body = html.split("<body", 1)[1].split(">", 1)[1].split("<script", 1)[0].strip()
    for d, f in PAGES:
        for lv in ("std", "adv"):
            p = OUT / f"{f}_{lv}"
            p.mkdir(exist_ok=True)
            (p / "index.html").write_text(PAGE_HTML % dict(build=BUILD, assets="../assets/", src=f"../../{d}/enduser/", lv=lv, prod=f"../../{d}/enduser/", body=body), encoding="utf-8", newline="\n")
    idx = ['<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>日本語キャプションTrial</title>',
           '<body style="font-family:sans-serif;max-width:720px;margin:20px auto;padding:0 14px;line-height:1.9"><h1>日本語キャプション Trial(ENDUSER-JA-CAPTION-TRIAL-01)</h1>',
           '<p>未採用の比較用ページです。各ページ上部のボタンで同一ページ内でキャプションON/OFFを切替でき、現行版(Production)へのリンクもあります。(?caption=0 でOFF)</p><ul>']
    for d, f in PAGES:
        for lv, nm in (("std", "Standard"), ("adv", "Advanced")):
            idx.append(f'<li>{f.upper()} {d} {nm}: <a href="{f}_{lv}/index.html">Trial</a> / <a href="../{d}/enduser/index.html?lv={lv}">現行</a></li>')
    idx.append("</ul></body></html>")
    (OUT / "index.html").write_text("\n".join(idx), encoding="utf-8", newline="\n")
    if a.verify_tree:   # er135検証用: <tree>/<x_std>/enduser/ に既公開dirの複製 + Trial index/app/style(src='')を重ねる
        for d, f in PAGES:
            for lv in ("std", "adv"):
                t = Path(a.verify_tree) / f"{f}_{lv}"
                if t.exists():
                    shutil.rmtree(t)
                shutil.copytree(ROOT / "user_test" / d, t)
                e = t / "enduser"
                (e / "app.js").write_text(js, encoding="utf-8", newline="\n")
                (e / "style.css").write_text(css, encoding="utf-8", newline="\n")
                (e / "index.html").write_text(PAGE_HTML % dict(build=BUILD, assets="", src="", lv=lv, prod="../index.html", body=body), encoding="utf-8", newline="\n")
    print("built", OUT)


if __name__ == "__main__":
    main()

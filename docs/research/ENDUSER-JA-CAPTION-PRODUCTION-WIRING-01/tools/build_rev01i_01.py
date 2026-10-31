"""ENDUSER-JA-CAPTION-PRODUCTION-WIRING-01: production asset rev01-i を rev01-h から機械的に派生する(API 0)。
rev01-i = rev01-h + 日本語キャプション(ENDUSER-JA-CAPTION-TRIAL-01 cap-trial-01 の実装を移植) + 固定再生バー内のON/OFFボタン(既定ON、設定保持=URL ?caption=0|1。lv保持と同方式)。
Trial帯・noindex・現行版リンク・Trial用の記事data参照(SRC/BASE)は移植しない。各置換は出現1回をassertする。rev01-h本体は変更しない。
使い方: py -3.12 build_rev01i_01.py [--out DIR]   (既定=enduser_page_assets/rev01-i)"""
import argparse, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / "enduser_page_assets" / "rev01-h"
BUILD = "rev01-i"

CAP_JS = r'''
  /* ===== rev01-i: 点灯中の日本語1文を固定再生バー内に表示(補助表示のみ。再生・点灯ロジックは無変更)。ON/OFF切替・既定ON ===== */
  var capText = null;
  function capUpdate() {   // activeG(点灯中の日本語群)の本文だけを表示。群なし/null/日本語なしは空(誤表示しない)。OFF中も更新する(ONへ戻した時に現在の訳を即表示)
    var el = $('jcapT'); if (!el) return;
    var t = (activeG && jgEls[activeG]) ? jgEls[activeG].map(function (e) { return e.textContent; }).join('') : '';
    if (t === capText) return;
    capText = t; el.textContent = t; $('jcap').classList.toggle('empty', !t); $('jcap').scrollTop = 0;
  }
  function capSetOn(on, keepUrl) {   // 再生・位置・点灯には触れない。設定保持=URLの?caption=(レベル切替の?lv=と同方式。history.replaceState)
    document.body.classList.toggle('capon', on); document.body.classList.toggle('capoff', !on);
    var b = $('capToggle'); if (b) { b.textContent = '字幕 ' + (on ? 'ON' : 'OFF'); b.setAttribute('aria-pressed', on ? 'true' : 'false'); }
    if (!keepUrl) { try { var u = new URL(location.href); u.searchParams.set('caption', on ? '1' : '0'); history.replaceState(null, '', u); } catch (e) { } }
  }
  (function capInit() {
    var b = $('capToggle'); if (b) b.addEventListener('click', function () { capSetOn(!document.body.classList.contains('capon')); });
    capSetOn(Q.get('caption') !== '0', true);
  })();
'''

CSS = '''
/* ===== rev01-i: 日本語キャプション(Trial cap-trial-01の外観を移植) + ON/OFFボタン ===== */
.jcap{display:none;margin-top:6px;padding:6px 10px;background:#fffdf0;border:1px solid #f0e2a0;border-radius:8px;font-size:14px;line-height:1.55;min-height:3.1em;max-height:5.4em;overflow-y:auto;-webkit-overflow-scrolling:touch;overflow-wrap:anywhere}
.jcap .jtag{display:inline-block;margin-right:6px;padding:0 6px;border-radius:4px;background:#f0e2a0;color:#5b4a00;font-size:11px;font-weight:700;vertical-align:1px}
.jcap.empty .jtag{visibility:hidden}
body.capon .jcap{display:block}
body.capon{--bar-h:176px}
@media(max-width:640px){.jcap{font-size:13.5px;padding:5px 8px}body.capon{--bar-h:168px}}
.skips #capToggle{min-width:72px;min-height:40px;padding:0 10px}
.skips #capToggle[aria-pressed=true]{background:var(--soft);border-color:var(--accent);color:var(--accent)}
'''


def rep_once(s, a, b):
    assert s.count(a) == 1, (a[:60], s.count(a))
    return s.replace(a, b)


def patch_js(js):
    js = rep_once(js, "  function gapGroup(g) {", CAP_JS + "  function gapGroup(g) {")
    js = rep_once(js, "if (g && jgEls[g]) jgEls[g].forEach(function (e) { e.classList.add('on'); });\n  }",
                  "if (g && jgEls[g]) jgEls[g].forEach(function (e) { e.classList.add('on'); });\n    capUpdate();\n  }")
    js = rep_once(js, "g.sids.forEach(function (s) { sidToG[s] = p.idx + ':' + g.g; }); }); });\n  }",
                  "g.sids.forEach(function (s) { sidToG[s] = p.idx + ':' + g.g; }); }); });\n    capText = null; capUpdate();\n  }")
    return js


def patch_html(h):
    assert h.count("rev01-h") == 4, h.count("rev01-h")
    h = h.replace("rev01-h", BUILD)
    h = rep_once(h, '<body data-build="rev01-i">', '<body data-build="rev01-i" class="capon">')
    h = rep_once(h, '<span class="skips"><button type="button" id="back10"',
                 '<span class="skips"><button type="button" id="capToggle" aria-pressed="true" aria-label="日本語キャプション(字幕)の表示切替">字幕 ON</button><button type="button" id="back10"')
    h = rep_once(h, '10秒 ▶</button></span>\n  </div>\n',
                 '10秒 ▶</button></span>\n  </div>\n  <div class="jcap empty" id="jcap" lang="ja"><span class="jtag">日本語</span><span class="jt" id="jcapT"></span></div>\n')
    return h


def sha(b):
    return hashlib.sha256(b.replace(b"\r\n", b"\n")).hexdigest()


def build(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rd = lambda n: (SRC / n).read_text(encoding="utf-8")   # noqa: E731  (universal newline: CRLF->LF)
    res = {"app.js": patch_js(rd("app.js")), "style.css": rd("style.css").rstrip("\n") + "\n" + CSS, "index.html": patch_html(rd("index.html"))}
    shas = {}
    for n in ("index.html", "app.js", "style.css"):
        b = res[n].encode("utf-8")
        (out / n).write_bytes(b)
        shas[n] = sha(b)
    man = json.loads((SRC / "ASSET_SHA256.json").read_text(encoding="utf-8"))
    man["asset_build"] = BUILD
    man["derived_from"] = man["derived_from"] + "。rev01-iは日本語キャプション(固定再生バー内・ON/OFF切替・既定ON。ENDUSER-JA-CAPTION-PRODUCTION-WIRING-01, tools/build_rev01i_01.py CAP1-CAP6)"
    man["files"] = shas
    man["edits"] = man["edits"] + [
        {"id": "CAP1", "file": "app.js", "kind": "ADD", "why": "rev01-i: capUpdate/capSetOn/capInit(点灯中の日本語群のtextContentを#jcapTへ。ON/OFFはbodyのcapon/capoff。保持=URL ?caption=)"},
        {"id": "CAP2", "file": "app.js", "kind": "ADD", "why": "rev01-i: jaLight末尾でcapUpdate()"},
        {"id": "CAP3", "file": "app.js", "kind": "ADD", "why": "rev01-i: render末尾でcapText初期化+capUpdate()"},
        {"id": "CAP4", "file": "style.css", "kind": "ADD", "why": "rev01-i: .jcap(Trial外観)・capon時--bar-h・ON/OFFボタン"},
        {"id": "CAP5", "file": "index.html", "kind": "ADD", "why": "rev01-i: build-id rev01-h->rev01-i、body class=capon(既定ON)、#jcap(row2直下)、#capToggle(.skips内)"},
    ]
    (out / "ASSET_SHA256.json").write_text(json.dumps(man, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return shas


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "enduser_page_assets" / BUILD))
    print(json.dumps(build(ap.parse_args().out), indent=1))

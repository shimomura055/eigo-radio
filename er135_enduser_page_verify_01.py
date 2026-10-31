# -*- coding: utf-8 -*-
"""END-USER-LISTENING-PAGE-PRODUCTION-WIRING-01 委任_02B: End Userページのブラウザ検証CLI(Playwright。API 0)。

記事非依存(公開dirの`enduser/data/article.json`・`sync_<lv>.json`から期待値を作る)。検査内容はDEV rev01-eの検証(ハイライト追従・英語文と日本語訳の連動[J]・文クリック再生・シーク・
パート間連続再生・停止/再開・KP英語のみ・引用英文の太字・学習コーナー0件非表示・console error 0・HTTP 4xx 0)を継承し、End User固有
(DEV表示なし・仮データ注記なし・Voice説明文・訳の出所・音声参照200/206)を追加。PC(1280x900)とモバイル模擬(390x844 iPhone UA)。
実機iOS Safari/Androidではない(模擬)。結果に`device=emulation`を明記する。

使い方: python er135_enduser_page_01.py verify-only --public-dir <dir> [--base-url https://…/user_test/<dir>] [--out result.json] [--shots shots_dir]
        (=本moduleの run())。--base-url省略時は<dir>をローカルのRange対応サーバで配信。
"""
from __future__ import annotations

import functools
import http.server
import json
import os
import re
import socketserver
import threading
import time
import urllib.request
from pathlib import Path

UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) "
      "Version/17.0 Mobile/15E148 Safari/604.1")
VIEWS = {
    "pc": dict(viewport={"width": 1280, "height": 900}),
    "mobile": dict(viewport={"width": 390, "height": 844}, user_agent=UA, device_scale_factor=2, is_mobile=True, has_touch=True),
}
JA = re.compile(r"[ぁ-んァ-ヶ一-龠]")


# ------------------------------------------------------------
# ローカルRange対応サーバ(標準のhttp.serverはRange非対応で音声シークを検証できない)
# ------------------------------------------------------------
class _Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send_head(self):
        rng = self.headers.get("Range")
        path = self.translate_path(self.path)
        if not rng or not os.path.isfile(path):
            return super().send_head()
        m = re.match(r"bytes=(\d*)-(\d*)$", rng.strip())
        if not m:
            return super().send_head()
        size = os.path.getsize(path)
        a, b = m.groups()
        start = int(a) if a else max(0, size - int(b))
        end = min(int(b) if (a and b) else size - 1, size - 1)
        if start > end:
            self.send_error(416)
            return None
        f = open(path, "rb")
        f.seek(start)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        self._left = end - start + 1
        return f

    def copyfile(self, src, dst):
        left = getattr(self, "_left", None)
        if left is None:
            return super().copyfile(src, dst)
        while left > 0:
            buf = src.read(min(65536, left))
            if not buf:
                break
            dst.write(buf)
            left -= len(buf)
        self._left = None


class _Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

    def handle_error(self, request, client_address):   # ブラウザ側のRange中断(接続リセット)は正常動作。標準エラーに出さない
        import sys
        if isinstance(sys.exc_info()[1], (ConnectionError, BrokenPipeError)):
            return
        super().handle_error(request, client_address)


def serve(root: str):
    srv = _Server(("127.0.0.1", 0), functools.partial(_Handler, directory=root))
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}"


def _get_json(u: str):
    req = urllib.request.Request(u + ("&" if "?" in u else "?") + f"cb={int(time.time())}", headers={"Cache-Control": "no-cache"})
    return json.load(urllib.request.urlopen(req, timeout=60))


def _head_ok(u: str) -> int:
    req = urllib.request.Request(u, method="GET", headers={"Range": "bytes=0-1"})
    try:
        return urllib.request.urlopen(req, timeout=60).status
    except urllib.error.HTTPError as e:                 # noqa: PERF203
        return e.code


# ------------------------------------------------------------
# 検証本体
# ------------------------------------------------------------

def boundary_probe_time(b_: dict, sync: list, cap: float = 1.0, margin: float = 0.15) -> float:
    """G検査(次パートへのハイライト移動)のサンプル時刻。次パート`b_`の最初の文のsync発話区間[start,end]の内側に置く:
    min(境界+cap, 当該文の終端-margin)。極短パート(例: 日本語タイトル0.63秒)で境界+1.0秒が発話後・次々パートに入って誤NGになるのを避ける。
    発話区間が短すぎてmarginを引くと境界以下になる場合は区間の中央。検査の意味(境界後にハイライトが次パートへ移る)は不変。"""
    sids = [x["sid"] for pa in b_["paragraphs"] for x in pa]
    rows = {r["sid"]: r for r in sync}
    first = rows[sids[0]] if sids and sids[0] in rows else None
    if first is None:
        return b_["start"] + cap
    lo, hi = max(b_["start"], first["start"]), first["end"]
    t = min(b_["start"] + cap, hi - margin)
    return t if t > lo else (lo + hi) / 2

def run(public_dir, base_url=None, out=None, shots=None) -> int:
    import sys as _pws_sys, pathlib as _pws_p; _pws_sys.path.insert(0, str(next(_q for _q in _pws_p.Path(__file__).resolve().parents if (_q / "tools" / "playwright_safe_01.py").exists()) / "tools")); from playwright_safe_01 import sync_playwright  # PLAYWRIGHT-AUDIO-SAFETY-01: 無音+終了保証+hard timeout
    srv = None
    public_dir = str(Path(public_dir).resolve())
    if base_url is None:
        srv, base = serve(public_dir)
    else:
        base = base_url.rstrip("/")
    live = base.startswith("https://")
    page_url = base + "/enduser/index.html"
    data_url = base + "/enduser/data/"
    art = _get_json(data_url + "article.json")
    syncs = {lv: _get_json(data_url + f"sync_{lv}.json")["sentences"] for lv in art["levels"]}
    binfo = _get_json(base + "/enduser/build_info.json")
    shots_dir = Path(shots) if shots else None
    if shots_dir:
        shots_dir.mkdir(parents=True, exist_ok=True)
    RES = {"base": base, "page": page_url, "live": live, "device": "emulation(Playwright Chromium。実機iOS Safari/Androidではない)", "family": art["family"],
           "id": art["id"], "build_info_dev_sha": binfo["dev_index_sha256"], "views": {}}
    try:
        with sync_playwright() as p:
            for view, opts in VIEWS.items():
                _run_view(p, view, opts, RES, art, syncs, page_url, base, shots_dir)
    finally:
        if srv:
            srv.shutdown()
    allr = [(v, it, k, c["ok"]) for v, R in RES["views"].items() for it, d in R.items() if isinstance(d, dict) for k, c in d.items()]
    RES["summary"] = {"total": len(allr), "ng": [x for x in allr if not x[3]]}
    if out:
        Path(out).write_text(json.dumps(RES, ensure_ascii=False, indent=1), encoding="utf-8")
    print("TOTAL", len(allr), "NG", len(RES["summary"]["ng"]))
    for x in RES["summary"]["ng"]:
        print("NG", x)
    return 0 if not RES["summary"]["ng"] else 3


def _run_view(p, view, opts, RES, art, syncs, page_url, base, shots_dir):
    browser = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    ctx = browser.new_context(**opts)
    page = ctx.new_page()
    errs, bad = [], []
    page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errs.append("PAGEERROR " + str(e)))
    page.on("response", lambda r: bad.append((r.status, r.url)) if r.status >= 400 else None)
    R = {}
    RES["views"][view] = R

    def rec(item, key, ok, detail=None):
        R.setdefault(item, {})[key] = {"ok": bool(ok), "detail": detail}
        print(view, item, key, "OK" if ok else "NG", detail if detail is not None and not ok else "")

    def shot(name, sel=None):
        if not shots_dir:
            return
        if sel:
            page.evaluate("(s) => { const e=document.querySelector(s); if(e) e.scrollIntoView({block:'start'}); window.scrollBy(0,-12); }", sel)
            page.wait_for_timeout(250)
        page.screenshot(path=str(shots_dir / f"{view}_{name}.png"))

    def open_lv(lv, nsent=True):
        page.goto(page_url + f"?lv={lv}&cb={int(time.time() * 1000)}")
        if nsent:
            page.wait_for_selector(".sent")
        page.wait_for_function("() => window.__EUP && window.__EUP.syncKind === 'real'", timeout=15000)
        page.wait_for_timeout(300)

    def A():
        return page.evaluate("() => { const a=document.getElementById('aud'); return {t:a.currentTime, paused:a.paused, src:a.src, err:a.error?a.error.code:null, eup:window.__EUP}; }")

    # ---------- 音声参照(200/206)・build id ----------
    refs = sorted(set(L["main"] for L in art["levels"].values()) | set(pt["seg"] for L in art["levels"].values() for pt in L["parts"]))
    codes = {r: _head_ok(base + "/" + r) for r in refs}
    badc = {r: c for r, c in codes.items() if c not in (200, 206)}
    rec("A", "all_audio_refs_200_or_206", not badc, dict(n=len(refs), bad=dict(list(badc.items())[:5])))
    for rel in ("enduser/app.js", "enduser/style.css", "enduser/data/article.json"):
        rec("A", "asset_" + rel.split("/")[-1] + "_200", _head_ok(base + "/" + rel) in (200, 206), rel)

    for lv, L in art["levels"].items():
        pre = lv + "_"
        parts = L["parts"]
        sync = syncs[lv]
        open_lv(lv)
        # ---- B DEV/仮データ/内部情報が無い ----
        t = page.evaluate("() => document.body.innerText")
        hid = page.evaluate("() => ({title: document.title, sel: document.querySelectorAll('select,option').length, phnote: document.querySelectorAll('.phnote,.devbar,[data-grammar-source],[data-nuance-source]').length, internal: document.querySelectorAll('[class*=\"rpt-\"],.chunk-mark,details.aux').length})")
        rec("B", pre + "no_dev_or_placeholder_text", not re.search(r"\[DEV\]|DEV試作|仮データ|DEV訳|未承認|placeholder|TTS 1回|PASS_WITH_WARNING|制作情報", t + hid["title"]) and hid["phnote"] == 0, dict(hid))
        rec("B", pre + "no_internal_marks_or_article_switch", hid["internal"] == 0 and hid["sel"] == 0 and "⏸" not in t and not re.search(r"記事切替|記事選択", t), hid)
        rec("B", pre + "no_horizontal_overflow", page.evaluate("() => document.documentElement.scrollWidth <= innerWidth"), None)
        # ---- C 見出し・Voice説明文・訳の出所 ----
        nt = page.evaluate("() => { const n=document.getElementById('notice'); return n ? {hidden:n.hidden, text:n.textContent, beforeTabs: !!(n.compareDocumentPosition(document.getElementById('tabs')) & Node.DOCUMENT_POSITION_FOLLOWING)} : null; }")
        if art["notice"]:
            rec("C", pre + "y_notice_shown_under_hero", bool(nt) and not nt["hidden"] and nt["text"] == art["notice"] and nt["beforeTabs"], nt)
        else:
            rec("C", pre + "notice_hidden_when_none", (not nt) or nt["hidden"], nt)
        want_ja = [pt for pt in parts if pt.get("ja")]
        got = page.evaluate("() => [...document.querySelectorAll('.tr')].map(e => ({src: e.dataset.src, n: e.querySelectorAll('p').length, after: e.previousElementSibling ? (e.previousElementSibling.classList.contains('gloss') || e.previousElementSibling.classList.contains('script')) : false}))")
        rec("C", pre + "translation_blocks_equal_approved_data", len(got) == len(want_ja) and all(g["src"] in ("approved_ja_manuscript", "approved_ja_original_in_dev_page", "generated") and g["after"] for g in got), dict(want=len(want_ja), got=len(got)))
        no_ja_en = [pt for pt in parts if pt["kind"] in ("preview", "comment", "story", "oneline") and not pt.get("ja")]
        leaked = page.evaluate("(idxs) => idxs.filter(i => { const b=document.querySelector('[data-part=\"'+i+'\"].partblock, [data-part=\"'+i+'\"].comment, section.card[data-part=\"'+i+'\"]'); return b && b.querySelector('.tr'); })", [pt["idx"] for pt in no_ja_en])
        rec("C", pre + "blocks_without_approved_translation_show_none", not leaked, leaked)
        # ---- D 学習コーナー(0件は見出し・枠ごと非表示/順序) ----
        h2 = page.evaluate("() => [...document.querySelectorAll('.card h2')].map(h => h.textContent)")
        expect = [("vocab", "Vocabulary & Expressions", "vocab"), ("grammar", "Grammar & Sentence Structure", "grammar")]
        # ニュアンス解説は廃止(2026-10-30): article.jsonのnuanceはキー無し/空のみ許容、ページにコーナー(#nuance・見出しh2)が無いこと(構造判定)
        rec("D", pre + "nuance_corner_abolished", not L.get("nuance") and not page.evaluate("() => !!document.getElementById('nuance')") and ("ニュアンス解説" not in h2),
            dict(nuance_items=len(L.get("nuance") or []), h2=h2))
        for key, head, elid in expect:
            n = len(L[key])
            present = page.evaluate("(i) => !!document.getElementById(i)", elid)
            rec("D", pre + f"{key}_corner_{'shown' if n else 'hidden'}", present == bool(n) and ((head in h2) == bool(n)), dict(items=n, present=present))
        order = [h for h in h2 if h in ("Full Story", "Vocabulary & Expressions", "Grammar & Sentence Structure")]
        want_order = ["Full Story"] + [h for k, h, _ in expect if L[k]]
        rec("D", pre + "corner_order", order == want_order, order)
        empty = page.evaluate("() => [...document.querySelectorAll('.card')].filter(c => !c.querySelector('p,dl,ul,div.kp,details,.partblock,.comment,.subblk,.kpitem')).length")
        rec("D", pre + "no_empty_cards", empty == 0, empty)
        cnt = page.evaluate("() => ({vocab: document.querySelectorAll('#vocab details.vi').length, grammar: document.querySelectorAll('#grammar .gr').length})")
        rec("D", pre + "corner_item_counts_equal_data", cnt == {"vocab": len(L["vocab"]), "grammar": len(L["grammar"])}, cnt)
        # ---- E 引用英文の太字 ----
        emph = page.evaluate("() => window.__EMPH")
        zero = [x["heading"] for k in ("vocab",) for x in emph[k] if not x["bold"]]
        rec("E", pre + "vocab_quotes_have_bold", not zero, dict(zero=zero[:5]))
        rec("E", pre + "no_bold_in_transcript_or_gloss", page.evaluate("() => document.querySelectorAll('.sent .target-term, .gloss .target-term, .tr .target-term, .kpitem .target-term').length") == 0, None)
        rec("E", pre + "bold_only_in_quote_dd", page.evaluate("() => [...document.querySelectorAll('strong.target-term')].every(s => { const dd=s.closest('dd'); const dt=dd&&dd.previousElementSibling; return !!dt && ['本文の英文','対象となる本文英文'].includes(dt.textContent); })"), None)
        bad_q = []
        for kind, sel, lab in (("vocab", "#vocab details.vi", "本文の英文"), ("grammar", "#grammar .gr", "対象となる本文英文")):
            for it, bx in zip(L[kind], page.query_selector_all(sel)):
                want = re.sub(r"<[^>]+>", "", [f for f in it["fields"] if f["label"] == lab][0]["html"]).replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
                gotq = bx.evaluate("(el, l) => { const dt=[...el.querySelectorAll('dt')].filter(x => x.textContent === l)[0]; return dt.nextElementSibling.textContent; }", lab)
                if gotq != want:
                    bad_q.append((kind, want[:40], gotq[:40]))
        rec("E", pre + "quote_text_unchanged_by_bold", not bad_q, bad_q[:3])
        # ---- F 本文ハイライト精度/文クリック/シーク/再生/停止 ----
        step = max(1, len(sync) // 24)
        bad_h, n = [], 0
        for r in sync[::step]:
            tt = r["start"] + 0.3 if r["end"] - r["start"] > 0.7 else (r["start"] + r["end"]) / 2
            act = page.evaluate("""(t) => new Promise(res => { const a=document.getElementById('aud'); const done=()=>requestAnimationFrame(()=>requestAnimationFrame(()=>res((window.__EUP||{}).active))); a.addEventListener('seeked', done, {once:true}); a.currentTime=t; setTimeout(done, 2500); })""", tt)
            n += 1
            if act != r["sid"]:
                bad_h.append((r["sid"], round(tt, 2), act))
        rec("F", pre + f"highlight_follows_playhead_{n}_sampled", len(bad_h) <= max(1, n // 20), dict(n=n, bad=bad_h[:5]))
        stories = [pt for pt in parts if pt["kind"] == "story" and pt.get("paragraphs")]
        if stories:
            sids = [s["sid"] for pa in stories[0]["paragraphs"] for s in pa]
            sid = sids[min(2, len(sids) - 1)]
            page.evaluate("document.getElementById('aud').pause()")
            exp = [x for x in sync if x["sid"] == sid][0]
            page.evaluate("(t) => { document.getElementById('aud').currentTime = t; }", max(0.0, exp["start"] - 8.0) if exp["start"] > 9.0 else exp["end"] + 6.0)
            page.wait_for_timeout(500)
            t0 = A()["t"]
            _click_sent(page, view, sid)
            page.wait_for_timeout(1500)
            s = A()
            st = page.evaluate(_STATE_JS)
            # ENDUSER-CLICK-HIGHLIGHT-NO-SEEK-01(2026-10-30承認): 文クリックは選択ハイライトのみ。再生開始・シークをしない
            rec("F", pre + "sentence_click_does_not_play_or_seek", s["paused"] and abs(s["t"] - t0) <= 0.05 and st["onSent"] == [sid] and (s["eup"] or {}).get("sel") == sid,
                dict(sid=sid, t0=t0, t=s["t"], paused=s["paused"], onSent=st["onSent"], sel=(s["eup"] or {}).get("sel")))
            page.evaluate("document.getElementById('aud').pause()")
        page.evaluate("() => { const s=document.getElementById('seek'); s.value=500; s.dispatchEvent(new Event('input',{bubbles:true})); }")
        page.wait_for_timeout(500)
        s = A()
        rec("F", pre + "seekbar_moves_to_50pct", abs(s["t"] / L["total_sec"] - 0.5) < 0.03, round(s["t"] / L["total_sec"], 3))
        page.click("#pp")
        page.wait_for_timeout(800)
        playing = not A()["paused"]
        page.click("#pp")
        page.wait_for_timeout(300)
        rec("F", pre + "play_pause_button", playing and A()["paused"], None)
        rec("F", pre + "audio_no_error", A()["err"] is None, A()["err"])
        # ---- G パート間連続再生(境界を実時間で跨ぐ)・停止/再開 ----
        text_parts = [pt for pt in parts if pt.get("paragraphs")]
        pairs = [(a, b) for a, b in zip(text_parts, text_parts[1:]) if a["idx"] + 1 == b["idx"]] or list(zip(text_parts, text_parts[1:]))
        if len(text_parts) >= 2:
            a_, b_ = sorted(pairs, key=lambda ab: ab[0]["dur"])[0]
            probe_t = boundary_probe_time(b_, sync)              # 次パートの最初の文のsync発話区間の内側(極短パートでも発話後・次々パートに入らない)
            page.evaluate("(t) => { const a=document.getElementById('aud'); a.currentTime=t; a.play(); }", b_["start"] - 2.5)
            try:
                # seek後に再生位置が境界の手前へ戻ったことを確認してから、境界を跨ぐのを待つ(直前の項目の古い再生位置で待機条件が即成立するのを排除)
                page.wait_for_function("(t) => window.__EUP && window.__EUP.gt <= t && !document.getElementById('aud').paused", arg=b_["start"], timeout=6000)
                page.wait_for_function("(t) => window.__EUP && window.__EUP.gt > t && !document.getElementById('aud').paused", arg=probe_t, timeout=12000)
            except Exception:
                pass
            s = A()
            act = s["eup"]["active"]                              # 境界を跨いだ直後(発話区間内)の点灯文
            try:
                page.wait_for_function("(t) => window.__EUP && window.__EUP.gt > t + 1.0 && !document.getElementById('aud').paused", arg=b_["start"], timeout=12000)
            except Exception:
                pass
            s2 = A()
            rec("G", pre + "continues_across_part_boundary", (not s2["paused"]) and s2["eup"]["gt"] > b_["start"] + 0.9 and s2["eup"]["mode"] == "full", dict(from_=a_["label"], to=b_["label"], gt=s2["eup"]["gt"], boundary=b_["start"]))
            nxt = [x["sid"] for pa in b_["paragraphs"] for x in pa]
            rec("G", pre + "highlight_moves_into_next_part", bool(act) and act in nxt and s["eup"]["gt"] >= b_["start"], dict(active=act, part=b_["label"], gt=s["eup"]["gt"], probe_t=probe_t))
            btn = page.query_selector(f'[data-part="{b_["idx"]}"] .btns .seek.stop')
            btn.scroll_into_view_if_needed()
            btn.click()
            page.wait_for_timeout(500)
            e1 = A()
            page.wait_for_timeout(1000)
            e2 = A()
            rec("G", pre + "stop_button_stops_during_continuous_playback", e1["paused"] and e2["paused"] and abs(e2["t"] - e1["t"]) < 0.05, dict(t1=e1["t"], t2=e2["t"]))
            fb = page.query_selector(f'[data-part="{b_["idx"]}"] .btns .seek.from')
            fb.scroll_into_view_if_needed()
            fb.click()
            page.wait_for_timeout(1500)
            s3 = A()
            rec("G", pre + "from_button_resumes_at_part_start", (not s3["paused"]) and abs(s3["eup"]["gt"] - b_["start"]) < 4 and s3["eup"]["mode"] == "full", dict(gt=s3["eup"]["gt"], start=b_["start"]))
            page.evaluate("document.getElementById('aud').pause()")
        btns = page.evaluate("() => ({from: document.querySelectorAll('.btns .seek.from').length, stop: document.querySelectorAll('.btns .seek.stop').length, adj: [...document.querySelectorAll('.btns .seek.from')].every(f => f.nextElementSibling && f.nextElementSibling.classList.contains('stop'))})")
        rec("G", pre + "from_and_stop_buttons_paired", btns["from"] == btns["stop"] and btns["from"] > 3 and btns["adj"], btns)
        # ---- H Key Phrase 英語のみ ----
        kps = [pt for pt in parts if pt["kind"] == "kp"]
        kbtns = page.query_selector_all(".kpitem button[data-act=kp]")
        rec("H", pre + "kp_buttons_equal_data", len(kbtns) == len(kps), dict(btns=len(kbtns), kp=len(kps)))
        main_url = page.evaluate("(m) => new URL('../' + m, location.href).href", L["main"])
        for i, pt in enumerate(kps[:3]):
            ea = pt["kp"][0]["en_audio"]
            kbtns[i].scroll_into_view_if_needed()
            kbtns[i].click()
            samples = page.evaluate("""([mainUrl]) => new Promise(res => { const a=document.getElementById('aud'); const out=[]; const t0=performance.now();
              (function f(){ out.push([Math.round(performance.now()-t0), +a.currentTime.toFixed(3), a.paused, a.src !== mainUrl]); if (performance.now()-t0 > 9000 || (a.paused && out.length>30 && a.currentTime>0)) res(out); else requestAnimationFrame(f); })(); })""", [main_url])
            segs = [x for x in samples if x[3]]
            started = [x for x in segs if not x[2] and x[1] > 0]
            first_t = started[0][1] if started else None
            maxt = max([x[1] for x in segs] or [0])
            ok = bool(started) and abs(first_t - ea["start"]) < 0.6 and samples[-1][2] and (not samples[-1][3]) and ea["end"] - 0.2 <= maxt <= ea["end"] + 0.35
            rec("H", pre + f"kp{i + 1}_plays_english_window_only", ok, dict(window=[ea["start"], ea["end"]], first_t=first_t, max_t=round(maxt, 3), stopped=samples[-1][2], back_to_full=not samples[-1][3]))
        # ---- V Vocabulary & Expressions の英語音声(rev01-g。掲載項目は全件再生可) ----
        vocab = L["vocab"]
        vbtns = page.query_selector_all("#vocab details.vi summary button[data-act=vocab]") if vocab else []
        rec("V", pre + "vocab_play_button_for_every_item", len(vbtns) == len(vocab) and all(isinstance(v.get("audio"), dict) for v in vocab), dict(btns=len(vbtns), vocab=len(vocab)))
        if vocab:
            codes = {v["audio"]["file"]: _head_ok(base + "/enduser/" + v["audio"]["file"]) for v in vocab if v.get("audio")}
            badv = {f: c for f, c in codes.items() if c not in (200, 206)}
            rec("V", pre + "vocab_audio_refs_200_or_206", len(codes) == len(vocab) and not badv, dict(n=len(codes), bad=dict(list(badv.items())[:3])))
            # 通し再生の途中(20秒付近)で各項目を押す: その項目の単体mp3が最後まで再生され、文ハイライトは出ず、終端で通し再生の状態(位置・停止)へ戻る
            bad_play = []
            for i, v in enumerate(vocab if len(vbtns) == len(vocab) else []):   # 再生ボタンが無い/不足の旧asset(rev01-f以前)はIndexErrorにせず上のrecでNG表示
                try:   # 直前の項目の終端で通し音声のsrcが戻る途中(metadata未取得)にseekしない(取得前のcurrentTime代入は0へ戻る=検査側の競合)
                    page.wait_for_function("() => document.getElementById('aud').readyState >= 1", timeout=5000)
                except Exception:
                    pass
                page.evaluate("(t) => { const a=document.getElementById('aud'); a.currentTime=t; a.play(); }", 20.0)
                page.wait_for_timeout(500)
                before_open = page.evaluate("(i) => document.getElementById('vi-' + %s + '-' + i).open" % json.dumps(lv), i)
                btn = vbtns[i]
                btn.scroll_into_view_if_needed()
                btn.click()
                try:
                    page.wait_for_function("(i) => window.__EUP && window.__EUP.mode === 'vocab' && window.__EUP.vi === i && !document.getElementById('aud').paused", arg=i, timeout=5000)
                except Exception:
                    pass
                page.wait_for_timeout(250)
                s_ = A()
                during = dict(mode=(s_["eup"] or {}).get("mode"), vi=(s_["eup"] or {}).get("vi"), paused=s_["paused"], src_ok=s_["src"].endswith("/enduser/" + v["audio"]["file"]),
                              active=(s_["eup"] or {}).get("active"), jg=(s_["eup"] or {}).get("jg"))
                after_open = page.evaluate("(i) => document.getElementById('vi-' + %s + '-' + i).open" % json.dumps(lv), i)
                try:
                    page.wait_for_function("() => window.__EUP && window.__EUP.mode === 'full' && document.getElementById('aud').paused", timeout=int(v["audio"]["dur"] * 1000) + 6000)
                except Exception:
                    pass
                # 終端でendVocab()はmode='full'+pause()を同期で行い、位置復帰(currentTime=)は通し音声のloadedmetadata後(withMeta)。mode/pausedだけを待つと復帰前のt=0を読む検査側の競合
                # (ENDUSER-JA-CAPTION-PRODUCTION-WIRING-01で確定。evidence_02/repro_vocab_flake.py: 通し音声の応答遅延でも製品は正しく復帰する)。通し音声のmetadata読込完了を待ってから位置を判定する。
                try:
                    page.wait_for_function("() => { const a = document.getElementById('aud'); return a.readyState >= 1 && a.src.indexOf('/audio/vocab_') < 0; }", timeout=8000)
                    page.wait_for_timeout(300)
                except Exception:
                    pass
                e_ = A()
                if not (during["mode"] == "vocab" and during["vi"] == i and not during["paused"] and during["src_ok"] and not during["active"] and not during["jg"]
                        and before_open == after_open and (e_["eup"] or {}).get("mode") == "full" and e_["paused"] and abs(e_["t"] - 20.0) < 2.5 and e_["err"] is None):
                    bad_play.append(dict(i=i, heading=v["heading"], during=during, open=[before_open, after_open], end=dict(mode=(e_["eup"] or {}).get("mode"), paused=e_["paused"], t=e_["t"])))
            rec("V", pre + "vocab_each_item_plays_own_audio_and_returns", not bad_play, bad_play[:2])
            if vbtns:
                # 再生中の一時停止ボタン(共有プレーヤ)で止まり、その後の通し再生が壊れていない
                vbtns[0].scroll_into_view_if_needed()
                vbtns[0].click()
                page.wait_for_timeout(200)
                page.click("#pp")
                page.wait_for_timeout(300)
                p1 = A()
                page.evaluate("window.scrollTo(0, 0)")
                page.click("#playAll")                      # 一時停止後に『全体を再生』で通し再生へ戻れる(共有プレーヤの状態が壊れていない)
                page.wait_for_timeout(1500)
                p2 = A()
                rec("V", pre + "vocab_pause_then_full_playback_still_works", p1["paused"] and (not p2["paused"]) and (p2["eup"] or {}).get("mode") == "full" and (p2["eup"] or {}).get("gt", 0) > 0.5
                    and "/enduser/audio/vocab_" not in p2["src"], dict(paused_in_vocab=p1["paused"], mode=(p2["eup"] or {}).get("mode"), gt=(p2["eup"] or {}).get("gt"), src=p2["src"][-40:]))
                page.evaluate("document.getElementById('aud').pause()")
        # ---- I 意味一覧(覚えておきたい表現) ----
        has_gl = any(pt.get("glossary") for pt in parts)
        if has_gl:
            dom = page.evaluate("() => [...document.querySelectorAll('.partblock')].filter(b => b.querySelector('.gloss')).map(b => ({part:+b.dataset.part, n:b.querySelectorAll('.gloss li').length, links:b.querySelectorAll('a.glink').length, order:[...b.children].map(c => c.className.split(' ')[0])}))")
            wantg = {pt["idx"]: len(pt["glossary"]) for pt in parts if pt.get("glossary")}
            rec("I", pre + "glossary_items_equal_data", {d["part"]: d["n"] for d in dom} == wantg, dict(got={d["part"]: d["n"] for d in dom}, want=wantg))
            rec("I", pre + "glossary_before_translation_after_body", all(("tr" not in d["order"]) or d["order"].index("gloss") < d["order"].index("tr") for d in dom) and all(d["order"].index("script") < d["order"].index("gloss") for d in dom if "script" in d["order"]), dom[:2])
            links = page.query_selector_all(".gloss a.glink")
            badl = []
            for li in links[:6]:
                en = li.evaluate("e => e.parentElement.querySelector('.ge').textContent")
                href = li.get_attribute("href")
                li.scroll_into_view_if_needed()
                li.click()
                # 長いページ(Yの3 Voice等)ではsmooth scrollが700msで終わらない。スクロール位置が止まる(150ms間隔で2回連続同値)まで最大5秒待ってから判定する
                # smooth scrollの開始が遅れる環境で『開始前に同値2回』と誤判定しないよう、目的地(開いた項目が画面内)に到達し、かつ停止してから判定する(最大6秒。到達しなければNG)
                page.evaluate("""(href) => new Promise(res => { let last = -1, same = 0; const t0 = performance.now();
                  (function f(){ const y = Math.round(scrollY); same = (y === last) ? same + 1 : 0; last = y;
                    const t = document.getElementById(href.slice(1)), b = t && t.getBoundingClientRect(), there = !!t && t.open && b.top >= -5 && b.top <= innerHeight * 0.8;
                    if ((there && same >= 2) || performance.now() - t0 > 6000) res(y); else setTimeout(f, 150); })(); })""", href)
                r_ = page.evaluate("(href) => { const t=document.getElementById(href.slice(1)); if(!t) return null; const b=t.getBoundingClientRect(); return {top:b.top, open:t.open, head:t.querySelector('.vh').textContent, vh:innerHeight}; }", href)
                if not r_ or r_["head"] != en or not r_["open"] or not (-5 <= r_["top"] <= r_["vh"] * 0.8):
                    badl.append((en, href, r_))
            rec("I", pre + "glossary_links_open_the_expression", not badl, badl[:2])
        else:
            rec("I", pre + "no_glossary_when_not_applicable", page.evaluate("() => document.querySelectorAll('.gloss').length") == 0, None)
        # ---- J 英語文と日本語訳の連動(J1-J8 + M7) ----
        linked_checks(page, view, lv, L, sync, rec, shot, open_lv, lvs=list(art["levels"]), art=art)
        # ---- CAP 日本語キャプション(rev01-i。ENDUSER-JA-CAPTION-PRODUCTION-WIRING-01 M-5) ----
        open_lv(lv)
        caption_checks(page, view, lv, L, rec, open_lv)
        # ---- J 画面の目視用shots ----
        open_lv(lv)
        shot(f"{lv}_top")
        shot(f"{lv}_fullstory", "#fullstory")
        for corner in ("vocab", "grammar"):
            if L[corner]:
                shot(f"{lv}_{corner}", "#" + corner)
    # 太字化の汎用単体確認(記事非依存): 語形変化・プレースホルダ・不規則動詞の3単現/ing形・曖昧時は太字にしない
    open_lv(list(art["levels"])[0])
    for h, tx, want in [("give up", "She gave it up quickly.", None), ("give sth up", "She gave it up quickly.", ["gave", "up"]), ("hold one's breath", "They held their breath for a minute.", ["held", "breath"]),
                        ("hold heat in", "What matters is how well it holds heat in", ["holds heat in"]), ("make progress", "They are making progress.", ["making progress"]),
                        ("carry over", "It carried over.", ["carried over"]), ("study", "He studies hard.", ["studies"]), ("stop", "We stopped.", ["stopped"]),
                        ("go on", "Go on and on.", ["Go on"]), ("on", "Go on and on.", None), ("get", "He had gotten it.", ["gotten"]), ("foo bar", "nothing here", None)]:
        r_ = page.evaluate("([h, t]) => { const m = window.__matchPhrase(h, t, true); return {n: m.n, txt: m.ranges.map(x => t.slice(x[0], x[1]))}; }", [h, tx])
        got_ = r_["txt"] if r_["n"] == 1 else None
        rec("U", "generic_" + re.sub(r"\W+", "_", h), got_ == want, dict(text=tx, result=r_))
    if len(art["levels"]) == 2:
        a_lv, b_lv = list(art["levels"])
        open_lv(a_lv)
        page.click(f"#tabs button[data-lv={b_lv}]")
        page.wait_for_timeout(800)
        ey = page.text_content("#eyebrow").lower()
        rec("K", "level_switch", ("advanced" if b_lv == "adv" else "standard") in ey and A()["eup"]["level"] == b_lv, ey)
    rec("Z", "console_errors_0", not errs, errs[:5])
    rec("Z", "http_4xx_5xx_0", not bad, bad[:5])
    browser.close()


# ------------------------------------------------------------
# K2: 日本語キャプション(ENDUSER-JA-CAPTION-PRODUCTION-WIRING-01 / Opus M-5。rev01-i以降のページのみ)
# ------------------------------------------------------------
_CAP_LAYOUT_JS = """() => { const cap = document.getElementById('jcap'), bar = document.getElementById('bar'), t = document.getElementById('capToggle'), a = document.getElementById('aud');
  return {on: document.body.classList.contains('capon'), disp: getComputedStyle(cap).display, jcapH: Math.round(cap.getBoundingClientRect().height * 10) / 10, barH: Math.round(bar.getBoundingClientRect().height * 10) / 10,
          capScroll: cap.scrollHeight, capClient: cap.clientHeight, txt: t.textContent, aria: t.getAttribute('aria-pressed'), url: location.search, capText: document.getElementById('jcapT').textContent,
          paused: a.paused, t: a.currentTime, sel: (window.__EUP || {}).sel, mode: (window.__EUP || {}).mode}; }"""
_CAP_CLICK_ALL_JS = """() => { const a = document.getElementById('aud'), t0 = a.currentTime, rows = [];
  const cs0 = getComputedStyle(document.getElementById('jcap')), twoBox = 2 * parseFloat(cs0.lineHeight) + parseFloat(cs0.paddingTop) + parseFloat(cs0.paddingBottom) + parseFloat(cs0.borderTopWidth) + parseFloat(cs0.borderBottomWidth);   // 2行分の枠高さ
  document.querySelectorAll('.sent').forEach(s => { s.click(); const c = document.getElementById('jcap'); rows.push({sid: s.dataset.sid, cap: document.getElementById('jcapT').textContent,
    barH: Math.round(document.getElementById('bar').getBoundingClientRect().height * 10) / 10, scr: c.scrollHeight, cli: c.clientHeight, two: twoBox}); });
  return {rows, played: !a.paused, moved: Math.abs(a.currentTime - t0) > 0.05}; }"""


def caption_expected(L: dict) -> dict:
    """sid -> 期待キャプション。ja_align由来(群なしsid・g.ja==null・ja無しpart・ja_align無し/劣化=空欄)。app.jsのcapUpdate(点灯中の群のtextContent)と同じ定義。"""
    groups, sid2key, _ = expect_maps(L)
    out = {}
    for pt in L["parts"]:
        for pa in pt.get("paragraphs") or []:
            for s in pa:
                out[s["sid"]] = groups.get(sid2key.get(s["sid"]), "") if sid2key.get(s["sid"]) else ""
    return out


def caption_checks(page, view, lv, L, rec, open_lv):
    pre = lv + "_CAP_"
    if (page.evaluate("() => document.body.dataset.build || ''") or "") < "rev01-i" or not page.evaluate("() => !!document.getElementById('jcap')"):
        rec("CAP", pre + "skipped_asset_without_caption", True, "ページがrev01-i未満(凍結dir等)。verify_consistencyが版を別途検査")
        return
    exp = caption_expected(L)
    L0 = page.evaluate(_CAP_LAYOUT_JS)
    rec("CAP", pre + "initial_ON", L0["on"] and L0["disp"] == "block" and L0["txt"].endswith("ON") and L0["aria"] == "true" and "caption" not in L0["url"], L0)
    # 停止中に全英文をクリック: capがja_align由来の期待値と一致・再生/シークしない・バー高さが0〜2行で一定
    info = page.evaluate(_CAP_CLICK_ALL_JS)
    rows = info["rows"]
    badx = [(r["sid"], r["cap"][:20], exp.get(r["sid"], "")[:20]) for r in rows if r["cap"] != exp.get(r["sid"], "")]
    blank_exp = sum(1 for r in rows if exp.get(r["sid"], "") == "")
    rec("CAP", pre + "click_stopped_caption_equals_ja_align_expected", bool(rows) and not badx and (not info["played"]) and (not info["moved"]),
        dict(sentences=len(rows), expected_blank=blank_exp, expected_nonblank=len(rows) - blank_exp, mismatch=badx[:3], played=info["played"], moved=info["moved"]))
    base_h = L0["barH"]
    fit = [r for r in rows if r["scr"] <= r["two"] + 1]   # キャプション本文が2行以内に収まる行(枠は0〜2行で同じ高さでなければならない。Opus R-1。旧CSSの1行以下162/2行176の差を検出)
    badh = sorted({r["barH"] for r in fit if abs(r["barH"] - base_h) > 0.6})
    rec("CAP", pre + "bar_height_constant_0_to_2_lines", bool(fit) and not badh, dict(base=base_h, fit_rows=len(fit), over2_rows=len(rows) - len(fit), other_heights=badh[:4]))
    # OFF -> ON(停止中。選択状態を保持)
    sel = next((r for r in rows if exp.get(r["sid"])), None)
    if sel:
        page.evaluate("(sid) => document.querySelector('[data-sid=\"'+sid+'\"]').click()", sel["sid"])
    S0 = page.evaluate(_CAP_LAYOUT_JS)
    page.click("#capToggle")
    page.wait_for_timeout(150)
    S1 = page.evaluate(_CAP_LAYOUT_JS)
    rec("CAP", pre + "OFF_hides_caption_frees_bar", (not S1["on"]) and S1["disp"] == "none" and S1["jcapH"] == 0 and S1["barH"] < S0["barH"] - 40 and S1["txt"].endswith("OFF") and S1["aria"] == "false" and "caption=0" in S1["url"], dict(on=S0["barH"], off=S1["barH"], url=S1["url"]))
    page.click("#capToggle")
    page.wait_for_timeout(150)
    S2 = page.evaluate(_CAP_LAYOUT_JS)
    rec("CAP", pre + "ON_again_restores_bar_and_current_ja_and_clears_url", S2["on"] and abs(S2["barH"] - S0["barH"]) < 0.6 and S2["capText"] == S0["capText"] and "caption" not in S2["url"]
        and S1["paused"] == S0["paused"] == S2["paused"] and S1["t"] == S0["t"] == S2["t"] and S1["sel"] == S0["sel"] == S2["sel"], dict(S0=S0, S2=S2))
    # 再生中の切替でcurrentTime・pausedが乱れない
    if rows:
        page.evaluate("() => { const a = document.getElementById('aud'); a.currentTime = 2; a.play(); }")
        page.wait_for_timeout(900)
        T0 = page.evaluate(_CAP_LAYOUT_JS)
        page.click("#capToggle")
        page.wait_for_timeout(300)
        T1 = page.evaluate(_CAP_LAYOUT_JS)
        page.click("#capToggle")
        page.wait_for_timeout(300)
        T2 = page.evaluate(_CAP_LAYOUT_JS)
        page.evaluate("() => document.getElementById('aud').pause()")
        rec("CAP", pre + "toggle_while_playing_keeps_playback", (not T0["paused"]) and (not T1["paused"]) and (not T2["paused"]) and 0.2 < T1["t"] - T0["t"] < 1.5 and 0.2 < T2["t"] - T1["t"] < 1.5 and T0["mode"] == T1["mode"] == T2["mode"],
            dict(t=[T0["t"], T1["t"], T2["t"]], paused=[T0["paused"], T1["paused"], T2["paused"]]))
    # ?caption=0で開く: OFF・キャプション高0・バー高さ復帰。レベル切替でOFF保持、ON操作でURLからcaptionが消える
    page.goto(page.url.split("?")[0] + f"?lv={lv}&caption=0&cb=cap")
    page.wait_for_function("() => window.__EUP && window.__EUP.syncKind === 'real'", timeout=15000)
    page.wait_for_timeout(200)
    Q0 = page.evaluate(_CAP_LAYOUT_JS)
    rec("CAP", pre + "caption0_opens_OFF_with_bar_restored", (not Q0["on"]) and Q0["disp"] == "none" and Q0["jcapH"] == 0 and Q0["barH"] < base_h - 40 and Q0["txt"].endswith("OFF"), Q0)
    open_lv(lv)   # 後続の検査のため通常状態(既定ON)へ戻す


# ------------------------------------------------------------
# J: 英語文と日本語訳の連動ハイライト(ENDUSER-EN-JA-LINKED-HIGHLIGHT-01。J1-J8 + M7)
# ------------------------------------------------------------
def expect_maps(L: dict) -> tuple:
    """(groups{key:text}, sid2key{sid:key}, null_sids[...])。keyはapp.jsのdata-jgと同じ '<part.idx>:<g>'。テキストはPythonのUTF-16切り出し(M4)。"""
    import er135_enduser_align_01 as AL
    groups, sid2key, null_sids = {}, {}, []
    for pt in L["parts"]:
        aligned = {s for g in (pt.get("ja_align") or []) if g.get("ja") for s in g["sids"]}
        for g in pt.get("ja_align") or []:
            if g.get("ja"):
                pi, a, b = g["ja"]
                key = f'{pt["idx"]}:{g["g"]}'
                groups[key] = AL.slice_u16(pt["ja"][pi], a, b)
                for s in g["sids"]:
                    sid2key[s] = key
        for pa in pt.get("paragraphs") or []:
            for s in pa:
                if pt.get("ja") and s["sid"] not in aligned:
                    null_sids.append(s["sid"])
    return groups, sid2key, null_sids


_STATE_JS = """() => ({ eup: window.__EUP || {}, onSent: [...document.querySelectorAll('.sent.on')].map(e => e.dataset.sid),
                         onJhl: [...document.querySelectorAll('.jhl.on')].map(e => e.dataset.jg) })"""
_SEEK_STATE_JS = """(t) => new Promise(res => { const a=document.getElementById('aud'); const fin=()=>requestAnimationFrame(()=>requestAnimationFrame(()=>res({
    eup: window.__EUP || {}, onSent: [...document.querySelectorAll('.sent.on')].map(e => e.dataset.sid),
    onJhl: [...document.querySelectorAll('.jhl.on')].map(e => e.dataset.jg) })));
  a.addEventListener('seeked', fin, {once:true}); a.currentTime=t; setTimeout(fin, 2500); })"""


def _consistent(st: dict, sid2key: dict, gap_ok: set | None = None) -> bool:
    """点灯状態がデータ通りか: EN点灯==active、JA点灯==active文の群(群なし=0個)。文と文の間(active無し)はgap_okの群のみ許容。"""
    act = st["eup"].get("active")
    if act is None:
        return st["onSent"] == [] and (st["onJhl"] == [] or (gap_ok is not None and st["onJhl"] and set(st["onJhl"]) <= gap_ok and len(set(st["onJhl"])) == 1))
    want = sid2key.get(act)
    return st["onSent"] == [act] and ((st["onJhl"] == []) if want is None else (set(st["onJhl"]) == {want} and len(st["onJhl"]) == len(set(st["onJhl"])) and st["eup"].get("jg") == want))


def _click_sent(page, view, sid):
    """英文のクリック(PC)/タップ(mobile=has_touch)。同じ.sent要素へ。"""
    sel = f'[data-sid="{sid}"]'
    if view == "mobile":
        page.tap(sel)
    else:
        page.click(sel)


_NOSEEK_PROBE_JS = """() => { const a=document.getElementById('aud'); window.__ev={seeking:0,pause:0,play:0};
  a.addEventListener('seeking',()=>window.__ev.seeking++); a.addEventListener('pause',()=>window.__ev.pause++); a.addEventListener('play',()=>window.__ev.play++); return true; }"""


def click_no_seek_checks(page, view, lv, L, sync, rec, sid2key, null_sids):
    """ENDUSER-CLICK-HIGHLIGHT-NO-SEEK-01 原文§3 項目1,2,3,6,7(+位置操作での解除/同一文再クリック)。クリックでseek/play/pauseが起きないことを実イベントで検査する。"""
    pre = lv + "_K_"
    A = lambda: page.evaluate("() => { const a=document.getElementById('aud'); return {t:a.currentTime, paused:a.paused, eup:window.__EUP}; }")
    startof = {r["sid"]: r for r in sync}
    sids_all = [r["sid"] for r in sync]
    mapped = [s for s in sids_all if s in sid2key]
    unmapped = [s for s in sids_all if s not in sid2key]
    by_grp = {}
    for s in mapped:
        by_grp.setdefault(sid2key[s], []).append(s)
    multi = next((v for v in by_grp.values() if len(v) >= 2), None)

    def far(cur, cands):
        return next((s for s in cands if abs(startof[s]["start"] - cur) > 6.0), cands[0] if cands else None)
    # 項目1 停止中クリック
    page.evaluate("document.getElementById('aud').pause()")
    page.evaluate("(t) => { document.getElementById('aud').currentTime = t; }", 0.0)
    page.wait_for_timeout(400)
    page.evaluate(_NOSEEK_PROBE_JS)
    t0 = A()["t"]
    target = far(t0, mapped)
    if target:
        _click_sent(page, view, target)
        page.wait_for_timeout(1500)
        s = A(); st = page.evaluate(_STATE_JS); ev = page.evaluate("() => window.__ev")
        rec("K", pre + "item1_click_while_stopped_lights_en_ja_no_play", s["paused"] and abs(s["t"] - t0) <= 0.05 and ev["play"] == 0 and ev["seeking"] == 0 and st["onSent"] == [target] and st["onJhl"] == [sid2key[target]],
            dict(sid=target, t0=t0, t=s["t"], paused=s["paused"], events=ev, onSent=st["onSent"], onJhl=st["onJhl"]))
        # 同一文の再クリック=選択維持(トグルしない)
        _click_sent(page, view, target)
        page.wait_for_timeout(300)
        st = page.evaluate(_STATE_JS)
        rec("K", pre + "reclick_same_sentence_keeps_selection", st["onSent"] == [target] and st["onJhl"] == [sid2key[target]], dict(onSent=st["onSent"], onJhl=st["onJhl"]))
        # 位置操作(+10秒)で選択解除
        page.click("#fwd10")
        page.wait_for_timeout(500)
        s = A()
        rec("K", pre + "position_op_clears_selection", (s["eup"] or {}).get("sel") is None, (s["eup"] or {}).get("sel"))
    # 項目2 一時停止中クリック
    page.evaluate("(t) => { document.getElementById('aud').currentTime = t; }", 0.0)
    page.click("#pp")
    page.wait_for_timeout(900)
    page.click("#pp")
    page.wait_for_timeout(400)
    page.evaluate(_NOSEEK_PROBE_JS)
    s0 = A()
    target2 = far(s0["t"], mapped)
    if target2 and s0["paused"]:
        _click_sent(page, view, target2)
        page.wait_for_timeout(1200)
        s = A(); st = page.evaluate(_STATE_JS); ev = page.evaluate("() => window.__ev")
        rec("K", pre + "item2_click_while_paused_keeps_position_lights_en_ja", s["paused"] and abs(s["t"] - s0["t"]) <= 0.05 and ev["play"] == 0 and ev["seeking"] == 0 and st["onSent"] == [target2] and st["onJhl"] == [sid2key[target2]],
            dict(sid=target2, t0=s0["t"], t=s["t"], events=ev, onSent=st["onSent"], onJhl=st["onJhl"]))
    # 項目3 再生中クリック
    page.evaluate("(t) => { document.getElementById('aud').currentTime = t; }", 0.0)
    page.click("#pp")
    page.wait_for_timeout(1200)
    page.evaluate(_NOSEEK_PROBE_JS)
    cur = A()["t"]
    target3 = far(cur, sids_all)
    if target3:
        samples = []
        _click_sent(page, view, target3)
        for _ in range(6):
            samples.append(A())
            page.wait_for_timeout(250)
        ev = page.evaluate("() => window.__ev")
        st = page.evaluate(_STATE_JS)
        mono = all(b["t"] >= a["t"] - 0.01 for a, b in zip(samples, samples[1:])) and samples[-1]["t"] > cur
        no_pause = all(not x["paused"] for x in samples)
        # 次の再生位置更新で自動ハイライトへ戻る=点灯中の文はクリックした文ではなく再生位置の文(クリック文の区間に再生位置が入った場合を除く)
        r3 = startof[target3]
        back = st["eup"].get("active") != target3 or (r3["start"] - 0.5 <= samples[-1]["t"] <= r3["end"] + 0.5)
        rec("K", pre + "item3_click_while_playing_no_seek_no_interrupt", mono and no_pause and ev["seeking"] == 0 and ev["pause"] == 0 and st["eup"].get("sel") is None and back and _consistent(st, sid2key, set(sid2key.values())),
            dict(sid=target3, cur=cur, t_end=samples[-1]["t"], mono=mono, no_pause=no_pause, events=ev, sel=st["eup"].get("sel"), active=st["eup"].get("active")))
    page.evaluate("document.getElementById('aud').pause()")
    page.wait_for_timeout(300)
    # 項目6 1対多(複数文1群)・対応未確定(null群)
    bad6 = []
    if multi:
        for sd in multi[:2]:
            _click_sent(page, view, sd)
            page.wait_for_timeout(300)
            st = page.evaluate(_STATE_JS)
            if not (st["onSent"] == [sd] and st["onJhl"] == [sid2key[sd]]):
                bad6.append(("multi", sd, st["onSent"], st["onJhl"]))
    for sd in (unmapped[:2] if unmapped else []):
        _click_sent(page, view, sd)
        page.wait_for_timeout(300)
        st = page.evaluate(_STATE_JS)
        if not (st["onSent"] == [sd] and st["onJhl"] == []):
            bad6.append(("null", sd, st["onSent"], st["onJhl"]))
    rec("K", pre + "item6_multi_sentence_group_and_null_group_no_false_light", not bad6, dict(multi=bool(multi), null_clicked=len(unmapped[:2]), bad=bad6[:3]))
    page.evaluate("document.getElementById('aud').pause()")


def linked_checks(page, view, lv, L, sync, rec, shot, open_lv, tabs_other=None, lvs=None, art=None):
    groups, sid2key, null_sids = expect_maps(L)
    pre = lv + "_"
    has = bool(groups)
    # ---- J1 span数・data-jg・テキスト(Python側UTF-16切り出し==ブラウザ側textContent) ----
    dom = page.evaluate("() => [...document.querySelectorAll('.jhl')].map(e => [e.dataset.jg, e.textContent])")
    got = {}
    dup = False
    for k, t in dom:
        dup = dup or (k in got)
        got[k] = t
    rec("J", pre + "J1_span_count_keys_text_equal_python_slice", (not dup) and got == groups, dict(want=len(groups), got=len(got), dup=dup,
        diff=[k for k in groups if got.get(k) != groups[k]][:3]))
    # ---- J2 訳本文は不変(.tr内のp==data.ja) ----
    bad2 = []
    for pt in L["parts"]:
        if not pt.get("ja"):
            continue
        txt = page.evaluate("(i) => [...document.querySelectorAll('[data-part=\"'+i+'\"] .tr p')].map(e => e.textContent)", pt["idx"])
        if txt != pt["ja"]:
            bad2.append(pt["label"])
    rec("J", pre + "J2_translation_text_unchanged", not bad2, bad2[:3])
    if not has:
        rec("J", pre + "J0_no_align_no_spans_old_display", len(dom) == 0, len(dom))
        return
    # ---- J3 文クリック: その文の群だけ点灯・他JA非点灯 / null群の文は無点灯 ----
    story = [pt for pt in L["parts"] if pt["kind"] == "story" and pt.get("paragraphs")]
    sids_all = [s["sid"] for pt in story for pa in pt["paragraphs"] for s in pa]
    pick = [sid for sid in sids_all if sid in sid2key][:1] + [sid for sid in sids_all if sid in sid2key][-1:] + ([sid for sid in sids_all if sid not in sid2key][:1])
    bad3 = []
    for sid in pick:
        page.evaluate("document.getElementById('aud').pause()")
        _click_sent(page, view, sid)
        page.wait_for_timeout(450)
        st = page.evaluate(_STATE_JS)
        if not _consistent(st, sid2key):
            bad3.append((sid, st["eup"].get("active"), st["onJhl"], st["onSent"]))
    page.evaluate("document.getElementById('aud').pause()")
    rec("J", pre + f"J3_click_lights_only_mapped_group_{len(pick)}", not bad3, bad3[:3])
    # ---- J3b story以外(Preview/Comment/In One Line。訳が生成された部分)も、各partの先頭の対応済みの文をクリックして同じ規則で点灯する(委任_03A: 全パート適用) ----
    other = [pt for pt in L["parts"] if pt["kind"] != "story" and pt.get("ja_align") and pt.get("paragraphs")]
    bad3b, picked_b = [], 0
    for pt in other:
        mapped = [s_["sid"] for pa in pt["paragraphs"] for s_ in pa if s_["sid"] in sid2key]
        if not mapped:
            continue
        picked_b += 1
        page.evaluate("document.getElementById('aud').pause()")
        _click_sent(page, view, mapped[0])
        page.wait_for_timeout(450)
        st = page.evaluate(_STATE_JS)
        if not _consistent(st, sid2key):
            bad3b.append((pt["key"], mapped[0], st["eup"].get("active"), st["onJhl"], st["onSent"]))
    page.evaluate("document.getElementById('aud').pause()")
    if other:
        rec("J", pre + f"J3b_click_lights_mapped_group_in_non_story_parts_{picked_b}", not bad3b, bad3b[:3])
    # ---- J4 全文走査: 全sidを再生位置に置いて点灯が常にデータ通り(null群は一度も点灯しない) ----
    bad4, nlit, n = [], 0, 0
    for r in sync:
        tt = r["start"] + 0.3 if r["end"] - r["start"] > 0.7 else (r["start"] + r["end"]) / 2
        st = page.evaluate(_SEEK_STATE_JS, tt)
        n += 1
        act = st["eup"].get("active")
        if act is not None and act not in sid2key and st["onJhl"]:
            nlit += 1
        if not _consistent(st, sid2key):
            bad4.append((r["sid"], act, st["onJhl"], st["onSent"]))
    rec("J", pre + f"J4_all_{n}_sentences_state_matches_data", not bad4, bad4[:4])
    rec("J", pre + "M7_null_group_sentences_never_light_ja", nlit == 0 and len(null_sids) >= 0, dict(null_sentences=len(null_sids), lit=nlit))
    # ---- 文と文の間: 同一群の前後なら保持・別群なら消灯 ----
    keep_t = drop_t = None
    for a, b in zip(sync, sync[1:]):
        if b["start"] - a["end"] > 0.2 and keep_t is None and sid2key.get(a["sid"]) and sid2key.get(a["sid"]) == sid2key.get(b["sid"]):
            keep_t = (a["end"] + b["start"]) / 2
        if b["start"] - a["end"] > 0.2 and drop_t is None and sid2key.get(a["sid"]) != sid2key.get(b["sid"]):
            drop_t = (a["end"] + b["start"]) / 2
    if keep_t is not None:
        st = page.evaluate(_SEEK_STATE_JS, keep_t)
        rec("J", pre + "M9_gap_inside_same_group_keeps_ja", st["eup"].get("active") is None and st["onSent"] == [] and len(st["onJhl"]) == 1, dict(t=round(keep_t, 2), onJhl=st["onJhl"]))
    if drop_t is not None:
        st = page.evaluate(_SEEK_STATE_JS, drop_t)
        rec("J", pre + "gap_between_groups_clears_ja", st["eup"].get("active") is None and st["onSent"] == [] and st["onJhl"] == [], dict(t=round(drop_t, 2), onJhl=st["onJhl"]))
    # ---- J5 シーク(#seek 50% / +-10秒)後の同期 ----
    bad5 = []
    page.evaluate("() => { const s=document.getElementById('seek'); s.value=500; s.dispatchEvent(new Event('input',{bubbles:true})); }")
    page.wait_for_timeout(500)
    st = page.evaluate(_STATE_JS)
    if not _consistent(st, sid2key, set(groups)):
        bad5.append(("seekbar50", st["eup"].get("active"), st["onJhl"]))
    for btn in ("fwd10", "back10"):
        page.click("#" + btn)
        page.wait_for_timeout(500)
        st = page.evaluate(_STATE_JS)
        if not _consistent(st, sid2key, set(groups)):
            bad5.append((btn, st["eup"].get("active"), st["onJhl"]))
    rec("J", pre + "J5_seek_and_skip_buttons_sync", not bad5, bad5)
    # ---- 一時停止・再開の状態一致 ----
    first_sid = next((s for s in sids_all if s in sid2key), sids_all[0])   # 連動対象の群が無いlevel(訳の生成が全段落不成立等)でも一時停止/再開の整合を検査する
    page.evaluate("(t) => { document.getElementById('aud').currentTime = t; }", [x for x in sync if x["sid"] == first_sid][0]["start"])
    page.click("#pp")                                  # 再生(2026-10-30: 文クリックでは再生が始まらないため#ppで再生してから一時停止/再開を検査する)
    page.wait_for_timeout(700)
    page.click("#pp")                                  # 一時停止
    page.wait_for_timeout(300)
    s1 = page.evaluate(_STATE_JS)
    page.wait_for_timeout(700)
    s2 = page.evaluate(_STATE_JS)
    page.click("#pp")                                  # 再開
    page.wait_for_timeout(500)
    s3 = page.evaluate(_STATE_JS)
    page.evaluate("document.getElementById('aud').pause()")
    rec("J", pre + "M7_pause_resume_state_consistent",
        s1["onJhl"] == s2["onJhl"] and s1["onSent"] == s2["onSent"] and _consistent(s1, sid2key, set(groups)) and _consistent(s3, sid2key, set(groups)),
        dict(paused=[s1["onSent"], s1["onJhl"]], later=[s2["onSent"], s2["onJhl"]], resumed=[s3["onSent"], s3["onJhl"]]))
    # ---- KPモード(英語音声のみ再生)で誤点灯なし ----
    kb = page.query_selector_all(".kpitem button[data-act=kp]")
    if kb:
        kb[0].scroll_into_view_if_needed()
        kb[0].click()
        page.wait_for_timeout(900)
        st = page.evaluate(_STATE_JS)
        page.evaluate("document.getElementById('aud').pause()")
        rec("J", pre + "M7_kp_mode_no_ja_lit", st["eup"].get("mode") == "kp" and st["onJhl"] == [] and st["onSent"] == [], dict(mode=st["eup"].get("mode"), onJhl=st["onJhl"]))
    # ---- 色・見た目が.sent.onと同一 ----
    same = page.evaluate("""() => { const j=document.querySelector('.jhl'), s=document.querySelector('.sent'); if(!j||!s) return null;
        const f=(e)=>{ e.classList.add('on'); const c=getComputedStyle(e); const r=[c.backgroundColor,c.boxShadow]; e.classList.remove('on'); return r; };
        return [f(j), f(s)]; }""")
    rec("J", pre + "J8_jhl_on_style_equals_sent_on", bool(same) and same[0] == same[1], same)
    # ---- 実再生中の可視性(情報): 再生しながらEN点灯文とJA点灯群が画面内(固定バーより上)にある割合 ----
    n_vis = {"samples": 0, "en_visible": 0, "ja_lit": 0, "ja_lit_and_visible": 0, "en_and_ja_both_visible": 0}
    mid = story[min(1, len(story) - 1)]
    shot_done = False
    page.click(f'[data-part="{mid["idx"]}"] .btns .seek.from')
    for _ in range(18):
        page.wait_for_timeout(600)
        v = page.evaluate("""() => { const bar=document.getElementById('bar').getBoundingClientRect().top;
            const vis=(e)=>{ if(!e) return null; const r=e.getBoundingClientRect(); return r.bottom>0 && r.top<bar; };
            return [vis(document.querySelector('.sent.on')), vis(document.querySelector('.jhl.on'))]; }""")
        if v[0] is None:
            continue
        n_vis["samples"] += 1
        n_vis["en_visible"] += 1 if v[0] else 0
        if v[1] is not None:
            if not shot_done:
                shot(f"{lv}_jhl_lit")             # 日本語群が点灯している瞬間の画面(PC/モバイルでの見え方の確認用)
                shot_done = True
            n_vis["ja_lit"] += 1
            n_vis["ja_lit_and_visible"] += 1 if v[1] else 0
            n_vis["en_and_ja_both_visible"] += 1 if (v[0] and v[1]) else 0
    page.evaluate("document.getElementById('aud').pause()")
    rec("J", pre + "info_visibility_during_playback", True, n_vis)
    # ---- K 英文クリック=選択のみ(ENDUSER-CLICK-HIGHLIGHT-NO-SEEK-01。原文§3 項目1,2,3,6,7) ----
    click_no_seek_checks(page, view, lv, L, sync, rec, sid2key, null_sids)
    # ---- J6 レベル切替で全消灯 + 切替直後のクリック ----
    other = [k for k in (lvs or []) if k != lv]
    if other:
        o = other[0]
        page.click(f"#tabs button[data-lv={o}]")
        page.wait_for_function("(l) => window.__EUP && window.__EUP.level === l && window.__EUP.syncKind === 'real'", arg=o, timeout=15000)
        st = page.evaluate(_STATE_JS)
        rec("J", pre + "J6_level_switch_clears_all", st["onJhl"] == [] and st["onSent"] == [], dict(onJhl=st["onJhl"], onSent=st["onSent"]))
        g2, s2k, _ = expect_maps(art["levels"][o])
        sid2 = next((s["sid"] for pt in art["levels"][o]["parts"] if pt["kind"] == "story" for pa in pt.get("paragraphs", []) for s in pa if s["sid"] in s2k), None)
        if sid2:
            _click_sent(page, view, sid2)
            page.wait_for_timeout(450)
            st = page.evaluate(_STATE_JS)
            page.evaluate("document.getElementById('aud').pause()")
            rec("J", pre + "M7_click_right_after_level_switch", _consistent(st, s2k), dict(sid=sid2, active=st["eup"].get("active"), onJhl=st["onJhl"]))


if __name__ == "__main__":
    import sys
    print("このmoduleはer135_enduser_page_01.py verify-only から呼ぶ", file=sys.stderr)

# -*- coding: utf-8 -*-
"""END-USER-LISTENING-PAGE-PRODUCTION-WIRING-01 委任_02B: End Userページのブラウザ検証CLI(Playwright。API 0)。

記事非依存(公開dirの`enduser/data/article.json`・`sync_<lv>.json`から期待値を作る)。検査内容はDEV rev01-eの検証(ハイライト追従・文クリック再生・シーク・
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
def run(public_dir, base_url=None, out=None, shots=None) -> int:
    from playwright.sync_api import sync_playwright
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
        rec("C", pre + "translation_blocks_equal_approved_data", len(got) == len(want_ja) and all(g["src"] in ("approved_ja_manuscript", "approved_ja_original_in_dev_page") and g["after"] for g in got), dict(want=len(want_ja), got=len(got)))
        no_ja_en = [pt for pt in parts if pt["kind"] in ("comment", "story", "oneline") and not pt.get("ja")]
        leaked = page.evaluate("(idxs) => idxs.filter(i => { const b=document.querySelector('[data-part=\"'+i+'\"].partblock, [data-part=\"'+i+'\"].comment'); return b && b.querySelector('.tr'); })", [pt["idx"] for pt in no_ja_en])
        rec("C", pre + "blocks_without_approved_translation_show_none", not leaked, leaked)
        # ---- D 学習コーナー(0件は見出し・枠ごと非表示/順序) ----
        h2 = page.evaluate("() => [...document.querySelectorAll('.card h2')].map(h => h.textContent)")
        expect = [("vocab", "Vocabulary & Expressions", "vocab"), ("grammar", "Grammar & Sentence Structure", "grammar"), ("nuance", "ニュアンス解説", "nuance")]
        for key, head, elid in expect:
            n = len(L[key])
            present = page.evaluate("(i) => !!document.getElementById(i)", elid)
            rec("D", pre + f"{key}_corner_{'shown' if n else 'hidden'}", present == bool(n) and ((head in h2) == bool(n)), dict(items=n, present=present))
        order = [h for h in h2 if h in ("Full Story", "Vocabulary & Expressions", "Grammar & Sentence Structure", "ニュアンス解説")]
        want_order = ["Full Story"] + [h for k, h, _ in expect if L[k]]
        rec("D", pre + "corner_order", order == want_order, order)
        empty = page.evaluate("() => [...document.querySelectorAll('.card')].filter(c => !c.querySelector('p,dl,ul,div.kp,details,.partblock,.comment,.subblk,.kpitem')).length")
        rec("D", pre + "no_empty_cards", empty == 0, empty)
        cnt = page.evaluate("() => ({vocab: document.querySelectorAll('#vocab details.vi').length, grammar: document.querySelectorAll('#grammar .gr').length, nuance: document.querySelectorAll('#nuance .gr').length})")
        rec("D", pre + "corner_item_counts_equal_data", cnt == {"vocab": len(L["vocab"]), "grammar": len(L["grammar"]), "nuance": len(L["nuance"])}, cnt)
        # ---- E 引用英文の太字 ----
        emph = page.evaluate("() => window.__EMPH")
        zero = [x["heading"] for k in ("vocab", "nuance") for x in emph[k] if not x["bold"]]
        rec("E", pre + "vocab_nuance_quotes_have_bold", not zero, dict(zero=zero[:5]))
        rec("E", pre + "no_bold_in_transcript_or_gloss", page.evaluate("() => document.querySelectorAll('.sent .target-term, .gloss .target-term, .tr .target-term, .kpitem .target-term').length") == 0, None)
        rec("E", pre + "bold_only_in_quote_dd", page.evaluate("() => [...document.querySelectorAll('strong.target-term')].every(s => { const dd=s.closest('dd'); const dt=dd&&dd.previousElementSibling; return !!dt && ['本文の英文','対象となる本文英文'].includes(dt.textContent); })"), None)
        bad_q = []
        for kind, sel, lab in (("vocab", "#vocab details.vi", "本文の英文"), ("nuance", "#nuance .gr", "本文の英文"), ("grammar", "#grammar .gr", "対象となる本文英文")):
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
            page.click(f'[data-sid="{sid}"]')
            page.wait_for_timeout(1500)
            s = A()
            exp = [x for x in sync if x["sid"] == sid][0]
            rec("F", pre + "sentence_click_plays_from_sentence", (not s["paused"]) and exp["start"] - 0.6 <= s["eup"]["gt"] <= exp["end"] + 2.0, dict(sid=sid, gt=s["eup"]["gt"], exp=[exp["start"], exp["end"]], act=s["eup"]["active"]))
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
            page.evaluate("(t) => { const a=document.getElementById('aud'); a.currentTime=t; a.play(); }", b_["start"] - 2.5)
            try:
                page.wait_for_function("(t) => window.__EUP && window.__EUP.gt > t + 1.0 && !document.getElementById('aud').paused", arg=b_["start"], timeout=12000)
            except Exception:
                pass
            s = A()
            rec("G", pre + "continues_across_part_boundary", (not s["paused"]) and s["eup"]["gt"] > b_["start"] + 0.9 and s["eup"]["mode"] == "full", dict(from_=a_["label"], to=b_["label"], gt=s["eup"]["gt"], boundary=b_["start"]))
            act = s["eup"]["active"]
            nxt = [x["sid"] for pa in b_["paragraphs"] for x in pa]
            rec("G", pre + "highlight_moves_into_next_part", bool(act) and act in nxt, dict(active=act, part=b_["label"]))
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
                page.wait_for_timeout(700)
                r_ = page.evaluate("(href) => { const t=document.getElementById(href.slice(1)); if(!t) return null; const b=t.getBoundingClientRect(); return {top:b.top, open:t.open, head:t.querySelector('.vh').textContent, vh:innerHeight}; }", href)
                if not r_ or r_["head"] != en or not r_["open"] or not (-5 <= r_["top"] <= r_["vh"] * 0.8):
                    badl.append((en, href, r_))
            rec("I", pre + "glossary_links_open_the_expression", not badl, badl[:2])
        else:
            rec("I", pre + "no_glossary_when_not_applicable", page.evaluate("() => document.querySelectorAll('.gloss').length") == 0, None)
        # ---- J 画面の目視用shots ----
        open_lv(lv)
        shot(f"{lv}_top")
        shot(f"{lv}_fullstory", "#fullstory")
        for corner in ("vocab", "grammar", "nuance"):
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


if __name__ == "__main__":
    import sys
    print("このmoduleはer135_enduser_page_01.py verify-only から呼ぶ", file=sys.stderr)

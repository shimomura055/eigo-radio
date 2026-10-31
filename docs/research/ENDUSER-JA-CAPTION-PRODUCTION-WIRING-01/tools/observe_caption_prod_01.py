"""ENDUSER-JA-CAPTION-PRODUCTION-WIRING-01: rev01-iページの§4-1全項目をPlaywrightで観測(PC 1280x900 / スマホ 390x844 + 狭幅 320x640)。API 0。
使い方: python observe_caption_prod_01.py <tree_dir> <out_dir> [--base-url URL] [--dirs a,b,c]
  <tree_dir>配下の<dir>/enduser/index.html?lv=std|adv を観測。--base-url指定時は<base>/<dir>/enduser/index.html(公開URL検証用)。"""
import argparse, functools, json, socketserver, sys, threading
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
import er135_enduser_page_verify_01 as V   # Range対応ローカルサーバ・UAを再利用
import sys as _pws_sys, pathlib as _pws_p; _pws_sys.path.insert(0, str(next(_q for _q in _pws_p.Path(__file__).resolve().parents if (_q / "tools" / "playwright_safe_01.py").exists()) / "tools")); from playwright_safe_01 import sync_playwright  # PLAYWRIGHT-AUDIO-SAFETY-01: 無音+終了保証+hard timeout

ap = argparse.ArgumentParser()
ap.add_argument("tree"); ap.add_argument("out"); ap.add_argument("--base-url"); ap.add_argument("--dirs"); ap.add_argument("--no-shots", action="store_true")
ap.add_argument("--browser", default="chromium", choices=["chromium", "webkit"]); ap.add_argument("--views"); ap.add_argument("--levels", default="std,adv")
ap.add_argument("--hard-timeout-s", type=float, default=1800.0, help="全体のhard timeout秒(超過でbrowserをkillしrc=124。PLAYWRIGHT-AUDIO-SAFETY-01)")
a = ap.parse_args()
out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
DIRS = (a.dirs.split(",") if a.dirs else ["family_x_meta_waddle_world_01", "family_y_production_surname_choice_01", "family_z_melos_kphr_evidence_r3"])
VIEWS = {"pc": dict(viewport={"width": 1280, "height": 900}),
         "mobile": dict(viewport={"width": 390, "height": 844}, user_agent=V.UA, device_scale_factor=2, is_mobile=True, has_touch=True),
         "narrow": dict(viewport={"width": 320, "height": 640}, user_agent=V.UA, device_scale_factor=2, is_mobile=True, has_touch=True)}

SAMPLE = """() => { const e = window.__EUP || {}; const on = Array.from(document.querySelectorAll('.jhl.on')).map(x => x.textContent).join('');
 const cap = document.getElementById('jcapT').textContent; const A = document.getElementById('aud'); const b = document.getElementById('bar').getBoundingClientRect();
 return {cap, on, ok: cap === on, paused: A.paused, t: A.currentTime, mode: e.mode, sel: e.sel, barH: Math.round(b.height * 10) / 10, gap: Math.round((innerHeight - b.bottom) * 10) / 10, scrollH: document.documentElement.scrollHeight}; }"""
LAYOUT = """() => { const g = id => document.getElementById(id).getBoundingClientRect(); const cs = getComputedStyle(document.body);
 const bar = g('bar'), cap = document.getElementById('jcap'), cr = cap.getBoundingClientRect(), r2 = document.querySelector('.row2').getBoundingClientRect(), pp = g('pp'), tg = g('capToggle');
 const vw = document.documentElement.clientWidth;
 return {on: document.body.classList.contains('capon'), off: document.body.classList.contains('capoff'), jcapDisplay: getComputedStyle(cap).display, jcapH: Math.round(cr.height), barH: Math.round(bar.height*10)/10,
  bodyPadBottom: parseFloat(cs.paddingBottom), padMinusBar: Math.round((parseFloat(cs.paddingBottom) - bar.height)*10)/10, toggleText: document.getElementById('capToggle').textContent, toggleAria: document.getElementById('capToggle').getAttribute('aria-pressed'),
  toggleW: Math.round(tg.width), toggleH: Math.round(tg.height), toggleInViewport: tg.left >= 0 && tg.right <= vw && tg.bottom <= innerHeight,
  jcapBelowRow2: cr.height === 0 || cr.top >= r2.bottom - 0.5, jcapOverlapPP: cr.height > 0 && !(cr.top >= pp.bottom || cr.bottom <= pp.top), row2Overflow: document.querySelector('.row2').scrollWidth > document.querySelector('.row2').clientWidth + 1,
  hScroll: document.documentElement.scrollWidth > vw + 1, nowLabel: document.getElementById('nowLabel').textContent, nowLabelTrunc: document.getElementById('nowLabel').scrollWidth > document.getElementById('nowLabel').clientWidth + 1, nowLabelW: Math.round(document.getElementById('nowLabel').clientWidth), jcapHOverflow: cap.scrollWidth > cap.clientWidth + 1, jcapScrollable: cap.scrollHeight > cap.clientHeight + 1, barTop: Math.round(bar.top), vh: innerHeight, vw}; }"""
CLICK = "(sid) => { const s = document.querySelector('[data-sid=\"'+sid+'\"]'); s.scrollIntoView({block:'center'}); s.click(); }"


def run_view(p, view, opts, base, d, lv, R, shots):
    br = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"]) if a.browser == "chromium" else p.webkit.launch()
    try:
        _run_view_body(p, br, view, opts, base, d, lv, R, shots)
    finally:
        try:
            br.close()
        except Exception:
            pass


def _run_view_body(p, br, view, opts, base, d, lv, R, shots):
    ctx = br.new_context(**opts); page = ctx.new_page()
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)))
    page.on("console", lambda m: errs.append("console:" + m.text) if m.type == "error" else None)
    page.on("response", lambda r: errs.append(f"http{r.status}:{r.url}") if r.status >= 400 else None)
    url = f"{base}/{d}/enduser/index.html?lv={lv}"
    page.goto(url); page.wait_for_function("window.__EUP && window.__EUP.syncKind==='real'", timeout=30000); page.wait_for_timeout(500)
    res = {"url": url, "browser": a.browser, "view": view}; chk = {}
    res["build_id"] = page.evaluate("() => (document.querySelector('meta[name=build-id]') || {}).content || null"); chk["build_id_is_rev01i"] = res["build_id"] == "rev01-i"
    art = page.evaluate("(u) => fetch(u + '?cb=' + Date.now()).then(r => r.json())", f"{base}/{d}/enduser/data/article.json"); EXP = V.caption_expected(art["levels"][lv])
    res["nowlabel_states"] = []
    sh = lambda n: (None if a.no_shots else page.screenshot(path=str(shots / f"{d[:10]}_{lv}_{view}_{n}.png")))
    sh("01_initial")
    L0 = page.evaluate(LAYOUT); res["initial"] = L0
    chk["initial_ON"] = L0["on"] and not L0["off"] and L0["jcapDisplay"] == "block" and L0["toggleText"].endswith("ON") and L0["toggleAria"] == "true"
    chk["toggle_size_ok"] = L0["toggleH"] >= 36 and L0["toggleW"] >= 64 and L0["toggleInViewport"]
    chk["now_label_initial_not_truncated"] = not L0["nowLabelTrunc"]   # 追加ボタンで既存ラベル(全体)が潰れない
    chk["layout_ok_ON"] = L0["jcapBelowRow2"] and not L0["jcapOverlapPP"] and not L0["row2Overflow"] and not L0["hScroll"] and L0["barTop"] > 0
    info = page.evaluate("""() => { const A = document.getElementById('aud'); const t0 = A.currentTime; const rows = [];
      document.querySelectorAll('.sent').forEach(s => { s.click(); const cap = document.getElementById('jcapT').textContent; const on = Array.from(document.querySelectorAll('.jhl.on')).map(x => x.textContent).join('');
        rows.push({sid: s.dataset.sid, cap, on, barH: Math.round(document.getElementById('bar').getBoundingClientRect().height * 10) / 10, scr: document.getElementById('jcap').scrollHeight, cli: document.getElementById('jcap').clientHeight, two: (() => { const q = getComputedStyle(document.getElementById('jcap')); return 2 * parseFloat(q.lineHeight) + parseFloat(q.paddingTop) + parseFloat(q.paddingBottom) + parseFloat(q.borderTopWidth) + parseFloat(q.borderBottomWidth); })()}); });
      return {rows, played: !A.paused, moved: Math.abs(A.currentTime - t0) > 0.05}; }""")
    rows = info["rows"]; withcap = [r for r in rows if r["cap"]]; nocap = [r for r in rows if not r["cap"]]
    res["sentences"] = len(rows); res["with_caption"] = len(withcap); res["without_caption"] = len(nocap)
    chk["click_no_play_no_seek"] = (not info["played"]) and (not info["moved"])
    chk["click_cap_equals_jhl_on"] = all(r["cap"] == r["on"] for r in rows)
    chk["caption_equals_ja_align_expected_for_every_sentence"] = bool(rows) and all(r["cap"] == EXP.get(r["sid"], "") for r in rows)   # 期待値=ja_align由来(群なしsid・g.ja==null・ja無しpart・degraded=空欄)
    res["expected_blank_sentences"] = sum(1 for r in rows if EXP.get(r["sid"], "") == ""); res["expected_nonblank_sentences"] = sum(1 for r in rows if EXP.get(r["sid"], ""))
    fit = [r for r in rows if r["scr"] <= r["two"] + 1]
    chk["bar_height_constant_0_to_2_lines"] = bool(fit) and all(abs(r["barH"] - L0["barH"]) <= 0.6 for r in fit); res["bar_rows"] = dict(fit=len(fit), over2=len(rows) - len(fit), base=L0["barH"])
    if withcap:
        mid = withcap[len(withcap) // 2]
        page.evaluate(CLICK, mid["sid"]); page.wait_for_timeout(250)
        sh("02_selected_ON")
        S0 = page.evaluate(SAMPLE)
        page.click("#capToggle"); page.wait_for_timeout(250)
        L1 = page.evaluate(LAYOUT); S1 = page.evaluate(SAMPLE); sh("03_OFF"); res["off"] = L1
        chk["OFF_hidden_and_area_freed"] = L1["off"] and L1["jcapDisplay"] == "none" and L1["jcapH"] == 0 and L1["barH"] < L0["barH"] - 40 and L1["toggleText"].endswith("OFF") and L1["toggleAria"] == "false"
        chk["OFF_no_extra_margin"] = abs(L1["padMinusBar"] - 24) <= 12
        chk["OFF_url_param"] = "caption=0" in page.url
        chk["toggle_keeps_state"] = (S1["paused"] == S0["paused"]) and abs(S1["t"] - S0["t"]) < 0.05 and S1["sel"] == S0["sel"]
        page.click("#capToggle"); page.wait_for_timeout(250)
        L2 = page.evaluate(LAYOUT); S2 = page.evaluate(SAMPLE); sh("04_ON_again")
        chk["ON_again_clears_caption_param"] = "caption" not in page.url and abs(S2["barH"] - S0["barH"]) <= 0.6   # 同じキャプション(OFF前と同じ文)ならバー高さも戻る
        chk["ON_again_shows_current_ja"] = L2["on"] and S2["cap"] == mid["cap"] and S2["cap"] != "" and L2["bodyPadBottom"] >= L2["barH"]
        longest = max(withcap, key=lambda r: len(r["cap"]))
        page.evaluate(CLICK, longest["sid"]); page.wait_for_timeout(250)
        LL = page.evaluate(LAYOUT); sh("05_long_caption")
        res["longest"] = {"len": len(longest["cap"]), **{k: LL[k] for k in ("jcapH", "barH", "jcapHOverflow", "jcapScrollable", "hScroll", "barTop")}}
        chk["long_caption_ok"] = (not LL["jcapHOverflow"]) and (not LL["hScroll"]) and LL["barTop"] > 100 and LL["jcapBelowRow2"] and LL["bodyPadBottom"] >= LL["barH"] and not LL["row2Overflow"]   # 長文でも本文末尾がバーに隠れない(body padding-bottom >= バー高さ)・横はみ出し無し
        sync = page.evaluate("(u) => fetch(u).then(r => r.json())", f"{base}/{d}/enduser/data/sync_{lv}.json")
        ss = sync["sentences"] if "sentences" in sync else sync
        sidcap = {r["sid"] for r in withcap}
        target = next((s for s in ss if s["sid"] in sidcap and s["start"] > 1), None)
        if target:
            page.evaluate("(t) => { const A = document.getElementById('aud'); A.currentTime = Math.max(0, t - 0.4); A.play().catch(() => {}); }", target["start"]); page.wait_for_timeout(1200)   # play()のAbortError(WebKitでsrc切替中に起きる検査側の拒否)を未処理にしない
            if page.evaluate("() => document.getElementById('aud').paused"):   # 再生が始まらなかった場合は1回だけ再試行(検査側の起動競合。製品のplayNowはAbortErrorを握りつぶす=app.js playNow)
                page.evaluate("() => document.getElementById('aud').play().catch(() => {})"); page.wait_for_timeout(1200)
            sh("06_playing"); res["nowlabel_states"].append(dict(state="playing", **{k: page.evaluate(LAYOUT)[k] for k in ("nowLabel", "nowLabelTrunc", "nowLabelW")}))
            samples = []
            for _ in range(80):
                samples.append(page.evaluate(SAMPLE)); page.wait_for_timeout(100)
            caps = [s["cap"] for s in samples]
            res["playing_8s"] = {"samples": len(samples), "mismatch": sum(1 for s in samples if not s["ok"]), "cap_changes": sum(1 for i in range(1, len(caps)) if caps[i] != caps[i-1]),
                                 "barH_values": sorted(set(s["barH"] for s in samples)), "scrollH_values": sorted(set(s["scrollH"] for s in samples)), "all_playing": all(not s["paused"] for s in samples)}
            chk["playing_cap_equals_jhl_on"] = res["playing_8s"]["mismatch"] == 0 and res["playing_8s"]["cap_changes"] >= 1
            res["playing_8s"]["bar_bottom_gap_values"] = sorted(set(s["gap"] for s in samples)); chk["bar_at_viewport_bottom_while_playing"] = res["playing_8s"]["bar_bottom_gap_values"] == [0.0]
            chk["playing_content_no_reflow"] = len(res["playing_8s"]["scrollH_values"]) == 1   # 本文(documentの高さ)は再生中に動かない。バー高さ変動(OBS)はTrialと同一の固定バー上端の移動のみ
            res["OBS_bar_height_varies_with_caption_lines"] = res["playing_8s"]["barH_values"]
            T0 = page.evaluate(SAMPLE); page.click("#capToggle"); page.wait_for_timeout(300); T1 = page.evaluate(SAMPLE); page.click("#capToggle"); page.wait_for_timeout(300); T2 = page.evaluate(SAMPLE)
            chk["toggle_while_playing_keeps_playback"] = (not T0["paused"]) and (not T1["paused"]) and (not T2["paused"]) and 0.2 < T1["t"] - T0["t"] < 1.5 and 0.2 < T2["t"] - T1["t"] < 1.5 and T2["ok"]
            tb = page.evaluate("() => document.getElementById('aud').currentTime")
            page.evaluate("() => { const s = document.querySelectorAll('.sent'); s[s.length - 1].click(); }"); page.wait_for_timeout(200)
            ta = page.evaluate("() => document.getElementById('aud').currentTime"); Sx = page.evaluate(SAMPLE)
            chk["click_while_playing_no_seek"] = 0 <= ta - tb < 0.6 and not Sx["paused"] and Sx["ok"]
            page.click("#pp"); page.wait_for_timeout(300); P1 = page.evaluate(SAMPLE); page.wait_for_timeout(500); P2 = page.evaluate(SAMPLE)
            chk["pause_keeps_caption"] = P1["paused"] and P1["cap"] == P2["cap"] and P2["ok"]
            page.evaluate(CLICK, mid["sid"]); page.wait_for_timeout(250)
            P3 = page.evaluate(SAMPLE); chk["paused_click_select"] = P3["paused"] and abs(P3["t"] - P2["t"]) < 0.05 and P3["cap"] == mid["cap"]
            page.click("#pp"); page.wait_for_timeout(500)
            fs = []
            page.click("#fwd10")
            for _ in range(15):
                fs.append(page.evaluate(SAMPLE)); page.wait_for_timeout(100)
            page.click("#back10")
            for _ in range(15):
                fs.append(page.evaluate(SAMPLE)); page.wait_for_timeout(100)
            page.evaluate("() => { const sk = document.getElementById('seek'); sk.value = 600; sk.dispatchEvent(new Event('input', {bubbles:true})); }")
            for _ in range(20):
                fs.append(page.evaluate(SAMPLE)); page.wait_for_timeout(100)
            chk["seek_pm10_cap_equals_jhl_on"] = all(s["ok"] for s in fs)
            res["seek_samples"] = len(fs)
            hb = page.query_selector_all("button[data-act=full]")
            if len(hb) > 2:
                hb[2].scroll_into_view_if_needed(); hb[2].click()
                hs = []
                for _ in range(25):
                    hs.append(page.evaluate(SAMPLE)); page.wait_for_timeout(100)
                chk["from_here_cap_equals_jhl_on"] = all(s["ok"] for s in hs) and not hs[-1]["paused"]
            for nm, sel in (("kp", "button[data-act=kp]"), ("vocab", "button[data-act=vocab]")):
                els = page.query_selector_all(sel)
                if not els:
                    chk[f"{nm}_cap_consistent"] = "N/A(該当ボタンなし: そのレベルに項目が無い)"; continue
                els[0].scroll_into_view_if_needed(); els[0].click(); ks = []
                for _ in range(25):
                    ks.append(page.evaluate(SAMPLE)); page.wait_for_timeout(100)
                chk[f"{nm}_cap_consistent"] = all(s["ok"] for s in ks) and any(s["mode"] == nm for s in ks)
                chk[f"{nm}_cap_blank_while_playing_clip"] = all(s["cap"] == "" for s in ks if s["mode"] == nm)
                res["nowlabel_states"].append(dict(state=nm + "_playing", **{k: page.evaluate(LAYOUT)[k] for k in ("nowLabel", "nowLabelTrunc", "nowLabelW")}))
                res[f"{nm}_play"] = {"modes": sorted(set(str(s["mode"]) for s in ks)), "caps_nonempty": sum(1 for s in ks if s["cap"])}
            page.evaluate("() => document.getElementById('aud').pause()")
    sh("07_end")
    page.goto(f"{base}/{d}/enduser/index.html?lv={lv}&caption=0"); page.wait_for_function("window.__EUP && window.__EUP.syncKind==='real'", timeout=30000)
    R0 = page.evaluate(LAYOUT); chk["reload_caption0_stays_OFF"] = R0["off"] and R0["jcapDisplay"] == "none" and R0["toggleText"].endswith("OFF")
    other = "adv" if lv == "std" else "std"
    page.click(f"#tabs button[data-lv={other}]"); page.wait_for_timeout(500)
    R1 = page.evaluate(LAYOUT); chk["level_switch_keeps_OFF"] = R1["off"] and "caption=0" in page.url and f"lv={other}" in page.url
    page.click("#capToggle"); page.wait_for_timeout(200); page.click(f"#tabs button[data-lv={lv}]"); page.wait_for_timeout(500)
    R2 = page.evaluate(LAYOUT); chk["level_switch_keeps_ON"] = R2["on"] and R2["jcapDisplay"] == "block"
    sh("08_after_level_switch")
    res["errors"] = errs; chk["no_console_or_http_errors"] = not errs
    res["checks"] = chk; R[f"{view}:{d}:{lv}"] = res
    ctx.close()


def main():
    srv = None
    if a.base_url:
        base = a.base_url.rstrip("/")
    else:
        h = functools.partial(V._Handler, directory=str(Path(a.tree).resolve()))
        srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), h); srv.daemon_threads = True
        threading.Thread(target=srv.serve_forever, daemon=True).start(); base = f"http://127.0.0.1:{srv.server_address[1]}"
    R = {}; shots = out / "shots"; shots.mkdir(exist_ok=True)
    try:
        with sync_playwright(hard_timeout_s=a.hard_timeout_s) as p:
            for view, opts in VIEWS.items():
                if a.views and view not in a.views.split(","):
                    continue
                for d in DIRS:
                    for lv in a.levels.split(","):
                        run_view(p, view, opts, base, d, lv, R, shots)
    finally:
        if srv:
            srv.shutdown()
    (out / "observe.json").write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")
    ng = {k: [c for c, v in r["checks"].items() if v is not True and not str(v).startswith("N/A")] for k, r in R.items()}
    for k, v in ng.items():
        print(k, "PASS" if not v else f"NG/other: {v}")
    sys.exit(0 if all(not v for v in ng.values()) else 1)


main()

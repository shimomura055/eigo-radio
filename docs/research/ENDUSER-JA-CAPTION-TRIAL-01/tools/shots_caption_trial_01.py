"""ENDUSER-JA-CAPTION-TRIAL-01: Trialページのスクリーンショットと挙動観察(PC 1280 / スマホ 390)。
使い方: py -3.14 shots_caption_trial_01.py <base_url> <out_dir> [pages=x_adv,y_adv,z_adv,x_std,y_std,z_std]"""
import json, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
VIEWS = {"pc": dict(viewport={"width": 1280, "height": 900}),
         "mobile": dict(viewport={"width": 390, "height": 844}, user_agent=UA, device_scale_factor=2, is_mobile=True, has_touch=True)}
base, out = sys.argv[1].rstrip("/"), Path(sys.argv[2])
pages = (sys.argv[3] if len(sys.argv) > 3 else "x_adv,y_adv,z_adv,x_std,y_std,z_std").split(",")
out.mkdir(parents=True, exist_ok=True)
R = {}

SAMPLE = """() => { const e = window.__EUP || {}; const on = Array.from(document.querySelectorAll('.jhl.on')).map(x => x.textContent).join('');
  const cap = document.getElementById('jcapT').textContent; const A = document.getElementById('aud');
  return {jg: e.jg, cap, on, ok: cap === on, paused: A.paused, t: A.currentTime, mode: e.mode, sel: e.sel}; }"""


def sample_run(page, ms, step=80):
    rows = []
    t0 = time.time()
    while (time.time() - t0) * 1000 < ms:
        rows.append(page.evaluate(SAMPLE))
        page.wait_for_timeout(step)
    return rows


def summarize(rows):
    caps = [r["cap"] for r in rows]
    changes = sum(1 for i in range(1, len(caps)) if caps[i] != caps[i - 1])
    return {"samples": len(rows), "mismatch": sum(1 for r in rows if not r["ok"]), "cap_changes": changes,
            "distinct_caps": len(set(c for c in caps if c)), "empty_samples": sum(1 for c in caps if not c)}


with sync_playwright() as p:
    for view, opts in VIEWS.items():
        br = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
        for pg in pages:
            ctx = br.new_context(**opts)
            page = ctx.new_page()
            errs = []
            page.on("pageerror", lambda e: errs.append(str(e)))
            page.on("console", lambda m: errs.append("console:" + m.text) if m.type == "error" else None)
            url = f"{base}/user_test/enduser_caption_trial_01/{pg}/index.html"
            page.goto(url)
            page.wait_for_function("window.__EUP && window.__EUP.syncKind==='real'", timeout=30000)
            page.wait_for_timeout(500)
            res = {"url": url}
            sh = lambda n: page.screenshot(path=str(out / f"{pg}_{view}_{n}.png"))
            sh("01_initial_stopped")
            # 各英文を順にクリックして キャプション有無/テキストを収集(停止中・選択のみ)
            info = page.evaluate("""() => { const A = document.getElementById('aud'); const t0 = A.currentTime; const rows = [];
              document.querySelectorAll('.sent').forEach(s => { s.click(); const cap = document.getElementById('jcapT').textContent;
                const part = s.closest('[data-part]'); rows.push({sid: s.dataset.sid, part: part ? part.dataset.part : null, cap, jg: (window.__EUP || {}).jg}); });
              return {rows, played: !A.paused, t_moved: Math.abs(A.currentTime - t0) > 0.05}; }""")
            rows = info["rows"]
            withcap = [r for r in rows if r["cap"]]
            nocap = [r for r in rows if not r["cap"]]
            res["sentences"] = len(rows); res["with_caption"] = len(withcap); res["without_caption"] = len(nocap)
            res["click_played_or_sought"] = info["played"] or info["t_moved"]
            # 日本語パートを持たない英文(captionなし) / 長文 / 通常 の各クリック選択
            def click_shot(sid, name):
                page.evaluate("(sid) => { const s = document.querySelector('[data-sid=\"'+sid+'\"]'); s.scrollIntoView({block:'center'}); s.click(); }", sid)
                page.wait_for_timeout(250)
                sh(name)
                return page.evaluate(SAMPLE)
            if withcap:
                longest = max(withcap, key=lambda r: len(r["cap"]))
                mid = withcap[len(withcap) // 2]
                res["select_normal"] = click_shot(mid["sid"], "02_click_selected")
                res["select_long"] = click_shot(longest["sid"], "05_long_caption")
                res["longest_len"] = len(longest["cap"])
                cl = page.evaluate("() => { const c = document.getElementById('jcap'); const r = c.getBoundingClientRect(); return {h: r.height, sh: c.scrollHeight, bar: document.getElementById('bar').getBoundingClientRect().height}; }")
                res["caption_box"] = cl
            if nocap:
                res["select_nocap"] = click_shot(nocap[0]["sid"], "04_no_ja_part")
            # 再生中: 日本語あり英文の開始から再生し、キャプション=点灯日本語 の一致とちらつきを観察
            sync = page.evaluate("() => fetch(SRC_URL).then(r => r.json())".replace("SRC_URL", json.dumps(url.rsplit('/', 1)[0] + "/../../" + {"x": "family_x_meta_waddle_world_01", "y": "family_y_production_surname_choice_01", "z": "family_z_melos_kphr_evidence_r3"}[pg[0]] + "/enduser/data/sync_" + pg.split("_")[1] + ".json")))
            ss = sync["sentences"] if "sentences" in sync else sync
            sidcap = {r["sid"]: r["cap"] for r in withcap}
            target = next((s for s in ss if s["sid"] in sidcap and s["start"] > 1), None)
            if target:
                page.evaluate("(t) => { const A = document.getElementById('aud'); document.getElementById('seek').value = 0; A.currentTime = Math.max(0, t - 0.4); A.play(); }", target["start"])
                page.wait_for_timeout(1500)
                sh("03_playing")
                r1 = sample_run(page, 12000)
                res["playing_12s"] = summarize(r1)
                # 一時停止
                page.click("#pp"); page.wait_for_timeout(300)
                a = page.evaluate(SAMPLE); page.wait_for_timeout(600); b = page.evaluate(SAMPLE)
                sh("06_paused")
                res["pause_keeps_caption"] = {"a": a["cap"] == b["cap"], "paused": b["paused"], "cap_nonempty": bool(b["cap"]) or None}
                # +10秒/-10秒/シーク(再生しながら)
                page.click("#pp"); page.wait_for_timeout(500)
                page.click("#fwd10"); page.wait_for_timeout(400); s_f = sample_run(page, 1500)
                page.click("#back10"); page.wait_for_timeout(100); s_b = sample_run(page, 1500)
                page.evaluate("() => { const sk = document.getElementById('seek'); sk.value = 600; sk.dispatchEvent(new Event('input', {bubbles:true})); }")
                s_s = sample_run(page, 2000)
                sh("07_after_seek")
                res["fwd10"] = summarize(s_f); res["back10"] = summarize(s_b); res["seek"] = summarize(s_s)
                # 一時停止中のシーク(停止中) -> キャプション=その時点点灯
                page.click("#pp"); page.wait_for_timeout(300)
                page.evaluate("() => { const sk = document.getElementById('seek'); sk.value = 300; sk.dispatchEvent(new Event('input', {bubbles:true})); }")
                page.wait_for_timeout(400)
                res["paused_seek"] = page.evaluate(SAMPLE)
            # KP再生(Key Phrase単独再生)でも破綻しないか
            kp = page.query_selector("[data-kp-play], .kpplay, button[data-act='kp']")
            kpb = page.evaluate("() => Array.from(document.querySelectorAll('button')).filter(b => /Key|再生/.test(b.textContent + (b.getAttribute('aria-label')||'')) && b.closest('.kp')).length")
            if kpb:
                page.evaluate("() => { const b = Array.from(document.querySelectorAll('button')).filter(b => b.closest('.kp'))[0]; b.click(); }")
                page.wait_for_timeout(300)
                rk = sample_run(page, 3000)
                res["kp_play"] = summarize(rk) | {"mode": rk[-1]["mode"]}
                sh("08_kp_play")
            # ON/OFF切替
            page.click("#capToggle"); page.wait_for_timeout(200)
            res["toggle_off"] = {"cap_visible": page.evaluate("() => getComputedStyle(document.getElementById('jcap')).display !== 'none'"), "url": page.url}
            sh("09_caption_off")
            res["errors"] = errs
            R[f"{view}:{pg}"] = res
            ctx.close()
        br.close()
(out / "observe.json").write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({k: {kk: v[kk] for kk in ("sentences", "with_caption", "without_caption", "click_played_or_sought", "playing_12s", "fwd10", "back10", "seek", "kp_play", "errors") if kk in v} for k, v in R.items()}, ensure_ascii=False, indent=1))

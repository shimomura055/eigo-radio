# -*- coding: utf-8 -*-
"""委任_05: 公開Pages上のStd試聴確認ページのPlaywright実再生evidence(API 0)。"""
import json, sys
from playwright.sync_api import sync_playwright
URL, OUT = sys.argv[1], sys.argv[2]
EXP = json.load(open("docs/research/FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01/std_preview_manifest_01.json", encoding="utf-8"))
out = {"url": URL}
with sync_playwright() as p:
    br = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"])
    pg = br.new_page(); errs, bad = [], []
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("response", lambda r: bad.append((r.url, r.status)) if r.status >= 400 else None)
    resp = pg.goto(URL, wait_until="networkidle")
    body = pg.inner_text("body")
    out["http"] = resp.status
    out["audio_ids"] = pg.eval_on_selector_all("audio", "els=>els.map(e=>e.id)")
    for kw in ("ASR", "M3", "Gate", "sha", "fallback", "Fallback", "gemini", "tts"):
        out.setdefault("tech_words_in_visible_text", {})[kw] = kw in body
    out["highlight_target_present"] = pg.locator(".blk.target").count() == 1 and "ここが確認対象" in body
    out["req_text_present"] = "Full Story第2部のみ、通常と異なる音声生成Styleを使用しています。全体を聴いて、第1部・第3部と比べて声の調子・話し方に違和感がないか確認してください。" in body
    res = pg.evaluate("""async () => {
      const out = {};
      const ld = a => new Promise(r => { if (a.readyState >= 1) r(); else { a.addEventListener('loadedmetadata', r, {once:true}); a.addEventListener('error', r, {once:true}); a.load(); } });
      const sleep = ms => new Promise(r => setTimeout(r, ms));
      for (const id of ['main','p1','p2','p3']) {
        const a = document.getElementById(id); a.muted = true; await ld(a);
        const o = {duration: a.duration, err: a.error ? a.error.code : null};
        if (!a.error) { await a.play(); const t0 = a.currentTime; await sleep(1500); o.advanced = a.currentTime > t0 + 0.8;
          const tgt = a.duration - 3; a.currentTime = tgt; await sleep(500); o.seek_ok = Math.abs(a.currentTime - tgt) < 2.5;
          const ended = new Promise(r => a.addEventListener('ended', () => r(true), {once:true})); o.ended = await Promise.race([ended, sleep(8000).then(() => false)]);
          a.pause(); }
        out[id] = o;
      }
      // chapter jump buttons on main
      const m = document.getElementById('main'); m.currentTime = 0;
      for (const b of ['goP1','goP2','goP3']) { document.getElementById(b).click(); await sleep(1200); out[b] = {t: m.currentTime, playing: !m.paused}; m.pause(); }
      document.querySelectorAll('button.jump')[3].click(); await sleep(1200); out.jump_script_part2 = {t: m.currentTime, playing: !m.paused}; m.pause();
      return out; }""")
    out["play"] = res; out["http_ge400"] = bad; out["console_errors"] = errs
    br.close()
exp = EXP["preview_duration_s"]
out["expected_preview_duration_s"] = exp
out["expected_marks"] = EXP["marks"]
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False)[:2500])

"""PLAYWRIGHT-AUDIO-SAFETY-01: observe_caption_prod_01.py に --hard-timeout-s(既定1800s)とbrowserのtry/finally closeを足す(冪等)。他workerとconflict時はorigin/main再取得後にこれを再実行。"""
import sys
from pathlib import Path
p = Path(sys.argv[1]) / "docs/research/ENDUSER-JA-CAPTION-PRODUCTION-WIRING-01/tools/observe_caption_prod_01.py"
s = p.read_text(encoding="utf-8")
if "--hard-timeout-s" in s:
    print("already patched"); sys.exit(0)
def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:60], s.count(old))
    s = s.replace(old, new)
rep('ap.add_argument("--browser", default="chromium", choices=["chromium", "webkit"]); ap.add_argument("--views"); ap.add_argument("--levels", default="std,adv")\n',
    'ap.add_argument("--browser", default="chromium", choices=["chromium", "webkit"]); ap.add_argument("--views"); ap.add_argument("--levels", default="std,adv")\n'
    'ap.add_argument("--hard-timeout-s", type=float, default=1800.0, help="全体のhard timeout秒(超過でbrowserをkillしrc=124。PLAYWRIGHT-AUDIO-SAFETY-01)")\n')
# run_view: browser close を finally へ(例外でも必ずclose)
rep('    br = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"]) if a.browser == "chromium" else p.webkit.launch()\n    ctx = br.new_context(**opts); page = ctx.new_page()\n',
    '    br = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"]) if a.browser == "chromium" else p.webkit.launch()\n    try:\n        _run_view_body(p, br, view, opts, base, d, lv, R, shots)\n    finally:\n        try:\n            br.close()\n        except Exception:\n            pass\n\n\ndef _run_view_body(p, br, view, opts, base, d, lv, R, shots):\n    ctx = br.new_context(**opts); page = ctx.new_page()\n')
rep('    res["checks"] = chk; R[f"{view}:{d}:{lv}"] = res\n    ctx.close(); br.close()\n', '    res["checks"] = chk; R[f"{view}:{d}:{lv}"] = res\n    ctx.close()\n')
rep('        with sync_playwright() as p:\n', '        with sync_playwright(hard_timeout_s=a.hard_timeout_s) as p:\n')
p.write_text(s, encoding="utf-8", newline=""); print("patched")

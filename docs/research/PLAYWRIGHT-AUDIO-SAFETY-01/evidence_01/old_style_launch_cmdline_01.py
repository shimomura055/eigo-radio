"""PLAYWRIGHT-AUDIO-SAFETY-01: 旧方式(素のPlaywright・helperなし)でChromium headlessを起動しただけ(再生なし)の実cmdlineを保存。--mute-audioがPlaywright既定で付くことの実測。API 0・無音。"""
import json, subprocess, sys
from playwright.sync_api import sync_playwright
out = {}
with sync_playwright() as p:
    b = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"]); pg = b.new_page()
    ps = "Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath -like '*ms-playwright*' -and $_.CommandLine -notlike '*--type=*' } | ForEach-Object { $_.CommandLine }"
    r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.strip().splitlines()
    out["chromium_main_cmdlines"] = r
    out["has_mute_audio_by_playwright_default"] = any("--mute-audio" in c for c in r)
    out["mute_audio_count"] = [c.count("--mute-audio") for c in r]
    b.close()
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(out["has_mute_audio_by_playwright_default"], out["mute_audio_count"])

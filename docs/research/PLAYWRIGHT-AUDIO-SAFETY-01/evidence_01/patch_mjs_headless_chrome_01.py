"""PLAYWRIGHT-AUDIO-SAFETY-01: 生CDPでheadless Chromeをspawnする *.mjs に --mute-audio と終了hookを足す(冪等・API 0)。使い方: python patch_mjs_headless_chrome_01.py <repo_root>"""
import re, subprocess, sys
from pathlib import Path
root = Path(sys.argv[1]).resolve()
files = [f.strip() for f in subprocess.run(["git", "grep", "-l", "--", "--headless=new", "--", "*.mjs"], cwd=root, capture_output=True, text=True, encoding="utf-8").stdout.split("\n") if f.strip().endswith(".mjs")]
HOOK = "\nprocess.on('exit', () => { try { proc.kill(); } catch (e) {} });  // PLAYWRIGHT-AUDIO-SAFETY-01: 異常終了でもChromeを残さない"
n = 0
for rel in files:
    p = root / rel; s = p.read_text(encoding="utf-8")
    if "--mute-audio" in s:
        continue
    s2 = s.replace("'--headless=new',", "'--headless=new', '--mute-audio', '--autoplay-policy=user-gesture-required',", 1)
    m = re.search(r"^const proc = spawn\(.*\);[ \t]*\r?$", s2, re.M)
    if m and "process.on('exit'" not in s2:
        s2 = s2[:m.end()] + HOOK + s2[m.end():]
    p.write_text(s2, encoding="utf-8", newline=""); n += 1; print("patched", rel, "hook" if "PLAYWRIGHT-AUDIO-SAFETY-01" in s2 else "NOHOOK")
print("patched", n)

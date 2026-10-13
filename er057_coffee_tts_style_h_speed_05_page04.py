# -*- coding: utf-8 -*-
"""LISTEN-COMPARE-01 委任_04 (API0): N01 Std Take4-6 のmp3化とindex.htmlのN01 Std行への追加。他行は変更しない。"""
import os, re, json, html, hashlib, importlib.util
ROOT = os.path.dirname(os.path.abspath(__file__)); O = f"{ROOT}/er057_output/coffee_tts_style_h_speed_05_listen"; PG = f"{ROOT}/user_test/coffee_style_h_speed_05"; AU = f"{PG}/audio"
# page02の関数(mp3/judge/met/row)を再利用するため、該当定義部分のみ取り出して実行
src = open(f"{ROOT}/er057_coffee_tts_style_h_speed_05_page02.py", encoding="utf-8").read()
head = src[src.index("import numpy"):src.index("conv = {}")]
head = head.replace("ROOT = ", "_R = ")
ns = {"os": os, "re": re, "json": json, "html": html, "hashlib": hashlib}
exec(head.replace("M2 = json.load", "M2_unused = None  # ").split("sha = lambda")[0].split("M2")[0] if False else "", ns)
import numpy as np, soundfile as sf, lameenc
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
fn_src = src[src.index("def mp3("):src.index("conv = {}")]
exec(fn_src, {**globals()})
M4 = json.load(open(f"{O}/gen04/measurements_04.json", encoding="utf-8"))
exec(fn_src, globals())
page = open(f"{PG}/index.html", encoding="utf-8").read(); orig = page
assert "N01 Take4" not in page
conv = {}; new = ""; lv = "std"; c = "N01"; res = ["pass", "fail", "fail"]; ok_n = 1
for tk in (4, 5, 6):
    k = f"N01_std_part1_t{tk}"; t = M4["takes"][k]; rs = judge(t, lv); ok = (M4["classification"][k] == "暫定合格")
    assert ok == (len(rs) == 0), (k, M4["classification"][k], rs)
    wav = f"{ROOT}/{t['path']}"; h = sha(wav); assert h == t["final_sha256"], k
    dst = f"{AU}/{c}_{lv}_t{tk}.mp3"; mp3(wav, dst)
    conv[os.path.basename(dst)] = {"src_wav": t["path"], "src_wav_sha256": h, "matches_measured_sha": True, "mp3_sha256": sha(dst), "encoder": "lameenc 96kbps mono q2", "measurements_source": "er057_output/coffee_tts_style_h_speed_05_listen/gen04/measurements_04.json"}
    new += row(c, tk, lv, t, ok, rs, f"audio/{c}_{lv}_t{tk}.mp3"); ok_n += ok; res.append("pass" if ok else "fail")
old_sum = "<b>N01 Standard: 3 take中の合格数 1</b>(Take1/2/3 = pass / fail / fail)"
assert page.count(old_sum) == 1
page = page.replace(old_sum, f"<b>N01 Standard: 6 take中の合格数 {ok_n}</b>(Take1〜6 = {' / '.join(res)}。Take4〜6は委任_04の再発確認で追加)")
sec_start = page.index("<section id='std'>"); sec_end = page.index("</section>", sec_start); sec = page[sec_start:sec_end]
m = re.search(r"<div class='row'><div class='hd'><b>N01 Take3</b>.*?</div></div>(?=<div class='row'>|<h3>|$)", sec, re.S); assert m
# Take3 row ends at its closing; find end robustly
i3 = sec.index("<b>N01 Take3</b>"); j = sec.index("<div class='row'>", i3)
sec = sec[:j] + new + sec[j:]
page = page[:sec_start] + sec + page[sec_end:]
assert page != orig and page.count("class='row'") == orig.count("class='row'") + 3
open(f"{PG}/index.html", "w", encoding="utf-8").write(page)
json.dump(conv, open(f"{O}/audio_conversion_04.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(conv), "mp3; rows", page.count("class='row'"))

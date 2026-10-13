# -*- coding: utf-8 -*-
"""LISTEN-COMPARE-01 委任_02 (API0): N01/N02 Take2/3 のmp3化とindex.htmlへの行追加。他候補行・H0・v5は変更しない。"""
import os, re, json, html, hashlib
import numpy as np, soundfile as sf, lameenc
ROOT = os.path.dirname(os.path.abspath(__file__)); O = f"{ROOT}/er057_output/coffee_tts_style_h_speed_05_listen"; PG = f"{ROOT}/user_test/coffee_style_h_speed_05"; AU = f"{PG}/audio"
M2 = json.load(open(f"{O}/gen02/measurements_02.json", encoding="utf-8")); M5 = json.load(open(f"{ROOT}/er057_output/coffee_tts_style_h_speed_04/round5/measurements_r5.json", encoding="utf-8"))
C5 = json.load(open(f"{ROOT}/er057_output/coffee_tts_style_h_speed_04/round5/classification_r5.json", encoding="utf-8"))["per_job"]
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
def mp3(src, dst):
    x, sr = sf.read(src, dtype="float64"); x = x.mean(axis=1) if x.ndim > 1 else x
    e = lameenc.Encoder(); e.set_bit_rate(96); e.set_in_sample_rate(sr); e.set_channels(1); e.set_quality(2)
    open(dst, "wb").write(e.encode((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes()) + e.flush())
def judge(t, lv):
    r = []; lo, hi = (151, 163) if lv == "std" else (161, 173); em = 498 if lv == "std" else 593; w = t["wpm"]
    if not (lo <= w <= hi): r.append(f"速度が基準外(実測{w}WPM、基準{lo}-{hi}。{'遅すぎ' if w<lo else '速すぎ'})")
    if t["end_pause_ms"]["mean"] > em: r.append(f"文末平均無音が基準超過({t['end_pause_ms']['mean']}ms > {em}ms)")
    if len(t["long800"]) > 1: r.append(f"800ms以上の長無音が{len(t['long800'])}本(基準は1本以下)")
    if t.get("asr_verified") is False: r.append(f"ASR不一致({t.get('primary_asr')})")
    if t["anomaly_medium_plus"] > 0: r.append(f"異音検知medium以上{t['anomaly_medium_plus']}件")
    return r
def met(t, lv):
    e = t["end_pause_ms"]
    w = f"Adv実測 {t['wpm']}" if lv == "adv" else f"Std実測(6%減速後) {t['wpm']} / raw換算 {round(t['wpm']/0.94,1)}"
    s = f"WPM {w} / 文末無音 平均{e['mean']}ms(最大{e['max']}ms) / 800ms以上の長無音 {len(t['long800'])}本"
    if t["long800"]: s += "(" + ", ".join(f"{x['ms']}ms:{x['prev']}->{x['next']}" for x in t["long800"]) + ")"
    s += f" / ASR(減速前音声) {t.get('primary_asr','-')}" + ("" if t.get("asr_verified", True) is not False else " [ASR不一致]") + f" / 異音検知 medium以上 {t['anomaly_medium_plus']}件"
    return s
def row(c, tk, lv, t, ok, rs, src):
    st = "<span class='ok'>暫定合格</span>" if ok else "<span class='ng'>不合格</span>"
    why = "" if ok else "<div class='ng'>不合格理由: " + html.escape(" / ".join(rs)) + "</div>"
    return f"<div class='row'><div class='hd'><b>{c} Take{tk}</b> {st}</div><audio controls preload='none' src='{src}'></audio><div class='s'>{met(t, lv)}</div>{why}</div>"
conv = {}; page = open(f"{PG}/index.html", encoding="utf-8").read(); orig = page
assert "N01 Take2" not in page
for lv in ("std", "adv"):
    for c in ("N01", "N02"):
        ok_n = 0; new = ""; k1 = f"{c}_{lv}_part1_t1"; t1 = M5["takes"][k1]; r1 = judge(t1, lv)
        assert (C5[k1]["cls"] == "暫定合格") == (len(r1) == 0), k1
        ok_n += (len(r1) == 0); res = ["pass" if not r1 else "fail"]
        for tk in (2, 3):
            k = f"{c}_{lv}_part1_t{tk}"; t = M2["takes"][k]; rs = judge(t, lv); ok = (M2["classification"][k] == "暫定合格")
            assert ok == (len(rs) == 0), (k, M2["classification"][k], rs)
            wav = f"{ROOT}/{t['path']}"; h = sha(wav); assert h == (t["final_sha256"] if lv == "std" else t["raw_sha256"]), k
            dst = f"{AU}/{c}_{lv}_t{tk}.mp3"; mp3(wav, dst)
            conv[os.path.basename(dst)] = {"src_wav": t["path"], "src_wav_sha256": h, "matches_measured_sha": True, "mp3_sha256": sha(dst), "encoder": "lameenc 96kbps mono q2", "measurements_source": "er057_output/coffee_tts_style_h_speed_05_listen/gen02/measurements_02.json"}
            new += row(c, tk, lv, t, ok, rs, f"audio/{c}_{lv}_t{tk}.mp3"); ok_n += ok; res.append("pass" if ok else "fail")
        summ = f"<div class='s' style='background:#eef;padding:4px'><b>{c} {'Standard' if lv=='std' else 'Advanced'}: 3 take中の合格数 {ok_n}</b>(Take1/2/3 = {' / '.join(res)})</div>"
        pat = re.compile(r"(<div class='row'><div class='hd'><b>%s Take1</b>.*?)(?=<div class='row'>|<h3>|</section>)" % c, re.S)
        sec_start = page.index(f"<section id='{lv}'>"); sec_end = page.index("</section>", sec_start)
        sec = page[sec_start:sec_end]; m = pat.search(sec); assert m, (c, lv)
        sec = sec[:m.start()] + summ + m.group(1) + new + sec[m.end():]
        page = page[:sec_start] + sec + page[sec_end:]
page = page.replace("新規生成なし)。", "新規生成なし)。委任_02でN01・N02のみTake2/Take3を追加生成しました(各Promptを3 takeで比較できます)。", 1)
assert page != orig
open(f"{PG}/index.html", "w", encoding="utf-8").write(page)
json.dump(conv, open(f"{O}/audio_conversion_02.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(conv), "mp3; rows", page.count("class='row'"))

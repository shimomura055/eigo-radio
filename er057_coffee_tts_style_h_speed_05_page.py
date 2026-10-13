# -*- coding: utf-8 -*-
"""LISTEN-COMPARE-01: 5候補(N01/N02/L02/J13/J07) Std/Adv比較試聴ページ生成(API0、既存wav再利用、新規TTS/ASRなし)。"""
import os, json, html, hashlib, shutil
import numpy as np, soundfile as sf, lameenc
ROOT = os.path.dirname(os.path.abspath(__file__)); O = f"{ROOT}/er057_output/coffee_tts_style_h_speed_05_listen"; PG = f"{ROOT}/user_test/coffee_style_h_speed_05"; AU = f"{PG}/audio"
os.makedirs(AU, exist_ok=True); os.makedirs(O, exist_ok=True)
SRC = {
 "J07": ("er057_output/coffee_tts_style_h_speed_03/round1", "r1"), "J13": ("er057_output/coffee_tts_style_h_speed_03/round1", "r1"),
 "L02": ("er057_output/coffee_tts_style_h_speed_03/round3", "r3"),
 "N01": ("er057_output/coffee_tts_style_h_speed_04/round5", "r5"), "N02": ("er057_output/coffee_tts_style_h_speed_04/round5", "r5")}
ORDER = ["N01", "N02", "L02", "J13", "J07"]
JA = {
 "N01": "陽気で優しい語り手が実話を、普段より少しゆっくり目に語る。各文を自然に言い切ってから、話の転換点でもすぐ次の文へ進む。",
 "N02": "温かく明るい語り手が実話を、普段より少しゆっくり目に語る。各文を最後まで言い切ってから、すぐ次の文へ進む(N01から『話の転換でも』の節を除いた版)。",
 "L02": "明瞭で親しみやすいナレーターが実話を、普段より少しゆっくりしたペースで語る。文と文の間で待たず、すぐ次を始め、ひと続きの語りにする。",
 "J13": "ニュース速報よりはっきり遅く、温かく明るく、抑揚豊かに読む。文と文の間の無音をとても短くし、声を途切れさせず進める。",
 "J07": "温かく落ち着いた、明るく明瞭なラジオ司会者。考えの区切りで短く自然に息継ぎし、息継ぎを長引かせない(速度の指示なし)。"}
M, P, JOBS = {}, {}, {}
for c in ORDER:
    d, tg = SRC[c]
    if d not in M:
        M[d] = json.load(open(f"{ROOT}/{d}/measurements_{tg}.json", encoding="utf-8"))
        C = json.load(open(f"{ROOT}/{d}/classification_{tg}.json", encoding="utf-8")); JOBS[d] = C.get("per_job", C)
        P[d] = json.load(open(f"{ROOT}/{d}/prompts_{tg}.json", encoding="utf-8"))["candidates"]
conv = {}
def mp3(src, dst):
    x, sr = sf.read(src, dtype="float64"); x = x.mean(axis=1) if x.ndim > 1 else x
    e = lameenc.Encoder(); e.set_bit_rate(96); e.set_in_sample_rate(sr); e.set_channels(1); e.set_quality(2)
    open(dst, "wb").write(e.encode((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes()) + e.flush())
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
def judge(t, lv):
    r = []
    lo, hi = (151, 163) if lv == "std" else (161, 173); em = 498 if lv == "std" else 593
    w = t["wpm"]
    if not (lo <= w <= hi): r.append(f"速度が基準外(実測{w}WPM、基準{lo}-{hi}。{'遅すぎ' if w<lo else '速すぎ'})")
    if t["end_pause_ms"]["mean"] > em: r.append(f"文末平均無音が基準超過({t['end_pause_ms']['mean']}ms > {em}ms)")
    if len(t["long800"]) > 1: r.append(f"800ms以上の長無音が{len(t['long800'])}本(基準は1本以下)")
    if t.get("asr_verified") is False: r.append(f"ASR不一致({t.get('primary_asr')})")
    if t["anomaly_medium_plus"] > 0: r.append(f"異音検知medium以上{t['anomaly_medium_plus']}件")
    return r
rows = {"std": [], "adv": []}
for c in ORDER:
    d, tg = SRC[c]
    for lv in ("std", "adv"):
        k = f"{c}_{lv}_part1_t1"; t = M[d]["takes"][k]
        wav = f"{ROOT}/{t['path']}"
        assert os.path.exists(wav), wav
        h = sha(wav)
        if lv == "std": assert h == t["final_sha256"], ("slow6 sha mismatch", k)
        else: assert h == t["raw_sha256"], ("raw sha mismatch", k)
        dst = f"{AU}/{c}_{lv}_t1.mp3"; mp3(wav, dst)
        conv[os.path.basename(dst)] = {"src_wav": t["path"], "src_wav_sha256": h, "matches_measured_sha": True, "mp3_sha256": sha(dst), "measurements_source": f"{d}/measurements_{tg}.json", "round": tg}
        cj = JOBS[d][k]; cls = cj["cls"] if isinstance(cj, dict) else cj
        rs = judge(t, lv); ok = (cls == "暫定合格")
        assert ok == (len(rs) == 0), ("classification mismatch", k, cls, rs)
        rows[lv].append(dict(id=c, t=t, cls=cls, reasons=rs, ok=ok, src=f"audio/{c}_{lv}_t1.mp3", tag=tg))
R5 = M["er057_output/coffee_tts_style_h_speed_04/round5"]
SRC04 = f"{ROOT}/user_test/coffee_style_h_speed_04/audio"
refs = {"std": [], "adv": []}
for lv in ("std", "adv"):
    for nm, key, label in (("H0_%s_t1" % lv, R5["H0_t1"][lv], "H0 Take1(前回高評価Prompt)"), ("v5_%s" % lv, R5["v5"][lv], "現行v5 Part1")):
        shutil.copyfile(f"{SRC04}/{nm}.mp3", f"{AU}/{nm}.mp3")
        conv[nm + ".mp3"] = {"copied_from": f"user_test/coffee_style_h_speed_04/audio/{nm}.mp3", "mp3_sha256": sha(f"{AU}/{nm}.mp3"), "measurements_source": "er057_output/coffee_tts_style_h_speed_04/round5/measurements_r5.json (H0_t1/v5)"}
        rs = judge(key, lv)
        if nm.startswith("v5"): key = dict(key, primary_asr="-", asr_verified=None)
        refs[lv].append(dict(id=label, t=key, reasons=rs, ok=not rs, src=f"audio/{nm}.mp3", ref=True))
json.dump(conv, open(f"{O}/audio_conversion_01.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)

def met(t, lv):
    e = t["end_pause_ms"]
    w = f"Adv実測 {t['wpm']}" if lv == "adv" else f"Std実測(6%減速後) {t['wpm']} / raw換算 {round(t['wpm']/0.94,1)}"
    s = f"WPM {w} / 文末無音 平均{e['mean']}ms(最大{e['max']}ms) / 800ms以上の長無音 {len(t['long800'])}本"
    if t["long800"]: s += "(" + ", ".join(f"{x['ms']}ms:{x['prev']}->{x['next']}" for x in t["long800"]) + ")"
    a = t.get("primary_asr", "-")
    s += f" / ASR(減速前音声) {a}" + ("" if t.get("asr_verified", True) is not False else " [ASR不一致]") + f" / 異音検知 medium以上 {t['anomaly_medium_plus']}件"
    return s
def row(r, lv):
    ref = r.get("ref")
    if ref: st = "<span class='ref'>比較用</span> " + ("<span class='ok'>数値基準内</span>" if r["ok"] else "<span class='ng'>基準外</span>")
    else: st = "<span class='ok'>暫定合格</span>" if r["ok"] else "<span class='ng'>不合格</span>"
    why = ""
    if not r["ok"]: why = "<div class='ng'>" + ("基準外の点" if ref else "不合格理由") + ": " + html.escape(" / ".join(r["reasons"])) + "</div>"
    elif ref and r["t"].get("asr_verified") is None: why = "<div class='s'>(v5のASRは本ページでは未測定)</div>"
    nm = r["id"] if ref else f"{r['id']} Take1"
    return f"<div class='row'><div class='hd'><b>{html.escape(nm)}</b> {st}</div><audio controls preload='none' src='{r['src']}'></audio><div class='s'>{met(r['t'], lv)}</div>{why}</div>"
def sect(lv, ttl, crit):
    h = f"<section id='{lv}'><h2>{ttl}</h2><p class='s'>合格基準(暫定): {crit}。合否は機械指標のみで、声の明るさ・抑揚は聴いて判断してください。</p><p><button class='seq'>このセクションを上から連続再生</button> <button class='stop'>停止</button></p>"
    h += "<h3>5候補(Take1)</h3>" + "".join(row(r, lv) for r in rows[lv])
    h += "<h3>比較用</h3>" + "".join(row(r, lv) for r in refs[lv])
    return h + "</section>"
cat = "<section id='prompts'><h2>(C) Prompt一覧(英語原文・日本語要約)</h2><p class='s'>日本語要約は作業者による意訳です。原文が正です。</p>"
for c in ORDER:
    d, tg = SRC[c]; pr = P[d][c]
    cat += f"<details open><summary><b>{c}</b>(出典 {tg}、sha {hashlib.sha256(pr['style'].encode()).hexdigest()[:8]})</summary><div class='sc'>{html.escape(pr['style'])}</div><p>{html.escape(JA[c])}</p><p class='s'>設計軸: " + html.escape(" / ".join(f"{k}={v}" for k, v in pr["axes"].items())) + "</p></details>"
h0 = json.load(open(f"{ROOT}/er057_output/coffee_tts_style_h_speed_02/prompts_h_speed_01.json", encoding="utf-8"))["candidates"]["H0"]["style"]
cat += f"<details><summary><b>H0</b>(比較用)</summary><div class='sc'>{html.escape(h0)}</div><p>温かく落ち着いた昼のラジオニュース司会者の語り。明瞭で信頼でき親しみやすく、声に笑みがある。意味のまとまりで語を区切り、滑らかにつなぎ、考えの間で自然に息をつく。</p></details></section>"
JS = """<script>
(function(){function stopAll(){document.querySelectorAll('audio').forEach(function(a){a.pause();});}
document.querySelectorAll('audio').forEach(function(a){a.addEventListener('play',function(){document.querySelectorAll('audio').forEach(function(b){if(b!==a)b.pause();});});});
document.querySelectorAll('.seq').forEach(function(b){b.addEventListener('click',function(){var s=b.closest('section');var l=[].slice.call(s.querySelectorAll('audio'));var i=0;function nx(){if(i>=l.length)return;var a=l[i++];a.currentTime=0;a.onended=nx;a.play();a.scrollIntoView({block:'center'});}stopAll();nx();});});
document.querySelectorAll('.stop').forEach(function(b){b.addEventListener('click',function(){document.querySelectorAll('audio').forEach(function(a){a.onended=null;});stopAll();});});})();
</script>"""
CSS = "body{font-family:sans-serif;max-width:760px;margin:0 auto;padding:8px 12px;line-height:1.55}section{border-top:2px solid #888;margin-top:18px;padding-top:6px}audio{width:100%}.s{color:#555;font-size:.85em}.n{background:#fff8e0;padding:6px;font-weight:bold}.sc{background:#f4f4f4;padding:6px;white-space:pre-wrap;font-size:.9em}h2{font-size:1.15em}h3{font-size:1em;margin:10px 0 2px}.row{border:1px solid #ccc;border-radius:6px;padding:6px;margin:8px 0}.ok{color:#070;font-weight:bold}.ng{color:#b30}.ref{color:#036}button{padding:6px 10px;margin:2px}"
html_ = f"""<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>Coffee TTS Style H 5候補 比較試聴(Std/Adv)</title><style>{CSS}</style></head><body>
<h1>Coffee TTS Style H 5候補 比較試聴(Standard / Advanced)</h1>
<p class='n'>暫定成果物。Trial(VALIDATED上限)。採用判断なし。ユーザー試聴用</p>
<p class='s'>FAMILY-X-COFFEE-TTS-STYLE-H-SPEED-LISTEN-COMPARE-01 委任_01。有望5候補 N01 / N02 / L02 / J13 / J07 を、同じ原稿(Part1)・同じ声(Aoede)・同じモデル(gemini-3.8-flash-lite-tts)で生成済みのTake1音声で並べました(新規生成なし)。Standardは6%減速後の音声です。K06(Std)・K01(Adv)はユーザー試聴評価NGのため除外しています。WPM=1分あたりの英語語数。数値は機械指標の参考値で、合否は暫定です。</p>
<p class='s'>一覧: <a href='#std'>(A) Standard</a> <a href='#adv'>(B) Advanced</a> <a href='#prompts'>(C) Prompt</a></p>
{sect('std', '(A) Standard 聞き比べ(6%減速後)', 'Std実測151-163WPM・文末平均498ms以下・800ms以上の長無音1本以下・ASR/異音OK')}{sect('adv', '(B) Advanced 聞き比べ', 'Adv実測161-173WPM・文末平均593ms以下・800ms以上の長無音1本以下・ASR/異音OK')}{cat}{JS}</body></html>"""
open(f"{PG}/index.html", "w", encoding="utf-8").write(html_)
json.dump({lv: [{"id": r["id"], "cls": r.get("cls"), "ok": r["ok"], "reasons": r["reasons"]} for r in rows[lv] + refs[lv]] for lv in rows}, open(f"{O}/judgement_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(os.listdir(AU)), "mp3")

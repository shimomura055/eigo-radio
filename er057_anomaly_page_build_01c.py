# -*- coding: utf-8 -*-
"""委任_01C §5: 異音候補の人間確認ページ(静的)と ANOMALY_CANDIDATES_01.md を生成する。有料API不使用(numpy/scipy/soundfile/lameenc/Pillowのみ)。
候補の確定はしない(ユーザーが聴いて確認する)。"""
import glob
import html
import json
import os
import re
import shutil

import lameenc
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw
from scipy.signal import spectrogram

ROOT = os.path.dirname(os.path.abspath(__file__))
P45 = os.path.join(ROOT, "er057_output", "coffee_final_listening_tone_trial_01", "part_45")
SNAP = os.path.join(P45, "evidence_snapshot")
OUT = os.path.join(ROOT, "user_test", "coffee_tone_trial_01", "anomaly")
E = html.escape

SYMPTOM_JA = {
    "clip": "音割れ・飽和(クリッピング)", "click": "クリック/ポップ(瞬間的な波形の飛び)", "dropout": "発話中の欠落(急な無音)",
    "long_gap": "不自然に長い無音", "edge_abrupt": "語頭/語末が急に始まる・切れる", "level_step": "音量の急変(階段状)",
    "spec_jump": "スペクトルの急変", "asr_low_conf_word": "ローカルASRの信頼度が低い語(聞き取りにくい可能性)",
    "asr_mismatch_word": "ローカルASR転写が原稿と異なる語(読み違い・不明瞭の可能性)",
}
SYMPTOM_ORDER = ["clip", "dropout", "click", "edge_abrupt", "long_gap", "level_step", "spec_jump", "asr_mismatch_word", "asr_low_conf_word"]
CONF_ORDER = {"high": 0, "medium": 1, "low": 2}
LEVEL_JA = {"a2": "Standard", "b1b": "Advanced"}
SEG_LABEL = {"welcome": "Welcome", "topic_intro": "Topic intro", "japanese_title": "Japanese title", "preview_intro": "Preview intro",
             "preview": "Preview", "key_phrases_intro": "Key phrases intro", "full_story_intro": "Full story intro",
             "comment_1": "Comment 1", "comment_2": "Comment 2", "comment_3": "Comment 3", "comment_4": "Comment 4",
             "full_story_part1": "Full Story Part 1", "full_story_part2": "Full Story Part 2", "full_story_part3": "Full Story Part 3",
             "in_one_line": "In One Line", "point_explanation": "Point explanation"}


def seg_label(s):
    if s is None:
        return "(不明)"
    if s in SEG_LABEL:
        return SEG_LABEL[s]
    m = re.match(r"kp(\d)_en$", s)
    if m:
        return f"Key Phrase {m.group(1)}(英語)"
    m = re.match(r"meaning_(\d)$", s)
    if m:
        return f"Key Phrase {m.group(1)}(日本語意味)"
    m = re.match(r"kp(\d)_explanation_en$", s)
    if m:
        return f"Key Phrase {m.group(1)}(英語解説)"
    s2 = s.replace("_charon", "")
    if s2 in SEG_LABEL:
        return SEG_LABEL[s2]
    return s


def encode_mp3(x, sr, path, kbps=96):
    enc = lameenc.Encoder()
    enc.set_bit_rate(kbps)
    enc.set_in_sample_rate(sr)
    enc.set_channels(1)
    enc.set_quality(2)
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2").tobytes()
    open(path, "wb").write(enc.encode(pcm) + enc.flush())


def make_spec_png(x, sr, t_center, path, width=640, height=150):
    f, t, S = spectrogram(x, fs=sr, nperseg=512, noverlap=384, window="hann", mode="magnitude")
    D = 20 * np.log10(np.maximum(S, 1e-7))
    D = np.clip(D, D.max() - 80, D.max())
    D = (D - D.min()) / max(D.max() - D.min(), 1e-9)
    D = D[::-1]
    # 簡易カラーマップ(黒→紫→橙→黄)
    stops = np.array([[0, 0, 0], [60, 20, 110], [200, 60, 80], [250, 190, 40], [255, 255, 200]], float)
    pos = np.linspace(0, 1, len(stops))
    rgb = np.stack([np.interp(D, pos, stops[:, k]) for k in range(3)], axis=-1).astype("uint8")
    im = Image.fromarray(rgb).resize((width, height), Image.BILINEAR)
    dr = ImageDraw.Draw(im)
    xc = int(t_center / (len(x) / sr) * width)
    dr.line([(xc, 0), (xc, height)], fill=(80, 255, 120), width=2)
    for sec in range(0, int(len(x) / sr) + 1):
        xx = int(sec / (len(x) / sr) * width)
        dr.line([(xx, height - 6), (xx, height)], fill=(255, 255, 255), width=1)
    im.convert("P", palette=Image.ADAPTIVE, colors=48).save(path, optimize=True)


def cut(x, sr, t, half=3.0):
    a = max(0, int((t - half) * sr))
    b = min(len(x), int((t + half) * sr))
    return x[a:b], (t - a / sr)


def main():
    res = json.load(open(os.path.join(P45, "ANOMALY_CANDIDATES_01.json"), encoding="utf-8"))
    cands = res["candidates"]
    timelines = {lv: json.load(open(os.path.join(SNAP, lv, "audit", "timeline.json"), encoding="utf-8")) for lv in ("a2", "b1b")}
    tts = {lv: json.load(open(os.path.join(SNAP, lv, "audit", "tts_generation_results.json"), encoding="utf-8")) for lv in ("a2", "b1b")}
    # --- 掲載対象の選定 ---
    seg_c = [c for c in cands if c["source"] == "segment" and not c["segment"].startswith("num_")]
    seg_ep = {(c["level"], round(c["t_episode"], 1)) for c in seg_c if c["t_episode"] is not None}
    asm_only = []
    for c in cands:
        if c["source"] != "assembled" or c["fixed_asset"]:
            continue
        if any(abs(c["t_episode"] - te) < 0.4 for (lv, te) in seg_ep if lv == c["level"]):
            continue
        asm_only.append(c)
    listed = seg_c + asm_only

    def sort_key(c):
        return (SYMPTOM_ORDER.index(c["symptom"]), CONF_ORDER[c["confidence"]], c["t_episode"] if c["t_episode"] is not None else 1e6, c["segment"] or "")
    cnt = {"a2": 0, "b1b": 0}
    for c in sorted(listed, key=lambda c: (c["level"], sort_key(c))):
        cnt[c["level"]] += 1
        c["display_id"] = ("STD" if c["level"] == "a2" else "ADV") + f"-{cnt[c['level']]:02d}"
    # --- 音声の読み込みキャッシュ ---
    asm = {}
    for lv in ("a2", "b1b"):
        f = glob.glob(os.path.join(SNAP, lv, "assembled", "*.wav"))[0]
        x, sr = sf.read(f, dtype="float64")
        asm[lv] = (x.mean(axis=1), sr)
    segcache = {}

    def segwav(lv, seg):
        k = (lv, seg)
        if k not in segcache:
            x, sr = sf.read(os.path.join(SNAP, lv, "narration", seg + ".wav"), dtype="float64")
            segcache[k] = (x.mean(axis=1) if x.ndim == 2 else x, sr)
        return segcache[k]

    shutil.rmtree(os.path.join(OUT, "clips"), ignore_errors=True)
    shutil.rmtree(os.path.join(OUT, "spec"), ignore_errors=True)
    os.makedirs(os.path.join(OUT, "clips"))
    os.makedirs(os.path.join(OUT, "spec"))

    def render(did, lv, seg, t_seg, t_ep, half=3.0):
        if t_ep is not None:
            x, sr = asm[lv]
            seg_x, rel = cut(x, sr, t_ep, half)
        else:
            x, sr = segwav(lv, seg)
            seg_x, rel = cut(x, sr, t_seg, half)
        encode_mp3(seg_x, sr, os.path.join(OUT, "clips", did + ".mp3"))
        make_spec_png(seg_x, sr, rel, os.path.join(OUT, "spec", did + ".png"))

    for c in listed:
        render(c["display_id"], c["level"], c["segment"], c["t_seg"], c["t_episode"])
    # --- 重点箇所 ---
    tl = timelines["a2"]
    p3 = [e for e in tl if e["part"] == "Full Story Part 3"][0]["start_seconds"]
    focus = [
        dict(did="FOCUS-STD-P3-coffee", level="a2", segment="full_story_part3", t_seg=43.3, label="Standard Full Story Part 3「A coffee price tag may have its own hidden clock」の coffee 付近",
             note="ローカルfaster-whisper(small)のword timestampで coffee = 43.30〜43.56秒(セグメント内)、episode上 %.2f〜%.2f秒。前後を含め5秒クリップ。" % (p3 + 43.3, p3 + 43.56)),
    ]
    p3b = [e for e in timelines["b1b"] if e["part"].startswith("Full Story Part 3")][0]["start_seconds"]
    focus.append(dict(did="FOCUS-ADV-P3-coffee", level="b1b", segment="full_story_part3", t_seg=39.02, label="(参考・対照)Advanced Full Story Part 3 の同じ文 coffee 付近",
                      note="local whisper(small) coffee = 39.02〜39.30秒、episode上 %.2f〜%.2f秒。" % (p3b + 39.02, p3b + 39.3)))
    for f in focus:
        f["t_episode"] = round((p3 if f["level"] == "a2" else p3b) + f["t_seg"], 3)
        render(f["did"], f["level"], f["segment"], f["t_seg"], f["t_episode"], half=2.5)
    res["listed_candidates"] = [dict(display_id=c["display_id"], id=c["id"]) for c in listed]
    res["focus"] = focus
    json.dump(res, open(os.path.join(P45, "ANOMALY_CANDIDATES_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # --- ANOMALY_CANDIDATES_01.md ---
    L = ["# ANOMALY_CANDIDATES_01(委任_01C §5 Phase 1、無料ローカル解析、候補の確定はユーザーが行う)", "",
         "検知スクリプト `er057_audio_anomaly_detect_trial_01.py`(numpy %s / scipy %s / soundfile %s / local faster-whisper %s `%s`、API不使用、費用JPY 0)。生データ: `ANOMALY_CANDIDATES_01.json`(全候補%d件、うち掲載%d件)。" % (
             res["libs"]["numpy"], res["libs"]["scipy"], res["libs"]["soundfile"], res["libs"]["faster_whisper"], res["libs"]["whisper_model"], len(cands), len(listed)),
         "人間確認ページ: https://shimomura055.github.io/eigo-radio/user_test/coffee_tone_trial_01/anomaly/index.html (候補ごとの前後3秒mp3+スペクトログラム+全編へのジャンプ)", "",
         "## 重点箇所(ユーザー指定)", ""]
    for f in focus:
        L.append(f"- **{f['did']}**: {f['label']} — {f['note']} 検知器の候補は ±1.0秒以内に**0件**(下記「重点箇所の所見」参照)。")
    L += ["", "## 掲載候補(%d件。症状の優先順→信頼度→時刻)" % len(listed), "",
          "| 表示ID | level | segment | seg内(s) | episode(s) | 症状 | 信頼度 | 指標値 | 近傍の語 |", "|---|---|---|---|---|---|---|---|---|"]
    for c in sorted(listed, key=lambda c: (c["level"], c["display_id"])):
        m = ", ".join(f"{k}={v}" for k, v in c["metrics"].items())
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            c["display_id"], LEVEL_JA[c["level"]], seg_label(c["segment"]), c["t_seg"], c["t_episode"] if c["t_episode"] is not None else "-",
            SYMPTOM_JA[c["symptom"]], c["confidence"], m.replace("|", "/"), (c.get("near_words") or "").replace("|", "/")))
    open(os.path.join(P45, "ANOMALY_CANDIDATES_01.md"), "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")

    # --- ページ ---
    def timeline_rows(lv):
        out = []
        for e in timelines[lv]:
            if e["part"].startswith("pause"):
                continue
            out.append('<tr><td><button class="jump" data-lv="%s" data-t="%s">&#9654; %.2fs</button></td><td>%s</td><td>%.2fs</td></tr>' % (lv, e["start_seconds"], e["start_seconds"], E(re.sub(r"\s*\((Aoede|Charon)[^)]*\)", "", e["part"])), e["duration_seconds"]))
        return "\n".join(out)

    def rows(lv):
        out = []
        for c in sorted([c for c in listed if c["level"] == lv], key=lambda c: c["display_id"]):
            m = ", ".join(f"{k}={v}" for k, v in c["metrics"].items())
            te = c["t_episode"]
            btn = '<button class="jump" data-lv="%s" data-t="%s">&#9654; 全編 %.2fs から</button>' % (lv, max(0, te - 3), te) if te is not None else "(全編timelineに直接対応しない固定shell/KP内)"
            seg = c["segment"] or ""
            v = None
            if seg in tts[lv]["segments"]:
                v = tts[lv]["segments"][seg].get("voice")
            vtxt = ("記録voice=%s" % v) if v else ("固定shell/共通音声(Master Store)" if seg in ("welcome", "preview_intro", "key_phrases_intro", "full_story_intro", "point_explanation") else "voice記録: 本文/KPはAoede系(audit)")
            out.append("""<tr id="%(d)s"><td><b>%(d)s</b><br><span class="conf %(cf)s">%(cf)s</span></td>
<td>%(seg)s<br>seg内 %(ts)ss<br>episode %(te)s<br><small>%(vt)s</small></td>
<td>%(sym)s<br><small>%(m)s</small></td>
<td><small>%(nw)s</small></td>
<td><audio controls preload="none" src="clips/%(d)s.mp3"></audio><br><img loading="lazy" src="spec/%(d)s.png" alt="spectrogram %(d)s" width="320"><br>%(btn)s</td>
<td class="chk">&#9744; 異常あり &nbsp; &#9744; 問題なし &nbsp; &#9744; 判断不能<br>メモ: ______</td></tr>""" % dict(
                d=c["display_id"], cf=c["confidence"], seg=E(seg_label(c["segment"])), ts=c["t_seg"], te=("%.2fs" % te) if te is not None else "-", vt=E(vtxt),
                sym=E(SYMPTOM_JA[c["symptom"]]), m=E(m), nw=E(c.get("near_words") or ""), btn=btn))
        return "\n".join(out)

    def focus_rows():
        out = []
        for f in focus:
            te = f["t_episode"]
            out.append("""<tr id="%(d)s"><td><b>%(d)s</b></td><td>%(lv)s / Full Story Part 3<br>seg内 %(ts)ss / episode %(te).2fs</td>
<td>%(lab)s<br><small>%(note)s</small></td>
<td><audio controls preload="none" src="clips/%(d)s.mp3"></audio><br><img loading="lazy" src="spec/%(d)s.png" width="320" alt="spectrogram %(d)s"><br>
<button class="jump" data-lv="%(l)s" data-t="%(t)s">&#9654; 全編 %(t2).2fs から</button></td>
<td class="chk">&#9744; 異常あり &nbsp; &#9744; 問題なし &nbsp; &#9744; 判断不能<br>聞こえ方: ______</td></tr>""" % dict(
                d=f["did"], lv=LEVEL_JA[f["level"]], ts=f["t_seg"], te=te, lab=E(f["label"]), note=E(f["note"]), l=f["level"], t=max(0, te - 3), t2=te))
        return "\n".join(out)

    cs = lambda lv: sum(1 for c in listed if c["level"] == lv)
    page = """<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Coffee Prices 異音・途切れ候補 確認ページ(Trial、試聴用)</title>
<style>
body{font-family:"Meiryo","Hiragino Kaku Gothic ProN",sans-serif;max-width:1180px;margin:1.2em auto;padding:0 1em;line-height:1.55;color:#111}
h1{font-size:1.35em} h2{border-bottom:2px solid #333;padding-bottom:3px;margin-top:1.8em;font-size:1.12em}
table{border-collapse:collapse;width:100%%;font-size:.86em;margin:8px 0} th,td{border:1px solid #bbb;padding:5px 7px;vertical-align:top;text-align:left} th{background:#f0f0f0}
audio{width:100%%;min-width:360px;height:36px;display:block;margin:4px 0}
.note{background:#fffbe6;border:1px solid #e0d080;padding:9px 13px;font-size:.9em;margin:12px 0}
.conf{display:inline-block;padding:0 6px;border-radius:8px;font-size:.8em;color:#fff}.conf.high{background:#c0392b}.conf.medium{background:#e67e22}.conf.low{background:#7f8c8d}
button.jump{font-size:.85em;padding:2px 6px;cursor:pointer} .chk{font-size:.85em;color:#333} .sticky{position:sticky;top:0;background:#fff;border-bottom:2px solid #888;padding:6px 0;z-index:5}
.sticky audio{display:inline-block;width:46%%;min-width:360px}
</style></head><body>
<h1>Coffee Prices 異音・音声途切れ 候補確認ページ(Trial・試聴用)</h1>
<div class="note"><b>管理ID: FAMILY-X-COFFEE-FINAL-LISTENING-TONE-TRIAL-01(委任_01C)</b>。無料のローカル音声解析で拾った<b>「候補」</b>です。<b>異常の確定はしません</b>(ユーザーが聴いて判断)。
各候補は前後約3秒のクリップ(mp3)・スペクトログラム(緑線=候補時刻)・全編の該当位置へのジャンプボタンを備えています。
重点箇所: Standard Full Story Part 3「A coffee price tag may have its own hidden clock」の coffee 付近(下記 FOCUS)。
Production Validatorには接続していません。TTS方式: Gemini 3.8 Flash-Lite TTS(Batch、既存run音声の再解析のみ。新規TTS・API呼出なし)。
&larr; <a href="../../coffee_new_tone_01/index.html">Coffee完成版 通しページ(Standard/Advanced)</a></div>
<div class="sticky"><b>全編(Standard)</b> <audio id="ep_a2" controls preload="none" src="../../coffee_new_tone_01/a2/web/episode.mp3"></audio>
<b>全編(Advanced)</b> <audio id="ep_b1b" controls preload="none" src="../../coffee_new_tone_01/b1b/web/episode.mp3"></audio></div>
<h2>重点箇所(FOCUS)</h2>
<p style="font-size:.9em">検知器(clip/click/dropout/long_gap/edge/level_step/spec_jump)は、この箇所の前後1.0秒以内に候補を出していません(未検出)。聴いて異常があれば、どの種の異音かを教えてください。</p>
<table><tr><th>ID</th><th>場所</th><th>内容</th><th>再生</th><th>判断欄(表示のみ)</th></tr>
%(focus)s</table>
<h2>Standard 候補(%(n_a2)d件)</h2>
<table><tr><th>ID / 信頼度</th><th>segment / 時刻</th><th>症状 / 指標</th><th>近傍の語(local whisper)</th><th>再生・スペクトログラム</th><th>判断欄(表示のみ)</th></tr>
%(rows_a2)s</table>
<h2>Advanced 候補(%(n_b1b)d件)</h2>
<table><tr><th>ID / 信頼度</th><th>segment / 時刻</th><th>症状 / 指標</th><th>近傍の語(local whisper)</th><th>再生・スペクトログラム</th><th>判断欄(表示のみ)</th></tr>
%(rows_b1b)s</table>
<h2>全編の構成(開始秒・クリックで該当位置から再生)</h2>
<p style="font-size:.88em">Intro/Outro/Notification(SFX)は固定音源で読み上げなし。他は読み上げ(Aoede/Charon、記録voiceは各行参照)。</p>
<h3>Standard</h3><table><tr><th>再生</th><th>segment</th><th>長さ</th></tr>%(tl_a2)s</table>
<h3>Advanced</h3><table><tr><th>再生</th><th>segment</th><th>長さ</th></tr>%(tl_b1b)s</table>
<script>
document.querySelectorAll('button.jump').forEach(function(b){b.addEventListener('click',function(){
 var a=document.getElementById('ep_'+b.dataset.lv); a.currentTime=parseFloat(b.dataset.t); a.play().catch(function(){});});});
</script>
</body></html>
""" % dict(focus=focus_rows(), n_a2=cs("a2"), n_b1b=cs("b1b"), rows_a2=rows("a2"), rows_b1b=rows("b1b"), tl_a2=timeline_rows("a2"), tl_b1b=timeline_rows("b1b"))
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8", newline="\n").write(page.replace("%%", "%"))
    print("listed", len(listed), "a2", cs("a2"), "b1b", cs("b1b"), "asm_only", len(asm_only))


if __name__ == "__main__":
    main()

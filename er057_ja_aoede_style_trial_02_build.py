# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-STANDARD-JA-AOEDE-STYLE-TRIAL-02 委任_01: 正規化・mp3化・KPコーナー通し/通し連結・異音検知・試聴ページ・比較表(ローカル処理のみ。API/Production書込なし)。"""
import os, sys, json, html
sys.path.insert(0, os.getcwd())
import numpy as np
import soundfile as sf
import er002_common as common
import er003_b1_p9a_audio as p9a
import er003_v1_n3_01_assemble as asm
import er057_ja_aoede_style_trial_02 as t
import er057_audio_anomaly_detect_trial_01 as ad

g = t.g
OUT, PREV, TONE = t.OUT, t.PREV, g.TONE
PAGE = f"{t.ROOT}/user_test/coffee_ja_style_trial_02"
AUD = f"{PAGE}/audio"
os.makedirs(AUD, exist_ok=True)
TARGET = json.load(open(f"{TONE}/audit/gain_report.json", encoding="utf-8"))["target_rms"]
NUMS = ["num_one", "num_two", "num_three", "num_four", "num_five"]


def norm_stereo(mono):
    gain = p9a.compute_gain_for_target_rms(mono, TARGET)
    return p9a.mono_24k_to_stereo_target(mono * gain)


def rd(path):
    s, sr = common.read_wav_float(path)[:2]
    assert sr == common.SAMPLE_RATE
    return s


def save_mp3(name, stereo):
    sf.write(f"{AUD}/{name}.mp3", np.clip(stereo, -1, 1), p9a.TARGET_SAMPLE_RATE, format="MP3")


def build_corner(intro, nums, en, ja):
    seq = [intro, p9a.silence_stereo(0.5)]
    for i in range(5):
        seq.append(p9a.build_key_phrase_block(nums[i], en[i], ja[i], asm.SR, numbering_pause_seconds=asm.A2_KEY_PHRASE_NUMBERING_PAUSE_SECONDS))
    return np.concatenate(seq)


def load_results():
    R = {}
    for l in open(f"{OUT}/results_01.jsonl", encoding="utf-8"):
        r = json.loads(l); R[r["id"]] = r
    A = {}
    for l in open(f"{OUT}/asr_results_01.jsonl", encoding="utf-8"):
        r = json.loads(l); A[r["id"]] = r
    return R, A


def src(sid, nm_or_i, kind):
    """kind='D' -> segment name, 'C' -> kp index。基準P2/M2は01B既存raw、候補は本Trial raw。"""
    base = PREV if sid in ("P2", "M2") else t.OUT
    return f"{base}/raw/{sid}_{nm_or_i}.wav" if kind == "D" else f"{base}/raw/{sid}_kp{nm_or_i}.wav"


def main():
    R, A = load_results()
    assert len(R) == 80 and all(r["status"] == "OK" for r in R.values())
    intro = norm_stereo(rd(f"{TONE}/narration/key_phrases_intro.wav"))
    nums = [norm_stereo(rd(f"{TONE}/narration/{n}.wav")) for n in NUMS]
    en_k2 = [norm_stereo(rd(f"{PREV}/raw/K2_kp{i}.wav")) for i in range(1, 6)]   # 英語K2(Final v2採用)は既存を再利用
    manifest = {"target_rms": TARGET, "durations": {}, "anomaly": {}, "wav_sha256": {}}
    import hashlib

    def shaf(p):
        return hashlib.sha256(open(p, "rb").read()).hexdigest()
    # D(Preview/Comment)
    for sid in ["P2"] + list(t.R):
        segs = []
        for nm in g.SEG_NAMES:
            p = src(sid, nm, "D"); m = rd(p)
            manifest["wav_sha256"][f"{sid}_{nm}"] = shaf(p)
            manifest["durations"][f"{sid}_{nm}"] = round(len(m) / common.SAMPLE_RATE, 3)
            c, _ = ad.analyze(m, common.SAMPLE_RATE, f"{sid}_{nm}", True)
            manifest["anomaly"][f"{sid}_{nm}"] = [x.get("symptom") + ":" + str(x.get("confidence")) for x in c]
            s = norm_stereo(m); segs.append(s); save_mp3(f"{sid}_{nm}", s)
        seq = []
        for k, s in enumerate(segs):
            if k: seq.append(p9a.silence_stereo(0.8))
            seq.append(s)
        full = np.concatenate(seq); save_mp3(f"{sid}_full", full)
        manifest["durations"][f"{sid}_full"] = round(len(full) / p9a.TARGET_SAMPLE_RATE, 2)
    # C(KP日本語意味)
    for sid in ["M2"] + list(t.Q):
        ja = []
        for i in range(1, 6):
            p = src(sid, i, "C"); m = rd(p)
            manifest["wav_sha256"][f"{sid}_kp{i}"] = shaf(p)
            manifest["durations"][f"{sid}_kp{i}"] = round(len(m) / common.SAMPLE_RATE, 3)
            c, _ = ad.analyze(m, common.SAMPLE_RATE, f"{sid}_kp{i}", True)
            manifest["anomaly"][f"{sid}_kp{i}"] = [x.get("symptom") + ":" + str(x.get("confidence")) for x in c]
            s = norm_stereo(m); ja.append(s); save_mp3(f"{sid}_kp{i}", s)
        corner = build_corner(intro, nums, en_k2, ja); save_mp3(f"{sid}_kp_corner", corner)
        manifest["durations"][f"{sid}_kp_corner"] = round(len(corner) / p9a.TARGET_SAMPLE_RATE, 2)
    json.dump(manifest, open(f"{OUT}/build_manifest_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    build_page(R, A, manifest)
    quality_table(R, A, manifest)
    print("built", len(os.listdir(AUD)), "mp3")


def aud(srcn, label, script="", voice="Aoede", extra=""):
    return (f'<div class="a"><span class="lbl">{html.escape(label)}</span><audio controls preload="none" src="audio/{srcn}.mp3"></audio>'
            f'<span class="v">{html.escape(voice)}</span><span class="s">{html.escape(script)}</span>{extra}</div>')


def asr_badge(A, key):
    a = A[key]
    cls = a["classification"]
    ok = cls in ("EXACT_MATCH", "NORMALIZED_MATCH")
    return f'<span class="asr {"ok" if ok else "warn"}">ASR: {cls}</span>'


def kp_table(kp):
    return ('<table class="kp">' + "".join(f"<tr><td>{html.escape(k['en'])}</td><td>{html.escape(k['ja'])}</td></tr>" for k in kp) + "</table>")


def build_page(R, A, M):
    kp, segs = g.load_texts()
    H = ["""<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Coffee Standard 日本語 Style Trial 02(Aoede)</title>
<style>body{font-family:sans-serif;max-width:1000px;margin:1em auto;padding:0 1em;line-height:1.5}h2{border-bottom:2px solid #888;margin-top:2em}
h3{margin-bottom:.2em}.set{border:1px solid #ccc;border-radius:6px;padding:.6em 1em;margin:1em 0}.a{display:flex;align-items:center;gap:.6em;margin:.2em 0;flex-wrap:wrap}
.a .lbl{min-width:9em;font-size:.9em}.a .v{font-size:.8em;color:#06c;min-width:4em}.a .s{font-size:.85em;color:#333;flex:1 1 20em}audio{height:32px;min-width:360px}
pre{white-space:pre-wrap;background:#f5f5f5;padding:.5em;font-size:.8em}.note{color:#555;font-size:.9em}.aim{font-size:.9em;color:#333}table{border-collapse:collapse}td,th{border:1px solid #ccc;padding:2px 6px}
.asr{font-size:.75em;padding:1px 5px;border-radius:4px}.asr.ok{background:#dfd}.asr.warn{background:#fed}</style></head><body>
<h1>Coffee Standard 日本語 Style Trial 02(試聴用・Trial)</h1>
<p class="note">Standard日本語(Voice=Aoede、model=gemini-3.8-flash-lite-tts、speech_metadata方式、Standard同期のDEV Trial)の追加探索です。Productionではなく、部品比較であり完成episodeではありません(Intro・Welcome・Full Storyは対象外)。基準は、直前のFinal v2に採用した「基準(P2)」(Preview/Comment用)と「基準(M2)」(Key Phrase日本語意味用)で、既存音声を再利用しています。R1〜R8(Preview/Comment用)・Q1〜Q8(日本語意味用)は、基準を中心に方向を変えた追加候補です(Blindにせず調整内容を併記)。音量は現行assembleと同じ目標RMSに正規化済み。どれが良いかはこのページでは判定していません。ASR表示は参考の機械判定で、NGでも再生成していません。</p>
<ul><li><a href="#pc">1. Preview/Comment1〜4(基準P2 + R1〜R8)</a></li><li><a href="#kj">2. Key Phrase日本語意味(基準M2 + Q1〜Q8)</a></li></ul>"""]
    H.append('<h2 id="pc">1. Preview/Comment1〜4</h2><p class="note">通し=preview→comment_1→2→3→4を0.8秒pauseで単純連結(Production assembleとは異なる試聴用)。各行は個別segment。Voice=Aoede。TTS方式=Standard同期(DEV Trial、Production既定=Batch)。</p>')

    def dset(sid, title, aim="", prompt="", chars=""):
        s = f'<div class="set"><h3>{title}</h3>'
        if aim: s += f'<div class="aim">調整内容・狙い: {html.escape(aim)}</div>'
        s += aud(f"{sid}_full", f"{sid} 通し", "preview→comment_1→2→3→4(単純連結)", "Aoede")
        for nm in g.SEG_NAMES:
            s += aud(f"{sid}_{nm}", f"{sid} {nm}", segs[nm]["manuscript"], "Aoede", asr_badge(A, f"{sid}_{nm}") + f' <span class="note">{M["durations"][f"{sid}_{nm}"]}s</span>')
        s += f'<details><summary>Prompt全文{chars}</summary><pre>{html.escape(prompt)}</pre></details></div>'
        return s
    H.append(dset("P2", "基準 P2(Final v2採用の現行Trial Style)", "J2逐語+「句読点を間として扱う」追記(基準)", t.P2, f"(J2+追記、{len(t.P2)}文字)"))
    for sid, (ap, aim, st) in t.R.items():
        H.append(dset(sid, f"{sid} {html.escape(ap)}", aim, st, f"({len(st)}文字、基準P2={len(t.P2)}文字、差{len(st)-len(t.P2):+d})"))
    H.append('<h2 id="kj">2. Key Phrase日本語意味</h2><p class="note">KPコーナー通し=key_phrases_intro → 0.5秒 → [番号 → 英語 → 日本語意味 → 英語(同一音声を再利用)]×5(現行assemble順を再現。Notification音は除く)。固定文言(intro・番号)と英語K2音声は既存を再利用し、日本語意味のみ差し替えています。Voice=Aoede(KP英語・日本語とも)。TTS方式=Standard同期(DEV Trial)。</p>')
    H.append('<div class="set"><h3>Key Phrases(原稿)</h3>' + kp_table(kp) + '</div>')

    def cset(sid, title, aim="", prompt="", chars=""):
        s = f'<div class="set"><h3>{title}</h3>'
        if aim: s += f'<div class="aim">調整内容・狙い: {html.escape(aim)}</div>'
        s += aud(f"{sid}_kp_corner", f"{sid} KPコーナー通し", "Key Phrasesコーナー全体(intro〜5件、日本語意味のみ差替)", "Aoede(KP)")
        for i in range(1, 6):
            s += aud(f"{sid}_kp{i}", f"{sid} 意味{i}", kp[i-1]["ja"], "Aoede", asr_badge(A, f"{sid}_kp{i}") + f' <span class="note">{M["durations"][f"{sid}_kp{i}"]}s</span>')
        s += f'<details><summary>Prompt全文{chars}</summary><pre>{html.escape(prompt)}</pre></details></div>'
        return s
    H.append(cset("M2", "基準 M2(Final v2採用の現行Trial Style)", "ひとまとまりの意味として滑らかに、ひと息で(基準)", t.M2, f"({len(t.M2)}文字)"))
    for sid, (ap, aim, st) in t.Q.items():
        H.append(cset(sid, f"{sid} {html.escape(ap)}", aim, st, f"({len(st)}文字、基準M2={len(t.M2)}文字、差{len(st)-len(t.M2):+d})"))
    H.append('<h2>原稿(逐語)</h2><table><tr><th>seg</th><th>text</th></tr>' + "".join(
        f"<tr><td>{nm}</td><td>{html.escape(s['manuscript'])}</td></tr>" for nm, s in segs.items()) + "</table></body></html>")
    open(f"{PAGE}/index.html", "w", encoding="utf-8").write("\n".join(H))


def quality_table(R, A, M):
    ids = ["P2"] + list(t.R)
    L = ["# QUALITY_COMPARISON_01(機械指標と所見の区別)\n",
         "## 機械指標(客観。Trial閾値不変の `er057_audio_anomaly_detect_trial_01.py` + Primary ASR判定 + 長さ)\n",
         "| ID | Prompt文字数 | 5seg合計長(s) | 通し長(s) | ASR EXACT/NORM/PHON/NG | 異音検知(件数: 詳細) |", "|---|---|---|---|---|---|"]
    def row(sid, chars, segids, full):
        dur = sum(M["durations"][x] for x in segids)
        c = {"EXACT_MATCH": 0, "NORMALIZED_MATCH": 0, "PHONETIC_MATCH": 0, "NG": 0}
        for x in segids:
            k = A[x]["classification"]; c[k if k in c else "NG"] += 1
        an = [f"{x}:{'/'.join(M['anomaly'][x])}" for x in segids if M["anomaly"][x]]
        return f"| {sid} | {chars} | {dur:.2f} | {M['durations'][full]} | {c['EXACT_MATCH']}/{c['NORMALIZED_MATCH']}/{c['PHONETIC_MATCH']}/{c['NG']} | {len(an)}: {'; '.join(an) if an else '-'} |"
    for sid in ids:
        L.append(row(sid, len(t.P2) if sid == "P2" else len(t.R[sid][2]), [f"{sid}_{n}" for n in g.SEG_NAMES], f"{sid}_full"))
    L += ["\n### KP日本語意味(M2/Q1〜Q8)\n", "| ID | Prompt文字数 | 5語合計長(s) | KPコーナー通し(s) | ASR EXACT/NORM/PHON/NG | 異音検知 |", "|---|---|---|---|---|---|"]
    for sid in ["M2"] + list(t.Q):
        L.append(row(sid, len(t.M2) if sid == "M2" else len(t.Q[sid][2]), [f"{sid}_kp{i}" for i in range(1, 6)], f"{sid}_kp_corner"))
    L += ["\n### ASR非PASS(EXACT/NORMALIZED以外)の内訳(警告記録。NGでも再生成していない)\n", "| ID | 判定 | 原稿 | ASR |", "|---|---|---|---|"]
    for k, a in A.items():
        if a["classification"] not in ("EXACT_MATCH", "NORMALIZED_MATCH"):
            L.append(f"| {k} | {a['classification']} | {a['canonical']} | {a['asr_text']} |")
    open(f"{OUT}/QUALITY_COMPARISON_01_metrics.md", "w", encoding="utf-8").write("\n".join(L))


if __name__ == "__main__":
    main()

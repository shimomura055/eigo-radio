# -*- coding: utf-8 -*-
"""委任_01B: 正規化・mp3化・KPコーナー通し/D通し連結・試聴ページ生成(ローカル処理のみ、API/Production書込なし)。"""
import os, sys, json, html
sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.join(os.getcwd()))
import numpy as np
import soundfile as sf
import er002_common as common
import er003_b1_p9a_audio as p9a
import er003_v1_n3_01_assemble as asm
import er057_tone_trial_kp_ja_gen_01 as g

OUT, PAGE, TONE = g.OUT, g.PAGE, g.TONE
AUD = f"{PAGE}/audio"
os.makedirs(AUD, exist_ok=True)
TARGET = json.load(open(f"{TONE}/audit/gain_report.json", encoding="utf-8"))["target_rms"]   # 現行Production assemble同一の目標RMS
NUMS = ["num_one", "num_two", "num_three", "num_four", "num_five"]


def norm_stereo(mono):
    gain = p9a.compute_gain_for_target_rms(mono, TARGET)
    return p9a.mono_24k_to_stereo_target(mono * gain)


def rd(path):
    s, sr = common.read_wav_float(path)[:2]
    assert sr == common.SAMPLE_RATE
    return s


def save_mp3(name, stereo):
    p = f"{AUD}/{name}.mp3"
    sf.write(p, np.clip(stereo, -1, 1), p9a.TARGET_SAMPLE_RATE, format="MP3")
    return p


def build_corner(intro, nums, en, ja):
    seq = [intro, p9a.silence_stereo(0.5)]
    for i in range(5):
        seq.append(p9a.build_key_phrase_block(nums[i], en[i], ja[i], asm.SR, numbering_pause_seconds=asm.A2_KEY_PHRASE_NUMBERING_PAUSE_SECONDS))
    return np.concatenate(seq)


def main():
    R = {}
    for l in open(f"{OUT}/results_01B.jsonl", encoding="utf-8"):
        r = json.loads(l)
        R[r["id"]] = r
    assert all(r["status"] == "OK" for r in R.values()) and len(R) == 75
    intro = norm_stereo(rd(f"{TONE}/narration/key_phrases_intro.wav"))
    nums = [norm_stereo(rd(f"{TONE}/narration/{n}.wav")) for n in NUMS]
    # --- Baseline(既存run dirの現行音声を同一正規化) ---
    base_en = [norm_stereo(rd(f"{TONE}/narration/kp{i}_en.wav")) for i in range(1, 6)]
    base_ja = [norm_stereo(rd(f"{TONE}/narration/meaning_{i}.wav")) for i in range(1, 6)]
    manifest = {"target_rms": TARGET, "files": {}}
    for i in range(5):
        save_mp3(f"base_en_kp{i+1}", base_en[i]); save_mp3(f"base_ja_kp{i+1}", base_ja[i])
    corner_base = build_corner(intro, nums, base_en, base_ja)
    save_mp3("base_kp_corner", corner_base)
    manifest["files"]["base_kp_corner_s"] = round(len(corner_base) / p9a.TARGET_SAMPLE_RATE, 2)
    # --- Bセット/Cセット(英語K n + 日本語M n) ---
    for n in range(1, 6):
        en = [norm_stereo(rd(f"{g.RAW}/K{n}_kp{i}.wav")) for i in range(1, 6)]
        ja = [norm_stereo(rd(f"{g.RAW}/M{n}_kp{i}.wav")) for i in range(1, 6)]
        for i in range(5):
            save_mp3(f"K{n}_kp{i+1}", en[i]); save_mp3(f"M{n}_kp{i+1}", ja[i])
        c = build_corner(intro, nums, en, ja)
        save_mp3(f"set{n}_kp_corner", c)
        manifest["files"][f"set{n}_kp_corner_s"] = round(len(c) / p9a.TARGET_SAMPLE_RATE, 2)
    # --- D: 5segment個別+通し(preview→comment_1→…を0.8秒pauseで連結) ---
    def d_set(prefix, loader):
        segs = [norm_stereo(loader(nm)) for nm in g.SEG_NAMES]
        for nm, s in zip(g.SEG_NAMES, segs):
            save_mp3(f"{prefix}_{nm}", s)
        seq = []
        for k, s in enumerate(segs):
            if k:
                seq.append(p9a.silence_stereo(0.8))
            seq.append(s)
        full = np.concatenate(seq)
        save_mp3(f"{prefix}_full", full)
        manifest["files"][f"{prefix}_full_s"] = round(len(full) / p9a.TARGET_SAMPLE_RATE, 2)
    d_set("base", lambda nm: rd(f"{TONE}/narration/{nm}.wav"))
    for n in range(1, 6):
        d_set(f"P{n}", lambda nm, n=n: rd(f"{g.RAW}/P{n}_{nm}.wav"))
    # --- baseline sha ---
    manifest["baseline_sha256"] = {f: g.sha(f"{TONE}/narration/{f}.wav") for f in
                                   [f"kp{i}_en" for i in range(1, 6)] + [f"meaning_{i}" for i in range(1, 6)] + NUMS +
                                   ["key_phrases_intro", "preview", "comment_1", "comment_2", "comment_3", "comment_4"]}
    manifest["baseline_dir"] = TONE
    json.dump(manifest, open(f"{OUT}/build_manifest_01B.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    build_page(R, manifest)
    print("built", len(os.listdir(AUD)), "mp3")


def aud(src, label, script="", voice=""):
    # Gate 7(l): 再生ボタン・voice名・scriptを同一行に置く。audioは最低幅360px。
    return (f'<div class="a"><span class="lbl">{html.escape(label)}</span><audio controls preload="none" src="audio/{src}.mp3"></audio>'
            f'<span class="v">{html.escape(voice)}</span><span class="s">{html.escape(script)}</span></div>')


def kp_table(kp):
    # Gate 7(n): Key Phrasesは左=英語・右=日本語の2列、ラベル文字列なし
    return ('<table class="kp">' +
            "".join(f"<tr><td>{html.escape(k['en'])}</td><td>{html.escape(k['ja'])}</td></tr>" for k in kp) + "</table>")


def build_page(R, manifest):
    kp, segs = g.load_texts()
    H = ["""<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Coffee Tone Trial 01B: Key Phrases / 日本語Preview・Comment</title>
<style>body{font-family:sans-serif;max-width:980px;margin:1em auto;padding:0 1em;line-height:1.5}h2{border-bottom:2px solid #888;margin-top:2em}
h3{margin-bottom:.2em}.set{border:1px solid #ccc;border-radius:6px;padding:.6em 1em;margin:1em 0}.a{display:flex;align-items:center;gap:.6em;margin:.2em 0}
.a{flex-wrap:wrap}.a .lbl{min-width:10em;font-size:.9em}.a .v{font-size:.8em;color:#06c;min-width:4em}.a .s{font-size:.85em;color:#333;flex:1 1 20em}audio{height:32px;min-width:360px}pre{white-space:pre-wrap;background:#f5f5f5;padding:.5em;font-size:.8em}.note{color:#555;font-size:.9em}table{border-collapse:collapse}td,th{border:1px solid #ccc;padding:2px 6px}</style></head><body>
<h1>Coffee Tone Trial 01B(試聴用・Trial)</h1>
<p class="note">Standard向けTrial候補の比較ページです(Productionではありません。部品比較であり完成episodeではありません、Intro/Full Storyは対象外)。model=gemini-3.8-flash-lite-tts、speech_metadata方式、Voice=Aoede(KP英語・日本語とも)。原稿は既存Coffee run_e_toneから逐語。音量は現行assembleと同じ目標RMSに正規化済み。名称は中立(K/M/P)で、各案のアプローチは説明のとおりです。どれが良いかはこのページでは判定していません。</p>
<ul><li><a href="#kp">1. Key Phrasesコーナー通し(5セット+既存)</a></li><li><a href="#kpe">2. 英語Phrase単独(K1〜K5)</a></li><li><a href="#kpj">3. 日本語意味単独(M1〜M5)</a></li><li><a href="#dj">4. Standard日本語 Preview/Comment1〜4(P1〜P5)</a></li></ul>"""]
    # 1
    H.append('<h2 id="kp">1. Key Phrasesコーナー通し(Standard)</h2><p class="note">key_phrases_intro → 0.5秒 → [番号 → 英語 → 日本語意味 → 英語(同一音声を再利用)]×5(現行assemble順を再現。Notification音は除く)。'
             '固定文言(intro「Here are today&#39;s key phrases.」・番号「One.」〜「Five.」)は既存run音声をそのまま使用(再生成なし)。セットn=英語Kn+日本語Mn。英語・日本語ともVoice=Aoede。</p>')
    H.append('<div class="set"><h3>Key Phrases(原稿)</h3>' + kp_table(kp) + '</div>')
    H.append('<div class="set"><h3>既存版(現行Production Style)</h3>' + aud("base_kp_corner", "既存版 通し", "Key Phrasesコーナー全体(intro〜5件)", "Aoede(KP)") + "</div>")
    for n in range(1, 6):
        H.append(f'<div class="set"><h3>セット{n}: 英語K{n} + 日本語M{n}</h3>' + aud(f"set{n}_kp_corner", f"セット{n} 通し", "Key Phrasesコーナー全体(intro〜5件)", "Aoede(KP)") +
                 f'<div class="note">K{n}: {html.escape(g.B_SPECS[f"K{n}"][0])} / M{n}: {html.escape(g.C_SPECS[f"M{n}"][0])}</div></div>')
    # 2
    H.append('<h2 id="kpe">2. 英語Phrase単独</h2><p class="note">Standard/Advanced共通のKey Phrase英語(同一関数・Style・Master Store再利用のため両レベル共通のTrial。初回・繰り返しとも同一音声)。TTS方式=Standard同期(DEV Trial、Production既定=Batch)。</p>')
    H.append('<div class="set"><h3>既存版</h3>' + "".join(aud(f"base_en_kp{i}", f"既存 {i}", kp[i-1]["en"], "Aoede") for i in range(1, 6)) + "</div>")
    for n in range(1, 6):
        sid = f"K{n}"
        H.append(f'<div class="set"><h3>{sid} {html.escape(g.B_SPECS[sid][0])}</h3>' + "".join(aud(f"{sid}_kp{i}", f"{sid}-{i}", kp[i-1]["en"], "Aoede") for i in range(1, 6)) +
                 f'<details><summary>Prompt全文</summary><pre>{html.escape(g.B_SPECS[sid][1])}</pre></details></div>')
    # 3
    H.append('<h2 id="kpj">3. 日本語意味単独(Standard)</h2><p class="note">TTS方式=Standard同期(DEV Trial、Production既定=Batch)。</p>')
    H.append('<div class="set"><h3>既存版(現行J2)</h3>' + "".join(aud(f"base_ja_kp{i}", f"既存 {i}", kp[i-1]["ja"], "Aoede") for i in range(1, 6)) + "</div>")
    for n in range(1, 6):
        sid = f"M{n}"
        H.append(f'<div class="set"><h3>{sid} {html.escape(g.C_SPECS[sid][0])}</h3>' + "".join(aud(f"{sid}_kp{i}", f"{sid}-{i}", kp[i-1]["ja"], "Aoede") for i in range(1, 6)) +
                 f'<details><summary>Prompt全文</summary><pre>{html.escape(g.C_SPECS[sid][1])}</pre></details></div>')
    # 4
    H.append('<h2 id="dj">4. Standard日本語 Preview/Comment1〜4</h2><p class="note">現行J2(明るさ・抑揚)を土台に、句読点付近の不自然な音程の上下の是正方向を変えた5案。通し=preview→comment_1→…→comment_4を0.8秒pauseで単純連結。Voice=Aoede、TTS方式=Standard同期(DEV Trial)。</p>')
    def dset(prefix, title, extra=""):
        s = f'<div class="set"><h3>{title}</h3>' + aud(f"{prefix}_full", f"{prefix} 通し", "preview→comment_1→2→3→4(単純連結)", "Aoede")
        for nm in g.SEG_NAMES:
            s += aud(f"{prefix}_{nm}", f"{prefix} {nm}", segs[nm]["manuscript"], "Aoede")
        return s + extra + "</div>"
    H.append(dset("base", "既存版(現行J2)"))
    for n in range(1, 6):
        sid = f"P{n}"
        H.append(dset(sid, f"{sid} {html.escape(g.D_SPECS[sid][0])}",
                      f'<details><summary>Prompt全文(J2+追記)</summary><pre>{html.escape(g.D_SPECS[sid][1])}</pre></details>'))
    H.append('<h2>原稿(逐語)</h2><table><tr><th>seg</th><th>text</th></tr>' + "".join(
        f"<tr><td>{nm}</td><td>{html.escape(s['manuscript'])}</td></tr>" for nm, s in segs.items()) + "</table></body></html>")
    open(f"{PAGE}/index.html", "w", encoding="utf-8").write("\n".join(H))


if __name__ == "__main__":
    main()

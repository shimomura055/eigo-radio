# -*- coding: utf-8 -*-
"""Comment4 Trial 比較試聴ページ生成(Trial専用静的ページ、Production不変)。各候補: Comment 4 -> (0.8s) -> In One Line(v4既存音声)。"""
import os, sys, json, html, hashlib
sys.path.insert(0, os.getcwd())
import numpy as np, soundfile as sf
from scipy.signal import resample_poly
import er057_tone_trial_final_build_03_asm as A
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = f"{ROOT}/er057_output/coffee_comment4_trial_01"
WEB = f"{ROOT}/user_test/coffee_comment4_trial_01"
V4A = f"{ROOT}/user_test/coffee_final_v4/audio"
SR = A.SR; GAP = 0.8
esc = html.escape


def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def load48(p):
    x, sr = sf.read(p, always_2d=True)
    if sr != SR: x = np.stack([resample_poly(x[:, c], SR, sr) for c in range(x.shape[1])], 1)
    if x.shape[1] == 1: x = np.repeat(x, 2, 1)
    return x
def rms(x): return float(np.sqrt(np.mean(x ** 2)))


def main():
    os.makedirs(f"{WEB}/audio", exist_ok=True)
    iol = load48(f"{V4A}/std_23.mp3"); c0 = load48(f"{V4A}/std_22.mp3"); tgt = rms(c0)
    gen = {(r["cand"], r["run"]): r for r in map(json.loads, open(f"{OUT}/generations.jsonl", encoding="utf-8"))}
    asr = {r["id"]: r for r in map(json.loads, open(f"{OUT}/asr_results.jsonl", encoding="utf-8"))}
    sel = json.load(open(f"{OUT}/selection.json", encoding="utf-8"))["reps"]
    J2 = f"{ROOT}/er057_output/ja_aoede_style_trial_02"
    items = [("C0", "C0 現行Prompt(v4現行Comment 4音声、そのまま)", "v4既存(再生成せず再利用)", c0, gen[("C0", 1)]["text"] and "コーヒー豆の値段が下がっても、店の値札がすぐに変わるとは限りません。値段が変わる時期には、豆以外の費用も関わります。続いて、記事の要点を英語で聞いていきましょう。", "P2_comment_4"),
             ("C0R2", "C0(R2スタイル、既存Trial音声)", "既存R2_comment_4(同文、R2)を再利用", load48(f"{J2}/raw/R2_comment_4.wav"), "コーヒー豆の値段が下がっても、店の値札がすぐに変わるとは限りません。値段が変わる時期には、豆以外の費用も関わります。続いて、記事の要点を英語で聞いていきましょう。", "R2_comment_4")]
    for k, n in sel.items():
        items.append((k, f"{k} 改善候補(run{n})", "今回生成(R2スタイル、Aoede、gemini-3.8-flash-lite-tts)", load48(f"{OUT}/raw/{k}_run{n}.wav"), gen[(k, n)]["text"], f"{k}_run{n}"))
    rows = []; man = []
    for key, title, origin, cm, text, aid in items:
        if key not in ("C0",): cm = cm * (tgt / rms(cm))
        peak = float(np.max(np.abs(cm)))
        if peak > 0.98: cm = cm * (0.98 / peak)
        full = np.concatenate([cm, np.zeros((int(GAP * SR), 2)), iol])
        fn_full, fn_c = f"{key}_comment4_to_iol.mp3", f"{key}_comment4_only.mp3"
        A.to_mp3(full, f"{WEB}/audio/{fn_full}", br="96k"); A.to_mp3(cm, f"{WEB}/audio/{fn_c}", br="96k")
        a = asr[aid]
        rows.append(f"<tr id='{key}'><td class='id'><b>{esc(title)}</b><br><span class='s'>{esc(origin)}</span></td><td class='play'>"
                    f"Comment 4 → In One Line(連続)<br><audio controls preload='none' src='audio/{fn_full}'></audio><br>Comment 4のみ<br><audio controls preload='none' src='audio/{fn_c}'></audio></td>"
                    f"<td><div class='script'>{esc(text)}</div><div class='s'>ASR判定: {esc(a['classification'])}(Primary、ja-JP)</div></td></tr>")
        man.append({"key": key, "title": title, "origin": origin, "comment_rms_target": tgt, "full_mp3": fn_full, "comment_only_mp3": fn_c, "text": text, "asr": a["classification"],
                    "full_sha256": sha(f"{WEB}/audio/{fn_full}")})
    iol_text = json.load(open(f"{ROOT}/er057_output/coffee_final_audio_assembly_01/iol_final_text_01.json", encoding="utf-8"))["std"]
    page = ("<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><title>Coffee Standard Comment 4 候補比較(Trial)</title><meta name='viewport' content='width=device-width, initial-scale=1'>"
            "<style>body{font-family:sans-serif;max-width:1100px;margin:1em auto;padding:0 1em;line-height:1.5}table{border-collapse:collapse;width:100%}th,td{border:1px solid #ccc;padding:6px;vertical-align:top;text-align:left}"
            "td.id{width:200px}td.play{min-width:340px}audio{width:100%}.script{background:#f6f6f6;padding:4px}.s{color:#666;font-size:.85em}</style></head><body>"
            "<h1>Coffee Standard Comment 4 候補比較(Trial)</h1>"
            "<p class='s'>Trial専用ページ(Production Promptではありません)。Comment 4から In One Line(v4既存音声)へつながる自然さを聞き比べてください。候補はTTS Comment Style R2・Aoede・gemini-3.8-flash-lite-tts。C0はv4現行音声(スタイル表示P2)とR2版の両方を置いています。音量はv4現行Comment 4のRMSに揃えています。Comment 4とIn One Lineの間は0.8秒(v4通しと同じ)。</p>"
            f"<p><b>In One Line(固定、v4):</b> {esc(iol_text)}</p>"
            "<table><tr><th>候補</th><th>音声</th><th>原稿 / ASR</th></tr>" + "".join(rows) + "</table></body></html>")
    open(f"{WEB}/index.html", "w", encoding="utf-8").write(page)
    json.dump({"items": man}, open(f"{OUT}/page_manifest.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    assert "file:///" not in page and "C:\\" not in page
    print("ok", len(man))


main()

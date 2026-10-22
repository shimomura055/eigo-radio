# -*- coding: utf-8 -*-
"""第2巡 試聴ページ(API 0)。user_test/pnps_stage2_hr7_listen_02/index.html。新規音声は読み取りのみ(mp3変換コピー)。
使い方: python er100_pnps_stage2_trial_01_r2_page.py --out user_test/pnps_stage2_hr7_listen_02"""
import argparse, hashlib, html, json, os, subprocess, sys
sys.path.insert(0, os.getcwd())
import imageio_ffmpeg
from pathlib import Path
from er100_pnps_stage2_trial_01_common import *
import er100_pnps_stage2_trial_01_r2_arms as AR
import er100_pnps_stage2_trial_01_r2_replay as RPL

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
A = ap.parse_args()
OUTD = A.out
os.makedirs(f"{OUTD}/audio", exist_ok=True)
R2 = Path(OUT) / "r2"
agg = json.load(open(R2 / "agg.json", encoding="utf-8"))
HEAD = agg["headline"]
est, S, AA, ARMD = RPL.load_sets()
esc = html.escape


def mp3(src, tag):
    h = hashlib.sha256(open(src, "rb").read()).hexdigest()[:10]
    dst = f"{OUTD}/audio/{tag}_{h}.mp3"
    if not os.path.exists(dst):
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", src, "-ac", "1", "-codec:a", "libmp3lame", "-b:a", "40k", dst], check=True)
    return f"audio/{os.path.basename(dst)}"


def hl(text, word):
    key = word.lower().replace("canele", "canel")
    i = text.lower().find(key)
    if i < 0:
        return esc(text)
    j = i + len(key)
    while j < len(text) and (text[j].isalnum() or text[j] in "é'’"):
        j += 1
    return esc(text[:i]) + "<mark>" + esc(text[i:j]) + "</mark>" + esc(text[j:])


def vc(v):
    cls = {"PASS_WITH_WARNING": "pw", "NG": "ng"}.get(v.split("(")[0], "hr")
    return f'<span class="{cls}">{esc(v)}</span>'


def arm_row(verdicts):
    return "<table><tr>" + "".join(f"<th>{a}</th>" for a in AR.ARMS) + "</tr><tr>" + "".join(f"<td>{vc(verdicts[a])}</td>" for a in AR.ARMS) + "</tr></table>"


def accepted_html(w):
    s = ARMD[w]
    return (f"受理集合(R1 EXT)={esc(' | '.join(' '.join(x) for x in sorted(s['R1_EXT'])) or '空')} ／ 新arm(N3以降)={esc(' | '.join(' '.join(x) for x in sorted(s['n3'])) or '空')}"
            f"<br><small>推定E2={esc('; '.join(s['sources']['E2']))} ／ E3(+N-best)={esc('; '.join(s['sources']['E3']))} ／ 取得={esc('; '.join(s['retrieved']) or 'なし')}</small>")


def card(title, wav, clip_note, text, word, strings, verdicts, note="", scope=""):
    d = Path(wav)
    full = mp3(str(d), "full") if d.exists() else None
    clip = d.with_name(d.stem + "__clip.wav")
    cl = mp3(str(clip), "clip") if clip.exists() else None
    h = [f"<div class='card'><b>{esc(title)}</b> <small>{esc(scope)}</small><br>"]
    if cl:
        h.append(f"対象文の窓: <audio controls preload='none' src='{cl}'></audio> ")
    if full:
        h.append(f"全体: <audio controls preload='none' src='{full}'></audio>")
    h.append(f"<br><small>{hl(text, word)}</small><br>")
    h.append("<table><tr>" + "".join(f"<th>{esc(k)}</th>" for k in strings) + "</tr><tr>" + "".join(f"<td>{esc(str(v) if v is not None else '(未観測/整列不能)')}</td>" for v in strings.values()) + "</tr></table>")
    h.append(arm_row(verdicts))
    h.append(f"<small>{accepted_html(word)}</small>")
    if note:
        h.append(f"<br><small>{esc(note)}</small>")
    h.append("</div>")
    return "\n".join(h)


H = ["<!doctype html><html lang='ja'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>固有名詞発音 Stage 2 Trial 第2巡 試聴</title>",
     "<style>body{font-family:sans-serif;max-width:1050px;margin:1em auto;padding:0 1em;line-height:1.5}h2{border-bottom:2px solid #444;margin-top:2em}.card{border:1px solid #bbb;border-radius:6px;padding:.6em .8em;margin:.8em 0}mark{background:#ffe08a}.pw{color:#065f46;font-weight:bold}.ng{color:#b91c1c;font-weight:bold}.hr{color:#92400e}table{border-collapse:collapse;font-size:.85em}td,th{border:1px solid #ccc;padding:2px 6px;vertical-align:top}small{color:#555}.warn{background:#fff3cd;padding:.5em;border-radius:4px}</style></head><body>",
     "<h1>固有名詞発音 Stage 2 Trial 第2巡 試聴ページ</h1>",
     "<p class='warn'>Trialの試聴用です(Production未採用)。音声は現行TTS(gemini-3.8-flash-lite-tts、Aoede、PD06 style)で今回新規に生成したものです。「判定」は機械replayで、正しい発音の保証ではありません(PASS_WITH_WARNINGは「誤発音と機械判定されなかった」の意味)。正否は耳で確認してください。ASR(Primary/Azure)は対象語を含む文の窓に対する書き起こしです(Whisper small/mediumは全体音声)。</p>",
     f"<p>見出しarm = <b>{esc(HEAD)}</b>。arm名: R1_V4/R1_EXT=第1巡、N1=縮約、N2=+弱化母音、N3=+2出所支持、N4=+ASR側G2P、N5=+母音1つ差は判定不能、N6=+Whisper一致要件。</p>"]
segs = [s for s in agg["segments"] if "seg_verdict" in s]
# A: PASS_WITH_WARNING(見出しarm または いずれかのarm)
passes = [s for s in segs if any(s["seg_verdict"][a] == "PASS_WITH_WARNING" for a in AR.ARMS if a != "R1_V4")]
H.append(f"<h2>A. 新方式でPASS_WITH_WARNINGになった新規音声({len(passes)}本・全数)</h2>")
if not passes:
    H.append("<p>該当なし。</p>")
for s in passes:
    for w, pw in s["per_word"].items():
        H.append(card(f"{s['id']}/{s['take']} 語={w} (現行Production判定のプロキシ={s['current_prod_proxy']}、元のHR事象{s['hr_events_orig']}件)", s["wav"], "", s["text"], w, pw["strings"],
                      pw["verdicts"], note="Primary単独の正しい綴りは判定根拠に数えていません。" + ("他の未解決span(%s)があるためsegment全体はPASSにしません。" % ",".join(s["other_unresolved_blocking"]) if s["other_unresolved_blocking"] else ""), scope=s.get("api_scope") or ""))
# B: Melos said.
H.append("<h2>B. 「Melos said.」(HR queueで28事象の反復だったsegment)</h2>")
for s in segs:
    if s["id"] == "s28":
        for w, pw in s["per_word"].items():
            H.append(card(f"{s['id']}/{s['take']}(現行TTS新規)", s["wav"], "", s["text"], w, pw["strings"], pw["verdicts"], note="取得・推定の受理集合が空のため、どのarmでもPASSにはなりません(Melosの同定は未確認)。"))
for n in agg["negatives"]:
    if n.get("id", "").startswith("n_melos_F2") or n.get("id", "").startswith("n_melos_C2"):
        H.append(card(f"負例 {n['id']} (TTS入力『{n['tts_text']}』)", n["wav"], "", "Melos said.", "melos", n["strings"], n["verdicts"], note=f"誤読確認={n['misread_confirmed']}(逸脱エンジン={n['deviating_engines']})。F2『Melo said.』は縮約(次語がS始まり)と区別できません。"))
# C: 負例
conf = [n for n in agg["negatives"] if n.get("misread_confirmed")]
split = [n for n in agg["negatives"] if "verdicts" in n and (len({v.split("(")[0] for v in n["verdicts"].values()}) > 1 or n["verdicts"][HEAD] == "PASS_WITH_WARNING" or not n["misread_confirmed"])]
H.append(f"<h2>C. 負例(意図した誤読)のうち判定がarm間で割れたもの/誤読が確認できなかったもの({len(split)}本)</h2>")
for n in split:
    H.append(card(f"{n['id']} (TTS入力文: {n['tts_text']})", n["wav"], "", n["tts_text"], n["word"], n["strings"], n["verdicts"], note=f"誤読確認={n['misread_confirmed']}(逸脱エンジン: {', '.join(n['deviating_engines'])})。Primary正綴り={n['primary_exact']}"))
# D: 全segment一覧
H.append("<h2>D. 新規生成30 segmentの判定一覧(現行TTS)</h2><table><tr><th>seg/take</th><th>語</th><th>現行(プロキシ)</th>" + "".join(f"<th>{a}</th>" for a in AR.ARMS) + "<th>ASR(Primary / Azure)</th></tr>")
for s in segs:
    w0 = list(s["per_word"])[0]
    H.append(f"<tr><td>{s['id']}/{s['take']}</td><td>{esc(','.join(s['words']))}</td><td>{s['current_prod_proxy']}</td>" + "".join(f"<td>{vc(s['seg_verdict'][a])}</td>" for a in AR.ARMS) +
             f"<td>{esc(str(s['per_word'][w0]['strings'].get('primary')))} / {esc(str(s['per_word'][w0]['strings'].get('azure')))}</td></tr>")
H.append("</table></body></html>")
open(f"{OUTD}/index.html", "w", encoding="utf-8").write("\n".join(H))
tot = sum(os.path.getsize(f"{OUTD}/audio/{f}") for f in os.listdir(f"{OUTD}/audio"))
print("audio files", len(os.listdir(f"{OUTD}/audio")), "bytes", tot)

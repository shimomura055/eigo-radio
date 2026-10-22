# -*- coding: utf-8 -*-
"""第3巡 試聴ページ(API 0)。user_test/pnps_stage2_hr7_listen_03/index.html。音声はmp3変換コピー(読み取りのみ)。
使い方: python er100_pnps_stage2_trial_01_r3_page.py --out user_test/pnps_stage2_hr7_listen_03"""
import argparse, hashlib, html, json, os, subprocess, sys
sys.path.insert(0, os.getcwd())
import imageio_ffmpeg
from pathlib import Path
from er100_pnps_stage2_trial_01_common import *
import er100_pnps_stage2_trial_01_r3_gen as G3

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
OUTD = ap.parse_args().out
os.makedirs(f"{OUTD}/audio", exist_ok=True)
R2 = Path(OUT) / "r2"
R3 = Path(OUT) / "r3"
agg = json.load(open(R3 / "agg.json", encoding="utf-8"))
r2agg = json.load(open(R2 / "agg.json", encoding="utf-8"))
esc = html.escape


def mp3(src, tag):
    h = hashlib.sha256(open(src, "rb").read()).hexdigest()[:10]
    dst = f"{OUTD}/audio/{tag}_{h}.mp3"
    if not os.path.exists(dst):
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", src, "-ac", "1", "-codec:a", "libmp3lame", "-b:a", "40k", dst], check=True)
    return f"audio/{os.path.basename(dst)}"


def audio_html(wav):
    d = Path(wav)
    h = ""
    clip = d.with_name(d.stem + "__clip.wav")
    if clip.exists():
        h += f"対象文の窓: <audio controls preload='none' src='{mp3(str(clip), 'clip')}'></audio> "
    if d.exists():
        h += f"全体: <audio controls preload='none' src='{mp3(str(d), 'full')}'></audio>"
    return h


def vc(v):
    cls = {"PASS_WITH_WARNING": "pw", "NG": "ng"}.get(str(v).split("(")[0], "hr")
    return f'<span class="{cls}">{esc(str(v))}</span>'


def yn(b):
    return '<span class="pw">PASS</span>' if b else '<span class="ng">no</span>'


def strings_tbl(d):
    return "<table><tr>" + "".join(f"<th>{esc(k)}</th>" for k in d) + "</tr><tr>" + "".join(f"<td>{esc(str(v) if v is not None else '(未整列)')}</td>" for v in d.values()) + "</tr></table>"


def card(e):
    w = e["word"]
    S = G3.SUPPLY[w]
    arm = {"R": "R 綴り置換", "R2": "R2 別綴り置換", "H": "H 発音ヒント注入", "N": "N 無供給"}[e["arm"]]
    head = f"{e['id']} / {e['take']} ・ {arm}" + (" ・ 【誤読対照:誤った読みを供給】" if e["wrong"] else "")
    sup = f"供給した読み=<b>{esc(str(e['supplied']))}</b>(取得した読み: {esc(S['hint'])} ／ 階層{S['tier']} ／ 出所: {esc(S['src'])})" if e["arm"] != "N" else "供給なし(対照)"
    h = [f"<div class='card'><b>{esc(head)}</b><br>{audio_html(e['wav'])}<br><small>期待語=<b>{esc(S['orig'])}</b> ／ {sup}</small><br>"]
    h.append(strings_tbl(e["per_word"][w]["strings"]))
    h.append(f"<small>原綴り比較: 現行プロキシ(Primary/Azureが原綴り一致)={yn(e['target_word_proxy_orig'])} ／ N5_UND={vc(e['target_word_N5'])} ／ R1_EXT={vc(e['target_word_R1_EXT'])}</small>")
    if "replaced" in e:
        r = e["replaced"]
        h.append(f"<br><small>置換後比較(Reicher方式): 比較語=<b>{esc(r['rep'])}</b>、Primary/Azure完全一致={yn(r['prod_exact_any'])}、音素一致(Primary&Azure)={yn(r['PASS_phon_all_prod'])}、4エンジン中一致={r['engines_match_of4']}。</small>")
    if e["unsupplied_target_words_in_segment"]:
        h.append(f"<br><small>同一segmentに供給不可の対象語({', '.join(e['unsupplied_target_words_in_segment'])})があるため、segment全体はHRのまま。</small>")
    h.append("</div>")
    return "\n".join(h)


def base_card(sid, take, w):
    b = next(x for x in agg["baseline_items"] if x["id"] == sid and x["take"] == take and x["word"] == w and x["src"] == "r2")
    wav = R2 / "audio" / f"{sid}__{take}.wav"
    return (f"<div class='card'><b>無供給対照(第2巡r2の同一segment・現行TTS) {sid}/{take}</b><br>{audio_html(str(wav))}<br><small>期待語=<b>{G3.SUPPLY[w]['orig']}</b>、供給なし</small><br>{strings_tbl(b['strings'])}"
            f"<small>原綴り比較: 現行プロキシ={yn(b['proxy_orig'])} ／ N5_UND={vc(b['N5'])}</small></div>")


items = agg["items"]
H = ["<!doctype html><html lang='ja'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>固有名詞発音 Stage 2 Trial 第3巡 試聴</title>",
     "<style>body{font-family:sans-serif;max-width:1050px;margin:1em auto;padding:0 1em;line-height:1.5}h2{border-bottom:2px solid #444;margin-top:2em}.card{border:1px solid #bbb;border-radius:6px;padding:.6em .8em;margin:.8em 0}.pw{color:#065f46;font-weight:bold}.ng{color:#b91c1c;font-weight:bold}.hr{color:#92400e}table{border-collapse:collapse;font-size:.85em}td,th{border:1px solid #ccc;padding:2px 6px}small{color:#555}.warn{background:#fff3cd;padding:.5em;border-radius:4px}</style></head><body>",
     "<h1>固有名詞発音 Stage 2 Trial 第3巡(TTS入力側の読み制御)試聴ページ</h1>",
     "<p class='warn'>Trialの試聴用です(Production未採用・Ledger/HR queue/Store無変更)。音声は現行TTS(gemini-3.8-flash-lite-tts、Aoede、PD06)で今回新規に生成。arm R=TTS入力の綴りを置換(Reicher→Riker方式)、arm H=styleへ発音ヒントを追記(本文は原綴り)。Khaite・Altuzarraの読みは報道/媒体の一致(B階層)、Meinkは本人Wikipedia記事(A階層相当)から取得したもので、B階層を供給してよいかはユーザー未承認です。「誤読対照」は意図的に誤った読みを供給した音声で、置換後比較ではPASSになり得ます(=この方式は供給した発音が正しいことに全面依存)。PASSは「機械判定で誤りと見なされなかった」の意味で、正否は耳で確認してください。</p>"]
for w, title in (("khaite", "Khaite(階層B: kate)"), ("meink", "Meink(階層A: MEENK)"), ("altuzarra", "Altuzarra(階層B: ahl-too-ZAH-rah)")):
    H.append(f"<h2>{title}</h2>")
    for e in sorted([x for x in items if x["word"] == w and not x["wrong"]], key=lambda x: (x["sid"], x["arm"], x["take"])):
        H.append(card(e))
    if w == "khaite":
        for sid in ("s09", "s12", "s13", "s16"):
            H.append(base_card(sid, "t1", w))
    if w == "meink":
        for sid in ("s02", "s03"):
            H.append(base_card(sid, "t1", w))
    if w == "altuzarra":
        H.append(base_card("s17", "t1", w))
H.append("<h2>誤読対照(誤った読みを供給した音声)</h2>")
for e in [x for x in items if x["wrong"]]:
    H.append(card(e))
H.append("<h2>供給不可の語(Toteme/Zabelina/Melos/Canele)</h2><p>取得なし・弱い根拠のため供給しません(HR維持)。無供給音声は第2巡試聴ページ(pnps_stage2_hr7_listen_02)を参照。</p></body></html>")
open(f"{OUTD}/index.html", "w", encoding="utf-8").write("\n".join(H))
tot = sum(os.path.getsize(f"{OUTD}/audio/{f}") for f in os.listdir(f"{OUTD}/audio"))
print("audio files", len(os.listdir(f"{OUTD}/audio")), "bytes", tot)

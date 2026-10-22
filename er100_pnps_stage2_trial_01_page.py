# -*- coding: utf-8 -*-
"""試聴ページ生成(API 0)。user_test/pnps_stage2_hr7_listen_01/index.html。既存音声は読み取りのみ(mp3へ変換コピー)。
使い方: python er100_pnps_stage2_trial_01_page.py --out user_test/pnps_stage2_hr7_listen_01"""
import argparse, hashlib, html, json, os, subprocess, sys, wave
sys.path.insert(0, os.getcwd())
import imageio_ffmpeg
from er100_pnps_stage2_trial_01_common import *

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
A = ap.parse_args()
OUTD = A.out
os.makedirs(f"{OUTD}/audio", exist_ok=True)
rep = json.load(open(f"{OUT}/replay_result.json", encoding="utf-8"))
att = json.load(open(f"{OUT}/attempts_replay_result.json", encoding="utf-8"))
p2 = json.load(open(f"{OUT}/p2_results.json", encoding="utf-8"))
rows = load_rows()
esc = html.escape
_cache = {}


def mp3(src, tag):
    h = hashlib.sha256(open(src, "rb").read()).hexdigest()[:12]
    dst = f"{OUTD}/audio/{tag}_{h}.mp3"
    if not os.path.exists(dst):
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", src, "-ac", "1", "-codec:a", "libmp3lame", "-b:a", "48k", dst], check=True)
    return f"audio/{os.path.basename(dst)}"


def dur(src):
    try:
        w = wave.open(src)
        return w.getnframes() / w.getframerate()
    except Exception:
        return None


def hint_t(canon, word, d):
    """概算位置(文字位置の比率からの目安。誤差あり)"""
    if not d:
        return 0
    i = canon.lower().find(word.lower().replace("canele", "canel"))
    if i < 0:
        return 0
    return max(0, int(d * i / max(1, len(canon)) - 3))


def hl(canon, word):
    key = word.lower().replace("canele", "canel")
    i = canon.lower().find(key)
    if i < 0:
        return esc(canon)
    j = i + len(key)
    while j < len(canon) and (canon[j].isalnum() or canon[j] in "é'’"):
        j += 1
    return esc(canon[:i]) + "<mark>" + esc(canon[i:j]) + "</mark>" + esc(canon[j:])


def asr_span_str(canon, txt, word):
    sp = asr_span(canon, txt, word)
    return (" ".join(sp) if sp is not None else "(整列不能)") + "   ← " + (txt or "")[:0]


def verd_cell(v):
    cls = {"PASS_WITH_WARNING": "pw", "NG": "ng"}.get(v.split("(")[0], "hr")
    return f'<span class="{cls}">{esc(v)}</span>'


def cards_for(word):
    out = []
    # 1) 最終保存wav(HR事象の代表行。別世代の可能性を明示)
    seen = set()
    for d in rep["detail"]:
        if d["word"] != word or not d["wav_exists"] or d["wav_path"] in seen:
            continue
        # その wav を指す最後の行
        last = [x for x in rep["detail"] if x["word"] == word and x["wav_path"] == d["wav_path"]][-1]
        seen.add(d["wav_path"])
        canon = rows[last["row"]]["canonical_text"]
        d0 = dur(last["wav_path"])
        src = mp3(last["wav_path"], "final")
        out.append({"kind": "最終保存wav(HR事象 行%d)" % last["row"], "src": src, "t": hint_t(canon, word, d0), "dur": d0, "canon": canon,
                    "note": "保存時刻とHR時刻が近い=同世代と推定" if last.get("same_generation_audio") else "保存wavはHR事象より後に再生成された別世代の可能性(ASR欄はHR事象時点のもの。Whisperは今回のwavへの転写)",
                    "asr": {k.replace("whisperREF_", "Whisper(今回wav・参考)_"): (" ".join(v) if isinstance(v, list) else v) for k, v in last["observations"].items()}, "v4": last["res"]["V4"]["verdict"], "ext": last["res"]["EXT"]["verdict"], "cur": "Human Review(現行)", "label": last["distinguish"]})
    # 2) attempt wav
    for a in att:
        if word in a["word"] and a["word"] == word:
            canon = None
            m = [r for r in rows if word in (r.get("pronunciation_lookups") or {}) and a["wav"].replace("\\", "/").split("/attempts/")[0] in r["wav_path"].replace("\\", "/")]
            canon = m[0]["canonical_text"] if m else ""
            d0 = dur(a["wav"])
            src = mp3(a["wav"], "att")
            out.append({"kind": "保存attempt音声(%s, %s)" % (os.path.basename(a["wav"]).split("_custom")[0].replace(".wav", ""), a["model"]), "src": src, "t": hint_t(canon, word, d0), "dur": d0, "canon": canon,
                        "note": "Production判定=%s / 分類=%s" % ("合格" if a["verified_in_production"] else "不合格", a["classification"]),
                        "asr": a["strings"], "v4": a["res"]["V4"]["prod_only"], "ext": a["res"]["EXT"]["prod_only"], "cur": "合格" if a["verified_in_production"] else "不合格(現行)", "label": ""})
    # 3) P2
    for p in p2:
        if p["word"] == word:
            d0 = p["sec"]
            src = mp3(p["wav"], "p2")
            out.append({"kind": "P2新規TTS(%s/%s)" % (p["set"], p["tag"]), "src": src, "t": 0, "dur": d0, "canon": p["canon"] + (" ／ TTS入力=" + p["tts_text"] if p["tts_text"] != p["canon"] else ""),
                        "note": "今回の実TTS(Gemini 3.8 flash-lite)。制御読みは期待の「合理的な読み/明確な誤発音」を人が作った入力", "asr": {k: asr_span_str(p["canon"], v, p["word"]) for k, v in p["asr"].items()},
                        "v4": p["verdicts"]["V4"]["verdict"], "ext": p["verdicts"]["EXT"]["verdict"], "cur": "(P2は現行判定の対象外)", "label": ""})
    return out


H = []
H.append("<!doctype html><html lang='ja'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>固有名詞発音 Stage 2 Trial 試聴</title>")
H.append("<style>body{font-family:sans-serif;max-width:1000px;margin:1em auto;padding:0 1em;line-height:1.5}h2{border-bottom:2px solid #444;margin-top:2em}.card{border:1px solid #bbb;border-radius:6px;padding:.6em .8em;margin:.8em 0}mark{background:#ffe08a}.pw{color:#065f46;font-weight:bold}.ng{color:#b91c1c;font-weight:bold}.hr{color:#92400e}table{border-collapse:collapse;font-size:.9em}td,th{border:1px solid #ccc;padding:2px 6px;vertical-align:top}small{color:#555}.warn{background:#fff3cd;padding:.5em;border-radius:4px}</style></head><body>")
H.append("<h1>固有名詞発音 Stage 2 Trial 試聴ページ(辞書外7語)</h1>")
H.append("<p class='warn'>これはTrialの試聴用です(Production未採用)。表示する「取得/推定した発音」はWebや推定から得た候補であり、<b>公式発音の保証ではありません</b>。「新方式の判定」は保存ASR転写への機械replayで、正しい/誤りの確定ではありません。正否は人の耳での確認が必要です。再生位置(#t)は文字位置からの概算の目安で、ずれることがあります。</p>")
for w in TARGETS:
    es = rep["estimator_sets"][w]
    acc = rep["accepted_sets"][w]
    H.append(f"<h2>{esc(w)}</h2>")
    H.append("<table><tr><th>区分</th><th>音素列(ARPAbet、ストレス除去)</th><th>出典/根拠</th></tr>")
    H.append(f"<tr><td>E2 G2P(g2p_en)</td><td>{esc('; '.join(es['E2']))}</td><td>綴りから決定論変換(推定)</td></tr>")
    H.append(f"<tr><td>E3 LLM(gpt-6-luna)</td><td>{esc('; '.join(es['E3']))}</td><td>web無しの推定</td></tr>")
    for r in es["retrieved"]:
        H.append(f"<tr><td>取得 {esc(r['type'])}</td><td>{esc(r['arpa'])}</td><td><a href='{esc(r['url'])}'>{esc(r['domain'])}</a> 原文「{esc(r['raw'])}」 <small>{esc(r['context'][:140])}</small></td></tr>")
    H.append(f"<tr><td>同定注記</td><td colspan=2>{esc(es['identity'][0])}: {esc(es['identity'][1])}</td></tr>")
    H.append(f"<tr><td>受理集合 V4 / EXT</td><td colspan=2>V4={esc(' | '.join(acc['V4']) or '(空=推定不成立)')} / EXT={esc(' | '.join(acc['EXT']) or '(空)')}</td></tr></table>")
    for c in cards_for(w):
        t = f"#t={c['t']}" if c.get("t") else ""
        H.append("<div class='card'>")
        H.append(f"<b>{esc(c['kind'])}</b> <small>{'%.1f秒' % c['dur'] if c.get('dur') else ''}</small><br>")
        H.append(f"<audio controls preload='none' src='{c['src']}{t}'></audio><br>")
        H.append(f"<small>{hl(c['canon'], w) if c['canon'] else ''}</small><br>")
        H.append("<table><tr>" + "".join(f"<th>{esc(k)}</th>" for k in c["asr"]) + "</tr><tr>" + "".join(f"<td>{esc(str(v) if v is not None else '(未観測)')}</td>" for v in c["asr"].values()) + "</tr></table>")
        H.append(f"現行: {esc(c['cur'])} ／ 新方式V4: {verd_cell(c['v4'])} ／ 新方式EXT(Trial内比較): {verd_cell(c['ext'])}<br>")
        if c["label"]:
            H.append(f"区別の候補: {esc(c['label'])}<br>")
        H.append(f"<small>{esc(c['note'])}</small></div>")
miss = [d for d in rep["detail"] if not d["wav_exists"]]
H.append(f"<h2>音声が保存されていないHR事象({len(miss)}件)</h2><p>Temp配下の一時wavで現在は存在しません(保存ASR転写のみで判定)。全件Melos(Family Z)で同一segment(c5)の繰り返しです。</p>")
H.append("</body></html>")
open(f"{OUTD}/index.html", "w", encoding="utf-8").write("\n".join(H))
tot = sum(os.path.getsize(f"{OUTD}/audio/{f}") for f in os.listdir(f"{OUTD}/audio"))
print("audio files", len(os.listdir(f"{OUTD}/audio")), "bytes", tot)

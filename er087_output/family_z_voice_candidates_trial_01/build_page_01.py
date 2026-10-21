# -*- coding: utf-8 -*-
import json, html, os, wave, lameenc
def to_mp3(src,dst):
    w=wave.open(src); e=lameenc.Encoder(); e.set_bit_rate(128); e.set_in_sample_rate(w.getframerate()); e.set_channels(w.getnchannels()); e.set_quality(2)
    open(dst,"wb").write(e.encode(w.readframes(w.getnframes()))+e.flush())

OUT="er087_output/family_z_voice_candidates_trial_01"; PG="user_test/family_z_voice_candidates_01"
os.makedirs(PG,exist_ok=True)
m=json.load(open(f"{OUT}/manifest.json",encoding="utf8")); L=m["lines"]
def sec(grp,title):
    s=[f"<h2>{title}</h2>"]
    for v,kind in m["candidates"][grp]:
        c=m["clips"]
        row=f'<div class="c"><h3>{v} <span class="k">({kind})</span></h3>'
        for ln,lab in (("calm","① 落ち着いた会話"),("emotional","② 感情のあるセリフ")):
            r=c[f"{v}/{ln}"]; fn=f"{v}_{ln}.mp3"; to_mp3(f"{OUT}/{v}/{ln}.wav",f"{PG}/{fn}")
            row+=f'<p class="s">{lab}(平均F0 {r["median_f0_hz"]}Hz / {r["duration_s"]}秒)</p><audio controls preload="none" style="width:100%" src="{fn}"></audio>'
        s.append(row+"</div>")
    return "\n".join(s)
page=f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Family Z 共通Voice候補 試聴</title>
<style>body{{font-family:Meiryo,sans-serif;max-width:760px;margin:1em auto;padding:0 1em;line-height:1.6}}.c{{border:1px solid #ccc;border-radius:8px;padding:.4em 1em;margin:.8em 0}}h3{{margin:.2em 0}}.k{{font-size:.8em;color:#555}}.s{{font-size:.85em;color:#444;margin:.3em 0}}.m{{background:#f4f4f4;padding:.6em 1em;border-radius:6px}}</style></head><body>
<h1>Family Z 共通Voice候補 試聴(男性的5+女性的5)</h1>
<p>Aoede(Narrator)とCharon(Advanced補助)は除外。選定用のTrialで、Production未採用です。</p>
<p class="s">条件(全Voice共通): TTSモデル {html.escape(m["model"])} / Family Z既定のDialogue Style 1種類 / 速度は生成そのまま(減速なし。Std側の6%減速は生成後処理のため掛けていない) / 同一セリフ。違いはVoiceだけ。平均F0は声の高さの目安(Hz)。</p>
<div class="m"><b>① 落ち着いた会話:</b> {html.escape(L["calm"])}<br><b>② 感情のあるセリフ:</b> {html.escape(L["emotional"])}</div>
{sec("male","男性的Voice 5名")}
{sec("female","女性的Voice 5名")}
</body></html>"""
open(f"{PG}/index.html","w",encoding="utf8").write(page)

# -*- coding: utf-8 -*-
"""委任_04(Advanced KP=K2反映、03版からの派生) 最終試聴ページ生成(Trial専用静的ページ)。完成版mp3+timelineスライスmp3+全スクリプト。
出力: user_test/coffee_tone_trial_01/final_v2/{index.html, standard/index.html, advanced/index.html, audio/*.mp3}
(A2)/(B1)/B1Bラベルは表示しない。file:/// や C:\\ を含めない。"""
from __future__ import annotations
import os, sys, json, html, shutil, hashlib
import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import er057_tone_trial_final_build_03_asm as A
import er057_tone_trial_final_build_03 as B
import er002_common as common
import er003_b1_p9a_audio as p9a

esc = html.escape
OUT = B.OUT
WEB = os.path.join(ROOT, "user_test", "coffee_tone_trial_01", "final_v2")
AUD = os.path.join(WEB, "audio")
TONE = B.TONE
SR = A.SR
JSON_LOG = {}


def read_json(p):
    return json.load(open(p, encoding="utf-8"))


def gen_log_index():
    d = {}
    for l in open(B.GENLOG, encoding="utf-8"):
        r = json.loads(l)
        d.setdefault(r["job"], []).append(r)
    return d


def texts():
    t = {}
    for lv, d in (("std", "a2"), ("adv", "b1b")):
        res = read_json(f"{TONE}/{d}/audit/tts_generation_results.json")
        parts = read_json(f"{TONE}/{d}/parts.json")
        sup = read_json(f"{TONE}/{d}/{'a2_support_texts.json' if lv == 'std' else 'b1_support_texts.json'}")
        kp = sorted(read_json(f"{TONE}/{d}/key_phrases/keywords_canonicalized.json")["items"], key=lambda it: it["rank"])
        t[lv] = {"res": res, "parts": parts, "sup": sup, "kp": kp}
    return t


FIXED_TEXT = {"welcome": "Welcome to English Your Way.", "preview_intro": "Here's a quick preview.", "key_phrases_intro": "Here are today's key phrases.",
              "full_story_intro": "Now, the full story.", "num_one": "One.", "num_two": "Two.", "num_three": "Three.", "num_four": "Four.", "num_five": "Five."}


def main():
    os.makedirs(AUD, exist_ok=True)
    man = read_json(os.path.join(OUT, "assembly_manifest_04_final.json"))
    gl = gen_log_index()
    T = texts()
    qa = read_json(os.path.join(OUT, "qa_04.json"))
    sections = {}
    for lv in ("std", "adv"):
        L = man["levels"][lv]
        x, sr = sf.read(os.path.join(ROOT, L["wav"]), dtype="float32")
        tl, prov = L["timeline"], L["provenance"]
        name = "Coffee_Standard_final_v2" if lv == "std" else "Coffee_Advanced_final_v2"
        shutil.copyfile(os.path.join(ROOT, L["mp3"]), os.path.join(AUD, name + ".mp3"))
        tt = T[lv]
        rows = []
        kpn = 0
        for e in tl:
            part = e["part"]
            if part.startswith("pause"):
                continue
            s, d = e["start_seconds"], e["duration_seconds"]
            sl = x[int(round(s * sr)): int(round((s + d) * sr))]
            fn = f"{lv}_{len(rows):02d}.mp3"
            A.to_mp3(sl, os.path.join(AUD, fn), br="96k")
            pl = part.lower()
            info = {"part": part, "start": s, "dur": d, "file": fn, "origin": "", "style": "", "voice": "", "text": "", "html": "", "notes": [], "extra": ""}

            def P(k):
                return prov[k]
            if part == "Intro" or part.startswith("Outro") or part.startswith("Notification"):
                info.update(origin="固定音源(TTSなし)", style="-", voice="-", text="(音楽・通知音。読み上げなし)")
            elif pl.startswith("welcome"):
                p = P("welcome" if lv == "std" else "welcome_charon")
                info.update(origin="再利用(Trial生成済み 委任_01A)", style="共通Intro A=A5", voice="Charon", text=FIXED_TEXT["welcome"])
            elif pl.startswith("topic intro"):
                p = P("topic_intro")
                if p["origin"] == "R":
                    info.update(origin="再生成1回(異音STD-24対処、既存承認Styleそのまま)", style="既存承認 TOPIC_INTRO(変更なし)", voice="Aoede", text=tt["res"]["segments"]["topic_intro"]["text"])
                    info["extra"] = "OLD_TOPIC"
                else:
                    info.update(origin="再利用(既存承認音声)", style="既存承認 TOPIC_INTRO", voice="Charon" if lv == "adv" else "Aoede", text=tt["res"]["segments"]["topic_intro"]["text"])
            elif pl.startswith("japanese title"):
                info.update(origin="再利用(既存承認音声)", style="既存承認(日本語J2)", voice="Aoede", text=tt["res"]["segments"]["japanese_title"]["text"])
            elif pl.startswith("preview intro"):
                info.update(origin="再利用(Trial生成済み 委任_01A)", style="共通Intro B=B5", voice="Charon", text=FIXED_TEXT["preview_intro"])
            elif pl.startswith("preview"):
                if lv == "std":
                    info.update(origin="再利用(Trial生成済み 委任_01B)", style="Standard日本語 Preview=P2", voice="Aoede", text=tt["sup"]["preview"])
                else:
                    info.update(origin="再利用(Trial生成済み 委任_01A)", style="Advanced Preview=E1", voice="Charon", text=tt["sup"]["preview"])
            elif pl.startswith("key phrases intro"):
                info.update(origin="再利用(既存共通shell)", style="既存承認(shell: natural, clear, conversational)", voice="Charon", text=FIXED_TEXT["key_phrases_intro"])
            elif pl.startswith("key phrase "):
                kpn += 1
                it = tt["kp"][kpn - 1]
                en = tt["res"]["key_phrases"][str(it["rank"])]
                nums = ["One.", "Two.", "Three.", "Four.", "Five."]
                if lv == "std":
                    info.update(origin="再利用(KP英語・日本語意味=Trial生成済み 委任_01B / 番号=既存shell)", style="KP英語=K2 / KP日本語意味=M2(番号は既存承認shell)", voice="Aoede(KP)/Charon(番号)",
                                text="", html=f"<table class='kp'><tr><td>{esc(it['display_phrase'])}</td><td>{esc(it['japanese_gloss'])}</td></tr></table>")
                    info["notes"].append(f"音声の流れ: {nums[kpn-1]} → 英語フレーズ → 日本語意味 → 英語フレーズ(繰返しは同一音声)。TTS用の日本語意味: {en['japanese_meaning']['text']}")
                else:
                    info.update(origin="KP英語=新規生成(Trial 委任_04、K2。Standardと同一Style) / 英語解説=再利用(既存承認音声) / 番号=既存shell", style="KP英語=K2 / 英語解説=既存承認(変更なし)", voice="Aoede(KP)/Charon(番号・英語解説)",
                                text="", html=f"<table class='kp'><tr><td>{esc(it['display_phrase'])}</td><td>{esc(it['japanese_gloss'])}</td></tr></table>")
                    info["notes"].append(f"音声の流れ: {nums[kpn-1]} → 英語フレーズ → 英語解説 → 英語フレーズ。音声で再生される英語解説: {en['explanation']['text']}")
            elif pl.startswith("full story intro"):
                info.update(origin="再利用(既存共通shell)", style="既存承認(shell)", voice="Charon", text=FIXED_TEXT["full_story_intro"])
            elif pl.startswith("comment"):
                n = int(part.split()[1])
                if lv == "std":
                    info.update(origin="再利用(Trial生成済み 委任_01B)", style="Standard日本語 Comment=P2", voice="Aoede", text=tt["sup"][f"comment_{n}"])
                else:
                    info.update(origin="再利用(既存承認音声)", style="既存承認 E2_UPBEAT(変更なし)", voice="Charon", text=tt["sup"][f"comment_{n}"])
            elif pl.startswith("full story part"):
                n = int(part.split("Part ")[1][0])
                gj = f"{lv}_part{n}"
                rec = [r for r in gl[gj] if r.get("verified")][-1]
                info.update(origin=f"再生成(F5、{rec['attempt']}回目で内容QA合格、同一Prompt再生成{rec['attempt']-1}回)", style="Full Story=F5" + ("+既存6%減速" if lv == "std" else "(減速なし)"), voice="Aoede",
                            text=tt["parts"][f"part{n}"])
                if lv == "std":
                    sd = [r for r in gl[gj] if r.get("event") == "SLOWDOWN_APPLIED"][0]
                    info["notes"].append(f"Standard 6%減速適用: 処理前 {sd['src_duration_seconds']}秒 → 処理後 {sd['dst_duration_seconds']}秒(実測+{sd['slowdown_pct_actual']}%、比 {sd['ratio']})。"
                                         f"処理=er008 apply_a2_slowdown(FFmpeg atempo=1/1.06)")
                else:
                    info["notes"].append("Advancedは減速処理なし(Full Story F5そのまま)")
                info["notes"].append(f"内容QA: Primary ASR(gpt-4o-mini-transcribe)+既存validator={rec['classification']}、length_ok={rec['length_ok']}")
            elif pl.startswith("in one line"):
                info.update(origin="再利用(既存承認音声" + ("、既に6%減速済み)" if lv == "std" else ")"), style="既存承認 IN_ONE_LINE(変更なし)", voice="Aoede", text=tt["parts"]["in_one_line"])
            else:
                info.update(origin="?", text="")
            rows.append(info)
        # 旧topic_intro(STD-24指摘のtake)比較用mp3
        if lv == "std":
            ox = A.rd(f"{TONE}/a2/narration/topic_intro.wav")
            gtopic = L["gain_report"]["topic_intro"]["gain"]
            A.to_mp3(p9a.mono_24k_to_stereo_target(ox * gtopic).astype("float32"), os.path.join(AUD, "std_topic_intro_OLD.mp3"), br="96k")
        sections[lv] = {"rows": rows, "name": name, "duration": L["duration_seconds"], "peak": L["peak"], "L": L}
    json.dump({lv: {"rows": s["rows"]} for lv, s in sections.items()}, open(os.path.join(OUT, "page_rows_04.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    def level_html(lv, rel):
        s = sections[lv]
        title = "Standard" if lv == "std" else "Advanced"
        trs = []
        for i, r in enumerate(s["rows"]):
            notes = "".join(f"<div class='note'>{esc(n)}</div>" for n in r["notes"])
            old = ""
            if r["extra"] == "OLD_TOPIC":
                old = f"<div class='note'>参考: 再利用していた旧take(STD-24で異音指摘)<br><audio controls preload='none' src='{rel}audio/std_topic_intro_OLD.mp3'></audio></div>"
            txt = r["html"] if r["html"] else "<div class='script'>" + esc(r["text"]).replace(chr(10), "<br>") + "</div>"
            trs.append(f"<tr id='{lv}{i}'><td class='id'><b>{esc(r['part'])}</b><br><span class='sec'>{r['start']:.1f}秒〜 ({r['dur']:.1f}秒)</span><br>"
                       f"<button class='jump' data-t='{r['start']}' data-lv='{lv}'>全編の位置へ</button></td>"
                       f"<td class='play'><audio controls preload='none' src='{rel}audio/{r['file']}'></audio>{old}</td>"
                       f"<td class='txt'><div class='tag'>{esc(r['origin'])}</div><div class='voice'>Style: {esc(r['style'])} / Voice: {esc(r['voice'])}</div>{notes}{txt}</td></tr>")
        return (f"<h2 id='{lv}'>{title}(通し全編 {s['duration']:.0f}秒)</h2>"
                f"<div class='combo'><b>{title} 通し全編再生</b><br><audio id='main_{lv}' controls preload='none' src='{rel}audio/{s['name']}.mp3' style='width:100%'></audio></div>"
                "<table><thead><tr><th>パート</th><th>音声(完成版からの切出し)</th><th>由来・Style・Script</th></tr></thead><tbody>" + "".join(trs) + "</tbody></table>")

    css = """<style>body{font-family:sans-serif;max-width:1180px;margin:1em auto;padding:0 1em;line-height:1.5}
table{border-collapse:collapse;width:100%;margin-bottom:1.5em}th,td{border:1px solid #ccc;padding:6px;vertical-align:top;text-align:left}
td.id{width:150px}td.play{min-width:340px}td.play audio{width:100%}.sec{color:#666;font-size:.85em}.voice{color:#555;font-size:.85em}
.script{background:#f6f6f6;padding:4px;margin:3px 0;font-size:.95em;white-space:pre-wrap}.tag{font-weight:bold;font-size:.9em}.note{background:#fff8e0;padding:3px;margin:3px 0;font-size:.85em}
.kp td{border:1px solid #ccc;padding:4px 10px;width:50%;font-size:1.05em}.combo{background:#eef6ff;padding:10px;border:1px solid #99c;margin-bottom:1em}nav a{margin-right:1em}button.jump{font-size:.8em}</style>"""
    js = """<script>
document.querySelectorAll('button.jump').forEach(b=>b.onclick=()=>{const a=document.getElementById('main_'+b.dataset.lv);a.currentTime=parseFloat(b.dataset.t);a.play();a.scrollIntoView({block:'center'})});
document.addEventListener('play',e=>{document.querySelectorAll('audio').forEach(x=>{if(x!==e.target)x.pause()})},true);
</script>"""
    kp_note = "<p>Key Phrases(両Level): 各Key Phraseブロック(番号→英語フレーズ→英語フレーズ→日本語意味/英語解説)は、下表のKey Phrase 1〜5の行で再生できます(Scriptに英語・意味を表示)。</p>"
    intro = ("<p>FAMILY-X-COFFEE-FINAL-LISTENING-TONE-TRIAL-01 委任_04更新(最終試聴版 v2)。ユーザーが選んだStyle(共通Intro A5/B5、Advanced Preview E1、Full Story F5、KP英語K2、KP日本語意味M2、Standard日本語Preview・Comment P2)を反映したCoffee最終試聴版です。"
             "これは<b>試聴用の採用候補</b>であり、全記事共通Styleの正式採用ではありません(Production未変更)。Standard Full Story(Part1〜3)にはF5生成後に既存の6%減速を適用しています。"
             "Advanced Key Phrase英語5件(lag / price tag / show up / come down / come with)にも、Standardと同一のK2 Styleで新規生成した音声を適用しました(英語解説は既存承認音声のまま)。TTS方式: 新規生成分はGemini gemini-3.8-flash-lite-tts・speech_metadata方式・Standard同期(試聴用DEV。Production既定はBatch)。固定音源(Intro・通知音・Outro)は読み上げなし。</p>")
    index = (f"<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><title>Coffee 最終試聴版 v2</title><meta name='viewport' content='width=device-width, initial-scale=1'>{css}</head><body>"
             f"<h1>Coffee 最終試聴版 v2(Standard / Advanced)</h1>{intro}<nav><a href='#std'>Standard</a><a href='#adv'>Advanced</a><a href='standard/index.html'>Standard単独ページ</a><a href='advanced/index.html'>Advanced単独ページ</a></nav>"
             f"{kp_note}{level_html('std', '')}{level_html('adv', '')}{js}</body></html>")
    open(os.path.join(WEB, "index.html"), "w", encoding="utf-8").write(index)
    for lv, d in (("std", "standard"), ("adv", "advanced")):
        os.makedirs(os.path.join(WEB, d), exist_ok=True)
        pg = (f"<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><title>Coffee 最終試聴版 v2 {d}</title><meta name='viewport' content='width=device-width, initial-scale=1'>{css}</head><body>"
              f"<h1>Coffee 最終試聴版 v2 ({'Standard' if lv=='std' else 'Advanced'})</h1>{intro}<p><a href='../index.html'>両Level一覧へ</a></p>{kp_note}{level_html(lv, '../')}{js}</body></html>")
        open(os.path.join(WEB, d, "index.html"), "w", encoding="utf-8").write(pg)
    for p in (os.path.join(WEB, "index.html"), os.path.join(WEB, "standard", "index.html"), os.path.join(WEB, "advanced", "index.html")):
        s = open(p, encoding="utf-8").read()
        assert "file:///" not in s and "C:\\" not in s and "C:/" not in s, p
        for bad in ("(A2)", "(B1)", "B1B", "b1b"):
            assert bad not in s, (p, bad)
    print("pages written; rows", {k: len(v["rows"]) for k, v in sections.items()})


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-FINAL-AUDIO-ASSEMBLY-01 委任_02: Final v3 最終試聴ページ生成(er057_tone_trial_final_page_04派生、Trial専用静的ページ)。完成版mp3+timelineスライスmp3+全スクリプト。
出力: user_test/coffee_final_v3/{index.html, standard/index.html, advanced/index.html, audio/*.mp3}
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
OUT = os.path.join(ROOT, "er057_output", "coffee_final_audio_assembly_01")
WEB = os.path.join(ROOT, "user_test", "coffee_final_v3")
V3GL = os.path.join(OUT, "generation_log_v3_01.jsonl")
IOL = json.load(open(os.path.join(OUT, "iol_final_text_01.json"), encoding="utf-8"))
AUD = os.path.join(WEB, "audio")
TONE = B.TONE
SR = A.SR
JSON_LOG = {}


def read_json(p):
    return json.load(open(p, encoding="utf-8"))


def gen_log_index():
    d = {}
    for l in open(V3GL, encoding="utf-8"):
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


def _slow():
    gl = gen_log_index()
    d = {}
    for n in (1, 3):
        e = [r for r in gl[f"std_part{n}"] if r.get("event") == "SLOWDOWN_APPLIED"][0]
        d[f"part{n}"] = {"src": e["src_duration_seconds"], "dst": e["dst_duration_seconds"], "ratio": e["ratio"]}
    e = [r for r in gl["std_in_one_line"] if r.get("event") == "SLOWDOWN_APPLIED"][0]
    d["iol"] = {"src": e["src_duration_seconds"], "dst": e["dst_duration_seconds"], "ratio": e["ratio"]}
    p2 = read_json(os.path.join(OUT, "std_part2_adopted_slowdown_01.json"))
    d["part2"] = {"src": p2["info"]["src_duration_seconds"], "dst": p2["info"]["dst_duration_seconds"], "ratio": round(p2["ratio"], 4)}
    return d


SLOW = None


def main():
    global SLOW
    SLOW = _slow()
    os.makedirs(AUD, exist_ok=True)
    man = read_json(os.path.join(OUT, "assembly_manifest_v3_01.json"))
    gl = gen_log_index()
    T = texts()
    qa = read_json(os.path.join(OUT, "qa_v3_01.json"))
    sections = {}
    for lv in ("std", "adv"):
        L = man["levels"][lv]
        x, sr = sf.read(os.path.join(ROOT, L["wav"]), dtype="float32")
        tl, prov = L["timeline"], L["provenance"]
        name = "Coffee_Standard_final_v3" if lv == "std" else "Coffee_Advanced_final_v3"
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
                    info.update(origin="再利用(Final v2で異音STD-24対処として再生成済みのtake、v3で再生成なし)", style="既存承認 TOPIC_INTRO(変更なし)", voice="Aoede", text=tt["res"]["segments"]["topic_intro"]["text"])
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
                if lv == "std":
                    gj = f"std_part{n}"
                    adopted = 1 if n == 2 else [r for r in gl[gj] if r.get("verified")][-1]["attempt"]
                    if n == 2:
                        origin = "再生成(PD8、同一Prompt3 attempt中 attempt1採用。Primary ASRは3回ともUNCERTAIN[表記差]→Production承認済みSecondary cascade[Azure]でNORMALIZED_MATCH)"
                    else:
                        origin = f"再生成(PD8、attempt{adopted}でPrimary ASR合格)"
                    info.update(origin=origin, style="Full Story=PD8+既存6%減速", voice="Aoede", text=tt["parts"][f"part{n}"])
                    sd = SLOW[f"part{n}"]
                    info["notes"].append(f"Standard 6%減速適用: 処理前 {sd['src']}秒 → 処理後 {sd['dst']}秒(比 {sd['ratio']})。処理=er008 apply_a2_slowdown(FFmpeg atempo=1/1.06)")
                    if n == 2:
                        info["notes"].append("試聴確認: Part2はSecondary ASR採択の音声です。ASR結果は原稿と実質同一(US/U.S.・cost/costs・数字表記等の表記差のみ)。聴感で読み間違いがないか確認してください。")
                else:
                    info.update(origin="再利用(PD8、pace_trial_02で生成・Primary ASR合格済みのTrial音声。v3で再生成なし、減速なし)", style="Full Story=PD8(減速なし)", voice="Aoede", text=tt["parts"][f"part{n}"])
                    if n == 1:
                        info["notes"].append("試聴確認: 13.3秒付近にlow click、「want to」が「wanna」に聞こえないか(local whisperがwannaと認識した疑い)")
                    if n == 3:
                        info["notes"].append("試聴確認: 39.85秒付近にlow click")
            elif pl.startswith("in one line"):
                info.update(origin="再生成(新原稿・2文。既存承認IN_ONE_LINE Styleのまま" + ("+A2減速指示、6%減速適用" if lv == "std" else "") + ")", style="既存承認 IN_ONE_LINE(Style不変)", voice="Aoede", text=IOL[lv])
                if lv == "std":
                    info["notes"].append(f"6%減速: {SLOW['iol']['src']}秒 → {SLOW['iol']['dst']}秒(比 {SLOW['iol']['ratio']})")
            else:
                info.update(origin="?", text="")
            rows.append(info)
        sections[lv] = {"rows": rows, "name": name, "duration": L["duration_seconds"], "peak": L["peak"], "L": L}
    json.dump({lv: {"rows": s["rows"]} for lv, s in sections.items()}, open(os.path.join(OUT, "page_rows_v3_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

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
    intro = ("<p>FAMILY-X-COFFEE-FINAL-AUDIO-ASSEMBLY-01 委任_02(Coffee最終試聴版 v3)。ユーザー決定により、Coffee記事に限りStyle選択はAPPROVED_FOR_PRODUCTION(全記事共通は未承認)。"
             "採用Style: 共通Intro A5/B5、Advanced Preview E1、Standard日本語Preview・Comment P2、KP英語K2、KP日本語意味M2、Full Story PD8(Standardは生成後に既存6%減速、Advancedは減速なし)、In One Lineは既存承認Styleのまま新原稿(2文)。"
             "これは<b>Trial隔離経路で制作した完成版</b>で、Production正式経路へはまだ配線されていません。Standard Full Story Part2はPrimary ASRが表記差でUNCERTAINとなったため、Production承認済みのSecondary ASR(Azure)cascadeで確認して採択しています。"
             "WPM実測(Full Story Part1〜3合計): Standard 全体166.0(発話部分190.5、減速前175.9)/Advanced 全体183.2(発話部分193.6)。" "既知の確認事項: Advanced Part1の13.3秒付近low click/「wanna」疑い、Part3の39.85秒付近low click。固定音源(Intro・通知音・Outro)は読み上げなし。</p>")
    index = (f"<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><title>Coffee 最終試聴版 v3</title><meta name='viewport' content='width=device-width, initial-scale=1'>{css}</head><body>"
             f"<h1>Coffee 最終試聴版 v3(Standard / Advanced)</h1>{intro}<nav><a href='#std'>Standard</a><a href='#adv'>Advanced</a><a href='standard/index.html'>Standard単独ページ</a><a href='advanced/index.html'>Advanced単独ページ</a></nav>"
             f"{kp_note}{level_html('std', '')}{level_html('adv', '')}{js}</body></html>")
    open(os.path.join(WEB, "index.html"), "w", encoding="utf-8").write(index)
    for lv, d in (("std", "standard"), ("adv", "advanced")):
        os.makedirs(os.path.join(WEB, d), exist_ok=True)
        pg = (f"<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><title>Coffee 最終試聴版 v3 {d}</title><meta name='viewport' content='width=device-width, initial-scale=1'>{css}</head><body>"
              f"<h1>Coffee 最終試聴版 v3 ({'Standard' if lv=='std' else 'Advanced'})</h1>{intro}<p><a href='../index.html'>両Level一覧へ</a></p>{kp_note}{level_html(lv, '../')}{js}</body></html>")
        open(os.path.join(WEB, d, "index.html"), "w", encoding="utf-8").write(pg)
    for p in (os.path.join(WEB, "index.html"), os.path.join(WEB, "standard", "index.html"), os.path.join(WEB, "advanced", "index.html")):
        s = open(p, encoding="utf-8").read()
        assert "file:///" not in s and "C:\\" not in s and "C:/" not in s, p
        for bad in ("(A2)", "(B1)", "B1B", "b1b"):
            assert bad not in s, (p, bad)
    print("pages written; rows", {k: len(v["rows"]) for k, v in sections.items()})


if __name__ == "__main__":
    main()

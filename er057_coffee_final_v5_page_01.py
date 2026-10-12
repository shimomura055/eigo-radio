# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-FINAL-AUDIO-ASSEMBLY-01 委任_02: Final v5 最終試聴ページ生成(v4ページ生成を踏襲)(er057_tone_trial_final_page_04派生、Trial専用静的ページ)。完成版mp3+timelineスライスmp3+全スクリプト。
出力: user_test/coffee_final_v5/{index.html, standard/index.html, advanced/index.html, audio/*.mp3}
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
DISCLOSURE_HTML = "<div class='combo' style='background:#fff0f0;border-color:#c66'><b>開示(Opus条件Cレビュー必須修正M-2、委任_03)</b><ul><li>(a) v5の組立はTrial用assembler(<code>er057_coffee_final_v5_build_01.py</code>)によるもので、runner <code>--stage assemble</code> のM3 Gate / Audio Validation Gateは通していません(代替としてオフライン実行: <code>gate_evidence/</code>、<code>AUDIO_VALIDATION_V5_01.md</code>)。</li><li>(b) Advanced Key Phrase英語解説の本文はv4から非正規手順(結果ファイルへのtext bundle事前配置)で注入しています(正規CLIは未整備、OPEN登録済み)。</li><li>(c) 原稿はv4(Tone Trial由来)を別source_dirにコピーしたもので、Production正本(run_l3_01)での通しrunではありません。</li><li>(d) In One Lineはv4の2文版です(仕様文言「中心1文+補足2文程度」との整合はOPEN-299で未決)。</li><li>(e) Comment 4の新Promptは共通定数のため、全Standard記事に適用されます(適用範囲はユーザー確認中。回答まで他Standard記事の生成は行いません)。</li><li>(f) PRODUCTION_WIREDは未判定です。適用範囲の表記: 「Coffee限定: FULL_STORY / SUPPORT_JA(Std) / KP_EXPLANATION_EN(Adv)のStyle解決のみ」。</li></ul></div>"  # 委任_03(M-2開示)。html再生成時も保持

esc = html.escape
V3D = os.path.join(ROOT, "er057_output", "coffee_final_audio_assembly_01")
OUT = os.path.join(ROOT, "er057_output", "coffee_final_v5")
V4O = os.path.join(ROOT, "er057_output", "coffee_final_v4")
RUN = os.path.join(ROOT, "er019_output", "family_x_audio_production_wiring_01", "coffee_prices__run_v5_ms_01")
WEB = os.path.join(ROOT, "user_test", "coffee_final_v5")
V3GL = os.path.join(V4O, "generation_log_v4.jsonl")
V3GL_OLD = os.path.join(V3D, "generation_log_v3_01.jsonl")
IOL = json.load(open(os.path.join(V3D, "iol_final_text_01.json"), encoding="utf-8"))
WPM = json.load(open(os.path.join(OUT, "wpm_v5_01.json"), encoding="utf-8"))
AUD = os.path.join(WEB, "audio")
TONE = B.TONE
SR = A.SR
JSON_LOG = {}


V4_COMMENT4 = json.load(open(os.path.join(RUN, "audit", "a2_support_texts_v4_original.json"), encoding="utf-8"))["comment_4"]


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
        sup = read_json(f"{RUN}/a2/a2_support_texts.json") if lv == "std" else read_json(f"{TONE}/{d}/b1_support_texts.json")
        kp = sorted(read_json(f"{TONE}/{d}/key_phrases/keywords_canonicalized.json")["items"], key=lambda it: it["rank"])
        t[lv] = {"res": res, "parts": parts, "sup": sup, "kp": kp}
    return t


FIXED_TEXT = {"welcome": "Welcome to English Your Way.", "preview_intro": "Here's a quick preview.", "key_phrases_intro": "Here are today's key phrases.",
              "full_story_intro": "Now, the full story.", "num_one": "One.", "num_two": "Two.", "num_three": "Three.", "num_four": "Four.", "num_five": "Five."}


def _slow():
    gl = gen_log_index()
    d = {}
    for n in (1, 2, 3):
        e = [r for r in gl[f"std_part{n}"] if r.get("event") == "SLOWDOWN_APPLIED"][0]
        d[f"part{n}"] = {"src": e["src_duration_seconds"], "dst": e["dst_duration_seconds"], "ratio": e["ratio"]}
    old = {}
    for l in open(V3GL_OLD, encoding="utf-8"):
        r = json.loads(l); old.setdefault(r["job"], []).append(r)
    e = [r for r in old["std_in_one_line"] if r.get("event") == "SLOWDOWN_APPLIED"][0]
    d["iol"] = {"src": e["src_duration_seconds"], "dst": e["dst_duration_seconds"], "ratio": e["ratio"]}
    return d


SLOW = None


def main():
    global SLOW
    SLOW = _slow()
    os.makedirs(AUD, exist_ok=True)
    man = read_json(os.path.join(OUT, "assembly_manifest_v5_01.json"))
    gl = gen_log_index()
    T = texts()
    qa = read_json(os.path.join(OUT, "qa_v5_01.json"))
    sections = {}
    for lv in ("std", "adv"):
        L = man["levels"][lv]
        x, sr = sf.read(os.path.join(ROOT, L["wav"]), dtype="float32")
        tl, prov = L["timeline"], L["provenance"]
        name = "Coffee_Standard_final_v5" if lv == "std" else "Coffee_Advanced_final_v5"
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
                    info.update(origin="v5で再生成(Production正式経路 coffee_final_v5、Style=R2)", style="Standard日本語 Preview=R2(承認済み)", voice="Aoede", text=tt["sup"]["preview"])
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
                    info.update(origin="KP英語=v4から再利用(K2) / 英語解説=v5で再生成(Production正式経路 coffee_final_v5、Style=P3) / 番号=既存shell", style="KP英語=K2 / 英語解説=P3(正式選択済み)", voice="Aoede(KP)/Aoede(英語解説)/Charon(番号)",
                                text="", html=f"<table class='kp'><tr><td>{esc(it['display_phrase'])}</td><td>{esc(it['japanese_gloss'])}</td></tr></table>")
                    info["notes"].append(f"音声の流れ: {nums[kpn-1]} → 英語フレーズ → 英語解説 → 英語フレーズ。音声で再生される英語解説: {en['explanation']['text']}")
            elif pl.startswith("full story intro"):
                info.update(origin="再利用(既存共通shell)", style="既存承認(shell)", voice="Charon", text=FIXED_TEXT["full_story_intro"])
            elif pl.startswith("comment"):
                n = int(part.split()[1])
                if lv == "std":
                    info.update(origin=("v5で文章・音声とも再生成(新Prompt=Trial-03最小修正、Style=R2、Production正式経路)" if n == 4 else "v5で再生成(Production正式経路 coffee_final_v5、Style=R2。文章はv4のまま)"), style="Standard日本語 Comment=R2(承認済み)", voice="Aoede", text=tt["sup"][f"comment_{n}"])
                    if n == 4:
                        info["notes"].append("v4のComment 4(参考): " + V4_COMMENT4)
                else:
                    info.update(origin="再利用(既存承認音声)", style="既存承認 E2_UPBEAT(変更なし)", voice="Charon", text=tt["sup"][f"comment_{n}"])
            elif pl.startswith("full story part"):
                n = int(part.split("Part ")[1][0])
                gj = f"{lv}_part{n}"
                ok = [r for r in gl[gj] if r.get("verified")]
                att = ok[-1]["attempt"]; vb = ok[-1].get("verified_by")
                origin = f"v4で新規生成(P8、attempt{att}で{'Primary ASR' if vb == 'primary' else 'Secondary cascade'}合格)"
                if lv == "std":
                    info.update(origin=origin, style="Full Story=P8(Aoede Style Trial-03、Coffee Full Story専用)+既存6%減速", voice="Aoede", text=tt["parts"][f"part{n}"])
                    sd = SLOW[f"part{n}"]
                    info["notes"].append(f"Standard 6%減速適用: 処理前 {sd['src']}秒 → 処理後 {sd['dst']}秒(比 {sd['ratio']})。処理=er008 apply_a2_slowdown(FFmpeg atempo=1/1.06)")
                else:
                    info.update(origin=origin, style="Full Story=P8(Aoede Style Trial-03、Coffee Full Story専用、減速なし)", voice="Aoede", text=tt["parts"][f"part{n}"])
                info["notes"].append("v3既知の低レベル異音箇所の新旧比較は報告書参照。聴感で違和感がないか確認してください。")
            elif pl.startswith("in one line"):
                info.update(origin="v3承認音声を再利用(新原稿・2文。既存承認IN_ONE_LINE Styleのまま" + ("+A2減速指示、6%減速適用" if lv == "std" else "") + ")", style="既存承認 IN_ONE_LINE(Style不変)", voice="Aoede", text=IOL[lv])
                if lv == "std":
                    info["notes"].append(f"6%減速: {SLOW['iol']['src']}秒 → {SLOW['iol']['dst']}秒(比 {SLOW['iol']['ratio']})")
            else:
                info.update(origin="?", text="")
            rows.append(info)
        sections[lv] = {"rows": rows, "name": name, "duration": L["duration_seconds"], "peak": L["peak"], "L": L}
    json.dump({lv: {"rows": s["rows"]} for lv, s in sections.items()}, open(os.path.join(OUT, "page_rows_v5_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

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
    w = WPM
    D5 = {lv: read_json(os.path.join(OUT, f"provenance_diff_v5_{lv}.json")) for lv in ("std", "adv")}
    ROLE_JA = {"preview": "Preview", "comment_1": "Comment 1", "comment_2": "Comment 2", "comment_3": "Comment 3", "comment_4": "Comment 4"}
    chg_std = "、".join(ROLE_JA.get(k, k) for k in D5["std"]["changed_roles"])
    chg_adv = "、".join(k.replace("_explanation_en", " 英語解説") .replace("kp", "Key Phrase ") for k in D5["adv"]["changed_roles"])
    c4_new = T["std"]["sup"]["comment_4"]
    intro = (DISCLOSURE_HTML + "<p>FAMILY-X-COFFEE-FINAL-V5-PRODUCTION-WIRING-01 委任_01(Coffee最終試聴版 v5)。ユーザー正式決定(2026-10-12)を反映した版です。"
             "<b>v4からの変更</b>: (1) Standard Comment 4 = Trial-03の最小修正Prompt(「In One Lineは番組の最後に流れる英語の要点整理」「橋渡しは『続いて』より『最後に』」の2文を追加)で文章を再生成。"
             "(2) Standard Preview/Comment 1〜4 = 承認済みR2 Styleで音声を再生成(文章はv4のまま、Comment 4のみ新文章)。(3) Advanced Key Phrase英語解説(5件)= 正式選択済みP3 Styleで音声を再生成。"
             f"変更あり: Standard [{chg_std}]、Advanced [{chg_adv}]。それ以外(Full Story=P8、Standard 6%減速、In One Line、固定音源、Key Phrase英語・日本語意味など)はv4の音声をそのまま再利用しています(sha256で同一を確認、PRODUCTION_DIFF_V5.md)。"
             f"<br>Standard Comment 4: v4=「{esc(V4_COMMENT4)}」→ v5=「{esc(c4_new)}」。"
             "<br>再生成した音声はProduction正式経路(runner <code>--style-profile coffee_final_v5</code>)で生成し、組立は試聴版用のTrial assemblerです(Production正式経路への配線完了=PRODUCTION_WIREDの判定は別)。原稿はv4(Tone Trial由来)のままで、Production正本原稿とは別です(ユーザー判断事項として別途記録)。"
             f"Full Story WPM(v4と同一音声): Standard 全体{w['std_v4']['total_wpm']}/発話部分{w['std_v4']['total_speech_wpm500']}、Advanced 全体{w['adv_v4']['total_wpm']}/発話部分{w['adv_v4']['total_speech_wpm500']}。"
             "音声品質の合否はユーザー試聴で判断します(R2/P3の採否は決定済みで再確認は不要)。固定音源(Intro・通知音・Outro)は読み上げなし。</p>")
    index = (f"<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><title>Coffee 最終試聴版 v5</title><meta name='viewport' content='width=device-width, initial-scale=1'>{css}</head><body>"
             f"<h1>Coffee 最終試聴版 v5(Standard / Advanced)</h1>{intro}<nav><a href='#std'>Standard</a><a href='#adv'>Advanced</a><a href='standard/index.html'>Standard単独ページ</a><a href='advanced/index.html'>Advanced単独ページ</a></nav>"
             f"{kp_note}{level_html('std', '')}{level_html('adv', '')}{js}</body></html>")
    open(os.path.join(WEB, "index.html"), "w", encoding="utf-8").write(index)
    for lv, d in (("std", "standard"), ("adv", "advanced")):
        os.makedirs(os.path.join(WEB, d), exist_ok=True)
        pg = (f"<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><title>Coffee 最終試聴版 v5 {d}</title><meta name='viewport' content='width=device-width, initial-scale=1'>{css}</head><body>"
              f"<h1>Coffee 最終試聴版 v5 ({'Standard' if lv=='std' else 'Advanced'})</h1>{intro}<p><a href='../index.html'>両Level一覧へ</a></p>{kp_note}{level_html(lv, '../')}{js}</body></html>")
        open(os.path.join(WEB, d, "index.html"), "w", encoding="utf-8").write(pg)
    for p in (os.path.join(WEB, "index.html"), os.path.join(WEB, "standard", "index.html"), os.path.join(WEB, "advanced", "index.html")):
        s = open(p, encoding="utf-8").read()
        assert "file:///" not in s and "C:\\" not in s and "C:/" not in s, p
        for bad in ("(A2)", "(B1)", "B1B", "b1b"):
            assert bad not in s, (p, bad)
    print("pages written; rows", {k: len(v["rows"]) for k, v in sections.items()})


if __name__ == "__main__":
    main()

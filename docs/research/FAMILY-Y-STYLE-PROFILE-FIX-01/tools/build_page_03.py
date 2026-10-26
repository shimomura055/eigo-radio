# -*- coding: utf-8 -*-
"""FAMILY-Y-STYLE-PROFILE-FIX-01 委任_02: 公開 `_03` ページ組立(API 0)。

run_style_fix_01/pages(runnerのpages stage出力)を user_test/family_y_production_redelivery_fee_03/ へ複製し、先頭に『比較節』を挿入する:
  - Voice 1〜3(Standard/Advanced 6 segment)を旧`_02`(default Style)と新版(承認PD06)で並べて個別再生(S9未評価・ユーザー判断項目。Opus M-3)
  - 話速WPM前後表(Opus R-1)
  - 部位別Style前後表(全segment: 旧prefix→新prefix・再生成/再利用)
旧`_01`/`_02`は一切変更しない(読み取りのみ)。旧音声は `_03/compare_old/` へ複製して自己完結にする。
使い方: .venv\\Scripts\\python.exe docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/tools/build_page_03.py [--dest DIR] [--check-only]
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
RUN = "er121_output/family_y_production_01/redelivery_fee/run_style_fix_01"
OLD = "user_test/family_y_production_redelivery_fee_02"
DEST = "user_test/family_y_production_redelivery_fee_03"
EVID = "docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/regen_evidence_01.json"
WPM = "docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/wpm_01.json"
ROW = re.compile(r"<tr><td><b>([^<]*)</b><br><span class='sec'>([^<]*)</span>.*?src='(audio/[a-z0-9_]+\.mp3)'", re.S)
STYLE_LABEL = {"3a680861": "PD06(承認:本文)", "060c08fd": "S3(承認:日本語補助)", "8862317f": "E1(承認:Adv Preview)", "9d905cfe": "K2(承認:KP英語)",
               "b12c8721": "P8-KP(承認:KP日本語意味)", "05180006": "P7(承認:KP英語解説)",
               "07d72dd6": "旧default(Adv本文)", "9293e0c3": "旧default(Std本文・減速指示連結)", "ae68e3e6": "旧default(日本語)", "2b0c7505": "旧default(KP英語)",
               "f44ef4e2": "旧default(KP解説)", "57c3fda6": "基底(Adv英語・変更なし)", "d16e099c": "基底(Topic intro・変更なし)"}


def _rows(page: str) -> list:
    return [(m.group(1), m.group(3)) for m in ROW.finditer(page)]


def _voice_map(page: str) -> dict:
    """{('std'|'adv', n): 'audio/xxx.mp3'} for 'Full Story: Voice n'(Introductionは除く)。"""
    out = {}
    for label, src in _rows(page):
        m = re.fullmatch(r"Full Story: Voice ([123])", label)
        if m:
            out[("std" if "/std_" in src else "adv", int(m.group(1)))] = src
    return out


def _style_cell(rec):
    if not rec or not rec.get("style"):
        return "-"
    s = rec["style"]["sha8"]
    return f"{STYLE_LABEL.get(s, s)} <span class='sec'>[{s}/{rec['style']['len']}字]</span>"


def build(dest: str, check_only: bool = False, pages: str | None = None) -> dict:
    os.chdir(ROOT)
    new_pages = pages or f"{RUN}/pages"
    page = open(f"{new_pages}/index.html", encoding="utf-8").read()
    old_page = open(f"{OLD}/index.html", encoding="utf-8").read()
    nv, ov = _voice_map(page), _voice_map(old_page)
    need = {(lv, n) for lv in ("std", "adv") for n in (1, 2, 3)}
    if set(nv) != need or set(ov) != need:
        raise SystemExit(f"Voice行の抽出に失敗: new={sorted(nv)} old={sorted(ov)}")
    wpm, evid = json.load(open(WPM, encoding="utf-8")), json.load(open(EVID, encoding="utf-8"))
    if check_only:
        return {"voice_rows": len(nv)}
    if os.path.exists(dest):
        raise SystemExit(f"{dest} が既に存在します(上書きしない)")
    shutil.copytree(new_pages, dest, ignore=shutil.ignore_patterns("listening"))
    os.makedirs(f"{dest}/compare_old", exist_ok=True)
    rows_html = []
    for lv, lvname, key in (("std", "Standard", "a2"), ("adv", "Advanced", "b1b")):
        for n in (1, 2, 3):
            old_rel = f"compare_old/{lv}_voice{n}_old_default.mp3"
            shutil.copyfile(f"{OLD}/{ov[(lv, n)]}", f"{dest}/{old_rel}")
            w = wpm[f"{key}:y_voice_{n}"]
            rows_html.append(
                f"<tr><td><b>{lvname} / Voice {n}</b></td>"
                f"<td class='play'><audio controls preload='none' src='{old_rel}'></audio><br><span class='sec'>旧 `_02`(default Style)</span></td>"
                f"<td class='play'><audio controls preload='none' src='{nv[(lv, n)]}'></audio><br><span class='sec'>新 `_03`(承認Style PD06)</span></td>"
                f"<td>{w['old_sec']}秒 → {w['new_sec']}秒<br><span class='sec'>{w['words']}語 / WPM {w['old_wpm']} → {w['new_wpm']}</span></td></tr>")
    style_rows = []
    for lv, lvname in (("a2", "Standard"), ("b1b", "Advanced")):
        for r in evid[lv]:
            if r["segment"].startswith("kp") and "phrase_repeat" in r["segment"]:
                continue
            n, o = r["new"], r["old"]
            changed = bool(n and o and n.get("style") and o.get("style") and n["style"]["sha8"] != o["style"]["sha8"])
            style_rows.append(f"<tr><td>{lvname}</td><td>{html.escape(r['segment'])}</td><td>{_style_cell(o)}</td><td>{_style_cell(n)}</td>"
                              f"<td>{'Style変更→再生成' if changed else 'Style不変(新runでも再生成)'}</td><td>{(n or {}).get('voice') or '-'}</td></tr>")
    section = (
        "<h2 id='compare'>旧版(`_02`)との比較: Voice 1〜3の聞こえ方(ユーザー判断項目)</h2>"
        "<div class='note'><b>S9未評価・ユーザー判断項目</b><br>"
        "承認済みの本文Style(PD06: 「smile in your voice」「reassuring」「like a favorite morning radio host」)を、"
        "ナレーターだけでなくVoice 1〜3の人物本文にも適用しています(承認記録A19/T10に基づく)。ただしこのStyleは司会者向けの文言で、"
        "批判的・不満を述べる人物の語りを平板にする可能性があります。承認時の条件「S9(人物の聞こえ方)を試聴で確認する」は未実施です。"
        "下の6組を聴き比べ、(a)新版のまま(PD06をVoice本文にも適用) (b)Voice本文だけ旧default Styleへ戻す(再生成の見込み: 約8円・約30分) のどちらかをご判断ください。</div>"
        "<table><thead><tr><th>音声</th><th>旧(default Style)</th><th>新(承認PD06)</th><th>長さ・話速</th></tr></thead><tbody>"
        + "".join(rows_html) + "</tbody></table>"
        "<details class='aux'><summary>部位別Style 前後表(全segment)</summary><table><thead><tr><th>level</th><th>segment</th><th>旧</th><th>新</th><th>区分</th><th>Voice</th></tr></thead><tbody>"
        + "".join(style_rows) + "</tbody></table></details>")
    out = page.replace("<h2 id='standard'>", section + "<h2 id='standard'>", 1)
    out = out.replace("<nav><a href='#standard'>", "<nav><a href='#compare'>旧版との比較</a><a href='#standard'>", 1)
    if out == page or "id='compare'" not in out:
        raise SystemExit("比較節の挿入に失敗")
    with open(f"{dest}/index.html", "w", encoding="utf-8") as f:
        f.write(out)
    return {"dest": dest, "voice_rows": len(rows_html), "style_rows": len(style_rows)}




# ============================================================
# 委任_03: 先行公開(組立前)ページ。runnerのpages stageはStd HR待ちのGate BLOCKで走らないため、
#   Advanced = 承認済みgain(apply_y_gain, 組立なし)を掛けたsegment個別再生、Standard = 素のsegment wavの個別再生+HR試聴節。
#   run dirは読み取りのみ(Gate検査が副産物を書くためrun全体をscratchへ複製して実行する)。API 0。
# ============================================================
HR_SEGS = (("y_voice_1", "en", "Voice 1(人物本文)"), ("preview", "ja", "Preview(日本語要約)"))


def _mp3(arr, sr, out, br="96k"):
    import subprocess
    import imageio_ffmpeg
    import soundfile as sf
    tmp = out + ".tmp.wav"
    sf.write(tmp, arr, sr)
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-i", tmp, "-codec:a", "libmp3lame", "-b:a", br, out], check=True)
    os.remove(tmp)


def _diff_pairs(ref: str, hyp: str, ja: bool) -> list:
    """台本(ref)とASR転写(hyp)の相違箇所を(台本側, ASR側)で返す(表示専用・判定に使わない)。"""
    import difflib
    if ja:
        a, b = list(re.sub(r"[\s、。,.]", "", ref)), list(re.sub(r"[\s、。,.]", "", hyp))
    else:
        nz = lambda t: t.replace("’", "'").lower()
        a, b = re.findall(r"[\w'-]+", nz(ref)), re.findall(r"[\w'-]+", nz(hyp))
    out = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        sep = "" if ja else " "
        out.append((sep.join(a[i1:i2]) or "(なし)", sep.join(b[j1:j2]) or "(なし)"))
    return out


def _std_script(sid: str, parts: dict, support: dict, res: dict) -> str:
    if sid in parts["segments"]:
        return parts["segments"][sid]
    if sid in support:
        return support[sid]
    e = (res.get("segments") or {}).get(sid) or {}
    return e.get("canonical_text") or e.get("text") or ""


def _ok_script(sid, parts, support, res):
    km = re.fullmatch(r"kp(\d)_(english|japanese_meaning)", sid)
    if km:
        k = (res.get("key_phrases") or {}).get(km.group(1)) or {}
        e = k.get(km.group(2)) or {}
        t = e.get("canonical_text") or e.get("text") or ""
    else:
        t = _std_script(sid, parts, support, res)
    return f"<div class='script'>{html.escape(t)}</div>" if t else "<span class='sec'>(KP音声)</span>"


def build_segments_page(dest: str) -> dict:
    import tempfile
    import soundfile as sf
    os.chdir(ROOT)
    sys.path.insert(0, ROOT)
    if os.path.exists(dest):
        raise SystemExit(f"{dest} が既に存在します(上書きしない)")
    old_page = open(f"{OLD}/index.html", encoding="utf-8").read()
    ov = _voice_map(old_page)
    wpm, evid = json.load(open(WPM, encoding="utf-8")), json.load(open(EVID, encoding="utf-8"))
    import er121_family_y_audio_01 as ya
    import er121_family_y_structure_01 as ys
    import er003_v1_n3_01_assemble as asm
    tmp = tempfile.mkdtemp(prefix="ysp3_")
    scratch = os.path.join(tmp, "run")
    shutil.copytree(RUN, scratch)
    for d in ("audio", "compare_old", "std_hr", "std_ok"):
        os.makedirs(f"{dest}/{d}", exist_ok=True)
    try:
        # ---- Advanced: gain適用済みsegment(組立なし) ----
        base = f"{scratch}/b1b"
        txt = open(f"{scratch}/translate/b1b.md", encoding="utf-8").read()
        src = ya.load_y_sources(scratch, "b1b", article_text=ys.canonical_body(txt))
        parts_g = ya.apply_y_gain(src, "b1b")
        sr = int(ya.xr.SR)
        bp = json.load(open(f"{base}/parts.json", encoding="utf-8"))
        bres = json.load(open(f"{base}/audit/tts_generation_results.json", encoding="utf-8"))
        bsup = json.load(open(f"{base}/support_texts.json", encoding="utf-8"))
        kp_items = sorted(json.load(open(f"{base}/key_phrases/keywords_canonicalized.json", encoding="utf-8"))["items"], key=lambda it: it["rank"])
        blocks = asm.build_b1_key_phrase_blocks(parts_g)
        seg = parts_g["b1_segments"]
        adv_rows = []

        def add_adv(label, arr, script_html):
            fn = f"audio/adv_{len(adv_rows):02d}.mp3"
            _mp3(arr, sr, f"{dest}/{fn}")
            adv_rows.append((label, fn, round(arr.shape[0] / sr, 2), script_html))

        def sc(t):
            return f"<div class='script'>{html.escape(t)}</div>" if t else "<span class='sec'>(定型音声)</span>"
        add_adv("Welcome", parts_g["welcome"], sc(""))
        add_adv("Topic intro", parts_g["topic_intro"], sc((bres["segments"]["topic_intro"] or {}).get("canonical_text")))
        add_adv("Preview intro", parts_g["preview_intro"], sc(""))
        add_adv("Preview", seg["preview"], sc(bsup["preview"]))
        add_adv("Key phrases intro", parts_g["key_phrases_intro"], sc(""))
        for i, b in enumerate(blocks, start=1):
            it = kp_items[i - 1]
            ex = (bres["key_phrases"][str(it["rank"])].get("explanation") or {}).get("explanation_text") or ""
            add_adv(f"Key Phrase {i}", b, f"<table class='kp'><tr><th>Key Phrase</th><th>英語での解説</th></tr><tr><td>{html.escape(it['used_form'])}</td><td>{html.escape(ex)}</td></tr></table>")
        add_adv("Full story intro", parts_g["full_story_intro"], sc(""))
        add_adv("Comment 1", seg["comment_1"], sc(bsup["comment_1"]))
        for sid in ("y_lead", "y_intro_1", "y_voice_1", "y_intro_2", "y_voice_2", "y_intro_3", "y_voice_3"):
            add_adv(ys.PAGE_LABEL[sid], seg[sid], sc(bp["segments"][sid]))
        add_adv("Comment 3", seg["comment_3"], sc(bsup["comment_3"]))
        add_adv(ys.PAGE_LABEL["y_closing"], seg["y_closing"], sc(bp["segments"]["y_closing"]))
        adv_total = round(sum(r[2] for r in adv_rows), 1)
        # ---- 比較節: 旧 _02(default) vs 新(PD06・同じgain条件) ----
        cmp_rows = []
        for n in (1, 2, 3):
            old_rel = f"compare_old/adv_voice{n}_old_default.mp3"
            shutil.copyfile(f"{OLD}/{ov[('adv', n)]}", f"{dest}/{old_rel}")
            w = wpm[f"b1b:y_voice_{n}"]
            new_fn = [r[1] for r in adv_rows if r[0] == ys.PAGE_LABEL[f"y_voice_{n}"]][0]
            cmp_rows.append(
                f"<tr><td><b>Advanced / Voice {n}</b><br><span class='sec'>{['Puck', 'Zephyr', 'Schedar'][n - 1]}</span></td>"
                f"<td class='play'><audio controls preload='none' src='{old_rel}'></audio><br><span class='sec'>旧 `_02`(default Style)</span></td>"
                f"<td class='play'><audio controls preload='none' src='{new_fn}'></audio><br><span class='sec'>新 `_03`(承認Style PD06)</span></td>"
                f"<td>{w['old_sec']}秒 → {w['new_sec']}秒<br><span class='sec'>{w['words']}語 / WPM {w['old_wpm']} → {w['new_wpm']}</span></td></tr>")
        wpm_rows = "".join(f"<tr><td>{'Advanced' if k.startswith('b1b') else 'Standard'}</td><td>{html.escape(k.split(':')[1])}</td><td>{v['words']}</td>"
                           f"<td>{v['old_sec']}</td><td>{v['new_sec']}</td><td>{v['old_wpm']}</td><td>{v['new_wpm']}</td></tr>" for k, v in wpm.items())
        style_rows = []
        for lv, lvname in (("a2", "Standard"), ("b1b", "Advanced")):
            for r in evid[lv]:
                if r["segment"].startswith("kp") and "phrase_repeat" in r["segment"]:
                    continue
                n, o = r["new"], r["old"]
                changed = bool(n and o and n.get("style") and o.get("style") and n["style"]["sha8"] != o["style"]["sha8"])
                style_rows.append(f"<tr><td>{lvname}</td><td>{html.escape(r['segment'])}</td><td>{_style_cell(o)}</td><td>{_style_cell(n)}</td>"
                                  f"<td>{'Style変更→再生成' if changed else 'Style不変(新runでも再生成)'}</td><td>{(n or {}).get('voice') or '-'}</td></tr>")
        # ---- Standard: 承認待ち2 segment の候補take ----
        a2 = f"{scratch}/a2"
        ares = json.load(open(f"{a2}/audit/tts_generation_results.json", encoding="utf-8"))
        apar = json.load(open(f"{a2}/parts.json", encoding="utf-8"))
        asup = json.load(open(f"{a2}/support_texts.json", encoding="utf-8"))
        hr_html, hr_data = [], {}
        for sid, lang, lab in HR_SEGS:
            e = ares["segments"][sid]
            script = e["canonical_text"] if lang == "ja" else apar["segments"][sid]
            takes = []
            for a in e["attempts_log"]:
                j = a.get("asr_judgement") or {}
                w = a["attempt_audio_path"].replace("\\", "/")
                takes.append(dict(n=a["attempt"], kind="承認Style(標準経路)", wav=os.path.join(scratch, w.split("run_style_fix_01/", 1)[1]),
                                  primary=a.get("asr_text") or "", azure=((j.get("secondary") or {}).get("text") or ""), state=j.get("state"), reason=j.get("reason_code")))
            f3 = [x for x in os.listdir(f"{a2}/narration/attempts") if x.startswith(f"{sid}_attempt3_minimalfallback") and x.endswith(".json")]
            if f3:
                j3 = json.load(open(f"{a2}/narration/attempts/{f3[0]}", encoding="utf-8"))
                takes.append(dict(n=3, kind="fallback短文Style(minimal_fallback。承認Styleと異なる)", wav=f"{a2}/narration/attempts/{f3[0][:-5]}.wav",
                                  primary=j3.get("asr_text") or "", azure="", state="3回ともNG_BOTH(locked_entry最終判定)。fallbackはStd規則でHR承認必須", reason=j3.get("audio_classification")))
            rows = []
            for t in takes:
                arr, s0 = sf.read(t["wav"], dtype="float32")
                fn = f"std_hr/std_{sid}_take{t['n']}.mp3"
                _mp3(arr, s0, f"{dest}/{fn}")
                d = round(arr.shape[0] / s0, 2)
                pairs = _diff_pairs(script, t["primary"], lang == "ja")
                pairs_az = _diff_pairs(script, t["azure"], lang == "ja") if t["azure"] else []

                def cell(ps):
                    return "<br>".join(f"台本「{html.escape(x)}」 ⇔ ASR「{html.escape(y)}」" for x, y in ps) or "(語句差なし)"
                az = (f"<div class='sec' style='margin-top:4px'>Azure転写(第2ASR)</div><div class='script'>{html.escape(t['azure'])}</div>{cell(pairs_az)}") if t["azure"] else ""
                rows.append(f"<tr><td><b>take {t['n']}</b><br><span class='sec'>{html.escape(t['kind'])}<br>{d}秒</span></td>"
                            f"<td class='play'><audio controls preload='none' src='{fn}'></audio></td>"
                            f"<td><div class='sec'>OpenAI ASR転写</div><div class='script'>{html.escape(t['primary'])}</div><div class='sec'>台本との語句差(句読点・空白は除く):</div>{cell(pairs)}"
                            f"{az}<div class='sec'>判定: {html.escape(str(t['state']))} / {html.escape(str(t['reason']))}</div></td></tr>")
                hr_data.setdefault(sid, []).append({"take": t["n"], "kind": t["kind"], "dur": d, "mp3": fn, "state": t["state"], "reason": t["reason"],
                                                    "diff_openai": pairs, "diff_azure": pairs_az, "openai_asr": t["primary"], "azure_asr": t["azure"]})
            hr_html.append(f"<h3>{html.escape(lab)}({sid})</h3><div class='script'><b>台本</b>: {html.escape(script)}</div>"
                           f"<table><thead><tr><th>候補</th><th>音声</th><th>ASR転写・台本との差</th></tr></thead><tbody>{''.join(rows)}</tbody></table>")
        # ---- Standard: 通過segment(素のwav・音量調整前) ----
        sva = json.load(open(f"{scratch}/audit/style_actual_vs_approved.json", encoding="utf-8"))["levels"]["a2"]["rows"]
        ok_rows = []
        for r in sva:
            sid = r["segment"]
            if sid in ("y_voice_1", "preview") or not r.get("match"):
                continue
            km = re.fullmatch(r"kp(\d)_(english|japanese_meaning)", sid)
            wp = f"{a2}/narration/{(f'kp{km.group(1)}_en' if km.group(2) == 'english' else f'meaning_{km.group(1)}') if km else sid}.wav"
            if not os.path.exists(wp):
                continue
            arr, s0 = sf.read(wp, dtype="float32")
            fn = f"std_ok/{sid}.mp3"
            _mp3(arr, s0, f"{dest}/{fn}")
            ok_rows.append(f"<tr><td><b>{html.escape(ys.PAGE_LABEL.get(sid, sid))}</b><br><span class='sec'>{html.escape(sid)} / {r.get('voice')} / {round(arr.shape[0] / s0, 1)}秒"
                           f"{' / Std6%減速済み' if r.get('slowdown_applied') else ''}</span></td><td class='play'><audio controls preload='none' src='{fn}'></audio></td>"
                           f"<td>{_ok_script(sid, apar, asup, ares)}</td></tr>")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    css = re.search(r"<style>(.*?)</style>", old_page, re.S).group(1)
    title = re.search(r"<title>(.*?)</title>", old_page, re.S).group(1)
    adv_html = "".join(f"<tr><td><b>{html.escape(l)}</b><br><span class='sec'>{d}秒</span></td><td class='play'><audio controls preload='none' src='{fn}'></audio></td><td>{s}</td></tr>" for l, fn, d, s in adv_rows)
    page = (
        f"<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><meta name=\"robots\" content=\"noindex,nofollow\"><title>{title}</title>"
        f"<meta name='viewport' content='width=device-width, initial-scale=1'><style>{css}</style></head><body><h1>{title}</h1>"
        "<nav><a href='#status'>状況</a><a href='#compare'>Voice 1〜3 旧新比較</a><a href='#advanced'>Advanced修正版</a><a href='#std_hr'>Standard 承認待ち2件</a><a href='#std_ok'>Standard 通過分</a></nav>"
        + ys.notice_html() +
        "<h2 id='status'>この `_03` ページの状況(先行公開)</h2><div class='note'><b>Advanced修正版は公開、Standardは承認待ち2 segmentがあるため通し版は未作成です。</b><br>"
        "・Advanced: 承認済みStyleで再生成した全segment(Gate 15/15 PASS)を個別再生できます。<b>通し音声(全編)は未組立</b>です(組立は全レベルのGate通過が条件で、Standardの承認待ち2件が残るため。承認後に追加します)。"
        "音量は通し版と同じ調整(gain)を掛けていますが、segment間の無音(pause)は含みません。Intro/Notification/Outro/番号は定型音声のため省略しています。<br>"
        "・Standard: <b>Voice 1(y_voice_1)とPreview(preview)の2件は自動検査(ASR)が通らず、あなたの試聴・承認待ち</b>です(原因は下記)。通過した16 segment は個別再生のみ(音量調整前の素の音声)。<br>"
        "・Advanced Comment 2は仕様どおり存在しません。</div>"
        "<h2 id='compare'>旧版(`_02`)との比較: Advanced Voice 1〜3の聞こえ方(ユーザー判断項目)</h2>"
        "<div class='note'><b>S9未評価・ユーザー判断項目</b><br>承認済みの本文Style(PD06: 「smile in your voice」「reassuring」「like a favorite morning radio host」)を、"
        "ナレーターだけでなくVoice 1〜3の人物本文にも適用しています。ただしこのStyleは司会者向けの文言で、批判的・不満を述べる人物の語りを平板にする可能性があります。"
        "承認時の条件「S9(人物の聞こえ方)を試聴で確認する」は未実施です。(a)新版のまま (b)Voice本文だけ旧default Styleへ戻す(再生成の見込み: 約8円・約30分) のどちらかをご判断ください。"
        "個性を損なっていないかは、あなたの試聴でのみ判断できます。</div>"
        "<table><thead><tr><th>音声</th><th>旧(default Style)</th><th>新(承認PD06)</th><th>長さ・話速</th></tr></thead><tbody>" + "".join(cmp_rows) + "</tbody></table>"
        "<details class='aux'><summary>話速(WPM)前後表(全segment)</summary><table><thead><tr><th>level</th><th>segment</th><th>語数</th><th>旧 秒</th><th>新 秒</th><th>旧 WPM</th><th>新 WPM</th></tr></thead><tbody>" + wpm_rows + "</tbody></table></details>"
        "<details class='aux'><summary>部位別Style 前後表(全segment)</summary><table><thead><tr><th>level</th><th>segment</th><th>旧</th><th>新</th><th>区分</th><th>Voice</th></tr></thead><tbody>" + "".join(style_rows) + "</tbody></table></details>"
        f"<h2 id='advanced'>Advanced 修正版(segment個別再生・計 約{adv_total}秒)</h2><table><thead><tr><th>パート</th><th>音声</th><th>Script / Key Phrase</th></tr></thead><tbody>{adv_html}</tbody></table>"
        "<h2 id='std_hr'>Standard: あなたの試聴・承認待ちの2 segment</h2><div class='note'>どちらも自動検査(ASR)が台本と一致せずNGになったものです。Previewは「思い通り」と「思いどおり」(読みは同じ)の表記ゆれのみです。"
        "Voice 1はtake 1/2で「re-deliveries」のハイフン表記に加え、<b>台本「who was not home」が両ASRで「who is not home」と聞こえている</b>(1語の言い違いの可能性。take 3は語句差なし)ため、ここは耳で確認してください。Styleの不具合ではありません。各候補を聴き、<b>どのtakeを採用するか</b>をご指定ください(操作方法は `HR_REQUEST_STD_01.md`)。"
        "take 1/2は承認Style、take 3はfallback(短文Style)で承認Styleと異なるため、特段の理由がなければtake 1または2を推奨します。</div>"
        + "".join(hr_html) +
        f"<h2 id='std_ok'>Standard: 検査を通過した {len(ok_rows)} segment(個別再生・音量調整前)</h2><table><thead><tr><th>パート</th><th>音声</th><th>Script</th></tr></thead><tbody>{''.join(ok_rows)}</tbody></table>"
        "</body></html>")
    with open(f"{dest}/index.html", "w", encoding="utf-8") as f:
        f.write(page)
    summary = {"dest": dest, "adv_rows": len(adv_rows), "adv_total_sec": adv_total, "cmp_rows": len(cmp_rows), "std_ok_rows": len(ok_rows), "hr": hr_data}
    with open(f"{dest}/build_summary_03.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    return {k: v for k, v in summary.items() if k != "hr"}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest", default=DEST)
    ap.add_argument("--check-only", action="store_true")
    ap.add_argument("--pages", default=None, help="入力pages dir(既定=run_style_fix_01/pages。テスト用)")
    ap.add_argument("--segments-only", action="store_true", help="委任_03: 組立前の先行公開ページ(Adv segment個別再生+Std HR試聴節)")
    a = ap.parse_args()
    print(json.dumps(build_segments_page(a.dest) if a.segments_only else build(a.dest, a.check_only, a.pages), ensure_ascii=False))

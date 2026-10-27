# -*- coding: utf-8 -*-
"""AI-ISLAND-FORM-PRODUCTION-01 委任_03: AI島(ai_island_temple)最終試聴ページ生成(API呼出なし)。
入力=Production runner(X)のrun dir(assemble/Gate通過済み)。共通builder `er_user_listening_page_common_01.render_standard_page` と
学習ブロック `er120_part2_wiring_01.public_study_html`(Part 1[Advのみ]+Part 2)を使う。出力=user_test/family_x_ai_island_form_01/{index.html,audio/*.mp3}。
使い方: .venv\\Scripts\\python.exe tools/build_aif3_listening_page_01.py [--run-name run_form_prod_01]"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import imageio_ffmpeg  # noqa: E402
import soundfile as sf  # noqa: E402

import er019_family_x_audio_production_runner_01 as R  # noqa: E402
import er120_part2_wiring_01 as p2w  # noqa: E402
import er_user_listening_page_common_01 as uc  # noqa: E402

esc = html.escape
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
SLUG = "ai_island_temple"


def rj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def to_mp3(x, sr, out, br="96k"):
    tmp = out + ".tmp.wav"
    sf.write(tmp, x, sr)
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", tmp, "-codec:a", "libmp3lame", "-b:a", br, out], check=True)
    os.remove(tmp)


def level_data(run, source_dir, web_aud, level, key, label, ja_title):
    base = f"{run}/{level}"
    summ = rj(f"{base}/run_summary_assemble.json")
    assert summ.get("status") == "OK", f"{level} assemble status={summ.get('status')}"
    x, sr = sf.read(summ["out_path"], dtype="float32")
    full = f"ai_island_{label}.mp3"
    to_mp3(x, sr, os.path.join(web_aud, full), br="128k")
    timeline = rj(f"{base}/audit/timeline.json")
    parts = rj(f"{base}/parts.json")
    support = rj(f"{base}/{'b1_support_texts.json' if level == 'b1b' else 'a2_support_texts.json'}")
    kp = rj(f"{base}/key_phrases/keywords_canonicalized.json")
    kp_by_rank = {i["rank"]: i for i in kp["items"]}
    expl = {}
    if level == "b1b":
        tts = rj(f"{base}/audit/tts_generation_results.json")
        expl = {int(r): {"explanation": (v.get("explanation") or {}).get("explanation_text")} for r, v in (tts.get("key_phrases") or {}).items()}
    rows = []
    for e in timeline:
        part = e["part"]
        if part.startswith("pause_"):
            continue
        s, dur = e["start_seconds"], e["duration_seconds"]
        fn = f"{key}_{len(rows):02d}.mp3"
        to_mp3(x[int(round(s * sr)): int(round((s + dur) * sr))], sr, os.path.join(web_aud, fn))
        info = R._row_info_family_x(part, level, parts, support, f"{base}/narration", kp_by_rank, ja_title, kp_explanations_by_rank=expl or None)
        if part.startswith("Key Phrase "):
            it = kp_by_rank[int(part.split(" ")[-1])]
            if level == "b1b":
                blocks = [uc.kp_block(["英語", "英語での解説"], [it["used_form"], expl[it["rank"]]["explanation"]])]
            else:
                blocks = [uc.kp_block(["英語", "日本語の意味"], [it["used_form"], it["japanese_gloss"]])]
        elif info["sfx"]:
            blocks = ["<span class='sec'>効果音・音楽(読み上げなし)</span>"]
        elif info["voice"] is None or info["text"].startswith("(共有固定"):
            blocks = ["<span class='sec'>定型の案内音声</span>"]
        else:
            blocks = [f"<div class='script'>{esc(info['text'])}</div>"]
        rows.append({"part": part, "start": s, "dur": dur, "src": f"audio/{fn}", "blocks": blocks})
    return {"summ": summ, "full": full, "duration": x.shape[0] / sr, "rows": rows, "parts": parts, "kp": kp, "support": support}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-name", default="run_form_prod_01")
    ap.add_argument("--web", default="user_test/family_x_ai_island_form_01")
    a = ap.parse_args()
    run = f"er019_output/family_x_audio_production_wiring_01/{SLUG}__{a.run_name}"
    source_dir = f"er019_output/{SLUG}/{a.run_name}"
    web_aud = os.path.join(a.web, "audio")
    os.makedirs(web_aud, exist_ok=True)
    ja_title = R.derive_japanese_title(source_dir)["japanese_title"]
    levels, info = [], {}
    for level, key, lid, label, jp in (("a2", "std", "std", "Standard", "Standard"), ("b1b", "adv", "adv", "Advanced", "Advanced")):
        d = level_data(run, source_dir, web_aud, level, key, label, ja_title)
        article_text = open(f"{source_dir}/{level}/article.md", encoding="utf-8").read()
        study = p2w.public_study_html(run, article_text, level=level)
        info[level] = d
        levels.append({"id": lid, "label": label, "full_src": f"audio/{d['full']}", "duration": d["duration"], "rows": d["rows"], "study_html": study})
    # 補助(全レベル節の後ろ): 制作情報と事後試聴リスト
    aux = ["<details class='aux'><summary>制作情報</summary><ul>"]
    for level, lab in (("a2", "Standard"), ("b1b", "Advanced")):
        sel = rj(f"{run}/{level}/key_phrases/confirmed_selection.json")
        aux.append(f"<li>{lab}: 本文sha256={esc(hashlib.sha256(open(f'{source_dir}/{level}/article.md', 'rb').read()).hexdigest()[:16])}… / "
                   f"ユーザー確定 confirmation_id={esc(sel['confirmation_id'][:19])} / 文法={esc(str((sel.get('grammar') or {}).get('status')))}(0件) / "
                   f"長さ={info[level]['duration']:.0f}秒</li>")
    aux.append("</ul></details>")
    pw = []
    for level, lab in (("a2", "Standard"), ("b1b", "Advanced")):
        lst = rj(f"{run}/{level}/audit/pass_with_warning_listening_list.json") if os.path.exists(f"{run}/{level}/audit/pass_with_warning_listening_list.json") else {"count": 0, "entries": []}
        items = "".join(f"<li>{esc(e.get('segment_id', ''))} / 期待={esc(str(e.get('canonical_text')))} / 一次ASR={esc(str(e.get('primary_text')))} / "
                        f"二次ASR={esc(str(e.get('secondary_text')))} / {esc(','.join(e.get('warning_labels') or []))}</li>" for e in lst.get("entries", []))
        pw.append(f"<h3>{lab}: 事後試聴リスト(PASS_WITH_WARNING) {lst.get('count', 0)}件</h3><ul>{items}</ul>")
    aux_html = "".join(aux) + "<h2 id='pww'>事後試聴リスト(PASS_WITH_WARNING、非ブロッキング)</h2>" + "".join(pw)
    title = f"{ja_title} 試聴ページ"
    intro = ("<div class='note'><b>状態: 完成版・ユーザー試聴待ち</b>(試聴PASSは未取得です)。Key Phrase／Key Wordはユーザー確定の各10件、文法は0件(確定済み)です。"
             "上のリンクでレベルを切り替えられます。<br>"
             "<b>後続反映予定</b>: 区分③(本文ハイライト・短い日本語意味)とStandardの区分②(追加解説)は、共通の表示機構が整い次第ページに追加します(音声の再生成はありません)。"
             "Advancedの学習内容は区分①＋②の5件です。</div>")
    page = uc.render_standard_page(title, levels, intro_html=intro, aux_html=aux_html)
    with open(os.path.join(a.web, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    print("page written", a.web, {lv["label"]: (len(lv["rows"]), round(lv["duration"], 2)) for lv in levels})


if __name__ == "__main__":
    main()

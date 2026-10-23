# -*- coding: utf-8 -*-
"""FAMILY-Y-VOICES-DESIGN-01 委任_08 Phase B: Family Y Persona Trial 試聴ページ生成(API 0、DEV/Trial専用)。
出力: user_test/family_y_trial_02/{index.html, audio/*.mp3}。Standard/Advanced切替、全編通し再生、パート別再生(Comment 1/2・見出し・Voice・
Tension+Closing)、全スクリプト、Key Phrase、日本語の元原稿、3人の人物設定(要約)、Trial表示、前回Trial(R0g)との比較リンク。開発者向け情報は載せない。
入力は er110_family_y_persona_audio_trial_01 の assemble 出力(Audio Validation Gate / Y style gate PASS)のみ。"""
from __future__ import annotations

import argparse
import glob
import html
import json
import os
import re
import subprocess

import imageio_ffmpeg
import soundfile as sf

import er110_family_y_persona_audio_trial_01 as y
import er110_family_y_persona_text_trial_01 as p
import er_user_listening_page_common_01 as common_page

ROOT = os.path.dirname(os.path.abspath(__file__))
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
esc = html.escape
WEB = os.path.join(ROOT, "user_test", "family_y_trial_02")
AUD = os.path.join(WEB, "audio")
NOSCRIPT = {"intro": "オープニング(導入)", "welcome": "ウェルカム(定型)", "notification": "(区切りの音)", "outro": "エンディング(定型)",
            "key phrases intro": "Key Phrasesの導入(定型)", "full story intro": "Full Storyの導入(定型)", "preview intro": "Previewの導入(定型)"}
PERSON = {"full_story_part1": "人物1(男性の声)", "full_story_part2": "人物2(女性の声)", "full_story_part3": "人物3(男性の声)",
          "full_story_part3_c2": "語り手(Tension+Closing、女性ナレーター)"}


def rj(p_):
    with open(p_, encoding="utf-8") as f:
        return json.load(f)


def mp3(x, sr, out, br="96k"):
    tmp = out + ".tmp.wav"
    sf.write(tmp, x, sr)
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", tmp, "-codec:a", "libmp3lame", "-b:a", br, out], check=True)
    os.remove(tmp)


def _script(text):
    return "<div class='script'>" + esc(text or "").replace("\n", "<br>") + "</div>"


def _kp_html(level, rank, kp_item, res, expl):
    k = res["key_phrases"][str(rank)]
    en = kp_item["used_form"]
    if level == "a2":
        ja = k["japanese_meaning"].get("canonical_text") or kp_item.get("japanese_gloss") or ""
        return common_page.kp_block(["英語", "日本語の意味"], [en, ja])
    ex = ((expl or {}).get("items") or {})
    row = ex.get(str(rank)) or ex.get(rank) or {}
    text = k["explanation"].get("explanation_text") or row.get("english_explanation") or ""
    return common_page.kp_block(["Key Phrase", "英語での解説"], [en, text])


def _ja_paras(it):
    t = open(os.path.join(y.TEXT_ROOT, it, "article_ja.md"), encoding="utf-8").read()
    m = re.match(r"^(.+?)\n+(.*)$", t.strip(), re.S)
    return [b.strip() for b in re.split(r"\n\s*\n", m.group(2)) if b.strip()]


def build_level(it, level):
    theme = y.theme_dir(it)
    base = os.path.join(theme, level)
    wavs = sorted(glob.glob(os.path.join(base, "assembled", "*.wav")))
    assert len(wavs) == 1, wavs
    x, sr = sf.read(wavs[0], dtype="float32")
    tag = "adv" if level == "b1b" else "std"
    full = f"{tag}_full.mp3"
    mp3(x, sr, os.path.join(AUD, full), br="128k")
    tl = rj(os.path.join(base, "audit", "timeline.json"))
    parts = rj(os.path.join(base, "parts.json"))
    res = rj(os.path.join(base, "audit", "tts_generation_results.json"))
    kp_items = sorted(rj(os.path.join(base, "key_phrases", "keywords_canonicalized.json"))["items"], key=lambda i_: i_["rank"])
    expl = res.get("key_phrase_explanations_text") or {}
    support = rj(os.path.join(base, "a2_support_texts.json" if level == "a2" else "b1_support_texts.json"))
    ja = _ja_paras(it)
    hd = rj(os.path.join(y.TEXT_ROOT, it, "headings", "headings.json"))["headings"]
    noslow = None
    if level == "a2":
        nsw = sorted(glob.glob(os.path.join(base, "assembled_voice_noslow", "*.wav")))
        if nsw:
            xn, srn = sf.read(nsw[0], dtype="float32")
            fulln = f"{tag}_full_voice_noslow.mp3"
            mp3(xn, srn, os.path.join(AUD, fulln), br="128k")
            tln = rj(os.path.join(base, "audit", "voice_noslow_timeline.json"))
            noslow = {"full": fulln, "duration": xn.shape[0] / srn, "x": xn, "sr": srn, "tl": tln}
    rows = []
    for e in tl:
        part = e["part"]
        if part.startswith("pause"):
            continue
        s0, dur = e["start_seconds"], e["duration_seconds"]
        fn = f"{tag}_{len(rows):02d}.mp3"
        mp3(x[int(round(s0 * sr)): int(round((s0 + dur) * sr))], sr, os.path.join(AUD, fn))
        pl = part.lower()
        blocks, label, extra = [], part, None
        mh = re.match(r"narrator: (one voice|another voice|a third voice) heading", pl)
        mv = re.match(r"full story: voice (\d)", pl)
        if mh:
            i = ["one voice", "another voice", "a third voice"].index(mh.group(1))
            label = f"見出し{i + 1}(ナレーター)"
            blocks.append(_script(hd[i]["spoken_en"]))
            blocks.append(f"<span class='sec'>日本語の見出し(読み上げなし): {esc(hd[i]['title_ja'])}</span>")
        elif mv or pl.startswith("full story: tension"):
            n = int(mv.group(1)) if mv else 4
            seg = y.Y_BODY_IDS[n - 1]
            label = f"Full Story Part {n} — {PERSON[seg]}"
            blocks.append(_script(parts[f"part{n}"]))
            blocks.append("<details><summary>日本語の元原稿</summary><div class='ja'>" + esc(ja[n - 1]) + "</div></details>")
            if noslow is not None and mv:
                ent = next((t for t in noslow["tl"] if t["part"].lower().startswith(f"full story: voice {mv.group(1)}")), None)
                if ent:
                    fn2 = f"{tag}_{len(rows):02d}_noslow.mp3"
                    a, b = int(round(ent["start_seconds"] * noslow["sr"])), int(round((ent["start_seconds"] + ent["duration_seconds"]) * noslow["sr"]))
                    mp3(noslow["x"][a:b], noslow["sr"], os.path.join(AUD, fn2))
                    extra = fn2
        elif pl.startswith("topic intro"):
            blocks.append(_script(res["segments"]["topic_intro"].get("canonical_text")))
        elif pl.startswith("japanese title"):
            blocks.append(_script(res["segments"]["japanese_title"].get("canonical_text") or res["segments"]["japanese_title"].get("text")))
        elif pl.startswith("preview (") or pl == "preview":
            blocks.append(_script(support["preview"]))
        elif re.match(r"comment (\d)", pl):
            blocks.append(_script(support["comment_" + re.match(r"comment (\d)", pl).group(1)]))
        elif pl.startswith("in one line"):
            blocks.append(_script(parts["in_one_line"]))
        elif re.match(r"key phrase (\d)$", pl):
            r = int(re.match(r"key phrase (\d)$", pl).group(1))
            blocks.append(_kp_html(level, kp_items[r - 1]["rank"], kp_items[r - 1], res, expl))
        else:
            key = pl.split(" (")[0].rstrip("0123456789 ").strip()
            blocks.append("<span class='sec'>" + esc(NOSCRIPT.get(key, "(定型音声)")) + "</span>")
        rows.append((label, s0, dur, fn, blocks, extra))
    return {"full": full, "duration": x.shape[0] / sr, "rows": rows, "noslow": noslow, "parts": parts, "tag": tag}


def build_blocked_level(it, level):
    """Audio Validation Gate / Y style gate でAssemblyが拒否されたlevel(人間確認待ちsegmentあり)。全編通し音声は作らない(Gateを回避しない)。
    個別segmentのtakeだけを順番に載せ、停止したsegmentのtakeは『人間確認待ち』と明示する。"""
    theme = y.theme_dir(it)
    base = os.path.join(theme, level)
    nd = os.path.join(base, "narration")
    parts = rj(os.path.join(base, "parts.json"))
    rls_path = os.path.join(base, "audit", "review_lock_state.json")
    rls = rj(rls_path) if os.path.exists(rls_path) else {}
    support = rj(os.path.join(base, "a2_support_texts.json" if level == "a2" else "b1_support_texts.json"))
    ja = _ja_paras(it)
    hd = rj(os.path.join(y.TEXT_ROOT, it, "headings", "headings.json"))["headings"]
    tag = "adv" if level == "b1b" else "std"
    held = {n for n, e in rls.items() if e.get("final_status") != "OK"}            # 人間確認待ち(HR Lock)
    ok = {n for n, e in rls.items() if e.get("final_status") == "OK"}
    plan = [("Preview", "preview", _script(support["preview"])), ("Comment 1", "comment_1", _script(support["comment_1"])),
            ("Comment 2", "comment_2", _script(support["comment_2"]))]
    for i in range(3):
        plan.append((f"見出し{i + 1}(ナレーター)", y.HEADING_IDS[i], _script(hd[i]["spoken_en"])))
        plan.append(("S", y.Y_BODY_IDS[i], None))
    plan += [("S", y.Y_BODY_IDS[3], None), ("In One Line", "in_one_line", _script(parts["in_one_line"]))]
    rows = []
    for label, seg, blk in plan:
        w = os.path.join(nd, f"{seg}.wav")
        if not os.path.exists(w):
            rows.append((label + "【未生成】", 0.0, 0.0, None, [blk or ""], None))
            continue
        x, sr = sf.read(w, dtype="float32")
        fn = f"{tag}_part_{len(rows):02d}.mp3"
        mp3(x, sr, os.path.join(AUD, fn))
        blocks = []
        if label == "S":
            n = y.Y_BODY_IDS.index(seg) + 1
            label = f"Full Story Part {n} — {PERSON[seg]}"
            blocks.append(_script(parts[f"part{n}"]))
            blocks.append("<details><summary>日本語の元原稿</summary><div class='ja'>" + esc(ja[n - 1]) + "</div></details>")
        else:
            blocks.append(blk)
        if seg in held:
            label += "【人間確認待ちのテイク】"
            blocks.insert(0, "<div class='hold'>このパートは自動検査(繰り返し検出)で停止しました。読み上げは原稿どおりで、自動の文字起こし照合は合格しています。"
                             "聴いて問題がなければ承認が必要です(承認されると全編通し音声を組み立てられます)。</div>")
        elif seg not in ok:
            label += "【生成途中で中断したテイク(未確定)】"
            blocks.insert(0, "<div class='hold'>費用の上限に達したため、この段階で生成を止めました。このテイクは検査が終わっていない途中のもので、確定していません。</div>")
        rows.append((label, 0.0, sf.info(w).duration, fn, blocks, None))
    return {"blocked": True, "rows": rows, "parts": parts, "tag": tag, "held": sorted(held), "missing": [r[0] for r in rows if r[3] is None]}


def rows_html(rows):
    out = []
    for label, s0, dur, fn, blocks, extra in rows:
        aud = f"<audio controls preload='none' src='audio/{fn}'></audio>" if fn else "<span class='sec'>(音声なし)</span>"
        if extra:
            aud = "<div class='sec'>通常(減速あり)</div>" + aud + "<div class='sec'>この人物の語りだけ減速なし</div>" + f"<audio controls preload='none' src='audio/{extra}'></audio>"
        out.append(f"<tr><td><b>{esc(label)}</b><br><span class='sec'>{s0:.1f}秒〜 ({dur:.1f}秒)</span></td><td class='play'>{aud}</td><td>{''.join(blocks)}</td></tr>")
    return ("<table><thead><tr><th>パート</th><th>音声</th><th>Script / Key Phrase</th></tr></thead><tbody>" + "".join(out) + "</tbody></table>")


def personas_html():
    names = {"voice_1": "人物1(男性の声)", "voice_2": "人物2(女性の声)", "voice_3": "人物3(男性の声)"}
    rows = "".join(
        f"<tr><td><b>{esc(names[s])}</b><br>{esc(p.SHEETS[s]['label'])}</td><td>{esc(p.SHEETS[s]['profile'])}</td><td>{esc(p.SHEETS[s]['claim'])}</td>"
        f"<td>{esc(p.SHEETS[s]['rhythm'])}</td></tr>" for s in p.VOICE_SLOTS)
    return ("<details open><summary><b>3人の人物設定(要約)</b></summary>"
            f"<div class='note'><b>3人に共通の前提(今回の具体案)</b>: {esc(p.COMMON_PREMISE_JA)}</div>"
            "<table><thead><tr><th>人物</th><th>年齢・生活</th><th>この人の主張</th><th>話し方(文のリズム)</th></tr></thead><tbody>" + rows + "</tbody></table></details>")


def section(level, d):
    sid = d["tag"]
    lab = "Advanced" if level == "b1b" else "Standard"
    if d.get("blocked"):
        return (f"<section id='{sid}' class='lv hidden'><h2>{lab}(通し再生なし: 人間確認待ち)</h2>"
                "<div class='hold'><b>このレベルは全編通し音声をまだ作れていません。</b>"
                + ("1つのパート(下で「人間確認待ち」と表示)が自動検査(繰り返し検出)で止まったためです。止まったパートを聴いて承認すると、全編通し音声を組み立てられます。"
                   if not d.get("missing") else "生成の途中で費用の上限に達したため、一部のパートが未生成です(下で「未生成」と表示)。人物1の語りは自動検査(繰り返し検出)で確定できていません。")
                + "それまでは、パートごとの音声だけ確認できます。</div>"
                f"<div class='note'><b>In One Line</b>: {esc(d['parts']['in_one_line'])}</div>"
                "<details open><summary>パート別再生・全スクリプト</summary>" + rows_html(d["rows"]) + "</details></section>")
    noslow_html = ""
    if d["noslow"]:
        n = d["noslow"]
        noslow_html = (f"<div class='combo2'><b>比較: 3人の語りだけ「減速なし」の通し再生</b>(約{n['duration'] / 60:.1f}分)<br>"
                       f"<span class='sec'>標準(上)は全体を約6%ゆっくりにしています。こちらは人物1〜3の語りのみ減速せず、他は同じです。</span>"
                       f"<audio id='main_{sid}_noslow' controls preload='none' src='audio/{n['full']}'></audio></div>")
    dur = d["duration"]
    return (f"<section id='{sid}' class='lv hidden'><h2>{lab}(通し再生 約{dur / 60:.1f}分 / {dur:.0f}秒)</h2>"
            f"<div class='combo'><b>全編を通し再生{'(標準: 全体を約6%ゆっくり)' if level == 'a2' else ''}</b><br>"
            f"<audio id='main_{sid}' controls preload='none' src='audio/{d['full']}'></audio></div>{noslow_html}"
            f"<div class='note'><b>In One Line</b>: {esc(d['parts']['in_one_line'])}</div>"
            "<details open><summary>パート別再生・全スクリプト・Key Phrase</summary>" + rows_html(d["rows"]) + "</details></section>")


CSS = ("<style>body{font-family:sans-serif;max-width:1100px;margin:1em auto;padding:0 1em;line-height:1.5}table{border-collapse:collapse;width:100%;margin:.5em 0 1.5em}"
       "th,td{border:1px solid #ccc;padding:6px;vertical-align:top;text-align:left}td.play{min-width:340px}audio{width:100%}.sec{color:#666;font-size:.85em}"
       ".script{background:#f6f6f6;padding:4px;margin:3px 0;font-size:.95em}.ja{background:#fffdf5;padding:4px;margin:3px 0;font-size:.9em;white-space:pre-wrap}"
       ".kp td,.kp th{border:1px solid #ccc;padding:4px 10px;width:50%}"
       ".combo{background:#eef6ff;padding:10px;border:1px solid #99c;margin-bottom:1em}.combo2{background:#f3eefc;padding:10px;border:1px solid #a9c;margin-bottom:1em}"
       ".hold{background:#fff0d0;padding:8px;border:2px solid #d90;margin:6px 0}.note{background:#fff8e0;padding:8px;border:1px solid #cb8;margin-bottom:1em}.trial{background:#fde8e8;padding:10px;border:2px solid #c55;margin-bottom:1em;font-weight:bold}"
       ".tabs button{font-size:1.05em;padding:.45em 1.3em;margin:0 .5em .5em 0;cursor:pointer}.tabs button.on{background:#336;color:#fff}.hidden{display:none}</style>")
JS = ("<script>var L='std';function show(){for(const s of document.querySelectorAll('section.lv')){s.classList.toggle('hidden',s.id!==L);}"
      "for(const b of document.querySelectorAll('.tabs button')){b.classList.toggle('on',b.dataset.k===L);}history.replaceState(null,'','#'+L);}"
      "document.querySelectorAll('.tabs button').forEach(b=>b.onclick=()=>{L=b.dataset.k;show();});"
      "(function(){const h=location.hash.slice(1);if(h==='std'||h==='adv'){L=h;}show();})();</script>")


def standard_check(built):
    levels, names = [], []
    for lvl, label in (("a2", "Standard"), ("b1b", "Advanced")):
        d = built.get(lvl)
        if d is None or d.get("blocked"):
            continue
        levels.append({"id": label.lower(), "label": label, "full_src": f"audio/{d['full']}", "duration": d["duration"],
                       "rows": [{"part": r[0], "start": r[1], "dur": r[2], "src": f"audio/{r[3]}", "blocks": r[4]} for r in d["rows"]]})
        names.append(label)
    if not levels:
        return {"overall": "NOT_APPLICABLE(全levelで通し再生音声なし=標準ページ検査の対象外)", "checks": {}, "levels_checked": []}
    html_text = common_page.render_standard_page("Family Y Persona Trial", levels)
    out = common_page.check_page(html_text, base_dir=WEB, levels=tuple(names))
    out["levels_checked"] = names
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--it", default="it1")
    a = ap.parse_args()
    os.makedirs(AUD, exist_ok=True)
    for f in glob.glob(os.path.join(AUD, "*.mp3")):
        os.remove(f)
    built, secs = {}, []
    for lvl in ("a2", "b1b"):
        d = build_level(a.it, lvl) if glob.glob(os.path.join(y.theme_dir(a.it), lvl, "assembled", "*.wav")) else build_blocked_level(a.it, lvl)
        built[lvl] = d
        secs.append(section(lvl, d))
    title = "学校でスマホを預けるべき?(Family Y・3人の声・第2回Trial)試聴ページ"
    tabs = "<div class='tabs'><button data-k='std'>Standard</button><button data-k='adv'>Advanced</button></div>"
    prev = ("<div class='note'><b>前回Trial(R0g)との比較</b>: 同じテーマの前回の試作は "
            "<a href='../family_y_trial_01/index.html#r0_std'>こちら(Standard)</a> / <a href='../family_y_trial_01/index.html#r0_adv'>こちら(Advanced)</a>。"
            "今回は、先に「実在しそうな3人の人物」を設計し、各人物の主張・経験・感情から語りを作り直しています。各語りの前にナレーターが短い見出しを読み、"
            "最後の1パートで3人の違いを整理します。</div>")
    pg = (f"<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><title>{esc(title)}</title>"
          f"<meta name='viewport' content='width=device-width, initial-scale=1'>{CSS}</head><body><h1>{esc(title)}</h1>"
          "<div class='trial'>Trial(未採用): 新しい番組形式(Family Y)の試作です。正式採用は決まっていません。</div>"
          + ("<div class='hold'><b>途中経過版(通し再生はまだありません)</b>: Advancedは人物1の語りが自動検査(繰り返し検出)で止まっており、他のパートは生成済みです。"
             "Standardは生成の途中で費用の上限に達したため、一部のパートだけです。聴けるのはパート別の音声です。続きは判断待ちです。</div>"
             if any(d.get("blocked") for d in built.values()) else "")
          + "<div class='note'>同じテーマを、暮らしも立場も違う3人がそれぞれ自分の言葉で語る形式です。人物の実在感、主張の分かりやすさ、3人の聞き分けやすさ、"
          "最後のまとめが耳で分かるかを確かめるための試聴ページです。上のボタンでレベル(Standard/Advanced)を切り替えられます。</div>"
          + prev + personas_html() + tabs + "".join(secs) + JS + "</body></html>")
    assert "file:///" not in pg and "C:\\" not in pg and "C:/" not in pg
    with open(os.path.join(WEB, "index.html"), "w", encoding="utf-8") as f:
        f.write(pg)
    info = {l: {"rows": len(d["rows"]), "duration": round(d.get("duration", 0), 1), "blocked": bool(d.get("blocked"))} for l, d in built.items()}
    print("page written", json.dumps(info))
    chk = standard_check(built)
    os.makedirs(y.theme_dir(a.it), exist_ok=True)
    with open(os.path.join(y.theme_dir(a.it), "page_standard_check.json"), "w", encoding="utf-8") as f:
        json.dump(chk, f, ensure_ascii=False, indent=1)
    print("standard check:", chk["overall"])
    for k, cv in chk["checks"].items():
        if not cv["ok"]:
            print("  FAIL", k, cv["detail"])
    return built


if __name__ == "__main__":
    main()

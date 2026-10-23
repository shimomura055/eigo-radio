# -*- coding: utf-8 -*-
"""FAMILY-Y-VOICES-DESIGN-01 委任_05 Phase 3: Family Y Trial 試聴ページ生成(API 0、DEV/Trial専用)。
出力: user_test/family_y_trial_01/{index.html, audio/*.mp3}。候補R2g/R0g × Standard/Advanced切替、全編通し再生、パート別再生、
全スクリプト、Key Phrase(英語+意味/解説)、人物Voice Card要約、Std「減速あり/Voice part減速なし」比較。開発者向け情報は載せない。
入力はer110_family_y_audio_trial_01 の assemble 出力(Audio Validation Gate / Y style gate PASS)のみ。"""
from __future__ import annotations

import glob
import html
import json
import os
import re
import subprocess

import imageio_ffmpeg
import soundfile as sf

import er110_family_y_audio_trial_01 as y
import er_user_listening_page_common_01 as common_page

ROOT = os.path.dirname(os.path.abspath(__file__))
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
esc = html.escape
WEB = os.path.join(ROOT, "user_test", "family_y_trial_01")
AUD = os.path.join(WEB, "audio")
SRC_ROOT = os.path.join(ROOT, "er110_output", "family_y_trial_01", "school_phone_ban")
THEME = os.path.join(ROOT, y.OUT_ROOT)

CAND_LABEL = {"r2": "候補A(R2g)", "r0": "候補B(R0g)"}
CAND_DESC = {
    "r2": "R2g: 導入の情景と最終パートの比喩の回収を重視して仕上げた原稿(主候補)。",
    "r0": "R0g: 基本の書き方のまま、不適切な箇所だけを局所修正した原稿(比較候補。追加の磨き込みなし)。",
}
PERSON = {
    "full_story_part1": ("語り手(リード)", "女性ナレーター"),
    "full_story_part2": ("人物1: 中学校で国語を教える教員", "男性の声"),
    "full_story_part3": ("人物2: 自治体で学校教育の予算査定を担当する職員", "女性の声"),
    "full_story_part3_c2": ("人物3: 働きながら定時制高校に通う成人の生徒", "男性の声"),
    "full_story_part3_c3": ("語り手(まとめ)", "女性ナレーター"),
}
NOSCRIPT = {"intro": "オープニング(導入)", "welcome": "ウェルカム(定型)", "notification": "(区切りの音)", "outro": "エンディング(定型)",
            "key phrases intro": "Key Phrasesの導入(定型)", "full story intro": "Full Storyの導入(定型)", "preview intro": "Previewの導入(定型)"}


def rj(p):
    with open(p, encoding="utf-8") as f:
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


def _ja_original(cand, idx):
    p = os.path.join(SRC_ROOT, "y_writer", f"gate_{cand}", "article_final.md")
    t = open(p, encoding="utf-8").read()
    m = re.match(r"^#\s+(.+?)\s*\n+(.*)$", t.strip(), re.S)
    rest = m.group(2) if m else t
    rest = re.split(r"\n##\s*(?:In one line|ひとこと|In One Line)", "\n" + rest, flags=re.I)[0]
    paras = [b.strip() for b in re.split(r"\n\s*\n", rest) if b.strip()]
    return paras[idx] if idx < len(paras) else ""


def build_level(cand, level, voice_noslow_rows=None):
    """戻り値: dict(full_mp3, duration, rows[(part_label, start, dur, mp3name, html_blocks, extra_audio)]), noslow dict or None"""
    theme = os.path.join(THEME, cand)
    base = os.path.join(theme, level)
    wavs = sorted(glob.glob(os.path.join(base, "assembled", "*.wav")))
    assert len(wavs) == 1, wavs
    x, sr = sf.read(wavs[0], dtype="float32")
    tag = f"{cand}_{'adv' if level == 'b1b' else 'std'}"
    full = f"{tag}_full.mp3"
    mp3(x, sr, os.path.join(AUD, full), br="128k")
    tl = rj(os.path.join(base, "audit", "timeline.json"))
    parts = rj(os.path.join(base, "parts.json"))
    res = rj(os.path.join(base, "audit", "tts_generation_results.json"))
    kp_items = sorted(rj(os.path.join(base, "key_phrases", "keywords_canonicalized.json"))["items"], key=lambda it: it["rank"])
    expl = res.get("key_phrase_explanations_text") or {}
    support = rj(os.path.join(base, "a2_support_texts.json" if level == "a2" else "b1_support_texts.json"))
    # voice_noslow variant(Stdのみ): 全編 + Voice partの該当区間
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
    for i, e in enumerate(tl):
        part = e["part"]
        if part.startswith("pause"):
            continue
        s0, dur = e["start_seconds"], e["duration_seconds"]
        fn = f"{tag}_{len(rows):02d}.mp3"
        mp3(x[int(round(s0 * sr)): int(round((s0 + dur) * sr))], sr, os.path.join(AUD, fn))
        pl = part.lower()
        blocks, label, extra = [], part, None
        m = re.match(r"full story: (lead|voice (\d)|closing)", pl)
        if m:
            seg = {"lead": "full_story_part1", "voice 1": "full_story_part2", "voice 2": "full_story_part3",
                   "voice 3": "full_story_part3_c2", "closing": "full_story_part3_c3"}[m.group(1)]
            n = y.Y_BODY_IDS.index(seg) + 1
            who, vtype = PERSON[seg]
            label = f"Full Story Part {n} — {who}({vtype})" if seg in y.VOICE_SEGMENT_IDS else f"Full Story Part {n} — {who}"
            blocks.append(_script(parts[f"part{n}"]))
            blocks.append("<details><summary>日本語の元原稿</summary><div class='ja'>" + esc(_ja_original(cand, n - 1)) + "</div></details>")
            if noslow is not None and seg in y.VOICE_SEGMENT_IDS:
                ent = next((t for t in noslow["tl"] if t["part"].lower().startswith(pl[:len("full story: voice 1")])), None)
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


def build_blocked_level(cand, level):
    """Audio Validation Gate / Y style gate でAssemblyが拒否されたlevel(人間確認待ちsegmentあり)。全編通し音声は作らない(Gateを回避しない)。
    個別segmentのtakeだけを順番に載せ、停止したsegmentのtakeは『人間確認待ち』と明示する。"""
    theme = os.path.join(THEME, cand)
    base = os.path.join(theme, level)
    nd = os.path.join(base, "narration")
    parts = rj(os.path.join(base, "parts.json"))
    res = rj(os.path.join(base, "audit", "tts_generation_results.json"))
    support = rj(os.path.join(base, "a2_support_texts.json" if level == "a2" else "b1_support_texts.json"))
    tag = f"{cand}_{'adv' if level == 'b1b' else 'std'}"
    held = {n for n, e in res["segments"].items() if e.get("status") != "OK"}
    plan = [("Preview", "preview", _script(support["preview"])), ("Comment 1", "comment_1", _script(support["comment_1"])),
            ("S", "full_story_part1", None), ("Comment 2", "comment_2", _script(support["comment_2"])),
            ("S", "full_story_part2", None), ("S", "full_story_part3", None), ("S", "full_story_part3_c2", None),
            ("Comment 3", "comment_3", _script(support["comment_3"])), ("S", "full_story_part3_c3", None),
            ("In One Line", "in_one_line", _script(parts["in_one_line"]))]
    rows = []
    for label, seg, blk in plan:
        w = os.path.join(nd, f"{seg}.wav")
        x, sr = sf.read(w, dtype="float32")
        fn = f"{tag}_part_{len(rows):02d}.mp3"
        mp3(x, sr, os.path.join(AUD, fn))
        blocks = []
        if label == "S":
            n = y.Y_BODY_IDS.index(seg) + 1
            who, vtype = PERSON[seg]
            label = f"Full Story Part {n} — {who}({vtype})" if seg in y.VOICE_SEGMENT_IDS else f"Full Story Part {n} — {who}"
            blocks.append(_script(parts[f"part{n}"]))
            blocks.append("<details><summary>日本語の元原稿</summary><div class='ja'>" + esc(_ja_original(cand, n - 1)) + "</div></details>")
        else:
            blocks.append(blk)
        if seg in held:
            label += "【人間確認待ちのテイク】"
            blocks.insert(0, "<div class='hold'>このパートは自動検査(繰り返し検出)で停止しました。読み上げは原稿どおりで、自動の文字起こし照合は合格しています。"
                             "聴いて問題がなければ承認が必要です(承認されると全編通し音声を組み立てられます)。</div>")
        rows.append((label, 0.0, sf.info(w).duration, fn, blocks, None))
    return {"blocked": True, "rows": rows, "parts": parts, "tag": tag, "held": sorted(held)}


def rows_html(rows, blocked=False):
    out = []
    for label, s0, dur, fn, blocks, extra in rows:
        aud = f"<audio controls preload='none' src='audio/{fn}'></audio>"
        if extra:
            aud = "<div class='sec'>通常(減速あり)</div>" + aud + "<div class='sec'>この人物の語りだけ減速なし</div>" + f"<audio controls preload='none' src='audio/{extra}'></audio>"
        timing = f"<span class='sec'>{s0:.1f}秒〜 ({dur:.1f}秒)</span>" if s0 or dur and not blocked else f"<span class='sec'>({dur:.1f}秒)</span>"
        out.append(f"<tr><td><b>{esc(label)}</b><br>{timing}</td><td class='play'>{aud}</td><td>{''.join(blocks)}</td></tr>")
    return ("<table><thead><tr><th>パート</th><th>音声</th><th>Script / Key Phrase</th></tr></thead><tbody>" + "".join(out) + "</tbody></table>")


def cards_html():
    cards = rj(os.path.join(SRC_ROOT, "y_cast", "voice_cards.json"))["cards"]
    names = {"voice_1": "人物1(男性の声)", "voice_2": "人物2(女性の声)", "voice_3": "人物3(男性の声)"}
    rows = "".join(
        f"<tr><td><b>{esc(names[c['slot']])}</b><br>{esc(c['person_label'])}</td><td>{esc(c['situation_and_scene'])}</td>"
        f"<td>{esc(c['concern'])}</td><td>{esc(c['stake'])}</td></tr>" for c in cards)
    return ("<details open><summary><b>3人の人物設定(要約)</b></summary><table><thead><tr><th>人物</th><th>状況と場面</th><th>気にかかっていること</th>"
            "<th>守りたいもの</th></tr></thead><tbody>" + rows + "</tbody></table></details>")


def section(cand, level, d):
    sid = f"{cand}_{'adv' if level == 'b1b' else 'std'}"
    lab = "Advanced" if level == "b1b" else "Standard"
    if d.get("blocked"):
        return (f"<section id='{sid}' class='lv hidden'><h2>{lab}・{esc(CAND_LABEL[cand])}(通し再生なし: 人間確認待ち)</h2>"
                f"<div class='note'>{esc(CAND_DESC[cand])}</div>"
                "<div class='hold'><b>このレベルは全編通し音声をまだ作れていません。</b>1つのパート(下で「人間確認待ち」と表示)が自動検査で止まったためです。"
                "止まったパートを聴いて承認すると、全編通し音声を組み立てられます。それまでは、パートごとの音声だけ確認できます。</div>"
                f"<div class='note'><b>In One Line</b>: {esc(d['parts']['in_one_line'])}</div>"
                "<details open><summary>パート別再生・全スクリプト</summary>" + rows_html(d["rows"], blocked=True) + "</details></section>")
    noslow_html = ""
    if d["noslow"]:
        n = d["noslow"]
        noslow_html = (f"<div class='combo2'><b>比較: 3人の語りだけ「減速なし」の通し再生</b>(約{n['duration'] / 60:.1f}分)<br>"
                       f"<span class='sec'>標準(上)は全体を約6%ゆっくりにしています。こちらは人物1〜3の語りのみ減速せず、他は同じです。</span>"
                       f"<audio id='main_{sid}_noslow' controls preload='none' src='audio/{n['full']}'></audio></div>")
    dur = d["duration"]
    return (f"<section id='{sid}' class='lv hidden'><h2>{lab}・{esc(CAND_LABEL[cand])}(通し再生 約{dur / 60:.1f}分 / {dur:.0f}秒)</h2>"
            f"<div class='note'>{esc(CAND_DESC[cand])}</div>"
            f"<div class='combo'><b>全編を通し再生{'(標準: 全体を約6%ゆっくり)' if level == 'a2' else ''}</b><br>"
            f"<audio id='main_{sid}' controls preload='none' src='audio/{d['full']}'></audio></div>{noslow_html}"
            f"<div class='note'><b>In One Line</b>: {esc(d['parts']['in_one_line'])}</div>"
            "<details open><summary>パート別再生・全スクリプト・Key Phrase</summary>" + rows_html(d["rows"]) + "</details></section>")


def aux_html(cands):
    pw = []
    for c in cands:
        for lvl, lab in (("a2", "Standard"), ("b1b", "Advanced")):
            pth = os.path.join(THEME, c, lvl, "audit", "pass_with_warning_listening_list.json")
            lst = rj(pth) if os.path.exists(pth) else {"count": 0, "entries": []}
            pw.append(f"<p>{lab}・{esc(CAND_LABEL[c])}: {lst['count']}件" + ("" if not lst["count"] else " — " + " / ".join(
                esc(e.get("segment_id", "")) + "(読み方の揺れ)" for e in lst["entries"])) + "</p>")
    return "<div class='note2'><b>事後試聴の参考(読み方の揺れが検出された箇所、非ブロッキング)</b>" + "".join(pw) + "</div>"


CSS = ("<style>body{font-family:sans-serif;max-width:1100px;margin:1em auto;padding:0 1em;line-height:1.5}table{border-collapse:collapse;width:100%;margin:.5em 0 1.5em}"
       "th,td{border:1px solid #ccc;padding:6px;vertical-align:top;text-align:left}td.play{min-width:340px}audio{width:100%}.sec{color:#666;font-size:.85em}"
       ".script{background:#f6f6f6;padding:4px;margin:3px 0;font-size:.95em}.ja{background:#fffdf5;padding:4px;margin:3px 0;font-size:.9em;white-space:pre-wrap}"
       ".kp td,.kp th{border:1px solid #ccc;padding:4px 10px;width:50%}"
       ".combo{background:#eef6ff;padding:10px;border:1px solid #99c;margin-bottom:1em}.combo2{background:#f3eefc;padding:10px;border:1px solid #a9c;margin-bottom:1em}"
       ".note{background:#fff8e0;padding:8px;border:1px solid #cb8;margin-bottom:1em}.trial{background:#fde8e8;padding:10px;border:2px solid #c55;margin-bottom:1em;font-weight:bold}"
       ".note2{background:#eef9ee;padding:8px;border:1px solid #8b8;margin-bottom:1em}.tabs button{font-size:1.05em;padding:.45em 1.3em;margin:0 .5em .5em 0;cursor:pointer}"
       ".tabs button.on{background:#336;color:#fff}.hidden{display:none}.hold{background:#fff0d0;padding:8px;border:2px solid #d90;margin:6px 0}details.aux{background:#fafafa;border:1px solid #ddd;padding:6px 10px;margin:1em 0}</style>")
JS = ("<script>var C='r2',L='std';function show(){for(const s of document.querySelectorAll('section.lv')){s.classList.toggle('hidden',s.id!==C+'_'+L);}"
      "for(const b of document.querySelectorAll('.tabs button')){b.classList.toggle('on',b.dataset.k===C||b.dataset.k===L);}"
      "history.replaceState(null,'','#'+C+'_'+L);}"
      "document.querySelectorAll('.tabs button').forEach(b=>b.onclick=()=>{if(b.dataset.k==='r2'||b.dataset.k==='r0'){C=b.dataset.k}else{L=b.dataset.k}show();});"
      "(function(){const h=location.hash.slice(1).split('_');if(h.length===2&&(h[0]==='r2'||h[0]==='r0')&&(h[1]==='std'||h[1]==='adv')){C=h[0];L=h[1];}show();})();</script>")


def standard_check(built):
    """ページ標準検査(er_user_listening_page_common_01.check_page)。単一ページに候補が複数あるため、候補ごとに
    render_standard_page相当(同じrows)を生成して標準適合を検査する(出荷物のindex.html自体は候補切替UI付き)。通し音声が無いlevel(blocked)は対象外。"""
    out = {}
    for c in sorted({c for c, _ in built}):
        levels, names = [], []
        for lvl, label in (("a2", "Standard"), ("b1b", "Advanced")):
            d = built.get((c, lvl))
            if d is None or d.get("blocked"):
                continue
            levels.append({"id": label.lower(), "label": label, "full_src": f"audio/{d['full']}", "duration": d["duration"],
                           "rows": [{"part": r[0], "start": r[1], "dur": r[2], "src": f"audio/{r[3]}", "blocks": r[4]} for r in d["rows"]]})
            names.append(label)
        if not levels:
            continue
        html_text = common_page.render_standard_page(f"Family Y Trial {c}", levels)
        out[c] = common_page.check_page(html_text, base_dir=WEB, levels=tuple(names))
        out[c]["levels_checked"] = names
    return out


def main():
    os.makedirs(AUD, exist_ok=True)
    for f in glob.glob(os.path.join(AUD, "*.mp3")):
        os.remove(f)
    secs, built = [], {}
    cands = [c for c in ("r2", "r0") if os.path.isdir(os.path.join(THEME, c, "a2", "narration"))]
    for c in cands:
        for lvl in ("a2", "b1b"):
            if glob.glob(os.path.join(THEME, c, lvl, "assembled", "*.wav")):
                d = build_level(c, lvl)
            else:
                d = build_blocked_level(c, lvl)
            built[(c, lvl)] = d
            secs.append(section(c, lvl, d))
    title = "学校でスマホを禁止すべき?(Family Y・3人の声)試聴ページ"
    tabs = ("<div class='tabs'>" + "".join(f"<button data-k='{c}'>{esc(CAND_LABEL[c])}</button>" for c in cands)
            + "<br>" + "<button data-k='std'>Standard</button><button data-k='adv'>Advanced</button></div>")
    pg = (f"<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><title>{esc(title)}</title>"
          f"<meta name='viewport' content='width=device-width, initial-scale=1'>{CSS}</head><body><h1>{esc(title)}</h1>"
          "<div class='trial'>Trial(未採用): 新しい番組形式(Family Y)の試作です。正式採用は決まっていません。</div>"
          "<div class='note'>同じテーマを、暮らしも立場も違う3人がそれぞれ「私」で語る形式です。聞き分けやすさ、3人の個性、聞きたくなる面白さを確かめるための試聴ページです。"
          "上のボタンで、原稿の候補(A/B)とレベル(Standard/Advanced)を切り替えられます。</div>"
          + cards_html() + tabs + "".join(secs) + aux_html(cands) + JS + "</body></html>")
    assert "file:///" not in pg and "C:\\" not in pg and "C:/" not in pg
    with open(os.path.join(WEB, "index.html"), "w", encoding="utf-8") as f:
        f.write(pg)
    info = {f"{c}_{l}": {"rows": len(d["rows"]), "duration": round(d.get("duration", 0), 1), "blocked": bool(d.get("blocked"))} for (c, l), d in built.items()}
    print("page written", json.dumps(info))
    chk = standard_check(built)
    os.makedirs(os.path.join(THEME), exist_ok=True)
    with open(os.path.join(THEME, "page_standard_check.json"), "w", encoding="utf-8") as f:
        json.dump(chk, f, ensure_ascii=False, indent=1)
    print("standard check:", {c: v["overall"] for c, v in chk.items()})
    for c, v in chk.items():
        for k, cv in v["checks"].items():
            if not cv["ok"]:
                print("  FAIL", c, k, cv["detail"])
    return built


if __name__ == "__main__":
    main()

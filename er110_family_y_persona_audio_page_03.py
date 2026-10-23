# -*- coding: utf-8 -*-
"""FAMILY-Y-VOICES-DESIGN-01 委任_09B Trial_03: 試聴ページ生成(API 0、DEV/Trial専用)。
er110_family_y_persona_audio_page_01 の部品を再利用し、出力先を user_test/family_y_trial_03/ に、人物設定表示を世界設定整合版に差し替える。
trial_01/trial_02 のページは残置(変更しない)。入力は assemble 出力(Audio Validation Gate / Y style gate PASS)のみ。"""
from __future__ import annotations

import argparse
import glob
import json
import os

import er110_family_y_persona_audio_page_01 as pg1
import er110_family_y_persona_trial03_01 as t3

ROOT = os.path.dirname(os.path.abspath(__file__))
pg1.WEB = os.path.join(ROOT, "user_test", "family_y_trial_03")
pg1.AUD = os.path.join(pg1.WEB, "audio")
esc = pg1.esc


def _style_gate_held(it, level):
    """組立前のY style gateでBLOCKされたsegment(例: ASR合格でも代替指示[fallback]で生成されたもの)。HR Lockとは別の保留。"""
    gp = os.path.join(pg1.y.theme_dir(it), level, "audit", "y_style_profile_gate.json")
    if not os.path.exists(gp):
        return set()
    g = pg1.rj(gp)
    return {b["segment"] for b in (g.get("y_body_blocked") or []) + (g.get("x_gate_blocked_after_filter") or [])}


def build_blocked_level_03(it, level):
    """pg1.build_blocked_level の派生: HR Lock(人間確認待ち)に加え、style gate保留のsegmentも明示する。全編通し音声は作らない(Gateを回避しない)。"""
    y, rj, sf = pg1.y, pg1.rj, pg1.sf
    theme = y.theme_dir(it)
    base = os.path.join(theme, level)
    nd = os.path.join(base, "narration")
    parts = rj(os.path.join(base, "parts.json"))
    rls_path = os.path.join(base, "audit", "review_lock_state.json")
    rls = rj(rls_path) if os.path.exists(rls_path) else {}
    support = rj(os.path.join(base, "a2_support_texts.json" if level == "a2" else "b1_support_texts.json"))
    ja = pg1._ja_paras(it)
    hd = rj(os.path.join(y.TEXT_ROOT, it, "headings", "headings.json"))["headings"]
    tag = "adv" if level == "b1b" else "std"
    held = {n for n, e in rls.items() if e.get("final_status") != "OK"}
    gate_held = _style_gate_held(it, level) - held
    plan = [("Preview", "preview", pg1._script(support["preview"])), ("Comment 1", "comment_1", pg1._script(support["comment_1"])),
            ("Comment 2", "comment_2", pg1._script(support["comment_2"]))]
    for i in range(3):
        plan.append((f"見出し{i + 1}(ナレーター)", y.HEADING_IDS[i], pg1._script(hd[i]["spoken_en"])))
        plan.append(("S", y.Y_BODY_IDS[i], None))
    plan += [("S", y.Y_BODY_IDS[3], None), ("In One Line", "in_one_line", pg1._script(parts["in_one_line"]))]
    rows = []
    for label, seg, blk in plan:
        w = os.path.join(nd, f"{seg}.wav")
        if not os.path.exists(w):
            rows.append((label + "【未生成】", 0.0, 0.0, None, [blk or ""], None))
            continue
        x, sr = sf.read(w, dtype="float32")
        fn = f"{tag}_part_{len(rows):02d}.mp3"
        pg1.mp3(x, sr, os.path.join(pg1.AUD, fn))
        blocks = []
        if label == "S":
            n = y.Y_BODY_IDS.index(seg) + 1
            label = f"Full Story Part {n} — {pg1.PERSON[seg]}"
            blocks.append(pg1._script(parts[f"part{n}"]))
            blocks.append("<details><summary>日本語の元原稿</summary><div class='ja'>" + pg1.esc(ja[n - 1]) + "</div></details>")
        else:
            blocks.append(blk)
        if seg in held:
            label += "【人間確認待ちのテイク】"
            blocks.insert(0, "<div class='hold'>このパート(人物1)は、言い換えた原稿で3回まで作り直しましたが、自動検査を通過できませんでした"
                             "(1・2回目=繰り返し検出の境界値、3回目=代替指示での生成で2つ目の文字起こし照合が1語の差を指摘)。検査は迂回していません。"
                             "聴いて問題がなければ人間の承認が必要です(承認されると全編通し音声を組み立てられます)。ここで聴けるのは最後のテイクです。</div>")
        elif seg in gate_held:
            label += "【組立前の検査で保留のテイク】"
            blocks.insert(0, "<div class='hold'>このパートは文字起こし照合と繰り返し検出には合格しましたが、声の調子の指定が標準と異なる代替の指示で生成されたため、"
                             "正式な組立前の検査で保留になっています(検査は迂回していません)。聴いて問題がなければ承認が必要です。</div>")
        rows.append((label, 0.0, sf.info(w).duration, fn, blocks, None))
    # Key Phrase(委任_10: 途中経過版では未掲載だった。確定済みclipをパート別に掲載)
    res = pg1.rj(os.path.join(base, "audit", "tts_generation_results.json"))
    kp_items = sorted(pg1.rj(os.path.join(base, "key_phrases", "keywords_canonicalized.json"))["items"], key=lambda i_: i_["rank"])
    expl = res.get("key_phrase_explanations_text") or {}
    second = "kp{r}_explanation_en.wav" if level == "b1b" else "meaning_{r}.wav"
    for r in (1, 2, 3):
        for kind, wn in (("英語", f"kp{r}_en.wav"), ("解説" if level == "b1b" else "日本語の意味", second.format(r=r))):
            w = os.path.join(nd, wn)
            if not os.path.exists(w):
                continue
            x, sr = sf.read(w, dtype="float32")
            fn = f"{tag}_part_{len(rows):02d}.mp3"
            pg1.mp3(x, sr, os.path.join(pg1.AUD, fn))
            blocks = [pg1._kp_html(level, kp_items[r - 1]["rank"], kp_items[r - 1], res, expl)] if kind == "英語" else []
            rows.append((f"Key Phrase {r} ({kind})", 0.0, sf.info(w).duration, fn, blocks, None))
    return {"blocked": True, "rows": rows, "parts": parts, "tag": tag, "held": sorted(held | gate_held), "missing": [r[0] for r in rows if r[3] is None]}


def section_03(level, d):
    """blockedレベルの見出し・説明を委任_10の状況に合わせる(通常レベルはpg1.section)。"""
    if not d.get("blocked"):
        return pg1.section(level, d)
    lab = "Advanced" if level == "b1b" else "Standard"
    return (f"<section id='{d['tag']}' class='lv hidden'><h2>{lab}(通し再生なし: 人物1のパートが人間確認待ち)</h2>"
            "<div class='hold'><b>このレベルは全編通し音声をまだ作れていません。</b>人物1の語りが自動検査を通過できないため、人間が聴いて承認するまで組み立てません。"
            "それまでは、パートごとの音声とKey Phraseだけ確認できます。</div>"
            f"<div class='note'><b>In One Line</b>: {esc(d['parts']['in_one_line'])}</div>"
            "<details open><summary>パート別再生・全スクリプト・Key Phrase</summary>" + pg1.rows_html(d["rows"]) + "</details></section>")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--it", default="it3")
    a = ap.parse_args()
    pg1.build_blocked_level = build_blocked_level_03
    t3.apply_overrides()          # process内の差替え(COMMON_PREMISE_JA / SHEETS)。ファイルは変更しない
    y, p = pg1.y, pg1.p
    os.makedirs(pg1.AUD, exist_ok=True)
    for f in glob.glob(os.path.join(pg1.AUD, "*.mp3")):
        os.remove(f)
    built, secs = {}, []
    for lvl in ("a2", "b1b"):
        d = pg1.build_level(a.it, lvl) if glob.glob(os.path.join(y.theme_dir(a.it), lvl, "assembled", "*.wav")) else pg1.build_blocked_level(a.it, lvl)
        built[lvl] = d
        secs.append(section_03(lvl, d))
    title = "休み時間もスマホを使わない学校?(Family Y・3人の声・第3回Trial)試聴ページ"
    tabs = "<div class='tabs'><button data-k='std'>Standard</button><button data-k='adv'>Advanced</button></div>"
    prev = ("<div class='note'><b>前回までのTrialとの違い</b>: 第2回(<a href='../family_y_trial_02/index.html'>こちら</a>)の「朝に全員から預かり、下校時に返す」ルールは、"
            "日本の高校の実情に合わないため見直しました。今回は日本の高校を例に、「今は授業中だけ使えない。休み時間や昼休みも含めて、学校にいる間は使わないことにするか」を"
            "3人が自分の暮らしから語ります。語りは、人物の語りが好評だった初回稿をもとに、ルールの言い方と不自然な文だけを直したものです。"
            "第1回は<a href='../family_y_trial_01/index.html'>こちら</a>。</div>")
    pg = (f"<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><title>{esc(title)}</title>"
          f"<meta name='viewport' content='width=device-width, initial-scale=1'>{pg1.CSS}</head><body><h1>{esc(title)}</h1>"
          "<div class='trial'>Trial(未採用): 新しい番組形式(Family Y)の試作です。正式採用は決まっていません。登場する3人は架空の人物です。</div>"
          + ("<div class='hold'><b>Advanced は全編通し再生できます。Standard は人物1の語りが自動検査を通過できず保留のため、通し再生がまだありません</b>"
             "(パート別の音声とKey Phraseは聴けます。保留のパートは下に表示)。</div>"
             if any(d.get("blocked") for d in built.values()) else "")
          + "<div class='note'>同じテーマを、暮らしも立場も違う3人がそれぞれ自分の言葉で語る形式です。人物の実在感、主張の分かりやすさ、3人の聞き分けやすさ、"
          "最後のまとめが耳で分かるか、日本の高校の話として自然かを確かめるための試聴ページです。上のボタンでレベル(Standard/Advanced)を切り替えられます。</div>"
          + prev + pg1.personas_html() + tabs + "".join(secs) + pg1.JS + "</body></html>")
    assert "file:///" not in pg and "C:\\" not in pg and "C:/" not in pg
    with open(os.path.join(pg1.WEB, "index.html"), "w", encoding="utf-8") as f:
        f.write(pg)
    info = {l: {"rows": len(d["rows"]), "duration": round(d.get("duration", 0), 1), "blocked": bool(d.get("blocked"))} for l, d in built.items()}
    print("page written", json.dumps(info))
    chk = pg1.standard_check(built)
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

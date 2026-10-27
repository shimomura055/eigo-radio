# -*- coding: utf-8 -*-
"""FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02 委任_01: 「中東情勢(イエメン・サウジ周辺)」正式E2E(run_mey_02)試聴ページ生成(有料APIなし)。
er071_coffee_m2p0_n01_page_04.py派生(既存Family X試聴ページ方式)。出力: user_test/middle_east_yemen_saudi_e2e_02/{index.html, audio/*.mp3}
Production runner --stage assemble の正式出力(Audio Validation Gate / M3 PASS)のみを入力にする。file:/// を含めない。"""
from __future__ import annotations
import er019_x_page_guard_01  # noqa: F401  SLOT-23 委任_04C: display_spec付き(新表示仕様)のrunならSTOP(旧per-article scriptは遡及なし。新規記事は er019_family_x_listening_page_01.py)
import html, json, os, re, subprocess
import imageio_ffmpeg
import soundfile as sf

ROOT = os.path.dirname(os.path.abspath(__file__))
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
esc = html.escape
RUN = os.path.join(ROOT, "er019_output", "family_x_audio_production_wiring_01", "middle_east_yemen_saudi__run_mey_02")
WEB = os.path.join(ROOT, "user_test", "middle_east_yemen_saudi_e2e_02")
AUD = os.path.join(WEB, "audio")


def rj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def mp3(x, sr, out, br="96k"):
    tmp = out + ".tmp.wav"
    sf.write(tmp, x, sr)
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", tmp, "-codec:a", "libmp3lame", "-b:a", br, out], check=True)
    os.remove(tmp)


def seg_html(res, parts, part, kp_items, kp_expl, level):
    pl = part.lower()
    segs = res["segments"]

    def style(s):
        sp = (segs.get(s) or {}).get("style_profile") or {}
        if not sp:
            return "(Style profile対象外ロール)"
        return f"{sp.get('role')} / {sp.get('profile_id')} / base_sha {str(sp.get('style_base_sha256'))[:12]}"

    m = re.match(r"full story part (\d)", pl)
    if m:
        n = m.group(1)
        return "<div class='script'>" + esc(parts["part" + n]).replace("\n", "<br>") + "</div><div class='sec'>" + esc(style("full_story_part" + n)) + "</div>"
    m = re.match(r"comment (\d)", pl)
    if m:
        s = "comment_" + m.group(1)
        txt = segs[s].get("text")
        note = style(s)
        if not txt:  # HR承認済みsegment(結果entryはSTOPPED/HUMAN_REVIEW_LOCKEDでtext無し)は台本ファイルから取得
            txt = rj(os.path.join(RUN, level, ("a2_support_texts.json" if level == "a2" else "b1_support_texts.json")))[s]
            note = "ユーザーHuman Review承認済み(2026-10-21、REGISTER #128)。音声=canonical comment_2.wav(attempt3)"
        return "<div class='script'>" + esc(txt) + "</div><div class='sec'>" + esc(note) + "</div>"
    if pl.startswith("preview (") or pl == "preview":
        return "<div class='script'>" + esc(segs["preview"]["text"]) + "</div><div class='sec'>" + esc(style("preview")) + "</div>"
    if pl.startswith("topic intro"):
        return "<div class='script'>" + esc(segs["topic_intro"]["text"]) + "</div>"
    if pl.startswith("japanese title"):
        return "<div class='script'>" + esc(segs["japanese_title"]["text"]) + "</div>"
    if pl.startswith("in one line"):
        return "<div class='script'>" + esc(parts["in_one_line"]) + "</div><div class='sec'>" + esc(style("in_one_line")) + "</div>"
    m = re.match(r"key phrase (\d)$", pl)
    if m:
        n = m.group(1)
        it = kp_items[int(n) - 1]
        k = res["key_phrases"][n]
        e = k["english"]
        sp = e.get("style_profile") or {}
        base = f"KP英語: {sp.get('role')} base_sha {str(sp.get('style_base_sha256'))[:12]} fallback_used={e.get('fallback_used')} reused={e.get('reused')}"
        if level == "a2":
            jsp = (k["japanese_meaning"].get("style_profile") or {})
            head = "<table class='kp'><tr><th>英語KP(K2)</th><th>日本語意味(P8-KP)</th></tr>"
            cell = str(it.get("japanese_gloss_tts"))
            tail = f"{base} / 日本語意味: {jsp.get('role')} base_sha {str(jsp.get('style_base_sha256'))[:12]}"
        else:
            xsp = (k["explanation"].get("style_profile") or {})
            head = "<table class='kp'><tr><th>英語KP(K2)</th><th>英語解説(P7)</th></tr>"
            cell = kp_expl["items"][n]["english_explanation"]
            tail = f"{base} / 英語解説: {xsp.get('role')} base_sha {str(xsp.get('style_base_sha256'))[:12]}"
        return head + f"<tr><td>{esc(it['used_form'])}</td><td>{esc(cell)}</td></tr></table><div class='sec'>{esc(tail)}</div>"
    return ""


def level_block(level_key, d, label, assembled_name):
    base = os.path.join(RUN, d)
    x, sr = sf.read(os.path.join(base, "assembled", assembled_name), dtype="float32")
    full = f"MEY_{label}_e2e_02.mp3"
    mp3(x, sr, os.path.join(AUD, full), br="128k")
    tl = rj(os.path.join(base, "audit", "timeline.json"))
    parts = rj(os.path.join(base, "parts.json"))
    res = rj(os.path.join(base, "audit", "tts_generation_results.json"))
    kp_items = sorted(rj(os.path.join(base, "key_phrases", "keywords_canonicalized.json"))["items"], key=lambda it: it["rank"])
    kp_expl = res.get("key_phrase_explanations_text") or {}
    rows = []
    for e in tl:
        part = e["part"]
        if part.startswith("pause"):
            continue
        s, dur = e["start_seconds"], e["duration_seconds"]
        fn = f"{level_key}_{len(rows):02d}.mp3"
        mp3(x[int(round(s * sr)): int(round((s + dur) * sr))], sr, os.path.join(AUD, fn))
        rows.append((part, s, dur, fn, seg_html(res, parts, part, kp_items, kp_expl, d)))
    return full, x.shape[0] / sr, rows


def table(rows):
    return ("<table><thead><tr><th>パート</th><th>音声</th><th>Script / Key Phrase / Style</th></tr></thead><tbody>"
            + "".join(f"<tr><td><b>{esc(p)}</b><br><span class='sec'>{s:.1f}秒〜 ({d:.1f}秒)</span></td><td class='play'>"
                      f"<audio controls preload='none' src='audio/{fn}'></audio></td><td>{b}</td></tr>" for p, s, d, fn, b in rows)
            + "</tbody></table>")


def main():
    global RUN, WEB, AUD
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("--run-dir"); ap.add_argument("--audio-dir"); ap.add_argument("--out"); a = ap.parse_args()
    RUN = os.path.abspath(a.audio_dir); WEB = os.path.abspath(a.out); AUD = os.path.join(WEB, "audio")
    os.makedirs(AUD, exist_ok=True)
    adv_full, adv_dur, adv_rows = level_block("adv", "b1b", "Advanced", "Family_X_Audio_B1_MIDDLE_EAST_YEMEN_SAUDI.wav")
    std_full, std_dur, std_rows = level_block("std", "a2", "Standard", "Family_X_Audio_A2_MIDDLE_EAST_YEMEN_SAUDI.wav")
    pa = rj(os.path.join(RUN, "a2", "parts.json")); pb = rj(os.path.join(RUN, "b1b", "parts.json"))
    kpl = []
    for lv, lab in (("a2", "Standard"), ("b1b", "Advanced")):
        its = sorted(rj(os.path.join(RUN, lv, "key_phrases", "keywords_canonicalized.json"))["items"], key=lambda it: it["rank"])
        kpl.append(f"<li>{lab}: " + " / ".join(esc(i["used_form"]) for i in its) + "</li>")
    meta = (f"<div class='note'><b>タイトル</b>: {esc(pb.get('title') or '')}<br><b>In one line (Adv)</b>: {esc(pb['in_one_line'])}<br>"
            f"<b>In one line (Std)</b>: {esc(pa['in_one_line'])}<br><b>Key Phrases</b><ul>{''.join(kpl)}</ul>"
            "費用・Style適用表: <code>audit/cost_by_stage_e2e_02.json</code> / <code>audit/e2e_segment_style_table_mey_02.json</code>(リポジトリ内)。"
            "確認項目: 攻撃主体(フーシ派)が「サウジ主導連合軍報道官の発表」として帰属付きで述べられているか。<br>"
            "<b>Standard Comment 2</b>: ASR(自動判定)では「タイフーン機」を「台風機/台風期」と認識したためHuman Review対象でしたが、ユーザーが実際に試聴して正しく発音されていることを確認し、2026-10-21に承認(PASS)済みです(REGISTER #128)。"
            "試聴に使った3テイク比較ページ: <a href='hr_comment_2/index.html'>hr_comment_2/index.html</a>(採用はStandard通し音声内のcanonical take=attempt3)。</div>")
    css = ("<style>body{font-family:sans-serif;max-width:1100px;margin:1em auto;padding:0 1em;line-height:1.5}table{border-collapse:collapse;width:100%;margin-bottom:1.5em}"
           "th,td{border:1px solid #ccc;padding:6px;vertical-align:top;text-align:left}td.play{min-width:340px}td.play audio,audio{width:100%}.sec{color:#666;font-size:.85em}"
           ".script{background:#f6f6f6;padding:4px;margin:3px 0;font-size:.95em}.kp td,.kp th{border:1px solid #ccc;padding:4px 10px;width:50%}"
           ".combo{background:#eef6ff;padding:10px;border:1px solid #99c;margin-bottom:1em}.note{background:#fff8e0;padding:8px;border:1px solid #cb8;margin-bottom:1em}</style>")
    pw = []
    for lvl, lab in (("b1b", "Advanced"), ("a2", "Standard")):
        lst = rj(os.path.join(RUN, lvl, "audit", "pass_with_warning_listening_list.json")) if os.path.exists(os.path.join(RUN, lvl, "audit", "pass_with_warning_listening_list.json")) else {"count": 0, "entries": []}
        pw.append(f"<h3>{lab}: PASS_WITH_WARNING {lst['count']}件</h3><ul>" + "".join(
            f"<li>{esc(e['segment_id'])} / 期待={esc(e['canonical_text'])} / 一次ASR={esc(str(e.get('primary_text')))} / "
            f"二次ASR={esc(str(e.get('secondary_text')))} / {esc(','.join(e['warning_labels']))}</li>" for e in lst["entries"]) + "</ul>")
    disc = ("<div class='note'><b>「中東情勢(イエメン・サウジ周辺)」正式E2E-02 試聴(run_mey_02)</b>: Production runner <code>--stage assemble</code> の正式出力"
            "(Audio Validation Gate・M3 Style Gateを通過)です。既定profile <code>fx_20261017</code>"
            "(Full Story=PD06 / KP英語=K2 / Std KP日本語意味=P8 / Adv KP英語解説=P7 / Adv Preview=E1 / Std Preview・Comment=R2)。"
            "各行の下に、その区間のStyle role・Prompt base sha(先頭12桁)を併記しています。試聴評価はユーザーが行います(自動PASSではありません)。"
            "試聴確認の観点: Std Full Storyの体感速度(PD06+6%減速)、Adv Full Story速度、KP英語(K2)の語頭語尾、Std KP日本語意味、Adv KP英語解説。</div>")
    pg = (f"<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><title>「中東情勢」正式E2E-02 試聴(mey_e2e_02)</title>"
          f"<meta name='viewport' content='width=device-width, initial-scale=1'>{css}</head><body>"
          f"<h1>「中東情勢(イエメン・サウジ周辺)」正式E2E-02 試聴(Standard / Advanced)</h1>{disc}{meta}"
          f"<h2 id='std'>Standard(通し全編 {std_dur:.0f}秒)</h2><div class='combo'><audio id='main_std' controls preload='none' src='audio/{std_full}'></audio></div>"
          + table(std_rows)
          + f"<h2 id='adv'>Advanced(通し全編 {adv_dur:.0f}秒)</h2><div class='combo'><audio id='main_adv' controls preload='none' src='audio/{adv_full}'></audio></div>"
          + table(adv_rows)
          + "<h2 id='pww'>事後試聴リスト(PASS_WITH_WARNING、非ブロッキング)</h2>" + "".join(pw) + "</body></html>")
    assert "file:///" not in pg and "C:\\" not in pg and "C:/" not in pg
    with open(os.path.join(WEB, "index.html"), "w", encoding="utf-8") as f:
        f.write(pg)
    print("page written", len(std_rows), len(adv_rows), round(std_dur, 2), round(adv_dur, 2))


if __name__ == "__main__":
    main()

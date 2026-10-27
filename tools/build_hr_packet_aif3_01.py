# -*- coding: utf-8 -*-
"""AI-ISLAND-FORM-PRODUCTION-01 委任_03: Style Gate(M3: LOCAL_REWRITE_RECOVERY)が止めたsegmentのHRパケット(新形式)生成。API 0。
形式: 原稿 / ASR全文 / 相違点 / NG理由 / 推奨音声(1つ) / AI評価 / 質問(1つ)。出力: user_test/family_x_ai_island_form_01/{hr_01.html, hr/*.mp3}
使い方: .venv\\Scripts\\python.exe tools/build_hr_packet_aif3_01.py"""
from __future__ import annotations

import difflib
import html
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
import imageio_ffmpeg  # noqa: E402

esc = html.escape
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
RUN = "er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01"
WEB = "user_test/family_x_ai_island_form_01"
SEG = "full_story_part1_k2"


def rj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def words(t):
    t = t.replace("“", "").replace("”", "")   # 引用符は読み上げに影響しない(差分から除外)
    return re.findall(r"[A-Za-z0-9’']+|[^\sA-Za-z0-9’']", t)


def diff_rows(a, b):
    wa, wb = words(a), words(b)
    out = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, [w.lower() for w in wa], [w.lower() for w in wb]).get_opcodes():
        if tag != "equal":
            out.append((tag, " ".join(wa[i1:i2]) or "(なし)", " ".join(wb[j1:j2]) or "(なし)"))
    return out


def mark(a, b):
    """aを基準に、bとの差分箇所を<mark>で強調したHTML(a側)。"""
    wa, wb = words(a), words(b)
    res = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, [w.lower() for w in wa], [w.lower() for w in wb]).get_opcodes():
        seg = " ".join(wa[i1:i2])
        res.append(esc(seg) if tag == "equal" else f"<mark>{esc(seg or '∅')}</mark>")
    return " ".join(res)


def mp3(wav, out):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", wav, "-codec:a", "libmp3lame", "-b:a", "96k", out], check=True)


def section(level, lab, ev_note):
    r = rj(f"{RUN}/{level}/audit/tts_generation_results.json")["segments"][SEG]
    lr = r["local_rewrite_recovery"]
    canon = r["canonical_text"]
    spoken = r["text"]
    prim = ((r.get("post_slowdown_asr_text") if level == "a2" else r.get("asr_text")) or "")
    asr_j = r.get("asr_judgement") or {}
    sec = (asr_j.get("secondary") or {}).get("text")
    wav = r["path"]
    fn = f"hr/{'std' if level == 'a2' else 'adv'}_{SEG}.mp3"
    mp3(wav, os.path.join(WEB, fn))
    chosen = (lr.get("selection") or {}).get("selected") or {}
    ng = lr.get("ng_span") or {}
    import soundfile as sf
    _i = sf.info(wav)
    dur = _i.frames / _i.samplerate
    h = [f"<h2 id='{level}'>{lab}: Full Story 第1部の2段落目(1 segment)</h2>"]
    h.append("<h3>1. 原稿(承認済み本文)</h3><div class='script'>" + mark(canon, spoken) + "</div>")
    h.append("<h3>2. 実際に読まれた文(自動書き換え後。音声認識の全文)</h3>")
    h.append("<ul><li>読ませた文(書き換え後): <div class='script'>" + mark(spoken, canon) + "</div></li>")
    h.append("<li>音声認識(OpenAI・一次): <div class='script'>" + esc(prim) + "</div></li>")
    if sec:
        h.append("<li>音声認識(Azure・二次): <div class='script'>" + esc(sec) + "</div></li>")
    h.append("</ul>")
    h.append("<h3>3. 相違点(原稿 → 読ませた文)</h3><ul>" + "".join(
        f"<li>{esc(t)}: 原稿 <code>{esc(x)}</code> / 実際 <code>{esc(y)}</code></li>" for t, x, y in diff_rows(canon, spoken)) + "</ul>")
    h.append("<h3>4. 自動検査が止めた理由</h3>" + ev_note)
    h.append("<h3>5. 推奨音声(1つ)</h3><audio controls preload='none' src='" + fn + "'></audio>"
             f"<p class='sec'>この段落のみ(約{(dur if dur else 0):.1f}秒)。書き換え案{esc(str(chosen.get('id')))}「{esc(chosen.get('changed_span_after') or '')}」を使った音声です。</p>")
    return "".join(h), {"level": level, "canon": canon, "spoken": spoken, "asr_primary": prim, "asr_secondary": sec, "ng_span": ng, "audio": fn,
                        "selected_candidate": chosen.get("id"), "changed_after": chosen.get("changed_span_after"), "duration": dur}


def main():
    std_note = ("<p>原稿の <code>The AIs sent to the …</code> の <code>AIs</code>(複数形)が、音声認識では <code>AI</code>(単数)になりました。"
                "標準の指示で2回、代替指示(fallback)で1回、計3回生成しましたが、生成直後の検査は(二次ASRの確認で)通ったものの、6%減速の後処理をした後の再検証が3回とも同じ位置(<code>AIs</code>→<code>AI</code>)で不一致(<code>ASR_VALIDATION_UNCERTAIN</code>)でした。"
                "そこで、承認済みの自動書き換え規則に従って <code>AIs</code> を <code>AI agents</code> に言い換えた文で再生成し、減速後の再検証も(二次ASR確認で)通っています。"
                "ただし「本文と違う語で読んでいる音声(自動書き換え)」と「承認済みの話し方(Style)ではない代替指示(fallback)を使った生成履歴」という2点が、人の承認なしでは組み立てを進めない承認済みの安全規則"
                "(M3 Style Gate: <code>LOCAL_REWRITE_RECOVERY</code> / <code>STD_FALLBACK_USED_OR_UNKNOWN</code>)に該当するため停止しています。数値・否定・固有名詞の変化はありません。</p>")
    adv_note = ("<p>原稿の <code>The AIs sent to the …</code> の <code>AIs</code>(複数形)を、音声認識が <code>AI</code>(単数)と書き起こしました(標準指示2回＋代替指示1回、計3回とも同じ位置)。"
                "規則に従って <code>AIs</code> を <code>AI systems</code> に言い換えた文で再生成し、一次・二次とも通過しています。"
                "ただし「本文と違う語で読んでいる音声（自動書き換え）」が、人の承認なしでは組み立てを進めない安全規則(M3 Style Gate: <code>LOCAL_REWRITE_RECOVERY</code>)に該当するため停止しています。"
                "数値・否定・固有名詞の変化はありません。</p>")
    s1, d1 = section("a2", "Standard", std_note)
    s2, d2 = section("b1b", "Advanced", adv_note)
    ai_eval = (
        "<h3>6. AIの評価</h3>"
        "<p>結論: 意味・事実は変わっていません。語の差は「<code>AIs</code>」を「<code>AI agents</code>(Standard)／<code>AI systems</code>(Advanced)」と言い換えた1箇所だけ(引用符の有無は読み上げに影響しません)で、"
        "残りの文は原稿と完全に同じ内容で読まれています。ただしAI自身は音声を聞けないため、聞いて問題ないかの最終確認は耳でお願いします。</p>"
        "<p>根拠(1) 同じ「AIs」は、Standard・Advancedとも3回の生成すべてで同じ位置が不合格になっており、試行の運ではなく読み上げ上の癖(複数形のsが聞き取れない)と判断しました。"
        "同じ段落の他の文・他の段落(第1部の1・3段落目、第2・第3部)は問題なく通過しています。</p>"
        "<p>根拠(2) 言い換え案は、意味保存・役割保存・事実非矛盾などをAIが検査し、自動書き換えの承認済み規則の範囲で選ばれています(Standardは案1「AI agents」、Advancedは案2「AI systems」)。"
        "他の案「bots」は「AIsより意味が狭い」として不合格でした。</p>"
        "<p>注意点: ページ上の原稿表示は承認済み本文のまま(「AIs」)で、この1箇所だけ音声は「AI agents」「AI systems」と読まれます。"
        "本文自体の変更は行っていません(本文変更はユーザー承認事項のため)。</p>")
    q = ("<h3>7. 質問(1つ)</h3><p><b>上の2つの音声(StandardとAdvanced)は、それぞれ「AIs」を言い換えて読んでいます。この音声でよいですか?</b></p>"
         "<p class='sec'>回答の例: 「両方OK」／「Standardのみ不可(理由)」／「Advancedのみ不可(理由)」。承認された場合のみ、その1 segmentに限って承認を記録し、残りの組立と公開を進めます。</p>")
    page = ("<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><title>AIの仮想の島 Human Review(2 segment)</title>"
            "<meta name='viewport' content='width=device-width, initial-scale=1'><style>body{font-family:sans-serif;max-width:900px;margin:1em auto;padding:0 1em;line-height:1.6}"
            ".script{background:#f6f6f6;padding:6px;margin:4px 0}mark{background:#ffd54f}.sec{color:#666;font-size:.9em}audio{width:100%}h2{border-top:3px solid #336;padding-top:.6em}</style></head><body>"
            "<h1>AIの仮想の島: Human Review(2 segment)</h1>"
            "<p>状態: 完成版の組立前に、承認済みの安全規則によって2 segmentが停止しています。最終の試聴ページではありません。</p>"
            + s1 + s2 + ai_eval + q + "</body></html>")
    assert "file:///" not in page and "C:\\" not in page
    with open(os.path.join(WEB, "hr_01.html"), "w", encoding="utf-8") as f:
        f.write(page)
    with open(os.path.join(RUN, "audit", "hr_packet_data_01.json"), "w", encoding="utf-8") as f:
        json.dump([d1, d2], f, ensure_ascii=False, indent=2)
    print("wrote", os.path.join(WEB, "hr_01.html"), d1["duration"], d2["duration"])


if __name__ == "__main__":
    main()

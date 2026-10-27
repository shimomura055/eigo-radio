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


# ============================================================
# 委任_05(AIF5): hr_02(ユーザー指定8項目セット。真因を先に説明)。API 0。使い方: tools/build_hr_packet_aif3_01.py --v2
# ============================================================
def build_v2():
    std = rj(f"{RUN}/a2/audit/tts_generation_results.json")["segments"][SEG]
    adv = rj(f"{RUN}/b1b/audit/tts_generation_results.json")["segments"][SEG]
    # 提示音声はhr_01で書き出し済みのmp3(同一wav由来)を再利用する。
    hr1 = rj(os.path.join(RUN, "audit", "hr_packet_data_01.json"))
    for fn in ("hr/std_full_story_part1_k2.mp3", "hr/adv_full_story_part1_k2.mp3"):
        assert os.path.exists(os.path.join(WEB, fn)) and any(x["audio"] == fn for x in hr1), fn
    s_post = std["post_slowdown_asr_text"]
    s_sec = std["post_slowdown_cascade"]["steps"][1]["text"]
    a_prim = adv["asr_text"]
    css = ("body{font-family:sans-serif;max-width:920px;margin:1em auto;padding:0 1em;line-height:1.65}.script{background:#f6f6f6;padding:6px;margin:4px 0}"
           "mark{background:#ffd54f}.sec{color:#555;font-size:.92em}audio{width:100%}h2{border-top:3px solid #336;padding-top:.6em}"
           "table{border-collapse:collapse;font-size:.92em}td,th{border:1px solid #bbb;padding:3px 6px}.box{border:2px solid #336;padding:6px 12px;background:#eef}")

    def lvl(label, r, fn, tries_html, rewrite_after, extra_diff):
        canon, spoken = r["canonical_text"], r["text"]
        h = [f"<h2>{label}: Full Story 第1部の2段落目(1 segment)</h2>"]
        h.append("<h3>1. 該当する元原稿(ユーザー確認済み本文のまま)</h3>"
                 f"<div class='script'>{esc(canon)}</div>"
                 "<p class='sec'>場所=Full Story 第1部(full_story_part1_k2・2段落目、Role=FULL_STORY)。article.mdは確認済み版と一致(本文SHA一致)。本文は一切変更していません。</p>")
        h.append("<h3>2. 書換え前後の英文(音声に読ませた文だけが変わっています)</h3>"
                 f"<ul><li>変更前(本文=原稿): <div class='script'>{mark(canon, spoken)}</div></li>"
                 f"<li>変更後(音声で読んだ文): <div class='script'>{mark(spoken, canon)}</div></li></ul>"
                 f"<p class='sec'>変更は1語句のみ:「AIs」→「{esc(rewrite_after)}」。数値・否定・固有名詞は無変更。</p>")
        h.append("<h3>3. 推奨音声(1件)</h3>"
                 f"<audio controls preload='none' src='{fn}'></audio><p class='sec'>この段落のみ(約{[x['duration'] for x in hr1 if x['audio'] == fn][0]:.1f}秒)。「{esc(rewrite_after)}」と読む音声です。</p>")
        h.append("<h3>4. 音声認識(ASR)の結果と具体的な不一致箇所</h3>" + tries_html + extra_diff)
        return "".join(h)

    std_tries = ("<p><b>元原稿「The AIs sent…」で音声を作り直した履歴(標準2回＋代替指示1回=3回)</b></p><table><tr><th>回</th><th>生成直後 OpenAI(一次)</th><th>生成直後 Azure(二次)</th><th>6%減速後 OpenAI</th><th>6%減速後 Azure</th></tr>"
                 "<tr><td>1</td><td>The <b>AI</b> sent…</td><td>The <b>AIS</b> sent…(救済で通過)</td><td>The <b>AI</b> sent…</td><td>The <b>AI</b> sent…(不一致)</td></tr>"
                 "<tr><td>2</td><td>The <b>AIs</b> sent…(通過)</td><td>不要</td><td>The <b>AI</b> sent…</td><td>The <b>AI</b> sent…(不一致)</td></tr>"
                 "<tr><td>3(代替指示)</td><td>The <b>AI</b> sent…</td><td>The <b>AIS</b> sent…(救済で通過)</td><td>The <b>AI</b> sent…</td><td>The <b>AI</b> sent…(不一致)</td></tr></table>"
                 "<p class='sec'>Standardは音声を6%ゆっくりにする承認済み処理があり、その後の再検証が3回とも「AIs→AI」で不一致でした。</p>"
                 f"<p><b>採用した音声(AI agents版)の認識:</b></p><ul><li>OpenAI(一次): <div class='script'>{esc(s_post)}</div></li><li>Azure(二次): <div class='script'>{esc(s_sec)}</div></li></ul>")
    std_diff = ("<p><b>不一致箇所(採用音声):</b> OpenAIは「rewards」を「awards」と認識(1語)。Azureは「rewards」を正しく認識し、二次確認として承認済み規則で通過しています(数値・否定の変化なし)。"
                "「AI agents」と読ませた箇所自体は両エンジンとも認識できています。</p>")
    adv_tries = ("<p><b>元原稿「The AIs sent…」で音声を作り直した履歴(標準2回＋代替指示1回=3回、Advancedは減速なし)</b></p><table><tr><th>回</th><th>OpenAI(一次)</th><th>Azure(二次)</th></tr>"
                 + "".join(f"<tr><td>{i + 1}{'(代替指示)' if i == 2 else ''}</td><td>The <b>AI</b> sent…</td><td>The <b>AI</b> sent…(不一致)</td></tr>" for i in range(3)) + "</table>"
                 f"<p><b>採用した音声(AI systems版)の認識:</b></p><ul><li>OpenAI(一次): <div class='script'>{esc(a_prim)}</div></li><li>Azure(二次): 一次が承認済み規則で通過したため追加の呼び出しなし</li></ul>")
    adv_diff = ("<p><b>不一致箇所(採用音声):</b> 「settings」→「setting」(複数形のsが1箇所落ちただけ。承認済みの複数形救済[Azure裏付けあり]で通過)。「AI systems」と読ませた箇所は認識できています。</p>")

    top = ("<div class='box'><p><b>先に結論(なぜ今Human Reviewなのか)</b></p><ul>"
           "<li><b>原稿の変更は本文にはありません。</b>変更したのは「音声に読ませる文」だけで、この1段落の主語「The AIs sent to the island…」の「AIs」を、Standardは「AI agents」、Advancedは「AI systems」に言い換えています。"
           "ページの本文は確認済みのまま「AIs」です(本文に「AI systems」が見当たらないのは当然で、Advanced末尾の「AI agents」は別の文の本文です)。</li>"
           "<li><b>起きたこと:</b> 「The AIs sent」の「AIs」を、音声認識(OpenAI・Azure)が毎回「AI」と書き起こし、原稿と合わない扱いになりました。通常の作り直し(3回)でも直らず、承認済みのLocal Rewrite(局所的な言い換え)で通過させました。"
           "ただし、言い換えで通した音声は、承認済みの安全規則(M3 Style Gate)により「人が確認するまで組み立てない」決まりです(Gateの緩和はしていません)。</li>"
           "<li><b>音声の品質問題ではありません。</b>音声は正常に読まれ、言い換え語もはっきり認識されています。確認してほしいのは「本文は『AIs』なのに、この段落だけ音声が『AI agents／AI systems』と読むことを許容するか」です。</li>"
           "<li><b>推定される原因(仮説・未検証):</b> 「AIs sent」は複数形のs(z音)と次の語sent(s音)が続くため、話し言葉ではsが融合して「AI sent」に聞こえやすい。同じ記事の他の「AIs」(13 AIs with…、the AIs could…)は問題なく認識されており、この1か所だけが失敗しています。</li></ul></div>")
    why = ("<h2>5. 自動処理では解消できなかった理由</h2><ol>"
           "<li><b>承認済みの救済はすべて評価され、いずれも対象外でした。</b>(a)複数形のTier3救済=二次Azureも「AI」と聞いたため成立せず(二次が裏付けないと救済不可)。(b)固有名詞アラーム受理=「AIs」は固有名詞ではなく対象外(<code>NO_PROPER_NOUN_EVIDENCE</code>)。"
           "(c)同音異表記救済(er109)=「AIs/AI」は同音異表記ではない。(d)発音台帳・Phrase List=台帳43件に「AI/AIs」は無く、二次ASRのPhrase Listは0件。台帳は固有名詞用で、略語の複数形を原稿不変のまま扱う承認済み手段は現行仕様にありません。</li>"
           "<li><b>通常の作り直しは上限まで実施済み</b>(標準2回＋代替指示1回＋Local Rewrite1回。Standardは減速後の再検証も3回)。これ以上の再生成は承認操作(approve_regenerate)が必要で、同じ「The AIs sent」で6回中6回失敗しており成功見込みも低い。</li>"
           "<li><b>M3 Style Gate(<code>LOCAL_REWRITE_RECOVERY</code>)は承認済みの安全規則</b>で、人の承認(<code>record_human_approval</code>)以外に解除手段がありません(Gate緩和はユーザー承認事項)。"
           "Standardのみ <code>STD_FALLBACK_USED_OR_UNKNOWN</code> も付いていますが、記録の付け方の非対称(OPEN-564)で、無くてもBLOCKは変わりません(模擬確認済み)。</li>"
           "<li>本文を「AI agents／AI systems」に変更すれば音声と本文が一致しますが、本文の変更はユーザー承認事項です。</li></ol>")
    ev = ("<h2>6. AIの評価とご確認いただきたい内容</h2><p>AIの評価: 意味・事実は変わっていません。違いは「AIs」→「AI agents／AI systems」の1語句のみで、言い換えは意味保存・事実非矛盾・自然さなどの7つの検査を通過しています。"
          "AI自身は音声を聞けないため、聞いて違和感がないかの最終確認は耳でお願いします。</p><p><b>聞いて確認してほしい点</b>: (1)「The AI agents sent to the island…」(Standard)／「The AI systems sent to the island…」(Advanced)と自然に読まれているか。"
          "(2)本文は「The AIs sent…」のままで、この1語だけ音声と異なることを許容できるか。</p>")
    q = ("<h2>7. 質問(1つ)</h2><p><b>上の2つの音声(Standard・Advanced)で、この段落の「AIs」を「AI agents／AI systems」と読む形でよいですか?</b></p>"
         "<p class='sec'>回答例:「両方OK」「Standardのみ不可」「Advancedのみ不可」。承認された場合のみ、この1 segmentの承認を記録し、残りの組立・公開へ進みます(追加の音声生成なし)。"
         "不可の場合の代替(本文を「AI agents／AI systems」に変更する等)は、その場合に別途ご相談します。</p>")
    page = ("<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><title>AIの仮想の島 Human Review(2 segment・原因説明つき)</title><meta name='viewport' content='width=device-width, initial-scale=1'>"
            f"<style>{css}</style></head><body><h1>AIの仮想の島: Human Review(2 segment)</h1>"
            "<p>状態: 完成版の組立前に、承認済みの安全規則で停止しています。最終の試聴ページではありません。(hr_01.htmlの説明を、原因調査の結果で置き換えた版です)</p>"
            + top + lvl("Standard", std, "hr/std_full_story_part1_k2.mp3", std_tries, "AI agents", std_diff)
            + lvl("Advanced", adv, "hr/adv_full_story_part1_k2.mp3", adv_tries, "AI systems", adv_diff)
            + why + ev + q + "</body></html>")
    assert "file:///" not in page and "C:\\" not in page
    with open(os.path.join(WEB, "hr_02.html"), "w", encoding="utf-8") as f:
        f.write(page)
    print("wrote hr_02.html", len(page))


if __name__ == "__main__":
    if "--v2" in sys.argv:
        build_v2()
    else:
        main()

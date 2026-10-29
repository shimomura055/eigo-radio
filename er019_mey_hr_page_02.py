# -*- coding: utf-8 -*-
"""FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02 委任_02: Std comment_2 HUMAN_REVIEW_REQUIRED 人間試聴判断用ページ(有料APIなし)。
er019_mey_page_02.py派生。Lock操作は一切しない(判断材料の表示のみ)。出力: user_test/middle_east_yemen_saudi_e2e_02/hr_comment_2/{index.html, audio/*}
PM_GOVERNANCE 14-7の4要素(疑い/確認箇所/機械判定結果/判断で何が確定するか)を記載。file:/// を含めない。"""
from __future__ import annotations
import er019_x_page_guard_01  # noqa: F401  SLOT-23 委任_04C: display_spec付き(新表示仕様)のrunならSTOP(旧per-article scriptは遡及なし。新規記事は er019_family_x_listening_page_01.py)
import difflib, glob, html, json, os, shutil, subprocess
import imageio_ffmpeg
import soundfile as sf

ROOT = os.path.dirname(os.path.abspath(__file__))
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
esc = html.escape
WAVRUN = os.path.join(ROOT, "er019_output", "family_x_audio_production_wiring_01", "middle_east_yemen_saudi__run_mey_02")
TXTRUN = os.path.join(ROOT, "er019_output", "middle_east_yemen_saudi", "run_mey_02")
WEB = os.path.join(ROOT, "user_test", "middle_east_yemen_saudi_e2e_02", "hr_comment_2")
AUD = os.path.join(WEB, "audio")
EV = os.path.join(ROOT, "docs", "research", "FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02", "hr_page_evidence_02.json")


def rj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def rt(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def hl(expected, got):
    """expectedを基準にした差分ハイライト(got側の差分を<mark>、期待側の欠落は[欠:..]、置換は(期待:..)で表示)。"""
    sm = difflib.SequenceMatcher(None, expected, got, autojunk=False)
    out = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            out.append(esc(got[j1:j2]))
        elif tag == "insert":
            out.append("<mark>" + esc(got[j1:j2]) + "</mark>")
        elif tag == "delete":
            out.append("<mark class='del'>[欠:" + esc(expected[i1:i2]) + "]</mark>")
        else:
            out.append("<mark>" + esc(got[j1:j2]) + "</mark><span class='exp'>(期待:" + esc(expected[i1:i2]) + ")</span>")
    return "".join(out)


def to_mp3(wav_src, mp3_dst, br="192k"):
    """*.wavは.gitignore対象のため、Pages配信用に高ビットレートmp3へ変換(元wavのsha/サイズはevidence jsonへ記録)。"""
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", wav_src, "-codec:a", "libmp3lame", "-b:a", br, mp3_dst], check=True)


def main():
    os.makedirs(AUD, exist_ok=True)
    a2 = os.path.join(WAVRUN, "a2")
    sup = rj(os.path.join(a2, "a2_support_texts.json"))
    expected = sup["comment_2"]
    att = []
    import er_hr_listing_policy_01 as hrl   # 委任_05(PM_GOVERNANCE 30-5): 掲載はユーザー判断対象のみ。本ページは3回ともASR NGだが『耳で読み誤りか判断してほしい』ため判断要求を明示(掲載は不変)
    _listed, _omitted = hrl.select_listing_takes([{"id": i, "asr_state": "NG_BOTH", "user_judgment_requested": True} for i in (1, 2, 3)])
    for i in [t["id"] for t in _listed]:
        wf = glob.glob(os.path.join(a2, "narration", "attempts", "comment_2_attempt%d_*.wav" % i))[0]
        j = rj(wf[:-4] + ".json")
        dst = "comment_2_attempt%d.mp3" % i
        to_mp3(wf, os.path.join(AUD, dst))
        x, sr = sf.read(wf, dtype="float32")
        s = j.get("scg_info") or {}
        att.append({"n": i, "route": j["route"], "wav": dst, "bytes": os.path.getsize(wf), "dur": round(x.shape[0] / sr, 2),
                    "sha256": j["sha256"], "mp3": dst, "mp3_bytes": os.path.getsize(os.path.join(AUD, dst)), "primary": j["asr_text"], "secondary": s.get("secondary_transcript"),
                    "cls": j["audio_classification"], "judge": s.get("unified_judge_state"), "reason": s.get("unified_reason_code"),
                    "phrase_list": s.get("phrase_list")})
    to_mp3(os.path.join(a2, "narration", "comment_3.wav"), os.path.join(AUD, "comment_3_reference.mp3"))
    c3 = sup["comment_3"]
    # Adv完成音声(mp3化、既存er019_mey_page_02.pyと同じ手順)
    x, sr = sf.read(os.path.join(WAVRUN, "b1b", "assembled", "Family_X_Audio_B1_MIDDLE_EAST_YEMEN_SAUDI.wav"), dtype="float32")
    tmp = os.path.join(AUD, "adv.tmp.wav")
    sf.write(tmp, x, sr)
    advmp3 = os.path.join(AUD, "MEY_Advanced_e2e_02.mp3")
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", tmp, "-codec:a", "libmp3lame", "-b:a", "128k", advmp3], check=True)
    os.remove(tmp)
    adv_dur = x.shape[0] / sr
    sizes = {n: os.path.getsize(os.path.join(AUD, n)) for n in sorted(os.listdir(AUD))}

    rows = ""
    for a in att:
        rows += ("<tr><td><b>録音%d</b><br>%s<br>%s秒 / 元wav %s bytes(再生はmp3 192k)<br><span class='sec'>sha %s</span></td>" % (a["n"], esc(a["route"]), a["dur"], format(a["bytes"], ","), a["sha256"][:12])
                 + "<td class='play'><audio controls preload='none' src='audio/%s'></audio></td>" % a["wav"]
                 + "<td>一次(OpenAI): %s<br><br>二次(Azure ja-JP, Phrase Listなし=%s): %s<br><span class='sec'>機械判定: 一次=%s / 統一judge=%s(%s)</span></td></tr>"
                 % (hl(expected, a["primary"]), a["phrase_list"] is False, hl(expected, a["secondary"] or ""), esc(a["cls"]), esc(str(a["judge"])), esc(str(a["reason"]))))
    pa = rt(os.path.join(TXTRUN, "a2", "article.md"))
    pb = rt(os.path.join(TXTRUN, "b1b", "article.md"))
    kpl = []
    for lv, lab in (("a2", "Standard"), ("b1b", "Advanced")):
        its = sorted(rj(os.path.join(WAVRUN, lv, "key_phrases", "keywords_canonicalized.json"))["items"], key=lambda it: it["rank"])
        kpl.append("<li>%s: %s</li>" % (lab, " / ".join(esc(i["used_form"]) for i in its)))
    css = ("<style>body{font-family:sans-serif;max-width:1100px;margin:1em auto;padding:0 1em;line-height:1.55}table{border-collapse:collapse;width:100%;margin-bottom:1.5em}"
           "th,td{border:1px solid #ccc;padding:6px;vertical-align:top;text-align:left}td.play{min-width:300px}audio{width:100%}.sec{color:#666;font-size:.85em}"
           "mark{background:#ffd6d6}mark.del{background:#ffe9b0}.exp{color:#a00;font-size:.8em}.note{background:#fff8e0;padding:8px;border:1px solid #cb8;margin-bottom:1em}"
           ".box{background:#f6f6f6;padding:8px;border:1px solid #ccc;white-space:pre-wrap}.combo{background:#eef6ff;padding:10px;border:1px solid #99c;margin-bottom:1em}</style>")
    req = ("<div class='note'><b>人間試聴依頼(PM_GOVERNANCE 14-7の4要素)</b><ol>"
           "<li><b>疑い</b>: Std「Comment 2」で、台本の「<b>タイフーン機</b>」が音声で正しく発音されているか。自動判定(ASR)が3回の録音すべてで「台風機/台風期/大奮期」と書き起こしたため、"
           "TTSの誤発音かASR側の表記揺れ・誤認識か未確定です。再生成上限(標準2+fallback1=3回)に達してHuman Review Lockになっています。</li>"
           "<li><b>確認してほしい箇所</b>: 各録音の冒頭「ここまでで、」直後の語。期待=「タイフーンき」(タイフーン+機)で、自然に「タイフーン」と聞こえれば許容。"
           "あわせて同じ録音内の「フーシ派」(録音2の一次ASRのみ「風師波」と誤記)が「ふーしは」と聞こえるか。参考として、同じrunのComment 3(『タイフーン戦闘機』)は二次ASRが完全一致で自動合格しています(下の参考音声)。</li>"
           "<li><b>機械判定</b>: 下表のとおり3回とも一次・二次ASRとも不一致(TRUE_CONTENT_MISMATCH / NG_BOTH)。数字・否定の差はなく、差は主に「タイフーン機」の語の書き起こしです。"
           "読みとして「台風(たいふう)機」は「タイフーン(たいふーん)機」と撥音「ん」の有無が異なるため、読み同値として自動受理される仕様は現状ありません。</li>"
           "<li><b>判断で確定すること</b>: (ア)どれかの録音を「問題なし」と承認 → その録音でHR Lockを解除(承認操作は人間の判断後にのみ実施)し、続けて残りのStd工程(組立・試聴ページ公開)を実行。"
           "(イ)全録音が不自然 → この文言のままでは音声化できない扱いとなり、文言(例: 「タイフーン戦闘機」)または方式の見直しが必要(新規判断)。</li></ol></div>")
    refc3 = ("<h3>参考: 同runのStd Comment 3(自動合格済み)</h3><p>台本: %s</p><audio controls preload='none' src='audio/comment_3_reference.mp3'></audio>" % esc(c3)
             + "<p class='sec'>一次ASR「台風戦闘機」/二次ASR「タイフーン戦闘機」(完全一致でSECONDARY_CONFIRMED)。同じ語が正しく読まれうる傍証であり、Comment 2の録音が正しい証明ではありません。</p>")
    pg = ("<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><title>Std Comment 2 人間試聴(HR)・中東E2E-02</title>"
          "<meta name='viewport' content='width=device-width, initial-scale=1'>" + css + "</head><body>"
          "<h1>Std Comment 2 人間試聴判断(中東E2E-02 run_mey_02)</h1>" + req
          + "<h2>期待文(台本)</h2><div class='box'>" + esc(expected) + "</div>"
          + "<h2>3録音と自動判定(差分を<mark>ハイライト</mark>、<span class='exp'>(期待:…)</span>は台本側の語)</h2>"
          + "<table><thead><tr><th>録音</th><th>再生</th><th>一次/二次ASR転写と差分</th></tr></thead><tbody>" + rows + "</tbody></table>"
          + refc3
          + "<h2>Advanced完成音声(通し全編 %.0f秒、Adv全segment自動合格・style gate PASS)</h2><div class='combo'><audio id='main_adv' controls preload='none' src='audio/MEY_Advanced_e2e_02.mp3'></audio></div>" % adv_dur
          + "<h2>Key Phrases</h2><ul>" + "".join(kpl) + "</ul>"
          + "<h2>Std日本語コメント全文(Preview/Comment1-4)</h2>" + "".join("<p><b>%s</b>: %s</p>" % (esc(k), esc(v)) for k, v in sup.items())
          + "<h2>Standard本文(A2)</h2><div class='box'>" + esc(pa) + "</div><h2>Advanced本文(B1B)</h2><div class='box'>" + esc(pb) + "</div></body></html>")
    assert "file:///" not in pg and "C:\\" not in pg and "C:/" not in pg
    with open(os.path.join(WEB, "index.html"), "w", encoding="utf-8") as f:
        f.write(pg)
    os.makedirs(os.path.dirname(EV), exist_ok=True)
    with open(EV, "w", encoding="utf-8") as f:
        json.dump({"expected": expected, "attempts": att, "adv_duration_s": round(adv_dur, 2), "file_sizes": sizes}, f, ensure_ascii=False, indent=1)
    print("page written; adv_dur", round(adv_dur, 2), sizes)


if __name__ == "__main__":
    main()

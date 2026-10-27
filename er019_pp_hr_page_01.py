# -*- coding: utf-8 -*-
"""FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01 委任_02: Std full_story_part2 (M3 Gate: fallback使用) Human Review試聴ページ(有料APIなし)。
er019_mey_hr_page_02.py派生。Lock/承認操作は一切しない(判断材料の表示のみ)。出力: user_test/paycheck_personality_e2e_01/hr_full_story_part2/{index.html, audio/*}
file:/// を含めない。正式試聴ページではない(Human Review用)。"""
from __future__ import annotations
import er019_x_page_guard_01  # noqa: F401  SLOT-23 委任_04C: display_spec付き(新表示仕様)のrunならSTOP(旧per-article scriptは遡及なし。新規記事は er019_family_x_listening_page_01.py)
import html, json, os, re, subprocess, difflib
import imageio_ffmpeg
import soundfile as sf

ROOT = os.path.dirname(os.path.abspath(__file__))
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
esc = html.escape
WAVRUN = os.path.join(ROOT, "er019_output", "family_x_audio_production_wiring_01", "paycheck_personality__run_pp_01")
TXTRUN = os.path.join(ROOT, "er019_output", "paycheck_personality", "run_pp_01")
WEB = os.path.join(ROOT, "user_test", "paycheck_personality_e2e_01", "hr_full_story_part2")
AUD = os.path.join(WEB, "audio")
EV = os.path.join(ROOT, "docs", "research", "FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01", "hr_page_evidence_01.json")
SEG = "full_story_part2"


def rj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def rt(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def to_mp3(wav_src, mp3_dst, br="192k"):
    """*.wavは.gitignore対象のため、Pages配信用にmp3へ変換(元wavはローカル保持、sha/サイズはevidence jsonへ記録)。"""
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", wav_src, "-codec:a", "libmp3lame", "-b:a", br, mp3_dst], check=True)


def nw(t):
    t = t.replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
    return re.sub(r"[^a-z0-9']", "", t.lower())


def word_diff(canon, asr):
    """canonical基準のword差分。ASR側は元表記のまま差分語を<mark>。(html, 差分リスト)を返す。"""
    cn = [nw(x) for x in canon.replace("\u201c", " ").replace("\u201d", " ").split() if nw(x)]
    at = asr.split()
    an = [nw(x) for x in at]
    idx = [i for i, x in enumerate(an) if x]
    sm = difflib.SequenceMatcher(None, cn, [an[i] for i in idx], autojunk=False)
    diffs, marked = [], set()
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            diffs.append((" ".join(cn[i1:i2]) or "(なし)", " ".join(at[idx[k]] for k in range(j1, j2)) or "(欠落)"))
            for k in range(j1, j2):
                marked.add(idx[k])
    out = ["<mark>%s</mark>" % esc(w) if i in marked else esc(w) for i, w in enumerate(at)]
    return " ".join(out), diffs


def main():
    os.makedirs(AUD, exist_ok=True)
    a2 = os.path.join(WAVRUN, "a2")
    res = rj(os.path.join(a2, "audit", "tts_generation_results.json"))["segments"][SEG]
    canon = res["canonical_text"]
    logs = res["standard_attempts_log"]
    ev = {"segment": SEG, "review_lock_canonical_text_sha256": rj(os.path.join(a2, "audit", "review_lock_state.json"))[SEG]["canonical_text_sha256"], "attempts": []}
    adopt_wav = os.path.join(a2, "narration", SEG + ".wav")
    to_mp3(adopt_wav, os.path.join(AUD, "part2_fallback_take_adopted.mp3"))
    x, sr = sf.read(adopt_wav, dtype="float32")
    ev["adopted"] = {"wav": os.path.relpath(adopt_wav, ROOT).replace("\\", "/"), "sha256": res["sha256"], "bytes": os.path.getsize(adopt_wav), "dur": round(x.shape[0] / sr, 2),
                     "mp3_bytes": os.path.getsize(os.path.join(AUD, "part2_fallback_take_adopted.mp3")), "model": res["model"], "instruction": res["instruction_label"],
                     "asr_class": res.get("post_slowdown_final_classification"), "slowdown_actual_pct": res["slowdown_info"]["slowdown_pct_actual"]}
    rows = ""
    for i, a in enumerate(logs, 1):
        wf = a["attempt_audio_path"]
        wf = wf if os.path.isabs(wf) else os.path.join(ROOT, wf)
        dst = "part2_style_attempt%d.mp3" % i
        to_mp3(wf, os.path.join(AUD, dst))
        prim = a["cascade_steps"][0]["text"]
        sec = a["cascade_steps"][1]["text"]
        judge = a["cascade_steps"][1].get("unified_judge_state")
        ph, pd = word_diff(canon, prim)
        sh, sd = word_diff(canon, sec)
        ev["attempts"].append({"n": i, "wav": os.path.relpath(wf, ROOT).replace("\\", "/"), "mp3": dst, "bytes": os.path.getsize(wf), "judge": judge,
                               "cls": a["audio_classification"], "primary_diffs": pd, "secondary_diffs": sd, "primary": prim, "secondary": sec})
        rows += ("<tr><td><b>承認Style attempt %d</b><br>不合格(統一judge=%s / %s)<br>%s秒<br><span class='sec'>%s</span></td>" % (i, esc(str(judge)), esc(a["audio_classification"]), a["duration_seconds"], esc(os.path.basename(wf)))
                 + "<td class='play'><audio controls preload='none' src='audio/%s'></audio></td>" % dst
                 + "<td>一次(OpenAI): %s<br><br>二次(Azure ja-JP/無Phrase List): %s<br><br><span class='sec'>台本との語差分(一次): %s / (二次): %s</span></td></tr>"
                 % (ph, sh, esc("; ".join("%s→%s" % d for d in pd) or "なし"), esc("; ".join("%s→%s" % d for d in sd) or "なし")))
    fh, fd = word_diff(canon, res["post_slowdown_asr_text"])
    ev["fallback_asr_diffs"] = fd
    fbrow = ("<tr><td><b>採用候補(fallback take)</b><br>style=natural, clear, conversational(既存fallback)<br>%s秒(6%%減速後)<br>ASR=%s</td><td class='play'><audio id='main_part2' controls preload='none' src='audio/part2_fallback_take_adopted.mp3'></audio></td>"
             "<td>ASR(減速後): %s<br><span class='sec'>台本との語差分: %s</span></td></tr>" % (ev["adopted"]["dur"], esc(str(res.get("post_slowdown_final_classification"))), fh, esc("; ".join("%s→%s" % d for d in fd) or "なし")))
    refs = ""
    for s in ("full_story_part1", "full_story_part3"):
        dst = "%s_reference.mp3" % s
        to_mp3(os.path.join(a2, "narration", s + ".wav"), os.path.join(AUD, dst))
        refs += "<p><b>%s</b>(標準・承認Styleのattempt採用)<br><audio controls preload='none' src='audio/%s'></audio></p>" % (s, dst)
    x, sr = sf.read(os.path.join(WAVRUN, "b1b", "assembled", "Family_X_Audio_B1_PAYCHECK_PERSONALITY.wav"), dtype="float32")
    tmp = os.path.join(AUD, "adv.tmp.wav")
    sf.write(tmp, x, sr)
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", tmp, "-codec:a", "libmp3lame", "-b:a", "128k", os.path.join(AUD, "PP_Advanced_e2e_01.mp3")], check=True)
    os.remove(tmp)
    adv_dur = x.shape[0] / sr
    pa = rt(os.path.join(TXTRUN, "a2", "article.md"))
    pb = rt(os.path.join(TXTRUN, "b1b", "article.md"))
    css = ("<style>body{font-family:sans-serif;max-width:1100px;margin:1em auto;padding:0 1em;line-height:1.55}table{border-collapse:collapse;width:100%;margin-bottom:1.5em}"
           "th,td{border:1px solid #ccc;padding:6px;vertical-align:top;text-align:left}td.play{min-width:300px}audio{width:100%}.sec{color:#666;font-size:.85em}"
           "mark{background:#ffd6d6}.note{background:#fff8e0;padding:8px;border:1px solid #cb8;margin-bottom:1em}"
           ".box{background:#f6f6f6;padding:8px;border:1px solid #ccc;white-space:pre-wrap}.combo{background:#eef6ff;padding:10px;border:1px solid #99c;margin-bottom:1em}</style>")
    banner = ("<div class='note'><b>これはHuman Review(人間試聴判断)用ページです。正式な試聴ページではありません。</b> "
              "Production技術完成=Advanced済 / Standard未完(Standardの完成音声はまだありません)。この判断が済むまでStandard通し音声は組み立てられません。</div>")
    req = ("<div class='note'><b>人間試聴依頼(PM_GOVERNANCE 14-7の4要素)</b><ol>"
           "<li><b>疑い</b>: Std「Full Story part 2」の採用候補は、承認済みStyleで2回続けて自動判定(ASR)が不合格となり、既存のfallback style(natural, clear, conversational)で生成した録音です。"
           "承認Styleで作られていないため、M3 Gate(FINAL_STYLE_SHA_MISMATCH_NO_HINT / STD_FALLBACK_USED_OR_UNKNOWN)が人間の承認なしの組立を止めています。同じ記事のpart1/part3と声の調子が揃っているか、不自然な読みが無いかが疑いです。</li>"
           "<li><b>確認してほしい箇所</b>: (1)全体の声の調子(下の参考part1/part3と比べて違和感が無いか) (2)「So, earning more makes me more serious!」が感嘆の引用として自然か(承認Styleの録音1/2は一次ASRが疑問符「serious?」と書き起こした) "
           "(3)「…binoculars you use to look at…」「Then you turn the pages…」の読み(録音1/2は「used to」、録音1は「you'd turn」と書き起こされた) (4)最後の「Wait before you jump to that conclusion.」。</li>"
           "<li><b>機械判定</b>: 承認Style録音1/2=統一judge NG_BOTH(一次・二次ASRとも不一致。差は語・句読点の揺れのみで、意味・数値・否定の差なし)。採用候補=fallback 1回目でprimary_pass(ASR転写は台本と語レベルで差分なし、6%減速後もNORMALIZED_MATCH)。リピート検査の旗なし・クリッピングなし。</li>"
           "<li><b>判断で確定すること</b>: (ア)採用候補を「問題なし」と承認 → 人間承認記録(record_human_approval)の後、Std組立・正式試聴ページ公開へ進む(費用ほぼJPY0)。"
           "(イ)不自然 → Std音声の再生成(新run、audio約JPY25〜30)などの代替をFableが提示。<b>承認はこのページでは行いません</b>(ユーザーの判断後にのみ実施)。</li></ol></div>")
    pg = ("<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><title>Std Full Story part2 人間試聴(HR)・給料と性格 E2E-01</title>"
          "<meta name='viewport' content='width=device-width, initial-scale=1'>" + css + "</head><body>"
          "<h1>Std Full Story part 2 人間試聴判断(給料と性格 E2E-01 run_pp_01)</h1>" + banner + req
          + "<h2>台本(canonical本文・英文全文)</h2><div class='box'>" + esc(canon) + "</div>"
          + "<h2>採用候補と承認Style録音の比較(<mark>ハイライト</mark>=台本と異なる語)</h2>"
          + "<table><thead><tr><th>録音</th><th>再生</th><th>ASR転写と差分</th></tr></thead><tbody>" + fbrow + rows + "</tbody></table>"
          + "<h3>声の調子の比較用(同記事Stdの承認Style採用segment)</h3>" + refs
          + "<h2>Advanced完成音声(先行試聴用・通し全編 %.0f秒)</h2><div class='note'>Production技術完成=Advanced済 / Standard未完。Advanced全segment自動合格・style gate PASS・key_phrase_source_gate PASS 5/5。</div>" % adv_dur
          + "<div class='combo'><audio id='main_adv' controls preload='none' src='audio/PP_Advanced_e2e_01.mp3'></audio></div>"
          + "<h2>Advanced全文スクリプト</h2><div class='box'>" + esc(pb) + "</div>"
          + "<h2>Standard本文(A2、参考)</h2><div class='box'>" + esc(pa) + "</div></body></html>")
    assert "file:///" not in pg and "C:\\" not in pg and "C:/" not in pg
    with open(os.path.join(WEB, "index.html"), "w", encoding="utf-8") as f:
        f.write(pg)
    ev["adv_duration_s"] = round(adv_dur, 2)
    ev["file_sizes"] = {n: os.path.getsize(os.path.join(AUD, n)) for n in sorted(os.listdir(AUD))}
    os.makedirs(os.path.dirname(EV), exist_ok=True)
    with open(EV, "w", encoding="utf-8") as f:
        json.dump(ev, f, ensure_ascii=False, indent=1)
    print("page written; adv_dur", round(adv_dur, 2), ev["file_sizes"])
    for a in ev["attempts"]:
        print(a["n"], a["primary_diffs"], a["secondary_diffs"])
    print("fb", ev["fallback_asr_diffs"])


if __name__ == "__main__":
    main()

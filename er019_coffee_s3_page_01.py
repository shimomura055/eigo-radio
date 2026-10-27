# -*- coding: utf-8 -*-
"""FAMILY-X-STD-JA-S3-ADOPTION-AND-WIRING-01 委任_01 (Phase A): Coffee Std 日本語Preview/Comment1〜4 S3差し替え版 試聴ページ生成(有料APIなし)。
Trial専用・Production非接続。R2版ページ(user_test/coffee_fxpw_e2e_01)は読み取りのみで不変。
入力: S3出力dir(er019_coffee_s3_support_regen_01.py の成果物)。出力: <out-dir>/index.html + audio/*.mp3 。file:/// を含めない。"""
from __future__ import annotations
import er019_x_page_guard_01  # noqa: F401  SLOT-23 委任_04C: display_spec付き(新表示仕様)のrunならSTOP(旧per-article scriptは遡及なし。新規記事は er019_family_x_listening_page_01.py)
import argparse, html, json, os, re, subprocess
import imageio_ffmpeg
import soundfile as sf

esc = html.escape
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
SEG = ("preview", "comment_1", "comment_2", "comment_3", "comment_4")
LABEL = {"preview": "Preview", "comment_1": "Comment 1", "comment_2": "Comment 2", "comment_3": "Comment 3", "comment_4": "Comment 4"}
R2_IDX = {"Preview": 6, "Comment 1": 16, "Comment 2": 18, "Comment 3": 20, "Comment 4": 22}   # R2 page std_NN.mp3 (R2 timeline.json non-pause index)


def rj(p):
    return json.load(open(p, encoding="utf-8"))


def mp3(x, sr, out, br="96k"):
    tmp = out + ".tmp.wav"
    sf.write(tmp, x, sr)
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", tmp, "-codec:a", "libmp3lame", "-b:a", br, out], check=True)
    os.remove(tmp)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s3-dir", required=True)
    ap.add_argument("--r2-page-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args()
    S3, R2P, WEB = a.s3_dir, a.r2_page_dir, a.out_dir
    AUD = os.path.join(WEB, "audio")
    os.makedirs(AUD, exist_ok=True)
    info = rj(f"{S3}/assemble_std_s3.json")
    qa = rj(f"{S3}/qa_results.json")
    ev = rj(f"{S3}/style_evidence.json")
    g3 = rj(f"{S3}/gain_report.json")
    cost = rj(f"{S3}/cost_actual_01.json")
    fr2 = rj("er019_output/family_x_audio_production_wiring_01/coffee_prices__run_fxpw_01/a2/audit/tts_generation_results.json")
    x, sr = sf.read(info["out_path"], dtype="float32")
    full = "Coffee_Standard_S3_support_01.mp3"
    mp3(x, sr, os.path.join(AUD, full), br="128k")
    tl = [e for e in info["timeline"] if not e["part"].startswith("pause")]
    start = {}
    rows = []
    for e in tl:
        if e["part"] in LABEL.values():
            fn = "s3_" + e["part"].lower().replace(" ", "_") + ".mp3"
            s, d = e["start_seconds"], e["duration_seconds"]
            mp3(x[int(round(s * sr)): int(round((s + d) * sr))], sr, os.path.join(AUD, fn))
            start[e["part"]] = (s, d, fn)
    for lab, i in R2_IDX.items():       # 比較用R2音声が存在すること
        assert os.path.exists(os.path.join(R2P, "audio", f"std_{i:02d}.mp3")), (lab, i)
    r2full = "../coffee_fxpw_e2e_01/audio/Coffee_Standard_fxpw_e2e_01.mp3"
    assert os.path.exists(os.path.join(R2P, "audio", "Coffee_Standard_fxpw_e2e_01.mp3"))

    css = ("<style>body{font-family:sans-serif;max-width:1100px;margin:1em auto;padding:0 1em;line-height:1.5}table{border-collapse:collapse;width:100%;margin-bottom:1.5em}"
           "th,td{border:1px solid #ccc;padding:6px;vertical-align:top;text-align:left}td.play{min-width:300px}audio{width:100%}.sec{color:#666;font-size:.85em}"
           ".script{background:#f6f6f6;padding:4px;margin:3px 0}.combo{background:#eef6ff;padding:10px;border:1px solid #99c;margin-bottom:1em}"
           ".note{background:#fff8e0;padding:8px;border:1px solid #cb8;margin-bottom:1em}.warn{background:#ffecec;padding:8px;border:1px solid #c88;margin-bottom:1em}"
           "pre{white-space:pre-wrap;background:#f6f6f6;padding:8px}button{margin:2px}</style>")
    head = ("<div class='warn'><b>Coffee Standard: 日本語Preview/Comment1〜4をS3「親しみのあるニュースナレーター」で差し替えた検証版</b>"
            "(Production未採用・Coffee限定の検証用)。旧R2版は <a href='../coffee_fxpw_e2e_01/index.html'>../coffee_fxpw_e2e_01/index.html</a>(変更なし)。"
            "<br>ユーザー試聴前です。<b>PASS/採用の判定はまだありません</b>(下記QAは機械的な品質確認であり、聴感の合否ではありません)。"
            "Standard英語音声・Key Phrase・日本語原稿・Voice・モデル・Advanced側は変更していません。</div>")
    main_player = (f"<h2>Standard通し(S3版・{info['duration_seconds']:.0f}秒)</h2><div class='combo'><audio id='main_s3' controls preload='none' src='audio/{full}'></audio>"
                   "<div>通しの該当位置へジャンプ: " + " ".join(
                       f"<button onclick=\"var a=document.getElementById('main_s3');a.currentTime={max(0, v[0]-1.5):.2f};a.play()\">{esc(k)}</button>" for k, v in start.items())
                   + f"</div><div class='sec'>参考: 旧R2版 通し <audio controls preload='none' src='{r2full}'></audio></div></div>")
    trs = []
    for nm in SEG:
        lab = LABEL[nm]
        s, d, fn = start[lab]
        q = qa[nm]
        r2s = fr2["segments"][nm]
        r2fn = f"../coffee_fxpw_e2e_01/audio/std_{R2_IDX[lab]:02d}.mp3"
        gk = "preview" if nm == "preview" else f"a2_{nm}"
        gi = g3[gk]
        qa_txt = (f"ASR分類={esc(str(q['primary_classification']))} / 統一judge={esc(str(q['asr_judgement_state']))}({esc(str(q['reason_code']))}) / 長さ={'OK' if q['final_length_ok'] else 'NG'} / "
                  f"TTS call={q['tts_call_count']}(retryなし・再生成なし・fallbackなし)")
        asr = f"<div class='sec'>ASR転写(S3): {esc(str(q['asr_text']))}</div>"
        gtxt = f"gain={gi.get('gain')} (RMS前 {gi.get('rms_before')} → 目標 {g3['target_rms']}" + (")" if nm != 'preview' else "、Previewは正式版と同じく無加工)")
        trs.append(
            f"<tr><td><b>{esc(lab)}</b><br><span class='sec'>S3版 {d:.1f}秒 / R2版 {r2s['duration_seconds']}秒</span></td>"
            f"<td class='play'>S3版<audio controls preload='none' src='audio/{fn}'></audio>R2版(比較)<audio controls preload='none' src='{r2fn}'></audio></td>"
            f"<td><div class='script'>{esc(ev['texts'][nm] and q['canonical_text'])}</div><div class='sec'>原稿sha256: {esc(ev['texts'][nm]['sha256'][:16])}… (正式版と一致)</div>"
            f"<div class='sec'>QA: {qa_txt}</div>{asr}<div class='sec'>音量処理: {esc(gtxt)}</div></td></tr>")
    table = "<h2>5 sectionの個別再生(S3版とR2版を並べて比較)</h2><table><thead><tr><th>パート</th><th>音声</th><th>原稿 / QA</th></tr></thead><tbody>" + "".join(trs) + "</tbody></table>"
    cond = ("<h2>S3 Style全文(共通指示込み・逐語、TTSへ実際に渡した文字列)</h2>"
            f"<pre>{esc(ev['s3_style_full_text'])}</pre><div class='sec'>{ev['s3_style_chars']}文字 / sha256 {ev['s3_style_sha256']} / 出典 {esc(ev['s3_source'])}</div>"
            "<h2>生成条件(正式版と同一であることの根拠)</h2><ul>"
            f"<li>Voice: {esc(ev['voice'])} / model指定: {esc(ev['model_requested'])} / 応答model_version: {esc(', '.join(ev['response_model_versions']))}(正式版と同一。正式版 tts_generation_results.json segments[preview/comment_*].voice/model)</li>"
            f"<li>無音trim margin: {ev['margin_s']}秒(正式版 er003_v1_n3_01_tts_generate.py:626 NARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS と同値をscript内でassert)</li>"
            "<li>減速(time-stretch): なし(正式版もPreview/Commentは減速なし。減速はFull Storyのみ)</li>"
            "<li>音量処理: Preview=無加工(er019_family_x_audio_production_runner_01.py:1838-1839)、Comment1〜4=目標RMS正規化(同:1853)。目標RMS "
            f"{g3['target_rms']}はR2版gain_reportの値に固定(他sectionを不変に保つため)。S3 Previewから再計算すると{g3['reference_if_production_recomputed_target']}(参考)。</li>"
            f"<li>Assembly: Production関数(build_family_x_a2_timeline/assemble_with_timeline)でR2と同一のsegment順・gap。R2版再現チェック max_abs_diff={info['replication_check_r2_vs_formal']['max_abs_diff']:.2e}、"
            f"S3差し替え対象外sectionのR2との差 最大{max(v for v in info['unchanged_sections_max_abs_diff'].values() if v is not None):.2e}(=実質同一)。</li>"
            f"<li>Style ID(Trial用): {esc(ev['style_instruction_id'])} / Master Audio Store書込み: なし / Production Style profile変更: なし(R2 base sha {esc(ev['r2_style_sha256'][:12])}…のまま)</li>"
            f"<li>実測費用(推定): TTS ¥{cost['tts_jpy']} + ASR ¥{cost['asr_jpy_est']} = ¥{cost['total_jpy_est']}</li></ul>"
            "<h2>Advanced</h2><p>Advanced側は変更なし: <a href='../coffee_fxpw_e2e_01/index.html#adv'>R2版ページのAdvanced</a></p>")
    pg = (f"<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><title>Coffee Standard S3差し替え検証版(s3_support_01)</title>"
          f"<meta name='viewport' content='width=device-width, initial-scale=1'>{css}</head><body><h1>Coffee Standard S3差し替え検証版</h1>{head}{main_player}{table}{cond}</body></html>")
    assert "file:///" not in pg and "C:\\" not in pg and "C:/" not in pg
    open(os.path.join(WEB, "index.html"), "w", encoding="utf-8").write(pg)
    tot = sum(os.path.getsize(os.path.join(AUD, f)) for f in os.listdir(AUD))
    print("page written", WEB, "audio files", len(os.listdir(AUD)), "bytes", tot)


if __name__ == "__main__":
    main()

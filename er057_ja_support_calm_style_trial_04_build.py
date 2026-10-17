# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-STANDARD-JA-SUPPORT-CALM-STYLE-TRIAL-04 委任_01: 正規化・mp3化・通し連結・異音検知・試聴ページ・機械指標表
(ローカル処理のみ。API/Production書込なし)。連結の間・音量処理は全10仕様×2 Takeで同一。"""
import os, sys, json, html, argparse, hashlib
sys.path.insert(0, os.getcwd())
import numpy as np
import soundfile as sf
import er002_common as common
import er003_b1_p9a_audio as p9a
import er057_audio_anomaly_detect_trial_01 as ad
import er057_ja_support_calm_style_trial_04_gen as gen

ROOT = gen.ROOT
SEG, TAKES, ORDER, S = gen.SEG, gen.TAKES, gen.ORDER, gen.S
GAP_SEC = 0.8   # 通し連結の無音gap(全候補同一。前回Trial 02と同じ0.8秒)
TARGET = json.load(open(f"{gen.FORMAL}/audit/gain_report.json", encoding="utf-8"))["target_rms"]   # 正式版の目標RMS
PREV_BASE = "https://shimomura055.github.io/eigo-radio/user_test/coffee_ja_style_trial_02/audio"
SEGJA = {"preview": "Preview", "comment_1": "Comment1", "comment_2": "Comment2", "comment_3": "Comment3", "comment_4": "Comment4"}


def norm_stereo(mono):
    gain = p9a.compute_gain_for_target_rms(mono, TARGET)
    return p9a.mono_24k_to_stereo_target(mono * gain)


def rd(path):
    s, sr = common.read_wav_float(path)[:2]
    assert sr == common.SAMPLE_RATE
    return s


def shaf(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load(in_dir):
    R, A = {}, {}
    for l in open(f"{in_dir}/results_01.jsonl", encoding="utf-8"):
        r = json.loads(l); R[r["id"]] = r
    for l in open(f"{in_dir}/asr_results_01.jsonl", encoding="utf-8"):
        r = json.loads(l); A[r["id"]] = r
    return R, A


def ok_cls(c):
    return c in ("EXACT_MATCH", "NORMALIZED_MATCH")


def asr_badge(a):
    c = a["classification"]
    cls = "ok" if ok_cls(c) else ("mid" if c == "PHONETIC_MATCH" else "warn")
    return f'<span class="asr {cls}">ASR: {html.escape(c)}</span>'


def aud(src, label, script="", voice="Aoede", extra=""):
    return (f'<div class="a"><span class="lbl">{html.escape(label)}</span><audio controls preload="none" src="{src}"></audio>'
            f'<span class="v">{html.escape(voice)}</span><span class="s">{html.escape(script)}</span>{extra}</div>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-dir", default=f"{ROOT}/er057_output/ja_support_calm_style_trial_04")
    ap.add_argument("--page-dir", default=f"{ROOT}/user_test/coffee_ja_style_trial_04")
    a = ap.parse_args()
    in_dir, page = os.path.abspath(a.in_dir), os.path.abspath(a.page_dir)
    aud_dir = f"{page}/audio"
    os.makedirs(aud_dir, exist_ok=True)
    gen.build_styles()
    texts = gen.load_texts()
    R, A = load(in_dir)
    exp = len(ORDER) * len(TAKES) * len(SEG)
    assert len(R) == exp and all(r["status"] == "OK" for r in R.values()), f"results incomplete {len(R)}/{exp}"
    assert len(A) == exp, f"asr incomplete {len(A)}/{exp}"
    M = {"target_rms": TARGET, "gap_sec": GAP_SEC, "durations": {}, "anomaly": {}, "wav_sha256": {}}
    for sid in ORDER:
        for tk in TAKES:
            segs = []
            for nm in SEG:
                k = f"{sid}_{tk}_{nm}"
                p = f"{in_dir}/raw/{k}.wav"
                m = rd(p)
                M["wav_sha256"][k] = shaf(p)
                M["durations"][k] = round(len(m) / common.SAMPLE_RATE, 3)
                c, _ = ad.analyze(m, common.SAMPLE_RATE, k, True)
                M["anomaly"][k] = [x.get("symptom") + ":" + str(x.get("confidence")) for x in c]
                s = norm_stereo(m); segs.append(s)
                sf.write(f"{aud_dir}/{k}.mp3", np.clip(s, -1, 1), p9a.TARGET_SAMPLE_RATE, format="MP3")
            seq = []
            for i, s in enumerate(segs):
                if i: seq.append(p9a.silence_stereo(GAP_SEC))
                seq.append(s)
            full = np.concatenate(seq)
            sf.write(f"{aud_dir}/{sid}_{tk}_full.mp3", np.clip(full, -1, 1), p9a.TARGET_SAMPLE_RATE, format="MP3")
            M["durations"][f"{sid}_{tk}_full"] = round(len(full) / p9a.TARGET_SAMPLE_RATE, 2)
    json.dump(M, open(f"{in_dir}/build_manifest_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    build_page(page, texts, R, A, M)
    quality(in_dir, texts, R, A, M)
    tot = sum(os.path.getsize(f"{aud_dir}/{f}") for f in os.listdir(aud_dir))
    print("built", len(os.listdir(aud_dir)), "mp3", round(tot / 1e6, 1), "MB")


def spec_stats(sid, tk, A, M):
    ids = [f"{sid}_{tk}_{n}" for n in SEG]
    c = {"EXACT_MATCH": 0, "NORMALIZED_MATCH": 0, "PHONETIC_MATCH": 0, "NG": 0}
    for x in ids:
        k = A[x]["classification"]; c[k if k in c else "NG"] += 1
    return c, sum(M["durations"][x] for x in ids), [x for x in ids if M["anomaly"][x]]


def build_page(page, texts, R, A, M):
    css = """body{font-family:sans-serif;max-width:1040px;margin:1em auto;padding:0 1em;line-height:1.5}h2{border-bottom:2px solid #888;margin-top:2em}
h3{margin:.2em 0}h4{margin:.8em 0 .2em}.set{border:1px solid #ccc;border-radius:6px;padding:.6em 1em;margin:1em 0}
.set.base{border:3px solid #b8860b;background:#fff8e1}.badge{display:inline-block;background:#b8860b;color:#fff;border-radius:4px;padding:1px 8px;font-size:.8em;margin-left:.5em}
.take{border-left:4px solid #9ab;padding-left:.7em;margin:.6em 0}.take.B{border-left-color:#c97}
.a{display:flex;align-items:center;gap:.6em;margin:.2em 0;flex-wrap:wrap}.a .lbl{min-width:9em;font-size:.9em}.a .v{font-size:.8em;color:#06c;min-width:4em}
.a .s{font-size:.85em;color:#333;flex:1 1 20em}audio{height:32px;min-width:360px}pre{white-space:pre-wrap;background:#f5f5f5;padding:.5em;font-size:.8em}
.note{color:#555;font-size:.9em}.warnbox{background:#ffe9e9;border:1px solid #c66;padding:.5em 1em;border-radius:6px}.aim{font-size:.9em;color:#333}
table{border-collapse:collapse}td,th{border:1px solid #ccc;padding:2px 6px;font-size:.85em}.asr{font-size:.75em;padding:1px 5px;border-radius:4px}
.asr.ok{background:#dfd}.asr.mid{background:#ffd}.asr.warn{background:#fed}.eval{font-size:.85em;color:#a00;background:#fff;border:1px dashed #aaa;padding:2px 6px;margin-top:.3em}"""
    H = [f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Coffee Standard 日本語解説 Style 比較 Trial 04(落ち着き方向)</title><style>{css}</style></head><body>
<h1>Coffee Standard 日本語解説(Preview／Comment1〜4)Style比較 Trial 04</h1>
<div class="warnbox"><b>試聴用Trialです。ユーザー試聴前のため、どの仕様にもPASS判定はありません。</b> Productionへは反映していません(現行Productionは基準R2のまま)。選定はあなたの試聴後に別タスクで行います。</div>
<p class="note">目的: 正式Coffee E2E完成版でやや高く感じたテンション・語尾・抑揚を、P2・R2の温かみ・親しみ・明瞭さを残したまま落ち着かせる方向で比較します。
基準(P2・R2、金色枠)+新規S1〜S8の計10仕様を、各仕様とも5セクション一式を<b>独立に2回(Take A／Take B)</b>生成しました。<b>全Takeを掲載しています(聞こえのよいものだけの選別はしていません)</b>。Blind比較ではなく、候補名と狙いを併記しています。
2 Takeとも許容範囲に収まるか(テンション・語尾・抑揚)をご確認ください。</p>
<h3>共通の条件</h3><ul class="note">
<li>原稿: 正式Coffee E2E完成版(run coffee_prices__run_fxpw_01)のStandard日本語解説 Preview／Comment1〜4を、TTSへ渡した文字列のままそのまま使用(書き換えなし)。</li>
<li>Voice=Aoede、model=gemini-3.8-flash-lite-tts、language=ja-JP、Standard同期(DEV Trial)、無音trim余白・減速なし等、正式版のPreview／Comment生成と同条件。比較で変えたのはStyleのみ。</li>
<li>基準P2・R2は前回Trial(coffee_ja_style_trial_02)の実際のStyle全文を逐語で使用(sha256検証済み)。S1〜S8のStyleは「個別指示+共通指示」を直接連結した全文です(P2・R2には共通指示を付けていません)。</li>
<li><b>通し再生は「試聴用の連結」であり、正式Assemblyではありません</b>: Preview→Comment1→2→3→4を、全仕様・全Takeで同一の{GAP_SEC}秒の無音で連結し、同一の音量処理(目標RMS={M['target_rms']}、正式版と同値)をかけています。個別セクションも同じ音量処理済みです。</li>
<li>ASR表示は機械による参考判定(前回Trialと同じ日本語ASR方式)であり、聴感の良し悪しではありません。NGでも再生成していません。「ユーザー聴感評価」欄はすべて未記入です。</li></ul>"""]
    # 目次+機械指標サマリ
    H.append('<h2>機械指標サマリ(聴感評価ではありません)</h2><table><tr><th>仕様</th><th>Style文字数</th>' + "".join(
        f"<th>Take {tk}: ASR 完全/正規化/音読み一致/NG</th><th>Take {tk}: 5セクション尺(s)</th>" for tk in TAKES) + "</tr>")
    for sid in ORDER:
        row = f'<tr><td><a href="#{sid}">{sid}</a>{" (基準)" if sid in ("P2","R2") else ""}</td><td>{len(gen.STYLES[sid])}</td>'
        for tk in TAKES:
            c, d, _ = spec_stats(sid, tk, A, M)
            row += f'<td>{c["EXACT_MATCH"]}/{c["NORMALIZED_MATCH"]}/{c["PHONETIC_MATCH"]}/{c["NG"]}</td><td>{d:.1f}</td>'
        H.append(row + "</tr>")
    H.append("</table>")
    for sid in ORDER:
        base = sid in ("P2", "R2")
        if base:
            title = f"基準 {sid}" + ("(前回Trialの好評Style・逐語)" if sid == "P2" else "(前回Trialの好評Style・逐語。現行ProductionのStd日本語Styleと同一)")
            aim = ("前回Trial(coffee_ja_style_trial_02)のP2をそのまま使用。共通指示は付けていません。" if sid == "P2" else
                   "前回Trial R2をそのまま使用。共通指示は付けていません。現行Productionと同一文字列(sha256一致)で、完成版でテンションが高めに感じられた比較元です。")
        else:
            nm, am, _ = S[sid]
            title, aim = f"{sid} {nm}", am
        H.append(f'<div class="set{" base" if base else ""}" id="{sid}"><h3>{html.escape(title)}{"<span class=badge>基準</span>" if base else ""}</h3>'
                 f'<div class="aim">調整内容と狙い: {html.escape(aim)}</div>')
        for tk in TAKES:
            c, d, anom = spec_stats(sid, tk, A, M)
            H.append(f'<div class="take {tk}"><h4>{sid} Take {tk}</h4>')
            H.append(aud(f"audio/{sid}_{tk}_full.mp3", f"{sid} Take {tk} 通し", f"Preview→Comment1→2→3→4(試聴用の連結・{GAP_SEC}秒無音・正式Assemblyではない)", "Aoede",
                         f' <span class="note">{M["durations"][f"{sid}_{tk}_full"]}s</span>'))
            for sg in SEG:
                k = f"{sid}_{tk}_{sg}"
                H.append(aud(f"audio/{k}.mp3", f"{sid} {tk} {SEGJA[sg]}", texts[sg]["tts"], "Aoede",
                             asr_badge(A[k]) + f' <span class="note">{M["durations"][k]}s</span>'))
            H.append(f'<div class="note">機械評価: ASR 完全一致/正規化一致/音読み一致/NG = {c["EXACT_MATCH"]}/{c["NORMALIZED_MATCH"]}/{c["PHONETIC_MATCH"]}/{c["NG"]}、異音検知={len(anom)}件</div>')
            H.append('<div class="eval">ユーザー聴感評価(テンション／語尾／抑揚): 未記入(ユーザー試聴前、PASS判定なし)</div></div>')
        H.append(f'<details open><summary>TTSへ渡したStyle全文({len(gen.STYLES[sid])}文字、sha256={gen.sha_s(gen.STYLES[sid])[:16]}…)</summary><pre>{html.escape(gen.STYLES[sid])}</pre></details>')
        H.append('<details><summary>実際に読み上げた原稿全文(5セクション、全仕様共通)</summary><pre>' + html.escape("\n\n".join(f"[{SEGJA[n]}]\n{texts[n]['tts']}" for n in SEG)) + "</pre></details></div>")
    # 参考: 前回Trial
    H.append('<h2 id="prev">参考: 前回Trial(旧原稿・既存音声)のP2／R2</h2><p class="note"><b>これは旧原稿・既存音声です</b>(前回Trial coffee_ja_style_trial_02で生成済み。今回は再生成していません)。'
             '原稿が今回の正式版と異なるため、今回の比較には使いません。同一原稿での比較は上の基準P2・R2(今回生成)を使ってください。</p>')
    for sid in ("P2", "R2"):
        H.append(f'<div class="set"><h3>旧原稿・既存音声: {sid}</h3>')
        H.append(aud(f"{PREV_BASE}/{sid}_full.mp3", f"{sid} 旧原稿 通し", "旧原稿・既存音声(前回Trial)。Preview→Comment1〜4(旧連結)", "Aoede"))
        for sg in SEG:
            H.append(aud(f"{PREV_BASE}/{sid}_{sg}.mp3", f"{sid} 旧 {SEGJA[sg]}", "旧原稿・既存音声(前回Trial)", "Aoede"))
        H.append("</div>")
    H.append("</body></html>")
    open(f"{page}/index.html", "w", encoding="utf-8").write("\n".join(H))


def quality(in_dir, texts, R, A, M):
    L = ["# QUALITY_COMPARISON_01(機械指標のみ。ユーザー聴感評価は未実施、PASS判定なし)\n",
         "機械指標 = Trial閾値不変の `er057_audio_anomaly_detect_trial_01.py` + Primary ASR判定(前回Trial 02と同方式) + 尺。聴感の良し悪しではない。\n",
         "| ID | Take | Style文字数 | 5seg合計尺(s) | 通し尺(s) | ASR 完全/正規化/音読み一致/NG | 異音検知(件数: 詳細) |", "|---|---|---|---|---|---|---|"]
    for sid in ORDER:
        for tk in TAKES:
            c, d, anom = spec_stats(sid, tk, A, M)
            an = "; ".join(f"{x}:{'/'.join(M['anomaly'][x])}" for x in anom) or "-"
            L.append(f"| {sid} | {tk} | {len(gen.STYLES[sid])} | {d:.2f} | {M['durations'][f'{sid}_{tk}_full']} | "
                     f"{c['EXACT_MATCH']}/{c['NORMALIZED_MATCH']}/{c['PHONETIC_MATCH']}/{c['NG']} | {len(anom)}: {an} |")
    L += ["\n## 正式版(Production R2)参考尺", "", "| segment | 正式版 duration_s |", "|---|---|"] + [f"| {n} | {texts[n]['formal_duration_s']} |" for n in SEG]
    L += ["\n## ASR非PASS(完全一致/正規化一致以外)の内訳(警告記録。再生成していない)\n", "| ID | 判定 | 原稿 | ASR |", "|---|---|---|---|"]
    for k, a in A.items():
        if not ok_cls(a["classification"]):
            L.append(f"| {k} | {a['classification']} | {a['canonical']} | {a['asr_text']} |")
    open(f"{in_dir}/QUALITY_COMPARISON_01.md", "w", encoding="utf-8").write("\n".join(L))


if __name__ == "__main__":
    main()

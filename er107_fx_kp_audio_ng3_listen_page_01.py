# -*- coding: utf-8 -*-
"""FAMILY-X-KP-AUDIO-NG3-EVIDENCE-01: Family X Key Phrase音声NG 3件(pump one's fist x2 / novelty minaudiere x1)の
全attempt wav 12本の試聴ページ+証拠json生成。API 0 / TTS 0 / Production経路外。既存wav・ログは読み取りのみ(mp3へ変換コピー)。
Whisperは保存wavに対するローカルfaster-whisper(small/int8、Production KP投票と同一設定)の再判定=参考値(本番では未実行)。
使い方: python er107_fx_kp_audio_ng3_listen_page_01.py"""
from __future__ import annotations
import glob, hashlib, html, json, os, subprocess, sys
sys.path.insert(0, ".")
import imageio_ffmpeg
import er104_kp_three_asr_vote_01 as vote
import er006_preprod_hardening_01_validation as V
import er006_secondary_asr_01 as S

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
E = "er019_output/family_x_audio_production_wiring_01/"
OUT = "user_test/fx_kp_audio_ng3_listen_01"
DATA = "docs/research/FAMILY-X-KP-AUDIO-NG3-EVIDENCE-01/evidence_data_01.json"
CASES = [
    dict(id="N1", run="coffee_prices__run_jre_01", level="a2", label="coffee_prices(コーヒー価格)/Standard(a2)", kp="pump one's fist", disp="pumps its fist"),
    dict(id="N2", run="coffee_prices__run_jre_01", level="b1b", label="coffee_prices(コーヒー価格)/Advanced(b1b)", kp="pump one's fist", disp="pumps its fist"),
    dict(id="N3", run="small_bag__run_jre_01", level="a2", label="small_bag(小さなバッグ)/Standard(a2)", kp="novelty minaudière", disp="novelty minaudière"),
]
PASS_CLS = ("NORMALIZED_MATCH", "EXACT_MATCH", "EXACT")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def mp3(src, dst):
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", src, "-codec:a", "libmp3lame", "-b:a", "128k", dst], check=True)


def verdict(canon, text):
    t = " ".join(str(text).split()) if text else ""
    if not t.strip():
        return False, "NO_TRANSCRIPT"
    cls = V.classify_asr_match(canon, t)
    alt = S._step_alternate_pass(cls) if not cls.should_pass else None
    return bool(cls.should_pass or alt), str(alt or getattr(cls, "classification", ""))


def pill(ok):
    if ok is None:
        return '<b style="color:#666">(不明)</b>'
    return '<b style="color:#0a7d2c">PASS</b>' if ok else '<b style="color:#c00">NG</b>'


def main():
    os.makedirs(OUT + "/audio", exist_ok=True)
    os.makedirs(os.path.dirname(DATA), exist_ok=True)
    data = {"generated_by": "er107_fx_kp_audio_ng3_listen_page_01.py", "cases": []}
    for c in CASES:
        base = f"{E}{c['run']}/{c['level']}"
        lock = json.load(open(f"{base}/audit/review_lock_state.json", encoding="utf-8"))["kp1_en"]
        lockmap = {os.path.basename(a["attempt_audio_path"]): a for a in lock["last_attempts_log"]}
        final_sha = sha(f"{base}/narration/kp1_en.wav")
        rows = []
        for f in sorted(glob.glob(f"{base}/narration/attempts/kp1_en_attempt*.json")):
            aj = json.load(open(f, encoding="utf-8"))
            wav = f[:-5] + ".wav"
            bn = os.path.basename(wav)
            steps = {s["step"]: s for s in aj["cascade_steps"]}
            p_txt, s_txt = steps["primary_1"]["text"], steps["secondary_vote"]["text"]
            lg = lockmap.get(bn)
            if lg:
                vb = lg["asr_judgement"]["vote"]
                p_pass, s_pass = vb["primary"]["pass"], vb["secondary"]["pass"]
                s_src = "stored_vote_block"
                vstate, vreason = vb["state"], vb["reason"]
                w_called = vb["whisper_called"]
            else:
                p_pass = steps["primary_1"]["classification"] in PASS_CLS
                s_pass = False  # att1/2はper-attempt vote block未保存。最終NG・同一転写のatt3/4保存値等からの推定
                s_src = "estimated_no_vote_block"
                vstate = "NG(vote block未保存; per-attempt json unified_judge_state=%s)" % steps["secondary_vote"].get("unified_judge_state")
                vreason = "未保存"
                w_called = None
            ws = vote.whisper_transcribe(wav)
            wp, wl = verdict(c["kp"], ws)
            n = int(bn.split("attempt")[1][0])
            mp = f"{c['id']}_attempt{n}.mp3"
            mp3(wav, f"{OUT}/audio/{mp}")
            rows.append(dict(attempt=n, loop_attempt_index=aj["loop_attempt_index"], route=aj["route"], saved_at=aj["saved_at"], wav=wav, wav_sha256=aj["sha256"],
                             wav_sha_verified=(sha(wav) == aj["sha256"]), is_final_hr_wav=(aj["sha256"] == final_sha), page_audio=f"audio/{mp}",
                             tts_model=aj["model"], tts_voice=aj["voice"], primary_text=p_txt, primary_class=steps["primary_1"]["classification"], primary_pass=p_pass,
                             azure_text=s_txt, azure_class=steps["secondary_vote"].get("classification"), azure_pass=s_pass, azure_pass_source=s_src,
                             vote_state=vstate, vote_reason=vreason, whisper_called_in_production=w_called,
                             whisper_offline_text=ws, whisper_offline_pass=wp, whisper_offline_label=wl,
                             source_attempt_json=f, source_lock=(f"{base}/audit/review_lock_state.json" if lg else None)))
            print(c["id"], n, "| P:", p_txt, p_pass, "| S:", s_txt, s_pass, "| W:", ws, wp, "| FINAL" if rows[-1]["is_final_hr_wav"] else "", flush=True)
        data["cases"].append(dict(c, lock_state=lock["state"], lock_reason=lock["reason"], lock_updated_at=lock["updated_at"], final_wav=f"{base}/narration/kp1_en.wav",
                                  final_wav_sha256=final_sha, cumulative_tts_attempts=lock["cumulative_tts_attempts"], rows=rows))
    json.dump(data, open(DATA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    H = ['<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>Family X KP音声NG 3件 試聴・ASR照合</title><style>body{font-family:sans-serif;max-width:1100px;margin:1em auto;padding:0 .6em}',
         'table{border-collapse:collapse;width:100%;font-size:.88em}td,th{border:1px solid #bbb;padding:5px;vertical-align:top}th{background:#eee}',
         '.fin{background:#fff6e0}audio{width:220px;max-width:100%}.tbl{overflow-x:auto}.note{background:#f4f4f4;padding:.5em;border-radius:6px;font-size:.9em}</style></head><body>',
         '<h2>Family X Key Phrase音声NG 3件: 全attempt試聴とASR判定(運営者向け)</h2>',
         "<p>対象: <code>pump one's fist</code> 2件(coffee_prices Standard/Advanced)と <code>novelty minaudière</code> 1件(small_bag Standard)。各件はTTSを4回生成(2回x2周)し、4回ともASR投票に合格せずHuman Review(HR)に至りました。"
         '下表の12本が実際にNG判定を受けた全音声です(橙行=最終的にHR待ちとして残ったwav)。既存wavは変更せず、mp3へ変換コピーしています。</p>',
         '<p class="note">凡例: OpenAI=gpt-4o-mini-transcribe(Primary) / Azure=Azure Speech STT en-US(Secondary) / Whisper=本番の判定では全て<b>未実行</b>。'
         '右端の「Whisper(参考)」は、保存wavをローカルのfaster-whisper(small/int8、本番KP投票と同一設定、費用0)で今回再判定した参考値で、<b>本番の判定には使われていません</b>。'
         'ASRの転写は事実の並記であり、発音の正否の断定ではありません。<b>実際に聴いて、各ASRの転写と照合してください。</b>PASS/NGは既存Validator(classify_asr_match+同音救済)の単独判定です。</p>']
    for c in data["cases"]:
        H.append(f'<h3>{c["id"]}. {html.escape(c["label"])} / 正しいKey Phrase: <code>{html.escape(c["kp"])}</code></h3>')
        H.append(f'<p><small>記事上の表記 <code>{html.escape(c["disp"])}</code>。最終判定: {html.escape(c["lock_state"])}({html.escape(c["lock_updated_at"])})、理由: {html.escape(c["lock_reason"])}。TTS累計{c["cumulative_tts_attempts"]}回。</small></p>')
        H.append('<div class="tbl"><table><tr><th>attempt</th><th>再生</th><th>OpenAI(Primary)</th><th>Azure(Secondary)</th><th>本番投票の結果</th><th>Whisper(本番)</th><th>Whisper(参考・今回offline)</th></tr>')
        for r in c["rows"]:
            fin = ' class="fin"' if r["is_final_hr_wav"] else ""
            tag = "<br><small>★HR待ちとして残ったwav</small>" if r["is_final_hr_wav"] else ""
            asrc = "" if r["azure_pass_source"] == "stored_vote_block" else "<br><small>(PASS/NGはvote block未保存のため推定: 最終NG)</small>"
            wprod = "未実行" if r["whisper_called_in_production"] is False else "未実行(推定。attempt#1/#2はvote block未保存)"
            H.append(f'<tr{fin}><td>#{r["attempt"]}<br><small>周{1 if r["attempt"] <= 2 else 2}-{r["loop_attempt_index"]}</small>{tag}</td>'
                     f'<td><audio controls preload="none" src="{r["page_audio"]}"></audio></td>'
                     f'<td><code>{html.escape(r["primary_text"])}</code> {pill(r["primary_pass"])}<br><small>{html.escape(str(r["primary_class"]))}</small></td>'
                     f'<td><code>{html.escape(r["azure_text"])}</code> {pill(r["azure_pass"])}{asrc}</td>'
                     f'<td><small>{html.escape(str(r["vote_state"]))}<br>{html.escape(str(r["vote_reason"]))}</small></td>'
                     f'<td><small>{wprod}</small></td>'
                     f'<td><code>{html.escape(r["whisper_offline_text"])}</code> {pill(r["whisper_offline_pass"])}</td></tr>')
        H.append('</table></div>')
    H.append('<p><small>Whisperを呼ばない理由: 本番KP投票(kp_vote_check_v1)は、OpenAIとAzureが両方NG(NG_BOTH)、または反対票側に保護差(数値/否定)がある(NG_PROTECTED_DISSENT)場合、Whisperを呼びません(er104_kp_three_asr_vote_01.py whisper_needed / tally)。</small></p>')
    H.append('<hr><p><small>出典: er019_output/family_x_audio_production_wiring_01/(coffee_prices__run_jre_01, small_bag__run_jre_01)の narration/attempts/kp1_en_attempt*.json・audit/review_lock_state.json。'
             '詳細: docs/research/FAMILY-X-KP-AUDIO-NG3-EVIDENCE-01/EVIDENCE_01.md。TTS: gemini-3.8-flash-lite-tts(voice Aoede)。</small></p></body></html>')
    open(OUT + "/index.html", "w", encoding="utf-8").write("\n".join(H))
    print("done")


if __name__ == "__main__":
    main()

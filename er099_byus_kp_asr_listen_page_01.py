# ============================================================
# er099_byus_kp_asr_listen_page_01.py  (API 0 / TTS 0 / Production経路外)
# byUs記事KP音声7件のASR比較(Primary/Secondary=保存済み結果、Whisper=ローカルfaster-whisper再判定)+
# take part 合格音声と問題音声(旧wav)の聞き比べ試聴ページを生成する。既存音声は読み取りのみ(コピーして変換)。
# 使い方: python er099_byus_kp_asr_listen_page_01.py --out user_test/byus_kp_asr_listen_01 --mapping <mapping.json>
# ============================================================
from __future__ import annotations
import argparse, hashlib, html, json, os, subprocess, sys, collections
sys.path.insert(0, ".")
import imageio_ffmpeg
import er008_disfluency_qa_18 as dq18
import er006_preprod_hardening_01_validation as V
import er006_secondary_asr_01 as S

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
STORE = "er006_output/master_audio_store_01/audio"
RUN = "er019_output/family_x_audio_production_wiring_01/manga_ai_chat_byus__run_byus_01"
SURVEY = "er096_output/kp_dual_prod_01/survey_article_b.json"
LIVE = "er096_output/kp_dual_prod_01/take_part_live.json"
E88 = "er088_output/kp_asr_dual_pass_trial_01"
OLD_WAV = f"{E88}/kp4_en.wav"
OLD_RUN_WAV = f"{RUN}/a2/narration/kp4_en.invalid_20261021.wav"

# 表示順(ユーザー原文の7件。think up / blurt を強調)
ITEMS = [  # (表示表現, survey used_form, 記事上の位置)
    ("think up", "think up", "Std KP1 / Adv KP1"),
    ("can't wait", "can't wait", "Std KP2 / Adv KP5"),
    ("fan stories", "fan stories", "Std KP3"),
    ("take part", "take part", "Std KP4"),
    ("story-maker", "story-maker", "Std KP5 / Adv KP4"),
    ("blurt", "blurt", "Adv KP2"),
    ("bring in", "bring in", "Adv KP3"),
]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def mp3(src, dst):
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", src, "-codec:a", "libmp3lame", "-b:a", "128k", dst], check=True)


def verdict(canon, text):
    """既存Production分類器(classify_asr_match + _step_alternate_pass)による単独PASS相当判定。"""
    t = " ".join(str(text).split()) if text else ""
    if not t.strip():
        return False, "NO_TRANSCRIPT"
    cls = V.classify_asr_match(canon, t)
    alt = S._step_alternate_pass(cls) if not cls.should_pass else None
    return bool(cls.should_pass or alt), str(alt or getattr(cls, "classification", ""))


def whisper(wav, size):
    ws = dq18.transcribe_verbatim(wav, language="en", model_size=size)
    return " ".join("".join(w["text"] for w in ws).split())


def pill(ok):
    return '<b style="color:#0a7d2c">PASS</b>' if ok else '<b style="color:#c00">NG</b>'


def cell(text, ok):
    return f'<code>{html.escape(str(text))}</code> {pill(ok)}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mapping", required=True)
    a = ap.parse_args()
    aud = os.path.join(a.out, "audio")
    os.makedirs(aud, exist_ok=True)
    os.makedirs(os.path.dirname(a.mapping), exist_ok=True)
    survey = {r["used_form"]: r for r in json.load(open(SURVEY, encoding="utf-8"))}
    mapping = {"generated_by": "er099_byus_kp_asr_listen_page_01.py", "items": [], "take_part": {}}
    rows = []
    for i, (disp, uf, pos) in enumerate(ITEMS, 1):
        s = survey[uf]
        k = s["kp_dual_check"]
        src = f"{STORE}/{s['master_audio_id']}.wav"
        real = sha(src)
        assert real == k["wav_sha256"], (uf, real, k["wav_sha256"])
        canon = k["canonical_text"]
        ws = whisper(src, "small")
        wm = whisper(src, "medium")
        wsp, wsl = verdict(canon, ws)
        wmp, wml = verdict(canon, wm)
        fn = f"kp_{i}_{uf.replace(' ', '_').replace(chr(39), '')}.mp3"
        mp3(src, os.path.join(aud, fn))
        p, sec = k["primary"], k["secondary"]
        overall = bool(k["ok"])
        rows.append(dict(disp=disp, pos=pos, canon=canon, p=p, sec=sec, ws=ws, wsp=wsp, wsl=wsl, wm=wm, wmp=wmp, overall=overall, fn=fn, bad=uf in ("think up", "blurt")))
        mapping["items"].append({"expression": disp, "judge_canonical": canon, "position": pos, "master_audio_id": s["master_audio_id"],
                                 "source_wav": src, "wav_sha256": real, "page_audio": f"audio/{fn}",
                                 "primary_openai": p, "secondary_azure": sec, "judge_state": k["judge_state"], "reason_code": k["reason_code"],
                                 "source_json": SURVEY, "whisper_small": {"text": ws, "pass": wsp, "label": wsl}, "whisper_medium": {"text": wm, "pass": wmp, "label": wml}})
        print(disp, "| P:", p["text"], p["pass"], "| S:", sec["text"], sec["pass"], "| Wsmall:", ws, wsp, "| Wmed:", wm, wmp, "| overall", overall, flush=True)

    # ---- take part 問題音声 ----
    good_src = f"{STORE}/0714639d351b47c34b4d4103.wav"
    assert sha(OLD_WAV) == "675cd6b1aec9865acbdb411b588672d9cc963b936bb4a35bb2d8158cb4172186"
    assert sha(OLD_RUN_WAV) == sha(OLD_WAV)
    mp3(OLD_WAV, os.path.join(aud, "take_part_PROBLEM_old_675cd6b1.mp3"))
    mp3(good_src, os.path.join(aud, "take_part_PASSED_e4405501.mp3"))
    t88 = []
    for l in open(f"{E88}/results.jsonl", encoding="utf-8"):
        r = json.loads(l)
        ps = r["primary_and_secondary"]
        t88.append(dict(trial=r["trial"], primary=ps["primary_call"]["text"], secondary=ps["judge"]["secondary_text"], state=ps["judge"]["state"],
                        whisper_stored=" ".join(r["whisper"]["text"].split())))
    live = json.load(open(LIVE, encoding="utf-8"))
    old_ws, old_wm = whisper(OLD_WAV, "small"), whisper(OLD_WAV, "medium")
    new_ws, new_wm = rows[3]["ws"], rows[3]["wm"]
    old_wsp, _ = verdict("take part", old_ws)
    old_wmp, _ = verdict("take part", old_wm)
    pc = collections.Counter(t["primary"] for t in t88)
    sc = collections.Counter(t["secondary"] for t in t88)
    print("OLD whisper small:", old_ws, old_wsp, "| medium:", old_wm, old_wmp)
    print("er088 primary counts:", dict(pc), "secondary:", dict(sc), "| live:", [(x["primary_text"], x["secondary_text"]) for x in live])
    mapping["take_part"] = {
        "problem_wav": {"source": OLD_WAV, "same_sha_copy_in_run": OLD_RUN_WAV, "sha256": sha(OLD_WAV), "page_audio": "audio/take_part_PROBLEM_old_675cd6b1.mp3",
                        "er088_10_trials": t88, "er096_live_3_trials": live, "whisper_small_now": old_ws, "whisper_medium_now": old_wm,
                        "original_production_primary_text": "Take part. (KP_TAKE_PART_INVESTIGATION_01.md:16 採用時のgpt-4o-mini-transcribe転写)",
                        "other_ng_audio_files": "なし(NG判定10回+3回は全て同一wav sha 675cd6b1。他にtake partのNG判定音声は保存されていない)"},
        "passed_wav": {"source": good_src, "sha256": sha(good_src), "run_wav": f"{RUN}/a2/narration/kp4_en.wav", "page_audio": "audio/take_part_PASSED_e4405501.mp3",
                       "primary": rows[3]["p"], "secondary": rows[3]["sec"], "whisper_small": new_ws, "whisper_medium": new_wm}}
    json.dump(mapping, open(a.mapping, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    # ---- HTML ----
    H = ['<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>byUs KP音声 ASR比較・試聴</title><style>body{font-family:sans-serif;max-width:980px;margin:1em auto;padding:0 .6em}',
         'table{border-collapse:collapse;width:100%;font-size:.9em}td,th{border:1px solid #bbb;padding:5px;vertical-align:top}th{background:#eee}',
         '.bad{background:#fff0f0}audio{width:230px;max-width:100%}.tbl{overflow-x:auto}</style></head><body>',
         '<h2>byUs記事 Key Phrase音声7件: ASR比較と試聴</h2>',
         '<p>対象: 記事 manga_ai_chat_byus(run_byus_01)のKey Phrase英語音声7種(Std5+Adv5、重複3を除く)。既存音声は再生成・編集していません(mp3へ変換コピーのみ)。'
         'ASR認識文字列は事実の並記であり、発音の正否の断定ではありません。<b>実際に聴いて判断してください。</b></p>',
         '<p>新基準(2026-10-22採用): KP英語はPrimary(OpenAI gpt-4o-mini-transcribe)<u>と</u>Secondary(Azure Speech STT)の両方PASSが必須。Whisperは参考列(判定には使われない)。</p>',
         '<h3>1. byUs 7件 ASR比較表</h3><div class="tbl"><table><tr><th>#</th><th>正しい表現(記事内位置)</th><th>Primary<br>OpenAI gpt-4o-mini-transcribe</th><th>Secondary<br>Azure Speech STT</th>'
         '<th>Whisper small<br>(faster-whisper、Production QA同一)</th><th>Whisper medium(参考)</th><th>新基準 総合</th><th>音声</th></tr>']
    for i, r in enumerate(rows, 1):
        cls = ' class="bad"' if r["bad"] else ""
        tag = ' <span style="color:#c00;font-weight:bold">★新基準で不合格</span>' if r["bad"] else ""
        H.append(f'<tr{cls}><td>{i}</td><td><b>{html.escape(r["disp"])}</b>{tag}<br><small>{r["pos"]}<br>判定用表記: {html.escape(r["canon"])}</small></td>'
                 f'<td>{cell(r["p"]["text"], r["p"]["pass"])}</td><td>{cell(r["sec"]["text"], r["sec"]["pass"])}</td>'
                 f'<td>{cell(r["ws"], r["wsp"])}</td><td>{cell(r["wm"], r["wmp"])}</td>'
                 f'<td>{pill(r["overall"])}</td><td><audio controls preload="none" src="audio/{r["fn"]}"></audio></td></tr>')
    H.append('</table></div><p><small>PASS/NGは各Providerの転写を既存Validator(classify_asr_match+同音救済)に通した単独判定(Primary/Secondaryは保存済みの判定値)。Primary/Secondaryの文字列は2026-10-22 09:18の保存済み結果(survey_article_b.json)で、'
             'いずれも保存済みの同一wav(sha256一致を確認)に対する結果です。Whisperは本ページ作成時に同じwavをローカルで判定(費用0)。</small></p>')
    H.append('<h3>2. take part: 合格音声と問題音声の聞き比べ</h3><p>期待する表現: <b>take part</b>(第2語は part)。どちらも既存の保存音声です。</p>')
    H.append('<div class="tbl"><table><tr><th>音声</th><th>再生</th><th>Primary</th><th>Secondary</th><th>Whisper small</th><th>Whisper medium(参考)</th><th>新基準</th></tr>')
    pp = rows[3]
    H.append(f'<tr><td><b>A. 合格済み音声</b><br><small>記事の現行正式KP4(sha256 e4405501…466f)</small></td><td><audio controls preload="none" src="audio/take_part_PASSED_e4405501.mp3"></audio></td>'
             f'<td>{cell(pp["p"]["text"], pp["p"]["pass"])}</td><td>{cell(pp["sec"]["text"], pp["sec"]["pass"])}</td><td>{cell(new_ws, pp["wsp"])}</td><td>{cell(new_wm, pp["wmp"])}</td><td>{pill(pp["overall"])}</td></tr>')

    def tcount(c):
        return "<br>".join(f'<code>{html.escape(k)}</code> x{v}' for k, v in c.most_common())

    H.append(f'<tr class="bad"><td><b>B. 問題音声(旧KP4)</b><br><small>sha256 675cd6b1…2186。NG判定(10回+3回)に使われた音声はこの1ファイルのみ</small></td>'
             f'<td><audio controls preload="none" src="audio/take_part_PROBLEM_old_675cd6b1.mp3"></audio></td>'
             f'<td>{tcount(pc)}<br><small>(同一wavを10回判定、er088。Production dual再判定3回は全て <code>Take tart.</code>)</small></td><td>{tcount(sc)}<br><small>(10回。再判定3回も同じ)</small></td>'
             f'<td>{cell(old_ws, old_wsp)}<br><small>保存済み(2026-10-21)も同じ: <code>Take Tarte.</code></small></td><td>{cell(old_wm, old_wmp)}</td><td>{pill(False)}<br><small>10回とも Secondary NG</small></td></tr>')
    H.append('</table></div>')
    H.append('<p><small>補足(事実): 旧wavは採用時のPrimary転写が <code>Take part.</code> で通過しており(KP_TAKE_PART_INVESTIGATION_01.md)、後日の同一wav再判定ではPrimaryの転写は回ごとに変動しました(上表B)。'
             'Secondary(Azure)は10/10・3/3で <code>Take Tart.</code>。</small></p>')
    H.append('<h3>3. 聴いて判断してほしい点</h3><ul><li>表1の <b>think up</b> と <b>blurt</b>(赤行): それぞれ正しい発音に聞こえるか。</li>'
             '<li>表2のAとB: Bの第2語が part に聞こえるか、tart などに聞こえるか。Aは part に聞こえるか。</li>'
             '<li>表1の他の5件も必要ならご確認ください。</li></ul>')
    H.append('<hr><p><small>ASRの関係: Primary=OpenAI gpt-4o-mini-transcribe(OpenAIの音声認識API)、Secondary=Azure Speech STT、Whisper=オープンモデルWhisperのfaster-whisper実装(ローカル、small int8 / medium int8)。'
             'PrimaryとWhisperは別モデル・別実装です。出典: docs/research/ASR-THREE-WAY-COMPARISON-TRIAL-01/TRIAL_RESULT_01.md:7。</small></p></body></html>')
    open(os.path.join(a.out, "index.html"), "w", encoding="utf-8").write("\n".join(H))
    print("done", a.out)


if __name__ == "__main__":
    main()

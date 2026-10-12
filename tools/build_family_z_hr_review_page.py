# FAMILY-Z-MELOS HR試聴ページ生成 v2(CS監査 委任_03、2026-10-12。API呼出0、読み取り+mp3変換のみ)
# 旧版(委任_12D)からの変更: 要確認 / 採用確定 / 解決済み の3区分、Std a2 part1_c5 を新take(attempt4、標準TTS)へ差替え、
# 各clipに原文/全ASR転写/期待発音/既存機構で判断できない理由を記載。採択・override・再生成・HR承認記録は一切行わない。
import hashlib
import html
import json
import os
import sys

RUN = "er026_output/family_z_production_e2e_01/melos/run_e2e_02"
BK = "er026_output/family_z_production_e2e_01/melos/cs_audit_01/pre_regen_c5_backup"
OUT = "user_test/family_z_melos_01"
QUEUE = "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl"

EXPECT_EN = ("期待発音: 作品内の名前 Melos(走れメロス)。英語での自然な読みは MEL-os 系(/ˈmɛlɒs/ 前後)。"
             "Pronunciation Ledger の melos は MEE-lahs(low、辞書推定で実際の読みと不一致の可能性、OPEN-308)。"
             "ASRの綴り(Mello/Mellow/Mellis/Mallow 等)は読みの根拠にならない。")
CHECK_NOTE = ("確認の観点(Opus指摘): <b>語末の s の有無</b>と<b>母音の読み(Mel- の e が「エ」か)</b>を同時に確認してください。"
              "Mellow/Mello と聞こえても語末 s が発音されていれば Melos と読めている場合があり、逆に s が脱落していれば誤りです。")


def load(p):
    return json.load(open(p, encoding="utf-8"))


def to_mp3(wav, mp3):
    import soundfile as sf
    data, sr = sf.read(wav)
    sf.write(mp3, data, sr, format="MP3")


def esc(x):
    return html.escape(str(x))


def seg(lv, cid):
    return load(f"{RUN}/{lv}/audit/tts_generation_results.json")["segments"][cid]


def lock(lv, cid):
    return load(f"{RUN}/{lv}/audit/review_lock_state.json")[cid]


def queue_steps(lv, cid):
    steps, ts = [], None
    for l in open(QUEUE, encoding="utf-8"):
        if "run_e2e_02" not in l:
            continue
        r = json.loads(l)
        if r.get("wav_path", "").replace("\\", "/").endswith(f"/{lv}/narration/{cid}.wav"):
            steps, ts = r.get("steps", []), r.get("timestamp")
    return steps, ts


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def audio_html(src, label):
    return f"<div><b>{esc(label)}</b><br><audio controls preload='none' src='{src}'></audio></div>"


def steps_table(steps):
    out = "<table><tr><th>step</th><th>provider</th><th>転写</th></tr>"
    for s in steps:
        out += f"<tr><td>{esc(s.get('step'))}</td><td>{esc(s.get('provider') or 'openai_asr')}</td><td>{esc(s.get('text'))}</td></tr>"
    return out + "</table>"


def main():
    os.makedirs(f"{OUT}/audio", exist_ok=True)
    sections = {"review": [], "adopted": [], "resolved": []}
    manifest = []

    # ---- 要確認1: Std a2 part1_c5 新take(attempt4、標準TTS) ----
    lk = lock("a2", "full_story_part1_c5")
    a4 = f"{RUN}/a2/narration/attempts/full_story_part1_c5_attempt4_customadfcf33f.wav"
    a6 = f"{RUN}/a2/narration/full_story_part1_c5.wav"
    to_mp3(a4, f"{OUT}/audio/a2_full_story_part1_c5_attempt4.mp3")
    to_mp3(a6, f"{OUT}/audio/a2_full_story_part1_c5_current_disk_attempt6.mp3")
    to_mp3(f"{BK}/full_story_part1_c5.wav", f"{OUT}/audio/a2_full_story_part1_c5_old_take.mp3")
    log4 = [a for a in lk["last_attempts_log"] if "attempt4" in (a.get("attempt_audio_path") or "")][0]
    steps4 = [{"step": s["step"], "provider": "azure" if ("secondary" in s["step"] or "tier3" in s["step"]) else "openai_asr", "text": s["text"]}
              for s in log4["cascade_steps"]]
    manifest.append({"level": "a2", "clip_id": "full_story_part1_c5", "section": "review", "take": "attempt4_standard_tts",
                     "wav": a4, "wav_sha256": sha(a4), "mp3": "audio/a2_full_story_part1_c5_attempt4.mp3"})
    sections["review"].append(
        "<section class='hr'><h2>要確認 1: Std(A2) / full_story_part1_c5 「Melos said.」(新take・標準TTS attempt4)</h2>"
        + audio_html("audio/a2_full_story_part1_c5_attempt4.mp3", "現行clip(正式採択の対象): 新take attempt4(標準TTS・最新Production経路)")
        + "<p><b>正式に採択するかを判断いただく対象はこの新take(attempt4)です。</b>OpenAI は「Mellis said」、Azure は「Mallow said.」と転写しました。"
          f"<br><small>(再生成の最終状態は <code>STOPPED</code> / review_lock=<code>{esc(lk['state'])}</code>。run_e2e_02 のレビューロックは未変更で、"
          "承認記録・採択はこの調査では一切行っていません。参考: ディスク上の現行wav(attempt6、最小fallback)は下記の参考音声で、転写が「melloset」「Mellowset」のTTS_FAILURE=不採用相当です)</small></p>"
        + f"<table><tr><th>原文(canonical)</th><td>Melos said.</td></tr><tr><th>期待発音</th><td>{esc(EXPECT_EN)}</td></tr></table>"
        + "<h3>全ASR転写(attempt4)</h3>" + steps_table(steps4)
        + "<h3>既存機構で自動判断できない理由</h3><ul>"
          "<li>承認済み Connected Speech Pattern A は綴り水準(ASR語 == 原文語から -s/-es を除いた綴り)の完全一致が必要。ASR は Mellis / Mallow を返し、原文語幹 Melo と綴りが一致しない。</li>"
          "<li>Equivalence Layer は TRUE_CONTENT_MISMATCH 限定+CMU音素辞書が必要。Melos は固有名詞(辞書未収録)でここに到達しない(OPEN-327)。</li>"
          "<li>OpenAI と Azure の2系統が互いに異なる綴りを返し、いずれも Melos と綴らないため独立ASRの一致(corroboration)も成立しない。</li>"
          "<li>固有名詞の表記ゆれだけを理由に TTS を繰り返し再生成しない既存方針(HR化)に従い、人間の聴感確認へ回しています。</li></ul>"
        + f"<p>{CHECK_NOTE}</p>"
        + "<details><summary>参考音声(採択対象ではありません)</summary>"
        + audio_html("audio/a2_full_story_part1_c5_old_take.mp3", "旧take(減速前の再検証では合格・6%減速後に不合格となった音声。退避先 cs_audit_01/pre_regen_c5_backup/)")
        + audio_html("audio/a2_full_story_part1_c5_current_disk_attempt6.mp3", "ディスク上の現行wav(attempt6、最小fallback。ASR転写 Mellowset、TTS_FAILURE)")
        + "</details></section>")

    # ---- 要確認2: Adv b1b part1_c5 ----
    e = seg("b1b", "full_story_part1_c5")
    lk = lock("b1b", "full_story_part1_c5")
    steps, ts = queue_steps("b1b", "full_story_part1_c5")
    to_mp3(e["path"], f"{OUT}/audio/b1b_full_story_part1_c5.mp3")
    manifest.append({"level": "b1b", "clip_id": "full_story_part1_c5", "section": "review", "wav": e["path"], "wav_sha256": sha(e["path"]),
                     "mp3": "audio/b1b_full_story_part1_c5.mp3"})
    sections["review"].append(
        "<section class='hr'><h2>要確認 2: Adv(B1b) / full_story_part1_c5 「Melos said.」</h2>"
        + audio_html("audio/b1b_full_story_part1_c5.mp3", "現行clip(Adv、TTS 1回、HR待ち)")
        + f"<p><small>status={esc(e.get('status'))} / review_lock={esc(lk['state'])} / voice={esc(e.get('voice'))} / model={esc(e.get('model_ids_measured'))} / {e.get('duration_seconds')}s</small></p>"
        + f"<table><tr><th>原文(canonical)</th><td>Melos said.</td></tr><tr><th>期待発音</th><td>{esc(EXPECT_EN)}</td></tr></table>"
        + "<h3>全ASR転写</h3>" + steps_table(steps)
        + "<h3>既存機構で自動判断できない理由</h3><ul>"
          "<li>OpenAI=Mello / Azure=Mellow と2系統とも別綴りで、Pattern A(綴り水準)・Equivalence Layer(OOV固有名詞)・Tier3(Azureが Melos と綴ること)のいずれも成立しない(OPEN-327)。</li>"
          "<li>Local Rewrite(別語への言い換え)5候補も7 Gateを全通過せず不採用(Gate7=全面書換でない、を全候補が満たさず。詳細は cs_audit_01/CS_AUDIT_01.md 付録)。</li></ul>"
        + f"<p>{CHECK_NOTE}</p></section>")

    # ---- 要確認3: JA comment_1(ユーザー判断待ち) ----
    e = seg("a2", "comment_1")
    lk = lock("a2", "comment_1")
    to_mp3(e["path"], f"{OUT}/audio/a2_comment_1.mp3")
    manifest.append({"level": "a2", "clip_id": "comment_1", "section": "review", "wav": e["path"], "wav_sha256": sha(e["path"]),
                     "mp3": "audio/a2_comment_1.mp3"})
    rows = "".join(f"<tr><td>{a.get('attempt')}</td><td>{esc(a.get('audio_classification'))}</td><td>{esc(a.get('asr_text'))}</td></tr>" for a in lk["last_attempts_log"])
    sections["review"].append(
        "<section class='hr'><h2>要確認 3: Std(A2・日本語) / comment_1(ユーザー判断待ち)</h2>"
        + audio_html("audio/a2_comment_1.mp3", "現行clip(日本語コメント1)")
        + f"<p><small>status={esc(e.get('status'))} / review_lock={esc(lk['state'])}</small></p>"
        + f"<table><tr><th>原文</th><td>{esc(e['canonical_text'])}</td></tr>"
          "<tr><th>確認点</th><td>「メロス」が正しく読まれているか、ほか原文どおりに読まれているか(attempt2のASR転写は『メオス』、attempt1は『3日間』表記などの差。いずれも TRUE_CONTENT_MISMATCH)。</td></tr></table>"
        + "<h3>全ASR転写(日本語)</h3><table><tr><th>attempt</th><th>分類</th><th>転写</th></tr>" + rows + "</table>"
        + "<p>既存機構で判断できない理由: 日本語Validatorが TRUE_CONTENT_MISMATCH と判定し、標準2回+fallback1回の上限でHR化したため(原因の詳細な切り分けは本委任の範囲外・未調査)。この調査では変更していません。</p></section>")

    # ---- 採用確定: b1b part3_c1 ----
    e = seg("b1b", "full_story_part3_c1")
    to_mp3(e["path"], f"{OUT}/audio/b1b_full_story_part3_c1.mp3")
    manifest.append({"level": "b1b", "clip_id": "full_story_part3_c1", "section": "adopted", "wav": e["path"], "wav_sha256": sha(e["path"]),
                     "mp3": "audio/b1b_full_story_part3_c1.mp3"})
    dev = e["audio_text_deviation"]
    sections["adopted"].append(
        "<section class='ok'><h2>採用確定: Adv(B1b) / full_story_part3_c1(Local Rewrite: Melos drank → He drank)</h2>"
        + audio_html("audio/b1b_full_story_part3_c1.mp3", "現行clip")
        + f"<p><small>status={esc(e['status'])} / review_lock=RESOLVED(OK確定) / {e.get('duration_seconds')}s</small></p>"
        + f"<table><tr><th>差異</th><td>{esc(dev.get('diff_summary'))}</td></tr><tr><th>音声が読む文(Local Rewrite後)</th><td>{esc(dev.get('audio_text_after'))}</td></tr>"
          f"<tr><th>最終ASR転写</th><td>{esc(e['asr_text'])}</td></tr></table>"
        + "<p>He drank への言い換えで固有名詞の連続発音問題を回避し、ASR一致で採用が確定しています。</p></section>")

    # ---- 解決済み: a2 part1_c1 / part3_c3 ----
    for cid in ("full_story_part1_c1", "full_story_part3_c3"):
        e = seg("a2", cid)
        lk = lock("a2", cid)
        mp3 = f"{OUT}/audio/a2_{cid}.mp3"
        to_mp3(e["path"], mp3)
        manifest.append({"level": "a2", "clip_id": cid, "section": "resolved", "wav": e["path"], "wav_sha256": sha(e["path"]), "mp3": f"audio/a2_{cid}.mp3"})
        sections["resolved"].append(
            f"<section class='ok'><h2>解決済み: Std(A2) / {esc(cid)}</h2>"
            + audio_html(f"audio/a2_{cid}.mp3", "現行clip(合格済み)")
            + f"<p><small>status={esc(e['status'])} / review_lock={esc(lk['state'])} / 分類={esc(e['attempts'][-1].get('audio_classification'))} / TTS {e.get('tts_generations_used')}回</small></p>"
            + f"<table><tr><th>原文</th><td>{esc(e['canonical_text'])}</td></tr><tr><th>最終ASR転写(Primary)</th><td>{esc(e['asr_text'])}</td></tr></table>"
            + "<p>OpenAI が Mellos と転写してもAzure が独立に Melos と一致(SECONDARY_ASR_CORROBORATED_MATCH)したため自動合格。参考として掲載します(判断不要)。</p></section>")

    h = ["<!doctype html><meta charset='utf-8'><title>Family Z メロス Human Review試聴 v2</title>",
         "<style>body{font-family:sans-serif;max-width:980px;margin:1em auto;padding:0 1em}table{border-collapse:collapse;margin:.5em 0}"
         "td,th{border:1px solid #999;padding:4px 8px;font-size:14px;vertical-align:top}.hr{background:#fee}.ok{background:#efe}"
         "section{border:1px solid #ccc;padding:.5em 1em;margin:1em 0}code{background:#eee;padding:0 3px}audio{width:100%;max-width:560px}</style>",
         "<h1>Family Z メロス Human Review試聴 (run_e2e_02) v2</h1>",
         "<p>Trial/検証用ページ。Production採用ではありません。採択・override・再生成・HR承認は試聴後にユーザーが判断します(本ページは何も採択しません)。"
         "ASR転写は Primary(OpenAI gpt-4o-mini-transcribe)と Secondary(Azure)。</p>",
         f"<p>要確認 {len(sections['review'])} 件 / 採用確定 {len(sections['adopted'])} 件 / 解決済み {len(sections['resolved'])} 件</p>",
         "<h2 style='border-bottom:3px solid #c33'>要確認(ユーザーの聴感判断待ち)</h2>"] + sections["review"] + \
        ["<h2 style='border-bottom:3px solid #3a3'>採用確定</h2>"] + sections["adopted"] + \
        ["<h2 style='border-bottom:3px solid #3a3'>解決済み(判断不要・参考)</h2>"] + sections["resolved"]
    open(f"{OUT}/hr_review_01.html", "w", encoding="utf-8").write("\n".join(h))
    json.dump(manifest, open(f"{OUT}/hr_items.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps([(m["level"], m["clip_id"], m["section"]) for m in manifest], ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())

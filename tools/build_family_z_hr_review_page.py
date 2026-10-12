# FAMILY-Z-MELOS 委任_12D: Human Review試聴ページ生成(API呼出0、読み取り+mp3変換のみ)
# 対象: HUMAN_REVIEW_REQUIRED(status非OK)の全clip と、Local Rewriteで本文から逸脱したclip(audio_text_deviation)。
# 採択・override・regenerateは行わない(ユーザー試聴後の判断)。
import html
import json
import os
import sys

RUN = "er026_output/family_z_production_e2e_01/melos/run_e2e_02"
OUT = "user_test/family_z_melos_01"
QUEUE = "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl"


def load(p):
    return json.load(open(p, encoding="utf-8"))


def queue_rows():
    rows = []
    for l in open(QUEUE, encoding="utf-8"):
        if "run_e2e_02" in l:
            rows.append(json.loads(l))
    return rows


def main():
    import soundfile as sf
    os.makedirs(f"{OUT}/audio", exist_ok=True)
    qrows = queue_rows()
    items = []
    for lv in ("b1b", "a2"):
        p = f"{RUN}/{lv}/audit/tts_generation_results.json"
        if not os.path.exists(p):
            continue
        d = load(p)
        for cid, e in (d.get("segments") or {}).items():
            hr = e.get("status") != "OK"
            dev = e.get("audio_text_deviation")
            if not (hr or dev):
                continue
            wav = e.get("path") or f"{RUN}/{lv}/narration/{cid}.wav"
            mp3 = f"{OUT}/audio/{lv}_{cid}.mp3"
            if os.path.exists(wav):
                data, sr = sf.read(wav)
                sf.write(mp3, data, sr, format="MP3")
            steps = []
            for r in qrows:
                if r.get("wav_path", "").replace("\\", "/").endswith(f"/{lv}/narration/{cid}.wav"):
                    steps = r.get("steps", [])
            kind = []
            if hr:
                kind.append("HUMAN_REVIEW_REQUIRED")
            if dev:
                kind.append("LOCAL_REWRITE逸脱")
            items.append({"level": lv, "clip_id": cid, "kinds": kind, "status": e.get("status"),
                          "canonical": e.get("canonical_text"), "asr_final": e.get("asr_text"),
                          "dev": dev, "steps": steps, "mp3": f"audio/{lv}_{cid}.mp3",
                          "attempts": [(a.get("attempt"), a.get("audio_classification"), a.get("asr_text")) for a in e.get("attempts", [])],
                          "model": e.get("model_ids_measured"), "voice": e.get("voice"), "duration": e.get("duration_seconds")})
    h = ["<!doctype html><meta charset='utf-8'><title>Family Z メロス Human Review試聴</title>",
         "<style>body{font-family:sans-serif;max-width:960px;margin:1em auto;padding:0 1em}table{border-collapse:collapse;margin:.5em 0}"
         "td,th{border:1px solid #999;padding:4px 8px;font-size:14px;vertical-align:top}.hr{background:#fee}.lr{background:#ffe}"
         "section{border:1px solid #ccc;padding:.5em 1em;margin:1em 0}code{background:#eee;padding:0 3px}</style>",
         "<h1>Family Z メロス Human Review試聴 (run_e2e_02)</h1>",
         "<p>Trial/検証用ページ。Production採用ではありません。採択・override・再生成は試聴後にユーザーが判断します(本ページは何も採択しません)。"
         "ASR転写は Primary(OpenAI gpt-4o-mini-transcribe) と Secondary(Azure)。</p>",
         f"<p>対象 {len(items)} clip</p>"]
    for it in items:
        cls = "hr" if "HUMAN_REVIEW_REQUIRED" in it["kinds"] else "lr"
        h.append(f"<section class='{cls}'><h2>{html.escape(it['level'])} / {html.escape(it['clip_id'])} : {html.escape(' + '.join(it['kinds']))}</h2>")
        h.append(f"<audio controls preload='none' src='{it['mp3']}'></audio> <small>status={html.escape(str(it['status']))} voice={html.escape(str(it['voice']))} "
                 f"model={html.escape(str(it['model']))} {it['duration']}s</small>")
        h.append("<table>")
        h.append(f"<tr><th>原文(canonical)</th><td>{html.escape(it['canonical'] or '')}</td></tr>")
        if it["dev"]:
            h.append(f"<tr><th>Local Rewrite前(原文)</th><td>{html.escape(it['dev'].get('canonical_text_before_local_rewrite') or '')}</td></tr>")
            h.append(f"<tr><th>Local Rewrite後(音声が読む文)</th><td>{html.escape(it['dev'].get('audio_text_after') or '')}</td></tr>")
            h.append(f"<tr><th>差異種別</th><td>{html.escape(it['dev'].get('diff_summary') or '')}</td></tr>")
        h.append(f"<tr><th>最終ASR転写(Primary)</th><td>{html.escape(it['asr_final'] or '')}</td></tr>")
        for st in it["steps"]:
            h.append(f"<tr><th>{html.escape(str(st.get('step')))} ({html.escape(str(st.get('provider')))})</th><td>{html.escape(str(st.get('text')))}"
                     f"<br><small>{html.escape(str(st.get('classification') or st.get('sub_reason') or ''))}</small></td></tr>")
        if it["attempts"]:
            h.append("<tr><th>attempts</th><td>" + "<br>".join(html.escape(f"#{a[0]} {a[1]}: {a[2]}") for a in it["attempts"]) + "</td></tr>")
        h.append("</table></section>")
    open(f"{OUT}/hr_review_01.html", "w", encoding="utf-8").write("\n".join(h))
    json.dump([{k: v for k, v in it.items() if k != "steps"} for it in items], open(f"{OUT}/hr_items.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps([(i["level"], i["clip_id"], i["kinds"]) for i in items], ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())

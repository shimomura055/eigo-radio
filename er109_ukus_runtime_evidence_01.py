# -*- coding: utf-8 -*-
# ============================================================
# er109_ukus_runtime_evidence_01.py  (有料: Gemini TTS + OpenAI Primary ASR + Azure Secondary。1実行=1 segment、上限は委任文で指定)
# ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 ②UKUS 委任_04 §9 X runtime evidence (W-08(1))。
# Family X の『正式TTS段関数 generate_family_x_b1_segments』(= @er109_scope.family_scope("X") decorator付きの本物の入口)を、隔離run_dirの
# 検証用segment text(UK専用綴りを含む。本文・既存runのcanonicalは一切改変しない)で呼ぶ。scope/flagはProduction同一(hook差し替え・monkeypatchなし)。
# Store書込・出力は隔離run_dir配下(共有の追記型ログ[attempt_history等]は本番関数が書く=差分を記録する)。
# 使い方: python er109_ukus_runtime_evidence_01.py --segment full_story_part1 --run-dir er109_output/ukus_prod_01/x_formal_tts_run --out <json>
# 最初に発火(ukus_spelling_variantで受理)した時点で呼出側が停止する(本scriptは1 segmentのみ実行。再実行は委任文の許可範囲内のみ)。
# ============================================================
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

PARTS = {
    # 検証用の短文(UK専用綴りを多く含む)。canonical本文の改変による発火誘導ではなく、隔離run_dirの検証用segment textとして与える(委任文§9)。
    "full_story_part1": "The organisation opened a new centre in the city. Its programme for colour printing began last week.",
    "full_story_part2": "Every Saturday the theatre offers a programme of favourite stories. The centre praised the colourful organisation of the whole neighbourhood.",
    "full_story_part3": "The speciality of the house is a grey jelly with a litre of fibre-rich juice. Her jewellery shop sold aluminium frames.",
}


def prepare(run_dir):
    out = os.path.join(run_dir, "b1b")
    os.makedirs(os.path.join(out, "audit"), exist_ok=True)
    pp = os.path.join(out, "parts.json")
    if not os.path.exists(pp):
        json.dump({"title": "A Test Of Spelling", "part1": PARTS["full_story_part1"], "part2": PARTS["full_story_part2"], "part3": PARTS["full_story_part3"],
                   "in_one_line": "This is a short test line."}, open(pp, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
        json.dump({"preview": "Preview text.", "comment_1": "Comment one.", "comment_2": "Comment two.", "comment_3": "Comment three.", "comment_4": "Comment four."},
                  open(os.path.join(out, "b1_support_texts.json"), "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--segment", required=True, choices=sorted(PARTS))
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    run_dir = os.path.abspath(a.run_dir)
    prepare(run_dir)
    import er005_cost_logger as cl
    cl.init_logger(os.path.join(run_dir, "cost_log.jsonl"))
    import er019_family_x_audio_production_runner_01 as r
    r._ONLY_SEGMENTS = {a.segment}                # --only-segments と同じ(同一module global。CLIがmain()で設定する値)
    summ = {"segment": a.segment, "text": PARTS[a.segment], "run_dir": run_dir, "scope_decorator": getattr(r.generate_family_x_b1_segments, "__er109_scoped__", None)}
    summ["ukus_run_evidence_before"] = None
    # 本物の正式TTS段入口(scope=Xはdecoratorが設定)。scope内のevidenceは別途(scope外では ukus_active=False になる事の確認用)
    summ["ukus_run_evidence_outside_scope"] = r.er109_scope.ukus_run_evidence()
    try:
        res = r.generate_family_x_b1_segments(run_dir, tts_backend="speech_metadata_flash_lite")
        summ["stage_result"] = res
        summ["error"] = None
    except BaseException as exc:  # noqa: BLE001  STOP(HR Lock等)も証跡に残す。再実行しない
        summ["error"] = f"{type(exc).__name__}: {exc}"
    rp = os.path.join(run_dir, "b1b", "audit", "tts_generation_results.json")
    if os.path.exists(rp):
        segs = (json.load(open(rp, encoding="utf-8")).get("segments") or {})
        e = segs.get(a.segment) or {}
        txt = json.dumps(e, ensure_ascii=False)
        oe = ((e.get("asr_judgement") or {}).get("orthographic_equivalence") or {})
        summ["entry"] = {k: e.get(k) for k in ("status", "attempts", "asr_verified", "asr_text", "canonical_text", "final_status", "human_review_required",
                                               "asr_attempts", "sha256", "reuse_value_guard_blocked_previous")}
        summ["asr_judgement_state"] = (e.get("asr_judgement") or {}).get("state")
        summ["asr_judgement_warnings"] = (e.get("asr_judgement") or {}).get("warnings")
        summ["orthographic_equivalence"] = oe
        summ["fired_ukus"] = "ukus_spelling_variant" in txt
        summ["ukus_pairs"] = [p for s in (oe.get("sites") or []) for p in ((s.get("er109") or {}).get("ukus_pairs") or [])]
    cp = os.path.join(run_dir, "cost_log.jsonl")
    if os.path.exists(cp):
        tot = 0.0
        for l in open(cp, encoding="utf-8"):
            try:
                d = json.loads(l)
                tot += float(d.get("cost_jpy") or d.get("estimated_cost_jpy") or 0)
            except Exception:
                pass
        summ["cost_jpy_this_run_dir_cumulative"] = round(tot, 4)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(summ, open(a.out, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1, default=str)
    print(json.dumps({k: summ.get(k) for k in ("segment", "error", "fired_ukus", "asr_judgement_state", "cost_jpy_this_run_dir_cumulative")}, ensure_ascii=False))
    print("saved", a.out)


if __name__ == "__main__":
    main()

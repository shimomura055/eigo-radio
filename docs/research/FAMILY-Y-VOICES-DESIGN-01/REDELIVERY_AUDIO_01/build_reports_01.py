# -*- coding: utf-8 -*-
"""委任_27: COMPARISON_01.md / QA_RESULT_01.md の機械生成部(API 0)。COMPARISONは本文を無編集で並べる。
実行: .venv\\Scripts\\python.exe docs/research/FAMILY-Y-VOICES-DESIGN-01/REDELIVERY_AUDIO_01/build_reports_01.py"""
import json
import os
import re
import sys

sys.path.insert(0, "C:/Users/tensh/eigo-radio")
os.chdir("C:/Users/tensh/eigo-radio")

import er110_family_y_audio_report_01 as rep               # noqa: E402
import er110_family_y_redelivery_audio_01 as rd             # noqa: E402
import er110_family_y_text_trial_01 as y0                   # noqa: E402

OUTD = "docs/research/FAMILY-Y-VOICES-DESIGN-01/REDELIVERY_AUDIO_01"
A = f"{rd.AUDIO_ROOT}/{rd.CAND}"
ROLE = ["リード(語り手・Aoede)", "Voice 1 現役の宅配ドライバー(Algieba)", "Voice 2 共働きの受取人(Zephyr)", "Voice 3 受取方法を工夫している受取人(Schedar)", "Tension+Closing(語り手・Aoede)"]


def rj(p):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def comparison():
    ja = y0.parse_article(open(f"{rd.RD}/y_writer/gate_r0/article_final.md", encoding="utf-8").read())
    adv = y0.split_en_article(open(f"{rd.RD}/english_r0/b1b/article.md", encoding="utf-8").read())
    std = y0.split_en_article(open(f"{rd.RD}/english_r0/a2/article.md", encoding="utf-8").read())
    mp = rj(f"{rd.RD}/english_r0/mapping_check.json")
    md = ["# COMPARISON_01 (委任_27: 日本語R0/5パート原稿 と 英訳Std/Adv の対応表。本文は無編集で転記)\n",
          f"日本語タイトル: {ja['title']} / Adv: {adv['title']} / Std: {std['title']}\n",
          "5パート対応確認(決定論・記録用): " + ("全言語で段落数5・段落2〜4の一人称と固有アンカー・段落1/5が一人称で始まらないことを確認(PASS)" if mp and mp["ok"] else "要確認(下記rows)") + "。`english_r0/mapping_check.json`。\n"]
    for i in range(5):
        md += [f"## パート{i + 1}: {ROLE[i]}\n", "### 日本語(R0無変更+補完)\n", ja["paragraphs"][i] + "\n", "### Advanced(忠実英訳)\n", adv["paragraphs"][i] + "\n",
               "### Standard(A2簡易化)\n", std["paragraphs"][i] + "\n"]
    md += ["## In One Line\n", "### Advanced\n", adv["in_one_line"] + "\n", "### Standard\n", std["in_one_line"] + "\n"]
    open(f"{OUTD}/COMPARISON_01.md", "w", encoding="utf-8", newline="\n").write("\n".join(md) + "\n")


def seg_row(name, e):
    if not e:
        return f"| {name} | (記録なし) | | | | | |"
    rq = e.get("repetition_qa_evidence") or {}
    rq_s = "未実施" if not e.get("repetition_qa_checked") else ("flagged" if rq.get("flagged") else "PASS")
    asr = f"{e.get('audio_classification')}" + ("(asr_verified)" if e.get("asr_verified") else "")
    calls = e.get("call_count") if e.get("call_count") is not None else (len(e.get("attempts_log") or []) or None)
    dur = e.get("duration_seconds") or (e.get("trim_info") or {}).get("trimmed_duration_seconds") or 0
    voice = e.get("voice") or e.get("y_tts_voice_requested") or ""
    flags = []
    if e.get("slowdown_applied"):
        flags.append("6%減速")
    if e.get("fallback_used"):
        flags.append("fallback")
    if e.get("local_rewrite_recovery"):
        flags.append("LocalRewrite")
    if e.get("reused_from_previous_run"):
        flags.append("再利用")
    return f"| {name} | {voice} | {e.get('status')} | {calls}/{e.get('retry_count')} | {asr} | {rq_s} | {' / '.join(flags) or '-'} / {round(dur, 1)}s |"


def qa():
    rep.BASE = rd.AUDIO_ROOT
    summary = rep.build(rd.CAND)
    md = ["# QA_RESULT_01 (委任_27: 再配達音声化Trial 音声QA。正式Gate結果、clip別。API 0)\n",
          f"証跡: `{A}/{{a2,b1b}}/audit/`(tts_generation_results.json・review_lock_state.json・y_style_profile_gate.json・run_summary_assemble.json)、`{A}/audio_qa_summary.json`、`{A}/raw_usage_log.jsonl`。\n",
          "凡例: calls/retry=TTS呼出数/再試行数。ASR=最終ASR照合。Repetition QA=method A+D'。\n"]
    for lvl, lab in (("b1b", "Advanced"), ("a2", "Standard")):
        r = rj(f"{A}/{lvl}/audit/tts_generation_results.json")
        md.append(f"## {lab}\n")
        if not r:
            md.append("(tts_generation_results.json なし)\n")
            continue
        md.append("| segment | Voice | status | calls/retry | ASR | Repetition QA | 備考 |\n|---|---|---|---|---|---|---|")
        for n, e in r["segments"].items():
            md.append(seg_row(n, e))
        for rk, d in sorted((r.get("key_phrases") or {}).items()):
            for role, e in d.items():
                if isinstance(e, dict) and "status" in e:
                    md.append(seg_row(f"kp{rk}_{role}", e))
        md.append("")
        rls = rj(f"{A}/{lvl}/audit/review_lock_state.json")
        held = [n for n, e in (rls or {}).items() if e.get("final_status") != "OK"]
        md.append(f"- Human Review Lock: {'なし(全segment final_status=OK)' if not held else '発火: ' + ', '.join(held)}")
        g = rj(f"{A}/{lvl}/audit/y_style_profile_gate.json")
        md.append(f"- Y style gate(M3+Y追加検査): {g.get('status') if g else '未実行'}")
        s = rj(f"{A}/{lvl}/run_summary_assemble.json")
        if s:
            md.append(f"- Assembly: status={s.get('status')} duration={s.get('duration_seconds')} clipping={s.get('clipping_detected')} peak={s.get('peak')}")
        pw = rj(f"{A}/{lvl}/audit/pass_with_warning_listening_list.json") or {"count": 0, "entries": []}
        md.append(f"- pass_with_warning(読み方の揺れ・非ブロッキング、事後試聴参考): {pw['count']}件 " + ", ".join(e.get("segment_id", "") for e in pw.get("entries", [])))
        lr = [n for n, e in r["segments"].items() if e.get("local_rewrite_recovery")]
        md.append(f"- 局所Rewrite(recovery)発動: {lr or 'なし'}\n")
    md += ["## Voice別実測(F0は自己相関法の簡易推定で、Voice間の相対比較用)\n", "| level | パート | Voice | 長さ(s) | 語数 | 語/分 | F0中央値(Hz) | F0幅(半音) | 重心(Hz) |", "|---|---|---|---|---|---|---|---|---|"]
    for row in rep.voice_table(summary):
        _c, level, seg, role, voice, dur, words, wpm, f0, rng, cen = row
        md.append(f"| {level} | {role} | {voice} | {dur} | {words} | {wpm} | {f0} | {rng} | {cen} |")
    md.append("")
    md.append(f"- 費用(このaudio dirのraw usage log、openai+gemini+azure換算): {summary.get('cost_jpy')} 円 {summary.get('cost_by_provider')}")
    open(f"{OUTD}/QA_RESULT_01.md", "w", encoding="utf-8", newline="\n").write("\n".join(md) + "\n")
    return summary


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd in ("comparison", "all"):
        comparison()
        print("COMPARISON_01 written")
    if cmd in ("qa", "all"):
        s = qa()
        print("QA_RESULT_01 written; cost", s.get("cost_jpy"))

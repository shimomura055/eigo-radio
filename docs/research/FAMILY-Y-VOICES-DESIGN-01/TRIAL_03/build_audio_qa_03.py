# -*- coding: utf-8 -*-
"""TRIAL_03 T-3/T-4: AUDIO_QA_03.md を it3 の audit から決定論的に生成する(API 0)。"""
import json
import os
import sys

sys.path.insert(0, "C:/Users/tensh/eigo-radio")
A = "er110_output/family_y_persona_trial_01/audio/it3"
OUT = "docs/research/FAMILY-Y-VOICES-DESIGN-01/TRIAL_03/AUDIO_QA_03.md"


def rj(p):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def seg_row(name, e):
    if not e:
        return f"| {name} | (記録なし) | | | | | | |"
    rq = e.get("repetition_qa_evidence") or {}
    rq_s = "未実施" if not e.get("repetition_qa_checked") else ("flagged" if rq.get("flagged") else "PASS")
    dis = "実施" if e.get("disfluency_checked") else "-"
    asr = f"{e.get('audio_classification')}" + ("(asr_verified)" if e.get("asr_verified") else "")
    slow = "6%減速" if e.get("slowdown_applied") else "-"
    reuse = "再利用" if e.get("reused_from_previous_run") else "新規生成"
    calls = e.get("call_count") if e.get("call_count") is not None else len(e.get("attempts_log") or []) or None
    dur = e.get("duration_seconds") or (e.get("trim_info") or {}).get("trimmed_duration_seconds") or 0
    voice = e.get("voice") or e.get("y_tts_voice_requested") or ""
    note = "" if voice else "(Master Audio Store再利用[同一phrase/同一voiceの既存検証済みclip]と推定)"
    return (f"| {name} | {voice} | {e.get('status')} | {calls}/{e.get('retry_count')} | "
            f"{asr} | {rq_s} | {dis} | {slow} / fallback={e.get('fallback_used')} / {reuse} / {round(dur, 1)}s {note} |")


V1_SECTION = """## 人物1(V1・Algieba)の停止と原因仮説(Fable報告用)
| level | 試行 | ASR | Repetition QA | 結果 |
|---|---|---|---|---|
| Adv(b1b) | 1 | NORMALIZED_MATCH | method D'(短ラグ)flagged: run長0.62s>=閾値0.6s、time_a 36.53s、lag 0.88s(method D長ラグ・Aは通過) | 再試行 |
| Adv | 2 | NORMALIZED_MATCH | D' flagged: run長0.60s、time_a 37.84s、lag 1.19s | 再試行 |
| Adv | 3 | TRUE_CONTENT_MISMATCH(原稿の「can」[43語目、If I **can** say]をASRが「could」と転写。1語のみの差、Repetition QAは未実施) | - | **HUMAN_REVIEW_REQUIRED / STOPPED**(cumulative_tts_attempts=3、3回で未確定) |
| Std(a2) | 1 | TRUE_CONTENT_MISMATCH(原稿の「it」をASRが「i」と転写。1語のみの差) | - | 再試行 |
| Std | 2 | NORMALIZED_MATCH | D' flagged: run長0.60s、time_a 33.35s、lag 1.79s | 再試行 |
| Std | 3 | NORMALIZED_MATCH(asr_verified) | D' 0.56s(flagなし) | OKだが**minimal_fallback(代替指示)**で生成 -> Y style gate: `FINAL_STYLE_SHA_MISMATCH_NO_HINT`+`STD_FALLBACK_USED_OR_UNKNOWN` -> **BLOCKED_STYLE_PROFILE_GATE**(Std組立不可) |
- 原因仮説(根拠): V1は**6試行(Adv3+Std3)のうち5試行で何らかの停止**(D'境界flag 3回=0.62/0.60/0.60秒、ASRの1語差 2回=can/could・it/i)。他の本文segmentの試行数(cumulative_tts_attempts): Adv V2=1/V3=2/Tension=1、Std V2=2/V3=1/Tension=2(いずれも正式な形で3回以内にOK)で、V1だけが両levelとも正式な形で確定できなかった。D'のflag位置はAdv 36.5〜37.8秒、Std 33.4秒で、語数比の推定では本文の「…I had no answer(for that). **I want** her to… **I don't want** to yell/shout like my father, either.」の区間。V1の英語は「I + 動詞」で始まる短文が3つ連続し(日本語原文「言い返せなかった。決めたことは守ってほしいんだ。うちの親父みたいに怒鳴るのも嫌だ。」の直訳)、同じ音の並び(I / I want / I don't want)がlag 0.9〜1.8秒で繰り返されるため、method D'のスペクトル類似が閾値(0.6秒)の境界で反応したと考える。ASR照合は(1語差を除き)原稿どおり、method A(n-gram)は通過しており、実音声の重複(TTSの言い直し)ではない可能性が高い。OPEN-469と同系の偽陽性。V1は最も長い(Adv 181語/Std 176語、約52〜56秒)ため、1語差や境界flagの機会も多い。Phase B it2のV1もAdvで同系のflag(別の区間=命令文の連続)。
- 修正案(未実施、Fable判断。詳細=V1_REPAIR_PLAN_01.md): 英語V1の「I + 動詞」連続の文頭を言い換えて変化をつけ、ASRで揺れやすい「If I can say, ...」の引用形を避け、V1を短くして(約150語)試行の機会を減らす。V1のみ再生成(両level)。
- 未検証: 実際に聴いて重複でないことの人間確認。区間の特定は語数比による推定(単語タイムスタンプなし)。
- 迂回していない: HR Lock・Y style gate・Repetition QAの閾値は無変更。Adv V1は再生成せず停止、Std V1はfallbackテイクのまま組立を保留。
"""


def main():
    md = ["# AUDIO_QA_03: Trial_03(it3)音声のQA(正式Gate結果、clip別)\n",
          "証跡: `er110_output/family_y_persona_trial_01/audio/it3/{a2,b1b}/audit/`(tts_generation_results.json・review_lock_state.json・y_style_profile_gate.json・run_summary_assemble.json)、"
          "`.../audio/it3/raw_usage_log.jsonl`。すべて**新規生成**(it2の音声は、本文が修正稿と一致しないため再利用しない。見出しのみ同文だが、Voice/style/ASR証跡の再検証を省く利得[約1円]が小さく、再利用判定のリスクに見合わないため新規生成)。",
          "凡例: calls/retry=TTS呼出数/再試行数。ASR=最終ASR照合(EXACT_MATCH/NORMALIZED_MATCH等)。Repetition QA=method A(n-gram)+D'(短ラグ)の結果。\n"]
    for lvl, lab in (("b1b", "Advanced"), ("a2", "Standard")):
        r = rj(f"{A}/{lvl}/audit/tts_generation_results.json")
        md.append(f"## {lab}\n")
        if not r:
            md.append("(tts_generation_results.json なし)\n")
            continue
        md.append("| segment | Voice | status | calls/retry | ASR | Repetition QA | Disfluency | 備考 |\n|---|---|---|---|---|---|---|---|")
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
            md.append(f"- Assembly: status={s.get('status')} duration={s.get('duration_seconds')} clipping={s.get('clipping_detected')} peak={s.get('peak')} out={s.get('out_path')}")
        md.append("")
    md.append(V1_SECTION)
    open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(md) + "\n")
    print("written", OUT)


if __name__ == "__main__":
    main()

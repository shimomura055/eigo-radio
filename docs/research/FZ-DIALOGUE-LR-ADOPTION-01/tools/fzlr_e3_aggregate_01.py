# -*- coding: utf-8 -*-
"""FZ-DIALOGUE-LR-ADOPTION-01 委任_03: E1(自然発火)/E3(注入)のevidence表を実run記録(state/sidecar/cost_log/ledgers)から機械的に生成する(手書き転記を避ける)。"""
import json
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
os.chdir(REPO)
sys.path.insert(0, REPO)
import er019_family_x_audio_production_runner_01 as x  # noqa: E402

ROOT = "er026_output/family_z_production_e2e_01/in_a_grove"
EVD = "docs/research/FZ-DIALOGUE-LR-ADOPTION-01/e3_evidence"
RUNS = [  # (label, run, level, clip, injected)
    ("E1 自然(藪の中Adv c6・実再開)", "run_sf_prod_01", "b1b", "full_story_part3_c6", False),
    ("E3-A Std 6スロット全NG注入(LR実走)", "run_fzlr_ev_a2_05", "a2", "full_story_part1_c6", True),
    ("E3-B Adv ①〜③NG注入→LR→④実判定PASS(+kill/resume)", "run_fzlr_ev_b1b_01", "b1b", "full_story_part2_c1", True),
    ("E3-C Std LR不可(偽T2・是正前)", "run_fzlr_ev_a2_01", "a2", "full_story_part2_c1", True),
    ("E3-D Std LR候補全滅(LR発動・7Gate全不合格)", "run_fzlr_ev_a2_04", "a2", "full_story_part1_c1", True),
]


def rj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def rjl(p):
    if not os.path.exists(p):
        return []
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def cost(run):
    return round(x.compute_cost_jpy_so_far(f"{ROOT}/{run}/cost_log.jsonl")[0], 3)


out = []
for label, run, lv, clip, inj in RUNS:
    st = rj(f"{ROOT}/{run}/{lv}/audit/dialogue_ctx_attempt_state.json")["clips"][clip]
    lk = (rj(f"{ROOT}/{run}/{lv}/audit/review_lock_state.json")).get(clip) or {}
    out.append(f"### {label} — `{run}/{lv}/{clip}`" + (" (全判定注入=INJECTED、品質根拠にしない)" if inj else ""))
    out.append(f"status={st['status']} / phase={st.get('phase')} / n_started={st['n_started']} / LR.state={(st.get('lr') or {}).get('state')} "
               f"({(st.get('lr') or {}).get('outcome_status')}) / Lock={lk.get('state')} cumulative_tts={lk.get('cumulative_tts_attempts')} / 費用(この run の cost_log)=¥{cost(run)}")
    out.append("")
    out.append("| n | block/ordinal | mode | 開始-終了 | verified | ASR判定 | 備考(Style sha/Voice/model) |")
    out.append("|---|---|---|---|---|---|---|")
    side = {}
    ad = f"{ROOT}/{run}/{lv}/narration/attempts"
    for fn in sorted(os.listdir(ad)) if os.path.isdir(ad) else []:
        if fn.startswith(clip + "_") and fn.endswith(".json"):
            j = rj(f"{ad}/{fn}")
            side[j.get("overall_attempt_n")] = j
    for a in st["attempts"]:
        r0 = (a.get("log_rows") or [{}])[0]
        j = side.get(a["n"]) or {}
        asr = (r0.get("asr_judgement") or {}).get("state")
        rep = (r0.get("repetition_qa_evidence") or {}).get("flagged")
        note = f"style={((a.get('log_rows') or [{}])[0].get('style_prefix') or {}).get('sha256', '-')[:8]} voice={j.get('voice')} model={j.get('model')}" + (f" rep_flag={rep}" if rep is not None else "")
        out.append(f"| {a['n']} | {a.get('block', 0)}/{a.get('ordinal', a['n'])} | {a.get('mode')} | {a.get('started_at', '')[11:19]}-{a.get('finished_at', '')[11:19]} | {a.get('verified')} | {asr} | {note} |")
    lr = st.get("lr") or {}
    if lr.get("audit"):
        sel = lr["audit"].get("selected") or {}
        out.append("")
        out.append(f"LR Before→After: `{sel.get('changed_span_before')}` → `{sel.get('changed_span_after')}` / 7Gate全PASS={sel.get('all_seven_gates_pass')} / 入力=#{(lr.get('input') or {}).get('n')} {(lr.get('input') or {}).get('source')} / skipped={json.dumps((lr.get('input') or {}).get('skipped'), ensure_ascii=False)[:300]}")
    elif lr.get("input"):
        out.append("")
        out.append(f"LR入力: {json.dumps(lr['input'], ensure_ascii=False)[:500]}")
    cds = st.get("cooldowns") or {}
    out.append("")
    out.append("待機(`cooldowns`): " + "; ".join(f"n<{k}: 要求{v.get('requested_seconds')}s / 開始{v.get('started_at', '')[11:19]} 終了{v.get('ended_at', '')[11:19]} / このprocess内待機{v.get('waited_seconds_this_process')}s / resumed={v.get('resumed')} / process_starts={v.get('process_starts')}" for k, v in cds.items()))
    if run != "run_sf_prod_01":
        led = f"{EVD}/{run}/ledgers"
        out.append(f"HRQ行(隔離台帳)={len(rjl(led + '/human_review_queue.jsonl'))} / 隔離attempt_history行={len(rjl(led + '/attempt_history.jsonl'))}")
        inj_files = sorted(f for f in os.listdir(f"{EVD}/{run}") if f.startswith("injection_") and f.endswith(".jsonl"))
        n_inj = sum(len(rjl(f"{EVD}/{run}/{f}")) for f in inj_files)
        n_all = sum(1 for f in inj_files for r in rjl(f"{EVD}/{run}/{f}") if r.get("INJECTED") is True)
        out.append(f"注入記録={n_inj}行(うちINJECTED=true {n_all}行) / kill記録={[f for f in os.listdir(f'{EVD}/{run}') if f.startswith('kill_')]}")
    out.append("")
print("\n".join(out))

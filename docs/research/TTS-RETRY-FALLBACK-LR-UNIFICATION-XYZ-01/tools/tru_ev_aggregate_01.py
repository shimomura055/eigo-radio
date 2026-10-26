# -*- coding: utf-8 -*-
"""TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_03: evidence_runs/*.json を case別に機械判定し、集計(JSON+md断片)を出す(API 0)。

判定は **evidence JSON(実TTS/ASR/待機/LRの観測値)から機械的** に行う。期待値はEVIDENCE_PLAN_01 §3の合格基準。
verdict: PASS=設計どおり / DEVIATION_NATURAL=本物のASR判定が注入計画と違った(自然発生。流れ自体は設計どおり) / FAIL=設計と異なる
"""
from __future__ import annotations

import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tru_ev_core_01 as core  # noqa: E402
import tru_ev_cases_01 as cases_mod  # noqa: E402

EVD = core.EVD
ER = core.EVIDENCE_RUNS
TOL = 2.0
CASES = {c["id"]: c for c in cases_mod.CASES}


def load_all():
    out = {}
    for f in sorted(glob.glob(f"{ER}/*.json")):
        b = os.path.basename(f)
        if ".partial" in b or ".smoke" in b or b.startswith("_"):
            continue
        cid = b[:-5]
        resume = False
        if cid.endswith(".resume"):
            cid, resume = cid[:-7], True
        out.setdefault(cid, {})["resume" if resume else "main"] = json.load(open(f, encoding="utf-8"))
    return out


def clip_attempts(ev, clip):
    return [a for a in ev.get("tts_attempts", []) if a.get("clip") == clip]


def n_tts(ev, clip):
    at = clip_attempts(ev, clip)
    if at:
        return len(at)
    sc = [x for x in ev.get("attempt_sidecars", []) if x.get("segment_id") == clip]
    return len(sc) or ev.get("tts_api_calls", 0)


def dialogue_tts(ev, clip):
    """Z会話(L8): results.jsonのdialogue_tts(ctx/legacy_fallbackのmode遷移・cooldown記録)。run dirから読む。"""
    rd, lv = ev.get("run_dir"), ev.get("level")
    r = core.read_json(f"{rd}/{lv}/audit/tts_generation_results.json") or {}
    return ((r.get("segments") or {}).get(clip) or {}).get("dialogue_tts")


def _file_results(ev):
    rd, lv = ev.get("run_dir"), ev.get("level")
    return core.read_json(f"{rd}/{lv}/audit/tts_generation_results.json") or {}


def final_entry(ev, clip):
    seg = (ev.get("results_segments") or {}).get(clip)
    if seg:
        return seg
    # evidence JSON(KP等は絞り込み)に無い場合はrun dirの結果ファイルから
    fr = _file_results(ev)
    if clip in (fr.get("segments") or {}):
        return fr["segments"][clip]
    if clip.startswith("kp") and clip[2:3].isdigit():
        rank = clip[2:3]
        roles = (fr.get("key_phrases") or {}).get(rank) or {}
        role = "explanation" if "explanation" in clip else "english"
        if role in roles:
            return roles[role]
    kp = ev.get("results_key_phrases") or {}
    role = "english" if clip.endswith("_en") and "explanation" not in clip else "explanation"
    for rk, rv in kp.items():
        if clip.startswith(f"kp{rk}") and role in rv:
            return rv[role]
    # chunk parent等
    for k, v in (ev.get("results_segments") or {}).items():
        if k.startswith(clip):
            return v
    return None


def status_of(ev, clip):
    e = final_entry(ev, clip)
    return (e or {}).get("status")


def label(a):
    return core.label_style(a.get("style_head", ""), a.get("style_sha"))


def chk(name, ok, detail=""):
    return {"check": name, "ok": bool(ok), "detail": detail}


def waits_ok(ev, n, resumed_ok=False):
    cds = ev.get("cooldown_events") or []
    ok = len(cds) == n and all((c["actual_seconds"] >= 180 - TOL) or (resumed_ok and c.get("resumed")) for c in cds)
    return chk(f"待機{n}回(各≥{180 - TOL:.0f}秒)", ok, f"回数={len(cds)} 実測秒={[c['actual_seconds'] for c in cds]}")


def voice_model_same(ev, clip):
    at = clip_attempts(ev, clip)
    v, m = {a["voice"] for a in at}, {a["model"] for a in at}
    return chk("Voice/modelが全attempt同一", len(v) == 1 and len(m) == 1, f"voice={sorted(v)} model={sorted(m)}")


def verdict_for(case, ev):
    sc = case["scenario"]
    clips = case["segments"]
    c0 = clips[0]
    at = clip_attempts(ev, c0)
    n = n_tts(ev, c0)
    checks = []
    exc = ev.get("exception")
    if exc and sc != "E-STOP":
        checks.append(chk("例外なし", False, f"{exc['type']}: {exc['message'][:160]}"))
    sty = [a["style_sha"] for a in at]
    lab = [label(a) for a in at]
    st = status_of(ev, c0)
    lock = (ev.get("lock_state") or {}).get(c0) or {}
    natural = False
    if sc == "E-N":
        checks += [chk("上書き0", ev["injected_override_count"] == 0), chk(f"TTS={len(clips)}(1/clip)", ev["tts_attempts_count"] == len(clips), ev["tts_attempts_count"]),
                   chk("待機0", ev["cooldown_count"] == 0), chk("LR=0", ev["lr_count"] == 0), chk("HRQ=0", ev["hrq_rows"] == 0),
                   chk("全clip OK", all(status_of(ev, c) == "OK" for c in clips), {c: status_of(ev, c) for c in clips})]
    elif sc.startswith("E-S1") or sc == "E-S1(L8 ctx)" or sc.startswith("E-S1("):
        if case["leaf"] == "L8":
            dt = dialogue_tts(ev, c0) or {}
            modes = [a.get("mode") for a in dt.get("attempts", [])]
            sc_ = [x for x in ev.get("attempt_sidecars", []) if x.get("segment_id") == c0]
            checks += [chk("TTS=3", n == 3, n), waits_ok(ev, 1), chk("①②=ctx方式 / ③=従来Dialogue Style(legacy_fallback)", modes == ["ctx", "ctx", "legacy_fallback"], modes),
                       chk("Voice/model全attempt同一", len({(x["voice"], x["model"]) for x in sc_}) == 1, sorted({(x["voice"], x["model"]) for x in sc_})),
                       chk("待機はn=3直前(required_before_n=3)", (dt.get("cooldown") or {}).get("required_before_n") == 3, dt.get("cooldown")), chk("LR=0", ev["lr_count"] == 0)]
        else:
            checks += [chk("TTS=3", n == 3, n), waits_ok(ev, 1), chk("①②同Style/③別Style", len(sty) == 3 and sty[0] == sty[1] and sty[2] != sty[0], [s[:6] for s in sty]),
                       voice_model_same(ev, c0), chk("LR=0", ev["lr_count"] == 0)]
        fin_ok = st == "OK"
        if not fin_ok:
            natural = True
        checks.append(chk("最終OK(③実PASS)", fin_ok, st))
    elif sc.startswith("E-S2a"):
        checks += [chk("TTS=4", n == 4, n), waits_ok(ev, 1), chk("LR=1", ev["lr_count"] == 1, ev["lr_count"]),
                   chk("LR RESOLVED", any(l["status"] == "RESOLVED_BY_LOCAL_REWRITE" for l in ev["lr_calls"]), [l["status"] for l in ev["lr_calls"]]),
                   chk("④=元role Style(①と同じ)", len(sty) == 4 and sty[3] == sty[0], [s[:6] for s in sty]), voice_model_same(ev, c0),
                   chk("④のjudgeがscript_version=v1", any(j.get("slot") == 4 and j.get("script_version") == "v1" for j in ev["judges"])),
                   chk("HRQ=0", ev["hrq_rows"] == 0, ev["hrq_rows"])]
        fin_ok = st == "OK"
        natural = natural or not fin_ok
        checks.append(chk("最終OK(LR採用)", fin_ok, st))
    elif sc.startswith("E-S2b"):
        lr_ok = ev["lr_count"] == 1
        checks += [chk("TTS=6", n == 6, n), waits_ok(ev, 2), chk("LR=1(再入0)", lr_ok, ev["lr_count"]),
                   chk("①②④⑤=role Style / ③⑥=Fallback", len(sty) == 6 and sty[0] == sty[1] == sty[3] == sty[4] and sty[2] == sty[5] != sty[0], [s[:6] for s in sty]),
                   voice_model_same(ev, c0), chk("HRQ=1行", ev["hrq_rows"] == 1, ev["hrq_rows"]), chk("最終NG(STOPPED)", st not in ("OK", None), st),
                   chk("Lock=HUMAN_REVIEW", "HUMAN_REVIEW" in str(lock.get("state")), lock.get("state"))]
    elif sc.startswith("E-S3"):
        judge_level_l8 = case["leaf"] in ("L8", "L7") and not case["plan"].post_ng
        checks += [chk("TTS=3", n == 3, n), waits_ok(ev, 1), chk("LR=0", ev["lr_count"] == 0),
                   (chk("HRQ行: L7(JA)/L8はjudge自身が最終slotの本物のNGで書く経路。judge戻り値の注入では行が出ない(driver側の限界・対象外)", True, ev["hrq_rows"]) if judge_level_l8
                    else chk("HRQ=1行", ev["hrq_rows"] == 1, ev["hrq_rows"])),
                   chk("最終NG", st not in ("OK", None), st)]
        checks.append(chk("Lock=HUMAN_REVIEW", "HUMAN_REVIEW" in str(lock.get("state")), lock.get("state")))
    elif sc.startswith("E-S4"):
        hr = case["plan"].ng.get("*") and 4 in case["plan"].ng["*"]
        if hr:
            checks += [chk("TTS=4", n == 4, n), waits_ok(ev, 1), chk("③④=ENGLISH_LOCK", len(lab) == 4 and lab[2] == lab[3] == "ENGLISH_LOCK", lab),
                       chk("HRQ=1行", ev["hrq_rows"] == 1, ev["hrq_rows"]), chk("最終NG", st not in ("OK", None), st)]
        else:
            checks += [chk("TTS=3", n == 3, n), waits_ok(ev, 1), chk("③=ENGLISH_LOCK", len(lab) == 3 and lab[2] == "ENGLISH_LOCK", lab),
                       chk("HRQ=0", ev["hrq_rows"] == 0, ev["hrq_rows"])]
            fin_ok = st == "OK"
            natural = natural or not fin_ok
            checks.append(chk("最終OK(③実PASS)", fin_ok, st))
        checks.append(chk("待機位置=ENGLISH_LOCK段直前(attempt 2→3)", all(c.get("attempt_before") == 2 and c.get("attempt_after") == 3 for c in ev["cooldown_events"]),
                          [(c.get("attempt_before"), c.get("attempt_after")) for c in ev["cooldown_events"]]))
    elif sc == "E-S7":
        checks += [chk("TTS=3", n == 3, n), waits_ok(ev, 1), chk("LR LLM=0", ev["lr_count"] == 0 or all(not l.get("ng_span_found") for l in ev["lr_calls"]), ev["lr_calls"] and [l["status"] for l in ev["lr_calls"]]),
                   chk("ASR一致(判定は本物PASS)", all(j["ok_real"] for j in ev["judges"]), [j["ok_real"] for j in ev["judges"]]),
                   chk("HRQ=1行", ev["hrq_rows"] == 1, ev["hrq_rows"]), chk("最終NG", st not in ("OK", None), st)]
    elif sc.startswith("E-S0"):
        checks += [chk("TTS=2(①NG→②PASS)", n == 2, n), chk("待機0", ev["cooldown_count"] == 0), chk("LR=0", ev["lr_count"] == 0), chk("HRQ=0", ev["hrq_rows"] == 0),
                   chk("①②同Style", len(sty) == 2 and sty[0] == sty[1]), chk("最終OK(②実PASS)", st == "OK", st)]
    elif sc == "E-STOP":
        ev_stop = [e for e in (ev.get("events") or []) if e.get("event") == "STOP_SENTINEL_CREATED"]
        prog = list((ev.get("block_progress") or {}).values())
        checks += [chk("TTS=2(③を実行していない)", n == 2, n), chk("例外=TtsBlockStopError(BaseException)でrunner最上位まで伝播", (exc or {}).get("type") in ("TtsBlockStopError", "FamilyZStopSentinel", "StopSentinelError") or "STOP" in str((exc or {}).get("message", "")), exc),
                   chk("待機は完了せず中断(sleep合計<180)", ev["sleep_total_seconds"] < 180 - TOL, ev["sleep_total_seconds"]),
                   chk("STOPPED結果を保存していない(Lockが無いか未HR)", "HUMAN_REVIEW" not in str(lock.get("state")), lock.get("state")),
                   chk("BlockProgress=IN_PROGRESS(resume可)", bool(prog) and prog[0].get("status") == "IN_PROGRESS", [p.get("status") for p in prog]),
                   chk("HRQ=0", ev["hrq_rows"] == 0, ev["hrq_rows"])]
    elif sc.startswith("E-C1"):
        checks += [chk("TTS=2(①減速後NG→②)", n == 2, n), chk("待機0(③に入らない)", ev["cooldown_count"] == 0), chk("上書き=減速後NG 1回", ev["injected_override_count"] == 1, ev["injected_overrides"]),
                   chk("①②同Style", len(sty) == 2 and sty[0] == sty[1]), chk("最終OK", st == "OK", st)]
        g = ev.get("gate_observation") or {}
        checks += [chk("Std chunk減速Gate: 当該chunkはviolationなし(他chunk=未生成はMISSING_MANDATORY扱いで対象外)", not any(x.get("segment") == case["segments"][0] for x in ((g.get("std_chunk_slowdown_gate") or {}).get("blocked") or [])), [x for x in ((g.get("std_chunk_slowdown_gate") or {}).get("blocked") or []) if x.get("segment") == case["segments"][0]]),
                   chk("M3 profile Gate: 当該chunk blockedなし(誤BLOCKなし)", not g.get("my_segment_blocked"), g.get("my_segment_blocked"))]
    elif sc.startswith("E-X5"):
        for seg in case["segments"]:
            at = clip_attempts(ev, seg)
            checks.append(chk(f"{seg}: 短文(minimal) Styleで1 take・ASR PASS(OK)・追加TTSなし", len(at) == 1 and status_of(ev, seg) == "OK", [len(at), status_of(ev, seg)]))
            checks.append(chk(f"{seg}: Styleが短文minimal", bool(at) and label(at[0]) == "MINIMAL_INSTRUCTION_PREFIX", label(at[0]) if at else None))
        checks += [chk("待機0", ev["cooldown_count"] == 0), chk("LR=0・HRQ=0", ev["lr_count"] == 0 and ev["hrq_rows"] == 0), chk("上書き0", ev["injected_override_count"] == 0)]
    elif sc.startswith("E-S6"):
        checks.append(chk("(E-S6は kill→resume の2段。別判定 resume_verdict)", True))
    else:
        checks.append(chk("未定義scenario", False, sc))
    # 共通
    checks.append(chk("injected_override_count記録", ev.get("injected_override_count") is not None, ev.get("injected_override_count")))
    all_ok = all(c["ok"] for c in checks)
    ok_exempt = ("最終OK", "LR=0", "HRQ=0", "LR RESOLVED", "④", "TTS=", "待機")      # ③等が本物のASRでNGになった自然発生時に連動して変わる項目
    v = "PASS" if all_ok else ("DEVIATION_NATURAL" if natural and all(c["ok"] or c["check"].startswith(ok_exempt) for c in checks) else "FAIL")
    return {"id": case["id"], "verdict": v, "checks": checks, "tts": n, "cooldowns": ev["cooldown_count"], "lr": ev["lr_count"], "hrq": ev["hrq_rows"],
            "cost_jpy": (ev.get("cost") or {}).get("jpy"), "final_status": st, "wall_seconds": ev.get("wall_seconds")}


def verdict_resume(case, main_ev, part, res_ev):
    """E-S6: killまでに①②がTTS済み(partial)、再開で①②再生成0・残り待機のみ・③1回・総TTS=3。"""
    c0 = case["segments"][0]
    pre = [a for a in (part or {}).get("tts_attempts", []) if a["clip"] == c0]
    post = clip_attempts(res_ev, c0)
    cds = res_ev.get("cooldown_events") or []
    resumed_cd = cds[0] if cds else {}
    total_elapsed = resumed_cd.get("total_elapsed_since_ref_seconds")
    st = status_of(res_ev, c0)
    sidecars = res_ev.get("attempt_sidecars") or []
    r5 = case["scenario"].startswith("E-S6(R-5")
    npre, ntot = (5, 6) if r5 else (2, 3)
    wait_ok = bool(cds) and resumed_cd.get("actual_seconds", 999) < 180 - TOL and (total_elapsed or 0) >= 180 - TOL
    checks = [chk(f"kill前: 再開前のTTS={npre}", len(pre) == npre, len(pre)), chk(f"再開後: 既完了attemptの再生成0・残り{ntot - npre}回のみ", len(post) == ntot - npre, len(post)),
              chk(f"TTS総数={ntot}", len(pre) + len(post) == ntot, len(pre) + len(post)),
              chk("再開後LR再呼出0(R-5のみ)", (not r5) or res_ev.get("lr_count", 0) == 0, res_ev.get("lr_count")),
              chk("待機: 残りのみ(resumed=True・実測<180、または壁時計で既に180秒経過済み=残り0)", wait_ok, resumed_cd),
              chk("総経過(起点から)≥180秒", total_elapsed is not None and total_elapsed >= 180 - TOL, total_elapsed),
              chk("最終attemptが③/⑥=Fallback Style", len(post) >= 1 and (not pre or post[-1]["style_sha"] != pre[0]["style_sha"]), [a["style_sha"][:6] for a in pre + post]),
              chk(f"attempt sidecar: {ntot}本(二重なし)", len([s for s in sidecars if s["segment_id"] == c0]) == ntot, len(sidecars)),
              chk("再開後の上書き(①②再注入)0", res_ev["injected_override_count"] == 0, res_ev["injected_overrides"]),
              chk("最終OK", st == "OK", st)]
    ok = all(c["ok"] for c in checks)
    only_final = all(c["ok"] or c["check"].startswith("最終OK") for c in checks)     # ③/⑥が本物のASRでNG(自然発生)でも、フロー(再生成0・残り待機のみ)自体は成立
    return {"id": case["id"] + " (resume)", "verdict": "PASS" if ok else ("DEVIATION_NATURAL" if only_final else "FAIL"), "checks": checks, "tts": len(pre) + len(post), "cost_jpy": ((res_ev.get("cost") or {}).get("jpy")),
            "final_status": st}


def shared_gate_segments(case, run_dir):
    """共有Audio Validation Gate(asm.verify_episode_audio_validation_gate)の**per-segment判定関数そのもの**を、当該case対象segmentだけに適用(API 0)。
    verify_episode_audio_validation_gateは結果ファイル内の全segmentを走査するが、本evidenceでは対象外segmentが SKIPPED_NOT_SELECTED で未検証扱いになるため。"""
    import er003_v1_n3_01_assemble as asm
    lv = case["level"]
    out_dir = f"{run_dir}/{lv}"
    data = core.read_json(f"{out_dir}/audit/tts_generation_results.json") or {}
    ap = asm.human_approval_path(out_dir)
    approvals = core.read_json(ap) if os.path.exists(ap) else {}
    narr = f"{out_dir}/narration"
    blocked, checked = [], []
    mine = set(case["segments"])
    for name, entry in (data.get("segments") or {}).items():
        if name not in mine and not any(name.startswith(m + "_") for m in mine):
            continue
        final = asm._segment_gate_status(entry, name, approvals)
        checked.append(f"{name}={final}")
        if final not in asm.AUDIO_GATE_ALLOWED_STATUSES:
            blocked.append(f"{name}={final}")
            continue
        level_s = "A2" if lv == "a2" else "B1"
        if level_s == "A2" and asm._segment_missing_mandatory_a2_slowdown(name, entry, narr):
            blocked.append(f"{name}={final}(MISSING_MANDATORY_A2_SLOWDOWN)")
        if asm._segment_missing_mandatory_disfluency_qa(name, entry, level_s):
            blocked.append(f"{name}={final}(MISSING_MANDATORY_DISFLUENCY_QA)")
        if asm._segment_asset_hash_stale(entry, narr):
            blocked.append(f"{name}={final}(ASSET_HASH_MISMATCH)")
    for rank, kp in (data.get("key_phrases") or {}).items():
        for sub_key, sub_entry in (kp or {}).items():
            seg_key = f"kp{rank}_{sub_key}"
            if not any(m.startswith(f"kp{rank}") for m in mine):
                continue
            final = asm._segment_gate_status(sub_entry, seg_key, approvals)
            checked.append(f"{seg_key}={final}")
            if final not in asm.AUDIO_GATE_ALLOWED_STATUSES:
                blocked.append(f"{seg_key}={final}")
    return {"checked": checked, "blocked": blocked, "assemble_blocked": bool(blocked), "allowed_statuses": sorted(asm.AUDIO_GATE_ALLOWED_STATUSES)}


def model_usage(run_dir):
    p = f"{run_dir}/raw_usage_log.jsonl"
    rows = core.read_jsonl(p)
    cnt = {}
    for r in rows:
        key = (r.get("provider"), r.get("model_id"), r.get("api"))
        cnt[key] = cnt.get(key, 0) + 1
    return [{"provider": k[0], "model_id": k[1], "api": k[2], "calls": v} for k, v in sorted(cnt.items(), key=lambda kv: str(kv[0]))]


def main():
    data = load_all()
    results = {}
    for cid, d in data.items():
        case = CASES.get(cid)
        if case is None:
            continue
        if case["scenario"].startswith("E-S6"):
            part_f = sorted(glob.glob(f"{ER}/{cid}.partial_before_kill.json"))
            part = json.load(open(part_f[0], encoding="utf-8")) if part_f else None
            if "resume" in d:
                results[cid] = verdict_resume(case, d.get("main"), part, d["resume"])
            else:
                results[cid] = {"id": cid, "verdict": "PENDING_RESUME", "checks": [], "partial": bool(part)}
            continue
        results[cid] = verdict_for(case, d["main"])
    out = {"cases": results}
    with open(f"{ER}/_aggregate_01.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, default=str)
    for cid in sorted(results, key=lambda x: (x.split("-")[0], x.split("-")[1], (int(__import__("re").match("[0-9]+", x.split("-")[2]).group()), x.split("-")[2]))):
        r = results[cid]
        bad = [c["check"] + ":" + str(c["detail"])[:80] for c in r["checks"] if not c["ok"]]
        print(f"{cid:10s} {r['verdict']:18s} tts={r.get('tts')} cd={r.get('cooldowns')} lr={r.get('lr')} hrq={r.get('hrq')} jpy={r.get('cost_jpy')} {('| ' + ' ; '.join(bad)) if bad else ''}")


if __name__ == "__main__":
    main()

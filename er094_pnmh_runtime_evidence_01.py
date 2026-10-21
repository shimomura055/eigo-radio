# -*- coding: utf-8 -*-
"""PNMH-01 A-2: 多語同音救済(L1)のFamily X/Z Production関数 発火証拠 runner。

mode=api0 : TTSとASR(Primary=OpenAI / Secondary=Azure)の取得seamだけを差替え(synthetic wav + 保存転写)。Production関数・
            Validator・unified judge・cascade・review_lock・retry loopは実コード。ネットワークguardで外部通信0を機械確認。
mode=paid : 実TTS/実ASR(Meterで費用計測)。専用run_id・隔離出力dir。
共有state(attempt_history/HR queue/store/cost log/ledger)はer077 apply_isolationでout dir配下へ隔離(Production file無編集)。
使い方: .venv/Scripts/python.exe er094_pnmh_runtime_evidence_01.py api0 [scenario ...]
"""
from __future__ import annotations

import json
import os
import socket
import sys
import time
import traceback

import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

import er078_auw_runtime_evidence_06 as e6
import er078_auw_runtime_evidence_06b as e6b

MODE = sys.argv[1] if len(sys.argv) > 1 else "api0"
if os.environ.get("PNMH_WATCHDOG"):   # 無限待ち防止(診断用。api0のみ)
    import faulthandler
    faulthandler.dump_traceback_later(int(os.environ["PNMH_WATCHDOG"]), exit=True)
EV = "er094_output/pnmh_prod_wiring_01/runtime_" + MODE
FL = "speech_metadata_flash_lite"

STATE = {"primary": [], "secondary": [], "p_calls": [], "s_calls": [], "net_attempts": [], "tts_calls": 0, "observed": []}


# ------------------------------------------------------------------ api0 stubs
def _synthetic_pcm(seconds=3.0, sr=24000):
    t = np.arange(int(seconds * sr)) / sr
    env = np.where((t > 0.4) & (t < seconds - 0.4), 1.0, 0.0)
    sig = 0.25 * env * (np.sin(2 * np.pi * 180 * t) + 0.5 * np.sin(2 * np.pi * 360 * t)) * (0.6 + 0.4 * np.sin(2 * np.pi * 3 * t))
    return (np.clip(sig, -1, 1) * 32767).astype(np.int16).tobytes()


def install_api0_stubs():
    import er002_common as common
    import er006_asr_provider_routing_01 as routing
    import er006_secondary_asr_01 as sec
    import er008_disfluency_qa_18 as dq18
    import er011_open121_repetition_qa_production_01 as rq

    def fake_tts(call_fn, prompt, max_retry, sleep_fn):
        STATE["tts_calls"] += 1
        return common.normalize_pcm(_synthetic_pcm()), 0, True, None
    common._call_tts_with_retry = fake_tts

    def pop(q, calls, wav, kind):
        if not q:
            raise AssertionError(f"scripted {kind} transcript queue exhausted")
        item = q.pop(0) if len(q) > 1 else q[0]
        calls.append({"wav": os.path.basename(wav), "text": item})
        return item

    def fake_primary(wav_path, *a, **k):
        return pop(STATE["primary"], STATE["p_calls"], wav_path, "primary"), None
    routing.transcribe = fake_primary

    def fake_azure(wav, *a, **k):
        return pop(STATE["secondary"], STATE["s_calls"], wav, "secondary"), None
    sec.get_full_text_via_azure_stt_with_phrase_list = fake_azure

    # 下流の局所モデルQA(ASR判定の対象外)は非flagの固定応答にする(合成音声に局所Whisperを走らせない)
    dq18.check_segment_for_disfluency = lambda *a, **k: {"flagged": False, "stub": "api0_not_under_test"}
    rq.evaluate_repetition_qa = lambda *a, **k: {"flagged": False, "stub": "api0_not_under_test"}
    time.sleep = lambda s: None   # 待機のみ即時化(判定へ影響なし)
    import er020_tts_retry_local_rewrite_01 as rp   # cool-down(固定10分)の待機だけ即時化。def時束縛のsleep_fn既定値を差替え(api0のみ)
    rp.maybe_cooldown_before_attempt.__defaults__ = (lambda s: None, rp.COOLDOWN_SECONDS)

    # ネットワーク guard: 外部通信が起きたら記録して失敗させる
    def guard_connect(self, address):
        STATE["net_attempts"].append(str(address))
        raise OSError(f"[api0 guard] network blocked: {address}")
    socket.socket.connect = guard_connect

    def guard_cc(address, *a, **k):
        STATE["net_attempts"].append(str(address))
        raise OSError(f"[api0 guard] network blocked: {address}")
    socket.create_connection = guard_cc


def install_observer():
    """sec.evaluate_attempt_with_cascade_detail(全呼出の最内層。evaluate_attempt_with_cascade[_wrapper]もここ経由)を観測のみでラップ。
    引数・戻り値・判定は無変更。減速後再検証(n3_01:144)などdetailを直接呼ぶ経路も記録される。"""
    import er006_secondary_asr_01 as sec
    orig = sec.evaluate_attempt_with_cascade_detail

    def obs(canonical_text, asr_text, prior_results, wav_path, *a, **k):
        d = orig(canonical_text, asr_text, prior_results, wav_path, *a, **k)
        steps = d.get("steps") or []
        aj = d.get("asr_judgement") or {}
        STATE["observed"].append({
            "wav": os.path.basename(str(wav_path)), "force_secondary": bool(k.get("force_secondary")),
            "primary_text": asr_text, "verified": bool(d.get("verified")), "classification": getattr(d.get("classification"), "classification", None),
            "judge_state": aj.get("state"), "primary_label": (aj.get("primary") or {}).get("label") if isinstance(aj.get("primary"), dict) else None,
            "steps": [{"step": st.get("step"), "text": st.get("text"), "classification": st.get("classification"),
                       "multiword_homophone_spans": st.get("multiword_homophone_spans")} for st in steps]})
        return d
    sec.evaluate_attempt_with_cascade_detail = obs


def setup(out):
    os.makedirs(out, exist_ok=True)
    r77, before, iso = e6.isolate(out)
    import er003_audio_tts_asr_safety as _safety
    _safety.FOREIGN_TOKEN_HUMAN_REVIEW_LOG_PATH = f"{out}/foreign_token_hr_queue.jsonl"
    e6b.redirect_local_rewrite(out)
    return r77, before, iso


def txt_variants(canonical):
    """canonical(byUs含む)に対する保存転写。buy us形。"""
    return canonical.replace("byUs", "buy us")


def scan(obj):
    s = json.dumps(obj, ensure_ascii=False, default=str)
    return {"has_multiword_homophone_spans": "multiword_homophone_spans" in s,
            "n_spans_keys": s.count("multiword_homophone_spans"),
            "has_multiword_in_diffs": "multiword_homophone" in s}


def spans_from(obj):
    out = []

    def walk(o):
        if isinstance(o, dict):
            if "multiword_homophone_spans" in o:
                out.append({"step": o.get("step"), "spans": o["multiword_homophone_spans"]})
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(obj)
    return out


def brief(r):
    if not isinstance(r, dict):
        return str(r)[:200]
    keys = ("status", "reason", "asr_text", "fallback_used", "verified", "asr_verified", "audio_classification", "slowdown_applied",
            "post_slowdown_classification", "tts_generations_used", "attempt_count", "instruction_type", "human_review_required")
    b = {k: r.get(k) for k in keys if k in r}
    for lk in ("attempts_log", "standard_attempts_log", "fallback_attempts_log", "slowdown_attempts_log"):
        if isinstance(r.get(lk), list):
            b[lk] = [{k: a.get(k) for k in ("attempt", "status", "asr_text", "verified", "audio_classification", "instruction_type",
                                            "post_slowdown_classification") if isinstance(a, dict) and k in a}
                     for a in r[lk]]
    return b


def judgement_states(r):
    """asr_judgementのstate/primary_label/secondary有無を再帰抽出。"""
    res = []

    def walk(o):
        if isinstance(o, dict):
            if isinstance(o.get("state"), str) and ("primary" in o or "secondary" in o):
                pr, se = o.get("primary"), o.get("secondary")
                res.append({"state": o.get("state"),
                            "primary_label": pr.get("label") if isinstance(pr, dict) else None,
                            "secondary_called": se.get("called") if isinstance(se, dict) else None,
                            "secondary_text": se.get("text") if isinstance(se, dict) else None})
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(r)
    return res


REGISTRY = {}


def scenario(name):
    def deco(fn):
        REGISTRY[name] = fn
        return fn
    return deco


T_BODY = "LINE Manga has launched byUs, an AI service that lets you shape stories."
T_KP = "Make one yourself with byUs."


def _wav(out, level, name):
    p = f"{out}/run_{name}/{level}/narration/{name}.wav"
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def run_scn(name, fn, primary, secondary, expect, family, entrypoint, note="", check=None):
    STATE["primary"][:] = list(primary)
    STATE["secondary"][:] = list(secondary)
    STATE["p_calls"].clear()
    STATE["s_calls"].clear()
    STATE["tts_calls"] = 0
    STATE["observed"].clear()
    n_net0 = len(STATE["net_attempts"])
    rec = {"scenario": name, "family": family, "entrypoint": entrypoint, "expect": expect, "note": note,
           "primary_script": list(primary), "secondary_script": list(secondary)}
    try:
        r = fn()
        rec["result_brief"] = brief(r)
        rec["scan"] = scan(r)
        rec["spans"] = spans_from(r)
        rec["judgement_states"] = judgement_states(r)
        rec["status"] = r.get("status") if isinstance(r, dict) else None
        rec["custom_result"] = r if check is not None else None
    except Exception as e:  # noqa: BLE001
        rec["exception"] = "".join(traceback.format_exception_only(type(e), e)).strip()
        rec["traceback_tail"] = traceback.format_exc()[-1500:]
    rec["primary_calls"] = list(STATE["p_calls"])
    rec["secondary_calls"] = list(STATE["s_calls"])
    rec["tts_stub_calls"] = STATE["tts_calls"]
    rec["observed_adapter_calls"] = list(STATE["observed"])
    rec["observed_spans"] = [{"step": st["step"], "spans": st["multiword_homophone_spans"], "judge_state": o["judge_state"]}
                             for o in STATE["observed"] for st in o["steps"] if st.get("multiword_homophone_spans")]
    rec["network_attempts"] = STATE["net_attempts"][n_net0:]
    st = rec.get("status")
    if expect == "PASS_WITH_SPANS":
        ok = (st == "OK") and bool(rec.get("spans") or rec["observed_spans"]) and not rec.get("exception")
    elif expect == "NOT_PASS":
        ok = (st != "OK") and not rec.get("exception")
    elif check is not None:
        ok = (not rec.get("exception")) and bool(check(rec.get("custom_result"), rec))
    else:
        ok = None
    rec["ok"] = bool(ok) and not rec["network_attempts"]
    return rec


# ---------------- Family X
@scenario("X_KP_repro01")
def x_kp(out):
    import er003_v1_repro01_main_generate as repro01
    p = _wav(out, "a2", "kp1_english")
    return run_scn("X_KP_repro01", lambda: repro01.generate_key_phrase_component_verified(T_KP, p, tts_backend=FL),
                   [txt_variants(T_KP)], ["unused"], "PASS_WITH_SPANS", "X",
                   "er003_v1_repro01_main_generate.generate_key_phrase_component_verified -> generate_narration_snippet_verified_strict (:356)")


@scenario("X_BODY_crosslevel_std")
def x_body(out):
    import er003_v1_crosslevel_audio_02_common as cl
    p = _wav(out, "a2", "full_story_part1")
    return run_scn("X_BODY_crosslevel_std",
                   lambda: cl.generate_english_segment_with_fallback(T_BODY, p, "LINE Manga has", max_extra_chars=30, tts_backend=FL),
                   [txt_variants(T_BODY)], ["unused"], "PASS_WITH_SPANS", "X",
                   "er003_v1_crosslevel_audio_02_common.generate_english_segment_with_fallback (標準経路 attempt1 -> repro01:356)")


def _fb(label, sec_text_fn, expect, out):
    import er003_v1_crosslevel_audio_02_common as cl
    name = f"X_FALLBACK_force_secondary_{label}"
    p = _wav(out, "a2", f"fb_{label}")
    bad = "Completely unrelated sentence about weather today."
    return run_scn(name,
                   lambda: cl.generate_english_segment_with_fallback(T_BODY, p, "LINE Manga has", max_extra_chars=30, tts_backend=FL),
                   [bad, bad, txt_variants(T_BODY)], [bad, bad, sec_text_fn(T_BODY)], expect, "X",
                   "er003_v1_crosslevel_audio_02_common.generate_english_segment_with_fallback -> _run_a2_minimal_fallback_attempt (:378, force_secondary=True)",
                   note=f"標準2回NG後のminimal fallback。Primary=buy us / Secondary={sec_text_fn(T_BODY)!r}")


@scenario("X_FALLBACK_by_us")
def x_fb1(out):
    return _fb("by_us", lambda t: t.replace("byUs", "by us"), "PASS_WITH_SPANS", out)


@scenario("X_FALLBACK_bias")
def x_fb2(out):
    return _fb("bias", lambda t: t.replace("byUs", "bias"), "PASS_WITH_SPANS", out)


@scenario("X_FALLBACK_bi_us_NG")
def x_fb3(out):
    return _fb("bi_us", lambda t: t.replace("byUs", "bi us"), "NOT_PASS", out)


@scenario("X_SLOWDOWN_a2_body")
def x_slow(out):
    import er003_v1_n3_01_tts_generate as n3
    p = _wav(out, "a2", "full_story_part2")
    ttext = n3.tts_safe_news_en(T_BODY)
    return run_scn("X_SLOWDOWN_a2_body",
                   lambda: n3.generate_a2_segment_with_slowdown(ttext, p, "LINE Manga has", style_prefix_override=None, tts_backend=FL,
                                                                 enable_repetition_qa=True),
                   [txt_variants(T_BODY)] * 2, ["unused"], "PASS_WITH_SPANS", "X",
                   "er003_v1_n3_01_tts_generate.generate_a2_segment_with_slowdown (減速前=標準経路 + 減速後再検証 :144)")


@scenario("X_HEADING_sing01")
def x_head(out):
    import er003_v1_sing01_point_headings_aoede as ph
    p = _wav(out, "a2", "point_one_heading")
    return run_scn("X_HEADING_sing01", lambda: ph.generate(T_KP, p, tts_backend=FL), [txt_variants(T_KP)], ["unused"],
                   "PASS_WITH_SPANS", "X", "er003_v1_sing01_point_headings_aoede.generate (:129)")


@scenario("X_CHARON_voice01")
def x_charon(out):
    import er003_v1_sing01_voice01_generate as v1
    p = _wav(out, "b1b", "topic_intro")
    return run_scn("X_CHARON_voice01", lambda: v1.generate_charon_english(T_BODY, p, tts_backend=FL),
                   [txt_variants(T_BODY)], ["unused"], "PASS_WITH_SPANS", "X", "er003_v1_sing01_voice01_generate.generate_charon_english (:246)")


@scenario("X_NEWS_tail_fix")
def x_news(out):
    import er003_v1_sing01_news_tail_fix as nt
    p = _wav(out, "b1b", "full_story_part1")
    return run_scn("X_NEWS_tail_fix", lambda: nt.generate_news_narration_wide_margin(T_BODY, p, tts_backend=FL),
                   [txt_variants(T_BODY)], ["unused"], "PASS_WITH_SPANS", "X", "er003_v1_sing01_news_tail_fix.generate_news_narration_wide_margin (:209)")


@scenario("X_KP_english_lock_fallback")
def x_kp_lock(out):
    import er003_v1_repro01_main_generate as repro01
    p = _wav(out, "a2", "kp3_english")
    bad = "Completely unrelated words here."
    return run_scn("X_KP_english_lock_fallback", lambda: repro01.generate_key_phrase_component_verified(T_KP, p, tts_backend=FL),
                   [bad, bad, txt_variants(T_KP)], [bad], "PASS_WITH_SPANS", "X",
                   "repro01.generate_key_phrase_component_verified: MINIMAL x2 NG -> ENGLISH_LOCK fallback attempt (:356)")


@scenario("X_RESUME_n8_a2_and_b1")
def x_resume(out):
    import er008_n8_a2_resume_01 as ra2
    import er008_n8_b1_resume_01 as rb1
    wav = _wav(out, "a2", "resume_probe")
    open(wav, "wb").write(b"RIFF0000WAVE")   # 存在のみ(ASR seamは保存転写)

    def go():
        o = {}
        STATE["primary"][:] = [txt_variants(T_BODY)]
        o["a2_verify_existing"] = ra2._verify_existing(wav, T_BODY, "en")
        STATE["primary"][:] = [txt_variants(T_BODY)]
        o["b1_verify_existing"] = rb1._verify_existing(wav, T_BODY, T_BODY, "en")
        return o
    return run_scn("X_RESUME_n8_a2_and_b1", go, [txt_variants(T_BODY)], ["unused"], "CUSTOM", "X",
                   "er008_n8_a2_resume_01._verify_existing:41 / er008_n8_b1_resume_01._verify_existing:47 (classify_asr_match直接=should_passのみ)",
                   note="P-01実挙動: 多語同音はshould_pass=False -> 再利用せず再生成(安全側。既存1:1同音と同じ)",
                   check=lambda r, rec: r["a2_verify_existing"] is None and r["b1_verify_existing"] is None)


@scenario("X_STORE_rejudge_J11")
def x_store(out):
    import er019_family_x_validation_inheritance_01 as inh

    def go():
        base = {"asr_text": txt_variants(T_BODY), "text": T_BODY, "sha256": "x" * 64}
        o = {"no_secondary": inh.rejudge_with_current_judge(dict(base), "a2", "full_story_part1")}
        e2 = dict(base)
        e2["asr_judgement"] = {"state": "PASS", "primary": {"passed": False, "text": base["asr_text"]},
                               "secondary": {"called": True, "text": T_BODY.replace("byUs", "by us")}}
        o["with_stored_secondary_by_us"] = inh.rejudge_with_current_judge(e2, "a2", "full_story_part1")
        return o
    return run_scn("X_STORE_rejudge_J11", go, ["unused"], ["unused"], "CUSTOM", "X",
                   "er019_family_x_validation_inheritance_01.rejudge_with_current_judge (:284-303 -> unified_judge)",
                   note="P-01実挙動: 保存転写のみ+Secondary保存なし -> REJUDGE_NG。保存Secondaryがshould_pass可なら継承可(既存1:1と同じ)",
                   check=lambda r, rec: (r["no_secondary"]["ok"] is False and "REJUDGE_NG" in str(r["no_secondary"]["reason"])
                                         and r["no_secondary"].get("secondary_new_calls") == 0))


@scenario("Z_KP_english_lock_fallback")
def z_kp_lock(out):
    t = T_KP
    bad = "Completely unrelated words here."
    return _z("Z_KP_english_lock_fallback", out, "kp_en", "a2", "kp3_en", t, "KP_EN", "narrator", "Aoede",
              [bad, bad, txt_variants(t)], [bad], "PASS_WITH_SPANS",
              "er063.run_tts_stage kp_en -> _kp_en_two_stage: minimal x2 NG -> ENGLISH_LOCK (er063:836 -> repro01:356)", rank=3)


# ---------------- Family Z (run_tts_stage = Z Production stage、各kindの正式関数)
def _z(name, out, kind, level, clip_id, text, role_key, speaker, voice, primary, secondary, expect, entry_desc, **spec_kw):
    import er063_family_z_audio_01 as Z
    spec = Z.ClipSpec(clip_id, level, kind, text, voice=voice, speaker=speaker, role_key=role_key, language="en", **spec_kw)
    run_dir = f"{out}/run_{name}"

    def go():
        r = Z.run_tts_stage(run_dir, level, [spec])
        d = json.load(open(r["results_path"], encoding="utf-8"))
        seg = (d.get("segments") or {}).get(clip_id)
        if seg is None:
            for v in (d.get("key_phrases") or {}).values():
                seg = (v or {}).get("english") if isinstance(v, dict) and (v.get("english") or {}).get("segment_id") == clip_id else seg
        seg = seg if seg is not None else d
        return {"status": seg.get("status") if isinstance(seg, dict) else None, "stage_statuses": r.get("statuses"), "entry": seg}
    return run_scn(name, go, primary, secondary, expect, "Z", entry_desc)


@scenario("Z_KP_en")
def z_kp(out):
    t = T_KP
    return _z("Z_KP_en", out, "kp_en", "a2", "kp1_en", t, "KP_EN", "narrator", "Aoede", [txt_variants(t)], ["unused"], "PASS_WITH_SPANS",
              "er063.run_tts_stage kp_en -> _kp_en_two_stage -> repro01.generate_narration_snippet_verified_strict (er063:827/836 -> repro01:356)", rank=1)


@scenario("Z_NARRATOR_a2")
def z_nar(out):
    t = T_BODY
    return _z("Z_NARRATOR_a2", out, "narrator", "a2", "full_story_part1_c1", t, "NARRATOR_FULL_STORY_STD", "narrator", "Aoede",
              [txt_variants(t)] * 2, ["unused"], "PASS_WITH_SPANS",
              "er063 narrator(a2) -> n3_tts.generate_a2_segment_with_slowdown (er063:778/788 -> n3_01:144)", part=1)


@scenario("Z_NARRATOR_b1b")
def z_nar_b(out):
    t = T_BODY
    return _z("Z_NARRATOR_b1b", out, "narrator", "b1b", "full_story_part1_c1", t, "NARRATOR_FULL_STORY_ADV", "narrator", "Aoede",
              [txt_variants(t)], ["unused"], "PASS_WITH_SPANS",
              "er063 narrator(b1b) -> news_tail_fix.generate_news_narration_wide_margin (er063:774 -> news_tail:209)", part=1)


@scenario("Z_DIALOGUE_a2")
def z_dlg(out):
    import er063_family_z_audio_01 as Z
    t = "I will try byUs today."
    return _z("Z_DIALOGUE_a2", out, "dialogue", "a2", "full_story_part1_c2", t, "DIALOGUE_STD", "melos", Z.resolve_dialogue_voice("melos"),
              [txt_variants(t)] * 3, ["unused"], "PASS_WITH_SPANS",
              "er063 dialogue(a2) -> n3_tts.generate_with_a2_slowdown_outer_loop -> bvoices.generate_voice_body_wide_margin (er063:788-792 -> er012:553; 減速後再検証=n3_01:144)", part=1)


@scenario("Z_TOPIC_INTRO_a2")
def z_ti(out):
    t = "Today's topic is byUs."
    return _z("Z_TOPIC_INTRO_a2", out, "topic_intro", "a2", "topic_intro_en", t, "TOPIC_INTRO_EN", "narrator", "Aoede", [txt_variants(t)], ["unused"],
              "PASS_WITH_SPANS", "er063 topic_intro(a2) -> crosslevel.generate_english_segment_with_fallback (er063:804 -> crosslevel:378前段)")


@scenario("Z_BI_US_NG_kp_en")
def z_neg(out):
    t = T_KP
    bad = t.replace("byUs", "bi us")
    return _z("Z_BI_US_NG_kp_en", out, "kp_en", "a2", "kp2_en", t, "KP_EN", "narrator", "Aoede", [bad] * 4, [bad] * 4, "NOT_PASS",
              "er063.run_tts_stage kp_en 負例: Primary/Secondary=bi us(4回構成) -> 全NG(V8でNG維持、Secondary=Azure NG_BOTH)", rank=2)


# ---------------- paid(実TTS/実ASR。専用run_id=run_pnmh_a2_07。X 1本 + Z 1本 + Bi-us負例候補)
class PMeter(e6.Meter):
    def __init__(self, out_dir, hard_stop):
        super().__init__(out_dir, hard_stop)
        self.n_tts = 0
        self.n_text = 0
        self.azure_seconds = 0.0
        self.out_dir_rel = out_dir

    def check(self):
        super().check()
        hit = e6.stop_present(self.out_dir_rel)
        if hit:
            raise RuntimeError(f"[STOP] sentinel present: {hit}")


PAID_X_TEXT = "LINE Manga has launched byUs, an AI service that lets you shape stories."
PAID_Z_TEXT = "Make one yourself with byUs."
BIUS_CANDS = [("c1_Bi-us", "Bi-us"), ("c2_Bi_us", "Bi us"), ("c3_Bi,_us", "Bi, us."), ("c4_Bye-us(control)", "Bye-us"),
              ("c5_B_I_us", "B I us"), ("c6_be-us", "be-us")]


@scenario("PAID_X_body_byUs")
def paid_x(out):
    import er003_v1_crosslevel_audio_02_common as cl
    p = _wav(out, "a2", "full_story_part1")
    r = run_scn("PAID_X_body_byUs",
                lambda: cl.generate_english_segment_with_fallback(PAID_X_TEXT, p, "LINE Manga has", max_extra_chars=30, tts_backend=FL),
                [], [], "CUSTOM", "X",
                "crosslevel.generate_english_segment_with_fallback (Family X 英語segmentの正式関数、実TTS+実Primary+(NG時)実Secondary)",
                check=lambda r, rec: True)
    r["ok"] = None
    return r


@scenario("PAID_Z_narrator_byUs")
def paid_z(out):
    return _z("PAID_Z_narrator_byUs", out, "narrator", "a2", "full_story_part1_c1", PAID_Z_TEXT, "NARRATOR_FULL_STORY_STD", "narrator", "Aoede",
              [], [], "CUSTOM", "er063.run_tts_stage narrator(a2) -> n3_tts.generate_a2_segment_with_slowdown (実TTS+実ASR+6%減速+再検証)", part=1)


def _norm_words(t):
    import re
    return re.sub(r"[^a-z0-9' ]+", " ", (t or "").lower()).split()


@scenario("PAID_BIUS_candidates")
def paid_bius(out):
    import er003_v1_repro01_main_generate as repro01
    import er006_secondary_asr_01 as sec
    import er006_asr_provider_routing_01 as routing
    import er008_disfluency_qa_18 as dq
    import er094_multiword_homophone_01 as mw
    rows = []
    canon = "Make one yourself with byUs."
    memo = {}
    real_az = sec.get_full_text_via_azure_stt_with_phrase_list

    def az_memo(wav, *a, **k):
        if wav not in memo:
            memo[wav] = real_az(wav, *a, **k)
        return memo[wav]
    sec.get_full_text_via_azure_stt_with_phrase_list = az_memo
    model = None
    for cid, variant in BIUS_CANDS:
        wav = f"{out}/run_bius/{cid}.wav"
        os.makedirs(os.path.dirname(wav), exist_ok=True)
        tts_text = f"Make one yourself with {variant}" + ("" if variant.endswith(".") else ".")
        row = {"cand": cid, "tts_input": tts_text}
        try:
            r = repro01.generate_english_component_minimal_instruction(tts_text, wav, tts_backend=FL, enable_pronunciation_resolver=True)
            row["tts_status"] = r.get("status")
            row["tts_model"] = r.get("model") or r.get("tts_model_id")
        except Exception as e:  # noqa: BLE001
            row["tts_status"] = "EXC:" + repr(e)[:200]
            rows.append(row)
            continue
        if row["tts_status"] != "OK":
            rows.append(row)
            continue
        p_text, p_err = routing.transcribe(wav, language="en-US")
        a_text, a_err = az_memo(wav, language="en-US", phrases=[])
        row["primary_openai"] = p_text
        row["azure"] = a_text
        try:
            if model is None:
                model = dq._get_model("small")
            segs, _ = model.transcribe(wav, language="en", condition_on_previous_text=False, vad_filter=False, word_timestamps=True)
            words = [(w.word.strip(), round(w.start, 2), round(w.end, 2)) for sg in segs for w in (sg.words or [])]
            row["local_whisper_small_words"] = words
            row["local_text"] = " ".join(w[0] for w in words)
        except Exception as e:  # noqa: BLE001
            row["local_error"] = repr(e)[:200]
        foc = {}
        for k in ("primary_openai", "azure", "local_text"):
            ws = _norm_words(row.get(k))
            foc[k] = ws[4:] if ws[:4] == ["make", "one", "yourself", "with"] else ws[-3:]
        row["focal"] = {k: " ".join(v) for k, v in foc.items()}
        # adapter全体(Primary->Secondary->最終ANDゲート)。canonicalは記事実テキスト byUs
        for tag, fs in (("adapter_normal", False), ("adapter_force_secondary", True)):
            d = sec.evaluate_attempt_with_cascade_detail(canon, p_text, [], wav, language="en-US", ledger_phrases=[], force_secondary=fs)
            aj = d.get("asr_judgement") or {}
            row[tag] = {"verified": d.get("verified"), "state": aj.get("state"),
                        "primary_label": (aj.get("primary") or {}).get("label"),
                        "classification": getattr(d.get("classification"), "classification", None),
                        "secondary_text": (aj.get("secondary") or {}).get("text"),
                        "multiword_spans": [st.get("multiword_homophone_spans") for st in d.get("steps") or []
                                            if st.get("multiword_homophone_spans")]}
        det = {}
        pf = foc["primary_openai"]
        row["why_primary_focal"] = (mw.multiword_span_equivalent_v3(["byus"], pf, detail=det) if 1 < len(pf) <= 3 else None, det.get("why"))
        # 意図した区切り発音の確認(自動基準): いずれかのエンジンのfocalが 2語で第1語がbi/bee/be/b、かつ by/buy/bias/bye を返すエンジンが無い
        split_set = {"bi us", "bee us", "be us", "bius", "bi-us", "b us"}
        wrong = {"by us", "buy us", "bias", "byus", "bye us"}
        fs_ = [v for v in row["focal"].values() if v]
        row["intent_split_confirmed"] = any(v in split_set for v in fs_) and not any(v in wrong for v in fs_)
        rows.append(row)
    sec.get_full_text_via_azure_stt_with_phrase_list = real_az
    return {"status": "DONE", "rows": rows}


def main_paid(names):
    out = EV
    os.makedirs(out, exist_ok=True)
    r77, before, iso = setup(out)
    hard = float(os.environ.get("PNMH_BUDGET_JPY", "20"))
    meter = PMeter(out, hard)
    e6b.install(meter)
    install_observer()
    snap0 = e6b.shared_snapshot()
    res = {"mode": "paid", "isolation": iso, "hard_stop_jpy": hard, "scenarios": []}
    for n in names:
        rec = REGISTRY[n](out)
        res["scenarios"].append(rec)
        print(n, "status=", rec.get("status"), "exc=", rec.get("exception"), "cum_jpy=", round(meter.jpy, 4), flush=True)
        json.dump(res, open(f"{out}/runner_paid_partial.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    res["shared_state_unchanged"] = (before == r77.snapshot_state())
    res["shared_files_changed_outside_evidence"] = [x for x in e6b.snapshot_diff(snap0, e6b.shared_snapshot()) if "er094_output" not in x]
    res["cost"] = {"est_total_jpy": round(meter.jpy, 4), "n_tts": meter.n_tts, "n_openai_asr": meter.n_openai, "n_azure": meter.n_azure,
                   "azure_seconds": round(meter.azure_seconds, 2), "n_text_llm": meter.n_text, "usage_log": f"{out}/usage_log.jsonl"}
    json.dump(res, open(f"{out}/runner_paid.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print(json.dumps(res["cost"], ensure_ascii=False), "shared_state_unchanged:", res["shared_state_unchanged"])


def main():
    names = [a for a in sys.argv[2:]] or [n for n in REGISTRY if not n.startswith("PAID_")]
    if MODE == "paid":
        return main_paid(names)
    os.makedirs(EV, exist_ok=True)
    r77, before, iso = setup(EV)
    snap0 = e6b.shared_snapshot()
    install_observer()
    if MODE == "api0":
        install_api0_stubs()
    res = {"mode": MODE, "isolation": iso, "scenarios": []}
    for n in names:
        rec = REGISTRY[n](EV)
        res["scenarios"].append(rec)
        print(n, "ok=", rec["ok"], "status=", rec.get("status"), "spans=", len(rec.get("spans") or []), "exc=", rec.get("exception"),
              "net=", rec["network_attempts"])
    after = r77.snapshot_state()
    res["shared_state_unchanged"] = (before == after)
    res["shared_files_changed_outside_evidence"] = e6b.snapshot_diff(snap0, e6b.shared_snapshot())
    res["network_attempts_total"] = len(STATE["net_attempts"])
    json.dump(res, open(f"{EV}/runner_{MODE}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print("shared_state_unchanged:", res["shared_state_unchanged"], "outside_changed:", res["shared_files_changed_outside_evidence"][:5])


if __name__ == "__main__":
    main()

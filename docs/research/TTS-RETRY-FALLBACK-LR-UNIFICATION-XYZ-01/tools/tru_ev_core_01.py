# -*- coding: utf-8 -*-
"""TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_03: runtime evidence driver core(Production codeではない。driver側monkeypatchのみ=Opus M-8)。

目的: X/Y/Z の**正式な生成関数**(Family runnerのgenerate_*_segments / run_tts_stage / KP・解説のleaf)を、X/Y/Z run scope内で
**実TTS・実ASR・実180秒待機・実LR(Luna)・実Gate**のまま呼び、判定結果を **NG方向にだけ** 上書きして統一3回構成ブロックの実挙動を観測する。

注入の原則(EVIDENCE_PLAN_01 §2):
  * 上書きは NG方向のみ(ok->NG)。NG->OK方向は実装しない。上書きしないattempt(③以降の実PASS等)は完全に本物の判定。
  * Style・Prompt・Voice・速度・model・待機・回数には一切触れない(判定の戻り値のみ)。
  * LR経路を駆動するcaseでは Primary転写へ「1語置換」を注入(NG方向のみ)=本物のjudge/identify_ng_spanが成立する。
  * 正常系(E-N)は injected_override_count==0 をassert。
  * 観測用の分離: HRQ・attempt_history・Master Audio Store・各telemetryはcase専用dirへ向ける(共有台帳を強制NG由来の行で汚さない。
    er089 TrialIsolation と同方式)。Productionのコード・設定は変更しない(module属性の一時差替えのみ、終了時に必ず復元)。
"""
from __future__ import annotations

import contextlib
import copy
import hashlib
import json
import os
import re
import subprocess
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)

MANAGEMENT_ID = "TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01"
EVD = "docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01"
EVIDENCE_RUNS = f"{EVD}/evidence_runs"

_SUBST_POOL = ["market", "window", "silver", "garden", "bottle", "winter", "pocket", "orange"]


def clip_of(path) -> str:
    return os.path.splitext(os.path.basename(str(path)))[0]


def sha8(s) -> str:
    return hashlib.sha256((s if isinstance(s, str) else repr(s)).encode("utf-8")).hexdigest()[:12]


# 言い換えやすい語を優先(LRの7 Gate[特に意味保存]を通る候補が作れる語。核心語[タイトル語・固有名詞・数値]の置換だとLR候補が全滅しLR blockに入れない)
_PREFERRED = ["topic", "raised", "affect", "compares", "about", "notice", "listen", "think", "show", "learn", "look", "change", "happen"]


def substitute_one_word(text: str, prefer=None) -> str:
    """転写の1語を別の実在語へ置換(NG方向の注入。ASRが誤読した状況の再現)。置換語は言い換えやすい語を優先、無ければ中ほどの内容語。
    prefer=case指定の置換対象語(あれば最優先)。"""
    words = re.findall(r"[A-Za-z']+", text or "")
    low_words = {w.lower(): w for w in words}
    target = next((low_words[w] for w in (list(prefer or []) + _PREFERRED) if w in low_words), None)
    if target is None:
        cands = [w for w in words if len(w) >= 5]
        if not cands:
            cands = [w for w in words if len(w) >= 3] or words
        if not cands:
            return text
        target = cands[len(cands) // 2]
    low = (text or "").lower()
    rep = next((w for w in _SUBST_POOL if w not in low), "river")
    return re.sub(r"\b" + re.escape(target) + r"\b", rep, text, count=1)


class Plan:
    """clip別の注入計画。key=clip_id or "*"。slot=ブロック通算番号(統一judgeのattempt_ctx['slot']。LR blockは4〜6)。"""

    def __init__(self, ng=None, sub=None, post_ng=None, dq=None, ja_ng=None, sub_word=None, by_count=False):
        self.by_count = bool(by_count)      # True=ctxのslotではなくclipごとの呼出順で数える(Z Adv会話は外側loopでslotが毎回1になるため)
        self.sub_word = dict(sub_word or {})   # clip(or "*") -> 置換対象語のlist(省略時は言い換えやすい語を優先)
        self.ng = self._norm(ng)          # 統一judge(EN/KP)をNG化するslot
        self.sub = self._norm(sub)        # Primary転写を1語置換するslot(LR駆動用)
        self.post_ng = self._norm(post_ng)  # 減速後の統一judge再検証をNG化するslot
        self.dq = self._norm(dq)          # disfluency gate(ASR一致でもQAのみNG)をNG化するslot(最新judge slotに紐付け)
        self.ja_ng = self._norm(ja_ng)    # JA統一judgeをNG化するslot

    @staticmethod
    def _norm(d):
        return {k: {int(x) for x in v} for k, v in (d or {}).items()}

    def wants(self, kind: str, clip: str, slot: int) -> bool:
        t = getattr(self, kind)
        for key in (clip, "*"):
            if key in t and slot in t[key]:
                return True
        return False

    @property
    def injects(self) -> bool:
        return any([self.ng, self.sub, self.post_ng, self.dq, self.ja_ng])

    def as_json(self):
        return {k: {c: sorted(v) for c, v in getattr(self, k).items()} for k in ("ng", "sub", "post_ng", "dq", "ja_ng")}


class Recorder:
    def __init__(self):
        self.judge_n = {}        # clip -> 実judge呼出数
        self.last_slot = {}      # clip -> 直近のjudge slot
        self.judges = []
        self.overrides = []
        self.tts_resolve = []    # resolve_tts_call_and_prompt(=TTS 1 attempt)
        self.tts_api = 0
        self.sleep_total = 0.0
        self.stop_checks = {"cooldown": 0, "attempt": 0, "other": 0}
        self.cooldowns = []
        self.lr_calls = []
        self.post_judges = []
        self.transcripts = []
        self.t0 = time.time()
        self.events = []
        self.in_outer = 0
        self.post_n = {}


@contextlib.contextmanager
def installed(plan: Plan, rec: Recorder, iso_dir: str, *, cost_log: str):
    """module属性の一時差替え(観測 + NG方向注入 + 台帳分離)。終了時に必ず復元。"""
    import er002_common as common
    import er003_v1_n3_01_tts_generate as n3
    import er005_cost_logger as cl
    import er006_asr_provider_routing_01 as routing
    import er006_master_audio_store_01 as store
    import er006_secondary_asr_01 as sec
    import er007_ja_secondary_asr_01 as jasec
    import er008_disfluency_qa_18 as dq18
    import er011_human_review_lock_01 as rl
    import er020_tts_retry_local_rewrite_01 as er020
    import er021_en_asr_semantic_equivalence_production_01 as sem
    import er025_entity_pronunciation_resolver_core_01 as e25
    import er033_tts_flash_lite_backend_wiring_01 as flw
    import er127_tts_block_policy_01 as er127

    os.makedirs(iso_dir, exist_ok=True)
    saved = []

    def patch(obj, name, new):
        saved.append((obj, name, getattr(obj, name)))
        setattr(obj, name, new)

    # ---- 台帳分離
    patch(sec, "HUMAN_REVIEW_LOG_PATH", os.path.join(iso_dir, "human_review_queue.jsonl"))
    patch(jasec, "HUMAN_REVIEW_LOG_PATH_JA", os.path.join(iso_dir, "human_review_queue_ja.jsonl"))
    patch(rl, "ATTEMPT_HISTORY_PATH", os.path.join(iso_dir, "attempt_history.jsonl"))
    patch(e25, "TELEMETRY_PATH", os.path.join(iso_dir, "er025_telemetry.jsonl"))
    sem_path = os.path.join(iso_dir, "semantic_equivalence_telemetry.jsonl")
    _orig_sem = sem.append_telemetry_log
    patch(sem, "append_telemetry_log", lambda record, path=None: _orig_sem(record, path=sem_path))
    sd = os.path.join(iso_dir, "master_audio_store")
    patch(store, "STORE_DIR", sd)
    patch(store, "AUDIO_DIR", f"{sd}/audio")
    patch(store, "MANIFEST_PATH", f"{sd}/manifest.json")
    patch(store, "TELEMETRY_PATH", f"{sd}/reuse_telemetry.jsonl")
    cl.init_logger(cost_log)

    # ---- 観測: TTS attempt(style/voice/model)
    _orig_resolve = flw.resolve_tts_call_and_prompt

    def resolve(text, style_prefix, model_name, voice_name, out_path=None, *a, **k):
        _tb = k.get("tts_backend", a[0] if a else flw.DEFAULT_TTS_BACKEND)
        rec.tts_resolve.append({"clip": clip_of(out_path) if out_path else cl._CONTEXT.get("segment"), "t": round(time.time() - rec.t0, 2),
                                "voice": voice_name, "model_requested": model_name, "model": flw.resolve_actual_model_name(model_name, _tb), "style_sha": sha8(style_prefix or ""), "style_head": (style_prefix or "")[:140],
                                "style_chars": len(style_prefix or ""), "text_head": (text or "")[:80], "text_sha": sha8(text or ""),
                                "backend": _tb})
        return _orig_resolve(text, style_prefix, model_name, voice_name, out_path, *a, **k)
    patch(flw, "resolve_tts_call_and_prompt", resolve)

    _orig_call = common._call_tts_with_retry

    def call_tts(*a, **k):
        rec.tts_api += 1
        return _orig_call(*a, **k)
    patch(common, "_call_tts_with_retry", call_tts)

    # ---- 観測: sleep/cooldown/STOP確認
    _orig_sleep = er127.RUNTIME.sleep

    def sleep(s):
        rec.sleep_total += float(s)
        return _orig_sleep(s)
    patch(er127.RUNTIME, "sleep", staticmethod(sleep))

    _orig_cd = er127.cooldown_core

    def cooldown_core(**kw):
        ev0 = time.time()
        r = _orig_cd(**kw)
        rec.cooldowns.append({"label": kw.get("label"), "requested_seconds": r.get("cooldown_requested_seconds"),
                              "actual_seconds": r.get("cooldown_actual_seconds"), "started_at": r.get("cooldown_started_at"),
                              "ended_at": r.get("cooldown_ended_at"), "resumed": r.get("resumed"),
                              "attempt_before": r.get("attempt_before_cooldown"), "attempt_after": r.get("attempt_after_cooldown"),
                              "total_elapsed_since_ref_seconds": r.get("total_elapsed_since_ref_seconds"), "wall_start_epoch": ev0})
        return r
    patch(er127, "cooldown_core", cooldown_core)

    _orig_rsc = er127.run_stop_check

    def run_stop_check(where):
        key = "cooldown" if str(where).startswith("tts_cooldown") else ("attempt" if str(where).startswith("tts_attempt") else "other")
        rec.stop_checks[key] += 1
        return _orig_rsc(where)
    patch(er127, "run_stop_check", run_stop_check)

    # ---- 観測: LR
    _orig_lr = er020.run_local_rewrite_recovery

    def lr(**kw):
        t = time.time()
        r = _orig_lr(**kw)
        rec.lr_calls.append({"segment_id": kw.get("segment_id"), "depth": kw.get("depth", 0), "status": (r or {}).get("status"),
                             "ng_span_found": ((r or {}).get("ng_span") or {}).get("found"),
                             "ng_span": ((r or {}).get("ng_span") or {}),
                             "model": ((r or {}).get("candidate_gen") or {}).get("model") or ((r or {}).get("candidate_gen") or {}).get("model_id"),
                             "rewritten_text": (((r or {}).get("selection") or {}).get("selected") or {}).get("rewritten_segment"),
                             "elapsed_s": round(time.time() - t, 2), "last_asr_text": kw.get("last_asr_text")})
        return r
    patch(er020, "run_local_rewrite_recovery", lr)

    # ---- 転写の1語置換(LR駆動。NG方向のみ)
    _orig_tr = routing.transcribe

    def transcribe(path, *a, **k):
        res = _orig_tr(path, *a, **k)
        clip = clip_of(path)
        nxt = rec.last_slot.get(clip, 0) + 1
        if plan.wants("sub", clip, nxt) and isinstance(res, tuple) and res and res[0]:
            new = substitute_one_word(res[0], prefer=plan.sub_word.get(clip) or plan.sub_word.get("*"))
            rec.overrides.append({"kind": "transcript_substitution", "clip": clip, "slot": nxt, "before": res[0], "after": new})
            res = (new,) + tuple(res[1:])
        return res
    patch(routing, "transcribe", transcribe)

    # ---- 統一judge(EN/KP/Z)のNG化
    def _slot(ctx, clip):
        if plan.by_count:
            return rec.judge_n.get(clip, 0) + 1
        s = (ctx or {}).get("slot")
        if isinstance(s, int) and s > 0:
            return s
        return rec.last_slot.get(clip, 0) + 1

    def wrap_judge(orig, kind):
        def w(*args, **k):
            canonical_text, asr_text = args[0], args[1]
            wav_path = args[2] if kind == "ja" else args[3]      # JA版は (text, asr_text, out_path, ...)、EN版は (text, asr_text, prior_results, wav_path, ...)
            clip = clip_of(wav_path)
            ctx = k.get("attempt_ctx") or {}
            slot = _slot(ctx, clip)
            rec.in_outer += 1
            try:
                res = orig(*args, **k)
            finally:
                rec.in_outer -= 1
            ok, stop, cls = res
            rec.last_slot[clip] = slot
            rec.judge_n[clip] = rec.judge_n.get(clip, 0) + 1
            row = {"clip": clip, "kind": kind, "slot": slot, "ok_real": bool(ok), "stop_real": bool(stop),
                   "cls_real": getattr(cls, "classification", None), "force_secondary": bool(k.get("force_secondary")),
                   "is_last_slot": ctx.get("is_last_slot"), "script_version": ctx.get("script_version"), "forced_ng": False,
                   "asr_text_head": (asr_text or "")[:120]}
            want = plan.wants("ja_ng" if kind == "ja" else "ng", clip, slot)
            if want and ok:      # NG方向のみ
                cls2 = copy.copy(cls)
                try:
                    cls2.classification = "TRUE_CONTENT_MISMATCH"
                except Exception:
                    pass
                d = k.get("detail_out")
                if isinstance(d, dict):
                    d["verified"] = False
                    aj = dict(d.get("asr_judgement") or {})
                    aj["forced_ng_by_driver"] = True
                    d["asr_judgement"] = aj
                row["forced_ng"] = True
                rec.overrides.append({"kind": "judge_ng", "clip": clip, "slot": slot, "judge_kind": kind})
                rec.judges.append(row)
                return False, False, cls2
            rec.judges.append(row)
            return res
        return w
    patch(sec, "evaluate_attempt_with_cascade", wrap_judge(sec.evaluate_attempt_with_cascade, "en"))
    patch(jasec, "evaluate_attempt_ja_with_cascade", wrap_judge(jasec.evaluate_attempt_ja_with_cascade, "ja"))

    # ---- 減速後の統一judge再検証のNG化
    _orig_det = sec.evaluate_attempt_with_cascade_detail

    def detail(canonical_text, asr_text, prior_results, wav_path, *a, **k):
        clip = clip_of(wav_path)
        ctx = k.get("attempt_ctx") or {}
        slot = ctx.get("slot") if isinstance(ctx.get("slot"), int) else rec.last_slot.get(clip, 0)
        if plan.by_count and not rec.in_outer:
            rec.post_n[clip] = rec.post_n.get(clip, 0) + 1
            slot = rec.post_n[clip]
        res = _orig_det(canonical_text, asr_text, prior_results, wav_path, *a, **k)
        if rec.in_outer:      # 統一judge(evaluate_attempt_with_cascade)の内部呼出は触らない(減速後の再検証だけが対象)
            return res
        row = {"clip": clip, "slot": slot, "verified_real": bool((res or {}).get("verified")), "forced_ng": False}
        if plan.wants("post_ng", clip, slot) and isinstance(res, dict) and res.get("verified"):
            res = dict(res)
            res["verified"] = False
            res["stop_retrying"] = False
            res["final_status"] = "TRUE_CONTENT_MISMATCH"
            res["human_review_required"] = bool(ctx.get("is_last_slot"))
            aj = dict(res.get("asr_judgement") or {})
            aj["forced_ng_by_driver"] = True
            res["asr_judgement"] = aj
            row["forced_ng"] = True
            rec.overrides.append({"kind": "post_slowdown_ng", "clip": clip, "slot": slot})
        rec.post_judges.append(row)
        return res
    patch(sec, "evaluate_attempt_with_cascade_detail", detail)

    # ---- disfluency gate(ASR一致でもQAのみNG=U-03)
    _orig_dq = dq18.apply_disfluency_gate

    def dq(verified, out_path, language="en", enabled=False, **k):
        res = _orig_dq(verified, out_path, language=language, enabled=enabled, **k)
        clip = clip_of(out_path)
        slot = rec.last_slot.get(clip, 0)
        if enabled and res.get("verified") and plan.wants("dq", clip, slot):
            res = dict(res)
            res["verified"] = False
            ev = dict(res.get("disfluency_evidence") or {})
            ev.update({"forced_ng_by_driver": True, "driver_slot": slot})
            res["disfluency_evidence"] = ev
            rec.overrides.append({"kind": "disfluency_gate_ng", "clip": clip, "slot": slot})
        return res
    patch(dq18, "apply_disfluency_gate", dq)

    try:
        yield rec
    finally:
        for obj, name, val in reversed(saved):
            setattr(obj, name, val)


def stop_scope_check(run_dir: str, out_path: str) -> int:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    r = subprocess.run([sys.executable, "tools/stop_scope_check_01.py", "--managed-id", MANAGEMENT_ID, "--run-dir", run_dir, "--out", out_path],
                       cwd=ROOT, capture_output=True, text=True)
    return r.returncode


def cost_of(raw_usage_log: str) -> dict:
    try:
        import er019_family_x_audio_production_runner_01 as xr
        jpy, by = xr.compute_cost_jpy_so_far(raw_usage_log)
        return {"jpy": round(float(jpy), 3), "by_provider": by}
    except Exception as e:      # noqa: BLE001
        return {"jpy": None, "error": f"{type(e).__name__}: {e}"}


def read_jsonl(path):
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    pass
    return out


def read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def label_style(head: str, full_sha: str) -> str:
    """Style文字列のラベル(観測用。判定には使わない)。"""
    try:
        import er003_v1_repro01_main_generate as repro01
        if repro01.MINIMAL_INSTRUCTION_PREFIX and (head or "").startswith(repro01.MINIMAL_INSTRUCTION_PREFIX[:60]):
            return "MINIMAL_INSTRUCTION_PREFIX"
        if repro01.KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION and (head or "").startswith(repro01.KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION[:60]):
            return "ENGLISH_LOCK"
    except Exception:
        pass
    return ""

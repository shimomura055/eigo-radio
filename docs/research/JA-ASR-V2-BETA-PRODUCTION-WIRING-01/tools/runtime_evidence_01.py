# -*- coding: utf-8 -*-
"""JA-ASR-V2-BETA-PRODUCTION-WIRING-01 委任_02A: runtime evidence harness (E0/E1/E2/E3)。

方針:
  - 実Production経路(`n3_tts.generate_a2_japanese_with_reading_safety` / `er003_v1_repro01_main_generate.generate_narration_snippet_verified_strict` /
    X family `generate_family_x_a2_segments`、実adapter `er007_ja_secondary_asr_01`、実scope `er109_xz_scope_01.run_scope`、実run単位Secondary hook)を呼ぶ。
    **TTSだけ**を、保存済みの実wav(月タイトル6本)を out_path へコピーする偽TTSに置換する(Gemini TTS 0円)。
  - E0: API 0(保存済み転写[Primary=attempt json、Secondary=EVAL記録]を注入)。E1/E2/E3: 実ASR(OpenAI gpt-4o-mini-transcribe + Azure Speech)。
  - 出力は**一時out_dirのみ**。Production results・Store・承認記録・Production監査ログ/HR queueには書かない(test_state_isolation_01で監査ログ/HR queueをtmpへ退避)。
  - 証跡JSONは引数で指定したdirにだけ書く。
使い方(.venv): python -X utf8 runtime_evidence_01.py <phase: e0|e1|e2|e3> <evidence_dir>   (e1/e2/e3 は有料: STOP確認後・費用上限¥20)
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import wave

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
import test_state_isolation_01  # noqa: F401,E402  Production監査ログ(attempt_history)・HR queueをtmpへ退避(import時)

import er003_b1_p9a_audio as p9a  # noqa: E402
import er006_asr_provider_routing_01 as routing  # noqa: E402
import er006_secondary_asr_01 as sec6  # noqa: E402
import er007_ja_secondary_asr_01 as sec  # noqa: E402
import er003_v1_n3_01_tts_generate as n3_tts  # noqa: E402
import er003_v1_repro01_main_generate as repro  # noqa: E402
import er078_pass_with_warning_registry_01 as pww  # noqa: E402
import er109_xz_scope_01 as xz  # noqa: E402

MOON = "月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密"
_A = "er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_{run}/a2/narration/attempts/japanese_title_attempt{n}_{kind}.wav"
# (name, wav, 保存済みPrimary転写[attempt json], 保存済みSecondary転写[EVAL_UNIFIED_03 §1a], 委任文のR-1 OFF期待)
MOON6 = [
    ("ms_03 a1", _A.format(run="ms_03", n=1, kind="customb8f0ff16"), "月野詩は8000句800本超え。その奥に潜む岩の上着の秘密。", "月野市は8900本越え。その奥に潜む岩の上着の秘密。", "HR"),
    ("ms_03 a2", _A.format(run="ms_03", n=2, kind="customb8f0ff16"), "月の死は八千九百本超。その奥に潜む岩の上着の秘密。", "月の詩は8900本超。その奥に潜む岩の上着の秘密。", "PASS_W"),
    ("ms_03 a3", _A.format(run="ms_03", n=3, kind="minimalfallback"), "月の氏は8000900本超。その奥に潜む岩の上着の秘密。", "杉野氏は8900本超。その奥に潜む岩の上着の秘密。", "PASS_W"),
    ("reselect a1", _A.format(run="reselect_01", n=1, kind="customb8f0ff16"), "月野氏は8,900本超。その奥に潜む岩の上着の秘密", "月の詩は8900本ちょ。その奥に潜む岩の上着の秘密。", "PASS_W"),
    ("reselect a2", _A.format(run="reselect_01", n=2, kind="customb8f0ff16"), "月の詩は八千九百本超。その奥に潜む岩の上着の秘密", "月の詩は8900本ちょうその奥に潜む岩の上着の秘密。", "PASS_W"),
    ("reselect a3", _A.format(run="reselect_01", n=3, kind="minimalfallback"), "スギノ市は、八千九百本超、その奥に潜む岩の上着の秘密。", "Sukino氏は8900本超。その奥に潜む岩の上着の秘密。", "HR"),
]
COST_CAP_JPY = 20.0
_STATE = {"net_hosts": {}, "openai_calls": 0, "azure_calls": 0}


def _sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def _dur(p):
    with wave.open(p) as w:
        return w.getnframes() / float(w.getframerate())


# ---------------- 安全装置: 偽TTS / 通信監視 / STOP確認 ----------------
def install_host_guard(block_all: bool):
    real = socket.getaddrinfo

    def counting(host, *a, **k):
        _STATE["net_hosts"][host] = _STATE["net_hosts"].get(host, 0) + 1
        if block_all:
            raise RuntimeError(f"API0 violation: network lookup attempted: {host}")
        if any(x in str(host) for x in ("anthropic", "generativelanguage")):   # TTS(Gemini)・LLMは本evidenceでは呼ばない(偽TTS)。呼ばれたら止める
            raise RuntimeError(f"unexpected paid host in runtime evidence: {host}")
        return real(host, *a, **k)
    socket.getaddrinfo = counting
    return real


def stop_check(label: str, out_dir: str) -> None:
    out = os.path.join(out_dir, f"stop_check_{label}.json")
    cp = subprocess.run([sys.executable, "-X", "utf8", "tools/stop_scope_check_01.py", "--managed-id", "JA-ASR-V2-BETA-PRODUCTION-WIRING-01",
                         "--run-dir", "docs/research/JA-ASR-V2-BETA-PRODUCTION-WIRING-01", "--out", out], cwd=ROOT, capture_output=True, text=True,
                        env=dict(os.environ, PYTHONUTF8="1"))
    if cp.returncode != 0:
        raise SystemExit(f"STOP check rc={cp.returncode}: 新規API呼出なしで停止 ({label})")


def fake_tts(src_wav: str):
    """p9a.generate_narration_snippet の代替: 保存済みwavを out_path へコピーし、実関数と同形のOK結果を返す(TTS API 0)。"""
    def _fake(text, language, out_path, tts_call_fn=None, sleep_function=None, safety_margin_seconds=None, style_prefix_override=None,
              tts_backend="structured_separation"):
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        shutil.copyfile(src_wav, out_path)
        return {"status": "OK", "text": text, "language": language, "path": out_path, "model": "FAKE_TTS(stored wav copy)", "voice": "-", "call_count": 0,
                "retry_count": 0, "sha256": _sha(out_path), "duration_seconds": round(_dur(out_path), 4), "trim_info": {}, "clipping_detected": False,
                "tts_backend": tts_backend, "style_prefix": "<fake>"}
    return _fake


@contextlib.contextmanager
def fake_tts_patch(src_wav):
    """TTSの全入口を偽TTSへ: 標準経路=p9a.generate_narration_snippet、minimal instruction fallback経路=n3_tts._generate_a2_japanese_minimal_instruction
    (後者は別のTTS呼出で標準の偽TTSを通らない。実Gemini TTSへ出ないよう両方を保存wavコピーに置換する。通信監視は実TTSホストへの到達を禁止)。"""
    orig = p9a.generate_narration_snippet
    orig_min = n3_tts._generate_a2_japanese_minimal_instruction
    ft = fake_tts(src_wav)
    p9a.generate_narration_snippet = ft
    n3_tts._generate_a2_japanese_minimal_instruction = lambda text, out_path, tts_backend="structured_separation": ft(text, "ja", out_path, tts_backend=tts_backend)
    try:
        yield
    finally:
        p9a.generate_narration_snippet = orig
        n3_tts._generate_a2_japanese_minimal_instruction = orig_min


@contextlib.contextmanager
def instrumented_asr(stored=None):
    """ASR呼出を数える。stored=(primary_text, azure_text) なら実APIを呼ばず保存済み転写を返す(E0)。"""
    real_tr, real_az = routing.transcribe, sec._azure_stt_strict

    def tr(wav, language, timeout_seconds=90.0, prompt=None):
        _STATE["openai_calls"] += 1
        if stored is not None:
            return stored[0], None
        return real_tr(wav, language=language, timeout_seconds=timeout_seconds, prompt=prompt)

    def az(path, language="ja-JP", timeout_seconds=90, **k):
        _STATE["azure_calls"] += 1
        if stored is not None:
            return stored[1], None
        return real_az(path, language=language, timeout_seconds=timeout_seconds, **k)
    routing.transcribe, sec._azure_stt_strict = tr, az
    try:
        yield
    finally:
        routing.transcribe, sec._azure_stt_strict = real_tr, real_az


# ---------------- 結果の要約 ----------------
_LOG_KEYS = ("attempts_log", "standard_attempts_log", "fallback_attempts_log")


def _all_judgements(res: dict) -> list:
    """成功entryは`attempts_log`、family fallback経路は`standard_attempts_log`+`fallback_attempts_log`に判定recordを持つ。全attemptの判定を集める。"""
    out = []
    for k in _LOG_KEYS:
        out += [a["asr_judgement"] for a in (res.get(k) or []) if isinstance(a, dict) and a.get("asr_judgement")]
    if res.get("asr_judgement") and not out:
        out.append(res["asr_judgement"])
    return out


def _judgement(res: dict) -> dict:
    """採用(または最後)の判定record。"""
    if res.get("asr_judgement"):
        return res["asr_judgement"]
    js = _all_judgements(res)
    return js[-1] if js else {}


def summarize(label, scope, wav, canon, res, rs) -> dict:
    j = _judgement(res)
    js = _all_judgements(res)
    v2 = j.get("ja_v2beta") or {}
    est = sum(float(((x.get("cost") or {}).get("est_jpy")) or 0.0) for x in js)
    return {
        "label": label, "scope": scope, "wav": wav, "wav_sha256": _sha(wav) if wav and os.path.exists(wav) else None, "canonical_text": canon,
        "status": res.get("status"), "asr_verified": res.get("asr_verified"), "fallback_used": res.get("fallback_used"),
        "state": j.get("state"), "verdict": j.get("verdict"), "reason_code": j.get("reason_code"), "rescue_basis": j.get("rescue_basis"),
        "rescue_reason_ja": j.get("rescue_reason_ja"), "judge_rule_version": j.get("judge_rule_version"), "warnings": j.get("warnings"),
        "primary_text": (j.get("primary") or {}).get("text"), "secondary_text": (j.get("secondary") or {}).get("text"),
        "secondary_called": (j.get("secondary") or {}).get("called"), "secondary_engine": (j.get("secondary") or {}).get("engine"),
        "r5": j.get("r5"), "primary_model": (j.get("primary") or {}).get("model"),
        "ja_v2beta_layers": v2.get("layers"), "ja_v2beta_error": v2.get("error"), "beta": v2.get("beta"), "weak_rank": v2.get("weak_rank"),
        "attempts": len(res.get("attempts_log") or []) or None,
        "audit_cost_est_jpy_sum": round(est, 4),
        "audit_cost": j.get("cost"),
        "run_state": ({"secondary_calls": rs.secondary_calls, "est_jpy_total": round(rs.est_jpy_total, 4),
                       "consecutive_failures": rs.secondary_consecutive_failures, "circuit_open": rs.circuit_open} if rs is not None else None),
        "asr_judgement": j,
    }


def verified_strict(canon, wav, scope, work, tag, max_attempts=1, stored=None):
    """formal strict経路(既定1 attempt): 偽TTS+実(またはE0なら保存)ASR。"""
    out = os.path.join(work, f"{tag}.wav")
    rs = sec6.begin_secondary_run()
    try:
        with fake_tts_patch(wav), instrumented_asr(stored), (xz.run_scope(scope) if scope else contextlib.nullcontext()):
            res = repro.generate_narration_snippet_verified_strict(
                canon, "ja", out, n3_tts.expected_substring_ja(canon), max_attempts=max_attempts, max_extra_chars=30)
        return summarize(tag, scope, wav, canon, res, rs), res
    finally:
        sec6.end_secondary_run()


def formal_a2(canon, wav, scope, work, tag, stored=None, max_attempts=1):
    """Family共通のSection生成入口 `n3_tts.generate_a2_japanese_with_reading_safety`(X/Y/Zの全日本語Sectionがこれを呼ぶ)。"""
    out = os.path.join(work, f"{tag}.wav")
    rs = sec6.begin_secondary_run()
    try:
        with fake_tts_patch(wav), instrumented_asr(stored), (xz.run_scope(scope) if scope else contextlib.nullcontext()):
            res = n3_tts.generate_a2_japanese_with_reading_safety(canon, out, n3_tts.expected_substring_ja(canon), max_extra_chars=30,
                                                                   max_attempts=max_attempts)
        return summarize(tag, scope, wav, canon, res, rs), res
    finally:
        sec6.end_secondary_run()


def hook_outputs(run_dir, label_text, seg_entry, extra_segments=None):
    """Family完了hookと同じ関数: 事後試聴リストJSON+最終制作報告ブロック(標準出力)+試聴ページ節HTMLを生成。
    extra_segments={segment_id: entry}: 追加segment(例: E1の実judgement recordから作ったβ例)。"""
    os.makedirs(os.path.join(run_dir, "audit"), exist_ok=True)
    segs = {"japanese_title": dict(seg_entry, segment_id="japanese_title", role="japanese_title", level="a2")}
    for sid, e in (extra_segments or {}).items():
        segs[sid] = dict(e, segment_id=sid, role=sid, level="a2")
    doc = {"segments": segs}
    with open(os.path.join(run_dir, "audit", "tts_generation_results.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1, default=str)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rep = pww.write_listening_list_safe(run_dir, completion_label=label_text)
    lst = json.load(open(rep["json"], encoding="utf-8")) if rep.get("json") else None
    html = pww.render_html_section(pww.load_listening_list(run_dir), href_fn=lambda e: e.get("audio_path") or "")
    return {"hook_report": {k: v for k, v in rep.items() if k != "completion_block"}, "completion_block_stdout": buf.getvalue(),
            "listening_list_json": lst, "section_html": html}


def run_e0(work, out_dir):
    """E0: API 0。保存済み転写を実adapter(X scope)へ注入。月6本が 4 PASS_W / 2 HR になること。"""
    install_host_guard(block_all=True)
    rows = []
    for name, wav, prim, azt, exp in MOON6:
        s, _ = verified_strict(MOON, wav, "X", work, "e0_" + name.replace(" ", "_"), stored=(prim, azt))
        s["expected"], s["match_expected"] = exp, (s["verdict"] == exp)
        rows.append(s)
    # E5: 同じ保存済み転写を scope外(None=A/B/C相当)で判定 -> 新キー(ja_v2beta/verdict/rescue_basis/judge_rule_version)が無く、従来(L0)判定のまま
    scope_none = []
    for name, wav, prim, azt, exp in MOON6:
        s, _ = verified_strict(MOON, wav, None, work, "e5_none_" + name.replace(" ", "_"), stored=(prim, azt))
        s["has_new_keys"] = {k: (k in (s["asr_judgement"] or {})) for k in ("ja_v2beta", "verdict", "rescue_basis", "judge_rule_version")}
        scope_none.append(s)
    return {"phase": "E0", "api": 0, "rows": rows, "scope_none_rows": scope_none, "openai_calls_stub": _STATE["openai_calls"], "azure_calls_stub": _STATE["azure_calls"],
            "net_hosts_attempted": _STATE["net_hosts"]}


def main():
    phase, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    work = tempfile.mkdtemp(prefix="ja_v2beta_rt_")
    if phase == "e0":
        res = run_e0(work, out_dir)
    else:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import runtime_evidence_paid_01 as paid   # noqa: E402
        res = paid.run(phase, work, out_dir, sys.modules[__name__])
    p = os.path.join(out_dir, f"runtime_evidence_{phase}_01.out.json")
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, ensure_ascii=False, indent=1, sort_keys=True, default=str)
    print("wrote", p, "work_dir", work)


if __name__ == "__main__":
    main()

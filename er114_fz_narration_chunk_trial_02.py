# -*- coding: utf-8 -*-
"""FZ-NARRATION-CHUNK-TTS-TRIAL-01 委任_02 (DEV/Trial専用。Production配線なし・Production file編集0)。

Phase 1 runner: Opus条件A必須N1〜N4を反映した隔離・生成・組立・計測。
  pre   : 無料の事前確認(Ledger事前計算[N1]、モジュール同一性[N2]、TTS入力同値、Style/Voice同一性、A側Gate状態)
  gen   : 有料生成(--arm A_r2|B_r1|B_fine|B_alt)。audit hook[N2]・sink隔離[N1]・上限30円の予約方式。
  post  : DEV assembler[N3]・計測[N4,R4]・mp3・試聴ページ(API 0。ASRはローカルfaster-whisperのみ)

隔離の考え方(N1/N2):
  - Production sinkはX Trialで検証済みの `redirect_production_sinks`(er113)をそのまま再利用(コピー実装しない)。
  - `sys.addaudithook`で自プロセスの書込みopen/remove/rename/mkdir/copyfile/Popenを記録し、許可dir外への書込みは例外で阻止+即STOP。
  - sha比較・mtime走査は補助(差分→STOP・事実報告、自動続行なし)。
  - 起動前に、importされるrepo moduleのgit未commit差分を確認(TTS/組立経路moduleが未commitなら待機→解消しなければSTOP)。
設計正本: docs/research/FZ-NARRATION-CHUNK-TTS-TRIAL-01/DESIGN_01.md
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time

import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

MANAGED_ID = "FZ-NARRATION-CHUNK-TTS-TRIAL-01"
CAP_JPY = 30.0
OUT = "er026_output/family_z_dev_trials/fz_narration_chunk_01"
PAGE_DIR = "user_test/fz_narration_chunk_trial_01"
A_RUN = "er026_output/family_z_dev_trials/fz_essence_01/the_tell_tale_heart/1b_s1"
A_LEVEL = f"{A_RUN}/b1b"
A_NARR = f"{A_LEVEL}/narration"
STORY_KEY = "the_tell_tale_heart"
CLIP_IDS = ("full_story_part1_c1", "full_story_part2_c3", "full_story_part3_c1")
PART_OF = {"full_story_part1_c1": 1, "full_story_part2_c3": 2, "full_story_part3_c1": 3}
SR24 = 24000
SR48 = 48000
RAW_LOG = f"{OUT}/raw_usage_log.jsonl"
# 見積(DESIGN_01 §6、X Trial実績ベース)。予約額 = 見積 x RESERVE_FACTOR(retry・NER・Azure余裕)
EST_JPY = {"A_r2": 4.0, "B_r1": 4.3, "B_fine": 4.3, "B_alt": 3.0}
RESERVE_FACTOR = 1.5
PLAN_FILES = {
    "B_r1": f"{OUT}/chunk_plan_tth_1b_s1_adv_01.json",
    "B_fine": f"{OUT}/chunk_plan_tth_1b_s1_adv_B_fine_01.json",
    "B_alt": f"{OUT}/chunk_plan_tth_1b_s1_adv_B_alt_manual_01.json",
}
# 各armのclipごとの音声ソース(B_altのpart1_c1はB_r1のchunk音声を再利用)
ARM_SOURCE = {
    "A": {c: "A" for c in CLIP_IDS},
    "A_r2": {c: "A_r2" for c in CLIP_IDS},
    "B_r1": {c: "B_r1" for c in CLIP_IDS},
    "B_fine": {c: "B_fine" for c in CLIP_IDS},
    "B_alt": {"full_story_part1_c1": "B_r1", "full_story_part2_c3": "B_alt", "full_story_part3_c1": "B_alt"},
}
EXTRA_PAUSE = 0.2
FIXED_TARGET_RMS_SOURCE = f"{A_LEVEL}/assembly/timeline.json"  # gain_report.target_rms (N3-1)

import er113_fx_paragraph_chunk_trial_01 as X   # noqa: E402  (隔離・計測の再利用。Xの挙動は変更しない)
import er114_fz_narration_chunk_trial_01 as P   # noqa: E402


# ============================================================
# 共通
# ============================================================
def now_jst() -> str:
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(timespec="seconds")


def jload(rel):
    return X.load_json(rel)


def jsave(rel, obj):
    X.save_json(rel, obj)


def sha(rel):
    return X.sha256_file(rel)


def assert_cwd_is_root():
    X.assert_cwd_is_root()


# ============================================================
# N2: audit hook(自プロセスの書込みを記録し、許可dir外は例外で阻止)
# ============================================================
_AUDIT = {"on": False, "allowed": [], "writes": {}, "violations": [], "popen": [], "n_events": 0}
_WRITE_EVENTS = {"os.remove", "os.rename", "os.mkdir", "os.rmdir", "shutil.copyfile", "shutil.copymode", "shutil.copystat",
                 "shutil.copytree", "shutil.rmtree", "shutil.move", "os.truncate", "os.chmod", "os.utime"}


def _is_write_open(mode, flags) -> bool:
    if isinstance(mode, str) and any(c in mode for c in "wax+"):
        return True
    if isinstance(flags, int) and (flags & (os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_TRUNC)):
        return True
    return False


def _norm(p) -> str | None:
    try:
        if isinstance(p, int):
            return None
        if isinstance(p, bytes):
            p = os.fsdecode(p)
        return os.path.normcase(os.path.realpath(os.path.abspath(os.fspath(p))))
    except Exception:
        return None


def _allowed(np_: str) -> bool:
    if np_ is None:
        return True
    if "__pycache__" in np_ or np_.endswith(".pyc") or np_ == os.path.normcase("nul") or np_.endswith(os.sep + "nul"):
        return True
    return any(np_ == a or np_.startswith(a + os.sep) for a in _AUDIT["allowed"])


def _audit_hook(event, args):
    if not _AUDIT["on"]:
        return
    try:
        paths = []
        if event == "open":
            path, mode, flags = args[0], args[1], args[2]
            if not _is_write_open(mode, flags):
                return
            paths = [path]
        elif event in _WRITE_EVENTS:
            paths = [a for a in args if isinstance(a, (str, bytes, os.PathLike))][:2]
            if event in ("os.chmod", "os.utime", "os.mkdir", "os.rmdir", "os.remove", "os.truncate", "shutil.rmtree"):
                paths = paths[:1]
            if event.startswith("shutil.") and event not in ("shutil.rmtree",):
                paths = paths[1:2]   # コピー/移動は書込み先(dst)のみ検査(読取元は対象外)
        elif event == "subprocess.Popen":
            _AUDIT["popen"].append(" ".join(str(x) for x in (args[1] if len(args) > 1 else []))[:300])
            return
        elif event == "os.system":
            _AUDIT["popen"].append("os.system:" + str(args[0])[:300])
            return
        else:
            return
        _AUDIT["n_events"] += 1
        for p in paths:
            np_ = _norm(p)
            if np_ is None:
                continue
            rel = os.path.relpath(np_, os.path.normcase(os.path.realpath(ROOT))).replace("\\", "/") if np_.startswith(os.path.normcase(os.path.realpath(ROOT))) else np_
            d = os.path.dirname(rel) or "."
            key = f"{event}:{d}"
            _AUDIT["writes"][key] = _AUDIT["writes"].get(key, 0) + 1
            if not _allowed(np_):
                _AUDIT["violations"].append({"event": event, "path": rel})
                raise PermissionError(f"[AUDIT STOP] 許可dir外への書込み/変更を阻止: {event} {rel}")
    except PermissionError:
        raise
    except Exception:
        return


_HOOK_INSTALLED = False


def install_audit(allowed_rel: list, allowed_abs: list = ()):
    global _HOOK_INSTALLED
    _AUDIT["allowed"] = [os.path.normcase(os.path.realpath(os.path.join(ROOT, r))) for r in allowed_rel] + \
                        [os.path.normcase(os.path.realpath(a)) for a in allowed_abs] + \
                        [os.path.normcase(os.path.realpath(tempfile.gettempdir()))]
    _AUDIT["writes"], _AUDIT["violations"], _AUDIT["popen"], _AUDIT["n_events"] = {}, [], [], 0
    if not _HOOK_INSTALLED:
        sys.addaudithook(_audit_hook)
        _HOOK_INSTALLED = True
    _AUDIT["on"] = True


def audit_report() -> dict:
    return {"n_write_events": _AUDIT["n_events"], "writes_by_event_dir": dict(sorted(_AUDIT["writes"].items())),
            "violations": list(_AUDIT["violations"]), "popen": list(_AUDIT["popen"]), "allowed_roots": [os.path.relpath(a, os.path.normcase(os.path.realpath(ROOT))) if a.startswith(os.path.normcase(os.path.realpath(ROOT))) else a for a in _AUDIT["allowed"]]}


# ============================================================
# N2: モジュール同一性(git未commit差分の検知)
# ============================================================
def _loaded_repo_modules() -> dict:
    mods = {}
    root_n = os.path.normcase(os.path.realpath(ROOT))
    for name, m in list(sys.modules.items()):
        f = getattr(m, "__file__", None)
        if not f or not str(f).endswith(".py"):
            continue
        ap = os.path.normcase(os.path.realpath(f))
        if not ap.startswith(root_n + os.sep):
            continue
        rel = os.path.relpath(ap, root_n).replace("\\", "/")
        if rel.startswith((".venv/", ".git/")):
            continue
        mods[rel] = name
    return mods


def git_dirty(paths: list) -> list:
    if not paths:
        return []
    r = subprocess.run(["git", "status", "--porcelain", "--"] + sorted(paths), cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    return [ln for ln in r.stdout.splitlines() if ln.strip()]


def module_identity(paths: list | None = None) -> dict:
    mods = _loaded_repo_modules() if paths is None else {p: p for p in paths}
    shas = {rel: sha(rel) for rel in sorted(mods)}
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return {"git_head": head, "n_modules": len(shas), "sha256": shas, "uncommitted": git_dirty(list(shas))}


def warmup_imports() -> None:
    """TTS・組立経路で使うProduction moduleを(API呼出なしで)import。real_generators()はmodule importとclosure定義のみ。"""
    import er063_family_z_audio_01 as z   # noqa: F401
    z.real_generators()
    import er003_v1_n3_01_assemble  # noqa: F401
    import er003_b1_p9a_audio  # noqa: F401
    import er013_family_c_production_runner_01  # noqa: F401
    import er103_pnap_runner_hooks_01  # noqa: F401
    import er103_run_entity_table_01  # noqa: F401
    import er019_family_x_audio_production_runner_01  # noqa: F401  (compute_cost_jpy_so_far)
    import er062_family_z_structure_01  # noqa: F401
    import er025_entity_pronunciation_resolver_core_01  # noqa: F401
    import er020_tts_retry_local_rewrite_01  # noqa: F401
    import er006_secondary_asr_01  # noqa: F401
    import er011_human_review_lock_01  # noqa: F401
    import er006_pronunciation_ledger_01  # noqa: F401
    import er006_pronunciation_tts_injection_01  # noqa: F401
    import er021_en_asr_semantic_equivalence_production_01  # noqa: F401


def wait_modules_clean(path_list_file: str, max_wait_s: int = 1800, interval_s: int = 300) -> dict:
    """起動前確認。記録済みmodule setにgit未commit差分があれば最大30分(5分間隔)待ち、解消しなければSTOP。"""
    paths = list(jload(path_list_file)["sha256"].keys())
    waited, log = 0, []
    while True:
        dirty = git_dirty(paths)
        log.append({"t": now_jst(), "dirty": dirty})
        if not dirty:
            return {"clean": True, "waited_s": waited, "log": log}
        if waited >= max_wait_s:
            raise SystemExit(f"[STOP] TTS/組立経路moduleに未commit差分が{max_wait_s}s解消しない: {dirty}")
        print(f"[WAIT] module dirty {dirty} -> {interval_s}s後に再確認", flush=True)
        time.sleep(interval_s)
        waited += interval_s


# ============================================================
# 他agentのZ TTS稼働確認(直列化)・STOP scope check
# ============================================================
def other_z_tts_processes() -> list:
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command",
                              "Get-CimInstance Win32_Process -Filter \"name='python.exe'\" | ForEach-Object { \"$($_.ProcessId)`t$($_.CommandLine)\" }"],
                             capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
    except Exception as e:  # noqa: BLE001
        return [f"process_list_failed:{e}"]
    hits = []
    me = str(os.getpid())
    for ln in out.splitlines():
        if not ln.strip():
            continue
        pid, _, cmd = ln.partition("\t")
        low = cmd.lower()
        if pid in (me, str(os.getppid())) or "run_project_regression" in low:
            continue
        if any(k in low for k in ("er026", "er063", "family_z", "fz_essence", "run_sf_prod", "er114_fz", "tts")):
            hits.append(f"{pid}:{cmd[:200]}")
    return hits


def stop_check(tag: str) -> None:
    out = f"{OUT}/stop_check_{tag}.json"
    r = subprocess.run([sys.executable, "tools/stop_scope_check_01.py", "--managed-id", MANAGED_ID, "--run-dir", OUT, "--out", out], cwd=ROOT)
    if r.returncode == 3:
        raise SystemExit("[STOP] stop_scope_check rc=3(STOP適用)")
    if r.returncode != 0:
        raise SystemExit(f"[STOP] stop_scope_check 異常 rc={r.returncode}")


# ============================================================
# 保護store(sha比較は補助)
# ============================================================
PROTECTED_STORES = tuple(X.PROTECTED_STORES)
PROTECTED_TREES = (A_RUN, "er011_output/local_rewrite_recovery", "er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_sf_prod_01",
                   "user_test/fx_paragraph_chunk_trial_01")
# 監視対象外(別agentが書込み中の領域): er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_sf_prod_02 ほか。自プロセスは書かない(audit hookが証明)。


def snapshot() -> dict:
    s = {p: sha(p) for p in PROTECTED_STORES}
    s.update({f"tree:{t}": X.tree_digest(t) for t in PROTECTED_TREES if os.path.exists(os.path.join(ROOT, t))})
    return s


def diff_snap(a: dict, b: dict) -> list:
    return [k for k in a if a[k] != b.get(k)]


# ============================================================
# 入力(A側)・plan
# ============================================================
def a_target_rms() -> float:
    """N3-1: target_rmsは1b_s1のtimeline.json gain_report.target_rms(0.07332)に固定。再計算でchunkのRMSを使わない。"""
    return float(jload(FIXED_TARGET_RMS_SOURCE)["gain_report"]["target_rms"])


def segment_clips() -> list:
    return jload(f"{A_RUN}/segment_plan_b1b.json")["clips"]


def a_results() -> dict:
    return jload(f"{A_LEVEL}/audit/tts_generation_results.json")


def load_arm_plan(arm: str) -> dict:
    """arm -> {clip_id: [chunk dicts(chunk_id, words, text)]} (A_r2は各clip=1 chunk(元text))。"""
    clips = {c["id"]: c for c in segment_clips()}
    if arm == "A_r2":
        return {cid: [{"chunk_id": cid, "words": clips[cid]["word_count"], "text": clips[cid]["text"]}] for cid in CLIP_IDS}
    pl = jload(PLAN_FILES[arm])
    out = {}
    for c in pl["clips"]:
        if c["clip_id"] in CLIP_IDS and c["split"]:
            out[c["clip_id"]] = c["chunks"]
    if arm in ("B_r1", "B_fine"):
        assert set(out) == set(CLIP_IDS), f"{arm}: 3 clip全てが分割対象のはず"
    if arm == "B_alt":
        assert set(out) == {"full_story_part2_c3", "full_story_part3_c1"}
    return out


def arm_items(arm: str) -> list:
    items = []
    for cid, chunks in load_arm_plan(arm).items():
        for ch in chunks:
            items.append({"chunk_id": ch["chunk_id"], "clip_id": cid, "part": PART_OF[cid], "text": ch["text"], "words": ch["words"]})
    return items


def make_spec(it: dict):
    import er063_family_z_audio_01 as z
    return z.ClipSpec(it["clip_id"], "b1b", "narrator", it["text"], voice="Aoede", speaker="narrator",
                      role_key="NARRATOR_FULL_STORY_ADV", part=it["part"], language="en")


def gen_wav_rel(src_arm: str, it_or_chunk_id, clip_id: str | None = None) -> str:
    chunk_id = it_or_chunk_id if isinstance(it_or_chunk_id, str) else it_or_chunk_id["chunk_id"]
    cid = clip_id or (it_or_chunk_id["clip_id"] if not isinstance(it_or_chunk_id, str) else chunk_id)
    return f"{OUT}/gen/{src_arm}/{chunk_id}/b1b/narration/{cid}.wav"


# ============================================================
# N1: Ledger事前計算(Z版。Xのledger_preflightと同じ呼出をZのTTS入力・Z Styleで行う)
# ============================================================
def ledger_preflight(arms=("A_r2", "B_r1", "B_fine", "B_alt")) -> dict:
    import er006_pronunciation_ledger_01 as ledger
    import er006_pronunciation_tts_injection_01 as inj
    import er063_family_z_audio_01 as z
    import er103_proper_noun_alarm_policy_01 as pol
    out = {"ledger_path": ledger.LEDGER_PATH, "ledger_sha256": sha(ledger.LEDGER_PATH), "items": {}, "all_empty": True}
    before = sha(ledger.LEDGER_PATH)
    seen = set()
    with pol.run_scope("Z"):          # 実生成と同じ run scope(固有名詞発音供給はscope内で有効)
        for arm in arms:
            for it in arm_items(arm):
                spec = make_spec(it)
                style = z.style_text_for(spec)
                tts_input = z._norm_for_tts(spec)
                key = (it["clip_id"], tts_input)
                if key in seen:
                    continue
                seen.add(key)
                _, hits = inj.augment_style_prefix_with_pronunciation(style, tts_input, min_confidence="medium")
                low = [e for e in ledger.get_low_confidence_entries_for_text(tts_input, exclude_entity_types={ledger.CASCADE_UNRESOLVED_ENTITY_TYPE})
                       if e.get("confidence") == "low" and e.get("entity_type") != ledger.JA_READING_ENTITY_TYPE]
                asr_phr = [h["canonical_spelling"] for h in ledger.get_hint_for_text(tts_input, min_confidence="low")]
                rec = {"arm": arm, "hints_medium_plus": [h.get("surface") for h in hits], "low_confidence_research_targets": [e["surface"] for e in low],
                       "asr_ledger_phrases_low_plus": asr_phr, "tts_input_sha256": hashlib.sha256(tts_input.encode()).hexdigest()}
                out["items"][f"{arm}:{it['chunk_id']}"] = rec
                if rec["hints_medium_plus"] or rec["low_confidence_research_targets"] or rec["asr_ledger_phrases_low_plus"]:
                    out["all_empty"] = False
    out["ledger_unchanged_by_preflight"] = (before == sha(ledger.LEDGER_PATH))
    return out


def tts_input_equivalence() -> dict:
    """B(chunk結合)のTTS入力がA(clip全体)のTTS入力と空白差を除いて同一か(分割以外の本文差がないこと)。"""
    import er063_family_z_audio_01 as z
    import er103_proper_noun_alarm_policy_01 as pol
    clips = {c["id"]: c for c in segment_clips()}
    res = {}
    with pol.run_scope("Z"):
        for arm in ("B_r1", "B_fine", "B_alt"):
            for cid, chunks in load_arm_plan(arm).items():
                spec_a = z.ClipSpec(cid, "b1b", "narrator", clips[cid]["text"], voice="Aoede", role_key="NARRATOR_FULL_STORY_ADV", part=PART_OF[cid])
                a_in = " ".join(z._norm_for_tts(spec_a).split())
                b_in = " ".join(" ".join(z._norm_for_tts(make_spec({"clip_id": cid, "part": PART_OF[cid], "text": ch["text"]})) for ch in chunks).split())
                res[f"{arm}:{cid}"] = (a_in == b_in)
    return res


def style_voice_identity() -> dict:
    import er063_family_z_audio_01 as z
    r = a_results()["segments"]
    spec = make_spec({"clip_id": CLIP_IDS[0], "part": 1, "text": "x", "chunk_id": CLIP_IDS[0]})
    style = z.style_text_for(spec)
    cur = hashlib.sha256(style.encode("utf-8")).hexdigest()
    out = {"current_style_sha256": cur, "style_version": z.FAMILY_Z_ROLE_STYLE_VERSION, "a_style_version": a_results().get("style_version"), "clips": {}}
    ok = out["style_version"] == out["a_style_version"]
    for cid in CLIP_IDS:
        e = r[cid]
        same = (e["style"]["style_prefix_sha256"] == cur)
        out["clips"][cid] = {"a_status": e["status"], "a_voice": e["voice"], "a_model_ids": e["model_ids_measured"], "a_style_sha256": e["style"]["style_prefix_sha256"],
                             "style_equal": same, "a_attempts": len(e["attempts"]), "a_asr_state": (e.get("asr_judgement") or {}).get("state"),
                             "a_audio_sha256": e["sha256"], "a_role": e["role"], "a_tts_backend": e["tts_backend"], "a_speed_profile": (e.get("speed_profile") or {}).get("profile")}
        ok = ok and same and e["status"] == "OK" and e["voice"] == "Aoede"
    out["all_equal"] = ok
    return out


def a_gate_hr_state() -> dict:
    """1b_s1 Adv音声のGate/HR状態(確認事項)。"""
    gate = jload(f"{A_LEVEL}/audit/gate_result_04C.json")
    rl = jload(f"{A_LEVEL}/audit/review_lock_state.json")
    pww = jload(f"{A_LEVEL}/audit/pass_with_warning_listening_list.json")
    st = {}
    for cid in CLIP_IDS:
        v = rl.get(cid) or {}
        st[cid] = {"review_lock_state": v.get("state"), "final_status": v.get("final_status"), "cumulative_tts_attempts": v.get("cumulative_tts_attempts")}
    return {"m2_complete": gate.get("m2_complete"), "z_speed_profile_ok": {k: v.get("ok") for k, v in (gate.get("z_speed_profile") or {}).get("clips", {}).items()},
            "audio_text_deviation_clips": gate.get("audio_text_deviation_clips"), "gate_keys": sorted(gate.keys()),
            "review_lock": st, "pass_with_warning_count": pww.get("count"),
            "human_review_queue_entries_for_1b_s1": "(Production HR queueはsink隔離のため本Trialでは書かない)"}


def cmd_pre(args) -> None:
    assert_cwd_is_root()
    os.makedirs(os.path.join(ROOT, OUT), exist_ok=True)
    warmup_imports()
    ident = module_identity()
    jsave(f"{OUT}/module_set_01.json", ident)
    led = ledger_preflight()
    eq = tts_input_equivalence()
    sv = style_voice_identity()
    gate = a_gate_hr_state()
    res = {"ts": now_jst(), "module_identity_uncommitted": ident["uncommitted"], "n_modules": ident["n_modules"], "git_head": ident["git_head"],
           "ledger_preflight_all_empty": led["all_empty"], "ledger_unchanged_by_preflight": led["ledger_unchanged_by_preflight"],
           "ledger_sha256": led["ledger_sha256"], "tts_input_equivalence": eq, "style_voice_identity": sv, "a_gate_hr_state": gate,
           "target_rms_fixed": a_target_rms(), "other_z_tts_processes": other_z_tts_processes()}
    jsave(f"{OUT}/preflight_01.json", {**res, "ledger_items": led["items"]})
    print(json.dumps(res, ensure_ascii=False, indent=1)[:6000])


# ============================================================
# 生成(有料)
# ============================================================
def spent_jpy() -> tuple:
    import er019_family_x_audio_production_runner_01 as runner
    return runner.compute_cost_jpy_so_far(os.path.join(ROOT, RAW_LOG))


def raw_log_by_provider() -> dict:
    p = os.path.join(ROOT, RAW_LOG)
    c = {}
    if os.path.exists(p):
        for ln in open(p, encoding="utf-8"):
            if ln.strip():
                r = json.loads(ln)
                k = f"{r.get('provider')}/{r.get('model_id') or r.get('model')}"
                c[k] = c.get(k, 0) + 1
    return c


def cmd_gen(args) -> None:
    arm = args.arm
    assert arm in EST_JPY, arm
    assert_cwd_is_root()
    # TTS実行mode: Z production runnerの既定(--tts-execution-mode STANDARD、er026:2315)と同一にそろえる。
    # 未設定だとer006_batch_tts_wiringの既定=BATCHになり、Aと条件が違う(委任_02で初回起動時に発見・修正)。
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    # --- 起動前: STOP / 他Z TTS / module未commit(待機)---
    stop_check(arm)
    others = other_z_tts_processes()
    if others:
        raise SystemExit(f"[STOP] 他のZ TTS/関連processが稼働中(直列化): {others}")
    mod_set_file = f"{OUT}/module_set_01.json"
    clean = wait_modules_clean(mod_set_file)
    warmup_imports()
    ident0 = module_identity()
    recorded = jload(mod_set_file)["sha256"]
    changed = {k: (recorded[k], ident0["sha256"].get(k)) for k in recorded if ident0["sha256"].get(k) != recorded[k]}
    if changed or ident0["uncommitted"]:
        raise SystemExit(f"[STOP] module同一性: 記録とshaが違う/未commit {changed} {ident0['uncommitted']}")
    # --- 上限(予約方式) ---
    import er005_cost_logger as cl
    cl.install(os.path.join(ROOT, RAW_LOG))
    spent0, byp0 = spent_jpy()
    reserve = EST_JPY[arm] * RESERVE_FACTOR
    if spent0 + reserve > CAP_JPY:
        raise SystemExit(f"[STOP] 予約額超過: 累計{spent0:.2f}+予約{reserve:.2f}>{CAP_JPY}")
    # --- N1: Ledger事前計算(空でなければSTOP。条件差) ---
    led = ledger_preflight((arm,))
    if not led["all_empty"] or not led["ledger_unchanged_by_preflight"]:
        jsave(f"{OUT}/ledger_preflight_STOP_{arm}.json", led)
        raise SystemExit("[STOP] Ledger事前計算が空でない(条件差)。Fableへ報告")
    eq = tts_input_equivalence()
    if not all(eq.values()):
        raise SystemExit(f"[STOP] TTS入力がAと同値でない: {eq}")
    sv = style_voice_identity()
    if not sv["all_equal"]:
        raise SystemExit(f"[STOP] Style/Voice/Model同一性NG: {sv}")
    # --- 隔離・audit hook ---
    before = snapshot()
    since_ts = time.time()
    # 許可root: OUT + HuggingFace model cache(Production secondary ASRのfaster-whisper small読込がrefs/lockを触る。公開モデルのcacheでrepo/Production状態ではない。初回起動で発見)
    install_audit([OUT], [os.path.join(os.path.expanduser("~"), ".cache", "huggingface")])
    res = {"arm": arm, "started_jst": now_jst(), "spent_before": round(spent0, 3), "reserve": reserve, "chunks": {},
           "tts_execution_mode": os.environ.get("TTS_EXECUTION_MODE")}
    items = arm_items(arm)
    import er063_family_z_audio_01 as z
    import er078_secondary_run_scope_01 as secondary_run_scope
    import er109_xz_scope_01 as er109_scope
    import er103_pnap_runner_hooks_01 as hooks
    import er103_run_entity_table_01 as ret
    import er020_tts_retry_local_rewrite_01 as retry_primitive
    run_dir = f"{OUT}/gen/{arm}"
    specs = [make_spec(it) for it in items]
    gens = z.real_generators()
    stop_reason = {"v": None}

    def body():
        for it, spec in zip(items, specs):
            spent, _ = spent_jpy()
            if spent >= CAP_JPY:
                stop_reason["v"] = f"cap到達 {spent:.2f}"
                return
            if _AUDIT["violations"]:
                stop_reason["v"] = "audit violation"
                return
            wav = gen_wav_rel(arm, it)
            os.makedirs(os.path.dirname(os.path.join(ROOT, wav)), exist_ok=True)
            tts_input = z._norm_for_tts(spec)
            n_lr0 = len(X.LR_EVENTS)
            t0 = time.time()
            t0_iso = now_jst()
            with cl.segment_context(it["chunk_id"]):
                r = gens["narrator"](spec, os.path.join(ROOT, wav)) or {}
            el = time.time() - t0
            attempts = r.get("attempts_log") or []
            lr = r.get("local_rewrite_recovery")
            canon_before = r.get("canonical_text_before_local_rewrite")
            pron = r.get("en_pronunciation_resolver_info") or {}
            fb = r.get("instruction_type") == "minimal_fallback" or any((a_.get("instruction_type") == "minimal_fallback") for a_ in attempts if isinstance(a_, dict))
            cond = []
            if lr:
                cond.append("local_rewrite_recovery")
            if canon_before is not None and canon_before != tts_input:
                cond.append("text_changed")
            if fb:
                cond.append("minimal_fallback_style")
            if pron.get("hints_applied") or pron.get("low_confidence_retry_attempted"):
                cond.append("pronunciation_hint_or_research")
            style_used = r.get("style_prefix")
            want_style = z.style_text_for(spec)
            cool = r.get("cooldown_events") or []
            res["chunks"][it["chunk_id"]] = {
                "clip_id": it["clip_id"], "words": it["words"], "status": r.get("status"), "path": wav, "wav_sha256": sha(wav),
                "tts_input_sha256": hashlib.sha256(tts_input.encode()).hexdigest(), "attempts": len(attempts),
                "audio_classification": r.get("audio_classification"), "repetition_qa_checked": r.get("repetition_qa_checked"),
                "trim_info": r.get("trim_info"), "asr_judgement_state": (r.get("asr_judgement") or {}).get("state"),
                "instruction_type": r.get("instruction_type"), "minimal_fallback_used": fb,
                "local_rewrite_recovery": ({"status": lr.get("status"), "ng_span": lr.get("ng_span")} if lr else None),
                "canonical_text_before_local_rewrite": canon_before, "en_pronunciation_resolver_info": pron,
                "style_prefix_sha256": hashlib.sha256((style_used or "").encode()).hexdigest() if style_used else None,
                "style_equals_A_style": (style_used == want_style) if style_used else None,
                "tts_model_id": r.get("tts_model_id"), "voice": r.get("voice"), "cooldown_events": cool,
                "condition_diff": cond, "condition_diff_flag": bool(cond), "local_rewrite_wrapper_calls": len(X.LR_EVENTS) - n_lr0,
                "started_jst": t0_iso, "elapsed_s": round(el, 2), "tts_input_chars": len(tts_input)}
            if r.get("status") != "OK":
                res["chunks"][it["chunk_id"]]["fail_reason"] = r.get("reason")
                stop_reason["v"] = f"chunk {it['chunk_id']} status={r.get('status')}"
                return
            if _AUDIT["violations"]:
                stop_reason["v"] = "audit violation"
                return

    @secondary_run_scope.with_secondary_run
    @er109_scope.family_scope("Z")
    def outer():
        return hooks.run_with_alarm_hook("Z", f"{run_dir}/b1b", body, _ret_provider=lambda: ret.ZProvider(run_dir, "b1b", specs))

    try:
        with X.redirect_production_sinks(f"{OUT}/sinks/{arm}"):
            outer()
    except PermissionError as e:
        stop_reason["v"] = f"audit hook: {e}"
    # --- 事後確認 ---
    spent1, byp1 = spent_jpy()
    after = snapshot()
    res["finished_jst"] = now_jst()
    res["stop_reason"] = stop_reason["v"]
    res["spent_after"] = round(spent1, 3)
    res["arm_cost_jpy"] = round(spent1 - spent0, 3)
    res["cost_by_provider_total"] = byp1
    res["raw_log_calls_by_provider_model"] = raw_log_by_provider()
    res["protected_changed"] = diff_snap(before, after)
    res["audit"] = audit_report()
    ident1 = module_identity()
    res["module_identity_end"] = {"uncommitted": ident1["uncommitted"], "n_modules": ident1["n_modules"],
                                  "new_modules_vs_start": sorted(set(ident1["sha256"]) - set(ident0["sha256"])),
                                  "changed_vs_start": sorted(k for k in ident0["sha256"] if ident1["sha256"].get(k) != ident0["sha256"][k])}
    res["module_identity_start"] = {"git_head": ident0["git_head"], "n_modules": ident0["n_modules"], "clean_wait": clean}
    res["local_rewrite_events"] = list(X.LR_EVENTS)
    res["mtime_scan_info_only"] = scan_info(since_ts)
    jsave(f"{OUT}/gen_result_{arm}.json", res)
    print(json.dumps({k: res[k] for k in ("arm", "stop_reason", "arm_cost_jpy", "spent_after", "protected_changed")}, ensure_ascii=False))
    print({k: (v["status"], v["attempts"], v["condition_diff"]) for k, v in res["chunks"].items()})
    print("audit violations:", res["audit"]["violations"], "module end:", res["module_identity_end"])
    if stop_reason["v"] or res["protected_changed"] or res["audit"]["violations"] or res["module_identity_end"]["uncommitted"]:
        raise SystemExit(f"[STOP] {stop_reason['v']} protected_changed={res['protected_changed']} violations={res['audit']['violations']} "
                         f"uncommitted={res['module_identity_end']['uncommitted']}")


def scan_info(since_ts: float) -> dict:
    """補助(情報のみ): repo全体で開始以降に更新されたfile。他agentの更新が混ざるため、判定は自プロセスのaudit hookで行う。"""
    hits = []
    root_n = os.path.normcase(os.path.realpath(ROOT))
    for dp, dn, fns in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in (".venv", ".git", "__pycache__", "node_modules")]
        rel_dp = os.path.relpath(dp, ROOT).replace("\\", "/")
        if rel_dp.startswith(OUT) or rel_dp.startswith(PAGE_DIR):
            continue
        for fn in fns:
            ap = os.path.join(dp, fn)
            try:
                if os.path.getmtime(ap) >= since_ts:
                    hits.append(os.path.relpath(ap, ROOT).replace("\\", "/"))
            except OSError:
                pass
    return {"n_total": len(hits), "sample_first_40": sorted(hits)[:40],
            "note": "他agent(OPEN-508/Trial-06等)の更新を含み得る。自プロセスの書込みはaudit hook記録(writes_by_event_dir)で判定"}


# ============================================================
# post: DEV assembler [N3]・計測 [N4,R4]・mp3・ページ
# ============================================================
def read_mono24(rel):
    x, sr = X._read_mono(rel)
    assert sr == SR24, (rel, sr)
    return x


def arm_clip_wavs(arm: str, cid: str) -> list:
    """arm・clipの音声ソース(chunk wav相対path列。Aは元wav 1本)。"""
    src = ARM_SOURCE[arm][cid]
    if src == "A":
        return [f"{A_NARR}/{cid}.wav"]
    if src == "A_r2":
        return [gen_wav_rel("A_r2", cid, cid)]
    chunks = load_arm_plan(src)[cid]
    return [gen_wav_rel(src, ch["chunk_id"], cid) for ch in chunks]


def dev_assemble(arm: str) -> dict:
    """A側のrun_assembly相当のDEV版。target_rmsは固定(N3-1)。対象clipのentryをarmの音声へ差替え(chunkは0.2秒でつなぐ。N3-2)。"""
    import er002_common as common
    import er003_b1_p9a_audio as p9a
    import er003_v1_n3_01_assemble as asm
    import er063_family_z_audio_01 as z
    target_rms = a_target_rms()
    clips = segment_clips()
    intro = p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH)
    outro = p9a.load_and_resample_to_target(p9a.OUTRO_MP3_PATH)
    notif = p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH)
    gain_report = {"target_rms": target_rms, "target_rms_source": FIXED_TARGET_RMS_SOURCE}

    def gs(mono, label):
        gain = p9a.compute_gain_for_target_rms(mono, target_rms)
        gained = mono * gain
        gain_report[label] = {"gain": round(float(gain), 4), "rms_after": round(p9a.rms(gained), 5), "peak_after": round(p9a.peak(gained), 5)}
        return p9a.mono_24k_to_stereo_target(gained)

    def gs_stereo(data, label):
        gain = p9a.compute_gain_for_target_rms(data, target_rms)
        gained = data * gain
        gain_report[label] = {"gain": round(float(gain), 4), "rms_after": round(p9a.rms(gained), 5), "peak_after": round(p9a.peak(gained), 5)}
        return gained

    intro_g = gs_stereo(intro["samples"], "intro")
    notif_g = gs_stereo(notif["samples"], "notification")
    outro_m = outro["samples"] * p9a.compute_gain_for_target_rms(outro["samples"], p9a.rms(intro_g))
    outro_g = outro_m * asm.OUTRO_EXTRA_GAIN_LINEAR
    kp_items = [{"rank": r} for r in (1, 2, 3)]
    seq0 = z.build_z_sequence(A_NARR, level="b1b", story_clips=clips, kp_items=kp_items, target_rms=target_rms, gs=gs,
                              gs_already_stereo=gs_stereo, intro_gained=intro_g, notification_gained=notif_g, outro_gained=outro_g,
                              kp_third="explanation", story_key=STORY_KEY)
    seq, expanded = [], {}
    for name, arr in seq0:
        if name in CLIP_IDS and not (arm == "A"):
            wavs = arm_clip_wavs(arm, name)
            if len(wavs) == 1 and ARM_SOURCE[arm][name] in ("A", "A_r2"):
                seq.append((name, gs(read_mono24(wavs[0]), name)))
                expanded[name] = [name]
            else:
                names = []
                for j, w in enumerate(wavs, start=1):
                    if j > 1:
                        seq.append((f"_silence_{EXTRA_PAUSE}", p9a.silence_stereo(EXTRA_PAUSE, p9a.TARGET_SAMPLE_RATE)))
                    nm = f"{name}_k{j}"
                    seq.append((nm, gs(read_mono24(w), nm)))
                    names.append(nm)
                gain_report.pop(name, None)
                expanded[name] = names
        else:
            seq.append((name, arr))
            if name in CLIP_IDS:
                expanded[name] = [name]
    # N3-2: 並びのassert
    order = [n for n, _ in seq]
    for cid, nms in expanded.items():
        i0 = order.index(nms[0])
        for j, nm in enumerate(nms):
            assert order[i0 + 2 * j] == nm, (cid, order[i0:i0 + 2 * len(nms)])
            if j > 0:
                assert order[i0 + 2 * j - 1] == f"_silence_{EXTRA_PAUSE}", (cid, j)
    i1 = order.index("Comment 2")
    last_p1 = expanded["full_story_part1_c1"][-1]
    assert order[order.index(last_p1) + 1:i1] == ["_silence_0.5", "_silence_1.0"], order[order.index(last_p1):i1 + 1]
    res = asm.assemble_with_timeline(seq)
    safety = asm.apply_headroom_safety_valve(res["assembled"], seq)
    return {"assembled": safety["assembled"], "timeline": res["timeline"], "headroom": safety["report"], "gain_report": gain_report,
            "sequence_order": [n for n in order if not n.startswith("_silence_")], "seq_with_silence": order, "expanded": expanded,
            "total_duration_seconds": res["total_duration_seconds"]}


def timeline_span(tl: list, first_label: str, last_label: str) -> tuple:
    e0 = next(e for e in tl if e.get("label") == first_label)
    e1 = next(e for e in tl if e.get("label") == last_label)
    return e0["start_seconds"], e1["start_seconds"] + e1["duration_seconds"]


def slice_stereo(arr, t0, t1):
    return arr[int(round(t0 * SR48)):int(round(t1 * SR48))]


def _rms(a):
    return float(np.sqrt(np.mean(np.asarray(a, dtype=np.float64) ** 2))) if len(a) else 0.0


def f0_and_centroid(x: np.ndarray, sr: int = SR24) -> dict:
    """R4(参考値・判定なし): 簡易自己相関F0中央値とスペクトル重心(有声フレームの平均)。librosa非依存。"""
    f, h = int(0.04 * sr), int(0.02 * sr)
    n = max(0, (len(x) - f) // h + 1)
    f0s, cents = [], []
    if n == 0:
        return {"f0_median_hz": None, "centroid_mean_hz": None, "n_voiced": 0}
    gmax = float(np.max(np.abs(x))) or 1.0
    lo, hi = int(sr / 400), int(sr / 70)
    win = np.hanning(f)
    freqs = np.fft.rfftfreq(f, 1 / sr)
    for i in range(n):
        fr = x[i * h:i * h + f]
        if _rms(fr) < 0.02 * gmax:
            continue
        fr0 = fr - fr.mean()
        ac = np.correlate(fr0, fr0, mode="full")[f - 1:]
        if ac[0] <= 0:
            continue
        ac = ac / ac[0]
        seg = ac[lo:hi]
        if len(seg) == 0:
            continue
        k = int(np.argmax(seg))
        if seg[k] >= 0.45:
            f0s.append(sr / (lo + k))
            mag = np.abs(np.fft.rfft(fr * win))
            if mag.sum() > 0:
                cents.append(float((freqs * mag).sum() / mag.sum()))
    return {"f0_median_hz": round(float(np.median(f0s)), 1) if f0s else None, "centroid_mean_hz": round(float(np.mean(cents)), 1) if cents else None,
            "n_voiced": len(f0s)}


def clip_paragraph_texts() -> dict:
    import er062_family_z_structure_01 as st
    txt = open(os.path.join(ROOT, A_RUN, "writer/r2.md"), encoding="utf-8").read()
    _, body = st.split_title_body(txt)
    paras = st.clean_body_paragraphs(body)
    out = {}
    for c in segment_clips():
        if c["id"] in CLIP_IDS:
            pt = [paras[i] for i in c["source_paragraph_indices"]]
            assert P.normalize_for_tts(" ".join(pt)) == P.normalize_for_tts(c["text"])
            out[c["id"]] = pt
    return out


def chunk_boundaries_in_paragraphs(arm_src: str, cid: str, ptexts: list) -> list:
    """分割chunk境界の『直前の段落index(clip内)』列(音量差の基準点を同じ位置にそろえるため)。"""
    chunks = load_arm_plan(arm_src)[cid]
    bounds = []
    for ch in chunks[:-1]:
        bounds.append(ch["last_para"])
    return bounds


def para_window_jump_db(mono: np.ndarray, al: dict, p: int, w: float = 1.0) -> float | None:
    """整列結果から、段落pの末尾w秒と段落p+1の先頭w秒のRMS差(dB)。A/Bとも同じ方法(N4基準点)。"""
    a, b = al["paragraphs"][p], al["paragraphs"][p + 1]
    if a["end"] is None or b["start"] is None:
        return None
    ra = _rms(mono[int(max(0, a["end"] - w) * SR24):int(a["end"] * SR24)])
    rb = _rms(mono[int(b["start"] * SR24):int((b["start"] + w) * SR24)])
    return round(float(20 * np.log10(max(rb, 1e-10) / max(ra, 1e-10))), 2)


def join_gained(arm: str, cid: str, target_rms: float):
    import er003_b1_p9a_audio as p9a
    wavs = arm_clip_wavs(arm, cid)
    monos = [read_mono24(w) for w in wavs]
    gained, gains = [], []
    for m in monos:
        g = p9a.compute_gain_for_target_rms(m, target_rms)
        gained.append(m * g)
        gains.append(round(float(g), 4))
    seq = []
    for i, c in enumerate(gained):
        if i > 0:
            seq.append(np.zeros(int(round(EXTRA_PAUSE * SR24)), dtype=c.dtype))
        seq.append(c)
    return {"joined": np.concatenate(seq), "chunks_gained": gained, "chunks_raw": monos, "gains": gains, "wavs": wavs}


def cmd_post(args) -> None:
    assert_cwd_is_root()
    from faster_whisper import WhisperModel
    import er003_b1_p9a_audio as p9a
    hf = os.path.join(os.path.expanduser("~"), ".cache", "huggingface")
    install_audit([OUT, PAGE_DIR], [hf])
    before = snapshot()
    since_ts = time.time()
    target_rms = a_target_rms()
    clips = {c["id"]: c for c in segment_clips()}
    ptexts = clip_paragraph_texts()
    arms = [a for a in ("A", "A_r2", "B_r1", "B_fine", "B_alt") if a == "A" or os.path.exists(os.path.join(ROOT, f"{OUT}/gen_result_{ARM_SOURCE[a][CLIP_IDS[1]]}.json"))]
    # ---- DEV assembly + A再現性(N3) ----
    asm_res = {}
    for arm in arms:
        asm_res[arm] = dev_assemble(arm)
    orig_tl = jload(f"{A_LEVEL}/assembly/timeline.json")
    a_re = asm_res["A"]
    n3 = {"target_rms_fixed": target_rms,
          "target_rms_recomputed_from_A_(preview+part1_c1)/2": None,
          "A_reassembly_duration_s": round(a_re["total_duration_seconds"], 3), "A_original_duration_s": orig_tl["duration_seconds"],
          "A_reassembly_sequence_order_equals_original": a_re["sequence_order"] == orig_tl["sequence_order"], "arms": {}}
    prev_rms = p9a.rms(read_mono24(f"{A_NARR}/preview.wav"))
    p1_rms = p9a.rms(read_mono24(f"{A_NARR}/{CLIP_IDS[0]}.wav"))
    n3["target_rms_recomputed_from_A_(preview+part1_c1)/2"] = round((prev_rms + p1_rms) / 2, 6)
    ares = a_results()["segments"]
    for arm in arms:
        r = asm_res[arm]
        n3["arms"][arm] = {
            "duration_s": round(r["total_duration_seconds"], 3), "target_rms_in_gain_report": r["gain_report"]["target_rms"],
            "sequence_order": r["sequence_order"],
            "comment2_follows_last_chunk": True, "headroom": r["headroom"],
            "clip_sources": ARM_SOURCE[arm],
            "audio_sha256": {cid: [sha(w) for w in arm_clip_wavs(arm, cid)] for cid in CLIP_IDS},
            "audio_sha_differs_from_A": {cid: [sha(w) != ares[cid]["sha256"] for w in arm_clip_wavs(arm, cid)] for cid in CLIP_IDS} if arm != "A" else None}
    # N3-3: A_r2のsha != A
    if "A_r2" in arms:
        n3["A_r2_is_new_take"] = all(all(v) for v in n3["arms"]["A_r2"]["audio_sha_differs_from_A"].values())
    # ---- 部分音声(mp3用)・全体 ----
    parts_audio, full_audio = {}, {}
    for arm in arms:
        parts_audio[arm] = _slice_parts(asm_res[arm])
        full_audio[arm] = asm_res[arm]["assembled"]
    jsave(f"{OUT}/postprocess/dev_assembly_check_01.json", {k: v for k, v in n3.items()})
    # ---- 計測(clip単位: 3 clip x arm) ----
    model = WhisperModel("small", device="cpu", compute_type="int8")
    mw = X._mw()
    meas = {"arms": {}}
    jc = {}
    for arm in arms:
        meas["arms"][arm] = {"clips": {}, "chunk_gains": {}}
        jc[arm] = {}
        for cid in CLIP_IDS:
            j = join_gained(arm, cid, target_rms)
            jc[arm][cid] = j
            words = clips[cid]["word_count"]
            m = X.measure_wav(j["joined"], SR24, words)
            wp = f"{OUT}/postprocess/align/{arm}_{cid}.wav"
            X._write_wav24(wp, j["joined"])
            al = X.measure_alignment(model, os.path.join(ROOT, wp), "\n\n".join(ptexts[cid]))
            meas["arms"][arm]["clips"][cid] = {"measure": {k: v for k, v in m.items() if k != "pauses_300_detail"}, "alignment": al,
                                              "n_chunks": len(j["wavs"]), "gains": j["gains"]}
    # 集計(clip単位をpart "1","2","3"とみなしてXのm4_decomposeを再利用)
    def _al(arm):
        return {str(PART_OF[c]): meas["arms"][arm]["clips"][c]["alignment"] for c in CLIP_IDS}
    summary = {}
    for arm in arms:
        pm = {c: meas["arms"][arm]["clips"][c]["measure"] for c in CLIP_IDS}
        agg = X._agg_wpm(pm)
        spans = [q["span"] for c in CLIP_IDS for q in meas["arms"][arm]["clips"][c]["alignment"]["paragraphs"]]
        words = sum(clips[c]["word_count"] for c in CLIP_IDS)
        agg["articulation_wpm_paragraph_span"] = round(words / sum(spans) * 60, 2)
        agg["n_paragraph_spans"] = len(spans)
        agg["asr_over_ref"] = {c: round(meas["arms"][arm]["clips"][c]["alignment"]["asr_words"] / meas["arms"][arm]["clips"][c]["alignment"]["ref_words"], 4) for c in CLIP_IDS}
        agg["match_ratio"] = {c: meas["arms"][arm]["clips"][c]["alignment"]["match_ratio"] for c in CLIP_IDS}
        agg["all_paragraphs_aligned"] = {c: meas["arms"][arm]["clips"][c]["alignment"]["all_paragraphs_aligned"] for c in CLIP_IDS}
        summary[arm] = agg
    decomp = {}
    for x_, y_ in [("A", "A_r2"), ("A", "B_r1"), ("A_r2", "B_r1"), ("A", "B_fine"), ("A_r2", "B_fine"), ("A", "B_alt"), ("A_r2", "B_alt")]:
        if x_ in arms and y_ in arms:
            d = X.m4_decompose(_al(x_), _al(y_))
            decomp[f"{x_}->{y_}"] = d
    # ---- N4: 境界音量差(Aの同じ段落境界位置との比較) ----
    boundary = {}
    for arm in arms:
        if arm in ("A", "A_r2"):
            continue
        boundary[arm] = {}
        for cid in CLIP_IDS:
            src = ARM_SOURCE[arm][cid]
            bps = chunk_boundaries_in_paragraphs(src, cid, ptexts[cid])
            al_b = meas["arms"][arm]["clips"][cid]["alignment"]
            al_a = meas["arms"]["A"]["clips"][cid]["alignment"]
            al_a2 = meas["arms"]["A_r2"]["clips"][cid]["alignment"] if "A_r2" in arms else None
            rows = []
            speech_bounds = X.boundary_jump_db(jc[arm][cid]["chunks_gained"])
            for bi, p in enumerate(bps):
                jb = para_window_jump_db(jc[arm][cid]["joined"], al_b, p)
                ja = para_window_jump_db(jc["A"][cid]["joined"], al_a, p)
                ja2 = para_window_jump_db(jc["A_r2"][cid]["joined"], al_a2, p) if al_a2 else None
                rows.append({"after_clip_paragraph": p, "B_jump_db": jb, "A_ref_jump_db": ja, "A_r2_ref_jump_db": ja2,
                             "B_minus_A_db": (round(jb - ja, 2) if jb is not None and ja is not None else None),
                             "A_r2_minus_A_db": (round(ja2 - ja, 2) if ja2 is not None and ja is not None else None),
                             "B_jump_db_speech_bounds_method(参考)": speech_bounds[bi] if bi < len(speech_bounds) else None})
            boundary[arm][cid] = rows
    # part境界(参考): A内のclip間(part1_c1末→part2_c1先頭など)は参考併記
    # ---- R4: 声質参考値(chunkごとの中央値F0・スペクトル重心を、Aの同じ区間と並べる。判定なし) ----
    voice_ref = {}
    for arm in arms:
        if arm in ("A", "A_r2"):
            continue
        voice_ref[arm] = {}
        for cid in CLIP_IDS:
            src = ARM_SOURCE[arm][cid]
            chunks = load_arm_plan(src)[cid]
            rows = []
            al_a = meas["arms"]["A"]["clips"][cid]["alignment"]
            for ch, cg in zip(chunks, jc[arm][cid]["chunks_gained"]):
                pa = al_a["paragraphs"][ch["first_para"]]
                pb = al_a["paragraphs"][ch["last_para"]]
                seg_a = jc["A"][cid]["joined"][int(pa["start"] * SR24):int(pb["end"] * SR24)]
                rows.append({"chunk_id": ch["chunk_id"], "B": f0_and_centroid(cg), "A_same_span": f0_and_centroid(seg_a)})
            voice_ref[arm][cid] = rows
    # ---- 判定(事前基準。合否ではなく到達/未達/判定不能) ----
    judge = judge_all(arms, summary, decomp, boundary, meas)
    # ---- 音声公開(mp3)・ページ ----
    audio_info = write_mp3s(arms, parts_audio, full_audio)
    out = {"ts": now_jst(), "arms": arms, "n3_assembly_check": n3, "summary": summary, "m4_decomposition": decomp, "boundary_N4": boundary,
           "voice_reference_R4": voice_ref, "judge": judge, "audio": audio_info, "per_arm_clip": {a: {c: {"measure": meas["arms"][a]["clips"][c]["measure"], "gains": meas["arms"][a]["clips"][c]["gains"], "n_chunks": meas["arms"][a]["clips"][c]["n_chunks"]} for c in CLIP_IDS} for a in arms},
           "alignments": {a: {c: meas["arms"][a]["clips"][c]["alignment"] for c in CLIP_IDS} for a in arms}}
    out["protected_changed"] = diff_snap(before, snapshot())
    out["audit"] = audit_report()
    out["mtime_scan_info_only"] = scan_info(since_ts)
    jsave(f"{OUT}/measure_01.json", out)
    build_page(out, asm_res)
    print(json.dumps({"summary": summary, "judge": judge, "protected_changed": out["protected_changed"], "audit_violations": out["audit"]["violations"]}, ensure_ascii=False, indent=1)[:5000])


PART_OF_INV = {1: "full_story_part1_c1", 2: "full_story_part2_c3", 3: "full_story_part3_c1"}


def _slice_parts(a: dict) -> dict:
    """timelineのpiece順(sequence_order+silence)から、part1(part1_c1)/part2(c1〜c3)/part3(c1)の音声区間を切り出す。"""
    tl = a["timeline"]
    # timelineはsilence pieceも含むかを確認して名前でなく位置で対応づける
    seq_names = a["seq_with_silence"]
    assert len(tl) == len(seq_names), (len(tl), len(seq_names))
    idx = {n: i for i, n in enumerate(seq_names)}
    arr = a["assembled"]

    def span(first, last):
        e0, e1 = tl[idx[first]], tl[idx[last]]
        return slice_stereo(arr, e0["start_seconds"], e1["start_seconds"] + e1["duration_seconds"])
    ex = a["expanded"]
    return {1: span(ex["full_story_part1_c1"][0], ex["full_story_part1_c1"][-1]),
            2: span("full_story_part2_c1", ex["full_story_part2_c3"][-1]),
            3: span(ex["full_story_part3_c1"][0], ex["full_story_part3_c1"][-1])}


def write_mp3s(arms, parts_audio, full_audio) -> dict:
    info = {}
    for arm in arms:
        info[arm] = {}
        for n in (1, 2, 3):
            rel = f"{PAGE_DIR}/audio/{arm}_part{n}.mp3"
            X._write_mp3(parts_audio[arm][n], rel, br="96k")
            info[arm][f"part{n}"] = {"path": rel, "seconds": round(len(parts_audio[arm][n]) / SR48, 2), "bytes": os.path.getsize(os.path.join(ROOT, rel))}
        rel = f"{PAGE_DIR}/audio/{arm}_full.mp3"
        X._write_mp3(full_audio[arm], rel, br="96k")
        info[arm]["full"] = {"path": rel, "seconds": round(len(full_audio[arm]) / SR48, 2), "bytes": os.path.getsize(os.path.join(ROOT, rel))}
    return info


# ============================================================
# 事前固定の判定基準(DESIGN_01 §5改訂版と一致させる。合否ではなく『到達/未達/判定不能』)
# ============================================================
SPEED_ART300_RATIO_MAX = 0.97      # B/A <= 0.97 (3%以上遅い)
BOUNDARY_TOL_DB = 3.0              # |B境界差 - Aの同位置差| <= 3.0 dB
ASR_RATIO_RANGE = (0.97, 1.03)
MATCH_RATIO_MARGIN = 0.02


def judge_all(arms, summary, decomp, boundary, meas) -> dict:
    out = {"criteria": {"speed": f"art300(B)/art300(A) <= {SPEED_ART300_RATIO_MAX} かつ 段落span(16)の平均比B/Aの方向が一致し |D_B| > |D_noise|(A_r2 vs A)",
                        "boundary": f"全chunk境界で |B境界差 - Aの同じ段落境界位置の差| <= {BOUNDARY_TOL_DB} dB",
                        "integrity": f"ASR語数/台本語数が{ASR_RATIO_RANGE}内かつ全段落整列かつmatch_ratio >= A-{MATCH_RATIO_MARGIN}",
                        "gate": "全chunkのstatus=OK・condition_diff空"}}
    noise = None
    if "A_r2" in arms and "A->A_r2" in decomp:
        noise = decomp["A->A_r2"]["mean_span_ratio_b_over_a"] - 1.0
    out["take_noise_D_A_r2_vs_A"] = noise
    for arm in [a for a in arms if a.startswith("B")]:
        s_a, s_b = summary["A"], summary[arm]
        r300 = s_b["articulation_wpm_300"] / s_a["articulation_wpm_300"]
        d = decomp.get(f"A->{arm}")
        d_b = (d["mean_span_ratio_b_over_a"] - 1.0) if d else None
        slower_art = r300 <= SPEED_ART300_RATIO_MAX
        para_dir_slower = (d_b is not None and d_b > 0)
        beyond_noise = (noise is not None and d_b is not None and abs(d_b) > abs(noise))
        if slower_art and para_dir_slower and beyond_noise:
            speed = "基準到達(減速効果あり)"
        elif (r300 > 1.0 and d_b is not None and d_b < 0) or (r300 > SPEED_ART300_RATIO_MAX and not para_dir_slower and not slower_art and d_b is not None and d_b <= 0):
            speed = "未達(減速なし/加速)"
        else:
            speed = "判定不能(閾値到達と段落spanが一致しない、または基準ノイズ以内)"
        # 境界
        bad, rows = [], []
        for cid, rs in (boundary.get(arm) or {}).items():
            for r in rs:
                v = r["B_minus_A_db"]
                rows.append(v)
                if v is None or abs(v) > BOUNDARY_TOL_DB:
                    bad.append((cid, r["after_clip_paragraph"], v))
        bnd = "基準到達" if rows and not bad else ("未達" if bad else "判定不能")
        # 整合
        integ_ok = True
        detail = {}
        for cid in CLIP_IDS:
            ab = meas["arms"][arm]["clips"][cid]["alignment"]
            aa = meas["arms"]["A"]["clips"][cid]["alignment"]
            ok = (ASR_RATIO_RANGE[0] <= ab["asr_words"] / ab["ref_words"] <= ASR_RATIO_RANGE[1] and ab["all_paragraphs_aligned"]
                  and ab["match_ratio"] >= aa["match_ratio"] - MATCH_RATIO_MARGIN)
            detail[cid] = ok
            integ_ok &= ok
        gen_ok = True
        for src in {ARM_SOURCE[arm][c] for c in CLIP_IDS}:
            gr = jload(f"{OUT}/gen_result_{src}.json")
            for ck, v in gr["chunks"].items():
                if arm == "B_alt" and src == "B_r1" and not ck.startswith("full_story_part1_c1"):
                    continue
                gen_ok &= (v["status"] == "OK" and not v["condition_diff_flag"])
        out[arm] = {"art300_ratio_B_over_A": round(r300, 4), "para_span_mean_D_B": d_b, "speed": speed,
                    "boundary": bnd, "boundary_out_of_tolerance": bad, "boundary_B_minus_A_db_all": rows,
                    "integrity": "基準到達" if integ_ok else "未達", "integrity_detail": detail, "gate_all_ok_no_cond_diff": gen_ok}
    return out


# ============================================================
# 試聴ページ
# ============================================================
def build_page(m: dict, asm_res: dict) -> None:
    import html as _h
    s = m["summary"]
    arms = m["arms"]
    LABEL = {"A": "A 現行(長い地の文を1回の読み上げ)", "A_r2": "A_r2 現行方式の別take", "B_r1": "B_r1 主規則(約70語ごとに分割+0.2秒)",
             "B_fine": "B_fine 細分割(約47語ごとに分割+0.2秒)", "B_alt": "B_alt 代替切断(クライマックス直前を避けた切り直し+0.2秒)"}

    def aud(rel):
        return f"<audio controls preload='none' src='audio/{os.path.basename(rel)}'></audio>"

    def row(arm):
        return (f"<tr><td><b>{LABEL[arm]}</b></td>" + "".join(f"<td class='play'>{aud(m['audio'][arm][f'part{n}']['path'])}</td>" for n in (1, 2, 3)) +
                f"<td class='play'>{aud(m['audio'][arm]['full']['path'])}</td></tr>")
    main_arms = [a for a in ("A", "B_r1", "B_fine", "B_alt") if a in arms]
    rows = "".join(row(a) for a in main_arms)
    ref_rows = row("A_r2") if "A_r2" in arms else ""

    def spd(arm):
        x = s[arm]
        return f"<tr><td>{LABEL[arm]}</td><td>{x['duration_s']}</td><td>{x['total_wpm']}</td><td>{x['articulation_wpm_300']}</td><td>{x['articulation_wpm_paragraph_span']}</td></tr>"
    table = ("<table style='width:auto'><thead><tr><th>方式</th><th>3区間の合計の長さ(秒)</th><th>全体WPM</th><th>実発話WPM(無音除く)</th><th>実発話WPM(段落ごとの発話区間)</th></tr></thead><tbody>"
             + "".join(spd(a) for a in arms if a in s) + "</tbody></table>")
    css = ("body{font-family:sans-serif;max-width:1100px;margin:1em auto;padding:0 1em;line-height:1.5}table{border-collapse:collapse;width:100%;margin:.5em 0 1.5em}"
           "th,td{border:1px solid #bbb;padding:.4em .6em;vertical-align:top;text-align:left}th{background:#f0f0f0}.note{background:#fff8e1;border:1px solid #e0c060;padding:.7em 1em;margin:1em 0}"
           ".sec{color:#555;font-size:.9em}.play audio{width:230px}")
    html_doc = ("<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><title>Family Z 長い地の文Chunk分割 比較試聴(Trial)</title>"
                f"<meta name='viewport' content='width=device-width, initial-scale=1'><style>{css}</style></head><body>"
                "<h1>Family Z『告げ口心臓』Advanced 長い地の文のChunk分割 比較試聴(Trial)</h1>"
                "<div class='note'><b>状態: Trial(Production採用ではありません)</b>。長く続く語り(地の文)だけを、段落の切れ目で複数回に分けて読み上げ、"
                "その間に0.2秒を足した版を、現行(1回で通して読む版)と聴き比べるページです。セリフ・話者の切替・声・スタイル・設定は全て同一です。<br>"
                "<b>このページは『告げ口心臓』の案A本文の正式再生成版(別途試聴ページ)とは別物です。本文はTrial版で、正式再生成版とは異なります。"
                "本ページは読み上げ方式の比較のみで、本文の良し悪しはここでは判断しません。</b><br>"
                "対象はTrial用に作った一人称版のAdvanced本文の長い3区間(本文1・2の後半・3。141語/118語/148語)です。"
                "<a href='../fx_paragraph_chunk_trial_01/index.html'>Family X(英国の電車マナー)の同種の比較試聴ページはこちら</a>。</div>"
                "<div class='note'><b>聴いていただきたい点</b>: 語りの流れ・緊張感・没入感 / 声や抑揚が途中で変わって聞こえないか / 速さ / 音量の差。<br>"
                "<b>最悪ケースの負荷テストについて</b>: B_r1の本文2(「Surely a neighbour would hear!」→「I rushed in.」)と本文3(「…quick beating.」→「I talked louder.」)の切れ目は、"
                "心臓の音が高まって行動・錯乱に移る<u>まさにクライマックスの直前</u>です。ここで抑揚の勢いが途切れて聞こえるかを確認するための、意図的に厳しい条件です。"
                "この2か所で違和感があっても、方式全体の不合格とは決めず、切る位置を変えた版(B_alt: 本文2は「Wide open.」の後、本文3は「You see how little I feared?」の後)で比べられます。"
                "B_altの本文1はB_r1と同じ音声です(本文1の切断位置は変えていません)。B_fineは約47語ごとに、さらに細かく分けた版です。</div>"
                f"<table><thead><tr><th>方式</th><th>本文1</th><th>本文2</th><th>本文3</th><th>Advanced通し(Intro〜Outro)</th></tr></thead><tbody>{rows}</tbody></table>"
                f"<h2>速さの目安(3区間の合計)</h2>{table}"
                "<p class='sec'>実発話WPM=1分あたりの語数(間を除く)。A_r2などの別takeとの差(読み上げのたびの偶然の差)は折りたたみの参考欄と比べてください。</p>"
                f"<details><summary><b>参考: 現行方式の別take(A_r2)</b></summary><table><thead><tr><th>方式</th><th>本文1</th><th>本文2</th><th>本文3</th><th>Advanced通し</th></tr></thead><tbody>{ref_rows}</tbody></table></details>"
                "</body></html>")
    with open(os.path.join(ROOT, PAGE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_doc)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("pre")
    g = sub.add_parser("gen")
    g.add_argument("--arm", required=True)
    sub.add_parser("post")
    a = ap.parse_args()
    {"pre": cmd_pre, "gen": cmd_gen, "post": cmd_post}[a.cmd](a)


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""FAMILY-C-JA-TTS-PRODUCTION-FIX-01 委任_02: 証跡harness(0円検査 + Run C' + 有料Run A/B)。

部分コマンド:
  symbol_gate_check  : 0円。JA 5文面(Comment1-3・japanese_title・preview)にLayer-4記号Gateを事前実施(R6)
  reuse_plan_dryrun  : 0円。全article_config.jsonのreuse_from先についてclipごとの由来判定を一覧化(R4)
  run_c_prime        : 0円。Memory A2をreuse_fromに空の出力dirで実行し、TTS/ASR関数を「呼ばれたら例外」に差し替えて
                       偽陰性(再利用されるべきclipが再生成になる)を検出(--tts-raise)
  run_a / run_b      : 有料(--execute指定時のみ)。Production正式entry(runner.main)を呼ぶ。費用meter・hard_stop・STOP監視は
                       er078_auw_runtime_evidence_06b/06のMeterを再利用(証跡先・ledger・上限だけ本委任に差替)。
監督ループ・自動再試行なし。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys

import er078_auw_runtime_evidence_06b as b
import er078_auw_runtime_evidence_06 as e6

ROOT = e6.ROOT
EV = "er079_output/family_c_ja_tts_production_fix_01/evidence_02"
MANAGED_ID = "FAMILY-C-JA-TTS-PRODUCTION-FIX-01"
b.EV = EV
b.LEDGER = f"{EV}/cost/spend_ledger.jsonl"
b.CAP_JPY = 11.0
if MANAGED_ID not in e6.MANAGED_IDS:
    e6.MANAGED_IDS.append(MANAGED_ID)

# ユーザー試聴承認済みepisodeの出力dirと承認根拠(照合したfile:line)。
APPROVED_EPISODE_DIRS = {
    "er013_output/family_c_episode_trial_11/memory_a2": "CURRENT_SPEC.md:1049-1050(Trial-11/12 試聴OK→Family C Production化), :1129-1130(Trial-11承認済みepisode wav[316.569秒])",
    "er013_output/family_c_episode_trial_12/digital_twins_a2": "CURRENT_SPEC.md:1049-1050(Digital Twins A2 試聴OK)",
    "er013_output/family_c_episode_trial_12/digital_twins_b1": "CURRENT_SPEC.md:1049-1050(Digital Twins B1 試聴OK)",
    "er013_output/family_c_episode_trial_11/memory_b1": "CURRENT_SPEC.md:1049-1050(Memory B1 試聴OK)",
}
C_SRC = "er058_output/unified_all_roles_production_wiring_01/evidence_06b/crun/c_out"
MEMORY_CFG = "er013_output/family_c_production/memory/article_config.json"


def _runner():
    import er013_family_c_production_runner_01 as R
    return R


def _write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)


def _comment_texts(md_path, comments_cfg):
    t = open(md_path, encoding="utf-8").read()
    out = {}
    for num_str in comments_cfg:
        n = int(num_str)
        after = t.split(f"## Comment {n}\n\n", 1)[1]
        out[n] = after.split("\n\n", 1)[0].strip()
    return out


def clip_inventory(level_cfg, reuse_from):
    """reuse_from先を使う場合に、runnerが採用判定にかける(clip名, 現行text)の一覧(runner本体と同じ導出)。"""
    R = _runner()
    segs, _ = R.build_segments_for_level(level_cfg)
    clips = [(f"{s['id']}.wav", s["tts_text"]) for s in segs]
    md = f"{reuse_from}/comments_ja.md"
    if level_cfg.get("comments") and os.path.exists(md):
        for n, t in sorted(_comment_texts(md, level_cfg["comments"]).items()):
            clips.append((f"comment_{n}_ja.wav", t))
    if level_cfg.get("topic_title"):
        clips.append(("topic_intro_en.wav", f"Today's topic is {level_cfg['topic_title']}."))
    if level_cfg.get("japanese_title_text"):
        clips.append(("japanese_title.wav", level_cfg["japanese_title_text"]))
    pv = f"{reuse_from}/preview.txt"
    if os.path.exists(pv):
        clips.append(("preview_ja.wav", open(pv, encoding="utf-8").read().strip()))
    return clips


# ---------------------------------------------------------------- 0円: 記号Gate事前検査(R6)
def cmd_symbol_gate_check(out):
    import er003_audio_tts_asr_safety as safety
    R = _runner()
    cfg = json.load(open(f"{C_SRC}/article_config.json", encoding="utf-8"))
    lv = cfg["levels"]["a2"]
    texts = _comment_texts(f"{C_SRC}/a2/comments_ja.md", lv["comments"])
    rows = [(f"comment_{n}_ja", t) for n, t in sorted(texts.items())]
    rows.append(("japanese_title", lv["japanese_title_text"]))
    rows.append(("preview_ja", open(f"{C_SRC}/a2/preview.txt", encoding="utf-8").read().strip()))
    res = []
    for label, t in rows:
        f = safety.detect_prohibited_symbols(t, language="ja")
        res.append({"label": label, "text": t, "findings": f, "requires_stop": bool(safety.symbol_gate_requires_stop(f))})
    n_stop = sum(1 for r in res if r["requires_stop"])
    n_any = sum(len(r["findings"]) for r in res)
    out_obj = {"source": f"{C_SRC}/(article_config.json japanese_title_text, a2/comments_ja.md, a2/preview.txt)",
               "gate": "er003_audio_tts_asr_safety.detect_prohibited_symbols(text, 'ja') + symbol_gate_requires_stop",
               "n_texts": len(res), "n_requires_stop": n_stop, "n_findings_total": n_any, "rows": res,
               "conditional_stop_a": n_stop > 0, "cost_jpy": 0}
    _write(out, out_obj)
    print(json.dumps({k: out_obj[k] for k in ("n_texts", "n_requires_stop", "n_findings_total", "conditional_stop_a")}, ensure_ascii=False))


# ---------------------------------------------------------------- 0円: reuse plan dry-run(R4)
def _classify_dir(reuse_from, level_cfg):
    R = _runner()
    rows = []
    for name, text in clip_inventory(level_cfg, reuse_from):
        sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
        chk = R.reuse_provenance_check(reuse_from, name, sha)
        # 旧ルール(変更前)の判定: src wavが存在すれば無条件に再利用(textは検査しない)
        old_rule = "reuse" if chk["src_exists"] else "regenerate"
        rows.append({"clip": name, "text_head": text[:24], "src_exists": chk["src_exists"],
                     "src_meta_kind": chk["src_meta_kind"], "audit_reused": chk["audit_reused"],
                     "new_rule": "reuse" if chk["ok"] else "regenerate", "basis": chk["basis"], "reason": chk["reason"],
                     "old_rule": old_rule})
    return rows


def cmd_reuse_plan_dryrun(out):
    R = _runner()
    cfg_paths = []
    for root, _dirs, files in os.walk(ROOT):
        if any(p in root for p in (".venv", "node_modules", ".git" + os.sep)):
            continue
        if "article_config.json" in files:
            cfg_paths.append(os.path.relpath(os.path.join(root, "article_config.json"), ROOT).replace("\\", "/"))
    plans, seen = [], set()
    for cp in sorted(cfg_paths):
        try:
            cfg = json.load(open(cp, encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        for lv, lcfg in (cfg.get("levels") or {}).items():
            rf = lcfg.get("reuse_from")
            if not rf:
                continue
            rf_n = rf.replace("\\", "/")
            plans.append({"config": cp, "level": lv, "reuse_from": rf_n,
                          "user_approved_episode": APPROVED_EPISODE_DIRS.get(rf_n),
                          "rows": _classify_dir(rf_n, lcfg)})
            seen.add(rf_n)
    # 追加: Run A / Run B / Run C'で使う候補reuse_from(C_SRC a2、Memory本番a2)も同じconfig(Memory a2)の文面で判定
    mem = json.load(open(MEMORY_CFG, encoding="utf-8"))["levels"]["a2"]
    extra = []
    for rf in (C_SRC + "/a2", "er013_output/family_c_production/memory/a2"):
        extra.append({"config": MEMORY_CFG + " (level a2の文面で判定)", "level": "a2", "reuse_from": rf,
                      "user_approved_episode": None, "rows": _classify_dir(rf, mem)})
    # 汚染資産(バグ期出力dir)一覧: 06d cja系dir、06b crun系dirの JA comment/title/preview wav の由来状態
    polluted = []
    base = "er058_output/unified_all_roles_production_wiring_01"
    for dp in sorted(os.listdir(f"{base}/evidence_06d")) + []:
        if not dp.startswith("cja"):
            continue
        for sub in ("c_out/a2", "reuse_src"):
            ad = f"{base}/evidence_06d/{dp}/{sub}/audio"
            if os.path.isdir(ad):
                for fn in sorted(os.listdir(ad)):
                    if fn.endswith(".wav") and (fn.startswith("comment_") or fn.startswith("japanese_title") or fn.startswith("preview_ja")):
                        mp = f"{ad}/{fn}.ok.meta.json"
                        kind = "none"
                        if os.path.exists(mp):
                            kind = "legacy_upgraded" if json.load(open(mp, encoding="utf-8")).get("upgraded_from_legacy_ok") else "regular"
                        polluted.append({"dir": f"{base}/evidence_06d/{dp}/{sub}", "wav": fn, "meta_kind": kind})
    summary = []
    for p in plans + extra:
        rg = [r["clip"] for r in p["rows"] if r["new_rule"] == "regenerate"]
        fn = [r["clip"] for r in p["rows"] if r["new_rule"] == "regenerate" and r["old_rule"] == "reuse"]
        summary.append({"reuse_from": p["reuse_from"], "config": p["config"], "n_clips": len(p["rows"]),
                        "n_reuse_new_rule": len(p["rows"]) - len(rg), "n_regenerate_new_rule": len(rg),
                        "regenerate_clips": rg, "user_approved_episode": p["user_approved_episode"],
                        "approved_episode_would_be_regenerated": bool(p["user_approved_episode"]) and bool(rg)})
    res = {"purpose": "R4 reuse plan dry-run(0円)。旧ルール=src wav存在のみで再利用 / 新ルール=reuse_provenance_check",
           "summary": summary, "plans": plans + extra, "polluted_assets_06d_cja": polluted,
           "n_polluted_ja_assets": len(polluted),
           "conditional_stop_b": any(s["approved_episode_would_be_regenerated"] for s in summary), "cost_jpy": 0}
    _write(out, res)
    print(json.dumps({"summary": summary, "conditional_stop_b": res["conditional_stop_b"],
                      "n_polluted_ja_assets": len(polluted)}, ensure_ascii=False, indent=1))


# ---------------------------------------------------------------- 0円: Run C'
def cmd_run_c_prime(reuse_from, out):
    """Memory A2をreuse_fromに空の出力dirで実行。(1)clipごとにadopt_from_reuse_source(Production採用関数)を実呼出し、
    (2)run_full_generationをTTS/ASR関数『呼ばれたら例外』で実行して最初の再生成要求を検出する。API 0。"""
    R = _runner()
    os.makedirs(out, exist_ok=True)
    cfg = json.load(open(MEMORY_CFG, encoding="utf-8"))
    lv = cfg["levels"]["a2"]
    lv["reuse_from"] = reuse_from
    # Phase 1
    adopt_dir = f"{out}/phase1_adopt/audio"
    os.makedirs(adopt_dir, exist_ok=True)
    rows = []
    for name, text in clip_inventory(lv, reuse_from):
        sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
        r = R.adopt_from_reuse_source(reuse_from, name, f"{adopt_dir}/{name}", sha, text)
        chk = R.reuse_provenance_check(reuse_from, name, sha)
        rows.append({"clip": name, "adopted": r is not None, "basis": chk["basis"], "reason": chk["reason"],
                     "false_negative": r is None and chk["src_exists"]})
    n_fn = sum(1 for r in rows if r["false_negative"])
    # Phase 2
    p2 = f"{out}/phase2_run"
    shutil.rmtree(p2, ignore_errors=True)
    os.makedirs(p2, exist_ok=True)
    cfg_path = f"{p2}/article_config.json"
    json.dump(cfg, open(cfg_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    calls = []

    def boom(kind):
        def f(*a, **k):
            label = (a[2] if len(a) > 2 else k.get("out_path", "?"))
            calls.append({"kind": kind, "target": str(label)})
            raise RuntimeError(f"[TTS_RAISE] {kind} called for {label}")
        return f
    R.repro01.generate_narration_snippet_verified_strict = boom("verified_strict")
    R.voice01.generate_charon_english = boom("charon_english")
    R.bvoices.generate_voice_body_wide_margin = boom("voice_body_wide_margin")
    import er006_asr_provider_routing_01 as routing
    routing.transcribe = boom("asr_transcribe")
    sys.argv = ["er013_family_c_production_runner_01.py", "--config", cfg_path, "--level", "a2", "--budget-jpy", "25"]
    outcome = "completed"
    try:
        R.main()
    except Exception as e_:  # noqa: BLE001
        outcome = f"{type(e_).__name__}: {str(e_)[:300]}"
    res = {"reuse_from": reuse_from, "phase1_rows": rows, "phase1_n_clips": len(rows),
           "phase1_n_adopted": sum(1 for r in rows if r["adopted"]), "phase1_false_negatives": n_fn,
           "phase2_outcome": outcome, "phase2_api_function_calls": calls, "cost_jpy": 0,
           "note": "false_negative=src wavが存在するのに由来照合を通らず再生成扱いになったclip"}
    _write(f"{out}/run_c_prime.json", res)
    print(json.dumps({k: res[k] for k in ("phase1_n_clips", "phase1_n_adopted", "phase1_false_negatives", "phase2_outcome")}, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["symbol_gate_check", "reuse_plan_dryrun", "run_c_prime", "run_a", "run_b"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--reuse-from")
    ap.add_argument("--tts-raise", action="store_true")
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--budget-jpy", type=float, default=11.0)
    a = ap.parse_args()
    if a.cmd == "symbol_gate_check":
        cmd_symbol_gate_check(a.out)
    elif a.cmd == "reuse_plan_dryrun":
        cmd_reuse_plan_dryrun(a.out)
    elif a.cmd == "run_c_prime":
        if not a.tts_raise:
            raise SystemExit("run_c_primeは--tts-raise必須(API 0)")
        cmd_run_c_prime(a.reuse_from, a.out)
    else:
        raise SystemExit("run_a/run_bは本版では未実装(条件付きSTOP判定後に追加)")


if __name__ == "__main__":
    main()

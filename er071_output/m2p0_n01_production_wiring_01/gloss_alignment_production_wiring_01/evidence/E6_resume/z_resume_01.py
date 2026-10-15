# -*- coding: utf-8 -*-
"""KGCPW E6 (Z): HR解決後の再開。E5_fail2/z_<lv>のmock context(run_mock)に対しresolve_gloss -> 正式stage_kp再実行。
provenance: synthetic(失敗注入で作ったHR状態)+production_formal_path(Production stage関数)。API 0、TTS 0(mock)。"""
import contextlib, io, json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 5))
sys.path.insert(0, ROOT); os.chdir(ROOT)
import er003_key_words_gloss_alignment as ga
import er026_family_z_fiction_production_runner_01 as r
lv = sys.argv[1]; base = sys.argv[2]; gloss = sys.argv[3]
ctx = r.build_mock_context(base)
out = ctx.out_dir
calls = []
_hr_src = {"a2": "A2", "b1b": "B1"}[lv]
_orig_kp = ctx.hooks["kp_fn"]
other_level_calls = []
def kp_fn_guard(text, kp_dir, article_id, source_level, *a, **k):
    # HR対象levelの選定が再実行されたらNG。HRで停止して未処理だった別levelの初回選定は正当(別途記録)。
    if str(source_level).upper() == _hr_src:
        calls.append(1); raise AssertionError("HR対象levelの選定が再実行された(snapshot復元されていない)")
    other_level_calls.append(str(source_level))
    return _orig_kp(text, kp_dir, article_id, source_level, *a, **k)
ctx.hooks["kp_fn"] = kp_fn_guard
snap = f"{out}/key_phrases/{lv}/gloss_alignment_pending_result.json"
res = {"level": lv, "snapshot_before": os.path.exists(snap)}
p = f"{out}/key_phrases/{lv}/keywords_canonicalized.json"
res["unresolved_before"] = [i["rank"] for i in ga.collect_unresolved(json.load(open(p, encoding="utf-8")))]
res["resolve"] = ga.resolve_gloss(p, 2, gloss, "KGCPW-E6-evidence")
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    try:
        r.run_stage(ctx, "kp"); res["stage_kp"] = "OK"
    except Exception as e:
        res["stage_kp"] = f"{type(e).__name__}: {str(e)[:300]}"
res["kp_fn_calls_after_resolve_for_HR_level"] = len(calls); res["other_level_first_selection_calls"] = other_level_calls
res["snapshot_after"] = os.path.exists(snap)
res["consumed_exists"] = os.path.exists(snap.replace(".json", ".consumed.json"))
d = json.load(open(f"{out}/{lv}/key_phrases/keywords_canonicalized.json", encoding="utf-8"))
res["deployed_rank2"] = {k: d["items"][1].get(k) for k in ("key_phrase", "japanese_gloss", "gloss_alignment_status")}
res["unresolved_after"] = [i["rank"] for i in ga.collect_unresolved(d)]
tts = f"tts_{lv}"
buf2 = io.StringIO()
with contextlib.redirect_stdout(buf2):
    try:
        r.run_stage(ctx, tts); res["tts_stage"] = "OK(mock TTS)"
    except Exception as e:
        res["tts_stage"] = f"{type(e).__name__}: {str(e)[:300]}"
print(json.dumps(res, ensure_ascii=False, indent=1, default=str))

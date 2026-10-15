# -*- coding: utf-8 -*-
"""KGCPW 委任_04 E11b: 正式 er026 main()(CLI本体)をin-processで駆動し、`_kp_fn_for_ctx`だけを差し替える(evidence専用、Production差分0)。
selection/canonicalizationは自然runのa2 mergedを録画固定(rank2を『語を足したKP』対象に加工)、alignは本物ga.align_glosses+本物make_alignment_fn+fake client(2回失敗)。
provenance: synthetic(入力・失敗注入) + production_formal_path(main/build_real_context/_launch_guard/run_stages/stage_kp/_gloss_hr_gate)。"""
import copy, importlib.util, json, os, sys, unittest.mock as mock
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *([".."] * 5)))
sys.path.insert(0, ROOT); os.chdir(ROOT)
os.environ.setdefault("TTS_EXECUTION_MODE", "STANDARD")
spec = importlib.util.spec_from_file_location("hk", os.path.join(ROOT, "er071_output/m2p0_n01_production_wiring_01/gloss_alignment_production_wiring_01/evidence/harness_kgcpw_01.py"))
hk = importlib.util.module_from_spec(spec); spec.loader.exec_module(hk)
import er026_family_z_fiction_production_runner_01 as r
import er003_key_words_gloss_alignment as ga

RUN = "er026_output/family_z_production_e2e_01/melos/run_kgcpw_z_e2e_01"
nat = json.load(open(f"{RUN}/key_phrases/a2_result.json", encoding="utf-8"))
base_merged = copy.deepcopy(nat["canonicalization"]["merged"])
calls = []

def kp_fn(text, kp_dir, article_id, source_level, process=None, **kw):
    calls.append(source_level)
    assert str(source_level).upper().startswith("A2"), source_level
    merged = copy.deepcopy(base_merged)
    for it in merged["items"]:
        if it["rank"] == 2:      # 注入: KPが表示候補より語を足した(対象)+glossが足りない
            it["kp_extends_beyond_candidate"] = True
            it["japanese_gloss"] = it["japanese_gloss_tts"] = "引き込む"
    w = hk.wrapped_make_alignment_fn("fail2")
    aligned = ga.align_glosses(merged, text, lambda msg: w(msg, model=hk._z_model("fail2", source_level)), out_dir=kp_dir,
                               article_id=article_id, enabled=True)
    os.makedirs(kp_dir, exist_ok=True)
    json.dump(aligned["merged"], open(f"{kp_dir}/keywords_canonicalized.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return {"selection": {"status": "KEY_WORDS_STRUCTURE_PASS"},
            "canonicalization": {"status": "CANONICALIZATION_PASS", "merged": aligned["merged"]},
            "redundancy_qa": {"status": "REDUNDANCY_OK"}, "redundancy_retry_log": []}

argv = sys.argv[1:]
with mock.patch.object(r, "_kp_fn_for_ctx", lambda ctx: kp_fn):
    rc = r.main(argv)
print(f"[INJECT] main rc={rc} kp_fn_levels={calls}")
sys.exit(rc)

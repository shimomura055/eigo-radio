# Trial-07 テスト(API 0)。 py test_trial_07.py
# (1) run_trial_07 selftest(規則・FRONT採否・学習価値・ELL・0件経路・引用連結回帰[Trial-06 open_window r2の固定データ]・費用ガード)
# (2) 許容集合の書き写し照合 (3) mock LLMでのend-to-end: 引用連結を返すLLM -> P21が復元され選定される / 全て基礎のLLM -> 0件・Step B call 0・固定文のみ
import os, sys, json, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_trial_07 as t7, analyze_07 as a7, run_trial_04 as t4
t7.selftest()
for w in t7.WORKS7:
    for tab in (a7.CORE[w], a7.EITHER[w]):
        for k, key in tab.items(): assert t4._qn(key) in t4._qn(" ".join(t7.work_data7(w)["body"])), (w, k, key)
tmp = tempfile.mkdtemp(); t7.BASE = tmp; calls = []
USAGE = {"model_actual": "mock", "elapsed_sec": 0, "input_tokens": 0, "output_tokens": 0, "reasoning_tokens": 0, "cost_jpy_at_160": 0.0}
CONCAT = {"features": [{"para": "P21", "sentence": t7.OW_R2_P21_RAW, "feature_class": "INV", "front_kind": "", "misread_target": "SUBJECT", "misread_quote": "came a young voice",
                        "misread_ja": "x", "omitted_words": "", "basic_only": False, "teaching_value": "HIGH", "teaching_value_ja": "場所句が文頭に出ると主語と動詞が逆順になる",
                        "construct_ja": "場所の副詞句の倒置", "points_ja": ["p"], "context_ja": "ctx"}], "no_feature_paras": []}
def mock_concat(prompt, tag): calls.append(tag); return json.dumps(CONCAT, ensure_ascii=False), USAGE
j = t7.run_stepa7("open_window", "t1", mock_concat)
assert [x["sentence"] for x in j["rule_selected"]["selected"]] == ["Across the quiet garden came a young voice:"], j["rule_selected"]
assert j["rule_selected"]["records"][0]["cross_para_flag"] == "cross_para_trimmed_tail" and j["rule_selected"]["records"][0]["single_span_ok"] is True
ALLBASIC = {"features": [{"para": "P1", "sentence": t4._sents(t7.work_data7("melos")["body"][0])[0], "feature_class": "OTHER", "basic_only": True}], "no_feature_paras": []}
def mock_zero(prompt, tag): calls.append(tag); return json.dumps(ALLBASIC, ensure_ascii=False), USAGE
j0 = t7.run_stepa7("melos", "t1", mock_zero); assert j0["rule_selected"]["selected"] == [] and j0["rule_selected"]["records"] == []
n_before = len(calls)
def must_not_call(prompt, tag): raise SystemExit("Step B must not be called for zero selection")
t7.run_stepb7("melos", "t1", must_not_call); assert len(calls) == n_before
u = open(os.path.join(tmp, "OUTPUT_07_melos_t1_USER.md"), encoding="utf-8").read(); assert t4.ZERO_P2 in u and "###" not in u
assert "Step B callなし" in open(os.path.join(tmp, "OUTPUT_07_melos_t1_DEV.md"), encoding="utf-8").read()
print("test_trial_07 OK")

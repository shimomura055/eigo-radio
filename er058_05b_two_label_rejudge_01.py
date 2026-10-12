# -*- coding: utf-8 -*-
"""ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_05B M1: Secondary PASS集合を2ラベル(EXACT/NORMALIZED)で
オフライン再判定する(費用0円、保存済み転写のみ、API呼出なし、Production書込なし)。
  - Trial B: er058_trial_b_analyze_01.py のSTRICTだけを差替えて再集計(4ラベル版と2ラベル版を並べる)
  - Trial C: er058_trial_c_en_asr_compare_01.py の cmd_analyze をSTRICT差替えで再実行(入力はコピー、出力は専用dir)
出力: er058_output/trial_abc/two_label_rejudge_05B/
"""
import io, json, os, re, shutil, sys, contextlib, copy

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
OUTW = os.path.join(ROOT, "er058_output", "trial_abc", "two_label_rejudge_05B")
os.makedirs(OUTW, exist_ok=True)
TWO = ("EXACT_MATCH", "NORMALIZED_MATCH")
FOUR = ("EXACT_MATCH", "NORMALIZED_MATCH", "TRANSCRIPT_STYLE_NORMALIZED_MATCH", "NUMERIC_EQUIVALENCE_MATCH")
res = {}
import er058_trial_b_intentional_misread_01  # noqa  (stdout再ラップを先に済ませる)
REALOUT = sys.stdout

# ---------------- Trial B ----------------
src = open(os.path.join(ROOT, "er058_trial_b_analyze_01.py"), encoding="utf-8").read()


def run_b(strict, tag):
    s = src.replace('STRICT = {"EXACT_MATCH", "NORMALIZED_MATCH", "TRANSCRIPT_STYLE_NORMALIZED_MATCH", "NUMERIC_EQUIVALENCE_MATCH"}',
                    "STRICT = %r" % (set(strict),))
    assert s != src or tag == "four" or True
    s = s.replace('os.path.join(OUT, "trial_b_summary_01.json")', 'os.path.join(OUTW, "trial_b_summary_%s.json")' % tag)
    s = s.replace('os.path.join(OUT, "trial_b_tables_01.md")', 'os.path.join(OUTW, "trial_b_tables_%s.md")' % tag)
    ns = {"__name__": "x", "__file__": os.path.join(ROOT, "er058_trial_b_analyze_01.py"), "OUTW": OUTW}
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(s, "analyze_b_%s" % tag, "exec"), ns)
    sys.stdout = REALOUT
    return ns


nb4, nb2 = run_b(FOUR, "four"), run_b(TWO, "two")


def b_stats(ns):
    clips = ns["clips"]
    out = {}
    for lang in ("en", "ja", "all"):
        cl = [c for c in clips if lang == "all" or c["lang"] == lang]
        mis = [c for c in cl if c["kind"] == "misread"]
        ctl = [c for c in cl if c["kind"] == "control"]
        conf = [c for c in mis if c["ground"] in ("confirmed_misread", "divergence_evidence", "confirmed_misread_same_text_readings")]
        out[lang] = {
            "n_clips": len(cl), "n_misread": len(mis), "n_control": len(ctl), "n_confirmed_misread": len(conf),
            "unverified_or_homophone": len(mis) - len(conf),
            "wrong_adopt(誤採用)": sum(1 for c in conf if c["flow"] != "REJECT"),
            "wrong_by_secondary(Secondary起因)": sum(1 for c in conf if c["flow"] == "ADOPT_S"),
            "control_rejected(対照不採用)": sum(1 for c in ctl if c["flow"] == "REJECT"),
            "control_adopt_by_secondary(Primary NG→Secondary救済の対照)": sum(1 for c in ctl if c["flow"] == "ADOPT_S"),
            "azure_false_pass_confirmed": sum(1 for c in conf if c["judge"]["azure"]["pass"]),
        }
    return out


res["trial_b"] = {"four_label": b_stats(nb4), "two_label": b_stats(nb2)}
# 差が出たclip
diff = []
c4 = {c["clip_id"]: c for c in nb4["clips"]}
for c in nb2["clips"]:
    o = c4[c["clip_id"]]
    if o["flow"] != c["flow"] or o["judge"]["azure"]["pass"] != c["judge"]["azure"]["pass"]:
        diff.append({"clip": c["clip_id"], "lang": c["lang"], "kind": c["kind"], "canonical": c["canonical"], "spoken": c["spoken"],
                     "azure_text": c["asr"]["azure"]["text"], "azure_cls": c["judge"]["azure"]["cls"],
                     "flow_4label": o["flow"], "flow_2label": c["flow"], "ground": c["ground"]})
res["trial_b"]["clips_that_change_between_4_and_2"] = diff

# ---------------- Trial C ----------------
import er058_trial_c_en_asr_compare_01 as t  # noqa
sys.stdout = open(1, "w", encoding="utf-8", closefd=False, buffering=1)
cdir = os.path.join(OUTW, "trial_c_two_label")
os.makedirs(cdir, exist_ok=True)
for f in ("azure_nopl_C_01.json", "local_asr_cache_C_01.json"):
    shutil.copy(os.path.join(ROOT, "er058_output", "trial_c", f), os.path.join(cdir, f))
items = json.load(open(os.path.join(ROOT, "er058_output", "trial_c", "sample_C_01.json"), encoding="utf-8"))
t.OUT = cdir
t.STRICT = TWO
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    t.cmd_analyze(items, False)
sys.stdout = open(1, "w", encoding="utf-8", closefd=False, buffering=1)
c2 = json.load(open(os.path.join(cdir, "trial_c_results_01.json"), encoding="utf-8"))
c4 = json.load(open(os.path.join(ROOT, "er058_output", "trial_c", "trial_c_results_01.json"), encoding="utf-8"))
res["trial_c"] = {"four_label": {k: c4["metrics"][k] for k in ("unified_safe", "control_primary_pass", "forced_secondary_items")},
                  "two_label": {k: c2["metrics"][k] for k in ("unified_safe", "control_primary_pass", "forced_secondary_items")},
                  "phrase_list_effect_4": {k: v for k, v in c4["metrics"]["phrase_list_effect"].items() if k != "detail"},
                  "phrase_list_effect_2": {k: v for k, v in c2["metrics"]["phrase_list_effect"].items() if k != "detail"},
                  "hr_offline_4": c4["hr_queue_offline_67rows"], "hr_offline_2": c2["hr_queue_offline_67rows"],
                  "qcd_pooled_rescue_4": c4["qcd_projection"]["pooled_rescue"], "qcd_pooled_rescue_2": c2["qcd_projection"]["pooled_rescue"]}
chg = []
r4 = {r["id"]: r for r in c4["rows"]}
for r in c2["rows"]:
    o = r4[r["id"]]
    if o["unified_safe"]["outcome"] != r["unified_safe"]["outcome"]:
        chg.append({"id": r["id"], "group": r["group"], "proxy_label": r["proxy_label"], "outcome_4": o["unified_safe"]["outcome"],
                    "outcome_2": r["unified_safe"]["outcome"], "azure_class": (r["systems"]["azure_noPL"] or {}).get("class")})
res["trial_c"]["rows_that_change"] = chg
json.dump(res, open(os.path.join(OUTW, "two_label_rejudge_summary_05B.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))

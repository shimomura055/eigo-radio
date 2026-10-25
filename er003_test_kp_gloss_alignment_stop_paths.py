# -*- coding: utf-8 -*-
"""KGCPW 委任_02: gloss再整合(修正版が唯一の方式)の失敗系・停止系 mock統合test(JPY0、実API・実TTS呼出なし)。

出自: er071_gloss_alignment_correction_01_t3_mock.py(KGDC T3 27シナリオ)を、legacy撤去(mode引数廃止)に合わせて移植した保守対象test
(OF-KGCPW-13)。移植先をer003_test_key_words_gloss_alignment.pyへ入れず独立ファイルにした理由: 本シナリオ群はrunner(X/Z)・Gate・
subprocessを跨ぐ統合型で、順序依存の共有fixture(HR artifactを作る->X TTS->Gate->resolve->再開)を持ち、unit testと混在させると
実行時間と責務が混ざるため。シナリオはsetUpClassで1回実行し、IDごとにsubTestで判定する(IDの欠落もtestで検出)。
移植しなかったシナリオ: T3(k-ga)=legacy版とHEAD版の出力同一性比較(legacy撤去により意味が消滅。API request bytesの同一性は
er003_test_kp_gloss_alignment_wiring.pyのgolden testが担う)。書換えたシナリオ: T3(k-X)=旧版"FAILED"も停止(OF-KGCPW-14)、T3(v)=
X scaffoldのsummary(mode引数廃止)、T3(j)/(m)=HR停止時にassetsを配備(OF-KGCPW-09)、T3(k-Z)=既定mock kp stageの通過。
usage(別プロセスdriver): .venv/Scripts/python.exe er003_test_kp_gloss_alignment_stop_paths.py --driver z|x --work <dir>
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest.mock as mock

import unittest


import er003_key_words_canonicalization as kc  # noqa: E402
import er003_key_words_gloss_alignment as ga  # noqa: E402
from er119_test_support_01 import declare_ctx as _declare_ctx  # noqa: E402

REPO = os.path.dirname(os.path.abspath(__file__))
RESULTS: list = []
API_ATTEMPTS = {"n": 0}          # 禁止patchに到達した回数(0でなければ失敗)
STUB_CALLS = {"tts": 0, "expl_llm": 0, "expl_tts": 0}
MONITORED = ["er011_output/attempt_history.jsonl", "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl",
             "er006_output/master_audio_store_01/manifest.json", "er006_output/master_audio_store_01/reuse_telemetry.jsonl",
             "er030_output/kp_backend_telemetry_01/telemetry.jsonl", "er005_output/cost_baseline_01/cost_summary.json"]


def sha_of(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else None


def snapshot_monitored():
    return {p: sha_of(os.path.join(REPO, p)) for p in MONITORED}


def record(pid, title, passed, evidence):
    RESULTS.append({"id": pid, "title": title, "pass": bool(passed), "api_calls": 0, "evidence": evidence})
    print(f"[T3][{'PASS' if passed else 'FAIL'}] {pid}: {title}")


# ---------------------------------------------------------------- fixtures
class FakeFn:
    def __init__(self, payloads):
        self.payloads, self.calls = list(payloads), 0

    def __call__(self):
        self.calls += 1
        p = self.payloads.pop(0)
        if isinstance(p, Exception):
            raise p
        return (p if isinstance(p, str) else json.dumps(p, ensure_ascii=False)), "gpt-6-luna", "resp_mock"


def resp(items):
    return {"items": [{"rank": r, "current_gloss_consistent": c, "japanese_gloss": g,
                       "added_word_mappings": [{"english_word": e, "japanese_span": j} for e, j in mp],
                       "qa_reflects_all_key_phrase_words": q, "reasoning": "mock"} for r, c, g, mp, q in items]}


def bad(rank):
    return resp([(rank, False, "x", [], "FAIL")])


def legacy_resp(items):
    return {"items": [{"rank": r, "current_gloss_consistent": c, "japanese_gloss": g,
                       "qa_reflects_all_key_phrase_words": q, "reasoning": "mock"} for r, c, g, q in items]}


def factory(payloads):
    fn = FakeFn(payloads)
    msgs = []

    def make(msg):
        msgs.append(msg)
        return fn
    return fn, make, msgs


ORIGINALS = [
    {"rank": 1, "display_phrase": "right away", "source_span": "right away", "source_sentence": "Do it right away.",
     "ja_gloss": "すぐに", "source_reference_contract": "X"},
    {"rank": 2, "display_phrase": "based on", "source_span": "based on",
     "source_sentence": "It is an estimate based on interviews with sellers.", "ja_gloss": "～をもとにした",
     "source_reference_contract": "X"},
    {"rank": 3, "display_phrase": "give back", "source_span": "give back", "source_sentence": "They give back the money.",
     "ja_gloss": "返す", "source_reference_contract": "X"},
    {"rank": 4, "display_phrase": "point to", "source_span": "point to", "source_sentence": "Studies point to a rise.",
     "ja_gloss": "～を示す", "source_reference_contract": "X"},
    {"rank": 5, "display_phrase": "locked into", "source_span": "locked into",
     "source_sentence": "Buyers were locked into a narrow view.", "ja_gloss": "とらわれた", "source_reference_contract": "X"},
]
QA = {f: "PASS" for f in kc.QA_FIELDS}


def canon_parsed(kp2="based on interviews", kp5="locked into"):
    def it(rank, kp, disp):
        return {"rank": rank, "key_phrase": kp, "changed_from_display_phrase": kp != disp,
                "normalization_reason": "restore_semantic_complement" if kp != disp else "none", "reasoning": "r", **QA}
    return {"items": [it(1, "right away", "right away"), it(2, kp2, "based on"), it(3, "give back", "give back"),
                      it(4, "point to", "point to"), it(5, kp5, "locked into")]}


@contextlib.contextmanager
def run_key_phrases_env(selections, canon_parsed_list, redundancy_list, align_fn):
    """実Production関数 sc.run_key_phrases(外側retryループ込み)を、LLM境界だけmockして動かす。"""
    import er003_v1_n3_01_scaffold_generate as sc
    sel_iter, canon_iter, red_iter = iter(selections), iter(canon_parsed_list), iter(redundancy_list)

    def sel(*a, **k):
        return next(sel_iter)

    def gate(*a, **k):
        return next(canon_iter), "CANONICALIZATION_PASS", [], "gpt-6-luna", "resp"

    def red(*a, **k):
        return next(red_iter)
    with mock.patch.object(sc, "run_key_phrase_selection", side_effect=sel), \
            mock.patch.object(sc.kc, "run_canonicalization_gate", side_effect=gate), \
            mock.patch.object(sc, "run_key_phrase_redundancy_qa", side_effect=red), \
            mock.patch.object(sc.gloss_align, "make_alignment_fn", side_effect=align_fn):
        yield sc


def one_selection():
    return {"status": "KEY_WORDS_STRUCTURE_PASS", "original_items": [dict(x) for x in ORIGINALS], "cost_jpy": 0.0}


RED_OK = {"status": "REDUNDANCY_OK", "duplicate_pairs": []}
RED_NG = {"status": "REDUNDANCY_NG", "duplicate_pairs": [{"rank_a": 1, "rank_b": 3, "reasoning": "mock"}]}


def run_kp(d, align_payloads, parsed=None, mapping_gate=False):
    """run_key_phrases(corrected)を1回。align_payloads=alignment LLM(fake)の応答列。戻り=(result, fake_fn, stdout)。"""
    fn = FakeFn(align_payloads)
    buf = io.StringIO()
    with run_key_phrases_env([one_selection()], [parsed or canon_parsed()], [RED_OK], lambda msg, **kw: fn) as sc:
        with contextlib.redirect_stdout(buf):
            res = sc.run_key_phrases("ART", d, "AID", "A2")
    return res, fn, buf.getvalue()


def load_kp(d):
    return json.load(open(os.path.join(d, "keywords_canonicalized.json"), encoding="utf-8"))


def validate_notice(d):
    return ga.validate_hr_report(os.path.join(d, ga.HR_REPORT_JSON))


GOOD2 = (2, False, "インタビューをもとにした", [("interviews", "インタビュー")], "PASS")
GOOD5 = (5, False, "狭い見方にとらわれた", [("narrow", "狭い"), ("view", "見方")], "PASS")


# ---------------------------------------------------------------- X stubs
@contextlib.contextmanager
def x_stubs(x, tts_ok=True):
    """X runnerのTTS/解説LLM入口をカウントstubへ(呼ばれた回数=STUB_CALLS)。実APIは無い。"""
    def ok(path=None, **kw):
        return {"status": "OK", "path": path}

    def en(text, wav, **k):
        STUB_CALLS["tts"] += 1
        return {"status": "OK", "path": wav, "disfluency_checked": True}   # 正式Validation済みを装う(Gate陽性対照用stub)

    def ja(text, wav, *a, **k):
        STUB_CALLS["tts"] += 1
        return {"status": "OK", "path": wav}

    def expl_gen(items, **k):
        STUB_CALLS["expl_llm"] += 1
        return {"items": {it["rank"]: {"status": "OK", "english_explanation": "to be stuck", "qa": {}} for it in items}}

    def expl_tts(text, wav, **k):
        STUB_CALLS["expl_tts"] += 1
        return {"status": "OK", "path": wav}
    with mock.patch.object(x.kp_vote, "ensure_key_phrase_english_component_x_vote", side_effect=en), \
            mock.patch.object(x.n3_tts, "generate_a2_japanese_with_reading_safety", side_effect=ja), \
            mock.patch.object(x.kp_explanation_gen, "generate_kp_explanations", side_effect=expl_gen), \
            mock.patch.object(x, "generate_key_phrase_explanation_en_verified", side_effect=expl_tts):
        yield


def stub_delta(fn):
    b = dict(STUB_CALLS)
    out = fn()
    return out, {k: STUB_CALLS[k] - b[k] for k in STUB_CALLS}


def gate_blocked(level_dir, level, kp_results, article_text=None):
    """tts_generation_results.json相当を書き、既存Audio Validation Gate(無変更)を呼ぶ。戻り=(blocked?, message)。"""
    import er003_v1_n3_01_assemble as asm
    os.makedirs(f"{level_dir}/audit", exist_ok=True)
    json.dump({"segments": {}, "key_phrases": kp_results}, open(f"{level_dir}/audit/tts_generation_results.json", "w",
                                                                 encoding="utf-8"), ensure_ascii=False, indent=2)
    try:
        asm.verify_episode_audio_validation_gate(level_dir, level, article_text=article_text)
        return False, ""
    except RuntimeError as e:
        return True, str(e)


def make_level_with_hr(base, name, failing_ranks=(2,)):
    """run_key_phrases(corrected)で実際に生成したartifact(HR待ちあり)を <base>/<name>/key_phrases/ に置く。"""
    lvl = os.path.join(base, name)
    kp_dir = os.path.join(lvl, "key_phrases")
    os.makedirs(kp_dir, exist_ok=True)
    payloads = [resp([GOOD5, (2, False, "x", [], "FAIL")]), bad(2)]
    res, fn, out = run_kp(kp_dir, payloads, parsed=canon_parsed(kp5="locked into a narrow view"))
    return lvl, kp_dir, res, fn, out


# ---------------------------------------------------------------- patterns
def pat_a_to_e(base):
    # (a) API例外2回
    d = os.path.join(base, "a"); os.makedirs(d)
    res, fn, out = run_kp(d, [RuntimeError("boom1"), RuntimeError("boom2")])
    kp = load_kp(d)
    record("T3(a)", "alignment API例外2回 -> FAILED_HUMAN_REVIEW_REQUIRED(KP維持・旧gloss維持)+HR報告書+event+stdout",
           fn.calls == 2 and [x["rank"] for x in ga.collect_unresolved(kp)] == [2] and not validate_notice(d)
           and len(res["gloss_alignment_human_review_events"]) == 1 and res.get("status") == ga.STOPPED_STATUS
           and "[GLOSS-ALIGN][HUMAN-REVIEW-REQUIRED]" in out and kp["items"][1]["key_phrase"] == "based on interviews"
           and kp["items"][1]["japanese_gloss"] == "～をもとにした",
           {"calls": fn.calls, "status": res.get("status"), "attempt_verdicts":
            [a["verdict"] for a in kp["items"][1]["gloss_alignment"]["failure"]["attempts"]]})
    # (b) JSON不正2回
    d = os.path.join(base, "b"); os.makedirs(d)
    res, fn, out = run_kp(d, ["not json", "{broken"])
    kp = load_kp(d)
    record("T3(b)", "JSON不正2回 -> HR待ち", fn.calls == 2 and len(ga.collect_unresolved(kp)) == 1 and not validate_notice(d),
           {"verdicts": [a["verdict"] for a in kp["items"][1]["gloss_alignment"]["failure"]["attempts"]]})
    # (c) 不正gloss(括弧/算用数字/…)2回
    d = os.path.join(base, "c"); os.makedirs(d)
    res, fn, out = run_kp(d, [resp([(2, False, "インタビュー(取材)をもとにした", [("interviews", "インタビュー")], "PASS")]),
                              resp([(2, False, "2つのインタビュー…", [("interviews", "インタビュー")], "PASS")])])
    kp = load_kp(d)
    rs = [r for a in kp["items"][1]["gloss_alignment"]["failure"]["attempts"] for r in a["reasons"]]
    record("T3(c)", "不正gloss(括弧/算用数字/…)2回 -> HR待ち", len(ga.collect_unresolved(kp)) == 1
           and any("括弧" in r for r in rs) and any("算用数字" in r for r in rs) and any("…" in r for r in rs), {"reasons": rs})
    # (d) mapping欠落2回: gate=HR待ち / record-only=採用され機械検査は不合格として並記
    d = os.path.join(base, "d_gate"); os.makedirs(d)
    nomap = resp([(2, False, "インタビューをもとにした", [], "PASS")])
    fn = FakeFn([nomap, nomap])
    with run_key_phrases_env([one_selection()], [canon_parsed()], [RED_OK], lambda msg, **kw: fn) as sc:
        # mapping gateはalign_glosses引数(Trial用)。scaffold経由の既定はrecord-only。gateはmodule関数で直接検証する。
        pass
    merged = ga.align_glosses({"items": [dict(ga_item(ORIGINALS[1], "based on interviews"))]}, "art",
                              lambda m: FakeFn([nomap, nomap]), enabled=True, mapping_gate=True)
    d_rec = ga.align_glosses({"items": [dict(ga_item(ORIGINALS[1], "based on interviews"))]}, "art",
                             lambda m: FakeFn([nomap]), enabled=True, mapping_gate=False)
    it_rec = d_rec["merged"]["items"][0]
    record("T3(d)", "mapping欠落: gate判定=HR待ち / record-only=LLM判定で採用+machine_check不合格を並記(誤NG/誤PASS採否材料)",
           merged["status"] == "ALIGN_FAILED_HUMAN_REVIEW_REQUIRED" and d_rec["status"] == "ALIGN_PASS"
           and it_rec["gloss_alignment"]["machine_check_record_only"]["pass"] is False
           and it_rec["gloss_alignment"]["machine_check_record_only"]["uncovered"] == ["interviews"],
           {"gate_status": merged["status"], "record_only_status": d_rec["status"],
            "record_only_machine_check": it_rec["gloss_alignment"]["machine_check_record_only"]})
    # (e) 1回目失敗 -> 2回目成功: 採用、HR無し
    d = os.path.join(base, "e"); os.makedirs(d)
    res, fn, out = run_kp(d, [bad(2), resp([GOOD2])])
    kp = load_kp(d)
    record("T3(e)", "1回目失敗->2回目成功: 採用・HR報告書なし・event空・非OK statusなし",
           fn.calls == 2 and res["gloss_alignment_human_review_events"] == [] and "status" not in res
           and not os.path.exists(os.path.join(d, ga.HR_REPORT_JSON)) and kp["items"][1]["japanese_gloss"] == "インタビューをもとにした"
           and "[GLOSS-ALIGN][HUMAN-REVIEW-REQUIRED]" not in out, {"calls": fn.calls})


def ga_item(orig, kp):
    return {"rank": orig["rank"], "display_phrase": orig["display_phrase"], "key_phrase": kp, "used_form": kp,
            "japanese_gloss": orig["ja_gloss"], "japanese_gloss_tts": kc.convert_display_gloss_to_tts_text(orig["ja_gloss"]),
            "kp_extends_beyond_candidate": True, "gloss_review_hint": True, "source_sentence": orig["source_sentence"]}


def pat_f_g(base):
    # (f) 2回連続失敗 -> 報告書必須項目 + queue/Lock不使用 + event + stdout (snapshot前後)
    before = snapshot_monitored()
    d = os.path.join(base, "f"); os.makedirs(d)
    res, fn, out = run_kp(d, [bad(2), bad(2)])
    doc = json.load(open(os.path.join(d, ga.HR_REPORT_JSON), encoding="utf-8"))
    e = doc["entries"][0]
    ev = res["gloss_alignment_human_review_events"][0]
    required = all([e["article"], e["level"], isinstance(e["rank"], int), e["key_phrase_en"], e["current_japanese_gloss"],
                    e["failure_reasons"], len(e["attempts"]) == 2, e["regeneration_candidates"]["reference_candidate"]["caution"]])
    after = snapshot_monitored()
    record("T3(f)", "2回連続失敗: 報告書必須項目(article/level/rank/英語KP/現gloss/失敗理由/全attempt/再生成候補)+event+stdout、queue/Lock/attempt_history不使用",
           required and not validate_notice(d) and ev["queue_used"] is False and ev["human_review_lock_used"] is False
           and after == before and "[GLOSS-ALIGN][HUMAN-REVIEW-REQUIRED]" in out,
           {"entry_keys": sorted(e), "event": {k: ev[k] for k in ("article", "level", "ranks", "report_schema_validated")},
            "monitored_unchanged": after == before, "stdout_line": out.strip().splitlines()[-1][:200]})
    shutil.copy(os.path.join(d, ga.HR_REPORT_JSON), os.path.join(base, "_evidence_report.json"))
    shutil.copy(os.path.join(d, ga.HR_REPORT_MD), os.path.join(base, "_evidence_report.md"))
    # (g) batch内一部成立・一部失敗(item単位): rank5成立 / rank2失敗
    d = os.path.join(base, "g"); os.makedirs(d)
    res, fn, out = run_kp(d, [resp([GOOD5, (2, False, "x", [], "FAIL")]), bad(2)], parsed=canon_parsed(kp5="locked into a narrow view"))
    kp = load_kp(d)
    st = {it["rank"]: it["gloss_alignment_status"] for it in kp["items"] if it["rank"] in (2, 5)}
    record("T3(g)", "batch内一部成立・一部失敗: 成立分(rank5)は採用、未解決(rank2)のみHR待ち、2回目は未解決のみ送信",
           st == {2: ga.STATUS_HR_REQUIRED, 5: "ALIGNED"} and kp["items"][4]["japanese_gloss"] == "狭い見方にとらわれた"
           and [x["rank"] for x in ga.collect_unresolved(kp)] == [2] and res["gloss_alignment_human_review_events"][0]["ranks"] == [2],
           {"status_by_rank": st, "calls": fn.calls})


def pat_h(base):
    """(h) HR通知の書込失敗 -> fail-closed(例外でstage停止。『通知失敗だが継続』しない)。X側(run_key_phrases)とZ側で検証。"""
    import er003_v1_n3_01_scaffold_generate as sc
    out = {}
    real_open = open
    # report json書込失敗
    for label, endswith in (("json_write_fail", ga.HR_REPORT_JSON), ("md_write_fail", ga.HR_REPORT_MD)):
        d = os.path.join(base, "h_" + label); os.makedirs(d)

        def bad_open(path, *a, _e=endswith, **k):
            if str(path).endswith(_e) and any(m in (a[0] if a else k.get("mode", "r")) for m in ("w",)):
                raise OSError("disk full (mock)")
            return real_open(path, *a, **k)
        raised = None
        fn = FakeFn([bad(2), bad(2)])
        with run_key_phrases_env([one_selection()], [canon_parsed()], [RED_OK], lambda msg, **kw: fn) as sc_:
            with mock.patch("builtins.open", side_effect=bad_open), contextlib.redirect_stdout(io.StringIO()):
                try:
                    sc_.run_key_phrases("ART", d, "AID", "A2")
                except ga.GlossAlignmentNotificationError as e:
                    raised = str(e)
        out[label] = raised
    # 再読検証失敗(スキーマ不備)
    d = os.path.join(base, "h_reread"); os.makedirs(d)
    fn = FakeFn([bad(2), bad(2)])
    raised = None
    with run_key_phrases_env([one_selection()], [canon_parsed()], [RED_OK], lambda msg, **kw: fn) as sc_:
        with mock.patch.object(ga, "validate_hr_report", return_value=["entry0.attemptsが空"]), contextlib.redirect_stdout(io.StringIO()):
            try:
                sc_.run_key_phrases("ART", d, "AID", "A2")
            except ga.GlossAlignmentNotificationError as e:
                raised = str(e)
    out["reread_validation_fail"] = raised
    record("T3(h)", "HR報告の書込失敗/再読検証失敗 -> GlossAlignmentNotificationErrorで当該stage停止(fail-closed)",
           all(out.values()), {k: (v or "")[:120] for k, v in out.items()})


def pat_i_o_p_q(base, x):
    lvl, kp_dir, res, fn, out = make_level_with_hr(base, "x_a2")
    kp = load_kp(kp_dir)
    narr = f"{lvl}/narration"; os.makedirs(narr, exist_ok=True)
    # (i) A2: 0 API call + Gate拒否
    with x_stubs(x):
        results, delta = stub_delta(lambda: x._generate_key_phrase_segments_a2(kp, narr, None))
    statuses = {(r, role): v["status"] for r, d_ in results.items() for role, v in d_.items()}
    blocked, msg = gate_blocked(lvl, "A2", results)
    record("T3(i-A2)", "FAILED itemのlevelはKP segment全体(5rank x en/ja)がSTOPPED_GLOSS_ALIGNMENT_FAILED・TTS 0 call・Gateがassembly拒否",
           delta == {"tts": 0, "expl_llm": 0, "expl_tts": 0} and set(statuses.values()) == {ga.STOPPED_STATUS}
           and len(statuses) == 10 and blocked and "EPISODE_BLOCKED_BY_AUDIO_VALIDATION" in msg,
           {"tts_calls": delta, "n_segments_stopped": len(statuses), "gate_message_head": msg[:160]})
    # (i-B1) B1: 解説LLMも0 call
    lvl_b, kp_dir_b, *_ = make_level_with_hr(base, "x_b1b")
    kp_b = load_kp(kp_dir_b)
    narr_b = f"{lvl_b}/narration"; os.makedirs(narr_b, exist_ok=True)
    with x_stubs(x):
        (results_b, bundle), delta_b = stub_delta(lambda: x._generate_key_phrase_segments_b1(kp_b, narr_b, None))
    blocked_b, msg_b = gate_blocked(lvl_b, "B1", results_b)
    record("T3(p)", "B1: 解説LLM・解説TTS・KP TTSいずれも0 call(glossが解説LLM入力になる経路を停止)、explanation segmentはSTOPPED、Gate拒否",
           delta_b == {"tts": 0, "expl_llm": 0, "expl_tts": 0} and bundle is None
           and all(v["explanation"]["status"] == ga.STOPPED_STATUS for v in results_b.values()) and blocked_b,
           {"calls": delta_b, "explanation_status": results_b[2]["explanation"]["status"], "bundle": bundle})
    # (o) tts_generation_results.json欠落: 既存Gateはreturn(fail-open既存挙動)だが、assemble前の新チェックが拒否
    import er003_v1_n3_01_assemble as asm
    lvl_o = os.path.join(base, "x_o")
    os.makedirs(f"{lvl_o}/key_phrases"); os.makedirs(f"{lvl_o}/audit")
    shutil.copy(f"{kp_dir}/keywords_canonicalized.json", f"{lvl_o}/key_phrases/keywords_canonicalized.json")
    gate_returned = asm.verify_episode_audio_validation_gate(lvl_o, "A2") is None       # results欠落=既存Gateは素通り
    try:
        x._assert_no_gloss_alignment_hr(lvl_o, "A2")
        pre = None
    except RuntimeError as e:
        pre = str(e)
    # stage_assemble本体も、Gateより前に同じ拒否をすることを確認
    try:
        x.stage_assemble_family_x_a2(os.path.dirname(lvl_o), "t")
        sa = None
    except RuntimeError as e:
        sa = str(e)
    except Exception as e:   # assemble本体の別理由(拒否でない)なら失敗扱い
        sa = "OTHER:" + type(e).__name__
    record("T3(o)", "tts_generation_results.json欠落: 既存Gateは素通り(既存fail-open)だが、assemble前チェックEPISODE_BLOCKED_BY_GLOSS_ALIGNMENTが拒否",
           gate_returned and pre and "EPISODE_BLOCKED_BY_GLOSS_ALIGNMENT" in pre,
           {"existing_gate_returned_without_raise": gate_returned, "pre_check": (pre or "")[:140], "stage_assemble": (sa or "")[:100]})
    # (q) page/playerにFAILED glossが出ない
    lvl_q = os.path.join(base, "x_q"); os.makedirs(f"{lvl_q}/key_phrases"); os.makedirs(f"{lvl_q}/audit")
    shutil.copy(f"{kp_dir}/keywords_canonicalized.json", f"{lvl_q}/key_phrases/keywords_canonicalized.json")
    json.dump([], open(f"{lvl_q}/audit/timeline.json", "w")); json.dump({}, open(f"{lvl_q}/parts.json", "w"))
    json.dump({"status": "OK"}, open(f"{lvl_q}/run_summary_assemble.json", "w"))
    html_ok_summary = x._build_level_table(lvl_q, "a2")
    json.dump({"status": "BLOCKED"}, open(f"{lvl_q}/run_summary_assemble.json", "w"))
    html_blocked = x._build_level_table(lvl_q, "a2")
    old_gloss = "～をもとにした"
    record("T3(q)", "page/player: HR待ちglossは(assemble summaryがOKを装っても/BLOCKEDでも)tableに出ない",
           old_gloss not in html_ok_summary and old_gloss not in html_blocked and "based on interviews" not in html_ok_summary,
           {"html_with_ok_summary": html_ok_summary, "html_blocked": html_blocked[:100]})
    return lvl, kp_dir, kp


def pat_k_t(base, x, lvl, kp_dir, kp):
    # (k) 旧版(ER-003-KP-GLOSS-ALIGN-01)が書いた"FAILED"もHR待ちとして停止する(OF-KGCPW-14。旧: legacy FAILEDはTTSへ進んだ)
    old_kp = json.loads(json.dumps(kp))
    for it in old_kp["items"]:
        if it.get("gloss_alignment_status") == ga.STATUS_HR_REQUIRED:
            it["gloss_alignment_status"] = "FAILED"      # 旧版が書いた状態
    narr = os.path.join(base, "x_oldfailed_narr"); os.makedirs(narr)
    with x_stubs(x):
        results, delta = stub_delta(lambda: x._generate_key_phrase_segments_a2(old_kp, narr, None))
    record("T3(k-X)", "旧版FAILED artifactも関所で停止(TTS 0 call・10 segmentがSTOPPED_GLOSS_ALIGNMENT_FAILED)",
           delta["tts"] == 0 and all(v["status"] == ga.STOPPED_STATUS for d_ in results.values() for v in d_.values()), {"tts_calls": delta})
    # (r) 統計汚染なし(全体は最後にも再確認)
    # (l-X) HR解消 -> 再開でTTSが進む(選定は再実行されない)
    kp_path = f"{kp_dir}/keywords_canonicalized.json"
    ga.resolve_gloss(kp_path, 2, "インタビューをもとにした", "t3_mock", now="2026-10-15T00:00:00+00:00")
    kp2 = json.load(open(kp_path, encoding="utf-8"))
    narr2 = os.path.join(base, "x_resumed_narr"); os.makedirs(narr2)
    with x_stubs(x):
        results2, delta2 = stub_delta(lambda: x._generate_key_phrase_segments_a2(kp2, narr2, None))
    blocked2, gate_msg2 = gate_blocked(lvl, "A2", results2, article_text=" ".join(it["used_form"] for it in kp2["items"]))
    record("T3(l-X)", "resolve_gloss後の再実行: KP TTSが進む(10 call)、Gateは拒否しない。人間確定glossが入力に使われる",
           ga.collect_unresolved(kp2) == [] and delta2["tts"] == 10 and not blocked2,
           {"tts_calls": delta2, "gate_blocked": blocked2, "gate_message": gate_msg2[:200],
            "resolution": kp2["items"][1]["gloss_alignment_human_resolution"]})
    # (t) 独立level: HRのないlevelのKPは止まらない
    lvl_ok = os.path.join(base, "x_independent"); kp_ok_dir = os.path.join(lvl_ok, "key_phrases"); os.makedirs(kp_ok_dir)
    run_kp(kp_ok_dir, [resp([GOOD2, GOOD5])], parsed=canon_parsed(kp5="locked into a narrow view"))
    narr3 = os.path.join(lvl_ok, "narration"); os.makedirs(narr3)
    with x_stubs(x):
        res3, delta3 = stub_delta(lambda: x._generate_key_phrase_segments_b1(load_kp(kp_ok_dir), narr3, None))
    record("T3(t-X)", "独立level(HRなし)のB1 KPは影響を受けず通常どおり進む(解説LLM 1 call・KP TTS/解説TTS実行)",
           delta3["expl_llm"] == 1 and delta3["tts"] == 5 and delta3["expl_tts"] == 5
           and all(v["english"]["status"] == "OK" and v["explanation"]["status"] == "OK" for v in res3[0].values()),
           {"calls": delta3})


def pat_n_outer_retry(base):
    """(n) 外側redundancy retry後にHR孤児が残らない: 1回目attemptでHR待ち発生->redundancy NG->2回目attemptで全成立。
    最終artifactにunresolvedが無いのでHR報告書/eventは出ない(途中attemptのHRは孤児にならない)。"""
    d = os.path.join(base, "n"); os.makedirs(d)
    fn = FakeFn([bad(2), bad(2),                         # attempt0: rank2が2回失敗(HR待ち状態)
                 resp([GOOD2])])                          # attempt1(外側retry): 成立
    buf = io.StringIO()
    with run_key_phrases_env([one_selection(), one_selection()], [canon_parsed(), canon_parsed()], [RED_NG, RED_OK],
                             lambda msg, **kw: fn) as sc:
        with contextlib.redirect_stdout(buf):
            res = sc.run_key_phrases("ART", d, "AID", "A2")
    kp = load_kp(d)
    record("T3(n)", "外側redundancy retryで選び直した最終artifactが整合 -> HR報告書/eventなし(途中attemptのHR孤児なし)",
           res["gloss_alignment_human_review_events"] == [] and ga.collect_unresolved(kp) == []
           and not os.path.exists(os.path.join(d, ga.HR_REPORT_JSON)) and "[GLOSS-ALIGN][HUMAN-REVIEW-REQUIRED]" not in buf.getvalue()
           and res.get("redundancy_retry_attempts") == 1, {"redundancy_retry_attempts": res.get("redundancy_retry_attempts")})
    # 逆: 最終attemptがHR待ち -> 報告書は最終artifactのみ(rankは最終)
    d = os.path.join(base, "n2"); os.makedirs(d)
    fn = FakeFn([resp([GOOD2]), bad(5), bad(5)])      # attempt0: rank2成立/rank5は対象外(KP無拡張) ; attempt1: rank5(拡張)失敗
    p0, p1 = canon_parsed(), canon_parsed(kp2="based on interviews", kp5="locked into a narrow view")
    buf = io.StringIO()
    with run_key_phrases_env([one_selection(), one_selection()], [p0, p1], [RED_NG, RED_OK], lambda msg, **kw: fn) as sc:
        with contextlib.redirect_stdout(buf):
            # attempt1ではrank2/5両方が対象: 3呼出目以降の応答をattempt1用に差し替える
            fn.payloads = [resp([GOOD2]),
                           resp([GOOD2, (5, False, "x", [], "FAIL")]), bad(5)]
            res = sc.run_key_phrases("ART", d, "AID", "A2")
    doc = json.load(open(os.path.join(d, ga.HR_REPORT_JSON), encoding="utf-8"))
    record("T3(n2)", "最終attemptにHR待ちが残る場合、報告書は最終artifactの該当rankのみ(1回・過去attemptの分を含まない)",
           [e["rank"] for e in doc["entries"]] == [5] and len(res["gloss_alignment_human_review_events"]) == 1,
           {"entries_ranks": [e["rank"] for e in doc["entries"]]})


def pat_scaffold_passthrough(base, x):
    """run_theme_scaffold: mode引数なし。summaryにevent/kp_run_status/gloss_alignment_run_status/flag/metricsが無条件で載り、
    最終専用stdout行はdisk上のartifact(collect_unresolved)基準(OF-KGCPW-03/04/05/11/16)。"""
    import er003_v1_n3_01_scaffold_generate as sc
    src = os.path.join(base, "src"); out = os.path.join(base, "scaf_out")
    for lv in ("a2", "b1b"):
        os.makedirs(f"{src}/{lv}"); os.makedirs(f"{out}/{lv}")
        open(f"{src}/{lv}/article.md", "w", encoding="utf-8").write(
            "# Title\n\nFirst paragraph here. It is fine.\n\nSecond paragraph here. It is fine.\n\nThird paragraph here. It is fine.\n\n## In one line\nA short line.\n")
        json.dump({"comment_1": "x"}, open(f"{out}/{lv}/{'b1_support_texts.json' if lv == 'b1b' else 'a2_support_texts.json'}", "w"))
    seen = []
    hr_doc = {"items": [dict(ga_item(ORIGINALS[1], "based on interviews"), gloss_alignment_status=ga.STATUS_HR_REQUIRED)]}

    def fake_run(*, text=None, kp_dir=None, article_id=None, level=None, **kw):   # KP Human Review: X Productionは確認付きKP経路(run_kp_with_review)を通る
        article_text = text
        seen.append(dict(kw))
        os.makedirs(kp_dir, exist_ok=True)
        json.dump(hr_doc, open(f"{kp_dir}/keywords_canonicalized.json", "w", encoding="utf-8"), ensure_ascii=False)
        return {"selection": {"status": "KEY_WORDS_STRUCTURE_PASS", "kp_backend_used": "mock"},
                "canonicalization": {"status": "CANONICALIZATION_PASS", "gloss_alignment_status": "ALIGN_FAILED_HUMAN_REVIEW_REQUIRED",
                                     "gloss_alignment_metrics": {"targets": 1}}, "m2_fallback_events": [],
                "status": "NG_REVIEW_REQUIRED", "gloss_alignment_run_status": ga.STOPPED_STATUS,
                "gloss_alignment_human_review_events": [{"article": article_id, "level": level, "ranks": [2]}]}
    import er119_kp_wiring_01 as _kpw
    with mock.patch.object(_kpw, "run_kp_with_review", side_effect=fake_run), contextlib.redirect_stdout(io.StringIO()):
        res = x.run_theme_scaffold(None, src, out, ["a2"], scaffold_only="kp")
    summ = json.load(open(f"{out}/scaffold_run_summary.json", encoding="utf-8"))
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        line = x.print_gloss_hr_final_line(out)
    a2 = summ["a2"]
    record("T3(v)", "X scaffold: run_key_phrasesへmode引数を渡さず、summaryにevent+kp_run_status(NG_REVIEW_REQUIRED)と別キーgloss_alignment_run_status(STOPPED)+flag+metrics。最終専用stdout行はartifact基準",
           "gloss_alignment_mode" not in seen[0] and a2["gloss_alignment_human_review_events"][0]["ranks"] == [2]
           and a2["kp_run_status"] == "NG_REVIEW_REQUIRED" and a2["gloss_alignment_run_status"] == ga.STOPPED_STATUS
           and a2["gloss_alignment_flag"]["enabled"] is True and a2["gloss_alignment_metrics"] == {"targets": 1}
           and "[HUMAN-REVIEW-REQUIRED][FINAL]" in line and "gloss_alignment_mode" not in a2,
           {"kwargs": seen[0], "final_line": line[:140], "summary_keys": sorted(a2)})


# ---------------------------------------------------------------- Z patterns
def z_ctx(tmp, kp_calls, fail_levels=("B1",), align_enabled=True, declare=True):
    import er026_family_z_fiction_production_runner_01 as r
    ctx = r.build_mock_context(tmp)
    if declare:
        _declare_ctx(ctx)   # KP Human Review: 既存mock testのfixture(Human不在を明示宣言)
    else:
        import er119_kp_human_review_01 as _rv0
        _p0 = _rv0.declarations_path(ctx.out_dir)   # 既存mock testがimportでwrapしていても『宣言なし』から始める
        if os.path.exists(_p0):
            os.remove(_p0)

    def kp_fn(text, kp_dir, article_id, source_level, process=None, **kw):
        kp_calls.append(source_level)
        spans = [s for s in r._MOCK_KP_CANDIDATES if s in text][:5]
        assert len(spans) == 5, spans
        items = []
        for i, s in enumerate(spans, 1):
            disp = s
            if i == 2 and source_level.upper() in [x.upper() for x in fail_levels]:
                disp = " ".join(s.split()[:-1])     # 候補から末尾語を削ったdisplay_phrase -> KPが伸びた扱い
            items.append({"rank": i, "source_span": s, "source_sentence": s, "display_phrase": disp, "key_phrase": s,
                          "used_form": s, "japanese_gloss": f"意味{i}", "japanese_gloss_tts": f"意味{i}",
                          "kp_extends_beyond_candidate": disp != s, "gloss_review_hint": False,
                          "fulltext_source_ref": "fulltext_exact_v1"})   # 委任_14: Production KPは全て全文選定(Part 1の厳格入力が要求)
        merged = {"items": items, "overall_status": "CANONICALIZATION_PASS", "article_id": article_id,
                  "canonicalization_version": "mock", "source_level": source_level}
        fnl = FakeFn([bad(2), bad(2)])
        aligned = ga.align_glosses(merged, text, lambda msg: fnl, out_dir=kp_dir, article_id=article_id, enabled=align_enabled)
        os.makedirs(kp_dir, exist_ok=True)
        json.dump(aligned["merged"], open(f"{kp_dir}/keywords_canonicalized.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        return {"selection": {"status": "KEY_WORDS_STRUCTURE_PASS"},
                "canonicalization": {"status": "CANONICALIZATION_PASS", "merged": aligned["merged"]},
                "redundancy_qa": {"status": "REDUNDANCY_OK"}, "redundancy_retry_log": []}
    ctx.hooks["kp_fn"] = ctx.mock_api.wrap("kp", kp_fn)
    return r, ctx


def api_kinds(ctx):
    p = f"{ctx.out_dir}/mock_api_calls.jsonl"
    rows = [json.loads(x) for x in open(p, encoding="utf-8")] if os.path.exists(p) else []
    k = {}
    for row in rows:
        k[row["kind"].split(":")[0]] = k.get(row["kind"].split(":")[0], 0) + 1
    return k


def pat_z(base):
    """KP Human Review(2026-10-25)導入後のZ。gloss再整合が成立しない候補(HR待ち)は候補段階で旗付け=AUTO対象外・Human選択不可
    (`resolve-gloss`後に選択可)になり、確定物(assets)には入らない。旧: kp stageがHR itemを含むartifactで停止していた。
    守るべき不変条件(HR itemが後段に流れない・人間確定glossが使われる・選定を再実行しない・有料呼出なし)は同じ。"""
    import er119_kp_human_review_01 as rv
    tmp = os.path.join(base, "z"); os.makedirs(tmp)
    kp_calls: list = []
    r, ctx = z_ctx(tmp, kp_calls)
    with contextlib.redirect_stdout(io.StringIO()):
        r.run_stages(ctx, ["seed_check", "writer", "std_adjust", "plan", "support"])
    kinds0 = api_kinds(ctx)
    stop = None
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            r.run_stage(ctx, "kp")
        except r.FamilyZE2EStop as e:
            stop = str(e)
    odir = ctx.out_dir
    kd = f"{odir}/key_phrases/b1b"
    asset = f"{odir}/b1b/key_phrases/keywords_canonicalized.json"
    cands = rv.load_candidates(kd)
    hr_c = [c for c in cands["candidates"] if c["flags"]["gloss_hr_pending"]]
    inst = json.load(open(asset, encoding="utf-8"))
    kinds1 = api_kinds(ctx)
    new_kinds = {k: kinds1.get(k, 0) - kinds0.get(k, 0) for k in kinds1 if kinds1.get(k, 0) != kinds0.get(k, 0)}
    record("T3(j)", "Z stage_kp: gloss HR(rank=2)の候補は旗付き・AUTO対象外で確定物(assets)に入らず、HR itemが後段へ流れない(stageは通る)。有料呼出は候補生成のみ",
           stop is None and len(hr_c) == 1 and not hr_c[0]["auto_eligible"] and ga.collect_unresolved(inst) == []
           and hr_c[0]["candidate_id"] not in [i["candidate_id"] for i in inst["items"]] and new_kinds.get("kp") == 2
           and kp_calls == ["B1", "A2"],
           {"stop": stop, "hr_candidates": [c["candidate_id"] for c in hr_c], "api_kinds_during_kp_stage": new_kinds})
    # (m-Z) 別stage(tts_b1b)の共有入力(load_level_inputs)もHR itemを含まない。TTS API 0 call(入力検査のみ)
    kinds2 = api_kinds(ctx)
    with contextlib.redirect_stdout(io.StringIO()):
        li = r.load_level_inputs(ctx, "b1b")
    record("T3(m)", "tts段の共有入力load_level_inputs: HR itemは含まれず検査を通る。この検査でTTS API 0 call",
           li is not None and not any(k.startswith("tts") for k in api_kinds(ctx)) and api_kinds(ctx) == kinds2,
           {"api_kinds": api_kinds(ctx)})
    # (l-Z) 宣言なし(=Human確認待ち)で候補生成 -> 候補のgloss HRをresolve-gloss -> Humanが選定 -> 同じstageを再実行:
    # 選定を再実行しない(kp_fn計1回+a2初回のみ)、人間確定glossがassetsに入り(HUMAN_RESOLVED)、解説sigにglossを含む
    tmp_l = os.path.join(base, "z_l"); os.makedirs(tmp_l)
    kp_calls_l: list = []
    rl, ctxl = z_ctx(tmp_l, kp_calls_l, declare=False)
    with contextlib.redirect_stdout(io.StringIO()):
        rl.run_stages(ctxl, ["seed_check", "writer", "std_adjust", "plan", "support"])
        try:
            rl.run_stage(ctxl, "kp")
        except rl.FamilyZKpReviewPending:
            pass
    kdl = f"{ctxl.out_dir}/key_phrases/b1b"
    hr_l = [c for c in rv.load_candidates(kdl)["candidates"] if c["flags"]["gloss_hr_pending"]][0]
    rv.op_resolve_gloss(kdl, rank=hr_l["ai_rank"], gloss="人間が確定した意味", by="t3_mock")
    rv.op_select(kdl, kp_ranks=[1, 2, 3], vocab_ranks=[1, 2, 3, 4, 5], by="t3_mock")
    rv.op_select(f"{ctxl.out_dir}/key_phrases/a2", kp_ranks=[1, 2, 3], by="t3_mock")
    with contextlib.redirect_stdout(io.StringIO()):
        res_kp = rl.run_stage(ctxl, "kp")
    installed = json.load(open(f"{ctxl.out_dir}/b1b/key_phrases/keywords_canonicalized.json", encoding="utf-8"))
    _sorted_items = sorted(installed["items"], key=lambda x: x["rank"])
    import er019_family_x_kp_explanation_01 as _kexp_t   # 解説sigは実装どおりexplanation_phrase(=used_form)
    _sig_payload = {"display": [_kexp_t.explanation_phrase(it) for it in _sorted_items],
                    "gloss": [it.get("japanese_gloss", "") for it in _sorted_items]}
    if any(it.get("source_reference_contract") for it in _sorted_items):
        _sig_payload["src"] = [[it.get("source_sentence_id", ""), it.get("source_sentence", "")] for it in _sorted_items]
    sig_expected = rl._sha(json.dumps(_sig_payload, ensure_ascii=False))
    pv = rl._m().w62.rj(f"{ctxl.out_dir}/writer/provenance.json")
    expl_entry = (pv.get("downstream_stages") or {}).get("kp_expl_b1b") or {}
    hit = [i for i in installed["items"] if i["candidate_id"] == hr_l["candidate_id"]]
    record("T3(l-Z)", "Z: 候補のresolve-gloss+Human選定後に同stageを再実行 -> 選定は再実行されない(kp_fn計1回+a2初回のみ)、人間確定glossがassetsへ(HUMAN_RESOLVED)、解説sigにgloss含む",
           kp_calls_l == ["B1", "A2"] and len(hit) == 1 and hit[0]["japanese_gloss"] == "人間が確定した意味"
           and hit[0]["gloss_alignment_status"] == ga.STATUS_HUMAN_RESOLVED and expl_entry.get("input_sha256") == sig_expected,
           {"kp_fn_levels_called": kp_calls_l, "expl_sig_includes_gloss": expl_entry.get("input_sha256") == sig_expected,
            "stage_status": res_kp.get("b1b") if isinstance(res_kp, dict) else None})
    # (k-Z) 既定のZ mock kp stage(gloss再整合の対象0件)は従来どおり通る: 未評価検出は対象0件を通す(OF-KGCPW-08)
    tmp3 = os.path.join(base, "z_default"); os.makedirs(tmp3)
    r3 = __import__("er026_family_z_fiction_production_runner_01")
    ctx3 = r3.build_mock_context(tmp3)
    _declare_ctx(ctx3)   # KP Human Review: 既存mock testのfixture(Human不在を明示宣言)
    with contextlib.redirect_stdout(io.StringIO()):
        r3.run_stages(ctx3, ["seed_check", "writer", "std_adjust", "plan", "support", "kp"])
    record("T3(k-Z)", "Z 既定mock kp stage(対象0件): 無条件配線後も従来どおり通る(未評価検出は対象0件を通過)",
           os.path.exists(f"{ctx3.out_dir}/b1b/key_phrases/keywords_canonicalized.json"), {})

# ---------------------------------------------------------------- subprocess drivers (終了statusの非OK確認)
def driver_z(work):
    kp_calls = []
    r, ctx = z_ctx(work, kp_calls, declare=False)   # KP Human Review: 宣言なし=確認待ち(FamilyZKpReviewPending=FamilyZE2EStop)で非0終了
    r.run_stages(ctx, ["seed_check", "writer", "std_adjust", "plan", "support", "kp"])   # kpで例外->rc!=0


def driver_x(work):
    import er019_family_x_audio_production_runner_01 as x
    lvl, kp_dir, res, fn, out = make_level_with_hr(work, "drv")
    print(out.strip())     # run_key_phrasesが出した専用stdout行(run_kp内でcaptureされているので実stdoutへ再出力して確認可能にする)
    kp = load_kp(kp_dir)
    narr = f"{lvl}/narration"; os.makedirs(narr, exist_ok=True)
    with x_stubs(x):
        results = x._generate_key_phrase_segments_a2(kp, narr, None)
    os.makedirs(f"{lvl}/audit", exist_ok=True)
    json.dump({"segments": {}, "key_phrases": results}, open(f"{lvl}/audit/tts_generation_results.json", "w", encoding="utf-8"))
    import er003_v1_n3_01_assemble as asm
    asm.verify_episode_audio_validation_gate(lvl, "A2")     # EPISODE_BLOCKED_BY_AUDIO_VALIDATION -> rc!=0
    print("UNREACHABLE: gate did not block")


def pat_exit_status(base):
    outs = {}
    for name in ("z", "x"):
        work = os.path.join(base, f"drv_{name}"); os.makedirs(work)
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "--driver", name, "--work", work],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=REPO,
                           env={**os.environ, "TTS_EXECUTION_MODE": "STANDARD", "PYTHONUTF8": "1"})
        outs[name] = {"rc": p.returncode, "stdout_has_line": "[GLOSS-ALIGN][HUMAN-REVIEW-REQUIRED]" in p.stdout,
                      "stderr_tail": p.stderr.strip().splitlines()[-1][:200] if p.stderr.strip() else "",
                      "unreachable": "UNREACHABLE" in p.stdout}
    record("T3(exit)", "別プロセス実行: Z=FamilyZE2EStopで非0終了、X=Gate拒否で非0終了。最終stdoutに専用行(「届いた」条件③)",
           outs["z"]["rc"] != 0 and "KP_REVIEW_PENDING" in outs["z"]["stderr_tail"]
           and outs["x"]["rc"] != 0 and outs["x"]["stdout_has_line"] and "EPISODE_BLOCKED_BY_AUDIO_VALIDATION" in outs["x"]["stderr_tail"]
           and not outs["x"]["unreachable"], outs)


# ---------------------------------------------------------------- main
@contextlib.contextmanager
def forbid_real_apis():
    def boom(name):
        def f(*a, **k):
            API_ATTEMPTS["n"] += 1
            raise AssertionError(f"REAL API PATH CALLED: {name}")
        return f
    import openai
    with mock.patch.object(openai, "OpenAI", side_effect=boom("openai.OpenAI")), \
            mock.patch.object(ga, "make_alignment_fn", side_effect=boom("ga.make_alignment_fn")), \
            mock.patch("er003_v1_en_direct_vfl_01_generate.get_client", side_effect=boom("get_client")):
        yield


def run_all_scenarios():
    """全シナリオを1回実行しRESULTSを返す(forbid_real_apisの下。共有state前後比較・API 0もここで記録)。"""
    RESULTS.clear()
    API_ATTEMPTS["n"] = 0
    import er019_family_x_audio_production_runner_01 as x
    before = snapshot_monitored()
    base = tempfile.mkdtemp(prefix="kgcpw_stop_paths_")
    try:
        with forbid_real_apis():
            pat_a_to_e(base)
            pat_f_g(base)
            pat_h(base)
            lvl, kp_dir, kp = pat_i_o_p_q(base, x)
            pat_k_t(base, x, lvl, kp_dir, kp)
            pat_n_outer_retry(base)
            pat_scaffold_passthrough(base, x)
            pat_z(base)
            pat_exit_status(base)
        after = snapshot_monitored()
        record("T3(r)", "attempt_history.jsonl/human_review_queue.jsonl/Master Store/telemetry/cost_summaryを汚染しない(全パターン実行前後でsha同一)",
               before == after, {"unchanged": before == after, "files": list(before)})
        record("T3(api0)", "全パターンで実API呼出0(OpenAI/alignment/get_client禁止patchへの到達0)", API_ATTEMPTS["n"] == 0,
               {"forbidden_path_attempts": API_ATTEMPTS["n"], "real_tts_calls": 0, "stub_calls_total": dict(STUB_CALLS)})
    finally:
        shutil.rmtree(base, ignore_errors=True)
    return list(RESULTS)


EXPECTED_IDS = ["T3(a)", "T3(b)", "T3(c)", "T3(d)", "T3(e)", "T3(f)", "T3(g)", "T3(h)", "T3(i-A2)", "T3(p)", "T3(o)", "T3(q)",
                "T3(k-X)", "T3(l-X)", "T3(t-X)", "T3(n)", "T3(n2)", "T3(v)", "T3(j)", "T3(m)", "T3(l-Z)", "T3(k-Z)",
                "T3(exit)", "T3(r)", "T3(api0)"]


class T3StopPaths(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._old = (ga.GLOSS_ALIGNMENT_ENABLED, os.environ.get("TTS_EXECUTION_MODE"))
        ga.GLOSS_ALIGNMENT_ENABLED = True
        os.environ["TTS_EXECUTION_MODE"] = "STANDARD"     # 本testは実TTSを実行しない(mock)。T-2に従い明示する
        cls.results = run_all_scenarios()

    @classmethod
    def tearDownClass(cls):
        ga.GLOSS_ALIGNMENT_ENABLED = cls._old[0]
        if cls._old[1] is None:
            os.environ.pop("TTS_EXECUTION_MODE", None)
        else:
            os.environ["TTS_EXECUTION_MODE"] = cls._old[1]

    def test_all_expected_scenarios_present(self):
        self.assertEqual(sorted(r["id"] for r in self.results), sorted(EXPECTED_IDS))

    def test_each_scenario_passes(self):
        for r_ in self.results:
            with self.subTest(r_["id"]):
                self.assertTrue(r_["pass"], f"{r_['id']}: {r_['title']} evidence={r_['evidence']}")

    def test_no_real_api_attempted(self):
        self.assertEqual(API_ATTEMPTS["n"], 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--driver", default=None)
    ap.add_argument("--work", default=None)
    a, rest = ap.parse_known_args()
    if a.driver:
        os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
        with forbid_real_apis():
            {"z": driver_z, "x": driver_x}[a.driver](a.work)
        return 0
    unittest.main(argv=[sys.argv[0]] + rest)
    return 0


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""KGCPW harness(委任_02で準備、実行=委任_03): Production正式runner関数をin-processで駆動し、gloss再整合の失敗注入・
合成対象artifact生成を行う。Production差分0(本ファイルはevidence配下の新規ファイル。Productionコードへフック/環境変数を足さない)。

方式B'(Opus M5 / OF-KGCPW-12): `ga.make_alignment_fn`をwrapし、**本物の`make_alignment_fn`をfake `client=`付きで呼ぶ**。
モデル照合(response.model==model)・usage・JSON解析・item単位retry・HR永続化まで本物を通り、他のOpenAI呼出は横取りしない
(selection/canonicalization/redundancyはsynthetic録画固定=下記SYNTH_*。TTSは呼ばない)。
provenance: synthetic(入力・失敗注入) + production_formal_path(X: sc.run_key_phrases/x.run_theme_scaffold、Z: w62.ensure_stage/r.stage_kp)。
**「fresh初回path」とは主張しない**。E4で作った合成対象artifactは `--synth-target` で同run dirへ書き出し、続きは正式runner CLI
(`--stage tts --only-segments` -> `--stage assemble` -> `--stage player`)で行う(E4->E7連結。委任_03のcommand計画参照)。

固定item集合(Std/Adv共通、OF-KGCPW-15): rank2=P1型(KP『based on interviews』/gloss『～をもとにした』=不整合)、rank4=P2型
(KP『give up easily』/gloss『簡単にあきらめる』=整合済みの対照)、他3件は対象外(KPが候補と同一)。全て同一call。

使い方:
  --self-test                         API 0。X(a2/b1b)・Z(a2/b1b)で2回失敗->HR->関所停止(TTS 0)を確認
  --scenario x_a2|x_b1b|z_a2|z_b1b --align-mode fail2|real --out-dir DIR [--source-dir DIR] [--allow-paid --managed-id ID]
  --synth-target --level a2|b1b --out-dir <run dir> [--source-dir DIR] --align-mode real --allow-paid
     合成対象artifactを`<out-dir>/<level>/key_phrases/`へ生成(X)。続きは同run dirで正式runner CLI。
real(実LLM)は --allow-paid が必須で、起動前に tools/stop_scope_check_01.py(STOP確認)を実行し stop=true なら実行しない。
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest.mock as mock
from types import SimpleNamespace

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *([".."] * 4)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
os.environ.setdefault("TTS_EXECUTION_MODE", "STANDARD")      # T-2: 本harnessはTTSを呼ばないが明示する

import er003_key_words_canonicalization as kc  # noqa: E402
import er003_key_words_gloss_alignment as ga  # noqa: E402
import er003_v1_n3_01_scaffold_generate as sc  # noqa: E402

# ------------------------------------------------------------ synthetic fixtures(録画固定)
SYNTH_ORIGINALS = [
    {"rank": 1, "display_phrase": "right away", "source_span": "right away", "source_sentence": "Do it right away.",
     "ja_gloss": "すぐに", "source_reference_contract": "X"},
    {"rank": 2, "display_phrase": "based on", "source_span": "based on",
     "source_sentence": "It is an estimate based on interviews with sellers.", "ja_gloss": "～をもとにした",
     "source_reference_contract": "X"},
    {"rank": 3, "display_phrase": "take part", "source_span": "take part", "source_sentence": "Many people take part.",
     "ja_gloss": "参加する", "source_reference_contract": "X"},
    {"rank": 4, "display_phrase": "give up", "source_span": "give up", "source_sentence": "They did not give up easily.",
     "ja_gloss": "簡単にあきらめる", "source_reference_contract": "X"},
    {"rank": 5, "display_phrase": "point to", "source_span": "point to", "source_sentence": "Studies point to a rise.",
     "ja_gloss": "～を示す", "source_reference_contract": "X"},
]
_QA = {f: "PASS" for f in kc.QA_FIELDS}


def synth_canon_parsed():
    def it(rank, kp, disp):
        return {"rank": rank, "key_phrase": kp, "changed_from_display_phrase": kp != disp,
                "normalization_reason": "restore_semantic_complement" if kp != disp else "none", "reasoning": "synthetic", **_QA}
    return {"items": [it(1, "right away", "right away"), it(2, "based on interviews", "based on"),
                      it(3, "take part", "take part"), it(4, "give up easily", "give up"), it(5, "point to", "point to")]}


SYNTH_ARTICLE = ("# Title\n\nFirst paragraph here. It is an estimate based on interviews with sellers. Do it right away.\n\n"
                 "Second paragraph here. Many people take part. They did not give up easily.\n\n"
                 "Third paragraph here. Studies point to a rise.\n\n## In one line\nA short line.\n")


class FailClient:
    """OpenAI client境界のfake(本物のmake_alignment_fnにclient=で渡す)。attempt毎に不正応答を返す: 1回目=不正JSON、2回目以降=qa FAIL。
    response.modelは要求modelと一致させる(モデル照合は通し、検証失敗を『内容』で起こす)。"""
    def __init__(self):
        self.calls = 0
        outer = self

        class _Responses:
            def create(self, **kw):
                outer.calls += 1
                if outer.calls == 1:
                    text = "not json"
                else:
                    # rank2(P1型)だけqa FAILを注入。rank4(P2型=整合済みの対照)は正しく『真なら不変』で返す(item単位の独立性)。
                    text = json.dumps({"items": [
                        {"rank": 2, "current_gloss_consistent": False, "japanese_gloss": "x",
                         "added_word_mappings": [], "qa_reflects_all_key_phrase_words": "FAIL", "reasoning": "injected"},
                        {"rank": 4, "current_gloss_consistent": True, "japanese_gloss": "簡単にあきらめる",
                         "added_word_mappings": [{"english_word": "easily", "japanese_span": "簡単に"}],
                         "qa_reflects_all_key_phrase_words": "PASS", "reasoning": "control"}]}, ensure_ascii=False)
                u = SimpleNamespace(input_tokens=1, output_tokens=1, input_tokens_details=SimpleNamespace(cached_tokens=0))
                return SimpleNamespace(model=kw["model"], output_text=text, id=f"resp_inject_{outer.calls}", usage=u)
        self.responses = _Responses()


def wrapped_make_alignment_fn(align_mode):
    """B': 本物のga.make_alignment_fn(のオリジナル)を、fake client付きで呼ぶwrapper。realはclient=None(=本物のOpenAI)。"""
    real = ga.make_alignment_fn
    holder = {"client": FailClient() if align_mode == "fail2" else None}

    def _wrapped(user_message, client=None, **kw):
        return real(user_message, client=holder["client"] if holder["client"] is not None else client, **kw)
    _wrapped.holder = holder
    return _wrapped


@contextlib.contextmanager
def sc_boundaries(align_mode):
    """selection/canonicalization/redundancyをsynthetic録画へ固定し、alignmentだけB'で本物を通す。"""
    sel = {"status": "KEY_WORDS_STRUCTURE_PASS", "original_items": [dict(x) for x in SYNTH_ORIGINALS], "cost_jpy": 0.0,
           "kp_backend_used": "synthetic"}
    w = wrapped_make_alignment_fn(align_mode)
    with mock.patch.object(sc, "run_key_phrase_selection", return_value=sel), \
            mock.patch.object(sc.kc, "run_canonicalization_gate",
                              return_value=(synth_canon_parsed(), "CANONICALIZATION_PASS", [], "synthetic", "resp")), \
            mock.patch.object(sc, "run_key_phrase_redundancy_qa", return_value={"status": "REDUNDANCY_OK", "duplicate_pairs": []}), \
            mock.patch.object(sc.gloss_align, "make_alignment_fn", side_effect=w):
        yield w


# ------------------------------------------------------------ X
def prepare_x_source(base, level, source_dir=None):
    """X run_theme_scaffoldの入力(source_dir/<level>/article.md + out_dir/<level>/<support>.json)を用意する。"""
    src, out = os.path.join(base, "src"), os.path.join(base, "out")
    os.makedirs(f"{src}/{level}", exist_ok=True)
    os.makedirs(f"{out}/{level}", exist_ok=True)
    art = SYNTH_ARTICLE
    if source_dir and os.path.exists(f"{source_dir}/{level}/article.md"):
        art = open(f"{source_dir}/{level}/article.md", encoding="utf-8").read()
    open(f"{src}/{level}/article.md", "w", encoding="utf-8").write(art)
    json.dump({"comment_1": "x"}, open(f"{out}/{level}/{'b1_support_texts.json' if level == 'b1b' else 'a2_support_texts.json'}", "w"))
    return src, out


def run_x(level, align_mode, base, source_dir=None, announce=True):
    import er019_family_x_audio_production_runner_01 as x
    src, out = prepare_x_source(base, level, source_dir)
    if announce:
        ga.announce_flag()
    t0 = time.time()
    os.makedirs(f"{out}/{level}/key_phrases", exist_ok=True)   # 本物のselectionはkp_dirを作る。synthetic固定では代わりに作る
    with sc_boundaries(align_mode) as w:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            res = x.run_theme_scaffold(None, src, out, [level], scaffold_only="kp")
    summ = json.load(open(f"{out}/scaffold_run_summary.json", encoding="utf-8"))[level]
    kp = json.load(open(f"{out}/{level}/key_phrases/keywords_canonicalized.json", encoding="utf-8"))
    return {"scenario": f"x_{level}", "align_mode": align_mode, "elapsed_sec": round(time.time() - t0, 2),
            "summary": {k: summ.get(k) for k in ("key_phrases_status", "kp_run_status", "gloss_alignment_run_status",
                                                  "gloss_alignment_status", "gloss_alignment_flag", "gloss_alignment_metrics")},
            "events": summ.get("gloss_alignment_human_review_events"),
            "unresolved_ranks": [i["rank"] for i in ga.collect_unresolved(kp)],
            "control_item_rank4_gloss": next(i["japanese_gloss"] for i in kp["items"] if i["rank"] == 4),
            "rank2_gloss": next(i["japanese_gloss"] for i in kp["items"] if i["rank"] == 2),
            "stdout_hr_line": [ln for ln in buf.getvalue().splitlines() if "[GLOSS-ALIGN][HUMAN-REVIEW-REQUIRED]" in ln][:1],
            "api_calls_by_fake_client": getattr(w.holder.get("client"), "calls", None), "out_dir": out}


def x_downstream_checks(level, out):
    """HR後の下流: KP segment TTS 0 call・B1解説LLM 0 call・assemble拒否・最終行(TTSは実行しない=stubで0 callを数える)。"""
    import er019_family_x_audio_production_runner_01 as x
    kp = json.load(open(f"{out}/{level}/key_phrases/keywords_canonicalized.json", encoding="utf-8"))
    counts = {"tts": 0, "expl_llm": 0}

    def tts_stub(*a, **k):
        counts["tts"] += 1
        return {"status": "OK"}

    def expl_stub(items, **k):
        counts["expl_llm"] += 1
        return {"items": {}}
    narr = f"{out}/{level}/narration"
    os.makedirs(narr, exist_ok=True)
    with mock.patch.object(x.shared_narration, "ensure_key_phrase_english_component", side_effect=tts_stub), \
            mock.patch.object(x.n3_tts, "generate_a2_japanese_with_reading_safety", side_effect=tts_stub), \
            mock.patch.object(x.kp_explanation_gen, "generate_kp_explanations", side_effect=expl_stub), \
            mock.patch.object(x, "generate_key_phrase_explanation_en_verified", side_effect=tts_stub), \
            contextlib.redirect_stdout(io.StringIO()):
        if level == "b1b":
            results, _ = x._generate_key_phrase_segments_b1(kp, narr, None)
        else:
            results = x._generate_key_phrase_segments_a2(kp, narr, None)
    stopped = {st["status"] for d in results.values() for st in d.values()}
    try:
        x._assert_no_gloss_alignment_hr(f"{out}/{level}", "B1" if level == "b1b" else "A2")
        assemble_blocked = False
    except RuntimeError as e:
        assemble_blocked = "EPISODE_BLOCKED_BY_GLOSS_ALIGNMENT" in str(e)
    with contextlib.redirect_stdout(io.StringIO()):
        final_line = x.print_gloss_hr_final_line(out, [level])
    return {"downstream_calls": counts, "segment_statuses": sorted(stopped), "assemble_blocked": assemble_blocked,
            "final_line": final_line[:160]}


# ------------------------------------------------------------ Z
def run_z(level, align_mode, base):
    """Z: mock context(TTS等はmock=API 0)。kp_fn hookでselection/canonicalizationを録画固定し、alignはga.align_glosses+B'(本物
    make_alignment_fn+fake client)。stage_kp(正式stage関数)でFamilyZE2EStop・HR報告・assets配備・TTS段の拒否を確認する。"""
    import er026_family_z_fiction_production_runner_01 as r
    ctx = r.build_mock_context(base)
    calls = []

    def kp_fn(text, kp_dir, article_id, source_level, process=None, **kw):
        calls.append(source_level)
        spans = [s for s in r._MOCK_KP_CANDIDATES if s in text][:5]
        items = []
        for i, s in enumerate(spans, 1):
            disp = " ".join(s.split()[:-1]) if (i == 2 and source_level.upper() == {"a2": "A2", "b1b": "B1"}[level]) else s
            items.append({"rank": i, "source_span": s, "source_sentence": s, "display_phrase": disp, "key_phrase": s,
                          "used_form": s, "japanese_gloss": f"意味{i}", "japanese_gloss_tts": f"意味{i}",
                          "kp_extends_beyond_candidate": disp != s, "gloss_review_hint": False})
        merged = {"items": items, "overall_status": "CANONICALIZATION_PASS", "article_id": article_id,
                  "canonicalization_version": "synthetic", "source_level": source_level}
        w = wrapped_make_alignment_fn(align_mode)
        aligned = ga.align_glosses(merged, text, lambda msg: w(msg, model="synthetic-model"), out_dir=kp_dir,
                                   article_id=article_id, enabled=True)
        os.makedirs(kp_dir, exist_ok=True)
        json.dump(aligned["merged"], open(f"{kp_dir}/keywords_canonicalized.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        return {"selection": {"status": "KEY_WORDS_STRUCTURE_PASS"},
                "canonicalization": {"status": "CANONICALIZATION_PASS", "merged": aligned["merged"]},
                "redundancy_qa": {"status": "REDUNDANCY_OK"}, "redundancy_retry_log": []}
    ctx.hooks["kp_fn"] = ctx.mock_api.wrap("kp", kp_fn)
    t0 = time.time()
    with contextlib.redirect_stdout(io.StringIO()):
        r.run_stages(ctx, ["seed_check", "writer", "std_adjust", "plan", "support"])
    stop, tts_stop = None, None
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        try:
            r.run_stage(ctx, "kp")
        except r.FamilyZE2EStop as e:
            stop = str(e)
        lv = "b1b" if level == "b1b" else "a2"
        try:
            r.run_stage(ctx, f"tts_{lv}")
        except Exception as e:  # noqa: BLE001
            tts_stop = f"{type(e).__name__}: {str(e)[:140]}"
    return {"scenario": f"z_{level}", "align_mode": align_mode, "elapsed_sec": round(time.time() - t0, 2),
            "stage_kp_stop": (stop or "")[:200], "tts_after_stop": tts_stop, "kp_fn_levels": calls,
            "hr_report_exists": os.path.exists(f"{ctx.out_dir}/key_phrases/{'b1b' if level == 'b1b' else 'a2'}/{ga.HR_REPORT_JSON}"),
            "events": json.load(open(f"{ctx.out_dir}/gloss_alignment_human_review_events.json", encoding="utf-8"))
            if os.path.exists(f"{ctx.out_dir}/gloss_alignment_human_review_events.json") else None,
            "out_dir": ctx.out_dir}


# ------------------------------------------------------------ driver
def stop_check(managed_id, run_dir):
    p = subprocess.run([sys.executable, "tools/stop_scope_check_01.py", "--managed-id", managed_id, "--run-dir", run_dir],
                       capture_output=True, text=True, cwd=ROOT)
    return p.returncode == 0 and '"stop": false' in p.stdout


def self_test():
    results, ok = [], True
    with tempfile.TemporaryDirectory() as tmp:
        for level in ("a2", "b1b"):
            r = run_x(level, "fail2", os.path.join(tmp, f"x_{level}"), announce=False)
            d = x_downstream_checks(level, r["out_dir"])
            good = (r["unresolved_ranks"] == [2] and r["summary"]["gloss_alignment_run_status"] == ga.STOPPED_STATUS
                    and r["control_item_rank4_gloss"] == "簡単にあきらめる" and r["api_calls_by_fake_client"] == 2
                    and d["downstream_calls"] == {"tts": 0, "expl_llm": 0} and d["segment_statuses"] == [ga.STOPPED_STATUS]
                    and d["assemble_blocked"] and "[HUMAN-REVIEW-REQUIRED][FINAL]" in d["final_line"]
                    and r["summary"]["gloss_alignment_flag"]["enabled"])
            results.append({**r, "downstream": d, "pass": good})
            ok &= good
        for level in ("a2", "b1b"):
            z = run_z(level, "fail2", os.path.join(tmp, f"z_{level}"))
            good = (("HUMAN_REVIEW_REQUIRED(" in z["stage_kp_stop"]) and z["hr_report_exists"] and bool(z["tts_after_stop"])
                    and "HUMAN_REVIEW_REQUIRED" in z["tts_after_stop"] and bool(z["events"]))
            results.append({**z, "pass": good})
            ok &= good
    print(json.dumps({"self_test": "PASS" if ok else "FAIL", "api_calls": 0, "tts_calls": 0, "results": results},
                     ensure_ascii=False, indent=1, default=str))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--scenario", choices=("x_a2", "x_b1b", "z_a2", "z_b1b"))
    ap.add_argument("--align-mode", choices=("fail2", "real"), default="fail2")
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--source-dir", default=None)
    ap.add_argument("--synth-target", action="store_true")
    ap.add_argument("--level", choices=("a2", "b1b"), default="a2")
    ap.add_argument("--allow-paid", action="store_true")
    ap.add_argument("--managed-id", default="KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.align_mode == "real":
        if not a.allow_paid:
            print("real(実LLM)は --allow-paid が必須(委任文で明示許可された回数のみ)")
            return 2
        if not stop_check(a.managed_id, a.out_dir or "."):
            print("STOP確認でstop=true/不明: 新規API呼出をしません")
            return 3
    base = a.out_dir or tempfile.mkdtemp(prefix="kgcpw_harness_")
    if a.synth_target:
        src, out = prepare_x_source(base, a.level, a.source_dir)
        res = run_x(a.level, a.align_mode, base, a.source_dir)
        print(json.dumps(res, ensure_ascii=False, indent=1, default=str))
        return 0
    if not a.scenario:
        print("--scenario / --synth-target / --self-test のいずれかが必要")
        return 2
    kind, level = a.scenario.split("_", 1)
    res = run_x(level, a.align_mode, base, a.source_dir) if kind == "x" else run_z(level, a.align_mode, base)
    if kind == "x" and a.align_mode == "fail2":
        res["downstream"] = x_downstream_checks(level, res["out_dir"])
    print(json.dumps(res, ensure_ascii=False, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())

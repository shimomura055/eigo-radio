# -*- coding: utf-8 -*-
"""er110_family_y_persona_pipeline_01_run.py -- Family Y 6段階パイプライン(委任_14 Phase B)の薄い入口(DEV/Trial専用)。

1 processで1つの (theme, run_id) を実行する。監督ループ・自動再試行ラッパは持たない。既存artifactがあれば再利用(二重課金防止)。
  py er110_family_y_persona_pipeline_01_run.py --theme school_phone_ban|office_seating --run-id main|repro [--text-only] [--cap N]
出力: er110_output/family_y_persona_pipeline_01/<theme>/<run_id>/ (X/Z・既存er110 dirには書かない)
STOP時: run_status.json に code/message を書き rc=4 で終了(再実行はFable/ユーザー判断)。
"""
import argparse
import glob
import hashlib
import json
import os
import sys
import time

import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_advanced_adaptation_generate as adv_gen
import er003_v1_n3_01_standard_a2_generate as std_gen
import er005_cost_logger as cl
import er012_e_family_entertainment_two_level_runner_01 as efam
import er053_family_x_factlock_ja_writer_01 as w1
import er110_family_y_text_trial_01 as y0
import er110_family_y_persona_text_trial_01 as p
import er110_family_y_persona_pipeline_01 as pl

TREE = "er110_output/family_y_persona_pipeline_01"

THEMES = {
    "school_phone_ban": {
        "topic_ja": "日本の高校で、スマートフォンの校内での使用をどこまで制限するか(学校へのスマートフォン持ち込み・使用制限をめぐる日本と各国の動き)",
        "ledger_path": "er110_output/family_y_persona_trial_01/school_phone_ban/research_ledger/verified_fact_ledger.txt",
        "ledger_fn": pl.school_ledger_facts,
        # 主要当事者リスト(Fable事前固定。委任_14 §3。S2には見せない)
        "primary_parties": ["高校生本人(全日制)", "高校生本人(定時制・働きながら)", "保護者(父または母)", "担任教師", "生徒指導担当", "養護教諭またはスクールカウンセラー",
                            "管理職(校長・教頭)", "定時制生徒のアルバイト先の雇用主", "PTA・保護者会"],
    },
    "office_seating": {
        "topic_ja": "日本の会社で、座席を固定席にするか、フリーアドレス(席を決めない)にするか",
        "ledger_path": "er012_output/editorial_b_voices_trial_06/research/verified_fact_ledger.txt",
        "ledger_fn": pl.office_ledger_facts,
        "primary_parties": ["集中作業が多い一般社員", "対面の雑談・相談を重視する一般社員", "チームを預かる管理職", "総務・ファシリティ担当(コスト・座席率)",
                            "新入社員・若手(居場所・相談相手)", "時短勤務・育児中の社員", "外回りが多い営業", "経営層(オフィス費用・方針)"],
    },
}
TREE_CAP_JPY = 245.0       # 委任_14+15合算上限(Fable判断2026-10-24。予算ガード定数のみ変更、Prompt/閾値/選定ロジック無変更)
# 注: これは委任_14+15のrun(tree)単位の歯止めであり『Family Y累計上限』ではない(Y累計上限は2026-10-24撤廃、日次1,000円で一元管理。PM_GOVERNANCE 7-9)。


def tree_cost() -> float:
    import er053_cost_aggregate_01 as ca
    return round(sum(ca.compute_stage_cost_breakdown_multi(f)["total_jpy"] for f in glob.glob(f"{TREE}/**/raw_usage_log*.jsonl", recursive=True)), 3)


def run_cost(rd: str) -> float:
    import er053_cost_aggregate_01 as ca
    return round(sum(ca.compute_stage_cost_breakdown_multi(f)["total_jpy"] for f in glob.glob(f"{rd}/raw_usage_log*.jsonl")), 3)


class Timer:
    def __init__(self):
        self.t0 = time.time()
        self.rec = {}

    def mark(self, name, since):
        self.rec[name] = round(time.time() - since, 1)


def guard(rd: str, note: str):
    c = tree_cost()
    if c > TREE_CAP_JPY:
        raise pl.PipelineStop("BUDGET_GUARD", f"tree cost {c} JPY > cap {TREE_CAP_JPY} JPY ({note})")
    print(f"[PIPELINE] {os.path.basename(os.path.dirname(rd))}/{os.path.basename(rd)} run={run_cost(rd)} tree={c} JPY ({note})", flush=True)


def stage(rd, name, fn, timer):
    """artifactがあれば再利用、なければ実行。"""
    path = f"{rd}/{name}.json"
    if os.path.exists(path):
        print(f"[PIPELINE] reuse {name}", flush=True)
        return json.load(open(path, encoding="utf-8"))
    t = time.time()
    out = fn()
    w1.wj(path, out)
    timer.mark(name, t)
    guard(rd, f"after {name}")
    return out


def cmd_run(a):
    th = THEMES[a.theme]
    rd = f"{TREE}/{a.theme}/{a.run_id}"
    os.makedirs(rd, exist_ok=True)
    cl.install(f"{rd}/raw_usage_log.jsonl")
    client = vfl01.get_client()
    ctx = pl.Ctx(client, rd, a.run_id)
    timer = Timer()
    raw_ledger = open(th["ledger_path"], encoding="utf-8").read()
    facts = th["ledger_fn"](raw_ledger)
    w1.wj(f"{rd}/entry_point.json", {"runner": "er110_family_y_persona_pipeline_01_run.py", "management_id": pl.MANAGEMENT_ID, "theme": a.theme, "run_id": a.run_id,
                                      "started": pl.now_iso(), "writer_model": pl.MODEL_TOP, "judge_model": pl.MODEL_CHEAP, "text_only": a.text_only,
                                      "module_sha256": hashlib.sha256(open("er110_family_y_persona_pipeline_01.py", "rb").read()).hexdigest(),
                                      "primary_parties_fixed_by_fable": th["primary_parties"], "tree_cap_jpy": TREE_CAP_JPY})
    # ---- S1 ----
    ledger_ids = {l.split(":")[0] for l in facts.split("\n") if ":" in l}
    if a.theme == "school_phone_ban":
        if a.run_id == "main":
            s1 = stage(rd, "s1_llm", lambda: (lambda r: {**r, "comparison_to_approved": pl.compare_s1_to_approved(r["world_frame"], pl.SCHOOL_WORLD_FRAME_APPROVED)})
                       (pl.stage_s1(ctx, th["topic_ja"], facts, ledger_ids)), timer)
        wf = pl.SCHOOL_WORLD_FRAME_APPROVED
        w1.wj(f"{rd}/world_frame_used.json", {"source": "WORLD_SETTING_01.md承認済み設定(OF-Y5-09)", "world_frame": wf})
    else:
        main_wf = f"{TREE}/{a.theme}/main/s1_llm.json"
        if a.run_id != "main" and os.path.exists(main_wf):
            wf = json.load(open(main_wf, encoding="utf-8"))["world_frame"]       # 再現run: 同一S1入力(出力)を使う
        else:
            s1 = stage(rd, "s1_llm", lambda: pl.stage_s1(ctx, th["topic_ja"], facts, ledger_ids), timer)
            wf = s1["world_frame"]
        w1.wj(f"{rd}/world_frame_used.json", {"source": "S1 LLM出力", "world_frame": wf})
    # ---- S2 ----
    s2 = stage(rd, "s2_stakeholders", lambda: pl.stage_s2(ctx, wf), timer)
    cov = stage(rd, "s2_coverage", lambda: pl.stage_coverage(ctx, th["primary_parties"], s2["stakeholders"]), timer)
    print(f"[PIPELINE] S2 stakeholders={len(s2['stakeholders'])} 主要当事者網羅 {cov['n_covered']}/{cov['n_listed']}", flush=True)
    if a.stop_after == "s2":      # 予算上限のため再現runを段階的に実行する場合のみ(委任_14 予算警告)。既存artifactは後続の再開で再利用される
        finish(rd, a, ctx, timer, "STOPPED_AFTER_S2")
        return
    # ---- S3 ----
    s3 = stage(rd, "s3_claims", lambda: pl.stage_s3(ctx, wf, s2["stakeholders"]), timer)
    # ---- S4 ----
    s4 = stage(rd, "s4_trios", lambda: pl.stage_s4(ctx, wf, s2["stakeholders"], s3["claims"]), timer)
    # ---- S5 ----
    try:
        s5 = stage(rd, "s5_personas", lambda: pl.stage_s5(ctx, wf, s2["stakeholders"], s3["claims"], s4), timer)
    except pl.PipelineStop as e:
        if e.code == "REWORK_LIMIT_EXCEEDED":
            raise
        raise
    sh_by = {x["id"]: x for x in s2["stakeholders"]}
    # ---- S6 ----
    s6 = stage(rd, "s6_voices", lambda: pl.stage_voices(ctx, wf, s5, sh_by, rd), timer)
    if s6["gate_status"] != "PASS":
        raise pl.PipelineStop("VOICES_GATE_" + s6["gate_status"], "Voice Leakage Gateが通過しない")
    voices = s6["final_voices"]
    if a.text_only:
        finish(rd, a, ctx, timer, "TEXT_ONLY_DONE")
        return
    tension = stage(rd, "tension", lambda: pl.stage_tension(ctx, wf, voices, rd), timer)
    if tension["gate_status"] != "PASS":
        raise pl.PipelineStop("TENSION_GATE_" + tension["gate_status"], "Tension Leakage Gateが通過しない")
    paras = [voices[s] for s in pl.SLOTS] + [tension["final_tension"]]
    ja = p.render_article(wf["title_ja"], paras)
    w1.wt(f"{rd}/article_ja.md", ja)
    stage_english(rd, a, ctx, wf, facts, ja, s5, timer)
    finish(rd, a, ctx, timer, "FULL_DONE")


def stage_english(rd, a, ctx, wf, facts, ja, s5, timer):
    """忠実英訳(Adv)->In One Line->Std簡易化。契約検査(4パート)は既存p.check_en_contractを再利用。Std英語でE1(主張抽出)を記録(OF-Y5-02)。"""
    ed = f"{rd}/english"
    if os.path.exists(f"{ed}/en_summary.json"):
        print("[PIPELINE] reuse english", flush=True)
        return
    t = time.time()
    client = ctx.client
    mf = pl.y_contrast_must_fix_pl()
    r = adv_gen.generate_family_x_faithful_translation(ja, client=client, must_fix=mf)
    iol = efam._advanced_in_one_line(client, r.title, r.body, ja, facts)
    adv = f"# {r.title}\n\n{r.body}\n\n## In one line\n{iol['text']}"
    c = p.check_en_contract(adv)
    retried = False
    if not c["ok"] and any("PARAGRAPH_COUNT" in v for v in c["violations"]):
        retried = True
        r = adv_gen.generate_family_x_faithful_translation(ja, client=client, must_fix=mf + efam._FAMILY_X_PARAGRAPH_RETRY_MUST_FIX)
        iol = efam._advanced_in_one_line(client, r.title, r.body, ja, facts)
        adv = f"# {r.title}\n\n{r.body}\n\n## In one line\n{iol['text']}"
        c = p.check_en_contract(adv)
    w1.wt(f"{ed}/b1b/article.md", adv)
    w1.wj(f"{ed}/b1b/contract.json", {"retried": retried, **{k: v for k, v in c.items() if k != "split"}})
    if not c["ok"]:
        w1.wj(f"{ed}/en_summary.json", {"status": "ADV_CONTRACT_STOP", "violations": c["violations"]})
        raise pl.PipelineStop("ADV_CONTRACT_STOP", str(c["violations"]))
    s = std_gen.generate_family_x_standard_a2_no_heading(adv, client=client, must_fix=mf)
    cs = p.check_en_contract(s.text)
    sretried = False
    if not cs["ok"] and any("PARAGRAPH_COUNT" in v for v in cs["violations"]):
        sretried = True
        s = std_gen.generate_family_x_standard_a2_no_heading(adv, client=client, must_fix=mf + efam._FAMILY_X_PARAGRAPH_RETRY_MUST_FIX)
        cs = p.check_en_contract(s.text)
    w1.wt(f"{ed}/a2/article.md", s.text)
    w1.wj(f"{ed}/a2/contract.json", {"retried": sretried, **{k: v for k, v in cs.items() if k != "split"}})
    e1 = None
    if cs["ok"]:
        sp = p.split_en_article(s.text)
        vs = {k: sp["paragraphs"][i] for i, k in enumerate(pl.SLOTS)}
        intended = {s_: s5["personas"][s_]["sheet"]["claim_core_ja"] for s_ in pl.SLOTS}
        e1 = pl.e1_claims(ctx, vs, intended, "English, simplified", "std")
    w1.wj(f"{ed}/e1_std_claims.json", e1)
    w1.wj(f"{ed}/en_monitors.json", {"b1b": p.en_monitors(adv), "a2": p.en_monitors(s.text)})
    w1.wj(f"{ed}/en_summary.json", {"status": "OK" if cs["ok"] else "STD_CONTRACT_STOP", "std_violations": cs["violations"], "ja_sha256": w1.sha_text(ja),
                                    "adv_sha256": w1.sha_text(adv)})
    timer.mark("english", t)
    guard(rd, "after english")


def finish(rd, a, ctx, timer, status):
    summ = {"status": status, "theme": a.theme, "run_id": a.run_id, "finished": pl.now_iso(), "run_cost_jpy": run_cost(rd), "tree_cost_jpy": tree_cost(),
            "n_calls_this_process": len(ctx.calls), "stage_seconds": timer.rec, "total_seconds": round(time.time() - timer.t0, 1)}
    w1.wj(f"{rd}/run_status.json", summ)
    print("[PIPELINE] " + json.dumps(summ, ensure_ascii=False), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--theme", required=True, choices=sorted(THEMES))
    ap.add_argument("--run-id", required=True, choices=("main", "repro"))
    ap.add_argument("--text-only", action="store_true", help="Voice Gateまで(Tension・英語なし)")
    ap.add_argument("--stop-after", choices=("s2",), default=None, help="S2(当事者洗い出し+網羅判定)の後で止める(予算管理用)")
    a = ap.parse_args()
    rd = f"{TREE}/{a.theme}/{a.run_id}"
    try:
        cmd_run(a)
    except (pl.PipelineStop, y0.YStop) as e:
        os.makedirs(rd, exist_ok=True)
        w1.wj(f"{rd}/run_status.json", {"status": "STOP", "code": getattr(e, "code", "?"), "message": str(e), "finished": pl.now_iso(),
                                       "run_cost_jpy": run_cost(rd) if os.path.exists(rd) else None})
        print(f"[PIPELINE] STOP {e}", flush=True)
        sys.exit(4)


if __name__ == "__main__":
    main()

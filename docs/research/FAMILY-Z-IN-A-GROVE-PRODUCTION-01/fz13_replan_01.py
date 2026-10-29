# -*- coding: utf-8 -*-
"""FAMILY-Z-IN-A-GROVE-PRODUCTION-01 委任_13 (OPEN-596): 閉じ引用符の無い発言のclip計画是正に伴う segment_plan 再導出(本文は不変)。
使い捨てtool。Production関数(w62.stage_plan=run_plan)を再利用し、(1)分割(select_split)だけは既存planの確定値をそのまま返す(LLMで境界を選び直さない=
Part境界・Comment位置・既存Preview/Commentが動かない) (2)話者判定(決定論+LLM突合)は修正後のextract_quotesで全引用を再判定(LLM 1 call/level)
(3)planの出力shaは正規のensure_stage(regenerate)で置換、(4)plan変更でstale化した子孫(support_*)は『本文・Part境界・clip数/idが不変』をassertしたうえで
入力shaだけを付け替える(出力不変・LLM再生成なし。entry['rebinds']に履歴)。不変条件違反は計画・来歴を実行前へ復元して停止。既定dry-run。使い方:
  py docs/research/FAMILY-Z-IN-A-GROVE-PRODUCTION-01/fz13_replan_01.py                                  # dry-run(API 0)
  py docs/research/FAMILY-Z-IN-A-GROVE-PRODUCTION-01/fz13_replan_01.py --apply --approved-budget-jpy 110
  py ... --apply --test-root <wavなしrunコピーのroot>                                                    # test専用(偽LLM・API 0)"""
import argparse, hashlib, json, os, re, shutil, sys, time
sys.path.insert(0, os.getcwd())
import er026_family_z_fiction_production_runner_01 as run
import er062_family_z_writer_01 as w62
import er062_family_z_structure_01 as st

RUN_REL = "er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01"
STORY = "in_a_grove"
# 藪の中の段落→話者(Std/Adv共通14段落。偽LLM[test]専用)
PARA_SPEAKER = {0: "woodcutter", 1: "monk", 2: "constable", 3: "old_woman", 4: "tajomaru", 5: "tajomaru", 6: "masago", 7: "masago", 8: "masago",
                9: "takehiro", 10: "takehiro", 11: "takehiro", 12: "takehiro", 13: "takehiro"}


def sha_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def old_split_info(old_plan):
    """既存planの確定済み分割をselect_splitの戻り値形式で返す(LLMを呼ばない)。"""
    calls = [c for c in old_plan.get("llm_calls", []) if str(c.get("label", "")).startswith("z_split_")]
    return {"boundaries": list(old_plan["boundaries"]), "reason_ja": old_plan["split_reason_ja"],
            "candidates": [list(c) for c in old_plan["candidate_boundaries"]], "attempts": [], "calls": calls,
            "split_model_id": old_plan.get("split_model_id", ""), "prompt_sha256": ""}


class FakeLLM:
    """test専用: 段落→話者表から話者判定JSONを返す(API 0)。"""
    class _B:
        spent = 0.0
    budget = _B()

    def call(self, key, label, user, *, developer=None, effort, schema=None):
        ids = re.findall(r"\[\[Q:(q(\d+)_(\d+))\]\]", user)
        arr = [{"quote_id": q, "speaker": PARA_SPEAKER[int(p)], "basis": "fake(test)"} for (q, p, _k) in ids]
        meta = {"label": label, "routing_key": key, "attempt": 1, "requested_model": "fake", "actual_model_id": "fake", "cost_jpy": 0.0}
        return {"text": json.dumps({"attributions": arr}), "meta": meta}


def core(ctx, llm, out):
    prov = run._prov(ctx)
    old = {}
    for lv in ("b1b", "a2"):
        p = f"{out}/segment_plan_{lv}.json"
        text = w62.rd(run._level_text_path(ctx, lv))
        old[lv] = {"plan": w62.rj(p), "support_in_old": w62.support_stage_input_sha(lv, text, sha_file(p))}
        for stem in ("segment_plan", "dialogue_attribution"):
            shutil.copyfile(f"{out}/{stem}_{lv}.json", f"{out}/{stem}_{lv}.pre_fz13.json")
    prov_p = f"{out}/writer/provenance.json"
    shutil.copyfile(prov_p, f"{out}/writer/provenance.pre_fz13.json")
    orig_select, cur = w62.select_split, {"lv": None}

    def stub_select(llm_, paragraphs, *, label="z_split"):
        si = old_split_info(old[cur["lv"]]["plan"])
        assert [list(c) for c in st.enumerate_split_candidates(st.para_word_counts(paragraphs))] == si["candidates"], "candidate boundaries changed"
        return si
    w62.select_split = stub_select
    events = []
    try:
        for lv in ("b1b", "a2"):
            cur["lv"] = lv
            with ctx.stage_context("plan"):
                r = w62.stage_plan(llm, ctx.out_dir, ctx.slug, ctx.run, lv, prov, True, story_key=ctx.story_key)
            plan = run._check_plan_after(ctx, lv)
            o = old[lv]["plan"]
            assert plan["boundaries"] == o["boundaries"], f"{lv}: boundaries changed"
            assert plan["source_text_sha256"] == o["source_text_sha256"], f"{lv}: text changed"
            assert plan["paragraph_count"] == o["paragraph_count"] and plan["parts"] == o["parts"], f"{lv}: parts changed"
            assert len(plan["clips"]) == len(o["clips"]), (lv, len(plan["clips"]), len(o["clips"]))
            assert plan["comment_after_segment_id"] == o["comment_after_segment_id"], f"{lv}: comment position changed"
            assert [c["id"] for c in plan["clips"]] == [c["id"] for c in o["clips"]], f"{lv}: clip ids changed"
            events.append({"level": lv, "status": r["status"], "dialogue_summary": plan["dialogue_summary"],
                           "clips_changed": [c["id"] for c, oc in zip(plan["clips"], o["clips"]) if (c["text"], c["speaker"]) != (oc["text"], oc["speaker"])]})
        prov2 = run._prov(ctx)
        rebinds = []
        for lv in ("b1b", "a2"):
            name = f"support_{lv}"
            ent = prov2.stage_entry(name)
            new_in = w62.support_stage_input_sha(lv, w62.rd(run._level_text_path(ctx, lv)), sha_file(f"{out}/segment_plan_{lv}.json"))
            assert ent is not None and ent["input_sha256"] == old[lv]["support_in_old"], f"{name}: 旧入力shaが想定と不一致(付け替えない)"
            assert sha_file(f"{out}/support/{lv}_support.json") == ent["output_sha256"], f"{name}: support出力shaが来歴と不一致"
            ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "reason": "FZ13_plan_quote_span_fix(閉じ引用符の無い発言をdialogue clipへ)",
                  "from_input_sha256": ent["input_sha256"], "to_input_sha256": new_in, "api_calls": 0,
                  "invariants": "本文sha・Part境界・段落数・parts統計・clip数/id・Comment位置が不変(上のassert)。support出力は本文とPart境界のみから作られるため不変"}
            ne = dict(ent, input_sha256=new_in)
            ne["rebinds"] = list(ent.get("rebinds") or []) + [ev]
            prov2.data["downstream_stages"][name] = ne
            if name in prov2.data["downstream_stale"]:
                prov2.data["downstream_stale"].remove(name)
            rebinds.append({"stage": name, "from": ent["input_sha256"][:12], "to": new_in[:12]})
        prov2.save()
        run.write_speaker_table(ctx)
        return {"events": events, "rebinds": rebinds, "downstream_stale_after": prov2.data["downstream_stale"]}
    except Exception:
        for lv in ("b1b", "a2"):    # 不変条件違反・STOP: 計画と来歴を実行前へ戻す(半端な状態を残さない)。費用は発生済みならcost_logに残る
            for stem in ("segment_plan", "dialogue_attribution"):
                shutil.copyfile(f"{out}/{stem}_{lv}.pre_fz13.json", f"{out}/{stem}_{lv}.json")
        shutil.copyfile(f"{out}/writer/provenance.pre_fz13.json", prov_p)
        print("[FZ13] 例外のため segment_plan/dialogue_attribution/provenance を実行前へ復元しました", file=sys.stderr)
        raise
    finally:
        w62.select_split = orig_select


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--approved-budget-jpy", type=float, default=0.0)
    ap.add_argument("--test-root", default=None)
    a = ap.parse_args()
    if not a.apply:
        for lv, f in (("b1b", "writer/r2.md"), ("a2", "writer/std.md")):
            _t, body = st.split_title_body(w62.rd(f"{RUN_REL}/{f}"))
            old = w62.rj(f"{RUN_REL}/segment_plan_{lv}.json")
            print(lv, "quotes(new extract)=", len(st.extract_quotes(st.clean_body_paragraphs(body))), "old summary=", old["dialogue_summary"], "boundaries=", old["boundaries"])
        print("dry-run: --apply --approved-budget-jpy N でLLM 2 call(話者判定のみ、約0.1円/level)を実行")
        return 0
    if a.test_root:
        out = f"{a.test_root}/{STORY}/run_sf_prod_01"
        ctx = run.E2EContext(story_key=STORY, slug=STORY, run="run_sf_prod_01", mode="mock", run_root=a.test_root)
        res = core(ctx, FakeLLM(), out)
    else:
        ns = argparse.Namespace(story=STORY, slug=STORY, run="run_sf_prod_01", approved_budget_jpy=a.approved_budget_jpy,
                                warn_threshold_jpy=run.E2E_WARN_THRESHOLD_JPY, ack_warn_threshold=False, tts_execution_mode=None)
        ctx = run.build_real_context(ns)
        try:
            res = core(ctx, run._w62_llm(ctx), RUN_REL)
            res["spent_jpy"] = round(ctx.budget.spent(), 4)
        finally:
            run._release_launch_lock()
    print(json.dumps(res, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())

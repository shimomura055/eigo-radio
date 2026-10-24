# -*- coding: utf-8 -*-
"""FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 委任_02: DEV/Trial専用runner(sftrial_dev_runner_01同型)。

- Production(er062_family_z_writer_01.py等)は書き換えない。import後にメモリ上でのみ関数/定数を差替える。Productionからのimport参照0。
- arm: i=現行Production文言(差替えなし) / ii=汎用置換のみ(Seed欄なし。REVISEの"in third person, "を汎用文へ) /
       iii=案A(Seedのnarration_voiceをMust-keepのNarration行として全段に描画 + REVISEの"in third person, "を欄参照へ置換)。
- 既定OFF保証: narration_voiceが無いessentialsでは描画関数は元関数とbyte同一。armがiii以外ではREVISE文は欄を参照しない。
- 出力は er026_output/family_z_dev_trials/fz_essence_01/ のみ(er026_output/family_z_production_e2e_01/ へ書かない)。flag新設なし。
"""
import argparse, os, sys, json, hashlib, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
import er062_family_z_writer_01 as w          # noqa: E402  (Production module。import only、file無変更)

OUT_ROOT = "er026_output/family_z_dev_trials/fz_essence_01"
PROD_RUN_ROOT = "er026_output/family_z_production_e2e_01"
DEV_SEED_TTH = "docs/research/FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01/dev_seed/the_tell_tale_heart"
ORIG = {"_render_essentials_block": w._render_essentials_block, "build_revise_prompt": w.build_revise_prompt,
        "REVISE_USER_TMPL": w.REVISE_USER_TMPL}
_sha = lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()

THIRD = "in third person, "
REV_II = "in the same point of view and narration as the story above, "
REV_III = "in the narration described in the Must-keep section below, "
NARR_LINE = ("- Narration: {voice} Keep this narration throughout: the same person, point of view and narrator's stance "
             "(including how the narrator speaks to the listener); wording, length and sentence structure may change. "
             "The role descriptions of people below do not change who is telling the story.")

ARM = {"v": "i"}      # 現在のarm(メモリ上のみ)


def render_dev(ess: dict, mode: str) -> str:
    """元の描画 + narration_voiceがある場合のみ、導入2行の直後(Key people行より前)にNarration行を1行挿入。無ければbyte同一。"""
    base = ORIG["_render_essentials_block"](ess, mode)
    v = (ess or {}).get("narration_voice")
    if not v:
        return base
    L = base.split("\n")
    L.insert(2, NARR_LINE.format(voice=v.strip()))
    return "\n".join(L)


def revise_dev(body: str, story_key: str = "melos", essentials=None) -> str:
    arm = ARM["v"]
    has_voice = essentials is not None and bool((essentials.ess or {}).get("narration_voice"))
    if arm == "ii" or (arm == "iii" and has_voice):
        rep = REV_II if arm == "ii" else REV_III
        tmpl = ORIG["REVISE_USER_TMPL"]
        assert THIRD in tmpl
        w.REVISE_USER_TMPL = tmpl.replace(THIRD, rep, 1)
        try:
            return ORIG["build_revise_prompt"](body, story_key, essentials=essentials)
        finally:
            w.REVISE_USER_TMPL = tmpl
    return ORIG["build_revise_prompt"](body, story_key, essentials=essentials)


def install(arm: str):
    assert arm in ("i", "ii", "iii")
    ARM["v"] = arm
    w._render_essentials_block = render_dev
    w.build_revise_prompt = revise_dev


def uninstall():
    ARM["v"] = "i"
    w._render_essentials_block = ORIG["_render_essentials_block"]
    w.build_revise_prompt = ORIG["build_revise_prompt"]
    w.REVISE_USER_TMPL = ORIG["REVISE_USER_TMPL"]


def validate_narration_voice(seed: dict):
    """DEV専用のSeed記入規則検査(DESIGN_02 §3-5。本文Validatorではない)。arm iii用。"""
    v = ((seed or {}).get("source_essentials") or {}).get("narration_voice")
    if not (isinstance(v, str) and v.strip()):
        raise SystemExit("STOP: DEV Seedのsource_essentials.narration_voiceが空(arm iiiでは必須)")


def _setup(out_dir, budget_cap):
    w.st.check_stop_sentinel("startup:fz_essence_dev_runner_real", out_dir)
    os.makedirs(out_dir, exist_ok=True)
    client, cl = w._setup_real(out_dir)
    return client, cl, w.Budget(budget_cap, w.DEFAULT_EST)


def cmd_1a(a):
    """r0.md固定入力でR1のみ。arm x samples。"""
    r0 = w.rd(f"{PROD_RUN_ROOT}/the_tell_tale_heart/run_sf_prod_01/writer/r0.md")
    prod_seed = w.rj(f"{PROD_RUN_ROOT}/the_tell_tale_heart/seed/seed.json")
    dev_seed = w.rj(f"{DEV_SEED_TTH}/seed.json")
    validate_narration_voice(dev_seed)
    jobs = []
    for arm in a.arms.split(","):
        for k in range(1, a.samples + 1):
            jobs.append((arm, k))
    prompts = {}
    for arm, k in jobs:
        install(arm)
        ess = w.build_essentials(dev_seed if arm == "iii" else prod_seed)
        prompts[(arm, k)] = w.build_revise_prompt(r0, "the_tell_tale_heart", essentials=ess)
    uninstall()
    base = f"{OUT_ROOT}/the_tell_tale_heart/1a"
    if a.mode == "dry-run":
        for (arm, k), p in prompts.items():
            print(f"===== arm {arm} s{k} sha={_sha(p)[:12]} =====")
            if k == 1:
                print(p)
        return 0
    if a.budget <= 0:
        sys.exit("STOP: real は --budget(>0)必須")
    client, cl, budget = _setup(base, a.budget)
    llm = w.LLM(client, budget)
    ctx = cl.logging_context("FZ_ESSENCE_TRIAL_1A", "writer")
    with ctx:
        for (arm, k), p in prompts.items():
            d = f"{base}/{arm}_s{k}"
            if os.path.exists(f"{d}/r1.md"):
                print("skip existing", d)
                continue
            os.makedirs(d, exist_ok=True)
            w.wt(f"{d}/r1_prompt.txt", p)
            res = llm.call(w.STAGE_KEY["r1"], f"fz1a_{arm}_s{k}", p, developer=None, effort=w.WRITER_EFFORT)
            w.wt(f"{d}/r1.md", res["text"].strip() + "\n")
            m = {"arm": arm, "sample": k, "prompt_sha256": _sha(p), "cost_jpy": res["meta"]["cost_jpy"],
                 "model": res["meta"]["actual_model_id"], "response_id": res["meta"]["response_id"], "attempts": res["attempts"],
                 "at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
            w.wt(f"{d}/meta.json", json.dumps(m, ensure_ascii=False, indent=1))
            print(json.dumps(m, ensure_ascii=False))
    print(json.dumps({"spent_jpy": round(budget.spent, 4), "calls": len(budget.calls)}))
    return 0


def cmd_chain(a):
    """全段チェーン r0->r1->r2->std_adjust。--seed-dir/--story/--sub/--samples/--arm。"""
    seed_dir = a.seed_dir.replace("\\", "/")
    seed = w.rj(f"{seed_dir}/seed.json")
    if a.arm == "iii":
        validate_narration_voice(seed)
    install(a.arm)
    try:
        if a.mode == "dry-run":
            ess = w.build_essentials(seed)
            p, _ = w.build_r0_prompt(seed, essentials=ess)
            print(p)
            print("\n=====REVISE=====\n")
            print(w.build_revise_prompt("<BODY>", a.story, essentials=ess))
            print("\n=====STD (tail)=====\n")
            print(w.build_std_prompt("# T\n\n<P1>\n\n<P2>", essentials=ess)[-2600:])
            return 0
        if a.budget <= 0:
            sys.exit("STOP: real は --budget(>0)必須")
        first_out = f"{OUT_ROOT}/{a.story}/{a.sub}_s1"
        client, cl, budget = _setup(first_out, a.budget)
        llm = w.LLM(client, budget)
        summary = []
        for k in range(1, a.samples + 1):
            out_dir = f"{OUT_ROOT}/{a.story}/{a.sub}_s{k}"
            os.makedirs(out_dir, exist_ok=True)
            if k > 1:
                cl.install(os.path.join(out_dir, "raw_usage_log.jsonl"))
            ctx = cl.logging_context("FZ_ESSENCE_TRIAL_CHAIN_" + a.story.upper(), "writer")
            before = budget.spent
            with ctx:
                res = w.run_writer_chain(llm, out_dir, seed_dir, stages=("r0", "r1", "r2", "std_adjust"), story_key=a.story)
            w.write_cp_checklist(out_dir, seed, a.story)
            if a.arm == "iii":
                with open(f"{out_dir}/writer/cp_checklist.md", "a", encoding="utf-8") as f:
                    f.write("\n## narration行(DEV追加。DESIGN_02 §3-4)\n\n| 深刻度 | 項目 | 内容 | 本文の該当引用(r0/r1/r2/std) | 判定 |\n|---|---|---|---|---|\n"
                            f"| 重大 | narration(人称・語り手の立場) | {seed['source_essentials']['narration_voice']} |  |  |\n")
            summary.append({"sample": k, "out_dir": out_dir, "spent_jpy": round(budget.spent - before, 4),
                            "stages": {s: v["status"] for s, v in res["stages"].items()},
                            "guardrails": {s: v["guardrails"] for s, v in res["stages"].items()}})
            print(json.dumps(summary[-1], ensure_ascii=False))
        w.wt(f"{OUT_ROOT}/{a.story}/{a.sub}_run_summary.json", json.dumps(
            {"arm": a.arm, "seed_dir": seed_dir, "total_spent_jpy": round(budget.spent, 4), "calls": len(budget.calls), "samples": summary},
            ensure_ascii=False, indent=1))
        print(json.dumps({"spent_jpy": round(budget.spent, 4), "calls": len(budget.calls)}))
        return 0
    finally:
        uninstall()


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("1a")
    p1.add_argument("--arms", default="i,ii,iii")
    p1.add_argument("--samples", type=int, default=2)
    p1.add_argument("--mode", choices=("dry-run", "real"), default="dry-run")
    p1.add_argument("--budget", type=float, default=0.0)
    p2 = sub.add_parser("chain")
    p2.add_argument("--story", required=True)
    p2.add_argument("--seed-dir", required=True)
    p2.add_argument("--sub", required=True)
    p2.add_argument("--arm", choices=("ii", "iii"), required=True)
    p2.add_argument("--samples", type=int, default=1)
    p2.add_argument("--mode", choices=("dry-run", "real"), default="dry-run")
    p2.add_argument("--budget", type=float, default=0.0)
    a = ap.parse_args()
    return cmd_1a(a) if a.cmd == "1a" else cmd_chain(a)


if __name__ == "__main__":
    sys.exit(main())

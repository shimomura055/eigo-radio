# -*- coding: utf-8 -*-
"""FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01 委任_03 U1統合Offline Trial: DEV専用runner(Trial専用)。

- Production(er062_family_z_writer_01.py等)は書き換えない。import後にメモリ上で build_r0/revise/std_prompt と Prompt定数だけ差替える。
- Seedは Trial dir内のコピー(sftrial_seeds/<arm>/)を使う(Production seed.json無変更)。seed_dir_forをメモリ上でoverride。
- arm: t1 = Seed修正のみ(Prompt現行のまま) / t2 = 修正版B(essentials全段引継ぎ+keep_name上書き+Std関係明示)。
- essentials(Seedの任意キー source_essentials)が無いSeedでは、修正版B関数は元の関数をそのまま呼ぶ=byte同一(メロス)。
- このfileは docs/research 配下のDEV専用。Production(er0xx_*.py)からのimport参照0。
"""
import argparse, os, sys, json, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
import er062_family_z_writer_01 as w          # noqa: E402  (Production module。import only、file無変更)

SEED_ROOT = os.path.join("docs", "research", "FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01", "sftrial_seeds")

# 元関数・定数の保存(byte同一testで比較に使う)
ORIG = {"build_r0_prompt": w.build_r0_prompt, "build_revise_prompt": w.build_revise_prompt,
        "build_std_prompt": w.build_std_prompt, "R0_BLOCK_COMMON": w.R0_BLOCK_COMMON,
        "R0_BLOCK_PRESERVATION": w.R0_BLOCK_PRESERVATION, "REVISE_USER_TMPL": w.REVISE_USER_TMPL,
        "R0_TEMPLATE": w.R0_TEMPLATE, "STD_PROMPT_TAIL": w.STD_PROMPT_TAIL}
ORIG_SEED_DIR_FOR = w.seed_dir_for

_sha = lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()


def _esc(s: str) -> str:
    return s.replace("{", "{{").replace("}", "}}")


# ---------------- essentials(決定論の純関数。作品固有名は共通Promptに無く、Seedデータ側のみ) ----------------
def _roles(ess):
    return ess.get("key_roles") or []


def keep_names(ess) -> list:
    return [r["name"] for r in _roles(ess) if r.get("keep_name") and r.get("name")]


def build_essentials_block(seed: dict, mode: str = "full") -> str:
    """mode='full': R0/R1/R2用。'std': Std調整用(入力が完成稿のため結末前の示唆禁止は不要。closing line関係明示を追加)。
    seedに source_essentials が無ければ ''(=従来動作)。"""
    ess = (seed or {}).get("source_essentials")
    if not ess:
        return ""
    L = ["[Must-keep -- story essentials]",
         "These are the points that make this story work. Keep their meaning (your own words are fine); everything not listed here may be shortened or reshaped."]
    er = ess.get("ending_reveal")
    if er:
        q = (' (the original\'s own last sentence: "' + er["source_quote"] + '").') if er.get("source_quote") else "."
        L.append("- Ending (required): " + er["meaning"] +
                 " The final reveal line is part of the story, not a summary, a moral or a new explanation: keep it as the closing line "
                 "of the story, in your own words if you like, but its idea must be clearly conveyed" + q)
        if mode == "full" and er.get("withhold_until_end"):
            L.append("- Not before the ending: " + er["withhold_until_end"])
    for sp in ess.get("setups_and_payoffs") or []:
        L.append("- Setup and payoff (keep both): " + sp["setup"] + " -> " + sp["payoff"])
    roles = _roles(ess)
    if roles:
        parts = []
        for r in roles:
            if r.get("keep_name") and r.get("name"):
                parts.append(f"{r['name']} ({r['role']}) -- keep the name {r['name']}")
            else:
                parts.append(f"{r['role']} -- refer to this person by role or relationship, without a name")
        L.append("- Key people: " + "; ".join(parts) + ".")
    for c in ess.get("key_causality") or []:
        L.append("- Cause and effect to keep: " + c)
    if mode == "std":
        L.append("- The closing line (the final reveal) must stay as the last line of the A2 version: it is part of the story, "
                 "not a closing summary or a new explanation, so the rules against summaries and new explanations do not apply to it.")
    if ess.get("free_to_cut"):
        L.append("- May be cut or compressed: " + "; ".join(ess["free_to_cut"]) + ".")
    return "\n".join(L)


_NAME_SENT_R0 = "Only the main character (the protagonist) may be given a personal name."
_NAME_SENT_R0_NEW = ("Only the main character (the protagonist) and the people marked \"keep the name\" in the Must-keep section may be given "
                     "personal names; use only one of the two names (first or last) of a person, consistently.")
_PRES_LAST = "- Keep the cast small and do not add named people other than the main character."
_PRES_LAST_NEW = ("- Keep the cast small and do not add named people other than the main character and the people marked "
                  "\"keep the name\" in the Must-keep section.")
_REV_NAME = "and only {main_character} may have a personal name."
_REV_NAME_NEW = ("and only {main_character} and the people marked \"keep the name\" in the Must-keep section below may have a personal name "
                 "(keep those names as they are; use no other personal names).")


def build_r0_prompt_t2(seed: dict, story_type: str = "literature"):
    ess_block = build_essentials_block(seed, "full")
    if not ess_block:
        return ORIG["build_r0_prompt"](seed, story_type)
    has_keep = bool(keep_names(seed["source_essentials"]))
    common = ORIG["R0_BLOCK_COMMON"]
    pres = ORIG["R0_BLOCK_PRESERVATION"]
    if has_keep:
        assert _NAME_SENT_R0 in common and _PRES_LAST in pres
        common = common.replace(_NAME_SENT_R0, _NAME_SENT_R0_NEW)
        pres = pres.replace(_PRES_LAST, _PRES_LAST_NEW)
    tmpl = ("[Story Seed -- inspired by a real, rights-cleared source, freely reimagined;\n"
            "this is NOT a summary to reproduce, just raw material]\n{seed_bullets}\n\n"
            "[How to convert it]\n{conversion}\n\n"
            + pres + "\n\n" + _esc(ess_block) + "\n\n" + w.R0_BLOCK_STORY_TYPE + "\n\n" + common + "\n\n"
            + w.R0_BLOCK_LENGTH_ADV + "\n\n" + w.R0_BLOCK_LISTENING + "\n\n" + w.R0_BLOCK_FINAL)
    saved = w.R0_TEMPLATE
    w.R0_TEMPLATE = tmpl
    try:
        return ORIG["build_r0_prompt"](seed, story_type)
    finally:
        w.R0_TEMPLATE = saved


def make_revise(seed):
    def build_revise_prompt_t2(body: str, story_key: str = "melos") -> str:
        ess_block = build_essentials_block(seed, "full")
        if not ess_block:
            return ORIG["build_revise_prompt"](body, story_key)
        tmpl = ORIG["REVISE_USER_TMPL"]
        if keep_names(seed["source_essentials"]):
            assert _REV_NAME in tmpl
            tmpl = tmpl.replace(_REV_NAME, _REV_NAME_NEW)
        tail = " Output the title and the story only."
        assert tail in tmpl
        tmpl = tmpl.replace(tail, "\n\n" + _esc(ess_block) + "\n\nOutput the title and the story only.")
        return tmpl.format(body=body.strip(), main_character=w.STORY_MAIN_CHARACTER[story_key])
    return build_revise_prompt_t2


def make_std(seed):
    def build_std_prompt_t2(adv_text: str) -> str:
        ess_block = build_essentials_block(seed, "std")
        if not ess_block:
            return ORIG["build_std_prompt"](adv_text)
        tail = ORIG["STD_PROMPT_TAIL"]
        anchor = "\n\nKeep the essence of the source story"
        assert anchor in tail
        w.STD_PROMPT_TAIL = tail.replace(anchor, "\n\n" + _esc(ess_block) + anchor, 1)
        try:
            return ORIG["build_std_prompt"](adv_text)
        finally:
            w.STD_PROMPT_TAIL = tail
    return build_std_prompt_t2


def install(arm: str):
    """arm=t1: Seedコピーのみ差替え(Prompt関数は現行)。arm=t2: 修正版B関数を差替え。"""
    seed_dir = f"{SEED_ROOT}/{arm}".replace("\\", "/")
    w.seed_dir_for = lambda slug: seed_dir if slug == "the_open_window" else ORIG_SEED_DIR_FOR(slug)
    if arm == "t2":
        seed = w.rj(f"{seed_dir}/seed.json")
        w.build_r0_prompt = build_r0_prompt_t2
        w.build_revise_prompt = make_revise(seed)
        w.build_std_prompt = make_std(seed)
    return seed_dir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=("t1", "t2"), required=True)
    ap.add_argument("--run", required=True)
    ap.add_argument("--stages", default="r0", help="comma: r0,r1,r2,std_adjust")
    ap.add_argument("--mode", choices=("dry-run", "real"), default="dry-run")
    ap.add_argument("--approved-budget-jpy", type=float, default=0.0)
    a = ap.parse_args()
    story = "the_open_window"
    sdir = install(a.arm)
    stages = tuple(a.stages.split(","))
    out_dir = w.out_dir_for(story, a.run)
    seed = w.rj(f"{sdir}/seed.json")
    if a.mode == "dry-run":
        p, _ = w.build_r0_prompt(seed)
        print(p)
        print("\n=====REVISE=====\n")
        print(w.build_revise_prompt("<BODY>", story))
        print("\n=====STD (tail excerpt)=====\n")
        print(w.build_std_prompt("# T\n\n<P1>\n\n<P2>")[-2200:])
        return 0
    if a.approved_budget_jpy <= 0:
        sys.exit("STOP: real は --approved-budget-jpy(>0)必須")
    w.st.check_stop_sentinel("startup:sftrial_dev_runner_real", out_dir)
    os.makedirs(out_dir, exist_ok=True)
    client, cl = w._setup_real(out_dir)
    ctx = cl.logging_context("FAMILY_Z_SOURCE_FIDELITY_U1_TRIAL_" + a.arm.upper(), "writer")
    budget = w.Budget(a.approved_budget_jpy, w.DEFAULT_EST)
    llm = w.LLM(client, budget)
    with ctx:
        res = w.run_writer_chain(llm, out_dir, sdir, stages=stages, story_key=story)
    ess = build_essentials_block(seed, "full") if a.arm == "t2" else ""
    meta_path = f"{out_dir}/sftrial_run_meta.json"
    prev = json.load(open(meta_path, encoding="utf-8")) if os.path.exists(meta_path) else {"invocations": []}
    prev["arm"] = a.arm
    prev["seed_dir"] = sdir
    prev["essentials_block_sha256"] = _sha(ess) if ess else None
    prev["invocations"].append({"stages_run": list(stages), "spent_jpy": round(budget.spent, 4), "calls": len(budget.calls)})
    json.dump(prev, open(meta_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: {"status": v["status"], "guardrails": v["guardrails"]} for k, v in res["stages"].items()}, ensure_ascii=False, indent=1))
    print(json.dumps({"spent_jpy": round(budget.spent, 4), "calls": len(budget.calls)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())

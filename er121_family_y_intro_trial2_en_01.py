# -*- coding: utf-8 -*-
"""FY-SPEAKER-INTRO-GENERALIZATION-TRIAL-01 委任_02 英語化preview(DEV/Trial専用)。ja_candidates_AB.jsonの全JA候補を、記事の既存英訳の紹介行を文体見本にAdv/Stdで英語化。記事未適用。"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import er005_cost_logger as cl
import er121_family_y_text_core_01 as tc
import er121_family_y_intro_trial2_01 as t2
DEV = "You translate one-to-two-sentence narrator introductions for a bilingual English-learning radio article. Output JSON only."
RULE = {
    "adv": "Level: Advanced (B1+). Faithful, natural English. Third person narrator voice, present tense. Start with the order phrase (First to speak / The next speaker / The last speaker ...). Do not add facts that are not in the Japanese.",
    "a2": "Level: Standard (A2). Very easy English: short sentences (about 8-12 words), common words, no relative-clause chains. Start with the order phrase (First / Next / Last ...). Do not add facts that are not in the Japanese.",
}


def intro_lines(run, lv):
    txt = open(f"{run}/translate/{lv}.md", encoding="utf-8").read()
    paras = [p.strip() for p in re.split(r"\n\s*\n", txt.strip())]
    return [p.split("\n", 1)[0].strip() for p in paras[2:5]]


def main(slug):
    out = f"er121_output/family_y_intro_trial_01/{slug}"
    cand = json.load(open(f"{out}/ja_candidates_AB.json", encoding="utf-8"))
    run = t2.ART[slug]["run"]
    base = {"adv": intro_lines(run, "b1b"), "a2": intro_lines(run, "a2")}
    sets = {f"{c}_{s}": cand[c]["intros"][s] for c in cand for s in tc.SLOTS}
    schema = {"name": "intro_en", "strict": True, "schema": {"type": "object", "additionalProperties": False, "required": list(sets), "properties": {k: {"type": "string"} for k in sets}}}
    cl.install(f"{out}/cost_log_en.jsonl")
    import er003_v1_en_direct_vfl_01_generate as vfl01
    client = vfl01.get_client()
    res = {}
    for lv in ("adv", "a2"):
        user = (RULE[lv] + "\n\nStyle reference (existing intro lines of the same article, keep this style):\n" + "\n".join("- " + r for r in base[lv])
                + "\n\nTranslate each Japanese introduction:\n" + "\n".join(f"{k}: {v}" for k, v in sets.items()))
        resp = tc.chat(client, route_key="FAMILY_Y_PERSONA_INTRO", user=user, developer=DEV, schema=schema, stage=f"trial2_intro_en_{slug}_{lv}")
        res[lv] = {"en": tc._json_resp(resp, "en"), "model": getattr(resp, "model", None), "response_id": getattr(resp, "id", None)}
    json.dump({"ja": sets, "baseline_en": base, "en": res}, open(f"{out}/en_preview.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(slug, "ok")


if __name__ == "__main__":
    main(sys.argv[1])

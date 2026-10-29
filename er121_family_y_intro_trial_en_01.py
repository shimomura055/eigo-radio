# -*- coding: utf-8 -*-
"""FY-SPEAKER-INTRO-GENERALIZATION-TRIAL-01 英語化preview(DEV/Trial専用)。JA紹介文候補を、既存の英訳(Adv=忠実/Std=易しい)の文体でintro行だけ英語化する。
run_02の既存英訳(V2/V3の紹介行)を文体見本として渡す。作成物は比較用であり、記事へは未適用。"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import er005_cost_logger as cl
import er121_family_y_text_core_01 as tc
OUT = "er121_output/family_y_intro_trial_01/surname"
SETS = {
    "V1_A1": "最初に話すのは、結婚して妻の姓を名乗り、妻の実家で家族と暮らしている男性だ。",
    "V1_MIN": "最初に話すのは、婿養子になって妻の姓を名乗っている男性。妻の実家で、家族と暮らしている。",
    "V1_B1": "最初に話すのは、結婚を機に妻の姓になった男性。妻や妻の家族と、同じ家で暮らしている。",
    "V2_B1": "次は、結婚を控えた息子が、相手の姓を名乗ると決めたことを知らされた母親。",
    "V3_B1": "最後は、妻の姓になった身内がいる親世代の人。子どもの結婚は、これからのこととして考えている。",
}
REF = {
    "adv": ["The next speaker is a mother whose son is getting married next year. She felt sad when she heard he would take his wife’s last name.",
            "The last speaker is a parent whose relative took his wife’s last name. Their own child has not married yet."],
    "a2": ["The next speaker is a mother. Her son will marry next year. She felt sad when she heard he would take his wife’s last name.",
           "The last speaker is a parent. A relative took his wife’s last name. The parent’s own child is not married yet."],
}
DEV = "You translate one-to-two-sentence narrator introductions for a bilingual English-learning radio article. Output JSON only."
RULE = {
    "adv": "Level: Advanced (B1+). Faithful, natural English. Third person narrator voice, present tense. Start with the order phrase (The first / The next / The last speaker is ...). Do not add facts that are not in the Japanese.",
    "a2": "Level: Standard (A2). Very easy English: short sentences (about 8-12 words), common words, no relative-clause chains. Start with the order phrase (The first / The next / The last speaker is ...). Do not add facts that are not in the Japanese.",
}
SCHEMA = {"name": "intro_en", "strict": True, "schema": {"type": "object", "additionalProperties": False, "required": list(SETS), "properties": {k: {"type": "string"} for k in SETS}}}


def main():
    cl.install(f"{OUT}/cost_log_en.jsonl")
    import er003_v1_en_direct_vfl_01_generate as vfl01
    client = vfl01.get_client()
    res = {}
    for lv in ("adv", "a2"):
        user = (RULE[lv] + "\n\nStyle reference (existing intro lines of the same article, keep this style):\n" + "\n".join("- " + r for r in REF[lv])
                + "\n\nTranslate each Japanese introduction:\n" + "\n".join(f"{k}: {v}" for k, v in SETS.items()))
        resp = tc.chat(client, route_key="FAMILY_Y_PERSONA_INTRO", user=user, developer=DEV, schema=SCHEMA, stage=f"trial_intro_en_{lv}")
        res[lv] = {"en": tc._json_resp(resp, "en"), "model": getattr(resp, "model", None), "response_id": getattr(resp, "id", None)}
        print(lv, json.dumps(res[lv], ensure_ascii=False), flush=True)
    json.dump({"ja": SETS, "en": res}, open(f"{OUT}/en_preview.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""FY-SPEAKER-INTRO-GENERALIZATION-TRIAL-01: 推奨/対照のV1紹介文に、Production既存の決定論検査(check_intro)と Lead+紹介 補助Gate(run_leadintro_gate)を当てる(DEV/Trial。run_02へは書かない)。"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import er005_cost_logger as cl
import er121_family_y_text_core_01 as tc
OUT = "er121_output/family_y_intro_trial_01/surname"
RUN = "er121_output/family_y_production_01/surname_choice/run_02"
THEME = "docs/research/FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01/theme_packages/surname_choice_package_01.json"
V1 = {"REC": "最初に話すのは、妻の姓を名乗り、妻の実家で家族と暮らしている男性だ。",
      "MIN": "最初に話すのは、婿養子になって妻の姓を名乗っている男性。妻の実家で、家族と暮らしている。"}


def main():
    cl.install(f"{OUT}/cost_log_gate.jsonl")
    import er003_v1_en_direct_vfl_01_generate as vfl01
    client = vfl01.get_client()
    theme = tc.load_theme_package(THEME)["theme"]
    spec = tc.intro_spec(theme)
    intros = json.load(open(f"{RUN}/text/lead_intro/intros_final.json", encoding="utf-8"))
    lead = open(f"{RUN}/text/lead_intro/lead_final.txt", encoding="utf-8").read().strip()
    art = open(f"{RUN}/text/article_assembled.md", encoding="utf-8").read()
    blocks = [b.strip() for b in re.split(r"\n\s*\n", art.strip())]
    voices = {s: blocks[2 + i].split("\n", 1)[1].strip() for i, s in enumerate(tc.SLOTS)}
    res = {}
    for k, t in V1.items():
        chk = tc.check_intro(t, "voice_1", voices["voice_1"], spec)
        new = dict(intros); new["voice_1"] = t
        try:
            g = tc.run_leadintro_gate(client, lead, new, f"{OUT}/gate_{k}")
            gs = {"status": g["status"], "applicable_flagged": g["applicable_flagged"], "model": g["model"]}
        except tc.YStop as e:
            gs = {"status": "STOP", "code": e.code, "msg": str(e)[:300]}
        res[k] = {"text": t, "len": len(t), "check_intro": chk, "leadintro_gate": gs}
        print(k, json.dumps(res[k], ensure_ascii=False), flush=True)
    json.dump(res, open(f"{OUT}/v1_gate_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""FY-SPEAKER-INTRO-GENERALIZATION-TRIAL-01 委任_02(DEV/Trial専用・Production未配線)。追加2記事(redelivery_fee/sns_age_limit)へ
er121_family_y_intro_trial_01.build(variant A/B、C/D不採用)を再利用して紹介文JAを生成し、check_intro(参考)を適用、英語化previewまで行う。音声生成なし。
出力: er121_output/family_y_intro_trial_01/<slug>/ 。run側へは書かない。"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import er005_cost_logger as cl
import er121_family_y_text_core_01 as tc
import er121_family_y_intro_trial_01 as t1

ART = {
    "redelivery_fee": dict(run="er121_output/family_y_production_01/redelivery_fee/run_voice_puck_ev_01",
                           theme_data="docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_02/THEME_DATA_02.json",
                           manifest="docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/theme_packages/redelivery_fee_reuse_01.json"),
    "sns_age_limit": dict(run="er121_output/family_y_production_01/sns_age_limit/run_01",
                          package="docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/theme_packages/sns_age_limit_package_01.json"),
}


def load(slug):
    a = ART[slug]
    if "package" in a:
        return tc.load_theme_package(a["package"])["theme"]
    raw = json.load(open(a["theme_data"], encoding="utf-8"))
    man = json.load(open(a["manifest"], encoding="utf-8"))
    raw["intro_checks"] = man["intro_checks"]
    for k in ("lead_premise_ja", "lead_scope_lines"):
        if k in man:
            raw[k] = man[k]
    return tc.load_theme_package(raw)["theme"]


def voices_of(run):
    art = open(f"{run}/text/article_assembled.md", encoding="utf-8").read()
    blocks = [b.strip() for b in re.split(r"\n\s*\n", art.strip())]
    return {s: blocks[2 + i].split("\n", 1)[1].strip() for i, s in enumerate(tc.SLOTS)}


def main(slug, variants=("A", "B"), n=2):
    out = f"er121_output/family_y_intro_trial_01/{slug}"
    os.makedirs(out, exist_ok=True)
    theme = load(slug)
    voices = voices_of(ART[slug]["run"])
    spec = tc.intro_spec(theme)
    parts = tc.load_article_prompt("intro")
    if os.environ.get("DRY"):
        for v in variants:
            p = t1.build(v, theme, voices, parts, spec)
            open(f"{out}/prompt_{v}.txt", "w", encoding="utf-8").write(p)
        print("dry ok", slug, {s: voices[s][:30] for s in tc.SLOTS}); return
    cl.install(f"{out}/cost_log.jsonl")
    import er003_v1_en_direct_vfl_01_generate as vfl01
    client = vfl01.get_client()
    res = {}
    for v in variants:
        prompt = t1.build(v, theme, voices, parts, spec)
        open(f"{out}/prompt_{v}.txt", "w", encoding="utf-8").write(prompt)
        for k in range(n):
            resp = tc.chat(client, route_key="FAMILY_Y_PERSONA_INTRO", user=prompt, developer=parts["developer"], schema=tc.INTRO_SCHEMA, stage=f"trial2_intro_{slug}_{v}{k+1}")
            raw = tc._json_resp(resp, "trial_intro")
            fin = {s: tc._fin(raw[s])[0] for s in tc.SLOTS}
            chk = {s: tc.check_intro(fin[s], s, voices[s], spec) for s in tc.SLOTS}
            res[f"{v}{k+1}"] = {"intros": fin, "check": chk, "model": getattr(resp, "model", None), "response_id": getattr(resp, "id", None)}
            print(slug, v, k + 1, json.dumps(res[f"{v}{k+1}"], ensure_ascii=False), flush=True)
    json.dump(res, open(f"{out}/ja_candidates_{''.join(variants)}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)




# --- 改善案E(1回限り): 原則+B(話題との関わり)+『属性がそのまま立場のときは属性名を使う』 ---
CLAUSE_E = ("【属性がそのまま立場のとき(Trial追加)】職業・当事者の立場など、属性の名前そのものが今回の話題での立場を表す場合(例: 宅配ドライバー、高校生)は、その名前を省かず使い、"
            "続けて話題との関わりを添える。属性が話題での立場を表さない場合だけ、属性名を主にしない。\n")


def main_e(slug, n=2):
    out = f"er121_output/family_y_intro_trial_01/{slug}"
    theme = load(slug); voices = voices_of(ART[slug]["run"]); spec = tc.intro_spec(theme); parts = tc.load_article_prompt("intro")
    t1.PRINCIPLE = t1.PRINCIPLE + CLAUSE_E
    prompt = t1.build("B", theme, voices, parts, spec)
    assert CLAUSE_E in prompt
    open(f"{out}/prompt_E.txt", "w", encoding="utf-8").write(prompt)
    cl.install(f"{out}/cost_log_E.jsonl")
    import er003_v1_en_direct_vfl_01_generate as vfl01
    client = vfl01.get_client(); res = {}
    for k in range(n):
        resp = tc.chat(client, route_key="FAMILY_Y_PERSONA_INTRO", user=prompt, developer=parts["developer"], schema=tc.INTRO_SCHEMA, stage=f"trial2_intro_{slug}_E{k+1}")
        raw = tc._json_resp(resp, "trial_intro"); fin = {s: tc._fin(raw[s])[0] for s in tc.SLOTS}
        res[f"E{k+1}"] = {"intros": fin, "check": {s: tc.check_intro(fin[s], s, voices[s], spec) for s in tc.SLOTS}, "model": getattr(resp, "model", None)}
        print(slug, "E", k + 1, json.dumps(res[f"E{k+1}"], ensure_ascii=False), flush=True)
    json.dump(res, open(f"{out}/ja_candidates_E.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "E":
        main_e(sys.argv[1])
    else:
        main(sys.argv[1], tuple(sys.argv[2].split(",")) if len(sys.argv) > 2 else ("A", "B"))

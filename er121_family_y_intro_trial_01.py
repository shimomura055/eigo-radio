# -*- coding: utf-8 -*-
"""FY-SPEAKER-INTRO-GENERALIZATION-TRIAL-01(DEV/Trial専用・Production未配線)。Y人物紹介の一般化原則(ユーザー候補原則)をPrompt差分として
Productionの persona_intro_01.txt(直接編集しない)のコピー上で試す。出力: er121_output/family_y_intro_trial_01/surname/ 。run_02へは書かない。
variant A = 原則bulletのみ追加 / variant B = 原則bullet + 人物ブロックに『話題との関係(contact_point_ja)』行を追加。"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import er005_cost_logger as cl
import er121_family_y_text_core_01 as tc

OUT = "er121_output/family_y_intro_trial_01/surname"
THEME = "docs/research/FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01/theme_packages/surname_choice_package_01.json"
RUN = "er121_output/family_y_production_01/surname_choice/run_02"
PRINCIPLE = ("- 【人物紹介の一般化原則(Trial)】紹介では、その人物の一般的な属性(親・父親・母親・職業・年齢など)を機械的に使わず、"
             "今回の話題に対して『どんな立場・経験から話すのか』を最優先で伝える。親であることなどの属性は、その発言の立場を理解するうえで重要な場合だけ使う。"
             "【人物】欄の役割名をそのまま写さない。属性を削るだけで終わらせず、聞き手がその人の立場を一度で理解できる言い方にする。根拠のない設定は足さない。\n")


GUARD_C = ("- 【事実の範囲(Trial追加)】紹介に書く立場・経験は、【人物】欄にあることだけ。欄に書かれていない時期・きっかけ・順序(例: 結婚を機に、結婚したときに)は足さない。"
           "迷ったら、欄にある言葉(婿養子になって、妻の家の苗字になった等)に沿って書く。\n")


GUARD_D = ("- 【時期の表現を使わない(Trial追加)】『結婚して』『結婚を機に』『結婚したときに』など、いつ・どのきっかけで姓が変わったかを示す言い方は書かない(欄に時期の裏付けがない)。"
           "姓についての立場は、欄にある言葉(婿養子になって、妻の家の苗字になった、息子が相手の姓を名乗る等)で書く。\n")


def person_block_b(slot, sheets, voices):
    base = tc.person_block(slot, sheets, voices)
    cp = sheets[slot]["contact_point_ja"]
    return base.replace("\n  暮らしの様子:", f"\n  話題との関わり: {cp}\n  暮らしの様子:", 1)


def build(variant, theme, voices, parts, spec):
    pb = tc.person_block if variant == "A" else person_block_b
    principle = PRINCIPLE + (GUARD_C if variant == "C" else "") + (GUARD_D if variant == "D" else "")
    persons = "\n\n".join(pb(s, theme["sheets"], voices) for s in tc.SLOTS)
    premise, _s, _src = tc.lead_inputs(theme)
    ut = parts["user_template"].replace("【書き方】\n", "【書き方】\n" + PRINCIPLE, 1)
    assert PRINCIPLE in ut
    return (ut.replace("@@PREMISE@@", premise).replace("@@PERSONS@@", persons)
            .replace("@@CLAIM_WORDS@@", spec["claim_prompt"]).replace("@@OBJECT_EXAMPLES@@", spec["object_prompt"]))


VARIANTS = tuple(sys.argv[1].split(",")) if len(sys.argv) > 1 else ("A", "B")


def main(n_samples=int(os.environ.get("N_SAMPLES", "2"))):
    os.makedirs(OUT, exist_ok=True)
    cl.install(f"{OUT}/cost_log.jsonl")
    import er003_v1_en_direct_vfl_01_generate as vfl01
    client = vfl01.get_client()
    theme = tc.load_theme_package(THEME)["theme"]
    parts = tc.load_article_prompt("intro")
    art = open(f"{RUN}/text/article_assembled.md", encoding="utf-8").read()
    voices = {}
    blocks = [b.strip() for b in re.split(r"\n\s*\n", art.strip())]
    for i, s in enumerate(tc.SLOTS):
        voices[s] = blocks[2 + i].split("\n", 1)[1].strip()
    spec = tc.intro_spec(theme)
    res = {}
    for variant in VARIANTS:
        prompt = build(variant, theme, voices, parts, spec)
        open(f"{OUT}/prompt_{variant}.txt", "w", encoding="utf-8").write(prompt)
        for k in range(n_samples):
            resp = tc.chat(client, route_key="FAMILY_Y_PERSONA_INTRO", user=prompt, developer=parts["developer"], schema=tc.INTRO_SCHEMA, stage=f"trial_intro_{variant}{k+1}")
            raw = tc._json_resp(resp, "trial_intro")
            fin, chk = {}, {}
            for s in tc.SLOTS:
                f, sym = tc._fin(raw[s])
                fin[s] = f
                chk[s] = tc.check_intro(f, s, voices[s], spec)
            res[f"{variant}{k+1}"] = {"intros": fin, "check": chk, "model": getattr(resp, "model", None), "response_id": getattr(resp, "id", None)}
            print(variant, k + 1, json.dumps(res[f"{variant}{k+1}"], ensure_ascii=False), flush=True)
    json.dump(res, open(f"{OUT}/ja_candidates_{''.join(VARIANTS)}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()

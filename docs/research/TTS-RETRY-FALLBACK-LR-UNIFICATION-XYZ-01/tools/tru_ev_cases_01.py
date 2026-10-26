# -*- coding: utf-8 -*-
"""evidence case表(EVIDENCE_PLAN_01 §6 Lean 46case + Opus 4-c追加2本)。

slot = ブロック通算番号(元ブロック①②③=1〜3、LR block①'②'③'=4〜6。KP英語は①②=1,2、ENGLISH_LOCK③④=3,4)。
ng=統一judgeをNG化 / sub=Primary転写へ1語置換(LR駆動) / post_ng=減速後再検証をNG化 / dq=disfluency gateをNG化 / ja_ng=JA統一judgeをNG化。
E-S6(kill→resume)は各groupの最後に置く(killでgroup processが終了するため)。
"""
from tru_ev_core_01 import Plan

X_ROOT = "er019_output/family_x_audio_production_wiring_01"
Y_ROOT = "er121_output/family_y_production_01/redelivery_fee"
Z_ROOT = "er026_output/family_z_production_e2e_01/the_monkeys_paw"
ALL = "*"


def _p(**kw):
    return Plan(**{k: {ALL: v} for k, v in kw.items()})


R6 = [1, 2, 3, 4, 5, 6]


def C(fam, id_, level, scenario, leaf, policy, segments, plan=None, **kw):
    root, prefix = {"X": (X_ROOT, "coffee_prices"), "Y": (Y_ROOT, None), "Z": (Z_ROOT, None)}[fam]
    c = {"id": id_, "group": f"{fam}-{'Std' if level == 'a2' else 'Adv'}", "family": fam, "level": level, "scenario": scenario, "leaf": leaf,
         "policy": policy, "segments": segments, "plan": plan or Plan(), "root": root, "theme_prefix": prefix}
    c.update(kw)
    return c


EXPL_X = "a delay between a change happening and its effect being seen or felt"
EXPL_Y = "to seem fair or acceptable to someone"

CASES = [
    # ---------------- X Std (a2)
    C("X", "X-Std-1", "a2", "E-S1", "L3", "EN_LR_STD", ["topic_intro"], _p(ng=[1, 2])),
    C("X", "X-Std-2", "a2", "E-S2a", "L3", "EN_LR_STD", ["topic_intro"], _p(ng=[1, 2, 3], sub=[3])),
    C("X", "X-Std-3", "a2", "E-S2b", "L3", "EN_LR_STD", ["topic_intro"], _p(ng=R6, sub=[3])),
    C("X", "X-Std-4", "a2", "E-S1", "L4", "EN_LR_STD", ["in_one_line"], _p(ng=[1, 2])),
    C("X", "X-Std-5", "a2", "E-S2b", "L4", "EN_LR_STD", ["in_one_line"], _p(ng=[1, 2, 3, 4, 6], sub=[3], post_ng=[5])),
    C("X", "X-Std-6", "a2", "E-S1", "L7", "JA_STD", ["japanese_title"], _p(ja_ng=[1, 2])),
    C("X", "X-Std-7", "a2", "E-S3", "L7", "JA_STD", ["japanese_title"], _p(ja_ng=[1, 2, 3])),
    C("X", "X-Std-8", "a2", "E-S4", "L6", "KP_EN", ["kp1_en"], _p(ng=[1, 2]), kp="en"),
    C("X", "X-Std-9", "a2", "E-S4", "L6", "KP_EN", ["kp1_en"], _p(ng=[1, 2, 3, 4]), kp="en"),
    C("X", "X-Std-11", "a2", "E-N", "L3+L7", "EN_LR_STD+JA_STD", ["topic_intro", "japanese_title"]),
    C("X", "X-Std-12", "a2", "E-C1(Opus4-c a)", "L4", "EN_LR_STD", ["full_story_part1_k1"], _p(post_ng=[1]), chunk_gate=True),
    C("X", "X-Std-1b", "a2", "E-S1", "L3", "EN_LR_STD", ["topic_intro"], _p(ng=[1, 2]), title_override="Coffee Bean Prices Fall"),
    C("X", "X-Std-10", "a2", "E-S6", "L3", "EN_LR_STD", ["topic_intro"], _p(ng=[1, 2]), kill_in_cooldown=60),
    # ---------------- X Adv (b1b)
    C("X", "X-Adv-1", "b1b", "E-S1", "L1", "EN_LR_ADV", ["comment_1"], _p(ng=[1, 2])),
    C("X", "X-Adv-2", "b1b", "E-S2a", "L1", "EN_LR_ADV", ["comment_1"], _p(ng=[1, 2, 3], sub=[3])),
    C("X", "X-Adv-3c", "b1b", "E-S2b", "L1", "EN_LR_ADV", ["comment_1"], Plan(ng={ALL: R6}, sub={ALL: [3]}, sub_word={ALL: ["compares"]})),
    C("X", "X-Adv-4", "b1b", "E-S7", "L1", "EN_LR_ADV", ["comment_1"], _p(dq=[1, 2, 3])),
    C("X", "X-Adv-6", "b1b", "E-S2b", "L2", "EN_LR_ADV", ["in_one_line"], _p(ng=R6, sub=[3])),
    C("X", "X-Adv-7", "b1b", "E-S1", "L5", "KP_EXPL", ["kp1_explanation_en"], _p(ng=[1, 2]), kp="expl", expl_text=EXPL_X),
    C("X", "X-Adv-8", "b1b", "E-S3", "L5", "KP_EXPL", ["kp1_explanation_en"], _p(ng=[1, 2, 3]), kp="expl", expl_text=EXPL_X),
    C("X", "X-Adv-9", "b1b", "E-X5", "L5", "KP_EXPL", ["kp1_explanation_en", "kp2_explanation_en", "kp3_explanation_en"], _p(), kp="expl_min",
      expl_texts=["a delay between a change happening and its effect being seen or felt", "to become visible or noticeable in a place or situation",
                  "to become lower, especially in price or amount"]),
    C("X", "X-Adv-10", "b1b", "E-S4", "L6", "KP_EN", ["kp1_en"], _p(ng=[1, 2]), kp="en"),
    C("X", "X-Adv-11", "b1b", "E-S4", "L6", "KP_EN", ["kp1_en"], _p(ng=[1, 2, 3, 4]), kp="en"),
    C("X", "X-Adv-13", "b1b", "E-N", "L1", "EN_LR_ADV", ["topic_intro", "comment_1"]),
    C("X", "X-Adv-14", "b1b", "E-S1(Opus4-c b: Voice=Charon)", "L1", "EN_LR_ADV", ["preview"], _p(ng=[1, 2])),
    C("X", "X-Adv-14b", "b1b", "E-S1(Opus4-c b: Voice=Charon・再実行)", "L1", "EN_LR_ADV", ["preview"], _p(ng=[1, 2])),
    C("X", "X-Adv-15", "b1b", "E-S0(②PASS・待機なし)", "L1", "EN_LR_ADV", ["comment_1"], _p(ng=[1])),
    C("X", "X-Adv-16", "b1b", "E-S6(R-5: LR block内kill)", "L2", "EN_LR_ADV", ["in_one_line"], _p(ng=[1, 2, 3, 4, 5], sub=[3]), kill_in_cooldown=250),
    C("X", "X-Adv-12", "b1b", "E-S6", "L1", "EN_LR_ADV", ["comment_1"], _p(ng=[1, 2]), kill_in_cooldown=60),
    # ---------------- Y Std
    C("Y", "Y-Std-1", "a2", "E-S2b", "L3", "EN_LR_STD", ["topic_intro"], _p(ng=R6, sub=[3])),
    C("Y", "Y-Std-2", "a2", "E-S1", "L7", "JA_STD", ["japanese_title"], _p(ja_ng=[1, 2])),
    C("Y", "Y-Std-2b", "a2", "E-S1", "L7", "JA_STD", ["japanese_title"], _p(ja_ng=[1, 2])),
    C("Y", "Y-Std-3", "a2", "E-S4", "L6", "KP_EN", ["kp1_en"], _p(ng=[1, 2]), kp="en"),
    C("Y", "Y-Std-4", "a2", "E-S1+YGate", "L4", "EN_LR_STD", ["y_voice_1"], _p(ng=[1, 2])),
    C("Y", "Y-Std-6", "a2", "E-STOP", "L3", "EN_LR_STD", ["topic_intro"], _p(ng=[1, 2]), stop_in_cooldown=40),
    C("Y", "Y-Std-4b", "a2", "E-S1+YGate", "L4", "EN_LR_STD", ["y_voice_1"], _p(ng=[1, 2])),
    C("Y", "Y-Std-5", "a2", "E-N", "L3+L7", "EN_LR_STD+JA_STD", ["topic_intro", "japanese_title"]),
    # ---------------- Y Adv
    C("Y", "Y-Adv-1", "b1b", "E-S2a", "L1", "EN_LR_ADV", ["comment_1"], _p(ng=[1, 2, 3], sub=[3])),
    C("Y", "Y-Adv-2", "b1b", "E-S1", "L5", "KP_EXPL", ["kp1_explanation_en"], _p(ng=[1, 2]), kp="expl", expl_text=EXPL_Y),
    C("Y", "Y-Adv-3", "b1b", "E-S4", "L6", "KP_EN", ["kp1_en"], _p(ng=[1, 2]), kp="en"),
    C("Y", "Y-Adv-4", "b1b", "E-S2a+YGate", "L2", "EN_LR_ADV", ["y_voice_1"], _p(ng=[1, 2, 3], sub=[3])),
    C("Y", "Y-Adv-4b", "b1b", "E-S2a+YGate", "L2", "EN_LR_ADV", ["y_voice_1"], Plan(ng={ALL: [1, 2, 3]}, sub={ALL: [3]}, sub_word={ALL: ["notice"]})),
    C("Y", "Y-Adv-5", "b1b", "E-N", "L1", "EN_LR_ADV", ["topic_intro", "comment_1"]),
    # ---------------- Z Std
    C("Z", "Z-Std-1", "a2", "E-S2b", "L4", "EN_LR_STD", ["full_story_part1_c14"], _p(ng=R6, sub=[3])),
    C("Z", "Z-Std-2", "a2", "E-S1(L8 ctx)", "L8", "Z_DLG_CTX", ["full_story_part1_c13"], _p(ng=[1, 2]), ctx=True),
    C("Z", "Z-Std-4", "a2", "E-S1", "L7", "JA_STD", ["japanese_title"], _p(ja_ng=[1, 2])),
    C("Z", "Z-Std-5", "a2", "E-S4", "L6", "KP_EN", ["kp1_en"], _p(ng=[1, 2])),
    C("Z", "Z-Std-6", "a2", "E-S2a(U-06)", "L3", "EN_LR_STD", ["topic_intro_en"], _p(ng=[1, 2, 3], sub=[3])),
    C("Z", "Z-Std-8", "a2", "E-STOP", "L3", "EN_LR_STD", ["topic_intro_en"], _p(ng=[1, 2]), stop_in_cooldown=40),
    C("Z", "Z-Std-7", "a2", "E-N", "L3+L7", "EN_LR_STD+JA_STD", ["topic_intro_en", "japanese_title"]),
    # ---------------- Z Adv
    C("Z", "Z-Adv-1", "b1b", "E-S2b", "L2", "EN_LR_ADV", ["full_story_part1_c14"], _p(ng=R6, sub=[3])),
    C("Z", "Z-Adv-2", "b1b", "E-S1(L8 ctx,減速後NG)", "L8", "Z_DLG_CTX", ["full_story_part1_c15"], Plan(post_ng={ALL: [1]}, ng={ALL: [2]}, by_count=True), ctx=True),
    C("Z", "Z-Adv-3", "b1b", "E-S3(L8 ctx)", "L8", "Z_DLG_CTX", ["full_story_part1_c15"], _p(ng=[1, 2, 3]), ctx=True),
    C("Z", "Z-Adv-3b", "b1b", "E-S3(L8 ctx・減速後NG×3でHRQ)", "L8", "Z_DLG_CTX", ["full_story_part1_c15"], Plan(post_ng={ALL: [1, 2, 3]}, by_count=True), ctx=True),
    C("Z", "Z-Adv-4", "b1b", "E-S2a(U-06)", "L1", "EN_LR_ADV", ["topic_intro_en"], _p(ng=[1, 2, 3], sub=[3])),
    C("Z", "Z-Adv-5", "b1b", "E-S1", "L5", "KP_EXPL", ["kp1_explanation_en"], _p(ng=[1, 2])),
    C("Z", "Z-Adv-6", "b1b", "E-S4", "L6", "KP_EN", ["kp1_en"], _p(ng=[1, 2])),
    C("Z", "Z-Adv-8", "b1b", "E-N", "L1", "EN_LR_ADV", ["topic_intro_en", "comment_1"]),
]

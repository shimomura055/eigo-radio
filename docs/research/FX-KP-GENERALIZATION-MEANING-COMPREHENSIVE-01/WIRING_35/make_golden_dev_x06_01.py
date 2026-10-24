"""DEV harness(er112_kp_gm_trial_06.build_x_message06 / x06_schema / G.M_DEVELOPER)の出力を、Production testのgolden fixtureとして保存する。
Production側(er003_key_words_gloss_alignment)はer112をimportしない。本scriptはDEV側の出力をfixture化するだけ(API 0)。
再生成: py docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/WIRING_35/make_golden_dev_x06_01.py
"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *([".."] * 4)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import er112_kp_gm_trial_06 as T6        # noqa: E402
import er112_kp_gm_trial_04_gen as G     # noqa: E402
import er003_key_words_gloss_alignment as ga  # noqa: E402

ARTICLE = ("The commuters said the plan did not work out. Each morning someone's bag blocked the aisle, and nobody wanted to speak up. "
           "In the end the railway had to draw a line between quiet coaches and the rest of the train.")


def item(rank, disp, kp, sent, reason=None):
    d = {"rank": rank, "display_phrase": disp, "key_phrase": kp, "used_form": kp, "japanese_gloss": None,
         "source_sentence": sent, "fulltext_source_ref": {"seq": rank}}
    if reason:
        d["normalization_reason"] = reason
    return d


A = item(1, "draw a line", "draw a line", "the railway had to draw a line between quiet coaches and the rest of the train.")
B = item(2, "work out", "work out", "The commuters said the plan did not work out.")
P = item(3, "block your bag", "block someone's bag", "Each morning someone's bag blocked the aisle.",
         reason=ga.PERSON_NORMALIZATION_REASON)
P2 = item(4, "speak up", "speak up", "nobody wanted to speak up.")

PRIOR = {2: {"gloss": "うまくいかなかった", "reasons": ["meaning_stage_fields_invalid", "括弧禁止違反"]},
         3: {"gloss": "あなたのかばんをふさぐ", "reasons": ["人称"]}}

cases = {
    "plain_noprior": {"targets": [A, B], "prior": None},
    "plain_prior": {"targets": [A, B, P2], "prior": PRIOR},
    "person_noprior": {"targets": [A, P], "prior": None},
    "person_prior": {"targets": [B, P, P2], "prior": PRIOR},
}
out = {"developer": G.M_DEVELOPER, "schema": T6.x06_schema(), "article": ARTICLE, "cases": {}}
for k, c in cases.items():
    msg = T6.build_x_message06(c["targets"], ARTICLE, prior=c["prior"])
    out["cases"][k] = {"targets": c["targets"], "prior": c["prior"], "message": msg}
dst = os.path.join(os.path.dirname(__file__), "golden_dev_x06_messages_01.json")
with open(dst, "w", encoding="utf-8", newline="\n") as f:
    json.dump(out, f, ensure_ascii=False, indent=1, sort_keys=False)
print("wrote", dst, {k: len(v["message"]) for k, v in out["cases"].items()})

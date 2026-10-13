# -*- coding: utf-8 -*-
"""er072検証。API呼出なし(mockのみ)。"""
import er072_melos_preview_std_adv_3take_01 as m

passed = 0


def check(name, cond):
    global passed
    assert cond, name
    passed += 1
    print("PASS", name)


inp = m.build_inputs()
inp["adv_text"] = inp["w62"].rd(inp["w62"].level_text_path(m.RUN, "b1b"))
v = m.verify(inp)
check("Std prompt sha == er070 sent prompt", v["std_matches_er070"])
check("Adv prompt == run_support_adv(mock) preview prompt", v["adv_matches_production_path"])
check("Std Comment 1/2 embedded", v["std_comments_embedded"])
check("Adv Comment 1/2 embedded", v["adv_comments_embedded"])
check("Adv mock path: only comment3 + preview calls (2)", v["adv_mock_calls_total"] == 2)
check("reasoning effort high both", v["reasoning_effort_std"] == "high" and v["reasoning_effort_adv"] == "high")
check("no leftover placeholders", "{comment_" not in inp["std"][2] and "{comment_" not in inp["adv"][2])
print(f"ALL PASS {passed}")

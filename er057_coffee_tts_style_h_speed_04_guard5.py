import sys, json, hashlib, os
R = os.path.dirname(os.path.abspath(__file__)); O = os.path.join(R, "er057_output", "coffee_tts_style_h_speed_04", "round5")
F = list(json.load(open(os.path.join(R, "er057_output/coffee_tts_style_h_speed_02/state_guard_pre.json"))).keys())
h = {f: hashlib.sha256(open(os.path.join(R, f), "rb").read()).hexdigest() for f in F}
if sys.argv[1] == "pre": json.dump(h, open(os.path.join(O, "state_guard_pre_r5.json"), "w"), indent=1)
else:
    pre = json.load(open(os.path.join(O, "state_guard_pre_r5.json")))
    json.dump({"post": h, "unchanged": {f: pre[f] == h[f] for f in F}, "all_unchanged": all(pre[f] == h[f] for f in F)}, open(os.path.join(O, "state_guard_r5.json"), "w"), indent=1)
    print(all(pre[f] == h[f] for f in F))

# 7記事の切り出し机上表(API 0)。usage: python table7_01.py [label]
import json, sys
sys.path.insert(0, ".")
import er019_family_x_std_comment3_z_method_01 as m
B = "er019_output/family_x_audio_production_wiring_01/"
ARTS = ["ai_island_temple__run_form_prod_01", "coffee_prices__run_m2p0_n01_01", "moon_shrinking__run_ms_03",
        "small_bag__run_kpq_02", "uk_train_speaker_playback__run_nws_02", "tesla_spacex_merger_talks__run_nws_01",
        "paycheck_personality__run_pp_02"]
out = []; fb = 0
for a in ARTS:
    p = json.load(open(B + a + "/a2/parts.json", encoding="utf-8"))
    i = m.build_part3_excerpt(p["part3"])
    fb += 1 if i["fallback_no_excerpt"] else 0
    out.append({"article": a, "fallback": i["fallback_no_excerpt"], "passed_sentences": i["passed_sentence_count"],
                "cut_reason": i["cut_reason"], "excerpt": i["excerpt"], "cut_sentence": i["cut_sentence"]})
print(sys.argv[1] if len(sys.argv) > 1 else "", "fallback", fb, "/", len(ARTS))
for o in out:
    print(" -", o["article"], "FB" if o["fallback"] else "n=%d" % o["passed_sentences"], o["cut_reason"], "| cut:", (o["cut_sentence"] or "")[:90])
json.dump({"fallback_count": fb, "rows": out}, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1) if len(sys.argv) > 2 else None

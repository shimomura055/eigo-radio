s = open("er057_coffee_tts_style_h_speed_05_play_verify.py", encoding="utf-8").read()
s = s.replace("play_evidence_01.json", "play_evidence_04.json")
s = s.replace('print({k: v for k, v in o.items() if k != "plays"})', 'o["n01_std_t4_6_present"] = all(any(x["src"] == f"audio/N01_std_t{t}.mp3" for x in plays) for t in (4, 5, 6)); json.dump(out, open("er057_output/coffee_tts_style_h_speed_05_listen/play_evidence_04.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)\nprint({k: v for k, v in o.items() if k != "plays"})')
exec(compile(s, "pv04", "exec"))

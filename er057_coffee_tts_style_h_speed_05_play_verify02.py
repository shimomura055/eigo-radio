import re
s = open("er057_coffee_tts_style_h_speed_05_play_verify.py", encoding="utf-8").read()
s = s.replace("play_evidence_01.json", "play_evidence_02.json")
exec(compile(s, "pv02", "exec"))

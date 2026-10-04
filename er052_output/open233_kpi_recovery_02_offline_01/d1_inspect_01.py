import json, sys, re
sys.stdout.reconfigure(encoding="utf-8")
D = json.load(open("er052_output/open233_kpi_recovery_02_offline_01/d_type_dump_01.json", encoding="utf-8"))
r = D[0]; art = r["article"]
print(art)
print("-----")
i = art.find("Their job is visual")
print(repr(art[i-300:i+400]))
print(repr(r["fragments"][0]))
print("dev flags", r["flags"])

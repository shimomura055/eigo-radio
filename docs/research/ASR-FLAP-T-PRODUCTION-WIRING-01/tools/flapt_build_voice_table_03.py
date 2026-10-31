# 静的Voice表生成(API 0)。実行: PYTHONUTF8=1 <py> docs/research/ASR-FLAP-T-PRODUCTION-WIRING-01/tools/flapt_build_voice_table_03.py
import hashlib, json
T = "docs/research/ASR-FLAP-T-EQUIVALENCE-TRIAL-01/voice_probe_02.json"
P = "docs/research/ASR-FLAP-T-PRODUCTION-WIRING-01/voice_probe_03.json"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
MODEL = {"fl": "gemini-3.8-flash-lite-tts", "pro": "gemini-2.5-pro-preview-tts"}
t02 = json.load(open(T, encoding="utf8")); p03 = json.load(open(P, encoding="utf8"))
fast = {k: v["maintained"] for k, v in p03["speed_106"].items()}
slow6 = {k: (v["verdict"] == "FLAP_DEMONSTRATED") for k, v in t02["slow6"].items()}
rows = []
for k, v in t02["voices"].items():
    if k in p03["combos"]: continue          # 独立probe(03)で置換(Zephyr|pro/Schedar|pro。02は循環/clip不足)
    rows.append((k, v["verdict"] == "FLAP_DEMONSTRATED", f"{T}#voices[{k}]", sha(T), v["clips"]))
for k, c in p03["combos"].items():
    rows.append((k, c["judgement"] == "confirmed", f"{P}#combos[{k}]", sha(P), c["clips"]))
out = {"schema": "Voice,path,confirmed,evidence_ref,sha (+model_id/speed flags)", "note": "confirmed=false/未記載はfail-closed(従来NG)。fast106_confirmed=Z Adv dialogue 1.06x高速化後wavでもflap維持を確認済みか(未probe=false)。slow6_confirmed=Std 6%減速後の維持確認済みか(Trial)。table sha256はloader側で算出。", "rows": []}
for k, conf, ref, s, n in sorted(rows):
    voice, path = k.split("|")
    out["rows"].append({"Voice": voice, "path": path, "model_id": MODEL[path], "confirmed": conf, "evidence_ref": ref, "sha": s, "probe_clips": n,
                        "fast106_confirmed": bool(conf and fast.get(k, False)), "slow6_confirmed": bool(conf and slow6.get(k, False))})
json.dump(out, open("er139_flapt_voice_table_01.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
for r in out["rows"]: print(r["Voice"], r["path"], r["confirmed"], r["fast106_confirmed"], r["slow6_confirmed"], r["probe_clips"])

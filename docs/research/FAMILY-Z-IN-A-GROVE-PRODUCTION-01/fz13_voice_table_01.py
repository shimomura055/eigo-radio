# -*- coding: utf-8 -*-
"""FAMILY-Z-IN-A-GROVE-PRODUCTION-01 委任_13: clip別 (実送信voice[cost_logのtts_voice_sent]・話者ラベル・テキスト・wav sha) 一覧(API 0、読取のみ)。
使い方: py fz13_voice_table_01.py before|after。before=*.pre_fz13.json(修正前plan)とtts_generation_results.pre_fz13.json(あれば)、after=現行。
cost_logは該当segmentの最後に成功したgemini TTS行のvoiceを採る。narrator clipに引用符(発言本文)が含まれていれば『NG(発言混入)』と判定する。"""
import json, sys, os, re, hashlib
RUN = "er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01"
DESIGN = {"woodcutter": "Algieba", "monk": "Schedar", "constable": "Fenrir", "old_woman": "Zephyr", "tajomaru": "Orus", "masago": "Kore", "takehiro": "Puck", "narrator": "Aoede"}
LABEL = sys.argv[1] if len(sys.argv) > 1 else "after"
SUF = ".pre_fz13" if LABEL == "before" else ""
rows = [json.loads(l) for l in open(f"{RUN}/cost_log.jsonl", encoding="utf-8") if l.strip()]
sent = {}
for r in rows:
    if r.get("provider") == "gemini" and r.get("tts_voice_sent") and r.get("success", True):
        sent.setdefault((r["stage"], r["segment"]), []).append(r["tts_voice_sent"])
out = []
bad = 0
for lv, stage in (("a2", "tts_a2"), ("b1b", "tts_b1b")):
    d = json.load(open(f"{RUN}/{lv}/audit/tts_generation_results{SUF if os.path.exists(f'{RUN}/{lv}/audit/tts_generation_results{SUF}.json') else ''}.json", encoding="utf-8"))["segments"]
    plan = json.load(open(f"{RUN}/segment_plan_{lv}{SUF}.json", encoding="utf-8"))
    out.append(f"\n### {lv} ({'Standard' if lv == 'a2' else 'Advanced'})\n\n| clip | 話者(plan) | 設計voice | 結果voice | 実送信voice(最終) | 一致 | 語数 | wav sha8 | text先頭 |\n|---|---|---|---|---|---|---|---|---|")
    for c in plan["clips"]:
        e = d.get(c["id"]) or {}
        s = sent.get((stage, c["id"]), [])
        wavp = f"{RUN}/{lv}/narration/{c['id']}.wav"
        sh = hashlib.sha256(open(wavp, "rb").read()).hexdigest()[:8] if os.path.exists(wavp) else "-"
        last = s[-1] if s else "(記録なし)"
        ok = "OK" if last == DESIGN[c["speaker"]] else ("(HR採用wav)" if not s else "NG")
        if c["speaker"] == "narrator" and '"' in c["text"]:
            ok = "NG(narratorに発言混入)"
        if ok.startswith("NG"):
            bad += 1
        out.append(f"| {c['id']} | {c['speaker']} | {DESIGN[c['speaker']]} | {e.get('voice')} | {last} | {ok} | {c['word_count']} | {sh} | {c['text'][:48].replace('|', '/')} |")
print("\n".join(out))
print(f"\n不一致(実送信voice != 設計voice): {bad}", file=sys.stderr)

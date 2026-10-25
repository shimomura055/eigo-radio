# Phase 3 有料結果の評価 (委任_03)。phase3_run/usage_log.jsonl の実転写を、v1(凍結)と現行に通す。API 0(socket guard)。
# 出力: eval_phase3_02.out.json / 標準出力。判定にLLMは使わない。
import collections, json, sys
sys.path.insert(0, ".")
sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
import eval_common_01 as E
D = "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/"
E.api0_guard_on()
log = [json.loads(l) for l in open(D + "phase3_run/usage_log.jsonl", encoding="utf8")]
MOON = "月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密"
out = {}

def judge(canon, ptext, stext):
    """Primary転写(必須) + Secondary転写(任意)の最終判定。base=現行 / v1=Primary差替+A4(a) / v1b=A4(b)も含む(新仕様候補)。"""
    b = E.primary_stage(canon, ptext, False) if ptext else {"primary_pass": False, "label": None, "state": None, "warnings": []}
    c = E.primary_stage(canon, ptext, True) if ptext else b
    sb = a4a = a4b = False; v1s = None
    if stext:
        sb, a4a, a4b, v1s = E.secondary_accept_kind(canon, stext)
    base_pass = bool(b["primary_pass"] or sb)
    v1_pass = bool(c["primary_pass"] or sb or a4a)
    v1b_pass = bool(v1_pass or a4b)
    return {"base_pass": base_pass, "v1_pass": v1_pass, "v1_incl_a4b_pass": v1b_pass,
            "primary_base": [b["primary_pass"], b["label"], b["state"]], "primary_v1": [c["primary_pass"], c["label"], c["state"], c["warnings"]],
            "sec": {"base": sb, "a4a": a4a, "a4b": a4b}, "v1why": c["v1"].why if c.get("v1") else None, "v1cause": c["v1"].cause if c.get("v1") else None}

# ---- A1/A2/A3/O1 (月題・Melos) ----
moon = []
for r in log:
    if r["stage"] in ("A1_azure_moon", "A3_azure_flip", "A2_openai_moon_x3", "O1_format_prompt"):
        item = r["item"]
        if r["stage"] == "A3_azure_flip" and item.startswith("preview"):
            continue
        a = r["stage"]
        if a in ("A1_azure_moon", "A3_azure_flip"):
            j = judge(MOON, None, r["text"])
        else:
            j = judge(MOON, r["text"], None)
        moon.append({"stage": a, "item": item, "text": r["text"], **j})
out["moon"] = moon
print("== moon ==")
for m in moon:
    print(m["stage"], m["item"][:40], "|", m["text"][:30], "| base", m["base_pass"], "v1", m["v1_pass"], "v1+a4b", m["v1_incl_a4b_pass"], m["primary_v1"][1])
# A3 Melos preview: Azure転写
mel = [r for r in log if r["stage"] == "A3_azure_flip" and r["item"].startswith("preview")]
p4 = json.load(open(D + "eval_api0_v1_01.out.json", encoding="utf8"))["p4"]["flips"]
for r in mel:
    cand = [f for f in p4 if "preview_attempt2" in f["file"]]
    if cand:
        canon = cand[0]["canon"]
        j = judge(canon, cand[0]["text"], r["text"])
        out["melos_preview"] = {"canon": canon, "primary_text": cand[0]["text"], "azure_text": r["text"], **j}
        print("== melos preview ==", canon[:40], "| P:", cand[0]["text"][:40], "| A:", r["text"][:60]); print(j)

# ---- N-3 ----
clips = json.load(open(D + "n3_clips_01.json", encoding="utf8"))
asr = {r["item"]: r for r in log if r["stage"] == "N3_asr"}
rows = []
for c in clips:
    r = asr.get(c["id"])
    if not r:
        continue
    j = judge(c["canonical"], r["openai_text"], r["azure_text"])
    rows.append({"id": c["id"], "type": c["type"], "canon": c["canonical"], "tts_input": c["tts_input"], "openai": r["openai_text"], "azure": r["azure_text"], **j})
out["n3"] = rows
print("== N-3 ==", len(rows), "clips")
for r in rows:
    print(r["id"], r["type"][:18], "|", r["canon"], "|", r["openai"], "|", r["azure"], "| base", r["base_pass"], "v1", r["v1_pass"], "v1+a4b", r["v1_incl_a4b_pass"])
inc = [r for r in rows if r["v1_pass"] and not r["base_pass"]]
inc_b = [r for r in rows if r["v1_incl_a4b_pass"] and not r["base_pass"]]
exist = [r for r in rows if r["base_pass"]]
print("N-3 incremental false PASS (v1; includes A4a):", [r["id"] for r in inc])
print("N-3 incremental incl A4(b) (new-spec candidate):", [r["id"] for r in inc_b])
print("N-3 existing false PASS (report only):", [(r["id"], r["type"][:14]) for r in exist])
json.dump(out, open(D + "eval_phase3_02.out.json", "w", encoding="utf8"), ensure_ascii=False, indent=1, default=str)
E.api0_guard_off()

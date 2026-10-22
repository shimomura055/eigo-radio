# -*- coding: utf-8 -*-
"""KPMG Trial①機械検証(API 0)+最小化指標。規則: 厳密本文一致(大小文字・引用符・末尾句読点のみ正規化)+5語以内+自己申告語数一致。
placeholder(~/A/B/someone等)や活用形差が出た場合は一般化wildcardを使わず『Prompt逸脱/本文不一致』として別記録(厳格不合格)。KP6M検証ロジック(er098 validate)は無改変でimportのみ。"""
import json, re, sys, statistics
from pathlib import Path
import er101_kp_prompt_min_gen_trial_02_common as K
import er098_kp_six_model_trial_01_validate as V
C = K.C

def vphrase(phrase, art, art_n):
    r = V.validate_phrase(phrase, art, art_n)
    if r["match_type"] in ("B_GEN_UNIQUE", "B_GEN_AMBIGUOUS"):
        r["prompt_deviation_placeholder"] = True
        r["match_type_wildcard"] = r["match_type"]; r["match_type"] = "NG_PLACEHOLDER_DEVIATION"
    return r

def validate_set(cands, art):
    art_n = V.norm(art); out = []; seen = {}
    for i, c in enumerate(cands):
        v = vphrase(c["phrase"], art, art_n)
        v["rank"] = i + 1; v["self_count"] = c.get("self_count")
        v["self_count_mismatch"] = (c.get("self_count") is not None and c["self_count"] != v["words_actual"])
        k = V.clean_cand(c["phrase"]); v["duplicate_of"] = seen.get(k); seen.setdefault(k, i + 1)
        v["strict_pass"] = bool(v["within_5"] and v["match_type"] == "A_EXACT" and v["duplicate_of"] is None)
        out.append(v)
    return out

def main():
    out = K.OUT; man = json.loads((out / "inputs" / "manifest_from_kp6m.json").read_text(encoding="utf8"))
    units = {u["unit_id"]: u for u in man["units"] if u.get("copy_path")}
    prev = json.loads((C.ROOT / "er098_output/kp_six_model_trial_01/validation.json").read_text(encoding="utf8"))
    res = {"generated_by": "er101_kp_prompt_min_gen_trial_02_validate.py", "sets": []}
    for rp in sorted((out / "runs").glob("*/*.json")):
        d = json.loads(rp.read_text(encoding="utf8")); u = units[d["unit_id"]]
        art = (C.ROOT / u["copy_path"]).read_text(encoding="utf8")
        if not d.get("ok"):
            res["sets"].append(dict(source=d["model_key"], unit_id=d["unit_id"], status="TECH_FAIL", candidates=[])); continue
        pinfo = {}; fg = PARSE_OVERRIDES.get("%s/%s" % (d["model_key"], d["unit_id"]))
        cands = C.parse_candidates(d["response_text"], pinfo, force_group=fg)
        if fg is not None: pinfo["override_group"] = fg
        key = "%s/%s" % (d["model_key"], d["unit_id"])
        if key in FINAL_LISTS:
            cands = [dict(phrase=p_, self_count=c_, line="(手動確定リスト)", rejected=False) for p_, c_ in FINAL_LISTS[key]]; pinfo["manual_final_list"] = True
        for (k_, rk), ph_ in PHRASE_OVERRIDES.items():
            if k_ == key:
                pinfo.setdefault("phrase_overrides", []).append(dict(rank=rk, parsed=cands[rk - 1]["phrase"], final=ph_)); cands[rk - 1]["phrase"] = ph_
        pinfo["draft_over5_mention"] = bool(re.search(r"(?<![\d])(?:[6-9]|1\d)\s*語", d["response_text"]))
        res["sets"].append(dict(source=d["model_key"], unit_id=d["unit_id"], status="OK", n_parsed=len(cands), finish=d.get("finish"), model_returned=d.get("model_returned"),
                                parse_info=pinfo, candidates=validate_set(cands, art)))
    (out / "validation.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf8")
    # 最小化指標(KP6M同モデルと並記)
    mm = {}
    pv = {}
    for s in prev["sets"]:
        pv.setdefault(s["source"], []).extend(c["words_actual"] for c in s["candidates"])
    for mk, m in K.MODELS.items():
        ws = [c["words_actual"] for s in res["sets"] if s["source"] == mk for c in s["candidates"]]
        pw = pv.get(m["prev_key"], [])
        mm[mk] = dict(n=len(ws), avg_words=round(statistics.mean(ws), 3), dist={k: ws.count(k) for k in range(1, 9)}, prev_n=len(pw), prev_avg_words=round(statistics.mean(pw), 3) if pw else None,
                      prev_dist={k: pw.count(k) for k in range(1, 9)},
                      strict=sum(c["strict_pass"] for s in res["sets"] if s["source"] == mk for c in s["candidates"]),
                      sets_lt5=sum(1 for s in res["sets"] if s["source"] == mk and len(s["candidates"]) < 5),
                      sets_gt5=sum(1 for s in res["sets"] if s["source"] == mk and len(s["candidates"]) > 5),
                      mismatch=sum(c["self_count_mismatch"] for s in res["sets"] if s["source"] == mk for c in s["candidates"]),
                      self_count_reported=sum(c["self_count"] is not None for s in res["sets"] if s["source"] == mk for c in s["candidates"]),
                      types={t: sum(1 for s in res["sets"] if s["source"] == mk for c in s["candidates"] if c["match_type"] == t) for t in sorted({c["match_type"] for s in res["sets"] for c in s["candidates"]})})
    (out / "minimization_metrics.json").write_text(json.dumps(mm, ensure_ascii=False, indent=1), encoding="utf8")
    print(json.dumps(mm, ensure_ascii=False, indent=1))
    for s in res["sets"]:
        for v in s["candidates"]:
            if not v["strict_pass"] or v["self_count_mismatch"]:
                print("VIOL", s["source"], s["unit_id"], v["rank"], repr(v["phrase"]), v["match_type"], "w=%s sc=%s" % (v["words_actual"], v["self_count"]))
        if s["status"] == "OK" and (s["parse_info"].get("multi_draft") or len(s["candidates"]) != 5): print("PARSE?", s["source"], s["unit_id"], len(s["candidates"]), s["parse_info"])

# 抽出の手動補正(モデル出力は無改変。モデル自身が取消/修正して最終提示した内容を採用。TRIAL_RESULT_02.md 8節に記載)
PARSE_OVERRIDES = {"n4_claude-haiku-5-5/A_Advanced": 0}      # 表(本文該当箇所付き)が選定結果、後続の箇条書きは解説(要約表現)
PHRASE_OVERRIDES = {("n2_gemini-3.1-flash-lite/A_Standard", 3): "in the ring",          # 草稿7語を出力後『修正→in the ring』
                    ("n2_gemini-3.1-flash-lite/G_Advanced", 3): "gave back their gains"}  # 草稿6語を出力後『修正』
FINAL_LISTS = {"n3_gemini-3.5-flash-lite/D_Standard": [("boredom became fuel", 2), ("see others suffer", 3), ("at random", 2), ("how the stage is set", 5), ("brief boredom", 2)]}  # 取消線相当の3番が重複番号
if __name__ == "__main__":
    sys.exit(main())

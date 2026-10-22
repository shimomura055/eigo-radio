# -*- coding: utf-8 -*-
"""FAMILY-X-KP-SELECTION-SIX-MODEL-COMPARISON-TRIAL-01 委任_01: 入力抽出(API 0)。
7記事x2レベルの本文・既存Production KP・既存KP選定実費を inputs/manifest.json へ保存する。読み取り専用。"""
import json, hashlib, subprocess, sys, os
from pathlib import Path
ROOT = Path(__file__).resolve().parent
OUT = ROOT / "er098_output" / "kp_six_model_trial_01" / "inputs"
AW = "er019_output/family_x_audio_production_wiring_01/"
# (id, 記事名, 本文source_dir, audio/KP dir, 備考)
ARTICLES = [
 ("A", "コーヒー価格の高騰", "er019_output/coffee_prices/run_v5_ms_01", AW + "coffee_prices__run_m2p0_n01_01", "audio wiring 最新(2026-10-21)=M2P0 db_hybrid KP。試聴 user_test/coffee_m2p0_n01_final_03"),
 ("B", "給料が上がると、性格も変わる？", "er019_output/paycheck_personality/run_pp_02", AW + "paycheck_personality__run_pp_02", "run_pp_02(再制作版)を使用。旧run_pp_01も存在(使用せず)"),
 ("C", "漫画のキャラクターとAIで会話(byUs)", "er019_output/manga_ai_chat_byus/run_byus_01", AW + "manga_ai_chat_byus__run_byus_01", "OPEN-431 CLOSED_USER_ACCEPTED"),
 ("D", "退屈と攻撃性の関係", "er019_output/boredom_aggression/run_bape_01", AW + "boredom_aggression__run_bape_01", "OPEN-408 CLOSED_USER_ACCEPTED"),
 ("E", "Meta関連の記事", "er019_output/meta/run_regen_01", AW + "meta__run_regen_01", "regen_01(最新のMeta audio wiring、user_test/meta_regen_01_asr_check)。run_03/run_sol61_01は本文なし/旧"),
 ("F", "中東情勢(イエメン・サウジアラビア)", "er019_output/middle_east_yemen_saudi/run_mey_02", AW + "middle_east_yemen_saudi__run_mey_02", "OPEN-416 USER_ACCEPTED_FINAL(完成版=run_mey_02)"),
 ("G", "ホルムズ海峡関連(旧記事)", "er019_output/family_x_b3_diversity_trial_01/hormuz/run_02", AW + "family_x_b3_diversity_trial_01/hormuz__run_02", "旧記事。試聴page user_test/flash_lite_family_x_02_hormuz が参照するrun_02。KPはgpt-5.6-luna世代(旧)、レベル名はFamily X内部名a2/b1b"),
]
LEVELS = [("a2", "Standard"), ("b1b", "Advanced")]  # er019_family_x_audio_production_runner_01.py:742,1205 (A2=Standard / B1B=Advanced)

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def git_last(p):
    try:
        r = subprocess.run(["git", "log", "-1", "--format=%h", "--", p], cwd=ROOT, capture_output=True, text=True)
        return r.stdout.strip() or "untracked_or_uncommitted"
    except Exception as e:
        return "git_error:%s" % e
def jl(p):
    d = {}
    for ln in Path(p).read_text(encoding="utf8").splitlines():
        ln = ln.strip()
        if ln:
            j = json.loads(ln)
            if j.get("response_id"):
                d[j["response_id"]] = j
    return d
PR = {"gpt-6-luna": (0.10, 0.01, 0.50), "gpt-5.6-luna": (0.20, 0.02, 1.20)}
def cost_jpy(u):
    p = PR.get(u.get("model_id"))
    if not p: return None
    it, ct, ot = u.get("input_tokens") or 0, u.get("cached_input_tokens") or 0, u.get("output_tokens") or 0
    return round(((max(it - ct, 0) * p[0] + ct * p[1] + ot * p[2]) / 1e6) * 160.0, 4)

def main():
    man = {"generated_by": "er098_kp_six_model_trial_01_extract.py", "levels_map": {"a2": "Standard", "b1b": "Advanced"},
           "levels_map_source": "er019_family_x_audio_production_runner_01.py:742,1205 (B1B=Advanced, A2=Standard)", "units": [], "missing": []}
    (OUT / "articles").mkdir(parents=True, exist_ok=True)
    for aid, name, src, kdir, note in ARTICLES:
        for lv, lvname in LEVELS:
            u = {"article_id": aid, "article_name": name, "level_internal": lv, "level": lvname, "unit_id": "%s_%s" % (aid, lvname), "note": note}
            ap = Path(ROOT / src / lv / "article.md")
            if not ap.exists():
                man["missing"].append({"unit": u["unit_id"], "what": "article.md", "path": str(ap)}); man["units"].append(u); continue
            txt = ap.read_text(encoding="utf8")
            copy = OUT / "articles" / ("%s_%s.txt" % (aid, lvname))
            copy.write_text(txt, encoding="utf8", newline="\n")
            u.update({"article_path": "%s/%s/article.md" % (src, lv), "article_sha256_file": sha(ap), "article_commit": git_last("%s/%s/article.md" % (src, lv)),
                      "article_chars": len(txt), "article_words": len(txt.split()), "copy_path": str(copy.relative_to(ROOT)).replace("\\", "/"), "copy_sha256": sha(copy), "kp_dir": kdir})
            kp = ROOT / kdir / lv / "key_phrases" / "keywords_canonicalized.json"
            if not kp.exists():
                man["missing"].append({"unit": u["unit_id"], "what": "keywords_canonicalized.json", "path": str(kp)})
            else:
                items = json.loads(kp.read_text(encoding="utf8"))["items"]
                u["kp_path"] = str(kp.relative_to(ROOT)).replace("\\", "/"); u["kp_sha256"] = sha(kp); u["kp_commit"] = git_last(u["kp_path"])
                u["production_kp"] = [{"rank": it.get("rank"), "key_phrase": it.get("key_phrase"), "display_phrase": it.get("display_phrase"), "source_span": it.get("source_span"),
                                       "role": it.get("key_phrase_role")} for it in items]
            sel = ROOT / kdir / lv / "key_phrases" / "key_phrases_db_hybrid" / "keywords_runtime_metadata.json"
            can = ROOT / kdir / lv / "key_phrases" / "canonicalization_runtime_metadata.json"
            ru = ROOT / kdir / "raw_usage_log.jsonl"
            cost = {"selector": "未確認", "canonicalization": "未確認"}
            usage_by_resp = jl(ru) if ru.exists() else {}
            if sel.exists():
                m = json.loads(sel.read_text(encoding="utf8"))
                cost["selector"] = {"model_id": m.get("model_id"), "cost_jpy_recorded": m.get("cost_jpy"), "usage": m.get("usage"), "response_id": m.get("response_id"),
                                    "attempts": len(m.get("attempts_detail") or []), "source": str(sel.relative_to(ROOT)).replace("\\", "/"), "kind": "実測(Production記録)"}
            elif kp.exists():
                m = json.loads((ROOT / kdir / lv / "key_phrases" / "keywords_runtime_metadata.json").read_text(encoding="utf8"))
                r = usage_by_resp.get(m.get("response_id"))
                if r:
                    cost["selector"] = {"model_id": r["model_id"], "cost_jpy_recomputed": cost_jpy(r), "usage": {k: r.get(k) for k in ("input_tokens", "output_tokens", "cached_input_tokens", "reasoning_tokens")},
                                        "response_id": m.get("response_id"), "source": kdir + "/raw_usage_log.jsonl", "kind": "実測token+単価で再計算(model=%s)" % r["model_id"]}
            if can.exists():
                m = json.loads(can.read_text(encoding="utf8"))
                r = usage_by_resp.get(m.get("response_id"))
                if r:
                    cost["canonicalization"] = {"model_id": r["model_id"], "cost_jpy_recomputed": cost_jpy(r), "usage": {k: r.get(k) for k in ("input_tokens", "output_tokens", "cached_input_tokens", "reasoning_tokens")},
                                                "response_id": m.get("response_id"), "source": kdir + "/raw_usage_log.jsonl"}
            u["production_cost"] = cost
            man["units"].append(u)
    (OUT / "manifest.json").write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf8")
    print("units", len(man["units"]), "missing", man["missing"])
    for u in man["units"]:
        print(u["unit_id"], u.get("article_words"), len(u.get("production_kp", [])), u.get("production_cost", {}).get("selector") and (u["production_cost"]["selector"] if isinstance(u["production_cost"]["selector"], str) else u["production_cost"]["selector"].get("cost_jpy_recorded", u["production_cost"]["selector"].get("cost_jpy_recomputed"))))
main()

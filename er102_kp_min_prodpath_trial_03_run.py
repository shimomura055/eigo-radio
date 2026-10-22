# -*- coding: utf-8 -*-
r"""FAMILY-X-KP-MINIMIZATION-PRODUCTION-PATH-TRIAL-03 委任_01: Trial専用ランナー。
Production関数列(sc.run_key_phrases: 選定[M2P0 db_hybrid]->canonicalization->gloss整合->Redundancy QA[+retry])を無改変のままimportして呼ぶ。
Trialプロセス内でのみ (1)KP_BACKEND_TELEMETRY_PATHをTrial out_dirへ (2)Arm Bのみbk.load_prompt_template()の戻りへ第3条を挿入
(3)m2_supply.build_m2_stage1_and_shortlistをpickleキャッシュ化(ArmA/Bで同一shortlist) (4)er005_cost_loggerをTrial logへinstall。
Productionファイル・Production run dir・Store・Production telemetryへは書かない。
使い方: .venv\Scripts\python.exe er102_kp_min_prodpath_trial_03_run.py --arm S|A|B --out er102_output/kp_min_prodpath_trial_03 --manifest er098_output/kp_six_model_trial_01/inputs/manifest.json --cap-jpy 45
  S=shortlist構築のみ(API 0、Production関数 build_m2_stage1_and_shortlist をそのまま呼ぶ)。A=現行template(無改変)。B=現行template+第3条。"""
import argparse, hashlib, json, os, pickle, sys, threading, time, traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
ROOT = Path(__file__).resolve().parent
os.chdir(ROOT); sys.path.insert(0, str(ROOT))

CLAUSE = ("学習ポイントの明確化と最小化（必須）：学ぶべき語彙・熟語・表現を明確にし、意味と自然さを保てる最短の形で抽出する。"
          "不要な目的語・修飾語・文脈は除く。5語は上限であり、目標ではない。短縮によって学習価値が失われる場合のみ、必要な語を残す。")
ANCHOR = "display_phraseは1〜5語にしてください。完全文、主語と有限動詞を持つ節、記事固有の長い説明は禁止です。"

def sha(s): return hashlib.sha256(s.encode("utf-8")).hexdigest()

def make_template_b(tmpl):
    assert tmpl.count(ANCHOR) == 1, "anchor not unique"
    return tmpl.replace(ANCHOR, ANCHOR + "\n\n" + CLAUSE, 1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=["S", "A", "B"]); ap.add_argument("--out", required=True)
    ap.add_argument("--manifest", required=True); ap.add_argument("--cap-jpy", type=float, default=45.0)
    ap.add_argument("--workers", type=int, default=4); ap.add_argument("--only", default=None)
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    man = json.loads(Path(a.manifest).read_text(encoding="utf-8"))
    import er003_v1_n3_01_scaffold_generate as sc
    import er003_b1_p2_keywords as bk
    import er030_key_phrase_db_hybrid_m2_supply_01 as m2s
    import er005_cost_logger as cl
    import er009_n1_routing_governance_10_actual_model_cost as pricing
    # (1) Production telemetryへ書かない
    sc.KP_BACKEND_TELEMETRY_PATH = str(out / ("telemetry_%s.jsonl" % a.arm))
    # (2) template
    tmpl_a = bk.load_prompt_template(); tmpl_b = make_template_b(tmpl_a)
    (out / "inputs").mkdir(exist_ok=True)
    (out / "inputs" / "template_A_current.txt").write_text(tmpl_a, encoding="utf-8")
    (out / "inputs" / "template_B_plus_clause3.txt").write_text(tmpl_b, encoding="utf-8")
    if a.arm == "B":
        orig = bk.load_prompt_template
        bk.load_prompt_template = lambda path=bk.PROMPT_TEMPLATE_PATH: make_template_b(orig(path))
    # (3) shortlist cache
    sl_dir = out / "shortlists"; sl_dir.mkdir(exist_ok=True)
    orig_build = m2s.build_m2_stage1_and_shortlist
    def cached_build(article_text, dbs, title):
        p = sl_dir / (sha(article_text)[:24] + ".pkl")
        if a.arm == "S":
            r = orig_build(article_text, dbs, title)
            with open(p, "wb") as f: pickle.dump(r, f)
            return r
        if not p.exists(): raise RuntimeError("shortlist cache missing: %s (先に --arm S)" % p)
        with open(p, "rb") as f: return pickle.load(f)
    m2s.build_m2_stage1_and_shortlist = cached_build
    # (4) cost logger (OpenAI Responses API usage)
    ulog = str(out / ("usage_%s.jsonl" % a.arm))
    if a.arm != "S": cl.install(ulog)
    units = man["units"]
    if a.only: units = [u for u in units if u["unit_id"] in a.only.split(",")]
    lock = threading.Lock()
    def spent():
        t = 0.0
        if os.path.exists(ulog):
            for ln in open(ulog, encoding="utf-8"):
                if ln.strip():
                    r = json.loads(ln)
                    if r.get("success"):
                        t += pricing.cost_jpy_for_call("openai", r.get("model_id"), r.get("input_tokens"), r.get("cached_input_tokens"), r.get("output_tokens"))
        return t
    def run(u):
        uid = u["unit_id"]
        if (out / "STOP").exists() or (out / "STOP_ALL").exists(): return (uid, "STOPPED")
        rdir = out / "runs" / a.arm / uid
        done = rdir / "result.json"
        if done.exists(): return (uid, "SKIP_EXISTS")
        if a.arm != "S" and spent() >= a.cap_jpy: return (uid, "CAP_REACHED")
        art_bytes = (ROOT / u["copy_path"]).read_bytes()
        assert hashlib.sha256(art_bytes).hexdigest() == u["copy_sha256"], uid
        text = art_bytes.decode("utf-8")
        lv = "b1b" if u["level"] == "Advanced" else "a2"
        proc = "B1_SUPPORT" if lv == "b1b" else "A2_SUPPORT"
        kp_dir = rdir / "key_phrases"; kp_dir.mkdir(parents=True, exist_ok=True)
        aid = "KPMP3_%s_%s" % (a.arm, uid)
        t0 = time.time()
        if a.arm == "S":
            import er030_key_phrase_db_hybrid_selector_01 as sel
            dbs = sel.core.load_group1_dbs(); title = sel.extract_article_title(text)
            r = m2s.build_m2_stage1_and_shortlist(text, dbs, title)
            res = {"status": "SHORTLIST_BUILT", "shortlist_total_count": r["shortlist_info"]["shortlist_total_count"]}
            (rdir / "result.json").write_text(json.dumps(res), encoding="utf-8"); return (uid, res)
        try:
            res = sc.run_key_phrases(text, str(kp_dir), aid, lv, process=proc, kp_backend="db_hybrid")
            err = None
        except Exception as e:
            res = {"exception": "%s: %s" % (type(e).__name__, e)}; err = traceback.format_exc()
        rec = {"unit_id": uid, "arm": a.arm, "article_id": aid, "level_code": lv, "process": proc, "elapsed_s": round(time.time() - t0, 2),
               "result": res, "traceback": err}
        rdir.mkdir(parents=True, exist_ok=True)
        (rdir / "result.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
        return (uid, (res.get("status") or ((res.get("canonicalization") or {}).get("status")) or res.get("exception")))
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(run, u) for u in units]
        for f in as_completed(futs):
            print(f.result(), "arm=%s spent_jpy=%.3f" % (a.arm, spent() if a.arm != "S" else 0.0), flush=True)
    print("DONE arm=%s spent_jpy=%.4f" % (a.arm, spent() if a.arm != "S" else 0.0))
    return 0

if __name__ == "__main__": sys.exit(main())

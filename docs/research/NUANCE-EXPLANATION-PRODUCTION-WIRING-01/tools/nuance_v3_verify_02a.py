# NUANCE-EXPLANATION-PRODUCTION-WIRING-01 委任_02A: Prompt v3 再検証driver (DEV/検証専用。Production resultsは変更しない。出力は v3_verify/ 配下のみ)
# 目的: Production形入力(暫定選定 + 提示pool最大12件 + 文法Top2)で、er134の**実関数**(candidate_stage -> run_candidate -> generate_candidate/judge_overlap/decide)を
#       01bと同じ8 levelで1回ずつ実行し、v2(01b)と比較する(Opus M-8)。続けて判定プローブ6件(固定fixture、R-8)。
# 使い方:
#   py -I tools/nuance_v3_verify_02a.py dry                  # API 0: 入力組立・promptサイズ・見積
#   NUANCE_TRIAL_PAID=1 py -I tools/nuance_v3_verify_02a.py gen run1     # 有料: 8 level (並列) -> v3_verify/run1/<key>/study_text/nuance_candidate.json
#   NUANCE_TRIAL_PAID=1 py -I tools/nuance_v3_verify_02a.py probe run1   # 有料: 判定プローブ6件
# 費用: v3_verify/usage_log_02a.jsonl に呼出ごとに記録。累計(実績+予約)がCAP_JPYを超える見込みの呼出は拒否(budget_guard)。
import sys, os, json, time, threading, importlib.util
BASE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.abspath(os.path.join(BASE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", "..", "..", ".."))
sys.path.insert(0, ROOT)
import er134_nuance_explanation_01 as er            # noqa: E402
import er119_kp_human_review_01 as rv               # noqa: E402

CAP_JPY = 5.0
VDIR = os.path.join(OUT, "v3_verify")
USAGE_LOG = os.path.join(VDIR, "usage_log_02a.jsonl")
RESERVE = {er.PROCESS_GEN: 0.40, er.PROCESS_JUDGE: 0.25}      # 実測(v2)の最大近傍。worst-caseの暴走はCAP拒否で止める
_lock = threading.Lock(); _reserved = [0.0]

spec = importlib.util.spec_from_file_location("nuance_trial_01", os.path.join(BASE, "nuance_trial_01.py"))
trial = importlib.util.module_from_spec(spec); spec.loader.exec_module(trial)

AIB = "er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01"
ZB = "er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_voice_fenrir_01"
YB = "er121_output/family_y_production_01/redelivery_fee/run_gpg5_y_01_s23f"
# key -> (kp_candidates.json, study_dir[grammar]) 。Paycheckは公開済みKP/文法docが存在しない(HR form導入前の記事)ため公開KP5件を提示poolとして使い、文法は無し
SRC = {
    "ai_island_std": (f"{AIB}/a2/key_phrases/kp_candidates.json", f"{AIB}/a2/study_text"),
    "ai_island_adv": (f"{AIB}/b1b/key_phrases/kp_candidates.json", f"{AIB}/b1b/study_text"),
    "paycheck_std": (None, None), "paycheck_adv": (None, None),
    "tth_std": (f"{ZB}/key_phrases/a2/kp_candidates.json", f"{ZB}/a2/study_text"),
    "tth_adv": (f"{ZB}/key_phrases/b1b/kp_candidates.json", f"{ZB}/study_text"),
    "y_redelivery_std": (f"{YB}/key_phrases/a2/kp_candidates.json", f"{YB}/a2/study_text"),
    "y_redelivery_adv": (f"{YB}/key_phrases/b1b/kp_candidates.json", f"{YB}/study_text"),
}
KEYS = list(SRC)


def _rj(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return json.load(f)


def build(key, T):
    t = T[key]; lv = "a2" if key.endswith("_std") else "b1b"
    kp_path, sd = SRC[key]
    paras = [p.strip() for p in t["body"].split("\n\n") if p.strip()]
    if kp_path:
        kp = _rj(kp_path); src_note = kp_path
    else:   # Paycheck: 公開KP5件を提示pool(=暫定選定)とする
        cs = []
        for i, k in enumerate(t["kp"], 1):
            cs.append({"candidate_id": f"pc_{key[-3:]}_{i}", "ai_rank": i, "used_form": k["expr"], "selection_phrase": k.get("display") or k["expr"], "kind": k.get("kind") or "phrase",
                       "japanese_gloss": k.get("gloss") or "", "auto_eligible": True, "item": {"display_phrase": k.get("display") or k["expr"], "key_phrase": k["expr"]}})
        kp = {"level": lv, "candidates": cs, "candidates_sha256": None}; src_note = "published KP (no kp_candidates.json)"
    gitems = []
    if sd:
        gd = _rj(f"{sd}/grammar_candidates.json")
        gitems = [{"id": c["candidate_id"], "rank": c["rank"], "title": c["construct_ja"], "example": c["sentence"]} for c in gd["candidates"][:2]]
    inp = er.build_inputs(family=t["family"], article_id=t["article"], title=t["title"], level=lv, paragraphs=paras, kp_cands=kp, grammar_items=gitems)
    return inp, src_note


def spent():
    if not os.path.exists(USAGE_LOG): return 0.0
    with open(USAGE_LOG, encoding="utf-8") as f:
        return sum(json.loads(l)["cost_jpy"] or 0 for l in f if l.strip())


def make_guard():
    def guard(process, prompt, attempt):
        assert os.environ.get("NUANCE_TRIAL_PAID") == "1", "paid call refused (NUANCE_TRIAL_PAID=1 required)"
        r = RESERVE[process]
        with _lock:
            if spent() + _reserved[0] + r > CAP_JPY: raise RuntimeError(f"CAP refused: spent={spent():.3f} reserved={_reserved[0]:.3f} next={r} cap={CAP_JPY}")
            _reserved[0] += r
    return guard


def make_fn(client, process, tag):
    base = er._default_call_fn_factory(client, er.MODEL, er.GEN_MAX_OUTPUT_TOKENS if process == er.PROCESS_GEN else er.JUDGE_MAX_OUTPUT_TOKENS)
    cnt = [0]
    def fn(prompt):
        cnt[0] += 1
        try:
            text, model, usage, rid = base(prompt)
        finally:
            with _lock: _reserved[0] -= RESERVE[process]
        cost = er._cost_jpy(model, usage or {})
        os.makedirs(os.path.join(VDIR, "raw"), exist_ok=True)
        with open(os.path.join(VDIR, "raw", f"{tag}_{process}_{cnt[0]}.txt"), "w", encoding="utf-8", newline="\n") as f: f.write(text or "")
        with _lock, open(USAGE_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps({"tag": tag, "process": process, "attempt": cnt[0], "model": model, "response_id": rid, "usage": usage, "cost_jpy": cost,
                                "prompt_sha256": __import__("hashlib").sha256(prompt.encode()).hexdigest()}, ensure_ascii=False) + "\n")
        return text, model, usage, rid
    return fn


def get_client():
    from dotenv import load_dotenv; load_dotenv(os.path.join(ROOT, ".env"))
    import er003_v1_b1_scaffold_01_generate as b1s
    return b1s.get_client()


def main():
    cmd = sys.argv[1]; T = trial.load_targets()
    if cmd == "dry":
        tot = 0
        for k in KEYS:
            inp, note = build(k, T)
            pr = er.build_gen_prompt(inp)
            print(k, inp["level"], "pool", len(inp["pool"]), "prov", len(inp["provisional"]), "grammar", len(inp["grammar"]), "gen_prompt_chars", len(pr), "src", note)
            print("   provisional:", [e["used_form"] for e in inp["provisional"]], "| others:", [e["used_form"] for e in inp["pool"] if not e["provisional"]], "| grammar:", [x["title"] for x in inp["grammar"]])
        print("gen_sha", er.PROMPT_GEN_SHA256, "judge_sha", er.PROMPT_JUDGE_SHA256); return
    tagrun = sys.argv[2]
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    client = get_client()
    if cmd == "gen":
        keys = sys.argv[3:] or KEYS; res = {}; ths = []
        def w(k):
            try:
                inp, note = build(k, T)
                sd = os.path.join(VDIR, tagrun, k, "study_text")
                er.ensure_spec(sd, level=inp["level"], new_review=True, issuer="v3_verify_02a")
                r = er.candidate_stage(sd, inp, call_fn=make_fn(client, er.PROCESS_GEN, f"{tagrun}_{k}"), judge_fn=make_fn(client, er.PROCESS_JUDGE, f"{tagrun}_{k}"), budget_guard=make_guard())
                d = r["doc"]; c = d.get("candidate")
                res[k] = {"status": d["status"], "reason": d.get("no_candidate_reason"), "expression": (c or {}).get("expression") or ((d.get("rejected_candidate_audit") or {}).get("candidate") or {}).get("expression"),
                          "n_calls": d["usage"]["n_calls"], "cost_jpy": d["usage"]["cost_jpy"], "pool_conflicts": (c or {}).get("pool_conflicts"), "grammar_conflicts": (c or {}).get("grammar_conflicts"),
                          "shared_terms": (c or {}).get("shared_terms"), "kp_source": note, "pool_n": len(inp["pool"]), "grammar_n": len(inp["grammar"])}
            except Exception as e:
                res[k] = {"error": repr(e)}
        for k in keys:
            th = threading.Thread(target=w, args=(k,)); th.start(); ths.append(th)
        for th in ths: th.join()
        json.dump(res, open(os.path.join(VDIR, f"summary_{tagrun}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(json.dumps(res, ensure_ascii=False, indent=1)); print("spent_total_jpy", round(spent(), 4)); return
    if cmd == "probe":
        fx = json.load(open(os.path.join(OUT, "judge_probes_fixture_02a.json"), encoding="utf-8")); out = []
        def w(pb):
            try:
                inp, _ = build(pb["target"], T); c = dict(pb["candidate"])
                qc = er.quote_check(c["quote_en"], inp["body"]); assert qc["ok"], ("probe quote invalid", pb["id"], qc)
                c["quote_en"] = qc["verbatim"]; c["focus_terms"] = er.derive_focus_terms(c["expression"])
                s1 = er.structural_check(c["expression"], inp["pool"]); judge = None
                if s1["verdict"] != "fail":
                    judge = er.judge_overlap(inp, c, stage1=s1, judge_fn=make_fn(client, er.PROCESS_JUDGE, f"{tagrun}_probe_{pb['id']}"), budget_guard=make_guard())
                oc = er.decide(inp, c, s1, judge)
                gt = {g["id"]: g["title"] for g in inp["grammar"]}
                out.append({"id": pb["id"], "target": pb["target"], "expected": pb["expected"], "verdict": oc["verdict"], "required_conflicts": [a["item"] for a in oc["against"] if a["item_id"] in oc["required_conflicts"]],
                            "pool_conflicts": oc["pool_conflicts"], "grammar_conflicts": [gt[i] for i in oc["grammar_conflicts"]], "stage1_auto": [a["matched_phrase"] for a in s1["auto_ng"]],
                            "closest": (oc["stage2_llm"].get("closest") or {}), "cost_jpy": sum((x.get("cost_jpy") or 0) for x in (judge or {}).get("calls", [])), "judge_skipped": judge is None})
            except Exception as e:
                out.append({"id": pb["id"], "error": repr(e)})
        ths = [threading.Thread(target=w, args=(pb,)) for pb in fx["probes"]]
        for th in ths: th.start()
        for th in ths: th.join()
        out.sort(key=lambda x: x["id"])
        json.dump(out, open(os.path.join(VDIR, f"probe_result_{tagrun}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(json.dumps(out, ensure_ascii=False, indent=1)); print("spent_total_jpy", round(spent(), 4))


if __name__ == "__main__":
    main()

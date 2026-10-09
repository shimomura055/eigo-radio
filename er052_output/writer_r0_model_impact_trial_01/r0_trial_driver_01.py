# -*- coding: utf-8 -*-
"""WRITER-R0-MODEL-IMPACT-TRIAL-01 薄いdriver(Trial/DEV、Production経路ではない)。既存関数・既存Promptをそのまま呼ぶ。
サブコマンド:
  prompts  : API非呼び出し。3テーマ分のR0 Promptを組み立てsha256を記録(dry-run)。
  r0       : 指定 theme x model のR0を1回生成(再試行は最大1回・同条件)。r0/<theme>/<model>.json に保存。
  flag     : 指定 theme x model のR0にRisk Flagger(D0 + D2記事モード)を実行。flags/<theme>/<model>.json に保存。
R0 = jaw.build_original_prompt(...)(Fact Lock差替え後のAN3ブロック込み) -> jaw.call_fresh(WRITER_MODELのみ差替え)。
Fact Check(ja_original_check)・must-fix再生成・記号must-fixは行わない(全セル共通・測定のみ記録)。
"""
import argparse, datetime, hashlib, json, os, sys, time

os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
sys.dont_write_bytecode = True
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(REPO, "er052_output", "writer_r0_model_impact_trial_01")
E2E = os.path.join(REPO, "er052_output", "factlock_astra_e2e_trial_01")
DET = os.path.join(REPO, "er052_output", "writer_dev_risk_flagger_01", "detectors")
THEMES = ["streaming_price", "space_weapons", "byd_recall"]
MODELS = ["gpt-6-luna", "gpt-6.1-sol", "gpt-6-astra"]
FLAGGER_MODEL = "gpt-6.1-sol"
FLAGGER_EFFORT = "medium"
USD_JPY = 160
os.chdir(REPO)
sys.path.insert(0, REPO)
sys.path.insert(0, DET)


def sha(b):
    return hashlib.sha256(b if isinstance(b, bytes) else b.encode("utf-8")).hexdigest()


def sha_file(p):
    return sha(open(p, "rb").read())


def paths(theme):
    r = os.path.join(E2E, "runs", theme, "new")
    return dict(brief=os.path.join(r, "storyline_b3", "selected_brief.md"), ledger=os.path.join(r, "research_ledger", "verified_fact_ledger.txt"),
                luna_old_r0=os.path.join(r, "new_writer", "r0.md"))


def build_prompt(theme):
    import er052_factlock_astra_e2e_runner_01 as run
    import er019_family_x_ja_writer_o_r1_r2_01 as jaw
    import er052_factlock_writer_trial_01_run as fl
    p = paths(theme)
    storyline, facts = run.parse_brief_md(open(p["brief"], encoding="utf-8").read())
    ledger = open(p["ledger"], encoding="utf-8").read()
    saved = fl.apply_factlock_patches()
    try:
        prompt = jaw.build_original_prompt(storyline, facts, must_fix=None, full_ledger_text=ledger)
        block_sha = sha(jaw.CONCRETENESS_CONTROL_AN3_BLOCK)   # パッチ適用後=build_r0_block出力
    finally:
        fl.restore_factlock_patches(saved)
    return prompt, dict(developer_message=jaw.DEVELOPER_MESSAGE, effort=jaw.WRITER_EFFORT, factlock_r0_block_sha256=block_sha,
                        brief_sha256=sha_file(p["brief"]), ledger_sha256=sha_file(p["ledger"]))


def cmd_prompts(a):
    out = {}
    for t in THEMES:
        prompt, meta = build_prompt(t)
        open(os.path.join(OUT, "prompts", t + ".txt"), "w", encoding="utf-8", newline="").write(prompt)
        out[t] = dict(prompt_sha256=sha(prompt), prompt_chars=len(prompt), **meta)
    json.dump(out, open(os.path.join(OUT, "prompts", "prompt_manifest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps(out, ensure_ascii=False, indent=2))


def cmd_r0(a):
    from dotenv import load_dotenv
    load_dotenv()
    import er052_factlock_astra_e2e_runner_01 as run
    import er019_family_x_ja_writer_o_r1_r2_01 as jaw
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er003_audio_tts_asr_safety as safety
    import er052_factlock_writer_trial_01_run as fl
    theme, model = a.theme, a.model
    assert theme in THEMES and model in MODELS
    prompt, meta = build_prompt(theme)
    jaw.WRITER_MODEL = model   # モデル以外は一切変えない(call_fresh内のmodel=WRITER_MODELのみ差替え)
    client = vfl01.get_client()
    attempts, resp, err = [], None, None
    for n in (1, 2):
        t0 = time.time()
        ts = datetime.datetime.now().isoformat(timespec="seconds")
        try:
            resp = jaw.call_fresh(client, jaw.DEVELOPER_MESSAGE, prompt, jaw.WRITER_EFFORT, "ja_original")
            el = time.time() - t0
            u = resp.usage
            attempts.append(dict(n=n, ts=ts, ok=True, elapsed_s=round(el, 3), response_id=resp.id, model_id=resp.model,
                                 input_tokens=u.input_tokens, output_tokens=u.output_tokens,
                                 reasoning_tokens=getattr(getattr(u, "output_tokens_details", None), "reasoning_tokens", None),
                                 cached_tokens=getattr(getattr(u, "input_tokens_details", None), "cached_tokens", None),
                                 status=getattr(resp, "status", None)))
            break
        except Exception as e:  # noqa: BLE001
            attempts.append(dict(n=n, ts=ts, ok=False, elapsed_s=round(time.time() - t0, 3), error=type(e).__name__ + ": " + str(e)[:300]))
            err = e
    rec = dict(theme=theme, requested_model=model, prompt_sha256=sha(prompt), input_meta=meta, attempts=attempts, ok=resp is not None)
    d = os.path.join(OUT, "r0", theme)
    os.makedirs(d, exist_ok=True)
    if resp is not None:
        final = resp.output_text.strip()
        try:
            clean = run.clean_ja_for_next(final).strip() + "\n"
            leak = None
        except Exception as e:  # noqa: BLE001
            clean, leak = None, str(e)[:200]
        sents = fl.split_sentences(final)
        rec.update(raw_text=final, clean_text=clean, tag_leak_error=leak, text_sha256=sha(clean) if clean else None, chars=len(clean or final),
                   tagged_sentences=sum(1 for s in sents if s["tags"] and not s["is_title"]),
                   tags_used=sorted({t for s in sents for t in s["tags"]}), r0_echo=run.detect_r0_echo(clean or final),
                   symbol_findings_measure_only=safety.detect_prohibited_symbols(final, language="ja"),
                   fact_check_run=False, must_fix_run=False)
        if clean:
            open(os.path.join(d, model + ".md"), "w", encoding="utf-8", newline="").write(clean)
    json.dump(rec, open(os.path.join(d, model + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(theme, model, "ok" if resp else "FAILED", [(x.get("elapsed_s"), x.get("output_tokens"), x.get("model_id")) for x in attempts])
    return 0 if resp is not None else 1


def cmd_flag(a):
    from dotenv import load_dotenv
    load_dotenv()
    import flagger_lib as L
    import run_flagger_01 as R
    import ledger_restore_01 as LR
    theme, model = a.theme, a.model
    cell = "%s__%s" % (theme, model)
    fd = os.path.join(OUT, "flags", theme)
    os.makedirs(fd, exist_ok=True)
    os.makedirs(os.path.join(OUT, "logs"), exist_ok=True)
    # 出力先を本Trial配下へ(detectors配下は書かない)
    R.RESULTS_DIR = os.path.join(OUT, "results")
    R.LOGS_DIR = os.path.join(OUT, "logs")
    L.LEDGER_PATH = os.path.join(OUT, "logs", "flagger_ledger_%s.jsonl" % cell)
    art = os.path.join(OUT, "r0", theme, model + ".md")
    facts = LR.parse_ledger_file(paths(theme)["ledger"])
    sents = R._split_sentences(open(art, encoding="utf-8").read())
    ss = [dict(sid="s%d" % (i + 1), text=s, before="", after="") for i, s in enumerate(sents)]
    unit = dict(unit_id=cell, mode="article", facts=facts, sentences=ss, ledger_complete=True, article_path=art)
    rc0 = R.run_d0([unit], cell)
    t0 = time.time()
    rc2 = R.run_llm([unit], "d2", FLAGGER_MODEL, cell, a.max_yen, a.max_yen, None, FLAGGER_EFFORT, None, False)
    el = time.time() - t0
    d0 = json.loads(open(R.result_paths("d0", "none", cell)[0], encoding="utf-8").readline())
    d2 = json.loads(open(R.result_paths("d2", FLAGGER_MODEL, cell)[0], encoding="utf-8").readline())
    union = R.union_flags([("d0", d0["flags"]), ("d2", d2["flags"])])
    raw = [json.loads(x) for x in open(R.result_paths("d2", FLAGGER_MODEL, cell)[1], encoding="utf-8") if x.strip()]
    out = dict(theme=theme, r0_model=model, cell=cell, flagger_model=FLAGGER_MODEL, flagger_effort=FLAGGER_EFFORT, article_sha256=sha_file(art),
               ledger_sha256=sha_file(paths(theme)["ledger"]), n_sentences=len(ss), n_facts=len(facts), rc_d0=rc0, rc_d2=rc2, d2_valid_json=d2["valid_json"],
               d2_attempts=d2["attempts"], d2_cost_jpy=d2["cost_jpy"], d2_elapsed_s=round(el, 2), d2_model_ids=sorted({r.get("model_id") for r in raw if r.get("model_id")}),
               d0_flags=d0["flags"], d2_flags=d2["flags"], union_flags=union, sentences={s["sid"]: s["text"] for s in ss},
               facts={f["fact_id"]: f["text"] for f in facts})
    json.dump(out, open(os.path.join(fd, model + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(cell, "d0=%d d2=%d union=%d cost=%.2f valid=%s" % (len(d0["flags"]), len(d2["flags"]), len(union), d2["cost_jpy"], d2["valid_json"]))
    return 0 if rc2 == 0 else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["prompts", "r0", "flag"])
    ap.add_argument("--theme")
    ap.add_argument("--model")
    ap.add_argument("--max-yen", type=float, default=30.0)
    a = ap.parse_args()
    return {"prompts": cmd_prompts, "r0": cmd_r0, "flag": cmd_flag}[a.cmd](a) or 0


if __name__ == "__main__":
    sys.exit(main())

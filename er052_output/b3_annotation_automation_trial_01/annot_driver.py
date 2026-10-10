# -*- coding: utf-8 -*-
"""B3-ANNOTATION-AUTOMATION-TRIAL-01 ドライバ骨格(Phase 1: dry-run / replay のみ。課金API呼び出しは実装しない)。
Trial(FACTLOCK-ASTRA-E2E-TRIAL-01)でsubagentに渡した注記者プロンプトを逐語移植する(新Promptなし)。
usage:
  annot_driver.py dry-run [--models claude-sonnet-5,gpt-6.1-sol,gpt-6-astra] [--themes a,b]   request payload を dry_run/ へ生成(API非呼び出し)
  annot_driver.py replay                                                                       既存Trial返答(reply.md)を extract->check->merge->eval に通し配線を確認(API非呼び出し・LLM不使用)
  annot_driver.py run ...                Phase 1では未実装(実行不可)。Phase 2は承認後にFableが別途配線する。
Production経路ではない(DEV/Trial専用)。Productionコード・CURRENT_SPEC・Promptは変更しない。"""
import sys, os, re, json, hashlib, argparse
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
TR = os.path.join(REPO, "er052_output", "factlock_astra_e2e_trial_01")
sys.path.insert(0, TR)
import b3_annotation_check_01 as chk
import b3_annotation_merge_01 as mrg

THEMES = ["byd_recall", "central_bank_mortgage", "hormuz", "inbound_tourism", "meta", "openai_copyright",
          "semiconductor_earnings", "small_bag", "space_weapons", "streaming_price"]
V2 = {"hormuz", "streaming_price"}   # B3 v2 (storyline_b3_v2) が基準のテーマ
MAX_OUT = 16000   # Trial外の新設定値(応答は約1.5〜6.5k字。thinking込みProviderを考慮)。Phase 2前にFableが確定
EFFORT = "medium"  # 既存xm_driver.py/flagger_libと同じ(OpenAI Responses)
# 条件定義。provider/model_idの実在確認(models list、無料)はPhase 2前に行う。未確認のまま置換しない。
CONDS = {
    "claude-sonnet-5": dict(provider="anthropic", model_id="claude-sonnet-5"),
    "gpt-6.1-sol": dict(provider="openai", model_id="gpt-6.1-sol"),
    "gpt-6-astra": dict(provider="openai", model_id="gpt-6-astra"),
    # Phase 2 (ユーザー方針): 実行対象はこの2つのみ。models list(無料)で実在確認済み(2026-10-10)
    "sonnet55": dict(provider="anthropic", model_id="claude-sonnet-5-5"),
    "luna": dict(provider="openai", model_id="gpt-6-luna"),
}
PRICES = {"claude-sonnet-5-5": (2.0, 0.10, 10.0), "gpt-6-luna": (0.10, 0.01, 0.50)}   # USD/MTok (in, cached, out)
USDJPY = 160.0
GUARD_JPY = 1200.0
LEDGER = os.path.join(HERE, "cost_ledger_annot_01.jsonl")
FORMAL9 = [t for t in THEMES if t != "inbound_tourism"]


def sha_b(b):
    return hashlib.sha256(b).hexdigest()


def rd(p):
    return open(p, encoding="utf-8", newline="").read()


def paths(slug):
    d = "storyline_b3_v2" if slug in V2 else "storyline_b3"
    return dict(brief=f"{TR}/stage_r/{slug}/{d}/selected_brief.md", ledger=f"{TR}/stage_r/{slug}/research_ledger/verified_fact_ledger.txt",
                spec=f"{TR}/B3_ANNOTATION_SPEC_v2_ANNOTATOR.md", template=f"{TR}/ANNOTATION_DELEGATION_TEMPLATE_v2.md")


def trial_prompt_body(slug, ann):
    """Trial実プロンプト(annotation/prompts/<slug>__<ann>.md)の『依頼文(ここから)〜(ここまで)』を逐語で取り出す。
    先頭の『ファイルをReadで読め』の前置きはsubagent用の運搬手段であり、API直渡しでは不要なので含めない。"""
    t = rd(f"{TR}/annotation/prompts/{slug}__{ann}.md")
    m = re.search(r"【依頼文\(ここから\)】\n(.*)\n【依頼文\(ここまで\)】", t, re.S)
    return t, m.group(1)


def verify_provenance(slug, ann):
    p = paths(slug)
    full, body = trial_prompt_body(slug, ann)
    reg = json.load(open(f"{TR}/annotation/PROMPT_SHA256.json", encoding="utf-8"))["prompts"]
    spec_sha, brief_sha = sha_b(open(p["spec"], "rb").read()), sha_b(open(p["brief"], "rb").read())
    fill = mrg.build_delegation(rd(p["template"]), ann, slug, rd(p["spec"]), rd(p["brief"]), rd(p["ledger"]), spec_sha, brief_sha)
    return dict(prompt_file_sha_matches_registry=sha_b(full.encode("utf-8")) == reg.get(f"{slug}__{ann}.md"),
                template_fill_is_prefix_of_trial_body=body.startswith(fill.rstrip("\n")), brief_sha=brief_sha, spec_sha=spec_sha,
                body_chars=len(body), trial_tail_is_common_clarification=("依頼文の末尾: 運用上の明確化" in body)), body


def build_request(cond, user):
    """xm_driver.build_request と同一規約(thinking/temperature等のProvider既定は上書きしない)。
    system指示は無く依頼文全体をuserで渡す(Trialのsubagentも1メッセージ)。"""
    if cond["provider"] == "openai":
        return dict(sdk="openai.responses.create", body=dict(model=cond["model_id"], input=user, reasoning={"effort": EFFORT}, max_output_tokens=MAX_OUT))
    if cond["provider"] == "anthropic":
        return dict(url="https://api.anthropic.com/v1/messages", headers={"anthropic-version": "2023-06-01", "content-type": "application/json"},
                    body=dict(model=cond["model_id"], max_tokens=MAX_OUT, messages=[{"role": "user", "content": user}]))
    raise ValueError(cond)


def dry_run(models, themes):
    out = os.path.join(HERE, "dry_run")
    os.makedirs(out, exist_ok=True)
    rows = []
    for s in themes:
        for ann in "AB":
            prov, body = verify_provenance(s, ann)
            for m in models:
                req = build_request(CONDS[m], body)
                fn = f"{out}/{m}__{s}__{ann}.json"
                json.dump(req, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
                rows.append(dict(model=m, theme=s, annotator=ann, payload=os.path.relpath(fn, REPO).replace("\\", "/"),
                                 payload_sha256=sha_b(open(fn, "rb").read()), **prov))
    json.dump(rows, open(f"{out}/_index.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    bad = [r for r in rows if not (r["prompt_file_sha_matches_registry"] and r["template_fill_is_prefix_of_trial_body"])]
    print(f"payloads={len(rows)} provenance_failures={len(bad)}")
    return 1 if bad else 0


def pipeline_one(slug, ann, reply_text, workdir):
    """返答本文 -> extract -> 単独check。LLM不使用。(Phase 2のAPI応答も同じ関数に通す)"""
    p = paths(slug)
    os.makedirs(workdir, exist_ok=True)
    try:
        md, side = mrg.extract_output(reply_text)
    except mrg.Stop as e:
        return dict(status="FORMAT_FAIL", reason=str(e))
    if md == "STOP":
        return dict(status="STOP_REPLY", reason=side)
    open(f"{workdir}/{ann}.annotated.md", "w", encoding="utf-8", newline="").write(md)
    json.dump(side, open(f"{workdir}/{ann}.annotation.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    r = chk.run(rd(p["brief"]), md, rd(p["ledger"]), side, spec_sha256=sha_b(open(p["spec"], "rb").read()),
                brief_sha256=sha_b(open(p["brief"], "rb").read()))
    return dict(status=r["verdict"], md=md, sidecar=side)


def replay():
    """既存Trial返答でextract->check->merge->評価を再現できるか(配線とGT再現性の確認。LLM不使用)。"""
    sys.path.insert(0, HERE)
    import annot_eval as ev
    work = os.path.join(HERE, "replay")
    res = []
    for s in THEMES:
        r = {"theme": s}
        p = paths(s)
        got = {}
        for ann in "AB":
            got[ann] = pipeline_one(s, ann, rd(f"{TR}/annotation/out/{ann}/{s}/reply.md"), f"{work}/{s}")
            r[f"{ann}_check"] = got[ann]["status"]
        if all(got[a]["status"] == "PASS" for a in "AB"):
            m = mrg.merge(rd(p["brief"]), rd(p["ledger"]), got["A"]["md"], got["A"]["sidecar"], got["B"]["md"], got["B"]["sidecar"],
                          sha_b(open(p["spec"], "rb").read()), sha_b(open(p["brief"], "rb").read()))
            r["merge_status"] = m["status"]
            gt = rd(f"{TR}/annotation/final/{s}/selected_brief_factlock.md")
            r["merged_equals_trial_final"] = (m["merged_md"] == gt)
            c = ev.compare(rd(p["brief"]), gt, m["merged_md"])
            r["eval_f1_fact_core_periph"] = [c["fact"]["f1"], c["core"]["f1"], c["peripheral"]["f1"]]
        res.append(r)
        print(r)
    json.dump(res, open(f"{HERE}/replay_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 0


def cost_jpy(model_id, u):
    pin, pc, pout = PRICES[model_id]
    inp, out, c = u.get("input_tokens") or 0, u.get("output_tokens") or 0, u.get("cached_tokens") or 0
    return ((inp - c) * pin + c * pc + out * pout) / 1e6 * USDJPY


def ledger_total():
    if not os.path.exists(LEDGER):
        return 0.0
    return sum(json.loads(l)["cost_jpy"] for l in open(LEDGER, encoding="utf-8") if l.strip())


def call_api(cond, body):
    """(text, usage, resp_id, model_returned, raw)。技術retryのみ(通信/429/5xx 最大2回)。内容を見た再実行はしない。"""
    from dotenv import load_dotenv
    load_dotenv(os.path.join(REPO, ".env"))
    last = None
    for attempt in range(3):
        try:
            if cond["provider"] == "openai":
                from openai import OpenAI
                r = OpenAI(api_key=os.environ["OPENAI_API_KEY"]).responses.create(**body)
                u = r.usage
                usage = dict(input_tokens=u.input_tokens, output_tokens=u.output_tokens,
                             reasoning_tokens=getattr(getattr(u, "output_tokens_details", None), "reasoning_tokens", None),
                             cached_tokens=getattr(getattr(u, "input_tokens_details", None), "cached_tokens", 0) or 0, status=getattr(r, "status", None))
                return r.output_text, usage, r.id, r.model, r.model_dump()
            import requests
            h = {"anthropic-version": "2023-06-01", "content-type": "application/json", "x-api-key": os.environ["ANTHROPIC_API_KEY"]}
            r = requests.post("https://api.anthropic.com/v1/messages", headers=h, json=body, timeout=600)
            if r.status_code in (429, 500, 502, 503, 504, 529):
                last = "HTTP %s" % r.status_code
                import time; time.sleep(5 * (attempt + 1)); continue
            j = r.json()
            if r.status_code != 200:
                raise RuntimeError("HTTP %s %s" % (r.status_code, json.dumps(j, ensure_ascii=False)[:300]))
            txt = "".join(b.get("text", "") for b in j.get("content", []) if b.get("type") == "text")
            u = j.get("usage", {}); cr = u.get("cache_read_input_tokens", 0) or 0; cc = u.get("cache_creation_input_tokens", 0) or 0
            usage = dict(input_tokens=(u.get("input_tokens", 0) or 0) + cr + cc, output_tokens=u.get("output_tokens", 0), cached_tokens=cr,
                         stop_reason=j.get("stop_reason"))
            return txt, usage, j.get("id"), j.get("model"), j
        except (OSError, ConnectionError) as e:   # 通信系のみ(requests例外もOSError系)
            last = repr(e)
            import time; time.sleep(5 * (attempt + 1))
    raise RuntimeError("technical retry exhausted: %s" % last)


def run_one(model_key, rep, slug):
    import time
    cond = CONDS[model_key]
    d = os.path.join(HERE, "runs", model_key, slug, "rep%d" % rep)
    if os.path.exists(os.path.join(d, "response_raw.json")) or os.path.exists(os.path.join(d, "request.json")):
        sys.exit("既存結果あり(上書き禁止): " + d)
    tot = ledger_total()
    if tot >= GUARD_JPY:
        sys.exit("費用ガード到達 JPY%.1f >= %.0f: 実行しない(STOP)" % (tot, GUARD_JPY))
    prov, body_text = verify_provenance(slug, "A")
    if not (prov["prompt_file_sha_matches_registry"] and prov["template_fill_is_prefix_of_trial_body"]):
        sys.exit("provenance FAIL: " + slug)
    req = build_request(cond, body_text)
    body = req["body"]
    ref = json.load(open(os.path.join(HERE, "dry_run", "claude-sonnet-5__%s__A.json" % slug), encoding="utf-8"))["body"]["messages"][0]["content"]
    assert ref == body_text, "dry_run payloadとuserが不一致"
    os.makedirs(d)
    json.dump(dict(model_key=model_key, **req), open(os.path.join(d, "request.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    t0 = time.time()
    try:
        txt, usage, rid, mret, raw = call_api(cond, body)
    except Exception as e:
        json.dump(dict(error=str(e)), open(os.path.join(d, "response_raw.json"), "w", encoding="utf-8"))
        print("API_ERROR", model_key, slug, rep, e); return None
    el = time.time() - t0
    json.dump(raw, open(os.path.join(d, "response_raw.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(os.path.join(d, "reply.txt"), "w", encoding="utf-8", newline="").write(txt)
    cj = cost_jpy(cond["model_id"], usage)
    res = pipeline_one(slug, "A", txt, d)
    chk_res = dict(status=res["status"], reason=res.get("reason"))
    if "md" in res:
        os.replace(os.path.join(d, "A.annotated.md"), os.path.join(d, "annotated.md"))
        os.replace(os.path.join(d, "A.annotation.json"), os.path.join(d, "annotation.json"))
    p = paths(slug)
    if "md" in res:   # 詳細検査結果も保存
        full = chk.run(rd(p["brief"]), res["md"], rd(p["ledger"]), res["sidecar"], spec_sha256=sha_b(open(p["spec"], "rb").read()),
                       brief_sha256=sha_b(open(p["brief"], "rb").read()))
        json.dump(full, open(os.path.join(d, "check.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    row = dict(ts=time.strftime("%Y-%m-%dT%H:%M:%S%z"), model_key=model_key, model_id_requested=cond["model_id"], model_id_returned=mret,
               theme=slug, rep=rep, usage=usage, cost_jpy=round(cj, 4), latency_s=round(el, 2), resp_id=rid, check=chk_res["status"],
               prompt_chars=len(body_text), reply_chars=len(txt))
    open(LEDGER, "a", encoding="utf-8").write(json.dumps(row, ensure_ascii=False) + chr(10))
    print(json.dumps(row, ensure_ascii=False))
    return row


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["dry-run", "replay", "run"])
    ap.add_argument("--models", default=",".join(CONDS))
    ap.add_argument("--themes", default=",".join(THEMES))
    ap.add_argument("--model")
    ap.add_argument("--rep", type=int)
    a = ap.parse_args()
    if a.cmd == "run":
        assert a.model in ("sonnet55", "luna") and a.rep in (1, 2)
        for t in a.themes.split(","):
            run_one(a.model, a.rep, t)
        sys.exit(0)
    if a.cmd == "dry-run":
        sys.exit(dry_run(a.models.split(","), a.themes.split(",")))
    sys.exit(replay())

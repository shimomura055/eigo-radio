# -*- coding: utf-8 -*-
"""FACTLOCK Trial 盲検評価(Trial専用)。3セル(factlock/all6/baseline)x24本=72本を同一パック・セル非開示で評価。
使い方: python eval_fl.py make_blind | judge [--limit N] | pairwise  (集計は agg_fl.py)
- 評価者=gpt-5.6-luna / gpt-6-luna(rubric適用の単独LLM判定)。各セルを評価者へ同数配分(セルごとにシャッフルして交互割当)。
- all6/baseline記事は all6_writer_redesign_necessity_01/runs から read-only 読み取りコピー(本パックで再採点)。
- 匿名コード+MAPは eval/_private/MAP.json。評価者にセル・モデル名は渡さない。
- STOP/未完了runも母数に含め、存在する最終段(R0/R1/R2/EN)を評価。無い段は明示。"""
import glob
import json
import os
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(__file__))
BASE = "er052_output/factlock_writer_trial_01"
EVAL = f"{BASE}/eval"
A6 = "er052_output/all6_writer_redesign_necessity_01/runs"
RUBRIC = "docs/pm/b3_trial_01/eval_rubric.md"
JUDGES = ["gpt-5.6-luna", "gpt-6-luna"]
SEED = 20261008
MISSING = "(この段は生成されず/存在しない)"
FILES = ["ja_writer/original.md", "ja_writer/revision1.md", "ja_writer/revision2.md", "b1b/article.md"]


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def cell_runs():
    out = []
    for cell, pat in (("factlock", f"{BASE}/runs/*/control/b*__factlock__r*"),
                      ("all6", f"{A6}/*/control/b*__all6__r*"),
                      ("baseline", f"{A6}/*/control/b*__baseline__r*")):
        for d in sorted(glob.glob(pat)):
            d = d.replace("\\", "/")
            if "_failed_a" in d or not os.path.exists(f"{d}/manifest.json"):
                continue
            slug = d.split("/control/")[0].split("/")[-1]
            b, _, rep = os.path.basename(d).split("__")
            out.append((cell, slug, int(b[1:]), int(rep[1:]), d))
    return out


def make_blind():
    os.makedirs(f"{EVAL}/_private", exist_ok=True)
    mp = f"{EVAL}/_private/MAP.json"
    mapping = json.load(open(mp, encoding="utf-8")) if os.path.exists(mp) else {"articles": {}, "judge_assign": {}}
    rnd = random.Random(SEED)
    used = {v["code"] for v in mapping["articles"].values()}
    for cell, slug, b, rep, d in cell_runs():
        key = f"{cell}/{slug}/b{b}/r{rep}"
        if key in mapping["articles"]:
            continue
        while True:
            code = "".join(rnd.choice("abcdefghjkmnpqrstuvwxyz23456789") for _ in range(4))
            if code not in used:
                used.add(code)
                break
        bd = f"{EVAL}/blind/{slug}/{code}"
        present = {}
        for rel in FILES:
            os.makedirs(os.path.dirname(f"{bd}/{rel}"), exist_ok=True)
            ok = os.path.exists(f"{d}/{rel}")
            present[rel] = ok
            with open(f"{bd}/{rel}", "w", encoding="utf-8", newline="") as f:
                txt = read(f"{d}/{rel}") if ok else MISSING
                if cell == "factlock" and "【" in txt:   # phase2のJA再確認(案B)で再生成された未除去タグがある場合の追加除去(セル漏洩防止、harnessのstrip_tagsと同一)
                    import er052_factlock_writer_trial_01_run as _h
                    txt = _h.strip_tags(txt)
                f.write(txt)
        man = json.load(open(f"{d}/manifest.json", encoding="utf-8"))
        mapping["articles"][key] = {"code": code, "cell": cell, "slug": slug, "b": b, "rep": rep, "run_dir": d,
                                    "exit_reason": man.get("exit_reason"), "present": present}
    by = {}
    for k, v in mapping["articles"].items():
        by.setdefault(v["cell"], []).append(k)
    for cell, keys in by.items():
        keys = sorted(k for k in keys if k not in mapping["judge_assign"])
        random.Random(SEED).shuffle(keys)
        cnt = {j: sum(1 for k, j2 in mapping["judge_assign"].items() if mapping["articles"][k]["cell"] == cell and j2 == j) for j in JUDGES}
        for k in keys:
            j = min(JUDGES, key=lambda x: (cnt[x], x))
            mapping["judge_assign"][k] = j
            cnt[j] += 1
    json.dump(mapping, open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("articles", len(mapping["articles"]), {c: len(v) for c, v in by.items()},
          {c: {j: sum(1 for k in v if mapping["judge_assign"].get(k) == j) for j in JUDGES} for c, v in by.items()})


def judge(limit=0, workers=4):
    import eval_ta_shared as ev
    import er005_cost_logger as cl
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er006_model_routing_contract_01 as routing
    mp = json.load(open(f"{EVAL}/_private/MAP.json", encoding="utf-8"))
    cl.install(f"{EVAL}/raw_usage_log_judge.jsonl")
    client = vfl01.get_client()
    os.makedirs(f"{EVAL}/judgments", exist_ok=True)
    jobs = [k for k in sorted(mp["articles"]) if not os.path.exists(f"{EVAL}/judgments/{mp['articles'][k]['code']}.json")]
    if limit:
        jobs = jobs[:limit]
    for j in JUDGES:
        routing.require_model_or_override("WRITER_FACT_CHECK", j, override_reason="FACTLOCK-WRITER-REDESIGN-TRIAL-01 eval")

    def one(k):
        a = mp["articles"][k]
        model = mp["judge_assign"][k]
        slug, code = a["slug"], a["code"]
        ledger = read(f"er052_output/open233_polysemy_trial_02/ledgers/{slug}/control/research_ledger/verified_fact_ledger.txt")
        bd = f"{EVAL}/blind/{slug}/{code}"
        prompt = (f"{ev.INSTR}\n\n# ルーブリック\n{read(RUBRIC)}\n\n# Verified Fact Ledger\n{ledger}\n\n"
                  f"# R0(修正前JA原稿)\n{read(bd + '/ja_writer/original.md')}\n\n"
                  f"# R2(JA最終稿)\n{read(bd + '/ja_writer/revision2.md')}\n\n"
                  f"# EN(英語版)\n{read(bd + '/b1b/article.md')}\n")
        t0 = time.time()
        for attempt in (1, 2, 3):
            try:
                with cl.logging_context("FL_EVAL", f"eval_{model}"):
                    resp = client.responses.create(model=model, reasoning={"effort": "high"},
                                                   text={"format": {"type": "json_schema", **ev.SCHEMA}},
                                                   input=[{"role": "developer", "content": "あなたは厳密で一貫した事実評価者です。"},
                                                          {"role": "user", "content": prompt}])
                parsed = json.loads(resp.output_text)
                break
            except Exception:  # noqa: BLE001
                if attempt == 3:
                    raise
                time.sleep(5 * attempt)
        rec = {"code": code, "judge": model, "judge_actual": resp.model, "parsed": parsed, "sec": round(time.time() - t0, 1)}
        json.dump(rec, open(f"{EVAL}/judgments/{code}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        return rec

    with ThreadPoolExecutor(max_workers=workers) as ex:
        recs = list(ex.map(one, jobs))
    print("judged", len(recs))


PW_SCHEMA = {"name": "pairwise", "strict": True, "schema": {
    "type": "object", "additionalProperties": False, "required": ["winner", "reason"],
    "properties": {"winner": {"type": "string", "enum": ["A", "B", "tie"]}, "reason": {"type": "string"}}}}
PW_INSTR = ("以下は同じニュース題材から作られた、英語学習者向け(日本語話者がA2程度の英語を学ぶラジオ)の日本語ラジオ記事AとBです。"
            "『聞いていて面白い・引き込まれる・自然で読みやすい(話し言葉として違和感がない)』のはどちらかを判定してください。"
            "事実の正確さは別途評価するのでここでは問いません。文体の窮屈さ・不自然な言い回し・省略の不自然さがあれば減点してください。"
            "winnerはA/B/tie、reasonは日本語で2文以内。")


def pairwise():
    import er005_cost_logger as cl
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er006_model_routing_contract_01 as routing
    mp = json.load(open(f"{EVAL}/_private/MAP.json", encoding="utf-8"))
    cl.install(f"{EVAL}/raw_usage_log_pairwise.jsonl")
    client = vfl01.get_client()
    routing.require_model_or_override("WRITER_FACT_CHECK", "gpt-6-luna", override_reason="FACTLOCK-WRITER-REDESIGN-TRIAL-01 pairwise")
    arts = mp["articles"]
    pairs = []
    for k, v in arts.items():
        if v["cell"] != "factlock":
            continue
        k2 = f"all6/{v['slug']}/b{v['b']}/r{v['rep']}"
        if k2 in arts:
            pairs.append((k, k2))
    outp = f"{EVAL}/pairwise.json"
    done = json.load(open(outp, encoding="utf-8")) if os.path.exists(outp) else {}

    def txt(k):
        a = arts[k]
        return read(f"{EVAL}/blind/{a['slug']}/{a['code']}/ja_writer/revision2.md")

    def one(args):
        kf, ka, order = args
        key = f"{kf}|{ka}|{order}"
        if key in done:
            return key, done[key]
        x, y = (kf, ka) if order == 0 else (ka, kf)
        prompt = f"{PW_INSTR}\n\n# 記事A\n{txt(x)}\n\n# 記事B\n{txt(y)}\n"
        with cl.logging_context("FL_PAIRWISE", "pairwise"):
            resp = client.responses.create(model="gpt-6-luna", reasoning={"effort": "medium"},
                                           text={"format": {"type": "json_schema", **PW_SCHEMA}},
                                           input=[{"role": "developer", "content": "あなたは公平な編集者です。"},
                                                  {"role": "user", "content": prompt}])
        p = json.loads(resp.output_text)
        win = {"A": x, "B": y}.get(p["winner"], "tie")
        return key, {"winner_key": win, "winner_label": p["winner"], "reason": p["reason"], "model": resp.model}

    jobs = [(kf, ka, o) for kf, ka in pairs for o in (0, 1)]
    with ThreadPoolExecutor(max_workers=4) as ex:
        for key, rec in ex.map(one, jobs):
            done[key] = rec
    json.dump(done, open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("pairwise", len(done))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    cmd = sys.argv[1]
    if cmd == "make_blind":
        make_blind()
    elif cmd == "judge":
        judge(int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 0)
    elif cmd == "pairwise":
        pairwise()

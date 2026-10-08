# -*- coding: utf-8 -*-
"""T-A 盲検評価(Trial専用)。make_blind: 匿名コピー+MAP / judge: APIジャッジ(rubric適用) / aggregate: MAP開封して集計。

使い方: python eval_ta.py make_blind | judge [--limit N] | aggregate
- 匿名コード+MAPは eval/_private/MAP.json(評価者には非開示)。評価者へはarm・モデル名を渡さない。
- 評価者(ジャッジ)=gpt-5.6-luna / gpt-6-luna のAPI呼び出し(rubric適用、単独LLM判定)。記事は無作為配分し、
  各評価者に両群同数(群ごとに交互割当)。
"""
import glob
import json
import os
import random
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
BASE = "er052_output/all6_writer_redesign_necessity_01"
RUNS = f"{BASE}/runs"
EVAL = f"{BASE}/eval"
RUBRIC = "docs/pm/b3_trial_01/eval_rubric.md"
JUDGES = ["gpt-5.6-luna", "gpt-6-luna"]
SEED = 20261008


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def completed_runs():
    out = []
    for man in sorted(glob.glob(f"{RUNS}/*/control/b*__*__r*/manifest.json")):
        m = json.load(open(man, encoding="utf-8"))
        d = os.path.dirname(man)
        if m.get("exit_reason") == "completed" and os.path.exists(f"{d}/b1b/article.md") and os.path.exists(f"{d}/ja_writer/revision2.md"):
            out.append((d, m))
    return out


def make_blind():
    os.makedirs(f"{EVAL}/_private", exist_ok=True)
    mp = f"{EVAL}/_private/MAP.json"
    mapping = json.load(open(mp, encoding="utf-8")) if os.path.exists(mp) else {"articles": {}, "judge_assign": {}}
    rnd = random.Random(SEED)
    used = {v["code"] for v in mapping["articles"].values()}
    for d, m in completed_runs():
        key = os.path.relpath(d, RUNS).replace("\\", "/")
        if key in mapping["articles"]:
            continue
        while True:
            code = "".join(rnd.choice("abcdefghjkmnpqrstuvwxyz23456789") for _ in range(4))
            if code not in used:
                used.add(code); break
        slug = m["slug"]
        bd = f"{EVAL}/blind/{slug}/{code}"
        os.makedirs(f"{bd}/ja_writer", exist_ok=True); os.makedirs(f"{bd}/b1b", exist_ok=True)
        for rel in ("ja_writer/original.md", "ja_writer/revision1.md", "ja_writer/revision2.md", "b1b/article.md"):
            with open(f"{bd}/{rel}", "w", encoding="utf-8", newline="") as f:
                f.write(read(f"{d}/{rel}"))
        mapping["articles"][key] = {"code": code, "slug": slug, "arm": m["arm"], "run_dir": d}
    # 評価者割当: 群ごとにシャッフルして交互割当(各評価者に両群同数)
    by_arm = {}
    for k, v in mapping["articles"].items():
        by_arm.setdefault(v["arm"], []).append(k)
    for arm, keys in by_arm.items():
        keys = sorted(k for k in keys if k not in mapping["judge_assign"])
        random.Random(SEED + hash(arm) % 1000 if False else SEED).shuffle(keys)
        # 既に割当済み件数に応じて開始評価者をずらす
        cnt = {j: sum(1 for k, j2 in mapping["judge_assign"].items() if mapping["articles"][k]["arm"] == arm and j2 == j) for j in JUDGES}
        for k in keys:
            j = min(JUDGES, key=lambda x: (cnt[x], x))
            mapping["judge_assign"][k] = j; cnt[j] += 1
    json.dump(mapping, open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("articles", len(mapping["articles"]), {j: sum(1 for x in mapping["judge_assign"].values() if x == j) for j in JUDGES})


SCHEMA = {
    "name": "article_eval", "strict": True,
    "schema": {
        "type": "object", "additionalProperties": False,
        "required": ["ng_items", "pending", "notes"],
        "properties": {
            "ng_items": {"type": "array", "items": {
                "type": "object", "additionalProperties": False,
                "required": ["text", "severity", "kind", "fact_id", "in_r0", "in_r2", "in_en", "reason"],
                "properties": {
                    "text": {"type": "string"},
                    "severity": {"type": "string", "enum": ["major", "minor"]},
                    "kind": {"type": "string", "enum": ["subject", "object", "scope", "time", "negation", "causal", "added_fact"]},
                    "fact_id": {"type": "string"},
                    "in_r0": {"type": "boolean"}, "in_r2": {"type": "boolean"}, "in_en": {"type": "boolean"},
                    "reason": {"type": "string"}}}},
            "pending": {"type": "array", "items": {
                "type": "object", "additionalProperties": False, "required": ["text", "reason"],
                "properties": {"text": {"type": "string"}, "reason": {"type": "string"}}}},
            "notes": {"type": "string"},
        }}}

INSTR = """あなたは記事の事実評価者です。以下のルーブリックに従い、Verified Fact Ledgerと照合して記事のNGを列挙してください。
- 対象テキストはR0(修正前JA原稿)・R2(JA最終稿)・EN(英語版)の3つ。NG項目ごとに、そのNGがR0/R2/ENのどれに存在するか(in_r0/in_r2/in_en)を真偽で付けること。
- 同一の誤りは1項目(JA/ENで共通なら1項目で両方true)。R0にあってR2で直ったものも in_r0=true,in_r2=false で記録する。
- 重大(major)=事実の意味が変わり読者に誤った理解を与える(主体・対象の入れ替わり/方向・状態の逆転/台帳にない事実の断定で理解が変わる/否定の反転)。軽微(minor)=意味は逆転しないが不正確・過剰断定・曖昧・範囲の曖昧さ・台帳未提示事項の軽い具体化。
- 確信が持てない境界や、文章品質のみ(事実の意味変化なし)のものは pending に入れる(NGには数えない)。境界でどちらかに倒す場合は軽微にし notes に書く。
- fact_idは台帳のID(該当が無ければ空文字)。textは記事中のNG文(原文のまま、短く)。
- 文脈で判定し、語の有無だけで重大にしない。台帳にある事実の言い換え・A2向けの簡略化は、意味が変わらない限りNGにしない。
- 判定は台帳とルーブリックのみで行い、条件・モデル名は与えられない。
"""


def build_prompt(d_blind, ledger):
    return (f"{INSTR}\n\n# ルーブリック\n{read(RUBRIC)}\n\n# Verified Fact Ledger\n{ledger}\n\n"
            f"# R0(修正前JA原稿)\n{read(d_blind + '/ja_writer/original.md')}\n\n"
            f"# R2(JA最終稿)\n{read(d_blind + '/ja_writer/revision2.md')}\n\n"
            f"# EN(英語版)\n{read(d_blind + '/b1b/article.md')}\n")


def judge(limit=0, workers=4):
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
        routing.require_model_or_override("WRITER_FACT_CHECK", j, override_reason="ALL-6-LUNA-WRITER-REDESIGN-NECESSITY-TRIAL-01")

    def one(k):
        a = mp["articles"][k]; model = mp["judge_assign"][k]
        slug, code = a["slug"], a["code"]
        ledger = read(f"er052_output/open233_polysemy_trial_02/ledgers/{slug}/control/research_ledger/verified_fact_ledger.txt")
        prompt = build_prompt(f"{EVAL}/blind/{slug}/{code}", ledger)
        t0 = time.time()
        with cl.logging_context("ALL6_EVAL", f"eval_{model}"):
            resp = client.responses.create(model=model, reasoning={"effort": "high"},
                                           text={"format": {"type": "json_schema", **SCHEMA}},
                                           input=[{"role": "developer", "content": "あなたは厳密で一貫した事実評価者です。"},
                                                  {"role": "user", "content": prompt}])
        rec = {"code": code, "judge": model, "judge_actual": resp.model, "parsed": json.loads(resp.output_text),
               "sec": round(time.time() - t0, 1)}
        json.dump(rec, open(f"{EVAL}/judgments/{code}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        return rec

    with ThreadPoolExecutor(max_workers=workers) as ex:
        recs = list(ex.map(one, jobs))
    print("judged", len(recs))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    cmd = sys.argv[1]
    if cmd == "make_blind":
        make_blind()
    elif cmd == "judge":
        lim = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 0
        judge(lim)

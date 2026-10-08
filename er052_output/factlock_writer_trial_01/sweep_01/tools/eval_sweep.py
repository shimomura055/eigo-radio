# -*- coding: utf-8 -*-
"""sweep評価(Trial専用、FACTLOCK-WRITER-REDESIGN-TRIAL-01 委任_04c)。評価規則は sweep_01/eval/EVAL_RULES_V2.md に固定。
サブコマンド: noise | noise_md | (本評価: eval_sweep_part2.py)。既存 tools/eval_fl.py は編集しない(判定文を中立化して新規実装)。
"""
import itertools
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(__file__))
SW = "er052_output/factlock_writer_trial_01/sweep_01"
EV = f"{SW}/eval"
A6 = "er052_output/all6_writer_redesign_necessity_01/runs"
TAGS = re.compile(r"【事実[^】]*】")

# ---- M1: 中立化した面白さ判定文(逐語。EVAL_RULES_V2.md と同一) ----
PW_INSTR = ("以下は同じニュースをもとにした、日本語ラジオで読み上げる記事AとBです。"
            "あなたが聞き手だとして、続きを聞きたい、誰かに話したくなるのはどちらですか。"
            "事実の正確さは別に評価するので考えなくてかまいません。"
            "winnerはA/B/tie。reasonは、そう感じた箇所を具体的に挙げて日本語2文以内で。")
PW_DEV = "あなたはラジオ番組の聞き手です。"
PW_SCHEMA = {"name": "pairwise", "strict": True, "schema": {
    "type": "object", "additionalProperties": False, "required": ["winner", "reason"],
    "properties": {"winner": {"type": "string", "enum": ["A", "B", "tie"]}, "reason": {"type": "string"}}}}
MAIN_JUDGE, SUB_JUDGE = "gpt-6-luna", "gpt-5.6-luna"


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def jload(p, default=None):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else default


def jdump(o, p):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(o, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def clean(text):
    return TAGS.sub("", text).strip()


def final_text(d):
    """JA最終稿。revision2.md(タグ除去)。存在しない/空ならNone(不戦敗、M2)。"""
    f = f"{d}/ja_writer/revision2.md"
    if not os.path.exists(f):
        return None
    t = clean(read(f))
    return t or None


# ---- 記事ディレクトリの解決 ----
def variants():
    return jload(f"{SW}/variants.json")


def ref_dir(rid, slug, b, rep=None):
    r = [x for x in variants()["references"] if x["id"] == rid][0]
    rp = rep or r.get("rep_override", {}).get(f"{slug}/b{b}", r["rep_default"])
    return r["path_template"].format(slug=slug, b=b, rep=rp)


def art_dir(vid, slug, b):
    if vid in ("S0", "S5"):
        return ref_dir(vid, slug, b)
    return f"{SW}/runs/{slug}/control/b{b}__{vid}__r1"


def briefs():
    return [tuple(x) for x in variants()["briefs"]]


# ---- API ----
_client = None


def client():
    global _client
    if _client is None:
        import er005_cost_logger as cl
        import er003_v1_en_direct_vfl_01_generate as vfl01
        import er006_model_routing_contract_01 as routing
        cl.install(f"{EV}/raw_usage_log_eval_sweep{os.environ.get('EVAL_LOG_SUFFIX', '')}.jsonl")
        for m in (MAIN_JUDGE, SUB_JUDGE):
            routing.require_model_or_override("WRITER_FACT_CHECK", m, override_reason="FACTLOCK-WRITER-REDESIGN-TRIAL-01 04c sweep eval")
        _client = (vfl01.get_client(), cl)
    return _client


def call_json(model, dev, prompt, schema, tag, effort="medium", retries=3):
    cli, cl = client()
    for attempt in range(1, retries + 1):
        try:
            with cl.logging_context("FL_SWEEP_EVAL", tag):
                resp = cli.responses.create(model=model, reasoning={"effort": effort},
                                            text={"format": {"type": "json_schema", **schema}},
                                            input=[{"role": "developer", "content": dev}, {"role": "user", "content": prompt}])
            return json.loads(resp.output_text), resp.model
        except Exception:  # noqa: BLE001
            if attempt == retries:
                raise
            time.sleep(5 * attempt)


def judge_pair(model, text_a, text_b):
    assert text_a and text_b, "M2: 両本文が非空であること"
    p, actual = call_json(model, PW_DEV, f"{PW_INSTR}\n\n# 記事A\n{text_a}\n\n# 記事B\n{text_b}\n", PW_SCHEMA, "pairwise")
    return {"winner_label": p["winner"], "reason": p["reason"], "model": actual}


def score_from(done, pid):
    """M3: x視点。2順序とも勝ち=1、割れ=0.5(片方勝ち片方負け、またはtie)、2順序とも負け=0。"""
    pts = []
    for o in (0, 1):
        w = done[f"{pid}|{o}"]["winner_label"]
        pts.append(0.5 if w == "tie" else (1.0 if (w == "A") == (o == 0) else 0.0))
    s = sum(pts) / 2
    if pts == [1.0, 1.0]:
        s = 1.0
    elif pts == [0.0, 0.0]:
        s = 0.0
    else:
        s = 0.5  # 割れ(片方勝ち片方負け/tie混じり)は0.5で固定(M3)
    return {"x_score": s, "pts": pts, "split": s == 0.5}


def run_pairs(pairs, cache_path, model, workers=4):
    """pairs: [(pair_id, text_x, text_y)] を2順序(o=0: x=A, o=1: y=A)で判定。キャッシュ再利用。"""
    done = jload(cache_path, {})
    jobs = [(pid, x, y, o) for pid, x, y in pairs for o in (0, 1) if f"{pid}|{o}" not in done]

    def one(j):
        pid, x, y, o = j
        a, b = (x, y) if o == 0 else (y, x)
        return f"{pid}|{o}", judge_pair(model, a, b)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        for k, rec in ex.map(one, jobs):
            done[k] = rec
    jdump(done, cache_path)
    out = {}
    for pid, _, _ in pairs:
        r = score_from(done, pid)
        r["reasons"] = [done[f"{pid}|0"]["reason"], done[f"{pid}|1"]["reason"]]
        out[pid] = r
    return out


# ---- ノイズ基準(M4) ----
def noise(model=MAIN_JUDGE):
    pairs, skipped = [], []
    for slug in ("meta", "hormuz", "space_weapons"):
        for b in (1, 2, 3, 4):
            t1 = final_text(f"{A6}/{slug}/control/b{b}__all6__r1")
            t2 = final_text(f"{A6}/{slug}/control/b{b}__all6__r2")
            if t1 and t2:
                pairs.append((f"{slug}/b{b}", t2, t1))  # x=r2 (r2のr1に対するスコア)
            else:
                skipped.append(f"{slug}/b{b}")
    res = run_pairs(pairs, f"{EV}/noise_pairwise_{model}.json", model)
    jdump({"model": model, "pairs": res, "skipped_no_pair": skipped}, f"{EV}/noise_result_{model}.json")


def noise_md(model=MAIN_JUDGE):
    d = jload(f"{EV}/noise_result_{model}.json")
    res = d["pairs"]
    designated = ["meta/b2", "hormuz/b4", "space_weapons/b3"]
    L = ["# NOISE_BASELINE(M4): S0 r1 対 r2 の同条件pairwise(委任_04c、2026-10-08)", "",
         f"judge={model}、判定文=EVAL_RULES_V2 M1の中立文、2順序。スコア=r2のr1に対する値(勝ち1/割れ0.5/負け0)。同一条件の2回生成どうしなので、差がなくてもこの程度は揺れる、の幅を測る。", "",
         "| pair | r2スコア | 順序別(1=r2勝,0.5=tie) | 割れ |", "|---|---|---|---|"]
    for k, v in res.items():
        L.append(f"| {k}{' (指定brief)' if k in designated else ''} | {v['x_score']} | {v['pts']} | {'割れ' if v['split'] else ''} |")
    L.append("")
    if d["skipped_no_pair"]:
        L += [f"両本文のある対がなく除外: {d['skipped_no_pair']}", ""]
    sc = {k: v["x_score"] for k, v in res.items()}
    ds = [sc[k] for k in designated if k in sc]
    by = [[v for k, v in sc.items() if k.startswith(s + "/")] for s in ("meta", "hormuz", "space_weapons")]
    trip = list(itertools.product(*by))
    sums = sorted(round(sum(t), 1) for t in trip)
    n = len(sums)
    up = sum(1 for t in trip if min(t) == 1.0 and sum(t) >= 2.5)
    dn = sum(1 for t in trip if max(t) == 0.0)
    L += [f"指定3brief(meta b2/hormuz b4/space_weapons b3)のr2スコア: {ds} 合計{sum(ds)}/3", "",
          f"全{n}通り(slugごとに1対を選ぶ3対の組)の合計スコア分布(0〜3): min={sums[0]} / 中央={sums[n // 2]} / max={sums[-1]}",
          f"M5規則(3 brief全勝=各1.0かつ合計>=2.5)を満たす組: {up}/{n}。全敗(各0.0): {dn}/{n}。=差がなくても「明確に上/下」と読まれる確率の目安。",
          f"割れ率(全{len(res)}対): {sum(1 for v in res.values() if v['split'])}/{len(res)}",
          f"**ノイズ幅(同条件の3 brief合計、0〜3): {sums[0]}〜{sums[-1]}**(中央値{sums[n // 2]})。変種の合計がこの幅の内側ならS0との差とノイズを区別できない、と読む。", "",
          "限界: 同一モデル(gpt-6-luna)・2生成のみ。r1/r2はbrief固定の別生成であり、判定のばらつきと生成のばらつきの合計。"]
    open(f"{EV}/NOISE_BASELINE.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    jdump({"band": [sums[0], sums[-1]], "median": sums[n // 2], "n_triples": n, "up_rate": up / n, "down_rate": dn / n}, f"{EV}/noise_band.json")
    print("\n".join(L))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    cmd = sys.argv[1]
    if cmd == "noise":
        noise()
        noise_md()
    elif cmd == "noise_md":
        noise_md()
    else:
        import eval_sweep_part2 as p2
        p2.main(cmd, sys.argv[2:])

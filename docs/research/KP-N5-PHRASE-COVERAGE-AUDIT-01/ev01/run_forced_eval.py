"""ev01 step3: 現行N5経路の部品(er138: select/pick/run_l3、いずれも無変更)に、対象Advancedの5表現(+他の句動詞・定型候補)を強制投入して評価する。
記事・音声の再生成なし。入力本文=公開Advancedと同一(text_sha256 937862fe...)。M10 untidi_b1b(N5現行・同一本文)の16候補pool(judged)をそのまま使い、
その末尾に強制候補(B1由来扱い)を足して、相対評価(包含dedupe・SEL keep・難易度順pick cap7)での挙動も見る。
usage: python run_forced_eval.py <repo_root>   (cwd=repo_root)。費用ガード: ev01実測合算が CAP を超える見込みなら実行しない。"""
import sys, os, json, glob
ROOT = os.path.abspath(sys.argv[1]); sys.path.insert(0, ROOT)
from dotenv import load_dotenv
load_dotenv("C:/Users/tensh/eigo-radio/.env")
EV = os.path.join(ROOT, "docs/research/KP-N5-PHRASE-COVERAGE-AUDIT-01/ev01")
CAP = float(os.environ.get("N5Q_CAP", "13.0"))
import er005_cost_logger as cl
import er053_cost_aggregate_01 as agg
import er138_kp_n5_generalization_01 as n5
import er003_v1_n3_01_scaffold_generate as sc
import er105_kp_fulltext_selector_01 as ft

def spent():
    return sum(agg.compute_stage_cost_breakdown_multi(p)["total_jpy"] for p in glob.glob(f"{EV}/cost_log*.jsonl"))

cl.install(f"{EV}/cost_log_forced.jsonl")
fx = json.load(open(f"{ROOT}/docs/research/KP-GENERALIZATION-N5-PRODUCTION-WIRING-01/fixtures/n5_trial_replay_fixture_01.json", encoding="utf-8"))
text = fx["cases"]["untidi_b1b"]["text"]
m10 = json.load(open(f"{ROOT}/docs/research/KP-GENERALIZATION-N5-PRODUCTION-WIRING-01/ev03/m10/untidi_b1b/result.json", encoding="utf-8"))
pool16 = [j["span"] for j in m10["doc"]["generalization"]["attempts"][0]["l1"][0]["judged"]]
assert len(pool16) == 16
ISO = ["put away", "put it away", "put that away", "putting something away", "in the way", "force it away", "leave it out", "Left out", "in sight",
       "No wonder", "bringing out", "relied on", "In other words", "in a way"]
INPOOL_EXTRAS = ["put away", "in the way", "force it away", "leave it out", "Left out", "in sight", "No wonder", "bringing out", "relied on"]
for s in ISO + INPOOL_EXTRAS:
    assert n5.span_in_text(s, text), s

def cands_of(spans, origin):
    cs = []
    for s in spans:
        c = {"span": s, "sentence": "", "n5_origin": origin}
        n5._fill_sentence(text, c)
        cs.append(c)
    return cs

def run_sel(tag, spans_with_origin):
    if spent() + 1.0 > CAP:
        raise SystemExit(f"cost guard: spent={spent():.2f} CAP={CAP}")
    ctx = n5.N5Ctx("B1_SUPPORT", tag=tag, stop_check_fn=sc.make_stop_check(EV), article_id="N5Q_untidi_b1b")
    log = n5.new_log(tag)
    cs = []
    for s, o in spans_with_origin:
        cs += cands_of([s], o)
    # collect_poolと同じ: 包含dedupeは本番ではpool構築時。ここでは強制投入なので包含関係は全候補をそのままSELに渡す(本番でdedupeされる場合は別途注記)
    with cl.logging_context(theme="N5Q_audit", stage=f"forced_{tag}"):
        judged = n5.select(text, cs, log, ctx)
    picked = n5.pick(judged, n5.PHRASE_PICK_CAP)
    return {"tag": tag, "judged": [{k: c.get(k) for k in ("span", "n5_origin", "cls", "chunk_type", "difficulty", "keep", "passive_fragment", "chunk_reason_ja", "sentence")} for c in judged],
            "picked_spans": [c["span"] for c in picked], "n_keep": sum(1 for c in judged if c["keep"]), "stages": log["stages"], "metas": ctx.metas}, judged

out = {"text_sha256": __import__("hashlib").sha256(text.encode("utf-8")).hexdigest(), "models": {s: n5.resolve_stage_model(s, "B1_SUPPORT") for s in ("b1", "sel", "gen5", "ver5", "chk5")},
       "prompt_sha16": n5.prompt_shas()}
res_iso, j_iso = run_sel("isolated", [(s, "B1") for s in ISO])
out["sel_isolated"] = res_iso
print("isolated: spent", round(spent(), 3)); sys.stdout.flush()
pool = [(s, "P7" if i < 6 else "B1") for i, s in enumerate(pool16)] + [(s, "B1") for s in INPOOL_EXTRAS]
res_p1, j_p1 = run_sel("inpool_r1", pool)
out["sel_inpool_r1"] = res_p1
print("inpool r1: spent", round(spent(), 3)); sys.stdout.flush()
res_p2, j_p2 = run_sel("inpool_r2", pool)
out["sel_inpool_r2"] = res_p2
print("inpool r2: spent", round(spent(), 3)); sys.stdout.flush()
json.dump(out, open(f"{EV}/forced_eval_sel.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# L3対象: 強制候補のうちいずれかのSEL runでkeepだった表現(重複はkey単位)。上限8、費用ガード
want = []
for j in j_iso + j_p1 + j_p2:
    if j["keep"] and j["span"] in set(ISO + INPOOL_EXTRAS) and j["span"] not in want:
        want.append(j["span"])
print("L3 candidates:", want)
# 同義の変種は代表1つ: put away系は 'put away' 優先、なければ最初
rep = []
for s in want:
    if s in ("put it away", "put that away", "putting something away") and any(r in ("put away",) for r in want):
        continue
    rep.append(s)
rep = rep[:8]
print("L3 targets:", rep)
if rep:
    if spent() + 0.7 * len(rep) + 0.3 > CAP:
        raise SystemExit(f"cost guard before L3: spent={spent():.2f} est={0.7*len(rep):.2f} CAP={CAP}")
    ctx = n5.N5Ctx("B1_SUPPORT", tag="forced_l3", stop_check_fn=sc.make_stop_check(EV), article_id="N5Q_untidi_b1b")
    tg = []
    for s in rep:
        c = {"span": s, "sentence": ""}; n5._fill_sentence(text, c)
        tg.append({"key": ft.phrase_key(s), "span": s, "sentence": c["sentence"], "prod_gloss": None, "n5_origin": "B1"})
    with cl.logging_context(theme="N5Q_audit", stage="forced_l3"):
        r = n5.run_l3(text, tg, ctx)
    out["l3"] = {"targets": tg, "kept": {k: n5.pack(v) for k, v in r["kept"].items()}, "dropped": r["dropped"],
                 "log_stages": r["log"].get("stages"), "metas": ctx.metas}
json.dump(out, open(f"{EV}/forced_eval_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print("DONE spent", round(spent(), 3))

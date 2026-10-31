"""Trial専用(非Production)。委任_01 原因確認probe: 同一記事本文に対し、現行B1抽出Promptの最小変種を各N回呼んで『抽出されない原因』を切り分ける。
Production module/Prompt/閾値/Gateは無変更(メモリ上でprompt文字列を作るのみ)。出力=ev01/probe_extract_result.json、費用=ev01/cost_log_probe.jsonl。
variants: L0 現行B1そのまま(対照) / L1 nodiff14(B1から難易度条件4,5を除去、最大14) / L2 nodiff30(同、最大30) / L3 enum_all(難易度不問の網羅列挙、最大40) /
          L4 enum_chunked(L3を本文3分割で各15) / L5 phrasal(句動詞を分離形・受動・-ing形も含め全箇所、最大30)
usage: python probe_extract_01.py <repo_root> <case_id> <N> <variants,comma> """
import sys, os, json, glob, re, time
ROOT = os.path.abspath(sys.argv[1]); sys.path.insert(0, ROOT)
CASE = sys.argv[2]; N = int(sys.argv[3]); VARS = sys.argv[4].split(",")
from dotenv import load_dotenv
load_dotenv("C:/Users/tensh/eigo-radio/.env")
TD = os.path.join(ROOT, "docs/research/KP-N5-EXTRACTION-ROOT-IMPROVEMENT-TRIAL-01"); EV = os.path.join(TD, "ev01")
CAP_STOP = float(os.environ.get("N5R_CAP_STOP", "20.0"))
import er005_cost_logger as cl, er053_cost_aggregate_01 as agg
import er138_kp_n5_generalization_01 as n5, er062_family_z_structure_01 as st
def spent():
    return sum(agg.compute_stage_cost_breakdown_multi(p)["total_jpy"] for p in glob.glob(f"{EV}/cost_log*.jsonl"))
cl.install(f"{EV}/cost_log_probe.jsonl")
fx = json.load(open(f"{ROOT}/docs/research/KP-GENERALIZATION-N5-PRODUCTION-WIRING-01/fixtures/n5_trial_replay_fixture_01.json", encoding="utf-8"))
text = fx["cases"][CASE]["text"]
BODY = n5.BODY
HEAD_COMMON = ("1. **本文一致(絶対条件)**: 本文中の連続した語句をそのまま抜き出す。変更・言い換え・創作は禁止。\n"
               "2. **5語以内(絶対条件)**: 6語以上は出力禁止。\n")
def p_L1(t, n=14):
    return (f"以下の記事から、英語上級者が学ぶ価値のあるフレーズ・表現・イディオム・句動詞・連語・定着した名詞句(2語以上の連続した語句)の**候補を最大{n}個**、広めに挙げてください(後段で絞り込みます。ランキングは不要)。\n\n"
            + HEAD_COMMON + "3. 意味と自然さを保てる最短の形で抜き出す。\n4. 難易度は問わない(易しい表現も除外しない。難易度・学習価値は後段で判定する)。\n"
            "同じ語句や、一方が他方を含む類似語句は重ねない。sentenceは本文中でその語句を含む文をそのまま書く。" + BODY + t)
def p_L3(t, n=40):
    return (f"以下の記事に含まれる、ひと塊で覚える対象になり得る表現を、本文から**漏れなく列挙**してください(最大{n}個)。対象は、句動詞(動詞+副詞/前置詞)、イディオム、固定表現、連語(コロケーション)、前置詞句の定型表現です。"
            "難易度や学習価値の高低で絞らず、基本語だけの表現も除外しないでください(絞り込みは後段で別に行います)。\n\n"
            + HEAD_COMMON + "3. 意味と自然さを保てる最短の形で抜き出す。\n"
            "同じ表現が本文の複数箇所にある場合は代表1箇所のみ。sentenceは本文中でその語句を含む文をそのまま書く。" + BODY + t)
def p_L5(t, n=30):
    return (f"以下の記事から、**句動詞(動詞+副詞/前置詞・小辞)が使われている箇所**を、最大{n}個、すべて抜き出してください。目的語が間に入る形(例: 動詞+代名詞+小辞)、受動形、-ing形、過去分詞形も対象に含めます。"
            "難易度は問いません(基本的な句動詞も除外しない)。\n\n"
            + HEAD_COMMON + "同じ句動詞が複数箇所にある場合は、本文の形が最も典型的な1箇所を選ぶ。sentenceは本文中でその語句を含む文をそのまま書く。" + BODY + t)
def chunks(t, k=3):
    sents = re.split(r"(?<=[.!?])\s+", t.strip()); per = -(-len(sents) // k)
    return [" ".join(sents[i:i + per]) for i in range(0, len(sents), per)]
PATS = {"put away": r"\bput\w*\b.{0,14}\baway\b", "in the way": r"in the way", "leave out": r"\b(leave|leaving|left)\b.{0,10}\bout\b", "in sight": r"in sight", "hear it out": r"hear.{0,6}out", "relied on": r"relied on|rely on", "gets heated": r"heated"}
out = {"case": CASE, "model": n5.resolve_stage_model("b1", "B1_SUPPORT"), "text_chars": len(text), "runs": {}}
def call(prompt, tag):
    if spent() + 0.6 > CAP_STOP: raise SystemExit("cost guard (stop at %.1f)" % CAP_STOP)
    st.check_stop_sentinel("n5r_probe", EV)
    ctx = n5.N5Ctx("B1_SUPPORT", tag=tag, stop_check_fn=lambda w: st.check_stop_sentinel(w, EV), article_id="N5R_" + CASE)
    with cl.logging_context("N5R_probe", tag):
        o, m = n5.call_llm("b1", prompt, n5.B1_SCHEMA, ctx, label="N5R_probe")
    return [c["span"] for c in o["candidates"]], m
for v in VARS:
    runs = []
    for i in range(N):
        t0 = time.time()
        if v == "L4":
            sp = []; cost = 0
            for ci, ch in enumerate(chunks(text)):
                s, m = call(p_L3(ch, 15), f"L4_{i+1}_{ci+1}"); sp += s; cost += m.get("cost_jpy") or 0
        else:
            pr = {"L0": lambda: n5.prompt_B1(text), "L1": lambda: p_L1(text, 14), "L2": lambda: p_L1(text, 30), "L3": lambda: p_L3(text), "L5": lambda: p_L5(text)}[v]()
            sp, m = call(pr, f"{v}_{i+1}"); cost = m.get("cost_jpy")
        hit = {k: any(re.search(p, s, re.I) for s in sp) for k, p in PATS.items()}
        runs.append({"sample": i + 1, "n": len(sp), "spans": sp, "hits": hit, "cost_jpy": cost, "sec": round(time.time() - t0, 1)})
        print(v, i + 1, len(sp), {k: int(b) for k, b in hit.items()}, "spent", round(spent(), 3)); sys.stdout.flush()
    out["runs"][v] = runs
fn = f"{EV}/probe_extract_result_{CASE}_{'-'.join(VARS)}.json"
json.dump(out, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("DONE spent", round(spent(), 3), fn)

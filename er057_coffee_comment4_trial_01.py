# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-STD-COMMENT4-BRIDGE-PROMPT-TRIAL-01 Trial専用(Production非経由、Prompt/定数不変)。
modes: prompts / gen / metrics / tts / asr / page"""
import os, sys, json, re, time, hashlib, concurrent.futures as cf
sys.path.insert(0, os.getcwd())
from dotenv import load_dotenv
load_dotenv()
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = f"{ROOT}/er057_output/coffee_comment4_trial_01"
TONE = r"C:\Users\tensh\eigo-radio-tone\er019_output\family_x_audio_production_wiring_01\coffee_prices__run_e_tone_01\a2"
import er019_family_x_audio_plan_01 as plan

C0 = plan.FAMILY_X_A2_COMMENT_4_ROLE
OLD_ROLE = """役割: 記事全体の意味を軽く回収し、In One Lineへつなぎます。本文を再説明し
すぎないでください。2〜3文にしてください。"""
assert OLD_ROLE in C0
NEW = {
 "C1": ("終盤感+聞き終え+英語結びへの接続を役割文へ明記(最小差)",
  """役割: 番組がいよいよ終盤に入り、本文をすべて聞き終えたことが聞き手に伝わるようにします。そのうえで記事全体の意味を軽く回収し、このあと英語による結びのまとめ(In One Line)を聞く流れへ自然につなぎます。本文を再説明しすぎないでください。2〜3文にしてください。"""),
 "C2": ("3要素の流れ指定(導入=聞き終え・終盤感 → 軽い回収 → 英語まとめへの橋渡し)。定型句は不要と明記",
  """役割: 次の流れで2〜3文にしてください。(1)本文を聞き終えたことに触れ、番組が終盤に入ったと感じられる導入。(2)記事全体の意味を軽く回収する(本文を再説明しすぎない)。(3)このあと英語で結びのまとめを聞くことへの橋渡し。決まった定型句を使う必要はありません。"""),
 "C3": ("最終文を橋渡し専用に固定(聞き手が「本文は終わり、次は英語のまとめ」と分かる)。特定語句の強制なし",
  """役割: 記事全体の意味を軽く回収し、In One Lineへつなぎます。最後の文は、英語による結びのまとめを聞く流れへの橋渡しにして、聞き手が「本文はここまでで、次は英語のまとめだ」と自然に分かるようにしてください。「最後に」など特定の言葉を使う必要はありません。本文を再説明しすぎないでください。2〜3文にしてください。"""),
 "C4": ("聞き手に区切りを与える役割+避けること(再説明・番組終了の挨拶・事務的つなぎのみ)を明示",
  """役割: 聞き手に「本文を聞き終えた」という区切りを与え、記事全体の意味を軽く回収して、英語による結びのまとめ(In One Line)へ橋渡しします。避けること: 本文の再説明や言い換え、番組全体を終えるような挨拶(「ありがとうございました」等)、「続いて〜」だけの事務的なつなぎ。2〜3文にしてください。"""),
}
ROLES = {"C0": C0, **{k: C0.replace(OLD_ROLE, v[1]) for k, v in NEW.items()}}
for k in NEW: assert ROLES[k] != C0
N = 3


def sha_s(s): return hashlib.sha256(s.encode("utf-8")).hexdigest()


def prompts():
    md = "# Comment 4 Prompt候補(C0=現行 FAMILY_X_A2_COMMENT_4_ROLE 逐語、C1-C4=役割文のみ差替)\n\n"
    for k, r in ROLES.items():
        desc = "現行(基準)" if k == "C0" else NEW[k][0]
        md += f"## {k} {desc}\n- 文字数 {len(r)} / sha256 {sha_s(r)}\n\n```\n{r}\n```\n\n"
    open(f"{OUT}/prompts/prompts_comment4.md", "w", encoding="utf-8").write(md)
    print("ok", {k: len(v) for k, v in ROLES.items()})


def ctx():
    p = json.load(open(f"{TONE}/parts.json", encoding="utf-8"))
    return f"【本文1】\n{p['part1']}\n\n【本文2】\n{p['part2']}\n\n【本文3】\n{p['part3']}"


def gen():
    import er003_v1_iran01_a2_generate as a2gen
    import er006_model_routing_contract_01 as routing
    model = routing.require_model("A2_SUPPORT", routing.SUPPORT_MODEL)
    client = a2gen.vfl01.get_client()
    usages = []
    orig = client.responses.create
    def wrapped(**kw):
        r = orig(**kw); u = getattr(r, "usage", None)
        usages.append({"model": r.model, "in": getattr(u, "input_tokens", 0), "out": getattr(u, "output_tokens", 0)})
        return r
    client.responses.create = wrapped
    c = ctx()
    jobs = [(k, i) for k in ROLES for i in range(1, N + 1)]
    def one(j):
        k, i = j
        r = a2gen.run_support_text(client, ROLES[k], c, model=model)
        return {"cand": k, "run": i, "status": r["status"], "text": r["text"], "model_id": (r["attempts"][-1].get("model")), "attempts": len(r["attempts"])}
    with cf.ThreadPoolExecutor(5) as ex: res = list(ex.map(one, jobs))
    with open(f"{OUT}/generations.jsonl", "w", encoding="utf-8") as f:
        for r in res: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    inp = sum(u["in"] or 0 for u in usages); out = sum(u["out"] or 0 for u in usages)
    jpy = (inp * 0.10 + out * 0.50) / 1e6 * 160
    json.dump({"routing_model": model, "response_models": sorted({u["model"] for u in usages}), "calls": len(usages), "in_tokens": inp, "out_tokens": out, "est_jpy": round(jpy, 4),
               "basis": "pricing_snapshot gpt-6-luna in0.10/out0.50 USD per M x160"}, open(f"{OUT}/cost_llm.json", "w"), indent=1)
    for r in res: print(r["cand"], r["run"], r["status"], r["text"])
    print("jpy", jpy, model)


RX = {
 "F終盤感": r"終盤|終わりに近|終わり|最後に|最後まで|結び|締めくくり|締め|聞き終",
 "L聞き終え": r"聞き終|最後まで聞|ここまで|たどってきました|見てきました|すべて",
 "B英語橋渡し(最終文に英語+聞く/振り返る)": None,
}
BAD = {"文数断定": r"一文|ひとこと|一言|one sentence", "構造ラベル": r"Part ?\d|Full Story|第\d部|本文\d",
       "番組終了挨拶": r"ありがとうございました|さようなら|またお会い|また次回|お別れ", "数字": r"[0-9０-９]"}


def sents(t): return [s for s in re.split(r"(?<=。)", t) if s.strip()]


def det(t):
    ss = sents(t); last = ss[-1]
    d = {"chars": len(t), "sentences": len(ss)}
    d["F終盤感"] = bool(re.search(RX["F終盤感"], t))
    d["L聞き終え"] = bool(re.search(RX["L聞き終え"], t))
    d["B英語橋渡し"] = bool("英語" in last and re.search(r"聞|振り返|確認|お聞き", last))
    d["recovery_chars(最終文除く)"] = len(t) - len(last)
    d["bad"] = [k for k, rx in BAD.items() if re.search(rx, t)]
    d["文数2-3"] = 2 <= len(ss) <= 3
    return d


def metrics():
    rows = [json.loads(l) for l in open(f"{OUT}/generations.jsonl", encoding="utf-8")]
    for r in rows: r["det"] = det(r["text"])
    json.dump(rows, open(f"{OUT}/metrics.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for r in rows:
        d = r["det"]; print(r["cand"], r["run"], d["chars"], d["sentences"], "F", int(d["F終盤感"]), "L", int(d["L聞き終え"]), "B", int(d["B英語橋渡し"]), d["recovery_chars(最終文除く)"], d["bad"])




REP = {"C1": 3, "C2": 1, "C3": 2, "C4": 2}
REP_REASON = {
 "C1": "3回中、終盤感/聞き終え/英語橋渡しの3軸を最も明確に満たしたのは run3(「これで記事の内容はすべて聞き終えました」「最後に、英語のまとめを」)。run1も満たすが回収が長め。回収2文のため再説明は△(注記)。",
 "C2": "3回とも3軸を満たす中で、run1は「本文を聞き終えて、番組も終盤に入りました」「英語で記事の結びを聞いていきましょう」が最も口語的で自然(run2は『値段が伝わるまで』がやや不自然、run3は『お聞きください』がやや硬い)。",
 "C3": "3回とも橋渡し(B)は満たすが終盤感なし。run2が最も自然で文のねじれがない(run1は文がねじれ不自然)。",
 "C4": "3回とも橋渡しは満たすが終盤感なし。run2は聞き終え感(たどってきました)があり不自然さが最小。",
}


def r2_style():
    import er057_ja_aoede_style_trial_02 as J
    return J.R["R2"][2]


def tts():
    import er057_tone_trial_kp_ja_gen_01 as g
    import er057_ja_aoede_style_trial_02 as J
    import er003_v1_n3_01_tts_generate as n3
    import er003_audio_tts_asr_safety as safety
    rows = {(r["cand"], r["run"]): r for r in map(json.loads, open(f"{OUT}/generations.jsonl", encoding="utf-8"))}
    style = r2_style()
    g.RAW = f"{OUT}/raw"; g.call_tts = J.call_tts_mv
    jobs = []
    for c, n in REP.items():
        t = rows[(c, n)]["text"]
        jobs.append({"id": f"{c}_run{n}", "spec": "R2", "grp": "D", "text": safety.to_tts_safe_japanese_fraction_reading(n3.tts_safe_ja(t)), "style": style,
                     "voice": g.VOICE_JA, "margin": g.JA_MARGIN, "lang": "ja", "manuscript": t})
    with cf.ThreadPoolExecutor(4) as ex: res = list(ex.map(g.gen_one, jobs))
    pt = ct = 0
    for r, j in zip(res, jobs):
        r["manuscript"] = j["manuscript"]; r["style_name"] = "R2"; r["style_sha256"] = sha_s(style)
        for u in r.get("usage") or []:
            if u: pt += u.get("prompt_tokens") or 0; ct += u.get("candidates_tokens") or 0
    usd = ct * g.PRICE_OUT_PER_M / 1e6 + pt * g.PRICE_IN_PER_M / 1e6
    with open(f"{OUT}/tts_results.jsonl", "w", encoding="utf-8") as f:
        for r in res: f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")
    json.dump({"reps": REP, "reason": REP_REASON}, open(f"{OUT}/selection.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"prompt_tokens": pt, "candidates_tokens": ct, "est_usd": round(usd, 5), "est_jpy": round(usd * g.USD_JPY, 2), "model": g.MODEL, "voice": g.VOICE_JA}, open(f"{OUT}/cost_tts.json", "w"), indent=1)
    for r in res: print(r["id"], r["status"], r.get("duration_s"), r.get("reason", ""), r.get("usage"))
    print("jpy", usd * g.USD_JPY)


def asr():
    import er006_asr_provider_routing_01 as routing
    import er007_ja_asr_validator_01 as javal
    res = [json.loads(l) for l in open(f"{OUT}/tts_results.jsonl", encoding="utf-8")]
    out = []
    for r in res:
        if r["status"] != "OK": continue
        t, err = routing.transcribe(f"{OUT}/raw/{r['id']}.wav", language="ja-JP")
        c = javal.classify_ja_asr_match(r["text"], t)
        out.append({"id": r["id"], "canonical": r["text"], "asr_text": t, "asr_error": err, "classification": c.classification, "should_pass": c.should_pass})
    # 参考: 既存R2_comment_4(C0文・R2)
    import er057_ja_aoede_style_trial_02 as J
    for l in open(f"{J.OUT}/asr_results_01.jsonl", encoding="utf-8"):
        x = json.loads(l)
        if x["id"] in ("R2_comment_4", "P2_comment_4"): out.append({**x, "note": "既存(再生成せず再利用)"})
    with open(f"{OUT}/asr_results.jsonl", "w", encoding="utf-8") as f:
        for r in out: f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")
    for r in out: print(r["id"], r["classification"], r["should_pass"], "|", r["asr_text"])


if __name__ == "__main__":
    {"prompts": prompts, "gen": gen, "metrics": metrics, "tts": tts, "asr": asr}[sys.argv[1]]()

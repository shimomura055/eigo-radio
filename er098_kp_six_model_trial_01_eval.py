# -*- coding: utf-8 -*-
"""FAMILY-X-KP-SELECTION-SIX-MODEL-COMPARISON-TRIAL-01 委任_01: 独立評価(有料)。Trial専用。
各本文について、6モデルの選定結果+既存Production KP(計7セット)を、モデル名を伏せて(set IDをシャッフル)
独立評価モデル2系統(gpt-6.1-sol / claude-sonnet-5-5)が共通rubric(TRIAL_DESIGN_01.md 6節)で採点する。
選定元モデルによる自己評価は行わない(同系統の評価は『参考』扱いで集計側が区別する)。
使い方: .venv\\Scripts\\python.exe er098_kp_six_model_trial_01_eval.py --cap-jpy 300 [--evaluators sol,sonnet] [--units ...] [--sol-effort low|medium|high]"""
import argparse, json, random, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import er098_kp_six_model_trial_01_common as C

EVALUATORS = {"sol": dict(provider="openai", model_id="gpt-6.1-sol"), "sonnet": dict(provider="anthropic", model_id="claude-sonnet-5-5")}

RUBRIC = """あなたは英語学習コンテンツの独立評価者です。以下の英語記事から「英語上級者が学ぶ価値のあるKey Phrase」を選ぶ課題があり、
複数の匿名の選定結果(セット S1〜Sn、各5件以内)があります。各候補を下記rubricで採点してください。どのセットがどのモデルの結果かは不明です。

【選定時に参加者へ与えられた条件(参考)】
1. 本文中の連続した語句だけを抜き出す(一般化以外の変更・言い換え・追加・創作は禁止)。
2. 一般化後5語以内。
3. 固有名詞や特定の人物・物事を指す部分は、意味と文法を保って ~ / A / B / someone / something 等に置き換える(一般化できる場合は必ず行う)。
4. 上級者でも学ぶ価値のある語彙・イディオム・慣用表現を優先する。
5. 基本語だけで構成され字面どおりに意味が分かる表現や、上級者なら知っている易しい表現は除外する。
6. 条件を満たす候補から5件選ぶ。適切な候補が不足する場合のみ5件未満とし、数合わせはしない。

【採点rubric(各候補、各0〜2の整数)】
- G 一般化の適切さ: 2=本文固有の固有名詞・特定の人物/物事が適切に一般化されている、または一般化すべき要素がなく原文のままで適切 / 1=一般化が不十分または過剰、あるいは軽微な不自然さ / 0=一般化すべき固有要素が残って学習価値を損なう、または一般化で意味・文法が壊れている。
- V 上級者向け学習価値: 2=上級者でも学ぶ価値が明確(句動詞・イディオム・コロケーション・語法・語彙として) / 1=価値はあるが中程度、または一部平易 / 0=学習価値がほぼない。
- E 易しさの排除: 2=易しい表現ではない(意味が字面から自明でない) / 1=やや易しいが慣用的な意味や語法の学びはある / 0=基本語のみで字面どおり、上級者なら当然知っている。
- N 単位の自然さ: 2=自然で完結した学習単位 / 1=余分な語または不足があるが許容 / 0=中途半端に切られている・不自然。
- needs_generalization: その候補の元の表現に、一般化(~, A/B, someone, something等)すべき要素が本文上あったか(true/false)。
セット単位: padding = 5件を埋めるために学習価値の低い候補(V<=0またはE<=0)を入れていると判断するか(true/false)。

【注意】
- 本文との一致・語数は別途機械検証するため、ここでは採点対象外。ただし本文に明らかに存在しない表現と気付いた場合のみ noteに "not_in_text" と書く。
- 候補の優劣を、セットの並び順やセットIDから推測しない。各候補を独立に採点する。
- 候補が0件のセットは candidates を空配列にする。

【出力】JSONのみ(説明文・コードフェンス不要)。noteは通常は空文字、本文に存在しない表現と気付いた場合のみ "not_in_text"。形式:
{"sets":[{"set_id":"S1","padding":false,"candidates":[{"idx":1,"G":2,"V":2,"E":1,"N":2,"needs_generalization":false,"note":""}]}]}
"""

def build_user(article, sets):
    lines = [RUBRIC, "\n【記事】\n", article, "\n\n【匿名の選定結果】\n"]
    for sid, cands in sets:
        lines.append("%s:" % sid)
        if not cands: lines.append("  (候補なし)")
        for i, c in enumerate(cands): lines.append("  %d. %s" % (i + 1, c))
        lines.append("")
    return "\n".join(lines)

def extract_json(text):
    s = text.strip()
    s = re.sub(r"^```(?:json)?|```$", "", s, flags=re.M).strip()
    i = s.find("{"); j = s.rfind("}")
    return json.loads(s[i:j + 1])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap-jpy", type=float, default=300.0); ap.add_argument("--evaluators", default="sol,sonnet")
    ap.add_argument("--units", default=""); ap.add_argument("--sol-effort", default="")
    ap.add_argument("--workers", type=int, default=4); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    out = C.OUT; man = json.loads((out / "inputs" / "manifest.json").read_text(encoding="utf8"))
    val = json.loads((out / "validation.json").read_text(encoding="utf8"))
    units = [u for u in man["units"] if u.get("copy_path") and (not a.units or u["unit_id"] in a.units.split(","))]
    if C.stop_present(out): print("STOP"); return 3
    (out / "eval").mkdir(parents=True, exist_ok=True)
    bm_path = out / "eval" / "blind_map.json"
    bmap = json.loads(bm_path.read_text(encoding="utf8")) if bm_path.exists() else {}
    jobs = []
    for u in units:
        uid = u["unit_id"]
        srcs = [s for s in val["sets"] if s["unit_id"] == uid and s["status"] == "OK"]
        if uid not in bmap:
            order = [s["source"] for s in srcs]; random.Random("er098:" + uid).shuffle(order)
            bmap[uid] = {("S%d" % (i + 1)): o for i, o in enumerate(order)}
        sets = []
        for sid, src in bmap[uid].items():
            s = next(x for x in srcs if x["source"] == src)
            sets.append((sid, [c["phrase"] for c in s["candidates"]]))
        art = (C.ROOT / u["copy_path"]).read_text(encoding="utf8")
        user = build_user(art, sets)
        for ev in a.evaluators.split(","):
            rp = out / "eval" / ev / ("%s.json" % uid)
            if rp.exists(): continue
            jobs.append((ev, uid, user, rp))
    bm_path.write_text(json.dumps(bmap, ensure_ascii=False, indent=1), encoding="utf8")
    print("eval jobs", len(jobs))
    if a.dry_run:
        print(jobs[0][2][:3000] if jobs else ""); return 0
    def run(job):
        ev, uid, user, rp = job
        if C.stop_present(out): return (ev, uid, "STOPPED", 0)
        if C.ledger_total_jpy() >= a.cap_jpy: return (ev, uid, "CAP_REACHED", 0)
        e = EVALUATORS[ev]
        extra = {"reasoning": {"effort": a.sol_effort}} if (ev == "sol" and a.sol_effort) else None
        body = C.build_body(e["provider"], e["model_id"], user, extra=extra)
        t0 = time.time(); r = C.call_with_retry(e["provider"], e["model_id"], body)
        rec = dict(evaluator=ev, requested_model_id=e["model_id"], unit_id=uid, user_message_sha256=C.sha_text(user), request_body=body,
                   settings=dict(temperature="provider_default", reasoning=("effort=%s" % a.sol_effort) if extra else "provider_default", max_tokens=C.MAX_OUT),
                   attempts=r["attempts"], ok=r["ok"], elapsed_s_total=round(time.time() - t0, 2))
        cost = 0.0
        if r["ok"]:
            cost = C.cost_usd(e["model_id"], r["usage"]) * C.USD_JPY
            try: parsed = extract_json(r["text"])
            except Exception as ex: parsed = None; rec["parse_error"] = str(ex)
            rec.update(response_text=r["text"], parsed=parsed, usage=r["usage"], response_id=r["response_id"], model_returned=r["model_returned"], finish=r["finish"],
                       cost_jpy=round(cost, 5), raw_response=r["raw"])
            C.ledger_add(dict(phase="eval", evaluator=ev, unit_id=uid, requested=e["model_id"], returned=r["model_returned"], usage=r["usage"], cost_jpy=round(cost, 5),
                              response_id=r["response_id"], ts=time.strftime("%Y-%m-%dT%H:%M:%S")))
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf8")
        return (ev, uid, "OK" if r["ok"] else "TECH_FAIL", cost)
    with ThreadPoolExecutor(max_workers=a.workers * 2) as ex:
        for f in as_completed([ex.submit(run, j) for j in jobs]):
            print(f.result(), "cum_jpy=%.3f" % C.ledger_total_jpy(), flush=True)
    return 0

if __name__ == "__main__":
    sys.exit(main())

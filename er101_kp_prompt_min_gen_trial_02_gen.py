# -*- coding: utf-8 -*-
r"""KPMG Trial②: Luna選定(Trial①出力そのまま=Before)を別LLM(claude-haiku-5-5)で一般化(有料)。再選定させない。1本文=1呼出(5件まとめて)。
使い方: .venv\Scripts\python.exe er101_kp_prompt_min_gen_trial_02_gen.py --cap-jpy 300 [--dry-run]。既存gen/<unit>.jsonはスキップ。"""
import argparse, json, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
import er101_kp_prompt_min_gen_trial_02_common as K
C = K.C
GEN = dict(provider="anthropic", model_id="claude-haiku-5-5")
SRC = "n1_gpt-6-luna"
FMT = ("【出力形式(受け渡し用の指定)】JSON配列のみを出力(説明文・コードフェンス不要)。要素は入力と同じ順序・同じ件数で、"
       "{\"no\": 番号, \"before\": 変更前(入力のKey Phraseそのまま), \"after\": 変更後, \"reason\": 変更理由(変更しない場合はその旨)}。")

def sentence_of(art, s, e):
    if s is None: return None
    a = max(art.rfind(x, 0, s) for x in (". ", "! ", "? ", "\n"))
    a = 0 if a < 0 else a + 1
    ends = [i for i in (art.find(x, e) for x in (". ", "! ", "? ", "\n")) if i >= 0]
    b = (min(ends) + 1) if ends else len(art)
    return art[a:b].strip()

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--cap-jpy", type=float, default=300.0); ap.add_argument("--dry-run", action="store_true"); a = ap.parse_args()
    out = K.OUT; man = json.loads((out / "inputs" / "manifest_from_kp6m.json").read_text(encoding="utf8"))
    val = json.loads((out / "validation.json").read_text(encoding="utf8"))
    prompt = (out / "inputs" / "gen_prompt_fixed.txt").read_text(encoding="utf8")
    if K.stop_present(): print("STOP"); return 3
    jobs = []
    for u in man["units"]:
        s = next(x for x in val["sets"] if x["source"] == SRC and x["unit_id"] == u["unit_id"])
        art = (C.ROOT / u["copy_path"]).read_text(encoding="utf8")
        lines = []
        for c in s["candidates"]:
            ctx = sentence_of(art, c.get("span_start"), c.get("span_end"))
            lines.append("%d. %s\n   本文中の該当文(参考情報): %s" % (c["rank"], c["phrase"], ctx if ctx else "(該当文を特定できず)"))
        user = prompt + "\n\n---\n\n【Key Phrase一覧】\n" + "\n".join(lines) + "\n\n" + FMT
        rp = out / "gen" / ("%s.json" % u["unit_id"])
        if not rp.exists(): jobs.append((u["unit_id"], user, rp, s))
    print("jobs", len(jobs))
    if a.dry_run: print(jobs[0][1]); return 0
    def run(job):
        uid, user, rp, s = job
        if K.stop_present(): return (uid, "STOPPED", 0)
        if C.ledger_total_jpy() >= a.cap_jpy: return (uid, "CAP_REACHED", 0)
        body = C.build_body(GEN["provider"], GEN["model_id"], user)
        t0 = time.time(); r = C.call_with_retry(GEN["provider"], GEN["model_id"], body)
        rec = dict(unit_id=uid, requested_model_id=GEN["model_id"], user_message_sha256=C.sha_text(user), gen_prompt_sha256=C.sha_text(prompt), user_message=user, request_body=body,
                   before_phrases=[c["phrase"] for c in s["candidates"]], attempts=r["attempts"], ok=r["ok"], elapsed_s_total=round(time.time() - t0, 2))
        cost = 0.0
        if r["ok"]:
            cost = C.cost_usd(GEN["model_id"], r["usage"]) * C.USD_JPY
            t = r["text"]; parsed = None
            try:
                t2 = re.sub(r"^```(?:json)?|```$", "", t.strip(), flags=re.M).strip(); parsed = json.loads(t2[t2.find("["):t2.rfind("]") + 1])
            except Exception as ex: rec["parse_error"] = str(ex)
            rec.update(response_text=t, parsed=parsed, usage=r["usage"], response_id=r["response_id"], model_returned=r["model_returned"], finish=r["finish"], cost_jpy=round(cost, 5), raw_response=r["raw"])
            C.ledger_add(dict(phase="generalization", unit_id=uid, requested=GEN["model_id"], returned=r["model_returned"], usage=r["usage"], cost_jpy=round(cost, 5), response_id=r["response_id"], ts=time.strftime("%Y-%m-%dT%H:%M:%S")))
        rp.parent.mkdir(parents=True, exist_ok=True); rp.write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf8")
        return (uid, "OK" if r["ok"] else "TECH_FAIL", cost)
    with ThreadPoolExecutor(max_workers=7) as ex:
        for f in as_completed([ex.submit(run, j) for j in jobs]): print(f.result(), "cum_jpy=%.3f" % C.ledger_total_jpy(), flush=True)
    return 0
if __name__ == "__main__": sys.exit(main())

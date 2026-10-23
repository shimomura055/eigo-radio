# -*- coding: utf-8 -*-
"""委任_07 T-4: Production関数 generate_kp_explanations を DEV注入(call_fn)で実行する KP説明段のtext E2E(TTSなし)。
Production fileに注入コードは残さない(call_fnはProduction公開引数)。対象=既存Production run(X/Z)の実Advanced Key Phrase item(used_form/source_sentence/gloss)。
armごとのretry発動(parse/QA)・語数/新規Fact fallback・最終status・費用を記録。開始/終了時にProduction module sha256をHEAD blobと照合。
"""
from __future__ import annotations
import hashlib, json, subprocess, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT)); sys.stdout.reconfigure(encoding="utf-8")
import er112_kp_gm_trial_02 as T
import er112_kp_gm_trial_01 as tr
import er019_family_x_kp_explanation_01 as kx

OUTJ = T.OUT / "e2e_kp_expl_02.jsonl"
PROD = tr.PROD_FILES + ["er112_kp_gm_trial_02.py"]


def head_hash(p):
    try:
        b = subprocess.run(["git", "show", "HEAD:" + p], cwd=ROOT, capture_output=True, check=True).stdout
        return hashlib.sha256(b).hexdigest()
    except Exception:
        return None


def hashes():
    h = tr.prod_hashes()
    return {p: dict(work=h.get(p), head_blob_sha256_lf=head_hash(p)) for p in tr.PROD_FILES}


def make_call_fn(arm, n):
    def call_fn(user_message):
        msg = user_message
        if arm != "E0":
            m2 = T._REF_ROW.sub("", msg)
            assert m2 != msg and T._REF_RULE in m2
            msg = m2.replace(T._REF_RULE, "", 1)
            rule = T.RULE_E4 if arm == "E4" else ""
            if rule:
                msg = msg.replace("\nKey Phrases:\n", rule + "\nKey Phrases:\n", 1)
        sch = T.expl_schema(arm if arm != "E0" else "E1")
        sch["schema"]["properties"]["explanations"]["minItems"] = n
        sch["schema"]["properties"]["explanations"]["maxItems"] = n
        r = T.client().responses.create(model=T.LUNA, reasoning={"effort": kx.REASONING_EFFORT}, text={"format": {"type": "json_schema", **sch}},
                                        input=[{"role": "developer", "content": kx.DEVELOPER_MESSAGE}, {"role": "user", "content": msg}])
        c, u = T.cost_of(r, T.LUNA)
        T.ledger_add(dict(kind="e2e_expl", arm=arm, usage=u, cost_jpy=round(c, 5), ts=time.strftime("%Y-%m-%dT%H:%M:%S")))
        raw = r.output_text
        # key位置(OF-13): 生出力のキー順を記録
        keys_order = list(json.loads(raw)["explanations"][0].keys()) if raw else None
        call_fn.last_keys = keys_order
        return json.loads(raw), r.model, u, r.id
    return call_fn


def runs():
    import er112_kp_gm_kpset_02 as K
    cen = json.load(open(K.CENSUS, encoding="utf-8"))
    seen, out = set(), []
    for x in cen:
        if x["level"] != "b1b" or (x["run"], x["level"]) in seen:
            continue
        seen.add((x["run"], x["level"]))
        p = ROOT / x["run"] / x["level"] / "key_phrases" / "keywords_canonicalized.json"
        if not p.exists():
            continue
        its = [it for it in json.load(open(p, encoding="utf-8"))["items"] if it.get("source_sentence") and it.get("japanese_gloss")]
        if its:
            out.append((x["family"], x["run"], its))
    return out


def main(arms, cap):
    h0 = hashes()
    rows = []
    for fam, run, its in runs():
        items = [{"rank": it["rank"], "display_phrase": kx.explanation_phrase(it), "source_sentence": it.get("source_sentence", ""),
                  "japanese_gloss": it.get("japanese_gloss", "")} for it in sorted(its, key=lambda x: x["rank"])]
        for arm in arms:
            if T.total() >= cap or T.stop():
                print("CAP/STOP", T.total()); break
            cf = make_call_fn(arm, len(items))
            t0 = time.time()
            try:
                res = kx.generate_kp_explanations(items, call_fn=cf)
                st = {r: v["status"] for r, v in res["items"].items()}
                rec = dict(family=fam, run=run, arm=arm, n=len(items), status=st, retried_for_parse=res["audit"]["retried_for_parse"],
                           retried_for_qa=res["audit"]["retried_for_qa"], calls=len(res["audit"]["calls"]),
                           words=[len((v["english_explanation"] or "").split()) for v in res["items"].values()],
                           texts={r: v["english_explanation"] for r, v in res["items"].items()}, key_order=getattr(cf, "last_keys", None), elapsed_s=round(time.time() - t0, 1))
            except Exception as e:   # ExplanationGenerationError等(fail-closed)の記録
                rec = dict(family=fam, run=run, arm=arm, n=len(items), error=type(e).__name__ + ":" + str(e)[:200])
            T._append_line(OUTJ, rec)
            rows.append(rec)
            print(fam, arm, rec.get("status") or rec.get("error"), "retry(parse,qa)=", rec.get("retried_for_parse"), rec.get("retried_for_qa"), "cum=%.3f" % T.total(), flush=True)
    h1 = hashes()
    json.dump(dict(start=h0, end=h1, identical=(h0 == h1), work_equals_head=all(v["work"] is not None for v in h1.values())), open(T.OUT / "production_hash_02.json", "w"), indent=1)
    print("production hash start==end:", h0 == h1)


if __name__ == "__main__":
    main(sys.argv[1].split(","), float(sys.argv[2]) if len(sys.argv) > 2 else 66.0)

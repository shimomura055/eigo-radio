# -*- coding: utf-8 -*-
"""FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_14: X/Z DEV注入 text E2E(TTSなし)。DEV専用、Production fileは編集しない(プロセス内attribute差し替えのみ)。
連鎖: canonicalization(possessor_roles + 決定論写像/修復) -> gloss再整合/新規生成(Production関数) -> [DEV注入] 独立検査(inspect) -> flag項目のみ attempt 2 で再生成
      -> (b1bのみ) Adv説明(Production関数)。retry/fallbackは各Production機構のまま。検査callの技術失敗は検査をスキップ(fail-open)し SKIPPED_TECH_FAIL を記録、
      attempt 2で採用済みの項目は FLAGGED_UNREPAIRED_NO_ATTEMPT、再生成が検証失敗なら元のglossを採用し FLAGGED_UNREPAIRED。
`install_e2e_patches()`を明示的に呼ぶまで何も差し替えない(既定OFF)。
サブコマンド: run / signature
"""
from __future__ import annotations

import argparse, json, os, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

os.environ.setdefault("KP04_INSPECT_VERSION", "v2")
os.environ.setdefault("KP04_INSPECT_EFFORT", "low")
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")
import er112_kp_gm_trial_04 as X                    # noqa: E402
import er112_kp_gm_trial_04_c as C                  # noqa: E402
import er112_kp_gm_trial_01 as t1                   # noqa: E402
import er112_kp_gm_poss_04 as P                     # noqa: E402
import er003_key_words_gloss_alignment as ga        # noqa: E402

OUT = X.OUT
RUNS = OUT / "e2e_runs"
INSP_LOGS: dict = {}
_LOCK = threading.Lock()
_ORIG: dict = {}
_INSTALLED = False
E2E_ARMS = {"a1ri": dict(a1=True, a2=False, a3=False, share=False, ctx=False, poss=True, insp=True)}


def install_e2e_patches():
    global _INSTALLED
    if _INSTALLED:
        return
    P.install_poss_patches(mode="role")
    t1.ARMS.update({k: dict(v) for k, v in E2E_ARMS.items()})
    _ORIG["gate"] = ga.run_alignment_gate_corrected
    orig = _ORIG["gate"]

    def e_gate(make_factory_for, targets, article_text, rules, mapping_gate=False, max_attempts=ga.MAX_GLOSS_ALIGNMENT_ATTEMPTS):
        gate = orig(make_factory_for, targets, article_text, rules, mapping_gate=mapping_gate, max_attempts=max_attempts)
        c = t1.cur()
        if not (c and c.cfg.get("insp")):
            return gate
        key = (c.arm, c.rep, c.unit)
        log = dict(status="NO_CANDIDATES", items={})
        adopted = gate["adopted"]
        cand = [t for t in targets if t["rank"] in adopted and ga.is_fulltext_gloss_missing(t)]
        if cand:
            rows = [dict(key_phrase=t["key_phrase"], source_sentence=t.get("source_sentence", ""), gloss=adopted[t["rank"]]["adopt_gloss"]) for t in cand]
            try:
                outs, cost, usage = X.inspect_call(rows)
                X.ledger_add(dict(kind="inspect", tag="e2e", n=len(rows), usage=usage, cost_jpy=round(cost, 5), unit=c.unit, ts=time.strftime("%Y-%m-%dT%H:%M:%S")))
            except Exception as e:      # noqa: BLE001  検査の技術失敗はスキップ(fail-open)
                log.update(status="SKIPPED_TECH_FAIL", error=f"{type(e).__name__}: {e}")
                with _LOCK:
                    INSP_LOGS.setdefault(key, []).append(log)
                return gate
            flagged, pend = [], []
            for t, o in zip(cand, outs):
                rank = t["rank"]
                rec = dict(inspect=o, flagged=C.is_flag(o), before=adopted[rank]["adopt_gloss"], adopted_attempt=adopted[rank]["attempt"])
                log["items"][str(rank)] = rec
                if rec["flagged"]:
                    flagged.append(rank)
                    if adopted[rank]["attempt"] >= ga.MAX_GLOSS_ALIGNMENT_ATTEMPTS:
                        rec["usage_check"] = "FLAGGED_UNREPAIRED_NO_ATTEMPT"
                    else:
                        pend.append((t, o))
            log["status"] = "INSPECTED"
            if pend:
                prior = {t["rank"]: {"gloss": adopted[t["rank"]]["adopt_gloss"], "reasons": [C.reason_text(o)]} for t, o in pend}
                tg = [dict(t) for t, o in pend]
                msg = ga.build_user_message_corrected(tg, article_text, rules, prior=prior)
                fn = make_factory_for(msg)
                try:
                    raw, model_id, rid = fn()
                    parsed = json.loads(raw)
                    by = {it["rank"]: it for it in parsed.get("items", []) if isinstance(it, dict) and isinstance(it.get("rank"), int)}
                except Exception as e:      # noqa: BLE001
                    by = {}
                    log["regen_error"] = f"{type(e).__name__}: {e}"
                for t, o in pend:
                    v = ga.validate_item_corrected(by.get(t["rank"]), t, mapping_gate=mapping_gate)
                    rec = log["items"][str(t["rank"])]
                    if v["valid"]:
                        gate["adopted"][t["rank"]] = {**v, "attempt": 2}
                        rec["usage_check"] = "REPAIRED"
                        rec["after"] = v["adopt_gloss"]
                    else:
                        rec["usage_check"] = "FLAGGED_UNREPAIRED"
                        rec["regen_reasons"] = v["reasons"]
                        rec["after_rejected"] = v.get("proposed_gloss")
            log["n_flagged"] = len(flagged)
            for r, rec in log["items"].items():
                rec.setdefault("usage_check", "FLAGGED" if rec["flagged"] else "NOT_FLAGGED")
        with _LOCK:
            INSP_LOGS.setdefault(key, []).append(log)
        return gate

    ga.run_alignment_gate_corrected = e_gate
    _INSTALLED = True


def uninstall_e2e_patches():
    global _INSTALLED
    if not _INSTALLED:
        return
    ga.run_alignment_gate_corrected = _ORIG["gate"]
    P.uninstall_poss_patches()
    _INSTALLED = False


UNIT_SEL = {"X": ["uk_train_speaker_playb"], "Z": ["Z_melos_run_kpq_01__"]}


def cmd_run(a):
    t1.LEDGER = X.LEDGER
    install_e2e_patches()
    start_h = t1.prod_hashes()
    hs = OUT / "production_hash_start.json"
    if hs.exists():
        assert json.loads(hs.read_text(encoding="utf-8")) == start_h, "Production module hash drift since Trial start"
    else:
        hs.write_text(json.dumps(start_h, indent=1), encoding="utf-8")
    units = json.load(open(t1.UNITS_PATH, encoding="utf-8"))["units"]
    pick = []
    for fam, subs in UNIT_SEL.items():
        us = [u for u in units if u["family"] == fam and any(s in u["unit_id"] for s in subs)]
        us.sort(key=lambda u: 0 if u["level"] == "a2" else 1)
        pick.append(us)
    print("units:", [[u["unit_id"] for u in us] for us in pick])

    def w(us):
        outs = []
        for u in us:
            if X.stop() or X.total() >= a.cap:
                outs.append((u["unit_id"], "SKIP"))
                continue
            rec = t1.run_unit("a1ri", 1, u, out_root=RUNS)
            d = RUNS / "a1ri" / "rep1" / u["unit_id"]
            with P._LOG_LOCK:
                lg = P.LOGS.get(("a1ri", 1, u["unit_id"]))
            if lg is not None:
                (d / "poss_log.json").write_text(json.dumps(lg, ensure_ascii=False, indent=1), encoding="utf-8")
            with _LOCK:
                il = INSP_LOGS.get(("a1ri", 1, u["unit_id"]))
            if il is not None:
                (d / "usage_check_log.json").write_text(json.dumps(il, ensure_ascii=False, indent=1), encoding="utf-8")
            outs.append((u["unit_id"], rec.get("canon_status"), rec.get("gloss_alignment_status"), rec.get("error")))
        return outs
    with ThreadPoolExecutor(2) as ex:
        for f in as_completed([ex.submit(w, us) for us in pick]):
            print(f.result(), "cum=%.3f" % X.total(), flush=True)
    end_h = t1.prod_hashes()
    (OUT / "production_hash_end_e2e.json").write_text(json.dumps(end_h, indent=1), encoding="utf-8")
    print("production_hash_unchanged:", start_h == end_h)


def _load_x_resolve():
    """Production `_resolve_kp_explanations_text`(X runner)のsourceをastで取り出し、API呼出スタブの名前空間でexecする(runner moduleのimportは環境依存の外部SDKを要するため回避。関数本体は無改変)。"""
    import ast, types
    import er019_family_x_kp_explanation_01 as kx
    src = (ROOT / "er019_family_x_audio_production_runner_01.py").read_text(encoding="utf-8")
    fn = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == "_resolve_kp_explanations_text")
    called = {"n": 0}

    def stub(input_items, **kw):
        called["n"] += 1
        return {"items": {}, "audit": {}, "stub": True}
    ns = {"kp_explanation_gen": types.SimpleNamespace(explanation_phrase=kx.explanation_phrase, generate_kp_explanations=stub)}
    exec(ast.get_source_segment(src, fn), ns)
    return ns["_resolve_kp_explanations_text"], called, kx


def _z_sig(items, kx):
    """Z runner `stage_kp`(er026_family_z_fiction_production_runner_01.py:1575-1581)の署名式と同一(複写。source_reference_contract無しのitem)。"""
    import hashlib
    sp = [kx.explanation_phrase(it) for it in items]
    if any(it.get("gloss_alignment_status") for it in items):
        sp = {"display": sp, "gloss": [it.get("japanese_gloss", "") for it in items]}
    return hashlib.sha256(json.dumps(sp, ensure_ascii=False).encode("utf-8")).hexdigest()


def cmd_signature(a):
    """signature変化でAdv説明が再生成されること(API呼出なし)。before=Production記録出力、after=E2E a1ri出力。X=Production関数そのもの、Z=署名式の複写。"""
    resolve, called, kx = _load_x_resolve()
    units = {u["unit_id"]: u for u in json.load(open(t1.UNITS_PATH, encoding="utf-8"))["units"]}
    res = []
    for uid in sorted(units):
        if units[uid]["level"] != "b1b" or units[uid]["synthetic"]:
            continue
        p = RUNS / "a1ri" / "rep1" / uid / "result.json"
        if not p.exists():
            continue
        after = json.loads(p.read_text(encoding="utf-8"))
        u = units[uid]

        def to_items(rows):
            return [dict(rank=r["rank"], display_phrase=r["display_phrase"], key_phrase=r["key_phrase"], used_form=r["used_form"], source_sentence=r.get("source_sentence", ""),
                         japanese_gloss=r.get("gloss") or "", gloss_alignment_status="ALIGNED") for r in rows]
        before_rows = [dict(rank=oi["rank"], display_phrase=oi["display_phrase"], key_phrase=u["production"][str(oi["rank"])]["key_phrase"], used_form=u["production"][str(oi["rank"])]["used_form"],
                            source_sentence=u["production"][str(oi["rank"])]["source_sentence"], gloss=u["production"][str(oi["rank"])]["gloss"]) for oi in u["original_items"]]
        b_items, a_items = to_items(before_rows), to_items(after["items"])
        changed = [(b["key_phrase"], x["key_phrase"], b["japanese_gloss"], x["japanese_gloss"]) for b, x in zip(b_items, a_items) if (b["japanese_gloss"], b["key_phrase"]) != (x["japanese_gloss"], x["key_phrase"])]
        rec = dict(unit=uid, family=u["family"], n_changed_items=len(changed), changed=changed)
        if u["family"] == "X":
            sig = lambda its: [[kx.explanation_phrase(it), it.get("key_phrase"), it.get("japanese_gloss", "")] for it in its]   # noqa: E731  (Productionと同一式。cached bundleのsignature用)
            bundle = {"phrases_signature": [kx.explanation_phrase(it) for it in b_items], "gloss_signature": sig(b_items), "items": {}}
            called["n"] = 0
            same = resolve(b_items, {"key_phrase_explanations_text": bundle})
            n_same = called["n"]
            diff = resolve(a_items, {"key_phrase_explanations_text": bundle})
            rec.update(same_input_reused=bool(same.get("reused_from_previous_run")), generate_calls_same=n_same,
                       changed_input_reused=bool(diff.get("reused_from_previous_run")), generate_calls_changed=called["n"] - n_same)
        else:
            rec.update(same_sig_equal=_z_sig(b_items, kx) == _z_sig(b_items, kx), changed_sig_equal=_z_sig(b_items, kx) == _z_sig(a_items, kx))
        res.append(rec)
        print(json.dumps(rec, ensure_ascii=False))
    (OUT / "e2e_signature_check.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--cap", type=float, default=X.CAP_JPY)
    a = ap.parse_args()
    {"run": cmd_run, "signature": cmd_signature}[a.cmd](a)

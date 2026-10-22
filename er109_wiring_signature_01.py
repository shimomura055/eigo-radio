# ============================================================
# er109_wiring_signature_01.py  (API 0 / 費用0)
# ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01 委任_04: er109 v1 配線の『前後不変』を行署名で固定する再利用ツール。
#   rows(canonical, ASR転写, [Azure転写], seg, kp) を、配線済み共有経路(adapter / guard_entry / rejudge_with_current_judge / make_voter)へ
#   API 0(Primary転写=保存、Secondary=mock[保存Azure転写 or 同転写]、Whisper=注入、HR/telemetry/lookupはspy)で通し、行ごとの署名を書く。
#   --scope none  = X/Z run scopeなし(Family A/B/C・単体呼出相当)。配線前HEADと完全一致(差分0)が受入条件。
#   --scope X|Z   = er109 run scope内(PNAP scopeも同時に設定=Production同様)。PASS->NG 0、NG->PASS=期待どおり。
#   配線前commitのbaselineと配線後を同じrows・同じこのscriptで比較する(このscriptは配線前HEADでも動く: scope moduleは --scope X|Z のときだけimport)。
# 使い方:
#   python er109_wiring_signature_01.py --build-rows --out rows.jsonl [--pairs-only]   # 保存データ(cwd=repo root)から rows を作る
#   python er109_wiring_signature_01.py --rows rows.jsonl --scope none --out sig_none.jsonl [--routes adapter,adapter_kp,guard,rejudge,voter]
#   python er109_wiring_signature_01.py --compare a.jsonl b.jsonl
# ============================================================
import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import wave

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
if os.environ.get("ER109_OVERLAY"):   # 配線前commitのProduction .pyを先頭に置いて比較したい場合(任意)
    sys.path.insert(0, os.environ["ER109_OVERLAY"])

PAIRS_REL = os.path.join("docs", "research", "PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01", "pairs_02.jsonl")
_JA = re.compile(r"[぀-ヿ㐀-䶿一-鿿]")
ALL_ROUTES = ("adapter", "adapter_kp", "guard", "rejudge", "voter")


def build_rows(out_path, pairs_only=False):
    sys.path.insert(0, os.getcwd())
    rows = []
    for i, l in enumerate(open(os.path.join(os.getcwd(), PAIRS_REL), encoding="utf-8")):
        if l.strip():
            p = json.loads(l)
            rows.append({"id": f"pair{i}", "canonical": p["canonical"], "asr": p["asr"], "azure": None, "seg": None, "kp": False})
    if not pairs_only:
        import glob
        import er109_stored_census_01 as census
        files = sorted(f for f in glob.glob("**/*tts_generation_results*.json", recursive=True)
                       if not f.startswith((".venv", "mfa_tool")))
        n = 0
        for f in files:
            for r in census.rows_from_results(f):
                rows.append({"id": f"st{n}", "canonical": r["canonical"], "asr": r["asr"], "azure": r.get("azure"),
                             "seg": r["seg"], "kp": bool(r["kp"]), "src": r["src"], "attempt": r.get("attempt")})
                n += 1
    with open(out_path, "w", encoding="utf-8") as fo:
        for r in rows:
            fo.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"rows={len(rows)} sha256={hashlib.sha256(open(out_path, 'rb').read()).hexdigest()}")


def _strip_volatile(o):
    if isinstance(o, dict):
        return {k: _strip_volatile(v) for k, v in o.items() if k not in ("rejudged_at", "timing", "ms", "checked_at", "total_ms", "secondary_ms", "created_at")}
    if isinstance(o, list):
        return [_strip_volatile(v) for v in o]
    return o


def _jsonable(o):
    return json.loads(json.dumps(o, ensure_ascii=False, sort_keys=True, default=str))


def run_signatures(rows, scope, routes, out_path, require_xz=False):
    os.chdir(ROOT)
    import contextlib
    import er006_asr_provider_routing_01 as routing
    import er006_secondary_asr_01 as sec
    import er103_proper_noun_alarm_policy_01 as pol
    import er104_kp_three_asr_vote_01 as kp3v
    import er078_reuse_value_guard_01 as rvg
    import er019_family_x_validation_inheritance_01 as vi
    wav = os.path.join(tempfile.gettempdir(), "er109_sig_silence.wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(1); w.setsampwidth(1); w.setframerate(8000); w.writeframes(b"\x00" * 8000)
    hr, lookups, tel = [], [], []
    sec._resolve_unresolved_entity_for_review = lambda span: lookups.append(span) or {"pronunciation_hint": "", "confidence": "unconfirmed", "sources": []}
    sec._log_human_review = lambda d: hr.append(d)
    sec.semantic_equivalence.append_telemetry_log = lambda *x, **k: tel.append(1)
    routing.transcribe = lambda *x, **k: (_ for _ in ()).throw(RuntimeError("Primary#2 forbidden"))
    xz = None
    if scope in ("X", "Z"):
        try:
            import er109_xz_scope_01 as xz   # 配線後のみ存在
        except ImportError:
            if require_xz:
                raise
            xz = None   # 配線前baseline: PNAP scopeのみ設定(er109 scope無し)

    @contextlib.contextmanager
    def scope_ctx():
        pol._RUN_SCOPE = None
        if scope in ("X", "Z"):
            with pol.run_scope(scope):          # PNAP scopeは配線前baselineでもProduction同様に設定する
                if xz is None:
                    yield
                elif scope == "X":
                    with xz.run_scope("X"):
                        yield
                else:
                    with xz.run_scope("Z"):
                        yield
        else:
            yield

    def adapter_sig(canon, asr, azure, seg, kp):
        ja = bool(_JA.search(canon))
        az_text = azure if azure else asr
        sec.get_full_text_via_azure_stt_with_phrase_list = lambda w, language="en-US", phrases=None, **kw: (az_text, None)
        sec.reset_secondary_cache()
        kw = {}
        actx = {"slot": 1, "is_last_slot": True}
        if kp:
            actx["vote_required"] = True
            actx["vote_whisper_fn"] = lambda: kp3v.make_voter("whisper", canon, (az_text if azure else asr), lang="en")
        d = sec.evaluate_attempt_with_cascade_detail(canon, asr, [], wav, language=("ja-JP" if ja else "en-US"), cascade_enabled=True,
                                                    segment_id=seg, attempt_ctx=actx)
        c = d["classification"]
        aj = d.get("asr_judgement") or {}
        return {"verified": bool(d["verified"]), "stop": bool(d["stop_retrying"]), "cls": c.classification, "hr": bool(d.get("human_review_required")),
                "state": aj.get("state"), "reason": aj.get("reason_code"), "tech": bool(d.get("technical_stop")),
                "warnings": aj.get("warnings"), "steps": [(s.get("step"), s.get("text"), s.get("classification")) for s in d.get("steps", [])],
                "final_status": d.get("final_status"), "keys": sorted(aj.keys()),
                "aj": _strip_volatile(aj)}

    def guard_sig(canon, asr, azure):
        entry = {"text": canon, "asr_text": asr}
        if azure:
            entry["scg_info"] = {"secondary_transcript": azure}
        g = rvg.guard_entry(entry, label="sig", canonical_text=canon)
        return _strip_volatile(g)

    def rejudge_sig(canon, asr, azure):
        entry = {"text": canon, "asr_text": asr, "sha256": "sig"}
        if azure:
            entry["scg_info"] = {"secondary_transcript": azure}
        lang = "ja" if _JA.search(canon) else "en"
        r = vi.rejudge_with_current_judge(entry, "a2" if lang == "ja" else "b1b", "full_story_part1", force_lang=lang)
        r.pop("tts_input", None)
        return _strip_volatile(r)

    def voter_sig(canon, asr, azure):
        out = {}
        for prov, t in (("openai", asr), ("azure", azure), ("whisper", asr)):
            if t is None:
                continue
            out[prov] = _strip_volatile(kp3v.make_voter(prov, canon, t, lang="en").audit())
        return out

    n = 0
    with open(out_path, "w", encoding="utf-8") as fo:
        for r in rows:
            canon, asr, azure, seg, kp = r["canonical"], r["asr"], r.get("azure"), r.get("seg"), bool(r.get("kp"))
            ja = bool(_JA.search(canon))
            if asr is None:
                continue
            for route in routes:
                if route in ("adapter_kp", "voter") and ja:
                    continue
                try:
                    with scope_ctx():
                        if route == "adapter":
                            sig = adapter_sig(canon, asr, azure, seg if not kp else None, False)
                        elif route == "adapter_kp":
                            sig = adapter_sig(canon, asr, azure, None, True)
                        elif route == "guard":
                            sig = guard_sig(canon, asr, azure)
                        elif route == "rejudge":
                            sig = rejudge_sig(canon, asr, azure)
                        elif route == "voter":
                            sig = voter_sig(canon, asr, azure)
                        else:
                            raise ValueError(route)
                except Exception as exc:  # noqa: BLE001
                    sig = {"error": f"{type(exc).__name__}: {exc}"}
                fo.write(json.dumps({"k": f"{r['id']}|{route}|scope={scope}", "sig": _jsonable(sig)}, ensure_ascii=False, sort_keys=True) + "\n")
                n += 1
    sys.stdout.write(f"rows={n} hr_spy={len(hr)} lookups={len(lookups)} out_sha256={hashlib.sha256(open(out_path, 'rb').read()).hexdigest()}\n")


def _pass_of(sig):
    if "verified" in sig:
        return sig.get("verified")
    if "ok" in sig:
        return sig.get("ok")
    if "blocked" in sig:
        return not sig.get("blocked")
    return None


def compare(a_path, b_path):
    def load(p):
        d = {}
        for l in open(p, encoding="utf-8"):
            if l.strip():
                o = json.loads(l)
                d[o["k"].rsplit("|scope=", 1)[0]] = _strip_volatile(o["sig"])
        return d
    A, B = load(a_path), load(b_path)
    keys = sorted(set(A) | set(B))
    same = sum(1 for k in keys if A.get(k) == B.get(k))
    ng2pass, pass2ng, other = [], [], []
    for k in keys:
        if A.get(k) == B.get(k):
            continue
        a, b = A.get(k) or {}, B.get(k) or {}
        av, bv = _pass_of(a), _pass_of(b)
        if av is False and bv is True:
            ng2pass.append(k)
        elif av is True and bv is False:
            pass2ng.append(k)
        else:
            other.append(k)
    print(json.dumps({"keys": len(keys), "identical": same, "different": len(keys) - same, "NG_to_PASS": len(ng2pass),
                      "PASS_to_NG": len(pass2ng), "other_diff": len(other)}, ensure_ascii=False))
    return {"identical": same, "NG_to_PASS": ng2pass, "PASS_to_NG": pass2ng, "other": other, "keys": len(keys)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build-rows", action="store_true")
    ap.add_argument("--pairs-only", action="store_true")
    ap.add_argument("--rows")
    ap.add_argument("--scope", default="none", choices=("none", "X", "Z"))
    ap.add_argument("--routes", default=",".join(ALL_ROUTES))
    ap.add_argument("--out")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--require-xz", action="store_true", help="配線後: scope module が無ければ失敗(silent skip禁止)")
    ap.add_argument("--compare", nargs=2)
    a = ap.parse_args()
    if a.compare:
        compare(*a.compare)
        return
    if a.build_rows:
        build_rows(a.out, a.pairs_only)
        return
    rows = [json.loads(l) for l in open(a.rows, encoding="utf-8") if l.strip()]
    if a.limit:
        rows = rows[:a.limit]
    run_signatures(rows, a.scope, a.routes.split(","), a.out, a.require_xz)


if __name__ == "__main__":
    main()

"""委任_08(B4) 旧Gate/新分類核の差分監査(読取専用・API 0)。

保存済みX/Y/Z run(er019_output/er121_output/er026_output配下のtts_generation_results.json全件)について、
  旧Gate: X=er019.m3_assembly_gate / Y=er121.y_style_gate(scratch複製上) / Z=er063._z_row_for_clip(Z Style実測照合の行判定)
  新   : er130.classify_adopted_take(er129.build_lr_ledgerのclip)
をsegment単位で並べて集計する。run dirは一切書き換えない(Yのy_style_gateだけscratch複製へ書かせる)。

新verdictの定義(W3 §1-§2の分割置換): 旧違反コードのうち「置換対象」(LR/Fallback/採用Style由来)はイベントclip(LR or Fallback証跡あり)に限り
分類核の判定へ置換し、その他の旧違反(記録欠落・status NG・Store key等=維持項目)は新でも残す。人間承認(個別承認X15)は新旧とも同じに効く。

使い方: .venv\\Scripts\\python.exe <this> <out_json> [--scope X,Y,Z]
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import sys
import tempfile
import types

sys.path.insert(0, os.getcwd())
import er019_family_x_style_profile_01 as xsp          # noqa: E402
import er063_family_z_audio_01 as z                    # noqa: E402
import er129_lr_display_reflection_01 as m129          # noqa: E402
import er130_adopted_take_classifier_01 as c130        # noqa: E402

X_REPLACED = {"LOCAL_REWRITE_RECOVERY", "ADV_MINIMAL_FALLBACK", "STD_FALLBACK_USED_OR_UNKNOWN", "JA_FALLBACK_USED_OR_UNKNOWN",
              "KP_JA_MEANING_FALLBACK_USED_OR_UNKNOWN", "PREVIEW_MINIMAL_FALLBACK", "ADV_STYLE_PREFIX_NOT_PROFILE_PREFIXED",
              "PREVIEW_STYLE_PREFIX_NOT_E1_PREFIXED", "FINAL_STYLE_SHA_MISMATCH_NO_HINT", "FINAL_STYLE_HEAD200_MISMATCH_WITH_HINT",
              "FINAL_STYLE_RECORD_MISSING", "JA_STYLE_ACTUAL_MISMATCH", "JA_STYLE_ACTUAL_UNMEASURED"}
Z_REPLACED = {"Z_STYLE_ACTUAL_MISMATCH", "Z_STYLE_FALLBACK_ADOPTED"}
GATE_NAME_KP = {"english": "en"}   # gate名kpN_english <-> ledger id kpN_en


def level_of(path: str) -> str:
    parts = path.replace("\\", "/").split("/")
    i = len(parts) - 1 - parts[::-1].index("audit") - 1 if "audit" in parts else None
    cand = parts[i] if i is not None and i >= 0 else ""
    if cand in ("a2", "b1b"):
        return cand
    low = path.lower()
    return "b1b" if ("b1b" in low or "adv" in low) else "a2"


def theme_dir_of(path: str) -> str:
    p = os.path.dirname(os.path.dirname(os.path.abspath(path)))   # <level_dir>
    return os.path.dirname(p)


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def gate_to_ledger_id(name: str) -> str:
    import re
    mm = re.fullmatch(r"kp(\d+)_english", name)
    return f"kp{mm.group(1)}_en" if mm else name


def x_old(profile_id, level, results, approvals):
    g = xsp.m3_assembly_gate(profile_id, level, results, approvals)
    out = {}
    for b in g["blocked"]:
        out[gate_to_ledger_id(b["segment"])] = {"viol": b["violations"], "human": False}
    for b in g["human_approved"]:
        out[gate_to_ledger_id(b["segment"])] = {"viol": b["violations"], "human": True}
    for n in g["checked"]:
        out.setdefault(gate_to_ledger_id(n), {"viol": [], "human": False})
    return out, g


def y_old(path, level, theme_dir):
    import er121_family_y_audio_01 as y
    res_p = os.path.abspath(path)
    level_dir = os.path.dirname(os.path.dirname(res_p))
    tmp = tempfile.mkdtemp(prefix="b4_ygate_")
    try:
        t_theme = os.path.join(tmp, "theme")
        t_level = os.path.join(t_theme, level)
        os.makedirs(os.path.join(t_level, "audit"))
        os.makedirs(os.path.join(t_theme, "audit"))
        shutil.copy(res_p, os.path.join(t_level, "audit", "tts_generation_results.json"))
        for extra in ("human_approved_segments.json",):
            sp = os.path.join(level_dir, "audit", extra)
            if os.path.exists(sp):
                shutil.copy(sp, os.path.join(t_level, "audit", extra))
        for extra in ("parts.json",):
            sp = os.path.join(level_dir, extra)
            if os.path.exists(sp):
                shutil.copy(sp, os.path.join(t_level, extra))
        rec = xsp.build_record(y.Y_APPROVED_STYLE_PROFILE)       # profile-level判定(Y1)は新旧同一のため、segment比較用に承認profile記録を置く
        with open(os.path.join(t_theme, "audit", "style_profile.json"), "w", encoding="utf-8") as f:
            json.dump(rec, f)
        try:
            res = y.y_style_gate(t_theme, level, y.Y_APPROVED_STYLE_PROFILE)
        except Exception as e:   # noqa: BLE001
            return None, {"error": f"{type(e).__name__}: {str(e)[:200]}"}
        approvals_p = os.path.join(t_level, "audit", "human_approved_segments.json")
        approvals = load(approvals_p) if os.path.exists(approvals_p) else {}
        segs = load(res_p).get("segments") or {}
        out = {}
        for e in res.get("y_body_checks") or []:
            sid = e["segment"]
            ent = segs.get(sid) or y._kp_entry(load(res_p), sid)
            hum = bool(e["violations"]) and ent is not None and xsp._approved(approvals, sid, ent)
            out[gate_to_ledger_id(sid)] = {"viol": list(e["violations"]), "human": hum}
        for b in (res.get("x_gate_blocked_after_filter") or []):
            cur = out.setdefault(gate_to_ledger_id(b["segment"]), {"viol": [], "human": False})
            cur["viol"] = list(dict.fromkeys(cur["viol"] + b["violations"]))
        xg = res.get("x_gate") or {}
        for h in xg.get("human_approved") or []:
            pass
        for n in xg.get("checked") or []:
            out.setdefault(gate_to_ledger_id(n), {"viol": [], "human": False})
        # x gate human_approved(承認で通ったX違反)は違反+human=Trueとして復元
        try:
            g = xsp.m3_assembly_gate(y.Y_APPROVED_STYLE_PROFILE, level, load(res_p), approvals)
            for b in g["human_approved"]:
                out[gate_to_ledger_id(b["segment"])] = {"viol": b["violations"], "human": True}
        except Exception:
            pass
        return out, res
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _z_all_entries(results):
    for sid, e in (results.get("segments") or {}).items():
        if isinstance(e, dict):
            yield sid, e
    for n, comp in (results.get("key_phrases") or {}).items():
        if isinstance(comp, dict):
            for role, e in comp.items():
                if isinstance(e, dict) and (e.get("path") or e.get("sha256")):
                    sub = {"english": "en", "japanese_meaning": "ja", "explanation": "explanation_en"}.get(role, role)
                    yield f"kp{n}_{sub}", e


def z_old(level, level_dir, results):
    approvals_p = os.path.join(level_dir, "audit", "human_approved_segments.json")
    approvals = load(approvals_p) if os.path.exists(approvals_p) else {}
    strict = os.path.exists(os.path.join(level_dir, z.STYLE_ACTUAL_MARKER_RELPATH))
    import er003_b1_p9a_audio as p9a
    dsha = z.style_prefix_sha256(p9a.ENGLISH_STYLE_PREFIX)
    out = {}
    for sid, e in _z_all_entries(results):
        rk = e.get("role_style_key")
        if not rk or rk not in z.FAMILY_Z_ROLE_STYLE:
            continue
        spec = types.SimpleNamespace(role_key=rk, level=level, clip_id=sid, kind=e.get("clip_kind") or "", rank=None)
        try:
            row = z._z_row_for_clip(spec, e, strict, approvals, dsha)
        except Exception as ex:   # noqa: BLE001
            out[sid] = {"viol": [f"OLD_GATE_EXCEPTION:{type(ex).__name__}"], "human": False}
            continue
        viol = list(row["violations"])
        # Z1(維持): assert_tts_results_completeの採択条件(status OK かつ z_adoption採択、または人間承認)。旧Gateの別段で必ずBLOCKされる
        ok = e.get("status") == "OK" or (sid in approvals)
        if not ok:
            viol.append(f"Z_TTS_RESULT_NOT_ADOPTED(status={e.get('status')})")
        out[sid] = {"viol": viol, "human": bool(row["human_approved"]) or (sid in approvals), "check": row.get("check")}
    return out


def entry_for(results, sid):
    seg = (results.get("segments") or {}).get(sid)
    if seg is not None:
        return seg
    import re
    mm = re.fullmatch(r"kp(\d+)_(.+)", sid)
    if mm:
        comp = (results.get("key_phrases") or {}).get(mm.group(1)) or {}
        key = "english" if mm.group(2) == "en" else mm.group(2)
        return comp.get(key)
    return None


def main():
    out_json = sys.argv[1]
    scope = {"X": "er019_output", "Y": "er121_output", "Z": "er026_output"}
    if "--scope" in sys.argv:
        want = sys.argv[sys.argv.index("--scope") + 1].split(",")
        scope = {k: v for k, v in scope.items() if k in want}
    allow = c130.build_allowlist()
    rows, runs = [], []
    errors = []
    for fam, root in scope.items():
        for path in sorted(glob.glob(os.path.join(root, "**", "tts_generation_results.json"), recursive=True)):
            rel = path.replace("\\", "/")
            level = level_of(rel)
            level_dir = os.path.dirname(os.path.dirname(os.path.abspath(path)))
            theme = theme_dir_of(path)
            try:
                results = load(path)
            except Exception as e:   # noqa: BLE001
                errors.append({"path": rel, "error": f"load {type(e).__name__}"})
                continue
            run_info = {"family": fam, "path": rel, "level": level}
            try:
                led = m129.build_lr_ledger("", "", results_path=path)
            except Exception as e:   # noqa: BLE001
                errors.append({"path": rel, "error": f"ledger {type(e).__name__}: {str(e)[:120]}"})
                continue
            clips = {c["clip_id"]: c for c in led["clips"]}
            # 旧Gate
            old, old_meta = {}, {}
            try:
                if fam == "X" or fam == "Y":
                    if fam == "X":
                        try:
                            rec = xsp.read_record(theme)
                            pid = xsp.verify_record(rec) if rec else xsp.PROFILE_DEFAULT
                            run_info["profile_source"] = "record" if rec else "no_record->default"
                        except Exception as e:   # noqa: BLE001
                            pid = xsp.PROFILE_DEFAULT
                            run_info["profile_source"] = f"record_unreadable({type(e).__name__})->default"
                        ap = os.path.join(level_dir, "audit", "human_approved_segments.json")
                        approvals = load(ap) if os.path.exists(ap) else {}
                        old, old_meta = x_old(pid, level, results, approvals)
                        run_info["profile"] = pid
                    else:
                        old, old_meta = y_old(path, level, theme)
                        old = old or {}
                        run_info["profile"] = "fx_20261017(scratch)"
                else:
                    old = z_old(level, level_dir, results)
            except Exception as e:   # noqa: BLE001
                errors.append({"path": rel, "error": f"oldgate {type(e).__name__}: {str(e)[:160]}"})
                continue
            ids = set(old) | set(clips)
            runs.append({**run_info, "old_checked": len(old), "event_clips": len(clips)})
            for sid in sorted(ids):
                in_old = sid in old
                ev = clips.get(sid)
                row = {"family": fam, "path": rel, "level": level, "segment": sid, "in_old_scope": in_old, "event": ev is not None,
                       "run_profile": run_info.get("profile"),
                       "z_strict_marker": (os.path.exists(os.path.join(level_dir, z.STYLE_ACTUAL_MARKER_RELPATH)) if fam == "Z" else None)}
                o = old.get(sid)
                if o is not None:
                    row["old_violations"] = o["viol"]
                    row["old_human_approved"] = o["human"]
                    row["old_verdict"] = "BLOCK" if (o["viol"] and not o["human"]) else "PASS"
                if ev is None:
                    row["new_verdict"] = row.get("old_verdict")
                    row["change"] = "UNCHANGED(no event: maintained checks only)" if in_old else "OUT_OF_SCOPE(no event)"
                    rows.append(row)
                    continue
                entry = entry_for(results, sid) or {}
                pol = c130.policy_for_clip(sid, entry, level)
                take = ev.get("adopted_take") if isinstance(ev.get("adopted_take"), dict) else None
                ctx = c130.ctx_from_entry(entry, take=take)
                cls = c130.classify_adopted_take(ev, pol, allow, ctx)
                row.update({"policy": pol, "new_class": cls["verdict"], "new_reasons": cls["reasons"],
                            "new_warning_kinds": [w["kind"] for w in cls["warnings"]], "notes": cls["notes"][:3],
                            "take_kind": (take or {}).get("kind"), "take_how": (take or {}).get("how"),
                            "lr": bool(ev.get("lr")), "parity": (ev.get("text_parity") or {}).get("verdict"), "ledger_verdict": ev.get("verdict")})
                if not in_old:
                    row["new_verdict"] = "BLOCK" if cls["verdict"] == "BLOCK" else "PASS"
                    row["change"] = "OUT_OF_OLD_GATE_SCOPE(info; new core not invoked for this role)"
                    rows.append(row)
                    continue
                replaced = Z_REPLACED if fam == "Z" else X_REPLACED
                residual = [v for v in o["viol"] if v not in replaced]
                new_viol = residual + (cls["reasons"] if cls["verdict"] == "BLOCK" else [])
                row["residual_old_violations"] = residual
                row["new_verdict"] = "BLOCK" if (new_viol and not o["human"]) else "PASS"
                ov, nv = row["old_verdict"], row["new_verdict"]
                if ov == "BLOCK" and nv == "PASS":
                    row["change"] = "RELEASED(old BLOCK -> new PASS)"
                elif ov == "PASS" and nv == "BLOCK":
                    row["change"] = "TIGHTENED(old PASS -> new BLOCK)"
                else:
                    row["change"] = "UNCHANGED(event)"
                rows.append(row)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({"runs": runs, "errors": errors, "rows": rows}, f, ensure_ascii=False, indent=1)
    print("runs", len(runs), "errors", len(errors), "rows", len(rows))


if __name__ == "__main__":
    main()

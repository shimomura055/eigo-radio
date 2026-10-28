"""委任_11(B-wire) 配線後の実Gate呼出による旧/新判定の差分監査(読取専用・API 0)。

B4の差分監査(audit_gate_diff_01.py)は「旧Gate+分類核を監査側で合成」して求めた。本scriptは**配線後の実Gate**(X `m3_assembly_gate(level_dir=)` / Y `y_style_gate` /
Z `_z_row_for_clip(ledger_clips=)`)を、同じコードパスのまま
  旧 = `er130.event_ledger_clips`を「台帳なし」(None)にした呼出(=UD-3前の判定。LR/Fallback由来の違反を置換しない)
  新 = 配線どおりの呼出
の2通りで保存run(X/Y/Z全件のtts_generation_results.json)に対し呼び、segment単位で旧BLOCK→新PASS(解除)・旧PASS→新BLOCK(厳格化)を集計する。
run dirは書き換えない(Yのy_style_gateだけscratch複製のaudit/へ書かせる。Zは行判定関数を直接呼ぶ)。

使い方: .venv\\Scripts\\python.exe <this> <out_json> [--scope X,Y,Z]
"""
from __future__ import annotations

import glob
import json
import os
import re
import shutil
import sys
import tempfile
import types
from unittest import mock

sys.path.insert(0, os.getcwd())
import er019_family_x_style_profile_01 as xsp          # noqa: E402
import er063_family_z_audio_01 as z                    # noqa: E402
import er130_adopted_take_classifier_01 as c130        # noqa: E402

OLD = mock.patch("er130_adopted_take_classifier_01.event_ledger_clips", return_value=None)   # 台帳なし=UD-3前の判定


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def level_of(path: str) -> str:
    parts = path.replace("\\", "/").split("/")
    i = len(parts) - 1 - parts[::-1].index("audit") - 1 if "audit" in parts else None
    cand = parts[i] if i is not None and i >= 0 else ""
    if cand in ("a2", "b1b"):
        return cand
    low = path.lower()
    return "b1b" if ("b1b" in low or "adv" in low) else "a2"


def to_lid(name: str) -> str:
    mm = re.fullmatch(r"kp(\d+)_english", name)
    return f"kp{mm.group(1)}_en" if mm else name


def x_gate(pid, level, results, approvals, level_dir, new):
    if new:
        g = xsp.m3_assembly_gate(pid, level, results, approvals, level_dir=level_dir)
    else:
        with OLD:
            g = xsp.m3_assembly_gate(pid, level, results, approvals, level_dir=level_dir)
    out = {}
    for b in g["blocked"]:
        out[to_lid(b["segment"])] = {"viol": b["violations"], "human": False}
    for b in g["human_approved"]:
        out[to_lid(b["segment"])] = {"viol": b["violations"], "human": True}
    for n in g["checked"]:
        out.setdefault(to_lid(n), {"viol": [], "human": False})
    warns = {to_lid(w["segment"]): w["warning"] for w in g.get("warnings") or [] if w.get("warning") in ("LR_APPLIED", "FALLBACK_APPLIED")}
    return out, warns


def y_gate(path, level, new):
    import er121_family_y_audio_01 as y
    res_p = os.path.abspath(path)
    level_dir = os.path.dirname(os.path.dirname(res_p))
    tmp = tempfile.mkdtemp(prefix="bw_ygate_")
    try:
        t_theme = os.path.join(tmp, "theme")
        t_level = os.path.join(t_theme, level)
        os.makedirs(os.path.join(t_theme, "audit"))
        shutil.copytree(os.path.join(level_dir, "audit"), os.path.join(t_level, "audit"), ignore=shutil.ignore_patterns("tts_block_progress"))
        for extra in ("parts.json",):
            sp = os.path.join(level_dir, extra)
            if os.path.exists(sp):
                shutil.copy(sp, os.path.join(t_level, extra))
        rec = xsp.build_record(y.Y_APPROVED_STYLE_PROFILE)
        with open(os.path.join(t_theme, "audit", "style_profile.json"), "w", encoding="utf-8") as f:
            json.dump(rec, f)
        try:
            if new:
                res = y.y_style_gate(t_theme, level, y.Y_APPROVED_STYLE_PROFILE)
            else:
                with OLD:
                    res = y.y_style_gate(t_theme, level, y.Y_APPROVED_STYLE_PROFILE)
        except Exception as e:   # noqa: BLE001
            return None, {}, {"error": f"{type(e).__name__}: {str(e)[:200]}"}
        approvals_p = os.path.join(t_level, "audit", "human_approved_segments.json")
        approvals = load(approvals_p) if os.path.exists(approvals_p) else {}
        results = load(res_p)
        segs = results.get("segments") or {}
        out = {}
        for e in res.get("y_body_checks") or []:
            sid = e["segment"]
            ent = segs.get(sid) or y._kp_entry(results, sid)
            hum = bool(e["violations"]) and ent is not None and xsp._approved(approvals, sid, ent)
            out[to_lid(sid)] = {"viol": list(e["violations"]), "human": hum}
        for b in (res.get("x_gate_blocked_after_filter") or []):
            cur = out.setdefault(to_lid(b["segment"]), {"viol": [], "human": False})
            cur["viol"] = list(dict.fromkeys(cur["viol"] + b["violations"]))
        xg = res.get("x_gate") or {}
        for n in xg.get("checked") or []:
            out.setdefault(to_lid(n), {"viol": [], "human": False})
        for h in xg.get("human_approved") or []:
            out[to_lid(h["segment"])] = {"viol": h["violations"], "human": True}
        warns = {to_lid(w["segment"]): w["warning"] for w in (res.get("lr_fallback_warnings") or []) if w.get("warning") in ("LR_APPLIED", "FALLBACK_APPLIED")}
        return out, warns, res
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _z_entries(results):
    for sid, e in (results.get("segments") or {}).items():
        if isinstance(e, dict):
            yield sid, e
    for n, comp in (results.get("key_phrases") or {}).items():
        if isinstance(comp, dict):
            for role, e in comp.items():
                if isinstance(e, dict) and (e.get("path") or e.get("sha256")):
                    sub = {"english": "en", "japanese_meaning": "ja", "explanation": "explanation_en"}.get(role, role)
                    yield f"kp{n}_{sub}", e


def z_rows(level, level_dir, results, new):
    approvals_p = os.path.join(level_dir, "audit", "human_approved_segments.json")
    approvals = load(approvals_p) if os.path.exists(approvals_p) else {}
    strict = os.path.exists(os.path.join(level_dir, z.STYLE_ACTUAL_MARKER_RELPATH))
    import er003_b1_p9a_audio as p9a
    dsha = z.style_prefix_sha256(p9a.ENGLISH_STYLE_PREFIX)
    clips = c130.event_ledger_clips(level_dir) if new else None
    out, warns = {}, {}
    for sid, e in _z_entries(results):
        rk = e.get("role_style_key")
        if not rk or rk not in z.FAMILY_Z_ROLE_STYLE:
            continue
        spec = types.SimpleNamespace(role_key=rk, level=level, clip_id=sid, kind=e.get("clip_kind") or "", rank=None)
        try:
            row = z._z_row_for_clip(spec, e, strict, approvals, dsha, clips)
        except Exception as ex:   # noqa: BLE001
            out[sid] = {"viol": [f"GATE_EXCEPTION:{type(ex).__name__}"], "human": False}
            continue
        viol = list(row["violations"])
        ok = e.get("status") == "OK" or (sid in approvals)
        if not ok:
            viol.append(f"Z_TTS_RESULT_NOT_ADOPTED(status={e.get('status')})")
        out[sid] = {"viol": viol, "human": bool(row["human_approved"]) or (sid in approvals)}
        for w in row.get("lr_fallback_warnings") or []:
            warns[sid] = w["kind"]
    return out, warns


def verdict(o):
    return None if o is None else ("BLOCK" if (o["viol"] and not o["human"]) else "PASS")


def main():
    out_json = sys.argv[1]
    scope = {"X": "er019_output", "Y": "er121_output", "Z": "er026_output"}
    if "--scope" in sys.argv:
        want = sys.argv[sys.argv.index("--scope") + 1].split(",")
        scope = {k: v for k, v in scope.items() if k in want}
    rows, runs, errors = [], [], []
    for fam, root in scope.items():
        for path in sorted(glob.glob(os.path.join(root, "**", "tts_generation_results.json"), recursive=True)):
            rel = path.replace("\\", "/")
            level = level_of(rel)
            level_dir = os.path.dirname(os.path.dirname(os.path.abspath(path)))
            theme = os.path.dirname(level_dir)
            try:
                results = load(path)
            except Exception as e:   # noqa: BLE001
                errors.append({"path": rel, "error": f"load {type(e).__name__}"})
                continue
            info = {"family": fam, "path": rel, "level": level}
            try:
                if fam == "X":
                    try:
                        rec = xsp.read_record(theme)
                        pid = xsp.verify_record(rec) if rec else xsp.PROFILE_DEFAULT
                    except Exception:   # noqa: BLE001
                        pid = xsp.PROFILE_DEFAULT
                    ap = os.path.join(level_dir, "audit", "human_approved_segments.json")
                    approvals = load(ap) if os.path.exists(ap) else {}
                    old, _ = x_gate(pid, level, results, approvals, level_dir, False)
                    new, warns = x_gate(pid, level, results, approvals, level_dir, True)
                    info["profile"] = pid
                elif fam == "Y":
                    old, _, mo = y_gate(path, level, False)
                    new, warns, mn = y_gate(path, level, True)
                    if old is None or new is None:
                        errors.append({"path": rel, "error": (mo or mn)})
                        continue
                else:
                    old, _ = z_rows(level, level_dir, results, False)
                    new, warns = z_rows(level, level_dir, results, True)
            except Exception as e:   # noqa: BLE001
                errors.append({"path": rel, "error": f"gate {type(e).__name__}: {str(e)[:160]}"})
                continue
            runs.append({**info, "old_checked": len(old), "new_checked": len(new)})
            for sid in sorted(set(old) | set(new)):
                ov, nv = verdict(old.get(sid)), verdict(new.get(sid))
                ch = "UNCHANGED"
                if ov == "BLOCK" and nv == "PASS":
                    ch = "RELEASED(old BLOCK -> new PASS)"
                elif ov == "PASS" and nv == "BLOCK":
                    ch = "TIGHTENED(old PASS -> new BLOCK)"
                rows.append({"family": fam, "path": rel, "level": level, "segment": sid, "old": ov, "new": nv, "change": ch,
                             "old_violations": (old.get(sid) or {}).get("viol"), "new_violations": (new.get(sid) or {}).get("viol"),
                             "warning": (warns or {}).get(sid)})
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({"runs": runs, "errors": errors, "rows": rows}, f, ensure_ascii=False, indent=1)
    print("runs", len(runs), "errors", len(errors), "rows", len(rows))


if __name__ == "__main__":
    main()

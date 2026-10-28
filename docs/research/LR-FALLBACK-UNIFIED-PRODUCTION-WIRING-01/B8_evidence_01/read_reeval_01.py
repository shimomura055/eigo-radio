"""委任_13(B8) 読取再評価(API 0・読取専用): 保存run×levelに対し配線後HEADの実関数(Gate/er129台帳/er131最終Human報告/汚染scan)を実行し、
Family×Level別の実証表(JSON)を作る。run dirは書き換えない(最終報告HTMLのみ <out>/reports/ へ)。
使い方: .venv/Scripts/python.exe <this> <out_dir>
"""
import glob, importlib.util, json, os, re, sys
sys.path.insert(0, os.getcwd())
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("aud", os.path.join(HERE, "..", "BWIRE_audit_01", "audit_wired_gate_01.py"))
aud = importlib.util.module_from_spec(spec); spec.loader.exec_module(aud)
import er129_lr_display_reflection_01 as e129
import er131_final_human_report_01 as e131
import er019_family_x_style_profile_01 as xsp
import er132_lr_overlay_pages_01 as e132

out_dir = sys.argv[1]
os.makedirs(out_dir, exist_ok=True)
ROOTS = {"X": "er019_output", "Y": "er121_output", "Z": "er026_output"}
SKIP = re.compile(r"superseded|aborted|smoke")
rows = []
for fam, root in ROOTS.items():
    for path in sorted(glob.glob(os.path.join(root, "**", "tts_generation_results.json"), recursive=True)):
        rel = path.replace("\\", "/")
        if SKIP.search(rel):
            continue
        level = aud.level_of(rel)
        level_dir = os.path.dirname(os.path.dirname(os.path.abspath(path)))
        run_dir = os.path.dirname(level_dir)
        row = {"family": fam, "level": level, "run": os.path.relpath(run_dir, os.getcwd()).replace("\\", "/"), "results": rel}
        try:
            results = aud.load(path)
            if fam == "X":
                try:
                    rec = xsp.read_record(run_dir); pid = xsp.verify_record(rec) if rec else xsp.PROFILE_DEFAULT
                except Exception:
                    pid = xsp.PROFILE_DEFAULT
                ap = os.path.join(level_dir, "audit", "human_approved_segments.json")
                appr = aud.load(ap) if os.path.exists(ap) else {}
                g, warns = aud.x_gate(pid, level, results, appr, level_dir, True)
            elif fam == "Y":
                g, warns, _ = aud.y_gate(path, level, True)
            else:
                g, warns = aud.z_rows(level, level_dir, results, True)
            if g is None:
                row["gate_error"] = str(_)[:200]; rows.append(row); continue
            blocked = {k: v["viol"] for k, v in g.items() if aud.verdict(v) == "BLOCK"}
            row["gate"] = {"checked": len(g), "block": blocked, "warn": warns,
                           "with_violation_but_human": [k for k, v in g.items() if v["viol"] and v["human"]]}
        except Exception as ex:
            row["gate_error"] = f"{type(ex).__name__}: {str(ex)[:200]}"
        try:
            L = e129.build_lr_ledger(run_dir, level, results_path=path, level_dir=level_dir, only_events=True)
            lr = [c["clip_id"] for c in L["clips"] if (c.get("lr") or {}).get("adopted_in_final")]
            lr_noadopt = [c["clip_id"] for c in L["clips"] if c.get("lr") and not (c["lr"] or {}).get("adopted_in_final")]
            fb = [c["clip_id"] for c in L["clips"] if (c.get("fallback") or {}).get("state") == "USED"]
            row["ledger"] = {"event_clips": len(L["clips"]), "lr_adopted": lr, "lr_not_adopted": lr_noadopt, "fb_used": fb,
                             "parity_nonpass": [c["clip_id"] for c in L["clips"] if (c.get("text_parity") or {}).get("verdict") not in ("PASS", None)],
                             "verdict": {v: sum(1 for c in L["clips"] if c.get("verdict") == v) for v in {c.get("verdict") for c in L["clips"]}}}
            ents = [e for _, e, _ in e129._iter_entries(aud.load(path))]
            row["final_adoption_recorded"] = sum(1 for e in ents if isinstance(e, dict) and e.get("final_adoption"))
        except Exception as ex:
            row["ledger_error"] = f"{type(ex).__name__}: {str(ex)[:200]}"
        try:
            L2 = e129.build_lr_ledger(run_dir, level, results_path=path, level_dir=level_dir, only_events=True)
            rd = e132.rendered_display_units(run_dir, level, ledger=L2, results_path=path, level_dir=level_dir)
            pr = e132.evaluate_text_parity(run_dir, level, rendered_display=rd, ledger=L2, results_path=path, level_dir=level_dir,
                                           not_rendered_clip_ids=e132.X_NOT_RENDERED_CLIP_IDS if fam == "X" else ())
            row["parity"] = {"status": pr["status"], "problems": [(p_["clip_id"], p_["code"]) for p_ in pr["problems"]], "checked": [c_["clip_id"] for c_ in pr["checked"]]}
        except Exception as ex:
            row["parity_error"] = f"{type(ex).__name__}: {str(ex)[:200]}"
        try:
            cn = e131.scan_run_contamination(run_dir)
            row["contamination"] = {k: v for k, v in cn.items() if k != "hits"}
            row["contamination"]["hit_count"] = len(cn["hits"])
        except Exception as ex:
            row["contamination_error"] = f"{type(ex).__name__}: {str(ex)[:200]}"
        try:
            model = e131.build_model(run_dir, level, fam, results_path=path, level_dir=level_dir)
            s = e131.summarize(model)
            html_ = e131.render_report(model, slug="b8", run_name=os.path.basename(run_dir), date="2026-10-28")
            nred = html_.count('class="fhr-lr-after"'); nblue = html_.count("fhr-fb-block")
            sub = os.path.join(out_dir, "reports", fam, os.path.basename(run_dir)); os.makedirs(sub, exist_ok=True)
            if s["lr"] or s["fb"] or s["gap_units"]:
                with open(os.path.join(sub, f"{level}.html"), "w", encoding="utf-8", newline="\n") as f:
                    f.write(html_)
            row["report"] = {"units": s["units"], "lr": s["lr"], "fb": s["fb"], "gap_units": s["gap_units"], "red_spans_html": nred, "blue_blocks_html": nblue,
                             "consistent": (nred >= s["lr"] if s["lr"] else True) and ((nblue >= s["fb"]) if s["fb"] else True),
                             "contamination_page_hits": e131.check_page_fhr_contamination(html_) and "n/a(report page itself)"}
        except Exception as ex:
            row["report_error"] = f"{type(ex).__name__}: {str(ex)[:200]}"
        rows.append(row)
with open(os.path.join(out_dir, "read_reeval_01.json"), "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, indent=1, default=str)
print("rows", len(rows))

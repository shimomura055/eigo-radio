# 委任_16: AI島 run_form_prod_01 の三者一致Gate・HR Lock・学習項目sha・候補ページ件数を読取で記録(API 0、書込みはjsonのみ)
import json, hashlib, os, re, sys, subprocess
sys.path.insert(0, "."); import er132_lr_overlay_pages_01 as e
W = "er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01"
out = {}
for lv in ("a2", "b1b"):
    g = e.assemble_gate_summary(W, lv, not_rendered_clip_ids=e.X_NOT_RENDERED_CLIP_IDS)
    rl = json.load(open(f"{W}/{lv}/audit/review_lock_state.json", encoding="utf-8"))
    st = {}
    for k, v in rl.items():
        s = v.get("state") if isinstance(v, dict) else None
        st[s] = st.get(s, 0) + 1
    cs = open(f"{W}/{lv}/audit/confirmed_selection.json", "rb").read()
    cj = json.loads(cs)
    sel = open(f"{W}/{lv}/key_phrases/confirmed_selection.json", "rb").read()
    d = subprocess.run(["git", "diff", "--stat", "HEAD", "--", f"{W}/{lv}/key_phrases/confirmed_selection.json", f"{W}/{lv}/audit/confirmed_selection.json"], capture_output=True, text=True).stdout.strip()
    sj = json.loads(sel)
    out[lv] = {"three_way_gate": g if g is None or isinstance(g, (dict, list, str)) else str(g),
               "review_lock_states": st, "review_lock_n": len(rl),
               "confirmed_selection_sha16": hashlib.sha256(sel).hexdigest()[:16],
               "kp_n": len(sj.get("key_phrases") or sj.get("kp") or []), "kw_n": len(sj.get("key_words") or sj.get("vocab") or []),
               "grammar": (sj.get("grammar") or {}).get("status") if isinstance(sj.get("grammar"), dict) else sj.get("grammar"),
               "git_diff_confirmed_selection": d or "no diff"}
html = open("user_test/family_x_ai_island_form_01_candidate_b7_01/index.html", encoding="utf-8").read()
out["page"] = {"chunk_mark": html.count("chunk-mark"), "rpt_lr_span": len(re.findall(r'class=.rpt-lr', html)), "rpt_fb": html.count("rpt-fb"),
               "sha256_16": hashlib.sha256(html.encode()).hexdigest()[:16], "AI agents sent": html.count("AI agents sent"), "AI systems sent": html.count("AI systems sent"), "AIs sent": html.count("AIs sent"),
               "old_note": html.count("Local Rewrite採用")}
json.dump(out, open("docs/research/LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01/B16_evidence/ai_island_evidence_16.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print(json.dumps(out, ensure_ascii=False, indent=1, default=str)[:4000])

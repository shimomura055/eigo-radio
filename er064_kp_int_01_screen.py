# ============================================================
# er064_kp_int_01_screen.py (Round1 A/C: 机上スクリーニング。JPY0、Trial専用)
# 1) 各M(M0-M3)のshortlistでアンカーが候補に届くか(Coffee Std/Adv) 2) M x P 20組合せの互換性・token 3) 他記事のM差(誤除外・追加)
# 出力: round1/screening_r1.json
# ============================================================
import json
import os
import sys

sys.path.insert(0, os.getcwd())
import er064_kp_int_01_eval as EV  # noqa: E402
import er064_kp_int_01_machine as MC  # noqa: E402
import er064_kp_int_01_prompts as PR  # noqa: E402
import er064_kp_opt_01_phase2_run_03 as R  # noqa: E402
import er064_kp_opt_01_upstream_core as U  # noqa: E402

OUT = MC.OUT
res = {"anchors_in_article": {}, "reach": {}, "machine": {}, "combos": {}, "other_articles": {}}
for lv in ("std", "adv"):
    key = f"coffee_{lv}"
    res["anchors_in_article"][lv] = EV.in_article(U.read_article(key))
    res["reach"][lv] = {}
    for pat in MC.PATTERNS:
        b = MC.build_pattern(key, pat)
        rc = EV.reach_in_shortlist(b["shortlist"])
        res["reach"][lv][pat] = {str(k): v for k, v in rc.items() if k in res["anchors_in_article"][lv] or v}
        d = MC.describe(key, pat)
        res["machine"][f"{key}_{pat}"] = {k: d[k] for k in ("n_candidates", "rows_tokens", "added_vs_M0", "removed_vs_M0", "reserved", "tier_h_dropped", "match_kind_counts", "build_secs")}
# M x P matrix
for lv in ("std", "adv"):
    key = f"coffee_{lv}"
    for pat in MC.PATTERNS:
        rows = MC.build_pattern(key, pat)["rows_text"]
        cand = R.cand_block(rows)
        for pid in ("P0", "P1", "P2", "P3", "P4"):
            msg = PR.render(pid, lv, cand)
            compat = True
            note = ""
            if pat == "M3" and pid == "P0":
                compat, note = False, "P0(現行逐語)は`match:`注釈を説明しない=未説明ラベルを渡す条件になるため除外"
            if pat in ("M1", "M2", "M3") and pid == "P0":
                note = (note + " ").strip() + " 注釈(contains:/contained_in:)はP0が説明しない(前回C1と同条件)" if compat else note
            res["combos"][f"{pat}{pid}_{lv}"] = {"compatible": compat, "note": note, "input_tokens_approx": PR.tokens(msg), "msg_sha256": PR.sha(msg)}
for key in MC.ARTICLE_KEYS:
    if key.startswith("coffee"):
        continue
    ent = {}
    for pat in MC.PATTERNS:
        d = MC.describe(key, pat)
        ent[pat] = {k: d[k] for k in ("n_candidates", "rows_tokens", "added_vs_M0", "removed_vs_M0", "reserved", "tier_h_dropped")}
    res["other_articles"][key] = ent
json.dump(res, open(f"{OUT}/screening_r1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for lv in ("std", "adv"):
    print(lv, "anchors in article:", res["anchors_in_article"][lv])
    for pat in MC.PATTERNS:
        print(" ", pat, res["reach"][lv][pat])
for k in sorted(res["combos"]):
    if k.endswith("_std"):
        print(k, res["combos"][k]["compatible"], res["combos"][k]["input_tokens_approx"], "| adv", res["combos"][k.replace("_std", "_adv")]["input_tokens_approx"])

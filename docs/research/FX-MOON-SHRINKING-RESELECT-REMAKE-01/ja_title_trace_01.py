# 今回3 attemptのPrimary転写を現行Production Primary判定(classify_ja_asr_match, API 0)に通し、差分spanとCandidate E(er011)の読み比較の結果を出す。
# 再現: PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/FX-MOON-SHRINKING-RESELECT-REMAKE-01/ja_title_trace_01.py
import sys; sys.path.insert(0, ".")
import er007_ja_asr_validator_01 as j
import er011_ja_asr_variant_layer_01 as VL
j.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED = False
C = "月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密"
T = {"cur_a1_P": "月野氏は8,900本超。その奥に潜む岩の上着の秘密", "cur_a2_P": "月の詩は八千九百本超。その奥に潜む岩の上着の秘密", "cur_a3_P": "スギノ市は、八千九百本超、その奥に潜む岩の上着の秘密。",
     "cur_a1_Azure": "月の詩は8900本ちょ。その奥に潜む岩の上着の秘密。", "cur_a2_Azure": "月の詩は8900本ちょうその奥に潜む岩の上着の秘密。", "cur_a3_Azure": "Sukino氏は8900本超。その奥に潜む岩の上着の秘密。"}
print("canon_norm:", j.normalize_ja(C))
for k, t in T.items():
    r = j.classify_ja_asr_match(C, t, allow_reading_resolver=False)
    print("---", k, "|", t); print("  ", r.classification, round(r.similarity_ratio, 3), r.reason[:160])
    print("   number_mismatches:", r.protected.number_mismatches, "| candidate_e_rejections:", getattr(r.protected, "candidate_e_rejections", None), "| cascade_diffs:", getattr(r.protected, "candidate_e_cascade_diffs", None))
    print("   content_diffs:", [(d["canonical"], d["asr"], d.get("cascade_eligible")) for d in r.protected.content_diffs])
    for d in r.protected.content_diffs:
        print("   E span reading variant match", (d["canonical"], d["asr"]), "=", VL._span_pair_reading_variant_match(d["canonical"], d["asr"]))
print("span-level probe (E reading engine): しわ vs 詩は =", VL._span_pair_reading_variant_match("しわ", "詩は"), "| しわ vs 詩わ(助詞の発音わに揃えた仮想形) =", VL._span_pair_reading_variant_match("しわ", "詩わ"))

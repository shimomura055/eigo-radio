# -*- coding: utf-8 -*-
# OPEN-233-KPI-RECOVERY-REDESIGN-02 委任_01 RCA(¥0): rep25 B3 s1 Stage 2 prompt全文をAPI無しで復元しsha256照合。
import json, sys, hashlib
sys.path.insert(0, ".")
import er052_open233_self_recovery_stage2_production_01 as s2p
import er052_open233_self_recovery_stage2_calibration_01 as s2c
import er052_open233_stage2_b3_misdowngrade_diag_01 as diag
OUT = "er052_output/open233_kpi_recovery_02_offline_01"
fx, claims, _ = diag.build_b3_input()
rub = s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V7B
blocks = []
for i, c in enumerate(claims):
    blocks.append(f"[claim_index={i}]\nclaim: {c['claim_text']}\nローカル文脈(段落±1): {c['local_context']}\n"
                  f"origin: {c.get('origin') or '(不明)'}\nrelated_fact_id: {c.get('related_fact_id') or '(不明)'}\n"
                  f"section_type(title/hook/in_one_line/body): {c.get('section_type') or 'body'}")
# section_type: s2 results had in_one_line; claims dict in diag lacks it -> sha check below decides
prompt = s2p.BATCH_PROMPT_TEMPLATE.format(verified_ledger_text=fx["ledger_text"], source_article_text=fx.get("source_article_text") or "(なし)",
    claims_block="\n\n".join(blocks), materiality_rubric=rub, rewrite_hint_instruction=s2p.REWRITE_HINT_INSTRUCTION)
sha = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
print("sha", sha, sha == diag.REP25_B3_STAGE2_SHA, len(prompt))
open(f"{OUT}/b3_stage2_prompt_reconstructed.txt", "w", encoding="utf-8").write(
    "[developer]\n" + s2p.STAGE2_PROD_DEVELOPER_MESSAGE + "\n\n[user]\n" + prompt)
json.dump({"sha256": sha, "match_rep25": sha == diag.REP25_B3_STAGE2_SHA, "chars": len(prompt)}, open(f"{OUT}/b3_stage2_prompt_sha.json", "w"))

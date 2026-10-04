# -*- coding: utf-8 -*-
# 委任_08: A構成(frozen生成元)のprompt sha再現確認。fixtureの include_related_fact_id フラグ(er051 trial_02_runはfixture.get(...,False)で呼ぶ)を反映する(API 0)
import json, sys, hashlib
sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import er052_open233_self_recovery_flow_runner_01 as runner
import er051_open233_checker_trial_variant_01 as trial
import er003_v1_en_direct_vfl_01_generate as vfl01
sha = lambda t: hashlib.sha256(t.encode("utf-8")).hexdigest()
def prompt(fx, rel):
    p = trial.build_trial_prompt_template("V4A").format(verified_ledger_text=fx["ledger_text"], article_text=fx["article_text"])
    if rel: p += vfl01.RELATED_FACT_ID_INSTRUCTION
    if fx.get("source_article_text") is not None: p += vfl01.ORIGIN_INSTRUCTION_TEMPLATE.format(source_article_text=fx["source_article_text"])
    return p
rows = []
for i in runner.build_target_instances():
    if i["stage1_mode"] != "reuse": continue
    src = i.get("stage1_source"); fx = i["fixture"]
    m = json.load(open(src, encoding="utf-8"))
    a = m.get("prompt_sha256")
    rows.append({"id": i["instance_id"], "src": src, "fx_rel_flag": fx.get("include_related_fact_id", False), "has_origin": fx.get("source_article_text") is not None,
      "m_rel_true": a == sha(prompt(fx, True)), "m_rel_false": a == sha(prompt(fx, False)), "m_fixture_flag": a == sha(prompt(fx, fx.get("include_related_fact_id", False)))})
print(sum(r["m_fixture_flag"] for r in rows), "/", len(rows), "match with fixture flag;", sum(r["m_rel_true"] for r in rows), "match rel=True")
for r in rows:
    if not r["m_fixture_flag"]: print("NOMATCH", r)
json.dump(rows, open("er052_output/open233_kpi_recovery_02_offline_01/agg_a_config_sha_check_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

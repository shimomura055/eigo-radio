# INPUT_CHECK_01(FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_01、2026-10-24、API 0)

| 項目 | 確認結果 |
|---|---|
| 完成本文 | `er026_output/family_z_production_e2e_01/the_gift_of_the_magi/run_sf_prod_01/writer/r2.md`(Advanced最終稿=Writer r2。`writer/provenance.json` chain r0→r1→r2、actual_model_id=gpt-6.1-sol)。語数434(`wc -w`、見出し含む)、本文30段落(見出し除く)。ユーザー承認済みPASS(UDR #177、委任文の記載)。Std稿は`writer/std.md`(今回対象外) |
| Advancedの識別 | `b1b`=Advanced、`a2`=Standard(`docs/pm/PM_GOVERNANCE.md:378`)。b1bのKeyPhraseが委任文の3件(hand down/catch sight of/catch one's breath)と一致 |
| Advanced KP(3件のみ) | `run_sf_prod_01/b1b/key_phrases/keywords_canonicalized.json`: (1)hand down「～を後の世代に受け継がせる」S10 (2)catch sight of「～をふと目にする」S8 (3)catch one's breath「息を整える」S16(本文表層形は`catch her breath`)。3件のため「最大5個」は3個で実施。新たな選定なし |
| 既存KP音声解説(英語) | `b1b/audit/tts_generation_results.json` segments kpN_explanation_en: (1)"to pass something to a younger person or a later generation" (2)"to see something suddenly or by chance" (3)"to pause and breathe normally again after effort" |
| Production KP段モデル | `run_sf_prod_01/key_phrases/b1b_result.json` selection.model_id=`gpt-6-luna`(fulltext_p2、kp_attempts=1)。routing=`er006_model_routing_contract_01.py:45-52`(SUPPORT_MODEL=gpt-6-luna)。API呼出は`er105_kp_fulltext_selector_01.py:295-307` make_selector_fn=Responses API、**reasoning引数なし(provider default)、temperature指定なし**。Trialも同条件 |
| Advanced定義 | `CURRENT_SPEC.md:838`(Advanced=Natural English Adaptation、Target level=CEFR B1)。委任文の「B1〜B2相当」は学習者側の想定として併記 |
| 単価 | gpt-6-luna Input $0.10/Cached $0.01/Output $0.50 per 1M(`er005_output/cost_baseline_01/pricing_snapshot.json`)、¥160/$(`compute_topic_cost.py:4`) |
| STOP確認 | `tools/stop_scope_check_01.py --managed-id FAMILY-Z-STUDY-TEXT-TRIAL-01 --run-dir <run>` rc=0(非停止) |

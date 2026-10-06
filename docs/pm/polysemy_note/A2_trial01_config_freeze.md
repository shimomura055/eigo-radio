# A2 Trial-01構成の再現確認と固定(OPEN-233-LEDGER-POLYSEMY-NOTE-DESIGN-01 A2、read-only・¥0、2026-10-06)
判定: 再現可能(注意点あり)。STOP非該当。機械可読版=`er052_output/open233_ledger_polysemy_note_01/phase0/FREEZE_T01_CONFIG.json`(全script sha256・全switch)
## 1 同一性の根拠
- Trial-01実行(18:49-19:03)はcommit 4ef943f5(19:14)直前。import連鎖の全local module(約60本)の最終commitは全てf1ce315d(10-06 11:30)以前、working tree dirtyなし(.py)。
- entry_point.jsonの埋込sha(er019 runner 164d8ef6/b3 93d0e31e/jaw b3b5b9ff)は現在のsha256と3件とも一致(実測)。
- Checker: run_checker_after_p01.pyは`apply_open233_approved_flow_switches()`既定使用。dump(66d18a3a...)はE2E_02 worker1(081de570...)と`switches_equal_e2e02=true`(provenance)。
- 未確認: pprime_dev/run_checker_after_p01の実行時sha(provenanceにscript shaなし。4ef943f5が初コミットで、以後変更なし)。
## 2 Writer側(いずれもgpt-5.6-luna=routing.WRITER_MODEL、reasoning high、raw_usage_log全行で実測)
| 工程 | 所在 | 回数(Trial-01実測) |
|---|---|---|
| Researcher/Verification | er012 run_researcher/verification_for_topic L161/L184、prompt=vfl01.build_*_prompt(+pprime追記) | research1/ledger1 |
| B3 storyline | er019 runner L141 run_storyline_b3→b3.run_storyline_b3_selection | 1 |
| JA R0/must_fix/R1/R2 | er019_..._ja_writer L148(prompt)/L209-235(call_fresh,call_with_previous_response_id)、DEVELOPER_MESSAGE L69 | original2(must_fix1+check_retry1含)/r1 2/r2 2/check計5 |
| EN advanced(b1b faithful) | er003_..._advanced_adaptation_generate L582-699、max_attempts=2 | advanced8(本文1、attempts=1、retry無)、model_id_actual=gpt-5.6-luna、fallback=false |
| EN Standard(a2) | er012 L458- | 未実行(stage=advanced) |
retry/regeneration枠: JA must_fix1回、JA recheck案B1回(er012 L581-)、EN paragraph retry/deviation must-fix各1回。上限は不変。
## 3 Checker側(runner=er052_open233_self_recovery_flow_runner_01.py、全てMODEL=gpt-6-luna L280)
スイッチ全項目(L496-523): FLOOR_MODE=number_only/FLOOR_VERIFY_MODE=off/CAUSAL_FLOOR=False/STAGE2_DOWNGRADE_VERIFY=False/TIER0_G_L_ENABLED=False/PRECHECK_MODE=number_only/STAGE1_RECLASSIFY=True/STAGE2_SECOND_OPINION=True/RECHECK_BEFORE_AFTER_PAIRS=False/STAGE2_VERDICT_REUSE_NONBLOCKING=True/STAGE2_SIBLING_LOCATIONS_CYCLE1=True/STAGE1_MODE=coverage_union/ROUTES=both/R5_MODE=full/R3=medium/R5=high/NEGATION=a/F3_PRECHECK_ALWAYS/STAGE1_FAIL_CLOSED/RECHECK_MODE=coverage_union/MAX_CYCLES=2/HARD_MAX=3/MODEL=gpt-6-luna。KPI継承分(HANDOFF violation_span、VS_*、STAGE4_ALLOWLIST、LADDER_*、REWRITE_REVERT_GUARD等)はdumpに全記載。
- Stage1: r3 medium(L1989)+r5 high+reclassify medium(L1895、reclf prompt sha cf3c7814)。precheck=number_onlyのみ。floor=changed_number(L855)。
- Stage2 body/hook+S1(L4160)。hook_aware(L2767)・disclosure_gap(L2827)降格はスイッチなし常時適用(L3985-3998)。
- Rewrite/Recheck/Stage4: コード上ON(ladder L6167、run_recheck L2154、STAGE4_ALLOWED_REASONS L8307=4種)。Trial-01では発火せず(下記)。
- fail-closed: STAGE1_FAIL_CLOSED=True、API失敗はapi_failureでSTOP許可リスト。Human Reviewへ新経路なし。
- Trial-01実測: 7 call(r3,r5,reclassify,stage2 body/hook,S1 body/hook)、final=RESOLVED_STAGE2_DOWNGRADE、Rewrite/Recheck/Stage4なし、¥2.54。
## 4 model表記差(gpt-5.6-luna vs gpt-6-luna)
正常。Research/Writer系=vfl01.MODEL=routing.WRITER_MODEL=gpt-5.6-luna(er003 L57)。Checker=runner.MODEL=gpt-6-luna(L280、CURRENT_SPEC L2418「Self-Recovery経路はgpt-6-luna、Writer不変」)。同一工程内の揺れなし。未確認: Checker側はraw_usage_logに実response.modelが残らない(call_logにmodel欄なし、providerのaliasは未検証)。
## 5 再現リスクと固定方法
- 非決定: temperature/seed指定は全script grepで0件(固定不可)。web_search結果・JA/ENの生成は毎回変わる。JA must_fix分岐の有無もrun依存。
- 固定可能: ①OPEN233_RESEARCHER_VARIANT(未設定=baseline/pprime、新variant追加時はdev scriptのVARIANTSのみ) ②out_dirに既存research_ledger/storyline_b3/ja_writerがあると再利用(er019 L92-97、dev scriptはassert_fresh_out_dirで防止、再現目的ならtxt再利用で台帳固定が可能) ③Checkerは`--ledger-path/--article-path/--source-path`で入力固定でき、Trial-01成果物(ledger sha 3f6e551e...)を再Check可能 ④model IDはrouting定数でpin済み、API側のmodel更新は検知手段=provenanceのmodel_id_actualのみ。
- 日時依存: provenance/ファイル名の時刻のみ。判定ロジックへの日時依存は未確認(grep未実施)。
## 6 STOP判定
再現不能項目なし。STOP_RECOMMENDED非該当。

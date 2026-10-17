# FZ_COMPLETION_PLAN_01 (委任_13 Phase 1, read-only, JPY0, 2026-10-17)
Status: FZ_COMPLETION_PLAN_READY_PENDING_FABLE。VALIDATED/APPROVED/PRODUCTION_WIRED判定なし。
注: 委任文・ユーザー原文の逐語保存(T-0 a/b)は、応答が安全分類器により中断されたため未実施(下記§0)。

## §0 T-0 / stop_scope
- stop_scope_check rc=3。適用=STOP_NOTICE(docs/pm/delegation_log/2026-10-12_..._STOP_NOTICE.md、sha f1c877e4…37df3、規則b=管理ID本文一致)。STOP_ALL・run直下STOP・RUN_LOCK・RESTART_STORM_LOCK(run_dir直下)は不在。出力 er026_output/family_z_production_e2e_01/_stop_scope_check_13.json。
- 他のセンチネル実在: melos/run_e2e_01/STOP(RUN_CLOSED, 2026-10-12)、melos/run_kgcpw_z_e5_a2_01/STOP と run_kgcpw_z_e5_b1b_01/STOP(+RESTART_STORM_LOCK, 2026-10-15 16:14-16:15、起動3回/300秒)。
- 本委任はread-onlyのため調査続行。有料API 0、git書込 0。

## §1 現状棚卸し
### (a) run一覧(er026_output/family_z_production_e2e_01/melos/)
| run | 最終更新 | 到達 | 費用JPY(再計算) |
|---|---|---|---|
| run_e2e_01 | 10-16(STOP=RUN_CLOSED) | 旧仕様。kp→tts途中 | 108.1056(全額sunk) |
| run_e2e_02 | 10-16(log) / 実体10-13 | writer,std_adjust,plan,support,kp,tts_a2,tts_b1b,provision_shell,gate,assemble,pages,page_verify完了(N01適用前=PD8生成) | 62.8314 |
| run_kga3_off_z_01 / run_kgcpw_z_01 | 10-15 | KP gloss整合Trial用 | 1.1191 / 1.9855 |
| run_kgcpw_z_e2e_01 | 10-15 17:24 | 同一本文でKP再選定(KGCPW)+tts_a2完了+tts_b1b途中(N01+R2)。REGISTER #70のHR Lock 3clip待ちで停止 | 38.7398 |
| run_kgcpw_z_e5_a2/b1b_01 | 10-15 | RESTART_STORMでSTOP、費用0 | 0 |
- 集計: docs/research/FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01/fz_cost_inventory_13.py / .json(JST日別・stage別あり)。
### (b) センチネル: §0参照。
### (c) 既存成果物(run_e2e_02、git追跡済み。wavは.gitignore=ローカルのみ)
- Adv本文 writer/r2.md sha 2a79a472a1d6301c43898d3187e0f23863d59753646d33cfa4224c59ffa03f18(395語)。Std writer/std.md sha 6a47e9d774fced82cbc00f594b3fa69f5ee746f71b6fd96ffc672a8496ca6569(417語)。範囲280-420内。run_kgcpw_z_e2e_01のr2/stdもsha同一。
- モデル: R0/R1/R2/Std調整=gpt-6.1-sol effort high(provenance.json chain)。seed_sha f4a85f5c…。
- 3分割: segment_plan_a2.json fb957bb3…(23 clip)、segment_plan_b1b.json 01c92a67…。dialogue_attribution_a2 d0534398…、b1b cbb91908…。
- Preview/Comment: support/a2_support.json 4ff00745…、b1b_support.json 90ee5296…(Comment各3、IOL/Comment4なし)。run_kgcpw_z_e2e_01と同sha。
- KP選定(Strategy L、候補ID無し): run_e2e_02 a2 keywords_canonicalized 6098c898…、b1b 366d9509…、kp_explanations_b1b 12c2b7ff…。run_kgcpw_z_e2e_01(再選定) a2 96374412…、b1b 4f30281e…、explanations 02b78696…。
- 元英文照合(決定論、今回実施): 両runの全20item(各5)で source_span・source_sentence とも本文に存在し、span⊂sentence=全True。ただし source_candidate_id は全item欠落(Strategy Lは自由記述)。run_e2e_02はKGCPW判定で targets=[]・unevaluated=[]・unresolved=[]。run_kgcpw_z_e2e_01 a2 rank2のglossは resolved_by="KGCPW-04-evidence"(Agent注入の記録でありユーザーHRではない)=引継ぎ不可。
- speaker/Voice: narrator=Aoede、melos=Algieba(PROVISIONAL_UNAPPROVED、OPEN-306)、selinuntius=Erinome、dionysius=Charon(er063:293-299)。Std dialogue 10clip、Adv 11clip(speaker_table.md)。
- HR承認記録(run_e2e_02 audit/human_approved_segments.json): Std full_story_part1_c5(sha 70572ff2…)とcomment_1(465950d2…)、Adv part1_c5。承認キーはcanonical text shaのみでStyleを区別しない。
- 現行試聴URL(暫定、REGISTER #23判断保留): https://shimomura055.github.io/eigo-radio/user_test/family_z_melos_01/standard.html および advanced.html。
### (d) Open Item / REGISTER 現Status
OPEN_ITEMS.md: 306(L809 Voice承認待ち/判断保留)、318(L821 UDR)、327(L830 UDR)、330(L833 UDR)、331(L834 UDR)、335(L838 OPEN候補)、338(L841 UDR)、339(L842 DESIGN_REVISED/UDR)、344(L853 CLOSED/REJECTED)、345(L854 CLOSED)。356(L865 KGCPW、Z E2E完成evidence待ちでPRODUCTION_WIRED保留)。
REGISTER(docs/pm/USER_DECISION_REGISTER_01.md): #10(L27判断済み)、#14(L31保留)、#23(L40保留)、#25(L42 UDR)、#35(L52判断済み)、#45(L64判断済み)、#46(L65判断済み)、#48(L67 UDR)、#51(L70 UDR)、#70(L89 UDR非ブロッキング、Z HR Lock 3clip再生成承認)。
### (e) Style決定箇所
er063_family_z_audio_01.py: Z独自のStyle定数コピー(_N01 L143、_PD8 L109、_R2、_E1 L118、_K2 L120、_M2)と FAMILY_Z_ROLE_STYLE(L168-213)、sha表 _STYLE_SHA256(L147-157)、version "z_v2_pd8_r2_e1_e2up_k2_m2_kpx_20261012"(L35)。narrator style記録/混在STOP(L504-555)。reuse_key=canonical_text+version+voice+style_sha+backend(L568-576)。Dialogue=kind分岐(L435-440,L495-499)で別clip生成→Narrator差替えの影響を受けない。Xのprofile機構(er019_family_x_style_profile_01.py: PD06 L107、P7、K2、P8_KP_JA L137、S3 L150、fx_20261017 L282)はZに未導入。
### (f) Source Reference Contract
CURRENT_SPEC.md:1919 に「Family X/Z共通Core、APPROVED_FOR_PRODUCTION(2026-09-28)」。実装 er030_key_phrase_db_hybrid_source_reference_contract_01.py(assign_candidate_ids L82、restore_source_fields L416、run_..._gate L561)。family_profile="family_z"は NotImplementedError、DB Hybrid Stage1 shortlist前提。Z KP経路は er062_family_z_writer_01.py:931 run_kp_stage / :971 run_kp_with_outer_retry(Strategy L)。現保証は er003_v1_n3_01_assemble.py:385 verify_key_phrase_source_gate(span本文存在のみ、run_e2e_02 a2 PASS 5/5)。IDによる決定論的対応は無い。
### (g) Regression(各1回、JPY0。unittest直接実行)
- OK: er026_family_z_e2e_integration 42、er026_family_z_fiction_production_runner 21、er063_audio 47、er063_n01 12、er062_writer 64。
- FAIL(Z関連): er026_cs_audit_regression_01_test_01 4件(test_layer_not_invoked_for_entity_only_uncertain_melos_said / test_secondary_spelling_exact_stem_is_rescued_by_pattern_a_in_cascade / test_characterization_post_slowdown_unrescuable_ends_stopped_not_hr_open320 / test_post_slowdown_rescue_accepts_when_secondary_exact_stem)、er026_post_slowdown_cascade_rescue_01_test_01 3件(test_no_rescue_consumes_budget_as_before / test_final_classification_top_level_field / test_no_rescue_when_secondary_also_misspells)。共通症状: 'M1_MULTI_CANDIDATE_ACCEPT' が 'CONNECTED_SPEECH_ACCEPT'/'ASR_VALIDATION_UNCERTAIN' より先に受理、'OK' が 'STOPPED' の位置に出る=M1(er006_m1_multi_candidate_01)配線後に旧characterization期待が古い疑い(原因は推定、未特定)。
- FAIL(既知): er006_model_routing_pricing_coverage_test_01.test_flagger_design_models_registered(集合差に FAMILY_Z_WRITER_ADV_R0/R1/R2・FAMILY_Z_STD_ADJUST=test期待集合側の古さ)、er020_tts_retry_local_rewrite_fullseg_test_01.test_recorded_candidates(er011_output/local_rewrite_recovery/run_e2e_01/…の記録参照)。
- 未実行: er026_family_z_stop_sentinel_test_01(testが本物の STOP_ALL を生成・削除するため禁止事項に抵触する恐れ。実行せず名前のみ記録)。run_project_regression.py の --pattern 経由はこのtestを巻き込むため個別unittest実行に変更。

## §2 仕様差分表
| 項目 | ユーザー決定 | 現行Z | 差分 | 対応 |
|---|---|---|---|---|
| Full Story Narrator | PD06 | N01(er063:170-176、生成はPD8) | あり | 配線変更+音声再生成 |
| Std日本語Preview/Comment | S3 | R2(er063:185-189) | あり | 配線変更+音声再生成(原稿再利用) |
| Adv英語Preview | E1 | E1(sha 8862317f…) | なし | 音声は再利用候補 |
| KP英語 | K2 | K2(sha 9d905cfe…、Xと同一) | なし | 再利用候補 |
| Std KP日本語意味 | P8-KP | M2(er063:199) | あり | 配線変更+再生成 |
| Adv KP英語解説 | P7 | 既存X_KP_EXPLANATION_EN(P相当、L206) | あり | 配線変更+再生成 |
| Std 6%減速 | 維持 | 維持(n3_tts.generate_a2_segment_with_slowdown、gate=er063:1152) | なし | PD06併用を実証 |
| AUW | 共通基盤 | 配線済み(06c/06e) | 実run証拠のみ要 | 新runで確認 |
| Dialogue別Voice | PD06非適用 | kind=dialogue分離、Style=Dialogue既存 | なし | 回帰確認 |
| KP方式 | Strategy L維持 | Strategy L | なし | 維持 |
| Source Reference Contract | Z正式適用 | 未適用(family_z NotImplementedError) | あり | 設計要(§5c) |
| Risk Flagger | 対象外 | 無し | なし | 対象外 |
| IOL/Comment4 | 設けない | 無し | なし | — |
| Preview/Comment1順序 | 現行維持 | 現行 | なし | OPEN-338/#48/#51のclose文案(§8) |
| Adv Comment | 表に記載なし | E2_UPBEAT | 指示範囲外 | 現状維持(要確認) |
- 追加差分: CURRENT_SPEC.md:1608 の記述(Narrator PD8、Std JA R2、「E1/R2はX限定」L1251)は本指示で更新が必要。

## §3 再利用可否
| 成果物 | 判定 |
|---|---|
| Adv/Std本文、3分割plan、dialogue_attribution、Preview/Comment原稿 | 再利用可(sha・provenance.json一致を新runで再検証。新run dirへcopyし同一CLIで ensure_stage 再利用=run_kgcpw_z_e2e_01がstage log 0.0秒・費用0で実証済みの先例) |
| KP選定 | 再利用可(provenance再検証要)。推奨=run_e2e_02版(clean、unevaluated=[])。kgcpw版は再選定+Agent注入gloss解決を含むため非推奨 |
| Dialogue音声(Std10/Adv11) | 再利用可(provenance再検証要)。Style不変・reuse_key一致が条件。version定数をbumpすると全再生成になるためbump不要 |
| Adv Comment E2_UPBEAT、KP英語K2、shell、topic_intro、JP title | 再利用可(provenance再検証要) |
| Narrator Full Story(Std13/Adv13-14 clip) | 再生成要(Style=PD06) |
| Std JA Preview/Comment(計4 clip) | 再生成要(S3) |
| Std KP日本語(5) | 再生成要(P8-KP) |
| Adv KP英語解説(5) | 再生成要(P7) |
| Adv Preview(E1) | 再利用可、または再生成(新Gate再通過) |
| 過去HR承認、ASR、wav | 無条件引継ぎ不可。HR承認(text shaのみ照合)は新run dirへcopyしない |
- Dialogue clipは既に分離生成のため、Narrator差替えで再生成は不要。

## §4 費用照合
- ¥300の所在: CURRENT_SPEC.md:1608 「本E2Eの追加API費用上限JPY300/警告JPY200(2026-10-12)」、delegation_log _02 L25、COST_LEDGER_MELOS_01.md。上限は「本E2E」の仕様で、今回のPD06/S3等の追加再生成まで含む明示承認はない。
- 実測累計: run_e2e_01 108.11 + run_e2e_02 62.83 = 170.94。COST_LEDGER §8-9記載の累計は233.5(ASR Trial 39.61+8.21、再評価約14.7含む)。別管理IDで発生したZ関連: KGCPW Z runs 41.84(1.12+1.99+38.74)、AUW 06e 3.51。
- 残枠: ledger基準 300-233.5=66.5。KGCPW・AUW分も算入すると約21。どちらを算入するかは未決。
- 再生成見積(既存wav秒数ベース): 再生成対象=Std narrator146.7+Preview16.1+Comment56.5+KP_JA9.3=228.6秒、Adv narrator137.8+Preview14.2(再生成する場合)+KP解説22.9=174.9秒、計約403.5秒。実測単価(Gemini+ASR+Azure含む)0.065〜0.085 JPY/秒(kgcpw tts_a2 18.48/283.6s、tts_b1b 18.28/239.5s、run_e2e_02 23.17/274s・17.0/245.4s)。→約26〜34 JPY、retry/LR・HR再入を1.3〜1.5倍見て約35〜50。文章系はKP再利用なら0、KP再選定+gloss+解説なら約2〜6。SRC D2を採る場合のみKP再選定費用が加わる。全面再生成なら約44(×1.5で約67)。
- 結論: ledger基準なら残枠66.5で収まるが余裕は薄い。他ID分算入だと不足の可能性。追加承認額の案=新規に「本指示分 JPY100上限(警告70)」の別枠。当日(10-17)開発費は既使用約370.8+BAPE進行中のため1000円/日の事前確認が必要。

## §5 配線設計案(Phase 2、Opus条件A対象)
(a) 推奨1: er063のFAMILY_Z_ROLE_STYLEが参照する定数を er019_family_x_style_profile_01.py の PD06_TEXT/SUPPORT_JA_STYLE_S3_20261017/P7_TEXT/P8_KP_JA_TEXT/E1_TEXT/K2_TEXT へ差替え(コピー定数を削除=共通性、PM_GOVERNANCE 18節)。shaはXの定数と相互assert。narrator_style_recordをPD06 shaへ更新し、旧run dirは混在STOP。推奨2: Zにprofile機構(fz_20261017、style_profile.json固定記録)を導入しXとコード共有。2は堅牢だが変更範囲が大きい。
(b) Dialogue: kind=dialogue(role_key DIALOGUE_*)をStyle差替えの対象外とし、test(Dialogue clipのstyle_sha不変、Narrator=PD06 sha、speaker→Voice対応)を追加。FAMILY_Z_ROLE_STYLE_VERSIONはbumpしない(reuse_key維持)か、per-role化。
(c) SRC: D1=Strategy L出力へ事後に決定論ID付与(sentence index+span offset)し、Pythonがsource_sentence/spanを復元、不一致/曖昧ならSTOP(プロンプト無変更、既存KP再利用可)。D2=プロンプトに文IDを付けLLMにIDを返させる(契約に忠実だがStrategy Lの入力形式が変わりKP再選定が必要)。どちらも「新仕様候補」の側面があり、Fable/ユーザー判断が必要(§9)。
(d) retry/resume: ensure_stageのprovenance、KP外側retry(3回)、generate_or_reuse_zのreuse guard、AUW 3回フロー、Std減速後再検証と整合させる。
(e) Dangling Reference: N01/PD8/R2/M2の文字列参照(er063 27箇所、er063_*_test 37箇所)、CURRENT_SPEC 1608、OPEN-345/#46のN01文言決定の扱い。
(f) test: 既存Z回帰(上記)+Style sha表test+Dialogue不変test+SRC integration test+新run dirでの混在STOP test。DefaultOffIsolation不要(承認済み仕様の正式配線)。
(g) Opus観点: ①Xとの定数二重管理の解消 ②Dialogue分離の保証 ③SRC D1/D2の妥当性と「KP方針不変」 ④旧runのHR承認・reuseの混入防止 ⑤7件の既存FAIL testの扱い。

## §6 実走計画(Phase 3)
- run名案: run_e2e_03(既存と衝突なし)。新run dirへ run_e2e_02 の writer/ support/ segment_plan_* dialogue_attribution_* speaker_table key_phrases/ をcopy(review_lock_state・human_approved_segments・audit・narrationのwavは除外または別途reuse検証経由)。正式CLIは --run run_e2e_03 --mode real --approved-budget-jpy <上限> --tts-execution-mode STANDARD。再利用の正式手段=provenance.json+ensure_stage(先例あり、STOPにはならない見込み)。
- stage: seed_check→writer(reuse)→std_adjust(reuse)→plan(reuse)→support(reuse)→kp(reuse or SRC)→tts_a2→tts_b1b→provision_shell→gate→assemble→pages→page_verify。
- Gate: AUW・6%減速(verify_std_english_slowdown)・Voice assignment・Assembly。Human Review(Lock)が発火したら停止(予想: Std part1_c5「Melos said.」がOPEN-318で再発)。
- 試聴: user_test/family_z_melos_02/ 配下(GitHub Pages)。
- 費用上限: §4の追加承認待ち。承認が出るまで有料実行しない。
- 前提: STOP_NOTICE(rc=3)の扱いをFableが決める。run_e2e_03実走前に26節の手順でstop_scope_checkをやり直す。

## §7 Cross-Family上位ルール文案(要点。8項目の逐語はユーザー原文§5からFableが転記)
- PM_GOVERNANCE.md 新節: 現末尾は27節のため「28. Cross-Family同時Production配線原則」を提案。接続=18節(横断共通化)、21節(既存仕様確認Gate)、22節(Trial開始前/終了前チェック)、11-3(Opus Gate)、27-7(開発対象はX/Z/将来Y)。
- 8項目: 仕様分類(共通/固有)、Family別APPROVED追跡、同時配線・テスト・runtime確認、Family別PRODUCTION_WIRED判定(他Family証拠の代用禁止)、困難時はOpen Item記録でclose禁止、例外(固有仕様・不採用)、新Family(Y)は共通承認仕様を最初から対象、開始/終了チェックへ組込み。
- CURRENT_SPEC 追記案(表): PD06 X=PRODUCTION_WIRED(L1254, 2026-10-16) / Z=APPROVED(2026-10-17指示)、S3 X=PRODUCTION_WIRED(L1259-1261, 2026-10-17) / Z=APPROVED、E1・K2・P7・P8-KP X=PRODUCTION_WIRED(L1254) / Z=APPROVED(E1・K2は実質配線済み・要runtime確認)、6%減速 X・Z既存、AUW=全Family(L2752、L2777でユーザーPRODUCTION_WIRED承認)、M2P0+A X固有(Z不採用=#45/OPEN-344)、Risk Flagger X固有、SRC=X配線済み(L1919)/ Z=APPROVED(2026-09-28共通Core+2026-10-17指示)・未配線、Strategy L=Z固有。
- DECISION_LOG文案: 2026-10-17 ユーザー決定(上記A〜D、上位ルール)、Z側のPD8/N01/R2記述のsuperseded注記。
- OPEN_ITEMS新規案(現最大OPEN-411、BAPEが並行して採番する可能性あり、確定は末尾Grep): OPEN-412 Z共通音声仕様配線追跡(PD06/S3/P7/P8-KP)、OPEN-413 SRC Z配線、OPEN-414 Cross-Family配線追跡台帳、OPEN-415 既存Z regression FAIL 9件(上記7+既知2)。

## §8 close候補(文案のみ)
- OPEN-338 / REGISTER #48・#51: 「ユーザー2026-10-17指示§2Aにより現行方式維持、新方式不採用、追加Trial不要」としてclose。
- OPEN-345・#46・OPEN-344・#45は既にclosed/判断済み(N01文言は本件でPD06に置換されるため文言論点は消滅する旨の注記のみ)。
- 再質問しない項目: Z構成(3分割・Comment3・IOL/Comment4なし)、Sol R0→R1→R2、Strategy L維持、Risk Flagger対象外、Preview/Comment1順序、Dialogue別Voice。
- #23(Melos最終試聴)は別扱い。新試聴ページ完成時にユーザーへ提示。

## §9 リスク・STOP候補・判断候補
- A既判断: 全体仕様(§2A〜D、ユーザー2026-10-17)。
- B自己解決: 定数の差替え方式(§5a推奨1)、Dialogue不変test、version非bump。
- C独立: 既存FAIL test 9件の是正(先行是正の要否はFable判断)。
- D新判断: (1)費用上限(別枠JPY100案)。(2)SRCのD1/D2(「候補ID等」の解釈、新仕様性)。(3)KP再利用元(run_e2e_02推奨)。(4)Melos HR(Melos said)が再発した場合の事前承認の可否。(5)Voice Algieba(OPEN-306)は新試聴で承認。(6)Adv Commentは表に記載なし、E2_UPBEAT維持で良いか。
- リスク: STOP_NOTICEがrc=3を返す(Fable判断で解除範囲を確定)。wavがgit未追跡で消失しうる。run_e2e_02由来のHR承認はStyle変更後に誤適用の恐れ(新run dirへcopyしない)。main/BAPEの並行commitによる衝突。

# AUW 委任_03 IMPLEMENTATION (EN統一judge配線) -- branch feat/auw-unified-asr-01, 未commit
JPY 0 (mockのみ)。main無変更。JA/A2slowdown/Dialogue/KP/Prompt/model/voice/閾値/Gate/HR Lock/予算guard/SSOT 無変更。U1=True, U2=A2_ONLY 維持。
変更一式のpatch: patch_03/auw3_changes.patch (+ 新規 er078_asr_unified_en_wiring_test_01.py)。テスト全体結果: patch_03/test_full_{baseline,post}.json

## 1. 配線点 (file:line)
- er006_secondary_asr_01.py:655 evaluate_attempt_with_cascade_detail (adapter。戻り型・callerキー維持、attempt_ctx kwarg追加)
  - L902 _secondary_fn / L923 unified_judge_mod.unified_judge(...) / L623 _AzureShared / L569 begin_secondary_run(opt-in run cache+circuit breaker)
  - 既存P連鎖(val.evaluate_attempt -> CS Equivalence -> Tier3 -> non-Latin KP -> CMU CaseA/homophone -> M1)は維持し、その後段でunified_judge。Primary#2 / Secondary#2 / 4段枯渇->stop_retrying+HR直行 は撤去。
- er006_preprod_hardening_01_validation.py:627-631 _MARKED_NUMBER_RE / _is_number (25xpercentx, 5xdollarx等をnumber扱い。28th等序数は対象外)
- er078_asr_unified_judge_01.py:77 COST_GUARD_IN_UNIFIED_JUDGE更新、force_secondary一致branch、negation_diffの縮約形展開
- leaf: er003_v1_sing01_voice01_generate.py(EN charon) / sing01_news_tail_fix / sing01_point_headings_aoede / er012_b_family_voices_production_01 / er003_v1_crosslevel_audio_02_common(minimal fallback+LR re-TTS) / er003_v1_repro01_main_generate: asr_judgement をattempts_logとOK戻りに追加
- er011_human_review_lock_01.build_attempts_detail に asr_judgement、er006_master_audio_store_01 は manifest保存+再利用時 asr_judgement_inherited
- registry hook: er019:949,1312 / er063:984 / er003_v1_n3_01_tts_generate.py:1095,1244 (write_listening_list_safe: 例外を投げない)
- ページ節: er019 build_player_html / er063 build_listening_page_html+build_index_html / legacy単独HTML(audit/pass_with_warning_listening_list.html)

## 2. caller互換表
戻りtuple/dict型・主要キー(verified, classification, final_status, human_review_required, stop_retrying, steps, cost)維持。追加はasr_judgementのみ(additive)。
stop_retrying=固定False。human_review_required=attempt_ctx.is_last_slotかつNG時のみTrue。cascade_enabled=False は従来どおりval.evaluate_attempt結果。
caller: 上記leaf、Trial/eval script(er010_no9_*, er012_editorial_b_voices_trial_09_audio, er011 kp runtime evidence, er006_retry_cascade_prod_01_eval, er008_n8_revalidation_15, er057_*, er077 runner, n3 rescue)は呼出シグネチャ不変(attempt_ctxは省略可)。

## 3. state -> return
PASS -> verified True / PASS_WITH_WARNING -> verified True(+warnings) / NG_PROTECTED, NG_EXCLUDED, NG_BOTH, NG_SECONDARY_UNAVAILABLE, NG_PRIMARY_ASR_FAILURE -> verified False(最終slotでHR)。
値guard DIFF->NG_PROTECTED、AMBIGUOUS->P3(NUMERIC_AMBIGUOUS_SURFACEは表層一致時のみ)。force_secondary一致=PASS(reason force_secondary_agreed)。

## 4. COST_GUARD結論
旧guardは到達不能(旧累積は最大約$0.000022)。実費で適用: Secondary1回見積(wav秒/3600*$1)が$0.05(=180s超)ならSecondaryを呼ばずfail-closed(NG_SECONDARY_UNAVAILABLE, cost_guard_triggered=True)。定数 "APPLIED_AT_ADAPTER_SECONDARY_FN_ACTUAL_SECONDS_03"。
SecondaryCache: 既定は呼出単位。run共有cache/circuit breakerはbegin_secondary_run()でopt-in(runnerは未導入)。

## 5. 新ラベル下流 (D)
新ラベル(PASS_WITH_WARNING等)はasr_judgement内にのみ存在し、既存classification/final_status集合は不変 -> allowlist/件数集計の更新対象なし。
追加・変更箇所: build_attempts_detail(er011)、registry _SKIP_KEYS(attemptログ重複排除)、master store継承、er019/er063再利用継承(asr_judgement_inherited)、n3 rescue(post_slowdown_cascade内にasr_judgement、verified時は置換し旧はasr_judgement_pre_slowdown)。
HR queue: 件数/形式変更なし(最終slot NGのみ従来どおり)。

## 6. registry hook / ページ節
tts完了時に audit/pass_with_warning_listening_list.json を再導出(冪等・失敗は生成継続)。節「事後試聴リスト(PASS_WITH_WARNING)」は常時表示、空は「0件」。
HTML証跡(screenshot代替, 実関数生成): evidence_03_pages/ z_standard_page_N1/N0.html, z_index_with_sections.html, x_player_b1b_N1_a2_N0.html, legacy_standalone_N1/N0.html, pass_with_warning_listening_list_N1.json

## 7. テスト
- 新規 er078_asr_unified_en_wiring_test_01.py 53 passed(adapter/e2e mock/registry/page/force_secondary/COST_GUARD/最終slot HR/LR_REWRITTEN/_is_number/circuit breaker/縮約形否定)。e2e: Primary NG+Secondary PASS -> 最終成果物PASS_WITH_WARNING かつ試聴リスト掲載(test_e2e_leaf_to_listening_list_and_page_section)。
- er078 judge 45 / value_guard 58 / registry 9 / static audit 12 passed。er021*/er006_preprod 102 passed。
- 全test per-file: 失敗 baseline 150 -> post 184 (新規34, 改善0)。内訳は下表。
| 分類 | 件数 | 備考 |
|---|---|---|
| commit後に解消する未commit-diff guard | 4 | er019 FamilyAUnchanged, er020x2 ProductionModuleUnchanged, er064 ProductionUnchanged |
| 承認設計で撤去した挙動を期待する既存test(Primary#2/Secondary#2、通常不一致でSecondary不呼出、cascade枯渇HR直行等) | 30 | er006_secondary_asr_01_test 11, ..._m1_wiring 6, er011 f1 6(同一3x2形式), er011 CS wiring 3, er021 Tier3 2, er026 primary2_single_pass 1 |
期待値は変更していない(委任の禁止事項)。
- G: 事前14 FAIL(main worktree eigo-radio-crbn と照合)と er006_secondary_asr_01_test の事前4 FAILは同一(scratchpad crbn_pair/baseline記録)。

## 8. 静的監査
allowlist=phase post_wiring_en(EN配線済み/JA未配線, 33件カテゴリ付き)。test_post_wiring_en_* 4件で固定、audit 12 passed。postwiring(完全)ではdeferredカテゴリ0を要求。

## 10. 未実装 / 逸脱
- 未実装: JA/J11(委任_04)、A2 slowdown/Dialogue/KP(委任_05)、runnerへのbegin_secondary_run導入、B/C family hook、leafのis_last_slot配線(crosslevel minimal fallback以外)、crosslevel以外のLR script_version配線、post-slowdown直接classifyの統一。
- 逸脱: (1) commit/pushは未実施(既存30test期待値が設計と矛盾=動作確認未完了のためCLAUDE.md規定でユーザー確認)。(2) 統合中に判明した偽否定(承認済み縮約形等価をnegationゲートが再否定)をjudgeで是正。

## 9. 既存test追随(委任_03b/03c) -- 状態: 03b(alpha適用・beta保留)→03c(beta=選択肢A適用・全解消)
実行環境注記: testは `.venv/Scripts/python.exe`(pronouncing等が入るrepo標準)で実行。システムの `py` は pronouncing 無しでCMU系testが偽失敗する。
JPY 0(mock)。ただし作業中の事故1件: 修正途中のtest(未mock)が最終slot HR package経路で `_resolve_unresolved_entity_for_review` を実呼出し、
Perplexity sonar API へ最大2回(pytest 1回ごと)実requestを送った可能性(cost logger未初期化で例外終了、レスポンス/課金額は未確認、推定 数円未満)。
以後の該当testは同関数をmock化済み(下表)。

### 9-1 分類表(失敗30 id + gamma4 id)
区分: alpha=撤去済み挙動(呼出回数/経路/HR出口時期)の固定、beta=承認済み等価・救済の最終判定の固定、gamma=未commit-diff guard。
assertが見ているもの: 「回数/経路」= 呼出回数・step名・human_review_required/stop_retrying、「最終判定」= verified / classification。

| # | test(ファイル::名) | 失敗assert | 旧前提 | 新設計の根拠 | 区分 |
|---|---|---|---|---|---|
| 1 | er006_secondary_asr_01_test::entity_like_mismatch_triggers_primary_2 | cascade_invoked, calls==1, step primary_2 | Primary#2(同一音声OpenAI再転写)を1回呼ぶ | DESIGN_01 §4-9表(Primary#2廃止) / 原文L54「Primary NGは原則Secondary」 | alpha(経路) |
| 2 | 同::primary_2_pass_stops_cascade_before_secondary | Secondary calls==0 | Primary#2でPASSしSecondary不呼出 | 同上 | alpha(経路) |
| 3 | 同::full_cascade_all_fail_routes_to_human_review | primary==1, secondary==2, HR, steps 4件 | Primary#2+Secondary#1/#2, 尽きて即HR | §4-3/§4-9(S#2廃止・尽きHR直行撤去)・§4-7(HRは最終slot) / 原文L58「両NGで再生成」 | alpha(回数) |
| 4 | 同::force_secondary_true_primary_pass_secondary_mismatch_not_auto_passed | human_review_required True | 即HR | §4-7「HR queueは最終slot NGのみ」 | alpha(HR時期)。verified False(自動PASSしない)は維持+最終slotでHR Trueを追加assert |
| 5 | 同::force_secondary_true_primary_mismatch_preserves_existing_cascade | step primary_2 必須 | Primary NGでPrimary#2経路 | §4-9(force_secondaryはPrimary PASS時のみ) | alpha(経路) |
| 6 | 同::tuple_wrapper_matches_val_evaluate_attempt_shape_and_logs_human_review | stop_retrying True, steps 4 | 尽きでstop_retrying・HR queueに4step記録 | §4-9(stop_retrying=False固定), §4-7 | alpha(回数/HR時期)。最終slotでHR queue記録・途中slotは未記録を追加assert |
| 7 | 同::homophone_requires_arpabet_match_not_string_similarity | cascade_invoked False | 通常内容語差はSecondary不呼出 | 原文L54「不一致の種類によらず」 / §4-3d | alpha(経路)。Secondaryも"wet"ならNG_BOTH(綴り類似でPASSしない)で安全側維持 |
| 8,9 | 同::case_b_unresolved_entity_does_not_auto_pass_and_enriches_review / ..research_failure_still_reports_unconfirmed | human_review_required True | 4step尽きで即HR | §4-7 | alpha(HR時期)。最終slot(attempt_ctx)でHR+pronunciation_lookups(unconfirmed marker)を維持、途中slotはHRなし |
| 10 | 同::non_latin_cascade_disabled_by_default_even_if_non_latin_and_mismatch | calls==0 | 非ラテン不一致でも既定OFFならSecondary不呼出 | 原文L54 / §4-9(非ラテンは「Primary NGは原則Secondary」に包含) | alpha(回数)。non_latin_cascade_invoked False・Secondary不一致ならreject を追加 |
| 11 | 同::non_latin_cascade_not_triggered_for_garbled_latin_mismatch | calls==0 | 同上 | 同上 | alpha(回数)。非ラテン層不発動+judge単独1回を assert |
| 12 | 同::negative_fixture_new_formal_not_non_latin_no_secondary_call | calls==0 | 同上 | 同上 | alpha(回数)。陰性対照(Secondaryも"new formal")でNG_BOTH |
| 13-18 | er006_secondary_asr_01_m1_wiring_test_01::primary2_fires / secondary2_fires / all_miss_goes_to_human_review_unchanged / forced_secondary_unexplained_still_hr / forced_secondary_contradiction_rejects / m1_enabled_false_restores_legacy | step primary_2/secondary_2でM1受理、4step到達、HR即時 | Primary#2・Secondary#2でのM1受理、尽きHR | §4-9(Primary#2/S#2廃止)・§4-7 | alpha(経路/回数/HR時期)。M1 secondary_1受理・矛盾拒否(誤受理0)・m1_enabled=False不発は維持 |
| 19,20 | er011 CS wiring::disabled_by_default_no_new_asr_calls... / enabled_but_no_category_match_skips_asr_calls | calls=={secondary:0,local:0} | 通常内容語差でSecondary不呼出 | 原文L54 / 重複呼出防止L60 | alpha(回数)。classification=TRUE_CONTENT_MISMATCH・Eq層不発動(最終判定assert)は既に通過=不変、localは0、Secondaryはjudgeの1回のみ |
| 21 | er026 post_slowdown::primary2_single_pass_rescues_after_tier3_no_corroboration | status OK(Primary#2救済) | Tier3不成立後にPrimary#2が正規綴りで単発PASS | §4-9(Primary#2廃止), 重複呼出防止 | alpha(経路)。Primary 1回・Azure 1回(Tier3とjudgeで共有)・独立証拠なし(Mellow)でSTOPPED を assert。ledger.json依存を避けるため空ledgerをmock |
| 22-27 | er011 f1::cascade_replay_user_example_stays_non_pass_with_supporting_secondary / ..multi_residual_after_first_eq_eligible_diff_stays_non_pass (各3収集形: plain/_f/F1RegressionWrapper) | verified is False (最終判定) | Secondary(+local)がcanonical全文を支持しても通常内容語差はSecondary不呼出ゆえNG | 原文L54-55「Primary NG・Secondary PASSならPASS_WITH_WARNING」/ §4-3d | **beta(最終判定)=未解決** |
| 28 | er011 CS wiring::enabled_mixed_evidence_does_not_accept_but_records_diagnostic | verified is False, classification TRUE_CONTENT_MISMATCH | Secondaryがcanonicalを支持・localが否定(MIXED)なら受理せず | 同上 | **beta(最終判定)=未解決** |
| 29,30 | er021 Tier3::role_not_applicable_tier3_not_attempted / no_segment_id_tier3_not_attempted | verified False, cascade_invoked False | role非適用/segment_id無しでは(Tier3が走らず)救済されない | 原文L54 / 適用範囲「全Section」 | **beta(最終判定)=未解決** |
| g1-4 | er019 FamilyAUnchanged / er020 x2 ProductionModuleUnchanged / er064 ProductionUnchanged | git diff が空であること | 未commitの委任_03変更を検知 | commit後に解消(4件とも失敗メッセージが 委任_03 の変更ファイル名: er003_v1_n3_01_tts_generate.py, er003_v1_sing01_voice01_generate.py, er011_human_review_lock_01.py 等) | gamma(commit後確認はcommit実行時に実施) |

件数: alpha 21 id(= er006 secondary 12 + m1_wiring 6 + CS wiring 2 + er026 1)、beta未解決 9 id(= 論理5件: F1 2件x3収集形 + CS mixed 1 + Tier3 2)、gamma 4 id。合計 34 id(委任_03の30件 + gamma4)。
注: 委任文は er006_secondary_asr_01_test を「11」としたが実測12 id(30件の合計は 12+6+6+3+2+1=30)。

### 9-1a (03b記録) beta 9 idの切り分け(「撤去挙動の固定」と断定しない根拠)
- 6+1+2 idとも assert は**最終判定**(`verified`)を見ている(コード: f1_test L203/L213, CS wiring L200(旧), er021 L308/L315)。呼出回数だけのassertではない。
- 原因は実装側のF1/Eq層/Tier3 layerの退行ではない。layer単位の判定は不変であることを実測(`beta_probe_f1_cs_secondary_routes.out.txt`):
  F1 user例・multi residual: asr_judgement.primary.passed=False(TRUE_CONTENT_MISMATCH)、connected_speech_equivalence_layer_invoked=False、layers=[]。受理の経路は常に reason_code=secondary_confirmed / state=PASS_WITH_WARNING(Secondaryが全文でcanonicalを支持した場合のみ。Secondaryがprimaryと同じ"dogs"等ならNG_BOTHでverified=False)。
  CS mixed: Eq層は呼ばれ layers=['cs_equivalence']、層判定MIXED(診断)。最終は同様にSecondary独立確認のみ。
  Tier3: role非適用/segment_id無しで tier3 layer・tier3_corroboration_secondary stepは発生せず(role gate不変)、受理はjudgeのSecondary確認のみ。
- 旧期待のNGは「通常内容語差(cats/dogs, turn/turned, points/point)ではSecondaryを呼ばない(DESIGN_01 §4-3d: 旧は呼ばない→新は呼ぶ)」の副産物。新設計ではPrimary NGは原則Secondary、Secondary PASSならPASS_WITH_WARNING(原文L54-55)。一方で `DESIGN_01.md:65` は「Tier1/CS層gateは不変(§6 C-G)」としており、Secondary確認ルートがrole gateやEq層のMIXED判定を上書きするかは設計文書上明示がない。ゆえに実装側の退行ではなく**設計判断が要る**と判断し、委任文(beta期待値は変更禁止)に従い期待値を変更せずSTOP。
- 提案(未適用): `patch_03b/*_PROPOSED.py`。layer不変条件(primary.passed=False、Eq層不発動/MIXED診断、tier3未発火、受理はsecondary_confirmed+PASS_WITH_WARNINGのみ)を assert に置換し、独立証拠なし(Secondaryもprimaryと同じ転写)なら従来どおり NG を assert。3ファイルとも単独実行で PASS(39 / 16 / 62 passed)。承認があれば元ファイルへ適用するだけで済む。

### 9-1b (03b記録) test結果
- 実行: `patch_03b/run_tests_per_file.py`(summary行をregexで解析。旧集計の「summary解析問題」=500文字切り捨てを修正)。対象 er006/er007/er011/er019/er020/er021/er026/er064/er078 の test 96ファイル(ファイル単位・直列)。
- 結果(alpha適用後): passed 1,671 / failed 38(`patch_03b/test_post_03b_alpha_applied.json`)。
- baseline(委任_03 `test_full_baseline.json`、同96ファイルのうち95がjson内)との失敗id差分: baseline 26 → 現在 38。**新規失敗 13 id = beta 9 + gamma 4**(alpha 21 idは全て解消)。baselineから消えた1件: er026_family_z_e2e_integration_test_01::MockFullPipelineTest::test_shared_state_files_unchanged_by_mock_run(作業ツリーの未commit出力差分に依存して揺れる)。
- baselineには passed 件数が無い(summary切り捨て)ため passed 合計の差は取れない(今回から取得)。
- 揺れる/環境依存の記録: (1) `.venv` 以外のpythonでは pronouncing 無しで CMU系testが偽失敗(homophone_wait_weight, case_a_entity)。(2) er026 post_slowdown の3件(final_classification_top_level_field, no_rescue_when_secondary_also_misspells, OuterLoop no_rescue_consumes_budget)は baseline から失敗。原因: 未commitの `er006_output/pronunciation_ledger_01/ledger.json` に "melos"(2026-10-12T13:17:58, confidence=low)が入っており、M1が"Mello(s)"を受理してSTOPPED期待が崩れる。再現: ledger.json の作業ツリー差分がある状態で当該testを実行(commit済みledgerのmain worktreeでは通る)。本委任では安定化していない。(3) er019/er020/er064 の guard は作業ツリー差分の有無で決まる。
- Regression基準の再現(API 0、`melos_m1_replay_api0.py`): er077 evidence の保存転写36件を新adapterで再判定(Secondaryは保存されたAzure転写をmock)。Melos said: 26/27 verified(旧27/27)、M1受理 20/21(旧21)、保存結果になかった新規受理 0(誤受理0)。1件の差分(Melos_said_L2_adv_t1_raw__segNone: Primary "Mallow said." をPrimary#2再転写 "Mello said." でM1受理していた)は、Primary#2廃止により、当該clipの保存Secondary転写が無く NG_SECONDARY_UNAVAILABLE になったもの(実Secondaryが"Mello said."等を返せばM1/Secondary経路で受理される見込みだが、本検証では未確認)。

### 9-2 委任_03c: beta 9 id(論理5件)へ選択肢A適用(2026-10-15, Fable判断)
根拠(Fable判断): 旧期待(通常の内容語差ではSecondary不呼出→verified False)は、ユーザー原文 L54「Primary NGなら、不一致の種類によらず原則Secondaryを実行する」・L55「Primary NG・Secondary PASSなら、PASS_WITH_WARNINGとして採用する」と正面から矛盾し、承認済みフローへの追随に当たる。L97の優先規定(重大内容差=数値・否定)は値ガード/否定ゲートで別途担保。cats/dogs等で独立Secondaryがcanonical全文を支持する場合の採用+事後試聴リスト登録は承認済み設計そのもの。選択肢Bは新ガード=未承認仕様追加のため不採用。layer単位の判定(Tier1/CS gate・role gate・MIXED)は不変(DESIGN_01:65と整合)。
適用: `patch_03b/*_PROPOSED.py` を元fileへ反映(各箇所に `# AUW 委任_03c(選択肢A): ...` コメント)。
- er011_b1_connected_speech_validator_01_f1_test_01.py (F1 user例・multi residual): Primary側 passed=False/F1 label・Eq層不発動・Secondary 1回。Secondaryがcanonical支持なら verified かつ reason_code=secondary_confirmed / state=PASS_WITH_WARNING。Secondaryがprimaryと同じ"dogs"等ならverified False(NG_BOTH)。
- er011_connected_speech_equivalence_layer_production_wiring_01_test_01.py (Eq層MIXED): Eq層step全て EQUIVALENCE_LAYER_MIXED_EVIDENCE_INSUFFICIENT(受理なし)不変。受理は secondary_confirmed / PASS_WITH_WARNING のみ。Secondaryが支持しない場合 verified False・TRUE_CONTENT_MISMATCH・非受理。
- er021_en_asr_semantic_equivalence_production_wiring_01_test_01.py (Tier3 role非適用/segment_id無し): adapter.layers に tier3 無し・tier3_corroboration_secondary step無し(role gate不変)。受理は secondary_confirmed / PASS_WITH_WARNING。Secondary非支持ならverified False。
差分の量: 変更量: f1 +32行相当 / CS wiring +38 / er021 +23 (git diff --stat、計 +72/-21)。
実測(単独): f1 39 passed / CS wiring 16 passed / er021 62 passed(+86 subtests)。
全体(96ファイル per-file, `patch_03b/test_post_03c.json`, 外部通信ブロック付き): passed 1,679 / failed 30。baseline(同ファイル分)失敗26 id に対し新規は gamma 4 idのみ(beta 0、alpha 0)。baselineから消えた1件は er064_kp_int_02::P5Rules::test_tokens_vs_p0 だが、同一testが「ModuleNotFoundError」付きの文字列差で再出現した扱い(両方に存在: 既存失敗のまま)。誤受理0維持(Secondaryが同じ誤りならNG_BOTH、Secondary障害はNG_SECONDARY_UNAVAILABLE、MIXED/role gate/Eq層不発動はassertで固定)。

### 9-3 事故記録(委任_03b: 未mock testからの実API request)
- 事象: 03b作業中、修正途中の未mock testが最終slot HR package経路(`er006_secondary_asr_01.py:960-962` の `_resolve_unresolved_entity_for_review`)を通り、`er006_pronunciation_research_01.py:101` の `requests.post`(Perplexity sonar)へ最大2回(pytest 1回につき1回)実requestが出た可能性。応答直後の `cl.record`(同:114付近)で cost logger未初期化(`er005_cost_logger.py:77-78` RuntimeError)により例外終了。
- 実額: **ログ未記録・未確認**。確認作業: `*.jsonl/*.json/*.log` を当日更新分で sonar/perplexity をGrep → 費用ログ/raw_usage_logには該当記録なし(docs/pm/transcripts/*と er011_output/pm_agent_read_audit_01/per_call.jsonl のhitは本事故と無関係)。cost logger未初期化のため記録が構造的に残らない。推定は数円未満(sonar 1 requestの典型単価、実額は未確認)。Perplexity管理画面での確認が必要。
- 再発防止(mock化済み): `er006_secondary_asr_01_test.py:125-126,354-355`(関数差替、finallyで復元)、`er006_secondary_asr_01_m1_wiring_test_01.py:119,142,162,184`、`er026_post_slowdown_cascade_rescue_01_test_01.py:43,139,193`、`er078_asr_unified_en_wiring_test_01.py:253`。
- 追加の検証手段: 03cの全test実行は、外部通信(非localhostのDNS/connect)を送信前に遮断するpytest plugin(scratchpad、リポジトリ外)付きで実行し、遮断ログを確認した。結果: 遮断された試行は4種(api.openai.com: er007_ja_secondary_asr_01_test::test_unrelated_kanji_reading_not_confirmed ほかtest外1箇所、huggingface.co: er011_open128/er011_open121の各1件)。いずれも既存test(本委任変更外)で、新規変更のtest 3ファイルとER078 EN配線testからの外部通信は0。これらの既存testは遮断なしだと実API(OpenAI)へ出る可能性があるため、委任_04以降の全体実行では遮断plugin付き実行を推奨(要Fable判断: 該当既存testのmock化は本委任の範囲外)。

### 9-4 委任_06向けメモ
- API-0再現(`patch_03b/melos_m1_replay_api0.py`)で Melos said: 26/27 verified、M1受理 20/21。差分1件は `Melos_said_L2_adv_t1_raw__segNone`(Primary#2廃止により保存Secondary転写が存在せず NG_SECONDARY_UNAVAILABLE)。
- 「Melos said. 12/12・12/12」構成は保存データ(er077 evidence)に存在しない。従って実音声での runtime evidence(実TTS→実Primary→実Secondaryの経路)が委任_06で必須。保存データの再判定だけでは合否を主張できない。

### 9-5 委任_03c commit後の確認
- commit cc01cd8f3b8b31a70f692160fa725154c8a92df9 を feat/auw-unified-asr-01 へpush済(main無変更)。
- gamma 4 id(er019 FamilyAUnchanged / er020 x2 ProductionModuleUnchanged / er064 ProductionUnchanged[のtest class全体7件])を再実行: 7 passed。gamma解消。

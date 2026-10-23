# PROD_WIRING_EVIDENCE_08: 委任_24 Fable受入前確認(A-1 Opus条件C必須修正W-01〜04の本文復元・実装照合・静止状態の全回帰)

2026-10-24、API 0・コード変更0。対象実装=commit 4128fffeb(委任_20)。

## 1. W-01〜04本文の復元
復元できた。出典=`C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\subagents\agent-aabcc38e75d54c8b1.jsonl` index 146(assistant SubagentHandback、2026-10-23T09:19:21.994Z、uuid e6bf1977-716e-40b2-a9ef-8ab1091e597a)。逐語保存=`OPUS_REVIEW_A1_CONDC_01.md`。検索条件=`~/.claude/projects/**/*.jsonl`(1,587ファイル)で「W-01」「W-03」+(A-1/不定化/WIRING_DESIGN)を含む2026-10-23以降の行。主セッションjsonl側のsubagent回答はindex 12869(user, `<agent-message from="aabcc38e75d54c8b1">`)。

## 2. W-01〜04 照合表(実装=4128fffeb)
| W | 要求(Opus原文要旨) | 実装箇所 | 判定 | 未充足の場合の必要差分 |
|---|---|---|---|---|
| W-01 | templateはa/anのみ(theは不可)。T5/T7文言からthe除去。templateに`assertNotIn("a/an/the")`。SSOT・委任文も「a/anのみ」に統一 | template `b1_p2_keywords_canonicalization_fulltext_prompt_template.txt` 規則5(a)「aに置換します…theは使いません」、qa(e)・reason説明もa/anのみ(grep `a/an/the`=template内0件)。test: `er003_test_kp_possessor_roles_wiring_01.py:456 test_old_rules_removed`(`"a/an/the"`をassertNotIn)・`:461 test_the_not_allowed_consistent`(`theは使いません`在+`draw the line←draw that line`拒否)。validator `er105_kp_fulltext_selector_01.py:750-775 reference_pair_ok`はa/anのみ許可。`a/an/the`が残るのはDEV `er112_kp_gm_trial_01.py:127,132,239`(Trial記録、Production非import) | ○ | なし(SSOT側: CURRENT_SPEC/DECISION_LOG/OPEN_ITEMSに KP文脈の `a/an/the` は0件をGrepで確認) |
| W-02(参考) | CMU判定は`reference_pair_ok`をer105へ。kc変更はenum+reasonゲートのみ | `reference_pair_ok`=er105:750(kcへの追加なし)、`find_inflection_window`:779が`or reference_pair_ok`。ただし(i)音素helperはer108でなくer105内`starts_with_vowel_sound`:727が`pronouncing`を直接使用、(ii)辞書に無い語・辞書例外時は**簡易規則へフォールバック**(Opus案=OOVはFalse・例外はfail-closed)、(iii)複数発音は`prons[0]`のみ(Opus案=いずれか一致で可) | △ | 2点目・3点目はOpus案との相違。実害は小(KP選定段M1/M2でCMU未登録語は除外されるため本番では辞書に載る語のみ)だが差分として記録。修正するなら(ii)(iii)を変更 |
| W-03 | 「置換しない」条件をvalidatorが決定論で却下する。(a)直前語not/all/quite/just/only・否定縮約でthat置換不可 (b)ブロック語へ時間名詞(week/month/year/weekend/evening/afternoon/season…)・same/other/very/exact/whole/only追加 (c)不可算判定を「key内のthat以降いずれかの語」へ拡張 (d)閉じた固定表現語彙リストで参照語置換を却下(me系含む) | 実装は`_DEM_FOLLOW_BLOCK`(er105:702)・`_UNCOUNTABLE`(:710、直後1語のみ判定:`reference_pair_ok`:757)。**(a)(b)(c)(d)とも未実装**(直前語の参照なし、時間名詞/same/other/veryなし、me系固定表現リストなし)。実測(`ft.is_valid_inflection_normalization(key, display)`、API 0): `not that bad→not a bad`=受理、`between you and me→between you and someone`=受理、`this year/week/weekend→a year/week/weekend`=受理、`that same day→a same day`/`that other guy→an other guy`/`that very thing→a very thing`=受理、`take that good advice→take a good advice`=受理、`excuse me→excuse someone`/`beats me→beats someone`=受理。却下されるのは`that said/like that/all that/at that point/this time`のみ(既存test `test_fixed_expressions_not_replaced`:100)。templateの規則5本文にはこれらの除外が文章で書かれている(LLM側抑止)が、validatorでは担保されない | × | Opus案(a)〜(d)を`reference_pair_ok`・ブロック語へ追加(受理範囲を狭めるだけ)。`ValidatorDev.CASES`相当の肯定ケース(draw/float/take/make that X)が維持されることを確認。固定表現否定testの追加 |
| W-04(1) | `er003_test_kp_fulltext_wiring_01.py:216-219`のenum等価assertを更新 | `er003_test_kp_fulltext_wiring_01.py`: 許可差分方式へ更新(`generalize_reference_word`のみ追加を許容、`NORMALIZATION_REASONS`不変をassert)。全回帰PASS | ○ | なし |
| W-04(2) | er112 testの是正(PROD_SRC_HASH更新、旧Production前提assert・anchor・二重enum対策、install_dev_patchesのRuntimeError)。Trial凍結、`test_no_production_module_imports_er112`をer0*系へ | `er112_kp_gm_trial_01_test_01.py`: PROD_SRC_HASH更新、`test_dev_installer_fails_closed_after_wiring`(:59、installが`drift`でRuntimeError=二重適用しない)、旧installテスト撤去、`test_gloss_prompt_a2_not_wired`。er1*全件で当該ファイルPASS。`test_no_production_module_imports_er112`はer112 test内のまま(:46)で、er0*系へは移していない | ○(一部△) | `test_no_production_module_imports_er112`がer0*既定patternに載らない点のみOpus案と相違(下記W-04(3)のer1*回帰で代替) |
| W-04(3) | 既定pattern(`er0*_test_*.py`)にer105/er108/er112 testが含まれない→配線委任で`--pattern "er1*_test_*.py"`を実行 | 委任_20のevidence_07に`er1*`実行の記録は無かった(§7は既定patternのみ)。**本委任で初めて実行**: §3 | ○(本委任で補完) | 今後の配線委任でer1*を回帰に含める(運用) |

結論: W-01○、W-04○(一部△)、W-02は△(Opus案との相違2点)、**W-03が×(validatorでの決定論却下が未実装。templateの文章指示のみ)**。未充足のため実装はせず(本委任の範囲外)、Fableへ報告する。修正は次委任。

## 3. 静止状態の全回帰
静止確認: `docs/pm/ACTIVE_TASK.md`の有料run行はすべて「終了」表記(進行中flagなし)、`stop_scope_check_01.py`(managed-id=本ID、run-dir=本研究dir)rc=0=非停止。ただし並行agentの活動は止まっておらず(`the_gift_of_the_magi/run_sf_prod_01/page_verify_public.json`が08:28:26更新、ASR/Family Yの新規commit)、「静止」は完全には成立していない。
- 既定pattern: `.venv\Scripts\python.exe run_project_regression.py`: collected=7065 passed=7050 failed=5 errors=0 skipped=10(904.6秒)。
- `--pattern "er1*_test_*.py"`: collected=477 passed=474 failed=3 errors=0(178秒)。
- 委任_20時点(evidence_07 §7)の6件→今回5件。er064のtracked変更検出(ASR er021未commit起因)は今回PASS(他agentがcommit済み)。

| # | test | 分類 | 根拠 |
|---|---|---|---|
| 1 | er019_family_x_fx_20261016_wiring_01_test_01 AbcGoldenTests.test_fallback_used_consumers_do_not_read_kp_english_entries | 他agent起因(FAMILY-X-NEWS-2ARTICLES-E2E-02) | 許可リスト外の読取元=`er019_nws2_eval_01.py`(commit 5e627e8db、2026-10-23 12:09、記事B)。assertメッセージのreaders dictに存在。委任_20の変更ファイルに`fallback_used`読取なし。単独再実行でも再現=永続的(test許可リスト更新が必要。別担当) |
| 2 | er020_tts_retry_local_rewrite_fullseg_test_01 RegressionCorpusTest.test_recorded_candidates | 他agent起因(FAMILY-Y-VOICES-DESIGN-01) | 失敗対象=`er011_output\local_rewrite_recovery\it2\b1b\local_rewrite_recovery_full_story_part1.json`(Family Y 委任_09B commit c0bcbf55bで追加した証跡)。KP/canonicalizationと無関係。単独再実行でも再現=永続的 |
| 3-5 | er026_family_z_e2e_integration_test_01 の3件(dry_run_all_stages_zero_side_effects / legacy_dry_run_flag_maps_to_dry_run / shared_state_files_unchanged_by_mock_run) | 他agentの一時状態 | 回帰中に`er026_output/family_z_production_e2e_01`配下を並行agent(Z『賢者の贈り物』run_sf_prod_01等)が更新。**同ファイル単独再実行 42 tests OK**(rc=0) |
| 6 | (er1*) er109_xz_isolation_01_test_01 StaticIsolation 2件(importers_of_scope_module / m3_scope_entry_call_sites) | 他agent起因(ASR-TIME-NUMERAL-EQUIVALENCE-01) | 許可リスト外importer=`docs/research/ASR-TIME-NUMERAL-EQUIVALENCE-01/er109_probe_01.py`・`runtime_evidence_02.py`(git tracked、委任_20無関係)。単独再実行でも再現=永続的 |
| 7 | (er1*) er110_family_y_persona_audio_trial_01_test_01 TestProductionIsolation.test_no_production_reference | 他agent起因(FAMILY-Y-VOICES-DESIGN-01) | `er110_family_y_opinion_based_01.py`(commit 8c1f4819b、Family Y 委任_18)が`er110_family_y_persona_`を含む。単独再実行でも再現 |

自分(委任_20)起因=0。「既知3件」は本リポジトリ内で定義を特定できず**未確認**(上記分類は個別の根拠で行った)。`er003_test_bad.FixtureTests`のFAIL表示は意図的な失敗fixtureの出力(集計外)。KP関連test(er003_test_kp_*、er105/er108/er112/er064)は全件PASS。

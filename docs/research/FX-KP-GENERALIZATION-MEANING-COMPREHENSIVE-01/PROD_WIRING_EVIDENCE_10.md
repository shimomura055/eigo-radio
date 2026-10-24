# PROD_WIRING_EVIDENCE_10: 委任_35 X2p'(本文での語義を確定してから訳す方式)XYZ共通 Production Wiring のruntime evidence

2026-10-24。管理ID FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_35。委任文が指定した `PROD_WIRING_EVIDENCE_09.md` は委任_27(A-1是正)の記録として既に存在し上書きできないため、本書は **`_10`** とした。設計正本=`WIRING_DESIGN_07.md`、整合確認=`CP_CHECK_35.md`、品質=`QUALITY_CHECK_35.md`、生データ=`WIRING_35/`。

## 1. 最終Status
| Family | Status | 根拠 |
|---|---|---|
| X | **WIRED_PENDING_FABLE**(`PRODUCTION_WIRED`はFable受入後) | 正式入口でX2p'が発火(記事B Std/Adv、`meaning_stage=applied`)。retry/fallback/regeneration/resume整合・test・全回帰0/0 |
| Z | **WIRED_PENDING_FABLE** | 正式KP段 `er026 --stage kp`(`run_kpgm35_01`)でa2/b1b とも `applied`。Z repairは新経路0回 |
| Y | **COMMON_IMPLEMENTED_NOT_PRODUCTION_WIRED**(`PRODUCTION_WIRED`ではない) | Y正式Production入口が存在しない(`production_reachable=False`、OPEN-484)。共通moduleは `er110_family_y_*` Trial scaffold(`sc.run_key_phrases(kp_backend="fulltext_p2")`)から到達するのでコード上は効くが、Trial専用経路。必要対応=Y正式Production入口の新設(OPEN-463/484)。Y全体のProduction構築は本委任で開始していない |

## 2. 実装(単一commit `d8fb8f9a4`、Production挙動変更を含む。撤退=`git revert d8fb8f9a4`)
- 変更は `er003_key_words_gloss_alignment.py`(X/Z/Y共有module)に閉じる。**新規flagなし**(単一flag読取関数 `EIGO_KP_GLOSS_ALIGNMENT` は従来どおり。OFFは「gloss生成の全停止=本番停止」で撤退手段ではない=WC-09 docstringに明記)。
- 追加: `NewGenMessage(str)`(方式P'、Promptにマーカーなし)、`NEWGEN_DEVELOPER_MESSAGE`・`NEWGEN_JSON_SCHEMA`(旧schema+`meaning_in_text_en`/`naive_ja`/`naive_ja_conveys`、欄順=Trial_06と同一)、`NEWGEN_*_TEXT`(Trial_06の `build_x_message06` と文面byte一致)、`build_user_message_newgen_meaning`、`validate_item_corrected(newgen=)`(新3欄 欠落/enum外=INVALID、持ち込み検出[`detect_import_flags`]・`gloss==naive_ja`・conveysは**記録のみ**)、`run_alignment_gate_corrected` の混在batch 2 call分割、`apply_alignment_corrected`/`align_glosses` の記録(`meaning_stage`・`n_newgen_calls`・`n_legacy_calls`・schema/developer sha・repair時 `n_repaired/n_realigned/n_already_consistent`)。
- 不変: `DEVELOPER_MESSAGE`・`GLOSS_ALIGNMENT_JSON_SCHEMA`・`NEW_GENERATION_TEXT`・`PERSON_CONSTRAINT_TEXT` のsha256(WC-01で固定)、`build_user_message_corrected`(source hash `32b12d9ceb965306` 不変)。**Productionは `er112` をimportしない**(golden fixtureはDEV出力をtest側にcommit: `WIRING_35/golden_dev_x06_messages_01.json`、生成script `make_golden_dev_x06_01.py`)。
- 後続工程: 新3欄はTTS・表示・validatorへ出さない(記録のみ)。TTS用 `japanese_gloss_tts` は従来の `convert_display_gloss_to_tts_text`。Validator(括弧・算用数字・…・音声化禁止記号・qa・人称整合・mapping)は新経路でも同一(WC-07)。
- 追随更新(旧実態を期待値にしていたtest): `er003_test_kp_fulltext_wiring_01.py` のfake gloss応答(新経路のschema契約=新3欄を返す形)、`er112_kp_gm_trial_01_test_01.py`(drift guard hash 2件)、`er112_kp_gm_trial_06_test_01.py`(B0pの「Production path」が新規生成経路になった新実態をassert)。既存gloss alignment test 4本は無変更で全PASS。

## 3. test
- 新規 `er003_test_kp_gloss_meaning_stage_01.py` **24件PASS**: WC-01(不変性sha・legacy-onlyでbyte一致/attempt記録形不変)、WC-02(新規生成選択・欄順・Production必須欄)、WC-03(旧句なし・範囲の規則/定訳・rules_fulltext・マーカーなし)、WC-04(混在=2 call、legacy側=現行builderとbyte一致、上限2不変)、WC-05(A/B/C形で新経路0)、WC-06(prior再掲・上限2・unresolved→HR・暗黙フォールバックなし・技術失敗もattempt消費)、WC-07(新欄欠落/enum外=INVALID、**型喪失=旧schemaで呼ばれてもINVALID→HR**、持ち込み検出はrecord-only、既存検査同一)、WC-08(Z repair=新経路0・repair件数メタデータ)、WC-09(flag OFF=DISABLED・API 0・fail-closed)、WC-10(`make_alignment_fn`: 素のstr/呼出側明示は現行)、WC-11(er112 import無し)、WC-12(DEV `build_x_message06` とbyte一致4ケース+schema+developer)、WC-13(正式入口 `sc.run_key_phrase_canonicalization` 経由で新規生成経路・永続化artifactに記録、Yが共通moduleを呼ぶこと)。
- 既存gloss alignment test 4本(`er003_test_key_words_gloss_alignment`/`..._kp_gloss_alignment_wiring`/`..._stop_paths`/`..._kp_gloss_person_alignment`)無変更で **125 PASS**(golden request bytes含む)。
- 全回帰(commit d8fb8f9a4 + 記事B成果物commit 後、`run_project_regression.py`既定pattern、`WIRING_35/regression_summary_35b.json`・`regression_35b.log`): **collected=7156 passed=7146 failed=0 errors=0 skipped=10**。
- `--pattern "er1*_test_*.py"`(`regression_er1_summary_35b.json`): collected=491 passed=487 failed=4(自分起因0): `er112_kp_gm_trial_06_test_01.T06.test_default_off_isolation_no_api_no_files`(Trial_06自身の費用台帳`LEDGER6`が存在しtotal>0。本件のコードに無関係で、Trial_06実行後に生じた既存状態)、`er109_wiring_golden_test_01.GoldenSignatures` 3件(ASR系 rejudge/adapter署名。当該testはKP gloss moduleをimportしない[importグラフ確認]、他agent=ASR-OOV系のcommit起因)。配線前の自分起因の失敗(trial_01 hash 2件・trial_06 B0p 1件・fulltext wiring 3件・outer_retry 2件・er064 tracked-py 1件・trial_03 production-edit 1件)は更新/commit後に解消。
- pytest形式群(er078/103/104/105/106/108/109): `regression_pytest_group_35.log`(§9参照)。
- **revert予行**: `git revert --no-commit d8fb8f9a4` → 既存gloss alignment 4本+fulltext wiring+outer_retry+不変性sha(4定数)=**197 passed**(旧状態=byte-identical) → `git revert --abort` で復帰(`git diff HEAD`空、NewGenMessage復帰を確認)。

## 4. runtime evidence(正式経路)
共通: STOP確認 rc=0(`stop_check_35*.json`)、flag `[GLOSS-ALIGN] 実効flag=ON (source=default)`、**actual model_id=`gpt-6-luna`**(`response.model`一致検査通過、routing: process `A2_SUPPORT`/`B1_SUPPORT`→`routing.SUPPORT_MODEL`、最新世代の推奨系)、reasoning effort=high(既定)、Version=`ER-003-KP-GLOSS-ALIGN-02`、`rules_sha256`(rules_fulltext)=`fa5ae89c…`(不変=G-9)、schema sha256=`40b0ef68…`、developer sha256=`3b1001fc…`。

### 4-1. X(記事B `uk_train_speaker_playback`、run `er019_output/family_x_audio_production_wiring_01/uk_train_speaker_playback__run_nws_02`)
- 入口: `WIRING_35/x_rerun_kp_35.py` が選定段の出力(original_items)を既存artifactから`er105.build_original_items`同形に**再構成**(選定LLMは再実行しない=KPの選び直しなし)し、正式入口 `sc.run_key_phrase_canonicalization(article_text, original_items, kp_dir, article_id, process)`(canonicalization[A-1/②hook込み]→merge→`gloss_align.align_glosses`[X2p']、`run_theme_scaffold`と同じprocess/article_id)を呼び、続けて `sc.run_key_phrase_redundancy_qa`。本文sha(`audit/scaffold_article_sha256.json`)一致を事前確認。旧artifactは`WIRING_35/x_backup/`へ退避。
- 結果: a2/b1b とも `CANONICALIZATION_PASS`・`ALIGN_PASS`(attempt 1、retry 0)・`REDUNDANCY_PASS`、全KP `meaning_stage=applied`・`n_newgen_calls=1`・`n_legacy_calls=0`・`n_import_flags=0`。入力本文⇔出力の対応は `QUALITY_CHECK_35.md` §1。KP変更=KP3のみ `draw that line → draw a line`(A-1。両level)。gloss=Std #1「誰も望んでいない音」・#3「一線を引く」、Adv #2「お金を払おうとする」・#3「境目をはっきりさせる」(その他は不変)。
- Prompt: `gloss_alignment_prompt.txt` sha256(先頭16)=Std `914c77ae54190d38`(11,228B)/Adv `df607f88581d3cab`(11,320B)。マーカー無し・旧句(「他の文脈でも再利用できる」)無し。
- 所要: canonicalization+gloss 合計 Std 57.6秒/Adv 71.5秒。gloss call単体 Std 39.6秒(出力3,261token・reasoning 2,890)/Adv 59.2秒(5,181・4,799)。
- 音声(最小更新): 変更KPのclipだけ再生成 — Std: `kp3_en`・`meaning_1`・`meaning_3`、Adv: `kp3_en`+KP1〜3解説(解説textは5件バッチ生成のため全件再生成=既存仕様 `_resolve_kp_explanations_text`)。**他の全segment(本文・Preview・Comment・In One Line・共有narration)は再利用**(`reused_from_previous_run=True`、ASR判定継承)。試聴ページのmp3は変更KPの行(Std 2行・Adv 3行)と通し音声2本のみが更新、他44行はbyte同一(`git diff --stat`)。HR Lock・STOP・approve_regenerate: 発生0。
- assemble: Std 307.05秒(旧306.68)/Adv 280.84秒(旧279.82)。ページ更新→公開(commit `705b9316b` push)→公開URL page_verify(Playwright実再生 47/47、seek OK、console error 0、HTTP≥400 0、長さ一致)**PASS**(`page_verify_public_35.json`)、標準ページ検査 PASS(`page_check_public_35.json`)。

### 4-2. Z(『猿の手』、公開物に触れないコピーrun `er026_output/family_z_production_e2e_01/the_monkeys_paw/run_kpgm35_01`)
- 入口: 公開版 `run_sf_prod_01` の writer/support/plan 等をコピーし、`er026_family_z_fiction_production_runner_01.py --story the_monkeys_paw --run run_kpgm35_01 --stage kp --mode real --approved-budget-jpy 10`(正式KP段: 選定→canonicalization→gloss=null から新経路)。初回起動は予算見積guard(`approved 6`で`spent+est>limit`)により**API 0でrc=2停止**(原因=承認予算値の過小設定、guardは迂回せず`--approved-budget-jpy 10`で再実行。有料runの再起動ではない)。
- 結果: a2/b1b とも `applied`・`ALIGN_PASS`(attempt 1)。gloss: Std 曹長/沈黙を破る/夜の闇へ高く響いていく、Adv 運命に手を加える/機械に巻き込まれた/失った悲しみの叫び。公開版との差・本文での語義は `QUALITY_CHECK_35.md` §2(同一KP 5件の比較で意味の悪化0)。
- 所要: gloss call a2 28.3秒/b1b 44.3秒(旧経路 12.6/7.1秒)。公開物 `run_sf_prod_01` は不変。
- **Z repair**: 現行builderのまま(新経路0回)。実Z artifact+fake LLMで確認(API 0、`WIRING_35/z_repair_and_mixed_check_35.py`): `only_ranks=[1]`(current gloss有・人称不整合)→ `n_newgen_calls=0`・`stage=legacy`・`n_repaired=1`。WC-08も同内容。

### 4-3. 共通(正式module経由・fake client、API 0)
- 混在batch(gloss有の人称不整合item + gloss=nullの全文選定item 2件)→ **2 call**(newgen=`NewGenMessage`、legacy=従来str)、`meaning_stage=mixed_split_newgen`、`attempt_paths=[newgen_meaning_v1, legacy]`(`z_repair_and_mixed_check_35.json`、WC-04)。
- 型喪失(`msg + ""` で素のstr化)→ 旧schema応答=新3欄欠落→`meaning_stage_fields_invalid`→retry 1回(上限2)→unresolved→`FAILED_HUMAN_REVIEW_REQUIRED`(安全停止。WC-07)。
- A/B/C形(`fulltext_source_ref`なし)入力で新経路0(WC-05)。
- Y: 共通module経由の到達性は `sc.run_key_phrases(kp_backend="fulltext_p2")`(`er110_family_y_text_trial_01_run.py:264`・`er110_family_y_persona_text_trial_01_run.py:281`)をWC-13がsource検査で固定。音声Trialは`"production_reachable": False`。

## 5. retry/fallback/regeneration/resume整合(ユーザー§3-2)
- attempt上限2(`MAX_GLOSS_ALIGNMENT_ATTEMPTS`)不変、混在attemptは「attempt番号共有・最大2 call」で2回を超えない(WC-04)。priorは項目単位で再掲(WC-06)。unresolved→HR(`GLOSS_ALIGNMENT_HUMAN_REVIEW_REQUIRED`、KP・旧gloss維持)。新経路失敗が旧builderへ暗黙フォールバックする経路なし(WC-06)。
- 初回/外側retry/fallback/regeneration/resumeはいずれも `run_key_phrase_canonicalization`→`align_glosses` 1箇所を通る(`er003_test_kp_possessor_roles_wiring_01::test_xz_share_single_canonicalization_path`)。resume時にglossが既にあるitemは自動的にlegacy側(従来出力と同一)。

## 6. 実測単価(KP単位・記事セット換算)
gloss段のみ(canonicalization・redundancy QA・解説・TTSを除く)。同一モデル・同一reasoning effort。
| | 旧経路(配線前の同記事) | X2p'(本委任) | 増分 |
|---|---|---|---|
| X 記事B(Std 3KP+Adv 3KP=1記事セット) | 0.1996円(Std 0.1011+Adv 0.0985) | 0.7731円(Std 0.3097+Adv 0.4634) | **+0.574円** |
| Z 猿の手(a2+b1b) | 0.2181円 | 0.6421円(a2 0.2563+b1b 0.3858) | **+0.424円** |
- KP単位: X 0.0335円→0.1288円(+0.095)、Z 0.0364円→0.1070円(+0.071)。Trial_06の 0.0266→0.0704円/KP(+0.0438、10KP/セット換算+0.438円)とは1callあたりKP数が違う(本番は1 level最大3KP/call、Trialは約5KP/group)ため固定オーバーヘッド分の比較不能。**記事セット換算の絶対増分は +0.42〜0.57円(70円の0.6〜0.8%)で、Trial_06の水準(+0.44円)・Opus試算(+0.5円)の範囲内**。不要な増加の原因(重複call・余計な再試行)は無い(各levelの新規生成は1 call・attempt 1で通過)。
- 本委任の実費合計 **約4.40円**(X KP段 1.33[canonicalization 0.42+gloss 0.77+redundancy 0.14]、X TTS/ASR/NER/解説text 0.62、Z KP段 2.45)。上限25円内。内訳=`cost_summary_35.json`。

## 7. 監視指標の新基準案(提案のみ。CURRENT_SPEC §2793の基準は未変更、Fable/ユーザー確認後)
- 実測(n=4 call): 記事セット当たりgloss費用 X 0.773/Z 0.642円、level当たりgloss call所要 28.3〜59.2秒。
- 案: 「align費用」= 実測最大×1.3 ≒ **1.0円/記事セット**(現行0.6円は常時発火)、「level単位align所要」= 実測最大×1.5 ≒ **90秒**(現行60秒は発火しうる)。n=4のため暫定。量産初期の実測で再計算する。新規監視(記録のみ): `meaning_stage`適用率、`n_import_flags`(今回 X 0/6、Z 1/6=`caught in the machinery`の過去分詞誤検出)、`n_legacy_calls`(混在率)、repair時のgloss変化率。

## 8. 失敗終了時の最終成果物(実例)
- gate unresolvedの場合: 従来どおり `FAILED_HUMAN_REVIEW_REQUIRED`(KP維持・旧gloss維持・HR報告書)。WC-06で`apply_alignment_corrected`の出力(`gloss_alignment_status=FAILED_HUMAN_REVIEW_REQUIRED`、`japanese_gloss=None`のまま)を固定。本委任の実runでは発生0。

## 9. pytest形式群(er078/103/104/105/106/108/109[golden除く]、`regression_pytest_group_35.log`)
**1,136件中 passed 1,130 / failed 6**(自分起因0)。失敗6件=`er103_run_entity_table_test_01`(TestInheritance 4・TestStoreGuard 1)+`er104_kp_vote_wiring_test_01::test_AST_attempt_ctx_vote_flag_is_forwarded_from_strict_only`。いずれもASR/RET/KP vote系で、`er003_key_words_gloss_alignment`をimportしない。`er104`の失敗は未追跡の `er103_ret_baseline_signature_01.py`(他agent=ASR系の新規file)が許可リスト外の読取元として検出されるため。他agent起因として列挙のみ(修正しない)。

## 10. 申し送り・逸脱
- 委任文のevidence file名 `PROD_WIRING_EVIDENCE_09.md` は委任_27で使用済み(上書き不可)のため `_10` とした。
- 実装中、gate/builder挿入用のpatch scriptが `build_user_message_corrected` 内の同一文面に誤ヒットしてProduction fileを壊した(importのSyntaxErrorで即検出、commit前)。`git show HEAD:` から復元して差分を再適用し、既存4 test+新test+全回帰で確認(commit済みの状態は正常、旧builderのsource hashは不変=§2)。
- 共有scratchpadに同名の一時script(patch1/2/3.py等)があり、同名で上書きした(一時ファイルのみ・成果物に影響なし)。
- 共有git indexに他agent(Family Z『告げ口心臓』準備)のstaged 4ファイルが存在。本委任のcommitはtemporary index(GIT_INDEX_FILE)経由で対象pathだけをcommitし、巻き込んでいない。`CURRENT_SPEC.md`の着手前からの他agent未commit差分(2026-10-23追記の1行の改行分割)・`DECISION_LOG.md`/`OPEN_ITEMS.md`の他agent未commit追記は作業ツリーに残し、commitには含めていない(HEAD blobに自分の編集だけを適用した版をcommit)。

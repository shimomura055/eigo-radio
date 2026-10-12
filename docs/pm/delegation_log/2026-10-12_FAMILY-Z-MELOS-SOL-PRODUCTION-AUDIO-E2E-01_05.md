# FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_05(2026-10-12)

範囲: er026正式経路への統合・tests/Regression・dry-run。**実呼出なし(課金JPY0)**。E2E実行は委任_06。SSOT編集なし。PRODUCTION_WIRED未達(E2E未実行)。

## 1. 統合概要
- `er026_family_z_fiction_production_runner_01.py` にE2E統合を追加(Phase 1の関数・testは残置)。stage順(`--stage <名前>` または `all`):
  `seed_check -> writer(r0->r1->r2) -> validate_b1b -> std_adjust -> validate_a2 -> plan -> support -> kp -> tts_b1b -> tts_a2 -> provision_shell -> gate -> assemble -> pages -> page_verify`
- `--mode dry-run`(既定・副作用ゼロ) / `--mode mock`(全LLM/TTS/ASR/KP fnを内蔵ダミーに固定) / `--mode real`(`--approved-budget-jpy`必須、委任_06用。本委任では未実行)。
- 04A/04B/04C moduleの内部は不変。**例外としてer063(Z所有)のみ最小拡張**(方針6のAdv KP英語解説。下記)。共有module(er003/er006/er011/er012/er013/er019/er020)、X Style定数、Seed/anchors/Trial成果物、SSOTは未編集。
- 出力run dir: `er026_output/family_z_production_e2e_01/melos/<run>/`(既定run=`run_e2e_01`)、ページ: `user_test/family_z_melos_01/`(mockは `<run>/pages_mock` に出力し公開用dirへ書かない)。
- 単一の`cost_log.jsonl`(`<run>/cost_log.jsonl`、cost_logger install)を全stage共通で集計(`compute_cost_jpy_so_far`)。各stageは新規API呼出の前にguard。

## 2. 方針1〜11の実施結果
| # | 内容 | 結果 |
|---|---|---|
| 1 | stage順・個別実行・`all`・resume | 実装。resumeはprovenance sha一致で再利用、不一致は`FamilyZProvenanceMismatchStop`(testで固定)。Validatorは入力sha(候補/anchors/Adv)一致時のみ再利用 |
| 2 | Std段落数不一致 | 不一致 -> `std_adjust`を**自動で1回だけ再生成** -> なお不一致(または再生成済みの再実行)は`FamilyZStdParagraphStop`でSTOP。`plan`段でStd境界がAdv境界の写像でない場合も独自分割に回らずSTOP(`run_plan`の独自分割コードは残置・未使用)。er062側の挙動変更なし(guardrail warningはそのまま、判定はer026側) |
| 3 | 語数Guardrail(OPEN-302) | WARNのみ・自動再生成なし。mockでAdv 364語(<400)・Std比1.18(>1.10)のWARNのまま全stage完走することをtestで固定 |
| 4 | 話者判定 | 04B方式(決定論None->LLM採用`llm_only`、値の食い違いのみSTOP)。`other`は`FamilyZDialogueOtherStop`。補助フィールド(`is_recollection`等)なし。E2E後の人間確認用に全引用の`speaker_table.md`を`plan`段で生成(mock 18引用:agree 7/llm_only 11) |
| 5 | Melos Voice | `Algieba`(PROVISIONAL_UNAPPROVED)のまま。`seed_check`出力に`melos_voice_status`を常時表示。narrator=Aoede/selinuntius=Erinome/dionysius=Charon。**ユーザー承認候補** |
| 6 | KP第3segment | 下記3節 |
| 7 | ASR「Melos」誤認識 | 下記4節 |
| 8 | 予算 | `E2EBudget`: `--approved-budget-jpy`(real必須、300超は拒否)・警告閾値200円。guardは「累計+次の見積 > limit」で新規API呼出前にSTOP(limit=200、`--ack-warn-threshold`明示時のみ300)。TTSはclip単位guard(STOP時は監査記録を保存してからSTOP)。未承認のrealは実client/ログ/ディレクトリ作成前にSTOP(testで固定) |
| 9 | 旧名前検査 | `run_text_stage`を`resolve_canonical_text_v2`(er061第1層)へ置換。`check_character_name_rule`/`restore_character_names`はSUPERSEDED注記で残置。known_gap testを新仕様(er020 Family Z clip pattern=RESOLVED、stub廃止)へ更新 |
| 10 | KP資産 | `<run>/key_phrases/<level>/keywords_canonicalized.json` -> `<run>/<level>/key_phrases/keywords_canonicalized.json` へcopy(`install_kp_assets`、無ければSTOP) |
| 11 | 出力先 | 上記1節のとおり |

補足の統合判断: (a) Std日本語タイトルTTSは `STORY_REGISTRY["melos"]["japanese_title_tts"]="走れメロス"`(括弧付き英題を日本語TTSに読ませない。表示用`japanese_title_text`は不変)。(b) Local Rewrite後の再検証は`revalidate_after_local_rewrite`の**第1層FAIL/PASS->FAILのみSTOP**、WARNは非ブロック(原稿自体がWARNだと全LR clipがSTOPするため)。(c) `--tts-execution-mode`既定=STANDARD(04C smokeと同じ。BATCH指定可)。(d) real時 `cl.install` は `build_real_context` 内で予算検証後に1回のみ。

## 3. 方針6: KP第3segmentの照合結果
- Coffee最終v3 Advanced(`er057_output/coffee_final_audio_assembly_01/assembly_manifest_v3_01.json`、`STYLE_APPLICATION_EVIDENCE_V3_01.md`)は **`kp{n}_en`(K2) + `kp{n}_explanation_en`(英語解説、既存承認Style=P=`KEY_PHRASE_EXPLANATION_EN`)** を使用(Stdは`kp{n}_ja`=M2)。timelineは `Key Phrase 1..5`(番号->英語->第3segment->英語再掲)。
- よって **Z Advも英語解説に変更**(ZのAdvが日本語意味だった04C実装を訂正)。実装: er063に `kind=kp_expl_en`・clip `kp{n}_explanation_en`・role style `KP_EXPL_EN`(X定数の逐語コピー、一致をtest)・`build_level_plan(kp_explanations=...)`・entry/Gate/page行の`explanation`サブキー対応・assemblyの`kp_third="explanation"`。`FAMILY_Z_ROLE_STYLE_VERSION`を`z_v2_..._kpx_...`へ更新。既存のX `generate_key_phrase_explanation_en_verified`/`generate_kp_explanations`(語数15以内・新Fact混入QA、NGはTTSへ渡さずSTOP)を読み取り利用。
- Stdは日本語意味(M2)のまま。Std/Advは本文が別なので KPは別々に選定(`kp_a2`/`kp_b1b`)。

## 4. 方針7: ASR「Melos」誤認識の読み取り確認結果
- **Secondary cascadeはLocal Rewriteより先に走る**: 全narrator/dialogue経路(Adv narrator=`news_tail_fix.generate_news_narration_wide_margin`、Std narrator=`repro01.generate_narration_snippet_verified_strict`+`crosslevel._run_a2_minimal_fallback_attempt`、dialogue=`er012.generate_voice_body_wide_margin`)が毎attemptで`secondary_asr.evaluate_attempt_with_cascade(cascade_enabled=FEATURE_FLAG_SECONDARY_ASR_ENABLED=True)`を呼ぶ。Primary UNCERTAIN(entity-like)ならPrimary#2->Azure(Phrase List)x2をその場で実行し、LR(`_local_rewrite_recovery_*`)は`stop_retrying`または試行枠尽きの後。04C smokeのcost_logも `openai_asr, azure, openai_asr, azure, azure -> perplexity, openai(luna)x2` の順(cascade後にLR)。
- **固有名詞リストは引数・設定では渡せない**: Phrase Listは各関数内で `pronun_ledger.get_hint_for_text(text, min_confidence="low")` の`canonical_spelling`から自動導出(引数なし)。したがってer026/er063側から渡す余地はなく、**変更なし**(共有module変更禁止)。
- 現状のLedger(HEAD): `melos`/`selinuntius`/`dionysius`は`ja_reading_katakana`・confidence high・canonical小文字で**登録済み**(=本文にそれらを含むclipでは既にPhrase Listに入る。それでもsmokeでMelos->"mellows"はcascadeで救われずLRが発火)。`Syracuse`は未登録。作業ツリーの`ledger.json`にはsmoke由来の未commit追記(`cascade_unresolved_entity` melos・low)があるが本委任は触れていない。
- 方針: E2Eで発生するLR回数/cool-down/費用を`audio_text_deviation`・`cooldown_occurred`・cost_logに記録する(M6)。**「Pronunciation Ledger登録(Syracuse等)は別承認」**。

## 5. テスト・検証(実測、すべて課金0)
- 新規 `er026_family_z_e2e_integration_test_01.py` **42件PASS**(page_verify実Playwright含む。約130秒。`ER026_SKIP_PAGE_VERIFY=1`で1件省略可)。更新 `er026_family_z_fiction_production_runner_01_test.py` **20件PASS**(known_gap新仕様・stub廃止・superseded・er061置換のtest)。
- 内訳: stage順固定/`all`順序/エラー停止、mock全stage通し(seed_check->...->pages)+page_verify `--local`、dry-run副作用ゼロ(監視9ファイルsha・dir snapshot不変、`os.makedirs`をpatchしてもdry-runが通る)、real未承認/300超でclient・dir作成前にSTOP、STOP条件(validator FAIL/NEEDS_REVIEW、Std同一本文、Std段落不一致2回+再実行でLLM追加0回、一致回復、話者不一致+`dialogue_override.json`、`other`、budget(新規API呼出前/TTS途中で監査保存後STOP)、TTS clip失敗)、resume(再実行でLLM/judge追加call 0・TTS再利用)、provenance sha不一致STOP、LR再検証wrapper(PASS/FAIL)、KP資産copy、er063 KP英語解説拡張。
- mock時は `get_client` 3種・`run_support_text` 2種・`run_key_phrases`・`cl.install`・`real_generators` を `AssertionError` にpatchして実API混入を阻止(04B事故再発防止)。mock時のみ `er011.ATTEMPT_HISTORY_PATH` をrun配下へ退避(共有履歴を汚さない)。
- Regression(新規failure 0): er026(2)+er060+er061+er062+er063 = 225件OK(1 skip) / er020 86件OK / er013 323件OK / er019 284件OK / er011 295件(failures=3) / er003 1557件(failures=3, errors=1)。**失敗はいずれも本変更と無関係**: er011 `test_default*_matches_pre_wiring_baseline`3件(別タスクのPrompt本文変更による既存のbyte parity不一致)、er003 `er003_test_p2j_investigate`の件数算術系・`er003_test_bad`(意図的に失敗する検証用fixture)。これらはer026/er063/er062/er061をimportしない(sys.modulesで確認)。
- 回帰test実行中に共有履歴へ追記された `er011_output/attempt_history.jsonl` の自分の行(archive_prior_tts_results由来、tmpパス)は除去して実行前の状態(12274行)へ復元済み。`er020_output/*/_test_scratch/attempt_log.jsonl`(未追跡のtest scratch)は回帰testが追記する既存挙動のまま。

## 6. dry-run / mock 通し結果
- dry-run: `er026_output/family_z_production_e2e_01/melos/integration_evidence_05/dry_run_all_stdout.json`(15 stage計画+preflight: seed凍結sha・anchors・routing 7key・Style表sha・Melos Voice暫定)。実行前後で Master Store / reuse_telemetry / human_review_queue / ledger / attempt_history / 各telemetry / er011 local_rewrite dir / er026 output dir / `user_test/family_z_melos_01` がすべて不変(snapshot一致)。
- mock通し(CLI `--mode mock --stage all --run integ05`、15 stage完走、実費0): `.../integration_evidence_05/mock_all_stages/`(stage log・provenance・validator summary・timeline・gate結果・speaker_table・page_verify_local.json)。mock run本体(約156MB)は削除済み。Playwright: standard/advanced各 全audio再生OK・console error 0・(a)〜(n)確認。通し音声のseek=falseは`http.server`のRange非対応による既知の偽陰性(GitHub Pagesでは対応)。

## 7. E2E実行コマンド(委任_06がそのまま使える形)
```
cd C:\Users\tensh\eigo-radio
# 事前確認(副作用なし)
.venv\Scripts\python.exe er026_family_z_fiction_production_runner_01.py --mode dry-run --stage all
# 本番E2E(全stage。STOPしたらその場で停止、自動再生成なし)
.venv\Scripts\python.exe er026_family_z_fiction_production_runner_01.py --mode real --stage all --run run_e2e_01 --approved-budget-jpy 300
# 段階実行(推奨: 文章系で人間確認してからTTSへ)
.venv\Scripts\python.exe er026_family_z_fiction_production_runner_01.py --mode real --stage all --stop-after kp --run run_e2e_01 --approved-budget-jpy 300
.venv\Scripts\python.exe er026_family_z_fiction_production_runner_01.py --mode real --stage tts_b1b --run run_e2e_01 --approved-budget-jpy 300
.venv\Scripts\python.exe er026_family_z_fiction_production_runner_01.py --mode real --stage tts_a2  --run run_e2e_01 --approved-budget-jpy 300   # tts_b1bと別プロセスで並列可(同一cost_logへ追記)
.venv\Scripts\python.exe er026_family_z_fiction_production_runner_01.py --mode real --stage provision_shell --run run_e2e_01 --approved-budget-jpy 300
#   以降 gate / assemble / pages / page_verify も同形式(--stage 名)
# 一部clipのみ再実行: --stage tts_b1b --only-clips full_story_part1_c3,kp2_en
# 明示再生成: --regenerate-stage {r0,r1,r2,std_adjust,plan_b1b,plan_a2,support_b1b,support_a2,kp_b1b,kp_a2,kp_expl_b1b}(子孫はstale化、自動再生成しない)
# 警告閾値(200円)到達でSTOPした場合のみ、ユーザー/Fable確認の上 --ack-warn-threshold を追加(上限300まで)
```
STOP時は終了コード2・`[STOP] <例外名>: <理由>`をstderrへ。証跡: `<run>/e2e_stage_log.jsonl`・`<run>/cost_log.jsonl`・`<run>/speaker_table.md`・各`audit/`。公開URL版Playwright((m))と実機試聴はE2E委任側で別途(`er063_family_z_page_verify_01.py --base <公開URL>`)。

## 8. 想定費用内訳(上限300、警告200。実測単価は04A/04B/04C smoke、設計値は設計書v01の保守値)
| 区分 | 低(実測単価ベース) | 高(設計保守値) |
|---|---|---|
| LLM text: Writer R0-R2(Sol high) + Std調整(+自動再生成時は+3〜6) + plan(分割/話者) + support(Luna 8call) + KP選定x2 + Adv解説 | 約24 | 約96 |
| Validator(Luna、PASS時¥0.2〜0.3/level、FAIL/再判定で¥0.5〜0.7/level) | 約0.5 | 約3 |
| TTS+ASR(約100 clip: Adv約49+Std約50。実測 ¥0.25〜0.5/clip、設計 ¥0.86/clip) | 約25〜50 | 約85 |
| **LR仮定A: 発生率5%(narrator約35 clipで約2回、¥1.2/回、cool-down最大20分)** | +2 | +3 |
| **LR仮定B: 発生率30%(約10回、¥12〜15、cool-down最大100分、Human Review到達の可能性大)** | +12 | +15 |
| 合計 A | 約52〜77 | 約187 |
| 合計 B | 約62〜90 | 約202(警告200到達の可能性あり) |
- 所要(見込み): Writer鎖約15分、Std約5分、Validator/plan/support/KP約20分、TTS(STANDARD同期)約50〜100分/level(2プロセス並列可)+cool-down(LR 1回につき最大10分)、assembly/pages/Playwright約5分。
- Perplexity(LR時のpronunciation research)は`compute_cost_jpy_so_far`の対象providerに含まれず0円計上(実額は小さい)。

## 9. 残リスク・判断依頼
1. **Melos Voice=Algieba(暫定・未承認)**: 最終報告でユーザー承認候補。Dialogue clipは共有関数がgemini-2.5-pro-preview-tts固定のためnarrator(flash-lite)と声質が異なりうる(04C残リスクA、共有module変更は別委任)。
2. **ASR "Melos"->"mellows"**: LR/cool-down/費用が上記仮定Bに寄る可能性。Syracuse等のLedger登録は別承認。
3. Adv KP英語解説はX既存承認の経路・Styleを使うが、Zでの聴感は未確認(E2E後の試聴)。Adv KPのBlock構成はFamily Cの`build_key_phrase_block`(番号->英語->第3segment->英語再掲)で、X B1と同形。
4. 実LLMでのPreview/Comment(news文言の打消し+lint)、Writer鎖、Std調整、話者判定、Adv解説は**未実呼出**(E2E初)。語数Guardrail(OPEN-302)は未承認のためWARN。
5. `q26_1 "I will wait."`型の回想・独白はLLM判定のまま(補助フィールドなし)。`speaker_table.md`で人間確認。
6. `dialogue_override`/Human Review/LR再検証がSTOPした場合は自動で通さない。Family C B1 assembly初実行(OPEN-305)の実音声peak/headroomはE2Eで確認。
7. 公開URL版Playwright((m))とGitHub Pages公開は未実施。

## 10. 変更ファイル
`er026_family_z_fiction_production_runner_01.py`(統合)、`er026_family_z_fiction_production_runner_01_test.py`(更新)、`er026_family_z_e2e_integration_test_01.py`(新規)、`er063_family_z_audio_01.py`(Adv KP英語解説の最小拡張)、`er026_output/family_z_production_e2e_01/melos/integration_evidence_05/`(証跡)、本ファイル、`docs/pm/RESULT_PACKET.md`、`docs/pm/ACTIVE_TASK.md`。

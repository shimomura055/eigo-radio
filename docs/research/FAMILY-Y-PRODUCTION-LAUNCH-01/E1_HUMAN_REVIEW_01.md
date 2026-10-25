# E1_HUMAN_REVIEW_01: E-1(宅配 redelivery_fee run_01)Human Review 3 segment の試聴・承認後手順 (委任_07、2026-10-25)

**本書は手順書。承認コマンドは実行していない(`approved_by="user"`はユーザー本人の承認発言があった場合のみ。AI/Fableは付けない)。** API費用は本委任で0円。

## 1. 試聴パッケージ(承認前・限定共有)
- 一式: `user_test/family_y_production_redelivery_fee_01/listening/`(`index.html`+mp3 3本)。生成: `.venv\Scripts\python.exe er121_e1_hr_listening_page_01.py`(API 0。wav→mp3は公開mp3と同じ`libmp3lame 96k`、wavはgit管理外)。
- raw URL(push後): `https://raw.githubusercontent.com/shimomura055/eigo-radio/main/user_test/family_y_production_redelivery_fee_01/listening/index.html`(公開ページURLは`https://shimomura055.github.io/eigo-radio/user_test/family_y_production_redelivery_fee_01/listening/index.html`)。冒頭にPAGE_NOTICE_JA(`er121_family_y_structure_01.PAGE_NOTICE_JA`同文)を掲載、`y_page_notice_check_01.py`=rc0、noindex。各segmentに「ユーザー承認待ち」を明記。
- 試聴対象は**書換え前(R0本文)の最終判定対象attempt**。ER-020 Local Rewrite後の書換え音声(`redeliveries`→`repeat deliveries`)は含めない。

| # | segment | 試聴attempt(wav sha256先頭12) | 自動判定 | NG理由(耳で確認する点) |
|---|---|---|---|---|
| 1 | a2 `preview`(日本語) | attempt5 `preview_attempt5_customb8f0ff16.wav`(698609923120…) | `ASR_VALIDATION_UNCERTAIN`(6 attempt全て同じ) | 正本「思いどおりに」をASR(OpenAI・Azure両方)が「思い通りに」と転写=表記差。「おもいどおり」と聞こえれば音声は正しい |
| 2 | b1b `y_voice_1`(英語) | attempt6 `y_voice_1_attempt6_englishstyleprefixwidemargin.wav`(821f2c180ec0…)。ASR一致(`NORMALIZED_MATCH`、`re-deliveries`のハイフン差のみ) | Repetition QA 短ラグ検査(D')のみflag | 約31.2秒付近で似た音が0.60秒続き閾値0.6秒の境界。不自然な反復・つっかえが聞こえるか |
| 3 | a2 `y_voice_1`(英語) | attempt5 `y_voice_1_attempt5_custom53fd514d.wav`(3a5736fc9a53…)に採用時必須の6%減速を適用した音(`a2_y_voice_1_slowed6pct.mp3`、46.5秒) | ASRは`NORMALIZED_MATCH`、D'のみflag(0.62秒、約30.6秒付近) | 同上。減速後の音を聴いて判断 |

b1bの別候補(同じR0本文): attempt5(`EXACT_MATCH`・D'0.61秒)。a2 `y_voice_1`の別候補: なし(attempt4は0.74秒、attempt2/6は`was→is`等の読み違い=採用不可)。必要なら別候補のmp3を追加で作る(API 0)。

## 2. 承認後の手順(承認コマンド。Fable/Sonnetが、ユーザーの承認発言を受けてから実行)
前提: ユーザーの承認発言を**逐語**で `docs/pm/delegation_log/<日付>_FAMILY-Y-PRODUCTION-LAUNCH-01_USER_E1_APPROVAL.md` に保存する(対象を`a2 preview` / `b1b y_voice_1` / `a2 y_voice_1`の識別子で冒頭に列挙)。採用スクリプトは、このファイルが存在し対象の`level`と`segment`の語を含む場合だけ書込む(それ以外はrc=2で何も書かない)。AIはこのファイルを「ユーザーの発言なしに作らない」。

```
# 0. STOP確認(rc=3なら停止)
.venv\Scripts\python.exe tools\stop_scope_check_01.py --managed-id FAMILY-Y-PRODUCTION-LAUNCH-01 --run-dir er121_output\family_y_production_01\redelivery_fee\run_01 --out er121_output\family_y_production_01\redelivery_fee\run_01\stop_check_e1_adopt.json

# 1. 承認されたsegmentごとに(dry-runは --apply を外す。既定=何も書かない)
.venv\Scripts\python.exe er121_e1_hr_adopt_r0_01.py --level a2  --segment preview   --user-statement-ref docs\pm\delegation_log\<日付>_FAMILY-Y-PRODUCTION-LAUNCH-01_USER_E1_APPROVAL.md --apply
.venv\Scripts\python.exe er121_e1_hr_adopt_r0_01.py --level b1b --segment y_voice_1 --user-statement-ref docs\pm\delegation_log\<日付>_FAMILY-Y-PRODUCTION-LAUNCH-01_USER_E1_APPROVAL.md --apply
.venv\Scripts\python.exe er121_e1_hr_adopt_r0_01.py --level a2  --segment y_voice_1 --user-statement-ref docs\pm\delegation_log\<日付>_FAMILY-Y-PRODUCTION-LAUNCH-01_USER_E1_APPROVAL.md --apply

# 2. 組立→ページ→検証(API 0)。段は1起動で(OPEN-480: 分割起動はRESTART_STORMを自行発動する)
.venv\Scripts\python.exe er121_family_y_runner_01.py --mode real --slug redelivery_fee --run run_01 --theme-package docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_02/THEME_DATA_02.json --reuse-manifest docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/theme_packages/redelivery_fee_reuse_01.json --approved-budget-jpy 170 --stages gate,assemble,pages,page_verify

# 3. 限定公開(API 0): <run>/pages/{index.html,audio/} を user_test/family_y_production_redelivery_fee_01/ へ配置(listening/はそのまま)
py -I tools\user_test_page_standard_check_01.py --page user_test\family_y_production_redelivery_fee_01\index.html
py -I tools\y_page_notice_check_01.py --page user_test\family_y_production_redelivery_fee_01\index.html
# 両方rc=0を確認後、対象pathのみ git add → commit → git push origin HEAD:main
```
- 採用スクリプトがやること(既存機構の適用。新Gate・flag・迂回なし。先例: `er019_fx_moon_title_individual_approval_01.py`、`er011_discovery_generalization_towels_trial_11_audio_03_b1b_individual_approval_and_assemble_01.py`): ①R0のattempt wavを`narration/<segment>.wav`へ配置(置換前の書換え版/最終fallback版は`<segment>.pre_ypl7_adopt.wav`で保全。a2 `y_voice_1`は`_original.wav`へR0を置き**ffmpeg atempoで6%減速**=API 0) ②既存`er003_v1_n3_01_assemble.record_human_approval(<level dir>, <segment>, <entry.canonical_text>, approved_by="user")` ③`review_lock_state.json`を`RESOLVED/HUMAN_APPROVED`へ(旧stateは`prior_state`に残す) ④`tts_generation_results.json`のentryにnote・採用wav sha・R0 textを記録(ASR/QAのNG記録=attempts_log/attempt_history/human_review_queueは**そのまま保存**。`local_rewrite_recovery`記録も削除せず`local_rewrite_audio_superseded_by_human_approval=true`を付与)。バックアップ=`*.pre_ypl7_adopt_backup.json`。承認の範囲は**この1segment・1attemptのみ**で、ASR/Repetition QA検査の一般免除ではない。
- **a2 `y_voice_1`の減速後ASR再検証**は実施しない(`post_slowdown_asr_recheck=NOT_RUN`と記録)。ユーザーが試聴した音=減速後の音を承認する形のため。これを避ける場合は有料のASR再検証(1〜2呼出、概ね1円未満)を別途実施できる(新機構ではなく既存`apply_a2_slowdown_postprocess`の再利用)。
- **リハーサル結果(本委任、API 0、承認ではない)**: run_01を別名dirへ複製し3 segmentの採用をダミー発言ファイルで実行→上記手順2の`gate,assemble,pages,page_verify`を1起動で実行: **gate b1b/a2=PASS、assemble b1b OK 330.1秒/a2 OK 347.0秒、pages生成、page_verify ok、final_manifest.json生成、`user_test_page_standard_check_01` overall=PASS、`y_page_notice_check_01` ok**(所要約20秒)。リハーサルdirは削除済み(run_01は無変更で、この時点で未承認)。

## 3. 残工程・見積費用
| 工程 | API | 費用 |
|---|---|---|
| 採用(3 segment) | 0 | 0円 |
| gate/assemble/pages/page_verify | 0 | 0円 |
| 限定公開(配置・check・commit/push) | 0 | 0円 |
| 合計 | 0 | **0円**、所要約15〜20分 |

**承認されないsegmentがある場合**: そのsegmentはGate BLOCKのまま(完成せず公開物なし)。選択肢=①`er011_human_review_lock_01.approve_regenerate(..., approved_by="user")`(ユーザー承認の再生成。1 attemptあたり数円以内[E-1実測: b1b TTS stage 5.58円/7 attempt、a2 13.75円/複数attempt]。ただし同じD'境界に再び入る可能性があり、通る保証はない) ②D'境界問題(OPEN: YPL6-O1)の仕様判断(閾値・Y Voice文境界Chunk=新仕様)。①②ともユーザー判断。

## 4. a2 `preview`: 試聴承認以外の経路(既存仕様にあるもの)
- 既存の正規経路は(a)日本語支援文(Preview文言)の再生成=`--regenerate-stage support_a2`(約3円。EVIDENCE_02 §5(d))のみ。**ER-020 Local Rewriteは英語TTS前提のProduction経路で、日本語segmentのLRは`er058_ja_local_rewrite_applicability_01.py`(Trial専用・Production非経由)のみ=Productionに存在しない**。
- (a)を委任_06が推奨度低とした理由: ①ASRの誤NGを避けるために承認済みのPreview日本語文の本文を変えることになる(本文は音声が正しく読んでいるのに表記差だけでNG=OPEN-517の不具合であり、台本側で回避するのは根本対応でない) ②再生成で別の語でも同型の誤NGが再発し得る(OPEN-517の救済=案βが未適用のため) ③`support_a2`の入力shaが変わると`tts_a2`が`stale`になり、下流の再生成範囲が広がる(OK segmentの再利用は設計上あるが、影響範囲は未検証) ④費用は約3円+再TTSで、試聴承認(0円)より高く、品質上の利点もない。
- 結論(事実): 試聴承認が最小コスト・本文不変。OPEN-517の案β適用後の再走(別委任)も正規の代替だが時間がかかる。

## 5. ER-020 `identify_ng_span` ハイフン正規化の是正(委任_07、不具合是正・API 0)
- 原因(`er020_tts_retry_local_rewrite_01.py` `identify_ng_span`): `asr_validation.tokenize`(=`normalize_text`)は非英数字を空白にするため、ASR転写`re-deliveries`は`['re','deliveries']`、正本`redeliveries`は`['redeliveries']`となり、SequenceMatcherがreplace opを返す。分類器(`classify_asr_match`)は同じ差を`_is_compound_spacing_only_span`(複合語の分かち書き・ハイフン位置の差のみ)で個別diff spanごとに許容するが、`identify_ng_span`はこの許容を使わず**差分をそのままNG span**にしていた(承認済み『表記正規化』仕様との不整合=不具合)。
- 変更: `identify_ng_span`のdiff opsから、**既存の`asr_validation._is_compound_spacing_only_span`が真のopだけ**を除外(3行相当。新しい許容規則・辞書・閾値なし)。数値/否定を含むspan・片側が空のspan・単複差(`point/points`、`deliveries/delivery`)は従来どおり検出。Local Rewriteの発火条件・Prompt・回数上限は不変。
- test: `er020_tts_retry_local_rewrite_01_test_01.py::IdentifyNgSpanHyphenNormalizationTest`(6件)。是正前=4件FAIL(再現)/2件PASS(負例)、是正後=全PASS。遮断harness(`netblock_harness_01`)下の回帰: er020系+er021/er058/er007/er012/er117/er121/er026/er063/test_state_isolation=**454 passed/1 skipped(是正前は450 passed+新規4 FAIL)**、X/Z runner系(er019/er026/er103/er060/er081/er026_stop)=**226 passed/2 skipped(是正前後で同数)**。遮断ログ=接続試行0(ファイルなし)。sha固定testは`er020_tts_retry_local_rewrite_01.py`を対象にするものがなく期待値更新なし(`ProductionModuleUnchanged`系の保護対象は`er003_v1_sing01_voice01_generate/er011_human_review_lock_01/er007_ja_secondary_asr_01/er019_family_x_pointless_tts_01`で、変更なし)。
- E-1 `y_voice_1`の保存転写を使ったdry判定(`er020_hyphen_fix_dry_judge_01.json`):
  - **b1b `y_voice_1`**: 是正前=NG span`redeliveries`→Local Rewrite起動(保存結果`RESOLVED_BY_LOCAL_REWRITE`)。是正後=`found=false`→**Local Rewriteは起動せず**`HUMAN_REVIEW_LOCKED_NO_NG_SPAN`で止まる(書換えなし。1回目のb1b launchと同じ挙動)。
  - **a2 `y_voice_1`**: 保存された最終attempt(minimal fallback、`TRUE_CONTENT_MISMATCH`)の転写には、ハイフン差とは別に**実際の読み違い**(`their→the`、`can→could`)がある。是正後も`found=true`(最初の差=`their redelivery`↔`the re delivery`)。ハイフン差が原因のLRは起こらなくなるが、**本物の読み違いが残るこの最終attemptではLocal Rewriteは正当に起動し得る**(R0 attempt5の`NORMALIZED_MATCH`音声は別attempt)。
- X/Z runner processの確認: er020編集前に`Get-CimInstance Win32_Process`で確認。X runner(`er019_family_x_audio_production_runner_01.py --slug part2_hr_evidence_01 --run run_r2`、PID 44280/42716)が編集前に稼働中→約5分(285秒)待機→消滅を確認(RUN_LOCKファイル0・X/Z runner系process 0)してから編集。

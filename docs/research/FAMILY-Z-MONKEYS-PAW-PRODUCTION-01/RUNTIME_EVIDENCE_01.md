# RUNTIME_EVIDENCE_01 (FAMILY-Z-MONKEYS-PAW-PRODUCTION-01 委任_01、2026-10-24) 【途中状態: RESTART_STORM STOPで停止中】

run dir: `er026_output/family_z_production_e2e_01/the_monkeys_paw/run_sf_prod_01/`。実行は `.venv/Scripts/python.exe`、`TTS_EXECUTION_MODE=STANDARD`、Production経路のCLI。各起動前に `tools/stop_scope_check_01.py --managed-id FAMILY-Z-MONKEYS-PAW-PRODUCTION-01 --run-dir <run>` rc=0(`_stop_scope_check_*.json`)。HEAD(着手時)=00815e4d8。

## 起動履歴(run_launch_log.jsonl)
| # | JST(2026-10-24) | stages | 結果 |
|---|---|---|---|
| 1 | 17:54:40 | seed_check,writer,std_adjust | OK 19.37円(Adv r0/r1/r2 + Std、Adv 434語/Std 443語、段落32/32) |
| 2 | 17:59:15 | plan,support | **plan STOP**: `DIALOGUE_ATTRIBUTION_MISMATCH(a2): q24_1`(`"It's Herbert!"`: 決定論=mr_white[窓内にMr. Whiteが'caught her arm'で出る]、LLM=mrs_white[正]) |
| 3 | 18:01:20 | plan,support | **support STOP**: `SUPPORT_LINT_FAILED`(retry 1回NG): Comment3候補が`died`/`second wish`でSPOILER判定 |
| 4 | 18:04:25 | plan,support | OK(+0.86円、累計20.23円)。plan mismatch 0、support lint_warn=LISTEN_INSTRUCTION(Std日本語、WARNのみ・既存仕様) |
| 5 | 18:06:13 | kp | **RESTART_STORM STOP**(300秒に3起動[18:01:20,18:04:25,18:06:13=293秒]。`<run>/STOP`を自行発動。APIは呼んでいない) |

### 原因と是正(起動2・3は自分起因のdata誤り。起動5は自分の起動間隔の見誤り)
- 起動2: 決定論話者判定の窓キーワードに人名単体(`mr. white`,`herbert`等)を入れたため、`"It's Herbert!" She ran...pulling free when Mr. White caught her arm.`で誤判定(mismatch)。是正=キーワードを会話タグ型(`said mr. white`,`mrs. white asked`等、動詞×主語の組合せ)に変更(`STORY_SPEAKER_CONFIG[...]["z_voice_keywords"]/["dialogue_voice_keywords"]`と runner `voice_keywords`、いずれも本作entryのdata表のみ)。LLM判定は不変(LLMがtruth、決定論はクロスチェック)。
- 起動3: `STORY_LINT_CONFIG["the_monkeys_paw"]`のspoiler語が過広(`died`,`second wish`等)でCommentに出る『すでに聞いた部分』の事実をNG判定。Commentの設計(Comment2/3は聞いた部分を踏まえる、run_support_*)に合わせ、先回りを禁じる語を結末(第三の最後の願い・戻ってきたもの・無人の道・種明かし語)に限定。承認済みのlint機構は無変更、本作entryの値のみ。
- 起動5: 起動2〜4の間隔が短く、3起動が300秒窓(293秒)に入り`FAMILY_Z_RESTART_STORM`を発動。**`<run>/STOP`は自分で削除・`--clear-stop`していない**(解除はFable/ユーザーのみ)。

## Voice配役(`voice_assignment.json`、pinなし・決定的割当規則)
narrator=Aoede / 軍曹(morris)=Algieba / Mr. White=Schedar / Herbert=Fenrir / 使者(visitor)=Orus / Mrs. White=Zephyr / Adv補助=Charon。登場順はAdv/Std両本文の初出順(CP_CHECK_01.md §A#2)。Rosterは原作の発話者のみ。当初rosterは原作順(Mr. Whiteが1番)で登録し、Writer出力の初出順確認後にplan前に『初出順』へ訂正(data表の順序のみ、plan前のため音声への影響なし)。

## 構成・語数
Adv r2 434語・32段落、Std 443語・32段落(330-470内)。Std/Adv段落数一致。

## 費用(実績、cost_log.jsonl)
累計 **20.23円**(上限100円・目標70円): seed_check 0 + Writer(r0/r1/r2/std_adjust)19.37 + plan/support 0.86。plan/support再実行分(起動2・3)の追加費用は約0.4円。

## モデル
Writer=`gpt-6.1-sol`、plan/support/kp=`gpt-6-luna`(最新世代、本番ライン既定)。TTSは未実行。

## 登録test・全回帰
- 登録test `er026_family_z_story_registry_monkeys_paw_test_01.py` 22 tests OK。既存 `..._after_twenty_years_test_01`(21)・`..._gift_of_the_magi_test_01`(22) OK。
- 全回帰 `run_project_regression.py`(既定pattern): collected=7102 passed=7091 failed=1 skipped=10。failed 1件=`er064_kp_int_01_test_01.ProductionUnchanged.test_no_tracked_py_or_template_modified`(`REGRESSION_BASELINE_2026-10-24.md`既知の『未commitのtracked .py変更があると必ず失敗』。未commit tracked .pyは本作の3 .py[commit後に解消]+Family Yの`er110_family_y_opinion_based_03.py`・`build_theme_data_02.py`等、実行時)。`er003_test_bad`のFAILはrunner自身の意図的fixture出力(失敗に数えない)。他の失敗0。

## 未完(STOP解除後に実施)
kp → tts_b1b → tts_a2 → provision_shell,gate,assemble,pages,page_verify(1起動) → 公開page_verify(Playwright)。

# RESULT_PACKET: USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-DISCOVERY

**Status: Part A = Human Review READY。Part B = 完了(採用済)。Part C = 未実行・STOP(USER_DECISION_REQUIRED、費用上限超過見込み)。**

## A) B1 Human Review Player(Part A、¥0、API不使用)
- 生成物: `discovery/audio/b1b/human_review_player.html`(標準Audio Review Player CSSを再利用・拡張、相対パスのみ、`file:///`/`C:\`検出0件)、`discovery/audio/b1b/human_review_diff.json`、mp3: `discovery/audio/b1b/web/review/full_story_part2_attempt{1,2,3}.mp3`(既定表示=attempt3=最終)。
- 表示要素: (1)canonical script(parts.json part2、2文分割版該当部)、(2)各attemptのASR transcript(差分`<mark>`ハイライト)、(3)差分テーブル(canonical側/ASR側/推定seek秒)、(4)推定seek位置(duration×文字位置比、「概算」明記)、(5)個別mp3再生(attempt切替ボタン)。
- 実測diff(difflib語単位、read-only): attempt1/3は"a study of about 2,500 college students...phone use. In"の丸ごと欠落(delete)+"a"→"one"+"Japan–United"→"Japan-United"。attempt2は欠落なしだが"six"→"6"/"a"→"one"/"Japan–United States"→"Japan/U.S."等の言い回し差。FIX02報告の分析と整合。
- 音声・canonical本文は無変更(sha256/wav未改変)。予定URL: `https://raw.githack.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/discovery/audio/b1b/human_review_player.html`

## B) A2再生成(Part B、実測¥155.06)
- **方式選定**: 既存Discovery S2正式Production path(`run_one_pattern_staged_discovery_focus`、同一Ledger、Research再実行なし)で再生成。圧縮編集は不採用(Fact Safety: 圧縮のたびに新たなLedger逸脱リスク、既存Local Rewrite上限[3回]で吸収しきれない懸念/コスト: 反復QAが再生成2回より高くなりうる)。Prompt変更・length指示追加なし。
- **attempt1**: status=OK、word_count_raw=510→(No Jargon fix後)word_count_final=**530語**。stage1_regen_attempts=0、stage2_3_retry_attempts=0(内部retry不要)。Point Overlap QA: 非flagged(overlap_ratio 0.051/0.057、閾値0.4)、Point Value QA=PASS。No Jargon: hit_count=3(EKG/need for cognition/positive affect)→既存rewrite経路(`fix_all_jargon`、Ledger Deviation Checker hook-aware)で修正、resolved=True×2件、hit_count=0達成。修正後の記事全体final QA再実行: Fact Checker A' verdict=REVIEW_REQUIRED(既存仕様上non-blocking)、Ledger Deviation=LEDGER_COMPLIANT(MAJOR 0件)、Directional Fact Precheck=DIRECTION_REVIEW_REQUIRED(non-blocking)。
- **attempt2**: status=STOP_BUDGET_EXCEEDED_MIDRUN(Stage 1 Writer呼び出し直後にdriver側実行時budget guardが発火、既存run_discovery_a2.py/run_discovery_fix_b1b_kp.pyと同一のfail-after型設計、Production関数自体は無変更)。テキスト未生成。
- **採用**: attempt1のみが候補(2attemptとも500語以上ではないため「両方とも500語以上ならSTOP」規定には非該当)。**word_count_flag = WORD_COUNT_GE_500**(530語、明示)。`discovery/a2/article.md`・`reader_facing_article.txt`を新版へ差し替え、旧604語版は`discovery/a2_before_regeneration_604w/`へ退避(履歴保持)。
- Focus/Main Story/Points役割維持: Stage 1 Main Story確定→Stage 2 Point Role Planning→Stage 3 Point生成の既存順序どおり実行、Main Story固定原則を崩す修正は発生しなかった(stage1_regen_attempts=0)。
- Cross-Level: `cross_level_consistency.md`へ新版A2とB1Bの最終テキスト引用による軽量再突合を追記(旧F001-F012詳細marker表の完全再生成はスコープ外、必要ならユーザー判断)。
- model_id: Writer/Fact Checker/Ledger Deviation Checker = `gpt-5.6-luna`(既存routing、無変更)。

## C) A2音声再完成(Part C): **未実行・STOP**
- 理由: 委任文の費用上限(合計¥180、内訳Part A¥0/Part B¥120/Part C¥60)に対し、Part Bの実測が¥155.06(nominal超過)。合計上限¥180に対する残headroomは¥24.94しかなく、Part Cのnominal budget¥60を下回る(委任文STOP条件「費用上限超過見込み」に該当)。Key Phrase再選定・TTS・Assembly・Audio Validation・player・web_delivery.jsonはいずれも未着手(旧`discovery/audio/a2/`・`discovery/key_phrases/a2/`も退避・変更していない)。
- **ユーザー判断が必要な選択肢**: (a)合計¥180上限を若干超える前提でPart Cを別委任として実行する(過去実績からPart C実費は概ね¥40前後の見込み、確定ではない)、(b)Part Bの¥120→より高いnominal budgetへ正式に見直す、(c)本タスクはここでSTOPし、旧604語版音声のみが試聴可能な状態を維持する。

## D) 費用
- 開発・Trial/検証費: ¥0(604語版は既に前回¥606.08へ計上済みの過去費用であり、本タスクでの新規「不採用run」は発生していない。attempt2はbudget途中停止で結果自体が出ていない)。
- Part A: ¥0。Part B(A2再生成、本文): ¥155.06(budget¥120に対し超過、既存fail-after型ガード仕様どおりの挙動)。Part C: ¥0(未実行)。
- **Discovery Production 1生成セット総原価 = ¥606.08(前回まで) + ¥155.06(Part B) = ¥761.14(Part C未反映)**。`discovery/production_set_cost.json`の既存フィールド`production_set_total_cost_including_audio_jpy`はPart C未実行のため606.08のまま(`fu03_running_total_after_part_b_jpy`=761.14を新設フィールドとして追記)。

## E) その他
- T-0: PASS(`docs/pm/delegation_log/USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-DISCOVERY_check.json`)。
- 事前指定外Read: (a)`er003_discovery_focus_staged_production_01.py`の`run_one_pattern_staged_discovery_focus`関数本体(Grep範囲外、606-806行目付近)を追加閲覧。理由: 最終Fact Checker/Ledger/Directional/`article.md`保存・`run_summary.json`のword_count算出箇所を正確に把握し、Part Bドライバの後処理(jargon fix後の再保存・word_count再計算)を安全に設計するため。(b)`run_discovery_fix_b1b_kp.py`の`main()`内、jargon fix呼び出し・Key Phrase呼び出し部分(340-600行目付近)を追加閲覧。理由: `fix_all_jargon`/`run_final_qa`/`scaffold_gen.run_key_phrases`の実際の呼び出し引数(`ledger_model`の取得元`routing.require_model("A2_WRITER", ...)`等)を正確に再現するため。(c)`run_discovery_audio_completion.py`の`prepare_key_phrases`/`run_level`/`update_shared_outputs`/`main()`(203-726行目、Grep範囲外)を追加閲覧。理由: Part C設計のため(Key Phrase再利用の前提[article.md sha256一致]、`run_level("a2")`のturnkey構成、`update_shared_outputs`がproduction_set_cost.jsonへ与える副作用を事前に把握する必要があった)。結果としてPart Cは未実行だが、設計判断(STOP)自体がこの事前確認に基づく。(d)`er014_output/four_type_observation_01/discovery/audio/b1b/parts.json`の`part2`全文(Grep範囲外)を閲覧。理由: canonical scriptの正確な引用がPart A player作成に必須だったため。
- STOP: Part Cのみ(理由・選択肢は上記C参照)。Part A/Bはいずれも完了。
- Open Item候補: OPEN-135末尾追記案「2026-09-15 USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-DISCOVERY: A2を既存Discovery S2正式pathで再生成し530語版(旧604語版から)を採用(word_count_flag=WORD_COUNT_GE_500)。No Jargon修正・Fact Checker/Ledger Deviation/Point Overlap・Value/Directionalいずれも既存仕様上PASS相当(non-blocking項目含む)。A2音声再完成(Part C)は費用上限超過見込みでSTOP、USER_DECISION_REQUIRED。」。OPEN-153追記案「B1(B1B)は追加TTS再生成を行わず、既存3attempt音声のHuman Review player(`discovery/audio/b1b/human_review_player.html`)を作成、人間試聴承認方式へ移行。」。新規Open Item案「production_set_cost.jsonの`production_set_total_cost_including_audio_jpy`はタスクをまたいだ累積加算になっておらず、`update_shared_outputs()`実行時に古い`grand_total_jpy_including_key_phrase`(463.27)基準で再計算されてしまう(今回Part C不実行のため実害は発生していないが、Part C実行時に既存関数をそのまま使うと総額表示が誤る可能性がある。本タスクでは別フィールド`fu03_*`で正しい累計を保持する対応で回避)。」。
- commit対象候補一覧(サイズ付き、wav除外・mp3必須):
  - `docs/pm/delegation_log/USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-DISCOVERY.md`(13,651B、新規)
  - `docs/pm/delegation_log/USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-DISCOVERY_check.json`(1,049B、新規)
  - `docs/pm/RESULT_PACKET_FU03_DISCOVERY.md`(本ファイル、新規)
  - `er014_output/four_type_observation_01/discovery/build_b1_human_review_player.py`(12,566B、新規)
  - `er014_output/four_type_observation_01/discovery/run_discovery_a2_regen_fu03.py`(29,336B、新規)
  - `er014_output/four_type_observation_01/discovery/audio/b1b/human_review_player.html`(12,574B、新規)
  - `er014_output/four_type_observation_01/discovery/audio/b1b/human_review_diff.json`(21,201B、新規)
  - `er014_output/four_type_observation_01/discovery/audio/b1b/web/review/full_story_part2_attempt1.mp3`(531,216B、新規、mp3、gitignore対象外確認済み)
  - `er014_output/four_type_observation_01/discovery/audio/b1b/web/review/full_story_part2_attempt2.mp3`(735,096B、新規)
  - `er014_output/four_type_observation_01/discovery/audio/b1b/web/review/full_story_part2_attempt3.mp3`(541,176B、新規)
  - `er014_output/four_type_observation_01/discovery/a2/article.md`(3,628B、更新、604語版→530語版)
  - `er014_output/four_type_observation_01/discovery/a2/`配下その他(attempt1の監査ファイル一式、`shutil.copytree`によるattempt1 out_dirの複製+`post_jargon_fix_fu03.json`新規)
  - `er014_output/four_type_observation_01/discovery/reader_facing_article.txt`(3,628B、更新)
  - `er014_output/four_type_observation_01/discovery/cross_level_consistency.md`(3,942B、更新・追記)
  - `er014_output/four_type_observation_01/discovery/a2_regeneration_log.md`(1,565B、新規)
  - `er014_output/four_type_observation_01/discovery/a2_regeneration_adoption.json`(663B、新規)
  - `er014_output/four_type_observation_01/discovery/a2_before_regeneration_604w/`(旧604語版退避一式、履歴保持)
  - `er014_output/four_type_observation_01/discovery/a2_v2/attempt1/`・`attempt2/`(生成過程一式)
  - `er014_output/four_type_observation_01/discovery/raw_usage_log_a2_regen_fu03.jsonl`(Part B実測ログ、新規)
  - `er014_output/four_type_observation_01/discovery/production_set_cost.json`(13,128B超、更新)
  - `er014_output/four_type_observation_01/progress_log.md`(1行追記)
  - 本タスクではGit操作を行っていない(committer=Fable/ユーザー判断待ち)。

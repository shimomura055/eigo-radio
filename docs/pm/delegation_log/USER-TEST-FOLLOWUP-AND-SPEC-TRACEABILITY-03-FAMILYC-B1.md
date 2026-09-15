## 管理ID

USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-FAMILYC-B1(Family C / Home robots B1 Trial生成+完成episode)
並行タスク衝突確認: 並行して Family C A2 v2修正(`home_robots_v2/`、`er013_family_c_episode_trial_09b_run.py`/`_09b_test_01.py`を編集中→**本タスクはこれらを編集しない。関数はimportして再利用のみ**)、Discovery、Trend命名整理、仕様追跡調査が走る。本タスクは`er013_output/family_c_episode_trial_09/home_robots_b1/`配下と新規`er013_family_c_future_writer_08_b1.py`/`er013_family_c_episode_trial_09b_b1_run.py`/`er013_family_c_episode_trial_09b_b1_test_01.py`のみを書く。Git・SSOT・ACTIVE_TASK・RESULT_PACKET.mdを触らない。RESULT_PACKETは`docs/pm/RESULT_PACKET_FU03_FAMILYC_B1.md`(新規)。

## 性質/到達上限Status/禁止事項

- 性質: **Trial**(Family C B1)。最大Status VALIDATED。Production採用判断禁止。Trial-08 free-form architectureをProduction仕様と誤認しない(Family C Production正式pathは存在しない・未承認と明記)。
- **B1記事生成**: 同じHome robotsテーマ。A2(Trial-08 `er013_output/family_c_future_trial_08/home_robots/reader_facing_article.txt`)の**同一Story core**(登場人物・設定・出来事の順序・転換点・結末・Core Provocation)を維持しつつ、B1向けNatural Spoken Englishへ調整した**独立生成**(A2の単純翻訳・単純難化ではない)。B1難易度思想は既存Launch scopeのB1定義(CURRENT_SPEC「B1(独立生成Natural Spoken News English)」節・B1 Writer prompt)を参考にするが、Family C Trial-08 Writer(`er013_family_c_future_writer_08.py`)の制約(hard rule 2つ: reader-facing現在事実0件/登場人物1〜2名最大3名、`[[IMAGINED]]`等の既存マーカー方針、AI固有名はこの記事に限り許容[恒久ルール化しない]、語数は目安[B1目安は既存B1定義から採る、超過は必ず報告])を継承した派生Writer `er013_family_c_future_writer_08_b1.py`を作る(Trial専用、Production Writerは無変更)。Story coreの一致を機械+目視で確認(`story_core_check.json`: 人物名・場面順・結末文の対応表)。QA: Trial-08と同じStory Spark Gate(補助)・Fact Safety(CURRENT FACT 0件)・語数記録。
- **完成episode構成(今回確定分)**: Family A由来のIntro/Outro/Title/SFX/Pause(v2と同じ流用表)/Preview(日本語、既存原則)/Key Phrase 5件(既存正式経路、Validator不合格時は入口再呼び出し最大4回、表示=canonical=TTS=ASR一致を検証)/**Comment 1〜3、Comment 4なし**(ユーザー正式決定: Comment 1=導入理解補助、Comment 2=Story途中の自然な節目、Comment 3=後半の自然な節目。位置はsegment番号固定ではなく、semantic break・scene transition・turning point・前後text volume・前後audio durationで本記事について決め、候補と選定理由を`comment_placement.json`に記録)/Story/Mother別Voice(Erinome、v2と同一)/Robot Voice(Charon)/Narrator(Aoede)。Comment 3は「誰が問いかけ誰が答えたか」が曖昧にならない日本語にする(A2 v2で指摘された問題の再発防止)。
- Assembly→Audio Validation Gate(緩和禁止)→mp3→標準player(`home_robots_b1/player.html`、相対パス、Title/level=**B1**表記)→article/audio・player/display/audio consistency。v2の`er013_family_c_episode_trial_09b_run.py`の関数をimportして再利用(編集禁止。必要な差分はB1 script側でラップ)。
- 費用上限: ¥90(Writer≈¥5、Key Phrase≈¥10、Preview/Comment≈¥5、TTS≈¥45、余裕)。**開発・Trial/検証費として記録**(Family C累計に加算)。
- 禁止: A2本文変更/Production Writer・QA変更/Comment 4の生成/Gate緩和/`approve_regenerate()`/Production(er003/er006/er011/er012)コード変更/`_09b_run.py`・`_09b_test_01.py`の編集/Git commit・push/`.gitignore`変更/`run_project_regression.py --pattern`に`_test`を含まないglob/PATH上の素`python`。
- STOP条件: Story coreが維持できない/Fact Safety(CURRENT FACT>0)が解消しない/TTS Human Review Lock到達/費用上限超過見込み/技術的にWeb配信不可。STOP時は「何を試したか/何が残ったか/ユーザーに必要な判断」を提示。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
---

## ユーザー指示(原文・要点)

> Family C B1: A2修正完了を待たず並行して生成開始してよい。同じHome robotsテーマ。B1は既存Launch scopeのB1難易度思想を参考にするが、Family C Trialとして生成。A2の単純翻訳・単純難化ではなく、同一Story coreを維持しながらB1向けNatural Spoken Englishへ調整。Family Cで今回確定した構成を使用: Family A由来のIntro/Outro/Title/SFX/Pause、Preview、Key Phrase、Comment 1〜3、Story、Mother別Voice、Robot Voice、Comment 4なし。Trial-08 free-form architectureをProduction仕様と誤認しない。B1生成はTrial。最大Status VALIDATED。Production採用判断は禁止。

## 事前指定Read一覧

1. `er013_output/family_c_future_trial_08/home_robots/reader_facing_article.txt` 全文(Story core)。
2. `er013_family_c_future_writer_08.py` 全文(派生元Writer。prompt構造・hard rule・出力形式)。
3. `CURRENT_SPEC.md`: Grep `B1(独立生成|B1.*Natural Spoken|B1.*語|B1.*words|Launch scope` → B1難易度定義・語数目安の該当行のみ。
4. `er013_family_c_episode_trial_09b_run.py`: Grep `^def |^class |ARGS|argparse` → 再利用可能関数の一覧とシグネチャのみ(編集禁止)。
5. `er013_output/family_c_episode_trial_09/home_robots_v2/{family_a_reuse_map.md, speaker_map.json, comment_placement.json}` 全文(v2の流用表・話者判定・位置決定の書式)。
6. `docs/pm/RESULT_PACKET_FIX02_FAMILYC.md`: Grep `^## |Erinome|Comment` → v2構成の要点のみ。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 出力: `er013_output/family_c_episode_trial_09/home_robots_b1/{reader_facing_article_b1.txt, article_normalized.txt, word_count.json, story_core_check.json, spark_gate.json, fact_safety.json, preview.txt, key_phrases/, comments_ja.md, comment_placement.json, speaker_map.json, segments.json, audio/, assembled/, audio_validation.json, article_audio_consistency.json, player_display_audio_consistency.json, key_phrase_consistency.json, comment_consistency.json, player.html, web/episode mp3, web/segments/, web_delivery.json, cost_summary.json, raw_usage_log.jsonl}`、`spec/episode_spec_b1.md`(A2 v2との差分のみ)。
- 新規script 3件(上記)。テストは決定的(story core対応表の構造、Comment 4不在、player相対参照、file:///不在)。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-FAMILYC-B1.md --json-out docs\pm\delegation_log\USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-FAMILYC-B1_check.json`
2. `.venv\Scripts\python.exe er013_family_c_episode_trial_09b_b1_run.py --budget-jpy 90`(段階再開可能、全文コマンド記録)
3. テスト: `.venv\Scripts\python.exe run_project_regression.py --pattern "er013_family_c_episode_trial_09b_b1_test_*.py"`
4. 確認: `Select-String -Path er013_output\family_c_episode_trial_09\home_robots_b1\player.html -Pattern "file:///|C:\\" | Measure-Object -Line`(0件)、`git check-ignore -v er013_output/family_c_episode_trial_09/home_robots_b1/web/episode.mp3`(exit 1)

## SSOT追記文

本タスクではSSOTを編集しない。RESULT_PACKETにOPEN-147末尾追記案(B1 Trial生成結果、語数、構成、費用、Status VALIDATED候補・試聴待ち)を記載。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作を行わない。RESULT_PACKETに「commit対象候補一覧(サイズ付き、wav除外・mp3必須)」を列挙。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_FU03_FAMILYC_B1.md`に: 1) 最終Status、2) B1記事(語数[目安と超過有無を必ず明記]、Story core対応表要約、Spark Gate、CURRENT FACT件数、A2との差異の性質[難易度・表現])、3) Preview/Key Phrase 5件(4者一致)/Comment 1〜3(本文・位置・選定理由・前後volume)、4) Voice構成、5) Assembly順序、Audio Validation、duration、6) consistency結果、7) mp3/player/予定URL(`https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_09/home_robots_b1/player.html`)、8) 費用(開発・Trial費、Family C累計)、9) model_id/TTS、10) Open Item候補、11) commit対象候補一覧、12) T-0・事前指定外Read・STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥90)
- [x] 並行タスク衝突回避あり(home_robots_b1限定・v2 script編集禁止・Git操作なし)

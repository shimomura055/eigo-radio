## 管理ID

USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-VOICES(継続CONT1、Fable修正指示1回目)
並行タスク衝突確認: 並行タスクなし(他3件は完了済み)。本タスクは`er014_output/four_type_observation_01/voices/`配下のみを書く(er012_*は前回修正済み・本タスクでは無変更)。Git・SSOT・ACTIVE_TASK・RESULT_PACKET.mdを触らない。RESULT_PACKETは`docs/pm/RESULT_PACKET_FIX02_VOICES_2.md`(新規)。

## 性質/到達上限Status/禁止事項

- 性質: 前回(`docs/pm/RESULT_PACKET_FIX02_VOICES.md`)で一人称化Prompt修正後、既存2V正式経路で2回再生成(`run3_first_person/`、`run3_first_person_r2/`)。いずれも一人称化OK(`pov_check.json`)だが、Tension文の事実精度でFact Safety Gate/Ledger Deviation Local Rewriteが作動し`NG_REVIEW_REQUIRED`で記事未確定。Status上限=`PARTIAL / USER TEST READY`。PRODUCTION_WIRED禁止。OPEN-151はPARTIALのまま。
- 手順(既存仕様内、Gate・MAX_WRITER_ATTEMPTS・Leakage基準は無変更):
  (1) **再生成を1回だけ追加**(同一Ledger再利用、`run_voices_2v_b1_v2.py`→`main_b1_2v()`の既存経路、出力`run3_first_person_r3/`)。status=OKなら(3)へ。
  (2) r3もNGの場合: r1/r2/r3のうちNG項目が最少のrunを選び、`NG_REVIEW_REQUIRED`の原因文(Tension文)に対して**既存のLocal Rewrite human_review escalation経路**(Discovery CONT1で使用した`er010_ledger_local_rewrite_09.apply_diff_qa_to_resolved_rewrite`へoperator修正文を投入し、Fact Checker A'+Ledger Deviation Checkerで受理判定)で修正する。operator修正文はLedgerの該当factに厳密に整合し、Voice/Tensionの一人称・役割は維持、語の追加削除は最小。受理後、Writer段の後続QA(Fact Checker A' 2V、Ledger Deviation、Analytical Leakage Check[結果は記録のみ、残存flagは許容=Status PARTIALの根拠]、Comment Contract)を通常どおり再実行し記事を確定(`run3_first_person_final/`)。escalation経路が存在しない/受理されない場合はSTOP。
  (3) 音声化: 前回CONT1のdriver(`run_voices_2v_audio_completion_2.py`)と同一経路で確定記事に対しPreview/Comment/Key Phrase/TTS/Assembly/Audio Validation Gate(緩和禁止)/mp3/player(`voices/audio/b1_2v_v2/player.html`、相対パス、Title/level=B1 2V、Status注記「PARTIAL / USER TEST READY(一人称版)」+Leakage残存有無)/article-audio consistency/`comment_fact_safety_evidence.json`(Fact Safety Gate発火記録を含む: 今回は2Vで実発火した証拠として詳細に記録=OPEN-120のevidence)。TTS Human Review Lock到達時は`approve_regenerate()`禁止でSTOP。
  (4) `pov_check.json`(最終記事)、費用更新(`voices/run2_clean/production_set_cost.json`または既存位置: Voices総原価=¥185.74+前回¥76.62+本タスク実費、差分明記)、`progress_log.md`1行。
- なぜ既存QAで三人称化を検出できなかったか: 前回の記載を再掲し、今回のGate発火(Tension文)が「正しく機能した」例であることを対比して記載。
- 費用上限: 本タスク¥120(再生成1回≈¥40+escalation≈¥10+音声化≈¥50)。段階ごとに次段階見込み込みで事前判定。
- 禁止: Research再実行/Prompt変更(前回修正以上の変更)/MAX_WRITER_ATTEMPTS変更/Gate緩和/3V変更/`approve_regenerate()`/PRODUCTION_WIRED表記/`.gitignore`変更/Git commit・push/`run_project_regression.py --pattern`に`_test`を含まないglob/PATH上の素`python`(前回3回の逸脱を繰り返さない。集計も`.venv\Scripts\python.exe`で)。
- STOP条件: r3 NGかつescalation不成立/新仕様が必要/Gate緩和が必要/費用上限超過見込み/TTS Human Review Lock到達/技術的にWeb配信不可。STOP時は「何を試したか/何が残ったか/ユーザーに必要な判断」を提示。

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

> 一人称が既存正式仕様なら新仕様ではなくProduction不整合。修正する。各Voice本人が自分の立場を語る構造へ戻す。Fact/Ledger/Comment/Leakage QAを通常どおり再実行。OPEN-151は残存Leakageがあるため勝手にPRODUCTION_WIREDにしない。Audio Validation PASSをEditorial構造PASSの根拠にしない。既存仕様・既存音声経路で完成できる限り途中でユーザーへ戻さず進める。

## 事前指定Read一覧

1. `docs/pm/RESULT_PACKET_FIX02_VOICES.md` 全文(前回到達点、r1/r2のNG内容)。
2. `er014_output/four_type_observation_01/voices/run3_first_person/`・`run3_first_person_r2/`: Glob `**/*.json` → NG理由(Fact Safety Gate/Ledger Deviation)を含むJSONのみRead(該当Tension文・deviation内容)。
3. `er014_output/four_type_observation_01/voices/run_voices_2v_b1_v2.py` 全文(再生成の入口)。
4. `er014_output/four_type_observation_01/discovery/run_discovery_complete_2.py`: Grep `operator|escalat|apply_diff_qa_to_resolved_rewrite|rewrite_result` → operator escalationの呼び出し方(Discovery CONT1実装)のみ。
5. `er012_b_family_production_runner_01.py`: Grep `def run_fact_check_a_prime_2v|def run_comment_contract_for_new_theme|leakage|def _apply_b_family_voice_safety_gate|NG_REVIEW_REQUIRED` → 記事確定後QAの呼び出し関数のみ。
6. `er014_output/four_type_observation_01/voices/run_voices_2v_audio_completion_2.py` 全文(音声化driver。`--article-dir`引数化して`_3.py`を派生)。
7. `er014_output/four_type_observation_01/voices/run2_clean/production_set_cost.json` 全文。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 出力: `voices/run3_first_person_r3/`、(必要時)`voices/run3_first_person_final/{article.md, audit/, operator_escalation.json}`、`voices/audio/b1_2v_v2/{...v1同構成..., player.html, web/}`、`voices/audio/web_delivery.json`(v2追記)、`voices/pov_check_final.json`、費用ファイル、`progress_log.md`。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-VOICES-CONT1.md --json-out docs\pm\delegation_log\USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-VOICES-CONT1_check.json`
2. 再生成: `.venv\Scripts\python.exe er014_output\four_type_observation_01\voices\run_voices_2v_b1_v2.py --reuse-ledger --out-subdir run3_first_person_r3 --budget-jpy 45`(前回の引数名に合わせる。全文コマンド記録)
3. (必要時)escalation: `.venv\Scripts\python.exe er014_output\four_type_observation_01\voices\run_voices_2v_operator_escalation.py --source-run <r1|r2|r3> --out run3_first_person_final --budget-jpy 25`(本タスクで作成)
4. 音声化: `.venv\Scripts\python.exe er014_output\four_type_observation_01\voices\run_voices_2v_audio_completion_3.py --article-dir <確定run> --out audio/b1_2v_v2 --budget-jpy 50`
5. 確認: `Select-String -Path er014_output\four_type_observation_01\voices\audio\b1_2v_v2\player.html -Pattern "file:///|C:\\" | Measure-Object -Line`(0件)、`git check-ignore -v er014_output/four_type_observation_01/voices/audio/b1_2v_v2/web/episode.mp3`(exit 1)
(回帰不要: er012無変更。)

## SSOT追記文

本タスクではSSOTを編集しない。RESULT_PACKETにOPEN-151末尾追記案(一人称版確定/未確定、音声化、Status PARTIAL / USER TEST READY)、OPEN-120追記案(2VでのFact Safety Gate実発火evidence: run・stage・deviation内容・結果)を記載。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作を行わない。RESULT_PACKETに「commit対象候補一覧(サイズ付き、wav除外・mp3必須、前回のer012変更ファイル・テスト含む)」を列挙。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_FIX02_VOICES_2.md`に: 1) 最終Status、2) r3結果(status、NG内容)、3) escalation実施有無(対象文 旧→新、diff QA結果、後続QA結果)、4) 確定記事(パス、語数、pov_check、Fact Checker/Ledger/Comment Contract/Leakage結果)、5) 音声化(TTS attempt、Audio Validation、duration、mp3・player・予定URL `https://raw.githack.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/voices/audio/b1_2v_v2/player.html`)、6) Comment/Fact Safety反映証拠(Gate実発火記録含む)、残存Leakage記録、7) なぜ既存QAで三人称化を検出できなかったか(再掲)+今回Gateが正しく機能した対比、8) 費用(本タスク実費、**Voices総原価=¥185.74+¥76.62+実費=¥xx.xx**)、9) model_id/TTS model、10) Open Item候補、11) commit対象候補一覧、12) T-0・事前指定外Read・STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥120)
- [x] 並行タスク衝突回避あり(voices/配下限定・Git操作なし)

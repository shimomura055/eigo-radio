# FAMILY-X-COFFEE-FINAL-AUDIO-ASSEMBLY-01 委任_02(2026-10-12)

Status: **完了・ユーザー試聴待ち(USER_DECISION_REQUIRED)**。Trial隔離、Production配線=未(PRODUCTION_WIRED未達)。共通Prompt/routing/Master Store/既存正式音声/CURRENT_SPEC共通仕様の変更なし。

## 1. 何が問題だったか
委任_01でStd Full Story Part2(PD8同一Prompt3 attempt)がPrimary ASRで全てUNCERTAIN(US/U.S.・cost/costs・数字表記等の表記差のみ=偽NG)となりSTOP。Fable判断(A)で、Production承認済みのSecondary確認をTrial隔離で適用して再開。

## 2. 何を変更したか
- `er057_coffee_final_v3_std_part2_secondary_01.py`: 既存`er006_secondary_asr_01.evaluate_attempt_with_cascade_detail`(cascade_enabled、connected speech layer有、segment_id=full_story_part2、Phrase List無し)を3候補に適用。Primary文はgeneration_log記録を再利用。ledger書込無効化、cost_loggerはTrial専用ファイル、telemetryはTrial内メモリ。結果: a1/a2=Secondary#1(Azure)でNORMALIZED_MATCH、a3=Primary#2でNORMALIZED_MATCH。local whisper差分: a1=4語/a2=8/a3=8 -> **a1採用**(50.47秒、複数PASSのため差分最少)。`std_part2_secondary_cascade_01.json`、`std_part2_local_whisper_diff_01.json`。
- 6%減速(Part2 50.47->53.48秒、比1.0596)。Standard v3組立(Trial assembler無改変、4 roleのみ差替え: Part1〜3+IOL、26 role不変)。Advanced v3は委任_01の組立を再利用。
- QA: Std 314.17秒 peak 0.951 clip 0、Adv 314.97秒 peak 0.959 clip 0。異音検知(閾値不変): Std候補20(非固定11)、medium以上0。
- WPM(Part1〜3、`wpm_v3_01.json`、既存measure_wpm_01ロジック): Std 全体166.0(発話部分190.5、減速前175.9)、Part別149.5/180.6/165.8。Adv(PD8)全体183.2(発話193.6)、Part別169.8/192.5/185.3。
- 試聴ページ `user_test/coffee_final_v3/`(commit 4276f676)、Playwright実再生PASS(`PLAY_EVIDENCE_V3_01.md`)。`PRODUCTION_DIFF_V3_01.md`、`STYLE_APPLICATION_EVIDENCE_V3_01.md`。
- SSOT: DECISION_LOG追記、CURRENT_SPEC(Coffee限定採用Style記録のみ追記)、OPEN_ITEMS(OPEN-298/299/300新規、272/279/281/293/295/296追記)、REPORT_LEDGER。

## 3. 何が改善されるか
Coffee Standard/Advanced両Levelの完成版v3(新In One Line・PD8・Style採用反映)を、ユーザーが通しで試聴できる。

## 4. リスク・注意点(未解決)
- Std Part2はSecondary採択(Primary単独では通らない)。聴感で読み間違いの確認が必要。
- Adv Part1 13.3秒付近low click/「wanna」疑い、Part3 39.85秒付近low click、Std Part2 32.07秒付近click(low)等、既知異音はlowのみ(未解決、要試聴)。
- F-5型偽NG(OPEN-272)はProduction経路でも再発し得る。
- Production配線なし。Coffee限定の反映は記事別Style override層の新設が必要(OPEN-300、Opus独立レビュー条件A対象)。全記事共通展開は未承認(OPEN-298)、In One Line 2文方針は未仕様化(OPEN-299)。

## 費用・作業時間
委任_02: Azure Secondary 2呼出(計99.9秒音声、約JPY4.4)+Primary#2 3呼出等(推定JPY約1.3)=約JPY5.7、委任_01 約JPY8.6、累計約JPY14.3(上限JPY50、推定値、請求画面未確認)。作業時間: 約25分(コーディング・実行・公開確認含む)。

## Production不変確認
Master Store manifest/reuse_telemetry、human_review_queue、attempt_history、各telemetry、ledgerの8ファイル: 最終更新はすべて本タスク開始前(10-11〜10-12 09:13)、sha256記録 `production_sha_after_v3_02.txt`。CURRENT_SPEC共通仕様差分なし(Coffee限定記録セクション追記のみ)。

## 成果物
`er057_output/coffee_final_audio_assembly_01/`(PRODUCTION_DIFF_V3_01.md、STYLE_APPLICATION_EVIDENCE_V3_01.md、PLAY_EVIDENCE_V3_01.md、qa_v3_01.json、anomaly_v3_{adv,std}.json、wpm_v3_01.json、pages_play_evidence_v3_01.json)、scripts `er057_coffee_final_v3_{std_part2_secondary,page,play_verify}_01.py`。

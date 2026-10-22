FABLE-DELEGATION-MARKER: PNPS-STAGE2-CLOSEOUT-委任_10-20261022

# 委任(PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02 委任_10: Stage 2 Trial Closeout。(A)Trial音声を**本番の判定器(M1複数候補判定込み)**にそのまま通してHuman Review基準値を取り直し、Melosを「解消済み」として対象から外す(API 0)。(B)Fable独立評価・終了Status・ユーザー判断事項をSSOTへ記録。費用JPY0)

## 管理ID
PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02 委任_10(OPEN-441。並行: 別agentが`HR-QUEUE-TEST-CONTAMINATION-FIX-01 委任_02`(er021系testのattempt_history隔離)を作業中でOPEN-447行・REPORT_LEDGER末尾を編集する。共有SSOTは`git status`→該当行再Grep→自分の行だけ→即add+commit、`index.lock`は30秒待ち。`er021*_test*.py`/`er011_output/attempt_history.jsonl`には触らない)。

## 性質/到達上限Status/禁止事項
- 性質: 0円のオフラインreplay+記録。到達Status: OPEN-441 Stage 2=`TRIAL_CLOSED_USER_DECISION_REQUIRED`(Fable分類: 判定側方式=`REJECTED`、TTS入力側供給=Khaite型限定で`VALIDATED(条件付き)`、Production採用はユーザー判断)。Opus Gate: Step B済み。追加レビュー不要(採用提案時に条件C)。
- 費用/日次: JPY0(有料API呼出禁止。TTS/ASR/LLM不可。保存済み転写のみ使用)。
- 禁止: Production/正式Ledger/HR queue/Store/Validator/Prompt変更禁止。`git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f。secret_scan hits=0。push=`git push origin HEAD:main`。ACTIVE_TASK/RESULT_PACKETはgitignore。SSOT全文読込禁止。他agentの未commit差分を混ぜない。推測で発音正否を断定しない。

## 前委任(委任_09)の受入記録(Gate 7、Fable記入)
- 当初目的(ユーザー原文逐語): 「正しい音声を安全に自動合格させ、Human Reviewを実際に削減すること。」
- 最終成果物: `STAGE2_TRIAL_RESULT_03.md`/`DESIGN_03`、`er100_output/pnps_stage2_trial_01/r3/`、`user_test/pnps_stage2_hr7_listen_03/`。commit 496daa990/b5110b551。
- 証拠: Khaite綴り置換(→Kate)8/8で4エンジン全員「kate」、Meink/Altuzarraは制御不能(`r3/agg.json summary_by_word_arm`)。誤読対照: Meink→Minkは置換後比較でPASS化=方式の安全性は供給発音の正しさに全面依存(事実)。費用49.85(`r3/paid_calls.jsonl`)、Trial累計128.94/300。Production無変更(`r3/protect_note*.json`)。
- 一致・不一致: 部分適合(Khaite型のみ効果)。
- 判定: ACCEPTED(第3巡として)。判定整合: 重大NG=なし/主因=制御不能語・供給元なし語/是正対象=なし/STOP理由=合理的な改善見込みの消尽(下記Fable評価)/提示=ユーザー判断1件。

## (A) 本番判定器でのreplay(API 0)
1. ユーザー指摘(2026-10-22): 「Melos said.」はM1複数候補判定(`er006_m1_multi_candidate_01.py`、Production配線・既定ON、CURRENT_SPEC ~L2807-2810、run_e2e_03[2026-10-17]で`M1_MULTI_CANDIDATE`PASS_WITH_WARNING・HR Lock 0)で**解消済み**。第1〜3巡の「HRプロキシ(Primary/Azureの綴り一致)」はM1を通していないため、Melos等を過大にHRと数えた。
2. 第2巡take1の30 segment(現行TTS)と第3巡の全音声について、保存済みの転写(Primary/Azure)を**本番の判定経路**(`er006_secondary_asr_01.py`の判定関数+M1+同音救済+Connected Speech等、実際にProductionで使われる関数。HR queue/Store/Ledgerへ書き込まないようwriterを隔離[tmpへmonkeypatch]し、実行前後でHR queue・attempt_history・Store manifest・Ledgerのsha256不変をassert)に通し、segmentごとに「本番判定=PASS/PASS_WITH_WARNING/NG→HR」を得る。判定に必要な入力(canonical本文、両転写、segment role、Ledger読み取り)は保存データから渡す。Secondary転写が無い音声は「Primary判定のみ」と明記。
3. 集計: (i)本番判定でHRになる独立segment数(=真の基準値)と語別内訳、Melosは別掲(解消済みと注記)。(ii)そのうちKhaite型(第3巡の綴り置換で4エンジン全一致「kate」になった)で救える件数(実測3+同系推定、実測と推定を分ける)。(iii)第1巡の保存HR事象58についても、単体テスト混入25行(OPEN-447 sidecar)を除いた実質件数と、M1配線前/後の区分(timestamp基準、M1配線=2026-10-14)を表に。
4. 成果物: `er100_pnps_stage2_trial_01_closeout_replay.py`、`er100_output/pnps_stage2_trial_01/closeout/{prod_judge_replay.json,baseline_table.json,protect_closeout.json}`。

## (B) Fable独立評価・Closeout(`STAGE2_TRIAL_RESULT_03.md` §7・§8へ逐語で追記し、要約を`STAGE2_TRIAL_CLOSEOUT_01.md`として新規作成[ユーザー§7の1〜8順、(A)の取り直し数値で記載])
### 7. Fable独立評価・Trial終了Status(2026-10-22)
- 分類: **判定側の改善方式(計画v4の中核: 取得/推定発音とASR転写の音素照合、第1巡・第2巡)=`REJECTED`**(Opus Step Bの補正を入れてもHR削減0〜2件。天井約24%、実測0%。主因は判定ではなく現行TTSの実誤読)。**TTS入力側への取得発音供給(第3巡)=Khaite型に限り`VALIDATED(条件付き)`**(綴り置換でTTSが追従する語では8/8で全エンジン一致。Meink/Altuzarraは制御不能、Toteme/Zabelina/Canelé/Melosは供給元なしまたは解消済み)。**Stage 2全体=`USER_DECISION_REQUIRED`**(Production採用の可否は下記8)。改善ループはStep A→B→Cを2回(第2巡・第3巡)回し、残る代替案(音素認識wav2vec2=判定側で天井低、Meink別制御=既存例なし・見込み低、取得拡充=22ページ確認済みで見込み低)はいずれも合理的な改善見込みが小さいため、ここでSTOPする(ユーザー§4の終了条件「原因分析と代替方式の検討により合理的な改善見込みがないと確認」に該当。予算は累計128.94/300で余裕があるが、費用があることは継続理由にならない)。
- 最重要の事実: 対象7語がHuman Reviewに回る主因は「正しい音声の誤判定」ではなく「TTSが実際に誤読している」こと(現行TTSで複数ASRが揃って別語に聞き取る事象が多数。試聴ページ02/03で確認可能)。したがって**これらの語についてはHuman Reviewは正しく機能している**。Melosは既存のM1複数候補判定で解消済み(第1〜3巡のHR件数にMelosを含めたのは過大で、途中報告で訂正済み)。
- 安全性: 全巡で明確な誤発音の新規誤PASS 0(拡充負例29本)。発音根拠の虚偽登録0、Production判定変更0、正式Ledger登録0。
- TTS入力側供給の限界(事実): Reicher→Riker方式は「置換後テキスト」でASR比較するため、**誤った発音を供給すればそれが正解として通る**(Meink→Minkの対照で実証)。安全性は供給元の正しさに全面依存し、Khaiteの供給元はNylon 1媒体(B階層)のみ。
- 費用: Trial累計JPY128.94(第1巡15.54/第2巡63.55/第3巡49.85)。量産単価影響: 採用しなければ0。採用しても文字列置換で追加API 0(Ledger→辞書の自動供給は未実装=新仕様)。
### 8. Production採用に必要なユーザー判断(1件)
- 問い: 「取得した発音(公式/実使用)をTTS入力の綴り置換へ供給し、Khaite型の誤読を自動で直す」仕組みを新仕様として採用するか。
- 選択肢: (ア)採用しない=現状維持(この型の新出ブランド名等は従来どおりHuman Reviewで人が1回聴いて承認。発生頻度は保存データで新出辞書外語12種/約2か月、HR 1回の人手コストのみ、API追加0)。(イ)採用する=A階層(公式・引用実在確認済み)のみ自動供給、B階層(媒体)は人が1回承認した語だけ辞書へ登録(Production変更・Opus条件Cレビュー・配線Trialが必要。効果は本Trialで確認できた範囲ではKhaite 1語型)。
- **Fable推奨=(ア)現状維持。** 理由: 実証できた効果が1語型に限られ、方式の安全性が供給元の正しさに全面依存する一方、Human Reviewはこれらの語で正しく機能しており、人手コストは月数件・1回限り。費用対効果でも(イ)の実装・運用コストが上回る。(イ)を選ぶ場合も、A階層限定+人承認登録なら安全条件は守れる。

## SSOT更新
- `OPEN_ITEMS.md` OPEN-441: Stage 2のStatusラベルを`STAGE2_TRIAL_CLOSED_USER_DECISION_REQUIRED(判定側REJECTED/TTS入力側Khaite型VALIDATED条件付き、Fable推奨=現状維持、UDR #147)`へ、履歴1文(取り直したHR基準値・Melos解消済み・費用累計)。
- `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `#146` → 直後に `- #147(UDR・**回答待ち**・非blocking、PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02 Stage 2、OPEN-441) 件名=取得発音のTTS入力側供給(綴り置換)の新仕様採用可否。選択肢(ア)現状維持=HRで人が1回承認/(イ)A階層のみ自動供給+B階層は人承認登録。Fable推奨=(ア)。根拠=STAGE2_TRIAL_CLOSEOUT_01.md §7-8。試聴=user_test/pnps_stage2_hr7_listen_0{2,3}。` を追加。#142行を「判断済み(Trial GO)→Trial完了(Closeout 2026-10-22)」と1句更新。
- `DECISION_LOG.md`: 末尾に「PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02 Stage 2 Trial Closeout Fable分類(2026-10-22)」エントリ(§7要旨・STOP根拠・§8・Production無変更・Melos解消済み訂正)。
- `docs/pm/OPUS_FINDINGS_LEDGER.md`: OF-PNPS-S2R-01〜10を`CLOSEOUT_CONFIRMED`(各1句: 実施結果)。S2R-02の「Melos said.」仮説は「M1で解消済み・HR行の25件はtest混入」と注記。S2R-06(Primary正綴り寄せ)は`FABLE_DECIDED`=観察継続(第2巡測定 6.9%・自然音声3/30。Production変更なし。実害の発生が確認された時点でOPEN起票)。
- `docs/pm/REPORT_LEDGER.md`: 1行。
- `docs/pm/ACTIVE_TASK.md`固定ヘッダ(当日費用=2026-10-22 約799.5/1,000[出典 RESULT_PACKET_PNPS9]、UDR-deferred #147/#146/#145/#144)。
- T-0: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02_委任_10.md`(Nは`FABLE-DELEGATION-MARKER: PNPS-STAGE2-CLOSEOUT-委任_10-20261022`を含むAgent tool_useの通番、274前後。先頭行で一致確認)。

## 事前指定Read/Grep
- Read: `STAGE2_TRIAL_RESULT_0{2,3}.md`(§1〜§3)、`er100_output/pnps_stage2_trial_01/r2/{agg.json,plan.json}`、`r3/agg.json`、`er006_m1_multi_candidate_01.py:1-80`、CURRENT_SPEC Grep `M1_MULTI_CANDIDATE`近傍(~L2807-2810)。
- Grep: 本番判定の入口関数=`def classify_asr_match|def _secondary_accept|def judge|m1_enabled` in `er006_secondary_asr_01.py`/`er078_asr_unified_judge_01.py`(replayで呼ぶ関数を特定し、writer隔離点[`HUMAN_REVIEW_LOG_PATH`等]を確認)。`human_review_queue_exclusions_01.json`(混入25行)。

## Git
- 明示add: `er100_pnps_stage2_trial_01_closeout_replay.py`、`er100_output/pnps_stage2_trial_01/closeout/**`、`docs/research/PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02/{STAGE2_TRIAL_RESULT_03,STAGE2_TRIAL_CLOSEOUT_01}.md`、delegation_log、上記SSOT5ファイル。
- commit: `PNPS Stage 2 委任_10 Closeout: 本番判定器(M1込み)replayでHR基準値を取り直し(Melos解消済み)、Fable分類=判定側REJECTED/TTS入力側Khaite型VALIDATED条件付き/全体USER_DECISION_REQUIRED(推奨=現状維持)、UDR #147、¥0`。push→到達確認。

## 報告(RESULT_PACKET_PNPS10.md)
(A)の取り直し表(本番判定でのHR基準値・語別・Melos別掲・Khaite型で救える実測/推定・保存58事象の実質件数とM1前後区分)/本番判定器の呼出関数と隔離方法/(B)の記録箇所/RESULT_PACKET 4行/raw URL(CLOSEOUT_01.md、prod_judge_replay.json)。
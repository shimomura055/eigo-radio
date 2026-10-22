FABLE-DELEGATION-MARKER: PNPS-STAGE2-TRIAL-R3-委任_09-20261022

# 委任(PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02 委任_09: Stage 2 Trial 第3巡[Step C-2]。HR主因が「TTSの実誤読」と判明したため、取得済み(公式/実使用)発音を**TTS入力側の読み制御**に使い、HRを「発生させない」方式をTrial内で検証。Guardrail JPY60(Trial累計Cap300の残220内)。Production/正式Ledger/HR queue/Store無変更)

## 管理ID
PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02 委任_09(OPEN-441。並行: 別agentが`er026_post_slowdown_cascade_rescue_01_test_01.py`のtest隔離とHR queue sidecarを作業中(`HR-QUEUE-TEST-CONTAMINATION-FIX-01`)。本委任はそれらのファイルに触らない。共有SSOT(`OPEN_ITEMS.md`/`REPORT_LEDGER.md`/`OPUS_FINDINGS_LEDGER.md`)は`git status`→該当行再Grep→自分の行だけ→即add+commit、`index.lock`は30秒待ち)。

## 性質/到達上限Status/禁止事項
- 性質: Trial第3巡(ユーザー指示§4 Step C「別のアプローチ」「既存計画v4に固執しない」の範囲内。Opus OF-PNPS-S2R-10(1)=2次案を、第2巡で主因がTTS実誤読と判明したため繰り上げ)。到達Status: `TRIAL_R3_DONE_PENDING_FABLE`。
- Opus Gate: Step B済み。本巡はその所見(S2R-10(1))の実行であり追加レビュー不要。
- 修正範囲(11-8): 範囲内=Trial専用`er100_*_r3_*.py`、`docs/research/PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02/STAGE2_TRIAL_{DESIGN,RESULT}_03.md`、`er100_output/pnps_stage2_trial_01/r3/`、試聴ページ`user_test/pnps_stage2_hr7_listen_03/`。範囲外=Production経路(`er003_v1_n3_01_tts_generate.py`の`tts_safe_name_pronunciation_en`辞書を含む)・正式Ledger・HR queue・Store・Validator・Prompt・モデル構成の変更。TTS生成は第2巡と同じ方法(TTSクライアント直接呼出、Production設定を読み取って記録、Store/HR queue/attempt_history非書込をsha256/行数assert)。
- 時間見込み(8-X): 約3〜4時間。生成→4エンジン書き起こし(並列)/判定replay/試聴ページ/報告。
- 費用/日次: 当日既使用 約JPY749.6(出典: 第2巡RESULT_PACKET_PNPS8)。残 約JPY250。本委任見積 約JPY40(約50本×実測[第2巻: TTS 0.46+ASR窓0.37/本]。推定LLM 0)。Guardrail(T-3) **JPY60**。Trial累計 79.09/300(残220.91)。承認区分: C。単価出典は第2巡と同じ(OpenAI ASR秒換算は上限見積と明記)。
- 禁止: `git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f。secret_scan hits=0。push=`git push origin HEAD:main`。ACTIVE_TASK/RESULT_PACKETはgitignore。SSOT全文読込禁止。他agentの未commit差分を混ぜない。有料runの再起動禁止、STOPセンチネル確認後に開始。`TTS_EXECUTION_MODE=STANDARD`。**ESTIMATED(推定)発音をTTS側へ供給しない**(計画v4-5、承認済み原則)。LLM official自己申告を根拠にしない。Primary正綴りを判定根拠に数えない。推測で発音正否を断定しない。

## 前委任(委任_08)の受入記録(Gate 7、Fable記入)
- 当初目的(ユーザー原文逐語): 「正しい音声を安全に自動合格させ、Human Reviewを実際に削減すること。」
- 最終成果物: `STAGE2_TRIAL_RESULT_02.md`/`DESIGN_02`/`OPUS_REVIEW_STAGE2_STEPB_01.md`(要旨)、`er100_output/pnps_stage2_trial_01/r2/`、`user_test/pnps_stage2_hr7_listen_02/`、`er100_*_r2_*.py`。commit 3a0891f1f/861bd4e05。
- 証拠: 現行TTS独立30 segment: HRプロキシ25→新arm PASS 0(`r2/agg.json arm_tables.t1`)、TTS実誤読疑い18/25、判定側天井6/25(24%)。負例29本誤PASS 0/29(全arm)。Khaite kite 8事象NG維持。Production/Ledger/HR queue/Store不変(`r2/protect_*.json`)。費用63.55(`r2/paid_calls.jsonl`)。
- 一致・不一致: ハード基準=充足。効果基準40%=未達。主因の特定(TTS実誤読)=証拠あり。
- 判定: ACCEPTED(第2巡として)。判定整合: 重大NG=なし/主因=現行TTS(Aoede/PD06)の実誤読+受理集合が空の語/是正対象=TTS入力側(本委任でTrial)/STOP理由=なし/提示=なし。
- QDC: 改善見込み=中〜高(負例で綴り替えにTTSが追従した事実、第1巡Charon設定でKhaite「Kate」2/2)。費用=Trial累計79.09。次の一手=本委任。

## Fableの事前整理(再照合すること)
- 対象語と供給可否(v4-5: TTSへ供給してよいのはOFFICIAL/ACTUAL_USE階層のみ。ESTIMATEDは不可):
  - Khaite: 「kate」(Nylon 1媒体=B階層)。Meink: 「MEENK」(Wikipedia本人記事=A相当)。Altuzarra: 「ahl-too-ZAH-rah」(媒体5件一致=B階層)。Canelé: 辞書サイト1件(弱い、B未満)。Toteme/Zabelina/Melos: 取得なし=**供給不可(Trialでも供給しない)**。
  - 本Trialでは**A階層とB階層を分けたarm**で測る(B階層の供給可否はユーザー判断事項。Trial内比較のみ)。Canelé・取得なし3語は「供給不可のためHR維持」として件数に残す。
- 読み制御の方法(既存機構の踏襲): `er003_v1_n3_01_tts_generate.py:990-999`の`tts_safe_name_pronunciation_en`(Reicher→Riker: TTS入力の綴り置換、ASR比較対象も置換後テキスト)と同じ考え方で、Trial内では(i)綴り置換(respelling: Khaite→Kate、Meink→Meenk、Altuzarra→Altoozarra等。置換先はCMU収録語または明確に読める綴りを優先し、第2巡の負例で「TTSが綴りに追従する」ことを確認済み)、(ii)可能ならTTS側のphoneme/pronunciation指示(Gemini TTSのstyle prompt内で読みを指示する方法。対応可否を確認し、使えるなら第2arm)。各語×各方法×2 take、第2巡と同じ実本文segment(Khaite s09/s12/s16等、Meink、Altuzarra s17、「Melos said.」は供給不可のため対照として無供給1本のみ再利用可=追加生成不要)。
- 判定: 現行Production判定(Primary/Secondaryの正綴り一致=プロキシ)と、第2巡の新arm(N4/N5)を両方適用。読み制御後の比較対象テキストは「置換後の綴り」と「元の綴り」の両方で判定し、どちらでPASSになるかを記録(Reicher方式は置換後テキストで比較)。4エンジン(OpenAI/Azure/Whisper small・medium)の転写を保存。**安全の確認**: 誤った読みを供給した対照(各語1本、例 Khaite→「Kite」)で、置換後テキスト比較では「PASS」になってしまうことを明示的に示す(=この方式の安全性は取得発音の正しさに全面依存する、という事実の記録)。したがって供給元はA階層(引用実在確認済み)に限る案と、B階層まで許す案のリスク差を表にする。
- 効果の測り方: 第2巡のHRプロキシ25(現行TTS take1)のうち、対象語(Khaite/Meink/Altuzarra)に起因するHRが何件で、読み制御後に何件がPASS(現行判定)になるか。語別・階層別。7語全体に対する削減率も出す(供給不可の語は削減0として)。
- 試聴ページ03: 読み制御後の全音声(期待語・供給した読み・根拠と階層・各ASR文字列・判定)+無供給の同一segment対照。Gate 7。

## 実行内容
1. 開始前チェック(22節)→`STAGE2_TRIAL_DESIGN_03.md`(arm・対照・合格基準[A階層供給でPASS化した件数/誤読対照の挙動/Production無変更]・見積)。STOPセンチネル・残予算。
2. 供給候補の確定(0円): 第1巡`o1_free_sources.json`/`r0_extractions.json`の取得結果から、語ごとの読み・出典・階層・引用実在確認(V1')の有無を表に。
3. 生成(有料): 対象3語×segment×{respelling, (phoneme指示が可能なら)指示}×2 take+誤読対照各1本。Whisperは全音声、OpenAI/Azureは窓(第2巡と同じ)。
4. 判定replay(0円)→集計→試聴ページ03→`STAGE2_TRIAL_RESULT_03.md`(ユーザー§7順。7・8はFable欄。限界: TTS確率性・標本小・B階層の扱いは未承認)。
5. SSOT: `OPEN_ITEMS.md` OPEN-441をStage 2=`TRIAL_R3_DONE_PENDING_FABLE`へ(履歴1文)。`REPORT_LEDGER.md`1行。`OPUS_FINDINGS_LEDGER.md` OF-PNPS-S2R-10を`TRIALED`へ。T-0: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02_委任_09.md`(Nは`FABLE-DELEGATION-MARKER: PNPS-STAGE2-TRIAL-R3-委任_09-20261022`を含むAgent tool_useの通番、272前後。先頭行で一致確認)。
6. commit→push→到達確認。`ACTIVE_TASK.md`固定ヘッダ。`RESULT_PACKET_PNPS9.md`。

## 事前指定Read/Grep
- Read: `STAGE2_TRIAL_RESULT_02.md`(§1〜§3・次の一手)、`er100_output/pnps_stage2_trial_01/r2/agg.json`(arm_tables.t1の語別内訳)、`r2/plan.json`(segment本文)、`er100_pnps_stage2_trial_01_r2_{gen,replay,page}.py`(流用元)、`er003_v1_n3_01_tts_generate.py:985-1000`、第1巡`o1_free_sources.json`/`r0_extractions.json`。
- Grep: Gemini TTSの読み指示の可否=`pronunciation|phoneme|IPA` in `er006_*tts*.py`/`er019_family_x_style_profile_01.py`(既存の指示例があれば記録)。

## 実行コマンド全文
実行した全コマンドを実値で記録(`.venv\Scripts\python.exe er100_pnps_stage2_trial_01_r3_*.py ...`)。secret scan。

## SSOT追記文
- OPEN-441履歴: `2026-10-22 Stage 2 第3巡(委任_09、TTS側読み制御): 対象<語>×<arm>、HRプロキシ<対象語分 h>→読み制御後PASS<p>(A階層<a>/B階層<b>)、誤読対照は置換後比較でPASS化=方式の安全性は供給発音の正しさに依存、費用JPY<x>(累計<y>/300)。Status=TRIAL_R3_DONE_PENDING_FABLE。`
- REPORT_LEDGER: `- 2026-10-22 | PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02 委任_09 | Stage 2 第3巡(TTS側読み制御Trial): <結果1行>、費用JPY<x>。TRIAL_R3_DONE_PENDING_FABLE。`

## Git
- SSOT編集権: `OPEN_ITEMS.md`(OPEN-441行のみ)・`REPORT_LEDGER.md`・`OPUS_FINDINGS_LEDGER.md`(OF-PNPS-S2R-10行のみ)。
- 明示add: `er100_pnps_stage2_trial_01_r3_*.py`、`er100_output/pnps_stage2_trial_01/r3/**`(wav除く)、`docs/research/PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02/STAGE2_TRIAL_{DESIGN,RESULT}_03.md`、`user_test/pnps_stage2_hr7_listen_03/**`、delegation_log、SSOT3ファイル。
- commit例: `PNPS Stage 2 委任_09 第3巡: TTS側読み制御Trial(A/B階層分離・誤読対照)、HR<h>→<p>、費用JPY<x>、Production/Ledger/HR queue無変更`。

## 報告(RESULT_PACKET_PNPS9.md)
ユーザー§7順(7・8はFable欄)+語別・階層別・arm別表/誤読対照の結果/供給不可3語の扱い/7語全体の削減率/試聴URL+Gate 7/費用(出典)・Trial累計・日次累計/量産単価影響(読み制御のAPI追加0の根拠、Ledger供給の実装見込み)/RESULT_PACKET 4行/実行コマンド/raw URL。`判断候補`(B階層供給の可否、Ledger→TTS供給の仕様化)はFable向けに整理のみ。
FABLE-DELEGATION-MARKER: PNPS-STAGE2-TRIAL-R2-委任_08-20261022

# 委任(PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02 委任_08: Stage 2 Trial 第2巡[Step C=Opus案1]。現行TTSでの再測定(実本文30 segment)+負例拡充(≥28本)+判定経路の改善arm(語境界子音縮約/弱化母音許容/2出所支持/ASR側OOVへのG2P)をTrial内で比較。Guardrail JPY80(Trial累計Cap300の残284内)。Production/正式Ledger/HR queue/Store無変更)

## 管理ID
PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02 委任_08(OPEN-441。並行agentなし。共有ファイル編集は`git status`→該当行再Grep→自分の行だけ→即add+commit)。

## 性質/到達上限Status/禁止事項
- 性質: Trial第2巡(ユーザー指示§4 Step C。取得・推定・評価方法のTrial内改善は承認範囲内。新しい自動PASS条件はTrial内比較に留め、Productionへ反映しない)。到達Status: `TRIAL_R2_DONE_PENDING_FABLE`(最終分類はFable)。
- Opus Gate: Step B実施済み(本委任の根拠=OF-PNPS-S2R-01〜10、下記Fable採否)。第2巡は同レビューの推奨案1の実行。
- 修正範囲(11-8): 範囲内=Trial専用`er100_*`の追加/改修、`docs/research/PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02/STAGE2_TRIAL_*`、`er100_output/pnps_stage2_trial_01/r2/`、試聴ページ`user_test/pnps_stage2_hr7_listen_02/`。範囲外=Production経路(`er006_*`/`er078_*`/`er063_*`/`er003_*`/`er097_*`配線部)・正式Ledger/negative_cache・HR queue・Master Audio Store・Validator・Prompt・モデル構成の変更。**TTS再生成はProduction runnerを経由せず、TTSクライアント関数を直接呼び(Production と同じ音声/style設定を読み取って使用し、設定値を記録)、Store/HR queue/attempt_historyへ書き込まない**(OF-S2R-02の「開発runがHR件数を水増し」懸念を本Trialで再現しないため)。
- 時間見込み(8-X): 全体約5〜6時間。並列: (A)30 segment×2本+負例≥28本のTTS生成→4エンジン書き起こし(実行待ち中心)と、(B)新arm(S2R-03/04/05)の実装・保存データreplay(0円)を並列。合流後に新規音声へ全armを適用→集計→試聴ページ→報告。
- 費用/日次: 当日(JST 2026-10-22)既使用 約JPY686(出典: RESULT_PACKET_B3RD8 275.35+KP6M1 206.60+KPMG1 188.28+PNPS7 15.54)。残 約JPY314。本委任見積 約JPY60(約90本×実測0.65円/本[TTS 0.185+OpenAI ASR 0.123+Azure 0.34、paid_calls実績]+推定LLM少額)。Guardrail(T-3) **JPY80**(到達だけで自動STOPしないが、超過見込みで有料呼出を止めて報告)。Trial累計Cap300の残284。承認区分: C。単価出典を記録(OpenAI ASR秒換算は上限見積のまま明記)。
- 禁止: `git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f。secret_scan hits=0。push=`git push origin HEAD:main`。ACTIVE_TASK/RESULT_PACKETはgitignore。SSOT全文読込禁止。他agentの未commit差分を混ぜない。有料runの再起動禁止、STOPセンチネル確認後に開始。`TTS_EXECUTION_MODE=STANDARD`。既存音声の変更禁止。推定一致だけで正解と断定しない。LLMの`official`自己申告をOFFICIAL区分へ流入させない(コード+testで保証、OF-S2R-08)。Primaryが正しい綴りを返したことを判定根拠に数えない(OF-S2R-06)。

## 前委任(委任_07)の受入記録(Gate 7、Fable記入)
- 当初目的(ユーザー原文逐語、`docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02_STAGE2-TRIAL-GO_USER.md`): 「本Trialの最終目的は、発音情報の取得方法を増やすことではなく、正しい音声を安全に自動合格させ、Human Reviewを実際に削減すること。」「初回Trialの効果が限定的・ゼロだった場合、それだけを理由に終了しないこと。」
- 最終成果物: `STAGE2_TRIAL_RESULT_01.md`/`STAGE2_TRIAL_DESIGN_01.md`、`er100_output/pnps_stage2_trial_01/`、試聴ページ`user_test/pnps_stage2_hr7_listen_01/`。commit 7e25586be/778a0e7d2/2f477f2f3。
- 証拠: HR事象58(延べ61、独立segment 30)→新方式PASS_WITH_WARNING 1(音声未保存)/NG 10/HR維持47(`replay_result.json`、`stepA_aggregates.json`)。負例6本誤PASS 0(`p2_results.json`)。取得4語/推定収束2語(`o1_free_sources.json`、`r0_extractions.json`、`est_e2_e3.json`)。費用JPY15.54(`paid_calls.jsonl`)。
- 一致・不一致: 母数3区分・誤PASS 0・Step A原因分析・試聴ページ=一致。HR削減(目的の本質)=未達(第1巡)。P2がHR主因segment「Melos said.」を再現していなかった(Opus OF-S2R-02)。
- 判定: ACCEPTED(第1巡として。改善ループ継続=本委任)。判定整合: 重大NG=なし/主因=受理集合が空(44/58)+ASR綴り経由の判定不能の直列/是正対象=判定経路(Trial内)/STOP理由=なし/提示=なし。
- QDC: 目的=HR削減/試行=第1巡/原因仮説=上記(証拠はstepA)/結果=HR 58→57(未確証)/改善見込み=中(Opus案1で0円改善+約60円の再測定)/費用=15.54/次の一手=本委任。

## Opusレビュー(Step B)のFable採否(OPUS_FINDINGS_LEDGERへ記録すること)
- OF-PNPS-S2R-01(主因の補正: 候補集合が空×ASR綴り経由の直列)=採用。第2巡は①②を同時に扱う。発音取得の改善は後回し。
- S2R-02(測定単位・現行TTSでの再測定・「Melos said.」再現)=採用。あわせて範囲外事項2点を**0円の事実確認として本委任で測る**: (a)同一本文・同一音声の再判定で人間承認が再利用されているか(HR queue 87〜113行のrun種別・時刻・同一segmentの反復回数を集計、approvalの再利用機構の有無をコードで確認)、(b)開発用runがHR件数に混入しているか(run id/dirで区分)。判断・修正はしない(報告のみ)。
- S2R-03(語境界の同一子音の縮約=degemination)=Trial arm採用。負例(語末子音の真の脱落)で検証。
- S2R-04(推定受理条件の緩和: (a)子音・強勢母音は厳密、弱化母音は同一視、(b)N-best・2出所以上の支持)=Trial arm採用。拒否条件維持(いずれかのエンジンで子音/強勢母音不一致→拒否、Primary正綴りは根拠にしない、取得根拠と矛盾する推定は捨てる)。Production採用はユーザー判断。
- S2R-05(ASR側OOVへのG2P適用+アクセント記号正規化)=Trial arm採用。推定側と判定側の両方でG2Pを使う誤りの重なりは負例で検証。
- S2R-06(PrimaryがPrimary単独PASS経路で誤発音を正綴りに寄せるProductionリスク)=**事実の追加測定を本委任で実施**: 拡充負例(≥28本)のうちPrimaryが正しい綴りを返した割合を記録(標本2→≥28)。Production変更はしない(Fableが結果を見てOPEN項目化を判断)。
- S2R-07(ASRが最寄り実在語へ寄せた母音1つ差はNGでなく判定不能)=Trial arm採用(誤NG記録の回避。HR件数は不変)。
- S2R-08(LLM official自己申告を無視)=採用(コード+test)。
- S2R-09(負例拡充: 7語×{子音置換/強勢母音置換/音節脱落/語末子音脱落}各≥1本=≥28本。TTSが実際に誤読したことを2エンジン以上の逸脱で確認、確認できないものは負例から除外。0/28でも95%上限約10%を開示)=採用。
- S2R-10(代替案評価)=(1)TTS側置換は2次案・本巡で実装しない(既存`tts_safe_name_pronunciation_en()`の配線状況のみGrepで記録)、(2)wav2vec2音素CTCは案2として保留(本巡で導入しない。案1の結果でFable判断)、(3)ASR合意条件化は非推奨=不採用。

## 実行内容(Opus案1)
1. 開始前チェック(22節): ユーザー指示§2〜§7+本委任の要求列挙→`STAGE2_TRIAL_DESIGN_02.md`(新規、第2巡設計: arm定義・拒否条件・負例設計・合格基準・見積)。STOPセンチネル・残予算。
2. (B)0円先行: 新arm実装(`er100_pnps_stage2_trial_01_arm_r2.py`等): degemination、弱化母音クラス同一視(強勢位置は取得/推定候補から)、推定器N-best(g2p_enの候補が1つなら`gpt-6-luna`にN-best≤3を出させる。費用小・計上)、2出所支持、ASR側OOVのG2P音素化+アクセント除去、S2R-07判定不能振分け、official無視test。保存データ(HR事象33行の保存wav・attempt 86本・P2 23本)へV4/EXT/新armをreplayし差分表。
3. (A)有料: HR事象30 segmentの実本文(「Melos said.」を含む。Family Zの本文はZの現行voice/style、XはXの現行設定)を現行TTSで各2本=60本、負例≥28本(S2R-09設計)。4エンジン(OpenAI Primary/Azure/Whisper small・medium)で書き起こし。Store/HR queue/attempt_history非書込を確認(実行前後でファイル行数不変をassert)。
4. 全armを新規音声へ適用→集計: 現行TTSで生成した独立segmentのうち「現行Production判定でHRになるもの」の件数(現行基準の再現)と、新armでPASS_WITH_WARNINGへ変わる件数・割合。保存データ(旧TTS)の件数と分けて報告。拡充負例の誤PASS(arm別)。Khaite「kite」8事象のNG維持。S2R-06測定(Primary正綴り率)。S2R-02(a)(b)の事実確認。
5. 合格基準(Opus案1、Fable承認): ハード=拡充負例でPASS 0・Khaite kite 8事象NG維持・Production/正式Ledger/HR queue/Store無変更。効果=現行TTSでHRになる独立segmentの40%以上がPASS_WITH_WARNINGへ。正例確認=PASS_WITH_WARNINGになった音声(≤20本なら全数)を試聴ページ02に載せる(期待語・各ASR文字列・根拠区分・arm別判定・理由)。
6. 試聴ページ`user_test/pnps_stage2_hr7_listen_02/index.html`(新規音声のPASS_WITH_WARNING全数+負例のうち判定が割れたもの+「Melos said.」の全サンプル)。Gate 7(Pages 200・Playwright再生・console 0)。
7. `STAGE2_TRIAL_RESULT_02.md`: ユーザー§7の1〜8順(1=HR削減件数を「現行TTS実測」と「保存データ」で分けて; 5=第1巡の原因・Opus指摘・改善内容・再Trial結果; 7・8はFable欄)。限界開示。STOP判定材料(Opusの(a)(b)(c)に該当するか)。
8. SSOT: `docs/pm/OPUS_FINDINGS_LEDGER.md`にOF-PNPS-S2R-01〜10を追加(上記採否をFABLE_DECIDED、本巡で実施したものはTRIALED)。`OPEN_ITEMS.md` OPEN-441をStage 2=`TRIAL_R2_DONE_PENDING_FABLE`へ(履歴1文)。`docs/pm/REPORT_LEDGER.md`1行。DECISION_LOG/CURRENT_SPEC/UDRは書かない。T-0: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02_委任_08.md`(Nは`FABLE-DELEGATION-MARKER: PNPS-STAGE2-TRIAL-R2-委任_08-20261022`を含むAgent tool_useの通番、270前後。先頭行で一致確認)。Opusレビュー全文は`docs/research/PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02/OPUS_REVIEW_STAGE2_STEPB_01.md`へ保存(本委任文の「Opusレビュー(Step B)のFable採否」節と、Fableが別途渡す全文がない場合は所見ID・要旨を本委任文から転記し「要旨」と明記)。
9. 段階commit→push→到達確認。`docs/pm/ACTIVE_TASK.md`固定ヘッダ。`docs/pm/RESULT_PACKET_PNPS8.md`。

## 事前指定Read/Grep
- Read: `docs/research/PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02/STAGE2_TRIAL_RESULT_01.md`(§2〜§5)、`STAGE2_TRIAL_DESIGN_01.md`(arm定義)、`er100_output/pnps_stage2_trial_01/{stepA_aggregates.json,p2_results.json,est_e2_e3.json}`、`er100_pnps_stage2_trial_01_{replay,p2,est,page}.py`(流用元)、`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl:87-113`。
- Grep: `tts_safe_name_pronunciation_en` in `*.py`(配線状況の記録のみ)、`human_approved|approval_reuse|reuse_human` in `er006_*.py`(S2R-02(a))、Family Z TTS設定=`er063_family_z_audio_01.py`(voice/style定数)、Family X設定=`speech_metadata_flash_lite|fx_20261017` in `er019_*.py`/`er006_*.py`。

## 実行コマンド全文
実行した全コマンドを実値で記録(`.venv\Scripts\python.exe er100_pnps_stage2_trial_01_r2_*.py ...`)。secret scan `.venv\Scripts\python.exe tools/secret_scan_01.py --staged`。

## SSOT追記文
- OPEN-441履歴: `2026-10-22 Stage 2 第2巡(委任_08、Opus Step B案1): 現行TTS再測定<独立segment n>中 現行HR<h0>→新arm PASS_WITH_WARNING<p>(<x>%)、保存データ<旧>、拡充負例<m>本 誤PASS<0/件>、Primary正綴り率<r>、費用JPY<x>(累計<y>/300)。Status=TRIAL_R2_DONE_PENDING_FABLE。`
- REPORT_LEDGER: `- 2026-10-22 | PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02 委任_08 | Stage 2 第2巡(Opus案1): 現行TTS再測定+負例拡充+新arm、HR<h0>→<p>、誤PASS<n>、費用JPY<x>。TRIAL_R2_DONE_PENDING_FABLE。`

## Git
- SSOT編集権: `OPEN_ITEMS.md`(OPEN-441行のみ)・`docs/pm/REPORT_LEDGER.md`・`docs/pm/OPUS_FINDINGS_LEDGER.md`(OF-PNPS-S2R-行のみ)。他SSOT不可。
- 明示add: `er100_pnps_stage2_trial_01_r2_*.py`(+既存er100の改修分)、`er100_output/pnps_stage2_trial_01/r2/**`(wavはmp3コピーのみcommit、サイズ注意)、`docs/research/PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02/{STAGE2_TRIAL_DESIGN_02,STAGE2_TRIAL_RESULT_02,OPUS_REVIEW_STAGE2_STEPB_01}.md`、`user_test/pnps_stage2_hr7_listen_02/**`、`docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02_委任_08.md`、上記SSOT3ファイル。
- commit例: `PNPS Stage 2 委任_08 第2巡(Opus案1): 現行TTS再測定30seg×2+負例<m>本+新arm(縮約/弱化母音/2出所/ASR側G2P)、HR<h0>→<p>、誤PASS<n>、費用JPY<x>、Production/Ledger/HR queue無変更`。

## 報告(RESULT_PACKET_PNPS8.md)
ユーザー§7の1〜8順(7・8はFable欄)。加えて: 開始前チェック対応表/arm別集計表(保存データ・P2・新規をそれぞれ、現行基準HR→各arm PASS_WITH_WARNING/NG/判定不能、負例誤PASS)/Melos said.の結果/S2R-06測定値/S2R-02(a)(b)事実/試聴URL+Gate 7/費用実測(出典)・Trial累計・日次累計/STOP判定材料(Opus (a)(b)(c))/RESULT_PACKET 4行/実行コマンド/raw URL。`判断候補`表記。推測で発音正否を断定しない。
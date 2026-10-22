FABLE-DELEGATION-MARKER: PNPS-STAGE2-TRIAL-R1-委任_07-20261022

# 委任(PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02 委任_07: Stage 2 Trial 第1巡[O0→O1→必要時P1/P2]+Step A原因分析。ユーザー承認済み(累計Cap JPY300、本巡Guardrail JPY150)。Trial専用経路限定。Production/正式Ledger/判定基準の変更禁止)

## 管理ID
PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02 委任_07(OPEN-441、UDR #142=本指示で回答済み扱い[Trial GO・Cap300・G2PはTrial内可])。並行agentなし。共有ファイル編集は`git status`→該当行再Grep→自分の行だけ→即add+commit。

## 性質/到達上限Status/禁止事項
- 性質: Trial(Stage 2 第1巡)。到達Status: 本委任では`TRIAL_R1_DONE_PENDING_FABLE`まで(最終分類`VALIDATED`/`REJECTED`/`USER_DECISION_REQUIRED`はFable。効果が小さい場合のOpus独立レビュー[ユーザー指示Step B]はFableが手配するので、あなたはStep Aの原因分析と証拠を揃えて返す)。
- Opus Gate: 計画v4はOpus S2-01〜09レビュー済み(OF-PNPS-S2)。本巡は同計画の実行で新規レビュー不要。Step Bは結果次第でFableが実施。
- 修正範囲(11-8): Trial内では「発音候補の取得・推定・評価方法」を改善してよい(ユーザー指示Step C)。範囲外=Production経路(`er006_*`/`er078_*`/`er097_*`のProduction配線部分)・正式Ledger(`er006_output/pronunciation_ledger_01/ledger.json`・negative_cache)・Validator・Prompt・モデル構成・Phrase Listの変更、Trial成果の正式Ledger登録。
- 時間見込み(8-X): 全体約4〜6時間。O0(保存データ再生、0円)60分 / 環境(G2P導入・Whisper既存)30分 / O1(無料源HTTP)45分 / P1(有料調査、必要語のみ)30分 / 推定+自動判定replay 60分 / P2(実TTS負例・正例、必要時)30分 / 試聴ページ・報告・SSOT 60分。並列: O1とG2P導入・replay基盤は並列。直列理由: P1/P2はO0/O1の結果(未解決語の確定)に依存、有料呼出は見積確認後。
- 費用/日次: 当日(JST 2026-10-22)既使用 約JPY482(出典: RESULT_PACKET_B3RD8 275.35+KP6M1 206.60)。残 約JPY518。本委任Guardrail(T-3) **JPY150**(Trial累計Cap JPY300のうち第1巡分。到達だけで自動STOPしないが、超過見込みで有料呼出を止めて報告。第2巡の残枠を残す)。内訳目安: O0/O1/R=0、P1(LLM+web調査)≤約60、P2(実TTS+ASR)≤約50、予備。承認区分: C(ユーザー承認済みTrial・Cap内)。単価は出典のあるもののみ(未確認は未確認と明記し見積に入れない)。
- 禁止: `git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f。commit前`.venv\Scripts\python.exe tools/secret_scan_01.py --staged` hits=0。push=`git push origin HEAD:main`。ACTIVE_TASK/RESULT_PACKETはgitignore(force-add禁止)。SSOT全文読込禁止。他agentの未commit差分を混ぜない。有料runの再起動禁止(26節)、STOPセンチネル確認後に開始。`TTS_EXECUTION_MODE=STANDARD`(P2のTTSは同期)。既存HR音声の再生成・変更禁止(コピーは可)。外部課金・契約変更(Perplexity枠購入等)禁止。推定発音とTTS音声の一致だけで「正解」と断定しない(ユーザー§2)。

## ユーザー原文(2026-10-22、逐語。`docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02_STAGE2-TRIAL-GO_USER.md`へ本文無改変で保存、文字数・sha256を記録)
---
# Claude Code指示：固有名詞発音 Stage 2 Trial実施

## 1. 目的・承認範囲

**Stage 2 Trialの実施を正式承認する。予算上限は累計300円（JPY）。**

目的は、正しい発音の音声がASRの認識限界や発音情報不足によってHuman Reviewに回る問題を減らし、品質を維持したまま量産を効率化すること。

対象はFamily X/Z共通の固有名詞発音取得・判定方式。

- Status：`TRIAL_APPROVED`
- 到達可能Status：`VALIDATED`／`REJECTED`／`USER_DECISION_REQUIRED`
- Production採用・配線は未承認
- 既存Production仕様・Ledgerは変更しない

## 2. Trialの基本方針

Stage 2計画v4を出発点に、以下を検証する。

1. **正しい発音をネット上から取得する方法**
   - 公式発音
   - 英語圏での実際の呼ばれ方
   - 信頼できる辞書・発音情報

2. **ネット上で正しい発音を取得できない場合の合理的な発音推定**
   - G2P（綴りから発音への変換）
   - 低コストLLMによる推定
   - 複数の推定結果や根拠を比較し、妥当な発音候補を選ぶ

3. **取得・推定した発音を使った自動判定**
   - 既存Human Review音声を用いて検証する。
   - 正しい発音を不当にNGとしない。
   - 明確な誤発音はPASSさせない。
   - 公式発音・実使用発音・推定発音の根拠区分を維持する。

推定発音と音声の一致だけで無条件に正解とすることは禁止する。

## 3. 対象と成果測定

既存Human Reviewに到達した辞書外7語を中心とする。

`Toteme / Khaite / Altuzarra / Zabelina / Canele / Meink / Melos`

保存済みの音声・ASR・Ledger・発音調査履歴を再利用する。

**必須測定項目**

- 対象音声の母数とHuman Review到達件数
- 実際の発音不良とASR誤認識の区別
- 発音情報を取得・推定できた語数
- 新方式で自動PASSに変更できる件数
- 明確な誤発音を誤PASSした件数
- 改善前後のHuman Review件数
- 量産単価への影響

延べlookup件数と独立音声数を混同しないこと。

必要に応じて音声を試聴できるページを用意し、ユーザーが発音を確認できるようにする。

## 4. 改善ループ【重要】

**初回Trialの効果が限定的・ゼロだった場合、それだけを理由に終了しないこと。**

次の改善ループを実行する。

### Step A：原因分析

候補が採用されなかった理由を語・音声単位で分類する。

例：

- Web上に発音情報が見つからない
- 情報はあるが抽出できない
- 出典の信頼性確認で落ちる
- IPAなどを音素に変換できない
- G2PとLLMの推定が一致しない
- 複数の合理的な発音候補を扱えない
- 音素照合で不合格になる
- 実際にTTSが誤発音している

原因を推測だけで決めず、具体的な証拠を残す。

### Step B：Opus独立レビュー

効果が小さい場合は、**必ずOpusによる独立レビューを実施**する。

レビューでは次を検討する。

- 根本原因の特定は正しいか
- 発音取得方法を改善できないか
- 合理的な読み方の推定条件が過度に厳しくないか
- 候補が不必要に捨てられていないか
- 別のアプローチの方が有効ではないか
- 品質・費用・速度のバランスを改善できないか

既存計画v4の方法に固執しないこと。

### Step C：改善・再Trial

原因分析とOpusレビューに基づき、最も改善見込みの高い方法を選んで再Trialする。

- 承認済み品質条件は維持する。
- 発音候補の取得・推定・評価方法はTrial内で改善してよい。
- 自動PASSの新条件はTrial内で比較検証するにとどめ、正式Productionに反映しない。
- 有効な改善が確認できた場合は、必要十分な品質に到達した時点で終了する。
- 効果が小さい場合は原因・方法を見直し、残予算と改善見込みから継続を判断する。

**単に「改善件数0」「効果なし」と報告して終了することは禁止。**

ただし、原因分析と代替方式の検討により合理的な改善見込みがないと確認された場合、または予算・安全上限・承認境界に達した場合はSTOPし、根拠を報告する。

Trial回数だけを理由にSTOPしない。

## 5. 費用・速度

**累計予算上限：300円。**

- O0など既存保存データによる無料検証を最大限活用。
- 有料検索・LLM・TTSは必要な部分に集中する。
- 同じ失敗を無意味に繰り返さない。
- 独立作業は並列化する。
- 不要な日付分割・待機・少額費用ごとの承認要求は禁止。
- 使用済み金額・残予算を記録し、予算内で自律的に改善ループを回す。

Perplexityが401で使用できない場合は、利用可能な無料源や承認範囲内の代替手段を先に検討する。外部課金・契約変更が必要なら、勝手に実施しない。

## 6. 品質・STOP条件

以下を必須とする。

- 明確な誤発音の新規誤PASS：0件
- 発音根拠の虚偽登録：0件
- 既存Production判定の無断変更：0件
- Trial成果の正式Ledgerへの無断登録：0件
- 承認済み仕様・安全条件の変更は、Production採用前にユーザー判断

不具合・軽微な技術課題は委任範囲内で自律解決する。

## 7. 最終報告・Closeout

技術報告の羅列ではなく、次の順序で簡潔に報告する。

1. **結論：Human Reviewを何件削減できたか**
2. 対象母数・現行HR件数・改善後HR件数
3. 誤PASS・誤NGの結果
4. Web取得と合理的発音推定、それぞれの成功・失敗理由
5. 初回で効果が限定的だった場合の原因、Opus指摘、改善内容、再Trial結果
6. 使用総額・量産単価への影響
7. Fable独立評価、Trial終了Status
8. Production採用に必要なユーザー判断

結果が`VALIDATED`でもProduction配線は開始しない。

Trial成果物・評価証拠・Opusレビュー・Fable評価をRepoに記録する。

**本Trialの最終目的は、発音情報の取得方法を増やすことではなく、正しい音声を安全に自動合格させ、Human Reviewを実際に削減すること。**

品質を守りながら、予算300円の範囲で自律的に問題解決まで進めてください。
---

## Fableの事前確認(再照合し、ズレがあれば開始前に報告)
- 出発点=計画v4(`docs/research/PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02/PLAN_01.md` v4節・`PLAN_SUMMARY_01.md`)。ユーザー指示で広がった点: (a)G2PをTrial内で導入してよい(`g2p_en`等をvenvへ。Production依存にはしない)、(b)Step Cで取得・推定・評価方法をTrial内で改善してよい、(c)Perplexity 401時は無料源→承認範囲内の代替(例: OpenAI Responses APIのweb_search tool。単価の出典が確認できる場合のみ有料利用)。(d)「推定一致だけで正解としない」=v4の`ESTIMATED/WARN`区分と、独立2推定(G2P+低コストLLM)の一致要件を維持。
- 対象7語の保存データの所在(あなたが特定・記録): HR queue `er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`(+Family Z側のHR queueがあれば)、`er011_output/attempt_history.jsonl`、Stage 1効果測定`stage1_effect_measure_0[12]*.txt`(HR到達span12種・一般語除外後、CMU未収録7種)、Ledger`ledger.json`(読み取りのみ)、PNEP調査履歴`er089_output/proper_noun_en_pronunciation_trial_01/`、音声ファイル(HR queue行が指すwav/mp3。無いものは「未保存」)。**母数は独立音声数とsegment数と延べlookup数を分けて数える**。
- 既存部品の再利用: 音素比較=`er094_multiword_homophone_01.py`のCMU比較関数/`er093`のproto(ストレス無視)、Stage 1=`er097_pronunciation_supply_stage1_01.py`(階層・否定記録の純関数)、Whisper=ASR3Wのローカルrunner(faster-whisper small/medium)、IPA→ARPAbet=M1の決定論変換器(`er006_m1_multi_candidate_01.py`付近)。
- 「実際の発音不良とASR誤認識の区別」: 機械的には(i)Primary/Secondary/Whisper(small/medium)の転写一致度、(ii)取得/推定発音との音素照合、で区分**候補**を出す。最終的な正否は人間の耳でしか確定しないため、7語の独立音声すべてを載せた試聴ページ(`user_test/pnps_stage2_hr7_listen_01/index.html`、各音声に期待語・各ASR文字列・取得/推定発音・新方式の判定[PASS_WITH_WARNING/NG/HR維持]と理由を表示)を作り、Pages 200・再生検証(Playwright、`er099_byus_kp_asr_listen_play_verify_01.py`の流用可)。音声は再生成せずコピー。
- 新方式の自動判定(Trial内比較のみ): v4の受理条件(OFFICIAL/ACTUAL_USE=A階層→PASS、ESTIMATED=独立2推定の共通部分と一致→PASS_WITH_WARNING、不一致/音素差・脱落→NG、推定不成立→HR維持)を保存音声のASR転写に再適用(replay)。負例(明確な誤発音)での誤PASS 0を必ず検証: 保存負例が無ければP2で3語×{合理的な読み1+明確な誤発音2}の実TTS(≈46円)を作る(v4どおり)。
- P1(有料調査)は O1で取れなかった語かつ本当に必要な語に限定(≤5語)。モデルは最新上位原則(25節)=`gpt-6.1-sol`+web_search(単価出典を`pricing_snapshot.json`/er009で確認、無ければ`gpt-6-luna`+web_searchで同条件を確認)。出典URL・引用・発音表記・出典種別を保存(V1'の弱い照合=ページ取得で名称と発音表記の出現確認、読み取り専用・サイズ上限・タイムアウト)。虚偽登録0=引用が確認できないものはOFFICIALにしない。
- Step A原因分析: 7語×独立音声ごとに、ユーザー例示の分類(見つからない/抽出不可/出典信頼性で落ちる/IPA変換不可/G2PとLLM不一致/複数候補扱えず/音素照合不合格/TTS実誤発音[候補])を証拠(URL・転写・音素列・diff)付きで表にする。効果が小さい場合に備え、「改善見込みの高い代替案」を事実ベースで最大3つ列挙(採否はFable/Opus)。
- 計画v4のO0必須測定(保存データ上、HR到達segmentのうち警告付きPASSへ変わる件数)は実施するが、**0件でもTrialを終了せず**(ユーザー§4)、O1→推定→P1/P2へ進み、Step Aを完了してから返す。

## 実行内容(順序)
1. 開始前チェック(22節): ユーザー§2〜§7の要求を列挙し、設計書`STAGE2_TRIAL_DESIGN_01.md`(同dir新規)のどこで満たすか対応表。STOPセンチネル・残予算・保存データ所在を確認。
2. O0(0円): 母数(独立音声/segment/延べlookup)、現行HR件数、各音声のPrimary/Secondary(保存)+Whisper small/medium(ローカル追加)転写、現行判定の再現。
3. 環境: `g2p_en`(またはphonemizer等、入手できる決定論G2P)をvenvへ導入(導入したパッケージ名・版を記録。Production importには入れない)。
4. O1(0円・HTTPのみ): 7語についてR0無料源(Wiktionary/Wikipedia/辞書サイトの発音欄、公式サイト)から発音表記取得を試行、取得結果とV1'結果を保存。
5. 推定(0円〜低コスト): E1(境界分割)不成立の語にE2(G2P)+E3(低コストLLM=`gpt-6-luna`、費用計上)で独立推定→共通部分→ESTIMATED候補。候補複数は共通部分のみ。
6. P1(有料・必要語のみ)。
7. 自動判定replay: 保存音声の転写に対し新方式で判定、現行HR件数→改善後HR件数、PASS_WITH_WARNINGへ変わった件数、NG件数。
8. P2(有料・必要時): 負例の誤PASS 0検証(保存負例が足りない場合のみ)。
9. 試聴ページ作成+Gate 7検証。
10. Step A原因分析表、量産単価影響(1記事セット当たりの期待追加費用、実測ベース。未測定は未測定)、費用実測(`paid_calls.jsonl`、出典・為替出典)。
11. 成果物: `docs/research/PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02/{STAGE2_TRIAL_DESIGN_01.md,STAGE2_TRIAL_RESULT_01.md}`(RESULTはユーザー§7の1〜8順。5はStep Aまで、7・8はFable欄)、script `er100_pnps_stage2_trial_01_*.py`、証跡`er100_output/pnps_stage2_trial_01/`(wavはコピー、鍵なし)。
12. SSOT: `OPEN_ITEMS.md` OPEN-441をStage 2=`TRIAL_R1_DONE_PENDING_FABLE`へ(履歴1文)。`docs/pm/REPORT_LEDGER.md`1行。`docs/pm/USER_DECISION_REGISTER_01.md` #142を「判断済み(2026-10-22 Trial GO・Cap300・G2P Trial内可、原文=上記USER.md)」へ更新(その行のみ)。DECISION_LOG/CURRENT_SPECは書かない。T-0: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02_委任_07.md`(Nは`FABLE-DELEGATION-MARKER: PNPS-STAGE2-TRIAL-R1-委任_07-20261022`を含むAgent tool_useの通番、266前後。先頭行で一致確認)。
13. 段階commit(O0→O1/推定→replay/P2→ページ/SSOT)→push→到達確認。`docs/pm/ACTIVE_TASK.md`固定ヘッダ。`docs/pm/RESULT_PACKET_PNPS7.md`へ報告。

## 事前指定Read/Grep
- Read: `docs/research/PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02/PLAN_SUMMARY_01.md`(全文、短い)、`PLAN_01.md`のv4節(Grep `v4` で位置特定→該当範囲)、`stage1_effect_measure_02*.txt`、`docs/pm/OPUS_FINDINGS_LEDGER.md`のOF-PNPS-S2-01〜09行、`er097_pronunciation_supply_stage1_01.py:1-80`、`er094_multiword_homophone_01.py`の比較関数(Grep `def `)。
- Grep: `toteme|khaite|altuzarra|zabelina|canele|meink|melos`(-i) in `er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`, `er011_output/attempt_history.jsonl`, `er006_output/pronunciation_ledger_01/ledger.json`, `er089_output/**`, `er026_output/**`/`er063_output/**`(Family Z側、melos)。`web_search` in `er0*.py`(既存のweb検索付き呼出の実装)。`faster_whisper|whisper` in `er08*asr*three*py`/`docs/research/ASR-THREE-WAY-COMPARISON-TRIAL-01/`。

## 実行コマンド全文
- 実行したコマンドを実値でRESULT_PACKETへ記録(script名・引数・モデル名・G2P導入コマンド `.venv\Scripts\python.exe -m pip install g2p_en` 等)。secret scan `.venv\Scripts\python.exe tools/secret_scan_01.py --staged`。

## SSOT追記文
- OPEN-441履歴: `2026-10-22 Stage 2 Trial GO(ユーザー、Cap累計JPY300、G2P Trial内可、改善ループStep A〜C指定)。第1巡(委任_07): 母数<独立音声n/segment m/延べlookup k>、現行HR<h0>→新方式<h1>、誤PASS<0/件数>、取得<語数>/推定<語数>、費用JPY<x>。Step A原因分析済み。Status=TRIAL_R1_DONE_PENDING_FABLE(Opus Step B要否はFable)。`
- REPORT_LEDGER: `- 2026-10-22 | PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02 委任_07 | Stage 2 Trial第1巡(O0/O1/推定/P1/P2/replay/試聴ページ)、HR<h0>→<h1>、誤PASS<n>、費用JPY<x>。TRIAL_R1_DONE_PENDING_FABLE。`

## Git
- SSOT編集権: `OPEN_ITEMS.md`(OPEN-441行のみ)・`docs/pm/REPORT_LEDGER.md`・`docs/pm/USER_DECISION_REGISTER_01.md`(#142行のみ)。他SSOT不可。
- 明示add: `er100_pnps_stage2_trial_01_*.py`、`er100_output/pnps_stage2_trial_01/**`(サイズ大のwavはローカルのみ可・その旨記録)、`docs/research/PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02/STAGE2_TRIAL_*`、`user_test/pnps_stage2_hr7_listen_01/**`、`docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02_{STAGE2-TRIAL-GO_USER,委任_07}.md`、上記SSOT3ファイル。
- commit例: `PNPS Stage 2 委任_07 第1巡: O0母数/O1無料源/G2P+LLM推定/replay判定/P2負例/試聴ページ、HR<h0>→<h1>・誤PASS<n>、費用JPY<x>、Production/正式Ledger無変更`。

## 報告(RESULT_PACKET_PNPS7.md)
ユーザー§7の1〜8順(5はStep Aまで、7・8はFable欄)。加えて: 開始前チェック対応表/母数の3区分/音声ごとの表(語・音声id・各ASR文字列・取得/推定発音と根拠区分・現行判定・新方式判定・理由・区別候補[発音不良/ASR誤認識/不明])/取得・推定の成功失敗理由/Step A原因分類表(証拠付き)/改善見込みの高い代替案≤3(事実ベース)/費用実測(出典・為替)と残枠(300-x)/試聴URL+Gate 7結果/導入パッケージ/RESULT_PACKET 4行/実行コマンド/raw URL。`判断候補`表記(USER_DECISION_REQUIREDラベルはFableのみ)。推測で発音正否を断定しない。
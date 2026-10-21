FABLE-DELEGATION-MARKER: PNMH-TRIAL-RUN-委任_04-20261022

# 委任(PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01 委任_04: Fix済み計画v3に基づくTrial実行[O1→P1]。ユーザーGOあり。Cap JPY50。Trial専用経路限定・Production/Validator/Ledger/Phrase List/モデル構成無変更)

## 0. 運用ルール・並列注意
- 別agentが同時に「ASR 3方式比較Trial #136 Closeout記録」を実行中で、`OPEN_ITEMS.md`(OPEN-438/439/440)・`DECISION_LOG.md`・`docs/pm/USER_DECISION_REGISTER_01.md`・`docs/pm/REPORT_LEDGER.md`・`CURRENT_SPEC.md`へ追記する。共有ファイル編集前に必ず `git status` → 該当行を再Grep → 自分の行だけ編集 → 即 `git add <file>` + commit。`index.lock`は30秒待って再試行。そのagentはOPEN-439を`PLAN_FIXED_ASR_CONFIRMED_WAITING_OPEN440`へ書く可能性があるが、本委任のユーザーGOにより上書きしてよい(Trial開始時に`TRIAL_RUNNING`、終了時に結果ラベル)。
- `git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f 禁止。commit前 `.venv\Scripts\python.exe tools/secret_scan_01.py --staged` hits=0。push=`git push origin HEAD:main`(local `work/post-merge-01`)。`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET_*.md`は一時ファイル(gitignore、force-add禁止)。SSOT全文読込禁止。作業treeの他人の未commit差分(`er0XX_output/*`)を混ぜない。
- 有料runの再起動禁止(PM_GOVERNANCE 26節)。STOPセンチネル確認後に開始。`TTS_EXECUTION_MODE=STANDARD`でTTS(構成音声)を生成(Batch不可、理由=Trialは同期・デバッグ性優先、7-4)。
- 費用: 見積JPY18〜28、**Cap JPY50**(到達だけで自動STOPしないが、超過見込みが出たら有料呼出を止めて報告)。費用は`paid_calls`等の実測ログから出典付きで集計(推定値を費用表に使わない)。

## 1. ユーザー原文(2026-10-22、逐語。`docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01_TRIAL-GO_USER.md` へ本文無改変で保存、文字数とsha256[本文のみ]を記録)
---
## Claude Code指示：多語同音救済計画 — Trial実行GO

### 1. ユーザー決定

ASR 3方式比較Trialが完了し、以下を正式決定した。

- Primary：OpenAI `gpt-4o-mini-transcribe`（現行維持）
- Secondary：Azure Speech STT（現行維持）
- Azure Phrase List重み2.0（現行維持）
- ローカルWhisper：Production導入しない
- Primary／Secondaryの入替なし

これにより、**多語同音救済計画のASR構成確定待ちを解除する。**

### 2. 実行指示

先に検討・Opusレビューを経てFixした「#133 固有名詞英語発音供給＋多語同音救済計画」に基づき、Trialを実行すること。

実行前に、最新版のFix計画・レビュー結果・CURRENT_SPEC・関連する過去Trialとの整合を確認する。

計画がまだ正式にFixされていない場合、または未解決の重要なレビュー指摘がある場合は、Trialを開始せず、その事項だけ報告すること。

**Fix済みで実行条件が満たされていれば、追加承認を待たずTrialを開始する。**

### 3. Trialで確認すること

- `ByUs` ↔ `by us` / `buy us` のような1語対複数語の発音同等性を、正しく救済できるか。
- 原稿側の正しい英語発音を、信頼できる情報から取得・供給できるか。
- 既存の1語対1語の同音判定・各種救済機構を壊さないか。
- 発音が異なるものを誤ってPASSさせないか。
- Family X／Zの共通仕様との整合。
- 処理速度・量産原価への影響。

評価対象・判定基準・予算・STOP条件は、承認済みFix計画に従うこと。独断で変更しない。

### 4. 注意事項

- 既存ProductionのASRモデル構成・Azure重み2.0は変更しない。
- ローカルWhisperを新たなProduction依存として追加しない。
- Key PhraseのPrimary／Secondary両方PASS仕様は別指示系統で対応中。今回の作業と重複させない。
- Trial専用経路に限定し、未承認のValidator・Pronunciation Ledger・Production仕様を変更しない。
- 既存音声と過去Trial成果物を優先再利用し、不要なAPI呼出・TTS再生成を避ける。
- 独立した検証は並列化し、品質を守りながら最短で完了させる。

### 5. Trial Closeout

結果は `VALIDATED`／`REJECTED`／`USER_DECISION_REQUIRED` に分類する。

以下を簡潔に報告する。

1. Fix計画に対する実施結果
2. 救済できた具体例と救済できなかった具体例
3. 誤PASS・過剰NGの発生状況
4. 既存Validator・ASR Cascadeへの影響
5. QCD（品質・処理速度・量産原価・Trial費用）
6. Fable独立評価
7. Production採用に必要なユーザー判断

Trial結果と未決事項はSSOT／OPEN_ITEMS／Gitへ記録すること。

**Trial成功でもProduction採用・配線は行わない。ユーザー正式承認を必須とする。**

本指示はFix済み計画の実行許可であり、新たな仕様検討・計画変更の依頼ではない。
---

## 2. Fableの事前確認(あなたが再照合し、ズレがあれば開始前に報告)
- 計画はFix済み: v3(commit 31c80d76d、`docs/research/PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01/PLAN_SUMMARY_01.md`・`TRIAL_PLAN_01.md`・`TRIAL_CASES_01.json` 41件・`proto_multiword_span_01.py` `multiword_span_equivalent_v3`・unit test 20件PASS)。Opusレビュー13件(OF-PNMH-R-01〜13)は全件反映済み・未解決の重要指摘なし(`docs/pm/OPUS_FINDINGS_LEDGER.md`で確認)。
- Fix計画の範囲は**判定層L1(隣接span音素列連結比較、ストレス無視、全語+entity_like代表発音限定、V8/G5ガード)**。供給層L2(原稿側の正しい英語発音の取得・供給、ユーザー§3の2点目)は計画v3で「#133判断後の別計画・継続検討候補」として**本Trialの範囲外**。これはFix済み計画に従う(独断で範囲を広げない)。報告では§3の2点目を「Fix計画の範囲外。本Trialで言えるのは: CMU収録語の扱い・辞書外語は判定不能=推測PASSしない、の2点」と明示する。byUsの英語公式発音は未確定のまま(J7未回答)。
- ASR構成=現行Production(Primary OpenAI `gpt-4o-mini-transcribe`、Secondary Azure STT、Phrase List重み2.0)で確定。`TRIAL_PLAN_01.md`§8「ASR確定時に差し替える条件チェックリスト」を現行構成で埋める(変更不要なら「変更なし」と記録)。
- KPのPASS条件(両方PASS化)は別系統(OPEN-440)。本Trialは**現行承認済み仕様(Primary PASSならSecondary不要)**の条件で判定する。ただし追加費用0で可能な範囲で、KP相当クリップについて「Primary・Secondary両方PASS必須」と読んだ場合の結果も同じ転写から**感度分析として別表に**出す(新仕様ではない、解釈の併記のみ)。
- 最新モデル原則(25節): 本Trialは「Production条件での検証」が目的のためProduction採用済みのTTS/ASRモデルを使う(理由を報告に明記)。実際のmodel_id・routingを記録。

## 3. 実行内容(計画v3 `TRIAL_PLAN_01.md`に従う。要点)
1. 開始前チェック(22節): ユーザー指示§3・§4の全件を列挙し、計画のどこで検証されるか対応表を作る(未反映があれば開始せず報告)。STOPセンチネル・予算・既存音声の再利用候補を確認。
2. O1(API 0): unit test再実行、リスク面(非代表発音・ストレス除去・機能語variant経由で一致する組)の目視リストの最終確認、O0再適用(4,032ペア)の結果再確認。
3. P1(有料): 構成音声13本をProduction TTS(STANDARD)で生成→Primary(OpenAI)+Secondary(Azure)でASR→層A(ASR生認識)/層B(現行Validatorの判定)/層C(v3救済関数適用後の判定)を分離集計。記事B既存wav約5本はTTSせず再ASRのみ(既存転写が保存済みなら再ASRも省略し再利用)。正例(`byus→buy us`/`by us`、`already→all ready`等)・実音声負例(`Bi-us`、`bios`、`buy`脱落、`buy us on`追加、辞書外)・ストレス差のみの組を含める。各クリップの採否をケース表のIDに対応付ける。
4. 既存機構への影響: 現行の1語⇔1語同音判定・CS/F1・M1・Case A・数値/否定ガードについて、golden/保存転写への再適用でPASS→NG 0・新規誤PASS 0を確認(v2のO0結果の再利用可、差分があれば再計測)。Family X/Zの共通性(判定関数が共通入口であること)を1行で。
5. QCD: 処理速度(救済関数の実行時間/クリップ、Trial総所要)、量産原価への影響(実行時API追加0の根拠、再試行削減見込みは実測が無ければ「未確認」)、Trial費用(実測・出典)。
6. 分類案: 計画の合格基準(既知正例の救済100%/新規誤PASS 0/実音声負例のPASS 0/Regression PASS→NG 0/層A・B分離報告)に照らし、`VALIDATED`/`REJECTED`/`USER_DECISION_REQUIRED`の候補と根拠。最終分類はFable。
7. 成果物: `docs/research/PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01/TRIAL_RESULT_01.md`(ユーザー§5の1〜7の順。6はFable記入欄を空けておく)、`er093_output/pnmh_trial_01/`等の証跡(dataset manifest、asr_raw、paid_calls、層別結果json。wavはローカルのみ可・大きければ未commit)。Trial用scriptは`er093_pnmh_trial_01_*.py`(Trial専用、Production import可だがProduction経路無変更)。
8. SSOT: OPEN-439をTrial結果ラベル(`TRIAL_DONE_PENDING_FABLE`)へ、履歴追記。DECISION_LOGは書かない(採用判断はユーザー)。REPORT_LEDGER行追加。T-0保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01_委任_04.md`(Nは jsonl 内で `FABLE-DELEGATION-MARKER: PNMH-TRIAL-RUN-委任_04-20261022` を含むAgent tool_useの0始まり通番、237前後)。`check_delegation_prompt.py`実行(見出し不一致FAILは既知の偽陽性)。
9. commit→push→到達確認。`docs/pm/ACTIVE_TASK.md`先頭に固定ヘッダ。`docs/pm/RESULT_PACKET_PNMH4.md`へ報告。

## 4. 禁止
Production経路(`er006_*`/`er078_*`/`er008_*`/`er003_*`/`er063_*`等)・Validator・Pronunciation Ledger・Phrase List・ASR/TTSモデル構成・Azure重みの変更禁止。新flag/Production配線禁止。ローカルWhisperをProduction依存に追加しない(Trial内の参考利用も不要)。KP両方PASS仕様の実装・設計禁止。Cap超過見込み時は有料呼出停止。合格基準・評価対象の独断変更禁止。

## 5. 報告(RESULT_PACKET_PNMH4.md)
ユーザー§5の1〜7順(6はFable欄、7は候補)。加えて: 開始前チェック対応表/使用model_id・routing/費用実測(出典)と日次累計/感度分析(KP両方PASS読み)の別表/範囲外事項(L2)/RESULT_PACKET 4行((1)既存仕様整合 (2)未承認機能の既定値 (3)成果物 (4)撤去・残置)/raw URL(TRIAL_RESULT_01.md)。
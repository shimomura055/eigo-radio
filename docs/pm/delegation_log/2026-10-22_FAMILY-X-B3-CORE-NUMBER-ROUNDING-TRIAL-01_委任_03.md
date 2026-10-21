FABLE-DELEGATION-MARKER: B3RD-LUNA-NINC-委任_03-20261022

# 委任(FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01 委任_03: 判断LLMのLuna化+Ledger整合性N増し検証Trial。Trial限定・Production採用/配線禁止。Guardrail=案件見積JPY300[超過見込みなら有料工程前にSTOP報告]、日次1,000円)

## 0. 運用ルール・並列注意
- 別agentが「多語同音救済Trial(PNMH 委任_04)」を実行中で、`OPEN_ITEMS.md`(OPEN-439)・`docs/pm/REPORT_LEDGER.md`・`docs/pm/ACTIVE_TASK.md`・`docs/research/PROPER-NOUN-*`・`er093_output/`へ書く。あなたはOPEN-437・`docs/research/FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01/`・`er090_*`・`er090_output/`のみを扱う。共有ファイル編集前に必ず `git status` → 該当行を再Grep → 自分の行だけ編集 → 即 `git add <file>` + commit。`index.lock`は30秒待って再試行。
- `git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f 禁止。commit前 `.venv\Scripts\python.exe tools/secret_scan_01.py --staged` hits=0。push=`git push origin HEAD:main`(local `work/post-merge-01`)。一時ファイル(`ACTIVE_TASK.md`/`RESULT_PACKET_*.md`)はforce-add禁止。SSOT全文読込禁止。他人の未commit差分(`er0XX_output/*`)を混ぜない。有料runの再起動禁止(26節)。STOPセンチネル確認後に開始。
- 費用は実測(token usage・API料金、Repoの正式単価定義)から出典付きで集計。推定値を費用表に使わない。価格・model_idはRepoの正式定義(モデルrouting/価格表のファイル)で確認し、実際のresponse model_idを記録。
- 最新モデル原則(25節): 判断LLMをLuna(下位系)で評価するのは**ユーザー指示による原価低減Trial**が明確な例外理由。報告に使用モデル名/最新か/理由を記載。

## 1. ユーザー原文(2026-10-22、逐語。`docs/pm/delegation_log/2026-10-22_FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01_LUNA-NINC_USER.md` へ本文無改変で保存し、文字数とsha256[本文のみ]を記録)
---
# Claude Code追加指示：B3中核数値丸めTrial — Luna低コスト化・Ledger整合性N増し検証

対象：`FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01`

現行Status：`USER_DECISION_REQUIRED`

## 1. 目的

既存Trialで確認した数値丸め機能について、次の2点を追加検証する。

1. **判断LLMをGPT-6.1 SolからGPT-6 Lunaへ変更し、品質を維持したまま原価・処理時間を削減する。**
2. **複数記事・複数数値パターンでFact整合性を検証し、丸めによって量産が頻繁にNG停止しないことを確認する。**

成功条件は、単に丸め判断が正しいことではなく、**既存のFact Lock・品質基準を守りながら、量産で安定して運用できること**。

今回もTrial限定。Production採用・配線は行わない。

## 2. Lunaへの変更

- 数値丸め判断に使用しているSolをLunaへ変更する。
- B3本体の既存Solモデル、Fact選定、構成判断は変更しない。
- 既存TrialのPrompt・入力・判定基準を原則維持し、モデル変更の影響を比較する。
- 必要なら、品質を保つ範囲で出力項目・effort・トークン量を最適化する。
- Solで確認した9件の評価セットを再使用し、Lunaの結果と比較する。
- Lunaの判断結果にも、既存の決定論的安全検証V1〜V7を適用する。

**モデル名・価格・routingはRepoの正式な定義で確認し、実際のmodel_idとAPI費用を記録すること。**

Lunaで品質が不足する場合、原因を分析し、最小限の改善を試す。ただし品質基準を引き下げないこと。

## 3. Ledger整合性のN増し検証

今回の記事Aだけでなく、既存のFamily X記事・過去Trial成果物から複数のケースを選ぶ。

対象には少なくとも以下を含める。

- 大きな人数・金額など、概数化が自然な数字
- 小数・割合・相関係数など、精度保持が重要な数字
- 閾値・境界値・僅差の比較
- 日付・回数・数量
- 複数の数字が関連するFact
- 既に「約」が付いている数字
- 同じ数字でも文脈によって丸めの適否が変わるケース

既存の機械的中核数値選定をそのまま使用すること。

実際に中核数値として選ばれた数字を主対象とし、人工fixtureは不足する境界条件の補完に限定する。

**検証対象は、単なる数字の件数だけではなく、独立した記事数・Fact数・丸め対象数をそれぞれ報告すること。**

## 4. Fact Lock・Ledgerチェック

今回最も重視する検証。

丸め後の数値が、元のVerified Fact Ledgerとの整合性を保っているか確認する。

- 元Factの意味・数量規模・比較方向・閾値・結論が維持されるか。
- 丸めによってFactの範囲・確信度が変化していないか。
- Fact Lock Writerの規則(5)に対するTrial限定例外が、指定された中核数値にしか適用されないか。
- 丸め指定のない数字が変更されないか。
- B3 → Writer → R0/R1/R2 → Standard/Advancedで数値の意味が保たれるか。
- 現行ProductionのRisk Flaggerと、既存Ledger Deviation Checkerの双方で整合性を検証する。

**重要：旧Ledger Deviation Checkerは現行Production経路から撤去済みであるため、旧CheckerのPASSだけで量産運用可能と判断しないこと。**

現行Productionの実際のFact Lock・Risk Flagger・停止条件で評価する。

## 5. 量産停止リスクの評価

今回の重要なゴールは、丸め機能を導入した結果、量産工程が頻繁に止まることを防ぐこと。

次を明確に区別して評価する。

1. 丸めによって実際にFactの意味が変わったNG
2. 丸めは正しいが、Checkerが誤ってNGにしたケース
3. 丸め以外のWriter生成揺れによるNG
4. 本来NGにすべき数値変更をCheckerが見逃したケース

各ケースについて、原因・再現性・影響を記録する。

Trialでは、現行仕様のControlとLuna丸め追加版を可能な限り同一条件で比較する。

**NG率だけでなく、丸め機能追加によるNG増分・retry増分・Human Review増分を評価すること。**

単なるChecker PASS率だけではなく、Productionの最終判定・停止まで確認する。

## 6. NGが発生した場合

原因を次のように切り分ける。

- Lunaの丸め判断の誤り
- 丸め粒度の不適切さ
- Writerへの伝達・追従の問題
- Fact Lockの例外処理の問題
- Checkerの誤判定
- 後続R1/R2・英訳工程による変化

既存仕様・承認範囲内の不具合は自律的に原因究明・修正・再検証する。

新たな品質基準・Validatorの判定緩和・Fact Lock仕様変更が必要な場合は、Productionへ適用せず、**原因・対策候補・誤PASSリスク・QCD影響を整理してユーザーへ提案すること**。

CheckerがNGを出すからという理由だけで、判定を緩めて通すことは禁止する。

## 7. 変更禁止事項

- B3本体のFact選定・構成判断
- 機械的な中核数値選定・件数上限・優先順位
- Verified Fact Ledgerの正確な数値
- 承認済みFact Safety基準
- Production Writer Prompt・Validator・Risk Flagger
- Family X／Zの正式Production経路

既存Trialのoverlay方式を維持し、丸め判断機能以外に意図しない変更を生じさせないこと。

## 8. QCD・実施方針

- 既存Trialデータ・記事・音声化前成果物を最大限再利用する。
- APIによる記事全文の再生成は、評価上必要な最小限にとどめる。
- 無料の差分検証・安全検証・回帰テストを優先する。
- 独立した検証は並列化し、不要な待機・日付分割をしない。
- 開発費は既存の日次予算1,000円（JST）および承認済み作業範囲を遵守する。
- Solとのコスト・速度比較には、実測モデルID・token usage・API料金を使用する。
- Lunaで必要十分な品質が得られた時点で、追加のモデル探索を停止する。

## 9. 最終報告・受入条件

以下を簡潔に報告する。

1. **Sol対Luna：丸め判断品質・原価・処理時間の比較**
2. 検証した記事数・Fact数・中核数値数・丸め件数
3. 丸めるべき数値／丸めてはいけない数値の正解率
4. Fact Lock／Risk Flagger／Ledger Deviation Checkerの検査結果
5. 真のFact NG、Checker誤NG、見逃しの件数と具体例
6. Control比のProduction停止率・retry・Human Reviewの増減見込み
7. B3既存機能・Writerへの情報伝達の不変性
8. NG発生時の根本原因と、品質を下げない対策案
9. 1記事セットあたりの追加原価・処理時間
10. Fable独立評価、最終Status、Production採用に必要なユーザー判断

Fableは、検証サンプルの偏り、Fact Safety、量産停止リスク、費用試算を独立評価すること。

Trialの終了時は `VALIDATED`／`REJECTED`／`USER_DECISION_REQUIRED` に分類する。

**VALIDATEDでもProductionには採用・配線しない。**

CURRENT_SPEC・DECISION_LOG・OPEN_ITEMSとの整合を確認し、Trial記録・結果をGitへ保存する。

## 最終ゴール

**B3の既存仕様を変えず、機械的に選定された中核数値だけをLunaで適切に丸め、その結果がFact Lock・Ledgerチェックで安定して通過する、低コストな最小仕様を確立する。**

品質（Q）＞速度（D）＞量産単価（C）≫開発費用を厳守すること。
---

## 2. 既存資産(再利用必須。鵜呑みにせず再照合)
- 前回Trial: `docs/research/FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01/{PRIOR_TRIAL_GATE_01.md, TRIAL_DESIGN_01.md, TRIAL_RESULT_01.md}`、`er090_b3_core_number_rounding_trial_01_{overlay,run,evidence,test_01}.py`(test 18 PASS)、`er090_output/b3_core_number_rounding_trial_01/`(evidence/structural_diff_evidence.json、judge_v1失敗版=JPY21.95、Prompt v2)。前回費用JPY80.76、評価セット9件(Sol)、決定論的安全検証V1〜V7、Writer overlay(「Writerへの注意」2行+規則8、規則5の例外は指定中核数値のみ)、Before/After(記事A `134,515 people`→`about 130,000`、粒度不安定=UDR #135 D3)、仕様変更提案S1〜S7。
- 関連仕様(変更禁止、整合確認のみ): Fact Lock Writer規則(5)`er053_family_x_factlock_ja_writer_01.py:86-93`、Spoken-first Number Treatment `CURRENT_SPEC.md:1730`、Listener-Friendly Numeric Precision `CURRENT_SPEC.md:2096`、`DECISION_LOG.md:14388`(丸めはChecker側でNG扱いしない)・`:20533`(規則5)、旧Fact Checker/LDC撤去(2026-10-10、現行はRisk Flagger)、OPEN-437(UDR #135)。
- 現行Productionの中核数値選定(機械的)・B3 deterministic producer `er053_b3_deterministic_producer_01.py`・Risk Flagger・Fact Lock・停止条件の実コードを特定し、Trialの判定はこれら**現行Production経路の実関数**で行う(旧Ledger Deviation Checkerは追加の参考検査として併用可だが、それだけで運用可と判断しない)。
- Family X既存記事・Trial成果物(B3出力・Verified Fact Ledger・Writer出力が残っているもの): `er019_output/family_x_audio_production_wiring_01/*`(paycheck_personality/manga_ai_chat_byus/coffee_prices等)、`er053_output/*`、ほかGrepで探す。独立記事数を最大化する(目安4〜8記事。残存artifactで決まる)。

## 3. 作業(フェーズと費用Gate)
**Phase 0(API 0)**: 事前Gate=前回Trialとの整合・CURRENT_SPEC整合・現行Production Fact経路(Risk Flagger/Fact Lock/停止条件)の実関数特定。モデル定義の確認(Repo正式定義でSol/Lunaのmodel_id・単価・routing、前回Trialの判断LLM設定[model/effort/出力形式])。データセット設計: 既存記事から機械的中核数値選定をそのまま流し、ユーザー§3の7カテゴリへの充足表(記事数/Fact数/中核数値数/カテゴリ別件数、不足カテゴリのみ人工fixtureで補完し明示)。**費用見積(出典付き)**を作り、Phase 1〜2の合計がJPY300以内なら続行、超える見込みなら有料工程に入らず見積と選択肢を報告してSTOP。
**Phase 1(有料・小)**: Luna判断を9件評価セットで実行しSol結果と比較(品質/原価/処理時間、実測model_id・usage)。V1〜V7を適用。必要ならeffort/出力項目/token量を品質維持の範囲で最適化(Prompt・判定基準の意味は変えない。変えた点は差分として記録)。Lunaが不足なら原因分析→最小改善1〜2回(基準引下げ禁止)。十分なら探索停止。
**Phase 1b(有料・小)**: Luna判断を全データセットの中核数値へ適用(判断のみ、Writer未実行)。正解ラベルは人間基準(Fact意味・規模・比較方向・閾値保持)で事前に定義し、丸めるべき/べきでないの正解率を出す。
**Phase 2(有料・中、最小限)**: Writer→R0/R1/R2→Standard/Advanced(text経路のみ、**TTSなし**)を、Control(現行)とLuna丸め版で同一入力・同一条件で実行。対象記事は評価上必要な最小(費用Gate内で選ぶ。既存Control出力が残っていれば再利用して再生成しない)。現行Production Fact経路の最終判定・停止(Risk Flagger/Fact Lock/retry/HR)まで追い、NGをユーザー§5の4区分へ分類(原因・再現性・影響)。丸め指定外の数字が不変であること、規則5例外が指定中核数値にしか効いていないことを決定論的diffで確認。
**Phase 3(API 0)**: 集計・報告・SSOT。NG増分/retry増分/HR増分(Control比)、1記事セットあたりの追加原価・処理時間(実測)、Sol対Luna比較表。分類候補(`VALIDATED`/`REJECTED`/`USER_DECISION_REQUIRED`、最終はFable)。

## 4. 禁止
B3本体のFact選定・構成判断、機械的中核数値選定・件数上限・優先順位、Verified Fact Ledgerの数値、承認済みFact Safety基準、Production Writer Prompt・Validator・Risk Flagger、Family X/Z正式経路の変更禁止。overlay方式維持(`er090_*`内に閉じる)。Checker NGを理由に判定を緩めて通すこと禁止。TTS/音声生成禁止。Production採用・配線禁止。費用Guardrail超過見込み時は有料工程前にSTOP。

## 5. 成果物・SSOT・報告
- `docs/research/FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01/TRIAL_DESIGN_02.md`(データセット・費用見積・手順)、`TRIAL_RESULT_02.md`(ユーザー§9の1〜10順。10のFable欄は空け、分類候補のみ)。証跡=`er090_output/b3_core_number_rounding_trial_02/`(dataset manifest、judge結果、writer/R出力、checker結果、paid_calls、usage)。script=`er090_*_02*.py`(Trial専用)+test。
- SSOT: OPEN-437へ履歴追記(Status=`TRIAL2_DONE_PENDING_FABLE`、UDR #135は維持)。DECISION_LOGは書かない(採用はユーザー)。REPORT_LEDGER行追加。T-0保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01_委任_03.md`(Nは jsonl 内で `FABLE-DELEGATION-MARKER: B3RD-LUNA-NINC-委任_03-20261022` を含むAgent tool_useの0始まり通番、238前後)。`check_delegation_prompt.py`実行(見出し不一致FAILは既知の偽陽性)。
- commit(対象のみ明示add)→push→到達確認。`docs/pm/ACTIVE_TASK.md`先頭に固定ヘッダ。`docs/pm/RESULT_PACKET_B3RD3.md`へ報告(ユーザー§9の順+費用実測[出典・日次累計、`docs/pm/tools/daily_dev_cost_01.py --date 2026-10-22`で確認]+使用モデル名/最新か/理由+RESULT_PACKET 4行+raw URL[TRIAL_RESULT_02.md])。Phase 0でSTOPした場合はその時点の見積・選択肢・推奨のみ報告。
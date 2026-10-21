FABLE-DELEGATION-MARKER: B3RD-PROD-C1-委任_05-20261022

# 委任(FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01 委任_05 [C-1]: Family X中核数値丸め仕様の正式採用記録+Production実装設計書+S5のTrial環境検証+V8回帰テスト準備。**Production既存ファイルの編集はまだ行わない**=Opus独立レビュー(11-3条件A/C)後のC-2で行う。API原則0[S5/V8はオフライン]。)

## 0. 運用ルール・並列注意
- 他agentが同時稼働中: (B-1)固有名詞発音取得計画 `docs/research/PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02/`、(A-2予定)多語同音救済配線 `er006_preprod_hardening_01_validation.py`・`er094_*`。あなたはB3/Writer/Family X runner系と`er090_*`・`docs/research/FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01/`のみ扱う。共有ファイル(`OPEN_ITEMS.md`/`DECISION_LOG.md`/`docs/pm/USER_DECISION_REGISTER_01.md`/`docs/pm/REPORT_LEDGER.md`/`CURRENT_SPEC.md`)編集前に `git status` → 該当行を再Grep → 自分の行だけ編集 → 即 `git add <file>` + commit。`index.lock`は30秒待って再試行。
- `git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f 禁止。secret_scan `--staged` hits=0。push=`git push origin HEAD:main`(local `work/post-merge-01`)。一時ファイルはforce-add禁止。SSOT全文読込禁止。他人の未commit差分(`er0XX_output/*`)を混ぜない。

## 1. ユーザー原文(2026-10-22、逐語。`docs/pm/delegation_log/2026-10-22_FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01_APPROVAL-AND-ARTICLE-A-REMAKE_USER.md` へ本文無改変で保存、文字数・sha256[本文のみ]を記録)
---
# Claude Codeへの指示：Family X 数値丸め正式採用・記事A再制作

## 1. 正式採用判断

**Family Xの中核数値丸め仕様を正式採用する。**

Status：`APPROVED_FOR_PRODUCTION`

対象は**Family Xのみ**。Family Zへの展開は今回の承認範囲外。

承認仕様は以下のとおり。

- 判断モデル：GPT-6 Luna、reasoning effort = low。
- B3の既存方式で中核数値を選定した後、丸めの可否を判断する。
- Fact Lock規則(5)には、B3で正式指定した概数に限って例外を認める。
- 小数％は既存の概数化原則に従う。
- 既に概数の数値は再丸めしない。
- **V8を採用**：元の数値との相対誤差10％以内。既存90件のオフライン検証結果を再利用し、正式実装の回帰テストにも組み込む。
- **S5を条件付き採用**：`【概数表記】` のタグ漏れを検出する。まずTrial環境で修正後の検出・回帰テストを実施し、PASSを確認してからProductionへ実装する。PASSの場合、途中報告・追加ユーザー承認は不要。

丸めによって数値の意味、限定条件、比較方向、重要な閾値、Ledgerとの事実整合性を損なわないこと。

既存B3のFact選定・機械的な中核数値選定は変更しない。

## 2. 記事AをB3から全面再制作

対象記事：

**「給料が上がると、性格も変わる？」**

既存のResearch成果物・Verified Fact Ledgerを再利用し、**Research工程は再実行しない。**

新しい正式仕様をProductionへ実装・検証したうえで、記事Aについて以下をすべて再実行する。

1. B3：既存の正式B3処理から再実行し、新しい数値丸め判断を適用。
2. 日本語Writer：R0 → R1 → R2を再生成。
3. Standard／Advanced：両レベルの英語記事・解説・Key Phrases等、必要な全コンテンツを再生成。
4. TTS：新しい全文・関連コンテンツを正式Production経路で音声化。
5. ASR・Fact Safety・各種Validator・品質検査を実施。
6. 最終記事を組み立て、**ユーザー試聴ページを更新**する。

これは既存音声の数字部分だけの差し替えではなく、**Research以外の全工程の作り直し**である。

既存の完成候補・音声・試聴ページは比較・ロールバック可能な状態で保持すること。

再生成時には、数値丸め以外の承認済みFamily X仕様もすべて適用する。既存のASR・TTS・Key Phrase品質対策を後退させないこと。

## 3. 実装・検証・受入条件

正式初回Production経路に実装し、retry／fallback／regeneration／resumeでも同じ承認仕様が適用されることを確認する。

特に以下を検証する。

- V8が不適切な丸めを拒否し、正しい丸めを不必要に拒否しない。
- S5がタグ漏れを検出し、正常な文章には誤発火しない。
- Ledgerの元の正確な数値は変更されない。
- 数値丸めによって不要なSTOP・retry・Human Reviewが増えない。
- B3既存機能・他Familyの動作を変更しない。
- 実際に使用したmodel_id・reasoning effort・Prompt・routingの証拠を残す。
- 必須Regression・Validator・integration testをPASSする。
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMSを更新し、Gitへ反映する。

既存仕様・承認予算内の技術的不具合は自律的に原因究明・修正・再検証する。独立作業は並列化し、不要な待機や日付分割を行わない。

**承認済み品質を満たしたら、追加Trialや磨き込みをせず完成させること。**

ただし、未承認の仕様変更、重大なFact Safety問題、解決不能なblocker、予算上限超過はSTOPして報告する。

## 4. 最終報告

Fableが独立評価したうえで、以下を報告すること。

1. Family X正式実装の結果と `PRODUCTION_WIRED` 判定根拠。
2. V8・S5の検証結果。
3. 記事Aで実際に使用された数値のBefore／After。**記事に使われなかった丸め候補は報告不要。**
4. Fact Lock・Ledger整合性・Risk Flagger・ASR・TTS・各種品質検査の結果。
5. Standard／Advancedの完成音声とユーザー試聴URL。
6. 記事セットの実費と量産時の追加原価。
7. 残存する品質問題と、ユーザー判断が必要な事項。

**完了の区別を厳守すること。**

- Family X数値丸め仕様：正式Productionでの配線・実走・証拠確認後に限り `PRODUCTION_WIRED`。
- 記事A：全工程・品質検査完了後も、ユーザー最終試聴PASSまでは「完成候補」。

最終的な記事品質の受入判断はユーザーが行う。
---

## 2. 既存資産(再利用必須)
- Trial1/2: `docs/research/FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01/{TRIAL_DESIGN_01,TRIAL_RESULT_01,TRIAL_DESIGN_02,TRIAL_RESULT_02}.md`、`er090_b3_core_number_rounding_trial_01_{overlay,run,evidence,test_01}.py`、`er090_b3_core_number_rounding_trial_02_*.py`、`er090_output/b3_core_number_rounding_trial_02/evidence/`(`judge_eval.json`等=保存済みLuna判断90件、V8提案の根拠)、仕様変更提案S1〜S7(TRIAL_RESULT_01、新module約250行/runner+8/writer+25/provenance+5/MARK_RE+2/tests)、Prompt v2。
- Production側: `er053_b3_deterministic_producer_01.py`、`er053_family_x_factlock_ja_writer_01.py:84-95`(規則5)、Family X runner(`er019_family_x_entertainment_production_runner_01.py`等、B3→Writer→R0/R1/R2→Std/Advの呼出)、`er006_model_routing_contract_01.py:45-51,134`(routing)、`er005_output/cost_baseline_01/pricing_snapshot.json`、Risk Flagger `er053_risk_flagger_production_01.py`、タグ漏れ検知`TAG_LEAK_RE`/`assert_no_tag_leak`/`MARK_RE`の所在、provenance/audit(`audit/writer_result.json`等)。
- 承認済み関連仕様: CURRENT_SPEC:1730(Spoken-first Number)、:2096(Listener-Friendly Numeric Precision)、DECISION_LOG:14388・:20533、小数%概数既定 `er003_v1_n3_01_evidence_compression_editor.py:121-131`、Family体系(Z非対象)。
- 記事A: `er019_output/family_x_audio_production_wiring_01/paycheck_personality__run_pp_01/`(Research成果物・Verified Fact Ledger・現行完成候補・`human_approved_segments.json`)、試聴ページ `user_test/paycheck_personality_e2e_01/`。

## 3. 作業(C-1)
1. **承認記録(SSOT)**: `DECISION_LOG.md`へ「Family X中核数値丸め仕様 `APPROVED_FOR_PRODUCTION`(2026-10-22、原文§1逐語、Family Xのみ、Luna low、規則5例外はB3正式指定概数限定、小数%既定、既概数再丸めなし、V8 10%、S5条件付き)」エントリ。`docs/pm/USER_DECISION_REGISTER_01.md` #135→判断済み(採用、条件付S5)。`OPEN_ITEMS.md` OPEN-437→`APPROVED_FOR_PRODUCTION_WIRING_IN_PROGRESS`(PRODUCTION_WIREDではない)。記事A再制作用に新OPEN 1行(`ARTICLE_A_REMAKE_PENDING`、旧完成候補の保持・ロールバック可)。
2. **実装設計書** `docs/research/FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01/IMPLEMENTATION_DESIGN_01.md`(Opusレビュー用、簡潔): (a)新module `er095_b3_core_number_rounding_01.py`(Trial overlayのjudge呼出+V1〜V7+**V8**(相対誤差10%以内、既概数の再丸め禁止、小数%は既定に従う)を純関数化。judgeはLuna lowをrouting contract経由で呼ぶ[新role名を1件追加、実model_id・effort・Prompt sha・usageをprovenanceに保存]。失敗時fail-closed=丸めなしで続行し停止させない)。(b)配線点: Family X runnerのB3後・Writer前(+8行)、Fact Lock Writerの「Writerへの注意」【概数表記】+規則8(規則5の例外、指定中核数値のみ)(+25行)、provenance(+5)、**S5**=`TAG_LEAK_RE`/`MARK_RE`等へ`【概数表記】`を追加(+2、Production Validator変更=ユーザー条件付き承認済み: Trial環境でPASS確認後に実装)。Family Xのみ呼出(Z runnerから到達しないことを配線表で示す)。(c)retry/fallback/regeneration/resumeでの同一適用(B3成果物に丸め指定を永続化し、Writer再試行・Local Rewrite・resumeが同じ指定を読む)。(d)rollback=module定数`B3_CORE_NUMBER_ROUNDING_ENABLED`(既定True、Family X runner側の1行)。(e)検証計画: unit(Trial test 30件移植+V8 90件回帰[`judge_eval.json`再利用: 不適切丸め6件拒否・正しい丸め阻止0]+S5検出/誤発火test)、Regression(B3/Writer既存test、Family X既存integration test)、記事A実走(C-2)。(f)費用見積(出典付き): 記事A再制作=text(B3 judge Luna約0.12+Writer R0-R2+Std/Adv)+音声(Std/Adv TTS+ASR)。過去実測(記事B 93.94円=text 40.9+audio 53.0、`docs/pm/ACTIVE_TASK.md`旧ヘッダ/REPORT参照)を根拠に見積。TTS実行方式はD優先で`TTS_EXECUTION_MODE=STANDARD`推奨(Batch待ち時間を避ける。Batch換算原価も15節5区分で併記)。合計300円以内か明記。
3. **S5のTrial環境検証(API 0)**: `er090_*`内で、修正後の検知正規表現(`TAG_LEAK_RE`/`MARK_RE`相当の複製)に対し、(i)`【概数表記】`残留を含むWriter出力fixture→検出、(ii)Trial2の12arm出力+記事A/B既存Production本文(正常文)→誤発火0、を回帰テストとして実行・記録(`S5_TRIAL_RESULT_01.md`)。PASSならC-2でProductionへ実装する条件充足と記録(FAILなら原因と修正案を報告)。
4. **V8回帰データ**: `judge_eval.json`等の保存90件からV8 fixture(`er090_output/.../v8_regression_90.json`)を生成し、期待=拒否6/阻止0を固定。
5. **未配線module先行作成可**: `er095_b3_core_number_rounding_01.py`+`er095_..._test_01.py`(Production既存ファイルは編集しない。`git diff HEAD`で既存Production .pyの差分0を確認)。Luna実呼出testは行わない(C-2)。
6. T-0保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01_委任_05.md`(Nは jsonl 内で `FABLE-DELEGATION-MARKER: B3RD-PROD-C1-委任_05-20261022` を含むAgent tool_useの0始まり通番、244前後)。`check_delegation_prompt.py`実行(見出し不一致FAILは既知の偽陽性)。
7. commit(対象のみ)→push→到達確認。`docs/pm/ACTIVE_TASK.md`先頭に固定ヘッダ。`docs/pm/RESULT_PACKET_B3RD5.md`へ報告: 設計要約(配線点・配線表・retry/resume適用・rollback・検証計画・費用見積)/S5 Trial結果/V8 fixture/unit test結果/SSOT・commit/Opusレビューで見てほしい論点3〜5個/RESULT_PACKET 4行/費用(JPY0見込み)。

## 4. 禁止
Production既存ファイルの編集(C-2まで)、B3 Fact選定・機械的中核数値選定・Ledger数値・Fact Safety基準の変更、Family Zへの適用、承認仕様外の拡張(粒度方針の独自追加等)、Checker緩和、記事A再制作の開始(C-2)。
# OPEN-238-PRECHECK-FALSE-POSITIVE-FIX-TRIAL-01 設計doc(委任_A1、2026-10-07、¥0・コード変更なし・未承認の設計案)
## 1 事象と原因(要旨)
ai_control P2 rep2のEN文「set up by a third party」の"a third"が33.3%と誤抽出→Ledger他fact(84%/50%)と不一致→number_mismatch→Stage 2スキップBLOCKING→「Ledger値へ置換」でACCEPTABLEな文が破壊された。詳細は`docs/pm/open238_precheck_mislink_diag_01.md`。原因は`precheck_01.py` L108-115分数語辞書+L149-156`extract_percentages`が後続語を見ず`\b`一致のみで採用する点。承認構成(runner L496-523、`PRECHECK_MODE="number_only"` L504)は設計どおり動作。
## 2 案1の規則候補と採用案
候補(i)=後続が名詞なら除外(ブラックリスト)/(ii)=量構文を伴う場合のみ採用(ホワイトリスト)/(iii)=序数除外。(iii)は現辞書に"first/second/third"単独・"one second"が既に無く、**追加対応不要**(実測: 記事の"the third act""The third is"は非抽出)。
**採用推奨=(ii)ホワイトリスト**。根拠: floorはStage 2を経由せず無条件BLOCKINGのため、誤検出の被害>見逃しの被害(分数の意味的誤りはStage1/2のLLMが別途検出可能)。規則(記事側抽出のみ):
 - 分数語の直前が英数字/ハイフンなら不採用、直後がハイフン続き(half-hour, half-life, third-party)なら不採用。
 - 直後が(a)句読点/文末、(b)`of`、(c)比較・量語(more/less/fewer/again/as/higher/lower/larger/smaller…)、(d)the/their/its/all/these/those、(e)接続・助動詞(and/or/but/so/that/is/was/are/were/had/has/to/by/in…)の場合のみ採用。それ以外(party/parties/an/a/option/century/earlier/ago/past/名詞)は不採用。
 - Ledger側(`numeric_value`)の抽出は現行のまま(文脈が短く"half"単独等が多い)。
プロトタイプ(scratchpad、リポジトリ外)で確認済み: 「a third party」「third-party」「two third parties」「a half-hour」「half an hour」「a quarter century ago」「one quarter earlier」「half a million users」「half-life」「half past noon」「a third option」=全て非抽出/「about a third of voters」「fell by half.」「one third of them」「two-thirds of the votes」「a quarter of the budget」「half of them」「three quarters of firms」「up by a third.」「one-third more」「half the voters」=全て抽出。
| 見逃しになる正当表現 | 影響 |
|---|---|
| "half a million"(count、半百万) | 分数でなく数量→元々分数扱いは誤り。むしろ改善 |
| "a third more than"(後続=more)/"half of"/"a third." | 採用(見逃しなし) |
| "a third larger"等比較形容詞の語彙漏れ | 軽微な見逃し(LLM Stage1/2が残る) |
| "half a" + 名詞/"one quarter earlier" | 不採用=正当な分数でない/稀 |
残存FP: "in a quarter."(四半期)・"a third in line"等(句読点/in採用のため)。稀、Regressionで要確認。
## 3 案2の影響実測と採否案
対象=18 run dirのb1b/article.md + prod_e2e_02の9 run jsonから抽出した英語長文73本(重複含む。計91テキスト、決定論スキャン、¥0)。
 - 分数語辞書の語を含む文: **1文のみ(=今回の「a third party」文。算用数字なし)**。正当な分数語のみの文は**0件**(half/quarter/fifth/tenth/"two thirds"等はEN記事に一度も出現せず)。
 - よって案2の副作用(正当検査の取りこぼし)は**実測0件**だが、母数の中に正当な分数表現がそもそも無いため「安全」とは言えない(理論上は"half of voters"等のFact誤りを機械検出できなくなる)。
 - **採否案: 単独採用せず、案1を主軸、案2は不採用(理由: 実測では効果が案1と同一(同じ1件を防ぐ)で、取りこぼしの理論リスクだけ増える。分数語の本物の誤りが出る文は数字を含まないのが通常)**。併用は冗長。案2はPM判断の余地として残す。
## 4 Trial専用実装方式
 - 方式A(推奨): `er052_open238_precheck_fix_dev_01.py`を新設。`import er052_open233_self_recovery_precheck_01 as precheck`後に`precheck.extract_percentages`をv2へ差し替え(precheck内部・runner L2585/L2838の呼び出しも実行時にモジュール属性を参照するため同時に反映)。Production precheckファイル無変更。runnerは`precheck`モジュールを共有するため、DEV起動スクリプト内でのみpatchし、戻す(try/finally)。
 - 方式B: Production precheckにDEVフラグ追加。Production混入リスクがあり**非推奨**。
 - 注意: 差し替えは`check_number_mismatch`(L239観測側)・L322(claim側)・L666(Ledger和集合)にも及ぶ。ledger側を現行維持するため、v2は`side`を引数に持たせず、**記事側のみ厳格化**するなら`check_number_mismatch`ラッパで`observed`だけv2を使う形が最小(要実装時確認)。
## 5 テスト・Regression計画
 - 単体: 誤検出防止(§2の非抽出リスト13件+"third parties")/正当維持(抽出リスト10件)/本当の不一致検出(Ledger=84%に対し記事"50%"・"half of rollouts"→number_mismatch、Ledger="one third"に対し記事"half of"→mismatch)。
 - 決定論Regression: 18 run dir(b1b/article.md+research_ledger)+prod_e2e_02 9 runの合計27 runで`precheck.run_precheck`を修正前後で実行し、全finding(kind/fact_id/foreign_values)をdiff。期待=差分は今回のai_control rep2の2件消失のみ、他は完全一致。
## 6 有料再生の計画と概算(実行はユーザー承認後)
cycle1入力(`cycles[0].en_text_before_rewrite`+同ledger)でStage 1→Stage 2→Rewrite(Stage1は既存結果の再利用不可=再実行)を方式Aで1回再生し、「third party」文が保持されEVID-008が最終ENに残ることを確認。概算=1 run分のStage1〜Rewriteで**約¥15〜35**(E2E 1 runの総費用≈¥11、既存実績¥110.4/10 runより、Stage 2〜Rewrite限定のため上限¥50で取る。実測の裏付け付き見積りではない)。LLMの非決定性があるため、precheck発火の消失は決定論側で、文保持はN=1参考扱い。
## 7 Production実装時の注意点
 - 承認済みChecker仕様(`00a_base_checker_config.md`のbase構成)・Stage 2スキップ(runner L8784-8800)・`PRECHECK_MODE`は不変。変更はprecheckの抽出規則のみ。
 - `extract_percentages`は他に3箇所(precheck L322/L666、runner L2585/L2838)で共有→影響をRegressionで確認。ledger側緩和/厳格化の方針をProduction前に確定。
 - CURRENT_SPEC更新・`APPROVED_FOR_PRODUCTION`は人間ユーザーのみ。
## 8 Opus条件Cレビュー用の論点
1 ホワイトリスト(ii)の語彙(比較語・接続語)の過不足と、見逃し(FN)許容度。
2 記事側のみ厳格化/Ledger側据置の非対称が他の判定(L322 claim側、`changed_number_is_natural_rounding_only`)に与える副作用。
3 案2不採用の妥当性(分数語のみ文の機械検出を残す価値)。
4 DEV方式A(module patch)がrunner経路の全呼び出し箇所に反映されることの検証方法。
5 偽陽性が分数語以外(序数・"one second"・金額/日付の他辞書、COUNT_WORD_RE)に存在する可能性への追加走査要否。
## 9 Dangling Reference Check
実在確認済み: precheck_01.py L108-116(FRACTION_WORD_TO_PERCENT、L112="a third")、L149-156(extract_percentages)、L216-280(check_number_mismatch、L239観測側)、L322/L666(extract_percentages呼出)、run_precheck L648。runner L496-523(L504 PRECHECK_MODE)、L8086(resolve_precheck_target_sentence)、L8148-8158(PRECHECK_MODE*・filter_precheck_findings)、L8161-8165(build_precheck_floor_claims)、L8784-8786(Stage2スキップ+hint)、L2585/L2838(extract_percentages呼出)。`docs/pm/open238_precheck_mislink_diag_01.md`・`00a_base_checker_config.md`存在。未確認: L8190/L8800の末端行(診断docの引用のまま)。

---
## 10 Opus条件C必須修正の反映(委任_B1、2026-10-07)
Opusレビュー逐語: `docs/pm/opus_l2_review_open238_fix_01.md`。判定=条件付き可。以下を本設計の確定事項とする(§4方式Aの「extract_percentagesのモジュール差し替え」は**撤回**)。
 - **M1**: 厳格版抽出(`extract_percentages_strict`)は`check_number_mismatch`の`foreign_observed`計算(precheck L262)**のみ**に使用。L253/L258の台帳値確認・expected・all_ledger_pct・L322・runner L2585/L2838/L3090・coverage_checker L475は現行(緩い)抽出のまま。実装=現行`check_number_mismatch`を呼び(全ゲートは現行抽出)、percent種別で結果が出た場合のみforeignを厳格版で再計算(空ならNone)。count種別は無変更。
 - **M2**: runner `resolve_precheck_target_sentence`(L8093)のnumber_mismatch対象文特定も厳格版。DEV差し替えは`install(runner_module, precheck_module)`で「実行中のモジュール」へ(`python runner.py`起動時は`__main__`になるため、DEVスクリプトがrunnerをimportしてから`main()`を呼ぶ)。カウンタ(`strict_foreign`/`strict_locate`/`loose_extract_percentages`)で反映箇所を検証。
 - **M3**: 分数語の直前語が first/second/last/latter/other/better/earlier/later なら不採用(実装は全分数語に適用)。単体テストに「in the first half of 2025」(非抽出)、「seeking a third.」「half the time」(残る偽陽性、期待値=抽出と明記)を追加。
 - **O2**: Regression期待値に「L2838型・coverage_checker L475型のloose抽出(文別)・台帳loose抽出・L322(changed_number_is_natural_rounding_only 全fact×全文)・number_mismatch以外の全findingがbit単位不変」を追加(修正前後を同一プロセスで同一手順算出)。
 - **O3**: "percentage point(s)"の件数走査は報告のみ(修正しない)。
 - **O1**(分数語をforeign証拠から外す単純案)は新仕様判断のためユーザー判断待ちのまま、本Trialでは実装しない。
実装: `er052_open238_precheck_fix_dev_01.py`(Trial専用、既定では何もしない)。単体テスト: `er052_output/open238_precheck_fix_trial_01/tests/test_precheck_fix_dev_01.py`。Regression: `.../tools/regression_after_fix.py` → `.../regression/`。

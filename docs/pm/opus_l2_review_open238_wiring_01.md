# Opus独立技術レビュー(条件C) OPEN-238-PRECHECK-FALSE-POSITIVE-PRODUCTION-WIRING-01
日付: 2026-10-07、¥0、read-only
(以下、opus-consultantの最終レポート全文をサブエージェント記録(セッションJSONLのsubagents配下)から機械抽出。改変なし)

## OPEN-238-PRECHECK-FALSE-POSITIVE-PRODUCTION-WIRING-01 Opus条件Cレビュー(read-only・¥0)

### 総合判定
**このdiffでcommit/push → runtime evidence取得 → PRODUCTION_WIRED判定へ進めてよい。** 必須修正(M)はありません。新しい仕様判断も不要です(O1の扱いのみ記録事項)。Production採用可否そのものは判断していません(採用はユーザー決定済みとの前提で、配線の妥当性だけを見ています)。

---

### 論点1 最小差分 → 問題なし
- precheckは前回レビューの最小差分の範囲に収まっています。新設は`extract_percentages_strict`(L179-205)と定数`_OPEN238_*`、変更は`check_number_mismatch`のforeign計算(L311-317)だけです。runnerはL8093-8094の1箇所だけです。
- M1を満たしています。`expected`・`observed`(L288、台帳値確認とnatural rounding判定)、`ledger_pct`(L281)、`all_ledger_pct`(L721)、count種別は現行の抽出のままです。
- M2を満たしています。L8094で厳格版を使っています。precheckは別モジュールとして`precheck.`経由で参照しているので、runnerを`__main__`として起動した場合も問題は起きません。
- M3を満たしています。L169の`_OPEN238_STRICT_PRIOR_BLOCK`と、L191-193の直前語による除外が入っています。テストにも"first half of 2025"/"second half of the year"の除外と、残存偽陽性2件("seeking a third."、"half the time")の期待値が明記されています。
- 厳格版は現行版の部分集合です。PERCENT_REは同一で、分数語は絞り込むだけです。そのため、この変更でforeignが増えることはなく、発火は「減る方向」にしか動きません。安全側の性質です。
- 確認できなかった点: Bashが無いため`git diff`自体は見ていません。grepで確認できた範囲(呼び出し箇所)は要約と一致しています。dev file(`er052_open238_precheck_fix_dev_01.py`)のdocstring追記は無害です。

### 論点2 不変経路 → 問題なし
- grepで実測しました。現行の`extract_percentages`を使う箇所はprecheck L281/L288/L377/L380/L721、runner L2585/L2587/L2838/L2839/L3090、coverage_checker L475です。どれも厳格版に替わっていません。`extract_percentages`本体(L149-156)と`FRACTION_WORD_TO_PERCENT`も無変更です。関数本体が同一なので、これらの経路が不変であることはコード構造から保証されます。o2_bitwise_check.json(loose_sent/loose_ledger/l322/non_number_findings すべてtrue、number_mismatchの差分は2件消滅のみ)もこれと一致しています。
- `foreign_values`を使うのはrunner L8091だけです(grepで確認)。そのほかにfloorへ流れる別経路はありません。
- rewrite後に再実行されるprecheck(runner L1535 → `run_precheck` → `check_number_mismatch`)にも、厳格版のforeign計算が自動で効きます。これは意図どおりで、9 run中count記録のある4 runの再判定で確認済みです。
- 00a (4)(5)との整合: 変更は`number_mismatch`の証拠を絞るだけです。`PRECHECK_MODE="number_only"`、floor発火後のStage 2スキップ、承認スイッチの意味は変わりません。
- 確認できなかった点: runnerのL8784-8800と承認スイッチがdiff上で無変更であることは、要約の「+2/-1」を根拠にしています。commit前に`git diff --stat`でrunnerが+2/-1であることを必ず確認してください(O3)。

### 論点3 テスト・Regressionの十分性 → 問題なし(記録上の補足あり)
- 新規12件は次をカバーしており、十分です。
  - 陰性13例と陽性10例
  - PERCENT_REの不変、現行版の不変
  - 本件の偽陽性の消滅と、真の不一致の残存(分数語と%の両方)
  - M1(台帳値確認は現行版のまま、count種別は不変)
  - M2(文の特定: 慣用句の文を飛ばす、not_locatableになる)
  - L322が現行版のまま
- 既存911件PASS(変更前と同件数)、26 run Regression(2→0、他25 run全項目不変)、o2のbit単位比較もそろっています。決定論の範囲では十分です。
- 9 runについて: findings本体が保存されていないため「再計算+記録値(0)照合」になっています。これは代替証拠として妥当です。ただし完全な証拠ではないことをREPORTに明記してください(fixtureで再計算した9 runは、修正前後とも発火0)。

### runtime evidence(PRODUCTION_WIRED判定用の最小構成)
未パッチのProduction入口(runnerの`main()`、承認スイッチのまま)で、Checker 1 runを実行してください。次を記録します。
1. 実行したcommit hashと、precheck/runner 2ファイルのsha256(配線したコードで走ったことの証明)
2. 承認スイッチのdump(既存のapproved_switches_dump形式。`PRECHECK_MODE`・`FLOOR_MODE`が不変であること)
3. **precheck findingsの本体**(`number_mismatch`の`field`/`foreign_values`/`article_evidence`、初回とrewrite後の各cycle)。今回の9 runの欠落を繰り返さないためです。runnerを改修せずに残せない場合は、同じ入力でrun後に`run_precheck`を再実行し、その出力を保存する形で代替できます。
4. 題材はai_control P2 rep2(HEADで2件発火した記事)の推奨です。理由は、「HEADなら発火する/配線後は0」という差分によって、配線が生きていることを直接示せるからです。最終判定とcycle数も記録してください。
- 真陽性側(分数語の正当な不一致が引き続き発火すること)は、単体テストと26 runで担保済みです。runtimeでの追加は不要です。
- 費用はStage1/2のLLM分だけです(B2の実費 約¥5.5が目安)。

---

### 必須修正(M)
なし。

### 任意改善(O)
- **O1(記録のみ)**: 辞書に"one-half"(連字符つき)がありません。現行版は"half"キーで50を拾っていますが、厳格版は直前が連字符なので捨てます。結果として"one-half of voters"がforeignの証拠から外れます。これは検出漏れ方向(発火が減る側)で、Stage 1/2が補う範囲です。今回は修正不要ですが、残存事項として"seeking a third."等の残存偽陽性と並べて記録しておくとよいです。将来、辞書に"one-half"を足す場合は、台帳側の抽出も変わるため別管理IDにしてください。
- **O2**: 文単位の再抽出(L8094)と記事全体の抽出(L314)は、文分割の境界でまれに結果がずれる可能性があります。ずれた場合はnot_locatable → Stage4へ回るだけなので、安全側の失敗です。対応は不要で、注記のみで足ります。
- **O3**: commit時は、対象ファイル(precheck、runner、dev docstring、新規テスト、production_regression/、docs)だけを明示的に`git add`してください。作業ツリーには別タスクの未commit変更(b3_variant_dev、flow_runnerのrep19/22予算state等)が多数あります。`git diff --stat`でrunnerが+2/-1のみであることを確認してからaddしてください。

### 新しい仕様判断
不要です。M1〜M3は承認済みの「慣用表現を数値抽出しない」の範囲内で、配線は承認内容と一致しています。

### 関連ファイル
- C:\Users\tensh\eigo-radio\er052_open233_self_recovery_precheck_01.py(L149-205, L281-334, L377-380, L721)
- C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01.py(L8086-8097、現行版のままの呼び出し L2585/L2587/L2838/L2839/L3090)
- C:\Users\tensh\eigo-radio\er052_open233_stage1_coverage_checker_01.py(L475)
- C:\Users\tensh\eigo-radio\er052_open233_open238_precheck_strict_test_01.py
- C:\Users\tensh\eigo-radio\er052_output\open238_precheck_fix_trial_01\production_regression\PRODUCTION_REGRESSION.md / o2_bitwise_check.json

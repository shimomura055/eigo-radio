# Opus独立技術レビュー(条件C) OPEN-238-PRECHECK-FALSE-POSITIVE-FIX-TRIAL-01
日付: 2026-10-07、¥0、read-only
(以下、opus-consultantの最終レポート全文をサブエージェント記録(セッションJSONLのsubagents配下)から機械抽出。改変なし)

## OPEN-238-PRECHECK-FALSE-POSITIVE-FIX-TRIAL-01 Opus条件Cレビュー(read-only・¥0)

### 結論
**条件付きで進めてよい。** 案1が主軸という方向は妥当です。ただし、設計docの実装方針「`extract_percentages`をモジュールごと差し替える(方式A)」と「`check_number_mismatch`ラッパで`observed`だけv2にする」がどちらとも決まっておらず、どちらの形でも副作用があります。下のM1〜M3を設計に反映してからPhase Bへ進めてください。

---

### 論点1 ホワイトリスト規則の過不足 → 要修正(M3)
- 方向は妥当です。floorはStage 2を経由せずに無条件でBLOCKING+置換指示を出すので、見逃しより偽陽性の方が被害が大きいという判断は正しいと考えます。
- **残る偽陽性(重要)**: "in the **first half of** 2025" / "the second half of the year" は、直後が`of`なので抽出され、50%になります。ニュースでは"a third party"より頻出です。設計docの「直前が英数字/ハイフンなら不採用」は文字単位のため、これを防げません。
  - 対策: `half`の直前の語が first/second/last/latter/other/better/earlier/later のどれかなら不採用にする。
- その他の残る偽陽性(稀なので許容可。テストで明記してください):
  - "seeking a third." のように、序数を省略した文末("third term"の省略)。
  - "half the time"(=しばしば)、"half the battle"。
  - "a quarter to five"(時刻)、"a third in line"。
- 見逃し(採用されない正当な表現): "Half said…"、"nearly half supported…" のように直後が動詞のもの、比較形容詞の語彙漏れ。M1の形にすれば、この見逃しは「誤りの検出漏れ」(Stage 1/2のLLMが補う)にとどまり、新たな誤検出にはならないので許容できます。
- より単純な代替案(O1、要ユーザー判断): 分数語は「Ledger値が記事にあることの確認」にだけ使い、「Ledgerにない数値の証拠」(foreign、Ledgerのどのfactにも当たらない記事側の数値)には使わない。証拠には算用数字+%だけを使う。
  - 利点: 語彙の保守が不要で、慣用句の偽陽性はゼロになります。実測91テキストでの損失は0件です。
  - 欠点: "half of voters"のような分数語の誤りを機械では検出できなくなります。
  - 正当な分数語をfloor対象から外すことになるため、案1の範囲を超える仕様判断になります。ホワイトリスト案はM3を入れれば採用可能です。

### 論点2 記事側/台帳側の非対称と他の呼び出し → 要修正(M1・M2)
**副作用1: 記事側を一律に厳格化すると、新しい偽陽性が生まれます。** `check_number_mismatch` L253 の`_any_close(expected, observed)`は「Ledger値が記事にあるか」の確認です。ここに厳格版を使うと、次のケースで現行は発火しないのに、v2では発火するようになります。
- Ledgerが"about half"(50)
- 記事は"Half said…"(厳格版では非抽出)+Ledgerにない別の%を含む

**副作用2: 呼び出し箇所が設計docの列挙より多いです。**
- 設計docの列挙に無い箇所: runner L3090 `floor_verify_fact_numbers`、runner L8093 `resolve_precheck_target_sentence`(診断docには記載あり)、L1535(rewrite後の`run_precheck`)、`er052_open233_stage1_coverage_checker_01.py` L475 `numeric_value_set`。
- モジュールごと差し替えると、次の挙動が変わります。
  - L2838: disclosure_gap降格ガードが緩みます(claimの「新規数値」が減るため、QUALITYへ降格しやすくなる)。範囲外の安全装置変更です。
  - coverage_checker L475: fact側の値が減り、Stage1候補が増えます。
  - L322: より安全側(fail-closed)へ寄ります。

**副作用3: 文の特定がずれる恐れがあります。** L8093は「foreign値を含む最初の文」を、`extract_percentages`で探します。証拠を厳格版で作るのに文の特定を現行版のままにすると、記事に"a third party"文と正当な"one third of"文が両方あった場合、慣用句の文が選ばれ、そこが置換されます(本件と同じ型の事故)。

### 論点3 案2不採用 → 問題なし
- 実測では、防げるのは案1と同じ1件で、取りこぼしの理論リスクだけが増えます。M1の形なら分数語の偽陽性はさらに絞られるので、併用の価値はありません。不採用に同意します。

### 論点4 Trial実装の検証方法とProduction最小差分 → 要修正(M2の一部)
**検証方法**
- Pythonは関数内のglobal参照を呼び出し時に解決するので、モジュール属性の差し替え自体は効きます。runner・coverage_checkerは`import … as precheck`経由で、`from … import extract_percentages`はリポジトリに無いことを確認済みです。
- 落とし穴: runnerを`python runner.py`で起動すると、実行中のモジュールは`__main__`になります。DEVスクリプトで改めてimportしたrunnerは別のモジュールになり、差し替えが効きません。DEVスクリプトがrunnerをimportしてから`main()`を呼ぶ形にしてください。
- 検証は次の2つで行ってください。
  - (a) 差し替える関数に呼び出し回数カウンタを付け、Regression後に「厳格版はcheck_number_mismatchの証拠計算とL8093のみ、それ以外は現行版」で呼ばれたことをassertする。
  - (b) ai_control rep2の再現で、`foreign_values`が空になることを確認する。

**Production実装時の最小差分**
- precheckに`extract_percentages_strict`を新設し、`check_number_mismatch`の証拠計算をこれに替える。
- runner L8093を厳格版に替える。
- `FRACTION_WORD_TO_PERCENT`と現行の`extract_percentages`は変更しない。
- 変更は2ファイル・数十行の見込みです。`PRECHECK_MODE`・L8784-8800・Stage 2は不変です。

### 論点5 分数語以外の同種偽陽性 → 修正は別管理ID、本Trialでは¥0の走査を報告のみ
- 機械的にBLOCKINGへ上げる経路は`number_mismatch`だけです(PERCENT_RE・分数辞書・COUNT_WORD_RE・万/億)。
- 序数は辞書に無いことを確認しました。COUNT_WORD_REは算用数字が前提なので、偽陽性は低リスクです。
- 気になる点: PERCENT_REの`percent`の後ろに語境界が無いため、"5 percentage points"が5%として抽出されます(意味は異なる)。
- 対応: 27 run Regressionのついでに91テキストを走査し、件数だけ報告する。修正は別管理IDにする。

---

### 必須修正
- **M1**: モジュール全体の差し替えはやめる。`check_number_mismatch`を次の形にする。
  - L253/L258 の「Ledger値があるかの確認」は、現行(緩い)抽出のまま。
  - `foreign_observed`(L262)の計算にだけ厳格版を使う。
  - expected・`all_ledger_pct`・L322・L2585・L2838・L3090・coverage_checker L475は現行のまま。

  これで、本件の33.3は証拠に入らず消えます。そのほかの判定挙動は不変です。
- **M2**: runner L8093の文の特定も、同じ厳格版を使う。DEVでは`precheck.check_number_mismatch`とrunnerの`resolve_precheck_target_sentence`を、実行中のモジュールに対して差し替える(`__main__`の問題に注意)。呼び出し回数カウンタで反映を検証する。
- **M3**: `first/second/last…half`の直前語による除外を追加する。"in the first half of 2025"・"seeking a third."・"half the time"を単体テストに加える(最後の2つは残る偽陽性として期待値を明記)。

### 任意改善
- **O1**(要ユーザー判断): 「分数語はLedger値の確認にのみ使い、foreignの証拠にしない」という単純な規則を代替案として提示する。
- **O2**: Regressionの期待値に「L2838/L322/coverage_checkerの判定がbit単位で不変」を加える(M1が正しく反映されたことの確認)。
- **O3**: "percentage point"の件数を走査して報告する(修正は別ID)。

### 新しい仕様判断
- M1〜M3は「慣用表現を数値抽出しない」範囲内の実装詳細です。新しいユーザー判断は不要です。
- O1を採用する場合のみ、ユーザー判断が必要です。

### Phase Bへ進めてよいか
**条件付きで進めてよい。** M1〜M3を設計docへ反映してから、¥0の実装・単体テスト・27 run決定論Regressionに入ってください。Production採用の可否は判断していません。

関連ファイル:
- C:\Users\tensh\eigo-radio\docs\pm\open238_fix\design_01.md
- C:\Users\tensh\eigo-radio\er052_open233_self_recovery_precheck_01.py(L149-156, L216-280, L322, L666)
- C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01.py(L1535, L2585, L2838, L3090, L8093, L8162)
- C:\Users\tensh\eigo-radio\er052_open233_stage1_coverage_checker_01.py(L475)
<!-- 抽出元: C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\f9ae115b-0305-437d-ac2d-b452b22a5e2a\subagents\agent-a047a3cb72ff271ae.jsonl のSubagentHandback呼び出しのmessage引数。改変なし(スクリプト抽出) -->

# 委任_53 報告 (OPEN-233-SELF-RECOVERY-TRIAL-01)

## (1) 結論(10行以内)
1. 12件を分類した。12件のうち10件は出力形式が主因で、2件はPromptが主因だった。後段処理が主因の件はない。ただし主因の分け方は私の推定で、実験で切り分けてはいない。
2. 設計書§3の形で`CHECKER_SPANS_MODE`(既定legacy)をTrial専用に実装した。要素ごとの照合で、全要素が確定したときだけ確定とする。空配列は人間確認にする。Productionと判定基準は変えていない。
3. テストは406件から418件になり全PASS。er052回帰は462件PASS。プロジェクト全体回帰は4385件中12件が失敗/エラーで、er052は含まない。
4. 限定確認は6記事×2腕×n=3の36 callで、費用は¥14.99。見込みの約¥22と上限¥30のどちらも下回った。
5. 特定不能率は対照が0/24、処置が0/24だった。処置の配列要素は35/35が確定し、記事に逐語で存在しない要素は0件だった。Stage 1の出力では説明文混入は両腕とも再現しなかった。12件のうち8件はRecheckの出力で、4件は固定fixtureの再生だった。Recheckは今回の確認の対象外。
6. 検出(BLOCKINGのfact単位)は対照が12/18、処置が8/18。false PASSは対照が1/15、処置が4/15。処置のほうが低く、悪い向きに出ている。対照どうしの一致率が20/30と揺れが大きく、n=3と少ないため、差の意味づけはFableが判断してください。
7. コストは対照の平均が¥0.412、処置が¥0.421。出力トークンは4723対4762で、ほぼ同じだった。
8. Human Reviewが増えた呼び出しは、対照が0/18、処置が0/18だった。
9. 結論・VALIDATED判定は書いていない(Fable判断)。

## (2) 作業1: 12件の分類
共通の事実として、現行Prompt(`DEVIATION_PROMPT_TEMPLATE`)には`claim_in_article`の書き方の指示がなく、schemaは単一文字列である。V4A追記(前後1〜2文の限定語を見る指示)との相互作用は仮説で、測定していない。表の「配列で解消」は見込みであり、実測ではない。

| # | 種類・記事・出所 | 混入したもの(Checker文字列は委任_45 §2に逐語あり) | なぜ入ったか(推定) | 主因 | 配列で解消 |
|---|---|---|---|---|---|
| 1 | U01 bgroup_B4 iter5 s1 Recheck cycle2、**実LLM** | Checker自身の語「Meta’s test」。2つの引用の間に入った。段落が別の2箇所 | 単一文字列で2箇所を表せず、自分の語でつないだ | 出力形式 | 見込める。要素2つとも逐語で各1箇所 |
| 2〜5 | U02 ×4 safety_A4(iter5 s1・s2、iter6 s1・s2)Stage 1初回、**固定fixture再生**(独立なChecker出力は1件) | 日本語のつなぎ「および冒頭の」(接続語+位置語)。英語の引用に日本語が混入 | 2箇所を表せず日本語でつないだ。後段は、つなぎが接続語リストに無いので分解せず確定不能にした(安全側。後段は副因) | 出力形式(副: 後段) | 見込める。ただし固定fixtureの再生は配列にならず、新規Stage 1にだけ効く |
| 6 | U06 safety_A4 iter5 s2 Recheck cycle2、**実LLM** | 引用の後ろにChecker自身の説明文が1文付いた。段落全体を指す可能性がある | 引用1つ+説明を1欄にまとめた。説明の置き場がPromptに無い | Prompt | 条件付き。説明は`issue`へ移せるが、範囲が1文か段落かをCheckerが選び直す必要がある |
| 7 | U08 bgroup_B4 iter6 s1 Recheck cycle3、**実LLM** | 位置ラベル「The headline says … and the opening says,」。見出しと冒頭の2箇所 | 位置を文章で書いた | 出力形式 | 見込める。要素2つとも逐語 |
| 8 | U09 neg1_meta_b3prod_a2 iter6 s1 Recheck cycle2、**実LLM** | つなぎ「reinforced by the headline」。末尾の句読点も記事と違う | 2箇所を説明でつないだ。句読点の差はC2と同じ癖 | 出力形式(副: 句読点) | 見込める。句読点はPromptで逐語を指示し、VS_MATCH_EXT=ONならL5でも救える |
| 9 | U10 neg1 iter6 s1 Recheck cycle3、**実LLM** | 位置ラベル「Headline:」と末尾ピリオド。ラベルが指す範囲は引用と同じ見出し全体 | ラベル付けの癖。Promptに禁止の指示が無い | Prompt | 見込める |
| 10 | U11 hormuz_run03_standard iter7 s2 Recheck cycle2、**実LLM** | 説明文が、引用していない見出しとin one lineの2箇所を位置だけで指している | 本文の引用1つ+他の2箇所を説明で指した。同じ指摘の`same_fact_id_locations`には両箇所の逐語が入っていた | 出力形式 | 条件付き。他の2箇所を別要素で出すかはCheckerの出力次第 |
| 11 | U12 hormuz_run03_standard rep9 s1 cycle2 Recheck、**実LLM** | 「(also reflected in the headline)」。見出しは引用されていない | 説明の括弧で他箇所を指した | 出力形式 | 条件付き。見出しを別要素にできるかはCheckerの出力次第 |
| 12 | U13 hormuz_run03_standard rep9 s1 cycle3 Recheck、**実LLM** | 括弧内の位置ラベル「(headline)」「(one-line summary)」。位置は実際と一致 | 位置を括弧で書いた | 出力形式 | 見込める |

**起因の集計**:
- 主因は、出力形式が10件(#1・#2〜5・#7・#8・#10・#11・#12)、Promptが2件(#6・#9)、後段処理が0件。
- 後段処理は#2〜5と#8で副因になった。
- 「見込める」が9件、「条件付き」が3件(#6・#10・#11)、「見込めない」が0件。
- 実LLM出力は8件、固定fixture再生は4件(U02)。

## (3) 実装の要点
- スイッチは`CHECKER_SPANS_MODE`(`legacy`が既定、`violation_spans`)。CLIは`--checker-spans-mode`。
- schema:
  - `build_deviation_schema_with_spans`は`claim_in_article`を外して`violation_spans`を足す。
  - `build_recheck_schema`は、スイッチONのときにその関数を使う。
  - Stage 1初回は`stage1_fresh_with_enumeration`、RecheckはPrompt追記+`run_recheck`が対象。
  - 確認用Recheck(`run_recheck_confirm`)と`stage1_fresh`(enumerationなし)は対象外。
- 組み立て: `assemble_claim_from_violation_spans`と`adopt_violation_spans`が、`claim_in_article`を改行区切りでコードが組み立てる。配列が無い固定fixtureは何もしない。
- 照合:
  - `resolve_violation_spans`は入口に変わり、旧本体は`_resolve_claim_string`へ移した。
  - 配列経路は`_resolve_spans_array`で、要素ごとに`_resolve_claim_string`(VS_MATCH_EXT=ONならL5・単語境界も)を使う。
  - 1要素でも確定不能なら全体が確定不能になる。理由は`reason_detail`の`span[i]:reason`と`failed_span_index`に残る。
  - 空配列は`violation_spans_empty`、言語が割れたときは`mixed_lang`。
- `same_fact_id_locations`は別のまま。展開した別箇所は元の配列を引き継がない。
- `claim_in_article`の読み取り箇所への対応:
  - 読み取り9箇所は、組み立てた文字列が入るので無改修で動く。
  - `resolve_violation_spans`を呼ぶ約10箇所も無改修。
- Prompt追記ブロック(`VIOLATION_SPANS_INSTRUCTION`)は`docs/pm/delegation_log`ではなくrunnerの`VIOLATION_SPANS_INSTRUCTION`に逐語がある。設計書§3-2に対して「文の一部だけが問題でも、その語句を含む文全体を引用」の行は使わず、次の行にした。
  - 「文の一部だけが問題の場合は、その語句・節だけを引用してかまいません(文全体に広げる必要はありません)。ただし、引用は記事内でちょうど1箇所に定まる長さにしてください。同じ語句が記事内の別の場所にも出てくる場合は、前後の語を足して1箇所に定まるようにしてください(足すのは問題の語句の前後の連続した語だけで、説明や接続語は入れないでください)。」
  - 冒頭に「引用は英語の記事本文からのみ行ってください」を足した。
- **設計書§3と異なる点(形は同じで、機構が違う)**:
  - 設計書は、claimへ`violation_spans`のlistを別フィールドで持たせるとしていた。実装は、claim文字列を鍵にしたモジュール内の対応表(`_VS_SPANS_REGISTRY`)で配列を引く。理由は、`claim_text`が10以上の関数を文字列のまま渡るので、無改修で済ませるため。
  - 空配列のStage 2表示用に、`"(violation_spans empty) " + issue`という文字列を組み立てる。確定には使わない。
  - Fableから見て不都合なら、claim dictに配列を載せる形へ直せる。直すと呼び出しが約10箇所変わる。

## (4) テスト・回帰
- runnerのテストは406件から418件(12件追加)。全PASS。U01〜U13を使った確認も含む。
  - 正しい配列要素は各要素が確定する。
  - 説明文が混入した文字列は確定不能になる。
  - 空配列は人間確認になる。
  - legacyで既存と同じになる。
- er052回帰は462件PASS。
- プロジェクト全体回帰は4385件のうち、失敗6件+エラー6件(計12件)。er052は含まず、er003/er011/er012/er015/er025/er040/er043のテストが失敗している。
- 委任文の「既存の失敗11件」と1件ずれている。私は基準をstashなしでは再現できず、原因は未確認。er052以外で、本変更が触れていないモジュール。
- 回帰後に`budget_state_c233an_42_rep22.json`が書き換わったので`git checkout`で戻した。rep19の1件は着手前からの既存差分で、触れていない。

## (5) 作業3の集計
n=3と少なく、6記事の限られた確認。対照は`claim_in_article`(単一文字列)、処置は`violation_spans`(配列)。

| 項目 | 対照 | 処置 |
|---|---|---|
| call数(失敗) | 18(0) | 18(0) |
| 1. 特定不能(Stage 1のMAJOR指摘、VS_MATCH_EXT=ON、日英両方) | 0/24 | 0/24。配列要素は35/35が確定 |
| 1. English onlyで照合した場合 | 0/24 | 0/24 |
| 2. BLOCKING factの検出率 | 12/18 | 8/18 |
| 3. false PASS(全MINOR/空) | 1/15 | 4/15 |
| 4. Human Review行き(確定不能を含む呼び出し) | 0/18 | 0/18 |
| 5. 費用(平均、範囲) | ¥0.412(¥0.084〜0.663) | ¥0.421(¥0.111〜0.871) |
| 5. 出力トークン(平均) | 4723 | 4762 |
| 6. JSON/schema失敗 | 0 | 0 |
| 6. MAJORなのに配列が空 | - | 0 |
| 6. 配列要素が記事に逐語で存在しない | - | 0/39 |
| 引用の長さ(MAJOR、平均) | 88文字(49〜186) | 66文字(11〜201) |

- 項目2の分母: 検出率は、BLOCKING対象のfactを記事×call数で数えたもの。MUSE-HC-010(meta_run03_standard)は軽微になったので除外して、参考として別に数えた。参考の検出は、対照が0/3、処置が0/3。
- 項目2のfact別(対照→処置):
  - HF-009(hormuz)は3/3→1/3。
  - MUSE-HC-002(B4-a)は0/3→0/3。
  - MUSE-HC-006(A4)は3/3→2/3。
  - MUSE-HC-012(A4)は1/3→1/3。
  - MUSE-HC-012(meta)は2/3→1/3。
  - er009_changed_number(Safety対照)は3/3→3/3。
- 項目3のfalse PASS: 処置の4件は、hormuz_run03_standardが2件、meta_run03_standardが2件。対照の1件はmeta_run03_standard。分母15は、BLOCKING対象のある5記事×3回。
- 項目7の揺れ: 対照どうしのfact単位の一致率は20/30=0.67。処置どうしは19/33=0.58。記事別では、hormuz_run03_standardは対照が3/3、処置が1/3、safety_A4は対照が7/9、処置が6/12。処置と対照の差(検出率で-0.17〜-0.67)が、この揺れを超えるかは、n=3では判断しにくい。判定はFable。
- Stage 1の限定確認なので、今回測っていないことがある。
  - 説明文混入の12件のうち8件はRecheck(prior_issuesあり)の出力で、今回は呼んでいない。
  - 4件は固定fixtureの再生で、配列の効果は見えない。
  - つまり「特定不能率が下がるか」は、今回のStage 1では両腕とも0で、確かめられていない。
- probeの単価は、bgroup_B4で対照¥0.446、処置¥0.544。見込みはn=3で約¥17.8だったので、nは3のまま進めた。
- 実行回数は36 call(probeの2 callを含む)。費用は今回¥14.9926、Phase累計¥530.0107、残額¥369.9893(上限¥900)。

## (6) SSOT・設計書への追記文案(本文は編集していない)
- **DECISION_LOG.md(委任_53の結果)**:
  - 「Checker説明文混入12件を分類した(主因は出力形式10・Prompt2、後段0。見込みは見込める9・条件付き3)。Trial専用の`CHECKER_SPANS_MODE=violation_spans`を実装した(既定legacy、Production未変更、判定基準不変)。Stage 1のみの限定確認(6記事×2腕×n=3、¥14.99)では、特定不能は対照・処置とも0/24、配列要素は35/35が確定した。一方、BLOCKING fact検出は対照12/18、処置8/18、false PASSは対照1/15、処置4/15だった(n=3、対照どうしの一致率0.67)。VALIDATEDではない。Production採用は未判断。」
- **OPEN_ITEMS.md OPEN-233行の次Action**:
  - 「(a)処置の検出低下が揺れかPromptの影響かを、hormuz_run03_standardとmeta_run03_standardに絞ってn増しで確認するか判断する。(b)説明文混入の本体はRecheck(prior_issuesあり)なので、Recheck文脈で確認するか判断する。(c)B-alt(確定不能のときだけ返し直す)との比較。」
- **`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md` §38**:
  - §3(1)(2)の実装内容に、§4の数値表を添える。
- **設計書§3への追補(12-2. 委任_53の結果)**:
  - 実装の機構(registry)が設計書の「claimにlistを別フィールドで持たせる」と異なること。
  - 空配列のStage 2表示にissueを添えること。
  - 要素ごとの照合の理由コードの形。
  - 限定確認の結果。

## (7) ユーザーへ戻す条件
- Safety原則・Product原則の変更が必要な事実: なし。
- Production仕様の変更判断が必要な事実: なし。
- 予算: 今回¥14.99で上限¥30以内。総枠¥900にも余裕がある。
- 設計がレビュー済みと異なる点: 形は同じ。機構の違い(上記(3))を報告した。
- 事実として注意すべき点: 処置腕の検出が対照より低い向きに出た(n=3、揺れ大)。これは判断材料としてFableへ。

## (8) T-0・commit・URL・Read
- T-0: 保存はした(要旨を含む形)。check結果はFAIL。理由は「事前指定Grep一覧」「実行コマンド全文」の見出しが検出されなかっただけで、記録用。保存文は全文ではなく一部を要旨化したため、全文保存の要件は満たしていない。
- commit 1(実装、測定前): `f7e46b38`
- commit 2(測定後): `74d805b9`
- push: `main`が`origin/main`と一致し、どちらも反映済み。
- 「確認できたこと」と「推測」の区別:
  - 確認できたことは、テスト・回帰・限定確認の数値。
  - 推測は、12件の主因の分け方・「配列で解消」の見込み・検出低下の原因(未確認)。
- 一覧外のRead:
  - runnerは1000〜1070行、5009〜5110行、6130〜6180行を読んだ。
  - `er003`の450〜610行と`er051`の150〜290行を読んだ。
  - 設計書の3705〜3755行を読んだ。
- CSV(`unverified35_classification_01.csv`)のC3行は、文字コード(cp932)で読めなかった。委任_45 §2の逐語を代わりに使った。
- 全体回帰の失敗リストは`/tmp/full_reg.txt`に取った(リポジトリ外)。

raw URL:
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_open233_self_recovery_flow_runner_01.py
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_open233_self_recovery_flow_runner_01_test_01.py
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_open233_checker_spans_format_compare_01.py
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_checker_spans_format_compare_01/results_01.json
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_checker_spans_format_compare_01/cases_01.csv
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/delegation_log/2026-10-03_OPEN-233-SELF-RECOVERY-TRIAL-01_53.md

(`docs/pm/RESULT_PACKET.md`は上書きしたがaddしていない。)

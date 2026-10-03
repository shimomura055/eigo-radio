## 管理ID

`OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_56)。並行タスク: 委任_55(線引きの正式採用の反映。runner・Stage 2・SSOTを編集する)。**本委任はrunner・Production code・SSOT・既存docを編集しない。** 新規doc 1点と、リポジトリ内の新規分析ディレクトリ(スクリプト・結果)だけを作る。git操作はしない(commitはFableが後で指示する)。

## 性質/到達上限Status/禁止事項

- 性質: Checker引用への説明文混入12件の原因の深掘り(前回の分離形式でなぜ検出性能まで落ちたかを含む)、複数の対策案の設計と比較、決定論的な案の¥0オフライン検証。この後、FableがOpus独立レビュー(必須)→Fable再評価→ユーザー提示を行う。
- 到達上限Status: なし(本委任は分析・設計のみ。採用判断はしない)。
- 禁止事項: コード(runner等)・Prompt・テスト・SSOT・既存docの編集禁止。LLM/API呼び出し禁止(¥0)。`git add`/`commit`/`push`禁止。「似ている文をAIや類似度で再推測する」案は、比較のための参照としてのみ扱い、推奨しない。
- 費用上限: ¥0(T-3対象外)。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)の該当判定: 条件A(Checker出力を後段で解釈・変換する仕組みの設計)に該当。ユーザーも「必ずOpusの独立技術レビューを実施」と指示。本委任は設計案の作成までで、レビューはFableが依頼する。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSを伴わない。)

T-0の補足: 保存先 `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-03_OPEN-233-SELF-RECOVERY-TRIAL-01_56.md`。**委任文は全文そのまま保存(要旨化・参照形式は不可)。** `RESULT_PACKET.md`は委任_55が使用中のため書かない(報告は最終メッセージ)。一時ファイルはリポジトリ外(`%TEMP%`配下)。

## ユーザー指示(原文、2026-10-03。全文は委任_55が`DECISION_LOG.md`へ逐語記録する)

```
## 4. Checker説明文混入12件は見送らない

今回の分離形式Trialでは、

- 原文位置の特定は改善
- しかしCheckerの重大事実検出が低下
- false PASSが増加

したため、その方式自体は不採用で問題ありません。

ただし、

**「1案試してうまくいかなかったので、この問題自体を見送る」**
という結論にはしないでください。

この問題は原因がかなり見えているため、引き続き対策を検討してください。

## 5. 説明文混入12件について、原因を改めて深掘りする

今回の結果を前提に、もう一度原因を掘り下げてください。

最低限、以下を切り分けてください。

- なぜ10件は出力形式起因だったのか
- なぜ2件はPrompt起因だったのか
- Checkerが「違反箇所」と「理由」を混ぜて出す具体的なパターン
- 初回CheckerとRecheckで混入の仕方が違うか
- どの処理段階で記事原文と説明文を安全に分離できるか
- 分離に必要な情報はすでにChecker出力内に存在しているか
- CheckerのPromptやSchemaを変えずに解決できる可能性
- 後段で決定論的に処理できる範囲
- 一意に確定できない場合のfail-safe

単に「別方式を試す」ではなく、
**なぜ前回方式で検出性能まで落ちたのか**
を、Prompt差・Schema差・実際の出力差から具体的に説明してください。

## 6. 対策案は複数案を出すこと

こちらから一つの候補案を提示しますが、これをそのまま採用しないでください。

### 候補案
**Checker自体の検出Prompt・判定方法・出力Schemaは変えず、後段で記事原文部分と違反理由を分離する。**

例えば、

- Checkerは今までどおり問題箇所・問題内容・理由を出す
- 後段で記事本文に完全一致する引用部分を抽出
- 句読点差だけなら承認済みの句読点吸収を使う
- 記事内で一意に1箇所確定できる場合だけ採用
- 似ている文をAIで再推測しない
- 一意に確定できなければ勝手に近い文を選ばない

という方向です。

ただし、これは**あくまで一つの候補案**です。

Claude側でも今回の原因分析から、
より単純・安全・低コスト・再現性の高い対策がないか、別案を必ず検討してください。

比較軸は最低限、

- Checkerの検出性能を落とさないか
- false PASSを増やさないか
- Human Reviewを増やさないか
- 不要Rewriteを増やさないか
- 再推測による誤範囲選択を起こさないか
- 実装が複雑化しすぎないか
- 初回 / Recheck / retry / fallbackで整合するか
- コスト
- 非決定性

です。
```

関連する既存のユーザー方針: 「Checkerが示した違反範囲を後段で再推測しない/複数文なら複数文のまま/離れた複数箇所なら複数範囲として渡す/別AIの引用でRewrite対象を決めない/類似度や単語重なりで勝手に1文へ縮小しない/最小修正優先」「最初から文全体Rewriteへ広げない」「Production正式pathは変更禁止」。

## 背景(前回までの事実)

- 12件(9種類: U01・U02[×4]・U06・U08・U09・U10・U11・U12・U13)の逐語・分類は委任_45(`docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_45_result.md` §2-1)と委任_53(同`_53_result.md` §(2))。8件は実LLMのRecheck出力、4件(U02)は固定fixtureの再生。
- 前回方式(委任_53、`CHECKER_SPANS_MODE=violation_spans`): Trial schemaから`claim_in_article`を外し`violation_spans`配列を追加、追記ブロック`VIOLATION_SPANS_INSTRUCTION`(runner内に逐語)を付けた。Stage 1限定確認(6記事×2腕×n=3、`er052_output/open233_checker_spans_format_compare_01/`に生の応答・`results_01.json`・`cases_01.csv`): 配列要素35/35逐語一致、特定不能0/24(両腕)、**BLOCKING fact検出 対照12/18→処置8/18、false PASS 対照1/15→処置4/15**、費用ほぼ同じ、引用の平均長 88→66文字。対照どうしの一致率0.67、処置どうし0.58。
- 受け渡し側の現行照合(委任_42・49): `resolve_violation_spans`→L0完全一致/L1引用符除去/L2空白・引用符正規化/L3大小文字/L4曲線引用符で囲まれた断片の分割(つなぎが接続語・句読点のみのとき)、`VS_MATCH_EXT`ONでL5(両端句読点除去+単語境界)・`label_only`・単語境界。「ちょうど1箇所」でのみ確定。確定不能→人間確認(fail-closed)。
- 同じ指摘の`same_fact_id_locations`(他箇所の列挙欄)には、U11のように説明文側が位置だけで指した箇所の逐語が入っていた例がある(委任_45)。

## 作業1: 原因の深掘り(¥0、記録とコードから)

1-1. **混入パターンの型化**: 12件(+委任_45 §2-4の非BLOCKING 5件、K2で捨てられた`same_fact_id_locations`14件も参考に)を、文字列の構造で型にする。例: [引用A]+[Checkerの語]+[引用B]/[引用A]+[説明文1文]/[位置ラベル:]+[引用]/[引用]+[(括弧の位置ラベル)]/[引用A]+[接続語]+[位置語]+[引用B]/日本語のつなぎ。各型について、引用部分が引用符(“ ”)で囲まれているか、囲まれていないか、を併記する(後段での分離可能性を左右する)。
1-2. **なぜ出力形式起因10件・Prompt起因2件か**: 委任_53の分類の根拠を、各件の文字列構造(1-1の型)と、現行Prompt・schemaのどの欠落(複数箇所を表せない単一文字列/書き方の指示なし/位置の説明の置き場がない)に対応するかで説明し直す。分類を変える必要があれば変えて理由を書く。
1-3. **初回CheckerとRecheckの違い**: 実LLM出力の8件が全てRecheckである理由を、Recheck特有の入力(`prior_issues`、前周回の指摘一覧、再検査の指示文)と出力の傾向から説明する。既存記録で、Stage 1初回の実LLM出力(fresh)に説明文混入が何件あるか、Recheckに何件あるかを数える(委任_41の`claims_detail_01.csv`の`phase`列と`cause`列、委任_53の`cases_01.csv`)。Recheckの指示文(runner `run_recheck`の追記ブロック、Grep `prior_issues`)に、位置の説明を促す文言が無いかを確認する。
1-4. **分離に必要な情報は既に出力内にあるか**: 12件それぞれについて、(i)引用部分が引用符で区切られているか、(ii)説明文側が指す「別箇所」の逐語が同じ指摘の`same_fact_id_locations`や`issue`に入っているか、(iii)`claim_in_article`から引用符内だけを取り出せば記事に逐語で一致するか、を表にする。
1-5. **前回方式で検出性能が落ちた理由**(最重要): `er052_output/open233_checker_spans_format_compare_01/`の生の応答を対照・処置で突き合わせる。
   - Prompt差: 対照と処置のPrompt全文の差分(追記ブロックの位置・長さ・内容)。
   - Schema差: `claim_in_article`を外して`violation_spans`を必須にしたことで、出力の順序・必須項目がどう変わったか(schemaの`required`・`properties`順を逐語で)。
   - 実際の出力差: 記事×腕×回ごとの指摘数、severity分布、fact_idの分布、1指摘あたりの引用長、`issue`の長さ、配列要素数の分布。検出が落ちたfact(HF-009 3/3→1/3、HC-006 3/3→2/3、HC-012 2/3→1/3)について、処置腕の出力ではそのfactに触れていないのか、触れているがMINORか、別のfactにまとめられたのか、を逐語で示す。
   - 仮説を2つ以上立て、記録で支持される/されないを示す(例: 「問題の語句だけを引用」の指示が注意を狭い範囲へ向け、文単位の判断を減らした/`claim_in_article`を外したことで『まず引用してから判断する』という生成順序が崩れた/追記ブロックの長さがV4Aの限定語確認の指示を薄めた/揺れの範囲内)。
1-6. **後段で決定論的に処理できる範囲と、fail-safe**: 1-1の型ごとに、Prompt・schemaを変えずに後段だけで「記事原文部分」を安全に取り出せるか(取り出せる条件、取り出せない条件)を整理する。

## 作業2: 対策案の設計(複数案。ユーザー候補案を含むが、それをそのまま採用しない)

最低限、次の案を具体化し、必要なら追加する。各案について、処理の流れ、変更箇所(関数名・行)、初回/Recheck/retry/fallbackでの扱い、fail-safe、実装規模、追加LLM呼び出しの有無、非決定性、を書く。
- **案P(ユーザー候補案)**: Prompt・schema不変。後段で`claim_in_article`から記事本文に逐語一致する部分だけを決定論的に取り出す。具体化: (1)引用符(“ ” " 「」)で囲まれた断片を全部取り出す、(2)各断片を既存の照合(L0〜L3、L5、単語境界)で「ちょうど1箇所」に確定、(3)引用符の外の残り(つなぎ)は**記事に逐語一致しない**ことを確認する(逐語一致する残りがあれば、それも範囲候補として扱うか確定不能にするか、を明記)、(4)全断片が確定した場合だけ採用、1つでも確定不能なら人間確認、(5)引用符が無い文字列は、文字列全体で既存照合→不一致なら確定不能(再推測しない)。既存のL4(曲線引用符の断片分割、つなぎが接続語・句読点のみ)との関係(L4の一般化になるか、L4の条件を緩めることになるか)を明記。
- **案Q**: 案Pに加え、説明文側が位置だけで指した別箇所(U11・U12の見出し、in one line)を、同じ指摘の`same_fact_id_locations`の逐語から補う(別AIの引用ではなく同じChecker出力の別欄。ユーザー方針「別AIの引用で決めない」との整合を確認)。
- **案R**: Prompt最小追記のみ(schema不変、`claim_in_article`は単一文字列のまま)。「`claim_in_article`には記事本文からの逐語引用だけを入れ、位置の説明や理由は`issue`へ。複数箇所なら引用符で区切って並べる」の1〜3行。前回方式との違い(`claim_in_article`を外さない、配列にしない、『語句だけ』の指示を入れない)と、検出性能への影響の見込み(1-5の原因分析に基づく)、確認に必要な限定測定の規模・費用。
- **案S**: Recheckだけに手当てする(混入の実例8件が全てRecheckのため)。Recheckの指示文の調整、またはRecheckの出力に対してのみ案Pを厳格に適用、など。
- **案T**: 現状維持(確定不能は人間確認)。比較の基準線。
- 必要なら案U以降を追加(例: 引用符の付与をPromptで強制するだけ、など)。

**比較表**: ユーザーの9軸(検出性能/false PASS/Human Review/不要Rewrite/再推測による誤範囲/実装の複雑さ/初回・Recheck・retry・fallbackの整合/コスト/非決定性)+「12件のうち何件を解消できるか(型別)」+「Production配線時のリスク」。

## 作業3: 決定論的な案の¥0オフライン検証

案P(と案Q)のロジックを、runnerをimportしない独立スクリプト(`er052_output/open233_explanatory_mixed_offline_check_01/check_01.py`、標準ライブラリのみ。既存照合のロジックは`er052_output/open233_handoff_log_aggregation_01/aggregate_01.py`と委任_49の`replay_01.py`からコピー)で実装し、次に適用する:
- (a)12件: 各件で取り出した断片、確定した範囲(逐語)、残りのつなぎ、採用/確定不能とその理由。**意図した範囲(委任_45の「現行の対象が意図と一致していたか」の列と、各件のissueが指す箇所)と一致するか**を目視で判定し表にする。
- (b)既存のBLOCKING 346行全体: 案Pを通した場合に、確定→確定不能、確定不能→確定、範囲が変わる、の件数(委任_49の再生表と同じ形式)。**現行で正しく確定していた範囲が変わる・外れる例が1件でもあれば全件逐語で報告**。
- (c)委任_53の対照腕の出力(現行形式の実LLM出力、18 call分)に案Pを通した場合の結果。
- (d)非BLOCKINGの確定不能7行とK2の`same_fact_id_locations`14件(参考)。
- 結果は`results_01.json`・`cases_01.csv`に保存し、docに表で載せる。

## 作業4: 自己点検と、Opusに見てほしい論点

- ユーザー指示§8の自己点検: 「見送り以外の合理的な手段を十分検討したか」を、案ごとの根拠つきで書く(見送り[案T]を推奨する場合は、原因が特定不能/複数案を比較しても改善しない/副作用が大きい/QCD上合理性を失う、のどれに当たるかを示す)。
- Opusに見てほしい論点(ユーザー指示§7の10項目に対応づけて、材料がdocのどこにあるかを表にする)。
- 自分の推奨案と、推奨しない理由を明示(Fableが最終判断する)。

## 事前指定Read一覧

- `docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_45_result.md`: §2、§3、§5。
- `docs/pm/delegation_log/2026-10-03_OPEN-233-SELF-RECOVERY-TRIAL-01_53_result.md`: §(2)(3)(5)。
- `er052_output/open233_checker_spans_format_compare_01/`: `results_01.json`、`cases_01.csv`、生の応答(Pythonで必要フィールドだけ抽出。全文Readしない)。
- `er052_output/open233_handoff_log_aggregation_01/claims_detail_01.csv`、`unverified35_classification_01.csv`(cp932で読めない場合はutf-8/utf-8-sigを試す)、`aggregate_01.py`(照合ロジックの関数範囲)。
- `er052_output/open233_match_ext_replay_01/replay_01.py`: 全文(L5・単語境界のロジック)。
- `er052_open233_self_recovery_flow_runner_01.py`: Grep `resolve_violation_spans`、`_resolve_claim_string`、`vs_match_levels`、`_VS_FRAG_RE`、`VIOLATION_SPANS_INSTRUCTION`、`build_deviation_schema_with_spans`、`run_recheck`、`prior_issues`、`SAME_FACT_ID_ENUMERATION_INSTRUCTION`、`expand_same_fact_id_locations` → 該当範囲だけ(**読むだけ。委任_55が同時に編集中なので行番号は自分で確認**)。
- `er003_v1_en_direct_vfl_01_generate.py`: Grep `DEVIATION_PROMPT_TEMPLATE`、`"claim_in_article"` → 454〜470行・502〜601行(読むだけ)。
- `er051_open233_checker_trial_variant_01.py`: Grep `V4A` → 追記ブロック。
- `docs/pm/design_open233_countermeasures_after_handoff_01.md`: §3(288〜362行)。
- `docs/pm/opus_l2_review_open233_self_recovery_06.md`: Grep `論点6` → 該当範囲。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 上記のGrepパターン。追記・更新: なし。
- 新規doc: `docs/pm/design_open233_explanatory_mixed_countermeasures_01.md`(作業1〜4の全内容。ユーザーが読める日本語で、各節冒頭に結論2〜3行、数値に出所)。

## 実行コマンド全文

T-0:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-03_OPEN-233-SELF-RECOVERY-TRIAL-01_56.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-03_OPEN-233-SELF-RECOVERY-TRIAL-01_56.md_check.json

オフライン検証:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_output\open233_explanatory_mixed_offline_check_01\check_01.py

テスト・回帰は不要(コード変更なし)。

## SSOT追記文

なし(案文は不要。Fableが後で指示する)。

## Git(明示add対象・コミットメッセージ・trailer)

なし(git操作をしない。作成ファイルは未追跡のまま残す)。SSOT編集権: なし。

## 報告(RESULT_PACKET項目)

最終メッセージに: (1)結論10行以内(混入の型と件数、検出低下の原因の結論[支持された仮説]、推奨案と12件中の解消見込み、346行再生の悪化件数)、(2)作業1の要約(1-5は仮説ごとの支持/不支持を明示)、(3)案の比較表、(4)作業3の結果表(特に(b)の悪化例の逐語全件)、(5)自己点検とOpus論点、(6)T-0、作成ファイルの絶対パス、一覧外Read、確認できたことと推測の区別。

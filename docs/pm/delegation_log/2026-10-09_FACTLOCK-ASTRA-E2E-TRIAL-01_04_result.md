# 結果: FACTLOCK-ASTRA-E2E-TRIAL-01 委任_04(B3注記仕様 v2、2026-10-09)

Status: SPEC_V2_READY(Opus条件Aレビュー8件反映のv2。ユーザー確認待ち・未固定)。E2E Trial=DESIGN_READY(v2)維持、実行Go未。API支出¥0、Production変更なし、既存コード(`er0XX_*.py`)・Prompt・harness・`CURRENT_SPEC.md`・`OPEN_ITEMS.md`無編集。注記の実施(10記事)なし。
check_delegation_prompt.py結果: FAIL(必須セクション4種・固定ブロックE-1/D-1/G-1欠落。仕様改訂・スクリプト修正でAPI・長時間コマンドなしのため。続行)。記録=`2026-10-09_FACTLOCK-ASTRA-E2E-TRIAL-01_04_check.json`。

## 1. 成果物・commit・raw URL・テスト
- commit hash: (commit後に追記)
- `er052_output/factlock_astra_e2e_trial_01/` 配下: `B3_ANNOTATION_SPEC_v2.md`(完全版・改訂履歴・付録に注記者用逐語)、`B3_ANNOTATION_SPEC_v2_ANNOTATOR.md`(注記者用・架空例のみ)、`ANNOTATION_DELEGATION_TEMPLATE_v2.md`(10記事共通固定)、`B3_ANNOTATION_SPEC_v2_OLD4_EXPECTED.md`(隔離)、`B3_ANNOTATION_SPEC_v2_USER_SUMMARY.md`、`B3_SPEC_V2_SHA256.json`、`b3_annotation_check_01.py`(修正)、`b3_annotation_merge_01.py`(新設)、`b3_annotator_audit_01.py`(新設、事後監査)、`b3_old4_expected_eval_01.py`(新設)、`old4_expected_eval_01.json`、`b3_annotation_check_01_test.py`(拡張)、`spec_v2_evidence/`(テストログ・CLI実行結果)。委任_02の未commit分(`B3_ANNOTATION_SPEC_v1.md`、`B3_ANNOTATION_SPEC_v1_OPUS_POINTS.md`、`docs/pm/delegation_log/..._02*`)も同commit。
- SSOT等: `PREREGISTRATION_01.md`(v2.1、§5-11追加)、`NEW_THEME_CANDIDATES_01.md`(ユーザー選定結果節)、`DECISION_LOG.md`(末尾に1節)、`docs/pm/opus_a_review_factlock_astra_e2e_01.md`(B3レビュー節)、`docs/pm/OPUS_FINDINGS_LEDGER.md`(OF-103〜110)、`docs/pm/REPORT_LEDGER.md`(1行)、委任_04の記録3種。`ACTIVE_TASK.md`・`RESULT_PACKET.md`は.gitignore対象のため更新のみ。
- テスト: `.venv/Scripts/python.exe -X utf8 -m unittest er052_output.factlock_astra_e2e_trial_01.b3_annotation_check_01_test` = **40件 全PASS**(確認済み、ログ=`spec_v2_evidence/unittest_log.txt`)。内訳: v1由来13件(一部はv2の規則に合わせ期待値を更新: happy pathのfixtureを新優先順に、実artifactのホルムズ/宇宙兵器は「宇宙の2021年11月15日は不適格でFAIL」→「E2'で中核適格、PASS」へ反転、レイアウトは「宣言必須」→「定義済み挿入のみPASS_LAYOUT_NORMALIZED」へ)+新規27件(数字正規化、numeric_scope除外、主数字限定[交差廃止]、E2'のISO/和文、Storyline条件なし、分割挿入の逆変換、箇条書き分割PASS、`COSMOS 1408`→`COSMOS1408`検出、`。`以外への挿入拒否、架空中核、概念束ね不備、概念内kind、sha/annotator照合、台帳スキーマ・代替規則・非VERIFIED、unmapped_claims種類別、STOP候補、複合タグ禁止、付け漏れ、上限超過、注記者用仕様の架空例が検査PASS・汚染語なし、返答抽出・テンプレート充填、事後監査、merge4件[粗い方採用・再計算・ledger_ids空でSTOP・Jaccard集計])。
- CLI実測(確認済み): 注記者用仕様の架空例で `b3_annotation_check_01.py --spec ...` PASS(exit 0)、`b3_annotation_merge_01.py`(A=B同一入力)PASS・一致率1.0・フラグなし。結果=`spec_v2_evidence/smoke_cli_*.json`。
- raw URL: https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/factlock_astra_e2e_trial_01/B3_ANNOTATION_SPEC_v2_USER_SUMMARY.md 他(commit後にFableへの最終報告に全件記載)

## 2. v1→v2 変更点(Opus 8件対応)
1. 注記者用版の分離: 注記者用(架空例のみ、汚染源への言及なし。テストで汚染語の不在を検査)/完全版/OLD4_EXPECTED(隔離)/固定委任テンプレート。隔離は貼り付け渡し+`b3_annotator_audit_01.py`の事後監査。同モデル相関の限界を§I-1。注記者用仕様sha256=`8d145c3d...1e57`、テンプレート=`e77e1ed6...bf09`、全sha=`B3_SPEC_V2_SHA256.json`。
2. 中核・周辺はスクリプト計算(`compute_expected`)、宣言との完全一致検査(付け漏れ検出)、統合は`b3_annotation_merge_01.py`(統合入力から再計算)、判定線(分割0.8/Jaccard 0.67、推定値)を事前登録、数値0件の記事はJaccardから除き件数併記。
3. 数字比較: 10進正規化、`(numeric_scope: …)`除外、主数字限定、交差廃止。
4. E2→E2'(先頭の日付表現、年のみ対象外、Storyline条件なし、ISO/和文)。要約に「推奨」明記。
5. 分割・段落正規化: 定義済み挿入の逆変換で厳密一致。箇条書きbriefの分割もPASS。限定文が別台帳ID由来なら別事実にせずledger_ids追加。
6. 上限式は固定、文言を整合、外れた概念数を報告(`cap_dropped_count`)。Writerプロンプト(L72-79 規則5)に中核上限の記述なしを確認(影響なし)。
7. STOP範囲を2場合に縮小。`unmapped_claims`種類別。B3由来NG別集計を`PREREGISTRATION_01.md` §5-11に追加。
8. スクリプトの穴: 架空中核、概念束ね、sha/annotator照合、台帳スキーマ点検+代替規則、複合タグ禁止、%/漢数字は警告のみ、harness年月日分解は記録のみ。
- 実装上の追加判断(Fable確認要): (a) 注記者がsha256を計算できないため、`spec_sha256`/`brief_sha256`/`annotator`は委任文テンプレートの値をそのまま写させ、スクリプトが実ファイルと照合する方式にした。 (b) 注記者は引き続き中核/周辺を自分で宣言し(規則の機械適用可能性=Jaccardを測るため)、スクリプトの計算結果との一致を検査する(Opus点2の「注記者が選ぶのではなく計算」を「計算結果との完全一致を検査」と解釈)。 (c) 数値のE1は量/範囲のみ、日付はE2'のみに適用(日付が`numeric_value`に載っていても日付のE1適格にはしない)。

## 3. 旧4実測表の要約(`B3_ANNOTATION_SPEC_v2_OLD4_EXPECTED.md`、隔離)
- 数値表記17件(META 0・ホルムズ7・宇宙兵器6・ミニバッグ4): v2計算結果と過去の人手注記の**不一致0件**(全件一致)。事実数も全項目で同数(合計14事実: META3・ホルムズ3・宇宙5・ミニバッグ3)。v2規則から描画した注記版の自己検査は4件ともPASS(ミニバッグの描画結果は過去の注記版とバイト一致)。
- ホルムズ: 日付2概念が適格だが上限3で周辺(cap_dropped=2、過去と同じ分類)。宇宙兵器: `2021年11月15日`=E2'適格で中核(v1のE2では周辺だった食い違いが解消)。ミニバッグ: `2026年9月`・`2026年10月`=E2'適格で中核、台帳に`numeric_value`欄なし(代替規則が警告に出る)。
- 型別の不一致はなし。限界: 表記・種類・概念・台帳IDは固定表(人手作成)、事実分割は文のbigram重なりによる近似、過去注記は規則文書のない人手指定で、一致は規則の妥当性の証明ではない(循環の危険)。

## 4. ユーザー提示用要約(8項目、そのまま転記できる形)
`er052_output/factlock_astra_e2e_trial_01/B3_ANNOTATION_SPEC_v2_USER_SUMMARY.md` に全文(8項目の決定案+旧4実測要約+持ち越し項目)。要旨: (1)中核の条件=量は台帳数値欄の主数字との一致、日付はE2'(推奨)(2)上限式固定、閾値は新6で初めて検証(未確認)、Writerプロンプトに上限記述なし確認済み(3)名称内番号は案Y継続(4)台帳ID境界で分割、限定文は直前の事実、1項目最大3(5)A・B二重注記を決定論で統合、判定線0.8/0.67(推定値)、同モデル相関の限界(6)注記者用版分離+固定テンプレ+貼り付け渡し+事後監査(7)許す差分は定義済み挿入のみ・逆変換で厳密一致(8)STOPは2場合のみ、B3由来NGは別集計。

## 5. 未確認・Fable判断要
- 判定線(0.8/0.67)は根拠となる実測のない推定値(未確認)。上限式の閾値は新6で初めて検証(未確認)。新6の台帳が`numeric_value`・`date_or_period`欄を持つか(未確認、代替規則を事前登録)。
- 事後監査は「transcriptに残る範囲」の検出で、注記者のツール不使用は依頼文の指示であり技術的強制ではない。subagent transcriptの実際のjsonl形式で`b3_annotator_audit_01.py`が動くかは合成データのテストのみ(実transcriptでの動作は**未確認**、最初の注記委任後に1度確認が必要)。
- 注記者のFAIL時は再実行せずSTOP(各1回)の方針を踏襲。1文字の誤りで記事が止まるためSTOP率が高い恐れ(未確認)。緩和案(機械的な軽微修正1回の許容)は仕様変更になるためユーザー判断。
- ユーザー提案テーマ2件(BYD、USA Today/OpenAI)は候補10件の外。ニュース性・一次情報取得可否・台帳の育ち方はresearchまで未確認、research前にtopic文をFableが確定する必要。
- OPEN項目候補「B3自動注記」は起票未(Fable判断)。
- 改行コード注意(リスク): sha256は作業ツリー(LF)のバイト列で計算。リポジトリは`core.autocrlf=true`のため、Windowsで再checkoutするとCRLFに変換されsha256が合わなくなる恐れがある(`.gitattributes`に既存の`-text`先例あり)。凍結する注記者用仕様・テンプレート・スクリプトに`-text`を付けるか、sha256をLF正規化後に計算する運用にするかはFable判断(本委任では設定変更になるため未実施)。
- ユーザー提示用要約の項目5・6は3行をやや超える文章量。そのまま転記か圧縮かはFable判断。

## 6. 所要時間・API支出
- 所要: 厳密な計測なし(実装・テスト・文書・SSOT追記を1セッションで実施)。API支出: ¥0(LLM・web検索不使用)。

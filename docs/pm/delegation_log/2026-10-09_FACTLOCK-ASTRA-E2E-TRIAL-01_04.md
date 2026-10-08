管理ID: FACTLOCK-ASTRA-E2E-TRIAL-01 委任_04(B3注記仕様 v1→v2 改訂[Opusレビュー反映]+検証スクリプト修正+ユーザー決定記録+commit、API支出¥0、Production変更なし)。日付 2026-10-09。並行委任なし。

## 対象(委任_02成果物、未commit・未stage)
- `er052_output/factlock_astra_e2e_trial_01/B3_ANNOTATION_SPEC_v1.md`
- `er052_output/factlock_astra_e2e_trial_01/b3_annotation_check_01.py`、`b3_annotation_check_01_test.py`(13件PASS)
- `er052_output/factlock_astra_e2e_trial_01/B3_ANNOTATION_SPEC_v1_OPUS_POINTS.md`
- `docs/pm/delegation_log/2026-10-09_FACTLOCK-ASTRA-E2E-TRIAL-01_02.md`、`_02.md_check.json`、`_02_result.md`

## Opusレビュー結果(2026-10-09、Fable採用判断済み。以下を全て反映すること。「ユーザー提示前に必ず直すべき点」8件)
1. **注記者用の版を分離**: 仕様から §7(旧4の予想解答)と過去の注記版のパス・汚染源(`annotate_briefs.py`のSPEC、`ANNOTATION_LOG.md`、`astra_revise_matrix_02/DESIGN.md` L21、`prep_inputs.py` L47-49)への言及を除いた `B3_ANNOTATION_SPEC_v2_ANNOTATOR.md` を作り sha256 を固定・記録。例示が必要なら架空の記事で。Fable/評価用の完全版は `B3_ANNOTATION_SPEC_v2.md`(§7相当は別ファイル `B3_ANNOTATION_SPEC_v2_OLD4_EXPECTED.md` に隔離)。注記委任文は10記事共通の固定テンプレート(`ANNOTATION_DELEGATION_TEMPLATE_v2.md`、sha256固定、記事ごとの補足禁止)。隔離手段は (i) brief・台帳・注記者用仕様を委任文に直接貼り付け、出力も本文で返させFable/統合スクリプトがファイル保存 + (ii) 事後監査(subagent transcriptからRead/Grep/Globで開いたパスを抽出し参照禁止リストと照合、結果保存)の両方を仕様に明記(新agent定義の新設はしない=設定変更になるため)。A・Bが同モデルで誤りが相関し一致率が高めに出る限界を§8に明記。
2. **中核・周辺はスクリプトが計算**: 注記者が選ぶのではなく「数値の表記・種類・台帳ID・概念のまとまり」から `b3_annotation_check_01.py` が計算し、検査は計算結果との完全一致(付け漏れ=適格なのに上限内で周辺、も検出)。二重注記の食い違い解決は統合入力からの再計算(決定論の統合スクリプト `b3_annotation_merge_01.py` を新設、手作業禁止)。種類の食い違い(量か名称内番号か)と分割の食い違いは保守側規則のまま。一致率の判定線を事前登録(推定値: 分割一致率0.8未満 または 中核Jaccard 0.67未満で「規則を機械的に適用できていない」と報告。数値0件の記事はJaccard=1.0に含めず件数併記)。
3. **E1/E2の数字比較バグ修正**(`b3_annotation_check_01.py` L192-197, L246): 先頭0を除き int/float で正規化比較、`(numeric_scope: …)` を除外してから照合、照合対象は「主数字」(表記末尾の数字列、範囲なら両端。例「1バレル85ドル」→85)に限定、交差(1数字共通で可)の緩さを廃止。ISO形式(`2026-07-13 10:16 EDT`)と和文(`2026年9月14日`)の両方で日付一致が取れること。
4. **E2→E2'**: 「紐付く台帳factの `date_or_period` の先頭の日付表現とbriefの日付の数字が一致(年のみは対象外)。Storylineに出るかは条件にしない」。Opus手計算では旧4の過去人手注記(宇宙 2021年11月15日=中核、ミニバッグ 9月・10月=中核、ホルムズ 日付は上限で周辺、META 0件)と全て一致する見込み→ v2 のOLD4_EXPECTEDで**スクリプトで実測**し一致/不一致を記録。E2'は設計選択としてユーザー提示用要約に「推奨」と明記。
5. **分割・段落正規化の統一**: 許す差分を「Selected Facts節内で `。` の直後(または節の先頭)に `\n- ` を挿入」という定義済み操作のみに限定し、検査はその挿入を逆に除いた結果が原文と厳密一致することで行う(`canon_layout` の全空白削除比較を廃止。`COSMOS 1408`→`COSMOS1408`等の改変を検出)。箇条書きbriefの分割でFAILになる矛盾(§1 vs harness `FACT_LINE_RE` 行頭印のみ)を解消。限定文が別台帳ID由来の場合は「別事実にしない(S2より優先)、その台帳IDを `ledger_ids` に追加」と順位明記。
6. **「全件中核禁止」の文言を式と整合**: 式 `max(3, min(6, floor(n/2)))` は固定、文言は「上限は式による(n≤5では全件中核になりうる)」へ。優先順 Storylineにある量→その他の量→日付。上限で外れた概念数を記事ごとに必ず報告。§8-5「Writerプロンプトに中核上限なし」を確認済み・影響なしに更新(`er052_factlock_writer_trial_01_run.py` L72-79)。
7. **STOP範囲の縮小**: 台帳外の記述は印を付けず `unmapped_claims` に種類別(新事実/新数値/新因果/一般化/具体化/限定)で記録、注記はSTOPしない。評価時は該当文由来のNGを「B3由来」として両腕で別集計しFact Lock起因に数えない(事前登録事項として `PREREGISTRATION_01.md` にも1項追加)。STOPは (i) Storylineの主張そのもの(記事の骨格)が台帳に無い、(ii) 台帳に無い数字がE1/E2'適格の形で記事の中心にある、の2場合のみ。
8. **スクリプトの穴**: サイドカー宣言の数値表記が本文に1回も出ない(架空の中核)を検出/概念の束ね(概念内で台帳IDが同一、短い表記が長い表記に含まれる、種類判定を先頭要素だけにしない)/サイドカーの `spec_sha256`・`brief_sha256`・`annotator` を実ファイルと照合/台帳スキーマ点検(各記録の欄の有無を出力、量を示す語[％・ドル・個等]が本文にあるのに `numeric_value` が無い記録は警告、status VERIFIED確認、欄名が無い台帳で全数値が黙って周辺にならないよう代替規則[欄が無ければ `statement` 内の主数字で判定]を事前登録)。brief内の複合タグ(`【事実1,事実2】`)は禁止。`%`/`％`のNFKC・漢数字は警告のみ(持ち越し)。harness `load_core_numbers` の年月日分解による周辺数値見逃しは記録のみ(harness変更禁止)。
- 名称内番号は案Y(【周辺数値】印)継続。分割単位(台帳fact ID境界、主体・行為・時期で割らない、1項目最大3)は採用可。

## ユーザー決定の記録(2026-10-09、DECISION_LOG末尾追記)
- 新6テーマ確定(ユーザー選定): (1) BYDが18万台超をリコール、ブレーキペダル部品の欠陥が原因(ユーザー提案、理由: 183,211台・対象車種・製造期間・欠陥原因・安全リスクまで具体的で数字・対象範囲・因果を試せる) (2) USA TodayなどがOpenAIを著作権侵害で提訴(ユーザー提案、理由: 認定ではなく提訴段階、主体・主張・裁判ステータスを正確に扱えるか) (3) 中央銀行の金利判断と住宅ローンへの影響(候補#1) (4) 訪日外国人数が過去最高水準に(候補#7) (5) 動画配信サービスの値上げが続く(候補#8) (6) 半導体大手の決算とAI需要の行方(候補#2)。補欠(Fable提案をユーザー承認「貴殿提案でよいです」): 第1補欠 #10 コーヒー価格の高騰、第2補欠 #4 最低賃金の引き上げ。
- B3注記仕様: Opusレビュー実施(2026-10-09)、Fable採用判断=上記8件を反映したv2をユーザー提示用とする。
- `docs/pm/opus_a_review_factlock_astra_e2e_01.md` に「B3注記仕様 v1 レビュー」節を追記(Fable転記として上記要点)。`docs/pm/OPUS_FINDINGS_LEDGER.md` にOF-103以降で追記。
- `NEW_THEME_CANDIDATES_01.md` 末尾に「ユーザー選定結果」節を追記(6件+補欠2件)。
- `docs/pm/ACTIVE_TASK.md` 固定ヘッダ更新(委任_04=SPEC v2 READY、ユーザー確認待ち、実行Go未。既存UDR行維持)。`docs/pm/REPORT_LEDGER.md` 1行。

## 成果物・手順
1. 仕様 v2(完全版・注記者版・OLD4_EXPECTED・委任テンプレート)、改訂履歴 v1→v2(Opus論点番号対応)を冒頭に。
2. `b3_annotation_check_01.py` 修正+`b3_annotation_merge_01.py` 新設+テスト追加(既存13件+新規: 数字正規化、numeric_scope除外、E2'のISO/和文、分割挿入の逆変換一致、架空中核検出、概念束ね検出、sha照合、スキーマ点検、merge再計算 各1件以上)。`.venv/Scripts/python.exe -X utf8 -m unittest` で全件PASSさせる。
3. OLD4_EXPECTEDで旧4テーマ(META/ホルムズ/宇宙兵器/ミニバッグ)の元briefに v2 規則をスクリプトで適用し、計算結果(事実分割・中核/周辺)と過去の人手注記との一致・不一致を実測表にする(これは注記の実施ではなく規則の検証。注記者には見せないファイルとして隔離)。
4. `B3_ANNOTATION_SPEC_v2_USER_SUMMARY.md` — ユーザー提示用: ユーザーの8項目に対する決定を各3行以内(Opus要約を基に、E2'を「推奨」、上限式の閾値は新6で初めて検証される旨、人手注記の上限性能である旨を明記)+ 旧4実測表の要約 + 持ち越し項目。
5. 委任記録: 本委任文全文を `docs/pm/delegation_log/2026-10-09_FACTLOCK-ASTRA-E2E-TRIAL-01_04.md`、check結果、最終報告を `_04_result.md` と `docs/pm/RESULT_PACKET.md`。
6. Git: 委任_02の未commitファイル+本委任の作成・変更ファイルだけを明示的に `git add`(`git add -A`禁止)、commit、push。hashとraw URL報告。

## 禁止事項
- API生成呼び出し禁止(¥0)。既存コード(`er0XX_*.py`)・Prompt・`CURRENT_SPEC.md`・`OPEN_ITEMS.md`・harness(`er052_factlock_writer_trial_01_run.py`)の編集禁止。注記の実施(10記事)禁止。未確認数値を確定値として書かない。

## 報告形式(result.md)
1. 成果物パス・commit hash・raw URL、テスト件数・結果
2. v1→v2変更点(Opus 8件対応)
3. 旧4実測表の要約(過去注記との一致/不一致、件数・型)
4. ユーザー提示用要約(8項目、そのまま転記できる形)
5. 未確認・Fable判断要
6. 所要時間・API支出(¥0)

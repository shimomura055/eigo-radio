管理ID: FACTLOCK-ASTRA-E2E-TRIAL-01 委任_02(B3注記仕様 v1 の作成、API支出¥0、Production変更なし、**git操作禁止**=並行する委任_03がcommitするため、本委任はファイル作成と報告のみ)。日付 2026-10-09。

## 背景・ユーザー決定(2026-10-09、逐語)
ユーザーは次を決定した: 「B3: 今回のTrial前に、正式なTrial仕様として先に固定すべきです。今のまま人が都度判断して【事実N】や重要数値を付けると、記事ごとに条件が揺れてしまい、Fact Lockそのものの性能が測れません。Trial開始前にたとえば以下を決める必要があります。
- 何を【事実N】として分けるか
- 1つの事実に複数要素がある場合の分け方
- どの数字を「重要数値」とするか
- 数字が記事の主役の場合の扱い
- 名称内番号(COSMOS 1408等)の扱い
- 注記してよい情報は台帳由来だけ、という制約
- 注記者が迷った場合のルール
- 注記後に元台帳との照合をどうするか
そして、その固定仕様で旧4+新6の全10記事を同じように注記してTrialするのがよいです。」
手順: B3注記仕様作成(¥0)→Opusレビュー→ユーザー提示・確認→E2E実装・実行。本委任は最初の「仕様作成」のみ。**注記の実施(旧4テーマの再注記を含む)は本委任では行わない**(仕様がユーザー確認されてから)。

## 事前指定Read一覧(SSOT全文読込禁止)
- `docs/pm/PM_BRIEF.md`(固定ヘッダ)
- Fact Lock v1 の仕様・結果: `er052_output/factlock_writer_trial_01/RESULT.md`、同ディレクトリ内の設計書(DESIGN*.md をGlobで特定)、`annotate_briefs.py`(Globで特定。現行のSPEC文字列・注記手順)、既存の注記版brief(META/ホルムズ/宇宙兵器: `inputs/`または`runs/*/b*__factlock__*/`配下の`selected_brief_factlock.md`相当をGlobで特定)、`er052_output/factlock_writer_trial_01/astra_revise_matrix_02/inputs/small_bag/selected_brief_factlock.md`(ミニバッグ、「Selected Facts分割(3事実化)と数値注記は人間が決めた」という記録がREPORT §108にある)
- 各テーマの元B3 brief(`selected_brief.md`)と台帳(`verified_fact_ledger.txt`、fact ID・conditions・scope・notesの構造)。4テーマ分の所在は`er052_output/factlock_astra_e2e_trial_01/DESIGN_E2E_01.md`の凍結入力節に記載。
- `er052_output/factlock_writer_trial_01/eval/residual_analysis/RESIDUAL_NG_VS_CHECK.md`(タグ検査で拾えたNG/拾えなかったNG)
- `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md` §104〜§108(Grepで見出し特定、該当範囲のみ。Fact Lockの数値規則(c)中核/周辺注記、タグ検査結果)
- Opus条件Aレビュー(本委任文末尾にFableが要点を転記): 論点5=「注記ルールを固定しsha256で凍結、注記者には生成結果も腕も見せない、別workerによる独立二重注記で一致率を記録、不一致はルール文書で機械的に決定、strip_tags(注記版)=旧腕B3原文をG0で照合(er019再利用分岐はJSON `fact_selection_evidence.json` の `selected_fact_brief_text` を読むためJSONも照合対象)、旧4は過去注記者・新6はSonnetなので層別報告」。

## 成果物(新規ファイルのみ、既存ファイル編集禁止)
1. `er052_output/factlock_astra_e2e_trial_01/B3_ANNOTATION_SPEC_v1.md` — 注記仕様 v1。必須節:
   - §0 目的・適用範囲(本Trialの旧4+新6全10記事に同一適用。過去の注記版は使わず再注記する)。
   - §1 入力・出力の定義(入力=元B3 brief + 台帳。出力=注記版brief(md)と、Writerが読むJSON側の対応。strip_tags後は元brief原文と完全一致でなければならない=注記は追加のみ、削除・言い換え禁止)。
   - §2 【事実N】の分割規則: 何を1事実とするか(台帳fact ID単位を原則とするか、brief の Selected Facts の項目単位か、を明確に決める。複数要素を含む1項目の分け方: 主体・行為・対象・時期・数量のうち独立に誤りうる要素を分ける基準、分けすぎを防ぐ上限)。番号付与の順序(brief出現順)。
   - §3 重要数値(中核)の規則: 何を中核とするか(台帳に明示があり記事の主張を支える数量・日付・割合等)、周辺数値との区別、数字が記事の主役の場合(例: 価格高騰・統計記事)の扱い(中核が多数になる時の上限や全件中核の可否)、**名称内番号(COSMOS 1408、GPT-6等)は数値扱いしない**規則、年号・序数・単位・範囲(「3〜5%」)・概数(「約」)の扱い、ヘッジ語(「約」「一時」「最大で」)を数値と一体で注記するか。
   - §4 台帳由来制約: 注記してよい情報は台帳(fact ID・conditions・scope・notes)に存在するものだけ。brief にあって台帳に無い記述は注記しない(その事実はフラグ列挙して報告)。注記に台帳fact IDを併記するかどうかを決める(Writerへの入力に含める/含めないの別と、含めない場合の照合用サイドファイル)。
   - §5 迷った場合の規則(決定木): 判断不能時のデフォルト(例: 分割は「分けない」、中核判定は「周辺」等)を明文化し、迷い箇所を必ず`annotation_notes`に記録。
   - §6 照合・検証手順: (a) strip_tags(注記版)==元brief原文(md・JSONの両方)のsha256照合、(b) 全【事実N】が台帳fact IDに1対1以上で紐付く、(c) 中核数値の表記が台帳の表記と一致(surface差は記録)、(d) 番号の連番性、(e) 二重注記プロトコル(注記者A/B独立、生成結果・腕を見せない、一致率の定義=分割一致率・中核数値指定一致率、不一致の機械的解決規則と記録)、(f) 注記者が参照してよいもの/いけないもの。
   - §7 旧4テーマへの適用例: META・ホルムズ・宇宙兵器・ミニバッグの元briefに本仕様を適用した場合の**例示**(実注記ではなく「この規則ならこう分割され、中核数値はこれ」という表。過去の注記版との差分を併記し、過去注記が本仕様とどこで食い違うかを明示)。
   - §8 既知の限界: Production化にはB3の自動注記が必要(本Trialは人手注記の上限性能)、Luna FCが「不在・未成立」型を取り逃す件との関係、等。
   - §9 変更禁止事項(Trial中に仕様を変えない。変更が必要ならSTOPして記録)。
2. `er052_output/factlock_astra_e2e_trial_01/b3_annotation_check_01.py` — 決定論の検証スクリプト(¥0、LLM不使用): §6(a)〜(d)を機械チェックしJSONで結果出力。CLI: `--brief <md> --annotated <md> --ledger <txt> [--json <fact_selection_evidence.json>]`。単体テスト(`b3_annotation_check_01_test.py`、5件以上)を同ディレクトリに置き、`.venv/Scripts/python.exe -m unittest` でPASSさせる。既存の`strip_tags`相当の関数があれば import せず、同一ロジックをコピーして出典行を注記(既存ファイル編集禁止のため)。
3. `er052_output/factlock_astra_e2e_trial_01/B3_ANNOTATION_SPEC_v1_OPUS_POINTS.md` — Opusレビューに出す論点(5〜7個)と、Sonnetが判断に迷った設計選択(複数案と採った案・理由)。
4. 委任記録: 本委任文全文を `docs/pm/delegation_log/2026-10-09_FACTLOCK-ASTRA-E2E-TRIAL-01_02.md` に保存、`python docs/pm/tools/check_delegation_prompt.py --file <path>` の結果を記録(FAILでも続行)。最終報告は `docs/pm/delegation_log/2026-10-09_FACTLOCK-ASTRA-E2E-TRIAL-01_02_result.md` に書く(**`docs/pm/RESULT_PACKET.md`は使わない**=並行委任との衝突回避)。

## 禁止事項
- API生成呼び出し一切禁止(¥0)。git add/commit/push禁止。既存ファイルの編集禁止(DECISION_LOG/ACTIVE_TASK/REPORT_LEDGERも本委任では触らない=委任_03が担当)。
- 注記の実施(旧4の再注記・新6の注記)禁止。
- 未確認事項は「未確認」と明記。仕様の中で「人が判断する」余地を残す箇所は、残す理由と記録方法を必ず書く。

## 報告形式(result.md)
1. 成果物パス一覧、テスト結果(件数・PASS)
2. 仕様の要点(ユーザーの8項目それぞれに対する決定を1行ずつ)
3. 旧4テーマ適用例での過去注記との食い違い(件数・主な型)
4. Opusに出す論点
5. 未確認事項・Fable判断が必要な点
6. 所要時間・API支出(¥0であること)

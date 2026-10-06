## 管理ID
OPEN-233-LEDGER-CLARITY-DESIGN-01(委任_01a: 既存仕様調査—Fact台帳の生成・検証工程、既存ルール、整合点、費用構造。read-only、¥0)。並列委任_01b(事例収集)、_01c(Trial評価設計)、_01d(SSOT先行起票)が同時進行。**書込先: `docs/pm/ledger_clarity/01_current_pipeline.md`(新規、150行以内)、`docs/pm/delegation_log/`のみ。コード・SSOT・git変更なし。API呼出なし。**
作業方式: 説明最小、Bash heredoc不使用、Write/Edit 1回40行以内。T-0はWrite+Edit追記で逐語保存(必須見出し3つを含む)。時間目安25分。

## 性質/到達上限Status/禁止事項
性質: ¥0既存仕様調査(設計の入力)。禁止: 有料API/コード変更/CURRENT_SPEC編集/推測を事実として書く(【確認】【推測】、根拠=ファイル・行・管理ID)。Opus Gate: 設計案に対し条件Aレビューを別途実施(本委任は入力)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力不使用。F-1: 退避不要。T-1: 事前指定一覧に従う(一覧外は理由記録)。T-0(常時有効): 委任文を`docs/pm/delegation_log/2026-10-06_OPEN-233-LEDGER-CLARITY-DESIGN-01_01a.md`へ逐語保存し`check_delegation_prompt.py`実行、結果1行を最終報告へ。T-2/T-2追記(7-5): TTSなし。T-3: 対象外。

## ユーザー指示(原文、要点)
> 設計案で明確にすること: 現行Fact台帳はどの工程で生成・検証されているか/既存の曖昧表現防止・時系列・因果関係のルールは何か/今回の改善で追加・変更が必要な部分はどこか/単なるPrompt改善で対応可能か、それ以外の仕組みが必要か/Fact分割時に既存のID・Fact数・Writer・Checkerとの整合性をどう守るか/Factの正確性を誰が、どの段階で検証するか/自動修正に失敗した場合、既存の安全な経路へ戻せるか/費用・処理時間がどの程度増える見込みか。既存機能との重複を避け、最小限の変更で実現できる設計を優先。

## 調査内容(各項目: 結論1〜3行+根拠)
A. 台帳の生成工程: `verified_fact_ledger.txt`を生成するscript・prompt・modelを特定。入力(原資料)、出力形式(fact block構造、`ledger_block_fields`定義)、1 fixtureあたりfact数、生成費用。
B. 台帳の検証工程: 生成後にFactの正確性を検証する既存処理の有無(`er012_output/.../audit/fact_check.json`の生成元)。誰が(AI/決定論/人間)、どの段階で、何を検証するか。
C. 既存ルール: 台帳生成promptおよびCURRENT_SPECにある曖昧表現防止/時系列/因果関係/主体・対象の明示/不確実性の保持のルールをGrepで逐語抽出(CURRENT_SPEC全文Read禁止)。
D. Writer側の台帳の使い方: 台帳をどう渡しているか(全文/選択/notes含む)、「推測禁止」等の指示。
E. 整合点: fact_idの参照箇所一覧(`SAFETY_CRITICAL_CLAIM_DEFS`、fixture、Checker r3の`support_fact_ids`、Stage 2の`related_fact_id`、`floor_verify_fact_block`、labels)。分割(1→2 ID)/書き換え(ID維持)それぞれで壊れる箇所を表に。ID維持本文明確化案と子ID(HC-012a/b)案の影響差。
F. 安全経路: 自動明確化が失敗した場合に「従来台帳のまま進む」fail-safeを置ける工程上の分岐点。
G. 費用・時間: 台帳生成1回の費用・時間、明確化追加時の追加call数見込み(fact数×1または台帳全体1回)。
H. 「Prompt改善のみで足りるか/別機構が必要か」の判断材料(事実のみ)。

## 事前指定Read一覧
Grep結果の範囲Readのみ(各40行以内)。

## 事前指定Grep一覧+追記位置・更新位置の手順
上記A〜HのGrep。新規ファイルのため追記位置なし。CURRENT_SPEC/DECISION_LOG全文Read禁止。

## 実行コマンド全文
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-LEDGER-CLARITY-DESIGN-01_01a.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-LEDGER-CLARITY-DESIGN-01_01a.md_check.json`

## SSOT追記文
なし。

## Git
なし。

## 報告(RESULT_PACKET項目)
最終報告8行以内(生成script/prompt/model、検証の有無、既存ルールの有無、ID整合の要点、fail-safe位置、費用、T-0)。RESULT_PACKETファイル不要。
(注: 調査内容A〜Hと固定ブロックは要点圧縮して保存。逐語の細部のGrepパターン例は省略。)

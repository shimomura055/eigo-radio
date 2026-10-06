## 管理ID
OPEN-233-LEDGER-CLARITY-DESIGN-01(委任_02: 設計案の作成。Phase A成果物①②③を統合し、Opus条件Aレビューに出せる設計docを書く。¥0)。**書込先: `docs/pm/ledger_clarity/04_design.md`(新規、200行以内)、`docs/pm/delegation_log/`のみ。コード・SSOT・CURRENT_SPEC・git変更なし。API呼出なし。**
作業方式: §ごとにEdit追記(1回40行以内)、Bash heredoc不使用、説明最小。T-0はWrite+Edit追記で逐語保存(必須見出し3つを含む)。時間目安25分。

## 性質/到達上限Status/禁止事項
性質: 設計(¥0)。到達上限: DESIGN_READY_FOR_REVIEW(Opus条件Aレビュー前)。禁止: 有料API/Trial実行/Production実装/CURRENT_SPEC更新/新Product仕様の「決定」記載(選択肢として提示)/事実の追加・改変を伴う明確化例の確定(【案】と原資料照合未了を明記)/S1等の採否変更。Opus Gate: 条件A必須(本doc完成後にFableが依頼)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力不使用。F-1: 退避不要。T-1: 事前指定一覧に従う。T-0(常時有効): 委任文を`docs/pm/delegation_log/2026-10-06_OPEN-233-LEDGER-CLARITY-DESIGN-01_02.md`へ逐語保存し`check_delegation_prompt.py`実行、結果1行を最終報告へ。T-2/T-2追記(7-5): TTSなし。T-3: 対象外。

## ユーザー指示(原文、要点)
> 方針A: Factは明確に(何が起きた/誰が何を/何がどう変化/どの時点/因果確認の有無)、複数解釈を避ける。B: 複雑なFactは適切に分割(HC-012例・ホルムズ例、原資料との意味一致を必ず確認)。C: Writerに不要な推測をさせない(ただし表現・構成は過度に拘束しない)。必須条件: ①事実を追加・改変しない ②Fact同士の関係(時系列・因果・条件・対象範囲)を維持 ③記事Qualityを維持 ④量産可能な自動処理(既存機構を優先、追加費用・待ち時間・運用負荷を抑える)。設計案で明確にすること: 生成・検証工程/既存ルール/追加・変更箇所/Prompt改善で足りるか/分割時のID・Fact数・Writer・Checker整合/正確性を誰がどの段階で検証/失敗時に安全経路へ戻せるか/費用・時間増。既存機能との重複を避け最小限の変更で。大きな設計変更や新Product仕様が必要な場合は選択肢として報告。

## 入力(必読)
`docs/pm/ledger_clarity/01_current_pipeline.md`、`02_cases.md`、`03_trial_eval_design_draft.md`(内容要約は元委任文に記載、省略)。

## 設計docの構成(§ごと、各項目に根拠パスを付す)
§0 要約(5行) / §1 現行仕様の確認(10行) / §2 問題の定義(HC-012/HF-009のBefore逐語・誤読実例・同型の曖昧Fact高3中14・共通構造(a)多義語(b)途中/最終の複数事象(c)主体・対象省略(d)因果確認有無不明) / §3 設計案比較(案P=Prompt強化のみ、案C=Verification直後に台帳全体1回の明確化パス・ID維持・events構造、案C+V=案C+意味一致の自動検証・fact単位fail-safe+工程fail-safe(推奨)、案S=子ID分割(不採用理由明記)、比較表) / §4 Before/After具体例(【案】原資料照合未了を明記) / §5 検証責任と段階 / §6 Writer/Checkerとの整合(SAFETY_CRITICAL_CLAIM_DEFSの定義が記事側かをGrep確認) / §7 既存fixtureへのoffline適用(DEV限定の台帳パス差替え引数) / §8 費用・時間(案C≈¥1・30〜60秒【推測】、案V+≈¥1、fact単位¥10〜15は不採用) / §9 Opusレビュー論点(ユーザー7観点+途中/最終構造と方向反転Checkerの干渉・quote変更のChecker影響・self-check同一モデル相関) / §10 Trial計画との接続 / §11 Dangling Reference候補のGrep確認 / §12 Status案(新Product仕様に当たる台帳スキーマ拡張・Writer向け出力形式は選択肢として列挙)。

## 事前指定Read一覧
1. `docs/pm/ledger_clarity/01_current_pipeline.md`、`02_cases.md`、`03_trial_eval_design_draft.md`: 全文。
2. `er003_v1_en_direct_vfl_01_generate.py`: Grep `def build_verified_ledger_text|notes_for_writer|causal_strength` →範囲Read(40行以内、出力形式確認)。

## 事前指定Grep一覧+追記位置・更新位置の手順
§6: runner Grep `SAFETY_CRITICAL_CLAIM_DEFS` →範囲Read(定義が記事側文か台帳文か)。§11: 上記関数・ファイルのGrep/Glob。新規ファイルのため追記位置なし。

## 実行コマンド全文
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-LEDGER-CLARITY-DESIGN-01_02.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-LEDGER-CLARITY-DESIGN-01_02.md_check.json`

## SSOT追記文
なし。

## Git
なし。

## 報告(RESULT_PACKET項目)
最終報告8行以内(推奨案、費用時間増、ID整合方針、fail-safe、新Product仕様候補、Dangling結果、T-0)。

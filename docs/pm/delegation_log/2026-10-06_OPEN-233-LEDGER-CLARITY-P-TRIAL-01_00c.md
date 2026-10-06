## 管理ID
OPEN-233-LEDGER-CLARITY-P-TRIAL-01(委任_00c: Before Evidence固定、Phase 0、¥0)

## 性質/到達上限Status/禁止事項
性質: 集計・固定(read-only+固定ファイル作成)。到達上限: Phase 0報告。禁止: コード変更/有料API/Trial実行/Production変更/SSOT編集/git/新テーマ追加/既存artifactの変更。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1/D-1/G-1/F-1: 該当なし(¥0)。T-0: 本委任文を `docs/pm/delegation_log/2026-10-06_OPEN-233-LEDGER-CLARITY-P-TRIAL-01_00c.md` に逐語保存し `python docs/pm/tools/check_delegation_prompt.py --file <パス> --json-out <同名_check.json>`(FAILでも続行)。T-2/T-2追記(7-5): TTSなし。T-3: 対象外。

## ユーザー指示(原文、要点)
「Phase 0: 既存Evidenceから、HC-012 Rollback型/その他の既知重大NG/既存Checkerベース構成/比較対象となる記事・Fact台帳を固定。新しいテーマを追加しない。」「Phase 1でBefore/Afterを最低限、Fact意味一致/HC-012型の曖昧さ/B3 brief/Writer記事/真の重大NG/Checker判定/Entertainment品質まで比較する。」Entertainment: 説明的すぎ・台帳逐語コピー・ストーリー性・テンポ・硬さの比較で従来品質を維持。

## 事前指定Read一覧
- `docs/pm/ledger_clarity/02_cases.md`(HC-012/HF-009の事例と曖昧fact棚卸し、全文)
- `docs/pm/ledger_clarity/05_trial_plan.md` §1(品質評価の事前定義。Entertainment決定論指標の定義を流用)
- `er019_output/meta/run_03/ledger/verified_fact_ledger.txt`(Before台帳、全文)
- `er019_output/meta/run_03/storyline_b3/selected_brief.md`(11行)
- `er019_output/meta/run_03/ja_writer/original.md`(14行)、`er019_output/meta/run_03/b1b/article.md`(21行)

## 事前指定Grep一覧+追記位置・更新位置の手順
1. metaテーマのBefore資産を固定: 上記台帳txt・`research_ledger/fact_ledger_draft.json`・verification結果JSON(Glob `er019_output/meta/run_03/**/*.json` でパスのみ列挙)。各sha256を記録(PowerShell `Get-FileHash -Algorithm SHA256`)。
2. metaテーマの既存Writer出力・Checker判定: Glob `er052_output/open233_prod_e2e_0*/runs/meta*` と `er052_output/open233_prod_e2e_0*/runs/*meta*` → run id一覧、各runの最終記事パス、Checker最終判定(重大件数・Rewrite回数・human_review)を集計ファイルからGrep(大量読込しない。`summary`/`report`系JSON/MDの該当行のみ)。
3. HC-012 Rollback型のBefore記録: Grep `HC-012` を `er052_output/open233_prod_e2e_0*/` の集計md/jsonl で行い、各runで「restored/put back/以前の状態」型の文が出たか・Checkerが拾ったかを表にする(run id/文(逐語20語以内)/Checker検出/human review結果)。
4. その他既知重大NG(gold): runner `er052_open233_self_recovery_flow_runner_01.py` L9817-9900 の `SAFETY_CRITICAL_CLAIM_DEFS` から、metaテーマに関係するgold定義のID・related_fact_id・text_substringを列挙(逐語可)。
5. Entertainment基準値(決定論、Before): meta記事EN(b1b/article.md と E2Eの最終記事)について、文数・平均文長(語)・type-token比・台帳逐語コピー率(台帳txtの8語以上の連続一致がEN記事中に占める割合、簡易Pythonで算出。scratchpadにscriptを置き、結果だけ記録)。
6. 固定ファイル: `er052_output/open233_ledger_clarity_p_trial_01/phase0/FREEZE_P01.json`(Before資産パス・sha256・run id一覧・gold ID一覧・Entertainment基準値・作成日時)と `docs/pm/ledger_clarity_p_trial/00c_before_evidence.md`(60行以内、表形式)。
7. 比較対象は**metaテーマ1本に限定**(¥50上限のため)。hormuz/small_bagは「held-out候補、今回は対象外」と明記。

## 実行コマンド全文
- `python docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-06_OPEN-233-LEDGER-CLARITY-P-TRIAL-01_00c.md --json-out docs/pm/delegation_log/2026-10-06_OPEN-233-LEDGER-CLARITY-P-TRIAL-01_00c_check.json`
- Entertainment指標: `python <scratchpad>/ent_metrics_before.py`(新規、scratchpad配置。出力はFREEZE_P01.jsonへ)

## SSOT追記文
なし。

## Git
なし。

## 報告(RESULT_PACKET項目、12行以内)
(1)Before台帳のfact数・HC-012のclaim(逐語) (2)meta Before run数とHC-012型の発生/検出表の要約 (3)metaに関係するgold ID一覧 (4)Entertainment基準値 (5)FREEZEファイルパス・sha256件数 (6)T-0結果 (7)出力パス・行数

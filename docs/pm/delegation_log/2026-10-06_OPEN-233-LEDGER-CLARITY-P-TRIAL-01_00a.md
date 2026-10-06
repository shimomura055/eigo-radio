## 管理ID
OPEN-233-LEDGER-CLARITY-P-TRIAL-01(委任_00a: ベースChecker構成の特定・固定、Phase 0、¥0)

## 性質/到達上限Status/禁止事項
性質: 調査(read-only+報告ファイル1本+ACTIVE_TASK更新)。到達上限: Phase 0報告。禁止: コード変更/有料API/Trial実行/Production変更/SSOT(CURRENT_SPEC・DECISION_LOG・OPEN_ITEMS・REPORT)編集/git。「ユーザー承認」を創作しない(承認Evidenceが見つからないものは「未確認」と書く)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1/D-1/G-1/F-1: 該当なし(¥0調査)。T-0: 本委任文を `docs/pm/delegation_log/2026-10-06_OPEN-233-LEDGER-CLARITY-P-TRIAL-01_00a.md` に逐語保存し `python docs/pm/tools/check_delegation_prompt.py --file <パス> --json-out <同名_check.json>` を実行(FAILでも続行、結果を報告)。T-2/T-2追記(7-5): TTSなし。T-3: 対象外。

## ユーザー指示(原文、要点)
「比較のベースは、ユーザー確認済みの以下のChecker構成とする。(1)『Ledgerに書いていない』だけではNG候補にしない。(2)Ledgerとの矛盾、具体的新事実の追加を主に確認する。(3)主体・相手先・範囲・限定条件を照合する。(4)後段の機械的な重大判定は数字の不一致のみ残す。(5)主体・否定・比較・時期・因果などは、機械的に重大NGへ強制昇格させない。(6)Stage 2等、既存のAI判定構成は変更しない。今回Checker仕様は変更しない。実行前に、このベース構成の管理ID・設定・実測EvidenceをRepo上で特定して固定すること。曖昧ならSTOPして報告する。」

## 事前指定Read一覧
- `docs/pm/design_open233_stage1_loop3_prep_01.md`(全文32行。「案イ」=問いの転換が未決定と記載。これが後日承認・実装されたかを本委任で確定する)
- `docs/pm/factcheck_judgment_inventory_01.md`(全文。判定処理の棚卸しと承認状況)
- `er052_open233_self_recovery_flow_runner_01.py` L490-530 のみ(`OPEN233_APPROVED_FLOW_SWITCHES`)

## 事前指定Grep一覧+追記位置・更新位置の手順
1. `DECISION_LOG.md`: Grep `number_only` / `FLOOR_MODE` / `案イ` / `問いの転換` / `3択` / `STAGE1_QUESTION` / `OPEN-233-STAGE1-CHECKER-RECOVERY` / `OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01` → 該当エントリの管理ID・日付・「ユーザー承認」の文言の有無を抜き出す(各エントリ3行以内)。
2. `OPEN_ITEMS.md`: Grep `OPEN-233` の本体行(Status語: APPROVED/PRODUCTION_WIRED/VALIDATED/USER_DECISION_REQUIRED)。
3. `er052_open233_stage1_coverage_checker_01.py`: Grep `Ledger` / `矛盾` / `追加` / `候補` / `主体` を含むprompt文字列の行番号。Stage 1の現行「問い」が上記(1)〜(3)に該当する文言かを引用(各5行以内)。
4. runner: Grep `FLOOR_MODE` / `number_only` / `CAUSAL_FLOOR` / `negation_polarity_mismatch` / `changed_subject` / `changed_negation` / `changed_time` / `changed_causal` で、上記(4)(5)「数字不一致のみ機械的重大、他は強制昇格なし」が現行承認スイッチ下で成立しているかを行番号付きで確認。
5. `docs/pm/factcheck_judgment_inventory_01.md` の S1/disclosure_gap/hook_aware 等「Fable判断のみ」項目が、ベース構成(6)「Stage 2等既存AI判定構成は変更しない」にどう関わるか(=現状ONのまま固定すればよいか、未承認であることを明記)。
6. 実測Evidence: `er052_output/open233_prod_e2e_02/` または E2E 9/20 run の集計ファイル(Glob `er052_output/open233_prod_e2e_0*/report_final/*.md`、`*summary*.json`)の**パスとrun数・テーマ別run id**のみ(内容の大量読込はしない。meta テーマのrun idと保存先を列挙)。
7. 判定: 上記(1)〜(6)それぞれについて「管理ID/設定箇所(ファイル:行)/ユーザー承認Evidence(DECISION_LOG行)/実測Evidence(run id)」の4列表を作る。1つでも「承認Evidenceなし」「設定箇所が特定できない」「ユーザー指示文と実装が食い違う」があれば `STOP_RECOMMENDED` と明記し理由を書く。
8. 出力: `docs/pm/ledger_clarity_p_trial/00a_base_checker_config.md`(新規、60行以内)。
9. `docs/pm/ACTIVE_TASK.md` を上書き: 管理ID=OPEN-233-LEDGER-CLARITY-P-TRIAL-01、Status=APPROVED FOR TRIAL(Production採用ではない)、上限¥50、到達可能Status=REJECTED/VALIDATED/USER_DECISION_REQUIRED、禁止事項(Research方法変更/台帳生成処理変更/新Checker仕様/Production変更/残11 run再開/予算超過/seed・記事の勝手な追加)、STOP条件10項目(ユーザー指示のとおり)、Phase 0=3並列(00a/00b/00c)、★報告13項目、他IDのUDR待ち(S1・TRIAL-03次方針・残11 run・LEDGER-CLARITY判断)は前版の行を維持。

## 実行コマンド全文
- `python docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-06_OPEN-233-LEDGER-CLARITY-P-TRIAL-01_00a.md --json-out docs/pm/delegation_log/2026-10-06_OPEN-233-LEDGER-CLARITY-P-TRIAL-01_00a_check.json`

## SSOT追記文
なし(本委任ではSSOT編集なし)。

## Git
なし。

## 報告(RESULT_PACKET項目、12行以内)
(1)4列表の要約(6項目それぞれ: 特定済み/未確認) (2)STOP_RECOMMENDEDの有無と理由 (3)現行Stage 1の問いの文言(逐語、3行以内)と案イとの関係 (4)metaテーマのBefore run id一覧と保存先 (5)T-0結果 (6)出力ファイルパス・行数

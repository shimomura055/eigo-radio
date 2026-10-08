# FACTLOCK-WRITER-REDESIGN-TRIAL-01(委任_01、2026-10-08)

(注: Fableからの委任文の要約保存。原文はセッション履歴。主要項目は全て保持。)

## 管理ID
FACTLOCK-WRITER-REDESIGN-TRIAL-01(委任_01: 設計・harness・事前登録・brief注記。API課金なし)。並行タスク ALL-6-LUNA-WRITER-REDESIGN-NECESSITY-TRIAL-01(別agent実行中、出力 er052_output/all6_writer_redesign_necessity_01/、RESULT_PACKET.md・ACTIVE_TASK.md・SSOT・Gitを使用中)。

## 性質/到達上限Status/禁止事項
- 性質: Trial準備(Writer根本設計「Fact Lock」の設計書・harness・事前登録・brief注記)。到達上限Status: DESIGN_READY_FOR_OPUS_A。記事生成・課金は本委任では行わない(生成は委任_02)。
- 隔離規則: (1)書込は er052_output/factlock_writer_trial_01/ 配下と新規 er052_factlock_writer_trial_01_run.py / er052_factlock_writer_trial_01_test_01.py / docs/pm/RESULT_PACKET_FACTLOCK.md / 本ファイル(+_check.json)のみ。(2)docs/pm/RESULT_PACKET.md・ACTIVE_TASK.md・CURRENT_SPEC.md・DECISION_LOG.md・OPEN_ITEMS.md・REPORT・REPORT_LEDGER編集禁止。(3)git add/commit/push禁止。(4)all6_writer_redesign_necessity_01/・open233_b3_trial_01/runs/への書込禁止(読取のみ)。(5)有料API禁止(単体テストはmockのみ)。(6)重いpython並列処理を起動しない。
- Production変更禁止(er019_family_x_ja_writer_o_r1_r2_01.py / er003_v1_en_direct_vfl_01_generate.py / er006_model_routing_contract_01.py等は編集しない)。prompt/モデル差替えはharness側monkeypatch(require_model_or_override(..., override_reason="FACTLOCK-WRITER-REDESIGN-TRIAL-01"))。
- 費用: 本委任¥0。委任_02の見込みは設計書に記載(24本・上限¥150 Guardrail、T-3定型文)。
- Opus独立技術レビューGate: 条件A該当(必須)。実装(生成開始)前にレビュー。

## 固定ブロック
E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3(T-2: TTS伴わない。T-3: 委任_02向け費用上限は設計書内に定型文)。

## ユーザー指示(原文要旨)
- 「やりたいのは、エンターテイメント性はRevise1,2,(場合によっては3以降も)で確保。従来通りFactは絞る(B3)。また数値・細かい情報があると読者読みづらく、かつ、Reviseでも消えないので、そこはWriteするときに規制。それ以外は、上記貴殿ideaベースでWriterのタイミングで嘘をかかないように固める。」
- 「Reviseというのは、現在のEntertainment Revisionのことです。」
- 数値規則「CでOK。それ以外も貴殿提案ベースでよい」((c)=必要数値はB3が指定、Writerは転記のみ)。
- 設計・harness・Opusレビューを並行、生成は進行中Trial完了後(承認済み)。本Trialは決定A(Writer単一パス自由生成・prompt不変)の例外Trial(ユーザー指示)。

## KPI provenance
本委任ではKPI測定なし。委任_02: 生成NG率=fresh(Trial harness)、brief=reuse(B3 V0 b1-b4注記版)、比較セル=進行中Trialのfresh値をreuse。E2E自己確認: No。

## 成果物
設計書 DESIGN_01.md(§0-§10)、briefs注記12本+ANNOTATION_LOG.md+core_numbers.json、harness+単体テスト、PREREGISTRATION.md、RESULT_PACKET_FACTLOCK.md(SSOT追記文案を含む)。DECISION_LOG追記文案: 「## FACTLOCK-WRITER-REDESIGN-TRIAL-01: ユーザー判断(2026-10-08、委任_01)」。

## Git
本委任ではgit操作禁止。commit候補は委任_02でFableが指示。

## 報告
docs/pm/RESULT_PACKET_FACTLOCK.md(新規)。項目1作成物/2設計要点+Opus論点/3brief注記結果/4harness注入方式+テスト/5衝突なし確認/6委任_02条件・費用・時間/7問題・残作業/8check結果1行+一覧外Read理由。推奨は書かず事実のみ。

## 事前指定Read一覧
er019_family_x_ja_writer_o_r1_r2_01.py(R0 prompt/AN3/R1R2指示/previous_response_id/Fact Check)、er003_v1_en_direct_vfl_01_generate.py L495-560、er052_open233_polysemy_nb_dev_01.py(brief読込・phase2入口)、b3 V0 selected_brief.md、docs/pm/b3_trial_01/eval_rubric.md、night_loop_morning_report L16-21、checker_action_policy_01/design_01.md L1-30。

## 事前指定Grep一覧+追記位置・更新位置の手順
Grep WRITER_MODEL|vfl01.MODEL / def .*prompt|PROMPT|instruction(in er019 writer)。数値抽出regexは設計書に定義。SSOT追記なし(RESULT_PACKET_FACTLOCKへ文案のみ)。

## 実行コマンド全文
1. .venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_01.md --json-out docs\pm\delegation_log\2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_01.md_check.json
2. 設計書 er052_output/factlock_writer_trial_01/DESIGN_01.md 作成
3. brief注記 briefs/<slug>/b<i>/selected_brief_factlock.md 12本
4. harness er052_factlock_writer_trial_01_run.py + er052_factlock_writer_trial_01_test_01.py(.venv\Scripts\python.exe -m pytest er052_factlock_writer_trial_01_test_01.py -q)
5. PREREGISTRATION.md

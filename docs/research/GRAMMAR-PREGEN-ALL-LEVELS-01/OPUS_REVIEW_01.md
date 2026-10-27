# OPUS_REVIEW_01 DESIGN_01 Opus条件Aレビューの採否表(GRAMMAR-PREGEN-ALL-LEVELS-01 委任_02)

原文(逐語)= `docs/pm/delegation_log/2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_OPUS_RESULT_01.md`。Fable判定=委任_02の委任文「Fable判定」節(必須修正1〜7全件採用+追加判断)。
台帳(`docs/pm/OPUS_FINDINGS_LEDGER.md`)の ID は `OF-GPG-*`。反映先は `DESIGN_02.md`(対応表 §0)。Status は 2026-10-27 委任_02 時点。

| ID | Opus論点 | 区分 | 指摘要旨 | Fable採否 | 反映(DESIGN_02/実装) | Status |
|---|---|---|---|---|---|---|
| OF-GPG-M-1 | O-1 | 必須修正1 | v2結果のref_ja照合を置換(署名照合にpoolを使わず、凍結の有無に関係なく同じISSUE rc=4)+ISSUEの解消手段を定義 | 採用(解消手段=別候補/省略+ユーザー了承) | `translation_issues`/`_check_translation`/`op_accept_translation_diff` | IMPLEMENTED(核。CLI配線は委任_04) |
| OF-GPG-M-2 | O-3 | 必須修正2 | `legacy_postselect`をreview v1かつresult v1に限定。v2成果物ありで事前生成物なし=INTEGRITY。v1進行中runの事前生成は選定済みidのみ | 採用 | `_is_legacy_postselect`/`_check_integrity`/`pregen_stage(confirmed)` | IMPLEMENTED(核) |
| OF-GPG-M-3 | O-4 | 必須修正3 | フォーム文法0件は同一ロック内でomit。ロック順(KP->文法)・書込み順(文法review->sidecar->KPレコード)・冪等・id別sha | 採用 | `apply_form_selection`/`decision.explanation_sha_by_id`。KCPの呼出順は委任_04 | IMPLEMENTED(文法側。KCP側呼出は委任_04) |
| OF-GPG-M-4 | O-6 | 必須修正4 | levelを必須引数にし`b1b`既定値・`discover_dirs()[0]`・`LEVEL_KEY`を撤去。candidates docの`level`欄で一致確認 | 採用 | 全API `level`必須、`discover_dirs(run, level)`、Grep test | IMPLEMENTED(核。er128の`discover_dirs(run)[0]`は委任_04) |
| OF-GPG-M-5 | O-6 | 必須修正5 | 節単位の4者一致検査(取り違えブロックも検出) | 採用 | `verify_outputs(level, html_text=節)`/`count_grammar_blocks` | IMPLEMENTED(関数。builderへの配線は委任_03) |
| OF-GPG-M-6 | O-8 | 必須修正6 | EVIDENCE_PLANの元run・費用再設定。6セルで非0件経路、2件採用を1経路で実証 | 採用(evidence費用上限¥150) | 後続(委任_02Sの実現性確認->委任_05) | 採用(後続委任で反映) |
| OF-GPG-M-7 | O-9 | 必須修正7 | exporterと`grammar-show`のfail-closed(事前生成不完全/failed/explanations不整合でデータを出さない) | 採用 | `require_explanations`/`form_grammar_bundle`/`render_request_md` | IMPLEMENTED(核。exporter接続は委任_04) |
| OF-GPG-R-1 | O-1軽 | 任意 | 速度: 直列実装、evidenceで所要時間を測り2分超なら並行化 | 採用 | 直列実装 | IMPLEMENTED(計測はevidence) |
| OF-GPG-R-2 | O-2/O-10 | 任意 | Std候補率計測を前倒し(Prompt無変更の方針の裏付け) | 採用 | 委任_02S | 別委任で実施 |
| OF-GPG-R-3 | O-5 | 任意 | 公開済みX scriptは書換えず、今後は`public_study_html(level=)`必須。Y/Z新unitは葉。`_assert_study_ready`はpages/page_verifyのみ | 採用 | `public_study_html(level=)`必須化 | IMPLEMENTED(核)。adapterは委任_03 |
| OF-GPG-R-4 | O-7 | 任意 | 2 ITEM/1 callによる将来の原価低減は今回実施しない(Trial要) | 採用(記録のみ) | 実装しない | 記録のみ |
| OF-GPG-R-5 | O-10 | 任意 | F-0スキーマ契約を先行固定して並行化 | 採用 | `SCHEMA_CONTRACT_01.md`(commit 26383d6c7) | IMPLEMENTED |
| OF-GPG-R-6 | O-4要確認 | 記録事項 | HR提示TOP2枠->全候補(最大8)の解釈をDECISION_LOGに記録 | 採用 | RESULT_PACKET_GPG2のSSOT文案 | SSOT文案提出(編集権はFable) |

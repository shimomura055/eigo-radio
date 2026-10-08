# OPEN-243-TRANSLATION-NG-ANALYSIS-01 委任_02 result (2026-10-08、S0オフライン監査)

Status: AUDITED(既存artifactのみ読取り・API支出 ¥0・Production/CURRENT_SPEC.md 無変更)
成果物(`er052_output/open243_translation_ng_analysis_01/`): `S0_AUDIT_01.md`(集計表・突合表・精査表・FLOOR_MODE・EV-28)、`S0_USER_CHECK.md`(ユーザー確認3件)、`s0_excluded_candidates.jsonl`(除外1,011行)。再現script・中間json(`_s0_*.py`/`_s0_*.json`)も同ディレクトリ。
check_delegation_prompt: 委任文を `..._02.md` に保存し実行 → **FAIL**(必須セクション不足: 事前指定Read一覧/事前指定Grep一覧+追記位置/実行コマンド全文、固定ブロックE-1/D-1/G-1/F-1。委任文が標準フォーマットでないため)。FAILのまま続行。結果: `..._02_check.json`。
所要時間: 約15分(20:45 委任文保存〜21:00頃、commit前まで)。

## S0 (a)〜(e) 要点(出典は S0_AUDIT_01.md)
- (a) 承認構成(switch dump で `STAGE1_RECLASSIFY=true`・`FLOOR_MODE=number_only` を133/133で確認)の Checker 実行133件(254ファイルから `after_instances` 複製を除き重複除去)。初回 Stage 1 の再分類対象 1,389 claim 中、**1,011 claim が excluded=true**(SUPPORTED 372/NO_FACT_CLAIM 639)。フラグ別(重複計上): unsupported_new_claim 886、changed_fact 339、changed_scope 272、changed_causality 160、changed_certainty 105、changed_comparison 76、changed_time 30、changed_negation 28、changed_number 4、**changed_actor 38**(actor_match=match 27、最終EN本文に文が残存 19)。Trial A/B 57実行では対象499中379除外、changed_actor 8。再検査・出口の再分類は件数のみ(出口263/再検査36、claim単位の内訳なし=未確認)。
- (b) 翻訳段由来/増幅26事象のうち初回再分類で除外された文と一致したのは **5事象**(EV-25重大・EV-06・EV-07・EV-10・EV-19)。「候補化なし10/24」のうち3事象(EV-06/07/10)は再分類除外、7事象(EV-32/35/38/02/45/48/01)は Stage 1 候補に出ていない。「ACCEPTABLE残存8」のうち再分類で落ちたのは EV-19 のみ。**M3(E0: changed_actor保護)で救済され得る上限は2事象(EV-25重大・EV-06軽微)**。「unsupported_new_claim以外のフラグ付きを保護」なら上限5事象。いずれも「Stage 2に渡る」上限で、BLOCKING化の保証ではない。補正: EV-25の Stage 2 QUALITY評価は HC-010 に対するもの(HC-011/changed_actor は未評価)で、ANALYSIS_01の「別事実の理由で候補化」の経路記述は S0 §2-4 で補正。
- (c) 要約MAJOR14世代の一次分類(手動、attempt1基準): **明確な誤り5(G01/G04/G05/G11/G14)・境界例7(G02/G03/G06/G08/G10/G12/G13)・過剰判定の疑い2(G07/G09)**。STOP 8世代の最終MAJOR基準: 明確1(G03)・境界4(G06/G08/G09/G14)・過剰疑い3(G02/G07/G12)。指摘は「AI phone feature/calling feature(ロールバック対象範囲)」系と「users(開示相手)」系の2系統。
- ユーザー確認3件(`S0_USER_CHECK.md`): 確認1=「users」(開示相手)を書くことはMAJORか(G02最終、同型G07/G09/G12)、確認2=「so」で因果をつなぐことはMAJORか(G09最終)、確認3=Brent先物を「oil prices」と一般化することはMAJORか(G06最終)。
- (d) FLOOR_MODE: Trial A/B の Checker 57実行(all6 38 + factlock/runs 19)で switch dump が `FLOOR_MODE=number_only`・`STAGE1_RECLASSIFY=true`・`PRECHECK_MODE=number_only`、dump の sha256 が `provenance.switch_dump_sha256` と一致、`switches_equal_e2e02=true`。ANALYSIS_01 の「直接確認していない」は解消(承認構成との全キー突合は未実施)。
- (e) EV-28: EN deviation check は要約を指摘せず(LEDGER_COMPLIANT)→ Checker Stage 1 が L1 を r3+r5 で候補化(changed_actor含む)→ 再分類は CANDIDATE 維持 → Stage 2 一次 ACCEPTABLE を第2意見が BLOCKING(`s1_second_opinion_blocking`)→ 書換え("people being called were not given proper disclosure")→ cycle2/3 ACCEPTABLE、`RESOLVED_REWRITE_THEN_DOWNGRADE`。ANALYSIS_01 の記述と一致。

## SSOT記録(同梱)
OPUS_FINDINGS_LEDGER(OF-088〜094)、OPEN_ITEMS OPEN-243(行長2,361字、3,000字以内のためHISTORY移動なし)、DECISION_LOG同日節(i)〜(v)、PM_BRIEF「PM運用メモ」1行、REPORT §106〜108 訂正注記+§109新設、REPORT_LEDGER 2行。
- astra正式単価 Standard 10/1/12.5/50、Batch・Flex 5/0.5/6.25/25(出典 https://platform.openai.com/docs/pricing、2026-10-08 16:38 JST)。過去の「Sol×2.5推定」(=5/0.5/6.25/25、Batch/Flex相当)は誤り。Sonnetの機械再計算(REPORT記載値、USD/JPY=160): Step 1 ¥22.27→約¥35.98、MATRIX-01 ¥48.48→約¥94.25、MATRIX-02 ¥64.92→約¥125.13、3試験合計 ¥135.67→約¥255.36。委任文記載値(¥134→¥254、MATRIX-02 ¥124)との差は¥1〜1.7で、**委任文値の算出根拠は未確認**。予算超過: META上限¥60に対し約¥94、ホルムズ+ミニバッグ上限¥80に対し約¥124〜125。

## 未確認事項
- 再検査・出口の再分類のclaim単位内訳。133実行は記事の重複を含む(独立標本数ではない)。EV-25/EV-19がStage 2に載った経路(兄弟location展開)はコード未確認。要約分類は手動判定(1名)。Opusレビュー原文ファイルは存在せず、所見は委任文経由で記録(OF-088〜094のEvidence欄に注記)。Step 1の予算上限は未確認。承認構成との全キー突合は未実施。
- 作業ツリーにある他の未コミット差分(er006/er011/er012/er021/er030/er052 budget_state 等)は本タスクと無関係のため触れていない。

## 変更ファイル
新規: `er052_output/open243_translation_ng_analysis_01/`(既存ANALYSIS等+S0_AUDIT_01.md、S0_USER_CHECK.md、s0_excluded_candidates.jsonl、_s0_*)、`er052_output/factlock_writer_trial_01/astra_pricing_01/`、delegation_log(本委任・委任_17・_18・OPEN-243委任_01の委任文/check/result)。
更新: `docs/pm/OPUS_FINDINGS_LEDGER.md`、`OPEN_ITEMS.md`、`DECISION_LOG.md`、`docs/pm/PM_BRIEF.md`、`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`、`docs/pm/REPORT_LEDGER.md`。

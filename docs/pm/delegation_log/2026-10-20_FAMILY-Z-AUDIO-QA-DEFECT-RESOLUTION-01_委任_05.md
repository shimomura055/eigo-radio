# 委任文(Fable→sonnet-worker) 委任_05 (保存注: 委任文本文のうちユーザー原文部分は別ファイルに逐語保存。下記は本文の保存版で、固定ブロックは原文どおり)

## 管理ID
FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_05(①Melos/Mellows: ユーザー2026-10-20新指示の原文保存[T-0]+「なぜ既存の承認済み音韻同等性判定で救済されなかったか」のA/B/C具体解明+11-8不具合判定テスト+範囲内不具合があれば修正・Regression・正式経路検証)。2026-10-20。
並行: 委任_06(②③配線保証の証拠整理+再生成計画、JPY0)。本委任は ITEMS23_WIRING_ASSURANCE_01.md・REGEN_PLAN_01.md・RESULT_PACKET_FZAQ6.md・er020_tts_retry_local_rewrite_01.py・er003_v1_n3_01_tts_generate.py・er003_v1_crosslevel_audio_02_common.py・er026_output/ を編集しない。SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/REPORT_LEDGER/USER_DECISION_REGISTER_01/OPUS_FINDINGS_LEDGER)の編集権無し。ACTIVE_TASK.mdは先頭に自委任ヘッダ追記のみ。

## 性質/到達上限Status/禁止事項
- 性質: 調査+範囲内不具合があれば修正・Regression・正式経路offline検証。
- 到達上限Status: ITEM1_ROOT_CAUSE_EXPLAINED_PENDING_FABLE / ITEM1_DEFECT_FIXED_TESTED_PENDING_FABLE / 判断候補あり。
- 禁止: (1)A案・A'案(P1=M1 _post_check受理拡張、Ledger限定版含む)およびP2(G-1/G-2)はREJECTED。別名実装禁止 (2)Melos/Mellows専用個別例外禁止 (3)承認済み許容判定を独断で厳格化しない (4)新規TTS生成禁止 (5)HR Lock・review_lock_state.json(sha256 6720ce80b7eedba9789dc190a431b030e20486b298a451479129e4d017fb3e19)変更禁止 (6)git add -A/-u/-f・amend・rebase・force push・stash・clean・reset --hard・checkout -f禁止 (7)有料run再起動禁止。
- 修正範囲の線引き(11-8): 範囲外=受理面・閾値・方式の新設/拡大。範囲内=承認済み仕様文・設計原則との矛盾の是正。共通ASR判定cascade(er006_secondary_asr_01/er006_m1_multi_candidate_01/er006_preprod_hardening_01_validation/er011_*validator*/er021_*/er078_*)の判定意味を変える場合は実装前に設計を文書化しRESULT_PACKETで報告。
- 費用: 見積JPY0〜10(新規TTS0・LLM0)。T-3上限JPY10 Guardrail。
- 前委任(_01/_03)結論: 不具合0件・P1/P2は仕様変更候補。ユーザーはA/A'をREJECTEDし具体説明を要求。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は--porcelain/--stat/--short等で最小化する。
F-1: 自タスクのtranscript退避は不要。
T-0: 受領した委任文を docs/pm/delegation_log/<管理ID>.md へ保存し check_delegation_prompt.py を実行、結果をRESULT_PACKETへ1行記録。
T-2: TTSを伴う委任はTTS_EXECUTION_MODE=STANDARD明示(本委任はTTSを伴わない)。
T-3: 費用上限はGuardrailでありCap到達=自動STOPではない。

## ユーザー指示(原文)
別ファイル docs/pm/delegation_log/2026-10-20_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_ROOT-CAUSE-WIRING-CLOSEOUT_USER.md に逐語保存。

## 本委任の作業(①のみ)
成果物 docs/research/FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/ITEM1_ROOT_CAUSE_02_SPEC_RECONCILIATION_01.md: §1承認済み音韻同等性仕様文の逐語一覧 / §2 A/B/C具体解明(C: c-1〜c-5) / §3 11-8不具合判定テスト表(R1〜R12) / §4是正 / §5ユーザー判断候補 / §6結論段落。報告=docs/pm/RESULT_PACKET_FZAQ5.md(項目(1)〜(12))。
Git: commit1=原文保存、commit2=本成果物。trailer: Delegation: FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/委任_05。

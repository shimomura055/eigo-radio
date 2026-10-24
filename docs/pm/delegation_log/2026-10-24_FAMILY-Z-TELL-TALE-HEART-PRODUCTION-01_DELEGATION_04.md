管理ID: FAMILY-Z-TELL-TALE-HEART-PRODUCTION-01 委任_04 — Std KP#2『vulture's』の是正と、Z runnerの`CANONICALIZATION_REVIEW_REQUIRED`自動受理の調査。上限=作品累計70円(既使用36.64円)。

(注: 抽出ツールのindexをsubagentから特定できなかったため、委任文を受領した本文から手で保存。要旨のみ。)
- Std KP#2『vulture's』(canonicalization QA 4項目FAIL・REVIEW_REQUIRED受理)は承認済み品質未満。試聴提出前に是正。
- 手順: (1)案B myself→oneself を `_PERSON_DEPENDENT_TO_GENERIC` に追加(影響分析gate: 既存test全PASS・X/Z保存KP replay変化0・他-self形確認、OPEN_KP_MYSELF_IMPACT_01.mdに記録、単独commit)。(2)`--stages kp --regenerate-stage kp_a2` 最大2回(間隔150秒以上)、CANONICALIZATION_PASSのみ採用、REVIEW_REQUIREDでQA FAIL含むなら不採用。(3)PASS後Std KP clipのみTTS→`provision_shell,gate,assemble,pages,page_verify`を1起動→公開差替え→page_verify PASS。
- 調査(API 0): er026 runner:1712-1713のREVIEW_REQUIRED受理の出自(委任_10コメント、DECISION_LOG/OPEN_ITEMS grep、er003_key_words_canonicalization.py:630-650との関係、X経路の扱い)。承認記録の有無を明記、無ければ新規OPEN(分類「修正へ進む」)登録、修正はしない。保存先 docs/research/FAMILY-Z-TELL-TALE-HEART-PRODUCTION-01/KP_REVIEW_REQUIRED_INVESTIGATION_01.md。
- 日本語タイトル読み(ASR一次「菅口新造」→二次OK)は試聴確認項目として報告。
- 制約: stop_scope_check rc=0、cost logger、日次1,000円内、TTS直列化flag、RESTART_STORM回避、--clear-stop禁止、.venv python。完成後RUNTIME_EVIDENCE_01/SOURCE_FIDELITY_CHECK_01更新、OPEN-503・DECISION_LOG・ACTIVE_TASK更新。Git: 自分の変更のみ、案Bは単独commit、push origin HEAD:main。報告 docs/pm/RESULT_PACKET_FZTTH4.md。到達目標「正式完成候補・ユーザー最終試聴待ち」、PASS先取り禁止。

# ASR-M1-OOV-MULTI-PRONUNCIATION-PRODUCTION-01 委任_02 (要点保存、T-0)

## 管理ID
ASR-M1-OOV-MULTI-PRONUNCIATION-PRODUCTION-01 委任_02(Fableからの継続指示1回目。Opus条件Aレビュー[OF-178〜187]を反映し、新規Production module+unit test+配線パッチ案+evidence用隔離runnerまで実装。既存Production fileへの配線編集は行わない=Coffee記事の有料Production run中のため。配線は委任_03)。

## 性質/到達上限Status/禁止事項
- 性質: Production実装(新規module)+test。到達上限Status: MODULE_IMPLEMENTED_PENDING_WIRING。費用: JPY0(有料API禁止)。
- 禁止: 既存Production file編集、C3、Trial oov_spelling_fallback、Gate緩和、allow-list、Melos固有hardcode、git add -A、amend/rebase/force push、Coffee run dirへのアクセス、ACTIVE_TASK/RESULT_PACKET commit、共有ファイル追記test。
- STOP条件: 承認範囲超の発音許容基準が必要/Gate緩和が必要/誤PASS抑制不能/既存正式仕様との重大矛盾。

## 固定ブロック
E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3: T-2 TTSなし、T-3 JPY0。

## ユーザー指示(原文)
委任_01保存分docs/pm/delegation_log/2026-10-13_ASR-M1-OOV-MULTI-PRONUNCIATION-PRODUCTION-01_01.mdの「ユーザー指示(原文)」節を参照。

## Opus反映
OF-178 F1 explained必須 / OF-179 凍結候補注入 / OF-180 ASR非依存契約test / OF-181 C2除外条件 / OF-183 矛盾拒否 / OF-186 evidence隔離runner / OF-187 ledger_key別audit。

## 実行コマンド
pytest er006_m1_multi_candidate_01_test_01.py / pytest er077_m1_oov_multi_pronunciation_01_test_01.py / er077 eval --use-module --out eval_02 / tools/secret_scan_01.py --staged

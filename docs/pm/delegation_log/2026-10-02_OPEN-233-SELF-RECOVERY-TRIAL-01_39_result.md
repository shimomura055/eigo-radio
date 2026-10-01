# 委任_39 結果(OPEN-233-SELF-RECOVERY-TRIAL-01、設計案作成のみ)

- 管理ID/委任番号: OPEN-233-SELF-RECOVERY-TRIAL-01 / 委任_39。Status: USER_DECISION_REQUIRED のまま。費用¥0。実装・Trial・API課金・Production変更・git add/commit/pushなし。
- T-0: check_delegation_prompt.py = PASS(warningはTTS関連の定型で本委任は非該当)。
- 成果物: `docs/pm/design_open233_violation_span_handoff_01.md`(設計書)。Opus独立レビュー待ち(Fableが起動)。
- 推奨: 案1「原文逐語+複数範囲(`violation_spans`配列)をそのまま渡す」。文ID・文字オフセットは現時点で不要(次段条件は設計書§6)。
- なくす処理: hint引用を第一手にする対象決定、`locate_multi_quote_span`の包含スパン、類似度/単語重なりの1文選び、JA位置比近似(主経路から)、類似度による再出現確認。
- 残す処理: 実在確認(完全一致+N1〜N5の機械的正規化、1箇所一致)、`.replace`での書き戻し、区分判定(包含)、文脈取得、before/after記録、全文Recheck。
- 実例: rep21 s1(連続2文)=1 span、rep20 s2(離れた2文)=2 span。設計が保証するのは「2文とも対象になり書き戻される」まで。Rewrite役の出来・JA対応の正しさ・Recheckの新規指摘(MUSE-HC-010)は保証外。
- 逐語の限界: Promptのみでは100%保証不可(`same_fact_id_locations`の前例)。不一致はfail-closed(人間確認)を初期仕様、Checker返し直し(概算¥0.5)は測定後。
- 既存記録の再集計(¥0、既存JSON読み取り、付録A): 検査役claim 389行(ユニーク134)のうち、Prompt変更なしで逐語範囲に復元可 82.8%、大小文字・空白の正規化まで91.5%、不一致8.5%。
- Existing Spec Check: Stage 2逐語引用/`same_fact_id_locations`/cite-or-release=A、`violation_spans`・文ID・オフセット=C(新規)、多箇所一括Rewrite=B寄り(Phase 2課題)。
- 他ファイル変更なし。新規は設計書・委任文保存・`_check.json`・本結果の4ファイル(委任文指定の3種+check.json)。`git status --porcelain=v1`で自分起因は上記のみ(他の約450件は既存差分・並行タスク由来)。

# 委任_01A KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01 (2026-10-15、要点保存。ユーザー指示は逐語要旨)

性質: 調査・設計・Trial計画(コード変更なし、有料API呼出なし、費用JPY0)。到達上限Status: DESIGN_DRAFT。Opus条件Aレビュー待ち。並行: 委任_01B(レビュー不全調査、別agent。er071_output/.../review_audit/ と RESULT_PACKET_KGDC_B.md を書く。01Aは触れない)。
禁止: 有料API、er003_key_words_gloss_alignment.py / er003_v1_n3_01_scaffold_generate.py / Prompt / Gate / Validator / config既定値の編集、Coffee完成物再生成、SSOT編集、git add -A/-f/amend/rebase/force push/stash/clean/reset --hard/checkout -f、STOPセンチネル編集、.env使用。
固定ブロック: E-1/D-1/G-1/F-1/T-0/T-1/T-2(TTSなし)/T-3(費用JPY0)。

## ユーザー指示(2026-10-15)
- 欠陥1: 英語KPに特定スロット語がなければ日本語glossの「〜」をFAILとする機構は、意味的整合を表面的文字条件へ置換したもの。承認済みgloss規則(辞書的に自然なら「〜」可)を維持し「〜」の有無を合否条件にしない。based on→「〜をもとにした」許容/based on interviews→「〜をもとにした」はinterviewsの意味欠落でNG/「インタビューをもとにした」は整合。
- 欠陥2: 再整合2回失敗時に最終KP+古いglossを残しFAILED通知のみで正常工程へ進み得る設計は認めない。2回失敗時はHuman Reviewへ例外報告(英語KP・現在gloss・失敗理由・試行結果・再生成候補)し対象の後続TTS・正常完成を停止。最終英語KPを安易に短い候補へ戻さない。
- 工程順: 1 KP候補選定・初期gloss生成 → 2 英語KP最終確定 → 3 再整合 → 4 必要な品質判定 → 5 TTS。
- 事前調査(§3)、設計(§4)、Trial(§5: まずオフライン、次に有料Trial)。既存機構優先、新Validator/Hook/管理機構を理解なく増設しない。Q>D>C、量産70円/記事セット、予算日次1,000円。
- 安全: 現行未承認再整合工程は既定flag ON。量産経路の誤発火に対する運用上の隔離を確認。
成果物: er071_output/m2p0_n01_production_wiring_01/gloss_alignment_correction_01/{INVESTIGATION_01.md,DESIGN_DRAFT_01.md,OFFLINE_AUDIT_01.md/.json,TRIAL_PLAN_01.md}、er071_gloss_alignment_correction_01_offline_audit.py、docs/pm/RESULT_PACKET_KGDC_A.md、docs/pm/ACTIVE_TASK_KGDC.md。
commit msg: KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01 委任_01A: 事前調査(経路/FAILED扱い/隔離)+オフライン監査+修正案設計草案DESIGN_DRAFT_01+Trial計画(JPY0、コード/Production/SSOT無変更) / trailer Managed-ID。

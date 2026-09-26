# NEWS-FAMILY-X-B3-FACT-SELECTION-PRODUCTION-WIRING-01(Fable差し戻し1回目)
# Fable Editorial Findings(記録のみ、修正・再生成はしない)

本ファイルは、Fable指摘3(Fact時制のドリフト)・4(Storyline観察)に対応する
事実記録である。**判断・修正案の実装は行わない**(ユーザー判断待ち)。

## 指摘3: Fact時制のドリフト(MUSE-HC-012、既完了 vs 未来形表現)

### (a) 該当文の逐語

- JA R2(`ja_writer/revision2.md`): 「Metaの幹部は、適切な開示なしにこのテストを始めたことを「ミス」と認めました。そして、人間のコンシェルジュ機能は当面ロールバックされます。」
- Advanced(`b1b/article.md`): 「The human concierge feature will be rolled back for now.」
- Standard(`a2/article.md`): 「The human concierge feature will be rolled back for now.」(Standardも同一文言、確認済み)

### (b) Ledger該当行の逐語

- `research_ledger/verified_fact_ledger.txt`: 「[VERIFIED] MUSE-HC-012: MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。」
- Ledgerは「ロールバックした」(完了・過去形)。JA R2は「ロールバックされます」
  (未来形・受身)。Advanced/Standardは"will be rolled back for now"(未来形)。

### (c) Advanced deviation check 1回目(MAJOR)の指摘文

**制約(重要)**: 1回目(MAJOR)の生JSON応答は、既存Production実装
(`er012_e_family_entertainment_two_level_runner_01.run_writer_stage()`)の
仕様上、retryが成功した場合はディスクへ保存されない
(`b1b/audit/deviation_check.json`は最終[retry後]の判定のみを保存する設計であり、
却下された1回目の判定内容はメモリ上で読み捨てられ、どのファイルにも残らない)。
よって1回目の指摘文の完全な逐語は、既存の保存済みartifactからは復元不可能
(raw_usage_log.jsonlはtoken数のみでresponse本文を含まない)。

参考として、本タスクの委任文(`docs/pm/ACTIVE_TASK_FXB3.md`、Fableからの
要約引用)には次のparaphraseが記載されている(これはFableによる要約であり、
LLM応答の逐語ではない、出典明記):

> 「(b)既に実施済みのロールバックを将来形で表現」
> (`docs/pm/ACTIVE_TASK_FXB3.md`「Fable指摘(Gate 3照合結果)」項番3より引用)

### (d) retry後の判定(現在ディスク上の最終保存内容、逐語)

- `b1b/audit/deviation_check.json`: `{"deviations": [], "overall_status": "LEDGER_COMPLIANT"}`
- retry後は`deviations`が空配列であり、時制の不一致を含め一切の指摘が
  記録されていない(1回目でMAJORとされた事象と同一の英文が、2回目では
  無指摘でLEDGER_COMPLIANTと判定された)。

### 観察(記録のみ、判断・修正はしない)

- Ledger Deviation Check(LLM判定)は同種の時制不一致に対し、実行のたびに
  判定が変動した(既知の非決定性)。
- 1回目の却下判定の完全な内容が保存されない現行ログ設計により、
  「なぜ2回目は指摘しなかったか」を事後的に完全再現することはできない
  (これは本タスクのGate 3 #13修正[stage別merge保存]とは別種の制約であり、
  deviation check自体の各attemptを両方とも保存する設計変更が必要になるが、
  それ自体の要否はユーザー判断)。

## 指摘4: Storyline観察(Trial-02 Core Storylineとの差異)

### (a) Trial-02 Core Storylineとの差

- Trial-02 `CORE_STORYLINE`(`er015_family_x_writer_fact_selection_trial_02.py`
  L91-94): 「Museが電話代行する→AIだと気付かれると切られることがある→人間スタッフへ引き渡す→人間介在によるprivacy/disclosure問題→Metaが機能を一旦戻す。」
- run_01 `selected_storyline`(AIが決定、`storyline_b3/fact_selection_evidence.json`):
  「MetaはAIエージェント「Muse」の電話機能で一部の通話を訓練済みの人間契約スタッフに担わせる実験を行ったが、ユーザー情報がスタッフに共有され得る懸念や適切な開示の不足を受けてミスと認め、機能を当面ロールバックした。」
- 差分: Trial-02のCore Storylineは「AIだと気付かれると切られることがある→
  人間スタッフへ引き渡す」という**人間を使った理由(なぜ人間なのか)**を
  明示的な因果連鎖として含む。run_01のAI決定Storylineは「一部の通話を
  訓練済みの人間契約スタッフに担わせる実験を行った」という**事実の記述**に
  留まり、「なぜAIではなく人間を使ったか(切られることへの対処)」という
  動機・因果には触れていない。
- この差の結果、記事(JA R2/Advanced/Standard)は「人間スタッフが電話を
  引き継いだ」という事実とその後のprivacy懸念・ロールバックは説明しているが、
  「なぜAIから人間へ引き継ぐ設計にしたのか」という理由そのものには触れていない。

### (b) fact_selection_evidence.json内のMUSE-HC-009(4テスト理由文)の逐語

MUSE-HC-009は「AIだと気づかれ電話を切られる」個別報告。run_01のAIは
以下の理由でこれを除外と判定した:

- test1_answer: YES / test2_answer: NO / test3_answer: NO / test4_answer: YES / decision: excluded
- reason(逐語): 「AIだと認識されて電話を切られた個別報告は別の実験上の問題だが、今回の中心的なロールバック理由である開示不足や情報共有懸念には直接つながらない。」

### 観察(記録のみ、判断・修正はしない)

- run_01のAIはMUSE-HC-009を「今回の中心的なロールバック理由(開示不足・
  情報共有懸念)に直接つながらない」としてTest2=NOで除外した。これは
  Storyline選定基準(4テスト)としては手順通りの適用だが、結果として
  「なぜAIから人間への引き継ぎという設計にしたのか」というTrial-02が
  含めていた動機面の因果連鎖が、run_01のAI決定Storylineには反映されて
  いない。これがStoryline選定手順そのものの欠陥か、単に今回のFull Ledgerの
  記述粒度・Fact構成の結果かは、本記録だけからは判断できない。


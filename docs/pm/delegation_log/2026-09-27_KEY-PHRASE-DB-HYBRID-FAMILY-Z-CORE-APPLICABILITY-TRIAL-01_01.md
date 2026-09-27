# 委任ログ: KEY-PHRASE-DB-HYBRID-FAMILY-Z-CORE-APPLICABILITY-TRIAL-01(初回)

日付: 2026-09-27
委任先: Sonnet(sandwich実行層)

## 委任文(逐語、Fableからの委任メッセージ全文)

管理ID: KEY-PHRASE-DB-HYBRID-FAMILY-Z-CORE-APPLICABILITY-TRIAL-01(新規Trial、ユーザー承認 2026-09-27)。一時ファイル `docs/pm/ACTIVE_TASK_KPZ1.md` / `docs/pm/RESULT_PACKET_KPZ1.md`(commitしない)。委任文全文を `docs/pm/delegation_log/2026-09-27_KEY-PHRASE-DB-HYBRID-FAMILY-Z-CORE-APPLICABILITY-TRIAL-01_01.md` に保存しcommitに含める。Guardrail **¥30**(STOP閾値 ¥25)。APIキーは環境変数のみ。**Production配線禁止。到達可能Status: REJECTED / VALIDATED / USER_DECISION_REQUIRED(仮分類、確定はFable)。Trial成功でもAPPROVED_FOR_PRODUCTIONにしない。**

### ユーザー指示(逐語要旨)

目的: Family Xで採用する共通DB Hybrid Core(Trial-04 baseline=er029 commit 57b61273)が、Fiction/Story系のFamily Zでも有効か確認する。
評価対象: dialogue-heavy本文 / 引用会話 / 固有名詞 / 作品固有語 / rare word / narrative understandingに効く表現 / phrasal verb・idiom / 一般語ばかりに偏らないか / 「物語理解に重要なKey Phrase」を拾えるか。
特に確認: (1) Core自体は共通利用できるか (2) Family Zで必要なのはCore変更ではなく最終選定Prompt/weight/category priorityの差分だけで済むか (3) X側のProduction仕様を壊さず「共通Core + Family別最終選定ルール」構成が成立するか。
重要: Zの結果でFamily X wiringを止めない。問題が出たら Core共通部の問題か Z固有selection ruleの問題か を切り分けて報告。**新DB追加や大きなCore仕様変更が必要なら勝手に実施せずSTOP。** Family Z固有Prompt変更が必要でもTrialとしてのみ実施。Production採用判断はユーザーへ返す。
Trial素材: 既存Family Z/Fiction実データ優先(Melos: `er026_output/family_z_production_e2e_01/melos/run_01/` の本文・既存KP artifact; user_test twins A2/B1 [dialogue-heavy、Trial-04で使用済み] も参考)。新規記事生成・新規LLM callは必要最小限(本文1件1 call)。
評価項目: structural PASS / important term保持 / narrative relevance / dialogue handling / proper noun handling / phrase・idiom quality / general-word偏重 / 公開・既存KPとの比較(参考扱い) / cost / shortlist quality / false positive / fallback必要性。

### 並行ルール(厳守)

- **er029(Core baseline)・er028/er027・er003_key_words_* は変更禁止**(read-only import)。別Agentがer029をProduction module `er030_*` へ昇格中 → er030も触らない。
- 本Trialの新規コードは `er031_key_phrase_db_hybrid_family_z_trial_01_{run,rules,test}.py` のみ。Z固有の最終選定ルール(prompt差分/weight/category priority)は er031 側に閉じる。
- 共有ストア非書込み、出力は `er031_output/key_phrase_db_hybrid_family_z_trial_01/`。SSOTは編集しない(記載案のみ)。

### 作業

1. Melos本文(A2/B1B等、存在するレベル)と、参考としてtwins A2/B1で、**er029 Coreをそのまま**(Z固有ルールなし)実行=条件Z0。
2. Z0の結果から不足(固有名詞/作品固有語/物語理解表現の落ち、一般語偏重、会話タグFP等)を分析し、**Coreを変えずに** er031側の最終選定ルール差分(prompt注記・weight・category priority)を設計=条件Z1。同本文で実行。
3. Z0/Z1 vs 既存KP artifact(er026のKP、参考扱い)を評価項目で比較表化。切り分け: 各問題を「Core共通部」/「Z固有selection rule」/「既知limitation(Trial-04留保①〜④)」に分類。Core変更が必要と判断した項目は**実施せず**STOP候補として列挙。
4. REPORT `KEY-PHRASE-DB-HYBRID-FAMILY-Z-CORE-APPLICABILITY-TRIAL-01_REPORT.md` 新設: 既存資産照合、素材、Z0/Z1設計、比較表、切り分け、(1)(2)(3)への回答、cost、STOP該当、Status仮分類、next user decision案、「Production未配線」明記。unit test(er031、Z固有ルールの決定論性)。

Git: er031_*・出力・REPORT・delegation_logのみpath指定add(`git add -A`禁止、他Agentのstageを外さない、index.lockリトライ)。トレーラー `Management-ID: KEY-PHRASE-DB-HYBRID-FAMILY-Z-CORE-APPLICABILITY-TRIAL-01`。push origin main。reset/amend/rebase/force push禁止。RESULT_PACKETに費用・commit hash・変更ファイル・(1)(2)(3)回答要約・STOP該当を記載。

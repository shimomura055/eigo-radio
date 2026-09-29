## 管理ID

LEDGER-DEVIATION-CHECK-REDESIGN-REVIEW-01(Part B=Product 設計・Fact Safety・Hormuz/重大/過剰品質事例への適用評価・Trial 設計・リスク抜け漏れ、委任 _02)。**read-only レビュー**。一時ファイル `docs/pm/ACTIVE_TASK_RRB.md` / `docs/pm/RESULT_PACKET_RRB.md`(commitしない)。並行: 別 Sonnet 1 件(Part A=Repo/実装整合・QCD・既存仕様競合、出力先 `docs/pm/review_ledger_deviation_redesign_01_part_a.md`)→ 同ファイルに触れない。本タスク出力先: `docs/pm/review_ledger_deviation_redesign_01_part_b.md`(新規)+delegation_log のみ。**Production code・Prompt・Ledger schema・Checker severity・SSOT 4 点・REPORT_LEDGERの変更禁止、Trial 実行禁止、Family X E2E 再開禁止、API 呼び出し禁止(¥0)、Opus 起動禁止**。削除・移動・`rm`・`git clean`・`git stash`・rebase/reset/amend/force push 禁止。未追跡ファイルは他タスク由来として触らない。push 競合時は `git merge origin/main` のみ。APIキー本文表示禁止。改善案の提示は可、**採用・実装はしない**。賛成ありきでなく批判的に。

## レビュー対象(ChatGPT 再設計素案、Status=PROPOSED/REVIEW)

目的: Checker の目的を「Ledger 逸脱の最大検出」から「英語学習教材としてユーザーの主要な Fact 理解を実質的に誤らせる重大事故を防ぐ」へ寄せる(嘘・根拠なし・信頼性軽視は許容しない。QCD バランスで量産可能に)。
- A. 「Deviation 検出」と「Production STOP」を分離: 検出 → 実害評価 → Severity 決定 → Action 決定。判断軸=「一般的な英語学習ユーザーがニュースの主要な事実関係を実質的に誤って理解する可能性があるか」。
- B. Severity 3 層: BLOCKING(数字改変/主体取り違え/対象取り違え/肯定否定反転/比較方向反転/時系列の重大変更/値動き方向の反転/根拠のない重要 Fact 追加/相関・同時発生を重大な因果として断定/元 Fact と逆の意味 → must-fix/STOP)、QUALITY(厳密には改善できるが主要 Fact 理解は変わらない → 通す+warning/log)、ACCEPTABLE(教材化・要約・自然化の合理的範囲 → 通過)。10 category は廃止せず、Category と Severity を分離。
- C. changed_causality を一律 BLOCKING にしない: Blocking causality(同時期 → 引き起こした、かつニュース理解の中心)と Non-blocking causal phrasing(観測事実の自然な文章化)を区別。Hormuz「料金案が消えたからといって、価格がそのまま大きく下がる展開にはなりませんでした」/"The disappearance of the fee plan did not lead to a large, lasting fall in prices." は自動 BLOCKING にしない候補(ChatGPT 見解: 元 Ledger に「上げ幅縮小後、高水準へ戻った」観測あり、`large, lasting` の限定あり、直後に留保あり → QUALITY または ACCEPTABLE 候補。**Claude 側で独立に評価すること**)。
- D. claim 単体でなく文脈: causality/certainty/unsupported_new_claim の境界事例は前後 1〜2 文の context window で最終 Severity。数字/actor/negation/comparison/time は単体判定のまま。
- E. notes_for_writer を soft guidance へ戻す: Ledger Fact(hard)と notes_for_writer(soft)を区別、notes_for_writer 違反だけでは BLOCKING にしない。将来 schema 分離 Trial を検討。
- F. JA 側=重大 Fact 事故を記事生成段階で除去/EN 側=翻訳・A2 simplification で意味が壊れていないか。EN で origin=ja_source でも一律即 STOP にせず Severity で Action。
- G. 最低 4 call(JA Original/JA R2/Advanced/Standard)を QCD で見直す(Trial 対象、確定せず)。
- H. LLM category 検出+deterministic post-processing で最終 Severity(例: actor changed+Ledger entity mismatch → BLOCKING/changed_causality+数値・entity・時間の矛盾なし+限定表現あり+直後 qualifier あり → QUALITY 候補)。
- I. Human Review は非常口(BLOCKING が must-fix retry 後も残る場合のみ)。QUALITY はログ蓄積。
- J. Disclaimer(AI 生成につき 100% 保証しない趣旨、文言未定)は残余リスク説明であり Checker 品質低下の理由にしない。
- 想定 Trial: 過去実例 fixture(重大/過剰品質/境界/見逃し)で Quality(重大 Fact 事故の BLOCKING 維持率・見逃し率・不要 BLOCK 率・QUALITY/ACCEPTABLE の妥当性)/Cost(call・retry・API 費用・HR 数)/Delivery(latency・STOP 率・完成記事率)+同一入力反復で判定一致率・非決定性。

## 前提資料(全文 Read 可)

`LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_REPORT.md`(調査 REPORT: 現行仕様、hard/soft、A 候補 5 件・B 候補 4 件、4 区分、QCD、最低ライン、Hormuz trace、§8 材料)。必要に応じ各事例の evidence json(REPORT の表に記載のパス)と Ledger を Read(短い json)。

## レビュー項目(出力ファイルの章立て)

### A. Product 設計
- 英語学習サービスとしてこの最低品質ラインは妥当か(調査 §6 の既存最低ラインとの差分を明示: 落ちるもの・残るもの)。
- 「主要 Fact 理解を誤らせるか」を STOP 基準にすることの弱点(「主要」の判定主体・基準の曖昧さ、記事ごとに何が主要かを誰が決めるか、LLM に判断させる場合の非決定性の増幅、学習者が英語で読むため日本語話者より誤読しやすい点、Key Phrase・Comment・In One Line へ逸脱が増幅伝播する経路)。
- 緩すぎる箇所/まだ過剰品質な箇所/Disclaimer との役割分担の妥当性。

### B. Fact Safety
- BLOCKING に残すべきものの抜け(例: 出典・帰属のすり替え(changed_actor の一種)、否定の範囲、数値の単位・母集団(numeric_scope)、日付の相対表現、固有名詞の綴り、"最初/唯一/最大" 等の極性語、引用発言の改変)。
- causality 緩和で重大誤情報を通すリスク(「ニュース理解の中心」か否かの判定を誰がどう行うか、Hormuz のように記事の主題が因果そのものである場合)。
- notes_for_writer soft 化の危険(調査で notes_for_writer に factual constraint が混在している可能性が指摘済み。実 Ledger(Hormuz HF-001〜012 の notes_for_writer)を読み、各 note が「factual constraint」「writer guidance」のどちらかを分類し、soft 化で失われる factual constraint の具体例を挙げる)。
- context window 採用で逆に見逃しが増えないか(留保文が形式的に付くだけで免罪符化するリスク、window 内に矛盾がある場合の扱い)。

### 事例適用評価(素案 B/C/D/E/H を機械的に当てはめ、期待どおり分離できるかを 1 件ずつ表で)
- STOP 維持候補: A-2「上げ幅縮小」→ "prices began to fall"/A-5 rollback → "put back the feature"/A-3 actor の勝手な具体化/A-4 企業・店舗 → users/A-1 時制 drift(Checker 見逃し。新設計でも検出できるか、検出は LLM 側の問題で Severity 設計では解決しない点)。
- 過剰品質候補: B-1 生活ブリッジ文/B-2 Hormuz causality(**Claude 独立評価**: BLOCKING/QUALITY/ACCEPTABLE のどれか、根拠=Ledger HF-009/HF-011 の観測との整合、"large, lasting" の限定、留保文、記事主題との関係。ChatGPT 見解に賛成ありきでなく判定)/B-3 接続詞 so/B-4 一般読者心理への一般化。
- 各件について「新設計のどのルール(B の列挙、C の区別、D の window、E の soft 化、H の deterministic rule)で分離されるか」「分離に失敗し得る条件」を書く。

### E. Trial 設計
- Fixture 構成の不足(重大 15 件では少ない。カテゴリ×origin×Family の被覆、negative example=「通すべきもの」、境界例、見逃し例、Standard(A2)由来の simplification 逸脱、日本語→英語固有の逸脱(主語省略・時制・可算/不可算)、合成 fixture(ER-009-N1 の 9 種)との併用)。
- 必要な positive/negative example の最小数、同一入力反復回数(非決定性測定に必要な n、例: 5〜10 回×fixture)、受入条件(BLOCKING 維持率 100% を要求すべき fixture 群、不要 BLOCK 率の目標、一致率の閾値)、false positive/false negative の測定方法(gold label を誰が付けるか=ユーザー/合議、ラベルの再現性)、Production 採用判断に必要な minimum sample(記事数・Family 数)。費用概算(Checker ¥0.90/回 × fixture 数 × 反復)。

### リスク / 抜け漏れ・改善提案
- 素案に無い論点(例: QUALITY の蓄積ログの置き場と誰がいつ見るか、QUALITY が Key Phrase 抽出・Comment 生成へ伝播する経路、Severity 変更が REJECTED/VALIDATED 判定や既存 REPORT の再解釈に与える影響、Disclaimer と学習者への説明責任、Family Z(fiction/literature)への適用可否)。
- 改善提案は「提案」として列挙(採用しない)。**新しい Product 判断が必要な項目は ★ を付けて明示**。

## 出力ファイル `docs/pm/review_ledger_deviation_redesign_01_part_b.md`

各主張に根拠(調査 REPORT の章・事例番号/evidence パス/Ledger fact_id)。断定と論点を分ける。ユーザー向け表記 Standard/Advanced。

## 固定ブロック

T-0: 本委任文を `docs/pm/delegation_log/2026-09-29_LEDGER-DEVIATION-CHECK-REDESIGN-REVIEW-01_02.md` へ逐語保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-29_LEDGER-DEVIATION-CHECK-REDESIGN-REVIEW-01_02.md --json-out docs/pm/delegation_log/2026-09-29_LEDGER-DEVIATION-CHECK-REDESIGN-REVIEW-01_02.md_check.json` を実行し結果1行記録。T-2: TTS なし。T-3: API 支出なし。E-1/D-1/G-1/F-1 標準。

## 事前指定Read一覧 / 事前指定Grep一覧

- 調査 REPORT(全文)、事例 evidence json(REPORT 記載パス)、Hormuz Ledger(`er019_output/family_x_refresh_e2e_01/hormuz/run_02/ledger/` 内 json、Grep `notes_for_writer`)、`CURRENT_SPEC.md` Grep `Key Phrase|Comment|In One Line|Family Z|fiction`(逸脱の伝播経路確認、該当箇所のみ)。
- 更新位置: 出力ファイル(新規)、delegation_log。

## 実行コマンド全文

- `git pull --ff-only origin main`

## Git

- add 対象(path 指定のみ): 出力ファイル、delegation_log+`_check.json`。メッセージ `LEDGER-DEVIATION-CHECK-REDESIGN-REVIEW-01: Part B(Product設計・Fact Safety・事例適用評価・Trial設計・リスク抜け漏れのレビュー、read-only)`、trailer `Management-ID: LEDGER-DEVIATION-CHECK-REDESIGN-REVIEW-01`。push。

## 報告(RESULT_PACKET_RRB + handback、目安45行)

【Product設計レビュー】【Fact Safetyレビュー】【Hormuz事例への適用評価(Claude 独立判定と根拠)】【重大事例への適用評価(5 件の分離可否)】【過剰品質候補への適用評価(4 件)】【Trial設計レビュー】【リスク / 抜け漏れ】【改善提案】【★新しい Product 判断が必要な事項】の各見出しで 3〜6 行の要点/notes_for_writer 12 件の factual/guidance 分類結果/commit hash・raw URL。

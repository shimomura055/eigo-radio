## 管理ID

LEDGER-DEVIATION-CHECK-REDESIGN-REVIEW-01(Part C=Fable 統合レビューの正式 REPORT 保存、委任 _03)。**保存のみ**。Production code/Prompt/schema/severity/SSOT 4 点/REPORT_LEDGER 変更禁止、Trial 実行禁止、E2E 再開禁止、API 支出なし(¥0)、Opus 起動禁止。削除・移動・`rm`・`git clean`・`git stash`・rebase/reset/amend/force push 禁止。未追跡ファイルは他タスク由来として触らない。`git pull --ff-only origin main` 後に着手。push 競合時は `git merge origin/main` のみ。

## 作業

1. `LEDGER-DEVIATION-CHECK-REDESIGN-REVIEW-01_REPORT.md`(root 直下、新規)を作成: 冒頭に Status 行「Status: PROPOSED / REVIEW(Claude レビュー完了、Opus L2 未実施)。Production code/Prompt/schema/severity/SSOT 変更なし。Family X E2E は STOP 維持。」、続けて「入力: ChatGPT 再設計素案(2026-09-29、ユーザー提示)/調査 REPORT `LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_REPORT.md`/Part A `docs/pm/review_ledger_deviation_redesign_01_part_a.md`(commit dcec107a)/Part B `docs/pm/review_ledger_deviation_redesign_01_part_b.md`(commit 2ce78967)」、その後に下記「=== FABLE 統合レビュー ここから ===」〜「=== ここまで ===」を **一字一句変更せず** 貼付。末尾に「詳細根拠(ファイル:行・事例 evidence)は Part A/B を参照」を付す。
2. T-0: 本委任文を `docs/pm/delegation_log/2026-09-29_LEDGER-DEVIATION-CHECK-REDESIGN-REVIEW-01_03.md` へ逐語保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-29_LEDGER-DEVIATION-CHECK-REDESIGN-REVIEW-01_03.md --json-out docs/pm/delegation_log/2026-09-29_LEDGER-DEVIATION-CHECK-REDESIGN-REVIEW-01_03.md_check.json` を実行し結果 1 行記録。
3. path 指定 add(REPORT、delegation_log+`_check.json` のみ)、メッセージ `LEDGER-DEVIATION-CHECK-REDESIGN-REVIEW-01: Fable統合レビュー(Claudeレビュー、PROPOSED/REVIEW、採用なし)を正式REPORTとして保存`、trailer `Management-ID: LEDGER-DEVIATION-CHECK-REDESIGN-REVIEW-01`、push。REPORT_LEDGER 登録文案を handback に 2 行で添える(編集はしない)。
4. 報告(8 行以内): 貼付の逐語性(文字数一致)、commit hash、raw URL。

=== FABLE 統合レビュー ここから ===
【総評】
素案の方向性(検出と Action の分離、Category と Severity の分離、非決定性を前提にした deterministic post-processing、Human Review の非常口化、Disclaimer を品質低下の理由にしない)は妥当で、調査で判明した構造問題(深刻度と STOP 挙動が連動していない/claim 単体判定/auto_downgraded 0 件)に正面から対応している。ただし批判的に見ると、素案の 2 本柱のうち「E. notes_for_writer の soft 化」は実データ(Hormuz Ledger 12 件がすべて factual constraint)と噛み合わず、「C. causality 緩和」は Hormuz B-2 をそのまま緩和対象にすると記事の中心主張を検証から外す危険がある。また素案は Prompt/Schema 変更なしでは実装できず、共有関数のため Family A/B/C/X へ同時波及し、既存決定(fail-closed、JA Fact Check 配線、ER-009-N1 の MAJOR 維持検証)の事実上の再設計になる。結論として「素案は Trial に進める価値があるが、E と C の前提修正、B-2 の扱いの Product 判断、Prompt 変更の波及管理を先に確定すべき」。

【Product設計レビュー】
- 最低品質ライン: BLOCKING 列挙(数値・主体・対象・否定・比較・時系列・値動き方向・重要 Fact 追加・重大因果断定・逆の意味)は調査 §6 の 10 カテゴリとほぼ対応し、抜けは「帰属(出典)のすり替え」「numeric_scope の混同(高値/終値)」「相対時間表現」「引用発言の改変」「極性語(最初/唯一/最大)」。
- STOP 基準「主要 Fact 理解を誤らせるか」の弱点: (1)「主要」の判定主体・基準が未定義で、LLM に委ねると非決定性が二重化する(検出の非決定性+実害評価の非決定性)。(2) 学習者は英語で読むため、母語話者より誤読しやすい(二重否定的な因果構文 "did not lead to a … fall" を Standard/Advanced 学習者が正確に読めるかは未検証)。(3) 逸脱は本文に留まらず Key Phrase・Comment・In One Line へ伝播する(いずれも最終確定本文から選定)。
- 緩すぎる箇所: QUALITY を「通す」とした場合の蓄積ログの置き場・閲覧者・頻度が未定義。まだ過剰品質な箇所: Standard/Advanced の対称 Check は translation-induced に限定できる余地があるが、削減根拠となる「JA/EN 重複検出」は Part A の集計で 0 件(JA MAJOR は must-fix 解消後に EN 段へ進む設計のため重複が観測されにくい)で、現時点では裏付けなし。
- Disclaimer: 役割分担(Checker=合理的最低品質、Disclaimer=残余リスク説明)は妥当。ただし Disclaimer の先行度(Checker 緩和より先に掲示するか)は未定義。

【Fact Safetyレビュー】
- notes_for_writer soft 化の危険(最重要): Hormuz HF-001〜012 の notes_for_writer を全件分類した結果 12/12 が factual constraint(禁止する因果主張の名指し、時系列固定、numeric_scope 固定、certainty の文言指定)、純粋な writer guidance は 0 件。素案 E の前提「Fact=hard/notes=soft」は少なくともこの Ledger では成立せず、soft 化は 10 カテゴリ判定の境界を具体化した情報そのものを失う。他 Ledger・他 Family の実態は未確認。
- causality 緩和: 「ニュース理解の中心か」の判定主体が未定義。Hormuz のように因果が記事主題そのものの場合、緩和は中心主張を検証対象から外す。
- context window: 留保文の「有無」だけを見ると、定型ヘッジを機械的に置くことで免罪符化できる(Hormuz 記事の留保文は JA/EN とも定型パターン)。window 内に矛盾がある場合の扱いも未定義。
- 検出漏れ(A-1 時制ドリフト、Checker 2 回見逃し)は Severity 再設計では解決しない。素案は「緩和」側だけでなく「検出精度」側の対策(fixture 拡充・反復判定)を同時に持つべき。

【Hormuz事例への適用評価】
- 事実: HF-011 の note は「撤回が価格を上昇させた、または下落させなかったと因果推論しない」を literally 禁止。EN "did not lead to a large, lasting fall" はこの禁止パターンと同型。因果は記事の中心テーマ(タイトル・構成が因果的対比)。一方で "large, lasting" の限定語と直後の留保文があり、記事が読者に与える理解(「撤回後も価格は高いままだった」)は HF-009 の観測(縮小 → 回復)と食い違わない。A-2(方向反転)ほどの事実誤認ではない。
- Part B の独立判定: QUALITY/ACCEPTABLE 降格に反対(BLOCKING 寄り)。ChatGPT 見解: QUALITY/ACCEPTABLE 候補。
- Fable 評価: 両者の差は「観測データと整合する『効果の不在』の記述(〜にはならなかった)を、Researcher が明示禁止した因果推論として BLOCKING にするか」という Product 判断そのものであり、Severity ルールで機械的に決められる領域ではない。素案の判断軸「主要な事実関係を実質的に誤って理解するか」に照らすと、実害は低い(理解は観測と一致)が、Ledger の明示禁止と同型である以上「Researcher の警告を Checker が無視してよいか」を先に決める必要がある。★
- 実装上の含意: 素案 H の deterministic rule に「notes_for_writer が明示禁止した推論パターンとの一致検出」を入れるか否かで、この事例の帰結が反転する。

【重大事例への適用評価】
- A-2(上げ幅縮小 → prices began to fall): BLOCKING 列挙「値動き方向の反転」で分離可、単体判定で足りる。
- A-5(rollback → put back the feature): 「意味反転」で BLOCKING 可だが、"put back" の多義性を LLM がどう読むかは非決定的で、context window 判定で QUALITY へ滑るリスク。
- A-3(支払義務者の具体化): 「根拠のない重要 Fact 追加」で BLOCKING 可だが、「重要」の基準が曖昧だと「自然な補完」と降格され得る。
- A-4(企業・店舗 → users): 「対象取り違え」で BLOCKING 可(プライバシー文脈の核心)。
- A-1(時制ドリフト): 検出漏れであり Severity 設計の対象外。fixture として「検出率」側に置くべき。

【過剰品質候補への適用評価】
- B-1(生活ブリッジ文、4 回再現): ACCEPTABLE 化の有力候補だが、「一般常識レベルの経済知識」と「新規具体主張」の境界ルールが素案に無い。JA Writer Prompt が要求する構造要素である以上、Checker 側だけでなく Writer Prompt 側との整合(どちらを直すか)が Product 判断。★
- B-2: 上記のとおり Product 判断。
- B-3(接続詞 so): 境界が最も曖昧。2 つの独立事象を "so" で単一因果に結んでおり、JA 原文が並列なら translation 由来の因果付与の可能性(origin 判定の信頼性も論点)。
- B-4(一般読者心理への一般化 3 件): 現行 must-fix retry 1 回で解消済みの実績があり、新設計で緩めると現状より品質が下がり得る。

【Repo / 実装整合】
- 素案 A〜J のうち Prompt/Schema 変更なしで実現できるものは無い。A(検出/実害/Action 分離)は新レイヤーが存在しない。E は Ledger テキスト埋込(`vfl01.py:302-303`)と Prompt 除外規定(存在しない)の両方が必要。
- origin=ja_source 即 STOP は `er012_e:266-274,388-398,484-498`(`JARecheckRequiredError`)、JA 側は `er019 JA Writer O` の `JAFactCheckStopError`。`_major_deviations()` が 2 ファイルにほぼ同一コードで重複(既に軽度 drift)。
- post-hoc validation(`_apply_deviation_post_hoc_validation` L544-561)は MAJOR/MINOR を機械固定する既存の置き場で、Severity 3 層化・Action 表の実装先として reuse 可能。ただし入力は現行 audit json の構造化フィールド(10 flag・origin・severity・related_fact_id)に限られる。
- 共有実装 drift 回避: 単一 `classify_severity()` を vfl01 に置き、呼び出し側(er012_e/er019/将来 er026)は Action 表のみ持つ構造が候補(採用判断は保留)。
- Family 波及: `run_deviation_check()` は Family A/B/C/X が共有。Family Z は import のみで未使用(将来影響)。

【Prompt変更の必要性】
- B(Severity 3 層)・C(causality 細分化)・D(context window)は `DEVIATION_PROMPT_TEMPLATE`(`vfl01.py:502-541`)本文の書換が不可避 → 全 Family へ同時波及。Prompt 変更は Trial(fixture 回帰)なしに Production へ入れられない。
- E(notes 除外)は Ledger テキスト化側の変更で Prompt を触らずに「notes を Checker に見せない」ことは可能だが、Part B の分類結果から見て推奨できない(factual constraint を失う)。

【Schema変更の必要性】
- severity を MAJOR/MINOR 2 値から 3 値へ変えると、既存 481 ファイル・224 件個票の統計・過去 REPORT 集計・`strict:True`(additionalProperties:False)schema と非互換 → 後方互換のため `severity`(既存)+`severity_final`/`action`/`basis`(hard field か notes か)/`context_evidence` の追加方式が現実的。
- FACT_LEDGER_JSON_SCHEMA の notes_for_writer 分離(factual_constraint / writer_guidance)は過去 Ledger 資産(テキスト保存のみ)への実害は小さい可能性があるが未確認。

【deterministic rule化できる部分】
- origin × severity × category の Action lookup table(既存構造化フィールドのみで可能)。
- 数値・日付・固有名詞の Ledger 値との完全一致/不一致(限定的に可能。単位・表記揺れは要正規化)。
- 「notes_for_writer が明示禁止した推論パターンとの一致」「限定語・qualifier の有無」「留保文の存在」は現行 audit json(自由文のみ)からは不可 → 新 schema で構造化出力(例: `matched_notes_for_writer_id`、`qualifier_present`、`hedge_sentence_within_n`)が前提。

【LLM判断に残す部分】
- paraphrase 境界、意味変化の有無、因果の「中心性」、多義語(put back 等)の読み、context window 内の整合。これらは自然言語理解が本質で deterministic 化不可 → 非決定性対策は「反復判定+多数決/一致率閾値」または「fixture による回帰」で扱うしかない。

【QCD評価】
- call 削減(素案 G): JA/EN の重複検出は Part A の突合(Family X 系 26 ファイル・15 run、related_fact_id)で 0 件。現設計では JA MAJOR が must-fix で解消されてから EN 段に進むため重複が観測されにくく、「JA canonical で品質確保後 EN は translation 限定」は仮説の域。Standard を「Advanced との差分限定 Check」にする案は latency/cost 削減の可能性があるが実測なし。
- 削ってはいけない Check: JA Original(Ledger 逸脱の最初の関門)と Advanced(忠実英訳の意味保持)。JA R2 は R1/R2 が Ledger 改訂を含むため現時点で削減根拠なし。
- 現行コスト: Checker 中央値 ¥0.90/33 秒、記事あたり最低 4 call ≈ ¥3.6。Severity 3 層化自体は call 数を増やさないが、反復判定(非決定性対策)を入れると n 倍。

【Trial設計レビュー】
- fixture 不足: origin 付き実例 15 件は少数。negative example(通すべきもの)が現状ゼロ。追加すべき: Standard 簡略化由来の逸脱、日本語→英語固有の逸脱(主語省略・時制・可算)、帰属・numeric_scope・相対時間・極性語、ER-009-N1 の合成 9 種、B-1 型の「通すべき一般化」。
- 反復: 同一入力 n=5〜10 回×fixture で一致率を測る(必須。既知の未実測ギャップ)。
- 受入条件: 重大 fixture 群の BLOCKING 維持率 100%(1 件でも落ちたら不採用)、不要 BLOCK 率の目標値はユーザー設定、一致率閾値(例: 判定一致 ≥90%)、gold label は 1 人の目視ではなく合議または再ラベルで再現性を確認(調査自体が「1 回限りの目視分類」と自己申告)。
- minimum sample: 記事数・Family 数(A/B/C/X)を跨ぐこと。費用概算: fixture 30 件 × n=5 × ¥0.9 ≈ ¥135/構成、比較構成 2〜3 で ¥300〜400。

【リスク / 抜け漏れ】
- QUALITY ログの置き場・閲覧者・頻度が未定義(貯めるだけになる)。
- QUALITY 逸脱が Key Phrase・Comment・In One Line へ伝播する経路への対策なし。
- Severity 変更が過去の REJECTED/VALIDATED 判定・REPORT 集計の遡及的再解釈を生む。
- 免罪符化(定型ヘッジで通る)。
- Disclaimer の先行度。
- Family Z(fiction/literature)への適用可否(Ledger 概念が異なる)。
- Human Review 非常口の統合先(既存 Human Review Lock は音声専用)。

【改善提案】(提案のみ、採用しない)
1. 素案 E を「notes_for_writer の soft 化」ではなく「notes_for_writer を factual_constraint / writer_guidance に schema 分離し、factual_constraint は hard のまま」へ修正。
2. 素案 C/H に「notes_for_writer が明示禁止した推論パターンとの一致」を deterministic rule として追加し、一致時は自動降格しない。
3. B-1 型は Checker 緩和より先に Writer Prompt(ブリッジ文要求)と Checker の整合をどちらで取るかを決める。
4. Severity は既存 `severity` を残し `severity_final`/`action` を追加(後方互換)。
5. 非決定性対策として反復判定を Trial で測り、Production では「BLOCKING 判定は 2 回中 2 回」等の閾値を検討。
6. QUALITY ログの運用(週次確認・OPEN 化基準)を仕様に含める。
7. 検出漏れ側の fixture(A-1 型)を回帰に追加し、緩和と検出精度を同時に測る。

【既存仕様との競合】
- fail-closed 設計決定(CURRENT_SPEC「安全≠成功」・origin=ja_source 即 STOP)は素案 F の直接的な緩和対象 → SSOT 上の決定更新が必要。★
- JA Fact Check 配線決定(2026-09-27、PRODUCTION_WIRED、OPEN-187)の Action 判定部分の事実上の再設計。★
- ER-009-N1 recalibration(危険 fixture 9 種 全 MAJOR 維持)は 3 層化後に再検証必須。
- OPEN-189(JA Fact Check 固定費最適化)と素案 G は重複 → 統合。
- Human Review Lock(音声専用)への統合可否 未確認。★

【未解決問題】
1. notes_for_writer の実態(他 Ledger・他 Family)が factual constraint 中心か未確認。
2. JA/EN 重複検出の実態(現設計では観測不能)→ 素案 G の根拠なし。
3. Checker 非決定性の定量(未実測)。
4. B-3 の origin 判定の信頼性(JA 原文が並列か因果か未確認)。
5. Family X E2E(B-2)は STOP 維持中。

【ユーザー判断が必要な事項】★
1. Hormuz B-2 型(観測と整合する「効果の不在」記述だが Researcher が明示禁止した因果推論と同型)を BLOCKING にするか QUALITY にするか。推奨: 素案の判断軸に忠実なら QUALITY だが、その場合「notes_for_writer の明示禁止を Checker が無視してよい条件」を仕様に明記すること。
2. 素案 E の修正可否(soft 化 → schema 分離・factual_constraint は hard 維持)。推奨: 修正する(実データ 12/12 が factual)。
3. B-1 型(Writer Prompt が要求するブリッジ文)を Checker 側で許容するか、Writer Prompt 側を直すか。推奨: Checker 側に「Ledger 外の一般常識レベルの帰結」許容ルールを Trial で検証(Writer Prompt は既承認のため変更しない)。
4. fail-closed 決定・JA Fact Check 配線決定の更新を伴う再設計として進めることの承認。
5. Trial の受入条件(重大 fixture BLOCKING 維持率 100%、不要 BLOCK 率目標、一致率閾値)と gold label の付与者(ユーザー単独か合議か)。
6. Family X E2E の扱い: 再設計 Trial 完了まで STOP 維持か、現行仕様で JA 側 must-fix 差し戻し(前回提示の (b))を暫定実装して E2E を先に完了させるか。推奨: 後者(暫定 (b) は Prompt 不変・既存 retry 原則の範囲、E2E の残り Gate 検証が先延ばしになるコストが大きい)。

【次にやること】
1. ユーザー・ChatGPT で本レビューを反映した修正版素案を作成。
2. 修正版 → Opus L2 レビュー(別管理ID、Fable は勝手に起動しない)。
3. Opus 後、Trial 計画(fixture・反復・受入条件)を確定して Trial 管理ID を起票。
4. 判断 6 に応じて Family X E2E の再開/待機。

【費用】
A. 開発・検証の一回限り費用: 本レビュー ¥0(Sonnet 3 件、Opus 0 件)。想定 Trial 概算 ¥300〜400(fixture 30 × n=5 × ¥0.9 × 構成 2〜3)。
B. Production 量産時の継続コスト差: 素案採用時の見込み — Severity 3 層化自体は ±0、反復判定を入れると Checker 費用 n 倍(n=2 で記事あたり +¥3.6)、call 削減(素案 G)は根拠未確立のため 0 で見積もる。

【Status / Open Item】
- 再設計案: PROPOSED / REVIEW(Claude レビュー完了、Opus 未実施)。VALIDATED / APPROVED_FOR_PRODUCTION / PRODUCTION_WIRED のいずれでもない。
- `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01`: USER_DECISION_REQUIRED(STOP 維持)。
- APPROVED_FOR_PRODUCTION / PRODUCTION_WIRED: 変更なし。
- CLOSED / OPEN_ITEMS 更新: なし(SSOT 未編集)。OPEN 新設候補: notes_for_writer の schema 分離、Checker 非決定性の定量実測、QUALITY ログ運用、Family Z への Checker 適用範囲。
- APPROVED_FOR_PRODUCTION だが未配線の項目: なし。
- 残存 USER_DECISION_REQUIRED: 上記 ★1〜6。
=== ここまで ===

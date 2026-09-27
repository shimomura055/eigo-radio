# 委任文全文(2026-09-27、KEY-PHRASE-DB-HYBRID-TRIAL-03、Sonnet委任 初回)

管理ID: KEY-PHRASE-DB-HYBRID-TRIAL-03(Trial。到達可能Status=REJECTED/VALIDATED/USER_DECISION_REQUIRED。**Production配線・APPROVED_FOR_PRODUCTION化・DBなしPrompt-only比較・Oxford/EVP等の新DB探索・有料DB契約検討・Key Phrase以外の記事仕様変更・LLM call増加による力技は禁止**)。一時ファイル `docs/pm/ACTIVE_TASK_KPH3.md` / `docs/pm/RESULT_PACKET_KPH3.md`(commitしない)。他Agent並走中(Family X Stage 3c=`er019_family_x_audio_*`、PMルール配線=docs/pm/PM_*)→ 触らない。Production Key Phrase module(`er003_key_words_*`、`er003_b1_p2_keywords.py`、prompt template)は**読み取り・importのみ**(Trial側in-memoryコピーで実験)。SSOT 3ファイル・REPORT_LEDGERは編集しない。

先に読む: `docs/pm/PM_BRIEF.md`、`docs/pm/PM_GOVERNANCE.md` の「Existing Spec / Prior Trial Check Gate」節と13節(新規記事テーマ選定ルール)(Grep)、`KEY-PHRASE-DB-HYBRID-TRIAL-02_REPORT.md`(全文)、`er027_key_phrase_db_hybrid_trial_02*.py`、`er027_output/key_phrase_db_hybrid_trial_02/`、`KEY-PHRASE-DB-BASED-SELECTION-TRIAL-01_REPORT.md` §13。

## 既存資産照合(先頭で実施、RESULT_PACKETにA/B/C分類を記載)
新しい修正・USER_DECISION_REQUIRED提示の前に必ず CURRENT_SPEC / DECISION_LOG / OPEN_ITEMS / 過去Key Phrase REPORT / Production code / tests を確認し、A(既存仕様あり→新規仕様化せず、未発火はimplementation/wiring bug)/B(過去Trialあり→理由なく繰り返さない)/C(本当に新規)に分類。特に: 既存Strategy L promptがarticle全文を渡す仕様の根拠、既存の有限助動詞hard requirement(`have a big moment`)の仕様と自動再試行の既定(`MAX_PRODUCTION_RETRY_ATTEMPTS`)、possessive/品詞処理の既存関数、upstream Topic metadataの所在。

## ユーザー指示(正本、逐語要点)
目的: Trial-02でVALIDATEDのHybridを、Production候補として成立する水準まで軽量化・安定化。(1) LLM inputを軽量化し現行Strategy Lと同等以下のcost、(2) 既知bug/false positiveを一般化して修正、(3) 既存6本文で回帰、(4) 条件を満たしたら新記事で実Trial、(5) Production採用・配線はしない。

**設計思想(維持)**: 本文→DB/deterministic codeで広く候補生成→deterministic screening/normalization→約20件へ圧縮→Strategy Lが最終5件を1回で選定。最終5件: 少なくとも1枠=重要word/technical term/multiword term/noun phrase、残り3〜4枠=phrase/idiom/phrasal verb優先、不足時のみword/termで補完、CEFR難易度は主要軸にしない、learner reuse value/article importance/generality/chunk valueを重視。

**最重要: LLM input軽量化(Primary設計)**: 最終Strategy Lへ**article全文を再送しない**。渡すものは必要最小限: A. 上流から再利用できるTopic情報(title / article topic・central theme / 必要ならheading / Writer・upstream metadataとして既に存在するtopic情報。**新しいLLM callでTopicを再抽出しない**)。B. Stage 1 shortlist(各候補: candidate text / type / article occurrence count / compact evidence / 必要最小限のlocal context=短いsource sentence・snippetのみ。同一sentenceの重複送信はsentence ID化等で削減。DB evidenceは冗長な自然文にしない。例 `candidate: contract workers | type: noun_phrase | occ: 3 | evidence: repeated_compound | context: "..."`)。DB名の長い説明・不要なfrequency説明・Trial由来の監査情報はpromptへ入れない。

**Topic word/important term**: 優先順位 (1) 上流のTopic/title/central-theme metadata再利用(Family X: `storyline_b3`出力・`ja_writer/runtime_evidence.json`のtitle・`entry_point.json`等を調査)、(2) deterministic code(title/heading/repeated noun phrase/occurrence/DB・wordfreq)でimportant term候補生成、(3) LLMはshortlist+最小contextから最終判断。Topic metadata不足でも別LLM callを追加しない。どうしても全文が必要なら「なぜshort context+upstream metadataでは判断不能だったか」を明示してSTOP。

**Cost目標**: 現行Strategy Lと同等以下。同条件で比較。必須計測: input/output/reasoning tokens、total cost、latency、LLM call count。1本文1 call、candidate cleanup用・Topic抽出用の追加LLM禁止。「現行以下」未達なら何tokenが何のために増えているかを分解。

**Known bugs(一般化して修正必須、個別hardcode禁止)**: A. discontinuous phrasal verb false positive("large bags out"→"bags out"): 文中でverbとして成立していない候補を落とす(POS/lemma/local syntax/particle relation等)。pull back/roll back/take over等の正しい候補を壊さない。回帰test必須。B. Wiktionary multiword_termの粗さ(even though/other side/other end がimportant noun phrase bucketへ誤混入): multiword_term=important noun phraseと単純扱いしない。important term bucketではnoun/noun phrase/technical termとして妥当かを判定。function-word中心・conjunction/discourse系・一般的すぎるfragmentはnoun phrase枠へ入れない(phrase/discourseとして価値があれば別category)。C. possessive 's等のnoise(user's/chart's/season's)を一般化して除去。D. important noun phrase bucket精度: contract workers/sea blockade/Brent crudeを保持。false positive削減のために重要候補を落とす方向へ過剰最適化しない。E. small_bag `have a big moment`(Hybrid/baseline双方で既存Gate INVALID、Hybrid起因ではない): 既存仕様・過去Trial・Production codeを確認し、対策済み仕様の未発火・実装bug・validator bugなら修正(**Trial側で**。Production module変更が必要ならSTOPして報告)。新しい仕様判断が必要ならSTOP。

**Regression(既存6本文、本文再生成なし)**: Meta/Hormuz/small_bag × Standard/Advanced。確認項目: (1) shortlist 20前後 (2) contract worker(s)保持 (3) Brent crude保持 (4) sea blockade保持 (5) phrase/idiom/phrasal verb候補が適切に残る (6) bags out false positive消失 (7) noun phrase bucketのWiktionary誤分類減少 (8) possessive noise除去 (9) Strategy L 1 call (10) article全文がLLM inputへ入っていない (11) 最終5件構成が設計どおり (12) 現行同等以下のcost (13) 品質がTrial-02から明確に悪化していない。Trial-02 outputと比較。

**新規記事Trial**(6本文regressionが受入条件を満たした場合のみ): 新しい記事1本。条件: 既存完成本文ではない新記事 / Key Phrase評価のために余計な記事仕様変更をしない / Standard・Advancedがあればlevelごと独立実行 / Hybrid以外の新仕様を混ぜない / 最終5件全文提示 / shortlist提示 / cost・token・latency提示 / Topic metadataをどこから再利用したか明示 / LLMへarticle全文を渡したか否か明示。**新規記事テーマ選定**: PM_GOVERNANCE 13節(新規記事テーマはFable/Claudeが単独で決めない。複数テーマ候補[英語・日本語・短い選定理由]を提示しユーザーが選ぶ)が既存ルールのため、regression完了時点で**テーマ候補3件をRESULT_PACKETに提示してSTOP**(記事生成はユーザー選定後の次委任)。既存のFamily X Production text runner(`er019_family_x_entertainment_production_runner_01.py`、テキスト工程のみ)を使う前提で、生成コスト見積(Meta実績約¥45/記事)も併記。

**Quality評価**(最終5件): article理解に重要か / learnerが他文脈でも使えるか / phrase・chunkとして自然か / article-specific fragmentではないか / proper nounだけではないか / trivialすぎないか / important term枠が意味のある語か / phrase偏重で重要termを隠していないか / word偏重へ戻っていないか。「現行Productionとの一致率」は参考指標に留める。

**Opus**: 今回はProduction module変更なしのため起動しない(儀式的起動禁止)。

**STOP条件**: article全文を渡さないと品質維持不能 / 追加LLM callが必要 / costが現行より明確に高いまま / important termが機械screeningで落ちる / known bug修正で正しいphraseを大量に落とす / 新しいDBが必要 / Production仕様変更が必要 / 既存仕様との衝突 / USER_DECISION_REQUIRED発生。

## 実装上の指示
- 新規ファイル er028(未使用番号をGlobで確認)`er028_key_phrase_db_hybrid_trial_03*.py`、出力 `er028_output/key_phrase_db_hybrid_trial_03/`。er027のStage 1ロジックはimport/コピー再利用可(er027成果物は壊さない)。
- LLM: 既存Strategy Lと同じ`SELECTOR_MODEL`/`SELECTOR_REASONING_EFFORT`/JSON schema/`run_production_selection_gate`(Routing Contract経由=Luna)。prompt本体はin-memoryコピー(article全文部分を除去し、Topic metadata+compact shortlist+構成ルールに置換)。`max_attempts=1`。
- 現行baseline比較: 既存`keywords_canonicalized.json`のusage記録(あれば)またはTrial-02のbaseline測定(small_bag 2件)を再利用し、再度baselineを走らせない(¥節約)。同条件が取れない本文は「参考」と明記。
- unit test: Stage 1の各修正(A〜D)の陽性/陰性、article全文非送信のassert(prompt文字列に本文の連続100語が含まれないこと)、決定論性。
- 費用Guardrail: 合計¥60(6本文×1 call≒¥8前後+予備)。¥50到達で中止・報告。APIキーは環境変数のみ。

## 報告(`KEY-PHRASE-DB-HYBRID-TRIAL-03_REPORT.md`、root)
ユーザー指定の14項目: 新しいHybrid input構造 / LLMへ実際に渡した情報(1本文分のprompt逐語をappendix) / article全文を送ったか / bug修正内容(A〜E、既存資産照合の分類付き) / regression 6本文結果(13項目表) / 新規記事Trial(テーマ候補提示でSTOPした旨) / 最終5件(6本文) / input・output・reasoning token / cost・latency / 現行Productionとのcost比較(token分解) / Trial-02との品質比較(9観点) / Fable評価欄(空欄) / Status仮分類 / 未解決事項。RESULT_PACKET_KPH3.mdに要約+テーマ候補3件。

## Git
新規ファイル・出力JSON・REPORTのみpath指定add(`git add -A`禁止、他Agentのstageを外さない、index.lockリトライ)。トレーラー `Management-ID: KEY-PHRASE-DB-HYBRID-TRIAL-03`。push origin main。`ACTIVE_TASK*`/`RESULT_PACKET*`はcommitしない。reset/amend/rebase/force push禁止。委任文全文を `docs/pm/delegation_log/2026-09-27_KEY-PHRASE-DB-HYBRID-TRIAL-03_01.md` へ保存しcommitに含める(新ルール)。

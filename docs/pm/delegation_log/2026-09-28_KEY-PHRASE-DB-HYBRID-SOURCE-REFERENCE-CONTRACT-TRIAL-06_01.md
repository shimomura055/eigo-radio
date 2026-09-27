# 委任ログ: KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-TRIAL-06

日付: 2026-09-28
委任元: sandwich-pm(Fable)
実行層: Sonnet 5

## 委任文全文

管理ID: KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-TRIAL-06(Phase A: 設計レビューのみ。**¥0、API呼び出しなし、コード変更なし、SSOT編集なし**)。一時ファイル `docs/pm/ACTIVE_TASK_KPS1.md` / `docs/pm/RESULT_PACKET_KPS1.md`(commitしない)。委任文全文を `docs/pm/delegation_log/2026-09-28_KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-TRIAL-06_01.md` に保存しcommitに含める。

### 背景(ユーザー指示、逐語要旨)
Core v2 Trial-05で、quote-heavy本文(twins A2 / Melos A2)においてLLMが `source_sentence` へ表示用の引用符まで含めて返し、substring照合でINVALIDになった。「再サンプルすれば通る」を合格理由にしない。量産(数百〜数千記事)では低確率の書式揺らぎでも頻繁なSTOPになる。**v1/v2共通のProduction耐久性課題**として扱う。
基本改善案(ChatGPT案): LLMにcanonical `source_sentence` 全文を再コピーさせず、**Sentence ID(例 "S6")だけを返させ**、システム側で S6→canonical sentence を決定論的に復元して保存・validator照合する。可能ならJSON Schemaで当該記事に実在するSentence IDのみをenum許可し、存在しないID・コピー揺らぎを構造的に防止。単に `"` を別delimiterに変えるだけで終わらせず、「そもそもLLMにcanonical sentenceを再生成/再コピーさせる必要があるか」から見直す。
最優先評価軸: **量産時に書式揺らぎでSTOPしないこと**。

### 先出しRead
- `er030_key_phrase_db_hybrid_selector_01.py`(v1 Production: prompt組み立て、SENTENCE REFERENCE表、JSON schema、`run_production_selection_gate` への受け渡し、S3 raw本文照合)、`er003_key_words_production.py`(Strategy L selector schema・structural validator・`source_sentence`/`source_span` の定義と照合ロジック)、`er003_key_words_min_unit.py::_normalize_for_match`、`er003_key_phrase_source_gate_01.normalize_text`(Assembly直前Gate)、`er003_key_words_canonicalization.py`(`qa_traceable_contiguous_span`)、`er029_*_stage1.py`/`er032_*_stage1.py`(sentence unit生成、v1/v2の文分割差)、Trial-05 REPORT §(twins/Melos INVALIDの実出力: `er032_output/.../twins_a2/`、`melos_a2/` の selector raw output と validator reason)、Family Z Trial REPORT、CURRENT_SPEC Key Phrase節(source_sentence/source_span/Source Consistency Gateの仕様行)。

### 設計レビュー(`docs/pm/design_kp_source_reference_contract_01.md` 新規)
以下の確認事項をそれぞれ事実+評価で記述(推測は明示):
1. Sentence ID方式で失われる情報(現在 `source_sentence` 文字列がvalidator・canonicalization・Source Gate・player表示・Trial比較でどう使われているか、IDから復元すれば等価か)。
2. phraseが複数sentence/spanにまたがる場合(現行仕様は許容するか、実データでの頻度)。
3. `source_span` との関係(spanは引き続きLLMが返すのか、span照合は復元sentence内で行うか、spanにも同種の揺らぎリスクがあるか→ span も "文字列コピー" なので同じ問題が残る点を必ず評価。代替: span を **sentence内オフセット**や**候補ID(shortlistの候補ID)**で返させる案)。
4. quote-heavy dialogue・sentence segmentation(v1/v2の文分割が異なるとIDの意味が変わる→ IDは「その呼び出しで提示したSENTENCE REFERENCE表」に対して閉じるので問題ないか、debug/監査での再現性)。
5. duplicate/similar sentence(同一文が2回出る場合のID一意性、Source Gateの複数一致)。
6. heading/fragment(見出し・断片がsentence unitに含まれる場合)。
7. multiword expression・pronoun normalization(`in someone's place` のような正規化形と原文spanの対応。候補IDで返す案との相性)。
8. existing validatorとの整合(`run_production_selection_gate` はテキストを期待→ Trial層で復元して渡せば**validator無変更**で済むか。Production validator側の変更が必要なら範囲)。
9. retry/fallback(Redundancy QA retryでのID表の再利用=S8キャッシュ、fallback[Strategy L全文方式]は現行contractのまま=混在の扱い)。
10. backward compatibility・artifact/schema影響(`keywords*.json` の `source_sentence` は復元テキストを保存すれば下流無変更か、`source_sentence_id` を追加フィールドとして保持)。
11. migration方法(既存artifactは無変更、新規のみ新contract。v1 Production[er030]への適用はTrial検証後の別判断)。
12. 新たなfalse accept/false reject(IDが実在するが意味的に誤った文を指すケース=validatorのspan照合で検出できるか、schema enumで存在しないIDを防げるか[OpenAI structured outputsのenum制約の実現可否・制限数]、LLMがIDを取り違えるリスクとその検出)。
13. より堅牢な代替案: (i) Sentence ID+span文字列 (ii) Sentence ID+sentence内文字オフセット (iii) shortlist候補ID(候補の `sentence_ids`/`surface`/`span` はStage 1で決定論的に既知)だけを返させ、テキストは一切LLMに書かせない (iv) 現行+正規化強化(引用符・空白・句読点をvalidator側で寛容化)。各案を「書式揺らぎ耐性 / 情報損失 / validator変更範囲 / 実装コスト / false accept・reject / v1・v2適用容易性」で比較表。
14. **Fableへの推奨案**(A: ChatGPT案そのまま / B: 改良版 / C: 別方式)と理由、Trial実装の最小範囲(新規 `er034_*` として er029(v1)/er032(v2) の選定層を**ラップ**し、Production `er030`・v1 baselineは無変更)、検証計画(twins A2・Melos A2・X 12本文、1本文1 call、全文非送信、cost、反復安定性は構造修正後に確認)、受入条件との対応、STOP条件該当の有無。

### Git
設計書・delegation_logのみpath指定add(`git add -A`禁止、他Agent[er003_v1_crosslevel_*, er006_preprod_*, er025_*]のstageを外さない、index.lockリトライ)。トレーラー `Management-ID: KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-TRIAL-06`。push origin main。RESULT_PACKETに推奨案・比較表要約・STOP該当・Trial見積を記載。

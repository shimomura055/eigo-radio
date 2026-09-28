# 委任文全文(2026-09-28、KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01、初回)

管理ID: KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01(Phase A: 現行実装調査+最小実装設計。**read-only・¥0・API呼び出しなし・コード/SSOT編集なし**)。一時ファイル `docs/pm/ACTIVE_TASK_KP41A.md` / `docs/pm/RESULT_PACKET_KP41A.md`(commitしない)。委任文全文を `docs/pm/delegation_log/2026-09-28_KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01_01.md` に保存しcommitに含める(このファイルと設計書のみcommit可)。他Agentが `er030_*`/`er003_v1_n3_01_scaffold_generate.py`/SSOT/`er021_*`/`er006_preprod_*`/`er003_v1_*`/`er033_*`/`er019_*` を編集中 → 読み取りのみ。

## ユーザー正式決定(APPROVED_FOR_PRODUCTION、逐語要旨)
1. Key Phraseは5枠固定のまま **4(重要語・重要表現)+1(Topic Phrase/Word)** 構成。総数不変。
2. Topic Phrase/Word定義: 「汎用性・一般的な学習重要度は必ずしも高くないが、その記事に特有であり、事前に意味・用法・音を理解しておくことで本文全体を追いやすくなるワードまたはフレーズ」。中心質問: 「この語・表現を事前に理解していると、この記事の本文を明確に追いやすくなるか?」
3. Topic Phraseは「固有名詞枠」ではない: 人名・企業名・ブランド名・地名だから選ぶruleを設けない、固有名詞優先の例示をPromptに入れない、網羅思想にしない、特定記事・固有名詞の例をhard-codeしない。
4. 追加表示: 音声5枠とは別に「Topic Phrase/Word」「5枠に入らなかった重要語・重要フレーズ」を将来のアプリのスクリプト表示画面で任意確認可能に。本番UIが未存在/別系統なら無理にUI新設せず、Production記事生成側で後段UIが利用可能な構造化データとして保持・出力するまでを対象、既存UI経路があればそこへ最小配線。
- 設計方針: 既存Strategy L(Listening Blocker Ranking)を全面置換しない。Canonicalization / Japanese gloss / display・TTS separation / Redundancy QA / source consistency gate / Human Review・retry / Standard・Advancedそれぞれの最終本文から独立選定 を壊さない。
- **Claude独自の追加Product ruleを作らない**(固有名詞優先・専門語優先・タイトル語優先・出現回数N回以上・難易度・CEFR外優先・名詞優先・必ず複合語・カテゴリ除外/優先)。必要と感じたらUSER_DECISION_REQUIREDでSTOP。
- QCD: 追加LLM callなし(既存選定call内で処理)が第一候補。大規模再設計しない。Important 4枠の品質低下なし。
- **ユーザー向け表記**: 学習レベルはStandard/Advanced(A2/B1/B1Bは内部ID・artifact名のみ)。

## Existing Spec Check(先に必ず)
- Family体系: Active Production = Family X/Z(開発フォーカスX/Z)。Family A/B/C = legacy(更新・新規実装なし、read-only参照のみ)。ユーザー指示の「Family A/B/C/News等の共通経路」「Voices系/Fiction・Family C系での検証」は、**legacy記事本文をread-onlyの検証入力として使う**ものと解釈し、配線対象はActive経路(Family X: DB Hybrid Primary[er030 候補ID contract、PRODUCTION_WIRED済み+修正中]/Strategy L fallback、Family Z: er026 text runnerのKP経路)に限定する。解釈の根拠をCURRENT_SPEC「Family体系」節でGrep確認し記載。
- 既存仕様との関係: Strategy L(`er003_key_words_production.py`)の選定原則・schema(`_ITEM_SCHEMA_PROPERTIES`、`phrase_type`等のenum)、DB Hybrid selector(`er030_key_phrase_db_hybrid_selector_01.py`/`..._source_reference_contract_01.py`: compact shortlist prompt、候補ID enum、復元)、canonicalization(`er003_key_words_canonicalization.py`、prompt template `er003_v1_translator_briefs/b1_p2_keywords_canonicalization_prompt_template.txt`)、Redundancy QA(`er011_key_phrase_set_redundancy_qa_01.py`)、source gate(`er003_key_phrase_source_gate_01.py`)、structural validator(`er003_key_words_min_unit.py`)、retry/regeneration入口(`er003_v1_n3_01_scaffold_generate.py::run_key_phrases`)、Family X runner `run_theme_scaffold`、Family Z `er026_*` のKP呼び出し、KP asset schema(`keywords*.json`、`keywords_canonicalized.json`、`keywords_runtime_metadata.json`)、user_test/script表示側で使うasset(`user_test/*.html` 生成元、`er003_b2_key_words.build_key_words_reading_copy`、player生成)、過去のKey Phrase関連決定(CURRENT_SPEC Key Phrase節、DECISION_LOG「Key Phrase」Grep: 5件固定・phrase優先・Strategy L・source consistency・4+1に類する過去議論の有無)。

## 調査・設計(設計書 `docs/pm/design_kp_4plus1_topic_phrase_01.md` 新規)
A. Production正式初回経路の特定(Family X: DB Hybrid→候補ID contract→validator→canonicalization→Redundancy QA→source gate、fallback Strategy L; Family Z: 現行経路)。retry/regenerationの入口。DEV/Trial scriptと区別。
B. 4+1の最小実装案: **同一selector call内**で `role: important|topic` を返させる(DB Hybrid: 候補ID+role; Strategy L: 既存item schemaへrole追加)。schemaはOpenAI structured outputsのenum。validatorで「topic=1件、important=4件」を構造条件として検証(不成立時の扱い: 既存retry予算内で再選定→fallback→Human Review。**新ruleを作らず**既存の失敗経路を使う)。Topic Phrase Promptはユーザー定義文と中心質問のみ(例示・優先ruleなし)。DB Hybridのcompact shortlistでTopic候補が候補集合に含まれるか(Stage 1が記事特有語をscreeningで落とす構造なら、それはSTOP候補[新rule必要]として報告)。
C. 構造化: 既存schemaへ最小追加(例: item `role` フィールド、`keywords_runtime_metadata` に `selection_contract="4plus1_v1"`)。後方互換(既存artifact無変更、`role`欠落=旧contract)。canonicalization/Redundancy QA/source gate/TTS reading copy が `role` を無視して従来どおり動くか、Redundancy QAが「topicとimportantの役割重複」を判定できるか(既存prompt流用の可否)。
D. 追加表示用データ: 5枠外の候補を、既存intermediate artifact(DB Hybrid shortlist `db_hybrid_stage1_debug.json`/候補ID表、Strategy Lのranking候補)から**安全に再利用**できるか。件数・UI配置は決めない(必要ならUSER_DECISION_REQUIRED)。既存UI経路(user_test html生成、Key Phraseハイライト OPEN-169)の有無と最小配線可否。
E. 検証計画: 既存完成記事(read-only): Family X News(Meta/Hormuz/small_bag)、Voices系(Family B legacy)、Fiction(Family Z Melos、Family C twins)の Standard/Advanced、evidenceモードで実行(見積・Guardrail案)。10項目の観点表。retry/regenerationでの4+1維持の確認方法。
F. STOP条件該当の事前判定(Topic定義だけで安定選定できるか / Strategy L衝突 / 追加call / Dangling Reference / UI件数判断)。
G. 他Agentとの衝突(er030・scaffold_generate・SSOTは修正中)→ 実装Phaseの開始条件を明記。

RESULT_PACKETに: 経路表、最小実装案、schema変更案、追加表示データ方式、STOP候補、見積。Git: 設計書・delegation_logのみpath指定add、トレーラー `Management-ID: KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01`、push origin main。

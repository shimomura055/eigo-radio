# ER-PM-001 受入テスト: 15問の回答速度テスト

**実施日: 2026-08-09**
**方法: Git全履歴の再監査を行わず、新設した6文書のみを参照して回答した。**

各回答に「参照した文書」を明記する。詳細な一次証拠(commit/manifest)は
参照先の文書内にリンクされている。

---

**Q1. A2の正式仕様は何か**
A. 存在しない。CEFR-A2の全項目(語彙・文長・語数等)が`TBD`。
参照: [CURRENT_SPEC.md](CURRENT_SPEC.md) CEFR節、[OPEN_ITEMS.md](OPEN_ITEMS.md) OPEN-01/OPEN-02

**Q2. B1の平均/最大文長は何か**
A. 平均15語以下・最長24語(`B1_MAX_SENTENCE_WORD_COUNT`)。ただし**診断のみでgateではない**。
参照: [CURRENT_SPEC.md](CURRENT_SPEC.md) CEFR節

**Q3. B2の平均/最大文長は何か**
A. 平均19語以下・最長32語(`B2_MAX_AVG_WORDS_PER_SENTENCE`/`B2_MAX_SENTENCE_WORD_COUNT`)。こちらは**実際のgate**。
参照: [CURRENT_SPEC.md](CURRENT_SPEC.md) CEFR節

**Q4. Key Phraseは何語までか**
A. 1〜5語(`key_phrase`)。
参照: [CURRENT_SPEC.md](CURRENT_SPEC.md) Key Phrase節

**Q5. Key Phraseはどう選ぶか**
A. 各記事自身の承認済みCEFR-B1本文から、Strategy L(Listening Blocker Ranking)で5件選定し、Pedagogical Phrase Canonicalization(最小十分原則、3状態QA、人間確認フロー付き)で正規化する。
参照: [CURRENT_SPEC.md](CURRENT_SPEC.md) Key Phrase節、[DECISION_LOG.md](DECISION_LOG.md) ER-003-P2I/KP-01/KP-02/KP-02-R1

**Q6. PreviewのTTS modelは何か**
A. `gemini-3.1-flash-tts-preview`、voice=Aoede、日本語のみ、単一call。
参照: [CURRENT_SPEC.md](CURRENT_SPEC.md) Preview節

**Q7. Full StoryのTTS modelは何か**
A. `gemini-2.5-pro-preview-tts`、voice=Aoede、3chunk構成(凍結仕様)。
参照: [CURRENT_SPEC.md](CURRENT_SPEC.md) Full Story節

**Q8. A01 B2音声は存在するか**
A. 存在しない(未生成)。現行CEFR-B2はテキストのみで、Preview/Key Phrase/Full Story/Podcast組立のいずれも生成実績がない。
参照: [ARTIFACT_REGISTRY.md](ARTIFACT_REGISTRY.md) A01行

**Q9. A01 B1音声は承認済みか**
A. Podcast組立(最終r2版)自体は存在するが、`user_quality_status`は`NOT_REVIEWED`(段階的な部分承認はあるが、最終版の通し試聴OK記録がない)。`publication_status`も`NOT_APPROVED`。
参照: [ARTIFACT_REGISTRY.md](ARTIFACT_REGISTRY.md) A01行・補足

**Q10. A02 B1は完成しているか**
A. 完成している。Source〜Podcast組立まで全てPASS、`user_quality_status: PASS`(2026-08-08、初回通し候補をそのままOK)。ただし`publication_status`は`NOT_APPROVED`。
参照: [ARTIFACT_REGISTRY.md](ARTIFACT_REGISTRY.md) A02行

**Q11. ADD03 B1は完成しているか**
A. 完成している。`user_quality_status: PASS`(2026-08-09)。meaning_3はASR homophone ambiguityとして人間確認済み(TTS自体は正常)。`publication_status`は`NOT_APPROVED`。
参照: [ARTIFACT_REGISTRY.md](ARTIFACT_REGISTRY.md) ADD03行

**Q12. 過去にAzureを試したか**
A. TTS(音声生成)としては、利用可否の確認のみで実生成テストは行っていない(比較対象止まり)。ASR(音声認識、Azure STT)としては全ステージで診断用途に使用している。
参照: [HISTORY_INDEX.md](HISTORY_INDEX.md) ER-003-B1-P5A行、[CURRENT_SPEC.md](CURRENT_SPEC.md) QA節

**Q13. 過去にGCPを試したか**
A. 試した。Google Cloud TTS(Neural2-B)で実際に生成しユーザー試聴したが、機械的な音声・誤読と判定され`REJECTED`。
参照: [HISTORY_INDEX.md](HISTORY_INDEX.md) ER-003-B1-P5B〜P5C行、[DECISION_LOG.md](DECISION_LOG.md) 「Google Cloud TTS(Neural2-B)を不採用」

**Q14. 現在のBlocking issueは何か**
A. OPEN-01(CEFR-A2仕様が0件)とOPEN-02(A2の生成元に関する矛盾)の2件。いずれもA2制作着手前に解決必須。B2音声化(OPEN-03)は現状Non-blocking。
参照: [OPEN_ITEMS.md](OPEN_ITEMS.md)

**Q15. A2で次に決めるべきことは何か**
A. まず(1)生成元をNatural English Sourceからの独立生成にするかB1からの派生にするか、(2)その上でCEFR-A2の語彙・文長・語数等の数値仕様をユーザーが新規決定すること。既存の`levels.py`(無関係な別番組の値)や現行B1/B2の値をそのままコピーしないこと。
参照: [OPEN_ITEMS.md](OPEN_ITEMS.md) OPEN-01/OPEN-02、[ER-003-A2-00_SPEC_AUDIT.md](ER-003-A2-00_SPEC_AUDIT.md)

---

## テスト結果まとめ

- 全15問、Git全履歴の監査を行わずに回答できた(新設6文書のみを参照)。
- 全ての回答が具体的な参照先を1〜2ホップで明示できた。
- 曖昧語(「たぶん」「以前使った気がする」等)を含む回答は0件。

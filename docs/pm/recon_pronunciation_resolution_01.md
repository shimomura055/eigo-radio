# Recon: 固有名詞読み解決(日本語TTS/英語TTS共通)設計調査(read-only、Phase 1)

管理ID: PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01(Phase 1)
作成: Sonnet実行層(read-only recon、Production code/Prompt/SSOT変更なし、API費用¥0)

前提: 本文書は「事実(コード引用・実データ引用、ファイルパス・行番号・関数名付き)」
と「推測/設計提案」を区別する。既存の関連recon
(`docs/pm/recon_tts_symbol_normalization_01.md`、
`docs/pm/recon_reading_validation_wiring_01.md`)と重複する詳細は新規知見のみ
追記し、全文は複製しない。

---

## 0. ユーザー決定の要約(委任文からの転記、正本は委任文本体)

対象は人名/企業名/サービス名/製品名/地名/ブランド名/略語/通常辞書にない固有
名詞・外来語について、(A) 日本語TTS(Latin表記の日本語読み)と (B) 英語TTS
(固有名詞の英語発音)の両方。「辞書未登録だからHuman Review」という現行の
一部挙動を禁止し、Detect→Known dictionary/cache→Existing reliable resolver→
Official/trusted source lookup if needed→Confidence判定→高confidence自動使用
→dictionary/cacheへ保存→TTS→ASR/pronunciation validation→retry/fallback→
それでも不能な場合のみHuman Reviewという共通フローを設計する。Active
Production Family = X/Z(開発中心)。Family A/B/Cはlegacy/backup(read-only
参照元のみ、新規実装しない)。Status: `APPROVED_FOR_PRODUCTION`(Phase 2で
配線、本Phaseは設計のみ)。

---

## 1. 棚卸し(作業1): 既存資産インベントリ

### 1.1 日本語側(JA TTS: Latin表記の日本語読み)

| 機構 | 既存仕様(SSOT/REPORT) | Production初回pathの実装 | retry/fallback/regeneration時の挙動 |
|---|---|---|---|
| 読み方辞書(静的、小規模) | `ER-009-JA-READING-DICTIONARY-ACRONYM-EXPANSION-AND-TREND-A2-RESUME-01_REPORT.md`(2026-09-12、AI/IT/EV等15語)+`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-01 Phase B`(2026-09-25、"meta"追加) | `DEFAULT_JA_READING_DICTIONARY`(`er003_audio_tts_asr_safety.py:682-701`)。現在22語のみ、全て**手動individual追加**(ユーザー承認は得ているが、1語ずつのコードハードコード方式)。`classify_foreign_tokens_in_japanese_text()`(同ファイル:709-791)が`token.lower() in dictionary`(:772)で照合し、`reading`フィールドも返す(NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02 Phase 3b、:776-780) | 静的辞書のため実行時に変化しない。辞書に無ければ常にカテゴリ`HUMAN_REVIEW`(下記Gate参照)。retry/fallback経路(`generate_a2_japanese_with_fallback`等)も同じ`classify_foreign_tokens_in_japanese_text`を経由する入口(`generate_*_with_reading_safety`)を通ってから呼ばれるため、辞書の有無に関する挙動はstandard/fallback間で同一 |
| Foreign Token Gate(4分類+STOP判定) | `ER-009-JA-FOREIGN-TOKEN-GATE-01`(`CURRENT_SPEC.md`/`OPEN_ITEMS.md`各所) | `classify_foreign_tokens_in_japanese_text()`(`er003_audio_tts_asr_safety.py:709-791`)。分類順序: (1)制作内部ラベル`NEEDS_JAPANESE_PARAPHRASE`(:739-745)→(2)Key Phrase英語表現`ENGLISH_PRONUNCIATION`(known_key_phrase_termsが渡された場合のみ、:749-764)→(3)読み方辞書`READING_DICTIONARY`(:772-781)→(4)残りは`HUMAN_REVIEW`(:783-788)。`foreign_token_gate_requires_stop()`(:794-797)は**カテゴリ4が1件でもあればTTS呼び出し自体をブロック**。呼び出し元: `generate_charon_japanese_with_reading_safety()`(:326-339、B1)/`generate_a2_japanese_with_reading_safety()`(A2、同型) | HUMAN_REVIEW該当時は`log_foreign_token_human_review()`(:845-855、`er009_output/ja_foreign_token_gate_01/human_review_queue.jsonl`)へ記録した上で`STOPPED`を返し、**TTS呼び出し自体を行わない**(retry予算を消費しない)。辞書登録済みトークンの読み(`reading`)はASR照合(`classify_ja_asr_match`)まで素通し配線済み(`er003_v1_n3_01_tts_generate.py:344-349`、NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02 Phase 3b) |
| known_key_phrase_terms救済 | 同上 | その記事のKey Phrase英語表現(used_form)がテキスト中にそのまま含まれる箇所を「意図的な英語発話」として救済(:747-764)。渡さない呼び出しではこの救済は効かない | 呼び出し元が`known_key_phrase_terms`を渡すかどうかに依存(現状Key Phrase JA gloss生成経路等、渡している箇所は本調査では未確認、Phase 2でgrep推奨) |
| Reading Resolver(A2専用、漢字異読み解決) | `ER-011-NO18-CONNECTED-SPEECH-READING-RESOLVER-PRODUCTION-WIRING-08`(OPEN-111 `RESOLVED`) | `er011_a2_reading_resolver_01.py`。`resolve_reading_diff()`(:198-233)は、canonical/ASRの機械かな変換(pykakasi)が不一致の場合のみ、差分箇所の漢字1文字について**pykakasi内蔵辞書(kanwadict)由来の読み候補**をLLM(`call_resolver()`:122-152、JSON Schema enumで候補外を選択不可)に文脈選択させ、再比較する。`classify_ja_asr_match()`(`er007_ja_asr_validator_01.py:297-441`)内、通常のratio不一致時に発火(:438-441、`READING_RESOLVED_MATCH`) | **これは「未知の固有名詞の読みを新規に作る」機構ではない**。対象は「後」の「あと/のち」のような**辞書に複数候補が存在する既知の一般漢字**の文脈選択のみで、カタカナ外来語(Muse等)のような未登録固有名詞には無関係(pykakasi kanwadictは漢字専用、Latin文字トークンには候補が存在しない=`single_char_candidates()`:100-115が空リストを返し不発火)。fail-safe設計(候補が無ければ未解決のまま、LLMが候補外を返せば例外、全例外でresolved_match=False) |
| Web/公式情報検索(JA側での固有名詞読み解決専用) | なし(`NEW`、本調査で確認) | **存在しない**。Fact Checker(`er002_ja_web_research_r3.py`、`make_writer_research_fn`)はOpenAI web_searchツールを使うが、目的は事実検証(数値・因果関係等)であり、外来語の読み方確認には使われていない | 該当なし |
| cache/自動登録(JA読み専用) | なし(`NEW`、本調査で確認) | 存在しない。`DEFAULT_JA_READING_DICTIONARY`はコード内の静的dict(ファイル編集でのみ変更可能)であり、実行時に新語を追記するAPI(`upsert`相当)が無い | 該当なし |
| confidence判定(JA読み専用) | なし | 存在しない(辞書に「有る/無い」の二値のみ、中間的な確信度の概念が無い) | 該当なし |
| Human Review Lock | `ER-011-HUMAN-REVIEW-COST-GUARD-01` | `er011_human_review_lock_01.py`(`check_before_generation`:199-236、`record_outcome`:255、`approve_regenerate`:370-395)。`PRODUCTION_MAX_TTS_ATTEMPTS=3`(:80)、`REGENERATE_APPROVED`はユーザー明示操作でのみ設定(:34) | JA Foreign Token Gate自体は**この一つ手前でTTS呼び出しをブロックする**ため、Human Review Lockの3回attempt予算を消費せずに`STOPPED`へ到達する(Gateがブロックした場合、TTS/ASRの実行自体が発生しないため、Lockの`check_before_generation`にも到達しない設計) |

### 1.2 英語側(EN TTS: 固有名詞の英語発音)

| 機構 | 既存仕様(SSOT/REPORT) | Production初回pathの実装 | retry/fallback/regeneration時の挙動 |
|---|---|---|---|
| 固有名詞抽出 | `ER-006-PRONUNCIATION-LEDGER-SECONDARY-ASR-01` | `er006_proper_noun_extraction_01.py::extract_proper_nouns()`(:108-113)。LLM(Model Routing Contract経由、`PROPER_NOUN_EXTRACTION`)がarticle_text/support_text/key_phrases_textから「発音が音声合成・音声認識で問題になりうる固有名詞のみ」を抽出(JSON Schema厳格) | **この関数はProduction TTS生成経路(`er003_v1_n3_01_tts_generate.py`)から一度も呼び出されていない**(grep 0件、下記2.2節参照)。呼び出し元はTrial/testファイルのみ(`er006_pronunciation_ab_01_run.py`等) |
| Web/公式情報検索(発音調査) | 同上 | `er006_pronunciation_research_01.py::research_pronunciations()`(:92-140)。Perplexity API(`sonar`モデル)へ1 topicにつき1 requestでまとめて問い合わせ、IPA・pronunciation_hint(カタカナ的近似ではなく英語ローマ字近似表記)・confidence(high/medium/low)・sources/citationsを取得。プロンプトは一次情報源(本人音声・公式サイト)優先、confidence="high"は本人の実音声確認が条件と明記(:72-79、ER-008-N8-FINAL-PRODUCTION-HARDENING-23) | 同上、Production TTS生成の初回pathからは未呼び出し。**唯一の実呼び出し経路**は下記「reactive lookup」(1.2節後半) |
| cache(Pronunciation Ledger) | 同上 | `er006_pronunciation_ledger_01.py`。`LedgerKey(surface, entity_type, source_context)`→sha256 16文字ID(:28-33)。`lookup()`(:49-53、cache hit判定)/`upsert()`(:56-73、confidence/sources/updated_at等を保存)/`get_hint_for_text()`(:93-105、min_confidence以上のみ返す)。実データ23件が既に蓄積済み(`er006_output/pronunciation_ledger_01/ledger.json`、Ottoni/Malmö/Vancouver/MTA等、confidence high/medium/low混在) | cache自体は言語非依存の設計(surface文字列一致)だが、**書き込みが発生するのは下記reactive lookup経由のみ**(Production初回生成時の能動的research→upsertは未実施) |
| TTSへの発音ヒント注入(style_prefix拡張) | 同上 | `er006_pronunciation_tts_injection_01.py::augment_style_prefix_with_pronunciation()`(:31-43)。Ledger登録済み固有名詞がtext中にあれば、style_prefixへ"X is pronounced approximately Y"を追記(本文テキスト自体は変更しない設計制約を明記、:8-15) | **この関数は`er003_v1_n3_01_tts_generate.py`・`voice01`・`repro01`いずれからも呼び出されていない**(grep該当ファイルはtest/trial/audit監査ファイルのみ)。すなわちLedgerに発音ヒントが登録済みでも、TTS生成そのものへは**一切反映されない** |
| ASR Cascade用Phrase List(Secondary ASR、Azure) | 同上 | `er003_v1_repro01_main_generate.py:303`(`ledger_phrases = [h["canonical_spelling"] for h in pronun_ledger.get_hint_for_text(text, min_confidence="low")]`)。`secondary_asr.evaluate_attempt_with_cascade(..., ledger_phrases=ledger_phrases, ...)`(:304-308)。静的監査`er006_audio_cost_spec_fix_01_static_audit.py::check_pronunciation_route_not_ignored()`(:171-199)がこの引数の存在を回帰的に保証 | Ledger登録済み語の**ASR認識精度**(Azure Secondary ASR向けPhrase List)には効くが、**TTS側の発音そのもの**には無関係(ASRが正しく聞き取れるようヒントを与えるだけで、TTSが誤発音していた場合はこの機構では救えない) |
| Reactive lookup(Human Review直前のcache/research、TTS再生成には使わない) | 同上 | `er006_secondary_asr_01.py`(:219-248、関数名は本調査では未特定だが呼び出し順序から`_lookup_or_research_pronunciation`相当)。ASR Cascade(Primary#1/#2、Secondary#1/#2)を尽くしても解決できなかった場合のみ、`pronun_ledger.lookup()`→cache miss時`pronun_research.research_pronunciations()`を1回呼び`upsert()`する(:227-248) | **明示的に「Human Reviewパッケージを充実させるためだけに使う」とコメントされている**(:221-226)。「IPA→ARPAbet変換等による自動PASSの根拠には一切使わない」「lookup/research失敗時はNoneを返し、追加のTTS呼び出しを一切行わずHuman Reviewへ進むこと」。すなわち**この情報を使ってTTSを再生成し直す経路が存在しない**(発音情報を得ても、それをTTS styleへフィードバックしてretryする配線が無い) |
| 内部ラベル検出(制作用語の露出防止、発音ではない) | `ER-008-N8-QA-CONTENT-SPEED-HARDENING-18` | `detect_internal_production_labels_in_english_text()`(`er003_audio_tts_asr_safety.py:821-835`)+`english_internal_label_gate_requires_stop()`(:838-842)。1件でも検出で無条件ブロック(日本語版のような救済分類なし) | 固有名詞の発音とは別目的(Part 1等の内部ラベル露出防止) |
| 短い孤立語の非決定的誤発音(恒久課題) | `OPEN-103`(`DEFERRED / NON-BLOCKING`、2026-09-02) | 対象外(TTSモデル自体の非決定性、Gemini TTSが短い孤立語"default"を試行ごとに異なる誤発音をする問題。修正コードなし、one-off固定assetで個別記事を回避) | ASR側再判定では救えない(TTSが実際に誤発話したケース)ため、固有名詞発音の一般解決とは別軸の既知の限界として記録されている |
| 人名英語表記の本文綴り事前確認(OPEN-146、発音ではなく綴りだが設計思想が酷似) | `OPEN-146`(`PRODUCTION_WIRED`、2026-09-13格上げ) | `er011_open146_ledger_canonical_en_spelling_production_01.py`。Verified Fact Ledgerへ`canonical_en_spelling: <日本語表記> = <English>`行を追加、Web検索(`r3.make_writer_research_fn()`、既存Production関数を無改変で再利用)で公式表記を確認、Writerへ1文追記(:86-102)、Fact Checkerへ照合ブロックを追加(:109-126)。**「一つの語を手で直す」ではなく、汎用抽出→web確認→Ledger→Writer→検証という一般パイプライン**として実装済み | 既存Gate順序・retry予算は無変更のまま、Ledger本文への1文追記のみで既存`build_common_block()`の出力をbyte不変に保つ設計(canonical_en_spelling行が無い記事では完全no-op) |

### 1.3 両側に共通する基盤

| 機構 | 内容 |
|---|---|
| Human Review Lock(`er011_human_review_lock_01.py`) | JA/EN共通。`PRODUCTION_MAX_TTS_ATTEMPTS=3`、`REGENERATE_APPROVED`はユーザー明示操作でのみ設定(:34, 80, 370-395)。JA Foreign Token GateはTTS呼び出し自体をこの手前でブロックするため、Lockの3回予算を消費しない(1.1節)。EN側はASR Cascadeの4段(Primary#1/#2、Secondary#1/#2)を経てなおHUMAN_REVIEWへ進む場合、Lockの通常フローに乗る |
| Master Audio Store(`er006_master_audio_store_01.py`) | 完全固定segment・B1/A2完全一致Key Phraseのみ対象の音声レベル再利用cache(:1-76)。読み情報のcacheとは別レイヤー(音声ファイル自体の再利用) |
| TTS Symbol Normalization Gate(`er003_audio_tts_asr_safety.py` G節、:858-1055) | 別タスク(`TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01`)で新設・並走中、記号(〜/…/括弧等)の正規化・検出が対象。固有名詞の読み解決とは別レイヤーだが、**同じ2関数(`generate_charon_japanese_with_reading_safety`/`generate_a2_japanese_with_reading_safety`)内で、Foreign Token Gateの直前に呼ばれる**(:312-325→326-339の順序、コード確認済み)。本タスクはこのGate自体には触れない(担当外) |

### 1.4 Family別の現状(Active Production Family = X/Z、Legacy = A/B/C)

| Family | JA TTS経路 | EN TTS経路 | 備考 |
|---|---|---|---|
| Family A(legacy、read-only参照元) | `generate_*_with_reading_safety()`(`er003_v1_n3_01_tts_generate.py`)を直接使用 | `voice01.generate_charon_english`/`news_tail_fix.generate_news_narration_wide_margin`等、同モジュール内 | 本タスクではA自体を変更しない(共有module変更がA/B/Cにも及ぶ場合はその旨明記、3.6節) |
| Family X(Active、開発中心) | 同上(`er019_family_x_audio_production_runner_01.py`が`er003_v1_n3_01_tts_generate.py`をimportして共有、`docs/pm/recon_tts_symbol_normalization_01.md`1.2節で確認済み。本タスクでも同モジュールへのgrepで直接呼び出しは0件、共有関数経由のみ) | 同上 | japanese_title等の生成元は`er019_family_x_ja_writer_o_r1_r2_01.py`(別モジュール)だが、**音声化の入口は共有の2関数**であるため、共通resolverをそこへ実装すればFamily Xへ自動的に及ぶ |
| Family B(Editorial Voices、legacy) | **存在しない**(`docs/pm/recon_tts_symbol_normalization_01.md`1.4節で確認済み、日本語segmentなし) | `bvoices`経由で`voice01`/`repro01`利用 | 本タスクのJA側設計はFamily Bには適用対象が無い(EN側設計は適用対象になりうる) |
| Family C(Future Story、legacy) | 1.4節に準ずる可能性が高い(未確認箇所あり) | 同上 | 本タスクではCを変更しない |
| Family Z(Fiction、Active/未実装) | 未実装 | 未実装 | `CURRENT_SPEC.md`「Family Z」節「Production配線自体は未実装」。将来の適用点としてのみ設計に含める(3.6節) |

---

## 2. 不足の明確化(作業2)

### 2.1 日本語側: できていること/できていないこと

**できていること**:
- 既知の22語(略語+"meta")については、Gateが正しく`READING_DICTIONARY`に分類し、読みをASR照合まで素通し配線済み(1.1節)。
- HUMAN_REVIEW該当時にTTS呼び出し自体をブロックし、無駄なAPI課金を発生させない安全設計(fail-safe側に倒れている)。
- 漢字の文脈依存異読み(「後」のあと/のち等)は、既存のReading Resolverが辞書候補+LLM文脈選択で解決済み(ただし対象は漢字限定、外来語Latin表記には無関係)。

**できていないこと(ユーザーが指摘した既知問題そのもの)**:
- **辞書登録の手段が「コードへの手動個別追加」のみ**。ユーザー承認は得ているが(ER-009・NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-01 Phase B)、いずれも「特定の1〜15語が出てきたので追加する」という**個別事後対応**であり、汎用パイプライン(未知語検出→web確認→自動登録)が存在しない。これがMuse 1件の手登録という、ユーザーが今回明示的に禁止した対応パターンそのものである(TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01_REPORT.md §5・§8で実例確認済み)。
- **web/公式情報検索によるJA読み解決機構が存在しない**。EN側のPronunciation Ledger+Perplexity researchに相当するJA版が無い(1.1節)。
- **confidence判定が二値(辞書に有る/無い)のみ**。中間的な確信度(複数ソース一致/単一ソース/不一致)の概念が無い。
- **未知語→即HUMAN_REVIEW**という、ユーザーが「禁止」と明言した状態が実際に発生している(Muse実例、`er009_output/ja_foreign_token_gate_01/human_review_queue.jsonl`2026-09-27エントリで確認済み。本調査中に実データを直接読み実在を確認した)。

### 2.2 英語側: できていること/できていないこと

**できていること**:
- 固有名詞抽出→Perplexity web研究→confidence判定→Ledger cache保存、という**パイプライン自体は実装済み**(1.2節、コードとして動く状態にある)。
- Ledger登録済み語はSecondary ASR(Azure)のPhrase Listとして活用され、**ASR側の認識精度**には貢献している。
- OPEN-146(人名の英語綴り)で、同種の思想(抽出→web確認→Ledgerへ保存→Writer/Checkerへ伝達)が**既にProduction配線・実発火まで完了している**実例が存在する(1.2節末尾)。これは「発音」ではなく「綴り」だが、汎用フローの実証済みテンプレートとして極めて有用。

**できていないこと(ユーザーが要求した「英語側にも同種の穴があるか」の答え)**:
- **TTS生成の初回pathが、固有名詞抽出・Perplexity research・style_prefix発音ヒント注入のいずれも一度も呼び出さない**(1.2節、grep 0件で確認)。すなわちEN側は実質**「TTSモデル任せ」のみ**で、ユーザーが例示した「一般的英語名/地名はモデル任せ+ASR照合で十分か」という前提を満たしていない可能性がある: モデル任せにした結果、TTSが誤発音してもASRが偶然一致する(false accept)、あるいは正しく発音してもASRが誤認識する(false reject)のどちらかが起き得るが、**発音そのものを確認・保証する機構が生成前に一切働いていない**。
- Ledger/research機構が実際に発火するのは「ASR Cascadeを4段すべて使い切ってなおHUMAN_REVIEWへ進む寸前」の1回のみであり、しかも**得られた発音情報をTTSの再生成に使う配線が無い**(コメントで明示的に「自動PASSの根拠には使わない」「追加のTTS呼び出しを一切行わない」とされている、1.2節reactive lookup行)。つまり現状は「発音を解決してから正しく読ませる」ではなく「発音を解決してもHuman Reviewパッケージの参考情報にするだけ」という設計であり、ユーザーが要求する「confidence十分なら当該runで自動使用」には未到達。
- **OPEN-103(短い孤立語の非決定的誤発音)が示す通り、TTS自体が誤発話した場合はASR側の対策では原理的に救えない**。これはJA側のMuse問題(未知語→即HUMAN_REVIEW)とは異なる失敗モードだが、「発音の正しさを生成前に担保する機構が無い」という根っこは共通する。
- 逆方向(false reject: TTSは正しいがASRが誤認識)は、Ledger Phrase List(Secondary ASR向け)・非ラテン文字支配判定(`KEYPHRASE-EN-ASR-FALSE-REJECTION-CASCADE-PROD-WIRING-01`)・Connected Speech Validator等、**複数の既存対策で相当程度カバーされている**(OPEN-107/110/119関連)。

### 2.3 JA/EN非対称性の整理(ユーザーへの直接回答)

| 観点 | JA側 | EN側 |
|---|---|---|
| 既知語の扱い | 静的dict、手動個別追加(禁止パターン) | 動的Ledger、web研究で自動登録可能な設計はある |
| 未知語→web確認の自動化 | **無い(gap)** | **コードはあるが未配線(gap)** |
| TTS生成前の発音ヒント供給 | 辞書ヒットのみ(読みをTTS入力へ反映する経路は無いが、Gate通過可否のみに使われる。TTS自体は元テキストをそのままGeminiへ渡し、モデルが読み方を推測する点はEN側と実は同じ) | 存在するが呼ばれていない(`augment_style_prefix_with_pronunciation`) |
| ASR側の後押し | 素通し配線済み(expected_readings) | Phrase List(Secondary ASRのみ、Primary OpenAIには非対応) |
| 未解決時の挙動 | 即HUMAN_REVIEW(TTS呼び出し自体をしない、安全だが「解決努力ゼロ」) | 4段Cascade+reactive research(解決努力はあるが「Human Review向けの参考情報止まり」) |
| **共通する根本ギャップ** | **「confidence十分なら当該runで自動使用」という、ユーザーが要求する核心のステップが、JA・EN双方とも実装されていない**(JAは分岐自体が無い、ENは分岐はあるが「参考情報止まり」でTTSへフィードバックしない) | 同左 |

---

## 3. 設計(作業3)

### 3.1 共通コアの配置先モジュール案

**事実整理**: 現状、JA側(Foreign Token Gate)とEN側(Pronunciation Ledger)は、
別モジュール(`er003_audio_tts_asr_safety.py` vs `er006_pronunciation_ledger_01.py`
+関連3ファイル)に、別のデータ構造(静的dict vs JSON cache)・別の識別key
(小文字トークン文字列 vs `LedgerKey(surface, entity_type, source_context)`の
sha256)で実装されている。共通化にあたっては、**言語非依存の「解決パイプライン
+confidence判定+store I/F」を1つの新規coreモジュールへ切り出し、JA/EN
それぞれの既存Gate/Ledgerをこのcoreの薄いラッパーとして再実装する**案を推奨
する(以下は提案、未実装)。

**提案**: 新規モジュール `er0XX_entity_pronunciation_resolver_core_01.py`
(Phase 2で番号確定)を新設し、以下を持たせる:
- `EntityKey`(surface, entity_type, target_language["ja"|"en"], source_context)
  ※現行`LedgerKey`(EN専用)と`DEFAULT_JA_READING_DICTIONARY`のkeyを統合した
  上位互換の識別子。
- `unified_lookup(key) -> Optional[dict]`: 既存`pronun_ledger.lookup()`と
  `DEFAULT_JA_READING_DICTIONARY`照合を、同じ戻り値schema(下記3.4節)で
  ラップする。
- `unified_resolve(surface, entity_type, target_language, context) -> dict`:
  cache miss時のみ、言語別resolver(3.2/3.3節)を呼び出し、confidence判定後
  upsertする。
- `confidence_gate(entry) -> "AUTO_USE" | "ASR_BACKED" | "HUMAN_REVIEW"`
  (3.4節のconfidence基準を実装)。

新規モジュールが必要な理由: (1) JA/ENで既存の識別key・store形式が異なり、
どちらか一方に無理に統合すると既存呼び出し元(`classify_foreign_tokens_in_
japanese_text`の`token.lower() in dictionary`直接比較、`pronun_ledger.
get_hint_for_text`のsurface文字列一致)の契約を壊すリスクがある。(2) 既存
2機構(Gate/Ledger)は「TTS呼び出し可否の判定」という薄い責務のまま維持し、
「resolve+confidence+store」という重い責務だけを新規coreへ分離すること
で、既存のテスト・回帰保証(`er009_ja_foreign_token_gate_01_test_01.py`
17件、`er006_pronunciation_ledger_01_test.py`等)への影響を最小化できる。

既存2機構は**廃止せず、coreの薄いクライアントとして残す**(Gate 4 Dangling
Reference Check観点: 新規coreは既存の`er003_audio_tts_asr_safety.py`/
`er006_pronunciation_ledger_01.py`をimportする側に置き、逆方向の依存
[安全モジュールが新規coreに依存する形]は作らない)。

### 3.2 JA resolver設計(提案)

```
未知のLatin/外来語トークン検出(既存classify_foreign_tokens_in_japanese_
textのHUMAN_REVIEW分岐がトリガー)
  -> 1) DEFAULT_JA_READING_DICTIONARY照合(既存、無変更)
  -> 2) 新規: unified coreのcache照合(surface一致、JA側で過去に解決済みか)
  -> 3) 新規: 「この語の既存英語発音情報(EN Pronunciation Ledgerの
       expected_pronunciation_ipa/pronunciation_hint)が既にあれば、それを
       文脈として与えた上でLLMに『日本のメディア・カタカナ表記慣行での
       一般的な読み』を尋ねる」(EN Ledgerとの相互参照、二重research回避)
  -> 4) 新規: web lookup(既存r3.make_writer_research_fn、OPEN-146と同一
       関数を再利用。プロンプトのみJA読み確認用に変更)。信頼ソース順位案:
       (a) 当該固有名詞の公式サイト日本語版・日本法人プレスリリース
       (b) 日本語版Wikipedia
       (c) 主要日本語報道(共同/時事/NHK等の表記)
       (d) 上記が無い場合のみ、英語IPA/pronunciation_hintからの機械的
           カタカナ近似(低confidence)
  -> 5) confidence判定(3.4節)
  -> 6) 高confidenceなら読みをDEFAULT_JA_READING_DICTIONARY相当の
       reading_dictionary引数へその場で追加し、当該runで自動使用
  -> 7) unified coreへ保存(次回以降はcache hit)
  -> 8) 中/低confidenceならASR照合(既存classify_ja_asr_match)で裏付け、
       それでも不一致ならHUMAN_REVIEW(既存Gateの安全側動作を維持)
```

カタカナ読みの正規化: 既存`er011_a2_reading_resolver_01.py`の
`normalize_kana_for_compare()`(カタカナ→ひらがな統一、句読点除去)を
比較用に再利用できる(新規実装不要)。

### 3.3 EN resolver設計(提案)

現行TTS任せで許容できる範囲の定義(提案、Fable/ユーザー確認推奨):
- 広く知られ発音に曖昧さがない一般的固有名詞(例: "United States"、
  "New York"、既存`er006_proper_noun_extraction_01.py`のPrompt自体が
  この基準を既に持っている、:56-58)はモデル任せ+ASR照合で許容。
- それ以外(非英語圏人名、ブランド名、非自明な略語[頭字語読みか単語読みか
  不明なもの])は、**既存の抽出→research→Ledger機構を「初回TTS生成前」に
  実際に呼び出す**よう配線する(現状は1.2節の通りreactive限定)。

```
記事Writer完成後(既存extract_proper_nouns()の入力タイミングと同じ)
  -> 1) extract_proper_nouns()(既存、無変更、Trial/testでのみ動作確認済み)
  -> 2) 各entityについてunified coreのcache照合(pronun_ledger.lookup()を
       ラップ)
  -> 3) cache missのみresearch_pronunciations()(既存、無変更、Perplexity
       1 topic 1 request)
  -> 4) confidence判定(3.4節)
  -> 5) 高confidenceならaugment_style_prefix_with_pronunciation()(既存、
       無変更だが**初めてTTS生成前に実配線**)でstyle_prefixへ発音ヒント
       注入。本文テキスト自体・visible scriptは変更しない(既存制約を維持)
  -> 6) unified coreへ保存(既存upsert())
  -> 7) TTS実行 -> ASR照合(既存classify_asr_match、変更なし)
  -> 8) 中/低confidence、またはASR不一致が続く場合のみ、既存4段Cascade
       (Primary#1/#2、Secondary#1/#2、Ledger Phrase List供給は既存のまま)
       -> それでも解決しなければHUMAN_REVIEW(既存、無変更)
```

Gemini TTSでの発音指定方法(事実確認、Phase 2着手前に公式doc HTTP GET
逐語引用が必要): 本Phase 1では未確認(API費用¥0方針のためHTTP取得は
実施していない)。現行実装(`augment_style_prefix_with_pronunciation`)は
style instructionへの自然文注記("X is pronounced approximately Y")という
非構造化な方法のみで、IPA直接指定やSSML的な発音タグのサポート有無は
未調査。Phase 2で `https://ai.google.dev/gemini-api/docs/speech-generation`
等の公式docを確認し、逐語引用のうえ設計へ反映することを推奨する。

OPEN-103(短い孤立語の非決定的誤発音)との関係: 本設計は「発音情報を
生成前に与える」対策であり、OPEN-103のような**TTSモデル自体の非決定性
(同じ入力でも試行ごとに結果が変わる)**を完全には解消しない可能性がある
(発音ヒントを与えても尚non-deterministicな挙動が残るかは実証が必要)。
Phase 2のfixtureで"default"のような既知の問題語を含めて実測することを
推奨する(3.8節)。

### 3.4 Store設計(既存Pronunciation Ledgerのスキーマ拡張案)

現行`er006_pronunciation_ledger_01.py`のentry(1.2節)を、JA/EN両対応へ
拡張する案(既存フィールドは全て維持、後方互換):

```
{
  "surface": ..., "entity_type": ..., "source_context": ...,   # 既存
  "canonical_spelling": ..., "language_origin": ...,            # 既存
  "expected_pronunciation_ipa": ..., "pronunciation_hint": ...,  # 既存(EN発音)
  "alternate_pronunciations": [...], "confidence": ...,          # 既存
  "ambiguity_note": ..., "sources": [...], "updated_at": ...,    # 既存
  # 以下、新規提案フィールド(既定値で後方互換)
  "ja_reading_katakana": "",       # 新規: 日本語カタカナ読み(空文字=JA解決未実施)
  "ja_reading_confidence": "",     # 新規: JA読みのconfidence(EN側confidenceと独立)
  "ja_reading_sources": [],        # 新規: JA読み確認に使ったURL一覧
  "resolution_method": "",         # 新規: "official_site"|"web_search"|
                                    #   "reactive_human_review_enrichment"|"manual"
  "resolved_at_stage": "",         # 新規: "pre_tts"|"post_cascade_reactive"|"manual_dict"
}
```

cache hitの優先順位: (1) 完全一致(surface小文字+entity_type一致)、
(2) 表記ゆれ正規化後一致(全角/半角、ハイフン有無等、既存`_LATIN_TOKEN_RE`
の正規化ルールと整合させる)。再利用の単位: 現行`LedgerKey`はsurface文字列
の大文字小文字を区別しない(`.strip().lower()`、`er006_pronunciation_
ledger_01.py:30`)が、`entity_type`が異なれば別entryになる設計(同一綴りで
人名/地名が異なる読みを持つケースに対応、既存設計を維持)。

### 3.5 retry/fallback/regeneration等での読み情報維持の配線点

| 経路 | 現状 | 配線点(提案) |
|---|---|---|
| JA standard→fallback(`generate_a2_japanese_with_fallback`、`er003_v1_n3_01_tts_generate.py:404-502`) | `expected_readings`引数で既に読み辞書登録語の読みをstandard/fallback両方へ素通し(:408, 430-432, 458) | 新規resolverが解決した読みも同じ`expected_readings`辞書へマージするだけでよい(既存の素通し配線をそのまま再利用、新規配線コード不要) |
| EN standard→fallback(`generate_key_phrase_component_verified`等) | `ledger_phrases`はASR Cascadeへのみ渡る(1.2節) | `augment_style_prefix_with_pronunciation()`の呼び出しをstandard経路の入口に追加すれば、fallback経路も同じtext/style_prefix生成関数を通る限り自動的に恩恵を受ける(要Phase 2でのコードパス確認) |
| Local Rewrite | 未確認(Phase 2でgrep推奨) | article_text書き換え後、固有名詞抽出をLocal Rewrite後のテキストに対して再実行する必要があるか(語が消える/変わるケース)を要確認 |
| Key Phrase再正規化(`er003_key_words_canonicalization.py`) | 未確認 | `convert_display_gloss_to_tts_text`の前後でresolverを挟む場合、Key Phrase専用の`known_key_phrase_terms`救済(1.1節)との重複判定順序を要設計(Key Phrase英語表現自体は「意図的な英語発話」なので、そもそも読み解決の対象外になる可能性が高い) |
| REGENERATE_APPROVED再生成 | Human Review Lock通過後の再生成は既存Production関数をそのまま呼ぶのみ(ER-009 REPORT §8-1で実証済み) | resolverが新規coreモジュール内の関数呼び出しである限り、既存`generate_*_with_reading_safety`/`generate_*_with_fallback`経由で自動的に及ぶ(新規Lock/新規retry予算は追加しない、既存に相乗り) |

### 3.6 Family X/Z(Active)への配線点、Family A/B/C非変更方針

- **Family X**: 共有TTS入口(`er003_v1_n3_01_tts_generate.py`の
  `generate_charon_japanese_with_reading_safety`/`generate_a2_japanese_with_
  reading_safety`、EN側`voice01`/`repro01`)へcoreを配線すれば、Family Xの
  japanese_title/comment/KP経路すべてに自動的に及ぶ(1.4節、Family Xは
  この共有モジュールをimportするのみで固有のTTS関数を持たない)。
- **Family Z**: 未実装のため、Writer/音声経路が新設される際に、設計時点
  から本resolverを組み込む前提を`CURRENT_SPEC.md`「Family Z」節へ明記する
  ことを推奨(本Phaseでは記述のみ、SSOT編集はFableに委ねる)。
- **Family A/B/C(legacy)**: 上記共有モジュール(`er003_audio_tts_asr_
  safety.py`/`er006_pronunciation_ledger_01.py`/`er003_v1_n3_01_tts_
  generate.py`)はFamily A/Xで共用されているため、**共有層への変更は
  結果的にFamily A(および1.4節の通りFamily Bを除くB/Cの可能性がある経路)
  にも影響する**。ただしこれは「共有moduleの拡張」であり、A/B/C固有の
  コード(`er012_b_family_voices_production_01.py`本体、`er013_family_c_
  *`本体等)は一切変更しない。挙動面では、A/B/Cも新規resolverの恩恵(既知語
  なら自動使用、未知語ならHuman Review)を自動的に受けることになるが、
  これはregressionではなく「安全側の機構が既存の安全側の機構を置き換える」
  形であり、既存のGate/Lock自体を緩めるものではない。

### 3.7 QCD設計

- **Web lookupは未知語かつcache missのときのみ**発火する(既存`research_
  pronunciations()`/`run_canonical_spelling_research()`双方とも、entities
  が空なら呼び出し自体をスキップする設計が既にある、`er011_open146_*:281-283`
  と同型で新規JA resolverも設計すべき)。
- **run内重複解決なし**: 同一記事内で同じsurfaceが複数segment(title/
  comment/KP等)に登場する場合、1 run内でのin-memory cache(dict)を経由し、
  2回目以降はunified coreのlookup()すら呼ばずメモリ内で解決する設計を
  推奨(API呼び出し回数=記事内のユニーク未知語数のみ)。
- **1記事あたりの上限回数**: 既存`ER-006-PRONUNCIATION-LEDGER-SECONDARY-
  ASR-01`は「1 topicにつき1 request」設計(全entities まとめて1回)。
  JA側も同型(1記事の未知語をまとめて1回のresearch呼び出し)を推奨。
- **latency見積**: Perplexity `sonar`モデルの実測値は本Phase未取得(Phase 2
  実行時に`elapsed_seconds`フィールドから取得可能、既存コードに計測済み)。
- **費用見積**: 既存単価は`er005_output/cost_baseline_01/pricing_snapshot.json`
  (OFFICIAL_SOURCE)参照。Perplexity `sonar`の単価は本Phase未確認(Phase 2で
  `raw_usage_log.jsonl`実測を推奨、過去実行実績が`er005_cost_logger.py`
  経由で記録されているはずのため、Phase 2冒頭でcost_logger該当行を grep
  すれば¥0で概算できる)。JA側web lookup(既存`r3.make_writer_research_fn`
  再利用)はOPEN-146実測で¥100〜200/記事(人名綴り確認、複数entity)という
  実績があり、発音確認も同程度の規模になる可能性が高い(仮説、Phase 2で
  実測要)。

### 3.8 Fixture/runtime evidence計画

| 対象 | fixture | 確認項目 |
|---|---|---|
| JA既知gap再現 | Meta A2 japanese_title「Muse」(実データ、`er019_output/family_x_audio_production_wiring_01/family_x_b3_production_wiring_01__run_01/a2/`) | (1)未登録語検出(2)web lookup発火(3)confidence判定(4)高confidenceなら自動使用・TTS成功(5)coreへ保存(6)2回目実行でcache hitし追加API呼び出しなし |
| JA別の未登録語 | 実記事コーパスに他の実例が無いことを確認済み(`er009_output/ja_foreign_token_gate_01/human_review_queue.jsonl`実データ、"Gloobargaxxx"はtest fixtureのみで実記事実例ではない)。**合成fixtureが必要**(例: 未登録の架空/実在するが辞書未登録の企業名を1件、既存記事の日本語説明文へ機械的に挿入したテスト専用テキスト) | 同上6項目 |
| EN固有名詞・略語 | 既存Pronunciation Ledger実データ23件のうち、confidence="low"かつentity_type="cascade_unresolved_entity"(reactive lookup由来、例: ganis/zabelina/lindberg/toteme/kallmeyer)を含む既存segmentを選定 | (1)pre_tts配線後、これらの語が実際に不明なままだった記事で、resolverがTTS生成前に解決を試みるか(2)confidence判定でreactiveより高いconfidenceに改善されるか(3)style_prefix注入がTTS発音を実際に変えるか(ASRだけでなく人間試聴での確認が望ましいが、本Phaseでは機械的な発音一致確認[ASR再照合]に留める) |
| 受入条件 | 1) 既知語(辞書/Ledger登録済み)は追加API呼び出しなしで即PASS 2) 未知語かつ高confidence解決可能な語は1回のweb lookupで自動使用・TTS成功 3) 未知語かつ低confidenceはASR照合で裏付けを試みる 4) 裏付けも失敗した場合のみHUMAN_REVIEW 5) 解決結果はcoreへ保存され同一記事内・別記事で再利用される 6) 既存retry予算(3回)・既存Lock機構を独自に緩めない 7) 既存Gate(Symbol Normalization等)との実行順序が壊れない 8) Family A/B/Cの既存テスト回帰にfailが出ない 9) 費用が既存予算内(¥250上限目安) 10) Web lookup失敗時はfail-safe(現状のHUMAN_REVIEWへ、既存Reading ResolverのfE-safe設計を踏襲) | 上記10項目をPhase 2のGate 3チェックリストへ転記予定 |

### 3.9 USER_DECISION_REQUIRED候補(該当するもののみ)

1. **永続化方法の設計選択**: 3.1節のcore新設案(JA/EN統合ラッパー)か、
   既存2機構(Gate辞書/Ledger)をそれぞれ別々に拡張する案か。前者は将来の
   保守性が高いが新規モジュール追加を伴う。後者はBlast Radiusが小さいが
   JA/EN間の再利用性が下がる。→ **ユーザー判断候補**(Fable推奨: 前者。
   ただしPhase 2着手前にFableの設計判断で足りる程度の粒度であり、必ずしも
   ユーザーまで上げる必要はない可能性がある)。
2. **有料外部サービスの追加利用**: JA側web lookupに既存`r3.make_writer_
   research_fn`(OpenAI web_searchツール、OPEN-146と同一)を使うか、EN側と
   同じPerplexity APIをJAでも使うか(Perplexityの日本語ソース検索精度は
   本Phase未検証)。→ **ユーザー判断候補**(コスト構造・精度のトレードオフ、
   Phase 2で小規模比較Trialを先に行うことを推奨する案もあり)。
3. **信頼できる読み複数で自動選択基準不能な場合の扱い**: 3.2節のconfidence
   基準(複数ソース一致=高)は本Phaseの設計提案であり、実際の閾値(例:
   「2ソース一致で高」か「3ソース」か)はユーザー確認が望ましい。

上記以外(通常の技術実装判断、モジュール分割・関数命名・既存コードとの
統合順序等)はFableへの通常報告に留め、ユーザーへは上げない。

### 3.10 Phase 2実装計画

- **変更ファイル一覧(見込み)**:
  - 新規: `er0XX_entity_pronunciation_resolver_core_01.py`(3.1節)
  - 拡張: `er006_pronunciation_ledger_01.py`(スキーマ拡張、3.4節、既存
    フィールドは無変更のため後方互換)
  - 拡張: `er003_audio_tts_asr_safety.py`(`classify_foreign_tokens_in_
    japanese_text`のHUMAN_REVIEW分岐前に、新規coreへの照会を追加する形の
    最小変更を想定。既存関数シグネチャ・戻り値schemaは維持)
  - 拡張: `er003_v1_n3_01_tts_generate.py`(`generate_charon_japanese_with_
    reading_safety`/`generate_a2_japanese_with_reading_safety`/EN側生成
    関数への新規core呼び出し追加)
  - 拡張: `er006_pronunciation_tts_injection_01.py`の呼び出し配線(EN側
    style_prefix注入を実際にProduction経路へ接続)
  - 新規: Phase 2用テストファイル群(既存`er009_ja_foreign_token_gate_01_
    test_01.py`/`er006_pronunciation_ledger_01_test.py`/`er006_
    pronunciation_tts_injection_01_test.py`への追加分含む)
- **影響範囲**: Family A/X(JA/EN共有TTS入口経由)。Family Bは英語側のみ
  影響。Family C/Zは1.4節の通り。
- **Gate 3チェックリスト充足計画**: 3.8節の受入条件10項目をそのまま転記、
  実データ(Muse実例+新規合成fixture+EN既存low-confidence実例)でのruntime
  evidence取得を必須とする。
- **費用見積**: Perplexity/OpenAI web_search実測(3.7節)+fixture実行分
  (既存の同種タスク実績[TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-
  WIRING-01実測¥5.93]から類推し、¥10〜30程度を見込む。ただしPhase 2委任文
  で正式な上限をFableが設定することを推奨)。

---

## 証跡パス一覧(本Phase 1で参照した実データ)

- `er003_audio_tts_asr_safety.py`(既存Production、無変更)
- `er003_v1_n3_01_tts_generate.py`(既存Production、無変更)
- `er006_pronunciation_ledger_01.py`/`er006_pronunciation_research_01.py`/
  `er006_pronunciation_tts_injection_01.py`/`er006_proper_noun_extraction_
  01.py`/`er006_secondary_asr_01.py`(既存Production、無変更)
- `er006_output/pronunciation_ledger_01/ledger.json`(実データ、既存23件、
  読み取りのみ)
- `er009_output/ja_foreign_token_gate_01/human_review_queue.jsonl`(実データ、
  Muse実例含む、読み取りのみ)
- `er011_a2_reading_resolver_01.py`(既存Production、無変更)
- `er011_open146_ledger_canonical_en_spelling_production_01.py`(既存
  Production、無変更)
- `ER-009-JA-READING-DICTIONARY-ACRONYM-EXPANSION-AND-TREND-A2-RESUME-01_
  REPORT.md`(既存REPORT、読み取りのみ)
- `TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01_REPORT.md`
  §5/§9(既存REPORT、読み取りのみ)
- `OPEN_ITEMS.md`(OPEN-103/OPEN-146該当行、読み取りのみ)
- `docs/pm/recon_tts_symbol_normalization_01.md`(既存recon、読み取りのみ)

本Phase 1でのProduction code/Prompt/SSOT変更: **なし**。API呼び出し: **なし
(¥0)**。

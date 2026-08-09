# CURRENT_SPEC — 現在有効な正式仕様

**管理ID: ER-PM-001**
**最終更新: 2026-08-09**

このファイルには、**現在正式に採用されている仕様だけ**を書く。経緯・
比較検討・却下案は書かない(→[DECISION_LOG.md](DECISION_LOG.md)/
[HISTORY_INDEX.md](HISTORY_INDEX.md))。未確定事項は書かない
(→[OPEN_ITEMS.md](OPEN_ITEMS.md))。

各項目は最低限、**管理ID／現在値／状態／根拠Decision／最終更新日**を持つ。

---

## Product(番組仕様)

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| サービス名 | English Your Way | `DECIDED` | ER-003-B1-P9A系 | 2026-08-07 |
| 対象ユーザー | 日本語話者の英語学習者(リスニング中心) | `DECIDED` | ER-003-B1系 | 2026-08-07 |
| 番組構成(19パート) | Intro→Welcome→Topic Intro→Japanese Title→notification1→Preview Intro→Point解説→Preview→notification2→Key Phrases Intro→Key Phrase×5→notification3→Full Story Intro→Full Story→Outro | `DECIDED` | ER-003-REPRO-01/02(A02・ADD03で再現確認済み) | 2026-08-09 |
| Key Phrasesセクション構成 | 番号→英語→日本語訳→英語(反復) | `DECIDED` | ER-003-B1-P9A系 | 2026-08-07 |

## CEFR(A2 / B1 / B2 比較)

| 項目 | CEFR-A2 | CEFR-B1 | CEFR-B2 |
|---|---|---|---|
| status | `TBD` | `DECIDED` | `DECIDED`(テキストのみ。音声化は[OPEN_ITEMS](OPEN_ITEMS.md)参照) |
| vocabulary | `TBD` | 定性的指示のみ("mostly common, everyday vocabulary... a B1 learner already knows")、wordlist参照コードなし | 定性的指示のみ("主に一般的なB2以下の語彙")、wordlist参照コードなし |
| 平均文長 | `TBD` | ≤15語(`B1_TARGET_AVG_WORDS_PER_SENTENCE`、**診断のみ、gateではない**) | ≤19語(`B2_MAX_AVG_WORDS_PER_SENTENCE`、**実際のgate**) |
| 最長文 | `TBD` | 24語(`B1_MAX_SENTENCE_WORD_COUNT`、診断のみ) | 32語(`B2_MAX_SENTENCE_WORD_COUNT`、実際のgate) |
| 全体語数 | `TBD` | 上限なし(明示的にhard limitを設けない設計) | 上限なし(記録のみ、gateなし) |
| 1文1アイデア | `TBD` | 定性的指示あり("Prefer one idea per sentence") | 規定なし |
| 等位接続・従属節 | `TBD` | 定性的指示のみ("avoid long subordinate clauses")、数値上限なし | 規定なし |
| 関係詞 | `TBD` | 規定なし | 規定なし |
| 受動態 | `TBD` | 規定なし | 規定なし |
| 完了形・進行形 | `TBD` | 規定なし | 規定なし |
| 助動詞 | `TBD` | 規定なし | 規定なし |
| 固有名詞 | `TBD` | 保持可(周辺文は簡単に) | 理解に必要な場合のみ |
| 数字・金額・日付・% | `TBD` | CEFR別の簡略化ルールなし(音声制作段階のMFA/ASR対応のみ) | 同左 |
| 専門語 | `TBD` | 理解に必要なら保持可 | 理解に不可欠なら残してよい |
| タイトル | `TBD` | 固定構造(`# Title`)のみ、CEFR別の語数・語彙制限なし | 同左 |
| 生成元 | `TBD`(要ユーザー判断、[OPEN_ITEMS](OPEN_ITEMS.md)参照) | Natural English Sourceから独立生成 | Natural English Sourceから独立生成 |

根拠: `er003_v1_translator_briefs/b1_p1_prompt_template.txt`、
`er003_b1_article.py`、`er003_v1_translator_briefs/b2_adapter_prompt_template.txt`、
`er003_b2_adapter.py`、[ER-003-A2-00_SPEC_AUDIT.md](ER-003-A2-00_SPEC_AUDIT.md)(2026-08-09)。

**`levels.py`のA2/B1/B2数値(vocab 1,000語/620-700語等)は、
`generate_test.py`/`tts_test.py`という無関係な別番組専用の値であり、
このCEFR表には一切採用していない。**

## Key Phrase

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| 選定方式 | Strategy L (Listening Blocker Ranking) | `DECIDED` | ER-003-P2I(commit `e33f227`) | 2026-07-xx |
| 件数 | 5件/記事 | `DECIDED` | ER-003-P2I | 2026-07-xx |
| 語数範囲 | 1〜5語(`key_phrase`) | `DECIDED` | ER-003-KP-02-R1(commit `5a94db0`) | 2026-08-08 |
| 選定元 | 各記事自身のCEFR-B1本文(承認済み) | `DECIDED` | ER-003-REPRO-01-KP(commit `46aa2e8`) | 2026-08-08 |
| 後処理 | Pedagogical Phrase Canonicalization(`source_span`→`display_phrase`→`key_phrase`→`used_form`) | `DECIDED` | ER-003-KP-01(commit `e607d26`) | 2026-08-08 |
| Canonicalization原則 | 「最小」ではなく「最小十分」 | `DECIDED` | ER-003-KP-02(commit `8856264`) | 2026-08-08 |
| QAモデル | 3状態(`CANONICALIZATION_PASS`/`REVIEW_REQUIRED`/`INVALID`)、11 QAフィールド | `DECIDED` | ER-003-KP-01→KP-02→KP-02-R1 | 2026-08-08 |
| Traceability定義 | 「source_spanから説明可能な正規化で導出できる」こと。文字通りの部分文字列一致は不要 | `DECIDED` | ER-003-KP-02-R1 | 2026-08-08 |
| human review条件 | いずれかのQAフィールドがFAILならREVIEW_REQUIRED、自動retryなし、人間承認で採用可 | `DECIDED` | ER-003-KP-01→KP-02 | 2026-08-08 |
| `used_form`/`key_phrase`の関係 | 現状100%重複(技術的負債として記録、整理はしない) | `DECIDED`(整理しない方針が決定事項) | ユーザー指示(2026-08-08、KP-02-R1承認時) | 2026-08-08 |

## Preview

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| 言語 | 日本語のみ | `DECIDED` | ER-003-B1-P9A-R1(英語Key Phrase埋め込み方式は不採用) | 2026-08-07 |
| TTS model | `gemini-3.1-flash-tts-preview` | `DECIDED` | ER-003-B1-P7A(commit `b4f871f`) | 2026-08-06 |
| 採用理由 | 旧モデル(2.5)で「激しい」→「げきせつな」等の誤読が発生し、3.1で解消を確認 | `DECIDED` | ER-003-B1-P7A | 2026-08-06 |
| voice | Aoede | `DECIDED` | ER-003-B1-P7A以降 | 2026-08-06 |
| 生成方式 | 単一TTS call(chunk分割なし) | `DECIDED` | ER-003-B1-P7A | 2026-08-06 |
| Key Phrase埋め込み | しない(Full Story側のみで扱う) | `DECIDED` | ER-003-B1-P9A-R1以降 | 2026-08-07 |
| モデル分離 | Preview(3.1)とFull Story(2.5)の設定を分離、片方の変更が他方に波及しない設計 | `DECIDED`、`ModelIsolationTests`で固定確認済み | ER-003-B1-P8A | 2026-08-07 |
| 承認フロー | ①台本(日本語テキスト)をチャットで提示→ユーザー承認→②その台本のまま音声生成→③音声試聴→ユーザー承認。台本確定後の勝手な再生成・変更はしない | `DECIDED` | ER-003-REPRO-01/02-PREVIEW系 | 2026-08-08〜09 |

## Full Story

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| TTS model | `gemini-2.5-pro-preview-tts` | `DECIDED`(凍結仕様) | ER-003-B1-P4D〜P8A | 2026-08-06以前 |
| voice | Aoede | `DECIDED` | 同上 | 同上 |
| chunk構成 | 3chunk | `DECIDED`(凍結仕様) | ER-003-B1-P4D〜P8A | 同上 |
| 内容QA retry | 3試行1セット(`run_tts_content_attempts`) | `DECIDED` | ER-003-B1-P8A系 | 2026-08-07 |
| 短文ナレーション生成 | 前後文脈のない短いフレーズは専用の最小限instructionで生成 | `DECIDED` | ER-003-B1-P9A-R1(commit `d41e4fe`) | 2026-08-07 |
| strict ASR検証 | 部分一致 + ASR文字数上限(期待文字数+少数の余裕)の両方を確認 | `DECIDED` | A02 meaning_5発見を機に追加 | 2026-08-08 |
| minimal instruction fallback | 標準経路が規定回数不合格の場合、最小限instructionへ自動フォールバック(短文ナレーション・英語Key Phrase Componentの両方に適用) | `DECIDED` | ER-003-REPRO-01-MAIN | 2026-08-08 |
| Dynamics処理 | **不使用**(scalar gainのみ、compressorやDynamics3は使わない) | `DECIDED` | `er003_b1_p9a_audio.py`にコード内コメントで明記 | 2026-08-07 |

## Audio Assembly

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| 複数箇所編集の順序 | 時系列で**後ろから前へ**適用(insert2→insert1→title_trim等) | `DECIDED` | ER-003-B1-P7C(バグ発見)〜P9A-R1/R2で徹底 | 2026-08-07 |
| 境界検出 | MFA(Montreal Forced Aligner)を優先、RMSは補助のみ | `DECIDED` | プロジェクト全体方針(P3W以降) | - |
| 数字・日付境界 | MFA単独で確定せず、必ずASRまたは他の診断で裏付ける | `DECIDED` | ER-003-B1-P9A-R2("England 1–2 Argentina"語順バグを機に確立) | 2026-08-07 |
| notification2挿入 | Full Story内2箇所(Today's Points直前、In One Line直前) | `DECIDED` | ER-003-REPRO-01/02-MAIN | 2026-08-08〜09 |
| 音量調整 | scalar RMS基準(Preview/Bodyは無調整のアンカー、他要素は平均RMSへ、OutroはIntro基準RMSへ一致)。A01のみ追加の聴感補正(約-5.85dB)を適用、A02/ADD03には適用していない | `DECIDED` | ER-003-B1-P9A系/ER-003-REPRO-01-MAIN | 2026-08-07〜08 |

## QA / Human Review

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| ASR診断 | Azure STT(`en-US`/`ja-JP`)を全内容確認・境界検証に使用。決定はASRだけで下さない | `DECIDED` | プロジェクト全体方針 | - |
| hallucination対応 | strict検証+minimal instruction fallbackで自動検出・自動吸収(A02で2件実績)。**根本原因は未解明のまま** | `DECIDED`(運用方針)、原因は`UNDER_REVIEW`ではなく未解明のまま保留 | ER-003-REPRO-01-MAIN | 2026-08-08 |
| ASR homophone ambiguity対応 | strict検証が規定回数不合格でも、TTS自体が正常な可能性がある場合はretryを打ち切り、`PROVISIONALLY_ACCEPTED_REQUIRES_HUMAN_REVIEW`→ユーザー試聴後`ACCEPTED_AFTER_HUMAN_REVIEW`という2段階の人間確認フローを使う | `DECIDED`(ADD03 meaning_3で初適用・確定) | ER-003-REPRO-02-MAIN/FINAL | 2026-08-09 |
| 最終人間試聴 | 機械QA全合格でも「完成」「量産再現性合格」とは判断せず、必ずユーザー試聴を経る | `DECIDED` | 全ステージで一貫 | - |
| 量産再現性判定 | A. 量産候補として採用可能(A02・ADD03の2記事連続成功に基づく)。ただし完全自動化ではなく最終人間試聴を必須ゲートとして維持 | `DECIDED` | ER-003-REPRO-FINAL(commit `c4a762c`) | 2026-08-09 |

## 参照元

[ER-003-A2-00_SPEC_AUDIT.md](ER-003-A2-00_SPEC_AUDIT.md)、
[ER-003-B2-AUDIT-01_SPEC_AUDIT.md](ER-003-B2-AUDIT-01_SPEC_AUDIT.md)、
[ER-003-REPRO_BASELINE.md](ER-003-REPRO_BASELINE.md)、
[ER-003_PIPELINE_CROSS_CUTTING_RULES.md](ER-003_PIPELINE_CROSS_CUTTING_RULES.md)、
[ER-003-B1_P8A-P9A_AUDIT_REPORT.md](ER-003-B1_P8A-P9A_AUDIT_REPORT.md)、
[DECISION_LOG.md](DECISION_LOG.md)

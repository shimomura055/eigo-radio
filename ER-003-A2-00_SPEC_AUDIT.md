# ER-003-A2-00 A2既存仕様監査

**管理ID: ER-003-A2-00**
**実施日: 2026-08-09**
**スコープ: 監査のみ。A2本文生成・音声生成・既存コード変更は一切行っていない。**

## 0. 結論(先に要約)

リポジトリ全体(コード・prompt・test・decision record・過去成果物)を監査した結果、
**「English Your Way」番組(ER-003パイプライン、B1/B2で運用中のもの)向けの
A2固有仕様は、現時点で1件も存在しない。**

- A2向けのCEFR語彙制限・文長数値・validator・testは、ER-003パイプライン内に
  ゼロ件(すべてgrep・読み込みで確認済み、根拠は下表参照)。
- `levels.py`にA2の数値(語彙1,000語・平均文長10語・620〜700語等)が存在するが、
  これは`generate_test.py`/`tts_test.py`という**ER-003と無関係な、別の対話形式
  番組(LEO/MAYAの掛け合い、演技指導)専用の古い参照値**であり、初回commit
  (`38f136b`)から存在する。この値を使ってA2の実記事が生成された記録
  (`candidates_A2_*.md`/`episode_A2_*.json`等)はリポジトリに1件も存在しない。
- 唯一の公式な言及は、`er003_v1_p1b_natural_source_spec.md`(commit `45c48ee`、
  確定日2026-07-20)の「Natural English SourceはB2・B1・A2の各レベル版を
  **独立して生成する**ための内部基準原稿」という一文のみ。数値条件・語彙制限・
  文長ルールは一切記載されていない。
- したがって、20項目のほぼ全てが**「未確定」**である。B1・B2の実際の値は
  「参考(コピー禁止)」として併記するが、A2の正式値ではない。

**矛盾点(4節参照、統合せず提示)**: 今回のユーザー依頼文言「B2→B1まで完了
したため、次はA2版を制作する」は、B1からA2への**逐次簡略化**を示唆している。
一方、上記の唯一の公式decision record(`er003_v1_p1b_natural_source_spec.md`)
は、A2をNatural English Sourceから**独立生成**する設計として明記している。
この2つの前提は一致しない。**どちらの設計でA2を作るかは、本監査では判断せず、
ユーザーの決定を仰ぐ。**

---

## 1. 20項目 監査表

| # | 項目 | 正式ルール(A2向け) | 数値条件(A2向け) | 根拠ファイル | commit / decision record | validator / test | 区分 |
|---|---|---|---|---|---|---|---|
| 1 | CEFR語彙制限 | **なし** | 未確定(参考: `levels.py`のA2="most frequent 1,000 words"は無関係な別番組の値、不採用候補) | `levels.py:13-16`(参考のみ) | `38f136b`(Initial commit、ER-003以前) | なし(wordlist参照コード自体がリポジトリに存在しない、grep確認済み) | **未確定** |
| 2 | 1文あたりの語数上限・目安 | **なし** | 未確定(参考: B1=平均15語以下・最長24語、B2=平均19語以下・最長32語。levels.pyのA2 avg=10語は不採用候補) | B1: `er003_v1_translator_briefs/b1_p1_prompt_template.txt:7`, `er003_b1_article.py:130-131`。B2: `er003_v1_translator_briefs/b2_adapter_prompt_template.txt:7`, `er003_b2_adapter.py:94-95` | B1側`fcb1387`、B2側`3975602` | B1は診断専用(`er003_b1_article.py:139`「指標違反でも記録するだけで、この関数自体は再生成のトリガーにしない」)。B2は実際のgate(`er003_v1_p2a_recalculate.py`、A01/A02/ADD03全記事が一度FAILし`ead43ab`で文分割ロジック修正後PASSへ訂正)。A2向けはゼロ | **未確定** |
| 3 | 記事全体の語数上限・目安 | **なし** | 未確定(参考: B1は「総語数のhard limitは設けない」と明記。levels.pyのA2=620〜700語は不採用候補) | `er003_b1_article.py:126-129` | `fcb1387` | なし | **未確定** |
| 4 | 1文の情報量・1文1アイデア | B1のみ定性的指示"Prefer one idea per sentence"あり。A2向けは**なし** | なし(数値化されていない) | `er003_v1_translator_briefs/b1_p1_prompt_template.txt:7` | `fcb1387` | なし | **未確定**(B1ルールのコピー可否は要決定) |
| 5 | 等位接続・従属節の制限 | B1のみ定性的指示"Avoid long subordinate clauses and heavy nesting"あり(数値上限なし)。A2向けは**なし** | なし | `er003_v1_translator_briefs/b1_p1_prompt_template.txt:7` | `fcb1387` | なし | **未確定** |
| 6 | 関係詞の扱い | **なし**(B1・B2いずれのpromptにも言及なし、grep該当0件) | なし | 該当なし | 該当なし | なし | **未確定** |
| 7 | 受動態の扱い | **なし**(同上、grep該当0件) | なし | 該当なし | 該当なし | なし | **未確定** |
| 8 | 完了形・進行形・時制 | **なし**(同上、grep該当0件) | なし | 該当なし | 該当なし | なし | **未確定** |
| 9 | 助動詞の扱い | **なし**(同上、grep該当0件) | なし | 該当なし | 該当なし | なし | **未確定** |
| 10 | 固有名詞の扱い | A2向けは**なし**。参考: B1「保持可、周辺文は簡単に」、B2「理解に必要な場合のみ」 | なし | `b1_p1_prompt_template.txt:5`, `b2_adapter_prompt_template.txt:5` | `fcb1387`, `3975602` | なし | **未確定** |
| 11 | 数字・金額・日付・%の扱い | **なし**。既存ルールは音声制作段階(MFA境界・書字順とのズレ対策)のみで、CEFR難易度別の数値簡略化ルールではない | なし | `ER-003_PIPELINE_CROSS_CUTTING_RULES.md`2節 | `1b62a20`等(横断ルール文書) | なし | **未確定** |
| 12 | 専門語・ニュース固有語の扱い | A2向けは**なし**。参考: B1/B2とも「理解に不可欠な場合のみ残してよい」という定性方針 | なし | `b1_p1_prompt_template.txt:5`, `b2_adapter_prompt_template.txt:5` | `fcb1387`, `3975602` | なし | **未確定** |
| 13 | B1/B2からA2への情報削減ルール | **なし。かつ設計方針自体が未確定**(4節「矛盾点」参照) | なし | `er003_v1_p1b_natural_source_spec.md:27` | `45c48ee` | なし | **未確定・要ユーザー判断** |
| 14 | タイトルのルール | A2向けは**なし**。B1も固定構造(`# Title`)のみでCEFR別の語数・語彙制限はない | なし | `b1_p1_prompt_template.txt:11-31` | `fcb1387` | 構造チェック`validate_p1b_structure`はB1共通(CEFR非依存) | **未確定** |
| 15 | Point One/Two/In One LineのA2固有ルール | **なし**。固定構造自体はCEFR非依存の製品仕様と推定されるが、A2向けとして明記された記録はない | なし | `b1_p1_prompt_template.txt:11-31` | `fcb1387` | 同上(CEFR非依存) | **未確定**(構造は共通の可能性が高いが未確認) |
| 16 | PreviewのA2固有ルール | **なし**。既存Preview仕様(日本語のみ、A01基準109文字/20.76秒)はCEFRではなく音声尺の製品仕様 | なし | `ER-003-REPRO_BASELINE.md`(A01 Preview欄) | 複数(P7A系) | なし | **未確定** |
| 17 | Key PhraseのA2選定条件 | **なし。明示的にスコープ外と記録されている** | なし | `er003_output/p2i/ER-003-P2I_decision_record.md:51`(「B1/A2 Key Words...本ステージでは実施していない」) | `e33f227` | なし | **未確定(明示的スコープ外)** |
| 18 | 音声速度・TTS条件のA2固有差 | **なし。仕組み自体が存在しない** | なし | `er003_b1_p3r_audio.py:10`(「speed/pitch指定は一切追加しない」) | 該当コミット未特定(P3r導入時) | なし | **未確定(該当機構なし)** |
| 19 | validatorで機械的に検査される条件 | A2向けは**ゼロ** | なし | (B1/B2の対照は上記2番参照) | - | A2向けvalidator: 0件 | **該当なし** |
| 20 | 過去A2実験記事・成果物の有無 | N/A(調査結果) | - | `candidates_A2_*.md`/`episode_A2_*.json`ともに0件(Glob確認)。`"estimated_cefr":"A2"`と判定された過去記録も0件 | - | - | **確認済み: 存在しない** |

---

## 2. 特に重要な2項目の根拠(詳細)

### 2-1. 語彙制限(項目1)

- ER-003パイプライン内に、CEFR別の語彙リスト(wordlist/frequency list/NGSL/
  CEFR-J等)を参照・検証するコードは**一切存在しない**(`wordlist|word_list|
  frequency list|vocab_list|oxford|NGSL|CEFR-J`で全`.py`をgrepし、0件)。
- B1・B2とも、語彙の扱いはprompt内の**定性的指示のみ**であり、機械的な
  語彙チェックは行われていない。
  - B1: `"Vocabulary: use mostly common, everyday vocabulary (the kind of
    words a general-interest B1 learner already knows)."`
    (`er003_v1_translator_briefs/b1_p1_prompt_template.txt:5`)
  - B2: `"主に一般的なB2以下の語彙を使ってください。"`
    (`er003_v1_translator_briefs/b2_adapter_prompt_template.txt:5`)
- `levels.py`の`"vocab_range": "most frequent 1,000 words"`(A2)は、
  `generate_test.py`/`tts_test.py`/`tts_test_openai.py`という、LEO/MAYAの
  対話・演技指導形式の**別の番組**でのみ`from levels import LEVELS`され
  使用されている(3ファイルのみ、いずれも"English Your Way"のB1/B2
  パイプライン=`er003_*`系ファイルとは無関係)。この値を根拠として
  採用することはできない。

### 2-2. 1文の長さ(項目2)

- B1の実コード上の値: `B1_MAX_SENTENCE_WORD_COUNT = 24`
  (`er003_b1_article.py:131`)、目標平均`B1_TARGET_AVG_WORDS_PER_SENTENCE
  = 15.0`(同130行)。ただし**この関数はgateではない**——
  `compute_b1_sentence_metrics`のdocstring(同137-139行)に明記の通り、
  「指標違反でも記録するだけで、この関数自体は再生成のトリガーにしない」。
- B2の実コード上の値: `B2_MAX_AVG_WORDS_PER_SENTENCE = 19.00`、
  `B2_MAX_SENTENCE_WORD_COUNT = 32`(`er003_b2_adapter.py:94-95`)。
  こちらは**実際のgate**として機能している。P2Aステージで
  `overall_status = "B2_SENTENCE_METRICS_FAIL"`が実際にA01/A02/ADD03の
  3記事すべてで一度発生し、文分割ロジックのバグ修正後にPASSへ訂正された
  記録がcommit `ead43ab`(「ER-003-P2AでB2文長ゲート判定をA01/A02/ADD03
  すべてPASSへ訂正」)に残っている。
- A2向けの数値は、コード・prompt・test・decision recordのいずれにも
  一切存在しない。`levels.py`の`"avg_sentence_len": "10"`(A2)は上記
  項目1と同じ理由(無関係な別番組専用の値)で不採用候補として扱う。

---

## 3. 全体所見: B1/B2との構造的な違い

- B1はNatural English Source(CEFR制約なし、`er003_v1_p1b_natural_source_
  spec.md:19`「CEFR・語彙・文長・語数制約 | なし」)から**直接**生成される
  (`b1_p1_prompt_template.txt`のプレースホルダーは`{approved_natural_
  english_source}`のみ、B2本文は入力に使われない構造的保証あり
  `er003_b1_article.py:190-192`)。
- B2はNatural English Sourceから独立して生成される(B2 adapter)別経路。
- A2の生成元をどちらに揃えるか(Natural English Sourceから独立生成する
  B1/B2と同じ設計か、それともB1本文からのさらなる簡略化か)は、
  4節の矛盾点として未解決。

---

## 4. 矛盾点(統合せず提示、ユーザー判断が必要)

**矛盾A: A2の生成元**

- ユーザー依頼の文言: 「B2→B1まで完了したため、次はA2版を制作する」
  → 逐次的な難易度低下(B2を作り、そこからB1を作り、そこからさらに
    A2を作る、という**派生**の設計を示唆しているように読める)
- 公式decision record: `er003_v1_p1b_natural_source_spec.md:27`
  「Natural English SourceはC1版ではなく、**B2・B1・A2の各レベル版を
  独立して生成するための**内部基準原稿である」
  → B1・B2と同じく、A2もNatural English Sourceから**独立して**生成する
    設計として明記されている(B1やB2の本文を入力にする設計ではない)

この2つは同じ「B2→B1→A2」という制作の**順序**を指しているのか、それとも
制作**順序**は逐次でも生成の**入力**は独立(=毎回Natural English Source
から生成)なのか、文言上は判別できない。**本監査ではどちらが正しいかを
判断せず、ここで提示するにとどめる。**

**矛盾B: 実装なし**

厳密には「矛盾」ではないが、注意点として記録する。levels.pyのA2数値
(語彙1,000語/平均10語/620-700語/wpm105-115)は、一見「A2の正式仕様」に
見える具体的な数値を持つため、誤って参照されるリスクがある。しかし
上記の通り、これは無関係な別番組専用の値であり、**"English Your Way"
のA2として採用された事実は一度もない**。この数値をA2の正式仕様として
扱うことは、本監査の結論と矛盾する。

---

## 5. 本監査のスコープ外(実施していないこと)

- A2本文の生成・試訳
- A2音声の生成
- 既存コード(`er003_b1_article.py`、`er003_b2_adapter.py`、`levels.py`等)の変更
- A2仕様の新規決定・数値の提案
- 矛盾点(4節)の統合・解決

---

## 参照元

- [levels.py](levels.py)
- [er003_v1_translator_briefs/b1_p1_prompt_template.txt](er003_v1_translator_briefs/b1_p1_prompt_template.txt)
- [er003_v1_translator_briefs/b2_adapter_prompt_template.txt](er003_v1_translator_briefs/b2_adapter_prompt_template.txt)
- [er003_b1_article.py](er003_b1_article.py)
- [er003_b2_adapter.py](er003_b2_adapter.py)
- [er003_v1_p1b_natural_source_spec.md](er003_v1_p1b_natural_source_spec.md)
- [er003_output/p2i/ER-003-P2I_decision_record.md](er003_output/p2i/ER-003-P2I_decision_record.md)
- [ER-003_PIPELINE_CROSS_CUTTING_RULES.md](ER-003_PIPELINE_CROSS_CUTTING_RULES.md)

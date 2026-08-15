# ER-003-B1-NOVEL-AUDIO-01 実行報告(新規記事によるBlind Listening検証)

**管理ID: ER-003-B1-NOVEL-AUDIO-01**
**実施日: 2026-08-16**
**ステータス: `PROTOTYPE / EXPERIMENT`(N増し検証。Production仕様化はしていない)**

**注意: 本報告書は記事内容の詳細(結論・引用等)を含む。ユーザーが
Blind Listening ArtifactでFull Audioを試聴し終える前に本ファイルを
開くと、内容を事前に知ってしまうため、試聴後の閲覧を推奨する。**

## 目的

B1 Supported Natural English方式が、ユーザーにとって未知の新規記事
(完全新規テーマ・完全新規Research)でも成立するかを検証した。既存A02は
ユーザーが内容を何度も読んでいるため、既知情報による理解とB1
Scaffoldによる理解を分離できないという制約があったため、今回は
Research→Fact Safety→B2 Natural English→B1 Scaffold→TTS→QA→Full Audio
の全工程を一から実施した。

## A. テーマ選定とResearch

テーマ: AI / Technological Singularity(ユーザー関心テーマ)。

WebSearch/WebFetchで最新情報を直接調査し、「Singularityが実際に起こる/
すでに起きている/特定年に到来する」ことを前提化せず、「2026年時点で
何が議論されているか」というニュース性のあるangleを選定した。

選定したangle: 2026年に著名なAI企業リーダー(OpenAI CEO・Sam Altman、
Elon Musk)がそれぞれ「Singularityの中にいる」「今年が到来の年だ」と
発言した一方、AI研究者を対象とした大規模調査は「高度な機械知能」到来の
50%確率時点を2047年と推定しており、両者の間に大きな時間軸のギャップが
あるという、確認可能な事実に基づく対比。

## B. Verified Fact Ledger

`er003_output/novel_audio_01/SING01/research/verified_fact_ledger.txt`
に、FACT([VERIFIED_FACT])/PREDICTION/OPINION/HYPOTHESISの4分類で
記録した(既存[VERIFIED]/[AMBIGUOUS]の考え方を本記事用に拡張)。8件の
FACT、2件のPREDICTION、2件のOPINION、1件のHYPOTHESISを、すべて出典
URL付きで記録した。「Singularityが実際に到来する/した」という主張
自体はいずれのFACTの対象にもしていない。

**独立Fact Checker(Web検索によるクロス検証)を3回実施**し、以下の
問題を発見・修正した:
1. HLMI(高度な機械知能。機械が支援なしにあらゆるタスクを人間より
   安く上手に遂行できる状態)とSingularityそのものを同一視していた
   → 明示的に「別の、より狭い指標」と区別する記述へ修正
2. McKinsey調査の「全社スケーリングに着手した約3分の1」を「完了した」
   かのように書いていた → 「着手した」に訂正(完全展開済みは7%)
3. 調査対象研究者について「商業的利害を持たない」という未確認の
   属性を記事に追加していた → 削除
4. Nick Bostromの発言として引用した比喩("brilliant new employee...")
   が出典で確認できなかった → 削除し、確認できる内容のみ残した

3回目の再検証で、Fact Checker `verdict: PASS`、Ledger Deviation Check
`overall_status: LEDGER_COMPLIANT`(deviations 0件)を達成した。

## C. B2 Natural English本文

`er003_output/novel_audio_01/SING01/article/B2_article.md`
(493語)。B1専用の別本文は作成していない(Full Story Part1/2・Point
One/Two・In One LineはB1/B2で完全共通)。

- Point One: 53語、Point Two: 58語(目標30〜60語の範囲内)
- Spoken-first Number Treatment: 93%/50.6%(AI能力対比)・88%/39%
  (企業調査のANCHOR数値)は精度を保持、その他(81.2%→「around eighty
  percent」、35/42点→「gold-medal-level score」等)は聞き取りやすさ
  優先で丸めた

## D. B1 Support(Preview/Comment1-4)

News本文より明確に易しいSupport Englishとして作成。Comment役割は
指定通り: Comment1=Listening Focus、Comment2=Mid-story Recovery+Next
Question、Comment3=Story Meaning+Bridge、Comment4=Point Recovery+
Bridge。News本文より先に結論・引用・数値を明かさない設計とした。

Support文言に対してもLedger Deviation Check(LEDGER_COMPLIANT達成)と
独立Fact Checkerを実施。Fact CheckerはSupport文の性質上(意図的に
曖昧な案内文であり、具体的な引用・数値を含まない)`REVIEW_REQUIRED`
という結果になったが、これはSupport設計の意図(News本文より先に
Factを明かさない)そのものであり、binding gateはLedger Deviation
Check(LEDGER_COMPLIANT)のみとした(ER-003-B1-SCAFFOLD-AUDIO-01の
既存方針を踏襲)。ただし、Comment3の「一つの調査がより遅い時期を
示す」という記述がB節と同じHLMI/Singularity同一視の懸念を指摘され
たため、B節と整合する表現へ修正した。

## E. Key Phrase選定(方式L + Canonicalization)

既存のStrategy L(Listening Blocker Ranking)selectorとCanonicalization
の仕組み(`er003_b1_p2_keywords.py`/`er003_key_words_canonicalization.py`)
を、入力をSING01のB2本文へ差し替えてそのまま再利用した。新しい選定
ロジックは設計していない。

| Rank | English | 日本語 |
|---|---|---|
| 1 | singularity | AIが人間を超え、予測不能になる転換点 |
| 2 | scale something across an organization | 組織全体へ本格展開する |
| 3 | jagged frontier | 能力に激しい凹凸がある境界 |
| 4 | event horizon | 後戻りできない境界点 |
| 5 | put good odds on | ～の可能性が高いと見る |

5件全件、Canonicalization QA(11項目)PASS、`overall_status: PASS`。

## F. TTS/ASR生成

`er003_audio_tts_asr_safety.py`(ER-003-AUDIO-HARDENING-01)を原則
利用し、同等処理を本記事専用scriptへ再実装しなかった。全15コンテンツ
segment(Topic intro・Preview・Comment1-4・News5本・Key Phrase英語
Component5件+日本語meaning5件)がASR検証PASSした。

**発見した技術的問題(2件)**:

1. **Key Phrase 5日本語meaningのASR検証失敗**: japanese_gloss
   「～の可能性が高いと見る」の先頭「～」(書き言葉のプレースホルダー
   記号)がTTSで正しく発話されず/ASRで認識されず、6回全て不合格に
   なった。OPEN-28と同種の事象と判断し、ナレーション用テキストのみ
   先頭の「～」を除去して再生成した(Canonicalization正式出力の
   japanese_glossフィールド自体は無変更)。

2. **News本文(ENGLISH_STYLE_PREFIX経路)でのtail切れ再発**:
   QA中、`point_one`の末尾波形が他segmentより明らかに高いRMSで
   終わっている(自然に減衰しきる前に終わっている)ことを発見した。
   調査の結果、`p9a.generate_narration_snippet`(Full Story/Point/In
   One Line生成の主経路)が、内部で`p3u.trim_english_keyword_
   silence`を**既定の安全マージン0.08秒(Key Phrase単語向け)のまま**
   呼び出していることが判明した。これはER-003-B1-SCAFFOLD-AUDIO-03で
   発見・修正したPreview"prove"語尾切れと**同一クラスのバグ**だが、
   AUDIO-03の修正はPreview/Comment生成経路(MINIMAL_INSTRUCTION経路)
   のみを対象としており、News本文が主に使うENGLISH_STYLE_PREFIX経路
   には未適用だった。今回、`point_one`(末尾10ms RMS 0.01495)と
   `full_story_part1`(同0.00938、軽度)を、安全マージン0.35秒
   (AUDIO-03と同じ値)で再生成し、両方とも0.0002未満まで改善した。
   `p9a.generate_narration_snippet`自体(Production隣接の既存共有
   関数)は変更していない。

## G. Full Audio組み立て

ER-003-B1-SCAFFOLD-AUDIO-03で確立したAudio Shell(Intro/Outro/
Notification/pause値/Key Phrase提示構造/post-processing、Comment=
Charon・News/Preview=Aoede、Japanese title除去、Point explanation
英語版"Here's the point."をAUDIO-03から無変更で再利用)をそのまま
継承した。新しいpause秒数・gain方式は設計していない。

- 総尺: **383.96秒(6分24秒)**
- clipping: なし(peak 0.95、既存のgain上限キャップに複数segmentが
  到達したための値であり、gain計算方式自体は無変更)
- 全27音声セクション、AUDIO-03と同じ並び順

## H. QA結果

| 項目 | 結果 |
|---|---|
| Fact Checker(B2本文) | PASS(3回目の再検証で達成) |
| Ledger Deviation Check(B2本文) | LEDGER_COMPLIANT |
| Ledger Deviation Check(Support文) | LEDGER_COMPLIANT |
| Key Phrase選定+Canonicalization | PASS(5件全件) |
| 全15content segment ASR検証 | PASS |
| head/tail cut | 2件発見・修正済み(F節参照)、修正後全segment tail RMS < 0.001 |
| 日本語残存Audit | Key Phrase訳(5件)以外0件 |
| Point word count | Point One 53語、Point Two 58語(目標30〜60語内) |
| B1/B2共通テキスト | Full Story/Point/In One LineはB1専用本文を作成せず、B2と完全共通(分離不要) |
| 既存回帰テスト(37件) | 全PASS(`er003_test_audio_tts_asr_safety.py`+`er003_test_b1_scaffold_audio_01.py`) |
| clipping | なし |

## I. Blind Listening Artifact

2画面構成:
- **View 1(初期表示)**: 番組タイトル(汎用)+尺バッジ+Full Audio
  player+「試聴後に開示」ボタンのみ。記事の実タイトル・要約・結論は
  一切表示しない
- **View 2(ボタンクリックで初めて表示、`display:none`で構造的に
  非表示)**: 実タイトル・全文transcript・Key Phrase一覧・出典・QA
  サマリー

URL: https://claude.ai/code/artifact/701978f4-0a54-489e-a766-6cdeba8d91d7

## J. Production非変更確認

- CURRENT_SPEC.md・DECISION_LOG.md・A2/AUDIO-03最終script・
  `er003_b1_p2_keywords.py`/`er003_key_words_canonicalization.py`/
  `p9a.generate_narration_snippet`等の既存共有関数: いずれも無変更
- B1専用News本文の再導入・A2/B2仕様変更・Comment voiceの正式確定・
  Preview voiceの再設計・Audio Shell細部文言の全面改善・HARDENING
  moduleのProduction integrationは、いずれも行っていない
- B1/B2共通化の正式決定は行っていない(プロトタイプ検証のまま)

## K. Git

commit/push結果は、本報告の送付メッセージ末尾を参照。

## 対象ファイル一覧

| ファイル | 内容 |
|---|---|
| `er003_v1_sing01_factqa_generate.py`(新規) | B2本文Fact Checker/Ledger Deviation Check |
| `er003_v1_sing01_kp_generate.py`(新規) | Key Phrase選定(方式L)+Canonicalization |
| `er003_v1_sing01_kp5_ja_fix.py`(新規) | Key Phrase5日本語meaning個別修正 |
| `er003_v1_sing01_audio_generate.py`(新規) | 全content TTS生成+ASR検証 |
| `er003_v1_sing01_news_tail_fix.py`(新規) | News本文tail切れ修正(F節) |
| `er003_v1_sing01_assemble_generate.py`(新規) | Full Audio組み立て |
| `er003_output/novel_audio_01/SING01/`(新規) | 記事本文・Ledger・Key Phrase・音声監査資料一式 |
| `ER-003-B1-NOVEL-AUDIO-01_REPORT.md`(新規) | 本報告書 |

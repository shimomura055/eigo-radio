# ER-003-B1-NOVEL-AUDIO-01-VOICE-01 実行報告(Voice役割再配置+Point見出し追加)

**管理ID: ER-003-B1-NOVEL-AUDIO-01-VOICE-01**
**実施日: 2026-08-16**
**ステータス: `PROTOTYPE / EXPERIMENT`(N増し検証。Production仕様化はしていない)**

**注意: 本報告書は記事内容の詳細を含む。Blind Listeningを維持したい
場合は、試聴後の閲覧を推奨する。**

## A. Voice Allocation修正結果

「Aoede=本文・Listening対象」「Charon=Navigator/Explanation」という
役割分担に沿って再配置した。

| セクション | 修正前 | 修正後 |
|---|---|---|
| Welcome | Aoede | **Charon** |
| Topic intro | Aoede | **Charon** |
| Preview intro | Aoede | **Charon** |
| Point explanation("Here's the point.") | Aoede | **Charon** |
| Preview(本文) | Aoede | Aoede(無変更) |
| Key phrases intro | Aoede | **Charon** |
| 番号ラベル(One.〜Five.) | Aoede | **Charon** |
| Key Phrase英語Component | Aoede | Aoede(無変更) |
| Key Phrase日本語meaning | Aoede | **Charon** |
| Full story intro | Aoede | **Charon** |
| Comment 1〜4 | Charon | Charon(無変更) |
| Full Story Part 1/2 | Aoede | Aoede(無変更) |
| Point One/Two(本文) | Aoede | **Charon** |
| In One Line | Aoede | **Charon** |

明示リスト外だった4項目(Preview intro/Point explanation/Key phrases
intro/Full story intro)と、Key Phraseの番号ラベル(One.〜Five.)は、
指示書の一般原則(Charon=Navigator/セクション案内)への該当を確認の
うえユーザーへ質問し、いずれも「Charonへ統一」の回答を得てから実施
した(独自判断で仕様を拡大解釈していない)。

## B. Point見出し追加

Point One/Two本文の直前に、短いspoken headingを追加した(役割:
Navigator、voice: Charon)。

## C. 重要な発見: "Point One."/"Point Two."は現行TTSモデルで実現不可

仕様指定の文言("Point One."/"Point Two."のみ)で生成を試みたところ、
voice・大文字小文字・単体発話/文中埋め込み・instruction方式のいずれを
変えても、毎回「.1.」「.2.」としか発音・認識されないことが判明した。

調査の結果、英語の"point one"/"point two"は、小数の読み方(例:
"3.1"="three point one"、"0.2"="point two")と完全に同じ語列であり、
TTSモデルが"Point"を独立した単語としてではなく小数点表現の一部として
解釈し発音しているためと判明した(この現象はvoice非依存で、Aoede/
Charonどちらでも再現した)。

**独自判断で仕様変更せず**、この事実をユーザーへ報告し、対応方針を
確認した。ユーザーの判断により、意味を保ちつつ字面のみ変える代替
文言"First point."/"Second point."を採用することとした(ASR検証で
即座にEXACT_MATCH、安定して発音・認識されることを確認済み)。

## D. Pause値

Point見出し→Point本文間のpauseは、既存Audio Shellで唯一の同型パターン
(Point explanation→Previewの0.7秒)をそのまま転用した。新しいpause値は
設計していない。Point One本文→Point Two見出し間は、既存のPoint1→
Point2間pause(0.8秒)をそのまま維持した。

## E. 再生成segment一覧

Charonで新規生成した21 segment、すべてASR検証PASS:

| Segment | 内容 | 結果 |
|---|---|---|
| welcome | "Welcome to English Your Way." | PASS |
| topic_intro | "Today's topic is..." | PASS |
| preview_intro | "Here's a quick preview." | PASS |
| point_explanation_en | "Here's the point." | PASS |
| key_phrases_intro | "Here are today's key phrases." | PASS |
| full_story_intro | "Now, the full story." | PASS |
| num_one〜five | "One."〜"Five." | PASS(数詞/数字等価判定を個別追加、後述F節) |
| point_one_heading | "First point."(代替文言) | PASS |
| point_two_heading | "Second point."(代替文言) | PASS |
| point_one | Point One本文(内容無変更) | PASS |
| point_two | Point Two本文(内容無変更) | PASS |
| in_one_line | In One Line本文(内容無変更) | PASS |
| kp1_ja〜kp5_ja | Key Phrase日本語meaning(内容無変更) | PASS |

## F. 発見した技術的問題(2件、記事専用の局所対応、共通moduleは無変更)

1. **数詞/数字のASR不一致**: Azure STTが発話された"One."を数字表記
   "1."へ正規化して書き起こすため、`er003_audio_tts_asr_safety.
   validate_asr_match`の単語一致検証が毎回不一致になった。共通module
   自体は変更せず、この記事専用スクリプト内に「数詞⇔数字」の等価性
   のみを許容するローカル判定関数を追加して対応した(過剰正規化を
   避けるため、対象は1〜5の数詞のみ)。
2. **"Point One."/"Point Two."の小数点誤読**: C節参照。

## G. Regression Test

既存回帰テスト37件、全PASS(`er003_test_audio_tts_asr_safety.py`+
`er003_test_b1_scaffold_audio_01.py`)。

## H. Full Audio

- 総尺: **394.332秒(6分34秒)**(修正前383.96秒から、Point見出し2件
  +pause分だけ増加)
- clipping: なし(peak 0.95)
- 日本語残存Audit: Key Phrase訳(5件)以外0件
- head/tail cut: 全21新規segment確認、問題なし

## I. Artifact

既存のBlind Listening Artifactを更新した(同一URL)。View 1(試聴前)
は変更なし。View 2(試聴後)に「Voice Allocation」セクションと
「"Point One."/"Point Two."が実現できなかった理由」の説明を追加した。

URL: https://claude.ai/code/artifact/701978f4-0a54-489e-a766-6cdeba8d91d7

## J. Production非変更確認

- Research内容・Fact Ledger・Full Story本文・Preview本文・Key Phrase
  本文・Key Phrase日本語訳・Comment 1〜4本文・Point One/Two本文・In
  One Line本文・B1 Scaffold構造・Number Treatment・記事angle: いずれも
  無変更
- SFX・Intro/Outro構造・segment order・post-processing・volume
  normalization・transition philosophy: いずれも無変更
- `er003_audio_tts_asr_safety.py`等の既存共有module: 無変更(数詞等価
  判定はこの記事専用スクリプト内のローカル関数として追加)
- CURRENT_SPEC.md・DECISION_LOG.md: 無変更

## K. Git

commit/push結果は、本報告の送付メッセージ末尾を参照。

## 対象ファイル一覧

| ファイル | 内容 |
|---|---|
| `er003_v1_sing01_voice01_generate.py`(新規) | Charon新規生成(13英語+5日本語) |
| `er003_v1_sing01_voice01_labels_fix.py`(新規) | 数詞ラベル(One.〜Five.)個別修正 |
| `er003_v1_sing01_voice01_labels_v2.py`(新規) | Point見出し代替文言生成 |
| `er003_v1_sing01_assemble_v2_generate.py`(新規) | Voice再配置後のFull Audio組み立て |
| `ER-003-B1-NOVEL-AUDIO-01-VOICE-01_REPORT.md`(新規) | 本報告書 |

## 受入条件チェック

| # | 条件 | 結果 |
|---|---|---|
| 1 | Welcome/Topic intro = Charon | 済 |
| 2 | Preview = Aoede | 済 |
| 3 | Key Phrase English = Aoede | 済 |
| 4 | Key Phrase Japanese = Charon | 済 |
| 5 | Full Story Part 1/2 = Aoede | 済 |
| 6 | Comment 1〜4 = Charon | 済 |
| 7 | Point One/Two = Charon | 済 |
| 8 | Point One本文直前に見出し追加 | 済(代替文言"First point."、C節で報告済み) |
| 9 | Point Two本文直前に見出し追加 | 済(代替文言"Second point."、C節で報告済み) |
| 10 | In One Line/OutroのNavigator部分がCharonとして整合 | 済(In One Line=Charon、Outroは非音声SFXのため対象外) |
| 11 | 記事本文・Fact・Scaffold本文変更なし | 済 |
| 12 | Key Phrase E→J→E構造維持 | 済 |
| 13 | Key Phrase以外の日本語spoken content = 0 | 済 |
| 14 | 再生成segmentのASR validation PASS | 済(21件全件) |
| 15 | head/tail cutなし | 済 |
| 16 | Full Audio再assemble | 済(394.332秒) |
| 17 | 回帰テストPASS | 済(37件) |
| 18 | Production未変更 | 済 |
| 19 | commit/push/git status報告 | 本報告書末尾参照 |

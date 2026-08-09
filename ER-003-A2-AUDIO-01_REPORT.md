# ER-003-A2-AUDIO-01 実行報告(A02 A2構造支援版 音声プロトタイプ)

**管理ID: ER-003-A2-AUDIO-01**
**実施日: 2026-08-09**
**ステータス: `PROTOTYPE / UNDER_EVALUATION`(CURRENT_SPECへは未反映、ユーザー試聴待ち)**

## 1. 使用した最新台本ファイル

[ER-003-A2-STRUCT-03_A02_INTEGRATED_SCRIPT.md](ER-003-A2-STRUCT-03_A02_INTEGRATED_SCRIPT.md)
(ER-003-A2-STRUCT-05でIn One Lineへ補足2文を反映した最新版)。Full Story
Part1/2・Point One/Two・In One Line中心文は、手入力による文字化け
(カーリークォート等)を避けるため、`er003_output/a2_p1_r3/A02/
a2_article_raw.md`(A2-03確定本文)からプログラムで直接抽出した
(`er003_a2_article.split_article_sections`を再利用)。日本語Comment
1〜4とIn One Line補足2文はSTRUCT-03/05の確定文言をそのまま使用した。

## 2. 使用TTS model / voice

- 日本語(Comment 1〜4): `gemini-3.1-flash-tts-preview` + Aoede(既存Preview方式と同一)
- 英語(Full Story Part1/2・Point One/Two・In One Line): `gemini-2.5-pro-preview-tts` + Aoede(既存B1本編・Key Phrase Component方式と同一)

いずれも`er003_b1_p9a_audio.py`の`generate_narration_snippet`(既存の
確立済み関数、変更なし)が言語に応じて自動選択する組み合わせをそのまま
使用した。

## 3. 日本語CommentのTTS条件

`er003_v1_repro01_main_generate.generate_narration_snippet_verified_strict`
(既存のstrict ASR検証、A01/A02のmeaning_X等と同一関数)を再利用。
代表語句による部分一致+ASR文字数上限の二重検証、最大6試行。新規の
演出・特殊instructionは追加していない。

## 4. 英語TTS条件

同じく`generate_narration_snippet_verified_strict`を使用。話速変更・
新規style指定は一切行っていない(既存の`ENGLISH_STYLE_PREFIX`+Aoede+
gemini-2.5-pro-preview-tts)。B1で確立した凍結設定をA2用の新規テキスト
にそのまま適用した。

## 5. ポーズ設定

| 切替 | 長さ | 理由 |
|---|---|---|
| 英語→日本語Comment | 1.0秒 | 言語切替の認識しやすさ |
| 日本語Comment→英語 | 0.8秒 | 同上 |
| Point One→Point Two(同一言語) | 0.5秒 | 既存慣例と同じ値を流用 |
| In One Line→Outro | 0.5秒 | 既存慣例と同じ値を流用 |

共通値2種(1.0秒/0.8秒)+既存流用1種(0.5秒)の、ごく少数のルールで
組んだ(記事個別の手調整は行っていない)。

## 6. 既存Transitionの扱い

Intro/notification(3箇所)/Outro/サービス共通ナレーション(Welcome・
Preview intro・Point解説・Key Phrases intro・Full story intro)は、
B1のA02組み立て([er003_v1_repro01_main_generate.py](er003_v1_repro01_main_generate.py))
と全く同じ実体(同じ音声ファイル)をそのまま再利用した。Preview・Key
Phrase Component(5件)・meaning_1-5もB1で承認済みの既存音声をそのまま
使用し、新規生成していない。

## 7. 新規効果音を入れていない確認

日本語Comment 1〜4の前後には、無音ポーズのみを挿入し、新規のTransition
効果音は追加していない(5節参照)。既存のnotification効果音は、B1の
Full Story内部にあった2箇所の挿入(notification2、Today's Points直前・
In One Line直前)を、今回のA2構成では**再配置していない**(Comment3・
Comment4がその構造的な合図の役割を代替するため)。これは今回の判断
であり、必要であればユーザー指示で復元できる。

## 8. 全パートタイムライン

| # | Part | Start(s) | Duration(s) |
|---|---|---:|---:|
| 1 | Intro | 0.000 | 10.736 |
| 2 | Welcome | 10.736 | 2.111 |
| 3 | Topic intro | 13.347 | 5.371 |
| 4 | Japanese title | 19.368 | 9.120 |
| 5 | Notification 1 | 28.988 | 2.040 |
| 6 | Preview intro | 31.428 | 1.451 |
| 7 | Point explanation | 33.529 | 1.220 |
| 8 | Preview | 35.249 | 19.940 |
| 9 | Notification 2 | 55.689 | 2.040 |
| 10 | Key phrases intro | 58.129 | 1.891 |
| 11 | Key Phrase 1 | 60.520 | 6.553 |
| 12 | Key Phrase 2 | 67.073 | 6.093 |
| 13 | Key Phrase 3 | 73.166 | 6.773 |
| 14 | Key Phrase 4 | 79.939 | 7.593 |
| 15 | Key Phrase 5 | 87.532 | 8.193 |
| 16 | Notification 3 | 95.725 | 2.040 |
| 17 | Full story intro | 98.165 | 1.871 |
| 18 | **Comment 1** | 101.036 | 5.520 |
| 19 | **Full Story Part 1** | 107.356 | 48.031 |
| 20 | **Comment 2** | 156.386 | 11.640 |
| 21 | **Full Story Part 2** | 168.826 | 22.551 |
| 22 | **Comment 3** | 192.377 | 14.540 |
| 23 | **Point One** | 207.717 | 33.511 |
| 24 | **Point Two** | 241.728 | 33.071 |
| 25 | **Comment 4** | 275.799 | 13.560 |
| 26 | **In One Line** | 290.159 | 13.611 |
| 27 | Outro | 304.270 | 6.144 |

(ポーズ区間は上表の「次パート開始時刻との差」として省略。詳細は
`er003_output/a2_audio_01/A02/audit/timeline.json`に全区間を記録済み)

## 9. Full Story Part 1/2の長さ

Part 1: 48.031秒(107語)。Part 2: 22.551秒(63語)。B1本編の合計相当は
約70.6秒。B1既存の連続Full Story本編(A02、約166秒)より大幅に短いのは、
A2言語仕様(平均11語以下等)による簡略化と、Point One/Twoをここでは
含まないため(B1は本編1本にPoints・In One Lineまで含む構成)。

## 10. Comment 1〜4の長さ

Comment 1: 5.520秒。Comment 2: 11.640秒。Comment 3: 14.540秒。
Comment 4: 13.560秒。合計45.26秒(全体310.4秒の約14.6%)。

## 11. In One Line 3文の長さ

13.611秒(中心1文+補足2文、合計195文字相当)。

## 12. 完成音声総尺

**310.414秒(5分10秒)**。参考: B1のA02完成版は269.902秒(4分30秒)。
Comment4件の追加(約45秒)+Points/In One Lineの構成変更により、
B1より約40秒長くなった。

## 13. ASR / content QA結果

### 13-1. 個別segment(9件)のstrict ASR検証

9件中7件は初回試行(1回)でsubstring一致+長さ検証の両方に合格した。
2件(comment_3、point_two)は、ASRの**数字表記ゆれ**により部分一致
条件に不一致が生じたが、目視で診断した結果、TTS内容自体は正常と判断した
(下記15節参照)。

### 13-2. 完成音声全体のASR全文確認

Azure STT連続認識(en-US/ja-JP)で全文確認した。**Welcome〜In One Line
まで、期待した内容が全て欠落なく含まれていることを確認した**(構造・
Comment・Full Story Part1/2・Point One/Two・In One Line3文、いずれも
順序通り検出)。診断過程で1つの技術的な問題を発見・解決した(14節参照)。

## 14. 診断過程で発見した技術的問題(ASR確認ツールのtimeout)

初回のASR全文確認で、Comment3以降(約192秒以降)の内容が一切含まれない
不完全な結果が返った。原因を調査した結果、共有の診断関数
`er003_b1_p4_audio.get_full_text_via_azure_stt_continuous`の
デフォルト引数`timeout_seconds=90.0`(既存コード、B1時代から不変)が、
今回の310秒という長い音声に対して短すぎたためと判明した。加えて、
timeout発生時に`stop_continuous_recognition()`を呼ぶと`session_stopped`
イベントが直後に発火し、`done["flag"]`がTrueになるため、実際には
timeoutで打ち切られたにもかかわらずエラーとして報告されず、**部分的な
結果が正常結果として返ってしまう**という、この関数の既存の潜在的な
制限も併せて確認した。

この関数は「境界決定には使わず、内容の診断用途のみに使う」と明記された
診断専用ツールであり、共有モジュールへの変更は行わず、**呼び出し側で
`timeout_seconds`引数に十分な値(300秒)を渡す**ことで対処した(関数の
既存引数を使っただけで、モジュール自体は無変更)。再実行の結果、全文が
正しく取得できた。

## 15. hallucination有無

**hallucinationは検出されなかった。** 完成音声全体のASR全文確認で、
9個のsegmentすべての内容が過不足なく含まれていることを確認した
(無関係な内容の混入・内容の欠落のいずれも検出されなかった)。

2件のASR不一致(comment_3、point_two)はhallucinationとは別種の事象と
判断した。

- **comment_3**: 期待した部分一致語句「2つの実験」に対し、ASRは
  「二つの実験」(漢数字)と書き起こした。全文を確認すると、それ以外の
  内容はComment3の確定文言と完全に一致しており、数字の表記(算用数字/
  漢数字)がASR側で正規化された結果と判断した。TTS音声は正常。
- **point_two**: 期待した部分一致語句"seven in ten children"に対し、
  ASRは"7 in 10 children"(算用数字)と書き起こした。また見出し
  "Point Two:"がASRで"point two"または場合により省略されるなど、
  見出し部分の書き起こしにも軽微な揺れが見られた。それ以外の内容は
  Point Twoの確定文言と一致しており、TTS音声は正常と判断した。

いずれも過去に確認された「ASR homophone/表記ゆれ」パターン
(ADD03 meaning_3の「航行」→「高校」と同系統、ただし今回は同音異義語
ではなく数字表記の正規化)であり、TTS側の不具合を示すものではないと
判断した。**ただし、この判断は機械的な突き合わせによるものであり、
最終確認はユーザー試聴に委ねる**(音声内で該当箇所: Comment 3は
約192秒、Point Twoは約242秒付近)。

## 16. MFA / boundary修正有無

**MFAは使用していない。** 今回はB1のように1本の連続音声を後から編集
(挿入・削除)する構成ではなく、9個のsegmentを個別に生成し、無音ポーズで
接続する構成のため、MFAによる境界特定・編集は不要だった。既存の
notification2挿入・タイトル除去等、B1本編に対するMFA編集はB1側の資産
として既に完了済みのものをそのまま再利用しており、今回新たなMFA作業は
発生していない。

## 17. 手動修正有無

**手動修正なし。** 生成された9個のsegmentは、2件のASR注記(15節)を除き
すべて機械検証に一発で合格し、音声波形やテキストへの手動編集は行って
いない。

## 18. ユーザー確認前の機械QA判定

| QA項目 | 結果 |
|---|---|
| 個別segment ASR検証(9件) | 7件合格、2件はASR表記ゆれと判断の上採用(15節) |
| 完成音声全体のASR全文確認 | 欠落・幻覚なし、全パート内容一致 |
| clipping | 検出なし(peak 0.899) |
| 構成順序(11パート) | 正しい順序で接続済み(タイムラインで確認) |
| Full Story Part1/2の順序 | 逆転なし |
| In One Line補足2文 | 欠落なし(3文とも音声化・ASR確認済み) |
| Outroまでの連結 | 完了 |
| プロジェクト全体回帰テスト | 1660件全合格(コード変更は新規スクリプトのみ、既存凍結モジュールは無変更) |

**機械QAは全て合格、または合格相当と判断した。これは音質・自然さ・
「Commentを挟むことで理解しやすくなったか」等の主観評価を意味しない。
最終判断はユーザーの通し試聴に委ねる。**

## 19. 出力音声ファイル

- WAV: `er003_output/a2_audio_01/A02/assembled/English_Your_Way_A2_A02.wav`
- MP3: `er003_output/a2_audio_01/A02/assembled/English_Your_Way_A2_A02.mp3`
- 試聴用Artifact: (チャット内リンク参照)

## 20. 作成・変更ファイル

- 新規: [er003_v1_a2_audio_01_generate.py](er003_v1_a2_audio_01_generate.py)(A2音声生成・組み立てスクリプト)
- 新規: `er003_output/a2_audio_01/A02/narration/*.wav`(新規segment9件)
- 新規: `er003_output/a2_audio_01/A02/assembled/*.wav`, `*.mp3`
- 新規: `er003_output/a2_audio_01/A02/audit/*.json`, `*.txt`(検証記録・タイムライン・ASR全文)
- 新規: 本レポート
- B1既存資産(`er003_output/b1_p9a/A02/`配下)・既存スクリプト
  (`er003_v1_repro01_main_generate.py`、`er003_b1_p9a_audio.py`等)は
  一切変更していない
- A01・ADD03の音声化は行っていない

## 21. テスト結果

プロジェクト全体回帰テスト: **1660件全合格**。既存の凍結モジュールへの
変更は行っていない(新規スクリプト1本の追加のみ)。

## 22. Git status

音声ファイル(`.wav`/`.mp3`)は`.gitignore`により追跡対象外(プロジェクト
方針どおり)。コード・監査JSON・レポートのみをcommit対象とする。

## 23. push未実行確認

**pushは実行していません。**

## 参照元

[PROJECT_INDEX.md](PROJECT_INDEX.md)、[OPEN_ITEMS.md](OPEN_ITEMS.md)、
[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)、
[ER-003-A2-STRUCT-03_A02_INTEGRATED_SCRIPT.md](ER-003-A2-STRUCT-03_A02_INTEGRATED_SCRIPT.md)、
[ER-003-A2-STRUCT-05_REPORT.md](ER-003-A2-STRUCT-05_REPORT.md)

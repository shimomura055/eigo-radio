# ER-003-B1 引き継ぎドキュメント(新チャット用)

> **[ER-PM-001、2026-08-09追記] 本文書の役割について**
> このファイルは今後、**直近の作業再開用**(現在地・直近完了Task・作業中
> Task・次Action・blocker・最新commit)としてのみ使用する。仕様の一次
> 情報源としては扱わない — 現在のサービス仕様は[CURRENT_SPEC.md](CURRENT_SPEC.md)、
> 決定理由は[DECISION_LOG.md](DECISION_LOG.md)、過去の試行錯誤は
> [HISTORY_INDEX.md](HISTORY_INDEX.md)を参照すること。まずは
> [PROJECT_INDEX.md](PROJECT_INDEX.md)から辿ることを推奨する。
> 以下の本文(2026-07-27作成、P3〜P6系の詳細な経緯)は**過去の作業ログ
> として保持**するが、新規更新時は上記の軽量フォーマットへ段階的に
> 移行する([OPEN_ITEMS.md](OPEN_ITEMS.md) OPEN-12参照)。

作成日: 2026-07-27
直前のHEAD: `90d7bb9`(ER-003-B1-P6B Stage1、未push)

このファイルは、A01のListening Preview音声(日本語ナレーション+英語Key
Phraseの埋め込み)を作る一連の検証(ER-003-B1)を、新しいチャットで
中断なく引き継ぐためのものです。新チャットの冒頭でこのファイルを読めば、
経緯を再説明する必要はありません。

---

## 1. 目的(そもそも何を作っているか)

記事A01のListening Preview音声を作る。構成は「日本語ナレーションの中に、
5箇所の英語Key Phrase(shot on target / take players off / a narrow lead /
close the door to the final / stoppage time)を自然な発音でそのまま
埋め込む」というもの。

課題は一貫して2つ:

1. **日本語TTSの声質・原稿忠実性**をどう保つか(TTSをchunk分割すると声質が
   ズレたり、語句が欠落したりする)
2. **英語Key Phraseの前後の日本語音節を壊さずに**どう置換・接続するか
   (助詞の「を」「へ」「という」などを誤って削ってしまう問題)

## 2. これまでの経緯(何を試して何が却下されたか)

時系列順。全て `er003_output/b1_p4/`〜`b1_p6b/` 配下に成果物と指示書が
保存されている。

| Stage | 試した方式 | 結果 |
|---|---|---|
| P4 | markerとして「合図」を使用、初回パイプライン | marker検出に問題あり |
| P4A | P4のTTS入力を監査、marker4を修正 | 部分修正 |
| P4B | chunk分割生成、marker「合図」 | **STOP**: ASRが「合図」を「アイズ」「会津」と誤認識、chunk05で停止 |
| P4C | marker「目印」に変更(単一トークンと確認済み) | 成功。5marker全検出 |
| P4D | 全文ひらがな化+単一TTS callで生成 | 静的検証は成功したが... |
| P4D-AUDIT | ユーザー試聴で「で下げる」「という決断」が音声から欠落と判明 | 監査の結果、前処理は正しく、Gemini TTS生成時の欠落と結論(新規実装なし、調査のみ) |
| P5A | 同じひらがな入力でGoogle Cloud TTS/Azure/Pollyを比較(仮説: エンジン依存かひらがな入力依存か) | 利用可否確認のみ |
| P5B | Google Cloud TTS/Amazon Pollyの認証確認(読み取り専用API、課金なし) | 認証確認のみ、音声合成は未実施 |
| P5B-GCP | ユーザーがADC認証後、Google Cloud TTS(ja-JP-Neural2-B)で実際に生成 | 機械的で不自然な日本語、「何が」の発話誤り |
| P5C | 同じGoogle Cloud TTSで、ひらがなではなく漢字かな交じり入力に変更して検証 | ひらがな入力が原因の一部と示唆されたが、依然として不自然 |
| P6A | 本編(ER-002)の分割・接続方式をコード監査し、4chunkでPreviewに適用 | **不合格**: `shot on target`挿入位置で助詞「を」が不自然に分断、chunk01/02間で声質差 |
| **P6B(現在)** | TTS call数を2回(Macrochunk)に削減+英語置換の除去範囲をRMSでなくMFA境界のみで決定する方式を設計 | **Stage 1(日本語接続)は完了・機械QA全合格。ユーザー試聴確認待ち。Stage 2(英語置換)は未実行** |

### 重要な技術的教訓

- **marker語は単一トークンで、かつ他の語と混同されないひらがな読みを持つこと**
  (「合図」はNG、「目印」はOK)
- **全文ひらがな化は、TTSが語句を省略するリスクを増やす**可能性がある
  (P4D-AUDITで欠落が発生、P5A/P5B-GCP/P5Cでも不自然さが継続)
- **RMS音量ベースの無音検出(`find_speech_bounds`)は、短く静かな日本語token
  (「へ」など)を検出できないことがある**(P6Aで実測: 0.221秒、最大RMS
  0.00119、閾値0.02の約17分の1)。→ **MFA(強制アライメント)が返す
  token境界を直接使えば、RMSより確実**(P6Bで実証済み、実データ回帰
  テストで確認)
- **TTS chunk数を減らすほど声質の不連続リスクは下がるが、ゼロにはならない**
  (4chunk→2chunkで改善するかがP6B Stage1の検証テーマ)
- 複数の異なるTTSエンジンで共通して見られるASRの同音異義語誤変換パターン:
  決勝→結晶、歓喜→寒気、選手→戦士系。これはASR(Azure STT)側の癖であり、
  TTS側の発音ミスではないと判断している。

## 3. 現在の状態(P6B Stage 1)

**ステータス: `STAGE1_REJECTED_BY_USER`(2026-07-27試聴確認済み)**

ユーザー試聴の結果、Stage 1は**不合格**と判定された。理由は2点:

1. Macrochunk A冒頭「前半は**激しい**接触と緊張が続き」の「激しい」が
   「**げきせつな**」と誤発音されている。これは従来「ASR側の同音異義語の
   癖」と誤判断していたが、実聴により**TTS自体の誤発音**と判明した
   (詳細: `er003_output/b1_p6b/A01/audio_validation.md` section 22-1)。
2. Macrochunk AとBの接続部で音質差が引き続き感じられる。TTS call数を
   4回→2回に減らしても声質不連続は解消していない
   (同section 22-2)。

指示書section16の分岐ルールに従い、**Stage 2(英語Key Phrase置換)は
実施しない**。次の対応方針(新方式の検討など)はユーザーと相談してから
決定する段階で、まだ相談・決定していない。

- 2-Macrochunk(Macrochunk A=第1〜2文、Macrochunk B=第3〜4文)でTTS call
  2回のみ実行
- 原稿忠実性QA: 6つの重点語句(選手を交代で下げる/という決断で/守備を
  固め/わずかなリード/最後の数分/何が起きるのでしょうか)すべて完全な形
  でASR検出、欠落なし(類似度0.9806/0.9286)
- 接続無音は0.8秒(本編標準)/0.4秒/0.6秒の3バリエーションを生成済み
  (新規TTS callなし、既存raw音声の再結合のみ)
- **機械QAは全合格。ただしこれは声質・自然さの合格を意味しない**
- Stage 2(MFA境界のみを使う英語Key Phrase置換)は**設計・実装・回帰テスト
  まで完了しているが、実際のStage1音声に対してはまだ実行していない**。
  指示の「最初に日本語接続を評価し、合格した場合のみ英語置換へ進む」に
  従い、**ユーザーのStage1試聴確認を待っている**。

### ユーザー試聴結果(確定・2026-07-27)

0.8秒無音版を試聴した結果、**不合格**。理由は本ファイルsection3および
`audio_validation.md` section22に記載の2点(「激しい」→「げきせつな」の
誤発音、Macrochunk A/B接続部の音質差)。

## 4. 次にやること(新チャットでの最初の分岐)

Stage1は不合格が確定した。指示書section16の分岐ルール:「2-Macrochunk
でも声質差が大きい場合、Geminiの独立生成を自然につなぐ方式はPreview
用途に不適合と判断する」に該当する状況。

**次にやるべきこと**: 新しい方式(別エンジン、単一TTS call+別の欠落
対策、など)をユーザーと相談して検討する。**先回りして新方式を実装しない
こと**(このプロジェクト全体で繰り返し強調されているルール)。まだこの
相談は行っていない。

参考: 誤発音「激しい→げきせつな」は、これまで「決勝→結晶」「歓喜→寒気」
等と同種の「ASR側の同音異義語の癖」として片付けていたパターンと類似の
書き起こしになっていたが、今回はユーザー実聴により**TTS自体の誤発音**と
確認された。今後、新方式を検討する際にはこの種の漢字誤読リスクも
評価観点に含めるべき。

## 8. ER-003-B1-P7A(2026-08-06実施、ユーザー試聴待ち)

Stage1不合格を受け、「新方式をユーザーと相談する」の第一歩として、
まずモデル監査(現行モデルが古い可能性の確認)を実施した。

- P4D/P6A/P6Bはいずれも`gemini-2.5-pro-preview-tts`(ER-002本編の
  凍結仕様)を使用していたことをコード経路+API疎通で確認
  (`er003_output/b1_p7a/A01/audio_validation.md` section2-3)
- 3.1未満だったため、`gemini-3.1-flash-tts-preview`でP4D入力
  (英語5件を目印へ置換した直後の漢字かな交じり原稿、変更なし)を
  単一TTS call(chunk分割なし)で生成
- ASR上は重点語句8件全検出、「目印」5件検出。特に**「激しい接触」が
  正しく検出された**(P6Bで「げきせつな」と誤発音されていた箇所)
- 「決勝→結晶」「歓喜→寒気」の同音異義語パターンのみ差分あり。
  P6Bの教訓を踏まえ、**これをASR側の癖と断定せず**ユーザー試聴での
  確認待ちとしている
- 機械QAは全合格だが、音声品質・自然さの合格は意味しない
- 音声: `er003_output/b1_p7a/A01/raw/A01_p7a_gemini31_single_call.wav`
  (ローカルのみ、.gitignore対象)

**次にやること**: ユーザーがこの3.1単一call音声を試聴し、指示書
(ER-003-B1-P7A)section11-12の合格条件・分岐に従って判定する。
まだ試聴結果を受け取っていない。

## 9. ER-003-B1-P7B-AUDIT(2026-08-06実施)

Stage1不合格を受け、旧モデルの切替経緯を監査した。結論: 「旧モデルで
問題が起き2.5 Proへ切り替えた」という経緯自体、リポジトリの記録
(初回commit2026-07-14以降)からは裏付けられなかった。確認できた唯一の
実問題(日英混在400エラー、ER-003-B1-P3R)はむしろ`gemini-2.5-pro-
preview-tts`自身で発生していた。`gemini-3.1-flash-tts-preview`が過去の
問題の原因だったという証拠は一切ない(そもそも本日のP7A以前に一度も
使用実績がない)。詳細はこのチャットの当該回答を参照(ファイル化して
いない、報告はチャット内のみ)。

## 10. ER-003-B1-P7A(2026-08-06、ユーザー試聴済み・合格)

P7Aの3.1単一call音声をユーザーが試聴し、**合格**と判定された。

- 「激しい」の誤発音なし
- 明確な語句欠落・言い換えなし
- 声質の連続性に問題なし
- 日本語の自然さがPreview用途として許容可能

## 11. ER-003-B1-P7C(2026-08-06実施、ユーザー試聴待ち)

P7A合格raw(`er003_output/b1_p7a/A01/raw/A01_p7a_gemini31_single_call.wav`、
sha256`30162196...`)を固定し、5箇所の「目印」を承認済み英語used form
(shot on target / take players off / a narrow lead / close the door
to the final / stoppage time)へMFA境界のみ(RMS不使用)を根拠に置換。
close the door to the finalは、P4Cの既存Component(`04_close_the_door_
to.wav`)がユーザーから「不自然に分断された」と明示されたため再利用
禁止とし、既に採用済みの方式(2.5 Pro、Aoede)で1件だけ新規生成した
(他4件は既存Componentを流用)。英語前後の実効間隔は0.40秒/0.30秒
(許容差±0.03秒)を全5件で達成。Dynamics3は最終全体へ1回だけ適用。

- 完成版候補: `er003_output/b1_p7c/A01/A01_p7c_gemini31_english_replaced_dynamics3.wav`
  (44.055秒、ローカルのみ、`.gitignore`対象)
- 境界確認clip5件: `er003_output/b1_p7c/A01/clips/`
- 詳細レポート: `er003_output/b1_p7c/A01/audio_validation.md`
- ASR診断で「shot」の誤表記・「へ」の未検出があるが、`p3z`の
  `speech_content_unchanged`検証(サンプル単位比較)により、日本語音声
  自体は一切変更されていないことを構造的に確認済み。ASR側の限界の
  可能性が高いが断定はしていない。
- プロジェクト全体回帰テスト1588件全合格

**ステータス: `PROTOTYPE / NOT_APPROVED`(ユーザー試聴前)**

**次にやること**: ユーザーが完成版候補を試聴し、指示書
(ER-003-B1-P7C)section14の項目・section15の合格条件に従って判定する。
特に「shot on target」前後の聞こえ方と、「stoppage time」直後の「へ」
が自然に残っているかを重点確認してもらう。まだ試聴結果を受け取って
いない。

**P7C試聴結果**: ユーザーから明示的な合否は受け取っていないが、次の
ER-003-B1-P8A指示に進んだため、P7Cは実質的に合格として扱われている。

## 12. ER-003-B1-P8A(2026-08-06実施、ユーザー試聴待ち)

P7C合格Previewを固定し、A01 B1本編(承認済み原稿、過去一度も音声化
されていなかった)を新規生成して接続した。

- B1本編原稿の承認状態が記録上曖昧だったためユーザーに確認し、
  「この原稿で進めてよい」と回答を得た(`b1_article_raw.md`、
  sha256`3a01120e...`)
- 本編音声生成は1回目3回試行が全てQA不合格(`unauthorized_paraphrase`
  、"Argentina captain"→"Argentine captain"等の軽微な言い回し)。
  ユーザーの許可を得て2回目3回試行を実施し、3回目で合格
  (2.5 Pro、凍結仕様、無変更)
- er002_output/A01(ER-002本編、B2レベル)には同じ試合の完成音声が
  存在するが、ユーザーの編集面での却下(`user_evaluation.json`)を
  受けており、内容も別バージョンのため使用していない
- Preview→0.80秒(可聴音間の実効間隔)→本編で接続。crossfade・自動
  音量補正なし。統合後への追加Dynamics3適用なし
- 全体試聴版: `er003_output/b1_p8a/A01/assembled/A01_p8a_preview_plus_main_full_listening.wav`
  (194.638秒、ローカルのみ。P7C修正後の値。旧193.848秒)
- 接続確認clip: `er003_output/b1_p8a/A01/clips/A01_p8a_preview_to_main_transition_clip.wav`
- 詳細レポート: `er003_output/b1_p8a/A01/audio_validation.md`
- PreviewのRMS(0.0910)と本編のRMS(0.0820)に約0.9dB差があるが、
  今回は未補正のまま(音量差の修正は指示書で「別タスク」と明記)
- プロジェクト全体回帰テスト1598件全合格

### P7C無音間隔バグの発覚と修正(2026-08-06、P8A提示後にユーザー指摘)

ユーザーがPreview原稿を見て「意図的なポーズ箇所とその秒数」を尋ね、
提示した内容(marker_2/3/4の英語直前0.40秒)について「短く感じる」と
指摘。独立したRMS再測定で確認したところ、**marker_2/3/4の英語直前の
間隔が実際には約0.15秒しかなかった**(目標0.40秒)ことが判明した。

原因は`er003_b1_p7c_audio.remove_markers_and_insert_components`の
処理順序バグ(中間segmentへの「前markerの後(leading)」調整と「次
markerの前(trailing)」調整を交互に適用しており、leading調整で
segmentの先頭がpadding/trimされた後にtrailing調整が古いサンプル
位置を基準に計算されていた)。全segmentのtrailing調整を先に一括で
行い、その後leading調整を一括で行う2パス方式へ修正した(commit
`b32c6e7`)。新規TTS callなし、既存のP7A raw・既存英語Componentから
再スプライスのみ。

**教訓**: 元のテストは`achieved_*_seconds`/`speech_content_unchanged`
という自己参照的な指標のみを検証しており、ズレた基準点に対しても
内部的に整合するため、このバグを検出できなかった。既知の値から完成
音声内の絶対位置を独立に逆算するテストを追加し、修正前コードに対して
実際に失敗することを確認した。

修正後、P7C・P8Aの両方の成果物(sha256・duration)を更新し、再度
commitした(`b32c6e7`、`c5aaf2c`)。**新しいPreviewファイルは
sha256`111788d6...`、統合版は`304be3b8...`。**

**ステータス: `PROTOTYPE / NOT_APPROVED`(ユーザー試聴前)**

**次にやること**: ユーザーが修正後の全体試聴版を(再度)試聴し、指示書
(ER-003-B1-P8A)section14の項目・section15の合格条件に従って判定する。
特に、今回のバグで影響を受けていたmarker_2/3/4付近のポーズが自然に
なっているか、Preview→本編の移行の自然さ、0.8秒の間隔の長さ、音量差・声質差が
気にならないかを重点確認してもらう。まだ試聴結果を受け取っていない。

## 13. ER-003-B1-P9A(2026-08-07実施、ユーザー試聴待ち)

ER-003-B1シリーズを飛び越えて、番組パッケージング(英語学習Podcast
「English Your Way」の完成版音声)を作成する新規指示があった。
Preview(P7C修正後)・Full Story(P8Aの本編)は無加工のまま再利用し、
新規TTSは発生させていない。

- Intro/notification(効果音、2回使用)/Outroは`C:\Users\tensh\sound\`
  配下の既存mp3をそのまま使用(soundfileでデコード、
  scipy.signal.resample_polyで48kHz/stereoへ内容・速度・ピッチを
  変えずリサンプリングのみ)
- 新規生成は5点のみ: 番組名"English Your Way."/記事タイトル(英語:
  b1_article_raw.mdのタイトル、日本語: 既存承認済みマスター記事
  `master_ja_approved.md`のタイトルをそのまま使用)/セクション案内
  "Here's a quick preview."・"Now, the full story."
  英語は2.5 Pro+ENGLISH_STYLE_PREFIX(英語Key Phrase Componentと同じ
  経路)、日本語タイトルは3.1+JAPANESE_STYLE_PREFIX(Previewと同じ
  経路)
- 全10パートを指定順序・指定ポーズで接続(Intro→番組名→タイトル
  英日→効果音→Preview案内→Preview→効果音→Full Story案内→本編→
  Outro)。Preview・本編はgainも無加工、それ以外の新規素材だけを
  両者の平均RMSへ近づけるスカラー音量調整(Dynamics3等の圧縮は不使用)
- 完成版: `er003_output/b1_p9a/A01/assembled/English_Your_Way_A01.wav`
  (234.6秒≒約3分55秒、48kHz stereo、ローカルのみ)
- 詳細レポート: `er003_output/b1_p9a/A01/audio_validation.md`
- 新規依存として`soundfile`パッケージを`.venv`へpip install(mp3
  デコード用。requirements-ci.txt等の正式反映は未実施、CI対象の
  curated listには本ステージのテストファイルは含まれていない)
- プロジェクト全体回帰テスト1610件全合格

**ステータス: `PROTOTYPE / NOT_APPROVED`(ユーザー試聴前)**

**次にやること**: ユーザーが完成版を試聴し、特に新規ナレーション5点の
声質がPreview/本編から浮いていないか、日本語タイトル選定の妥当性、
音量バランス、全体のテンポ・長さが「毎日複数記事を聞く」用途として
適切かを確認してもらう。まだ試聴結果を受け取っていない。

## 14. ER-003-B1-P9A-R1(2026-08-07実施、ユーザー試聴待ち)

P9Aの完成版に対し、ユーザーから10項目の修正指示があった。

- **重大な発見**: ユーザーが"Now, the full story."周辺に「不要な音声が
  混入している」と指摘。ASRで確認したところ、実際に**TTSが指定テキスト
  と無関係な内容(別記事のような文章)を生成していた**ことが判明
  (48秒に渡るフランスのRPGゲーム解説など)。原因は、英語Key Phrase用
  instruction(`ENGLISH_STYLE_PREFIX`)が文脈のない単独の短いフレーズ
  には不向きで、モデルが指示文自体や無関係な内容を読み上げてしまう
  現象と推定。声・モデルは変えず、instructionだけ最小限のものへ
  差し替えて解消。同種の問題は新設した「ポイント解説」でも発生し、
  同じ手法(ASR検証付き再試行)で解消した
- Previewを英語Key Phraseなしの日本語のみ版へ差し替え(新規作成、
  このプロジェクトに過去存在しなかった)
- Key Phrasesセクションを新設(番号→英語→日本語→英語×5、英語音声は
  P7Cの既存Componentを再利用、新規TTSなし)
- Full Story冒頭のタイトル重複読み上げをMFAで除去(**英語MFAモデルを
  新規ダウンロード**、日本語MFAは既にあったが英語は未導入だった。
  RMSは使わずMFA境界のみ、本文内容は無変更)
- Outro音量をIntroの調整後RMSに一致させるよう再設計

**追加修正(同日、ユーザーから2件の追加指摘)**:
1. "In One Line"セクション内、"...through the gap."と"Argentina will
   now..."の間にMFA実測2.18秒の異常な無音(P8A生成の本編音声に内在、
   同一音声内の他の段落区切りは約0.68秒)。`trim_internal_gap()`を
   新設し0.68秒へ短縮、前後の発話内容は無変更
2. Outro音量がIntroに合わせた後も大きいとの指摘。「聴感上2/3」に
   相当する追加gain(約-5.85dB、経験則: 10dBで聴感ラウドネス2倍/半分)
   をIntro基準の音量へさらに適用(最終RMS 0.04433)

- 完成版(最新): `er003_output/b1_p9a/A01/assembled/English_Your_Way_A01_r1.wav`
  (256.9秒≒約4分17秒、ローカルのみ、sha256`f20b80df...`)
- 詳細レポート: `er003_output/b1_p9a/A01/audio_validation_r1.md`(追加
  修正の内容は冒頭の「追加修正」セクション参照)
- プロジェクト全体回帰テスト1620件全合格

**ステータス: `PROTOTYPE / NOT_APPROVED`(ユーザー試聴前)**

**次にやること**: ユーザーが修正版を試聴し、特に"Now, the full story."
周辺の異常が解消されているか、Full Story冒頭のタイトル重複が解消されて
いるか、Key Phrasesセクションのテンポ、日本語のみPreviewの自然さ、
Outro音量を確認してもらう。まだ試聴結果を受け取っていない。

**添付ファイル再生問題への対応**: ユーザー環境でチャット添付ファイルが
再生できない問題が判明(「Pin as chapter」しか表示されない)。対応として
(1) WAV→MP3変換(47MB→2.7MB)、(2) 音声を埋め込んだHTMLページを
Artifactとして公開(https://claude.ai/code/artifact/a823418e-a0c7-43f1-8590-000108fcd467、
非公開・本人のみアクセス可)。以後の版もこのURLを維持したまま
再公開している(同一ファイルパスで再publish)。

## 15. ER-003-B1-P9A-R2(2026-08-07実施、ユーザー試聴待ち)

ユーザーから2件の追加指示があり対応した。

1. Full Story内2箇所("Today's Match-Turning Points"前、"In One Line"
   前)へ`C:\Users\tensh\sound\notification2.wav`をMFA境界基準で挿入
   (既存notification.mp3と同じセンス: 前0.5秒/後0.4秒、前後の発話
   内容は無変更)
2. Preview(日本語のみ)を既存の半分〜2/3へ短縮(186→109文字、
   31.66秒→20.76秒、65.6%)。**音声生成前に短縮台本をテキストで提示し、
   ユーザーの承認("OKです")を得てから生成**(このプロジェクトの
   「先回りして実装しない」原則を遵守)

Full Story音声への4つの編集(内部無音短縮/挿入2箇所/タイトル除去)は、
P7Cの無音バグの教訓を踏まえ、**時系列で後ろから前へ**の順序で適用した
(前方の編集を先に行うと後段の絶対時刻指定が無効になるため)。

- 完成版: `er003_output/b1_p9a/A01/assembled/English_Your_Way_A01_r2.wav`
  (245.952秒≒約4分6秒、sha256`07acd974...`、ローカルのみ)
- MP3版: 同ディレクトリの`English_Your_Way_A01_r2.mp3`(添付・
  Artifact埋め込み用)
- 詳細レポート(全パートのポーズ一覧表を含む):
  `er003_output/b1_p9a/A01/audio_validation_r2.md`
- プロジェクト全体回帰テスト1623件全合格

**ステータス: `PROTOTYPE / NOT_APPROVED`(ユーザー試聴前)**

### 15.1 追加修正: notification2挿入①の"two"欠落バグ(2026-08-07)

ユーザー試聴で、"England 1–2 Argentina"読み上げ中に"two"が切れて
notification2の効果音が始まってしまうと報告された。

**原因**: "England 1–2 Argentina"はTTSで"England one, Argentina two"の
語順で発話されるが、挿入位置特定のMFAは書字通りの語順("England 1 2
Argentina")を書き起こしとして使っており、数字トークン"1"/"2"が辞書に
無いため整列が乱れ、"argentina"の終了時刻(70.630秒)を誤って直前語の
境界として採用していた。実際の直前語は"two"で、正しい語順で再整列した
結果、終了時刻は70.960秒だった(ASR・波形エネルギーでも裏付け済み)。

**修正**: `er003_v1_b1_p9a_r1_generate.py`の
`INSERT1_PRECEDING_WORD_END_SECONDS`を70.629997→70.960へ修正。旧値へ
戻らないことを確認する回帰テスト`Insert1BoundaryRegressionTests`を追加。
単体テスト14件・全体回帰1623件、全合格。

- 完成版(修正後): `English_Your_Way_A01_r2.wav`
  (246.282秒、sha256`2f581bcf...`)
- commit: `d2aa9e6`(fix: notification2挿入①の"two"欠落バグ修正)

**次にやること**: ユーザーが最新版(Artifactリンク経由)を試聴し、
修正後のnotification2挿入①、notification2挿入②、短縮版Previewの
分かりやすさを確認してもらう。まだ試聴結果を受け取っていない。

## 5. このプロジェクト全体で守るべきルール(必ず継続すること)

- **CLAUDE.mdの説明順序**: 1)何が問題だったか 2)何を変更したか
  3)何が改善されるか 4)リスクや注意点。技術用語には簡単な日本語説明を
  添える。ユーザーはプロジェクト責任者であり実装担当者ではない。
- **Git運用**: 意味のある変更は動作確認後に自動でcommitする。ただし
  **push は原則自動実行しない**(このER-003-B1シリーズでは各stageの
  指示書で明示的に「非対象範囲: push」と繰り返し指定されている)。
  commit報告の最後には、変更ファイルのraw.githubusercontent.com URLを
  添える。
- **段階的検証の原則**: 音声品質の合否は必ずユーザー試聴で判断する。
  機械QA(ASR一致率、marker検出数など)が全合格でも「品質合格」
  「自然さ確認済み」とは判断しない。
- **秘密情報の取り扱い**(Google Cloud TTS/Azure/AWS認証まわりで
  繰り返し明示): APIキーやsecret値をログ・レポート・テスト出力・
  Git管理ファイルに一切出力しない。ユーザーの許可なく新しい恒久的
  アクセスキーを作成しない。サービスアカウントキーファイルの作成を
  要求しない。
- **利用不可なエンジンを勝手に代替エンジンへ変更しない**。利用できない
  理由を報告し、生成可能な候補だけを実行する。
- **不合格になった方式の特定の実装(語句単位の例外辞書追加、chunk数の
  逆戻し、全文ひらがな化への回帰など)を、明示的な指示なしに再導入
  しない**。各stage指示書の「非対象範囲」を必ず確認する。
- **すべての技術的主張は再現可能な証拠に基づかせる**: sha256による
  ファイル同一性証明、MFAのTextGrid境界(ASR/RMSの推測ではなく)、
  実際のAPI呼び出し結果(ドキュメントからの推測ではなく)。

## 6. 主要ファイルの場所(新チャットで最初に読むべきもの)

- 本ファイル: `ER-003-B1_HANDOFF.md`
- 直近の指示書: `er003_output/b1_p6b/A01/instruction/ER-003-B1-P6B_instruction.md`
- 直近の実行報告: `er003_output/b1_p6b/A01/audio_validation.md`
- 直近の構造化メタデータ: `er003_output/b1_p6b/A01/audio_metadata.json`
- P6A(直前段階、比較対象): `er003_output/b1_p6a/A01/`
- 本編(ER-002)の分割・接続方式のコード: `er002_common.py`
  (`build_narration_plan`/`run_tts_content_attempts`/`assemble_audio`)
- P6B用の主要モジュール:
  - `er003_b1_p6a_audio.py`(chunk plan構築、`chunk_end_anchors`引数対応済み)
  - `er003_b1_p6b_audio.py`(2-Macrochunk化ラッパー、MFA境界サンプル変換)
  - `er003_v1_b1_p6b_stage1_generate.py`(Stage1実行スクリプト)
  - `er003_test_b1_p6b_audio.py`(P6A実データを使った回帰テスト含む)
- 再利用され続けている基盤モジュール: `er003_b1_p3w_audio.py`(MFA
  align)、`er003_b1_p3z_audio.py`(無音調整)、`er003_b1_p3u_audio.py`
  (RMS系、marker隣接境界には使わない)、`er003_b1_p4_audio.py`(marker
  span検出)

## 7. 未コミットのその他ファイルについて

このリポジトリには、ER-003-B1シリーズとは無関係な未追跡ファイルが
多数存在する(`er002_output/`、`er003_output/p1/`、`p1b/`、`p2*/`など)。
これらは過去の別stageの作業ディレクトリであり、**P6B commitでは意図的に
含めていない**。新チャットで作業する際も、コミット範囲をP6B(または
その後のP6C以降)関連ファイルのみに限定すること。

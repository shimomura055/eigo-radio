# ER-003-B1-NOVEL-AUDIO-01-VOICE-01〜03 総括レポート

**対象範囲: VOICE-01 → VOICE-02 → VOICE-03(3段階の連続修正)**
**ベース記事: ER-003-B1-NOVEL-AUDIO-01(SING01、AI/Technological Singularity)**
**最終更新: 2026-08-16**
**ステータス: `PROTOTYPE / EXPERIMENT`(N増し検証。Production仕様化はしていない)**
**commit範囲: `ce75195` → `5e38b79` → `d95353a`(いずれも `origin/main` へpush済み)**

このレポートは、完成済みだったER-003-B1-NOVEL-AUDIO-01(SING01)に対して
行った3段階のVoice(話者)修正を、経緯・技術的発見・最終状態を含めて
1つにまとめたものです。記事本文・Fact・B1 Scaffold構造・Production
本体は、この3段階を通じて一切変更していません。

---

## 1. 目的

B1音声のVoice(話者)の役割を明確にし、Listening UX上の区別を安定
させること。

基本方針(VOICE-01で確立):
- **Aoede**: 本文・Listening対象。ニュース記事や物語など、リスナーが
  英語として実際に聞き取る対象となる「正解の英語コンテンツ」を朗読する
  Voice。
- **Charon**: Navigator / Explanation。番組進行、セクションの案内、
  理解支援、ブリッジ、補足説明など、リスナーがコンテンツを理解するのを
  助ける「進行役・解説者」を担当するVoice。

この基本方針自体は3段階を通じて変わっていませんが、「どのセクションが
どちらの役割に該当するか」の解釈は、ユーザーとのやり取りを通じて
2回修正されました(詳細は3節・4節)。

## 2. 3段階の変更概要

| 段階 | commit | 主な変更 |
|---|---|---|
| VOICE-01 | `ce75195` | Aoede/Charonの役割を初めて明確化。21 segmentをCharonへ再配置。Point One/Two本文の直前にspoken heading("Point One."/"Point Two.")を追加しようとしたが技術的制約が判明し、代替文言"First point."/"Second point."を採用 |
| VOICE-02 | `5e38b79` | ユーザー指摘により、Point One/Two(見出し+本文)を「記事本体」として扱い直しCharon→Aoedeへ変更。また、Preview の日本語訳として機能していた"Point explanation"("Here's the point.")がPreview introと内容重複していたため削除 |
| VOICE-03 | `d95353a` | ユーザー指摘により、Preview introがCharonなのにPreview本文がAoedeのままだった不整合を修正し、Preview全体(intro+本文)をCharonへ統一 |

## 3. VOICE-01: 初回のVoice役割再配置

### 3.1 変更内容

以下21 segmentを新規にCharonで生成し直した(既存のAoede音声を上書きせず、
別ファイルとして新規生成):

- Welcome、Topic intro、Preview intro、Point explanation、Key phrases
  intro、Full story intro(Shell案内文6件)
- Key Phrase番号ラベル(One.〜Five.、5件)
- Key Phrase日本語meaning(5件)
- Point One/Two本文、In One Line(3件)
- 新規追加のPoint見出し2件(後述3.3)

Preview本文・Key Phrase英語Component・Full Story Part1/2は、Listening
対象の本文としてAoedeのまま維持した。

明示的な指示リストに無かった項目(Preview intro/Point explanation/Key
phrases intro/Full story intro/番号ラベル)については、独自判断せず
ユーザーに確認したうえで「Charonへ統一」の回答を得てから実施した。

### 3.2 発見した技術的問題(1): 数詞と数字の不一致

Azure STT(音声認識)が、発話された"One."を数字表記"1."へ正規化して
書き起こすため、既存のASR検証ロジック(`er003_audio_tts_asr_safety.
validate_asr_match`)の単語一致チェックが毎回不一致になった。共通
moduleは変更せず、この記事専用スクリプト内に「数詞⇔数字」の等価性
のみを許容するローカル判定関数を追加して対応した(過剰正規化を避ける
ため対象は1〜5の数詞のみに限定)。

### 3.3 発見した技術的問題(2): "Point One."が小数点として発音される

Point One/Two本文の直前にspoken heading("Point One."/"Point Two.")を
追加しようとしたところ、voice・大文字小文字・単体発話/文中埋め込みの
いずれを試しても、TTSモデルが毎回「.1.」「.2.」としか発音・認識
しないことが判明した。

原因調査の結果、英語の"point one"/"point two"は小数の読み方(例:
"3.1"="three point one")と完全に同じ語列であり、TTSモデルが"Point"を
独立した単語ではなく小数点表現の一部として解釈していたことが判明した。

**独自判断で仕様変更せず、ユーザーへ報告・確認**した結果、意味を保ち
つつ字面のみ変える代替文言"First point."/"Second point."を採用する
ことで合意した(ASR検証でEXACT_MATCH、安定して発音・認識されることを
確認済み)。

### 3.4 QA結果

- Full Audio: 394.332秒(6分34秒)、clippingなし
- 日本語残存: Key Phrase訳(5件)以外0件
- 回帰テスト: 37件全PASS
- 再生成21 segment: 全件ASR検証PASS、head/tail cutなし

## 4. VOICE-02: ユーザー指摘による2件の追加修正

VOICE-01完了後、ユーザーから以下2件の指摘を受けた。

### 4.1 指摘(1): Point One/Twoは記事本体なのでAoedeにすべき

> First Pointとsecond pointおよびそれに続く英文はAoede(女性)に変更
> いただけますか。ここはナレーションのあとに続く記事本体だからです。

VOICE-01ではPoint One/Two(見出し+本文)をNavigator役としてCharonへ
変更していたが、ユーザーの指摘を受けてこれを記事本体(Listeningコン
テンツ)として扱い直し、Aoedeへ戻した。Point One/Two本文は、元の
NOVEL-AUDIO-01時点で生成済みだったAoede音声をそのまま再利用した
(再生成不要)。見出し("First point."/"Second point.")のみ新規に
Aoedeで生成し直した。

**自己発見した問題**: 見出しをAoedeで再生成する1回目の試行で、ASR
検証ロジックのチェック漏れ(単語列の先頭一致は確認していたが、末尾の
長さ上限チェックを付け忘れていた)により、"First point."の生成結果に
無関係かつ不適切な内容(hallucination)が含まれていたにもかかわらず、
誤って合格判定してしまうミスがあった。生成直後に自分でASR全文を
確認して発見し、即座に該当ファイルを破棄・長さチェックを追加した
うえで再生成し、hallucination内容が含まれていないことを確認した。

### 4.2 指摘(2): "Point解説"は不要なので削除

> ポイント解説はPreviewに対する日本語訳なので、ポイント解説を英語に
> するとダブルになります。B1の仕様としては不要なので、削除して
> 音声化してください

VOICE-01では旧A2仕様の"ポイント解説"を英語化("Here's the point.")
してCharonのまま残していたが、これは元々Preview(英語)に対する日本語
訳・解説として機能していたセグメントであり、機械的に英語化すると
直前の"Here's a quick preview."(Preview intro)と内容が重複する。
ユーザー指摘を受け、このセグメントをShellから完全に削除した。
Preview introの直後は既存のpause値(0.65秒)をそのまま残し、新しい
pause値は作っていない。

### 4.3 QA結果

- Full Audio: 392.421秒(6分32秒、Point explanation削除分だけ短縮)
- 日本語残存: Key Phrase訳(5件)以外0件
- 回帰テスト: 37件全PASS

## 5. VOICE-03: Previewの声の不整合を修正

VOICE-02完了後、ユーザーから以下の指摘を受けた。

> Here's the quick PreviewはCharonですが、それ以降の実際のPreviewの
> 内容(Today, we're talking about something big...)はAOEDEになって
> います。ここはすべてCharonが正しいと思うので確認の上、修正ください。

Preview intro("Here's a quick preview.")はCharonだったが、直後の
Preview本文がAoedeのままで声が不整合になっていた(VOICE-01でPreview
本文をAoede=Listening対象として維持する判断をしていたことに起因)。
ユーザー指摘を受け、Preview全体(intro+本文)をCharonへ統一した。

Preview本文をCharonで新規生成し、ASR全文確認で内容が正確に読み上げ
られていることを確認した。

### 5.1 QA結果

- Full Audio: **394.231秒(6分34秒)**
- 日本語残存: Key Phrase訳(5件)以外0件
- 回帰テスト: 37件全PASS
- clippingなし(peak 0.95)

## 6. 最終Voice Allocation(VOICE-03時点、現行版)

| セクション | Voice | 備考 |
|---|---|---|
| Welcome | Charon | |
| Topic intro | Charon | |
| Preview intro | Charon | |
| Preview(本文) | **Charon** | VOICE-03で変更 |
| Key phrases intro | Charon | |
| Key Phrase 英語Component(5件) | Aoede | 無変更 |
| Key Phrase 日本語meaning(5件) | Charon | |
| Key Phrase 番号ラベル(One.〜Five.) | Charon | |
| Full story intro | Charon | |
| Comment 1〜4 | Charon | 無変更(元々Charon) |
| Full Story Part 1/2 | Aoede | 無変更 |
| "First point." / "Second point." 見出し | **Aoede** | VOICE-02で変更 |
| Point One / Two(本文) | **Aoede** | VOICE-02で変更 |
| In One Line | Charon | |
| ~~Point explanation~~ | ~~(削除)~~ | VOICE-02で削除 |

## 7. 最終Full Timeline構成

Intro → Welcome → Topic intro → Notification → Preview intro →
Preview(intro/本文ともCharon) → Notification → Key phrases intro →
Key Phrase 1〜5 → Notification → Full story intro → Comment 1 →
Full Story Part 1 → Comment 2 → Full Story Part 2 → Comment 3 →
"First point." → Point One → "Second point." → Point Two → Comment 4 →
In One Line → Outro

(全22音声セクション+pause。詳細タイムラインは
`er003_output/novel_audio_01/SING01/audit/timeline_v4.json`参照)

## 8. 発見した技術的問題のまとめ(横断)

| # | 問題 | 発見段階 | 対応 |
|---|---|---|---|
| 1 | 数詞("One.")がASRで数字("1.")として認識され不一致になる | VOICE-01 | 記事専用スクリプトにローカルな数詞⇔数字等価判定を追加(共通module無変更) |
| 2 | "Point One."がTTSモデルに小数点表現として解釈され発音される | VOICE-01 | ユーザー確認のうえ代替文言"First point."/"Second point."を採用 |
| 3 | ASR検証の長さチェック漏れによりhallucination内容を誤って合格判定 | VOICE-02 | 自己発見・即座に破棄し長さチェック追加のうえ再生成 |
| 4 | "Point解説"がPreview introと内容重複 | VOICE-02(ユーザー指摘) | セグメント削除 |
| 5 | Preview intro/本文でVoiceが不整合 | VOICE-03(ユーザー指摘) | Preview全体をCharonへ統一 |

いずれも既存の共通module(`er003_audio_tts_asr_safety.py`)・Production
本体・記事本文・Fact Ledgerは変更していません。

## 9. Production非変更確認

- 記事本文(Full Story/Preview/Comment/Point/In One Line)・Fact
  Ledger・B1 Scaffold構造・Number Treatment・記事angle: 3段階を通じて
  無変更
- CURRENT_SPEC.md・DECISION_LOG.md・Production本体・共通TTS/ASR
  module: 無変更
- 変更は「どのVoiceで読むか」「Shell内の1セグメントの要否」に限定

## 10. 成果物

- **Blind Listening Artifact**(3回更新、同一URL):
  https://claude.ai/code/artifact/701978f4-0a54-489e-a766-6cdeba8d91d7
- 最終音声: `er003_output/novel_audio_01/SING01/assembled/English_Your_Way_B1_SING01_v4.{wav,mp3}`(394.231秒)
- 各段階の個別報告書:
  - [ER-003-B1-NOVEL-AUDIO-01-VOICE-01_REPORT.md](ER-003-B1-NOVEL-AUDIO-01-VOICE-01_REPORT.md)
  - [ER-003-B1-NOVEL-AUDIO-01-VOICE-02_REPORT.md](ER-003-B1-NOVEL-AUDIO-01-VOICE-02_REPORT.md)
  - VOICE-03は本レポート5節が正式記録(個別ファイルは作成していない)

## 11. Git

| commit | 内容 |
|---|---|
| `ce75195` | VOICE-01: Voice役割再配置+Point見出し追加 |
| `5e38b79` | VOICE-02: Point One/Two=Aoede化+Point explanation削除 |
| `d95353a` | VOICE-03: Preview本文もCharonへ統一 |

いずれも`origin/main`へpush済み。

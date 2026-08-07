# ER-003-B1-P9A 実行報告(英語学習Podcast「English Your Way」完成版音声作成)

**ステータス: `PROTOTYPE / NOT_APPROVED`(ユーザー試聴前)**

## 1. 検証目的

完成済みのPreview(P7C修正後)・本編/Full Story(P8A)を無加工のまま使い、
指定された外部音源(Intro/効果音/Outro)と、新規生成した5点の短い
ナレーション(番組名・記事タイトル英日・セクション案内2件)を、指定
順序・指定ポーズで接続し、英語学習Podcast「English Your Way」の完成版
音声を作成する。

## 2. 使用した既存音声とsha256

| 項目 | path | sha256 |
|---|---|---|
| Preview | `er003_output/b1_p7c/A01/A01_p7c_gemini31_english_replaced_dynamics3.wav` | `111788d635637be7d4edb38d2c45784a5d929144cbf7e68e5e1e3b31c0671168` |
| Full Story(本編) | `er003_output/b1_p8a/A01/body_raw/A01_b1_body_dynamics3.wav` | `d9c71e1fbf6eab45140b8df4271397153a3f8c10fd5f4a55e809978ae36d00e6` |

いずれもP7C(無音間隔バグ修正後)・P8Aで生成済みの、ユーザー試聴待ちの
音声をそのまま再利用した。**新規TTS callは発生していない**(sha256は
組み立てスクリプトが読み込んだ時点のものと完全一致することを
`common.read_wav_float`の直接読み込みで確認済み)。

## 3. 外部音源とsha256

| 項目 | path | sha256 | 元フォーマット |
|---|---|---|---|
| Intro | `C:\Users\tensh\sound\Intro.mp3` | `152c587bb6ba16458673c3cda454c615ac79ce8ad0f9031a509559a521893584` | MP3, 44100Hz, stereo, 10.748秒 |
| Transition(効果音) | `C:\Users\tensh\sound\notification.mp3` | `212d57034ac58ad39e491a8354284c321fd583d14f8fa96bd3c23ad225b7e7a5` | MP3, 48000Hz, stereo, 2.040秒(2回使用) |
| Outro | `C:\Users\tensh\sound\outro.mp3` | `d87b5a8bb1ddd27ee6db3108f952b51d68488f5a56f8ece91a3faca1f521d0fe` | MP3, 48000Hz, stereo, 6.144秒 |

いずれも`soundfile`(libsndfile)でデコードし、内容・速度・ピッチは
変えず、`scipy.signal.resample_poly`による有理数比リサンプリングのみで
48000Hz/stereoへ統一した(タイムストレッチ・ピッチシフトは一切
行っていない)。

## 4. 新規生成した5点のナレーション

**ナレーターはAoede、既存の確立済み経路をそのまま再利用**(新しい
instruction/styleは作っていない)。

| 項目 | テキスト | 言語 | 使用モデル | instruction | path | sha256 | duration |
|---|---|---|---|---|---|---|---|
| 番組名 | "English Your Way." | 英語 | gemini-2.5-pro-preview-tts | 英語Key Phrase Componentと同一(`ENGLISH_STYLE_PREFIX`) | `narration/podcast_name.wav` | `e13f7c3f...` | 1.431秒 |
| 記事タイトル(英語) | "Five Minutes from the Final—Then the Champions Struck" | 英語 | gemini-2.5-pro-preview-tts | 同上 | `narration/english_title.wav` | `8b68fba3...` | 4.231秒 |
| 記事タイトル(日本語) | "あと5分で決勝だった。だが、王者は時計まで味方につけた" | 日本語 | gemini-3.1-flash-tts-preview | Previewと同一(`JAPANESE_STYLE_PREFIX`) | `narration/japanese_title.wav` | `03c685fb...` | 5.600秒 |
| Preview案内 | "Here's a quick preview." | 英語 | gemini-2.5-pro-preview-tts | 英語Key Phrase Componentと同一 | `narration/preview_intro.wav` | `159b6374...` | 1.451秒 |
| Full Story案内 | "Now, the full story." | 英語 | gemini-2.5-pro-preview-tts | 同上 | `narration/full_story_intro.wav` | `9e3589a9...` | 1.391秒 |

### 日本語タイトルの由来

既存承認済みの日本語マスター記事
(`er003_output/b1_p1/A01/master_ja_approved.md`)のタイトル行
「あと5分で決勝だった。だが、王者は時計まで味方につけた」を、
**新規生成せずそのまま使用した**(指示「既存データにある場合はそれを
そのまま使用」に従う)。翻訳チェーン上、この日本語タイトルは
`master_en_natural_source_approved.md`の英語タイトル("Five Minutes
from the Final—Then the Champions Made Time Their Ally")の元になった
ものであり、B1本編の実際のタイトル("...Then the Champions Struck")
はそれをさらに平易化した版であるため、日本語⇄英語タイトルの対応は
完全に1対1ではないが、同じ出来事(終盤の逆転劇)を指しており、内容の
食い違いはない。

### モデル選択の理由(判断の開示)

指示に「既に指定済みのナレーター音声・声質に統一」とあったが、
本ステージで生成する5点はこのPodcast全体で初めて登場する種類の
コンテンツ(番組名・タイトル読み・セクション案内)であり、既存の
「Preview用モデル(3.1)」「本文用モデル(2.5)」のどちらか一方に
機械的に決まるものではなかった。以下の方針で判断した。

- 英語の短いフレーズ(番組名・英語タイトル・セクション案内2件)は、
  英語Key Phrase Component(shot on target等)と役割が近い「短い英語
  フレーズの読み上げ」であるため、その既存経路(2.5 Pro+
  `ENGLISH_STYLE_PREFIX`)をそのまま再利用した。
- 日本語タイトルは、直後に続くPreviewと同じ日本語ナレーションの
  流れの一部として聞かれるため、Previewと同じモデル(3.1)を選んだ。

この判断が意図と異なる場合はご指摘ください。

## 5. Intro/Outro後に追加無音を入れていないことの確認

Intro・Outro(mp3)のデコード後の先頭・末尾サンプル振幅を直接確認した。

| 項目 | 先頭振幅 | 末尾振幅(直前5サンプルの最大絶対値) |
|---|---|---|
| Intro | 0.0 | 0.0 |
| Transition効果音 | 0.0 | 約1.0×10⁻⁷(実質無音) |
| Outro | 0.0 | 約2.9×10⁻⁵(実質無音) |

いずれも音源ファイル自体が自然に無音へ収束しており、追加の無音を挿入
しなくても不自然な切れ方にならないことを確認した(指示「Intro/Outro
終了後に追加の無音時間は入れない」を、根拠を持って実施)。

## 6. 全体構成とタイムライン

| # | パート | 開始 | 終了 | 長さ | 直後のポーズ |
|---|---|---|---|---|---|
| 1 | Intro | 0.000秒 | 10.736秒 | 10.736秒 | 0秒(追加無音なし) |
| 2 | Podcast Name | 10.736秒 | 12.167秒 | 1.431秒 | 0.5秒 |
| 3a | English Title | 12.667秒 | 16.898秒 | 4.231秒 | 0.65秒 |
| 3b | Japanese Title | 17.548秒 | 23.148秒 | 5.600秒 | 0.5秒 |
| 4 | Transition(効果音1回目) | 23.648秒 | 25.688秒 | 2.040秒 | 0.4秒 |
| 5 | Preview Introduction | 26.088秒 | 27.539秒 | 1.451秒 | 0.5秒 |
| 6 | Preview | 28.039秒 | 72.884秒 | 44.845秒 | 0.5秒 |
| 7 | Transition(効果音2回目) | 73.384秒 | 75.424秒 | 2.040秒 | 0.4秒 |
| 8 | Full Story Introduction | 75.824秒 | 77.215秒 | 1.391秒 | 0.7秒 |
| 9 | Full Story(本編) | 77.915秒 | 227.948秒 | 150.033秒 | 0.5秒 |
| 10 | Outro | 228.448秒 | 234.592秒 | 6.144秒 | 0秒(追加無音なし) |

指定順序どおりに全10パートが1回ずつ、欠落・重複なく配置されている
ことを、この積み上げ計算(各パートのサンプル長+指定ポーズ長の
累積)で確認した。

## 7. 音量バランス調整

PreviewとFull Story(本編)は**無加工のまま**(既存の承認済み音声、
gainも一切変更していない)。それ以外(Intro/効果音/Outro/新規
ナレーション5点)は、Preview・Full StoryのRMS平均値(目標RMS=0.0865)
へ近づけるスカラーgain(単純な音量の一律拡大縮小、ダイナミックレンジ
圧縮=Dynamics3は使用していない)を適用した。

| 項目 | 適用gain | 調整後ピーク |
|---|---|---|
| Intro | 0.878倍(減衰) | 0.875 |
| Transition効果音 | 0.596倍(減衰) | 0.606 |
| Outro | 0.649倍(減衰) | 0.476 |
| Podcast Name | 0.755倍(減衰) | 0.528 |
| English Title | 0.916倍(減衰) | 0.641 |
| Japanese Title | 0.853倍(減衰) | 0.597 |
| Preview Introduction | 0.743倍(減衰) | 0.520 |
| Full Story Introduction | 0.449倍(減衰) | 0.314 |

全項目が減衰方向(1.0未満)のgainで、目標ピーク上限0.95を超えるものは
なかった(ピーク超過によるgain頭打ちは発生していない)。詳細:
`er003_output/b1_p9a/A01/audit/gain_report.json`。

## 8. 完成音声の場所

| 項目 | 値 |
|---|---|
| path | `er003_output/b1_p9a/A01/assembled/English_Your_Way_A01.wav` |
| sha256 | `e1320e530acb2bf05e226fe4baea2b9459d11175a7a5aa26fe5a5e6f612703fc` |
| duration | 234.592秒(約3分55秒) |
| sample rate | 48000Hz |
| channels | 2(stereo) |
| peak | 0.888 |
| clipping | 検出なし |

**注意**: `.wav`ファイルは`.gitignore`によりリポジトリには含まれて
いない。ローカルファイルとして存在するので、ユーザーが直接再生する
必要がある。

## 9. 機械QA

| 項目 | 結果 |
|---|---|
| Preview/Full Storyが既存ファイルとsha256一致(無加工) | 合格 |
| Preview/Full Storyへの新規TTS callが0 | 合格 |
| 全10パートが指定順序で1回ずつ存在(欠落・重複なし) | 合格(section6のタイムライン計算で確認) |
| Intro/Outro直後に追加無音を入れていない | 合格 |
| Intro/Outro/効果音の末尾が実質無音でIntro/Outro境界にクリックリスクがない | 合格(section5) |
| 各ポーズが指示範囲内 | 合格(0.5/0.65/0.5/0.4/0.5/0.5/0.4/0.7/0.5秒、指示の範囲内または指定値通り) |
| 音声がdecode可能 | 合格 |
| clippingなし | 合格(peak 0.888 < 1.0) |
| 全体duration が3〜4分程度 | 合格(3分55秒) |

**機械QAは全て合格した。ただし、これは音質・自然さ・Podcastとしての
完成度の承認を意味しない。ユーザー試聴での判断が必須。**

## 10. 作成・変更したファイル

- `er003_b1_p9a_audio.py`(新規): 外部mp3の読み込み・リサンプリング、
  ナレーション生成、gain計算、無音生成の各関数
- `er003_v1_b1_p9a_generate.py`(新規): 組み立てオーケストレーション
  script
- `er003_test_b1_p9a_audio.py`(新規、12件、合成データのみ、実TTS/
  外部mp3呼び出しなし)
- `er003_output/b1_p9a/A01/`配下の成果物一式(`narration/`、
  `audit/`、`assembled/`、`instruction/`、本報告書)
- 依存関係: `soundfile`(mp3デコード用)を新規インストール(pyproject/
  requirements.txt等の変更は未実施、`.venv`へのpip installのみ)

## 11. テスト結果

- `er003_test_b1_p9a_audio.py`(新規12件、合成データのみ): 全合格
- プロジェクト全体回帰テスト(`run_project_regression.py`、
  er0*_test_*.py全探索): **1610件全合格、回帰なし**

## 12. 再実行方法

```
.venv/Scripts/python.exe er003_v1_b1_p9a_generate.py
```

新規ナレーション5点(`narration/`配下)が既に存在する場合は読み込む
だけで新規TTS callは発生しない(ナレーション自体を作り直す場合は
`er003_b1_p9a_audio.generate_narration_snippet`を個別に呼ぶ)。

## 13. 既知のリスク

- 新規ナレーション5点の生成では、一時的なサーバーエラー(500/503/
  timeout/DNS失敗など)が複数回発生し、特に"Now, the full story."は
  6回試行してようやく成功した。診断のため生レスポンスを直接確認した
  結果、内容起因の拒否ではなく、Gemini API側の一時的な不安定さと
  判断した。最終的に使用しているのは各項目1件の成功結果のみ。
- 日本語タイトルの選定(section4)は、既存の承認済みマスター記事の
  タイトルをそのまま使ったが、これはB1記事本文の実際のタイトルとは
  微妙に異なる英語表現("Made Time Their Ally" vs "Struck")に基づく
  ものである。意味は同じ出来事を指しているが、完全な直接対応では
  ない点はご留意ください。
- 音量バランス(section7)は、Preview・Full StoryのRMSを基準にした
  シンプルなgain調整であり、ラウドネス規格(LUFS等)による正式な
  マスタリングではない。
- 新規ナレーション5点の実際の発音の自然さ・Previewとの声質の連続性は、
  ユーザー試聴でのみ確認できる。
- `soundfile`パッケージを新規インストールした(mp3デコードに必須。
  requirements.txt等の正式な依存関係ファイルへの反映は未実施)。

## 14. 指示書の保存先とsha256

| 項目 | 値 |
|---|---|
| path | `er003_output/b1_p9a/A01/instruction/ER-003-B1-P9A_instruction.md` |
| sha256 | `7b45b26ddf3249c03e6392f43d4913bd148df64c36125aa2a8187dc3b6d938c8` |
| 管理ID | ER-003-B1-P9A |
| 指示書からの逸脱 | ポーズ秒数はレンジ指定のため中央付近の値へ固定(0.65秒/0.4秒)。それ以外は指示通り |

## 15. Git status

このレポート作成時点では未コミット。P9A関連ファイルのみをステージして
コミットします。

## 16. push

実行していません。

---

## ユーザーへの確認事項

以下の完成版をご試聴ください。

- [English_Your_Way_A01.wav](assembled/English_Your_Way_A01.wav)(完成版、約3分55秒)

特に以下をご確認ください。

- Intro→番組名→タイトル(英語→日本語)→効果音→Preview案内→Preview→
  効果音→Full Story案内→本編→Outroの流れが自然か
- 新規生成した5点のナレーション(番組名・タイトル2件・案内2件)の
  声質・話し方が、PreviewやFull Storyと不自然に浮いていないか
  (section4の「モデル選択の理由」もあわせてご確認ください)
- 日本語タイトルの選定(section4)が適切か
- 音量バランス(Intro/効果音/ナレーション/Preview/本編/Outro)が
  気にならないか
- 全体の長さ・テンポが「毎日複数記事を聞く」用途として適切か

**機械QAは全て合格していますが、「完成版合格」「公開可能」とは
判断していません。**

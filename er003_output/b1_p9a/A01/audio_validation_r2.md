# ER-003-B1-P9A-R2 実行報告(「English Your Way」Preview短縮+notification2挿入)

**ステータス: `PROTOTYPE / NOT_APPROVED`(ユーザー試聴前)**

## 1. 対応内容

ユーザーから2件の追加指示に対応した。

1. Full Story内の2箇所("Today's Match-Turning Points"見出し直前、"In
   One Line"見出し直前)へ`notification2.wav`を挿入
2. Preview(日本語のみ)の長さを、既存(31.66秒)の半分〜2/3程度に短縮

修正2は、音声作成前に短縮台本をテキストで提示し、ユーザーの承認
("OKです")を得てから音声を生成した。

## 2. Preview短縮

| 項目 | 修正前 | 修正後 |
|---|---|---|
| 文字数 | 186文字 | 109文字 |
| duration | 31.66秒 | **20.76秒**(承認時提示の推定値18.6秒に近い実測値) |
| 現状比 | - | **65.6%**(指示レンジ「半分〜2/3」の上限付近) |

台本(承認済み、変更なし):

> 前半は激しい接触が続き、静かな均衡が保たれます。後半、イングランドは守備を固め、わずかなリードを守ろうとします。しかし後半終了間際、メッシが流れを変え、ついにアディショナルタイムへ。最後の数分、何が起きるのでしょうか。

- 音声: `er003_output/b1_p9a/A01/narration/preview_japanese_only_short.wav`
- モデル: `gemini-3.1-flash-tts-preview`(Previewで採用済み、単一TTS call)
- ASR検証: 台本と完全一致(1回目の生成で合格)

## 3. notification2.wav挿入(Full Story内、2箇所)

英語MFAモデルで、挿入位置直前・直後の単語境界を特定した(既存の
`er003_output/b1_p9a/A01/mfa/_output_en/A01_body_dynamics3.TextGrid`
を再利用、追加のMFA実行なし)。

| 挿入箇所 | 直前の語(終了時刻) | 直後の語(開始時刻) | 元の無音 |
|---|---|---|---|
| "Today's Match-Turning Points"直前 | "argentina"(70.630秒、"England 1–2 Argentina"の末尾) | "today's"(72.480秒) | 1.85秒 |
| "In One Line"直前 | "result"(131.150秒、"...helped decide the result."の末尾) | "in"(132.450秒、"In One Line"の先頭) | 1.30秒 |

挿入方法: 直前語の終了位置で切り、`notification2.wav`(44100Hz/mono、
0.670秒、内容・長さとも無加工)を、前後のポーズとともに差し込んだ
(既存のnotification.mp3挿入と同じセンス: 前0.5秒・後0.4秒)。**前後の
発話内容はサンプル単位で変更していない**
(`before_content_unchanged`/`after_content_unchanged`をコードで確認、
2箇所とも`True`)。

`notification2.wav`挿入により、元々あった1.85秒/1.30秒の自然な無音は、
新しい0.5秒+0.670秒+0.4秒=1.57秒の構成に置き換わっている(挿入前後で
Full Story全体の長さはほぼ変わらない: 2箇所合計で約0.01秒短縮)。

## 4. 編集順序(重要、既存の教訓を踏襲)

Full Story音声には計4つの編集を、MFAで特定した元のbody_dynamics3.wav
上の絶対時刻を基準に適用している。**時系列で後ろにある編集から順に
適用**した(前方の編集を先に行うと、インデックスがずれて後段の絶対
時刻指定が無効になるため。P7Cの無音間隔バグで得た教訓を踏襲)。

1. 内部無音短縮(約139秒地点、2.18秒→0.68秒)
2. notification2挿入(約131秒地点、"In One Line"前)
3. notification2挿入(約71秒地点、"Today's..."前)
4. タイトル除去(約4.86秒地点)

全ての編集について、編集対象区間の前後で発話内容が変更されていない
ことをコードで確認済み。

## 5. 全体構成とポーズ一覧(前回と同様の形式)

**トップレベルの構成(19パート):**

| # | パート | 開始 | 終了 | 長さ | 直後のポーズ |
|---|---|---|---|---|---|
| 1 | Intro Music | 0.000秒 | 10.736秒 | 10.736秒 | 0秒(追加無音なし) |
| 2 | "Welcome to English Your Way." | 10.736秒 | 12.847秒 | 2.111秒 | 0.5秒 |
| 3 | "Today's topic is [英語タイトル]." | 13.347秒 | 18.538秒 | 5.191秒 | 0.65秒 |
| 4 | 日本語タイトル | 19.188秒 | 24.788秒 | 5.600秒 | 0.5秒 |
| 5 | Transition Sound(1回目、notification.mp3) | 25.288秒 | 27.328秒 | 2.040秒 | 0.4秒 |
| 6 | "Here's a quick preview." | 27.728秒 | 29.179秒 | 1.451秒 | 0.65秒 |
| 7 | 「ポイント解説」 | 29.829秒 | 31.049秒 | 1.220秒 | 0.5秒 |
| 8 | Preview(日本語のみ、**短縮版**) | 31.549秒 | 52.309秒 | **20.760秒** | 0.5秒 |
| 9 | Transition Sound(2回目、notification.mp3) | 52.809秒 | 54.849秒 | 2.040秒 | 0.4秒 |
| 10 | "Here are today's key phrases." | 55.249秒 | 57.140秒 | 1.891秒 | 0.5秒 |
| 11-15 | Key Phrase 1〜5(各: 番号0.4秒英語0.4秒日本語0.4秒英語0.8秒) | 57.640秒 | 90.465秒 | 計32.825秒 | (各ブロック内に含む) |
| 16 | Transition Sound(3回目、notification.mp3) | 90.465秒 | 92.505秒 | 2.040秒 | 0.4秒 |
| 17 | "Now, the full story." | 92.905秒 | 94.775秒 | 1.870秒 | 0.7秒 |
| 18 | Full Story(タイトル除去・内部編集込み、詳細下記) | 95.475秒 | 239.308秒 | 143.833秒 | 0.5秒 |
| 19 | Outro Music | 239.808秒 | 245.952秒 | 6.144秒 | 0秒(追加無音なし) |

**Full Story内部(パート18の中、絶対位置):**

| 内部イベント | 絶対位置(秒) | 内容 |
|---|---|---|
| 本文開始("On July 15, 2026...") | 95.475 | タイトル除去後の第1文 |
| notification2挿入(1回目) | 161.915 - 162.585 | "...England 1–2 Argentina" の後、"Today's Match-Turning Points" の前(前後ポーズ0.5秒/0.4秒込み) |
| notification2挿入(2回目) | 222.155 - 222.825 | "...helped decide the result." の後、"In One Line" の前(前後ポーズ0.5秒/0.4秒込み) |
| 本文終了("...final five minutes.") | 239.308 | |

全体duration: **245.952秒(約4分6秒)**

## 6. 完成音声の場所

| 項目 | 値 |
|---|---|
| path(WAV) | `er003_output/b1_p9a/A01/assembled/English_Your_Way_A01_r2.wav` |
| sha256(WAV) | `07acd9744ea0ecff223edf78c28cb00e22a7dcbdbf0650069d466d22c2854f2c` |
| path(MP3、添付用) | `er003_output/b1_p9a/A01/assembled/English_Your_Way_A01_r2.mp3` |
| sha256(MP3) | `e94bb48f3ab54da177095d9180644877c79db7f37a20960187bb68ad9f52ae21` |
| duration | 245.952秒(約4分6秒) |
| sample rate | 48000Hz |
| channels | 2(stereo) |
| peak | 0.934 |
| clipping | 検出なし |

## 7. 機械QA

| 項目 | 結果 |
|---|---|
| Previewの短縮率が指示レンジ(50%〜67%)内 | 合格(65.6%) |
| Preview短縮版がASRで台本と一致 | 合格 |
| notification2挿入2箇所とも前後の発話内容が無変更 | 合格(コードで確認) |
| notification2挿入2箇所とも指定通りの前後ポーズ(0.5秒/0.4秒) | 合格 |
| Full Story内の編集順序が正しい(後方から前方へ) | 合格 |
| 全体duration・構造がASRで確認可能 | 合格(通し2回のASR呼び出しで全区間を確認) |
| clippingなし | 合格(peak 0.934) |

**機械QAは全て合格した。ただし音質・自然さ・完成度の承認を意味しない。
ユーザー試聴での判断が必須。**

## 8. 作成・変更したファイル

- `er003_b1_p9a_audio.py`(更新): `load_mono_at_rate`/
  `insert_sound_at_internal_gap`を追加
- `er003_v1_b1_p9a_r1_generate.py`(更新): notification2挿入2箇所・
  短縮Preview使用・出力ファイル名をr2へ変更
- `er003_test_b1_p9a_r1_audio.py`(更新、3件追加): 挿入ロジックの
  回帰テスト
- `er003_output/b1_p9a/A01/`配下の新規成果物(`narration/
  preview_japanese_only_short.wav`、`source/
  japanese_only_preview_script_short.txt`、`audit/`追加分、
  `asr/r2_full_asr.txt`、本報告書)

## 9. テスト結果

- `er003_test_b1_p9a_r1_audio.py`(13件、合成データのみ): 全合格
- プロジェクト全体回帰テスト(`run_project_regression.py`、
  er0*_test_*.py全探索): **1623件全合格、回帰なし**

## 10. 再実行方法

```
.venv/Scripts/python.exe er003_v1_b1_p9a_r1_generate.py
```

## 11. 既知のリスク

- Preview短縮は65.6%で、指示レンジ「半分〜2/3」の上限付近。より短く
  したい場合は台本をさらに削る必要がある。
- notification2挿入により、元々あった自然な間(1.85秒・1.30秒)を
  0.5秒+効果音+0.4秒(計1.57秒)へ置き換えている。聴感上の印象は
  試聴でのみ判断できる。
- 機械QA・ASR確認は全て「診断情報」であり、完成度の承認を意味しない。

## 12. Git status

このレポート作成時点では未コミット。関連ファイルのみをステージして
コミットします。

## 13. push

実行していません。

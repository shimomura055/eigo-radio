# ER-003-B1-P9A-R1 実行報告(「English Your Way」完成音声の修正)

**ステータス: `PROTOTYPE / NOT_APPROVED`(ユーザー試聴前)**

## 追加修正(初版公開後にユーザー指摘で発覚、2件)

初版(本報告書の元の内容)公開後、ユーザーから以下2点の追加指摘があり、
対応した。完成音声・sha256・durationは対応後の値に更新済み。

### A. Full Story内の異常に長い無音(約2.18秒)

指摘: 引用文("England tried to close the door to the final. Messi
slipped two keys through the gap.")と、次の文("Argentina will now
face Spain...")の間のポーズが約2秒あり長い。

調査: MFA(英語モデル)で正確な時刻を測定したところ、"gap."の終了が
138.95秒、"Argentina"の開始が141.13秒で、**実測2.18秒**の無音だった。
これはP8Aで生成された本編音声(2.5 Pro、凍結仕様)自体に内在していた
異常であり、今回の統合作業で新たに生じたものではない。同一音声内の
他の段落区切り(例:"...quiet first half."と"Neither team..."の間)を
同じ方法で測定すると約0.68秒であり、2.18秒は明らかに逸脱していた。

対応: `er003_b1_p9a_audio.trim_internal_gap`(新規関数)で、この無音
区間だけを0.68秒(同一音声内の他の段落区切りの実測値)へ短縮した。
前後の発話内容はサンプル単位で変更していない
(`before_content_unchanged`/`after_content_unchanged`をコードで確認)。

### B. Outro音量の追加調整

指摘: Introと音量を揃えたはずのOutroが、まだ大きく感じる。人間の聴覚的
に2/3程度まで下げてほしい。

対応: Introの調整後RMSに一致させた状態から、さらに追加のgainを適用した。
「音量が2/3に聞こえる」という聴感上のラウドネス比を、audio engineering
で広く使われる経験則(10dBの変化で聴感上のラウドネスがおよそ2倍/半分に
なる)で近似すると、2/3のラウドネス比は約-5.85dB(線形gain換算で
約0.510倍)に相当する。この追加gainをIntro基準の音量へさらに掛け合わせた。

| 項目 | 値 |
|---|---|
| Intro基準に合わせた時点のOutro RMS | 0.08693 |
| 追加の聴感調整gain | 0.510倍(約-5.85dB) |
| 最終的なOutro RMS | 0.04433 |
| 最終的なOutroピーク | 0.244(クリッピングの心配なし) |

この計算根拠(-5.85dB)は経験則に基づく近似であり、実際の聴感が
「ちょうど2/3」になっているかはユーザー試聴でのみ確認できる。狙った
数値と体感が異なる場合は、追加で調整する。

いずれの修正も、既存テスト・回帰テストへ新規テスト2件を追加した上で
プロジェクト全体回帰テスト**1620件全合格**を確認済み。

---

## 1. 修正目的

先に作成した完成版(`English_Your_Way_A01.wav`)について、ユーザーからの
10項目の修正指示に対応する。特に、①Previewから英語Key Phraseを除いて
日本語のみにし、代わりに新設のKey Phrasesセクションで番号付き学習
コーナーを設ける、②Full Story Introduction音声に混入していた不要な
音声を除去する、③本編冒頭の記事タイトル重複読み上げを除去する、
④Outro音量をIntroに揃える、の4点が技術的な中心。

## 2. 発見した問題と対応(重要)

### 2-1. "Now, the full story." / "ポイント解説" の異常音声(ユーザー指摘で発覚)

ユーザーの指摘通り、"Now, the full story."の音声には**実際に指定テキスト
と無関係な内容が混入していた**ことを確認した。ASRで内容を確認したところ、
以下のような無関係な内容が生成されていた(いずれも別の記事のような
文章):

- "New to ET."(1回目、内容自体が別物)
- 48秒に渡るフランスのRPGゲームに関する解説(2回目)
- "Two things."(3回目)
- ecサイトの説明、ストーリーテリングの説明、パレードの説明など(4〜9回目)

新設した「ポイント解説」(2語の短い日本語フレーズ)でも同様に、27秒に
渡る「あいさつの効果」についての無関係な内容が生成される事例を確認した。

**原因の推定**: 両方とも、既存の英語Component用instruction
(`ENGLISH_STYLE_PREFIX`。記事本文から抜粋した英語Key Phraseを、前後の
文脈込みの「連続する番組の一部」として読む前提の指示を含む)を、
**文脈のない単独の短い案内フレーズ**に対して使っていたことが原因と
推定した。ある試行では、モデルが指定テキストの代わりに
instruction文自体の一部("Read directly to one interested listener"、
instructionの"Speak directly to one interested listener..."に酷似)
を読み上げる事例も確認しており、単独の短いフレーズでは"文脈"が不足し、
モデルが指示文や無関係な学習データ由来の内容へ迷い込みやすいと考えられる。

**対応**: "Now, the full story."については、声(Aoede)・モデル
(gemini-2.5-pro-preview-tts)は変更せず、**instructionのみ**を
「以下のテキストをそのまま自然に読み上げてください」という最小限の
指示へ差し替えたところ、1回目の試行で正しく生成された。「ポイント解説」
は、既存のASR検証付き再試行(後述2-2)で規定回数以内に正しい内容へ
到達した。

**開示**: "Now, the full story."だけinstructionを変更したのは、
指示「既に指定済みのナレーターと同じ設定を使用」の趣旨(声・モデルの
一貫性)を保ちつつ、この1フレーズでの再現性のある異常を解消するための
最小限の技術的対応であり、内容(読み上げるテキスト)そのものは一切
変更していない。この判断が意図と異なる場合はご指摘ください。

### 2-2. ASR検証付き生成の導入

上記の教訓を踏まえ、`er003_b1_p9a_audio.generate_narration_snippet_
verified`を新設した。生成のたびにAzure STTで内容を確認し、指定テキスト
の一部が含まれない場合は自動的に再試行する(最大試行回数を指定可能)。
今回の修正で生成した全ての新規ナレーションについて、この検証付き生成
または個別のASR確認のいずれかを実施済み。

## 3. Preview(日本語のみ)について

このプロジェクトの全履歴を調査したが、英語Key Phraseを含まない
「日本語のみのPreview」音声は一度も作られていなかった(P5A〜P5Cは
別TTSエンジンの比較検証だが、いずれも「目印」マーカー入りで英語Key
Phrase挿入を前提とした原稿のまま)。そのため、指示に従い新規作成した。

原稿は、既存Preview原稿(Pattern A、英語Key Phrase入り)から英語部分
だけを除去し、日本語の流れが自然につながるよう調整したもの(語順・
語彙・事実関係は一切変更していない、英語で二重に説明されていた部分を
一度だけの日本語表現にしただけ)。

- 原稿: `er003_output/b1_p9a/A01/source/japanese_only_preview_script.txt`
- 音声: `er003_output/b1_p9a/A01/narration/preview_japanese_only.wav`
  (sha256: `df8c34fc...`、31.66秒)
- モデル: `gemini-3.1-flash-tts-preview`(Previewで採用済みのモデルを
  継続使用)、単一TTS call
- ASR確認: 原稿と完全一致(「決勝→結晶」「歓喜→寒気」の2箇所のみ、
  このプロジェクトで繰り返し確認されている既知のASR側同音異義語
  パターン)

## 4. Full Story冒頭のタイトル除去(MFA使用、RMSは不使用)

### 4-1. 英語MFAモデルの新規導入

本編音声(英語)の単語境界を正確に特定するため、Montreal Forced
Alignerの**英語音響モデル・辞書(english_mfa)を新規にダウンロード
した**(既存のMFA環境には日本語モデルのみが導入されており、英語音声の
整列には使えなかったため)。日本語モデルと同様、`mfa_tool/`配下に
ローカル保存され、.gitignore対象。

### 4-2. 境界特定と除去

`er003_output/b1_p8a/A01/body_raw/A01_b1_body_dynamics3.wav`(既存の
本編音声、無変更)へMFA(english_mfa)を適用し、単語ごとの正確な時刻を
取得した。

| 項目 | 値 |
|---|---|
| タイトル("...Champions Struck")の終了 | 4.08秒 |
| 本文第1文の最初の単語("on") の開始 | 4.86秒 |
| 元の音声先頭の無音(最初の単語"five"の開始) | 0.17秒 |

本文第1文の開始位置(4.86秒)を基準に、`p3z.adjust_leading_silence`で
先頭を除去した。除去後に残す無音は、**元の音声が最初の文の前に
自然に持っていた無音の長さ(0.17秒)** と同じ値にすることで、恣意的な
値を使わず、不自然な切れ目を避けた。

- `speech_content_unchanged: True`(本文第1文以降のサンプルが一切
  変更されていないことを機械的に確認)
- ASR確認: 除去後の音声は"On July 15, 2026, England and Argentina
  met in Atlanta..."から正しく始まることを確認(タイトルの再出現なし)
- 音声: `er003_output/b1_p9a/A01/narration/full_story_no_title.wav`
  (145.343秒、150.033秒から4.69秒短縮)

## 5. Key Phrasesセクション

5つのused form(shot on target / take players off / a narrow lead /
close the door to the final / stoppage time)について、**英語部分は
新規生成せず、P7Cで既に検証済みの英語Componentをそのまま再利用**した
(1回目・2回目の読み上げとも同一音声)。日本語の意味は、Pattern A本文
で既に使われている表現をそのまま使用し、新しい訳語は作っていない。

| # | 番号 | 英語(既存Component再利用) | 日本語(新規生成) |
|---|---|---|---|
| 1 | One. | shot on target(`b1_p3u/.../en_shot_on_target_trimmed.wav`) | 枠内シュート |
| 2 | Two. | take players off(`b1_p4c/.../02_take_a_player_off.wav`) | 選手を交代で下げる |
| 3 | Three. | a narrow lead(`b1_p4c/.../03_narrow_lead.wav`) | わずかなリード |
| 4 | Four. | close the door to the final(`b1_p7c/.../new_close_the_door_to_the_final.wav`) | 決勝への道を閉ざす |
| 5 | Five. | stoppage time(`b1_p4c/.../05_stoppage_time.wav`) | アディショナルタイム |

各ブロックの構成: 番号(0.4秒)英語(0.4秒)日本語(0.4秒)英語(0.8秒)。
Preview・本編よりポーズを短くしつつ、区切りが聞き取れる長さを確保した
(指示section6)。

## 6. 全体構成とタイムライン(19パート)

| # | パート | 直後のポーズ |
|---|---|---|
| 1 | Intro Music | 0秒(追加無音なし) |
| 2 | "Welcome to English Your Way." | 0.5秒 |
| 3 | "Today's topic is [英語タイトル]." | 0.65秒 |
| 4 | 日本語タイトル(既存音声を再利用、テキスト無変更) | 0.5秒 |
| 5 | Transition Sound(1回目) | 0.4秒 |
| 6 | "Here's a quick preview." | 0.65秒 |
| 7 | 「ポイント解説」 | 0.5秒 |
| 8 | Preview(日本語のみ、新規作成) | 0.5秒 |
| 9 | Transition Sound(2回目) | 0.4秒 |
| 10 | "Here are today's key phrases." | 0.5秒 |
| 11-15 | Key Phrase 1〜5(各: 番号0.4秒英語0.4秒日本語0.4秒英語) | 各0.8秒 |
| 16 | Transition Sound(3回目) | 0.4秒 |
| 17 | "Now, the full story."(修正済み) | 0.7秒 |
| 18 | Full Story(タイトル除去済み、本文第1文から) | 0.5秒(既存慣習に基づく判断、指示に明記なし) |
| 19 | Outro Music | 0秒(追加無音なし) |

Transition Sound(notification.mp3)は指示通り**3回**使用(Preview前・
Preview後・Key Phrases後)。

## 7. Outro音量調整

指示「Outro Musicの音量を、Intro Musicと聴感上ほぼ同程度にする」に
対応するため、v1(前回)の「Preview・本編の平均RMSへ全素材を合わせる」
方式から、**Outroだけは特別にIntroの調整後RMSへ直接合わせる**方式に
変更した。

| 項目 | 値 |
|---|---|
| Intro(調整後)RMS | 0.08672 |
| Outro(調整後)RMS | 0.08672(Introと完全一致) |
| Outro適用gain | 0.6501倍(減衰) |
| Outro調整後ピーク | 0.478(クリッピングの心配なし) |

Outroの音源自体の長さ・内容は変更していない(gainのみのスカラー調整)。

## 8. 完成音声の場所

**追加修正A・B反映後の最終値。**

| 項目 | 値 |
|---|---|
| path | `er003_output/b1_p9a/A01/assembled/English_Your_Way_A01_r1.wav` |
| sha256 | `f20b80df78d9603872b1ec977bcc9f8dcce82d1c33d8c23241f0255178d69cf4` |
| duration | 256.862秒(約4分17秒。無音短縮1.5秒分だけ初版より短縮) |
| sample rate | 48000Hz |
| channels | 2(stereo) |
| peak | 0.888 |
| clipping | 検出なし |

## 9. 最終確認チェックリスト(指示の「完成後の最終確認」に対応)

全体音声に対してASR(en-US、連続認識)を実施し、以下を確認した。

| 確認項目 | 結果 |
|---|---|
| 冒頭が"Welcome to English Your Way."になっている | 確認("Welcome to English Your Way. Today's topic is...") |
| タイトルが"Today's topic is [英語タイトル]."の形式 | 確認 |
| Previewが日本語のみになっている | 確認(ASR上、Preview区間に英語Key Phraseの単語は出現しない) |
| Preview内に英語キーフレーズが残っていない | 確認(新規作成した日本語専用原稿・音声を使用しているため構造的に不在) |
| "Here are today's key phrases."の後に「キーフレーズ」という日本語音声を入れていない | 確認(構成上、直後はKey Phrase 1のブロックのみ) |
| 5つのキーフレーズがすべて番号→英語→日本語→英語の順になっている | 確認(ASR上も"one shot on target...shot on target"等のパターンで検出) |
| 番号がOneからFiveまで正しく読み上げられている | 確認(ASRは一部を"3"等の数字表記にするが、これは数字読み上げに対するASR側の表記揺れであり、過去のP7A/P7C等でも繰り返し確認済みの既知のパターン) |
| "Now, the full story."周辺に不要な音声が混入していない | 確認(2-1の対応後、ASRで"Now the full story."のみを検出) |
| Full Story冒頭の記事タイトルが削除され、本文第1文から始まっている | 確認(4節、MFA境界+ASR) |
| Transition Soundの位置と回数が正しい | 確認(3回、Preview前後・Key Phrases後) |
| Outro MusicのIntroとの音量バランス | 確認(7節、RMS完全一致) |
| 指定していないBGM・効果音・ナレーション・締めコメント等が追加されていない | 確認(構成は19パートのみ、指示以外の要素を追加していない) |

## 10. 機械QA

| 項目 | 結果 |
|---|---|
| Preview(日本語のみ)・Full Story(タイトル除去)以外の既存音声を変更していない | 合格 |
| 新規ナレーション全てがASR検証済み | 合格 |
| 全19パートが指定順序で1回ずつ存在 | 合格 |
| Transition Soundが3回 | 合格 |
| 音声がdecode可能 | 合格 |
| clippingなし | 合格(peak 0.888) |
| Outro音量がIntroと一致 | 合格(RMS完全一致) |

**機械QAは全て合格した。ただし、これは音質・自然さ・完成度の承認を
意味しない。ユーザー試聴での判断が必須。**

## 11. 作成・変更したファイル

- `er003_b1_p9a_audio.py`(更新): ASR検証付き生成関数、タイトル除去
  関数、Key Phraseブロック組み立て関数、v2ナレーション原稿定数を追加
- `er003_v1_b1_p9a_r1_generate.py`(新規): 修正版オーケストレーション
  script
- `er003_test_b1_p9a_r1_audio.py`(新規、8件、合成データのみ)
- `er003_output/b1_p9a/A01/`配下の新規成果物(`narration/`追加分、
  `mfa/_output_en/`、`audit/`追加分、`instruction/ER-003-B1-P9A-R1_
  instruction.md`、本報告書)
- MFA英語モデル(`mfa_tool/`配下、.gitignore対象、Git管理外)を新規
  ダウンロード
- `er002_common.py`・`er002_gemini_client.py`: **変更なし**(凍結仕様)

## 12. テスト結果

- `er003_test_b1_p9a_r1_audio.py`(新規8件、合成データのみ): 全合格
- プロジェクト全体回帰テスト(`run_project_regression.py`、
  er0*_test_*.py全探索): 追加修正A・B反映後の時点で**1620件全合格、回帰なし**

## 13. 再実行方法

```
.venv/Scripts/python.exe er003_v1_b1_p9a_r1_generate.py
```

新規ナレーションは既に生成・保存済みのため、再実行時は新規TTS callなし
で組み立てから再実行できる(ただし本編タイトル除去は
`er003_b1_p9a_audio.trim_title_from_body`をscript内で毎回呼ぶため、
`body_raw/A01_b1_body_dynamics3.wav`が存在すれば追加のMFA実行なしで
即座に再現できる)。

## 14. 既知のリスク

- "Now, the full story."は、既存のENGLISH_STYLE_PREFIXでは高頻度に
  無関係な内容を生成する不具合が確認された。今回は最小限のinstruction
  へ差し替えて解消したが、根本原因(モデル側の挙動)は解明できて
  いない。同様の短い単独フレーズを今後追加する場合、同じ問題が
  再発する可能性がある。
- Key Phrasesの日本語訳語は、Pattern A本文で既に使われている表現を
  そのまま採用した(新規の訳語判断はしていない)。学習教材として
  この訳語が最適かどうかはユーザーの判断による。
- Full Story冒頭のタイトル除去は、新規に導入した英語MFAモデルに
  基づく。日本語MFA同様、ローカル環境固有のツールであり、Git管理
  対象外。
- 18(Full Story)→19(Outro)間の0.5秒ポーズは、指示に明記がなかった
  ため、既存の慣習(v1相当)を踏襲した判断。指示と異なる場合はご指摘
  ください。
- 機械QA・ASR確認は全て「診断情報」であり、音質・自然さ・完成度の
  承認を意味しない。指示の「完成後の最終確認」項目は形式的にASRで
  照合したが、実際の聴感はユーザー試聴でのみ判断できる。

## 15. 指示書の保存先とsha256

| 項目 | 値 |
|---|---|
| path | `er003_output/b1_p9a/A01/instruction/ER-003-B1-P9A-R1_instruction.md` |
| sha256 | `e2c3fc5fa5ba9fa538a7d279587d82dffc8e875fa4faaab2dedd8e95dd7feb70` |
| 管理ID | ER-003-B1-P9A-R1 |
| 指示書からの逸脱 | Full Story→Outro間のポーズ(0.5秒、指示に明記なし、section14参照) |

## 16. Git status

このレポート作成時点では未コミット。P9A-R1関連ファイルのみをステージ
してコミットします。

## 17. push

実行していません。

---

## ユーザーへの確認事項

以下の修正版をご試聴ください。

- [English_Your_Way_A01_r1.wav](assembled/English_Your_Way_A01_r1.wav)(修正版、約4分17秒。無音短縮・Outro追加調整を反映した最新版)

特に以下を重点的にご確認ください。

- "Now, the full story."が正しく、余計な音声なく読まれているか
- Full Story冒頭でタイトルが重複していないか、本文第1文からの入りが
  自然か
- Key Phrasesセクション(5つ)のテンポ・区切りの聞き取りやすさ
- 日本語のみのPreview(新規作成)の自然さ・分かりやすさ
- Outroの音量がIntroと比べて違和感がないか

**機械QAは全て合格していますが、「完成版合格」「公開可能」とは判断して
いません。**

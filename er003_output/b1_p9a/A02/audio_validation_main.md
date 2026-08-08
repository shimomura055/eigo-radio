# ER-003-REPRO-01-MAIN 実行報告(A02本文・学習セクションまとめて生成)

**ステータス: `PROTOTYPE / NOT_APPROVED`(ユーザー試聴前、初回通し候補)**

## 1. 使用したA02原稿・記事ID

- 記事ID: **A02**(「英国政府が16〜17歳向けに夜間SNS利用を制限する計画」)
- B1本文: `er003_output/b1_p1/A02/b1_article_raw.md`(ER-003-REPRO-01 Stage1-2で生成済み、まだユーザー未承認だが「初回完成候補を作ってから試聴・修正する」対象として使用)
- 英語タイトル: "UK Plans Midnight Social Media Break for Teenagers"
- 日本語タイトル: "午前0時、SNSに"おやすみ"――英国が夜更かしスクロールへ静かな消灯"(承認済み日本語マスターのタイトル行から絵文字・「」・見出し記号を除いたもの)

## 2. 使用した構成

A01最終版(P9A-R2)の19パート構成をそのまま踏襲。サービス共通文言(Podcast Name/Preview案内/ポイント解説/Key Phrases案内/Full Story案内/番号1〜5)はA01の既存音声をそのまま参照し、新規TTSは行っていない。A01固有のスポーツ用文言・見出しはコピーしていない。

## 3. Preview再利用結果

`er003_output/b1_p9a/A02/narration/preview_japanese_only.wav`(ER-003-REPRO-01-PREVIEW-AUDIOでユーザー試聴・承認済み)を**無変更のまま**使用。内容・話速・声質は一切変更していない。

## 4. Key Phrase 5件

ER-003-KP-02-R1で確定した最終値をそのまま使用。

| # | used_form | 日本語 |
|---|---|---|
| 1 | opt out | 参加・適用を断る |
| 2 | covered apps | 規制対象のアプリ |
| 3 | urge to watch | 見たいという衝動 |
| 4 | personalized feed | 個人向けに選ばれた投稿欄 |
| 5 | digital switch-off period | デジタル利用の停止時間帯 |

## 5. Full Story生成条件

ER-002/A01で確立した本文用凍結仕様をそのまま適用(変更なし)。

| 項目 | 値 |
|---|---|
| model | gemini-2.5-pro-preview-tts |
| voice | Aoede |
| instruction | `common.build_style_prefix()`(無変更) |
| chunk分割 | 3chunk固定構造(本文/Today's...Points+Point One+Point Two/In One Line) |
| セクション間無音 | 0.8秒(common.SECTION_JOIN_PAUSE_SECONDS) |
| QA | embedded+grounded QA(QAモデル gemini-3-flash-preview) |
| Dynamics 3 | 結合後の本編全体へ1回 |

## 6. Full Story TTS call数・retry数

| 項目 | 値 |
|---|---|
| 試行回数 | 2回(1回目は内容QA不合格`unauthorized_paraphrase`相当、2回目で合格) |
| 上限超過 | なし(既存QA契約の3回以内で合格、A01のような追加許可は不要だった) |
| technical retry | 0回 |

## 7. 短文ナレーション生成結果

| 名前 | 試行回数 | 備考 |
|---|---|---|
| topic_intro | 1 | |
| japanese_title | 1 | |
| meaning_1(opt out訳) | 1 | |
| meaning_2(covered apps訳) | 2 | ASR不一致1回で自動再試行 |
| meaning_3(urge to watch訳) | 1 | |
| meaning_4(personalized feed訳) | 2 | ASR不一致1回で自動再試行 |
| meaning_5(digital switch-off period訳) | 3 | **1回目hallucination発見(後述9節)** |

## 8. 数字・時刻QA

ASRで全体を通し試聴診断した結果、"16 and 17 year olds"、"midnight until 6:00 AM"、"9 PM until 7 AM"、"309 families"、"spring 2027"、"seven and ten"等、本文中の数字・時刻表現はすべて書字順どおりに発話されていることを確認した。A01のスコア表記("1-2")のような語順入れ替わりは検出されなかった。

## 9. MFA利用箇所・重大な不具合の発見と修正

### 9-1. MFA利用箇所

Full Story本編音声全体(166.43秒)へ英語MFAを1回実行(`mfa_tool/a02_body_output/A02_body.TextGrid`)。タイトル境界1箇所、notification2挿入位置2箇所の特定に使用。MFA単独では確定せず、いずれもASRで前後の発話内容を確認済み(8節参照)。MFA手修正は発生していない。

### 9-2. 【重大】短文ナレーションのhallucination(2件)

A01の"Now, the full story."と同種の不具合が、A02でも2件発生した。

**meaning_5("デジタル利用の停止時間帯")**: 標準の検証(部分一致のみ)では「合格」と判定されたが、実際の生成音声は**28.8秒**(目的の文言は本来2〜3秒程度)で、ASR全文は「デジタル利用の停止時間帯。ポイント。ワン。日中はいくらでも使える時間帯を設けよう。ポイント、two。夜は停止時間帯を設けて…」という、**目的の文言の後に全く無関係な創作内容(架空の生活習慣アドバイス)が28秒以上続くもの**だった。部分一致検証だけではこの種の不具合を検出できないと判明したため、ASR文字数が期待文字数を大きく超えていないかも検証する`generate_narration_snippet_verified_strict`を新設し、全短文ナレーションをこの基準で再生成した。

**Key Phrase Component"opt out"**: 標準経路で6回とも不合格。実際の生成内容は「Don't get into this mindset of letting your mess perfection creep in...」(部屋の片付けについて)や「Lake of Baikal.」(バイカル湖の地理雑学)など、指定テキストと無関係だった。A01の"Now, the full story."の対症療法(声・モデルは変えず、instructionのみ最小限のものへ差し替える)と同じ考え方をフォールバックとして実装し、1回目で解決した(声・モデル・テキストは変更していない)。

## 10. Point One / Two / In One Line

本文全体の一部としてFull Story音声内に含まれる(A01同様、独立したセクションとしては分離していない)。ASRで見出し・内容とも欠落なく確認済み。

## 11. 音声編集内容

Full Story音声へ、notification2挿入2箇所+タイトル除去の計3編集を、時系列で後ろから前の順(insert2→insert1→title_trim)で適用。編集前後で発話内容が変更されていないことをコードで確認済み(詳細: `audit/full_story_edit_info.json`)。

## 12. 効果音・ポーズ

Intro/Outro/notification(3回)/notification2(2回、Full Story内)はA01最終仕様の共通部分を使用。A01固有のスポーツ構造(タイトル除去位置・notification2挿入時刻等)は機械的にコピーせず、A02自身のMFA+ASRで新たに特定した。

## 13. 音量調整

A01 R1で確立した一般的な方法(Preview・本編は無加工のまま基準、他素材は平均RMSへ、OutroはIntroの調整後RMSへ一致)を適用。**A01固有のOutro追加減衰(聴感2/3、-5.85dB)はA02では適用していない**(A02について同様のユーザー指摘をまだ受けていないため、A01の個別判断を機械的にコピーしない)。

## 14. 初回完成候補の場所

| 項目 | 値 |
|---|---|
| path(WAV) | `er003_output/b1_p9a/A02/assembled/English_Your_Way_A02.wav` |
| sha256(WAV) | `e3961615009d3eaea6aeb737fed5c9347668ca6d4b28bf3ca93657a0fd166439` |
| path(MP3) | `er003_output/b1_p9a/A02/assembled/English_Your_Way_A02.mp3` |
| sha256(MP3) | `3b5e7baaec13745fad147410489a853d2075b98302bba4a54b0b2d22569ec047` |

## 15. 全体duration

**269.902秒(約4分30秒)**

## 16. セクション一覧とduration

| # | パート | 開始 | 終了 | 長さ | 直後のポーズ |
|---|---|---|---|---|---|
| 1 | Intro | 0.000 | 10.736 | 10.736秒 | 0秒 |
| 2 | "Welcome to English Your Way."(A01再利用) | 10.736 | 12.847 | 2.111秒 | 0.5秒 |
| 3 | "Today's topic is [A02タイトル]."(新規) | 13.347 | 18.718 | 5.371秒 | 0.65秒 |
| 4 | 日本語タイトル(新規) | 19.368 | 28.488 | 9.120秒 | 0.5秒 |
| 5 | Transition(1回目) | 28.988 | 31.028 | 2.040秒 | 0.4秒 |
| 6 | "Here's a quick preview."(A01再利用) | 31.428 | 32.879 | 1.451秒 | 0.65秒 |
| 7 | 「ポイント解説」(A01再利用) | 33.529 | 34.749 | 1.220秒 | 0.5秒 |
| 8 | Preview(承認済み、無変更) | 35.249 | 55.189 | 19.940秒 | 0.5秒 |
| 9 | Transition(2回目) | 55.689 | 57.729 | 2.040秒 | 0.4秒 |
| 10 | "Here are today's key phrases."(A01再利用) | 58.129 | 60.020 | 1.891秒 | 0.5秒 |
| 11-15 | Key Phrase 1〜5 | 60.520 | 95.725 | 計35.205秒 | (各内包) |
| 16 | Transition(3回目) | 95.725 | 97.765 | 2.040秒 | 0.4秒 |
| 17 | "Now, the full story."(A01再利用) | 98.165 | 100.036 | 1.871秒 | 0.7秒 |
| 18 | Full Story(タイトル除去・notification2挿入2箇所込み) | 100.736 | 263.258 | 162.523秒 | 0.5秒 |
| 19 | Outro | 263.758 | 269.902 | 6.144秒 | 0秒 |

## 17. 機械QA

| 項目 | 結果 |
|---|---|
| Previewが承認済みファイルと同一 | 合格(sha256照合) |
| Key Phrase 5件が正しい順序・構成 | 合格(ASR全文で番号→英語→日本語→英語のパターンを確認) |
| Full Storyに重大な欠落・追加がない | 合格(ASR全文で本文全体が欠落なく検出) |
| 短文ナレーションに無関係な内容がない | 合格(strict検証導入後、全件確認) |
| decode可能 | 合格 |
| clippingなし | 合格(peak 0.930) |
| セクション順序・ポーズ仕様 | 合格(16節の積み上げ計算で確認) |
| 効果音位置 | 合格(notification2挿入2箇所、ASRで前後確認済み) |
| 音量差に重大な異常なし | 合格(全素材RMS均一化、Outroのみ別基準) |
| Preview=3.1、本文=2.5のモデル分離維持 | 合格 |

**機械QAは全て合格した。ただしこれは音質・自然さ・完成度の承認を意味しない。ユーザー試聴での判断が必須。**

## 18. 再現性指標

| 指標 | 値 |
|---|---|
| Preview TTS call数 | 1(再利用、今回の新規callは0) |
| 本文TTS call数 | 2(1回不合格→2回目合格) |
| technical retry数 | 0 |
| 内容起因再生成数(本文) | 1 |
| 短文ナレーションTTS call数(topic_intro+japanese_title+meaning_1-5) | 11 |
| 短文内容不一致再生成数 | 4(meaning_2×1, meaning_4×1, meaning_5×2[うち1件は28.8秒のhallucination]) |
| Key Phrase Component TTS call数 | 標準経路6+フォールバック1=7(opt outのみ) |
| MFA利用箇所数 | 1箇所(本編音声全体、3境界の特定に使用) |
| MFA手修正数 | 0 |
| ASRで検出した問題数 | 2件(meaning_5のhallucination、Key Phrase"opt out"のhallucination) |
| 人間試聴前の手修正数 | 0(全て自動検出・自動対応) |
| A01固有例外を追加した数 | 0(汎用的なフォールバック機構として実装) |
| 初回通し候補までの人間確認回数 | 0(指示どおり、細かい途中確認なしで到達) |
| 初回通し候補の修正版番号 | 1版(初回) |

## 19. A01との比較

| 指標 | A01(最終) | A02(初回候補) |
|---|---:|---:|
| 本文TTS call数 | 6(1回目3回不合格+2回目3回目合格) | **2**(1回目不合格→2回目合格) |
| 短文ナレーションのhallucination件数 | 1種類("Now, the full story.") | 2種類(meaning_5、opt out) |
| MFA手修正数 | 1(スコア読み上げ語順問題) | 0 |
| notification2挿入のMFA単独判定 | していない(ASR併用) | していない(ASR併用) |
| 人間試聴前に検出できた不具合 | 0件(全て試聴後に発覚) | **2件(hallucination、試聴前に検出・自動修正)** |
| 初回通し候補までの人間確認回数 | 複数回(段階的に進行) | 0回(一括生成) |

**A01より少ない人間介入で初回通し候補に到達できた**(本文TTSはA01の6回に対し2回、hallucination 2件も試聴前に自動検出・修正できた)。ただし、hallucinationという不具合の「種類」自体はA01より多く発見されており、この種の不具合が記事によらず一定の頻度で発生することが確認された(横断ルールへの反映が必要)。

## 20. 人間試聴前に残るリスク

- 機械QA・ASR確認は全て「診断情報」であり、音質・自然さ・完成度の承認を意味しない。
- Outro音量はA01のような追加の聴感調整をしていないため、A01と比べて大きく感じる可能性がある。
- B1本文自体(`b1_article_raw.md`)はまだユーザー最終承認を得ていない(音声化してよいという指示に基づき使用したのみ)。
- meaning_5・opt outのhallucination対応は自動検出・自動修正できたが、根本原因(モデル側の挙動)は未解明(A01と同様)。

## 21. 作成・変更したファイル

- `er003_v1_repro01_main_generate.py`(新規、全stage a〜e)
- `er003_output/b1_p9a/A02/`配下の新規成果物一式(`narration/`、`key_phrase_components/`、`assembled/`、`audit/`、`asr/`)
- 既存A01コード(`er003_b1_p8a_audio.py`/`er003_b1_p9a_audio.py`等): **変更なし**

## 22. テスト結果

新規ロジック(strict検証・minimal instructionフォールバック)は新規スクリプト内の関数として実装。プロジェクト全体回帰テスト: **1660件全合格、回帰なし**。

## 23. Git status

このレポート作成時点では未コミット。関連ファイルのみをステージしてコミットする。

## 24. Push

実行していません。

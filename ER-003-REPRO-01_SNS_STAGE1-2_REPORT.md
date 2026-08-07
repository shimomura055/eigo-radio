# ER-003-REPRO-01 実施報告(SNS規制記事: Stage1入力監査〜Stage2設計確認)

**作成日: 2026-08-08**
**管理ID: ER-003-REPRO-01**
**ステータス: `PROTOTYPE / NOT_APPROVED`(B1原稿レベルまで到達、Preview設計・
音声生成は未着手。下記10節の理由により、この時点でユーザー判断を
仰ぐために一旦停止している)**

---

## 1. 監査レポートFeedbackへの対応

`ER-003-B1_P8A-P9A_AUDIT_REPORT.md`のユーザー承認粒度を修正した。

- 冒頭に「承認区分の凡例」(**[原稿承認]** / **[実装方針承認]** /
  **[修正箇所承認]** / **[音声試聴承認]** / **[エピソード全体の最終承認]**)
  を新設し、各「ユーザーOKの記録」箇所に区分タグを付けた。
- 特にご指摘のP9A-R1「修正した箇所はOKです。」は
  **[修正箇所承認]**タグを付け、「直前に提示・試聴した修正箇所につい
  ての承認であり、P9A-R1全体、またはエピソード全体の最終承認を意味
  するものではない」と明記した。
- 事実関係(誰が・いつ・何を言ったか、commit・sha256等)は一切変更して
  いない。

## 2. A01から抽出した横断ルール

[ER-003_PIPELINE_CROSS_CUTTING_RULES.md](ER-003_PIPELINE_CROSS_CUTTING_RULES.md)
を新規作成した。TTS生成/音声編集/音質・品質確認/承認運用の4カテゴリで
整理し、A01固有の値(スコア境界値、タイトル除去時刻、Outro gain値等)は
「個別対応として残すもの」に分離して、共通仕様へ混入させないようにした。

## 3. A01 Baseline指標

[ER-003-REPRO_BASELINE.md](ER-003-REPRO_BASELINE.md)を新規作成した。
既存レポート・監査JSONから再構成できた範囲で、TTS call数・MFA利用箇所・
人間試聴のみで発見した問題数(7件)・修正版数(6版)などを集計し、復元
できない指標は`NOT_RECORDED`とした(信頼度も高/中/推測含むで区別)。
次記事の指標が出るたびにこの表を更新する。

## 4. SNS規制記事の正式ID・タイトル

| 項目 | 値 |
|---|---|
| 記事ID | **A02**(勝手な新規ID確定はしていない。`er003_output/p1/ER-003-P1_user_review.md`133行、`er003_ja_to_en_translation.py`の`APPROVED_ARTICLE_SOURCE_PATHS`に既存登録済み) |
| 日本語での呼称(P1レビュー内) | 「英国の未成年向け夜間SNS設定」 |
| 英語タイトル(自然英語ソース承認版) | "Midnight Means Goodnight: The UK's Quiet Plan to Curb Late-Night Scrolling" |
| 英語タイトル(本日新規生成したB1原稿) | "UK Plans Midnight Social Media Break for Teenagers" |
| 内容 | 英国政府が16〜17歳向けに、深夜0時〜午前6時のSNS利用を初期設定で
  停止する"digital switch-off period"を導入する計画。通知停止・
  autoplay停止・レコメンド機能停止を含むが、強制ではなくopt-out可能。
  効果を裏付ける2つの実証研究(309家庭の夜間制限実験、Ofcomの
  デフォルト設定実験)を紹介。 |

## 5. 原稿・Preview・Key Phraseの既存状態

| 段階 | 状態 |
|---|---|
| 自然英語ソース(p1b) | **承認済み**(`natural_source_approval.json`、見出し等の軽微編集の上承認) |
| 要約/Podcast風書き出し(p2b) | **承認済み**(`USER_APPROVED_LIGHT_EDIT`) |
| Key Phrase選定(p2i) | **承認済み**(Strategy L採用、5句確定): `by default` / `opt out` /
  `digital switch-off period` / `speed bump` / `hands-off approach` |
| B1本文(記事全文、A01の`b1_p1`相当) | **本日新規生成**(下記6節)。**まだユーザー未承認** |
| Preview原稿 | **未着手**。設計方針(後述9節)自体が未決定 |
| Key Phrase Component音声 | **なし**(TTS生成は一度も行っていない) |

## 6. 過去成果物の有無と承認状態

`er003_output/`配下でA02を含む全ディレクトリ(`p1`/`p1b`/`p2`/`p2b`/
`p2d`/`p2f`/`p2g`/`p2i`)を確認した。**`b1_p*`配下にA02のディレクトリは
一つも存在せず、音声(`.wav`)ファイルも一件も存在しなかった**(A01の
ような過去の音声実験・過去のTTSエンジン比較検証はA02に対して一度も
実施されていない)。

過去成果物を勝手に本番候補として再利用することを避けるため、承認記録
(`*_approval.json`)の`article_id`フィールドが必ず`"A02"`であることを
確認した上で、p1b/p2b/p2iの3つの承認済み成果物のみを入力として使用した。

## 7. A01との構造差

| 観点 | A01(England vs Argentina) | A02(SNS規制) |
|---|---|---|
| ジャンル | スポーツの試合速報 | 政策解説記事 |
| 構造 | Title / 本文 / Today's...Points(Point One・Point Two) / In One Line | 同一の型(Title / 本文 / Today's...Points(Point One・Point Two) / In One Line)。**構造そのものは共通** |
| 数字・固有名詞の量 | 少なめ(スコア"1–2"、時刻"85th minute"程度) | **中程度**(309家庭、7割/5割、深夜0時〜6時、2027年春、7月15日) |
| 数字の読み上げリスク | P9A-R2で実際に発覚(スコア"1-2"の語順問題) | 「7 in 10」「16- and 17-year-olds」等、口語的に読み替えられる可能性がある表現が複数あり、**A01と同種のMFA語順ズレリスクが潜在** |
| 比喩表現 | 少ない | 多い("speed bump"、"digital switch-off period"などが比喩・専門用語で、Key Phrase選定でも「聞き取りにくさ」の理由として明記されている) |

## 8. 再利用できる共通処理

[ER-003_PIPELINE_CROSS_CUTTING_RULES.md](ER-003_PIPELINE_CROSS_CUTTING_RULES.md)
に整理した全ルールに加え、コードレベルでは以下がそのまま再利用できる
ことを確認した(変更なし)。

- `er003_b1_article.py`の全ての汎用関数(`export_master_files`/
  `build_b1_user_message`/`make_b1_generator_fn`/`check_b1_structure`/
  `compute_b1_sentence_metrics`/`run_machine_checks`)。いずれも
  モジュール定数(`TOPIC_ID="A01"`固定)に依存せず、引数だけで動作する
  設計だったため、**このモジュール自体は一切変更していない**(既存の
  `test_only_one_topic_id_defined`テストも無傷)。
- Preview/Full Story用TTSモデル設定(Preview=`gemini-3.1-flash-tts-preview`、
  本文=`gemini-2.5-pro-preview-tts`)、ASR検証付き生成、MFAによる境界
  検出、後ろから前への編集順序など、P9A系列の全関数群(`er003_b1_p9a_audio.py`
  等)は記事非依存の設計であり、そのまま使える見込み。

## 9. 記事固有に必要な処理(A01からのコピーを避けた部分)

- B1原稿の入力パス・出力先を、`er003_b1_article.py`を変更せず、新規の
  薄いオーケストレーションスクリプト`er003_v1_repro01_b1_p1_generate.py`
  でA02向けに指定した(詳細は18節)。
- Preview原稿の設計方針そのものが、A01と同じにするか一新するかの
  決定が必要(下記10節)。
- Key Phrase 5句の英語Componentは、A01のような既存流用元がないため、
  全て新規TTS生成が必要になる。

## 10. 初回生成までにユーザー承認が必要な事項(重要、この時点で停止)

Stage3(初回完成候補生成)へ進む前に、以下が判明したため、**ここで
一旦停止し、ユーザー判断を仰ぐ**。

### 10-1. 【最重要】新規生成したB1原稿が、承認済みKey Phraseのうち3件を保持していない

`er003_output/b1_p1/A02/b1_article_raw.md`(本日、既存の承認済み自然
英語ソースを入力に新規生成)を、承認済み5句(p2i)と文字列一致で機械
照合したところ、以下の結果だった。

| Key Phrase(承認済み) | B1原稿での出現 |
|---|---|
| by default | **見つからない**(原稿では"under the standard settings"と言い換えられている) |
| opt out | 見つかる |
| digital switch-off period | 見つかる |
| speed bump | **見つからない**(原稿では"small extra step"と言い換えられている) |
| hands-off approach | **見つからない**(原稿では"doing nothing"と言い換えられている) |

**原因の推定**: B1原稿生成は、承認済み自然英語ソース(p1b)を入力に、
学習者向けにやさしく書き直すプロンプト(A01と同一テンプレート)で
1回のAPI呼び出しにより生成される。このプロンプトはKey Phraseの保持を
明示的に指示しておらず、モデルが理解しやすい平易な言い換えを自発的に
行った結果、比喩的・専門的な3句が失われたと考えられる。承認済み自然
英語ソース自体には5句とも存在することを確認済みであり(`natural_source_
approved.md`)、**ソースの承認内容が変わったわけではなく、B1書き直し
段階で新たに失われた**。

この事象は、A01のB1本編生成で発生した「軽微な言い換えによる
`unauthorized_paraphrase`不合格」(P8A、6回試行の原因)と同種の、TTS
より手前の原稿生成段階での言い換え癖である。[[ER-003_PIPELINE_CROSS_
CUTTING_RULES]]には現時点でこのケース(B1原稿生成段階でのKey Phrase
消失)への対処ルールがなく、**新しい教訓として追加が必要**と考えられる。

**判断が必要な点**: 以下いずれかの対応が考えられるが、どちらも
「学習上の意味を変える原稿変更」に触れるため、ユーザー確認が必要と
判断した。

- (a) B1原稿の該当箇所を、Key Phraseの語句を保持する形に手直しする
  (文意は変えず語句だけ戻す軽微な修正)
- (b) B1原稿はこのまま採用し、Key Phrase 5句をFull Story本文とは
  独立した「Key Phrasesセクション」専用の学習コーナーとして扱う
  (A01のP9A-R1もこの設計、English Componentは既存記事から抜粋した
  ものを再利用しており、必ずしもFull Story音声内に同じ語句が登場する
  ことを厳密に要求してはいなかった)
- (c) B1原稿を、Key Phrase保持を明示指示したプロンプトで再生成する

### 10-2. Preview原稿の設計方針が未決定

A01のPreviewは、①英語Key Phrase埋め込み版→②日本語のみ版、と設計が
大きく変遷した(横断ルールにはどちらが「標準」かの結論が明記されて
いない)。A02のPreviewをどちらの方針で最初から作るか(最初から日本語
のみで作るか、A01の初期方式を踏襲して英語埋め込み版から作るか)は
ユーザー判断が必要。

### 10-3. B1原稿自体のレビュー

A01の precedent(「はい、この原稿で進めてよい」)に倣い、新規生成した
B1原稿(`er003_output/b1_p1/A02/b1_article_raw.md`)についても、音声化
前にユーザーの内容確認をお願いしたい(特に10-1の言い換え箇所)。

**上記が解消されるまで、Preview・Key Phrase音声・Full Story音声の
生成には着手していない。**

## 11〜14. TTS call数・再生成/retry数・MFA利用箇所・ASR検出問題

| 指標 | 値 |
|---|---|
| 実施したTTS call数 | **0回**(音声生成は一切行っていない、B1原稿はLLMのテキスト生成であり別モデル) |
| B1原稿生成のAPI call数 | 1回(`gpt-5.6-sol`、reasoning_effort=high、A01と同一設定を再利用) |
| 再生成・retry数 | 0回(1回で構造チェック・機械チェックとも合格) |
| MFA利用箇所 | 0箇所(音声が存在しないため未実施) |
| ASRで検出した問題 | 0件(音声が存在しないため未実施)。ただし**文字列レベルの機械照合で
  Key Phrase消失3件を検出**した(10-1節、音声生成前に検出できたという
  意味で、A01のP9A-R1で確立した「ASR検証」の原則をテキスト段階に
  応用した形になっている) |

## 15. 人間試聴前に検出できなかったリスク

音声を一切生成していないため「人間試聴」自体が未実施。ただし、
**人間試聴を待たずに機械照合(文字列一致)で先に発見できたリスク**が
10-1のKey Phrase消失であり、これはA01の教訓([[ER-003_PIPELINE_CROSS_
CUTTING_RULES]]「短い単独ナレーションは生成後ASRで内容一致を確認する」
の考え方をB1原稿レベルにも広げた効果)を活かせた具体例と言える。

## 16. 初回通し試聴候補の場所

**まだ生成していない**(10節の理由により、Preview設計方針・B1原稿の
Key Phrase保持方針についてユーザー判断を待つため)。

## 17. 再現性指標(この時点まで)

[ER-003-REPRO_BASELINE.md](ER-003-REPRO_BASELINE.md)の比較表のうち、
A02について現時点で埋められる範囲のみ更新した。

| 指標 | A01 | SNS規制(A02、Stage1-2まで) |
|---|---:|---:|
| Preview TTS call数 | NOT_RECORDED(内訳あり) | 0(未着手) |
| 本文 TTS call数 | 6 | 0(未着手、B1原稿のLLM生成は別カウントで1回) |
| 再生成数 | 少なくとも18件相当 | 0 |
| 人間修正ターン数 | 最低11件 | 0(この報告が最初のユーザー確認ポイント) |
| MFA手修正数 | 1 | 0(未着手) |
| 人間試聴のみで発見した問題数 | 7 | 0(音声未生成。ただし機械照合で1件[Key Phrase消失]を音声化前に発見) |
| 最終修正版数 | 6版 | NOT_RECORDED(進行中) |
| 最終品質 | `PROTOTYPE / NOT_APPROVED` | `PROTOTYPE / NOT_APPROVED`(B1原稿段階) |

## 18. 作成・変更したファイル

- `ER-003-B1_P8A-P9A_AUDIT_REPORT.md`(更新): 承認区分の凡例追加、
  各「ユーザーOKの記録」に区分タグ付与
- `ER-003_PIPELINE_CROSS_CUTTING_RULES.md`(新規): 横断ルール
- `ER-003-REPRO_BASELINE.md`(新規): A01 Baseline指標・比較表
- `er003_v1_repro01_b1_p1_generate.py`(新規): A02向けB1原稿生成
  オーケストレーションスクリプト。`er003_b1_article.py`(A01専用、
  変更なし)の汎用関数を再利用し、パス指定のみA02向けに行う
- `er003_output/b1_p1/A02/`配下の新規成果物(`b1_article_raw.md`、
  `b1_article_for_review.md`、`b1_metrics.json`、`generation_metadata.json`、
  `b1_prompt.txt`、`master_ja_approved.md`、`master_en_natural_source_
  approved.md`)
- `ER-003-REPRO-01_SNS_STAGE1-2_REPORT.md`(本報告書)
- `er003_b1_article.py`・その他既存A01コード: **変更なし**

## 19. テスト結果

- 新規テストは追加していない(B1原稿生成は既存の汎用関数のみを再利用
  したオーケストレーションスクリプトのため、新規ロジックがない)
- プロジェクト全体回帰テスト(`run_project_regression.py`): **1624件
  全合格、回帰なし**(A01の既存成果物は一切再生成・差し替えしていない)

## 20. Git status

このレポート作成時点では未コミット。ER-003-REPRO-01関連ファイルのみを
ステージしてコミットする。

## 21. Push

実行していません(引き続きpushは対象外)。

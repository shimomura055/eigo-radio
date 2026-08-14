# ER-003-B1-SCAFFOLD-AUDIO-01 実行報告(A02 B1 Supported Natural English Audio Prototype)

**管理ID: ER-003-B1-SCAFFOLD-AUDIO-01**
**実施日: 2026-08-14〜15**
**ステータス: `PROTOTYPE / EXPERIMENT`(N増し検証。Production仕様化はしていない)**

## A. Executive Summary

**全11パートの音声化に成功した。** ニュース本文(Full Story Part1/2、
Point One/Two、In One Line)はB2 V2版(ER-003-CEFR-DIRECT-02)と一字
一句共通のテキストをそのまま読み上げ、Preview/Comment1-4は易しい
Support英語、Key Phrasesは5件すべてEnglish→Japanese→Englishで生成
した。**全パートがTTS生成→ASR検証(内容一致+長さ)→合格確認を経て
から組み立てに使用されており、検証不合格のまま採用したパートはない。**

- Comment 4のscope逸脱(night-curfew群限定の結果を一般化していた件)
  を2段階で修正し、最終的にLedger Deviation Check `LEDGER_COMPLIANT`
  を確認した(D節)
- Previewの「Britain is considering」→「Britain is planning」修正も
  適用済み
- **開発中に5件の技術的問題を発見・対処した**(G節): Azure音声認識の
  認証エラー(ユーザー側で解決)、Markdown強調記号・カーブ引用符が
  Gemini TTSを誤動作させる問題、ASR検証の文字列比較方式の欠陥、
  英国綴り/米国綴りの表記差によるASR誤検出
- 総尺4分21秒(261.3秒)、新規生成20件・既存流用5件(H節)
- 音声Artifact(試聴可能)を作成した(F節)

最終的なListening品質・B1として成立するかの判断はユーザー試聴を
優先する。

## B. 修正したSupport文

### Preview(語彙修正)

修正前: "Britain is considering new social media protections..."
修正後: **"Britain is planning new social media protections for
older teenagers. The central issue is what these protections could
change in real life. An earlier test offers useful context, but its
findings need careful reading. As you listen, ask: What can the test
show, and what can it not prove?"**

### Comment 4(scope逸脱の修正、2段階)

修正前(ER-003-B1-SCAFFOLD-01時点): "So, this pilot gives us context,
not a prediction. People reported better sleep, but many changed
when they used screens rather than how much they used them. With
that in mind, here is the story in one line."
→ Ledger Deviation: MAJORではないがMINOR 1件("this pilot"/"People"
がnight-curfew群限定の結果を一般化)

修正v1(今回、1回目): "screens"→"social media"へ変更したが、night-
curfew群のscopeを明示していなかったため別のMINOR逸脱(Preview/
Comment1が「議会承認が必要」という条件を明記していない、という
チェッカー側のブレも一時的に検出、E節参照)

修正v2(今回、最終採用): **"So, the night-curfew group found this
easier to manage, and reported better sleep. But many just changed
when they used social media, not how much. With that in mind, here
is the story in one line."**
→ "night-curfew group"を主語に明示し、"screens"を"social media"へ
訂正。Fact Check `PASS`、Ledger Deviation `LEDGER_COMPLIANT`を確認
(E節)。

## C. 使用した固定B2本文

`er003_output/cefr_direct_02/A02/B2_v2/article.md`(SHA256:
`e0d1c7f6d839ff83ed42bfe58fd1a4a79e3bb0284a6e082be79e71d0763611d7`)
を一字一句変更せずに使用した。Full Story Part1/Part2の分割は、意味上
の転換点("And the plan does not stop at bedtime.")での機械的な
パラグラフ切り出しのみで、文言の変更は行っていない(ER-003-B1-
SCAFFOLD-01と同一の分割)。

## D. Fact / Ledger QA(Support部分)

| Check | 結果 |
|---|---|
| Support Fact Checker | `PASS`(矛盾0件) |
| Support Ledger Deviation Check(最終) | `LEDGER_COMPLIANT`(逸脱0件) |

ニュース本文自体はER-003-CEFR-DIRECT-02で既にFact Check済みのため、
今回はSupport部分(Preview+Comment1-4)のみを対象とした。

### D-1. Ledger Deviation Checkの再現性について(重要な観察)

修正後の同一Support文セットに対し、Ledger Deviation Checkを独立に
4回実行したところ、結果は以下のように揺れた。

| 実行回 | 結果 |
|---|---|
| 1回目(修正前テキスト) | `LEDGER_DEVIATION`(Comment 4のscope問題、MINOR) |
| 2回目(修正v1テキスト、単独検証) | `LEDGER_COMPLIANT` |
| 3回目(同一テキスト、パイプライン内で再検証) | `LEDGER_DEVIATION`(Preview/Comment1が議会承認要件を明記していない、MINOR) |
| 4回目(同一テキスト、再々検証) | `LEDGER_COMPLIANT` |
| 5回目(修正v2テキスト、最終) | `LEDGER_COMPLIANT` |

これはER-003-CEFR-DIRECT-02/03で確認したB1関連チェックの判定ゆれと
同種の現象であり、短いSupport文に対してもLedger Deviation Checkの
判定にばらつきが生じることを示している。今回は、実質的なscope問題
(Comment 4がnight-curfew群を一般化していた点)を修正した上で、複数回
の独立実行のいずれでも重大な逸脱が再現しないことを確認してから音声化
に進んだ。

## E. 新規生成した音声と再利用した音声の区別

### E-1. 新規生成(20件、すべてASR検証合格)

| 種別 | 件数 | 内容 |
|---|---|---|
| Newsセグメント | 5 | Full Story Part1/Part2、Point One、Point Two、In One Line(B2共通本文) |
| Supportセグメント | 5 | Preview、Comment1〜4(易しいSupport英語) |
| Key Phrase 英語Component | 5 | by default / curfew / cross the finish line / pilot / personalised feeds |
| Key Phrase 日本語meaning | 5 | 各英語Componentに対応する日本語の意味説明 |
| **合計** | **20** | すべて個別にTTS生成→ASR検証→合格を確認済み |

### E-2. 既存流用(5件)

| ファイル | 内容 | 由来 |
|---|---|---|
| `num_one.wav`〜`num_five.wav` | Key Phrase番号読み上げ("One"〜"Five") | `er003_output/b1_p9a/A01/narration/`(service-level、記事非依存の既存承認済み音声、A01制作時に生成) |

これらはArticle非依存のservice-levelナレーションであり、内容の
書き換えを伴わないため、新規生成せずそのまま再利用した。

**B2本文音声の新規生成について**: ER-003-CEFR-DIRECT-02の時点では
B2 V2記事はテキストのみで、音声は未生成だった。したがって今回が
B2 V2テキストの初回音声化であり、既存の承認済みB2音声を再利用した
わけではない(新規生成)。これは「B1用に別のB2音声を作らない」という
今回の設計とは矛盾しない(B2側の音声も今回はじめて作られたものであり、
将来的にB2版を音声化する際はこの音声をそのまま流用できる、という
位置づけ)。

## F. 全体音声Artifact

Preview→Key Phrases→Comment1→Full Story Part1→Comment2→Full Story
Part2→Comment3→Point One→Point Two→Comment4→In One Lineの順で、
全11パート+Key Phrases内5ブロックを、パート間0.5秒のポーズで接続した
(EN-EN間の新規territory、K節で扱いを説明)。

**URL**: https://claude.ai/code/artifact/a1fa2f2f-3ffe-4f42-aa2d-ee2c05a01ee4

リポジトリ内の原本: `er003_output/b1_scaffold_audio_01/A02/b1_scaffold_final.mp3`
(WAV原本: `er003_output/b1_scaffold_audio_01/A02/b1_scaffold_final.wav`)

## G. 各セクションの長さ

| パート | 種別 | 長さ |
|---|---|---:|
| Preview | Support | 19.6秒 |
| Key Phrases(5件) | Support | 33.2秒 |
| Comment 1 | Support | 6.2秒 |
| Full Story Part 1 | News(B2共通) | 40.0秒 |
| Comment 2 | Support | 9.0秒 |
| Full Story Part 2 | News(B2共通) | 55.2秒 |
| Comment 3 | Support | 16.2秒 |
| Point One | News(B2共通) | 28.8秒 |
| Point Two | News(B2共通) | 22.1秒 |
| Comment 4 | Support | 13.8秒 |
| In One Line | News(B2共通) | 12.3秒 |
| (パート間ポーズ計) | — | 5.0秒(0.5秒×10) |
| **合計** | — | **261.3秒(4分21秒)** |

Support(Preview+Comment計)は約84.8秒、News(B2本文)は約158.4秒。
Supportは各隣接News区間より一貫して短く、「Supportがニュースの勢いを
止めない」という目標(セクション5)の量的な裏付けとなっている。

## H. 開発中に発見・対処した技術的問題(5件)

今回の音声化過程で、以下5件の技術的問題を発見し、いずれも透明に記録
した上で対処した。

### H-1. Azure Speech-to-Text認証エラー(ブロッカー、ユーザー側で解決)

初回の音声化試行で、全セグメントのASR検証が理由不明のまま空文字を
返す現象が発生した。直接調査した結果、`.env`のSPEECH_KEY/
SPEECH_REGIONの組み合わせが401認証エラーを返していることを特定した。
これは実装側の問題ではなくAzure側の認証情報の問題だったため、ユーザー
に報告し、対応後に再開した。

### H-2. Markdown強調記号(`**`)がGemini TTSを誤動作させる

固定B2本文中の`**"default"**`を含むFull Story Part 1、`**when**`を
含むPoint Twoが、Gemini TTSから`Model tried to generate text, but it
should only be used for TTS`という400エラーを返す原因になっていた。
TTS入力の直前だけでMarkdown強調記号を除去する処理を追加した(表示用
テキストは元のMarkdownを保持)。

### H-3. カーブ引用符(smart quotes)が同種のエラーを引き起こす

H-2の対処後も、Full Story Part 1が同じ400エラーを返し続けた。原因は
`**`除去後も残っていたカーブ引用符("default")だった。カーブ引用符
の除去も追加したが、それでもFull Story Part1は改善しなかった(H-4
参照)。

### H-4. 自己言及的な一文がTTS-onlyモードを混乱させる(テキスト変更不可のため代替手段で対処)

H-2・H-3の対処後も、Full Story Part 1は毎回同じ400エラーを返し続けた。
残る要因は"The word default matters."という一文自体が、"the word X"
という自己言及的な構文であるため、Gemini TTSがこれを「音声化すべき
台詞」ではなく「言葉についての説明を生成せよという指示」と誤認して
いる可能性が高いと判断した。固定B2本文は一字一句変更できないため、
テキスト側の修正はできない。代わりに、Key Phrase Componentの既存
fallback経路(標準のENGLISH_STYLE_PREFIXで失敗した場合、より単純な
MINIMAL_INSTRUCTION_PREFIXへ切り替える、既存Production機構)と同じ
仕組みを、Full Story等のnews本文セグメント全体にも適用した。これに
より、Full Story Part 1はMINIMAL_INSTRUCTION_PREFIX経路で正常に生成
できるようになった。

### H-5. ASR検証の文字列比較方式に起因する偽陰性

`expected_substring`をテキストの先頭40文字で単純に切り出す方式
(`text[:40]`)が、(a)改行文字を含んでしまう、(b)単語の途中で切れる、
(c)ハイフン付き複合語(例: night-curfew)がASR側で空白区切りに正規化
される、(d)コンマの有無で文字列一致が崩れる、という複数の理由で、
実際には正しく生成された音声を繰り返し「不合格」と誤判定していた
(comment_4、full_story_part2、point_oneで発生)。単純な文字列包含
チェックを、句読点・改行・ハイフンを無視した「単語列の連続部分列
一致」判定へ置き換えて解消した。

### H-6. 英国綴り/米国綴りの表記差によるKey Phrase検証失敗

Key Phrase 5「personalised feeds」(英国綴り、記事本文と同じ表記)が、
Azure STT(en-US)では常に"Personalized feeds"(米国綴り)として書き
起こされるため、既存Production機構(`generate_key_phrase_component_
verified`、変更していない)の文字列比較で毎回不合格になっていた。
発音は英国綴り・米国綴りで完全に同一(s/zの綴り差のみで発音は変わら
ない)であるため、**TTS/ASR検証の入力テキストだけ**米国綴り
"personalized feeds"を使用し、表示・記録用のused_form(台本・
Artifact・本報告書)は記事本文と同じ英国綴り"personalised feeds"の
まま維持した。音声の発音内容自体は変更していない。

## I. B1 scaffold audioとしての技術QA

| 観点 | 結果 |
|---|---|
| 全11パートがTTS生成→ASR検証→合格確認を経ているか | Yes(全パートasr_verified: true) |
| 検証不合格のまま採用したパートがあるか | No |
| B2共通ニュース本文が一字一句変更されているか | No(SHA256で原本と一致確認済み) |
| Key PhrasesがEnglish→Japanese→Englishか | Yes(5件とも) |
| Support音声が本文より明確に短いか | Yes(G節、Support計84.8秒 vs News計158.4秒) |
| Spoken-first Number Treatmentは維持されているか | Yes(ER-003-B1-SCAFFOLD-01時点の監査結果を継続採用、本文は書き換えていない) |
| クリッピングが検出されたか | No(全セグメントclipping_detected: false) |

## J. Production非変更確認

- **CURRENT_SPEC.md・R4 Production prompt・TTS/audio各モジュール本体
  (er002_common.py、er002_gemini_client.py、er003_b1_p9a_audio.py、
  er003_b1_p4_audio.py、er003_v1_repro01_main_generate.py等)**: 無変更。
  新規の独立ファイル(`er003_v1_b1_scaffold_audio_01_generate.py`)から
  これらの関数を読み取り専用でimportした
- **B1専用ニュース英文生成**: 実施していない
- **B2本文rewrite**: 実施していない(H節の対処はTTS入力直前のみの
  Markdown/引用符除去であり、本文そのものは無変更)
- **A01/ADD03の音声化**: 実施していない
- **B1/B2共通化の最終決定**: 行っていない(プロトタイプ検証のまま)
- **A2仕様変更**: 実施していない
- **OPEN-35**: 変更・CLOSEしていない

## K. 今回新たに決めた暫定事項(次回検証時の参考)

- **Support(英語Comment)のTTS instruction**: ENGLISH_STYLE_PREFIX
  (「complete story読み上げ」前提の長い指示)ではなく、Key Phrase
  Componentの既存fallback経路と同じMINIMAL_INSTRUCTION_PREFIXを主
  経路として採用した。これは今回はじめて英語Comment/Previewを生成した
  ため、既存の確立済み経路が存在しなかったことによる新規判断である
- **パート間ポーズ**: 0.5秒(EN→EN間の新規territory、既存仕様の
  Comment用ポーズ(EN→JA 1.0秒/JA→EN 0.8秒)はComment自体が日本語
  だった前提のため今回は適用できず、既存の「同一言語間デフォルト」の
  値をそのまま踏襲した)

これらはいずれも今回の検証のための暫定選択であり、Production仕様への
反映は行っていない。

## 対象ファイル・新規Artifact一覧

| ファイル | 内容 |
|---|---|
| `er003_v1_b1_scaffold_audio_01_generate.py`(新規) | B1 Supported Natural English音声生成パイプライン。既存TTS/ASR/Key Phrase Production機構を読み取り専用でimport |
| `er003_output/b1_scaffold_audio_01/A02/narration/`(新規) | 全20件の新規生成音声(News5+Support5+KP英語5+KP日本語5) |
| `er003_output/b1_scaffold_audio_01/A02/b1_scaffold_final.wav`/`.mp3`(新規) | 完成版音声(4分21秒) |
| `er003_output/b1_scaffold_audio_01/A02/timeline.json`・`gain_report.json`(新規) | 組み立てタイムライン・音量調整記録 |
| `er003_output/b1_scaffold_audio_01/A02/player_final.html`(新規) | 音声Artifact原本 |
| `er003_output/b1_scaffold_audio_01/A02/audit/`(新規) | 全セグメント・Key Phraseの生成試行ログ(ASR検証結果含む) |

## 受入条件(Git操作報告)

Git操作を行った場合のcommit/push状態は、本報告の送付メッセージ末尾を参照。

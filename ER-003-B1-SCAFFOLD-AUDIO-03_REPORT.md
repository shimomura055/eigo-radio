# ER-003-B1-SCAFFOLD-AUDIO-03 実行報告(B1 Audio Language/Voice Separation 修正版)

**管理ID: ER-003-B1-SCAFFOLD-AUDIO-03**
**実施日: 2026-08-15**
**ステータス: `PROTOTYPE / EXPERIMENT`(N増し検証。Production仕様化はしていない)**

## A. Language Audit

修正着手前に、AUDIO-02完成版の全セグメントについて言語・voice・出典を
洗い出した(送付メッセージ本文の監査表を参照)。結果:

- **日本語音声は2箇所**: `Japanese title`("午前0時、SNSに"おやすみ"――
  英国が夜更かしスクロールへ静かな消灯")と`Point explanation`
  ("ポイント解説")。どちらもKey Phrase訳ではないため、B1方針
  (Key Phrase訳以外は英語のみ)に違反していた
- 独立した「Point One導入」「Point Two導入」「In One Line導入」という
  告知ナレーションは、現行Shellには**存在しない**(見出しはB2ニュース
  本文自体に組み込まれ、そのまま英語で読み上げられている)。仕様書の
  監査項目リストとは一致しない点として報告する(誤りではなく、現状の
  Shell構造がそうなっているという事実の確認)

## B. B1 Shell Changes

- **Japanese title**: 削除した。Topic introが既に英語でタイトルを
  読み上げているため(`"Today's topic is UK Plans Midnight Social
  Media Break for Teenagers."`)、英語での再読み上げ(二重読み上げ)は
  行わず、単純に該当ノードと専用pauseを取り除いた。前後の構造は
  `Topic intro → pause_0.65 → Notification 1`とし、既存のpause値
  (0.65秒)をそのまま1つ残す形にした(新しいpause秒数は作っていない)
- **Point explanation**: 役割(Preview直前の短いヘッダー)は維持した
  まま、英語ナレーション`"Here's the point."`を新規生成し差し替えた。
  この英文自体はどこにも決まっていなかったため、**今回の判断として
  選定した**(短く、自己言及的でなく、"ポイント"という原語の趣旨を
  保つ最小限の表現)。妥当性の最終確認はユーザーに委ねる
- 生成方式は、他のservice-level narration(`preview_intro`/
  `full_story_intro`等)と同じ、ENGLISH_STYLE_PREFIX経路を主体に
  MINIMAL_INSTRUCTION経路へのfallbackを備えた構成とした(HARDENING-01
  の`er003_audio_tts_asr_safety.generate_tts_with_fallback`を再利用。
  実際には主経路のみで一発成功、fallbackは発動していない)

## C. Preview Tail Investigation

ユーザー指摘の"prove"語尾切れについて、原因切り分けを行った。

| 切り分け | 結果 |
|---|---|
| A. TTS生成時点 | 生成関数はtrim後の音声のみを保存する設計のため、trim前のraw音声は直接確認不可 |
| B. ASR | 新旧どちらの版もASRは"...it not prove?"まで正しく認識(内容自体の欠落ではない) |
| C. Segment duration/waveform | **原因を特定**。旧Preview単体wavの末尾10msRMSは0.0154で、まだ有意な音量が残ったまま急停止していた。同じ生成経路を使う他segment(comment_4/comment_1/in_one_line)の末尾10msRMSは0.0009〜0.0011で、自然に無音まで減衰していた。旧Previewだけが明確な異常値だった |
| D. Assembly | 除外。np.concatenateは既存配列をそのまま連結するのみで、単体wav時点で既に欠損は発生していた |
| E. silence/trim処理 | **根本原因**。Preview/CommentはMINIMAL_INSTRUCTION経路(`repro01.generate_english_component_minimal_instruction`)で生成されており、末尾無音除去に`p3u.trim_english_keyword_silence`を使用する。このtrim関数はKey Phrase単語(短い孤立語)向けに設計されており、末尾安全マージンが固定0.08秒(`EN_TRIM_SAFETY_MARGIN_SECONDS`)しかない。Previewの19.57秒の文は"...it not prove?"という疑問形の語尾フリケイティブで終わり、そのエネルギー減衰がRMS閾値(0.02)を下回るまで0.08秒では足りず、実際にはraw音声に0.48秒の無音余地があったにもかかわらず、trimがその途中でhard cutしていた |

## D. Comment Voice(Charon適用結果)

Comment 1〜4を、B節と同じMINIMAL_INSTRUCTION経路・広げたtrimマージン
で、voiceのみCharonへ変更して新規生成した。台本(発話内容)は無変更。

| Comment | 状態 | ASR一致 | 尺 |
|---|---|---|---|
| Comment 1 | OK | 完全一致 | 6.22s |
| Comment 2 | OK | 完全一致 | 8.74s |
| Comment 3 | OK | 完全一致 | 16.93s |
| Comment 4 | OK | 完全一致 | 14.00s |

過去記録上、Charonは本プロジェクトで既にナレーター実績のあるvoice
(`er001b2_narrator_compare.py`、`er002_s3_config.py`のA02/A06記事等)
であることを確認した。演技指示は既存のMINIMAL_INSTRUCTION_PREFIX
("Speak the following text aloud naturally and clearly, in a warm
podcast announcer voice.")をそのまま使用し、新しい演技指示は作って
いない(過剰にゆっくり・説教的等にはしていない)。

Previewは今回voiceを変更していない(現状のまま、tail修正のみ適用)。
News本文(Full Story/Point/In One Line)・Key Phrasesも無変更。

## E. Key Phrases

変更なし。English→Japanese→Englishの提示構造、prosody、phoneme、
グルーピングはすべてAUDIO-01/02から無変更で再利用した(音声ファイル
自体も再生成していない)。B1で唯一許可された日本語領域として維持。

## F. B2 Shared News

Full Story Part1/Part2、Point One/Two、In One Lineの音声・テキストは
一切変更していない。SHA256確認により、今回もB2 V2記事本文との完全
一致(`match: true`)を確認した。既存のASR検証済み音声
(`er003_output/b1_scaffold_audio_01/A02/narration/`)をそのまま
再利用している。

## G. Full Timeline(Language / Voice込み)

全27音声セクション(pause除く)。詳細はArtifact内のFull Timeline表、
および`er003_output/b1_scaffold_audio_03/A02/audit/timeline.json`参照。

| # | Section | Language | Voice | Dur | New/Reused |
|---|---|---|---|---:|---|
| 1 | Intro | — | — | 10.74s | Reused(A2既存) |
| 2 | Welcome | English | Aoede | 2.11s | Reused |
| 3 | Topic intro | English | Aoede | 5.37s | Reused |
| — | ~~Japanese title~~ | ~~Japanese~~ | ~~Aoede~~ | — | **削除(AUDIO-02では存在)** |
| 4 | Notification 1 | — | — | 2.04s | Reused |
| 5 | Preview intro | English | Aoede | 1.45s | Reused |
| 6 | Point explanation (EN) | English | Aoede | 0.95s | **New(英語化)** |
| 7 | Preview | English | Aoede | 22.64s | **New(tail修正)** |
| 8 | Notification 2 | — | — | 2.04s | Reused |
| 9 | Key phrases intro | English | Aoede | 1.89s | Reused |
| 10-14 | Key Phrase 1〜5 | English + Japanese | Aoede | 33.19s(計) | Reused(AUDIO-01) |
| 15 | Notification 3 | — | — | 2.04s | Reused |
| 16 | Full story intro | English | Aoede | 1.87s | Reused |
| 17 | Comment 1 | English | **Charon** | 6.22s | **New(Charon化)** |
| 18 | Full Story Part 1 | English | Aoede | 39.97s | Reused(B2共通) |
| 19 | Comment 2 | English | **Charon** | 8.74s | **New(Charon化)** |
| 20 | Full Story Part 2 | English | Aoede | 55.23s | Reused(B2共通) |
| 21 | Comment 3 | English | **Charon** | 16.93s | **New(Charon化)** |
| 22 | Point One | English | Aoede | 28.81s | Reused(B2共通) |
| 23 | Point Two | English | Aoede | 22.13s | Reused(B2共通) |
| 24 | Comment 4 | English | **Charon** | 14.00s | **New(Charon化)** |
| 25 | In One Line | English | Aoede | 12.29s | Reused(B2共通) |
| 26 | Outro | — | — | 6.14s | Reused(A2既存) |

**合計: 309.52秒(5分9秒)**。AUDIO-02(316.33秒)からの差は、主に
Japanese title削除(約7秒)による短縮。

## H. Japanese Residual Audit

機械判定(発話テキスト中の日本語文字有無をtimeline全セクションで
照合)を実施した。1回目の実行では、監査スクリプト自身のプレースホルダ
テキスト(News本文セクションに"（B2共通ニュース本文、英語）"という
日本語の説明文を暫定的に入れていた)が原因で5件の偽陽性
(`UNEXPECTED_JAPANESE`)を検出したが、これは**音声の不具合ではなく
監査コード側のバグ**と判明したため、実際のB2英語本文テキストに
差し替えて再計算した。

| 結果 | 件数 |
|---|---|
| Key Phrases(日本語訳、想定通り) | 5件 |
| それ以外の想定外の日本語 | **0件** |

期待値(Key Phrases以外の日本語0件)を満たしている。

## I. Audio QA / ASR

| 項目 | 結果 |
|---|---|
| Introあり | OK |
| Outroあり | OK |
| SFX/Notificationあり(3箇所) | OK |
| B1 Shell narrationは英語 | OK(Japanese title削除、Point explanation英語化) |
| Key PhrasesのみE→J→E | OK(無変更) |
| Key Phrase以外の日本語なし | OK(H節) |
| Preview末尾自然 | OK(C節、末尾RMS 0.0154→0.00007) |
| Comment 1〜4 = Charon | OK(D節) |
| News body = 従来voice(Aoede) | OK(F節、無変更) |
| B2 text完全一致 | OK(SHA一致) |
| Support Fact-safe | OK(AUDIO-01のLEDGER_COMPLIANT/PASSを継承。台本自体を今回変更していないため未再検証) |
| ASR PASS(全新規音声) | OK(point_explanation_en/preview/comment_1-4、計6件全て合格) |
| head/tail cutなし | OK(新規6件すべて末尾10ms RMSが0.0001〜0.0004の自然減衰レンジ) |
| duplicateなし | OK |
| section order正常 | OK |
| pause仕様維持 | OK(全pause値AUDIO-02から無変更) |
| clippingなし | OK(peak 0.95307、`measure_metrics`のclipping_detected: false) |

**peak値についての補足**: AUDIO-02(0.862)からAUDIO-03(0.953)へ
上昇しているが、これはPreview再生成によりtarget_rmsアンカーが微小に
変化した結果、既存のgain上限キャップ(ピークが0.95を超えないよう
`compute_gain_for_target_rms`が制御する仕組み、A2から無変更)に
複数segment(Point One/Full Story Part2)が到達したためであり、
clippingは発生していない。ゲイン計算方式自体は変更していない。

## J. Final Artifact

**URL**: https://claude.ai/code/artifact/dbb9767a-eab5-485a-8129-3f5e77a4b520

以下4種を掲載:
- A. 完成版フル音声(Intro〜Outro、309.52秒)
- B. Preview Before/After比較(語尾修正の確認)
- C. Comment 1 voice比較(旧Aoede版 / 新Charon版)
- Full Timeline表・日本語残存Audit表・Full Audio QAチェックリスト

## K. Production非変更確認

- CURRENT_SPEC.md・DECISION_LOG.md・A2最終承認script
  (`er003_v1_a2_audio_ab_01_generate.py`)・その他Production audio
  モジュール本体: 無変更。新規独立ファイル
  (`er003_v1_b1_scaffold_audio_03_generate.py`)から関数・定数を
  読み取り専用でimportした
- `p3u.trim_english_keyword_silence`関数自体は変更していない
  (呼び出し時の`safety_margin_seconds`引数のみ、長文向けに0.35秒を
  指定。関数のデフォルト値0.08秒はKey Phrase単語向けとして無変更)
- 23節に列挙された非スコープ項目(Preview男性化、Key Phrase仕様変更、
  B2ニュースvoice変更、B1本文rewrite、A2変更、B1/B2共通化Production
  確定、新規SFX設計、Production仕様変更、OPEN-35処理)はいずれも
  行っていない
- HARDENING-01の成果(`er003_audio_tts_asr_safety.py`)を、指示section
  17に従い安全に再利用した(`generate_tts_with_fallback`/
  `validate_asr_match`)。大規模refactorは行っていない

## L. Git

commit/push結果は、本報告の送付メッセージ末尾を参照。

## 対象ファイル一覧

| ファイル | 内容 |
|---|---|
| `er003_v1_b1_scaffold_audio_03_generate.py`(新規) | Shell英語化・Preview tail修正・Comment Charon化・再assembleスクリプト |
| `er003_output/b1_scaffold_audio_03/A02/narration/`(新規) | point_explanation_en/preview/comment_1-4_charon等の新規音声 |
| `er003_output/b1_scaffold_audio_03/A02/assembled/`(新規) | 完成版v3 wav/mp3(309.52秒) |
| `er003_output/b1_scaffold_audio_03/A02/audit/`(新規) | timeline.json・gain_report.json・japanese_residual_audit.json・各種生成結果json |
| `ER-003-B1-SCAFFOLD-AUDIO-03_REPORT.md`(新規) | 本報告書 |

## 受入条件チェック

| 条件 | 結果 |
|---|---|
| AUDIO-02全セグメント言語Audit実施 | 済(A節) |
| B1で不要な日本語箇所を全件特定 | 済(A節、2箇所) |
| Key Phrases以外の日本語読み上げを0にする | 済(H節) |
| B1用Title/Preview等英語音声を必要に応じ新規生成 | 済(B節、Point explanation英語版) |
| Preview prove切れ原因を特定 | 済(C節) |
| Preview末尾自然化 | 済(C節、末尾RMS 0.0154→0.00007) |
| Comment 1〜4をCharon化 | 済(D節) |
| Comment本文は変更しない | 済(台本無変更) |
| B2 News本文変更なし | 済(F節、SHA一致) |
| ASR検証PASS | 済(I節) |
| Fact Safety維持 | 済(AUDIO-01の検証結果を継承、台本無変更のため再検証不要と判断) |
| A2 Audio Shellの非言語部分維持 | 済(SFX配置・pause値等無変更) |
| 完成版フル音声再assemble | 済(309.52秒、clippingなし) |
| Artifactで通し試聴可能 | 済(J節) |
| 日本語残存Audit結果報告 | 済(H節) |
| voice別Timeline報告 | 済(G節) |
| Production非変更 | 済(K節) |
| commit/push/status報告 | 本報告書末尾参照 |

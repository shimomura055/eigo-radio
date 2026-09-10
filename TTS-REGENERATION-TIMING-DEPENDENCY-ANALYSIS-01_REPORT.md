# TTS-REGENERATION-TIMING-DEPENDENCY-ANALYSIS-01 調査報告

読み取り専用調査(¥0、API呼び出しなし、編集・Git操作なし)。CAR-T記事(Trial-09)B1B `full_story_part1` の「3回連続ASR NG(TRUE_CONTENT_MISMATCH、"a report on"の読み落とし)→約14時間21分後の4回目でPASS」という1件について、過去ログを横断集計し、時間依存性(TTSの再生成間隔とPASS率の関係)を検証した。

## サマリー(結論を先に)

1. **判定: 時間依存性「なし」〜「判断材料不足」。今回1件の成功だけでは「時間を置けば改善する」と結論できない。**
2. 「長い間隔(30分以上)を置いた再挑戦」のサンプルはN=3しかなく、うち1件(kp5_ja_charon、間隔39分)は**失敗**している。時間を置いても直らなかった反証事例が存在する。
3 入力同一性: CAR-T事例のcanonical_text(仕様本文)はold_entry/new_entryで完全一致(バイト同一)。voice/model/instruction_typeも4回とも同一。regen記録自身が「同一引数、Prompt/本文は無変更」と明記。ただし**attempt1〜3個別の生TTS入力文字列("text"引数)はper-attempt形式では保存されておらず、完全なバイト同一性は直接検証不能**(データ欠落、下記参照)。
4. システム全体(417件のattempt記録)でattempt番号が進むほどPASS率が低下する傾向(attempt1: 90.6%→attempt3: 53.3%)が見られるが、これは「後まで残る=難しいsegmentの選択効果」で説明可能であり、時間経過による改善とは別の現象。
5. 類似の「複数回連続失敗→後で解決」事例(household topic_intro、6回連続FAIL)は、**音声バイト不変のままASR手法変更で事後的にPASS**と判明しており、"時間が解決した"のではなく"検証方法が変わった"ケースだった。これは時間依存性を支持しない反証として重要。

## 1. 横断集計

### 1-1. システム全体のattempt番号別PASS率(N=417件、`er0*_output/**/attempts/*.json` 全件走査)

| attempt番号 | 総数 | PASS(verified=true) | PASS率 |
|---|---|---|---|
| 1 | 318 | 288 | 90.6% |
| 2 | 76 | 61 | 80.3% |
| 3 | 15 | 8 | 53.3% |
| 4 | 5 | 3 | 60.0% |
| 5 | 1 | 0 | 0.0% |
| 6 | 1 | 0 | 0.0% |
| 7 | 1 | 1 | 100.0% |

出典: `er0*_output/**/attempts/*.json` 中の `audio_classification`/`verified`/`attempt_number(or attempt)` フィールドをPython集計。分類内訳: NORMALIZED_MATCH 259, EXACT_MATCH 79, TRUE_CONTENT_MISMATCH 42, PHONETIC_MATCH 21, ほか少数。
**解釈上の注意**: attempt3以降のN(15,5,1,1,1)は極小。PASS率の低下は「3回目以降まで残るのは元々難しいsegmentだけ」という選択効果(生存バイアス)が主因と考えられ、時間経過そのものが原因である証拠ではない。

### 1-2. NG直後の次attemptまでの時間間隔別PASS率(同一segmentの連続attemptを時系列ソートし、直前がNGだった遷移のみ抽出)

| 間隔区分 | N(遷移数) | 次attemptがPASSした数 | PASS率 |
|---|---|---|---|
| (a) 短間隔(<5分、同一runの連続リトライ相当) | 48 | 27 | 56.2% |
| (b) 中間隔(5〜30分) | 1 | 1 | 100.0%(N=1、参考値) |
| (c) 長間隔(30分以上、Lock解除後の再生成相当) | 3 | 2 | 66.7% |

出典: 同上スクリプトで `(theme_id, level, segment_id)` ごとに `saved_at` を時系列ソートし、`verified=false` の直後attemptとの時刻差を計算。
**(c)長間隔=N=3の内訳(全件記載、隠蔽なし)**:
- `family_a_completion_a2_trend_end_to_end_01/b1b/kp5_ja_charon` attempt3→4、間隔39.2分、**PASS=False(失敗)**
- `news_stage3_new_theme_ledger_trial_09_b1b_full/b1b/full_story_part1` attempt3→4、間隔860.6分(≒14時間21分)、PASS=True(今回のCAR-T事例)
- `editorial_b_voices_trial_09_audio/b1b/point_two_heading` attempt1→2、間隔139.3分(≒2時間19分)、PASS=True

**(a)と(c)の差(56.2% vs 66.7%)はN=3対N=48で信頼区間が極めて広く、統計的に有意な差とは言えない。むしろ(c)には明確な失敗例が1/3含まれており、「時間を置けば直る」を裏付ける決定的パターンにはなっていない。**

## 2. 事例一覧

### 事例1: CAR-T `full_story_part1`(今回の対象、Trial-09)
- attempt1(2026-09-09 19:28:19)〜attempt3(19:29:43): 全てTRUE_CONTENT_MISMATCH。3回ともASRテキストから"a report on"が欠落(例: "...a medical journal published a new gene treatment..." で "a report on" が抜けている)。attempt間隔は37〜47秒(同一run内の即時リトライ)。
- attempt4(2026-09-10 09:50:18、ユーザー承認済み再生成): NORMALIZED_MATCH、PASS。ASRテキストに"a report on"が含まれる。
- 出典: `er011_output/news_stage3_new_theme_ledger_trial_09_b1b_full/b1b/audit/regen01_full_story_part1_family_a_news_stage3_new_theme_ledger_trial_09.json`、同`narration/attempts/full_story_part1_attempt{1,2,3,4}_*.json`

### 事例2: Household `fact03_fix_02` point_one(2026-09-09)
- attempt1(17:40:37)〜attempt3(17:41:13): 全てTRUE_CONTENT_MISMATCH(間隔17〜19秒の即時リトライ)。失敗内容は句読点・ハイフン化の揺れ("shortcut—fruit"のem-dash処理、"high humidity"のハイフン有無等)で、CAR-T事例のような単語欠落ではない。
- 出典: `er003_output/n3_01/household/fact03_fix_02/b1b/narration/attempts/point_one_attempt{1,2,3}_*.json`(この3回で尽きた後の解決経路は本調査では未追跡)

### 事例3: `family_a_completion_a2_trend_end_to_end_01` kp5_ja_charon(日本語キーフレーズ、2026-09-09)
- attempt1〜3(13:44:13〜13:44:20、間隔3〜4秒): 全てTRUE_CONTENT_MISMATCH。
- 39分の間隔(→14:23:30)を置いたattempt4: **依然TRUE_CONTENT_MISMATCH(失敗)**。
- attempt5〜6(14:23:34〜14:23:37、間隔3〜4秒): 全てTRUE_CONTENT_MISMATCH。
- さらに5分の間隔(→14:28:19)を置いたattempt7: EXACT_MATCH、PASS。
- 合計7回中6回NG、最終的にPASSしたのは通算7回目。**39分の間隔を置いても直らなかった明確な反証**であり、「時間を置けば改善する」という単純な仮説と矛盾する。
- 出典: `er011_output/family_a_completion_a2_trend_end_to_end_01/b1b/narration/attempts/kp5_ja_charon_attempt{1..7}_*.json`、`e2e_run_summary.json`(kp5_japaneseがSTOPPED→GATE_BLOCKEDとして記録)

### 事例4: `in_one_line`(CAR-T記事と同一Trial-09内、2026-09-09 19:32台)
- attempt1: TRUE_CONTENT_MISMATCH(失敗理由はCAR-T本文と異なり、"CD19 CAR T-cell"の重複挿入という付加型エラー。length_ok=falseも同時発生)。
- attempt2(同一run内の短時間リトライ): NORMALIZED_MATCH、PASS。
- 出典: `er011_output/news_stage3_new_theme_ledger_trial_09_b1b_full/b1b/audit/tts_generation_results.json`(segments.in_one_line.attempts_log)

### 事例5: Household `household_unified_final_candidate_01` comment_3の"prevent"→"perfect"誤認識(ユーザー指摘、2026-09-10)
- attempt1(2026-09-09 20:25:44): 主ASR(asr_text)はNORMALIZED_MATCHでPASSしていたが、**独立したdisfluency QA用ローカルASR(faster_whisper_small_local_verbatim)のみ**が"prevent"を"perfect"と誤認識(ユーザー試聴指摘箇所と一致)。
- 約10時間34分後のattempt2(2026-09-10 06:59:41): 同ローカルASRが"prevent"を正しく認識。
- ただしこれは主分類(audio_classification)が最初からPASSだったケースであり、CAR-T事例(主ASRがNG)とはメカニズムが異なる。新規TTS音声が実際に生成されている(duration 17.531s→17.291sで異なる)ため、「音声が変わったから直った」のか「ASR側の偶然」なのか切り分け不能。
- 出典: `er011_output/household_unified_final_candidate_01/b1b/audit/segfix_comment3_prevent_pronunciation_pm_closeout_consolidation_64.json`、同`narration/attempts/comment_3_attempt{1,2}_*.json`

### 事例6(最重要の反証候補): Household `fact03_fix_02` topic_intro / kp2_english の"CRISPR"誤認識(2026-08-17実行、2026-09-09に事後判明)
- 2026-08-17時点でtopic_introは**6回連続attempt全てFAIL**(ASR判定)。原因は"crisper"(引き出しの意)をASRが"CRISPR"(遺伝子編集技術の略称)と一貫して聞き間違えていたこと。
- 重要: **音声バイトは一度も変わっていない(音声byte不変)**。2026-09-09になって、現行の改良版ASR cascade(Primary OpenAI×2 + entity_like判定でSecondary Azureへエスカレーション)で同一音声を再照合したところNORMALIZED_MATCHでPASSした。
- つまりこの「6回連続NG→後で解決」は**時間経過やTTS再生成が原因ではなく、ASR検証方式そのものが変わった(改善された)ことが原因**。「時間を置いたら直った」ように見えても、実際は「検証ロジックが変わった」だけの可能性があることを示す直接証拠。
- 出典: `er003_output/n3_01/household/fact03_fix_02/b1b/audit/human_approved_segments.json`(topic_intro、kp2_englishのnote/asr_reverify_evidence/asr_homophone_evidence)

## 3. 今回事例(CAR-T)の入力同一性確認

- `canonical_text`(記事仕様本文、句読点・改行・スペル込み): old_entry(attempt1〜3が参照した値)とnew_entry(attempt4)で**完全一致**(改行位置・em dash・カーブクォート含めバイト同一)。出典: `regen01_full_story_part1_family_a_news_stage3_new_theme_ledger_trial_09.json` L79とL267。
- `voice`="Aoede"、`model`="gemini-2.5-pro-preview-tts"、`tts_execution_mode`="STANDARD"、`route`/`instruction_type`="english_style_prefix_wide_margin"は4回のattempt jsonすべてで同一値。
- regen記録の`reason`フィールドに「元のfull_story_part1呼び出しと同一引数[disfluency_qa=False, enable_connected_speech_equivalence_layer=True, enable_repetition_qa=True]で再生成した。Prompt/本文は無変更」と明記(システム側の申告)。
- **データ欠落(確認できなかった点)**: attempt1〜3個別に実際TTS APIへ渡された生の"text"引数(canonicalizationで数字表記・引用符などが正規化された後の最終文字列)は、per-attempt JSONには保存されておらず(asr_textという出力側のみ記録)、segment単位の集約ファイル`tts_generation_results.json`は再生成後に最終状態(attempt4分)へ上書きされているため、attempt1〜3が実際に投入した"text"文字列そのものをバイト単位で遡って確認することはできなかった。したがって「4回とも完全に同一の入力だった」という結論は、canonical_text一致・route/voice/model一致・システム申告の3点からの**強い推定**であり、100%の直接証拠ではない。
- sha256(生成音声のハッシュ)は4回とも相違(9c1d515b.../0752cd17.../d1e84382.../076b7a18...)。同一入力からでもTTS生成自体が毎回異なる音声を生成する(=確率的生成であり、キャッシュ再利用ではない)ことは確認できた。

## 4. 考えられる説明(ログで確認できるもの/できないもの)

| 仮説 | ログで確認できるか | 所見 |
|---|---|---|
| TTSのサンプリング/温度による確率的ゆらぎ | できる(部分的) | sha256が4回とも異なり、同一入力でも毎回異なる音声波形が生成されている。TTS自体が非決定的であることは確認できる。 |
| TTSモデルのバックエンド更新(サイレント) | できない | `model`フィールドは4回とも"gemini-2.5-pro-preview-tts"で不変。ただしこのフィールドは呼び出し側が指定した論理モデル名であり、Google側のバックエンド実体が無断更新された場合はログに現れない。判断不能。 |
| キャッシュ/音声再利用 | 否定できる | sha256が毎回異なり、`saved_at`も個別に記録されており、新規生成であることが確認できる。 |
| 入力テキストの微差(前処理・改行・style prefix) | 概ね否定できる(ただし直接証拠は不完全) | canonical_text/route/voice/modelは完全一致。ただし3-節で述べた通りattempt1〜3個別の最終投入文字列は直接保存されておらず、完全なバイト同一性の証明はできない。 |
| ASR側のゆらぎ(独立ローカルASRの有無・ASR自体の非決定性) | できる | `er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`(N=31)で、同一音声・同一プロバイダ(openai_asr)への2回の独立呼び出し(primary_1/primary_2)でテキストが異なった割合は24/31(77.4%)。ただし分類(classification)自体が食い違った例は0/31で、今回のような「a report on」丸ごと欠落タイプの誤りとは性質が異なる可能性がある。事例6(CRISPR誤認識)はASR側の系統的誤認識(ホモフォン)が主ASR単発判定では6回連続で解消しなかった直接証拠。 |
| Human Review Lock解除に伴う運用上の別経路(regenerate関数自体の違い) | できる | CAR-T attempt4は`review_lock.approve_regenerate` + `news_tail_fix.generate_news_narration_wide_margin`という既存segment再生成経路を使用しており、経路自体はattempt1〜3の元呼び出しと同一と申告されている(3-節参照)。経路の違いによる説明は薄い。 |
| 時間経過そのものによる何らかの改善(仮説の核心) | 支持する直接証拠なし、反証あり | 1-2節(c)のN=3中1件(kp5_ja_charon)は39分の間隔を置いても失敗。事例6は音声バイト不変のままASR方式変更で解決しており「時間」自体が原因ではなかった。今回のCAR-T 1件の成功だけで時間依存性を主張する根拠は薄い。 |

## 5. 判定と根拠

**判定: 時間依存性「なし」〜「判断材料不足」(いずれの表現でも「あり」と断定はできない)。**

根拠:
1. 長間隔(30分以上)での「NG直後の再挑戦」サンプルはN=3のみで、うち1件(kp5_ja_charon、39分)は失敗している。今回のCAR-T事例(14時間21分でPASS)はこのN=3中の1件に過ぎず、単独の成功例から一般化はできない。
2. 短間隔(<5分)でのPASS率(56.2%、N=48)と長間隔でのPASS率(66.7%、N=3)の差は、N=3の極小サンプルにより信頼区間が非常に広く、統計的に意味のある差とは言えない。
3. 類似の「複数回連続失敗→後で解決」事例(事例6、household topic_intro)では、解決の原因が時間経過ではなくASR検証方式の変更であったことが記録上明確であり、「時間が経てば直る」という表層パターンの裏に別要因が隠れている可能性を具体的に示している。
4. CAR-T事例のTTS入力(canonical_text/voice/model/route)はattempt1〜4で一致していることが強く推定されるが、attempt1〜3個別の生入力文字列は直接保存されておらず完全な同一性証明はできない(3節のデータ欠落)。この欠落自体が「4回目だけ入力が違って偶然直った」可能性を完全には排除できないことも意味する。

## 6. 観測項目案(Production retry仕様の変更提案ではなく、将来の観測強化案のみ)

- 各attemptで実際にTTS APIへ渡した最終"text"文字列(canonicalization後)をper-attempt JSONに保存し、regen前後の入力同一性を機械的に検証可能にする。
- 長間隔での再挑戦(Human Review Lock解除後の承認済み再生成)を専用ログとして時系列蓄積し、N数を意図的に増やしてから時間依存性を再評価する(現状はN=3で結論不能)。
- ASR側の独立2回判定(primary_1/primary_2相当)をTRUE_CONTENT_MISMATCH系の欠落型エラーにも適用し、「TTSが本当に読み落としたのか」「ASRが聞き落としたのか」を切り分けられるようにする。
- 可能であればTTSプロバイダ側のモデルバージョン/リビジョン情報(取得できる場合)をログへ記録し、サイレントなバックエンド更新の可能性を後から検証できるようにする。

## 7. QCD

- Quality(品質): 読み取り専用、API呼び出しなし(¥0)。集計スクリプトはローカルJSON走査のみ。人手確認箇所(CAR-T regen記録、household 3事例)は原文を直接読み込み転記。
- Cost(コスト): ¥0(Trial実行・API呼び出しなし)。
- Duration(所要): 本調査セッション内で完了(1回のログ横断調査)。

## 出典ファイル一覧(主要)

- `er011_output/news_stage3_new_theme_ledger_trial_09_b1b_full/b1b/audit/regen01_full_story_part1_family_a_news_stage3_new_theme_ledger_trial_09.json`
- `er011_output/news_stage3_new_theme_ledger_trial_09_b1b_full/b1b/audit/tts_generation_results.json`
- `er011_output/news_stage3_new_theme_ledger_trial_09_b1b_full/b1b/audit/review_lock_state.json`
- `er011_output/news_stage3_new_theme_ledger_trial_09_b1b_full/b1b/narration/attempts/full_story_part1_attempt{1,2,3,4}_englishstyleprefixwidemargin.json`
- `er003_output/n3_01/household/fact03_fix_02/b1b/narration/attempts/point_one_attempt{1,2,3}_englishstyleprefixwidemargin.json`
- `er003_output/n3_01/household/fact03_fix_02/b1b/audit/human_approved_segments.json`
- `er011_output/family_a_completion_a2_trend_end_to_end_01/b1b/narration/attempts/kp5_ja_charon_attempt{1..7}_*.json`
- `er011_output/family_a_completion_a2_trend_end_to_end_01/e2e_run_summary.json`
- `er011_output/household_unified_final_candidate_01/b1b/audit/segfix_comment3_prevent_pronunciation_pm_closeout_consolidation_64.json`
- `er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`
- `er012_output/editorial_b_voices_trial_09_audio/b1b/narration/attempts/point_two_heading_attempt{1,2}_englishstyleprefix.json`

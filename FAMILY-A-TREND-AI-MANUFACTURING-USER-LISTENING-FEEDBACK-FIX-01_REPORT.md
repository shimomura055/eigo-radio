# FAMILY-A-TREND-AI-MANUFACTURING-USER-LISTENING-FEEDBACK-FIX-01

管理ID: FAMILY-A-TREND-AI-MANUFACTURING-USER-LISTENING-FEEDBACK-FIX-01
実施日: 2026-09-13(UTC 2026-09-12 22:33〜22:44)
対象: `er011_output/family_a_trend_ai_manufacturing_prod_run_01/`
種別: ユーザー視聴Feedback(2026-09-13、承認済み)への**個別対応**。新しい
一般仕様の追加ではない。Git操作は本タスクでは行っていない(後続の統合
タスクでcommit予定)。

---

## 1. A2「## Main story」混入の原因

### 1.1 原因箇所

`er003_v1_n3_01_scaffold_generate.py::split_article_text()`(115行目)。

```python
intro_text = text[title_match.end():h3_matches[0].start()].strip() if title_match else text[:h3_matches[0].start()].strip()
```

この関数は、記事本文のH1タイトル直後から最初の`### `見出し(Point One相当)
までの範囲を丸ごと`intro_text`として取り出し、段落単位(`\n\n`区切り)で
語数バランス分割してMain Storyの`part1`/`part2`を作る(137〜152行目)。
`## In one line…`より前に現れる**それ以外の`## `見出し行**(今回は
`## Main story`)を除去する処理が存在せず、見出し行がそのまま最初の段落
として`part1`側の本文に混入していた。

`a2/article.md`は下記の構造になっていた(WriterのLLM出力が、指示していない
`## Main story`という飾りの小見出しを自発的に追加したもの。Writerの
prompt自体にこの見出しを要求する記述は無い):

```
# The AI Factory Story Has Two Different Clocks

## Main story

As of September 2026, the factory AI story has two clocks.
...
```

この結果、`a2/parts.json`の`part1`先頭に`"## Main story\n\n..."`が literal
に残り、実際のTTS入力・ASR結果にも
`"Main story. As of September 2026, ..."`として音声化されていた
(修正前`audit/tts_generation_results.json`の`asr_text`で確認済み)。

### 1.2 他segment/他記事への同型混入チェック(Grepのみ、修正対象外)

- 今回対象記事(`family_a_trend_ai_manufacturing_prod_run_01`)の`b1b/article.md`
  には`## Main story`相当の見出しは存在しない(B1側は無事故)。
- `er011_output/**/parts.json`全件(現存ファイル)を走査した結果、
  `part1`/`part2`に`##`を含むものは**今回の1件のみ**(修正後は0件)。
- 名指しされたTrial-11(`discovery_generalization_towels_trial_11`)・
  Trial-12(`discovery_generalization_wake_before_alarm_trial_12`)配下の
  `article.md`には`## Main Story`類の混入は**無い**(Grep 0件)。
- 参考情報(対応不要、列挙のみ): リポジトリ全体の`article.md`を広く
  Grepすると、過去の別Trialのドラフト段階ファイル16件
  (`news_focus_hint_comparison_trial_06`・`point_overlap_gap_fix_trial_05`・
  `discovery_stage4_cautionary_language_trial_10`・
  `news_ledger_enrichment_ab_trial_12`・
  `open112_trend_synthesis_minimal_prompt_trial_09`配下の`run1`/`run2`/
  `gapfix`等のサブパス)にも同種の`## Main Story`見出しが見つかった。
  ただしこれらは対応する`parts.json`が存在しない(=採用されなかった
  draft、音声化まで到達していない)ため実害は確認されていない。本タスクの
  修正対象外、実装は行っていない。

### 1.3 修正方針(Production関数は無変更)

`split_article_text()`自体は一切変更していない。代わりに、**artifact側**
である`a2/article.md`から不要な`## Main story`見出し行を手動で除去した上で、
無変更のまま同関数を再実行して`a2/parts.json`を作り直した(同一関数・
修正済み入力→正しい出力、という「artifact側の整形」)。`part2`以下の
全フィールドは変化していないことをscriptでassert済み。

---

## 2. 変更内容

### 2.1 A2: `## Main story`除去 + `full_story_part1`再生成

1. `er011_output/family_a_trend_ai_manufacturing_prod_run_01/a2/article.md`:
   `## Main story`見出し行(2行、見出し自体+直後の空行)を削除。
2. `sc.split_article_text()`(無変更)を修正後article.mdへ再実行し、
   `a2/parts.json`を再生成(`part1`から見出し除去、`part2`以下は不変を
   assert済み)。
3. `n3.generate_a2_segment_with_slowdown()`(無変更、既存
   `generate_a2_segments()`がfull_story_part1へ渡すのと同一の引数:
   `style_prefix_override=A2_ENGLISH_STYLE_PREFIX_SLOWER`、
   `disfluency_qa=False`、`enable_connected_speech_equivalence_layer=True`、
   `enable_repetition_qa=True`)で`narration/full_story_part1.wav`のみ
   再生成。
   - 結果: `status=OK`、`asr_verified=True`、
     `asr_text="As of September 2026, the factory AI story has two clocks. ..."`
     (「Main story」の混入無し)。`slowdown_applied=True`(A2必須6%
     time-stretchも実施・内蔵ASR再検証込み)。
   - Repetition QA(OPEN-121相当): `repetition_qa_checked=True`、
     `flagged=False`(不発火)。
   - Connected Speech Equivalence Layer: 実行、`connected_speech_info=None`
     (問題無し、fallback不要)。
   - Human Review Lock: 新規エントリなし(`review_lock_state.json`に
     `full_story_part1`の新規状態追加なし)。
4. `audit/tts_generation_results.json`の`segments.full_story_part1`を
   新結果へ更新。

### 2.2 B1: Key Phrase 1 `not there yet` → `autonomous`

ユーザー向け表記は本ReportおよびREADME上「B1」と呼ぶ(内部dir/ファイル名
`b1b`はrename不要、そのまま)。

1. `b1b/key_phrases/keywords_canonicalized.json`のrank1エントリを手動更新
   (既存Production canonicalization/redundancy関数は再実行していない、
   ユーザー指定の個別差替):
   - `source_span`/`display_phrase`/`key_phrase`/`used_form`:
     `"not there yet"` → `"autonomous"`
   - `source_sentence`: `b1b/article.md`本文中の実際の用例
     `"So the big change is not that factories have already become autonomous."`
   - `japanese_gloss`/`japanese_gloss_tts`: `"人の手を借りずに自分で動く"`
     (同記事内の実際の文脈["factories have already become autonomous"]に
     基づく訳。既存の他エントリと同じ「短い名詞句/description」形式)。
   - `qa`ブロック: `null`に変更、`qa_overall_status`を
     `"MANUAL_OVERRIDE_NOT_RERUN"`に変更(旧`not there yet`向けのPASS結果を
     新phraseへ誤って流用しないため)。`reasoning`に差替理由を明記。
2. `n3.shared_narration.ensure_key_phrase_english_component()` +
   `n3.generate_charon_japanese_with_reading_safety()`(いずれも無変更、
   既存`generate_b1_segments()`がKey Phrase 1へ渡すのと同一引数)で
   `narration/kp1_en.wav`・`narration/kp1_ja_charon.wav`を再生成。
   - 英語: `status=OK`、`asr_text="Autonomous"`、`asr_verified=True`。
   - 日本語: `status=OK`、`asr_text="人の手を借りずに、自分で動く。"`、
     `asr_verified=True`、`reading_safety_changed_text=False`(OPEN-145
     相当の読み曖昧性なし、不発火)。
3. `audit/tts_generation_results.json`の`key_phrases["1"]`を新結果へ更新。

### 2.3 Assembly / Audio Validation Gate 再実行

`er003_v1_n3_01_assemble.py::stage_assemble_a2()`/`stage_assemble_b1()`
(いずれも無変更)を再実行。

| Level | Assembly(既定OFF経路) | Gate opt-in ON(OPEN-129 required_structure) | duration | peak | clipping |
|---|---|---|---|---|---|
| A2 | PASS | PASS | 359.462s(旧361.075s) | 0.95202 | False |
| B1(b1b) | PASS | PASS | 393.094s(旧391.484s) | 0.95049 | False |

### 2.4 標準player再生成 + 表示ラベル「B1B」→「B1」

- `er011_family_a_trend_synthesis_ai_manufacturing_production_run_01_b1b_player.py`:
  `<title>`・`<h1>`・`<h2>`×2・注記文中の表示ラベルを`B1B`→`B1`へ変更
  (`THEME_ID`/`B1_DIR`等の内部識別子・`b1b`ディレクトリ名・出力ファイル名
  `index.html`は維持)。
- `er011_family_a_trend_synthesis_ai_manufacturing_production_run_01_a2_player.py`:
  `B1B`表記なし(変更不要)。
- 両player scriptを再実行し、`player_std/index.html`(B1)・
  `player_std/a2_index.html`(A2)を再生成。

**発見した既存の不具合(このタスクで修正・報告のみ、Production関数では
ないため対応済み)**: 両player scriptの`wav_to_mp3_url()`/
`episode_mp3_url()`は`if not os.path.exists(out_path):`でmp3変換を
スキップする設計のため、既存のmp3(`full_story_part1.mp3`・`kp1_en.mp3`・
`kp1_ja_charon.mp3`・`a2_episode.mp3`・`b1b_episode.mp3`)が残っていると、
wav側を再生成してもplayerは**古い音声を配信し続ける**(サイレントな
キャッシュ問題)。今回はこれに気づき、該当5ファイルを削除してから
player scriptを再実行することで正しい新音声に更新した(スクリプト自体は
無変更)。この設計(存在すれば無条件で再利用)は本記事のplayer script
固有ではなく、同一パターンを使う他のper-theme player script
(`audio_review_player.py`利用箇所)全般に共通する潜在リスクであり、
一般修正の要否は本タスクの範囲外のため**Fable/ユーザーへ報告のみ**
(実装しない)。

---

## 3. 費用(5区分、JPY、実測)

| 区分 | 金額 | 内訳 |
|---|---|---|
| ①今回実測(Standard同期、3segment[A2 full_story_part1・B1 kp1_en・kp1_ja_charon]のTTS+ASRのみ) | ¥9.46 | gemini(TTS)¥8.82+openai_asr¥0.65。単価は`er005_output/cost_baseline_01/pricing_snapshot.json`(OFFICIAL_SOURCE)、為替`USD_JPY=160.0`。Assembly/Gate判定はローカル処理のみで¥0 |
| ②Trial特有の追加コスト | ¥0 | 本タスクはTrialではなく既存Production記事の個別Feedback対応のため該当なし |
| ③異常retry・Human Review由来の上振れ | ¥0 | `full_story_part1`は`retry_count=0`・outer slowdown attempt=1回で成功(内部で計2回のgemini TTS呼び出しがあるのは、通常ペース生成→6% time-stretch post-process後の再検証という既存の1セット設計であり、失敗によるretryではない)。KP1(英/日)も各1回で成功。Human Review Lockの新規発動なし |
| ④Standard同期でのコスト(1記事あたり、累積) | 前回累計¥131.68(`ER-009-JA-READING-DICTIONARY-ACRONYM-EXPANSION-AND-TREND-A2-RESUME-01_REPORT.md`)+今回¥9.46 = **¥141.14** | 前回§10実測値に今回分を加算 |
| ⑤Batch量産換算時のコスト | 今回分TTS(¥8.82)のみ半額(Gemini Batch tier=Standardの50%)→約¥4.41。ASR(¥0.65)にBatch tierは存在しないため不変。今回分Batch換算合計≈¥5.06 | `pricing_snapshot.json`参照 |

---

## 4. OPEN-121 / OPEN-145 / OPEN-146 発火有無

| Open Item | 内容 | 今回の発火有無 |
|---|---|---|
| OPEN-121(TTS Repetition QA) | full_story_part1で`repetition_qa_checked=True`実施 | **不発火**(`flagged=False`) |
| OPEN-145(日本語ASR表記ゆれ/pykakasi読み) | B1 kp1日本語gloss「人の手を借りずに自分で動く」で読み解決を実施 | **不発火**(`reading_safety_changed_text=False`、候補外読みなし) |
| OPEN-146(日本人名ローマ字表記) | 今回のsegmentに日本人名なし | 対象外(該当箇所なし) |

---

## 5. 13項目監査表(標準player、Gate 7準拠)

対象: `player_std/index.html`(B1)、`player_std/a2_index.html`(A2)。

| # | 項目 | B1 | A2 |
|---|---|---|---|
| 1 | audio+script同一ページ | ○ | ○ |
| 2 | 再生UI近接(script行と同一セルにaudio要素) | ○ | ○ |
| 3 | A2・B1区別(表示ラベル、旧B1B→B1修正済み) | ○ | ○ |
| 4 | Full Story・Point One・Two・In One Line全segment存在 | ○ | ○ |
| 5 | Preview・Comment 1〜4全segment存在 | ○ | ○(A2は日本語Comment 1〜4+Preview) |
| 6 | Key Phrase英日併記(rank1=autonomous/人の手を借りずに自分で動く反映済み) | ○ | ○(A2側KPは別セット、変更対象外で不変) |
| 7 | intro・outro・SFX・固定文言(Welcome/Notification等)明示 | ○ | ○ |
| 8 | 順序・start sec・seek(timeline.json実測値、再Assembly後に再生成済み) | ○ | ○ |
| 9 | voice情報表示(Aoede/Charon等) | ○ | ○ |
| 10 | unretrieved marker(`class="missing"`、SFX等の無音声segmentを区別) | ○ | ○ |
| 11 | TTS mode表示(`TTS_EXECUTION_MODE=STANDARD`明記) | ○ | ○ |
| 12 | controls≥360px(`audio_review_player.py`共通CSS`AUDIO_MIN_WIDTH_PX=360`) | ○ | ○ |
| 13 | Source列なし(ヘッダはSeek/Segment/Script/個別音声の4列) | ○ | ○ |

Seekボタン動作: `SEEK_SCRIPT`(`audio_review_player.py`、無変更)が
`button.seek`クリックで`episode_audio.currentTime`をtimeline実測の
`start_seconds`へ設定し再生する仕組み。両episode mp3のduration
(A2=359.462s、B1=393.094s)は再Assembly後のwav durationと一致することを
確認済み(コード読解によるロジック確認+duration突合。ブラウザでの実際の
クリック操作によるE2E確認は本タスクでは未実施)。

---

## 6. 変更ファイル一覧(絶対パス、commit対象・未commit)

Production code(表示ラベルのみ変更、ロジック無変更):
- `C:\Users\tensh\eigo-radio\er011_family_a_trend_synthesis_ai_manufacturing_production_run_01_b1b_player.py`

記事artifact(A2):
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\a2\article.md`
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\a2\parts.json`
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\a2\audit\tts_generation_results.json`
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\a2\audit\timeline.json`
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\a2\audit\gain_report.json`
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\a2\audit\review_lock_state.json`(Assembly実行に伴う既存機構の書き込み、`full_story_part1`の新規lockエントリなし)
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\a2\run_summary_assemble.json`
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\a2\narration\full_story_part1.wav`
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\a2\assembled\English_Your_Way_A2_FAMILY_A_TREND_AI_MANUFACTURING_PROD_RUN_01.wav`

記事artifact(B1/内部b1b):
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\b1b\key_phrases\keywords_canonicalized.json`
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\b1b\audit\tts_generation_results.json`
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\b1b\audit\timeline.json`
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\b1b\audit\gain_report.json`
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\b1b\audit\review_lock_state.json`
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\b1b\run_summary_assemble.json`
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\b1b\narration\kp1_en.wav`
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\b1b\narration\kp1_ja_charon.wav`
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\b1b\assembled\English_Your_Way_B1B_FAMILY_A_TREND_AI_MANUFACTURING_PROD_RUN_01.wav`

標準player:
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\player_std\index.html`
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\player_std\a2_index.html`
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\player_std\audio_mp3\a2\full_story_part1.mp3`
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\player_std\audio_mp3\a2\a2_episode.mp3`
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\player_std\audio_mp3\b1b\kp1_en.mp3`
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\player_std\audio_mp3\b1b\kp1_ja_charon.mp3`
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\player_std\audio_mp3\b1b\b1b_episode.mp3`

本タスクの証跡・fixスクリプト一式(新規、evidence保存先):
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\user_feedback_fix_01\`
  (内訳: `pre_fix_sha256_snapshot.json`、`article_pre_fix_backup.md`、
  `b1_keywords_canonicalized_pre_fix_backup.json`、
  `a2_main_story_heading_fix_runtime_evidence.py`、
  `a2_main_story_heading_fix_run_summary.json`、
  `a2_assemble_runtime_evidence.py`、`a2_assemble_run_summary.json`、
  `b1_kp1_replacement_runtime_evidence.py`、
  `b1_kp1_replacement_run_summary.json`、`b1_assemble_runtime_evidence.py`、
  `b1_assemble_run_summary.json`、`raw_usage_log_a2_fix.jsonl`、
  `raw_usage_log_b1_kp1_fix.jsonl`)

共有Production資産(既存の共有function呼び出しによる正常な副作用、
本タスク固有の変更ではない):
- `C:\Users\tensh\eigo-radio\er006_output\master_audio_store_01\manifest.json`
  (KP英語Component "autonomous"の新規Master登録)
- `C:\Users\tensh\eigo-radio\er006_output\master_audio_store_01\reuse_telemetry.jsonl`

**注意(commit時の除外対象、このタスクでは発生していない変更)**:
作業中、`git status`で以下も変更検知されているが、いずれも本タスクの
scriptからは一切参照・実行していない(セッション開始前からdirty、または
セッション中に別プロセスが並行して更新したと推定される)。commit対象から
明示的に除外すること:
`er011_output/discovery_generalization_wake_before_alarm_trial_12/**`、
`er011_wake_before_alarm_trial12_std_player_01.py`、
`er011_output/family_a_completion_a2_trend_end_to_end_01/b1b/**`、
`er012_b_family_*.py`、`er012_editorial_b_family_voices_3v_production_wiring_phase1_test_01.py`、
`er006_output/pronunciation_ledger_01/ledger.json`、
`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`、
`er011_output/attempt_history.jsonl`。

---

## 7. OPEN_ITEMS.md OPEN-135 Trend行 追記文案(SSOT本体は未編集、案のみ)

```
**追記(2026-09-13、FAMILY-A-TREND-AI-MANUFACTURING-USER-LISTENING-FEEDBACK-FIX-01)**
【Trend】: ユーザー個別視聴Feedback(2026-09-13、個別対応、一般仕様化ではない)
に基づき、`family_a_trend_ai_manufacturing_prod_run_01`へ2件の修正を実施した。
(1) A2 `full_story_part1`冒頭に混入していたartifact不具合`## Main story`
見出し行(原因: `er003_v1_n3_01_scaffold_generate.py::split_article_text()`
115行目のintro_text抽出が`## In one line…`以外の`## `見出しを除去しない
仕様のため、Writer出力の飾り見出しがそのまま本文へ混入。Production関数は
無変更、article.md側の見出し除去+再パースで対応)を除去し、TTS+ASR再生成・
A2必須6% slowdown・Assembly・Audio Validation Gate(既定/opt-in両方)PASSを
再確認した。(2) B1 Key Phrase 1を`not there yet`から`autonomous`へ
ユーザー指定で差替(既存canonicalization関数は再実行せず個別上書き)、
関連音声(kp英語/日本語gloss)を再生成しASR verified、Assembly・Gate両方
再PASSを確認した。(3) 標準player(index.html=B1、a2_index.html=A2)を
表示ラベル`B1B`→`B1`へ修正のうえ再生成し、13項目監査は両player○/×表で
全項目○。今回実測費用¥9.46(記事全体累計¥131.68→¥141.14)。
OPEN-121(Repetition QA)・OPEN-145(日本語読み)いずれも不発火、OPEN-146は
対象外。詳細:
`FAMILY-A-TREND-AI-MANUFACTURING-USER-LISTENING-FEEDBACK-FIX-01_REPORT.md`。
**Statusは`USER_LISTENING_PENDING`のまま維持**(修正後の再視聴・承認は
未実施、`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`への格上げなし)。
Git commit/pushは本タスクでは未実施(Fable統合時に実施予定)。
```

---

## 8. 未実施・残課題

- Gitへのcommit/push: 本タスクでは実施していない(指示によりGit操作禁止)。
  上記§6のファイル一覧を後続の統合タスクへ引き継ぐ。
- ブラウザでの実際のSeekボタンクリックによるE2E再生確認は未実施
  (コード読解+duration/timeline数値突合のみ)。
- player scriptのmp3キャッシュ設計(§2.4で発見)の一般修正は
  USER_DECISION_REQUIRED相当のため未実装、報告のみ。
- ユーザーによる再視聴・最終承認は未実施(Status: `USER_LISTENING_PENDING`
  のまま)。

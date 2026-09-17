# RESULT_PACKET: PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01-PHASE-B-FIX-01(累積Full Report)

管理ID: `PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01-PHASE-B-FIX-01`(前段:
Phase B `docs/pm/RESULT_PACKET_PN_A2_PHASE_B.md`[Status=`WIRING_INCOMPLETE`、
Narrator見出し2 segmentがHuman Review Lock])。本ファイルはPhase Bの結果を
含む累積Full形式。

★★★★報告ここから★★★★

## 0. T-0(委任文検証)

`docs/pm/delegation_log/PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01-PHASE-B-FIX-01.md`
を保存し`check_delegation_prompt.py`を実行。結果=`FAIL`(既知パターンと同型:
「事前指定Grep一覧+追記位置・更新位置の手順」「実行コマンド全文」セクション
見出し欠落。他の必須項目6/8`OK`、固定ブロックE-1/D-1/G-1/F-1`OK`)。ルール
どおりFAILでも継続。JSON: `docs/pm/delegation_log/PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01-PHASE-B-FIX-01_check.json`。

並行タスク`USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-04`のmarker
`docs/pm/RESULT_PACKET_NEWS_2EP_RESUME4.md`は、コード調査・是正・unit
test・regression実行(共有store書き込みなし)を先に済ませた後、待機開始
から約20〜30分後に出現を確認し、TTS/Assembly/Gate stageを開始した。

## 1. 現在Status

`PRODUCTION_WIRED`(新規topic A2 E2E配線・retry policy整合・Personalized
News A2 episode生成・Assembly/Gate/player/web export/E2E再生確認まで
全条件充足)。記事内容としての最終OKはユーザー試聴待ち(`USER_TEST_READY`
確定扱いにはしない)。Phase B時点のStatus(`WIRING_INCOMPLETE`)から本FIX-01
で前進。

## 2. retry policy差分(既存経路 vs 新経路)と是正内容

- **旧新経路**(`er012_b_family_voices_a2_production_01.py`
  `generate_narrator_heading_with_a2_slowdown()`、修正前): `point_headings.
  generate()`(`er003_v1_sing01_point_headings_aoede.py` 43-126行目)を直接
  呼んでいた。この関数はstandard instruction(`p9a.ENGLISH_STYLE_PREFIX`)と
  minimal instruction fallbackが単一の`attempts_log`ループ内にあり
  (`minimal_after = max(1, max_attempts // 2)`で切替)、`secondary_asr.
  evaluate_attempt_with_cascade()`が`stop_retrying=True`を返すと
  (`if stop_retrying: return {...}`、119-124行目)、minimal fallbackへ一度も
  到達せず即座に`ASR_VALIDATION_UNCERTAIN`で`return`する構造だった。実データ:
  `point_one_heading`/`point_two_heading`とも`attempt1`のみで終了
  (`.../attempts/point_*_heading_attempt1_englishstyleprefix.json`のみ存在)。
- **既存承認済み経路**(free_address、`er003_v1_n3_01_tts_generate.py`
  834-845行目、A01/ADD03記事向けの既存呼び出しパターン):
  `n3_tts.generate_a2_segment_with_slowdown()`(189-248行目)を使用。内部で
  `er003_v1_crosslevel_audio_02_common.py::generate_english_segment_with_
  fallback()`(59-190行目)を呼び、standard経路(`generate_narration_
  snippet_verified_strict`、`standard_attempts`回)とminimal instruction
  fallback経路(`repro01.generate_english_component_minimal_instruction`、
  独立予算`fallback_budget = max_attempts - len(standard.attempts_log)`)が
  明確に分離されている。standard側が`stop_retrying`等で早期終了しても
  fallback側は必ず試行される設計(107-113行目の`HUMAN_REVIEW_LOCKED`時のみ
  fallbackをskipする、それ以外は必ずfallbackへ進む)。既存承認済みaudit
  (`er012_output/editorial_b_family_voices_a2_production_wiring_01/a2/
  audit/tts_generation_results.json` L403-500)でも、free_addressの
  `point_one_heading`は`standard_attempts_log`(1回、UNCERTAIN)→
  `fallback_attempts_log`(1回、minimal instruction、NORMALIZED_MATCH)と
  いう構造で通過しており、この2経路が異なるpolicyだったことを裏付けた。
- **是正**: `generate_narrator_heading_with_a2_slowdown()`
  (`er012_b_family_voices_a2_production_01.py` 674-679行目)を、承認済み
  free_address経路と同一の呼び出しパターン(`n3_tts.generate_a2_segment_
  with_slowdown(tts_input, out_path, n3_tts.first_words(tts_input, 3),
  max_extra_chars=20, style_prefix_override=n3_tts.A2_ENGLISH_STYLE_PREFIX_
  SLOWER, disfluency_qa=True)`)へ統一。新規TTS/ASR/time-stretchロジックは
  一切追加していない(既存承認済み合成primitiveの呼び出し方を揃えたのみ)。
  既存`main_a2()`・`main_b1_2v()`・`main_b1_3v()`・`point_headings.generate()`
  自体は無変更。
- **player.html配置の副次修正**(`er012_b_family_production_runner_01.py`
  `build_player_html_a2_2v_new_topic()`、1863-1873行目): Episode audio要素
  のみ、`file:///`絶対パス(`player_common.abs_file_url`、ローカル監査専用、
  リモート解決不可)から`web/episode.mp3`相対パス(`export_web_delivery_
  a2_2v_new_topic()`が実際に書き出す既存命名と一致)へ変更。`unified.html`
  の`chooseAudio()`は`audio.main`/`audio[id*="episode"]`のみを見て
  per-row個別audioは参照しない設計のため、この1箇所のみで足りる(他segment
  の個別audio参照はローカル監査用として無変更のまま維持、player.html自体は
  既存どおり記事dir直下=`out_dir_base`ルートに配置)。

## 3. 見出し2 segment再実行結果

既存Human Review Lock機構の正規手続き`review_lock.approve_regenerate()`
(out_path/canonical_text指定、approved_by=`claude_code_operator_pn_a2_
phase_b_fix_01`、この命名規則は本プロジェクトの既存precedent
[`er011_no18_open107_b1_failed_segments_retry_03.py`等]と同型)を使用。
これはcontent(ASR不一致のまま)を承認したのではなく、是正済みcodeでの
1回限りの再生成を許可する既存Gate機構であり、Human Approvalの代行(承認記録)
には該当しない。他segmentは再生成せず既存OK音声を再利用。

- `point_one_heading`("One Voice: My morning news route."): standard
  1回目で"One voice, my morning news route."=`NORMALIZED_MATCH`→`OK`
  (fallback未使用、attempt数=1)。
- `point_two_heading`("Another Voice: What is missing?"): standard不合格
  →fallback(minimal instruction)で"Another voice: What is missing?"=
  `NORMALIZED_MATCH`→`OK`(`fallback_used=True`、想定どおりfallbackが機能)。
- 両segmentとも`slowdown_applied=True`(6% time-stretch適用済み)、
  `post_slowdown_classification=NORMALIZED_MATCH`。
- 最終`segment_status`: 14 segment全て`OK`(topic_intro/point_one_heading/
  point_two_heading/point_one/point_two/full_story_part1/full_story_part2/
  tension_reflection/in_one_line/preview/comment_1-4)。
- 既知の非blocking観測(Phase Bから継承、未変更): `check_required_segments_
  completeness()`は`japanese_title`が`tts_generation_results.json`の
  `segments`辞書にマージされていない構造上の理由で"missing"と表示するが、
  `japanese_title.wav`自体はPhase Bで既に`status=OK`で生成済み(別audit
  ファイル`japanese_title_result.json`)であり、これは新規topic経路の元々の
  設計上の表示上の隙間であって本FIX-01が新たに壊したものではない
  (Audio Validation Gateはこの辞書の`segments`のみを見るため、この表示上の
  隙間はGate合否には影響しない)。

## 4. Assembly/Gate

`assemble` stage実行: `status=OK`、`duration_seconds=359.264`、
`peak=0.89034`、`clipping_detected=False`、`headroom_safety_valve`適用の
有無は`run_summary_assemble.json`記載どおり(Audio Validation Gate通過、
override無し、Gate緩和なし)。

## 5. player配置・web export・E2E再生evidence

- `player.html`: `er012_output/b_family_a2_new_topic_production_01/
  personalized_news_2v_a2/player.html`(記事dir直下、`build_player_html_
  a2_2v_new_topic()`)。
- `web export`: `.../personalized_news_2v_a2/web/episode.mp3`
  (4,041,384 bytes)+`web/segments/*.mp3`(35件)。
- E2E再生(Playwright、headless Chromium、rawcdn.githack.com
  `unified.html`、interstitial "Open the page"クリック経由):
  - `before_play`: `readyState=0`, `paused=true`, `error=null`
  - `after_play_4s`: `currentTime=3.812103`, `paused=false`,
    `readyState=4`, `error=null`, `duration=359.263625`(Assembly実測値と
    一致)
  - `after_seek`(60秒seek+1.5秒待機): `currentTime=61.448778`,
    `paused=false`, `readyState=4`, `error=null`
  - `kp_present=true`(Key Phrase表示確認)、`timeline_rows=4`
    (Intro/Preview/Key Phrases/Full Scriptカード表示)
  - `ja_title`="見えているニュースと、見えていないニュース"
    (期待値と完全一致、日本語エンコード確認済み)
  - `console_errors`: `ERR_BLOCKED_BY_RESPONSE.NotSameOrigin`
    (ethicalads広告ブロック、既存precedent[RESUME-04/05]と同一の無害な
    既知エラーであり本記事コンテンツとは無関係)
  - evidence保存先: `er012_output/b_family_a2_new_topic_production_01/
    personalized_news_2v_a2/web/e2e_playback_evidence.json`/`.png`

## 6. URL

- unified.html(rawcdn): `https://rawcdn.githack.com/shimomura055/eigo-radio/194d502270c0e452a060fe543d09e20d067b4f0a/user_test/unified.html?src=er012_output/b_family_a2_new_topic_production_01/personalized_news_2v_a2/player.html&level=A2&en=The%20News%20You%20See%2C%20and%20the%20News%20You%20Miss&ja=%E8%A6%8B%E3%81%88%E3%81%A6%E3%81%84%E3%82%8B%E3%83%8B%E3%83%A5%E3%83%BC%E3%82%B9%E3%81%A8%E3%80%81%E8%A6%8B%E3%81%88%E3%81%A6%E3%81%84%E3%81%AA%E3%81%84%E3%83%8B%E3%83%A5%E3%83%BC%E3%82%B9`
- player.html直URL(raw.githack): `https://raw.githack.com/shimomura055/eigo-radio/194d502270c0e452a060fe543d09e20d067b4f0a/er012_output/b_family_a2_new_topic_production_01/personalized_news_2v_a2/player.html`
- (注)上記SHA`194d5022...`は成果物commit時点のもの。本ファイル自体を含む
  SSOT反映commitは別SHAとなるため、10節の最終SHAも参照のこと(コード・
  音声・player.html/web/はSSOT反映commitより前のcommitで既にpush済みで
  内容は変わらない)。

## 7. Leakage残存flagの内容と扱い

Phase Bで検出済み・本FIX-01でも再生成していないため残存: voice_a=
`leak_discovery_syntax`、voice_b=`leak_numbers_foreground`/
`leak_discovery_syntax`(いずれも3 attempt上限到達)。既存B1/3V仕様の
前例(同種残存flag付きで`PARTIAL`扱いとしユーザー試聴へ回した実績)と
同じ扱いとし、記事は再生成せず、記事完成の判定をブロックしない。
ユーザー試聴時の確認事項に含める(14節)。

## 8. regression(件数、新規test)

- `er012_b_family_voices_a2_new_topic_production_01_test_01.py`:
  15件PASS(既存13件+新規2件: `generate_narrator_heading_with_a2_slowdown`
  が`point_headings.generate`ではなく`n3_tts.generate_a2_segment_with_
  slowdown`を承認済み引数[expected_substring=first_words(text,3)/
  max_extra_chars=20/style_prefix_override=A2_ENGLISH_STYLE_PREFIX_SLOWER/
  disfluency_qa=True]で呼ぶことの確認、standard経路が`stop_retrying`で
  早期終了してもfallback予算が独立して確保・実行されることの確認)。
- 他`er012_*test*.py`(6ファイル、実質test collection対象は5ファイル):
  全PASS(`er012_b_family_voices_variable_voice_count_test_01.py`/
  `er012_b_family_voices_writer_generic_01_test_01.py`/
  `er012_editorial_b_family_production_phase1_test_01.py`/
  `er012_editorial_b_family_voices_3v_production_wiring_phase1_test_01.py`/
  `er012_open131_fact_attribution_production_wiring_01_test_01.py`)。
- `er013_family_c_production_test_01.py`: 39件PASS。
- project-wide regression(`run_project_regression.py`): **2893/2896
  PASS**(是正前2891/2894から新規test 2件追加分がそのまま増分、既知FAIL
  3件のみ[`er003_test_bad`/`er003_test_p2j_investigate`系、本タスクと
  無関係な既存FAIL]、新規FAILなし)。2回実行(見出し関数是正直後・
  player.html是正直後)いずれも同一結果。summary:
  `/scratchpad/regression_summary_fix1.json`,
  `/scratchpad/regression_summary_fix1b.json`(スクラッチパッドのみ、
  repo未配置)。

## 9. cost(本タスク+Phase B累計、model_id)

本タスク実測: 累積¥42.38(内訳は`raw_usage_log.jsonl`ログ全体の累積値、
openai=¥3.15、gemini=¥36.70、openai_asr=¥2.53、azure=¥0.00。見出し2
segmentの再生成分[TTS+ASR、standard+fallback各1回ずつ]が主な増分)。
model_id: TTS英語=`gemini-2.5-pro-preview-tts`(Aoede)、ASR primary=
`gpt-4o-mini-transcribe`、ASR secondary cascade=`azure-speech-stt`。
Phase B分(¥71.84)と合算した累計は約¥114.22(予算目安¥250以内)。
E2E Playwright/web export(mp3変換)はAPI呼び出しを伴わないため追加費用
¥0。

## 10. Git SHA

- 成果物commit: `194d502270c0e452a060fe543d09e20d067b4f0a`(コード修正2
  ファイル+新規test+delegation log+runtime artifacts[wav除外]、57
  files changed)。push済み(`c2aa1416..194d5022 main -> main`)。
- SSOT反映commit: 本RESULT_PACKET保存後に別途commit・push(完了後、末尾
  に追記)。

## 11. SSOT更新

- `CURRENT_SPEC.md`「新規topic A2 Production経路」行(L669)へ本FIX-01の
  是正内容・runtime結果・Status変更(`WIRING_INCOMPLETE`→`PRODUCTION_
  WIRED`)を追記(既存記述は保持、追記のみ)。
- `DECISION_LOG.md`: `## PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01-PHASE-B-FIX-01`
  エントリを新設(`## 参照元`節の直前)。retry policy差分・是正内容・
  runtime結果・E2E evidence・Leakage残存の扱い・cost・Statusを記録。
- `OPEN_ITEMS.md`: OPEN-159のサブ項目へ(6)を追記(見出し接頭ラベル
  "One Voice:"/"Another Voice:"のASR脱落パターンが既知パターン化して
  いること[2026-09-07 Pronunciation Ledger登録、2026-09-17本タスクで
  実例確認・標準retry policyで解消可能なことを確認]、恒久対応は
  OPEN-159の他サブ項目と合わせて今後着手)。新規Open Itemの登録はなし。
  `PM_GOVERNANCE.md`は無変更。

## 12. Production Wiring Checklist(PM_GOVERNANCE Gate 3、実質11項目
     [「15条件」という名称の固定リストはPM_GOVERNANCE/Phase B報告のいずれ
     にも存在しないため、Gate 3の正本記載項目で代替評価])

1. Production正式初回経路: ○(`main_a2_2v()`、Trial非経由)
2. retry・fallback・regenerationとの整合: ○(本FIX-01の主目的、2節)
3. DEV・Trial-onlyではないこと: ○(既存test`NoTrialOrFixedTopicImportTests`
   でimport無しを確認、regression PASS)
4. Production runtimeでの実発火: ○(3節、実TTS/実ASR実行)
5. 必要testのPASS: ○(8節)
6. runtime evidence: ○(3-6節)
7. 実際のmodel_id・routing確認: ○(9節)
8. コスト影響評価: ○(9節、予算内)
9. `CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`: ○(11節)
10. 必要なGit反映: ○(10節)
11. approved specとProduction挙動の一致: ○(2節、既存承認済みfree_address
    経路と同一retry policyへ統一)

## 13. Dangling Reference Check(6項目)

1. 是正後の関数が参照するのは既存承認済みprimitive(`n3_tts.generate_a2_
   segment_with_slowdown`)のみで新規/Trialロジックを追加していないか:
   ○(2節、grep+test確認)。
2. player.htmlのEpisode audio src変更が実際のexport出力パスと一致するか:
   ○(5節、`web/episode.mp3`実ファイル存在確認済み)。
3. 是正後のretry policyがfree_address承認済み経路の実際の呼び出し引数と
   完全一致するか: ○(2節、n3_tts.py 842-844行目と同一引数)。
4. Human Review Lock解除手続きが既存precedent(approved_by命名規則含む)
   と整合しているか: ○(3節)。
5. Gateが緩和・無効化されていないか: ○(4節、override無しで正常通過)。
6. 他Editorial Type経路(`main_a2()`/`main_b1_2v()`/`main_b1_3v()`)が
   無変更のままか: ○(`git diff`で該当関数への変更なしを確認、15節)。

## 14. 未決事項/ユーザー試聴時の確認事項

- Analytical Leakage残存flag(7節、voice_a: `leak_discovery_syntax`、
  voice_b: `leak_numbers_foreground`/`leak_discovery_syntax`)は記事完成
  をブロックしていないが、ユーザー試聴時にVoice A/B本文の該当箇所
  (数字の扱い・話法の一貫性)を意識して確認いただきたい。
- Narrator見出し2件は是正後のretry policyでNORMALIZED_MATCH(=ASRが
  わずかに異なる表記[大文字小文字・コンマ]で認識したが内容は一致と判定)
  として通過している。実際の発音が意図通り("One Voice:"/"Another
  Voice:"という接頭ラベルを含む読み上げ)になっているかは、ユーザー
  試聴での最終確認が必要(1節、`USER_TEST_READY`未確定)。
- OPEN-159サブ項目(6)として記録した見出し接頭ラベルASR脱落パターンの
  恒久対応(Pronunciation Ledger IPAの自動判定配線等)は未着手のまま。

## 15. 無変更証跡/事前指定外Read

- `git status --porcelain er003_*.py er006_*.py er011_*.py er013_*.py`:
  `er003_v1_n3_01_tts_generate.py`のみ`M`(並行タスク
  `USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-04`/`06`由来、本タスクは
  Read専用でEdit/Writeしていないことを確認済み)。他は`??`(未追跡、
  いずれも過去タスクの残置物で本タスク由来ではない)。共有store
  (`er006_output/*`/`er011_output/*`)の差分は並行タスク由来のためcommit
  対象外(9-2節の運用ルールどおり)。
- 事前指定外Read(理由付き): (1) `docs/pm/PM_GOVERNANCE.md` Gate 3節
  (「Production Wiring Checklist」の正本定義箇所を特定するため、12節の
  評価根拠として必要)。(2) `user_test/unified.html`全文(事前指定は
  `docs/pm/RESULT_PACKET_NEWS_2EP_RESUME5.md` 1-3節のみだったが、
  player.html配置修正の妥当性[`chooseAudio()`/`abs()`の相対パス解決
  ロジック]を正確に把握する必要があったため全文確認、変更なし)。
  (3) `docs/pm/RESULT_PACKET_WEB_AUDIO_EXPORT.md`(free_address A2の
  player.html file:///参照の既存precedentを確認する目的、変更なし)。
  (4) `er011_output/household_unified_final_candidate_01/player.html`
  抜粋(相対path形式の実例確認、変更なし)。

★★★★報告ここまで★★★★

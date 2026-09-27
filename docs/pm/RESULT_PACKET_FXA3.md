# RESULT_PACKET_FXA3(一時ファイル、commitしない)

管理ID: NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01(Stage 3b: Hormuz記事runtime実行)

## 0. 結論
scaffold/tts/assembleを実行しruntime evidenceを取得した。所有ファイル
(`er019_family_x_audio_production_runner_01.py`)の変更は不要だった
(スラッシュ入りslug`family_x_b3_diversity_trial_01/hormuz`は既存
`derive_out_dir()`の単純文字列結合でそのままネスト出力先を生成でき、
`--dry-run --stage plan`で事前確認・実行後も問題なし)。**STOP該当3件**:
A2 `full_story_part2`、B1B `full_story_part2`、B1B key_phrase `kp2`
(rank2)日本語glossが、既存retry/cool-down/Local Rewrite機構を全て
使い切ってもASR検証を通過できずSTOPPED→HUMAN_REVIEW_REQUIRED。
その結果両level(A2/B1B)ともAudio Validation Gateがepisode assemblyを
BLOCK(想定どおりの安全側動作、Gateは回避せず)。完成audioは生成されて
いない。Placeholder Notation Gate該当("…"/"〜")は今回0件(Meta run
固有の事象と判明)。一方、既存のConnected Speech cool-down(10分固定)/
Local Rewrite回復機構が複数回実測発火し、5件中3件は自動回復に成功した
(B1B `full_story_part1`/`full_story_part3`/`comment_4`)。

## 1. 入力article.md不変性
- a2/article.md sha256(raw): `e29b21c67f2140393001cbeefebe47db4fae3559979d6f0c7b17b20955106137`
- b1b/article.md sha256(raw): `5290325c6c663aff67f762a0f0eae29dfe76451c5524cdfa457f856233fcf987`
- 実行前後で再計算し完全一致(不変)確認済み。

## 2. segment表

### A2(Standard)
| segment_id | attempt数 | 最終classification | duration(s) |
|---|---|---|---|
| topic_intro | 1 | NORMALIZED_MATCH | 6.09 |
| japanese_title | 1 | NORMALIZED_MATCH | 6.79 |
| preview | 1 | NORMALIZED_MATCH | 13.45 |
| comment_1 | 1 | PHONETIC_MATCH | 9.87 |
| comment_2 | 1 | NORMALIZED_MATCH | 11.04 |
| comment_3 | 1 | NORMALIZED_MATCH | 22.08 |
| comment_4 | 1 | PHONETIC_MATCH | 24.20 |
| full_story_part1 | 1 | NORMALIZED_MATCH | 56.77 |
| full_story_part2 | 3(標準2+fallback1) | 全てTRUE_CONTENT_MISMATCH→**STOPPED/HUMAN_REVIEW_REQUIRED** | - |
| full_story_part3 | 1 | NORMALIZED_MATCH | 29.77 |
| in_one_line | 1 | NORMALIZED_MATCH | 24.08 |
| KP1-5(en/meaning) | 各1 | 全OK(5組) | - |

### B1B(Advanced)
| segment_id | attempt数 | 最終classification | duration(s) |
|---|---|---|---|
| topic_intro | 1 | NORMALIZED_MATCH | 5.94 |
| preview | 1 | NORMALIZED_MATCH | 15.53 |
| comment_1 | 1 | **NUMERIC_EQUIVALENCE_MATCH**(Tier1数値救済) | 6.02 |
| comment_2 | 1 | NORMALIZED_MATCH | 12.08 |
| comment_3 | 1 | NORMALIZED_MATCH | 24.41 |
| comment_4 | 4(標準2+fallback1+Local Rewrite1) | attempt1-3=ASR_VALIDATION_UNCERTAIN("point"→"points")→attempt4=NORMALIZED_MATCH回復 | 14.71 |
| full_story_part1 | 3(標準2+fallback1) | attempt1-2=TRUE_CONTENT_MISMATCH(sub_reason=protected_number)→attempt3=NORMALIZED_MATCH回復 | 49.24 |
| full_story_part2 | 5(標準2+fallback1+Local Rewrite2) | 全てTRUE_CONTENT_MISMATCH/repetition flagged/length超過→**STOPPED/HUMAN_REVIEW_REQUIRED** | - |
| full_story_part3 | 4(標準2+fallback1+Local Rewrite1) | attempt1-3=TRUE_CONTENT_MISMATCH→attempt4=NORMALIZED_MATCH回復 | 29.34 |
| in_one_line | 1 | NORMALIZED_MATCH | 21.10 |
| KP1,3,4,5(en/ja) | 各1 | 全OK(4組) | - |
| KP2(en) | 1 | OK | - |
| KP2(ja、rank2)「海からの封鎖」 | 3(標準2+fallback1) | 全てTRUE_CONTENT_MISMATCH(ASRが「海からの風さ」等と誤認識)→**STOPPED/HUMAN_REVIEW_REQUIRED**(Key Phrase日本語roleはConnected Speech対象外のためLocal Rewrite非適用、既存仕様どおり) | - |

## 3. ASR Phase B(semantic_equivalence)telemetry
`er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl`
は他Agent(並走中のTTS A/B Trial等)と共有書き込みされており、実行前後の
単純な行数差分(826→927行、+101)はそのままでは本タスク由来と断定できない。
本記事のcanonical text断片(`Strait of Hormuz`/`20% plan`/`center stage`)
で内容照合した結果、本記事由来の新規記録は**9件**、全て`role=FULL_STORY`:
- `classification=TRUE_CONTENT_MISMATCH`: 7件
  (`sub_reason=content_word`×4[A2 full_story_part2の数値誤認識2件+
  B1B full_story_part2のrepetition/length系2件]、
  `sub_reason=protected_number`×3[B1B full_story_part1×2、
  full_story_part3×1、"Act One"→"Act 1"表記差])
- `classification=ASR_VALIDATION_UNCERTAIN`: 2件(`sub_reason=entity_only`)
- `SECONDARY_ASR_CORROBORATED_MATCH`(Tier3救済)/`NUMERIC_EQUIVALENCE_MATCH`
  (Tier1救済)発火: この9件中**0件**(rescue不成立のまま最終的に
  cool-down/fallback/Local Rewriteで回復または最終STOPPEDへ帰着)。
  ※B1B `comment_1`のTier1救済(`NUMERIC_EQUIVALENCE_MATCH`)はattempt1
  時点で直接成立したためこのtelemetry(観測専用ログ)には現れない。

## 4. Cool-down/Local Rewrite/Human Review Lock 発生件数
- Cool-down(10分固定、`cooldown_events`実測値、各`cooldown_actual_
  seconds`≒600.00〜600.01秒)発生: **5回**(A2 full_story_part2×1、
  B1B full_story_part1×1、B1B full_story_part2×1、B1B full_story_part3×1、
  B1B comment_4×1)。
- Local Rewrite発生: **4回**(B1B comment_4×1[成功]、
  B1B full_story_part2×2[いずれも失敗]、B1B full_story_part3×1[成功])。
- Human Review Lock(最終STOPPED)到達: **3件**(A2 full_story_part2、
  B1B full_story_part2、B1B kp2_japanese)。

## 5. Assembly / Audio Validation Gate
両levelを個別実行(`--level a2 --stage assemble`/`--level b1b --stage
assemble`、およびbothでの一括実行でも同じ結果)。既存
`asm.verify_episode_audio_validation_gate()`が`EPISODE_BLOCKED_BY_
AUDIO_VALIDATION`(RuntimeError)を送出しGate側でepisode assemblyを中止:
```
A2: ['full_story_part2=STOPPED']
B1B: ['full_story_part2=STOPPED', 'kp2_japanese=STOPPED']
```
timeline.json/player.html/manifestは生成されていない(Gate通過前に停止)。
assemble試行による追加APIコストは¥0(Gate判定はローカルのみ)。
Point Notification音・「ポイント解説」の不在は、Meta run(Stage 3a)と
同じ理由でコード上確認済み(Point系segment/SFXはFAMILY_X_A2_SEGMENT_
ORDER/FAMILY_X_B1_SEGMENT_ORDERに一切含まれない)。

## 6. STOP該当(回避せず報告、3件)
- **A2 `full_story_part2`**: 標準2回+fallback1回=計3回、全て
  `TRUE_CONTENT_MISMATCH`。attempt2/3は`$83.30`→`$83.37`の数値誤認識、
  attempt3(fallback、数値自体は`$83.30`で一致)は見出し
  "The 20% plan changes overnight"が後続文と読点で連結され独立文として
  読まれなかった可能性(TTS instructionの見出し読み上げ要件との齟齬)。
- **B1B `full_story_part2`**: 標準2回+fallback1回+Local Rewrite2回=計5回、
  全て失敗。見出し句"The 20% plan"が本文冒頭付近で近接反復するテキスト
  構造をrepetition QAが繰り返しflagged(intentional=false判定)。
  Local Rewriteは別span("20%"の読み方等)を修正したが同じ反復パターン
  自体は解消しなかった。
- **B1B key_phrase `kp2`(rank2)日本語gloss「海からの封鎖」**: 標準2回+
  fallback1回=計3回、全て`TRUE_CONTENT_MISMATCH`(ASRが「海からの風さ」
  等と誤認識)。Key Phrase日本語roleはConnected Speech適用対象外
  (既存仕様、`retry_primitive.CONNECTED_SPEECH_SEGMENT_IDS`に不含)の
  ためcool-down/Local Rewriteは適用されず、3回で確定STOPPED。
いずれもテキスト書き換え・Gate回避は行っていない。選択肢(a)(b)は
`NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01_REPORT.md`§Stage 3b/4参照。
Sonnet単独では選択・実装しない。

## 7. Cost / Wall clock
- scaffold後: ¥8.89(openai)
- tts後(最終): **¥120.66**(openai=17.30、gemini=97.24、
  openai_asr=6.11、azure=0.00[corroboration呼び出し5件はコスト計上上
  0円扱い])。
- Guardrail(¥150)以内(目安¥60〜100はcool-down/Local Rewrite多発により
  超過)。
- assemble試行(両level、失敗込み)による追加APIコストは¥0。
- Wall clock: 02:16:14〜03:40:09(UTC、約1時間24分)。うちcool-down
  (10分固定)5回=約50分を占め、実処理時間は正味約34分。

## 8. Gate 3 checklist
| # | 項目 | 状態 |
|---|---|---|
| retry/fallback/regeneration整合 | 既存TTS/ASR retry・cool-down・Local Rewrite・Placeholder Gate・Audio Validation Gate・Human Review Lockは無改変のまま動作(独自バイパスなし) | 充足 |
| runtime evidence(実TTS/Assembly) | 本Packet§2-6、実API呼び出し実測 | 充足(assembly完走はGate STOPのため未達、Meta同様) |
| actual model/routing | scaffold: OpenAI(gpt-5.6-luna、support+Local Rewrite共用)。TTS: Gemini(Charon/Aoede)。ASR: openai_asr+Azure(Tier3 corroboration、今回5件呼出・rescue不成立)。cost内訳§7 | 充足 |
| regression/validator/integration test | 対象runner unit test`er019_family_x_audio_production_runner_01_test_01`: 25/25 PASS(実行前後2回、コード変更なし確認)。全体regression(`run_project_regression.py --pattern "er0*_test_*.py"`)はTTS実行と並行実行したため`collected=3258 passed=3253 failed=3 errors=2`(内訳未取得、他Agent並行作業による汚染の可能性が高くこの数値を本タスクの正式regression結果として採用しない。対象runnerファイル自体は無変更のため単体testの25/25 PASSを本タスクの正式根拠とする) | 一部限定(理由明記) |
| SSOT記載案 | 本タスクはSSOT編集なし(委任文どおり)。事実関係はREPORT.md参照、SSOT反映はFable/ユーザー判断 | 対象外(委任範囲外) |
| Git | 所有ファイル変更なし(runner本体は無改修)。出力ディレクトリ配下のJSON/audit/raw_usage_log(wav除く)+REPORT追記のみ | 充足 |
| Dangling Reference Check | 既存関数は無変更のままimport、コード変更なし | 充足(該当なし) |

## 9. Git
コミット対象(所有ファイルのみ、`git add -A`不使用、runnerコード変更なし):
- `er019_output/family_x_audio_production_wiring_01/
  family_x_b3_diversity_trial_01/hormuz__run_02/**`(wav除く、
  JSON/audit/raw_usage_log.jsonl)
- `NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01_REPORT.md`(§Stage 3b追記、
  既存節は無変更)
commit/push結果・raw URLはこのメッセージ本体(SubagentHandback)に記載。

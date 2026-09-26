# TTS-LOCAL-REWRITE-CONNECTED-SPEECH-PRODUCTION-WIRING-01 — REPORT

Sonnetがユーザー承認済み仕様A〜F(2026-09-26)に基づき実装した、TTS retryの
10分cool-down + Local Rewrite + Natural English QA(Human Review Lock手前の
回復経路)と、Connected Speech(OPEN-122 Equivalence Layer)5-role適用範囲の
Production配線報告。

## 1. 目的

既存のTTS初回/retry経路(`PRODUCTION_MAX_TTS_ATTEMPTS=3`)に対し、以下を追加する。

- (A) 3回とも不合格の場合、Human Review Lock到達前に、問題span周辺のみを
  Luna(`gpt-5.6-luna`)でLocal Rewriteし、7 Gate(意味保持/role保持/Fact
  非矛盾/前後文脈/Natural English[独立Gate]/局所性/非全文)を課し、全PASS
  候補のみ再TTSする。
- (B) attempt1即時→attempt2即時→(NG時のみ)固定600秒cool-down→attempt3。
- (C) Connected Speech Equivalence Layerの適用範囲を、Full Story(Point本文
  含む)/Comment/Preview/Topic intro/In One Lineの5 roleへ拡張する(旧来
  A2/B1英語本文4segment限定から拡張。Comment/Preview/Topic introは、実装
  上の引数欠落により従来構造的に非適用だった)。Heading readout/Key Phrase
  には適用しない。
- (D) Local Rewrite回復が失敗した場合のみ既存Human Review Lockへ進む。

## 2. Recon

詳細: `docs/pm/recon_tts_local_rewrite_wiring_01.md`。要旨:

| role | 現行production関数 | 実施前Connected Speech引数 | 実施前cool-down/Local Rewrite | 実施後 |
|---|---|---|---|---|
| Full Story(+Point本文) | `news_tail_fix.generate_news_narration_wide_margin`(B1)/`generate_a2_segment_with_slowdown`→`generate_english_segment_with_fallback`(A2) | あり(既存) | 無し | B1:追加 / A2:role一元化のみ(Gap) |
| Comment | `voice01.generate_charon_english`(B1) | **引数自体が存在しなかった** | 無し | B1:引数追加+cool-down+回復配線済み |
| Preview | 同上 | 同上 | 無し | 同上 |
| Topic intro | B1:同上 / A2:`generate_english_segment_with_fallback` | B1:無し / A2:あり(旧False固定) | 無し | B1:配線済み / A2:role一元化のみ(Gap) |
| In One Line | B1:`generate_news_narration_wide_margin` / A2:同上 | あり(旧: 明示的False「対象外」) | 無し | **新規enable**。B1:cool-down+回復も配線 |
| Heading readout | `point_headings.generate` | 該当引数なし | 無し | 変更なし(非適用のまま) |
| Key Phrase | `shared_narration.ensure_key_phrase_english_component`等 | 該当引数なし | 無し | 変更なし(非適用のまま) |

既知Gap(隠蔽せず記録): A2経路(`generate_english_segment_with_fallback`)は
role判定の一元化のみ実施し、cool-down/Local Rewrite回復コードは本タスクでは
未配線(第3の関数への複製実装は本タスクの時間内で同水準のtest/runtime
evidenceを取れる保証がなく拡大を避けた)。拡張要否はFable/ユーザー判断待ち。

## 3. 配線構成

新規Production module `er020_tts_retry_local_rewrite_01.py`:

- `connected_speech_enabled_for(segment_id)`: role→適用判定の単一SSOT関数
  (経路ごとの個別ハードコード条件式を廃止)。
- `maybe_cooldown_before_attempt(attempt, max_attempts, cooldown_gate_enabled, sleep_fn)`:
  `max_attempts>=3`の最終attempt直前のみ固定600秒cool-down。
- `run_local_rewrite_recovery(...)`: NG span特定→Luna候補生成(json_schema
  strict、5候補)→Luna 7 Gate QA→選定→`retts_fn`(呼び出し元が渡す1回だけの
  再TTSクロージャ)。

配線先(2関数、いずれも`@review_lock.guarded_generate`配下):

- `er003_v1_sing01_voice01_generate.generate_charon_english`(Comment/
  Preview/Topic intro): 新規`enable_connected_speech_equivalence_layer`引数
  を追加し`secondary_asr.evaluate_attempt_with_cascade`へ転送。cool-down
  呼び出し+`_local_rewrite_recovery_for_charon_english`(`.__wrapped__`を
  `max_attempts=1`で呼ぶ、Trial-01と同じ既存設計パターン)を追加。
- `er003_v1_sing01_news_tail_fix.generate_news_narration_wide_margin`
  (Full Story/In One Line): 同様にcool-down+
  `_local_rewrite_recovery_for_news_narration`を追加(既存
  `enable_connected_speech_equivalence_layer`引数は流用)。

呼び出し元`er003_v1_n3_01_tts_generate.py`(B1 `generate_b1_segments`/A2
`generate_a2_segments`)を、旧`name in (...)`ハードコード条件式から
`retry_primitive.connected_speech_enabled_for(name)`参照へ置換。

回復ヘルパーは`review_lock._has_valid_narration_layout`/
`derive_segment_key`で標準layout(`.../<theme>/<level>/narration/<segment>.wav`)
外のout_pathに対して安全にNoneを返す(既存呼び出し元約50ファイルへの影響
ゼロ)。回復成功時は呼び出し元がstatus="OK"のままreturnし、
`review_lock.record_outcome()`はRESOLVEDへ遷移する(Human Review Lockを
経由しない)。実行時に、retts単独のattempts_log(1件)だけを返すと
累積TTS/ASR call数guard(Part F)が実消費数を数え落とすバグを発見し、
メインループ+re-TTSのattempts_logを連結する修正を行った。

## 4. Runtime evidence(実API)

専用out-dir`er020_output/tts_local_rewrite_production_wiring_01/`。
`TTS_EXECUTION_MODE=STANDARD`。既存記事artifactは無変更。

**差分再生成チェック**: 対象は評価用に新規作成した架空theme
(`evidence_theme_01`)の7 segmentのみ(5 role×1 + Heading×1 + Key Phrase×1)。
既存記事・既存Family X/Family A artifactへの再生成は一切発生していない。

**(a) 5 role適用 + 2 role非適用(各1 segment)**:

| segment | role | 結果 | 備考 |
|---|---|---|---|
| full_story_part1 | FULL_STORY | OK(attempt1) | `enable_connected_speech_equivalence_layer=True`受理 |
| preview | PREVIEW | OK(attempt1) | 同上 |
| topic_intro | TOPIC_INTRO | OK(attempt1) | 同上(従来引数が存在しなかった経路) |
| in_one_line | IN_ONE_LINE | OK(attempt1) | 同上(新規適用) |
| comment_4 | COMMENT | OK(cool-down+Local Rewrite経由、下記(b)) | 同上(従来引数が存在しなかった経路) |
| point_one_heading | HEADING_READOUT | STOPPED→`HUMAN_REVIEW_REQUIRED` | `inspect.signature()`で当該引数が関数シグネチャに**存在しない**ことを確認。Local Rewrite回復も発火せず(意図通り) |
| kp1_en | KEY_PHRASE | OK | 同様に引数なし |

**(b) cool-down→Local Rewrite→QA→再TTS→ASR PASSの実end-to-end経路**
(Family X comment_4「bring the main point together」、2026-09-26実本番runで
attempt1-3すべてASR_VALIDATION_UNCERTAINだった既知segment):

- `voice01.generate_charon_english(max_attempts=3, enable_connected_speech_equivalence_layer=True)`
  をProduction経路(Review Lockデコレータ含む)で実行。
- attempt1/2/3すべてASRが"point"を"points"と聞き取り不一致。
- cool-down実測: `cooldown_actual_seconds=600.009`
  (`cooldown_started_at=2026-09-26T16:48:31+09:00` →
  `cooldown_ended_at=2026-09-26T16:58:31+09:00`、JST)。
- Local Rewrite候補生成(Luna `model_id=gpt-5.6-luna`、5候補)→7 Gate QA
  (Luna `model_id=gpt-5.6-luna`)で`candidate_3`
  ("bring the main point together" → "boil it down to the main idea")を
  選定(全7 Gate PASS)。
- 再TTS(cool-downなし、1回)→ASR完全一致→`status="OK"`確定。
- `review_lock_state.json`: comment_4の最終`state`は**`RESOLVED`**
  (`HUMAN_REVIEW_REQUIRED`に到達せず)。対比としてpoint_one_headingは
  `HUMAN_REVIEW_REQUIRED`のまま(Local Rewrite回復機構を持たないため)。
- 総wall clock: 702.4秒。

詳細: `er020_output/tts_local_rewrite_production_wiring_01/
comment_4_cooldown_local_rewrite_evidence.json`・`roles_evidence.json`・
`evidence_theme_01/b1b/audit/review_lock_state.json`。

## 5. コスト表

| 項目 | 内訳 |
|---|---|
| 5 role + 2 role(a) | gemini(TTS)+openai_asr、合計¥2.62 |
| cool-down+Local Rewrite経路(b) | gemini(TTS)¥5.86+openai_asr¥0.27+openai(Luna)¥1.02 |
| 合計 | **¥7.15**(予算上限¥100に対し十分な余裕、想定¥25〜50の下限側) |

## 6. テスト

- 新規`er020_tts_retry_local_rewrite_01_test_01.py`(22件、オフラインmock、
  API呼び出し¥0): role taxonomy(5+2+未知/None)・cool-down発火条件
  (attempt1/2では発火せず、`max_attempts>=3`の最終attemptかつgate=Trueの
  みで発火)・NG span特定・compute_unchanged_ratio・7 Gate QA選定(全PASS/
  一部FAIL)・回復パイプライン4分岐(RESOLVED/NO_CANDIDATE_PASSED_QA/
  RETTS_FAILED/NO_NG_SPAN)・呼び出し元ヘルパーの非標準layoutでの安全な
  None返却。全22件PASS。
- 既存regression: `python -m unittest discover -s . -p "*_test_01.py"`
  (1156件、他並行タスクの追加分含む)。**3件failure**、いずれも
  「Production module/Family Aファイルにuncommitted git diffが無いこと」
  を検証する既存自己チェックテスト(`er019_family_x_pointless_01_test_01.
  FamilyAUnchangedTest`・Trial-01/02自身の`ProductionModuleUnchangedTest`)
  で、本タスクが正規に`er003_v1_sing01_voice01_generate.py`等を変更した
  ことによる一時的な差分検知(commit後は`git status --porcelain`/
  `git diff --stat`が空になり自然解消する既知の性質。DECISION_LOG既往
  エントリでも同種の扱い)。他1153件PASS。

## 7. SSOT

- `CURRENT_SPEC.md` L1262(新規行、TTS retry cool-down/Local Rewrite/
  Natural English QA仕様+Connected Speech 5 role適用範囲、既知Gap明記)。
- `DECISION_LOG.md`(本管理IDエントリ、末尾に追記)。
- `OPEN_ITEMS.md` OPEN-122(適用範囲更新: A2/B1英語本文4segment限定→5
  role[In One Line新規]、Comment/Preview/Topic introの引数欠落修正を明記、
  A2側Gapを記録)。OPEN-121(TTS Repetition/False Start QA)は別仕様のため
  **変更していない**(適用範囲は無変更)。
- Dangling Reference Check: Trial artifact
  (`er020_output/tts_cooldown_local_rewrite_trial_01/`・
  `er020_output/tts_local_rewrite_natural_english_qa_trial_02/`)・旧
  「A2/B1英語本文4segment限定」表記への参照が新規コード・コメントに残って
  いないことをGrepで確認。

## 8. Production Wiring Checklist(16項目)証跡表

| # | 項目 | 状態 | 根拠 |
|---|---|---|---|
| 1 | Production正式TTS初回path | 充足 | §3(2関数への配線) |
| 2 | retry path | 充足 | §3 |
| 3 | 10分cool-down | 充足 | §4(b)実測600.009秒 |
| 4 | Local Rewrite | 充足 | §4(b) |
| 5 | Natural English QA | 充足 | §4(b)(7 Gateの1つ、独立Gate) |
| 6 | Luna actual model_id | 充足 | `gpt-5.6-luna`(§4(b)) |
| 7 | retry・fallback・regeneration整合 | 充足(B1・A2とも、修正1回目) | §2既知Gap→§12で解消 |
| 8 | 5 roleすべてでConnected Speech発火 | 充足 | §4(a)(b) |
| 9 | Heading・Key Phraseには非適用 | 充足 | §4(a)(inspect.signatureで引数不在を確認) |
| 10 | Human Review前にLocal Rewrite recovery | 充足 | §4(b)(review_lock_state.json= RESOLVED) |
| 11 | runtime evidence | 充足 | §4 |
| 12 | integration・regression test | 充足(3件既知failureのみ) | §6 |
| 13 | CURRENT_SPEC | 充足 | §7 |
| 14 | DECISION_LOG | 充足 | §7 |
| 15 | OPEN_ITEMS | 充足 | §7 |
| 16 | Git反映 / Dangling Reference Check | commit後に充足(本コミットで反映) | §7、下記commit(修正1回目分も同様) |

## 9. Sonnet仮判定(初回、参考)

B1経路(Comment/Preview/Topic intro/Full Story/In One Line、5 role)は
Checklist16項目のうち15項目を充足し、Git反映(#16)は本commitで満たされる。
**A2経路は#7(retry・fallback・regeneration整合)が未充足(cool-down/Local
Rewrite回復コード未配線のGapあり)**。よってSonnet仮判定は
**「B1経路: `PRODUCTION_WIRED`相当の技術的証跡は揃っている」「A2経路:
`WIRING INCOMPLETE`」**とする(`PRODUCTION_WIRED`の正式宣言はFable/ユーザー
判断)。**→修正1回目(§12)でA2側のGapを解消した。以下は初回判定として
そのまま保持し、更新後の仮判定は§12末尾を参照。**

## 12. 修正1回目(Fable差し戻し対応、2026-09-26)

### 12.1 Fable指摘

ユーザー承認仕様は「Production正式TTS初回/retry path」全体と「role差による
漏れがない形」を要求しており、A2(Standard)経路
`generate_english_segment_with_fallback`に cool-down/Local Rewrite/Natural
English QA 回復が未配線のままでは Checklist #1/#7 未充足で
`PRODUCTION_WIRED`にできない、との差し戻し。

### 12.2 配線構成(A2経路)

`er003_v1_crosslevel_audio_02_common.generate_english_segment_with_fallback`
は、標準経路(`generate_narration_snippet_verified_strict`、最大2回)+
fallback(minimal instruction)経路(最大1回)で総予算3回を構成する既存設計
(標準2+fallback1=3)。fallbackのこの1回が総予算3回の実質最終attemptに
あたるため、ここへB1と**同一の**`er020_tts_retry_local_rewrite_01`関数を
配線した(第3の複製実装ではない)。

- fallbackループの各attempt直前で`retry_primitive.maybe_cooldown_before_
  attempt(overall_attempt, max_attempts, enable_connected_speech_
  equivalence_layer)`を呼ぶ(`overall_attempt`=標準側消費済みattempts数+
  fallback側のloop attempt番号)。
- fallback単体の本体ロジック(既存コードをそのまま移設)を
  `_run_a2_minimal_fallback_attempt()`という共通ヘルパーへ抽出し、通常の
  fallbackループと、Local Rewrite回復の再TTS(retts_fn)の両方から同じ
  ヘルパーを呼ぶ(コード重複を避ける、B1側`voice01.py`/`news_tail_fix.py`
  は無変更)。
- 標準+fallbackとも不合格の場合(stop_retrying経由の早期終了、または
  fallback予算exhaustionの2経路とも)、`enable_connected_speech_
  equivalence_layer=True`のときのみ`_local_rewrite_recovery_for_english_
  segment_with_fallback()`(新規ヘルパー)を呼び、内部で`retry_primitive.
  run_local_rewrite_recovery()`(B1と同一関数)を実行する。回復成功時は
  status="OK"のまま返し、失敗時はNoneを返して従来通りHuman Review Lockへ
  進む(B1と同一のHuman Review Lock到達条件)。
- あわせて、A2 topic_intro呼び出し(`er003_v1_n3_01_tts_generate.py::
  generate_a2_segments`)が`enable_connected_speech_equivalence_layer`
  引数自体を渡していなかった漏れ(role差による構造的な非適用)を修正し、
  B1側(`generate_b1_segments`)と同様`retry_primitive.connected_speech_
  enabled_for("topic_intro")`を参照するようにした。

**構造的事実(Gapではなく記事構成自体の違い、隠蔽せず記録)**: A2の
Preview/Comment(1-4)は英語ナレーションとして存在しない
(`generate_a2_japanese_with_reading_safety`経由の日本語音声、
`generate_a2_segments`のコード自体がそうなっている)。よってA2側で
「5 role」のうち実際に適用され得るのはFull Story(Point本文含む)/
Topic intro/In One Lineの3 roleのみであり、Comment/Previewの2 roleは
A2側にそもそも適用対象が存在しない。

### 12.3 Runtime evidence(実API、`er020_output/tts_local_rewrite_production_wiring_01/a2/`)

**差分再生成チェック**: 対象は評価用に新規作成した架空theme
(`evidence_theme_01/a2`)のsegmentのみ。既存記事・既存Family X/Family A
artifactへの再生成は一切発生していない。**キャッシュ確認**:
narration_dirは本タスクで新規作成、既存キャッシュなし。**予算**:
Guardrail上限¥100(超過見込み時STOP)。

**(a) A2で実在する3 role(各1 segment、attempt1でOK)**:

| segment | role | 結果 | 備考 |
|---|---|---|---|
| full_story_part1(相当) | FULL_STORY | OK(attempt1) | `enable_connected_speech_equivalence_layer=True`受理 |
| topic_intro | TOPIC_INTRO | OK(attempt1) | 同上(旧: 引数自体が渡っていなかった漏れを修正) |
| in_one_line | IN_ONE_LINE | OK(attempt1) | 同上 |

詳細: `er020_output/tts_local_rewrite_production_wiring_01/a2/
roles_evidence.json`。

**(b) cool-down→Local Rewrite→QA→再TTS→ASR再検証の実end-to-end経路**:

架空theme上の新規segment(数値表記の言い換えが必要なテキスト、"The price
rose to two point three million dollars, a fifteen percent increase from
last year.")で実行。

- 標準経路2回とも、ASRが正しく意味を捉えつつ数字表記(digit形式)で
  書き起こすため`TRUE_CONTENT_MISMATCH`(2回とも同一)。
- fallback(3回目)直前で実測cool-down: `cooldown_actual_seconds=600.004`
  (`cooldown_started_at=2026-09-26T17:32:19+09:00` →
  `cooldown_ended_at=2026-09-26T17:42:19+09:00`、JST)。
- fallback(3回目)も同一signatureでNG。
- Local Rewrite候補生成(Luna`gpt-5.6-luna`、5候補)→7 Gate QA(Luna
  `gpt-5.6-luna`)で`candidate_2`("two million three hundred thousand
  dollars"、全7 Gate PASS)を選定。
- 再TTS(cool-downなし、1回)を実行したが、post-retts ASR再検証も不一致
  (依然digit/spelled-out表記差)。最終`status`は
  `HUMAN_REVIEW_LOCKED_RETTS_FAILED`(`run_local_rewrite_recovery()`が
  定義する4分岐の1つ、Human Review Lockへ正しく進む正常な終端)。
- 総wall clock: 707.8秒。

同一回復パイプラインを、別の話題(homophone想定の"forty"、court merger
の平易文)でも実行し、いずれも標準経路attempt1で合格(cool-down/Local
Rewriteは発火せず、既定の正常系動作を再確認)。詳細:
`er020_output/tts_local_rewrite_production_wiring_01/a2/
comment_test2_probe.json`(cool-down+Local Rewrite発火分)・
`er011_output/local_rewrite_recovery/evidence_theme_01/a2/
local_rewrite_recovery_comment_test2.json`(候補生成/QA/選定の全ログ)。

**正直な報告**: B1の"boil it down to the main idea"のような
`RESOLVED_BY_LOCAL_REWRITE`(完全解決)への到達は、A2側の実行では確認
できなかった(今回選んだ失敗モードが数字表記形式の差[digit vs
spelled-out]であり、言い換えでは解決しにくい性質だったため、と観察
している。既存の6% slowdown post-process再検証[`apply_a2_slowdown_
postprocess`]と同種の傾向)。ただし、cool-down実測・Local Rewrite候補
生成/QA(Luna実model_id)・再TTS・ASR再検証という回復パイプライン全工程
が実際に発火し、`run_local_rewrite_recovery()`が定義する正しい終端状態
(`HUMAN_REVIEW_LOCKED_RETTS_FAILED`)へ到達することは実証した(配線
自体の正しさの証跡)。

### 12.4 Natural English Gate "main idea"整合性確認(記録のみ、再生成なし)

Fable指摘(Trial-02で"main idea"を含む候補がFAILした経緯と、run_01の
comment_4で"main idea"を含む候補がPASSした経緯の整合性)について、両方の
実際のLuna判定ログを突き合わせ、`er020_output/tts_local_rewrite_
production_wiring_01/natural_english_gate_main_idea_reconciliation.md`
に記録した。結論: 矛盾ではない。両runとも、"bring...together"型の
機械的な単語置換("bring the main idea together")は一貫してNatural
English Gate FAILと判定され、"boil it down to"/"distill...into"のような
別の慣用的な言い換えは一貫してPASSしている。

### 12.5 テスト(修正1回目分)

新規`er007_ja_tts_retry_path_fix_test_01.py::A2CooldownLocalRewriteWiringTests`
(5件: cooldown非発火[gate=False]・cooldown発火[実際の`maybe_cooldown_
before_attempt`呼び出し引数を検証]・Local Rewrite回復RESOLVED分岐・
Local Rewrite回復失敗分岐・gate=FalseでのLocal Rewrite非発火)、
`A2TopicIntroConnectedSpeechRoleWiringTests`(1件、topic_introのrole配線
regression guard)、`er020_tts_retry_local_rewrite_01_test_01.py`に
A2側`_local_rewrite_recovery_for_english_segment_with_fallback`の非標準
layout安全性テスト1件を追加。全件オフラインmock(API呼び出し¥0)。
既存regression `python -m unittest discover -s . -p "*_test_01.py"`
実行(詳細は下記QCD/commit hash欄参照)。

### 12.6 SSOT変更

`CURRENT_SPEC.md` L1262(A2経路配線・topic_intro修正・A2の構造的事実
[Preview/Comment非該当]を追記)。`OPEN_ITEMS.md` OPEN-122(A2側Gap解消を
追記)。`DECISION_LOG.md`(本管理IDエントリへ修正1回目の要旨を追記)。

### 12.7 費用(修正1回目分、実API)

| 項目 | 内訳(概算、cost logger未使用のためrun_01の単価から概算) |
|---|---|
| 3 role評価(a) | TTS 3回+ASR 3回 |
| cool-down+Local Rewrite経路(b、comment_test2) | TTS 4回(標準2+fallback1+retts1)+ASR 4回+Luna 2回(候補生成+QA) |
| 追加probe(comment_test3/4、正常系再確認) | TTS 2回+ASR 2回 |
| 概算合計 | 約¥15〜20(run_01実測¥7.15[TTS/ASR/Luna計8回相当]を基準に呼び出し数で按分した概算値。予算上限¥100に対し十分な余裕) |

### 12.8 Checklist16項目(修正1回目後)

#7(retry・fallback・regeneration整合)・#8(5 role Connected Speech発火)は
A2経路の配線完了+runtime evidenceにより充足(A2側Comment/Previewは
「非該当」という構造的事実であり、非充足ではない)。他項目は§8のまま。

### 12.9 STOP条件該当の有無

該当なし(新しいConnected Speech仕様の追加は発生していない、既存Human
Review Lock/ASR cascade/Foreign Token Gateとの矛盾は確認されていない、
想定外の全segment再生成は発生していない)。

### 12.10 Sonnet仮判定(修正1回目後)

B1経路・A2経路とも、Checklist16項目のうち15項目(#1-15)を技術的に充足
し、Git反映(#16)は本commitで満たされる。A2経路のcool-down/Local
Rewrite回復パイプラインは実際に発火し正しい終端状態へ到達することを
実証したが、**A2側での`RESOLVED_BY_LOCAL_REWRITE`(完全解決)の実例は
今回未取得**(§12.3「正直な報告」)。よってSonnet仮判定は「B1経路・A2
経路とも`PRODUCTION_WIRED`相当の技術的配線・証跡は揃っている」とする
(`PRODUCTION_WIRED`の正式宣言はFable/ユーザー判断)。

## 10. Fable評価

(1) Checklist16項目はB1経路・A2経路とも証跡が揃っている(#7/#8はA2側を修正1回目で充足。A2のPreview/Commentは英語ナレーションが存在しない構造的事実であり非充足ではない)。role→Connected Speech適用判定が単一関数`connected_speech_enabled_for()`に集約され、経路別フラグが廃止された点、cool-down(固定600秒)→Local Rewrite→7 Gate QA(Natural English含む、Luna 1 call)→再TTS→未解消時のみHuman Review Lock、の順序がB1・A2で同一moduleにより保証されている点を確認。(2) runtime evidence: B1(comment_4)で実600.009秒cool-down→Local Rewrite→再TTS ASR一致→`RESOLVED`の完全経路、A2で実600.004秒cool-down→Local Rewrite→再TTS→`HUMAN_REVIEW_LOCKED_RETTS_FAILED`(正常終端)の経路を確認。A2側で`RESOLVED_BY_LOCAL_REWRITE`の実例は未取得だが、同一module関数の発火・終端到達が実証されており配線証跡としては充足。(3) 留保2点(配線Statusには影響しない記録事項): ①A2 evidenceの失敗モードが「数字表記(digit)とspelled-outのASR不一致」で、Local Rewriteでは解決しにくい種類。ASR照合の数値正規化(`classify_asr_match`のbenign扱い)は別Open項目として記録する。②A2 evidenceの費用がcost logger未使用の概算(¥15〜20)。以後のTTS runtime evidenceは必ずcost loggerを通す。(4) Natural English Gateの"main idea"判定(Trial-02 FAIL vs 本番PASS)は候補文全体が異なり一貫した判定と確認済み。(5) 費用: 初回¥7.15+修正1回目概算¥15〜20。

## 11. 分類

**PRODUCTION_WIRED**(Fable Gate判定、2026-09-26。ユーザー承認仕様[Local Rewrite+Natural English QA、10分cool-down、Connected Speech 5役割適用/Heading・Key Phrase非適用]との一致を確認。B1・A2両経路)。

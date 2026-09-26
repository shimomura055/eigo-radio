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
| 7 | retry・fallback・regeneration整合 | 充足(B1) / **一部Gap(A2)** | §2既知Gap |
| 8 | 5 roleすべてでConnected Speech発火 | 充足 | §4(a)(b) |
| 9 | Heading・Key Phraseには非適用 | 充足 | §4(a)(inspect.signatureで引数不在を確認) |
| 10 | Human Review前にLocal Rewrite recovery | 充足 | §4(b)(review_lock_state.json= RESOLVED) |
| 11 | runtime evidence | 充足 | §4 |
| 12 | integration・regression test | 充足(3件既知failureのみ) | §6 |
| 13 | CURRENT_SPEC | 充足 | §7 |
| 14 | DECISION_LOG | 充足 | §7 |
| 15 | OPEN_ITEMS | 充足 | §7 |
| 16 | Git反映 / Dangling Reference Check | commit後に充足(本コミットで反映) | §7、下記commit |

## 9. Sonnet仮判定

B1経路(Comment/Preview/Topic intro/Full Story/In One Line、5 role)は
Checklist16項目のうち15項目を充足し、Git反映(#16)は本commitで満たされる。
**A2経路は#7(retry・fallback・regeneration整合)が未充足(cool-down/Local
Rewrite回復コード未配線のGapあり)**。よってSonnet仮判定は
**「B1経路: `PRODUCTION_WIRED`相当の技術的証跡は揃っている」「A2経路:
`WIRING INCOMPLETE`」**とする(`PRODUCTION_WIRED`の正式宣言はFable/ユーザー
判断)。

## 10. Fable評価

(空欄)

## 11. 分類

(空欄)

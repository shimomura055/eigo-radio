# RESULT_PACKET_WIRING_FAMILY_C.md

管理ID: FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-AND-USER-TEST-INVENTORY-01(委任A)

## 1. T-0 / Family C Production経路の現状確定

- T-0: 委任文を`docs/pm/delegation_log/FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-01_A.md`へ保存し`check_delegation_prompt.py`実行。結果=`FAIL`(reasons: 「実行コマンドに引数/絶対パスが無い行を検出: ``` が10件」。これは委任文中のコードブロック区切り記号```を実行コマンド行と誤検知した既知の形式的falseレポートであり、必須キーワード8/8・固定ブロックE-1/D-1/G-1/F-1全OK。FAILでも作業は継続[T-0既定どおり]。
- Grep1(現状確定): `Glob er013_family_c_*production*.py`=0件(未存在)。`Grep "family_c|Family C" er012_b_family_production_runner_01.py`=0件。`Grep "Family C" CURRENT_SPEC.md`=0件(本タスク前)。想定どおりFamily C専用Production moduleは存在せず、Trial script(`er013_family_c_episode_trial_09〜12`系)のみが存在していた。

## 2. Story TTS segmentation原則

- Status: `PRODUCTION_WIRED`
- Production初回path: `er013_family_c_production_01.py::plan_story_segments()`(+`build_flat_voice_chunks`/`classify_quote_voice_window`/`split_paragraph_by_quotes`/`_apply_word_guideline_splits`)。runner: `er013_family_c_production_runner_01.py::build_plan_for_level()`(`--plan-only`)。
- retry/regeneration/fallback/resume整合: 本委任のrunner実装では、Comment生成(`generate_family_c_a2_comment`)が禁止語句検出時に**同一関数内**で自動retryする設計(呼び出し元で別ロジックを持たない)。Segment側は`plan_story_segments()`が唯一の分割ロジックであり、TTS再生成が必要になった場合も同じplanの`seg["tts_text"]`を再利用する構造(本タスクでは実TTS呼び出しは行っていない、QCD注意「不要な再生成禁止」に基づく)。
- runtime evidence(6記事、`--plan-only`、¥0、TTSなし):

| 記事 | level | segment数 | 最短/最長語数 | warning | approved成果物との一致 |
|---|---|---|---|---|---|
| Memory | a2 | 10 | 2/89 | 0 | **完全一致**(Trial-11、10 seg/最長89語) |
| Memory | b1 | 10 | 2/91 | 0 | **完全一致**(Trial-12委任1、10 seg/最長91語) |
| Digital Twins | a2 | 22 | 2/99 | 0 | **完全一致**(narrator12/twin10、Trial-12委任2) |
| Digital Twins | b1 | 24 | 2/97 | 0 | **完全一致**(narrator13/twin11、Trial-12委任2) |
| Home Robots(参考のみ、再生成なし) | a2 | 13 | 2/96 | 0 | 旧25 segmentと相違(差分理由下記) |
| Home Robots(参考のみ、再生成なし) | b1 | 18 | 3/92 | 2(hard_avoid超過166語→自動2分割) | 旧未整理版との単純比較なし(初のsegmentation計画) |

  Home Robots差分理由: 原記事の入れ子引用符(例: `"I wrote: 'I am fine...'"`)・選択肢表示段落(`**CARE HOUSE...** / **HOME...**`)が、Memory/Twinsで確認した汎用quote-window判定パターンの対象外であるため、一部のVoice区間(段落6/14/16/18周辺)が新原則では別区分になる。Home Robotsは承認済み既存音声を再生成しない前提のため「新原則を適用した場合の参考計画」としてのみ提示。
  b1で実際にhard_avoid_words(150語)超過(166語)に対する自動段落境界分割(`word_count_guideline_auto_split`)が発火し、両半分に`auto_split_hard_avoid_exceeded`warningが記録されることを確認(機構の実発火確認)。
- Twins A2「The door opened.」(story_019、3語、旧設計と同一)は本runtime evidenceでも同一のVoice境界+scene boundary保持による分割として再現(現状維持)。
- tests: `er013_family_c_production_test_01.py`の`PlanStorySegmentsUnitTests`(7件)+`ApprovedEpisodeReproductionTests`(4件、Memory A2/B1・Twins A2/B1のsegment数・最長語数を`assertEqual`で厳格照合)。
- SSOT更新位置: `CURRENT_SPEC.md`「Family C(Future Story)Production」節(新設、`## Cross-level仕様`直前)。`DECISION_LOG.md`新エントリ(`## FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-AND-USER-TEST-INVENTORY-01`、「参照元」節直前)。`OPEN_ITEMS.md` OPEN-147行末追記・OPEN-157行末追記。
- commit hash: 本PACKET末尾参照。

## 3. A2 Comment理解ガイド型Contract

- Status: `PRODUCTION_WIRED`
- Production初回path: `er013_family_c_production_01.py::FAMILY_C_A2_COMMENT_ROLE_JA_1/2/3`+`check_a2_comment_quality()`+`generate_family_c_a2_comment()`。runner: `er013_family_c_production_runner_01.py::run_comments_only()`。
- retry/regeneration/fallback: `generate_family_c_a2_comment()`内部の1ループで初回生成→品質チェック(`check_a2_comment_quality`)→NG時は**同一Contract・同一関数**で`max_retries`回まで再試行(`er013_family_c_production_test_01.py::GenerateFamilyCA2CommentRetryTests`でモック確認、同一promptで2回呼ばれることを検証)。呼び出し元が異なるロジックの「retry専用path」を持てない設計。
- B1非適用の構造的担保: `grep FAMILY_C_B1_COMMENT er013_family_c_production_01.py` = 0件(そもそもB1用定数を持たない)。`guard_a2_only("b1")`はRuntimeErrorを送出(テストで確認)。runner`run_comments_only()`はlevel!="a2"の場合`guard_a2_only`を呼びRuntimeErrorで停止。
- runtime evidence(Memory A2、実LLM呼び出し、TTSなし、¥9.00):
  model=`gpt-5.6-luna`、routing=`er003_v1_iran01_a2_generate.run_support_text`、Contract=`FAMILY_C_A2_COMMENT_ROLE_JA_1/2/3`。3件とも1回目で禁止語句0件・品質チェックPASS。

  | Comment | 新生成(本タスク) | Trial-11生成(参考) |
  |---|---|---|
  | 1 | レナは、両手で小さな銀色の箱を持っています。箱の中には、亡くなった兄との最後の記憶が一つだけ入っています。しかし、レナはその記憶をまだ開けていません。 | レナは小さな銀色の箱を両手で持っています。その箱の中には、亡くなった兄との最後の記憶が一つだけ入っています。しかし、レナはその記憶をまだ一度も開けていません。 |
  | 2 | レナが兄に関する記憶を箱にしまってから、五年という時間がたちました。五年後の寒い朝、箱から記憶が戻り始めます。このあと、兄の最期の言葉を含む記憶がよみがえります。 | レナが記憶を箱に預けてから、五年がたちました。五年後の冷たい朝、台所にいたレナのもとへ、箱からその記憶が戻ってきます。その中では、兄の最期の言葉もよみがえります。 |
  | 3 | レナは銀色の箱に手を伸ばしたまま、記憶を止めるか迷っています。記憶をもう一度先送りするのか、それとも今ここで受け止めるのかが、目の前の選択です。 | 記憶を取り戻したレナは、記憶をもう一度箱へ戻せるよう、箱に手を伸ばしたまま迷っています。記憶を箱へ戻して先送りするか、それとも今ここで記憶を受け止めるか、その選択が問題になっています。 |

  全文保存先: `er013_output/family_c_production/memory/evidence/a2_comment_runtime_evidence.json`(attempts・quality_check・prompt含む)。
- tests: `A2CommentQualityCheckTests`(5件)+`GenerateFamilyCA2CommentRetryTests`(3件、retry成功/retry上限到達RuntimeError/B1ガード)。
- SSOT更新位置: CURRENT_SPEC同節内(仕様B)、DECISION_LOG新エントリ内。
- commit hash: 本PACKET末尾参照。

## 4. Dangling Reference Check結果表

| 参照元 | 参照先(関数/定数) | 実在確認 |
|---|---|---|
| `er013_family_c_production_runner_01.py` | `fam_c.plan_story_segments` | Grep一致(line 73)、moduleに定義あり |
| `er013_family_c_production_runner_01.py` | `fam_c.generate_family_c_a2_comment` / `check_a2_comment_quality` | Grep一致、moduleに定義あり |
| `er013_family_c_production_test_01.py` | `plan_story_segments`/`check_a2_comment_quality`/`generate_family_c_a2_comment` | 21件一致、いずれもmodule定義済み関数 |
| `er013_family_c_production_01.py` / `_runner_01.py` | Trial script(`import er013_family_c_episode_trial*`) | **0件**(非依存確認、python re Grep実測) |
| `CURRENT_SPEC.md`「Family C(Future Story)Production」節 | `er013_family_c_production_01.py`/`_runner_01.py`/`_test_01.py` | 3ファイルとも実在(本タスクで新規作成、commit対象) |
| `OPEN_ITEMS.md` OPEN-157/158追記 | CURRENT_SPEC「Family C(Future Story)Production」節 | 節実在(同上) |
| `DECISION_LOG.md`新エントリ | `docs/pm/RESULT_PACKET_WIRING_FAMILY_C.md` | 本ファイル実在 |

Trial-onlyのみに仕様が存在する状態・retryのみ新仕様参照・validatorのみ新仕様前提・A2 Comment仕様のB1誤適用、いずれも該当なし。

## 5. Gate判定

**`PRODUCTION_WIRED`**

完了判定12項目チェック表:

| # | 項目 | 証跡 |
|---|---|---|
| 1 | Production正式初回path実装 | `er013_family_c_production_01.py`+`er013_family_c_production_runner_01.py` |
| 2 | retry・fallback・regeneration整合 | `generate_family_c_a2_comment`内蔵retryループ(同一関数、モックテスト確認) |
| 3 | Trial専用script依存なし | import Grep 0件(module/runner) |
| 4 | runtime evidenceあり | 6記事segmentation plan(¥0)+Memory A2 Comment実LLM(¥9.00) |
| 5 | Regression/integration PASS | `run_project_regression.py --pattern "er013*_test_*.py"` 306/306 PASS(新規22件含む16ファイル) |
| 6 | actual model/routing証跡 | `gpt-5.6-luna`/`er003_v1_iran01_a2_generate.run_support_text`(evidence json記録) |
| 7 | CURRENT_SPEC更新 | 「Family C(Future Story)Production」節新設 |
| 8 | DECISION_LOG更新 | 新エントリ(本委任ID) |
| 9 | OPEN_ITEMS更新 | OPEN-147/157/158行末追記 |
| 10 | Dangling Referenceなし | 本PACKET4節の表 |
| 11 | Git commit/push確認 | 本PACKET末尾のcommit hash |
| 12 | ユーザー承認内容とProduction挙動一致 | approved 4 episode(Memory A2/B1・Twins A2/B1)のsegment数・最長語数が完全一致、A2 Comment理解ガイド型が禁止語句0件で実発火 |

## 6. Twins A2「The door opened.」現状維持採用の記録位置

`DECISION_LOG.md`新エントリ1行目(「Twins A2『The door opened.』3語segmentは現状維持で採用...USER_DECISION_REQUIRED解消」)。CURRENT_SPEC「Family C(Future Story)Production」節Status欄末尾にも明記。

## 7. 費用・確認事項

- 費用(LLM実費): ¥9.00(Memory A2 Comment 1〜3、各1回、上限¥10/タスク上限¥25以内)。segmentation runtime evidenceは¥0(`--plan-only`、TTS/LLM呼び出しなし)。
- Trial-10/11/12成果物無変更: `git status --porcelain er013_output/family_c_episode_trial_10/ er013_output/family_c_episode_trial_11/ er013_output/family_c_episode_trial_12/` = 空(出力なし)。
- 回帰結果: 306 tests OK(新規`er013_family_c_production_test_01.py` 22件含む16ファイル)。
- commit hash: `a04c9221`。push: origin/main。
- 残差分要約: Home Robots(A2/B1)は既存承認済み音声を再生成せず、新原則適用時の「参考計画」としてのみ提示(旧segmentationとは一致しない、理由は2節記載)。これは委任文が明示的に許容する範囲(「Home robotsはTrial-10方式のまま承認済みのため『新原則を適用した場合の計画』として提示のみ」)。

## 8. STOP該当有無・事前指定外Read

- STOP該当: なし(未承認の新仕様決定は発生せず、既存Production architectureとの重大な衝突もなし、追加API費用は¥9.00のみで大規模ではない)。
- 事前指定外Read(理由付き):
  1. `er013_family_c_episode_trial_12_twins_b1_run.py`のsegmentation関数本体(行120-280): 事前指定は「retry|fallback|regenerate|resume|.ok|cascade」Grepのみだったが、Twins B1のarticle_configを正確に構築するため`classify_quote_voice`/`build_story_segments_trial12_twins_b1`の実装を追加Read。
  2. `er013_output/family_c_episode_trial_09/home_robots_v2/segments.json`・`speaker_map.json`: Home Robots用article_config(voice_keywords)を構築するため、既存承認済み出力から話者判定パターン(robot/mother keyword)を確認する目的で追加Read(事前指定Read一覧に無し、Trial-09本体scriptは未読)。
  3. `er013_family_c_episode_trial_11_memory_run.py`のCOMMENT_1/2/3_ROLE_JA_TRIAL11本文(行420-467)・segmentation add()呼び出し(行260-340相当): Memory A2 article_configのcontent_facts/scene_transitionおよびforce_split境界を正確に再現するため、事前指定の「差分確認用」の範囲を超えて追加Read。
  4. `er013_output/family_c_episode_trial_11/memory_a2/comments_ja.md`: A2 Comment runtime evidenceでTrial-11実生成文と並記するため追加Read(事前指定はRESULT_PACKET数値のみ)。

# INHERITANCE_STATUS_01: Family X基盤の継承状況とFamily Y固有の追加部分(FAMILY-Y-VOICES-DESIGN-01 委任_04)

位置づけ: Phase 0〜2(テキスト段階)の到達状況。X/Zの.py・Prompt・閾値・辞書は**1行も変更していない**(下の証拠)。Yの追加は全て新規ファイル`er110_family_y_*.py`(DEV/Trial専用)。

## 1. 接続点T1〜T17の対応(設計書 DESIGN_PROPOSAL_02 §③-4)
| T | 接続点 | 本Trialでの実施状況 | 区分 |
|---|---|---|---|
| T1 | Writer prompt | Y版R0(`build_y_r0_prompt`)を新規。Fact Lockブロックは`er053_family_x_factlock_ja_writer_01.build_r0_block`を**そのまま呼出**(逐語、testで同一性固定)、記号予防ブロック・AN3固有名詞文も既存定数を流用。R1/R2=X`USER_TMPL`を逐語流用+Y追加1段落。実行済み | A+新規 |
| T2 | B3/Fact選定 | **X B3を無変更で使用**(`xr.run_storyline_b3`、契約V1〜V10・注記producer・丸め判断まで既存関数)。視点候補はB3とは**別call**(`build_cast_prompt`、+約2.1円)。設計書は「Y版B3の出力に視点候補を含める(呼出回数不変)」だったが、B3統合は設計書自身が『Trial後』と位置づけており、原因切り分けのため別callにした(差分として記録) | A+新規 |
| T3 | 構造定義・分割 | `parse_article`/`check_contract`(日本語5段落)、`split_en_article`/`check_en_contract`(英語)。segment用Y分割関数(audio plan)はPhase 3 | 新規 |
| T4 | 英訳/簡易化 | 既存`generate_family_x_faithful_translation`/`generate_family_x_standard_a2_no_heading`をそのまま呼出。5段落ちょうど・話者取り違え防止をY側で決定論確認(JA/Adv/Std×3原稿=全PASS、再生成0) | A+新規(小) |
| T5 | Preview/Comment scaffold | Comment 1・PreviewはX既存role、Comment 2/3はY用role(`Y_COMMENT_2_ROLE`/`Y_COMMENT_3_ROLE`、「第1部・第2部」前提を除去)。**Comment 4は生成していない**(`scaffold_summary.json`の`comment_4_generated=false`)。R2g/R0gのStd/Adv全4件で生成OK | 新規 |
| T6 | KP選定 | `sc.run_key_phrases(kp_backend="fulltext_p2")`をそのまま。4件ともCANONICALIZATION_PASS(KP 3件、CMU gate・gloss alignment含む) | A |
| T7 | In One Line | `_advanced_in_one_line`(M1(a)入り)・A2側の既存生成。仕様内(2〜3文)で全PASS | A |
| T8 | segment ID検査の網羅 | **未実施(音声なし)**。再Grepで直書き一覧を最終化(下表2)。parity testはPhase 3のY runnerと同時に実装する | A+小改修+test(Phase 3) |
| T9 | TTS segment生成・Voice割当 | 未実施(Phase 3)。固定割当は`TTS_VOICE_FIXED`に定数化(自動割当関数は使わない)。reuse keyへのvoice名追加(M4)はPhase 3 | 新規+A |
| T10 | Style profile | 未実施(Phase 3)。`er019_family_x_style_profile_01.py:201`の`FULL_STORY`がpart1〜3固定→Y用にpart4/5を渡す必要あり | A |
| T11 | Assembly timeline | 未実施(Phase 3)。Y用segment順序表は`PHASE3_PLAN_01.md` | 新規 |
| T12 | 試聴ページ | 未実施(Phase 3) | A+新規 |
| T13 | scope限定機構 | 未実施(Phase 3)。`er103_proper_noun_alarm_policy_01.py:42` `APPROVED_SCOPES={"X","Z"}`、`er109_xz_scope_01.py`等に"Y"追加が必要(技術対応、PM_GOVERNANCE 28-1運用7) | 技術対応 |
| T14 | RF | **実施**。X共有関数`rf.run_risk_flagger`を呼出(Review QueueはTrialのdir内`english_<stage>/review_queue_post_en/`へ保存し、X/Zの正式Queue[`review_queue/post_en`]には書かない)。6回全てstatus=OK | A |
| T15 | STOP/RUN_LOCK | 有料段階ごとに`tools/stop_scope_check_01.py`を実行(rc=0)。KPはscaffold内の既存`make_stop_check(stop_run_dir)`でSTOPセンチネル確認。Y専用RUN_LOCKはPhase 3 | A |
| T16 | 来歴契約 | `entry_point.json`に`chain_method=Y-TRIAL-R0-R1-R2`・module sha256を記録。U-1契約の拡張は採用判断後 | 新規(小) |
| T17 | routing/pricing | **`er006_model_routing_contract_01.py`は変更していない**(Production file)。Y moduleは既存の単価登録済みモデル(gpt-6.1-sol/gpt-6-luna)を使用し、モデル不一致は`chat()`内でProvenance違反としてSTOP。Y用キー登録は採用判断後 | 新規(小、未実施) |

## 2. segment名直書き一覧の再Grep結果(M3、Phase 3で使用する対応表)
| # | 場所(file:行) | 内容 | Y part1〜5への影響と対応 |
|---|---|---|---|
| 1 | `er003_v1_n3_01_tts_generate.py:115-118` `A2_SLOWDOWN_TARGET_SEGMENTS` | `point_one_heading, point_two_heading, full_story_part1, full_story_part2, point_one, point_two, in_one_line`(part3も無い=OPEN-466) | Std 6%減速の未適用検知の対象外(part3〜5)。Yは共有定数を直接拡張せず、Y用対象集合を渡す/X側修正後に追従。要Fable判断 |
| 2 | `er003_v1_n3_01_assemble.py:273`(`_segment_missing_mandatory_a2_slowdown`)、`:490` | 上記定数に無い名前は常に`False`(=未適用でも検知しない) | #1と同じ。parity testで「Y part1〜5の未適用を検知できる」を確認 |
| 3 | `er019_family_x_audio_production_runner_01.py:80` `_REQUIRED_FULL_STORY_SEGMENT_IDS` | part1〜3(import時の`resolve_narrative_role`整合確認用) | Y runnerは独自タプル |
| 4 | 同`:488` `_BODY_SEGMENT_NAMES`(repetition QA対象、`:1011`,`:1421`) | part1〜3 | part4/5がrepetition QAを受けない → Y用タプルを渡す |
| 5 | `er020_tts_retry_local_rewrite_01.py:105,130` `resolve_narrative_role` | part1〜3のみFULL_STORY(Zは`_c[0-9]+`パターン) | part4/5がNone → 加算のみで追加(Xへの影響なし)。Voice segmentのLocal Rewrite時は一人称保持を確認・記録(S6) |
| 6 | `er019_family_x_style_profile_01.py:201` | `"FULL_STORY": (part1, part2, part3)` | part4/5にPD06が当たらない → Y用に拡張 |
| 7 | `er019_family_x_audio_plan_01.py:259-351`(`FAMILY_X_B1/A2_SEGMENT_ORDER(_V2)`) | part1〜3+Comment4 | Y用plan新設(Comment 1→part1→Comment 2→part2〜4→Comment 3→part5→In One Line) |
| 8 | `er056_en_asr_retry_replay_01.py:46` `BODY_SEGMENTS` | part1〜3+point_one/two(ASR retry replay) | 実装時に使用範囲を確認 |
| 9 | `er003_v1_n3_01_assemble.py:363-371,792,806` ほか名前直書き | timeline/gain基準(`full_story_part1`のRMS) | Y用builder新設(T11) |
| 10 | `er019_family_x_validation_inheritance_01.py:580` | `l.startswith("full_story_part")`で動的 | 影響なし(動的) |

(`full_story_part`をGrepしたX/Z系moduleで、上記以外はtest・過去Trial・evidence runnerの参照のみ。)

## 3. Y固有の追加部分(全て新規ファイル。Production file参照0)
| ファイル | 内容 |
|---|---|
| `er110_family_y_text_trial_01.py` | 視点候補/Card schema・検証・`not_my_point`決定論生成、Y版R0 Prompt、R1/R2 Y追加、Leakage Check(日本語7+6項目、旧B承認済み項目の移植)、局所書き換え(M5: flag段落のみ・他段落byte固定・決定論検査・判定上限3・失敗時は全文書き直しへ戻さずSTOP)、Acceptance Gate、決定論モニタ(記録専用)、5段落契約確認(日本語/英語)、Comment 2/3 Y role、対策弱化アーム用Prompt(評価専用) |
| `er110_family_y_text_trial_01_run.py` | 薄い入口(prep/write/gate/english/rf/scaffold/ablation)。X共有関数の呼出のみ |
| `er110_family_y_m7_calibration_01.py`・`er110_family_y_m7_aggregate_01.py` | M7校正の実行・集計 |
| `er110_family_y_text_trial_01_test_01.py` | offline test(API 0) |

## 4. Production無変更・隔離の証拠
- `git status`: tracked `.py`の変更は**0件**(新規ファイルのみ)。本委任のcommitに含まれる既存ファイルはSSOT文書(DECISION_LOG/OPEN_ITEMS/UDR/REPORT_LEDGER)のみ。
- `er110_family_y`を参照する`.py`はY自身のfile以外に存在しない(`test_no_production_reference`で固定)。環境変数・CLI引数・flagでProductionを変える経路なし(`test_no_env_flag_or_cli_switch_in_module`)。Yは未採用であり`PRODUCTION_WIRED`ではない。
- X Prompt無変更: `USER_TMPL_Y.startswith(w1.USER_TMPL)`(test)。X Fact Lockブロックの再利用は`build_r0_block`の呼出であり複製・編集なし(test)。
- 全回帰(`run_project_regression.py`単独)の結果は`RESULT_PACKET_FYT1.md`に記載。

## 5. Opusレビュー指摘(M1〜M7・S1〜S13)の本Trialでの反映
- M1(スコープ分離・Voice数字なし)=Promptに実装、Leakage Gateとの衝突を観測(`WRITER_COMPARISON_01.md` §3)
- M2=JA・Adv・Stdで決定論確認(全PASS) / M3=一覧再Grep済み、parity testはPhase 3 / M4=Phase 3
- M5=実装・実測(3原稿とも判定2回で通過) / M6=R0最終稿に`postprocess_ja`+記号QA適用 / M7=実施(`LEAKAGE_CALIBRATION_01.md`)
- S1=Card 7項目+決定論`not_my_point` / S2=R2gで比較(差は微小) / S3=Std英語3原稿・0件 / S4=モニタ記録 / S5=RF flag件数記録 / S6=書き換え後の一人称保持を記録(保持) / S7=最終パートの締め2〜3型をPromptに / S8=R0/R1/R2全段比較(R0+R1枠は包含) / S9=Phase 3 / S10=リードに『取材』系0件 / S11=外部制約統合は使わず(必須化も禁止もしない) / S12=KP日本語意味の人称一般化moduleは既存経路で自動継承(KP 3件PASS) / S13=『です・ます』調0件

# REGRESSION_02(Part 1 T1 翻訳工程・描画有効化・X公開ページbuilder 回帰結果)

管理ID: FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_16 / 日付: 2026-10-25 / Production commit=`a9e87da40`(origin/main、rebase後。元commit `ffa7e5693`)

## 1. 新規・直接関連test
| test | 結果 |
|---|---|
| `er003_kp_source_sentence_ja_01_test_01.py`(新規) | 53 PASS |
| `er003_kp_general_explanation_01_test_01.py` | 40 PASS |
| `er003_kp_general_explanation_01_runner_integration_test_01.py`(T1追加分+旧期待値の追随) | 27 PASS(Z/X統合、M2、失敗系、5項描画、Xページ) |
| `er053_c3_audio_guard_test_01.py`/`er030_key_phrase_db_hybrid_m2_supply_01_test_01.py`/`er003_test_kp_gloss_alignment_wiring.py`(Part 1を直交扱いにするfixtureへT1のpatchを追加) | 82 PASS |
| `er054`/`er009`/`er053_cost_aggregate`(routing新key 1行の閉集合更新) | PASS(commit後。`er053_cost_aggregate`の`test_routing_addition_only`はgit HEAD比較のためcommit前はFAILが想定どおり) |
| 他agentのchunk配線(`er117_chunk_tts_production_01_test_01`/`er117_x_chunk_wiring_test_01`/`er117_z_chunk_wiring_test_01`)とのmerge後確認(origin/mainへrebaseしたworktree) | 3ファイル+上記Part 1 test 182 PASS、統合test 27 PASS |

## 2. プロジェクト全体回帰(`run_project_regression.py`、main checkout、`PYTHONUTF8=1`)
- 1回目(T1実装直後、fixture追随前): collected 7,207 / passed 7,186 / failed 6 / errors 5。自分起因=fixture 8件(`er003_test_kp_gloss_alignment_wiring`3・`er053_c3_audio_guard`4・`er030`1。いずれもPart 1を直交扱いにするpatchがT1の関数を知らないだけ)→上記のとおりpatch追加して**82 PASS**(検査の緩和なし)。残り3件=git差分比較test(`er064`/`er090`/`er053_cost_aggregate`)でcommit前は想定どおりFAIL。
- 2回目(commit後、fixture追随後、`reg3`): collected 7,207 / **passed 7,192** / failed 3 / errors 2 / skipped 10(既存)。内訳: (a)`er003_test_bad.FixtureTests.test_case_0`=`er003_test_p2k_regression_entry`が意図的に失敗させる入れ子fixture(従来から常に出力される) (b)他agentの並行commit起因=`er019_family_x_fx_20261016_wiring_01_test_01`2・`er019_family_x_new_structure_wiring_01_test_01`1・`er053_c5_review_fixes_test_01`1(実行中に`er019_family_x_audio_production_runner_01.py`が他agentのcommitで更新され`inspect.getsource`の行がずれたレース。該当4ファイルを再実行して127 PASS) (c)`er053_c2_old_checker_removal_test_01.test_dangling_residual_words_all_classified_none_orphaned`=他agent(FX-FZ-CHUNK-TTS)が追加した`er019_family_x_audio_production_runner_01.py:1382`のchunk telemetry行が未分類語に該当(私のコードではない。**他agentへの引継ぎ事項**として報告)。
- `er054_..._test_01.T.test_real_refused_without_budget`は子processの標準出力をUTF-8で読む仕様のため、環境の既定encodingにより失敗する(`PYTHONUTF8=1`で常にPASS。T1とは無関係、既存の環境依存)。
- **clean worktreeでの再現の限界**: worktree(`git worktree add`)はautocrlf変換で凍結seed[`er026_output/.../melos/seed`等]のshaが変わり、未追跡の音声資産[`er003_output/b1redesign_audio_01`]・`.env`が無いため約90件が環境起因でFAIL/ERRORする(Part 1/Z/X/chunk関連はいずれも0)。そのため全件回帰はmain checkoutで実施し、merge後の直接確認はworktreeで上記の関連testに限定した。

## 3. Dangling Reference・撤去
- 撤去した旧規則: なし(旧T1相当のコード・Promptは存在しなかった)。置換した記述: `er003_kp_general_explanation_01.py`ヘッダの「訳欄はユーザー判断待ち」コメント(今回T1承認で更新)、旧期待値test 2件(PENDING_USER_DECISION前提→PROVIDED前提)。
- Grep: `grep -n "PENDING_USER_DECISION\|WIRED_EXCEPT_USER_PAGE" er0*.py`→残存は`assemble_part1`の訳なし経路(T2/将来用の機構[条件分岐として保持。Production経路ではT1訳が常に渡る])と`TRANSLATION_PENDING`定数・`render_markdown`の`null(PENDING_USER_DECISION)`表示のみ。`WIRED_EXCEPT_USER_PAGE`はdocs(履歴)にのみ残る。

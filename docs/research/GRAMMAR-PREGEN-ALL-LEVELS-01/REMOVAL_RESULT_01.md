# REMOVAL_RESULT_01 撤去・残置の結果(GRAMMAR-PREGEN-ALL-LEVELS-01 委任_03、Charter 8)

基準: `ADV_ONLY_INVENTORY_01.md` §7、委任_03 実施事項3/6。確認日: 2026-10-27(commit `e2785c11a`+本委任の本体commit)。

## 1. 撤去したもの(Grep証跡)
| 識別子 | 場所(旧) | 置換 | 残存Grep(0件を確認) |
|---|---|---|---|
| `FAMILY_Y_PART2_ON_STANDARD_PAGE` | `er121_family_y_runner_01.py` `_verify_part2_outputs`(旧:945付近) | 各levelの節に文法ブロックがちょうど1個+節単位4者一致(`FAMILY_Y_PART2_OUTPUT_MISMATCH(<lv>)`)。Std節にPart 1が出たらSTOP | `grep -rn "PART2_ON_STANDARD_PAGE" --include=*.py .` = **0件** |
| `FAMILY_Z_PART2_ON_STANDARD_PAGE` | `er026_..._runner_01.py` `_verify_part2_outputs`(旧:1708付近) | 同上(節`adv`/`std`)。開発確認用`standard.html/advanced.html`に文法が載っていないこと(別id `FAMILY_Z_PART2_ON_DEV_DETAIL_PAGE`)は維持 | 同上 = **0件** |
| X `--stage study_text` のAdv限定`parser.error("--stage study_textはAdvanced(b1b)のみ対象です…")` | `er019_..._runner_01.py`(旧:3548付近) | `--level a2`/`both`を許容(Part 1はb1bのみ、Part 2は両level) | `grep -c "study_textはAdvanced" er019_family_x_audio_production_runner_01.py` = **0** |
| `m.LEVEL == "Advanced"` assert | `er120_part2_grammar_production_01_test_01.py::test_P5`(旧:594) | `m.LEVELS == {"b1b":"Advanced","a2":"Standard"}`(levelは必須引数) | `grep -rn "m\.LEVEL\b" er120*.py er119*.py` = **0件**(`LEVELS`は別識別子) |
| Y `if lvd["id"] == "advanced" and study_html` / Z `label == "Advanced"` のstudy_html限定 | `er121_..._runner_01.py`(旧:1113)/`er063_family_z_audio_01.py`(旧:2588) | Y: `html_by_id={"advanced","standard"}`でlevel別差込 / Z: `study_html_by_level`(キー`b1b`/`a2`) | `grep -n 'lvd\["id"\] == "advanced" and study_html\|label == "Advanced")' er121_family_y_runner_01.py er063_family_z_audio_01.py` = **0件** |
| Z `build_pages(study_html: str)` 引数 | `er063_family_z_audio_01.py` | `study_html_by_level: dict` | 呼出側(`er026` `stage_pages`・`er003_..._integration_test`)を更新済み。旧引数名での呼出 = 0件 |
| runnerの `finalize_stage(explain_call_fn=, client=, budget_guard=)` | X/Y/Z | 核のAPIがLLM引数を持たない(LLM 0 call) | `grep -n "finalize_stage(" er019*.py er121_family_y_runner_01.py er026*.py \| grep -c "explain_call_fn\|client="` = **0** |
| runnerの `p2w.*(` 呼出での `level` 欠落(暗黙のb1b既定) | X/Y/Z | 全呼出に`level=` | 同Grep(`candidate_stage/finalize_stage/require_final/verify_outputs/cand_marker/pregen_stage/public_study_html` で`level`を含まない呼出) = **0件** |
| 旧`_part2_next` の「`--regenerate-stage part2_cand_*`」を失敗時の次の一手にする案内 | Y/Z | 失敗時の次の一手=`--stage kp`(X scaffold時=同じscaffold)再実行。regenerate拒否時=revoke案内 | 統合test(`test_pregen_failure_stops_with_resume_command...`/`test_rejected_regenerate_...`)でmessage検証 |

## 2. 残置したもの(理由)
| 識別子 | 残置理由 | 確認 |
|---|---|---|
| `er120_part2_grammar_production_01.LEVEL = "Advanced"` | v1読取専用の定数(旧run互換)。新コードは参照しない(委任_02 IMPLEMENTATION_02 §5)。`er120_part2_pregen_test_01.py:311`が「残置」を固定 | `grep -rn "\.LEVEL\b" er019*.py er121_family_y_runner_01.py er026*.py er062*.py er063*.py` = 0件 |
| Part 1(Vocabulary & Expressions)のAdvanced限定(`if "b1b" in levels:` のPart 1生成/描画、X tts/assemble入口) | 今回の対象外(文法のみ。`ADV_ONLY_INVENTORY_01` S3/C10)。Stdへ広げる提案はしない | X/Y/ZのPart 1箇所は不変 |
| tts/assemble/gate入口の文法検査はAdvancedのみ | 文法はページ専用。Std(a2)のtts/gate/assembleに文法入口を付けない(委任_03禁止事項)。Stdはpages/page_verify(X: player)でのみ検査 | Yの`_assert_study_ready`はpages/page_verify/tts_b1b/gate/assemble。`_assert_std_part2_ready`はpages/page_verifyのみ(testで分離を固定) |
| 旧`run_part2`(v1 orchestrator)・`part2_b1b`等の旧stage名 | 旧run互換(legacy_postselect)。Adv名は不変 | 核のtest(T3)で固定 |
| `er019_nws2_final_page_01.py`(公開済みX記事のpage script) | 履歴。書換え禁止(委任_03)。Part 1のみを描画しており`public_study_html`を呼ばない | 無編集 |
| `er121_family_y_runner_01.py` `PART2_CAND_STAGE/PART2_FINAL_STAGE` | Advancedの名前(既存test・参照用)。level別は`PART2_STAGES[lv]` | `PART2_STAGES`と`p2w.stage_names`の一致をtestで確認 |

## 3. 切り分け(本委任と無関係の既存失敗)
- `er019_x_std_chunk_opus_test_01.R4HunkClassifierTest`: `git diff bb578265c`のhunk分類が**HEADでも失敗**(UNCLASSIFIED: er019=1, er121_family_y_audio=3, er121_family_y_structure ほか)。本委任でer019のUNCLASSIFIEDが増える(Part 2のhunk。TTS/Chunk処理ではない)。分類toolの許可リスト更新はChunk TTS側(OPEN-543系)の所有のためFableへ報告。
- `er121_family_y_structure_match_test_01.NoticeDisplay::test_no_xz_page_in_repo_contains_the_y_notice`: KCP3 evidenceの`docs/research/KP-CONFIRMED-CONTENT-PROTECTION-01/evidence_runs/y2/_bak_index.html`(Y注意書きを含むbackupページ)を検出。本委任と無関係(KCP evidence側の整理)。
- `er003_..._integration_test::ZPart1Tests::test_kp_expression_change_needs_two_step_regeneration_with_hints`: テストがKP artifactを確定後に書換え -> 確定内容保護G0(`CONFIRMED_CONTENT_INTEGRITY_VIOLATION`)が `finalize_kp` で止める(KCPの設計どおり)。Part 2無関係。

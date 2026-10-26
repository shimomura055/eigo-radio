# FIX_01 — 実装差分要約・test結果(X/Y Standard へ Chunk分割+0.2秒を配線。Z Stdは設計のみ)

管理ID: CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_01(2026-10-26)。基準HEAD=`bb578265c`(実装前に`git rev-parse HEAD`で記録)。API 0・外部接続試行は新規testで0。**到達Status: X/Y Std=IMPLEMENTED_PENDING_EVIDENCE、Z Std=DESIGN_READY。PRODUCTION_WIREDではない(正式runtime evidence未取得)。**

## 1. 差分(Production code)
| ファイル | 変更 |
|---|---|
| `er117_chunk_tts_production_01.py` | **plannerは無変更**(`plan_x_part(s)`・`plan_z_clip`・`CHUNK_PLANNER_VERSION`不変)。追加のみ: 定数`STD_LEVEL`/`STD_SLOWDOWN_COMPOSITION`/`STD_SLOWDOWN_RATIO_MIN,MAX`、`attach_chunk_meta(level=None)`(Std時のみ`level`/`std_slowdown_composition`)、`std_chunk_slowdown_violations`、`std_parent_slowdown_fields`、`drop_cached_std_chunks_without_slowdown(is_chunk_id)`、`evidence_record`のStd項目(entryに`slowdown_applied`がある場合のみ) |
| `er019_family_x_audio_production_runner_01.py` | X Std: `generate_family_x_a2_segments`に chunk plan/`reconcile_saved_plan(chunk_plan_a2.json)`/stale・減速証跡なしcache拒否/`_generate_x_body_part_chunked_a2`(chunkごとに`n3_tts.generate_a2_segment_with_slowdown`)/親集約(`_refresh_x_chunk_parents(level="a2")`)/`chunk_tts_evidence_a2.json`。`load_family_x_a2_sources`(整合検査+`verify_raw_parent`)、`apply_family_x_a2_gain`(chunk別gain+0.2秒)、`stage_assemble_family_x_a2`(親refresh+`_x_std_chunk_slowdown_blocked`+`chunk_tts_assembly_a2.json`)。`validate_only_segments_args`のa2 `_k`拒否(旧I5)を撤去。**Adv関数(`generate_family_x_b1_segments`等)のソースには触れていない** |
| `er121_family_y_structure_01.py` | `CHUNK_TTS_Y_LEVELS=("b1b","a2")`、承認参照・注記を更新 |
| `er121_family_y_audio_01.py` | Y Std: `generate_y_a2_segments`に chunk plan/cache拒否/`_generate_y_body_segment_chunked_a2`/親refresh(level="a2")/`chunk_tts_evidence_a2.json`。`check_std_slowdown(results, plans)`をchunk対応、`load_y_sources`のa2に`_load_y_body_chunks`、`assemble_level`のrefresh・summaryファイル名をlevel別、`_record_chunk_decision`のa2非適用分岐を撤去、`validate_only_segments`のa2 `_k`拒否を撤去。**試聴ページ表示**: `_tts_unit_badge`/`page_legend_html`の『Standardの本文は分割対象外/仕様上、分割しません』(利用者に見える誤記)を判定記録(`chunk_tts_decision.json`)に従う表示へ是正(2026-10-26以前の旧Std記録は『旧記録』と明示) |
| 共有module | **無編集**(`er003_v1_n3_01_assemble.py`・`er003_v1_n3_01_tts_generate.py`・`er020`・`er063`) |

## 2. test
| 区分 | ファイル | 結果 |
|---|---|---|
| 新規 | `er117_std_chunk_wiring_test_01.py`(17: Adv golden一致・attach_chunk_meta不変・合成物理[実ffmpeg]・Std証跡検査) | 17 PASS |
| 新規 | `er019_x_std_chunk_test_01.py`(18: X Std生成kwargs・親集約・親wav=減速後chunk+正確に4800サンプル・共有Gate・追加Gate・人間承認で迂回不可・失敗継続・resume・再計画禁止・only-segments・単一段落不発火・legacy・gain・assemble BLOCK) | 18 PASS |
| 新規 | `er121_family_y_std_chunk_test_01.py`(14: Y Std範囲・実記事不発火・複数段落発火・Voice・Gate chunk検査・組立gap0.2秒・減速欠落BLOCK・resume・再計画・改ざん停止・隔離) | 14 PASS |
| 書換え | `er117_x_chunk_wiring_test_01.py`(旧『Std非chunk固定』→『Stdにchunk経路あり』、a2の`_k`受理) / `er121_family_y_audio_chunk_test_01.py`(a2非chunk固定→両level適用) / `er121_family_y_structure_match_test_01.py`(許可リスト1行) / `er121_family_y_page_pause_test_01.py`(Stdバッジの旧『分割対象外』assertを判定記録準拠へ) | PASS |

### 回帰(遮断harness下 `PYTHONPATH=netblock_harness_01`、`.venv\Scripts\python.exe run_project_regression.py --pattern …`。`system python`には`google.genai`が無いため`.venv`を使用)
| pattern | 変更前(in-place、実装着手前) | 変更後(serial) | 判定 |
|---|---|---|---|
| `er117*_test_*.py` | 89 collected / 89 pass | 106 / 106 pass(+17新規) | 回帰なし |
| `er019*_test_*.py` | 560 / 560 pass | 578 / 578 pass(+18新規) | 回帰なし |
| `er121*_test_*.py` | 277 / 276 pass, 1 skip | 291 / 290 pass, 1 skip(+14新規) | 回帰なし(skipは変更前から) |
- 注: 並行Agent(FZ)のuncommitted差分(`er003_v1_n3_01_tts_generate.py`等)が一時的に作業ツリーにあり、`er019_family_x_pointless_01_test_01::FamilyAUnchangedTest`(Family Aファイルの作業ツリー差分検出)が1回だけFAILした(`M er003_v1_n3_01_tts_generate.py`、本委任は編集していない)。並行Agentのcommit後は578/578 PASS。I10(clean worktree)に倣い`git worktree`でHEADの回帰も試みたが、worktreeには未追跡成果物が無くenvironment差でFAIL/ERROR(er019 5件・er121 12件)となり基準に使えないため、変更前基準は『実装着手前のin-place実測』を採用した(同worktreeは削除済み)。
- 接続試行: 遮断harness(`NETBLOCK_LOG`)のログ。er117=0、er121=0、er019=129件(`api.openai.com` getaddrinfoのみ、**全て遮断**)。内訳は既存のstyle_profile 66・integration 45・s3_wiring 12・variable_role_style 6で、**変更前も同数129**(新規testは0)。初回の変更後実行では新規X Std testが51件の接続を試みた(他testが残したPNAP=ONの状態で実体表構築[OpenAI NER]に入る)ため、Rigで`pnap.is_enabled`を明示OFFにして0にした。実OpenAI/Geminiへの到達は0(全て遮断)。

## 3. 確認事項
- 既定値/flag: 新機能に別flagは無い(Advと同じく常時有効。承認済みAPPROVED_FOR_PRODUCTION範囲=Std/Adv双方の配線)。Production到達経路に入る未承認機能は無い(Z Stdは未配線)。
- Adv不変: goldenバイト一致(X 2 run・Y 2 run)、`attach_chunk_meta`/`evidence_record`のAdv出力不変、Adv生成関数のソース不変(grepで`_generate_x_body_part_chunked_a2`/`chunk_plan_a2`/`drop_cached_std…`が含まれない)。Z: `git diff -- er063…` に本委任由来の差分0。
- 旧規則の撤去・残置(Grep): `a2.*_k.*b1b のみ`(旧I5文言)=撤去済み。残置: Z Stdの除外(`er117:plan_z_clip`の`level!="b1b"`、`er063:598`)=次委任で撤去、その固定test(`er117_z_chunk_wiring_test_01.py:130-132,202`)=維持。
- 既知の制限(変更なし・記録のみ): Opus I11 `validation_inheritance.derive_expected_texts`(手動CLI)はchunk labelを導出できない(Adv同様。Stdも同じ)。

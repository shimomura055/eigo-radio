# OPEN-129-AUDIO-GATE-STRUCTURAL-COMPLETENESS-PRODUCTION-WIRING-01

管理ID: OPEN-129-AUDIO-GATE-STRUCTURAL-COMPLETENESS-PRODUCTION-WIRING-01
(Lane B、Sonnet委任、Production Wiring)。

対象: ユーザー決定(2026-09-09、`APPROVED_FOR_PRODUCTION`)に基づき、案(a)
(family+level複合キーでrequired_segmentsを定義し、Audio Gate側で正式構造と
実Assemblyを突合、`OPEN-129-AUDIO-GATE-STRUCTURAL-COMPLETENESS-TRIAL-
01_REPORT.md`と同一ロジック)を、共有Audio Validation Gate
(`er003_v1_n3_01_assemble.py::verify_episode_audio_validation_gate()`)へ
**opt-in(既定OFF)**として配線した。**mandatory化はしていない**。

---

## 1. 実装(正本は生成側、Gate側は参照のみ)

| ファイル | 変更内容 |
|---|---|
| `er003_v1_n3_01_assemble.py` | `verify_episode_audio_validation_gate(out_dir, level, required_structure: dict \| None = None)`(既定`None`=OFF、既存3箇所の呼び出し元は無変更のまま)。`_check_structural_completeness(data, required_structure)`(missing/voice_mismatch/extra segment/key phrase missing・incomplete・extraを検知、reorderは対象外)。A-Family用正本`derive_a_family_required_structure(level)`・`A_FAMILY_A2_REQUIRED_SEGMENTS`・`A_FAMILY_B1_REQUIRED_SEGMENTS`を新規追加(既存関数は無変更) |
| `er012_b_family_editorial_type_registry_01.py` | `B_FAMILY_B1_REQUIRED_SEGMENTS`(新規、B1用正本)・`B_FAMILY_A2_CONFIG`へ`key_phrase_ranks`/`key_phrase_subkey_count`追加(既存`required_segments`は無変更)・`build_required_structure(level, voice_a, voice_b)`(role文字列→実voice名解決、Gate引数へそのまま渡せる辞書を返す) |

Gate側(`verify_episode_audio_validation_gate`)は`required_structure`を
受け取って検証するだけで、required_segmentsという別の正本を持たない
(生成側=registry/derive_a_family_required_structureのみが正本)。

既存呼び出し元(`asm.load_b1_sources`・`asm.load_a2_sources`・`a2prod.
load_a2_sources_for_b_family`)は**1行も変更していない**(引数省略のまま、
既定OFF)。opt-in ONでの検証は、Gate関数自体を直接呼び出す評価スクリプトで
実施した(4節)。mandatory化(全productionコールサイトへの自動適用)は
今回実装していない。

## 2. Key Phrase sub-key命名のschema drift対応

Trial-01が発見した命名drift(`english/japanese_meaning` vs `english/
japanese` vs `en/ja_charon`)は、名称を統一せず、**rank毎のsub-entry件数
のみで判定する**設計を踏襲した(`_check_structural_completeness`内、
`key_phrase_subkey_count`件数比較のみ、sub-keyの実際の名称は一切参照
しない)。これにより既存出力の読み込み互換を保ったまま、命名drift由来の
false rejectを構造的に回避した(単独の大規模リネームは行っていない)。

## 3. Gate 3必須確認(ユーザー指定項目)

| # | 項目 | 結果 |
|---|---|---|
| 1 | Production正式pathに実装 | PASS(`er003_v1_n3_01_assemble.py`本体、Trialの並行実装ではない) |
| 2 | Trial専用checkで終わっていない | PASS(実Gate関数へ引数追加。4節の評価は実Gate関数を直接呼び出して実施) |
| 3 | A-Family A2・B1、B-Family A2・B1のfamily+level構造差を正しく扱う | PASS(4種類の`required_structure`が全て異なる。同一`level="B1"`でもA-Family[13segment・tension無し]とB-Family[14segment・tension有り]で別正本、単体テスト`test_b_family_b1_vs_a_family_b1_differ_despite_same_level_string`で明示確認) |
| 4 | delete検知 | PASS(4節、12/12中4/4) |
| 5 | voice_swap検知 | PASS(4節、4/4) |
| 6 | extra segment検知 | PASS(4節、4/4) |
| 7 | 正常episode false rejectなし | PASS(4節、既存完成episode12/12。1件[free_address_02]はTrial-01で確認済みの既知true positive[未完成中間iteration]、false rejectではない) |
| 8 | reorderの扱いが仕様どおり | PASS(dict lookup方式のため順序は検証対象外。「segmentの順序はtimeline builderが別途保証し、完全性チェックの検知対象外」と設計どおり明記、4節で8/8非検知確認) |
| 9 | 既存完成episode再検証 | PASS(4節、13件) |
| 10 | B-Family 3V/4V拡張可能性を壊していない | PASS(`_ROLE_TO_VOICE_RESOLVERS`は role文字列ベースの辞書解決方式であり、`voice_c`/`voice_d`エントリを追加するだけで3V/4Vへ拡張できる設計。3V/4V本体作業は今回実施せず[禁止事項どおり]) |
| 11 | retry・fallback・regenerationとの整合 | PASS(5節) |
| 12 | `CURRENT_SPEC.md` | 反映(Part 3) |
| 13 | `DECISION_LOG.md` | 反映(Part 3) |
| 14 | `OPEN_ITEMS.md` | 反映、PRODUCTION_WIRED候補+commit hash、mandatory化は別判断と明記(Part 3) |
| 15 | Git / Dangling Reference / runtime evidence | 反映(下記6節・4節) |

## 4. Runtime evidence

`er011_open129_structural_completeness_production_wiring_evidence_01.py`
(root)が、**実際の`asm.verify_episode_audio_validation_gate()`**(Trial側
の並行実装ではない)を直接呼び出して実施した。費用¥0(TTS/LLM呼び出し
なし)。

**(a) 既存完成episode全件の再検証(false reject確認)**: 13件
(A-Family A2×4・A-Family B1×4・B-Family B1×1・B-Family A2×4)の実
`out_dir`へ、`required_structure=None`(OFF、既存呼び出しと同一)と
`required_structure=<registry/derive_a_family_required_structure()の
出力>`(ON)の両方を実行し比較した。

- OFF結果は本タスク以前と同一(既存3箇所の呼び出し元を1行も変えていない
  ため自明。実測でも既存BLOCKED/PASSの内訳は変化なし)。
- ON時のfalse reject(定義: OFFではPASSしていたのにONでのみBLOCKEDに
  なった件数)は**13件中1件のみ**で、その1件(`editorial_b_voices_a2_
  free_address_02`、`japanese_title`欠落)はTrial-01で確認済みの既知
  true positive(`_02`は`_03`で追加される前の中間iteration、実際に未完成。
  `_03`以降は同segmentが存在)であり、false rejectではない。**最終・
  完成episode12/12でfalse reject 0**。詳細:
  `er011_output/open129_production_wiring_evidence_01/false_reject_
  sweep.json`。

**(b) 4経路×5ケースの検知reproduction**: A_FAMILY_A2/A_FAMILY_B1/
B_FAMILY_B1/B_FAMILY_A2の代表episodeを一時コピーし(実ファイル無変更)、
baseline/delete_segment/voice_swap/reorder/extra_segmentの5ケースを実
Gate関数(`required_structure`指定)へ通した。

| ケース | 期待 | 実測(4経路とも) |
|---|---|---|
| baseline | 非検知 | 非検知(4/4一致) |
| delete_segment | 検知 | 検知(4/4) |
| voice_swap | 検知 | 検知(4/4) |
| reorder | 非検知(negative control) | 非検知(4/4一致) |
| extra_segment | 検知 | 検知(4/4) |

**検知率(delete/voice_swap/extra、Trial-01と同じ定義)= 12/12**。
期待一致(match_expected)= **20/20**。詳細:
`er011_output/open129_production_wiring_evidence_01/reproduction_
results.json`。

## 5. retry/fallback/regenerationとの整合

- A2: `finalize_tts_results_a2()`は承認済みbyte再利用(`A2_SEGMENTS_TO_
  REUSE`固定tuple)+新規TTS(`point_one`/`point_two`)のmergeで、常に
  registry正本と同一のsegment名集合を再構成する(単体テスト
  `test_a2_reused_plus_new_segments_equals_required_structure_names`で
  集合一致を確認)。再生成(retry)してもこの集合自体は変わらない。
- B1: `run_tts()`が生成するsegment名は常に固定(14種類)であり、
  registry`B_FAMILY_B1_REQUIRED_SEGMENTS`の名前集合と一致する。
- 既存のLane B runner側完全性チェック(`a2prod.check_required_segments_
  completeness()`、Gate統合とは別物、無変更)が、本タスクで追加した
  registry新規キー(`key_phrase_ranks`等)によって壊れていないことを単体
  テストで確認した。

## 6. Gate 4(Dangling Reference Check)・Regression

- Gate側は`required_structure`引数を受け取るだけで、独自の正本(別の
  required_segments定義)を一切持たない(1節参照、重複正本なし)。
- 新規テスト`er011_open129_structural_completeness_production_wiring_
  01_test_01.py`(15テスト、全PASS): 構造導出・既定OFF不変・opt-in時の
  5パターン検知/非検知・Key Phrase欠落検知・retry整合。
- `run_project_regression.py`: collected=2242, passed=2239, failed=3
  (失敗3件は`er003_test_p2j_investigate.py`のテスト総数reconciliation
  drift、詳細はOPEN-131 Report 5節と同一理由、機能的回帰ではない)。

## 7. mandatory化について

**今回はopt-in導入のみ**。全productionコールサイト(`load_b1_sources`/
`load_a2_sources`/`load_a2_sources_for_b_family`)への自動適用は行って
いない。mandatory化はB-Family 3V/4V Trialと次回A-Family Production run
の実績後に別途ユーザー判断(`USER_DECISION_REQUIRED`)とする。

## 8. STOP条件確認

該当なし(既定OFFで既存出力不変[13件のうち12件OFF/ON同一結果、1件は
既知true positive]・regression機能的break無し・既存完成episodeでの
false reject無し・mandatory化なし・費用¥0・承認内容[案(a)]と実装が
一致)。

## 9. Status

`PRODUCTION_WIRED候補(Fable受入待ち)`。mandatory化は別判断のまま。

## 新規ファイル一覧

- `OPEN-129-AUDIO-GATE-STRUCTURAL-COMPLETENESS-PRODUCTION-WIRING-01_REPORT.md`(本ファイル、root)
- `er011_open129_structural_completeness_production_wiring_01_test_01.py`(root、regression test)
- `er011_open129_structural_completeness_production_wiring_evidence_01.py`(root、runtime evidence script)
- `er011_output/open129_production_wiring_evidence_01/`(false_reject_sweep.json、reproduction_results.json)

---
Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SPsKBAZP5KEqdTH9TnkJdp

# IMPLEMENTATION_01 — Y runner Style profile配線是正(OPEN-537) 実装記録

管理ID: FAMILY-Y-STYLE-PROFILE-FIX-01 委任_02 / commit 3af84a499(委任_02a) / API 0。設計=DESIGN_01.md+DESIGN_02.md(差分)。

## 1. 変更ファイル
| ファイル | 内容 |
|---|---|
| `er121_family_y_audio_01.py` | `Y_APPROVED_STYLE_PROFILE="fx_20261017"`(単一ソース)・`Y_ROLE_COVERAGE`・`y_expected_coverage`・`_y_profile_assert`・`y_style_gate`をfail-closedへ全面改修・`generate_y_b1/a2_segments`の`style_profile`を既定値なしの必須キーワード引数へ |
| `er121_family_y_runner_01.py` | 旧`STYLE_PROFILE="default"`撤去、`YContext.style_profile/style_profile_source`、`resolve_style_profile`(課金前・X方式)、`_style_profile`(stage入口の再検証)、`_tts_input_sha`/生成/Gate/組立へ透過、`gate_summary.json`に`y_profile_blocked`/`coverage`、統合照合表`audit/style_actual_vs_approved.json` |
| `er121_family_y_mock_01.py` | 偽TTSが送信Style(`style_prefix_override`)を記録、偽KPがK2 Store key・profile記録を付ける(本物と同じ形) |
| `er121_family_y_style_profile_test_01.py`(新規, 37件) | drift/静的配線(AST)/runner解決/Gate fail-closed/送信Style実測/横断登録表(R-7) |
| 既存test 6本 | `r.STYLE_PROFILE`→`ya.Y_APPROVED_STYLE_PROFILE`(audio_chunk/hr_approval_guard/multiparagraph_regression/runner_01/std_chunk/std_chunk_opus)。`y_style_gate(..., "default")`を呼んでいた2箇所は承認profileへ |

## 2. Gate契約(`y_style_gate(theme_out_dir, level, style_profile)`)
1. 固定記録`audit/style_profile.json`: 欠落`Y_STYLE_PROFILE_RECORD_MISSING`/破損`..._UNREADABLE`/sha不一致`..._RECORD_MISMATCH`/承認profile以外`Y_STYLE_PROFILE_NOT_APPROVED`/引数と記録の食い違い`..._ARG_DISAGREES_WITH_RECORD`/role表drift`Y_STYLE_ROLE_TABLE_DRIFT` → 評価に進まずBLOCK(`y_profile_blocked`)。legacy waiverなし。
2. 本文8segment(chunk化は全chunk)+日本語補助(Std preview/comment_1〜3)+Preview(Adv)+KP英語3+KP日本語意味3(Std)+KP解説3(Adv)を検査。Adv=15件、Std=18件。
3. 網羅: `Y_ROLE_COVERAGE`の期待集合と『evaluate_segment_evidenceを実行した集合』が完全一致であること(不足`Y_STYLE_COVERAGE_EMPTY`/期待外`Y_STYLE_COVERAGE_UNEXPECTED`)。Opus M-1の再現test(Y本文0件でもx_gate.checkedは非空→BLOCK)あり。
4. 日本語role: top-level `style_prefix`(送信instruction)のsha256を承認shaと照合(`JA_STYLE_ACTUAL_MISMATCH`)。取れない場合`JA_STYLE_ACTUAL_UNMEASURED`+照合表は`意図sha(実測なし)`/`match=false`。
5. 既存規則は不変: Adv `ADV_STYLE_PREFIX_NOT_PROFILE_PREFIXED`/`ADV_MINIMAL_FALLBACK`、Std `STD_FALLBACK_USED_OR_UNKNOWN`・減速必須、`LOCAL_REWRITE_RECOVERY`、HR承認(`name_not_approved`)、OPEN-535 reconcile。
6. 出力: `{level}/audit/y_style_profile_gate.json`、`{level}/audit/style_actual_vs_approved.json`(1行ずつ: role・segment・承認sha・実測sha・実測方法・voice・model・fallback・減速・match=『Style一致かつGate違反なし』)、統合`audit/style_actual_vs_approved.json`。

## 3. test結果(実測)
- 新規`er121_family_y_style_profile_test_01.py`: 37件OK。
- `run_project_regression.py --pattern "er121*_test_*.py"`: 実装前(HEAD)=330件(329 pass/1 skip)、実装後=367件(366 pass/1 skip、failed 0/errors 0)。
- `er063*`=130 pass、`er011*`=292 pass。`er019*`=595件中592 pass・3 fail(いずれも本変更と無関係。下記)。
- CRLF test: 委任文の「`TestPlannerBoundary`がCRLFで赤」はHEADで再現せず。`er121_family_y_multiparagraph_regression_test_01.py`は7/7 PASS(unittest・pytest[PYTHONPATH=netblock_harness_01]とも)。test/planner変更なし。
- er019の3 fail(区別): (a) `er019_x_std_chunk_opus_test_01 ...R4HunkClassifier...`=既知R4赤、(b) `er019_family_x_pointless_01_test_01 ...FamilyAUnchangedTest`=`er003_v1_n3_01_tts_generate.py`の未commit差分(並行Agent TTS-RETRY-FALLBACK-LR-UNIFICATION)による、(c) `er019_family_x_fx_20261016_wiring_01_test_01 ...test_fallback_used_consumers_do_not_read_kp_english_entries`=`er003_v1_crosslevel_audio_02_common.py`の未commit差分(同並行Agent、173行追加)が`fallback_used`の読取者に増えたため。er121は許可リストに既に含まれており、本変更で読取者ファイルは増えていない。

## 4. Grep(撤去・残置)
- `STYLE_PROFILE`(単独識別子)の残存: er121_*.pyの非test 0件(runner冒頭のコメントのみ)。`"default"`リテラル: er121_family_y_*.pyの実行コード 0件(AST testで固定)。`migrate_record`: runnerのdocstringに禁止注記のみ(AST testが呼出0を固定)。
- 意図的残置: Xの`PROFILE_DEFAULT`/`resolve_role_style`のdefault素通し/`m3_assembly_gate`のdefault分岐(R-8。X/Z/legacy用、不変)。
- 旧Trial driverの参照(AttributeErrorで検出される=撤去設計どおり。履歴scriptのため改変しない): `docs/research/CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01/tools/{adv_invariance_driver_01,y_chunk_evidence_driver_01}.py`、`FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01/tools/yfb_voice1_candidates_01.py`、`FAMILY-Y-VOICE1-MALE7-TRIAL-01/tools/ym7_generate_01.py`、`FAMILY-Y-VOICE1-PAUSE-CAUSE-TRIAL-01/tools/yvp_cross_generate_01.py`。

## 5. 影響する運用上の注意
- 既存run(`run_01`、`run_voice_puck_ev_01`、`sns_age_limit/run_01`等、固定記録なし+run stateあり)は、runner起動時にM2で課金前STOPする(新規runは`resolve_run_profile`が承認profileを固定記録)。旧runの再pagesは不要(M-2)。必要になった場合は新out_dirへ入力を複製する。
- Production経路に入る未承認機能: なし(承認済みprofile fx_20261017の配線是正のみ。新flag・新Style・新Promptなし)。

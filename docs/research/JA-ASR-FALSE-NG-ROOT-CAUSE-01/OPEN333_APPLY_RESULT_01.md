# OPEN333_APPLY_RESULT_01(OPEN-333 E3 のProduction適用結果。JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_12、2026-10-25)
**区分: 承認済み不具合是正(PM_GOVERNANCE 11-8)であり、新しい合格条件の導入ではない。** Status=**APPLIED(Production適用済み・初回run集計待ち)**。`VALIDATED→Production採用`の新仕様採用ではない。API 0・有料run 0・実費0円。P-1(助詞は→わ免除)は未実装(ユーザー判断)。E4は未適用(Fable判断待ち)。設計=`OPEN333_DESIGN_02.md`、評価=`OPEN333_EVAL_02.md`。
## 1. 変更一覧(Production差分)
| file | 内容 |
|---|---|
| `er011_ja_asr_variant_layer_01.py`(+87) | rollback定数`CANDIDATE_E_FULL_DIFF_CHECK`/`CANDIDATE_E_VALUE_GUARD_CHECK`(既定True)、`_mask_value_spans`(値ガードatom span→placeholder)、`_candidate_e_number_entry_rejections`(数値entryのみ。非数値差の全件再検査+値ガード多層防御、fail-closed)、Candidate E分岐に拒否時`protected.candidate_e_rejections`記録+`return None`。コメント更新(E分岐の前提) |
| `er007_ja_asr_validator_01.py`(+10、コメントのみ) | 数字不一致経路のコメント(『誤PASSのリスクを生まない』)に、Candidate E追加後の検査漏れとE3での是正を注記 |
| `er007_ja_secondary_asr_01.py`(+5) | adapterが`protected.candidate_e_rejections`を`asr_judgement.candidate_e_full_diff`へ複写(M-6。判定不変、拒否が無ければfield無し) |
| test | 新規`er011_ja_asr_variant_layer_candidate_e_full_diff_test_01.py` 27件+`er078_asr_value_guard_kana_unify_test_01.py`に1件追加。既存更新(前提変更のため最小): `er078_asr_r5_measurement_test_01.py`の2件と`er078_asr_value_guard_kana_unify_test_01.py::test_candidate_e_phonetic_match_value_diff_blocked_via_adapter`は、『Candidate E由来のREADING_MATCH PASSを最終Gate[F1]が拒否する』記録/判定の固定が目的で、E3が同じpairを先に拒否するようになったため、E3のrollback定数をFalseにして最終Gate単体を検査する形へ(E3有効時の同pair=NG_PROTECTED/p1_value_diffは新testで固定) |
| docs/research | `proto_open333_fix_04.py`(E3v3)・`proto_open333_fix_05.py`(E4)・`sweep_cases_open333_02.py`・`sweep_cases_open333_e4_01.py`・`eval_open333_api0_04.py`・`eval_open333_prod_parity_01.py`・`open333_runtime_fire_01.py`・`open333_first_run_tally_01.py` と各出力、`OPEN333_PREREGISTERED_02.md`/`DESIGN_02`/`EVAL_02`/本書、`OPUS_REVIEW_01_OPEN333.md` |
protoを Production から import していない(M-4)。Production→Trial importなし(Grep)。
## 2. 既存仕様整合・既定値
- 照合: `er007_ja_asr_validator_01.py:258-261, 366-386`(数字差のcontinue・OPEN-145承認コメント)、`er011_ja_asr_variant_layer_01.py:347-372`(Candidate E)、`er007_ja_secondary_asr_01.py:83,644`(SCG_PASS_CLASSIFICATIONS・Secondary受理)、`er078_asr_unified_judge_01.py:362-373`(最終Gateの`_protected`=F2付き値ガード。R-6の多層防御はこれと同じ`value_guard_kana_unified`を使用)、`CURRENT_SPEC.md:2196`(Variant Layer節。追記済み)、DECISION_LOG:10208-10300(R-1)。
- 既定値Grep: `CANDIDATE_E_FULL_DIFF_CHECK = True` / `CANDIDATE_E_VALUE_GUARD_CHECK = True`。env/flag/引数/起動scriptで切替なし(test `test_constants_not_read_from_env_or_args`で関数ソースに`environ`/`getenv`が無いことを固定)。承認済み不具合是正のためflag化・Default Off隔離は不要(11-7の適用外=新仕様ではない)。
- 既存のretry/fallback/Gate: 拒否は既存の`TRUE_CONTENT_MISMATCH`(retry対象、unified judgeのP1/P2/P3)へ落ちるのみ。Gate・上限回数・resume/HR Lockは無変更。E3は『Eが得ていたPASS』を狭める方向のみ。
## 3. 一致検証・API 0再評価
| 項目 | 結果 |
|---|---|
| proto E3V ↔ Production(既定ON)(`eval_open333_prod_parity_01.py`。2,716キー=Primary段classify+正式adapter state/reason/label 1,442 + Secondary受理sim 1,274) | **差分0** |
| Production(定数OFF) ↔ git HEAD | **差分0**(OFF=HEAD完全一致) |
| Production(ON) vs HEAD の変化 | 104キー、**NG→PASS(広がり)0**(変化はE経由PASSの縮小とSecondary classificationラベルの変化[受理不変]) |
| 実データ1,327行(`OPEN333_EVAL_02.md`) | N3-07遮断、非PASS→PASS 0、負例以外のPASS→非PASS 1/677(月題#1) |
## 4. 回帰(ネットワーク遮断harness`netblock_harness_01`+`.venv`)
- 対象43 file(er007 JA系・er066・er078全test・static audit・er109・er011 JA/KP/repetition系・er009/er025/er038の該当): **1,064 passed / 8 failed**(最終状態)。
- 8件は全て本変更と無関係の既存失敗: er007_ja_secondary_asr_01_test 2件(`test_koro_kanji…`/`test_single_engine…`。HEADスナップショットでも同名で失敗)、er109_wiring_golden 3件・er109_xz_isolation 2件(07A結果でHEADのみのworktreeでも失敗と記録済み。HEADスナップショットでxz_isolationの2件は同名で失敗を再確認)、`er078_asr_unified_wiring_static_audit_01.py::test_asr_call_inventory_matches_allowlist`(er103/er104/er019の未登録ASR呼出点。HEADスナップショットでも失敗=別agent変更起因)。
- 当初の失敗11件のうち3件(r5 measurement 2、kana_unify 1)は上記のとおり前提変更に合わせてtestを更新し解消。
- XYZ共通経路とYの配線漏れ確認(`er078_asr_unified_wiring_static_audit_01`のうちinventory以外=全PASS)。外部接続: harnessログで`api.openai.com`への試行12件(全て遮断、到達0)は既存失敗testの`er109_*`/`er007_ja_secondary_*`由来(個別実行で再現、新規testと評価scriptは0件)。
## 5. runtime発火確認(API 0、`open333_runtime_fire_01.py`、出力`open333_runtime_fire_01.out.txt/.json`)
保存転写1,327行を**正式adapter**(`evaluate_attempt_ja_with_cascade_detail`、Azureはstub・socket guard)へ注入:
| | E経由PASS(Primary) | E3拒否が発火したattempt(拒否pair計) |
|---|---|---|
| ON(既定) | 21 | **5(8 pair)**: N3-07・MOON#1(`しわ`↔`詩は`)・MOON#2・N3-02・N1-er066b-020(`三日目`↔`3日間`) |
| OFF(rollback定数False) | 23 | 0 |
(`azure_real_calls`=399はstubの呼出回数。実Azure呼出0。)有料Trialはしていない。正式runでの発火は未取得: `open333_first_run_tally_01.py <run_dir>`で集計する。
## 6. 適用後の監視・rollback手順
- 監視: 適用後の正式runごとに`PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/open333_first_run_tally_01.py <run_dir>`。拒否(`candidate_e_full_diff`)が1runで3件超ならFableへ報告(自動rollbackはしない)。
- rollback: `er011_ja_asr_variant_layer_01.py`の`CANDIDATE_E_FULL_DIFF_CHECK = False`(再検査)・`CANDIDATE_E_VALUE_GUARD_CHECK = False`(多層防御)。または適用commitの`git revert`。
## 7. リスク(隠さない)
- 再生成増: 負例以外の現行PASSの0.148%(1/677、月題#1のみ)。数値entryで『カタカナ等価表記[ヴェ↔ベ等]+数値表記差』が重なる正常音声は再生成になり得る(合成で25件中24件。実データ0。E4-N案で整合化可能)。
- 値と認識されない単位(℃・km・〇/零)・片側のみ認識される助数詞(七晩↔七番)は非数値残余として拒否され得る(将来Eに到達する形になった場合)。
- 実運用での頻度は未取得(正式run集計待ち)。

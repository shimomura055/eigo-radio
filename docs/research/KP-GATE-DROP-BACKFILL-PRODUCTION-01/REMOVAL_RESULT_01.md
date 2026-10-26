# REMOVAL_RESULT_01: 撤去・残置した規則と残存Grep(KP-GATE-DROP-BACKFILL-PRODUCTION-01 委任_02、2026-10-26)

## 1. 撤去したもの(補完ON=既定のときだけ。flag `EIGO_KP_BACKFILL=0`で完全復帰)
| 識別子 | 内容 | 撤去前 | 撤去後 |
|---|---|---|---|
| 外側retry `gate_dropped`脚(M-2) | `n_auto<3 and gate_dropped`で候補list全体を再生成・置換 | `er119_kp_candidates_01.py`(commit `cbcd29d27`時点):376 `if n_auto < rv.KP_FINAL_MAX and (gate_dropped or rescued_not_auto) and not last:` | `:403` `if (not backfill_on) and n_auto < rv.KP_FINAL_MAX and (gate_dropped or rescued_not_auto) and not last:` |
| 外側retry `rescued_not_auto`脚(M-3) | 救済済みでauto不可の候補があれば全件再生成 | 同上 | 同上(同一条件式のON時の無効化) |
| 代替 | 除外分は`_run_backfill`(1回・末尾追加・初回候補保持) | - | `er119_kp_candidates_01.py` `_run_backfill`(配線: ai_rank付番後・Redundancy QA前) |

## 2. 残置したもの(理由)
- 外側retry自体: 候補0件(`not cands`)・call1/call2失敗・live 0・canonicalization全体失敗(技術失敗)は存続(失われる合格候補が無い)。ON/OFF共通。
- 補完OFF(`EIGO_KP_BACKFILL=0`)の旧条件式: 上の`(not backfill_on) and …`として物理的に残置(安全停止スイッチ)。
- `gate_dropped`/`rescued_not_auto`の計算とlog(`entry.n_gate_dropped`/`rescued_not_auto`): 観測用に残置(ON時もlogされる)。
- F1累積除外(OPEN-456)の更新ロジック(`excluded.append`): OFF時のretry内でのみ働く。残置。
- call1のattempt内再選定(K0): 無変更(er105/er003)。K1はOPEN候補(ユーザー判断)。

## 3. 更新したtest(不整合な旧期待値をassertし続けない)
| test | 変更 |
|---|---|
| `er119_kp_human_review_01_test_01.py::test_outer_retry_only_when_auto_lt3_and_gate_drop_M7c` | 補完OFF/ONの両方をsubTestで検証(call1回数1・候補5のまま。ONでは補完が発動するが応答が全て既出/除外句で追加0) |
| 同 `::test_outer_retry_replaces_list_when_auto_lt3` | 旧条件(gate_dropped脚)の検証なので`EIGO_KP_BACKFILL=0`を明示。ON側の新挙動は`er119_kp_backfill_test_01.py::test_gate_drop_with_auto_lt3_no_longer_retries_on_TBF18a` |
| `er119_kp_rescue_wiring_test_01.py::test_w6_m3_rescued_but_not_auto_triggers_outer_retry_without_f1_exclusion` | 旧条件(rescued_not_auto脚)なので`EIGO_KP_BACKFILL=0`を明示。ON側は`er119_kp_backfill_test_01.py::test_rescued_not_auto_leg_removed_on_TBF18c`(retryなし・候補3件保持) |

## 4. 残存Grep結果(2026-10-26、本commit時点)
- `grep -n "gate_dropped\|rescued_not_auto" er119_kp_candidates_01.py` → 362(計算)/395(計算)/396-397(log)/403(OFF限定のretry条件)/405(OFF限定のF1累積)。ON時にretryを起こす参照は0。
- テスト内の旧脚参照: `er119_kp_human_review_01_test_01.py:119,134`、`er119_kp_rescue_wiring_test_01.py:214,226`(いずれもOFF明示)、`er119_kp_backfill_test_01.py:397`(ON側の撤去確認)。`er125_kp_rescue_production_test_01.py:590`はコメントのみ。
- flag名の読取箇所: `er119_kp_backfill_01.py:18,backfill_enabled()`の1箇所(`os.environ.get`1回)。他のProduction .pyに実装側の参照0(`test_flag_name_read_only_in_backfill_module_TBF20`)。`er119_kp_candidates_01.py`にはコメントの言及のみ。
- Family別の補完分岐: X/Y/Z runner・`er119_kp_wiring_01.py`に`backfill`文字列0(`test_x_y_z_use_single_wiring_point_and_no_family_branch_TBF21`)。
- A/B/C: `er119_kp_backfill_01`をimportするのは`er119_kp_candidates_01`のみ(`test_abc_modules_do_not_import_backfill_module_TBF22`)。`er105`/`er003`/`er125`/`er108`/`er119_kp_prompt_2v_01`の差分0(`git diff --stat`空)。

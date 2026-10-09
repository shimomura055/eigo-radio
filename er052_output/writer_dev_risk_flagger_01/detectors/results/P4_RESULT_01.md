# P4_RESULT_01: 保留セット最終評価(1回のみ。構成はP3で確定したものを変更していない)

- モデル gpt-6.1-sol。casebank: 保留37件(重大11/非重大26) + 合成保留7件。構成: C_main=D0rollback ∪ D2(1rep)、副=D1v2(D0ゲート+因果創作 各Flag上限3)、和集合。
- **K01(rf_y84g5r)は D0 の方向語彙設計時に参照した『汚染済み回帰』**。Recall_human(主)は3件(K01/K02/K11)だが、K01を除いた2件版も併記し、K01は別掲する。
- D1v2はD0ゲートで呼ぶタイプを絞り、因果創作は常に呼ぶ。ゲートで呼ばなかったタイプは未測定扱い。

## 1. 保留(実記事37件)

| 検出器 | units(重大/人間確認/非重大) | Recall_human(主) | Recall_all(副) | FPR_clear | FPR_boundary | FPR_hardneg | Flag(unit,sent,type)/unit | Flag固有文/unit | Rollback | 方向反転(別Fact) | 費用JPY |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D0(rollbackのみ) | 37(11/3/26) | 1/3 (33%, CI 6%-79%) | 1/11 (9%, CI 2%-38%) | 2/18 (11%, CI 3%-33%) | 0/3 (0%, CI 0%-56%) | 0/5 (0%, CI 0%-43%) | 0.08 | 0.08 | 1/1 | 0/0 | 0.00 |
| D2 1rep | 37(11/3/26) | 3/3 (100%, CI 44%-100%) | 8/11 (73%, CI 43%-90%) | 1/18 (6%, CI 1%-26%) | 1/3 (33%, CI 6%-79%) | 0/5 (0%, CI 0%-43%) | 0.27 | 0.27 | 1/1 | 0/0 | 51.50 |
| D1v2 gate+因果 | 37(11/3/26) | 3/3 (100%, CI 44%-100%) | 9/11 (82%, CI 52%-95%) | 2/18 (11%, CI 3%-33%) | 1/3 (33%, CI 6%-79%) | 1/5 (20%, CI 4%-62%) | 0.49 | 0.35 | 1/1 | 0/0 | 176.41 |
| C_main = D0rb ∪ D2 | 37(11/3/26) | 3/3 (100%, CI 44%-100%) | 8/11 (73%, CI 43%-90%) | 3/18 (17%, CI 6%-39%) | 1/3 (33%, CI 6%-79%) | 0/5 (0%, CI 0%-43%) | 0.32 | 0.32 | 1/1 | 0/0 | 51.50 |
| D0rb ∪ D1v2 | 37(11/3/26) | 3/3 (100%, CI 44%-100%) | 9/11 (82%, CI 52%-95%) | 4/18 (22%, CI 9%-45%) | 1/3 (33%, CI 6%-79%) | 1/5 (20%, CI 4%-62%) | 0.54 | 0.41 | 1/1 | 0/0 | 176.41 |
| D0rb ∪ D2 ∪ D1v2 | 37(11/3/26) | 3/3 (100%, CI 44%-100%) | 9/11 (82%, CI 52%-95%) | 4/18 (22%, CI 9%-45%) | 1/3 (33%, CI 6%-79%) | 1/5 (20%, CI 4%-62%) | 0.62 | 0.41 | 1/1 | 0/0 | 227.92 |

見逃し重大 / 誤Flag(clear・boundary・hardneg):
- D0(rollbackのみ): 見逃し=rf_emcgyx,rf_hdr8y4,rf_7suvyn,rf_665ga9,rf_t9nxuv,rf_nck2y6,rf_fmu3aa,rf_p4mtyd,rf_tcdxe4,rf_vph9nb / 誤Flag clear=rf_c3p892,rf_b2nvsf boundary=- hardneg=-
- D2 1rep: 見逃し=rf_t9nxuv,rf_fmu3aa,rf_vph9nb / 誤Flag clear=rf_5cryu9 boundary=rf_6j5x2m hardneg=-
- D1v2 gate+因果: 見逃し=rf_t9nxuv,rf_fmu3aa / 誤Flag clear=rf_da6twd,rf_5cryu9 boundary=rf_6j5x2m hardneg=rf_hmpyuu
- C_main = D0rb ∪ D2: 見逃し=rf_t9nxuv,rf_fmu3aa,rf_vph9nb / 誤Flag clear=rf_c3p892,rf_b2nvsf,rf_5cryu9 boundary=rf_6j5x2m hardneg=-
- D0rb ∪ D1v2: 見逃し=rf_t9nxuv,rf_fmu3aa / 誤Flag clear=rf_c3p892,rf_b2nvsf,rf_da6twd,rf_5cryu9 boundary=rf_6j5x2m hardneg=rf_hmpyuu
- D0rb ∪ D2 ∪ D1v2: 見逃し=rf_t9nxuv,rf_fmu3aa / 誤Flag clear=rf_c3p892,rf_b2nvsf,rf_da6twd,rf_5cryu9 boundary=rf_6j5x2m hardneg=rf_hmpyuu

### 既知事故別(拾った/件数)
| 検出器 | 20%の対象入替 | Rollback方向反転 | 因果・仕組みの創作 | 時期の創作 |
|---|---|---|---|---|
| D0(rollbackのみ) | 0/1 | 1/1 | 0/2 | 0/1 |
| D2 1rep | 1/1 | 1/1 | 1/2 | 0/1 |
| D1v2 gate+因果 | 1/1 | 1/1 | 1/2 | 0/1 |
| C_main = D0rb ∪ D2 | 1/1 | 1/1 | 1/2 | 0/1 |
| D0rb ∪ D1v2 | 1/1 | 1/1 | 1/2 | 0/1 |
| D0rb ∪ D2 ∪ D1v2 | 1/1 | 1/1 | 1/2 | 0/1 |

### タイプ別Recall(重大ケースのaccident_type別、hit/n)
| 検出器 | rollback方向反転 | その他 | 不在断定 | 主体対象入替 | 数量時系列 |
|---|---|---|---|---|---|
| D0(rollbackのみ) | 1/1 | 0/4 | 0/1 | 0/4 | 0/1 |
| D2 1rep | 1/1 | 2/4 | 1/1 | 4/4 | 0/1 |
| D1v2 gate+因果 | 1/1 | 3/4 | 1/1 | 4/4 | 0/1 |
| C_main = D0rb ∪ D2 | 1/1 | 2/4 | 1/1 | 4/4 | 0/1 |
| D0rb ∪ D1v2 | 1/1 | 3/4 | 1/1 | 4/4 | 0/1 |
| D0rb ∪ D2 ∪ D1v2 | 1/1 | 3/4 | 1/1 | 4/4 | 0/1 |

### Flag精度(KPI2: Flagされた(unit,sent,type)のうち重大ケース上のFlagの割合)と、参考: severity無視版(事前登録のKPI定義はseverity=重大のFlagのみ。以下は定義外の参考)

| 検出器 | Flag精度(重大のみFlag) | 参考: Recall_all(severity無視) | 参考: FPR_clear(severity無視) | FPR_boundary(同) | FPR_hardneg(同) |
|---|---|---|---|---|---|
| D0(rollbackのみ) | 33% | 1/11 (9%, CI 2%-38%) | 2/18 (11%, CI 3%-33%) | 0/3 (0%, CI 0%-56%) | 0/5 (0%, CI 0%-43%) |
| D2 1rep | 80% | 8/11 (73%, CI 43%-90%) | 1/18 (6%, CI 1%-26%) | 1/3 (33%, CI 6%-79%) | 0/5 (0%, CI 0%-43%) |
| D1v2 gate+因果 | 78% | 10/11 (91%, CI 62%-98%) | 2/18 (11%, CI 3%-33%) | 1/3 (33%, CI 6%-79%) | 2/5 (40%, CI 12%-77%) |
| C_main = D0rb ∪ D2 | 67% | 8/11 (73%, CI 43%-90%) | 3/18 (17%, CI 6%-39%) | 1/3 (33%, CI 6%-79%) | 0/5 (0%, CI 0%-43%) |
| D0rb ∪ D1v2 | 70% | 10/11 (91%, CI 62%-98%) | 4/18 (22%, CI 9%-45%) | 1/3 (33%, CI 6%-79%) | 2/5 (40%, CI 12%-77%) |
| D0rb ∪ D2 ∪ D1v2 | 74% | 10/11 (91%, CI 62%-98%) | 4/18 (22%, CI 9%-45%) | 1/3 (33%, CI 6%-79%) | 2/5 (40%, CI 12%-77%) |

### K01(汚染済み回帰)を除外した版

| 検出器 | Recall_human(主、K01除外) | Recall_all(K01除外) | FPR_clear | FPR_boundary | FPR_hardneg |
|---|---|---|---|---|---|
| D0(rollbackのみ) [K01除外] | 0/2 (0%, CI 0%-66%) | 0/10 (0%, CI 0%-28%) | 2/18 (11%, CI 3%-33%) | 0/3 (0%, CI 0%-56%) | 0/5 (0%, CI 0%-43%) |
| D2 1rep [K01除外] | 2/2 (100%, CI 34%-100%) | 7/10 (70%, CI 40%-89%) | 1/18 (6%, CI 1%-26%) | 1/3 (33%, CI 6%-79%) | 0/5 (0%, CI 0%-43%) |
| D1v2 gate+因果 [K01除外] | 2/2 (100%, CI 34%-100%) | 8/10 (80%, CI 49%-94%) | 2/18 (11%, CI 3%-33%) | 1/3 (33%, CI 6%-79%) | 1/5 (20%, CI 4%-62%) |
| C_main = D0rb ∪ D2 [K01除外] | 2/2 (100%, CI 34%-100%) | 7/10 (70%, CI 40%-89%) | 3/18 (17%, CI 6%-39%) | 1/3 (33%, CI 6%-79%) | 0/5 (0%, CI 0%-43%) |
| D0rb ∪ D1v2 [K01除外] | 2/2 (100%, CI 34%-100%) | 8/10 (80%, CI 49%-94%) | 4/18 (22%, CI 9%-45%) | 1/3 (33%, CI 6%-79%) | 1/5 (20%, CI 4%-62%) |
| D0rb ∪ D2 ∪ D1v2 [K01除外] | 2/2 (100%, CI 34%-100%) | 8/10 (80%, CI 49%-94%) | 4/18 (22%, CI 9%-45%) | 1/3 (33%, CI 6%-79%) | 1/5 (20%, CI 4%-62%) |

### K01 の扱い(別掲)

- D0(rollbackのみ): K01(rf_y84g5r) = Flag
- D2 1rep: K01(rf_y84g5r) = Flag
- D1v2 gate+因果: K01(rf_y84g5r) = Flag
- C_main = D0rb ∪ D2: K01(rf_y84g5r) = Flag
- D0rb ∪ D1v2: K01(rf_y84g5r) = Flag
- D0rb ∪ D2 ∪ D1v2: K01(rf_y84g5r) = Flag


### confidence閾値曲線: C_main (D0rb ∪ D2) 保留
| 閾値 | Recall_human | Recall_all | FPR_clear | FPR_boundary | FPR_hardneg | Flag(unit,sent,type) | Flag固有文 |
|---|---|---|---|---|---|---|---|
| 0.00 | 3/3 (100%, CI 44%-100%) | 8/11 (73%, CI 43%-90%) | 3/18 (17%, CI 6%-39%) | 1/3 (33%, CI 6%-79%) | 0/5 (0%, CI 0%-43%) | 12 | 12 |
| 0.30 | 3/3 (100%, CI 44%-100%) | 8/11 (73%, CI 43%-90%) | 3/18 (17%, CI 6%-39%) | 1/3 (33%, CI 6%-79%) | 0/5 (0%, CI 0%-43%) | 12 | 12 |
| 0.50 | 2/3 (67%, CI 21%-94%) | 5/11 (45%, CI 21%-72%) | 1/18 (6%, CI 1%-26%) | 1/3 (33%, CI 6%-79%) | 0/5 (0%, CI 0%-43%) | 7 | 7 |
| 0.70 | 2/3 (67%, CI 21%-94%) | 4/11 (36%, CI 15%-65%) | 1/18 (6%, CI 1%-26%) | 1/3 (33%, CI 6%-79%) | 0/5 (0%, CI 0%-43%) | 6 | 6 |
| 0.90 | 1/3 (33%, CI 6%-79%) | 3/11 (27%, CI 10%-57%) | 0/18 (0%, CI 0%-18%) | 0/3 (0%, CI 0%-56%) | 0/5 (0%, CI 0%-43%) | 3 | 3 |

## 2. 合成保留(7件、全て重大)

| 検出器 | units(重大/人間確認/非重大) | Recall_human(主) | Recall_all(副) | FPR_clear | FPR_boundary | FPR_hardneg | Flag(unit,sent,type)/unit | Flag固有文/unit | Rollback | 方向反転(別Fact) | 費用JPY |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D0(rollbackのみ) | 7(7/0/0) | - | 1/7 (14%, CI 3%-51%) | - | - | - | 0.14 | 0.14 | 0/0 | 1/5 | 0.00 |
| D2 1rep | 7(7/0/0) | - | 4/7 (57%, CI 25%-84%) | - | - | - | 0.57 | 0.57 | 0/0 | 2/5 | 10.07 |
| D1v2 gate+因果 | 7(7/0/0) | - | 3/7 (43%, CI 16%-75%) | - | - | - | 0.86 | 0.43 | 0/0 | 1/5 | 31.30 |
| C_main = D0rb ∪ D2 | 7(7/0/0) | - | 4/7 (57%, CI 25%-84%) | - | - | - | 0.57 | 0.57 | 0/0 | 2/5 | 10.07 |
| D0rb ∪ D1v2 | 7(7/0/0) | - | 3/7 (43%, CI 16%-75%) | - | - | - | 0.86 | 0.43 | 0/0 | 1/5 | 31.30 |
| D0rb ∪ D2 ∪ D1v2 | 7(7/0/0) | - | 4/7 (57%, CI 25%-84%) | - | - | - | 1.29 | 0.57 | 0/0 | 2/5 | 41.37 |

見逃し重大 / 誤Flag(clear・boundary・hardneg):
- D0(rollbackのみ): 見逃し=S-01,S-04,S-05,S-07,S-11,S-14 / 誤Flag clear=- boundary=- hardneg=-
- D2 1rep: 見逃し=S-01,S-04,S-05 / 誤Flag clear=- boundary=- hardneg=-
- D1v2 gate+因果: 見逃し=S-01,S-04,S-05,S-07 / 誤Flag clear=- boundary=- hardneg=-
- C_main = D0rb ∪ D2: 見逃し=S-01,S-04,S-05 / 誤Flag clear=- boundary=- hardneg=-
- D0rb ∪ D1v2: 見逃し=S-01,S-04,S-05,S-07 / 誤Flag clear=- boundary=- hardneg=-
- D0rb ∪ D2 ∪ D1v2: 見逃し=S-01,S-04,S-05 / 誤Flag clear=- boundary=- hardneg=-

### タイプ別Recall(重大ケースのaccident_type別、hit/n)
| 検出器 | 否定反転 | 数量時系列 | 方向反転(別Fact) |
|---|---|---|---|
| D0(rollbackのみ) | 0/1 | 0/1 | 1/5 |
| D2 1rep | 1/1 | 1/1 | 2/5 |
| D1v2 gate+因果 | 1/1 | 1/1 | 1/5 |
| C_main = D0rb ∪ D2 | 1/1 | 1/1 | 2/5 |
| D0rb ∪ D1v2 | 1/1 | 1/1 | 1/5 |
| D0rb ∪ D2 ∪ D1v2 | 1/1 | 1/1 | 2/5 |

### Flag精度(KPI2: Flagされた(unit,sent,type)のうち重大ケース上のFlagの割合)と、参考: severity無視版(事前登録のKPI定義はseverity=重大のFlagのみ。以下は定義外の参考)

| 検出器 | Flag精度(重大のみFlag) | 参考: Recall_all(severity無視) | 参考: FPR_clear(severity無視) | FPR_boundary(同) | FPR_hardneg(同) |
|---|---|---|---|---|---|
| D0(rollbackのみ) | 100% | 1/7 (14%, CI 3%-51%) | - | - | - |
| D2 1rep | 100% | 4/7 (57%, CI 25%-84%) | - | - | - |
| D1v2 gate+因果 | 100% | 3/7 (43%, CI 16%-75%) | - | - | - |
| C_main = D0rb ∪ D2 | 100% | 4/7 (57%, CI 25%-84%) | - | - | - |
| D0rb ∪ D1v2 | 100% | 3/7 (43%, CI 16%-75%) | - | - | - |
| D0rb ∪ D2 ∪ D1v2 | 100% | 4/7 (57%, CI 25%-84%) | - | - | - |

## 3. 記事モード(保留側の既知重大元記事7本、C_main = D0rb ∪ D2rank上位3、Recall@top3=文脈内)

| 記事 | 既知重大(case) | ラベル根拠/分割 | 文の位置 | D2rank順位(top3) | ±2文窓内 | D0 rollback Flag | C_main Flag固有文数 | Checker(Production単一run) |
|---|---|---|---|---|---|---|---|---|
| holdout_meta_refresh_run03_b1b | rf_y84g5r | ユーザー確認/holdout | s23 | 3 | YES | あり | 3 | NONBLOCKING |
| holdout_ai_control_jb9k_b1b | rf_emcgyx | ユーザー確認/holdout | s24 | 1 | YES | なし | 3 | NONBLOCKING |
| holdout_space_p2rep2_ja | rf_hdr8y4 | ユーザー確認/holdout | s16 | 2 | YES | なし | 3 | NA_JA |
| holdout_ai_control_p2rep1_b1b | rf_7suvyn | Sonnet判定/holdout | s10 | - | NO | なし | 3 | BLOCKING |
| holdout_ai_control_p2rep1_b1b | rf_qupxd4 | Sonnet判定/dev | s26 | 1 | YES | なし | 3 | BLOCKING |
| holdout_hormuz_T0M0rep2_b1b | rf_665ga9 | Sonnet判定/holdout | s6 | 1 | YES | なし | 4 | NO_PRIMARY |
| holdout_hormuz_an3_b1b | rf_t9nxuv | Sonnet判定/holdout | s21 | 1 | YES | なし | 3 | BLOCKING |
| holdout_hormuz_b3div_run02_b1b | rf_p4mtyd | Fable確定/holdout | s28 | 1 | YES | なし | 3 | BLOCKING |

- **保留重大の記事モード Recall@top3(D2rank上位3、位置特定できた保留重大 7件) = 6/7**、±2文窓 6/7。K01除外 5/6。
- rf_qupxd4 はdev分割の重大だが、同じ記事に保留重大 rf_7suvyn があるため保留側として評価した(devとしてはP3で使っていない)。上の分母は保留分割(split=holdout)のみ。
- unlocated(記事ファイル未保存): rf_nck2y6/rf_fmu3aa/rf_tcdxe4/rf_vph9nb は記事モードでは測れない(casebankモードのみ)。

## 4. Checker参考との並置(保留重大)

- Checker検出の定義: Production単一run BLOCKING=検出 / NONBLOCKING・NOT_CANDIDATE=見逃し / Trial多runのみは blocking_any_cycle/runs >= 50% なら検出 / JA・Checker未実行は比較対象外(n/a)。
- 注意(選択バイアス): casebankの重大はCheckerが浮上させた文に偏る(CHECKER_REFERENCE §0)。Checker側のRecallは有利に出る。

| case | 型 | 根拠 | Checker | C_main(D0rb∪D2) | D1v2 | 全合算(+D1v2) |
|---|---|---|---|---|---|---|
| rf_y84g5r | rollback方向反転 | ユーザー確認 | 見逃し | Flag | Flag | Flag |
| rf_emcgyx | 不在断定 | ユーザー確認 | 見逃し | Flag | Flag | Flag |
| rf_hdr8y4 | 主体対象入替 | ユーザー確認 | n/a | Flag | Flag | Flag |
| rf_7suvyn | その他 | Sonnet判定 | 検出 | Flag | Flag | Flag |
| rf_665ga9 | 主体対象入替 | Sonnet判定 | n/a | Flag | Flag | Flag |
| rf_t9nxuv | 数量時系列 | Sonnet判定 | 検出 | - | - | - |
| rf_nck2y6 | 主体対象入替 | Sonnet判定 | 検出 | Flag | Flag | Flag |
| rf_fmu3aa | その他 | Sonnet判定 | 検出 | - | - | - |
| rf_p4mtyd | その他 | Fable確定 | 検出 | Flag | Flag | Flag |
| rf_tcdxe4 | 主体対象入替 | Fable確定 | 検出 | Flag | Flag | Flag |
| rf_vph9nb | その他 | Sonnet判定 | n/a | - | Flag | Flag |

| 集合 | 両方拾った | Flaggerだけ | Checkerだけ | どちらも拾えず | 比較対象外 |
|---|---|---|---|---|---|
| C_main(D0rb∪D2) | 4 | 2 | 2 | 0 | 3 |
| 全合算(D0rb∪D2∪D1v2) | 4 | 2 | 2 | 0 | 3 |

- 非重大(保留26件)の誤検出: C_main 4/26、全合算 6/26、Checker(参考、比較可能24件中) 4。Checkerの『誤検出』は**BLOCKING/MAJOR STOP**で、Flaggerの『Flag』とは意味が異なる(Flaggerは人間確認依頼で、合否に使わない)。

## 5. S0_USER_CHECK 反転時の再計算(ユーザー回答待ち。S0-1=rf_aennw4[保留]、S0-2=rf_xyw4mp[dev]、S0-3=rf_8fbz5r[保留])

| 反転対象 | 対象分割 | 構成 | Recall_all | Recall_human | FPR_boundary |
|---|---|---|---|---|---|
| S0-1のみ | holdout | C_main = D0rb ∪ D2 | 8/12 (67%, CI 39%-86%) | 3/4 (75%, CI 30%-95%) | 1/3 (33%, CI 6%-79%) |
| S0-1のみ | holdout | D0rb ∪ D2 ∪ D1v2 | 9/12 (75%, CI 47%-91%) | 3/4 (75%, CI 30%-95%) | 1/3 (33%, CI 6%-79%) |
| S0-3のみ | holdout | C_main = D0rb ∪ D2 | 8/12 (67%, CI 39%-86%) | 3/4 (75%, CI 30%-95%) | 1/3 (33%, CI 6%-79%) |
| S0-3のみ | holdout | D0rb ∪ D2 ∪ D1v2 | 9/12 (75%, CI 47%-91%) | 3/4 (75%, CI 30%-95%) | 1/3 (33%, CI 6%-79%) |
| S0-1+S0-3 | holdout | C_main = D0rb ∪ D2 | 8/13 (62%, CI 36%-82%) | 3/5 (60%, CI 23%-88%) | 1/3 (33%, CI 6%-79%) |
| S0-1+S0-3 | holdout | D0rb ∪ D2 ∪ D1v2 | 9/13 (69%, CI 42%-87%) | 3/5 (60%, CI 23%-88%) | 1/3 (33%, CI 6%-79%) |
| 全て | holdout | C_main = D0rb ∪ D2 | 8/13 (62%, CI 36%-82%) | 3/5 (60%, CI 23%-88%) | 1/3 (33%, CI 6%-79%) |
| 全て | holdout | D0rb ∪ D2 ∪ D1v2 | 9/13 (69%, CI 42%-87%) | 3/5 (60%, CI 23%-88%) | 1/3 (33%, CI 6%-79%) |

## 6. 費用(P4、台帳)

- d1v2: ¥209.86
- d2: ¥61.57
- d2rank: ¥19.80
- P4合計 ¥291.23

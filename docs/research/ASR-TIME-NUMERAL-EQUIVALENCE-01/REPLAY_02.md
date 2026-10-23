# REPLAY_02(ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_02、OF-TN-05、API 0)

## 方法
- pairs再抽出: `py replay_extract_pairs_01.py --root ../../.. --out pairs_02.jsonl --skip-substr ASR-TIME-NUMERAL-EQUIVALENCE-01`(47,392 json/jsonlから**2,701対**。`--skip-substr`は委任_02で追加=自作の合成test/replay出力が混入しないようにするため。最初の抽出[10,511対]は自作の `matrix02_*.json`/`pairs_01.jsonl` 等を含み、意図的なNE合成行が『PASS→NG』に出たので破棄して再抽出した)。
- replay: `py replay_judge_01.py --pairs pairs_02.jsonl --out replay02_{base,after}.json [--modules base_HEAD]`(修正前=HEAD `er021`、修正後=working tree。value_guard / classify_asr_match / tier1 / 統一judge[Primary 1本]の4層)。比較: `replay_compare_01.py`、Family別: `replay_family_02.py`。生データ `replay02_*.json/.txt`。
- 注意: 抽出は `text` 系キーも対象にするため、判定の変化の確認用であり件数をPASS率として使わない。

## 結果(修正前→修正後)
| 項目 | 件数 |
|---|---|
| 対の総数 | 2,701 |
| **judge PASS→NG** | **0** |
| **分類層(classify_asr_match) PASS→NG** | **0** |
| **value_guard PASS→NG** | **0** |
| tier1 変化 | 0 |
| judge NG→PASS | 0 |
| judge 状態の変化(NG→NG) | 1 |
| value_guard NG/UNKNOWN→EQUAL | 3(全て時刻起因) |

NG→PASS/EQUALの内訳(時刻起因のみ):
1. `at five thirty`↔`at 5:30`(fixture `pattern_probe_01.json`): UNKNOWN→EQUAL(判定PASSのまま)。
2. 『二十年後』c8保存entry(canon `At ten thirty`/ASR `At 10:30`): UNKNOWN→EQUAL(PASSのまま)。
3. Hormuz記事 `At 10:16 a.m.`↔ASR `At 10 16 a.m.`(`er103_ret_baseline_signature_v1.json`): value_guard DIFF→EQUAL(OF-TN-02の効果=am/pm付きの`10 16`をtime atomに揃えた)。判定は他要因(分類N)で NG_PROTECTED→NG_SECONDARY_UNAVAILABLE(= 時刻の誤保護が外れ、Secondaryを呼べる状態になっただけ。PASSにはならない)。

(委任_01のreplay[5,330対]にあった実対 c8『At 10 thirty』×『At ten-thirty』のNG→PASSは、今回の抽出では抽出元の `er021_output/.../telemetry.jsonl` に当該行が無く対に現れない。実在の対は **c8 attempt2ファイル**から取り、RUNTIME_EVIDENCE_01.md で修正前NG→修正後PASSを確認済み。)

## Family別内訳(src pathによるヒューリスティック分類。`replay_family_02.py`)
```
family                    pairs  judge_PASS->NG judge_NG->PASS judge_state_other vg_PASS->NG vg_NG->PASS cls_PASS->NG cls_NG->PASS
A/B legacy                  407        0              0               0               0            0          0           0
C                            28        0              0               0               0            0          0           0
X                           203        0              0               0               0            0          0           0
Y                            18        0              0               0               0            0          0           0
Z                            35        0              0               0               0            1          0           0
other(共通/docs/fixture)   2010        0              0               1               0            2          0           0
TOTAL                      2701        0              0               1               0            3          0           0
```
A/B/C Legacy entryへのPASS→NG=0(§27-3、判定変化なし)。変化はZ 1件(c8保存entryのUNKNOWN→EQUAL)と共通/fixture 2件のみ。

## 判定
OF-TN-05 の replay条件(judge PASS→NG=0、分類層PASS→NG=0、value_guard PASS→NG=0)を満たす。意図したPASS→NG(桁連結・年号語形↔桁連結)は、organicな対には存在せず(replay上は該当0件)、TEST_MATRIX_02の合成行でのみ発生(意図どおり)。

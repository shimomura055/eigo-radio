# NEGATIVE_RECHECK_01(JA-ASR-V2-BETA-PRODUCTION-WIRING-01 委任_02A。Offline再現・API 0)

生成物: `tools/offline_recheck_01.py` -> `offline_recheck_01.out.json`(決定的・socket guard・Reading Resolver無効)。再現: `PYTHONUTF8=1 .venv/Scripts/python.exe -X utf8 docs/research/JA-ASR-V2-BETA-PRODUCTION-WIRING-01/tools/offline_recheck_01.py <out.json>`(約1分)。
同じ手順を単体test `er078_ja_v2beta_wiring_test_01.py::test_t_p3_offline_parity_with_frozen_proto_and_negative_increment_equals_known_eight_rows` が毎回実行する(下の合格条件を assert)。

## 1. 方法
- コーパス: `docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/eval_unified_03.out.json`(2,103行: N3 30負例・拡張負例[T1同音異表記便乗/T2 β最悪露出]・N1/R4R3等・正例[POS]・ラベルなし[UNL])。
- 各行を **Production adapter**(`evaluate_attempt_ja_with_cascade_detail`)で2回判定する: ① scope外(None) = 従来(L0)、② scope X = v2+β(R-1 OFF)。Secondary(Azure)は記録済み転写をstub注入。
- oracle: 凍結proto `proto_unified_03.judge(Flags(l1=True,l2=True,l3=False,r1=False))`。Productionの(cat, reason)と全行比較(reason `composite` は Productionの `ja_beta_composite` に対応づけ)。

## 2. 結果(実測)
| 項目 | 値 | 合格条件 | 判定 |
|---|---|---|---|
| 比較行数 | 2,103 | - | - |
| proto との不一致 | **0** | 0 | OK |
| 負例の誤PASS増分(L0がNG -> 新方式で通過)の行数 | **8** | 既知8行(T1 6 + T2 2) | OK |
| 増分の**行集合**が既知8行と同一(R-5) | **同一(identical=true、想定外の新規行 0、欠落 0)** | 同一 | OK |
| 回帰(L0 PASS系 -> 新方式 NG) | **0** | 0 | OK |
| 新層の例外(`ja_v2beta.error`) | **0** | 0 | OK |
| Secondary側v2の救済行のうちE3/E4(Variant Layer)を持つ行(R-4) | **0** | 0(出れば報告) | OK |

負例(NEG)全体の新判定内訳: NG 1,415 / clean PASS 177(L0から不変) / 既存PASS_W 200(L0から不変) / 新方式の救済(`rescue_basis`付き) 11。この11行のうち **8行がL0でNG(= 上の増分)**、残り3行はL0でも通過していた(増分でない)。
正例(POS) 213行: L0 NG -> 新方式で通過 **2行**、L0通過のまま通過 159行、NGのまま 52行(= 本コーパスは負例中心で、正例の救済増は小さい。月タイトルの救済は RUNTIME_EVIDENCE_01.md)。

### 2-1. 増分8行(既知8行と同一であることを行の同一性[group, scenario, primary, secondary]で確認)
| group | scenario | Primary転写 | Secondary転写 | 新判定 | rescue_basis | reason |
|---|---|---|---|---|---|---|
| N1_150 | S_canon | 月の詩は8000900本超 | 月のしわ、8,900本超 | PASS_W | beta | ja_beta_composite |
| R4R3_extra18 | P_only | 月の詩は、8900本超！その奥に潜む「岩の上着」の秘密 | (なし) | PASS_W | v2 | primary_pass |
| R4R3_extra18 | PS_same | 月の詩は、8900本超！(同左) | 月の詩は、8900本超！(同左) | PASS_W | v2 | primary_pass |
| R4R3_extra18 | P_only | 月の詩は、8,900本超！(同左) | (なし) | PASS_W | v2 | primary_pass |
| R4R3_extra18 | PS_same | 月の詩は、8,900本超！(同左) | 月の詩は、8,900本超！(同左) | PASS_W | v2 | primary_pass |
| R4R3_extra18 | S_canon | 月のしわ、8000900本超！その奥に潜む「岩の上着」の秘密 | 月のしわ、8,900本超！(同左) | PASS_W | beta | ja_beta_composite |
| UC6_U6_同音異表記便乗 | P_only | 月の死は、8,900本超！その奥に潜む「岩の上着」の秘密 | (なし) | PASS_W | v2 | primary_pass |
| UC6_U6_同音異表記便乗 | PS_same | 月の死は、8,900本超！(同左) | 月の死は、8,900本超！(同左) | PASS_W | v2 | primary_pass |

これらは承認済みの既知の構造的リスク(T1: 同音異表記[詩/死]の便乗=漢字違いは音声から区別不能、T2: β最悪露出[SecondaryがPrimaryと同じ内容を原稿どおり出した場合])で、ユーザー正式決定(2026-10-29、UDR #201/#202/#206/#207)の範囲内。**増分はこの8行に限られ、他の負例には新規の誤PASSを生まない**(行の同一性で確認)。
再提示トリガー(R-6): 実運用でPASS_Wの誤りが1件でも確認された場合は #206/#207 をユーザーへ再提示する(USER_DECISION_REGISTER_01.md に記録)。

## 3. 汎用題・metamorphic(題固有の例外を作っていないことの検査。API 0、`er078_ja_v2beta_01_test_01.py`)
- 汎用題positive 10種(`今日の売上は1,200円でした。` 等、月と無関係): scope Xで全て PASS_W(`rescue_basis=v2`、`JA_NEWLAYER_PRON_EQUIVALENT`)、Azure呼出0(`test_t_g2_...`)。scope外では新キー無し(`test_generic_v2_positive_is_ng_without_scope` 10件)。
- 汎用題negative 6種(値違い/桁違い/助数詞違い/脱落/否定/単位違い) x Secondary 3条件(なし/Primaryと同じ誤り/原稿どおり): いずれも新層の寄与(`rescue_basis`)による通過は 0(`test_t_n_ng_generic_negatives_have_no_new_pass` 6件)。
- metamorphic: 題材名詞の差替え(売上/参加者/会議 -> 入場料/気温/来場者/授業)・無関係な前置きの追加でも verdict/rescue_basis が不変(positive 6件)、負例は差替え後も救済されない(negative 6件)(`test_t_g3_metamorphic_*`)。
- 非観測形のPrimary数字崩れ(β対象外4形): 説明されず NG(`test_t_b1_beta_non_observed_forms_are_not_explained`)。M-1(不規則読み数詞: 一人/二人/一日等)は新層で救済されない(`test_t_m1_irregular_...`)。
- R-9(a) precheck健全性: コーパス全行で `composite_judge`成立 => `precheck_composite`成立(`test_r9a_precheck_is_sound_over_the_stored_eval_corpus`)。
- 静的: 新moduleに題固有語・記事/題ID参照なし(`test_t_g1_...`/`test_t_g4_...`)。

## 4. 結論
Offline再現は **承認済みの基準線(R-1 OFF構成)を逐行で再現**(protoと0不一致)。誤PASS増分は既知8行と同一、回帰0。追加の新規リスクは検出されなかった。

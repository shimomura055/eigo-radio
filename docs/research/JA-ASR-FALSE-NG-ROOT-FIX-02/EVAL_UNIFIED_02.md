# EVAL_UNIFIED_02(JA-ASR-FALSE-NG-ROOT-FIX-02 委任_02B。eval_unified_02.py の出力から自動生成。API 0)
事前登録=PREREGISTERED_02.md。Production HEAD 定数: {"JA_SECONDARY_VALUE_EQUIVALENCE_ENABLED": true, "READING_MATCH_FINAL_GATE": true}。Production file sha256(先頭16桁・不変確認): {"er007_ja_asr_validator_01.py": "9a0e104422c8c243", "er007_ja_secondary_asr_01.py": "d3c5565dd91ad10f", "er078_asr_unified_judge_01.py": "c3e7c2566f5bb16d", "er078_asr_value_guard_01.py": "f3fd435cfc408637"}。
NEG集合(Phase 1と同一): n=1439 sha256=d55f24e239d3eb024951c01e57a8d186d9cd6a8ebf979c6470399b5cea2405dd(事前登録値とassert一致)。L0とPhase 1 M0の行ごと一致: 比較1706行・不一致0。L1とPhase 1 M1の差: 3行(すべて不規則読みガード由来: True、`今日は一日中雨→ついたち中雨` M1=PASS_W→L1=NG)。
PASS_W=警告付きPASS(判定器のPASS_WITH_WARNING、または新層[v2発音救済/β/辞書]経由=試聴必須)。PASSと別集計。

## 1. 6音声×層: 最終Gate結果(決定対=当時記録のOpenAI転写 × 当該wavのAzure転写)
| 音声 | L0 | L1 | L1+L2 | L1+L3 | L1+L2+L3 | +L4 N=2 | +L4 N=3 | +L4 N=4(参考) |
|---|---|---|---|---|---|---|---|---|
| run_ms_03 a1 | NG:p1_value_diff | NG:p1_value_diff | NG:p1_value_diff | NG:p1_value_diff | NG:p1_value_diff | PASS_W(draw2で停止/再転写1回) | PASS_W(draw2で停止/再転写1回) | PASS_W(draw2で停止/再転写1回) |
| run_ms_03 a2 | NG:secondary_not_accepted | PASS_W:L1_v2_pron:primary:A3_value+A2_particle | PASS_W:L1_v2_pron:primary:A3_value+A2_particle | PASS_W:L1_v2_pron:primary:A3_value+A2_particle | PASS_W:L1_v2_pron:primary:A3_value+A2_particle | PASS_W(draw1で停止/再転写0回) | PASS_W(draw1で停止/再転写0回) | PASS_W(draw1で停止/再転写0回) |
| run_ms_03 a3 | NG:p1_value_diff | NG:p1_value_diff | PASS_W:L2_beta_composite:listen | NG:p1_value_diff | PASS_W:L2_beta_composite:listen | PASS_W(draw1で停止/再転写0回) | PASS_W(draw1で停止/再転写0回) | PASS_W(draw1で停止/再転写0回) |
| run_reselect_01 a1 | NG:secondary_not_accepted | PASS_W:L1_v2_pron:primary:A3_value+A2_particle | PASS_W:L1_v2_pron:primary:A3_value+A2_particle | PASS_W:L1_v2_pron:primary:A3_value+A2_particle | PASS_W:L1_v2_pron:primary:A3_value+A2_particle | PASS_W(draw1で停止/再転写0回) | PASS_W(draw1で停止/再転写0回) | PASS_W(draw1で停止/再転写0回) |
| run_reselect_01 a2 | NG:secondary_not_accepted | PASS_W:L1_v2_pron:primary:A3_value+A2_particle | PASS_W:L1_v2_pron:primary:A3_value+A2_particle | PASS_W:L1_v2_pron:primary:A3_value+A2_particle | PASS_W:L1_v2_pron:primary:A3_value+A2_particle | PASS_W(draw1で停止/再転写0回) | PASS_W(draw1で停止/再転写0回) | PASS_W(draw1で停止/再転写0回) |
| run_reselect_01 a3 | NG:secondary_not_accepted | NG:secondary_not_accepted | NG:secondary_not_accepted | NG:secondary_not_accepted | NG:secondary_not_accepted | NG:secondary_not_accepted | PASS_W(draw3で停止/再転写2回) | PASS_W(draw3で停止/再転写2回) |

### 1a. 決定対の転写(OpenAI=記録時、Azure=当該wav)
| 音声 | OpenAI(stored) | Azure |
|---|---|---|
| run_ms_03 a1 | 月野詩は8000句800本超え。その奥に潜む岩の上着の秘密。 | 月野市は8900本越え。その奥に潜む岩の上着の秘密。 |
| run_ms_03 a2 | 月の死は八千九百本超。その奥に潜む岩の上着の秘密。 | 月の詩は8900本超。その奥に潜む岩の上着の秘密。 |
| run_ms_03 a3 | 月の氏は8000900本超。その奥に潜む岩の上着の秘密。 | 杉野氏は8900本超。その奥に潜む岩の上着の秘密。 |
| run_reselect_01 a1 | 月野氏は8,900本超。その奥に潜む岩の上着の秘密 | 月の詩は8900本ちょ。その奥に潜む岩の上着の秘密。 |
| run_reselect_01 a2 | 月の詩は八千九百本超。その奥に潜む岩の上着の秘密 | 月の詩は8900本ちょうその奥に潜む岩の上着の秘密。 |
| run_reselect_01 a3 | スギノ市は、八千九百本超、その奥に潜む岩の上着の秘密。 | Sukino氏は8900本超。その奥に潜む岩の上着の秘密。 |

## 2. 全draw対(OpenAI全draw × Azure[0]): 層別 PASS / PASS_W / NG
| 音声 | draw数 | L0 | L1 | L1+L2 | L1+L3 | L1+L2+L3 |
|---|---|---|---|---|---|---|
| run_ms_03 a1 | 4 | 0/0/4 | 0/0/4 | 0/0/4 | 0/2/2 | 0/2/2 |
| run_ms_03 a2 | 4 | 0/0/4 | 0/1/3 | 0/1/3 | 0/1/3 | 0/1/3 |
| run_ms_03 a3 | 4 | 0/0/4 | 0/1/3 | 0/3/1 | 0/1/3 | 0/3/1 |
| run_reselect_01 a1 | 5 | 0/0/5 | 0/3/2 | 0/3/2 | 0/3/2 | 0/3/2 |
| run_reselect_01 a2 | 5 | 0/0/5 | 0/1/4 | 0/4/1 | 0/1/4 | 0/4/1 |
| run_reselect_01 a3 | 5 | 0/0/5 | 0/1/4 | 0/1/4 | 0/1/4 | 0/1/4 |
| 合計 | 27 | 0/0/27 | 0/7/20 | 0/12/15 | 0/9/18 | 0/14/13 |
(セルは PASS/PASS_W/NG の件数)

### 2a. 各draw対の判定(層 L1+L2+L3)と経路(NG理由 or 発火層)
- **run_ms_03 a1**: stored→NG:p1_value_diff / phase3_redraw0→PASS_W:L3_dict_koe:secondary:v1:A3_value+A2_particle|prod_warning:SECONDARY_C / phase3_redraw1→PASS_W:L3_dict_koe:secondary:v1:A3_value+A2_particle|prod_warning:SECONDARY_C / phase3_redraw2→NG:p1_value_diff
- **run_ms_03 a2**: stored→PASS_W:L1_v2_pron:primary:A3_value+A2_particle / phase3_redraw0→NG:p1_value_diff / phase3_redraw1→NG:p1_value_diff / phase3_redraw2→NG:p1_value_diff
- **run_ms_03 a3**: stored→PASS_W:L2_beta_composite:listen / phase3_redraw0→PASS_W:L1_v2_pron:primary:A3_value+A2_particle / phase3_redraw1→NG:p2_exclusion:A4_C2_HOMOGRAPH / phase3_redraw2→PASS_W:L2_beta_composite:listen
- **run_reselect_01 a1**: stored→PASS_W:L1_v2_pron:primary:A3_value+A2_particle / reasr_openai0→PASS_W:L1_v2_pron:primary:A3_value+A2_particle / reasr_openai1→PASS_W:L1_v2_pron:primary:A3_value+A2_particle / reasr_openai2→NG:p2_exclusion:A4_C2_HOMOGRAPH / reasr_openai3→NG:secondary_not_accepted
- **run_reselect_01 a2**: stored→PASS_W:L1_v2_pron:primary:A3_value+A2_particle / reasr_openai0→PASS_W:L2_beta_composite:listen / reasr_openai1→PASS_W:L2_beta_composite:listen / reasr_openai2→NG:p1_value_diff / reasr_openai3→PASS_W:L2_beta_composite:listen
- **run_reselect_01 a3**: stored→NG:secondary_not_accepted / reasr_openai0→NG:p1_value_diff / reasr_openai1→PASS_W:L1_v2_pron:primary:A3_value+A2_particle / reasr_openai2→NG:p1_value_diff / reasr_openai3→NG:p1_value_diff

### 2b. L4(判定前OpenAI再転写)の到達確率(L1+L2+L3 判定、k draw中m本が非NG)
| 音声 | k | m(非NG) | N=1 | N=2 | N=3 | N=4 |
|---|---|---|---|---|---|---|
| run_ms_03 a1 | 4 | 2 | 0.50(保存順:NG) | 0.83(保存順:PASS_W) | 1.00(保存順:PASS_W) | 1.00(保存順:PASS_W) |
| run_ms_03 a2 | 4 | 1 | 0.25(保存順:PASS_W) | 0.50(保存順:PASS_W) | 0.75(保存順:PASS_W) | 1.00(保存順:PASS_W) |
| run_ms_03 a3 | 4 | 3 | 0.75(保存順:PASS_W) | 1.00(保存順:PASS_W) | 1.00(保存順:PASS_W) | 1.00(保存順:PASS_W) |
| run_reselect_01 a1 | 5 | 3 | 0.60(保存順:PASS_W) | 0.90(保存順:PASS_W) | 1.00(保存順:PASS_W) | 1.00(保存順:PASS_W) |
| run_reselect_01 a2 | 5 | 4 | 0.80(保存順:PASS_W) | 1.00(保存順:PASS_W) | 1.00(保存順:PASS_W) | 1.00(保存順:PASS_W) |
| run_reselect_01 a3 | 5 | 1 | 0.20(保存順:NG) | 0.40(保存順:NG) | 0.60(保存順:PASS_W) | 0.80(保存順:PASS_W) |
(hyper_reach=draw集合からN個を無作為に選んで少なくとも1本が非NGの確率。保存順=記録された順に最初にPASS/PASS_Wで停止するシミュレーション)

## 3. 負例: 誤PASS(PASS+PASS_W)と増分(L0比)
### 3a. 層別 総誤PASS / 増分誤PASS(truth==NEG全行、Phase 1の1439行+L3_NEG+N3_redraw)
NEG行数=1803(Phase 1: 1439 + L3_NEG + N3_redraw)
| 層 | 総誤PASS | うちPASS | うちPASS_W | 増分誤PASS(L0=NG→誤PASS) | 回帰(L0 PASS系→NG, 全truth) |
|---|---|---|---|---|---|
| L0 | 380 | 177 | 203 | 0 | 0 |
| L1 | 386 | 177 | 209 | 6 | 0 |
| L1+L2 | 388 | 177 | 211 | 8 | 0 |
| L1+L3 | 386 | 177 | 209 | 6 | 0 |
| L1+L2+L3 | 388 | 177 | 211 | 8 | 0 |

### 3b. 増分誤PASSの型別内訳(Phase 1の3型 T1/T2/T3 以外=OTHER があれば当該層は不合格)
| 層 | T1 同音異表記便乗 | T2 β値garble | T3 不規則読み | OTHER |
|---|---|---|---|---|
| L1 | 6 | 0 | 0 | 0 |
| L1+L2 | 6 | 2 | 0 | 0 |
| L1+L3 | 6 | 0 | 0 | 0 |
| L1+L2+L3 | 6 | 2 | 0 | 0 |

### 3c. 増分誤PASSの全列挙(L1+L2+L3。他層はこの部分集合)
| group | tag | scenario | canon | Primary | Secondary | 型 | 層別cat(L1/L1+L2/L1+L3/L1+L2+L3) | 経路 |
|---|---|---|---|---|---|---|---|---|
| N1_150 | 値garble | S_canon | 月のしわ、8,900本超 | 月の詩は8000900本超 | 月のしわ、8,900本超 | T2_β値garble | NG/PASS_W/NG/PASS_W | L2_beta_composite:listen |
| R4R3_extra18 | しわ→詩は(R1、非受理のまま) | P_only | 月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密 | 月の詩は、8900本超！その奥に潜む「岩の上着」の秘密 |  | T1_同音異表記便乗 | PASS_W/PASS_W/PASS_W/PASS_W | L1_v2_pron:primary:A3_value+A2_particle |
| R4R3_extra18 | しわ→詩は(R1、非受理のまま) | PS_same | 月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密 | 月の詩は、8900本超！その奥に潜む「岩の上着」の秘密 | 月の詩は、8900本超！その奥に潜む「岩の上着」の秘密 | T1_同音異表記便乗 | PASS_W/PASS_W/PASS_W/PASS_W | L1_v2_pron:primary:A3_value+A2_particle |
| R4R3_extra18 | しわ→詩は(桁区切り付き) | P_only | 月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密 | 月の詩は、8,900本超！その奥に潜む「岩の上着」の秘密 |  | T1_同音異表記便乗 | PASS_W/PASS_W/PASS_W/PASS_W | L1_v2_pron:primary:A3_value+A2_particle |
| R4R3_extra18 | しわ→詩は(桁区切り付き) | PS_same | 月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密 | 月の詩は、8,900本超！その奥に潜む「岩の上着」の秘密 | 月の詩は、8,900本超！その奥に潜む「岩の上着」の秘密 | T1_同音異表記便乗 | PASS_W/PASS_W/PASS_W/PASS_W | L1_v2_pron:primary:A3_value+A2_particle |
| R4R3_extra18 | 値garble | S_canon | 月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密 | 月のしわ、8000900本超！その奥に潜む「岩の上着」の秘密 | 月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密 | T2_β値garble | NG/PASS_W/NG/PASS_W | L2_beta_composite:listen |
| UC6_U6_同音異表記便乗 | U6_同音異表記便乗 | P_only | 月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密 | 月の死は、8,900本超！その奥に潜む「岩の上着」の秘密 |  | T1_同音異表記便乗 | PASS_W/PASS_W/PASS_W/PASS_W | L1_v2_pron:primary:A3_value+A2_particle |
| UC6_U6_同音異表記便乗 | U6_同音異表記便乗 | PS_same | 月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密 | 月の死は、8,900本超！その奥に潜む「岩の上着」の秘密 | 月の死は、8,900本超！その奥に潜む「岩の上着」の秘密 | T1_同音異表記便乗 | PASS_W/PASS_W/PASS_W/PASS_W | L1_v2_pron:primary:A3_value+A2_particle |

### 3d. 負例の群別 総誤PASS(L0 → L1+L2+L3)
| group | n | L0誤PASS | L1+L2+L3誤PASS |
|---|---|---|---|
| BLIGHT_synthetic | 86 | 15 | 15 |
| L3_NEG | 124 | 47 | 47 |
| N1_150 | 429 | 91 | 92 |
| N3_real30 | 30 | 14 | 14 |
| N3_redraw | 240 | 150 | 150 |
| OPEN333_E4 | 168 | 26 | 26 |
| OPEN333_sweep8 | 63 | 3 | 3 |
| OPEN517_wrongvalue_kana | 471 | 0 | 0 |
| R4R3_extra18 | 54 | 6 | 11 |
| UC6_U1_異なる発音 | 21 | 9 | 9 |
| UC6_U2_異なる数値 | 24 | 0 | 0 |
| UC6_U3_助数詞違い | 24 | 3 | 3 |
| UC6_U4_語句脱落 | 21 | 5 | 5 |
| UC6_U5_意味を変える読み違い | 21 | 5 | 5 |
| UC6_U6_同音異表記便乗 | 27 | 6 | 8 |

### 3e. L1不規則読みガードの効果(Phase 1 M1との差)
- 今日は一日中雨 → 今日はついたち中雨 [P_only]: M1=PASS_W → L1=NG(L0=NG)
- 今日は一日中雨 → 今日はついたち中雨 [PS_same]: M1=PASS_W → L1=NG(L0=NG)
- 今日は一日中雨 → 今日はついたち中雨 [S_canon]: M1=PASS_W → L1=NG(L0=NG)

## 4. L3(読み候補辞書拡張『数量+超』の接尾)の検証
### 4a. 正例 L3_POS(辞書で救済されるべき)と、シナリオ別 層結果
| tag | scenario | L0 | L1 | L1+L2 | L1+L3 | L1+L2+L3 |
|---|---|---|---|---|---|---|
| 月題:超え | PS_same | NG | NG | NG | PASS_W | PASS_W |
| 月題:超え | S_canon | PASS_W | PASS_W | PASS_W | PASS_W | PASS_W |
| 月題:超え | P_only | NG | NG | NG | NG | NG |
| 汎用人:超え | PS_same | NG | NG | NG | PASS_W | PASS_W |
| 汎用人:超え | S_canon | PASS_W | PASS_W | PASS_W | PASS_W | PASS_W |
| 汎用人:超え | P_only | NG | NG | NG | NG | NG |
| 汎用円:超え | PS_same | NG | NG | NG | PASS_W | PASS_W |
| 汎用円:超え | S_canon | PASS_W | PASS_W | PASS_W | PASS_W | PASS_W |
| 汎用円:超え | P_only | NG | NG | NG | NG | NG |
| 月題:越え | PS_same | NG | NG | NG | PASS_W | PASS_W |
| 月題:越え | S_canon | PASS_W | PASS_W | PASS_W | PASS_W | PASS_W |
| 月題:越え | P_only | NG | NG | NG | NG | NG |
| 汎用人:越え | PS_same | NG | NG | NG | PASS_W | PASS_W |
| 汎用人:越え | S_canon | PASS_W | PASS_W | PASS_W | PASS_W | PASS_W |
| 汎用人:越え | P_only | NG | NG | NG | NG | NG |
| 汎用円:越え | PS_same | NG | NG | NG | PASS_W | PASS_W |
| 汎用円:越え | S_canon | PASS_W | PASS_W | PASS_W | PASS_W | PASS_W |
| 汎用円:越え | P_only | NG | NG | NG | NG | NG |
| 月題:こえ | PS_same | NG | NG | NG | PASS_W | PASS_W |
| 月題:こえ | S_canon | PASS_W | PASS_W | PASS_W | PASS_W | PASS_W |
| 月題:こえ | P_only | NG | NG | NG | NG | NG |
| 汎用人:こえ | PS_same | NG | NG | NG | PASS_W | PASS_W |
| 汎用人:こえ | S_canon | PASS_W | PASS_W | PASS_W | PASS_W | PASS_W |
| 汎用人:こえ | P_only | NG | NG | NG | NG | NG |
| 汎用円:こえ | PS_same | NG | NG | NG | PASS_W | PASS_W |
| 汎用円:こえ | S_canon | PASS_W | PASS_W | PASS_W | PASS_W | PASS_W |
| 汎用円:こえ | P_only | NG | NG | NG | NG | NG |
| 月題:詩は+超え(L1+L3併用) | PS_same | NG | NG | NG | PASS_W | PASS_W |
| 月題:詩は+超え(L1+L3併用) | S_canon | PASS_W | PASS_W | PASS_W | PASS_W | PASS_W |
| 月題:詩は+超え(L1+L3併用) | P_only | NG | NG | NG | NG | NG |
| 月題:市は+越え(L1+L3併用) | PS_same | NG | NG | NG | PASS_W | PASS_W |
| 月題:市は+越え(L1+L3併用) | S_canon | PASS_W | PASS_W | PASS_W | PASS_W | PASS_W |
| 月題:市は+越え(L1+L3併用) | P_only | NG | NG | NG | NG | NG |
(P_only=Secondary無し: 発火しない[両engine必須])。S_canon=Secondary:=原稿そのもの[最悪露出]では L0 が既に PASS_W(Production既存のSecondary確認経路)で、L3は変化を与えない。

### 4b. 負例 L3_NEG(L0 vs 各層。増分=0が条件)
L3_NEG 行数=124。増分誤PASS(L0=NG→L1+L3/L1+L2+L3 で非NG)=0/0。
| tag | scenario | L0 | L1+L3 | L1+L2+L3 |
|---|---|---|---|---|
| 値違い:8,800本超え | PS_same | NG | NG | NG |
| 値違い:8,800本超え | S_canon | NG | NG | NG |
| 値違い:890本超え | PS_same | NG | NG | NG |
| 値違い:890本超え | S_canon | NG | NG | NG |
| 値違い:89,000本超え | PS_same | NG | NG | NG |
| 値違い:89,000本超え | S_canon | NG | NG | NG |
| 値違い:9,900本超え | PS_same | NG | NG | NG |
| 値違い:9,900本超え | S_canon | NG | NG | NG |
| 値違い:8,090本超え | PS_same | NG | NG | NG |
| 値違い:8,090本超え | S_canon | NG | NG | NG |
| 助数詞違い:個 | PS_same | NG | NG | NG |
| 助数詞違い:個 | S_canon | NG | NG | NG |
| 助数詞違い:枚 | PS_same | NG | NG | NG |
| 助数詞違い:枚 | S_canon | NG | NG | NG |
| 助数詞違い:人 | PS_same | NG | NG | NG |
| 助数詞違い:人 | S_canon | NG | NG | NG |
| 助数詞違い:円 | PS_same | NG | NG | NG |
| 助数詞違い:円 | S_canon | NG | NG | NG |
| 助数詞違い:冊 | PS_same | NG | NG | NG |
| 助数詞違い:冊 | S_canon | PASS_W | PASS_W | PASS_W |
| 汎用値違い | PS_same | NG | NG | NG |
| 汎用値違い | S_canon | NG | NG | NG |
| 汎用助数詞違い | PS_same | NG | NG | NG |
| 汎用助数詞違い | S_canon | PASS_W | PASS_W | PASS_W |
| 汎用値違い2 | PS_same | NG | NG | NG |
| 汎用値違い2 | S_canon | NG | NG | NG |
| E4/C2同形異音:本長 | PS_same | NG | NG | NG |
| E4/C2同形異音:本長 | S_canon | PASS_W | PASS_W | PASS_W |
| E4/C2同形異音(汎用):人長 | PS_same | PASS | PASS | PASS |
| E4/C2同形異音(汎用):人長 | S_canon | PASS | PASS | PASS |
| E4/C2同形異音:本帳 | PS_same | PASS | PASS | PASS |
| E4/C2同形異音:本帳 | S_canon | PASS | PASS | PASS |
| E4/C2同形異音(汎用):人帳 | PS_same | PASS | PASS | PASS |
| E4/C2同形異音(汎用):人帳 | S_canon | PASS | PASS | PASS |
| E4/C2同形異音:本蝶 | PS_same | PASS | PASS | PASS |
| E4/C2同形異音:本蝶 | S_canon | PASS | PASS | PASS |
| E4/C2同形異音(汎用):人蝶 | PS_same | PASS | PASS | PASS |
| E4/C2同形異音(汎用):人蝶 | S_canon | PASS | PASS | PASS |
| E4/C2同形異音:本調 | PS_same | PASS | PASS | PASS |
| E4/C2同形異音:本調 | S_canon | PASS | PASS | PASS |
| E4/C2同形異音(汎用):人調 | PS_same | PASS | PASS | PASS |
| E4/C2同形異音(汎用):人調 | S_canon | PASS | PASS | PASS |
| E4/C2同形異音:本町 | PS_same | PASS | PASS | PASS |
| E4/C2同形異音:本町 | S_canon | PASS | PASS | PASS |
| E4/C2同形異音(汎用):人町 | PS_same | PASS | PASS | PASS |
| E4/C2同形異音(汎用):人町 | S_canon | PASS | PASS | PASS |
| E4/C2同形異音:本鳥 | PS_same | PASS | PASS | PASS |
| E4/C2同形異音:本鳥 | S_canon | PASS | PASS | PASS |
| E4/C2同形異音(汎用):人鳥 | PS_same | PASS | PASS | PASS |
| E4/C2同形異音(汎用):人鳥 | S_canon | PASS | PASS | PASS |
| 挿入:を | PS_same | NG | NG | NG |
| 挿入:を | S_canon | PASS_W | PASS_W | PASS_W |
| 挿入:は | PS_same | NG | NG | NG |
| 挿入:は | S_canon | PASS_W | PASS_W | PASS_W |
| 脱落:助数詞 | PS_same | NG | NG | NG |
| 脱落:助数詞 | S_canon | PASS_W | PASS_W | PASS_W |
| 脱落:数値 | PS_same | NG | NG | NG |
| 脱落:数値 | S_canon | NG | NG | NG |
| 脱落:末尾 | PS_same | NG | NG | NG |
| 脱落:末尾 | S_canon | PASS_W | PASS_W | PASS_W |
| 脱落:中間 | PS_same | NG | NG | NG |
| 脱落:中間 | S_canon | PASS_W | PASS_W | PASS_W |
| 意味:未満 | PS_same | NG | NG | NG |
| 意味:未満 | S_canon | NG | NG | NG |
| 意味:以上 | PS_same | NG | NG | NG |
| 意味:以上 | S_canon | PASS_W | PASS_W | PASS_W |
| 意味:超えない | PS_same | NG | NG | NG |
| 意味:超えない | S_canon | NG | NG | NG |
| 意味:超えず | PS_same | NG | NG | NG |
| 意味:超えず | S_canon | NG | NG | NG |
| 意味:超える(活用形は辞書対象外) | PS_same | NG | NG | NG |
| 意味:超える(活用形は辞書対象外) | S_canon | PASS_W | PASS_W | PASS_W |
| 同音異表記便乗:しわ→すわ+超え | PS_same | NG | NG | NG |
| 同音異表記便乗:しわ→すわ+超え | S_canon | PASS_W | PASS_W | PASS_W |
| 同音異表記便乗:岩→石+超え | PS_same | NG | NG | NG |
| 同音異表記便乗:岩→石+超え | S_canon | PASS_W | PASS_W | PASS_W |
| 数量に付かない超(超高速) | PS_same | NG | NG | NG |
| 数量に付かない超(超高速) | S_canon | PASS_W | PASS_W | PASS_W |
| 数量に付かない超(超高速2) | PS_same | NG | NG | NG |
| 数量に付かない超(超高速2) | S_canon | PASS_W | PASS_W | PASS_W |
| 片engine:P値違い+S正 | explicit | NG | NG | NG |
| 片engine:P正+S値違い | explicit | NG | NG | NG |
| 片engine:P値garble+S正 | explicit | NG | NG | NG |
| 片engine:P正+S助数詞違い | explicit | NG | NG | NG |
(指示『本長/本帳/本蝶は不受理』: L3の**増分**としては満たす[増分0・test固定]。ただし本帳/本蝶/本調/本町/本鳥・人長…は **L0=Production既存の読み一致で既にPASS**[PS_same]=同音(ちょう)の異表記を既存仕様が受理している基線事実。L3はこれらを変化させない。本長のみ L0もNG[PS_same]。この基線の扱いはFableへ報告事項)。

## 5. L4(判定前ASR再転写)のN3 30wav × 新規4 draw: 誤PASS(PASS+PASS_W)率
対象=N3 30 wav(意図的誤読TTS、真値NEG)。Azure=保存転写(変動0仮定)。『N draw までのいずれかが非NG』のclip数。
| シナリオ | 構成 | N=1 | N=2 | N=3 | N=4 | 順列平均 N=1/2/3/4 |
|---|---|---|---|---|---|---|
| real | L0 | 15/30 | 15/30 | 16/30 | 16/30 | 0.492/0.517/0.525/0.533 |
| real | L1+L2+L3 | 15/30 | 15/30 | 16/30 | 16/30 | 0.492/0.517/0.525/0.533 |
| S_canon | L0 | 22/30 | 23/30 | 25/30 | 25/30 | 0.758/0.800/0.817/0.833 |
| S_canon | L1+L2+L3 | 22/30 | 23/30 | 25/30 | 25/30 | 0.758/0.800/0.817/0.833 |

参考: 保存済みOpenAI転写を第0drawとして加えた場合(N=1..5)
| シナリオ | 構成 | N=1 | N=2 | N=3 | N=4 | N=5 |
|---|---|---|---|---|---|---|
| real | L0 | 14/30 | 15/30 | 15/30 | 16/30 | 16/30 |
| real | L1+L2+L3 | 14/30 | 15/30 | 15/30 | 16/30 | 16/30 |
| S_canon | L0 | 22/30 | 23/30 | 24/30 | 25/30 | 25/30 |
| S_canon | L1+L2+L3 | 22/30 | 23/30 | 24/30 | 25/30 | 25/30 |

(基線: N3の誤PASSの大半はL0でも起きる『表記が同一/等価な誤読』型[Phase 1 §3b、同形異音・助詞・連濁]で、ASRがテキストしか見ないため区別不能。L1+L2+L3はL0に対し増分0。L4は誤PASS率をdraw数に応じて押し上げる: real N=1→3 で +1clip[N3-13]、S_canon[Secondary=原稿の最悪露出]で N=1→3 で +3clip。)
N=1 → N 増加で新たに誤PASSになるclip(real, L1+L2+L3, 新4draw):
- N=2: +0件 
- N=3: +1件 N3-13(M6 同形異音(一日・いちにち)/TTS入力=ついたちじゅうあめだった/新draw=['ついたち中は雨だった。', 'ついたち中は雨だった。', '1日中雨だった。', 'ついたち中は雨だった。']/Azure=一日中は雨だった。)
- N=4: +1件 N3-13(M6 同形異音(一日・いちにち)/TTS入力=ついたちじゅうあめだった/新draw=['ついたち中は雨だった。', 'ついたち中は雨だった。', '1日中雨だった。', 'ついたち中は雨だった。']/Azure=一日中は雨だった。)

L0とL1+L2+L3のN3(新draw)での差(増分): 0 (clip×N組合せ)。

## 6. 残NG・Human Review条件(iv)
### 6a. 層適用後に残るNG(決定対)
- run_ms_03 a1: L1+L2+L3 でNG(p1_value_diff)。draw集合の非NG=2/4。L4[N=3]で解消=True
- run_reselect_01 a3: L1+L2+L3 でNG(secondary_not_accepted)。draw集合の非NG=1/5。L4[N=3]で解消=True
- 原因(RESIDUAL_NG_ANALYSIS_01.md): ms_03 a1=OpenAI数詞崩れ(stored『8000句800』)+TTS読みゆれ『超→こえ』(L3で読みは解消、値はL4/βが必要。L3の発火条件は両engine値一致のため、値崩れdrawでは発火しない)。reselect a3=2engineが『スギノ/Sukino』と一致して原稿と異音=ASR誤認識かTTSの弱い『つ』か**転写のみでは確定不能**(ローカルWhisper 2/2は『月の詩/死』)。
- 機械確定不能の根拠: reselect a3 の決定対では、2つの独立Production engine(OpenAI・Azure)が一致して原稿と異なる音(スギノ)を出し、原稿の音を支持する転写はdrawの偶然(OpenAI 5drawのうち『月野市は』1本)と第三証人(ローカルWhisper、判定不使用)のみ。音声そのものを聞かずに『正常音声がASRに誤認識された』と『TTSが誤読した』は区別できない。

### 6b. Human Review 機械条件案(hr_candidate)
条件(全層NG後、全draw対のうち1対でも満たせば候補): (a)少なくとも片方のengine転写が原稿との値ガードEQUAL かつ全転写に否定差なし (b)値atomを除いた読み(v2モーラ列)の差分が連続1区間・3モーラ以内 (c)原稿に不規則読み数詞なし。**判定(PASS/NG)は変えない**=人間の試聴キューに付ける証拠。judge関数はhr_candidateを参照しない(test固定)。
| 対象 | HR候補 | 差分/証拠 |
|---|---|---|
| 正例 run_ms_03 a1 | True | [['ちょう', 'こえ']] / 月野市は8900本越え。その奥に潜む岩の上着の秘密。 |
| 正例 run_ms_03 a2 | True | [] / 月の死は八千九百本超。その奥に潜む岩の上着の秘密。 |
| 正例 run_ms_03 a3 | True | [['つき', 'すぎ']] / 杉野氏は8900本超。その奥に潜む岩の上着の秘密。 |
| 正例 run_reselect_01 a1 | True | [] / 月野氏は8,900本超。その奥に潜む岩の上着の秘密 |
| 正例 run_reselect_01 a2 | True | [] / 月の詩は八千九百本超。その奥に潜む岩の上着の秘密 |
| 正例 run_reselect_01 a3 | True | [['つき', 'すぎ']] / スギノ市は、八千九百本超、その奥に潜む岩の上着の秘密。 |
| N3負例30wav(全draw対) | 候補6/30 | N3-03, N3-07, N3-08, N3-18, N3-20, N3-30 |

負例text行(L1+L2+L3でもNGのもの)の群別HR候補件数: {"BLIGHT_synthetic|cand": 45, "BLIGHT_synthetic|not": 26, "L3_NEG|cand": 30, "L3_NEG|not": 47, "N1_150|cand": 56, "N1_150|not": 281, "N3_real30|cand": 2, "N3_real30|not": 14, "OPEN333_E4|cand": 8, "OPEN333_E4|not": 134, "OPEN333_sweep8|cand": 40, "OPEN333_sweep8|not": 20, "OPEN517_wrongvalue_kana|cand": 139, "OPEN517_wrongvalue_kana|not": 332, "R4R3_extra18|cand": 11, "R4R3_extra18|not": 32, "UC6_U1_異なる発音|cand": 10, "UC6_U1_異なる発音|not": 2, "UC6_U2_異なる数値|cand": 8, "UC6_U2_異なる数値|not": 16, "UC6_U3_助数詞違い|cand": 5, "UC6_U3_助数詞違い|not": 16, "UC6_U4_語句脱落|cand": 6, "UC6_U4_語句脱落|not": 10, "UC6_U5_意味を変える読み違い|cand": 6, "UC6_U5_意味を変える読み違い|not": 10, "UC6_U6_同音異表記便乗|cand": 6, "UC6_U6_同音異表記便乗|not": 13}
- 読み取り: 6正例は(全draw集合基準で)すべて候補になるが、原稿と1モーラ差のみの負例(U1『異なる発音』など)も候補になる=**HR条件は正誤を分離せず、人間が聞くべき対象を絞る(自動PASSにしない)用途に限る**。候補率が高い群はレビュー負荷の見積に使う。
- 既存HR機構との差分: 既存は `er007_ja_secondary_asr_01.py:759-764`(最終slotでNGのとき human_review_required=True)→ `_log_human_review`(同:42-59、`er007_output/ja_asr_cascade_01/human_review_queue.jsonl`)→ review_lock(`er011_human_review_lock_01`)→ 個別採用(`asm.record_human_approval`、例 `er011_..._audio_03_b1b_individual_approval_and_assemble_01.py:step1`)。(iv)案はこれに**上記3条件の証拠欄を追加するだけ(iv-a: 挙動不変)**、または候補ならTTS再生成上限前に早期にキューへ送る(iv-b: 再生成回数が変わる=承認済みretry仕様の変更でユーザー判断事項)。
- 抜け道の有無: hr_candidateは判定関数から呼ばれずPASS/NGを返さない(test_hr_candidate_never_changes_judgement...)。承認は既存の個別採用(sha単位・ユーザー試聴)のまま=Gateの恒久免除になる経路はない。負例が候補になっても人間が不採用にできる。

## 7. 6合格条件(ユーザー原文§6)への到達度
| 条件 | 到達度 | 根拠 |
|---|---|---|
| 1. 6音声すべて最終判定でPASS | **部分**: clean PASS 0/6。PASS_W(試聴必須) 決定対 L1+L2+L3 で4/6、+L4[N=2]で5/6、+L4[N=3]で6/6 | §1。新方式経由は常にPASS_W(R2/R-1)。『無条件PASS』は構造的に出ない(ユーザー§6『警告付きPASSを無条件PASSと同一視しない』) |
| 2. 既知の実誤読・負例を誤PASSしない | **部分**: 増分誤PASSはPhase 1の3型(T1/T2。T3はL1ガードで0)のみで OTHER=0。回帰0。ただし T1(音素列が原稿と同一=区別不能)とT2(β)は構造的に残る | §3b-3c |
| 3. 『月のしわ』固有でない | **達成** | 辞書層はatom位置から導出(月題固有語なし=test固定)、汎用題(100人超/1,200円超 等)でL3_POS救済・L3_NEG増分0 | 
| 4. X/Y/Zの対象範囲・既存仕様影響 | **達成(評価済み)** | Phase 1 EVAL_UNIFIED_01.md §5(Family×Level×Section)を継承。L1〜L3は既存adapter位置への差替で適用範囲は同一。AdvにJA音声なし |
| 5. retry/fallback/resume/再判定整合 | **部分**: 設計整合は記載、実行検証は未配線のためproto内のみ | L0〜L3は保存転写+wav shaで再判定可能(API 0)。**L4は承認済み仕様『同一音声のASR再試行廃止』と衝突**=ユーザー判断事項。L3発火でSecondary未呼出時はAzure追加呼出が要る |
| 6. 費用・量産単価 | **達成(区間提示)** | §8 |

### Status候補(最終判定はFable): **USER_DECISION_REQUIRED**(VALIDATEDにしない)
- 理由: 条件1が『PASS』でなく『PASS_W(試聴必須)』止まり(clean PASS 0/6)、L4なしでは2本がNG、L4[N=2]で1本・L4[N=3]で0本がNG(保存順シミュレーション。reselect a3のN=3到達確率は超幾何で0.60=確率的)。条件2も同音異表記(T1)とβ最悪露出(T2)を構造的に許容する。これらを許容して『PASS_W+試聴』を合格と見なすか、L4(ASR再試行)の承認済み仕様変更を認めるかは、ユーザーの品質定義に関わる判断。
- REJECTEDにしない理由: 回帰0・OTHER増分0・汎用性達成・費用は軽微。

## 8. 単価(採用時の記事あたり増減)
- L1/L2/L3: 判定ロジックのみ(¥0)。保存Secondary転写を使う場合の追加ASR費は0。Azure追加呼出が要るのは『Primaryだけで受理でき、Secondary未呼出』かつL3/β発火のとき(6音声27draw中 5件)。Azure実測 ¥0.27〜0.31/clip(6秒題)。
- L4: OpenAI再転写の実費は BUDGET_LOG_01.md(120呼出)。1clip(約1.7秒)あたり¥0.01程度(公表単価ベースの上限推定。1回あたり TTS再生成 ¥0.92 の約1%)。L4[N=3]の期待追加呼出(6音声の保存順): run_ms_03 a1=1, run_ms_03 a2=0, run_ms_03 a3=0, run_reselect_01 a1=0, run_reselect_01 a2=0, run_reselect_01 a3=2。
- 再生成削減: 誤NG1件で TTS再生成1回(¥0.65)+ASR2本(¥0.27)≈¥0.92/clip を避けられる(Phase 3実測)。現行の誤NG率は**未確認**(月題6本は6/6がNGだが題が特殊)。区間: 記事あたり削減 ≈ ¥0.92×(回避できた誤NG再生成数 x) − ¥0.3×(L3/βがSecondary未呼出で発火した回数) − ¥0.01×(L4追加呼出数)。x=0なら削減0(追加費のみ)。例示: 月題級のJA題で再生成1〜2回回避なら ¥0.9〜1.8/記事(70円/記事セット目標比 約1〜3%)。記事あたりのx・JA clip数は現行誤NG率データがなく**未確認**。
- 時間(D): 誤NGによる再生成ループ(各TTS+ASR)が1〜2周減る見込み。

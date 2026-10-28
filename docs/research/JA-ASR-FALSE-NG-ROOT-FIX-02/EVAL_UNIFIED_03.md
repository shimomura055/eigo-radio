# EVAL_UNIFIED_03(JA-ASR-FALSE-NG-ROOT-FIX-02 委任_03。eval_unified_03.py の出力から自動生成。API 0)
事前登録=PREREGISTERED_03.md(+補遺§7、評価実行前にcommit済み)。Opus条件Aレビュー=OPUS_REVIEW_01.md(M-1〜M-7/R-1〜R-7全採用)。層版=proto_unified_03 / 規則版=consensus_v1(PREREGISTERED_03)。
Production HEAD 定数: {"JA_SECONDARY_VALUE_EQUIVALENCE_ENABLED": true, "READING_MATCH_FINAL_GATE": true}。Production file sha256(先頭16桁・不変確認): {"er007_ja_asr_validator_01.py": "9a0e104422c8c243", "er007_ja_secondary_asr_01.py": "d3c5565dd91ad10f", "er078_asr_unified_judge_01.py": "c3e7c2566f5bb16d", "er078_asr_value_guard_01.py": "f3fd435cfc408637"}。
NEG集合(Phase 1/2と同一): n=1439 sha256=d55f24e239d3eb024951c01e57a8d186d9cd6a8ebf979c6470399b5cea2405dd(事前登録値とassert一致)。L0とPhase 1 M0の行ごと一致: 比較1706行・不一致0。
**区分(M-2)**: PASS=Production clean PASS / PASS_W(既存)=Productionの警告付きPASS / PASS_W(新方式)=新層[v2発音救済・β・別表L3・合意再試行]経由=専用warning `JA_NEWLAYER_*` 付き・常に試聴リスト別枠(APPROVED_EQUIVALENCE_BASES非登録) / HR=再試行発火後の早期HR(エンジン間の内容矛盾のみが根拠、PASSにしない) / NG。
**主設定=R-1 ON**(PREREGISTERED_03どおり)。R-1 OFF(=Opusの『4/6』想定、Phase 2のv2規則相当)を全表で併記する。R-1は『ASR側差分span内の漢字1字でも読み候補が2つ以上あれば発音救済しない』検査(M-2/R-1、Opus推奨)。

## 0. 要旨(事実のみ。Statusは§12の候補)
- 6音声の決定対(記録済みOpenAI×Azure)の機械判定: **R-1 ON 0/6 が PASS系**、**R-1 OFF 4/6**(いずれもPASS_W(新方式)または既存PASS_W。clean PASSは0)。残りは R-1 OFF でも ms_03 a1・reselect a3 の2本が NG のまま(Opus予測どおり)。
- ASR再試行(合意規則)は6本に**新たなPASSを1本も足さない**(§3、再試行起因PASS 0)。best-of-N(参考)は足す(§3、N3負例で再試行起因の誤PASSも出る=§5)。
- 負例の増分誤PASS: R-1 ON は T2(β最悪露出)1件のみ、R-1 OFF は T1 6件+T2 2件(§4)。回帰0。
- 合意規則のN3負例での再試行起因誤PASSは0(BoNは出る)。ただし分母が小さい(§5の上限を参照)。

## 1. 6音声×層: 最終Gate結果(決定対=記録済みOpenAI転写 × 当該wavのAzure転写。合意再試行は記録順[first=記録済み、追加=記録順])
### 1A. R-1 ON(主設定)
| 音声 | L0 | L1 | L1+L2 | L1+L2+L3 | +合意N=2 | +合意N=3 | HR候補(最終NGのとき) |
|---|---|---|---|---|---|---|---|
| run_ms_03 a1 | NG:p1_value_diff | NG:p1_value_diff | NG:p1_value_diff | NG:p1_value_diff | NG(追加draw1本) | NG(追加draw2本) | あり |
| run_ms_03 a2 | NG:secondary_not_accepted | NG:secondary_not_accepted | NG:secondary_not_accepted | NG:secondary_not_accepted | NG(追加draw1本) | NG(追加draw2本) | あり |
| run_ms_03 a3 | NG:p1_value_diff | NG:p1_value_diff | NG:p1_value_diff | NG:p1_value_diff | NG(追加draw1本) | NG(追加draw2本) | あり |
| run_reselect_01 a1 | NG:secondary_not_accepted | NG:secondary_not_accepted | NG:secondary_not_accepted | NG:secondary_not_accepted | NG(追加draw1本) | NG(追加draw2本) | あり |
| run_reselect_01 a2 | NG:secondary_not_accepted | NG:secondary_not_accepted | NG:secondary_not_accepted | NG:secondary_not_accepted | NG(追加draw1本) | NG(追加draw2本) | あり |
| run_reselect_01 a3 | NG:secondary_not_accepted | NG:secondary_not_accepted | NG:secondary_not_accepted | NG:secondary_not_accepted | NG(追加draw1本) | NG(追加draw2本) | あり |

### 1B. R-1 OFF(参考=Opus想定)
| 音声 | L0 | L1(R1off) | L1+L2+L3(R1off) | +合意N=2 | +合意N=3 | HR候補(最終NGのとき) |
|---|---|---|---|---|---|---|
| run_ms_03 a1 | NG:p1_value_diff | NG:p1_value_diff | NG:p1_value_diff | NG(追加draw1本) | NG(追加draw2本) | あり |
| run_ms_03 a2 | NG:secondary_not_accepted | PASS_W(新方式):L1_v2_pron:primary:A3_value+A2_particle | PASS_W(新方式):L1_v2_pron:primary:A3_value+A2_particle | PASS_W(新方式):L1_v2_pron:primary:A3_value+A2_particle | PASS_W(新方式):L1_v2_pron:primary:A3_value+A2_particle | - |
| run_ms_03 a3 | NG:p1_value_diff | NG:p1_value_diff | PASS_W(新方式):L2_beta_composite:listen | PASS_W(新方式):L2_beta_composite:listen | PASS_W(新方式):L2_beta_composite:listen | - |
| run_reselect_01 a1 | NG:secondary_not_accepted | PASS_W(新方式):L1_v2_pron:primary:A3_value+A2_particle | PASS_W(新方式):L1_v2_pron:primary:A3_value+A2_particle | PASS_W(新方式):L1_v2_pron:primary:A3_value+A2_particle | PASS_W(新方式):L1_v2_pron:primary:A3_value+A2_particle | - |
| run_reselect_01 a2 | NG:secondary_not_accepted | PASS_W(新方式):L1_v2_pron:primary:A3_value+A2_particle | PASS_W(新方式):L1_v2_pron:primary:A3_value+A2_particle | PASS_W(新方式):L1_v2_pron:primary:A3_value+A2_particle | PASS_W(新方式):L1_v2_pron:primary:A3_value+A2_particle | - |
| run_reselect_01 a3 | NG:secondary_not_accepted | NG:secondary_not_accepted | NG:secondary_not_accepted | NG(追加draw1本) | HR:mixed_evidence_content_contradiction(追加draw2本) | あり |

### 1a. 決定対の転写(OpenAI=記録時、Azure=当該wav)と判定の具体的条件
| 音声 | OpenAI(stored) | Azure | R-1 OFF時の決め手 | R-1 ON時の決め手 |
|---|---|---|---|---|
| run_ms_03 a1 | 月野詩は8000句800本超え。その奥に潜む岩の上着の秘密。 | 月野市は8900本越え。その奥に潜む岩の上着の秘密。 | NG:p1_value_diff | NG:p1_value_diff + R-1:- |
| run_ms_03 a2 | 月の死は八千九百本超。その奥に潜む岩の上着の秘密。 | 月の詩は8900本超。その奥に潜む岩の上着の秘密。 | PASS_W(新方式):L1_v2_pron:primary:A3_value+A2_particle | NG:secondary_not_accepted + R-1:blocked |
| run_ms_03 a3 | 月の氏は8000900本超。その奥に潜む岩の上着の秘密。 | 杉野氏は8900本超。その奥に潜む岩の上着の秘密。 | PASS_W(新方式):L2_beta_composite:listen | NG:p1_value_diff + R-1:blocked |
| run_reselect_01 a1 | 月野氏は8,900本超。その奥に潜む岩の上着の秘密 | 月の詩は8900本ちょ。その奥に潜む岩の上着の秘密。 | PASS_W(新方式):L1_v2_pron:primary:A3_value+A2_particle | NG:secondary_not_accepted + R-1:blocked |
| run_reselect_01 a2 | 月の詩は八千九百本超。その奥に潜む岩の上着の秘密 | 月の詩は8900本ちょうその奥に潜む岩の上着の秘密。 | PASS_W(新方式):L1_v2_pron:primary:A3_value+A2_particle | NG:secondary_not_accepted + R-1:blocked |
| run_reselect_01 a3 | スギノ市は、八千九百本超、その奥に潜む岩の上着の秘密。 | Sukino氏は8900本超。その奥に潜む岩の上着の秘密。 | NG:secondary_not_accepted | NG:secondary_not_accepted + R-1:- |

### 1b. R-6: Phase 2の表記との差(両方を正直に併記)
| 音声 | Phase 2(L1+L2+L3+L4 best-of-N)の記載 | 今回(合意規則+M-5別表、R-1 OFF=Phase 2相当のv2規則) | 今回(R-1 ON=主設定) |
|---|---|---|---|
| run_ms_03 a1 | N=2でPASS_W | NG | NG |
| run_ms_03 a2 | PASS_W | PASS_W(新方式) | NG |
| run_ms_03 a3 | PASS_W | PASS_W(新方式) | NG |
| run_reselect_01 a1 | PASS_W | PASS_W(新方式) | NG |
| run_reselect_01 a2 | PASS_W | PASS_W(新方式) | NG |
| run_reselect_01 a3 | N=3でPASS_W(確率0.60) | HR(mixed_evidence_content_contradiction) | NG |
Phase 2の『(ii)併用で5〜6/6』は best-of-N の釣り(多数派の反証を捨てて少数派drawを採る)を含み、合意規則(M-3)では 4/6(R-1 OFF時)+NG/HR 2 に下がる(R-6)。

## 2. 全draw対(OpenAI全draw × Azure[0]): 層別 PASS系/NG の件数
| 音声 | draw数 | L0 | L1 | L1(R1off) | L1+L2 | L1+L2+L3 | L1+L2+L3(R1off) |
|---|---|---|---|---|---|---|---|
| run_ms_03 a1 | 4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| run_ms_03 a2 | 4 | 0/4 | 0/4 | 1/4 | 0/4 | 0/4 | 1/4 |
| run_ms_03 a3 | 4 | 0/4 | 0/4 | 1/4 | 0/4 | 0/4 | 2/4 |
| run_reselect_01 a1 | 5 | 0/5 | 0/5 | 3/5 | 0/5 | 0/5 | 3/5 |
| run_reselect_01 a2 | 5 | 0/5 | 0/5 | 1/5 | 0/5 | 0/5 | 4/5 |
| run_reselect_01 a3 | 5 | 0/5 | 0/5 | 1/5 | 0/5 | 0/5 | 1/5 |
| 合計 | 27 | 0/27 | 0/27 | 7/27 | 0/27 | 0/27 | 11/27 |

## 3. ASR再試行: 合意規則(主) vs best-of-N(参考)。全(first, 追加draw部分集合)組合せの等重み平均(出た順に依存しない)
セル=『PASS系 件数/組合せ数(率) HR件数 NG件数』。N=1は再試行なし。BoN列=best-of-N(参考、矛盾無視)のPASS系率。
### 3A. R-1 ON(主設定)
| 音声 | N=1 | 合意N=2 | 合意N=3 | BoN N=2 | BoN N=3 | 合意の再試行起因PASS(N=2/3) | BoNの再試行起因PASS(N=2/3) |
|---|---|---|---|---|---|---|---|
| run_ms_03 a1 | 0/4(0%) HR0 NG4 | 0/12(0%) HR0 NG12 | 0/12(0%) HR0 NG12 | 0/12(0%) | 0/12(0%) | 0/0 | 0/0 |
| run_ms_03 a2 | 0/4(0%) HR0 NG4 | 0/12(0%) HR0 NG12 | 0/12(0%) HR0 NG12 | 0/12(0%) | 0/12(0%) | 0/0 | 0/0 |
| run_ms_03 a3 | 0/4(0%) HR0 NG4 | 0/12(0%) HR0 NG12 | 0/12(0%) HR0 NG12 | 0/12(0%) | 0/12(0%) | 0/0 | 0/0 |
| run_reselect_01 a1 | 0/5(0%) HR0 NG5 | 0/20(0%) HR0 NG20 | 0/30(0%) HR0 NG30 | 0/20(0%) | 0/30(0%) | 0/0 | 0/0 |
| run_reselect_01 a2 | 0/5(0%) HR0 NG5 | 0/20(0%) HR0 NG20 | 0/30(0%) HR0 NG30 | 0/20(0%) | 0/30(0%) | 0/0 | 0/0 |
| run_reselect_01 a3 | 0/5(0%) HR0 NG5 | 0/20(0%) HR0 NG20 | 0/30(0%) HR0 NG30 | 0/20(0%) | 0/30(0%) | 0/0 | 0/0 |

### 3B. R-1 OFF
| 音声 | N=1 | 合意N=2 | 合意N=3 | BoN N=2 | BoN N=3 | 合意の再試行起因PASS(N=2/3) | BoNの再試行起因PASS(N=2/3) |
|---|---|---|---|---|---|---|---|
| run_ms_03 a1 | 0/4(0%) HR0 NG4 | 0/12(0%) HR0 NG12 | 0/12(0%) HR0 NG12 | 0/12(0%) | 0/12(0%) | 0/0 | 0/0 |
| run_ms_03 a2 | 1/4(25%) HR0 NG3 | 3/12(25%) HR3 NG6 | 3/12(25%) HR6 NG3 | 6/12(50%) | 9/12(75%) | 0/0 | 3/6 |
| run_ms_03 a3 | 2/4(50%) HR0 NG2 | 6/12(50%) HR0 NG6 | 6/12(50%) HR0 NG6 | 10/12(83%) | 12/12(100%) | 0/0 | 4/6 |
| run_reselect_01 a1 | 3/5(60%) HR0 NG2 | 12/20(60%) HR3 NG5 | 18/30(60%) HR6 NG6 | 18/20(90%) | 30/30(100%) | 0/0 | 6/12 |
| run_reselect_01 a2 | 4/5(80%) HR0 NG1 | 16/20(80%) HR4 NG0 | 24/30(80%) HR6 NG0 | 20/20(100%) | 30/30(100%) | 0/0 | 4/6 |
| run_reselect_01 a3 | 1/5(20%) HR0 NG4 | 4/20(20%) HR4 NG12 | 6/30(20%) HR12 NG12 | 8/20(40%) | 18/30(60%) | 0/0 | 4/12 |

読み取り: 合意規則は『N=1でNGだった組合せ』をPASSにする(再試行起因PASS)ことが**ない**(全音声で0)。追加drawで非NGが見つかっても、他のdrawに値以外の内容食い違い(例 reselect a3 の『スギノ』)があるため HR に回る。best-of-N は同じ組合せをPASS系にする(列『BoNの再試行起因PASS』)=Opusの指摘した釣りが実データで起きる。

### 3a. reselect a3 の釣り事例(R-1 OFF): どのdrawが非NGで、どのdrawが矛盾か
- draws: [0] スギノ市は、八千九百本超、その奥に潜む岩の上着の秘密。 / [1] 杉の市は、8000坪のその奥に潜む岩の上着の秘密。 / [2] 月野市は、八千九百本超。その奥に潜む岩の上着の秘密。 / [3] 月の死は、発生900本超。その奥に潜む岩の上着の秘密。 / [4] 月野氏は、発生900本超。その奥に潜む岩の上着の秘密。
- Azure: Sukino氏は8900本超。その奥に潜む岩の上着の秘密。
- N=3組合せ 30件中 HR=12・PASS系=6(first=月野市のdrawの組合せのみ。再試行なしで単独PASS)・NG=12。BoNなら PASS系 18/30。

## 4. 負例・対照の誤PASS(コーパス=Phase 1/2と同一1439行+L3_NEG+N3_redraw。PASS系=PASS/PASS_W(既存)/PASS_W(新方式))
NEG行数=1803。増分=L0がNGで当該構成がPASS系。回帰=L0がPASS系で当該構成がNG(全truth)。
| 構成 | 総誤PASS | 増分誤PASS | T1同音異表記 | T2β最悪露出 | T3不規則読み | OTHER | 回帰 |
|---|---|---|---|---|---|---|---|
| L0 | 380 | 0 | 0 | 0 | 0 | 0 | 0 |
| L1 | 380 | 0 | 0 | 0 | 0 | 0 | 0 |
| L1(R1off) | 386 | 6 | 6 | 0 | 0 | 0 | 0 |
| L1+L2 | 381 | 1 | 0 | 1 | 0 | 0 | 0 |
| L1+L2+L3 | 381 | 1 | 0 | 1 | 0 | 0 | 0 |
| L1+L2+L3(R1off) | 388 | 8 | 6 | 2 | 0 | 0 | 0 |

**R-3(事後再分類の明記)**: 事前登録(PREREGISTERED_01/02)では『増分誤PASS』を型に関わらず全て誤PASSとして数えた(Phase 1 M4=増分11[T1 6+T2 2+T3 3]、Phase 2 L1+L2+L3=増分8[T1 6+T2 2、T3はL1ガードで0])。T1(音素列が原稿と同一=ASRテキストから区別不能)を『by-design』と分類し直したのは**事後**である。今回の数字は、事前登録どおりの数え方(全増分=誤PASS)で: R-1 OFF=8(Phase 2と一致)、R-1 ON=1。T1を区別不能としてby-design扱いにした場合の『設計外増分』は R-1 OFF=2(T2のみ)、R-1 ON=1(T2のみ)。

### 4a. 増分誤PASSの全列挙(L1+L2+L3)
| 型 | 群 | シナリオ | 原稿 | Primary | Secondary | 経路 |
|---|---|---|---|---|---|---|
| T2 | R4R3_extra18 | S_canon | 月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密 | 月のしわ、8000900本超！その奥に潜む「岩の上着」の秘密 | 月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密 | L2_beta_composite:listen |

### 4a. 増分誤PASSの全列挙(L1+L2+L3(R1off))
| 型 | 群 | シナリオ | 原稿 | Primary | Secondary | 経路 |
|---|---|---|---|---|---|---|
| T2 | N1_150 | S_canon | 月のしわ、8,900本超 | 月の詩は8000900本超 | 月のしわ、8,900本超 | L2_beta_composite:listen |
| T1 | R4R3_extra18 | P_only | 月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密 | 月の詩は、8900本超！その奥に潜む「岩の上着」の秘密 | - | L1_v2_pron:primary:A3_value+A2_particle |
| T1 | R4R3_extra18 | PS_same | 月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密 | 月の詩は、8900本超！その奥に潜む「岩の上着」の秘密 | 月の詩は、8900本超！その奥に潜む「岩の上着」の秘密 | L1_v2_pron:primary:A3_value+A2_particle |
| T1 | R4R3_extra18 | P_only | 月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密 | 月の詩は、8,900本超！その奥に潜む「岩の上着」の秘密 | - | L1_v2_pron:primary:A3_value+A2_particle |
| T1 | R4R3_extra18 | PS_same | 月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密 | 月の詩は、8,900本超！その奥に潜む「岩の上着」の秘密 | 月の詩は、8,900本超！その奥に潜む「岩の上着」の秘密 | L1_v2_pron:primary:A3_value+A2_particle |
| T2 | R4R3_extra18 | S_canon | 月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密 | 月のしわ、8000900本超！その奥に潜む「岩の上着」の秘密 | 月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密 | L2_beta_composite:listen |
| T1 | UC6_U6_同音異表記便乗 | P_only | 月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密 | 月の死は、8,900本超！その奥に潜む「岩の上着」の秘密 | - | L1_v2_pron:primary:A3_value+A2_particle |
| T1 | UC6_U6_同音異表記便乗 | PS_same | 月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密 | 月の死は、8,900本超！その奥に潜む「岩の上着」の秘密 | 月の死は、8,900本超！その奥に潜む「岩の上着」の秘密 | L1_v2_pron:primary:A3_value+A2_particle |

### 4b. 対照(POS 正例のコーパス行・UNL 真値不明)のPASS系件数
| 構成 | POS行(213) PASS系 | うちL0に対する増分 | UNL行(87) PASS系 |
|---|---|---|---|
| L0 | 159 | +0 | 32 |
| L1 | 161 | +2 | 32 |
| L1(R1off) | 161 | +2 | 35 |
| L1+L2 | 161 | +2 | 32 |
| L1+L2+L3 | 170 | +11 | 32 |
| L1+L2+L3(R1off) | 170 | +11 | 35 |

### 4c. 負例の群別 総誤PASS(L0 → 主設定 → R-1 OFF)
| group | n | L0 | L1+L2+L3 | L1+L2+L3(R1off) |
|---|---|---|---|---|
| BLIGHT_synthetic | 86 | 15 | 15 | 15 |
| L3_NEG | 124 | 47 | 47 | 47 |
| N1_150 | 429 | 91 | 91 | 92 |
| N3_real30 | 30 | 14 | 14 | 14 |
| N3_redraw | 240 | 150 | 150 | 150 |
| OPEN333_E4 | 168 | 26 | 26 | 26 |
| OPEN333_sweep8 | 63 | 3 | 3 | 3 |
| OPEN517_wrongvalue_kana | 471 | 0 | 0 | 0 |
| R4R3_extra18 | 54 | 6 | 7 | 11 |
| UC6_U1_異なる発音 | 21 | 9 | 9 | 9 |
| UC6_U2_異なる数値 | 24 | 0 | 0 | 0 |
| UC6_U3_助数詞違い | 24 | 3 | 3 | 3 |
| UC6_U4_語句脱落 | 21 | 5 | 5 | 5 |
| UC6_U5_意味を変える読み違い | 21 | 5 | 5 | 5 |
| UC6_U6_同音異表記便乗 | 27 | 6 | 6 | 8 |

## 5. N3負例(30 wav、意図的誤読TTS=真値NEG)× 5 draw(記録済み1+新4)での再試行の誤PASS
Azure=保存転写(real)、またはSecondary=原稿そのもの(S_canon=最悪露出)。セルは『PASS系率(組合せ平均)』。再試行起因=同じfirst drawでN=1はNGなのにN=2/3の合意でPASS系になった組合せ。
| シナリオ | 構成 | N=1 PASS系率 | 合意N=2 | 合意N=3 | BoN N=2 | BoN N=3 | 再試行発火組合せ(N=2/3) | 合意の再試行起因PASS(N=2/3) | BoNの再試行起因PASS(N=2/3) | 早期HR組合せ(N=2/3) |
|---|---|---|---|---|---|---|---|---|---|---|
| real | L0 | 73/150(49%) | 292/600(49%) | 438/900(49%) | 306/600(51%) | 468/900(52%) | 204/306 | 0/0 | 14/30 | 10/18 |
| real | L1+L2+L3 | 73/150(49%) | 292/600(49%) | 438/900(49%) | 306/600(51%) | 468/900(52%) | 188/282 | 0/0 | 14/30 | 10/18 |
| real | L1+L2+L3(R1off) | 73/150(49%) | 292/600(49%) | 438/900(49%) | 306/600(51%) | 468/900(52%) | 188/282 | 0/0 | 14/30 | 10/18 |
| S_canon | L0 | 113/150(75%) | 452/600(75%) | 678/900(75%) | 478/600(80%) | 735/900(82%) | 64/96 | 0/0 | 26/57 | 6/12 |
| S_canon | L1+L2+L3 | 113/150(75%) | 452/600(75%) | 678/900(75%) | 478/600(80%) | 735/900(82%) | 52/78 | 0/0 | 26/57 | 6/12 |
| S_canon | L1+L2+L3(R1off) | 113/150(75%) | 452/600(75%) | 678/900(75%) | 478/600(80%) | 735/900(82%) | 52/78 | 0/0 | 26/57 | 6/12 |

### 5a. 再試行起因誤PASS 0 の統計的意味
- real / L1+L2+L3: 再試行が1回でも発火したclip=13/30 → clip単位の誤PASS 0/13の95%上限(Clopper-Pearson)=20.6%。組合せ単位(従属)は 0/470 で0.64%だが、同一clipのdraw間は独立でないため参考値。
- real / L1+L2+L3(R1off): 再試行が1回でも発火したclip=13/30 → clip単位の誤PASS 0/13の95%上限(Clopper-Pearson)=20.6%。組合せ単位(従属)は 0/470 で0.64%だが、同一clipのdraw間は独立でないため参考値。
- S_canon / L1+L2+L3: 再試行が1回でも発火したclip=4/30 → clip単位の誤PASS 0/4の95%上限(Clopper-Pearson)=52.7%。組合せ単位(従属)は 0/130 で2.28%だが、同一clipのdraw間は独立でないため参考値。
- S_canon / L1+L2+L3(R1off): 再試行が1回でも発火したclip=4/30 → clip単位の誤PASS 0/4の95%上限(Clopper-Pearson)=52.7%。組合せ単位(従属)は 0/130 で2.28%だが、同一clipのdraw間は独立でないため参考値。
- **限界**: 真値NEGとして使える保存wavはN3の30本(うちL0でNGの約16本)のみ。95%上限は大きい誤PASS増加しか否定できない(Opus指摘どおり)。人間NG判定済みの実誤読wavの台帳は他に存在せず(PREREGISTERED_03 §3の探索範囲)、母集団拡大は既知誤値TTS入力の追加生成=TTS呼出が必要で本委任の範囲外(判断候補)。

### 5b. N3でBoN(参考)が釣る例(N=3、real、R-1 OFF構成)
- N3-13 (M6 同形異音(一日・いちにち), TTS入力=`ついたちじゅうあめだった`): BoN再試行起因PASS 12組合せ。合意規則では0。
- N3-21 (M6 不規則読み誤読(三日), TTS入力=`さんにち待った`): BoN再試行起因PASS 12組合せ。合意規則では0。
- N3-24 (M6 助詞誤読(町へ), TTS入力=`まちヘ行く`): BoN再試行起因PASS 6組合せ。合意規則では0。

## 6. draw独立性と時刻依存(P-5)
| 対象 | wav数 | draw/wav | 異なる転写数(平均) | 同一転写のみ(全draw同一)のwav |
|---|---|---|---|---|
| N3(記録済み1+新4) | 30 | 5 | 1.87 | 17 |
| N3(新4 drawのみ) | 30 | 4 | 1.73 | 17 |
| 6音声 | 6 | 4〜5 | 3.67 | 0 |
| 拡張4wav | 4 | 5 | 3.25 | 0 |
- 時刻依存の検査(N3): 記録済み(Phase 3、別日の呼出)の転写が新4 drawのいずれかと一致するclip=26/30(87%)、新draw1本が他の新drawのいずれかと一致する率=95/120(79%)。差は8ポイントで、記録済みが新draw同士より特に食い違う(=モデル更新等の時刻依存)証拠は無い(n=30、断定はしない)。draw単位の揺らぎが主。新draw取得時刻: 2026-10-28T20:32:35+0900 〜 2026-10-28T20:33:53+0900(約80秒内)。記録済みdrawの呼出時刻はusage_logに無い。
- 6音声のdraw多様性(異なる転写数/draw数): run_ms_03 a1: 3/4, run_ms_03 a2: 2/4, run_ms_03 a3: 4/4, run_reselect_01 a1: 5/5, run_reselect_01 a2: 3/5, run_reselect_01 a3: 5/5。
- 参考(Opus指摘): ms_03 a2 は再転写3本が同一(月の島は千九百本超)=draw独立性は限定的。再現性メタデータ(モデルID・時刻・draw順)は redraw_03.json / n3_redraw_02.json に保存。

## 7. 正例拡張4wav(人間承認済みの日本語a2 attempt、新規4 draw+記録済み1)とY/Preview型
| wav | 長さ | Azure保存転写 | draw別 判定(L0 / L1+L2+L3 / L1+L2+L3(R1off)) |
|---|---|---|---|
| middle_east_yemen_saudi__run_mey_02/comment_2 (sha 8a05886bd20d0c27、同sha: -) | 13.72s | あり | stored:NG/NG/NG ; draw1:NG/NG/NG ; draw2:NG/NG/NG ; draw3:NG/NG/NG ; draw4:NG/NG/NG |
| run_e2e_02/comment_1 (sha f82318854523220c、同sha: -) | 18.8s | なし(P_only) | stored:PASS_W(既存)/PASS_W(既存)/PASS_W(既存) ; draw1:PASS_W(既存)/PASS_W(既存)/PASS_W(既存) ; draw2:PASS_W(既存)/PASS_W(既存)/PASS_W(既存) ; draw3:PASS_W(既存)/PASS_W(既存)/PASS_W(既存) ; draw4:PASS_W(既存)/PASS_W(既存)/PASS_W(既存) |
| run_01/preview (sha 6986099231eed083、同sha: run_hrguard_ev_02_mock/preview,run_voice_puck_ev_01/preview,run_ev_01/preview) | 14.03s | なし(P_only) | stored:NG/NG/NG ; draw1:NG/NG/NG ; draw2:NG/NG/NG ; draw3:NG/NG/NG ; draw4:PASS/PASS/PASS |
| run_gpg5_y_01/preview (sha ac3f74670b039bfb、同sha: run_gpg5_y_01_s23f/preview,run_style_fix_01/preview) | 15.72s | なし(P_only) | stored:NG/NG/NG ; draw1:NG/NG/NG ; draw2:NG/NG/NG ; draw3:NG/NG/NG ; draw4:NG/NG/NG |

- **middle_east_yemen_saudi__run_mey_02/comment_2**: 原稿 `ここまでで、タイフーン機の任務はサウジの防空で、フーシ派を攻撃しないと分かりました。では、発表にある空中給油の支援は、こ…` / draws: stored=`ここまでで、台風期の任務はサウジの防空でフーシ派を攻撃しないとわかりました。では…` | draw1=`ここまでで、台風機の任務はサウジの防空でフーシ派を攻撃しないとわかりました。では…` | draw2=`ここまでで、台風期の任務はサウジの防空でフーシ派を攻撃しないとわかりました。では…` / 合意N=3(R-1 OFF)分布=0/30(0%) HR0 NG30。
- **run_e2e_02/comment_1**: 原稿 `メロスは、恐怖から人を殺し、話す機会も与えない支配者を責め、死刑を命じられます。妹の結婚式に出るため三日間の猶予を求め、…` / draws: stored=`メロスは恐怖から人を殺し、話す機会も与えない支配者を責め、死刑を命じられます。妹…` | draw1=`メロスは恐怖から人を殺し、話す機会も与えない支配者を責め、死刑を命じられます。妹…` | draw2=`メロスは恐怖から人を殺し、話す機会も与えない支配者を責め、死刑を命じられます。妹…` / 合意N=3(R-1 OFF)分布=30/30(100%) HR0 NG0。
- **run_01/preview**: 原稿 `荷物の再配達では、受け取る側が時間を指定しても、思いどおりに届かないことがあります。配達する人と受け取る人の経験を通して…` / draws: stored=`荷物の再配達では、受け取る側が時間を指定しても思い通りに届かないことがあります。…` | draw1=`荷物の再配達では、受け取る側が時間を指定しても、思い通りに届かないことがあります…` | draw2=`荷物の再配達では、受け取る側が時間を指定しても思い通りに届かないことがあります。…` / 合意N=3(R-1 OFF)分布=6/30(20%) HR0 NG24。
- **run_gpg5_y_01/preview**: 原稿 `荷物の再配達では、受け取る側が時間を指定しても、思いどおりに届かないことがあります。配達する人と受け取る人の経験を通して…` / draws: stored=`荷物の再配達では、受け取る側が時間を指定しても、思い通りに届かないことがあります…` | draw1=`荷物の再配達では、受け取る側が時間を指定しても思い通りに届かないことがあります。…` | draw2=`荷物の再配達では、受け取る側が時間を指定しても、思い通りに届かないことがあります…` / 合意N=3(R-1 OFF)分布=0/30(0%) HR0 NG30。

### 7a. Y/Preview型『思いどおり↔思い通り』: 案R(i)は効くか(P-6)
- run_01/preview stored: Production分類=`ASR_VALIDATION_UNCERTAIN`(理由: (JA ASR Variant Layer/Candidate B)形態素解析ベースの読みが濁点/半濁点の有無を除き一致)。v2判定 equal=False why=`not_tcm`。最終(Secondary未保存のstub): L0=NG / L1+L2+L3=NG。
- run_gpg5_y_01/preview stored: Production分類=`ASR_VALIDATION_UNCERTAIN`(理由: (JA ASR Variant Layer/Candidate B)形態素解析ベースの読みが濁点/半濁点の有無を除き一致)。v2判定 equal=False why=`not_tcm`。最終(Secondary未保存のstub): L0=NG / L1+L2+L3=NG。
- 結論: Production既存のVariant Layerは『濁点の有無を除き読みが一致』をCascade対象(ASR_VALIDATION_UNCERTAIN)に分類済みで、案R(i)のv2は**そもそも発火しない**(not_tcm)。判定は Secondary(Azure)が原稿と同じ『思いどおり』を返すか次第(返せば既存の secondary_confirmed=PASS_W(既存)、返さなければ NG_BOTH)。Y/Previewの保存attemptにはAzure転写が無く、ここでは実結果を再現できない(Azure 0)。つまり案R(i)はこの型には**効かない/不要**で、救うには清濁を許容する比較(連濁)が要る=er008冒頭の『ころ/ごろ』問題と同じ危険があるため**別ID・別Opusレビュー**(OPEN新規(a)、分類=修正へ進む)。月題以外の実在誤NGで『案R(i)が効かない』ことの実証(R-5、検証のみ本Phase)。run_01 previewは5 draw中1本(draw4)が原稿と同表記(思いどおり)でProduction既存のPASSになった=draw揺らぎの実例。
- mey_02 comment_2(固有名詞タイフーン機↔台風機/台風期): 全draw・全構成でNG(OOV同音。案Rの対象外=OPEN-498/PN系)。Z melos comment_1(三日間↔3日間): M-1ガード(不規則読み)でL1が不適用、L0で既にPASS_W(既存、`JA_NUMERIC_IRREGULAR_READING`警告)。

## 8. M-5 別表L3(送り仮名省略形の訓読み)の検証
- L3_POS L0: PS_same=NG:11, P_only=NG:11, S_canon=PASS_W(既存):11
- L3_POS L1+L2+L3: PS_same=NG:2, PS_same=PASS_W(新方式):9, P_only=NG:11, S_canon=PASS_W(既存):11
- L3_NEG L0: PS_same=NG:29, PS_same=PASS:11, P_only=NG:29, P_only=PASS:11, S_canon=NG:15, S_canon=PASS:11, S_canon=PASS_W(既存):14, explicit=NG:4
- L3_NEG L1+L2+L3: PS_same=NG:29, PS_same=PASS:11, P_only=NG:29, P_only=PASS:11, S_canon=NG:15, S_canon=PASS:11, S_canon=PASS_W(既存):14, explicit=NG:4
- L3_NEG 増分誤PASS=0(目標0)。L3_POS PS_same(両engine揃い)で救済: 9/11。救済されない2件=『月野詩は+超え』『月野市は+越え』(発音同一との併用は残差0文字でないため不可。Phase 2のL3より意図的に狭い)。S_canon(Secondary=原稿)はL0が既にPASS_W(既存)でL3は寄与なし。P_only(Secondary無し)は発火しない。
- 汎用辞書 `er008_asr_variant_hardening_15_ja_kanji_readings.py` は不変(test: `reading_candidates_for_span('超')` に『こえ』が無い)。別表は `proto_unified_03.KUNYOMI_OKURIGANA` のみ。

## 9. ガードの効果(M-1/M-6/R-1/R-2)
- M-6(E3/E4非空で全新層不適用): コーパス2103行中 34行がブロック(E3由来。E4由来は0。群: OPEN333_sweep8:15, N3_redraw:14, N1_150:3, N3_real30:2)。ブロック行はL0と同一結果(test固定)。
- M-1(不規則読み): 両側・PRON/VALUE_ONLY両経路でL1不適用。Phase 1 M1で誤PASSだった『一日中→ついたち中』3行はNG(L1⊇L0)。
- R-1の効果(R-1 OFF→ON で PASS系→NG になる行): 全体10行。内訳 truth=NEG:7, UNL:3。
- R-1の副作用(重要): 6音声の正例で R-1 ON は ms_03 a2・a3、reselect a1・a2 の4本すべてをNGに戻す(§1)。『月の詩は/死は/氏は/野氏は』の漢字(詩・死・氏・野)が複数の読み候補を持つため。これは負例T1(同音異表記便乗)6件を消す効果と**同じ性質の裏表**(区別不能な同音を受理する/しない)。
- R-2: `ENGINE_reading_difference` 経路は除外(コーパスで発火0=Opus確認どおり)。

## 10. run単位の実益(参考): 完走までのattempt数・再生成・HR
| run | 構成 | N | 完走/終端 | attempt別判定 | 追加OpenAI draw |
|---|---|---|---|---|---|
| run_ms_03 | L0 | - | 未完走(全attempt NG→既存HR Lock) | a1:NG, a2:NG, a3:NG | 0 |
| run_ms_03 | L1+L2+L3 | 1 | 未完走(全attempt NG→既存HR Lock) | a1:NG, a2:NG, a3:NG | 0 |
| run_ms_03 | L1+L2+L3 | 2 | 未完走(全attempt NG→既存HR Lock) | a1:NG, a2:NG, a3:NG | 3 |
| run_ms_03 | L1+L2+L3 | 3 | 未完走(全attempt NG→既存HR Lock) | a1:NG, a2:NG, a3:NG | 6 |
| run_ms_03 | L1+L2+L3(R1off) | 1 | attempt2で完走 | a1:NG, a2:PASS_W(新方式) | 0 |
| run_ms_03 | L1+L2+L3(R1off) | 2 | attempt2で完走 | a1:NG, a2:PASS_W(新方式) | 1 |
| run_ms_03 | L1+L2+L3(R1off) | 3 | attempt2で完走 | a1:NG, a2:PASS_W(新方式) | 2 |
| run_reselect_01 | L0 | - | 未完走(全attempt NG→既存HR Lock) | a1:NG, a2:NG, a3:NG | 0 |
| run_reselect_01 | L1+L2+L3 | 1 | 未完走(全attempt NG→既存HR Lock) | a1:NG, a2:NG, a3:NG | 0 |
| run_reselect_01 | L1+L2+L3 | 2 | 未完走(全attempt NG→既存HR Lock) | a1:NG, a2:NG, a3:NG | 3 |
| run_reselect_01 | L1+L2+L3 | 3 | 未完走(全attempt NG→既存HR Lock) | a1:NG, a2:NG, a3:NG | 6 |
| run_reselect_01 | L1+L2+L3(R1off) | 1 | attempt1で完走 | a1:PASS_W(新方式) | 0 |
| run_reselect_01 | L1+L2+L3(R1off) | 2 | attempt1で完走 | a1:PASS_W(新方式) | 0 |
| run_reselect_01 | L1+L2+L3(R1off) | 3 | attempt1で完走 | a1:PASS_W(新方式) | 0 |

## 11. 残NG 2本の扱い(新状態は作らない=R-4)
残る ms_03 a1・reselect a3 は、安全条件を保つと機械判定で確定できない(a1: 記録済みOpenAIは『月野詩は8000句800本超え』、Azureは『月野市は8900本越え』で、詩/市の食い違いと値garble『8000句800』[explain_garble対象外]があり、別表L3が要求する「両engineとも置換後に原稿と残差0文字」を満たさない/a3: 5 drawのうち『スギノ』『杉の』『月の死は発生900』等、値以外の内容が原稿と食い違うdrawが多数で、PASSできる1本は少数派の釣りになるため合意規則はHR)。扱い=既存の流れそのまま: ASR NG→TTS再生成(上限内)→尽きたらSTOPPED→Human Review Lock(`human_review_queue.jsonl`)→ユーザー試聴で聴取OKなら `record_human_approval(out_dir, segment_key, canonical_text[=元の原稿])` を呼んでsha単位の個別採用→`verify_episode_audio_validation_gate` が HUMAN_APPROVED を許可(Assemblyへ進めるのはVALIDATED/HUMAN_APPROVEDのみ)。今回ユーザーはこの6音声を既に試聴OK済み(ms_03 a2は個別採用済み)。新しい『条件付きPASS』状態は作らない。再試行合意が早期HRを出す条件はエンジン間の内容矛盾のみ(ローカルWhisperの証言は添付情報に留め、機械PASSの根拠にしない)。API 0。

## 12. 6合格条件(ユーザー原文§6)への到達度とStatus候補(最終判定はFable)
| 条件 | 到達度 | 根拠 |
|---|---|---|
| 1. Human OKの6音声すべて最終判定でPASS | **未達**: 機械判定の上限は R-1 OFF 4/6 (PASS_W(新方式)/既存PASS_W)、R-1 ON(Opus R-1採用の主設定) 0/6。clean PASSは0/6。残りはHR Lock→個別採用(HUMAN_APPROVED)が必要 | §1 |
| 2. 既知の実誤読・負例を誤PASSしない | **部分**: 回帰0・OTHER=0。R-1 ON は増分1(T2)、R-1 OFF は増分8(T1 6=区別不能な同音異表記便乗、T2 2)。N3での再試行起因誤PASS 0(分母が小さい=上限は§5a) | §4・§5 |
| 3. 『月のしわ』固有の例外でない | **達成** | atom位置・別表・合意規則はいずれも題固有語なし。汎用題(100人超/1,200円超)で別表L3救済、負例増分0 | §8 |
| 4. X/Y/Zの対象範囲・既存仕様影響 | **達成(評価済み)** | Family×Level×Section影響範囲はEVAL_01 §5を継承(AdvにJA音声なし)。拡張4wavで X(mey)/Z(melos)/Y(preview)を実測。M-6でE3/E4と干渉しない構造 | §7 |
| 5. retry/fallback/resume/再判定整合 | **部分(設計達成・配線未)**: 合意再試行は承認済み仕様『同一音声ASR再試行廃止』の変更を伴う(D-1)。保存drawのみから再現(R-7 test)、flag OFF/scope外を先にblock、Azure再試行なし、COST_GUARD計上は設計案に残置(未配線) | proto test 48件 |
| 6. 実行費用・量産単価 | **達成(区間提示)** | §13 |

### Status候補: **USER_DECISION_REQUIRED**(VALIDATEDにしない)
- 理由: 条件1が未達(機械上限 R-1 OFF 4/6[PASS_W+試聴]、R-1 ON 0/6)。ユーザー§6『安全基準を緩めて6本を通さない』に従うと、残りは人間承認が必須。ユーザー判断事項: D-1(ASR再試行=承認済み仕様の変更、6本への効果0本)、D-2(超→こえ等の意味等価な非標準読みの受理)、D-3(新方式PASS_Wを事後試聴か公開前試聴必須か)、D-4(HUMAN_APPROVEDを『最終判定PASS』に数えるか)。
- 新規の事実(Opusレビュー採用後に判明): **R-1(漢字1字ごとのC2検査)を採用すると、案R(i)は6本のうち1本も救済しない**(§1・§9)。R-1は『ASRが書いた漢字に他の読みがあるなら、TTSが別の読みで読んだ可能性を排除できない』という安全側の検査で、それ自体は妥当。しかし本件の誤NGの原因である『しわ→詩は/死は/氏は/野氏は』型の同音異表記はすべて該当する。R-1 ONでは誤NG救済をほぼ諦める、R-1 OFFでは負例T1(区別不能な同音異表記便乗)6件を新層が受理する、というトレードオフ。参考事実: Production現行(L0)は既に『本帳/本蝶/本調/本町/本鳥』等の同音異表記(読み一致)を PS_same で PASS にしている(§8のL3_NEG E4/C2同形異音 11行がL0でPASS)=R-1 ONは現行Productionより新層の方が厳しい。これは品質基準の選択(判断候補D-5: 区別不能な同音異表記をどこまで受理するか。分類=D真に新しい判断)であり、私は決めない。
- REJECTEDにしない理由: 回帰0・OTHER増分0・汎用性達成・費用は軽微・合意規則の再試行起因誤PASS 0。

## 13. 費用・単価
- 本Phase 3の実費: 正例拡張4wav×4draw=OpenAI 16呼出(cost_log: input 2,488 tok / output 1,110 tok)。公表単価[$1.25/$5 per Mtok, ¥150/$]で約¥1.3、分課金[$0.003/min×249秒]で約¥1.9。請求明細は未取得=推定。見積(BUDGET_PLAN_03)¥1.9以内。Azure/TTS 0。負例追加drawなし(N3既出を再利用)。
- 単価への影響(採用した場合): 層L1〜L3は判定ロジックのみ(追加API 0)。Secondary未呼出でβ/L3が発火するときだけAzure追加呼出(約¥0.3/clip)。合意再試行はOpenAI 1本あたり約¥0.01(短題)〜¥0.1(15秒級)で、force_secondaryでもAzureはsha cacheに当たり追加0。6音声への新規PASS追加は0本のため、再生成削減(¥0.92/clip)の効果は『一般的なdrawノイズによる再生成の削減』に限られ、実測は未確認(現行の誤NG率データなし)。70円/記事セット目標に対する影響は軽微(≪1%)で、誤NG率が未知のため区間は『削減0〜¥1.8/記事(月題級の再生成を1〜2回回避した場合)』のまま。

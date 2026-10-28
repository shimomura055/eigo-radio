# EVAL_UNIFIED_01(JA-ASR-FALSE-NG-ROOT-FIX-02 委任_01B。eval_unified_01.py の出力から自動生成。API 0・費用0円)
事前登録=PREREGISTERED_01.md。Production HEAD 定数: {"JA_SECONDARY_VALUE_EQUIVALENCE_ENABLED": true, "READING_MATCH_FINAL_GATE": true} 。PASS_W=警告付きPASS(判定器のPASS_WITH_WARNING、または新方式[v2発音救済・β]経由=試聴必須)。PASSと別集計。
方式: M0=現行Production最終判定 / M1=v2(Primary+Secondary値等価層) / M2=M0+β / M3=P-1(M1の部分集合: 助詞は→わ/へ→え救済のみ) / M4=M1+β。M5(再転写best-of-N)は§2dに集計。

## 1. 6音声の転写全文(保存済み全転写。wav sha256先頭16桁で紐付け)
### run_ms_03 attempt1  sha256=5ccb3c481547abba…  `attempts/japanese_title_attempt1_customb8f0ff16.wav`
| engine | 出所 | 転写 |
|---|---|---|
| OpenAI(gpt-4o-mini-transcribe) | stored | 月野詩は8000句800本超え。その奥に潜む岩の上着の秘密。 |
| OpenAI(gpt-4o-mini-transcribe) | phase3_redraw0 | 月野詩は8,900本超え。その奥に潜む岩の上着の秘密。 |
| OpenAI(gpt-4o-mini-transcribe) | phase3_redraw1 | 月野詩は8,900本超え。その奥に潜む岩の上着の秘密。 |
| OpenAI(gpt-4o-mini-transcribe) | phase3_redraw2 | 好きの詩は8000900本超え。その奥に潜む岩の上着の秘密。 |
| Azure | phase3_azure | 月野市は8900本越え。その奥に潜む岩の上着の秘密。 |
| ローカルWhisper(参考・判定不使用) | medium | 月の詩は8,900本超え、その奥に潜む岩の上着の秘密。 |
| ローカルWhisper(参考・判定不使用) | small | 月の詩は8900本語へ その奥に潜む岩の上着の秘密 |

### run_ms_03 attempt2  sha256=f0c4b41580d30e2d…  `attempts/japanese_title_attempt2_customb8f0ff16.wav`
| engine | 出所 | 転写 |
|---|---|---|
| OpenAI(gpt-4o-mini-transcribe) | stored | 月の死は八千九百本超。その奥に潜む岩の上着の秘密。 |
| OpenAI(gpt-4o-mini-transcribe) | phase3_redraw0 | 月の島は千九百本超。その奥に潜む岩の上着の秘密。 |
| OpenAI(gpt-4o-mini-transcribe) | phase3_redraw1 | 月の島は千九百本超。その奥に潜む岩の上着の秘密。 |
| OpenAI(gpt-4o-mini-transcribe) | phase3_redraw2 | 月の島は千九百本超。その奥に潜む岩の上着の秘密。 |
| Azure | stored_scg_info | 月の詩は8900本超。その奥に潜む岩の上着の秘密。 |
| ローカルWhisper(参考・判定不使用) | medium | 月の死は8,900本超、その奥に潜む岩の上着の秘密 |
| ローカルWhisper(参考・判定不使用) | small | 月の種は8900本長、その奥に潜む岩の上着の秘密。 |

### run_ms_03 attempt3  sha256=d0dd41e4d8bf4995…  `attempts/japanese_title_attempt3_minimalfallback.wav`
| engine | 出所 | 転写 |
|---|---|---|
| OpenAI(gpt-4o-mini-transcribe) | stored | 月の氏は8000900本超。その奥に潜む岩の上着の秘密。 |
| OpenAI(gpt-4o-mini-transcribe) | phase3_redraw0 | 月野氏は八千九百本超、その奥に潜む岩の上着の秘密。 |
| OpenAI(gpt-4o-mini-transcribe) | phase3_redraw1 | 月の詩は八千九百本長。その奥に潜む岩の上着の秘密。 |
| OpenAI(gpt-4o-mini-transcribe) | phase3_redraw2 | 月のシワ、8000九百本超。その奥に潜む岩の上着の秘密。 |
| Azure | phase3_azure | 杉野氏は8900本超。その奥に潜む岩の上着の秘密。 |
| ローカルWhisper(参考・判定不使用) | medium | 月のしは8,900本帳その奥に潜む岩の上着の秘密 |
| ローカルWhisper(参考・判定不使用) | small | 月の種は8900ポンチョ、 その奥に潜む岩の上着の秘密。 |

### run_reselect_01 attempt1  sha256=6801464baf94805e…  `attempts/japanese_title_attempt1_customb8f0ff16.wav`
| engine | 出所 | 転写 |
|---|---|---|
| OpenAI(gpt-4o-mini-transcribe) | stored | 月野氏は8,900本超。その奥に潜む岩の上着の秘密 |
| OpenAI(gpt-4o-mini-transcribe) | reasr_openai0 | 月の詩は8,900本超。その奥に潜む岩の上着の秘密。 |
| OpenAI(gpt-4o-mini-transcribe) | reasr_openai1 | 月野氏は八千九百本超。その奥に潜む岩の上着の秘密 |
| OpenAI(gpt-4o-mini-transcribe) | reasr_openai2 | 月の詩は八千九百本調。その奥に潜む岩の上着の秘密。 |
| OpenAI(gpt-4o-mini-transcribe) | reasr_openai3 | 好きの詩は八千九百本超。その奥に潜む岩の上着の秘密。 |
| Azure | stored_scg_info | 月の詩は8900本ちょ。その奥に潜む岩の上着の秘密。 |
| ローカルWhisper(参考・判定不使用) | medium | 月の死は8,900本帳その奥に潜む岩の上着の秘密 |
| ローカルWhisper(参考・判定不使用) | small | 月の死は8900本長 その奥に潜む岩の上着の秘密 |

### run_reselect_01 attempt2  sha256=dd3dbc1e63045030…  `attempts/japanese_title_attempt2_customb8f0ff16.wav`
| engine | 出所 | 転写 |
|---|---|---|
| OpenAI(gpt-4o-mini-transcribe) | stored | 月の詩は八千九百本超。その奥に潜む岩の上着の秘密 |
| OpenAI(gpt-4o-mini-transcribe) | reasr_openai0 | 月の詩は8000900本超。その奥に潜む岩の上着の秘密。 |
| OpenAI(gpt-4o-mini-transcribe) | reasr_openai1 | 月の詩は8000900本超。その奥に潜む岩の上着の秘密。 |
| OpenAI(gpt-4o-mini-transcribe) | reasr_openai2 | 月野氏は発線900本超。その奥に潜む岩の上着の秘密。 |
| OpenAI(gpt-4o-mini-transcribe) | reasr_openai3 | 月の詩は8000900本超。その奥に潜む岩の上着の秘密。 |
| Azure | stored_scg_info | 月の詩は8900本ちょうその奥に潜む岩の上着の秘密。 |
| ローカルWhisper(参考・判定不使用) | medium | 月の死は8,900本蝶、その奥に潜む岩の上着の秘密。 |
| ローカルWhisper(参考・判定不使用) | small | 月の死は8900本長、その奥に潜む岩の上着の秘密。 |

### run_reselect_01 attempt3  sha256=45309c9f88e1af70…  `attempts/japanese_title_attempt3_minimalfallback.wav`
| engine | 出所 | 転写 |
|---|---|---|
| OpenAI(gpt-4o-mini-transcribe) | stored | スギノ市は、八千九百本超、その奥に潜む岩の上着の秘密。 |
| OpenAI(gpt-4o-mini-transcribe) | reasr_openai0 | 杉の市は、8000坪のその奥に潜む岩の上着の秘密。 |
| OpenAI(gpt-4o-mini-transcribe) | reasr_openai1 | 月野市は、八千九百本超。その奥に潜む岩の上着の秘密。 |
| OpenAI(gpt-4o-mini-transcribe) | reasr_openai2 | 月の死は、発生900本超。その奥に潜む岩の上着の秘密。 |
| OpenAI(gpt-4o-mini-transcribe) | reasr_openai3 | 月野氏は、発生900本超。その奥に潜む岩の上着の秘密。 |
| Azure | stored_scg_info | Sukino氏は8900本超。その奥に潜む岩の上着の秘密。 |
| ローカルWhisper(参考・判定不使用) | medium | 月の死は8,900ポンチョウ。その奥に潜む岩の上着の秘密。 |
| ローカルWhisper(参考・判定不使用) | small | 月の詩は8900ポンチョ、その奥に潜む岩の上着の秘密。 |

## 2a. 6音声×方式: 最終Gate結果(決定対=当時記録のOpenAI転写 × 当該wavのAzure転写)
| 音声 | M0 現行Production | M1 v2 | M2 β | M3 P-1 | M4 v2+β | 決定条件(M4の経路 / M0のNG理由) |
|---|---|---|---|---|---|---|
| run_ms_03 a1 | NG | NG | NG | NG | NG | M4=p1_value_diff / M0=p1_value_diff |
| run_ms_03 a2 | NG | PASS_W | PASS_W | PASS_W | PASS_W | M4=v2_pron:primary:A3_value+A2_particle / M0=secondary_not_accepted |
| run_ms_03 a3 | NG | NG | PASS_W | NG | PASS_W | M4=beta_composite:listen / M0=p1_value_diff |
| run_reselect_01 a1 | NG | PASS_W | PASS_W | PASS_W | PASS_W | M4=v2_pron:primary:A3_value+A2_particle / M0=secondary_not_accepted |
| run_reselect_01 a2 | NG | PASS_W | PASS_W | PASS_W | PASS_W | M4=v2_pron:primary:A3_value+A2_particle / M0=secondary_not_accepted |
| run_reselect_01 a3 | NG | NG | NG | NG | NG | M4=secondary_not_accepted / M0=secondary_not_accepted |

決定対のOpenAI/Azure: 
- run_ms_03 a1: OpenAI=`月野詩は8000句800本超え。その奥に潜む岩の上着の秘密。` / Azure=`月野市は8900本越え。その奥に潜む岩の上着の秘密。`
- run_ms_03 a2: OpenAI=`月の死は八千九百本超。その奥に潜む岩の上着の秘密。` / Azure=`月の詩は8900本超。その奥に潜む岩の上着の秘密。`
- run_ms_03 a3: OpenAI=`月の氏は8000900本超。その奥に潜む岩の上着の秘密。` / Azure=`杉野氏は8900本超。その奥に潜む岩の上着の秘密。`
- run_reselect_01 a1: OpenAI=`月野氏は8,900本超。その奥に潜む岩の上着の秘密` / Azure=`月の詩は8900本ちょ。その奥に潜む岩の上着の秘密。`
- run_reselect_01 a2: OpenAI=`月の詩は八千九百本超。その奥に潜む岩の上着の秘密` / Azure=`月の詩は8900本ちょうその奥に潜む岩の上着の秘密。`
- run_reselect_01 a3: OpenAI=`スギノ市は、八千九百本超、その奥に潜む岩の上着の秘密。` / Azure=`Sukino氏は8900本超。その奥に潜む岩の上着の秘密。`

決定対の集計(6音声): M0: PASS=0 PASS_W=0 NG=6 / M1: PASS=0 PASS_W=3 NG=3 / M2: PASS=0 PASS_W=4 NG=2 / M3: PASS=0 PASS_W=3 NG=3 / M4: PASS=0 PASS_W=4 NG=2

## 2b. 同一wavの転写変動(draw集合): OpenAI draw × Azure(2種以上あれば全て)の判定分布
| 音声 | OpenAI draw数 / 異なる転写数 | 値が正しい転写(値ガードEQUAL) | Azure転写数(異なる) | 判定対数 | M0 PASS+PASS_W | M1 PASS+PASS_W | M2 PASS+PASS_W | M3 PASS+PASS_W | M4 PASS+PASS_W | Primary単独(Azure不呼出) M0/M1 |
|---|---|---|---|---|---|---|---|---|---|---|
| run_ms_03 a1 | 4 / 3 | 2/4 | 1 | 4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 , 0/4 |
| run_ms_03 a2 | 4 / 2 | 1/4 | 1 | 4 | 0/4 | 1/4 | 1/4 | 1/4 | 1/4 | 0/4 , 1/4 |
| run_ms_03 a3 | 4 / 4 | 2/4 | 1 | 4 | 0/4 | 1/4 | 3/4 | 1/4 | 3/4 | 0/4 , 1/4 |
| run_reselect_01 a1 | 5 / 5 | 5/5 | 1 | 5 | 0/5 | 3/5 | 3/5 | 3/5 | 3/5 | 0/5 , 3/5 |
| run_reselect_01 a2 | 5 / 3 | 1/5 | 1 | 5 | 0/5 | 1/5 | 4/5 | 1/5 | 4/5 | 0/5 , 1/5 |
| run_reselect_01 a3 | 5 / 5 | 2/5 | 1 | 5 | 0/5 | 1/5 | 1/5 | 1/5 | 1/5 | 0/5 , 1/5 |

## 2c. 6音声×方式×全draw対の判定(全行)
| 音声 | OpenAI(出所) | Azure(出所) | M0 | M1 | M2 | M3 | M4 | M0 NG理由 | M4経路 |
|---|---|---|---|---|---|---|---|---|---|
| ms_03 a1 | stored: 月野詩は8000句800本超え。その奥に潜む岩の上着の秘密。 | phase3_azure: 月野市は8900本越え。その奥に潜む岩の上着の秘密。 | NG | NG | NG | NG | NG | p1_value_diff | p1_value_diff |
| ms_03 a1 | phase3_redraw0: 月野詩は8,900本超え。その奥に潜む岩の上着の秘密。 | phase3_azure: 月野市は8900本越え。その奥に潜む岩の上着の秘密。 | NG | NG | NG | NG | NG | secondary_not_accepted | secondary_not_accepted |
| ms_03 a1 | phase3_redraw1: 月野詩は8,900本超え。その奥に潜む岩の上着の秘密。 | phase3_azure: 月野市は8900本越え。その奥に潜む岩の上着の秘密。 | NG | NG | NG | NG | NG | secondary_not_accepted | secondary_not_accepted |
| ms_03 a1 | phase3_redraw2: 好きの詩は8000900本超え。その奥に潜む岩の上着の秘密。 | phase3_azure: 月野市は8900本越え。その奥に潜む岩の上着の秘密。 | NG | NG | NG | NG | NG | p1_value_diff | p1_value_diff |
| ms_03 a2 | stored: 月の死は八千九百本超。その奥に潜む岩の上着の秘密。 | stored_scg_info: 月の詩は8900本超。その奥に潜む岩の上着の秘密。 | NG | PASS_W | PASS_W | PASS_W | PASS_W | secondary_not_accepted | v2_pron:primary:A3_value+A2_particle |
| ms_03 a2 | phase3_redraw0: 月の島は千九百本超。その奥に潜む岩の上着の秘密。 | stored_scg_info: 月の詩は8900本超。その奥に潜む岩の上着の秘密。 | NG | NG | NG | NG | NG | p1_value_diff | p1_value_diff |
| ms_03 a2 | phase3_redraw1: 月の島は千九百本超。その奥に潜む岩の上着の秘密。 | stored_scg_info: 月の詩は8900本超。その奥に潜む岩の上着の秘密。 | NG | NG | NG | NG | NG | p1_value_diff | p1_value_diff |
| ms_03 a2 | phase3_redraw2: 月の島は千九百本超。その奥に潜む岩の上着の秘密。 | stored_scg_info: 月の詩は8900本超。その奥に潜む岩の上着の秘密。 | NG | NG | NG | NG | NG | p1_value_diff | p1_value_diff |
| ms_03 a3 | stored: 月の氏は8000900本超。その奥に潜む岩の上着の秘密。 | phase3_azure: 杉野氏は8900本超。その奥に潜む岩の上着の秘密。 | NG | NG | PASS_W | NG | PASS_W | p1_value_diff | beta_composite:listen |
| ms_03 a3 | phase3_redraw0: 月野氏は八千九百本超、その奥に潜む岩の上着の秘密。 | phase3_azure: 杉野氏は8900本超。その奥に潜む岩の上着の秘密。 | NG | PASS_W | PASS_W | PASS_W | PASS_W | secondary_not_accepted | v2_pron:primary:A3_value+A2_particle |
| ms_03 a3 | phase3_redraw1: 月の詩は八千九百本長。その奥に潜む岩の上着の秘密。 | phase3_azure: 杉野氏は8900本超。その奥に潜む岩の上着の秘密。 | NG | NG | NG | NG | NG | p2_exclusion:A4_C2_HOMOGRAPH | p2_exclusion:A4_C2_HOMOGRAPH |
| ms_03 a3 | phase3_redraw2: 月のシワ、8000九百本超。その奥に潜む岩の上着の秘密。 | phase3_azure: 杉野氏は8900本超。その奥に潜む岩の上着の秘密。 | NG | NG | PASS_W | NG | PASS_W | p1_value_diff | beta_composite:listen |
| reselect_01 a1 | stored: 月野氏は8,900本超。その奥に潜む岩の上着の秘密 | stored_scg_info: 月の詩は8900本ちょ。その奥に潜む岩の上着の秘密。 | NG | PASS_W | PASS_W | PASS_W | PASS_W | secondary_not_accepted | v2_pron:primary:A3_value+A2_particle |
| reselect_01 a1 | reasr_openai0: 月の詩は8,900本超。その奥に潜む岩の上着の秘密。 | stored_scg_info: 月の詩は8900本ちょ。その奥に潜む岩の上着の秘密。 | NG | PASS_W | PASS_W | PASS_W | PASS_W | secondary_not_accepted | v2_pron:primary:A3_value+A2_particle |
| reselect_01 a1 | reasr_openai1: 月野氏は八千九百本超。その奥に潜む岩の上着の秘密 | stored_scg_info: 月の詩は8900本ちょ。その奥に潜む岩の上着の秘密。 | NG | PASS_W | PASS_W | PASS_W | PASS_W | secondary_not_accepted | v2_pron:primary:A3_value+A2_particle |
| reselect_01 a1 | reasr_openai2: 月の詩は八千九百本調。その奥に潜む岩の上着の秘密。 | stored_scg_info: 月の詩は8900本ちょ。その奥に潜む岩の上着の秘密。 | NG | NG | NG | NG | NG | p2_exclusion:A4_C2_HOMOGRAPH | p2_exclusion:A4_C2_HOMOGRAPH |
| reselect_01 a1 | reasr_openai3: 好きの詩は八千九百本超。その奥に潜む岩の上着の秘密。 | stored_scg_info: 月の詩は8900本ちょ。その奥に潜む岩の上着の秘密。 | NG | NG | NG | NG | NG | secondary_not_accepted | secondary_not_accepted |
| reselect_01 a2 | stored: 月の詩は八千九百本超。その奥に潜む岩の上着の秘密 | stored_scg_info: 月の詩は8900本ちょうその奥に潜む岩の上着の秘密。 | NG | PASS_W | PASS_W | PASS_W | PASS_W | secondary_not_accepted | v2_pron:primary:A3_value+A2_particle |
| reselect_01 a2 | reasr_openai0: 月の詩は8000900本超。その奥に潜む岩の上着の秘密。 | stored_scg_info: 月の詩は8900本ちょうその奥に潜む岩の上着の秘密。 | NG | NG | PASS_W | NG | PASS_W | p1_value_diff | beta_composite:listen |
| reselect_01 a2 | reasr_openai1: 月の詩は8000900本超。その奥に潜む岩の上着の秘密。 | stored_scg_info: 月の詩は8900本ちょうその奥に潜む岩の上着の秘密。 | NG | NG | PASS_W | NG | PASS_W | p1_value_diff | beta_composite:listen |
| reselect_01 a2 | reasr_openai2: 月野氏は発線900本超。その奥に潜む岩の上着の秘密。 | stored_scg_info: 月の詩は8900本ちょうその奥に潜む岩の上着の秘密。 | NG | NG | NG | NG | NG | p1_value_diff | p1_value_diff |
| reselect_01 a2 | reasr_openai3: 月の詩は8000900本超。その奥に潜む岩の上着の秘密。 | stored_scg_info: 月の詩は8900本ちょうその奥に潜む岩の上着の秘密。 | NG | NG | PASS_W | NG | PASS_W | p1_value_diff | beta_composite:listen |
| reselect_01 a3 | stored: スギノ市は、八千九百本超、その奥に潜む岩の上着の秘密。 | stored_scg_info: Sukino氏は8900本超。その奥に潜む岩の上着の秘密。 | NG | NG | NG | NG | NG | secondary_not_accepted | secondary_not_accepted |
| reselect_01 a3 | reasr_openai0: 杉の市は、8000坪のその奥に潜む岩の上着の秘密。 | stored_scg_info: Sukino氏は8900本超。その奥に潜む岩の上着の秘密。 | NG | NG | NG | NG | NG | p1_value_diff | p1_value_diff |
| reselect_01 a3 | reasr_openai1: 月野市は、八千九百本超。その奥に潜む岩の上着の秘密。 | stored_scg_info: Sukino氏は8900本超。その奥に潜む岩の上着の秘密。 | NG | PASS_W | PASS_W | PASS_W | PASS_W | secondary_not_accepted | v2_pron:primary:A3_value+A2_particle |
| reselect_01 a3 | reasr_openai2: 月の死は、発生900本超。その奥に潜む岩の上着の秘密。 | stored_scg_info: Sukino氏は8900本超。その奥に潜む岩の上着の秘密。 | NG | NG | NG | NG | NG | p1_value_diff | p1_value_diff |
| reselect_01 a3 | reasr_openai3: 月野氏は、発生900本超。その奥に潜む岩の上着の秘密。 | stored_scg_info: Sukino氏は8900本超。その奥に潜む岩の上着の秘密。 | NG | NG | NG | NG | NG | p1_value_diff | p1_value_diff |

## 2d. M5 判定前のASR再試行(best-of-N): 同一wavのOpenAI draw をN本まで許し、いずれか1本でPASS(+PASS_W)ならPASS扱い(決定対のAzure固定)
| 音声 | draws | M0 best-of-N | M4 best-of-N | M4 draw別(上から順) |
|---|---|---|---|---|
| ms_03 a1 | 4 | NG | NG | .... |
| ms_03 a2 | 4 | NG | PASS_W | o... |
| ms_03 a3 | 4 | NG | PASS_W | oo.o |
| reselect_01 a1 | 5 | NG | PASS_W | ooo.. |
| reselect_01 a2 | 5 | NG | PASS_W | ooo.o |
| reselect_01 a3 | 5 | NG | PASS_W | ..o.. |

注: 負例側のbest-of-N誤PASSは実測不能(再転写が無い)。理論上、同一wavへのN回再転写でいずれか1本が誤PASSすれば誤PASSになる=誤PASS率は最大N倍(各draw独立でない場合は小さい)。設計案で扱う。

## 3. 負例・対照の誤PASS件数(群×シナリオ×方式。PASS/PASS_W別。増分=M0がNG→当該方式がPASS/PASS_W)
真値 NEG=誤PASSしてはならない / POS=救済されうる対照 / UNL=真値不明(増分は列挙して個別審査、誤PASS率に算入しない)
| 真値 | 群 | シナリオ | n | M0 PASS/PASS_W (増分) | M1 PASS/PASS_W (増分) | M2 PASS/PASS_W (増分) | M3 PASS/PASS_W (増分) | M4 PASS/PASS_W (増分) |
|---|---|---|---|---|---|---|---|---|
| NEG | BLIGHT_synthetic | explicit | 86 | 11/4 (+0) | 11/4 (+0) | 11/4 (+0) | 11/4 (+0) | 11/4 (+0) |
| NEG | N1_150 | PS_same | 143 | 11/3 (+0) | 11/3 (+0) | 11/3 (+0) | 11/3 (+0) | 11/3 (+0) |
| NEG | N1_150 | P_only | 143 | 11/3 (+0) | 11/3 (+0) | 11/3 (+0) | 11/3 (+0) | 11/3 (+0) |
| NEG | N1_150 | S_canon | 143 | 11/52 (+0) | 11/52 (+0) | 11/53 (+1) | 11/52 (+0) | 11/53 (+1) |
| NEG | N3_real30 | real | 30 | 10/4 (+0) | 10/4 (+0) | 10/4 (+0) | 10/4 (+0) | 10/4 (+0) |
| NEG | OPEN333_E4 | PS_same | 56 | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) |
| NEG | OPEN333_E4 | P_only | 56 | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) |
| NEG | OPEN333_E4 | S_canon | 56 | 0/26 (+0) | 0/26 (+0) | 0/26 (+0) | 0/26 (+0) | 0/26 (+0) |
| NEG | OPEN333_sweep8 | PS_same | 21 | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) |
| NEG | OPEN333_sweep8 | P_only | 21 | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) |
| NEG | OPEN333_sweep8 | S_canon | 21 | 0/3 (+0) | 0/3 (+0) | 0/3 (+0) | 0/3 (+0) | 0/3 (+0) |
| NEG | OPEN517_wrongvalue_kana | PS_same | 157 | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) |
| NEG | OPEN517_wrongvalue_kana | P_only | 157 | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) |
| NEG | OPEN517_wrongvalue_kana | S_canon | 157 | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) |
| NEG | R4R3_extra18 | PS_same | 18 | 0/0 (+0) | 0/3 (+3) | 0/2 (+2) | 0/3 (+3) | 0/3 (+3) |
| NEG | R4R3_extra18 | P_only | 18 | 0/0 (+0) | 0/3 (+3) | 0/0 (+0) | 0/3 (+3) | 0/3 (+3) |
| NEG | R4R3_extra18 | S_canon | 18 | 0/6 (+0) | 0/7 (+1) | 0/7 (+1) | 0/7 (+1) | 0/8 (+2) |
| NEG | UC6_U1_異なる発音 | PS_same | 7 | 1/0 (+0) | 1/0 (+0) | 1/0 (+0) | 1/0 (+0) | 1/0 (+0) |
| NEG | UC6_U1_異なる発音 | P_only | 7 | 1/0 (+0) | 1/0 (+0) | 1/0 (+0) | 1/0 (+0) | 1/0 (+0) |
| NEG | UC6_U1_異なる発音 | S_canon | 7 | 1/6 (+0) | 1/6 (+0) | 1/6 (+0) | 1/6 (+0) | 1/6 (+0) |
| NEG | UC6_U2_異なる数値 | PS_same | 8 | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) |
| NEG | UC6_U2_異なる数値 | P_only | 8 | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) |
| NEG | UC6_U2_異なる数値 | S_canon | 8 | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) |
| NEG | UC6_U3_助数詞違い | PS_same | 8 | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) |
| NEG | UC6_U3_助数詞違い | P_only | 8 | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) |
| NEG | UC6_U3_助数詞違い | S_canon | 8 | 0/3 (+0) | 0/3 (+0) | 0/3 (+0) | 0/3 (+0) | 0/3 (+0) |
| NEG | UC6_U4_語句脱落 | PS_same | 7 | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) |
| NEG | UC6_U4_語句脱落 | P_only | 7 | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) |
| NEG | UC6_U4_語句脱落 | S_canon | 7 | 0/5 (+0) | 0/5 (+0) | 0/5 (+0) | 0/5 (+0) | 0/5 (+0) |
| NEG | UC6_U5_意味を変える読み違い | PS_same | 7 | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) |
| NEG | UC6_U5_意味を変える読み違い | P_only | 7 | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) |
| NEG | UC6_U5_意味を変える読み違い | S_canon | 7 | 0/5 (+0) | 0/5 (+0) | 0/5 (+0) | 0/5 (+0) | 0/5 (+0) |
| NEG | UC6_U6_同音異表記便乗 | PS_same | 9 | 1/0 (+0) | 1/1 (+1) | 1/1 (+1) | 1/1 (+1) | 1/1 (+1) |
| NEG | UC6_U6_同音異表記便乗 | P_only | 9 | 1/0 (+0) | 1/1 (+1) | 1/0 (+0) | 1/1 (+1) | 1/1 (+1) |
| NEG | UC6_U6_同音異表記便乗 | S_canon | 9 | 1/3 (+0) | 1/3 (+0) | 1/3 (+0) | 1/3 (+0) | 1/3 (+0) |
| POS | OPEN333_sweep8 | PS_same | 19 | 10/1 (+0) | 10/1 (+0) | 10/1 (+0) | 10/1 (+0) | 10/1 (+0) |
| POS | OPEN333_sweep8 | P_only | 19 | 10/1 (+0) | 10/1 (+0) | 10/1 (+0) | 10/1 (+0) | 10/1 (+0) |
| POS | OPEN333_sweep8 | S_canon | 19 | 10/4 (+0) | 10/4 (+0) | 10/4 (+0) | 10/4 (+0) | 10/4 (+0) |
| POS | R4R3_pos | PS_same | 4 | 4/0 (+0) | 4/0 (+0) | 4/0 (+0) | 4/0 (+0) | 4/0 (+0) |
| POS | R4R3_pos | P_only | 4 | 4/0 (+0) | 4/0 (+0) | 4/0 (+0) | 4/0 (+0) | 4/0 (+0) |
| POS | R4R3_pos | S_canon | 4 | 4/0 (+0) | 4/0 (+0) | 4/0 (+0) | 4/0 (+0) | 4/0 (+0) |
| POS | er066_POSITIVE | PS_same | 37 | 19/14 (+0) | 20/14 (+1) | 19/14 (+0) | 20/14 (+1) | 20/14 (+1) |
| POS | er066_POSITIVE | P_only | 37 | 19/14 (+0) | 20/14 (+1) | 19/14 (+0) | 20/14 (+1) | 20/14 (+1) |
| POS | er066_POSITIVE | S_canon | 37 | 19/15 (+0) | 20/14 (+0) | 19/15 (+0) | 20/14 (+0) | 20/14 (+0) |
| UNL | HIST_43pairs | real | 36 | 0/15 (+0) | 0/16 (+1) | 0/16 (+1) | 0/16 (+1) | 0/16 (+1) |
| UNL | N1_150 | PS_same | 1 | 0/0 (+0) | 0/1 (+1) | 0/0 (+0) | 0/1 (+1) | 0/1 (+1) |
| UNL | N1_150 | P_only | 1 | 0/0 (+0) | 0/1 (+1) | 0/0 (+0) | 0/1 (+1) | 0/1 (+1) |
| UNL | N1_150 | S_canon | 1 | 0/1 (+0) | 0/1 (+0) | 0/1 (+0) | 0/1 (+0) | 0/1 (+0) |
| UNL | OPEN333_E4 | PS_same | 16 | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) |
| UNL | OPEN333_E4 | P_only | 16 | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) | 0/0 (+0) |
| UNL | OPEN333_E4 | S_canon | 16 | 0/16 (+0) | 0/16 (+0) | 0/16 (+0) | 0/16 (+0) | 0/16 (+0) |

NEG全体(全シナリオ合算 1439行): M0: 誤PASS=183 増分=0 回帰(M0 PASS→NG)=0 / M1: 誤PASS=192 増分=9 回帰(M0 PASS→NG)=0 / M2: 誤PASS=188 増分=5 回帰(M0 PASS→NG)=0 / M3: 誤PASS=192 増分=9 回帰(M0 PASS→NG)=0 / M4: 誤PASS=194 増分=11 回帰(M0 PASS→NG)=0

### 3a. 増分(M0がNGで、いずれかの方式がPASS/PASS_Wにした行)の全件(NEG/UNL。POS対照は§3c)
| 真値 | 群 | シナリオ | 原稿 | Primary | Secondary | 増分を出した方式 | 経路 | 分類(事後) |
|---|---|---|---|---|---|---|---|---|
| NEG | N1_150 | S_canon | 月のしわ、8,900本超 | 月の詩は8000900本超 | 月のしわ、8,900本超 | M2,M4 | beta_composite:listen | β: 数値garble断片(Secondaryが原稿値を返した場合のみ)=設計対象型 |
| UNL | N1_150 | P_only | 月のしわ | 月の詩は | - | M1,M3,M4 | v2_pron:primary:A2_particle | v2: 音素列が原稿と同一(ツキノシワ)=ASRテキストから区別不能な同音(by-design) |
| UNL | N1_150 | PS_same | 月のしわ | 月の詩は | 月の詩は | M1,M3,M4 | v2_pron:primary:A2_particle | v2: 音素列が原稿と同一(ツキノシワ)=ASRテキストから区別不能な同音(by-design) |
| NEG | R4R3_extra18 | P_only | 月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密 | 月の詩は、8900本超！その奥に潜む「岩の上着」の秘密 | - | M1,M3,M4 | v2_pron:primary:A3_value+A2_particle | v2: 音素列が原稿と同一(ツキノシワ)=ASRテキストから区別不能な同音(by-design) |
| NEG | R4R3_extra18 | PS_same | 月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密 | 月の詩は、8900本超！その奥に潜む「岩の上着」の秘密 | 月の詩は、8900本超！その奥に潜む「岩の上 | M1,M2,M3,M4 | v2_pron:primary:A3_value+A2_particle | v2: 音素列が原稿と同一(ツキノシワ)=ASRテキストから区別不能な同音(by-design) |
| NEG | R4R3_extra18 | P_only | 月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密 | 月の詩は、8,900本超！その奥に潜む「岩の上着」の秘密 | - | M1,M3,M4 | v2_pron:primary:A3_value+A2_particle | v2: 音素列が原稿と同一(ツキノシワ)=ASRテキストから区別不能な同音(by-design) |
| NEG | R4R3_extra18 | PS_same | 月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密 | 月の詩は、8,900本超！その奥に潜む「岩の上着」の秘密 | 月の詩は、8,900本超！その奥に潜む「岩の | M1,M2,M3,M4 | v2_pron:primary:A3_value+A2_particle | v2: 音素列が原稿と同一(ツキノシワ)=ASRテキストから区別不能な同音(by-design) |
| NEG | R4R3_extra18 | S_canon | 月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密 | 月のしわ、8000900本超！その奥に潜む「岩の上着」の秘密 | 月のしわ、8,900本超！その奥に潜む「岩の | M2,M4 | beta_composite:listen | β: 数値garble断片(Secondaryが原稿値を返した場合のみ)=設計対象型 |
| NEG | R4R3_extra18 | P_only | 今日は一日中雨 | 今日はついたち中雨 | - | M1,M3,M4 | prod_warning:JA_NUMERIC_IRREGULAR_READING | v2層のVALUE_ONLY経路が不規則読み(一日→ついたち)をwarning付きで受理(Production既存のwarning挙動と同系) |
| NEG | R4R3_extra18 | PS_same | 今日は一日中雨 | 今日はついたち中雨 | 今日はついたち中雨 | M1,M3,M4 | prod_warning:JA_NUMERIC_IRREGULAR_READING | v2層のVALUE_ONLY経路が不規則読み(一日→ついたち)をwarning付きで受理(Production既存のwarning挙動と同系) |
| NEG | R4R3_extra18 | S_canon | 今日は一日中雨 | 今日はついたち中雨 | 今日は一日中雨 | M1,M3,M4 | prod_warning:JA_NUMERIC_IRREGULAR_READING | v2層のVALUE_ONLY経路が不規則読み(一日→ついたち)をwarning付きで受理(Production既存のwarning挙動と同系) |
| NEG | UC6_U6_同音異表記便乗 | P_only | 月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密 | 月の死は、8,900本超！その奥に潜む「岩の上着」の秘密 | - | M1,M3,M4 | v2_pron:primary:A3_value+A2_particle | v2: 音素列が原稿と同一(ツキノシワ)=ASRテキストから区別不能な同音(by-design) |
| NEG | UC6_U6_同音異表記便乗 | PS_same | 月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密 | 月の死は、8,900本超！その奥に潜む「岩の上着」の秘密 | 月の死は、8,900本超！その奥に潜む「岩の | M1,M2,M3,M4 | v2_pron:primary:A3_value+A2_particle | v2: 音素列が原稿と同一(ツキノシワ)=ASRテキストから区別不能な同音(by-design) |
| UNL | HIST_43pairs | real | 月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密 | 月の死は八千九百本超。その奥に潜む岩の上着の秘密。 | 月の詩は8900本超。その奥に潜む岩の上着の | M1,M2,M3,M4 | v2_pron:primary:A3_value+A2_particle | v2: 音素列が原稿と同一(ツキノシワ)=ASRテキストから区別不能な同音(by-design) |

### 3b. 既存Production(M0)の誤PASS(NEG・S_canon以外=Primary/両エンジン同一誤り)=新方式と無関係の基準線
| 群 | シナリオ | M0カテゴリ | 件 | 例 |
|---|---|---|---|---|
| BLIGHT_synthetic | explicit | PASS | 11 | 月のしわ、8,900本超！そ→月のしわ、8,900本超。そ; 月のしわ、8,900本超！そ→月のしわ、8,900本超。そ |
| BLIGHT_synthetic | explicit | PASS_W | 4 | 三日待った→3日待った。; 二十歳になった→20歳になった |
| N1_150 | PS_same | PASS | 11 | 三分の一→3分の1; 3分の一→三分の1 |
| N1_150 | PS_same | PASS_W | 3 | 2人でいちばに行った→二人で市場に行った; 3人でついたちに会った→三人で一日に会った |
| N1_150 | P_only | PASS | 11 | 三分の一→3分の1; 3分の一→三分の1 |
| N1_150 | P_only | PASS_W | 3 | 2人でいちばに行った→二人で市場に行った; 3人でついたちに会った→三人で一日に会った |
| N3_real30 | real | PASS | 10 | 魚を市場で買う→魚を市場で買う。; 駅まで行った→駅まで行った。 |
| N3_real30 | real | PASS_W | 4 | 今日、話した→こんにちは、話した。; 十月一日に会う→10月1日に会う。 |
| UC6_U1_異なる発音 | PS_same | PASS | 1 | 橋を渡る→箸を渡る |
| UC6_U1_異なる発音 | P_only | PASS | 1 | 橋を渡る→箸を渡る |
| UC6_U6_同音異表記便乗 | PS_same | PASS | 1 | 今日は晴れです→京は晴れです |
| UC6_U6_同音異表記便乗 | P_only | PASS | 1 | 今日は晴れです→京は晴れです |

(上の基準線は『原稿とASR転写の表層が同一または既存規則で等価』なため機械では区別不能な型[同形異音・助詞誤読・桁区切り] と BLIGHT value_wrong:S_only[Primaryが原稿通りでSecondaryだけ誤り=either-engine設計]。方式による増減なし。)

### 3c. POS対照(救済されうる正例): M0がNGで救済された件と回帰
- 救済: er066_POSITIVE/P_only 20％の人が来ました。 | 20パーセントの人が来ました。 → M1,M3,M4 (prod:primary_pass)
- 救済: er066_POSITIVE/PS_same 20％の人が来ました。 | 20パーセントの人が来ました。 → M1,M3,M4 (prod:primary_pass)
- POS回帰(M0 PASS→NG)件数: 0
- 全行の回帰(M0 PASS/PASS_W→NG)件数: 0 (M1⊇M0, M3⊇M0, M2⊇M0, M4⊇M1 の確認)

## 4. §4-3 の6分類の被覆(各分類>=3件のテキスト負例。UC6は新規合成、他群と合わせた誤PASS)
| 分類 | 件数(シナリオ別行数) | M0誤PASS | M4誤PASS | M4増分 |
|---|---|---|---|---|
| U1_異なる発音 | 7件×3シナリオ | 9 | 9 | 0 |
| U2_異なる数値 | 8件×3シナリオ | 0 | 0 | 0 |
| U3_助数詞違い | 8件×3シナリオ | 3 | 3 | 0 |
| U4_語句脱落 | 7件×3シナリオ | 5 | 5 | 0 |
| U5_意味を変える読み違い | 7件×3シナリオ | 5 | 5 | 0 |
| U6_同音異表記便乗 | 9件×3シナリオ | 6 | 8 | 2 |
(S_canonシナリオ[Secondary=原稿]のM0 PASS_Wは『either-engine: Secondaryが原稿と完全一致なら受理』の既存設計。P_only/PS_same[両エンジン同じ誤り]が実際の誤PASSの評価面。)
U1-U6の P_only/PS_same で M0 が PASS となるのは『橋→箸』『今日→京』=表層差が同音の同形異音(機械では区別不能・基準線)のみ。値/助数詞/脱落/意味変化の誤りはM0・M4とも誤PASS 0。

## 5. X/Y/Z Standard 日本語音声の適用範囲(ja_asr_wiring_matrix_scan_01.out.json 再利用)
| Family | Level | Section | JA segment数 | R5 telemetry付き | NG_BOTH | PASS | PASS_WITH_WARNING |
|---|---|---|---|---|---|---|---|
| X | a2(Std) | comment | 100 | 8 | 1 | 88 | 11 |
| X | a2(Std) | japanese_title | 31 | 12 | 4 | 25 | 2 |
| X | a2(Std) | kp_japanese_meaning | 54 | 8 | 0 | 50 | 4 |
| X | a2(Std) | preview | 25 | 2 | 0 | 24 | 1 |
| Y | a2(Std) | comment | 24 | 9 | 0 | 24 | 0 |
| Y | a2(Std) | japanese_title | 12 | 7 | 1 | 11 | 0 |
| Y | a2(Std) | kp_japanese_meaning | 6 | 3 | 0 | 6 | 0 |
| Y | a2(Std) | preview | 5 | 4 | 4 | 1 | 0 |
| Z | a2(Std) | comment | 75 | 12 | 0 | 65 | 10 |
| Z | a2(Std) | japanese_title | 27 | 6 | 0 | 13 | 14 |
| Z | a2(Std) | kp_japanese_meaning | 107 | 22 | 0 | 107 | 0 |
| Z | a2(Std) | preview | 25 | 4 | 0 | 14 | 11 |

注: Y/preview は n=5 のうち4件が NG_BOTH(R5付き4件)。本委任の評価対象(月題)とは別の事象で、原因は未調査(OPEN候補として報告)。

Adv(b1b)の日本語音声行は0(スキャン対象にb1bを含めたが JA segment が存在しない=実run記録上の除外。Advは英語本文[CURRENT_SPEC.md:838 Natural English Adaptation 等]で日本語音声(題・Preview・Comment・KP日本語意味)を持たない)。

## 6. v2・β・P-1 それぞれの効果とリスク(本評価の観測値)
- 6音声の全draw×Azure対 27 本の PASS+PASS_W: M0=0 / M1=7 / M2=12 / M3=7 / M4=12。うち clean PASS(警告なし)= M0=0 / M1=0 / M2=0 / M3=0 / M4=0
- 決定対(stored)の PASS_W: M0=0/6 / M1=3/6 / M2=4/6 / M3=3/6 / M4=4/6、clean PASS: すべて0/6(新方式の救済はすべて試聴必須の警告付き)。
- **P-1(M3)とv2(M1)の差**: 全1706行+27正例対で判定が異なる件数=0。本コーパスではv2が余分に出す救済(同形別読み ENGINE_reading_difference / A3_value+pron)は発火せず、v2の実効はほぼP-1(助詞は→わ/へ→え)+桁区切り/値形一致。→ v2とP-1は別方式ではなく **P-1 ⊂ v2** で、評価上は同一機能(二重評価しない)。
- **β(M2)の追加効果**: Primaryの数値garble(8000900/8000句800等の『d×10^k断片+残り』)を、Azureが原稿値を返したときだけ救済(試聴必須)。決定対(stored)でβ固有の増は ms_03 a3 の1本のみ(garble型)。ms_03 a2・reselect a1/a2はβの読み規則=v2読み(Secondary受理経路)による救済でM1と同一。リスク: M0に対するβの増分は、(i)値garble型2行[Secondary=原稿そのもの=最悪露出シナリオのみ]、(ii)音素列が原稿と同一の『詩は/死は+正しい値』3行[PS_same、βがv2読みを内包するため]。両エンジンが同じ値違い・桁違い・助数詞違い・脱落・意味変化を出す場合、片側のみ誤りの場合の増分は0。βは新たにAzure呼出が要る場合がある(p1_value_diffでSecondary未呼出のとき=1clipあたりAzure概算¥0.27〜0.31)。
- **v2(M1)のリスク**: (1) 『月の詩は/死は/氏は/市は + 正しい値』=音素列が原稿と同一のため増分誤PASS扱いの行が出る(事前登録ではNGラベルだったが、音声としては原稿と同一音であり区別不能=by-design。事後分類として開示)。 (2) **真の増分1型**: 『今日は一日中雨→ついたち中雨』(M1/M3/M4)。v2層のVALUE_ONLY経路がPrimary側で不規則読み(一日→ついたち)のガード(V2-1はSecondary側のみ)を持たず、warning付きで受理。Production既存のIRREGULAR_READINGは『一日で→ついたちで』等を既にPASS_Wにする(基準線3b)が、『一日中』は現行NG→新たにPASS_W。実装時はPrimary側にも不規則読みガードを入れて現行判定へフォールバックさせる必要がある(設計案に記載)。
- **共通の限界**: 原稿と表層が同一または既存規則で等価な誤読(橋→箸、今日→京、同形異音、助詞誤読[月はをつきハ等])は、どの方式でもテキストから区別できない(§3b基準線、M0で既に存在)。これは『ASR転写が原稿と同一表記になる音声誤り』であり、ASR Gateの原理的限界(音声の音素列を見ない)。

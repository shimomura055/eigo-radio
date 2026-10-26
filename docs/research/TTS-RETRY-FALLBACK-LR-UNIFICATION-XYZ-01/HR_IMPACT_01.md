# HR_IMPACT_01 — ③採用・LR採用のGate対象化によるHuman Review待ち件数の見込み(R-7)

管理ID: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_03 / 作成: 2026-10-27 00:48 JST / 材料=委任_03のevidence(強制NG条件下の**機構単位**の観測。発生率の測定ではない)

## 1. 結論

- ③またはLRで**音声が採用された**25case(強制NGで③/LRまで到達させたもの)のうち、**Gate(方針Gate or 共有Audio Gate)がBLOCKしたのは4case**。BLOCKしたのは下記の**特定部位に限られる**(他のFamily/部位の③・LR採用は無BLOCKでHR増なし)。
- BLOCKする部位: **X Adv preview③**(`PREVIEW_MINIMAL_FALLBACK`)、**X Adv KP解説③**(`FINAL_STYLE_SHA_MISMATCH_NO_HINT`)、**Y Std本文Voice③**(`STD_FALLBACK_USED_OR_UNKNOWN`)、**Y Adv本文Voice LR採用**(`LOCAL_REWRITE_RECOVERY`)。これらはOPEN-537等の既存fail-closed Gate設計どおり(本委任ではGate不変更)で、③/LR採用音声は人間承認(HR)待ちになる。
- 無BLOCK(HR増なし)の③/LR採用: X Std(topic_intro/body_s/JA/KP英語[WARNINGのみ])、X Adv comment_1③・LR、Y KP/JA/Adv comment LR、Z全部位(narrator chunk・topic_intro_en LR・JA・KP・dialogue legacy③)。
- 終端HR(③/LR後も不合格→STOPPED)は19case: Lock=HUMAN_REVIEW_REQUIRED+HRQ 1行(JA・Zセリフの判定注入caseはdriver限界でHRQ行なしだがLockは作成)+Assemble BLOCK(共有Audio Gate)/ZはGate BLOCK。これは**旧仕様でも③不合格後はHR**で、新仕様の差は「LRあり部位の最大試行が増える(6 TTS/2待機/LR1)」点のみ(HR発生数を増やす方向ではなく、③/LRで救済できる機会が増える方向)。

## 2. ③/LR採用case別のGate結果(実測)

| case | Family/Lv | 方針/leaf | 区分 | 方針Gate | 共有Audio Gate | 方針Gateの内容 | 判定 |
|---|---|---|---|---|---|---|---|
| X-Adv-1 | X/b1b | EN_LR_ADV/L1 | ③採用 | PASS | PASS | BLOCKなし | PASS |
| X-Adv-2 | X/b1b | EN_LR_ADV/L1 | LR採用 | PASS | PASS | BLOCKなし | PASS |
| X-Adv-7 | X/b1b | KP_EXPL/L5 | ③採用 | BLOCK | PASS | BLOCK(kp1_explanation:FINAL_STYLE_SHA_MISMATCH_NO_HINT) | PASS |
| X-Adv-10 | X/b1b | KP_EN/L6 | ③採用 | PASS | PASS | BLOCKなし WARN(KP_EN_ENGLISH_LOCK_FALLBACK_AUDIO_NOT_K2) | PASS |
| X-Adv-14b | X/b1b | EN_LR_ADV/L1 | ③採用 | BLOCK | PASS | BLOCK(preview:FINAL_STYLE_SHA_MISMATCH_NO_HINT+PREVIEW_STYLE_PREFIX_NOT_E1_PREFIXED+PREVIE | PASS |
| X-Std-1b | X/a2 | EN_LR_STD/L3 | ③採用 | PASS | PASS | BLOCKなし | PASS |
| X-Std-2 | X/a2 | EN_LR_STD/L3 | LR採用 | PASS | PASS | BLOCKなし | PASS |
| X-Std-4 | X/a2 | EN_LR_STD/L4 | ③採用 | PASS | PASS | BLOCKなし | PASS |
| X-Std-6 | X/a2 | JA_STD/L7 | ③採用 | PASS | PASS | BLOCKなし | PASS |
| X-Std-8 | X/a2 | KP_EN/L6 | ③採用 | PASS | PASS | BLOCKなし WARN(KP_EN_ENGLISH_LOCK_FALLBACK_AUDIO_NOT_K2) | PASS |
| Y-Adv-1 | Y/b1b | EN_LR_ADV/L1 | LR採用 | PASS | PASS | BLOCKなし | PASS |
| Y-Adv-2 | Y/b1b | KP_EXPL/L5 | ③採用 | PASS | PASS | BLOCKなし | PASS |
| Y-Adv-3 | Y/b1b | KP_EN/L6 | ③採用 | PASS | PASS | BLOCKなし | PASS |
| Y-Adv-4b | Y/b1b | EN_LR_ADV/L2 | LR採用 | BLOCK | PASS | BLOCK(y_voice_1:LOCAL_REWRITE_RECOVERY) | PASS |
| Y-Std-2b | Y/a2 | JA_STD/L7 | ③採用 | PASS | PASS | BLOCKなし | PASS |
| Y-Std-3 | Y/a2 | KP_EN/L6 | ③採用 | PASS | PASS | BLOCKなし | PASS |
| Y-Std-4b | Y/a2 | EN_LR_STD/L4 | ③採用 | BLOCK | PASS | BLOCK(y_voice_1:FINAL_STYLE_SHA_MISMATCH_NO_HINT+STD_FALLBACK_USED_OR_UNKNOWN) | PASS |
| Z-Adv-2 | Z/b1b | Z_DLG_CTX/L8 | ③採用 | PASS | PASS | Z Gate PASS(m2_complete/audio_gate) | PASS |
| Z-Adv-4 | Z/b1b | EN_LR_ADV/L1 | LR採用 | PASS | PASS | Z Gate PASS(m2_complete/audio_gate) | PASS |
| Z-Adv-5 | Z/b1b | KP_EXPL/L5 | ③採用 | PASS | PASS | Z Gate PASS(m2_complete/audio_gate) | PASS |
| Z-Adv-6 | Z/b1b | KP_EN/L6 | ③採用 | PASS | PASS | Z Gate PASS(m2_complete/audio_gate) | PASS |
| Z-Std-2 | Z/a2 | Z_DLG_CTX/L8 | ③採用 | PASS | PASS | Z Gate PASS(m2_complete/audio_gate) | PASS |
| Z-Std-4 | Z/a2 | JA_STD/L7 | ③採用 | PASS | PASS | Z Gate PASS(m2_complete/audio_gate) | PASS |
| Z-Std-5 | Z/a2 | KP_EN/L6 | ③採用 | PASS | PASS | Z Gate PASS(m2_complete/audio_gate) | PASS |
| Z-Std-6 | Z/a2 | EN_LR_STD/L3 | LR採用 | PASS | PASS | Z Gate PASS(m2_complete/audio_gate) | PASS |

## 3. 部位別集計

| 部位・区分 | 採用case数 | うちGate BLOCK |
|---|---|---|
| X/a2 EN_LR_STD/L3 LR採用 | 1 | 0 |
| X/a2 EN_LR_STD/L3 ③採用 | 1 | 0 |
| X/a2 EN_LR_STD/L4 ③採用 | 1 | 0 |
| X/a2 JA_STD/L7 ③採用 | 1 | 0 |
| X/a2 KP_EN/L6 ③採用 | 1 | 0 |
| X/b1b EN_LR_ADV/L1 LR採用 | 1 | 0 |
| X/b1b EN_LR_ADV/L1 ③採用 | 2 | 1 |
| X/b1b KP_EN/L6 ③採用 | 1 | 0 |
| X/b1b KP_EXPL/L5 ③採用 | 1 | 1 |
| Y/a2 EN_LR_STD/L4 ③採用 | 1 | 1 |
| Y/a2 JA_STD/L7 ③採用 | 1 | 0 |
| Y/a2 KP_EN/L6 ③採用 | 1 | 0 |
| Y/b1b EN_LR_ADV/L1 LR採用 | 1 | 0 |
| Y/b1b EN_LR_ADV/L2 LR採用 | 1 | 1 |
| Y/b1b KP_EN/L6 ③採用 | 1 | 0 |
| Y/b1b KP_EXPL/L5 ③採用 | 1 | 0 |
| Z/a2 EN_LR_STD/L3 LR採用 | 1 | 0 |
| Z/a2 JA_STD/L7 ③採用 | 1 | 0 |
| Z/a2 KP_EN/L6 ③採用 | 1 | 0 |
| Z/a2 Z_DLG_CTX/L8 ③採用 | 1 | 0 |
| Z/b1b EN_LR_ADV/L1 LR採用 | 1 | 0 |
| Z/b1b KP_EN/L6 ③採用 | 1 | 0 |
| Z/b1b KP_EXPL/L5 ③採用 | 1 | 0 |
| Z/b1b Z_DLG_CTX/L8 ③採用 | 1 | 0 |

## 4. HR待ち件数の見込み(推定。式と前提を明記)

- 追加のHR待ち/記事 ≒ Σ_(BLOCK部位)[ その部位のclip数 × ③到達率(p) ] + Σ[LR採用clip数 × LR率]。③到達率pはBUDGET_PLAN §4が引く棚卸し実績(Z dialogue「3回以上」6/347=1.7%、JA comment 7/102=6.9%)を**上限寄りの代用**とすると、BLOCK部位のclip数は記事あたり X Adv preview 1 + KP解説 数件(最大5)+ Y本文Voice 1〜2 程度 → **0.1〜0.5件/記事程度(推定)**。
- **注意**: 上記pは旧仕様の実績からの代用値で、統一flow後の発生率は未測定(本evidenceは強制NGのため率を出せない)。実測は量産(自然発生)でのGate BLOCK件数の追跡が必要。
- 低減余地(判断候補ではなく所見): BLOCK部位は③/LR採用音声のStyleを承認profileと照合するGate側の設計に由来する(X Adv KP解説③、Y本文③/LR)。Gate緩和は承認済みGateの変更でありユーザー判断事項(本委任では変更しない)。
- 旧仕様との比較: 旧仕様でもAdv英語・Std本文で③に当たる経路は存在したが、本evidence時点で「旧flowのBLOCK件数」との差分は計測していない(旧flowの再実走は範囲外)。

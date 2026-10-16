# DQI前向き効果観察台帳(DQI_PROSPECTIVE_OBS_01)

作成: 2026-10-16(FAMILY-X-COFFEE-E2E-COST-AND-DQI-FOLLOWUP-01 委任_05)。根拠: ユーザー指示原文§5(`docs/pm/delegation_log/2026-10-16_FAMILY-X-COFFEE-E2E-COST-AND-DQI-FOLLOWUP-01_USER.md`)。
目的: DQIパッケージP(PM_GOVERNANCE 27節)の効果を、今後の実際の受入案件10件で測定する。追加の有料盲検Trialはしない。既知正解の机上評価(`DQI_DESK_EVAL_01.md`)と本観察を混同しない。観察のためだけの受入案件・追加タスクは作らない。10件蓄積時にPM向けにまとめて報告する。Day 5・6の代替ではない(保留維持)。

## 合否基準(原文§5表)
| 指標 | 目標 |
|---|---|
| 重大NGの被覆漏れ | 0件 |
| 承認済み事項の再質問 | 0件 |
| 機械Validatorの誤警告率 | 10%以下(= 誤警告warn数 / 全warn数。warn0件の案件は分母0) |

測定できなかった項目は「未検証」と明示する(未知の重大NGは通常運用では確実に発見できないため、「被覆漏れ0」は『観察できた範囲で0』であり、観察できない漏れは未検証)。

## 観察表
| # | 管理ID/委任 | P1 判定整合行 | P2 仕分け結果(A/B/C/D件数) | P3 抑制件数 | P4 Validator所見(warn数・真陽性/誤警告) | 再質問 | 重大NG被覆漏れ | 備考 |
|---|---|---|---|---|---|---|---|---|
| 1 | PM-20261016-AUW-CLOSEOUT-DQI-PRODUCTION-01 委任_02 | 重大NG=なし | 判断候補なし(0/0/0/0) | 0 | status OK / warn 0 / info 0(`RESULT_PACKET_DQIP2.md`、2026-10-16実走) | なし | 観察範囲で0(未知NGは未検証) | DQI実装案件自体。Validator parsedは判定整合行を検出 |
| 2 | FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01 委任_02A/02B | 重大NG=なし | 判断候補1件[K2 fallback BLOCK化] = 区分C(現依頼と独立)1件 | 1(ユーザーへ未提示。本日ユーザーが原文§4で同趣旨を判断=Open Item管理、OPEN-399) | 02A: OK/warn0(判定整合行検出)、02B: OK/warn0(判定整合行は未検出=パケット書式差、info/warnなし) | なし | 観察範囲で0 | 抑制成功例: C区分を未提示とした判断が、後日のユーザー判断(Open Item管理)と整合 |
| 3 | 同 委任_04 | 重大NG=なし / 提示=証拠のみ | 判断候補1件[7-7費用承認] = 区分A(既判断規則の適用)1件 | 0(1問のみ提示。区分Aだが費用承認手続としてFableが提示) | OK/warn0。ただしparsed.judgment_line=null(パケットに判定整合行が機械検出できる形で無い)。warn/infoは出ていないため誤警告0・真陽性0 | なし | 観察範囲で0 | 7-7費用承認はユーザーが本日JPY205で承認(原文§3) |
| 4 | FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01 委任_06 | 重大NG=なし | 判断候補なし(0/0/0/0) | 0 | status OK / warn 0 / info 0(`RESULT_PACKET_FXPW6.md`、2026-10-16実走、判定整合行を検出[judgment_line parsed]) | 0(Fable記入) | 0(Fable記入) | Fable記入(2026-10-16 委任_07): 重大NG被覆漏れ=0/再質問=0/誤警告=0(Validator warn0、`validator_fxpw6_fable.json` status OK)/P1判定整合行あり/P2仕分け=判断候補なし(Sonnet)→Fable提示=可(試聴依頼のみ)/P3=ユーザー判断事項0件(試聴は既定次工程)/P4=Validator OK。Fable判定=PRODUCTION_WIRED |
| 5 | | | | | | | | |
| 6 | | | | | | | | |
| 7 | | | | | | | | |
| 8 | | | | | | | | |
| 9 | | | | | | | | |
| 10 | | | | | | | | |

## 集計(10件蓄積時に記入)
- 重大NG被覆漏れ: 現在 #1-#3 = 0 / 未検証=未知NG全般
- 承認済み事項の再質問: 現在 #1-#3 = 0
- Validator誤警告率: 現在 warn総数0のため算出不能(未検証)。FXPW2B/FXPW4のようにjudgment_line=nullとなる書式差が機械検出の死角になりうる点は観察事項(P4所見)
- 未検証項目: 未知の重大NGの発見力、warn発火時の真陽性率

## 運用
通常の委任受入記録(Fable)時に1行追記。専用タスクは作らない。

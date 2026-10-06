# ラベル付け見本(旧9 run、RCA22推測ラベルから逐語引用、委任_05c)

位置づけ: `labeling_guide_01.md`に沿った「判定の書き方」の見本。既存ラベル(`labels_old9_from_rca22.json`、`rca_22_sonnet_guess`、確認前)は書き換えない。以下の「見本ラベル」は基準書の手順で書き直した例示であり、既存ラベルとは別物。理由の根拠はrca_open233_e2e_neg7_human_review_01.md §3等の既存記述に依拠。

## A. 不要(true_problem=N、問題なし)
| run/cycle/fact | claim_text(逐語) | 見本ラベル | reason |
|---|---|---|---|
| meta_run03_advanced/1/MUSE-HC-012 | The issue was not that humans made the calls themselves. | N/N/問題なし/rewrite N | 修辞的対比。MUSE-HC-012のnotes(サービス全体を停止したとは書かない等)と矛盾せず、具体的新Factなし。 |
| meta_run03_advanced/1/MUSE-HC-012 | The more useful a service is, the less it should hide the people working behind the scenes. | N/N/問題なし/rewrite N | 一般論(意見)で具体的Factを含まない。 |
| hormuz_run03_advanced/1/HF-009 | At the same time, attacks by the United States and Iran, a sea blockade, and concerns about tanker safety continued. | N/N/問題なし/rewrite N | HF-009の背景要因と同趣旨のつなぎ。主体・方向・規模の変更なし【既存ラベルN、要確認】。 |

## B. 正当(true_critical=Y)
| run/cycle/fact | claim_text(逐語) | 見本ラベル | reason |
|---|---|---|---|
| meta_run03_standard/1/MUSE-HC-011 | It said human staff made inappropriate comments about race during calls. | Y/Y/重大/rewrite Y | MUSE-HC-011は従業員の報告に基づく主張。報告元の限定が落ちると、事実として断定した読みになり、主体・限定条件の誤認(重大)。Ledgerのconditions/notesを逐語確認して確定のこと。 |
| neg3_hormuz_prodrunner_b1b/1/HF-003 | On July 13, Trump posted that all cargo passing through the Strait of Hormuz should provide a 20 percent reimbursement. | Y/Y/重大/rewrite Y | HF-003は具体的制度設計が示されなかったことが核心。範囲(all cargo)・断定の強さを4観点で照合し、Ledgerのscopeとの食い違いで重大と判断する書き方の見本。 |
| neg3_hormuz_prodrunner_b1b/1/HF-009 | The fee plan left the stage, but the events driving oil prices—and the prices themselves—quickly returned. | Y/Y/重大/rewrite Y | HF-009は「一時的に縮小後、ほどなく戻った」。「events driving ... returned」は継続していた出来事を戻ったと読ませる(線引き: 継続→消えて戻った)【既存ラベルY、要確認】。 |

## C. 判断不能(UNDECIDABLE、理由必須)
| run/cycle/fact | claim_text(逐語) | 見本ラベル | reason |
|---|---|---|---|
| neg7_meta_prodrunner_b1b/1/MUSE-HC-004 | Imagine asking AI to book a haircut. | UNDECIDABLE/空/空/rewrite UNDECIDABLE | HC-004は「散髪の予約を依頼できる」。AIが予約を完結と読める軽微な拡張か、問いかけ(修辞)かが曖昧。Hookの許容線に近い。 |
| neg7_meta_prodrunner_b1b/1/MUSE-HC-010 | But users could not know who was really doing the work they had asked AI to do—and their personal information might reach that person. | UNDECIDABLE/空/空/rewrite UNDECIDABLE | HC-010は従業員の懸念。ユーザー一般へ主体を拡張しており軽微〜中。どちらかはHC-010のnotesの読みに依存するためFable確認へ。 |
| neg1_meta_b3prod_a2/1/MUSE-HC-008 | A human can handle situations that AI alone finds difficult. | UNDECIDABLE/空/空/rewrite UNDECIDABLE | 一般化か具体的Factかが曖昧(HC-008との範囲の照合が要る)。 |

## D. 線引き例(参考、既存SSOT)
- Meta-1/Meta-2「Also, some calls needed user information to continue.」: 軽微(QUALITY)、Safety-critical外。
- A4-1「actually speaking with human staff」(MUSE-HC-012): 問題なし(ACCEPTABLE)。

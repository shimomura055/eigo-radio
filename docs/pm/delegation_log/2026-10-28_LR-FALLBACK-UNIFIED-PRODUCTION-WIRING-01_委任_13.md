# 委任_13(Phase B / B8): 正式runtime evidence(Family×Level×Role別)=保存run読取再評価(API 0)+承認済みevidence driverによる最小有料実走(見積≤¥40、Cap: 本委任¥60)

共通事項=`…_委任_00_COMMON.md`。前提=統合配線commit(委任_11)完了後。設計=`W1_ROUTE_WIRING_AND_RECORDS_01.md` §3(再現手段表、`docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/tools/tru_ev_*.py`)+`INTEGRATION_01.md` F-15+ユーザー原文§10(受入12条件、「コード配線のみ・DEV動作のみ・単体testのみではPRODUCTION_WIRED不可」「各Family・Levelで証拠を区別」)。成果物=`docs/research/LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01/B8_RUNTIME_EVIDENCE_01.md`。

## 作業
1. **読取再評価(API 0)**: 配線後HEADで保存run(X: AI島hr_02・Word Gacha・Coffee等/Y: E-1 run_01・redelivery_fee_03/Z: 告げ口心臓run_reselect_01・メロス_02・猿の手・tru_ev evidence run群)に対し、正式Gate関数(M3/Y gate/Z run_audio_gate)+三者一致Gate+ledger+最終Human報告生成を**実関数で**実行し、Family×Level×Role別に「正常LR→通過(警告)」「正常Fallback→通過(警告)」「異常Style/記録欠落/品質NG/parity不一致→停止」「発動なし→不変」の実証表を作る。
2. **最小有料実走**: 承認済みdriver(`tru_ev_*.py`、正式経路・既定profile)で、配線後に**初回Production経路で発火**する証拠が不足する経路を選び実走(優先: X Std/Adv本文LR 1件・Y本文Fallback 1件・Z narrator LR 1件・JA短文Fallback 1件・KP_EN ENGLISH_LOCK 1件。W1 §3の実費表で合計≤¥40を事前記録。stop sentinel確認・`--approved-budget-jpy`明示)。各実走で(a)`final_adoption`が記録される(b)ledger導出(c)Gate判定(d)overlay表示(e)最終Human報告(赤/青)(f)注記混入0、を確認。retry/fallback/regeneration/resume経路: resume(途中kill→再開)1件をmock優先・必要なら有料1件で確認(M-4のLR根拠復元)。
3. 未実走9行(W1 §3)の扱い: shell固定英語3=表外・固定mp3=生成なし、残り(Y chunk 2/Z legacy会話2/shell日本語2)は見積(各¥0.3〜3)内で実走、超過見込みなら「未観測」と明記(実証済みと書かない)。
4. 受入12条件(原文§10)の各項へ証拠(file:line/run path/sha先頭8桁)を対応付けた表。**PRODUCTION_WIRED判定はFableが行う**(本委任では「判定材料」と書く)。
5. 実費: `cost_log`実測、Cap¥60・日次1,000円内。超過見込みなら実走前にSTOPして報告。
6. Git: 成果物+evidence run(軽量な記録のみ、wavは既存規則に従う)のみ`git add`、commit「LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01 委任_13(B8): runtime evidence(読取再評価+最小有料実走 実費¥N)」+`Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`、`git push origin HEAD:main`。
7. 最終応答: 成果物パス+Family×Level別の要約(各1行)+実費+未観測一覧。

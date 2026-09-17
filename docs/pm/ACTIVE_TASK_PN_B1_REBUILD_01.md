# ACTIVE_TASK: USER-TEST-PERSONALIZED-NEWS-B1-REBUILD-01

管理ID: USER-TEST-PERSONALIZED-NEWS-B1-REBUILD-01
Status: IN_PROGRESS (RESEARCH開始)
Lock: docs/pm/locks/audio_stage.lock 取得済み(このタスクのみ)
Budget cap: ¥400
T-0 delegation check: FAIL(既知パターン、実行コマンド全文セクション欠落等。継続)

## 工程チェックリスト
- [x] T-0 delegation log + check (FAIL, 継続)
- [x] lock取得
- [x] cost logger install
- [x] A2 sha256 baseline記録(開始時、a2_baseline_sha256_before.txt)
- [x] Research (Phase1+Part2、¥115.80)
- [x] Ledger更新(verified_fact_ledger.txt、Writer供給用は政治的態度研究を意図的に除外、
      監査用全文はledger_full_documentation_with_staleness_analysis.txt)
- [x] B1再生成(main_b1_2v write_new_theme、r8で0 leakage/Fact PASS/LEDGER_COMPLIANT、
      r1-r7はTension leakage residualで破棄、教訓・cost記録済み)
- [x] Comment Contract(r8内で自動実行、PASS/LEDGER_COMPLIANT)
- [ ] Key Phrase / 日本語タイトル
- [ ] TTS / ASR
- [ ] Assembly / Gate
- [ ] player.html / unified.html / E2E check
- [ ] A2 sha256 final確認(非変更)
- [ ] SSOT反映(DECISION_LOG/OPEN_ITEMS/ARTIFACT_REGISTRY)
- [ ] RESULT_PACKET作成
- [ ] git commit/push
- [ ] lock解除

## コスト実測(進行中、上限¥400)
Research(Part1+Part2)=¥115.80。Writer試行r1(3attempt、旧ledger構成)=¥50.55。
r2-r7(Tension leakage是正試行、いずれもSTOP/破棄)=¥20.92+17.81+33.67+25.57+12.01+29.24=¥139.22。
r8(成功、Comment Contract込み)=¥15.03。**小計=¥320.60**。残予算≈¥79.40。
TTS/ASR/KeyPhraseで¥36-70程度を見込む(旧B1 2V episode実績¥36.54)ため、¥400上限に
近接する見込み。超過した場合は実額を正直に報告する(既存予算超過時の扱いはUSER_DECISION_
REQUIRED、Fable/ユーザー判断)。

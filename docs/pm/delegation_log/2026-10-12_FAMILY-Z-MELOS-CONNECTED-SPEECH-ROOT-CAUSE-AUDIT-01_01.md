# FAMILY-Z-MELOS-CONNECTED-SPEECH-ROOT-CAUSE-AUDIT-01 委任_01 (2026-10-12)

## 結果
0. STOP: STOP_NOTICE(別run_e2e_01スコープ)確認、STOP/STOP_ALL不在。runner/TTS/有料API起動0。
1. 結論: 先行『D機械判定不能』を C(設計上の不足、主)+A(減速後救済欠落、是正済み)+D残余 へ訂正。B1 CS Validator(Pattern A)は配線・実発火済み(Melos案件で5回ACCEPT、うち4回Melos clip。Std a2 part1_c5 fallbackでAzure=Melo→ACCEPT)。Equivalence LayerはMelos案件で0回(TRUE_CONTENT_MISMATCH限定+CMU OOV)。
2. Std a2 part1_c5: 減速前に2回PASS(Tier3、Pattern A)→減速後STOPPED(旧コードの救済欠落)。Adv b1b: ASR全転写がMello/Mellow、Local Rewrite実行(候補5件不通過)→HR。
3. entity gate先行問題: 実データ26pair/合成108pairで『Validatorが受理できたのに遮られた』0件。限界は綴り水準のPattern A定義(stem同音の別綴り)。
4. 汎化: exact stem drop 108/108 PASS、反例誤PASS 0。実データはMelos 17/18でMelos以外無し。
5. 実施: Productionコード変更0。新規test `er026_cs_audit_regression_01_test_01.py` 12件PASS、既存CS関連test PASS。SSOT: DECISION_LOG追記、OPEN-327/328新規、OPEN-318/320/322追記、CURRENT_SPEC記述訂正2箇所、ROOT_CAUSE_01.md 11節訂正。
6. 費用: JPY0(local faster-whisperのみ)。
## 要判断
- OPEN-327(C案、Trial+Opus必須)、OPEN-328、有料検証案(上限JPY10、未実行)。
- 副作用: 初回オフライン再評価が共有 er021 telemetry.jsonl へ約1,675行追記(7155→9155、他agent約325行混在)。整理は権限外(自動承認で拒否)のため未実施。以後no-op化。
## 証跡
`er026_output/family_z_production_e2e_01/melos/cs_audit_01/`(CS_AUDIT_01.md ほか)

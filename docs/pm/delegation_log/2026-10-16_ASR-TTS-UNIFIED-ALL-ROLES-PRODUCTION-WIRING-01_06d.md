# 委任_06d: AUW — 残Section/Familyの実音声evidence(①〜④)+是正後経路の実音声確認+legacy A費用記録の是正

場所: `C:\Users\tensh\eigo-radio`、branch `feat/auw-unified-asr-01`(HEAD e81696197)。main禁止。禁止git操作: `add -A`/`-f`/`stash`/`reset --hard`/`checkout -f`/`clean`/`rebase`/`amend`/`force push`。**費用上限 JPY 45**(各run前にstop_scope_check rc=0と累計記録、超過見込みで停止)。全有料経路にcost logger/wrapper記録(校正済み単価)を事前確認(06b D-B3の教訓: 単価の妥当性もtoken実測で確認)。実Production HR queue/Lock/共有stateへの書込は隔離(06bのD-B1/D-B2を再発させない。run後に共有state md5・JA queue 2ファイルの行数不変を確認)。

## Fable判断(前提)
- 06c(A): HR Lock record_outcomeの技術STOP早期returnは実施しない(U4としてユーザー判断事項。現行はSecondary障害のみの最終STOPPEDがLockに入る安全側挙動を逸脱として記録)。
- 06c(B): results cache DIFF 16件は再利用時動的guardで再生成へ回す現行実装を採用。偽陽性の可能性(「いちばん/一番」、装飾記号)は委任_07でOPEN化。
- 06c(C): legacy A(er003_v1_n3_01_tts_generate.py main())がcost logger未installのまま初回Secondaryで停止する件は本委任で是正(E)。

## T-0
委任文を本ファイルへ全文保存、checker→_check.json(FAILでも継続)。

## 参照
RUNTIME_EVIDENCE_06.md §12-7(残作業①X a2 KP[KGCPW前提] ②Family B B1全体・Hook/Tension/Closing・見出し ③C Comment(JA)・JA title ④Dialogue(Std)・KP phrase 4回構成の通算上限runtime)、IMPLEMENTATION_06c.md、er078_auw_runtime_evidence_06b.py、ユーザー原文_01.md L201-215。

## やること
A. 残Section実音声①〜④(06bと同runner方式)。①X a2 KP(KGCPW gloss Gate停止時はGate迂回せず「既存Gate停止」記録、gloss整合済み既存KP入力があればそれで実行)②Family B B1全体+Hook/Tension/Closing+見出し(pro-preview-tts単価を事前計上)③C Comment(JA)+JA title ④Dialogue(Std)減速後NG→取り直し→通算3回runtimeと、KP英語phrase 4回構成の通算上限runtime(既存例外維持確認)。各clipにasr_judgement有無・state・Secondary回数・重複0・費用。
B. 是正後経路の実音声: (a)非ラテンKP救済(can't wait/30 percent等、Primary非ラテン転写)→PASS_WITH_WARNING採用、採用転写への否定差/値DIFFはNG_PROTECTED。自然発生しなければ保存Azure転写+実Primaryで再現し「半実音声」明記。(d)技術STOP=実Secondaryをmock障害化し最終slotまで到達、TECHNICAL_STOP_SECONDARY_UNAVAILABLE+[TECHNICAL_STOP]報告+(現行では)leaf HR Lockに入る事実を記録(U4材料)。(e)導出失敗表示=registry失敗模擬で最終ページに「導出失敗(要確認)」。
C. 再利用経路の実動作: Master Store/結果cache再利用1件でer078_reuse_value_guard_01が動き、DIFFなら再生成、EQUALなら再利用+asr_judgement_inherited記録を実runで確認(blocklist 16件のうち1件を意図的に再利用対象、費用は再生成1 clip分)。
D. 15条件対応表更新: RUNTIME_EVIDENCE_06.md §13「委任_06d」に43行マトリクスの実音声カバレッジ最終版と条件1〜10の充足/一部/未充足(残作業と費用)。
E. legacy A費用記録是正: er003_v1_n3_01_tts_generate.py main()(同経路でcost logger未installの他legacy entryも、Grep cl.install/init_loggerで確認)にProductionと同じcost logger installを追加(新単価は追加しない)。test: legacy A経路でSecondary呼出時に費用記録されRuntimeError停止しないこと。実音声1 clipで記録確認。
F. 06c(A)の逸脱記録と06c(B)のOPEN候補をRUNTIME_EVIDENCE_06.md §13に明記(委任_07がSSOT転記)。
G. commit/push(branch、明示add、secret_scan --staged hits=0)。message: `ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 委任_06d: 残Section/Family実音声(X KP/B B1・見出し/C JA/Dialogue通算3回/KP4回)+是正後経路(非ラテンKP・技術STOP・導出失敗表示・再利用guard)実音声+legacy A費用記録是正。main無変更、JPY <実額>`。

## STOP
誤受理・数値/否定の誤PASS・旧PASS→新NG 1件でも/HR Lock・共有stateへの未隔離書込/費用JPY45超過見込み/Gate迂回が必要になる場合。

## 報告様式(受入記録5項目)
(1)当初目的=原文L201-215逐語(ファイル:行) (2)成果物 (3)証拠(run path・件数・費用実額と出典) (4)15条件ごと+A〜Gごとの一致/不一致 (5)判定材料(宣言しない)。加えて逸脱・累計費用(06+06b+06d)・委任_07申し送り。

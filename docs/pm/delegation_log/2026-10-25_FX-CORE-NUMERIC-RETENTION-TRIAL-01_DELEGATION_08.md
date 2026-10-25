FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_08(委任_07の残工程を完了: 月の記事run_ms_03の音声証跡確認→完成候補ページ→SSOT→RESULT_PACKET→commit/push→最終報告)。あなたはsonnet-worker。Fable(PM)からの委任。

## 背景
委任_07(別agent)は、v4+J2のProduction配線(commit 44b18d41a、45 test、回帰で自案件起因の失敗0)と月の記事の本文段(正式経路run_ms_03、実費25.43円: 欄=約42〜46m、R0〜EN Std/Advで保持、B3再実行0、Gate発火0、J2がR1/R2で範囲各1件を正規化、記号QA指摘0)まで完了し、音声段(PID 15170、12:31:34起動)の完了待ちで中断した。残工程の準備物がscratchpadにある(`ssot_edit.py`、`spec_section.md`、`active_task_edit.py`、`active_task_line.txt`。場所は`C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\scratchpad\`配下を探す)。委任_07のagentが一部を再開して進めた可能性があるため、**まず現状を確認し、済んでいる工程は重複して行わない**。

## 手順
1. 現状確認(API 0): `git log --oneline -15`で44b18d41a以降の本件commit有無、`er019_output/moon_shrinking/run_ms_03/`の音声段完了状態(全wav・assembly・gate結果・page_verify、process 15170の生存=`tasklist`で確認、**生きていれば終了を待つ。終了させない**)、`user_test/family_x_moon_shrinking_02/`の有無、`docs/research/FX-CORE-NUMERIC-RETENTION-TRIAL-01/WIRING_RUNTIME_EVIDENCE_01.md`の§5有無、SSOT(OPEN-507/509/514、CURRENT_SPECの新節、DECISION_LOG、UDR #194/#195)の反映有無、`docs/pm/RESULT_PACKET_FXNR7.md`の有無。
2. 音声証跡(未了なら): run_ms_03のAdv/Stdで「約42から46メートル」を含むsegmentのASR転写(「から」で読まれ、波ダッシュ由来の「なになに」が無いこと)、Gate結果(PASS/HR Lock/retry)、英語Std/Advの"42 to 46 meters"のASR一致、数字丸め仕様の正常動作、費用(音声段実費、方式追加分)、処理時間。`WIRING_RUNTIME_EVIDENCE_01.md` §5へ記録。
3. 完成候補ページ(未了なら): `user_test/family_x_moon_shrinking_02/`に既存標準形式で生成(**既存公開ページは差し替えない**、完成候補・ユーザー試聴待ちの注記)、push後HTTP 200と再生確認。
4. SSOT(未了なら、scratchpadの準備物を再Readして現在のSSOTに最小Editで適用): CURRENT_SPEC新節(v4+J2正式仕様・適用範囲・E=∅/M1最終違反/Gate不足の既定動作・runtime evidence項目・原価)、OPEN-507=`WIRED_PENDING_FABLE`、OPEN-509=J2配線で解消(Normalizer残置の関係を記録)、新規OPEN-514(内容は準備物どおり。11-8分類付き)、DECISION_LOG、UDR #194/#195実施記録。編集直前再Read・バックアップ・`git diff --stat`。
5. `docs/pm/RESULT_PACKET_FXNR7.md`(委任_07の内容を集約)、ACTIVE_TASK自行。委任文逐語保存: 抽出tool(index 550前後、冒頭「FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_08」で照合、±6)→`..._DELEGATION_08.md`。
6. Git: 対象pathのみadd(`-A/-u/-f/-N`禁止)→`git diff --cached --name-status`→`git commit --only`→`git push origin HEAD:main`。wav/raw_usage_log不追跡(公開mp3は`user_test/`配下のみ)。secret grep 0件。並行agent(Chunk配線がer019 TTS関数・er063・er026を編集中、Part 1 T1配線)との衝突: 本委任はProduction fileを編集しない。

## 報告(Fableへ、ユーザー§7の簡潔形式)
(1)Production Wiring完了Status候補と受入条件充足表(配線/Std・Adv正式runtime/retry・fallback整合/必須test/承認内容と実動作の一致/SSOT/Git/判断待ち・Dangling無し) (2)中核数値保持・J2・数字丸めのruntime evidence要約(本文段+音声段: 欄・各段の数値・J2適用・記号QA・ASR読み・Gate・費用) (3)回帰結果 (4)制作時間・量産単価への影響(実測、Trial推定4円との比較、方式追加分) (5)残存リスク・Open Item(C-1候補、半導体型初回選定の観察、C-2結果、O-2'桁付き通貨の穴の修正状況=委任_07で対処済みか確認して記載) (6)Git/SSOT・commit・raw URL (7)月の記事 完成候補の試聴URL (8)RESULT_PACKET 4行+「判定整合」1行。
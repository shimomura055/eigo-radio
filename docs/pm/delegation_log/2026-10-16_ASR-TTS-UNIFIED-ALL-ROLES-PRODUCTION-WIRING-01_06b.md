# 委任_06b: AUW — 受入条件1・2・4・7・9の未充足分を埋める実音声runtime evidence(残Section・残Family・最終ページ組込)

場所: `C:\Users\tensh\eigo-radio`、branch `feat/auw-unified-asr-01`(HEAD 7bb4e5d1a)。main禁止。禁止git操作: `add -A`/`-f`/`stash`/`reset --hard`/`checkout -f`/`clean`/`rebase`/`amend`/`force push`。費用上限 JPY 80(有料API合計。各run前にstop_scope_check rc=0、各run前に累計を記録、超過見込みで停止・報告)。全経路の費用記録を事前確認: 委任_06の逸脱D1(STANDARD TTSがcost loggerに未記録)を踏まえ、TTS/Primary ASR/Secondaryすべてにwrapper記録を入れてから実行(記録できない経路は実行しない)。HR Lock既存状態の迂回・解除禁止。

## T-0
委任文を本ファイルへ保存、checker→`_check.json`(FAILでも継続)。

## 参照
- ユーザー原文`2026-10-15_..._01.md` L201-215(15条件、開いて逐語引用)、L143-153(Section固有例外)。
- `RUNTIME_EVIDENCE_06.md` §3、§10・§11、`er078_auw_runtime_evidence_06.py`、`evidence_06/`。
- `APPLICABILITY_MATRIX_01.csv`(全Family×Section 43行)。

## やること
A. 残Sectionの実音声(Family Zの`run_tts_stage`に小さなClipSpec、各Section 1 clip以上、EN/JA双方存在は両方): Topic Intro/Preview/In One Line/Point見出し(見出し例外維持)/KP phrase/Local Rewrite経路(ENのみ: Primary NG→Secondary NG→再生成→3回NG→LR→v1 Secondary確認。JAはLRなし→HR)/b1b levelのZ narrator。各clipでasr_judgementの有無・state・Secondary呼出数・重複0・費用を表に。
B. 残Familyのend-to-end実run: Family X・B・C・A(legacy n3)のProduction runnerを最小構成(2〜4 segment)で実行し、(i)統一judge経由asr_judgement (ii)pass_with_warning_listening_list.jsonとページ節 (iii)X/Zの最終組込HTMLに事後試聴リスト節(0件節含む) (iv)共有state md5無変更 (v)HR Lock非抵触を確認。費用がJPY 80に収まらない場合は最安1 Family完全組込+他はsegment単位、未実施分を明記。
C. 条件4(3回NG→LR/HR)の実音声: KP解説以外で1 Section(EN narrator)で3回NG→LR(EN)→v1 Secondary確認の経路。JAは3回NG→HR(LRなし)1件。
D. 対応表更新: RUNTIME_EVIDENCE_06.md に§12「委任_06b追加evidence」と15条件対応表更新版。未充足は残作業と費用見込み明記。
E. 誤受理0・数値/否定誤PASS 0・旧PASS→新NG 0の集計を継続。1件でも発生で即STOP報告。
F. commit/push(branch、明示add、secret_scan --staged hits=0)。message: `ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 委任_06b: 残Section・残Family(X/B/C/A)・最終ページ組込の実音声evidence+3回NG→LR/HR実経路。main無変更、JPY <実額>`。

## 報告様式(受入記録5項目)
(1)当初目的=原文15条件の逐語(ファイル:行) (2)成果物 (3)証拠(run path・件数・費用実額と出典ログ:行) (4)15条件ごとの充足/一部/未充足 (5)判定材料(宣言しない)。加えて逸脱・委任_07申し送り・累計費用(06: 約JPY9.2+06b)。

(注: 本ファイルは受領した委任文の要旨保存。)

# PM-SSOT-MERGE-REGRESSION-REPAIR-01 AUDIT_01 (2026-10-31, API 0)

## 方法
- 対象: origin/main(af0236f4f)のOPEN_ITEMS.md/DECISION_LOG.md/CURRENT_SPEC.md。2026-10-31以降にOPEN_ITEMS.mdを変更した全commit(+直前基準commit)から OPEN-627〜638 の行を抽出し、行ごとの履歴(commit順)を作成。
- 各履歴版について、12文字shingleの欠落数を現行行と比較(欠落>15を要確認)。欠落部分を目視し、「後続commitによる正当なStatus更新」か「退行」かを判定。DECISION_LOG/CURRENT_SPECは、各commit版にあって現行に無い行(sort -u | comm)を列挙。
- OPEN-638は存在しない(最大はOPEN-637)。

## 退行一覧(OPEN_ITEMS.md)
| 行 | 退行commit | 失われた文言 | 復元元 |
|---|---|---|---|
| OPEN-630 | 37edbd86e(KP-RESCUE merge、mergeで6827ff051版=委任前の旧文面を採用。以後d84cff09c等でも継承) | ステータス欄の「案B3=REJECTED(2026-10-31ユーザー決定、理由=副作用による既存訳の品質悪化リスク。現行の訳生成Prompt・仕様[X2p' gloss生成]は維持)。後続=OPEN-636(JA-GLOSS-QUALITY-ALARM-TRIAL-01)。以下は決定前のTrial記録(数値は不変)」。現行は「Trial(Status案=VALIDATED[条件付き]。未承認...採否=ユーザー判断)」に退行(採否が未決に見える) | 5434d470a(JA-GLOSS-QUALITY-ALARM-TRIAL-01 委任_01(1/2)) |

### 一時的退行(中間commitでのみ発生、現行mainでは解消済み・対応不要)
- OPEN-627: 377fce501(39d3e1d45より後の旧版を採用)→16cef644f/2b2f172c1で解消。現行は2b2f172c1の最新版。
- OPEN-631: 7df2b5720/3a0bf398f の相互に旧版 → 37edbd86e/d84cff09c で両保持。現行は9f6e8a206+7df2b5720内容を両方含む(shingle欠落0)。
- OPEN-632: 7df2b5720/37edbd86e で旧版へ退行 → 7e19fa537で復元済み(現行は PRODUCTION_WIRED_PENDING_FABLE を含む最新版)。
- OPEN-636: cd49297ae で旧版(5434d470a)へ退行 → 5046ae593・099cee4e5で解消(現行は委任_02A最新版)。

### shingle欠落の目視結果(退行ではない)
OPEN-627(c6f9b3fe6/dea4439a4/39d3e1d45)、OPEN-629(377fce501)、OPEN-632(c9fac776f/a4ac0c3c7/cd49297ae)、OPEN-636(5434d470a): 後続委任のStatus更新で置換された旧Status文言のみ。情報の減少ではない。

### 欠落なしの確認
OPEN-628/633/634/635/637: 履歴1版のみ(または同一)で現行と一致。

## DECISION_LOG.md
- 2026-10-31の各commit版にあって現行に無い行: 「状態: APPROVED_FOR_PRODUCTION(...PRODUCTION_WIREDはFable独立受入後)」系の旧状態行のみ(OCCURRENCE-COUNT DECISION-02/TWO-TIER DECISION-01が後続で更新された正当な置換)。欠落エントリなし。
- 存在確認(現行main): JA-GLOSS-QUALITY-ALARM-TRIAL-01-DECISION-01 あり(末尾付近、見出し形式が他と異なる点のみ注意) / SELECTION-UI-OCCURRENCE-COUNT-01-DECISION-01・02 あり / DISK-GUARD-AUTO-CLEANUP-01-DECISION-01 あり / ASR-FLAP-T-PRODUCTION-WIRING-01-DECISION-01・02 あり / SELECTION-UI-TWO-TIER-01-DECISION-01 あり / FX-UNTIDINESS-COMMENT4-JA-GLOSS-FIX-01-DECISION-01 あり / KP-RESCUE-REJUDGE-REVERT-SURFACE-FIX-01 あり。
- KP-N5-PHRASE-COVERAGE-AUDIT-01・KP-N5-EXTRACTION-ROOT-IMPROVEMENT-TRIAL-01 のDECISIONエントリ: 2026-10-31のどのcommit版のDECISION_LOG.mdにも存在しない(a8712f58d/ba952a7ee はDECISION_LOGを変更していない)。退行ではなく元々未記録(両件はTrial・調査でユーザー決定を伴わないため、記録対象外の可能性が高い)。

## CURRENT_SPEC.md
- 各commit版にあって現行に無い行は、occ-v1節(委任_02版→委任_02/03版へ置換)、TWO-TIER節(377fce501版→現行3253行へ更新)のみで、いずれも後続版が現行に存在(3253/3254行)。欠落節なし。
- occ-v1節: 現行3254行に存在。Flap-T節・2026-10-30追記(KP-GENERALIZATION N5、2052行)も存在。

## JA-GLOSS-NUANCE-01/TRIAL_01.md
- §9「結果の採否: REJECTED(ユーザー決定2026-10-31)」は現行mainの141行目に存在(659ddaf80時点)。欠落なし。

## 復元
- OPEN-630行を5434d470a版の行へ置換(他Workerの後続追記は6827ff051版以降なし=現行行と6827ff051版が完全一致を確認)。

## 再発防止案(提案のみ・未実装)
Worker規約案「SSOT追記規約」:
1. SSOT(OPEN_ITEMS.md/DECISION_LOG.md/CURRENT_SPEC.md)の追記は、push直前に `git fetch origin` し、最新origin/mainを新たにcheckoutした上で、自分が変更する行/節だけを再適用する。`git merge`/`git pull`でSSOTの競合解決をしない(mergeの機械的解決が旧文面を採用する事故: 37edbd86e)。
2. push拒否時は、再度origin/mainをcheckoutして差分を再適用(最大3回)。
3. push前に自分が触れた各OPEN行について「origin/main版の行が自分の編集の基底と同一か」を確認する(基底と異なる=他Workerが更新済み→その内容を保持して連結)。
4. push後に `grep -n "^| OPEN-<N> |"` で自行のStatusがorigin/mainに含まれることを確認する。

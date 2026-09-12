# PM-TOKEN-EFFICIENCY-DELEGATION-TRIAL-AFTER-MEASUREMENT-01(read-only実測)

管理ID: `PM-CLOSEOUT-CONSOLIDATION-98-3V-PHASE1B-04-UDR-RECORD-OPUS-L3-AND-DELEGATION-TRIAL-AFTER`
(Part C)、2026-09-12、Sonnet、実測¥0(offline read-only集計のみ)。判定語(VALIDATED等)は付けない。

## 要点(5行)

1. E-1/D-1/G-1条項付きで委任した直近6管理ID(CONSOLIDATION-95再開・ER-009再開・
   3V Phase1b-04[再開+修正1〜3回目、同一ID]・CONSOLIDATION-96・97・Opus L3
   packet作成)を対象に、`er011_pm_agent_read_audit_01.py`(無変更)+Fable転記
   `<task-notification>`からのusage抽出(別途軽量スクリプト、repo外scratchpad)で
   委任文字数・tool_uses・subagent_tokensを実測した。
2. **6管理IDの委任(delegation)総数14件、tool_uses合計981回、subagent_tokens合計
   1,831,844 token、Fable→Sonnet委任文字数合計36,930字**。
3. **Sonnet側の同一ファイル重複読込比率が実測できたのは6件中1件のみ**
   (`EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1B-04-GENERALIZATION-
   AND-REGRESSION`、6delegationのうち転記が現存したのは2件のみ)。残り5件は
   対応する`tasks/<id>.output`が全て0バイトで抽出不能(Part Aで発見した
   `a3fc1b9e17aa0c9ac.output`0バイトと同一の事象パターン)。
4. 現存2件で実測した重複比率は**37.5%(103,227字/275,193字、内訳49.5%・
   28.3%)**。Before(Phase 1実測、`PM-TOKEN-EFFICIENCY-SUBAGENT-TOKEN-
   CONSUMPTION-BY-TASK-TYPE-01_REPORT.md`、18件合計27.8%)と比べると、
   今回のN=2はBefore値より高いが、Before/Afterともにサンプル数が少なく
   (18件・2件)、E-1/D-1/G-1の効果を判定できる統計的な材料ではない
   (判定語なし)。
5. 品質・ルール遵守は「Fable差し戻し回数/ルール逸脱件数」欄を設けた。
   3V Phase1b-04のみ差し戻し3回(Leakage 2/2再現によるループ上限到達→
   Opus L3診断)が記録上明確、他5件は差し戻し0(初回で完了)、ルール逸脱は
   6件とも記録上0件(不明ではなく、既存SSOT・MODEL_ROUTING_TRIAL_LOGに
   逸脱記載なしを確認した上での0件)。

## 1. 対象6管理ID

| # | 管理ID | 内容 |
|---|---|---|
| 1 | `PM-CLOSEOUT-CONSOLIDATION-95-OPEN-121-SYMMETRIC-NORMALIZATION-WIRING-TRIAL-12-A2-ASSEMBLY-AND-SSOT` | CONSOLIDATION-95再開 |
| 2 | `ER-009-JA-READING-DICTIONARY-ACRONYM-EXPANSION-AND-TREND-A2-RESUME-01` | ER-009再開 |
| 3 | `EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1B-04-GENERALIZATION-AND-REGRESSION` | 3V Phase1b-04(初回+修正1〜3回目、同一ID) |
| 4 | `PM-CLOSEOUT-CONSOLIDATION-96-TRIAL-12-A2-COMPLETION-ER-009-WIRING-USER-ANSWERS-AUTONOMY-RULES` | CONSOLIDATION-96 |
| 5 | `PM-CLOSEOUT-CONSOLIDATION-97-ARTICLE-CLOSE-REQUIRES-USER-LISTENING-AND-STANDARD-PLAYER-AUDIT` | CONSOLIDATION-97 |
| 6 | `EDITORIAL-B-FAMILY-VOICES-3V-PHASE1B-04-OPUS-L3-DIAGNOSIS-01` | Opus L3 packet作成(Sonnet分) |

## 2. 方法

- 委任文字数・tool_uses・subagent_tokens: Fable本体転記
  (`294958fe-da6e-491c-8a02-4f864d8195c8.jsonl`)を1回走査し、`Agent`/`Task`
  tool_useの`prompt`から管理IDを正規表現抽出(`er011_pm_agent_read_audit_01.py`
  の`extract_mgmt_id`と同一パターン)、`<task-notification>`ブロックの
  `<tool-use-id>`で突合。同一task-idの重複通知は最終(最大)値のみ採用
  (`PM-TOKEN-EFFICIENCY-SUBAGENT-TOKEN-CONSUMPTION-BY-TASK-TYPE-01`と同じ
  補正方針)。一時スクリプトはrepo外scratchpadのみに保存、Git管理外。
- Sonnet実読込文字数・重複比率: `er011_pm_agent_read_audit_01.py`(無変更)を
  実行し、`per_agent_task_summary.json`/`per_call.jsonl`から対象6管理IDに
  該当する`subagent:*`行のみ抽出。重複比率はBeforeと同一方式(1つの
  subagent転記[=1回のSonnet実行]内での同一ファイル2回目以降Read/Grep/Bash
  cat文字数の比率)。

## 3. 結果表

| 管理ID | delegation数 | tool_uses | subagent_tokens | Fable→Sonnet委任文字数 | Sonnet実読込文字数(転記現存分) | 重複比率(転記現存分) | Fable差し戻し回数 | ルール逸脱件数 |
|---|---|---|---|---|---|---|---|---|
| CONSOLIDATION-95再開 | 2 | 102 | 282,352 | 7,398 | 不明(転記0バイト) | 不明 | 0 | 0 |
| ER-009再開 | 2 | 103 | 156,265 | 5,451 | 不明(転記0バイト) | 不明 | 0 | 0 |
| 3V Phase1b-04(同一ID、初回+修正1〜3回) | 6(転記現存2) | 393 | 661,940 | 12,448 | **275,193字**(2件合計) | **37.5%**(103,227字/275,193字、49.5%・28.3%の2件) | **3**(Leakage 2/2再現でループ上限到達) | 0 |
| CONSOLIDATION-96 | 1 | 182 | 274,169 | 4,937 | 不明(転記0バイト) | 不明 | 0 | 0 |
| CONSOLIDATION-97 | 1 | 143 | 245,392 | 3,201 | 不明(転記0バイト) | 不明 | 0 | 0 |
| Opus L3 packet作成(Sonnet分) | 2 | 58 | 211,726 | 3,495 | 不明(転記0バイト、Part Aで発見した`a3fc1b9e17aa0c9ac.output`含む) | 不明 | 0(診断目的のためFable差し戻し概念なし) | 0 |
| **合計** | **14** | **981** | **1,831,844** | **36,930** | 275,193(6件中1件のみ実測可) | — | 3 | 0 |

## 4. Before(Phase 1実測)との比較

| 指標 | Before(Phase 1、`PM-TOKEN-EFFICIENCY-SUBAGENT-TOKEN-CONSUMPTION-BY-TASK-TYPE-01`) | After(本測定) |
|---|---|---|
| 実測サンプル数(転記現存・重複比率算出可能) | 18件(254件中7.1%) | 2件(6管理ID・14 delegation中) |
| 重複読込比率(合算) | 27.8%(839,754字/3,024,137字) | 37.5%(103,227字/275,193字) |
| 転記消失率 | 92.9%(236/254件) | 85.7%(12/14 delegation) |
| 種別平均token(参考、Before全254件の種別別、(a)Consolidation平均130,578/(d)Production配線平均207,506) | 上記参照 | 本測定6管理IDのsubagent_tokens平均=130,846(1,831,844÷14delegation)、Before(a)Consolidation平均(130,578)とほぼ同水準 |

**注記**: BeforeとAfterはサンプル数(18件 vs 2件)・タスク性質(Before=254件の
無作為に近い現存サンプル、After=特定6管理IDに限定)がいずれも異なるため、
重複比率27.8%→37.5%の変化がE-1/D-1/G-1条項の効果不在を示すものではない
(判定語なし、材料提示のみ)。むしろ転記消失率が依然85.7%と高く、次回以降の
同種測定のためには`F-1`(転記アーカイブ運用、本タスクPart Aで実施)の継続が
前提条件になることが今回のより重要な発見である。

## 5. 制約・限界(正直な記載)

- 対象6管理ID中5件でSonnet実読込文字数・重複比率が測定不能(転記0バイト)。
  これは委任文最小化ルール(E-1/D-1/G-1)の効果測定というより、転記保存の
  信頼性問題(このセッションで頻発、`tasks/`ディレクトリ内233件中83件が
  0バイト)によるものであり、E-1/D-1/G-1の効果検証には転記保存の安定化
  (F-1)が先決である。
- 3V Phase1b-04は「同一管理IDでの複数回delegation(初回+修正3回)」という
  Beforeにはなかった構造を持つため、重複比率の計算対象(1回のSonnet実行内
  の重複)を厳密にBeforeと同一粒度(1delegation=1転記)に揃えたが、Before・
  Afterの母集団の質(タスク難易度・要求される修正回数)自体が異なる点は
  比較の限界として残る。
- subagent_tokensはSDK報告値、Sonnet実読込文字数はtool_result文字数の
  独立集計であり、直接の1:1対応はしない(既存Phase 1報告と同じ既知の限界)。
- 品質・ルール遵守欄の「差し戻し回数」「ルール逸脱件数」は、DECISION_LOG.md/
  MODEL_ROUTING_TRIAL_LOG.mdの既存記載に基づく手動確認であり、機械集計では
  ない。

## 付録: 生成物一覧

- 本REPORT: `PM-TOKEN-EFFICIENCY-DELEGATION-TRIAL-AFTER-MEASUREMENT-01_
  REPORT.md`(新規)
- `er011_pm_agent_read_audit_01.py`実行出力(無変更、既存パス):
  `er011_output/pm_agent_read_audit_01/per_call.jsonl`、
  `er011_output/pm_agent_read_audit_01/per_agent_task_summary.json`、
  `er011_output/pm_agent_read_audit_01/summary.md`
- 一時usage抽出スクリプト・中間データ(repo外scratchpad、Git管理外):
  `C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\
  294958fe-da6e-491c-8a02-4f864d8195c8\scratchpad\`配下
  (`after_usage_summary.json`、`after_ids_summary.json`、
  `per_round_dup.py`、`per_round_dup_result.txt`)

# SSOT_APPEND_DRAFT_01: 委任_02で適用するSSOT追記文(下書き、**未適用**)
管理ID: PM-20261016-AUW-CLOSEOUT-DQI-PRODUCTION-01 委任_01 / 2026-10-16
適用ルール: すべて**追記のみ**(既存文言は削除・書換しない。旧Status文はそのまま残し、追記で新Statusを示す)。挿入位置は行番号ではなく`grep`パターンで特定する(並行委任`FAMILY-X-APPROVED-SPEC-…`が同ファイルを編集中で行番号が変動するため)。ユーザー原文=`docs/pm/delegation_log/2026-10-16_PM-20261016-AUW-CLOSEOUT-DQI-PRODUCTION-01_USER.md`(11,076文字、以下`USER`)。逐語引用はUSERからの一字一句の抜粋。
件数: CURRENT_SPEC 2 / DECISION_LOG 1 / OPEN_ITEMS 9行(行内追記) / REGISTER 1ブロック(#80〜#95) / REPORT_LEDGER 1行。

---
## 1. CURRENT_SPEC.md(2か所)

### 1-1. 統一ASR判定仕様節の末尾
- 挿入位置: `grep -n '^## 参照元' CURRENT_SPEC.md`の行の**直前**(= 節`## 統一ASR判定仕様(…`の最終bulletの後、空行を挟んで)。
- 追記全文:
```
- **追記(2026-10-16 ユーザー正式承認 `PRODUCTION_WIRED` Closeout、`PM-20261016-AUW-CLOSEOUT-DQI-PRODUCTION-01`、原文=`docs/pm/delegation_log/2026-10-16_PM-20261016-AUW-CLOSEOUT-DQI-PRODUCTION-01_USER.md` §1-A・§6)**: 本節冒頭の旧Status(「main merge待ち」「`PRODUCTION_WIRED`未宣言」)は歴史的記録として残し、現行Statusは本追記が優先する。**現行Status=`PRODUCTION_WIRED`(ユーザー正式承認)**。原文(逐語): 『**ユーザーが`PRODUCTION_WIRED`を正式承認。**』『Family X・Zの通常Production生成において、追加指示なしにAUWが自動適用される状態を維持。』『初回・retry・fallback・regeneration・Local Rewrite後の適用を維持。』『今回報告されたruntime evidence・test・Git反映をCloseout証跡として紐付ける。』『承認済みAUWの再Trial・再実装・追加改修は行わない。』『Family Yは将来の開発対象。Yの開発時に正式配線する。現時点では実装しない。』『**AUW本体は完了。** 別の改善候補を理由にStatusを後退させない。』(§6)『ユーザー正式承認済みのため、`PRODUCTION_WIRED`としてCloseout。』『既存証跡を参照し、再検証のためだけの有料runは行わない。』Closeout証跡の所在(参照のみ): `er058_output/unified_all_roles_production_wiring_01/CLOSEOUT_PLAN_07.md`§4-e、`RUNTIME_EVIDENCE_06.md`、commit `69817ebde`(Fable独立照合=PRODUCTION_WIRED判定のSSOT記録)。AUWの追加改修候補(OPEN-394・OPEN-395・A7範囲限定[REGISTER #95]・#85等)は記録のみ維持し、判断要求を再発行しない。Family Y(将来)の正式配線は未実装。
```

### 1-2. PM運用: DQIパッケージPと開発対象Family制限(新規節)
- 挿入位置: `grep -n '^## 参照元' CURRENT_SPEC.md`の行の**直前**に新節(1-1の直後)。
- 追記全文:
```
## PM運用: DQI(PM判断品質改善)パッケージPと開発対象Family制限(2026-10-16ユーザー正式採用、`PM-20261016-AUW-CLOSEOUT-DQI-PRODUCTION-01`)

- **DQIパッケージP: `APPROVED_FOR_PRODUCTION`**(ユーザー正式採用、原文=`…_USER.md`§2: 『ユーザーはDQIパッケージPを正式採用した。』『対象はPM自律運営モデル。Family X／Zのコンテンツ生成仕様を変更する指示ではない。』)。内容=P1(受入判定の整合・判定整合行)・P2(ユーザー判断前の4区分仕分け)・P3(ユーザー提示制限・例外K1〜K6)・P4(機械Validator、初期は非ブロッキング)・重大NGの2軸定義(内容品質/成果物品質、『厳密には少し異なるというだけでは重大NGとしない』)。規則の正本=`docs/pm/PM_GOVERNANCE.md`27節。実装=27節+`.claude/agents/sandwich-pm.md`手順4-2+`.claude/agents/sonnet-worker.md`+`docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.md`+`docs/pm/tools/check_decision_quality.py`(+test)。机上評価=`docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/dqi/DQI_DESK_EVAL_01.md`。**現Status=`DQI_P_IMPLEMENTED_DESK_EVALUATED`相当(実装+机上評価、未知ケース未実証)。`PRODUCTION_WIRED`はFable独立受入・commit/push・SSOT更新の確認後であり、本記載時点では未宣言。**
- **開発対象Familyの制限**(原文§1-C): 『現在の開発対象はFamily X・Z、将来Yのみ。』『Family A・B・Cは開発停止とする。』ユーザーの明示依頼がない限り、A/B/Cについて新規開発・コード修正、Trial・検証run、実音声生成・再生成、問題是正、調査を名目とした独立タスクの開始、API費用の発生を禁止。『AUW等の既存共通コードがA／B／Cから参照されていることと、これらのFamilyの開発を再開することは別である。』共通基盤の変更がA/B/Cの挙動へ影響する場合は対象を拡張せず、互換性維持と変更範囲を確認する。
- **Family Zの3件の懸念**(原文§1-B): 日本語TTSへの言語指定誤り/原稿の一致を確認しない音声再利用/記号Gateによるコロン検出。ユーザーはFamily Zでの予防的対応を不要と正式判断。『Family Zで実際に問題が発生するまでは、追加調査・Trial・改修を行わない。』既存のProduction品質Gateは維持。
- **スコープ管理の再発防止記録**(原文§1-C: 『今回Family Cの開発が指示範囲外で進行したことを、スコープ管理上の再発防止事項として記録する。』『ただし、この問題を理由にFamily Cの追加調査・改修を開始してはならない。』): 事実関係のみ。(i)`FAMILY-C-JA-TTS-PRODUCTION-FIX-01`(FCJ)はユーザー指示B(`docs/pm/delegation_log/2026-10-16_AUW-FAMILY-C-DQI-USER-INSTRUCTION.md` B-1〜B-4、日本語Commentの言語経路・reuse_from整合・実音声evidence)に基づき委任_01〜03で実施された(`docs/pm/RESULT_PACKET_FCJ1/2/3.md`、REPORT_LEDGER 2026-10-16 FCJ行)。(ii)FCJ実施中にOPEN-385(承認済み資産の再利用保証)・OPEN-386・OPEN-387(story_001コロン)が起票され、REGISTER #92として判断事項化、Family Zへの3件の懸念も提示された(提示元の記録所在は本委任では未確認)。(iii)ユーザーは上記を「指示範囲外で進行」と評価し、以後A/B/Cで明示依頼のない作業を禁止した(PM_GOVERNANCE 27-7)。原文の評価に反論せず事実のみ記録。この記録を理由にFamily Cの調査・改修は開始しない。
```

---
## 2. DECISION_LOG.md(1エントリ)
- 挿入位置: ファイル**末尾**(`tail`で最終エントリを確認し、その後に空行を挟んで追記)。並行委任のエントリ(`## FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01 委任_01…`以降)の後ろ。`grep -n '^## PM-20261016-AUW-CLOSEOUT-DQI-PRODUCTION-01' DECISION_LOG.md`が0件であることを適用前に確認。
- 追記全文:
```
## PM-20261016-AUW-CLOSEOUT-DQI-PRODUCTION-01 委任_01(2026-10-16): ユーザー最終判断の保存・DQIパッケージP実装・机上評価(JPY0、LLM呼出0)

- ユーザー指示原文: `docs/pm/delegation_log/2026-10-16_PM-20261016-AUW-CLOSEOUT-DQI-PRODUCTION-01_USER.md`(11,076文字)。委任文=同`_01.md`(+`_01_check.json`: check_delegation_prompt=FAIL[理由=『事前指定Grep一覧+追記位置・更新位置の手順』見出し欠落のみ。記録のみ]。固定ブロックE-1/D-1/G-1/F-1は検出)。
- ユーザー判断(2026-10-16、既存REGISTER/決定の重複登録なし): (A)AUW=`PRODUCTION_WIRED`正式承認、再Trial・再実装・追加改修なし、Family Yは将来/(B)Family Z 3件の予防対応不要/(C)開発対象はX・Z・将来Yのみ、A/B/C開発停止/(2)DQIパッケージP=`APPROVED_FOR_PRODUCTION`(REGISTER #88〜#91は判断済み=採用。#80〜#82も統合済みで同扱い)。#85・#93〜#95は記録のみ(§1-A/§7、Fable読み取り)、#92はFamily C開発停止で判断不要(§1-C)。
- 実装(未commit、Fable受入・commit待ち): `docs/pm/PM_GOVERNANCE.md`27節新設+12-13(09-27)/12-13(10-12)へ参照追記+変更履歴/`.claude/agents/sandwich-pm.md`手順4-2へ判定整合行・UDR仕分け・Family制限/`.claude/agents/sonnet-worker.md`(判断候補表記・判定整合行・Family制限)/`docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.md`(2か所)/`docs/pm/tools/check_decision_quality.py`+`check_decision_quality_test_01.py`(17 test PASS)。提案書からの設計差分=下記。
- 提案書(`DQI_PROPOSAL_01.md`§3・§9)からの差分: (1)P2の統合記載先は12-13重複2節の統合ではなく新設27-3を正本とし、12-13の2節には参照のみ追記(番号付け替えが既存参照を壊すため)/(2)P3の「提示」4値と例外K1〜K6はPM_GOVERNANCE 27-4へ集約/(3)P4のValidatorは提案書の『既存check_delegation_prompt.pyへの別関数追加を先に再検討』に対し、責務・既存testへの影響から新規1本とした(INVENTORY§5の結論どおり)。(4)`OPUS_INDEPENDENT_REVIEW_BLOCK.md`への1行追加(P5)は本委任では未実施(27-6に記載のみ。Fable判断)。
- 机上評価: `docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/dqi/DQI_DESK_EVAL_01.md`。評価対象1〜6すべて机上基準を満たす(E5=8/10、498本のRESULT_PACKETでwarn 10本=2.0%)。ただし基準は結果閲覧後に文書化、Validator検出語を誤検出観測に基づき1回調整、正解を知る評価者による机上評価で未知ケースの有効性は未実証。不合格なし、追加Trial・追加改修なし。未知ケース評価は案a(JPY0前向き観察)/案b(有料)を提示のみ。Day 5〜6の保留は維持。
- Status: `DQI_P_IMPLEMENTED_DESK_EVALUATED`。`PRODUCTION_WIRED`はFable独立受入後。AUW Closeout=`PRODUCTION_WIRED`(ユーザー正式承認)はCURRENT_SPECへ追記(本管理ID委任_02適用)。
```

---
## 3. OPEN_ITEMS.md(行内追記、9行。各行**末尾の`|`の直前**に`【2026-10-16追記】…`を挿入。先頭タグ・既存本文は変更しない)
各行は`grep -n '^| OPEN-<番号> |' OPEN_ITEMS.md`で特定(行番号は変動する)。

- **OPEN-385**: `【2026-10-16追記】Family C開発停止(ユーザー正式判断、…_USER.md §1-C)。ユーザーの明示依頼があるまで凍結。closeではない。REGISTER #92は判断不要(作業禁止)。】`
- **OPEN-386**: `【2026-10-16追記】Family C開発停止(§1-C)。ユーザー明示依頼まで凍結。closeではない。】`
- **OPEN-387**: `【2026-10-16追記】Family C開発停止(§1-C)。ユーザー明示依頼まで凍結。closeではない。】`
- **OPEN-388**(AUW A3 length): `【2026-10-16追記】AUWは2026-10-16にユーザーがPRODUCTION_WIRED正式承認(§1-A)。『承認済みAUWの再Trial・再実装・追加改修は行わない。』以後の追加改修なし。是正の実施状況は本行の既記載(委任_11・委任_13)に従う。】`
- **OPEN-389**(NEWS tail fix最小fallback): `【2026-10-16追記】AUWの追加改修は行わない(§1-A)。対象FamilyがA/B/Cに該当する場合はFamily A/B/C開発停止(§1-C)により凍結。対象Familyの確認はFable(本委任では未確認)。拡大はユーザー明示依頼まで行わない。】`
- **OPEN-392**(U1既定): `【2026-10-16追記】AUWはPRODUCTION_WIRED正式承認済み(§1-A)。『別の改善候補を理由にStatusを後退させない。』本行の旧Status(暫定True等)は歴史的記録。現行の既定値は実コード(er078_asr_unified_judge_01.py)とREGISTER #83の更新(委任_11)に従う(本追記では変更しない)。再発行する判断要求なし。】`
- **OPEN-394**: `【2026-10-16追記】記録のみ(§1-A/§7)。原文: 『承認済みAUWの再Trial・再実装・追加改修は行わない。』『ユーザーが明示的に保留した非Blocking事項は、判断要求を再発行せず記録のみ維持する。』REGISTER #93は再発行しない。USER_DECISION_REQUIRED候補のタグは歴史的記録。】`
- **OPEN-395**: `【2026-10-16追記】記録のみ(§1-A/§7)。OPEN-394と同じ原文。REGISTER #94は再発行しない。】`
- **OPEN-396**(未取得evidence): `【2026-10-16追記】ユーザーがPRODUCTION_WIREDを正式承認(§1-A、§6: 『再検証のためだけの有料runは行わない。』)。未取得evidenceの追加取得のための有料runは行わない。前提未充足のタグは歴史的記録。Family Y(将来)の正式配線は未実装。】`
- 変更しない行: OPEN-390(記録のみ・非該当)、OPEN-391(AUW起因でない技術的負債)、OPEN-393(Coffee試聴待ち、並行委任の管轄)。Family Zの3件の懸念に対応するOPEN行は、本委任のGrep(`Family Z`×`2026-10-16`)では**該当行なし**(新規追記しない。Zで実発生した場合に初めて起票)。OPEN-372等の既存AUW/Family C行は本委任では追記しない(必要ならFableが指示)。

---
## 4. docs/pm/USER_DECISION_REGISTER_01.md(1ブロック)
- 挿入位置: ファイル**末尾**(`grep -n '^- 本追記後: #96〜#100はすべて判断済み' docs/pm/USER_DECISION_REGISTER_01.md`の行以降。並行委任が#96〜#100を更新済みの後ろ)。既存の#80〜#95行は変更しない。
- 追記全文:
```
- 2026-10-16 ユーザー指示(`PM-20261016-AUW-CLOSEOUT-DQI-PRODUCTION-01`、原文=`docs/pm/delegation_log/2026-10-16_PM-20261016-AUW-CLOSEOUT-DQI-PRODUCTION-01_USER.md`)による更新(既存行は不変、以下が現行):
- #88=**判断済み=採用**(DQIパッケージP): 原文§2『ユーザーはDQIパッケージPを正式採用した。』『Status：`APPROVED_FOR_PRODUCTION`』。#89=**判断済み=採用**(重大NG 2軸定義): 原文§2『ユーザーはパッケージPを承認しており、この定義もその構成要素として扱う。別途承認を求めない。』。#90=**判断済み=採用**(遡及机上チェック): 原文§3 Phase 2『まず既存のDay 3・4の失敗事例など、利用可能な記録で無課金検証する。』『その結果は、既知の正解を使った机上評価と明示する。』。#91=**判断済み(Fable読み取り)**(問題1の実例確認): 原文§3『まず既存のDay 3・4の失敗事例など、利用可能な記録で無課金検証する。』に従い、本日の実例(AUW #83〜#86、FXWA、FCJ)を机上評価に含めて処理(`DQI_DESK_EVAL_01.md`)。ユーザーからの追加の実例指定なし。#80〜#82(Day3 再盲検の最終扱い・次の一手・v3欠陥提案)は#88〜#91へ統合済みとして同扱い(Fable読み取り、原文§2・§3)。
- #85(U3 AMBIGUOUS同表層)・#93(OPEN-394)・#94(OPEN-395)・#95(A7範囲限定)=**記録のみ(判断要求を再発行しない)**(Fable読み取り。ユーザー原文に#番号の明示なし): 原文§1-A『承認済みAUWの再Trial・再実装・追加改修は行わない。』『**AUW本体は完了。** 別の改善候補を理由にStatusを後退させない。』§7『ユーザーが明示的に保留した非Blocking事項は、判断要求を再発行せず記録のみ維持する。』
- #92(Family C 再利用保証 OPEN-385/387)=**判断不要・作業禁止**(Family C開発停止): 原文§1-C『Family A・B・Cは開発停止とする。』。OPEN-385/386/387は凍結(closeではない)。
- AUW=**`PRODUCTION_WIRED`ユーザー正式承認**(新規UDRではなく記録): 原文§1-A『**ユーザーが`PRODUCTION_WIRED`を正式承認。**』。#83・#84・#86・#87の既存「判断済み」は不変。
- 本追記後: 本管理IDによる新規USER_DECISION_REQUIREDは0件。#80〜#95のUSER_DECISION_REQUIRED残は0件。ブロックする既存UDR(#72等)の現状はFableがREGISTER本体で照合して確定する(本委任ではREGISTER編集禁止のため#72・#81の最終状態を未確認。#81は#88〜#91へ統合として扱う)。
```

---
## 5. docs/pm/REPORT_LEDGER.md(1行)
- 挿入位置: ファイル**末尾**(`grep -n 'FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01' docs/pm/REPORT_LEDGER.md`の最終行の後)。
- 追記全文:
```
- 2026-10-16 | PM-20261016-AUW-CLOSEOUT-DQI-PRODUCTION-01 委任_01(ユーザー指示原文保存[11,076文字]+DQIパッケージP P1〜P4実装[PM_GOVERNANCE 27節/sandwich-pm.md 4-2/sonnet-worker.md/DELEGATION_STANDARD_TEMPLATE.md]+機械Validator `check_decision_quality.py`[17 test PASS、498本のRESULT_PACKETへ実走]+机上評価+SSOT追記下書き。JPY0・LLM呼出0。AUW=PRODUCTION_WIRED[ユーザー正式承認]、Family A/B/C開発停止、Family Z予防対応不要を記録。Status=DQI_P_IMPLEMENTED_DESK_EVALUATED、PRODUCTION_WIREDはFable独立受入後) | 状態=委任_01完了・Fable受入待ち・初回報告未・commitは`git log`でメッセージ冒頭の管理IDを特定 | `docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/dqi/DQI_DESK_EVAL_01.md`
```

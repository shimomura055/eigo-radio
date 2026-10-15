# DAY3_ACCEPTANCE_EVIDENCE_DRAFT_01: 受入条件A〜Eの証拠表(草案、委任_G、2026-10-15)

位置づけ: 草案。受入判定はFable(Gate 7)と最終的にユーザーが行う。本表は「実装済みの所在」と「F(実行検証)で確認する項目」を並べたもの。**未充足と判断した項目は「未充足」欄に明記**(充足と書けないものを充足と書かない)。条件Fは盲検リプレイ(`BLIND_REPLAY_RUNBOOK_01.md`)で実施する(本委任では未実施)。
規則ファイルの基準commit: `71baeb78f`(F1)、`a342f7b52`(F2)、SSOT反映`a1118d9ec`(F3)。行番号は2026-10-15時点のHEAD。ユーザー原文=`DAY3_USER_DECISION_RECONCILIATION_01.md`付録B。

| 条件 | ユーザー原文の項目 | 実装済みの所在(ファイル:行 / commit) | Fで確認する項目 | 未充足・注意 |
|---|---|---|---|---|
| A | 8原則が明文化 | `CLAUDE.md:10`【8原則】(共通Charter、F1 `71baeb78f`) | 新セッションがCharterを読み、行動に反映するか(R-観点のtranscript) | なし |
| A | Fableの5責任が明文化 | `.claude/agents/sandwich-pm.md:31`(5責任)、`PM_GOVERNANCE.md` 1節の役割(F2 `a342f7b52`) | 同上 | なし |
| A | 4 Gateが明文化 | `PM_GOVERNANCE.md:179`(2-0 G1〜G4と既存Gate 1〜7の対応、F2) | 受入でG2/G3/G4の使い分けが出るか | 「新Gateを作らない対応表」であり、4 Gate独立の運用機構は無い(設計通り。ユーザー原文『明文化』は満たす) |
| A | U1〜U5判断と実装が一致 | 照合書`DAY3_USER_DECISION_RECONCILIATION_01.md`、F2/F1の各RESULT_PACKET(`docs/pm/RESULT_PACKET_ROLL3F1.md`/`F2.md`)。U2=11-6(`PM_GOVERNANCE.md:2401`)、U3'=11-7(:2427)、U5=7-9(:857)・15-9(:2999) | Fableが原文と規則文言を再照合(Opus条件Aの所見OF-D3-01〜15は反映済み) | U6(secret scan)は意図的に非実装(OPEN-364で継続管理) |
| A | 承認済みSTOP・安全・Production Gateが弱体化していない | 11-6「維持する境界」(:2401付近)、26節不変、11-1 STOP(1)〜(5)不変(F2のRESULT_PACKET) | SC-C2(境界は即STOP)、SC-D2 | 弱体化なしはF2時点のGrep照合による。独立再確認はF(合成シナリオ)で行う |
| A | 既存規則と新規則に重大な矛盾がない | F2の矛盾確認(2-1/21節の旧検査撤去・11-6他規定との関係) | Fでの規則文面の齟齬を採点者が記録 | 11-4(自律3回・4回目以降毎回Gate)とL3診断後Human Gateは現行維持=U2-Q1/Q2としてユーザー判断待ち(REGISTER #63/#64)。競合を解消済みとは扱わない |
| A | 新しいDangling Referenceがない | `rg -n "^### (11-6|11-7|7-9|15-9)\." docs/pm/PM_GOVERNANCE.md` = 4行(各1行、2026-10-15確認) | 実行検証で参照切れが出ないか | Day2文書内の旧参照は照合書§4-1で「使用しない」と宣言済み(Day2文書は無変更) |
| B | 単純転送でなく実際の証拠を照合し観測値を引用 | `sandwich-pm.md:61`(4-2 独立受入)、`PM_GOVERNANCE.md:262`(受領≠受入)、`受入記録:`固定見出し(`sandwich-pm.md:70`、9-0) | **盲検リプレイ R1・R2**(欠陥ケースn=2+陰性対照) | 未実行。ルールがあることと守られることは別(盲検で確認) |
| B | テストPASSだけでなく正しい受入条件が検証されたか確認 | `sandwich-pm.md:61-69`(既定値Grep/テスト内容Grep/承認済み仕様との文言照合から2件以上) | R3・R5(承認規則Grep)・R4 | 未実行 |
| B | 失敗時の最終成果物・周辺工程への影響を確認 | `sandwich-pm.md:64-67`(高リスクは失敗終了時の最終成果物まで)、観点11注記(`docs/pm/templates/OPUS_INDEPENDENT_REVIEW_BLOCK.md:35`) | **R4**(欠陥②の検出)、UC1 | 未実行。R4は事例から作ったルールの再検出であり汎化は未検証 |
| C | 回数到達だけでUDRにならない | 11-6(`PM_GOVERNANCE.md:2401`)、`sandwich-pm.md` 手順6 | SC-C1、SC-C3、SC-C6 | 未実行 |
| C | 改善見込みを評価しアプローチを変更 | 11-6「改善見込み『低』」「再計画トリガ」「QDC記録」 | SC-C1、SC-C4(L3 vs 条件B) | 未実行 |
| C | 解決可能な技術問題をHumanへ転送しない | 11-6「STOP報告と丸投げの区別」(6点) | **R6**、SC-C1、SC-C3、SC-C5 | 未実行。11-1(3)構造的問題はUDR維持(SC-C5で確認) |
| C | 予算・安全・明示STOP・承認条件は守る | 11-6「維持する境界」、26節、7-9 | SC-C2、SC-E1 | 未実行 |
| D | 未承認機能は既定OFFの5条件で隔離 | 11-7(`PM_GOVERNANCE.md:2427`、5条件逐語) | **R7**(条件1・3・5)、SC-D1、UC1 | 未実行。U3'状態行(ACTIVE、2026-10-15)は`OPEN_ITEMS.md:874`(OPEN-365)にある。ただしREGISTER #65は『潜在迂回路=SUSPENDEDの確認推奨』で、状態行ACTIVEとの関係はユーザー裁定待ち(整合は未確定)。個別機能の「未承認・既定OFF+flag名」行は機能が生じた時点で追加する運用 |
| D | 既定OFFだけでは保証できない迂回経路も検証 | 11-7「状態管理」(mode・設定dict・環境変数・`.env`・起動script・共通到達点・期待値固定test) | **R3**、SC-D1、UC1(別題材) | **未充足(機械的担保)**: flag突合test(OPEN_ITEMSのflag一覧とProductionモジュールのflag読取箇所の突合回帰test)は未作成。OPEN-365(`OPEN_ITEMS.md:874`)で継続管理(Opus論点9 #2)。現状の担保は受入記録の観測値(人手のGrep)のみ。旧DefaultOffIsolation型testはgloss事例の旧仕様でHEADでは前提が変わっている(単独で一般担保とは言えない) |
| D | 違反発覚時の一般例外廃止ルールが明確 | 11-7(3状態ACTIVE/SUSPENDED/REVOKED、発生時の動作7項、`PM_GOVERNANCE.md:2427`以降) | SC-D2(REVOKED)、SC-D3(SUSPENDED中の例外適用) | 未実行。SUSPENDEDの解除裁定=ユーザーのみ(REGISTER #65の確認推奨が未回答) |
| D | VALIDATED/APPROVED_FOR_PRODUCTION/PRODUCTION_WIREDを混同しない | `sandwich-pm.md:73-78`(手順5)、CLAUDE.md Charter、PM_GOVERNANCE 11-7(条件5) | **R9**(宣言0件) | 未実行 |
| E | 量産費70円/記事セットの計算範囲が定義 | 15-9(`PM_GOVERNANCE.md:2999`、分母=15-8の1生成セット等) | SC-E3(予測73円>70円の扱い) | **未充足(実測ベースライン)**: Family別の正式1生成セット原価の測定が未了(15-9「ベースライン」`PM_GOVERNANCE.md:3009`、OPEN-366=`OPEN_ITEMS.md:875`)。範囲の定義は充足、測定値は未 |
| E | 日次1,000円の使用額・残予算をFableが確認できる | 7-9(`PM_GOVERNANCE.md:857`)、`docs/pm/tools/daily_dev_cost_01.py`、`day3/daily_dev_cost_2026-10-15.json`、ACTIVE_TASK `QDC:`行書式(`PM_BRIEF.md:255`) | R8(QDC費用欄)、SC-E1/E2 | 日次集計scriptの継続的な実運用実績は未確認(W9b実施時の実行例のみ) |
| E | Trial設計時に費用見積と改善見込みを評価 | 7-9「Fableの確認義務」(`:867`)、委任文テンプレ(`docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.md`)、25節 | SC-E4(モデル降格の可否) | 未実行 |
| E | 予算超過時の承認Gateと整合 | 7-9「承認要否」(7-7との優先関係)、7-6不変 | SC-E1(960+80>1,000)、SC-E2 | 未実行 |
| F | 盲検リプレイ/陰性対照/独立受入記録/技術問題の不転送/隔離と費用判断 | 本委任の準備物(Repo外`C:\Users\tensh\eigo-radio-replay\`、`BLIND_REPLAY_RUNBOOK_01.md`) | 欠陥ケース2セッション+陰性対照1+SC 14件+UC1、別セッションのopus-consultantが採点 | **未実施**(準備のみ=`DAY3_PHASE3_G_PREP_COMPLETE`)。Day5〜6の実案件評価はF完了後の別Gate |

## 未充足項目の要約(A〜E)
1. **D・機械的担保**: U3'のflag突合testが未作成(OPEN-365)。受入記録の人手Grepのみで迂回経路を検査している。
2. **E・実測ベースライン**: 70円の対象範囲は定義済みだが、Family別の正式1生成セット原価の実測が無い(OPEN-366)。SC-E3は例示値(68円)による机上判断で、実測の代替ではない。
3. **A・競合の未解決**: 11-4とL3診断後Human Gateは現行維持(U2-Q1/Q2、REGISTER #63/#64)。
4. **D・ユーザー確認待ち**: SUSPENDED解釈(REGISTER #65)、70円のTTS判定基準・1,000円/日の運用(REGISTER #66)が未回答。
5. 上記以外のA〜E項目は規則・Agent定義・テンプレとして実装済みだが、**実際に守られるか(B・C・Dの行動)は未実行**であり、Fの盲検で初めて確認できる。

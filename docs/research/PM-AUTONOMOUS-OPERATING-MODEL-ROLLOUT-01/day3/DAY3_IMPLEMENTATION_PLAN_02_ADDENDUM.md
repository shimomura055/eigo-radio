# DAY3_IMPLEMENTATION_PLAN_02_ADDENDUM: Opus条件A所見反映後の実装計画補遺(F2実施結果・F1/F3への申し送り・盲検設計の改訂)
管理ID: PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 / Day3 Phase2 委任_F2 / 2026-10-15 / 性質: 計画補遺。`DAY3_IMPLEMENTATION_PLAN_01.md`は無変更で、競合する記述は本補遺が優先する(Opus所見採否表OF-D3-01〜15は`OPUS_FINDINGS_D3_LEDGER_DRAFT_01.md`)。
実施結果の事実は`docs/pm/RESULT_PACKET_ROLL3F2.md`(一時ファイル)と、F2のcommitの差分を正とする。

## 1. F2で実施した範囲と、F1/F3へ残した単位
| 単位 | 状態 | 備考 |
|---|---|---|
| W4(A1,A2,A3,A6〜A9,B1〜B9,B10注記,B13) | F2で実施 | `PM_GOVERNANCE.md`・`CLAUDE.md`・`PM_BRIEF.md`。A4(sandwich-pm.md手順6)・A5・C群はF1 |
| 11-6 / 11-7 / 7-9 / 15-9 新設 | F2で実施 | 11-7は3状態(ACTIVE/SUSPENDED/REVOKED)。事例固有語なし |
| W5a 1〜6,8(§1役割・2-0・Gate 7・2-1/21節・11-3追加型・11-5・9-0) | F2で実施 | 委任文の列挙どおり。下記の「実施しなかった項目」を参照 |
| W5a-7(26-2(d)のstop_scope_check_01.py差替え) | **未実施** | 委任文の列挙外であり、かつ26-2は逐語不変の対象。実施するなら別途ユーザー判断を含め明示指示が必要 |
| U5書 E3(PM_BRIEF予算Cap追記)・E4/E5/E8(テンプレ)・E6(ヘッダ書式)・E7(9-0第5節) | F1で実施 | F2の編集許可ファイル外、または列挙外。9-0第5節(E7)は`PM_GOVERNANCE.md`だが列挙外のためF1/F3で追記 |
| U5書 E1(7-6末尾への参照追記の2文目) | 一部実施 | B5(語句置換)のみ。`日次1,000円の運用は7-9、量産単価目標は15-9。`の追記は7-6本文を増やさないため見送り |
| Charter挿入(W1)・sonnet-worker.md(W2)・sandwich-pm.md(W3)・PM_BRIEF入口/ヘッダ書式(W6)・テンプレ(W7/X2) | F1 | **F2のcommit後に実施**(Opus条件A (c)。F1はF2のcommit hashを確認してからcommit) |
| W8(UDR台帳)・X1のOPEN_ITEMS状態行・X3・SSOT文案 | F3(KGCPW完了後) | 下記3・4 |
| W9b(日次集計script) | 任意 | Opus: 現状は必須でない。初めて日次300円を超えた日に作成。作る場合は単価未登録を0円にしない |
| OF-D3-02(e)(check_delegation_promptのWARN) | 任意 | F1判断。委任#が2以上でQDC記録ブロックがない場合にWARN(ブロッキングでない) |

## 2. F1への申し送り(要点)
1. **A4**(sandwich-pm.md手順6): U2書A4の変更後文。QDC記録を再委任・再計画の前に作る。
2. **A5**(sandwich-pm.md「上限到達時」→「STOPしてユーザーへ報告する場合」): Opus MINOR(OF-D3-08)に従い、L3診断後の条件を「L3診断後(Sonnetを自動再実行しない。実装が必要なら人間ユーザーの判断を仰ぐ)」と**両方**書く。さらにOF-D3-03の区分文(再委任後も未解決の問題へのOpusへの診断依頼は名称にかかわらずL3、条件Bは評価に限る)を同文でsandwich-pm.mdへ入れる(`PM_GOVERNANCE.md` 11-6と同一文)。
3. **C1〜C5**(sonnet-worker.md/テンプレ): U2書§2-C。見出し文字列(`check_delegation_prompt.py`の検出対象)を変えない。
4. **Charter挿入**: `CHARTER_DRAFT_04.md`(2,081字、4か所のみv3から変更)を`CLAUDE.md`へ逐語挿入し、`difflib`で一致を確認。原則4は是正文(OF-D3-04)。
5. **W2の条件の明文化**: sonnet-worker.md L21-22は`PM_GOVERNANCE.md` 11-7の5条件・3状態と整合させる(`SUSPENDED`時は「新機能への例外適用の凍結」を含める)。
6. **W3**: Fableの5責任、手順4-2(受領≠受入)。`PM_GOVERNANCE.md` Gate 7の本文は「詳細手順は`sandwich-pm.md`手順4-2」と参照しているため、F1で手順4-2を実在させること(F2時点では参照先が未記載=一時的なDangling。F1のcommitで解消)。
7. **W6**: ヘッダ書式に`QDC:`行。U5書E6と共通。
8. **W7/X2**: テンプレの性質欄に費用/日次の1行、前委任のQDC記録・受入記録。`OPUS_INDEPENDENT_REVIEW_BLOCK.md`観点11の注記(`PM_GOVERNANCE.md` 11-3に周知済み)。
9. **順序**: F1はF2のcommit後に実施する(F2のcommitからF1のcommitまでの間は、`CLAUDE.md`/`PM_BRIEF.md`(新・11-6参照)と`sandwich-pm.md`(旧ループ上限)が一時的に食い違う。F1を速やかに実施するか、F1完了後に一括pushにまとめる)。
10. `CLAUDE.md`へのCharter挿入後、`CLAUDE.md`冒頭からCharterが読み込まれることによる起動時のトークン増(約2,081字)をRESULT_PACKETに記録する。

## 3. F3への申し送り
### 3-1. SSOT文案の更新点(DAY3_IMPLEMENTATION_PLAN_01.md §3の文案への差分)
- DECISION_LOG: U3'は「違反=発火または実質的有効配線(REVOKED)」「潜在迂回路=SUSPENDED(失効ではない、ユーザー裁定待ち)」「受入前の検出は違反でない」の3層で記録(OF-D3-05)。**ユーザー原文の解釈を含むため、最終報告でユーザー確認を求めた結果を併記**する。
- DECISION_LOG: A9是正(副作用STOP維持)をU2の実装注記として記録。Opus所見OF-D3-01〜15の採否と目的照合1行は`OPUS_FINDINGS_D3_LEDGER_DRAFT_01.md`を台帳本体へ追記。
- OPEN_ITEMS: 状態行『U3'一般例外: ACTIVE / SUSPENDED / REVOKED(日付・事実・裁定)』(初期値ACTIVE)。各未承認機能のflag名と『未承認・既定OFF』を同行に。
### 3-2. Open Item文案(3件)
1. **U3' flag突合test**: OPEN_ITEMSの状態行にあるflag一覧と、Productionモジュール内のflag読取箇所を突き合わせる回帰testを作る(Fableの注意力に依存しない機械的検出。OF-D2-22の約12件の既定ONフラグの突合と同根)。受入条件D「迂回経路の検証」の機械的担保。
2. **70円ベースライン測定**: Family別(News/Trend/Discovery/Voices/X/Z等)の正式1生成セットの原価測定(DECISION_LOG上99〜840円とばらつき、70円超の可能性)。15-8の標準表で報告し、比較義務は量産単価影響行(+JPY/セット)の評価を主とする。
3. **MODEL_ROUTING_TRIAL_LOG.mdの旧記述**: 「合計最大4回」「ループ上限4回以内」等の履歴記述(運用中文書だが歴史的記録)は許容リストに置き、改訂しない(Opus追加所見)。新規の実運用記述が追加されないことだけを監視する。

## 4. 盲検リプレイ設計の改訂(委任_G。DAY3_IMPLEMENTATION_PLAN_01.md §2-5を以下で上書き。OF-D3-06)
1. **隔離環境**: `git worktree`は使わない。`git archive <commit>`で展開した**履歴なし・remoteなし**のディレクトリ(`.git`なし)を使う。`git log --all`等で後のcommitが見えないこと、`.git`が無いことを事前に確認する。
2. **JPY0・push防止**: 被験環境にorigin未設定、APIキーなし(または無効化)の状態で起動する。`.env`・環境変数の有料APIキーが見えないことを事前に確認する手順を委任文に入れる(確認できなければ起動しない)。
3. **規則ファイルの中立化**: 重ねる規則ファイル(`CLAUDE.md`、`.claude/agents/`、`docs/pm/PM_GOVERNANCE.md`、`docs/pm/PM_BRIEF.md`、`docs/pm/templates/`)を`gloss|GLOSS|KP-GLOSS|KGCPW|a337d8acc|c21cce27a|64d3ec975`でGrepし、事例固有の記述が0であることを確認する。F2で新設した11-6/11-7/7-9/15-9と差分の追加行は0件(RESULT_PACKET_ROLL3F2.md)。既存の`PM_GOVERNANCE.md`には一般機能名としての「日本語gloss」が10行あるが、事例固有語(KP-GLOSS・KGCPW・commit hash)ではない。`ACTIVE_TASK.md`・変更履歴・`PM_BRIEF.md`の事例記述は、被験環境では空の`ACTIVE_TASK.md`に差し替える。
4. **汎化の限界の明記**: 新ルールは当該事例から作られているため、合格は「事例から作ったルールが同じ事例を再検出した」ことを示すだけで、汎化は未検証である。報告にこの旨を明記する。
5. **未使用の合成事例を1件追加**: 表面の形を変えた別事例(例: 別モジュールで環境変数による既定ON、別の機能で劣化出力をassertするtest)を合成し、同じ採点基準で判定する。
6. **合成シナリオの追加(SC-C3〜C6)**: SC-C3=解決見込みなし→6点を揃えたSTOP報告(丸投げでない)/SC-C4=難しい問題でL3と条件Bを区別できるか/SC-C5=11-1(3)の構造的問題を伴う再計画→UDRになるか/SC-C6=回答までの11-4の効果(Opusを使うサイクルが11-4のサイクルとして数えられるか)。さらにSUSPENDED/受入前の検出(11-7)の判定を問うシナリオ(SC-D3)を1件追加する。
7. **n=2は「初期確認」**と明記する(欠陥ケースのセッション数)。採点者の分離と基準の事前固定は維持。

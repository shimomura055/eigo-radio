## 管理ID

`OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_59)。並行タスクなし。

## 性質/到達上限Status/禁止事項

- 性質: Opus独立レビュー#8とFableのPM評価の保存、委任_58の報告保存、SSOTへの記録、`USER_DECISION_REQUIRED`でのSTOP(記録のみ。実装・Trial・測定はしない)。
- 到達上限Status: `USER_DECISION_REQUIRED`(機械判定の解放をLLM確認に委ねるか)。次Trial・限定flow・29件横断は開始しない(限定flowと29件横断は承認済みだが、機械判定の扱いが決まってから1回で行うため待機)。
- 禁止事項: コード・Prompt・テストの編集禁止。LLM/API呼び出し禁止(¥0)。Production正式pathの変更禁止。`CURRENT_SPEC.md`・`PM_GOVERNANCE.md`の編集禁止。下記の追記文を言い換えない。`git add -A`/`stash`/`amend`禁止。既存のM表示差分に触れない。
- 費用上限: ¥0(T-3対象外)。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)の該当判定: 非該当(記録のみ)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSを伴わない。)

T-0の補足: 保存先 `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-SELF-RECOVERY-TRIAL-01_59.md`。委任文は全文そのまま保存(要旨化不可)。

## ユーザー指示(原文、2026-10-04。全文は`DECISION_LOG.md`の委任_58エントリに逐語あり)

- 「機械判定も、今回正式採用した「重大 / 軽微 / 問題なし」の基準に合わせて見直してください。…ただし、主体取り違え・数値改変・否定反転等、本当に重大なケースまで一括して緩めないこと。」
- 「この変更はSafety系の判定処理に触れるため、既存のOpusレビュー条件に該当するか判定し、該当する場合は必ずレビューを入れてください。」
- 「本当に新しい価値判断が残る場合のみ `USER_DECISION_REQUIRED` としてユーザーへ戻してください。」

## 作業1: 保存

1-1. Opusレビュー#8: `C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\f9ae115b-0305-437d-ac2d-b452b22a5e2a\subagents\agent-a08354b774dfa39c7.jsonl`から依頼文とSubagentHandbackの報告文を抽出し、`docs/pm/opus_l2_review_open233_self_recovery_08.md`に`_07.md`と同じ構成で保存。(4)に下記PM評価をそのまま貼る。
1-2. 委任_58の報告: `agent-a6d5685b1530a2221.jsonl` → `docs/pm/delegation_log/2026-10-04_OPEN-233-SELF-RECOVERY-TRIAL-01_58_result.md`。
1-3. 委任_57の報告: `agent-a32da2286eb7c3907.jsonl` → `..._57_result.md`(未保存なら)。

**Fable PM評価(2026-10-04、Opus独立レビュー#8)**(そのまま貼る)
1. 照合(11-3節8項目): 委任_58の設計doc・Opus#8・ユーザー指示(2026-10-04 §1B・§2・§3)・正式採用の線引き・「本当に重大なケースを緩めない」・QCD・予算を照合した。
2. 採用(Fable判断で確定): (a)F1の「整合の証拠による自動解放(CLEARED)」は廃止する。Opusがコードで示したとおり、比較の裏取りは事実文に両方向の語があるとどの方向でも解放され、ユーザーが禁じる「撤回後に原油価格が下落した」も解放されうる。数値・時期・否定の自動解放は付け替え・反義語の反転を見逃す。(b)F4は撤回する。Stage 2は現行でもフラグを見ておらず(calibration_01.py 627〜638行)、「フラグを見せない独立再判定」は同じpromptの引き直しにすぎない。(c)決定論で不一致を確認できたもの(CONFIRMED)はBLOCKING確定を維持する(維持方向にしか働かず安全)。(d)V7の文言「数値・主体・否定・比較・時期の差は…明確にBLOCKING」は、既存の基底rubric R3(e)に揃えて「Ledgerと矛盾する重大な変更(数値の改変、主体の取り違え、否定の反転、方向の反転、時期の取り違え)は…明確にBLOCKING」へ直す(新基準の作成ではなく既存への整合。再較正必須)。(e)動機: 「帰属」と「創作」は別事象。委任_58の案文(2)(V7(1)(イ)へ「仕組み・意図」を追加)は採らない(B4-aは基底R3(b)(c)でBLOCKINGが保たれており不要。限定なしの「意図」は既存より厳しくなりうる)。案文(1)はProduction配線時に、案文(3)は文書のみ反映可。B1-cはユーザーの2026-09-30の判断と基底R3のQUALITY行で整理済みとし、「notes禁止=BLOCKING」と自然な推論の優先順位はProduction配線時の確認項目として記録する(ユーザー判断は不要)。(f)限定flowの合格基準から「floor単独BLOCKING 0〜1件/run」を外し監視値にする。解放は全件ログ+人がラベル付け、重大ラベルのclaimが1件でも解放されたらSTOP。(g)Production配線時の必須対策(解放claimを2-of-2降格の対象から外す/`dev`のフラグを書き換えない/確認callの失敗はBLOCKING固定/cycleごとに再評価)とruntime evidence項目を`OPEN-233-A1-PROD`に追加する。
3. ユーザーへ戻す(Opus指摘に同意): 「Checkerのフラグが立ったclaimを、LLMの確認で解放するか」。機械判定の決定論的な保証を、確率的な保証(確認callが見逃す可能性)に置き換える新しいリスク許容の判断であり、ユーザーのSTOP条件「Safety原則の変更が必要」に当たる。決定論だけでは、役職の一般化(K13・K14)と主体の取り違え(A4-0)を字面で区別できず、比較の目印(K19)も安全に解放できない。したがって「機械判定を正式基準に一致させる」には、(i)LLM確認による解放を導入する(F5)か、(ii)現状維持で一部の軽微な文が機械判定で重大のまま残ることを受容するか、のどちらかになる。
4. Fableの推奨: F5を**比較(`changed_comparison`)と時期(`changed_time`)に限って**導入し、主体・数値・否定は決定論のまま維持する。理由: ユーザーが「本当に重大」と名指しした主体取り違え・数値改変・否定反転を確率的な判定に委ねない。K19型(比較)はこれで解放され、K16型(時期)は確認callで止める(2回とも非BLOCKINGのときだけ解放、失敗はBLOCKING固定)。K13・K14型(主体の一般化)は過剰品質として受容する(是正後の実行で機械判定単独は14件中1件)。導入前に、Opus指摘の単体測定(重大ケースK16・A4-0・K18・A2A3-0と敵対的合成ケース[「After the plan was withdrawn, oil prices fell.」・20%の付け替え・7/13と7/14の取り違え]、過剰ケースK13・K14・K19・B2「vanished overnight」・B4「Names…」をn≥10、¥10〜30)で見逃し0・解放の妥当性を確認してから有効化する。
5. 進行判断: 上記3はSTOP条件に該当するため、`USER_DECISION_REQUIRED`としてSTOPする。限定flow確認と29件横断(承認済み)は、機械判定の扱いが決まってから1回で行う(2回に分けて費用を重ねない)。
6. Production採用の可否は判断していない。

## 作業2: SSOT更新

2-1. `DECISION_LOG.md`末尾に「OPEN-233-SELF-RECOVERY-TRIAL-01(2026-10-04、委任_58〜59、Opus独立レビュー#8後のFable判断。`USER_DECISION_REQUIRED`で停止)」: 上記PM評価の2〜5を本文として記載(逐語)。あわせて、委任_58の調査結果の要点(8種類の原因内訳: 全件が裏取りなしのフラグ依存、6種類は是正済みの波及、2種類+K19は再発しうる型、機械判定だけが重大を止めた記録2件、是正後は14件中1件)。
2-2. `OPEN_ITEMS.md` OPEN-233行Status: 「`USER_DECISION_REQUIRED`(2026-10-04、委任_59): 機械判定の正式基準への整合は、決定論だけでは役職の一般化と主体取り違え・比較の目印を安全に区別できず、LLM確認による解放(確率的保証)の導入可否がユーザー判断。Fable推奨=比較・時期に限定して導入、主体・数値・否定は決定論維持。CLEARED(自動解放)廃止・F4撤回・V7文言の基底R3(e)への整合・動機は整理で解消(文書のみ)はFable判断で確定。限定flow確認・29件横断(承認済み)は判断後に1回で実施。次Trial(5記事×2レベル)は開始禁止。P-strict-closed=`APPROVED_FOR_PRODUCTION`(未配線)。`PRODUCTION_WIRED`ではない。」(旧Statusは「旧Status参考(委任_58)」として残す)。次Actionセルに「判断後: 委任_60=V7文言整合+(採用時)F5実装+単体測定(¥10〜30)+再較正(¥8〜10)→委任_61=限定flow(¥12〜30)→29件横断(¥35〜70)→委任_62=Closeout確認」を追記。`OPEN-233-A1-PROD`行にPM評価2(g)の必須対策とruntime evidence項目を追記。
2-3. `docs/pm/REPORT_LEDGER.md` OPEN-233行: 備考追記、Opus発火列に「L2(条件A、#8、2026-10-04)」併記。
2-4. `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md` §41: 委任_58の要点、Opus#8の要点、PM評価、判断事項。
2-5. `docs/pm/design_open233_floor_alignment_01.md`末尾に「6. Opusレビュー#8後の採否(Fable判断)」を追記(PM評価2〜4)。Opusが指摘した事実誤認4点(F4の前提、非列挙floor単独18→現行関係14件、UNDETERMINED旗付き5→8件、K19のCLEAREDは整合の証拠ではない)を「正誤表」として同節に記載(本文は書き換えない)。
2-6. `docs/pm/ACTIVE_TASK.md` Status=`USER_DECISION_REQUIRED`、判断事項(判断D: LLM確認による解放の導入可否と範囲[(1)比較・時期に限定=推奨/(2)主体も含む/(3)導入せず現状維持])を記載(addしない)。

## 事前指定Read一覧

- `docs/pm/opus_l2_review_open233_self_recovery_07.md`: Grep `^#` で構成のみ。
- `OPEN_ITEMS.md`: Grep `OPEN-233` → 該当行。`DECISION_LOG.md`・`REPORT_LEDGER.md`・REPORT・設計doc: 追記位置だけ。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 上記のとおり。

## 実行コマンド全文

C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-SELF-RECOVERY-TRIAL-01_59.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-SELF-RECOVERY-TRIAL-01_59.md_check.json

テスト・回帰は不要(コード変更なし)。

## SSOT追記文

作業2のとおり。

## Git(明示add対象・コミットメッセージ・trailer)

- SSOT編集権: あり(`DECISION_LOG.md`末尾、`OPEN_ITEMS.md`の2行、`REPORT_LEDGER.md`の1行)。
- 明示add対象: `DECISION_LOG.md`、`OPEN_ITEMS.md`、`docs/pm/REPORT_LEDGER.md`、`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`、`docs/pm/design_open233_floor_alignment_01.md`、`docs/pm/opus_l2_review_open233_self_recovery_08.md`、`docs/pm/delegation_log/2026-10-04_OPEN-233-SELF-RECOVERY-TRIAL-01_57_result.md`(作成した場合)、`_58_result.md`、`_59.md`、`_59.md_check.json`。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。
- コミットメッセージ: `OPEN-233-SELF-RECOVERY-TRIAL-01: Opus独立レビュー#8(機械判定整合)を保存、自動解放(CLEARED)廃止・F4撤回・V7文言整合・動機整理をFable判断で確定、LLM確認による解放の導入可否をUSER_DECISION_REQUIREDとして記録(委任_59)`。`git push origin main`まで。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`と最終メッセージに: (1)保存・更新したファイル、(2)T-0・commit・push・raw URL、(3)指示どおりにできなかった点。

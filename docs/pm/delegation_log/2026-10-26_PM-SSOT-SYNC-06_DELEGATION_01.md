## 管理ID

PM-SSOT-SYNC-06(ユーザー決定2026-10-26「Family YはPRODUCTION_WIREDと判定しない」の反映=直前のPM-SSOT-SYNC-05で記録したY Std/Adv行の是正、OPEN-527/532更新、Y/Z Voice候補差分の承認記録[事前記録]、FZ ctx LR未配線の記録確認。API 0・JPY0)。並行タスク衝突確認: 並行Agent 5件(TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01 委任_01X/01Y/01Z[read-only]、KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01[`er124_*`]、FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01 委任_01[`er121_*`・`docs/research/FAMILY-Y-VOICE-TABLE-…/`、SSOT編集権なし])。**SSOT編集権は本Agentのみ**(`CURRENT_SPEC.md`/`OPEN_ITEMS.md`/`DECISION_LOG.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/USER_DECISION_REGISTER_01.md`/`docs/pm/ACTIVE_TASK.md`)。これ以外は編集しない。git index.lock競合時は10秒待って再実行(最大3回)。

## 性質/到達上限Status/禁止事項

- 性質: SSOT転記(ユーザー決定の反映)。到達上限Status: 転記完了。
- 禁止: Production/コード変更、API支出、`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。
- worktree状態: 直前のSYNC-05で各SSOTはHEADと一致するよう書き戻し済み(RESULT_PACKET_SSOT5 (1))。本委任でも編集前に`git diff HEAD --stat -- <path>`で差分が無いことを確認し、差分があればHEAD blob+自hunk方式(scratchpad経由)で扱う。
- 費用/日次: JPY0。
- Opus独立技術レビューGate(11-3): 非該当(転記のみ)。
- 時間見込み: 約30分。並列化: なし(SSOT直列ルール8-Y)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし)
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。

T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_PM-SSOT-SYNC-06_DELEGATION_01.md` をN=655から順に試し、先頭が「## 管理ID」+「PM-SSOT-SYNC-06」で始まるものを採用(同時刻にFAMILY-Y-VOICE-TABLE委任も送られているため先頭一致を必ず確認。`--index -1`不可)。

## ユーザー指示(原文・該当部分の逐語。全文は並行AgentがFAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01_USER.mdへ保存する。本委任では以下の逐語をSSOTへの引用に使う)

§1(抜粋): 「**Family YのVoice候補変更を正式採用（APPROVED_FOR_PRODUCTION）。**」「AlgiebaはFamily Yの候補から除外。」「Family Y Voice 1はPuckを採用。」「男性5名・女性5名の候補構成を正式仕様に反映する。」「既存の完成音声を無断で差し替えない。今後の制作に適用する。」「Trialで判明したポーズ・再生成率の問題も記録する。」「**Family Zは変更しない。**」「ユーザーはFamily ZのAlgiebaの声を気に入っており、**Family YとFamily ZのVoice候補差分を明示的に許容した。**」「この差分は承認済みFamily固有仕様としてCURRENT_SPEC／DECISION_LOG等に記録すること。」「共通仕様の統一を理由に、Family ZのAlgiebaを削除したりPuckへ変更したりしない。」
Y表: 男性1 Puck/2 Schedar/3 Fenrir/4 Orus/5 Iapetus、女性1 Zephyr/2 Kore/3 Leda/4 Sulafat/5 Erinome。Z表(不変): 男性1 Algieba/2 Schedar/3 Fenrir/4 Orus/5 Puck、女性1 Zephyr/2 Kore/3 Leda/4 Sulafat/5 Erinome。

§2(抜粋): 「承認済み仕様は以下。- Family X／Y：段落境界で分割、0.2秒ポーズ。- Family Z：おおむね70語を目安に段落境界で分割、0.2秒ポーズ。- Standard／Advancedの両方に適用。- Standardの既存約6%減速を維持。」「**Family X/Z：** 正式runtimeで発火確認済み。残るSSOT/Git反映と証拠の最終照合を完了させる。」「**Family Y：** 正式承認・配線済みだが、現行本文が1段落固定のため実記事ではChunkが発火しない。したがって、**Family YはPRODUCTION_WIREDと判定しない。**現状をOPEN-527等に正確に記録する。本文の段落構成や分割方式は未承認のまま変更しない。」

§3(抜粋): 「文脈・感情付きTTS本体および3回目Fallbackまでは正式runtime検証済み。ただし、Local Rewriteは未配線であり、現行ではHuman Review／STOPに進む。SSOT/Gitの最終反映を完了し、Local Rewriteについては次項の調査結果と照合すること。Local Rewriteの新仕様を独断で追加しない。」

§6(抜粋): 「ユーザー承認済みでも、実装・runtime・記録のいずれかが未確認ならPRODUCTION_WIREDとしない。」「特に、Family Y/ZのVoice候補差分は今回正式に許容されたものであり、今後これを未承認の仕様不一致として扱わないこと。」

## Fable判定(転記する内容)

### A. Chunk Y行の是正(SYNC-05 commit 764901e3aで「PRODUCTION_WIRED(配線済み・構造的不発火)」と記録した箇所を是正)
- Y Std / Y Adv の新Status: **APPROVED_FOR_PRODUCTION・配線済み(WIRED_NOT_FIRING)・PRODUCTION_WIREDとは判定しない**(ユーザー決定2026-10-26 §2逐語引用)。根拠: 実記事は1段落固定のため正式経路で発火せず、正式runtimeの発火証拠が無い(dev入力での発火証拠は「配線の動作確認」として残す)。Y本文の段落構成・分割方式は未承認のまま変更しない(OPEN-527で判断待ち)。
- X Std/Adv・Z Std/Adv=PRODUCTION_WIRED(変更なし)。案件全体のStatus=「X/Z PRODUCTION_WIRED、Y WIRED_NOT_FIRING(PRODUCTION_WIRED未判定)」。
- SYNC-05の記録は誤判定ではなく、ユーザーの判定基準(発火証拠のない配線はPRODUCTION_WIREDとしない)が後から明示されたことによる是正、と注記(履歴として旧記載を残す)。

### B. Y/Z Voice候補差分の承認記録(事前記録。配線のStatusは並行委任の結果待ち)
- OPEN-531: Status=**APPROVED_FOR_PRODUCTION(2026-10-26、Voice 1=Puck、Y候補表 男性5/女性5)_WIRING_IN_PROGRESS**(FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01 委任_01)。PRODUCTION_WIREDは配線・evidence後にFable判定。
- CURRENT_SPEC Family Y Voice節(Grep `Family Y`+`Voice 1|Algieba|Zephyr`で特定): 「承認済みVoice候補表(2026-10-26 APPROVED_FOR_PRODUCTION)」としてY表を追記、Status=「APPROVED・配線中(Production未反映、既存完成音声は差し替えない・今後の制作に適用)」。同節に「**Family Zとの候補差分(Z男性1=Algieba・Z男性5=Puck、Y男性1=Puck・Algieba除外)はユーザーが2026-10-26に明示的に許容した承認済みFamily固有仕様。共通仕様統一を理由に変更しない。今後これを未承認の仕様不一致として扱わない**」を明記。Z Voice表(CURRENT_SPEC.md:1563付近)には「2026-10-26ユーザー再確認: 変更なし(Y表との差分は承認済み)」の1行のみ追記(表本体は変更しない)。
- DECISION_LOG 1件: ユーザー決定(Y表採用・Z不変・差分許容)+Chunk Y判定是正+FZ LR未配線の扱い(§3)をまとめて記録。

### C. FZ ctx(OPEN-528)の記録確認
- OPEN-528行に「2026-10-26ユーザー再確認: ctx本体と3回目Fallbackまで正式runtime検証済み。Local Rewriteは未配線で現行はHR/STOP。LR新仕様は独断で追加しない。TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01の調査結果と照合後にユーザー判断」を追記(既存Deferred項目「Zセリフ用LR新設要否」と統合し重複させない)。

### D. OPEN-527
- 「2026-10-26ユーザー決定: YのChunkはPRODUCTION_WIREDと判定しない(配線済み・実記事不発火)。本文の段落構成・分割方式は未承認のまま変更しない」を追記。ユーザー判断事項(文境界分割/本文契約変更/現状維持)は継続。

## KPI provenance欄

該当なし。

## Opus台帳更新

該当なし。

## 事前指定Read一覧

- `docs/pm/RESULT_PACKET_SSOT5.md` 全文(前委任の更新箇所)
- `docs/pm/ACTIVE_TASK.md` 全文
- `CURRENT_SPEC.md`: Grep `Std拡張|PRODUCTION_WIRED\(配線済み|構造的に不発火|Y Std|Y Adv` → 該当行±5(是正対象)、Grep `Family Y` + `Voice 1|Algieba|Zephyr|Schedar` → Y Voice節の位置、`CURRENT_SPEC.md:1555-1575`(Z Voice表)

## 事前指定Grep一覧+追記位置・更新位置の手順

- `CURRENT_SPEC.md` Chunk節「Std拡張」小節のY Std/Y Adv行 → 判定語を上記Aへ置換(旧記載は「(旧: PRODUCTION_WIRED(配線済み・構造的不発火)=2026-10-26ユーザー決定により是正)」として残す)。Status行の6行表要約も「X/Z PRODUCTION_WIRED、Y WIRED_NOT_FIRING」へ。Family Y節末尾の1行も同様に是正。
- `OPEN_ITEMS.md`: Grep `OPEN-532` → Status文言を「PRODUCTION_WIRED(X/Z)・Y=WIRED_NOT_FIRING(PRODUCTION_WIRED未判定、ユーザー決定2026-10-26)」へ。Grep `OPEN-527` → D追記。Grep `OPEN-531` → B更新。Grep `OPEN-528` → C追記。
- `DECISION_LOG.md`: 本日末尾に1件追記(B)。
- `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `OPEN-531` → 「決定済み(Puck採用・Y表・Z不変・差分許容)」、Grep `OPEN-532` → 「Y=PRODUCTION_WIRED未判定(ユーザー決定)」、Grep `OPEN-527` → 継続(Chunk Y不発火の注記)。
- `docs/pm/REPORT_LEDGER.md`: ユーザー決定受領(2026-10-26 Voice表/Chunk Y判定/FZ LR)・FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01 委任_01開始・本件を記録。
- `docs/pm/ACTIVE_TASK.md`: 上書き(並行=TTS-RETRY…01X/Y/Z(JPY0)、KP Trial(Cap80)、FAMILY-Y-VOICE-TABLE(Cap60)、UDR-blocking=OPEN-526・527・529(区分2)[OPEN-531は決定済み→配線中]、STOP条件=猿の手run_fzcw_e1_01残置、QDC=当日約510円+KP≤80+Y Voice≤60/1,000)。

## 実行コマンド全文

- `git diff HEAD --stat -- CURRENT_SPEC.md OPEN_ITEMS.md DECISION_LOG.md docs/pm/REPORT_LEDGER.md docs/pm/USER_DECISION_REGISTER_01.md`(編集前。空であること)
- `git diff --cached --stat`(自分の追記のみ)
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

上記Fable判定A〜Dの文言をそのまま使う(ユーザー逐語引用を含める)。

## Git(明示add対象・コミットメッセージ・trailer)

- add対象: `CURRENT_SPEC.md`、`OPEN_ITEMS.md`、`DECISION_LOG.md`、`docs/pm/USER_DECISION_REGISTER_01.md`、`docs/pm/REPORT_LEDGER.md`、`docs/pm/delegation_log/2026-10-26_PM-SSOT-SYNC-06_DELEGATION_01.md`(+`_check.json`)。ACTIVE_TASK/RESULT_PACKETはaddしない。
- commit message: `PM-SSOT-SYNC-06: ユーザー決定反映(Chunk Y=PRODUCTION_WIRED未判定[WIRED_NOT_FIRING]へ是正、Y Voice候補表APPROVED_FOR_PRODUCTION・Z不変・Y/Z差分は承認済みFamily固有仕様、FZ LR未配線の扱い、OPEN-527/528/531/532、API 0)`
- trailer: `Delegation: PM-SSOT-SYNC-06/01`
- push: `git push origin HEAD:main`(non-ffなら`git fetch origin`→`git merge --no-edit origin/main`→push。競合はSTOPし報告)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_SSOT6.md`: (0)T-0結果、(1)編集前のworktree状態、(2)更新行(ファイル:行、CURRENT_SPECは是正前後を引用)、(3)`git diff --cached --stat`、(4)commit hash・push結果・raw URL(CURRENT_SPEC.md/OPEN_ITEMS.md/DECISION_LOG.md)、(5)RESULT_PACKET必須4行+「判定整合: 重大NG=<なし|あり>」1行、(6)一覧外Read。末尾に10行以内の要約。
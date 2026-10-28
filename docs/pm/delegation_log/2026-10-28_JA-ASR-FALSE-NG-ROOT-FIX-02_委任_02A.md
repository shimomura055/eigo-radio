管理ID JA-ASR-FALSE-NG-ROOT-FIX-02 委任_02A「課題A是正のSSOT反映(Fable受入済み)+横展開点検A8」。前提=`docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/PM_AUDIT_01.md`(§11 A1〜A8・§12 反映文案)、`docs/pm/RESULT_PACKET_JAFIX2A.md`、ユーザー原文`docs/pm/delegation_log/2026-10-28_JA-ASR-FALSE-NG-ROOT-FIX-02_USER.md` §3。Fable判断: 新Gate増設なし。A1〜A7は既存規則(4-2/項目32/27-3/C-18)の適用明確化として反映、A8は本委任で実施。並行worker(委任_02B)が`docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/`配下の評価ファイルを編集中=そこは触らない(PM_AUDIT_*のみ可)。

**ファイル範囲**: `OPEN_ITEMS.md`(OPEN-515/333/517の該当行のみ)、`DECISION_LOG.md`(末尾1件追加)、`docs/pm/PM_GOVERNANCE.md`(項目32末尾・:2586直後・27-3の各1〜2文のみ)、`docs/pm/ACTIVE_TASK.md`(管理ID(F)行に受入条件表を追加)、`docs/pm/USER_DECISION_REGISTER_01.md`(新規UDRは**起票しない**。#201〜203の備考に本管理IDで再評価中の1文のみ)、`docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/PM_AUDIT_02_CROSSCHECK.md`、`docs/pm/delegation_log/2026-10-28_JA-ASR-FALSE-NG-ROOT-FIX-02_委任_02A.md`(本文逐語)。Production code・他dir編集禁止。API 0。Family A/B/Cの開発は不可(点検で該当行が出ても記録のみ)。
開始時に `.venv\Scripts\python.exe tools/stop_scope_check_01.py --managed-id JA-ASR-FALSE-NG-ROOT-FIX-02 --run-dir docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02 --out docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/stop_check_02A.json`(rc=3で停止)。

### 1. SSOT反映(PM_AUDIT_01 §12の文案を基に、最小追記。既存文は削除しない)
- OPEN-515: 見出しStatusを目的単位へ更新=「INVESTIGATING→**目的達成度: 未達(正常な月題の救済=0/6 clean PASS)**。個別対策(F1+F2 WIRED、E3/E4 APPLIED)は誤PASS防止で、誤NG救済は未解決。JA-ASR-FALSE-NG-ROOT-FIX-02で再評価中(Phase 1: v2+β併用で決定対PASS_W 4/6、clean 0/6)」+PM管理不備の主因M1〜M3(1行)+証拠=PM_AUDIT_01.md。OPEN-333/517: 「誤NG救済の機能なし。案件目的の達成度はOPEN-515参照」の1文。
- DECISION_LOG末尾1件: 課題Aの結論(主因M1受入単位のずれ/M2保留が管理終点化/M3完了語彙の混用)、再発防止=新Gateなし・A1〜A7の運用明確化、A8実施、Fable判断・日付。
- PM_GOVERNANCE: 項目32末尾に「案件の受入条件表(ユーザー原文から逐語抜粋)を最初の受入時にACTIVE_TASKへ置き、各受入で達成/部分/未達を更新する。未達行が残る間は『完了』『一区切り』『進行中なし』を使わない(A1/A2)」。:2586直後に「保留を置く場合は、保留理由→再提示の計測指標→期限を1行で書き、指標が当該原因を測ることをfile:lineで確認する(A4)。報告で約束した後続評価はOPEN/ACTIVE_TASKにID付きで置く(A6)」。27-3に「DECISION_LOGで判断候補Dと書いた項目は受入時にREGISTER登録を確認し、未登録なら受入前に登録する(A3)」。いずれも新Gateではない旨を括弧で明記。
- ACTIVE_TASK (F)行: ユーザー原文§6の合格条件1〜6+課題A を「条件/達成・部分・未達/担当手段」3列表(現時点: 課題A=達成(反映済み)、B1=未達(4/6 PASS_W, clean 0/6)、B2=部分(増分3型)、B3=達成、B4=部分、B5=部分、B6=部分)。
- UDR #201〜203 備考: 「JA-ASR-FALSE-NG-ROOT-FIX-02 Phase 1/2で再評価中。回答はPhase 2結果と併せて提示」。

### 2. A8 横展開点検(read-only)→`PM_AUDIT_02_CROSSCHECK.md`
`OPEN_ITEMS.md`で「VALIDATED(限定)」「保留」「推奨現状維持」「実測後」「ユーザー判断待ち」「判断候補(D」を含む行を抽出(POST_USER_VALIDATION優先、PRE_USER_VALIDATIONは一覧のみ)、各行について UDR register(`docs/pm/USER_DECISION_REGISTER_01.md`)に対応番号があるか/Deferred・再提示トリガー・期限の有無/目的達成度の記載有無 を表にする。未登録・トリガー不適合の行を列挙(判断・登録はFable。あなたは登録しない)。Family A/B/C該当行は「対象外(27-7)」とだけ記す。

### 3. Git
`git diff --cached --name-only`空を確認→自分のファイルのみ明示`git add … && git commit -m "JA-ASR-FALSE-NG-ROOT-FIX-02 委任_02A: 課題A再発防止のSSOT反映(運用明確化・新Gateなし)+横展開点検(API 0)"`を1コマンド、`git add -A`禁止、並行workerのファイルをaddしない。`git push origin HEAD:main`(FFのみ、拒否時fetch後再試行、force禁止)。hand-back: 反映箇所(file:line)、A8の未登録件数と上位の要注意行、commit sha、判断候補(A/B/C/D)。

## 管理ID

PM-SSOT-SYNC-20(SSOT同期: ユーザー正式決定【全面修正版】の記録、KP-CONFIRMED-CONTENT-PROTECTION-01 委任_02B、LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_04/_05、FAMILY-Y-STYLE-PROFILE-FIX-01 委任_06、GRAMMAR-PREGEN-ALL-LEVELS-01 委任_01(新規OPEN-559起票)、PM_GOVERNANCE違反記録、誤追跡ファイルの追跡解除。API 0・JPY0)。**本委任のみがSSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`)・`docs/pm/ACTIVE_TASK.md`・`docs/pm/PM_GOVERNANCE.md`・`docs/pm/DELEGATION_STANDARD_TEMPLATE.md`の編集権を持つ**。並行Agent: KP-CONFIRMED-CONTENT-PROTECTION-01 委任_03(evidence、コード最小是正のみ)、Opus(read-only)。所有=上記SSOT 6ファイル、`docs/research/PM-SSOT-SYNC-20/REPORT_01.md`、`docs/pm/delegation_log/2026-10-27_PM-SSOT-SYNC-20_DELEGATION_01.md`(+check.json)、`docs/pm/RESULT_PACKET_SSOT20.md`。pathspec付きcommit。

## 性質/禁止

- 性質: SSOT同期(Fable判定の転記・整合)。到達上限=同期完了。
- 禁止: SSOT全文読込、判定変更、Status格上げ、禁止Git操作(`git rm --cached <path>`は許可=追跡解除のみ、`-f`不可)、worktree stale上書き(編集直前に`git log origin/main -1 -- <path>`)。
- 時間見込み: 約1h。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文保存+check、結果1行。T-2/T-3: なし。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-27_PM-SSOT-SYNC-20_DELEGATION_01.md` をN=716から順に試し、先頭「## 管理ID」+「PM-SSOT-SYNC-20」のものを採用。

## Fable判定(転記内容。一次資料=`docs/pm/RESULT_PACKET_{KCP2B,FORM4,FORM5,YSP6,GPG1}.md`の(7)/(8)SSOT文案。齟齬はFable判定優先)

### A. ユーザー正式決定【全面修正版】(2026-10-27、原文=`docs/pm/delegation_log/2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_USER.md`)
- DECISION_LOG新規エントリ: 4項目(①フォームv3 ②文法解説の事前生成 ③全候補AI選定理由 ④確定内容保護)を全6経路(X/Y/Z×Std/Adv)にAPPROVED_FOR_PRODUCTION。到達目標PRODUCTION_WIRED(全6経路)。「Part 2文法解説はAdvancedのみ」等の旧記述は本決定で置換(旧仕様として履歴化)。7+5のPRODUCTION_WIRED判定とフォーム/文法解説の判定は区別。
- CURRENT_SPEC: Part 2文法節(Grep `Part 2|文法解説|Advanced.*のみ|b1b.*のみ`、:2096-2099/:2080/:3104付近)に「2026-10-27ユーザー決定によりStd/Adv両方・事前生成へ移行(実装中=GRAMMAR-PREGEN-ALL-LEVELS-01、OPEN-559)。Advanced限定は旧仕様」の注記を付け、旧記述を現行仕様として参照されない形に(履歴化)。確定内容保護の正式節は委任_03 evidence後(SYNC-21)。
- UDR-FORM-1(文法の型不一致・事前生成の採否)=本決定で解消(OPEN_ITEMS該当箇所・`USER_DECISION_REGISTER_01.md:489`付近を更新)。

### B. GRAMMAR-PREGEN-ALL-LEVELS-01 → 新規OPEN-559(11-8=修正へ進む、Status=DESIGN_READY→Opus条件Aレビュー中)
- 設計5a2c3dba1。重要所見: 「Part 2=Advancedのみ」はユーザー原文(2026-10-25 `PART2-GRAMMAR-PRODUCTION-WIRING-01_USER.md:90`「Standard/Advancedなど既存Productionで対象となるレベル」)ではなくAI設計判断(`DESIGN_02.md:5,77`、`er120:42`、DECISION_LOG:21)だった=是正対象。
- 設計要点: 候補抽出→全候補Step B事前生成(`grammar_explanations.json`、PREGEN_MAX=8、直列、signature一致で再利用、失敗STOP・再開で未生成分のみ)→HR/フォーム(文法名+解説全文)→最大2件確定・凍結→finalize(LLM 0)→公開(Adv=Part 1直後、Std=Stdの節に文法ブロック)。Prompt sha・eligible7・Trial-08 Tier無変更。Step B呼出点をpregen 1箇所に集約、`run_part2`/finalizeは生成禁止(fail-closed)。`part2_grammar_v2(items[])`/`grammar_human_review_v2(pick)`。KCP接続(explanations_sha256固定、from-form文法照合、level別sidecar、凍結items[])。X/Y/Z adapter。Std候補0件=正常。
- Fable設計判断D-a〜D-h(StdへのPrompt無変更/失敗STOP再開/PREGEN_MAX=8/Std ZERO同一文面/2件表示=本文出現順/`ref_ja=None`/Std文法ブロックはStdの節・Part 1はAdv限定のまま=原文は文法解説のみ対象/auto採用TOP1)、evidence=方式A(copy-run、≤¥40。方式B=新規記事E2E約¥200は次の通常制作に相乗り)。新仕様判断=なし。
- 費用見込: Step B ¥0.05-0.11/call、増分/記事セット X約¥0.9/Y約¥0.8/Z約¥0.34(保守¥2.7/2.1/0.9、¥70比≤4%)。Std候補数は未観測(evidenceで計測)。
- 撤去予定: `FAMILY_Y/Z_PART2_ON_STANDARD_PAGE`(置換)、X `--stage study_text`のAdv限定parser.error、`run_part2`内の選定後Step B、`m.LEVEL=="Advanced"` assert。
- 次: Opus条件A→委任_02(核)→委任_03(adapter・ページ・Validator)→委任_04(KCP/FORM接続)→委任_05(evidence→SSOT→Fable受入)。

### C. KP-CONFIRMED-CONTENT-PROTECTION-01(OPEN-556) → IMPLEMENTED(第1段+第2段)+EVIDENCE部分(X a2下流実走・Z実走、Y runner下流は旧run起因で未達→委任_03で現行run補完中)。PRODUCTION_WIRED未判定(6経路揃い+文法事前生成接続後)
- 02B(438ac1b22/93915b971): G2〜G4(AND・fail-closed)、M6 Part 2凍結(`frozen:<sha>`、revoke必須、`ref_ja`は差異時のみISSUE)、M8再バインド(出典文逐語→API 0連鎖更新、不成立ISSUE)、M2-b(Y/Z Stdページ「日本語の意味」=表示用`japanese_gloss`。既存Y/Z a2 44件で表示が変わる記事0件)、Z `_gloss_person_gate`ISSUE化、LR重なり警告のみ(既存18 runで重なり0件)、単一アクセサ、actor=evidence(「ユーザー確定ではない」明記)。同一委任内是正3件(M8曲線引用符の誤ISSUE→NFKC正規化、Z/Y `part2_cand_b1b`来歴shaにmodel混入で解消不能STOP→`cand_input_sha`据置、evidence対照が実コピーを退避→復元)。test er128 84/84、他回帰は既存失敗のみ。evidence実費¥7.45(X ¥7.39=不要なFull Story TTS再生成を含む=反省記録、Z ¥0.06)。公開URL G3: Y PASS、Z BLOCK(melos kphr_evidence_r3の旧公開訳≠現doc=旧ページと現docの差、保護の欠陥ではない)。
- 委任_03(進行中): Y現行run(`run_style_fix_01`コピー)・X Adv・Z Std/Advの補完、TTS再生成禁止、上限¥20。
- 新規OPEN候補: 「melos kphr_evidence_r3 公開ページの訳が現docと不一致」=修正へ進む候補(軽微、再ビルド要否)。er020 `test_recorded_candidates`はOPEN-543へ統合。
- `er119_grammar_review_01.py`を所有外で編集(並行所有なしを確認済み)=記録のみ。

### D. LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01(OPEN-545) → IMPLEMENTED+公開+自己検証(承認済み表示仕様は全て反映済み。ユーザー実操作確認待ち。Production runnerからの自動出力接続=GPG委任_04で実施予定)
- 委任_04(802bbf853/aa6dc9075): cap 12・kind別cap 7/5・`reason_ja`逐語、7+5 evidence 8doc追加(旧3+5は`data/legacy/`)、node 45/py 15/公開headless 38+19+9。
- 委任_05(9a1b08a1b/44f3b48d7): 理由なし候補は理由欄非表示(「AI理由なし」撤去)、7+5 docの理由欠落は`data_warnings[reason_missing_in_p7w5]`警告、node 47/py 17/公開headless 30。
- ユーザー決定§2でフォームv3は正式採用(FIX)。追加UI変更なし。

### E. FAMILY-Y-STYLE-PROFILE-FIX-01 委任_06(01e7d02ec) → OPEN-537/539/550/552更新
- ユーザー承認(原文=`docs/pm/delegation_log/2026-10-27_FAMILY-Y-STYLE-PROFILE-FIX-01_USER_03.md`): Std preview Take 1をHR PASS確定(採用tool正規手順、approved_by=user、lock RESOLVED/HUMAN_APPROVED、preview entry復元=OPEN-552解消)。`fx_20261017`適用のStd/Adv完成版を組立(Style Gate 18/18・15/15、clipping 0、page_verify ok)、通常の最終試聴ページ`_03/index.html`公開(Std 337.2s/Adv 314.9s通し、旧index→`preview_segments_01.html`)。費用0円。**Fable受入OK(2026-10-27)→ユーザー最終試聴待ち**(承認まで最終受入としない)。OPEN-539のStatusを「`_03`完成版・ユーザー最終試聴待ち(Fable受入済み)」へ。OPEN-537は「是正完了・完成版公開・ユーザー試聴承認待ち」。UDR-YRF-2/3撤回済み。
- 注記: Y runnerに`provision_shell`は存在しない(Z専用)。Fable委任文の誤記、未起動で副作用なし。`docs/pm/DELEGATION_STANDARD_TEMPLATE.md`にFamily別stage名の注意(X/Y/Zのrunner `--stages`一覧は各runner `--help`で確認、`provision_shell`はZのみ)を1項追記。

### F. PM_GOVERNANCE違反記録(既存の違反記録節へ追記。Grep `違反記録|stash`で位置)
1. PM-SSOT-SYNC-19 agentが`git pull --rebase`を試行(dirty treeで失敗、履歴書換えなし)=禁止操作の試行として記録。
2. GRAMMAR-PREGEN-ALL-LEVELS-01 委任_01 agentが`git add -f docs/pm/RESULT_PACKET_GPG1.md`(gitignore対象を強制追加、`-f`禁止)=違反。**本委任で`git rm --cached docs/pm/RESULT_PACKET_GPG1.md`により追跡解除**(ローカルファイルは残す)。
3. KP-CONFIRMED-CONTENT-PROTECTION-01 委任_02B agentがコピーrunで同一run 300秒内3回起動→RESTART_STORM自発動(費用0、STOP未解除)=起動規律違反。同委任で不要なFull Story TTS再生成¥7.39(evidence目的に不要)=費用規律の反省。
4. 再発防止: 委任テンプレ固定ブロックに「`git add -f`/`pull --rebase`禁止の再掲」「同一run起動間隔150秒・5分3回禁止」「有料stage実行前に『そのstageがevidenceに必要か』を1行記録」を追記(`DELEGATION_STANDARD_TEMPLATE.md`)。

### G. ACTIVE_TASK.md
管理ID=PM-SSOT-SYNC-20、進行中=KCP 委任_03(evidence)・GPG Opus条件A、UDR-blocking=Y `_03`最終試聴承認・フォーム実操作確認・OPEN-526・UDR-MONKEY-1、QDC=2026-10-27当日 約¥33(TRU 1.15+KP75 15.84+KCP2B 7.45+他)、次=GPG委任_02〜05、KCP3受入→SYNC-21。

## 事前指定Grep一覧+追記位置・更新位置の手順

- `OPEN_ITEMS.md`: Grep `OPEN-556|OPEN-545|OPEN-537|OPEN-539|OPEN-550|OPEN-552|OPEN-543|OPEN-519|UDR-FORM-1`→該当行末尾追記。新規OPEN-559(文法事前生成)・OPEN-560(melos旧公開ページ訳不一致、軽微)を末尾追加(現最大OPEN-558をGrepで確認)。
- `CURRENT_SPEC.md`: Grep `Part 2|文法解説|Advanced.*のみ|b1b.*のみ`(:2080,:2096-2099,:3104付近)→注記・履歴化。
- `DECISION_LOG.md`: 先頭ヘッダーチェーン規則(Grep `^## `)に従い新規エントリ。
- `docs/pm/PM_GOVERNANCE.md`: Grep `違反記録|stash|9-15`。
- `docs/pm/DELEGATION_STANDARD_TEMPLATE.md`: Grep `固定ブロック|T-2|Git`→追記。
- `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `UDR-FORM-1|UDR-YRF`→解消/撤回を記録。

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-27_PM-SSOT-SYNC-20_DELEGATION_01.md --json-out ...\_check.json`
- `git rm --cached docs/pm/RESULT_PACKET_GPG1.md`(追跡解除のみ)
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

上記A〜G(本委任が編集)。

## Git

- commit message: `PM-SSOT-SYNC-20: ユーザー正式決定(フォームv3/文法事前生成/選定理由/確定内容保護 全6経路)記録、OPEN-559/560起票、OPEN-556/545/537/539更新、Y _03 Fable受入、違反記録+RESULT_PACKET_GPG1追跡解除(API 0)`。push。

## 報告

`docs/pm/RESULT_PACKET_SSOT20.md`: (0)T-0、(1)更新箇所一覧(ファイル:行)、(2)齟齬・保留、(3)必須4行+「判定整合: 重大NG=<なし|あり>」、commit hash・raw URL。末尾5行要約。
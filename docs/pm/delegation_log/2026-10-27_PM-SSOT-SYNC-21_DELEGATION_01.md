## 管理ID

PM-SSOT-SYNC-21(SSOT同期: ユーザー正式決定3件の記録(①Y再配達Closeout+Voice説明文+Chunk境界マーカー[USER_04]、②AI島Std/Adv KP/KW各10件USER_CONFIRMED+文法選定仕様変更[Top1/Top2提示・1件選択・0件可・2件禁止]APPROVED_FOR_PRODUCTION[AI-ISLAND USER_02]、③AI島V3フォーム実運用指示[AI-ISLAND USER])、GRAMMAR-PREGEN-ALL-LEVELS-01 委任_02/_02S/_03/_04(OPEN-559更新)、KP-CONFIRMED-CONTENT-PROTECTION-01 委任_03(OPEN-556更新)、FAMILY-Y-STYLE-PROFILE-FIX-01 委任_07(OPEN-537/539更新、CURRENT_SPEC是正)、AI-ISLAND-FORM-PRODUCTION-01 委任_01(新規OPEN起票、OPEN-526整理)、PM_GOVERNANCE違反記録。API 0・JPY0)。**本委任のみがSSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`)・`docs/pm/ACTIVE_TASK.md`・`docs/pm/PM_GOVERNANCE.md`・`docs/pm/USER_DECISION_REGISTER_01.md`の編集権を持つ**。並行Agent: GPG 委任_05A(コード)、AI-ISLAND 委任_02(フォーム)、YSP 委任_08(Yページbuilder)=SSOT非編集。所有=上記SSOT 6ファイル、`docs/research/PM-SSOT-SYNC-21/REPORT_01.md`、`docs/pm/delegation_log/2026-10-27_PM-SSOT-SYNC-21_DELEGATION_01.md`(+check.json)、`docs/pm/RESULT_PACKET_SSOT21.md`(gitignore、`-f`禁止)。pathspec付きcommit(他Agentのstage分を巻き込まない=`git commit <pathspec>`)。

## 性質/禁止

- 性質: SSOT同期(Fable判定の転記・整合)。到達上限=同期完了。
- 禁止: SSOT全文読込、判定変更、Status格上げ(下記Fable判定どおり)、禁止Git操作(`add -f`/`pull --rebase`/pathspecなしcommit)、worktree stale上書き(編集直前に`git log origin/main -1 -- <path>`)。
- 時間見込み: 約1h。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文保存+check、結果1行。T-2/T-3: なし。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-27_PM-SSOT-SYNC-21_DELEGATION_01.md` をN=727から順に試し、先頭「## 管理ID」+「PM-SSOT-SYNC-21」のものを採用。

## Fable判定(転記内容。一次資料=`docs/pm/RESULT_PACKET_{GPG2,GPG2S,GPG3,GPG4,KCP3,YSP7,AIF1}.md`の(7)/(8)SSOT文案。齟齬はFable判定優先。ユーザー原文=`docs/pm/delegation_log/2026-10-27_FAMILY-Y-STYLE-PROFILE-FIX-01_USER_04.md`、`2026-10-27_AI-ISLAND-FORM-PRODUCTION-01_USER.md`、`2026-10-27_AI-ISLAND-FORM-PRODUCTION-01_USER_02.md`(並行Agentが保存中。未作成なら本委任文の要約を根拠にし「原文保存は委任_02」と注記))

### A. DECISION_LOG新規エントリ(3件のユーザー決定)
1. **Y再配達Closeout(USER_04、2026-10-27)**: (A)`_03` Std/Adv最終試聴PASS・正式承認(音声sha std_full `7c037f49…`/adv_full `f2c7d26f…`、本文・KP・学習内容承認、表示修正に伴う再生成・再試聴不要)。(B)Voice説明文の正式文言「Voice 1〜3は実在人物の発言をそのまま再現したものではなく、実際に投稿された意見をもとに、AIが編集・再構成したものです。」=Family Y共通・将来アプリ表示でも同一・実投稿に基づく記事のみ適用(根拠のない出典主張を生成しない)。(C)開発用Chunk境界マーカー: 実TTS Chunk分割境界のみ`⏸`(秒数・説明なし)、ASRポーズ非表示、**開発段階のユーザー確認用表示に限定**(量産スクリプト・公開コンテンツ・アプリには表示しない)、X/Y/Z共通、Chunk分割・ポーズ長・音声生成仕様は不変。OPEN-537のWIRED再確認指示(ユーザー試聴PASSを自動認定根拠にしない)。
2. **AI島確定+文法選定仕様変更(AI-ISLAND USER_02、2026-10-27)**: AI島Std/Adv KP/KW各10件(①3/②2/③5、全件official訳、candidate_id・本文SHA・候補集合SHA付き)=USER_CONFIRMED。文法=Std/Advとも再選定待ち(0件確定にしない)。**文法選定仕様の正式変更(全Family共通、APPROVED_FOR_PRODUCTION)**: AI評価Top1/Top2の最大2件のみ提示(順位順)、文法名+解説全文を選定前表示、ユーザーは原則1件選択・0件可・2件同時選択禁止、確定後不変、事前生成はTop2のみ(費用削減、Trial-08・品質仕様不変)、旧「文法最大2件選定可」を置換(フォームUI/schema/Validator/HR/確定保存/finalize/公開/retry系/CURRENT_SPEC/test)。公開対象はX/Y/Z Std/Adv全て。到達目標PRODUCTION_WIRED(全6経路)。
3. **AI島V3フォーム実運用(AI-ISLAND USER、2026-10-27)**: 既存本文再利用・再生成禁止、7+5既存結果再利用、文法は今回記事限りの暫定事前生成を許可(正式配線と区別)、第1報=選定待ち(提出済み)、全Family WIRINGとは別管理。

### B. CURRENT_SPEC
- 文法選定節(SYNC-20で「Std/Adv両方・事前生成へ移行(実装中)」注記済み)に、上記2の新仕様(Top1/Top2提示・1件選択・0件可・2件禁止・事前生成Top2のみ)を追記し、旧「最大2件選定可」(フォームv3仕様の「文法は独立枠で最大2件」を含む)を「2026-10-27決定で置換・旧仕様」として履歴化(フォームv3節 Grep `文法.*最大2|独立枠`)。
- Y Style節(`:3166`付近「別途Fable」)は、委任_07照合結果「確認条件1〜7充足、条件8(Fable独立受入)は全体回帰後に判定」へ更新(WIREDとは書かない)。
- Y Voice説明文の正式文言・適用条件、Chunk境界マーカー表示仕様(開発用限定・X/Y/Z共通・既定public)を新規節または既存Y節へ追記(実装=委任_08進行中と注記)。
- 確定内容保護の正式節(KCP 02A/02B/委任_03の実装内容: 確定レコード・G0〜G4・操作ガード・legacy drift・M2-b・M6・M8・6経路evidence状況)を新設(PRODUCTION_WIREDではなくIMPLEMENTED+EVIDENCE(X/Z Adv/Y)と明記)。
- 7+5節のフォーム連携欄にcap 12・理由欄非表示規則(FORM委任_04/05)を追記。

### C. OPEN_ITEMS
- **OPEN-559(文法事前生成)**: 委任_02(核 b27d88309)・_02S(Std候補率 X1.25/Y2.0/Z0.4、0件はZ 3/5、実費¥3.885、evidence元run=X part2_hr_evidence_01__run_r1/Y run_style_fix_01/Z melos r3・r4、EVIDENCE_PLAN_02 上限¥150)・_03(X/Y/Z配線 e2785c11a/c3b83a3e0、Std節文法ブロック、節単位4者一致、`*_ON_STANDARD_PAGE`撤去、D1再バインド、D4)・_04(er128/CLI/exporter接続 dafd60693)→Status=IMPLEMENTED(配線)。既知不具合1件(wiring: 凍結済み文法がmodel変更でPart2Stale、`expectedFailure` test、委任_05Bで是正)。**仕様変更(上記2)により委任_05A(核≤1化・Top2のみ事前生成・grammar-pending)進行中**。Opus条件A(M必須修正1〜7全件採用、Fable判定F-1〜F-7)。
- **OPEN-556(確定内容保護)**: 委任_03(12aede6f7): 6経路化=X Std/Adv・Y Std/Adv(現行runner世代コピー、gate通過後はHR Lock起因で別理由停止)・Z Adv=実runnerで確定→下流→改変BLOCK実測、Z Std=関数レベル+改変STOP(現行仕様のStd runなし、次回Z記事で採取)。是正1件(G2が`phrase_repeat`未検査→3行追加+test 2件)。02Bの「Z公開URL G3=旧公開訳」は検査ページ取り違えの誤記(index.html PASS)→OPEN-560を「誤記・CLOSED」へ。所見D1/D4=GPG委任_03で是正済み、D3(Std G3 any-of)=低優先・残。実費¥0.71。Status=IMPLEMENTED+EVIDENCE_COLLECTED(X/Z Adv/Y)、PRODUCTION_WIREDは文法新仕様接続後に全6経路で判定。
- **OPEN-537**: 委任_07照合=確認条件1〜7充足(根拠=`WIRED_CHECK_01.md`)、条件8=Fable独立受入は全体回帰(委任_08後)で実施。`_03`表示修正(ポーズ表示19箇所撤去・説明文差替え、音声sha不変、945b07a28)。Status=「是正完了・ユーザー承認済み・WIRED判定待ち(全体回帰後)」。
- **OPEN-539**: ユーザー最終試聴PASS・正式承認(USER_04 §1-A)→**CLOSED(記事承認)**、表示修正は委任_08で整合確認中。
- **OPEN-526**: AI島旧HR(7件PENDING、ユーザー明示確定なし)はユーザーのフォーム選定(USER_02、KP/KW各10件USER_CONFIRMED)で置換。旧runは残置(破壊しない)。→CLOSED(フォーム確定へ移行)。
- **OPEN-545(フォーム)**: AI島Std/Adv登録(委任_01 bc11b0197/10708c8c1)、文法枠は新仕様(Top1/Top2・1件)へ変更中(AI-ISLAND委任_02)。
- **新規OPEN-561**: AI-ISLAND-FORM-PRODUCTION-01(AI島Std/Adv V3フォーム実運用・完成記事制作、修正へ進む)。Status=第1報提出済み(2026-10-27)、KP/KW各10件USER_CONFIRMED(保存=委任_02)、文法Top1/Top2再選定待ち(USER_DECISION_REQUIRED=ユーザー選定)、文法暫定事前生成(実費¥0.873、Std 4/Adv 3候補)は正式配線と区別。
- **OPEN-543**: GPG委任_03報告の既存失敗3件(er019 R4Hunk UNCLASSIFIED+9、er121 NoticeDisplay test=KCP3 evidence_runs/y2/_bak_index.html検出→退避/除外要、er003 Part1 test=確定後KP書換えをG0が止める→期待値更新要)を追記。
- **OPEN-558**(gloss不対応)変更なし。OPEN-549(補完自然発火): 単語補完2件観測(Y)を追記。

### D. USER_DECISION_REGISTER
- 新規: AI島文法Top1/Top2選定(Std/Adv、USER_DECISION_REQUIRED、提示=AI-ISLAND委任_02後)。UDR-MONKEY-1据置。OPEN-526のUDR=解消(フォーム確定へ移行)。

### E. PM_GOVERNANCE違反記録(既存節へ追記)
1. KCP 委任_03: 起動間隔150秒未満×2(139秒・120秒)、コピーrunでRESTART_STORM自発動(STOP未解除)後に**別コピーで続行**=安全停止の実質回避(Fable判定: Production・公開物・HR Lock影響なし、evidenceは採用、再発防止=STOP発生時は停止・報告し続行しない)。
2. KCP 委任_03のcommit `12aede6f7`にGPG 委任_02Sのstage済み24ファイルが同梱=**pathspecなしcommit**(禁止)。履歴書換えはしない。再発防止=`git commit -- <pathspec>`の徹底(テンプレ既記載)。
3. GPG 委任_03: 作業中にPID 2件をtaskkill(コマンドライン未照合)=プロセス操作の確認不足として記録(影響なし)。
4. 委任_02B(既記録)の追記: Y/Z evidenceでrepo内run root直下に実コピーを置いた(完了後退避、残存なし)。

### F. ACTIVE_TASK.md
管理ID=PM-SSOT-SYNC-21、進行中=GPG 05A/AI-ISLAND 02/YSP 08、UDR-blocking=AI島文法Top1/Top2選定(第1報提出後)・フォーム実操作確認・UDR-MONKEY-1、QDC=2026-10-27当日 約¥38(TRU 1.15+KP75 15.84+KCP2B 7.45+KCP3 0.71+GPG2S 3.885+AIF1 0.873+他)、次=GPG 05B(wiring≤1化+既知不具合是正)→委任_05 evidence→SYNC-22、Y WIRED判定(委任_08後)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- `OPEN_ITEMS.md`: Grep `OPEN-559|OPEN-556|OPEN-537|OPEN-539|OPEN-526|OPEN-545|OPEN-543|OPEN-549|OPEN-560`→行末追記/Status更新。新規OPEN-561を末尾(現最大OPEN-560確認)。
- `CURRENT_SPEC.md`: Grep `文法|Part 2|最大2|独立枠|fx_20261017|別途Fable|確定内容|Voice 1〜3|⏸`→該当節に追記・履歴化。
- `DECISION_LOG.md`: 先頭ヘッダーチェーン規則(Grep `^## `)で3エントリ追加。
- `docs/pm/PM_GOVERNANCE.md`: Grep `違反記録`→末尾追記。
- `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `UDR-|OPEN-526|MONKEY`→更新。

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-27_PM-SSOT-SYNC-21_DELEGATION_01.md --json-out ...\_check.json`
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

上記A〜F(本委任が編集)。

## Git

- commit message: `PM-SSOT-SYNC-21: ユーザー決定3件(Y Closeout/Voice説明文/Chunkマーカー、AI島KP確定+文法Top1/Top2仕様、AI島実運用)記録、OPEN-559/556/537/545更新、OPEN-539/526/560 CLOSED、OPEN-561起票、違反記録(API 0)`。push。

## 報告

`docs/pm/RESULT_PACKET_SSOT21.md`: (0)T-0、(1)更新箇所一覧(ファイル:行)、(2)齟齬・保留、(3)必須4行+「判定整合: 重大NG=<なし|あり>」、commit hash・raw URL。末尾5行要約。
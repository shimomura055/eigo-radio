## 管理ID

PM-SSOT-SYNC-16(本日後半の案件のSSOT反映: 選定フォームv3・Gate除外補完・Y Style是正の進捗・OPEN-535 evidence・OPEN-540 IMPLEMENTED・新規OPEN起票。API 0・JPY0)。並行Agent: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_03(evidence、SSOT編集権なし)。**SSOT編集権は本委任のみ**。所有=`OPEN_ITEMS.md`・`CURRENT_SPEC.md`・`DECISION_LOG.md`・`docs/pm/USER_DECISION_REGISTER_01.md`・`docs/pm/ACTIVE_TASK.md`・`docs/pm/delegation_log/2026-10-26_PM-SSOT-SYNC-16_DELEGATION_01.md`(+check.json)・`docs/pm/RESULT_PACKET_SSOT16.md`。pathspec付きcommit。index.lock競合は10秒待って再実行(最大3回)。worktree SSOTがHEADより古ければHEAD blob書き戻し後に自hunk追加。

## 性質/禁止

- 性質: SSOT同期(Fable判定の転記)。到達上限=SYNCED。
- 禁止: SSOT全文読込、コード編集、判定語の格上げ(本委任で`PRODUCTION_WIRED`と書く項目はなし)、禁止Git操作。
- 時間見込み: 約1h。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1/D-1/G-1/F-1: 従来どおり。T-0: 委任文保存+`check_delegation_prompt.py`、結果をRESULT_PACKETへ1行(FAILでも継続)。T-2: TTSなし。T-3: 費用なし。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_PM-SSOT-SYNC-16_DELEGATION_01.md` をN=691から順に試し、先頭「## 管理ID」+「PM-SSOT-SYNC-16」のものを採用。

## 事前指定Read一覧(文案の正本。Fable判定と矛盾すればFable判定優先)

- `docs/pm/RESULT_PACKET_FORM1.md`(9)SSOT文案、`docs/pm/RESULT_PACKET_KBF2.md`(8)、`docs/pm/RESULT_PACKET_KBF3.md`(8)、`docs/pm/RESULT_PACKET_YSP2.md`(9)、`docs/pm/RESULT_PACKET_YSP3.md`/`YSP4.md`(要点)、`docs/pm/RESULT_PACKET_YHG1.md`(SSOT文案)、`docs/pm/RESULT_PACKET_TRU2.md`(9)
- `docs/pm/delegation_log/2026-10-26_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_USER.md`(承認原文: §1 APPROVED_FOR_PRODUCTION、§6受入条件11項目、§7)
- `CURRENT_SPEC.md`: Grep `外側retry|n_auto<3|gate_dropped` → :2021付近、Grep `Family Y.*Style|fx_20261017|default` → Y節、Grep `公開一覧|redelivery` → 公開一覧
- `OPEN_ITEMS.md`: Grep `^\| OPEN-(534|535|537|539|540|526|544) `、末尾の最大ID(新規採番用)

## 事前指定Grep一覧+追記位置・更新位置の手順

- OPEN行: headのStatus語置換+行末追記`**2026-10-26追記(PM-SSOT-SYNC-16): …**`。履歴削除なし。
- 新規OPENは末尾に採番(11-8分類必須)。

## Fable判定(転記)

### A. 新規OPEN: 学習項目選定フォームv3(LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01)
- 種別=ユーザー正式採用(APPROVED_FOR_PRODUCTION、原文§1)の実装。Status=**IMPLEMENTED・公開・自己検証済み・ユーザー実操作確認待ち(受入条件11)**。PRODUCTION_WIRED未判定(補完機構と受入条件11項目が揃ってからFable判定)。
- 事実: 公開URL `https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/`、commit 0f4caaaff/77e445d45、参照HTML `docs/pm/Phrase_Form/eigo_radio_selection_form_reference.html` 無改変保全(sha256 13ef9085…)、差異15件はUI不変(DIFF_01)、node 25/Python 6/headless 32項目PASS、送信=ChatGPT `?q=` URL生成+ワンクリックコピー(chatgpt.com反映・実コピー成功は**未検証**)。試作候補=DEV Trial-02由来(猿の手Adv、7+4)+Production候補版6件(`*_prod`、うち猿の手Advはreplay由来と明記)。文法=「候補なし・要生成」(仮データ不使用)。
- 判断候補(11-8 D): (1)文法選定の型=フォーム「文法名+解説全文・最大2」vs 現行Part 2「英文1つ選択→解説後生成・最大1」。Fable推奨=Part 2候補の英文ごとに短い解説を事前生成して全文表示(費用数円/level増)。代替=フォーム側変更(承認済みUI変更)。(2)候補ソース=OPEN-534へ統合(現行3+最大5・単語0 vs 7+5未採用)。(3)「既存Family X記事選定フォーム」はRepo内に不在(事実、ユーザーへ確認中)。
- UDRへ: (1)文法の型(推奨a)。

### B. 新規OPEN: Gate除外候補の補完(KP-GATE-DROP-BACKFILL-PRODUCTION-01)
- 種別=ユーザー正式採用(APPROVED_FOR_PRODUCTION、原文§3)の実装。Status=**IMPLEMENTED+EVIDENCE_COLLECTED(条件付き)**。PRODUCTION_WIRED未判定。
- 事実: 設計 f5d466617、Opus条件A GO with changes(M-1〜M-7/R-1〜R-10反映)、実装 cbcd29d27/61ad83b93(`er119_kp_backfill_01.py`、`_generate_candidates_impl`配線1箇所、既定ON `EIGO_KP_BACKFILL`、test 55件、Prompt 2-V本文sha不変、A/B/C・runner差分0)、evidence 2b3fcefe1/109fc9016(fresh 10 level-run: 自然発動=X中東Std E=1/Adv E=2・Y再配達Std E=1・Zメロス Std E=1、不発動=E=0の6件[初回上限未満でE=0の不発動をX AI島Std/Adv・Y Adv・コーヒーStdで観測]、救済済み非計上、外側retry不発火、resume再課金0、HR依頼書表示、Z SRC D1 PASS、replay 7件補助、実費¥26.25、補完1発動あたり¥0.585〜0.710)。**未観測**: Y Adv・Z Advでの自然発動(不発動のみ観測)、call1最終attempt除外計数(M-1、mockのみ)、AUTO n_auto<3挙動(mockのみ)。
- 承認範囲と区別した挙動変更(ユーザーへ報告済み2026-10-26): 外側retry条件(`n_auto<3 and (gate_dropped or rescued_not_auto)`の全件再生成)を補完ON時に撤去(原文§3-1「初回合格候補を保持し入れ替えない」に従う。OFFで完全復帰)。call1のattempt内再選定は現行維持(K0)。2-Vへ除外noteを後置(新Promptではない)。単語枠は種類別計数のローカル規則(単語専用抽出は7+5採用待ち)。
- CURRENT_SPEC: :2021付近の外側retry記載を更新(「補完ON時は撤去。候補0件・技術失敗のretryは存続。OFF時は旧条件」)+補完仕様の新節(発動条件・件数・順序・救済非計上・1回限り・kill switch・データ契約path)。「PRODUCTION_WIRED」とは書かず「IMPLEMENTED・evidence取得(条件付き)」。
- 新規OPEN候補(別行): (b1)K1=call1のattempt内全件再選定のitem単位化(承認済み仕様CURRENT_SPEC:2010/2016の変更=D、evidenceで頻度を見てから)。(b2)**猿の手 seed provenance不一致**(`the_monkeys_paw/seed/seed.json` 10-25更新 sha 8f763160… vs 既存runのwriter provenance 8f1128b9…→Z runner経由の猿の手新規KP生成が`FamilyZProvenanceMismatchStop`で不可。公開物不変。分類=要照合[10-25 seed更新の意図]→再pinで足りればB、本文再生成が必要ならD)。(b3)Y Adv/Z Advの自然発動の追跡(次の正式runで記録、分類=追跡)。

### C. OPEN-537/539(Y Style是正・再配達)
- OPEN-537: 「是正実装完了(3af84a499: fx_20261017継承・固定記録・fail-closed Gate・Y_ROLE_COVERAGE完全一致・test 37件)、再生成完了(d2d68194d、Adv 15/15 PASS、Std 16/18→y_voice_1はFable許可の再生成で新take4がPASS[b9be75ef4、was/is読み違い疑いを回避]、実費計32.09円)。残=Std preview 1件のHR承認(ユーザー、表記ゆれのみ)→通し版組立→Fable受入→`_03`再試聴+S9(Voice 1〜3のPD06可否、A19条件付き承認・未評価)」。PRODUCTION_WIREDとは書かない。
- OPEN-539: 「`_03`先行公開(a3f693b83/bd52cde30: Adv修正版segment個別再生・Voice 1〜3旧新比較・Std HR試聴節)。旧`_02`承認=旧版扱い。新版の再試聴・再承認待ち」。公開一覧(CURRENT_SPEC)に`_03`(先行版・未完成)を追記。
- 新規OPEN候補: (c1)ASR表記ゆれ(ハイフン・かな漢字)でHR待ちが出る(Gate条件変更を伴うためD候補。AI側で対策案整理中)。(c2)Z側Style実測照合の網羅確認(read-only、B)。(c3)Y runner `--only-segments`実行でpreview entryが`SKIPPED_NOT_SELECTED`に置換される副作用(実害なし・採用toolで復元、B)。
- OPEN-535: 「FIXED(5568631ba)+実経路evidence(d2d68194d: run_style_fix_01で意図的複製した旧y_voice_1承認が`Y_HR_APPROVAL_VOICE_UNDETERMINABLE`で退避→Puckで再生成)。Fable受入=**PRODUCTION_WIRED(Y経路)**判定はFableが別途(本委任では「evidence取得済み・Fable受入待ち」)」。

### D. OPEN-540
- 「IMPLEMENTED(18d997941/e8773980a/65e5b036e: er127共通核・leaf L1〜L8・X/Y/Z call site・Opus M-1〜M-11反映・test 97件・A/B/C golden 80ケースbyte同一)。委任_03 runtime evidence進行中(上限¥280)」。OPEN-376/312/U-04/U-12=「解消(evidence確認待ち)」。

### E. UDR/ACTIVE_TASK
- UDR: 新規「文法選定の型(フォーム)」「Std preview承認(`_03`)」「S9(`_03`完成後)」。OPEN-526/534は据置。
- ACTIVE_TASK: 管理ID=並行(TTS統一evidence)/UDR-blocking=OPEN-526・534・preview承認・文法の型/QDC=当日約¥621+TTS evidence進行中(上限¥280)。

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-26_PM-SSOT-SYNC-16_DELEGATION_01.md --json-out docs\pm\delegation_log\2026-10-26_PM-SSOT-SYNC-16_DELEGATION_01.md_check.json`
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## Git

- add対象: `OPEN_ITEMS.md`、`CURRENT_SPEC.md`、`DECISION_LOG.md`、`docs/pm/USER_DECISION_REGISTER_01.md`、delegation_log。pathspec付きcommit。
- commit message: `PM-SSOT-SYNC-16: 選定フォームv3/Gate除外補完(IMPLEMENTED+evidence条件付き、外側retry変更記録)、OPEN-537/539/535進捗、OPEN-540 IMPLEMENTED、新規OPEN(K1/猿の手provenance/ASR表記ゆれ等)(API 0)`
- trailer: `Delegation: PM-SSOT-SYNC-16/01`
- push: `git push origin HEAD:main`。

## 報告

`docs/pm/RESULT_PACKET_SSOT16.md`: (0)T-0、(1)編集箇所一覧(ファイル:行、新規OPEN ID)、(2)Fable判定との差異、(3)必須4行+「判定整合: 重大NG=<なし|あり>」、(4)commit hash・raw URL。末尾5行要約。
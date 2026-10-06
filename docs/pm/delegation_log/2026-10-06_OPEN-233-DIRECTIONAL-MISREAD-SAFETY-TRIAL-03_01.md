## 管理ID
OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-03(委任_01: Trial script v3。修正1=時間的位置の区別、修正2=NONE時の限定フォールバック。API呼出は本委任では行わない)。並列委任_02(held-out/testset_03/正解)、_03(集計)、_04(SSOT)が同時進行。**書込先: `er052_open233_directional_trial_03.py`(新規、v2 `er052_open233_directional_trial_02.py`はimport流用し変更しない)、`er052_open233_directional_trial_03_test.py`、`er052_output/open233_directional_misread_trial_03/dryrun/`、`docs/pm/RESULT_PACKET_T03_01.md`、`docs/pm/delegation_log/`。Production code・SSOT・git操作なし。**
作業方式: Edit/Write 1回40行以内(関数単位)、Bash heredoc不使用、説明最小。T-0はWrite+Edit追記で逐語保存(必須見出し「事前指定Read一覧」「事前指定Grep一覧+追記位置・更新位置の手順」「実行コマンド全文」を含む)。時間目安25分。

## 性質/到達上限Status/禁止事項
性質: Trial専用script(¥0、dry-run)。到達上限: unit test PASS+dry-run完走。禁止: 有料API/Production変更/floor復活/gold・KPI変更/Opus承認のない新構造(修正1・2以外の新機構を足さない)/前回の誤修正案(事象名具体化・部分一致拡大)の混入。Opus Gate: 設計はOPUS-REVIEW-03で承認済み(本委任はその実装、Trial専用)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力不使用。F-1: 退避不要。T-1: 事前指定一覧に従う。T-0(常時有効): 委任文を`docs/pm/delegation_log/2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-03_01.md`へ逐語保存し`check_delegation_prompt.py`実行、結果1行をRESULT_PACKETへ。T-2/T-2追記(7-5): TTSなし。T-3: 本委任¥0(実行は別委任、上限¥8は`--budget-yen`で強制)。

## ユーザー指示(原文、要点)
> 修正1: Ledger側の事象について INTERIM(途中の変化)/FINAL(最終状態・結末)/SINGLE(区別がない単一事象)を抽出する。記事側も必要な範囲で INTERIM/FINAL/UNSPECIFIED を判定する。そのうえで、同じ時間的位置に属する事象同士だけを方向比較する。
> 修正2: factとの対応が既に分かっている記事文について、通常の事象選択がNONEになった場合のみ、各事象を個別に確認する方式へフォールバックする。無条件に全事象総当たりへ戻さないこと。
> 構成X: NONEフォールバック中心/構成Y: 時間的位置の区別+NONEフォールバック。
> 「限定語なしの方向表現を最終結果として読む」は新しいProduct基準ではなく、Trial上の判定方法として検証する。

## 設計(固定。v2との差分のみ実装、他はv2を流用)
1. Ledger側抽出(v2+phase): events=[{subject_x, result_state, phase∈{INTERIM,FINAL,SINGLE}, quote}]。promptに「同じ対象について途中の変化と最終状態が両方ある場合、途中=INTERIM、結末=FINAL。区別がない単一事象=SINGLE」を追記。`--ledger-only --ledger-repeat 3`→`ledger_cache.json`(v2と同形式+phase)。phase欠落はSINGLE扱い(記録)。
2. 記事側(blind、v2の単一選択+phase): 入力=subject_xラベル一覧(重複除去、**phase・state・quoteは渡さない**)+記事文+前後文(あれば)。schema `{selected_subject: str|"NONE", result_state: enum, phase: INTERIM|FINAL|UNSPECIFIED, quote}`。promptに「文が『一時的・途中の動き』(briefly/initially/temporarily等)を述べていればINTERIM、結末・現状を述べていればFINAL、判断できなければUNSPECIFIED」を追記。
3. 比較(Python): 構成Y=選択subjectのevents(同一subjectに複数eventあり得る)から、記事phaseがINTERIM→Ledger phase INTERIMのevent、FINAL/UNSPECIFIED→FINAL/SINGLEのeventを**一意に**選び`compare()`(v2規則)。該当phaseのeventが無い→UNCLEAR(重大化しない)。v2の「SAME優先」tie-breakは使わない(phaseで一意化)。構成X=phase照合なし(v2と同じ単一選択+SAME優先)。
4. NONE限定フォールバック(X・Y共通): 選択がNONEのとき**のみ**、Ledger側の各eventについて個別に記事側へ「対象X(subject_x)についてこの文は結果状態を述べているか」を問う(TRIAL-01方式のcall、eventごと1 call、Ledger state/quoteは渡さない)。Yではphase照合を併用(記事phaseと不一致のeventは比較しない)。個別判定の集約=1つでもREVERSED(両側quoteあり)→REVERSED、それ以外はSAME>SAME_FAMILY>NOT_MENTIONED>UNCLEARの順で代表値、全NOT_MENTIONED→NOT_MENTIONED。**選択がNONE以外のときはフォールバックしない**(unit testでassert)。フォールバック発動件数・callを記録(`fallback_used`, `fallback_calls`)。
5. 引数: `--config {X,Y}`、`--ledger-only`、`--ledger-cache`、`--article-shard i/n`、`--merge`、`--effort`、`--budget-yen`、`--dry-run`、`--testset`、`--population`。shard並列・meta hash検証はv2流用。
6. 出力record(委任_03の集計契約): v2のkeysに加え `repeats[*].{article_phase, matched_event_phase, fallback_used, fallback_calls, fallback_details:[{subject_x, phase, ledger_state, article_state, compare}]}`、`is_heldout`(testsetの`heldout: true`を転記)。summaryにfallback件数・call数・費用内訳(通常/フォールバック)。
7. unit test(unittest): phase一意照合(INTERIM↔INTERIM、FINAL/UNSPECIFIED↔FINAL/SINGLE、該当なし→UNCLEAR)、Xはphase無視、NONE以外でフォールバック不発、NONE時のみ発動かつ総当たり集約規則、blind保証(記事側promptにphase/state/quote/Ledger本文なし)、shard/merge、budget停止、v2移植分。
8. dry-run: ミニ3項目+testset(委任_02の`testset_03.json`が未完なら`../trial_02/testset_02.json`)でX/Y×`--ledger-only`→shard 3→mergeを通す。

## 事前指定Read一覧
1. `er052_open233_directional_trial_02.py`: 全文(流用元、約200行)。
2. `er052_open233_directional_trial_02_test.py`: 全文。
3. `docs/pm/RESULT_PACKET_TRIAL02_01.md`: 全文(v2のコマンド例)。

## 事前指定Grep一覧+追記位置・更新位置の手順
新規ファイルのため追記位置なし。v2のGrep `def build_article_prompt|def compare_selected|def main|add_argument` で流用箇所を特定。

## 実行コマンド全文
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-03_01.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-03_01.md_check.json`
2. `.venv\Scripts\python.exe -m unittest er052_open233_directional_trial_03_test`
3. dry-run一連(X/Y): `--dry-run --ledger-only ...`→`--dry-run --config Y --article-shard 1/3 --ledger-cache ...`(2/3,3/3)→`--merge`(出力`er052_output\open233_directional_misread_trial_03\dryrun\{X,Y}`)。

## SSOT追記文
なし。

## Git
なし。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_T03_01.md`: test件数、dry-run出力パス、本実行コマンド例(ledger-only→X/Y各shard×3→merge)、record/summary keys、T-0。最終報告8行以内。

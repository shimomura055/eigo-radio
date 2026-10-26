## 管理ID

KP-GATE-DROP-BACKFILL-PRODUCTION-01 委任_03(Family X/Y/Z×Std/Advの正式経路runtime evidence: Gate除外→補完発動/除外0→不発動/初回上限未満→不発動/救済済みは数えない/HR依頼書・フォームJSON表示/Z SRC D1・人称整合/resume再課金0/AUTO挙動、+フォーム用データ契約JSONの正式経路からの生成。有料: 見積約¥22〜30)。並行Agent: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_02(`er127_*`・TTS leaf。Family runnerのcall siteは未変更の取り決め)。あなたの所有=新run dir(各Familyの`er0XX_output/.../run_kpbf_ev_01/`、wav/raw_usage_log/STOP/lock不追跡)、`docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/{EVIDENCE_01,COST_01,FORM_DATA_01}.md`+`evidence_runs/`+`replay_results/`、`docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py`(候補doc→フォームJSON変換、API 0)、`user_test/selection_form_v3/data/`(**追加のみ**: Production候補由来の記事データを`<slug>__<level>__prod.json`として追加し`articles.json` indexへ登録。既存の猿の手Adv Trial-02データとUIは不変)、`docs/pm/delegation_log/2026-10-26_KP-GATE-DROP-BACKFILL-PRODUCTION-01_DELEGATION_03.md`(+check.json)、`docs/pm/RESULT_PACKET_KBF3.md`。Productionコード編集禁止(不具合発見時は原因・最小修正案を報告しSTOP。ただし`export_form_data_01.py`はtool)。既存HR候補(AI島`run_ai_01`等)・公開ページ・既存run dirは不変。SSOT編集権なし。pathspec付きcommit。

## 性質/到達上限Status/禁止事項

- 性質: 承認済み仕様のruntime evidence取得(PRODUCTION_WIRED判定材料)。到達上限Status=EVIDENCE_COLLECTED(判定はFable)。
- 禁止: Production/Prompt/Gate編集、既存HR候補・公開ページ改変、同一run 5分3回超起動、起動間隔150秒未満、フォームUI変更、禁止Git操作(`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`)。
- 費用: 上限¥45(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- 費用/日次: 当日既使用約JPY595/本委任見積JPY22〜30(fresh 6 level-run KP stage限定≈¥2〜3/level+replay 6件≈¥0.7〜1.0/件+R-9追加fresh≤2回)/改善見込み高/承認区分: C(300円以下、承認済みScope)。
- 修正範囲の線引き(11-8): 範囲内=evidence取得・フォームJSON変換tool・データ追加。範囲外=コード修正(報告のみ)。
- 時間見込み: 約2.5h(fresh 6 run並列≈40分[起動間隔150秒・Family別run dir]/replay 30分/変換・検証30分/文書30分)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1/D-1/G-1/F-1: 従来どおり。T-0: 委任文保存+`check_delegation_prompt.py`、結果をRESULT_PACKETへ1行(FAILでも継続)。T-2: KP stageのみでTTSなし。ただし正式CLIが`--tts-execution-mode`を要求する場合は`STANDARD`を明示し、TTS stageを起動しない(`--stage`/`--stages`でKP限定)。T-2追記4点: (1)KP stage限定起動が可能か`--help`で確認、(2)新run dirなのでcache再利用なし、(3)`--approved-budget-jpy`等があれば¥10/levelを明示、(4)TTS等の全再生成が走る構成と判明したらAPI前にSTOP。T-3: 上記定型文。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_KP-GATE-DROP-BACKFILL-PRODUCTION-01_DELEGATION_03.md` をN=689から順に試し、先頭「## 管理ID」+「KP-GATE-DROP-BACKFILL-PRODUCTION-01 委任_03」のものを採用。

## 事前指定Read一覧

- `docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/{EVIDENCE_PLAN_01,BUDGET_PLAN_01,DATA_CONTRACT_01,IMPLEMENTATION_01}.md`(自成果物、evidence方法・replay対象・R-9追加観測)
- `docs/research/KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01/EVIDENCE_01.md`(前回KP救済evidenceの起動コマンド・run dir規約・KP stage限定起動の実値=X `er019`、Y `er121`、Z `er026`の引数)
- `user_test/selection_form_v3/data/articles.json`、`data/monkeys_paw__b1b.json`(フォームJSONの形式)、`docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/DATA_MODEL_01.md`
- `er119_kp_backfill_01.py`(E計数・backfillブロックの出力項目)

## 事前指定Grep一覧+追記位置・更新位置の手順

- 各fresh run前: `py tools/stop_scope_check_01.py --managed-id KP-GATE-DROP-BACKFILL-PRODUCTION-01 --run-dir <run dir> --out docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/stop_check_<family>_<level>.json`
- 起動は`.venv\Scripts\python.exe`、`TTS_EXECUTION_MODE=STANDARD`環境変数明示。

## 実施事項

1. **fresh 6 level-run**(除外が起きやすい既知記事を使用: X=AI島[Std: 6語/canonicalization除外の実績]・英国電車[Std: 数字除外]、Y=再配達[`redelivery fee` CMU除外・`catch their interest`]、Z=猿の手[過去形除外])。各Family×Std/Advで新run dir、KP stageのみ、正式CLI。観測: `kp_candidates.json`の`backfill`ブロック(triggered/E_phrase/E_word/N/status/dropped stage別)、補完候補(`origin=backfill`・ai_rank連番・Gate全段結果)、救済済み候補が除外に数えられていないこと、call1最終attempt除外の計数(M-1)、HR依頼書の補完要約行・旗、外側retry不発火(`rescued_not_auto`候補があっても再生成されない)、Z SRC D1・人称整合(補完用dir `gloss_person_repair_backfill`)、actual model_id・Prompt sha(2-V不変)・routing。除外0のレベルでは`triggered=false`・API増0を記録。自然に補完が発動しなかったFamilyはR-9追加fresh(別記事1回、≤¥2)。
2. **replay 6件**(EVIDENCE_PLAN: AI島Std、UK Std、再配達Std、SNS Adv、猿の手Adv、melos Adv[E=0対照]): 凍結初回出力+実LLM補完。「正式関数の動作証拠(補助)」として記録。
3. **不発動の証拠**: (a)除外0(E=0)、(b)初回返答が上限未満(例: call2が4件)でE=0 → いずれも`triggered=false`。(b)はfresh/replayで自然に出た例を記録、無ければmock testの該当ケース(TBF)を引用し「runtime未観測」と明記。
4. **resume**: fresh 1 runで同引数再起動→`kp_candidates.json` sha不変・API 0(usage log差分0)。
5. **AUTO挙動**: HRなし宣言はユーザー宣言なしでは使えないため、AUTOでのn_auto<3挙動は**mock testの引用+「runtime未観測」**で記録(宣言付きrunは実行しない)。
6. **フォームJSON生成**: `tools/export_form_data_01.py`で各fresh runの`kp_candidates.json`→フォームJSON(DATA_CONTRACT: kind/origin/ai_rank/auto_eligible/flags/rescue/human_selectable、level `backfill`/`shortfall`)。猿の手Adv(Production候補、`monkeys_paw__b1b__prod.json`)を含む6件を`user_test/selection_form_v3/data/`へ追加・indexへ登録(表示名に「Production候補・補完evidence」を付す)。フォームの既存test(`form1_selection_form_v3_test_01.py`)PASS、公開URL HTTP 200。文法候補は正式Part 2候補が無ければ「候補なし・要生成」。
7. **費用**: `COST_01.md`(raw_usage_log出典、level別・補完1発動あたり実費、外側retry撤去による削減見込み)。
8. `EVIDENCE_01.md`: 受入条件§6の1〜8・11を項目別に証拠(path:行)で表にする(未観測は未観測と明記)。

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-26_KP-GATE-DROP-BACKFILL-PRODUCTION-01_DELEGATION_03.md --json-out docs\pm\delegation_log\2026-10-26_KP-GATE-DROP-BACKFILL-PRODUCTION-01_DELEGATION_03.md_check.json`
- 正式CLI(Family別、KP stage限定。実値は`--help`と前回EVIDENCE_01の引数を踏襲し全文記録)
- test: `.venv\Scripts\python.exe run_project_regression.py --pattern "form1_selection_form_v3_test_01.py"`、`--pattern "er119_kp_backfill_test_01.py"`
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

SSOT編集権なし。`RESULT_PACKET_KBF3.md`(8)にOPEN更新文案(補完=EVIDENCE_COLLECTED、Family別観測結果)、CURRENT_SPEC新節案(補完仕様+外側retry条件変更)、OPEN-526への影響(AI島は既存候補保全、補完は新run以降)。

## Git

- add対象: `docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/`配下(evidence・replay・tools・stop_check)、`user_test/selection_form_v3/data/`追加分+`articles.json`、delegation_log。pathspec付きcommit。
- commit message: `KP-GATE-DROP-BACKFILL-PRODUCTION-01 委任_03: X/Y/Z Std/Adv runtime evidence(fresh 6+replay 6、補完発動/不発動/救済非計上/resume/HR依頼書)+フォーム用Production候補JSON 6件(実費¥X)`
- trailer: `Delegation: KP-GATE-DROP-BACKFILL-PRODUCTION-01/03`
- push: `git push origin HEAD:main`。

## 報告

`docs/pm/RESULT_PACKET_KBF3.md`: (0)T-0、(1)Family×レベル別の観測表(E/N/triggered/補完候補/Gate結果/除外stage)、(2)不発動証拠、(3)救済非計上・外側retry不発火・M-1計数の証拠、(4)resume・HR依頼書・Z整合、(5)フォームJSON追加と検証、(6)費用実績・単価影響、(7)受入条件§6対応表、(8)SSOT文案、(9)判断候補(2-Vが指示を守らず件数文言が必要になった場合等)、(10)必須4行+「判定整合: 重大NG=<なし|あり>」、(11)一覧外Read、commit hash、raw URL。末尾10行要約。
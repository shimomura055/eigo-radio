## 管理ID

KP-GATE-EXCLUSION-RESCUE-DESIGN-02 委任_03(区分1=承認済み規則への準拠修正のProduction適用: ①副詞前の原形化[guard是正、−ly名詞等の誤原形化遮断]②動詞haveの役割判定[fulltext経路限定]③過去形表の補完[同形語除外]。+OPEN-530のCURRENT_SPEC文書是正。救済フロー本体(区分2)は配線しない)。並行Agent: FZ Phase 2 evidence(er063・有料)、Y男性7Voice Trial(有料)、Chunk X/Y是正+evidence(er117/er019/er121・有料)。本委任の所有=`er105_kp_fulltext_selector_01.py`、`er003_key_words_min_unit.py`、`er003_key_words_canonicalization.py`(必要最小限)、対応test(新規`er105_kp_rule_compliance_test_01.py`等)、`er123_kp_rescue_dev_01.py`(DEV側の参照のみ)、`docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-02/**`、`docs/pm/delegation_log/2026-10-26_KP-GATE-EXCLUSION-RESCUE-DESIGN-02_DELEGATION_03*`、`docs/pm/RESULT_PACKET_KPRS5.md`、`CURRENT_SPEC.md`(KP canonicalization節:1997付近のみ)。他SSOT(DECISION_LOG/OPEN_ITEMS/OPUS台帳/UDR/ACTIVE_TASK)は編集しない(文案のみ。Fableが後続のSSOT同期で転記)。

## 性質/到達上限Status/禁止事項

- 性質: 区分1のProduction適用。ユーザー原文「区分1: 承認済み仕様への準拠修正。既存ルールの意図に反する過剰除外や実装不具合を修正するもの。仕様変更を伴わず、既存の委任・予算範囲内なら自律的に解決する。ただし今回の新しい候補救済フロー全体を、正式採用前に無断でProductionへ配線しない。」Fable判断で区分1を適用(Opus Q1(b)/Q2(b)「区分1でよい、M1/M2が条件」、M1/M2はDEVで反映・敵対的85件で0誤受理)。
- 到達上限Status: 区分1=IMPLEMENTED_PENDING_EVIDENCE(runtime evidenceは次のKP生成run[AI島以外]で取得。AI島のHR候補は再生成しない)。**PRODUCTION_WIREDとは書かない。**
- 禁止: 区分2(救済フロー・慣用句閉表・A1短縮・再アンカー・A2・CMU分解・辞書guard・縮約形是正)の配線禁止/A/B/C経路(`is_fulltext=False`)の挙動変更禁止(バイト同一test)/AI島run_ai_01のHR候補の再生成・確定禁止(`status`のみ)/有料API 0/Git禁止操作(`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・`reset --hard`・`checkout -f`・`git checkout -- <file>`)。
- 修正範囲(11-8): 範囲内=①guardを承認文(CURRENT_SPEC.md:1997「先頭またはto直後の動詞」)の水準へ戻しつつP-04の目的(`heated debate`型=V+名詞を原形化しない)を維持する是正(副詞後続のみ許可、−ly名詞/動詞除外表・語幹CMU実在・LLM提案語一致・前方活用一致の検査)②`_FINITE_AUX_WORDS`の`have/has/had`を「役割判定」に置換(fulltext経路のみ。倒置・量化詞介在・限定詞+名詞+分詞・不変化分詞はaux=現行どおり除外)③過去形表の補完(他動詞原形と同形の語は除外)。範囲外=上記以外の受理面変更。
- Opus独立技術レビューGate: 条件A実施済み(DESIGN-02 Opusレビュー、M1/M2反映済み)。本委任はProduction移植のため非該当だが、DEV→Productionの移植で判定が1件でも変わればSTOPして報告。
- 時間見込み: 2〜2.5時間。費用/日次: 当日(JST 2026-10-26)既使用JPY約219+進行中/本委任JPY0/承認区分: C。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2: TTSなし。T-3: Capなし(JPY0)。

委任文保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 646 --out docs\pm\delegation_log\2026-10-26_KP-GATE-EXCLUSION-RESCUE-DESIGN-02_DELEGATION_03.md`(先頭が「## 管理ID」+「KP-GATE-EXCLUSION-RESCUE-DESIGN-02 委任_03」でなければ642〜658を順に試す)→check実行。

## ユーザー指示(原文)

`docs/pm/delegation_log/2026-10-26_KP-GATE-EXCLUSION-RESCUE-DESIGN-02_USER.md` §3④(区分1の定義、上記引用)。

## 事前指定Read一覧

1. `docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-02/DESIGN_02.md` §3-1(Production適用差分案)・§7(回帰test計画)、`OPUS_REVIEW_02.md` Q1/Q2/M1/M2/R3、`adversarial_01.json`(schema)、`monotonicity_02.json`(基準値)。
2. `er123_kp_rescue_dev_01.py`: `is_manner_adverb`・`have_role`・過去形表補完・`RulePatch`(移植元、該当関数全体)。
3. `er105_kp_fulltext_selector_01.py` :200-230, :560-700(guard・活用表・`_GUARD_DET`)、`er003_key_words_min_unit.py` :240-290(`_FINITE_AUX_WORDS`・`_WORD_TOKEN_RE`・使用箇所)、`er003_key_words_canonicalization.py` :576-632(:627のkey検査)。
4. 既存test: Glob `er105*_test_*.py`、`er003_key_words*_test_*.py`、`er119*_test_*.py`、`er109*_test_*.py`(件数・実行方法)。
5. `CURRENT_SPEC.md` :1990-2003(是正文の挿入位置)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- A/B/C不変: Grep `is_fulltext|_is_ft|allow_inflection_normalization` でfulltext限定の分岐を特定し、新ロジックはその内側にのみ置く。A/B/C経路のgolden(既存test fixtureの入出力)をバイト一致で固定。
- CURRENT_SPEC.md:1997付近へ追記(OPEN-530の文書是正): 「基本形化の例外は『先頭またはto直後の動詞』。実装上の次トークン条件(限定詞/代名詞/不変化詞/前置詞/**副詞**[2026-10-26是正]のとき原形化、V+名詞[形容詞化分詞]は原形化しない=P-04目的)。−ly名詞/動詞除外表・語幹CMU実在・LLM提案語一致・前方活用一致の検査。有限助動詞の`have/has/had`はfulltext経路で役割判定(倒置・量化詞介在・限定詞+名詞+分詞・不変化分詞はaux扱い=除外)。過去形専用表は不規則動詞を補完(他動詞原形と同形の語は除外)。A/B/C経路は不変。(KP-GATE-EXCLUSION-RESCUE-DESIGN-02 委任_03、区分1=承認済み規則への準拠修正、Opus Q1(b)/Q2(b))」をCURRENT_SPECの既存書式に合わせて追記。CURRENT_SPECはworktreeに他差分がある可能性があるため、HEAD blob+自hunk方式でcommit。
- 文案のみ(RESULT_PACKETへ): DECISION_LOG(Fable決定: 区分1適用)、OPEN-529/530/152更新、OPUS台帳OF-KPRS2-M1〜M4/R1〜R6のIMPLEMENTED遷移(M1/M2/R3)。

## 実行コマンド全文

- 変更前基準(遮断下): `$env:PYTHONPATH="netblock_harness_01"; py run_project_regression.py --pattern "er105*_test_*.py"`、同`"er003_key_words*_test_*.py"`、`"er119*_test_*.py"`、`"er109*_test_*.py"`、`"er123*_test_*.py"`(`--help`で実引数確認、`py`で動かない場合は`.venv\Scripts\python.exe`+遮断harness。前後でPASS/FAIL集合比較)。
- 移植後の同値確認: DEV(`er123` RulePatch適用)とProduction新コードで、`adversarial_01.json`(85件)+実データ315種(`monotonicity`入力)+`have_probe`72窓の判定が**完全一致**することをscriptで確認(`py docs\research\KP-GATE-EXCLUSION-RESCUE-DESIGN-02\tools\prod_vs_dev_parity_01.py --out …\parity_01.json`、socket遮断付き)。1件でも不一致ならSTOP報告。
- 新規test: `$env:PYTHONPATH="netblock_harness_01"; py -m pytest er105_kp_rule_compliance_test_01.py -q`(敵対的85件をfixture化、A/B/Cバイト同一、AI島a2の`studied separately`がvalidator PASSになること[保存済みparsed応答で机上]、`heated debate`型が原形化されないこと、`increased supply`不受理、`has spread`等がaux、`rang through→ring through`、`lay/wound/ground/bore`非追加)。
- 保全: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01`(前後不変)。
- secret grep: `git diff --cached | findstr /R /C:"sk-[A-Za-z0-9]" /C:"AIza[A-Za-z0-9_-]" /C:"BEGIN PRIVATE KEY"`。

## 成果物

Production差分(最小)、新規test、`docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-02/{PROD_APPLY_01.md(差分要約・影響範囲・A/B/C不変証拠・DEV/Prod parity・runtime evidence計画[次のKP生成runでdropped[]にRule7/FINITE_AUX由来の該当句が出ないこと、`study separately`型の受理ログ]),parity_01.json,tools/prod_vs_dev_parity_01.py}`、CURRENT_SPEC追記、`docs/pm/RESULT_PACKET_KPRS5.md`。

## SSOT追記文

CURRENT_SPECのみ本委任で編集(上記)。他は文案。

## Git(明示add対象・コミットメッセージ・trailer)

- SSOT編集権: CURRENT_SPEC.md(該当節のみ、自hunk)。他なし。
- 明示add: `er105_kp_fulltext_selector_01.py`、`er003_key_words_min_unit.py`、(必要なら)`er003_key_words_canonicalization.py`、新規test、研究dir成果物、CURRENT_SPEC.md(自hunk)、delegation_log+check.json。
- commit: `git commit --only <paths…> -m "KP-GATE-EXCLUSION-RESCUE-DESIGN-02 委任_03: 区分1(承認済み規則への準拠修正)をProduction適用=副詞前原形化の是正・動詞have役割判定(fulltext限定)・過去形表補完、敵対的85件回帰固定、A/B/C不変、CURRENT_SPEC:1997是正(API 0、IMPLEMENTED_PENDING_EVIDENCE)"`→`git push origin HEAD:main`(non-fast-forwardは`git fetch origin`→`git merge --no-edit origin/main`→再push。競合は両方残してSTOP)。

## 報告(RESULT_PACKET項目)

(0)T-0 (1)結論(区分1の適用内容、DEV/Prod parity一致、A/B/C不変、test結果) (2)差分要約(ファイル:行) (3)回帰前後PASS/FAIL集合 (4)runtime evidence計画(次のKP生成run) (5)CURRENT_SPEC追記行 (6)SSOT文案 (7)保全証拠 (8)commit/push・raw URL (9)一覧外Read (10)Fable向け懸念。最終行に要約10行以内。
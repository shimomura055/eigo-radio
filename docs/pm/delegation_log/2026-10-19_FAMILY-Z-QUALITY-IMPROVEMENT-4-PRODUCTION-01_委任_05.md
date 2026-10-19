# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01 委任_05(Opusレビュー_E逐語保存+①Key Phrase日本語意味の共通仕様(案III、Opus修正F1-1〜F1-6・F2-1反映)のProduction実装+test+実LLM Regression(少額)。メロス再処理の実走はPhase 3=別委任)。日付: 2026-10-19(JST)。

## 性質・到達上限Status・禁止事項
- 性質: 承認済み仕様①(ユーザー2026-10-19 APPROVED_FOR_PRODUCTION)の正式Production配線(X/Z共通module改修+Z runner関所+X runner記録)。有料は実LLM Regression(Production経路と同一モデル、約8〜12 item×1回、見積JPY1未満、上限JPY3)のみ。
- 到達上限Status: `ITEM1_CODE_WIRED_TESTED_REGRESSION_PASS_PENDING_PHASE3`。PRODUCTION_WIREDはFable判定(Phase 3 runtime evidence後)。
- 禁止: 特定表現の置換hardcode/案IV・V(生成点移動・canonicalization Promptへのgloss入力)/承認済み選定Prompt・canonicalization Promptの直接編集/新しい数値基準・新Gateの創設(既存validate→retry(2回)→HRの枠内に収める)/`GLOSS_ALIGNMENT_ENABLED` kill switchの既定変更/メロス成果物(run_e2e_03)の書換え/Family Xの修復経路の新設(STOPのみの現状をOPENに記録)/有料実行は実LLM Regression以外禁止/②の実装(er062 `run_support_std`・stage_support・lint)には触れない(別委任)。
- 固定ブロック: **E-1**(ITEM1_KP_JA_MEANING_DESIGN_01 §4案III・§5、OPUS_REVIEW_E R-E1/R-E2の全Fix、KGCPW承認仕様(CURRENT_SPEC 2751-2759付近)、OPEN-352)/**D-1**(不適用=承認済み仕様。kill switch `GLOSS_ALIGNMENT_ENABLED`がOFFなら新検査も無効=既存思想どおり)/**G-1**(変更ファイルのみ明示add、`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f禁止、secret_scan hits=0後commit、push=`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only; git merge --ff-only work/post-merge-01; git push origin main`、戻って`git merge --ff-only origin/main`。並行agentなし。SSOTは自分の変更行のみstaged blob)/**F-1**(実LLM Regressionの実費は`raw_usage_log`等から実測し出典付きで報告)/**T-0**(本委任文を全文そのまま`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_委任_05.md`へ保存し`check_delegation_prompt.py --file <path> --json-out <path>_check.json`実行。要約保存=FAIL逸脱)/**T-2・T-3**(報告=`C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZQI5.md`、ACTIVE_TASK.md先頭へ自分のブロックのみEdit追記)。
- 使用モデル: 実LLM RegressionはProduction経路(gloss再整合)と同一モデル(検証対象が本番経路のため。25節の「最新でない理由」として記載)。

## Fable決定(Opus_E採用。記録用)
- ①方式=案III(再整合対象の拡張+汎用制約文+決定論的人称語突合check)。Opus修正を全採用: **F1-1** 生成用対象と消費側(未評価判定)対象の関数分離(消費側に人称一般化item全件を入れない。Coffee等の健全artifact fixtureでSTOP 0件をtestで固定)/**F1-2** 決定論checkはstatusにかかわらず全itemへ(例外=`HUMAN_RESOLVED`はWARN記録のみ)/**F1-3** checkは採用値`adopt_gloss`へ適用。制約文に「不定の人称を具体的な人称で訳すことは『誤っている』に当たる」を明記。retryのuser messageに前回INVALID理由(人称語残存)を項目単位で渡す/**F1-4** 日本語人称語は境界付き照合(直前が漢字でない、直後が助詞・接尾(の/が/は/を/に/と/も/へ/たち/ら/自身/方)または末尾)。再帰は「KPのどこかにone's/oneselfがあれば自分/自身を許容」。「相手/その人/人」は検出しない。発火条件=「KPに一般形トークンあり、かつKPに具体人称語(me/him/us/them等)なし」/**F1-5** 実LLM Regression(記事非依存の合成item約8〜12、同一KPを代わり義/立場義の2文脈に置くペア含む)を受入evidenceに含める/**F1-6** CURRENT_SPECに「新validate理由+HR経路+kill switch OFF時は無効」を明記。
- メロス適用=**F2-1(a)**: `stage_kp`内、`ensure_stage(kp_<lv>)`後・`collect_unevaluated`(:1273付近)前の全経路共通位置に「人称整合関所」を置く。永続化済みartifactに不整合itemがあれば、選定・canonicalizationを保持して既存`align_glosses`でglossのみ再生成→`a2_result.json`を更新し、同処理内で`prov.set_entry`により`output_sha256`を更新+修復記録(理由・対象rank・旧/新gloss・version)→`prov.save()`。修復不成立は既存`_gloss_hr_gate`と同じHR報告→STOP経路(新STOP経路を作らない)。有料呼出は`_guard(ctx, …)`の予算guardを通す。`mark_stale_descendants("kp_a2")`は空振り(DEPENDENTS無)なので下流stale化を前提にしない。`load_level_inputs`と`--stage tts_*`単独起動はF1-1(b)でfail-closed。
- X: X runner関所は`collect_unevaluated`でSTOPのみ(修復経路なし)。OPEN_ITEMSに「X: 修復経路なし・STOPのみ(census不整合0件)」を記録(ユーザー§4)。

## 事前指定Read一覧
- Opusレビュー_E原文: subagent jsonl `C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\subagents\agent-a0d78161d93175d18.jsonl`→`docs/pm/tools/extract_delegation_from_jsonl_01.py --tool-use-name SubagentHandback --tool-input-field <field>`(委任_14で追加したオプション)で`docs/research/FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01/OPUS_REVIEW_E_01_VERBATIM.md`へ逐語保存(文字数・sha256報告。抽出不能ならSTOP報告)。
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01\ITEM1_KP_JA_MEANING_DESIGN_01.md`(全文)
- `C:\Users\tensh\eigo-radio\er003_key_words_gloss_alignment.py` L100-160(_GENERIC_TOKENS/対象選定)・L240-260(HUMAN_RESOLVED)・L360-460(指示文・validate_item_corrected)・L470-490(retry message)・L610-645(collect_unevaluated)
- `C:\Users\tensh\eigo-radio\er003_key_words_canonicalization.py` L700-760
- `C:\Users\tensh\eigo-radio\er026_family_z_fiction_production_runner_01.py` L1173-1190(`_load_gloss_hr_resume`)・L1225-1340(stage_kp・_src_gate・collect_unevaluated・load_level_inputs)
- `C:\Users\tensh\eigo-radio\er062_family_z_writer_01.py` L500-520(ensure_stage/provenance)
- `C:\Users\tensh\eigo-radio\er019_family_x_audio_production_runner_01.py` L520-590(X関所)
- 既存test: `er003_key_words_gloss_alignment*_test*.py`、`er026_family_z_fiction_production_runner_01_test.py`、`er019_family_x_fx_20261016_wiring_01_test_01.py`
- Coffee等の健全artifact(fixture用): `er019_output/coffee_prices/run_fxpw_01/**/key_phrases/*result.json`(読み取りのみ)

## 事前指定Grep一覧+追記位置・更新位置の手順
- `er003_key_words_gloss_alignment.py`: Grep `_GENERIC_TOKENS|def select_alignment_targets|def collect_unevaluated|def validate_item_corrected|HUMAN_RESOLVED`→F1-1〜F1-4を実装(新関数例: `select_generation_targets`/`select_consumer_unevaluated`、`person_reference_mismatch(kp_en, gloss_ja) -> reason|None`、制約文定数)。
- `er026_family_z_fiction_production_runner_01.py`: Grep `_src_gate\(ctx, lv, text\)|collect_unevaluated`→関所`_gloss_person_gate(ctx, lv)`を`_src_gate`直後・`collect_unevaluated`前に挿入(全経路共通)。
- `er019_family_x_audio_production_runner_01.py`: 変更は消費側関数名の差替え(STOPのみ)に限る。
- `CURRENT_SPEC.md`: Grep `KGCPW|gloss再整合|人称一般化`(2751-2759・1945付近)→①仕様文(共通module、対象拡張、決定論check、HR経路、kill switch、Z関所=修復あり/X=STOPのみ)。「2026-10-19ユーザー決定、コード配線済み、runtime evidence待ち」。
- `OPEN_ITEMS.md`: Grep `OPEN-419`→①進捗+「X修復経路なし」記録。Grep `OPEN-352`→同原因クラスの是正として参照追記。
- `DECISION_LOG.md`: 末尾に委任_05エントリ(Opus_E GO_WITH_FIXES採用、F1-1〜F2-1、Phase 3方針=新run dir全再生成(F6-1)もここに記録)。
- `docs/pm/OPUS_FINDINGS_LEDGER.md`: OF-FZQI-E-01〜(R-E1〜R-E6)を追加、Status(ADOPTED/EVIDENCED/OPEN)。
- `docs/pm/REPORT_LEDGER.md`: 末尾1行。

## 作業(順序)
A. T-0・Opus_E保存。B. 共通module実装(F1-1〜F1-4)+単体test(parametrized fixture: someone's→あなた/私/彼/君(境界: 暴君/主君は非検出)、one's→自分(許容)、tell someone off→彼を(検出)、英語側に具体人称がある表現は対象外、HUMAN_RESOLVEDはWARNのみ、adopt_glossへの適用、retry messageに理由が入る、個別フレーズ分岐なしのGrep test、Coffee実artifact fixtureで消費側STOP 0件)。C. Z関所実装(F2-1(a))+test(初回/reuse/regenerate/HR resumeで1箇所を通ること(monkeypatch)、修復時にprov output_sha256更新+修復記録、不成立→既存HR経路、`_guard`経由、`--stage tts_*`単独はfail-closed)。D. X runner消費側差替え+X test不変確認。E. 回帰: er003 gloss系・er026 runner/integration・er019 X wiring・er063系(PASS数)。F. 実LLM Regression(`docs/research/FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01/item1_llm_regression_05.py`、合成item 8〜12、Production経路の`align_glosses`を直接呼ぶ、上限JPY3、結果json+表: 期待(不定人称保持・語義選択)/実出力/判定)。期待未達が出た場合は制約文の調整を1回まで(Prompt創作ではなく制約文の明確化の範囲)→再実行、それでも未達ならSTOP報告。G. メロス該当item(run_e2e_03 a2 rank2 `in someone's place`「あなたの代わりに」)に対し決定論checkがオフラインで不整合を検出することを示す(成果物は書き換えない)。H. SSOT→commit→push。

## 実行コマンド全文(作業dir=`C:\Users\tensh\eigo-radio`)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_委任_05.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_委任_05.md_check.json`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\extract_delegation_from_jsonl_01.py --jsonl "C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\subagents\agent-a0d78161d93175d18.jsonl" --role assistant --index -1 --tool-use-name SubagentHandback --tool-input-field <実装のfield名> --out C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01\OPUS_REVIEW_E_01_VERBATIM.md`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I -m pytest <er003 gloss alignment test file> C:\Users\tensh\eigo-radio\er026_family_z_fiction_production_runner_01_test.py C:\Users\tensh\eigo-radio\er026_family_z_e2e_integration_test_01.py C:\Users\tensh\eigo-radio\er019_family_x_fx_20261016_wiring_01_test_01.py C:\Users\tensh\eigo-radio\er063_family_z_audio_01_test_01.py -q`
- 実LLM Regression: `$env:TTS_EXECUTION_MODE="STANDARD"; C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01\item1_llm_regression_05.py --budget-jpy 3 --out C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01\item1_llm_regression_05_result.json`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\secret_scan_01.py --staged`(実在script名に置換)

## SSOT追記文(要点)
- CURRENT_SPEC(KGCPW節/KP日本語意味): 「① 人称・指示対象整合(2026-10-19): 再整合対象に人称一般化itemを追加。制約=不定の人称は日本語でも不定のまま、文脈は語義選択にのみ使用、逐語強制なし。決定論的人称語突合(境界付き、再帰許容)を採用値へ適用し、不整合は既存validate→retry(理由付き)→HR。kill switch OFF時は無効。Z: stage_kp関所で選定保持のままgloss修復+provenance更新/X: STOPのみ(修復経路なし、OPEN記録)。X/Z/Y共通module。コード配線済み(commit)、runtime evidence待ち」。
- DECISION_LOG: 上記+Opus_E採用+Phase 3方針(新run dir・音声全再生成・上限JPY80 Fable設定)。

## Git(明示add対象・コミットメッセージ・trailer)
- commit: delegation_log 委任_05+_check.json、OPUS_REVIEW_E_01_VERBATIM.md、`er003_key_words_gloss_alignment.py`、`er026_family_z_fiction_production_runner_01.py`、`er019_family_x_audio_production_runner_01.py`(差替え分)、test新規/更新、`item1_llm_regression_05.py`+result json、CURRENT_SPEC.md、OPEN_ITEMS.md、DECISION_LOG.md、OPUS_FINDINGS_LEDGER.md、REPORT_LEDGER.md。msg: `FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01 委任_05: Opus条件Aレビュー_E(GO_WITH_FIXES)逐語保存+①KP日本語意味の人称・指示対象整合をX/Z共通moduleへ配線(再整合対象拡張・汎用制約文・境界付き決定論check・理由付きretry・HR経路、生成用/消費側の対象分離)+Z stage_kp修復関所(選定保持・provenance更新)+X=STOPのみ記録+test+実LLM Regression(JPY x)`

## 報告(RESULT_PACKET項目: `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZQI5.md`)
4行: (1)整合(Opus Fix F1-1〜F1-6・F2-1の反映箇所:行)(2)Production到達経路(関所の位置と全経路、消費側fail-closed、kill switch、X差替え)(3)成果物とcommit sha、test PASS数、実LLM Regression結果表(item/期待/実出力/判定、費用実測)、メロス該当itemのオフライン検出結果、Opus_E原文の文字数・sha256(4)撤去/残置。`判定整合:`・`判断候補:`・T-0 check・自己チェック(hardcodeなし/承認済みPrompt不変/新Gateなし/実費≤3/run_e2e_03不変/②未着手)。

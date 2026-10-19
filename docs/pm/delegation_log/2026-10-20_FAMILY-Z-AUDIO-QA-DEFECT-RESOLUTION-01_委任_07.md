# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_07(Fable照合結果の確定反映: 録音2のHuman Review承認を正規APIで記録→run_e2e_04凍結→新run `run_e2e_05` でStd/Adv全TTSを正式Production経路で再生成→gate/assemble/pages/page_verify→runtime evidence記録→SSOT統合→T-0逐語保存の是正)。2026-10-20。
並行タスク衝突確認: 並行委任なし(委任_05/_06は完了・commit済み: 1b545f1ff・cb50b7127・1844ea4e0)。本委任はSSOT編集権**あり**(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/USER_DECISION_REGISTER_01.md`/`docs/pm/OPUS_FINDINGS_LEDGER.md`。Grep→該当行のみ編集、全文Read禁止)。

## Fableの照合結果と決定(本委任の前提。Sonnetは再判断しない)
- ①(委任_05 `ITEM1_ROOT_CAUSE_02_SPEC_RECONCILIATION_01.md`): 11-8不具合0件(仕様どおり10・承認時に意図的対象外1[R8]・空白1[R9])。承認済み機構(Tier3/M1/Case A/PhraseList/統一judge)は設計どおり動作。配線漏れ0。**新たな仕様承認は不要**=ユーザー原文§5末尾のSTOP条件(「①の解決に新たな仕様承認が必要となった場合」)に**該当しない**→§5の全TTS再生成へ進む(Fable決定)。A/A'/P2はREJECTEDのまま、実装しない。
- ②(委任_06 `ITEMS23_WIRING_ASSURANCE_01.md`): 旧条件はコードに存在したことがなく、現行経路参照0、flag非依存、test PASS、SSOT一致、run_e2e_04のlive LR発火(2026-10-19 11:57/12:14、発火条件ロジックは修正前後で同一)=**Fable判定: PRODUCTION_WIRED**。文書表記2点(OPEN_ITEMS:786のOPEN-283旧Status・旧文残置)は本委任で是正。
- ③: コード配線済み(呼出元 n3_tts:219・er019:254、未配線対象なし)+offline正式経路PASS(NORMALIZED_MATCH)。**修正後コードでのlive発火evidence未取得のためFableはまだPRODUCTION_WIREDと判定しない**。run_e2e_05でLRが自然発火し`post_slowdown_expected_text_source=local_rewrite_text`+減速後判定が観測されれば、その事実をもってFableが最終報告で判定する。発火しなければ「配線済み・live未観測」のまま記録(追加の有料検証はしない)。
- 録音2 Lock解除(ユーザー承認済み): 正規API `record_human_approval`(run_e2e_04 a2 part3_c1、承認キー=元原稿)で**承認記録を残す**(#116の正式クローズ)。`approve_regenerate`は使わない。review_lock_state.json sha `6720ce80…3e19`は承認後も不変が正常。
- 判断候補(a) provenance `audio_text_deviations`(旧Melos→He 3件)の新runでのリセット: **承認**(データのみ、判定・生成に不使用、seed sha照合に影響なし)。旧3件はrun_e2e_05のcopy記録jsonへ退避。run_e2e_04側は不変。
- 判断候補(b) 新runでLRが再発火して`He drank`になった場合: **承認済み仕様(②基本フロー)どおりに進める**(受理/拒否を独自に再判断しない、`LR_REWRITTEN`警告+試聴リスト運用)。発火事実・経路・③のlive evidenceを記録し、Fableがユーザーへ報告する。STOP理由にはしない。
- HR Lockが新runで再発した場合: 迂回せずrc≠0でSTOP、`--only-clips`等の追加有料起動はせずFableへ報告(26節)。
- 費用: 当日(2026-10-20 JST)既使用JPY0.0(委任_05 `daily_dev_cost_01.py --date 2026-10-20`採用値、run dir外・Claude Code自体は未集計)。本委任見積JPY40〜60(出典: `run_e2e_04/audit/cost_by_stage_04.json` TTS系45.83)。承認区分C(ユーザー明示指示§5・案件300円以下・日次1,000円以内)。

## 性質/到達上限Status/禁止事項
- 性質: Production正式経路でのMelos記事 Std/Adv全TTS再生成(有料)+承認記録+SSOT統合。
- 到達上限Status: `MELOS_REGENERATED_ASSEMBLED_PAGES_UPDATED_PENDING_FABLE`(全stage完了時)/`MELOS_REGEN_STOPPED_AT_<stage>_PENDING_FABLE`(rc≠0時)。PRODUCTION_WIRED・完成判定はFable。
- 禁止: (1)P1/P2/A/A'/個別例外の実装、判定閾値・Prompt・Validator・Gateの変更。(2)runnerの再起動(1回起動のみ。rc≠0でも再起動しない。26節)。(3)`approve_regenerate`の使用、`review_lock_state.json`の直接編集、`er026_output/family_z_production_e2e_01/STOP_ALL`の操作。(4)`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f。(5)wav等の大容量バイナリのcommit(run_e2e_04の前例: 179 files・wav無し、に倣う)。(6)Batch TTS(7-2例外非該当)。(7)ユーザー承認済みの録音2を判断待ちとして再提示する文面。
- 修正範囲の線引き(11-8): 本委任に不具合修正は含まれない。実走中に承認済み仕様文と実装の乖離(配線不備)を発見した場合は、範囲内なら原因・証拠・最小修正案をRESULT_PACKETへ記し、runを止めずに記録(再起動不可のため修正は次委任)。
- Opus独立技術レビューGate(11-3): 非該当(新構造なし・承認済み仕様どおりの実走・SSOT統合)。
- T-3: 上限¥80(Guardrail、runner `--approved-budget-jpy 80`)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- 時間見込み: 全体2.5〜3.5h(T-0是正15分/承認記録+STOP設置+copy 20分/dry-run 10分/real run 45〜60分[run_e2e_04実績44.7分、cooldown含む]/evidence集計30分/pages確認10分/SSOT 30分/報告15分)。並列化: real run待機中にSSOT文案作成・T-0是正・runtime evidence集計scriptの準備を先行する。直列化理由: gate/assemble/pagesはrunner内で順序依存。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。**T-0は「受領した委任文の逐語保存」であり要旨保存はFAIL扱い。本委任文は本メッセージ全文を一字一句そのまま保存すること。**
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。T-2追記(7-5)4点: (1)差分再生成は`--only-clips`で可能だがユーザー§5の明示指示による**意図的な全再生成**(REGEN_PLAN_01 T-2欄)、(2)run内再利用は新runに`tts_generation_results.json`が無く0・Master Audio StoreはZ経路で不呼出(同欄)、(3)`--approved-budget-jpy 80`明示、(4)「想定外の全再生成」に該当しない。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`): 定型文は上記「性質」欄に記載済み。

## ユーザー指示(原文)
逐語保存済み: `docs/pm/delegation_log/2026-10-20_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_ROOT-CAUSE-WIRING-CLOSEOUT_USER.md`(6785文字、sha256 `A8E240AFC090FA2E608C68FB02110530427969F88E97403D00F54F184EE3375E`)。本委任が直接対応する§は次の逐語:
> 4. 録音2のHuman Review Lock解除は承認済み。
> 5. ①の問題解決後、Family Zの該当記事についてAdvancedを含む全TTSを再生成する。Advancedの「He drank」は元の「Melos」を含む原稿に戻す。
> ## 5. 音声再生成・Human Review
> 録音2のHuman Review Lock解除はユーザー承認済み。まず①の問題を解決し、承認済み発音判定が正しく機能していることを確認する。その後、Family Zの該当Melos記事について、**Standard／Advancedの全TTSを正式Production経路で再生成する。**
> - Advancedの「He drank」は、元の「Melos」を含む原稿へ戻す。
> - 原稿の意味・構成・その他の承認済み品質仕様は維持する。
> - 必須の音声QA・再試行・Rewrite・減速後再検証・Assembly Gateを通す。
> - 完成音声と試聴ページを更新する。
> - 実際に発動した判定経路・警告・Human Review対象を記録する。
> ユーザー承認済みの録音2を、新たな判断待ちとして再提示しないこと。ただし、再生成した新音声は既存の品質Gateに従って独立に検証する。①の解決に新たな仕様承認が必要となった場合は、その境界でSTOPし、未承認仕様のまま再生成を強行しない。
> ## 6. (抜粋) FableはClaudeの「完了」報告をそのまま採用せず、実装・正式経路・runtime evidence・SSOT・Gitを独立照合すること。
> ## 7. (抜粋) 4. **Standard／Advancedの音声再生成結果**：全SectionのQA、Assembly、試聴ページ。 6. **QCD・SSOT・Git**：実費、量産単価への影響、commit/push、残課題。

## KPI provenance欄
全clipのQA結果=`production_formal_path`(fresh、run_e2e_05初回Production経路)。writer/plan/support/kp=`reuse`(run_e2e_04からcopy、原稿sha不変を確認)。E2E自己確認: fresh Production初回pathを含むE2E値か=**Yes**(tts以降)。

## Opus台帳更新
`docs/pm/OPUS_FINDINGS_LEDGER.md`: Opus_G(`OPUS_REVIEW_G_01_VERBATIM.md:20`)の「`Melo drank`のbenign単複PASSは約26文字」は実測で誤り(トークン数50以上の文のみ0.98到達、`validation.py:1201`既定値、委任_05 `item1_spec_reconciliation_verify_02_result.json`)。Opus_G関連OF行(Grep `Opus_G|OF-178`)の末尾に「訂正(2026-10-20 委任_05実測)」を1文追記。Opus_H条件(①〜⑥)は委任_03で充足済み、状態変更なし。

## 作業手順(順序厳守。有料起動は手順5の1回のみ)
1. **T-0是正+本委任保存**: (a)本委任文全文を`docs/pm/delegation_log/2026-10-20_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_委任_07.md`へ逐語保存しcheck実行。(b)委任_05/_06の保存版は要旨版でFAIL扱いのため、session transcriptから逐語を復元して**上書き**する: `.venv\Scripts\python.exe docs\pm\tools\extract_delegation_from_jsonl_01.py --help`で引数を確認後、`--jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index <N>`(Nは0から順に試し、本文先頭が`# 委任文(Fable→sonnet-worker)`かつ管理ID行に`委任_05`/`委任_06`を含むものを採用。`--index`の意味[0=最初]は委任_03で確認済み)→`docs/pm/delegation_log/2026-10-20_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_委任_05.md`/`..._委任_06.md`へ上書き→各`_check.json`再生成→文字数・sha256・check結果をRESULT_PACKETへ。復元できなければ理由を記し、要旨版に`<!-- 要旨版(逐語復元不可) -->`を先頭に付ける。
2. **録音2承認記録(API 0)**: `er003_v1_n3_01_assemble.record_human_approval(out_dir="C:/Users/tensh/eigo-radio/er026_output/family_z_production_e2e_01/melos/run_e2e_04/a2", segment_key="full_story_part3_c1", canonical_text=<run_e2e_04/a2/audit/tts_generation_results.json の segments.full_story_part3_c1.canonical_text、sha256 b6d43773…と一致確認>, approved_by="user(2026-10-20 Human Review承認: 録音2=attempt2 'Melos drank'を自然と試聴確認、原文=delegation_log/2026-10-20_..._ROOT-CAUSE-WIRING-CLOSEOUT_USER.md sha A8E240AF…; Fable記録 委任_07)")`。関数シグネチャは`er003_v1_n3_01_assemble.py:96`付近で確認し、引数名が異なれば実装に合わせる。実行前後で`review_lock_state.json`のsha(`6720ce80b7eedba9789dc190a431b030e20486b298a451479129e4d017fb3e19`)不変、`a2/audit/human_approved_segments.json`への追記を確認。録音2のwav実体パス(attempt2)をRESULT_PACKETへ記録(run_e2e_04は以後凍結)。
3. **run_e2e_04凍結**: `er026_output/family_z_production_e2e_01/melos/run_e2e_04/STOP`を作成(JSON: `{"reason":"SUPERSEDED_BY_run_e2e_05 (Fable 2026-10-20, FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_07)","created_at":"<ISO JST>","note":"RUN_CLOSEDではない。録音2(attempt2)はHUMAN_APPROVED記録済み。--mode real禁止。正規解除は --clear-stop --reason のみ(Fable判断)"}`、前例`run_e2e_03/STOP`の書式に合わせる)。
4. **新run作成**: dry-runでALLOW 66/DENY 306を再確認後、`C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -c "import er063_family_z_audio_01 as a; r=a.copy_reusable_run_assets('er026_output/family_z_production_e2e_01/melos/run_e2e_04','er026_output/family_z_production_e2e_01/melos/run_e2e_05',dry_run=False); print(r['copied'],r['denied'])"`。copy計画を`run_e2e_05/run_e2e_05_copy_plan_07.json`へ保存。`run_e2e_05/writer/provenance.json`の`audio_text_deviations`(3件)を`run_e2e_05/audit/provenance_audio_text_deviations_inherited_from_run_e2e_04.json`へ退避してから`[]`にリセット(provenance内の他キー・sha値は不変、編集前後のsha256を記録)。`segment_plan_b1b.json`/`segment_plan_a2.json`/`writer/*`のsha256がrun_e2e_04と一致することを確認(`He drank`を含まないことをGrep)。`stop_scope_check_01.py --managed-id FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 --run-dir C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_05 --out C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_05\stop_scope_check_fzaq7.json`→rc=0必須(rc=3なら中止・報告)。`er026_output/family_z_production_e2e_01/STOP_ALL`が存在しないことを確認(存在すれば起動せず報告)。
5. **dry-run→real(1回のみ)**: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er026_family_z_fiction_production_runner_01.py --run run_e2e_05 --mode dry-run --stage all`(JPY0、preflight確認)→ 問題なければ `$env:TTS_EXECUTION_MODE='STANDARD'; C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er026_family_z_fiction_production_runner_01.py --run run_e2e_05 --mode real --stage all --approved-budget-jpy 80 --tts-execution-mode STANDARD`(backgroundで起動しconsoleを`run_e2e_05/run_07_console.log`へ、開始・終了時刻JSTを記録。**rc≠0でも再起動しない**)。待機中に手順7のSSOT文案とevidence集計を先行準備する。
6. **runtime evidence記録**(`docs/research/FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/MELOS_REGEN_RUN_E2E_05_RECORD_01.md`、事実のみ): REGEN_PLAN_01 (vii)の全項目=各clipの`asr_judgement`(state/reason_code/Secondary使用)、M1/Tier3/Eq Layer発動、`pass_with_warning_listening_list.json`件数と内容、**LR発火の有無**(`er011_output/local_rewrite_recovery/run_e2e_05/`、`attempt_history.jsonl` theme_id=run_e2e_05)、発火時は`post_slowdown_expected_text_source`・`post_slowdown_classification`・`A2_SLOWDOWN_REVERIFY`行・`audio_text_deviation`(=③live evidence)、HR Lock/HR queue新規行(`lock_canonical_text`/`expected_text_source`)、**Std/Adv part3_c1の最終採用テキストと転写(Melosのまま/He等に書換え)**、stage別費用(`audit/cost_by_stage_05.json`相当を作成、`cost_log.jsonl`から集計、TTS/ASR azure/ASR openai/LLM別)、壁時計時間・cooldown、原稿sha一致、copy記録。gate/assemble/pages/page_verify結果(`page_verify_local.json`の`user_page_standard_check`)。
7. **公開確認**: `user_test/family_z_melos_02/`の更新ファイルをcommit/push後、`curl.exe -I https://shimomura055.github.io/eigo-radio/user_test/family_z_melos_02/`で200確認(Pages遅延時は最大10分・3回まで再確認、それでも未反映なら時刻付きで記録)。
8. **SSOT統合**(各ファイルはGrepで該当行のみ編集): 
   - `DECISION_LOG.md`末尾: 「2026-10-20 ユーザー決定(FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01、原文=`docs/pm/delegation_log/2026-10-20_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_ROOT-CAUSE-WIRING-CLOSEOUT_USER.md`、6785文字、sha256 A8E240AF…): (1)A/A' REJECTED(再提案は原因・既存仕様との関係・他案比較・QCDを揃えた場合のみ、名称変更採用禁止) (2)②③の正式Production有効性確認 (3)録音2 Lock解除承認 (4)①解決後にStd/Adv全TTS再生成・Advancedは元のMelos原稿 (5)大原則対策は維持・追加制度なし。Fable決定(2026-10-20): ①=11-8不具合0件・承認済み機構は設計どおり動作・新仕様承認不要(委任_05 `ITEM1_ROOT_CAUSE_02_SPEC_RECONCILIATION_01.md`)→§5再生成へ。②=PRODUCTION_WIRED(Fable判定、根拠=`ITEMS23_WIRING_ASSURANCE_01.md`)。③=配線済み・live evidence<取得済み[run_e2e_05で観測]/未観測>。録音2=`record_human_approval`で記録、run_e2e_04はSUPERSEDED(STOP設置)。再生成結果=<rc・全clip OK数・LR発火有無・HR有無・実費JPY>」。
   - `OPEN_ITEMS.md`: OPEN-422(統合)Status更新(上記要点+run_e2e_05結果)。OPEN-283: L786付近の旧Status`ITEMS23_FIXED_TESTED_PENDING_OPUS_AND_FABLE`と旧文「ユーザー判断待ち・未実装」を現状(修正済み・Opus_H条件充足・live evidence<有/無>)へ是正。OPEN-330: 「2026-10-20 ユーザー: A/A' REJECTED。現行挙動は維持(独断の厳格化禁止)。実測補足: benign単複によるMelo PASSはトークン50以上の文のみ(0.98既定値`validation.py:1201`)、run_e2e_04のMelos含有6文中1文のみ非対称。Status=判断保留(再提案は条件付き)」。OPEN-318/OPEN-371は変更なし(触れない)。
   - `CURRENT_SPEC.md` L2136付近(classify/benign単複の文)に事実注記1文のみ: 「【注記 2026-10-20】`HIGH_SIMILARITY_SAFE`の一致率閾値0.98はコード既定値(`er006_preprod_hardening_01_validation.py:1201`)であり本文に未記載だった。挙動変更なし(委任_05実測)。」L2818は変更しない(③live evidenceが取得できた場合のみ「live発火evidence=run_e2e_05 <clip>(2026-10-20)」を末尾に追記)。
   - `docs/pm/USER_DECISION_REGISTER_01.md`: #116→判断済み(2026-10-20 録音2承認・Lock解除承認、`record_human_approval`記録、run_e2e_04 SUPERSEDED、新run run_e2e_05で独立判定)。#120→判断済み(A/A' REJECTED、再提案条件)。#119→進捗追記(①不具合0・②WIRED・③<状態>・再生成結果)。#23(Melos試聴)→「run_e2e_05で更新、試聴待ち」追記。新規番号は増やさない。
   - `docs/pm/REPORT_LEDGER.md`: 本管理IDの行に委任_05〜_07の報告状態を追記。
   - `docs/pm/OPUS_FINDINGS_LEDGER.md`: 上記「Opus台帳更新」。
9. **ACTIVE_TASK.md**先頭へ本委任ヘッダ(管理ID/Status/UDR-blocking=なし[#116・#120判断済み]/禁止維持/報告=RESULT_PACKET_FZAQ7.md)を追記。

## 事前指定Read一覧
- `docs/research/FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/REGEN_PLAN_01.md`:1-101(実行計画の正本。B-1の実行形を含む)
- `docs/research/FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/ITEMS23_WIRING_ASSURANCE_01.md`: 結論欄(Grep `不足|結論`)
- `docs/pm/RESULT_PACKET_FZAQ5.md`:(11)SSOT追記文案の節(Grep `SSOT|追記文`)と(2)§6結論
- `docs/pm/RESULT_PACKET_FZAQ6.md`: (7)(8)の節(Grep `record_human_approval|再生成計画`)
- `er003_v1_n3_01_assemble.py`:90-130(`record_human_approval`シグネチャ)
- `er026_output/family_z_production_e2e_01/melos/run_e2e_03/STOP`(書式)
- `docs/research/FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01/PHASE3_RUN_E2E_04_RECORD_01.md`:1-30(記録書式の前例)
- `docs/pm/tools/extract_delegation_from_jsonl_01.py`:1-60(引数)
- `tools/stop_scope_check_01.py`:1-40(引数)

## 事前指定Grep一覧+追記位置・更新位置の手順
- `OPEN_ITEMS.md`: Grep `^- OPEN-(422|283|330)`→各行末尾へStatus更新文を追記(本文置換は旧Status文字列のみ)。
- `CURRENT_SPEC.md`: Grep `HIGH_SIMILARITY_SAFE` (L2136付近)→該当行末尾に注記1文。Grep `Local Rewrite(英語のみ・5 role)` (L2818)→③live evidence取得時のみ末尾追記。
- `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `^- #(116|119|120|23)\(`→各行末尾に追記(区分見出し[判断済み/UDR]の移動が必要なら索引行も更新)。
- `docs/pm/REPORT_LEDGER.md`: Grep `FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01`→該当行更新。
- `docs/pm/OPUS_FINDINGS_LEDGER.md`: Grep `Opus_G|OF-178`→該当行末尾に訂正1文。
- `DECISION_LOG.md`: 末尾(`tail`相当でGrep `^## 2026-10-19`の最後のエントリの後)へ新エントリ追加。索引(先頭の直近25件リスト)があれば1行追加。

## 実行コマンド全文
- T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-20_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_委任_07.md --json-out docs\pm\delegation_log\2026-10-20_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_委任_07.md_check.json`
- 逐語復元: `.venv\Scripts\python.exe docs\pm\tools\extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 0 --out docs\pm\delegation_log\_extract_try_0.md`(`--out`等の実引数名はhelpで確認、indexを0,1,2…と増やして照合。一時ファイルは採用後に削除)
- Lock sha: `powershell -Command "Get-FileHash -Algorithm SHA256 er026_output\family_z_production_e2e_01\melos\run_e2e_04\a2\audit\review_lock_state.json | Select-Object -ExpandProperty Hash"`
- 承認記録: `.venv\Scripts\python.exe -c "import er003_v1_n3_01_assemble as m, json; r=json.load(open('er026_output/family_z_production_e2e_01/melos/run_e2e_04/a2/audit/tts_generation_results.json',encoding='utf-8')); t=r['segments']['full_story_part3_c1']['canonical_text']; print(m.record_human_approval('C:/Users/tensh/eigo-radio/er026_output/family_z_production_e2e_01/melos/run_e2e_04/a2','full_story_part3_c1',t,'user(2026-10-20 Human Review approve: recording2=attempt2 Melos drank; Fable 委任_07)'))"`(シグネチャ確認後に引数順を合わせる)
- copy / stop_scope_check / dry-run / real: 上記手順4・5の全文。
- 費用集計: `.venv\Scripts\python.exe docs\pm\tools\daily_dev_cost_01.py --date 2026-10-20`(完了後)。
- Pages: `curl.exe -I https://shimomura055.github.io/eigo-radio/user_test/family_z_melos_02/`
- secret scan: `.venv\Scripts\python.exe tools\secret_scan_01.py --staged`
- Git: `git status --porcelain`→明示add→commit→push(直近commit cb50b7127/1844ea4e0と同じ手順、`git log --oneline -3 origin/main`で到達確認)。

## SSOT追記文
上記手順8の各文案を実測値で埋めて使用する(`<…>`は必ず実値に置換、未取得は「未観測」と明記)。

## Git(明示add対象・コミットメッセージ・trailer)
- commit A(手順1〜4、API 0): delegation_log 3件+check 3件、`run_e2e_04/STOP`、`run_e2e_04/a2/audit/human_approved_segments.json`、`run_e2e_05/`の生成済みjson/計画(wav無し)。msg: `FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_07: 録音2 Human Review承認記録(record_human_approval)+run_e2e_04凍結(SUPERSEDED)+run_e2e_05作成(ALLOW66/DENY306、provenance deviations退避)+T-0逐語是正`
- commit B(手順5〜7): `run_e2e_05/`配下のjson/log/md(wav・mp3等バイナリ除外。前例run_e2e_04=179 files)、`user_test/family_z_melos_02/`更新ファイル(音声が含まれる場合は前例の公開方式に従う: run_e2e_04/03のpages commitで音声がcommit対象だったかを`git log --stat -1 -- user_test/family_z_melos_02`で確認し同じ扱い)、`MELOS_REGEN_RUN_E2E_05_RECORD_01.md`。msg: `FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_07: Melos Std/Adv全TTS再生成 run_e2e_05(rc=<n>、clip OK <x>/<y>、LR発火<有/無>、HR <0/n>、実費JPY<v>/80)+試聴ページ更新`
- commit C(手順8): SSOT 6ファイル。msg: `FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_07: SSOT(DECISION_LOG[2026-10-20ユーザー決定+Fable決定]/OPEN-422・283・330/CURRENT_SPEC注記/REGISTER #116・#119・#120・#23/REPORT_LEDGER/OPUS_LEDGER訂正)`
- trailer: `Delegation: FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/委任_07`
- SSOT編集権: あり(上記6ファイル)。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_FZAQ7.md`(新規): (1)T-0(本委任+委任_05/_06復元の文字数・sha・check結果) (2)承認記録の結果(human_approved_segments.json追記内容、Lock sha前後、録音2 wavパス) (3)run_e2e_04 STOP設置 (4)run_e2e_05作成(copy件数、provenance退避・リセット前後sha、原稿sha一致、stop_scope rc) (5)dry-run結果 (6)real run: 開始/終了JST・rc・stage到達・clip OK数(b1b/a2別)・NG/retry/cooldown・**LR発火の有無と詳細**・**Std/Adv part3_c1の最終テキストと転写**・HR Lock/queue・PASS_WITH_WARNING件数・`post_slowdown_expected_text_source`観測(③live evidence) (7)gate/assemble/pages/page_verify結果・Pages HTTP状態・試聴URL (8)費用: stage別実費・種別別・合計/80、当日累計(`daily_dev_cost_01.py`)、量産単価への含意(Melos記事1セットのTTS+ASR原価、PM_GOVERNANCE 15-8形式で1行) (9)SSOT差分(ファイル:行) (10)Git(commit A/B/C hash・push到達・secret scan hits) (11)判断候補(あれば。ラベルは付けない) (12)失敗終了時の最終成果物(rc≠0の場合)と受入記録5項目 (13)一覧外Read理由。判定整合行を末尾に1行。
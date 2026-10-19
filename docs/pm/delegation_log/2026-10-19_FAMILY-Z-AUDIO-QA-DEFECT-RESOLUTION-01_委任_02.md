# 委任文(Fable→sonnet-worker)

## 委任文冒頭注記
ユーザー指示原文(2026-10-19「Family Z 音声品質不具合の解決・大原則不遵守の原因分析と再発防止」)の逐語保存は並行agent(委任_01)が`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_USER.md`へ行う。本委任は同ファイルを**読む**(存在しなければ60秒間隔で最大10回待ち、無ければ本委任文末尾の「ユーザー指示原文抜粋」で作業し、その旨報告)。本委任の対象は不具合②③のみ。

## 管理ID
FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_02(不具合②「Rewrite発動条件『両ASR合意』の削除(ユーザーAPPROVED_FOR_PRODUCTION)の原因調査+Production反映」と不具合③「Rewrite後の音声検査が旧原稿と照合される不整合(OPEN-283)」の原因特定・修正・Regression・正式経路検証。コード変更あり、原則JPY0(③の正式経路検証で既存wavに対する検証再実行のみ上限JPY10)。新規TTS禁止、HR Lock不変)。日付: 2026-10-19(JST)。

## 性質・到達上限Status・禁止事項
- 性質: 調査+Production修正+Regression+offline正式経路検証。
- 到達上限Status: `ITEMS23_FIXED_TESTED_PENDING_OPUS_AND_FABLE`(PRODUCTION_WIRED判定はFable。③はCross-Family共通経路のためOpusレビュー[条件C]をFableが実施してからFable判定)。
- 禁止: HR Lock・`review_lock_state.json`の変更/新規TTS/音韻同等性判定ロジック(er006 M1/er011 F1/er021 Tier3/er078)の変更(①=委任_01担当)/未承認のRewrite許容条件・品質基準の追加/「両ASR合意」削除に乗じて他の発動条件(最大2回のTTS再生成後にのみRewrite、7 Gate、PASS_WITH_WARNING条件等)を緩めること/er019・run_mey_01への接触/`er026_output/.../run_e2e_04`配下の成果物変更(読取・copyして別dirでの検証は可)。
- 固定ブロック: **E-1**(CURRENT_SPEC L2801-2816[統一ASR/LR発火条件⑤]、LR設計文書 DESIGN_01 §4-7⑤・変更表#17、ADDENDUM §5、IMPLEMENTATION_02b〜13、CLOSEOUT_PLAN_07、OF-AUW-07、OPEN-283、`er020_tts_retry_local_rewrite_01.py`:708-775、`er003_v1_crosslevel_audio_02_common.py`:386、`er003_v1_n3_01_tts_generate.py`:121,182,281-282をGrep/Readし、導入経緯→実装→現状の対応表を作る)/**D-1**(②=仕様文からの条件削除+コード側の不要参照・検査の整理[実装が元々無いなら「参照整理のみ」]。③=減速後再検証・retry・fallback・resume・最終検証が「正式に許可されたRewrite後の実送信文」を正解とするよう、原稿参照の一元化で修正。新しいGate/閾値は作らない)/**G-1**(変更ファイルのみ明示add、`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f禁止、secret_scan hits=0後commit、push=`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only; git merge --ff-only work/post-merge-01; git push origin main`、戻って`git merge --ff-only origin/main`。**並行agentあり(委任_01: er006/er011/er021/er078とdocs/research/FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/ITEM1_*を担当)**: 共有SSOT(OPEN_ITEMS/DECISION_LOG/USER_DECISION_REGISTER/REPORT_LEDGER/CURRENT_SPEC)は「編集直前に`git status --porcelain <file>`でclean確認(dirtyなら60秒間隔最大10回待つ)→再読→自分の行のみ編集→直ちにadd→commit」、`.git/index.lock`待ち再試行、non-ffは`pull --ff-only`後再試行、conflictはSTOP。ACTIVE_TASKは先頭に自ブロック追記(gitignore))/**F-1**(原則JPY0。offline検証は既存転写・既存wavの再判定を優先しAPI 0。どうしても必要な既存wavへのASR再実行は上限JPY10、実費出典付き)/**T-0**(本委任文を全文そのまま`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_委任_02.md`へ保存し`check_delegation_prompt.py`実行。要約保存=FAIL逸脱)/**T-2・T-3**(報告=`C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZAQ2.md`)。

## Fable指示(②の要件)
1. **導入経緯と不一致原因**: 「両ASRが同じ箇所の誤読に合意」条件がいつ・どの文書で仕様化され(DESIGN_01 §4-7⑤、変更表#17、ADDENDUM §5の閾値未定義)、実装文書(IMPLEMENTATION_02b〜13、CLOSEOUT_PLAN_07)で実装記録が無い理由(未実装のまま配線完了とされた/閾値未定義で実装保留/別条件で代替したと誤認 等)をcommit履歴・REPORT・DECISION_LOGから証拠付きで特定。OF-AUW-07のOpus指摘がどう処理されたか(OPEN_ITEMS登録の有無・その後の扱い)も記録。CURRENT_SPECが「配線済み」と記す範囲と実装の差を表にする。
2. **Production反映(ユーザー決定)**: CURRENT_SPEC L2816の条件⑤を削除し、基本フロー「TTS初回生成→Primary/Secondaryの承認済み検証→NGなら最大2回のTTS再生成→なおNGならRewrite」を明記(既存文の最小修正。他の条件①〜④等は不変)。コード側: `er020`/crosslevel/er003_v1_n3に「合意」条件の名残(未使用引数・docstring・コメント・flag・test期待)があれば整理。**現行コードが既にこのフローなら、コード変更は最小限(docstring/コメント)に留め、Regressionで「最大2回のTTS再生成後にのみRewriteへ進む」「Rewrite前の承認済み検証(音韻同等性判定を含む)が省略されない」を固定**。
3. **①との整合(ユーザー§3-4)**: 委任_01の結果(音韻同等性判定の棄却箇所)を本委任では待たず、「Rewrite前のNG判定が①の修正で変わり得る箇所」を特定しRESULT_PACKETに記す(Fableが委任_03で統合)。
4. **Rewrite後〜HR移行の確認(§3-5)**: Rewrite採用→再TTS→検証→PASS_WITH_WARNING/NG→減速→再検証→最終NG時の処理(HR Lock)の実フローを関数:行で記述し、③の修正後に整合することを確認。

## Fable指示(③の要件)
5. **原因特定**: `er003_v1_n3_01_tts_generate.py` L281-282付近の減速後再検証が旧`tts_input`(書換え前)を参照する経路を、原稿(期待テキスト)がどの変数/ファイル(`tts_input`、`last_asr_text`、rewrite結果、manifest、`*_original.wav`の付随json)で保持され、LR採用時にどこが更新され、どこが更新されないかを追跡して特定。run_e2e_04 Std part3_c1の実ログ(attempt_history行15172-15176、E21行9619-9621、`lr_slowdown_whatif_part3c1_10_result.json`)で裏付ける。
6. **修正**: 正式に許可されたRewrite後は「書換え後の実送信文」を正解として、減速後再検証・再生成・retry・fallback・resume・最終検証の全てが同一の原稿ソースを参照するように一元化(例: Rewrite採用時に正解原稿を更新する単一の参照点を設け、全検査がそれを読む)。既存の音韻同等性判定・7 Gate・PASS_WITH_WARNING条件・HR Lock条件は不変。**同種の不整合の横展開確認**: Family X(B1/A2 er003_v1_crosslevel経路)、Family Z(er063)、Family Y(Trial、変更不要なら記録のみ)で、Rewrite後に旧原稿を参照する箇所をGrep(`tts_input|expected_text|script_text|original_text`等)し、該当があれば同じ修正を適用(Legacy A/B/Cは変更しない・記録のみ)。
7. **Regression**: (a)LR採用後の減速後再検証が書換え後文と照合される(モックASRで決定論) (b)LR非採用時は従来どおり (c)resume/retry/fallback経路でも正解原稿が書換え後文 (d)最終NG時のHR Lock遷移が維持される (e)②の「最大2回再生成後にのみRewrite」「Rewrite前検証の非省略」 (f)既存test全PASS(関連suite+全体suiteの既知failとの差分0)。
8. **正式経路での検証(offline、新規TTS 0)**: run_e2e_04 Std part3_c1のLR版(`narration/full_story_part3_c1_original.wav`[減速前]と現行減速版、書換え後文「He drank …」)を一時dir(`C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04_verify_fzaq2\`等、本体run dirは不変)へcopyし、修正後の正式検証関数で減速後再検証を実行(既存転写がcacheされていればAPI 0、無ければ上限JPY10)。期待: 書換え後文に対してPASS相当(NORMALIZED_MATCH)。結果を`ITEM3_FORMAL_PATH_VERIFY_01.json`に保存。**HR Lock自体は解除しない**(Lockの扱いはFable/ユーザー)。
9. 文書: `C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01\ITEMS23_REWRITE_CONDITION_AND_SCRIPT_REF_01.md`(§1 ②導入経緯と不一致原因/§2 ②Production反映/§3 Rewrite後〜HRフロー/§4 ③原因/§5 ③修正と横展開/§6 Regression/§7 正式経路検証/§8 E-1・Family別配線状況表/§9 Opus観点案[条件C: ③の共通経路変更])。

## 事前指定Read一覧
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01\HR_LOCK_PART3C1_ROOT_CAUSE_01.md` §1・§4と`lr_slowdown_whatif_part3c1_10_result.json`
- `C:\Users\tensh\eigo-radio\er020_tts_retry_local_rewrite_01.py`(L700-800中心)、`C:\Users\tensh\eigo-radio\er003_v1_crosslevel_audio_02_common.py`(L360-420)、`C:\Users\tensh\eigo-radio\er003_v1_n3_01_tts_generate.py`(L100-300)、`C:\Users\tensh\eigo-radio\er063_family_z_audio_01.py`(TTS検証・減速・HR遷移部分)
- LR設計/実装文書: Grep `LR-|LOCAL-REWRITE|local_rewrite` を`docs/`と`ER-*_REPORT.md`で実施し、DESIGN_01・ADDENDUM・IMPLEMENTATION_02b〜13・CLOSEOUT_PLAN_07を特定して該当節
- `C:\Users\tensh\eigo-radio\er011_output\attempt_history.jsonl` 行15172-15176、`C:\Users\tensh\eigo-radio\er021_output\en_asr_semantic_equivalence_production_wiring_01\telemetry.jsonl` 行9619-9621

## 事前指定Grep一覧+追記位置・更新位置の手順
- `CURRENT_SPEC.md`: `両エンジン|合意誤読|発火条件|Local Rewrite|LR`(L2801-2816)→条件⑤を削除し基本フローを明記(最小修正)、OPEN-283該当の記述があれば「書換え後の実送信文を正解とする(2026-10-19修正)」へ。`docs/pm/`配下・`.claude/agents/`に同条件の複製があればGrepして整合。
- `OPEN_ITEMS.md`: `OPEN-283`→Status=修正済み(委任_02、commit sha、正式経路検証結果)。`OPEN-42[0-9]`→委任_01が`OPEN-422`(親)を起票済みならその行に②③の結論を追記、未起票なら自分で起票(重複防止: 直前Grep)。
- `DECISION_LOG.md`: 末尾に「2026-10-19 ②両ASR合意条件の削除をProduction反映(ユーザー決定)、③Rewrite後原稿照合の修正(OPEN-283)」(委任_01のユーザー指示受領行と重複させない)。`docs/pm/REPORT_LEDGER.md`: 1行。`docs/pm/ACTIVE_TASK.md`: 先頭固定ヘッダ。`docs/pm/OPUS_FINDINGS_LEDGER.md`: OF-AUW-07の処理状況を追記。

## 実行コマンド全文(作業dir=`C:\Users\tensh\eigo-radio`)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_委任_02.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_委任_02.md_check.json`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\stop_scope_check_01.py --managed-id FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 --run-dir C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04 --out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FZAQ2_stop_check.json`
- `rg -n "tts_input|expected_text|script_text|original_text|rewritten" C:\Users\tensh\eigo-radio\er003_v1_n3_01_tts_generate.py C:\Users\tensh\eigo-radio\er003_v1_crosslevel_audio_02_common.py C:\Users\tensh\eigo-radio\er020_tts_retry_local_rewrite_01.py C:\Users\tensh\eigo-radio\er063_family_z_audio_01.py`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m pytest C:\Users\tensh\eigo-radio -q -k "er020 or local_rewrite or er003_v1_n3 or crosslevel or er063 or slowdown" --ignore=C:\Users\tensh\eigo-radio\er082_output`(修正前baseline・修正後)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m pytest C:\Users\tensh\eigo-radio -q --ignore=C:\Users\tensh\eigo-radio\er082_output -p no:cacheprovider`(全体、既知failとの差分を報告)
- 正式経路検証script(新規): `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01\item3_formal_path_verify_01.py --src-run C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04 --work-dir C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04_verify_fzaq2 --clip full_story_part3_c1 --out C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01\ITEM3_FORMAL_PATH_VERIFY_01.json`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\secret_scan_01.py --staged`

## SSOT追記文(要点)
- CURRENT_SPEC(LR節): 「Rewrite発動条件⑤『両エンジン合意誤読のみ』は2026-10-19ユーザー決定で削除(FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01)。基本フロー=TTS初回→Primary/Secondary承認済み検証→NGなら最大2回再生成→なおNGならRewrite。Rewrite採用後は書換え後の実送信文を正解として減速後再検証・retry・fallback・resume・最終検証を行う(OPEN-283修正)」。
- OPEN-283: 修正済み(commit、正式経路検証結果、横展開結果)。

## Git(明示add対象・コミットメッセージ・trailer)
- commit 1: 委任_02 delegation_log(+check+stop_check)、ITEMS23_*.md、コード(er003_v1_n3/er020/crosslevel/er063の変更分)、test、verify script+json。msg: `FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_02: ②Rewrite発動条件「両ASR合意」の導入経緯・未実装原因の特定+ユーザー決定(条件削除)のProduction反映、③Rewrite後の原稿照合をRewrite後実送信文へ一元化(OPEN-283修正)+横展開確認+Regression+offline正式経路検証(新規TTS 0)`
- commit 2: SSOT(CURRENT_SPEC/OPEN_ITEMS/DECISION_LOG/REPORT_LEDGER/OPUS_FINDINGS_LEDGER)。

## 報告(RESULT_PACKET項目: `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZAQ2.md`)
4行: (1)整合(②導入経緯→未実装原因[証拠]、OF-AUW-07の処理状況、CURRENT_SPEC新旧、Family別配線状況表[X B1/A2・Z・Y・Legacy])(2)Production到達経路(③の変更箇所:行、一元化した参照点、retry/fallback/resume/最終検証の各経路が同一ソースを読む証拠)(3)成果物とcommit sha、Regression結果(新規test名・件数、全体suite差分)、正式経路検証結果(書換え後文でPASS相当か)、①と干渉し得る箇所、実費(出典)(4)撤去/残置(旧条件の参照残り0の確認、横展開で修正した箇所/しなかった箇所[Legacy])。`判定整合:`・`判断候補:`・T-0 check・自己チェック(Lock sha不変/新規TTS 0/run_e2e_04本体不変/未承認条件追加なし)。

## ユーザー指示原文抜粋(②③該当部、委任_01が保存するUSER.mdが正本)
### 3. 不具合② TTS再試行・Rewrite発動条件 / 正式なユーザー決定: 「両ASRが同じ箇所の誤読に合意すること」というRewrite発動条件を削除する。Status: APPROVED_FOR_PRODUCTION。基本フロー: TTS初回生成 → Primary／Secondaryによる承認済み検証 → NGなら最大2回のTTS再生成 → なおNGならRewriteへ進む。既存の音韻同等性判定やその他の承認済み品質・安全条件を省略することは認めない。必須対応1〜5(導入経緯・未遵守原因の調査、関連コード・Validator・retry・fallback・HRとの関係、Production反映と旧参照整理、①との整合、Rewrite後再検証〜HR移行の確認)。この仕様変更によって、別の未承認のRewrite許容条件や品質基準を追加しないこと。
### 4. 不具合③ Rewrite後の原稿照合: `Melos drank`→`He drank`と書き換えた後、減速処理後の音声を旧原稿`Melos drank`と比較していた。これは明確な実装不整合である。正式に許可されたRewrite後は、書換え後の原稿を正解として、すべての後続音声検査を行うこと。古い原稿が残存した原因を特定/Rewrite後の正しい原稿が減速・再生成・retry・fallback・resume・最終検証まで一貫して参照されることを確認/同種の不整合が他のProduction経路やFamilyにないか必要十分な範囲で確認/修正・Regression test・正式経路での検証を完了する。

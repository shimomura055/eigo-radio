## 管理ID

`ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01` 委任_11(U1解放の発効[Fable判断: s1非該当]+A3 length再評価の是正[OPEN-388]+残Section実音声[B-A2-01 narrator・X-B1-06]+fresh JA正例+SSOT/REGISTER更新+commit/push)。並行: `FAMILY-X-COFFEE-KP-EN-EXPLANATION-PACING-TRIAL-01` 委任_01(er080系・user_test、commit/pushあり)。編集ファイルは重ならない。Git競合回避: commit時`.git/index.lock`があれば60秒待ち再試行(最大10回)。mainへの反映は`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only origin main`→`git merge --ff-only work/post-merge-01`(ff不可なら`--no-ff`、競合は中止報告)→`git push origin main`(rejectedなら`pull --ff-only`→再push、最大3回)。SSOT追記直前に`git fetch origin; git merge --ff-only origin/main`で最新化。他委任の未追跡file・本番state fileはaddしない。

## 前委任(委任_10)の受入記録(Gate 7)
- 当初目的(A-3逐語): 「固有名詞差でもPrimary NGならSecondary確認。低類似度でもPrimary NGならSecondary確認。Secondaryが原稿を正当に支持すればWARNING付き採用。数値・否定等の保護差、独立QAは例外として維持。既存日本語ASR Validator・Pronunciation Ledgerとの整合確認。過剰救済・誤受理がないことをRegressionで確認。」
- 最終成果物: commit `dfcb0bb55`/`ca32dd1a4`(実装済み・既定True=未発効)。
- 証拠: live負例8件=Secondary経由の誤受理0(N5/N6 NG_BOTH、N3 A7除外、N7/N8 NG_PROTECTED)、N1/N2/N4はPrimary PASS(U1 True/False同一、Secondary不呼出)。保存wav×Azure 8本: NG_EXCLUDED→NG_SECONDARY_UNAVAILABLE遷移0。frozen 25行: g7/g8のみ救済。
- 一致・不一致: 実装・Regressionは一致。不一致=未発効(s1文言該当で停止)、A3未是正、fresh正例未実施。
- 判定: 委任_10=ACCEPTED(実装)。**Fable判断: s1は非該当**(s1の趣旨は「U1解放によるSecondary経由の誤受理」の検出であり、N1/N2/N4はPrimary層の既存挙動でU1と因果なし[U1 True/False同一・Secondary不呼出]。Primary層の弱点は独立問題としてOPEN起票[下記])。
- QDC: 費用JPY2.23/改善見込み高/次=本委任。

## 性質/到達上限Status/禁止事項
- 性質: ユーザー承認済み統一仕様(A-2/A-3)の発効と残evidence。到達上限Status: `AUW_EVIDENCE_COMPLETE_PENDING_FABLE_15`(条件15=Fable独立照合は本委任後にFableが実施。`PRODUCTION_WIRED`は書かない)。
- 禁止: `git add -A`/`-f`、amend、rebase、force push、stash、clean、`reset --hard`、`checkout -f`、STOPセンチネル削除・回避、HR Lock変更(U4現行許容)、`force_secondary`拡大、読みでの受理導入、A4/P1/A7の変更、β期待値変更、EN側A5/A6挙動変更、有料runの再起動、Primary層の綴り読み問題への新仕様実装(OPEN起票のみ)、言語判定QAの新設。
- **T-0は全文保存**(委任_10は要約保存でFAILした。本委任文を一字一句そのまま保存すること。要約・短縮禁止)。
- 条件付きSTOP: (s4)A3是正の設計が、unified judge内の局所変更(Secondary受理時にSecondary転写でlength再評価)で収まらず、呼出元5箇所以上のAND修正やHR Lock変更を要する→設計案と影響を記録して是正を保留しFableへ(他項目は続行)。(s5)narrator/X-B1-06/fresh JAの実音声で誤受理(原稿と異なる内容がPASS/PASS_WITH_WARNING)を人手確認なしに断定できない場合は「事後試聴リスト登録・未試聴」と記録(STOPではない)。(s6)有料runが途中終了→再起動せず記録。
- Opus独立技術レビューGate(11-3): 条件C実施済み(委任_10前、U1R-01〜10)。A3是正はU1R-04でOpusが是正方向を示しており内容不変→再レビュー不要(Fable判断)。
- 時間見込み: 3〜4時間(U1発効30・A3 60〜90・narrator/X-B1-06/fresh JA 45・SSOT/Git 45)。並列化: 有料runは直列。unit testは先行。
- 費用/日次: 当日(2026-10-16 JST)既使用=AUW 約1.3+2.23、FCJ 12.65、Coffee Trial進行中(上限40)/本委任見積 約JPY8(narrator `run_tts_a2_2v_new_topic` 1 topic分=topic_intro+見出し+Hook/Tension/Closing+Voice A/B本文の新規clip 約6〜9本×実測TTS約JPY1.4〜1.6[FCJ 委任_03実測]+ASR。**旧単価0.062は過小のため使わない**; X-B1-06 1 phrase 約1.5; fresh JA 2 clip 約3)/改善見込み 高/承認区分: C。
- T-3定型文: 「上限¥16(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。(定型文は「性質」欄)

T-0保存先: `docs/pm/delegation_log/2026-10-16_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_11.md`(**全文**)。

## ユーザー指示(原文)
`docs/pm/delegation_log/2026-10-16_AUW-FAMILY-C-DQI-USER-INSTRUCTION.md`「# A.」節。A-2太字「**Primaryの差が大きいという理由だけでSecondaryを省略したり、Secondaryの正当なPASSを拒否したりしない。**」A-5「特にFamily B A2 narratorの見出し・Hook・Tension・Closingの必要な実音声確認を実施する。」「全SectionのProduction Wiring受入条件から未確認項目を黙って除外しない。」A-7完了条件13項目。

## 作業項目
1. **U1発効**: `er078_asr_unified_judge_01.py`の`U1_KEEP_C1_SIMILARITY_EXCLUSIONS`をFalse。`test_u1_constants_unchanged`/`test_u1_default_state_documented`のassert更新、Phase0 regressionの旧挙動固定5 test(`IMPLEMENTATION_10.md`§5の一覧)を解放後期待値へ更新(α)。βは不変。ロールバックtest(`U1=True` monkeypatch)は維持。OPEN-392をclose(行内追記)。REGISTER #83=「実装・発効(委任_11、commit)。範囲限定A7=登録読み保護」。
2. **A3是正(OPEN-388)**: 設計=unified judgeで「Secondaryを受理(PASS_WITH_WARNING候補)する場合、length判定をSecondary転写の文字数で再評価し、最終ANDゲートもSecondary転写由来のlengthを使う」。A3除外(`A3_LENGTH_NG`、P2)は「Primary lengthがNGでもSecondaryへ回す」よう変更し、Secondary転写でもlength NGなら`NG_BOTH`。EN/JA両方(langsが両方のため)。呼出元(`er003_v1_crosslevel_audio_02_common.py:348`、`er003_v1_n3_01_tts_generate.py:725,734`、`er003_v1_sing01_news_tail_fix.py:192`ほか)がPrimary由来lengthをANDに使う箇所を一覧化し、judgeの結果(`adopted_text`由来のlength)を使うよう最小修正。5箇所超・HR Lock変更が必要なら(s4)。unit test追加(Primary length NG・Secondary length OK→PASS_WITH_WARNING/両NG→NG_BOTH/EN同様)。保存データでA3が作用した件数集計(API 0)。
3. **B-A2-01 narrator実音声(U1R-08)**: 新規harness `er078_auw_runtime_evidence_11.py bnarr`で`er012_b_family_production_runner_01.py`の`run_tts_a2_2v_new_topic`(L1705-1757)を**実在する新規topicのparts.json**でそのまま呼ぶ(flag/module monkeypatchなし、`tts_backend`渡さない、出力レイアウト本番同一、`@with_secondary_run`相当はrunner側で張られる)。見出し(数値入り)・Hook・Tension・Closing(`disfluency_qa=True`)・Voice A/B本文を含む。共有narrationはMaster Store再利用。`tts_generation_results.json`記録と試聴リスト導出まで確認(runner側処理)。attempt_history/HR Lockの前後差分を記録し隔離由来segment_keyであることを確認。
4. **X-B1-06(U1R-07)**: X B1入口からStore missを確実に起こす新規phrase 1本(`ensure_key_phrase_english_component`経由)。約JPY1.5。APPLICABILITY_MATRIX CSVのX-B1-06行を区分1へ、「R(3回へ揃える)」とCURRENT_SPEC「KP英語phrase=4回」の食い違いを訂正(追記形式)。
5. **fresh JA正例 2 clip**: U1発効後、類似度<0.4またはentity_likeになりやすいJA原稿(委任_09集計の代表例に近い語を含む既存原稿、原稿変更禁止)でTTS→統一judge。期待=Primary NG時にSecondary呼出→PASS_WITH_WARNING(または正当なNG)。「Secondary呼出が実際に起きた」ことを実音声で確認する目的。隔離dir。
6. **OPEN起票**: (i)Primary層の弱点=誤文面TTS(ガス→カス、Meta綴り読み→META、橋→箸)をPrimaryが原稿どおりPASS(委任_10 live負例N1/N2/N4、TTS誤読の有無は未試聴)。仕様候補(Primary近音・ラテン文字化の扱い)としてユーザー判断事項、区分POST_USER_VALIDATION。(ii)`-k test_g`が5 passed(期待3)の件数差の原因(軽微)。
7. **commit後確認**: `er020_*ProductionModuleUnchanged` 2件をcommit後に再実行しPASSを確認。中核test再実行(期待: 新規失敗0、koro2件は既知OPEN-391)。静的監査(15 passed+差分空)。
8. **SSOT**: CURRENT_SPEC統一ASR判定仕様節に「U1発効(2026-10-16 委任_11、commit <hash>)」「A3是正(Secondary転写でlength再評価)」を追記、43行マトリクス最終区分(実音声<N>/再利用<N>/N/A 1/別不具合 0[Family C JAはFCJ 委任_03で実音声取得済み→区分1へ更新、根拠=`er079_output/.../EVIDENCE_02.md`§6])。DECISION_LOG委任_11エントリ。REGISTER #83更新。REPORT_LEDGER。RUNTIME_EVIDENCE_06.md §17(bnarr/X-B1-06/fresh JA/A3集計)。`CLOSEOUT_PLAN_07.md`§4の15条件表を「委任_11時点」として再掲追記(条件1・2・4・9・11・12の現状、15はFable)。ACTIVE_TASK(gitignore)。

## KPI provenance欄
narrator/X-B1-06/fresh JA: `production_formal_path`(fresh)。A3集計: `frozen`。unit: `synthetic`。E2E自己確認: narrator=Yes(Family B入口)、X-B1-06=Yes(X B1入口)。

## Opus台帳更新
`OF-AUW-U1R-04`(A3)→IMPLEMENTED/EVIDENCED、`-07`(X-B1-06)→EVIDENCED、`-08`(narrator)→EVIDENCED。追記のみ。

## 事前指定Read一覧
- `er058_output/unified_all_roles_production_wiring_01/IMPLEMENTATION_10.md` §3・§5。`RUNTIME_EVIDENCE_06.md` §16。`U1_U2_SECTION_PLAN_09.md` §3(マトリクス・bnarr計画)。`OPUS_REVIEW_C2_U1_VERBATIM.md`のQ5(a)〜(f)・Q6(narrator条件・X-B1-06)の該当部分のみ(Grep `Q5`/`Q6`)。
- `er078_asr_unified_judge_01.py` 全体構造(Grep `length_ok`/`A3_LENGTH_NG`/`adopted_text`/`final_and`→該当範囲)。
- `er003_v1_crosslevel_audio_02_common.py` L340-370、`er003_v1_n3_01_tts_generate.py` L710-740、`er003_v1_sing01_news_tail_fix.py` L185-200(length AND箇所)。全repo Grep `length_ok`で他の呼出元。
- `er012_b_family_production_runner_01.py` L1690-1760、`er012_b_family_voices_a2_production_01.py` L735-760。新規topicのparts.json候補: Glob `er012_output/**/parts.json`で未生成(a2/narration未作成)のtopicを特定、無ければ既存topicの隔離複製(新テーマ名)を使い、その旨記録。
- `er019_family_x_audio_production_runner_01.py` Grep `ensure_key_phrase_english_component`→X-B1-06経路。`er058_output/unified_all_roles_production_wiring_01/APPLICABILITY_MATRIX_01.csv` 行7。
- `OPEN_ITEMS.md` Grep `OPEN-388 `/`OPEN-392 `/末尾最大番号(起票直前に再Grep)。`docs/pm/USER_DECISION_REGISTER_01.md` L170以降。

## 事前指定Grep一覧+追記位置・更新位置の手順
(上記「作業項目」8に記載。追記はすべて節末尾・ファイル末尾へ、既存行不変。)

## 実行コマンド全文
手順0: `cd C:\Users\tensh\eigo-radio; git fetch origin; git merge --ff-only origin/main; git branch --show-current`(`work/post-merge-01`)。`New-Item -ItemType Directory -Force er058_output\unified_all_roles_production_wiring_01\evidence_11`。`.venv\Scripts\python.exe tools\stop_scope_check_01.py --managed-id ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 --run-dir er058_output\unified_all_roles_production_wiring_01\evidence_11` rc=0。
手順1〜2(実装+unit): 作業項目1・2。`$env:PYTHONPATH="C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\scratchpad"; .venv\Scripts\python.exe -m pytest -p netguard <中核12 file+er078_asr_unified_wiring_10_test_01.py+新規er078_asr_unified_wiring_11_test_01.py+er078_asr_unified_backcompat_07_test_01.py+er007_ja_scg_phase0_regression_test_01.py> -q -p no:cacheprovider`。静的監査pytest+script。
手順3(narrator、有料): `$env:TTS_EXECUTION_MODE="STANDARD"; .venv\Scripts\python.exe er078_auw_runtime_evidence_11.py bnarr --parts <実パス> --out er058_output\unified_all_roles_production_wiring_01\evidence_11\bnarr --budget-jpy 16 --execute`(T-2追記(1)〜(4)を事前記録。STOPセンチネル`evidence_11\bnarr\STOP`)。
手順4(X-B1-06、有料): `... er078_auw_runtime_evidence_11.py xkp_miss --out ...\evidence_11\xkp_miss --budget-jpy 16 --execute`。
手順5(fresh JA、有料): `... er078_auw_runtime_evidence_11.py ja_fresh --out ...\evidence_11\ja_fresh --budget-jpy 16 --execute`。
手順6(A3集計、API 0): scratchpad scriptで保存データのA3作用件数。
手順7(文書・SSOT・Git): secret scan(`--paths`)hits=0 → `git add er078_asr_unified_judge_01.py <A3是正で変更したfile群> er078_asr_unified_wiring_11_test_01.py er078_auw_runtime_evidence_11.py <更新したα test file群> er058_output/unified_all_roles_production_wiring_01/IMPLEMENTATION_11.md er058_output/unified_all_roles_production_wiring_01/RUNTIME_EVIDENCE_06.md er058_output/unified_all_roles_production_wiring_01/CLOSEOUT_PLAN_07.md er058_output/unified_all_roles_production_wiring_01/APPLICABILITY_MATRIX_01.csv er058_output/unified_all_roles_production_wiring_01/evidence_11 CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md docs/pm/USER_DECISION_REGISTER_01.md docs/pm/REPORT_LEDGER.md docs/pm/OPUS_FINDINGS_LEDGER.md docs/pm/delegation_log/2026-10-16_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_11.md docs/pm/delegation_log/2026-10-16_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_11_check.json`(wav等gitignore/大容量は除外記録) → `git commit -m "ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 委任_11: U1発効(A7登録読み保護は維持)+A3 length Secondary転写再評価+B-A2-01 narrator/X-B1-06/fresh JA実音声(JPY <実費>)"` → crbnでmainへff→push → main dirでff → 手順7の後にer020 2件再実行(作業項目7)。

## SSOT追記文
作業項目8(実値置換)。

## Git(明示add対象・コミットメッセージ・trailer)
SSOT編集権: あり(追記のみ)。`PM_GOVERNANCE.md`編集なし。Coffee Trialのfile・本番state file・他委任の未追跡fileはaddしない。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_AUW11.md`: 1 T-0(全文保存の確認) / 2 U1発効の差分・α更新一覧・β不変 / 3 A3是正の設計・差分・呼出元一覧・unit結果・A3集計(s4該当なら設計案のみ) / 4 narrator結果(clipごと: role・state・Secondary呼出・HR・試聴リスト・tts_generation_results記録・model_id/voice・費用、Q5(a)〜(f)の充足) / 5 X-B1-06結果(Store miss確認・state・費用) / 6 fresh JA結果(Secondary呼出の実発生・state) / 7 test結果(中核・新規・静的監査・er020 commit後) / 8 43行マトリクス最終表・15条件表(委任_11時点) / 9 SSOT・OPEN新規番号・commit hash・push・secret scan / 10 逸脱・新規発見 / 11 費用実測(usage_log/meter出典、単価の出典明記)・所要・使用モデル名 / 12 受入記録5項目(当初目的=A-2/A-3/A-5/A-7逐語/最終成果物[失敗終了時含む]/証拠/一致・不一致/判定)。`PRODUCTION_WIRED`は宣言しない。

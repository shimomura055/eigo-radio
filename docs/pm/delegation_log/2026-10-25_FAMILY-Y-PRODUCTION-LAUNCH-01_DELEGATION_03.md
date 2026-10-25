管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 委任_03(runner結線の仕上げ[API 0]→条件を満たせば正式E2E evidence E-3(SNS)・E-1(宅配案B)の有料実走。Cap 170円[既支出14.347円]、日次1,500円)。

## 読むもの
`docs/pm/PM_BRIEF.md`、`docs/pm/ACTIVE_TASK.md`(本案件節のみ)、`docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/{DESIGN_02,BUDGET_PLAN_03,OPEN_TRACKING_02,OPERATIONS_01,SPEC_LEDGER_02}.md`、`er121_family_y_runner_01.py`、`er121_family_y_audio_01.py`、`er121_family_y_structure_01.py`、`er121_family_y_text_core_01.py`(`produce_article` I/F、`ROUTE_AUX`、`preflight_routes`、`load_reuse`、`FIXED_CLOSING_REGISTRY`)、`theme_packages/{sns_age_limit_package_01.json,redelivery_fee_reuse_01.json}`、`er006_model_routing_contract_01.py`、`docs/research/KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01/OPERATIONS_01.md`(HR CLI操作・宣言)、ユーザー原文 `docs/pm/delegation_log/2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_USER.md`(§10 受入条件5「HRあり/なし両経路」)。

## Part A(API 0): 結線の仕上げ
1. er006へ補助routingキー2本(`FAMILY_Y_VOICE_PROVENANCE_MAP`、`FAMILY_Y_VOICE_STRUCTURE_TAG`、gpt-6-luna/medium)と価格を登録、列挙test・drift test更新。
2. runner `stage_text`から`produce_article(..., theme_package_path=, reuse=)`へ結線(`--reuse-manifest`)。runnerのreal Cap定数を150→170へ(BUDGET_PLAN_03と一致、test更新)。
3. CRLF: 案B registryのTheme Package sha照合がfile bytesで計算されるため、凍結ファイル(theme_packages配下・Voice R0 `article_ja.md`等、sha固定で参照するもの)に`.gitattributes`で`-text`(LF固定)を設定し、現在のworking treeのbytesがregistry shaと一致することを確認(不一致なら原因を特定して修正、shaを変えずに揃える。揃えられなければSTOP報告)。
4. offline smoke(偽client)で全stageを一周、test(runner/structure/text core)を`.venv`のPythonでネットワーク遮断harness下で実行(`py`にはgoogle.genaiがないため)。X/Z回帰のうち本変更に関係するもの(er006/er109/er103/er020)PASS。
5. commit/push(対象pathのみ、`git commit --only`、non-fast-forwardならfetch→`git merge --no-edit origin/main`→push、競合は両方残しSTOP報告。他agentの未commit差分を巻き込まない)。

## Part B(有料): 正式E2E evidence。**開始条件**=次の両方を満たすこと。満たさなければPart Bを行わず報告で終了。
- (i) `git log origin/main --oneline -50`に「KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 委任_03」を含むcommitがある(KP HR統合=er119の期限付き宣言撤去・文法kind追加が完了済み。未完了のままer119を使うと途中で壊れる)。
- (ii) `py docs/pm/tools/daily_dev_cost_01.py`の当日累計+94.28円(ツール未捕捉のer110 Round 2分)+本Part見積(≤160円)が1,500円以内。
手順(各起動前に`py tools/stop_scope_check_01.py --managed-id FAMILY-Y-PRODUCTION-LAUNCH-01 --run-dir <run_dir> --out <run_dir>/stop_check_<name>.json`、rc=3なら起動しない。有料は`.venv\Scripts\python.exe`。同一run dirへの起動間隔150秒以上・5分3回禁止。外部停止/原因不明rc≠0が2回続いたら再起動せずSTOP):
- **E-3(SNS年齢制限、Closing一般化Prompt 02+sol high、voices実生成、HRあり経路)**: `--mode real --approved-budget-jpy 170`相当で起動。KP HRでrc=4待機→`review_request.md`を確認→CLIで**HRあり操作**(KP: 候補からAI順位と異なる選択を1件含むselect+NG 1件[理由必須]、文法: 接続済みならtop2またはomit[理由必須])→再開→完走(TTS/ASR/gate/assemble/pages/page_verify)。候補・選択・理由・確定・後続反映(Part 1/study_text/ページ)の一致を`verify_selection_matches_outputs`で確認。
- **E-1(宅配、案B固定、R0再利用、HRなし経路)**: `--reuse-manifest theme_packages/redelivery_fee_reuse_01.json`で起動。案Bは1回判定・FAILなら**STOPしてPart Bを終了**(OT-27、ユーザー判断へ)。KP HRは**不在宣言**(`declare-absent`、`declared_by`=Fable代行、`user_ref`=ユーザー原文§10-5「Human Reviewあり／なしの両経路が確認されている」のevidence目的。候補sha/roundに紐づく)→自動確定(TOP1〜3/解説TOP1〜5)→完走。NG/未レビューの区別が記録されていることを確認。
- 各runで収集: stage順序log、actual model_id/routing key/prompt sha(Closing=gpt-6.1-sol high・判定=gpt-6-luna・Prompt 02 sha 4713ceff…)、Gate履歴(Voice/Closing/Lead紹介)、Chunk非適用記録、注意書き表示、segment ID網羅、Master store key、実費(stage別)、所要時間、retry/HR Lock発生。公開は**限定共有dir**(Yの既存運用に従う。公開先URLは`user_test/`配下の既存Y命名に合わせ、Pagesへ反映。公開前にpage_verify PASS)。
- `EVIDENCE_01.md`(E-1/E-3の結果、受入条件12項目との対応表[未達は未達と明記]、HRあり/なしの証跡、実費・単価見込み[通常Y記事の実測原価]、残課題)。`BUDGET_LOG_01.md`。

## SSOT・Git・逐語保存
OPEN-520更新(結線完了・E-1/E-3結果またはPart B未実施の理由)。OPEN_ITEMS直前再Read・最小Edit・バックアップ。CURRENT_SPEC変更なし(PRODUCTION_WIRED判定はFable)。wav/raw_usage_log不追跡、公開mp3は`user_test/`配下のみ。secret grep 0件。委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_DELEGATION_03.md`(Nは593前後、先頭「管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 委任_03」を588〜625で走査)。

## 禁止
Prompt 02・Gate基準・案B本文の変更。書換え・再判定による案B救済。Chunk/中核数値のY適用。新規テーマの選定(SNS・宅配は既存テーマ)。`er119/er120/er019/er026`の編集(他agent所有)。日次1,500円・Cap 170円超過。

## 報告(RESULT_PACKET_YPL3.md+口頭要約)
Part A変更点・test、Part B開始条件の判定結果、E-3/E-1の結果(受入条件12項目対応表、HRあり/なし証跡、Closing実使用証拠、Gate結果、実費・所要、公開URL[限定])、案B判定結果、残課題、commit hash・raw URL、RESULT_PACKET 4行+判定整合、判断候補(27-3)。
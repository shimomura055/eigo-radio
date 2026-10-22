FABLE-DELEGATION-MARKER: KPMP-TRIAL-RUN-委任_01-20261022

# 委任(FAMILY-X-KP-MINIMIZATION-PRODUCTION-PATH-TRIAL-03 委任_01: ユーザー決定の記録(#145 Luna維持/#146 A=Luna維持・B=2工程見送り・C=GO)+提案C=「最小化条件(新Prompt第3条)を現行Production経路のKP選定Promptに組み込み、同一14本文・Lunaで現行方式と比較する小規模Trial」。事前見積→開始→結果報告。Production無変更・Trial専用)

## 管理ID
FAMILY-X-KP-MINIMIZATION-PRODUCTION-PATH-TRIAL-03 委任_01(新規。前提=OPEN-445[6モデル比較、VALIDATED]・OPEN-446[Prompt改善+一般化、Trial①VALIDATED/②REJECTED]。並行: 別agentが`HR-QUEUE-TEST-CONTAMINATION-FIX-01 委任_02`(er021系test隔離、OPEN-447行・REPORT_LEDGER末尾)を作業中。共有SSOTは`git status`→該当行再Grep→自分の行だけ→即add+commit、`index.lock`は30秒待ち。新規OPEN番号は編集直前にGrepで最新+1)。

## 性質/到達上限Status/禁止事項
- 性質: 比較Trial(Trial専用実装)+ユーザー決定の記録。到達Status: 本委任は`TRIAL_DONE_PENDING_FABLE`まで(最終分類はFable。Prompt変更のProduction採用はユーザー判断)。Opus Gate: 非該当(Trial。採用提案時に条件C)。
- 修正範囲(11-8): Production側(`er030_*`、Prompt templateファイル、`er019_*`runner、`er006_model_routing_contract_01.py`、KP Store)の編集は範囲外。範囲内=Trial専用`er102_kp_min_prodpath_trial_03_*.py`(Production関数をimportして呼ぶのは可。Prompt差替えは引数/monkeypatchでTrialプロセス内のみ)、`docs/research/FAMILY-X-KP-MINIMIZATION-PRODUCTION-PATH-TRIAL-03/`、`er102_output/kp_min_prodpath_trial_03/`。Production run dir・Store・shortlist cache(Production側)への書込禁止(Trial用out_dirへ)。
- 時間見込み(8-X): 約3時間。経路特定・Trial配線45分 / 見積10分 / 2 arm×14本文の実行(並列)20分 / 機械検証・評価45分 / Excel+RESULT 45分 / SSOT 15分。
- 費用/日次: 当日(JST 2026-10-22)既使用 **約JPY800**(出典: RESULT_PACKET_PNPS9 799.5)。**日次上限1,000円まで残約200円**。本委任見積(事前算出が必須=ユーザー指示): 選定2 arm×7記事セット×約1.83円(既存Production実測/セット、shortlist+選定+canonicalization込み)≈26円+独立評価(Luna出力の異系統評価者=`claude-sonnet-5-5`のみ、2 arm×約70KP。前回Sonnet評価84run≈87円を参考に≈60〜90円)≈**合計約90〜120円**。Guardrail(T-3) **Cap JPY150**。**実トークン・単価で見積を確定し、見積+800が1,000円を超える見込みなら有料呼出を開始せず報告**(7-9: 日次超過は事前承認)。承認区分: C(ユーザーGO済み・300円以下)。評価費を抑えるため評価者は1系統(Sonnet 5.5)とし、前回との比較可能性の差を明記(前回主評価もLuna行はSonnetだったので同一尺度)。
- 禁止: `git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f。secret_scan hits=0。push=`git push origin HEAD:main`。ACTIVE_TASK/RESULT_PACKETはgitignore。SSOT全文読込禁止。他agentの未commit差分を混ぜない。STOPセンチネル確認後に開始。記事本文の再生成禁止。品質理由の再生成禁止(技術的失敗のみ同一入力で最大2回)。既存Production KPの再生成・上書き禁止。

## ユーザー原文(2026-10-22、逐語。`docs/pm/delegation_log/2026-10-22_FAMILY-X-KP-MINIMIZATION-PRODUCTION-PATH-TRIAL-03_USER.md`へ本文無改変で保存、文字数・sha256を記録)
---
KP選定モデルは GPT-6 Luna を維持 します。
選定・一般化の2工程方式（Trial②）は見送りとし、提案（C）を実行してください。

内容: 最小化条件（新Promptの第3条）を現行Production経路のPromptに組み込み、同一14本文・Lunaで現行方式と比較する小規模Trialを行う。

事前に見込み費用を算出した上で開始し、結果を報告してください。
---

## Fableの事前整理(再照合すること)
- ユーザー決定の記録(先に実施、API 0): UDR #145=判断済み(Luna維持)、#146=判断済み(A=Luna維持/B=2工程方式見送り/C=GO)。OPEN-445=`CLOSED_USER_DECIDED_LUNA_RETAINED`、OPEN-446=`CLOSED_USER_DECIDED(A:Luna維持/B:見送り/C:→TRIAL-03)`。DECISION_LOGに決定エントリ(原文の所在・sha256)。
- 組み込む条項(新Prompt第3条、`docs/pm/delegation_log/2026-10-22_FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02_USER.md` §3-2の3を逐語): 「**学習ポイントの明確化と最小化（必須）**：学ぶべき語彙・熟語・表現を明確にし、意味と自然さを保てる最短の形で抽出する。不要な目的語・修飾語・文脈は除く。5語は上限であり、目標ではない。短縮によって学習価値が失われる場合のみ、必要な語を残す。」
- 現行Production経路: KP選定=M2P0 DB hybrid(`er030_key_phrase_db_hybrid_selector_01.py` `run_db_hybrid_selection`: shortlist→軽量prompt選定[Luna]→source span検証)、Prompt template=`bk.load_prompt_template()`(所在をGrepで特定: `er030_key_phrase_db_hybrid_core_01.py`等)、その後canonicalization(原形化、Luna呼出)。呼出元=`er019_family_x_audio_production_runner_01.py`のKPステージ(Grep `run_db_hybrid_selection|canonical`)。**Trialでは同じ関数列をTrial out_dirで実行**し、Arm A=現行template(無改変・fresh実行)、Arm B=現行template+第3条(既存条項の文言・順序・出力形式は不変。第3条の挿入位置は現行templateの選定条件列挙の中で、Trial②Promptと同じ「5語以内」の直後、「学習価値」の前)。両armともshortlistは同一(Arm Aで生成したshortlistをArm Bで再利用=選定Promptの差だけを測る)。canonicalizationも両armで実行し、「選定直後」と「canonicalization後」の両方を保存。
- 14本文: `er098_output/kp_six_model_trial_01/inputs/manifest.json`と同一(sha256一致をassert)。記事G(旧記事)が現行X経路のshortlist DBで扱えない場合は欠落として明記(推測補完しない)。
- 比較軸: (1)機械=語数分布(平均・中央値・5語の割合)、本文一致(canonicalization前は厳密、後は原形化のみ許容)、5件充足数、重複。(2)既存Production KP(実記録)とArm Aの一致率(Arm Aが現行の再現になっているかの確認)。(3)独立評価=`claude-sonnet-5-5`で前回と同じrubric(V/E/N+最小化4観点C/U/S/X)をArm A/Bの両方に同一バッチで適用(同一尺度での比較)。(4)Trial②のLuna(全文渡し+新Prompt)との参考比較(尺度差を明記)。(5)例示3件(`think up what happens next`等)の追跡。
- 費用: 選定・canonicalization・評価を分離し、1記事セット当たりのArm A/Bの選定費(=量産原価への影響)を実測で。

## 実行内容
1. ユーザー決定の記録(UDR #145/#146、OPEN-445/446、DECISION_LOG、REPORT_LEDGER)→commit(本Trialの前に完了)。
2. 開始前チェック(22節)→`TRIAL_DESIGN_03.md`(経路図・Prompt差分[Before/After全文]・arm・比較軸・合格基準[Arm BがArm Aと同等以上の遵守率で平均語数が短縮し、評価のC/U/S/Xが上回り、V/E/Nが下がらないこと]・見積)。STOPセンチネル。
3. 見積確定→日次判定(超過見込みならSTOP報告)。
4. 実行: Arm A→shortlist保存→Arm B(同shortlist)。canonicalization両arm。request/response/usage/返却model ID/Prompt sha保存。
5. 機械検証・評価・Excel(`KP_MIN_PRODPATH_COMPARISON_03.xlsx`: Sheet1 記事×レベル×{既存Production/Arm A/Arm B(選定直後・canonical後)}横並び、Sheet2 品質・遵守・語数、Sheet3 評価詳細、Sheet4 費用・条件[Prompt全文Before/After])。
6. `TRIAL_RESULT_03.md`: 結論(最小化は改善したか)/遵守・語数/評価/例示追跡/既存Productionとの一致/費用・量産原価影響/限界/分類候補(7=Fable欄、8=判断候補[Prompt変更の採用可否])。
7. SSOT: 新規OPEN「FAMILY-X-KP-MINIMIZATION-PRODUCTION-PATH-TRIAL-03」`TRIAL_DONE_PENDING_FABLE`、REPORT_LEDGER。T-0: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_FAMILY-X-KP-MINIMIZATION-PRODUCTION-PATH-TRIAL-03_委任_01.md`(Nは`FABLE-DELEGATION-MARKER: KPMP-TRIAL-RUN-委任_01-20261022`を含むAgent tool_useの通番、276前後。先頭行で一致確認)。
8. commit→push→到達確認。`ACTIVE_TASK.md`固定ヘッダ。`RESULT_PACKET_KPMP1.md`。

## 事前指定Read/Grep
- Read: `er030_key_phrase_db_hybrid_selector_01.py:389-600`(選定・template読込・出力)、`docs/research/FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02/TRIAL_DESIGN_02.md`(rubric)、`er101_kp_prompt_min_gen_trial_02_{eval,excel}.py`(流用)、`er098_output/kp_six_model_trial_01/inputs/manifest.json`。
- Grep: `load_prompt_template|PROMPT_TEMPLATE|keywords_selector` in `er030_*.py`/`er003_*.py`(templateの実体ファイル)、`canonical` in `er019_family_x_audio_production_runner_01.py`/`er030_*.py`(canonicalization関数と呼出順)、`run_db_hybrid_selection(` in `er019_*.py`(引数実値)、`OPEN-44[0-9]|OPEN-45[0-9]` in `OPEN_ITEMS.md`。

## 実行コマンド全文
実行した全コマンドを実値で記録(`.venv\Scripts\python.exe er102_kp_min_prodpath_trial_03_run.py --arm A|B --out er102_output/kp_min_prodpath_trial_03 --manifest er098_output/kp_six_model_trial_01/inputs/manifest.json --cap-jpy 150` 等)。secret scan。

## SSOT追記文
- DECISION_LOG(ユーザー決定): `## FAMILY-X-KP-SELECTION-* ユーザー決定(2026-10-22): KP選定モデル=gpt-6-luna維持(UDR #145/#146-A)。選定・一般化2工程方式(TRIAL-02 Trial②)=見送り(#146-B)。提案C=最小化条件を現行Production経路Promptへ組み込む比較Trial=GO(#146-C→FAMILY-X-KP-MINIMIZATION-PRODUCTION-PATH-TRIAL-03)。原文=docs/pm/delegation_log/2026-10-22_FAMILY-X-KP-MINIMIZATION-PRODUCTION-PATH-TRIAL-03_USER.md(<文字数>字、sha256 <hash>)。Production無変更。`
- OPEN_ITEMS新規行(TRIAL-03)、OPEN-445/446のStatus更新(自分の行のみ)。REPORT_LEDGER 2行(決定記録/Trial)。

## Git
- SSOT編集権: `OPEN_ITEMS.md`(445/446/新規行)、`DECISION_LOG.md`(末尾追記のみ)、`docs/pm/USER_DECISION_REGISTER_01.md`(#145/#146行のみ)、`docs/pm/REPORT_LEDGER.md`。CURRENT_SPECは編集不可。
- 明示add: `er102_*.py`、`er102_output/kp_min_prodpath_trial_03/**`、`docs/research/FAMILY-X-KP-MINIMIZATION-PRODUCTION-PATH-TRIAL-03/**`、delegation_log 2件、上記SSOT4ファイル。
- commit例: (1)`KP選定 ユーザー決定記録: Luna維持/2工程見送り/提案C GO(UDR #145/#146、OPEN-445/446 CLOSED)、¥0` (2)`KPMP 委任_01: 最小化条件をProduction経路Promptへ組み込む比較Trial(Arm A現行/Arm B+第3条、同一shortlist・14本文・Luna、canonicalization込み)、Excel、費用JPY<x>、Production無変更、TRIAL_DONE_PENDING_FABLE`。

## 報告(RESULT_PACKET_KPMP1.md)
事前見積と実費(選定/canonicalization/評価、出典)・日次累計/Prompt Before・After全文とsha/経路図(Trialが本番と同じ関数列であることの根拠file:行)/Arm Aと既存Production KPの一致率/Arm A vs Bの機械指標・評価(同一尺度)・例示追跡/量産原価影響(Arm B−Arm A 円/セット)/限界/分類候補・判断候補(Prompt変更採用)/RESULT_PACKET 4行/実行コマンド/raw URL(xlsx、TRIAL_RESULT_03.md)。
## 管理ID
FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_13(ユーザー2026-10-17指示「Family Z Production完成・Cross-Family共通仕様の配線管理」の**Phase 1: read-only棚卸し・差分確定・再利用可否・費用照合・配線設計案・Cross-Family上位ルール文案**。JPY0。**git commit/push禁止・既存ファイル編集禁止・有料実行禁止**)。関連PM ID(新設、文案のみ): `PM-CROSS-FAMILY-SIMULTANEOUS-PRODUCTION-WIRING-RULE-01`。並行タスク衝突: BAPE 委任_04(別Agent)が`er019_output/boredom_aggression/**`・`er019_output/family_x_audio_production_wiring_01/boredom_aggression__run_bape_01/**`・`user_test/boredom_aggression_bape_e2e_01/**`・SSOT・commitを使用中 → **本委任はこれらに触れない。新規ファイル作成は`docs/research/FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01/`配下(無ければ新設)と`docs/pm/delegation_log/`の新規ファイルのみ。`docs/pm/ACTIVE_TASK.md`/`OPEN_ITEMS.md`/`DECISION_LOG.md`/`CURRENT_SPEC.md`/`PM_GOVERNANCE.md`/`REPORT_LEDGER.md`は編集しない(文案はRESULT_PACKETと計画書へ)。commitはFableが別委任で行う。**

## 性質/到達上限Status/禁止事項
- 性質: 調査・計画(read-only)。到達上限Status=`FZ_COMPLETION_PLAN_READY_PENDING_FABLE`。VALIDATED/APPROVED_FOR_PRODUCTION/PRODUCTION_WIRED判定はしない。
- 禁止: 有料API呼出一切(TTS/LLM/ASR)。Production code・Prompt・Style・test・SSOTの編集。git add/commit/push/stash等のgit書込(読み取り`git log/status/show`は可)。STOPセンチネル(`er026_output/family_z_production_e2e_01/STOP_ALL`、`<run>/STOP`、STOP_NOTICE)の削除・改名。scratchpadの`*.DISABLED_BY_FABLE`の復元。Family A/B/C。新Trial開始。
- Opus独立技術レビューGate(11-3): 本委任は非該当(調査)。**Phase 2(配線実装)は条件A該当見込み**(Family Zへの共通Style適用・Source Reference ContractのKP経路反映=処理フロー変更)。計画書にOpusレビュー観点案を含める。
- 時間見込み: 全体約60〜90分(状態棚卸し25/差分表15/再利用可否15/費用照合10/設計案・ルール文案20)。直列(単一Agent、read-only)。
- 費用/日次: JPY0。(参考: 当日2026-10-17既使用約JPY370.8+BAPE音声工程進行中。本委任は支出なし。)
- 前委任QDC/受入記録: 本管理IDの直近委任=12D(2026-10-12)、その後FAMILY-Z-MELOS-FINAL-ASSEMBLY-AND-ASR-GENERALIZATION-01 委任_04(2026-10-13)でMelos最終試聴は判断保留(REGISTER #23)。今回はユーザー新指示による再開であり、前委任の受入記録は本委任の棚卸し結果(§1)で代替する(Fableが受入記録を作成する材料を本委任が揃える)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし)
T-3: JPY0のため費用上限[Cap]なし。
**T-0補足(必須)**: (a)本委任文は**全文そのまま**保存(要約保存はFAIL逸脱)。保存先=`docs/pm/delegation_log/2026-10-17_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_委任_13.md`。(b)下記「ユーザー指示(原文)」本文(「# Claude Code／Fableへの指示」から「**今回の中心方針は、既存成果の最大限再利用、Family X共通音声仕様のFamily Z正式配線、そしてCross-Family配線漏れの恒久的防止である。**」まで)を一字も省略せず`docs/pm/delegation_log/2026-10-17_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_COMPLETION-AND-CROSS-FAMILY_USER.md`へ保存、文字数(`wc -m`)とsha256を記録。(c)stop_scope_check: `.venv\Scripts\python.exe tools/stop_scope_check_01.py --managed-id FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 --run-dir er026_output/family_z_production_e2e_01 --out er026_output/family_z_production_e2e_01/_stop_scope_check_13.json`(本委任はread-onlyなのでrc=3でも調査は続行可だが、**rcと検出したセンチネル一覧を必ず報告**。有料実行は無い)。

## ユーザー指示(原文)
(2026-10-17受領)

# Claude Code／Fableへの指示
## Family Z Production完成・Cross-Family共通仕様の配線管理

### 1. 管理対象・目的

- Family Z：`FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01` および関連継続管理ID
- Cross-Family：PM_GOVERNANCEへの上位ルール追加（既存管理体系に従って記録）

**目的：**
1. Family Z「走れメロス」を、ユーザー承認済み最新仕様に従って正式Production E2Eとして完成させる。
2. Family Xで正式採用した共通音声仕様をFamily Zにも適用する。
3. Source Reference ContractをFamily Zの正式KP経路へ反映する。
4. 今後、共通仕様のFamily間配線漏れを防止する。

今回の到達目標は、対象仕様の`PRODUCTION_WIRED`および「走れメロス」の正式Production E2E完走である。

### 2. ユーザー正式判断

以下は今回のユーザー決定として扱う。

**A. Family Z構成・Writer**

- Story本文：3分割
- Comment：3つ
- In One Line／Comment 4：設けない
- Writer：Sol R0→R1→R2
- Advancedを自然な英語で作成し、そこからStandardへ難易度調整
- Preview／Comment 1の生成順序は**現行方式を維持**。A/B Trialの新方式を採用しない。
- 今回問題となった程度の展開の先取りは許容し、Preview改善の追加Trialは行わない。

**B. Family Z音声**

Family Xで正式採用された最新の共通音声仕様をFamily Zにも適用する。

| Role | Family Zへ適用する仕様 |
|---|---|
| Full Story Narrator | PD06（旧N01から変更） |
| Standard日本語Preview／Comment | S3（旧R2から変更） |
| Advanced英語Preview | E1 |
| Key Phrase英語 | K2 |
| Standard KP日本語意味 | P8-KP |
| Advanced KP英語解説 | P7 |
| Standard英語Full Story | 既存6%減速を維持 |
| ASR・音声品質検証 | 承認済みAUW共通基盤 |

**Family Z固有仕様：Dialogue別Voice**

- Fictionの登場人物のセリフは、事前に設定した別Voiceで読み上げる。
- NarratorのPD06を登場人物のセリフへ一律適用しない。
- 既存のspeaker assignment・Dialogue Style・Voice設定を尊重する。
- NarratorとDialogueの切替、speakerの誤割当、音声結合を確認する。

**C. KP**

- Family XのKP候補供給M2P0およびKP選定優先順位A方式は、Family Zでは品質悪化のTrial結果に基づき適用しない。既存のFamily Z方式を維持する。
- **Source Reference ContractはFamily Zへ正式適用する。**
- KP選定結果と元英文の対応を、候補ID等によって決定論的に保証する。
- Source Reference Contract導入を理由に、KP選定方針自体をFamily X方式へ変更しない。

**D. Risk Flagger**

Risk FlaggerはFamily XのNews／Fact Ledger固有仕様として扱う。

今回のFamily Zへの配線対象外とし、不要な仕組みを追加しない。

### 3. 「走れメロス」の再利用方針

**既存成果を最大限再利用し、原稿から無条件に作り直さない。**

基本的な再利用対象：

- Advanced／Standard本文
- Story 3分割構成
- Preview／Comment原稿
- Key Phrase選定結果
- その他、現行仕様に適合する検証済み成果

最初に、既存成果物の内容・SHA・承認状態・Production正式経路からの利用可否を確認する。

**「新仕様との整合確認」は、既存成果物が承認済み仕様と矛盾していないか調べるという意味であり、再生成を前提としない。**

KPについては、既存の選定結果が元英文と一致するかを確認する。既存成果を安全に正式経路へ引き継げる場合は、不必要な再選定を行わない。

一方、音声Styleが変更されるRoleは正式Production経路で再生成し、検証する。

過去のHuman Review承認、ASR結果、wav、テキスト等を無条件に新runへ引き継がない。再利用には正式な検証・provenance・Gateを満たすこと。

### 4. Production Wiringの受入条件

対象仕様ごとに以下を確認する。

1. 正式Production初回経路に配線済み
2. retry／fallback／regeneration／resumeとの整合
3. DEV／Trial専用scriptのみの実装になっていない
4. 正式Productionでruntime発火を確認
5. actual model_id／routing／TTS Style SHA／Voice等が承認内容と一致
6. 必要なRegression／Validator／integration testがPASS
7. AUW・ASR・6%減速・Voice assignment・AssemblyがPASS
8. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMSを更新
9. 必要なcommit／push／mergeを確認
10. ユーザー承認仕様と実際のProduction動作が一致

**全項目を満たすまで`PRODUCTION_WIRED`にしない。**

Production側のPromptやretryに新しい仕様名を追加する場合は、正式な初回経路・承認済み仕様への参照が存在するか、Dangling Reference Checkも実施する。

### 5. Cross-Family同時Production配線原則【上位ルール】

以下を、個別Familyより上位の恒久的な開発・PM運用ルールとして正式記録すること。

**基本原則：Family固有ではない共通仕様は、あるFamilyでProduction配線する際、原則として他の対象Familyにも同時に配線する。**

対象：

- Family X
- Family Z
- 将来のFamily Y

運用：

1. 仕様変更時に、必ず「共通仕様／Family固有仕様」を分類する。
2. 共通仕様としてユーザー承認されたものは、対象Familyごとに`APPROVED_FOR_PRODUCTION`として追跡する。
3. あるFamilyでProduction配線する際、他の対象Familyでも原則同時に配線・テスト・runtime確認を行う。
4. Family別に`PRODUCTION_WIRED`の成立を判定する。1つのFamilyでの成功を他Familyの証拠として代用しない。
5. 同時配線が技術的・運用上困難な場合は、理由・未完了事項・解消予定をOpen Itemに記録し、無条件にタスクをcloseしない。
6. Family固有仕様およびユーザーが明示的に不採用とした仕様は例外。
7. 新規Family（将来のY等）をProduction化する際は、既存の共通承認仕様を最初から配線対象に含める。
8. 今後の仕様変更・Production Wiring・新規Family記事E2Eの開始／終了チェックに、この原則を組み込む。

**「Family Xで採用したがZには未反映」「Zで改善したがX／Yには未反映」という状態の放置を防止することが目的。**

今回決定した共通仕様の対象範囲をCURRENT_SPEC・DECISION_LOGへ明記し、配線追跡をOPEN_ITEMSで管理する。

### 6. 実施順序・費用管理

1. 既存の承認・Production状態・未解決Open Item・既存runをread-only確認
2. Family Zの現行構成と承認済み仕様との差分を確定
3. 必要なProduction配線を実装
4. 必要最小限の新規有料音声生成
5. 正式E2E・QA・runtime検証
6. 試聴ページ作成・費用集計
7. Fable独立受入判定
8. SSOT・Decision Log・Open Items・Git反映結果の最終確認

並列化・キャッシュ・既存資産再利用により費用と時間を抑える。

**重要：過去の¥300承認が今回の追加再生成までカバーするか、既存累計・残枠を先に照合すること。**

費用上限や対象範囲が不明な状態で新しい有料実行を開始しない。追加費用承認が必要なら、その時点でSTOPして金額と理由を報告する。

### 7. STOP条件

以下の場合はSTOPする。

- 承認済み仕様と実装が矛盾する
- Family Z固有仕様が共通仕様の導入で破壊される
- 未承認の新機能・仕様変更が必要になる
- 正式Production経路で期待したStyle／Voice／KP contractが発火しない
- 費用上限に達する、または超過が予見される
- Human Review等、ユーザー承認必須Gateが発火する
- 必須テスト・Validatorが不合格
- Production Wiring Checklistを満たせない

新たなTrial・Prompt探索・品質基準の緩和を独断で開始しない。

### 8. 最終報告

ユーザーには以下を簡潔に報告する。

1. Family Z「走れメロス」のProduction E2E完走可否
2. Standard／Advanced試聴URL
3. Family X共通音声仕様のFamily Z適用一覧とruntime証拠
4. Dialogue別Voiceの適用結果
5. Source Reference ContractのProduction配線状況
6. 既存成果の再利用範囲と新規生成範囲
7. 実測費用・工程別内訳
8. Regression／ASR／Assemblyの結果
9. 各仕様の`PRODUCTION_WIRED`判定
10. 未解決Open Item・ユーザー判断が必要な事項

FableはClaude Codeの「完了」報告をそのまま受け入れず、CURRENT_SPEC・ユーザー承認内容・Production実経路・runtime evidenceと照合して判定すること。

**「走れメロス」の音声を生成しただけで、Family Z全体の`PRODUCTION_WIRED`と判断しないこと。**

なお、既存の「走れメロス」最終試聴・受入保留については、今回のProduction仕様整備とは区別する。新しい正式試聴ページが完成した段階で結果を提示し、ユーザー判断を求めること。

---

**今回の中心方針は、既存成果の最大限再利用、Family X共通音声仕様のFamily Z正式配線、そしてCross-Family配線漏れの恒久的防止である。**

(原文ここまで)

## KPI provenance欄
該当なし(JPY0調査。費用照合は既存cost_log/stage_logの`frozen`実測値を集計し、出典行を付ける)。

## Opus台帳更新
該当なし(Phase 2でOF-FZ-*を新設予定)。

## 調査・成果物(計画書 `docs/research/FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01/FZ_COMPLETION_PLAN_01.md` に次の§1〜§9を書く。推測で埋めず、確認できない項目は「未確認(理由)」)
§1 現状棚卸し(read-only): (a)Family Z Melos run一覧(`er026_output/family_z_production_e2e_01/`配下の`run_*`、`er063_*`関連、最終assembly run)と各runのstage到達・最終更新・費用(`cost_log.jsonl`/`e2e_stage_log.jsonl`)。(b)STOPセンチネル一覧(`STOP_ALL`、`<run>/STOP`、STOP_NOTICE 2026-10-12)の存在・内容要約・設置主体。(c)既存成果物の所在とsha256: Adv/Std本文(3分割part1〜3)、Preview/Comment1〜3原稿(Std日本語/Adv英語)、KP選定結果(Strategy L、候補ID・元英文対応の有無)、speaker assignment/Dialogue Voice設定(Melos Voice=Algieba暫定 OPEN-306)、Human Review承認記録(REGISTER #10/#35、record_human_approval)、現行試聴ページURL(暫定)。(d)関連Open Item/REGISTER: OPEN-306/318/327/330/331/335/338/339/344/345、REGISTER #23/#25/#45/#46/#48/#51 の現Status(行番号付き)。(e)Family Z runnerの正式entrypointと音声Style決定箇所(Grep `N01|NARRATOR|R2|SUPPORT_JA|PREVIEW|K2|P8|P7|style_profile|speaker|dialogue` in `er026_family_z_fiction_production_runner_01.py`、`er063_*`、`er062_*`、共有`er003_v1_n3_01_tts_generate.py`。Family Xの`er019_family_x_style_profile_01.py`のようなprofile機構がZにあるか)。(f)Source Reference Contract: Family Xでの定義・実装(`CURRENT_SPEC.md`:1919周辺をGrep `Source Reference Contract`で位置特定→該当節のみRead、実装ファイル:行)と、Family Z KP経路(Strategy L)の現状(候補ID/元英文対応がどう保証されているか、`key_phrase_source_gate`相当の有無)。(g)関連regression現状: `er006 test_flagger_design_models_registered` FAIL(Family Zモデル登録、2026-10-17観測)と`er020 test_recorded_candidates`既知FAILの内容(test名:行、FAIL理由をtest実行で確認可=JPY0。`run_project_regression.py --pattern "er026*_test_*.py"`等Family Z関連testも1回実行し結果を記録)。
§2 仕様差分表(ユーザー§2 A〜D × 現行Z実装): 各行に「ユーザー決定/現行Z(ファイル:行・sha)/差分あり・なし/対応=再利用・配線変更・再生成・対象外/根拠」。特に: PD06(N01→)、S3(R2→)、E1、K2、P8-KP、P7、6%減速、AUW、Dialogue別Voice(PD06非適用の担保方法)、Strategy L維持、Source Reference Contract、Risk Flagger対象外、IOL/Comment4なし、Preview/Comment1現行順序維持(A/B Trial新方式=不採用 → OPEN-338/REGISTER #48/#51 closeの文案)。
§3 再利用可否判定(ユーザー§3): 成果物ごとに「再利用可(そのまま)/再利用可(provenance再検証要)/再生成要(理由=Style変更)/不可」。原則: 本文・3分割・Preview/Comment原稿・KP選定=再利用候補、Style変更Role(Full Story PD06、Std日本語Preview/Comment S3、Adv Preview E1、KP K2/P8/P7)の**音声**=正式経路で再生成。過去HR承認・ASR・wavは新runへ無条件引継ぎしない(新runで再検証)。Dialogue Voiceの音声は再生成が必要か(Narrator PD06化でセリフclipを分離生成しているか)を実装から判定。
§4 費用照合(ユーザー§6「¥300承認」): 承認原文の所在(delegation_log Grep `300`、`--approved-budget-jpy 300`)、承認範囲(run_e2e_01限定か管理ID全体か)、実測累計(cost_log集計、stage別、JST日別。STOP_NOTICE記載の推定約71.97+αを実測で置換)、残枠。**本件の再生成見積**: 音声秒数ベース(Coffee教訓: 既存wavの秒数合計×TTS単価+ASR+LLM)で、再生成対象Roleの秒数を実測wavから算出し、Gemini TTS/ASR/Azure二次/KP LLMを分離。見積が残枠を超えるなら「追加承認が必要な金額と理由」を明記(有料実行はしない)。
§5 配線設計案(Phase 2用、Opus条件Aレビュー対象): (a)Family ZにStyle profile機構を導入するか、Zの既存Style決定箇所へX共通定数(`er019_family_x_style_profile_01.py`のPD06/S3/E1/K2/P8/P7 sha)を参照させるか(Family横断の共通性=PM_GOVERNANCE 18節に沿う案を推奨順で2案)。(b)Dialogue別VoiceとPD06の共存(セリフsegmentにはDialogue Style、NarratorにはPD06。segment分類の実装箇所)。(c)Source Reference ContractのZ KP経路反映(候補ID決定論、gate、失敗時安全側)。(d)retry/fallback/regeneration/resume整合点。(e)Dangling Reference Check対象。(f)test計画(DefaultOffIsolation不要=承認済み仕様の正式配線、既存Z regression+新規integration test)。(g)Opusレビュー観点案5点以内。
§6 実走計画(Phase 3): 新run名案(`run_e2e_03`等、既存と衝突しない)、再利用入力の引継ぎ方法(正式経路のresume/reuse機構の有無。無ければ「原稿を入力として渡す正式手段」を特定、無ければSTOP候補)、stage順、Gate(HR Lock・AUW・6%減速・Voice assignment・Assembly)、試聴ページ(GitHub Pages、`user_test/`配下)、費用上限(§4の結論)。
§7 Cross-Family上位ルール文案(ユーザー§5の8項目を**逐語**で含む): PM_GOVERNANCE.mdへの新節案(節番号は既存末尾Grep `^## [0-9]+\.`で次番号を提案)、CURRENT_SPEC.mdへの「共通仕様の対象範囲(X/Z/将来Y)と各FamilyのAPPROVED/WIRED Status表」追記案(現時点のStatus: PD06/S3/E1/K2/P8/P7/AUW/6%減速/M2P0+A[X固有・Z不採用]/Risk Flagger[X固有]/Source Reference Contract/Strategy L[Z固有]を、X=PRODUCTION_WIRED(出典行)、Z=APPROVED_FOR_PRODUCTION(2026-10-17本指示)で埋める)、DECISION_LOG文案、OPEN_ITEMS新規「配線追跡」項目案(OPEN-412〜、番号は末尾Grepで確定)。既存21節(Existing Spec Check Gate)・22節(Trial開始前/終了前チェック)・11-3節との接続箇所(行番号)を示す。
§8 close候補(文案のみ): REGISTER #48/#51(Preview/Comment1=現行方式維持・新方式不採用・追加Trial不要=ユーザー2026-10-17 §2A)、OPEN-338、その他本指示で判断済みになる項目。再質問しない項目一覧。
§9 リスク・STOP候補・Fableへの判断候補(A/B/C/D区分): 例=STOP_ALL解除の権限(Fable設置なら26節の手順)、Voice Algieba暫定(OPEN-306)の扱い=再生成後の試聴でユーザー承認(今回は新試聴ページで提示)、#23最終試聴保留との区別、費用枠不足の可能性、regression FAILの先行是正要否。

## 事前指定Read一覧
- `docs/pm/delegation_log/2026-10-12_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_STOP_NOTICE.md` 全文
- `docs/pm/delegation_log/2026-10-12_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_11.md`、`_12D.md`: Grep `承認|300|再生成|run_e2e_02|仕様` → 該当範囲
- `docs/pm/delegation_log/2026-10-13_FAMILY-Z-MELOS-FINAL-ASSEMBLY-AND-ASR-GENERALIZATION-01_04.md`: Grep `試聴|保留|Status|URL` → 該当範囲
- `docs/pm/USER_DECISION_REGISTER_01.md`:25-70(Family Z関連行)、Grep `#48|#51|#23|#45` → 該当行
- `OPEN_ITEMS.md`: Grep `^\| OPEN-(306|318|327|330|331|335|338|339|344|345) ` → 各行
- `CURRENT_SPEC.md`: Grep `Source Reference Contract` → 該当節(±40行)、Grep `Family Z|FAMILY-Z` で節見出しのみ列挙→音声仕様・KP仕様の節だけRead、Grep `Family体系` → 該当節
- `er026_family_z_fiction_production_runner_01.py`: Grep `add_argument|def main|def run_stage|stage ==|N01|style|speaker|dialogue|voice|kp_|resume|regenerate|approved_budget` → 該当範囲(全文Read禁止)
- `er063_*.py`・`er062_*.py`: Glob後、Grep `N01|R2|SUPPORT_JA|PREVIEW|K2|P8|P7|speaker|DIALOGUE|verify_std_english_slowdown|source_reference|candidate_id` → 該当範囲
- `er019_family_x_style_profile_01.py`:140-200、:270-290(profile定義・既定)
- `er003_v1_n3_01_tts_generate.py`: Grep `A2_SLOWDOWN_TARGET_SEGMENTS|def generate_a2|style_instruction` → 該当範囲
- `docs/pm/PM_GOVERNANCE.md`: Grep `^## 18\.|^## 21\.|^## 22\.|^## 11-3|^## 2[6-9]\.` → 見出し行と各節冒頭10行、末尾の最大節番号
- `run_project_regression.py`: Grep `--pattern` の使い方1箇所

## 事前指定Grep一覧+追記位置・更新位置の手順
- 上記Read一覧のGrep。追記はしない(文案のみ計画書§7/§8へ)。
- 費用: `er026_output/family_z_production_e2e_01/run_*/cost_log.jsonl`・`e2e_stage_log.jsonl`をpythonで集計(`.venv\Scripts\python.exe`、read-only、集計scriptは`docs/research/FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01/fz_cost_inventory_13.py`として新規保存可)。
- wav秒数: 再生成対象Roleの既存wav/mp3の秒数合計(`wave`/`mutagen`/ffprobe等既存手段。失敗時は「未取得」)。

## 実行コマンド全文
1. `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-17_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_委任_13.md --json-out docs/pm/delegation_log/2026-10-17_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_委任_13.md_check.json`
2. `.venv\Scripts\python.exe tools/stop_scope_check_01.py --managed-id FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 --run-dir er026_output/family_z_production_e2e_01 --out er026_output/family_z_production_e2e_01/_stop_scope_check_13.json`
3. `git -C C:\Users\tensh\eigo-radio log --oneline -n 15 -- er026_family_z_fiction_production_runner_01.py er063_family_z_production_audio_01.py`(ファイル名はGlobで実在を確認して置換)、`git -C C:\Users\tensh\eigo-radio status --porcelain -- er026_output/ er063_output/ scratchpad/ | head -50`
4. `.venv\Scripts\python.exe docs/research/FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01/fz_cost_inventory_13.py --root er026_output/family_z_production_e2e_01 --out docs/research/FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01/fz_cost_inventory_13.json`
5. `.venv\Scripts\python.exe run_project_regression.py --pattern "er026*_test_*.py"`、`... --pattern "er063*_test_*.py"`、`... --pattern "er006*_test_*.py"`(FAIL内容の確認のみ、修正しない。各1回、JPY0であることをtest内容で確認してから実行。有料APIを叩くtestがあれば実行せず名前を記録)
(Production runnerの`--mode real`・`--stage`付き実行は禁止。`--help`/dry-run/`--mode mock`はJPY0確認後のみ可。)

## SSOT追記文
本委任では編集しない。§7/§8の文案を計画書に置く。

## Git(明示add対象・コミットメッセージ・trailer)
**本委任ではgit書込を行わない。** 新規作成ファイル一覧(計画書・費用集計script/json・委任文・ユーザー原文)をRESULT_PACKETに列挙し、Fableが次委任でcommitする。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_FZ13.md`(25行目安): T-0(委任文・ユーザー原文のpath・文字数・sha・check結果)/stop_scope rcとセンチネル一覧/§1要点(最新run・到達stage・成果物sha・HR承認・現試聴URL)/§2差分表の要点(差分ありRole一覧)/§3再利用・再生成の区分一覧/§4費用(承認原文の所在、実測累計、残枠、再生成見積[秒数根拠]、追加承認要否と金額)/§5設計案の推奨と代替/§6実走計画の要点(再利用入力の正式手段の有無=重要)/§7ルール文案の所在/§8 close候補/§9判断候補(A/B/C/D区分、`USER_DECISION_REQUIRED`ラベルは付けない)/regression結果(FAIL名と原因)/新規作成ファイル一覧/(1)既存仕様整合 (2)未承認機能既定値(変更なし) (3)失敗終了時の最終成果物 (4)撤去・残置(なし)/`判定整合:`行/QDC(次の一手=Opus条件Aレビュー→Phase 2配線、見込み)。

## Fable自己チェック(送信前)
Read一覧にGrep/行範囲あり/追記位置=なし(read-only)明記/コマンド実値あり/禁止事項(有料・git・編集)明記/並行衝突回避(BAPE領域不可触)あり/Opus Gate判定あり/時間・直列理由あり/費用JPY0行あり/前委任受入記録=棚卸しで代替と明記。
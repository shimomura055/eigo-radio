## 管理ID

`FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01`(略称FXPW)委任_01(Phase 1: ユーザー指示保存+ユーザー判断のSSOT記録+§3 Production仕様反映マトリクス確定+§7 VALIDATED分類+Hook廃止反映+Phase 2配線設計書[実装前]+Coffee E2E費用見積+test計画。**実装・有料API・Coffee生成は本委任では禁止**。設計書はFable照合→Opus条件Aレビュー後に実装へ進む)。並行: なし。Git: commit時`.git/index.lock`は60秒待ち再試行。mainへは`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only origin main`→`git merge --ff-only work/post-merge-01`→`git push origin main`→main dirで`git merge --ff-only origin/main`。

## 前委任の受入記録(Gate 7)
直前はFXWA 委任_03(commit `7f8af8ea9`、AUDIT_COMPLETE_REVIEWED、Fable受入ACCEPTED: Opus12件全反映・§14ユーザー判断5件・§14-6 Blocking最終版・§15補完sweep)。本管理IDはその後継で、ユーザーが2026-10-16に新指示を発出し、FXWA #96〜#100の判断を同時に下した(下記)。

## 性質/到達上限Status/禁止事項
- 性質: SSOT記録+監査マトリクス+設計(read-only調査+文書作成+SSOT追記)。到達上限Status: `PHASE1_MATRIX_AND_DESIGN_COMPLETE`(PRODUCTION_WIRED判定なし、実装なし)。
- 禁止: 有料API、Production code/Prompt/閾値の変更、Coffee生成、Open Itemのclose(Hook OPEN-176系の「廃止」Status更新は指示に基づき可)、既存SSOT行の書換え・削除(追記・行内追記のみ。ユーザー決定のStatusタグは指示されたもの以外変えない)、VALIDATED未決(§7のA)の採用・不採用への変更、追加Trial・個別質問、`git add -A`等。
- Opus独立技術レビューGate(11-3): **条件A該当(新しい処理フロー: 既定Style profile・Master Audio Store key・IOL文数の全経路変更)。本委任の設計書完成後にFableがOpusへ委任する。Sonnetは実装に入らない。**
- 時間見込み: 120〜150分。
- 費用/日次: JPY0。承認区分: A(ユーザー指示の実施、設計まで)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし。Phase 3以降の費用見積ではSTANDARD単価で算出)
T-3: 費用上限[Cap]なし(JPY0)。

T-0保存先(2本・**全文**・要旨化禁止):
(1) 本委任文 → `docs/pm/delegation_log/2026-10-16_FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01_01.md`
(2) 下記「ユーザー指示(原文)」の`<<<USER>>>`〜`<<<END USER>>>`の間を一字も変えずに → `docs/pm/delegation_log/2026-10-16_FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01_USER.md`(先頭に「# ユーザー指示原文(2026-10-16受領、Fable転記)」1行のみ付加可)。保存後に文字数をRESULT_PACKETへ記録。

## ユーザー指示(原文)
<<<USER>>>
# Claude Code／Fableへの正式指示
## Family X最新仕様Production統合 ＋ Coffee全面再制作

**管理ID：FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01**

**現在Status：APPROVED_FOR_PRODUCTION（一部既存PRODUCTION_WIRED）**

**今回の目標：Family X正式仕様のPRODUCTION_WIRED ＋ Coffee新規E2E完成・試聴可能**

## 1. 目的

これまでにユーザーが正式採用したFamily Xの仕様を、漏れなくProduction正式経路へ反映する。

Coffeeを代表記事として、テーマだけを維持し、Researchから音声・試聴ページまで全面的に新規生成する。

**重要：Coffee専用の例外的な完成を目的としない。今後のFamily X全記事で同じ正式仕様が自動的に適用される状態を完成させる。**

過去の反映漏れ（In One Line・K2・M2など）を再発させない。

## 2. 最新ユーザー判断

以下を最終確定仕様として扱う。

| 対象 | 正式仕様 |
|---|---|
| B3・Writer R0→R1→R2 | すべて `gpt-6.1-sol`。既存Production Wired |
| Full Story TTS（Std／Adv） | **PD06**：聞き手への語りかけ＋落ち着き |
| KP英語音声（Std／Adv） | **K2**：英語フレーズを自然なひとまとまりで発音 |
| KP日本語意味（Std） | **P8**：ニュースキャスター風。旧M2を置換 |
| KP英語解説（Adv） | **P7**：速度・リズムのバランス型。旧P3を置換 |
| Advanced Preview音声 | **E1** |
| Standard日本語Preview／Comment音声 | **R2** |
| KP候補供給 | **M2P0** |
| KP選定優先順位 | **A方式（現行）維持**。B／C不採用 |
| In One Line（Std／Adv） | **基本2文、必要な場合のみ3文** |
| Hook Side Output | **廃止**。R2 Titleを正式表示する仕様は維持 |

**適用範囲：Family X全体。Family Z等への拡大は対象外。**

Promptの正本：

- PD06＝`er057_output/pace_trial_02/prompts/prompts_pace_02.md`のPD6
- P7＝`er080_coffee_kp_pacing_trial_01.py`のp7
- P8＝`er057_std_kp_ja_style_trial_02.py`のP8
- K2／E1／R2＝既存の採用済みTrial正本と照合

同名の別Promptや別Roleを混同しないこと。逐語一致・SHAで追跡する。

Standard Full Storyの既存6%減速は維持し、PD06との併用を実証する。

## 3. 最初に必ず実施：Production仕様反映マトリクスの確定

**Research開始前に実施すること。**

参照資料：

- CURRENT_SPEC
- DECISION_LOG
- OPEN_ITEMS
- USER_DECISION_REGISTER
- FAMILY-X-WRITER-TRIAL-ADOPTION-AND-PRODUCTION-GAP-AUDIT-01
- 2026-10-16ユーザー最終判断記録
- 過去のProduction Wiring証跡

Family XのResearchからAssemblyまで、承認済み仕様を全件抽出する。

マトリクスには最低限以下を記録する。

1. 仕様名・管理ID・ユーザー承認証拠
2. 最新の正式仕様とStatus
3. Production初回経路
4. retry／fallback／regeneration／resume経路
5. 正式Prompt・モデル・routing・SHA
6. Validator／QA／Gate
7. 過去のTrial専用実装との差分
8. runtime evidenceの有無
9. 未配線・競合・Dangling Reference
10. Coffee E2Eで確認する受入条件

**承認済み仕様の反映漏れを、制作開始前にすべて検出する。**

新たなUSER_DECISION_REQUIREDが発覚した場合、ユーザーが明示的にdeferした項目以外はSTOPする。

## 4. Production Wiring

承認済み仕様について、Family X正式初回経路へ実装する。

対象：

- PD06／K2／P8／P7／E1／R2のTTS Style
- In One Line基本2文・必要時3文
- 既定Style profileへの登録
- retry／fallback／regeneration／resumeへの整合
- 必要Validator／QA／Regression test

### In One Line

旧Promptの `Exactly one sentence` を置換する。

仕様は**「基本2文、必要な場合のみ3文」**で確定済み。1文を許容する旧経路を残さない。

初回生成だけでなく、Standard継承、Local Rewrite、retry、regenerationにも適用する。

文数だけでなく、要点・意味・示唆を自然に伝える内容品質を維持する。

具体的Prompt文面と3文にする基準は設計して報告する。これは既存承認仕様の実装であり、文数方針を再度Trialに戻さない。

ただし、新しい編集方針を追加する必要が生じた場合は、ユーザー判断を要する。

### TTS Style

6仕様をFamily Xの既定profileとして適用する。

CLIによる特別指定を忘れた場合でも、承認済みStyleが自動適用されるようにする。

Master Audio Storeでは、Style変更後の音声を旧Style音声として誤再利用しない。Role・Style ID・version・Prompt SHAを整合させる。

特にP8は旧Full Story候補にも同名が存在するため、Roleを明確に分離する。

## 5. Coffee全面再制作

**テーマだけ同じ。Researchからすべて新規生成する。**

旧CoffeeのResearch結果・Fact Ledger・B3・Writer原稿・Key Phrase・音声を、新記事の正本として流用しない。

正式Production経路で以下を実施する。

1. Research新規実行
2. Verified Fact Ledger新規生成
3. B3（Sol）
4. W-1 Writer R0→R1→R2（すべてSol）
5. Advanced英語化
6. Standard難易度調整
7. M2P0＋A方式でKey Phrase新規抽出・選定
8. KP日本語意味・Advanced英語解説の新規生成
9. In One Line新規生成
10. 正式StyleでTTS新規生成
11. Standard／Advanced Assembly
12. 試聴ページ生成・実再生確認

既存のResearchから記事作成までの正式手順、Fact Lock、Risk Flagger、Review Queue、QAを省略しない。

既存ProductionのMandatory STOP／Human Review Gateがある場合は、勝手に迂回しない。

**Researchから音声までを無条件に一気通貫で実行しない。工程ごとに仕様反映マトリクスと照合し、必要なSTOPを守ること。**

## 6. Writerの重要確認

既存のB3→R2 Sol統一は、実装済みという報告だけでなく、今回の実runでも証拠を取得する。

- B3／R0／R1／R2のactual model_id
- W-1正式経路使用の証拠
- R1→R2入力契約
- Fact Lock、B3注記、AN3等の承認済みPrompt要素
- 実送信PromptのSHA
- retry／regeneration時のroutingとPrompt整合
- Trial用Writerや旧Luna／Astra経路への意図しない退行がないこと

必要なFact QA・品質Gateも省略しない。

## 7. VALIDATED未決事項の扱い

過去の未決Trialは以下に分類してSSOTへ記録する。

- **A：VALIDATEDだが正式採否未決**
- **B：後続の承認済み仕様に吸収・代替済み**
- **C：不成立・不採用・未検証**

今回、ユーザーは**個別の採否判断を行わない**と明示した。

したがって、Aはdeferredとして管理し、今回のProduction作業を妨げない。ただし、勝手に採用・不採用へ変更しない。

Bは後続仕様との関係と根拠を記録する。CはVALIDATEDと誤記しない。

この整理のための追加Trial・個別質問は禁止。

Hook Side Outputはユーザー正式判断により廃止し、OPEN-176等を更新する。

## 8. QCD・作業効率

**Quality最優先。不要な再生成・重複Trial・過剰なAPI呼出は行わない。**

- 既存の採用済みTrial成果を再利用し、採用判断をやり直さない。
- 監査・設計・テストなど無課金作業を先行する。
- 独立しているread-only作業・テストは安全な範囲で並列化する。
- 実装方法は既存Production構造を最大限再利用し、新規機構の乱立を避ける。
- 追加Trialや品質改善案を見つけた場合、独断で採用せずSTOP・報告する。
- 有料E2E開始前に費用見積を提示し、承認済み予算・既存Gateを守る。
- 無意味な再試行は行わず、同一原因の再発時は根本原因を調査する。

## 9. 受入条件

以下をすべて満たした場合に限り、`PRODUCTION_WIRED`と判断する。

1. Family X正式初回経路で全承認仕様を使用。
2. retry／fallback／regeneration／resumeも整合。
3. DEV／Trial専用scriptにしか存在しない仕様がない。
4. 正式経路のruntime evidenceあり。
5. actual model_id・routing・Prompt SHA確認済み。
6. 必要なValidator／Regression／integration test PASS。
7. CoffeeのResearchからAssemblyまで正式経路で実走。
8. Standard／Advancedとも完成・試聴可能。
9. 承認済み仕様と完成記事・音声を全件照合。
10. CURRENT_SPEC・DECISION_LOG・OPEN_ITEMS・判断台帳更新。
11. 必要なcommit／push／merge確認済み。
12. 未報告Trial・未登録Open Item・未処理のBlocking事項なし。

1件でも未達なら、完了扱いにしない。

## 10. STOP条件

以下の場合は直ちにSTOPし、事実と判断事項を報告する。

- 過去の正式承認と矛盾する新仕様が必要。
- 承認済みPrompt正本を特定できない。
- Production配線に重大な設計変更が必要で、Opus条件Aの確認が必要。
- 新しいTrialが必要となる。
- Mandatory Human Review／Budget Gate／品質Gateに到達。
- 同じ原因の失敗が再発し、既存retryで解決できない。
- 承認済み仕様の実装範囲が不明。
- 新たなユーザー判断なしでは進められない。

STOP時に勝手に次段階へ進まない。

## 11. 最終報告

非エンジニアPM向けに、以下を簡潔に報告する。

1. Family X正式仕様のProduction反映状況。
2. 今回修正・配線した仕様と適用範囲。
3. Coffee新規記事・音声・試聴ページ。
4. B3→R2の実際のSol使用証拠。
5. 初回・retry・fallback・regenerationのテスト結果。
6. 品質QAと実際の未解決問題。
7. 費用実績。
8. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS更新状況。
9. Git commit／push／merge証拠。
10. PRODUCTION_WIRED判定と残存Open Item。

FableはClaude Codeの完了報告を鵜呑みにせず、ユーザー承認・CURRENT_SPEC・実装・runtime evidence・QCD・PM Gateと照合して独立受入判定すること。
<<<END USER>>>

## Fableによるユーザー判断の読み取り(REGISTER反映用。原文の該当箇所を逐語引用して記録すること)
- #96(P7正本=er080 p7、PD06=PD6): **判断済み(Yes)**。原文「P7＝`er080_coffee_kp_pacing_trial_01.py`のp7」「PD06＝…のPD6」。
- #97(IOL 2文Prompt文面): **ユーザー承認不要・設計して報告**。原文「具体的Prompt文面と3文にする基準は設計して報告する。これは既存承認仕様の実装であり、文数方針を再度Trialに戻さない。ただし、新しい編集方針を追加する必要が生じた場合は、ユーザー判断を要する。」
- #98(Hook): **判断済み=廃止**。原文「Hook Side Output | 廃止。R2 Titleを正式表示する仕様は維持」「OPEN-176等を更新する」。
- #99(一括整理): **判断済み=今回は個別採否を行わず、A/B/C分類でSSOT記録。Aはdeferred**。原文§7。
- #100(E1/R2のFamily X既定化): **判断済み=採用**。原文「Advanced Preview音声 | E1」「Standard日本語Preview／Comment音声 | R2」「適用範囲：Family X全体」。
- Std 6%減速: **判断済み=維持+PD06併用を実証**。原文「Standard Full Storyの既存6%減速は維持し、PD06との併用を実証する。」
- FXUD-1〜8: Status「判断済み・未配線」維持、本管理IDで配線。

## 事前指定Read一覧(D-1厳守)
- `docs/research/FAMILY-X-WRITER-TRIAL-ADOPTION-AND-PRODUCTION-GAP-AUDIT-01/AUDIT_REPORT_01.md` §3・§7・§9・§14-5〜14-8・§15(マトリクスの土台。再調査せず引用)。`PART_B_TRIAL_MATRIX_01.md`(§7分類の土台)。`PART_C_PROMPT_AND_PATHS_01.md`(Prompt正本sha)。
- `docs/pm/delegation_log/2026-10-16_FAMILY-X-20261016-0900-USER-DECISION-RECORD-01_USER.md`、`CURRENT_SPEC.md` L1203-1250(09:00判断小節+訂正注記)。
- `docs/pm/USER_DECISION_REGISTER_01.md` 末尾(#96〜#100、FXUD-1〜8)。
- Production経路(Grep→範囲Read): `er019_family_x_audio_production_runner_01.py`(stage一覧・profile解決・Master Store呼出・retry/resume)、`er019_family_x_entertainment_production_runner_01.py`(Research〜Writer〜KP〜IOLの初回経路、`chain_method`、retry、Hook stageの有無)、`er019_family_x_style_profile_01.py`(全体構造: PROFILE定義・`DEFAULT_NEW_RUN_PROFILE`:110・`coffee_n01_r2_p3_e1`:108・`P8_TEXT`:48・`resolve_role_style`)、`er019_family_x_audio_plan_01.py`(role→style対応)、`er006_master_audio_store_01.py` L30-60・L130-150(key構成)、`er020_tts_retry_local_rewrite_01.py` L140-170、`er003_v1_n3_01_advanced_adaptation_generate.py` L540-620(IOL Prompt)、Std IOL継承箇所(Grep `in_one_line`/`one_line` in er003_v1_n3_01_standard*/er019*)、`er053_family_x_factlock_ja_writer_01.py`(規則・R0 block)、`er006_model_routing_contract_01.py` L40-60・L100-145。
- Prompt正本: `er057_output/pace_trial_02/prompts/prompts_pace_02.md` L70-85(PD6)、`er080_coffee_kp_pacing_trial_01.py` L30-40(p7)、`er057_std_kp_ja_style_trial_02.py` L20-30(P8)、K2=`er057_tone_trial_kp_ja_gen_01.py` L30-40、E1/R2=Grep `E1`/`R2` in `er019_family_x_style_profile_01.py`と該当Trial正本(PART_C参照)。各sha256を再計算して突合。
- Human Review/STOP Gate: Grep `STOP_NOTICE|HUMAN_REVIEW|hr_lock|Mandatory` in `er019_family_x_*runner*.py`。
- 費用出典: `docs/pm/REPORT_LEDGER.md` Grep `2026-10-16`(本日累計、行ごとの費用を合算し出典行番号を列挙)、直近Family X E2E費用(Grep `coffee_prices|FAMILY-X|FAMILY-Z-MELOS` で費用記載行)、`er005_output/cost_baseline_01/cost_summary.json`(単価)。

## 成果物(すべて`docs/research/FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01/`)
1. `SPEC_WIRING_MATRIX_01.md`: ユーザー§3の10列×Family X承認済み仕様全件(Research/Fact Ledger/Risk Flagger/Review Queue/B3/W-1 R0-R2/英語化/Std調整/IOL/KP供給M2P0/KP選定A/KP日本語意味P8/KP英語解説P7/KP英語音声K2/Full Story PD06+Std6%減速/Preview E1/R2/Comment R2/Comment4/Title R2表示/Hook廃止/統一ASR判定/Local Rewrite/Master Audio Store/Assembly/試聴ページ)。各行の「未配線・競合・Dangling」列はFXWA §9/§14-6と整合させ、新規発見は明示マーク。末尾に「新規USER_DECISION_REQUIRED候補」節(無ければ「なし」。あれば原文根拠付き。ユーザーが明示deferした§7-Aは含めない)。
2. `VALIDATED_TRIAGE_01.md`: FXWA §3・§15・PART_Bの全未決TrialをA/B/C分類(各行: Trial名/管理ID/VALIDATED根拠/分類/Bなら吸収先仕様と根拠/Cなら理由/OPEN番号)。Aは「deferred(2026-10-16ユーザー指示§7)」と記す。採用・不採用への変更禁止。
3. `WIRING_DESIGN_01.md`(実装前設計書・Opus条件Aレビュー対象): 
   - §A 既定profile: 新PROFILE(例`PROFILE_FX_20261016`)の定義案(Full Story=PD06 Std/Adv、KP EN=K2、KP JA意味=P8[KP role用の新定数名、`P8_TEXT`[Full Story候補]と分離]、KP EN解説=P7、Adv Preview=E1、Std Preview/Comment=R2)、`DEFAULT_NEW_RUN_PROFILE`切替、Family Z非影響の保証方法(Family Z runnerの参照箇所をGrepで列挙)、CLI未指定時の自動適用のtest案、Coffee限定profile`coffee_n01_r2_p3_e1`の扱い(残置/非推奨注記)。
   - §B Master Audio Store: `style_instruction_id`/`version`/Prompt shaの割当案、旧Style音声の誤再利用防止の判定ロジック(既存keyにshaが含まれるか確認し、含まれなければ追加の要否)、regression test案。
   - §C In One Line: 新Prompt文面案(「Exactly one sentence.」置換、基本2文・必要時3文、3文にする基準の具体文、Trial専用文言「12-18 words」の撤去/維持判断と根拠、内容品質要件)、適用経路一覧(Adv初回/Std継承/Local Rewrite `er020:158`ラベル/retry/regeneration)、文数Validator案(非ブロッキングか警告か=既存QA構造に合わせ、新閾値は仕様追加に当たらない範囲で)、test案。**新しい編集方針が必要と判断した場合はその箇所を明示し設計を止める(STOP候補)**。
   - §D retry/fallback/regeneration/resume整合: 各経路でprofile/Styleが初回と同一に解決されることの確認方法。
   - §E Hook廃止: 該当コード・Open Item(OPEN-176等)・SSOTの更新箇所。
   - §F test計画(unit/regression/DefaultOff不要=承認済み仕様のため既定ON、integration dry-run)。
   - §G 影響範囲・リスク・撤去対象の旧ルール(Charter原則8)。
   - §H 変更ファイル一覧とおおよその行数。
4. `COFFEE_E2E_PLAN_01.md`: ユーザー§5の12工程をstageごとに分け、各stageの実行コマンド・STOP/HR Gate・マトリクス照合項目・ユーザー§6のWriter証拠取得方法(actual model_id、chain_method、R1→R2契約、送信Prompt sha記録方法=既存機能で可能か/追加実装が必要か)・費用見積(stage別、出典付き、STANDARD単価)・本日累計(出典)と日次1,000円との関係・予算超過見込みの有無。旧Coffee成果の非流用の担保方法(新run dir名、reuse_from禁止、Master Store再利用の扱い=旧Style音声は新Style IDにより自動的に非再利用となるか)。
5. SSOT: `docs/pm/USER_DECISION_REGISTER_01.md` #96〜#100を「判断済み」へ(原文逐語引用付き)、FXUD-1〜8備考に本管理ID。`DECISION_LOG.md`末尾に本管理ID 委任_01エントリ。`OPEN_ITEMS.md`: Hook関連(OPEN-176を番号でGrep。行内追記「【2026-10-16ユーザー判断】廃止(R2 Title表示は維持)。本管理IDで反映」; closeは実装後)、§7-A項目に「deferred(2026-10-16§7)」行内追記、§7-C項目に「VALIDATEDではない」注記(該当時)。`CURRENT_SPEC.md` L1203小節末尾に「2026-10-16追補: E1/R2 Family X既定化採用・Hook廃止・IOL Prompt文面は設計報告で可・Std 6%減速維持+PD06併用実証(原文逐語)」を追記。`docs/pm/REPORT_LEDGER.md`。ACTIVE_TASK(gitignore)。

## 実行コマンド全文
手順0: `cd C:\Users\tensh\eigo-radio; git fetch origin; git merge --ff-only origin/main; git log --oneline -1`。
手順1: T-0保存2本+check。
手順2: Read/Grep(上記)→成果物1〜4作成→SSOT追記。
手順3: secret scan(`--paths` 対象ファイル)hits=0 → 明示`git add`(成果物4本+delegation_log 2本+check.json+REGISTER+DECISION_LOG+OPEN_ITEMS+CURRENT_SPEC+REPORT_LEDGER)→`git diff --cached --stat`混入なし→`git commit -m "FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01 委任_01: ユーザー指示保存+判断記録(#96-#100)+仕様反映マトリクス+VALIDATED A/B/C分類+配線設計書(Opus条件Aレビュー前)+Coffee E2E計画・費用見積(JPY0、実装なし)"`→crbnでmainへff→push→main dirでff。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_FXPW1.md`: 1 T-0(2本の保存先・文字数・check結果) / 2 マトリクス行数と「未配線・競合・Dangling」の全件リスト(FXWA既知/新規の別)+新規UDR候補(なし/あり) / 3 VALIDATED分類の件数(A/B/C)と一覧 / 4 設計書の要点: 新profile名・各roleのstyle id/version/sha、IOL新Prompt文面全文と3文基準、Master Store再利用防止の判定、Hook廃止箇所、変更ファイル一覧、STOP候補(新編集方針が必要か) / 5 Coffee E2E費用見積(stage別・合計・出典)と本日累計(出典行)・日次1,000円との関係 / 6 HR/STOP Gateの所在 / 7 commit hash・push・secret scan / 8 逸脱 / 9 費用JPY0・所要 / 10 受入記録5項目(当初目的=ユーザー§1・§3逐語/最終成果物/証拠/一致・不一致/判定)。

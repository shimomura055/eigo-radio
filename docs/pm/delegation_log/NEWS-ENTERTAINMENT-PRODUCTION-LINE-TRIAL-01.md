# 委任文全文(NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01、Sonnet受領そのまま保存)

## 管理ID

`NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01`(初回委任)。並行タスクなし。一時ファイルは標準名`docs/pm/ACTIVE_TASK.md`/`docs/pm/RESULT_PACKET.md`を上書きしてよい(前タスクNEWS-R2-TO-HOOK-TRIAL-01はcommit 8f2d246e済み。ACTIVE_TASKヘッダの「APPROVED未配線」に`NEWS-ITERATIVE-R2-PRODUCTION-WIRING-01`を保持すること)。

## 性質/到達上限Status/禁止事項

- 性質: Trial(1記事)。VALIDATED済みEntertainment方式(Original→Entertainment revision→Further entertainment revision、2回目revisionを最終記事)を**英語+既存News Production構造**へ適用し、既存Production parser/validator/downstreamへ載るかを検証する。到達上限Status=`VALIDATED`。1記事成功で`PRODUCTION_WIRED`にしない。英語Prompt版を`APPROVED_FOR_PRODUCTION`にしない。
- 本委任は**Phase A(read-only recon+前提条件判定)→Phase B(実行)**の2段構成。Phase Aの前提条件P1〜P5が1つでも不成立なら、Phase Bへ進まずSTOPして報告する(Sonnetが回避策を設計・実装しない)。
- 禁止事項(恒久変更禁止): Production Writer Prompt/Production Router(`er006_model_routing_contract_01.py`)/`CURRENT_SPEC.md`の正式Writer仕様/retry・fallback仕様/Validatorルール/Fact Check・Verified Fact Ledger関連処理/Structure Validator/Audio後工程/既存Production Gate。既存Production code(`er003_*`/`er006_*`/`er010_*`/`er011_*`/`er012_*`等)は**1行も変更しない**(importして呼ぶのみ)。Gateを通らない場合はGateを直さずSTOP。
- 既存Writer PromptのEditorial instruction(`B1_B_DIRECT_INSTRUCTION`/`A2_KAI1_INSTRUCTION`等)を新Promptに混ぜない。追加してよいのは「後工程に必要な契約」(英語/Length Target/必須Section・heading/Markdown形式)のみ。新しいEditorial ruleを追加しない。
- 新しい検索・別Source追加を行わない(Fact素材はTRIAL-02 Article Aの素材のみ)。
- R3(3回目revision)を生成しない。別途Hook生成callを行わない。
- 費用上限¥150(Writer 3 call+既存Fact Check/Validator+到達可能ならAudio[Standard同期])。Audioで新仕様・新Prompt・新fallbackが必要ならSTOP。
- 品質の主観評価はSonnetが行わない(観察事実・機械結果のみ。Editorial評価はFable)。
- `git add -A`/`stash`/`amend`禁止。DEV専用の別物パイプラインを再実装しない(Trial entry pointから既存primitiveを呼ぶ)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。

## ユーザー指示(原文)

(2026-09-24、管理ID `NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01`。要点抜粋。全文は本委任文末尾【ユーザー指示全文】としてdelegation_logへ保存)
- 「既存News Production lineをできるだけ維持したまま、News Writerの生成思想をVALIDATED済みのEntertainment方式へ置き換えられるかを、1記事だけで検証する。対象: Meta MuseのAI電話代行。」
- 「既存News Writer Promptをベースに改良しない。3記事でVALIDATEDされたEntertainment Promptを新しい基本Promptとする。Production後工程との互換性のため、英語出力/既存NewsのLength Target/既存Newsの必要Section構造/必要Markdown形式 だけをProduction contractとして追加する。既存Writer PromptのEditorial instructionを混ぜないこと。」
- 「既存Trialで使用したFact素材・Sourceを可能な限りそのまま再利用(TRIAL-02 Article A)。新しい検索や別Source追加は原則行わない。」
- 「Prompt変更内容を全文保存すること。」「既存contractを推測で作らない。実際のProduction parser/validatorが期待する形式を確認すること。」
- 「Stage 0 Original(Entertainment Prompt+Productionの最小構造contract)→Stage 1 R1(Trialで実際に使用したR1修正指示)→Stage 2 R2(同R2修正指示)。R2をFinal articleとする。R3は生成しない。」
- 「R1/R2ではTitle/Point One/Point Two/In One Lineを含む記事全体をRevision対象にする。section削除・追加・heading形式破壊・Markdown contract破壊が起きないこと。」
- 「Writer後段の既存Production品質プロセスは原則変更しない。R2が既存Gateを通らない場合、Gateを直すのではなく、そこでSTOPして原因を報告する。」
- 「Original/R1/R2ごとに新しい固有名詞・数字・出来事・Sourceにない因果関係が増えていないか確認。Factを追加して面白くすることは禁止。」
- 「英語化したPromptで同様のPrompt echo("Isn't this kind of interesting?"等)が発生するか観察。Stageごとに記録するだけ。」
- 「可能な限り正式Production code/parser/validator/downstream primitiveを使用する。Production正式Prompt/Routerを恒久変更しない。Trial用entry pointから呼び出す。DEV専用の別物を再実装しない。」
- 「既存line上で低コストにAudioまで到達可能ならAudioまで実行してよい。新仕様・新Prompt・新fallbackが必要になった場合はSTOP。」
- STOP条件: Entertainment PromptとProduction contractを両立できない/R1・R2でsection構造が崩れる/Production parserが読めない/Existing validatorがFAIL/Fact逸脱/既存Production line側にPrompt変更以外の仕様変更が必要/retry・fallback仕様判断が必要/Audio後工程で新設計が必要/新しいEditorial ruleが必要/予想外のProduction code変更が必要。
- 「最大Status VALIDATED。Trial完了後はSTOP。」

## 事前指定Read一覧

### Phase A(recon)
- `CURRENT_SPEC.md`: Grep `通常News|Daily News|Length Target|語数|Point One|In One Line|B1|A2`で「通常News」節(行204〜260付近、行804〜830付近)を特定し、該当行のみRead。確認事項: News記事(B1/A2)の必須Section構造・heading表記・Length Target(語数)・Writer入力(Verified Fact Ledger形式)・Fact Checkの入力・Structure Validatorの名称・Production正式入口(runner名/関数名)。
- `er003_v1_n3_01_articles_generate.py`: Grep `Point One|Point Two|In One Line|def parse|def validate|def run_writer|B1_B_DIRECT_INSTRUCTION|A2_KAI1_INSTRUCTION|WORD|word_count|MAX_WRITER_ATTEMPTS|def _writer_process|ledger`で位置特定→該当関数範囲Read。
- `er012_b_family_voices_writer_generic_01.py`: Grep `def run_writer_stage_generic|instruction|label`→該当範囲。
- `er006_model_routing_contract_01.py`: Grep `WRITER_MODEL|B1_WRITER|A2_WRITER|FACT_CHECK|def `→定義行のみ。
- `docs/evidence/news_iterative_r2_adoption_2026-09-24/prompts.md`: 全文。
- `docs/evidence/news_iterative_r2_adoption_2026-09-24/articles/ai_phone_original.md`/`ai_phone_revision1.md`/`ai_phone_revision2.md`: 全文。
- `er015_output/news_iterative_entertainment_trial_02/sources.md`: Article A部分。
- Verified Fact Ledgerの生成primitive: Grep `def build_ledger|def make_ledger|verified_fact_ledger|def run_research|evidence_pack` glob=`er0*.py` -l → 該当ファイルの関数定義範囲のみRead。
- 直近のNews Production記事の成果物1件の構造だけ確認。
- `docs/pm/PM_BRIEF.md`: 行151-175(ACTIVE_TASK固定ヘッダ書式)。
- `er015_news_iterative_entertainment_trial_02.py`: Grep `def call_with_previous_response_id|previous_response_id|effort`→該当範囲。

### Phase B(実行時)
- Phase Aで特定した関数のみ。

## 事前指定Grep一覧+追記位置・更新位置の手順

### Phase A 前提条件判定(全て事実で判定。RESULT_PACKET §Aに結果と根拠行を記載)
- P1: 既存Production Writer primitive(またはその直下のLLM呼出+parser+validator)を、Editorial instructionを差し替えた形で、Production codeを変更せずTrial entry pointから呼べる。
- P2: 既存Fact Check/Ledger Deviation Checkの入力となるVerified Fact Ledgerを、TRIAL-02 Article Aの素材文(sources.md)だけから、既存primitiveで、新規Web検索なしに生成できる。できない場合はP2不成立。
- P3: parserが要求するSection構造・heading表記・Length Targetが、Production code/CURRENT_SPECから一意に確定できる。
- P4: Stage 1/2(revision)の出力を同じparser/validatorで再検証できる。
- P5: 既存Writer primitiveの内蔵retryを変更せずに使える、またはTrial entry point側で「retryなし・1回生成」にでき、retry/fallback仕様判断が発生しない。
- P1〜P5全て成立→Phase Bへ。1つでも不成立→Phase Bを実行せずSTOP(RESULT_PACKETに不成立条件・根拠・必要となる仕様変更候補[提案ではなく事実列挙]を記載、Git commitは行わずSTOP報告)。

### Phase B 実行(P1〜P5全成立時のみ、詳細は省略。委任文原本参照)

### 英語Entertainment Prompt(Fable指定、骨子。詳細は委任文原本参照)

## 実行コマンド全文

```
cd C:\Users\tensh\eigo-radio
.venv\Scripts\python.exe er017_news_entertainment_production_line_trial_01.py --out-dir er017_output\news_entertainment_production_line_trial_01 --level b1 --stages 0,1,2 --downstream auto
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01.md --json-out docs\pm\delegation_log\NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01.md_check.json
.venv\Scripts\python.exe run_project_regression.py --pattern "er017*_test_*.py"
git status --short
```

## SSOT追記文

なし(SSOT変更なし。DECISION_LOG/OPEN_ITEMS/CURRENT_SPECは触らない)。

## Git(明示add対象・コミットメッセージ・trailer)

明示add: `er017_news_entertainment_production_line_trial_01.py`、`er017_news_entertainment_production_line_trial_01_test_01.py`、`er017_output/news_entertainment_production_line_trial_01/`、`NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01_REPORT.md`、`docs/pm/delegation_log/NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01.md`、同`_check.json`。
Phase A不成立でSTOPする場合はcommitせず(delegation_logのみcommit可)報告。

## 報告(RESULT_PACKET項目)

0. T-0結果。
1. §A Phase A: P1〜P5判定(成立/不成立、根拠ファイル:行)、既存contractの正確な内容。
2〜11. (Phase B実施時のみ、詳細は委任文原本参照)

---
【ユーザー指示全文】

管理ID: `NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01`

## 1. 目的
既存News Production lineをできるだけ維持したまま、News Writerの生成思想を今回VALIDATED済みのEntertainment方式へ置き換えられるかを、1記事だけで検証する。対象: Meta MuseのAI電話代行「AIに店への電話を頼んだら、裏では人間が話していた」テーマ。今回確認したいのは「既存News Productionの後工程を壊さず、新しいEntertainment Writer Promptで英語記事を生成し、その完成記事をさらにR1→R2とRevisionして、R2を既存後工程へ流せるか」である。

## 2. 今回の考え方
既存News Writer Promptをベースに改良しない。既存PromptのEditorial思想に引っ張られることを避けるため、今回3記事でVALIDATEDされたEntertainment Promptを新しい基本Promptとする。ただし、Production後工程との互換性のため、英語出力/既存Newsの長さTarget/既存Newsの必要Section構造/必要Markdown形式 だけをProduction contractとして追加する。既存Writer PromptのEditorial instructionを混ぜないこと。

## 3. 対象記事
Meta Muse / AI電話代行。既存Trialで使用したFact素材・Sourceを可能な限りそのまま再利用する。既存Evidence: `NEWS-ITERATIVE-ENTERTAINMENT-TRIAL-02`のArticle A。新しい検索や別Source追加は原則行わない。今回の目的はSource探索ではなくWriter方式の検証。

## 4. 新Writer Prompt
基本Promptは、下水道・AI電話・旅行荷物で使用したEntertainment Prompt。趣旨: 最も意外なFactではなく、最も面白い「見方」を一つ選ぶ/その見方に必要なFactを中心に使う/ニュース全体を網羅説明しようとしない/軽快で自然/新聞・行政資料・教材調にしない/Audioで一度聞いて理解しやすい/Factは厳守/架空の出来事・発言を加えない。これを英語記事生成用に適用する。単純な日本語Promptの直訳で品質を損なわないようにしてよいが、Editorial思想・要求内容は変えない。Prompt変更内容を全文保存すること。

## 5. Production contractとして残すもの
今回残すのはEditorial思想ではなく、後工程に必要な契約のみ。既存News Productionが要求する正確なcontractをRepoで確認したうえで適用する。最低限: 英語/既存NewsのLength Target/Point One/Point Two/In One Line/既存parserが要求するMarkdown heading・section形式。既存contractを推測で作らない。実際のProduction parser/validatorが期待する形式を確認すること。

## 6. 生成順序
最初からProduction互換構造で生成する。Stage 0 Original: Entertainment Prompt+Productionの最小構造contractで英語記事を生成。Stage 1 R1: Stage 0の記事全文に対して、Trialで実際に使用したR1修正指示を適用。Stage 2 R2: R1全文に対して、Trialで実際に使用したR2修正指示を適用。R2をFinal articleとする。R3は生成しない。

## 7. Revision時の重要条件
R1/R2では本文だけでなく Title/Point One/Point Two/In One Line を含む記事全体をRevision対象にする。ただしRevisionによって section削除/section追加/heading形式破壊/Markdown contract破壊 が起きないこと。Revision後も既存Production parserで正常に読める必要がある。

## 8. 今回変えないもの
Writer後段の既存Production品質プロセスは原則変更しない。特に Fact Check/Verified Fact Ledger関連処理/Structure Validator/その他既存Validator/Audio向け後工程/既存Production Gate は、新Prompt対応のために安易に緩和・変更しないこと。R2が既存Gateを通らない場合、Gateを直すのではなく、そこでSTOPして原因を報告する。

## 9. Fact Safety
Meta Museについては既存Trialで使用したFact素材を正式入力として使用する。Original/R1/R2ごとに 新しい固有名詞/新しい数字/新しい出来事/Sourceにない因果関係 が増えていないか確認。特にRevisionによってEntertainment性を上げる際に、Factを追加して面白くすることは禁止。

## 10. 重要：広告問題は今回対象外
旅行荷物で発見した広告・商品紹介Source問題は別Open Item。今回はMeta Museなので、Search/Source Selection改善は行わない。

## 11. 「これ、ちょっと面白くない？」問題
現在Monitoring中。英語化したPromptで同様のPrompt echoが発生するか観察する("Isn't this kind of interesting?"/"Here's something interesting..."/Prompt指示文の露骨な反映)。今回はPrompt修正目的ではない。発生した場合はStageごとに記録するだけ。

## 12. 既存Production lineでのTrial
可能な限り正式Production code/parser/validator/downstream primitiveを使用する。ただし今回はTrial。Production正式Prompt/Routerを恒久変更しない。必要であればTrial用entry pointから 新Entertainment Writer Prompt→R1→R2→既存Production parser/validator/downstream を呼び出す。DEV専用の別物を再実装しない。

## 13. Audioについて
第一目的は「R2英語記事が既存Production lineへ正常に載るか」の確認。既存line上で低コストにAudioまで到達可能ならAudioまで実行してよい。ただし、Audio生成のために新仕様・新Prompt・新fallbackが必要になった場合はSTOP。既存経路をそのまま通せる場合のみ進める。

## 14. 比較
以前の日本語Original/R1/R2と今回の英語Original/R1/R2を保存・報告する。完全な翻訳一致を求めるものではない。確認したいのは「日本語Trialで確認されたEntertainment性の改善パターンが、英語+Production構造でも再現するか」。

## 15. 評価観点
Editorial Quality: OriginalよりR1が良くなるか/R1よりR2が安定して良いか/面白い「見方」が一本通っているか/説明記事に戻っていないか/Newspaper・textbook調になっていないか/Audioで聞きやすいか。Production Compatibility: Point One/Point Two/In One Lineが維持される/Markdown contract PASS/parser PASS/existing validators PASS/Fact Check PASS/downstreamに渡せる。Revision Safety: Revisionでstructure破壊なし/Fact追加なし/R3を呼んでいない/Prompt echo観測。

## 16. Hookについて
今回は別途Hook model Trialを混ぜない。ただし Original Title/R1 Title/R2 Title がどのように改善したかは保存する。R2 Titleが既に強いHook相当になるかは観察事項として報告。別のHook生成callは今回は行わない。

## 17. Cost / runtime evidence
各Stageについて actual model_id/response_id・previous_response_id/input・output token/reasoning usage/latency/cost を保存。Production parser/validator/downstreamについても実行結果を残す。

## 18. STOP条件
Entertainment PromptとProduction contractを両立できない/R1・R2でsection構造が崩れる/Production parserが読めない/Existing validatorがFAIL/Fact逸脱/existing Production line側にPrompt変更以外の仕様変更が必要/retry・fallback仕様判断が必要/Audio後工程で新設計が必要/新しいEditorial ruleが必要/予想外のProduction code変更が必要。問題が起きたら原因を報告し、追加Trialはユーザー判断待ち。

## 19. Status
開始Status: R2方式自体は`APPROVED_FOR_PRODUCTION / WIRING INCOMPLETE`。今回の英語+既存Production lineへの適用方法は新しいTrial。最大Status `VALIDATED`。1記事成功だけで`PRODUCTION_WIRED`にしない。英語Prompt版を自動的に`APPROVED_FOR_PRODUCTION`にしない。

## 20. Production変更禁止
恒久変更しない: Production Writer Prompt/Production Router/CURRENT_SPECの正式Writer仕様/retry・fallback仕様/Validatorルール。Trial用に必要なコードとEvidenceのみ。

## 21. 最終報告
1. 実際に使用した英語Writer Prompt全文 2. Production contractとして追加した部分 3. 英語Original全文 4. 英語R1全文 5. 英語R2全文 6. TitleのOriginal→R1→R2変化 7. Editorial Quality評価 8. Production parser結果 9. Fact Check/Validator結果 10. downstream到達点 11. Audioまで到達したか 12. actual model_id/cost/latency 13. 日本語Trialとの比較 14. 問題点 15. Fable評価 16. Trial status分類 17. USER_DECISION_REQUIRED事項 18. Production恒久変更なし。Trial完了後はSTOP。追加修正・Production wiringへはユーザー判断なしに進まないこと。

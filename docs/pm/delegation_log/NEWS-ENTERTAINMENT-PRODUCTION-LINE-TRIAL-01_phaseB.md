# NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01 Phase B 委任文(2026-09-24、全文保存)

## 管理ID

`NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01`(Phase B、Fableからの継続指示1回目。Phase Aはcommit ea55b569でSTOP済み、ユーザーがOption (a)を承認しPhase B実施を指示)。**並行タスクあり**: 別のsonnet-workerが`NEWS-HOOK-POLICY-DECISION-01`でDECISION_LOG/OPEN_ITEMS/CURRENT_SPEC/REPORT 2件(HOOK-MODEL-COMPARISON-01/R2-TO-HOOK-01)を編集中。衝突回避のため、本タスクは(1)SSOTと当該REPORT 2件を一切触らない、(2)一時ファイルは`docs/pm/ACTIVE_TASK_ENT.md`/`docs/pm/RESULT_PACKET_ENT.md`(接尾辞付き)を使う、(3)commit時に`index.lock`があれば10秒待って再試行し、自タスクのファイルだけを明示addする。

## 性質/到達上限Status/禁止事項

- 性質: Trial(1記事)。既存News Production lineの正式Research/VerificationでVerified Fact Ledgerを作り、英語Entertainment Writer Prompt+Production contractでOriginal→R1→R2を生成し、R2を既存parser/Structure Validator/Ledger Deviation Checker/Fact Check/downstreamへ通す。到達上限Status=`VALIDATED`。`PRODUCTION_WIRED`/`APPROVED_FOR_PRODUCTION`にしない。
- 禁止事項: Production code(`er003_*`/`er006_*`/`er010_*`/`er011_*`/`er012_*`等)を1行も変更しない(importして呼ぶのみ。sha256を実行前後で比較し証跡化)。既存Research/Verification/Fact Check/Deviation/Structure Validator/Audio後工程/Gateを緩和・変更しない。Gate FAIL時はGateを直さずSTOP。既存Writer Editorial instruction(`B1_B_DIRECT_INSTRUCTION`/`COMMON_BLOCK_TEMPLATE`等)を新Promptへ混ぜない。手作りLedger禁止。R3を生成しない(code pathも作らない)。新しいEditorial rule・新Prompt(Side Hook以外)・新fallbackを追加しない。retry/fallbackの新仕様判断が必要になったらSTOP。費用上限**¥250**(Research/Verification含む。超過見込みでSTOP)。品質の主観評価はSonnetが行わない。`git add -A`/`stash`/`amend`禁止。
- 既存Production Trial(News Writer/R2)を邪魔しない: Production記事の共有ストア(Pronunciation Ledger/Master Audio Store等)へ書き込むstageに到達する場合は、既存Trial記事と同様のTrial用theme名(`entertainment_trial_meta_muse`等)で分離し、既存記事のartifactを上書きしない。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。本Phase Bは`docs/pm/delegation_log/NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01_phaseB.md`へ保存(Phase Aのlogを上書きしない)。

## ユーザー指示(原文)

(2026-09-24、Phase B承認指示。全文を以下に転記し、delegation_log(phaseB)へそのまま保存)

> ユーザー判断: Meta Museについて、既存ProductionのResearch/Verificationを使って正式なVerified Fact Ledgerを作ることを承認する。したがって、Ledger調達方法はOption (a)で確定。
> ## 1. Phase Bへ進むこと: 既存ProductionのResearch/VerificationをMeta Muse題材で1回実行し、正式なVerified Fact Ledgerを作成する。これは今回に限って「新しい記事探索をするための検索」ではなく、既存News Productionの正式Fact Check工程を成立させるためのResearch/Verificationとして許容する。既存Research/Verificationの挙動自体は変更しないこと。
> ## 2. 今回のTrial対象: Meta Muse/AI電話代行の記事1本のみ。テーマ「AIに店への電話を頼んだら、裏では人間が話していた」。既存TRIAL-02で使用したReuters系素材と同一テーマを対象にする。
> ## 3. 実施順序: Step 1 既存Production Research/Verification→Verified Fact Ledger作成。Step 2 新Entertainment Writer Prompt+既存Production contractで英語Original生成。Step 3 R1。Step 4 R2。Step 5 R2をFinal articleとして既存Productionのparser/Structure Validator/Ledger Deviation Checker/Fact Check/必要な既存Gateへ通す。Step 6 全PASSした場合のみ既存downstream(Key Phrase/TTS/Assembly/Player)へ進む。新しい仕様・Prompt・fallbackが必要になった時点でSTOP。
> ## 4. Writer方針: 既存News WriterのEditorial思想を混ぜない。VALIDATED済みのEntertainment Promptを基本とし、Production互換のために必要なものだけ追加する(英語出力/B1 Length Target/# Title/Main Story/### 見出し×2/## In one line)。その他の既存Writer Editorial instructionは持ち込まない。
> ## 5. Revision: Original生成後に記事全体をR1→R2とRevisionする。Title/Main Story/Point相当Section/In one lineを含めた全文がRevision対象。R3は呼ばない。
> ## 6. B1条件: 総語数280〜420語(soft target)、Point相当Section各30〜60語目安、既存Structure contractを維持。A2は対象外。
> ## 7. Ledger/Fact Safety: Verified Fact Ledgerは正式Productionの既存Research/Verificationで作る。Trial用手作りLedgerは禁止。R1/R2によってLedger外の固有名詞・数字・出来事・因果関係が増えていないか確認する。既存Fact Check/Deviation Gateを緩和しない。
> ## 8. Hook: 今回の正式表示はR2 Title。別Hook Generatorは今回のTrialの合否に使わない。R2完成後にLunaで比較観測用Hookを1本Side outputとして生成することは可。Side HookはUI/Audio/Validator/Trial合否に使わず、失敗してもMain Trialは失敗扱いにしない。`R2 Title vs Luna Hook`の比較ログとして保存するだけ。
> ## 9. STOP条件: Research/Verificationが既存Production条件で正常に完了しない/Ledgerが作れない/Entertainment PromptとProduction contractを両立できない/R1・R2でSection構造が崩れる/parser FAIL/Structure Validator FAIL/Ledger Deviation・Fact Check FAIL/downstreamで新仕様が必要/Production code本体の変更が必要/retry・fallbackの新仕様判断が必要。問題が出た場合は原因と選択肢を報告する。
> ## 10. Cost上限: 既存Research/Verificationを含め¥250以内。上限超過見込みの場合はSTOP。
> ## 11. Status: 最大`VALIDATED`。1記事PASSしても`PRODUCTION_WIRED`にしない。英語Entertainment Writer方式を自動的に`APPROVED_FOR_PRODUCTION`に変更しない。
> ## 12. 最終報告: 1.Research/Verification結果 2.Verified Fact Ledger 3.Entertainment Writer Prompt全文 4.Production contract追加部分 5.英語Original全文 6.英語R1全文 7.英語R2全文 8.Titleの変化 9.parser/Structure Validator結果 10.Ledger Deviation/Fact Check結果 11.downstream到達点 12.Audio生成有無 13.R2 Title 14.比較観測用Luna Hook 15.actual model_id 16.cost/latency 17.Editorial Quality評価 18.日本語Trialとの比較 19.Trial status分類 20.USER_DECISION_REQUIRED事項 21.Production恒久変更なし。完了後はSTOPし、ユーザー判断を待つこと。

## 事前指定Read一覧

- `NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01_REPORT.md`: 行8-47(Phase Aで確定したcontract・Gate関数名・行番号。再調査せずこれを使う)。
- `er003_v1_en_direct_vfl_01_generate.py`: Grep `def run_researcher|def run_verification|def run_deviation_check|def run_writer_with_technical_retry|VERIFICATION_PROMPT_TEMPLATE|def build_ledger_text|ledger_path|def main`→各関数のシグネチャ・入出力(Ledgerファイル形式・保存先・戻り値)のみRead。**Productionがこの2関数をどう呼んでいるか**を`er012_b_family_production_runner_01.py`(Grep `run_researcher|run_verification|research|ledger`)と`er003_v1_n3_01_articles_generate.py`(Grep `run_researcher|verified_ledger_text|def load_ledger|ledger`)で確認し、同じ引数・同じmodel・同じeffortで呼ぶ。
- `er003_v1_n3_01_articles_generate.py`: Grep `def parse_article|def parse_|validate_point_structure|def run_point_overlap_qa|def compute_metrics|TOTAL_SOFT|def build_fact_check|canon_spelling|def _extract_sections`→parser/metrics/QA関数のシグネチャと、**検査のみ(再生成なし)で呼べる関数の有無**を確認。
- `er002_ja_free_markdown_restore_r2.py`: Grep `def validate_point_structure`→関数範囲。
- `er011_open146_ledger_canonical_en_spelling_production_01.py`: Grep `def build_canonical_spelling_fact_check_block|def run_fact_check|def `→Fact Check blockの呼び方。
- `er012_b_family_production_runner_01.py`: Grep `def main_b1_2v|stage ==|"key_phrases"|"tts"|"assemble"|"player"|theme_module|THEME_CONFIG|article_path|def load_theme`→downstream各stageの入力(記事ファイルpath/JSON/theme config)とTrial記事を渡す方法。Production codeを変えずに渡せるか判定。
- `docs/evidence/news_iterative_r2_adoption_2026-09-24/prompts.md`: 全文(P7逐語[AI電話版]・developer・R1/R2指示)。
- `docs/evidence/news_iterative_r2_adoption_2026-09-24/articles/ai_phone_original.md`/`ai_phone_revision1.md`/`ai_phone_revision2.md`: 全文(比較表用。Promptへ入れない)。
- `er015_output/news_iterative_entertainment_trial_02/sources.md`: Article A部分(テーマ・Reuters URL。Researchのテーマ入力に使う)。
- `er015_news_iterative_entertainment_trial_02.py`: Grep `previous_response_id|effort|def call`→連鎖呼出実装(流用)。
- `er016_news_r2_to_hook_trial_01.py`: Grep `developer|user =|schema|EFFORT`→Side Hook用Prompt逐語(そのまま流用)。
- `er005_output/cost_baseline_01/pricing_snapshot.json`: luna/sol/web_search単価行。
- `docs/pm/PM_BRIEF.md`: 行151-175。

## 事前指定Grep一覧+追記位置・更新位置の手順

### Step 1 Research/Verification(既存Production primitive、挙動無変更)
- Productionが呼ぶのと同一の関数・引数・model・effortで、テーマ=「AIに店への電話を頼んだら、裏では人間が話していた(Meta Muse AI電話代行、Reuters 2026-09-22報道)」をResearch→Verificationし、Verified Fact Ledgerを`er017_output/news_entertainment_production_line_trial_01/ledger/`へ保存(Productionと同じファイル名・形式)。Research/Verificationのraw response・usage・cost・`response.model`・Web検索回数を記録。**Ledger内容を編集しない。** 完了しない/Ledgerが作れない→STOP(原因・選択肢を報告)。
- Ledger本文をREPORT §1に全文転記。

### Step 2〜4 Writer(Trial entry point `er017_news_entertainment_production_line_trial_01.py`)
- Stage 0 user prompt=英語Entertainment Prompt(P7を文単位で忠実に英訳。REPORT §3にP7原文との対照表)+contract(下記)+`[News — Verified Fact Ledger]`欄にLedger本文(Productionと同じ`verified_ledger_text`)。developer: `You are a writer who explains the news clearly and makes it enjoyable to read.` model=`routing.WRITER_MODEL`(gpt-5.6-luna)、effort high、Responses API、web_searchなし、1回生成(Trial側retryは空出力/JSON不正のみ1回)。
- **英語Entertainment Prompt(骨子。P7の各文に対応させ、追加・削除なし)**: `Turn the news below into a piece you might share with a friend, the way you'd say "Hey, isn't this kind of interesting?"` / `From the news, pick not the most surprising fact but the single most interesting way of looking at it, and build the piece around that. Use mainly the facts needed for that viewpoint; do not try to cover the whole story.` / `Keep the tone natural and light. Do not write like a newspaper, a government document, or a school textbook.` / `Write so that a learner of English can understand it by listening to it once.` / (P7の「遠い地域だけの特殊な話に見える場合は…一度だけ示してください」の文を忠実に英訳) / `Stick strictly to the facts. Do not add fictional events or quotes.` / `Theme: <テーマ英訳>`。
- **Production contract(追加部分として分離明記)**: `Write in English.` / `Length: about 280–420 words in total.` / `Format (Markdown): start with "# " followed by the title; then the main story; then exactly two "### " subsections, each 30–60 words, with headings that describe their content in your own words (do not use labels like "Point One"); then a final section headed exactly "## In one line" containing one sentence.` ←Phase A §A「前提」節のcontractと一致させる(heading表記は`# `/`### `×2/`## In one line`の正確な文字列)。
- Stage 1: `previous_response_id`=Stage 0、user=「この記事を、事実関係は変えずに、もっとエンターテインメント性の高い記事に修正してください。」+contract 1行 `Keep the same Markdown structure (the "# " title, the main story, exactly two "### " subsections, and the "## In one line" section); do not add or remove sections. Write in English.`
- Stage 2: `previous_response_id`=Stage 1、user=「この記事を、事実関係は変えずに、さらにもっとエンターテインメント性の高い記事に修正してください。」+同contract 1行。
- 各Stage: `stage{0,1,2}_*.md`保存、`api_meta_stage{n}.json`(`response.model`・response_id・previous_response_id・usage[input/output/reasoning]・latency・cost)。Prompt echo検査(`Isn't this|isn't it interesting|Here's something interesting|kind of interesting|これ、ちょっと面白くない`、大小無視)→`prompt_echo.json`。Title抽出→`titles.json`。語数(総語数・各###節)→`metrics_stage{n}.json`。

### Step 5 既存Gate(検査のみ、再生成なし)
- 各Stage出力に対し順に: 既存parser→`validate_point_structure()`→Ledger Deviation Checker(`run_deviation_check`、Ledger=Step 1)→Fact Check block(canonical spelling、Ledgerに該当行があれば)→Point Overlap QA(**検査のみで呼べる関数がある場合のみ**。再生成付き関数しか無ければ「未実行(再生成付きのため)」と記録し、Fableへ報告)。結果を`gate_stage{n}.json`。
- **Stage 2(final)がいずれかFAIL→STOP**(downstreamへ進まない。Stage 0/1の結果も併記して原因報告)。Local Rewrite/記事retryは呼ばない(新仕様判断に該当)。

### Step 6 downstream(Stage 2全PASS時のみ)
- 既存runnerのB1 downstream stage(Key Phrase→TTS[Standard同期]→Assembly→Player)を**既存関数そのまま**で実行。Trial記事を渡すためにtheme config(data)の作成が必要なら`er017_output/.../theme_config/`配下にTrial用moduleを置く(Production codeの変更ではない)。Production code変更が必要/新仕様・新Prompt・新fallbackが必要→その時点でSTOPし到達点を記録。Audio Validation Gate/Human Review Lockが出たらoverrideせず記録してSTOP。各stageの結果・生成物path・費用を`downstream_log.json`。
- 費用は逐次集計し、累計が¥250に達する見込みなら次stageに進まずSTOP。

### Step 7 Side Hook(合否に無関係、失敗しても継続)
- Stage 2完成後、`er016_news_r2_to_hook_trial_01.py`のPrompt逐語(developer/user/schema)で、テーマ文+Stage 2全文(英語)を入力にLuna・effort medium・1 call。`side_hook_luna.json`(hook_ja/used_angle_ja/`response.model`/usage/latency/cost)。`hook_comparison.md`に`R2 Title | Luna Hook`を並べる(評価はFable)。失敗時はエラーを記録して続行。

### 証跡
- 実行前後で`er003_v1_n3_01_articles_generate.py`/`er003_v1_en_direct_vfl_01_generate.py`/`er002_ja_free_markdown_restore_r2.py`/`er011_open146_ledger_canonical_en_spelling_production_01.py`/`er012_b_family_production_runner_01.py`/`er006_model_routing_contract_01.py`のsha256を記録→`production_code_sha256.json`(一致必須)。
- `cost.json`: Step別(Research/Verification/Writer×3/Gate/downstream各stage/Side Hook)、model_idキー集計、Web検索回数、合計。
- `comparison_ja_en.md`: 日本語Original/R1/R2 vs 英語Stage 0/1/2。
- 新規test `er017_news_entertainment_production_line_trial_01_test_01.py`: (1)Stage 3のcode pathなし、(2)Promptに`B1_B_DIRECT_INSTRUCTION`/`COMMON_BLOCK_TEMPLATE`の文字列が含まれない、(3)contract部分がPhase A確定contractと一致、(4)Production code sha256一致。

## 実行コマンド全文

```
cd C:\Users\tensh\eigo-radio
.venv\Scripts\python.exe er017_news_entertainment_production_line_trial_01.py --out-dir er017_output\news_entertainment_production_line_trial_01 --step research
.venv\Scripts\python.exe er017_news_entertainment_production_line_trial_01.py --out-dir er017_output\news_entertainment_production_line_trial_01 --step write --stages 0,1,2 --level b1
.venv\Scripts\python.exe er017_news_entertainment_production_line_trial_01.py --out-dir er017_output\news_entertainment_production_line_trial_01 --step gates
.venv\Scripts\python.exe er017_news_entertainment_production_line_trial_01.py --out-dir er017_output\news_entertainment_production_line_trial_01 --step downstream --only-if-gates-pass --budget-jpy 250
.venv\Scripts\python.exe er017_news_entertainment_production_line_trial_01.py --out-dir er017_output\news_entertainment_production_line_trial_01 --step side-hook
.venv\Scripts\python.exe run_project_regression.py --pattern "er017*_test_*.py"
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01_phaseB.md --json-out docs\pm\delegation_log\NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01_phaseB.md_check.json
git status --short
```

## SSOT追記文

なし(DECISION_LOG/OPEN_ITEMS/CURRENT_SPECは触らない。並行タスクが編集中)。

## Git(明示add対象・コミットメッセージ・trailer)

明示add: `er017_news_entertainment_production_line_trial_01.py`、`er017_news_entertainment_production_line_trial_01_test_01.py`、`er017_output/news_entertainment_production_line_trial_01/`(配下全て。mp3が生成された場合はサイズを記録し、既存Production記事のaudio artifactと同じ扱いでadd)、`NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01_REPORT.md`(Phase A §A/§Bを保持し、§1〜§21をユーザー指示12節の番号で追記。Fable記入欄§17/§18/§19/§20は`[Fable記入]`)、`docs/pm/delegation_log/NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01_phaseB.md`、同`_check.json`。
メッセージ: `NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01 Phase B: 既存Research/VerificationでVerified Fact Ledger作成→英語Entertainment Writer Prompt+Production contractでOriginal→R1→R2→既存parser/Validator/Deviation/Fact Check→downstream(Meta Muse、Production code変更なし)`
trailer: `Management-ID: NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01`
`index.lock`存在時は10秒待って再試行(最大3回)。STOP時もそこまでの成果物をcommit(メッセージ先頭に`STOP:`)。

## 報告(RESULT_PACKET_ENT項目)

0. T-0結果。
1. Research/Verification: 呼び出した関数・引数・model実値・Web検索回数・費用・所要時間、Ledger保存先、Ledger本文の要約(fact数・source URL一覧)、Productionと同一条件であることの根拠行。
2. 使用Prompt全文(developer/英語Entertainment/contract追加部分/R1・R2指示+contract行)、P7対照表。
3. Stage 0/1/2全文、Title 3件、語数(総/各###節)。
4. Gate結果Stage別(parser/Structure/Deviation[MAJOR/MINOR件数と内容]/Fact Check/Point Overlap QA実行可否)。STOPした場合はどのStage・どの項目・原因・選択肢。
5. downstream到達点(stage別結果、生成物path、Audio有無、Gate/Lock発生有無、theme config作成の有無)。
6. Side Hook結果(hook_ja/used_angle_ja/model/cost)、`R2 Title | Luna Hook`。
7. api_meta全call(model実値・response_id・previous_response_id連鎖・usage・latency・cost)、Step別費用と合計(¥250以内か)。
8. Prompt echo(Stage別)、Fact機械観測(Ledger外の固有名詞・数字・引用の候補、Stage別)。
9. Production code sha256前後一致、`git status --short`でer003/er006/er010/er011/er012に差分なし。
10. 回帰(`er017*_test_*.py`)結果、commit SHA、push結果。
11. 一覧外Read/Grepの理由、想定外事項・STOP条件該当・懸念。

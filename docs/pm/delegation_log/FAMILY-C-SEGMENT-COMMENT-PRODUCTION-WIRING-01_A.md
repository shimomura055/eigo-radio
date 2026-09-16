## 管理ID

`FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-AND-USER-TEST-INVENTORY-01`(委任A: Family C 2仕様のProduction wiring)
並行タスク: 委任B(ユーザー実検証記事一覧のread-only監査)が同時実行中。委任Bは`docs/pm/RESULT_PACKET_UT_INVENTORY.md`・`USER-TEST-INVENTORY-01_REPORT.md`のみ新規作成し、Git操作・SSOT編集・`er013_*`編集を一切行わない。本委任Aはそれら2ファイルに触らない。Git操作は本委任Aのみが行う。報告は`docs/pm/RESULT_PACKET_WIRING_FAMILY_C.md`(新規)へ。`docs/pm/ACTIVE_TASK.md`は本委任Aが上書き。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー正式決定(2026-09-16、Trial-11/12の3 episode試聴OK)により`APPROVED_FOR_PRODUCTION`となったFamily C 2仕様(A: Story TTS segmentation原則、B: A2 Comment理解ガイド型)をFamily Cの正式Production生成経路へ配線し、Gate 3(下記完了判定)を満たせば`PRODUCTION_WIRED`とする。
- 到達上限Status: 両仕様とも`PRODUCTION_WIRED`(完了判定全項目充足時のみ)。1件でも未充足なら`APPROVED_FOR_PRODUCTION / WIRING_INCOMPLETE`として不足項目を明示(自分で`PRODUCTION_WIRED`と宣言するのは全項目の証跡が揃った場合のみ)。
- 禁止: Trial-11/12専用script(`er013_family_c_episode_trial_1[012]_*.py`)にしか仕様が存在する状態、ProductionコードがTrial scriptを暗黙参照(import)する構造、retryだけ新仕様で初回経路が旧仕様、validatorだけ新仕様前提、A2 Comment理解ガイド型のB1 Commentへの適用、Family A/BへのProduction横展開、OPEN-157/158だけに仕様がありCURRENT_SPECに正式仕様がない状態、既存完成episode(Home robots/Memory/Twins、Trial-10/11/12成果物)の再TTS・上書き、記事固有のVoice boundary/scene boundaryを一律固定値で上書き、hard capのValidator実装(語数目安は運用目安・分割理由の記録対象であり生成をブロックしない)、Opus使用、新規仕様Trial、`git add -A`/`stash`/`amend`、wavのcommit。
- 費用上限: ¥25(runtime evidence用の最小限LLM呼び出し[A2 Comment生成1記事分]のみ。TTSは呼ばない)。
- STOP条件(ユーザー指定): Family C Production配線に未承認の新仕様決定が必要/approved仕様と既存Production architectureが重大に衝突/runtime evidence取得に大規模な追加API費用が必要。該当時は`WIRING_INCOMPLETE`で不足と選択肢を報告し停止。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
(保存名: `docs/pm/delegation_log/FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-01_A.md`)

## ユーザー指示(原文)

ユーザー原文(2026-09-16)の本委任該当部分を引用:

---
0. ユーザー正式決定: ユーザーがFamily C Trial-11 / Trial-12の以下3 episodeを試聴し、3本ともOKと判断した。Memory B1/Digital Twins A2/Digital Twins B1。これにより、今回Family CでTrialしていた以下2仕様を正式採用する。

採用仕様A: Family C Story TTS segmentation。基本原則: 同一Voiceの自然な連続性を優先する/不要な短segmentを避ける/Voice変更点では分割する/Comment挿入位置・scene / semantic boundaryを考慮する/word countだけで機械的に細分化しない/概ね100語以内を運用目安とし、120語を大きく超えない/150〜200語級の長segmentは避ける/Voice境界によって不可避な短segmentは許容する。Trialで確認したMemory / Digital Twinsの考え方をFamily C正式仕様とする。

採用仕様B: Family C A2 Comment 理解ガイド型。Family C A2 Commentは、「聞いてみましょう」「耳を澄ませましょう」等のメタナレーションではなく、次の英語理解に必要な具体的contextを短く提供する理解ガイドとする。具体的には必要に応じて、現在の場所・状況/人物関係/場面転換/次の英文理解に重要な行動/選択・対立点を簡潔に日本語で整理する。禁止・回避: 聞いてみましょう/耳を傾けて/耳を澄ませて/注目してみましょう/これからどうなるでしょう/雰囲気だけの抽象的誘導/無内容な予告/結末の先出し/StoryにないFact追加/不要な長文化。

1. Status: Trial終了時点: Story segmentation: VALIDATED/Family C A2 Comment理解ガイド型: VALIDATED。今回のユーザー正式決定により、両方をAPPROVED_FOR_PRODUCTIONへ変更する。ただし、コード変更だけでPRODUCTION_WIREDとしないこと。以下Gate 3をすべて満たした場合のみPRODUCTION_WIREDとする。

2. Production Wiring — 必須: 今回正式採用された2仕様を、Family Cの正式Production生成経路へ配線する。
2-A. Story segmentation: 確認・実装対象: Family C Production正式初回生成経路/A2 / B1双方/Story segment生成/retry/regeneration/fallback/resume / reuse時/Comment挿入境界との整合/Voice assignmentとの整合。Trial-11 / Trial-12専用scriptにしか存在しない状態を禁止する。Trial scriptをProductionコードが暗黙参照する構造にもしてはならない。必須確認: Home Robots/Memory/Digital Twinsで確認したStory構造差を踏まえても、Family C共通原則として破綻しないこと。ただし記事固有のVoice boundaryやscene boundaryを一律固定値で上書きしない。
2-B. A2 Comment理解ガイド型: Family C A2の正式Comment生成Prompt / Contractへ配線する。Trial-11 / Trial-12だけのPromptに残さない。初回生成だけでなく、retry/regeneration/fallbackでも同じ思想が維持されること。B1 Commentへ誤適用しないこと。Family A / Family BへはまだProduction横展開しない。

3. Dangling Reference Check: Production Prompt / code / validator等から、Story segmentation原則/A2 Comment理解ガイド型を参照する場合、参照先が今回正式Production仕様として存在することを確認する。禁止: Trial-only定義をProduction側が参照/retryだけが新仕様を参照し初回経路は旧仕様/validatorだけが新仕様前提/A2 Comment仕様がB1へ誤適用/OPEN-157 / OPEN-158だけに仕様がありCURRENT_SPECに正式仕様が存在しない状態。

4. Production runtime evidence: 実際のFamily C Production正式pathでruntime発火を確認すること。最低限、Story segmentation: 同一Voice連続部の統合原則が実際に適用される/Voice boundaryは保持される/不自然な1〜数語segmentが理由なく生成されない/segment word count / 分割理由を確認可能。A2 Comment: 理解ガイド型Promptが実際に使用される/禁止メタナレーションが出ない/StoryにないFactを追加しない/結末を先出ししない。をruntime evidenceで示す。既存完成episodeを壊す必要はない。無駄な全音声再生成は避ける。必要最小限のProduction runtime evidenceを取得すること。

5. Regression / Test: 必要なRegression / integration testを実施。最低限: Family C A2/Family C B1/Voice境界/同一Voice連続/Comment placement/A2 Comment生成/B1 Comment非影響/retry/fallback整合。既存Home Robots / Memory / Digital Twinsのapproved成果物と矛盾しないこと。

6. SSOT / PM更新: 必須: CURRENT_SPEC.md/DECISION_LOG.md/OPEN_ITEMS.mdを実態に合わせて更新。OPEN-147等: Family C採用判断待ちに関する既存Open Itemがあればclose / update。OPEN-157「全Family共通候補 Story TTS segmentation原則」: これはFamily C採用済みになったが、全Family共通仕様への採用はまだしていない。したがって、Family C: PRODUCTION_WIREDになった場合は正式仕様/他Family: DEFERRED / 次回Trial待ち、と区別する。OPEN-158「全Family共通候補 A2 Comment理解ガイド型」: 同様に、Family C A2: 正式採用/他Family: 次回Trial待ち、として管理する。全Family共通仕様としてcloseしない。

7. Twins A2短segmentのユーザー判断: Trial-12でUSER_DECISION_REQUIREDだった"The door opened."3語segmentについては、今回ユーザーが3 episodeすべてOKと判断したため、現状維持で採用とする。追加再TTS・Comment位置変更は不要。この判断を必要ならDecision Logへ記録し、USER_DECISION_REQUIREDを残さない。

8. Git: 必要なProductionコード・test・SSOT変更をcommit / push。commit hashを報告する。未commit / local-only状態ではPRODUCTION_WIREDとしない。

9. Production Wiring完了判定: 以下すべて満たした場合のみPRODUCTION_WIREDとする。Production正式初回path実装/retry / fallback / regeneration整合/Trial専用script依存なし/runtime evidenceあり/Regression / integration PASS/actual model / routing等必要証跡あり/CURRENT_SPEC更新/DECISION_LOG更新/OPEN_ITEMS更新/Dangling Referenceなし/Git commit / push確認/ユーザー承認内容とProduction挙動一致。1件でも未確認なら、APPROVED_FOR_PRODUCTION / WIRING_INCOMPLETEとして不足項目を明示する。

QCD注意: 不要な再生成禁止/完成音声の再TTS禁止/Opus不要/新規仕様Trial禁止。
STOP条件: Family C Production配線に未承認の新仕様決定が必要/approved仕様と既存Production architectureが重大に衝突/Production runtime evidence取得に大規模な追加API費用が必要。
---

## 事前指定Read一覧

- `CURRENT_SPEC.md`: Grepで`Family C`→全ヒット行(Family CのProduction path定義の有無・Status。Fable把握: 2026-09-15時点でCURRENT_SPECに"Family C"は0件、Family Cは`er012_*`Production runnerの対象外でTrial scriptのみ存在)。Grepで`## |### `で節見出し一覧を取得し、Family C節を新設する位置(Family A/B節の後、既存構造に合わせる)を決める。Grepで`B1 Support|Comment役割(C1〜C4)|A2 Comment|Comment Contract`→既存A2/B1 Comment仕様行(理解ガイド型はFamily C A2限定であり、標準A2/B1 Comment Contractは変更しないことを確認)。
- `er012_b_family_production_runner_01.py`: Grepで`level=|family|def main|argparse`→runner構造(Family Cを組み込むか別runnerにするかの判断材料。既存runnerは編集しない方針: Family Cは独立Production moduleとする)。
- `er013_family_c_episode_trial_12_twins_run.py`: Grepで`def build_all_story_segments_trial12|def plan_segments|segmentation_plan|COMMENT_1_ROLE_JA_TRIAL12|COMMENT_2_ROLE_JA_TRIAL12|COMMENT_3_ROLE_JA_TRIAL12|BANNED|禁止`→segmentation plannerとComment Prompt定数の範囲Read(Production module化する対象。Trial-11 memory版・Trial-12 memory B1版と同一ロジックのはずだが差分があればGrepで比較し統合版を採用)。
- `er013_family_c_episode_trial_12_memory_b1_run.py`: Grepで`def plan_segments|def build_story_segments|classify_quote_voice|" ".join`→B1 segmentation(段落境界空白修正・OPEN-156修正)範囲Read。
- `er013_family_c_episode_trial_11_memory_run.py`: Grepで`def plan_segments|def build_story_segments|COMMENT_1_ROLE_JA_TRIAL11`→差分確認用(範囲Readのみ)。
- `er013_family_c_episode_trial_12_twins_b1_run.py`・`er013_family_c_episode_trial_10_twins_run.py`: Grepで`retry|fallback|regenerate|resume|\.ok|cascade`→retry/regeneration/fallback/resumeがsegment planとComment Promptをどこで参照するか(配線対象)。
- `er013_family_c_future_writer_08_b1.py`: 1-60行(B1 Writer契約、Family C共通module候補の既存例。編集しない)。
- `docs/pm/RESULT_PACKET_T12_TWINS.md`: 8-12行・21-25行(approved segmentationの実績値: Twins A2 22 segment/最長99語、Twins B1 24 segment/最長97語)。`docs/pm/RESULT_PACKET_T12_MEMORY_B1.md`: 8-27行(Memory B1 10 segment/最長91語)。`docs/pm/RESULT_PACKET.md`(Trial-11): 8-27行(Memory A2 10 segment/最長89語)。runtime evidenceの照合基準。
- `docs/pm/PM_GOVERNANCE.md`: Grepで`Dangling Reference`→該当節(チェック手順)、Grepで`Gate 3`→該当節。
- `docs/pm/PM_BRIEF.md`: 135-159行。

## 事前指定Grep一覧+追記位置・更新位置の手順

1. **Family C Production経路の現状確定**: `Glob er013_family_c_*production*.py`、`Grep pattern="family_c|Family C" path=er012_b_family_production_runner_01.py`、`Grep pattern="Family C" path=CURRENT_SPEC.md output_mode=count`。結果を報告(想定: Family C専用Production moduleは未存在、Trial scriptのみ)。
2. **設計(Fable指定、新仕様決定ではなくapproved仕様の配置)**: Family C共通Production module `er013_family_c_production_01.py`を新設し、以下を集約する。(a) `plan_story_segments(paragraphs, speaker_of_paragraph_fn, comment_boundaries, voice_map, *, target_words=100, soft_max_words=120, hard_avoid_words=150)`: 承認原則(同一Voice連続統合/Voice変化点分割/Comment境界分割/scene boundary[呼び出し側が段落indexで渡す]/目安超過時は最も近い段落境界で分割/分割理由を各segmentに記録)。語数は運用目安であり生成をブロックしない(hard_avoid超過は`warning`として記録のみ)。記事固有のVoice/scene boundaryは引数で受け取り固定値で上書きしない。(b) A2 Comment理解ガイド型Contract: `FAMILY_C_A2_COMMENT_ROLE_JA_1/2/3`(Trial-11/12の定数を正本化、記事固有表記指示[例: エコー片仮名]は呼び出し側`extra_instructions`引数で注入)、禁止語句リスト`FAMILY_C_A2_COMMENT_BANNED_PATTERNS`と`check_a2_comment_quality(text)`(禁止語句0件・文字数目安・空でない、をbool+理由で返す。retry/regeneration時も同じ関数で判定)。(c) B1 Commentは既存B1 Support経路(`er003_v1_b1_scaffold_01_generate`)をそのまま使い、本moduleはB1 Comment Promptを提供しない(誤適用防止をコード構造で担保)。(d) 話者判定ヘルパ`classify_quote_voice_window(...)`(OPEN-156修正版)を共通化するが、人物名→Voiceのキーワードは記事側引数。
3. **配線**: 新規Production runner `er013_family_c_production_runner_01.py`(A2/B1をlevel引数で分岐、記事設定[本文path/OUT_DIR/ARTICLE_ID/voice_map/人物キーワード/scene boundaries/日本語タイトル/extra_instructions]をJSON設定ファイル`er013_output/family_c_production/<article>/article_config.json`から読む)を作り、初回生成・retry(既存cascade)・regeneration(`--only-segments`型)・fallback・resume(`.ok`reuse)のいずれもmoduleの`plan_story_segments`と`FAMILY_C_A2_COMMENT_ROLE_JA_*`+`check_a2_comment_quality`を通ることをコード上で確認(Grep`plan_story_segments|check_a2_comment_quality`がrunner内の初回・retry・regeneration各経路にあること)。既存Trial script(10/11/12)は**編集しない**(履歴として残置)。Production moduleはTrial scriptをimportしない(`Grep pattern="import er013_family_c_episode_trial" path=er013_family_c_production_01.py`および`_runner_01.py`が0件)。Trial-10/11/12成果物は無変更(git statusで空)。
4. **runtime evidence(最小限)**: (a) segmentation: runnerの`--plan-only`(TTSなし、¥0)をHome robots A2/B1・Memory A2/B1・Twins A2/B1の6記事に対して実行し、`segmentation_plan.json`(segment id/voice/段落範囲/語数/分割理由/warning)を`er013_output/family_c_production/<article>/evidence/`へ出力。approved成果物(Trial-11 Memory A2 10 seg/Trial-12 Memory B1 10 seg/Twins A2 22 seg/Twins B1 24 seg)と語数・境界を比較し一致または差分理由を報告(Home robotsはTrial-10方式のまま承認済みのため「新原則を適用した場合の計画」として提示のみ、再生成しない)。(b) A2 Comment: runnerの`--comments-only --dry-run-tts`相当でMemory A2の1記事分だけ理解ガイド型Contract経由でComment 1〜3を生成(LLM¥5〜6、TTSなし)、`check_a2_comment_quality`結果・禁止語句0件・使用model/routing(`a2gen.run_support_text`経由、model名)・Promptが`FAMILY_C_A2_COMMENT_ROLE_JA_*`であることのログを`evidence/a2_comment_runtime_evidence.json`へ保存。生成文はTrial-11 Commentと並記(採用済み音声は差し替えない)。
5. **テスト**: `er013_family_c_production_test_01.py`新設: plan_story_segmentsの単体(同一Voice統合/Voice境界分割/Comment境界分割/目安超過分割/短segment許容理由付与/固定値上書きなし)、approved 4 episodeのsegmentation再現(Memory A2/B1・Twins A2/B1のplanが承認成果物のsegment数・最長語数と一致)、A2 Comment quality check(禁止語句検出、B1経路が本Contractを参照しないこと[import/呼び出しGrepベース])、retry/regeneration経路が同一関数を呼ぶこと(モックで呼び出し確認)、Trial script非依存(import文Grep)。既存`er013*_test_*.py`全件も回帰。
6. **Dangling Reference Check**: `docs/pm/PM_GOVERNANCE.md`の手順に従い、CURRENT_SPEC新節→module/runner→test→OPEN-157/158→DECISION_LOGの相互参照が全て実在することを確認(参照先ファイル・関数名・定数名のGrep実在確認、結果表を報告)。
7. **SSOT**: `CURRENT_SPEC.md`にFamily C節を新設(「Family C(Future Story)Production」: 対象要素/Story TTS segmentation原則[承認原則8項目、運用目安100/120/150、hard capではない]/A2 Comment理解ガイド型Contract[役割・禁止語句・B1非適用]/Production経路[module/runner/設定JSON]/Status`PRODUCTION_WIRED`または`APPROVED_FOR_PRODUCTION / WIRING_INCOMPLETE`/根拠Decision/日付、既存節の表形式に合わせる)。標準A2/B1 Comment Contract節・Family A/B節は変更しない。`DECISION_LOG.md`: `Grep pattern="^## FAMILY-C-SEGMENT-COMMENT-TRIAL-12(委任2" `→末尾直後に新エントリ(ユーザー正式決定・APPROVED_FOR_PRODUCTION→配線結果・Gate判定・Twins A2「The door opened.」現状維持採用の記録・runtime evidence・commit)、索引1行。`OPEN_ITEMS.md`(python行末追記): OPEN-147=Family C 2仕様採用済み・配線結果・Status更新(採用判断待ち記述を解消)、OPEN-157/158=「Family C: <PRODUCTION_WIRED/WIRING_INCOMPLETE>(正式仕様、CURRENT_SPEC Family C節)/他Family: DEFERRED、次回Trial待ち」に区別更新(closeしない)。`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`にruntime evidence Comment生成の行を追加。

## 実行コマンド全文

作業ディレクトリ`C:\Users\tensh\eigo-radio`、pythonは`.venv\Scripts\python.exe`。

T-0:
```
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-01_A.md --json-out docs\pm\delegation_log\FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-01_A_check.json
```

runtime evidence(segmentation、¥0、6記事):
```
.venv\Scripts\python.exe er013_family_c_production_runner_01.py --config er013_output\family_c_production\memory\article_config.json --level a2 --plan-only
.venv\Scripts\python.exe er013_family_c_production_runner_01.py --config er013_output\family_c_production\memory\article_config.json --level b1 --plan-only
.venv\Scripts\python.exe er013_family_c_production_runner_01.py --config er013_output\family_c_production\digital_twins\article_config.json --level a2 --plan-only
.venv\Scripts\python.exe er013_family_c_production_runner_01.py --config er013_output\family_c_production\digital_twins\article_config.json --level b1 --plan-only
.venv\Scripts\python.exe er013_family_c_production_runner_01.py --config er013_output\family_c_production\home_robots\article_config.json --level a2 --plan-only
.venv\Scripts\python.exe er013_family_c_production_runner_01.py --config er013_output\family_c_production\home_robots\article_config.json --level b1 --plan-only
```
(B1のplan入力はTrial-10で確定済みの`reader_facing_article_b1.txt`を`article_config.json`の`b1_article_path`で指定。Writer再実行しない。)

runtime evidence(A2 Comment、Memory 1記事、LLMのみ):
```
.venv\Scripts\python.exe er013_family_c_production_runner_01.py --config er013_output\family_c_production\memory\article_config.json --level a2 --comments-only --no-tts --budget-jpy 10
```

Trial script非依存確認:
```
.venv\Scripts\python.exe -c "import re;[print(f, len(re.findall(r'import\s+er013_family_c_episode_trial|from\s+er013_family_c_episode_trial', open(f,encoding='utf-8').read()))) for f in ['er013_family_c_production_01.py','er013_family_c_production_runner_01.py']]"
```
(両方0であること。)

回帰:
```
.venv\Scripts\python.exe run_project_regression.py --pattern "er013*_test_*.py"
```
(新規テスト+既存Family Cテスト全件PASS。Trial-10/11/12成果物無変更: `git status --porcelain er013_output/family_c_episode_trial_10/ er013_output/family_c_episode_trial_11/ er013_output/family_c_episode_trial_12/`が空。)

Dangling Reference Check: `docs/pm/PM_GOVERNANCE.md`該当節に既存ツール/コマンドの指定があればそれを実行、無ければ参照表(参照元→参照先→実在確認結果)をpython Grepで作成し報告。

## SSOT追記文

`DECISION_LOG.md`(Trial-12委任2エントリ末尾直後):
```
## FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-AND-USER-TEST-INVENTORY-01(委任A: Family C 2仕様Production wiring)

- 日付: 2026-09-16
- ユーザー正式決定: Trial-11/12の3 episode(Memory B1/Digital Twins A2/Digital Twins B1)を試聴し3本ともOK→Family C 2仕様(A: Story TTS segmentation原則、B: A2 Comment理解ガイド型)を正式採用、`VALIDATED`→`APPROVED_FOR_PRODUCTION`。Twins A2「The door opened.」3語segmentは現状維持で採用(再TTS・Comment位置変更なし、USER_DECISION_REQUIRED解消)。
- 配線: Family C共通Production module `er013_family_c_production_01.py`(plan_story_segments/FAMILY_C_A2_COMMENT_ROLE_JA_1〜3/check_a2_comment_quality/話者判定ヘルパ)+runner `er013_family_c_production_runner_01.py`(A2/B1、初回・retry・regeneration・fallback・resume全経路が同一module経由)。Trial script非依存(import 0件)。B1 Commentは既存B1 Support経路のまま(本Contract非適用をコード構造で担保)。Family A/Bへは横展開なし。
- runtime evidence: segmentation plan 6記事(<各segment数/最長語数、approved成果物との一致/差分理由>)、A2 Comment(Memory、model=<実名>、禁止語句0件、Contract=FAMILY_C_A2_COMMENT_ROLE_JA_*使用ログ)。費用¥<実測>。
- テスト: `er013_family_c_production_test_01.py` <n>件+既存er013テスト<n>件 全PASS。
- Dangling Reference Check: <結果、参照表はRESULT_PACKET>。
- SSOT: CURRENT_SPEC「Family C(Future Story)Production」節新設、OPEN-147更新、OPEN-157/158をFamily C=<Status>/他Family=DEFERREDに区別更新(closeせず)。
- Gate判定: **<PRODUCTION_WIRED / APPROVED_FOR_PRODUCTION / WIRING_INCOMPLETE(不足: …)>**
- 参照: `docs/pm/RESULT_PACKET_WIRING_FAMILY_C.md`、commit <hash>
```
索引1行。`CURRENT_SPEC.md`Family C節・`OPEN_ITEMS.md`OPEN-147/157/158追記は上記Grep 7のとおり(文言は実結果に合わせ、Statusは完了判定の実結果を書く。未充足なら`APPROVED_FOR_PRODUCTION / WIRING_INCOMPLETE`と不足項目)。
`docs/pm/ACTIVE_TASK.md`: 固定ヘッダ形式で上書き(APPROVED未配線欄にFamily C 2仕様の配線Statusを正確に記載)。

## Git(明示add対象・コミットメッセージ・trailer)

- 明示add対象(wav除外): `er013_family_c_production_01.py`、`er013_family_c_production_runner_01.py`、`er013_family_c_production_test_01.py`、`er013_output/family_c_production/**`(article_config.json・evidence/*.json・comments生成テキスト。mp3/wavは生成しないため無し)、`CURRENT_SPEC.md`、`DECISION_LOG.md`、`OPEN_ITEMS.md`、`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`、`docs/pm/delegation_log/FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-01_A.md`、同`_check.json`、`docs/pm/RESULT_PACKET_WIRING_FAMILY_C.md`。
- **委任Bの成果物(`docs/pm/RESULT_PACKET_UT_INVENTORY.md`・`USER-TEST-INVENTORY-01_REPORT.md`)はaddしない**(Fableが後で別途処理)。`er013_output/family_c_episode_trial_1*/`・`er006_output/`・`er011_output/`の既存M、`docs/pm/ACTIVE_TASK_*.md`/`RESULT_PACKET_*.md`の既存??は触らない。
- コミットメッセージ: `FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-01: Family C Story segmentation原則+A2 Comment理解ガイド型をProduction module/runnerへ配線(<PRODUCTION_WIRED/WIRING_INCOMPLETE>)`
- trailer: `Task-ID: FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-AND-USER-TEST-INVENTORY-01`
- push: `git push origin main`。commit hashを報告。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_WIRING_FAMILY_C.md`に、ユーザー指示18-Aの形式で:
1. T-0結果、Family C Production経路の現状確定結果(Grep 1)
2. Story segmentation: Status/Production初回path(module・runner・関数名)/retry・fallback・regeneration・resume各経路での参照箇所(ファイル:行)/runtime evidence(6記事のplan表: segment数・最短/最長語数・warning件数、approved成果物との一致/差分理由)/tests/CURRENT_SPEC・DECISION_LOG・OPEN_ITEMS更新位置/commit hash
3. A2 Comment理解ガイド型: Status/Production初回path(Contract定数・quality check関数)/retry・regeneration・fallbackでの参照箇所/B1非適用の構造的担保(Grep結果)/runtime evidence(Memory A2 Comment 1〜3全文、Trial-11版との並記、model/routing、禁止語句0件、check結果)/tests/SSOT更新位置/commit hash
4. Dangling Reference Check結果表
5. Gate判定: `PRODUCTION_WIRED`または`APPROVED_FOR_PRODUCTION / WIRING_INCOMPLETE`(不足項目を具体列挙)。完了判定12項目のチェック表(各項目に証跡の所在)
6. Twins A2「The door opened.」現状維持採用のDECISION_LOG記録位置
7. 費用(LLM実費)、Trial-10/11/12成果物無変更確認、回帰結果、commit hash・push結果、残差分要約
8. STOP該当有無、事前指定外Read(理由付き)

ユーザー向け表記は「B1」に統一(「B1B」不使用)。

## 管理ID

`NEWS-META-ENGLISH-ONLY-TRIAL-01`(初回委任)。並行タスクなし。一時ファイルは標準名`docs/pm/ACTIVE_TASK.md`/`docs/pm/RESULT_PACKET.md`を上書きしてよい(ヘッダの「APPROVED未配線」に`NEWS-ITERATIVE-R2-PRODUCTION-WIRING-01`、「UDR-deferred」に`NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01`/`TOPIC-SELECTION-SEARCH-TRIAL-03`を保持)。

## 性質/到達上限Status/禁止事項

- 性質: 原因切り分けTrial。「英語化だけ」を単離(Production構造contractは混ぜない)。到達上限Status=`VALIDATED`。品質の最終判定はユーザー。Production採用なし。
- 禁止事項: Production wiring/Production Prompt変更/Point One・Point Two・`###`・`## In one line`・280〜420語target・B1構造・Production Writer instruction/Verified Fact Ledger/Ledger Deviation Gate/Parser/Structure Validator/Key Phrase/Audio/Scaffold/TTS/Assembly/Web Search/Search改善/Hook改善/retry・fallback変更/英語Prompt追加改善Trial を行わない。**新規Editorial rule(simplify more/use fewer facts/make it more entertaining/start with a concrete scene/avoid explanation/use only one metaphor 等)を追加しない。** 入力Fact・別Source追加禁止。R3生成禁止。Production code・SSOT無変更。既存scriptは変更しない(import/複製のみ)。品質の主観評価はSonnetが行わない。費用上限**¥10**。`git add -A`/`stash`/`amend`禁止。
- 生成前に`NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01`の英語R2や日本語条件2 R2をPromptに参照させない(比較表は生成完了後に作成)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。

## ユーザー指示(原文)

(2026-09-24、管理ID `NEWS-META-ENGLISH-ONLY-TRIAL-01`。要点抜粋。全文は本委任文末尾【ユーザー指示全文】としてdelegation_logへ保存)
- 「Entertainment性低下の主因が『英語化』なのか『Production構造contract』なのかを切り分ける。今回は英語化だけを単離して検証する。」
- 「使用する入力: `NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01`の条件2をそのまま(前回Baselineと同一の2文・209字の日本語素材)。入力Factを追加しない。別Sourceを追加しない。Ledgerを渡さない。Web Searchもしない。」
- 「変えるのは出力言語(日本語→英語)だけ。維持: Theme/元情報/Entertainment Promptの思想/Original→R1→R2/Luna/effort high/previous_response_id連鎖/Revision指示の意味/Fact safety。」
- 「Production構造は禁止。出力はTitle+Body only。」
- 「英語Prompt: 前回VALIDATEDした日本語Entertainment Promptを、意味を変えず英語で使用する。追加のEditorial ruleを入れない。Prompt英訳は文ごとの対応が分かるよう保存する。」
- 「重要: 日本語R2を英訳するのではない。同じ元情報2文→英語Original→英語R1→英語R2として生成する。」
- 「比較対象: 日本語Baseline(条件2 R2)/今回のEnglish Original・R1・R2/参考として`NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01`の英語R2(生成前には参照させない)。」
- 「Fable/Claudeは参考評価を行ってよいが、最終品質判断は必ずユーザーが行う。最終報告では記事全文を提示し、ユーザー判断待ちでSTOPする。」
- STOP条件: 「条件2素材を正確に再利用できない/前回Prompt・Revision指示を確認できない/元情報外Fact追加が発生/English Prompt化で意味が変わる/新仕様判断が必要/Cost上限超過。追加修正を何度も試さない。」
- 費用上限¥10。最終報告16項目(下記「報告」参照)。完了後STOP。

## 事前指定Read一覧

- `er015_output/news_meta_source_volume_format_trial_01/inputs/cond2.md`: 全文(条件2素材、逐語再利用。sha256を記録)。
- `NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01_REPORT.md`: 行329-360(§4 Prompt・Revision指示全文・model/effort/連鎖方式)。日本語条件2 R2全文は生成完了後にのみ行461-522(§5 条件2)から比較表へ転記。
- `docs/evidence/news_iterative_r2_adoption_2026-09-24/prompts.md`: P7逐語(AI電話版)・developer・R1/R2指示(正本)。
- `NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01_REPORT.md`: 行239-260(§2 英語Entertainment Prompt対照表。**P7の文単位英訳を再利用**。行261-266のProduction contractは使わない)。英語R2(行360-388)は生成完了後にのみ比較表へ転記。
- `er015_news_meta_source_volume_format_trial_01.py`: Grep `def cmd_generate|call_fresh|call_with_previous_response_id|developer|STAGE0|template`→生成・連鎖の実装(流用)。
- `er005_output/cost_baseline_01/pricing_snapshot.json`: luna単価。
- `docs/pm/PM_BRIEF.md`: 行151-175。

## 事前指定Grep一覧+追記位置・更新位置の手順

### Prompt(Fable固定)
- developer(英語、P7 developer「あなたは日本語のニュースを分かりやすく面白く伝える書き手です。」の対応): `You are a writer who explains the news clearly and makes it enjoyable to read.`
- user(英語。PRODUCTION-LINE-TRIAL §2の文単位英訳をそのまま使い、**contract行は入れない**。P7の「長さ：800〜1000字」は`Length: about 350–450 words.`(800〜1000字の英語換算。Fable判断、対照表に明記)、「出力はタイトルと本文のみ。」は`Output only the title and the body. Write in English.`に対応させる。「難しい内容は、短く簡単な日本語に言い換えてください。日本語を勉強している外国人が…」は`Rephrase difficult content in short, simple English. Aim for a level that a learner of English can understand by listening to it once.`)。`Theme:`は条件2と同じテーマ文の英訳(`I asked an AI to call a store for me, and it turned out a human was on the line`相当。PRODUCTION-LINE §2のTheme行から括弧内の補足は除き、前回日本語テーマ文と同じ情報量にする)。`[News]`欄=条件2素材(**日本語のまま逐語**。素材は変えない)。
- Prompt対照表: P7各文 | 英訳 | 差異メモ(長さ換算・出力形式の2行のみ差異)を`prompt_alignment.md`へ。
- R1指示(英語、意味同一): `Revise this article to make it more entertaining, without changing the facts.` R2指示: `Revise this article to make it even more entertaining, without changing the facts.`(日本語逐語も併記して保存。userメッセージはこの英文のみ)。
- model=`gpt-5.6-luna`、effort=high、`previous_response_id`連鎖、web_searchなし、schemaなし(プレーンテキスト)。R3なし。

### 生成・保存
- `er015_output/news_meta_english_only_trial_01/`: `input_cond2.md`(sha256一致)、`prompt_developer.txt`/`prompt_user_stage0.txt`/`prompt_r1.txt`/`prompt_r2.txt`、`prompt_alignment.md`、`en_original.md`/`en_revision1.md`/`en_revision2.md`、`titles.json`、`api_meta_stage{0,1,2}.json`(`response.model`・response_id・previous_response_id・usage・latency・cost)、`cost.json`。
- Fact機械観測: 各Stageの固有名詞(大文字始まり語)・数字・引用符内発言を抽出し、条件2素材(日本語)およびその対訳語(Meta/Muse/Reuters/human concierge/contract staff/privacy/rolled back/New York/September 22, 2026)に無いものを列挙→`fact_diff_machine.json`(判定はFable)。
- Prompt echo観測: `Isn't this|kind of interesting|Here's something interesting|これ、ちょっと面白くない`→`prompt_echo.json`。
- 語数(各Stage)→`metrics.json`。
- 生成完了後: `comparison.md`に 日本語条件2 R2全文 | English Original | English R1 | English R2 | (参考)PRODUCTION-LINE英語R2 を並べる。
- REPORT `NEWS-META-ENGLISH-ONLY-TRIAL-01_REPORT.md`: §1 条件2素材/§2 日本語Prompt(P7逐語)/§3 英語Prompt全文/§4 Prompt対照表/§5 English Original/§6 R1/§7 R2/§8 Title変化/§9 日本語条件2 R2との並置/§10 PRODUCTION-LINE英語R2との並置/§11 Fact観測・echo・語数/§12 model・cost・latency/§13 Fable参考評価`[Fable記入]`/§14 原因仮説`[Fable記入]`/§15 Trial分類`[Fable分類待ち]`/§16 USER_DECISION_REQUIRED`[Fable記入]`/§17 Production変更なし。

## 実行コマンド全文

```
cd C:\Users\tensh\eigo-radio
.venv\Scripts\python.exe er015_news_meta_english_only_trial_01.py --out-dir er015_output\news_meta_english_only_trial_01 --stages 0,1,2
.venv\Scripts\python.exe er015_news_meta_english_only_trial_01.py --out-dir er015_output\news_meta_english_only_trial_01 --assemble-only
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\NEWS-META-ENGLISH-ONLY-TRIAL-01.md --json-out docs\pm\delegation_log\NEWS-META-ENGLISH-ONLY-TRIAL-01.md_check.json
git status --short
```

## SSOT追記文

なし。

## Git(明示add対象・コミットメッセージ・trailer)

明示add: `er015_news_meta_english_only_trial_01.py`、`er015_output/news_meta_english_only_trial_01/`(配下全て)、`NEWS-META-ENGLISH-ONLY-TRIAL-01_REPORT.md`、`docs/pm/delegation_log/NEWS-META-ENGLISH-ONLY-TRIAL-01.md`、同`_check.json`。
メッセージ: `NEWS-META-ENGLISH-ONLY-TRIAL-01: 条件2素材(2文)から英語でOriginal→R1→R2を生成し英語化のみを単離(P7英訳、Production contractなし、Luna、Production変更なし)`
trailer: `Management-ID: NEWS-META-ENGLISH-ONLY-TRIAL-01`

## 報告(RESULT_PACKET項目)

0. T-0結果。
1. 条件2素材の逐語一致(sha256)。
2. 英語Prompt全文・対照表(差異行の明示)・R1/R2英文指示。
3. English Original/R1/R2全文(RESULT_PACKETにも転記)、Title 3件、語数。
4. 3 callの`response.model`実値・連鎖確認・usage・latency・cost(¥10以内か)。
5. Fact機械観測・echo観測。
6. `comparison.md`の絶対パス。
7. Production/SSOT無変更、`git status --short`、commit SHA、push結果。
8. 一覧外Read/Grepの理由、STOP該当の有無、懸念。

---
【ユーザー指示全文】(delegation_logへそのまま保存)

管理ID: `NEWS-META-ENGLISH-ONLY-TRIAL-01`

## 目的
Meta Muse/AI電話記事について、Entertainment性低下の主因が「英語化」なのか、「Production構造contract」なのかを切り分ける。今回はまず英語化だけを単離して検証する。Production実装は行わない。

## 背景
日本語Trialでは、参照情報量の増加/Ledger形式への変換 はいずれもEntertainment性低下の主因とは考えにくい結果になった。一方、直近の英語Production-line TrialではEntertainment性が大きく落ちた。したがって次の主因候補は 1.英語化 2.Production構造contract の2つ。今回はこのうち1.英語化だけを見る。

## 使用する入力
`NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01`の条件2をそのまま使用する。つまり前回Baselineと同一の2文・209字の日本語素材(Meta Museの電話代行/一部通話を人間の契約スタッフが担当/「人間コンシェルジュ」/プライバシー懸念/一旦取りやめ)。入力Factを追加しない。別Sourceを追加しない。Ledgerを渡さない。Web Searchもしない。

## 最重要：変えるのは言語だけ
維持するもの: Theme/元情報/Entertainment Promptの思想/Original→R1→R2/Luna/effort high/previous_response_id連鎖/Revision指示の意味/Fact safety。変えるもの: 出力言語を日本語→英語 だけ。

## Production構造は禁止
以下は入れないこと: Point One/Point Two、`###` section、`## In one line`、280〜420語Production target、B1構造、Production Writer instruction、Verified Fact Ledger、Ledger Deviation Gate、Production Parser、Structure Validator、Key Phrase、Audio、Scaffold、TTS、Assembly。出力はTitle+Body onlyとする。

## 英語Prompt
前回VALIDATEDした日本語Entertainment Promptを、意味を変えず英語で使用する。追加のEditorial ruleを入れない。特に今回の結果を良く見せるために simplify more/use fewer facts/make it more entertaining/start with a concrete scene/avoid explanation/use only one metaphor などの新規ルールを追加しない。Prompt英訳は文ごとの対応が分かるよう保存する。

## 生成
Stage 0 English Original/Stage 1 English R1(前回使用したR1 Revision instructionと同じ意味)/Stage 2 English R2(前回使用したR2 Revision instructionと同じ意味)。R3は生成しない。

## 重要
日本語R2を英訳するのではない。必ず、同じ元情報2文→英語Original→英語R1→英語R2として生成する。Productionで実際に想定している「英語で最初から記事を作る」方式を検証するため。

## 比較対象
日本語Baseline(`NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01`条件2 R2)/今回(English Original/R1/R2)/参考として`NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01`の英語R2も並べてよい。ただし今回の原因切り分けを汚さないよう、生成前には参照させない。

## 評価
Fable/Claudeは参考評価を行ってよいが、最終品質判断は必ずユーザーが行う。Fable評価だけでVALIDATED品質/Production採用可/日本語と同等と結論づけない。最終報告では記事全文を提示し、ユーザー判断待ちでSTOPする。

## 観察項目
1.面白い見方が一本に絞れているか 2.説明記事化していないか 3.冒頭で続きを聞きたくなるか 4.不要な一般論が増えていないか 5.比喩・見立てが自然か 6.R1→R2でEntertainment性が上がるか 7.タイトルが強くなるか 8.英語になったことで新聞・教材調へ戻っていないか 9.元情報にないFactが追加されていないか 10.日本語条件2との差がどこに出るか

## Fact Safety
元情報2文にない固有名詞/数字/出来事/発言/因果関係を追加しない。今回Ledgerは使わないため、元情報との直接比較で確認する。

## 原因判定
今回のEnglish R2をユーザーが見て十分Entertainment性がある場合: 英語化そのものは主因ではない可能性が高まる。次の候補: Production構造contract。ただし自動で次Trialへ進まない。English R2が日本語条件2より明確に弱い場合: 英語化/英語Prompt変換を主因候補として残す。この場合も追加Prompt改善Trialを勝手に実施しない。

## 保存
元情報2文/日本語Entertainment Prompt/英語Prompt全文/文単位のPrompt対照/R1指示/R2指示/English Original全文/English R1全文/English R2全文/各Title/model_id/response_id/previous_response_id/tokens/latency/cost/Fact観測結果

## Cost / QCD
Web Search、Ledger、Production Gate、Audio等は不要。最小コストで実施。費用上限¥10以内。超過見込みならSTOP。

## Status
開始時`TRIAL`。最大Status`VALIDATED`。ただし品質の最終判定はユーザー。Fableが良好と判断してもProduction採用しない。

## 非対象
Production wiring/Production Prompt変更/Point One・Point Two追加/In One Line追加/Ledger設計変更/Search改善/Hook改善/Audio生成/retry・fallback変更/英語Prompt追加改善Trial

## STOP条件
条件2素材を正確に再利用できない/前回Prompt・Revision指示を確認できない/元情報外Fact追加が発生/English Prompt化で意味が変わる/新仕様判断が必要/Cost上限超過。追加修正を何度も試さない。

## 最終報告
1.使用した条件2素材 2.日本語Prompt 3.英語Prompt 4.Prompt対照 5.English Original全文 6.English R1全文 7.English R2全文 8.Title変化 9.日本語条件2 R2との比較 10.直近英語Production R2との比較 11.Fact観測 12.model/cost/latency 13.Fable参考評価 14.原因仮説 15.Trial分類 16.USER_DECISION_REQUIRED。完了後はSTOP。記事全文をユーザーへ提示し、品質の最終判断をユーザーに委ねること。

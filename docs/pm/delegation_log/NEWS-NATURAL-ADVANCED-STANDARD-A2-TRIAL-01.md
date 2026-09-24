# NEWS-NATURAL-ADVANCED-STANDARD-A2-TRIAL-01 委任文(Fable→Sonnet、逐語保存)

## 管理ID
`NEWS-NATURAL-ADVANCED-STANDARD-A2-TRIAL-01`(初回委任)。並行タスクなし。一時ファイルは標準`docs/pm/ACTIVE_TASK.md`/`docs/pm/RESULT_PACKET.md`(上書き可)。**`docs/pm/ACTIVE_TASK*.md`/`RESULT_PACKET*.md`はcommitに含めない**(前回`ACTIVE_TASK_RR.md`誤commitあり。今回はその処置もしない)。

## 性質/到達上限Status/禁止事項
- 性質: Trial。News Entertainment英語記事を2段階(Advanced=CEFR B1 / Standard=CEFR A2)として成立させられるか検証。中心仮説「**Simplify the English, not the story.**」到達上限`VALIDATED`(Standardについて)。Advanced Natural(=`NEWS-JA-TO-EN-ADAPTATION-TRIAL-01` arm3 Natural、ユーザー正式採用`APPROVED_FOR_PRODUCTION`、ただし配線未完で`PRODUCTION_WIRED`ではない)は今回変更しない。
- 禁止: 新規Web Search/新規日本語記事の執筆/Production Prompt・routing・retry/fallback・Audio配線の変更/CURRENT_SPECを`PRODUCTION_WIRED`へ更新/Standard Promptの正式採用/SSOT変更/記事要約化/新Fact・新一般論の追加/追加Variation(原則3生成で終了)/既存script変更(importのみ)/`git add -A`・`stash`・`amend`。費用上限**¥5**(Web Searchなし。retryが必要な場合は理由記録、上限内)。
- STOP条件(ユーザー指定): 下水道の正式日本語R2を一意に特定できない/A2化するとStoryが大幅に崩れる/Fact ambiguityを解決できない/A2判定のために仕様変更が必要/追加Variationを試したくなった/Cost超過見込み/Production変更が必要。STOP時は`stop_reason.json`を保存しそこまでをcommit(`STOP:`接頭)。

## 固定ブロック
E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Readを基本、全文Readは逐語入力に使う記事ファイル・Promptファイルのみ許可。G-1: git出力は`--short`/`--stat`で最小化。F-1: transcript退避不要。T-0: 本委任文を`docs/pm/delegation_log/NEWS-NATURAL-ADVANCED-STANDARD-A2-TRIAL-01.md`へ保存し`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行、結果をRESULT_PACKETへ1行記録(FAILでも継続)。

## ユーザー指示(要点、全文は末尾【ユーザー指示全文】)
- Article A 下水道: 既存Entertainment日本語R2完成稿を逐語入力に、A-1 Advanced/B1(Natural English Adaptation、ADAPTATION-TRIAL-01 Natural armと同じ思想・Promptを原則再利用)→A-2 Standard/A2(A-1を基準に英語だけA2へ)。旅行記事は対象外。
- Article B Meta AI Call: 既存採用済みNatural English版(タイトル `"Hello, I'm AI" — A Human Was Behind the AI Phone Call`)を改変せずAdvanced Baselineに固定→B-1 Standard/A2を生成。
- Standardで維持: 中心となる面白い見方/冒頭Hook・expectation/Reveal/Story順序/中心比喩・見立て/山場/必要Fact/Endingの意味/同じEditorial angle。簡略化してよい: vocabulary/syntax(長い従属節分割・1文1メッセージ・重い関係節減・過度な受動態回避・抽象名詞構文→具体動作)。禁止: 要約化(Factの羅列)、Storytelling・見立て・Reveal削除、難しいという理由での面白箇所削除、新一般論・新Fact・Advancedにない説明、子供向け英語、単調な短文羅列、順序変更。
- Model `gpt-5.6-luna` effort high、`response.model`実値保存、fallback発生は明示。
- Ledger: 生成材料として膨らませるためには使わない。Fact drift確認用の参照は可。
- Level比較: word count/平均文長/語彙難度参考値/文複雑さ参考値/既存手段でCEFR推定可能ならその結果(機械判定を最終判断にしない、新規有料サービス・API追加禁止)。
- Fact drift(Advanced→Standard): 人名/会社名/数字/因果/時系列/誰が何をしたか/否定・限定/some・all等の範囲/Privacy等の意味。日本語「通話の一部」のような曖昧表現は勝手に解釈を固定しない。既存Ledgerで確認できる場合は照合。
- 最終報告: 記事全文を必ずユーザーがその場で比較できる形で。

## 事前指定Read一覧
- `docs/evidence/news_iterative_r2_adoption_2026-09-24/README.md`: Grep `下水|sewer|articles/`→下水道R2ファイル名・管理ID・元Trialの特定。該当ファイル(例 `articles/sewer_revision2.md` 相当)を全文Read、sha256を記録。**候補が複数(別Trial artifactにも下水道R2がある等)で正式対象を一意に判断できない場合はSTOP**(`Glob **/*sewer*`・`Grep 下水道 glob="*.md" -l`で存在確認し、README記載のadoption evidence配下の1件が「正式採用Original→R1→R2のR2」と明記されていれば一意とみなす)。
- `er015_output/news_ja_to_en_adaptation_trial_01/`: Glob `*`→arm3(Natural)のPromptファイル(developer/user共通block+NATURAL ENGLISH arm block)を全文Read、逐語再利用。arm3出力(`arms/arm3/*.md`相当)を全文Read→タイトルが`"Hello, I'm AI" — A Human Was Behind the AI Phone Call`であることを確認しsha256記録。これがMeta Advanced Baseline(改変禁止)。
- `er015_news_ja_to_en_adaptation_trial_01.py`: Grep `def call_|responses.create|effort|def _cost|price|def sha256`→API呼び出し・cost集計を流用(import)。
- `er017_output/news_entertainment_production_line_trial_01/ledger/verified_fact_ledger.txt`: 全文(Meta Fact drift照合用。特に「通話の一部」= some calls / parts of calls のどちらがLedger上の事実か確認。生成材料に使わない)。
- 下水道のFact照合用: README/`comparison_and_decision.md`に下水道Source URL・Fact列があればGrep `下水`で該当行のみ(なければ日本語R2本文との照合のみ)。
- `er005_output/cost_baseline_01/pricing_snapshot.json`: luna単価。
- Level指標: `Grep pattern="textstat|flesch|cefr|syllable" -i glob="*.py" -l`→既存実装があれば流用。無ければ標準ライブラリのみで word count/文数/平均文長/平均音節数(簡易ヒューリスティック)/長文(≥20語)比率/従属接続詞・関係詞出現数(that/which/who/although/while/if/because等)を算出。`.venv`に`textstat`が既にあれば(`pip show textstat`で確認、**新規installはしない**)Flesch–Kincaid Gradeも記録。CEFR推定は既存手段が無ければ「なし」と明記。

## 実行手順
### STEP 1 Source特定
上記Readで下水道R2と Meta Advanced Baselineを確定→`sources.json`(管理ID/path/title/sha256)。

### STEP 2 A-1 Advanced(下水道)
ADAPTATION-TRIAL-01 arm3 Promptを逐語再利用(記事本文だけ差替え)。ただしADAPTATION-TRIAL-01の共通blockにはMeta記事固有の「Preserve…」列挙(主役/舞台裏/代役/プライバシー等)が含まれる可能性がある。その場合、Meta固有の列挙部分だけを下水道R2の編集設計に合わせた同形式の列挙に置換し(冒頭の期待→反転→中心比喩→結び、を日本語R2から抽出して記述)、それ以外の文は一字も変えない。置換前後の差分を`prompt_diff_a1.md`に保存。1 call、`gpt-5.6-luna` effort high。出力 `a1_advanced_sewer.md`。

### STEP 3 Standard共通Prompt(記事非依存、A-2/B-1で完全同一)
developer(逐語): `You are an editor who rewrites English feature articles for learners of English at CEFR A2 level, while keeping the article just as enjoyable as the original.`
user(逐語、`{advanced_article}`のみ差替え):
```
Rewrite this English article for an A2-level English learner (CEFR A2).
Simplify the language, not the story.

Preserve the same story structure.
Preserve the same interesting angle.
Preserve the same surprise, in the same place in the story.
Preserve the important metaphor or storytelling device.
Preserve the ending logic.
Do not turn the article into a summary.
Do not remove entertaining details only because they are harder to express. Use simpler vocabulary and grammar instead.
Do not add new facts or explanations.
Keep every fact exactly as it is: names, numbers, who did what, cause and effect, the order of events, negations, and words of scope such as "some" or "all".
Use simple, common words. Prefer short sentences, mostly one idea per sentence. Split long clauses. Avoid heavy relative clauses, heavy passive forms, and abstract noun phrases; say what people do instead.
The English must still sound natural when read aloud. Do not write like a children's book, and do not write a flat list of short sentences.
The article may be a little longer or shorter than the original, but do not shorten it into a summary.

Output only the English title and the English body.

[Article]
{advanced_article}
```
A-2: `{advanced_article}`=a1_advanced_sewer.md → `a2_standard_sewer.md`。B-1: `{advanced_article}`=Meta Advanced Baseline → `b1_standard_meta.md`。各1 call、effort high。Prompt全文を`prompt_standard_common.txt`、A-1 Promptを`prompt_advanced_a1.txt`に保存。

### STEP 4 機械確認
- Level指標(上記)をAdvanced/Standard各記事で算出→`level_metrics.json`/`level_metrics.md`。
- Fact drift(Advanced→Standard、A/B各): 数字・固有名詞(大文字語)・引用符付き語・否定語(not/no/never)・範囲語(some/all/every/only/part)の出現をAdvancedとStandardで抽出比較→`fact_diff_machine.json`。目視で 因果/時系列/誰が何をしたか の対応表(段落単位)→`structure_map.md`(Advanced段落→Standard段落の対応と、Reveal/中心比喩/Ending が同じ位置にあるかを○×)。
- Metaの「通話の一部」: Ledgerでの事実表現を記録し、Advanced(Natural)の"some parts of the calls"がStandardでどう表現されたかを記録(解釈を固定する修正はしない、事実列挙のみ)。
- Story崩れ(Reveal・比喩・Endingのいずれかが消失/順序変更/要約化)を検出した場合はSTOP条件該当として報告(再生成しない)。

### STEP 5 資料
- `comparison_sewer.md`(日本語R2全文→Advanced全文→Standard全文)、`comparison_meta.md`(Advanced全文→Standard全文)。
- `cost.json`(call別 model実値/response_id/tokens/latency/JPY/retry)。
- REPORT `NEWS-NATURAL-ADVANCED-STANDARD-A2-TRIAL-01_REPORT.md`: §1 下水道R2の管理ID/path/hash/§2 下水道R2全文/§3 下水道Advanced全文/§4 下水道Standard全文/§5 Meta Advanced全文(Baseline、hash)/§6 Meta Standard全文/§7 Standard共通Prompt全文+A-1 Prompt全文(差分含む)/§8 Level比較表/§9 Story structure preservation(structure_map)/§10 Fact drift/§11 model_id・effort・cost・latency・tokens・retry/§12 Fable参考評価`[Fable記入]`/§13 Standard Trial status`[Fable記入]`/§14 USER_DECISION_REQUIRED`[Fable記入]`/§15 未解決/§16 Production未配線事項一覧(Advanced Naturalは`APPROVED_FOR_PRODUCTION`だが: 正式path未定・retry/fallback未配線・runtime evidence無し・CURRENT_SPEC/DECISION_LOG未記録・contract付与工程未検証・Audio未配線、を事実列挙)。

## 実行コマンド全文
```
cd C:\Users\tensh\eigo-radio
.venv\Scripts\python.exe er015_news_natural_advanced_standard_a2_trial_01.py --out-dir er015_output\news_natural_advanced_standard_a2_trial_01 --step sources
.venv\Scripts\python.exe er015_news_natural_advanced_standard_a2_trial_01.py --out-dir er015_output\news_natural_advanced_standard_a2_trial_01 --step generate --budget-jpy 5
.venv\Scripts\python.exe er015_news_natural_advanced_standard_a2_trial_01.py --out-dir er015_output\news_natural_advanced_standard_a2_trial_01 --step analyze
.venv\Scripts\python.exe er015_news_natural_advanced_standard_a2_trial_01.py --out-dir er015_output\news_natural_advanced_standard_a2_trial_01 --step assemble
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\NEWS-NATURAL-ADVANCED-STANDARD-A2-TRIAL-01.md --json-out docs\pm\delegation_log\NEWS-NATURAL-ADVANCED-STANDARD-A2-TRIAL-01.md_check.json
git status --short
```

## SSOT追記文
なし(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS無変更)。

## Git
明示add: `er015_news_natural_advanced_standard_a2_trial_01.py`、`er015_output/news_natural_advanced_standard_a2_trial_01/`配下、`NEWS-NATURAL-ADVANCED-STANDARD-A2-TRIAL-01_REPORT.md`、`docs/pm/delegation_log/NEWS-NATURAL-ADVANCED-STANDARD-A2-TRIAL-01.md`、同`_check.json`。
メッセージ: `NEWS-NATURAL-ADVANCED-STANDARD-A2-TRIAL-01: 下水道日本語R2→Advanced(B1 Natural Adaptation)→Standard(A2)、Meta Advanced Baseline→Standard(A2)を生成し、Level指標・Story構造・Fact drift資料を作成(Luna、Production変更なし)`
trailer: `Management-ID: NEWS-NATURAL-ADVANCED-STANDARD-A2-TRIAL-01`

## 報告(RESULT_PACKET項目)
0. T-0結果 1. 下水道R2の管理ID/path/title/hash、Meta Baselineのpath/hash(一意性の根拠) 2. A-1 Promptの再利用状況(Meta固有列挙の置換有無と差分) 3. 生成3本の`response.model`実値/tokens/latency/JPY/retry、合計JPY(¥5以内か) 4. Level比較表 5. structure_map要約(Reveal/比喩/Ending位置の○×) 6. Fact drift要約(「通話の一部」のLedger事実とStandard表現を含む) 7. STOP該当の有無 8. 各記事全文の所在(REPORT §2〜§6) 9. Production/SSOT無変更確認、`git status --short`、commit SHA、push結果 10. 一覧外Read/Grepの理由、Open Item候補(事実列挙)。

---
【ユーザー指示全文】(delegation_logへそのまま保存)
管理ID: NEWS-NATURAL-ADVANCED-STANDARD-A2-TRIAL-01
1. 目的: News Entertainment記事の英語レベルを2段階(Advanced Target B1: NEWS-JA-TO-EN-ADAPTATION-TRIAL-01のNatural English Adaptationを基準、日本語完成記事のEditorial design/Storytellingを維持し自然な英語へAdapt/Standard Target A2: Advancedと同じStory構造・面白さ・見立てを維持し、簡略化するのは主にvocabulary・sentence structure・clause complexity・abstract expressions。記事そのものを要約・単純化してはならない)として成立させられるか検証。中心仮説: Simplify the English, not the story.
2. Status: Natural English Adaptation/Advanced=ユーザー正式採用済み APPROVED_FOR_PRODUCTION、ただしProduction wiring未完でPRODUCTION_WIREDではない。Standard A2=方向性はユーザー承認済み、生成品質未検証。今回最大到達VALIDATED。Standardの具体Promptを勝手にProduction採用しない。
3. 作るもの: Article A 下水道(既存Entertainment日本語R2完成稿をRepoから特定し逐語入力。旅行記事は対象外[楽天等の広告Source contamination]。A-1 Advanced/B1: 日本語R2→Natural English Adaptation、ADAPTATION-TRIAL-01 Natural armと同じ思想・Promptを原則再利用。A-2 Standard/A2: A-1を基準にStory structure/interesting angle/metaphor/surprise/endingを固定したまま英語だけA2へ)。Article B Meta AI Call(既存採用済みNatural English版 "Hello, I'm AI" — A Human Was Behind the AI Phone Call をAdvancedとして改変せずBaseline。B-1 Standard/A2を生成)。
4. Standard A2で維持: 中心となる面白い見方/冒頭Hook・expectation/意外性のReveal/Story順序/中心比喩・見立て/面白さの山場/必要なFact/Endingの意味/Advancedと同じEditorial angle。Metaなら 未来的なAI電話→実は舞台裏に人間→AIが主役・人間がunderstudy→Privacy問題→誰が幕の後ろにいるのか のStory progression維持。
5. 簡略化してよい: Vocabulary(on a user's behalf→for the user 等)/Syntax(長い従属節分割、1文1メッセージ、重い関係節減、過度な受動態回避、抽象名詞構文→具体動作。例 Advanced「If people learned that contract workers had actually listened to and responded to conversations they thought they had left to AI...」→A2「People thought the AI was making the call. But a human worker could hear the conversation and answer it.」)。
6. 禁止: A2=要約版(Factの羅列)禁止。Storytelling削除/見立て削除/Reveal削除/難しいからという理由での削除/新一般論/新Fact/Advancedにない説明/子供向け英語/単調な短文羅列/unnatural learner English/Story順序変更。
7. Standard Prompt設計: 量産前提、個別記事依存にしない。基本思想 Rewrite this English article for an A2-level English learner. Simplify the language, not the story. 明示: Preserve the same story structure/interesting angle/surprise/important metaphor or storytelling device/ending logic. Do not turn the article into a summary. Do not remove entertaining details only because they are harder to express. Use simpler vocabulary and grammar instead. Do not add new facts or explanations. The English must still sound natural when read aloud. Prompt全文をartifactへ保存。
8. Target Level: Advanced=CEFR B1(過度にB2化しない)。Standard=CEFR A2(CEFR conformity>Entertainmentにはしない。両方必要。A2にするためStoryを壊す必要がある場合は勝手に壊さずSTOPまたは問題箇所として報告)。
9. Model: gpt-5.6-luna high effort。実runtime model_id保存。fallback発生は明示。
10. Web/Ledger: 新規Web Search禁止。既存記事・既存Factのみ。既存Verified Fact Ledgerは生成材料として膨らませるためには使わない。Fact drift確認用参照は可。
11. 評価: 最終品質判断はユーザー。Fable/Claude評価は参考。下水道: 日本語R2/Advanced Natural/Standard A2を並べる。Meta: Advanced Natural/Standard A2を並べる。比較項目: 面白さ維持/Story構造同一/Reveal維持/比喩・見立て維持/Ending維持/Standardは明確に易しいか/A2として理解しやすいか/不自然なlearner Englishでないか/Factが消えすぎていないか/新規Fact追加なしか/Audioで一度聞いて理解しやすいか/「簡単なだけの記事」になっていないか。
12. Level比較: word count/average sentence length/vocabulary difficulty参考値/sentence complexity参考値/CEFR推定が既存手段で可能ならその結果。機械判定を最終判断にしない。新しい有料サービス・余計なAPI追加禁止。
13. Fact Drift: 人名/会社名/数字/因果/時系列/誰が何をしたか/否定・限定/some・all等の範囲/Privacy等の意味。日本語「通話の一部」のような曖昧表現は勝手に解釈を固定しない。既存Ledger等で正解確認できる場合は照合。
14. 下水道のSource確認: 既存の正式な日本語Entertainment R2をRepoから特定。似たTrial artifactが複数ある場合は勝手に選ばず管理ID/file path/title/hashを確認。判断不能ならSTOP。新規に日本語記事を書き直さない。
15. Cost/QCD: Web Searchなし。¥5以内。無駄なVariation禁止。Meta Standard 1本+下水道Advanced 1本+Standard 1本、原則計3生成で終了。retry必要時は理由記録。
16. Production変更禁止: Production Prompt変更/routing変更/CURRENT_SPECをProduction Wiredと更新/retry・fallbackへの配線/Audio Production wiring/ユーザー未承認Standard Promptの正式採用。
17. Dangling Reference Check: Storytelling等の原則をProduction側へまだ追加しない。Trial artifact内でpreserve story structure等を使うのは可。正式Production Promptへの参照追加はユーザー評価後。
18. STOP条件: 下水道の正式日本語R2を一意に特定できない/A2化するとStoryが大幅に崩れる/Fact ambiguityを解決できない/A2判定のために仕様変更が必要/追加Variationを試したくなった/Cost超過見込み/Production変更が必要。
19. Closeout: StandardはREJECTED/VALIDATED/USER_DECISION_REQUIRED。Advanced NaturalはAPPROVED_FOR_PRODUCTIONのまま維持。Production正式path・retry/fallback・runtime evidence・SSOT等が未完ならPRODUCTION_WIREDとしない。
20. 最終報告: 下水道日本語R2の管理ID/path/hash/日本語R2全文/下水道Advanced全文/下水道Standard全文/Meta Advanced全文/Meta Standard全文/Standard共通Prompt全文/Level比較/Story structure preservation/Fact drift/model_id・effort/cost・latency・tokens/retry有無/Fable参考評価/Standard Trial status/USER_DECISION_REQUIRED/未解決/Production未配線事項一覧。記事全文を必ずユーザーがその場で比較できる形で報告。完了後STOP。

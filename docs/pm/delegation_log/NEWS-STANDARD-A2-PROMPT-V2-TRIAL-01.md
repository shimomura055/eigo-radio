## 管理ID
`NEWS-STANDARD-A2-PROMPT-V2-TRIAL-01`(初回委任)。**並行タスクあり**: 別sonnet-workerが`TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01`(er016_*、`ACTIVE_TASK_RR`/`RESULT_PACKET_RR`)を実行中。本タスクは標準`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`を使い、er016_*に触らない。commit時`index.lock`は10秒待ち再試行(最大3回)。**`docs/pm/ACTIVE_TASK*.md`/`RESULT_PACKET*.md`/`.env`/er016_*は絶対にaddしない**(並行タスクがstageしている可能性があるため、`git add`は自タスクのパスのみ、`git commit`は`git commit -m ... -- <自タスクのパス>`ではなく、stage状況を`git status --short`で確認し他タスクのstaged変更が混在していれば、自タスクのパスだけを`git commit <paths>`で対象指定してcommitする)。

## 性質/到達上限Status/禁止
- 二部構成: (A) Standard A2 Prompt v2 Trial(到達上限`VALIDATED`、Production採用禁止)+(B) Advanced Natural English AdaptationのSSOT正式記録(ユーザー正式承認済み`APPROVED_FOR_PRODUCTION`、**`PRODUCTION_WIRED`にはしない**)。
- 禁止: 既存Advanced本文の変更/Production Prompt・routing・retry/fallback・Audio配線の変更/Production code側へ新参照追加/追加Variation(原則2 call)/新規Web Search/Fact summary化・短文羅列・幼児向け英語・Story・比喩・Reveal削除・Ending弱化・新規Fact・一般論・語注・難語説明文の追加/個別記事専用Prompt化/Meta Baselineの"some parts of the calls"の修正(既存Open Itemとして保持)/`git add -A`・`stash`・`amend`。費用上限**¥1**(retry必要時はSTOPまたは理由報告、多数試行禁止)。
- STOP条件(ユーザー指定): v2でも簡略化がほぼ起きない/Storyが大幅に壊れる/Fact drift発生/9〜11語達成のため不自然になる/追加Variationを試したくなる/¥1超過見込み/SSOT既存仕様と競合/Open Item重複整理で判断が必要。STOP時は`stop_reason.json`保存、そこまでをcommit(`STOP:`接頭)。**Trial(A)がSTOPしてもSSOT記録(B)はユーザー承認済みのため実施する**(SSOT競合・Open Item整理判断が必要な場合のみ(B)もSTOP)。

## 固定ブロック
E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Read、全文Readは逐語入力の記事・Promptファイルのみ。G-1: git出力は`--short`/`--stat`。F-1: transcript退避不要。T-0: 本委任文を`docs/pm/delegation_log/NEWS-STANDARD-A2-PROMPT-V2-TRIAL-01.md`へ保存し`check_delegation_prompt.py`実行、結果をRESULT_PACKETへ1行(FAILでも継続)。

## ユーザー指示(全文は末尾【ユーザー指示全文】としてdelegation_logへ保存)

## 事前指定Read一覧
- `er015_output/news_natural_advanced_standard_a2_trial_01/`: `comparison_sewer.md`・`comparison_meta.md`(Advanced Baseline本文とv1本文の取得、sha256は`sources.json`と照合)、`prompt_standard_common.txt`(v1、差分記録用)、`level_metrics.json`(v1指標)。
- `er015_news_natural_advanced_standard_a2_trial_01.py`: Grep `def call_|def level_metrics|def fact_diff|def sha256|price`→API呼び出し・Level指標・Fact diff関数を**import流用**(同一関数で再計測すること。変更禁止)。
- `CURRENT_SPEC.md`: Grep `Entertainment生成方式|APPROVED_FOR_PRODUCTION / WIRING INCOMPLETE|Natural English|Adaptation`→既存行(行828付近)の形式と内容を確認。競合(既に英語版生成方式の正式行が存在し内容が異なる等)があればSTOP。
- `DECISION_LOG.md`: Grep `NEWS-ITERATIVE-R2-PRODUCTION-WIRING-01|NEWS-HOOK-POLICY-DECISION-01`→直近エントリ(行9329以降)の形式(見出し・日付・Status・根拠・関連ID)を確認し同形式で追記。
- `OPEN_ITEMS.md`: Grep `OPEN-17[0-9]|配線|WIRING|Entertainment|Ledger|通話の一部|some parts`→最大番号と、Advanced配線に関する既存項目の有無。既存に統合可能なら統合、無ければ新規1件(乱立禁止)。整理に判断が必要(既存項目と範囲が食い違う等)ならSTOP。
- `docs/pm/PM_BRIEF.md`: Grep `SSOT|CURRENT_SPEC|DECISION_LOG`で記録ルール該当行のみ。

## (A) Standard Prompt v2(記事非依存、2記事で完全同一)
developer(逐語): `You are an editor who rewrites English feature articles for learners of English at CEFR A2 level, while keeping the article just as enjoyable as the original.`
user(逐語、`{advanced_article}`のみ差替え):
```
Rewrite this entire article for CEFR A2 learners.
Simplify the English, not the story.

Rebuild the sentences. Do not just replace difficult words. Write every sentence again using simpler grammar and shorter structures.
Aim for an average sentence length of about 9–11 words across the whole article. Some sentences may be longer or shorter; do not force every sentence to the same length.
Use mostly one main idea per sentence. Split long clauses. Do not pack a cause, an extra detail, an exception, and a result into one sentence.
Prefer common, high-frequency English words (roughly the 2,000 most common words).
Keep harder words only when they are necessary to understand the topic (for example, a technical term or a name). Do not add an explanation for a hard word; make the sentences around it simple instead.
Keep the metaphor words when they are simple enough for A2 learners (for example, stage, backstage, lead role, curtain).

Preserve the same story structure, the same interesting angle, the same surprise in the same place, the important metaphor or storytelling device, the same order of information, the same selection of facts, and the same ending logic.
Do not turn the article into a summary.
Do not remove an entertaining detail only because it is harder to express. Say it in simpler English instead.
Do not add new facts, new explanations, or new general observations.
Keep every fact exactly as it is: names, numbers, who did what, cause and effect, the order of events, negations, limitations, and words of scope such as "some" or "all".

The result must still sound natural when read aloud. Do not write like a children's book, and do not write a flat list of short sentences.

Output only the English title and the English body.

[Article]
{advanced_article}
```
- 2 call: 下水道Advanced(A-1)→`a2v2_standard_sewer.md`、Meta Advanced Baseline→`b1v2_standard_meta.md`。`gpt-5.6-luna` effort high、`response.model`実値・tokens・latency・JPY・retryを`cost.json`。Prompt全文を`prompt_standard_v2.txt`、v1との差分を`prompt_diff_v1_v2.md`。
- 機械確認: Level指標(v1と同一関数)をAdvanced/v1/v2の6記事で再計測→`level_metrics.json`/`.md`(平均語/文が9〜11に近づいたか明記)。Fact diff(Advanced→v2、v1同一関数)→`fact_diff_machine.json`。structure_map(段落対応、Reveal/比喩/Ending位置○×、比喩語 stage/backstage/lead role/curtain/main artery/washing machine の保持有無)→`structure_map.md`。Metaの"some parts of the calls"がv2でどう表現されたかを事実列挙(修正しない)。
- 資料: `comparison_sewer_v2.md`(Advanced→v1→v2全文)、`comparison_meta_v2.md`(同)。
- STOP判定: 平均語/文がAdvanced比で1語未満しか下がらない(簡略化ほぼ無し)/Reveal・比喩・Endingのいずれか消失/数字・固有名詞・否定・範囲語のdrift/明らかな不自然さ→STOP報告(再生成しない)。

## (B) SSOT記録(ユーザー承認済み、Trial結果に関わらず実施)
- **CURRENT_SPEC.md**: 「Entertainment生成方式」行の直後に同形式で1行追加(既存行は変更しない): 項目名「Entertainment英語版生成方式(Advanced)」、内容「Advanced = Natural English Adaptation。Target level = CEFR B1。日本語完成Entertainment記事(Original→R1→R2のR2)→Natural English Adaptation(`NEWS-JA-TO-EN-ADAPTATION-TRIAL-01` arm3 Prompt、developer/共通block/NATURAL ENGLISH arm block)。Editorial structure/angle/metaphor/surprise/endingを維持。新規Fact・一般論の追加禁止。」Status「`APPROVED_FOR_PRODUCTION / WIRING INCOMPLETE`(2026-09-24ユーザー正式承認。Production配線未完のため`PRODUCTION_WIRED`ではない)」根拠「NEWS-JA-TO-EN-ADAPTATION-TRIAL-01(Meta)、NEWS-NATURAL-ADVANCED-STANDARD-A2-TRIAL-01(下水道で再現確認)」。Standard(A2)は「Trial中(v1 REJECTED、v2 `NEWS-STANDARD-A2-PROMPT-V2-TRIAL-01`)、未採用」と同行内または隣接行で明記。
- **DECISION_LOG.md**: 直近エントリと同形式で追記: 管理ID`NEWS-STANDARD-A2-PROMPT-V2-TRIAL-01`(記録契機)、決定「User formally approved Natural English Adaptation as Advanced (B1)」、status=`APPROVED_FOR_PRODUCTION`、approval date 2026-09-24、supporting Trial: `NEWS-JA-TO-EN-ADAPTATION-TRIAL-01`(arm3 Natural、Meta)/`NEWS-NATURAL-ADVANCED-STANDARD-A2-TRIAL-01`(sewerで再現確認)、Production wiring incomplete(`PRODUCTION_WIRED`ではない)、Standard v1 REJECTED(簡略化不十分)・v2 Trial中。
- **OPEN_ITEMS.md**: Advanced配線に関する既存項目があれば統合、無ければ新規1件(次番号、例 OPEN-177)「Advanced Natural English Adaptation Production配線残項目」として: Production official initial path wiring/retry・fallback consistency/Production contract(2つの`### `節+`## In one line`)付与/Audio path/runtime evidence/Fact・Ledger consistency(英語化時のLedger照合)/Meta "some parts of the calls" ambiguity(Ledger MUSE-006の読みとの差、一次情報確認待ち、Baseline改変禁止)/final regression・integration tests、をサブ項目列挙。Status OPEN、`USER_DECISION_REQUIRED`ではなく配線作業待ち。
- 追記後、Dangling Reference Check: CURRENT_SPECにNatural English Adaptationが正式仕様として存在し、Production code(`er003_*`/`er012_*`)に新参照を追加していないことを`Grep "Natural English Adaptation" glob="*.py"`=0件で確認。

## REPORT `NEWS-STANDARD-A2-PROMPT-V2-TRIAL-01_REPORT.md`
§1 v2 Prompt全文+v1差分/§2 下水道Advanced全文/§3 下水道v1全文/§4 下水道v2全文/§5 Meta Advanced全文/§6 Meta v1全文/§7 Meta v2全文/§8 Level比較(6記事)/§9 Story preservation/§10 Fact drift(「通話の一部」の扱い含む)/§11 model・cost・latency・tokens・retry/§12 Fable参考評価`[Fable記入]`/§13 Standard v2分類`[Fable記入]`/§14 USER_DECISION_REQUIRED`[Fable記入]`/§15 CURRENT_SPEC更新内容(追記行を逐語)/§16 DECISION_LOG更新内容(逐語)/§17 OPEN_ITEMS更新内容(逐語)/§18 Production未配線一覧/§19 commit・push/§20 未解決。

## 実行コマンド全文
```
cd C:\Users\tensh\eigo-radio
.venv\Scripts\python.exe er015_news_standard_a2_prompt_v2_trial_01.py --out-dir er015_output\news_standard_a2_prompt_v2_trial_01 --step generate --budget-jpy 1
.venv\Scripts\python.exe er015_news_standard_a2_prompt_v2_trial_01.py --out-dir er015_output\news_standard_a2_prompt_v2_trial_01 --step analyze
.venv\Scripts\python.exe er015_news_standard_a2_prompt_v2_trial_01.py --out-dir er015_output\news_standard_a2_prompt_v2_trial_01 --step assemble
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\NEWS-STANDARD-A2-PROMPT-V2-TRIAL-01.md --json-out docs\pm\delegation_log\NEWS-STANDARD-A2-PROMPT-V2-TRIAL-01.md_check.json
git status --short
```

## Git
明示add: `er015_news_standard_a2_prompt_v2_trial_01.py`、`er015_output/news_standard_a2_prompt_v2_trial_01/`配下、`NEWS-STANDARD-A2-PROMPT-V2-TRIAL-01_REPORT.md`、`CURRENT_SPEC.md`、`DECISION_LOG.md`、`OPEN_ITEMS.md`、`docs/pm/delegation_log/NEWS-STANDARD-A2-PROMPT-V2-TRIAL-01.md`、同`_check.json`。
メッセージ: `NEWS-STANDARD-A2-PROMPT-V2-TRIAL-01: Standard A2 Prompt v2(全文再構築・平均9〜11語/文・高頻度語)で下水道/Meta Advancedから生成しv1と比較、Advanced Natural English Adaptationを正式仕様としてCURRENT_SPEC/DECISION_LOG/OPEN_ITEMSへ記録(APPROVED_FOR_PRODUCTION / WIRING INCOMPLETE、Production変更なし)`
trailer: `Management-ID: NEWS-STANDARD-A2-PROMPT-V2-TRIAL-01`
報告にcommit hash・branch・push結果。

## 報告(RESULT_PACKET)
0. T-0 1. Baseline sha256一致確認 2. 2 callの`response.model`実値/tokens/latency/JPY/retry、合計(¥1以内か) 3. Level比較表(6記事、平均語/文の変化) 4. structure_map要約(比喩語保持含む) 5. Fact drift要約 6. STOP該当有無 7. SSOT追記内容(逐語)、OPEN番号、統合/新規の別、Dangling check結果 8. `git status --short`・commit SHA・branch・push 9. 一覧外Read/Grep理由、Open Item候補(事実列挙)。

---
【ユーザー指示全文】(delegation_logへそのまま保存)
管理ID: NEWS-STANDARD-A2-PROMPT-V2-TRIAL-01
1. 目的: Standard A2 Prompt v1がStory構造は維持できたが英語簡略化が不十分だったため、Prompt v2で再検証。目標: Simplify the English, not the story. を維持しつつ、聴いて明確にA2と分かるレベルまで英語を簡略化。
2. 現在Status: Advanced Natural=ユーザー正式採用 APPROVED_FOR_PRODUCTION。今回ユーザー承認: Advanced NaturalをSSOTへ正式記録(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS)。ただしProduction wiring未完なのでPRODUCTION_WIREDには変更しない。Standard Prompt v1=REJECTED(英語の簡略化不十分。Story保持は成功したがAdvancedとの差が小さい)。Standard Prompt v2=今回Trial対象、最大到達VALIDATED、ユーザー承認なしにProduction採用しない。
3. 対象記事: v1と同じ2記事。Article A 下水道: Advanced Natural版を固定Baseline。Article B Meta AI Call: Advanced Natural採用版を固定Baseline。既存Advanced本文を変更しない。
4. Standard Prompt v2必須条件(ユーザー承認済み6条件): (1)平均9〜11語/文(全記事平均、無理に全文同じ長さにしない)(2)1文1メッセージ(長い従属節分割。原因/補足/例外/結果を詰め込まない)(3)最頻出2000語程度を基本(high-frequency vocabulary優先。機械的な完全一致は不要)(4)難語は必要語だけ残す(septic tank/wastewater/Muse/contract worker等は可。必要性の低い難語は平易化)(5)語句置換ではなく全文を書き直す(最重要。Promptで明示: Rewrite the full article for A2 learners. Do not merely replace difficult words. Rebuild the sentences using simpler grammar and shorter structures.)(6)Story構造・比喩・Ending固定(Story progression/Interesting angle/Reveal/Surprise/Important metaphor/Storytelling device/Ending logic/Fact selection/Information order維持。要約しない)。
5. Prompt v2設計: 量産可能な共通Prompt、記事固有hard coding禁止。思想: Rewrite this entire article for CEFR A2 learners. Simplify the English, not the story. Rebuild the sentences. Do not just replace difficult words. Aim for an average sentence length of about 9–11 words. Use mostly one main idea per sentence. Prefer common, high-frequency English words. Keep harder words only when they are necessary to understand the topic. Preserve the same story structure, surprise, metaphor, and ending. Do not turn the article into a summary. Do not remove an entertaining detail only because it is harder to express. Do not add new facts or explanations. The result must still sound natural when read aloud. Prompt全文をartifactへ保存。
6. 禁止: Fact summary化/箇条書き的短文羅列/幼児向け英語/不自然なlearner English/Story削除/比喩削除/Reveal削除/Ending弱化/新規Fact/新規一般論/Advancedにない語注/難語説明のための余計な説明文/個別記事専用Prompt化。
7. 比喩語: v1でMetaの lead role→main part になり見立てが弱くなった。v2では比喩として重要かつ十分平易な語は保持(stage/backstage/lead role/curtain等、A2でも理解可能なら残す)。
8. 難語: 記事固有で必要な難語は残す。難語を残す→説明文追加は禁止。必要なら周囲の文を簡単にして理解可能にする。
9. Model: gpt-5.6-luna effort high。response.model実値保存。fallback発生時は報告。
10. Call数/Cost: 下水道Standard v2+Meta Standard v2、原則2 call。追加Variation禁止。総費用上限¥1。retry必要時はSTOPまたは理由報告、多数試行しない。
11. 評価: 最終判断はユーザー。Fable/Claude評価は参考。比較: 下水道(Advanced Natural/Standard v1/Standard v2)、Meta(同)。項目: v2はv1より明確に易しいか/平均9〜11語/文に近づいたか/1文1メッセージか/語彙が平易か/Story構造維持/比喩維持/Reveal維持/Ending維持/Summary化していないか/Audioで一度聞いて理解しやすいか/不自然な短文列でないか/Fact driftがないか。
12. Level指標: v1と同じ指標を必ず再計測(word count/sentence count/average words per sentence/subordinate markers per 100 words/FK grade)。平均9〜11語/文を重要参考値。数値達成のために不自然な文章にしない。
13. Fact Drift: Advanced→Standard v2で固有名詞/数字/who did what/cause-effect/order of events/negation/scope words/important limitationsを確認。新規Fact追加0を目標。
14. Meta「通話の一部」: 既存Advanced Baselineの some parts of the calls は今回のTrialとは分離。勝手に修正しない。既存Open Itemとして保持。A2 v2ではBaselineの意味をそのまま維持。一次情報確認または別判断が必要。
15. Advanced Natural SSOT反映(ユーザー正式承認済み): CURRENT_SPEC(Advanced=Natural English Adaptation/Target level=B1/Japanese completed Entertainment article→Natural English Adaptation/Editorial structure・angle・metaphor・surprise・endingを維持/Production wiring未完了)。DECISION_LOG(User formally approved Natural English Adaptation/status=APPROVED_FOR_PRODUCTION/approval date/supporting Trial: NEWS-JA-TO-EN-ADAPTATION-TRIAL-01・NEWS-NATURAL-ADVANCED-STANDARD-A2-TRIAL-01/sewerで再現確認済み/Production wiring incomplete)。OPEN_ITEMS(Advancedに残る項目: Production official initial path wiring/retry・fallback consistency/Production contract付与/Audio path/runtime evidence/Fact・Ledger consistency/Meta some parts of the calls ambiguity/final regression・integration tests。既存Open Itemと重複する場合は新規乱立せず統合)。
16. Dangling Reference Check: SSOT記録の際、Natural English AdaptationがProduction正式仕様として存在することを確認。ただしProduction code側へ新しい参照を追加しない。SSOT記録だけを理由にPRODUCTION_WIRED扱いしない。
17. Git: 必要なTrial artifact/SSOT更新をcommit・push。報告: commit hash/branch/push結果。ACTIVE_TASK_RR.md等、別Trialの一時ファイルを今回のcommitに混ぜない。
18. STOP条件: v2でも簡略化がほぼ起きない/Storyが大幅に壊れる/Fact drift発生/9〜11語/文達成のため不自然になる/追加Variationを試したくなる/¥1超過見込み/SSOT既存仕様と競合/Open Item重複整理で判断が必要。
19. Closeout: Standard v2はREJECTED/VALIDATED/USER_DECISION_REQUIRED。良好でもAPPROVED_FOR_PRODUCTIONへ変更しない。最終採否はユーザー判断。Advanced NaturalはAPPROVED_FOR_PRODUCTIONを正式記録、ただしPRODUCTION_WIREDではない。
20. 最終報告: Standard v2 Prompt全文/下水道Advanced全文/下水道Standard v1全文/下水道Standard v2全文/Meta Advanced全文/Meta Standard v1全文/Meta Standard v2全文/v1 vs v2 Level比較/Story preservation/Fact drift/model_id/cost・latency・tokens/Standard v2 Trial分類/USER_DECISION_REQUIRED/CURRENT_SPEC更新内容/DECISION_LOG更新内容/OPEN_ITEMS更新内容/Production未配線一覧/commit hash・push/未解決事項。記事全文は必ずユーザーがその場で比較できる形で報告。完了後STOP。

## 管理ID

`NEWS-JA-TO-EN-ADAPTATION-TRIAL-01`(初回委任)。並行タスクなし。一時ファイルは標準名`docs/pm/ACTIVE_TASK.md`/`docs/pm/RESULT_PACKET.md`を上書きしてよい(ヘッダの「APPROVED未配線」に`NEWS-ITERATIVE-R2-PRODUCTION-WIRING-01`、「UDR-deferred」に`NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01`/`TOPIC-SELECTION-SEARCH-TRIAL-03`/`TOPIC-SELECTION-REFERENCE-PROCESS-TRIAL-01`/`NEWS-META-ENGLISH-ONLY-TRIAL-01`/`NEWS-META-ENGLISH-PROMPT-VARIATION-TRIAL-01`を保持)。

## 性質/到達上限Status/禁止事項

- 性質: Trial。完成した日本語R2(Editorial設計が確立した記事)を英語へAdaptする方式が、英語で最初から書く方式よりEntertainment性を保つかを3 armで検証。到達上限`VALIDATED`。最終品質判断はユーザー。Production採用なし。
- 禁止事項: 新しい日本語記事の生成/Web Search/Ledger/Production構造(Point One・Two/In one line/Key Phrase)/Audio/Production変更/3 arm以外のVariation追加/Fable指定Promptの改変/Revision連鎖(各armは1 callのAdaptのみ)。SSOT無変更。既存script無変更(import/複製のみ)。品質の主観評価はSonnetが行わない(機械観測とブラインド資料のみ)。費用上限**¥10**(3 call、見込み¥1)。`git add -A`/`stash`/`amend`禁止。
- STOP条件(ユーザー指定): 英語化で重大なFact drift/3 Arm以外の追加Variationが必要/元日本語記事の意味解釈が曖昧/¥10超過見込み/Production変更が必要。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。

## ユーザー指示(原文)

(2026-09-24、管理ID `NEWS-JA-TO-EN-ADAPTATION-TRIAL-01`。全文を末尾【ユーザー指示全文】としてdelegation_logへ保存)。要点: 「日本語で『面白さ』を完成させ→英語では新しく記事を考えず、Editorial designを維持したまま自然な英語へAdaptする方式を試す。」「使用する日本語記事: Meta Museの既存日本語R2『「もしもし、AIです」――その声の裏で、人間が代役を務めていた』本文逐語再利用。」「最重要原則: 守るのは日本語の文面ではなくEditorial design(冒頭の『未来の便利なAI電話』という期待/『実は舞台裏に人間がいた』逆転/主役・舞台裏・代役の見立て/主題『AI電話の裏に人間がいた』固定/Privacyは主題でなく後半情報/不要なFact追加なし/終盤で『舞台の上/幕の後ろ』へ戻る/山場/Fact関係)。変えてよい: 文の長さ/語順/段落の切り方/接続表現/日本語特有の省略/不自然な比喩の微調整。」「禁止: 新しい主張・一般論・背景説明・Fact・比喩の大量追加/Privacy主題化/『より良い記事にする』再編集/構成を別物にする。英語側に新たなEditorial judgmentをさせない。」「Arm 1 Faithful(構成・情報順序・比喩・展開・結びを維持、不自然箇所のみ調整)/Arm 2 Balanced(本命。angle・structure・metaphor・information selection・ending logicを維持し、英語の流れ・段落リズム・文構成・反復回避は再構成可)/Arm 3 Natural English(自然さ優先。中心の見立て・主題・Fact・取捨・結論は維持)。」「Model: 全arm gpt-5.6-luna、effort high。Promptに『Do not rewrite the article from scratch. Do not add new ideas. Preserve the Japanese article's editorial angle, structure, and sense of surprise.』相当の制約を入れる。出力はEnglish title+bodyのみ。」「比較: 日本語R2/Arm 1/2/3/参考B・C2。量産観察: call数・latency・token・cost・Prompt長・retry有無・Human Reviewなしで安定するか・Adaptationだけで十分か・原文品質依存度・Fact drift発生率。」「Cost上限¥10。」

## 事前指定Read一覧

- `docs/evidence/news_iterative_r2_adoption_2026-09-24/articles/ai_phone_revision2.md`: 全文(入力の日本語R2。タイトルが『「もしもし、AIです」――その声の裏で、人間が代役を務めていた』であること、元artifact`er015_output/news_iterative_entertainment_trial_02/A_revision2.md`とsha256一致を確認)。
- `er015_output/news_meta_english_prompt_variation_trial_01/arms/B/revision2.md`、`arms/C2/revision2.md`: **生成完了後にのみ**比較表へ転記。
- `er015_news_meta_english_prompt_variation_trial_01.py`: Grep `def call|responses.create|effort|def save_meta`→単発call・保存の実装(流用)。
- `er005_output/cost_baseline_01/pricing_snapshot.json`: luna単価。
- `docs/pm/PM_BRIEF.md`: 行151-175。

## 事前指定Grep一覧+追記位置・更新位置の手順

### Prompt(Fable固定。変更禁止。各armは1 call、Original→Revisionの連鎖なし、web_searchなし、schemaなし)
- developer(3 arm共通): `You are an editor who adapts finished Japanese feature articles into natural English for listeners who are learning English.`
- 共通制約ブロック(3 arm共通、userの先頭):
```
Adapt the Japanese article below into English.

Do not rewrite the article from scratch. Do not add new ideas, claims, background, general observations, examples, or facts that are not in the Japanese article. Preserve the Japanese article's editorial angle, structure, and sense of surprise:
- the opening expectation of a convenient "AI makes the phone call" future;
- the reversal that a human was actually working behind the scenes;
- the framing of lead role / backstage / understudy;
- the theme fixed on "there was a human behind the AI phone call";
- privacy treated as necessary later information, not as the main theme;
- the ending that returns to the image of the stage and what is behind the curtain.
Keep every fact exactly as in the Japanese article. Use short, simple English that a learner could understand by listening once.

Output only the English title and the English body.
```
- Arm 1(Faithful)追加ブロック:
```
Adaptation level: FAITHFUL.
Keep the same paragraph order, the same order of information, the same metaphors, and the same ending. Follow the Japanese sentence by sentence as closely as natural English allows. Change wording only where a literal rendering would be clearly unnatural in English. Do not merge, split, or reorder paragraphs.
```
- Arm 2(Balanced)追加ブロック:
```
Adaptation level: BALANCED.
Keep the editorial angle, the story structure, the metaphors, the selection of information, and the logic of the ending exactly as in the Japanese. Within that, you may reconstruct sentences, adjust paragraph rhythm, and avoid repetition so that the piece reads as if it had been written in English. Do not change what makes the piece interesting.
```
- Arm 3(Natural)追加ブロック:
```
Adaptation level: NATURAL ENGLISH.
Make the piece read like a natural English news feature. Keep the central metaphor, the theme, the facts, the selection of information, and the conclusion. You may reorder, merge, or reshape paragraphs, and adjust the wording of metaphors where English needs it. Still add nothing that is not in the Japanese article.
```
- 末尾(3 arm共通): `[Japanese article]` + 日本語R2全文(タイトル行を含む逐語)。
- model=`gpt-5.6-luna`、effort=high。retryは空出力/API失敗時のみ1回(発生を記録)。

### 保存(`er015_output/news_ja_to_en_adaptation_trial_01/`)
- `input_ja_r2.md`(sha256)、`arms/{arm1,arm2,arm3}/prompt_developer.txt`/`prompt_user.txt`/`output.md`/`api_meta.json`(`response.model`・response_id・usage[input/output/reasoning]・latency・cost・prompt文字数)、`titles.json`、`metrics.json`(語数・段落数)、`cost.json`。
- Fact機械観測`fact_diff_machine.json`: 各armの固有名詞(大文字始まり語)・数字・引用符内発言を抽出し、日本語R2(および対訳語 Meta/Muse/Reuters/human concierge/contract staff/privacy/understudy/stage/backstage)に無いものを列挙。段落数・情報順序の対応(日本語R2の段落→英語の段落の対応表を機械的に[文の主要名詞の一致で]推定し、arm別に`structure_map.json`。判定はFable)。
- 一般論・背景追加の候補: 英語出力中で日本語R2に対応する文が見つからない文を列挙→`unmatched_sentences.json`(観察のみ)。
- ブラインド資料`blind.md`(3 armをX/Y/Zでランダム化、arm名なし)+`blind_key.json`。
- `comparison_all.md`: 日本語R2 | Arm1 | Arm2 | Arm3 | 参考B R2 | 参考C2 R2(生成完了後)。
- REPORT `NEWS-JA-TO-EN-ADAPTATION-TRIAL-01_REPORT.md`: §1 日本語R2全文/§2〜§4 各Arm Prompt全文/§5〜§7 各Arm全文・タイトル・語数/§8 構造対応・未対応文(機械)/§9 参考B・C2の並置/§10 Fact機械観測/§11 cost・latency・token・Prompt長・retry/§12 量産適性の観察(事実のみ: call数1/記事、latency、token、Prompt長、retry有無)/§13 Fable記入欄(参考順位・分類・UDR・未解決)`[Fable記入]`/§14 Production変更なし。

## 実行コマンド全文

```
cd C:\Users\tensh\eigo-radio
.venv\Scripts\python.exe er015_news_ja_to_en_adaptation_trial_01.py --out-dir er015_output\news_ja_to_en_adaptation_trial_01 --arms arm1,arm2,arm3
.venv\Scripts\python.exe er015_news_ja_to_en_adaptation_trial_01.py --out-dir er015_output\news_ja_to_en_adaptation_trial_01 --assemble-only
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\NEWS-JA-TO-EN-ADAPTATION-TRIAL-01.md --json-out docs\pm\delegation_log\NEWS-JA-TO-EN-ADAPTATION-TRIAL-01.md_check.json
git status --short
```

## SSOT追記文

なし。

## Git(明示add対象・コミットメッセージ・trailer)

明示add: `er015_news_ja_to_en_adaptation_trial_01.py`、`er015_output/news_ja_to_en_adaptation_trial_01/`(配下全て)、`NEWS-JA-TO-EN-ADAPTATION-TRIAL-01_REPORT.md`、`docs/pm/delegation_log/NEWS-JA-TO-EN-ADAPTATION-TRIAL-01.md`、同`_check.json`。
メッセージ: `NEWS-JA-TO-EN-ADAPTATION-TRIAL-01: 日本語R2(AI電話代行)をEditorial design維持で英語へAdapt(Faithful/Balanced/Natural 3 arm、Luna、1 call/arm、Production変更なし)`
trailer: `Management-ID: NEWS-JA-TO-EN-ADAPTATION-TRIAL-01`

## 報告(RESULT_PACKET項目)

0. T-0結果。
1. 入力日本語R2のsha256一致。
2. 各Arm Prompt全文(developer/共通ブロック/arm別ブロック)、Prompt文字数。
3. 各Arm出力全文(RESULT_PACKETにも転記)、タイトル、語数、段落数。
4. 3 callの`response.model`実値・usage・latency・cost(¥10以内か)、retry有無。
5. Fact機械観測・構造対応・未対応文(arm別)。
6. `blind.md`/`blind_key.json`/`comparison_all.md`の絶対パス。
7. Production/SSOT無変更、`git status --short`、commit SHA、push結果。
8. 一覧外Read/Grepの理由、STOP該当の有無、懸念。

---
【ユーザー指示全文】(delegation_logへそのまま保存)

管理ID: `NEWS-JA-TO-EN-ADAPTATION-TRIAL-01`

## 目的
日本語でEntertainment性が十分に出た完成記事を先に作り、その後Lunaで英語へAdaptする方式が、英語で最初から記事を書く方式より、Entertainment性を保ちやすいかを検証する。今回はProduction実装ではなくTrial。最大到達Statusは`VALIDATED`。

## 背景
これまでのTrialでは、日本語R2はEntertainment性が高い/英語で最初から生成すると説明記事化しやすい/英語Promptを改善すると一定改善する/ただし日本語R2にはまだ及ばない という結果が出ている。そこで今回は、日本語で「面白さ」を完成させる→英語では新しく記事を考えず、Editorial designを維持したまま自然な英語へAdaptする方式を試す。

## 使用する日本語記事
まずMeta Museの既存日本語R2を使用する。タイトル『「もしもし、AIです」――その声の裏で、人間が代役を務めていた』。本文も既存R2を逐語再利用。新しく日本語記事を生成しない。

## 最重要原則
英語化の際に守るものは、日本語の文面そのものではなく、記事のEditorial designである。必ず維持するもの: 冒頭の「未来の便利なAI電話」という期待/「実は舞台裏に人間がいた」という逆転/主役・舞台裏・代役という見立て/主題を「AI電話の裏に人間がいた」に固定/Privacyは主題ではなく必要な後半情報/不要なFactを追加しない/終盤で「舞台の上・幕の後ろ」の見立てに戻る/元記事のEntertainment性の山場/Fact関係。変えてよいもの: 文の長さ/英語として自然な語順/段落の切り方/接続表現/日本語特有の省略/英語として不自然な比喩の微調整。

## 禁止
英語化の過程で以下をしない: 新しい主張を追加/一般論を追加/説明記事化/元にない背景説明を追加/新しいFactを追加/新しい比喩を大量追加/Privacyを主題化/「より良い記事にする」ための再編集/日本語記事の構成を別物にする。英語側に新たなEditorial judgmentをさせない。

## Trial Arms
同じ日本語R2から3パターン作る。Arm 1 Faithful Adaptation: 日本語の構成/情報順序/比喩/展開/結びをできるだけ維持する。英語として明らかに不自然な箇所だけ調整。目的「どこまで日本語R2をそのまま英語へ移せるか」。Arm 2 Balanced Adaptation(本命候補): 維持=Editorial angle/Story structure/Metaphor/Information selection/Ending logic。一方で英語の自然な流れ/Paragraph rhythm/Sentence construction/Repetition avoidanceは英語として自然になるよう再構成してよい。ただし元記事の面白さの構造を変えないこと。Arm 3 Natural English Adaptation: 英語記事としての自然さをより優先。ただし中心の見立て/主題/Fact/情報の取捨/結論は維持。目的: 英語として自然にする自由度を上げると、どこから日本語R2のEntertainment性が薄れるかを見る。

## Model
全Arm: `gpt-5.6-luna`、effort high。同一条件。

## Prompt設計
各ArmのPrompt全文を保存する。Promptには「Do not rewrite the article from scratch. Do not add new ideas. Preserve the Japanese article's editorial angle, structure, and sense of surprise.」に相当する明確な制約を入れる。ただしArmごとに、自然さと忠実度の強度を変える。

## 出力
各Arm: English title/English body のみ。Production構造は入れない(Point One・Twoなし/In One Lineなし/Ledgerなし/Audioなし/Key Phraseなし)。

## 評価
最終判断はユーザー。Claude/Fableは参考評価のみ。比較対象: 日本語Original R2/Arm 1/Arm 2/Arm 3/参考B(日本語Prompt→英語生成)/参考C2(意味強調英語Prompt)。最低限見る項目: 1.日本語R2の面白さが残っているか 2.英語として自然か 3.見立てが維持されているか 4.説明記事化していないか 5.不要な一般論が増えていないか 6.情報の取捨が維持されているか 7.結びの力が残っているか 8.Fact追加がないか 9.Translation臭が強すぎないか 10.英語だけ読んでも自然なNews featureとして成立するか

## 量産を意識した追加観察
この方式を量産Lineで使えるかも観察する。記録: 1記事あたりcall数/latency/token/cost/Prompt長/追加retryの有無/Human Reviewなしでも安定するか/Adaptationだけで十分か/原文の品質依存度/Fact driftの発生率

## Fact Safety
日本語R2と英語版を直接比較し、固有名詞/数字/出来事/因果/発言/例示 の追加・変質を確認。元の日本語記事にない情報は追加しない。

## Cost
Web Search不要。総費用上限¥10。不要な追加Trialは禁止。

## STOP条件
英語化で重大なFact drift/3 Arm以外の追加Variationが必要/元日本語記事の意味解釈が曖昧/¥10超過見込み/Production変更が必要。その場合はSTOPして報告。

## Trial Closeout
終了時はREJECTED/VALIDATED/USER_DECISION_REQUIREDのいずれか。良いArmがあってもProduction採用しない。ユーザー判断待ちでSTOP。

## 最終報告
1.使用した日本語R2全文 2.Arm 1 Prompt 3.Arm 2 Prompt 4.Arm 3 Prompt 5.Arm 1全文 6.Arm 2全文 7.Arm 3全文 8.日本語Originalとの比較 9.B/C2との比較 10.Fact drift確認 11.cost/latency/token 12.量産適性の参考所見 13.Fable参考順位 14.Trial分類 15.USER_DECISION_REQUIRED 16.未解決事項。完了後STOP。最終品質判断はユーザーが行う。

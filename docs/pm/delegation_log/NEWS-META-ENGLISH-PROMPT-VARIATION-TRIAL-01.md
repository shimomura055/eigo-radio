## 管理ID

`NEWS-META-ENGLISH-PROMPT-VARIATION-TRIAL-01`(初回委任)。並行タスクなし。一時ファイルは標準名`docs/pm/ACTIVE_TASK.md`/`docs/pm/RESULT_PACKET.md`を上書きしてよい(ヘッダの「APPROVED未配線」に`NEWS-ITERATIVE-R2-PRODUCTION-WIRING-01`、「UDR-deferred」に`NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01`/`TOPIC-SELECTION-SEARCH-TRIAL-03`/`TOPIC-SELECTION-REFERENCE-PROCESS-TRIAL-01`/`NEWS-META-ENGLISH-ONLY-TRIAL-01`を保持)。

## 性質/到達上限Status/禁止事項

- 性質: 切り分けTrial。条件2素材を固定し、英語記事のEntertainment性低下が英語Prompt/Revision表現に起因するかを4 arm(A再利用+B/C1/C2/C3新規生成)で比較。到達上限`VALIDATED`。最終品質判断はユーザー。Production採用なし。
- 禁止事項: Production変更/Web Search/Ledger/Production contract(Point One・Point Two・`###`・`## In one line`・280〜420語)/Audio/R3生成/Arm間でPrompt以外の条件を変えること/Fable指定以外のPrompt Variationを増やすこと/Promptの「自由改善」。Arm Aは`NEWS-META-ENGLISH-ONLY-TRIAL-01`の既存artifactを再利用し**再callしない**。品質の主観評価はSonnetが行わない(ブラインド資料作成と機械集計のみ)。費用上限**¥10**(新規9 call、見込み¥1.5)。SSOT無変更。既存script無変更(import/複製のみ)。`git add -A`/`stash`/`amend`禁止。
- STOP条件(ユーザー指定): 素材条件が揃わない/Arm間でPrompt以外の条件が変わる/元情報外Factの重大追加/¥10超過見込み/新しいPrompt Variationを勝手に増やす必要が生じる。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。

## ユーザー指示(原文)

(2026-09-24、管理ID `NEWS-META-ENGLISH-PROMPT-VARIATION-TRIAL-01`。全文を末尾【ユーザー指示全文】としてdelegation_logへ保存)。要点: 「素材は条件2の2文・209字を逐語再利用。固定: 同一素材/Luna/effort high/Original→R1→R2/previous_response_id連鎖/Web Searchなし/Ledgerなし/Production contractなし/Audioなし/Title+Body only/English output。Prompt以外の条件を変えない。」「Arm A: 現行英語Prompt+現行英語Revision(ENGLISH-ONLY-TRIAL-01の再現Baseline、既存artifact再利用)。Arm B: 日本語Prompt+日本語Revision、出力だけ英語。Arm C1: 自然な英語意訳(新しいEditorial principleは追加しない)。Arm C2: 意味強調版(Do not try to explain the entire news story/Choose one most interesting angle/Use only the facts needed/Avoid turning the piece into an explanatory summary。元Promptの重要部分の強度だけ上げる)。Arm C3: Conversation/Storytelling寄り版(友人に話す感覚/新聞・行政資料・教材のようにしない/聞き手が続きを知りたくなる/具体的な出来事・場面として語る。虚構・脚色・架空発言は禁止)。C1/C2/C3ではR1/R2 Revision文もArmの意図に合う自然な英語にする(意味が変わりすぎないように)。各ArmのCore Prompt/R1/R2を全文保存。」「評価: 各ArmのR2全文をユーザーへ提示。Claude/Fableは参考評価のみ。比較: 日本語条件2 R2/A/B/C1/C2/C3。」「総費用上限¥10。既存Aを再利用して節約。」

## 事前指定Read一覧

- `er015_output/news_meta_source_volume_format_trial_01/inputs/cond2.md`: 全文(素材、sha256 `4a2d9f899cc6083eb46cd006d8df1fdb02db10c23bdce020b7d6ee58bf903ecb`と一致確認)。
- `docs/evidence/news_iterative_r2_adoption_2026-09-24/prompts.md`: P7逐語(AI電話版)・developer「あなたは日本語のニュースを分かりやすく面白く伝える書き手です。」・R1「この記事を、事実関係は変えずに、もっとエンターテインメント性の高い記事に修正してください。」・R2「…さらにもっと…」(Arm Bの正本)。
- `er015_output/news_meta_english_only_trial_01/`: `prompt_developer.txt`/`prompt_user_stage0.txt`/`prompt_r1.txt`/`prompt_r2.txt`/`en_revision2.md`/`api_meta_stage2.json`(Arm A=既存artifactをそのままコピー。再call禁止)。
- `er015_news_meta_english_only_trial_01.py`: Grep `def |developer|previous_response_id|effort`→生成・連鎖・保存の実装(流用。Prompt文字列をArmごとに差替え可能な構造にする)。
- `NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01_REPORT.md`: 行461-522(§5 条件2)から日本語条件2 R2全文を**生成完了後にのみ**比較表へ転記。
- `docs/pm/PM_BRIEF.md`: 行151-175。

## 事前指定Grep一覧+追記位置・更新位置の手順

### Arm定義(Fable固定。Sonnetは文言を変更しない。`[News]`欄は4 armとも条件2素材の日本語逐語、`Theme:`/`テーマ：`は4 armとも同じテーマ文[Aと同一の英文`I asked an AI to call a store for me, and it turned out a human was secretly on the line.`、Arm Bのみ日本語版`AIに店への電話を頼んだら、裏では人間が話していた`]。長さ指定は4 armとも「約350〜450語」相当。developerはA/C1/C2/C3=`You are a writer who explains the news clearly and makes it enjoyable to read.`、B=P7 developer逐語)

**Arm A(再利用)**: 既存3ファイルをコピー。再call禁止。

**Arm B(日本語Prompt逐語+出力英語)**: user=P7逐語(prompts.md)。ただし「長さ：800〜1000字」→「長さ：英語で350〜450語程度」、「出力はタイトルと本文のみ。」→「出力はタイトルと本文のみ。**本文とタイトルは英語で書いてください。**」に置換(この2行が唯一の差異、対照表に明記)。R1=「この記事を、事実関係は変えずに、もっとエンターテインメント性の高い記事に修正してください。英語で出力してください。」R2=「この記事を、事実関係は変えずに、さらにもっとエンターテインメント性の高い記事に修正してください。英語で出力してください。」(ユーザー指示文中の短縮形ではなく、VALIDATED時の逐語+出力言語指定1文。REPORTに注記)。

**Arm C1(自然な英語意訳)**: user=
```
Write this news story the way you'd tell a friend: "Hey, did you hear about this? It's kind of interesting."

Don't go for the most surprising fact. Instead, pick the one angle that makes the story most interesting, and build the piece around it. Use only the facts that angle needs — don't try to cover the whole story.

Keep the voice natural and light. It shouldn't read like a newspaper article, an official document, or a school textbook. Put difficult ideas into short, simple English, at a level an English learner could follow by listening just once.

If the story looks like it only matters somewhere far away, connect it once to the reader's own life or to a bigger change in society — but don't stretch it.

Stay strictly factual. Don't invent events or quotes.

Theme: I asked an AI to call a store for me, and it turned out a human was secretly on the line.

Length: about 350–450 words.

Give only the title and the body, in English.

[News]
{cond2}
```
R1=`Make this piece more entertaining, keeping every fact exactly the same.` R2=`Now make it even more entertaining, still keeping every fact exactly the same.`

**Arm C2(意味強調版)**: user=
```
Turn the news below into a piece you'd share with a friend: "Hey, isn't this kind of interesting?"

Do not try to explain the entire news story. Choose the single most interesting angle — not the most surprising fact — and build the whole piece around that one angle. Use only the facts needed for that angle and leave the rest out. Do not let the piece turn into an explanatory summary of the news.

Keep the tone natural and light. Do not write like a newspaper, a government document, or a school textbook. Rephrase difficult content in short, simple English that a learner could understand by listening once.

If the story seems specific to a distant place, connect it once to the reader's life or to a larger social change, without forcing it.

Stick strictly to the facts. Add no fictional events or quotes.

Theme: I asked an AI to call a store for me, and it turned out a human was secretly on the line.

Length: about 350–450 words.

Output only the title and the body, in English.

[News]
{cond2}
```
R1=`Revise this piece to be more entertaining, without changing the facts. Keep it built around the one angle; do not expand it into an explanatory summary.` R2=`Revise it again to be even more entertaining, without changing the facts. Stay on the one angle; still no explanatory summary.`

**Arm C3(Conversation/Storytelling寄り)**: user=
```
Tell this news the way you'd tell a friend over coffee: "Hey, listen to this — it's kind of interesting."

Find the one angle that makes it worth telling, and tell it as something that happened — concrete moments and scenes — rather than as a topic to be explained. Use only the facts that angle needs; don't cover the whole story.

Talk, don't lecture. Keep it natural and light, never like a newspaper, an official document, or a textbook. Make the listener want to hear what happens next. Use short, simple English that a learner could follow by listening once.

If it seems like a faraway story, connect it once to the listener's own life or to a bigger change — no need to force it.

Everything must be true to the facts: no invented events, scenes, or quotes.

Theme: I asked an AI to call a store for me, and it turned out a human was secretly on the line.

Length: about 350–450 words.

Give only the title and the body, in English.

[News]
{cond2}
```
R1=`Tell it again, more entertainingly — same facts, nothing invented.` R2=`Once more, even more entertaining — same facts, nothing invented.`

### 生成・保存(`er015_output/news_meta_english_prompt_variation_trial_01/`)
- 新規script `er015_news_meta_english_prompt_variation_trial_01.py`(ENGLISH-ONLY scriptの生成関数を流用、Arm別Prompt辞書)。B/C1/C2/C3を各3 call(Original→R1→R2、`previous_response_id`連鎖、Luna、effort high、web_searchなし、schemaなし)。Arm Aはコピー。
- 保存: `arms/{A,B,C1,C2,C3}/prompt_core.txt`/`prompt_r1.txt`/`prompt_r2.txt`/`original.md`/`revision1.md`/`revision2.md`/`api_meta_stage{0,1,2}.json`、`titles.json`(arm×段)、`metrics.json`(語数)、`fact_diff_machine.json`(素材外の固有名詞・数字・引用符内発言候補、arm×段。判定はFable)、`prompt_echo.json`(`Isn't this|kind of interesting|Hey,|listen to this|Here's something interesting|これ、ちょっと面白くない`)、`cost.json`(model_idキー集計)。
- **ブラインド資料**: `blind_r2.md`=5 armのR2全文をランダム記号(P/Q/R/S/T)で並べる(arm名・Promptを書かない)。対応表は`blind_key.json`(Fableはblindを先に読む)。
- `comparison_all.md`: 日本語条件2 R2 | A | B | C1 | C2 | C3 のR2全文+Original/R1+タイトル一覧(生成完了後に作成)。
- REPORT `NEWS-META-ENGLISH-PROMPT-VARIATION-TRIAL-01_REPORT.md`: §1 固定条件・素材sha256/§2 各ArmのCore/R1/R2全文と対照メモ(Bの差異2行、C1〜C3がP7のどの文に対応するか)/§3 各Arm Original/R1/R2全文・タイトル/§4 機械集計(語数・echo・Fact候補)/§5 api_meta・cost・latency/§6 比較表(日本語条件2 R2+5 arm R2)/§7 Fable記入欄(参考評価・Status・UDR)`[Fable記入]`/§8 Production変更なし。

## 実行コマンド全文

```
cd C:\Users\tensh\eigo-radio
.venv\Scripts\python.exe er015_news_meta_english_prompt_variation_trial_01.py --out-dir er015_output\news_meta_english_prompt_variation_trial_01 --arms B,C1,C2,C3 --stages 0,1,2 --reuse-arm-a er015_output\news_meta_english_only_trial_01
.venv\Scripts\python.exe er015_news_meta_english_prompt_variation_trial_01.py --out-dir er015_output\news_meta_english_prompt_variation_trial_01 --assemble-only
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\NEWS-META-ENGLISH-PROMPT-VARIATION-TRIAL-01.md --json-out docs\pm\delegation_log\NEWS-META-ENGLISH-PROMPT-VARIATION-TRIAL-01.md_check.json
git status --short
```

## SSOT追記文

なし。

## Git(明示add対象・コミットメッセージ・trailer)

明示add: `er015_news_meta_english_prompt_variation_trial_01.py`、`er015_output/news_meta_english_prompt_variation_trial_01/`(配下全て)、`NEWS-META-ENGLISH-PROMPT-VARIATION-TRIAL-01_REPORT.md`、`docs/pm/delegation_log/NEWS-META-ENGLISH-PROMPT-VARIATION-TRIAL-01.md`、同`_check.json`。
メッセージ: `NEWS-META-ENGLISH-PROMPT-VARIATION-TRIAL-01: 条件2素材固定で英語Prompt表現4 arm(A現行英訳[再利用]/B日本語Prompt+英語出力/C1自然意訳/C2意味強調/C3会話・場面寄り)×Original→R1→R2を比較、ブラインド資料作成(Luna、Production変更なし)`
trailer: `Management-ID: NEWS-META-ENGLISH-PROMPT-VARIATION-TRIAL-01`

## 報告(RESULT_PACKET項目)

0. T-0結果。
1. 素材sha256一致、Arm A再利用(再callなし)の確認。
2. 各ArmのCore/R1/R2全文(RESULT_PACKETにも転記)。
3. 各ArmのR2全文とタイトル(Original/R1タイトル含む)、語数。
4. 9 callの`response.model`実値・連鎖確認・usage・latency・cost(¥10以内か)。
5. Fact機械観測・echo観測(arm×段)。
6. `blind_r2.md`/`blind_key.json`/`comparison_all.md`の絶対パス。
7. Production/SSOT無変更、`git status --short`、commit SHA、push結果。
8. 一覧外Read/Grepの理由、STOP該当の有無、懸念。

---
【ユーザー指示全文】(delegation_logへそのまま保存)

管理ID: `NEWS-META-ENGLISH-PROMPT-VARIATION-TRIAL-01`

目的: Meta Museの条件2素材を固定し、英語記事のEntertainment性低下が、英語Prompt/Revision表現に起因するかを切り分ける。現在Status`TRIAL`。今回到達してよい最大Status`VALIDATED`。Production変更は禁止。

### 固定条件
素材は`NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01`条件2の2文・209字を逐語再利用する。固定: 同一素材/Luna/effort high/Original→R1→R2/previous_response_id連鎖/Web Searchなし/Ledgerなし/Production contractなし/Point One・Point Twoなし/In one lineなし/Audioなし/Title+Body only/English output。Prompt以外の条件を変えない。

### Arm A: 現行英語Prompt＋現行英語Revision
`NEWS-META-ENGLISH-ONLY-TRIAL-01`の再現Baseline。Core Prompt、R1、R2とも前回と完全同一。再生成が不要で既存artifactをそのままBaseline利用できるなら、無駄な再callはしない。

### Arm B: 日本語Prompt＋日本語Revision、出力だけ英語
日本語でVALIDATEDした元Promptをそのまま使用する。R1「もっとエンターテインメント性の高い記事にしてください。」R2「さらにもっとエンターテインメント性の高い記事にしてください。」ただし出力言語のみ明示的にEnglish指定。目的: 指示言語が日本語であること自体が効いているかを見る。

### Arm C1: 自然な英語意訳
日本語Promptの意味・強度を変えず、英語話者に自然なEditorial instructionとして意訳する。直訳調にしない。ただし新しいEditorial principleは追加しない。狙い: 日本語Promptの意図を、自然な英語で最も忠実に再現する。

### Arm C2: 意味強調版
日本語Promptに元々含まれている以下の思想を、英語で少し明示的・強めに表現する: Do not try to explain the entire news story./Choose one most interesting angle./Use only the facts needed for that angle./Avoid turning the piece into an explanatory summary. 新しい思想は追加せず、元Promptの重要部分の強度だけ上げる。

### Arm C3: Conversation / Storytelling寄り版
日本語Promptの、友人に「これちょっと面白くない？」と話す感覚/新聞・行政資料・教材のようにしない/聞き手が続きを知りたくなる/具体的な出来事・場面として語る というニュアンスを、英語で自然に強く出す。ただし虚構・脚色・架空発言は禁止。

### Revision Variation
C1/C2/C3では、Core PromptだけでなくR1/R2 Revision文も、そのArmの意図に合う自然な英語表現にする。ただし各ArmでRevisionの意味が変わりすぎないようにする。各Armについて、Core Prompt/R1 instruction/R2 instruction を全文保存する。

### 重要
C1/C2/C3は単なる単語置換ではなく、明確に異なる英語表現Variationにする。一方で「良くなるように自由改善」しすぎない。比較したいのは、英語のPrompt表現差による生成品質差である。

### 評価
各ArmのR2全文をユーザーへ提示する。Claude/Fableは参考評価のみ。最終品質判断はユーザー。最低限比較: 日本語条件2 R2/A/B/C1/C2/C3。観点: 一つの面白い見方に収束しているか/説明記事化していないか/R1→R2で本当に改善したか/会話的な軽快さ/比喩・見立ての自然さ/不要な一般論/元情報外Fact/タイトルの強さ/英語として自然か。

### Cost
Web Search不要。総費用上限¥10。既存Aを再利用して節約すること。

### STOP条件
素材条件が揃わない/Arm間でPrompt以外の条件が変わる/元情報外Factの重大追加/¥10超過見込み/新しいPrompt Variationを勝手に増やす必要が生じる。終了時: REJECTED/VALIDATED/USER_DECISION_REQUIRED。良いArmがあってもProduction採用しない。ユーザー判断待ちでSTOP。

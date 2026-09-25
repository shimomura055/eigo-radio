## 管理ID
`KEY-PHRASE-LEVEL-SPEC-TRIAL-01`(初回委任)。**並行タスクあり**: 別sonnet-workerが`NEWS-ADVANCED-A2-PRODUCTION-E2E-WIRING-01`(er003_*/er012_*/er012_output/SSOT、標準ACTIVE_TASK/RESULT_PACKET)を長時間実行中。本タスクは`docs/pm/ACTIVE_TASK_KP.md`/`RESULT_PACKET_KP.md`を使い、**er003_*/er012_*/SSOT/Production Prompt/正式経路を一切変更しない**。読み取りは可。commit時`index.lock`は10秒待ち再試行(最大3回)。他タスクのstaged変更が混在していれば自タスクのパスだけを`git commit <paths>`で対象指定。`ACTIVE_TASK*`/`RESULT_PACKET*`/`.env`はaddしない。履歴操作禁止。trailer必須。TTS・音声・playerは一切生成しない。

## 性質/到達上限/禁止
- Trial。到達上限`VALIDATED`。Production採用・配線・retry/fallback/downstream変更・TTS・音声化・player・過去記事一括再生成・新Key Phraseカテゴリ追加・追加Trial禁止。既存Key Phrase Production仕様(`er003_v1_n3_01_scaffold_generate.py`の`run_key_phrases`/`run_key_phrase_selection`のPromptとロジック)は変更しない(隔離したTrial script)。
- **想定ターゲット(下記)をPromptに入れない**(答えの漏洩禁止)。想定セットは評価専用ファイルにのみ保持。
- LLM callは4回(Sewer/Meta × Standard/Advanced)+schema失敗時の同一条件再試行1回まで。`gpt-5.6-luna` effort medium、`response.model`実値記録。費用上限¥20。
- STOP条件(ユーザー指定): 既存Production仕様を変更しないとTrialできない/Phrase選定が構造的に5個出せない/Advanced英語解説が長文化・難化する/想定外の既存仕様競合/1回目の結果から新仕様案を思いついても追加Trialしない。

## 固定ブロック
E-1/D-1/G-1/F-1(前回同一)。T-0: 本委任文を`docs/pm/delegation_log/KEY-PHRASE-LEVEL-SPEC-TRIAL-01.md`へ保存し`check_delegation_prompt.py`実行、結果をRESULT_PACKET_KPへ1行(FAILでも継続)。

## 事前指定Read一覧
- 入力記事(優先順で存在するものを使用し、採用パスとsha256を記録): Meta Advanced=`er012_output/e_family_two_level_wiring_01/meta/b1b/article.md`、Meta Standard=`er012_output/e_family_two_level_wiring_01/meta/a2/article.md`(Production経路で生成済み)。Sewer Advanced=`er012_output/e_family_two_level_wiring_01/sewer/b1b/article.md`が存在すればそれ、無ければ`er015_output/news_natural_advanced_standard_a2_trial_01/a1_advanced_sewer.md`。Sewer Standard=`er012_output/e_family_two_level_wiring_01/sewer/a2/article.md`が存在すればそれ、無ければ`er015_output/news_standard_a2_vocab_6000_cutoff_trial_01/a2v5_standard_sewer.md`。**読み取りのみ、他タスクの出力を変更しない。**
- `er003_v1_n3_01_scaffold_generate.py`: Grep `def run_key_phrases|def run_key_phrase_selection|KEY_PHRASE|keywords_selector|def _call|responses.create|json_schema`→既存仕様(個数・選定基準・出力schema・解説言語)と、API呼び出しヘルパー(importで再利用可、変更禁止)。既存仕様との競合点(個数・Topic Word概念・解説言語)を`conflict_check.md`に事実列挙。
- 既存Key Phrase出力例(比較用): `er012_output/e_family_two_level_wiring_01/meta/b1b/key_phrases/keywords_canonicalized.json`・`meta/a2/key_phrases/keywords_canonicalized.json`(Production既存仕様での選定結果、読み取りのみ)。
- `er005_output/cost_baseline_01/pricing_snapshot.json`: luna単価。
- wordfreq(既導入): Advanced解説の語彙難度チェックに使用(`frequency_rank_top20000.json`を`er015_output/news_standard_a2_vocab_banding_trial_01/`から読み取り)。

## Trial Prompt(記事非依存、逐語。`{article}`のみ差し込み)
developer(共通): `You choose Key Phrases for an English-learning news audio program for Japanese adult learners. The goal of Key Phrases is not only to understand this article, but to take away English that the learner can reuse in other situations.`

user(Standard):
```
Choose exactly 5 Key Phrases from the article below for STANDARD level learners (CEFR A2).

Priorities:
- Reusability: prefer basic expressions that the learner can use again in everyday life or in news on other topics.
- Learning value and natural English chunks (e.g., phrasal verbs, common collocations, useful function phrases).
- Fit for A2 level. Do not choose a word only because it is difficult, and do not choose a word only because it is specific to this article.
- Keep each phrase short: one learning point per phrase. Do not pack two grammar or vocabulary points into one phrase. Do not attach article-specific nouns to a general phrase when the general phrase is the real learning point. Use "..." for a slot when needed (for example, "put ... on hold").
- At most ONE of the 5 may be a Topic Word: a theme-specific word that is worth learning for this article even though it is not a general expression. A Topic Word is optional, not required.

For each phrase give: phrase (as written in the article, with "..." for slots), is_topic_word (true/false), example_sentence (the sentence from the article that contains it), reason_ja (one short line in Japanese on why it was chosen), explanation_ja (a short Japanese explanation of the meaning and how to use it).

Return JSON only: {"key_phrases": [ {...} x5 ]}.

[Article]
{article}
```
user(Advanced):
```
Choose exactly 5 Key Phrases from the article below for ADVANCED level learners (CEFR B1).

Priorities:
- Compared with basic level, prefer slightly more advanced vocabulary, natural collocations, and expressions that are easy to reuse in news or explanatory writing and speech.
- Reusability and learning value come first. Do not choose a word only because it is difficult, and do not choose a word only because it is specific to this article.
- "Advanced" does not mean longer. Keep each phrase about as short as a basic-level phrase: one learning point per phrase. Do not pack two points into one phrase (for example, do not combine "consider" and "replace A with B"). Do not attach unnecessary words when the real learning point is shorter (for example, "take care of", not "take care of the rest"). But keep a natural collocation together when it is worth learning as a unit (for example, "raise privacy concerns").
- Do not fix article-specific nouns into a general phrase if that lowers reusability. Use "A", "B", or "..." for slots (for example, "replace A with B").
- At most ONE of the 5 may be a Topic Word: a theme-specific word that is worth learning for this article even though it is not a general expression. A Topic Word is optional, not required.

For each phrase give: phrase, is_topic_word (true/false), example_sentence (the sentence from the article that contains it), reason_ja (one short line in Japanese on why it was chosen), explanation_en (a short, simple English explanation of the meaning — one sentence, plain words, easier than the phrase itself; not a dictionary definition. Example style: "raise privacy concerns" → "to make people worry about how personal information is used or protected").

Return JSON only: {"key_phrases": [ {...} x5 ]}.

[Article]
{article}
```
json_schema strict: `key_phrases` minItems=maxItems=5、Standardは`explanation_ja`、Advancedは`explanation_en`必須。

## 想定ターゲット(評価専用、`expected_sets.json`に保存。Promptに入れない)
- Sewer Standard: take care of / instead of / keep ... going / treatment plant / sewer(Topic Word)
- Meta Standard: in other words / put ... on hold / raise concerns / there is nothing wrong with ... / AI agent(Topic Word)
- Sewer Advanced: replace A with B / be connected to / main artery / treatment plant / septic tank(Topic Word)
- Meta Advanced: raise privacy concerns / put ... on hold / behind the curtain / personal information / human concierge(Topic Word)

## 実行手順
1. 入力記事の確定(パス・sha256)。`conflict_check.md`(既存Production Key Phrase仕様との相違: 個数・Topic Word・解説言語・選定基準。競合により既存仕様変更が必要ならSTOP)。
2. 4 call実行→`outputs/{sewer,meta}_{standard,advanced}.json`(+raw response、usage、cost、latency、`response.model`)。
3. 機械+目視の一致判定(仮判定、最終はFable/ユーザー): 各Phraseを想定セットと照合し「完全一致/同義・同一学習単位(例: "keep ... going"↔"keep going"、"raise concerns"↔"raise privacy concerns"は学習単位として近いが切り方が異なる点を注記)/不一致」に分類。一致数と判定(PASS≥3/STRONG PASS≥4/FAIL≤2)を各記事×レベルで算出。全体一致率(20個中)。Topic Wordの妥当性(テーマ語として学ぶ価値)を注記。
4. Phrase品質チェック: 学習ポイントの重複(例 be considering replacing…型)/不要語の付加(take care of the rest型)/記事固有名詞の固定化 を目視で列挙。
5. Advanced解説チェック: 語数(目安15語以内)/wordfreq順位でPhrase本体より難しい語が解説に含まれていないか/意味の正しさ(目視)/長文化・難化があればSTOP条件該当として報告。
6. 既存Production Key Phrase結果(Meta b1b/a2の`keywords_canonicalized.json`)との差分を参考表に(仕様の違いを説明、優劣判断はしない)。
7. REPORT `KEY-PHRASE-LEVEL-SPEC-TRIAL-01_REPORT.md`: §1 入力記事・Prompt全文・schema/§2 既存仕様との競合確認/§3 Standard(Sewer/Meta)の5個+選定理由+日本語解説/§4 Advanced(Sewer/Meta)の5個+選定理由+英語解説/§5 一致表と判定(4セット+全体)/§6 不一致Phraseの理由(Sonnet仮分析)/§7 Phrase品質・Advanced解説チェック/§8 Prompt上の問題点候補(事実列挙、追加Trialしない)/§9 既存Production結果との差分(参考)/§10 cost・latency・model実値/§11 Fable参考評価`[Fable記入]`/§12 分類`[Fable記入]`/§13 USER_DECISION_REQUIRED`[Fable記入]`/§14 Production変更ゼロの確認(`git diff --stat`で`er003_*`/`er012_*`/SSOTに差分なし)。

## 実行コマンド全文
```
cd C:\Users\tensh\eigo-radio
.venv\Scripts\python.exe er017_key_phrase_level_spec_trial_01.py --out-dir er017_output\key_phrase_level_spec_trial_01 --step inputs
.venv\Scripts\python.exe er017_key_phrase_level_spec_trial_01.py --out-dir er017_output\key_phrase_level_spec_trial_01 --step run --budget-jpy 20
.venv\Scripts\python.exe er017_key_phrase_level_spec_trial_01.py --out-dir er017_output\key_phrase_level_spec_trial_01 --step evaluate
.venv\Scripts\python.exe er017_key_phrase_level_spec_trial_01.py --out-dir er017_output\key_phrase_level_spec_trial_01 --step assemble
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\KEY-PHRASE-LEVEL-SPEC-TRIAL-01.md --json-out docs\pm\delegation_log\KEY-PHRASE-LEVEL-SPEC-TRIAL-01.md_check.json
git status --short
```

## SSOT追記文
なし。

## Git
明示add: `er017_key_phrase_level_spec_trial_01.py`、`er017_output/key_phrase_level_spec_trial_01/`配下、`KEY-PHRASE-LEVEL-SPEC-TRIAL-01_REPORT.md`、`docs/pm/delegation_log/KEY-PHRASE-LEVEL-SPEC-TRIAL-01.md`、同`_check.json`。**他タスクのファイル(er003_*/er012_*/er012_output/SSOT)は絶対にaddしない。**
メッセージ: `KEY-PHRASE-LEVEL-SPEC-TRIAL-01: Key Phraseのレベル別選定・解説方針(汎用性優先・Topic Word最大1・Standard日本語解説/Advanced平易英語解説)を隔離Trialで実装し、Sewer/Metaで想定セットとの一致を評価(Luna 4 call、Production変更なし)`
trailer: `Management-ID: KEY-PHRASE-LEVEL-SPEC-TRIAL-01`

## 報告(RESULT_PACKET_KP)
0. T-0 1. 入力記事パス・sha256 2. 競合確認の結論(STOP該当有無) 3. 4セットの実際の5個(転記)と一致数・判定、全体一致率 4. 不一致理由・Phrase品質・Advanced解説チェックの要点 5. `response.model`実値・cost合計 6. Production変更ゼロ確認(`git diff --stat`) 7. `git status --short`・commit SHA・push 8. 一覧外Read理由、Prompt問題点候補(事実列挙)。

---
【ユーザー指示全文】(delegation_logへ保存)
KEY-PHRASE-LEVEL-SPEC-TRIAL-01。目的: Key Phrasesの新しい選定・解説方針をTrial実装し、既存2記事で、我々が狙うKey Phraseが安定して出力されるか確認する。今回はTrialのみ。Production正式採用・Production wiringは行わない。対象記事: Sewer記事/Meta AI Phone記事。共通思想: Key Phrasesは「記事理解のためだけの補助語彙」ではなく、この記事をきっかけに、別の場面でも使える英語を持ち帰ることを主目的とする。選定では汎用性/学習価値/自然な英語のまとまり/対象レベルへの適合/難しいだけ・記事固有なだけの語を優先しない。5個選定。Topic Wordは最大1個まで可、必須ではない(その記事では学ぶ価値が高いが一般的な重要表現とは言いにくいテーマ固有語を救う枠。別コーナーにはせず5個の中に含める)。Standard(旧A2、今後表示・仕様上はStandard): 基本的で再利用しやすい表現を優先/日常・ニュースの別テーマでも使えるものを優先/難語を拾うこと自体を目的にしない。想定例 Sewer: take care of/instead of/keep ... going/treatment plant/sewer(Topic Word)。Meta: in other words/put ... on hold/raise concerns/there is nothing wrong with .../AI agent(Topic Word)。Standardの解説言語は日本語。Advanced(旧B1、今後表示・仕様上はAdvanced): Standardより、やや高度な語彙/自然なコロケーション/ニュース・説明文で再利用しやすい表現を優先。長い表現を選ぶことをAdvanced化とはしない。Phrase長はStandardと同程度でよい。複数の学習ポイントを1つに詰め込まない(悪い例: be considering replacing ... with ... → replace A with B程度にする)。take care of the restのように本質がtake care ofなら不要な語を付けない。raise privacy concernsのように自然なコロケーションとしてまとまりで覚える価値が高い場合はつなげてよい。記事固有の名詞まで不用意に固定し汎用性を落とさない。想定例 Sewer: replace A with B/be connected to/main artery/treatment plant/septic tank(Topic Word)。Meta: raise privacy concerns/put ... on hold/behind the curtain/personal information/human concierge(Topic Word)。Advancedの解説は英語。内容を簡単に、簡潔に。Key Phrase自体より一段やさしい英語で説明(例: raise privacy concerns → to make people worry about how personal information is used or protected)。辞書的に硬くしすぎず意味がすぐ取れる短い説明。Trial判定基準: 完全一致は求めない。想定Key Phraseとの一致を評価。各記事・各レベル: PASS=5個中3個以上一致/STRONG PASS=4個以上/FAIL=2個以下。Topic Wordは一致必須ではないが、選ぶ場合は「この記事で学ぶ価値のあるテーマ語」として妥当であること。全体: 対象セットで60%以上の一致を目安。文字列一致だけでなく同義・ほぼ同じ学習単位/汎用性/レベル適合/Phraseの切り方を見て評価。Advancedの英語解説は短い/簡単/意味が正しい/Phraseより難しくなりすぎていないを確認。対象範囲: Trial用のPrompt・選定ロジックの最小変更/Sewer・MetaでのStandard・Advanced出力/結果比較/Trial結果の記録。非対象: Production正式Promptへの採用/正式経路への配線/retry・fallback・downstreamのProduction変更/TTS生成/音声化/player生成/過去記事の一括再生成/新Key Phraseカテゴリ追加/勝手な追加Trial。Status: Trial実施承認済み。到達はVALIDATED/REJECTED/USER_DECISION_REQUIREDのみ。APPROVED_FOR_PRODUCTION/PRODUCTION_WIREDへ進めない。結果が良くてもProduction実装しない。実装上の注意: 既存Key Phrase Production仕様を壊さないようTrialは可能な限り隔離。既存Production Promptや正式経路を直接変更する必要がある場合はSTOPして報告。既存Key Phrase仕様・選定ロジックとの競合がないか確認。報告内容: Standard/Advancedそれぞれの実際の5個/各Phraseの短い選定理由/Advanced英語解説/想定セットとの一致数/PASS・STRONG PASS・FAIL/不一致Phraseの理由/Prompt上の問題点とその原因/Trial最終Status/USER_DECISION_REQUIREDの残件/Production変更がゼロであることの確認。STOP条件: 既存Production仕様を変更しないとTrialできない/Phrase選定が構造的に5個出せない/Advanced英語解説が長文化・難化する/想定外の既存仕様競合/1回目の結果を見て新しい仕様案を思いついても勝手に追加Trialしない。

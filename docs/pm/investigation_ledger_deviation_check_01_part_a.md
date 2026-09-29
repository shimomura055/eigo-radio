# LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01 Part A

現行 Ledger Check(JA側 Fact Check)/ Deviation Check(EN側)の役割整理・
hard/soft 区別・信頼性の最低ライン・Hormuz 事例 trace(read-only 調査、
2026-09-29、管理ID `LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01` 委任_01)。

**本ファイルは論点整理のみ。新Checker仕様・閾値・Prompt・判定ロジックの
採用提案・Production変更提案は書かない。**

ユーザー向け表記は Standard/Advanced(内部名 A2/B1B を併記)。

---

## 0. まず結論の要約(両者は何が同じで何が違うか)

**最重要の事実確認**: JA側「Fact Check」とEN側「Deviation Check」は、
**実装上まったく同一の1つの関数**
`er003_v1_en_direct_vfl_01_generate.py::run_deviation_check()`
(以下 `vfl01.run_deviation_check()`)である。同じPrompt本文・同じ10カテゴリ
判定基準・同じMAJOR/MINOR閾値・同じpost-hoc降格ロジックを、**JA記事**に
適用するか**EN記事(Advanced/Standard)**に適用するかの違いしかない。
「JA側が甘い基準・EN側が厳しい基準」という設計上の二段階(2段構え)は
存在しない(コード上そのような分岐は無い)。

| 項目 | JA側(Ledger Check / Fact Check) | EN側(Deviation Check) |
|---|---|---|
| 呼び出す関数 | `vfl01.run_deviation_check()`(同一) | `vfl01.run_deviation_check()`(同一) |
| Prompt/10カテゴリ/閾値 | 同一(`DEVIATION_PROMPT_TEMPLATE`) | 同一 |
| 検証対象テキスト | JA Original / JA R2 | Advanced(English忠実英訳)/ Standard(A2) |
| 参照するLedger | Full Ledger(同一) | Full Ledger(同一) |
| `origin`判定(ja_source/translation) | 行わない(`source_article_text`未指定) | 行う(`source_article_text=ja_text`指定) |
| MAJOR時の挙動 | must-fix 1回retry→なおMAJORなら`JAFactCheckStopError` | must-fix 1回retry→なおMAJORなら`RuntimeError`。ただし`origin=ja_source`が1件でもあれば retryせず即`JARecheckRequiredError`でSTOP |
| Standard(A2)側の扱い | (該当なし、JAは1系統のみ) | Advancedと**全く同一ロジック**でDeviation Check実施(後述1-4) |

「両者で結果が食い違う」という事象(第7章のHormuz事例)は、**基準が違う
から**ではなく、**同一の基準・同一のLLM判定機構が、JA記事に対して行った
判定とEN記事(内容はほぼ翻訳版)に対して行った判定とで、結果が一致
しなかった**という、LLM-as-judge固有の**実行間の非決定性/一貫性**の
問題として観察された(第7章で実データを提示。ER-009-N1-LEDGER-DEVIATION-
RECALIBRATION-02[2026-08-29]でも「実行ごとの非決定性はv2でも解消されて
いない」と既に明記されている、`DECISION_LOG_HISTORY.md:5963`該当行)。

---

## 1. 現行 Ledger Check / Deviation Check の正確な役割整理

### 1-1. Verified Fact Ledgerの構造(Researcher→Verification→Ledger確定)

主要ファイル: `er003_v1_en_direct_vfl_01_generate.py`(以下`vfl01`、
961行)。Family X(`er019_family_x_entertainment_production_runner_01.py`)
はこの`vfl01`のprompt/schema/関数を**そのままimportして再利用**しており、
`er012_e_family_entertainment_two_level_runner_01.py::run_researcher_for_topic()`
(L160-180)/`run_verification_for_topic()`(L183-203)も`vfl01.build_researcher_prompt`
/`vfl01.RESEARCHER_DEVELOPER_MESSAGE`/`vfl01.FACT_LEDGER_JSON_SCHEMA`を
直接呼んでおり、独自のprompt改変は無い(確認済み、`er012_e...py:160-228`)。

各Factのfield(`vfl01.py:78-126` `FACT_LEDGER_JSON_SCHEMA`、
sha未取得[構造体のためsha256対象はprompt文字列のみ計測]):
- `fact_id`/`claim`/`subject`: Factの識別・主張・主体
- `date_or_period`/`scope`/`conditions`: 時期・対象範囲・成立条件
- `numeric_value`/`numeric_scope`: 数値と、その数値が指す母集団
- `causal_strength`(`OBSERVED_REPORTED`/`CORRELATIONAL`/
  `CAUSAL_STATED_BY_SOURCE`/`NOT_APPLICABLE`): 観察・相関・
  Source自身の因果主張の区別
- `source_title`/`source_url`/`source_type`/`support_level`: 出典情報
- `ambiguity`: 曖昧さの明記
- `notes_for_writer`: **Researcherがwriterへ向けて書く自由記述の注記**
  (第2章で詳述)

Researcher Prompt(`RESEARCHER_PROMPT_TEMPLATE`、
sha256=`023f6d96e17ab4a29a8cdcb7c1e79dc92b738aca48b8371cadc6f5f70b0c33b0`、
`vfl01.py:133-163`)は、`notes_for_writer`の意図を明示している(`vfl01.py:157`
逐語): 「観察・相関・因果の区別: (中略)Sourceより強い因果表現
(caused/produced/proved等)を後工程のwriterが使わないよう、
causal_strengthとnotes_for_writerで明示する」。**つまりnotes_for_writer
は設計時点でwriterへの執筆ガイダンスとして構想されたフィールドである**
(この位置付けは第2章のhard/soft論点と直結する)。

Verification(`vfl01.py:195-272`)は独立Web検索でFactを
VERIFIED/AMBIGUOUS/REJECTEDに判定し、`build_verified_ledger_text()`
(`vfl01.py:275-305`)がkept facts(REJECTEDのみ除外)をテキスト化する。
この際`notes_for_writer`はfactごとの他フィールド(scope/numeric_value等)
と**同列の1行**としてLedgerテキストへ埋め込まれる(`vfl01.py:302-303`)。
Family X用のLedger確定も同じ`vfl01.build_verified_ledger_text()`を呼ぶ
(`er012_e...py:222-223`、`er019_family_x_entertainment_production_runner_01.py:116-118`)。

### 1-2. Ledger逸脱チェック(=Deviation Check、10カテゴリv2)

`vfl01.py:434-561`。10フラグ
(`DEVIATION_FLAG_KEYS`、`vfl01.py:448-452`): `changed_fact`/
`changed_scope`/`changed_causality`/`changed_certainty`/`changed_number`/
`changed_actor`/`changed_negation`/`changed_comparison`/`changed_time`/
`unsupported_new_claim`。

判定Prompt本体(`DEVIATION_PROMPT_TEMPLATE`、
sha256=`d3ad565d6d2b3b156c01156295d02c2c14ac33816767ea05af4eb963e5afefc9`、
`vfl01.py:502-541`)の核心部分(逐語、`vfl01.py:531-537`):
> 「上記10種類のいずれかが明確にtrueである場合のみ、severityをMAJORに
> してください。10種類すべてがfalseなのにMAJORにすることは禁止です。
> (中略)判断に迷う場合は、『記事の主張がLedgerの主張とほぼ同じ意味を
> 保っているか』を最優先の基準にしてください。厳密な文言一致は求め
> ません。」

許容範囲(`vfl01.py:523-529`、同prompt内): 自然なparaphrase・A2/B1向け
平易化・bridge sentence・「明確な新規Factを伴わない一般的な情景描写」
・Ledgerと一字一句一致しないが同じ意味の表現、は逸脱として報告しない
よう明記されている。

post-hoc validation(`_apply_deviation_post_hoc_validation()`、
`vfl01.py:544-561`): モデルがMAJORを返したのに10フラグ全てfalseなら
自動的にMINORへ降格し(`auto_downgraded=True`)、`overall_status`は
モデルの自己申告ではなくプログラム側で(降格後の)MAJOR残存有無から
再計算する。**MAJOR/MINORの最終決定はcodeレベルで機械的に固定されて
おり、モデルの自由裁量ではない**(この設計自体は誤検知防止のための
安全策、ER-009-N1-LEDGER-DEVIATION-RECALIBRATION-02由来)。

Hook-aware判定(`vfl01.py:565-631`)はProduction本経路(Family X)では
**未使用**(`hook_aware=False`固定、`er019_family_x_ja_writer_o_r1_r2_01.py`
・`er012_e...py`とも全呼び出しで`hook_aware=False`を明示指定)。Hook-aware
は別の既存Production経路(`er003_v1_n3_01_articles_generate.py`)専用。

### 1-3. JA Fact Check(`er019_family_x_ja_writer_o_r1_r2_01.py`)

`run_ja_writer_o_r1_r2()`(`jaw.py:235-494`)。`full_ledger_text`が渡され
た場合のみ発動(既定None、後方互換)。

- JA Original直後(`jaw.py:263-310`): `vfl01.run_deviation_check(client,
  full_ledger_text, original_text, hook_aware=False,
  include_related_fact_id=True)`(`source_article_text`は渡さない=
  `origin`判定なし、JAが原文=起点であるため理論上不要)。MAJORなら
  `build_must_fix_block()`(`jaw.py:125-145`)でFact ID・該当箇所・指摘・
  理由を1回だけ提示して再生成、再Checkで`LEDGER_COMPLIANT`かつ
  `all_prior_issues_resolved`両方を満たさなければ`JAFactCheckStopError`
  でSTOP(`jaw.py:169-181`, `291-299`)。
- JA R2確定後(`jaw.py:375-438`): 同型のCheck+must-fix 1回retry構造。

### 1-4. English Deviation Check(Advanced/Standard、`er012_e_family_entertainment_two_level_runner_01.py`)

`run_writer_stage()`(`er012_e...py:339-546`)。**Advanced(L380-431)と
Standard(L476-522)は完全に対称の同一ロジック**(委任文にあった「Standard
[A2]側のDeviation Checkの有無」への回答: **Standardにも同一のDeviation
Checkが存在し、Advancedと同一の実装・同一のJA由来判定を持つ**、コード上
非対称ではない)。

`vfl01.run_deviation_check(client, ledger_text, <advanced_text|standard_text>,
hook_aware=False, include_related_fact_id=True, source_article_text=ja_text)`
── ここで初めて`source_article_text`(JA R2確定テキスト)が渡され、
`origin`(`ja_source`/`translation`/`not_applicable`)の追加判定が行われる。

`origin`判定Prompt(`ORIGIN_INSTRUCTION_TEMPLATE`、
sha256=`665a74c84277ca6f479b36e4fb8df624d6d65c5f81a5d2a360e713cb22e74015`、
`vfl01.py:667-675`、逐語):
> 「ja_source: 原文記事の時点で既にこの逸脱に相当する内容が存在していた」
> 「translation: 原文記事では問題なく、翻訳・適応の過程で新たに生じた」

`JARecheckRequiredError`(`er012_e...py:266-274`)は、MAJORのうち1件でも
`origin=="ja_source"`と判定された場合に**即座に**送出される(must-fix
retryを1回も試さない)。これは「Englishを盲目的に再生成せず、JA側の
再確認が必要」という設計意図(コメント`er012_e...py:267-269`)であり、
`CURRENT_SPEC.md:1220-1223`の正式仕様(「JA側が正しい場合のみ英訳工程で
must-fix retry、JA R2が誤っている場合はJA側へ差し戻し」)と一致する。
`origin=="translation"`のMAJORのみがEnglish側でmust-fix 1回retryの対象
になる(`er012_e...py:399-431`, `495-522`)。

### 1-5. Production量産上の目的(既存記述からの整理)

`OPEN_ITEMS.md`(OPEN-187、`awk`確認)によれば、この設計は「英訳段の
Advanced Deviation Check retryが1回目MAJORの内容を一切受け取らず同一
入力で英訳を再生成するだけ」だった旧実装の不具合
(`NEWS-FAMILY-X-B3-ADVANCED-RETRY-ROOTCAUSE-01`で確認)への対策として、
2026-09-27に`NEWS-FAMILY-X-JA-FACT-CHECK-PRODUCTION-WIRING-01`で
Production配線された(`commit 6087e764`、Fable Gate 3判定
`PRODUCTION_WIRED`、`DECISION_LOG.md:9687-9700`)。固定費約¥2.20/記事・
latency約110秒(JA側のみ、改善候補は`OPEN-189`、未着手)。

---

## 2. hard constraint / soft guidance の区別

### 2-1. `notes_for_writer`の設計意図と実際の扱い

**設計意図(soft guidance)**: `RESEARCHER_PROMPT_TEMPLATE`(`vfl01.py:157`)
は明確に「後工程のwriterが使わないよう」と書いており、これは**writerが
執筆時に読む注意書き**として構想されている。git履歴(`git log -S
"notes_for_writer" -- "er0*.py"`)では、このフィールドは
`ER-003-EN-DIRECT-VFL-01`(commit `03a356b4`、Trial/Experiment開始時点)
で導入され、以降のcommitは主に本文生成・Trial実行のログでありnotes_for_writer
自体の役割再定義commitは見当たらない(**未確認**: notes_for_writerの
役割を明示的に議論したDECISION_LOGエントリは、本調査のgrep範囲では
発見できなかった。CURRENT_SPEC/DECISION_LOG本体でnotes_for_writerを
主題にした専用セクションは無い)。

**実際の扱い(hard化の実態)**: `build_verified_ledger_text()`
(`vfl01.py:302-303`)は`notes_for_writer`を他のfact fieldと**区別なく**
Ledgerテキストへ埋め込む。この`verified_ledger_text`全体がそのまま
Deviation Check Promptの`{verified_ledger_text}`枠(`vfl01.py:505-506`)
へ渡される。Deviation Check Prompt自体には「notes_for_writerは
writerへのガイダンスであり、それ自体は検証対象のFactではない」という
除外規定・区別記述は**存在しない**(`DEVIATION_PROMPT_TEMPLATE`全文を
確認、`vfl01.py:502-541`にnotes_for_writerという語自体が出現しない)。
結果として、Deviation Checkは「Ledgerの範囲内に収まっているか」を判定
する際、`notes_for_writer`の記述内容も他のFact fieldと同列に判定根拠
として使用できる状態になっている。

**実例(Hormuz、第7章で詳述)**: HF-011の`notes_for_writer`(逐語、
`er019_output/family_x_refresh_e2e_01/hormuz/run_02/ledger/verified_fact_ledger.txt:80`)
「7月14日は撤回があったにもかかわらず日次清算値は上昇した。これだけ
から撤回が価格を上昇させた、または下落させなかったと因果推論しない」
は、writerへの執筆時ガイダンスとして書かれたものだが、実際のEN
Deviation Check(`advanced_attempt1.json`)は、このnotes_for_writerの
文言を**MAJORの直接的な判定根拠**として引用している(`explanation`
逐語: 「HF-009が保証するのは(中略)観測であり、記事はそれを撤回の
非因果的な結果として断定している」)。つまり、**Researcher段階では
「writerへの助言」として設計されたテキストが、Deviation Check段階では
「これに反したらMAJOR」という事実上のhard constraintとして機能して
いる**。これはコード上の明示的な仕様変更ではなく、**同じテキストが
2つの異なる工程(Writer生成/Deviation Check検証)で異なる強度の意味
を持たされている**という構造上の帰結として観察された(推測ではなく
上記promptの文言比較・実データの`explanation`引用から直接確認できる
事実)。

### 2-2. どこでhard化されているか(コード上の分岐点)

- `_apply_deviation_post_hoc_validation()`(`vfl01.py:544-561`)は
  「10フラグのいずれかがtrue→MAJORの可能性」を機械的に強制する
  (soft/hardの区別ではなく、フラグの有無のみを見る)。
- `JAFactCheckStopError`/`JARecheckRequiredError`(`jaw.py:169-181`,
  `er012_e...py:266-274`)は、MAJORが1件でも解消しなければ**必ずSTOP**
  する設計であり、MAJORの原因がnotes_for_writer由来か他のfield由来かを
  区別する分岐は存在しない。つまり「hard化」はDeviation Check自体の
  prompt設計(2-1)に起因し、STOP機構(retry/Gate)側は10フラグの真偽
  以外の情報を見ていない。

### 2-3. B3 fact selection側での`notes_for_writer`の生成・意図

`er019_family_x_storyline_b3_fact_selection_01.py`をgrepした限り、
`notes_for_writer`という語自体は同ファイルに出現しない
(`grep -n "notes_for_writer"`結果0件)。B3(Storyline選定+4テスト)は
Full Ledgerから`selected_fact_ids`/`selected_fact_brief`を選ぶ工程で
あり、`notes_for_writer`フィールド自体の生成はResearcher段階
(1-1、`vfl01.RESEARCHER_PROMPT_TEMPLATE`)のみが担っている。B3は
Ledger内の既存notes_for_writerを**改変せずそのまま**選定結果へ含める
(直接コード確認、B3は新規notes_for_writerを生成しない)。

---

## 6. 信頼性の最低ライン(既存仕様からの抽出、新規定義しない)

以下は、既存Prompt・DECISION_LOGから抽出した「eigo-radioが崩さないと
明記してきたFact品質の下限」。各項目に根拠を付す。

| 最低ライン | 根拠 |
|---|---|
| Ledgerにない/矛盾する具体的事実を主張しない(`changed_fact`) | `DEVIATION_PROMPT_TEMPLATE`(`vfl01.py:512`)、ER-009-N1-LEDGER-DEVIATION-RECALIBRATION-02で「意図的に危険な9種のfixture」の1つとして検知維持を確認済み(`DECISION_LOG_HISTORY.md:5931-5934`) |
| 対象範囲・母集団を超えて一般化しない(`changed_scope`) | 同上(`vfl01.py:513`)。No.9で「NYCタクシー研究をレストラン全般へ広げすぎ」を実問題として検知した実績あり(`DECISION_LOG_HISTORY.md:5922-5923`、この例はscope拡張が「本物の問題」だったケース) |
| 相関を因果に変えない・因果の方向を変えない(`changed_causality`) | 同上(`vfl01.py:514`)。Researcher Prompt自身も「Sourceより強い因果表現を後工程のwriterが使わないよう」明記(`vfl01.py:157`) |
| 仮説・自己申告を断定に強めない(`changed_certainty`) | 同上(`vfl01.py:515`) |
| 数値・割合・件数を改変しない(`changed_number`) | 同上(`vfl01.py:516`)。fixtureの1つとして数値改変のMAJOR検知維持を確認(`DECISION_LOG_HISTORY.md:5933`) |
| 発言主体・調査主体を別人物・組織にすり替えない(`changed_actor`) | 同上(`vfl01.py:517`) |
| 肯定・否定を反転させない(`changed_negation`) | 同上(`vfl01.py:518`) |
| 比較の方向を反転・変更しない(`changed_comparison`) | 同上(`vfl01.py:519`) |
| 時期・年代を変えない(`changed_time`) | 同上(`vfl01.py:520`) |
| Ledgerに全く無い新しい具体的主張を追加しない(`unsupported_new_claim`) | 同上(`vfl01.py:521`) |
| 曖昧なFactを無理に確定しない([AMBIGUOUS]は断定禁止) | `WRITER_PROMPT_TEMPLATE`(`vfl01.py:342`)、Ledger確定テキストの`[AMBIGUOUS - 断定禁止、曖昧さを保持すること]`タグ(`vfl01.py:288`) |
| 数字のscopeを混同しない(全体母集団 vs 特定条件群) | `WRITER_PROMPT_TEMPLATE`(`vfl01.py:340`)、Researcher Prompt(`vfl01.py:154-156`) |
| 時間条件を別項目へ拡張しない | `WRITER_PROMPT_TEMPLATE`(`vfl01.py:341`) |

**この最低ライン自体(10カテゴリの存在・MAJOR=STOP対象という設計)は、
本調査の範囲では正当と評価する根拠(ER-009-N1-LEDGER-DEVIATION-
RECALIBRATION-02での「意図的に危険な9種のfixtureは全てMAJOR判定を
維持」という検証実績)がある**。一方で、**この最低ラインの「適用のされ方」
(同じ最低ラインをJA記事とEN記事に別々に、非決定的なLLM判定で適用して
いること)が一貫性の問題を生んでいる**というのが第7章の観察である。

---

## 7. Hormuzの事例trace

### 7-1. run_02(JA Fact Check配線後)

**Ledger上の元Fact(逐語)**:
- HF-009(`ledger/verified_fact_ledger.txt:58-64`): 「Yahoo Financeは、
  7月14日の撤回・投資案件への置換発表後、Brent先物が一時的に上げ幅を
  縮小したものの、ほどなく発表前に近い高い水準へ戻ったと報じた。(中略)
  約2.6％高で、1バレル85ドルを上回っていた。」
  notes_for_writer: 「撤回後に原油価格が全面的に下落したとは書かない。
  観測されたのは一時的な上げ幅縮小と、その後の回復。」
- HF-011(同`:74-80`): 「Brent原油先物は7月14日に1.43ドル、1.7％上昇し、
  1バレル84.73ドルで清算された。(中略)」
  notes_for_writer: 「7月14日は撤回があったにもかかわらず日次清算値は
  上昇した。これだけから撤回が価格を上昇させた、または下落させなかった
  と因果推論しない。」

**JA R2生成文**(`ja_writer/revision2.md`該当段落、run_02): 「料金案が
消えたからといって、価格がそのまま大きく下がる展開にはなりませんでした。
米国とイランの間では攻撃が続き、海上封鎖やタンカーの安全への懸念も
残っていました。」直後の段落で「もちろん、この値動きだけで価格の理由
を一つに決めることはできません。」という留保文が続く。

**JA R2 Fact Check判定**(`ja_writer/audit/deviation_checks/ja_r2_attempt1.json`):
`overall_status: LEDGER_COMPLIANT`、`deviations: []`(0件)。この段落は
一切問題視されなかった。

**EN Advanced生成文**(`b1b/article.md`): 「The disappearance of the fee
plan did not lead to a large, lasting fall in prices. Attacks between the
United States and Iran continued, and concerns about a sea blockade and
the safety of tankers remained.」次段落で「Of course, this price movement
alone cannot tell us that there was just one reason for the price.」と
いう、JA側と同じ趣旨の留保文が続く(EN側にも留保文自体は存在する)。

**EN Advanced Deviation Check判定**
(`b1b/audit/deviation_checks/advanced_attempt1.json`): `overall_status:
LEDGER_DEVIATION`。該当claim「The disappearance of the fee plan did not
lead to a large, lasting fall in prices.」を`severity: MAJOR`、
`changed_causality: true`、`related_fact_id: HF-011`、`origin: ja_source`
と判定。explanation(逐語): 「HF-009が保証するのは撤回後の一時的な
上げ幅縮小とその後の高水準への回復という観測であり、記事はそれを撤回
の非因果的な結果として断定している。」

**JA Original段のFact Check履歴(参考)**: 同じrun_02のJA Original段では、
1回目(`ja_original_attempt1.json`)で3件のMAJORが検出されている
(市場の関心対象を「料金ではなく危険」と排他的に断定/置換の安全効果を
断定/船舶停止と燃料・運送費への影響を新規因果として追加、いずれも
`changed_causality`+`unsupported_new_claim`を含む)。must-fix 1回retryで
2回目(`ja_original_attempt2.json`)は`LEDGER_COMPLIANT`(0件)に解消して
いる。つまりJA Original→R1→R2の執筆・改稿過程のどこかで、Original段の
3件とは別の新しい表現(「料金案が消えたからといって〜」)が**R1または
R2の「もっとエンターテインメント性の高い記事に」という改稿指示**の中で
新たに生まれ、それがR2 Fact Checkでは検出されず、EN側でのみ検出された。

### 7-2. run_01(HF-006、参考事例)

run_01時点では`ja_writer/`に`audit/deviation_checks/`が存在せず(JA側
Fact Check未配線、run_01はER-019の初期段階かつACTIVE_TASK記載の通り
一部er039 Trialセル由来のJA入力を使っていた)、JA側の直接比較はできない。
EN Advanced Deviation Check(`b1b/audit/deviation_checks/advanced_attempt1.json`)
は「Even if this seems like a story about a distant sea, oil prices are
linked to gasoline prices and transportation costs.」を`unsupported_new_claim`
でMAJOR、`related_fact_id: HF-006`、`origin: ja_source`と判定。JA原文
(`ja_writer/original.md:19`)を確認すると「遠い海の話に見えても、原油
価格はガソリンや運送費につながります。」という**ほぼ同一内容の一文が
実在**する。この一文は、JA Original Prompt(`R0_PROMPT`、
sha256=`6108a7cddaa9eaf31262354ba32d33e4683ccaf810d861f27e3dcc8972028366`、
`jaw.py:52-66`)自体が要求する構造要素、逐語(`jaw.py:58`)「遠い地域だけ
の特殊な話に見える場合は、読者の暮らしや、より大きな社会の変化との
つながりを一度だけ示してください。」に対応する、**Prompt自身が求める
一般化ブリッジ文**である。

### 7-3. 「現行仕様でMAJORになる理由」と「実害の論点」(分けて記述)

**現行仕様でMAJORになる理由(事実)**:
1. Deviation Checkの10カテゴリのうち`changed_causality`
   (相関を因果に変えている/因果の方向を変えている)が明確にtrueと
   判定されたため(HF-011の一件)。
2. その判定根拠は、Ledgerの`notes_for_writer`が明示的に「これだけ
   から因果推論しない」と書いていた事項について、記事側が
   "did not lead to"という因果的な結論表現を使ったこと(第2章の
   hard/soft論点そのもの)。
3. 一方で、**同じ内容が含まれるJA R2は同一の判定機構でCOMPLIANTと
   判定された**。これは10カテゴリ・閾値・promptがJA/EN間で異なる
   から(仕様上の非対称)ではなく、**同一のLLM判定が同一Ledgerに対して
   JA文とEN文とで異なる結論を出した**という、実行間の一貫性の問題
   として観察される(0-3節、ER-009-N1-LEDGER-DEVIATION-RECALIBRATION-02
   の既知の限界と符合)。
4. run_01のHF-006の例では、MAJORの原因となった一文が**JA Writer
   Prompt自身が要求する構造的なブリッジ文**であり、Deviation Checkの
   「許容範囲」規定(`vfl01.py:527-528`「明確な新規Factを伴わない
   一般的な情景描写」)がこのケースに適用されなかった(推測: ガソリン・
   運送費という「具体的な経済的帰結」への言及は、Checkerには「一般的
   情景描写」ではなく「新規の具体的主張」と判定された可能性が高いが、
   この判定自体の妥当性は本調査では評価しない)。

**実害・英語学習サービス上の観察(論点整理、断定しない)**:
- JA文・EN文ともに、問題視された断定文の直後(1〜2文後)に「これだけ
  から理由を一つに決めることはできない」という趣旨の留保文が存在する
  (JA: 「もちろん、この値動きだけで価格の理由を一つに決めることは
  できません。」/EN: 「Of course, this price movement alone cannot tell
  us that there was just one reason for the price.」)。Deviation Check
  は該当claim単体を切り出して判定しており、**同一記事内の後続の留保文
  との整合を評価する仕組みは無い**(`DEVIATION_PROMPT_TEMPLATE`は
  `claim_in_article`を個別に判定する設計であり、記事全体の文脈上の
  自己限定を加点要素として扱う指示は含まれていない、事実として観察)。
- EN文の実際の表現は"did not lead to a **large, lasting** fall in
  prices"であり、"large"と"lasting"という限定語を伴っている(無限定の
  "did not lead to a fall"ではない)。この限定語の存在が、Ledgerの
  observed factsの範囲(一時的な上げ幅縮小→高水準への回復)とどの程度
  整合するかは評価が分かれ得る論点である(本調査では判定しない)。
- run_01のHF-006の例は、Writer Promptが要求する構造的要素(遠い地域の
  話を読者の生活へ一般化するブリッジ文)と、Deviation Checkの「Ledger
  範囲外の具体的主張を許さない」という制約が、**同じProduction仕様の
  内部で緊張関係にある**ことを示す一事例である(この緊張自体の解消策は
  本調査のスコープ外)。

---

## 未確認事項・新たに見つかった重大問題(修正せず報告のみ)

1. **未確認**: `notes_for_writer`の役割定義(soft guidance/hard
   constraint)を正面から議論した専用のDECISION_LOGエントリは、本調査の
   grep範囲(`notes_for_writer`/`changed_causality`/`ja_source`/
   `JARecheckRequiredError`のgit -S検索、CURRENT_SPEC/DECISION_LOG該当
   Grep)では発見できなかった。ER-003-EN-DIRECT-VFL-01(Trial導入時)の
   コメント(1-1参照)以外に、公式な役割定義文書は無い可能性がある。
2. **重大所見(修正せず報告)**: JA R2 Fact Check(`vfl01.run_deviation_check`)
   とEN Advanced Deviation Check(同一関数)が、**内容的に対応する同一の
   主張**に対して異なるMAJOR/COMPLIANT判定を下した実例をHormuz run_02で
   確認した(7-1)。これは個別記事の偶発事象という可能性と、Checker自体
   の非決定性(ER-009-N1-LEDGER-DEVIATION-RECALIBRATION-02で既知の限界
   として記録済み)に起因する構造的な再現可能性のある問題という可能性の
   両方が考えられ、本調査単独では判別できない(Part Bの過去事例集計と
   合わせて評価する必要がある)。
3. **観察(修正せず報告)**: run_01のHF-006事例は、JA Writer Prompt
   (`R0_PROMPT`)自体が要求する一般化ブリッジ文の構造的要求と、
   Deviation Checkの「Ledger範囲外の新規具体的主張禁止」という制約が
   矛盾し得ることを示している。この矛盾はJA Fact Check配線(2026-09-27
   以降)によりJA段で先に捕捉されるようになった(`DECISION_LOG.md:9695`
   「旧記事[run_01]で英語Advanced段まで伝播していた問題がJA段で先に
   捕捉されることを確認」)が、JA段のCheckerも同一機構である以上、
   同種の緊張が解消されたか、単にJA段での判定結果が偶然一致した
   だけかは、本調査だけでは判別できない。
4. OPEN-189(JA Fact Check固定費・latency最適化)は`OPEN(改善候補、
   ユーザ実検証後)`のまま未着手。本調査で新たな緊急性の指摘はしない。

---

## Part Bとの関係

本ファイルはPart A(役割整理・hard/soft区別・信頼性の最低ライン・Hormuz
trace)のみを扱う。過去のSTOP事例の分類・QCD評価はPart B
(`docs/pm/investigation_ledger_deviation_check_01_part_b.md`、並行する
別Sonnetの担当)で扱われる。**両者の統合(新Checker設計の検討含む)は
別委任とする**。

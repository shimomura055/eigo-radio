# LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01 REPORT

**Status**: 調査タスク(read-only)。Production code/Prompt/閾値/SSOT変更なし。
Family X E2E は STOP 維持。設計素案は ChatGPT 側で作成後、Opus L2 レビュー
(未実施)。

本REPORTは、Part A(`docs/pm/investigation_ledger_deviation_check_01_part_a.md`、
委任_01)とPart B(`docs/pm/investigation_ledger_deviation_check_01_part_b.md`、
委任_02)を統合し、ユーザー指定の章立て1〜8で再構成したものである(委任_03)。
**本REPORTは決定・採用提案・Production変更提案を行わない**。Part A/B自体は
編集していない(参照のみ)。ユーザー向け表記はStandard/Advanced(内部名
A2/B1B併記)。

---

## 1. 現行 Ledger Check(JA側)/ Deviation Check(EN側)の役割整理

### 1-0. 冒頭: 何が同じで何が違うか

**最重要の事実確認(Part A §0)**: JA側「Fact Check」とEN側「Deviation
Check」は、**実装上まったく同一の1つの関数**
`er003_v1_en_direct_vfl_01_generate.py::run_deviation_check()`(以下
`vfl01.run_deviation_check()`)である。同じPrompt本文・同じ10カテゴリ判定
基準・同じMAJOR/MINOR閾値・同じpost-hoc降格ロジックを、**JA記事**に適用
するか**EN記事(Advanced/Standard)**に適用するかの違いしかない。「JA側が
甘い基準・EN側が厳しい基準」という設計上の二段階(2段構え)は存在しない
(コード上そのような分岐は無い)。

| 項目 | JA側(Ledger Check / Fact Check) | EN側(Deviation Check) |
|---|---|---|
| 呼び出す関数 | `vfl01.run_deviation_check()`(同一) | `vfl01.run_deviation_check()`(同一) |
| Prompt/10カテゴリ/閾値 | 同一(`DEVIATION_PROMPT_TEMPLATE`) | 同一 |
| 検証対象テキスト | JA Original / JA R2 | Advanced(English忠実英訳)/ Standard(A2) |
| 参照するLedger | Full Ledger(同一) | Full Ledger(同一) |
| `origin`判定(ja_source/translation) | 行わない(`source_article_text`未指定) | 行う(`source_article_text=ja_text`指定) |
| MAJOR時の挙動 | must-fix 1回retry→なおMAJORなら`JAFactCheckStopError` | must-fix 1回retry→なおMAJORなら`RuntimeError`。ただし`origin=ja_source`が1件でもあれば retryせず即`JARecheckRequiredError`でSTOP |
| Standard(A2)側の扱い | (該当なし、JAは1系統のみ) | Advancedと**全く同一ロジック**でDeviation Check実施 |

「両者で結果が食い違う」という事象(第7章のHormuz事例)は、**基準が違う
から**ではなく、**同一の基準・同一のLLM判定機構が、JA記事に対して行った
判定とEN記事(内容はほぼ翻訳版)に対して行った判定とで、結果が一致
しなかった**という、LLM-as-judge固有の**実行間の非決定性/一貫性**の
問題として観察された(ER-009-N1-LEDGER-DEVIATION-RECALIBRATION-02
[2026-08-29]でも「実行ごとの非決定性はv2でも解消されていない」と既に
明記されている、`DECISION_LOG_HISTORY.md:5963`該当行)。

### 1-1. Verified Fact Ledgerの構造(Researcher→Verification→Ledger確定)

主要ファイル: `er003_v1_en_direct_vfl_01_generate.py`(以下`vfl01`、961行)。
Family X(`er019_family_x_entertainment_production_runner_01.py`)はこの
`vfl01`のprompt/schema/関数を**そのままimportして再利用**しており、
`er012_e_family_entertainment_two_level_runner_01.py::run_researcher_for_topic()`
(L160-180)/`run_verification_for_topic()`(L183-203)も`vfl01.build_researcher_prompt`
/`vfl01.RESEARCHER_DEVELOPER_MESSAGE`/`vfl01.FACT_LEDGER_JSON_SCHEMA`を
直接呼んでおり、独自のprompt改変は無い(確認済み、`er012_e...py:160-228`)。

各Factのfield(`vfl01.py:78-126` `FACT_LEDGER_JSON_SCHEMA`):
- `fact_id`/`claim`/`subject`: Factの識別・主張・主体
- `date_or_period`/`scope`/`conditions`: 時期・対象範囲・成立条件
- `numeric_value`/`numeric_scope`: 数値と、その数値が指す母集団
- `causal_strength`(`OBSERVED_REPORTED`/`CORRELATIONAL`/
  `CAUSAL_STATED_BY_SOURCE`/`NOT_APPLICABLE`): 観察・相関・Source自身の
  因果主張の区別
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
は設計時点でwriterへの執筆ガイダンスとして構想されたフィールドである**。

Verification(`vfl01.py:195-272`)は独立Web検索でFactを
VERIFIED/AMBIGUOUS/REJECTEDに判定し、`build_verified_ledger_text()`
(`vfl01.py:275-305`)がkept facts(REJECTEDのみ除外)をテキスト化する。
この際`notes_for_writer`はfactごとの他フィールド(scope/numeric_value等)
と**同列の1行**としてLedgerテキストへ埋め込まれる(`vfl01.py:302-303`)。
Family X用のLedger確定も同じ`vfl01.build_verified_ledger_text()`を呼ぶ
(`er012_e...py:222-223`、`er019_family_x_entertainment_production_runner_01.py:116-118`)。

### 1-2. Ledger逸脱チェック(=Deviation Check、10カテゴリv2)

`vfl01.py:434-561`。10フラグ(`DEVIATION_FLAG_KEYS`、`vfl01.py:448-452`):
`changed_fact`/`changed_scope`/`changed_causality`/`changed_certainty`/
`changed_number`/`changed_actor`/`changed_negation`/`changed_comparison`/
`changed_time`/`unsupported_new_claim`。

判定Prompt本体(`DEVIATION_PROMPT_TEMPLATE`、
sha256=`d3ad565d6d2b3b156c01156295d02c2c14ac33816767ea05af4eb963e5afefc9`、
`vfl01.py:502-541`)の核心部分(逐語、`vfl01.py:531-537`):
> 「上記10種類のいずれかが明確にtrueである場合のみ、severityをMAJORに
> してください。10種類すべてがfalseなのにMAJORにすることは禁止です。
> (中略)判断に迷う場合は、『記事の主張がLedgerの主張とほぼ同じ意味を
> 保っているか』を最優先の基準にしてください。厳密な文言一致は求め
> ません。」

許容範囲(`vfl01.py:523-529`、同prompt内): 自然なparaphrase・A2/B1向け
平易化・bridge sentence・「明確な新規Factを伴わない一般的な情景描写」・
Ledgerと一字一句一致しないが同じ意味の表現、は逸脱として報告しないよう
明記されている。

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
  `origin`判定なし)。MAJORなら`build_must_fix_block()`(`jaw.py:125-145`)
  でFact ID・該当箇所・指摘・理由を1回だけ提示して再生成、再Checkで
  `LEDGER_COMPLIANT`かつ`all_prior_issues_resolved`両方を満たさなければ
  `JAFactCheckStopError`でSTOP(`jaw.py:169-181`, `291-299`)。
- JA R2確定後(`jaw.py:375-438`): 同型のCheck+must-fix 1回retry構造。

### 1-4. English Deviation Check(Advanced/Standard、`er012_e_family_entertainment_two_level_runner_01.py`)

`run_writer_stage()`(`er012_e...py:339-546`)。**Advanced(L380-431)と
Standard(L476-522)は完全に対称の同一ロジック**(Standard[A2]側にも
Advancedと同一の実装・同一のJA由来判定を持つ)。

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

### 1-5. Production量産上の目的

`OPEN_ITEMS.md`(OPEN-187)によれば、この設計は「英訳段のAdvanced Deviation
Check retryが1回目MAJORの内容を一切受け取らず同一入力で英訳を再生成する
だけ」だった旧実装の不具合(`NEWS-FAMILY-X-B3-ADVANCED-RETRY-ROOTCAUSE-01`
で確認)への対策として、2026-09-27に`NEWS-FAMILY-X-JA-FACT-CHECK-
PRODUCTION-WIRING-01`でProduction配線された(`commit 6087e764`、Fable
Gate 3判定`PRODUCTION_WIRED`、`DECISION_LOG.md:9687-9700`)。固定費約
¥2.20/記事・latency約110秒(JA側のみ、改善候補はOPEN-189、未着手)。

---

## 2. hard constraint / soft guidance の区別

### 2-1. `notes_for_writer`の設計意図と実際の扱い

**設計意図(soft guidance)**: `RESEARCHER_PROMPT_TEMPLATE`(`vfl01.py:157`)
は明確に「後工程のwriterが使わないよう」と書いており、これは**writerが
執筆時に読む注意書き**として構想されている。git履歴(`git log -S
"notes_for_writer" -- "er0*.py"`)では、このフィールドは
`ER-003-EN-DIRECT-VFL-01`(commit `03a356b4`、Trial/Experiment開始時点)
で導入され、以降のcommitは主に本文生成・Trial実行のログでありnotes_for_writer
自体の役割再定義commitは見当たらない(**未確認**: notes_for_writerの役割を
明示的に議論した専用のDECISION_LOGエントリは、本調査のgrep範囲では発見
できなかった)。

**実際の扱い(hard化の実態)**: `build_verified_ledger_text()`
(`vfl01.py:302-303`)は`notes_for_writer`を他のfact fieldと**区別なく**
Ledgerテキストへ埋め込む。この`verified_ledger_text`全体がそのまま
Deviation Check Promptの`{verified_ledger_text}`枠(`vfl01.py:505-506`)
へ渡される。Deviation Check Prompt自体には「notes_for_writerはwriterへの
ガイダンスであり、それ自体は検証対象のFactではない」という除外規定・
区別記述は**存在しない**(`DEVIATION_PROMPT_TEMPLATE`全文を確認、
`vfl01.py:502-541`にnotes_for_writerという語自体が出現しない)。結果として、
Deviation Checkは「Ledgerの範囲内に収まっているか」を判定する際、
`notes_for_writer`の記述内容も他のFact fieldと同列に判定根拠として使用
できる状態になっている。

**実例(Hormuz、第7章で詳述)**: HF-011の`notes_for_writer`(逐語、
`er019_output/family_x_refresh_e2e_01/hormuz/run_02/ledger/verified_fact_ledger.txt:80`)
「7月14日は撤回があったにもかかわらず日次清算値は上昇した。これだけ
から撤回が価格を上昇させた、または下落させなかったと因果推論しない」
は、writerへの執筆時ガイダンスとして書かれたものだが、実際のEN
Deviation Check(`advanced_attempt1.json`)は、このnotes_for_writerの
文言を**MAJORの直接的な判定根拠**として引用している(`explanation`逐語:
「HF-009が保証するのは(中略)観測であり、記事はそれを撤回の非因果的な
結果として断定している」)。つまり、**Researcher段階では「writerへの助言」
として設計されたテキストが、Deviation Check段階では「これに反したら
MAJOR」という事実上のhard constraintとして機能している**。これはコード
上の明示的な仕様変更ではなく、**同じテキストが2つの異なる工程(Writer
生成/Deviation Check検証)で異なる強度の意味を持たされている**という
構造上の帰結として観察された(推測ではなく上記promptの文言比較・実データ
の`explanation`引用から直接確認できる事実)。

### 2-2. どこでhard化されているか(コード上の分岐点)

- `_apply_deviation_post_hoc_validation()`(`vfl01.py:544-561`)は「10フラグ
  のいずれかがtrue→MAJORの可能性」を機械的に強制する(soft/hardの区別
  ではなく、フラグの有無のみを見る)。
- `JAFactCheckStopError`/`JARecheckRequiredError`(`jaw.py:169-181`,
  `er012_e...py:266-274`)は、MAJORが1件でも解消しなければ**必ずSTOP**
  する設計であり、MAJORの原因がnotes_for_writer由来か他のfield由来かを
  区別する分岐は存在しない。つまり「hard化」はDeviation Check自体の
  prompt設計(2-1)に起因し、STOP機構(retry/Gate)側は10フラグの真偽以外
  の情報を見ていない。

### 2-3. B3 fact selection側での`notes_for_writer`の生成・意図

`er019_family_x_storyline_b3_fact_selection_01.py`をgrepした限り、
`notes_for_writer`という語自体は同ファイルに出現しない(`grep -n
"notes_for_writer"`結果0件)。B3(Storyline選定+4テスト)はFull Ledgerから
`selected_fact_ids`/`selected_fact_brief`を選ぶ工程であり、`notes_for_writer`
フィールド自体の生成はResearcher段階(1-1)のみが担っている。B3はLedger
内の既存notes_for_writerを**改変せずそのまま**選定結果へ含める(直接
コード確認、B3は新規notes_for_writerを生成しない)。

### 2-4. 世代・実データ上のhard/soft観察(Part B由来)

Part Bのクロス集計(第4章)は、Family X origin付き15件のMAJORが
`changed_causality`(5件ja_source)・`unsupported_new_claim`(7件ja_source・
2件translation)に偏っていることを示す。これは、Deviation Checkの
「Ledgerに書かれた観測範囲(hard)を超えた因果・新規主張(soft寄りの
paraphraseとの境界が曖昧な領域)」への判定が、Family Xの実データ上でも
最も頻繁に発火するcategoryであることを裏付ける(2-1のnotes_for_writer
hard化観察と整合する実データ)。

---

## 3. 過去のSTOP事例(A/B表、Part B §3)

母集団: 全724件"deviation"系JSONファイルのうち481件が10-category
Ledger Deviation Checker schemaを持つ(431件COMPLIANT・50件DEVIATION、
deviation個票224件=MAJOR 87・MINOR 137)。`origin`フィールドを持つのは
9ファイル・15件のみ、全てFamily X Entertainment(JA原文→EN Advanced/
Standard翻訳)パイプライン(er019/er037/er039/er045)。以下のA/B分類は
この15件を対象とする。

### A候補: 明らかに止めるべきだったと思われる事例

| # | 管理ID/対象 | 該当文(JA→EN逐語) | 判定 | STOP/retry | 解決 | コスト | Evidence |
|---|---|---|---|---|---|---|---|
| A-1 | `family_x_b3_production_wiring_01`run_01 Meta記事 | JA Original「ロールバックされます」(未来形、上流ドリフト)→Advanced/Standard英訳もこの未来形を継承 | MAJOR、origin混在(claim単位でja_source/translation) | 2回ともCheckerがCOMPLIANT誤判定(RuntimeErrorのSTOPは発生せず)。後に**別タスクの手動テキスト直接修正**(`fact_fidelity_fix_01`)で是正・recheck | 人手修正+recheck ¥1.567(b1b¥0.323+a2¥1.244) | `NEWS-FAMILY-X-B3-ADVANCED-RETRY-ROOTCAUSE-01_REPORT.md`§3/§9-B、`er019_output/family_x_b3_production_wiring_01/run_01/audit/fact_fidelity_fix_01_recheck_summary.json` |
| A-2 | `family_xy_concreteness_control_trial_01`hormuz task_a_advanced(A3) | JA「上げ幅が一時的に縮小した」(HF-009)→EN「prices began to fall」 | MAJOR/ja_source | Trial測定(retry無し)。USER_DECISION_REQUIRED、Production不採用のまま終了 | Trial実測費用のみ | `er037_output/.../task_a_advanced/A3_deviation.json`、`FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01_REPORT.md`L165 |
| A-3 | `family_xy_concreteness_control_trial_01`hormuz task_a_advanced(A3、別項目) | JA「支払義務者は未提示」(HF-003)→EN「those carrying the cargo would repay」(支払義務者を具体化) | MAJOR/ja_source | 同上Trial測定 | 同上 | `er037_output/.../task_a_advanced/A3_deviation.json` |
| A-4 | `family_xy_concreteness_control_trial_02`meta cells/AN2-T1 | JA「相手」(企業・店舗)→EN「users」(Museのユーザー) | MAJOR/translation | Trial cell測定(retry無し) | 同上 | `er039_output/.../meta/cells/AN2-T1_deviation.json` |
| A-5 | `family_x_no_heading_segmentation_trial_01`meta | JA「元に戻しました」(ロールバック)→EN「put back the feature」(再有効化と読める、意味反転) | MAJOR/translation | v1でMAJOR検出→v2でmust-fix retry 1回実施→LEDGER_COMPLIANT | ¥0.8142(retry generate+recheck) | `er045_output/.../meta/v2/must_fix_retry_result.json` |

分類理由(候補・断定せず): A-1/A-5は「起きた/まだ起きていない」「ロールバック
/再有効化」という事実の方向そのものが反転しており、英語学習記事としても
事実誤認を生む可能性が高い。A-2は数値の言い換え(上げ幅縮小→価格下落)
で実際の値動きの向きが変わっている。A-3/A-4は支払主体・対象範囲(誰が
対象か)という具体的な取り違えで、プライバシー文脈(A-4)では特に重要と
なりうる。

### B候補: 過剰品質の可能性がある事例

| # | 管理ID/対象 | 該当文(JA→EN逐語) | 判定 | STOP/retry | 解決 | コスト | Evidence |
|---|---|---|---|---|---|---|---|
| B-1 | `family_x_b3_production_wiring_01`run_01(diversity_trial ja_writer)/`family_x_refresh_e2e_01`run_01/b1b/`family_xy_concreteness_control_trial_01`A3/`family_xy_concreteness_control_trial_02`AN3-T1(**4回独立発生**) | JA「原油価格が高い状態が続けば、ガソリンや輸送費など身近な価格にも影響する」→EN「oil prices...linked to gasoline prices and transportation costs」 | MAJOR/ja_source(unsupported_new_claim・changed_scope) | 各回で個別にSTOP/Trial終了、retryなし(ja_source起因のためfail-closedでretry対象外) | 各回のCheckerコール実費(¥0.5〜1.6程度/回) | `er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/ja_writer/audit/deviation_checks/ja_original_attempt1.json`、`er019_output/family_x_refresh_e2e_01/hormuz/run_01/b1b/audit/deviation_checks/advanced_attempt1.json`、`er037_output/.../task_a_advanced/A3_deviation.json`、`er039_output/.../hormuz/cells/AN3-T1_deviation.json` |
| B-2 | **`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01`run_02(委任背景に記載の本件)**、`family_x_refresh_e2e_01`hormuz run_02/b1b | JA「料金案が消えたからといって、価格がそのまま大きく下がる展開にはなりませんでした」→EN「The disappearance of the fee plan did not lead to a large, lasting fall in prices.」 | MAJOR/ja_source(changed_causality、related_fact_id=HF-011) | **STOP**(origin=ja_source検知でfail-closed、retry未実施の設計) | **未解決**(2026-09-29時点でUSER_DECISION_REQUIRED、次工程未着手) | run_02累計¥5.07(前run_01¥0.99232と合算で管理ID全体約¥6.05)+複数回委任(_08〜_10)の調査工数(未計測) | `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md`L923-960、`er019_output/family_x_refresh_e2e_01/hormuz/run_02/b1b/audit/deviation_checks/advanced_attempt1.json` |
| B-3 | `family_xy_concreteness_control_trial_01`hormuz task_b_cleanup(B1) | JA全体の文脈→EN「...continued on July 14, so the flashy 20% plan left the stage, but the chart only pulled back briefly before recovering.」(接続詞"so"で因果連結) | MAJOR/ja_source(changed_causality、HF-007) | Trial測定、retryなし | 未評価(Trial終了) | 同上 | `er037_output/.../task_b_cleanup/B1_deviation.json` |
| B-4 | `family_x_b3_production_wiring_01`run_01/b1b(Meta記事、他3項目) | JA「Meta従業員のプライバシー懸念」→EN「People feel differently when they think they are speaking to a machine and when they know a person is listening.」等、一般読者心理への一般化3件 | MAJOR/ja_source×2、translation×1(MUSE-HC-004/006/010) | 初回MAJOR→retry 1回(feedback未伝達の全文再生成)→最終的にCOMPLIANT | retry generate+check込み(§5参照、run全体¥4.9853) | `er019_output/family_x_b3_production_wiring_01/run_01/b1b/audit/deviation_checks/advanced_attempt1.json` |

分類理由(候補・断定せず): B-1は原油価格とガソリン価格の連動という一般
常識レベルの経済知識であり、Checker自身のプロンプトが許容範囲と明記する
「新規Factを伴わない一般的な情景描写」に近い可能性がある(4回独立して
同種claimが指摘されており、偶発ではなく構造的パターン)。B-2(本件)は
「一時的な上げ幅縮小+回復」という観測を「大幅な持続的下落は起きなかった」
と要約しており、意味の実質を大きく変えていない自然な要約表現である可能性
がある。B-3は複数の事実を並べる際の自然な接続表現(「so」)であり、断定的
な単一原因の主張とまでは言い切れない可能性がある。B-4は解説記事によく
ある一般化的言い回し。

### auto_downgraded(MAJOR→MINOR自動降格)事例

**0件**。スキャンした481ファイル・224件の個票のいずれにも
`auto_downgraded: true`は存在しなかった(該当キー自体は
`family_x_refresh_e2e_01`のスキーマに存在するが、実際に発火した記録は
見つからず)。

---

## 4. 現在の判定がどこまで厳しいかの分類(4区分、Part B §4)

| 区分 | 件数 | 代表例 | 共通category | 共通origin |
|---|---|---|---|---|
| (i) 絶対にSTOPすべき | 2件 | A-2(価格方向反転)、A-5(ロールバック↔再有効化) | changed_causality/changed_number相当、changed_scope | ja_source1・translation1 |
| (ii) 高リスクなのでSTOP妥当 | 3件 | A-3(支払義務者具体化)、A-4(ユーザー範囲取り違え)、B-3系(具体的因果は要注意) | unsupported_new_claim、changed_scope | ja_source2・translation1 |
| (iii) 品質改善の意味はあるがSTOP必須か疑問 | 7件 | B-3(接続詞"so")、B-2(本件)、B-4の3項目、A-1のうち生成解釈寄りの一部 | changed_certainty、changed_causality | ja_source中心 |
| (iv) 過剰品質の可能性が高い | 3件 | B-1(原油→ガソリン価格、4回独立発生) | unsupported_new_claim、changed_scope | ja_source |

(この4区分は本調査担当者による1回限りの目視分類であり、断定ではなく
「候補」。合議・再現性検証は未実施。件数はMAJOR/MINOR15件全件を重複なく
1区分ずつに割り当てた結果。)

### category × severity × origin クロス集計(実データ)

**全母集団(224件、origin無しの旧世代含む)**:

| category | MAJOR | MINOR |
|---|---|---|
| changed_fact | 31 | 14 |
| changed_scope | 16 | 24 |
| changed_causality | 14 | 9 |
| changed_certainty | 9 | 49 |
| changed_number | 1 | 0 |
| changed_actor | 0 | 7 |
| changed_negation | 0 | 0 |
| changed_comparison | 3 | 1 |
| changed_time | 1 | 7 |
| unsupported_new_claim | 36 | 28 |

**origin付き15件のみ(MAJORのみ、origin別)**:

| category | ja_source | translation |
|---|---|---|
| changed_fact | 0 | 0 |
| changed_scope | 3 | 1 |
| changed_causality | 5 | 0 |
| changed_certainty | 0 | 1 |
| changed_number | 0 | 0 |
| changed_comparison | 1 | 0 |
| changed_time | 0 | 0 |
| unsupported_new_claim | 7 | 2 |

(全母集団ではchanged_fact/changed_certaintyが最多カテゴリだが、origin付き
Family X 15件ではchanged_causality・unsupported_new_claimに偏っている。
これはFamily Xが「JA原文への忠実な翻訳+Ledgerとの整合」という二重制約下
にあり、数値そのものの誤りより「原文の含意をどこまで因果・新規主張として
引き継ぐか」が主な論点になっているためと推測される。断定はしない。)

### アーキテクチャ上の重要な観測

`NEWS-FAMILY-X-B3-ADVANCED-RETRY-ROOTCAUSE-01_REPORT.md`(既存REPORT、
read-only調査)によれば、現行retry機構は(a)1回目Checkerの指摘内容
(`deviations`のclaim/issue/explanation)を2回目の生成呼び出しへ一切渡さない
「ゼロベース全文再生成」であり、(b) `origin="ja_source"`のMAJORはそもそも
retryの対象外でfail-closedに即STOPする設計。したがって、ja_source起因の
MAJORは(i)〜(iv)のどの区分であっても常に同じ扱い(即STOP・retry無し)を
受けており、**問題の深刻度(区分)とSTOP時の挙動が現状では連動していない**。
これは既存仕様どおりの動作であり、本調査はこの設計自体の変更を提案しない
(採用判断はユーザー)。

---

## 5. QCD影響(Part B §5、未計測は「未計測」と明記)

母集団: 主にFamily X entertainment(Hormuz/Meta Muse記事、er019/037/039/045、
2026年9月)。一部、Editorial B-Family(4V/2V Trial、er012)のFact Checker A'
(Web検索付き、Ledger Deviation Checkerとは別のCheckerだが同じ3段構成の
一部)のコストも参考値として含む。

### Checker単発コール(実測、n=12、model=gpt-5.6-luna、reasoning=high)

| 指標 | コスト(JPY) | latency(秒) |
|---|---|---|
| 最小 | ¥0.323 | 9.55 |
| 中央値 | ¥0.9024 | 33.16 |
| 平均 | ¥0.954 | 38.07 |
| 最大 | ¥1.6505 | 84.89 |

出典: `NEWS-FAMILY-X-JA-FACT-DOUBLE-CHECK-COST-01_REPORT.md`§0/§1。

### retry(MAJOR時の生成+再Check、翻訳origin相当のみ実施される経路)

| 事例 | GENコスト | CHECKコスト | 結果 |
|---|---|---|---|
| meta final advanced 1回目→retry | ¥1.8575→¥0.6569 | ¥0.5939(MAJOR)→¥0.6477(compliant) | 解消 |
| hormuz(diversity trial) advanced 1回目→retry | ¥0.6656→¥0.8296 | ¥1.0079(MAJOR)→¥1.5466(なおMAJOR) | **retry後もSTOP** |
| meta first-pass standard 1回目→retry | ¥1.1477→¥0.3119 | ¥1.2140(MAJOR)→¥1.1136(compliant) | 解消 |
| no_heading_segmentation meta v1→v2 must-fix retry | ¥0.3333(gen)+¥0.4809(check) | 合計¥0.8142 | 解消 |

出典: 同REPORT§1-2/§2、`er045_output/.../must_fix_retry_result.json`。

### NG(MAJOR)発生率(参考値、母数小さい)

- n=7(Family X production/diversity trial、Advanced/Standard 1回目コール
  のみ): MAJOR 3/7≈43%。うち2/3は1回retryでLEDGER_COMPLIANTに解消、
  1/3(hormuz diversity trial)はretry後もMAJORが残りSTOP。出典: 同
  REPORT§2。
- Family X E2E本番(`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01`、Hormuz
  記事1本×run_01/run_02の2回試行): **2/2がAdvanced段でorigin=ja_source
  MAJORによりSTOP、Standard・Audio未着手**(完成0/2)。母数が記事1本・2
  runのみのため一般化不可。出典:
  `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md`L964-968。

### Human Review・attempt_historyへのCheckerの寄与

**未計測**(該当ログに含まれず)。`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`
(63行)・`er011_output/attempt_history.jsonl`(9,643行)を"deviation"/"ledger"
でGrepしたが、ヒットは全てTTS/ASR音声QA文脈(記事本文中の統計値
"standard deviations"、themeディレクトリ名に"ledger_trial"を含むだけ)
であり、Ledger Deviation Checker/JA Fact Check起因のHuman Reviewエスカ
レーションは1件も確認できなかった。

### Checker自体のモデルコスト・比較値

- Ledger Deviation Checker(Family X、web検索なし): 1回あたり中央値¥0.90
  (¥0.32〜¥1.65)。
- 参考: 別Checker「Fact Checker A'」(Editorial B-Family、web検索付き、
  Ledger Deviation Checkerとは別コンポーネント)は1回¥20〜25、
  MAX_WRITER_ATTEMPTS=3ループで1記事Writer段合計¥74.49に達した実例あり
  (`LEDGER-DEVIATION-CHECKER-SEARCH-COST-RECONCILIATION-01_REPORT.md`§10)。
  Family XのLedger Deviation Checker自体はこれよりコスト的に軽い(web
  検索0回)。

### throughput・未完成記事率

- 1呼び出しあたりのlatencyは実測済み(上記中央値33秒)。「STOPまでの所要
  時間」の記事単位集計はログに存在せず**未計測**。
- 未完成記事率: Family X E2E(Hormuz、上記)は2/2試行が未完成。他Family
  (diversity trial、concreteness trial等)はTrial扱いのため「未完成」の
  定義に当てはまらない(Trialは意図的に1回で測定終了するため)。

---

## 6. 信頼性の最低ライン(既存仕様からの抽出、新規定義しない)

以下は、既存Prompt・DECISION_LOGから抽出した「eigo-radioが崩さないと明記
してきたFact品質の下限」。各項目に根拠を付す。

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
RECALIBRATION-02での「意図的に危険な9種のfixtureは全てMAJOR判定を維持」
という検証実績)がある**。一方で、**この最低ラインの「適用のされ方」
(同じ最低ラインをJA記事とEN記事に別々に、非決定的なLLM判定で適用して
いること)が一貫性の問題を生んでいる**というのが第7章の観察である。

---

## 7. Hormuzの事例trace

### 7-1. run_02(JA Fact Check配線後)

**Ledger上の元Fact(逐語)**:
- HF-009(`ledger/verified_fact_ledger.txt:58-64`): 「Yahoo Financeは、
  7月14日の撤回・投資案件への置換発表後、Brent先物が一時的に上げ幅を
  縮小したものの、ほどなく発表前に近い高い水準へ戻ったと報じた。(中略)
  約2.6％高で、1バレル85ドルを上回っていた。」notes_for_writer: 「撤回後
  に原油価格が全面的に下落したとは書かない。観測されたのは一時的な上げ幅
  縮小と、その後の回復。」
- HF-011(同`:74-80`): 「Brent原油先物は7月14日に1.43ドル、1.7％上昇し、
  1バレル84.73ドルで清算された。(中略)」notes_for_writer: 「7月14日は
  撤回があったにもかかわらず日次清算値は上昇した。これだけから撤回が
  価格を上昇させた、または下落させなかったと因果推論しない。」

**JA R2生成文**(`ja_writer/revision2.md`該当段落、run_02): 「料金案が
消えたからといって、価格がそのまま大きく下がる展開にはなりませんでした。
米国とイランの間では攻撃が続き、海上封鎖やタンカーの安全への懸念も残って
いました。」直後の段落で「もちろん、この値動きだけで価格の理由を一つに
決めることはできません。」という留保文が続く。

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
と判定。explanation(逐語): 「HF-009が保証するのは撤回後の一時的な上げ幅
縮小とその後の高水準への回復という観測であり、記事はそれを撤回の非因果的
な結果として断定している。」

**JA Original段のFact Check履歴(参考)**: 同じrun_02のJA Original段では、
1回目(`ja_original_attempt1.json`)で3件のMAJORが検出されている(市場の
関心対象を「料金ではなく危険」と排他的に断定/置換の安全効果を断定/船舶
停止と燃料・運送費への影響を新規因果として追加、いずれも
`changed_causality`+`unsupported_new_claim`を含む)。must-fix 1回retryで
2回目(`ja_original_attempt2.json`)は`LEDGER_COMPLIANT`(0件)に解消して
いる。つまりJA Original→R1→R2の執筆・改稿過程のどこかで、Original段の
3件とは別の新しい表現(「料金案が消えたからといって〜」)が**R1またはR2の
「もっとエンターテインメント性の高い記事に」という改稿指示**の中で新たに
生まれ、それがR2 Fact Checkでは検出されず、EN側でのみ検出された。

### 7-2. run_01(HF-006、参考事例)

run_01時点では`ja_writer/`に`audit/deviation_checks/`が存在せず(JA側
Fact Check未配線、run_01はER-019の初期段階かつACTIVE_TASK記載の通り一部
er039 Trialセル由来のJA入力を使っていた)、JA側の直接比較はできない。EN
Advanced Deviation Check(`b1b/audit/deviation_checks/advanced_attempt1.json`)
は「Even if this seems like a story about a distant sea, oil prices are
linked to gasoline prices and transportation costs.」を`unsupported_new_claim`
でMAJOR、`related_fact_id: HF-006`、`origin: ja_source`と判定。JA原文
(`ja_writer/original.md:19`)を確認すると「遠い海の話に見えても、原油
価格はガソリンや運送費につながります。」という**ほぼ同一内容の一文が
実在**する。この一文は、JA Original Prompt(`R0_PROMPT`、
sha256=`6108a7cddaa9eaf31262354ba32d33e4683ccaf810d861f27e3dcc8972028366`、
`jaw.py:52-66`)自体が要求する構造要素、逐語(`jaw.py:58`)「遠い地域だけの
特殊な話に見える場合は、読者の暮らしや、より大きな社会の変化とのつながり
を一度だけ示してください。」に対応する、**Prompt自身が求める一般化ブリッジ
文**である。

### 7-3. 「MAJORになる理由」と「実害の論点」(分離)

**現行仕様でMAJORになる理由(事実)**:
1. Deviation Checkの10カテゴリのうち`changed_causality`(相関を因果に
   変えている/因果の方向を変えている)が明確にtrueと判定されたため
   (HF-011の一件)。
2. その判定根拠は、Ledgerの`notes_for_writer`が明示的に「これだけから
   因果推論しない」と書いていた事項について、記事側が"did not lead to"
   という因果的な結論表現を使ったこと(第2章のhard/soft論点そのもの)。
3. 一方で、**同じ内容が含まれるJA R2は同一の判定機構でCOMPLIANTと判定
   された**。これは10カテゴリ・閾値・promptがJA/EN間で異なるから(仕様上
   の非対称)ではなく、**同一のLLM判定が同一Ledgerに対してJA文とEN文とで
   異なる結論を出した**という、実行間の一貫性の問題として観察される
   (1-0節、ER-009-N1-LEDGER-DEVIATION-RECALIBRATION-02の既知の限界と
   符合)。
4. run_01のHF-006の例では、MAJORの原因となった一文が**JA Writer Prompt
   自身が要求する構造的なブリッジ文**であり、Deviation Checkの「許容範囲」
   規定(`vfl01.py:527-528`「明確な新規Factを伴わない一般的な情景描写」)
   がこのケースに適用されなかった(推測: ガソリン・運送費という「具体的な
   経済的帰結」への言及は、Checkerには「一般的情景描写」ではなく「新規の
   具体的主張」と判定された可能性が高いが、この判定自体の妥当性は本調査
   では評価しない)。

**実害・英語学習サービス上の観察(論点整理、断定しない)**:
- JA文・EN文ともに、問題視された断定文の直後(1〜2文後)に「これだけから
  理由を一つに決めることはできない」という趣旨の留保文が存在する
  (JA: 「もちろん、この値動きだけで価格の理由を一つに決めることはできま
  せん。」/EN: 「Of course, this price movement alone cannot tell us that
  there was just one reason for the price.」)。Deviation Checkは該当claim
  単体を切り出して判定しており、**同一記事内の後続の留保文との整合を評価
  する仕組みは無い**(`DEVIATION_PROMPT_TEMPLATE`は`claim_in_article`を
  個別に判定する設計であり、記事全体の文脈上の自己限定を加点要素として
  扱う指示は含まれていない、事実として観察)。
- EN文の実際の表現は"did not lead to a **large, lasting** fall in
  prices"であり、"large"と"lasting"という限定語を伴っている(無限定の
  "did not lead to a fall"ではない)。この限定語の存在が、Ledgerの
  observed factsの範囲(一時的な上げ幅縮小→高水準への回復)とどの程度
  整合するかは評価が分かれ得る論点である(本調査では判定しない)。
- run_01のHF-006の例は、Writer Promptが要求する構造的要素(遠い地域の話
  を読者の生活へ一般化するブリッジ文)と、Deviation Checkの「Ledger範囲
  外の具体的主張を許さない」という制約が、**同じProduction仕様の内部で
  緊張関係にある**ことを示す一事例である(この緊張自体の解消策は本調査の
  スコープ外)。

---

## 8. 再設計に向けた材料(決定しない、観察と論点を分離)

以下は、Part A/Bの観察を統合した「材料」の一覧である。**「この案を採用
すべき」「Productionをこう変更する」は書かない**。各項目は「観察された
事実」と「論点」を分けて記載する。

### 8-1. 現行設計で守れているもの

- **観察**: ER-009-N1-LEDGER-DEVIATION-RECALIBRATION-02で「意図的に危険な
  9種のfixture」全件がMAJOR判定を維持していることが検証済み(第6章)。
  post-hoc validation(`_apply_deviation_post_hoc_validation()`、
  `vfl01.py:544-561`)により、MAJOR/MINORの最終決定がモデルの自己申告
  ではなくcodeレベルで機械的に固定されている(第1-2章)。
- **論点**: この「守れている」評価はfixtureベースの検証(合成データ)で
  あり、Family Xの実運用データ(第3〜4章のA/B分類)でも同水準の精度が
  出ているかは、本調査のスコープ(統合・整理)では再検証していない
  (Part Bの15件サンプルのみが実データ)。

### 8-2. 過剰品質になっている可能性がある箇所

- **観察**: B-1(原油価格→ガソリン価格の一般化ブリッジ文)が、独立した
  4つのrun/trialで繰り返し同一パターンのMAJORを受けている(第3章B候補、
  第4章(iv)区分3件)。この一文はJA Writer Prompt自身が要求する構造要素
  (7-2、`jaw.py:58`)でもある。
- **論点**: 「Ledger範囲外の一般常識レベルの経済知識」と「Ledgerに無い
  新規具体的主張」の境界線をCheckerがどう扱うべきかは、本調査では判定
  しない。4回独立発生という再現性は、偶発的な誤判定ではなく構造的
  パターンである可能性を示唆する(第3章末尾)。

### 8-3. 緩和すると危険な箇所

- **観察**: A-2(価格方向反転、上げ幅縮小→"prices began to fall")・A-5
  (ロールバック↔再有効化の意味反転)は、事実の方向そのものが逆転する
  ケースであり、第4章(i)区分(絶対にSTOPすべき候補)に分類されている。
  A-3/A-4(支払義務者・対象範囲の具体的取り違え)も(ii)区分(高リスク)。
- **論点**: これらは「英語学習記事としての事実誤認」に直結する可能性が
  高いとPart Bは評価しているが、この評価自体も1回限りの目視分類であり
  合議・再現性検証は未実施(第4章の注記どおり)。

### 8-4. hard/softを分けられそうな箇所

- **観察**: `notes_for_writer`は設計時点(Researcher Prompt、`vfl01.py:157`)
  ではwriterへの執筆時ガイダンス(soft)として構想されたが、Ledgerテキスト
  への埋め込み(`vfl01.py:302-303`)後はDeviation Checkの判定根拠として
  他fieldと同列(事実上hard)に扱われている(第2章、Hormuz HF-011の
  explanation引用が直接証拠)。
- **観察**: `origin=ja_source`のMAJORは、深刻度区分(i)〜(iv)のいずれで
  あっても一律即STOP・retry対象外というfail-closed設計であり、問題の
  深刻度とSTOP時の挙動が連動していない(第4章末尾のアーキテクチャ観測)。
- **観察**: `changed_causality`・`changed_certainty`は、全母集団では
  MINOR比率が高いカテゴリ(changed_certainty: MAJOR9/MINOR49)だが、
  origin付きFamily X 15件ではchanged_causalityが5件ともMAJORのみで
  MINORが0件(第4章クロス集計)。severityの重み付けがcategoryごとに
  異なる可能性がある観察。
- **論点**: 上記いずれも「どこをhard/softに分けるべきか」の採用判断は
  本調査のスコープ外。

### 8-5. STOPではなくwarning・loggingの候補になり得る箇所

- **観察**: B-2(本件、Hormuz run_02)・B-3(接続詞"so")・B-4(3項目の
  一般化)は、第4章(iii)区分(品質改善の意味はあるがSTOP必須か疑問)に
  分類されている。B-2は問題視された断定文の直後1〜2文に留保文が存在する
  にもかかわらず、Deviation Checkはclaim単体を切り出して判定しており、
  記事全体の文脈上の自己限定を評価する仕組みが無い(7-3)。
- **論点**: 「claim単体判定」から「文脈込み判定」への変更が可能か・
  望ましいかは本調査では評価しない。auto_downgraded機構(MAJOR→MINOR
  自動降格)は既に存在するが、実データでは0件しか発火していない(第3章
  末尾)ため、現状の運用実態としては機能していない可能性がある(観察の
  みで、原因分析は本調査のスコープ外)。

### 8-6. 追加Trialが必要な論点

- **Checker非決定性の実測**: 同一入力(同一Ledger・同一記事文)に対して
  Checkerをn回実行した際の判定一致率は、本調査では実測していない
  (ER-009-N1-LEDGER-DEVIATION-RECALIBRATION-02で「実行ごとの非決定性は
  v2でも解消されていない」と定性的に記録されているのみ、第1-0章・7-3章)。
- **留保文を含むclaim単位判定の扱い**: 8-5で観察した「claim単体切り出し
  vs 文脈込み判定」の効果差は未検証。
- **Standard/Advanced対称Checkの必要性**: 第1-4章で確認した通り現状
  Standard(A2)にもAdvancedと同一のDeviation Checkが存在するが、両者を
  独立に実施することの効果(重複コスト対効果)は本調査では評価していない。

---

## 未解決問題・未計測項目(Part A/Bから集約)

1. **未確認**(Part A §未確認事項1): `notes_for_writer`の役割定義
   (soft guidance/hard constraint)を正面から議論した専用のDECISION_LOG
   エントリは、本調査のgrep範囲では発見できなかった。
2. **重大所見**(Part A §未確認事項2): JA R2 Fact CheckとEN Advanced
   Deviation Check(同一関数)が、内容的に対応する同一の主張に対して異なる
   MAJOR/COMPLIANT判定を下した実例をHormuz run_02で確認した(7-1)。個別
   記事の偶発事象という可能性と、Checker自体の非決定性に起因する構造的な
   再現可能性のある問題という可能性の両方が考えられ、本調査単独では判別
   できない。
3. **観察**(Part A §未確認事項3): run_01のHF-006事例は、JA Writer
   Prompt自体が要求する一般化ブリッジ文の構造的要求と、Deviation Checkの
   「Ledger範囲外の新規具体的主張禁止」という制約が矛盾し得ることを示す。
   JA Fact Check配線(2026-09-27以降)によりJA段で先に捕捉されるように
   なったが、JA段のCheckerも同一機構である以上、同種の緊張が解消された
   か、単にJA段での判定結果が偶然一致しただけかは、本調査だけでは判別
   できない。
4. OPEN-189(JA Fact Check固定費・latency最適化)は`OPEN(改善候補、ユーザ
   実検証後)`のまま未着手。
5. Human Review・attempt_historyへのCheckerの寄与は**未計測**(第5章)。
6. 「STOPまでの所要時間」の記事単位集計は**未計測**(第5章)。
7. Checker非決定性の定量実測(同一入力n回判定の一致率)は**未実施**(8-6)。
8. B-2(Hormuz run_02本件)は2026-09-29時点で**USER_DECISION_REQUIRED、
   次工程未着手**のまま(第3章)。

---

## 整合メモ(Part A/B間の矛盾・重複の明示)

- Part A(第1-0章)は「JA側とEN側は実装上まったく同一の1つの関数」と
  明記し、「JA側が甘い基準・EN側が厳しい基準という設計上の二段階は存在
  しない」と強調する。Part B(§0)は「10-category Ledger Deviation
  Checker schema」と「(参考扱いの)旧世代Checker」を区別し、後者を
  「英語原文記事(JA→EN翻訳を経ない)や旧世代Checker」と表現している。
  これは矛盾ではなく**対象範囲の違い**である: Part Aは現行Family X
  経路(JA→EN翻訳)内でのJA/EN比較に限定した記述であり、Part Bの
  「旧世代Checker」という語は、origin概念自体を持たない別のPipeline
  (pool_pilot/cefr_direct/Editorial B-Family等、209件)を指す。両者を
  同一の対象について矛盾する記述と誤読しないよう、本REPORTでは第3章冒頭
  で母集団の切り分け(origin付き15件 vs 全体224件)を明示した。
- Part A(第2章)はHormuz HF-011の1事例を根拠に「notes_for_writerの
  事実上のhard化」を論じ、Part B(第4章クロス集計)は15件全体の
  category分布から「changed_causality・unsupported_new_claimへの偏り」
  を論じている。両者は矛盾しないが、**評価の単位が異なる**(Part A=
  単一事例の深掘り、Part B=15件全体の統計)。本REPORTの2-4節で、
  Part Bのクロス集計がPart Aの単一事例観察を補強する形で整合すること
  を明示した。
- Part A(第6章)の「信頼性の最低ライン」表とPart B(第3-4章)のA/B
  分類は、直接には矛盾しないが、**評価軸が異なる**(Part A=10カテゴリ
  それぞれの正当性の根拠、Part B=15件個票の深刻度の目視分類)。両者を
  合わせて読むことで、「カテゴリとしては正当だが、適用結果として過剰
  品質(B-1等)/不十分(A-1等)の両方が実データ上で観察された」という
  第6章末尾の観察が成り立つ。

---

## 出典一覧(委任_01/_02のPart A/Bをそのまま参照)

- `docs/pm/investigation_ledger_deviation_check_01_part_a.md`(Part A、
  委任_01、2026-09-29)
- `docs/pm/investigation_ledger_deviation_check_01_part_b.md`(Part B、
  委任_02、2026-09-29)
- 上記2ファイルが引用する既存REPORT・DECISION_LOG・evidenceファイル
  (本REPORT内に転記した箇所を参照)

---

## 本調査の位置づけ(再確認)

本REPORTは、Part A/Bの統合と§8「再設計に向けた材料」の整理のみを行う
read-only調査である。**Production code・Prompt・Checker threshold・SSOT
(CURRENT_SPEC.md/DECISION_LOG.md/OPEN_ITEMS.md/HISTORY_INDEX.md)・
REPORT_LEDGERの変更は行っていない**。Family X E2E
(`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01`)はB-2(Hormuz run_02)の
USER_DECISION_REQUIREDのままSTOP状態を維持する。新Checker設計の素案
作成・採用判断は、本REPORTのスコープ外(ChatGPT側で作成後、Opus L2
レビューを経る想定、未実施)。

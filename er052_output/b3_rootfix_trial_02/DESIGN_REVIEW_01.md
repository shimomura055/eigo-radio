# DESIGN_REVIEW_01(B3-FACT-INSTRUCTION-SEPARATION-ROOTFIX-TRIAL-02 Phase 1、2026-10-10、課金API 0件)

範囲: Trial設計のみ。Production code / Production Prompt / CURRENT_SPEC / SSOT 不変更。Lane A C2編集中のファイル(er012_e / jaw / er019 entertainment runner / audio runner)は読んでいない。git操作なし。
前提(ユーザー確定 2026-10-10): 案D(Fact本文=台帳claimから決定論組立、注意書きは別ブロックへ逐語複写)=APPROVED_FOR_PRODUCTION。ただし問題1(中核/周辺数値ランク)・問題2(Storyline側への注意書き混入)を可能な限り同時に解消してから一体でProduction wiring。本書は両者を同時に扱うTrial構成の設計。

## 0. 現行B3 callの仕様(読取り結果)
- module: `er019_family_x_storyline_b3_fact_selection_01.py`(Production、未改変で参照のみ)。model=`gpt-6-luna`、effort=`high`(`vfl01.REASONING_EFFORT`)。1 call、Responses API、strict JSON schema。
- Prompt: DEVELOPER_MESSAGE(Editor役)+USER_PROMPT_TEMPLATE{topic, ledger_text(台帳全文を整形せずそのまま), 4テスト逐語}。手順5つ(Storyline決定/1行明示/全Factへ4テスト/selected・excluded/Selected Fact Brief作成)。採用目安3〜5件、6件以上はrecheck_note。
- 出力schema: `selected_storyline`, `fact_tests[{fact_id,test1..4,decision,reason}]`, `selected_fact_ids`, `selected_fact_brief`, `recheck_note`。技術retry=1回(JSON不正/未知fact_id/SELECTED_FACT_IDS_MISMATCH/空)。内容の善し悪しではretryしない。
- 入力: 台帳(`[VERIFIED|AMBIGUOUS…] ID: claim` + 2字下げ欄 scope/conditions/numeric_value/date_or_period/notes_for_writer/ambiguity_note/causal_strength)をそのまま渡す。つまり**Fact本文と注意書きは現行でも別欄として見えている**(混ざっているのは欄の中身ではなくB3の出力側=briefとStoryline)。AMBIGUOUSのヘッダタグ`[AMBIGUOUS - 断定禁止、曖昧さを保持すること]`は指示調。
- 実測(ROOTFIX-01 cost_ledger, C1 18 call): 平均 **JPY0.455/call**(max 0.72)、latency平均43.6秒、input平均3,643 token(2,315〜6,733)、output平均4,955 token(うちreasoning 3,295)、A'は+2.1%。(委任文の「JPY0.50」は丸め。実測値を使う。)
- 台帳欄分布(`b3_fact_instruction_separation_trial_01/ledger_stats_01.*` 再利用): 9テーマ、台帳Fact 6〜22件、採用3〜6件、notes_for_writerのうち命令形が大半(例 space 22件中18件)。numeric_value欄は全Factの約半数(46/98)にしかない=**数値欄のあるFactは限られる**。

## 1. Claude側設計レビュー(ユーザー6観点)
### 観点1 より単純な構造はないか → **あり。数値ランクの大半は機械規則であり、LLMが判断する部分は小さい**
Lane B注記仕様(`factlock_astra_e2e_trial_01/annotation/prompts/*__A.md` 3-5節)の中核/周辺は、(1)適格判定=主数字がnumeric_value欄に有る/日付がdate_or_period先頭と一致、(2)概念数nから上限`max(3,min(6,n//2))`、(3)優先順=Storylineに出る量→他の量→日付、(4)先頭から上限まで中核、で**機械的に決まる**(既存`b3_annotation_check_01.compute_expected`もこの規則で再計算し、LLMの宣言は使っていない)。LLMが必要なのは「どの表記を数値として拾うか」(ヘッジ語・範囲・日時の切り方)だけで、これも正規表現でほぼ拾える。
→ 簡素な順に4段の候補を比較する:
 - **D-det(新・LLM 0)**: claimから正規表現で表記を抽出し、台帳欄+Storylineから規則で中核/周辺を導出。B3 Prompt変更なし・追加call 0・追加費用0。
 - **D-plus-single-call**(ユーザー指定Trial A): B3に`number_ranks`を同一call内で出させる。
 - **Separate-call**(Trial B): 数値ランクだけ別call。
 - (参考)Lane B Sonnet注記(約JPY15.7/記事)=置換対象。
 **予備プローブ(¥0・Trial評価ではない・結果を見て基準を作らないため事前登録前の設計材料としてのみ使用)**: D-det(C0の採用ID・C0 Storyline)をLane B GT(`g0_real_annotation_01/<theme>/shared/annotation.json`、MERGED、C0 briefと同sha)と比較。GT数値(magnitude/date/range)47件のうちD-detが同じ主数字で対応付けられたのは38件で、**対応付け済み38件中36件で中核/周辺が一致**、GT中核25件のうち20件を中核として再現。未対応9件はGTの表記がC0 briefの言い換え文(例 small_bagの「2026年9月」はclaimに無い)由来で、claim由来のD-detが拾えない=**設計上の限界**(Writerに渡るのはclaim由来のFact文なので、D経路ではGTの比較基準そのものがずれる点に注意)。`ddet_preliminary_probe_01.txt`。D-detの抽出はclaimの数値を多く拾う(68概念 vs GT47)=GTより周辺が多い。
 **結論**: D-detをTrial腕に加えることを提案(費用0)。もしD-detが基準を満たすなら、LLM側の数値ランクは不要となり問題1は決定論で閉じる。D-plus/Separateはその比較対象(「規則では拾えない表記・概念」をLLMが埋めるか)としての位置づけ。これはユーザー指定構成への**追加提案**であり、Fable/ユーザー承認があるまで事前登録の本線には入れず「推奨追加腕」として記載する(下記5節)。

### 観点2 B3 Prompt変更範囲の最小化 → 追加のみ・削除なし(+約1,400字、約+750 token、+約20%)
`PROMPT_DIFF_01.md`(unified diff自動生成、Production sha `93d0e31e…`との置換12箇所を全てちょうど1回出現でassert)。変更は(1)【Ledgerの読み方】役割宣言(2)手順2末尾に「事実の記述だけ」(3)手順6 数値ランク(4)出力説明+schema末尾に`number_ranks`(5)入力整形`shape_ledger_for_b3`(欄ラベルのみ置換: notes_for_writer→`制約(notes_for_writer)`、ambiguity_note→`制約(ambiguity_note)`、値・ID行は不変)(6)number_ranksの技術検証。**既存手順1・3・4・5の文言、schema項目、4テスト逐語、retry回数は不変**。number_ranksをschemaの最後尾に置き、Fact選択・Storyline・briefの生成が先に完了してから数値を出させる(生成順序の副作用を最小化)。
 - さらに削る余地: 規則式(`max(3,min(6,floor(n/2)))`)をPromptから外し、LLMには表記とkindだけを出させて**roleを決定論で導出**すれば手順6が約半分になる(D-plus-lite)。D-plusの結果が「ROLE_DISAGREES_WITH_RULE」多発なら次の手として設計済みだが、今回は事前登録の本線に入れない(LLMのrole出力そのものの精度を測るため)。
 - `selected_fact_brief`はD経路ではWriterに渡らない(台帳claimから決定論組立)ので出力から外せば約200〜400 token減だが、「既存schema項目は削らない」指示により今回は残す。外す案は将来の簡素化候補として報告のみ。

### 観点3 既存B3 callだけで完結できるか → 技術的に可能(追加call 0)
number_ranksは同一callのstrict JSON schemaで出せる。追加call 0・追加retry経路なし。ただしreasoningの追加負荷(規則適用)が観点6のリスク。

### 観点4 Storyline品質を落とさないか
**重要な事実(¥0実測、ベースライン)**: ROOTFIX-01の既存C1出力18件+C0 9件のStoryline(各75〜155字・1行)に、指示調検出器`IMP`該当は **0/27**、notes_for_writerとの最長共通部分が12字以上は **3/27**(C1 1/18, C0 2/9。語の重なりが主で指示調ではない)。一方、「〜断定しない/確認されていない/〜ではない」等の限定表現を含むStorylineは C1 5/18、C0 4/9(台帳由来の限定であり正当な場合もあるが、注意書き由来が混入した可能性は人手目視が必要)。`baseline_storyline_contamination_01.json`。
→ **問題2(Storyline側への注意混入)は、ROOTFIX-01の観測範囲ではStoryline行に顕在化していない**(混入が顕在化していたのはSelected Fact Brief側で、D経路ではbrief出力を使わないので既に回避済み)。したがって役割宣言の効果は天井(ベースライン≒0)で測りにくく、**Trialでは「悪化させない(Storylineの質・長さ・Fact被覆・限定表現率がC1並み)」の確認が中心**になる。これは設計上の不確実性として明示する。
 - 評価: D-baseのStoryline(C1の18件、C0の9件、既存)とD-plusの18件を腕名を伏せてペア目視(9テーマ)。決定論指標=長さ/Fact被覆(Storylineの内容語が採用Fact claim群に含まれる率)/IMP該当/notes共通12字/限定表現率/Storyline内の数字が採用Factに存在するか(`STORYLINE_NUMBER_NOT_IN_SELECTED_FACTS`)。

### 観点5 注意書きを制約として見せることでFact選択・Storylineに悪影響が出ないか
現行も注意書き(notes_for_writer)は台帳欄として見えている。D-plusが変えるのは(a)欄ラベル(`制約(…)`)(b)役割宣言(「Fact選択の慎重さの参考にしてよいが転記しない」)の2点のみで、**新たに見せる情報はない**。悪影響の測り方: 選択Fact集合のJaccard。**ノイズ床(¥0実測、`baseline_selection_noise_floor_01.json`)**: C1自身のrep1 vs rep2で平均 **0.698**(9テーマ中完全一致2)、C0 vs C1 平均 0.648。すなわち同一入力でもB3の選択は大きく揺れる。したがってD-plusの合否は「C1のrep間ノイズ床より悪化しない」で判定し、絶対的な一致は要求しない(事前登録で数値化)。
 - 注意: 役割宣言が「制約に反する断定をしない」と書くことで、Storylineが限定表現を増やす(安全側)可能性。限定表現率で観測する。

### 観点6 同一callで数値ランクを足すことでB3本来性能が落ちないか
リスク: (a)reasoning増によるlatency/費用増(見積+8〜55%) (b)選択・Storylineの質低下 (c)strict schemaの出力肥大→max_output超過(C1最大output 8,168 token、A'最大10,585 token観測)。対策=事前登録で(b)をノイズ床比較、(a)を単価上限(C1の1.5倍、JPY0.70)、(c)は技術retry1回+truncation発生数を報告。**追加Checker・二重化・補正AIは使わない**(決定論検証のみ)。同一call方式で(b)が許容を超える場合に限り、Separate-callが「B3本体を無改変のまま数値だけ別callにする」代替として機能する(B3本体はD-base=Production無改変で済む点が最大の利点。ただし+1 call)。

## 2. 候補構成(確定)
| 腕 | 内容 | B3 Prompt | 追加call | 新規call数 |
|---|---|---|---|---|
| **D-base** | VALIDATED済み案D(ROOTFIX-01のC0 9本+C1 18本を**再利用**、claim(+scope/conditions)から決定論組立、注意は別ブロック逐語) | 無改変 | 0 | 0 |
| **D-plus-single-call** | 案D+同一callで`number_ranks`+Fact本文/制約の欄ラベル分離+役割宣言(Storyline制約) | 追加のみ(PROMPT_DIFF_01) | 0 | 9テーマ×2反復=18 |
| **Separate-call** | D-base相当の選択結果(C0の採用ID・C0 Storyline)に対し、数値ランクだけ別call | 無改変(別Prompt `b3r2_sepcall_01.py`) | +1/記事 | 9×2=18(Luna)。Sol比較は条件付き6 |
| **D-det(推奨追加腕)** | claim正規表現+規則で決定論導出 | 無改変 | 0 | 0(API費用0) |
| D-plus-min(任意) | 役割宣言のみ・ラベル整形なし(入力整形の寄与分離) | 追加のみ(SHAPE_MODE="none") | 0 | 18(Fable裁量) |
- D-baseのFact組立変種(D-min / D-full)は**ROOTFIX-01で未決**(ユーザー判断待ち)。本Trialの比較ではD-minを既定として明示し、変種は結果に影響しない評価(選択・ランク)に限定する。E9のみ影響するため変種を明記。
- Separate-callをC0の採用IDに対して実行する理由: (1)同一入力で2反復=選択ノイズを除いた純粋な数値ランク再現性が測れる (2)Lane B GT(C0 briefに対するMERGED注記)と同一入力で比較できる (3)D-detも同じ入力なので3者を同一条件で比較できる。D-plusは自身で選択するためGT直接比較は不可(自腕内の規則整合・欠落・人手目視で評価)。

## 3. 数値ランク構造(確定案)と決定論検証
```
number_ranks: [{fact_id: "HF-002", surface: "7月13日午前10時16分", kind: magnitude|date_time|range|year|ordinal|name_embedded, role: core|peripheral}]
```
- surface=当該Factの本文(ID行claim)に書かれた表記(数字+単位+ヘッジ語)。kindはLane B注記仕様3-2と同一6種。roleはcore/peripheral。
- 検証 `b3r2_rank_01.validate_number_ranks`(LLM不使用)。
 - **hard(技術不整合→B3既存の1回retry対象)**: `UNKNOWN_FACT_ID` / `FACT_NOT_SELECTED`(選択外Factの数値)/ `SURFACE_NOT_IN_FACT`(当該Factのclaim・numeric_value・date_or_periodのいずれにもNFKC一致で存在しない=新数字混入・Fact取り違え)/ `BAD_ROLE`・`BAD_KIND` / `DUPLICATE`。
 - **flags(報告のみ・retryしない=内容面の注意)**: `SURFACE_ONLY_IN_LEDGER_FIELD_NOT_CLAIM`(numeric_valueにだけある表記=Writerの本文に出ない)/ `MISSING_SURFACES`(claimに有る数字の欠落=regex抽出集合との差。regex誤検出あり得るので人手で確定)/ `NO_CORE` / `STORYLINE_NUMBER_NOT_IN_SELECTED_FACTS`(Storylineの数字が採用Factに無い)/ `ROLE_DISAGREES_WITH_RULE`(LLMのroleが規則導出と異なる)。
- 最終タグ付与は**決定論**`insert_marks`(原文不改変で表記末尾に【中核数値】/【周辺数値】を足すだけ。長い表記を優先し二重付与を防ぐ)。9テーマでround-trip(印を除くと原文一致)・二重付与0を確認済み(`selftest_result_01.json` ALL_PASS)。
- 「Fact取り違え」は、他の採用Factのclaimにだけある表記を別Factに紐付ける形で出る。selftestで`swapped_fact`を検出(hardエラー)することを確認。
- 台帳欄不足の扱い【委任_02で訂正(A3)】: 旧記述「当該Factにnumeric_value欄が無い場合は量は常にperipheralに倒れる」は不正確だった。仕様3-5-2は「**台帳に**numeric_value欄が1件も無い場合に限り、statement(Fact本文)の数字で代わりに比べる」(date_or_periodも同様)であり、判定単位は台帳全体。台帳に1件でも欄がある場合に限り、欄の無いFactの量/日付はcore候補にならずperipheralに倒れる。訂正後の規則をD-det(`b3r2_rank_01.eligible`)とStep6文言(`b3r2_sepcall_01.STEP6_RULES`)の両方に反映済み。(以下は旧記述の残り)台帳側にnumeric_value欄の無いFactが過半(46/98)である点は、Lane Bの数値ランクの上限を決める台帳側の事実であり、Trialでは変更しない。

## 4. Separate-call設計
- 入力: topic・Storyline・採用FactのID行claim+numeric_value+date_or_periodのみ(scope/conditions/制約は渡さない=役割分離・入力最小化)。出力: `number_ranks`のみ。手順6の定義はD-plusと逐語同一(`SEP.STEP6_RULES`、比較条件を揃える)。検証はD-plusと同一関数。
- model: 基本=`gpt-6-luna`(最廉価・B3と同一。gpt-6世代の最新だが最上位系かは未確認。評価用途の最新モデル原則(PM_GOVERNANCE 25節)に従い、Lunaが基準不達の場合に限り`gpt-6.1-sol`(登録単価 in$2/out$10)を6 call比較する条件付き腕)。effort=high(B3と同一)。
- **1記事あたり追加費用の見積(=見積。根拠: 入力token=dry-run実Prompt長×実測比[ROOTFIX-01 C1実測のprompt文字数→input_token昇順対応、比0.537(0.488〜0.591)]、出力tokenは仮定、単価=登録値)**: 平均入力約1,470 token(938〜1,991)。Luna: low JPY0.09 / mid 0.18 / high 0.38 (出力800/2,000/4,500 token仮定)。Sol(条件付き): 1.75 / 3.7 / 7.7。いずれもSonnet注記JPY15.7/記事より小さい(Luna約1/40〜1/170)。**実測は Phase 2 の最初のcall後に確定**。`ESTIMATE_01.json`。
- 利点: B3本体を無改変(Productionの検証済み挙動を保つ)。欠点: +1 call、+latency(別call分)、2段のFact ID整合管理、実装複雑性(別module・別retry・別cost記録)。

## 5. より単純な代替の検討結果
 1. **D-det**: 観点1。推奨追加腕(¥0)。数値ランクをLLMにさせないので、問題1の「B3本来性能が落ちない」リスクがそもそも無い。限界=regexで拾えない表記/概念束ね(例: 同一数値の異表記)。
 2. **決定論ルールで仮付与しB3には確認だけさせる**: 「確認」はLLMが決定論結果を承認/修正する二重化に近く、「追加Checker・二重化で解決しない」に抵触しやすい。採用しない(D-det単独 vs D-plusの比較で代替される)。
 3. **Storylineの注意文混入は入力分離だけで消えるか**: 入力ラベル分離(`制約(…)`)は現行入力でも別欄である点から効果が小さいと予想。ベースラインのStoryline IMP該当が0/27のため効果自体が測れない(観点4)。役割宣言のみ(D-plus-min)と整形+宣言(D-plus)の差を見るには任意腕D-plus-minが必要だが、ベースラインが天井のため情報量は低い。**任意腕は推奨しない**(費用JPY約9〜13)。Fable判断。

## 6. Lane A C2への interface 影響(列挙。Lane A編集中ファイルは読んでいない=下記の一部は「契約」であって実装確認ではない)
1. **B3出力契約**: D-plusはB3 JSONに`number_ranks`を追加(`selected_fact_brief`は後方互換で残すがD経路では不使用)。B3呼出側がschemaを固定している箇所は影響を受ける。
2. **R0入力契約(Writerニュース欄)**: D-base(案D)と同一の`compose_news_field(Facts, 制約ブロック)`。D-plusは加えてFact行・Storyline内の数値に【中核数値】/【周辺数値】を`insert_marks`で付与。`TAG_LEAK_RE`(`er052_factlock_astra_e2e_runner_01.py` L164)は【中核数値】【周辺数値】【事実N】を既に漏出検出対象としており、タグ方式自体は既存のFact Lock Writer契約と同じ。
3. **annotated B3 producer**: 現行は「B3 → Sonnet注記 → `b3_annotation_check_01`」。D-plus/D-det/Separate-callのいずれが採用されても、producerは「決定論assembler(D)+`number_ranks`→`insert_marks`」になり、Sonnet注記call(約JPY15.7)は不要になりうる。ただしannotation.jsonの`numbers[].role`(日本語の説明文)・`concept`・`unmapped_claims`を誰が作るか、既存検査(a〜e)が通るかは**未確認**(Phase 2で、assemblerの出力に既存`b3_annotation_check_01.py`を適用して合否を見る予定=新Checkerは作らない)。
4. **number rank情報の運び方**: `fact_selection_evidence_*.json`に`number_ranks`(または`numbers`)を追加する必要が出る。既存`annotated_json_from`/`md_facts_of_json`(runner L225-239)が読む形(`facts[{n,ledger_ids}]`, `numbers[{surface,kind,class,concept,ledger_ids,role}]`)に合わせる変換が要る。`class`=role、`ledger_ids`=[fact_id]、`concept`=主数字キーはD-detの`derive_ranks`が既に出す。
5. **Writer制約欄**: D-baseと同一(`事実Nについて：notes`逐語、【事実N】番号一致)。D-plusでも変更なし。
6. **衝突回避**: 本Trialはer012_e/jaw/er019 entertainment/audio runnerを読まず、importもしない。`b3sep_build_01`(Trial_01 module)と`b3sep_common_01`のみ読み取りimport。

## 7. Opus独立技術レビューGate(PM_GOVERNANCE 11-3)
D-plus-single-call(B3の出力契約変更+決定論assembler+タグ付与の新しい処理フロー)は条件A「新しい構造・処理フローの設計」に該当しうる。本委任(Sonnet実行層)はAgent起動禁止のため実施していない。**Fable判断**: Phase 2実行前にOpus独立レビューを入れるか、Trial結果後(Production採用提案前=条件C)にまとめて入れるか。

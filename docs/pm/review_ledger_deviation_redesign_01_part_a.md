# LEDGER-DEVIATION-CHECK-REDESIGN-REVIEW-01 Part A(Repo/実装整合レビュー、read-only)

**Status**: レビュータスク(read-only)。Production code/Prompt/Schema/SSOT
変更なし。採用・実装判断はしない。批判的検証を主眼とする。

対象: ChatGPT再設計素案(A〜J、`docs/pm/delegation_log/
2026-09-29_LEDGER-DEVIATION-CHECK-REDESIGN-REVIEW-01_01.md`に転記した委任文
参照)。前提REPORT: `LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_REPORT.md`
(commit `247e0a1f`)。

---

## C. Repo / 実装整合

### C-1. 素案ごとの変更箇所(現行code対応)

| 素案 | 変更が必要な箇所 |
|---|---|
| A(検出/実害/severity/action分離) | `vfl01.run_deviation_check()`のprompt/schemaは「検出」まで。「実害評価→severity決定→action決定」は**現状どこにも実装がない新レイヤー**。post-hocは`_apply_deviation_post_hoc_validation()`(`vfl01.py:544-561`)のみで、これは10フラグ真偽→MAJOR/MINORの機械固定のみ行い、「実害があるか」は判定しない。新規に呼び出し側(`er012_e...py`/`er019...py`)へsevierty→action対応表を実装する必要がある |
| B(3層severity) | schema(`DEVIATION_JSON_SCHEMA`/`_extended_deviation_item_schema`)の`severity` enumが`["MINOR","MAJOR"]`固定(`vfl01.py:466`,`713`)。3層化にはenum変更+`DEVIATION_PROMPT_TEMPLATE`(`vfl01.py:531-537`「10種類のいずれかが明確にtrueである場合のみMAJOR」の記述自体を書き換え不可避)+post-hoc関数の全面書き換えが必要 |
| C(changed_causality細分化) | `DEVIATION_PROMPT_TEMPLATE`の`changed_causality`定義行(`vfl01.py:514`「相関を因果に変えている、または因果の方向を変えている」)はBlocking/Non-blockingを区別しない単一boolean。post-hocにもcausality専用ロジックは無い。Prompt文言変更またはpost-hocでの下位分類ロジック新設が必須 |
| D(context window判定) | `run_deviation_check()`は`article_text`全体を渡すが、判定は`claim_in_article`単位(`vfl01.py:464`)。前後1-2文契約は**現行promptに明示の指示が無い**(第7章7-3で確認済み: 「記事全体の文脈上の自己限定を評価する仕組みは無い」)。Prompt文言追加が必要 |
| E(notes_for_writer soft化) | `build_verified_ledger_text()`(`vfl01.py:302-303`)がnotes_for_writerを他fieldと同列にテキスト埋込。分離するには(i)Ledgerテキスト生成関数の改修、(ii)`DEVIATION_PROMPT_TEMPLATE`側で「notes_for_writer由来の指摘はhard判定に使わない」旨の除外規定追加、の両方が必要(片方だけでは不十分、後述C-4) |
| F(JA=Fact事故除去/EN=翻訳整合) | `origin`分岐は既に`JARecheckRequiredError`(`er012_e...py:266-274`)で実装済みだが、現行は「origin=ja_source→即STOP」の単純ロジック。「severityで action決定」への変更は同ファイルL388-398,484-498の分岐ロジック書き換えが必要 |
| G(4call見直し) | `er019...py`(JA Original/R2 Fact Check、2call)+`er012_e...py`(Advanced/Standard Deviation Check、2call)の4呼び出し箇所。どれかを削るには呼び出し元コードの削除+Ledger連携経路の見直しが必要(単純) |
| H(deterministic post-processing) | 現状の`_apply_deviation_post_hoc_validation()`は10フラグ真偽のみを見る非常に薄い後処理。「actor changed+Ledger entity mismatch→BLOCKING」等の照合には、Ledgerの`subject`/`numeric_value`等の構造化fieldとdeviation側の`claim_in_article`テキストとの**突合ロジックが現状存在しない**(deviation側はfree textのみ返す。related_fact_idはあるがLedgerとの値レベル比較は無い) |
| I(Human Review非常口) | `JAFactCheckStopError`/`RuntimeError`/`JARecheckRequiredError`はいずれも**即STOP**であり、Human Review Queueへの自動エスカレーション経路が無い(既存Human Review Lockは音声TTS/ASR側の別機構`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`であり、Deviation Check系のSTOPはこのqueueへ書き込まれない、第5章で確認済み「Ledger Deviation Checker/JA Fact Check起因のHuman Reviewエスカレーションは1件も確認できなかった」)。素案Iを実装するには新規の書き込み経路が必要 |
| J(Disclaimer) | code変更なし、運用方針の話 |

### C-2. `_apply_deviation_post_hoc_validation()`のreuse可能性

現在機械固定しているのは**「10フラグ全てfalseなのにMAJOR」→MINOR降格**の
1点のみ(`vfl01.py:552-556`)。それ以外は一切の後処理を行わない
(`auto_downgraded`はこの1経路でのみtrueになりうるが実データでは0件、
REPORT第3章末尾)。Severity 3層化・deterministic ruleの置き場としては
**関数の骨格(raw_parsed→deviations加工→overall_status再計算という構造)
は再利用できるが、中身のロジックはほぼ全面新規実装が必要**。現状「10種の
いずれかがtrue」以上の情報(どのフラグが、どの深さで、Ledgerのどのfield
とどう矛盾したか)を機械的に取得する仕組みがそもそも無いため、素案Hの
「actor changed+Ledger entity mismatch」等の**値レベル照合はfromゼロで
書く**ことになる。

### C-3. Schema変更の要否

- `severity`をMINOR/MAJORの2値からBLOCKING/QUALITY/ACCEPTABLEの3値
  (または`severity`+`severity_final`の2フィールド)に変えると、**既存
  481ファイル・224件個票のseverity値と非互換**になる(REPORT第3章の
  母集団統計はMAJOR/MINORの2値集計。REPORT自体・過去の全DECISION_LOG
  エントリ・REPORT_LEDGER集計ロジックが2値前提)。後方互換を保つ選択肢は
  「新フィールド`severity_final`/`action`を追加し、既存`severity`は
  維持」だが、この場合MAJORの意味(「must-fix対象」か「単なる10-flag
  発火」か)が二重化し、既存コード(`_major_deviations()`が
  `severity=="MAJOR"`だけを見て抽出、`er012_e...py:278`/`er019...py:184`)
  をどちらのフィールドで判定するか全呼び出し元で書き換えが必要。
- `context_evidence`/`ledger_field_basis`の追加は、既存`strict: True`の
  JSON Schema(`additionalProperties: False`、`vfl01.py:485`,`490`等)に
  対する**破壊的変更**であり、既存テスト(`er003_v1_en_direct_vfl_01_
  generate_test_01.py`、`run_deviation_check(`の呼び出し元として本レビュー
  のGrepで検出済み)が固定するJSON構造との整合を全て洗い直す必要がある。
- `FACT_LEDGER_JSON_SCHEMA`(`vfl01.py:78-126`)からnotes_for_writerを
  hard field群と分離する場合、`required`配列(`vfl01.py:113-117`)に
  notes_for_writerが含まれているため、分離先を「別array」等にすると
  Researcher出力schema自体が変わり、**過去の全Ledger資産(JAテキスト化
  済みの`verified_fact_ledger.txt`)との後方互換は無い**(過去生成物は
  新schemaで再パースできない。ただし過去Ledgerはテキストとして保存され
  再利用されないため実害は小さい可能性がある、要確認)。

### C-4. Prompt変更の要否

Prompt変更なしで(呼び出し側・post-hocのみで)実現できる可能性があるもの:
- E(notes_for_writer downgrade)の**一部**: `related_fact_id`が
  notes_for_writer由来であることをdeterministicに判定できれば
  (C-5参照)、呼び出し側でMAJORをdowngradeする後処理は追加できる。ただし
  Deviation Check自体が「notes_for_writerの文言を判定根拠として使う」
  という挙動(Hormuz HF-011の実例、REPORT 2-1)はPrompt側の問題であり、
  post-hocでの降格は「一度MAJORと判定させてから機械的に打ち消す」形に
  なり、素案Eの意図(そもそもsoft扱いとして判定させない)とは異なる。

Prompt変更が不可避なもの:
- B(3層severity)の`severity` enum自体
- C(causality細分化の判定基準)
- D(context window判定、claim単体切り出し設計自体の変更)
- 「notes_for_writerを判定根拠に使わない」という**判定入力からの除外**
  (post-hocでは「後から見えた結果を打ち消す」ことしかできず、「そもそも
  見せない」ことはPrompt/入力構築側の変更が必要)

**Prompt変更は`vfl01.run_deviation_check()`の共有関数のため、Family
A(`er003_v1_n3_01_articles_generate.py`)・B(`er012_b_family_production_
runner_01.py`等)・C(`er013_family_c_future_safety_06.py`)・X(JA/Advanced/
Standard)の全呼び出し元へ同時に波及する**(REPORT第1-0章で確認済みの
「同一関数」という事実そのもの)。Family Xだけを対象にした限定的な文言
変更を行いたい場合、`hook_aware`と同様に**新しい`prompt_variant`引数を
追加して分岐する**設計変更が必要になる(現状そのような汎用フラグは無く、
`hook_aware`はHook専用の狭い分岐)。

### C-5. deterministic ruleとして実装できる部分/できない部分

現行audit json(`deviation_audit_record()`、`vfl01.py:755-770`)から
取得できる入力: `parsed.deviations[].{claim_in_article, issue, severity,
10フラグ, explanation, related_fact_id, origin}`のみ。

| ruleの候補 | 現行audit jsonで実装可能か |
|---|---|
| notes_for_writerのみを根拠とする降格 | **不可**。`explanation`は自由文であり、根拠が`notes_for_writer`由来かLedgerの他fieldかを機械的に区別する構造化情報が無い(`related_fact_id`はfact単位までしか特定しない、fact内のどのfieldを参照したかは記録されない)。新schemaで`ledger_field_basis`のような専用フィールドをモデルに出力させる必要がある(=Prompt/Schema変更前提、C-4のE参照) |
| changed_number/actor/negation/comparison/timeのLedger値との機械照合 | **限定的に可能**。`related_fact_id`があればLedger側の`numeric_value`/`subject`等をfact_idで引き当てられるが、`claim_in_article`(記事側の該当文字列)からLedger値を突合する自動抽出ロジックは無く、結局「一致しているか」の最終判断はLLM任せになる。数値の完全一致チェック程度なら文字列比較で実装可能 |
| 限定語・qualifier検出(素案H「限定表現+直後qualifier」) | **不可**(構造化されていない自由文からの検出は本質的にNLPタスクであり、deterministicなキーワード一致では"large, lasting"のような表現を安定検出できない。Hormuz実例で観察したのは1事例のみ、汎化未検証) |
| origin=ja_source × severity のAction表 | **可能**(`origin`と`severity`は共に既存構造化フィールドであり、素案A/Bのsevirity値さえ定義されれば単純なlookup tableで実装できる。ただしseverity自体が3層化されない限りORIGIN×MAJOR/MINORの2x2表にしかならない) |

LLM判断に残すべき部分: 「意味が変わったかどうか」自体の判定(paraphrase
境界)は本質的に自然言語理解が必要でありdeterministic化不可能。context
window判定(素案D)も文脈理解を要するためLLM任せにならざるを得ない。

### C-6. retry/origin/exception構造への影響

`JARecheckRequiredError`(`er012_e...py:266-274`)・`JAFactCheckStopError`
(`er019...py:169-181`)・`RuntimeError`(`er012_e...py:409-431`,
`427-431`)の3種をSeverity×Actionへ再編する場合:
- `er012_e...py::run_writer_stage()`のAdvanced(L380-431)/Standard
  (L476-522)双方の分岐を書き換える必要がある(対称構造のため2箇所同時)
- `er019...py::run_ja_writer_o_r1_r2()`のOriginal(L263-310)/R2
  (L375-438)双方も同様
- `--stage writer`単独実行(委任文に記載、本レビューでは該当箇所を
  直接コード確認していない。**未確認**: 単独実行時にexceptionハンドリング
  が呼び出し元runnerでどう扱われるかは別途確認が必要)
- `build_must_fix_block()`(`er019...py:125-145`)は現状`must_fix`
  リスト全件を無条件でブロック化する。BLOCKING限定にする場合、呼び出し側
  で事前にBLOCKING分のみへフィルタする処理を追加する必要がある(関数
  自体は汎用的で変更不要な可能性が高い)

### C-7. drift防止構造の選択肢(採用しない、列挙のみ)

- 選択肢1: `vfl01.py`内に`classify_severity(deviation: dict) -> str`の
  ような単一関数を新設し、`er012_e`/`er019`/将来の他Family runnerは
  この関数の戻り値のみを見てAction分岐する(現状の`_major_deviations()`
  が両ファイルに重複実装されている、`er012_e...py:277-278`と
  `er019...py:184-185`はほぼ同一コード=**既に軽度のdrift観察**)
- 選択肢2: Action表自体を呼び出し側ごとに独自定義させる(JA用/EN用で
  異なるAction、ただしdrift再発リスクが高い)
- 選択肢3: 現状維持(vfl01側はseverity/originのみ返し、Action判断は
  呼び出し側に委ねる現行設計のまま)

### C-8. Family A/B/C/Z への波及

`run_deviation_check(`呼び出し元(Trialファイル除く、"trial"を含まない
ファイル名でGrep)は本レビューで89件ヒットのうち48件(Trial除外後)。
現行Productionと確認できる代表例: `er003_v1_n3_01_articles_generate.py`
(Family A、hook_aware=True固定)、`er012_b_family_production_runner_01.py`
/`er012_b_family_voices_a2_production_01.py`(Family B)、
`er013_family_c_future_safety_06.py`(Family C)、`er012_e_family_
entertainment_two_level_runner_01.py`+`er019_family_x_ja_writer_o_r1_r2_
01.py`(Family X)。Family Z(`er026_family_z_fiction_production_runner_
01.py`)は`vfl01`をimportするが`run_deviation_check(`は未呼び出し(将来
利用、L60/L634で`get_client()`のみ確認)。**Severity 3層化はこれら全ての
呼び出し元のoverall_status判定(`LEDGER_COMPLIANT`/`LEDGER_DEVIATION`)・
Gate分岐・REPORT集計(224件個票の既存MAJOR/MINOR統計)へ同時に影響する**。
Family A(hook_aware)は8種のフラグを常時判定する専用分岐があり
(`vfl01.py:571-573`)、3層化する場合はHook-aware側のprompt
(`HOOK_AWARE_DEVIATION_PROMPT_TEMPLATE`)も二重に書き換える必要がある。

---

## D. QCD

### D-1. 4call削減余地(素案G)

各callの役割(REPORT第1章より): JA Original Check(新規生成直後、Full
Ledger照合)/JA R2 Check(改稿確定後、同型Check)/Advanced Deviation
Check(英訳段、origin判定付き)/Standard Deviation Check(A2版、Advanced
と完全対称)。

- **削ってはいけない候補の実測根拠**: A-1事例(REPORT第3章、Meta記事の
  時制ドリフト)は「Checkerが2回とも見逃した」ケースであり、call数を
  減らす根拠にはならない(むしろ見逃しは既存4callでも発生している)。
- **重複検出の実データ**(本レビューで独自集計、scratchpadスクリプト、
  ¥0): Family X系(`family_x_b3_diversity_trial_01`/`family_x_refresh_
  e2e_01`)のdeviation_checksファイル26件・15 run分をrelated_fact_id基準
  でJA stage MAJORとEN stage(Advanced/Standard) MAJORの重複を機械集計
  した結果、**重複0件**(JA側MAJORはmust-fixで解消されてから英訳段が
  実行されるため、最終状態のJSONにはJA由来の未解消MAJORがそもそも残ら
  ない設計上の理由による可能性が高い。この集計方法では「本質的に同じ
  claimを2度チェックしている」ことの直接証明にはならない、限界あり)。
  **したがって「JA R2とAdvancedが同じLedger・ほぼ同じ内容を判定している」
  という素案Gの前提を、related_fact_id突合という機械的な方法では裏付け
  られなかった**(定性的にはHormuz run_02[REPORT第7章]でJA R2は
  COMPLIANT・Advancedのみ同一論点でMAJORという「不一致」の実例はあるが、
  「重複」ではなく「不一致」であり、素案Gが想定する「無駄な二重判定」
  とは異なる観察)。
- Standard(A2)をtranslation-diff限定にする案は、Standardが「Advancedの
  再翻訳・簡略化」でありAdvanced自体がJA由来の問題を解消済みの前提であれば
  理屈は成立しうるが、**Standard生成はAdvanced本文からの再生成であり
  (`er012_e...py:460`、`advanced_text`を入力)JA原文を直接参照しない
  ため、Standard側で新たに生じるtranslation起因の逸脱をAdvanced段の
  Diffだけで検出できるかは未検証**(本調査スコープ外、Trial対象)。

### D-2. latency/cost削減の可能性(数値は実測範囲のみ)

Checker単発コール中央値¥0.90/33秒(REPORT第5章、n=12実測)。4call合計は
単純計算で約¥3.6/130秒程度(実測合算値ではなく単発中央値×4の概算、
実測合計値は本調査では未算出)。reasoning=high見直し・call統合の効果は
「可能性」の域を出ず、本調査では未実測。

### D-3. 二重・重複Checkの箇所

構造上「同一Ledgerを複数回判定している」箇所自体は事実(JA Original/R2/
Advanced/Standardいずれも同一`ledger_text`を`verified_ledger_text`に
渡す、`er012_e...py:381-382`,`477-478`、`er019...py:265-266`)。ただし
D-1のとおり、これが「実質的に無駄」かは重複検出の実データでは裏付け
られず、**「対称構造だが判定対象テキストが異なる(JA文/Advanced英文/
Standard英文はそれぞれ内容が異なりうる)」という反論も成立しうる**点は
素案Gへの弱点として指摘する。

---

## 既存仕様との競合

| 既存決定 | 競合点 |
|---|---|
| ER-009-N1-LEDGER-DEVIATION-RECALIBRATION-02(「意図的に危険な9種の fixtureは全てMAJOR判定を維持」検証済み、REPORT第6章) | 素案B(3層化)・素案C(causality細分化)を実装する場合、この既存fixture群での再検証(9種全てが引き続き適切なsevirity[BLOCKING相当]になるか)が必須。fixtureが2値(MAJOR/MINOR)前提で設計されている場合、3層化後の再テストが必要 |
| 「安全≠成功」原則(`PM_GOVERNANCE.md`6節、「安全になっただけでは成功としない」) | 直接の反対ではないが、素案は逆方向(「検出を絞る」)の変更であり、この原則が要求する「面白さ・分かりやすさの劣化がないか」の確認とは別軸。素案採用により**過検知は減るが過少検知(見逃し)が増えるリスク**があり、原則の「安全側に倒す」という基本姿勢との緊張関係が生じうる(原則自体は品質劣化側を懸念しており逆方向だが、「安全側の判断を緩める」変更全般に慎重であるべきという趣旨は共通)★ |
| fail-closed設計(origin=ja_source即STOP、`er012_e...py:266-274`のコメント「Englishを盲目的に再生成せず、JA側の再確認が必要」という設計意図、`CURRENT_SPEC.md:1220-1223`) | 素案F(「EN側でorigin=ja_sourceでも一律即STOPにせずseverityでAction」)はこの既存fail-closed設計の緩和そのもの。`CURRENT_SPEC.md`の正式仕様記述を変更する必要がある★ |
| JA Fact Check配線決定(`NEWS-FAMILY-X-JA-FACT-CHECK-PRODUCTION-WIRING-01`、2026-09-27、Fable Gate 3判定`PRODUCTION_WIRED`、OPEN-187備考2) | この配線自体が「JA正なら英訳must-fix retry、JA誤ならJA側へ戻す」というユーザー基本方針の実装であり、素案A/Fはこの配線のAction判定部分を再設計する提案に当たる。配線決定自体を撤回するわけではないが、Action分岐ロジックの変更はこの決定に対する修正として扱う必要がある★ |
| OPEN-189(JA Fact Check固定費・latency最適化、`OPEN(改善候補、ユーザ実検証後)`) | 素案Gの「4 call見直し」はOPEN-189の候補(1)〜(4)と一部重複する内容であり、別のOPEN Itemとして先行登録済み。統合または重複整理が必要 |
| Human Review Lock仕様(既存は音声TTS/ASR専用機構、REPORT第5章「Ledger Deviation Checker/JA Fact Check起因のHuman Reviewエスカレーションは1件も確認できなかった」) | 素案I(「Human Reviewは非常口」)は、Deviation Check系のSTOPを**既存の音声用Human Review Lock機構(`review_lock_state.json`、`er011_human_review_lock_01.py`相当)へ統合するのか、別の新規queueを作るのか**が未定義。既存機構への統合は、既存のapprove_regenerate()等のAPIが「音声attemptの再生成許可」を前提に設計されている可能性があり、記事本文のFact逸脱という異なる種類の承認対象を同じ機構に載せてよいかは要確認(**未確認**、本レビューでは`er011_human_review_lock_01.py`のAPI詳細は読んでいない)★ |
| B-2(Hormuz run_02)USER_DECISION_REQUIRED(2026-09-29時点、次工程未着手) | 素案全体の検証背景そのものであり、本レビュー中もFamily X E2E再開は禁止(委任範囲内で遵守済み)。素案採用判断が下されるまでB-2自体は解決しない |

---

## 再発防止(F)

過剰品質問題(B-1: 原油→ガソリン価格ブリッジ文が4回独立発生)の再発防止の
置き場候補(現行repo構造に即して):

- **regression fixture**: `er009_ledger_deviation_recalibration_02.py`/
  `er009_ledger_deviation_recalibration_02_test.py`が既存の「危険9種
  fixture」の維持を検証する仕組みを持つ。同様に「過剰品質側」のfixture
  (B-1のような繰り返し過検知パターン)を追加登録し、post-hoc変更のたびに
  両方向(見逃し増加なし・過検知減少)を回帰確認する仕組みが考えられる
  (現状は危険側のfixtureのみで、過剰品質側のfixtureは無い、REPORT第8-1章
  の指摘と符合)。
- **OPEN_ITEMS**: OPEN-187/OPEN-189に加え、B-1パターン専用のOPEN Item
  として新規登録し、「Ledger範囲外の一般常識レベルの経済知識」の許容
  基準をPromptの「許容範囲」節(`vfl01.py:523-529`)へ追記する候補として
  追跡する(現状はA/Bどちらの分類に倒すか未決定のまま埋もれている)。
- **auto_downgraded機構**: 既存の降格ログ機構(`auto_downgraded`フィールド)
  は実データで0件しか発火していない(第3章末尾)。これは「機能していない」
  のではなく「10フラグ全falseでMAJORという矛盾したモデル出力自体が
  レア」という意味であり、素案Hのような新しい降格ルールを追加する場合は
  同じ`auto_downgraded`的なフラグ(例: `context_downgraded`)を追加して
  ログに残し、REPORT集計時に「新ルールがどれだけ発火したか」を追跡可能に
  する設計が望ましい(採用判断はしない)。
- **SSOT**: 3層化・deterministic rule導入を採用する場合、CURRENT_SPEC.md
  の当該Deviation Check節・DECISION_LOGへの正式decision entry追加は
  必須(ER-009-N1の前例と同型)。

---

## ★新しいProduct判断が必要な事項(まとめ)

1. fail-closed(origin=ja_source即STOP)を緩和するかどうか(素案F、
   `CURRENT_SPEC.md`正式仕様の変更を伴う)
2. 「安全側判断を緩める」変更全般について、「安全≠成功」原則との整合を
   どう説明するか(過検知減少と見逃し増加のトレードオフをユーザーがどこまで
   許容するか)
3. JA Fact Check配線決定(2026-09-27、Gate 3 PRODUCTION_WIRED)のAction
   ロジックを事実上再設計することになる点をユーザーへ明示するか
4. Human Review非常口(素案I)を既存の音声用Human Review Lock機構に
   統合するか、別queueを新設するか(既存API仕様の詳細未確認のまま提案
   されている)
5. Ledger schema(notes_for_writer分離)・Deviation schema拡張による
   既存224件個票・過去REPORT統計との後方互換をどう扱うか(集計方法の
   変更が必要になる可能性)

---

## 出典・根拠一覧

- `LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_REPORT.md`(commit
  `247e0a1f`)第1〜8章、未解決問題節
- `er003_v1_en_direct_vfl_01_generate.py:78-126,275-305,313-344,434-561,
  602-631,634-839`
- `er012_e_family_entertainment_two_level_runner_01.py:262-546`
- `er019_family_x_ja_writer_o_r1_r2_01.py:120-330`
- `OPEN_ITEMS.md`(OPEN-183備考6/OPEN-187/OPEN-189)
- `docs/pm/PM_GOVERNANCE.md:562-566`(6節「安全になっただけでは成功と
  しない」原則)
- `DECISION_LOG.md:9540`(安全≠成功原則の参照箇所)
- 独自集計(scratchpad、¥0): Family X系deviation_checks 26ファイル・15 run
  でrelated_fact_id突合、JA/EN間のMAJOR重複0件(方法論の限界は本文D-1参照)

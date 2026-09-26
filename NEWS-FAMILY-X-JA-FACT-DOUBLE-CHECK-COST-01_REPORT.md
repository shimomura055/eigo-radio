# NEWS-FAMILY-X-JA-FACT-DOUBLE-CHECK-COST-01

性質: コスト・latency確認(read-only)。実装・Trial(生成物のProduction/正式Trial扱いは無し)・
Production変更・SSOT編集は一切行っていない。既存Production artifact(`er019_output/family_x_b3_production_wiring_01/**`等)は無変更。
今回、実測精度向上のためCheckerの実測1回分として許可された範囲内(最大¥3)で実API呼び出しを2回行った
(合計¥2.1962、上限内)。証跡は `er019_output/ja_fact_double_check_cost_01/`(Trial用out-dir、新規)へ保存。
推奨・採否は記載しない(数字のみ)。

## §0 要約表(固定費/変動費/latency)

### Checker単発コール(実測値、n=12: 今回のJA直接測定2件 + 既存Production/Trialログ由来10件、すべてmodel=`gpt-5.6-luna`, reasoning effort=`high`)

| 指標 | 値 |
|---|---|
| 最小 | ¥0.323 |
| 中央値 | ¥0.9024 |
| 平均 | ¥0.954 |
| 最大 | ¥1.6505 |

latency(同n=12、Checker単発コールのみ、generate呼び出しは除く):

| 指標 | 値(秒) |
|---|---|
| 最小 | 9.55 |
| 中央値 | 33.16 |
| 平均 | 38.07 |
| 最大 | 84.89 |

### 今回実測した「JA記事に対する直接ダブルチェック」の実例(1記事、real API call、n=1)

| 段 | article文字数 | input_tokens | output_tokens(うちreasoning) | cost(JPY) | elapsed(秒) | overall_status |
|---|---|---|---|---|---|---|
| JA Original後Checker | 852字 | 4724 | 7809(7584) | ¥1.6505 | 84.889 | LEDGER_DEVIATION(MAJOR 1件) |
| JA R2後Checker | 974字 | 4789 | 2044(2024) | ¥0.5457 | 25.211 | LEDGER_COMPLIANT |
| 合計(ダブル) | - | - | - | **¥2.1962** | **110.10(逐次実行の合計)** | - |

### 1/10/30/100記事換算(固定費のみ、NG発生時の再生成費用は含まない、§2で別掲)

| パターン | 単価根拠 | 1記事 | 10記事 | 30記事 | 100記事 |
|---|---|---|---|---|---|
| Original後のみ(中央値ベース) | ¥0.9024/回 | ¥0.90 | ¥9.02 | ¥27.07 | ¥90.24 |
| Original後のみ(今回実測例) | ¥1.6505/回 | ¥1.65 | ¥16.51 | ¥49.52 | ¥165.05 |
| R2後のみ(中央値ベース) | ¥0.9024/回 | ¥0.90 | ¥9.02 | ¥27.07 | ¥90.24 |
| R2後のみ(今回実測例) | ¥0.5457/回 | ¥0.55 | ¥5.46 | ¥16.37 | ¥54.57 |
| ダブル(中央値ベース、2回) | ¥1.8048/記事 | ¥1.80 | ¥18.05 | ¥54.14 | ¥180.48 |
| ダブル(今回実測例、2回) | ¥2.1962/記事 | ¥2.20 | ¥21.96 | ¥65.89 | ¥219.62 |

latency換算(1記事あたり、逐次実行・パイプライン内の追加待ち時間として):

| パターン | 中央値ベース | 今回実測例 |
|---|---|---|
| Original後のみ | 33.16秒 | 84.89秒 |
| R2後のみ | 33.16秒 | 25.21秒 |
| ダブル(合計) | 66.32秒 | 110.10秒 |

※ reasoning_tokensの分散が大きく(899〜7584)、コスト・latencyともに個別記事で±2倍以上ぶれる。中央値ベースはn=12の安定推定、実測例はn=1の実際の記事1本の生値。

## §1 Checker固定費(根拠ログ逐語・token内訳)

### 1-1. 既存関数の実体確認

`er003_v1_en_direct_vfl_01_generate.py::run_deviation_check()`(L634-657)を実測根拠として使用。
シグネチャ: `run_deviation_check(client, verified_ledger_text, article_text, model=MODEL, hook_aware=False)`。
`MODEL = routing.WRITER_MODEL`(`"gpt-5.6-luna"`)、`REASONING_EFFORT = r3.WRITER_REASONING_EFFORT`(`"high"`、
モジュール定数として関数本体にハードコードされており、呼び出し時の引数では上書きできない)。

`DEVIATION_DEVELOPER_MESSAGE`(L495-500)・`DEVIATION_PROMPT_TEMPLATE`(L502-541)は**既に全文日本語**で書かれている
(`article_text`が日本語か英語かを区別する記述は一切ない。英語専用の指示・アルファベット圏を前提にした表現は存在しない)。
現行のProduction呼び出し元(`er012_e_family_entertainment_two_level_runner_01.py::run_writer_stage()`)は
`advanced_text`/`standard_text`(いずれも英語)をこの関数に渡しているが、それは呼び出し側がそう渡しているだけであり、
関数自体・prompt自体に英語前提の実装は存在しない。

### 1-2. 既存ログからの実測(Production/Diversity Trial、EN側article_textに対するCheckerコール)

`er019_output/family_x_b3_production_wiring_01/run_01/raw_usage_log.jsonl`(全18行)より、`stage="advanced"`/`"standard"`の
各ブロックは「generate呼び出し→deviation checkコール」のペアであることをコード対照(`run_writer_stage()`L270-341)で確認した上で分離:

| ログ内訳(run_01、2回のパス=first-pass[superseded]+final[fact_fidelity_fix後]を含む) | input | output(reasoning) | cost(JPY、公式pricing snapshotで再計算) | elapsed(秒) |
|---|---|---|---|---|
| final advanced CHECK(attempt2、MAJOR判定) | 4544 | 2336(2070) | ¥0.5939 | 24.205 |
| final advanced CHECK retry(attempt4、compliant) | 4592 | 2608(2588) | ¥0.6477 | 25.88 |
| final standard CHECK(attempt2、compliant) | 4597 | 3217(3197) | ¥0.7648 | 32.905 |
| first-pass advanced CHECK(compliant) | 4568 | 3389(3369) | ¥0.7969 | 33.421 |
| first-pass standard CHECK(MAJOR判定) | 4542 | 5566(5178) | ¥1.2140 | 53.135 |
| first-pass standard CHECK retry(compliant) | 4555 | 5041(4660) | ¥1.1136 | 42.709 |

`cost.json`の`by_stage_jpy.advanced=4.985`/`standard=4.873`は、上記generate+check双方(first-pass+final、計6+6コール)の合計と
完全一致することを検算済み(advanced: 0.4324+0.7969+1.8575+0.5939+0.6569+0.6477=4.9853、standard:
1.1477+1.2140+0.3119+1.1136+0.3208+0.7648=4.8728)。pricing formula(下記1-4)が実際のcost.json生成ロジックと
一致していることの裏付けとして採用。

`er019_output/family_x_b3_production_wiring_01/run_01/audit/fact_fidelity_fix_01_recheck_summary.json`・
`fact_fidelity_fix_01_usage_log.jsonl`(修正後の単独deviation_recheckコール、generateを伴わない):

| stage | input | output(reasoning) | cost(JPY) | elapsed(秒) |
|---|---|---|---|---|
| deviation_recheck_b1b | 4592 | 919(899) | ¥0.323 | 9.55 |
| deviation_recheck_a2 | 4597 | 5715(5695) | ¥1.244 | 52.322 |

**差の理由**: input_tokensはほぼ同一(4592 vs 4597、article本文サイズがb1b/a2でほぼ同じため)。差はほぼ全てoutput側の
reasoning_tokens(899 vs 5695)に起因する。a2側の記事の方がLedgerとの照合で複雑な判断(比較・因果関係の疑い等)を要し、
モデルが多くのreasoning tokenを消費した結果であり、input側の規模(記事文字数・Ledger文字数)の違いによるものではない
(このばらつき自体が非決定的で、記事の内容次第で変動する)。

`er019_output/family_x_b3_diversity_trial_01/hormuz/run_01/raw_usage_log.jsonl`(小さいバッグ/ホルムズ Diversity Trial、
ホルムズはLedger外断定によりadvanced段で1回retryしてもMAJORが残りSTOPした実例):

| stage | input | output(reasoning) | cost(JPY) | elapsed(秒) |
|---|---|---|---|---|
| advanced CHECK(attempt2、MAJOR) | 4503 | 4499(4142) | ¥1.0079 | 39.885 |
| advanced CHECK retry(attempt4、なおMAJOR→STOP) | 4512 | 7303(6732) | ¥1.5466 | 68.375 |

### 1-3. 今回実測: JA本文(Original/R2)を直接article_textとして渡した場合

`er019_output/family_x_b3_production_wiring_01/run_01/research_ledger/verified_fact_ledger.txt`(Full Ledger、6,454文字、
日本語)を`verified_ledger_text`、同runの`ja_writer/original.md`(852文字)・`ja_writer/revision2.md`(974文字)を
`article_text`として、`run_deviation_check()`と全く同一のprompt/schema/model/developer messageをそのまま使い、
実際にAPIを2回呼び出した(証跡: `er019_output/ja_fact_double_check_cost_01/summary.json`・
`ja_original_deviation_check_full.json`・`ja_r2_deviation_check_full.json`)。

結果は§0の表の通り。JA Originalは実際にMAJOR(`changed_causality`)を1件検出した:

> `claim_in_article`: "AIが苦手な場面を人が助ける。"
> `explanation`: "一部通話を人間が担当した事実に、AIの弱点を人間が補うという未確認の因果的説明を加えています。"

これはこのrunのJA R2で既に修正済みの内容と一致しており(R2側は`LEDGER_COMPLIANT`)、Checkerが日本語article_textに
対しても意味的なdriftを正しく検出できることを実データで確認した(コードのみの推測ではない)。

**JA文字数とinput_tokensの関係(実測差分)**: Ledger文字数は両コールで同一(6,454文字)。article文字数がoriginal(852字)→
r2(974字)で+122字のとき、input_tokensは4724→4789で+65トークン。差分から日本語article_text 1文字あたり約0.53トークンと
直接推定できる(tiktoken等の外部推定ツールは未導入・不使用、実測差分のみによる推定)。JA記事850〜1,000字なら、
article_text自体の寄与は450〜530トークン程度であり、input_tokens全体(4,700〜4,800台)の大半はFull Ledger
(6,454文字)側が占める。英語版(b1b/a2、記事2,200バイト台)との入力サイズ規模を比較しても、input_tokensは概ね
4,500〜4,600台で同程度であり、JA本文を直接渡すこと自体がinput側コストを大きく増やす要因にはなっていない
(Ledgerサイズが支配的なため)。

### 1-4. Pricing根拠

`er005_output/cost_baseline_01/pricing_snapshot.json`: `gpt-5.6-luna` input ¥0.20/1M tokens、cached input ¥0.02/1M、
output ¥1.20/1M(`PROJECT_INTERNAL_RECORD`)。USD→JPYレートは`USD_JPY = 160.0`
(`er003_v1_n3_01_advanced_adaptation_generate.py`と同一定数)。
`cost_jpy = ((input-cached)/1e6*0.20 + cached/1e6*0.02 + output/1e6*1.20) * 160`。

## §2 Rewrite/Retry変動費(NG発生時のみ)

### JA must-fix Rewrite(既存`er019_family_x_ja_writer_o_r1_r2_01.py`、original→r1→r2)

3run分の実測(いずれも1回のみ、既存o→r1→r2の通常フロー、故意のmust-fix再生成ではない):

| run | ja_original | ja_r1 | ja_r2 |
|---|---|---|---|
| meta(production_wiring_01) | ¥0.2355 | ¥0.2425 | ¥0.2598 |
| small_bag | ¥0.2084 | ¥0.2180 | ¥0.2850 |
| hormuz | ¥0.1889 | ¥0.2205 | ¥0.2601 |

いずれも¥0.19〜¥0.29の範囲(委任文記載の「各¥0.2〜0.3程度」と一致)。latencyは9.2〜11.6秒/回(3run×3段=9サンプル、
最小9.218秒・最大11.575秒)。

### Advanced英訳Retry(既存`generate_advanced_adaptation`、deviation MAJOR時の1回だけの全文再生成)

| run/段 | GENコスト | GEN latency | 直後のCHECKコスト | CHECK latency |
|---|---|---|---|---|
| meta final advanced(1回目GEN) | ¥1.8575 | 91.310秒 | ¥0.5939(MAJOR) | 24.205秒 |
| meta final advanced retry(2回目GEN) | ¥0.6569 | 35.425秒 | ¥0.6477(compliant) | 25.88秒 |
| hormuz advanced(1回目GEN) | ¥0.6656 | 29.614秒 | ¥1.0079(MAJOR) | 39.885秒 |
| hormuz advanced retry(2回目GEN) | ¥0.8296 | 37.257秒 | ¥1.5466(なおMAJOR→STOP) | 68.375秒 |

Standard側(既存`generate_standard_a2`)も同型:

| run/段 | GENコスト | GEN latency | 直後のCHECKコスト | CHECK latency |
|---|---|---|---|---|
| meta first-pass standard(1回目GEN) | ¥1.1477 | 81.653秒 | ¥1.2140(MAJOR) | 53.135秒 |
| meta first-pass standard retry(2回目GEN) | ¥0.3119 | 30.406秒 | ¥1.1136(compliant) | 42.709秒 |

**must-fix受け渡し(新規追加分)の推定**: 現行実装には既存のmust-fix constraint機構は存在しない
(`NEWS-FAMILY-X-B3-ADVANCED-RETRY-ROOTCAUSE-01_REPORT.md` §10 案1参照。`run_writer_stage()`はMAJORの
`explanation`等を一切Writerへ渡さず、全く同一引数で`generate_advanced_adaptation()`/`generate_standard_a2()`を
再呼び出しするのみ)。同REPORTの見立てでは、追加した場合の増分は「プロンプトへの追加分のみ(数百トークン程度)」
であり、既存のretry回数(1回)自体は変えない前提。数百トークン(入力側)の追加は、luna input単価¥0.20/1Mから
換算すると¥0.01〜¥0.03程度の増分に相当する規模感(このmust-fix機構自体は未実装、実測ではなく上記REPORTからの
参照+単価換算)。

### NG発生率の参考値(母数は小さい、n=7の「1回目Checkerコール」のうちMAJORは3件)

| run/段(1回目コールのみ) | overall_status |
|---|---|
| meta first-pass advanced | LEDGER_COMPLIANT |
| meta first-pass standard | LEDGER_DEVIATION(MAJOR) |
| meta final advanced | LEDGER_DEVIATION(MAJOR) |
| meta final standard | LEDGER_COMPLIANT |
| small_bag advanced | LEDGER_COMPLIANT |
| small_bag standard | LEDGER_COMPLIANT |
| hormuz advanced | LEDGER_DEVIATION(MAJOR、retry後もMAJORでSTOP) |

3/7(約43%)。うち2/3は1回retryでLEDGER_COMPLIANTに解消、1/3(hormuz)はretry後もMAJORが残り
`run_writer_stage()`のSTOP条件(RuntimeError)が実際に発動した(standard段は未実行のまま)。
今回のJA直接測定(n=2、Original/R2それぞれ1回)ではOriginal側1/1がMAJOR、R2側1/1がCOMPLIANT。
いずれもサンプル数が極めて小さく、母比率の推定には使えない参考値。

## §3 最小コスト案(数字のみ、推奨・採否なし)

既存`run_deviation_check()`をコード変更なしでそのまま呼ぶ場合、呼び出し時に選べる引数は`model`
(デフォルト`MODEL`=`gpt-5.6-luna`、既存Routing Contract上の唯一の値)と`hook_aware`(True/False、
prompt/schemaへのHOOK_CLAUSE追加有無)の2つのみ。**reasoning effort(`"high"`)は関数内部のモジュール定数
`REASONING_EFFORT`にハードコードされており、呼び出し時の引数としては公開されていない**(下げる余地は
現行コードのシグネチャ上は存在しない。下げるには`run_deviation_check()`自体へのパラメータ追加という
コード変更が必要になる)。`hook_aware=True`はHOOK_CLAUSE(約300字程度の追加日本語文)をprompt/developer messageに
追加するのみで、コスト削減目的の設定ではない(判定基準を一部緩和するための機能であり、今回の対象呼び出し元
[production/DEV/Trial]は全てデフォルトの`hook_aware=False`を使用している)。

したがって「既存機構をそのまま再利用した場合の最小構成」は、§0/§1に示した実測値(1回あたり中央値¥0.9024、
実測例¥0.55〜¥1.65)がそのまま下限であり、これより追加でコードを変更せずに下げられる既存設定上の余地はない。

3パターンの固定費比較表(§0から再掲、数字のみ):

| パターン | 1記事(中央値) | 1記事(実測例) | 10記事(中央値) | 30記事(中央値) | 100記事(中央値) |
|---|---|---|---|---|---|
| Original後のみ | ¥0.90 | ¥1.65 | ¥9.02 | ¥27.07 | ¥90.24 |
| R2後のみ | ¥0.90 | ¥0.55 | ¥9.02 | ¥27.07 | ¥90.24 |
| ダブル | ¥1.80 | ¥2.20 | ¥18.05 | ¥54.14 | ¥180.48 |

## §4 実装上の注記

- **日本語article_text受付可否**: コード確認済み(`DEVIATION_DEVELOPER_MESSAGE`/`DEVIATION_PROMPT_TEMPLATE`は
  既に全文日本語、英語専用の記述なし)+実測確認済み(§1-3、JA本文2件を実際に渡し、2件ともJSON Schema通りの
  有効な応答が返り、うち1件は実際に意味的driftを正しく検出した)。**コード変更は不要**。
- **must-fix受け渡しの既存有無**: **なし**。`NEWS-FAMILY-X-B3-ADVANCED-RETRY-ROOTCAUSE-01_REPORT.md`で確認済みの
  通り、現行`run_writer_stage()`のretryは、1回目Checkerの`deviations`(claim_in_article/issue/explanation等)を
  一切Writer側へ渡さず、同一引数での「ゼロベース再生成」のみを行う。JA側Original/R2ダブルチェックを新規導入する
  場合も、現行コードのままではCheckerの指摘をJA Writerへ構造的に渡す経路は存在しない(§2の同REPORT案1〜3は
  いずれも未実装、Trial要否の仮見解付き)。
- 今回の実API呼び出し(JA Original/R2に対する2回)は`er019_output/ja_fact_double_check_cost_01/`
  (新規Trial用out-dir)にのみ保存し、Production側の`er019_output/family_x_b3_production_wiring_01/**`配下は
  一切変更していない(読み取りのみ)。

## §5 参照

- `er003_v1_en_direct_vfl_01_generate.py` L634-657(`run_deviation_check()`)、L454-541(prompt/schema/developer message)
- `er012_e_family_entertainment_two_level_runner_01.py` L259-373(`run_writer_stage()`)
- `er019_output/family_x_b3_production_wiring_01/run_01/raw_usage_log.jsonl`・`cost.json`・
  `audit/fact_fidelity_fix_01_recheck_summary.json`・`audit/fact_fidelity_fix_01_usage_log.jsonl`
- `er019_output/family_x_b3_diversity_trial_01/{small_bag,hormuz}/run_01/raw_usage_log.jsonl`
- `er005_output/cost_baseline_01/pricing_snapshot.json`(gpt-5.6-luna単価)
- `er003_v1_n3_01_advanced_adaptation_generate.py` L272-311(`USD_JPY`・cost計算ロジック、同一ロジックを本REPORTでも使用)
- `NEWS-FAMILY-X-B3-ADVANCED-RETRY-ROOTCAUSE-01_REPORT.md` §10(must-fix constraint未実装の確認元)
- 今回新規生成(このタスクの実測証跡、Trial用out-dir): `er019_output/ja_fact_double_check_cost_01/summary.json`・
  `ja_original_deviation_check_full.json`・`ja_r2_deviation_check_full.json`

## §6 Fable評価(2026-09-26)

コスト報告として受領。固定費: 既存Checker単発 中央値¥0.90(n=12、¥0.32〜¥1.65)、
latency中央値33秒。JA直接実測: Original後¥1.65/84.9秒、R2後¥0.55/25.2秒、ダブル
¥2.20/110秒。中央値換算1/10/30/100記事=¥1.80/¥18/¥54/¥180。変動費: JA Rewrite
1段¥0.19〜0.29、英訳retry(生成+Checker)¥0.31〜¥1.86。既存Checkerは日本語入力を
無変更で受け付ける(実測でOriginalのMAJOR[changed_causality]検出、R2はCOMPLIANT)。
重要な観察: この1サンプルでCheckerは既知の時制ドリフト(ロールバックされます)を
検出しなかった。JA段チェックは有効だがChecker判定の揺らぎ(ROOTCAUSE-01 §9-B)は
残る。Status: コスト報告完了・STOP(ユーザーのJAダブルチェック正式採用判断待ち、
Production変更なし)。

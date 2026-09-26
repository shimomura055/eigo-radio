# NEWS-FAMILY-X-B3-ADVANCED-RETRY-ROOTCAUSE-01

性質: 原因調査(read-only)。Production code/Prompt/SSOTは一切変更していない。API呼び出しは行っていない(¥0)。記事再生成も行っていない。

対象: `er019_output/family_x_b3_production_wiring_01/run_01/`(Meta「Muse人間コンシェルジュ」記事、b1b=Advanced/a2=Standard)。

## §0 要約(5行以内)

Advancedの1回目MAJOR原文は既存Production仕様上ディスクへ一切保存されず復元不能(推測ではなく`run_deviation_check()`の戻り値のうちparsedのみが保存される設計をコードで確認)。Retryは`run_writer_stage()`が`generate_advanced_adaptation(ja_text, ...)`を**全く同一の引数で再呼び出しするだけ**で、MAJORの指摘内容・Fact ID・違反種別はどのAPI呼び出しにも一切渡らない(previous_response_idも未使用、prompt自体が`ja_text`のみから決定論的に組み立てられる)。さらに時制ドリフトの発生源はAdvanced/Standardの英訳段階ではなく、それより上流の**JA Original生成段階**(Selected Brief「ロールバックした」→JA Original「ロールバックされます」)にあり、Advanced Retryは常にこの同一の(既に破損した)JA R2テキストを入力として使い続けるため、構造的に自己修復不可能だった。なお本調査開始時点で、本件の該当英文・JA文は本タスクとは別の"fact_fidelity_fix_01"という直接テキスト手動修正+recheckにより、既にディスク上で完了形へ修正済み(未commit)であることを確認した(§1(d)参照、本調査はこの修正を行っていない)。

## §1 1回目Checkerが返したMAJOR指摘の全文

**存在しない。** 復元不可能。根拠(推測ではなくコード読解):

- `er003_v1_en_direct_vfl_01_generate.py::run_deviation_check()`(L634-657)の戻り値は`{"prompt", "raw_text", "raw_parsed", "parsed", "model", "response_id", "hook_aware"}`。
- 呼び出し元`er012_e_family_entertainment_two_level_runner_01.py::run_writer_stage()`は、1回目の呼び出し結果(L275 `deviation = vfl01.run_deviation_check(...)`)を`dev_status`判定にのみ使い(L276)、MAJORなら即座に2回目の呼び出しで`deviation`変数を**上書き**する(L282)。1回目の`deviation`(prompt/raw_text/raw_parsedを含む)はどのファイルにも保存されないままガベージコレクトされる。
- `save_json(f"{b1b_dir}/audit/deviation_check.json", deviation["parsed"])`(L296)は**最終(2回目)**の`parsed`のみを保存する。1回目用の別ファイル書き込みは存在しない(STOPケース[L285-293]でのみ`rejected_advanced_attempt2.md`を保存するが、これは「retryも失敗した場合」のフォールバックで、本件[retry成功]には該当しない)。
- `raw_usage_log.jsonl`(`er019_output/.../run_01/raw_usage_log.jsonl` 全18行を確認)は`{"theme","stage","segment","timestamp","provider","api","model_id","response_id","attempt_number","success","elapsed_seconds","usage_source","web_search_call_count","input_tokens","cached_input_tokens","output_tokens","reasoning_tokens","total_tokens"}`のみで構成され、応答本文(response text/JSON)は一切含まない。1回目MAJOR判定の`response_id`は`resp_084fa73a11421b4b006ab76f1921d887d0b22920377c28daab`(L14、timestamp 2026-09-26T07:07:29Z、attempt_number=2、output_tokens=2336)だが、これはtokenメタデータのみで本文は含まれない。

代わりに残っているもの:
- `er019_output/.../run_01/audit/fable_editorial_findings.md`(L21-29、L502-507に相当する既存記録)が同じ結論(1回目原文は仕様上復元不能)を既に記録済み。本調査はコード読解によりこの結論を独立に再確認した(既存記録の丸写しではない)。
- Fableの委任文からのparaphrase引用(逐語ではないと明記): `docs/pm/ACTIVE_TASK_FXB3.md`「Fable指摘(Gate 3照合結果)」項番3「(b)既に実施済みのロールバックを将来形で表現」(`fable_editorial_findings.md` L31-36が出典明記の上で引用)。

## §2 1回目MAJORがRetry Promptへどう渡されたか

**渡っていない(ゼロ)。** Retry Prompt全文(system/developer/user)は以下:

`er003_v1_n3_01_advanced_adaptation_generate.py::build_prompt(ja_article_text)`(L261-270、逐語):

```
Adapt the Japanese article below into English.

Do not rewrite the article from scratch. Do not add new ideas, claims,
background, general observations, examples, or facts that are not in
the Japanese article. Preserve the Japanese article's editorial angle,
structure, and sense of surprise:
- the opening expectation the article sets up at the beginning;
- the reversal or turn partway through the story;
- the central metaphor or storytelling device the article uses;
- the order in which information and details are revealed;
- the ending and how it resolves or lands the story.
Keep every fact exactly as in the Japanese article. Use short, simple
English that a learner could understand by listening once.

Output only the English title and the English body.

Adaptation level: NATURAL ENGLISH.
Make the piece read like a natural English news feature. Keep the
central metaphor, the theme, the facts, the selection of information,
and the conclusion. You may reorder, merge, or reshape paragraphs, and
adjust the wording of metaphors where English needs it. Still add
nothing that is not in the Japanese article.

[Vocabulary difficulty rule ブロック(ADVANCED_VOCAB_RULE_V2_BLOCK、L144-187、既存語彙ルール、本タスクと無関係のため中略)]

Write in English.
Length: about 280–420 words in total.
Format (Markdown): start with "# " followed by the title; then the
main story; then exactly two "### " subsections, each 30–60
words, with headings that describe their content in your own words
(do not use labels like "Point One"); then a final section headed
exactly "## In one line" containing one sentence.

[Japanese article]
{ja_article_text}
```

developer message(L74-77、逐語): `"You are an editor who adapts finished Japanese feature articles into natural English for listeners who are learning English."`

API呼び出し(`er003_v1_en_direct_vfl_01_generate.py::run_writer_no_search()` L359-378):
```python
response = client.responses.create(
    model=model,
    reasoning={"effort": REASONING_EFFORT},
    input=[
        {"role": "developer", "content": developer},
        {"role": "user", "content": user_message},
    ],
)
```
`previous_response_id`パラメータは一切渡されていない(コード全体で本関数・`run_writer_with_technical_retry()`・`run_deviation_check()`のいずれにも`previous_response_id`という文字列は出現しない)。

**決定的な事実**: `run_writer_stage()`のRetry呼び出し(L280)は`adv_gen.generate_advanced_adaptation(ja_text, client=client)`であり、1回目の呼び出し(L272)`adv_gen.generate_advanced_adaptation(ja_text, client=client)`と**完全に同一の引数**。`deviation`変数(1回目MAJORの結果)はL282で`run_deviation_check`の**入力としても**使われていない(`run_deviation_check(client, ledger_text, advanced_text, hook_aware=False)`は毎回`ledger_text`+新しい`advanced_text`のみを受け取り、前回の判定結果は一切参照されない)。つまりMAJOR指摘は「単なる一般的なLedger遵守指示」にすら変換されず、**完全に破棄される**。

量的な裏付け(raw_usage_log.jsonl): Retry generate呼び出し(L15、`resp_02f11b18ddc1c555...`、timestamp 07:08:04、attempt_number=3)の`input_tokens=1502`のうち`cached_input_tokens=1499`(99.8%がキャッシュヒット)。これは1回目generate呼び出し(L13、`resp_0d51952213aa455c...`、attempt_number=1)の`input_tokens=1502`と**同一の入力サイズ**であり、prompt cachingの挙動と整合する(=プロンプト文字列が実質的に完全一致、新規追加分は3トークンのみ)。これはコード読解結果(build_promptがja_article_textのみに依存する決定論的関数)を独立に裏付ける定量的証拠。

## §3 Retry時Writerへ渡されたLedger / Selected Brief

- **Full Ledger(MUSE-HC-012、Checkerへ渡る側)**: `research_ledger/verified_fact_ledger.txt` L74「[VERIFIED] MUSE-HC-012: MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を**当面ロールバックした**と社内投稿で説明した。」(完了・過去形、曖昧さなし)。
- **Selected Brief(storyline_b3、JA Writerへ渡る側)**: `storyline_b3/selected_brief.md` L11「Metaの幹部は、適切な開示なしに契約スタッフが電話をかけるテストを始めたことを「ミス」と認め、人間コンシェルジュ機能を**当面ロールバックした**。」(こちらも完了・過去形、Full Ledgerと同じ時制)。
- **両者を並記**: Full LedgerもSelected Briefも「ロールバックした」で完全に一致しており、**曖昧表現はどちらにも存在しない**。「当面」はどちらにも共通して含まれるが、これは「(一時的に)ロールバックした」という完了した一時措置を表す副詞であり、Ledger/Brief単体では未来形を示唆しない。

**Advanced/Standardの直接入力について(訂正)**: Advanced/Standardの生成関数(`generate_advanced_adaptation`/`generate_standard_a2`)はLedgerやSelected Briefを直接受け取らない。Advancedの入力は`ja_text`(=JA R2完成本文、`ja_writer/revision2.md`)、Standardの入力は`advanced_text`(=生成済みAdvanced英文)である(`run_writer_stage()` L272, L320)。したがって時制の曖昧さがLedger/Briefに含まれていないにもかかわらず英文に紛れ込んだ経路を追う必要がある(§9Aで詳述)。

## §4 Retry前後の本文diff

**「1回目Advanced出力」の本文は存在しない**(§1参照、STOPしなかったため保存されず)。よって1回目↔2回目(retry)のunified diffは作成不可能。

代わりに提示できる事実:
- 現在ディスク上の`b1b/article.md`(=retry採用文、resp_02f11b18ddc1c555)の該当行(L27、修正前=fact_fidelity_fix_01適用前):
  `A Meta executive admitted that starting the test without clearly telling users was a mistake. The human concierge feature will be rolled back for now.`
- 上記は`audit/superseded_fact_fidelity_01/b1b_article_superseded.md`(fact_fidelity_fix_01適用前のバックアップ、2026-09-26 19:45作成)に保存されている、**本タスクの調査対象そのものの状態**。
- fable_editorial_findings.md(L11-13)がすでに「Advanced/Standardとも同一文言」と記録しており、これは1回目MAJORの原因になった文がretry後も(文言レベルで)ほぼ変化しなかったことを示す間接証拠(1回目原文が無いため完全一致の証明はできないが、否定する証拠も無い)。
- **なお、本調査の実施中(2026-09-26 19:45-19:47、本タスク開始[19:52頃]の直前)、別の"fact_fidelity_fix_01"という直接手動修正作業により、上記文は`has been rolled back for now`(完了形)へ書き換えられ、`gpt-5.6-luna`によるrecheckで両レベルとも`LEDGER_COMPLIANT`(`overall_status`、`deviations_found: null`)と再確認されている**(`audit/fact_fidelity_fix_01_recheck_summary.json`、`audit/fact_fidelity_fix_01_usage_log.jsonl`)。この修正はAdvanced Retry機構(本調査の対象)とは別の経路(手動テキスト編集+単発recheck呼び出し)であり、本調査はこれを実施していない。現在article.mdはこの修正後の状態(`has been rolled back for now`)である。

## §5 Retry Writerのraw response

`raw_usage_log.jsonl`該当行(L15、逐語):
```json
{"theme": "NEWS_FAMILY_X_B3_PRODUCTION_RUNNER_01", "stage": "advanced", "segment": null, "timestamp": "2026-09-26T07:08:04.611285+00:00", "provider": "openai", "api": "responses.create", "model_id": "gpt-5.6-luna", "response_id": "resp_02f11b18ddc1c555006ab76f3150a887d0a4bb1dc19cb5b20e", "attempt_number": 3, "success": true, "elapsed_seconds": 35.425, "usage_source": "OFFICIAL_API_RESPONSE", "web_search_call_count": 0, "input_tokens": 1502, "output_tokens": 3171, "total_tokens": 4673, "cached_input_tokens": 1499, "reasoning_tokens": 2697}
```
`model_id_actual`=`model_id_requested`=`gpt-5.6-luna`(`writer_run_summary.json`より`fallback_detected: false`)。`previous_response_id`フィールドは本ログスキーマに存在しない(コード上も未使用、§2参照)。`finish/incomplete reason`はこのログスキーマに存在しない(`success: true`のみ記録、OpenAI Responses APIの`status`/`incomplete_details`はcost loggerが記録対象としていない)。usage: input=1502(うちcached=1499)/output=3171(うちreasoning=2697)。

`attempt_number=3`である理由: このログの`attempt_number`はプロセス起動ごとの通し番号(er005_cost_logger、プロセス生存期間のみ有効なモジュールレベルカウンタ)であり、この呼び出しが「同一invocation内3回目のAPI呼び出し」であることを示す。実際のセマンティクスは「retry generate」の1回のみ(1回目generate→1回目deviation_check→2回目generate[retry]→2回目deviation_check、の3番目)。

## §6 Retry後CheckerのPrompt/Response

Retry後Checker呼び出し(`raw_usage_log.jsonl` L16): `response_id="resp_0d6c441b91c3b659006ab76f54c9c487d0a2638a49ab82fabb"`, timestamp 07:08:30, attempt_number=4, input_tokens=4592(cached=0), output_tokens=2608, reasoning_tokens=2588。

保存済みの最終parsed結果(`b1b/audit/deviation_check.json`、逐語):
```json
{
  "deviations": [],
  "overall_status": "LEDGER_COMPLIANT"
}
```
これが「reasoning/structured output全文」の全て。`DEVIATION_JSON_SCHEMA`(`er003_v1_en_direct_vfl_01_generate.py` L454-493)は`deviations`配列のみを要求するスキーマで、配列が空の場合はfree-text reasoningフィールド自体が存在しない(1件ごとの`issue`/`explanation`は`deviations`要素にのみ存在するため、0件ヒットのときは説明文自体が生成されない設計)。1回目Checker呼び出しの`raw_text`/`raw_parsed`は§1の通り復元不能。

**1回目と2回目のChecker条件対比**:

| 項目 | 1回目(MAJOR) | 2回目(retry後、LEDGER_COMPLIANT) |
|---|---|---|
| 呼び出しコード | `vfl01.run_deviation_check(client, ledger_text, advanced_text, hook_aware=False)`(L282、1回目はL275) | 同一コード行(L282) |
| developer message | `DEVIATION_DEVELOPER_MESSAGE`(hook_aware=False固定) | 同一 |
| prompt template | `DEVIATION_PROMPT_TEMPLATE`(L502-541) | 同一 |
| JSON schema | `DEVIATION_JSON_SCHEMA`(L454-493、strict=True) | 同一 |
| model | `gpt-5.6-luna`(`MODEL`定数、明示指定なし) | 同一 |
| reasoning effort | `"high"`(`REASONING_EFFORT`定数) | 同一 |
| temperature | 指定なし(コード上どこにも`temperature`引数は存在しない。GPT-5系reasoningモデルのResponses API呼び出しにtemperatureパラメータ自体が渡されていない) | 同一 |
| 入力Ledger(`verified_ledger_text`) | 同一の`ledger_text`(runner起動時に一度読み込まれ、両呼び出しで使い回し) | 同一 |
| 入力article_text | 1回目generateの出力(復元不能) | retry generateの出力(現存) |
| hook_aware | False(呼び出し元L275/L282とも明示的にFalse) | 同一 |

**結論**: Checker側の設定(prompt/model/schema/reasoning effort/入力Ledger/hook_aware)は1回目・2回目で完全に同一。差分は「検証対象のarticle_text」(モデルの非決定的出力)のみ。

## §7 現行Retry仕様の正確な挙動(コード根拠)

`er012_e_family_entertainment_two_level_runner_01.py::run_writer_stage()`(L259-373):
- Advanced: L270-314。generate(L272)→deviation_check(L275)→MAJORならgenerate再呼び出し(L280、**引数は1回目と完全同一**)→deviation_check再呼び出し(L282)→まだMAJORなら`rejected_advanced_attempt2.md`保存の上でRuntimeError STOP(L285-293)。**最大1回のretry**(コードコメントL16-18「MAJORの場合は1回だけ再生成しても解消しない場合はSTOP」と一致)。
- Standard: L316-360。同一パターン(generate L320→check L323→MAJORならgenerate再呼び出しL328[引数は`advanced_text`のみ、1回目と同一]→check L330→まだMAJORならSTOP L333-338)。

**全文再生成か問題箇所修正か**: 全文再生成(`generate_advanced_adaptation`/`generate_standard_a2`は常に記事全体を新規生成する関数であり、部分修正パッチAPIは存在しない)。

**前回出力の引き継ぎ**: 引き継がない。retry呼び出しの引数はAdvancedなら`ja_text`(JA R2本文、不変)、Standardなら`advanced_text`(直前に確定したAdvanced本文、不変)のみで、前回の**English**生成結果自体は引数にもプロンプトにも含まれない。

**previous_response_idでの継承**: していない(§2で確認済み、コード全体に`previous_response_id`の使用箇所なし)。

**「前回のMAJORを必ず解消せよ」という契約**: 存在しない。retry呼び出し(L280/L328)にMAJOR内容を渡すコードパスが無いため、契約自体が実装されていない。

`er019_family_x_entertainment_production_runner_01.py`のadvanced/standardステージ呼び出し確認: 本ファイルは`run_writer_stage(client, theme, ja_text, ledger_text, budget_jpy, only=...)`をそのまま呼び出す薄いラッパーであり(`--stage writer`/`--regenerate-stage advanced|standard`経由)、retryロジック自体は上記`er012_e_family_entertainment_two_level_runner_01.py`に完全に委譲されている。`er019_family_x_entertainment_production_runner_01.py`内にMAJORフィードバックを扱う独自コードは存在しない。

## §8 MAJOR指摘をRetry成功条件として保持しているか

**保持していない。** 根拠:
- `DEVIATION_JSON_SCHEMA`(L454-493)に`issue_id`/`fact_id`に相当するフィールドは存在しない(`claim_in_article`/`issue`/`severity`/10種フラグ/`explanation`のみ)。仮に1回目の結果を保存していたとしても、2回目の結果と機械的に同一issueかどうか突き合わせるための一意キーがスキーマ上そもそも無い。
- `run_writer_stage()`のretry判定条件(L283-285)は`dev_status == "LEDGER_DEVIATION"`という**overall_statusの再判定のみ**であり、「1回目に指摘された特定のdeviationが2回目にも残っているか」を個別に追跡するコードは存在しない。2回目呼び出しはゼロベースの再判定(`run_deviation_check`は毎回新規のarticle_textに対して独立採点するのみで、過去の判定結果を入力に含まない、§6参照)。
- 成功条件は事実上「2回目の`overall_status`が`LEDGER_COMPLIANT`であること」だけであり、「新しい文章を生成したこと」自体が成功条件ではないが、「MAJORが実際に解消されたこと」を検証する仕組みも無い(Checkerの判定を鵜呑みにするのみ)。

## §9 原因分析

### A. Rewrite/Retry側: なぜ修正されなかったか

各候補についてEvidenceで支持/否定/判定不能を明記する。

1. **Checker feedbackがRetry Promptへ具体的に渡っていない** → **支持(確定)**。§2・§7のコード読解で完全に裏付け。MAJORのFact ID/問題箇所/violation typeはretry呼び出しのどの引数にも一切含まれない。
2. **MAJOR指摘が一般化・欠落している** → **支持だが「一般化」ですらない、完全な欠落**。フィードバックが薄められて渡っているのではなく、そもそも渡り口(パラメータ)自体が存在しない。
3. **前回本文の慣性(model尤度バイアス)** → **判定不能(部分的仮説)**。1回目原文が無いため「同じ本文に引きずられた」ことを直接証明できないが、§2の量的証拠(retry呼び出しのinput_tokensが1回目と完全一致、cached_input_tokens=1499)は「promptが1回目と同一であること」を示すのみで、モデルの出力自体が慣性で似るかは別問題(責任企業契約のプロンプトが同じである以上、モデルが似た表現を再生成する可能性は高いが、これはPromptが同一であることの帰結であり独立した原因ではない)。
4. **previous_response_idによる前Attempt維持** → **否定(確定)**。使われていない(§2・§7)。
5. **全文再生成だがmust-fix constraintなし** → **支持(確定)**。§7で確認。
6. **Ledgerより英語文脈(JA R2の文言)優先** → **支持(確定、これが最も根本的)**。Advancedのprompt(§2)は明示的に「Keep every fact exactly as in the Japanese article」「Preserve the Japanese article's editorial angle」と指示しており、これはWriterに対して「Ledgerと照合せよ」ではなく「日本語記事に忠実であれ」と命じている。§3で確認した通り、実際にはFull Ledger/Selected Briefのどちらも過去形「ロールバックした」だが、**JA Original生成段階(§3後段、L`ja_writer/original.md` L15)ですでに「ロールバックされます」(未来形)へドリフトしており**、JA R1(`ja_writer/revision1.md` L19)・JA R2(修正前、`audit/superseded_fact_fidelity_01/revision2_superseded.md` L25)ともにこの未来形が引き継がれたまま確定稿になっていた(fact_fidelity_fix_01適用前)。Advanced/Standardの英訳は指示通り「日本語記事に忠実」に振る舞った結果、この上流のドリフトをそのまま英訳しただけであり、Advanced自身が新たな誤りを作り出したのではない。**Retryは`ja_text`(=このドリフトを含んだまま不変のJA R2)を再度渡すだけなので、何回retryしても同じ上流の誤りを再翻訳するだけで、原理的に自己修復できない**(Advanced/Standardの生成関数にはLedgerそのものを参照する手段が無く、参照先はJA R2本文のみ)。
7. **retry成功条件が「新しい文章を生成したこと」であり「MAJOR解消」ではない** → **部分的に支持**。§8で確認した通り、成功条件は「2回目Checkerが`LEDGER_COMPLIANT`と判定すること」であり、これは「新しい文章の生成」よりは強い条件だが、「(1回目に具体的に指摘された)MAJORが実際に解消されたことの検証」ではない(Checkerの2回目判定を無条件に信頼する設計)。
8. **その他実装欠陥**: `run_deviation_check()`はLedger全文とarticle全文を都度スキャンする「独立採点」方式であり、時制ドリフトの発生源(JA Original生成段階)を全く検査対象にしていない(Advanced/Standardの英文とLedgerだけを比較し、JA原稿とLedgerの整合性を検査するdeviation checkは、確認した範囲のコードには存在しない)。これは実装欠陥というより設計スコープの限界(検査対象がAdvanced/Standardの最終英文のみ)。

### B. Checker側: なぜ同じ差を2回目に`LEDGER_COMPLIANT`としたか

1. **Prompt差** → **否定(確定)**。§6の対比表の通り完全同一。
2. **input差(article_text以外)** → **否定(確定)**。Ledger/developer/schemaとも同一。article_textのみが異なる(モデルの非決定的出力の差)。
3. **Ledger差** → **否定(確定)**。同一の`ledger_text`変数を使い回し。
4. **context差** → **否定に近い**。会話継続(previous_response_id)は無く、両呼び出しとも独立したゼロコンテキスト呼び出し。
5. **structured outputの扱い** → **判定不能な部分あり**。`DEVIATION_FLAG_KEYS`の`changed_time`の定義文(L520）は「時期・年代をLedgerと異なるものに変えている」であり、暦年・時期のズレを主眼にした説明で、「単一の出来事が完了済みか未来かという動詞の時制」を明示的に扱う文言ではない。`changed_certainty`(L515「仮説・自己申告・専門家の解釈にすぎないものを断定的な事実であるかのように強めている」)も方向が逆(未来形は「まだ起きていない」という意味で確信度を弱める方向であり、本ケースの誤りパターンとは方向が一致しない)。このため「will be rolled back」対「has been rolled back」の違いをどの1種のフラグに対応づけるべきかがプロンプト上明確でなく、LLM判定者ごとに(あるいは同一設定内の再試行ごとに)解釈が割れる余地がある。これは1回目がMAJOR・2回目がCOMPLIANTになったことの**もっともらしい一因(仮説)**だが、1回目の生JSON(該当箇所・フラグ)が復元できないため、実際に1回目がどのフラグで判定したかは確認できず、**断定はできない**。
6. **threshold・severity定義** → 上記5と同じ(スキーマ/プロンプトの構造的曖昧さ)。
7. **retry後のChecker routing** → **否定(確定)**。ルーティングの分岐は無く、常に同一関数・同一パスを通る。
8. **model_id差** → **否定(確定)**。両方`gpt-5.6-luna`。
9. **temperature・reasoning差** → **否定(確定)**。両方`reasoning={"effort": "high"}`、temperatureは両方とも未指定。
10. **同一issue追跡の不在** → **支持(確定)**。§8の通り、issue_id等の追跡キー自体がスキーマに存在せず、2回目呼び出しは1回目の判定内容を一切参照しない「ゼロベース再判定」である。これ自体が2回目が異なる結論を出せる(=1回目の判定を無視できる)構造的余地を作っている。

**総合**: BについてはPrompt/Model/Schema/入力Ledger等の構成要因はすべて同一であり、唯一の相違はarticle_text(モデルの非決定的出力)と、Checker自身のサンプリングの非決定性である。加えて、`changed_time`/`changed_certainty`のいずれのフラグ定義も「単一事象の完了/未来の時制」を名指しで扱っておらず、この種の違反がどのフラグに該当するかがモデルにとって曖昧である可能性が、判定のブレを助長した一因として考えられる(仮説、断定不可)。

## §10 対策案(実装しない、最小限の設計メモ)

### 案1: Retry時のmust-fix constraint

- 変更箇所: `er012_e_family_entertainment_two_level_runner_01.py::run_writer_stage()` L279-282付近(Advanced)、L327-330付近(Standard)。`deviation["parsed"]["deviations"]`(MAJORのみ抽出)を文字列化し、`generate_advanced_adaptation()`/`generate_standard_a2()`に新規オプション引数(例: `must_fix: list[dict] | None = None`)として渡し、`build_prompt()`側で「以下の指摘を必ず解消すること」ブロックを追加する。
- 想定diff規模: `er003_v1_n3_01_advanced_adaptation_generate.py`/`er003_v1_n3_01_standard_a2_generate.py`(build_prompt関数へのオプション引数追加、中規模)、`er012_e_family_entertainment_two_level_runner_01.py`(retry呼び出し箇所2箇所、小規模)。
- false positive/negativeリスク: MAJORの`explanation`文言がそのままモデルへの追加指示になるため、Checkerの誤検知(false positive MAJOR)がそのままWriterへの誤った修正指示になり、正しい記述を不必要に書き換えてしまうリスクがある(Checker自体の精度に依存する設計になる)。
- cost/latency増分: プロンプトへの追加分のみ(数百トークン程度)、retry回数は変えないため大きな増分ではない。
- 既存Deviation Checkerとの整合: 既存の「1回だけ再生成」上限は維持可能。DEVIATION_JSON_SCHEMAの出力(claim_in_article/issue/explanation)をそのまま転記すればよく、スキーマ変更は不要。
- retry/fallbackへの影響: 既存のSTOP条件(2回目もMAJOR)はそのまま維持できる。
- Trial要否(仮見解): 記事の英語表現の質・意図しない過剰修正が起きないかを確認する必要があり、Trialでの事前検証が望ましい(Production直接変更はWriterの出力品質に影響するため)。

### 案2: Retry後のissue persistence

- 変更箇所: `run_deviation_check()`の呼び出し元(`run_writer_stage()`)で、1回目の`deviation["parsed"]["deviations"]`(MAJORのみ)を保持し、2回目のCheckerが「解消したか」を明示的に問う専用チェック(例: 各MAJOR項目について「この指摘は解消されたか」をYES/NOで再確認する軽量な追加LLM呼び出し、またはdeterministicな文字列パターンチェック)を追加する。同一issueが残っていれば、Checkerの2回目`overall_status`がCOMPLIANTでも強制的にFAIL継続とする。
- 想定diff規模: `run_writer_stage()`に新規ロジック追加(中規模)、必要なら`er003_v1_en_direct_vfl_01_generate.py`に新規関数追加。
- false positive/negativeリスク: 「解消したか」の再確認自体もLLM判定であれば同じ非決定性の問題を抱える(堂々巡りになりうる)。deterministicパターンチェック(案3)と併用しないと効果が薄い可能性。
- cost/latency増分: 追加のLLM呼び出し1回分(Advanced/Standardそれぞれ)。
- 既存Deviation Checkerとの整合: 既存Checkerの判定を上書き・追加条件にする形になるため、既存の「Checkerが最終判断者」という設計思想を一部変更することになる(ユーザー判断が必要)。
- Trial要否(仮見解): 判定ロジックの二重化であり、Trialでの誤動作確認が必要。

### 案3: deterministic補助チェック(past/completed vs future、number、named fact)

- 変更箇所: 新規モジュール(例: `er0XX_deterministic_fact_guard_01.py`)を追加し、Ledgerの各Factに`date_or_period`/`notes_for_writer`等の既存メタデータ(`verified_fact_ledger.txt`のフォーマット参照)から「完了済み」であることが明示されているFactについて、対応する英文が未来形助動詞(`will be`, `is going to be`等)で書かれていないかを正規表現等でチェックする。
- 想定diff規模: 新規ファイル1つ(中規模)、`run_writer_stage()`への呼び出し追加(小規模)。
- false positive/negativeリスク: **Validator肥大化・false positiveの懸念が大きい**。英語の時制は文脈依存性が高く(例: 引用文中の未来形、仮定法、他のFactに関する未来形など)、単純な正規表現ベースの検知は誤検知しやすい。既存のLedger Deviation Checker(LLM判定)がすでに"lexical/scope的な厳密一致を暗黙に重視"していたv1判定を誤検知として撤回した経緯(コードコメント`er003_v1_en_direct_vfl_01_generate.py` L437-447、ER-009-N1-LEDGER-DEVIATION-RECALIBRATION-02)があり、同種の誤検知リスクを再導入する可能性がある。
- cost/latency増分: API呼び出し無し(ローカル処理)、無視できるレベル。
- 既存Deviation Checkerとの整合: 既存のLLM判定に対する**追加の安全网**として動作させることは可能(LLM判定がCOMPLIANTでも、deterministicチェックがFAILならSTOPする、というAND条件)。
- Trial要否(仮見解): false positive率を事前に測定するTrialが必須(既存のER-009-N1経緯を踏まえると、拙速なProduction直接導入は同種の問題を繰り返すリスクが高い)。

## §11 Trial要否とProduction直接修正可否の仮見解

- 案1(must-fix constraint)は、既存retryロジックへの局所的な追加であり比較的リスクは低いが、Writerへの追加指示がWriterの表現の質・過剰修正リスクに直結するため、**Trialでの事前検証を推奨**(Production直接修正は非推奨、あくまで仮見解)。
- 案2(issue persistence)は、既存Checkerの「最終判断者」という設計思想を変更する可能性があり、**Trial必須**。
- 案3(deterministic補助チェック)は、ER-009-N1の既知の誤検知経緯を踏まえると**Trial必須**(false positive率の事前測定なしでのProduction導入は非推奨)。
- いずれの案も、本調査の範囲(read-only)では実装していない。ユーザー判断待ち。

## §12 参照ファイル一覧

- `er019_output/family_x_b3_production_wiring_01/run_01/audit/fable_editorial_findings.md`
- `er019_output/family_x_b3_production_wiring_01/run_01/writer_run_summary.json`
- `er019_output/family_x_b3_production_wiring_01/run_01/raw_usage_log.jsonl`(全18行)
- `er019_output/family_x_b3_production_wiring_01/run_01/b1b/article.md`, `b1b/audit/deviation_check.json`, `b1b/audit/final_advanced_summary_manual_reconstructed_superseded.json`
- `er019_output/family_x_b3_production_wiring_01/run_01/a2/article.md`, `a2/audit/deviation_check.json`
- `er019_output/family_x_b3_production_wiring_01/run_01/audit/superseded_fact_fidelity_01/`(b1b_article_superseded.md, a2_article_superseded.md, revision2_superseded.md 等)
- `er019_output/family_x_b3_production_wiring_01/run_01/audit/fact_fidelity_fix_01_recheck_summary.json`, `fact_fidelity_fix_01_usage_log.jsonl`
- `er019_output/family_x_b3_production_wiring_01/run_01/research_ledger/verified_fact_ledger.txt`
- `er019_output/family_x_b3_production_wiring_01/run_01/storyline_b3/selected_brief.md`
- `er019_output/family_x_b3_production_wiring_01/run_01/ja_writer/original.md`, `revision1.md`, `revision2.md`
- `er012_e_family_entertainment_two_level_runner_01.py`(L259-373 `run_writer_stage()`)
- `er003_v1_n3_01_advanced_adaptation_generate.py`(L261-270 `build_prompt()`, L337-380 `generate_advanced_adaptation()`)
- `er003_v1_en_direct_vfl_01_generate.py`(L359-400 `run_writer_no_search()`, L403-431 `run_writer_with_technical_retry()`, L448-493 `DEVIATION_FLAG_KEYS`/`DEVIATION_JSON_SCHEMA`, L495-541 プロンプト定数, L634-657 `run_deviation_check()`)
- `docs/pm/ACTIVE_TASK_FXB3.md`(Fable委任文からのparaphrase引用、出典は`fable_editorial_findings.md`経由)

---

## §13 Fableレビュー(2026-09-26)

「(1) 原因分析の妥当性: 支持。根本原因は2点。①Retryが1回目MAJORの
内容を一切受け取らず同一入力(JA R2)で英訳を再生成するだけで、
must-fix契約もissue追跡も存在しない。②逸脱の発生源がJA Original段
(Selected Brief/Full Ledgerは正しい)であり、JA Writer段にLedger照合
Gateが無いため、英訳段のretryでは原理的に自己修復不能。hormuz
(Diversity Trial)のMAJOR 3件もJA R2時点で存在しており、2件/2件が
同じ構造で説明できる。
(2) 訂正: 「1回目Checkerが時制差をMAJORとして正しく検出した」という
前提は、1回目Checkerの生JSONが保存されない設計のため未検証(Fableの
前回報告の記述は実行時ログのparaphraseだった)。
(3) Checker側: 1回目/2回目の設定は完全同一で、差はarticle_textと
判定の非決定性のみ。`changed_time`/`changed_certainty`の定義が
「単一事象の完了/未来」を名指ししていない曖昧さは妥当な仮説。
(4) 最小対策の推奨: [a] 観測性修正(全deviation check結果[attempt
1/2、raw JSON含む]を保存)=挙動変更なし、Production直接修正可、¥0。
[b] 挙動修正=Trial必須: (i) JA Writer段(R2確定前)にSelected Brief/
Full Ledger照合とmust-fix retryを追加(発生源で止める)、(ii) 英訳段
retryにmust-fix constraint+issue persistence(1回目MAJORの各項目が
解消したかを2回目で個別再確認、残存なら自動FAIL継続)。[c]
deterministic時制チェック(案3)は現時点で不採用(ER-009-N1の誤検知
経緯、false positiveリスク)。Trial対象はMeta run_01(JA段から再生成)
とhormuz(STOP済み事例)、想定¥20〜40。
(5) リスク: [b-i]はJA段の追加LLM呼び出し1〜2回/記事(+¥0.5〜1、
+20〜40秒)。[b-ii]はChecker誤検知がそのまま修正指示になるfalse
positive連鎖の懸念があり、must-fix指示は「Ledger原文を提示して
整合させる」形に限定する。retry上限1回・STOP条件は維持。
(6) Production直接修正の可否: [a]のみ可。[b]はTrial後にユーザー
承認。」

# FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01_REPORT.md

管理ID: FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01(Phase B、委任_02)
Status: `APPROVED_FOR_PRODUCTION`(配線完了・Fable Gate 3判定待ち)。
`PRODUCTION_WIRED`はSonnetが書かない。

Phase A設計書: `docs/pm/design_family_x_concreteness_an3_t0_production_wiring_01.md`
(§8にPhase B実施記録を追記済み)。

## Checklist 15項目(ユーザー指定)

### 1. 初回Writer経路へAN3実装

`er019_family_x_ja_writer_o_r1_r2_01.py`へ4箇所の最小diff(合計37行、
34 insertions/3 deletions)。

- `CONCRETENESS_CONTROL_AN3_BLOCK`(A3+N2逐語、L98-106付近)を新設。
- `build_original_prompt()`: `prompt += SYMBOL_PREVENTION_BLOCK_JA`の直後
  へ`prompt += CONCRETENESS_CONTROL_AN3_BLOCK`を1行追加。
- `CONCRETENESS_CONTROL_AN3_REMINDER_JA`を新設し、`verbatim_shas()`へ
  2キー追加。

### 2. R1/R2整合(3箇所)

`CONCRETENESS_CONTROL_AN3_REMINDER_JA`を、関数化されていない既存3箇所
(通常r1/r2ループ・R2 Fact Check must-fix・R2音声記号must-fix)全てへ
個別追加した(証拠:
`grep -c CONCRETENESS_CONTROL_AN3_REMINDER_JA er019_family_x_ja_writer_o_r1_r2_01.py`
= 5件[定義1+verbatim_shas内1+使用箇所3]、新規test
`test_normal_r1_r2_loop_references_reminder`/
`test_r2_must_fix_instruction_references_reminder`/
`test_r2_symbol_instruction_references_reminder`で個別assert)。

### 3. retry・fallback・regenerationの維持

新規実装は既存パターン([既存コード]+[AN3ブロック])のappendのみで、
retry回数・STOP条件・Gateロジックは一切変更していない。確認用再生成
実行で、Hormuz Original(1発PASS)・R2(既存1回must-fix retryでMAJOR
解消)、Meta Original(既存1回must-fix retryでMAJOR解消)・R2(1発PASS)、
Hormuz Advanced(既存1回must-fix retryでMAJOR解消)、Meta Advanced
(1発PASS)と、既存のretry機構が複数パターンで正しく作動することを実測
確認した(§4参照)。previous_response_id失敗時のfallback_full_text経路
は本確認用再生成では発火しなかった(chain_method=`previous_response_id`
を両記事とも確認)が、コード上REMINDERは同一instruction文字列に含まれる
ため、fallback発火時も内容は変わらない。

### 4. Trial scriptだけに残さない(Production module本体へ実装)

`er019_family_x_ja_writer_o_r1_r2_01.py`(Production module)へ直接実装。
`er037`/`er039`(Trial script)は無変更(`git diff --stat`で確認済み、
下記§9)。

### 5. T1混入なし

新規test`test_ja_writer_source_has_no_t1_phrases`/
`test_advanced_adaptation_source_has_no_t1_phrases`で、
`er019_family_x_ja_writer_o_r1_r2_01.py`と
`er003_v1_n3_01_advanced_adaptation_generate.py`のソースにT1文言
(`"Trial-only additional instruction"`、`"not already in the Japanese
article"`)が含まれないことを機械的に確認(PASS)。

### 6. 現行英語化Prompt無変更

`er003_v1_n3_01_advanced_adaptation_generate.py`は本タスクで一切編集
していない(`git diff --stat`にファイル名が出現しないことで確認)。
新規test`test_advanced_vocab_rule_v2_block_sha256_unchanged`で
`ADVANCED_VOCAB_RULE_V2_BLOCK`のsha256が既存の固定値
`ADVANCED_VOCAB_RULE_V2_SHA256`(`d536f4b8...`)と一致することを確認
(同ファイル内の既存import時assertと同じ基準を利用)。

### 7. 共有Prompt非影響

Grep調査(設計書§1b)により、`R0_PROMPT`/`REVISION_INSTRUCTIONS`は
Family X専用でありFamily A/B/Y/Zとは共有されていない。今回変更した
ファイルは`er019_family_x_ja_writer_o_r1_r2_01.py`のみ(他Family Writer
モジュールへのimport・参照はゼロ)。

### 8. runtime発火確認(実API)

専用out-dir
`er019_output/family_x_entertainment_production_runner_01/an3_t0_wiring_regression_01/{hormuz,meta}/`
にて、既存Production run(Hormuz:
`er019_output/family_x_b3_diversity_trial_01/hormuz/run_02`、Meta:
`er019_output/family_x_b3_production_wiring_01/run_01`)からresearch_
ledger/storyline_b3を複製し(既存run非上書き)、正式path
`er019_family_x_entertainment_production_runner_01.py`を`--stage writer
--stop-after writer`→`--stage advanced --stop-after advanced`の順で
実行(TTS/ASR呼び出しはコード上不存在、下記§10で確認根拠を記載)。

両記事の`ja_writer/runtime_evidence.json`に以下が記録され、
`jaw.verbatim_shas()`の値と一致:

```
"concreteness_an3_block_sha256": "067030ff53ecb76a4d1477a3deace07b3e1fac438a33cb873edbe045cf6927fe",
"concreteness_an3_reminder_sha256": "0b5c99af5b15bab445954387cf5c9f1e3ef3972792c9f9ff1e9d8c22b19a8597"
```

### 9. Essential Fact・因果Regression(既存Ledger Deviation Check)

| 記事 | 段 | 1回目 | 2回目(must-fix後) |
|---|---|---|---|
| Hormuz | Original | LEDGER_COMPLIANT | - |
| Hormuz | R2 | LEDGER_DEVIATION(MAJOR 2件) | LEDGER_COMPLIANT |
| Hormuz | Advanced | (1回目実行はparts.json手前でクラッシュ、§14参照) | LEDGER_DEVIATION(MAJOR 1件)→再generate→LEDGER_COMPLIANT |
| Meta | Original | LEDGER_DEVIATION(MAJOR 1件) | LEDGER_COMPLIANT |
| Meta | R2 | LEDGER_COMPLIANT | - |
| Meta | Advanced | LEDGER_COMPLIANT | - |

2記事とも最終的にEssential Fact・因果関係のMAJOR Deviation 0件
(`LEDGER_COMPLIANT`)に到達した。既存の1回must-fix retry→STOP機構が
複数箇所で正しく作動しており、独自の追加retryは行っていない。

### 10. CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS反映

- `CURRENT_SPEC.md`: 新設「## Family X Writer — Concreteness Control
  (AN3-T0)」節(「## 通常News」節の末尾、L885直前)。
- `DECISION_LOG.md`: 末尾新規エントリ
  「## FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01」。
- `OPEN_ITEMS.md`: OPEN-224→`CLOSED`(T1不採用確定)。OPEN-220→
  `DEFERRED`+所在ファイル誤記訂正(`articles_generate.py`ではなく
  `advanced_adaptation_generate.py`が正)。新規OPEN-227(R2 must-fix経路
  のSYMBOL_PREVENTION_BLOCK_JA非対称性、変更せず記録のみ)・新規
  OPEN-228(Hormuz Advanced生成でのMain Story段落数チェック失敗、§14)。
- `docs/pm/REPORT_LEDGER.md`: Trial-02行のStatusを更新
  (AN3-T0のみ`APPROVED_FOR_PRODUCTION`)、Wiring-01新規行追加。
- 差分所有者確認(開始時・commit直前の2回):
  `git status --porcelain CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md
  docs/pm/REPORT_LEDGER.md docs/pm/PM_GOVERNANCE.md`
  → 開始時: 出力なし(クリーン)。commit直前: `CURRENT_SPEC.md`/
  `DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`の4件の
  みが`M`(本タスク由来のみ、他Agent差分ゼロ、`PM_GOVERNANCE.md`は
  無変更)。

### 11. Trial-02 status反映

`FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02_REPORT.md`末尾へ「## 14.
訂正注記」を追加し、「JA数字はAN3が両記事で0」がArabic数字専用カウンタ
の表現であり漢数字は未計測だった旨を訂正した。`DECISION_LOG.md`同エントリ
内にも同旨を記載。`docs/pm/REPORT_LEDGER.md`のTrial-02行のStatus欄も
更新した(§10参照)。

### 12. commit・push

下記§16参照(commit hash・push結果)。

### 13. approved内容と実挙動一致

ユーザー承認事項(AN3-T0=A3+N2+現行英語化Prompt、「数字を0にする」とは
定義しない、数値カウンタを成功条件にしない)と実装・実測結果は一致
している。Advanced Prompt(T0)は無変更のまま使用し、実際に生成された
Hormuz/Meta英語記事は§4に全文転記した通り自然な記述であり、必要な
Fact(数量・固有名詞含む)は保持されている(Deviation Check
`LEDGER_COMPLIANT`)。

### 14. 数字カウンタ誤認の是正

`FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02_REPORT.md`§14、
`DECISION_LOG.md`本エントリへ訂正注記を記載(§11参照)。

### 15. STOP有無

STOPなし(暴走疑いの3項目[大量API発火/意味のないretry loop/原因不明の
費用増加]はいずれも発生していない)。ただしHormuz Advanced生成での
構造チェック失敗(§14に既述、TTS準備artifactのみに影響)について、
governance上の「同じ失敗の無意味なretry loop」STOP基準に抵触しない
範囲(1回のみの正当な`--regenerate-stage`相当の再実行)で対応し、
2回目失敗後はこれ以上の追加retryを行わず、新規OPEN-228として報告する
判断とした(詳細§14)。

---

## 記事本文全文(JA最終R2 + Advanced English最終)

### Hormuz — JA(R2、最終)

```
二割の料金案は撤回。それでも原油価格はすぐ戻った

原油価格のニュースには、ときどき政策発表よりも、発表後の値動きが大きなオチを持ってくる。今回のオチは、料金案が舞台から退場したのに、価格が一緒には退場しなかったことだ。

七月十三日、トランプ氏は、アメリカがホルムズ海峡の安全確保に使う費用について、海峡を通るすべての貨物に二割の償還を求めると投稿した。いきなり大きな数字が登場し、ニュースの舞台に新しい主役が出てきた形だ。

ところが翌日の七月十四日、その主役はあっさり交代する。トランプ氏は二割の償還料を、湾岸諸国によるアメリカとの貿易や投資の案件に置き換えると投稿した。中東の指導者たちとの「非常に生産的な協議」に基づく決定だと説明したのだ。

さらに記者団には、ホルムズ海峡を通る船舶に誰も料金を課すべきではないとの考えを示し、料金という考え方自体を好まないとも述べた。前の日に出てきた料金案が、次の日には別の話へ置き換わったことになる。

ここで普通なら、料金の話が消えたのだから、原油価格も落ち着きそうに見える。実際、発表直後のブレント原油先物は、上げ幅をいったん縮めた。

しかし、値動きはそこで終わらない。価格はほどなく、発表前に近い高い水準へ戻った。記事掲載時点では、およそ二・六パーセント高で、一バレル八十五ドルを上回っていた。

この戻りが面白い。政治の舞台では看板が掛け替えられたのに、価格の舞台では、数字がすぐ元の勢いを取り戻したからだ。しかもその時間帯には、米国とイランの間の攻撃、海上封鎖、タンカーの安全への懸念が続いていた。

今回わかるのは、発表の言葉が変わったことと、価格の動きが同じようには変わらないことがある、ということだ。料金案は置き換えられても、同じ時間に続いている出来事まで、発表一つで舞台裏へ消えるわけではなかった。
```

### Hormuz — Advanced(English、最終、`LEDGER_COMPLIANT`)

```
# The 20% Fee Plan Is Withdrawn, but Oil Prices Quickly Return

Oil price news sometimes gets its best ending not from the policy announcement itself, but from the move that follows. The words on the political stage may change before the market has finished reacting. This story sets up a familiar expectation: if a new charge is withdrawn, the market should settle. The surprise comes when the words change, but the price refuses to follow. The story also unfolds like a play. A new lead appears, leaves the stage, and leaves behind a question: will the market leave with it?

### A new fee takes center stage

On July 13, President Trump posted that all cargo passing through the Strait of Hormuz should pay a 20% charge to cover U.S. efforts to keep the strait safe. The next day, he said it would be replaced by trade and investment deals involving Gulf countries and the United States, based on "very productive talks" with Middle Eastern leaders.

Trump also told reporters that no one should charge ships passing through the strait, and said he did not like the idea of a fee. So the plan announced one day had been replaced by another story the next. With the fee idea gone, oil prices might now be expected to calm down. But the next movement came from another part of the stage.

### The price refuses to exit

Brent crude futures briefly gave back some of their gains after the announcement. But prices soon returned to a high level close to where they had been before it. At the time of publication, they were about 2.6% higher, above $85 a barrel. Meanwhile, attacks involving the U.S. and Iran, a sea blockade, and concerns about tanker safety continued.

## In one line

The political sign changed, but the price soon returned: the words were replaced, while the events behind them stayed onstage.
```

注: 上記はHormuz Advanced「2回目」(must-fix後、`LEDGER_COMPLIANT`)の
本文。この段でMain Story段落数チェックがクラッシュしたため`parts.json`
は未生成(§14)。

### Meta — JA(R2、最終)

```
AI電話のはずが、舞台裏から人間が登場した

AIに散髪の予約を頼む。店に電話をかけ、在庫を聞き、業者から見積もりを取る。そんな仕事を、画面の中のAIが全部やってくれる。なかなか便利な未来です。

MetaのAIエージェント、Museには、実際にそうした電話機能があります。

ところが、その舞台裏で予想外の展開が起きました。Muse経由の電話の一部で、電話をかけていたのはAIではなく、訓練を受けた人間の契約スタッフだったのです。

Museが依頼を受ける。そこまではAIです。けれど、その先で人間スタッフに仕事を引き渡す。スタッフが電話をかけ、相手とのやり取りを終える。まるでAI主演の舞台に、台本には見えにくい助演者が登場したような話です。

この仕組みは、人間コンシェルジュと呼ばれていました。人間が電話を担当すること自体が、ただちに問題だったわけではありません。大きな問題になったのは、その事実を十分に知らせないまま、テストが始まったことです。

Metaの従業員からは、電話に必要な利用者の機微情報が、コールセンターの契約スタッフに意図せず共有されるかもしれないという懸念が出ました。

ここは大事なところです。大規模な情報漏えいが起きたと確認されたわけではありません。ただ、AIに頼んだ仕事を、実際には誰が担当しているのか分からない。しかも、その人に自分の個人的な情報が伝わる可能性がある。そうなると、便利なサービスが急にミステリー作品のように見えてきます。

Metaの幹部は、適切な説明なしにテストを始めたのはミスだったと認めました。そして、人間が電話を担当する機能を、当面はいったん元に戻しました。Museそのものを止めたわけではありません。

今後は、準備が整い、誰が電話をするのかをきちんと説明できる場合にだけ、公開する方針です。

AIが仕事をしてくれる時代でも、人間が助けに入ることはある。けれど、そのとき必要なのは、こっそり登場することではありません。舞台に上がるなら、最初に名前を名乗る。今回の一件は、そんな当たり前のルールを、かなり印象的に見せてくれました。
```

### Meta — Advanced(English、最終、`LEDGER_COMPLIANT`)

```
# It Was Supposed to Be an AI Call—Then a Human Appeared Backstage

Imagine asking AI to book a haircut. Or asking it to call a store and check whether something is in stock. It could even ask a supplier for a price estimate. In this convenient future, the AI on your screen handles everything for you.

Meta's AI agent, Muse, really does have phone features like these. So it sounds like a simple story: you make a request, and AI takes care of the call. But the picture changed once people looked behind the stage.

### The call that was not made by AI

Some calls through Muse were not made by AI at all. Trained human contract workers made them. Muse received the request—that part was AI—but then passed the job to a person. The worker made the call and finished the conversation. It was like an AI-led play with a hidden supporting actor. The system was called "human concierges."

The hidden role made the simple picture less simple.

### Why the hidden role mattered

Meta employees worried that sensitive information needed for the calls might be shared by mistake with contract workers at a call center. The issue was not that humans handled calls. It was that testing began without clearly telling users about it. A service that seemed simple now looked like a mystery story.

No large information leak was confirmed. But users could not know who was really doing the work they had asked AI to do—and their personal information might reach that person. That uncertainty turned convenience into a mystery.

A Meta executive admitted that starting the test without a proper explanation was a mistake. Meta then temporarily put the human-call feature back on hold. The company did not stop Muse itself.

In the future, Meta will make the feature public only when it is ready and can clearly explain who will make the call.

Even in an age when AI does our work, a human may still need to help. But that person should not appear secretly. If they step onto the stage, they should give their name first. This case made that simple rule unusually clear.

## In one line

AI may need human help, but humans must say clearly when they take over.
```

### 参考指標(成功条件にしない、目視列挙のみ)

- Hormuz JA: Arabic数字表記なし。漢数字による数量表現(七月十三日・
  二割・二・六パーセント・一バレル八十五ドル)は理解に必要な範囲で
  複数残存。固有名詞: トランプ氏、ホルムズ海峡、ブレント原油。
- Meta JA: 数字表現は本文中0件(Arabic・漢数字とも)。固有名詞: Meta、
  Muse。
- 上記はAN3の定性的な効果を示す参考データであり、本タスクの成功条件
  ではない(主判定はLedger Deviation Check、§9)。

---

## テスト結果

- 新規: `er019_family_x_concreteness_an3_t0_production_wiring_01_test_01.py`
  17件PASS(`python -m unittest`実行、pytest未インストールのためunittest
  で実行)。
- 既存regression: `run_project_regression.py --pattern "er019*_test_*.py"`
  → collected=143 passed=143 failed=0 errors=0(新規17件含む)。
  `--pattern "er037*_test_*.py"` → 12件PASS。
  `--pattern "er039*_test_*.py"` → 17件PASS。

## 費用実測

Hormuz ¥8.822 + Meta ¥5.209 = **合計¥14.031**(Guardrail上限¥15内)。
内訳はraw_usage_log.jsonlから`compute_stage_cost_breakdown()`で算出
(§8のout-dir配下に保存済み)。research_ledger/storyline_b3はreuseの
ため追加費用¥0。

## STOP・費用超過なし

暴走疑いの兆候(想定外の大量API/Web Search発火・同じ失敗の無意味な
retry loop・原因不明の費用増加・scope外処理・QCD上不合理な追加処理)
は発生していない。Hormuz Advancedの構造チェック失敗への対応(1回のみの
`--stage advanced`再実行)は、既存のProduction運用capability
(`--regenerate-stage advanced`相当の手動再実行)の範囲内であり、2回目
失敗後はこれ以上のretryを行わず報告に切り替えた(§14)。

## §9. `git diff --stat`(コード側の変更範囲確認)

`git diff --stat HEAD -- "er0*.py"`:

```
 er019_family_x_ja_writer_o_r1_r2_01.py | 37 +++++++++++++++++++++++++++++++---
 1 file changed, 34 insertions(+), 3 deletions(-)
```

`er019_family_x_ja_writer_o_r1_r2_01.py`のみが本タスク由来の変更。
`er037`/`er039`(Trial script)、`er003_v1_n3_01_advanced_adaptation_
generate.py`(Advanced Prompt)、Family A/B/Y/Z関連ファイルはいずれも
変更なし。

## §10. TTS/ASR不呼び出しの根拠(実行前確認事項)

`er019_family_x_entertainment_production_runner_01.py`のimport文
(L44-48)は`vfl01`/`cl`/`efam`/`jaw`/`b3`のみで、TTS/ASR/scaffold/
assemble/player関連モジュールを一切importしていない(ファイル冒頭
コメントL24-26にも構造的Mandatory STOPとして明記)。`efam.run_writer_
stage(..., only="advanced")`が呼ぶのは`adv_gen.generate_advanced_
adaptation()`(JA→English変換、テキストのみ)であり、TTS呼び出しは
含まれない(`er012_e_family_entertainment_two_level_runner_01.py`
L304-306確認)。本タスクでは`--stop-after advanced`を指定し、
`--stage standard`/`--stage all`は一度も実行していない。

## §14. 新規発見: Hormuz Advanced生成でのMain Story段落数チェック失敗
(新規OPEN-228、修正せず報告のみ)

Hormuz Advanced生成で、`h3_count==2`の構造Gate(`validate_point_
structure()`、`run_writer_with_technical_retry()`内でmax_attempts=2の
自動retry付き)はPASSしたが、その後段の`er012_e_family_entertainment_
two_level_runner_01.py::run_writer_stage()`が呼ぶ`er003_v1_n3_01_
scaffold_generate.py::split_article_text()`の「Main Story(タイトル
直後、最初の###見出し前の導入部)は段落数2以上」というチェックに2回
連続で失敗した(`RuntimeError`、自動retry機構なし、未捕捉のまま
main()がクラッシュ)。

- 1回目: Advanced deviation `LEDGER_COMPLIANT`(MAJORなし)判定後に
  クラッシュ。
- 2回目(`--stage advanced`を同一コマンドで再実行): Advanced deviation
  MAJOR 1件→既存must-fix retryで`LEDGER_COMPLIANT`に解消後、再度同じ
  段落数チェックでクラッシュ。

Meta側は1発でこのチェックもPASSした(§4のMeta Advanced本文参照)ため、
AN3固有の系統的問題とは断定できない(n=1の偶発的な生成ばらつきの可能性
が高い。JA記事の段落数・情報量はHormuz/Meta双方とも既存baselineと近い
水準)。この構造チェックはTTS準備専用の成果物`parts.json`
(`er019_family_x_audio_production_runner_01.py`のみが消費、本タスクでは
実行しない)の生成失敗に留まり、article.md本文・Fact Check・Prompt
sha256などの本タスクの証拠(§9のチェックリスト)には影響しない。

本タスクの禁止事項(新規Validator/retry機構の追加禁止)に従い、この
チェックへの修正・retry追加は行わず、新規OPEN-228として
`OPEN_ITEMS.md`へ記録した。2回連続の同一失敗以降は追加retryを行わず、
governanceの「同じ失敗の無意味なretry loop」STOP基準に抵触する前に
対応を打ち切った。

## commit・push

commit `1f47ff72`(実装+テスト+確認用再生成evidence+REPORT+SSOT一括、
`git push origin main`成功、`b814f241..1f47ff72`)。

## Fable Gate 3判定に必要な残確認事項

1. OPEN-227(R2 must-fix経路のSYMBOL_PREVENTION_BLOCK_JA非対称性)の
   是正要否。
2. OPEN-228(Main Story段落数チェックの自動retry追加要否、AN3との
   因果関係のn=1超サンプルでの再現性確認要否)。
3. OPEN-220(Advanced Prompt側固有名詞抑制拡張要否、`DEFERRED`のまま)。
4. 生成されたHormuz/Meta記事本文(§4)自体のユーザー確認・試聴判断
   (既存Mandatory STOP、音声化は本タスクのスコープ外)。

## §16. ユーザー決定による R1/R2 reminder削除(2026-09-28、委任_04)

### 背景・ユーザー決定(逐語要旨)

Trial-02(`er039_family_xy_concreteness_control_trial_02.py`)でAN3-T0を
実測評価した際の実際の構成は、Original生成時にAN3(A3+N2)を追加するのみで、
R1/R2は既存Revision指示(`REVISION_INSTRUCTIONS["r1"/"r2"]`)のみであり、
`CONCRETENESS_CONTROL_AN3_REMINDER_JA`のようなreminder文は含まれていな
かった。Phase B(委任_02)でProduction Wiring時に独自追加した当該reminder
は、Trialで検証されていない未Trial追加仕様であったため、ユーザーが
Production正式経路から外すことを決定した(2026-09-28)。

### 削除箇所(ファイル・行、修正前後)

`er019_family_x_ja_writer_o_r1_r2_01.py`:

1. `CONCRETENESS_CONTROL_AN3_REMINDER_JA`定数定義(旧L109-115、コメント+
   定数本体)を削除。`CONCRETENESS_CONTROL_AN3_BLOCK`(Original側)は
   無変更のまま維持。
2. `verbatim_shas()`から`concreteness_an3_reminder_sha256`キーを削除
   (旧L130)。`concreteness_an3_block_sha256`キーは維持。
3. 通常r1/r2ループ(旧L357-360): `instruction = (REVISION_INSTRUCTIONS
   [stage_key] + SYMBOL_PREVENTION_BLOCK_JA + CONCRETENESS_CONTROL_AN3_
   REMINDER_JA)` → `instruction = REVISION_INSTRUCTIONS[stage_key] +
   SYMBOL_PREVENTION_BLOCK_JA`(Phase B以前=commit `b814f241`時点の
   逐語に復元)。
4. R2 Fact Check must-fix経路(旧L403-408): `r2_must_fix_instruction`
   からreminder追記を削除、`REVISION_INSTRUCTIONS["r2"] + "\n\n" +
   build_must_fix_block(...)`のみに復元(`b814f241`時点の逐語)。
5. R2音声記号must-fix経路(旧L464-469): `r2_symbol_instruction`から
   reminder追記を削除、`REVISION_INSTRUCTIONS["r2"] + SYMBOL_PREVENTION_
   BLOCK_JA + "\n\n" + safety.build_symbol_violation_prompt_note(...)`
   のみに復元(`b814f241`時点の逐語)。

fallback_full_text経路(`previous_response_id`失敗時)は上記3経路と同一の
`instruction`変数をそのまま使うため、reminder文言は当然残らない
(fallback専用の追加箇所は存在しない)。

### Phase B以前(commit `b814f241`)との逐語一致diff結果

`git show b814f241:er019_family_x_ja_writer_o_r1_r2_01.py`を一時ファイルへ
出力し、現行ファイルと`diff -u`で比較した結果、残る差分は以下3箇所のみ
(全てOriginal側=`CONCRETENESS_CONTROL_AN3_BLOCK`関連、ユーザー決定で
「Original側のみ維持」とされた部分と完全一致):

1. `CONCRETENESS_CONTROL_AN3_BLOCK`定数定義(コメント6行+定数本体6行、
   `build_original_prompt()`より前に新設)。
2. `verbatim_shas()`内`"concreteness_an3_block_sha256": sha256_text(
   CONCRETENESS_CONTROL_AN3_BLOCK)`の1キー追加。
3. `build_original_prompt()`内`prompt += CONCRETENESS_CONTROL_AN3_BLOCK`
   の1行追加。

R1/R2の3経路(通常ループ・R2 Fact Check must-fix・R2音声記号must-fix)に
対応する箇所は、`b814f241`との差分ゼロ(diffに出現しない=完全一致)を
確認した。すなわちR1/R2は現在Trial-02と同一条件(既存Revision指示のみ)
に戻っている。

`diff -u`出力全文(`git show b814f241:er019_family_x_ja_writer_o_r1_r2_
01.py`との比較、3ハンクのみ、全てOriginal側):

```diff
--- jaw_b814f241.py (commit b814f241)
+++ er019_family_x_ja_writer_o_r1_r2_01.py (現行)
@@ -94,6 +94,18 @@
     "- URLやメールアドレスは書かないでください。絵文字も使わないでください。"
 )
 
+# FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01(2026-09-28): Trial
+# (er037/er039)のA3+N2(AN3、ユーザー正式決定APPROVED_FOR_PRODUCTION)を
+# 逐語で移設。R0_PROMPT自体は無変更、build_original_prompt()で別途追記
+# する(SYMBOL_PREVENTION_BLOCK_JAと同型パターン)。「数字を0にする」とは
+# 定義しない(定性的な抑制指示であり数値目標ではない)。
+CONCRETENESS_CONTROL_AN3_BLOCK = (
+    "\n\n数字・時刻は基本的に使わないでください。記事の理解に本当に必要な場合"
+    "だけ、最小限に使ってください。\n"
+    "人名・企業名・地名などの固有名詞は、話の理解に必要な場合だけ使い、それ"
+    "以外は一般的な言い方にしてください。"
+)
+
 
 def sha256_text(text: str) -> str:
     return hashlib.sha256((text or "").encode("utf-8")).hexdigest()
@@ -105,6 +117,8 @@
         "developer_message_sha256": sha256_text(DEVELOPER_MESSAGE),
         "r1_instruction_sha256": sha256_text(REVISION_INSTRUCTIONS["r1"]),
         "r2_instruction_sha256": sha256_text(REVISION_INSTRUCTIONS["r2"]),
+        # FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01(2026-09-28): 追加
+        "concreteness_an3_block_sha256": sha256_text(CONCRETENESS_CONTROL_AN3_BLOCK),
     }
 
 
@@ -146,6 +160,7 @@
     prompt = "\n".join(new_lines)
     prompt += "\n\n[ニュース]\n" + selected_fact_brief_text
     prompt += SYMBOL_PREVENTION_BLOCK_JA
+    prompt += CONCRETENESS_CONTROL_AN3_BLOCK  # FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01
     if must_fix:
         prompt += "\n\n" + build_must_fix_block(must_fix, full_ledger_text or "")
     return prompt
```

`grep -n "再び増やさない" er0*.py`の結果は、本削除確認用に新設した
regressionテスト(`er019_family_x_concreteness_an3_t0_production_wiring_
01_test_01.py`内の`assertNotIn("再び増やさない", self.source)`という
文字列リテラル1件のみ)であり、Production側コード(`er019_family_x_ja_
writer_o_r1_r2_01.py`を含む全er0*.pyのProduction module)には0件。

### テスト結果

`er019_family_x_concreteness_an3_t0_production_wiring_01_test_01.py`の
`R1R2ReminderThreeLocationsTests`を`R1R2NoReminderThreeLocationsTests`
へ置換し、3経路とも「reminderが含まれないこと」「Phase B以前の逐語と
一致すること」をassertする内容へ変更、`VerbatimShasIncludeAN3KeysTests`
も`concreteness_an3_reminder_sha256`が存在しないことをassertする内容へ
変更した(Original側のBLOCK含有・er037逐語一致・T1不在・Advanced Prompt
sha一致のテストは無変更のまま維持)。単体実行18件全PASS。
`run_project_regression.py --pattern "er019*_test_*.py"`は157件中156件
PASS、1件FAIL(`er019_family_x_pointless_01_test_01.
FamilyAUnchangedTest.test_family_a_files_have_no_working_tree_diff`、
`er003_v1_n3_01_tts_generate.py`の未commit差分を検知するテスト。この
ファイルは本タスク開始時点で既に並行作業中の別Sonnet[Task 4 Phase B]が
編集中であり[委任文T-0記載]、本タスクの変更対象外・無関係。本タスクの
変更適用前から存在する差分であり、本削除作業に起因するFAILではない)。
`er037*_test_*.py`(12件)・`er039*_test_*.py`(17件)は全PASS
(Trial script側は無変更のため回帰なし)。

### runtime evidenceの扱い

`er019_output/family_x_entertainment_production_runner_01/an3_t0_wiring_
regression_01/{hormuz,meta}/`配下の既存`runtime_evidence.json`
(`ja_writer/runtime_evidence.json`等)は、Phase B時点(reminderあり構成)
の実測記録であり、削除・上書きせずそのまま残す。reminder削除後のR1/R2は
Trial-02(`er039`、AN3-T0セル)と実行時の構成が同一(Original側のみAN3
BLOCKを追加、R1/R2は既存Revision指示のみ)であり、Original側の
`CONCRETENESS_CONTROL_AN3_BLOCK`定数の文言・sha256は本修正で一切変更して
いない。したがってTrial-02の実測結果(AN3-T0セルのJA/EN記事)が、reminder
なし構成でのR1/R2挙動の実証根拠となる。**本タスクではAPI再生成を行って
いない(¥0)**。

### Checklist項目「R1/R2で数字・固有名詞を再前景化しない既存方針との整合」
の再評価

設計書§3-2で提起されたこの要件は、Phase B時点ではreminder追加により対応
していたが、Trial-02で未検証の仕様であったため、ユーザー決定によりこの
対応方法自体を撤回した。現在は「Trial-02と同一条件(R1/R2は既存Revision
指示のみで、reminder等の追加なし)」を要件充足の基準とし、この基準で
充足していることを上記regressionテストで機械的に確認した。

### commit・push

commit `54739a9d`(実装+テスト+REPORT+設計書+delegation_log一括、
`git push origin main`成功)。

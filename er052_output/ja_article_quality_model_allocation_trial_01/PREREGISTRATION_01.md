# PREREGISTRATION_01(案): JA記事品質 工程別モデル配置Trial

管理ID: FAMILY-X-JA-ARTICLE-QUALITY-MODEL-ALLOCATION-TRIAL-01 委任_02
Status: DRAFT(案。Fable/ユーザー承認前。課金実行は承認後の別委任)
区分: DEV/Trial。Production採用判断を含まない(採用は`APPROVED_FOR_PRODUCTION`を人間ユーザーのみが承認)。
設計: `DESIGN_01.md`(同ディレクトリ)。使用モデル報告(PM_GOVERNANCE 25節): Luna=`gpt-6-luna`、Astra=`gpt-6-astra`、Sol=`gpt-6.1-sol`(案。確定待ち)。いずれもユーザー指定の配置。Sol idの最新性は価格登録(2026-10-09取得)と過去API実績で確認、`gpt-6-sol`との関係は未確認。

## 1. 目的・問い
META記事(OPEN-255:品質懸念)のR2日本語記事を、工程別モデル配置5案で比較し、「どの配置が人間ユーザーの品質判断で良いか」を調べる。A=現行Production、B=旧仕様(既存、委任_01)、C/D/E=新規。

## 2. 比較条件(案)
| 案 | B3① | R0 | R1 | R2 | 実行 |
|---|---|---|---|---|---|
| A 現行 | Luna | Luna | Astra | Astra | 既存`er019_output/meta/run_regen_01`複製(課金0) |
| B 旧仕様 | (委任_01の定義) | | | | 既存再利用(課金0。委任_01で確定) |
| C | Luna(A再利用) | Astra | Luna | Luna | 新規1回 |
| D | Astra | Luna | Luna | Luna | 新規1回 |
| E | Sol | Sol | Sol | Sol | 新規1回 |
注: B3②(決定論注記・制約付与)は全案Production同一(LLM無し)。

## 3. 固定するもの(実行前assert、`runtime_evidence.json`へ記録)
| 項目 | 値 |
|---|---|
| Fact Ledger | `er019_output/meta/run_regen_01/research_ledger/verified_fact_ledger.txt` sha256 `ea0ce587e605beeac8f02315ae4520899156393bbba2e059d99f45988b7c5f56` |
| topic(B3入力) | `Meta Muse AI電話代行「人間コンシェルジュ」実験` |
| B3 developer message sha | `b4391b0387c54d39cf2ed095e7c00e028b13f173065ed0077b3a16f0fe37981a` |
| B3 user template sha | `d6fe9bc33ceccf4c4af3a44ce12b9d83ef7c2efe04de4dfbb2cf17adb02ff333` |
| B3 fact test定義 sha | `91513c8999a63439adb40d5c28a253e4cdbb438228ba1deda199d2ae6c6c5a8a` |
| B3 JSON schema(json.dumps sort_keys, ensure_ascii=False)sha | `ccfef73de9a12a232284786d9a52d935fcb3d66357e7f123febd2665c4903d51` |
| W-1 `USER_TMPL`(R1/R2) sha | `313120e94232497290e7efac2df1210dc628a8a1b497bb04e7174b5a98442f7f` |
| `R0_PROMPT` sha | `6108a7cddaa9eaf31262354ba32d33e4683ccaf810d861f27e3dcc8972028366` |
| W-1 `DEVELOPER_MESSAGE`(R0のみ) sha | `d1fbb04224d346e79c588b8e69da4dcfe26e758ceefc71aa83d13ff7f216ed8d` |
| `SYMBOL_PREVENTION_BLOCK_JA` sha | `0629ab47a18ccb986844d8cff4ea087a9690eb8a7b8aefb28039496eec603b73` |
| `CONCRETENESS_CONTROL_AN3_BLOCK` sha | `067030ff53ecb76a4d1477a3deace07b3e1fac438a33cb873edbe045cf6927fe` |
| `FACTLOCK_R0_BLOCK_HEAD` / `TAIL` / `R0_BLOCK` sha | `e72822deeabf4d395b02e5f03b7a6a177203b123d9a41613a0347cb53e9377fc` / `4ff7844384e20534ae45e1e6a19a79970cfe88cfac6d05822723d605f8396d5f` / `74b948719e14fd7184ff3719d36639ede7905e45cef95b97c1cca1a5638b2bf1` |
| 後処理regex sha | `TAG_RE e741d7b5…2c70`、`BROAD_TAG_RE 3040b637…653d`、`MARK_RE b1a952f9…9cf4`、`TAG_LEAK_RE 25219395…4ed8`、`ECHO_RE fcce9077…d5`(全値は`verbatim_shas()`の出力) |
| R0 prompt全文(参考) | A runの`r0_prompt_sha256 = bc835749de9218ff54f178889419dd868267dde1e232f0dec046afb31f24a331`。R0 promptは注記済みB3に依存するため案ごとに異なる(C=Aと同一になるはず=C再利用の検証に使う) |
| reasoning effort | 全stage `high` |
| 呼出条件 | developerはR0のみ(`DEVELOPER_MESSAGE`)、R1/R2はなし。`previous_response_id`なし。temperature/seed/max_output_tokens/service_tier/text.format(B3のjson_schemaを除く)を送らない |
| R2入力 | R1の生出力(後処理前)のファイル往復(CRLF→LF) |
| 記号QA | R0再生成最大1回、R2再実行最大1回(同一R1 raw)、残ればSTOP |
| module sha | writer `87339033…2e4a38`、B3 `93d0e31e…b758`、producer `8899d0fa…155f2`、contract `5f4c725e…017885`、jaw `a696d8f2…b8b0`、routing `438df87d…c285`(全値はDESIGN_01 2-5。実行前後で一致をassert) |
| 為替・単価 | USD/JPY 160、`pricing_snapshot.json`登録値 |

## 4. 変えるもの
**各stageのmodel idのみ**(2節)。Prompt本文・Ledger・effort・呼出条件・後処理・QAは不変。driver内のmodel gateは`routing.require_model_or_override`(理由つき)。Production routing contractは不変。

## 5. 測定項目
(a) 人間(ユーザー)のBlind評価(主): 5本の匿名比較(記事①〜⑤、`user_test/ja_quality_model_allocation_01/index.html`、音声なし、割当はseed固定でBLIND_MAP_01.jsonに別保存、結果提示までチャットに出さない)。順位、各記事の「公開してよい水準か」、自由コメント。
(b) 補助評価(機械、Fable/Claude): 文字数・文数・です/ます率、選択Fact数、使用tag数、Fact忠実性(数値・固有名詞のLedger照合)、制約文混入grep、記号QA結果、タグ残存・R0復唱、生成時間(stage別秒)。人間判断の代替ではない。
(c) 費用: stage別 input/output/reasoning token・USD・JPY。案別・累計。
(d) 運用面: 返却model id(requested=returnedの前方一致)、STOP/再生成の有無と回数、effort/json_schemaの受理可否。

## 6. 判定基準(案)
ユーザー品質判断が主。機械指標は補助で、単独で採否を決めない。
- **VALIDATED(候補として有望)**: ユーザーBlind評価で、C/D/Eのうち少なくとも1案がAより明確に良い(上位かつ「公開水準」と判断)かつ、(b)で重大な忠実性退行なし(Ledger非掲載の数値・固有名詞0件、制約文混入0件、記号QA/Provenance STOPなし)。ただしN=1なのでStatusは`VALIDATED`ではなく`MEASURED(N=1)`止まりとし、Production採用検討に必要な追加検証(複数テーマ・複数回、費用対効果、routing変更の別承認)は別途提案する。
- **REJECTED(その案を却下)**: ユーザー評価でAと同等以下、または(b)で重大な忠実性退行(Ledger外の数値/固有名詞の断定、制約文混入、記号QA STOP)がある案。
- **USER_DECISION_REQUIRED**: (i) 品質が良い案が費用増(Aより高額、D案は約¥41/記事、C案は約¥32/記事 対 A約¥35.6を踏まえて判断)を伴い、採否が費用対効果の価値判断になる場合、(ii) ユーザーが優劣を付けにくい場合、(iii) 追加Trialや仕様変更が必要になる場合。Production採用は人間ユーザーのみ。
- 帰属上の限界(必須注記): 各案は複数stageが同時に変わる(C=R0/R1/R2、D=B3/R1/R2、E=全4)ため、「どの工程のモデルが効いたか」は単一因子として特定できない。N=1のため非決定性との分離もできない。因子分離が必要なら別Trialを提案する。

## 7. 費用
上限: C/D/E合計 ¥200(A/Bは再利用で¥0)。案別cap C ¥65 / D ¥85 / E ¥50。各案**1回のみ、自動追加なし**。点見積合計 約¥94.5、×1.5で約¥142(DESIGN_01 7節)。各call前に累計+保守見積≤案capをチェック、超過見込みはSTOP。

## 8. STOP条件(草案。ユーザー指示の6点の原文を受け取っていないため、原文で差替え要)
1. 累計実測または次call見積で案cap/総額¥200を超える見込み。
2. C/D/E各案の追加実行・自動再生成が必要になる(1案1回のみ。技術retry・記号QA再生成/再実行は既存のProduction同一の上限のみ)。
3. 指定構成が技術的に成立しない(model id不明、effort=high非受理、B3 json_schema非受理等)。自動で別model・別effortへ降格しない。
4. Production code/Prompt/Routing/SSOTの変更が必要になる、またはTrial driverがProduction経路へ混入する。
5. Provenance不一致(返却modelが指定と異なる)、Prompt/Ledger/module shaの不一致、等価テスト不合格。
6. 記号QAがProduction同一上限後も残る(案STOP)、またはBlind対応表がチャット等に漏れる。
(いずれも発生時は実行を止めてFable/ユーザーへ報告。)

## 9. 手順(承認後の実装委任の見取り図)
1. (無課金)driver実装、等価テスト、見積assert、Blind page generator、評価script。モデル一覧取得(無料)でSol id存在確認。
2. (課金)C/D/Eを3 process並列で各1回実行(各自のout_dir、cost log、cap)。
3. A複製、B(委任_01)統合、Blind page生成、BLIND_MAP別保存、補助評価。
4. ユーザーBlind評価依頼(対応表は評価後に開示)。

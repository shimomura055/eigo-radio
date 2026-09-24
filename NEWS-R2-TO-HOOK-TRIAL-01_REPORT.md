# NEWS-R2-TO-HOOK-TRIAL-01 REPORT

管理ID: `NEWS-R2-TO-HOOK-TRIAL-01`
実行日: 2026-09-24(JST)
性質: Trial(仮説「Hookを記事作成前ではなく2回目revision完成記事[R2]の後に作れば、Reference級Hookへ近づく」の検証)。到達上限Status=`VALIDATED`。
Production変更なし。

---

## §0 条件

- Prompt(逐語、Fable固定、変更・追加なし):
  - developer: `あなたはHook Writerです。`
  - user: テーマ文+R2記事全文を埋め込んだ固定テンプレート(`er016_news_r2_to_hook_trial_01.py` `USER_TEMPLATE`)。
- 入力: 各記事のテーマ文(1文)+R2完成記事全文のみ。
- **含めていないもの**: Reference Hook(REFERENCE_20)、過去のLuna/Terra/Sol Hook(旧Topic概要→Hook方式の出力)、ユーザー評価点、Fable評価、他モデルの出力、previous_response_id(各callは独立)。
- Model: `gpt-5.6-luna` / `gpt-5.6-terra` / `gpt-5.6-sol`。Effort: `medium`(全モデル同一)。
- Schema(json_schema strict): `{"hook_ja": string, "used_angle_ja": string}`(両方required、additionalProperties false)。
- 対象記事: A. sewer(下水道、入力=TRIAL-01 R2)/B. ai_phone(AI電話代行、入力=TRIAL-02 Article A R2)/C. travel_bag(旅行荷物、入力=TRIAL-02 Article B R2)。
- 新規記事本文の生成なし(既存R2全文をそのまま使用、sha256一致確認済み、§Fに詳細)。

---

## §A 比較表(転記)

### 表1: R2タイトル / Existing・Reference Hook / 旧方式(Topic概要→Hook) / 新方式(R2記事→Hook)

| Article | R2タイトル | Existing/Reference Hook | 旧方式Luna | 旧方式Terra | 旧方式Sol | Luna from R2 | Terra from R2 | Sol from R2 |
|---|---|---|---|---|---|---|---|---|
| sewer | “合併”するのは町じゃない？　下水道の大引っ越し作戦 | Referenceなし(下水道は既存Trialに対応するReference Hookが存在しない。R2タイトルを比較対象とする) | 旧方式なし | 旧方式なし | 旧方式なし | 町に一つの巨大な洗濯機を、家ごとに分けるって？ | 町の地下の大動脈、家のそばへ引っ越せる？ | 町の巨大な洗濯機を、家ごとに置き直すってどういうこと？ |
| ai_phone | 「もしもし、AIです」――その声の裏で、人間が代役を務めていた | AIに店への電話を頼んだら、裏では人間が話していた？ | 電話対応をAIに任せても、人間は必要？ | AI電話でも、難しい場面は人が支える？ | AIの電話代行を人間が補うって不思議じゃない？ | AIに任せた電話、実は人間が話していたら？ | AIに任せた電話、実は誰が話していたと思う？ | AIに任せた電話を、実は人間が聞いていたら？ |
| travel_bag | 旅行バッグ満員事件、犯人は服ではなく「服が連れてきた空気」 | 旅行の荷物は、なぜ毎回バッグいっぱいになる？ | 旅行の荷物は、減らすより圧縮して運ぶ？ | 荷物を減らせなくても、旅のストレスは減らせる？ | 旅行荷物、減らすより圧縮するのが人気なのはなぜ？ | 服を何枚か入れただけで満員になるバッグ、実は空気も一緒に詰めてる？ | バッグを満員にしていたのは、服ではなく空気かも？ | 旅行バッグを満員にした犯人、服が連れてきた空気かも？ |

(旧方式は`er016_output/news_hook_model_comparison_01/hooks_{model}.json`の reference_id 1[ai_phone相当]・13[travel_bag相当]を転記。sewerは旧Trial対象外のため「旧方式なし」「Referenceなし」。)

### 表2: used_angle_ja

| Article | Model | used_angle_ja |
|---|---|---|
| sewer | luna | 町全体の大きな水処理の仕組みを、家ごとの小さな洗濯機に分けるたとえを使いました。 |
| sewer | terra | 古くなった下水道を延命する代わりに、家の近くで水を処理する仕組みへ変えるという見方を使いました。 |
| sewer | sol | 町全体の下水処理を巨大な洗濯機、合併浄化槽を家ごとの小さな洗濯機にたとえた場面を使いました。 |
| ai_phone | luna | AIがひとりで演じているように見える電話の裏で、人間の契約スタッフが代役を務めていた場面を使いました。 |
| ai_phone | terra | AI電話代行の試験で、一部の通話を人間の契約スタッフが担当していたという舞台裏を使いました。 |
| ai_phone | sol | AI電話代行の舞台裏で、人間の契約スタッフが通話を担当していた場面を使いました。 |
| travel_bag | luna | 服のふくらみの中にある空気を、服が連れてきた同伴者として捉える見方を使いました。 |
| travel_bag | terra | 服そのものではなく、服のふくらみに含まれる空気がバッグ内のスペースを占めているという見方を使いました。 |
| travel_bag | sol | 服そのものではなく、服のふくらみに含まれる空気が場所を取っているという見方を使いました。 |

### 表3: 機械統計(観察事実のみ)

| Article | Model | 文字数 | ？終端 | でしょうか含有 | R2タイトル一致率(SequenceMatcher) | Fact機械一致(数字・カタカナ語が記事/テーマ文に存在) |
|---|---|---|---|---|---|---|
| sewer | luna | 23 | True | False | 0.163 | True |
| sewer | terra | 20 | True | False | 0.304 | True |
| sewer | sol | 27 | True | False | 0.151 | True |
| ai_phone | luna | 21 | True | False | 0.346 | True |
| ai_phone | terra | 22 | True | False | 0.264 | True |
| ai_phone | sol | 22 | True | False | 0.340 | True |
| travel_bag | luna | 33 | True | False | 0.226 | True |
| travel_bag | terra | 24 | True | False | 0.491 | True |
| travel_bag | sol | 26 | True | False | 0.655 | True |

全hookが「？」終端・「でしょうか」不使用の条件を満たす(9/9)。Fact機械一致は9/9でTrue(hook中の数字・カタカナ語候補が記事本文またはテーマ文に部分一致、機械検出の範囲で虚偽事実の付加なし)。

---

## §B actual model_id・usage・latency・cost

全9 callで`response.model`実値が要求model_idと完全一致(`gpt-5.6-luna`×3/`gpt-5.6-terra`×3/`gpt-5.6-sol`×3)。詳細は`er016_output/news_r2_to_hook_trial_01/raw_responses/*.json`。

| Model | calls | input_tokens | output_tokens | reasoning_tokens | latency合計(秒) | 単価出典 | total_jpy | per_hook_jpy |
|---|---|---|---|---|---|---|---|---|
| luna | 3 | 2619 | 531 | 289 | 7.912 | pricing_snapshot.json(KNOWN) | ¥0.19 | ¥0.063 |
| terra | 3 | 2619 | 223 | 0 | 5.823 | UNKNOWN(前回同様、単価未確定のためtoken数のみ) | - | - |
| sol | 3 | 2619 | 227 | 0 | 5.921 | pricing_snapshot.json(KNOWN) | ¥3.18 | ¥1.06 |

合計費用(既知単価モデルのみ): **¥3.37**(上限¥30以内)。Terraは前タスクと同様、単価出典が機械的に確定できずUNKNOWN扱い(token数のみ記録、捏造回避)。各call latency詳細は`cost.json`の`latency_seconds_by_call`参照。

---

## §C 非混入検査

`er016_output/news_r2_to_hook_trial_01/contamination_check.json`:
- 検査対象文字列数: 177件(REFERENCE_20 hook_ja 20件+旧方式hooks_luna/terra/sol.json 60件+cont02 hook_test_h3/h3_sol 40件+topic_selection_user_eval_dataset.json 57件)
- 検査対象ファイル: `prompts/*.json` 9件全て
- 検出: **0件**(`contamination_free: true`)
- actual model一致検査: 9/9 `matched: true`(`model_id_all_match: true`)

---

## §D 機械統計(詳細)

§A表3参照。追加観察:
- R2タイトルとの文字列一致率(SequenceMatcher ratio)は0.151〜0.655の範囲。最も高いのはtravel_bag/solの0.655で、タイトルとHookに共通語彙(「服」「空気」「バッグ」)が多い。最も低いのはsewer/solの0.151。
- 「？」終端は9/9で満たす。「でしょうか」使用は0/9(条件通り不使用)。
- Fact機械一致(hook中の数字・カタカナ語候補が記事本文/テーマ文に部分一致)は9/9でTrue。機械検査の範囲では記事に無い固有名詞・数字の追加は検出されなかった。

---

## §E Fable記入欄

- Q1(R2記事を読ませることでHookは改善するか): [Fable記入]
- Q2(Reference Hookの特徴「具体的な場面へ落とす」ことが増えるか): [Fable記入]
- Q3(Lunaでも十分なHookが作れるようになるか): [Fable記入]
- Q4(それでもTerra/Solとの差は残るか): [Fable記入]
- Q5(差が残るなら原因はどこか): [Fable記入]
- Referenceへの近さ: [Fable記入]
- R2タイトルそのものとの比較(別途Hook生成が必要か/そのまま使えるか/短縮のみでよいか): [Fable記入]
- 推奨: [Fable記入]

---

## §F Status

`[Fable分類待ち]`(到達上限`VALIDATED`。Hook Productionモデル・生成順序・R2タイトル流用のいずれもProduction採用しない。)

---

## §G Production変更なし宣言

本Trialでは以下を変更していない: Production Hook generator、Production routing、Topic Search、Writer、retry/fallback機構、`CURRENT_SPEC.md`、`DECISION_LOG.md`、`OPEN_ITEMS.md`、Production prompt。既存`er015_*`/`er016_*` scriptも変更していない(`er016_topic_selection_chatgpt_repro_01.py`をimportのみ、複製・改変なし)。新規記事本文の生成も行っていない(既存R2全文をそのまま入力、sha256一致確認済み)。

---

## 参考: 入力ファイルsha256一致確認

| Article | 入力ファイル(本Trial) | 元artifact | sha256一致 |
|---|---|---|---|
| sewer | `docs/evidence/news_iterative_r2_adoption_2026-09-24/articles/sewer_revision2.md` | `er015_output/news_iterative_entertainment_trial_01/revision2.md` | 一致(a7fa4fd7...) |
| ai_phone | `docs/evidence/news_iterative_r2_adoption_2026-09-24/articles/ai_phone_revision2.md` | `er015_output/news_iterative_entertainment_trial_02/A_revision2.md` | 一致(474c2a16...) |
| travel_bag | `docs/evidence/news_iterative_r2_adoption_2026-09-24/articles/travel_bag_revision2.md` | `er015_output/news_iterative_entertainment_trial_02/B_revision2.md` | 一致(cbd8619b...) |

詳細は`er016_output/news_r2_to_hook_trial_01/run_meta.json`。比較用Hook(REFERENCE_20 id1/13、旧方式hooks_luna/terra/sol.json)は全て生成完了後(assemble-only実行時、2026-09-24 11:57:44 JST)に読み込み。generate完了は同日11:57:14〜11:57:44 JST。

証跡ディレクトリ: `er016_output/news_r2_to_hook_trial_01/`(prompts/, raw_responses/, hooks/, comparison_table.md, mechanical_stats.json, cost.json, contamination_check.json, run_meta.json, r2_titles.json)。

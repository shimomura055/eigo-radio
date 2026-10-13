# phase2_plan_01: Phase 2 Trial設計(JPY50上限、Fable承認後に実行。本委任では未実行・JPY0)

## 1. 目的と比較
方式1(機械抽出改善+Prompt改善)の効果を、同一本文・同一モデルで3条件比較する。
| 条件 | Prompt | shortlist | 見るもの |
|---|---|---|---|
| C0 | 現行(Production) | 現行(Production v5実runのshortlist) | ベースライン |
| C1 | 現行 | 改善(Phase 1-A出力) | 上流改善の単独効果 |
| C2 | 改善(`prompt_after_01.txt`) | 改善(Phase 1-A出力) | 方式1(上流+Prompt)の合成効果 |
| C3(任意) | 改善 | 現行 | Promptの単独効果の分離(予算外、段階化案参照) |
モデル: **gpt-6-luna(Production同一)**。最新モデル原則(`PM_GOVERNANCE.md` 25節)の例外理由=比較可能性(本番ラインと同一条件での挙動比較。実測対象が選定Promptであり、モデル差を混ぜないため)。評価・Trial報告には「使用モデル名/最新か/最新でない場合の理由」を記載する。reasoning effort等はProduction既定のまま変更しない。
実行形態: ABCと同じ(`er064_kp_idiom_priority_abc_01_run.py`の骨格を再利用)。選定→Production canonicalization gate→Production Redundancy QAをProduction関数のまま実行し、**自動retryはしない**(初回gate結果を記録、費用固定化)。反復 n=3/セル。同一セルは同時並列(独立request、rate limitに注意、並列度は低く)。

## 2. 方式2/3(LLM補助抽出あり)の扱い
方式2(LLM補助抽出v4=OPEN-325のb1、本文全文送信)・方式3(その他LLM補助)は、**新規の抽出callを行わない**。既存Phase D成果物(`er064_output/kp_idiom_trial_01/phase_d/` のV2 shortlist・M1 extractor結果)を固定候補として再利用し、**S2(V2 shortlist)に対するC0'(現行Prompt、ABC-Aの既存結果を再利用可)とC2'(改善Prompt)**の2条件だけを追加比較対象にできる。ただし費用はこの¥50に含まれていない(§4のoptional)。本文全文をLLMへ送らない原則(`CURRENT_SPEC.md:1847`)の改訂を要するPkg Eの採否はユーザー判断(設計書§10)であり、本Phase 2はその採否を前提としない。

## 3. 評価指標と期待ラベル
期待ラベル事前登録案(DRAFT、`step3_expected_labels_preregistration_01.json`を基に更新): `phase2_expected_labels_draft_01.json`。承認時にsha256を凍結してから実行する。
主指標: 受入2(Important枠での記事独自比喩混入率)、受入3(Topic妥当性)、受入4(断片採択率)、受入5(good採択率)、受入6(基本連語の占有枠数)。維持確認: `pump one's fist`採択率(上下は合否に使わない)。
副指標: Jaccard安定性(n=3のitem集合)、gate通過率(Rule7起因/選定INVALID/Redundancy NG/QA失敗は別集計、`static_eval_01.md` §4の2層)、`established_or_article_specific`分布とImportant×article_specificのflag件数(記録のみ)、ja_gloss機械検査(括弧・算用数字・「…」。グロス段落統合D12の副作用検査)、費用/出力token/所要時間。
判定の注意: n=3の小標本のため断定せず方向性の確認とする(ABC同様)。「改善」はC2がC0に対して受入2/4/5/6のいずれかで改善し、かつRule7起因を除いたgate通過率が低下しない場合のみ。

## 4. 費用見積(JPY、`phase2_cost_estimate_01.json`、実行前の推定。未実行)
単価: ABC実測(18 job、総計JPY19.1078)から Std 1.185/job、Adv 0.938/job(平均1.06)。Phase D時の0.91は過小(ABC実測のStdが重い)。C2/C3は入力+約10%のため単価に+3%上乗せ。

| 段階 | 内容 | job数 | 費用 | 累計 |
|---|---|---|---|---|
| Stage 1 | Coffee Std/Adv × C0/C1/C2 × n=3 | 18 | 19.30 | 19.30 |
| Stage 2 | meta Std/Adv × C0/C2 × n=3 | 12 | 12.93 | 32.23 |
| Stage 3 | hormuz Std/Adv × C0/C2 × n=3 | 12 | 12.93 | 45.16 |
| (予備) | | | | 残 4.84 |

- 推奨は Stage 1→2→3 の順。各Stage終了ごとにFableへ中間報告し、結果次第で後続を止められる。
- **収まらない比較(未検証と明示)**: 3記事×2Level×3条件×n=3=54 job=JPY57.9(上限超過)。meta/hormuzのC1(上流改善単独の効果、12 job、+JPY12.7)とCoffee C3(Prompt単独効果の分離、6 job、+JPY6.6)は¥50に収まらないため**未検証**とする。つまりmeta/hormuzでは「上流改善の効果」と「Prompt改善の効果」を分離できない(C0 vs C2の合成効果のみ)。分離が必要ならCoffeeに限ってC3(6 job)を追加(累計51.7超過=要追加承認)。
- 停止規則: 累計JPY48到達で新規job停止し報告。retry自動実行なし。1 jobあたり異常高額(>JPY2.5)は即停止。
- 方式2/3用の追加比較(既存V2 shortlistでC2'のみ追加=6 job、約JPY6.6、ABC-Aの既存18 jobをC0'として再利用)はoptional(予算外)。

## 5. 実行前の確認事項(承認時にFableが決める)
1. Phase 1-Aの改善shortlistが確定していること(C1/C2の入力。注釈`含む:`/`タグ:`の仕様確定)。未確定なら、Stage 1はC0とC2'(V2 shortlist)で代替できるか。
2. 期待ラベルDRAFTの凍結(特にmeta/hormuzの`avoid`はユーザー確認待ち)。`pumps its fist`の扱い(設計書§10-E)。
3. OPEN-J(Std冒頭「B1」)の扱い: AfterはTrial専用に「B1」を除去している。C2の差分に含まれるため、効果の帰属を分けたいなら別途C3相当が必要。
4. 並行実行(Coffee H-speed、Phase 1-A)とrate limit/APIキー使用の競合の有無、STOP通知(`docs/pm/delegation_log/*STOP_NOTICE*`、`<run>/STOP`)の確認。
5. Production採用は本Trialと別判断。Trial結果は`APPROVED_FOR_PRODUCTION`ではない。

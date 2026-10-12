# PHASE_D_REPORT_01 (委任_03、2026-10-12) 結果: M1再確認でMUST-1未達(5/6)のためSTOP。Phase D本体は未実行

## 1. M1〜M5 実施(Trialコードのみ、Production無変更)
- M1: ITEM_CAP/RESERVED_SLOT_CAP 5->3(extractor.py/pipeline.py)。抽出schemaに `transparency`(opaque/semi/transparent)追加、Pythonでtransparentを除外。Prompt v2(`prompts/extractor_prompt_v2.txt`)に「通常は0〜2件、該当なしなら0件」「枠が3件あることは3件出す理由にならない」を追加。confidenceは閾値に不使用。
- M2: LLM候補の表示typeを `phrase` へ(候補 unit_type=phrase、`trial_display_type` も llm_noncompositional は phrase)。guidanceの「優先せよ」系の語なし(区分名/ラベル名の言及のみ。testで固定)。
- M3: 包含重複除外(既存の複数語候補を連続部分に含み、差分が閉クラス語のみ。例 `show up in` vs `show up`。既存が1語の場合は対象外)。schemaに `core_span` 追加、Pythonで「spanの連続部分・2語以上・spanより短い」を検証した場合のみ core_span を候補化(決定論、LLMが出した語の範囲内)。
- M4: Adv guidance(`select.py` LEVEL_LINE["adv"])の句動詞一律既知扱いを、「句動詞でも本文中で基本義と異なる意味(抽象的な主語や数値が主語など)で使われ、構成語から意味を推測しにくいものは非字義的表現として同列に評価」へ変更(構成語どおりの基本的な句動詞は既知扱いのまま)。
- M5: `phase_d/FROZEN_PLAN_01.md/json`(受入基準の数値・判定単位[MUST-3はitem単位/run単位を分けて報告]、variant定義V0/V1+d/V2/V3、Prompt/コード/入力記事のsha256、正解表[`GOLD_TABLE_02.md`])を **2026-10-12T21:06:53+0900** に凍結。ランナーは凍結shaと現ファイルが一致しないと起動しない。自作6記事(D2/D3/D4/D5/D6/N1、各約290語)は `phase_d/inputs/`。
- 抽出段のPython基本形化・`one's`統一は行っていない(委任どおり)。`one's own hidden clock`型は別論点として下記に記録。
- test: 既存36件+新規11件=47件PASS(`phase_d/test_results_01.txt`、API・ネットワーク呼出なし)。

## 2. 凍結証跡
- frozen_at = 2026-10-12T21:06:53+0900。全有料call(M1の6件)の `started_at` = 2026-10-12T21:07:00+0900(`phase_d/cost.json`)。凍結が全有料callより前であることを確認。

## 3. M1: Coffee再確認(extractor v2、C1のみ各Level n=3、JPY1.2792)
| Level | run | 抽出accepted | pump-fist抽出 | V2 shortlist |
|---|---|---|---|---|
| Std | 1 | pumps its fist / in the ring | ○(core_span縮約: `your wallet pumps its fist`->`pumps its fist`) | ○ |
| Std | 2 | pumps its fist / its own hidden clock | ○(縮約) | ○ |
| Std | 3 | pumps its fist / in the ring | ○(縮約) | ○ |
| Adv | 1 | unseen clock of its own / in the ring | **×(LLMがrawに出さず。reject/duplicate/transparent除外ではない)** | **×** |
| Adv | 2 | pumps its fist / in the ring | ○(縮約) | ○ |
| Adv | 3 | pumps its fist / in the ring / flash to a new price | ○(縮約) | ○ |
- **MUST-1(6/6)= 5/6 で未達**。事前凍結どおり、Phase D本体は開始せずSTOP。未達の原因は(b1)LLMが「通常0〜2件」の圧力下で`wallet pumps its fist`相当を2件枠(`unseen clock of its own`/`two figures in the ring`)の外へ出さなかったこと(自己申告transparent除外・core_span・包含重複が原因ではない)。v1(cap5・件数圧なし)は6/6。
- 良い点: core_span縮約により主語込みスパン(`your wallet pumps its fist`)は 全てPython側で`pumps its fist`へ縮約された(Std 3/3、Adv 2/2)。LLM自己申告は全件`semi`(transparent 0件、opaque 0件)で、transparency欄は除外にほぼ機能しない(自己申告の弁別力が低い)。抽出件数は2〜3(平均2.17)で、v1の5件固定偏りは解消。
- 再実行(同一条件の追加n)や閾値の事後変更は委任外のため行っていない。

## 4. 費用
- Phase C累計 14.4411 + 本委任(M1) 1.2792 = 15.7203(本件専用上限50に対し残 34.2797。本委任の残予算35.56に対しM1消費1.2792、残 34.2808)。Phase Dの抽出・最終選定・V1+dは未実行(0円)。

## 5. 未解決論点・Fableへの判断依頼
1. MUST-1が5/6。選択肢: (a)Prompt v2の件数圧(「通常は0〜2件」)を緩和し、MUST-1を満たす形でv3を再凍結して再実行、(b)基準を事後変更せず「v2は枠制約でMUST-1を満たさない」と結論してREJECTED/再設計、(c)追加n(同一v2で再抽出)で偶発性を確認(基準は変えない)。凍結済みのため、再実行・再凍結はFable/ユーザー指示が必要。
2. transparency自己申告は全件`semi`で除外に効いていない。判別基準をPrompt側で再設計するか、(M1の意図どおり)主な効果はcap3と件数圧だけになる点を認める必要がある。
3. extractor LEVEL_DESC["adv"] には「基本的な句動詞・高頻度コロケーションは既知とみなす」の旧表現が残っている(M4は選定guidanceのみが指示範囲のため未変更)。抽出側も同様に修正するか要判断(抽出Promptを変えるため再凍結・再M1が必要)。
4. cap3では(a)placeholder候補が4件ある記事(D2)で1件は予約枠overflowになる設計(llm候補が先頭優先のため、llm 3件があるとplaceholderは全て押し出される)。予約枠の由来優先順位(llm先/placeholder先)は未指定で、現行はllm先。Phase Dで再確認が必要な論点。
5. `one's own hidden clock`(辞書外比喩の過剰一般化)はOPEN-310とは別論点として記録(Phase C C3 Std2で正規化INVALIDの原因)。
6. 発見事項(実装せず報告): 実行中に同一パスのSTOP確認で `STOP_ALL` の一時的な存在を疑う挙動が1回あったが(ドライ実行の空結果)、以降の確認では不在で再現せず、原因は未特定(ドライ実行の偽クライアント側の可能性)。有料runには影響なし。

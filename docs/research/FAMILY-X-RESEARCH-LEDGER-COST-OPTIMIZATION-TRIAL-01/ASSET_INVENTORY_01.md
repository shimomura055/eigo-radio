# ASSET_INVENTORY_01(委任_01報告 §3 抜粋)

> 本文は委任_01 sonnet-workerの最終報告(2026-10-17)を無改変で転記。Opusレビュー前。採用判断はユーザー(正本=TRIAL_PREP_REPORT_01.md)

# 3. 棚卸し(ASSET_INVENTORY_01相当)と5記事選定
## 3-1 Family X経路で保存済みResearch下書き(draft)を持つ記事
- 全て `er019_family_x_entertainment_production_runner_01.py` 経由(entry_point.json で確認)。er052 stage_r の6記事は stop_after=storyline_b3 で、Research・Ledger・B3が揃っている(ja_writerは無い)。
- Researcher・Verifier Promptは全runで同一(静的部分のhashが一致)。Researcher draftと既存Ledgerは、比較基準として再利用できる。

| 記事 | run | Fact数 | VERIFIED/AMBIG/REJECTED | B3採用 | Ledger検索 | 作成日・Ledger model | B3 model |
|---|---|---|---|---|---|---|---|
| Coffee | er019 coffee_prices/run_fxpw_01 | 17 | 13/4/0 | 4 | 14回 JPY25.13 | 10-16 gpt-6-luna | gpt-6.1-sol(JPY10.94) |
| Coffee | run_l3_01 | 19 | 18/1/0 | 5 | 14回 | 10-10 gpt-6-luna | sol系 |
| Meta(AI) | meta/run_sol61_01、family_x_b3_production_wiring_01/run_01 ほか(同draft・複製) | 15 | 15/0/0 | 3 | 7回 JPY14.27 | 09-26 gpt-5.6-luna(旧) | sol6.1(JPY6.96) |
| AI(Broadcom決算) | er052 stage_r/semiconductor_earnings | 6 | 5/1/0 | 5 | 3回 JPY5.58 | 10-08 gpt-6-luna | gpt-6-luna |
| AI(訴訟) | stage_r/openai_copyright | 8 | 8/0/0 | 5 | 5回 JPY9.01 | 10-08 | gpt-6-luna |
| 社会(訪日客統計) | stage_r/inbound_tourism | 15(B3可視13) | 11/2/2 | 4 | 16回 JPY28.26 | 10-08 | gpt-6-luna |
| 社会/制度(Fed) | stage_r/central_bank_mortgage | 11 | 11/0/0 | 6 | 4回 JPY7.38 | 10-08 | gpt-6-luna |
| 消費(Disney+) | stage_r/streaming_price | 7 | 5/2/0 | 6 | 7回 JPY12.78 | 10-08 | gpt-6-luna |
| 複数出来事 | stage_r/byd_recall | 11 | 11/0/0 | 5 | 3回 JPY5.55 | 10-08 | gpt-6-luna |
| 小物(ミニバッグ) | er052 gpt6_wiring_e2e_01/run_02 | 6 | 6/0/0 | 3 | 4回 | 10-08 | |

- 参照のみ(使わない):
  - Hormuz系(er019 diversity/refresh/an3): 保存は verified_fact_ledger.txt のみ。draft欠落。
  - Family A/B/C/他系(er003、er012 sewer、er017)の verification_full_record.json: 形式は同じ(同じ関数が出力)だが、Prompt・経路が別。改修・利用はしない。
  - open233 after_pprime: Meta複製。
- **重要な発見**: stage_r の6記事のB3は gpt-6-luna(JPY約0.5)で実行されている。現行Production(2026-10-11以降)のB3は gpt-6.1-sol(JPY約7〜11)。つまり、Coffee以外では既存B3を従来方式の基準に使えない。従来方式として gpt-6.1-sol のB3を新規に1回走らせる必要がある(§5に含めた)。
- もう一つ: 既存Ledgerは10-08〜10-16の時点のWebに対する結果。Trialでの再検証は本日のWebに対して行うので、情報更新やURLの別名の指す先が変わることによる差が、方式差に混ざる。この切り分けが§4-4の統制(同日・上限なしの再検証)である。

## 3-2 5記事選定(確定案)。新規Researchは不要、テーマ選定をユーザーに求める必要もなし
保存済みのテーマを比較素材として再利用するもので、新規記事の生成ではない(PM_GOVERNANCE 13節の対象外と判断。反対意見があればFableで判断)。

| # | タイプ | 記事 | 選定理由・検証難度の特徴 |
|---|---|---|---|
| 1 | 統計・価格 | Coffee fxpw_01 | 17 Fact、採用4(比率24%、案2が最も効く)。版違い(USDA 7月/12月)、季節調整ラベル誤り(F12)、曖昧4、因果(F05/F09)、時系列。基準B3(sol6.1)あり |
| 2 | AI・テクノロジー | openai_copyright | 8 Fact。訴状提出段階と判決の区別(断定禁止)、14原告、Reuters報道とコメント状況。全VERIFIED(易)。代替=semiconductor_earnings(6 Factで採用5、案2の効果が出にくい)、Meta(15 Fact、旧モデル) |
| 3 | 社会・制度 | inbound_tourism | 公的統計(JNTO・観光庁)。推計vs確定の版違い(F05/F06)、REJECTED 2(F05、F12)、AMBIGUOUS 2(F04、F06)。時系列比較(2019年比)。**自然にREJECTEDが出る唯一の記事で、案2の再選定loopが実際に動き得る**。F05(年間過去最多)は物語の中心になり得る |
| 4 | 生活・消費 | streaming_price | Disney+値上げ。適用時期の二段階(9/23新規、10/21既存)、「最新」「主要」の範囲が曖昧(F01 AMBIGUOUS)、理由が未確認(F07)。7 Factで採用6(比率86%)。案2の効果が小さい側の例外。streaming F04は9クエリ |
| 5 | 複数出来事・出典 | central_bank_mortgage | FOMC決定(9/16)、議事要旨・SEP(予測)、Freddie Mac金利、AP報道、セントルイス連銀解説の複数出来事・出典。因果(政策金利→住宅ローン金利)と予測/実績の区別。全VERIFIED(検証は易)。代替=byd_recall(二本の召回公告、全VERIFIED) |

- 難度の分散: 統計と版違い(1、3)、曖昧(1、3、4)、時系列(1、3、5)、因果(1、5)、断定禁止/段階(2、4)。REJECTEDを持つのは3のみ。
- 採用比率: 0.24、0.62、0.31、0.86、0.55。Fact数と採用比率が案2の削減幅に効くので、傾向と例外が出せる。
- 検証難度の偏り: 5記事のうち全VERIFIEDが2(openai、central)あり、重大Factの見逃しを検出する力は弱い。見逃し検出はinbound・Coffeeに依存する(受入条件7の限界として明記)。

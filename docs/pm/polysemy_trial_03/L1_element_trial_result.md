# L1 要素Trial結果(OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-03 / L1r)
性質: DEV要素Trial(Production非接続)。評価のみ(Sonnet)。パターン最終判断はFable。実費合計 **¥75.42 / 上限¥80**(`er052_output/open233_polysemy_trial_03/runs/cost_l1.json`)。
入力: 5台帳(core)+holdout2(A02, small_bag)。web_search=none、各call上限¥5。台帳は既存notes_for_writer付きのまま入力(ablationのみ除去)。

## 1. ハーネス整合
- gen_notes_p03.py: pattern.json(mode/max_chars=100/fallback)を読む。A=全fact`judgments`→pass_ruleをコード側評価(reversible && flipped!=none && contradicts!=none && changes_conclusion && ledger_quoteがclaim/scope/conditionsに空白正規化で部分一致)。全fact判定は`judgments_all.json`に保存。B=stage1通過(reversible && quote一致)→stage2、`self_check`両true以外は却下。C=notes_for_writer非空factのみ`promotions`、`source_prohibition`がnotes内に逐語で無ければ却下、notes無しfactはAをfallback(追加call)。
- 付与前に接頭辞`注意(逆転): `・{MAX_CHARS}=100字・改行なしを検証。items入力へscope/conditions/date_or_periodを追加(旧版はclaimのみで台帳引用規則が成立しないため)。`--no-existing-notes`追加。runnerへholdout slug対応・`--run-tag`追加。json_object+parse失敗時のみ1回再試行(発生0)。
- test: 12 PASS。prompt衛生: PASS。holdout: A02(既存draft/verif)+small_bag(`er019_output/family_x_b3_diversity_trial_01/small_bag/run_01/...`。指定のrun_03は無く代替。英語台帳)。
- 注意: 評価基準・ラベル表は`eval/l1_labels.py`(評価専用)。promptへの対象fact_id混入なし。

## 2. 比較表(core5台帳。()はholdout)
| 指標 | A_onepass | B_twostage | C_promote |
|---|---|---|---|
| 対象捕捉(正解14) | 8/14 | 6/14(接頭辞空白却下を寛容救済すると9/14) | 9/14 |
| うち内容一致(一致/部分/不一致) | 4/2/2 | 2/2/2 | 6/1/2 |
| 対象外付与(付与率) | 27(41%=35/85) | 13(22%=19/85) | 28(44%=37/85) |
| 対象外の型 妥当/変質止まり/誤り(hedge・範囲+Rが不自然) | 11/8/8 | 9/2/2 | 3/8/17 |
| 台帳に無い事実の混入 | 0 | 0 | 5(F-003 恒久・F-004/F-005 試験・F-013 別fact混入疑い・HF-002焦点ずれ) |
| 曖昧語流用(改める/見直す等) | 0 | 0 | 0 |
| 字数 平均/最大 | 50.8/62 | 72.9/91 | 61.7/79 |
| ledger_quote一致 | reversible=true 35件中35 | 37件中37 | 該当なし(source_prohibition逐語一致で代替、1件不一致却下) |
| 迎合(台帳別件数) | 3/8/16/5/3 変動あり | 3/11/0/5/0 | 2/8/13/5/9 変動あり。警告なし |
| holdout 付与(A02/small_bag) | 9/19・10/17 | 10/19・0/17 | 13/19・1/17 |
| holdout 参考対象(A02 POL-01/06) | 2/2 | 2/2 | 2/2 |
| 実費(core5/全体) | ¥14.0/¥20.2 | ¥22.5/¥27.9 | ¥10.2/¥15.0 |
- 期待(small_bag 0〜1件): Aは10件で**NG**、B 0件・C 1件はOK。台帳全体が対象外の記事でもAは拾いすぎる。
- 全パターンとも「対象外付与」が多い(特にA/C)。付与率41〜44%は「重要なFactだけ」に届かない。

## 3. ablation(Aから既存notes_for_writerを除去、5台帳、¥12.34)
- 捕捉 8/14 → 6/14。付与 35 → 23。meta 2/2→0/2、hormuz 1/2→0/2(捕捉減)、sewer 2/3→3/3(付与5→13と増加)。
- 判定は既存notesに強く依存している。sewerのみ付与が急増しており、既存notesを外すと基準が不安定になる。
- Cはpromote型で既存notesが入力そのものなので、ablation対象外(ハーネスで拒否)。最良候補(捕捉最多)はCだが上記理由でA(次点)に実施。内容ラベルはablation分は未実施(件数のみ)。

## 4. FN(対象の見落とし)理由
- A(6件): 全て`reversible=false/flipped=none`(LLM判定が「成分を1つ反転できない」。HF-009, F-001, F-016, EVID-004/006, CONTROL-001)。
- B(8件): stage2 `self_check`でR_is_natural_reading=false(ai_control EVID-004/006含む10件却下)、接頭辞空白欠落(`注意(逆転):`後の半角空白なし)でbad_prefix却下(space_weapons 8件、うち対象3件F-002/F-007/F-009)、F-001/F-016/CONTROL-001はstage1でreversible=false。
- C(5件): 既存notesが禁止文でなく`note_null`(HC-014, F-001, F-007, EVID-004, CONTROL-001)。既存notesに無い誤読は拾えない設計。
- 共通: F-001(初回発言→配備と読む)、EVID-004、CONTROL-001は3パターンとも未捕捉。

## 5. パターン別所見
- A: 件数上限なしの全fact判定。内容は台帳準拠(台帳外混入0、R妥当型11)。しかし「Rが不自然」(地上試験を軌道配備と読む等)と変質止まり計16件で拾いすぎ。small_bag holdoutで10件(期待0〜1)NG。ablationで既存notes依存が高い。
- B: 精度は最良(付与率22%、妥当型9/13)で迷う例も残す。ただしstage1が再現率重視でも基準が緩く、stage2が自己検証で10件を全落し(ai_control)、接頭辞の空白だけで8件が落ちる(形式却下が捕捉率を下げた)。字数が長い(最大91)、費用最大。
- C: 既存notes昇格で捕捉最多(9/14、内容一致Y6)。ただし既存notesが誤読警告以外(過剰一般化・範囲限定)を含むため、誤り型17件・台帳外混入5件・別fact向け禁止文の取り違えが出る。small_bagは1件でholdout良好。
- 推奨(最終判断はFable): 単独採用は不可。**BのstageをCのように既存notesで補助しつつ、接頭辞検証は空白を正規化してから比較**する構成(B+寛容接頭辞)が最も精度と再現率のバランスが良い見込み。ただし本結果は1実行ずつのn=1で、特定5テーマ向けの目視ラベルであり、過学習の有無はholdout2のみ。

## 6. 逐語一覧・ラベル(全件)
- 付与note全件(theme・fact_id・逐語・ラベル・FN理由)は各sheetに記載(本ファイル90行制約のため分離)。
  - `er052_output/open233_polysemy_trial_03/eval/A_onepass_content_label_sheet.md`
  - `er052_output/open233_polysemy_trial_03/eval/B_twostage_content_label_sheet.md`
  - `er052_output/open233_polysemy_trial_03/eval/C_promote_content_label_sheet.md`
- 集計表: `eval/l1_summary.md`(捕捉率/付与率/ledger_quote)、`eval/l1_label_summary.json`、ablation=`eval/ablation/ablation_table.md`。
- 生run: `er052_output/open233_polysemy_trial_03/runs/<pattern>/<theme>/`(stage*_raw.json、judgments_all.json、notes.json、rejected.json、provenance.json)、`runs/ablation/`。

## 7. 限界(Fable判断用)
- ラベルは当該claim/scope/conditions(先頭150字表示)に基づくSonnet判断で、人手確認前。「台帳外混入」は表示範囲外の文言を見落とす可能性がある。
- 既知誤読14件は5テーマ固有。内容一致の数値は小さいnで有意差とは言えない。holdoutの正解は参考のみ。
- 新規仕様案(B+寛容接頭辞)は提案のみ。Production実装なし。

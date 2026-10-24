# TRIAL_DESIGN_07: 課題① X2p'(範囲の規則+定訳優先)補強検証の設計確定(OPUS_REVIEW_08 OF-KP2-01〜03/07反映、委任_30、2026-10-24)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_30 / 前版=`TRIAL_DESIGN_06.md`(arm構成・X2p差分は§9) / 根拠=`OPUS_REVIEW_08.md`(逐語) / harness=`er112_kp_gm_trial_06.py`(DEV専用、**本委任は実行しない=API 0**) / test=`er112_kp_gm_trial_06_test_01.py`
状態: **有料runの前に確定(判定基準は出力を見る前に固定=事前宣言)**。有料runは**案件累計が7-7の300円を超えるためユーザーの費用承認後=次委任**(`BUDGET_PLAN_T6_01.md`、UDR #178)。Production module(`er003_*`/`er019_*`/`er026_*`/`er105_*`)は編集せずimportのみ。

## 0. 使用モデル(25節、最新モデル原則)
生成=`gpt-6-luna`、reasoning effort=**high固定**(Production系列と同一)。最新世代の最上位系ではない。例外理由=評価対象がProduction系列のluna生成の品質そのもの(Trial_04/05と同一条件、armの差だけを見る)。判定=Fable盲検+第二評価者(Opus/新contextのFable、API 0)。Sonnet参考Judgeは使わない。

## 1. X2p' の差分(**修正は1回のみ**。再度の文言調整はしない=不合格ならCp最適化版へ)
X2p(`er112_kp_gm_trial_05.X2P_MEANING`)に対する差分は次の2点のみ(他は一字も変えない。実装=`er112_kp_gm_trial_06.py` の `X2PP_SCOPE`・`X2PP_MEANING`)。

### 1-1. 範囲の規則を新設(`X2PP_SCOPE`。`X_NEWGEN`の直後・`X2PP_MEANING`の直前に挿入)
```
【範囲の規則(meaning_in_text_enとjapanese_glossの両方に適用)】
- 本文で使われている語義・用法(字義どおりか、比喩・慣用か)を選んでください。ただし、japanese_glossが表すのはkey_phraseの範囲だけです。
  key_phraseに含まれていない、本文側の否定・主語・時制・具体的な対象・場面は、japanese_glossに持ち込まないでください
  (例: 本文が「the plan did not work out」でkey_phraseが「work out」なら、japanese_glossは「うまくいかなかった」ではなく「うまくいく」)。
```
### 1-2. `japanese_gloss` のpartly/no分岐に『定訳優先』を追加(`X2PP_MEANING`)
X2pの「partly/noなら、naive_jaの字義の像を使わず、meaning_in_textの意味【全体】を…言い換えで表す」を次に置換:
```
partly/noのときは、まず、このkey_phraseのこの語義に日本語の定訳(英和辞典の見出し訳や日本語として定着した言い方。例: cut cornersなら「手を抜く」、break evenなら「収支がとんとんになる」)があればそれを優先し、
無い場合だけ、naive_jaの字義の像を使わず、meaning_in_textの意味【全体】を日本語の慣用表現か平易な短い言い換えで表す(意味の一部だけを取り出した語にしない)。
```
- **例示KPの選び方(逸脱の開示)**: 委任文・OPUS_REVIEW_08の例は `サプライチェーン`・`つじつまが合う` だが、これは Stage 2 の評価KP(`supply chain`・`add up`)そのもの。Promptに入れると**評価KPへの過適合(teaching to the test)**になり、Stage 2再検証が無効になる。そこで評価集合(S2/R/held-out/新hard-core)に**含まれない**KP(`work out`・`cut corners`・`break even`)を例示にした(test `test_examples_not_leaked_from_evaluation_sets`で担保)。
- 変えないもの: `X_HEAD`・`X_NEWGEN`・`X_OUTRULES`・`naive_ja_conveys`の定義・動作主/動詞の意味を変えない規則(X2pで追加済み)・長さ/説明文化禁止・出力schema(X2pと同一の3欄+Production必須欄)。
- 期待する効果(反証可能な予測): (a) 通常KPの持ち込み(`add up`→「つじつまが合わない」、`move in the other direction`→「売れ行きは逆に下がった」型)が減る。(b) `naive_ja_conveys` が構造的にほぼ `no` になる偏り(yes 7/partly 8/no 39)のもとでも、定訳があるKPは定訳に着地する(`supply chain`→サプライチェーン型)。(c) hard-core 4KPのFAIL系0は維持される。**反証条件**: R 12出力でFAIL系が1以上、またはStage 2で持ち込み系THINが増える。

### 1-3. Trial_05 X2p との構成差(本番構成化。いずれも『本番に近づける』差であり効果の原因は分離される)
| 項目 | Trial_05 X2p | 本harness X2pp | 理由 |
|---|---|---|---|
| gloss規則 | `rules`(非fulltext) | **`rules_fulltext`**(全文選定itemが使う規則。数値placeholder回避段落を含む) | OPUS_REVIEW_08 論点4: 配線後ではなく事前に測る |
| `prior`(前回却下理由) | 省略 | **`previous_attempt_rejected`を再提示**(retry時。ga.build_user_message_correctedと同一形式) | 同上。test `test_prior_block_matches_production_item_form` |
| call構成 | 1 callに最大3KP(平均1.9) | **1 level(同一run)の全KPを1 call**(本番のalign対象) | 論点1-4 |
| gate | 単発(retryなし) | ga.run_alignment_gate_correctedと同一構造のDEVコピー(item単位retry・上限2) | retry/fallback機構と整合 |
| developer message | `M_DEVELOPER` | `M_DEVELOPER`(不変。新経路の候補=WIRING_DESIGN_07) | B0pとの差に含まれる(§3の限界) |
- 宣言した差分だけを戻すと Trial_05 `build_x_message("X2p")` と**1文字も違わない**(人称あり/なしKPで確認、test `test_golden_x2pp_builder_matches_trial05_x2p_except_declared_diffs`)。

## 2. arm・集合・実行単位(OF-KP2-01/02/03/07)
| 補強 | 集合 | arm | rep | 構成 | 費用見積(円。`BUDGET_PLAN_T6_01.md`) |
|---|---|---|---|---|---|
| **(b)** 新hard-core | `HARDCORE_HELDOUT_02.md` の9KP | B0p / X2pp | **各2** | siblingなし(Trial_05と同形)+rules_fulltext+prior | B0p 0.93 / X2pp 2.13 |
| **(b')** 退行確認 | R 7KP(hard-core 4+co-KP 3) | X2pp | 1 | 同上 | 0.75 |
| **(c)(e)** 本番構成 | Stage 2 54KP(Trial_05と同一集合) | B0p / X2pp | **各1** | **1 level全KPを1 call**(sibling含む、1 call 3〜8KP[`--max-level 5`で5以下]) | B0p 2.0 / X2pp 14.3〜15.2 |
- (b')は委任文に無い**追加**(Prompt変更の退行確認。hard-core 4KPの字義訳が戻らないことは最重要で、約0.75円)。不要ならFableが外してよい。
- **(c)の費用が Opus見積(約11円)より大きい理由**: 本番構成は1 callに同levelのsibling KP(評価しない)を含み、評価54KPに対し生成対象が151〜161KPになる(出力tokenはKP数比例)。sibling無し(評価KPのみ、本番構成ではない)だと X2pp 5.7円。**判断はFable**: ①本番構成の忠実性(OPUS要求)を優先して full-level、②コスト優先で `--max-level 5`、③評価KPのみ(5.7円、論点1-4の『5件同時』は検証できない)。
- 実行手順(次委任): `prodhash --tag start` → `gen --set HC --siblings off --reps 1,2 --cap <>` → `gen --set R --siblings off --arm X2pp --cap <>` → `gen --set S2 --siblings on --max-level 5 --reps 1 --cap <>` → `prodhash --tag end`(一致確認)。再起動は委任文が許可した回数のみ。

## 3. 事前宣言の判定基準(出力を見る前に固定)
ラベル=PASS/THIN/FAIL/FAIL_LIT。**THINには『範囲を超えた持ち込み』を含める**(`fable_blind_06.md`の基準)。評価者=Fable盲検+第二評価者(二重判定、§4)。**二人のラベルが分かれたら厳しい方を採用**。
1. **(b) 新hard-core(9KP×2rep=18出力/arm)**: 次を**全て**満たす: (1) X2pp のFAIL系(FAIL+FAIL_LIT)≦B0p のFAIL系、(2) **B0pがPASSでX2ppがTHIN以下に悪化したKP-repが0**(近重複 `story with two different speeds` を除いた8KP×2rep=16出力でも同様)、(3) X2ppのTHIN数≦B0pのTHIN数+1、(4) record-only持ち込み検出がB0pより増えない。
2. **(b') R退行確認(7KP×1rep)**: X2ppのFAIL系=0 かつ THIN≦2(`TRIAL_DESIGN_06.md` §4-追記の改訂gating基準と同一)。
3. **(c) Stage 2本番構成(54KP×1rep)**: 比較基準=B0の良い方rep(Trial_04のB0 2rep+B0p 1rep=計3rep中の最良)。次を**全て**満たす: (1) PASS→FAIL系=0、(2) **PASS→THIN≦2/54(第二評価者を含む厳しい側のラベルで数える)**、(3) 本番構成でも `validate` 互換と全itemのADOPT(HR=0)、(4) 参考: 持ち込み検出(`detect_import`)の件数がX2p(Trial_05 Stage 2: 3件)以下。
4. **(e) 実測(判定ではなく採用資料)**: level単位の費用・出力token・reasoning token・wall-clock(`results.jsonl`の`level_*`)、call内KP数別。監視指標(align費用0.6円/記事セット・level 60秒)の再設定の基礎。
5. **総合**: 1〜3を全て満たす → 『VALIDATED候補(補強検証PASS)』としてFableがユーザーへ採否提示(`ADOPTION_PROPOSAL_02.md`を実測で更新)。**1つでも満たさない → 修正は1回のみの規則に従い規則の再調整はしない**。次案=Cp最適化版(OPUS_REVIEW_08 論点2)または現行維持(選択肢2)をFableが判断。

## 4. 二重判定(OF-KP2-03)
- 盲検表=`TRIAL_05/fable_blind_06.md`(**API 0・本委任で作成済み**): Stage 2で文字列が変わった35KP+R 7KP+held-out 9KPの51行・128文字列(うちX2p文字列を含むもの61)を、arm伏せ・明示基準つきで提示。key=`fable_blind_06_key.json`(既存Fableラベル含む。判定後にのみ開く)。第二評価者=Opus(別context)または新しいcontextのFable。
- 再照合対象を明示: `add up`(「つじつまが合わない」の否定の持ち込み疑い)、`reach for someone's wallet`(過去のユーザー判断『見出し語忠実でPASS』との整合)。
- 集計=`py er112_kp_gm_trial_06_blind.py agree --labels <json>`(厳密一致率、PASS/非PASS一致率、第二評価者が厳しい/緩い件数、変化した35KPでの Stage 2 PASS→THIN 再計算)。**有料runで生成した新しい文字列(X2pp・B0p)も同方式の追加盲検表で二重判定**する(次委任)。
- 補強検証(b)(c)の新規出力は、有料run後に追加盲検表を作成(同script形式)。
- 一次評価(Fable)と第二評価者の一致率が低い(厳密一致<70%)場合は、『判定基準が曖昧で事前宣言基準の解釈が割れる』ことを報告に明記し、厳しい側を採用する。

## 5. 撤去・残置
撤去する規則・検査・testは無い(新規DEV追加のみ)。残置: Production現行Prompt/schema(B0p=Productionそのもの)、Trial_05の`X2P_MEANING`/`build_x_message`(再利用・golden基準)。

## 6. 安全装置
- `gen` は `--cap` 既定0=dry-run(API client生成0、test `test_default_off_isolation_no_api_no_files`)。STOP/STOP_ALL・`er026_output/.../STOP_ALL`・`docs/.../STOP`・Trial_04/05のSTOPを尊重。cap超過見込み・1 job見積の2倍超でHALT(再起動で回避しない)。
- Production moduleは未編集(`prodhash`のstart/endとgit diff HEADで確認、test `test_production_modules_unchanged_vs_head`)。

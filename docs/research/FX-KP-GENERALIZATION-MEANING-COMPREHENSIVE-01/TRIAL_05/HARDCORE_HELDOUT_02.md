# HARDCORE_HELDOUT_02: 設計に使っていない新hard-core KP集合の事前固定(委任_30、OPUS_REVIEW_08 OF-KP2-01(b)、2026-10-24)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_30 / API 0 / **gloss出力は一切見ていない**(選定は見出し語・本文・canonicalization reasoningの有無だけ) / 選定script=`er112_output/kp_gm_trial_06/hardcore_select_06.py`(再現可能・乱数なし) / 出力=`er112_output/kp_gm_trial_06/hardcore_set_06.json`(KP詳細)・`hardcore_select_log_06.json`(基準・除外理由)。

## 1. 目的と位置づけ
X2pの規則はR hard-core 4KP(`draw a line`/`an unseen clock`/`question shaped like a trophy`/`greener grass`)の結果を見て足された(設計に使ったデータ)。OPUS_REVIEW_08 OF-KP2-01は、**設計に使っていない新しいhard-core型KPでB0とX2p'を比較する**ことを求めた。本書はその集合を**有料runの前に・結果非依存の基準で固定**する(事前宣言)。

## 2. 選定基準(出力を見る前に固定)
合計9KP = [H] held-out未使用 4件 + [Z] Z小説由来 5件。
- **[H]** Trial_05 held-out選定順(`heldout_selection_log_05.json` の `selected` 14件)のうち、`--nheld 10` で評価に使わなかった**末尾4件**(選定順で機械的に決まる)。選定基準はTrial_05のとおり(canonicalization reasoningが比喩|慣用|イディオム|熟語|figurative|idiomを述べる、seed=22)。
- **[Z]** Z小説(family=Z)の過去Production run由来KP(`er112_kp_gm_kpset_03.candidates` と同じ走査・除外規則、57KP)から、次を**全て**満たすもの。
  - (z1) `all_kps()`の115KP・`PRE_A1_DROP`・R hard-core 4KP・held-out選定14KPのいずれでもない。
  - (z2) key_phraseが上記使用済みKPを語として含まない/含まれない(`rise above everyone's voices` は `rise above` を含むので除外。4件除外)。
  - (z3) 3語以上(33件除外)。
  - (z4) key_phraseに、**字義でも文法が成立する具体物・身体・自然語**の合図語(`CUE`: leg(s)/eye(s)/face/voice(s)/tear(s)/hand(s)/heart/light/rain/water/stick/door/window/clock/wall/fire/wind/shadow/road/river/bridge/knife。script内に固定)を含む。hard-core型(字義読みが文法的に成立し、直訳では意味が運ばれない)の**構造的な代理指標**で、意味の良否や本番gloss出力は参照しない(15件除外)。
  - 選定=key名ソート順、上限6件(該当は5件のため全件)。
- 限界(開示): (i) `CUE`はZ候補57KPの**見出し語一覧を見た後**にscriptへ固定した(gloss出力は見ていない)。(ii) Z小説にhard-core型の新造比喩は元々少なく(Trial_05 held-outの母集団でもZは2件)、[Z]の5件は『身体・自然語を含む描写的表現』が中心で、厳密な新造比喩(`an unseen clock`型)は含まれない可能性が高い。**字義訳が正解になる用法(`sheltered from the rain`は字義のまま正しい)も含む=過剰解釈(文脈の持ち込み)を検出する対照にもなる**。(iii) [H]の `story with two different speeds` は使用済みKP `two different speeds`(Trial_05 held-out評価済み)を語として含む近重複。基準(z2)は[Z]のみに適用したため残しているが、集計では**単独件数(9件)と、近重複を除いた8件の両方**を示す。

## 3. 固定したKP集合(9件)
| # | 区分 | key_phrase | 本文の文 | 由来run |
|---|---|---|---|---|
| 1 | H | feel borrowed | Now the office can feel borrowed. | editorial_b_family_production_phase1_01/b1b |
| 2 | H | feel like friction | So a rule that looks flexible on paper may feel like friction to one person, ... | 同上 |
| 3 | H | jump into action | The marketing team may be ready to jump into action, but wait | ig_nobel_2026__run_nws_02/a2 |
| 4 | H | story with two different speeds | As of September 2026, travel surveys in Japan tell a story with two different speeds. | open112_trend_theme2_b_full_audio_trial_13/b1b |
| 5 | Z | keep one's eyes on them | The ruler kept his eyes on them | melos/run_kpgm20_02 |
| 6 | Z | legs fail someone | His legs suddenly failed him. | melos/run_e2e_01 |
| 7 | Z | one's face harden | The ruler's face became hard. “Then you will die.” | er035 kp_4plus1_evidence_02/melos_a2 |
| 8 | Z | sheltered from the rain | Bob stood in the doorway of a closed hardware store, sheltered from the rain | after_twenty_years/run_sf_prod_01 |
| 9 | Z | smile through one's tears | She pressed them to her chest and smiled through her tears | the_gift_of_the_magi/run_sf_prod_01 |

## 4. 汚染の確認(開示)
- Trial_05の誤実行(`--set H` を `--nheld 10` なしで実行、BUDGET_LOG_01 委任_23追記)で、[H]の4KP(`feel borrowed`/`feel like friction`/`jump into action`/`story with two different speeds`)に**Cp armのgloss出力が各1件存在する**(`er112_output/kp_gm_trial_05/results.jsonl`)。これらは**ラベル付けも閲覧もされておらず**(盲検・集計はオリジナル10KPのみ)、Cpは本補強検証のarmではなく、本委任でも開いていない。B0/X2p'は新規に生成する。
- 設計(X2p/X2p'の規則)に使ったKPは、R 4KP(+co-KP 3)のみ。本集合はそのいずれでもなく、X2p'の例示(`work out`/`cut corners`/`break even`)も評価集合(S2/R/held-out/本集合)に含まれない(`er112_kp_gm_trial_06_test_01.py::test_examples_not_leaked_from_evaluation_sets`)。

## 5. 実行計画・判定基準(事前宣言。有料runは次委任・ユーザー予算承認後)
- arm = **B0p**(現行Productionをそのまま呼ぶ) と **X2pp**(X2p')、各**2rep以上**。B0は失敗で選んだ集合ではないので、Trial_05の既存B0を流用せず**新規に取り直す**(OPUS_REVIEW_08 補強案(b))。1 call = 1 level内の本集合KP(siblingなし=Trial_05と同じ形。本番構成の確認は補強検証(c))。費用見積=`BUDGET_PLAN_T6_01.md`。
- ラベル: Fable盲検(`er112_kp_gm_trial_06_blind.py` 同形式で作る追加盲検表)+二重判定(第二評価者)。
- **有効の基準(出力を見る前に固定)**: (1) X2p'のFAIL系(FAIL+FAIL_LIT)がB0のFAIL系以下、(2) **B0=PASSからX2p'=THIN以下への悪化が0**(9KP×2rep=18出力中)、(3) X2p'のTHIN(持ち込み含む)が B0のTHIN+1以下、(4) 持ち込み検出(record-only `detect_import`)が新規に増えない。(2)(3)を満たさなければ『新規KPで改善を再現できない/悪化する』と報告し、Cp最適化版(OPUS_REVIEW_08 論点2の次案)を検討する。
- **効果の検出力の限界(開示)**: 本集合にはB0がFAIL_LITになる新造比喩がほとんど無い見込みで、『効果の再現』は検出しにくい。主眼は**悪化(過剰解釈・持ち込み)の検出**と、字義訳が出た場合の再現。

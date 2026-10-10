# RESULT_01(B3-FACT-INSTRUCTION-SEPARATION-ROOTFIX-TRIAL-02 最終報告、Phase 2a+2b、2026-10-10)
Status提案: **D-det v2=`VALIDATED`(Trial限定)。ただしProduction採用は`USER_DECISION_REQUIRED`(人間ユーザーのみ)**。D-plus-single-call=`REJECTED`、Separate-call(Luna)=`REJECTED`(Sol未実施)、役割宣言のみ=`VALIDATED`(Trial限定・no-harm。採用はPrompt変更を伴うためユーザー判断)。いずれも`APPROVED_FOR_PRODUCTION`ではない。Production code・Production Prompt・CURRENT_SPECは変更していない。
**ただしv2は結果を見てから作った修正(post-hoc)であり、central_bankに対する成績は「独立予測」ではない。** 他8テーマで差がないことと、E9(記事への影響)が「副作用の確認」にあたる。
使用モデル(25節): B3系・Separate-call・R0(E9)=`gpt-6-luna`(effort=high。gpt-6世代の最新だが最上位系かは未確認。例外理由=Production B3/R0と同一条件での比較が目的)。Solは未使用。D-det v2自体はLLMを使わない(call 0)。
実費: Phase 2a JPY31.68 + Phase 2b(E9 R0 6 call)JPY2.62 = **JPY34.30**(cap: 2a本線JPY60内、E9はJPY20内)。技術retry 0。台帳 `cost_ledger_b3r2_01.jsonl`。

## ユーザー指定6点(Phase 2b)
1. **central_bank誤判定は解消したか**: **解消した**。Storylineの主役数値「25ベーシスポイント」とFact本文の「0.25パーセントポイント」が同じ数値として扱われ、両方が中核になった(v1では両方が周辺で、代わりに「12対0」「30年」が中核の主役扱いだった)。原因だった「25ベーシスポイント=0.25パーセントポイント」の単位換算を、決定論の換算表で入れた。副作用として、中核の枠(6件)に25bpが入った分、7.40%が押し出されて周辺になった(5.98%は中核のまま。規則どおりの結果だが、利率の比較の片方だけが中核という見え方になる。HUMAN_CHECK参照)。
2. **他テーマへの副作用**: **0**。central_bank以外の8テーマは、各数値の紐付け・中核/周辺・適格・上限枠・押し出しが、v1とv2で完全に同一(`eval_v2/diff_v1_v2_03.md`)。central_bank内の差分は3表記(0.25パーセントポイント、25ベーシスポイント、7.40%)だけで、全件説明済み。
3. **中核・周辺ランクの精度**: 既存の注記(C0のMERGED注記)との参考比較(**既知値の比較で独立予測ではない**)。全9テーマ: 一致 42/49(0.857)→42/48(0.875)、GT中核の再現 22/25(0.88)→22/24(0.917)、適合率 0.815→0.815。central_bank以外の8テーマは変化なし(一致0.889/再現0.947/適合0.818)。既存の注記検査(`b3_annotation_check_01.py`無改変)は9/9テーマで、`annotator`欄の値(`DETERMINISTIC`)の指摘以外は0件。中核の取りこぼし・分類漏れ・印の不一致は0。
4. **再現性**: 同一入力で3回実行し、全表記・role・適格が完全一致(決定論)。
5. **Writer R0への影響(E9、6テーマ=問題5+byd_recall、各1回)**: 制約行への【事実N】付与0、制約文の記事転記0、台帳ID・台帳内部語の漏出0、音声化禁止記号Gate該当0、印そのものの漏出0、タグ整合PASS 6/6。数値印の効果: 対照(ROOTFIX-01のE9。印なし)は6テーマ×2腕の12記事すべてで記事に数値がほぼ出ない(中核候補の使用0)のに対し、印ありでは中核数値が記事に出る(semiconductor 3/5、space_weapons 1/3、hormuz 5/5、central_bank 3/7、byd 1/3、small_bag 0/2=日付のみ)。central_bankでは「0.25パーセントポイント」が中核として記事に書かれた。気になる点2件(Writer R0の遵守度の問題で、v2の誤りではない): (a) hormuzで周辺数値「85ドル」「1バレル」を記事に書いた(1記事。「周辺数値は書かない」規則への違反、内容は台帳どおりの事実)。(b) central_bankで「3.75～4.00％」を「3.75％から4.00％」に書き換えた(表記のままという規則の軽微な逸脱、中身は正しい)。R0冒頭復唱検出が1件(central_bank、「これ、ちょっと面白くない？」、OPEN-175既知の傾向、対照12記事は0)。R0全文を6本通読し、事実誤りなし、制約が事実扱いされた箇所なし。
6. **D-det v2のProduction採用推奨(採用判断はしない)**: **採用を推奨する(Claude側の意見)**。理由=費用0・追加call 0、再現性100%、既存注記検査にほぼそのまま通る、LLM方式(D-plus)より安く速く壊れにくい、E9で記事への悪影響なし。ただし採用にはユーザー判断が要る事項がある(下記)。

## 残るユーザー判断
- U3: 「同一callでの構造化が第一候補」というユーザー確定に対し、決定論方式(D-det v2)へ切り替えるか(同一call方式は費用・速度・STOPの面で不合格だったため、判断材料として決定論を推奨)。U2(number_ranks不整合の扱い)はLLM腕を採らないため該当なし。
- v2規則の採用(単位換算表: ベーシスポイント/パーセントポイント/ポイント/パーセント。ASCII「bp」・%と小数の換算・Storyline日付の包含は対象外)。Storyline表記を台帳`numeric_value`経由で紐付ける仕様は新仕様候補(未実装)。
- 検証器の`DUPLICATE`(同じ表記が同じFactに2回)の扱い(D-detでは発生しない。LLM腕を採らないなら不要)。
- `annotator`欄の値(既存検査は`A/B/MERGED`のみ許容。`DETERMINISTIC`は現状だとメタ欄エラー1件/テーマ)。
- 役割宣言のみ(Prompt変更)を採るか(Storylineの混入が減る傾向[探索的]、Storylineが長くなる副作用)。
- 周辺数値をWriterが書いた場合(hormuz 1/6)の扱い(Production側のGate化は新仕様候補)。

## ユーザー指定10点(Phase 2a中間の更新版)
1. 同一callで数値ランク付けは成立したか: 動くが割に合わない(Phase 2aのまま。STOP 1、JPY0.915/出力、66秒)。
2. 別call方式は必要か: **不要**。決定論(D-det v2)で足りる(Phase 2aのまま)。
3. 別callなら1記事いくら: 成功callの平均でJPY0.18/記事(retry込み0.31)。ただし再現性0.67・STOP 2で不合格。D-det v2はJPY0。
4. Fact/注意の分離をB3へ見せる方式は成立したか: 成立(Phase 2aのまま。注意書き継承100%)。
5. Storyline混入は消えたか: 事前登録の検出器は天井(0/27)。探索的regexでは役割宣言のみ・D-plusで減る傾向(Phase 2aのまま)。
6. Storyline品質は落ちなかったか: 事実誤りなし。ただし長くなる(Phase 2aのまま)。
7. **D-detは十分か**: **十分**。v2で危険な誤りが1→0(9テーマ)、E9で記事への悪影響なし。LLMが補えた実在の表記は0件(Phase 2aのまま)。
8. 追加コスト: D-det v2=JPY0。
9. **Sonnet注記不要化の見通し**: **見通し良好**。決定論assembler+D-det v2が作る注記(【事実N】+【中核数値】【周辺数値】)は、既存の機械検査に`annotator`欄以外すべて通過。Sonnet注記(約JPY15.7/記事)→JPY0にできる見込み。残り=上記の`annotator`値、`unmapped_claims`・`annotation_notes`の仕様化。
10. 残るユーザー判断: 上記。

## 腕別Closeout
| 腕 | 分類 | 根拠 |
|---|---|---|
| D-det v2 | **VALIDATED(Trial限定)**。Production採用=`USER_DECISION_REQUIRED` | 事前登録(PREREGISTRATION_03)の段階1基準1〜5・7を満たし、E9(M10)合格(周辺数値の記述1件・範囲表記の書き換え1件は説明可能なWriter遵守度の問題)。post-hoc修正である点を明記。 |
| D-plus-single-call | **REJECTED** | M7 STOP・M9超過(Phase 2a)。 |
| Separate-call(Luna) | **REJECTED**(Sol未実施) | M7 STOP 2、再現性0.67<0.90。 |
| 役割宣言のみ | **VALIDATED(Trial限定・no-harm)** | 採用はPrompt変更のためユーザー判断。 |

## Lane A interface への含意(annotated B3 producer)
- **annotated B3 producer = 決定論assembler(案D、`B3`は`selected_fact_ids`+Storylineのみ)+ D-det v2**。LLMに数値ランク(`number_ranks`)を出させる必要はない(不要)。
- **annotation.json の作り手**: `ledger_ids`(表記を含む全Fact)・`concept`(同表記/同Factの主数字・単位一致/包含の束ね)・`class`(core/peripheral)・`kind`はD-det v2が決定論で出せる。`unmapped_claims`(Storylineだけにある台帳外の数字は`_STORY`として検出可能だがtype付与の規則が必要)・`annotation_notes`(cap超過の周辺化は`capped_off`、漢数字候補は走査)は**要仕様化**。`annotator`値と`spec_sha256`は既存検査との整合が必要。
- **【事実N】の作り手**: assemblerのFact行順で決定論付与(E9で動作確認済み)。
- **Storyline行の印**: D-det v2が付与(表記を単位換算つきでFact本文表記と照合)。Storylineにだけある表記が台帳外の場合は`_STORY`=周辺扱い。
- `number_ranks`(LLM出力)は不要。したがってB3 Prompt/schemaの変更は不要(案D+D-det v2でProduction B3 Promptは無変更)。役割宣言のみ(Prompt変更)を入れる場合のみPrompt変更。
- 注意: D-fullのFact行は`scope/conditions`の数字も含むため、数値印の対象は「組立済みFact行」にする必要がある(E9では組立済みFact行を使用)。

## 事前登録からの逸脱・開示
- v2はcentral_bankの結果を見てから設計したpost-hoc修正。freeze前にv2の動作確認probeを1回実行(`--probe`、central_bankの差分を見た)。probe後に規則は変更していない(probe前のコードをfreeze)。
- E9スクリプト(`b3r2_e9_03.py`)はfreezeの「_e9_modules」に追記(実行前)。cwdはリポジトリルート(cost loggerのimport要件)。初回実行はcwd違いのimport失敗(API前)で、再実行した(課金なし)。
- E9のStorylineは印付き(Production runnerが注記版briefのStorylineを使う仕様に合わせた)。対照(ROOTFIX-01 E9)は印なしのStorylineで条件が異なる(差は印の有無の効果を含む。参考比較)。

## 成果物
`er052_output/b3_rootfix_trial_02/`: PREREGISTRATION_03.md、frozen_b3r2_03.json、b3r2_rank_02.py、b3r2_v2eval_03.py、b3r2_e9_03.py、eval_v2/(v2_eval_results_03.json、diff_v1_v2_03.md、blind_sheet_v2_03.md、m11/ddet_v2_c0/)、e9/(各テーマR0出力、eval_e9_03.json、e9_articles_03.md)、cost_ledger_b3r2_01.jsonl、HUMAN_CHECK_B3R2_02.md、RESULT_2A_01.md(Phase 2a)。

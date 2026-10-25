# B_LIGHT_EVAL_01(②B-light API 0評価、JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_07B、2026-10-25)
評価対象=`b_light_proto_01.py`(案β、sha256 `5b715f8e55a6c4583e74c267283fd6ed4c402d15592f4e90ff5c174da7236f76`、事前登録`B_LIGHT_PREREGISTERED_01.md`で凍結後に**変更なし**)。評価=`eval_b_light_api0_01.py`(保存済み転写のみ・socket guard・LLM判定なし・新規ASR/TTS/Azure呼出0・**費用0円**)。出力=`eval_b_light_api0_01.out.txt`/`.out.json`。再現: リポジトリrootで`PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/eval_b_light_api0_01.py`(**2回実行で`.out.json`/`.out.txt`のsha256が完全一致=決定的**: json `b7866335…`/txt `6708f19c…`)。単体test=`b_light_proto_01_test_01.py` 44 PASS。
使用モデル: 新規モデル呼出なし(転写の元は既存: OpenAI `gpt-4o-mini-transcribe`=Production Primary[比較基準のため旧世代の例外]/Azure ja-JP=Production Secondary)。
**比較基準のProduction**は07Aが`er078_*`/`er007_*`を並行編集中のため作業ツリーに依存せず、pin commit `89b630bd1086a638b2fec1f00d69bfae8722b665`のtop-level `*.py`スナップショットで評価(スナップショットがF2前のProductionであることをassertで確認)。F1+F2適用後の姿は`proto_value_gate_fix_04.apply_in_process`(v4)で再現(07A適用の元になる凍結proto)。**07Aの最終コードで再実行すれば同じ手順で再確認できる**(PINを差し替えるだけ)。

## 1. 事前登録基準の結果
| 基準 | 結果 | 判定 |
|---|---|---|
| 1a 増分誤PASS(N-3 30clip、実OpenAI+実Azure、音声は意図的誤読) | **0**(+F→+B で新たにPASSになった件なし)。composite評価対象12件の阻止理由: 二次値不一致4(N3-01/02/03/30)、一次読み不一致2(08/15)、不規則読み2(17/21)、適用外4(04/05/19/29) | **合格** |
| 1b 増分誤PASS(N-1 確定負例151対、最悪ケース=Secondary転写が原稿そのもの) | 露出**1件**: `N1-new-018` 原稿`月のしわ、8,900本超`/Primary`月の詩は8000900本超`(型=値garble)。それ以外の型は**0** | **合格**(型内の1件。下記§3で個別審査・残余リスク開示) |
| 1c 合成負例55件(Secondary正答のみ/Primary正答のみ/両方違い/矛盾/読み違い/不規則/否定/助数詞/値違い) | composite PASS **0**(案αも0) | **合格** |
| 1d 実Production履歴のP-S対(`ng_pool_cases_01.json`のSecondary記録あり**43対**) | compositeによる増分PASS **0** | **合格** |
| 2 回帰(+FがPASS→+BでNG) | 月題・N-3・履歴43対・Melos: **0** | **合格** |
| 3 月題12転写の救済 | base 2 → +v2 4 → **+F 3** → **+B 5**(増分**+2**)。attempt別(+F→+B): a1 0/4→0/4、a2 1/4→1/4、**a3 2/4→4/4** | 効果あり(狭い) |
| 4 Melos副作用 | 判定同一(`三日目`は不規則読み値でcomposite適用外。Primary側v2のPASS_WITH_WARNINGが従来どおり) | **合格** |
| 5 評価不能の開示 | §4 | 開示済み |
| 6 決定性・隔離 | 2回実行一致/Production file変更0(`git diff`で`er*`は07A分のみ)/AST test(Productionがprotoをimportしない) | **合格** |
→ **Status候補(事前登録の機械写像): VALIDATED(限定)**。限定の中身=§5。最終Statusは Fable。VALIDATEDが上限(Production採用は自動開始しない・ユーザー専決)。

## 2. 月題12転写の詳細(`+F`=07A適用後の代表)
| 転写 | base | +v2 | +F | +B | composite経路 |
|---|---|---|---|---|---|
| a1 保存 `月野詩は8000句800` | NG | NG | NG | NG | 矛盾(8000+800=8800≠8900・`句`含む) |
| a1 再転写 `月野詩は8,900本超え`×2 | NG | NG | NG | NG | Primary読み`つきのうたわ`≠`つきのしわ`(値は正しい) |
| a1 再転写 `好きの詩は8000900…` | NG | NG | NG | NG | Primary読み不一致(`すきの`) |
| a2 保存 `月の死は八千九百本超` | NG | **PASS** | PASS | PASS | v2のPrimary層で既に救済 |
| a2 再転写 `月の島は千九百本超`×3 | NG | NG | NG | NG | **矛盾**(千九百=1900 vs Azure8900。桁欠落は断片説明不成立) |
| **a3 保存 `月の氏は8000900本超`** | NG | NG | NG | **PASS_WITH_WARNING** | **composite**(断片`8000+900`=8900、Azure`8900`、Primary読み`氏は`=`しわ`) |
| a3 再転写 `月野氏は八千九百本超` | NG | PASS | PASS | PASS | v2 |
| a3 再転写 `月の詩は八千九百本長` | PASS | PASS | PASS | PASS | 既存PHONETIC(値EQUAL) |
| **a3 再転写 `月のシワ、8000九百本超`** | **PASS** | PASS | **NG(F1)** | **PASS_WITH_WARNING** | **composite**(`8000+九百`=8900。F1が新たにNG化した型をβが戻す) |
- 読み: Azure転写の`杉野氏は`(a3)の読みは使っていない(Primaryの`氏は`/`シワ`で保証)=`杉野氏`型のAzure誤読を通さない設計が実データで効いた。
- **F1の副作用の定量**: base(現行)でPASSだったa3再転写#2が、F1適用で唯一NGに転じる(12転写中1件、07Aの771+未知493評価では出ていない型)。βなしでF1だけを入れると月題の救済数は4→3に減り、βで5に戻る。
- 効果の天井: **a1・a2のNGはβ(およびAzure値を使う全方式)では救えない**。a1=Primaryが`月野詩`/`好きの詩`と書く読み不一致(+全エンジンが`超え`と書く→TTSが`こえ`と読んだ可能性=真のNGかもしれない)、a2=Primary`千九百`とAzure`8900`の2エンジン値矛盾+Primary読み`島`。a2は第3の独立証拠(γ)があっても、**読みをPrimaryに限る限り**`月の島は`で不一致のまま。

## 3. N-1最悪ケース露出1件の個別審査(基準1b)
`N1-new-018`(`月のしわ、8,900本超`/`月の詩は8000900本超`、型=値garble): この負例は委任_02で**自作した合成**(音声はない)。『Primaryが8000900と書き、Azureが台本通り8900を返した』という最悪仮定でのみβがPASSにする。実音声が8,000,900と読まれていた場合の誤PASSがβの**残余リスク**: 発生には『Azureが音声と無関係に台本通りの値を返す』ことが必要。実測のAzureは意図的に値を誤読させたN-3の3件(8,800/89,000/+近音)でいずれも**音声どおり**(`8800`/`8万9千`)を返し、台本通りには返していない(0/3、統計的保証ではない)。他の型(値違い・桁違い・近音・わ脱落・助詞・否定・不規則・助数詞・同形異音)の露出は**0**。事前登録1bの許容(値garble型の露出のみ)に収まる。

## 4. 評価不能の件数(基準5)
- P-4 実attempt=562件(`attempt_pool_01.json`、Secondary記録あり**0件**。うち421ユニークがOPEN-517評価の母集団): Primary×Secondary対が揃わず**評価不能**(v2/F1の評価は別資料。βはSecondary前提のためP-4へは最悪ケース被覆のみ)。
- 未知データ493件(`unknown_pool_02.json`、Primary転写のみ): 評価不能。
- N-1 151対: 音声・Secondary実転写なし=**最悪ケース被覆**のみ(§3)。
- 実履歴P-S対: `ng_pool_cases_01.json` 176件中、Primary・Secondary・原稿が揃うのは**43対**(133件は評価不能)。43対中、compositeの評価対象になったのは24(適用外13・Primary数値脱落5・Secondary値不一致3・不規則読み2・Primary読み不一致1)で、**救済・誤PASSとも0**。
- 追加Azure呼出が要る対(現行はP1/最終ゲートでAzureを呼ばず、βの事前判定が真):評価母集団で**2件**(月題a3保存・a3再転写#2)=見積約0.53円。

## 5. Status候補と限界(隠さず開示)
- Status候補: **VALIDATED(限定)**(事前登録の機械写像、最終はFable)。上限VALIDATED。
- 限界: (a)**効果は『位取り断片連結型の数詞崩れ』に限られ**、月題12転写で+2(a1・a2は構造上救えない)。(b)断片連結型の実データは月題の2転写のみ(n=2)で**汎化は未確認**。合成の正例4件(`売上は1000200円`等)は設計対象型の動作確認であり実頻度の証拠ではない。(c)同一データ(月題・N-3)で設計と評価を行った(未知データでの検証なし)。(d)P-4・未知データではSecondary未記録のため評価できない。(e)追加Azure呼出の実測コストは未計測(見積のみ)。
- 汎化確認の手段は`B_LIGHT_BUDGET_PLAN_01.md`に見積のみ記載(本委任では実行しない)。
- Opus独立レビュー(条件A: 新しい判定フロー)依頼文=`OPUS_REVIEW_REQUEST_01_BLIGHT.md`。

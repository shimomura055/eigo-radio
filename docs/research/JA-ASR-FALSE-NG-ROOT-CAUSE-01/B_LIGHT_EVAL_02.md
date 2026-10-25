# B_LIGHT_EVAL_02(②B-light 案β API 0再評価。M-1是正後。JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_08、2026-10-25。API 0・LLM/ASR/TTS呼出0・実費0円・Production変更0)
事前登録=`B_LIGHT_PREREGISTERED_02.md`(proto v2 sha `d041b1ca…`。評価前に凍結)。評価=`eval_b_light_api0_02.py`(出力=`eval_b_light_api0_02.out.txt/.json`)。**2回実行で出力完全一致(決定的)**。比較基準=pin `89b630bd1`のProductionスナップショット。07A commitは本評価時点で未着(`prod07a_committed_at_eval=false`)=Production関数での再現一致確認は07A commit後に再実行(§7)。
v1評価(`B_LIGHT_EVAL_01.md`)の数字(F後3→β5、増分+2)は比較基準が誤っていた(Opus M-1)ため**引用しない**。以下が是正後の数字。

## 1. 月題12転写(基準3)
| 列 | PASS | 内訳 |
|---|---|---|
| base(pin Production) | 2 | a3再転写#1・#2 |
| **base+F1F2(07A後Productionの代表)** | **1** | a3再転写#1のみ。F1が a3再転写#2(`月のシワ、8000九百本超`)を`final_gate_value_diff`で**新たにNG化** |
| **base+F1F2+β** | **5** | +4: a2保存転写・a3保存転写・a3再転写#0・a3再転写#2 |
| (参考)β読みstrict(`normalize_ja`完全一致のみ) | 1 | 増分**0** |
| (参考)β Secondary読み食い違い=veto | 2 | 増分1(a2保存転写のみ) |
| (参考)base+v2+F1F2 / +β(旧基準) | 3 / 5 | v2部品(Primary層)が+2を足していた |
- attempt別(F12→F12B): attempt1 0/4→0/4、attempt2 0/4→1/4、attempt3 1/4→4/4(安定救済=全転写PASSはattempt3のみ)。a1(Primary読み不一致)・a2(桁欠落[千九百]=2エンジンの値矛盾)は設計どおり救えない。
- **増分4件の依存関係(重要)**: 値atom除去後の残りに対するProduction既存の読み分類(`classify_ja_asr_match`)は、a3再転写#2のみ`PHONETIC_MATCH`で成立。残る3件(`月の死は`・`月の氏は`・`月野氏は`)は`TRUE_CONTENT_MISMATCH`で、**v2の助詞発音等価(`は→わ`)に依存**して初めて成立する。さらに3件(a3保存・#0・#2)はSecondaryの残りの読みが原稿と食い違う(`杉野氏`)=警告+試聴必須。→ **月題の効果は『v2読み規則の採用』と『Secondary読み食い違いの許容(試聴必須)』にほぼ全面的に依存**する。
- a2保存転写の増分は、v1評価で『F後に既に通っていた』と誤認していたもの(v2部品の効果)。

## 2. N-3 30 clip(基準1a・2)
誤PASS数(=PASSになった件。音声は意図的誤読で本来全てNG): base 16 / F1F2 15 / **F1F2+β 15** / strict 15 / veto 15 / 旧v2F12 15 / 旧v2F12B 15。
- **基準1a 増分誤PASS(F1F2→β)= 0**(strict・veto列も0)。基準2 回帰0。
- F1F2がbaseから新たにNG化した1件=`N3-02`(`final_gate_value_diff`、転写`八万九千本町`=本来NGの誤読音声)=**F1の正しい効果**。compositeは`R4_atom_notation`等で評価対象外(NG維持)。
- composite評価対象になった12件の阻止理由: `secondary_value`1(N3-01)・`R4_atom_notation`3・`not_applicable`4・`primary_reading`2・`A4a_irregular_reading`2(N3-17/21)。eligible reason外でcompositeが通りうる件=0。

## 3. 実Production履歴のP-S対43(基準1d・2)
PASS数: base 18 / F1F2 18 / **F1F2+β 19**。増分**1件**=`月の死は八千九百本超。…`(原稿`月のしわ、8,900本超`、S=`月の詩は8900本超`)。**個別審査**: これは月題a2保存転写と**同一音声・同一対**(`ng_pool_cases`に月題が含まれる)。値は原稿・Primary(八千九百)・Secondary(8900)で一致し、2エンジンとも`し|は`と分割(音は『しわ』で一致、助詞は→わ)。読みは試聴必須(`JA_PRON_EQUIVALENT`+`JA_COMPOSITE_LISTEN_REQUIRED`)。**誤PASS疑いなし**(独立な新規増分ではなく月題の1件の再掲)。回帰0。F1が履歴でbaseから新たにNG化した件=0。

## 4. N-1最悪ケース(基準1b。Secondary=原稿そのもの、比較=F1F2)
対=151。compositeがPASS候補にしたのは3件、うちF1F2がNGなのにcompositeがPASS(**露出**)=**1件**=`N1-new-018`(型=値garble、自作負例: 原稿`月のしわ、8,900本超`/Primary`月の詩は8000900本超`)。**基準1b: 型内のみ(合格)**。strict読みでは露出0(=この1件もv2読み規則=`詩は→しわ`に依存)。型外の露出0。残余リスク(開示): 実音声が`8,000,900`のように本当に読まれていてもAzureが台本値を返す場合に限りcompositeが通るが、その場合の誤受理は『台本値と同じ数を断片で発音した』ケースで、試聴必須が付く。

## 5. 合成負例(基準1c・9)
| 群 | 件数 | composite(β)がPASS | 案αがPASS | 増分誤PASS(F1F2 NG→β PASS) |
|---|---|---|---|---|
| V1(v1の55件: 値違い・読み違い・不規則・否定・助数詞・値) | 55 | **0** | 0 | **0** |
| **M3(複数atom・同助数詞反復)** | 17 | **0** | 0 | **0** |
| **FB(F-B・Secondary表記[かなN数詞・全角空白run・万]・Primary空白run・万含み・R-3違反[`12000|300`・3断片・`80|九百`]・R-4)** | 19 | **0** | 0 | **0** |
- 阻止理由の分布(M3+FB): `primary_secondary_value_contradiction`18・`secondary_value`(順序/個数/値)10・`R4_atom_notation`5・`primary_value_missing`2・`primary_reading`1。
- V1のうちF1F2自体が通した15件はβ非関与の既存Production挙動(Primaryのみ正しい場合のPrimary単独PASS、`3日待った`型の既存盲点[DESIGN_02 §2]、Secondary=原稿そのもの=EXACTでのP3受理)で、βは増やしていない。
- 合成の正例8件(設計対象型の動作確認のみ・実頻度の証拠ではない): 複数atomの両garble/片garble・反復garble・全角数字を含め全て`PASS_WITH_WARNING`+試聴必須。

## 6. Melos(基準4)・追加Azure呼出・評価不能(基準5・7)
- Melos preview(`三日目`、不規則読み値): base NG / F1F2 NG / **β NG(F1F2と同一)**。副作用0(旧基準でv2部品が救っていた1件は、v2を比較基準から外したため『Productionに無い救済』として消えた)。
- 追加Azure呼出が要る対(現行はP1/最終ゲートでAzure不呼出)=2件(見積0.53円/評価母集団ぶん)。
- 評価不能(開示): P-4 実attempt562(Secondary記録0)、未知データ493(Primary転写のみ)、N-1 150対(実Secondary転写なし)。

## 7. R-5予備集計(API 0・保存転写。判定基準ではない)
F1+F2が新たにNG化する件(base PASS→F1F2 NG)と、β対象になりうる値差NG(`p1_value_diff`/`final_gate_value_diff`)の件数:
| 母集団 | n | F1F2が新たにNG化 | F1F2下の値差NG |
|---|---|---|---|
| P-4 attempt_pool(562) | 562 | 0 | p1_value_diff 13 |
| 未知データ(493) | 493 | 0 | p1_value_diff 36 |
| 履歴P-S対(43) | 43 | 0 | p1_value_diff 5 |
| 月題(12) | 12 | **1**(a3再転写#2) | p1 6 / final_gate 1 |
| N-3(30) | 30 | 1(N3-02=本来NG) | p1 3 / final_gate 1 |
- 実データ(P-4・未知・履歴=合計1,098件)ではF1の新規誤NGは**0件**。F1の新規NGは月題の1件(正常音声)のみ。βの対象型(Primary値runが断片連結で説明可能)の実頻度はこの予備集計では決まらない(Secondary転写が無い母集団が大半)。**本計測はProduction側で行う**(`R5_MEASUREMENT_SPEC_01.md`、07A commit後の別委任)。
- Production関数での再現一致確認(07A commit後): 同じ入力(月題12・N-3・履歴43)で列`base+F1F2`の判定がProduction版(`value_guard_kana_unified`導入後)と一致するかを、`BLIGHT_PROD07A=1`のとき追加で検査する拡張を07A commit後の委任で行う(現時点で07Aは未commit)。

## 8. 事前登録基準の機械判定とStatus候補
| 基準 | 結果 |
|---|---|
| 1a 増分誤PASS=0 | 合格 |
| 1b N-1露出が値garble型のみ | 合格(1件、型内) |
| 1c 合成負例PASS=0(V1+M3+FB) | 合格 |
| 1d 履歴増分の個別審査 | 1件(月題a2と同一)=誤PASS疑いなし |
| 2 回帰0 | 合格 |
| 4 Melos副作用0 | 合格 |
| 9 M-3・F-B負例全NG | 合格(36件) |
| 3 月題増分 | **4**(strict 0 / veto 1) |
- 事前登録写像: **VALIDATED(限定)候補[低優先]**(最終Statusは Fable)。限定の中身: ①評価母集団が月題中心(断片連結の実データはn=2〜3)、②**効果の3/4がv2読み規則に、3/4がSecondary読み食い違い許容に依存**、③合成データ比率が大きい、④R-5実測が未了。**Opus所見(iii)に従い、VALIDATED(限定)で止め、低優先の採用候補**を推奨する。T1(有料Trial)は非実施。
- 参考: 読み規則別の内訳(§J、事後追加の探索的集計・判定基準ではない)は`eval_b_light_api0_02.out.txt`末尾。

## 9. 結論(先に)
是正後の基準で、βは**安全性の全基準に合格**(増分誤PASS 0・回帰0・複数atom/F-B負例36件全てNG)。ただし**効果は月題12転写で+4(1→5)で、その大半が(a)v2の助詞発音等価の採用、(b)Secondary読み食い違いの許容(試聴必須)に依存**する。Production既存の読みクラスだけで成立するのはa3再転写#2の1件(F1が新たに生むNGの回復)のみ。これはβを採用提案する材料としては弱く、R-5の頻度データ(Production側計測)を待って判断するのが妥当。

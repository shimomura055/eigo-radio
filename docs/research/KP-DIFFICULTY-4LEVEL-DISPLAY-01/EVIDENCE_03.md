# EVIDENCE_03 (KP-DIFFICULTY-4LEVEL-DISPLAY-01 委任_03): Prompt較正案v2のheld-out評価 -> 不採用(v1残置)

結論: v2は採用条件(ii)「難/激難がSonnet難判定の半数以上」を満たさない(3/14=21%)ため**不採用**。本番Prompt(v1、sha 3d9c3c83...)・test・DESIGN_01は無変更。実費1.05円(Cap 6円内)。

## 条件
held-out 52件(委任_02の55件=ai_island_temple/redelivery_fee/melosと重複なし。X=uk_train_speaker_playback run_kp75_ev_01 / Y=sns_age_limit run_01 / Z=the_tell_tale_heart run_reselect_01、各Std(a2)+Adv(b1b)、既存run保存docのkp_candidates.json)。
Sonnet 5.5実読(blind、LLM呼出前に確定)=kpd03_out/kpd03_sonnet_labels.json: 易8/中30/難14/激難0。
LLM=gpt-6-luna(本番と同一grade())。v1=現行Prompt(sha 3d9c3c8322af...)、v2=委任_02の較正案(sha 134872989e7a...、文言はkpd03_common_01.v2_text)。ユーザー表示例は別3件(rely on/make room for/narrow down、Promptには含めない)。

## 結果(集計=kpd03_eval_01.py、生=kpd03_out/kpd03_eval_result.json、cost=kpd03_out/kpd03_cost_ledger.jsonl)
| 項目 | v1 | v2 | 採用条件 | v2判定 |
|---|---|---|---|---|
| Sonnetとの一致/隣接/2段階以上 | 26/26/0 | 31/21/0 | 2段階以上<=1 | OK |
| 難/激難の出力件数 | 2 | 5(難4+激難1) | - | - |
| Sonnet難14件のうちLLMが難/激難 | 1/14 | **3/14(21%)** | >=50% | **NG** |
| ユーザー表示例 rely on/make room for/narrow down | 易/易/中 | 易/中/中 | 全て隣接以内 | OK(Std/Adv同) |
| 同一表現のStd/Adv差(4表現) | 全0 | exceptionのみ1(易/中)、他0 | <=1 | OK |
| 分布 | 易16/中34/難2 | 易9/中38/難4/激難1 | - | - |

別系列(gemini-3.8-flash)のheld-out比較は、主要条件(ii)で不採用が確定したため**未実行**(費用節約。Charter 1・3)。参考: 委任_02の55件ではgeminiも難は2件のみ(Sonnet 15)=lunaだけでなく現行Prompt自体が難を出しにくい。

## 観測と限界
- 難の取りこぼしは句動詞/比喩(thrown into it, a say in)・文学語(vulture's, hideous, shriek, fastening)に集中。v2のrule5(基本語以外は原則medium以上)は「易->中」の分離には効くが、「中->難」の閾値は動かさない(「難」の定義とlunaの保守性が支配的)。
- v2の「全部同じ段階にしない」は難を押し出す効果が弱い(4件)。Sonnet 14件に対し3件のみ。
- 限界: Sonnetラベラーは単一(私)・blindだがSonnetの難基準はluna/geminiより厳しい。Sonnet難14は全件が本番モデルより上=ラベラー差の可能性もある。ただし目的(4段階を実質使う)に対し、難が出ない事実は「実質2〜3段階表示」のまま。
- 今回のheld-outはv2評価で使用済み。v3等で再調整するなら新たなheld-out(別記事)が必要。
## 次の一手候補(未実施・Fable判断)
(a) v1残置(現状: 隣接以内率100%、表示は易/中主体)。(b) rule5に加え「難」の定義を具体化(句動詞の比喩用法・文語・抽象語は難)したv3を新held-out(別記事>=50件)で再評価(見込み約1円/回、改善見込み中)。(c) 判定モデルをgemini-3.8-flash等へ変更(55件でも難2件で改善見込み低、費用増ゆえ非推奨)。分類=B(承認範囲内の品質調整、ユーザー判断不要)。

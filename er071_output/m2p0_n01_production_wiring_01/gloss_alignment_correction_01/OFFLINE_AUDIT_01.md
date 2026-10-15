# OFFLINE_AUDIT_01 (KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01 委任_01A)

スクリプト: `er071_gloss_alignment_correction_01_offline_audit.py`(API 0回、費用JPY0)。結果JSON: `OFFLINE_AUDIT_01.json`。入力: `gloss_alignment_01/census_01.json`・`aprime_targets_01.json`・`replay_high_01.json`(再集計せず流用)。本番コード・Prompt・Gateは無変更(importして読むのみ)。

## 分母
| 集計 | 分母 |
|---|---|
| census(全er*_output) | 226 record / 1,129 item |
| A'窓再判定 | 153 attempt / 765 item、対象11 row、ユニーク6 |
| replay(現行規則、gpt-6-luna high) | 27 row = 実対象16(8ユニーク×2rep)+ 対照10 + スロット罠1 |
| 意味欠落候補の列挙 | A'ユニーク6 + census対象ユニーク5 を重複排除 = 8ユニーク |

## (a) 現行「～」機械FAILの誤NG候補
- (a1) replay 27 rowの出力glossへ現行ルールを適用: **FAIL 0件**(実対象16/16は「～」を含まない整合gloss。スロット罠1件はKPにsomethingがあるため許可)。= 実出力での誤NGは観測されなかった(ただし8ユニークのサンプル依存)。
- (a2) census 1,129 itemのうち、KPにスロット語が無いのにglossに「～」がある item: **29件**。目視で付けたラベル(Sonnet、ユーザー未確認): 承認規則上は辞書的に自然(`LEGIT_DICTIONARY_TILDE`)7件 / 欠落(`STALE_OMISSION`、`urge to watch→～したい衝動`)1件。残り21件は**機械推定**(KP==displayで末尾が前置詞/不変化詞。`point to`『～を示す』、`answer for`『～の責任を負う』等)。
  - 内訳: 手動ラベル 8(legit 7 + stale 1)/ 機械推定legit 21 / ラベル不能 0。機械ヒューリスティックだけで数えると legit 24 / 判定不能 5(うち4件は手動で legit と判明、残る1件が真の欠落 `urge to watch`)。
- (a3) 誤NG候補の母集団: 29件中 **28件(97%)が承認済み規則上は正当と推定**。ただしこれらは大半がKP==display(再整合の対象外)で、現行ルールが実際にFAILにするのは「対象に入って、LLMが正当な『～』を返した」場合のみ。**実測誤NGではなく、仮に対象になった場合の仮想的な母集団**であり、頻度の推定にはならない。
- 解釈: 誤NG自体は稀(0/16)だが、29件のうち28件が正当な「～」であることは、「～の有無」が品質の指標になっていないことの傍証。

## (b) 意味欠落候補(canonicalizationでKPが伸びた対象)
- 8ユニークはすべて「追加された内容語」を持つ(機械算出: interviews / prices / human,helper / me / watch / narrow,view)= 欠落**候補**は8/8(必要条件であって欠落の証明ではない)。
- 目視ラベル(委任_01`VALIDATION_01.md` 3節、Sonnet、ユーザー未確認): 不整合 6(欠落4、曖昧1、弱い欠落1)/ 整合 2。
- **現行「～」ルールが旧glossで検出できるのは6件中3件(50%)**。見逃す3件は全て「～」が無い意味欠落(`raw-bean prices→焙煎前のコーヒー豆`〔prices欠落〕、`bring in a human helper→人を呼んで加える`〔helperの意味が曖昧〕、`close around me→周りから迫ってくる`〔me欠落〕)。= 欠陥①の核心(表層条件では意味欠落を拾えない)を数値で確認。
  - 注意: ルールが実際に適用されるのは「再整合LLMの出力gloss」であり、旧glossではない。旧gloss適用は「その型の不整合が『～』の有無で区別できるか」の検証であり、再整合出力のFAIL率ではない。
- 追加語ごとに日本語の対応が必要なケースは、機械的な確認(追加語→日本語span対応の存在)で検出可能なものが多い(prices/me/watchは対応spanが旧glossに無い)。一方 `helper`↔`人`のように**対応らしき語はあるが意味が曖昧**なものは言語的判断が必要(DESIGN_DRAFT_01の分離設計の根拠)。

## (c) 限界
1. ユニークが少ない(6〜8)。割合は参考値、0件は「起きない」の証明ではない。
2. ラベルは全てSonnet目視でユーザー未確認。機械推定と手動ラベルは件数を分けた。
3. 誤PASS(不整合を整合と通す)の事前推定は、既存記録だけでは**出来ない**(再整合出力は16/16整合で、誤PASSを起こす材料が無い)。有料Trial(TRIAL_PLAN_01.md T2)の注入欠陥セットで測る。
4. 新設計の機械検査(追加語→日本語span対応)を過去記録へ後ろ向きに適用した件数は未算出(span対応はLLM出力が必要で、旧gloss記録には無い)。

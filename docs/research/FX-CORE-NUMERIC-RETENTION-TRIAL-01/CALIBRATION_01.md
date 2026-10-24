# CALIBRATION_01 (M4: 保持Gate照合の較正、API 0円、2026-10-25)

目的: Opus M4。`er114.ja_present`は計測器と同じ関数のため、自己検証を避けて(1)人手blindラベルとの突合 (2)単位言い換え表の追加 (3)単位なし一致の厳格化 (4)英語側`_UNIT_HINT`の補完 を行う。コード=`er115_fx_numeric_retention_trial_01.py`(match_core / en_present)、較正実行=`er115_fx_numeric_retention_calibration_01.py`、結果JSON=`er115_output/fx_numeric_retention_trial_01/calibration/calibration_result_01.json`。

## 1. 人手blindラベル(コーパス由来)
- 対象: 既存20 run(ja_writerとannotationの揃うもの)のR0・R2本文 x 評価可能な中核数値(AMBIG[単位なし小整数]除外)=63個 x 2段 = **126ラベル**。ファイル=`calibration/blind_labels_01.json`(sha256=`76357591200b73f595d40fa4570e5e69eda8bfeed1e5d23728a847ae08957e8f`)。
- blind手順: 照合関数(ja_present等)の**結果を見る前に**、Sonnetが本文(R0/R2全文)を読み、数値が「書かれている(present)/ない(absent)/数字表記でなく言い換え・部分一致で伝達(partial)」を確定→ファイル保存→その後に関数を実行。(注: 集計値[R0 28/63]は委任_01で既知だが、項目別の結果は未見。)
- partial 4件(runごと: coffee fxpw_01の「2025年2月」[本文は「2月」]、tesla/spacex「2社」[本文は「両社」])はFP/FN集計から除外し別掲(いずれも関数はFalse。**Gate対象は日付・単位なし小整数を含まないので影響しない**)。

## 2. 結果(コーパス122ラベル: present 56 / absent 66)
| 照合 | TP | FP | FN | TN |
|---|---|---|---|---|
| 旧 er114.ja_present | 56 | 0 | 0 | 66 |
| 新 er115.match_core(単位言い換え表+単位厳格化) | 56 | 0 | 0 | 66 |
- 新照合が単位の分からない数字だけで一致とした(weak)件数: 0。旧新の判定差: 0件。
- **限界(重要)**: 既存コーパスには「単位の言い換え」「単位違いの同数値」の事例がほぼ無く、**コーパスだけではM4が指摘した弱点を検証できない**(旧でも誤判定0)。そのため次の合成ストレスで補った。

## 3. 合成ストレスケース(著者作成・コーパス由来ではない。21件)
| 照合 | TP | FP | FN | TN |
|---|---|---|---|---|
| 旧 | 10 | **4** | **2** | 5 |
| 新 | 12 | 0 | 0 | 9 |
- 旧の誤り: FN=「約9か月」が「約9カ月/9ヶ月」と書かれた場合(単位表記ゆれ)。FP=「約42〜46」が「42〜46人」「42〜46度」、「最大50(セント)」が「最大50人」、「約45(m)」が「約45度」と一致扱い(旧規則`not unit or not tunit`=単位が片方空なら一致)。
- 英訳側(observe-only): 旧`en_present`は`_UNIT_HINT`に m/meters 等が無く、「42 to 46 people」「400 million dollars」を一致扱い→新は単位hint(m/km/cm/mm/%/通貨/months/years等)で False。
- 新照合の方針: (a)単位は表記自体/通貨記号/ニュース欄で直後に付く単位(例『約42〜46【中核数値】 m』のm)から求め、本文側も同じ言い換え群(m=メートル、km=キロメートル、%=パーセント、か月=カ月/ヶ月、£=ポンド等)であること (b)単位が全く不明な場合のみ数字一致をweakとして認め計測に区別して残す (c)範囲は『AからB』『A〜B』(間に単位語可)。

## 4. 残る限界(Phase 1/2で観測し報告)
- 漢数字表記(例「千ポンド」)や表に無い単位語は未対応=**偽陰性側**(不足と判定→R0再生成が1回余計に走る安全側)。
- 概数可(rounding overlay)の概数表記は`approx_forms`で許容。
- 合成ケースは著者作成のため独立ラベルではない。Fableの抜き取り確認を想定(`calibration_result_01.json`の`synthetic.cases`に全件)。

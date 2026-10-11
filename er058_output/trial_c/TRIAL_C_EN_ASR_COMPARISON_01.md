# TRIAL_C_EN_ASR_COMPARISON_01 (英語ASR 現行 vs 統一案 縮小版比較)

管理ID: ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_04C / 2026-10-12 / Trial限定・Production変更なし・提案のみ(採用は人間ユーザー判断)
使用モデル: Azure Speech STT en-US と OpenAI Primary ASR は**測定対象=Production同一(最新性原則の例外)**。参考列にローカル faster-whisper small/medium。新規LLM/TTS呼出0、新規TTS生成0(保存wavのみ)。
実費: **Azure約35.05円**(32本・788.6秒・送信秒数x$1/h x160円。上限40円以内、`cost_actual_C_01.json`)。他の課金0。
結果: `trial_c_results_01.json`(全行・転写・分類・代理ラベル・合成誤読試験)。script: `er058_trial_c_en_asr_compare_01.py`(mock乾式 -> real、`--approved-budget-jpy 40`必須、Production telemetry/queue/attempt_history/Master Store書込なし)。

## 0. 結論(先行)
**限界**: 標本が小さい(評価可能 NG系22件+Primary PASS対照6件)。**真の正解(人間試聴)はなく**、独立3系統(OpenAI/Azure noPL/whisper)の合意による**代理ラベル**。したがって「統計的な確定」ではなく**方向性の根拠**。

1. **統一案(安全条件付き)は現行より「安全側」だった(この標本では誤PASS 0)。ただし救済は小さい。** Primary NG系22件中、Secondary(Azure、Phrase Listなし、厳格ラベル)で通ったのは **4件(18%)**: 偽NG判定の2件(HRキューの見出し2件)、曖昧1件(Coffee系 missing/messy)、曖昧+最小対警告1件(Muse/used)。合意誤読(TRUE_ERROR_SUSPECT)11件は**1件も通らなかった**(Azure noPLは11件すべてで原稿へ補正せず、誤りを誤りとして返した)。現行方式は定義上これらの救済0(標本が現行で不合格のものだから)。
2. **安全条件は必要。** 単純OR(安全条件なし、Secondary should_passなら通す)は実データで、**繰返し/言い淀みQAでNGだった音声(S13)をAzure HIGH_SIMILARITY_SAFEで通した**・最小対の警告なし通過(S23)も出た。合成誤読試験(Secondaryが最悪ケースで原稿に補正すると仮定)では、単純ORはPrimary NGの誤読144件を**100%通す**のに対し、安全条件案は**37件ブロック(数値・否定は全件)・24件を警告(最終試聴連動)**。**ただし残り83件(内容語置換24・脱落24・固有名詞置換27・複数形8)は安全条件では防げない**=Secondaryが原稿に補正しないことに依存(今回の実測では補正0/11)。
3. **Phrase Listは効果が見えない。** 同一wavでPL付き保存転写とPLなし転写を比べられた5件で、PLなしの方が厳格PASSが多い(3対0)。PL付きが改善した例は0。Phrase Listなし採用(5-3 #5)を支持(n=5、強い結論は不可)。
4. **統一案のQCD**(narrative5 160 callへの射影): 同一Promptで3回まで継続する効果で完了率 **95.3〜97.4%**(現行93.1%、定義差あり)・平均TTS 1.15〜1.22回(現行1.19)・LR/HR行きは **2.6〜4.8%**。**改善の主因はSecondary救済(実測の通過率5.6%)ではなく「旧フローが打切った所を3回目まで継続」(外挿、5〜8%のcall)**。ASR費用は増える(現行約0.07円/call -> 約0.27〜0.30円/call)。1回のSecondary(Azure約1.8円/40秒)は1回のTTS再生成(約0.135円)より約13倍高く、**費用だけで見るとSecondaryは割に合わない**(時間は Azure約10秒 対 TTS約120秒で、通過率約9%以上なら時間は得)。
5. **例外が必要**: (a) 数値・否定は不呼出(37/37ブロック、必須)、(b) 固有名詞(Muse -> use、Khaite、Toteme等、全ASRが同じ誤りを返す)はASRでは救えない=辞書/Ledger・最終試聴、(c) length/繰返しQA NGはSecondaryで救わない、(d) 最小対(-ed/-s/冠詞)はPASS_WITH_WARNING+最終試聴、(e) Key Phrase 4回構成は対象外(別Trial未実施)。
6. **推奨(提案、ユーザー判断)**: 統一案の骨格(Primary NG -> 安全条件 -> Secondary 1回[PLなし・厳格ラベル] -> 同一条件再生成)は**安全性の面では採用可能**だが、**期待できる救済は小さく費用は増える**ため、主眼は「Cascade 4段(Primary#2/Secondary#2)の廃止・force_secondary廃止・同一Prompt3回継続」とし、Secondaryは**ローカルwhisper medium(0円)を第一候補として再検討**する価値がある(下記7)。実装前に追加Opus確認は内容変更があれば要(Gate条件A)。

## 1. 標本と方法
| 群 | 本数 | 秒 | 内容 |
|---|---|---|---|
| PRIMARY_NG | 18 | 696.0 | er056の保存wav NG attempt全件(sha重複2件除外)。現行でPrimary NGだった音声 |
| HR_QUEUE | 6 | 30.8 | 現行HR queue(67行)のうち保存wavが存在する短い順(見出し・in_one_line) |
| CONTROL_PRIMARY_PASS | 8 | 61.7 | Primary PASS記録済みattempt(短い音声から無作為、seed=20261012) |
| 合計 | 32 | 788.6 | Azure noPL 1パス(Production同一method、cl.recordなし) |
**除外(評価対象外、課金は発生)**: S21,S22(HR: 保存PL転写とnoPL転写が全く異なる=wavがその後の再生成で上書きされた疑い、ratio 0.29/0.26)、S26,S27(対照: 現行Validatorで保存Primary判定を再現できず=原稿復元不一致)。評価対象 28本(NG系22+対照6)。
**代理ラベル**(系統族 = openai/azure noPL/whisper[medium優先]): 2族以上が同一差分(既知のUS->"u s"は除く)でNG=`TRUE_ERROR_SUSPECT`(真の誤読 **または全系統共通のASR限界**)、2族以上が原稿を支持=`FALSE_NG_LIKELY`、他=`AMBIGUOUS`(要試聴)。
**現行方式の挙動**は保存された実績(verified/HR/cascade_steps)をそのまま採用(再実行なし)。統一案・単純ORはPrimary保存転写+今回のAzure noPL転写にValidator(`classify_asr_match`)を適用して机上判定。

## 2. 誤PASS・不要NG・救済(NG系 n=22)
| 指標 | 現行(実績) | 統一案(安全条件あり) | 単純OR(安全条件なし) |
|---|---|---|---|
| 救済(Secondary PASS) | 0(定義上) | 4(PASS 3+警告付き1) | 6 |
| うち偽NG判定(FALSE_NG_LIKELY)の救済 | 0 | 2(S19,S20) | 3(S19,S20,S13) |
| 誤PASS(合意誤読を通す、TRUE_ERROR_SUSPECT 11件中) | 0 | **0** | 0 |
| 曖昧(AMBIGUOUS)の通過(要最終試聴) | 0 | 2(S14,S23[警告]) | 3(S02,S14,S23) |
| QA/長さGate NGの音声を通した | 0 | **0**(S03,S13,S18は不呼出) | **1(S13)** |
| Secondary不呼出(安全条件) | - | 7(数値否定4・長さ2・繰返し1) | 0 |
| ASR原因の不要NG残(Gate以外) | 2(S19,S20) | 0 | 0 |
注: S03/S13/S18は転写は原稿一致でもlength/QAでNG(ASR起因でない正当なNG)。「偽NG判定」2件(S03,S13)は転写ベースの代理ラベルで、Gate NGなので不要NGには数えない。
Primary PASS対照(n=6): Azure noPLも全件厳格PASS(Secondary単独に切替えた場合の偽NGは0/6)。**統一案ではPrimary PASSならSecondaryを呼ばない**ため、対照への影響なし。forced-Secondary(HRキュー5行)は保存転写のみ(wav無し)で、統一案ではPrimary PASSで完了=HR回避(5/5、Primary PASSが正しいかは未検証)。
**HR queue 67行のオフライン再判定(課金0)**: cascade 62行は保存Azure(PL付き)転写では全件が厳格PASSにならず(0/62)、Phrase List付きAzureの救済力は低い。今回のPLなし再転写では見出し2/4が救済された(上表、小標本)。

## 3. Phrase List有無(同一wav、n=5)
| id | PL付き(保存) | PLなし(今回) |
|---|---|---|
| S15 | UNCERTAIN(muse -> use) | 同一転写 |
| S19 | UNCERTAIN | NORMALIZED(厳格PASS) |
| S20 | UNCERTAIN | NORMALIZED(厳格PASS) |
| S23 | UNCERTAIN(muse -> use) | EXACT(厳格PASS) |
| S24 | UNCERTAIN | TCM(別の差分、NG維持) |
(S21/S22は上書き疑いで除外。)PLなしが優位または同等、PL付きが優位は0。

## 4. 合成誤読試験(安全条件の必要性、課金0)
音声が誤読Yを発話しPrimaryがYを正確に転写、Secondaryが**最悪ケース=原稿へ補正**と仮定(実ASRの補正率の測定ではない)。保存原稿28本から合成188件。
| 誤読の種類 | n | Primary段階で誤PASS(両フロー共通) | 単純OR誤PASS | 安全条件: ブロック | 警告(最終試聴) | 残存誤PASS |
|---|---|---|---|---|---|---|
| 数値変更 | 15 | 0 | 15 | 11 | 4 | 0 |
| 否定 追加/削除 | 26 | 0 | 26 | 26 | 0 | 0 |
| -ed脱落 | 21 | 5 | 16 | 0 | 16 | 0 |
| 複数形脱落 | 25 | 13 | 12 | 0 | 4 | 8 |
| 冠詞脱落 | 26 | 26 | 0 | - | - | - |
| 内容語置換(無関係語) | 24 | 0 | 24 | 0 | 0 | 24 |
| 内容語脱落 | 24 | 0 | 24 | 0 | 0 | 24 |
| 固有名詞置換 | 27 | 0 | 27 | 0 | 0 | 27 |
合計: Primary NG 144件のうち単純ORは**144/144通す**、安全条件案は**ブロック37・警告24・残存83**。Primary段階で誤PASS 44件(冠詞26・複数形13・-ed 5)は**両フロー共通の既存リスク**(Opus M6、統一案のPrimaryも変えない)。→ **数値・否定は安全条件で確実に守れるが、内容語・固有名詞の誤読は「Secondaryが補正しない」前提に依存**(実測では補正0/11)。

## 5. QCD射影(narrative5 160 call、`qcd_projection`)
Secondary救済率: カテゴリ別実測(内容語1/5、固有名詞0/5、数値否定0/4=不呼出、他0/4)→ 全体5.6%(Wilson 95%上限で上位シナリオ)。low/mid/high:
| 指標 | 現行(実績) | 統一案 low | mid | high |
|---|---|---|---|---|
| 完了率(3 TTS以内/LR前) | 93.1%(fallback含む) | 95.3% | 95.7% | 97.4% |
| 平均TTS/call | 1.188 | 1.222 | 1.205 | 1.146 |
| LR/HR行き | 6.9% | 4.8% | 4.3% | 2.6% |
| 追加ASR費用/call(Cascade or Secondary分のみ) | 約0.07円(Cascade発火3件) | 約0.30円 | 約0.29円 | 約0.27円 |
| 外挿(旧フローが打切った後の再生成)の割合 | - | 8.0% | 7.4% | 4.7% |
前提: 打切り後の再生成通過率は実測(2回目13/22、3回目2/8)、Azure音声40秒仮定。**完了率向上の大半は外挿(同一Prompt継続)由来**で、Secondary救済の寄与は小さい。時間: Secondary Azure平均10.4秒/回(実測)対TTS約120秒。
**Human Review率**: 現行 narrative5 は旧記録の「LR前の未完了」6.9%に対し、統一案(LR前)2.6〜4.8%(外挿込み)。LRはモデル化していない(別途)。

## 6. 現行 vs 統一案 の差まとめ
| 観点 | 現行(Cascade 4段・PL付き・fallback・減速後Primaryのみ) | 統一案 |
|---|---|---|
| 誤PASS | Primary単独 + Cascade救済(Secondary UNCERTAIN時のみ)。標本では救済0 | 標本0(ただし最悪ケース試験で内容語は無防備) |
| 不要NG | PL付きAzureでASR誤認により保持(見出し等) | 見出し型2件を救済 |
| 追加ASR呼出/NG attempt | Primary#2 + Azure PL x2 = 最大4 | Azure noPL 1(Primary NGかつゲート通過時のみ) |
| 費用 | NG発火少なく低い | Secondary呼出分だけ増(+0.2円/call級) |
| 実装の複雑さ | 4段+force+fallback+LR | ゲート+Secondary1回+再生成 |

## 7. 参考列: ローカルwhisper medium(0円)
NG系22件での厳格PASS: medium 5件(偽NG判定3/4・曖昧2/7・合意誤読0/11=ラベル構成上ほぼ0)、small 7件。Azure(4件)と同程度の救済を**0円**で得られる可能性がある一方、局所脱落(`People`脱落等、FREE_VERIFICATION 4-2)があるため単独の最終権威は不可。**Secondaryの第一候補をAzure(PLなし)かlocal mediumかは、U-8(Secondary選択)としてユーザー判断**。

## 8. 例外要否・制約・次の提案
- 例外(統一不能): 数値・否定(不呼出・必須)、固有名詞(ASR共通限界、Ledger/最終試聴)、length/QA Gate、最小対(警告+最終試聴)、Key Phrase 4回構成。
- 制約: n=22(NG系)で、救済率の信頼区間は広い(18%、Wilson 95%で約7〜39%)。標本はNG/HRのみで母集団の分布を代表しない。「補正0/11」もn小。代理ラベルは人間試聴の代替ではない。HRキュー wavの一部は上書きされており(2件除外)、残りも保存時点と同一音声である保証は完全でない。
- 次の提案(未実行・要承認): (1) 合意誤読11件・曖昧6件の**人間試聴**(0円、ユーザー作業)で代理ラベルの妥当性確認、(2) Secondary=local mediumの追加検証(0円)、(3) Key Phrase 4回構成のASR比較(別Trial)。Production変更・CURRENT_SPEC等SSOT編集はしていない。

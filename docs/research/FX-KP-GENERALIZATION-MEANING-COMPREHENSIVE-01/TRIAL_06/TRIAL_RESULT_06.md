# TRIAL_RESULT_06: X2p'補強Trial 最終結果(委任_33、Fable判定。API 0)

**最終Status: USER_DECISION_REQUIRED**(VALIDATEDとは宣言しない。REJECTEDとも判定しない)。Production配線なし。Prompt修正は1回のみ(TRIAL_DESIGN_07)を守り、本Trial内で追加のPrompt調整はしない。

## 1. 実行事実(機械的、DRAFT§1を継承)
- 構成: P案(本番相当 full-level・1 level全KP 1 call・rules_fulltext・prior・retry上限2)、arm=B0p(現行)/X2pp(X2p')。gpt-6-luna(Production gloss同一系列)、reasoning effort=high。X2p' Prompt無変更。
- 102 call・19.306円(cap 28円以下)、全group ALIGN_PASS・retry 0・JSON失敗0。Production hash start/end一致(`production_hash_start.txt`/`_end.txt`)。
- 二重判定: Fable(盲検、key開封前)+Opus(別context、`opus_labels_06.json`、理由=`OPUS_EVAL_06.md`)、厳しい側採用(継承ラベル含む)。集計=`AGREE_06_FINAL.md`。

## 2. 記録項目(ユーザー確認6項目)
1. **本番構成での効果再現**: HC(新難例9KP)のFAIL系 B0p 1 -> X2pp 0(Fable/Opus/厳しい側とも)。字義訳(FAIL_LIT)の解消は本番相当構成でも再現(feel like friction系=B0pの『摩擦のように感じる』、X2ppは『邪魔に感じる』等でPASS)。Stage 2(54KP)のPASS->FAIL系は0。R集合(元難例7出力)のFAIL系は、継承ラベル厳しい側で1(`question shaped like a trophy`『賞の形をした問いかけ』=継承FAIL_LIT。今回Fable=THIN・Opus=PASS)。
2. **新難例9件**: X2pp 18出力 = Fable単独 全PASS / Opus単独 PASS14+THIN4 / 厳しい側 PASS14+THIN4。字義訳0・FAIL0。B0pは同9KPで厳しい側 PASS13+THIN4+FAIL_LIT1。THIN4はkeep one's eyes on them rep2『人々から目を離さない』(対象特定)、legs fail someone rep2『誰かの脚が体を支えられなくなる』(説明的)、story with two different speeds(長い説明句、2出力)。
3. **過剰解釈**: 字義が正解のKP(`sheltered from the rain`・`smile through one's tears`・`keep one's eyes on them`対照、41番4件ほか)で解釈訳化 = **0**(Opus明言「41は4件ともPASS」「過剰解釈ではない」)。
4. **通常KP品質維持(Stage 2 54KP)**: PASS->THIN = Fable単独2件(grow lighter・shock someone's wallet)/ Opus単独7件 / **厳しい側7件**(keep someone company / grow lighter / shock someone's wallet / not the same picture / take off an ai costume / reach for someone's wallet / too broad a label)。PASS->FAIL系 = 0(3通りとも)。いずれも意味が誤りではなく、弱い・説明調・対象の持ち込み・狭い訳。
5. **実測単価・時間**: S2 B0p 0.0266円/KP -> X2pp 0.0704円/KP(2.6倍)、1記事セット(約10KP)換算+0.438円(70円目標の0.63%)。level当たり時間増分+25.8s(記事セット当たり=level数×25.8s、S2全体は+約5.3s/KP)。
6. **X/Y/Z適用可能性**: 下記§5。

## 3. 事前基準(TRIAL_DESIGN_07 §3)照合(詳細=AGREE_06_FINAL.md (d))
| 基準 | Fable単独 | Opus単独 | 厳しい側(継承込み) |
|---|---|---|---|
| (b)(1) HC FAIL系 X2pp<=B0p | 達成 | 達成 | 達成 |
| (b)(2) B0p=PASS->X2pp<=THIN 0 | 達成(0) | 不適合(4) | 不適合(2) |
| (b)(3) HC THIN<=B0p+1 | 達成 | 不適合 | 達成 |
| (b)(4) 持ち込み検出が増えない(HC 2->3) | 不適合 | 不適合 | 不適合 |
| (b') R FAIL系0・THIN<=2 | 達成 | 達成 | 不適合(継承FAIL_LIT 1) |
| (c)(1) S2 PASS->FAIL系0 | 達成 | 達成 | 達成 |
| (c)(2) S2 PASS->THIN<=2/54 | 達成(2) | 不適合(7) | 不適合(7) |
| (c)(3) 全itemADOPT(HR=0) | 達成 | 達成 | 達成 |
| (c)(4) S2持ち込み検出<=3 | 達成(1) | 達成 | 達成 |
- 持ち込み検出(機械)7件の目視: 真の否定持ち込みは0、全て語義に内在する否定(『離さない』『足りない』『表に出ず』等)の偽陽性または語義言い換え(AGREE_06_FINAL.md (e))。機械件数は合否に使わない。
- 一致率: 厳密一致83/100・PASS/非PASS二値一致83/100(70%以上=基準曖昧警告なし)。不一致17件=Fable PASS->Opus THIN 15件、Fable THIN->Opus PASS 2件(17:A・33:B)。

## 4. Fable判定(逐語)
- **字義訳の根本問題**: X2p'は新難例9KP(18出力)で字義訳0・FAIL 0、元難例R集合でもFAIL 0(継承ラベル厳しい側で1件FAIL_LIT=『賞の形をした問いかけ』、今回のFable=THIN・Opus=PASS)。現行B0pは新難例で字義訳1・THIN2。**字義訳の解消は本番相当構成でも再現**。過剰解釈(字義が正解のKP)=0。
- **新規悪化**: 通常KP(Stage 2 54KP)でPASS->THIN(意味は誤りでないが弱い・説明調・対象の持ち込み)が、Fable単独2件、厳しい側採用では7件。PASS->FAIL系は0。持ち込み検出(機械)はB0p 2->X2pp 5(目視は全て偽陽性または語義の言い換え)。
- **事前基準との照合**: (c)(2) PASS->THIN<=2/54 は厳しい側採用で7件(不適合)、(b') R集合のFAIL系0は継承ラベル採用で不適合、(b)(2)も厳しい側で不適合、(4)持ち込み検出は増加。**事前基準を全ては満たさないため、FableはVALIDATEDを宣言しない**。REJECTEDとも判定しない(根本問題=字義訳は解消し、悪化はTHIN級に限られ、単価増+0.44円/記事セット[0.6%]のため)。
- **Trial最終Status: USER_DECISION_REQUIRED**(品質トレードオフ: 意味の誤り[字義訳]の解消 vs 通常KPでの弱い訳の微増+単価0.6%増)。

## 5. X/Y/Z適用
- **X**: 主対象(比喩KP 15.4%)。HC側の字義訳解消はXのKPで起きた(AGREE_06_FINAL.md (g))。
- **Z**: HCのZ小説5KPはB0pの時点でFAIL系0、X2ppはFable単独で全PASS、Opusでは2出力がTHIN(厳しい側)。比喩KP発生率2.2%のためX2p'の利益が小さい。ユーザー判断の選択肢に「Z除外(Xのみ)」または「X/Z共通」を含める(UDR #179 A-1/A-2)。
- **Y**: 共通KP段(`er003_v1_n3_01_scaffold_generate.py` align_glosses)に依存し、OPEN-484(Y正式経路)と同時に配線される構造(実装なし)。

## 6. 次の選択肢(UDR #179)
(A)X2p'を採用候補として確定し、Production採用の正式判断へ / (B)説明調・持ち込みを抑える規則を1回だけ追加して再検証(約20円、KP累計約335円/500円) / (C)現行維持(REJECTED)。Fable推奨=A(記録のみ、採否はユーザー)。
## 7. 費用・使用モデル
本委任0円(API 0)。KP累計314.74円/500円。使用モデル(Trial_06生成)=gpt-6-luna(Production gloss同一系列、最新世代最上位系ではない。例外理由=評価対象がProduction系列そのもの・本番同一条件・Trial_04/05と比較可能にするため)。評価はFable+Opus。

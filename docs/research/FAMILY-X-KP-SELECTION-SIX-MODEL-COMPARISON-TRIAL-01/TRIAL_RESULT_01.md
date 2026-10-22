# TRIAL_RESULT_01: Family X Key Phrase選定・6モデル比較Trial 結果

管理ID: FAMILY-X-KP-SELECTION-SIX-MODEL-COMPARISON-TRIAL-01 委任_01 / 実施日: 2026-10-22(JST) / 実行者: Sonnet 5.5(実行層)
Status: **TRIAL_DONE_PENDING_FABLE**(Trial承認済み。**Production採用未承認**。Production・Prompt・選定ロジック・Validatorは無変更)
設計(実行前固定): `TRIAL_DESIGN_01.md` / 比較Excel: `KP_MODEL_COMPARISON_01.xlsx`(5シート) / 生データ: `er098_output/kp_six_model_trial_01/`

**重要な前提(読み方)**
1. 本Trialは**ユーザー指定Prompt(記事本文全文を渡す)**での比較で、現行Productionの方式(DB shortlist+軽量prompt+canonicalization+QA)とは別物。「既存Production」行は**方式差込みの参考値**であり、モデル差とPrompt方式差を混同しない。
2. 規則は厳密: 一般化(`~`/`A`/`someone`等への置換)**以外の変更は不可**。活用形の変更(例: `gave back`->`give back`)も「変更」とみなし本文一致の確認済みに含めない(別欄「活用形のみ相違」に分離)。
3. 14本文・各1回生成・評価者2系統の小標本。モデル間の差は『機械検証』(本文一致・5語以内)が明確、『学習価値』の主観評価は差が小さく評価者間でも揺れる(8節)。

## 1. Excel比較ファイルへのアクセス方法
- 場所: `docs/research/FAMILY-X-KP-SELECTION-SIX-MODEL-COMPARISON-TRIAL-01/KP_MODEL_COMPARISON_01.xlsx`(Excelで開くだけ)。push後のraw URL: https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/research/FAMILY-X-KP-SELECTION-SIX-MODEL-COMPARISON-TRIAL-01/KP_MODEL_COMPARISON_01.xlsx
- シート1「比較表」: 記事A->Standard->Advanced->記事B…。各レベルに「既存Production」「1 gpt-6-luna」〜「6 claude-sonnet-5-5」の行、列=KP1〜5、セル=「表現 (語数)」。緑=本文一致確認済みかつ5語以内 / 黄=要確認・活用形のみ相違 / 赤=NG・5語超 / 灰=技術的失敗。セルのコメントに判定・原文span・位置・一般化内容。
- シート2「品質評価サマリ」/シート3「費用サマリ」/シート4「検証詳細」(453候補、原文span・文字位置・一般化内容・主/参考評価・判定)/シート5「条件・Prompt」(Prompt全文・調整・設定・返却model ID・版表・単価出典)。

## 2. モデル別の本文一致・5語以内の遵守率(全14本文。分母=出力された候補数)
| 選定元 | 候補数(平均/セット) | 5語以内 | 本文一致 確認済み | うち一般化(置換)で確認 | 活用形のみ相違 | 言い換え/創作等のNG | 5語超 | 自己申告語数の不一致 | 5件未満セット |
|---|---|---|---|---|---|---|---|---|---|
| 既存Production(別方式) | 70 (5.00) | 100% (70/70) | 67.1% (47/70) | 1 | 21 | 2 | 0 | (申告なし) | 0 |
| 1 gpt-6-luna(現行) | 70 (5.00) | 100% (70/70) | 100% (70/70) | 6 | 0 | 0 | 0 | 0/70 | 0 |
| 2 gpt-6.1-sol | 37 (2.64) | 100% (37/37) | 100% (37/37) | 5 | 0 | 0 | 0 | 1/37 | 11 |
| 3 gemini-3.1-flash-lite | 70 (5.00) | 94.3% (66/70) | 92.9% (65/70) | 21 | 3 | 2 | 4 | 14/49 | 0 |
| 4 gemini-3.5-flash-lite | 67 (4.79) | 98.5% (66/67) | 73.1% (49/67) | 12 | 16 | 2 | 1 | 6/47 | 3 |
| 5 claude-haiku-5-5 | 69 (4.93) | 100% (69/69) | 100% (69/69) | 4 | 0 | 0 | 0 | 2/68 | 1 |
| 6 claude-sonnet-5-5 | 70 (5.00) | 100% (70/70) | 100% (70/70) | 24 | 0 | 0 | 0 | 0/70 | 0 |

- 「要確認(一般化spanが複数該当)」は0件(同一原文の繰り返し出現は一意扱い)。重複候補0件。技術的失敗0件。
- 厳格版(5語以内∧本文一致確認済み)合格KP数: Production 47 / Luna 70 / Sol 37 / G3.1 63 / G3.5 48 / Haiku 69 / Sonnet 70。
- 5語超の実例(全て Gemini): G3.1 `putting the two in the ring`(6語・本文に無い言い換え)、`it is too soon to say`(6語・本文には存在)、`on the other end of the line`(7語、自己申告5)、`zoom in on the name tag`(6語、自己申告5・活用形違い); G3.5 `a way into making a story`(6語、自己申告5・本文には存在)。
- 抽出(解析)の注記: モデル出力テキストから候補を機械抽出(Promptに出力形式指示を足していないため)。3セットは出力内に複数リストがあり、規則「最後の有効3件以上のグループ」で抽出、うち2セット(Sonnet D_Advanced/E_Advanced=『選定表』の後に語形を直した『意味説明リスト』が併記)は選定表(グループ0)を手動指定(`PARSE_OVERRIDES`、理由=選定表が『本文の元の箇所』列付きの実際の選定結果で、説明リストは解説目的の再掲)。G3.5 C_Advancedは下書き(除外項目あり)と最終リストが併記され、最終リストを採用(下書きの存在を『複数ドラフト出力』として記録)。モデル出力自体は一切修正していない。

## 3. 一般化と上級学習価値の比較
評価: 選定元と異系統の評価者=**主評価**(Luna/Sol/既存Production行はClaude Sonnet 5.5、Haiku/Sonnet行はGPT-6.1 Sol、Gemini行は2者平均)。各0〜2、候補スコア=(G+V+E+N)/8。総合版=厳格版∧主評価>=0.75∧G/V/E/Nが全て1以上。

| 選定元 | 主評価平均(0-1) | 参考(同系統)評価 | 主G 一般化 | 主V 上級価値 | 主E 易しさ排除 | 主N 単位自然さ | 一般化が必要な箇所の主G(n) | padding率(主) | 総合版 合格KP |
|---|---|---|---|---|---|---|---|---|---|
| 既存Production(別方式) | 0.636 | 0.696 | 1.79 | 0.83 | 0.71 | 1.76 | 1.00 (12) | 92.9% | 16 / 70 |
| 1 gpt-6-luna | 0.732 | 0.732 | 1.83 | 1.26 | 1.01 | 1.76 | 1.39 (18) | 42.9% | 48 / 70 |
| 2 gpt-6.1-sol | 0.760 | 0.949 | 1.89 | 1.24 | 1.14 | 1.81 | 1.60 (5) | 28.6% | 32 / 37 |
| 3 gemini-3.1-flash-lite | 0.707 | -(両者が主) | 1.79 | 1.14 | 0.99 | 1.74 | 1.59 (54) | 75.0% | 34 / 70 |
| 4 gemini-3.5-flash-lite | 0.749 | -(両者が主) | 1.90 | 1.16 | 1.02 | 1.90 | 1.72 (46) | 53.6% | 30 / 67 |
| 5 claude-haiku-5-5 | 0.745 | 0.750 | 1.83 | 1.19 | 1.13 | 1.81 | 1.25 (16) | 71.4% | 49 / 69 |
| 6 claude-sonnet-5-5 | 0.777 | 0.777 | 1.94 | 1.27 | 1.26 | 1.74 | 1.82 (22) | 35.7% | 53 / 70 |

- 一般化(置換)の実施数(機械で原文span確認済み): Sonnet 24 > Gemini3.1 21 > Gemini3.5 12 > Luna 6 > Sol 5 > Haiku 4(Production 1)。「一般化が必要な箇所の主G」はSonnet 1.82が最も高く、Haiku 1.25・Luna 1.39が低め(必要箇所で未実施が多い)。
- 上級者向け学習価値(主V)・易しさの排除(主E)は全モデルで1前後〜1.3と中程度で、モデル間の差は小さい(0.1〜0.3)。Productionは別方式(shortlist+原形化)の影響でV/Eが低い(0.83/0.71)。
- 件数: SolはPromptの「数合わせをしない」を最も強く適用し平均2.64件/セット(11セットが5件未満、C_Standardは0件と回答)。他モデルはほぼ5件を出力。評価者はpadding(価値の低い候補で5件を埋める)率をSolが最小(28.6%)・Gemini 3.1が最大(75.0%)と判定。
- **自己選好の観測**: Solの候補をSol自身が評価した値は0.949、Claudeが評価した値は0.760(差0.19)。同系統評価を主評価に使わない設計(異系統=主)の妥当性を裏付ける。Sonnetは自己評価0.777=Sol評価0.777で偏りは観測されず。
- 評価者間の一致: 453候補で2評価者のスコア相関0.58、平均絶対差0.11(0〜1尺度)。モデル間の主評価差(0.707〜0.777)は評価者間のぶれと同程度であり、**主観評価だけでの順位付けには注意**。

## 4. 代表的な良い選定・悪い選定の実例(各モデル、本文根拠付き)
| 選定元 | 良い例(記事/レベル) | 本文根拠(原文span) | 悪い例 | 根拠・判定 |
|---|---|---|---|---|
| Luna | `stretch what was said`(F Advanced, 4語, 主1.00) | 本文 “you stretch what was said about the Typhoon mission too far”(A_EXACT) | `alone caused the different results`(D Standard, 5語, 主0.25) | 本文には存在(A_EXACT)するが説明的で平易(V/E=0)。機械検証PASSでも学習価値は低い |
| Sol | `hands the baton to someone`(E Advanced, 5語, 主1.00) | 本文 “hands the baton to a person” の `a person`->`someone`(B_GEN_UNIQUE) | `stretch`(F Advanced, 1語, 主0.25)。またC Standardは0件回答 | 1語で基本動詞のみ(Claude評価でV/E/N=0)。件数不足は『数合わせしない』規定の最大適用 |
| Gemini 3.1 | `none other than someone`(B Standard, 4語, 主1.00) | 本文 “none other than you.” の `you`->`someone`(B_GEN_UNIQUE) | `putting the two in the ring`(A Advanced, **6語**) | 5語超かつ本文に存在しない言い換え(NG_NO_MATCH)。別に `it is too soon to say`(D Standard)は本文にあるが**6語**、`on the other end of the line`(E Advanced)は7語(自己申告5語) |
| Gemini 3.5 | `hands the baton to someone`(E Advanced, 5語, 主1.00) | 本文 “hands the baton to a person” | `a way into making a story`(C Advanced, **6語**、自己申告5語) | 本文にはあるが6語=5語以内違反かつ語数誤申告。`give back some gains`(G Standard)は本文 “gave back some gains.” と活用形が違い『活用形のみ相違』(16件) |
| Haiku | `become fuel for meanness`(D Advanced, 4語, 主1.00) | 本文 “did boredom become fuel for meanness?”(A_EXACT) | `approved by their original creators`(C Advanced, 5語, 主0.25) | 本文には存在するが説明的な平易句(V/E低)。F Standardは5件目を出せず4件で、出力内に却下項目や表が混在し体裁が乱れる |
| Sonnet | `~-led coalition forces`(F Standard, 3語, 主1.00) | 本文 “Saudi-led coalition forces” の `Saudi`->`~`(B_GEN_UNIQUE) | `solve something by itself`(B Advanced, 4語, 主0.38) | 本文 “solve the case by itself” の一般化は存在確認できるが、内容が平易(Sol評価V/E=0) |
| 既存Production(別方式) | `none other than`(B Standard, 3語, 主1.00) | 本文にA_EXACT | `make a reward smaller`(D Standard, 主0.25) | 本文は “make the other person’s reward smaller”(語を抜いた原形化)で連続部分列でない(NG_NO_MATCH)。`pump one's fist`等もcanonicalizationで原形化されるため厳密規則では活用形のみ相違(21件) |

(各例の全候補は Excel「検証詳細」で確認できる。)

## 5. モデル別の実費・記事セット単価(実測usage x 単価。為替 USD/JPY=160 はプロジェクト既定[`er009_n1_routing_governance_10_actual_model_cost.py:20`]、実為替ではない)
| 選定元 | 入力token計 | 出力token計(思考込み) | うち推論token | 単価 in/cached/out (USD/1M) | 選定実費JPY(14本文) | 1記事セット単価JPY(Std+Adv) | 7記事セット合計JPY | 厳格版KP 1件JPY | 総合版KP 1件JPY |
|---|---|---|---|---|---|---|---|---|---|
| gpt-6-luna | 13,556 | 27,618 | 24,243 | 0.10/0.01/0.50 | 2.426 | 0.347 | 2.426 | 0.035 | 0.051 |
| gpt-6.1-sol | 13,556 | 8,970 | 4,800 | 2.00/0.10/10.00 | 18.690 | 2.670 | 18.690 | 0.505 | 0.584 |
| gemini-3.1-flash-lite | 12,744 | 4,179 | 0(既定) | 0.25/0.025/1.50 | 1.513 | 0.216 | 1.513 | 0.024 | 0.045 |
| gemini-3.5-flash-lite | 12,744 | 5,234 | 0(既定) | 0.30/0.03/2.50 | 2.705 | 0.386 | 2.705 | 0.056 | 0.090 |
| claude-haiku-5-5 | 18,080 | 31,710 | (分離値なし、出力に包含) | 0.10/0.01/0.50 | 2.826 | 0.404 | 2.826 | 0.041 | 0.058 |
| claude-sonnet-5-5 | 18,080 | 23,618 | (分離値なし、出力に包含) | 2.00/0.10/10.00 | 43.574 | 6.225 | 43.574 | 0.623 | 0.822 |

- 単価出典: Luna/Sol=`pricing_snapshot.json`・`er009:30,34`、Gemini 2種・Haiku/Sonnet 5.5=公式pricingページ(2026-10-22取得、raw html sha256は`er098_kp_six_model_trial_01_common.py` `PRICES`およびExcel「条件・Prompt」)。全6モデル単価確認済み(未確認なし)。
- **既存Production Key Phrase選定の実費(別方式・実測)**: selector(`gpt-6-luna` DB hybrid)の記録`cost_jpy`合計 JPY8.115(14本文=1記事セット平均1.16)+canonicalization(raw_usage_logのtoken x 単価で再計算)JPY4.683(同0.67)=**1記事セット平均 約JPY1.83**。記事Gのみ`gpt-5.6-luna`世代(単価0.20/0.02/1.20で再計算)。抽出元はExcel「費用サマリ」下表・`inputs/manifest.json`。
- 独立評価費用(選定費用とは別): Sol JPY47.588(14回, 入力25,917/出力24,559[推論9,271])、Sonnet JPY87.273(14回, 入力33,144/出力47,917)。計JPY134.861。
- **Trial実費合計: JPY206.596**(選定JPY71.735[pilot6回込み]+評価JPY134.861、疎通専用の別呼出なし=pilotを84回の一部として採用、台帳`paid_calls.jsonl` 112件)。案件Cap JPY300の範囲内(69%)。日次(JST 2026-10-22): 既使用約JPY258+本Trial JPY206.6=約JPY465(C-3進行中分は別)で日次1,000円以内。
- 所要時間(1呼出の平均): Luna 22.0s / Sol 20.0s / Gemini3.1 1.9s / Gemini3.5 2.0s / Haiku 10.9s / Sonnet 13.1s。

## 6. 現行Lunaから変更する価値があるかのPM向け考察(事実材料。採否の推奨はFable記入)
- **同一Prompt・本文条件での現行Luna(`gpt-6-luna`)**: 5語以内100%・本文一致100%・自己申告語数の不一致0・5件を毎回出力。総合版合格率68.6%(48/70)、実費は記事セット当たり約JPY0.35と最安級。厳密規則の面では欠点が見当たらず、『学習価値』の面で平易な説明句が混ざる(padding率42.9%)。
- **品質(総合版合格・主評価)で上回るのはSonnet 5.5(75.7%/0.777)とHaiku 5.5(71.0%/0.745)**。ただし差は小さい(Lunaとの差は総合版合格で+5件/+1件相当、主評価で+0.045/+0.013)。評価者間のぶれが同程度のため、標本14本文では品質差が確定できない。Sonnet 5.5の実費は記事セット約JPY6.2でLunaの約18倍。Haiku 5.5は約JPY0.40でLunaと同程度(約1.2倍)。
- Sol 6.1は総合版合格率が最も高い(86.5%)が候補数が少ない(平均2.64件/セット)。『5件選定』を満たす点では不利で、1記事セット約JPY2.7(Lunaの約8倍)。
- Gemini 2種は安価(約JPY0.22/0.39)だが、**5語超(G3.1: 4件)・本文に無い言い換え・活用形変更(G3.5: 16件)・語数の自己申告ミス**など指示遵守に弱点。
- **現行Production方式との比較は方式差込み**: 現行のKP選定+canonicalizationは記事セット約JPY1.83。本Trial方式(全文渡し)のLunaは選定のみで約JPY0.35だが、canonicalization・Standard/Advanced別の日本語gloss・QAなど後続工程は本Trialの範囲外(未評価)。Productionの出力は原形化・短縮により厳密規則では67.1%しか本文一致にならず(活用形のみ相違21件)、これは仕様差であって不具合ではない。
- 本Trialで未検証: 1本文1回生成のため生成ばらつき、KP DB(`kp_english_lock`等)との整合、日本語glossのTTS・ASR工程、5件固定仕様(4+1 role構成)の扱い。方式をPrompt全文渡しへ変えるかは別途設計判断(Fable11-3条件A等)になる。

## 7. Fableによる独立レビュー・Trial Closeout
(Fable記入欄)
- 最終Status(VALIDATED / REJECTED / USER_DECISION_REQUIRED):
- Opus独立レビュー要否(採用提案時は条件C):
- ユーザー判断に回す事項:
- 備考:

## 8. 追加報告(委任文§3-8の必須項目)
### 8-1. 開始前チェック対応表
`TRIAL_DESIGN_01.md` 1節。未反映0件を確認して有料呼出を開始(STOP確認rc=0、全6モデルmodels list実在確認、単価全確認、疎通=pilot[A_Standard x 6]を84回の一部として採用)。
### 8-2. Prompt調整の事後報告(指示2 §3の4項目)
- 変更前: ユーザー指示1 §4のPrompt本文のみ(記事本文の渡し方の規定なし)。
- 変更後: Prompt本文は**1字も変更せず**、直後に `\n\n---\n\n【記事本文】\n` と記事本文(`article.md`全文)を追加。全6モデル・全84回で同一構築(`prompt_sha256`が全84 runで一致 = `4360c9cccee8765543b7ecc8d7e9dc60f73754951803e86383e24ac286b6921d`、user messageがPrompt本文で始まることも全runで確認)。
- 変更理由: Promptは記事を別途与える前提の文面で、記事本文の受け渡し位置が必要なため(指示2 §1「データ受け渡し方式との整合に必要な文言調整」)。
- 選定条件・品質基準への影響なし: 条件1〜6・優先順位・出力直前の再確認指示・語数併記指示は文字列として不変。区切り線と見出しの追加のみ。出力形式の指示は追加していない(解析はValidator側)。
### 8-3. 公平条件と差異
system=なし、user=Prompt+記事の1メッセージ。温度・推論設定は全社provider既定値(未送信)。max出力token=16,000を全モデル同一。差異(提供側仕様、記録のみ): OpenAI(Luna/Sol)は推論token(reasoning_tokens)が分離されて返る(Luna 24,243/14回、Sol 4,800/14回)。Gemini 3.x(3.1/3.5 Flash-Lite)は既定でthoughtsTokenCount=0。Claude(Haiku/Sonnet 5.5)は既定でthinking blockが付き(`thinking_blocks=1`)出力tokenに包含され分離値なし。APIは、OpenAI=Responses API、Anthropic=Messages API、Gemini=generateContent。
返却model ID: gpt-6-luna / gpt-6.1-sol / gemini-3.1-flash-lite / gemini-3.5-flash-lite / claude-haiku-5-5 / claude-sonnet-5-5(全84 runで指定と一致)。評価者の返却ID: gpt-6.1-sol / claude-sonnet-5-5。
### 8-4. 技術的失敗一覧
選定84回・評価28回ともに技術的失敗0件、API再試行0回。品質理由の再生成0回(5件未満・5語超・本文不一致の結果もそのまま掲載)。
### 8-5. 検証ツールの較正と限界(実行後に判明し修正した事項。API再呼出なし)
validate.pyの初期版で、(i)大文字placeholder(`A`/`B`)が小文字化されて検出されなかった、(ii)語内`~`(`~-led`)の正規表現生成、(iii)活用形判定の語幹処理(`passes`等)、(iv)同一原文の繰り返し出現を『複数該当』と誤判定、を検証ツール側で修正し再検証した(モデル出力は不変、評価者へ渡した候補文字列も不変)。最終集計は修正後。Production KPにも同じ規則を適用して妥当性を確認。限界: 『一般化の妥当性』(例: `something`が`what`を置換)は機械では存在確認のみで、評価者rubricのG項目で判定。
### 8-6. 分類候補(最終分類はFable)
`USER_DECISION_REQUIRED`候補(`VALIDATED`ではあるが採否はユーザー判断が必要な性質)。根拠: Trial自体は計画どおり完了(技術的失敗0・費用Cap内・全項目記録)。厳密規則の遵守ではLuna/Haiku 5.5/Sonnet 5.5/Solが同等(100%)で、Gemini 2種は劣る。品質(総合版・主評価)はSonnet 5.5が最良だが差は小さく、費用はLunaの約18倍。方式差(全文渡し vs 現行DB hybrid)があり、採否(モデル変更/方式変更)はProduction採用判断となるためユーザー決定事項。`判断候補`: 現行Lunaを維持するか、Haiku 5.5等へ変更するか、Prompt全文渡し方式を別Trialで評価するか(区分D: 新規の採否判断、Fable経由)。
### 8-7. 再現
```
.venv\Scripts\python.exe er098_kp_six_model_trial_01_extract.py
.venv\Scripts\python.exe er098_kp_six_model_trial_01_run.py --out er098_output/kp_six_model_trial_01 --manifest er098_output/kp_six_model_trial_01/inputs/manifest.json --cap-jpy 300 [--units A_Standard] 
.venv\Scripts\python.exe er098_kp_six_model_trial_01_validate.py
.venv\Scripts\python.exe er098_kp_six_model_trial_01_eval.py --cap-jpy 300
.venv\Scripts\python.exe er098_kp_six_model_trial_01_excel.py
```
実行は有料のため既存`runs/`・`eval/`があるとスキップ(再課金防止)。Production(`er030_*`等)は一切importしない。

# RESULT_01: One Step Further 品質検証Trial(ONE-STEP-FURTHER-CORNER-TRIAL-01 委任_01、2026-10-30)

Status: Trial完了。Closeout案=**VALIDATED(条件付き)**。新コーナーの採否・現行ニュアンス解説の扱い・表示=ユーザー判断(UDR #225、Fableが提示)。Production未変更。
比較ページ(学習コンテンツ本体)=`user_test/one_step_further_trial_01/index.html`、開発ログ・内部評価(分離)=同`dev_log.html`。設計=`TRIAL_DESIGN_01.md`。生成物・費用ログ=`out/`(`usage_log.jsonl`、`*__v1|v2__s1|l1|l2.json`、`*__AUDIT.json`、`raw/`)。

## 1. 結論(先頭)
- 3記事(Y姓・X AIの島・Z告げ口心臓)×Std/Adv全6セルで、主候補(gpt-6.1-sol・Prompt v2)の表現は独立監査で学習価値が平均5.00(v2 sol、監査n=7)/solの全採点4.93(n=15、3以下0件)。同じ基準で採点した現行ニュアンス解説は2.3〜2.5(n=6、全て3以下)。ユーザーの狙い(「聞いたことはあるが自分では使えない」「覚えたい」)に近い内容を、Family・レベルをまたいで出せた。
- 捏造0件(監査45件中0、筆者目視でも主候補8件の着想文は本文の記述で裏付け)。KP/文法との重複0件(機械検査56項目中0、監査0)。
- 費用: 主候補sol=1記事セット約¥6.5(70円目標の9%)、本番ラインluna=約¥0.4〜0.5(0.5〜0.7%、現行ニュアンスの1記事セット¥0.47と同水準)。時間は1セル約25〜37秒(2レベル並列)。
- 弱点(正直に): (1)**選定する表現は生成ごとに入れ替わる**(同条件の複数生成で同一表現になったのはZ Adv `read too much into`、X Std v1の`come in handy`など一部。品質の水準は保たれるが、表現そのものの再現性は低い)。(2)lunaは学習価値が高め(4.2)でも、v2でStandardに難しい表現(`come to terms with`、`make a case for`)を選びレベル適合が3.7に下がった。(3)有料枠¥60に到達したためv3(luna向けStd調整)は未検証。(4)監査者はsol自身(sol生成物の採点に自己評価の甘さがありうる)。最終判断はユーザーが読んで行う。

## 2. 主候補の選定表現(gpt-6.1-sol・Prompt v2。ページ上部に掲載)
| 記事/Lv | 表現(核) | 基本→発展 | 学習価値 | 正確性・自然さ | 関連 | レベル | 備考 |
|---|---|---|---|---|---|---|---|
| Y Std | `it's not my decision to make` | `you should decide`→`I'm worried about it, but it's not my decision to make.` | ○(5) 心配と決定権を分ける定型。使い所が多い | ○(5) | ○ 第3の話者「本人たちが決める」 | ○ | 「無関心にも聞こえうる」点をmeaning_shiftに明記 |
| Y Adv | `make something about someone` | `think only about my own feelings`→`I don't want to make their decision about me.` | ○(5) 「自分中心の話にしない」は日本語から出にくい | ○(5)。例文はやや硬い(`make this about me`の方が自然との指摘あり) | ○ 母親の「受け入れたい」 | ○ | |
| X Std | `give someone something to work with` | `they can help me`→`they give me something to work with.` | ○(5) 「不完全だが足がかり」 | ○(5) | ○ リセット後も残るメモ | ○ | |
| X Adv | `have something to show for ...` | `we made some progress`→`at least we have something to show for all that work.` | ○(5) | ○(4。「労力に見合う成果が十分ある」と言い過ぎない注意が必要) | ○ | ○ | 長文で核を取り出しにくいとの指摘 |
| X Adv | `see where something takes someone` | `I'll try this`→`I'll see where this takes me.` | ○(5) 日本語から出にくい発想 | ○(5) | ○ 課題も報酬も無いAIの探索 | ○ | |
| Z Std | `let something show` | `I'm nervous.`→`I'm nervous, but I'm trying not to let it show.` | ○(5) 感情を表に出さない | ○(5)。letの説明がやや回りくどい | △〜○ 語り手が警官の前で平静を装う場面 | ○ | |
| Z Adv | `read too much into something` | `I think she's upset because her reply was so short.`→`I may be reading too much into her short reply, but ...` | ○(5) 解釈への留保 | ○(5) | ○ 警官の笑顔を嘲りと受け取る語り手 | ○ | 6生成中4回(v1 luna・v2 sol・v2 luna×2)で選ばれた最頻出 |
(評価の○は筆者目視+独立監査の整合。学習価値の最終判断はユーザー。)

## 3. 条件別の独立監査(1〜5点平均。sol匿名・順序シャッフル、`dev_log.html`に全案)
| 条件 | n | 学習価値 | 正確性 | 日本語 | 関連性 | レベル適合 | 捏造 | KP重複 |
|---|---|---|---|---|---|---|---|---|
| v2 sol(主候補) | 7 | 5.00 | 4.86 | 4.71 | 4.71 | 4.71 | 0 | 0 |
| v1 sol | 8 | 4.88 | 4.75 | 5.00 | 5.00 | 4.88 | 0 | 0 |
| v2 luna(1回目) | 10 | 4.40 | 4.60 | 4.20 | 4.50 | 3.70 | 0 | 0 |
| v2 luna(2回目) | 11 | 4.09 | 4.45 | 4.36 | 4.82 | 3.64 | 0 | 0 |
| v1 luna | 9 | 4.22 | 4.56 | 4.67 | 5.00 | 4.44 | 0 | 0 |
| 現行ニュアンス(Y採用文) | 2 | 2.50 | 3.50 | 4.50 | 5.00 | 4.00 | 0 | 0 |
| ニュアンス改善Trial v3(X/Z) | 4 | 2.25 | 4.25 | 4.00 | 5.00 | 4.00 | 0 | 0 |
- 注: v2 solはn=7(Y std1/Y adv1/X std1/X adv2/Z std1/Z adv1)の合計で、dev_log.htmlと同じ。Std/Adv別(sol全体): Std学習価値5.00・Lv適合4.67、Adv 4.89・4.89。
- ニュアンス解説は「本文の表現の含みを解く」コーナーで、「覚えて使いたいか」を目的とする本採点基準には元々不利。この比較は『ユーザーが求める学習体験に近いか』の評価で、ニュアンス解説の優劣そのものではない(比較対象にしたX/Zは現行より改善済みのTrial v3)。

## 4. v1→v2(欠陥の種類ごとの変更と効果)
- v1の欠陥: (a)言い換え型(`come in handy`=`useful`の同義置換が6生成中4で選ばれた)、(b)学校英語の頻出熟語(`jump to conclusions`、`pay off`)で新味が薄い。
- v2の変更: 「言い換え型でないか」「新鮮味」の2条件追加+ポイントへ「基本表現では言えない点」「日本語話者の間違えやすい点」。
- 効果: sol=学習価値4.88→5.00、`come in handy`・`jump to conclusions`は0件に(`give someone something to work with`、`let it show`などへ)。luna=学習価値4.22→4.40/4.09と横ばいで、**Std向けの難易度が上がりレベル適合が4.44→3.7に低下**(副作用)。改善効果は主にsolで、lunaには別手当(Std向けレベル上限の明示)が要る。v3の検証は費用枠到達のため未実施。

## 5. Standard / Advanced の品質差と再現性
- 品質差: sol v2はStd 5.00/Adv 4.89でほぼ同等。Stdは日常の短い表現(`let it show`、`it's not my decision to make`)、Advは一段抽象的(`make something about someone`、`have something to show for`)で、レベル差は選定に表れた。lunaはStdの方が学習価値は高い(4.47)がレベル適合が低い(3.73)=難しすぎる選定が出る。
- 再現性(`dev_log.html` 表3): 同条件(v2 luna 2回)で1件以上の表現が一致したのはZ Adv `read too much into`のみ(Y Stdは`make it all about someone`/`make this about me`と同じ型)。v1のX Stdは3生成とも`come in handy`で一致。ただしテーマ傾向(Y=他人の選択への向き合い方、Z=解釈・緊張)は安定し、品質(学習価値4以上の比率)は全生成で維持された(luna 30案中LV≤3は4件=13%、sol 15案は0件)。表現を固定して再現したい場合は、選定を決定的にする仕組み(候補を多めに出させて固定選別する等)が別途必要。

## 6. 既存Key Phraseとの重複
- 機械検査(核表現とKP/Word全件・本文の突合、発展文へのKP混入、参考6例の使用): 全6セル×5生成(v1/v2×sol/luna)の56項目で問題0。監査のkp_overlap=true 0件。
- 文法解説との重複: Y/Xは文法候補の見出しを入力に与えて回避(重複0)。Zは文法が「該当なし」のため重複判定自体が不要。
- 補足: Y Advの`make something about someone`は`hold someone back`等のKPと別。X Stdの`give someone something to work with`と本文`worth paying attention to`も別。

## 7. 生成時間・費用・量産単価への影響(`out/usage_log.jsonl`実測)
| 条件 | 1セル費用 | 1記事セット(2Lv) | 70円比 | 1セル秒 | 入力tok | 出力tok |
|---|---|---|---|---|---|---|
| v2 sol | ¥3.27 | ¥6.54 | 9.3% | 36.9 | 2,521 | 1,538 |
| v1 sol | ¥2.91 | ¥5.81 | 8.3% | 33.6 | 2,216 | 1,373 |
| v2 luna(1回目) | ¥0.184 | ¥0.37 | 0.53% | 26.3 | 2,521 | 2,094 |
| v2 luna(2回目) | ¥0.248 | ¥0.50 | 0.71% | 33.8 | 2,521 | 2,758 |
| v1 luna | ¥0.177〜0.178 | ¥0.35 | 0.5% | 22〜23 | 2,216 | 1,889〜2,034 |
- 独立監査: 3回 ¥18.17(各約¥6)。Trial総費用 **¥59.93**(呼出39回: 生成36+監査3)。当初の通常上限¥40を、独立監査(委任の必須項目)実施のため¥60まで使用(委任文の許容範囲内)。
- 量産単価への影響: 現行ニュアンス解説と置き換える場合、lunaなら+約¥0〜0.03/セット(現行¥0.47に対し¥0.37〜0.50)。solを使うと+約¥6/セット(70円目標の約9%)で、品質向上分との費用対効果はユーザー判断。再試行1回を許す設計なら上限は2倍。
- 時間: 1セル約25〜37秒、6セル並列でwall約48秒。ニュアンス解説(約20秒)よりやや長い。

## 8. 現行ニュアンス解説との学習価値比較
- Y姓記事Std: 現行の`at least a little`解説(「最低ラインを示しつつ要求を控えめに響かせる」)は本文の読解に閉じ、監査の学習価値3、「要求を弱めるのは主にa littleで混同」との指摘。新コーナーは自分の言いたい場面(`it's not my decision to make`)にそのまま使える。Adv `at least`は学習価値2(known_to_most=true)。
- X/Z(改善Trial v3): 学習価値2〜3(`everything vs almost everything`は1、既知)。新コーナーは4〜5。
- ただし『本文の中の含みを深く理解する』価値はニュアンス解説独自のもので、置換か併存かはユーザー判断(併存だと1記事セットの学習項目が増えHR負荷も増える)。

## 9. 受入条件(委任文§7)の自己確認
1. 学習価値: sol v2は6セル全てLV≥4(○)。luna v2は一部Stdで弱い(△)。 2. 発見: 「自分では出てこない」型(`see where this takes me`、`let it show`、`it's not my decision to make`)を確認(○、最終はユーザー判断)。 3. 正確性: 4〜5、軽微な注意(`have something to show for`の成果の量、Zのletの説明)あり(○)。 4. 日本語の簡潔さ: point_ja≤130字、監査4.7(○)。 5. 関連・捏造: 0件(○)。 6. KP/文法重複: 0件(○)。 7. 他Family・レベルでの再現: 品質は再現(○)、表現は再現せず(△)。 8. 時間・費用: 測定済み(○)。
→ Closeout案: **VALIDATED(条件付き)**。条件=(a)主生成モデルの選択(solは高品質だが約¥6.5/セット、lunaは¥0.4〜0.5でStd難度制御が要追加検証)(b)表現固定の再現性は未達 (c)ユーザーが比較ページを読んで「覚えたい」と判断すること。

## 10. 残る課題と正式採用時の論点
- 課題: 表現のぶれ、lunaのStdレベル適合、監査の自己採点バイアス、v3未検証(luna向けStd上限規則の追加+再検証にluna 6セル約¥1.2+監査約¥6が必要=¥60枠超のためFableへ報告)。
- 採用時の論点: (1)ニュアンス解説の廃止か併存か(UDR #224=ニュアンス改善Trial採否との関係を整理) (2)表示位置・分量(1レベル1〜2件) (3)HR(Human Review)で提示する単位・事前チェック項目(新規の捏造/KP重複/レベル適合のgate) (4)既存公開記事への遡及適用の可否・費用 (5)主生成モデル(sol/luna)とレベル別難度制御、再試行・Gateとの整合 (6)Production実装範囲(Prompt新設・sidecar保存・ページ描画・QA gate)と重要変更のOpus独立レビューGate(条件C) (7)本Trialはreview 未実施のため、採用提案前にFable/Opus独立評価が必要。

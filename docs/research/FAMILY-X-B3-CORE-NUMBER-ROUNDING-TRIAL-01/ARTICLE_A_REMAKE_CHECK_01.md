# 記事A 新text(run_pp_02) 丸め0件の事実確認 + Advanced s10 Fact整合確認(委任_07)

作成: 2026-10-22。調査のみ(コード・Prompt・旧run・run_pp_02の本文/overlay 無変更)。事実と推測は「推測」と明記して分離。
費用: Luna low 3回(各 input 3,869 tok / output 657・751・669 tok)。APIは費用を返さないため、cost.jsonの実測(同入力 475 out = JPY0.100)とTrial 2(4 call JPY0.923)から線形推定し **約JPY0.35**(上限JPY2以内。推定値であり計量値ではない)。
証跡: `er019_output/paycheck_personality/run_pp_02/audit/judge_stability_01.json`(3回再実行)、同 `p11_supplement_prompt_match_01.json`(D、API 0)。

## A. 丸め0件の原因切り分け

### A(1) 中核数値の比較(事実)
| 項目 | 旧B3(run_pp_01) | Trial 1/2 の記事A | 新B3(run_pp_02) |
|---|---|---|---|
| 採用Fact ID | F02,F04,F07,F08,F15 | 同左 | 同左 |
| Fact本文(【】印除去後sha256) | fb91b21a… | fb91b21a… | fb91b21a…(3者完全一致) |
| annotation.json の numbers/class/concept/notes | 9件(core: 11件,最大134,515人,134,515人,3回以上,0.0630) | 同左 | 同左(完全一致) |
| 134,515人のFact文脈 | F04「解析に含まれた参加者数は最大134,515人で、解析ごとに異なる」 | 同左 | 同左 |
| Ledger sha256 | a31992b5… | a31992b5… | a31992b5…(同一) |
| **Storyline行** | 「大規模な縦断データで安定した個人差と個人内の変化を分けて分析すると…」 | 同左 | 「**11件【中核数値】の縦断研究の統合分析で**、収入と勤勉性には個人内の小さな双方向の関連が見つかったが、観察データに基づくため因果関係とは断定できない」 |

134,515人は旧/新とも中核数値(concept C2、surface「最大134,515人」「134,515人」)で、文脈(最大解析標本数)も同じ。**差はStoryline行のみ**(新B3=storyline_b3段をSolで再生成、費用JPY11.305)。judge Promptを再構成し、Trial 2 art_a31992b5のPromptとdiffすると差はline 91(Storyline)の1行だけ。再構成Promptのsha256は実run記録 `a660304e…` と完全一致(再現性確認済み)。

### A(2) 実runのLuna判断(overlay記録、事実)
- C2「最大134,515人/134,515人」: llm=EXACT_REQUIRED。理由=「これは解析に含まれた最大標本数であり、『最大』という限定と正確な人数を保つ必要があります。概数化すると最大値の記録としての精度が失われます。」
- C1(11件)・C4(3回以上): EXACT_REQUIRED(研究数/閾値)。
- C5「0.0630」: **llm=APPROXIMATE_OK**(「約0.06としても小さな正の関連という解釈を保てます」)→ V7(同Fact内の0.0589と約0.06で衝突)で final=EXACT_REQUIRED に降格。
- 実runのusage: input 3,869 / output 475 / **reasoning_tokens 0**。

### A(3) Trial 2 との比較(事実)
同一入力クラス(Prompt v2、art_a31992b5、Storyline以外同一):
| 試行 | C2 判断 | C5 llm→final |
|---|---|---|
| Trial 2 luna low rep1/2/3 | APPROX ×3 | APPROX→V7でEXACT ×3 |
| Trial 2 luna medium rep1/2 | APPROX ×2 | EXACT/EXACT(LLMが衝突を理由にEXACT) |
| Trial 2 luna high rep1 | APPROX | APPROX→V7でEXACT |
| **run_pp_02 実run(新Storyline)** | **EXACT** | APPROX→V7でEXACT |

Trial 2のC2理由は「1人単位の精度は聞き手に重要でない。『最大』は表記に残す」型。実runの理由は「最大値の記録としての精度」型で、同じ「最大」を正反対に評価している。

### A(4) 安定性の実測(追加3回、新Storyline・実runと同一Prompt)
| 回 | C1 | C2 | C4 | C5(llm→final) | reasoning tok | 秒 |
|---|---|---|---|---|---|---|
| rep1 | EXACT | **APPROX**(最大約13万5千人/約13万5千人) | EXACT | EXACT→EXACT | 175 | 8.2 |
| rep2 | EXACT | **APPROX** | EXACT | EXACT→EXACT | 210 | 7.7 |
| rep3 | EXACT | **APPROX** | EXACT | EXACT→EXACT | 161 | 6.3 |

- C2は新Storyline下でも3/3 APPROX。実run(EXACT)と合わせて新Storylineでは3/4 APPROX、旧Storyline(Trial 2、6回)と合わせると同一Fact・同一Promptで 9/10 APPROX。
- C1/C4は全回EXACTで安定。C5は再実行では全回llm段階でEXACT(実runのみAPPROX→V7降格)。C5の最終結果はどちらでもEXACT。
- 観察のみ: 実runはreasoning_tokens=0の呼出。Trial 2 luna low 54 callのうち0は6件(11%)で、0件callのAPPROX率 10/22 vs 非0 68/191 と偏りは見えない(n小、因果は言えない)。

### A(5) 結論
- B3文脈の変化: **寄与なし(0%)**。中核数値・Fact・Ledger・注釈は完全同一、差はStoryline1行のみで、再実行3/3がAPPROXなのでStoryline差で説明されにくい。
- V7等の決定論ゲート: **C2には無関係(0%)**。C2はllm段階でEXACTだった(降格記録なし)。V7が働いたのはC5(0.0630)のみで、再実行ではLLM段階でEXACTになるため丸め0件の主因ではない。
- Luna判断の揺れ: **主因(推測: ほぼ100%)**。同一Promptで9/10 APPROX、1/10 EXACT。ただしn=10で、Storyline差の小さな寄与を完全には排除できない(推測)。
- 含意(事実): overlayは同一B3版で確定値として再利用される(`run_core_number_rounding`の冪等仕様、er095_b3_core_number_rounding_01.py:595-)ため、run_pp_02の0件は再判断(force_rejudge)しない限り固定される。

## B. 新textの内容変化(事実のみ、優劣判断なし)
Fact Ledgerは同一。B3の採用Fact(F02,F04,F07,F08,F15)もFact本文も旧/新で完全一致。B3が別のFact構成を選んだのではなく、Storyline行の変更とそれを受けたWriterの揺れ。

| 項目 | 旧JA(run_pp_01 revision2) | 新JA(run_pp_02 revision2) |
|---|---|---|
| タイトル | 「稼ぐ性格」を探せ！ と思ったら、主役は「前の自分」だった | 給料が上がると、まじめさもアップ？ 比べる相手は「いつもの自分」 |
| 冒頭 | 「まじめになれば、もっと稼げる？」/「それとも、稼げるようになると、まじめになる？」 | 「まじめに働けば、給料が上がる」→「給料が上がると、まじめになる」はどうだろう(“逆向き”に注目) |
| 11件 | あり(大規模調査) | あり(同じ人を長く追った11件) |
| 最大134,515人 | **あり**(「最大134,515人」+解析ごとに異なる) | **なし**(人数言及なし) |
| 3回以上 | あり(「同じ人の収入と性格を3回以上」) | あり(全角「３回以上」、「性格と収入をそれぞれ」) |
| 0.0630/0.0589/1.30年 | なし(「小さなプラスの関連」) | なし(「少し高い」「小さい」) |
| 双方向+小さい | あり | あり(「逆向きの車線」) |
| 個人間差/個人内変化の分離 | あり | あり(「いつもの自分」比較) |
| 因果不確定/第三変数 | あり | あり |
| 年齢調整(F15の一部) | なし | なし |
| 勤勉性の説明 | 「まじめに物事に取り組む性格」 | 「まじめさ」 |
| 末尾 | 自分の続編を読む | 連続ドラマの主役はあなた自身 |

数値監査(rounding_text_audit_01.json): 新JAの数値トークンは 11, 3 のみ(EXACT_CORE)。UNAUTHORIZED 0。

## C. Advanced s10 のFact整合疑い(修正なし)

### C(i) 原Factと文
- 文(Advanced s10、`run_pp_02/b1b/article.md`): "In every study, personality and income were each measured at least three times."
- F07: 「収入とBig Fiveの**少なくとも1特性**を縦断的に3回以上測定することなどを適格条件とし」(numeric_value: 最低3測定波、適格条件)。F06: 「各研究…測定波は3～18回」。F04 conditions: 「参加者数はBig Five各特性と収入の解析ごとに異なる」。F13: 5特性それぞれの結果を記載。
- Ledger内に「全Big Five特性が全研究で3回以上測定された」という記述はない。一方、文は "personality"(総称・不可算)で "each trait / all five traits" とは書いていない。RF(luna-A4, conf 0.32)の読み(各特性すべて)は文の一解釈であり、文自体が各特性と明言しているわけではない。
- 判定(事実の範囲): 「各特性が3回以上測定」はこの文の字面にはない。Ledgerは「少なくとも1特性が3回以上」までしか保証せず、総称"personality"がそれ以上を含意するかは**曖昧(真の逸脱と断定できず、Ledger裏付けが完全でもない)**。確定判断はFable。

### C(ii) 同箇所のJA/Standard
- JA: 「どの研究でも、性格と収入をそれぞれ３回以上調べている」(run_pp_02/ja_writer/revision2.md:5)。
- Standard(a2): "Each study measured personality and income at least three times."(a2/article.md:5)。この文自体はStandardのRFではflagされていない(Standardのflagは別9件)。

### C(iii) Risk Flagger(run_pp_02、`review_queue/post_en/paycheck_personality__run_pp_02/`)
- Advanced(b1b): 2件。s10(上記、conf 0.32、luna-A4)/ s26 "not a story about more serious people earning more than others" が個人間差の扱いと食い違うのではという疑い(conf 0.58、luna-A3)。
- Standard(a2): 9件(s14,s17,s21,s27,s29,s31,s37,s38,s40)。要旨=「did not compare people」が"個人間差と個人内変化を分けた"と食い違うか(s14,s17,s29,s31)/因果を示唆する語(s27,s40)/一般化の過剰(s37,s38: "Low/High income does not mean…")/用語定義の追加(s21)。Luna A4中心、Gemini35FLは0件。

### C(iv) 旧run_pp_01
- Advanced: "In every study, the same people's income and personality were measured at least three times."(b1b/article.md:8)。RF(gemini35fl-A3, conf 0.7)が同位置を「同一人物が全研究で3回以上」と読めると指摘(別の読み)。Standard(a2 s12、conf 0.3)でも同位置がflagされていた。旧JAも「同じ人の収入と性格を3回以上調べた調査」。
- つまりこの言い回しは旧/新どちらのrunでもRF候補に挙がる既存パターンで、新run固有の新規逸脱ではない。

### C 現行Production仕様での扱いと是正経路
- RFは非Blocking(CURRENT_SPEC.md:1190「合否判定せず・記事を書き換えず・自動Rewrite/retryなし」)。flagがあっても停止せずReview Queueに保存されHuman Review待ち。
- 是正経路(逸脱と判断された場合): 英訳(Advanced→Standard派生、`a2/audit/derived_from_advanced_sha256.json`)の再生成。費用(run_pp_02 cost.json by_stage): advanced JPY0.264 + standard JPY0.267 + RF(b1b 0.965 + a2 1.128 = 2.093)= 約JPY2.6。ただしJA自体が同じ総称表現を含むため、英訳のみの再生成ではJAと英語が乖離しうる(JAも直す場合はWriter再実行 w1_r0 8.001 + r1 3.131 + r2 2.611 = 約JPY13.7が別途)。再生成で表現が確実に変わる保証もない(推測)。**修正は行っていない**。

## D. P-11(2)補完の妥当性
- 現状の補完(`audit/p11_check_01.json` の仮定概数によるoffline Prompt組立)は「規則8+【概数表記】行が入る経路」の構成証拠としては十分だが、仮定(Lunaの判断ではない)に基づく。
- **API 0 の強い補完(今回実施)**: Trial 2 phase2のafter armで、実Luna判断(response_id一致)からProduction経路(`er095.build_overlay`→`news_field_for_writer`→`w1.build_r0_prompt`)でR0 Promptを組立て、Trial 2の実Writer runが使ったR0 Prompt sha256と比較(`audit/p11_supplement_prompt_match_01.json`):

| art | 概数可(Production経路) | Production経路sha | Trial実Writer sha | 一致 |
|---|---|---|---|---|
| art_a31992b5(記事A) | 1概念(2 surface) | c6c4ad31… | c6c4ad31… | **一致** |
| art_701612d8 | 2概念 | f7fc5069… | f7fc5069… | **一致** |
| art_36b2c87d | 0(Trial時1: V8bで降格) | 1c9e857b…(=概数なし) | f98b6c90… | 不一致 |
| art_9bd6834e | 2(Trial時3: V7/V8/V8bで降格) | 4ab0755c… | f253a839… | 不一致 |

  不一致2件は、Production gate(V7/V8/V8b)がTrial時より厳しく降格した結果であり、安全側の差(想定通り)。
- 記事Aではその実Writerが「13万5千」「135,000」を指定どおり使用し、UNDESIGNATED/UNAUTHORIZED 0(phase2_summary.json audit)。つまりProductionと同一バイトのPromptで、実Writerが概数を使った証拠がAPI 0で得られた。
- 限界(事実): これは「Prompt組立の同一性」であり、runner W1〜W6の呼出配線を実runで通した証拠ではない。実run証拠が必要なら:
  - 案1: 記事Aをforce_rejudge(`--regenerate-stage writer`)で再実行 = judge約JPY0.1 + Writer R0〜R2 約JPY13.7 + EN/RF 約JPY2.6 = 約JPY16(再判断は9/10 APPROXなので概数≥1件になる確率が高い、推測)。
  - 案2: 他記事のR0のみ1回 約JPY8(w1_r0実績8.001)。R1/R2・overlay永続・resume経路は通らない。
  - 案3: 追加実走なし(上記API 0証拠+C-2のRegression全PASSで足りるとFableが判断)。

## 次の一手の候補(改善見込みの自己評価)
1. 記事Aで概数入りが必要ならjudgeのみforce_rejudge(約JPY0.1、概数≥1が出る確率は約9/10、推測)→Writer再実行(約JPY16)。判断が必要なのは「0件でも承認可能か」という品質判断(Fable/ユーザー)。
2. 0件を許容(丸め判断は安全側EXACTで正しく動作済み)。費用0。
3. 揺れの恒常対策(例: 同一入力で2回judgeし一致のみ採用)は新仕様候補。実装せず報告のみ。

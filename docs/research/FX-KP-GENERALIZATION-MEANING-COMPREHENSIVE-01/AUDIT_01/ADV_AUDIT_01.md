# ADV_AUDIT_01: Advanced英語説明の検証実態とNG原因(FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_10、API 0・新規生成0・コード変更0)

生成=`AUDIT_01/audit_01_build_adv.py`(読み取り専用集計)。生データ=`er112_output/kp_gm_trial_02/results.jsonl`(以下T2)・`er112_output/kp_gm_trial_03/results.jsonl`(T3)。行番号=各jsonlの1始まり行。

## 0. 結論(先頭)

1. **「59/60」と「120件で伝染0」は別物で、母集団・判定者・Std誤り入力の有無が異なる。** 59/60=難例20KP×3回のAdv出力(Opus盲検、確定gold)。120件=通常40KP×Std 3方式のrep1 gloss(各1回)を入力にしたAdv出力(実行層Sonnetの目視、独立Judgeなし)。
2. **59/60の唯一のNGは Std意味の誤りに起因する(分類(i))**: `reach for someone's wallet` rep1。入力Std「人の財布に手を伸ばす」(盗む読み)の「人の」を引き継ぎ、Advが "another person's wallet to take or use it" と生成した。同一入力のrep2・rep3はPASS(支払いの準備)、gloss無し(E1)・正しいgloss(E0@G2/E0@G3)ではPASS。Adv生成の確率的ゆらぎも関与するため、Std誤り入力でも常に波及するわけではない。
3. **分母=Std意味が誤っていた出力、分子=Adv NGに波及した出力**: **A(難例20×3=60): 1/5**(Std誤りは `draw a line`「線を引く」2出力+`reach for someone's wallet`「人の財布に手を伸ばす」3出力。波及はreach rep1の1件のみ)。**B(通常40×3方式=120): 0/1**(Fable盲検でStd誤りと確定したrep1 glossは `an unseen clock` G0「目に見えない時計」の1件のみ。Advは字義を引き継がず)。「0/120」は分母が誤りで、**波及を測れる事例は1件**。Std薄(△)入力は2件で、誤り化は0件。
4. 「伝染0件」の根拠は**実行層Sonnetの目視**で、独立Judge・gold・複数rep・Std/Adv整合の正式Judge(kind P)のいずれも無い。
5. Std誤りが無い出力でのAdv NG: A=0/55、B=0/119(Std誤り以外)。ただしBには**Adv生成起因の欠陥が1件**(`run on` E0@G0が2義併記)あり、Stdは正のため分類(ii)。正式NG判定は未実施のため『欠陥』扱い。

## 1. 検証の一覧(ユーザー§2-1〜4)

| 項目 | A: 難例20 KP×3回(=60出力) | B: 通常40 KP×3方式(=120出力) |
|---|---|---|
| 出所 | T2 arm=`E0@G0`(行は付表A) | T3 arm=`E0@G0`/`E0@G2`/`E0@G3`(kind=E、各40行、付表B) |
| 独立KP数 / 生成回数 | 20 KP / 各KP3回(同一入力で再生成)=60出力 | 40 KP(重複なし)/ 方式3×各KP1回(rep1のgloss)=120出力。各出力は異なるStd入力に対する別条件 |
| KPの種類 | GOLD_LABELS_FINAL_01の用法列: 慣用句・比喩(figurative)11[draw a line, shine a light on, fire the starting gun, Carry the Load, brace yourself for, leap into action, take the wheel, on the throne, off the hook, turn on its head, jump to conclusions]・字義/用語(literal/literal-legal/term/collocation)6[pull someone under, sentence someone to death, refueling support, execution bell, letter of introduction, apply one's findings]・句動詞(phrasal)2[bring in, hold on]・figurative-literal境界1[reach for someone's wallet] | er112_kp_gm_kpset_03の型: 句動詞(P)10・慣用句/定型(I)11・コロケーション(C)11・名詞句/用語(T)8(`fable_blind_std_03.md`の型列) |
| X / Z | X16 / Z4(blind表の列) | X30 / Z10 |
| 使用Prompt | `er112_kp_gm_trial_02.py:250-253` `expl_message('E0')`=Production関数 `er019_family_x_kp_explanation_01.build_explanation_user_message`(同:154-175)をそのまま呼ぶ。DEVELOPER_MESSAGEも同モジュール定数(`expl_call` :266-272) | T3 `run_e0`(`er112_kp_gm_trial_03.py:137-160`)が `T.expl_call('E0', kp, g)` を呼ぶ=Aと同一経路 |
| PROMPT_SHA256との同一性 | **バイト同一ではない**。Prompt本文(定数・規則文)はProductionと同一だが、**1 KP/call**(ヘッダの件数語が "1 Key Phrase"、末尾 `x1`。`_header_for`/`_footer_for` :154-165)、schemaはDEV専用(`kp_expl_e0_trial02`、minItems/maxItems無し)。Productionの本番は1 callに5 KP(`PROMPT_SHA256`はn=5・5固定schemaから算出。現値 c3d3734b760af258b86020002ef8a1ab63e16633a72bdab45019ca5b7be6fa7e、`er019_family_x_kp_explanation_01.py:140-142`)。PROMPT_SHA256自体はT2/T3のresults.jsonlに記録されていない | 同左 |
| model / reasoning | gpt-6-luna(`kx.MODEL`)/ medium(`kx.REASONING_EFFORT`。コードが実行時に参照する値。results.jsonlには未記録) | 同左 |
| 入力条件 | 本文1文(`sent`)+KP+Std日本語意味(`gloss_in`)。**他のKPは同じcallに入らない**(1 KP/call) | 同左 |
| Std日本語意味の出所 | T2 G0 arm。`draw a line`のみrep対応(rep1/2/3=G0 rep1/2/3のgloss: 線を引く/一線を引く/線を引く)、他19KPは**3回とも同じG0 rep1のgloss**(`run_expl` :292、`res.get((gloss_arm,k,rep)) or res.get((gloss_arm,k,1))`)。したがってStd glossの独立サンプルは22(20KP+draw a line rep2,rep3) | T3 G0/G2/G3の**rep1** glossのみ(rep2のglossは未使用)。E行の`gloss_in`が同arm・同KPのG rep1と一致することを全120行で確認 |
| Adv判定者・基準 | **Opus盲検(OPUS_REVIEW_04.md:6)、Fable確定gold**。個別行の判定ログは未保存で、集計 E0@G0 59/60 のみ記録。NGの特定(reach rep1)は委任_10 §1(Fable)による | **実行層Sonnetの全件目視**(TRIAL_RESULT_03.md:16,54)。独立Judge無し。LLM Judge C(kind P等)は費用上限のため未実施 |
| Adv PASS / NG | **59 PASS / 1 NG**(Opus、集計値) | 公式報告: Std語義取り違えの伝染0・Std/Adv矛盾0・sense誤り0(Sonnet目視)。別所見: `run on` E0@G0 の2義併記1件。本監査の再目視(実行層、同一系統)も同じ結果。**正式なPASS/NG件数は無い** |
| Std意味の正誤(入力側) | 誤り5出力(2KP)/ 正55(うち`apply one's findings`3出力は要注意)/ 薄い=**未判定**(Opusの個別薄判定は未保存) | **Fable盲検でrep1 gloss 120中**: 誤り1(G0 `an unseen clock`)・薄2(G2 `price tag`、G3 `standard deviation`)・正117 |

## 2. NG原因別内訳(ユーザー§2-5)

| 原因分類 | A: 60出力 | B: 120出力 | 該当 |
|---|---|---|---|
| (i) Std意味の誤りに起因 | **1** | 0 | A: `reach for someone's wallet` rep1 |
| (ii) Adv生成自体に起因 | 0 | 正式NG 0(欠陥1: `run on` E0@G0の2義併記、Stdは正) | B欠陥は正式判定外 |
| (iii) 両方に原因 | 0 | 0 | Aの1件は(i)としたが、同一入力でrep2/3はPASSのためAdv生成のゆらぎも条件。(iii)と読む余地あり(分類は実行層の判断) |
| (iv) 原因特定不能 | 0 | 0 | |
| **NG合計** | **1(=59/60の残り)** | 0(正式) | |

(i)とした根拠(A、reach rep1): (a) 出力 "another person's wallet" が入力 "人の財布" の「人の」と対応(T2 行174)。(b) 同一KP・同一本文でgloss無し(E1 rep1)・正しいgloss(E0@G2: 行111 gloss「人が支払いに備えて自分の財布に手を伸ばす」、E0@G3: 行122 gloss「財布に手を伸ばす」)はいずれも"to get ready to pay for something..."でPASS(`REPRESENTATIVE_01.md` C表のE1・E4と、T2 行111・122)。(c) 一方、同一入力(rep2・rep3)でもAdvは"to get ready to spend money"(行167)、"to get ready to pay for something, often because you want to buy it"(行181)を生成し波及しなかった=Std誤り入力が波及の必要条件(推定)であって十分条件ではない。n=1のため因果は『強い状況証拠』にとどまる。

## 3. 59/60の唯一のNG(ユーザー§2-6)

| 項目 | 内容 |
|---|---|
| KP | `reach for someone's wallet`(X記事、gold用法=figurative-literal境界) |
| 本文の文 | "That's enough to make you reach for your wallet before the volume button" |
| 入力Std日本語意味 | 「人の財布に手を伸ばす」(G0 rep1、T2 行10。E0@G0の3回とも同じ入力) |
| Std意味の判定 | 誤り(盗む読み)。gold(GOLD_LABELS_FINAL_01.md、reach行)の「不可: 『盗む』解釈」。Trial_03でも同一文字列がFable盲検FAIL(FABLE_BLIND_RESULT_03.md:9) |
| Adv英語説明(原文、T2 行174) | "to move your hand toward another person's wallet to take or use it" |
| NG理由 | goldの許容="to take out money to pay for something (reach to get one's money)"。出力は「別人の財布へ手を伸ばし、取る/使う」で、gold『不可』欄の盗む解釈そのもの。入力の「人の財布」の逐語反映 |
| 同入力のrep2/rep3 | rep2(行167)"to get ready to spend money"、rep3(行181)"to get ready to pay for something, often because you want to buy it"=いずれもPASS(Opus) |
| 根拠 | T2 results.jsonl 行174(NG)・167・181。OPUS_REVIEW_04.md:6(E0@G0 59/60)。NG行の特定は委任_10 §1(Fable)による: **Opusの個別判定ログはrepoに無く、NG行の同定はFable記述に依存**。実行層の独立照合(60出力をgold『不可』欄と照合)でも該当は本行のみ(ただし結果を事前に知っていたため独立性は限定的) |
| Sonnet暫定(gold確定前)の同行 | 行174は sense_ok=0(暫定Judgeも不合格。REPRESENTATIVE_01.md C表 [0010]) |

## 4. 分母=Std誤り、分子=Adv波及(ユーザー§2・特に指定)

| 検証 | 母集団 | 分母: Std意味が誤りの入力を使った出力 | 分子: うちAdvが誤り(NG) | 波及率 | Std誤りでない入力でのAdv NG | 備考 |
|---|---|---|---|---|---|---|
| **A: E0@G0 難例20×3** | 60 | **5**(draw a line rep1・rep3「線を引く」、reach rep1〜3「人の財布に手を伸ばす」) | **1**(reach rep1) | **1/5** | 0/55 | Opus G0 Std NG2件(draw a line・reachと推定)に基づく。非波及4件はAdvが正しい意味を自力で生成(Opus『Std/Adv用法矛盾 G0+E0@G0 4件』と件数一致、内訳は未保存=推定) |
| A(感度): 要注意gloss込み | 60 | 8(+`apply one's findings`「人の研究結果を応用する」×3) | 1 | 1/8 | 0/52 | Fable T03基準(「人の研究結果」をFAIL)に揃えた場合。Advは"what someone learned..."でNGなし |
| **B: E0@G0/G2/G3 通常40×3** | 120 | **1**(`an unseen clock` G0「目に見えない時計」。Fable盲検FAIL) | **0** | **0/1** | 0/119(正式NG0。欠陥1=run on 別原因) | 『0/120』ではなく**波及を測れる事例は1件のみ** |
| B: Std薄(△)入力 | 120 | 2(G2 `price tag`、G3 `standard deviation`) | 0 | 0/2 | | 薄いStdはAdvを誤らせなかった |
| 参考 A': E0@G2 | 28行(うち難例22) | 0(Opus Std G2 26/26) | 0 | 測れない | 0/22 | 分母0 |
| 参考 A'': E0@G3 | 28行(うち難例22) | 0〜1(Opus Std G3「25〜26/26」。未特定) | 0 | 0/(0〜1) | 0/22 | Opus薄化指摘5件のうち難例は`brace yourself for`「～に備える」・`on the throne`「トップの座にいる」の2。Adv出力は正しい |

注: Opusの「E0@G2 22/22・E0@G3 22/22」の22の内訳は未記録。T2のE0@G2/E0@G3は各28行=難例20(rep1)+`draw a line`rep2・rep3(2)+通常6(rep1)。`summary_02.json`の22=難例20+通常のうちe4_normal30に含まれる2KP(behind the scenes・think up)で別母集団。以後の付表は『難例22(20+draw a line rep2,3)』を示す。通常6行のOpus判定は不明(未判定)。

## 5. 「伝染0件」の検査内容(ユーザー§2-7)

| 項目 | 内容 | 根拠 |
|---|---|---|
| 誰が | 実行層Sonnet(委任_08のagent)。独立Judgeではない | TRIAL_RESULT_03.md:16,54(「確認者=Sonnet agentによる全件目視であり独立Judgeではない」) |
| 何を | 通常40KP×3方式のrep1 gloss→E0説明(T3 kind=E、120行)の`gloss_in`と`text`の対応を目視 | TRIAL_RESULT_03.md:54 |
| 基準 | 「Std語義の取り違えがAdvへ伝染したか」「Std/Adv用法矛盾」「sense誤り」の3観点。数値基準・goldは無し(通常40にはgold無し) | 同上 |
| 確認していないこと | (1) 独立Judge(LLM Judge C/kind Pは費用上限30円のため未実施) (2) 通常KPのgold(存在しない) (3) rep2のgloss→Advの対応(rep1のみ。Advは各条件1回のみ生成=確率的波及を測れない) (4) 難例20のAdv(Trial_03のEは通常40のみ) (5) Productionのバッチ(5KP/call)での挙動 | 同上、T3 results.jsonl kind=E は`tier=normal`のみ(120行) |
| 事後に判明した事実 | Fable盲検(FABLE_BLIND_RESULT_03.md:7-11)でrep1 glossに誤りが1件(G0 `an unseen clock`「目に見えない時計」)あった。実行層Sonnet自身の参考判定でも当該glossはFAIL(sonnet_reference_03_detail.md、an unseen clock G0 rep1=F)。つまり『誤り入力が0件なので伝染0』ではなく『誤り入力1件で伝染0』。1件ではAdvの耐性を一般化できない | sonnet_reference_03_detail.md、T3 results.jsonl 該当行 |

## 6. 付表A: E0@G0 全60出力(T2 results.jsonl)

Std判定: 誤り=入力gloss誤り。Opus個別判定は未保存のため、Adv(Opus)列は『集計59 PASS + 唯一のNG=reach rep1(Fable)』から導出(個別確認ではない)。Sonnet暫定=gold確定前のSonnet Judge E3(sense/core/singleのどれが不良か)。

| # | E行 | G元行 | KP | rep | 入力Std gloss | Std判定 | Adv説明(原文) | Adv(Opus) | Sonnet暫定 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 127 | 7 | draw a line | 1 | 線を引く | 誤り | to show where one thing ends and another begins | PASS | NG:core |
| 2 | 103 | 81 | draw a line | 2 | 一線を引く | 正 | to set a clear limit between what is acceptable and what is not | PASS | NG:core |
| 3 | 113 | 80 | draw a line | 3 | 線を引く | 誤り | to decide where a limit or boundary should be | PASS | PASS3 |
| 4 | 104 | 2 | pull someone under | 1 | 人を水中に引きずり込む | 正 | to drag someone down below the surface, especially of water | PASS | NG:single |
| 5 | 115 | 2 | pull someone under | 2 | 人を水中に引きずり込む | 正 | to pull someone down below the surface of water | PASS | PASS3 |
| 6 | 120 | 2 | pull someone under | 3 | 人を水中に引きずり込む | 正 | to pull someone down below the surface of the water | PASS | NG:core |
| 7 | 138 | 3 | shine a light on | 1 | ～に光を当てる | 正 | to help people notice or understand something that might otherwise be overlooked | PASS | PASS3 |
| 8 | 139 | 3 | shine a light on | 2 | ～に光を当てる | 正 | to draw attention to something and help people understand it better | PASS | PASS3 |
| 9 | 156 | 3 | shine a light on | 3 | ～に光を当てる | 正 | to help people notice or understand something | PASS | PASS3 |
| 10 | 198 | 4 | brace yourself for | 1 | ～に備えて心の準備をする | 正 | to get mentally ready for something difficult or unpleasant that may happen | PASS | PASS3 |
| 11 | 208 | 4 | brace yourself for | 2 | ～に備えて心の準備をする | 正 | to prepare yourself for something difficult or unpleasant that may happen | PASS | PASS3 |
| 12 | 203 | 4 | brace yourself for | 3 | ～に備えて心の準備をする | 正 | to prepare yourself mentally for something difficult or unpleasant that may happen | PASS | PASS3 |
| 13 | 133 | 5 | sentence someone to death | 1 | 人に死刑を言い渡す | 正 | to officially order that someone be killed as punishment | PASS | PASS3 |
| 14 | 128 | 5 | sentence someone to death | 2 | 人に死刑を言い渡す | 正 | to officially decide that someone must be put to death as a punishment | PASS | PASS3 |
| 15 | 143 | 5 | sentence someone to death | 3 | 人に死刑を言い渡す | 正 | to officially order that someone be killed as a punishment | PASS | PASS3 |
| 16 | 277 | 6 | execution bell | 1 | 処刑の鐘 | 正 | a bell rung to announce or mark an execution | PASS | PASS3 |
| 17 | 279 | 6 | execution bell | 2 | 処刑の鐘 | 正 | a bell rung to signal that an execution is about to happen | PASS | NG:core |
| 18 | 274 | 6 | execution bell | 3 | 処刑の鐘 | 正 | a bell rung to announce or mark an execution | PASS | PASS3 |
| 19 | 169 | 8 | fire the starting gun | 1 | スタートの合図をする | 正 | to signal that an activity or process is beginning | PASS | PASS3 |
| 20 | 171 | 8 | fire the starting gun | 2 | スタートの合図をする | 正 | to signal that an event or activity is beginning | PASS | PASS3 |
| 21 | 182 | 8 | fire the starting gun | 3 | スタートの合図をする | 正 | to signal that an activity or process is beginning | PASS | PASS3 |
| 22 | 375 | 9 | turn on its head | 1 | ひっくり返す | 正 | to change an idea or situation completely, often making it the opposite of what people expected | PASS | PASS3 |
| 23 | 379 | 9 | turn on its head | 2 | ひっくり返す | 正 | to change an idea or situation so that it becomes very different, often the opposite of what people expected | PASS | PASS3 |
| 24 | 388 | 9 | turn on its head | 3 | ひっくり返す | 正 | to change an idea or situation completely, often making it the opposite of what people expected | PASS | PASS3 |
| 25 | 174 | 10 | reach for someone's wallet | 1 | 人の財布に手を伸ばす | 誤り | to move your hand toward another person's wallet to take or use it | NG | NG:sense/core |
| 26 | 167 | 10 | reach for someone's wallet | 2 | 人の財布に手を伸ばす | 誤り | to get ready to spend money | PASS | NG:core |
| 27 | 181 | 10 | reach for someone's wallet | 3 | 人の財布に手を伸ばす | 誤り | to get ready to pay for something, often because you want to buy it | PASS | NG:core |
| 28 | 264 | 17 | leap into action | 1 | すぐに行動を起こす | 正 | to start doing something quickly and with energy | PASS | PASS3 |
| 29 | 267 | 17 | leap into action | 2 | すぐに行動を起こす | 正 | to start doing something quickly and with energy | PASS | PASS3 |
| 30 | 266 | 17 | leap into action | 3 | すぐに行動を起こす | 正 | to start doing something quickly and energetically | PASS | PASS3 |
| 31 | 319 | 20 | hold on | 1 | ちょっと待つ | 正 | to wait for a moment before doing or deciding something | PASS | PASS3 |
| 32 | 327 | 20 | hold on | 2 | ちょっと待つ | 正 | to wait for a moment before doing or deciding something | PASS | PASS3 |
| 33 | 324 | 20 | hold on | 3 | ちょっと待つ | 正 | to wait for a short time before doing or deciding something | PASS | PASS3 |
| 34 | 335 | 21 | letter of introduction | 1 | 紹介状 | 正 | a letter that introduces someone to another person and explains who they are | PASS | PASS3 |
| 35 | 336 | 21 | letter of introduction | 2 | 紹介状 | 正 | a letter that presents someone to another person or organization | PASS | PASS3 |
| 36 | 341 | 21 | letter of introduction | 3 | 紹介状 | 正 | a written note that introduces someone to another person | PASS | PASS3 |
| 37 | 387 | 22 | bring in | 1 | ～を持ち込む | 正 | to take something into a place | PASS | PASS3 |
| 38 | 302 | 22 | bring in | 2 | ～を持ち込む | 正 | to take something into a place from outside | PASS | PASS3 |
| 39 | 312 | 22 | bring in | 3 | ～を持ち込む | 正 | to take something with you into a place | PASS | NG:single |
| 40 | 202 | 30 | carry the load | 1 | 荷物を運ぶ | 正 | to hold and transport the things that need to be carried | PASS | NG:sense |
| 41 | 200 | 30 | carry the load | 2 | 荷物を運ぶ | 正 | to hold and move the things someone needs to take with them | PASS | NG:sense |
| 42 | 204 | 30 | carry the load | 3 | 荷物を運ぶ | 正 | to carry most of the weight or take on most of the responsibility | PASS | PASS3 |
| 43 | 344 | 31 | on the throne | 1 | 王座に君臨する | 正 | to be in the most powerful or important position in a particular area | PASS | PASS3 |
| 44 | 351 | 31 | on the throne | 2 | 王座に君臨する | 正 | to be in the most powerful or leading position | PASS | PASS3 |
| 45 | 358 | 31 | on the throne | 3 | 王座に君臨する | 正 | to be in the leading or most powerful position | PASS | PASS3 |
| 46 | 244 | 32 | refueling support | 1 | 給油支援 | 正 | help with supplying fuel so vehicles or aircraft can keep operating | PASS | NG:core |
| 47 | 230 | 32 | refueling support | 2 | 給油支援 | 正 | help with supplying fuel to vehicles or aircraft | PASS | PASS3 |
| 48 | 242 | 32 | refueling support | 3 | 給油支援 | 正 | Help that provides fuel or helps vehicles or aircraft refuel so they can keep operating. | PASS | NG:core |
| 49 | 298 | 33 | take the wheel | 1 | ハンドルを握る | 正 | to take control of a situation or become the person in charge | PASS | PASS3 |
| 50 | 296 | 33 | take the wheel | 2 | ハンドルを握る | 正 | to take control of a situation and decide what happens next | PASS | PASS3 |
| 51 | 300 | 33 | take the wheel | 3 | ハンドルを握る | 正 | to take control of a situation and decide what happens next | PASS | PASS3 |
| 52 | 231 | 34 | apply one's findings | 1 | 人の研究結果を応用する | 正(要注意) | to use what someone learned from research in a real situation | PASS | PASS3 |
| 53 | 236 | 34 | apply one's findings | 2 | 人の研究結果を応用する | 正(要注意) | to use what someone learned through research in a practical situation | PASS | NG:core |
| 54 | 228 | 34 | apply one's findings | 3 | 人の研究結果を応用する | 正(要注意) | to use what someone learned through research in another situation | PASS | NG:core |
| 55 | 368 | 46 | off the hook | 1 | 責任を問われずに済む | 正 | not held responsible for something or expected to deal with it | PASS | PASS3 |
| 56 | 361 | 46 | off the hook | 2 | 責任を問われずに済む | 正 | to avoid being blamed or punished for something | PASS | PASS3 |
| 57 | 369 | 46 | off the hook | 3 | 責任を問われずに済む | 正 | to avoid being blamed or punished for something | PASS | PASS3 |
| 58 | 389 | 47 | jump to conclusions | 1 | 早まって結論を出す | 正 | to decide something is true before you have enough information | PASS | PASS3 |
| 59 | 390 | 47 | jump to conclusions | 2 | 早まって結論を出す | 正 | to decide what is true before you have enough information | PASS | PASS3 |
| 60 | 391 | 47 | jump to conclusions | 3 | 早まって結論を出す | 正 | to decide what is true before you have enough information | PASS | PASS3 |

Std判定の根拠(ユニーク別):
- draw a line「線を引く」: 誤り — 字義訳。GOLD_LABELS_FINAL_01の「不可: 線を引く」に明記。Opus Std G0 24/26のNG2件の1つ(確実)
- reach for someone's wallet「人の財布に手を伸ばす」: 誤り — 盗む読み。Fable T03で同一文字列がFAIL(blind #15 D)。Opus G0 NG2件の1つ(推定: OPUS_REVIEW_04.md:5「難例の誤り2種」+委任_08 §1「draw a line字義、reach for someone's wallet」)
- apply one's findings「人の研究結果を応用する」: 正(要注意) — Opus G0 NG2件に含まれない(推定)ため正。Sonnet暫定=deictic指摘。Fable T03はG3「人の研究結果を当てはめる」をFAIL(所有者誤り)としており、同型で基準差の可能性(CONSISTENCY_01参照)
- 上記以外のglossは『正』。根拠=Opus Std G0 24/26のNG2件(draw a line・reachと推定)に含まれないこと。個別判定ログは未保存。T3で同一文字列がFable盲検判定済みのKP(carry the load/hold on/jump to conclusions/leap into action/letter of introduction/off the hook/pull someone under/refueling support/sentence someone to death/shine a light on/take the wheel)は全てPASS(`CONSISTENCY_01.md` §照合)。

Sonnet暫定(gold確定前)の不合格 15 / 60(Opus確定=1)。不良項目別(複数計上): sense=3, core=11, single=2。→暫定→確定で14件がNG→PASSに転じた(gold追補・core判定基準の差。`CONSISTENCY_01.md`)。

## 付表A2: E0@G2 難例22出力(T2。Opus 22/22 PASS・集計のみ)

| E行 | G元行 | KP | rep | 入力Std gloss | Adv説明 | Sonnet暫定 |
|---|---|---|---|---|---|---|
| 106 | 12 | draw a line | 1 | 境界をはっきりさせる | to make a clear boundary between things | PASS3 |
| 483 | 84 | draw a line | 2 | 境界をはっきりさせる | to clearly separate one thing from another | PASS3 |
| 484 | 85 | draw a line | 3 | はっきり区別する | to make a clear difference between two things or decide where one ends and another begins | PASS3 |
| 157 | 13 | pull someone under | 1 | 人を水中に引きずり込む | to drag someone down below the surface of water | PASS3 |
| 123 | 36 | shine a light on | 1 | ～を明らかにする | to help people see or understand something that was not clear before | PASS3 |
| 129 | 37 | brace yourself for | 1 | ～に備えて心の準備をする | to prepare yourself for something difficult or surprising that may happen | PASS3 |
| 110 | 18 | sentence someone to death | 1 | 人に死刑を言い渡す | to officially order that someone be killed as punishment for a crime | PASS3 |
| 144 | 19 | execution bell | 1 | 処刑を知らせる鐘 | a bell that announces an execution | PASS3 |
| 107 | 24 | fire the starting gun | 1 | 物事を始めるきっかけになる | to cause an activity or process to begin | PASS3 |
| 205 | 25 | turn on its head | 1 | ～をひっくり返す | to change an idea or situation so completely that it becomes the opposite of what people expected | PASS3 |
| 111 | 38 | reach for someone's wallet | 1 | 人が支払いに備えて自分の財布に手を伸ばす | to get ready to pay for something by taking out your wallet | PASS3 |
| 159 | 44 | leap into action | 1 | すぐに行動を起こす | to start doing something quickly and with energy | PASS3 |
| 173 | 52 | hold on | 1 | ちょっと待って | to wait before doing or deciding something | PASS3 |
| 189 | 53 | letter of introduction | 1 | 紹介状 | a letter that introduces someone to another person | PASS3 |
| 168 | 69 | bring in | 1 | ～を取り入れる | to add or introduce something into a place or situation, often so it can be used | PASS3 |
| 154 | 56 | carry the load | 1 | 荷物を運ぶ | to carry or handle most of what needs to be carried | NG:core |
| 192 | 57 | on the throne | 1 | トップの座にいる | to be in the most powerful or important position | PASS3 |
| 136 | 60 | refueling support | 1 | 給油の支援 | help with providing fuel to vehicles or aircraft | NG:core |
| 170 | 61 | take the wheel | 1 | ハンドルを握る | to take control or be the person who makes the decisions | PASS3 |
| 131 | 50 | apply one's findings | 1 | 自分の研究結果を当てはめる | to use the results of one's research to understand or deal with a situation | NG:core |
| 185 | 63 | off the hook | 1 | 責任を免れる | to no longer be blamed or held responsible for something | PASS3 |
| 206 | 64 | jump to conclusions | 1 | 早まった結論を出す | to decide what is true before you have enough information | PASS3 |

## 付表A3: E0@G3 難例22出力(T2。Opus 22/22 PASS・集計のみ)

| E行 | G元行 | KP | rep | 入力Std gloss | Adv説明 | Sonnet暫定 |
|---|---|---|---|---|---|---|
| 102 | 11 | draw a line | 1 | 区別をはっきりさせる | to make a clear difference between two things | NG:sense |
| 485 | 83 | draw a line | 2 | 境界をはっきりさせる | to make clear where a limit or boundary is | PASS3 |
| 486 | 82 | draw a line | 3 | 一線を引く | to set a clear limit between what is acceptable and what is not | NG:core |
| 116 | 14 | pull someone under | 1 | 人を水中に引きずり込む | to drag someone down below the surface of the water | PASS3 |
| 105 | 26 | shine a light on | 1 | ～を明らかにする | to help people notice or understand something more clearly | PASS3 |
| 134 | 27 | brace yourself for | 1 | ～に備える | to prepare yourself for something difficult or surprising that may happen | PASS3 |
| 114 | 15 | sentence someone to death | 1 | 人に死刑を言い渡す | to officially order that someone be killed as a punishment | PASS3 |
| 151 | 16 | execution bell | 1 | 処刑を知らせる鐘 | A bell rung to let people know that an execution is happening or about to happen. | PASS3 |
| 125 | 28 | fire the starting gun | 1 | 始まりの合図を出す | to signal that something is beginning | PASS3 |
| 193 | 29 | turn on its head | 1 | ～をひっくり返す | to change something completely, often into its opposite | PASS3 |
| 122 | 35 | reach for someone's wallet | 1 | 財布に手を伸ばす | to get ready to pay for something | PASS3 |
| 145 | 45 | leap into action | 1 | すぐに行動を起こす | to start doing something quickly and energetically | PASS3 |
| 162 | 49 | hold on | 1 | ちょっと待って | to wait for a moment before continuing or deciding | PASS3 |
| 187 | 51 | letter of introduction | 1 | 紹介状 | a letter that presents someone to another person and explains who they are | PASS3 |
| 161 | 58 | bring in | 1 | ～を持ち込む | to take something into a place | PASS3 |
| 132 | 54 | carry the load | 1 | 荷物を運ぶ | to hold and move the things that need to be carried | NG:sense |
| 184 | 55 | on the throne | 1 | トップの座にいる | to be in the most powerful or important position | PASS3 |
| 146 | 67 | refueling support | 1 | 給油支援 | help that provides fuel to vehicles or aircraft so they can keep operating | NG:core |
| 163 | 68 | take the wheel | 1 | ハンドルを握る | to take control and decide what happens | NG:sense |
| 135 | 41 | apply one's findings | 1 | 自分の研究結果を応用する | to use what someone learned through research in a practical way | NG:core |
| 180 | 71 | off the hook | 1 | 責任を問われずに済む | not blamed or held responsible for something | PASS3 |
| 196 | 72 | jump to conclusions | 1 | 早まった結論を出す | to decide what is true before you have enough information | PASS3 |

## 7. 付表B: 通常40×3方式 E0説明 120出力(T3 results.jsonl kind=E)

Std判定=Fable盲検最終判定(FABLE_BLIND_RESULT_03.md)。Adv判定=Sonnet目視の公式報告(NG0)+本監査の再目視メモ(『所見』列。正式判定ではない)。

| blind# | 型/X-Z | KP | arm | E行 | G(rep1)行 | 入力Std gloss | Std(Fable) | Adv説明(原文) | 所見 |
|---|---|---|---|---|---|---|---|---|---|
| 21 | T/X | a place of one's own | G0 | 435 | 86 | 自分だけの場所 | PASS | a space that belongs to you or is just for your use |  |
| 21 | T/X | a place of one's own | G2 | 441 | 214 | 自分だけの場所 | PASS | a space that is yours to use and arrange as you like |  |
| 21 | T/X | a place of one's own | G3 | 442 | 186 | 自分だけの場所 | PASS | a space you can use as your own, without having to share it |  |
| 22 | P/X | add up | G0 | 422 | 83 | つじつまが合う | PASS | to fit together in a way that makes sense |  |
| 22 | P/X | add up | G2 | 429 | 230 | つじつまが合う | PASS | to make sense when you consider all the details together |  |
| 22 | P/X | add up | G3 | 424 | 155 | つじつまが合う | PASS | to make sense when all the facts are considered together |  |
| 23 | T/X | an unseen clock | G0 | 412 | 60 | 目に見えない時計 | FAIL | a hidden sense of time that affects when something happens or changes | Std誤り入力(字義訳)。出力は「時計」を引き継がず"hidden sense of time"。誤りの波及なし(実行層目視。"sense of time"はG2/G3の"hidden process"よりやや曖昧) |
| 23 | T/X | an unseen clock | G2 | 416 | 174 | 表には見えない時間の仕組み | PASS | a hidden process that affects when something changes or happens |  |
| 23 | T/X | an unseen clock | G3 | 418 | 194 | 見えないところで時を刻む仕組み | PASS | a hidden process that affects when something changes |  |
| 24 | I/X | behind the curtain | G0 | 414 | 95 | 舞台裏に | PASS | in a hidden role, doing or controlling things out of public view |  |
| 24 | I/X | behind the curtain | G2 | 411 | 167 | 表に出ずに裏で関わっている | PASS | to be involved in something without being seen or known by others |  |
| 24 | I/X | behind the curtain | G3 | 415 | 170 | 舞台裏で | PASS | involved in or controlling something without being seen by the public |  |
| 25 | I/Z | catch one's breath | G0 | 462 | 91 | 息を整える | PASS | to pause until you can breathe normally again after physical effort |  |
| 25 | I/Z | catch one's breath | G2 | 463 | 246 | 息を整える | PASS | to rest briefly until your breathing becomes normal again |  |
| 25 | I/Z | catch one's breath | G3 | 457 | 209 | 息を整える | PASS | to pause and breathe normally again after being active or feeling tired |  |
| 26 | I/X | center stage | G0 | 389 | 64 | 注目の中心 | PASS | in the position that gets the most attention |  |
| 26 | I/X | center stage | G2 | 387 | 136 | 注目の的になる | PASS | to be the main focus of attention |  |
| 26 | I/X | center stage | G3 | 393 | 126 | 注目の中心 | PASS | the position or situation that gets the most attention |  |
| 27 | C/X | change one's surroundings | G0 | 443 | 87 | 自分の周りの環境を変える | PASS | to make changes to the place or environment around you |  |
| 27 | C/X | change one's surroundings | G2 | 436 | 215 | 身の回りの環境を変える | PASS | to make changes to the place or environment around you |  |
| 27 | C/X | change one's surroundings | G3 | 440 | 187 | 身の回りの環境を変える | PASS | to make changes to the place or conditions around you |  |
| 28 | P/X | come down | G0 | 405 | 59 | 下がる | PASS | to become lower in amount, price, or level |  |
| 28 | P/X | come down | G2 | 403 | 173 | 下がる | PASS | to become lower in amount, level, or value |  |
| 28 | P/X | come down | G3 | 406 | 193 | 値下がりする | PASS | to become lower, especially in price |  |
| 29 | C/X | control over time | G0 | 368 | 55 | 時間を自分で決められること | PASS | the ability to choose when and how you spend your time |  |
| 29 | C/X | control over time | G2 | 361 | 145 | 時間の使い方を自分で決められること | PASS | being able to choose how you use your time |  |
| 29 | C/X | control over time | G3 | 367 | 119 | 時間を自分で調整できること | PASS | the ability to decide how and when your time is used |  |
| 30 | I/Z | fall to one's knees | G0 | 447 | 104 | ひざまずく | PASS | to drop down so that both knees touch the ground |  |
| 30 | I/Z | fall to one's knees | G2 | 456 | 241 | ひざをつく | PASS | to drop down until your knees touch the ground |  |
| 30 | I/Z | fall to one's knees | G3 | 455 | 223 | ひざまずく | PASS | to drop down until your knees touch the ground |  |
| 31 | T/Z | far bank | G0 | 479 | 13 | 向こう岸 | PASS | the land beside a river on the opposite side from where you are |  |
| 31 | T/Z | far bank | G2 | 478 | 44 | 向こう岸 | PASS | the side of a river or other body of water that is farther away |  |
| 31 | T/Z | far bank | G3 | 471 | 33 | 向こう岸 | PASS | the side of a river opposite to where you are |  |
| 32 | P/X | fill in | G0 | 425 | 96 | ～を補う | PASS | to provide what is missing or needed |  |
| 32 | P/X | fill in | G2 | 417 | 168 | 足りないところを補う | PASS | to provide what is missing or needed |  |
| 32 | P/X | fill in | G3 | 428 | 171 | 足りない部分を補う | PASS | to provide what is missing so that something is more complete |  |
| 33 | T/X | gap between | G0 | 364 | 53 | ～の間の隔たり | PASS | a difference or distance separating two things |  |
| 33 | T/X | gap between | G2 | 362 | 143 | ～の間にある隔たり | PASS | a difference or separation between two things |  |
| 33 | T/X | gap between | G3 | 378 | 117 | ～の間にある隔たり | PASS | a difference or distance that separates two things |  |
| 34 | C/X | give back gains | G0 | 383 | 62 | 上昇分を失う | PASS | to lose some of an earlier increase in value |  |
| 34 | C/X | give back gains | G2 | 379 | 133 | 上昇分の一部を失う | PASS | to lose some of an earlier increase in value |  |
| 34 | C/X | give back gains | G3 | 384 | 124 | 上昇分を失う | PASS | to lose some of an earlier increase in value or amount |  |
| 35 | I/Z | give one's word | G0 | 450 | 103 | 約束する | PASS | to promise that you will do something or keep a promise |  |
| 35 | I/Z | give one's word | G2 | 454 | 240 | 固く約束する | PASS | to make a serious promise and intend to keep it |  |
| 35 | I/Z | give one's word | G3 | 458 | 222 | 約束する | PASS | to promise that you will do something |  |
| 36 | C/Z | grow lighter | G0 | 466 | 92 | 軽くなる | PASS | to become less heavy or burdensome |  |
| 36 | C/Z | grow lighter | G2 | 467 | 247 | 気持ちが軽くなる | PASS | to feel less worried or burdened than before |  |
| 36 | C/Z | grow lighter | G3 | 476 | 210 | 軽くなる | PASS | to become less heavy or feel less burdensome |  |
| 37 | C/Z | hold out a hand | G0 | 477 | 12 | 手を差し出す | PASS | to extend your hand toward someone or something |  |
| 37 | C/Z | hold out a hand | G2 | 480 | 43 | 手を差し出す | PASS | to extend your hand toward someone, often to offer help or make contact |  |
| 37 | C/Z | hold out a hand | G3 | 470 | 32 | 手を差し出す | PASS | to stretch your hand toward someone or something |  |
| 38 | T/X | impulse buying | G0 | 438 | 89 | 衝動買い | PASS | buying something suddenly without planning to do so |  |
| 38 | T/X | impulse buying | G2 | 449 | 183 | 衝動買い | PASS | buying something suddenly without planning to, because you want it at that moment |  |
| 38 | T/X | impulse buying | G3 | 444 | 200 | 衝動買い | PASS | buying something suddenly without planning to, because you want it at that moment |  |
| 39 | I/Z | in one's place | G0 | 464 | 106 | 人の代わりに | PASS | instead of another person, doing what they would normally do |  |
| 39 | I/Z | in one's place | G2 | 465 | 243 | 人の代わりに | PASS | instead of another person |  |
| 39 | I/Z | in one's place | G3 | 459 | 225 | 人の代わりに | PASS | instead of someone, doing what they would normally do |  |
| 40 | C/Z | lose trust in someone | G0 | 472 | 11 | 人への信頼を失う | PASS | to stop believing that someone is honest or can be relied on |  |
| 40 | C/Z | lose trust in someone | G2 | 474 | 42 | 人への信頼を失う | PASS | to stop believing that someone is honest or will do what they say |  |
| 40 | C/Z | lose trust in someone | G3 | 469 | 31 | 人への信頼を失う | PASS | to stop believing that someone is honest or can be relied on |  |
| 41 | C/X | move in the other direction | G0 | 453 | 90 | 反対の方向に動く | PASS | to go or change in a way that is opposite to another direction |  |
| 41 | C/X | move in the other direction | G2 | 448 | 184 | 反対の方向に動く | PASS | to go the opposite way |  |
| 41 | C/X | move in the other direction | G3 | 452 | 201 | 逆の方向に動く | PASS | to go or change toward the opposite side or result |  |
| 42 | I/X | not the same picture | G0 | 363 | 51 | 同じ状況ではない | PASS | to describe a situation that is different from another one |  |
| 42 | I/X | not the same picture | G2 | 366 | 129 | 同じ状況ではない | PASS | to describe a situation that is different from another one |  |
| 42 | I/X | not the same picture | G3 | 372 | 108 | 同じ状況ではない | PASS | to describe a situation that is different from another one |  |
| 43 | I/X | on paper | G0 | 433 | 85 | 書面上では | PASS | As it is described in writing or theory, rather than how it works in real life. | 軽微: "in writing or theory"と2語併記(実質単一義) |
| 43 | I/X | on paper | G2 | 432 | 213 | 理論上は | PASS | as something seems or is described in theory, rather than in actual practice |  |
| 43 | I/X | on paper | G3 | 439 | 185 | 書面上では | PASS | as something written or planned, rather than as it works in real life |  |
| 44 | T/X | price tag | G0 | 399 | 58 | 値札 | PASS | A label on an item that shows how much it costs. |  |
| 44 | T/X | price tag | G2 | 409 | 172 | 値札に表示された価格 | THIN | the amount of money shown on an item as its price | Std入力は薄(Fable△「値札に表示された価格」)。出力は「表示された金額」寄り。誤りではない |
| 44 | T/X | price tag | G3 | 397 | 192 | 値札 | PASS | a label that shows how much something costs |  |
| 45 | P/X | pull back | G0 | 394 | 74 | 取り下げる | PASS | to decide not to continue with or offer something |  |
| 45 | P/X | pull back | G2 | 395 | 147 | いったん引き下げる | PASS | to stop doing or offering something, often for a while |  |
| 45 | P/X | pull back | G3 | 404 | 157 | ～を取り下げる | PASS | to stop or reduce something you were doing or planning |  |
| 46 | I/X | put on hold | G0 | 413 | 94 | ～を保留にする | PASS | to stop or delay something for a while |  |
| 46 | I/X | put on hold | G2 | 419 | 166 | ～をいったん保留にする | PASS | to pause or delay something for now without deciding to cancel it |  |
| 46 | I/X | put on hold | G3 | 421 | 169 | ～をいったん保留にする | PASS | to stop or delay something for a time without deciding to cancel it |  |
| 47 | C/X | room for one's own pace | G0 | 376 | 54 | 自分のペースで行動できる余地 | PASS | the freedom to do things at a speed that feels right for you |  |
| 47 | C/X | room for one's own pace | G2 | 377 | 144 | 自分のペースで過ごせる余地 | PASS | the freedom to do things at a speed that feels comfortable to you |  |
| 47 | C/X | room for one's own pace | G3 | 369 | 118 | 自分のペースで過ごせる余裕 | PASS | enough freedom to do things at a speed that feels right to you |  |
| 48 | C/X | room to choose | G0 | 382 | 52 | 選ぶ余地 | PASS | having the freedom to decide what you want from different options |  |
| 48 | C/X | room to choose | G2 | 381 | 130 | 選ぶ余地 | PASS | to have the freedom to make your own choices |  |
| 48 | C/X | room to choose | G3 | 386 | 109 | 選ぶ余地 | PASS | the freedom to decide between different options |  |
| 49 | P/X | run on | G0 | 426 | 82 | ～に合わせて動く | PASS | to operate using a particular source of power or following a particular system or schedule | Std入力は正(Fable PASS)。出力が2義併記("power source" or "system or schedule")=Adv生成起因の欠陥(single不良)。G2/G3は単一義 |
| 49 | P/X | run on | G2 | 427 | 229 | ～の時間軸で進む | PASS | to happen or develop according to a particular schedule or timescale |  |
| 49 | P/X | run on | G3 | 423 | 154 | ～の時間軸で進む | PASS | to follow a particular schedule or time frame |  |
| 50 | P/X | settle at | G0 | 390 | 65 | ～で取引を終える | PASS | to end at a particular amount or level |  |
| 50 | P/X | settle at | G2 | 391 | 137 | ～で取引を終える | PASS | to finish at a particular level or amount |  |
| 50 | P/X | settle at | G3 | 388 | 127 | ～で取引を終える | PASS | to finish at a particular level or amount |  |
| 51 | P/X | settle down | G0 | 430 | 84 | 落ち着く | PASS | to become calmer or more stable after being unsettled |  |
| 51 | P/X | settle down | G2 | 434 | 231 | 落ち着く | PASS | to become calmer or more stable after a period of change or activity |  |
| 51 | P/X | settle down | G3 | 431 | 156 | 落ち着く | PASS | to become calmer or more stable after changing or being unsettled |  |
| 52 | C/Z | speak against someone | G0 | 460 | 105 | 人を批判する | PASS | to say that you disagree with someone or think they have done something wrong |  |
| 52 | C/Z | speak against someone | G2 | 461 | 242 | 人を批判する | PASS | to say that you disagree with or disapprove of someone |  |
| 52 | C/Z | speak against someone | G3 | 451 | 224 | 人を批判する | PASS | to say that you disagree with or disapprove of someone |  |
| 53 | P/X | speak for | G0 | 400 | 75 | ～に代わって話す | PASS | to say what someone else thinks or wants, or represent them |  |
| 53 | P/X | speak for | G2 | 396 | 148 | ～の代わりに話す | PASS | to say something on someone else’s behalf or represent their views |  |
| 53 | P/X | speak for | G3 | 401 | 158 | ～の代わりに話す | PASS | to say something on behalf of someone else |  |
| 54 | T/X | standard deviation | G0 | 446 | 88 | 標準偏差 | PASS | a measure of how much values in a group usually differ from the average |  |
| 54 | T/X | standard deviation | G2 | 445 | 182 | 標準偏差 | PASS | a measure of how spread out a group of numbers is from its average |  |
| 54 | T/X | standard deviation | G3 | 437 | 199 | データのばらつきを表す値 | THIN | a measure of how spread out values are from the average | Std入力は薄(Fable△「データのばらつきを表す値」)。出力は正しい定義。誤りなし |
| 55 | P/X | step out | G0 | 410 | 76 | 外へ出る | PASS | to leave a place and go outside |  |
| 55 | P/X | step out | G2 | 398 | 149 | 姿を現す | PASS | to come out from somewhere so people can see you |  |
| 55 | P/X | step out | G3 | 402 | 159 | 外へ出てくる | PASS | to leave a place for a short time, often by going outside |  |
| 56 | I/X | take a sharp turn | G0 | 380 | 63 | 急展開する | PASS | to change suddenly in a very different direction |  |
| 56 | I/X | take a sharp turn | G2 | 392 | 135 | 急展開する | PASS | to change suddenly in an unexpected way |  |
| 56 | I/X | take a sharp turn | G3 | 385 | 125 | 急展開する | PASS | to change suddenly in a different and often unexpected direction |  |
| 57 | C/X | take off an AI costume | G0 | 407 | 77 | AIの衣装を脱ぐ | PASS | to stop seeming artificial and show a more natural, human side |  |
| 57 | C/X | take off an AI costume | G2 | 420 | 150 | AIの仮面を脱ぐ | PASS | to stop seeming like an AI and show a more real or human side |  |
| 57 | C/X | take off an AI costume | G3 | 408 | 160 | AIの衣装を脱ぐ | PASS | to stop seeming like AI and appear more natural or human |  |
| 58 | I/X | the new normal | G0 | 371 | 50 | 新しい当たり前 | PASS | a new way of doing things that has become usual |  |
| 58 | I/X | the new normal | G2 | 370 | 128 | 新しい当たり前 | PASS | a new way of doing things that people now see as usual |  |
| 58 | I/X | the new normal | G3 | 373 | 107 | 新しい当たり前 | PASS | a new way of doing things that has become usual and accepted |  |
| 59 | T/X | too broad a label | G0 | 374 | 56 | 広すぎるくくり | PASS | a description that groups together things or people that are too different from one another |  |
| 59 | T/X | too broad a label | G2 | 375 | 146 | 大まかすぎるくくり | PASS | a description that groups together things that are too different from each other |  |
| 59 | T/X | too broad a label | G3 | 365 | 120 | 広すぎる呼び方 | PASS | A description that includes too many different people or things to be useful or accurate. |  |
| 60 | P/Z | walk out | G0 | 473 | 93 | 歩いて外へ出る | PASS | to leave a place on foot |  |
| 60 | P/Z | walk out | G2 | 475 | 248 | 歩いて外へ出る | PASS | to leave a place by walking |  |
| 60 | P/Z | walk out | G3 | 468 | 211 | 歩いて出ていく | PASS | to leave a place by walking |  |

集計: Std誤り(Fable FAIL)1・Std薄(△)2・Std正117(計120)。Adv: 正式NG 0、欠陥1(run on)、Std誤り入力でのAdv誤り 0/1。

## 8. 補足: A/B以外のE行(参考・今回の対象外)

T2にはE0@prod(通常55、Production gloss入力、Sonnet暫定のみ)・E1(115)・E1c(77)・E4(52)がある。これらはStd glossを入力にしない、または別Promptであり、今回の『Std誤り→Adv波及』分析の対象外。

## Fable訂正(2026-10-23、ユーザー指摘反映)
59/60の唯一のNG(reach rep1 "to move your hand toward another person's wallet to take or use it")は見出し語 "someone's" に忠実な出力でStdと整合している。「Std誤り→Adv波及 1/5」は「見出し語不整合→Std/Advが揃って見出し語に従った1件」に訂正、Std意味生成の誤りに起因するAdv NGは0件。元の分類(i)は記録として残す。根拠は `FABLE_VERIFICATION_02.md`・`HEADWORD_PLACEHOLDER_01.md`。

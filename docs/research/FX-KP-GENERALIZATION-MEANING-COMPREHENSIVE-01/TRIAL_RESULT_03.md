# TRIAL_RESULT_03: Std日本語glossの確認Trial(G0/G2/G3 x 2rep、委任_08、2026-10-23、DEV er112基盤、Production変更0)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 / 前=`TRIAL_RESULT_02.md`(0-A追記済み)・`OPUS_REVIEW_04.md` / 設計=`DESIGN_04.md` / 実行=`er112_kp_gm_trial_03.py`(+`er112_kp_gm_kpset_03.py`、`er112_kp_gm_trial_03_detail.py`)
生データ=`er112_output/kp_gm_trial_03/`(results.jsonl、paid_calls.jsonl、judge/cache.jsonl、**fable_blind_std_03.md**、fable_blind_std_03_key.json、sonnet_reference_03.md、sonnet_reference_03_detail.md、kpset_03.json、kpall_03.json、run_*.log)
使用model: 生成=**gpt-6-luna**(本番Std glossと同一。新Prompt案の評価対象でありProduction routingのmodel。最新世代かの比較ではなくProduction同一条件の確認のため)、参考Judge=**claude-sonnet-5-5**(評価用の最新世代、25節)。Fable盲検が最終判定。
費用: **30.12円/上限30円(0.12円=0.4%超過、下記§6に経緯)**。内訳(出典=paid_calls.jsonl): luna gloss 150call+再実行1call 15.14円(G0 3.50/G2 6.49/G3 5.30)、E0(Adv現行Prompt)120call 1.67円、Sonnet参考Judge 7batch 13.16円。

## 0. 結論(先頭)
1. **Fable盲検用の表を用意した(`fable_blind_std_03.md`、60行x6列、arm/repはKPごとにランダム化、keyは別ファイル)。最終判定はFable盲検。** 以下はSonnet参考値(3値 PASS/薄△/FAIL)。
2. **Sonnet参考値では、Trial_02で見えたG2/G3の優位は再現しなかった**(全体PASS: G0 76%、G2 73%、G3 73%。FAIL: G0 4/120、G2 3/120、G3 2/120。いずれも差は誤差範囲)。
   - 難例20(gold確定済み): PASS G0 90%、G2 75%、G3 78%だが、差の大半は『薄△』判定(G0 3、G2 9、G3 7)で、**gold上の致命(FAIL)はG0 1、G2 1、G3 2で同等**。G0は難例では想定より安定していた(draw a line G0は2/2が『一線を引く』)。
   - 新規通常40: PASS G0 69%、G2 72%、G3 71%。FAIL G0 3、G2 2、G3 0。**G0に固有のFAIL**は字義訳(`an unseen clock`→「目に見えない時計」x2)と誤用(`settle at`→「～で落ち着く」)で、G2/G3はこれらを避けた(G2/G3のFAIL=center stage「注目の的になる」、run on「～に沿って動く」、apply one's findings「人の研究結果」等)。
   - draw a line(ユーザー検証項目1)を2 Trial合算: **G0 5出力中2出力が字義『線を引く』(NG)、G2 5中1(「はっきりと線を引く」)、G3 5中0**。傾向はG3>G2>G0だが、n=5同士(Fisher p≈0.4)で有意差なし。
3. **薄化はG3の方が多い、とは言えなかった**: 通常40の薄△率はG0 28%、G2 25%、G3 29%(Sonnetは薄△を広く付ける傾向で、G0にも多数付与)。Opusが挙げた薄化5例のうち本Trialの対象にあるのは`brace yourself for`(G3 rep2「～に備える」)と`on the throne`(G3 rep2「トップの座にいて」)で、いずれもG3のrep2のみ、G0には同形なし。薄化率の判定はFable盲検で行う。
4. **安定性(rep間の自己一致)はG0>G2≈G3**: 判定一致 G0 90%、G2 77%、G3 78%。gloss文字列一致 G0 65%、G2 40%、G3 50%。G2/G3は同じKPでも訳語が揺れやすい(2案選択・用法先決めの分だけ分散が増える)。
5. **E0(現行Adv Prompt)の引き継ぎ**: 通常40件x3 arm(E0@G0/G2/G3 rep1)の説明120本を目視確認(§4)。**Std誤り(語義取り違え・字義訳)がAdvへ伝染した件数、Std/Adv用法矛盾は0件**(LLM Judgeは費用上限のため未実施。確認者=Sonnet agentによる全件目視であり独立Judgeではない)。別所見: `run on`のE0説明が2義併記(power源/スケジュール)で、Adv側の既知の弱点(Std起因ではない)。
6. **採否提案のための所見(Sonnet参考値ベース、Fable盲検で上書き可)**: G2/G3がG0より『明確に良い』根拠はTrial_02+Trial_03を通して**弱い**(改善はFAILの減少とdraw a lineの傾向に留まり、薄△と安定性ではG0が同等以上)。費用はG3 +0.03円/call、G2 +0.06円/call。**規則文・検査の変更は不要**(`RULE_CONSISTENCY_01.md`)。→ ユーザー提案は『G0維持』も含めた3択になりうる(§7)。

## 1. 条件
- KP集合(`kpset_03.json`/`kpall_03.json`): 難例20(Trial_02と同一入力、X16/Z4、gold=`TRIAL_02/GOLD_LABELS_FINAL_01.md`)+**新規通常40**(Trial_01/02の集合に無い既存記事のKP、X30/Z10、12記事、型=句動詞10・慣用句/定型11・コロケーション11・名詞句/用語8)。種類を先に決め、出力を見ずに選定(`er112_kp_gm_kpset_03.py` SELECT)。記事単位に3〜4件ずつ(本番のバッチ形)。合計25記事=1armあたり25 callx2 rep。
- arm: G0(現行Production Prompt、`ga.build_user_message_corrected`そのまま)/G2(用法先決め)/G3(定訳・慣用句優先+同一call内で2〜3案選択)。**新Prompt案は追加せず**、G2/G3のブロックとschemaはTrial_02の`G2_BLOCK`/`G3_BLOCK`をそのまま再利用。reasoning=high、各arm rep1・rep2は別call。
- 参考Judge: Sonnet 5.5、gold(難例)+薄化例5件を基準に3値。重複(同一key・同一gloss)は1行に集約(158行)。

## 2. 数値(Sonnet参考値。rep対応の出力単位。最終判定はFable盲検)
| 集合 | arm | n出力 | PASS | 薄△ | FAIL |
|---|---|---|---|---|---|
| 難例20 | G0 | 40 | 36 (90%) | 3 (8%) | 1 (2%) |
| 難例20 | G2 | 40 | 30 (75%) | 9 (22%) | 1 (2%) |
| 難例20 | G3 | 40 | 31 (78%) | 7 (18%) | 2 (5%) |
| 新規通常40 | G0 | 80 | 55 (69%) | 22 (28%) | 3 (4%) |
| 新規通常40 | G2 | 80 | 58 (72%) | 20 (25%) | 2 (2%) |
| 新規通常40 | G3 | 80 | 57 (71%) | 23 (29%) | 0 (0%) |
| 全60 | G0 | 120 | 91 (76%) | 25 (21%) | 4 (3%) |
| 全60 | G2 | 120 | 88 (73%) | 29 (24%) | 3 (2%) |
| 全60 | G3 | 120 | 88 (73%) | 30 (25%) | 2 (2%) |

G0対比のflip(出力単位、改善/悪化/不変): G2 = 11/13/96、G3 = 10/12/98(いずれも有意差なし)。
rep間自己一致(60KP): G0 判定90%・文字列65%、G2 判定77%・文字列40%、G3 判定78%・文字列50%。
通常40の型別(PASS/薄/FAIL、2rep合計): 句動詞(10KP) G0 8/11/1・G2 13/6/1・G3 12/8/0、慣用句(11) G0 17/5/0・G2 16/5/1・G3 17/5/0、コロケーション(11) G0 17/5/0・G2 18/4/0・G3 16/6/0、名詞句(8) G0 13/1/2・G2 11/5/0・G3 12/4/0。→ **句動詞でG2/G3がG0より薄△を減らし、名詞句(`an unseen clock`字義訳)でG0がFAILを出す**。他は差なし。
詳細表(各KPの全出力と判定)=`er112_output/kp_gm_trial_03/sonnet_reference_03_detail.md`。

## 3. ユーザー検証項目1〜6との対応(手段/目的の区別)
| # | 項目 | 結果 | 判定 |
|---|---|---|---|
| 1 | `draw a line`のStd日本語 | 合算(T2+T3) G0 2/5が字義NG、G2 1/5、G3 0/5。G3の出力=区別をはっきりさせる/境界をはっきりさせる/一線を引く(いずれも確定gold内) | 傾向G3最良。**ただし現行G0も本Trialでは2/2が慣用義で、『安定してNG』ではない**(確率的失敗)。有意差なし |
| 2 | 同KPのAdv英語 | 本Trialの対象外(Adv Promptは現行E0維持、Fable判断)。Std改善後のE0@G3は`OPUS_REVIEW_04`で3/3 | 範囲外(前Trial参照) |
| 3 | 他の慣用句・句動詞・一般表現 | 新規通常40(型4種混在)+難例20。FAIL率は全arm低位(2〜3%)で、G0のFAILは字義訳/誤用型 | Std水準はG0含め概ね到達、改善余地は主に『字義訳の稀な発生』と薄△ |
| 4 | 既に正しい説明/意味を壊さない | 通常40でG0 PASS→G2/G3で悪化(PASS→薄△/FAIL)が6/7出力(G2/G3それぞれ)、改善10/10。**壊す件数と直す件数は同数** | 現行を壊さない根拠は弱い(要Fable盲検) |
| 5 | X/Z双方 | 通常40=X30/Z10、難例=X16/Z4。FAIL・薄△はX/Zで同種(Zの`give one's word`等の薄△はG0にも) | X/Z差なし |
| 6 | retry/fallbackを含む量産条件 | 本Trialはgloss段のDEV単体(`ga.build_user_message_corrected`は本番と同一関数)。retry/fallback/Store reuseはWIRING_DESIGN_03で設計のみ。実run evidenceは採用後 | 設計のみ(採用判断前) |
目的(要求品質のStd到達)は『G0でも概ね到達、G2/G3は字義訳型FAILを減らすが薄△・揺れを増やす』という状況。**手段(Trialを実施し計測した)の成功と、目的(G2/G3が現行より要求品質に明確に近い)の達成は別**で、後者は本Trialで確認できていない。

## 4. E0引き継ぎ確認(通常40、E0@G0/G2/G3 rep1)
- 入力gloss→E0説明の全120組を目視(`results.jsonl` kind=E、`gloss_in`/`text`)。結果: **Std語義の取り違えがAdvへ伝染した例0、Std/Adv用法矛盾0、sense誤り0**。説明の長さ・core混入は前Trialと同程度。
- 所見(Std起因でない): `run on`のE0@G0説明が『operate using a particular source of power or following a particular system or schedule』と2義併記。`settle down`等は問題なし。
- LLM Judge(consistent/sense)はコード実装済み(`judge --what C`)だが、上限30円のため**未実施**。目視の限界(確認者=実行agent、独立Judgeではない)を明記する。必要ならFableが『Judge Cを数円で追加』を判断できる。

## 5. 規則整合(BE-06)
`RULE_CONSISTENCY_01.md`: 承認済み「全語反映」は既存gloss判定(指示1)の文言で、新規生成の基準は『全体の意味に過不足なく』。mapping検査は新規生成itemで必須語0・record-only。G2/G3のsomeone's省略は`PERSON_CONSTRAINT_TEXT`が許容。**規則文・検査の変更は不要**。

## 6. 運用上の記録(隠さず報告)
- **上限30円を0.12円(0.4%)超過**(30.12円): Sonnet参考Judgeを4並列workerで7バッチ起動し、各batchのcap検査は『発行前の累計』のためin-flightの分だけ超過した(`judge_call`のcapチェック設計)。Judge開始時の累計は16.8円で、Judge 7バッチの見積は1バッチ1.4〜2.9円(Trial_02実績1.5円/バッチ)x7=約10〜20円=『上限30円ぎりぎり』と認識しながら、24円到達時の再計算(委任_08 T-0)を並列実行中に挟めず(4並列が同時に発行)、結果として30.12円に到達した。再計算の機会を逃したのは手順上の不備。以後のJudge C(consistent)は実施せず終了。
- results.jsonlで**並行process書込みの交錯により1行が欠損**(G3 draw a line rep2)。欠損行は出力内容が不明のため、同じ入力・同じPromptで**1回だけ再実行**(0.06円)して補った(出力を見て選んだ再実行ではない)。台帳でも1行(断片、G2のcost 0.1446円)が欠損したため断片を除去して補正行を追記(`paid_calls.jsonl` repair行)。Trial_02の同種事象(BUDGET_LOG_01)と同じ原因(Windowsのappendがprocess間で非atomic)。
- STOP確認: `stop_check_08.json` rc=0(非停止)。gloss 3process(PID 3846/3847/3848)は全て正常終了。外部停止・再起動なし。

## 7. ユーザー採否提案の下書き(Fable盲検後に更新)
| 案 | 難例の改善 | 薄化/揺れ | 自己一致 | 費用差(1call) | 規則変更 | 所見 |
|---|---|---|---|---|---|---|
| **G0維持(現行)** | draw a lineが確率的に字義化(2/5)、字義訳型FAIL(`an unseen clock`) | 薄△率は同等 | 判定90%(最良) | 0 | なし | 変更0・最安全。字義訳の稀な発生は残る |
| G2(用法先決め) | draw a line 1/5、FAIL 3/120 | 薄△24%(難例22%) | 77% | +0.06円 | なし | 難例で薄△が増える(「心の準備」「明らかにする」) |
| G3(定訳・慣用句優先) | draw a line 0/5、FAIL 2/120、字義訳型を回避 | 薄△25%(難例18%)。薄化例はrep2のみ | 78% | +0.03円 | なし | 揺れ・薄△が残る。Opus所見(通常KPで系統的薄化)は本Trialで再現せず |
1記事セットのgloss callを2回とすると、G3 +0.07円、G2 +0.12円(70円目標比+0.1〜0.2%)。
**Sonnet参考値のみから言えること**: G2/G3は字義訳型FAILを減らす可能性があるが、現行G0を明確に上回る証拠は得られていない。採否は(1)Fable盲検の結果、(2)ユーザーが重視する失敗類型(字義訳FAILの根絶 vs 薄化・揺れの回避)で決まる。技術問題ではなく品質水準の判断(承認済みPrompt変更=ユーザー事項)。

## 8. 残リスク
(1)参考JudgeはSonnet 1系統・薄△の付与が広く、G0にも多数付与(絶対値より相対比較)。(2)新規通常40は1記事3〜4件ずつ・12記事で、記事内相関がある。(3)rep=2のためself-agreementはn=60KPの粗い推定。(4)Judge C未実施(E0引き継ぎは目視)。(5)Std glossの『個別KP難所』(`reach for someone's wallet`は全armで不安定)は規則/Prompt側でなくKP個別の意味決定の問題で、個別対策は禁止のため未対処。

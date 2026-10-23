# PHASE0_CALIBRATION_01: ①独立検査器の較正(既存Trial_02/03出力、委任_14 T-2)

対象: Trial_02/03で**Fable確定ラベル済み**の既存Std出力。入力=一意の(KP, 本文の文, gloss) 161件(Trial_03 全360セル[G0/G2/G3 x 2rep x 60KP]の重複除去158件+Trial_02 `draw a line` の未重複3件)。ラベル(Fable確定/gold): PASS 147・薄(△) 7・字義NG(LITERAL_NG) 3・その他NG(OTHER_NG) 4。
LITERAL_NG(3文字列/5セル): `目に見えない時計`(G0 rep1/rep2、an unseen clock)・`はっきりと線を引く`(G2 rep2、draw a line)・`線を引く`(Trial_02 G0 rep1/rep3、draw a line)。OTHER_NG=`reach for someone's wallet`の『人の/誰かの財布に手を伸ばす』2・`apply one's findings`『人の研究結果を当てはめる』・`settle at`『～で落ち着く』(ただし reach/apply は見出し語に忠実な訳で、原因は課題②側。FABLE_VERIFICATION_02)。
検査器: luna(`SUPPORT_MODEL`)、strict structured output、8項目/call。実装=`er112_kp_gm_trial_04.py`(`INSPECT_*`/`inspect_call`)。生ログ=`er112_output/kp_gm_trial_04/phase0/inspect_{v1,v2low}.jsonl`、集計=`phase0_report_v1_medium.txt`・`phase0_report_v2low.txt`(同ディレクトリ)。

## 1. 結果

| 版 | effort | 処理した入力 | 費用 | 1call費用 | 検査不成立(内容語重なり) | 字義NG recall(文字列) | 他NG flag | 薄 flag | PASSのflag(偽陽性) | flag総数 |
|---|---|---|---|---|---|---|---|---|---|---|
| v1 | medium | 136/161(cap到達で25件未処理) | 4.40円 | 0.259円 | 3件(2.2%) | 1/2(V1/V2とも。未処理25件に「線を引く」が含まれる) | 2/4 | 0/5 | 14/125(11.2%) | 17 |
| **v2low** | low | 161/161 | 2.60円 | 0.124円 | 16件(9.9%) | **V1/V2: 1/3、V1_inv/V2_inv: 2/3**(セル単位 4/5) | 2/4 | 0/7 | 12〜13/147(8〜9%) | 15〜17 |

v2lowの詳細(flag規則別): V1(conveys単独、検査不成立は非flag)=15件(字義NG 1)、V2(figurative AND conveys)=V1と同一(15件)、**V1_inv/V2_inv(検査不成立でもflag)=17件(字義NG 2)**、V3(literal_image_only/otherかつfigurative)=25件で偽陽性22。V1とV2の差は出なかった(literal_image_onlyの出力は全てfigurative判定)。

## 2. 事例別の読み
- `目に見えない時計`: v1・v2lowとも検出(literal_image_only)。再生成の入力になる。
- `線を引く`(Trial_02 G0 x2): v2lowは字義と判定(literal_image_only、gloss_alone_reading_en='Someone makes a mark by drawing a straight shape.')したが**内容語`draw`が重なり検査不成立**扱い=V1/V2では取りこぼし、**V*_invでは検出**。→ flag規則を事前に`V2_inv`へ宣言した根拠。
- `はっきりと線を引く`(G2 rep2、Fable=FAIL字義): v1・v2lowとも**未検出**(same_meaning。検査器は『はっきり境界を引く』と日本語として慣用的に読んだ)。人間(Fable)と検査器で境界が割れる事例で、**検出器の限界**。
- 偽陽性(PASS相当をflag)の多くは、日本語glossが字義の像のまま比喩としても日本語で通じうる表現(`軽くなる`/`書面上では`/`舞台裏に`/`AIの衣装を脱ぐ`/`ハンドルを握る`/`王座に就いて`/`人が自分の財布に手を伸ばす`等)。検査器は『日本語の字義の像のみ』と読んでflagする傾向。`ja_expression_shares_figure`(v2で追加)は偽陽性を明確には減らさなかった(PASS flag 14->12)。
- 薄(△)は一件もflagされない(狙い通り、薄い訳の再生成は本件の範囲外)。

## 3. 1回限りの改訂(v1->v2low)とその理由
- v1(medium)の1call費用が想定0.06円の約4倍(0.26円)で、かつ遅い。effortを下げて再測(v2low)。
- 偽陽性(PASSのflag 11%)を下げる狙いで`ja_expression_shares_figure`欄を追加(日本語表現そのものが比喩を共有するか)。効果は限定的(上記)。
- 改訂は1回のみ(委任文の『1回だけ改訂し再測』)。以降の検査仕様はv2lowで固定してTrialへ。

## 4. 較正結論(Trialへ持ち込む前提)
1. recallは既知字義NGの一部(文字列2/3、セル4/5)。人間境界が割れる事例は取りこぼす。
2. **precisionは低い**(字義NG 2/flag 17=12%)。flagされた大半は『許容しうる訳』で、再生成は『改善/不変/悪化』を測るべき操作(Trial本体で測定)。
3. 検査不成立(内容語重なり)は10%。重なりで除外するとrecallが下がるため、flagは検査不成立でも有効とする(事前宣言`V2_inv`)。
4. 費用はlowで約0.016円/項目(8項目=0.124円)。DESIGN_05の想定0.05〜0.06円/記事を**上回る**(約0.15円/記事)。

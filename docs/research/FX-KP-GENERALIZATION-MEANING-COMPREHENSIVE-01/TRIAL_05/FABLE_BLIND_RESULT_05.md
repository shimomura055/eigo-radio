# FABLE_BLIND_RESULT_05 (Fable盲検ラベル Stage 1 + held-out、Key未開封で確定。委任_23で逐語保存)

ラベル: `fable_labels_05.json`(形式 `{"<row#>:<col>": LABEL}`)。

## Fable注記(逐語)
- 1:A「玄関先のような場所になる」は日本語の玄関先に米国のporchの社交的含意がなくTHIN。
- 3:B/3:G「時間差」は原文の「独自のタイミング(市場ニュースと切り離された時間)」より狭くTHIN。3:E「見えない時計」・3:H「見えないところで時を刻む時計」は字義像のままでFAIL_LIT。
- 4:A は記事固有の説明文で長いが意味は正しくPASS(説明文化の傾向として記録)。
- 5:B「誰も聞きたくない音」は asked for(頼む)→聞きたくない への意味移動でTHIN。
- 7(a door inside the pain、Z小説の新造比喩): 7:Aは字義像だが物語内の比喩として通じ得るためTHIN(FAIL_LITとしない)。7:B「記憶へ戻る道」は物語の解釈を含み、本文のみでは検証できないためTHIN。
- 9: gold(区別する/違いをはっきり示す)に照らし全てPASS。「線引きをする」は日本語で区別の慣用表現としてPASS。
- 10:H/10:I は字義像(芝生)のままでFAIL_LIT。10:Aは日本語の諺「隣の芝生は青い」に接続しPASS。
- 11「小さな爆弾」は本文自体が直喩(seemed to be a tiny bomb)なので字義訳が正しくPASS。
- 13:A/13:B「〜の形をした質問/問いかけ」FAIL_LIT。13:C「賞の形を借りた問いかけ」は偽装の含意が伝わりPASS。13:Dは「トロフィー」が残るがで「形を借りた」で含意が伝わるためTHIN。
- 16「～に備える」は身構える含意が落ちTHIN。17「人の財布に手を伸ばす」は見出し語忠実でPASS(ユーザー判断済み)。

## 集計(委任_23、`er112_kp_gm_trial_05_report.py report --labels fable_labels_05.json`。詳細表=`report_05_fable_labels_05.md`)
Cp追加実行後(R Cp 12出力・held-out Cp 12KP)の時点。**Cpの未ラベル文字列(10文字列=下記「Cp追加後」の追加盲検05c)を除いた暫定値**。

### OF-KP1-08 control再判定の一致率
厳密一致 7/10、粗区分一致 7/10。不一致3件: `draw a line|区別する` 前回THIN→今回PASS(Fable注記: goldに照らしPASS)、`reach for someone's wallet|人の財布に手を伸ばす` 前回FAIL→今回PASS(ユーザー判断済みの見出し語忠実)、`on the throne|トップの座にいて` 前回THIN→今回PASS。いずれも緩む方向(前回より厳しくなった例なし)。集計には前回ラベルを維持(再判定ラベルは使わない)。

### R(hard-core 4KP x 3rep=12出力/arm)と事前宣言基準(FAIL_LIT+FAIL<=1/12 かつ 2rep以上失敗KP=0 かつ THIN<=B0+1)
| arm | n | PASS | THIN | FAIL_LIT+FAIL | 未ラベル | 2rep以上失敗KP | 基準 |
|---|---|---|---|---|---|---|---|
| B0 | 12 | 2 | 0 | 10 | 0 | unseen clock/trophy/greener grass | (基準線) |
| M | 12 | 6 | 0 | 6 | 0 | unseen clock/trophy | 満たさない |
| X1 | 12 | 7 | 0 | 5 | 0 | trophy | 満たさない |
| X2 | 12 | 8 | 4 | **0** | 0 | なし | THIN=4>B0+1(=1)のため**満たさない**(FAIL系0・2rep以上失敗KP 0は満たす) |
| Cp | 12 | 6 | 1 | **2** | **3** | なし | (FAIL_LIT+FAIL)=2>1のため**ラベル確定前でも満たさない**(未ラベル3が全PASSでもFAIL系2は動かない) |
| Cp_t4(参照rep1) | 4 | 3 | 1 | 0 | 0 | なし | n<12参考 |

- Cpの失敗2件: `an unseen clock` rep2「見えない時計」(FAIL_LIT)、`greener grass` rep3「より青々とした芝生」(FAIL_LIT)。いずれも字義訳。Cpは平均で品質は良いがrepごとの揺れが残る。
- X2対B0: FAIL系 10→0。X2のTHIN 4件は `an unseen clock` x3(「価格が変わるまでの見えない時間差」等=Fable注記3:B/3:G「時間差は原文より狭い」)と `greener grass` rep2、`sound no one asked for` rep1,3(「誰も聞きたくない音」=asked forの意味移動、これはR co-KP側)。
- X1対M(H5): FAIL系 M 6 → X1 5 (PASS 6→7)。差は1出力で、`an unseen clock` rep1,3 のみX1がPASS。2rep以上失敗KPは M=2→X1=1。**有意な差とは言い難い**(同条件の追加repなし)。
- R co-KP(come down / behind the scenes / sound no one asked for): X2で `sound no one asked for` が rep1,3 でTHIN(B0は全PASS)=**X2のco-KP悪化1件(2出力)**。他KP・他armに悪化なし。Cpは悪化なし(rep1,2 PASS)。
- X2対Cp(部分): Cp 12出力のうち9がラベル済(PASS 6/THIN 1/FAIL_LIT 2)。未ラベル3(`draw a line` rep3「境界線を引く」、`question shaped like a trophy` rep2,3)は追加盲検05cで確定する。

### held-out(10KP x 1rep)
- X2: B0=PASSでX2がTHIN/FAIL系に悪化したKP **0件**(`a door inside the pain` はB0もX2もTHIN)。
- Cp: 10KP中 PASSと判定可能なのは `tiny bomb` `inner timekeeper` `all it takes` の3、他7KPは未ラベル文字列(05cで確定)。Cp悪化は未確定。
- 追加実行の誤り(正直な記録): `--set H` を `--nheld 10` なしで実行したため、held-out順序リスト全12jobs(10KP+`jump into action`、`feel borrowed/feel like friction`の2call)を実行した。余分な2callの費用は約0.343円。盲検・集計はオリジナル10KPのみ使用。

## Cp追加後(05c: 追加盲検表)
`fable_blind_05c.md`(9行・10文字列。Cp追加で**新たに出現した文字列のみ**、既出文字列[既知ラベル+05ラベル]は継承、arm伏せ)+`fable_blind_05c_key.json`(別ファイル)。Fableが `fable_labels_05c.json`(`{"<row#>:<col>": LABEL}`)を作成後、`py er112_kp_gm_trial_05_report.py report --labels fable_labels_05.json --labels_c fable_labels_05c.json` で再集計(出力=`report_05_fable_labels_05_withc.md`)。

## 05c ラベル(委任_25で逐語保存、Key未開封で確定)
`fable_labels_05c.json`:
```
{"1:A":"PASS","1:B":"PASS","2:A":"PASS","3:A":"PASS","4:A":"PASS","5:A":"PASS","6:A":"PASS","7:A":"PASS","8:A":"THIN","9:A":"PASS"}
```
Fable注記(逐語): 3:A「境界線を引く」は日本語で区別の慣用表現として機能しPASS(「線を引く」単独はFAIL_LITの従来判定と区別)。8:A「苦しみの中にある戻り道」は物語解釈を含み本文だけでは検証できないためTHIN(05の7:Bと同基準)。

### Fable判定の揺れ(緩化方向)
OF-KP1-08 control再判定の一致率は7/10。不一致3件(`draw a line|区別する` THIN->PASS、`reach for someone's wallet|人の財布に手を伸ばす` FAIL->PASS、`on the throne|トップの座にいて` THIN->PASS)はいずれも前回より緩い方向。集計は前回ラベル維持で正しい(Fable判断)。

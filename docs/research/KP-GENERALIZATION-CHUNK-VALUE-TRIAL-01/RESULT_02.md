# RESULT_02: 改善ループ1回(方式D')の結果(KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01 委任_02、2026-10-30)

Trial専用・Production変更0。比較ページ=https://shimomura055.github.io/eigo-radio/user_test/kp_generalization_trial_01/ (D'列・G1/G2併記を追加)。RESULT_01.md(委任_01)の続き。

## 1. 結論・Closeout案
**Closeout案: USER_DECISION_REQUIRED(Status上限VALIDATED手前。D'は未完=費用上限¥20到達で8/16ケースのみ実行)。** 推奨は『D'の延長ではなく、方式D'に別系列の最終ゲートを足した案(D'')を残り8ケースで検証』(下記7節)。

要点(Sonnet実読。必須検証の同一8ケース、フレーズ枠):
| | Before | A(統合) | D(委任_01) | **D'(今回)** |
|---|---|---|---|---|
| そのまま選べる/提示 | 12/45(27%) | 30/39(77%) | 31/39(79%) | **27/42(64%)** |
| Standard | 4/21 | 13/20 | 15/17(88%) | 15/22(68%) |
| Advanced | 8/24 | 17/19 | 16/22(73%) | 12/20(60%) |
| 3件以上選べるケース(8中) | 1 | 6 | 6 | **7** |
- **率はDより低下**(64% vs 79%)。ただし8ケース・約40件・run間ばらつき大(untidi_b1b: D 7/7 vs D' 3/6、jwst_m_b1b: D 2/7 vs D' 3/6)のため、差の大半は塊判定(luna)のばらつきを含み、確定的な優劣ではない。**目的の改善(修正せず選べる率)はこのループでは未達**。
- 改善できた点: G1(a2で`take something away from`、b1bは`take points away`でfrom欠落=1/2)、G2(`make something work`)が提示、V3 blow a whistleとV4 sales pitch(b1b)の脱落を解消、`hear it out`→`hear someone out`(a2)、`narrow down`/`turn something around`/`at the time of`維持、V1(confirm a clear fall)除外維持。
- 悪化/残った点: 塊判定が**易しい表現(rely on×3・turn something into・pick up)と自由な組合せ(need an instruction manual・deep image・early step toward)を2回とも『塊』と判定**する。2回判定の和集合で追加された候補(1回目のみ合格)の精度は5/8、2回とも合格は22/34で同等=**和集合自体は悪化原因ではなく、判定器(luna)の難易度・F/C境界の甘さが主因**。
- 費用: 本ループ¥19.92(上限¥15→理由記録で¥20未満)。1レベル¥1.80(うち過剰生成0.17・塊判定2回0.56・一般化約0.3・検証約0.7=main+alt)・約123秒。1記事セット(Std+Adv)約¥3.6=70円の約5.1%(D比 +¥1.6)。**既存段置換による相殺は未確認**。

## 2. 実装した改善(1)〜(4)(すべてTrial: kpg02_methods.py)
(1) **意味修飾語のDROP禁止ガード**(決定論): 形容詞/比較級/否定語がDROPされ、次の非DROP語がCOREならCOREへ戻す(`guard_tokens`)。例: `took an unexpected turn`→`take an unexpected turn`(語義保持)。SLOT名詞を修飾する語(`the usual steps`)は対象外。加えて検証`meaning_preserved=false`なら元span形へ戻す(`generalize_items`)。今回meaning_preserved=falseで戻した件数0、ガード発動は`took an unexpected turn`等。副作用: `set a limit`(語義喪失)→`set a lower limit`(lower残り=未一般化NG)に変わった(語義保持とのトレードオフ)。
(2) **塊判定の2回和集合**: 順序反転の2passを並列実行、どちらかが合格なら採用。難易度は**C判定でeasyとされたら不可**(初版は『どちらかがeasy』で不可としたがblow a whistleが脱落したため、C判定のeasyに限定=下記3節)。
(3) **someone/something判定・受動形除外**: 一般化段Promptに人称判定規則・受動形/過去分詞を核に残さない規則、塊判定に`passive_fragment`フラグ。関係詞で始まる節断片(whose…/which…)は正規表現で決定論除外(`whose interests the conversation serves`の混入対策)。結果: untidi_a2で`hear someone out`に改善、untidi_b1bは同じ候補の再生成がなくhear something outのまま(NG)。
(4) **G1/G2併記**: `chunk_if_generalized`(Fでも一般化すれば見出し語として成立)の別枠alt出力を実装。ただし和集合でC判定が出た場合はmainに入るため、untidi_a2ではG1/G2ともmainで提示された。併記表は比較ページ3b。方針F(現行どおり)=提示されない、方針G=`take something away from`/`make something work`。D_sol(塊判定sol)は費用により未実施。

付随修正: 複数形lemma補正(`Sales`→`sale`が語形違いと判定されassemble失敗し`Sales pitch`が脱落していた不具合。Trial側monkeypatch)、WordNet(zip)のthread-unsafe対策のlock(並列実行で2回AssertionError/AttributeError=費用約¥3の再実行ロス)。

## 3. 設計途中の修正の記録(同一ループ内)
初版D'はeasy veto=『どちらかのpassがeasyなら不可』で実行→blow a whistle(F/easyとC/upper)が脱落(V3退行)、`whose interests the conversation serves`が混入。8ケースの塊判定ログ(API 0で再計算)から、veto条件を『C判定でeasy』に限定+節断片の正規表現除外へ変更し、候補集合が変わる4ケースのみ再実行(約¥2.7)。この修正は新方式ではなく同一ループ内のパラメータ調整。

## 4. 必須9例(D')
G1 ○a2/×b1b(1/2)、G2 ○(a2)、G3 ○、G4 ○、G5 ○、V1 ○(除外)、V2 ○、V3 ○、V4 ○。Before/A/Dは比較ページ2節。

## 5. 残NG(D' main 15/42、alt NG 3件は別)と失敗箇所
| NG | 失敗箇所 | 原因 | 次の一手(見込み) |
|---|---|---|---|
| rely on(×3)・turn something into・pick up・take up(alt) | 選定(難易度) | lunaがC・upper_intermediateと判定。基本動詞+前置詞 | 別系列最終ゲート(7節)または基本動詞+基本前置詞の語彙ベース決定論除外(見込み中〜高) |
| need an instruction manual・deep image・lower limit・early step toward(×2) | 選定(F/C境界) | 比喩/専門名詞句/形容詞+名詞をCと判定 | 同上(別系列ゲートはdeep image/lower limitを不可と判定=見込み高)。early step towardはgeminiも不可 |
| hear something out(b1b)・take points away(b1b)・set a lower limit・or so it seemed | 一般化 | 人称判定が文脈でぶれる/動詞が時制のまま/修飾語保持とのトレードオフ | 見込み低〜中(個別事情) |
| 機構外 | Before成功例の脱落 | 12件中1件(meta_w_b1b `an open question`) | 判定ばらつき |
独立判定(gemini-3.8-flash、非thinking、出力上限1,500、全8ケースのD' 47候補): Sonnetとの一致42/47(89%)。geminiが不可とした12件は、うちSonnet OKは1件のみ(`take something away from`=OVER_GENERALIZED)。

## 6. QCD・ばらつき
- ばらつき: 同一入力の再実行(2回×1〜2ケース)は費用上限のため**未実施**。参考として、D(委任_01)とD'の同一記事比較では提示集合が3〜5件入れ替わる(例: untidi_b1bのD 7/7とD' 3/6)。同一方式の初回→ルール調整後の再生成(untidi_a2・ai_cha_a2・jwst_m_a2)でも候補が入れ替わった。再実行ばらつきの定量は次ループで実施(要追加費用)。
- 使用モデル(開発評価の最新原則): gpt-6-luna(Production routing相当=比較基準・例外2)、gemini-3.8-flash(最新Flash、別系列検証/独立判定、非thinking+出力上限)。thinking既定モデルは使用せず、前回のdeepseek-v4-pro事故(¥7.4)は再発なし。ledger=kpg02_work/cost_ledger.jsonl(luna ¥10.08・gemini ¥9.85=合計¥19.92、77 call)。

## 7. 次の一手(Fable判断材料)と採用時のユーザー判断
**D''案(D'+別系列最終ゲート)の仮説検証(API 0の概算)**: 既存の独立判定(gemini)をそのまま選定ゲートに使うと、D'の8ケースは26/30(87%)・3件以上7/8ケース、失われるSonnet OKはG1のみ。**ただし判定者=評価者が同系列のため循環**しており、独立評価(Sonnet/Fable別基準)が必要。費用+約¥0.2/レベル。D'の8ケースは既にgemini判定済みのため追加費用なしで再集計でき、残り8ケース(aiisland_b1b・surname_b1b・melos_a2/b1b・ignobel×2・tesla_b1b・moon_a2)の全工程実行に約¥15〜17(Cap追加要)。
採用時のユーザー判断事項(UDR #227、分類D): (1)display_form新許容ルール(something化・後続名詞句除去・意味修飾語保持)、(2)7件未満の容認(D'平均5.25件)、(3)G1型の方針(F=現行/G=一般化すれば塊。D'は和集合でG寄り)、(4)費用+約¥1.6〜3.6/記事セット(既存段置換による相殺は未確認)、(5)追加Trial(D''、約¥15〜17)のCap。

## 8. 限界・未確認
- 未実行: 6ケース(aiisland_b1b・surname_b1b・melos_a2・ignobel_a2/b1b・tesla_b1b)とmoon・melos_b1b(X月・Z追加)、再実行ばらつき、D_sol。いずれも費用上限(¥20)到達による。
- 判定はSonnet実読の一次判定(最終はFable)。geminiゲート案の87%は同一judge由来で上振れの可能性。

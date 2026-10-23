# TRIAL_RESULT_02: Std日本語意味・Adv英語説明の品質改善Trial(委任_07、2026-10-23、DEV er112基盤、Production変更0)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 / 設計=`DESIGN_04.md` / Opus=`OPUS_REVIEW_03.md` / 生データ=`er112_output/kp_gm_trial_02/`(results.jsonl, judge/, paid_calls.jsonl, e2e_kp_expl_02.jsonl, fable_sampling_list_02.md) / 代表例=`TRIAL_02/REPRESENTATIVE_01.md` / 正解ラベル案=`TRIAL_02/GOLD_LABELS_DRAFT_01.md`
使用model: 生成=gpt-6-luna(本番と同じ)、Std比較=gpt-6.1-sol(最新世代、Production routingで既に承認済みのmodel)。Judge=claude-sonnet-5-5 と gpt-6.1-sol(いずれも評価用の最新世代、25節)。
費用: **68.98円/上限70円**(luna gloss 5.37・Sol gloss 18.24・Adv生成+E2E 8.32・Judge Sonnet 31.63/Sol 5.40・repair 0.03)。累計55円到達時点(Judge段階)で完成見込み約67〜69円と再計算し、70円以内のため停止せず続行した(予算警告の条件=70円超過見込みに該当せず)。

## 0. 結論(先頭)

1. **Std(日本語意味)は改善した。** 新規生成項目の目標を「英和辞典の定訳→対応する日本語慣用句→無ければ中心義を平易に」に変え、同一call内で2〜3案から選ばせる方式(G3、luna)で、`draw a line`は3回とも慣用義(区別をはっきりさせる/境界をはっきりさせる/一線を引く)。現行(G0)は「線を引く」2回(字義でNG)・「一線を引く」1回。難例20+通常6(n=26)でJudge合格率 G3=96%(25/26、CI 81-99) / G0=85%(22/26) / G2(用法先決め)=85%。KP単位flip G0→G3は改善3・悪化0・不変23。残る不合格はG3で1件(apply one's findings、「自分の」逐語)。
2. **「モデルの判断力が律速」(DESIGN_03仮説)は支持されなかった。** 上位model(gpt-6.1-sol)のG0同条件は10/12でluna G0 9/12とほぼ同じで、luna G3(11/12)に及ばない。Solは1call 1.1〜1.6円(luna約0.09円の12〜18倍)で、**律速はmodelでなく生成目標の種類だった**。Sol化(+約1.9円/セット)は不要。→ OF-15の費用低減候補は『G3(lunaのまま、費用差ほぼ0)』が最良。
3. **Adv(英語説明)は、統計的に有意な改善を確認できていない。** glossを外すE1は現行E0と同等(KP単位flip 改善4/悪化3、PASS3 80% vs 78%)。E1+core_sense(E1c)は悪化傾向(6/8)。usage_type先決めのE4は+8〜10pt・flip 7:3(難例20+通常30、n=50でPASS3 86%[CI 74-93] vs E0 78%)だが、CIが重なり有意ではない。Opusの読み(E4の悪化は『用法先決め』が原因)に対し、本Trialの修正後Judgeでは**E4が最良の傾向**で、E1型(要因分解の第一候補)は効果なし。ただし**Judge自体の信頼性が低く**(下記)、Adv側の差はJudge雑音の範囲内の可能性が高い。
4. 副次: Std gloss自体を良くするとAdvも良くなる経路が観測された。`draw a line`のAdvは、G2 gloss(「境界をはっきりさせる」)を入力するE0で3/3合格、G0 gloss入力のE0は1/3、E1(gloss無し)も1/3。glossは『悪い含意』だけでなく『良い含意』も運ぶ(一方向の伝染を断つ=必ず良い、とは言えない)。
5. **目的(Key Phrase意味・説明の要求品質到達)は、Stdは到達候補、Advは未到達(判定不能を含む)。** 手段(Trialを実施し計測した)の成功と、目的(ユーザー§2の要求品質を安定して満たす)の達成は別。Closeしない。

## 1. ユーザー検証項目1〜6との対応

| # | 項目 | 結果 | 判定 |
|---|---|---|---|
| 1 | `draw a line`のStd日本語 | G3: 区別をはっきりさせる/境界をはっきりさせる/一線を引く(3/3慣用義)。G2: 境界をはっきりさせる×2/はっきり区別する(3/3)。G0(現行): 線を引く/一線を引く/線を引く(字義NG 2/3)。Sol: G0-sol 線引きをする×2/境界をはっきりさせる、G2-sol 許される範囲をはっきりさせる/区別をはっきりさせる×2(3/3) | **達成(G3/G2)**。3回目の『一線を引く』は慣用義だがOpus指摘のとおり『許容の限界』含意が強い(Fable確定要) |
| 2 | 同KPのAdv英語 | 3rep合格: E0@G0 1/3、E0@G2 3/3、E0@G3 1/3、E1 1/3、E1c 1/3、E4 2/3。失敗は『between what is acceptable and what is not』(core混入)と『a clear difference between two things』(語義が弱い)型 | **未達**(安定して満たすarmなし。E0@G2のみ3/3だがn=3でG2をStdに採るかは別判断) |
| 3 | 他の慣用句・句動詞・一般表現 | 難例20(慣用句・句動詞・多語動詞句中心)+通常55。下記§2・REPRESENTATIVE_01 | 部分達成(Std改善、Advは差なし〜E4が微増) |
| 4 | 既に正しい説明を壊さない | 通常KP55: E0@prod→E1 flip 改善2/悪化2、E1c 改善4/悪化8。通常30のPASS3はE0 80%→E4 87% | E1は壊さない、**E1cは壊す傾向**、E4は壊さない傾向 |
| 5 | X/Z双方 | Std/Advともhard20にX16/Z4、通常にX40/Z15を含む。E2E KP説明段はX12+Z8バッチ | X/Zとも失敗は同種(固有人名を含むZの通常KPで悪化なし) |
| 6 | retry/fallbackを含む量産条件 | `generate_kp_explanations`(Production関数、call_fnのみDEV注入)でX12+Z8実バッチ×3arm: E0 78/78 OK(QA起因retry 1)、E1 78/78 OK(retry 0)、E4 78/78 OK(retry 0)。parse失敗0、語数最大15(上限15内)、新規Fact fallback発動0。E4生出力のkey順=phrase→usage_type→core_sense→english_explanation(全20バッチ)。ProductionのStop/NGは0 | **KP説明段は達成**。記事全体のtext E2E(X1+Z1、Writer含む)は**予算のため未実施** |

## 2. 数値(Sonnet Judge E3定義、PASS3=sense_ok&core&single、rep1、難例20+通常30=n50。通常のE0はproduction gloss入力、難例のE0はG0 gloss入力)

| arm | n | PASS3 [Wilson 95%] | sense_ok | core不良率 [CI] | single |
|---|---|---|---|---|---|
| E0(現行) | 難例20+通常30 | 39/50=78% | 47/50 | 14% | 47/50 |
| E1(gloss無) | 50 | 40/50=80% [67-89] | 50/50 | 16% [8-29] | 48/50 |
| E1c(+core_sense) | 50 | 37/50=74% [60-84] | 48/50 | 16% | 47/50 |
| **E4(+usage_type+core_sense)** | 50 | **43/50=86% [74-93]** | 50/50 | **8% [3-19]** | 47/50 |
| E0@G2 / E0@G3(難例+Std通常) | 22 | 19/22 / 17/22 | 22 / 19 | 14% / 9% | 22/22 |

KP単位flip(改善/悪化/不変): E0→E1 (4/3/43)、E0→E1c (6/8/36)、E0→E4 (7/3/40)、E1→E4 (6/3/41)。いずれもMcNemar型で有意でない(E0→E4 片側p≈0.17)。3rep自己一致(難例20、3回とも同判定): E0@G0 13/20、E1 12/20(約65%=Opus11の『同armでも揺れる』を再確認)。3rep平均PASS3(難例): E0 45/60=75%、E1 45/60=75%。
事前宣言の許容差(±10pt以内かつflip比2:1未満=差なし)に照らすと、E1・E1cは『差なし/悪化傾向』、E4は『改善傾向(flip 7:3は2:1を僅かに上回る)だが有意でなく判断保留』。
基準(DESIGN_03 §6-4)との対応: 基準1(sense_ok≥90%) E4/E1とも100%で達成(Sonnet)。基準2(core混入≤5%) E4でも8%で**未達**。基準3(over_generalは信頼できず参考値)。基準4(Std/Adv整合100%): 下記で未達(P判定85〜90%)。基準5(非劣化): E1は通常で不変、E1cは悪化。基準6(draw a line Std3/3, Adv3/3): Std達成/Adv未達。基準7(逐語gloss≤10%かつG0比半減): G3 literal不良0件(literalは全arm0)、deictic不良がG0 3→G3 1。基準8(single≥95%): E4 94%/E1 96%。基準9(X/Z双方): 難例のZはsentence someone to death/pull someone under/execution bell/letter of introductionの4件で、同傾向。

## 3. Std/Adv整合(矛盾件数、Sonnet1系統、難例20)
- G3+E4: 矛盾2/20(carry the load『字義と比喩で食い違い』、take the wheel『日本語は字義、英語は比喩』)。いずれも正解ラベルが曖昧なKP(GOLD_LABELS_DRAFT_01で『Fable確定要』)。
- G0+E0@G0(現行): 矛盾3/20(draw a line『日本語が字義の線引き』、reach for someone's wallet『説明が字義的な窃取含意』、carry the load)。
- 難例で1件以上出たため、OF-09の条件付き再整合を『検討する』基準には達したが、2/20はいずれも正解ラベル曖昧KPで、条件付き再整合を入れる根拠は弱い。

## 4. Judgeの信頼性(重要な限界)
- 2系統Judge(Sonnet/Sol)の重複行(Advの難例57行): sense_ok kappa -0.03、core 0.40、single 0.30、over_general -0.03、総合PASS一致40/57(kappa 0.23)。Sonnetはover_generalを10件flagしSolは1件。同義の文でflagが割れる例(jump to conclusionsのE1/E0とE4)があり、**over_generalは使えない**。Std(G)の重複7行は全項目一致(kappa 1.0、ただしn=7)。
- したがってAdv側の差(特に78→86%)はJudge雑音の範囲内の可能性がある。Fable目視サンプル`fable_sampling_list_02.md`(104行=無作為20%+Judge不一致20行、arm伏せ)で最終確認が必要。
- **未実施**: probe-03既存行の再判定キャリブレーション、Judge再判定一致(約30行)、Fable確定後のgold差分再判定、正解ラベルに対する2系統Judgeのkappa(代わりにJudge同士のkappaを報告)。いずれも予算(上限70円)優先で省略した。
- E3-sol(Sol gloss固定)・G3-sol: Solが難例で用法を『ほぼ正しく』判定したとは言えない(10/12)ためOpus条件(14)に従い未実施。

## 5. Sol費用実測と70円目標への影響(OF-15)
Sol gloss 1callは1.13円(2048in/299out、単一KP)〜1.6円(2KP)。難例11 KP+draw a line 3rep×2armで14回18.24円。1記事セットのStd glossをSol化すると約+1.1〜1.9円/セット(70円目標の+1.6〜2.7%)。効果はluna G3以下のため**採否比較表の推奨はG3(lunaのまま、費用差≈0〜+0.001円/セット)**。

| 候補 | 効果(n=26 Std) | 費用差/セット | 備考 |
|---|---|---|---|
| G0(現行) | 85% | 0 | draw a line字義NG |
| **G3(luna)** | **96%** | ≈0 | 新規生成項目のみ。同一call内2〜3案。Prompt追加(承認要) |
| G2(luna) | 85% | ≈+0.001円 | 悪化1(pump one's fist) |
| G0-sol | 10/12(83%) | +約1.1〜1.9円 | luna G0と同等 |
| 慣用句辞書 | 未測定 | 整備費大 | G3で足りたので現時点で進言不要 |

## 6. 残リスク
(1)Adv側は有意な改善なし・Judge信頼性低。(2)G3は新規生成(current=null)項目のみ対象。既存glossの書換え経路(current_japanese_glossあり)は未検証。(3)Carry the Loadは全armで字義『荷物を運ぶ』(正解ラベル曖昧)。(4)通常KP6件のみで通常Std汎化は小n。(5)記事全体のtext E2E未実施。(6)G3の『brace yourself for→～に備える』『keep someone company→人の相手をする』など、G0より薄い訳が混じる(Judgeは許容、Fable目視推奨)。(7)単一KP/1〜3KPバッチでの検証で、5KP等の本番バッチと完全同一ではない(Production関数`generate_kp_explanations`自体は実バッチを使用)。

## 7. 自己判定
- **Std(G3): VALIDATED候補**(ユーザー要求『区別をはっきりさせる』級の訳が3/3、悪化0、費用差≈0)。ただし根拠はn=26・Sonnet1系統が中心(Std重複Judge n=7)・gold未確定。Fable目視とgold確定後に最終判定。Production採用はユーザー判断(Prompt変更を伴う)。
- **Adv: 目的未達/判定保留**。E1(要因分解の第一候補)は効果なし。E4は改善傾向だが有意でなく、Judgeの信頼性が不足。推奨は『Std G3を先に採否判断へ提示し、Advは現行維持のままE4をn拡大+Judge改善(gold確定・Fable目視)で再検証』。USER_DECISION_REQUIRED候補: (a)Std G3の採否(Prompt変更・新仕様)。Adv側は判断材料不足のため現時点で判断候補にしない(Closeしない)。
- 方針転換の進言: Adv側は『Std glossを良くするとAdvも良くなる』(E0@G2 3/3)を考慮すると、Adv説明のPrompt/構造変更より『Stdを先に直す→Advを再測定』の順が合理的(G3採用後の再測定をAdv検証の第一手にする)。

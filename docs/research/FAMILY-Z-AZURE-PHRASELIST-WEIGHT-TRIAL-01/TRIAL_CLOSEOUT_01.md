# TRIAL_CLOSEOUT_01: Azure PhraseList重み比較Trial(FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01、委任_02b)

到達Status: `PLW_TRIAL_CLOSEOUT_PENDING_FABLE`。eval機械判定=**REJECTED**(Fable最終ラベル前。`USER_DECISION_REQUIRED`ラベルはFableのみ)。Production非変更(`er006_secondary_asr_01.py`含むProduction module・Prompt・判定・設定は無変更、`git diff a21103942 HEAD --name-only`のうちer084_*・docs・user_test/plw_trial_01・委任文ログ以外=0件)。Production採用提案ではない(REJECTED案のため条件Cレビュー対象外)。
**適用範囲(S-6の限定文言)**: 本結果は「**Melos・Family Z・2 Voice(Aoede/Charon)・ナレーター経路(flash-lite+PD06)・Azure en-US**」に限る。他の固有名詞(長い多音節語・CMU辞書に無い短い名前・一般語と同音の名前)への一般化は未検証(本文clipにMelos以外のPL対象名が無く、一般化probeは対象takeなしで0本)。
使用モデル(開発・評価の最新モデル原則、25節): TTS=`gemini-3.8-flash-lite-tts`(最新世代flash-lite、Production同一)、Primary=OpenAI `gpt-4o-mini-transcribe`(Production同一・prompt無し、rawに記録)、Secondary=Azure Speech en-US(SDK 1.50.0、連続認識)。旧/下位モデルの使用なし。
詳細: 設計=`TRIAL_DESIGN_01.md`(v02)、Phase A=`PHASE_A_RESULT_01.md`(+v02再注入)、Phase B=`PHASE_B_RESULT_01.md/.json`、Opus_J逐語=`OPUS_REVIEW_J_01_VERBATIM.md`、試聴=`user_test/plw_trial_01/`。

## 1 結論

**重みを1.5/2.0へ上げても、不要なTTS再生成・Human Reviewの削減効果は小さく、誤発音を見逃すリスクが増えるため、重み変更は有効とは言えない(REJECTED案)。現行(重み未指定=1.0)のPhraseListは既に大きく効いており、現状維持が妥当。**

- 効果が小さい: Primary(OpenAI)がMelosを正転写できない正例35wavのうち、**現行(重み未指定)で既に26wav(74%)がAzure確認で本番判定PASS系**になる。残るNGは9wav(R=9)で、重み1.5で直ったのは**1wav**(P1 take3)、重み2.0で**2wav**(+P5)。悪化(PASS→NG)は0。片側符号検定 p=0.50(1.5)/0.25(2.0)で偶然と区別できない。効果量の基準(up≥3かつ≥0.30×R)も満たさない。
- 副作用が出る: Melosと読んでいない音声(許容外母音`Mullos`のminimal pair)を、重みを上げるとAzureが`Melos`と転写し、本番判定が**誤PASS**にする例が新たに出た(有効負例33wavのうち、1.5で+1件、2.0で+3件。いずれも`Then Mullos walked away.`)。現行(重み未指定)ではこの4wavはNG。「認識率が上がっても誤発音を見逃す危険が増えるなら成功としない」というユーザー基準に照らし、重みを上げる側にリスクがある。
- 現行の仕組みの価値は高い: PhraseListなし→現行(重み未指定)で、本番判定は**15wavがNG→PASS系に改善、悪化0、有効負例の誤PASS増0**(8→8。この8件はPrimary側/現行判定で既に通る別要因)。Melos正認識率は合算50wavで32%→68%。
- 残るNG(9wav)は重みで解決しない: 重み2.0でも7/9(78%)がNGのまま。典型は`Melos drank`→`Mellow strength`のような語境界の誤分割、`Melo spoke`、長尺clip(>15秒の4本はMelos正認識0→1/4)で、PhraseListの重みでは直らない音響・分割側の失敗(Primary/Azure両方が失敗するためTTS再生成=現行のRetryが適切)。

## 2 条件別認識率(Melos正認識、rep1、wav単位)

| 集合 | no_pl | pl_unspecified(現行) | pl_w1.5 | pl_w2.0 |
|---|---|---|---|---|
| 正例・合成30 | 8/30(27%) | 20/30(67%) | 22/30(73%) | 25/30(83%) |
| 正例・本番take20(Primary NG系を再利用) | 8/20(40%) | 14/20(70%) | 14/20(70%) | 16/20(80%) |
| 正例・合算50 | 16/50(32%) | 34/50(68%) | 36/50(72%) | 41/50(82%) |

Melos正認識率は重みを上げると素直に上がる(68→72→82%)が、**本番判定の改善は+1/+2wavにとどまる**。理由: 認識率が上がるwavの多くは、現行の重みでも本番判定が既にPASS(Tier3/Secondary確認が`Melos`以外の近似転写でも通る)だったため。「認識率」だけで評価すると効果を過大に見る(Opus_J M-4の指摘どおり主要指標を本番判定flipに置いた)。
本番判定のflip(FULL_STORY role、Primary NGの正例のうち。Tier3なしroleも同数):

| 比較 | up(NG→PASS系) | down(PASS→NG) | 変化なしNG | 変化なしPASS | 片側符号検定p |
|---|---|---|---|---|---|
| no_pl → 現行(参考) | 15 | 0 | 9 | 11 | (参考) |
| 現行 → pl_w1.5 | 1 | 0 | 8 | 26 | 0.50 |
| 現行 → pl_w2.0 | 2 | 0 | 7 | 26 | 0.25 |

判定基準(§3-v02): 1識別力(R=9≥6)=○ / 2効果量=×(up 1/2 <3) / 3有意性=× / 4広がり=×(up wavがclusterの1〜2種) / 5副作用なし=×(w1.5:+1、w2.0:+3の新規誤PASS、Azure誤Melos+1/+3) / 6悪化なし=○ / 7 Tier3なし非逆転=○。→ 2を満たさないため`REJECTED`(R≥6なので`INCONCLUSIVE`ではない)。
録音2(Phase A基準wav、確認集計から除外・参考値): v02再注入で、FULL_STORY roleでは**w1.5・w2.0とも3/3 PASS_WITH_WARNING**(旧v01判定ではw2.0は3/3 NG_BOTH。Tier3がdiff位置1語だけを見るため`onto→unto`は効かない=Opus_J M-1の予測が実機で確認された)、Tier3なしroleではw1.5のみPASS。現行(重み未指定)は両roleとも3/3 NG_BOTH。つまり**録音2は重みで救える稀なケース**だが、本Trial全体の代表ではない(選択バイアス)。

## 3 文脈別の効果とばらつき

(Melos正認識数。詳細=`PHASE_B_RESULT_01.md` §3b)
- 文脈: P2(歯擦音後続)は現行0/3→w1.5で1/3→w2.0で3/3、P5(複数出現)は0/3→0/3→1/3と**文脈で反応が異なる**。一方P3(文末)・P4(文中)・P6(長文)・P7は現行で既にほぼ全て正認識(重みの余地なし)。P1(非歯擦音後続、4take×Voice)は現行8/12→9/12→9/12。
- Voice/話速: Aoede通常 6→8→9、Aoede減速 6→6→7、Charon 8→8→9(いずれもn=10)。減速音声は重みの恩恵が最も小さい。
- 本番take(長さ別): ≤5秒 9→9→10(n=11)、5〜15秒 5→5→5(n=5)、**>15秒 0→0→1(n=4)**。長尺で重みが効かないのが、HR Lockの原因だった長尺clip(part3_c1)の失敗と整合する。
- 決定論: 抜き打ち9wavで全条件rep1=rep2の転写が一致(45/45)。`pl_w1.0`と`pl_unspecified`(送信バイト同一)も9/9一致=Azureは同一wavに対し決定論的で、条件間差は純粋に条件(重み)由来。wire証拠: 全410呼出の`speech.context`の`bias`が要求した重みと一致(no_plはdgi無し、不一致0)。
- take差は大きい: P1の同一文4take(Aoede通常+減速)のうち、take1とtake3(減速)は`Mellow strength`で全条件NG(重みで直らない)、take2・take4は現行で既に救済済み、重みで新たに救えたのはtake3(通常)のみ。up wavは1つのcluster(P1)に集中(top cluster share=1.0)。重みの効果よりtake(音声)の個体差が大きい(H3を支持)。

## 4 副作用(他語perturbation・負例)

- 他語perturbation(M-5、89wav): 重み1.5/2.0で新規に増えた「Melos以外の誤り語」は**各2語**(うち保護対象1件=内容語。数値・否定・固有名詞への影響0)。Melosから平均5語離れた位置で、判定をNGに転じたケースは0(down=0)。重みは他語の転写をほぼ乱さない。
- 負例(有効33wav = N1・N3の6wav + minimal pair 27wav):
  - 本番判定の誤PASSは、現行(重み未指定)で8件(N1/N3の全6件+`Mullos`のP3 2件)。**これはPrimary側/現行判定で既に通る別要因**(Melosの別読み`mellow`等をLedger許容集合が通す。Azureの重みとは無関係で、no_plでも8件)。
  - **重みが新たに作った誤PASS(ベースラインNG→PASS)**: w1.5=1件、w2.0=3件(rule of threeは非0のため非適用)。例: `Then Mullos walked away.`(Primary`Molos`/Azure現行`Molos`→w2.0で`Melos`)。Azure誤`Melos`件数: 現行2→w1.5で3→w2.0で5(/33)。
  - 境界例(N2 mellows / N4 Milos、判定には不使用): N2は全条件でMelosと出ず、N4`Milos`は**w1.5・w2.0でAzureが`Melos`と出し、本番判定もPASS**(3/3)。N4はLedger別読み/ˈmɪlɒs/に近く「誤認識と言い切れない」例で、かつ重み1.0では起きない=重みが近似固有名詞を引き寄せる傾向を示す。
- 判定整合(11-8): 副作用の「見逃し」は重みを上げる側にのみ発生し、現行側に増加はない。

## 5 録音2の改善

上記§2のとおり(Phase A v02再注入)。FULL_STORY roleで現行3/3 NG_BOTH→w1.5・w2.0とも3/3 PASS_WITH_WARNING。ただしこれは1wavの基準条件で、Phase Bの本番take20本(同じ失敗パターンを含む)では重みの効果は上表のとおり小さい。録音2のHR Lock(旧v01で『w2.0は効かない』と見えた点)は、judgeがTier3を通らない欠陥による見かけ(M-1)だった。

## 6 本番判定・TTS再生成・HR削減への実効性

- Primary NG 35wavのうち、現行で本番判定NGのまま残る9wav=**clip全体の18%**(35/50のPrimary NGのうち26が現行PASS)。この9wavは現行ならTTS再生成(最大2 attempt、次に最終slotならHR)へ進む。
- 重み1.5で救えるのは+1wav(clip全体の2%)、2.0で+2wav(4%)。一方、誤発音を見逃す方向のリスク(+1/+3 / 33負例=3%/9%)が出る。**得られる削減(+1〜2/50)よりも誤PASSの増加(+1〜3/33)の方が大きく、割に合わない**。
- 「HRを減らせるか」の推定: 本Trialでは`ng_would_hr`(最終slot換算)を保存。現行NG9wav=HR候補9→w1.5で8→w2.0で7。いずれも有意でない。重み調整は、TTS再生成・HR削減の主要手段にならない。

## 7 QCD実費(JPY)

| 区分 | 内容 | JPY |
|---|---|---|
| Azure STT Phase B | 410呼出・2,073.8秒(1回再開含む。重複0) | 92.17 |
| TTS(追加負例18 take、flash-lite STANDARD、tokens in166/out1290) | | 約1.25 |
| OpenAI Primary(追加27wav) | | 約0.62 |
| 本委任(02b)合計 | | **約94.0**(Fable上限JPY200・T-3 Guardrail内、超過なし) |
| 案件合算(委任_01〜02b) | 20.91 + 94.0 | **約114.9**(300円以下) |
| 当日累計(JST 2026-10-20、`daily_dev_cost_01.py`) | 他タスク28.79を含む | 143.5(日次1,000円以内) |

量産単価(70円/記事セット目標): 重み導入は`setWeight`1行でAzure呼出回数・秒数は不変=追加費用0だが、効果が小さいため便益側もほぼ0。変更しないことによる費用増なし。Q: 品質面ではむしろ誤PASS増のリスク。D: Phase B実走は逐次約15分(09:36〜09:50 JST)で完了。

## 8 成果物・Git・SSOT

- 設計書v02: `TRIAL_DESIGN_01.md`(§2-D〜§2-F、§3-v02、§9改訂履歴)。閾値正本=`criteria_thresholds_01.json`(v02)、`design_matrix_01.json`(v02)。
- 判定是正+golden replay test: `er084_azure_phraselist_weight_trial_01_judge.py` / `..._judge_test_02.py`(run_e2e_04 part3_c1 attempt2[Primary`Mello`/Azure`Mellows`→tier3 step→NG_BOTH]、run_e2e_05 Std減速後[`Mellos`/`Melos`→SECONDARY_ASR_CORROBORATED_MATCH→PASS_WITH_WARNING]を再現、副作用ファイル5種のsize+mtime不変)。
- 評価: `er084_azure_phraselist_weight_trial_01_eval_v02.py`(+test 25件)、結果=`PHASE_B_RESULT_01.md/.json`。生ログ=`er084_output/azure_phraselist_weight_trial_01/raw/azure_calls.jsonl`(Phase B 410行、除外なし、err 0)。追加負例manifest=`wav/manifest_02.json`、本番take集合=`production_takes_manifest_01.json`(20 take、209秒)。
- 試聴ページ: `user_test/plw_trial_01/index.html`(19件: flip 2、負例の誤PASS・誤Melos 11[★=重みで新たに生じた4]、境界例6)。
- SSOT: OPEN-424 / DECISION_LOG / USER_DECISION_REGISTER #124 / REPORT_LEDGER / OPUS_FINDINGS_LEDGER(OF-PLW-J-01〜13)。

## 9 推奨案と判断候補

推奨: **重みは変更しない(現行の未指定=1.0を維持)。Trial StatusはREJECTED案。**
- Production側に変更不要(`er006_secondary_asr_01.py:288`のコメント『SDKは重みAPI非公開』は事実誤認で、SDK 1.50.0は`setWeight`(0〜2)を持つ。コメントの訂正は将来の保守タスクとして別途、本Trialでは触らない)。
- 判断候補(ラベル無し、Fableが整理): (a)REJECTEDで閉じる(推奨、データは十分: 決定論・文脈多様・負例33・本番take20)。(b)重み1.25/1.75の追加は**推奨しない**: 1.5で+1、2.0で+2とどちらも基準の3に届かず、副作用は重みに単調に増える(+1→+3)ため、中間値でup≥3かつ副作用0となる見込みは低い(S-5の『トレードオフが見えた場合のみ判断候補』にも、効果が小さいため該当しない)。実施するなら承認3値以外のため別途ユーザー承認が必要。(c)長尺clip(>15秒)や語境界誤分割(`Mellow strength`)の失敗は重みでは解決しない=別原因の調査(例: clip分割長、ASR segmentationの観測)を別管理IDで検討する余地。ただし新仕様の採否はユーザー判断で、本Trialは実装しない。

## 補足: Production採用提案時に必要な追加証拠(条件C向け。REJECTED案のため現時点では不要)
もし将来重み変更を提案する場合は、(i)他の固有名詞3系統(長い多音節語/CMU辞書に無い短い名前/一般語と同音の名前)でflip・負例を測る、(ii)対話経路(Production ZのCharon)での再現、(iii)Primary NGが本番で実際に起きた分母(R)≥30程度での有意性、(iv)現行比で誤PASS増0を複数Voiceで示す、が最低限必要。

## 5分類(S-8)への対応(ユーザー原文§6)

| 観点 | 判定 | 根拠 |
|---|---|---|
| 条件が簡単すぎて差が出なかったか | **一部該当** | Primary NG 35wavの74%が現行で既にPASS(改善余地はR=9のみ)。ただしR≥6で識別は可能 |
| Phrase Listがほとんど効いていないか | **否** | PL自体(no_pl→現行)で15wavがNG→PASS、転写変化率23%、Melos正認識32→68% |
| 既に1.0で十分か | **概ね該当** | 現行で残るNG 9wavのうち重み1.5/2.0が直すのは1/2wavのみ |
| 文脈・音声品質で効果が変わるか | **一部該当** | P2/P5は2.0のみ反応、減速・長尺(>15秒)は効かない。ただしup wav数が少なく有意でない |
| 実用上、重み調整では解決できないか | **該当** | 残NG 7/9が重み2.0でも不変(語境界の誤分割・長尺)。重みを上げるほど近似発音の誤PASSが増える |

# BUDGET_LOG_01 (委任_22 Trial_05 Stage 1 + held-out の一部。個別枠8.33円=Trial_04枠残3.43+rep2枠残4.90)

台帳: `er112_output/kp_gm_trial_05/paid_calls.jsonl`(全API呼出を1行ずつ、65行。reasoning_tokens付き)。使用モデル: 生成=`gpt-6-luna`、reasoning effort=**high固定**(最新世代の最上位系ではない。25節の例外理由=評価対象がluna生成の品質そのもの[Production系列と同一、Trial_04と同条件]。判定=Fable盲検でAPI 0、Sonnet参考Judgeは不使用)。
日次(JST 10-24)開始時累計=281.78円(`daily_dev_cost_01.py`、採用値=max(log,ledger))。本委任の有料分=**6.252円**(累計 約288.0円、日次上限1,000円内)。案件累計は委任_21までの約270円+6.25円≒276円(7-7の300円以内、Fable見込み)。

| 区分 | 呼出数 | 費用(円) | 1call平均 | reasoning_tokens平均 | 備考 |
|---|---|---|---|---|---|
| R B0(3rep新規) | 12 | 0.688 | 0.0573 | 361 | pilot1callを含む |
| R M(rep3新規) | 4 | 0.210 | 0.0524 | 335 | Trial_04の既存2repを参照 |
| R X1(3rep) | 12 | 0.785 | 0.0654 | 527 | |
| R X2(3rep) | 12 | 1.567 | 0.1306 | 1,206 | pilot0.2089円・rep2 draw a line 0.2246円が0.20円超(平均は0.131円=見積0.16円以内) |
| R Cp(新規) | 5 | 1.212 | 0.2424 | 2,308 | **rep1 4call+rep2 1call。平均0.242円が0.20円超のため自動停止(HALT)。rep2残3+rep3 4=7callは未実行** |
| held-out B0(10KP 1rep) | 10 | 0.598 | 0.0598 | 234 | |
| held-out X2(10KP 1rep) | 10 | 1.193 | 0.1193 | 915 | |
| held-out Cp | 0 | 0 | - | - | **未実行**(見込み約2.4円=残枠2.08円を超過) |
| **合計** | **65** | **6.252** | | | 上限8.33円内(残2.08円) |

## 見積りとの差(正直な記録)
- 見積り(TRIAL_DESIGN_05 §4): X2 0.16円/call(実測0.131円、内)、B0 0.07(実測0.057)、X1 0.045(実測0.065、Production互換欄追加で+45%)、**Cp 0.18円(Trial_04平均)→実測0.242円(+35%)**。Cpは1回のcallで0.098〜0.359円と変動が大きい。
- 当初の予定一式(R: B0/M/X1/X2/Cp 各3rep、held-out 10KP x B0/X2/Cp)の実測単価ベース見込み総額≒10.5円(R 約8.2円[うちCp約3.6円]+held-out約4.3円)>8.33円。**超過見込みのため、Cpの残りとheld-out Cpを停止**(分割・日付分割による回避はしていない)。
- pilot上限0.20円/callの扱い: X2 pilotは0.2089円(+4%)、Cp pilotは0.283円(+42%)で閾値超。判断=X2は後続の平均が0.131円で見積内に収まる(平均で判定)として継続、Cpは平均0.242円>0.20円のためコード側の自動停止規則(arm平均>0.20円 or 単callが0.40円超)で停止。**閾値を引き上げて継続はしていない**。
- Cp rep2の残りと rep3、およびheld-out Cp: 追加見込み約4.1円(Cp R 7call 約1.7円+held-out Cp 10call 約2.4円)=合計約10.5円で枠8.33円を約2.2円超過 → Fable判断(判断候補)。

# 委任_23 追記(Fable判断(a)によるCp完遂。2026-10-24)
- Fable判断: Cp R残り7call+held-out Cp 10callを実行。個別枠8.33円超過(約2.1円まで)は案件累計約280円<300円・承認済みScope内の7-7 Fable自律判断。Cp armの平均閾値(PER_CALL_ARM)を0.20円→**0.26円/callへ一時引上げ(Cp armのみ・本委任限り、`er112_kp_gm_trial_05.py` PER_CALL_ARM)**。他armは0.20円不変。理由=Cpの推論token増による単価(Trial_05前半でreasoning_tokens平均2,308)。cap=11.25円(既使用6.252+5)を引数指定。
- 実行: `gen --arm Cp --set RCORE --reps 2,3`(7call、1.047円)、`gen --arm Cp --set H --reps 1`(12call、1.698円)。使用モデル=gpt-6-luna effort=high(Trial_04/05と同条件、25節例外=Production系列評価)。再起動なし、HALTなし。
- 費用: 追加19call **2.545円**(1call平均0.134円、reasoning_tokens平均1,085)。台帳は計84行、累計 **8.797円**(個別枠8.33円を0.47円超過、Fable許容上限〜10.4円内)。Cp全24callの平均は0.157円(旧閾値0.20円も下回る=今回の閾値引上げは結果的に未使用)。見込み約4.1円に対し実測は小さい(前半5callのreasoning 2,308が後半19callで1,085に低下=出題KP/repによる変動)。
- 誤り(正直な記録): held-outを `--nheld 10` 指定なしで実行したため余分2call(`jump into action`0.095円、`feel borrowed`0.248円=0.343円)。盲検・集計はオリジナル10KPのみ。
- 日次(JST 10-24): 開始時の281.78円(委任_22で6.25円加算済み=約288.0円)+本委任2.545円 = **約290.6円**/1,000円。案件累計は約276円+2.5円≒**約279円<300円**。
- 台帳 `er112_output/kp_gm_trial_05/paid_calls.jsonl`(84行)。

# 委任_25 追記(X2p。2026-10-24)
- 実行: pilot 1call(`an unseen clock` rep1、0.1236円)->`gen --arm X2p --reps 1,2,3 --set R`(pilot分は再利用、12 job)->`gen --arm X2p --reps 1 --set H --nheld 10`(10 call)。cap=12.80円(開始時累計8.797+上限約4.0)、workers=2、再起動なし、HALTなし、Cp閾値は0.20円に戻した。
- 費用: X2p 23 call **3.247円**(1call平均0.1412円、reasoning_tokens平均1,240)。台帳 `er112_output/kp_gm_trial_05/paid_calls.jsonl` 累計 **12.044円**(個別枠8.33円を3.714円超過=Fable委任_25で承認済みの約4.0円内)。
- 日次(JST 10-24): 開始時約290.6円+3.25円 = **約293.8円**/1,000円。案件累計 約279円+3.25円 = **約282.3円<300円**。
- 使用モデル: gpt-6-luna effort=high(最新系/Production系列、25節例外理由=評価対象がluna生成の品質)。

# 委任_26 追記(Stage 2 X2p。2026-10-24)
- 実行: `gen --arm X2p --set S2 --reps 1 --cap 16.0 --workers 2`(29 job見込み、見積3.64円)。1起動のみ、再起動なし。**cap 16.0円(開始時累計12.044+約4.0)で自動HALT**: 21 jobを完了(43 KP、4.054円、1call平均0.193円)、cum=16.098円(最後の1callでcap超過0.098円)、残8 job(11 KP: play a part/pull back/reach for someone's wallet/step out/stone video/supply chain/take off an ai costume/take the wheel/too broad a label/turn out/weak link)は未実行(SKIP_CAP 1+SKIP_STOP 7)。
- 見積差: 見積0.1254円/call(X2実測)に対し実測0.193円/call(+54%、non-R batchは1callに2〜4KP入り、X2p推論token増)。完走見込み=残8 job約1.5〜1.9円、合計約5.6〜6.0円(見積3.64円の約1.6倍)。
- 累計: 台帳(128行)12.044->**16.098円**。日次(JST 10-24)約293.8->**約297.9円**/1,000円。案件累計約282.3->**約286.4円<300円**(完走しても約288円で300円内)。個別枠8.33円は既に超過(Fable委任_25承認の約4.0円も本委任で追加4.054円使用)。
- 再起動は委任文で許可されていないため未実行(判断候補: 残8 job約1.5〜1.9円の追加実行)。

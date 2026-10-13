# ROUND3_REPORT_01: KP統合最適化 Round 3((b1)LLM補助抽出Trial、Stage 0のみ実施・Stage 1は事前登録Go条件不成立で中止)
管理ID: FAMILY-X-KP-INTEGRATED-OPTIMIZATION-TRIAL-01 委任_03 / 2026-10-13 / Trial専用(Production code/Prompt/DB/gate無変更、音声生成なし、Melos無関係) / **採用判断なし** / Status案=**VALIDATED未満**(Go条件不成立のためb1選定armは未検証。Stage 0の供給品質は小標本で測定済み)
モデル: gpt-6-luna(全18 call、応答model_id実測で全件一致。Production Family X KP選定と同一=最新モデル原則の例外「比較可能性」。最上位系モデルでの検証は未実施)。

## 1. 総括
- Stage 0(b1抽出のみ、選定なし、18呼出、JPY3.46)を事前登録どおり実施した結果、**Go条件(Coffee Adv run1のb1予約3枠に`be behind price increases`系が入る)が成立せず、事前登録の規則に従いStage 1(b1選定arm・対照揃え38 job)を中止した**。残額は使っていない(Round 3実績JPY3.46/上限60、本Trial累計102.46/300)。
- Coffee Adv run1のb1出力は`pumps its fist`(b2と重複)/`in the ring`/`unseen clock of its own`。`been behind price increases`はrun1・run3に無く、run2のみLLMが`had been behind price increases`(5語)で出したが、(i)LLM自身のcore_spanは`been behind`(目的語を落とす既知の失敗3の型)、(ii)縮約ガードで5語spanを維持してもProductionの既存除外gate(`unnatural_out_of_context`)が先頭の`had`で除外した。つまり出力率は1/3で、出ても素のままでは通らない。
- 逐語率は45件中45件(100%)で非逐語STOPは非該当。ただし精度は暫定ラベルで正61%(登録run1の23件中正14/粒度不良7/誤2)。粒度不良の多くは`in the ring`型の断片・副詞や代名詞付き・主語欠落。陰性対照R3で`gets the first word`の偽陽性がPhase Dと同様に再現(3件中、他2件は正当)。
- Round 2までの結論(供給側M2が主レバー、P5はP3より契約遵守を保ちつつpumpを回復)は不変。b1はCoffeeの狙いアンカーに寄与せず、他記事では新規候補を供給するが採用効果は未測定。

## 2. 前提
- ユーザー承認(2026-10-13): (b1)をRound 3のTrialに含める(Trialのみ、Production採用ではない、累計JPY300遵守、結果はTrialステータス)。運用ルール4点(探索Trial一括承認運用)はSSOT(PM_GOVERNANCE 7-8、DECISION_LOG、USER_DECISION_REGISTER)に記録。
- Opus条件Aレビュー反映: M1(Phase D抽出器再利用、REJECTED理由と失敗3件対策を`plan_r3.md`に転記)/M2(Promptに評価語句なし、testで担保)/M3(surface_form逐語、canonicalは(b2)と同関数、選定とcanon PASS別計測、合否基準事前登録)/M4(予約枠の直後にappend、rank上位3の絞り規則事前登録)/M5(Tier H削除記録)/R1(Stage 0先行+Go/No-Go)/R2(`source: llm_aux`非表示・行形式同一)/R3-R7(Std害検出、判定は同等幅±5+CI、per-anchor、`pump`押し出し確認、M2P3削除)/R8(非逐語率分母定義+目視ラベル)。
- 事前登録: `plan_r3.md`(生成前に確定。最初の有料call 2026-10-13 14:40:14より前)。

## 3. Coffee最終5件
Stage 1未実施のためM2+b1の最終5件は無い(測定していない)。既存の対照(M2P0 n=3、M2P5 n=5)の最終5件は`round2/analysis_r2.md`を参照。b1が実際にCoffee shortlistへ足した候補は下記7節の表のとおりで、Std `in the ring just yet`/`its own hidden clock`、Adv `in the ring`/`unseen clock of its own`(いずれも創作比喩・断片系。評価アンカー定義では`creative_metaphor_patterns`に該当し、Importantに入るとNG側)。

## 4. アンカー(Coffee)
| アンカー | b1の供給(Stage 0、Coffee Adv run1-3 / Std run1-3) | 備考 |
|---|---|---|
| `pump one's fist`(rank1) | 6/6で出力(Adv 3/3、Std 3/3)。**全件がb2の`pumps its fist`と重複して除外** | b1は新規供給せず。pump回収は引き続きb2(M2)が担う |
| `be behind price increases`(rank2) | Adv 1/3のみ(run2、`had been behind price increases`、core_spanは`been behind`)。run1・run3は出さず。Stdには本文に無い | run2は既存gate(`unnatural_out_of_context`)で除外。**事前登録Go基準=不成立**。素の4語`been behind price increases`はgateを通る(確認済み) |
| `time lag`(rank4) | b1は出さず(M2側で到達済み) | |
| `push prices up`(rank3) | b1は出さず(断片`prices up`のみ従来どおり) | |
| 創作比喩(評価上はImportant NG) | `in the ring`系 6/6、`hidden/unseen clock`系 5/6を供給 | b1はCoffeeでは創作比喩の候補を増やす方向。Importantに入るかは未測定(Stage 1未実施) |
M2P0/M2P5のper-anchor採用数(分母付き)はRound2の`report_tables_r2.md`と同値(再計算なし)。

## 5. take time型(低優先)
b1は`take time`系を出さない(Coffee 6呼出で0件)。(b2)(c)の機械処理が`take time`型を削除しないtest(`test_take_time_type_not_deleted`)は維持。Round 2のM2P5 Std `take time` 1/5(n=5)が既存の事実。b1選定armは未実施。

## 6. M×P表(既存run、b1なし。Std/Adv別、bootstrap 95%CI)
| 条件 | Std score(n) | Adv score(n) | 合算 [95%CI] | pump Std/Adv | time lag Adv | 低優先枠/run Std/Adv | 全gate PASS Std/Adv | 費用/job Std/Adv | reasoning tok(sel) Std/Adv |
|---|---|---|---|---|---|---|---|---|---|
| M2P0 | 33.3 (3) | 38.0 (3) | 71.3 [69.3, 73.3] | 3/3, 3/3 | 3/3 | 1.67 / 0.67 | 2/3, 3/3 | 0.88 / 0.90 | 3141 / 2842 |
| M2P5 | 32.4 (5) | 34.8 (5) | 67.2 [62.8, 71.2] | 5/5, 4/5 | 5/5 | 1.20 / 0.40 | 5/5, 5/5 | 1.03 / 0.94 | 5756 / 3473 |
| M2+b1 P0 | 未実施(Go条件不成立) | | | | | | | | |
| M2+b1 P5 | 未実施 | | | | | | | | |
- M2P0とM2P5の差(合算4.1点)は事前登録の「|差|≦5点は実質同等」の範囲内。CIは重なる(M2P0のn=3のCIは狭いが標本が小さい)。差の内訳はAdv(`hold on`/`price tag`等の枠)。表は`report_tables_r3.md`、gate内訳(選定INVALID/canon INVALID/Redundancy NG)はRound2報告(P5は0/10)参照。
- 対照揃え(M2P0 n=5化、meta n=4化)は中止したためCoffee M2P0はn=3、M2P5はn=5のまま。比較時は同一n=3の併記が必要(Round 2報告のとおり)。

## 7. Stage 0結果・Go判定、Round 1〜3総括
### 7-A. b1供給品質表(`stage0_analysis_r3.json`、`report_tables_r3.md`)
| 記事 | run1のb1予約(Tier H後) | LLM生件数→accepted | 逐語 | 重複除外 | 目視ラベル(accepted) | Tier H削除(既存) |
|---|---|---|---|---|---|---|
| coffee_adv | `in the ring`, `unseen clock of its own` | 3→2 | 3/3 | `pumps its fist`(b2) | 粒度不良, 正(創作) | 0 |
| coffee_std | `in the ring just yet`, `its own hidden clock` | 3→2 | 3/3 | `pumps its fist` | 粒度不良, 正(創作) | 0 |
| hormuz_adv | `stood at center stage`, `curtain rose` | 3→2 | 3/3 | `gave back` | 正, 正 | 0 |
| hormuz_std | `stood at center stage`, `gave back some gains`, `refuses to stay down` | 3→3 | 3/3 | なし | 正, 正, 正 | 0 |
| meta_adv | `small twist`, `on the other end` | 3→2 | 3/3 | `behind the scenes` | 誤, 粒度不良 | 0 |
| meta_std | `in stock` | 2→1 | 2/2 | `behind the scenes` | 誤 | 0 |
| semi_adv | `skip over this`, `fit for leading roles` | 3→2 | 3/3 | `catches the eye` | 粒度不良, 正 | 0 |
| semi_std | `take the seat`, `switch off quietly`, `feel heavy` | 3→3 | 3/3 | なし | 正, 粒度不良, 粒度不良 | 0 |
| smallbag_adv | `having a big moment`, `carry the mood`, `sits on the throne` | 3→3 | 3/3 | なし | 正, 正, 正 | 0 |
| smallbag_std | `having a big moment`, `on the throne`, `carry the mood` | 3→3 | 3/3 | なし | 正, 粒度不良, 正 | 0 |
- 非逐語率: 45件中0件(出力1件以上の16呼出の累計。出力0件の呼出は2件=陰性対照N1・D5)。STOP(>50%)非該当。rank付けは全呼出で3件(cap)まで出る傾向(Phase D v3と同じ)。
- 目視精度(暫定ラベル、sonnet-worker): 登録run1の23件で正14(61%)/粒度不良7/誤2。全45生件で正31/粒度不良11/誤3(69%)。粒度不良の型: 閉クラス始まりの断片(`in the ring`/`on the other end`/`on the throne`)、修飾語付き(`in the ring just yet`/`switch off quietly`/`skip over this`)、主語欠落(`feel heavy`)。縮約ガード(閉クラス始まりを縮約しない)は4呼出で発動したが、LLMが断片spanを直接出す場合(`in the ring`)は防げない。
- 陰性対照(Phase D記事、各1呼出): N1 Std 0件、D5 Std 0件、D6 Adv 0件(`make up`は既存DB重複)、**R3 Adv 2件(`sleep inertia`=正、`gets the first word`=偽陽性、Phase D R3の偽陽性が再現)**。accepted平均0.5/呼出(Phase D 0.42と同水準)。選定側の挙動は測っていない。
- 揺れ(Coffee n=3): accepted集合のJaccard平均 Std 0.00、Adv 0.28(生span集合 Std 0.07、Adv 0.23)。**抽出の毎回の揺れが大きく、選定に使う1回目に依存する**(事前登録どおりrun1を使用)。
- Tier H削除: 18呼出すべてで既存候補の削除0件、b1自身の削除0件(`tierh_deletions_r3.json`)。
- Go判定: **No-Go**(`stage0_summary_r3.json`の`go`)。理由: Coffee Adv run1のb1予約に`behind price increases`系なし。
- 事後(非登録)観察、¥0(`posthoc_r3.json`、Go判定には不使用): 縮約ガード案D(縮約で末尾を切らない+先頭の有限助動詞を除く)を保存済み出力に再適用すると、Coffee Adv run2のみ`been behind price increases`(rank2)が通る(1/3)。他の全13抽出runは不変。すなわち仮に案Dを採用してもCoffee Advの供給率は1/3で、run1を登録固定する運用ではGoにならない。

### 7-B. 判断用長所短所表(採用判断は書かない)
| 観点 | M2P0 | M2P5 | M2+b1(P0/P5) |
|---|---|---|---|
| 狙いアンカー供給 | pump 6/6(b2経由)、time lag 3/3、`be behind price increases`は不可 | 同左(供給は同一) | b1は`pump`を新規供給せず(b2と重複)、`be behind price increases`は1/3、素のままではgateで除外 |
| score(同等幅±5) | 71.3 | 67.2(実質同等圏) | 未測定 |
| 契約遵守 | canon INVALID 1/6相当 | 0/10 | 未測定 |
| 他記事への効果 | meta concierge 3/4 | 1/4 | b1は他記事に新規候補を供給(hormuz `stood at center stage`/smallbag `having a big moment`等)。採用効果・誤採用は未測定 |
| 追加費用 | なし | 推論量・費用+10〜12% | 抽出1呼出 約JPY0.19(0.14〜0.30)+選定入力が少し増える |
| リスク | | Std推論量が大 | 粒度不良が約3割(accepted 32件中10件)、創作比喩・断片の供給増、毎回揺れ、陰性対照偽陽性、OPEN-310 Rule7とgate干渉 |
- Production化に必要な前提(いずれも未承認・未実装): (1) OPEN-325(b1)のユーザー判断 (2) 「本文全文をLLMへ送らない」原則(`CURRENT_SPEC.md` L1847付近)の改訂要否(O3)=b1採用は改訂が必要 (3) OPEN-310 Rule7(所有格・助動詞始まり除外gate)の整理 (4) model routing契約への抽出段登録 (5) 抽出の揺れを抑える設計(複数回合意等、費用増) (6) Family X 12記事回帰。

### 7-C. Round 1〜3を通じた総括
1. **供給側が主レバー**: 選定Prompt単独の変更はP0を超えず(Round 1)。機械供給M2(+(a)(b2)(c))でCoffee score 47.0→71.3、pump 2/6→6/6、time lag 0/3→3/3。
2. **Prompt変更の効果**: P5はP3より契約遵守を保ちつつpumpを回復(9/10)。M2P0に対し合算4.1点差(実質同等圏)で、低優先枠は減るが推論量・費用は+10〜12%、Std推論は約1.8倍。
3. **b1の価値と制約**: 値は「辞書にも(b2)にも拾えない比喩表現」の供給(hormuz/smallbag/semiで観察)に限られ、Coffeeの狙いアンカーには寄与しない。制約は(a)出力の揺れが大きい (b)粒度不良が約3割 (c)創作比喩・断片の供給が増える (d)陰性対照の偽陽性(R3) (e)原則改訂が必要。**Go条件不成立のため、b1を含む選定の効果(採用率・誤採用・gate)は未測定**。

## 8. 他記事(meta/hormuz)
Stage 1中止のためM2+b1のconcierge/gate/b1由来の採用・誤採用は未測定。b1が供給した候補は7-Aの表のとおり(meta: `small twist`誤/`on the other end`粒度不良/`in stock`誤が主、hormuz: `stood at center stage`/`curtain rose`/`gave back some gains`/`refuses to stay down`が正)。meta/hormuzの既存M2P0/M2P5結果はRound 2報告のまま(M2P5 concierge 1/4、hormuz Redundancy NG 1/4)。

## 9. 費用・時間・モデル
- 実績: **JPY3.4596**(18 call、平均0.192/call、最大0.299)。Round 3上限60・ハードストップ65に対し5.8%。本Trial累計 99.00+3.46 = **102.46/300**。見積(事前登録): 4.5(設計書L176基準0.25/call)、Phase D実測基準約2.1。実績は範囲内。Stage 1見積45.4は未使用。
- 時間: Stage 0 約1分(14:40:14〜14:41:09開始、6並列)、call平均22.6秒、reasoning token計36,185(入力28,590/出力38,716)。
- モデル: gpt-6-luna(全call応答model_id一致、Production同一=比較可能性の例外、最新世代最上位系での検証は未実施)。価格はpricing_snapshot.json(USD/JPY=160)。
- Production state 8ファイル: `state_guard_r3.json` unchanged_after_stage0=true。Melos用STOP_NOTICE(run_e2e_01限定)は存在したがKP用STOP/STOP_ALL/KP用STOP_NOTICEは不在(`prep_stage0_r3.json`の`stop_scan`)。再起動0、外部停止0、rc=0。

## 10. 事前登録からの変更
- 変更なし(コードはStage 0実行後に変更していない。ただし事後観察`er064_kp_int_03_posthoc.py`を別ファイルで追加し、Go判定には使っていない)。
- 解釈の記録: 委任文の「評価10記事xStd/Adv=20呼出」は評価記事が10キー(Std/Adv別本文)なので10呼出と解釈(二重計上)。陰性対照4記事x1呼出(Phase D記事)を「該当記事があれば」に基づき追加(JPY約0.45)。「予約3枠」はb1候補枠(Tier H後)と定義。
- Stage 1(38 job)と`reuse_check`の本実行は中止。再利用資産の有効性のみ¥0で確認(`reuse_check_r3.json`: M2P0/M2P5の12セルとも現行構築とsha一致)。

## 11. commit・raw URL
commit message「FAMILY-X-KP-INTEGRATED-OPTIMIZATION-TRIAL-01 委任_03: Round3 (b1)Trial+対照揃え(job数、JPY、採用判断なし)」(job数=Stage 0の18呼出のみ、Stage 1は0 job、JPY3.46)。commit hashは最終報告に記載。主なraw URL:
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er064_output/kp_integrated_opt_01/round3/ROUND3_REPORT_01.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er064_output/kp_integrated_opt_01/round3/plan_r3.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er064_output/kp_integrated_opt_01/round3/stage0_analysis_r3.json
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er064_output/kp_integrated_opt_01/round3/report_tables_r3.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er064_output/kp_integrated_opt_01/round3/posthoc_r3.json
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er064_kp_int_03_b1.py
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er064_kp_int_03_run.py
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/delegation_log/2026-10-13_FAMILY-X-KP-INTEGRATED-OPTIMIZATION-TRIAL-01_03.md

## 12. 注意
- **n小標本・暫定ラベル**: 目視ラベルはsonnet-workerの暫定判断(Fable/ユーザーが覆してよい)。Coffee抽出はn=3で揺れが大きい。
- Go条件は「事前登録した1回目(run1)」固定。run2では出ているため、**運用設計次第(複数回抽出・縮約規則の改善)でGoになり得る**が、それは新しい仕様候補(報告のみ・実装なし)。
- 新仕様候補(実装せず報告): (i)LLM span先頭の有限助動詞除去+末尾を切らない縮約(案D) (ii)抽出の複数回実行と合意(費用増) (iii)断片を決定論で落とす規則(閉クラス始まりの2〜3語)。いずれもユーザー判断事項。
- Round 1/2のtest(tiktoken未導入の環境でtoken数testのみERROR、本Round追加分18件はPASS)。tiktoken依存の2件は環境起因で、今回の変更とは無関係。
- 証跡: `er064_output/kp_integrated_opt_01/round3/`(plan_r3.md, prep_stage0_r3.json, stage0_summary_r3.json, stage0_stdout_r3.txt, stage0_analysis_r3.json, b1/*/run*.json[LLM生出力・usage含む], tierh_deletions_r3.json, report_tables_r3.md, posthoc_r3.json, reuse_check_r3.json, cost_r3.json, state_guard_r3.json, test_results_r3.txt)。

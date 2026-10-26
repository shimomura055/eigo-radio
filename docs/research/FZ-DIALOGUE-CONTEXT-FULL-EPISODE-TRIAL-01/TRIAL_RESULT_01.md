# TRIAL_RESULT_01 — 全編通しTrial 結果要約(FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01 委任_04、2026-10-26 JST)

詳細は `EVAL_01.md`(C1〜C7・N1〜N6・費用・開示)、費用は `BUDGET_LOG_01.md`。機械指標の出典は `er118_output/fz_full_episode_trial_01/analysis_all.json` ほか。

## 1. 何をしたか
猿の手・走れメロスの Standard / Advanced の**セリフ53 clip**を、前後文脈・場面・話者感情をStyleに足すctx方式で新規生成し、地の文などは現行音声のまま、Productionと同一の`run_assembly`で通し版を組み立てた(DEV隔離、Production上書き0)。現行版(同経路で再組立したコピー)と並べた試聴ページを公開済み。

試聴ページ: https://shimomura055.github.io/eigo-radio/user_test/fz_full_episode_trial_01/index.html (作品別: `monkeys_paw.html` / `melos.html`、開発者向け `dev_details.html`)。**4単位すべて掲載**。

## 2. Status候補(機械判定。ユーザー試聴前のため確定ではない)
| 単位 | Status候補 | NG | 備考 |
|---|---|---|---|
| 猿の手 Std | PHASE1B_DONE_USER_LISTENING_PENDING | 0 | |
| 猿の手 Adv | PHASE1B_DONE_USER_LISTENING_PENDING | 0 | M-5(3)改訂による記録付き成立(−0.030 dB) |
| メロス Std | **REJECTED候補(比較条件不成立)** | 1 | C5(ii)不成立: Trial全体−0.158 dB(原因clip part3_c4のpeak、Prod安全弁非作動 vs Trial作動)。方式の品質欠陥ではない |
| メロス Adv | PHASE1B_DONE_USER_LISTENING_PENDING | 0 | |
VALIDATEDとは言わない。最終判断=ユーザー通し試聴(特に同一人物の演技の一貫性・地の文→セリフの切替・不自然な速度変化/長ポーズ)。

## 3. 数値の要点
- 実Trial支出 **25.581円/100円**(TTS 24.158 + ASR 1.423)。感情LLM(Phase 0)は別途1.011円。
- 53 clip / 56 TTS call = **k_ctx 1.057**、初回OK 51/53(96.2%)、NG 1(メロスStd part3_c10→Production原音で置換)、Trialレベル再生成0。
- 生成時間 合計516秒(clipあたり約9.7秒、単位あたり105〜150秒)。
- 量産想定Δ/set **+1.8〜+3.3円**(70円比2.6〜4.7%)。感情情報レビュー自動化費用は未計上。70円/setは、現行単価に同額の余裕がなければ維持できない。
- 機械指標の外れ値(要試聴): N2 3 clip、N3 +3 dB超境界 20/98、N1 mrs_white(猿の手Adv)。

## 4. 開示
観測後改訂1件(M-5(3))、解析実装上の補正1件(C4を採用clipで評価、Status不変)、交絡5項目(scalar差2件・NG1件のProduction原音差替・Std会話ctx初回・メロスpart1_c4前run再利用・通し秒ずれ)は `EVAL_01.md` §5。

## 5. 学習事項
ctx方式のdialogue clipは同一本文でもサンプル間ピークがProductionより高くなり得る(Opusの前提「会話peak≦0.95<0.98」は猿の手Adv 0.9834・メロスStd 0.998で崩れた)。量産化を検討する場合は、headroom/peak正規化の扱いを設計項目にする(新仕様判断=ユーザー)。

## 6. 到達点
Phase 1b完了(Status候補付き)・ユーザー試聴待ち。Production採用ではない。Fable評価欄は`EVAL_01.md` §8(空欄)。

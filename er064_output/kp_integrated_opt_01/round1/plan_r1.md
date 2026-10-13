# Round 1 事前登録(実行前に確定。結果を見て変更しない)
管理ID: FAMILY-X-KP-INTEGRATED-OPTIMIZATION-TRIAL-01 委任_01 / 2026-10-13 / モデル: gpt-6-luna(Production同一=比較可能性例外)、retryなし

## M x P スクリーニング結果(20組合せ -> 有料10組合せ、`screening_r1.json`)
- 除外(互換): M3P0 = P0(現行逐語)は`match:`注釈を説明しない。未説明ラベルを渡す条件になるため。
- 除外(冗長): M1P1/M1P2/M1P3/M1P4 = Coffeeでは M2 が M1 の厳密な上位(M2 = M1 + 予約枠。アンカー到達はM2>=M1)。M1はP0でのみ実行し、機械効果の段階(M0->M1->M2)を分離する。
- 未実行(R2候補): M2P1/M2P3/M3P1/M3P2/M3P3/M3P0。Round1の結果次第で決める。
- 実行: Coffee Std/Adv x n=3
  - Stage1(機械のみ/Promptのみ/統合の核): M0P0(基準), M1P0, M2P0 [機械のみ], M0P2 [Promptのみ], M2P2, M3P4 [統合]
  - Stage2(Prompt比較の拡張と注釈分離): M0P1, M0P3, M0P4 [Promptのみ], M2P4 [M3P4との差=`match:`注釈の効果]
  - Stage3(他記事参考): meta/hormuz x Std/Adv x n=2、下記規則で選ぶ最良2組合せ。基準M0P0は前回Phase2のC0(n=3)を参照(Prompt byte一致をshaで確認)。

## Stage3の組合せ選択規則(事前登録)
Coffee全10組合せについて Std/Adv 合算の run平均アンカースコア(`anchors_r1.json`の重み、fullのみ)を主指標とし、次のどれかに該当する組合せは除外してから上位2を選ぶ:
(a) 選定gate PASS率が M0P0 より10pt超低い、(b) 創作比喩のImportant混入率がM0P0より高い、(c) 低優先枠(アンカー9-12)の占有がM0P0より多い。
同点は 低優先枠が少ない > Jaccard安定性が高い > 費用が低い の順。選択結果は `stage3_plan_r1.json` に Stage3 実行前に保存する。

## 費用規則
Stage前に「累計+見積<=95」を確認(runner内で自動)。累計>=95でjob開始を停止(ハードストップ)。見積は`cost_estimate_r1.json`(合計約80.7、保守側)。

## Stage1結果後の変更記録(実行前に記録、Stage2実行前)
- Stage1実績: 36 job、累計JPY32.78(見積38.21より低い)。観察: 機械側(M2)の供給が最大効果、P2は`pumps its fist`を「筆者独自の比喩」と見て選ばないrunがあり、M0ではPromptだけでは供給不足の項目(pump/time lag)に届かない。
- 変更: Stage2を `M0P1, M0P3, M0P4, M2P4`(事前登録4組合せ) から **`M0P1, M0P3, M0P4, M2P1, M2P3, M2P4`(6組合せ)** へ拡張。理由: 供給が揃うM2下でのPrompt差を測るため(M x P の 2x5 要因配置を完成させる。M2P2は実施済み)。見積 36 job x 約1.06 = 38.2(保守)、実績ベースでは約33。Stage3の見積17を加えても累計は95未満(保守見積でも約88)。
- 事前登録の他項目(Stage3の選択規則・費用規則)は不変。
- 追記: Stage2以降、runnerは選定callの生出力(output_text)をjob_result.json内のusage.selection[*].output_textへ保存する(backup_itemを層1の評価に含めるため。gate結果にbackupが露出しないため)。Stage1は未保存。

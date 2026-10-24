# BUDGET_PLAN_OB_04 (委任_24: 次委任=日本語R0生成の見積。承認前・本委任では有料runを起動しない)

作成: 2026-10-24。**本書は見積であり、承認ではない。`er110_output/family_y_opinion_based_03/BUDGET_APPROVED.json`は作成していない**(testで固定)。次委任でFable(日次一元管理・7-7の承認済みScope内)が委任文で承認する。

## 1. 費用の根拠(前回の実測)
- run_03実績: 23.667円(gen 13.637 + map1 0.533 + 未対応再生成 8.731[V2・V3の各1回] + map2 0.258 + 構造タグ 0.088 + final_map 0.42)、所要約209秒。Leakage Gateは累計22円超のためrunnerが`SKIPPED_BUDGET`にし、**後追いで0.109円**(別実行)。run_01は20.197円(再生成7.6円を含む)。
- 判定: R0 1回の実測は**20〜24円**。再生成(UNMAPPED)は各Voiceに最大1回で、Voiceあたり約4〜5円。

## 2. 次委任の見積

| 項目 | 見積(円) | 根拠 |
|---|---|---|
| R0 3 Voice生成(gpt-6.1-sol) | 約13〜14 | run_03 gen 13.637 |
| 出典対応の付番+機械照合(gpt-6-luna) | 約0.5〜1 | map1 0.533 + map2 0.258 + final_map 0.42 |
| 再生成(UNMAPPED)最大 各Voice1回 | 約0〜13 | 実績 8.731(2 Voice)。最悪3 Voiceで約13 |
| 構造タグ(luna) | 約0.1 | 0.088 |
| Leakage Gate(後追い) | 約0.1〜0.2 | 0.109 |
| **1run合計(典型)** | **約20〜24** | 実測の範囲 |
| **1run合計(最悪、再生成3回)** | **約28** | |
| **提案する1run上限(cap_jpy)** | **30** | 最悪+余裕。runnerの歯止め(`BUDGET_STOP_JPY`)に使う |
| 再Trial(run_02)をユーザー§6の自己ループで行う場合 | +30 | 原因究明→対策→再Trialは承認済みScope内。**同じPromptの微修正の反復は無益**(ユーザー§6) |
| Opusレビュー | API費用に含めない(別枠。日次の開発費としては計上するならFableが決める) | |

## 3. 日次1,000円の確認(10-24 JST)
約414(把握分)+ KP補強Trial上限28 + 次委任R0 30 = **約472円**。再Trial1回を足しても約502円。余裕は約500円。超過見込みなし。

## 4. 起動手順(次委任)
1. Fable/Opusが`PERSONAS_05.md`・`THEME_DATA_02.json`・`PROMPT_DIFF_05.md`を確認(`OPUS_REVIEW_REQUEST_06.md`)。
2. 承認ファイルを作る: `er110_output/family_y_opinion_based_03/BUDGET_APPROVED.json` = `{"cap_jpy": 30, "runs": 1, "approved_by": "<Fable委任文の識別>"}`。
3. `stop_scope_check_01.py --managed-id FAMILY-Y-VOICES-DESIGN-01 --run-dir er110_output/family_y_opinion_based_03/redelivery_fee/run_01 --out <json>` が rc=0。
4. `py er110_family_y_opinion_based_03.py run_01 --paid` を**1回だけ**起動(再起動0。引数はrun名と`--paid`のみ)。起動済みrunは再起動できない(`entry_point.json`)。
5. 終了後、Gateが`SKIPPED_BUDGET`ならLeakage Gateを後追い(約0.1円、前回委任_23と同じ手順)。出典対応表(`PROVENANCE_TEMPLATE_01`の書式)を作成し、Fable独立評価・Opusレビューへ。
6. 失敗終了時の最終成果物は`run_status.json`と`article_ja_partial.md`(到達時点の本文。確定稿ではない)。

# FIX01_DISNEY_RERUN_01: Disney+(streaming_price)を完全台帳F01-F07でRisk Flagger再実行(FIX01-A、2026-10-10)

性質: Trial/DEV。Production変更なし。R0は再生成せず、Flagger Prompt/model/effort/判定条件は無変更。モデル優劣は書かない。「Sonnet暫定」は未確定。

## 1. 完全台帳の渡し方(再実行前に決定した方法。本記録ファイルは実行後に清書)
- 原因: `ledger_restore_01._HDR = ^\[[A-Z_]+\]\s+...` が `[AMBIGUOUS - 断定禁止、曖昧さを保持すること] F01:` を不一致とし、F01・F07を読み飛ばしていた。
- 方法: detectors配下は無変更。新規 `r0_fix01_driver.py` が、そのprocess内だけで `ledger_restore_01._HDR` を `^\[(?P<st>[A-Z_]+)(?:\s+-\s+[^\]]*)?\]\s+(?P<id>[^\s:]+):\s*(?P<text>.*)$` に差替え、既存の `parse_ledger_file` をそのまま呼ぶ(以降の文分割・D0・D2は前回driverと同一コード)。`assert fact_ids == F01..F07` で機械確認。
- F01/F07の扱い: 他5件と同じ扱いを選択。既存パーサは全Factについて見出し接頭辞(`[VERIFIED] F02:` 等)を除去し、本文1行目+後続行(scope/conditions/ambiguity_note/notes_for_writer等)をtextとして渡す。F01/F07も同様に接頭辞(`[AMBIGUOUS - 断定禁止、曖昧さを保持すること]`)を除去し、本文+後続行(ambiguity_note, notes_for_writer含む)を台帳原文のまま渡した。理由: 5件と同じ処理にして「欠落以外の差」を作らないため。副作用(注意): AMBIGUOUSの見出しタグ自体はFlaggerに渡らない(他の[VERIFIED]タグも渡らないのと同じ)。ただし F07本文は ambiguity_note「確認できた資料の範囲で会社が示した理由は特定できない」等を含む。
- 機械確認(3セルとも): Flagger受領 `n_facts`=7、fact_ids=[F01,F02,F03,F04,F05,F06,F07]。D2リクエスト(raw log `request.user`)内のfactsも F01〜F07(7件)。
- F07本文(Flaggerに渡した全文): 「今回確認したDisney+の米国価格ページとReuters報道では、Disneyが今回の値上げ理由を明示した記述は確認できない。Reutersは、DisneyがReutersのコメント要請に直ちには回答しなかったと報じた。」+ scope/conditions(「確認対象に含まれない別の顧客通知等で、追加説明が行われた可能性までは否定しない」)/date_or_period/ambiguity_note/notes_for_writer。
- F01本文: 「2026年10月8日までに今回のWeb調査で確認できた主要な米国向け動画ストリーミング価格改定のうち、最も新しい発表としてDisney+の2026年9月23日の改定を選定した。」+ scope/conditions/date_or_period/ambiguity_note/notes_for_writer。

## 2. 比較条件同一性(前回との機械照合、3セル全て一致)
| 項目 | 前回 | 今回 | 一致 |
|---|---|---|---|
| R0記事(`r0/streaming_price/<model>.md`)sha256 | flags/*.json の article_sha256 | 同 | True(3セル) |
| 台帳ファイルsha256 | 同 | 同(11eb38bd...81ce3) | True |
| 文分割(sentences dict) | 19/22/24文 | 同 | True(完全一致) |
| D2 system prompt sha | b8dacc147009a13b | b8dacc147009a13b(raw log request.systemから計算) | True |
| Flaggerモデル/effort | gpt-6.1-sol / medium | gpt-6.1-sol(応答model_id同) / medium(driver定数) | True |
| 変わった点 | n_facts=5 | n_facts=7(F01,F07追加)のみ | 意図どおり |
- 前回との差は台帳Fact数のみ。D2は記事モード(D0+D2、D2rank不使用)、Flagger呼び出し1回/セル、形式再呼び出し0、attempts=1、valid_json=True。
- detectors配下の追跡ファイル差分: git diff --stat 0件。主要5ファイルのsha256は事前登録値と一致(prompts_flagger 730bc55f... / run_flagger 0962b6e4... / flagger_lib 4cb071ff... / d0_directional 972634b4... / ledger_restore 7e465e5b...)。
- driver: r0_fix01_driver.py sha256 `ad61253de77587223b850ee349abcc9efec50a9d39a7828fd538376e7bd24655`(r0_trial_driver_01.py `ab25f13d...` は無変更)。

## 3. 結果: 修正前 / 完全台帳 のFlag数
| モデル(R0) | 修正前Flag数(5 Fact入力) | 完全台帳(7 Fact)でのFlag数(D0rb∪D2) | D2 | D0 |
|---|---|---|---|---|
| gpt-6-luna | 4 | **0** | 0 | 0 |
| gpt-6.1-sol | 1 | **0** | 0 | 0 |
| gpt-6-astra | 0 | **0** | 0 | 0 |

修正後のFlagは全セル0件。よって「修正後の全Flagの confidence/種類/該当文/対応Fact/理由」の提示対象は無い(D2応答は3セルとも `{"flags":[]}`)。

## 4. 修正前Flagとの対応(5件すべて「消えた」。新規0、残った0)
| モデル | 修正前Flag(文/種類/confidence/対応Fact) | 今回 | 消えた理由 |
|---|---|---|---|
| Luna | s16 不在断定 0.86 [F02-F06]「なぜ改定するのかは資料から特定できない」 | 消えた | 下記注 |
| Luna | s17 不在断定 0.90 [F05]「米国価格ページとReuters報道では、Disneyが理由を明示した記述は確認できず」 | 消えた | 同 |
| Luna | s17 その他 0.78 [F05]「Reutersはコメント要請に直ちには回答しなかったと伝えている」 | 消えた | 同 |
| Luna | s18 不在断定 0.86 [F02-F06]「値上げの理由は確認できない一方、…」 | 消えた | 同 |
| Sol | s7 不在断定 0.96 [F05,F06]「公式料金ページとロイターの報道では、会社が値上げの理由を明示した記述は確認できなかった」 | 消えた | 同 |
- 注: 今回のFlagger応答は空配列のみで理由欄が無いため、「Flaggerが何を根拠に消したか」はFlagger出力の事実としては述べられない。台帳のF07本文は、旧Flagが問題視した2点(Disneyが値上げ理由を明示した記述が確認できない/ReutersのコメントにDisneyが直ちには回答しなかった)をそのまま含む。F07追加以外に入力差が無いため、消失はF07が入力に入ったことによる可能性が高い(推測。Flagger理由欄の記載ではない)。
- 確認結果: 「値上げ理由が確認できない」「Reutersへのコメント要請に直ちに回答しなかった」に対するFlagは、完全台帳では全セルで出ていない。
- 注意(未判定): Flaggerが0件を出したことは「記事が正しい」の確定ではない。Luna記事の「資料から特定できない」「確認できず」の表現がF07の範囲(確認した資料の範囲)に収まっているかは人間確認事項(Sonnet暫定: F07の範囲内に見えるが未確定)。

## 5. 費用(実測 = usage x pricing_snapshot.json gpt-6.1-sol 入力$2/出力$10 per 1M、USD/JPY=160)
| セル | in tok | out tok(reasoning) | 費用円 | response_id |
|---|---|---|---|---|
| Luna記事 | 3176 | 122(112) | 1.2115 | resp_0980e473dcd09d42006ac977da4a3c87d0a1e3e3539e1b70cc |
| Sol記事 | 3333 | 8(0) | 1.0794 | resp_083f9a71fc5b5a3e006ac977db525c87d082eb527a5f4405ee |
| Astra記事 | 3386 | 8(0) | 1.0963 | resp_0f7870f73c921292006ac977da911087d08e5fb418169a3583 |
| 合計 | | | **3.39** | |
`cost_ledger_01.jsonl` に phase=fix01 で3行追記。上限¥20内。Trial累計(本Trial) ¥165.97 + ¥3.39 = ¥169.36(別担当FIX01-Bの費用は含まない)。

## 6. 保存物
- `flags_fix01/streaming_price/<model>.json`(全フィールド、facts本文含む) / `results_fix01/` / `logs_fix01/`(raw request/response、flagger_ledger) / `fix01_run_<model>.out` / `r0_fix01_driver.py`
- 旧結果(`flags/`, RESULT_01.md, FLAG_LIST_01.md)は無変更で残す。

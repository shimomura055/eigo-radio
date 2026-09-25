## 管理ID
`TOPIC-DISCOVERY-ANGLE-INTEGRATED-LUNA-TRIAL-01`(初回委任。ユーザー判断2026-09-25: 3-wayは**保留**(中止ではない)、まずLuna単独で方式の品質と実コストを測る。Sol/Terraは実行しない。Jevは引き続きDEFERRED/NON-BLOCKING)。**並行タスクあり**: 別sonnet-workerが`NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01`(er015_*、標準ACTIVE_TASK/RESULT_PACKET)を実行中。本タスクは`docs/pm/ACTIVE_TASK_TD.md`/`RESULT_PACKET_TD.md`、er016_*のみ。SSOT不変。commit時`index.lock`は10秒待ち再試行(最大3回)。他タスクのstaged変更が混在していれば自タスクのパスだけを`git commit <paths>`で対象指定。`ACTIVE_TASK*`/`RESULT_PACKET*`/`.env`はaddしない。**履歴操作(reset/amend/rebase)禁止**(trailer付け忘れ時は追加のcommitで補正せず、RESULT_PACKETに記録するだけでよい)。

## 性質/到達上限/禁止
- Trial。到達上限`VALIDATED`。ユーザー評価前にProduction採用しない。Production変更・SSOT変更禁止。Sol/Terra呼び出し禁止。旧RERANK成果物は不変。
- 方式: 3WAYと同じ「Search+Angle Discovery+追加検索+Topic Package化+選定を1つのResponses API call(web_search付き、内部複数tool call許容)で行う」。検索と選定を分離しない。Candidate Poolを渡さない。
- 費用上限**¥100**(Luna単独、暴走防止。数円単位で止めない)。**実行前概算がLuna 1 callで¥100超ならSTOP**。暴走ガードとしてResponses APIの`max_tool_calls`(内部tool call上限)を**30**に設定(設計変更ではなくガード。記録する)。1 callは途中停止できないため、実測が¥100を超えた場合は事実として報告(追加callはしない)。
- STOP条件(ユーザー指定): ¥100超過見込み/Search条件を再設計しないと実行できない/Teacher Dataが揃わない/追加仕様が必要/Production変更が必要。STOP時`stop_reason.json`、そこまでcommit(`STOP:`接頭)。
- `git add -A`/`stash`禁止。

## 固定ブロック
E-1/D-1/G-1/F-1(前回同一)。T-0: 本委任文を`docs/pm/delegation_log/TOPIC-DISCOVERY-ANGLE-INTEGRATED-LUNA-TRIAL-01.md`へ保存し`check_delegation_prompt.py`実行、結果をRESULT_PACKET_TDへ1行(FAILでも継続)。

## 事前指定Read一覧
- `er016_topic_discovery_angle_integrated_3way_trial_01.py`: Grep `def |argparse|--step|--arm|max_tool_calls|web_search|json_schema|DEVELOPER|USER_TEMPLATE|teacher`→run/verify-window/assemble実装の再利用(**Prompt本文・schema・Teacher差し込みは3WAY委任文と逐語同一**。`docs/pm/delegation_log/TOPIC-DISCOVERY-ANGLE-INTEGRATED-3WAY-TRIAL-01.md`のGrep `共通Prompt`節で照合)。新script `er016_topic_discovery_angle_integrated_luna_trial_01.py`は3WAY scriptをimportし、arm L固定・`max_tool_calls=30`・out-dir変更のみ(3WAY script自体は変更しない)。
- `er016_output/topic_discovery_angle_integrated_3way_trial_01/cost_estimate.json`: Luna 1 callの概算根拠(¥40〜60)。
- `er016_topic_discovery_eval_01.py`: Grep `def |--user-eval|blind_map`→○△×集計を単一arm用に流用(dry-run)。
- `er016_topic_selection_reference_process_trial_01.py`: Grep `def verify|published`→公開日時HTTP実測(3WAY scriptに未実装なら流用)。
- `docs/pm/topic_selection_user_eval_dataset.json`(Teacher 57、逐語差し込み)。

## 実行手順
1. `--step estimate`: Luna単独の概算(内部検索20/25/30回)→`cost_estimate.json`。¥100超見込みならSTOP。
2. `--step run`: `gpt-5.6-luna`、effort medium、tools=[web_search, search_context_size low]、`max_tool_calls=30`、json_schema(3WAYと同一)。`raw_response.json`全保存、`web_search_call`数と各query→`search_log.md`、usage(input/output/reasoning)・latency・JPY→`api_meta.json`(`response.model`実値)。空出力・schema不一致時は同一条件で1回のみ再実行(記録、費用は累計)。
3. `--step verify-window`: 10件のseed_urlをHTTP実測し窓内/外/不明→`window_compliance.json`(除外せずフラグ)。
4. `--step assemble`:
   - **ユーザー評価一覧** `USER_EVAL_TOPIC_DISCOVERY_LUNA.md`(root): 10件、`| # | 仮タイトル | 元ニュース(媒体・日付・URL) | 事実の核 | 一般人との接点 | 疑問 | Angle(1〜2段) | 追加検索した事実(あれば) | 評価(○/△/×) | コメント |`。self_note・内部判断は載せない。番号はランダム順、`eval_map.json`に対応。
   - `dropped_candidates.md`(モデルが落とした候補と理由)、`lane_ratio.md`(News/Social比率、追加検索ありの件数)、`qcd.md`(web_search回数/input・output・reasoning tokens/latency/total cost/1 Topic Packageあたりcost)。
   - 評価script dry-run(単一arm: ○率/○+△率/×率、独自候補Hit率は非該当と明記)。
5. REPORT `TOPIC-DISCOVERY-ANGLE-INTEGRATED-LUNA-TRIAL-01_REPORT.md`: §1 条件(24h窓・lane・Teacher・max_tool_calls=30の記録・3WAY保留の経緯[¥200→¥400変更後も概算超過])/§2 Prompt全文・schema(3WAYと逐語同一、sha256)/§3 `response.model`実値/§4 検索回数・query一覧/§5 最終10件(Topic Package全項目)/§6 落とした候補/§7 News/Social比率・追加検索件数/§8 window compliance/§9 QCD(1 Packageあたりcost含む)/§10 評価一覧のパス・評価方法/§11 Fable参考評価`[Fable記入]`/§12 分類`[Fable記入]`/§13 USER_DECISION_REQUIRED`[Fable記入]`/§14 Open Item候補/§15 Dangling Reference Check(`Grep "TOPIC-DISCOVERY" glob="er003_*.py,er012_*.py"`=0件)・Production変更なし。

## 実行コマンド全文
```
cd C:\Users\tensh\eigo-radio
.venv\Scripts\python.exe er016_topic_discovery_angle_integrated_luna_trial_01.py --out-dir er016_output\topic_discovery_angle_integrated_luna_trial_01 --step estimate --budget-jpy 100
.venv\Scripts\python.exe er016_topic_discovery_angle_integrated_luna_trial_01.py --out-dir er016_output\topic_discovery_angle_integrated_luna_trial_01 --step run --budget-jpy 100 --max-tool-calls 30
.venv\Scripts\python.exe er016_topic_discovery_angle_integrated_luna_trial_01.py --out-dir er016_output\topic_discovery_angle_integrated_luna_trial_01 --step verify-window
.venv\Scripts\python.exe er016_topic_discovery_angle_integrated_luna_trial_01.py --out-dir er016_output\topic_discovery_angle_integrated_luna_trial_01 --step assemble
.venv\Scripts\python.exe er016_topic_discovery_eval_01.py --out-dir er016_output\topic_discovery_angle_integrated_luna_trial_01 --user-eval er016_output\topic_discovery_angle_integrated_luna_trial_01\user_eval_DUMMY.json --dry-run
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\TOPIC-DISCOVERY-ANGLE-INTEGRATED-LUNA-TRIAL-01.md --json-out docs\pm\delegation_log\TOPIC-DISCOVERY-ANGLE-INTEGRATED-LUNA-TRIAL-01.md_check.json
git status --short
```

## SSOT追記文
なし。

## Git
明示add: `er016_topic_discovery_angle_integrated_luna_trial_01.py`、`er016_output/topic_discovery_angle_integrated_luna_trial_01/`配下、`TOPIC-DISCOVERY-ANGLE-INTEGRATED-LUNA-TRIAL-01_REPORT.md`、`USER_EVAL_TOPIC_DISCOVERY_LUNA.md`、`docs/pm/delegation_log/TOPIC-DISCOVERY-ANGLE-INTEGRATED-LUNA-TRIAL-01.md`、同`_check.json`。(`er016_topic_discovery_eval_01.py`を単一arm対応で修正した場合はそれも)
メッセージ: `TOPIC-DISCOVERY-ANGLE-INTEGRATED-LUNA-TRIAL-01: 2026-09-18 JSTの24時間を対象にSearch+Angle Discovery+追加検索+Topic Package化+選定を1 callで行う方式をLuna単独で実行し、10件のTopic Package・評価一覧・QCDを作成(3-wayは保留、Production変更なし)`(STOP時`STOP:`接頭)
trailer: `Management-ID: TOPIC-DISCOVERY-ANGLE-INTEGRATED-LUNA-TRIAL-01`

## 報告(RESULT_PACKET_TD)
0. T-0 1. 概算と¥100判定 2. `response.model`実値/web_search回数/tokens(input・output・reasoning)/latency/JPY/再実行有無、1 Packageあたりcost 3. 10件の仮タイトル+元ニュース媒体(RESULT_PACKETには載せてよい) 4. window compliance 5. News/Social比率・追加検索件数 6. 評価一覧・eval_mapのパス、dry-run 7. STOP該当有無 8. `git status --short`・commit SHA・push 9. 一覧外Read理由、Open Item候補(事実列挙)。

---
【ユーザー指示全文】(delegation_logへ保存)
② TOPIC-DISCOVERY-ANGLE-INTEGRATED-LUNA-TRIAL-01。3-wayは一旦やめます。ユーザー判断: まずLunaだけで実行する。Sol/Terraは今回実行しない。理由は、3-way概算が想定以上に高かったため。目的: 新しいTopic Discovery方式そのものが、記事発見→Angle Discovery→必要なら追加検索→Topic Package化→最終選定をOne goで行ったときに、実際に良い候補を出せるか確認する。まず品質と実コストをLunaで測る。条件: 対象期間は前Trialと同じ固定24時間(2026-09-18 JSTの24時間)/News lane+Social-signal lane/今回までのユーザーFeedbackをTeacher Dataとして使用/検索と選定を分離しない/各記事を見つけた時点で「どう広げると面白くなるか」まで考える/必要なら追加検索可/最終10件のTopic Packageを作る。Topic Package: 元ニュース/事実の核/一般人との接点/「なぜ？」「本当？」「そんなことできる？」等の疑問/1〜2段広げたAngle/必要に応じた追加検索内容/最終Topic案/仮タイトル。重要: 表面的な記事タイトルだけで採否を決めない。火星サンプル→火星有人探査・火星移住→なぜ月には行けるのに火星にはまだ行けないのか、のように記事をスタート地点として考える。逆に、芸能人の小ネタ/スポーツ選手個人の話/災害続報/一般健康ハウツーなどは、そのままでは弱い。一般人が自分事にできる大きなテーマへ自然に広がらないなら落とす。SNSの扱い: SNSは事実Sourceではなく Topic Discovery Sensorとして使う。SNSで話題になっているものを拾った場合、事実確認は信頼できる報道・一次Sourceで行う。コスト: 今回はLunaのみ。暴走防止上限¥100。数円単位では止めない。実行後に必ず、web/search回数/input・output tokens/reasoning tokens(取得可能なら)/latency/total cost/1 Topic Packageあたりcost を報告。今回の狙い: モデル比較ではなく「この方式そのものが良いか」を確認するTrial。Lunaで十分良い候補が出るなら、Sol/Terra比較が本当に必要か後で判断する。Status: 今回最大VALIDATED。ユーザー評価前にProduction採用しない。STOP条件: ¥100超過見込み/Search条件を再設計しないと実行できない/Teacher Dataが揃わない/追加仕様が必要/Production変更が必要。その場合はSTOPして報告。PM上の扱い: Topic Discovery: 3-wayは中止ではなく保留/今回はLuna単独Trial/Sol・Terra比較はLuna実測後にユーザー判断/Jevは引き続きDEFERRED/NON-BLOCKING。両タスク終了後、ユーザー判断事項を明示してSTOP。

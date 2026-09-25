## 管理ID
`TOPIC-DISCOVERY-ANGLE-INTEGRATED-LUNA-TRIAL-01`(修正1回目: REPORT §11〜§13の`[Fable記入]`置換のみ)。**並行タスクあり**: 別sonnet-workerが`NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01`(er015_*、標準ACTIVE_TASK/RESULT_PACKET)を実行中。本タスクは`TOPIC-DISCOVERY-ANGLE-INTEGRATED-LUNA-TRIAL-01_REPORT.md`と自タスクのdelegation_logのみ触る。一時ファイルは`docs/pm/ACTIVE_TASK_TD.md`/`RESULT_PACKET_TD.md`。commit時`index.lock`は10秒待ち再試行(最大3回)。他タスクのstaged変更が混在していれば自タスクのパスだけを`git commit <paths>`で対象指定。`ACTIVE_TASK*`/`RESULT_PACKET*`/`.env`はaddしない。履歴操作禁止。

## 性質/禁止
Trial記録の追記のみ。Production/SSOT変更・API支出・再実行・他セクション変更禁止。`git add -A`/`stash`禁止。

## 事前指定Read
- `C:\Users\tensh\eigo-radio\TOPIC-DISCOVERY-ANGLE-INTEGRATED-LUNA-TRIAL-01_REPORT.md`

## 事前指定Grep
- 対象: `C:\Users\tensh\eigo-radio\TOPIC-DISCOVERY-ANGLE-INTEGRATED-LUNA-TRIAL-01_REPORT.md`
- パターン: `\[Fable記入\]`(3箇所: §11/§12/§13)
- 更新位置: 各見出し直下の`[Fable記入]`をFable記入テキストで置換(前後の他行は変更しない)

## 固定ブロック
E-1/D-1/G-1/F-1(前回同一)。T-0: 本委任文を`docs/pm/delegation_log/TOPIC-DISCOVERY-ANGLE-INTEGRATED-LUNA-TRIAL-01_fix01.md`へ保存し`check_delegation_prompt.py`実行、結果をRESULT_PACKET_TDへ1行(FAILでも継続)。

## 作業
REPORTの §11/§12/§13 の`[Fable記入]`(Grep `\[Fable記入\]`、3箇所)を以下で置換。他は変更しない。

§11:
```
### 11.1 方式(Angle Discovery統合)について
- 各Packageの構造(事実の核→一般人との接点→疑問→1〜2段の広げ方→追加検索した事実)は概ね成立しており、追加検索の事実にはURLが付き創作は見られない。Angleの質は、ユーザーの正例(火星→有人火星、5G→6G生活)に近い「記事をスタート地点にして広げる」形になっている(例: #4 AIロボット→権限設計、#9 10分配送→速さに払う消費者心理、#12 失敗公開→信頼の測り方)。
- 費用は¥4.62(1 Packageあたり¥0.39)で、事前概算(¥40〜59)の約1/10。方式のコストは問題にならない。

### 11.2 探索の幅(本Trialの主要な弱点)
- web_search回数は8回のみ(max_tool_calls=30に対し)。入力80,825 tokens、出力10,588、reasoning 2,107。
- 12件すべてが英語圏のTech系媒体(TechCrunch 8、Tom's Hardware、Axios、Google公式、OpenAI公式)で、日本の国内ニュース・経済・生活・科学など指定News laneの大半が未探索。テーマもAI関連が10/12に偏る。
- Social-signal laneは実質未実施(「SNS反応」枠3件も通常の記事)。
- 対象窓: 12件中1件のみが2026-09-18 JST内。8件は米国時間9/18(JSTでは9/19早朝)。モデルは「その日」を米国日付で解釈した。
- 件数は指示「exactly 10」に対し12件(schemaで固定していない)。同一seedの別Angleが2組(#1/#11 Google CC、#5/#6 Tilly Norwood)あり、実質ユニークseedは10件。
- ユーザーの正例(日銀金利・能登・退職代行・15歳OECD等)が示す国内・生活・社会の幅と比べ、今回の出力は明らかに狭い。これは方式そのものよりも、探索量(8検索)と探索対象の指定不足に起因すると見る。

### 11.3 Fable所見(参考、最終はユーザー評価)
Angle化の品質は期待できるが、「何を探すか」の幅が不足したため、方式の本来の力はまだ測れていない。次回は (a) 探索の最低要件(日本語Sourceを含む/指定laneを各1回以上検索/社会的話題の検索を実施)を明示、(b) JST窓の解釈を明示(公開日時をJSTで判定)、(c) schemaで10件固定、(d) 同一seedの重複を禁止、を入れた上で再実行するのが妥当。費用が¥5前後であれば、Sol(単価約25倍→約¥115見込み)を含む3-wayも¥400内に収まる可能性が高い。
```

§12:
```
**USER_DECISION_REQUIRED**。Angle Discovery統合の方式自体は機能し費用も低いが、探索の幅(国内・Social lane・JST窓・件数固定)がユーザー指定条件を満たしておらず、この出力だけで方式をVALIDATEDとはしない。ユーザーの12件評価と、探索要件を明示した再実行の要否判断が必要。
```

§13:
```
1. 12件の○/△/×評価(`USER_EVAL_TOPIC_DISCOVERY_LUNA.md`)を提出するか、探索の幅が不足しているため評価を省略して再実行へ進むか。
2. 再実行(Luna、概算¥5〜10)を承認するか。変更点: 探索の最低要件(日本語Source・指定laneごとの検索・社会的話題の検索)/JST窓の明示/schemaで10件固定/同一seed重複禁止。Prompt条件が変わるため新Trial IDとする。
3. 実測が安価だったため、再実行時にSol/Terraを同一条件で加える3-way(概算¥150〜250、Terra単価UNKNOWN)を同時に行うか、Luna再実行の結果を見てからにするか。
```

## 実行コマンド全文
- `python C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\TOPIC-DISCOVERY-ANGLE-INTEGRATED-LUNA-TRIAL-01_fix01.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\TOPIC-DISCOVERY-ANGLE-INTEGRATED-LUNA-TRIAL-01_fix01.md_check.json`
- `git add C:\Users\tensh\eigo-radio\TOPIC-DISCOVERY-ANGLE-INTEGRATED-LUNA-TRIAL-01_REPORT.md C:\Users\tensh\eigo-radio\docs\pm\delegation_log\TOPIC-DISCOVERY-ANGLE-INTEGRATED-LUNA-TRIAL-01_fix01.md C:\Users\tensh\eigo-radio\docs\pm\delegation_log\TOPIC-DISCOVERY-ANGLE-INTEGRATED-LUNA-TRIAL-01_fix01.md_check.json`
- `git commit -m "TOPIC-DISCOVERY-ANGLE-INTEGRATED-LUNA-TRIAL-01: REPORT §11-13 Fable参考評価(Angle化は機能・探索の幅不足)・USER_DECISION_REQUIRED記入"`

## SSOT
本タスクはTrial REPORTの`[Fable記入]`置換のみであり、`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`等SSOTへの追記は行わない。

## Git
明示add: `TOPIC-DISCOVERY-ANGLE-INTEGRATED-LUNA-TRIAL-01_REPORT.md`、`docs/pm/delegation_log/TOPIC-DISCOVERY-ANGLE-INTEGRATED-LUNA-TRIAL-01_fix01.md`、同`_check.json`。
メッセージ: `TOPIC-DISCOVERY-ANGLE-INTEGRATED-LUNA-TRIAL-01: REPORT §11-13 Fable参考評価(Angle化は機能・探索の幅不足)・USER_DECISION_REQUIRED記入`
trailer: `Management-ID: TOPIC-DISCOVERY-ANGLE-INTEGRATED-LUNA-TRIAL-01`

## 報告(RESULT_PACKET_TD)
0. T-0 1. 置換箇所と`git diff --stat` 2. commit SHA・push 3. 一覧外Read理由。

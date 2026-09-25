## 管理ID
`NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01`(修正1回目: REPORT §10〜§12の`[Fable記入]`置換のみ)。**並行タスクあり**: 別sonnet-workerが`TOPIC-DISCOVERY-ANGLE-INTEGRATED-3WAY-TRIAL-01`(er016_*、`_TD`一時ファイル)を実行中。本タスクは`NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01_REPORT.md`と自タスクのdelegation_logのみ触る。標準`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`。commit時`index.lock`は10秒待ち再試行(最大3回)。他タスクのstaged変更が混在していれば自タスクのパスだけを`git commit <paths>`で対象指定。`ACTIVE_TASK*`/`RESULT_PACKET*`/`.env`はaddしない。

## 性質/禁止
Trial記録の追記のみ。Production/SSOT変更・API支出・記事再生成・他セクション変更禁止。`git add -A`/`stash`/`amend`禁止。

## 事前指定Read
- `C:\Users\tensh\eigo-radio\NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01_REPORT.md`

## 事前指定Grep
- 対象: `C:\Users\tensh\eigo-radio\NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01_REPORT.md`
- パターン: `\[Fable記入\]`(3箇所: §10/§11/§12)
- 更新位置: 各見出し直下の`[Fable記入]`をFable記入テキストで置換(前後の他行は変更しない)

## 固定ブロック
E-1/D-1/G-1/F-1(前回同一)。T-0: 本委任文を`docs/pm/delegation_log/NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01_fix01.md`へ保存し`check_delegation_prompt.py`実行、結果をRESULT_PACKETへ1行(FAILでも継続)。

## 作業
REPORTの §10/§11/§12 の`[Fable記入]`(Grep `\[Fable記入\]`、3箇所)を以下で置換。他は変更しない。

§10:
```
### 10.1 Fable参考評価(Meta v4本文を通読)
- 自然さ: v4は不自然な一語置換(Sewer v3の installation→putting in 型)を起こしていない。"put on hold"→"paused"、"on a person's behalf"→"for people" など自然な置換のみ。文長9.68語/文・FK 5.06でSewer v3と同水準。
- 比喩・Story: lead role / backstage / understudy / curtain / piano をすべて保持し、v1で弱化した "lead role" も "The lead role belonged to Muse" として維持。Reveal・Endingは同位置。
- Fact: 機械diffの「not ×2脱落」「some脱落」は言い換えによるもので、通読では意味は保持されている("it would not be surprising if they were shocked"→"people might be shocked"、"the important question may not be only"→"it may not be enough to ask"、"some parts of the calls"→"some parts of calls"[定冠詞のみ脱落])。事実誤りなし。
- ニュアンスの軽微な弱化2件: (1) "leak outside the company"→"leave the company"(日本語R2「流出」の含意が薄れる)、(2) "According to internal posts reviewed by Reuters, a Meta executive said…"→"Reuters reviewed internal posts. A Meta executive said…"(発言の出典関係が分割で緩む)。いずれもFact driftではなく表現の弱化。
- "some parts of the calls" の意味はBaselineどおり維持(OPEN-177サブ項目のまま、本Trialでは修正していない)。

### 10.2 頻度帯指標について
Meta Advancedはもともと平易で、帯C/Dの異なり語はAdvanced 6→v4 7(固有名詞ヒューリスティックの誤判定"Reuters"と、"paused"のような自然だが順位上は高帯の語を含む)。この記事では頻度帯指標が方針の効果を示せず、指標側の限界(固有名詞判定・自然な語の順位ノイズ)も判明した。v4の「自然さ優先」が Sewer の不自然置換を実際に解消するかは、Sewerでv4を再生成しないと確認できない(本Trialの範囲外)。
```

§11:
```
**VALIDATED(部分)**。別Topic(Meta)でも v4方針は Story・比喩・自然さを保ちつつ文長簡略化を再現し、不自然な一語置換を起こさなかった。ただし頻度帯別の語彙削減効果はこの記事では実証されず、Sewerでの不自然置換解消も未検証。Production採用ではない。
```

§12:
```
1. 決定的な検証として、Sewer AdvancedからStandard v4を1本生成し(1 call、概算¥0.5)、v3の installation→putting in / collects→gathers / distant→faraway 型が解消するかを確認するか(Fable推奨: 実施。v4の主目的はこの型の抑止であり、Metaでは元々発生していなかった)。
2. ニュアンス弱化(leak→leave、出典関係の分割)を許容するか、v4 Promptに「否定・出典・漏えい等の意味を弱めない」旨の1行を足すか(Fable推奨: 1のSewer結果を見てから判断)。
3. 頻度帯指標の固有名詞判定(文頭位置依存)の改善は測定器側の課題として記録のみ(Open Item候補)。
```

## 実行コマンド全文
- `python C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01_fix01.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01_fix01.md_check.json`
- `git add C:\Users\tensh\eigo-radio\NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01_REPORT.md C:\Users\tensh\eigo-radio\docs\pm\delegation_log\NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01_fix01.md C:\Users\tensh\eigo-radio\docs\pm\delegation_log\NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01_fix01.md_check.json`
- `git commit -m "NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01: REPORT §10-12 Fable参考評価(自然さ・比喩・Story維持、帯指標は未実証)・VALIDATED(部分)・USER_DECISION_REQUIRED記入"`

## SSOT
本タスクはTrial REPORTの`[Fable記入]`置換のみであり、`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`等SSOTへの追記は行わない。

## Git
明示add: `NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01_REPORT.md`、`docs/pm/delegation_log/NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01_fix01.md`、同`_check.json`。
メッセージ: `NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01: REPORT §10-12 Fable参考評価(自然さ・比喩・Story維持、帯指標は未実証)・VALIDATED(部分)・USER_DECISION_REQUIRED記入`
trailer: `Management-ID: NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01`

## 報告(RESULT_PACKET)
0. T-0 1. 置換箇所と`git diff --stat` 2. commit SHA・push 3. 一覧外Read理由。

## 管理ID
`NEWS-JA-TO-EN-ADAPTATION-TRIAL-01`(修正1回目: REPORT §13 Fable記入欄の反映のみ)。**並行タスクあり**: 別sonnet-workerが`TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01`(er016_*、`ACTIVE_TASK_RR`/`RESULT_PACKET_RR`)を実行中。本タスクは標準`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`を使い、er016_*に触らない。commit時`index.lock`は10秒待ち再試行(最大3回)、自タスクのファイルのみ明示add。

## 性質/上限Status/禁止事項
Trial記録の追記のみ。Status `VALIDATED`(Fable分類)。Production変更・SSOT変更・API支出・記事再生成・他セクション変更は禁止。`git add -A`/`stash`/`amend`禁止。

## 固定ブロック
E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Readを基本。G-1: git出力は`--short`/`--stat`で最小化。F-1: transcript退避不要。T-0: 本委任文を`docs/pm/delegation_log/NEWS-JA-TO-EN-ADAPTATION-TRIAL-01_fix01.md`へ保存し`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行、結果をRESULT_PACKETへ1行記録(FAILでも継続)。

## 作業
`NEWS-JA-TO-EN-ADAPTATION-TRIAL-01_REPORT.md` 行219-221(`## §13 Fable記入欄` 直下の `[Fable記入]`)を以下の本文で置換する(Grep `\[Fable記入\]`で位置確認、他箇所は変更しない)。

```
### 13.1 Fableブラインド参考評価(blind.md を先読み→blind_key.json 開封、2026-09-24)

参考順位(僅差): **Z(arm2 Balanced) ≥ Y(arm3 Natural) > X(arm1 Faithful)**。3本とも日本語R2の編集設計(主役Muse/舞台裏の人間/代役/最後に舞台と幕へ戻る結び)を保持しており、差は英語表現の硬さ・省略の有無のみで、B/C2(英語で最初から生成)との差より明らかに小さい。

- X(arm1 Faithful): 「A phone-call stage like this was being built at Meta」「human contract staff」「there is a human backstage」など日本語構文をそのまま移した箇所があり、聴取時にやや硬い。一方、「通話の一部」を "some of the calls" と解釈しており、Reuters報道の事実("some calls were handled by human contract workers")に最も近い。
- Y(arm3 Natural): 最も平易で聴きやすいが、「当面の間」に当たる "for the time being" が落ち、結びの「幕の後ろに何があるかを説明する」が "explain what is happening" に一般化されるなど、小さな省略・簡略化がある。
- Z(arm2 Balanced): 自然な英語で、"for the time being"・"behind the scenes"・"we looked backstage" 等の要素を保持。省略が最少で聴きやすさも十分。

### 13.2 Fact/ニュアンス観察
- 機械チェック(数字追加0・新規固有名詞なし・新規引用発言なし)をFableも確認。B/C2で見られた「日本語記事にない一般論の追加」は3 armとも無し。
- 日本語R2「通話の一部を…担当」は「一部の通話」とも「通話内の一部」とも読める曖昧文。X="some of the calls"、Y/Z="some parts of the calls" と解釈が分かれた。Adaptation方式では日本語側の曖昧さがそのまま英語へ伝播するため、英語化時にVerified Fact Ledgerと照合する工程が量産時に必要(Open Item候補、提案ではなく事実列挙)。

### 13.3 分類
**VALIDATED**(Trial上限)。仮説「完成した日本語R2をAdaptすれば、英語で最初から書くより編集設計を保ちやすく一般論の追加も起きにくい」は記事1本・3 armの範囲で支持された。Production採用ではない。

### 13.4 USER_DECISION_REQUIRED
なし(ブロッキング判断なし)。ユーザーへの提示事項: (1) X/Y/Zの品質判断(Fable参考順位はZ≥Y>X)、(2) 再現Trial(下水道・旅行の日本語R2を同じBalanced指示でAdapt、¥5以内)の要否、(3) 英語版の量産ルートを「Adaptation(日本語R2→英語)」と「英語直接生成(C2)」のどちらを本命候補にするか。

### 13.5 未解決
- 記事1本のみで再現性未検証。
- Adaptation時のLedger照合工程は未設計(13.2)。
- 英語Adaptation後にProduction contract(2つの`### `節・`## In one line`)を付与する工程は本Trialの範囲外で未検証。
```

## Git
明示add: `NEWS-JA-TO-EN-ADAPTATION-TRIAL-01_REPORT.md`、`docs/pm/delegation_log/NEWS-JA-TO-EN-ADAPTATION-TRIAL-01_fix01.md`、同`_check.json`。
メッセージ: `NEWS-JA-TO-EN-ADAPTATION-TRIAL-01: REPORT §13 Fableブラインド参考評価・分類VALIDATED・未解決事項を記入`
trailer: `Management-ID: NEWS-JA-TO-EN-ADAPTATION-TRIAL-01`
push後、`git status --short`とcommit SHAをRESULT_PACKETへ。

## 報告(RESULT_PACKET)
0. T-0結果 1. 置換した行範囲と差分の要約 2. 他箇所無変更の確認(`git diff --stat`) 3. commit SHA・push結果 4. 一覧外Read/Grepの理由。

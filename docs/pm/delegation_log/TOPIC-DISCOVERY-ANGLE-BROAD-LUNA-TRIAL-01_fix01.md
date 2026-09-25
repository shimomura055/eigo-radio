## 管理ID
`TOPIC-DISCOVERY-ANGLE-BROAD-LUNA-TRIAL-01`(修正1回目: REPORT §11〜§13の`[Fable記入]`置換のみ)。**並行タスクあり**: 別sonnet-workerが`NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-PRODUCTION-WIRING-01`(er003_*、SSOT、標準ACTIVE_TASK/RESULT_PACKET)を実行中。本タスクは`TOPIC-DISCOVERY-ANGLE-BROAD-LUNA-TRIAL-01_REPORT.md`と自タスクのdelegation_logのみ触る。一時ファイル`docs/pm/ACTIVE_TASK_TD.md`/`RESULT_PACKET_TD.md`。**API呼び出し禁止(いかなる理由でも実callしない)**。commit時`index.lock`は10秒待ち再試行(最大3回)。他タスクのstaged変更が混在していれば自タスクのパスだけを`git commit <paths>`で対象指定。`ACTIVE_TASK*`/`RESULT_PACKET*`/`.env`はaddしない。履歴操作禁止。trailer必須。

## 固定ブロック
E-1/D-1/G-1/F-1(前回同一)。T-0: 本委任文を`docs/pm/delegation_log/TOPIC-DISCOVERY-ANGLE-BROAD-LUNA-TRIAL-01_fix01.md`へ保存し`check_delegation_prompt.py`実行、結果をRESULT_PACKET_TDへ1行(FAILでも継続)。

## 作業
REPORT §11/§12/§13 の`[Fable記入]`(Grep `\[Fable記入\]`、3箇所)を以下で置換。他は変更しない。

§11:
```
### 11.1 前回(LUNA-TRIAL-01)からの改善(採用attempt_1)
- 10件固定(schema)・同一seed重複なし・JST窓: HTTP実測で窓内8/10、確認不能2、窓外0(前回は窓内1/12)。8系統のうち7系統を探索(queries 28件、web_search 10回)。日本語Source 1件、Social入口1件(#10 ローソン弁当: X上の反応を入口にローソン公式で事実確認=意図した「SNSはセンサー」の型)。#9(米財務長官→日本の金利→住宅ローン・輸入品)はBig Newsを自分事にする型で、ユーザー正例(日銀金利)に近い。
- 費用: 採用call ¥5.13(1 Packageあたり¥0.51)、累計¥11.34(3 call)。

### 11.2 残る弱点
- 系統8(エンタメ・スポーツ)は正当な2回の実行とも未探索(STOP条件該当)。
- AI関連が8/10(その日のニュースサイクルの偏りもあるが、系統1〜7を「AI×○○」で埋めた形)。
- **Source品質**: seed URLの6/10が `news.chathome.org`(他媒体記事のミラー/アグリゲータ)で、一次URL(OpenAI/Guardian/AWS/Verge/Google公式)ではない。#10は まとめサイト(tweetsoku)がseed。OPEN-174(Source品質Gate)の対象となる問題で、Promptに「一次・元媒体のURLを使う」要件が無かったことが原因。
- 探索の「幅」は前回より改善したが、ユーザー正例の国内・社会・科学の幅にはまだ届かない。

### 11.3 プロセス逸脱(開示)
機械チェック修正の動作確認中に、scriptの安全装置不備(`--force`が再実行防止を無効化)により**未許可の3回目API call**が発生し、正当な2回目callの生データが上書き消失した。3回目の結果はチェックPASSだったが正当性を欠くため不採用。原因は修正済み(`retried=true`記録後は`--force`でもAPIを呼ばない)。費用は上限内(¥11.34/¥100)。Sonnetが自己申告し、REPORT §5.2に全文開示している。
```

§12:
```
**USER_DECISION_REQUIRED(STOP相当)**。改善(10件固定・重複なし・JST窓・7系統・Social入口の型)は確認できたが、系統8未探索(STOP条件)・Source品質(ミラーURL 6/10)・AI偏重が残り、方式をVALIDATEDとはしない。採用10件はAngle化の質の評価対象としては使用可能。
```

§13:
```
1. 採用10件(attempt_1)を○/△/×評価の対象として使うか(Fable推奨: 使う。Angle化の質と「Big Newsを自分事に」「SNSをセンサーに」の型が実際に出ているかを確認できる。系統8未探索・ミラーURLは既知の弱点として扱う)。
2. 次回改定(新ID)の要件: (a) seed URLは一次・元媒体に限定(アグリゲータ/ミラー/まとめサイト禁止、OPEN-174と整合)、(b) 系統8は「探索したが該当なし」の明示申告を許容(無理な採用はさせない)、(c) 同一テーマ(AI)の上限(例: 最終10件中4件まで)を置くか(比較条件を変えるためユーザー判断)。
3. プロセス逸脱の扱い: 記録のみ(修正済み)とするか、Trial scriptの安全装置(再実行防止)の横展開をOpen Itemとして起票するか。
```

## Git
明示add: `TOPIC-DISCOVERY-ANGLE-BROAD-LUNA-TRIAL-01_REPORT.md`、`docs/pm/delegation_log/TOPIC-DISCOVERY-ANGLE-BROAD-LUNA-TRIAL-01_fix01.md`、同`_check.json`。
メッセージ: `TOPIC-DISCOVERY-ANGLE-BROAD-LUNA-TRIAL-01: REPORT §11-13 Fable参考評価(窓・件数・重複は改善、系統8未探索・ミラーURL・AI偏重が残る)・USER_DECISION_REQUIRED・プロセス逸脱の開示記入`
trailer: `Management-ID: TOPIC-DISCOVERY-ANGLE-BROAD-LUNA-TRIAL-01`

## 報告(RESULT_PACKET_TD)
0. T-0 1. 置換箇所と`git diff --stat` 2. commit SHA・push 3. 一覧外Read理由。

## 管理ID
`NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01`(修正3回目=最終: REPORT §14.8〜§14.10の`[Fable記入]`置換のみ)。**並行タスクあり**: 別sonnet-workerが`TOPIC-DISCOVERY-ANGLE-INTEGRATED-LUNA-TRIAL-01_REPORT.md`と`_TD`一時ファイルを編集中。本タスクは`NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01_REPORT.md`と自タスクのdelegation_logのみ触る。標準`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`。commit時`index.lock`は10秒待ち再試行(最大3回)。他タスクのstaged変更が混在していれば自タスクのパスだけを`git commit <paths>`で対象指定。`ACTIVE_TASK*`/`RESULT_PACKET*`/`.env`はaddしない。履歴操作禁止。

## 性質/禁止
Trial記録の追記のみ。Production/SSOT変更・API支出・再生成・他セクション変更禁止。`git add -A`/`stash`禁止。

## 固定ブロック
E-1/D-1/G-1/F-1(前回同一)。T-0: 本委任文を`docs/pm/delegation_log/NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01_fix03.md`へ保存し`check_delegation_prompt.py`実行、結果をRESULT_PACKETへ1行(FAILでも継続)。

## 事前指定Read一覧
- `NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01_REPORT.md`(§14.8〜§14.10周辺のみ)。

## 事前指定Grep一覧+追記位置・更新位置の手順
- `Grep \[Fable記入\] NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01_REPORT.md` で3箇所を特定し、§14.8/§14.9/§14.10の各`[Fable記入]`を指定テキストへ置換する(他行は変更しない)。

## 実行コマンド全文
```
python C:/Users/tensh/eigo-radio/docs/pm/tools/check_delegation_prompt.py C:/Users/tensh/eigo-radio/docs/pm/delegation_log/NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01_fix03.md
```

## SSOT追記文
なし(本タスクはSSOT非該当。REPORT本文のみ更新)。

## 作業
REPORT §14.8/§14.9/§14.10 の`[Fable記入]`(Grep `\[Fable記入\]`、3箇所)を以下で置換。他は変更しない。

§14.8:
```
Fable最終評価(Sewer v4本文を通読、Sonnetの語彙遷移表を確認):
- 主目的「難語→別の難語の置換抑止」は**達成されなかった**。collects→gathers、distant→faraway はv3と同一のまま再現。さらに invisible→hidden(v3、良好)が v4では unseen(rank 12,884、Advancedの invisible より低頻度)へ後退し、「明確に易しく自然な場合のみ置換」の自己点検指示が効いていない直接の反例となった。convenience・getting rid of もv3の改善からAdvanced水準へ後退。
- 改善点は限定的: installation→"put in, checked, and cleaned" は文法が揃い、v3の "putting in, checks, and cleaning" より自然。municipalities は "towns or cities"/"local governments" と平易化されたが訳語が不統一で、"cities" は原文にない軽微な拡張。
- 体裁: 段落8→14、1行1文の改行が多く "Turn on the tap. Flush the toilet." など短文の羅列に近づいた(v4 Promptが禁じる flat list 方向)。音声化では改行は影響しないが、文の流れは v3 より断片的。
- Story・比喩・Reveal: 維持。洗濯機の比喩は「〜とは違う」で論理を保ち、main artery も直喩のまま。Endingは "familiar place" と "surprisingly close" の2文に分割され、重心がやや移動(意味は保持)。
- Fact drift: 実質なし。
- 結論: Meta v4 の良好さは Meta Advanced がもともと平易だったことによるもので、難語の多い Sewer では v4 の頻度帯+自然さ指示は v3 に対して優位を示せず、一部後退した。Prompt文言だけでは語彙制御の再現性が低い(v2→v3→v4を通じた一貫した観察)。
```

§14.9:
```
**REJECTED(v4語彙設計)**。Story・自然さは維持されたが、v4の目的(頻度帯ごとの扱い分け/不自然置換の抑止/難語→難語置換の抑止)がSewerで再現せず、v3からの後退(invisible→unseen、convenience復帰)も生じた。現時点のStandard A2 Promptの最良候補は v3(VALIDATED)のまま。Production採用はしない。
```

§14.10:
```
1. Standard A2 の語彙制御について、次のどれを採るか:
   (a) v3 を当面の Standard Prompt 候補として固定し、語彙のPrompt反復をここで止める(Fable推奨。v2→v4で「Prompt文言だけでは語彙制御の再現性が低い」ことが確認できたため)。
   (b) v5: v3 に「置換の反例(例: collects→gathers、distant→faraway は易しくなっていない)」を数例だけ明示した最小変更で1回だけ再試行(¥1)。
   (c) 生成後に wordfreq の帯判定で難語をフラグし、1回だけ狙い撃ちの修正callを行う軽量な2段構成(これまで禁止していた工程追加に当たるため、方針転換の承認が必要)。
2. 頻度帯の測定基準(effectiveness Trial=top2,000圏外、banding Trial=帯A≤3,000)の統一方針(記録のみ、Open Item候補)。
```

## Git
明示add: `NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01_REPORT.md`、`docs/pm/delegation_log/NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01_fix03.md`、同`_check.json`。
メッセージ: `NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01: REPORT §14.8-14.10 Fable最終評価(Sewer v4で難語→難語置換が再現、v3から一部後退)・v4語彙設計REJECTED・USER_DECISION_REQUIRED記入`
trailer: `Management-ID: NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01`

## 報告(RESULT_PACKET項目)
0. T-0 1. 置換箇所と`git diff --stat` 2. commit SHA・push 3. 一覧外Read理由。

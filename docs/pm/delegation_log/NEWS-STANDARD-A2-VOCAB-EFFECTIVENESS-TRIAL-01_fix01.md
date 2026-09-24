## 管理ID
`NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01`(修正1回目: REPORT §11〜§13の`[Fable記入]`置換のみ)。**並行タスクあり**: 別sonnet-workerが`TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01`(er016_*、OPEN_ITEMS.md、同REPORT、`_RR`一時ファイル)を実行中。本タスクは`NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01_REPORT.md`と自タスクのdelegation_logのみ触る。標準`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`使用。commit時`index.lock`は10秒待ち再試行(最大3回)。他タスクのstaged変更が混在していれば自タスクのパスだけを`git commit <paths>`で対象指定。`ACTIVE_TASK*`/`RESULT_PACKET*`/`.env`はaddしない。

## 性質/禁止
Trial記録の追記のみ。Production/SSOT変更・API支出・記事再生成・他セクション変更禁止。`git add -A`/`stash`/`amend`禁止。

## 固定ブロック
E-1/D-1/G-1/F-1(前回同一)。T-0: 本委任文を`docs/pm/delegation_log/NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01_fix01.md`へ保存し`check_delegation_prompt.py`実行、結果をRESULT_PACKETへ1行(FAILでも継続)。

## 事前指定Read
- `C:\Users\tensh\eigo-radio\NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01_REPORT.md`(§11〜§14周辺、編集前に該当箇所の前後文脈確認)

## 事前指定Grep
- `\[Fable記入\]` を対象ファイル内で検索し、§11/§12/§13の該当3箇所の行位置を確認した上で、各箇所を以下本文へ置換する。他セクションは変更しない。

## 作業
REPORTの §11/§12/§13 の`[Fable記入]`(Grep `\[Fable記入\]`で位置確認、3箇所)を以下で置換。他は変更しない。

§11:
```
### 11.1 「2,000語優先」指示の実効性(Fable確認)
Sonnetの実測(wordfreq上位2,000語・lemma化)をFableも確認: 圏外異なり語はAdvanced 36→v1 33→v2 36で、v2の数値目標型の指示は語彙面でほぼ無効だった(文長・文法の簡略化は起きたが語彙は変わらなかった)。v3(判断基準+仕上げ前の自己点検)で36→28(-22%)。ユーザー指摘の代表例 municipalities は消え towns に置換、facilities/installation/inspections/convenience も平易化。平均語/文はv2 9.51→v3 9.74、FK 5.41→5.07で、文長面の効果は維持。

### 11.2 記事品質(Fable参考評価、下水道v3)
- Story構造・順序・Reveal(「合併」の勘違い→家庭排水)・結び(surprisingly familiar place)は維持。
- 中心比喩は v2より改善: v2で事実文化していた洗濯機の比喩が、v3では "It is like putting a small washing machine in each home. The other choice is one huge washing machine for the whole town." と比喩の論理(「代わりに」)を取り戻した。"main artery" も直喩(like)のまま。
- 難語→難語の交換が3件(distant→faraway、collects→gathers、divide→split)。頻度リスト上は同等かむしろ圏外で、真の簡略化ではない。
- やや不自然な句が2箇所: "It still needs putting in, checks, and cleaning."(installation/inspectionsの無理な平易化)、"The system stretches a long way and is connected."。音声で聞くと引っかかる可能性。
- 意味の軽微な狭まり: 「一部の自治体」→ "Some towns"(municipalitiesは市も含む。事実誤りではないが範囲がやや狭い)。
- artery / septic tank / wastewater / underground は残存。artery は日本語R2の中心比喩「見えない大動脈」そのものであり、Fableは原則A(見立てとして必要)に該当すると見る(最終判断はユーザー)。
```

§12:
```
**VALIDATED**(Trial上限)。本Trialの問い「v2の語彙指示は効いているか」「Prompt単体で語彙制御を強められるか」の両方に実測で答えが出た(v2は無効、v3で-22%かつStory維持)。ただし v3 Promptは下水道1記事のみの結果であり、Production採用ではない。難語→難語交換と不自然句の残存は次の改善点。
```

§13:
```
1. artery(見立て語)・septic tank・wastewater を「必要な難語(原則A)」として残す方針でよいか(Fable推奨: 残す。arteryは中心比喩そのもの)。
2. Meta記事への適用: 未実行の Meta Standard v2 を飛ばし、v3 Promptで Meta Standard を1本生成して2記事横断で判定するか(Fable推奨: v3で実行、概算¥1〜2)。
3. v3 Promptの次の改善(難語→難語交換の抑止: 置換語は元の語より平易・高頻度であること、および不自然な名詞の動詞化を避ける旨)を、Meta実行の前に入れるか後に入れるか(Fable推奨: 後。まずv3のままMetaで再現性を見る)。
```

## 実行コマンド全文
- `python C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01_fix01.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01_fix01.md_check.json`
- `git add C:\Users\tensh\eigo-radio\NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01_REPORT.md C:\Users\tensh\eigo-radio\docs\pm\delegation_log\NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01_fix01.md C:\Users\tensh\eigo-radio\docs\pm\delegation_log\NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01_fix01.md_check.json`
- `git commit --file <heredoc>`(メッセージ本文はSSOT節参照)

## SSOT
本タスクはREPORT本体（Trial記録ファイル）への追記のみであり、`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`等の正式SSOTへの追記は行わない(§13はUSER_DECISION_REQUIREDとしてREPORT内に記録するのみ)。

## Git
明示add: `NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01_REPORT.md`、`docs/pm/delegation_log/NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01_fix01.md`、同`_check.json`。
メッセージ: `NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01: REPORT §11-13 Fable参考評価(v2語彙指示は無効・v3で-22%・Story維持)・VALIDATED・USER_DECISION_REQUIRED記入`
trailer: `Management-ID: NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01`

## 報告(RESULT_PACKET)
0. T-0 1. 置換箇所と`git diff --stat`(対象1ファイルのみ) 2. commit SHA・push 3. 一覧外Read理由。

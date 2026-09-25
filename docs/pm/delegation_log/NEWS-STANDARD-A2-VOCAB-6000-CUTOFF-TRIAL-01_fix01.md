## 管理ID
`NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01`(修正1回目: REPORT §12〜§14の`[Fable記入]`置換のみ)。**並行タスクあり**: 別sonnet-workerが`TOPIC-DISCOVERY-ANGLE-BROAD-LUNA-TRIAL-01`(er016_*、`_TD`一時ファイル)を実行中。本タスクは`NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01_REPORT.md`と自タスクのdelegation_logのみ触る。標準`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`。commit時`index.lock`は10秒待ち再試行(最大3回)。他タスクのstaged変更が混在していれば自タスクのパスだけを`git commit <paths>`で対象指定。`ACTIVE_TASK*`/`RESULT_PACKET*`/`.env`はaddしない。履歴操作禁止。trailer `Management-ID:` を忘れない。

## 性質/禁止
Trial記録の追記のみ。Production/SSOT変更・API支出・再生成・他セクション変更禁止。`git add -A`/`stash`禁止。

## 固定ブロック
E-1/D-1/G-1/F-1(前回同一)。T-0: 本委任文を`docs/pm/delegation_log/NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01_fix01.md`へ保存し`check_delegation_prompt.py`実行、結果をRESULT_PACKETへ1行(FAILでも継続)。

## 事前指定Read一覧
- `C:\Users\tensh\eigo-radio\NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01_REPORT.md`

## 事前指定Grep一覧+追記位置・更新位置の手順
- `grep -n '\[Fable記入\]' NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01_REPORT.md` で§12/§13/§14の3箇所を特定し、各`[Fable記入]`を以下の作業節の本文で置換する。

## 作業
REPORT §12/§13/§14 の`[Fable記入]`(Grep `\[Fable記入\]`、3箇所)を以下で置換。他は変更しない。

§12:
```
### 12.1 Fable参考評価(Sewer v5・Meta v5を通読)
- 語彙: 6,000語ラインは意図どおり「必要語は残し、不要な難語だけ落とす」方向に働いた。Sewerでは municipalities が消え(towns / local governments)、installation・checks・convenient は自然なまま残存。残る6,000超語は surprisingly / convenience / flush / sewer / artery / wastewater / invisible で、いずれも主題語・比喩語・自然な一般語であり置換不要と見る。Metaの6,000超は leak / curtain / backstage / Reuters のみで全て必要語。
- 不自然な置換・難語→難語置換: v3/v4で問題だった installation→putting in、collects→gathers、invisible→unseen/hidden は発生せず、Advancedの語がそのまま残った。唯一の逸脱は distant(6,000以内)→faraway(表外)が2箇所中1箇所で残ったこと(もう1箇所は distant のまま)。文書内の訳語不統一(towns / local governments)は残る。
- 文長: Sewer 9.91語/文・FK 5.43、Meta 9.66語/文・FK 5.25 で、v3/v4と同水準の簡略化を維持。段落数はAdvancedと同じ8(v4の断片化が解消)。
- Story・比喩・Reveal・Ending: 両記事とも維持(main artery / washing machine / lead role / backstage / understudy / curtain / piano)。
- Fact・意味: 数字・固有名詞・引用句の欠落なし。Metaで "some parts of the calls"(Baseline)が "parts of some calls" に変わり、曖昧文の読みが「一部の通話の一部」へ寄った(Baselineの意味保持という条件からはズレ。OPEN-177の曖昧性と関連)。Meta末尾 "can it make a call? That may not be the only important question." の分割はやや不自然。
- 総評: v5は v3(語彙改善はあるが不自然置換あり)と v4(帯設計、後退あり)の問題を、より短いルールで回避しており、2記事横断で再現した。
```

§13:
```
**VALIDATED**(Trial上限)。「6,000語ライン+自然さ維持」の簡素ルールは、不要な難語(municipalities)を落としつつ必要語(installation / artery / wastewater / 比喩語)を壊さず、不自然置換・難語→難語置換を2記事で起こさなかった。残課題は distant→faraway 1件と Meta "parts of some calls" の意味の寄り。Production採用ではない。
```

§14:
```
1. Standard A2 Promptの現時点の最良候補を v3 から **v5(6000-cutoff)** に更新してよいか(Fable推奨: 更新。Trial上の候補であり、Production採用ではない)。
2. Meta v5 の "parts of some calls": Baselineの "some parts of the calls" を保持する方針(OPEN-177の一次情報確認まで)に照らし、(a) 許容 (b) v5 Promptに「範囲語の位置を変えない」旨を足す (c) Baseline側の曖昧性解消(一次情報確認)を先に行う、のどれか(Fable推奨: (c)。Prompt側で個別対応するより、Baselineの曖昧性を解くのが根本)。
3. Advanced(Natural)+Standard(v5候補)の2段階をProduction配線(OPEN-177)へ進める設計着手の可否(着手時期はユーザー判断)。
```

## SSOT
SSOT(CURRENT_SPEC.md/DECISION_LOG.md/OPEN_ITEMS.md)への追記なし。REPORT本文のみ更新。

## 実行コマンド全文
```
grep -n '\[Fable記入\]' "C:\Users\tensh\eigo-radio\NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01_REPORT.md"
python "C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py" --file "C:\Users\tensh\eigo-radio\docs\pm\delegation_log\NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01_fix01.md" --json-out "C:\Users\tensh\eigo-radio\docs\pm\delegation_log\NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01_fix01_check.json" --pretty
git add "NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01_REPORT.md" "docs/pm/delegation_log/NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01_fix01.md" "docs/pm/delegation_log/NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01_fix01_check.json"
git commit -m "NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01: REPORT §12-14 Fable参考評価(必要語保持・不自然置換なし・2記事再現)・VALIDATED・USER_DECISION_REQUIRED記入" --trailer "Management-ID: NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01"
git push origin main
```

## Git(明示add対象・コミットメッセージ・trailer)
明示add: `NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01_REPORT.md`、`docs/pm/delegation_log/NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01_fix01.md`、同`_check.json`。
メッセージ: `NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01: REPORT §12-14 Fable参考評価(必要語保持・不自然置換なし・2記事再現)・VALIDATED・USER_DECISION_REQUIRED記入`
trailer: `Management-ID: NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01`

## 報告(RESULT_PACKET項目)
0. T-0 1. 置換箇所と`git diff --stat` 2. commit SHA・push 3. 一覧外Read理由。

# News記事 逐次Revision方式(Original→R1→R2)Production採用 Evidence

## 目的

管理ID`NEWS-ITERATIVE-R2-PRODUCTION-WIRING-01`にてユーザーが正式採用した
News記事Entertainment生成方式(Original generation→Entertainment
revision→Further entertainment revision、2回目revisionの結果を最終記事と
して使用)について、「なぜこの方式(Trial内呼称R2)を選んだのか」を将来
にわたって完全に追跡できるようにするための正式Evidenceである。

- ユーザー正式判断日: 2026-09-24
- 管理ID: `NEWS-ITERATIVE-R2-PRODUCTION-WIRING-01`
- Status: `APPROVED_FOR_PRODUCTION / WIRING INCOMPLETE`
  (`PRODUCTION_WIRED`はGate 3全項目充足後にユーザーへ報告して確定する)
- 関連Trial管理ID: `NEWS-ITERATIVE-ENTERTAINMENT-TRIAL-01`、
  `NEWS-ITERATIVE-ENTERTAINMENT-TRIAL-02`、
  `NEWS-R25-PRODUCTION-METHOD-TRIAL-01`(参考)

## 構成

| ファイル | 内容 |
|---|---|
| `README.md` | 本ファイル |
| `prompts.md` | 使用Prompt逐語(developer message、Original Prompt3通り、R1/R2/R3修正指示、model/effort、連鎖方式) |
| `articles/` | 12記事全文(下水道/AI電話代行/旅行荷物 × Original/R1/R2/R3) |
| `comparison_and_decision.md` | 3テーマ横断比較・latency/cost/model_id・Fact維持確認・ユーザー判断・Fable評価 |
| `prompt_echo_and_ad_observation.md` | Open Item B(Prompt復唱)・Open Item A(広告記述)の12記事機械集計結果 |

## 元Trial artifactへのpath(一次データ、本Evidenceはここから逐語転記・sha256一致コピー)

- `er015_news_iterative_entertainment_trial_01.py` / `er015_news_iterative_entertainment_trial_02.py`(Trial実行script、Production非該当、変更なし)
- `er015_news_original_baseline_repro_01.py`(Original Prompt本体・developer message・model/effort定数の定義元)
- `er015_output/news_iterative_entertainment_trial_01/`(下水道テーマ、素材なし)
- `er015_output/news_iterative_entertainment_trial_02/`(AI電話代行/旅行荷物テーマ、実在元記事に基づく素材2〜3文あり)
- `NEWS-ITERATIVE-ENTERTAINMENT-TRIAL-01_REPORT.md`
- `NEWS-ITERATIVE-ENTERTAINMENT-TRIAL-02_REPORT.md`
- DECISION_LOGエントリ: `NEWS-ITERATIVE-R2-PRODUCTION-WIRING-01`(本Evidence保存と同時に追記)

## 12記事 sha256一致確認

`articles/`配下の12ファイルは、元Trial artifact(`er015_output/news_iterative_entertainment_trial_01/*.md`、
`er015_output/news_iterative_entertainment_trial_02/{A,B}_*.md`)からのバイト単位コピーであり、
sha256ハッシュが完全一致することを`.venv/Scripts/python.exe`のhashlib実行で確認済み(2026-09-24、Sonnet実施)。

| 元ファイル | Evidenceファイル | sha256(先頭16桁一致確認) |
|---|---|---|
| news_iterative_entertainment_trial_01/original.md | articles/sewer_original.md | e54ff7feb7acc507... 一致 |
| news_iterative_entertainment_trial_01/revision1.md | articles/sewer_revision1.md | 6d0d03ec30b578ba... 一致 |
| news_iterative_entertainment_trial_01/revision2.md | articles/sewer_revision2.md | a7fa4fd7dcd02b55... 一致 |
| news_iterative_entertainment_trial_01/revision3.md | articles/sewer_revision3.md | fbb5dc9357ff8d6c... 一致 |
| news_iterative_entertainment_trial_02/A_original.md | articles/ai_phone_original.md | 2f018292f43bdbf5... 一致 |
| news_iterative_entertainment_trial_02/A_revision1.md | articles/ai_phone_revision1.md | 5bcc53244e7d5bfc... 一致 |
| news_iterative_entertainment_trial_02/A_revision2.md | articles/ai_phone_revision2.md | 474c2a1669b6f90f... 一致 |
| news_iterative_entertainment_trial_02/A_revision3.md | articles/ai_phone_revision3.md | a9e88a78a68c2efa... 一致 |
| news_iterative_entertainment_trial_02/B_original.md | articles/travel_bag_original.md | 206cc7f05dbad8e7... 一致 |
| news_iterative_entertainment_trial_02/B_revision1.md | articles/travel_bag_revision1.md | c2452f7a4a71e1bd... 一致 |
| news_iterative_entertainment_trial_02/B_revision2.md | articles/travel_bag_revision2.md | cbd8619b53d1734d... 一致 |
| news_iterative_entertainment_trial_02/B_revision3.md | articles/travel_bag_revision3.md | 1b6d0785bea089ea... 一致 |

## Trial呼称とProduction用語の対応(注記)

本Evidence内および元Trial artifactでは、段階名を`Original`/`R1`(Revision 1)/
`R2`(Revision 2)/`R3`(Revision 3)という**Trial内部の作業呼称**で記録している。
Production仕様(`CURRENT_SPEC.md`)上は、これを以下のように定義する。

1. Original generation(= Trial呼称`Original`)
2. Entertainment revision(= Trial呼称`R1`、1回目の「もっとエンターテインメント性を高めて」指示)
3. Further entertainment revision(= Trial呼称`R2`、2回目の同種指示)
4. 2回目revision(上記3)の結果を最終記事として使用する

3回目revision(Trial呼称`R3`)はProduction標準に含めない(Trial実施の
事実としてのみ本Evidenceに保存する)。

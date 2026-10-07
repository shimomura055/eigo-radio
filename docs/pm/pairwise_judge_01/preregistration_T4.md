# 事前登録 T4: 1文x1factの狭い対判定の精度(OPEN-233-PAIRWISE-JUDGE-MODEL-TRIAL-01 委任_01)

登録時刻: 2026-10-08 01:30(dev判定APIの本実行前。単価・1call費用確認の2call probe[非対象文、各モデル2回]のみ実施済み)。Trial/DEV。Production変更なし、`APPROVED_FOR_PRODUCTION`なし、Writer/Checker/runner未編集、git無し。上限¥30、¥27でSTOP。held-outは手順4まで開かない(項目構築はdev後)。

## 1. 対象
- 既知NG: T3 oracle_dev(`er052_output/open233_link_precision_01/oracle_dev.py`)のlocated 29のうちfact_id既知の21件(oracle文=EN unit[複数unitは連結]、oracle fact=known_relation_ng.jsonlのfact_id、台帳fact block全文を提示)。
- 対照: 同記事内で、既知NG/oracle located unitではなく、T3 r3がSUPPORTEDかつsupport_fact_ids(正規化)非空のjudged unit(5語以上)。型(否定/全称/因果/数値/その他=plain)を揃え(同一記事内に同型が無い場合はplain等へフォールバック)、seed=20261008で1件ずつ非復元抽出、NG1件につき1件=21件。対照のfactはr3の先頭support fact。注意: 対照は「r3がSUPPORTEDにした文」であり、NG疑いが全く無い文とは限らない(oracle目視でNG未判定、人間確認なし)。
- 項目構築は`build_items.py`(決定論)。

## 2. 判定形式・条件
- 入力=1文+1 fact entry(台帳block全文、notes含む)。記事全文は渡さない。出力=`verdict ∈ {contradicts, asserts_unstated, consistent, unclear}`+根拠1行(strict JSON schema)。prompt=`judge.py`のDEV_MSG(固定、dev実行中は変更しない)。reasoning effort=medium(両条件)。
- (A) 現行判定モデル`gpt-6-luna`(runner MODEL、Stage1/Stage2の判定モデル)x狭い対判定。(B) 別モデル`gpt-6-sol`(DECISION_LOG 2026-09-29の「Luna不足時の上位候補」。単価$2.00/0.20/10.00、Lunaの20倍)x同じ狭い対判定。(参考)現行Stage1 r3の保存済み判定(model_verdict: SUPPORTED=consistent扱い、それ以外=検出扱い。Stage2の保存判定は対文unit単位でないため本集計に含めない)。
- 費用実測: probeで luna 約¥0.013-0.02/call、sol 約¥0.26-0.30/call。42項目x3回のSolは約¥36で上限を超えるため、**反復を非対称にする**: A=dev 42項目x3回。B=dev 42項目x1回+安定性サブセット8項目(`stability_subset_B.json`: jb9k-n3+NG3+対照4、seed固定)に追加2回(計3回)。
- 指標の定義(件数): 検出=verdict≠consistent(unclearも検出扱い、別掲)。主判定は**rep1**(A/B同条件・同回数)。A反復はrep1/rep2/rep3の多数決(2/3以上が非consistent)を参考値に併記。3/3一致=3回の4値verdictが全て同一(併記: 検出/非検出フラグが3回同一)。Aは42項目全体、Bは8項目サブセットで算出。
- 指標: 既知NG検出率(21件中)、対照誤検出率(21件中)、3/3一致率、重大2件(jb9k-n3[devに存在]、89wf[held-outに存在、手順4で確認])の検出、型別検出率、asserts_unstatedの出方。

## 3. 合格ライン(件数、dev、各条件ごとに主判定=rep1で適用)
- 検出 >= 15/21 かつ 対照誤検出 <= 4/21 かつ 3/3一致率 >= 80%(Aは42項目、Bは8項目サブセットで >=7/8)。費用<=¥30。
- 条件ごとに全てを満たせばPASS。1つでも欠ければFAIL。読み替えない。CONDITIONAL無し。
- 解釈の交絡(事前に明記): A対Bの差=モデル差、A対現行r3の差=判定形式差(文脈つき広い判定→1文1fact)。重大1件(dev)の検出は合否外の記述。

## 4. held-out(手順4)
dev確定後、T3 oracle_heldout(既知NG fact_id既知14件)+対照14件を同じ方法で構築し、各条件1回(rep1)のみ。方向一致(dev比、検出率・誤検出率の方向)のみ確認、合格ライン再適用なし。Bの費用が¥27STOPに達する場合はAのみ実施しBは未実施と記録。

## 5. 並行・実行
`tasklist`で別python常駐プロセスあり(並行タスク)。自分の同時プロセス<=2(A,Bを別プロセス)。出力`er052_output/open233_pairwise_judge_01/out/`、費用`out/cost_log.jsonl`(全call)。

## 6. 追記(2026-10-08 、dev実行・集計後、held-out実行前)
- dev実費: ¥24.87(A=¥1.9、B=¥22.3[1call約¥0.33]、probe¥0.6)。B(Sol)のheld-out 28件(約¥9)は¥27STOPを超えるため、4節の規定(Bの費用が¥27STOPに達する場合はAのみ)を適用。ただし重大2件のうちheld-out側(space_weapons-89wf-n1、major)の検出確認だけは目的に含まれるため、**Bはheld-outで89wf-n1・89wf-n2の2件のみ**(約¥0.7、`heldout_B_ids.json`)に限定して実行する。Bのheld-out検出率・誤検出率は算出しない(未実施と記録)。Aのheld-outは28件全件(rep1)。
- dev結果(合否は3節機械適用、T4_RESULT.mdに記載)を見た後の変更だが、合否線・指標定義は不変。

# 委任_13 結果 FACTLOCK-ASTRA-E2E-TRIAL-01(2026-10-09) Status=G2_COMPLETE(全9テーマ x 2腕 到達、集計・ユーザーパック作成済み。判定線評価はFable未)。runner欠陥なし(新規0)。Production変更なし、VALIDATED/APPROVED_FOR_PRODUCTION未宣言

## 1. 成果物・commit・raw URL
- 集計: `er052_output/factlock_astra_e2e_trial_01/runs/final_aggregate/{AGGREGATE.md,aggregate_final.json}`(全9/旧4/新5の3層、到達表、テーマ別(ii)、B3/AMBIGUOUS候補、費用、段別)
- ユーザーパック: `runs/USER_PACK_E2E_01.md`(JA対)、`runs/USER_PACK_E2E_EN_01.md`(EN Adv/Std対)
- ログ: `runs/g2_round2_logs/`(worker3-7のstdout/stderr、driver、watcher、`aborted_wrong_python/`)
- 新script: `er052_factlock_astra_e2e_final_aggregate_01.py`、`er052_factlock_astra_e2e_user_pack_01.py`、`er052_factlock_astra_e2e_aggregate_01.py`(only_themes引数と小数丸めのみ追加)。runner本体は不変(テスト33件は委任_12で確認、今回未再実行)。
- 記録: `_13.md`、`_13_check.json`、本書、RESULT_PACKET、REPORT_LEDGER、DECISION_LOG末尾1節、ACTIVE_TASK固定ヘッダ。commit hash・raw URLは末尾。

## 2. 到達状態(JA / shadow / Advanced EN->Checker / Standard EN->Checker)
| テーマ | 腕 | JA | shadow | Adv EN / Checker | Std EN / Checker |
|---|---|---|---|---|---|
| meta | new | done | done | done / DOWNGRADE | done / DOWNGRADE |
| meta | old | **JA STOP**(R2 FC MAJOR1) | - | - | - |
| hormuz | new | done(B1) | done | done / DOWNGRADE | done / DOWNGRADE |
| hormuz | old | **JA STOP**(original) | - | - | - |
| space_weapons | new | done(B1) | done | done / REWRITE_THEN_DOWNGRADE | **EN STOP** / - |
| space_weapons | old | done | done | done / DOWNGRADE | done / DOWNGRADE |
| small_bag | new | done | done | done / DOWNGRADE | done / DOWNGRADE |
| small_bag | old | done(案B) | done | **EN STOP** / DOWNGRADE(残存記事) | - |
| byd_recall | new | done | done | done / REWRITE_THEN_DOWNGRADE | **EN STOP**(translation) / - |
| byd_recall | old | done | done | **EN STOP** / DOWNGRADE(残存記事) | - |
| central_bank_mortgage | new | **JA STOP**(R0、30年固定の範囲拡張) | - | - | - |
| central_bank_mortgage | old | done | done | done / DOWNGRADE | done / DOWNGRADE |
| openai_copyright | new | done(B1=Trial3回目) | - | **EN STOP**(B1後も ja_source MAJOR、1記事1回上限) / - | - |
| openai_copyright | old | done | done | done / DOWNGRADE | done / REWRITE_THEN_DOWNGRADE |
| semiconductor_earnings | new | done | - | **EN STOP**(B1 trial上限3/3で拒否、STOP記録) / - | - |
| semiconductor_earnings | old | done(R2 FC MAJOR3) | done | done / DOWNGRADE | done / REWRITE_THEN_DOWNGRADE |
| streaming_price | new | done | done | done / DOWNGRADE | done / DOWNGRADE |
| streaming_price | old | done | done | done / DOWNGRADE | done / REWRITE_THEN_DOWNGRADE |
- Human Review 0。Checker run 完了 22/36(新10、旧12)。provenance違反0、(m)違反0、全体STOP 0。
- 注: 旧腕でEN Advancedが STOP でも `b1b/article.md` が残る場合、runnerの設計でChecker advが実行される(small_bag old、byd old)。分母上はEN STOPとして計上、Checker結果は参考。
- **runner欠陥: 新規なし**。再開回数: round1再開1回(worker3/4)。環境事故1件(下記)。
- 環境事故: 1回目起動でbash既定のpython(openai未導入)を使い、全stageが0.4秒でModuleNotFoundErrorにより失敗(API呼出0、確定費用0)。失敗stateは理由付きresetで解除し、`.venv/Scripts/python.exe` で起動し直した(欠陥扱いのrunner修正はなし)。失敗ログは `g2_round2_logs/aborted_wrong_python/`。

## 3. 費用・時間・累計
- 台帳(G1+round1+本委任): raw 459.04円 / guard 625.89円(cap1000内、raw800未達)。本委任の増分 raw 約212.82円。
- Astra段(new_r1+new_r2): raw 336.71 / guard 503.56(r1 173.19、r2 163.52)。B1再支出(推定): raw 102.99 / guard 148.42(hormuz 33.52、space_weapons 36.24、openai 33.23)。
- 腕別 raw: 新 395.12 / 旧 63.92。段別(raw): new_check_adv 20.04、new_check_std 11.05、old_check_adv 15.61、old_check_std 18.52、new_en_adv 6.40、new_en_std 5.43、new_ii 4.81、new_r0 7.84、new_shadow 2.83、old_ja 12.08、old_adv 9.63、old_std 1.98、old_ii 3.46、old_shadow 2.65。
- テーマ別 raw: byd 39.08、cbm 7.89、hormuz 75.03、meta 42.95、openai 67.02、semiconductor 43.91、small_bag 49.29、space_weapons 85.78、streaming 48.07(詳細はAGGREGATE.md 7節、テーマ/腕別も)。
- **Trial累計(Stage R 178.99込み)= raw 約638.03円**。請求ダッシュボード照合は未実施(Astraのx1.5はguard額)。Checker 1 run 20円超は watcher 検知0。
- 時間: 再起動 10:34:31 から最終stage 11:14:40(約40分、最大5プロセス)。空き物理メモリ 約4.0-4.3GB(下限4GB未満が10分継続した事象なし)。

## 4. 集計表の要点(数値のみ。判定なし。分母=予定run、各腕 全9=18 / 旧4=8 / 新5=10)
| 指標 | 全9 新 | 全9 旧 | 旧4 新 | 旧4 旧 | 新5 新 | 新5 旧 |
|---|---|---|---|---|---|---|
| JA STOP(記事) | 1 | 2 | 0 | 2 | 1 | 0 |
| EN STOP(Adv/Std) | 2/2 | 2/0 | 0/1 | 1/0 | 2/1 | 1/0 |
| 影(shadow) STOP | 0 | 0 | 0 | 0 | 0 | 0 |
| 人手介入必要(件/率) | 6 / 0.333 | 6 / 0.333 | 1 / 0.125 | 5 / 0.625 | 5 / 0.5 | 1 / 0.1 |
| Rewrite run(率) | 2 (0.111) | 3 (0.167) | 1 (0.125) | 0 | 1 (0.1) | 3 (0.3) |
| Human Review | 0 | 0 | 0 | 0 | 0 | 0 |
| 初回JA_RECHECK(記事) | 4 | 3 | 2 | 1 | 2 | 2 |
| JA R2 FC MAJOR | 0 | 4 | 0 | 1 | 0 | 3 |
| (ii)新規具体主張(最終JA) | 2 | 15 | 1 | 5 | 1 | 10 |
| B1回復(発動/拒否) | 3 / 2 | 0 | 2 / 0 | - | 1 / 2 | - |
| M1発火(Std) | 2 | 0 | 1 | 0 | 1 | 0 |
| M3保護claim / 旧腕の影対照(changed_actor) | 6 / 0 | 0 / 5 | 1 / 0 | 0 / 0 | 5 / 0 | 0 / 5 |
| JA字数(本文のあるrunの平均、手計算) | 931(8本) | 740(7本) | - | - | - | - |
- 重大/軽微(Checker最終): 新10 run・旧12 run とも最終状態は DOWNGRADE 系のみ(RESOLVED_STAGE2_DOWNGRADE または REWRITE_THEN_DOWNGRADE)、STAGE4_ESCALATION 0。真に重大/軽微のラベルは未付与(要Fable/盲検ラベル)。
- 初回JA_RECHECK率: 新 4/9、旧 3/9。人手介入率は定義案(DESIGN 1-3)どおり。
- B3由来/台帳AMBIGUOUS由来(**機械的候補**、確定ではない、AGGREGATE.md 6節): AMBIGUOUS候補 新2(streaming adv)/旧0、B3候補 新4/旧4(hormuz新、semiconductor旧)。EN/JA言語差のため本文突合は未実施。
- 層別(旧4/新5)は上表と AGGREGATE.md 3・4節。

## 5. 観察(各テーマ一言)
- meta: 新は完走、旧はJA FC STOP(R2でMAJOR1)。
- hormuz: 新は B1 1回で完走、旧は original でJA STOP。
- space_weapons: 新Advは Rewrite 経由で解決、新StdはB1後も EN STOP(M1発火)。旧は完走だが(ii)2。
- small_bag: 新は完走((ii)1)、旧は案B後に EN Adv STOP((ii)3、字数665)。
- byd_recall: 新Advは Rewrite 経由、新Stdは translation 起源で STOP(M1発火)。旧は EN Adv STOP((ii)4)。
- central_bank_mortgage: 新は R0 で JA STOP(「30年固定」の範囲拡張)、旧は完走((ii)0)。
- openai_copyright: 新は B1(Trial3回目)後も ja_source MAJOR で EN Adv STOP、旧は完走(Std Rewrite)。
- semiconductor_earnings: 新はJA完了後 EN Adv ja_source MAJOR(F6、unsupported_new_claim)で B1 trial上限(3/3)により拒否->STOP。旧は R2 FC MAJOR3 でも完走、(ii)4。
- streaming_price: 新は完走(AMBIGUOUS候補2)、旧も完走(Std Rewrite、(ii)1、字数629)。
- 全体: 新腕のJA側 STOP は 1/9(旧 2/9)、新腕の主な離脱は EN 段の ja_source MAJOR(B1後含む)。新の(ii)合計 2 に対し旧 15、JA字数は新が長い(本文のあるrunの平均 931 vs 740)。Astra段が総raw の約73%。

## 6. 未確認・Fable判断要
1. **B1上限の順序依存**: Trial全体3回の枠を hormuz/space_weapons/openai が消費したため、semiconductor(新Adv)は上限拒否で STOP になった。上限が無ければ回復し得たかは未検証(反実仮想は未実行、cherry-picking禁止のため再実行していない)。
2. openai_copyright 新は B1 実施後の再MAJOR で STOP(1記事1回上限、Production等価性規定どおり)。
3. 旧腕でEN STOP後にもChecker advが走る設計の扱い(集計は分母=EN STOP、Checker run完了数にも残る)。判定時の取扱いはFable判断。
4. B3由来/AMBIGUOUS由来は機械的候補。真の突合・ラベル(重大/軽微)は未実施。
5. 請求ダッシュボード照合未実施。shadow失敗リトライ重複支出の有無、Astra x1.5 の実勢は未確認。
6. ユーザー提示パックのEN STOP新腕(openai/semiconductor Adv、space_weapons/byd Std)は採用本文が無く(被検本文はdeviation check promptにのみ残る)、パック上は「採用本文なし」と注記。
7. Production変更なし、判定線評価は未実施。VALIDATED/APPROVED_FOR_PRODUCTION未宣言。

## commit・raw URL
commit: 8607777455551defb83bc44c91781df552db9b3b
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/factlock_astra_e2e_trial_01/runs/final_aggregate/AGGREGATE.md
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/factlock_astra_e2e_trial_01/runs/USER_PACK_E2E_01.md
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/factlock_astra_e2e_trial_01/runs/USER_PACK_E2E_EN_01.md
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/delegation_log/2026-10-09_FACTLOCK-ASTRA-E2E-TRIAL-01_13_result.md
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_factlock_astra_e2e_final_aggregate_01.py
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_factlock_astra_e2e_user_pack_01.py

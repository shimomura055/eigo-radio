# ROUND1_MIDCHECK (FACTLOCK-ASTRA-E2E-TRIAL-01 委任_12, 2026-10-09) Status=ROUND1_PARTIAL(runner欠陥1件で全worker停止、再開待ち)

出典: runs/<theme>/{new,old}/state.jsonl, checker/*.json, telemetry/*, ledger_costs_worker1..4.jsonl, round1_aggregate/AGGREGATE.md。判定線の評価はしない(最終集計でFable)。

## 1. 到達状態(4テーマ x 2腕 x 2レベル)
| テーマ | 腕 | JA | Advanced(EN) | Checker adv | Standard(EN) | Checker std | 備考 |
|---|---|---|---|---|---|---|---|
| meta | new | R2 FC major 0 | done | RESOLVED_STAGE2_DOWNGRADE(¥1.91) | done | RESOLVED_STAGE2_DOWNGRADE(¥2.31) | B1回復0。G1分+本round分 |
| meta | old | JA FC STOP(rc46, G1確定) | - | - | - | - | 再実行せず(state尊重を確認) |
| hormuz | new | R2 FC major 0 | 初回 ja_source MAJOR(HF-006)=JA_RECHECK -> B1回復1回 -> 再実行で done | RESOLVED_STAGE2_DOWNGRADE(¥2.51) | done | RESOLVED_STAGE2_DOWNGRADE(¥2.94) | B1発火1(Trial全体1件目) |
| hormuz | old | JA FC STOP(rc46, Original FC MAJOR残存) | - | - | - | - | |
| space_weapons | new | R2 FC major 0 | done(初回compliant) | RESOLVED_REWRITE_THEN_DOWNGRADE(¥5.35、Rewrite 1run) | **EN Standard STOP**(初回 ja_source MAJOR F-001 -> B1回復 -> 再実行後も MAJOR 残存でSTOP) | 未到達(分母に残る) | B1発火1(Trial全体2件目) |
| space_weapons | old | JA done | done(old_adv、**旧腕Advanced経路 実証1**) | **未実行**(全停止で中断) | 未実行 | 未実行 | old_std以降は再開待ち |
| small_bag | new | R2 FC major 0 | done | RESOLVED_STAGE2_DOWNGRADE(¥2.14) | done | RESOLVED_STAGE2_DOWNGRADE(¥3.31) | B1回復0 |
| small_bag | old | JA done | 案B(JA_RECHECK 1回、Advancedは再生成後 LEDGER_COMPLIANT で生成) | RESOLVED_STAGE2_DOWNGRADE(¥2.36)(**旧腕Advanced -> Checker 実証2**) | **EN Standard STOP**(案B後も ja_source MAJOR 2件=MB-05、er019 rc42) | 未到達 | old_shadowはrunner欠陥でfailed(後述) |
Human Review: 0件。Checker `provenance_violations` / `waste_flags` は全実行 空。

## 2. runner欠陥の有無(1件、本roundで検出)
- **欠陥**: `worker_shadow` が `a2/article.md` を無条件に読んでいた。EN Standard STOP(a2/audit はあるが a2/article.md 無し)の腕で FileNotFoundError(space_weapons/new の new_shadow、small_bag/old の old_shadow)。3回リトライ後 `stage_failed`。例外発生前のshadow内API分は台帳計上済み(space_weapons/new ¥1.43、small_bag/old ¥0.65、重複支出の疑いはstate上リトライ3回分に含まれる可能性、未確認)。
- 検出時の対応(Fable指示どおり): `STOP.json` を置き全worker停止(進行中stageは完走、次stage開始で停止)。worker3 が検出して停止(STOP.json は worker3 の記録に上書きされた)。worker1/2/4 は完走。
- 最小修正済み: `a2/article.md` が存在するときだけ Standard attempt1 分類を行う(1行)。テスト追加(ShadowNoStandardArticleTest 1件)PASS。**再開は未実施**(runner例外=停止条件のためFable判断待ち)。
- 前処理の修正2件(G1軽微欠陥): theme_summary.json は別invocationの腕を残してmerge、run_summary は `run_summary_worker{wid}_{arms}.json` に腕別化、m3_protected.jsonl は新腕Checker後に0件でも空ファイルを出力(保護>0なら1行/levelのcandidate_filter要約)。テスト +1(split_arm)。
- meta旧腕のSTOP尊重: 再実行されず(state stage_stop 尊重、新規API 0)を確認。
- その他の既知欠陥の再発: 費用台帳 open reserve が複数worker並走時に一時的に出る(完了後 0)、G1で出たID_RE問題の再発なし。

## 3. 旧腕Advanced経路の実証(round1で初)
- 実証1: space_weapons/old。JA合格 -> old_ii -> old_adv(JA再利用分岐、`既存JA記事(R2)を再利用`) done、Advanced deviation LEDGER_COMPLIANT、費用 ¥0.63。Checker adv は欠陥による全停止で未実行。
- 実証2: small_bag/old。JA合格 -> old_adv で Advanced 初回は ja_source MAJOR 1件で案B(JA再生成1回) -> Advanced LEDGER_COMPLIANT -> **old_check_adv 完走(RESOLVED_STAGE2_DOWNGRADE、¥2.36)**。Standardは案B後も MB-05 ja_source MAJOR 2件で STOP(rc42)。
- 結論: 旧腕 JA -> Advanced(再利用分岐)-> Checker の経路は実API実証済み(runner経路不通なし)。

## 4. B1回復の発火と残回数
- 発火2件(hormuz=Advanced段 ja_source MAJOR、space_weapons=Standard段 ja_source MAJOR)。Trial全体上限3 -> **残1**。1記事1回の枠は両方使用済み(space_weapons は回復後もSTOP=EN STOPとして記録)。
- 新腕のEN段 ja_source MAJOR は R2 FC が major 0 でも発生(JA段のFCとEN段deviation checkの検出差)。

## 5. 新腕STOP件数と系統性
- 新腕 EN STOP 1/4テーマ(space_weapons/Standard)。JA STOP 0/4。影STOP(最終) 0。= STOPの系統性は現時点で見られない(4/4での連発ではない)。
- 旧腕: JA STOP 2/4(meta, hormuz)、old Standard STOP 1/4(small_bag)、完走見込み 1/4(space_weapons、Standard以降未実行)。

## 6. 費用(登録単価x トークン。raw / guard)
| 区分 | raw円 | guard円 |
|---|---|---|
| 台帳合計(G1+round1、runner ledger) | 246.22 | 344.02 |
| うち本委任(round1)増分 | 205.58 | 約285.9 |
| Astra R1+R2(台帳内4テーマ) | 197.32 | 295.98 |
| 新腕 ledger計 テーマ別 raw | meta 41.19 / hormuz 73.87 / space_weapons 77.02 / small_bag 41.17 | |
| 旧腕 ledger計 テーマ別 raw | meta 1.76 / hormuz 1.16 / space_weapons 2.15 / small_bag 7.89 | |
- Stage R(¥178.99)はrunner台帳外。**Trial累計(raw) = 178.99 + 246.22 = 約¥425.21**。guard基準(runner cap 820、alert 650)は344.02で未到達。
- 段別内訳は `round1_aggregate/aggregate.json` と ledger_costs_worker1..4.jsonl。B1回復の再実行(hormuz/space_weapons)分のAstra R1/R2再支出を含む(各約¥64、通常の約2倍)。
- 1 Checker run 最大 ¥5.35(cap ¥10内)。API失敗行 0、web_search行 0((m)違反なし)。
- 請求ダッシュボードとの照合は未実施。

## 7. 所要時間・資源
- 起動 09:56:39 -> 全worker終了 10:22:36(約26分、4並列)。worker別: meta 約3分(新腕Checker stdのみ)、hormuz 約18分(B1再実行含む)、space_weapons 約24分(停止)、small_bag 約26分。
- 空き物理メモリ 約4.0〜4.4GB(4GB下限の近傍、割り込みなし、runner wait_memory 発動なし、4並列で降格なし)。
- Waste検知: waste_flags 空。ただし B1回復の再実行によるAstra重複支出は上記のとおり。

## 8. 観察(各テーマ)
- meta(新): JA 1029字、R0〜R2 FC major 0、new_specific_claim 0、M1発火なし、Checker adv/std とも STAGE2_DOWNGRADE。
- hormuz(新): JA 962字、new_specific_claim 0、EN Advanced 初回に HF-006 ja_source MAJOR -> B1回復後 全段 LEDGER_COMPLIANT・Checker 2本とも DOWNGRADE。旧腕はOriginal FC MAJOR残存でJA STOP。
- space_weapons(新): JA 898字、new_specific_claim 0、Advanced compliant・Checker adv は Rewrite 1回を経て DOWNGRADE(¥5.35、最高額)、Standard は ja_source MAJOR(F-001)が B1後も残りSTOP。旧: JA 888字、new_specific_claim 2、Advanced compliant。
- small_bag(新): JA 992字、new_specific_claim 1、全段 compliant、Checker 2本 DOWNGRADE。旧: JA 700字、new_specific_claim 3、Advanced は案B後に compliant、Standard は MB-05 で STOP。
- JA品質の一言所見(機械指標のみ): 新腕の new_specific_claim は 0/0/0/1、旧腕は 2/3 (JA合格した2本)。内容の面白さ・読み味は未評価(盲検ラベルは最終集計)。

## 9. 暫定集計(判定線評価なし)
`round1_aggregate/AGGREGATE.md`(再開前の部分データ。旧腕 space_weapons は途中)。主要欄: 予定run 8/8、Checker run完了 新7/旧1、Rewrite 新1/旧0、Human Review 0/0、EN std STOP 新1/旧0(旧small_bagは別カテゴリ集計)、N B1回復 新2、費用raw 新233.26/旧12.96。
**注意**: この表は旧腕が未完了のため確定値ではない。再開完了後に再集計する。

## 10. 再開に必要な手順(Fable承認後)
1. `runs/STOP.json` を `STOP_defect_delegation12.json` へ改名して全停止を解除。
2. ArmState に reset を追記(space_weapons/new の new_shadow、small_bag/old の old_shadow = failed 解除)。
3. `run --root ... --themes space_weapons --arms new,old --worker-id 3 --cap-jpy 820 --alert-jpy 650 --allow-script-change` と `--themes small_bag --arms new,old --worker-id 4 ...`(runner変更のため script sha 不一致は記録のみ)。

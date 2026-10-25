# BUDGET_PLAN_02: Family Y Production立上げ 費用計画(委任_02A更新。**見積であり増額承認の依頼ではない**)

管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 委任_02A / 2026-10-25(JST)。`BUDGET_PLAN_01.md`を、Opus M-6(voices段のruntime evidence追加)・M-1較正・M-2書換えevidenceの**実費**で更新。単価の出典・前提(再利用/新規)はBUDGET_PLAN_01 §0〜§1のとおり。実測が出たものは実測、他は推定。為替=pricing_snapshot.json。

## 1. 本委任(02A)の実費(実測)

| 項目 | 内容 | 実費(円) | 出典 |
|---|---|---|---|
| M-1較正 gate | 過去Closing 11+案B+Lead/紹介の再判定+食い違い件の旧prompt対照(gpt-6-luna high、15 call) | 2.294 | `calibration_01/raw_usage_log.jsonl` |
| M-1較正 repeat | 判定器ばらつき(Closing新prompt追加、案B新6+旧6) | 2.913 | 同 |
| M-1較正 leadrepeat | Lead/紹介 新3+旧3 | 0.762 | 同 |
| M-2書換え 初回run(guardなし) | R1宅配gen_1(判定1回)+R2宅配H2(判定2+書換え1) | 2.641 | `rewrite_evidence_01_v1_without_scope_guard/` |
| M-2書換え 最終run(guardあり) | 同(H2は判定3+書換え2) | 5.737 | `rewrite_evidence_01/` |
| **合計** | | **14.347円** | `er121_family_y_calibration_01.spent_jpy` |

- 見積(委任文: 約5〜15円)の範囲内。Cap 150円に対する消化率 9.6%。残Cap **135.65円**。
- 計上外: 本委任のClaude Code利用分(日次API費用の対象外)。単価の根拠: M-1判定 約0.15〜0.2円/call(luna high、実測。BUDGET_PLAN_01の想定0.05〜0.6円内)、M-2書換え(sol medium)1 call 約1〜2.5円(実測の範囲)。

## 2. 立上げ総額の更新(Opus M-6・R-2・R-7反映)

BUDGET_PLAN_01 §2(2)からの変更点: (a)E-3に`voices`段(Production Voice生成+Voice Gate)を追加(M-6)、(b)E-3は`english`・`plan`まで(R-2)、(c)M-1較正とM-2 evidenceは実費14.35円(上表)。

| 項目 | 内容 | 見積(円) | 備考 |
|---|---|---|---|
| E-1 | 宅配(案B固定)を正式経路で1記事完成。再利用manifest使用。**案BのGate判断待ち**(GATE_CALIBRATION_01 §3) | 27〜39 | 変更なし |
| E-2 | HRなし/ありの両経路(KP差分のみ) | 8〜18 | 変更なし |
| E-3 | SNS年齢制限: `voices`段(M-6)+Lead/紹介+`closing`(一般化)+Gate+英訳(`english`)+`plan`まで、音声なし | **44〜62**(旧24〜36 +voices 20〜26) | voices実測=宅配/SNSのTrial R0が19.8〜25.5円(BUDGET_PLAN_01 §1) |
| 試験的少額call | routing/model_id確認等 | 1〜2 | 変更なし |
| 再試行余裕(E-1+E-3の約25%) | HR Lock、翻訳retry、Gate書換え | 18〜25 | E-3増に比例 |
| (済)M-1較正+M-2 evidence | 本委任の実費 | 14.35 | §1 |
| **立上げ総額** | | **約112〜160円(中央約135円)** | 旧73〜113円(中央93円)から+約39〜47円 |

- **個別Cap 150円との関係**: 中央値135円はCap内、**上限側(160円)はCapを約10円超過し得る**。Cap超過見込みはFableへの報告事項(委任文の規定)。**提案: 個別Capを170円へ引上げ**(見積上限160円+約6%)。承認済みScope(APPROVED_FOR_PRODUCTION)内・案件見積300円以下のため、7-7によりユーザーの都度承認は不要(Fable判断)。日付・stage分割による境界回避なし。
- 削減余地(Charter原則3、承認事項を独断で取らない): ①E-3のvoicesを「既存SNS R0を来歴検査付きで再利用」に変えれば約20〜26円減(**ただしOpus M-6が『voices段のProduction runtime evidence』を求めているため、再利用では目的を満たさない。Fable判断**)。②Closing effort mediumは単価-55%だがRound 2で宅配が劣り不採用候補(ユーザー判断)。
- **案BのGate判断により、E-1の見積は変わらない**が、STOPが出た場合はE-1の「Closing固定注入」で止まり、その時点までの費用(Lead/紹介再利用で約0円+判定1回)が無駄になるだけで、大きな損失はない。

## 3. 正常系1記事の完成費用(BUDGET_PLAN_01 §2(1))の更新

- A(宅配、案B固定、再利用あり): 約27〜35円(変更なし)。
- B(通常のY記事、再利用なし): 約69〜93円(中央81円。**M-1の判定回数変動**は±0.2円/判定の範囲で影響軽微。Closing Gate FAILの局所書換え期待追加0.5〜1.4円/記事は、**M-2実測(H2: 判定3回+書換え2回=約5.7円)**から、FAIL発生時の1記事あたり追加は約2〜6円と読み直す。FAIL頻度が高い題材(宅配H2型)では期待値が上振れ)。
- 量産単価70円に対しBの中央81円は約11円超過(変更なし。実測後にユーザー判断として提示)。

## 4. 本日の予算(JST 2026-10-25)

| 項目 | 円 | 根拠 |
|---|---|---|
| 日次上限 | 1,500 | 委任文 |
| 日次累計(`docs/pm/tools/daily_dev_cost_01.py` adopted) | 991.61 | 実行出力(records 1,065)。02A開始時の974.9から+16.71(本委任の14.35+並行案件分) |
| 未反映分(Closing一般化 Round 2、ツール未捕捉) | +94.28 | OPEN-463 委任_33記載(`raw_usage_log_high/medium.jsonl`名は走査対象外) |
| **補正後の日次累計** | **1,085.89** | |
| **本日残額** | **414.11** | |

- 本日中にさらに有料を行うのはFableの判断。E-3の`closing`部だけなら約20〜25円で本日中にも実行可能(runner不要)だが、**案B判断と独立のためFableが判断**(本委任の範囲外)。
- 補足: ツール未捕捉(Batch等)があるため日次累計は下限値。

## 5. R-6(原価): 未確認
- cached_tokens実測: 本委任のusageログに`cached_tokens`が含まれるか未確認(次委任のE-3実測時に`resp.usage`の詳細で確認)。flex/Batch(非同期割引)の可否も未確認。Closing生成(1生成約17〜21円)は入力約3k+出力約11k tokensでreasoning出力が支配的のため、入力cacheの効果は小さい見込み(推測)。

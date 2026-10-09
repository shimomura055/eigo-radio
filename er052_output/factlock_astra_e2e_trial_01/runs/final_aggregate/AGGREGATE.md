# E2E 最終集計(委任_13、自動生成・判定線評価なし)

root: `er052_output/factlock_astra_e2e_trial_01/runs` / テーマ(9): meta, hormuz, space_weapons, small_bag, byd_recall, central_bank_mortgage, openai_copyright, semiconductor_earnings, streaming_price
予定run数 = 9テーマ x 2腕 x 2レベル = 36 run(旧4=16、新5=20)。分母は予定run数、STOPは独立カテゴリ。

## 1. 到達状態表(JA / EN / Checker最終状態)

| テーマ | 腕 | JA | JA FC MAJOR(R2) | shadow | Adv EN | Adv Checker | Std EN | Std Checker |
|---|---|---|---|---|---|---|---|---|
| meta | new | done | 0 | done | done | RESOLVED_STAGE2_DOWNGRADE | done | RESOLVED_STAGE2_DOWNGRADE |
| meta | old | stop | 1 | - | - | - | - | - |
| hormuz | new | done | 0 | done | done | RESOLVED_STAGE2_DOWNGRADE | done | RESOLVED_STAGE2_DOWNGRADE |
| hormuz | old | stop | 0 | - | - | - | - | - |
| space_weapons | new | done | 0 | done | done | RESOLVED_REWRITE_THEN_DOWNGRADE | stop | - |
| space_weapons | old | done | 0 | done | done | RESOLVED_STAGE2_DOWNGRADE | done | RESOLVED_STAGE2_DOWNGRADE |
| small_bag | new | done | 0 | done | done | RESOLVED_STAGE2_DOWNGRADE | done | RESOLVED_STAGE2_DOWNGRADE |
| small_bag | old | done | 0 | done | stop | RESOLVED_STAGE2_DOWNGRADE | - | - |
| byd_recall | new | done | 0 | done | done | RESOLVED_REWRITE_THEN_DOWNGRADE | stop | - |
| byd_recall | old | done | 0 | done | stop | RESOLVED_STAGE2_DOWNGRADE | - | - |
| central_bank_mortgage | new | stop(R0) | None | - | - | - | - | - |
| central_bank_mortgage | old | done | 0 | done | done | RESOLVED_STAGE2_DOWNGRADE | done | RESOLVED_STAGE2_DOWNGRADE |
| openai_copyright | new | done | 0 | - | stop | - | - | - |
| openai_copyright | old | done | 0 | done | done | RESOLVED_STAGE2_DOWNGRADE | done | RESOLVED_REWRITE_THEN_DOWNGRADE |
| semiconductor_earnings | new | done | 0 | - | stop | - | - | - |
| semiconductor_earnings | old | done | 3 | done | done | RESOLVED_STAGE2_DOWNGRADE | done | RESOLVED_REWRITE_THEN_DOWNGRADE |
| streaming_price | new | done | 0 | done | done | RESOLVED_STAGE2_DOWNGRADE | done | RESOLVED_STAGE2_DOWNGRADE |
| streaming_price | old | done | 0 | done | done | RESOLVED_STAGE2_DOWNGRADE | done | RESOLVED_REWRITE_THEN_DOWNGRADE |

## 2. 全9テーマ(§81行立て+追加指標)

テーマ: byd_recall, central_bank_mortgage, hormuz, meta, openai_copyright, semiconductor_earnings, small_bag, space_weapons, streaming_price(各腕予定run 18)

| 指標 | 新腕 | 旧腕 | 差(新-旧) |
|---|---|---|---|
| 予定run数 | 18 | 18 | 0 |
| Checker run完了 | 10 | 12 | -2 |
| A 初回候補(延べ) | 82 | 106 | -24 |
| A 再分類で除外されたclaim | 169 | 76 | 93 |
| I M3保護claim | 6 | 0 | 6 |
| I M3: changed_actor保護されたはずの除外claim(影) | 0 | 5 | -5 |
| C Rewrite発生run数 | 2 | 3 | -1 |
| C Rewrite率(予定run分母) | 0.111 | 0.167 | -0.056 |
| D Human Review run数 | 0 | 0 | 0 |
| E 費用 raw円 | 395.115 | 63.923 | 331.192 |
| G JA FC MAJOR(R2) | 0 | 4 | -4 |
| G JA 記号Gate指摘 | 0 | 0 | 0 |
| H EN advanced STOP | 2 | 2 | 0 |
| H EN advanced 初回MAJOR | 2 | 0 | 2 |
| H EN advanced 初回MAJOR(translation由来) | 0 | 0 | 0 |
| H EN standard STOP | 2 | 0 | 2 |
| H EN standard 初回MAJOR | 2 | 3 | -1 |
| H EN standard 初回MAJOR(translation由来) | 2 | 0 | 2 |
| K 初回JA_RECHECK(記事数) | 4 | 3 | 1 |
| L 人手介入(件) | 6 | 6 | 0 |
| L 人手介入率(予定run分母) | 0.333 | 0.333 | 0.0 |
| M 新規具体主張(ii)最終JA | 2 | 15 | -13 |
| N 影STOP(最終) | 0 | 0 | 0 |
| N B1回復発動 | 3 | 0 | 3 |

追加(段別EN内訳・M1/影・shadow):

- 新腕: EN adv STOP 2 / EN std STOP 2 / ja_source MAJOR(adv,std)=2,0 / M1発火(adv,std)=0,2 / 人手介入内訳={'ja_stop': 2, 'shadow_stop': 0, 'en_stop': 4, 'human_review': 0, 'total': 6, 'rate_over_planned': 0.3333333333333333} / shadow初回STOP=0 最終=0 / B1回復=3 拒否=2 / M3保護=6 影=0 / R0 echo残存=0
- 旧腕: EN adv STOP 2 / EN std STOP 0 / ja_source MAJOR(adv,std)=0,3 / M1発火(adv,std)=0,0 / 人手介入内訳={'ja_stop': 4, 'shadow_stop': 0, 'en_stop': 2, 'human_review': 0, 'total': 6, 'rate_over_planned': 0.3333333333333333} / shadow初回STOP=0 最終=0 / B1回復=0 拒否=0 / M3保護=0 影=5 / R0 echo残存=0

## 3. 層別: 旧4テーマ(meta/hormuz/space_weapons/small_bag)

テーマ: hormuz, meta, small_bag, space_weapons(各腕予定run 8)

| 指標 | 新腕 | 旧腕 | 差(新-旧) |
|---|---|---|---|
| 予定run数 | 8 | 8 | 0 |
| Checker run完了 | 7 | 3 | 4 |
| A 初回候補(延べ) | 54 | 30 | 24 |
| A 再分類で除外されたclaim | 135 | 31 | 104 |
| I M3保護claim | 1 | 0 | 1 |
| I M3: changed_actor保護されたはずの除外claim(影) | 0 | 0 | 0 |
| C Rewrite発生run数 | 1 | 0 | 1 |
| C Rewrite率(予定run分母) | 0.125 | 0.0 | 0.125 |
| D Human Review run数 | 0 | 0 | 0 |
| E 費用 raw円 | 395.115 | 63.923 | 331.192 |
| G JA FC MAJOR(R2) | 0 | 1 | -1 |
| G JA 記号Gate指摘 | 0 | 0 | 0 |
| H EN advanced STOP | 0 | 1 | -1 |
| H EN advanced 初回MAJOR | 0 | 0 | 0 |
| H EN advanced 初回MAJOR(translation由来) | 0 | 0 | 0 |
| H EN standard STOP | 1 | 0 | 1 |
| H EN standard 初回MAJOR | 1 | 2 | -1 |
| H EN standard 初回MAJOR(translation由来) | 1 | 0 | 1 |
| K 初回JA_RECHECK(記事数) | 2 | 1 | 1 |
| L 人手介入(件) | 1 | 5 | -4 |
| L 人手介入率(予定run分母) | 0.125 | 0.625 | -0.5 |
| M 新規具体主張(ii)最終JA | 1 | 5 | -4 |
| N 影STOP(最終) | 0 | 0 | 0 |
| N B1回復発動 | 2 | 0 | 2 |

追加(段別EN内訳・M1/影・shadow):

- 新腕: EN adv STOP 0 / EN std STOP 1 / ja_source MAJOR(adv,std)=0,0 / M1発火(adv,std)=0,1 / 人手介入内訳={'ja_stop': 0, 'shadow_stop': 0, 'en_stop': 1, 'human_review': 0, 'total': 1, 'rate_over_planned': 0.125} / shadow初回STOP=0 最終=0 / B1回復=2 拒否=0 / M3保護=1 影=0 / R0 echo残存=0
- 旧腕: EN adv STOP 1 / EN std STOP 0 / ja_source MAJOR(adv,std)=0,2 / M1発火(adv,std)=0,0 / 人手介入内訳={'ja_stop': 4, 'shadow_stop': 0, 'en_stop': 1, 'human_review': 0, 'total': 5, 'rate_over_planned': 0.625} / shadow初回STOP=0 最終=0 / B1回復=0 拒否=0 / M3保護=0 影=0 / R0 echo残存=0

## 4. 層別: 新5テーマ(byd_recall/central_bank_mortgage/openai_copyright/semiconductor_earnings/streaming_price)

テーマ: byd_recall, central_bank_mortgage, openai_copyright, semiconductor_earnings, streaming_price(各腕予定run 10)

| 指標 | 新腕 | 旧腕 | 差(新-旧) |
|---|---|---|---|
| 予定run数 | 10 | 10 | 0 |
| Checker run完了 | 3 | 9 | -6 |
| A 初回候補(延べ) | 28 | 76 | -48 |
| A 再分類で除外されたclaim | 34 | 45 | -11 |
| I M3保護claim | 5 | 0 | 5 |
| I M3: changed_actor保護されたはずの除外claim(影) | 0 | 5 | -5 |
| C Rewrite発生run数 | 1 | 3 | -2 |
| C Rewrite率(予定run分母) | 0.1 | 0.3 | -0.2 |
| D Human Review run数 | 0 | 0 | 0 |
| E 費用 raw円 | 395.115 | 63.923 | 331.192 |
| G JA FC MAJOR(R2) | 0 | 3 | -3 |
| G JA 記号Gate指摘 | 0 | 0 | 0 |
| H EN advanced STOP | 2 | 1 | 1 |
| H EN advanced 初回MAJOR | 2 | 0 | 2 |
| H EN advanced 初回MAJOR(translation由来) | 0 | 0 | 0 |
| H EN standard STOP | 1 | 0 | 1 |
| H EN standard 初回MAJOR | 1 | 1 | 0 |
| H EN standard 初回MAJOR(translation由来) | 1 | 0 | 1 |
| K 初回JA_RECHECK(記事数) | 2 | 2 | 0 |
| L 人手介入(件) | 5 | 1 | 4 |
| L 人手介入率(予定run分母) | 0.5 | 0.1 | 0.4 |
| M 新規具体主張(ii)最終JA | 1 | 10 | -9 |
| N 影STOP(最終) | 0 | 0 | 0 |
| N B1回復発動 | 1 | 0 | 1 |

追加(段別EN内訳・M1/影・shadow):

- 新腕: EN adv STOP 2 / EN std STOP 1 / ja_source MAJOR(adv,std)=2,0 / M1発火(adv,std)=0,1 / 人手介入内訳={'ja_stop': 2, 'shadow_stop': 0, 'en_stop': 3, 'human_review': 0, 'total': 5, 'rate_over_planned': 0.5} / shadow初回STOP=0 最終=0 / B1回復=1 拒否=2 / M3保護=5 影=0 / R0 echo残存=0
- 旧腕: EN adv STOP 1 / EN std STOP 0 / ja_source MAJOR(adv,std)=0,1 / M1発火(adv,std)=0,0 / 人手介入内訳={'ja_stop': 0, 'shadow_stop': 0, 'en_stop': 1, 'human_review': 0, 'total': 1, 'rate_over_planned': 0.1} / shadow初回STOP=0 最終=0 / B1回復=0 拒否=0 / M3保護=0 影=5 / R0 echo残存=0

## 5. 新規具体主張(ii)・JA字数(テーマ別)

| テーマ | 腕 | (ii)最終 | (ii)差vs R0 | JA字数 | 初回JA_RECHECK | M1発火(adv/std) | 影の対照(m1a alt判定 / m1b) |
|---|---|---|---|---|---|---|---|
| meta | new | 0 | 0 | 988 | False | False/False | alt=LEDGER_COMPLIANT(old_input) / m1b_fired=False |
| meta | old | None | None | None | False | None/None | - |
| hormuz | new | 0 | -1 | 914 | True | False/False | alt=LEDGER_COMPLIANT(old_input) / m1b_fired=False |
| hormuz | old | None | None | None | False | None/None | - |
| space_weapons | new | 0 | 0 | 857 | True | False/True | alt=LEDGER_DEVIATION(old_input) / m1b_fired=False |
| space_weapons | old | 2 | 1 | 851 | False | False/False | alt=LEDGER_COMPLIANT(m1_input) / m1b_fired=False |
| small_bag | new | 1 | 1 | 942 | False | False/False | alt=LEDGER_COMPLIANT(old_input) / m1b_fired=False |
| small_bag | old | 3 | 1 | 665 | True | False/False | alt=LEDGER_COMPLIANT(m1_input) / m1b_fired=False |
| byd_recall | new | 1 | 0 | 974 | False | False/True | alt=LEDGER_COMPLIANT(old_input) / m1b_fired=False |
| byd_recall | old | 4 | 2 | 835 | True | False/False | alt=LEDGER_DEVIATION(m1_input) / m1b_fired=False |
| central_bank_mortgage | new | None | None | None | False | None/None | - |
| central_bank_mortgage | old | 0 | -1 | 779 | False | False/False | alt=LEDGER_COMPLIANT(m1_input) / m1b_fired=False |
| openai_copyright | new | 0 | 0 | 971 | True | False/None | - |
| openai_copyright | old | 1 | 0 | 671 | True | False/False | alt=LEDGER_COMPLIANT(m1_input) / m1b_fired=False |
| semiconductor_earnings | new | 0 | 0 | 882 | True | False/None | - |
| semiconductor_earnings | old | 4 | 3 | 750 | False | False/False | alt=LEDGER_COMPLIANT(m1_input) / m1b_fired=False |
| streaming_price | new | 0 | 0 | 922 | False | False/False | alt=LEDGER_COMPLIANT(old_input) / m1b_fired=False |
| streaming_price | old | 1 | 1 | 629 | False | False/False | alt=LEDGER_COMPLIANT(m1_input) / m1b_fired=False |

## 6. B3由来 / 台帳AMBIGUOUS由来(機械的候補、確定ではない)

注: Checker cycle1 stage2 MAJOR を母集団とし、AMBIGUOUS候補=related_fact_idが当該テーマのAMBIGUOUS選択ID、B3候補=B3 unmapped_claimsを持つテーマでrelated_fact_id空 or unsupported_new_claim。EN/JA言語差のため本文照合は未実施、確定は人手/Fable突合。

| テーマ | 腕 | レベル | cycle1 stage2 MAJOR | AMBIGUOUS候補 | B3候補 | テーマunmapped数 | テーマAMBIGUOUS選択 |
|---|---|---|---|---|---|---|---|
| meta | new | advanced | 6 | 0 | 0 | 0 | [] |
| meta | new | standard | 6 | 0 | 0 | 0 | [] |
| hormuz | new | advanced | 13 | 0 | 1 | 1 | [] |
| hormuz | new | standard | 15 | 0 | 3 | 1 | [] |
| space_weapons | new | advanced | 22 | 0 | 0 | 0 | [] |
| space_weapons | old | advanced | 13 | 0 | 0 | 0 | [] |
| space_weapons | old | standard | 12 | 0 | 0 | 0 | [] |
| small_bag | new | advanced | 18 | 0 | 0 | 0 | [] |
| small_bag | new | standard | 16 | 0 | 0 | 0 | [] |
| small_bag | old | advanced | 17 | 0 | 0 | 0 | [] |
| byd_recall | new | advanced | 25 | 0 | 0 | 0 | [] |
| byd_recall | old | advanced | 21 | 0 | 0 | 0 | [] |
| central_bank_mortgage | old | advanced | 11 | 0 | 0 | 0 | [] |
| central_bank_mortgage | old | standard | 6 | 0 | 0 | 0 | [] |
| openai_copyright | old | advanced | 5 | 0 | 0 | 0 | [] |
| openai_copyright | old | standard | 19 | 0 | 0 | 0 | [] |
| semiconductor_earnings | old | advanced | 11 | 0 | 1 | 4 | ['F1'] |
| semiconductor_earnings | old | standard | 13 | 0 | 3 | 4 | ['F1'] |
| streaming_price | new | advanced | 13 | 2 | 0 | 0 | ['F01', 'F07'] |
| streaming_price | new | standard | 10 | 0 | 0 | 0 | ['F01', 'F07'] |
| streaming_price | old | advanced | 16 | 0 | 0 | 0 | ['F01', 'F07'] |
| streaming_price | old | standard | 16 | 0 | 0 | 0 | ['F01', 'F07'] |

合計(候補): AMBIGUOUS 新2/旧0 / B3 新4/旧4

## 7. 費用(円。raw=登録単価xトークン、guard=astra分x1.5)

- 本台帳合計(G1+G2): raw 459.04 / guard 625.89
- Astra段(new_r1+new_r2): raw 336.71 / guard 503.56
- B1回復の再支出(推定、b1_recovery以降の同テーマ新腕再実行段): raw 102.99 / guard 148.42 内訳 [{'theme': 'hormuz', 'trigger': 'en_ja_source_major', 'after_ts': '2026-10-09T10:00:48', 'raw': 33.52, 'guard': 48.58}, {'theme': 'openai_copyright', 'trigger': 'en_ja_source_major', 'after_ts': '2026-10-09T10:44:31', 'raw': 33.23, 'guard': 48.5}, {'theme': 'space_weapons', 'trigger': 'en_ja_source_major', 'after_ts': '2026-10-09T10:04:51', 'raw': 36.24, 'guard': 51.34}]
- Trial累計(Stage R raw 178.99込み): raw 638.03

腕別:

| 腕 | raw | guard |
|---|---|---|
| new | 395.12 | 561.96 |
| old | 63.92 | 63.92 |

テーマ別:

| テーマ | raw | guard |
|---|---|---|
| byd_recall | 39.08 | 50.0 |
| central_bank_mortgage | 7.89 | 7.89 |
| hormuz | 75.03 | 106.85 |
| meta | 42.95 | 60.41 |
| openai_copyright | 67.02 | 93.21 |
| semiconductor_earnings | 43.91 | 60.8 |
| small_bag | 49.29 | 65.98 |
| space_weapons | 85.78 | 117.62 |
| streaming_price | 48.07 | 63.14 |

テーマ/腕別:

| テーマ/腕 | raw | guard |
|---|---|---|
| byd_recall/new | 30.6 | 41.51 |
| byd_recall/old | 8.49 | 8.49 |
| central_bank_mortgage/new | 1.64 | 1.64 |
| central_bank_mortgage/old | 6.25 | 6.25 |
| hormuz/new | 73.87 | 105.69 |
| hormuz/old | 1.16 | 1.16 |
| meta/new | 41.19 | 58.66 |
| meta/old | 1.76 | 1.76 |
| openai_copyright/new | 56.18 | 82.36 |
| openai_copyright/old | 10.85 | 10.85 |
| semiconductor_earnings/new | 35.64 | 52.52 |
| semiconductor_earnings/old | 8.28 | 8.28 |
| small_bag/new | 41.17 | 57.85 |
| small_bag/old | 8.12 | 8.12 |
| space_weapons/new | 77.45 | 109.29 |
| space_weapons/old | 8.33 | 8.33 |
| streaming_price/new | 37.38 | 52.45 |
| streaming_price/old | 10.69 | 10.69 |

段別:

| 段 | raw | guard |
|---|---|---|
| new_check_adv | 20.04 | 20.04 |
| new_check_std | 11.05 | 11.05 |
| new_en_adv | 6.4 | 6.4 |
| new_en_std | 5.43 | 5.43 |
| new_ii | 4.81 | 4.81 |
| new_r0 | 7.84 | 7.84 |
| new_r1 | 173.19 | 259.02 |
| new_r2 | 163.52 | 244.54 |
| new_shadow | 2.83 | 2.83 |
| old_adv | 9.63 | 9.63 |
| old_check_adv | 15.61 | 15.61 |
| old_check_std | 18.52 | 18.52 |
| old_ii | 3.46 | 3.46 |
| old_ja | 12.08 | 12.08 |
| old_shadow | 2.65 | 2.65 |
| old_std | 1.98 | 1.98 |

台帳の最初/最後のts: 2026-10-09T09:32:56 - 2026-10-09T11:14:40

盲検ラベル・Fable突合が必要な欄(真に重大/不要/F重大軽微)は未計測(None)。判定線の評価は本書では行わない。

# FAMILY-X-COFFEE-P8-FINAL-AUDIO-AND-PRODUCTION-WIRING-01 委任_03(runtime evidence run、2026-10-12、実費JPY13.19/上限30)

Status: runtime evidence取得済み。**`PRODUCTION_WIRED`判定はFable/ユーザー確認待ち(未判定・未表記)**。詳細証跡: `er019_output/coffee_prices/run_p8_wiring_01/WIRING_EVIDENCE_01.md`(表・費用・model_id実測)。

## Checklist項目別結果
| 項目 | 結果 |
|---|---|
| 初回経路sha(Adv3+Std3) | 充足(style_base_sha256==P8、hintなし最終sha==P8、S2 hit 0) |
| retry sha | Std外側減速loop(3 call)は充足。内側標準retry(attempt2以降)は未発生=**未実測** |
| regen sha(1 segment) | 充足(Adv part2、+JPY0.95) |
| resume(再課金なし) | 充足(ログ増加0、費用差0、全segment再利用) |
| M3 Gate | 両level PASS。fallback/LR時の実BLOCKは未発生=**未実測**(test 32件のみ) |
| Std逐語+6%減速 | 充足(len402、減速指示非連結、減速5.97%) |
| Audio Validation/ASR/duration | 充足(全6 verified、clipping/repetition flagなし) |
| default非影響 | 充足(test 32件OK) |
| per-call照合 | Gemini 36 callのうちP8はFull Story 9 callのみ(他27 callはP8なし) |

## 費用
実費JPY13.19(b1b 4.29 -> +a2 12.24 -> resume +0 -> regen 13.19)。Coffee累計約JPY147.1(COST_LEDGER 133.9+13.19、未集計除く)。

## v4との速度差(原稿が異なる参考値)
Std全体WPM 165.7 vs v4 162.2(+2.2%)、Adv 172.9 vs 180.7(-4.3%)。同一text再生成のばらつき(Adv part2)尺+1.4%。

## 要Fable判断(重要)
1. v3/v4 Full Story原稿("Beans cost less now!"系)は現行`er019_output/coffee_prices/run_l3_01`原稿("Coffee prices are falling!"系)と別原稿だった。指示の「v3原稿から明示コピー」は、v3原稿がProduction runnerのsource_dir(article.md)として存在しないため成立せず、現行run_l3_01原稿で実施。配線証跡としては有効だがWPM比較はv4と同一原稿の再現ではない。同一原稿で再現するなら別委任(source_dir用意+追加約JPY12)。
2. regenerationは`approve_regenerate`を呼ばず、wav退避によるcache miss経路を使用(RESOLVEDはブロックしない仕様、人間承認の代行を避けた)。
3. `PRODUCTION_WIRED`判定、Production採用(人間のみ)。

## 残リスク
内側retry・fallback/LR BLOCK実測なし、Std japanese_title(非P8 role)で既存minimal_fallback発生(既存挙動)、OPEN-312/313未解決、聴感未評価。

## 成果物
`er019_coffee_p8_wiring_evidence_01.py`(集計script、API 0)、`er019_output/coffee_prices/run_p8_wiring_01/`(wav除く)、SSOT(DECISION_LOG/OPEN_ITEMS OPEN-300/CURRENT_SPEC注記)。

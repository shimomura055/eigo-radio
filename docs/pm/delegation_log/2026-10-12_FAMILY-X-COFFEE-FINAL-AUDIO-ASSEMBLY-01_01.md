# FAMILY-X-COFFEE-FINAL-AUDIO-ASSEMBLY-01 委任_01(2026-10-12)

Status: **STOP / USER_DECISION_REQUIRED(Standard Full Story Part2がPrimary ASR判定を3回連続で通過せず)**。Advancedは組立・QA完了、Standard組立は未実施、試聴ページ・Production差異・SSOT記録は未実施(Standardが完成しないため保留)。Trial隔離、Production未配線、共通Prompt/routing/Master Store変更なし。

## 実施済み
1. 計画・概算 `er057_output/coffee_final_audio_assembly_01/FINAL_V3_BUILD_PLAN_01.md`(再生成=Std Full Story 3 + IOL 2 call、概算JPY6〜8、上限JPY50)。
2. In One Line新原稿(両レベル2文、gpt-6-luna各1 call、費用JPY0.204)+事実対応表+難易度+Comment 4接続 `IN_ONE_LINE_REWRITE_01.md`。Std/Adv IOL TTS(現行Style踏襲、Primary ASR attempt1で合格)。
   - Std: Coffee bean prices fell, but shop prices may take at least about nine months to change. Other costs also matter, so lower bean prices do not promise a cheaper cafe cup.
   - Adv: Experts estimate raw-bean prices may take at least about nine months to show up in US retail prices. Even if bean prices fall, a cafe cup may not get cheaper because cups and labor also add to its cost.
3. Std Full Story: PD8 Prompt(sha 329ff46a…照合OK、gemini-3.8-flash-lite-tts/Aoede、F5同様tts_safe_news_en適用)。Part1 OK(NUMERIC_EQUIVALENCE_MATCH)・Part3 OK(NORMALIZED_MATCH)、6%減速適用(Part1 44.32->46.964s ratio 1.0597、Part3 45.76->48.487s ratio 1.0596、IOL 11.59->12.272s ratio 1.0588)。**Part2は3 attempt(初回+再生成2回、同一Prompt)すべて `ASR_VALIDATION_UNCERTAIN`**(duration 50.47/49.44/53.48s)。
4. Advanced v3組立: PD8 Trial wav(sha一致)+K2+新IOL等。288.45s -> 314.97s、peak 0.959、clip 0、headroom安全弁未発動。QA `qa_v3_01.json`、異音検知(閾値不変)`anomaly_v3_adv.json`: 候補20件(固定音源含む、非固定11件)、medium/high非固定0件(全てlow: click/level_step/spec_jump)。

## STOP理由と判断依頼(USER_DECISION_REQUIRED)
Part2の3 attempt全てのASR文は原稿と実質同一(差異は US->U.S.、cost->costs、9->nine、2->two、raw-bean->raw bean、大文字小文字、コロン消失のみ)だが、既存validatorが `us` vs `u s` 等を entity_like差分として UNCERTAIN とした(Final v2のF5 Part2は同条件で NORMALIZED_MATCH だった)。指示は「minimal/LR/Secondary禁止、それでもNGはSTOP」のため、独自判断でGateを回避せず停止した。
選択肢: (A) Part2に限りSecondary ASR(Production既存のcascade)での確認を許可、(B) 3 attempt中の1つ(候補wav `attempts/std_part2_a{1,2,3}.wav`)をユーザー試聴のうえ人間承認として採用、(C) 追加の同一Prompt再生成を許可。いずれも追加費用は数円。

## 費用・保存先
TTS+ASR推定JPY約8.43(Part2再生成2回含む)+IOL原稿LLM JPY0.204、累計約JPY8.6(上限JPY50)。成果物: `er057_output/coffee_final_audio_assembly_01/`(attempts/segments/final_v3は音声のためgit対象外)、scripts `er057_coffee_final_v3_{gen,build,anomaly,iol_text}_01.py`。
## 未実施(再開時)
Std Part2確定->Std組立・QA・異音->試聴ページ `user_test/coffee_final_v3/`・Playwright実再生->PRODUCTION_DIFF_V3_01.md->SSOT(DECISION_LOG/CURRENT_SPEC追記/OPEN_ITEMS/REPORT_LEDGER)。ユーザー決定(Coffee限定APPROVED_FOR_PRODUCTION、採用Style表、IOL方針の履行不足/新方針区別)のSSOT記録も未実施。

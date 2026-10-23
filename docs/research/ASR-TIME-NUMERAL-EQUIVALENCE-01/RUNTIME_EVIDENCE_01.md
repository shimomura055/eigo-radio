# RUNTIME_EVIDENCE_01(ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_02、API 0・新規TTSなし・費用0円)

実行器 `runtime_evidence_02.py`、生データ `runtime_base_02.json`(修正前=`--modules base_HEAD`)/`runtime_after_02.json`(修正後)。X/Zの既存保存entry(`tts_generation_results.json`)を **再利用の正式経路 `er078_reuse_value_guard_01.guard_entry`(内部で引継ぎの正式経路 `rejudge_with_current_judge` を呼ぶ)** で再判定した。Z entryは `er109_xz_scope_01.run_scope('Z')`、Xは `run_scope('X')` の内側(=X/Z Productionと同じscope)。`classify_asr_match`のtelemetry自動追記はno-op化。各recordの`api_calls`/`secondary_new_calls`は0(API 0、Secondary新規呼出0)。
対象: Z `er026_output/family_z_production_e2e_01/after_twenty_years/run_sf_prod_01/a2/audit/tts_generation_results.json`(『二十年後』Std)+同runのc8 attempt2ファイル、X `er019_output/family_x_audio_production_wiring_01/` の coffee_prices(2 run)/hormuz/small_bag/ig_nobel_2026 の a2 results。合計43 record、判定が変化したのは3件(下表)。保存entry(35件: Z・X)の判定変化=0(PASS→NG 0)。

## 1. 変化したrecord・時刻/通貨に関わるrecord

| 範囲 | segment | variant | 修正前 | 修正後 |
|---|---|---|---|---|
| Z | full_story_part2_c8 | synthetic(canon=At 10 thirty[TTS数字化後] / ASR=At 10:30) | ok PASS/primary_pass | **ok PASS/primary_pass** |
| Z | full_story_part2_c8 | synthetic(canon=At 10 thirty / ASR=At ten-thirty) [ROOT_CAUSE_01実対] | BLOCKED NG_PROTECTED/final_gate_value_diff | **ok PASS/primary_pass** |
| Z | full_story_part2_c8 | synthetic(canon=At ten thirty / ASR=At 1030) [桁連結=NG側であるべき] | BLOCKED NG_PROTECTED/final_gate_value_diff | **BLOCKED NG_PROTECTED/final_gate_value_diff** |
| Z | full_story_part2_c8 | REAL attempt2(canon=TTS入力 `At 10 thirty,` / ASR=`At ten-thirty,`) | BLOCKED NG_PROTECTED/final_gate_value_diff | **ok PASS/primary_pass** |
| X | full_story_part1 | synthetic(+ 'The shop opens at 10 thirty.' / ASR 'ten-thirty') | BLOCKED NG_PROTECTED/final_gate_value_diff | **ok PASS/primary_pass** |
| X | full_story_part1 | synthetic(+ 'The shop opens at ten thirty.' / ASR '10:30') | ok PASS/primary_pass | **ok PASS/primary_pass** |
| X | full_story_part1 | synthetic(+ 'The shop opens at ten thirty.' / ASR '1030')[NG側] | BLOCKED NG_PROTECTED/final_gate_value_diff | **BLOCKED NG_PROTECTED/final_gate_value_diff** |
| X | full_story_part1 | synthetic(+ 'Coffee costs 10 twenty-dollar bills.' / ASR '$20') | ok PASS/primary_pass | **ok PASS/primary_pass** |

## 2. 読み方
- **Z 実在の対(合成ではない)**: c8 attempt2(`full_story_part2_c8_attempt2_customa3c4625e.json`のASR=`At ten-thirty,`)とTTS入力(`er003.tts_safe_number_words_en`で数字化された `At 10 thirty,`)の対は、修正前=NG_PROTECTED(final_gate_value_diff)→修正後=PASS。これがROOT_CAUSE_01の実対。
- Z c8 保存entry(canon=`At ten thirty,`/ASR=`At 10:30,`、PRODUCTION_PLAN_01記載の実対)は修正前から再利用/引継ぎ経路ではPASS(委任_03[第1層]・委任_04[第2層 `_clock_pair`]で解消済み)で、修正後もPASS(退行なし)。
- 桁連結 `ten thirty`×`1030` は引継ぎ経路で修正前後ともNG_PROTECTED(長文では分類層の影響が異なる。短文の分類層での誤PASSはTEST_MATRIX_02で修正前BAD→修正後NGを確認)。
- X: 保存entryに時刻パターンは実質無く(時刻様のsegment=2、いずれも判定変化なし)、**合成entry**(X coffee_prices a2 の `full_story_part1` に時刻文/金額文を1文追加。合成であることをvariant名に明記)で、`At 10 thirty`×`ten-thirty` NG→PASS、`ten thirty`×`1030` NG維持、`10 twenty-dollar bills`×`10 $20 bills` PASS維持(OF-TN-01)を確認した。
- X/Zともに共通moduleの修正が正式経路(guard_entry→rejudge_with_current_judge→統一judge)で効くこと、保存entryに退行がないことを確認。完成作品への影響なし(既存完成記事の再生成はしない。『二十年後』は承認済みで再処理不要)。新規TTS=0、費用0円。

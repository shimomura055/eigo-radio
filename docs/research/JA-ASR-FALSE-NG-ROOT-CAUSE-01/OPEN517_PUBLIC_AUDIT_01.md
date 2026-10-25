# OPEN517_PUBLIC_AUDIT_01(R-2: 過去公開物の監査抽出。委任_06、2026-10-25。API 0・費用0円・Production変更0・保存済みrecordの読取のみ)
目的: OPEN-517(READING_MATCHのPrimary PASSが最終ANDゲートの値DIFF・否定差の再確認をskip)により、**値が違う音声が既に採用・公開されていないか**を保存済みrecordから抽出する(Opus R-2)。遡及是正の要否はユーザー判断(本書は事実のみ)。
再現: `PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/open517_public_audit_01.py`。出力=`open517_public_audit_01.out.json`/`.out.txt`。
## 1. 抽出条件と方法
- **A節(監査recordによる直接抽出)**: 全run dirの`tts_generation_results*.json`(435 file)の`segments[*].attempts_log[*].asr_judgement`のうち、`final_gate.skipped == "approved_equivalence:READING_MATCH"` かつ判定がPASS系 かつ `value_guard.primary.kind == DIFF`(監査は`value_guard.primary`を記録=`er078_asr_unified_judge_01.py:510`、skip=`:530`)。DIFFに加え参考としてUNKNOWN/AMBIGUOUSも列挙。
- **B節(旧run・監査record無しを含む再判定)**: 統一judge導入前(2026-10-16以前)や`legacy A/B/C`のrunには`asr_judgement`が無いため、`audio_classification in {PHONETIC_MATCH, READING_RESOLVED_MATCH}`かつ`verified`の全attempt(183件)を保存された(canonical, Primary転写)でv4(F1+F2)の純関数`reading_match_final_gate`に通し、PASS以外になる件を抽出(『F1があれば止まった』件)。
- **公開物判定**: 該当segmentの最終音声(`segments[*].sha256`/attempt音声sha256)が`user_test/`配下の音声3,869ファイル(unique sha 3,525)とsha256一致するか。sha不一致でもファイル名一致を参考として別掲。
## 2. 結果
| 項目 | 件数 |
|---|---|
| 走査したtts_generation_results file | 435(うち統一judgeの監査record有り 57) |
| 走査したjudge監査付きattempt | 633 |
| `skipped=approved_equivalence:READING_MATCH`のPASS | 62(value_guard.primary: NO_VALUES 56・EQUAL 6・**DIFF 0**・UNKNOWN 0・AMBIGUOUS 0) |
| **A節 該当(DIFF)** | **0件** |
| B節 再判定したPHONETIC_MATCH/READING_RESOLVED_MATCH verified attempt | 183 → v4でPASS以外 **0件** |
| 公開物(user_test)該当 | **0件**(該当segment自体が無い) |
補足: B節の対象外の`attempts/*.json`系(P4コーパスの421ユニークattempt、READING_MATCH PASS 133)は`eval_open517_api0_04.py`で別に全件再判定済み(F1由来の正常attemptのNG化0、既知負例以外のF1由来の変化なし=`OPEN517_EVAL_02.md` §1基準1・3)。
## 3. 解釈と限界
- **保存recordの範囲では、READING_MATCHのskipにより『値が違うのに通った』採用音声は見つからなかった**。公開物への該当は0件で、ユーザーへの遡及是正の判断依頼は不要(事実報告のみ)。
- 既知の誤PASS(`三日間`↔`三日目`等)は、N-1/N-3の人工/実音声評価で現れたもので、実運用run recordでは確認できていない(実運用での出現頻度は低いと推定されるが、証明ではない)。月題の`8000九百本超`はPhase 3の再転写(`A2_openai_moon_x3`)で得た転写で、本監査のrun recordには該当(DIFF)が無い(元runの採用判定との個別対応は未確認)。
- 限界: (1)保存されていないrun・上書き/削除されたrecord・Master Store再利用で参照された音声は対象外。(2)監査recordの`value_guard`は現行ガードの出力で、現行ガードが検出できない型(同形異音・助詞誤読・`七晩`↔`七番`・弱いかな数詞のUNKNOWN素通し)は『DIFFなし』になる。これらはF1/F2でも検出できない既知の限界(OPEN517_APPLY_PLAN_01 §7)。(3)公開物判定はsha256一致のみ。

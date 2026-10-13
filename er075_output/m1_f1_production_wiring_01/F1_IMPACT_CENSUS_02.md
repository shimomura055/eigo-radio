# F1_IMPACT_CENSUS_02 (委任_03、修正後Production関数を直接呼ぶcensus再実行)

Status: F1=WIRED_PENDING_RUNTIME_EVIDENCE。API 0 / JPY0。コマンド: `er075_m1_f1_production_wiring_01_census.py --mode production --out er075_output/m1_f1_production_wiring_01/f1_census_02.json`(stdout: census_stdout_02.txt)。
判定基準(固定): 「誤NG」=全差分が承認済みPattern A/B/Cまたは既存正規化(冠詞・`_is_benign_plural_pair`等)で説明できるのにF1が非PASSにしたケース。

## 1. 実データ(674ペア = HR queue 187 / er021 telemetry 434 / er069 results_02 53)
| 条件 | PASS→非PASS | 非PASS→PASS | その他分類変化 |
|---|---|---|---|
| segment_id=full_story_part1(role gate適用) | **0** | **0** | 0 |
| segment_id=None(dialogue相当) | **0** | **0** | 0 |
旧版でCONNECTED_SPEECH系PASS: 12件(いずれもF1後もPASS維持)。誤NG=0。
(注: 集計途中でer021 telemetryの末尾2行[9196-9197、本担当のsmoke testが追記したsynthetic例]を除外。`range(9195,9200)`を除外リストに追加済み。telemetryは共有ファイルのためcommitしない。)

## 2. KP実データ
`er019_output`/`er026_output`配下の`tts_generation_results.json`からKP名(key_phrase/kp_)のセグメントを走査: 該当2件、いずれも `text==asr_text`(差分なし)。**canonical≠ASRのKP転写ペア: なし**。KP経路は同関数共有のため自動適用(runtime evidenceは次回以降のKP有料runで取得)。

## 3. 真値付きデータ(er068 labeled sets、旧PASS→新非PASS)
- defect: `The studies suggest cats today.`/`The study suggests dogs today.`(意図どおりの是正)
- normal(仮ラベル)4件: `a US sea blockade`→`a U S se blockade`/`a U S blockade`/`planned U S blockade`/`a U S C blockade`
  - 旧: Pattern Aが `US`→`U`+s を複数形脱落と誤認(OF-162: `US`は頭字語で複数形ではない)して偶然PASS。
  - 新: `sea`の欠落/`S`・`C`の余りは連結発音で説明できない残差。**固定誤NG定義には該当しない**(`US`→`U`+s自体が未承認の頭字語正規化に由来)。別Open Item(頭字語Pattern A誤適用)へ。
  - 元音声(聴取は実施せず存在確認のみ): `er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/hormuz__run_02/a2/narration/full_story_part2.wav`(存在=True、HR queue 3行)/`.../hormuz__run_03_baseline/b1b/narration/full_story_part2.wav`(存在=True、HR queue 1行)。

## 4. 反例・正常連結(Production経路、segment_id有/無の両方)
census_stdout_02.txt の `CTR` 行。反例11件=非PASS(うち`Rex→Max`は`ASR_VALIDATION_UNCERTAIN`=retry停止、他10件=`TRUE_CONTENT_MISMATCH`)、元から非PASSの2件(`did not`・`5→6`)は維持、正常連結6件=PASS維持(`Their studies... survey suggests`1件のみ ACCEPT→PASS_WITH_WARNING[Pattern C併発のため警告ラベル付与、PASSは維持])。

# OPUS_REVIEW_STAGE2_STEPB_01(要旨): Stage 2 Trial 第1巡へのOpus独立レビュー(Step B)の所見と Fable採否

注記: **本ファイルは「要旨」である**。Opusレビュー全文はFableから渡されていないため、委任_08の委任文(`docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02_委任_08.md`「Opusレビュー(Step B)のFable採否」節)から所見ID・要旨・採否を転記した。全文が渡された場合は差し替える。

| 所見ID | 要旨 | Fable採否 | 本巡(第2巡)での扱い |
|---|---|---|---|
| OF-PNPS-S2R-01 | 第1巡の主因の補正: 受理候補集合が空であること×ASR綴り経由の判定不能が直列に効いている。発音取得の改善は後回し | 採用 | 両方を同時に扱うarm群(N1〜N6)を同一データで比較 |
| OF-PNPS-S2R-02 | 測定単位・現行TTSでの再測定・「Melos said.」の再現。範囲外事実2点(a)承認再利用 (b)開発runのHR混入 | 採用(再測定+0円の事実確認) | 現行TTS30 segment生成。(a)(b)は事実確認のみ(RESULT_02付録) |
| OF-PNPS-S2R-03 | 語境界の同一子音の縮約(degemination) | Trial arm採用 | N1。負例(語末子音の真の脱落)で検証 |
| OF-PNPS-S2R-04 | 推定受理条件の緩和: (a)子音・強勢母音は厳密、弱化母音は同一視 (b)N-best・2出所以上の支持。拒否条件維持(子音/強勢母音の不一致は拒否、Primary正綴りは根拠にしない、取得根拠と矛盾する推定は捨てる) | Trial arm採用(Production採用はユーザー判断) | N2/N3 |
| OF-PNPS-S2R-05 | ASR側OOVへのG2P適用+アクセント記号正規化。推定側と判定側の両方でG2Pを使う誤りの重なりは負例で検証 | Trial arm採用 | N4 |
| OF-PNPS-S2R-06 | PrimaryがPrimary単独PASS経路で誤発音を正綴りに寄せるProductionリスク | 事実の追加測定のみ(Production変更なし) | 確認済み誤読負例でPrimary正綴り率を記録 |
| OF-PNPS-S2R-07 | ASRが最寄り実在語へ寄せた母音1つ差はNGでなく判定不能 | Trial arm採用 | N5 |
| OF-PNPS-S2R-08 | LLMのofficial自己申告を無視 | 採用(コード+test) | `r2_test_01.py` |
| OF-PNPS-S2R-09 | 負例拡充(7語×4種≥28本)、2エンジン以上の逸脱で誤読確認、確認できないものは除外、0/n でも95%上限を開示 | 採用 | `r2_gen.py` NEG_VARIANTS |
| OF-PNPS-S2R-10 | 代替案評価: (1)TTS側置換は2次案・本巡で実装せず (2)wav2vec2音素CTCは案2として保留 (3)ASR合意条件化は非推奨=不採用 | 採用 | 実装せず。`tts_safe_name_pronunciation_en`の配線状況のみGrep記録 |

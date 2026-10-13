# PATH_INVENTORY_01 英語ASR Production経路の棚卸し(M1/F1適用範囲)

管理ID: ASR-PHONETIC-EQUIVALENCE-M1-F1-PRODUCTION-WIRING-01 委任_02 / 作成: 2026-10-13 / 性質: 設計資料(Production code無変更・費用JPY0)
根拠: 委任_01のコード読取り結果(再利用)+ `er006_preprod_hardening_01_validation.py` L1062-1130 / `er006_secondary_asr_01.py` L296-345,507 / `er011_connected_speech_equivalence_layer_production_01.py` L193-300 の本委任での再確認。

## 結論(要約)
- 全Production経路は `evaluate_attempt_with_cascade[_detail]` と `val.classify_asr_match` を共有する。**F1は `classify_asr_match` が呼ぶ `csv3.classify_connected_speech`(L1076/L1119)1か所の修正で全経路に効く**(個別配線不要)。
- **M1は共有cascadeの `cascade_eligible` early return(`er006_secondary_asr_01.py` L726〜)より前、Primary#1直後**に置けば全経路に効く(減速後は `_post_slowdown_cascade_rescue` が同じdetail関数を呼ぶため自動で効く)。
- 未配線候補(穴)は下表の3点。うち `segment_id` 未渡し2経路はM1/F1を `segment_id` 非依存にすれば解消する。

## 経路表
| # | 経路(呼出点) | 内容 | cascade共有 | M1到達可否(設計案) | F1適用 | 未配線候補/備考 |
|---|---|---|---|---|---|---|
| 1 | `er003_v1_sing01_news_tail_fix.py` L202 | Family Xニュース本文(Std/Adv) | 共有 | 到達(Primary#1直後に挿入) | 自動(classify_asr_match経由) | なし |
| 2 | `er003_v1_sing01_voice01_generate.py` L238 | 音声生成(初回) | 共有 | 到達 | 自動 | なし |
| 3 | `er003_v1_repro01_main_generate.py` L349 | 本編再生成 | 共有 | 到達 | 自動 | なし |
| 4 | `er003_v1_crosslevel_audio_02_common.py` L348 | クロスレベル共通。fallback(`force_secondary=True`)・LR後再検証もここ経由 | 共有 | 到達。fallback救済はSecondary同意必須(OOV_SAFETY/M1設計参照) | 自動 | なし |
| 5 | `er012_b_family_voices_production_01.py` L549 | dialogue(Family Z等) | 共有 | **`segment_id`未渡しでTier3不動(OPEN-322)**。M1は `segment_id` 非依存に設計すれば到達 | 自動 | 穴1: segment_id未渡し(M1側で非依存化、F1は影響なし) |
| 6 | `point_headings_aoede` | 見出し音声 | 共有 | `segment_id`未渡し+Eq Layerフラグ未渡し。M1を `segment_id`/Eq Layerフラグ非依存にすれば到達 | 自動 | 穴2: Eq Layerフラグ未渡し(Eq Layerは別承認範囲のためM1とは独立) |
| 7 | `er003_v1_n3_01_tts_generate.py` L196 | Standard 6%減速後の再検証 | 共有 | 到達(同じdetail関数) | 自動 | なし |
| 8 | 同 L146 `_post_slowdown_cascade_rescue` | 減速後cascade救済 | 共有 | 自動で効く(同じdetail関数) | 自動 | OPEN-328(減速後のEq Layerフラグ)とは別論点 |
| 9 | Key Phrase検証(KP) | KP英語検証 | `classify_connected_speech` を共有 | M1: 対象外(en-US narration/dialogue限定の設計。KPは別承認) | **自動で効く**(関数共有) | 穴3: KPにもF1が効く(意図通りだが影響集計に含める。census対象データにKP実データは含まれず=未集計) |
| 10 | `er006_secondary_asr_01.py` L300-345 Eq Layer(`classify_connected_speech_equivalence`) | Pattern A/B/C UNCLASSIFIEDの後段 | 共有 | M1とは独立(Eq Layerは別承認OPEN-122) | **同種のF1不備を持つ(要点検)**: 最初の食い違い(`existing["diff"]`)のみ見て、corroborationも同一位置のみ(`_word_at_diff_matches_canonical`)。F1_FIX_DESIGN_01の点検表参照 | 候補: 同様の全差分ガード追加はF1是正の範囲内か要判断 |

## F1の波及(関数共有の確認)
`csv3.classify_connected_speech` の呼出元(grep): `er006_preprod_hardening_01_validation.py`(L1076,L1119)、`er011_connected_speech_equivalence_layer_production_01.py`(`classify_connected_speech_equivalence` 冒頭)、`er006_secondary_asr_01.py`(コメント参照のみ)。他は Trial/診断script(Production経路ではない)。よって**修正対象は `er011_b1_connected_speech_validator_01.py::classify_connected_speech` 本体(または呼出側2か所)に絞れる**。

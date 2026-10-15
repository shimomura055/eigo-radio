# FAMILY-C-JA-TTS-PRODUCTION-FIX-01 委任_01 (2026-10-16、委任文保存 T-0)

注記: sandwich-pmから受領した委任文を、見出し構成を保って保存したもの。ユーザー指示原文(B)は逐語。他節は受領内容をそのまま転記(固定ブロックの定型句のみ要約)。

## 管理ID
`FAMILY-C-JA-TTS-PRODUCTION-FIX-01` 委任_01(**read-only調査・是正設計**: Family C日本語Comment/タイトルのTTS言語en固定不具合とreuse_from整合の調査、最小修正案・test・runtime evidence計画)。並行: AUW 委任_08(main merge・Git・SSOT・ACTIVE_TASK担当)、AUW 委任_09(read-only)、DQI 委任_01(read-only)。本委任はコード・SSOT・既存ファイルを一切編集せず、Git操作もしない。新規作成は調査書とRESULT_PACKET_FCJ1.mdと委任文保存のみ。衝突なし。

## 性質/到達上限Status/禁止事項
- 性質: 既存Production不具合の調査・是正設計(ユーザー承認済み=2026-10-16指示B「既存Production不具合の是正承認」)。到達上限Status: `FIX_PLAN_READY`(実装は委任_02以降。Fableが計画を承認、必要ならOpusレビュー後)。
- 禁止: ファイル編集(新規ファイルと委任文保存を除く)、Git操作、有料API実行(API 0)、新Voiceの正式採用提案を「決定」として書くこと(候補と根拠のみ)、AUW仕様との混同。
- Opus独立技術レビューGate(11-3): 本委任は調査のため非該当。実装委任は修正規模により条件A/C候補(計画書に「変更点・影響範囲・後続経路[retry/fallback/regeneration/reuse]」をまとめる)。
- 時間見込み: 60〜90分。並列化: 他3委任と並列(read-only)。
- 費用/日次: 本委任 JPY0 / 改善見込み 高 / 承認区分 C(承認済みscope内)。

## 固定ブロック
E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3(定型。T-2: TTSなし、計画書内の実行コマンドには`TTS_EXECUTION_MODE=STANDARD`を明示。T-3: 費用上限なし[API 0])。T-0保存先: 本ファイル。

## ユーザー指示(原文)
# B. Family C日本語TTSの既存Production不具合是正
**管理ID：FAMILY-C-JA-TTS-PRODUCTION-FIX-01**
**現在Status：既存Production不具合の是正承認**
**到達目標：正式Production経路で日本語音声生成・検証・再利用整合が正常動作すること**
## B-1. 確認済みの不具合
Family CのProduction runner `er013_family_c_production_runner_01.py`で、日本語Comment生成時にも共通のnarrator処理を呼んでおり、その内部でTTSの言語が`"en"`に固定されている。
このため日本語Commentの新規音声生成が失敗した。
また、既存音声のreuse_fromで、原稿変更後にも旧音声が紐づくリスクが確認されている。
**AUWの統一ASRとは別のProduction不具合である。**
## B-2. 是正方針
最初に既存のFamily C正式仕様とProduction経路を確認する。
そのうえで、承認済み仕様の範囲内で必要な修正を実施する。
最低限：
- 日本語Commentを日本語としてTTS生成する。
- 日本語タイトル等、同じ問題が及ぶSectionを調査する。
- 適切な日本語Voice・言語設定・ASR Validatorを使用する。
- 英語Sectionの従来動作を壊さない。
- 日本語の長さ・音声品質・Segment構造を検証する。
- 原稿と音声の対応を保証する。
- reuse_from／metadata／hash等の整合を確認し、変更後の原稿に旧音声が誤って紐づく問題を防ぐ。
- retry／fallback／regenerationとの整合を確認する。
- 必要な実音声をProduction正式経路から生成し、runtime evidenceを取得する。
単なる`"en"`→`"ja"`の置換だけで安全に解決できるなら、過度な改修はしない。
ただし、単一行の修正だけで品質・再利用整合を確認せず完了としない。
## B-3. 自律是正原則
既存仕様に沿った言語設定・配線・metadata等の技術的不具合修正であれば、ユーザーへ再承認を求めず実施する。
新しいVoiceの正式採用、音声品質基準の変更、日本語Commentの内容仕様変更など、新たな仕様判断が必要になった場合のみSTOPする。
不具合がAUW検証中に発見されたことを理由に、AUW仕様と混同しない。
## B-4. 完了条件
- Family C日本語Commentの新規TTS成功
- 必要な日本語Sectionの生成・ASR確認
- 英語Sectionの回帰なし
- 原稿変更時の誤音声再利用なし
- Production実行でruntime evidenceを取得
- Validator／Regression／integration test PASS
- SSOT／Open Item／Git反映
- Dangling Reference Check
- 実成果物が既存Family C仕様を満たすこと
条件未充足ならPRODUCTION_WIREDとしない。

## KPI provenance欄
該当なし(計画書内で、次委任のevidenceを`production_formal_path`(fresh)で取得する計画を記す)。

## Opus台帳更新
該当なし。

## 事前指定Read一覧
- `er013_family_c_production_runner_01.py`: L380-440、L740-760、L800-815、およびGrep `comment`/`ja_`/`title`/`reuse_from`/`resume`/`meta`/`hash` → 該当関数全体。
- `CURRENT_SPEC.md`: Grep `Family C` → Family C仕様節。Grep `Family体系(2026-09-27ユーザー決定` → L1543-1570(本件は2026-10-16にユーザーが明示承認した是正であることを計画書に明記)。
- `OPEN_ITEMS.md`: Grep `OPEN-372 `。
- `er058_output/unified_all_roles_production_wiring_01/RUNTIME_EVIDENCE_06.md`: Grep `cja`/`F4`/`Family C`。`IMPLEMENTATION_06d.md`(存在すれば)。
- JA TTS/ASR既存実装: `er007_ja_secondary_asr_01.py`冒頭、Grep `generate_narration_snippet_verified_strict`、Family X/Zの日本語TTS呼出1例。
- Family Cの既存成果物: `er013_output/**/*.ok.meta.json`代表1件。

## 事前指定Grep一覧+追記位置
- 全repo `*.py`: `er013_family_c_production_runner_01` / `er013_*_test_01.py`の`"en"`/`language`/`reuse_from`。
- 追記位置: 既存ファイルへ追記しない。新規 `er079_output/family_c_ja_tts_production_fix_01/INVESTIGATION_01.md`(`er079`使用済みなら次の空き番号)。

## 実行コマンド全文
- `Get-ChildItem er0*_output -Directory | Sort-Object Name | Select-Object -Last 3`
- `.venv\Scripts\python.exe -m pytest -p no:cacheprovider --collect-only -q er013_family_c_production_runner_01_test_01.py`(存在すれば。実行しない)
- 有料APIは実行しない。実音声evidence用コマンド(次委任用)は計画書に全文で(`TTS_EXECUTION_MODE=STANDARD`明示、`--budget`、STOPセンチネル配置先、見積JPYと根拠)。

## SSOT追記文
本委任ではSSOT編集しない。計画書末尾に次委任用の追記文案(OPEN-372 Status更新文、DECISION_LOG新規節[ユーザー2026-10-16承認・Legacy Family Cへの例外的是正である旨を含む]、CURRENT_SPEC Family C節追記文案)。

## Git
SSOT編集権なし。Git操作なし。新規ファイルは未追跡のまま(commitは後続委任)。

## 報告(RESULT_PACKET項目) -> docs/pm/RESULT_PACKET_FCJ1.md
1 T-0結果・er番号 / 2 不具合の確定(ファイル:行、生成経路図、06d実エラー、同じ問題が及ぶSection全列挙) / 3 Family C正式仕様の照合(逐語、仕様未定義は明示、他Family既存JA値は候補のみ) / 4 reuse_from整合(判定キー、旧音声が紐づく条件、meta非複製の影響、最小是正案、er078_reuse_value_guard_01との関係) / 5 最小修正案(擬似diff、en->ja置換で足りるか、英語非影響、retry/fallback/regeneration/HR Lock/試聴リスト整合) / 6 test計画 / 7 runtime evidence計画 / 8 新仕様判断の要否 / 9 新規発見の独立問題 / 10 費用JPY0・所要時間 / 11 受入記録5項目。

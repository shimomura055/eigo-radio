# FIX_02 — Opus M1/R1〜R5 実装差分・test結果(委任_02)

管理ID: CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_02(2026-10-26)。基準=委任_01のcommit 7ca0df0ad。commit(1)=d00f41c8b。Opus M/R↔実装の対応表は`DESIGN_02.md` §1。

## 1. 差分(Production code)
| ファイル | 変更 |
|---|---|
| `er117_chunk_tts_production_01.py` | (+) `unknown_chunk_ids_in_selection`(R3c)、`legacy_partial_retry_parents`/`apply_legacy_partial_retry`(M1)。(変更) `std_chunk_slowdown_violations`: 減速前後長の欠損を違反`STD_CHUNK_SLOWDOWN_DURATION_RECORD_MISSING`に(R2、従来は素通し)。planner・版・Adv出力は無変更 |
| `er019_family_x_audio_production_runner_01.py` | `generate_family_x_b1_segments`/`generate_family_x_a2_segments`: cache取得直後に`apply_legacy_partial_retry`(M1)、`reconcile_saved_plan`直後に`unknown_chunk_ids_in_selection`の課金前拒否(R3c)。`load_family_x_a2_sources`: 整合検査の直後にchunk単位減速証跡検査(R1) |
| `er121_family_y_audio_01.py` | `_load_y_body_chunks(out_dir, level="b1b")`: `level=="a2"`のときchunk単位減速証跡検査(R1)、`load_y_sources` a2分岐が`"a2"`を渡す。`_record_chunk_decision`: 課金前のplan外chunk id拒否(R3c)。`page_legend_html`: 最終文を`n_chunked`で出し分け(R5) |
| 共有module(`er003_*`・`er020`・`er063`) | **無編集**(`er063`は並行Agentの未commit差分あり=本委任由来0) |
| test | `er121_family_y_structure_match_test_01.py`の許可リストに`chunk_tts.apply_legacy_partial_retry`(Y-NO-LEGACY)と`chunk_tts.ChunkIntegrityError`(Y-DIFF-STOP-TYPE)を追加(理由付き) |

## 2. 新規test(30件)
- `er019_x_std_chunk_opus_test_01.py` 17件: M1 Std 5+Adv 1、R2 3、R3 (a)(b)(c)×2+helper 4、R1 3、R4(a)機械分類 1。**mutation確認**: `apply_legacy_partial_retry`を無効化するとM1のStd/Adv各1件がFAIL(`PYTHONPATH`のscratch scriptで確認)。
- `er121_family_y_std_chunk_opus_test_01.py` 7件: R1×2、R2、R3(c)、R5、Y b1b decision golden×2。
- 不整合な出力を期待値とするtestなし(M1は『本文のTTS 0回・親が上書きされない・共有Gate VALIDATED』、R1は『親の集約値を偽装しても直接呼出でBLOCK』をassert)。

## 3. 回帰(遮断harness下、`PYTHONPATH=netblock_harness_01`、`.venv\Scripts\python.exe run_project_regression.py --pattern …`)
| pattern | 委任_01時点 | 本委任 | 判定 |
|---|---|---|---|
| `er117*_test_*.py` | 106/106 | **106/106 PASS** | 回帰なし(本委任の変更はer117 test追加なし) |
| `er019*_test_*.py` | 578/578 | **595/595 PASS**(+17) | 回帰なし |
| `er121*_test_*.py` | 290 pass+1 skip | **297 pass+1 skip**(+7) | 回帰なし。初回実行で`er121_family_y_structure_match_test_01`の2件FAIL(Xに追加した共通呼出しの追従漏れ検知=許可リスト漏れ)→許可リスト追加後に全PASS(`regression/reg_er121_first_run_2fail.txt`) |
- 接続試行(`NETBLOCK_LOG`): er019は初回135件→私の新規Adv M1 testがPNAP=ON状態で実体表構築を試みていたのが原因と特定(単独実行では0)→testでPNAPを明示OFFにして再実行**129件(委任_01時点と同数、全て`api.openai.com`のgetaddrinfo遮断、既存testの分)**。er117=0、er121=0(ログ未作成=試行0)。新規testの接続試行0。実OpenAI/Geminiへの到達は0。
- 詳細ログ: `regression/`(reg_*.txt, netblock_*.log, done.txt)。

## 4. 確認事項(Grep・既定値)
- 既定値/flag: 新機能に別flagなし(Advと同じ常時有効)。M1/R3(c)はAdvにも効くが正常入力ではno-op。Production到達経路に入る未承認機能なし(Z Stdは本委任で未配線、`er063`未編集)。
- 撤去した旧ルール: なし(本委任は追加・厳格化のみ)。残置: Z向けレベル条件`er117:plan_z_clip`の`level != "b1b"`・`er063:598`は本委任では撤去しない(Z次委任)。**ただし作業中に並行Agent(FZ委任_03)がer117とer063を未commitで編集していることを確認**(`git diff HEAD -- er117_chunk_tts_production_01.py`=`plan_z_clip`のレベル条件撤去・docstring。本委任のcommit(1)には含まれない=私のcommitはその編集より前)。commit(2)ではer117/er063をstageしない。
- Grep: `STD_CHUNK_SLOWDOWN_DURATION_RECORD_MISSING`=er117:358のみ(Production)、`apply_legacy_partial_retry`=er019 2箇所(b1b/a2 generate)+er117定義1、`unknown_chunk_ids_in_selection`=er019 2箇所+er121 1箇所+er117定義1。
- 既存仕様との整合(照合した行): `er117:335-367,554-563`、`er019:940-980,1085-1125,1985-2000,2535-2555`(委任_01時点の行番号。以後ずれあり)、`er121_family_y_audio_01.py:1090-1110,_load_y_body_chunks`、`er121_family_y_structure_01.py:152-183`、`er003_v1_n3_01_assemble.py:270-300,485-500`、`er019_coffee_s3_support_regen_01.py:180-200`(R1: 直接呼出経路は`apply_family_x_a2_gain`ではなく`load_family_x_a2_sources`を通るため、load関数内の検査で網羅される)。

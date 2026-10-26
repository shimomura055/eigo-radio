# FIX_01 — 変更一覧
- `er121_family_y_structure_01.py`: Y_DIALOGUE_VOICE_POOL追加、FIXED_VOICE_SLOTS voice_1=Puck、verify_voice_assignmentをY表で検証、コメント更新。
- `er121_family_y_audio_01.py:13` コメント更新。
- 更新した既存test: `er121_family_y_runner_01_test_01.py`(:231, :534 Algieba→Puck)、`er121_family_y_structure_match_test_01.py`(:239 値、test名 matches_z_formal_table→matches_y_voice_table)。`er121_family_y_audio_chunk_test_01.py:323`はfixture(旧Voice破棄の入力)で変更不要。
- 新規 `er121_family_y_voice_table_test_01.py`(9件: 表完全一致/Algieba除外/Voice1=Puck・2,3不変/Z表不変・Y/Z差分意図/メロスpin/コード行Algieba残存なし/run_01・公開ページ無変更[git status])。
- 回帰: `PYTHONPATH=netblock_harness_01 .venv\Scripts\python.exe run_project_regression.py --pattern "er121*_test_*.py"` → collected=307 passed=306 failed=0 errors=0 skipped=1(skipは既存)、`regression/reg_er121.txt`。新規test単体 9 passed。

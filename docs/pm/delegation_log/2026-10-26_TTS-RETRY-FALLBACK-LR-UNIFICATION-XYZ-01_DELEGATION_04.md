## 管理ID

TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_04(evidence後の残課題是正: (1)JA部位の終端NGでHRQ行が登録されない可能性の確認・是正、(2)BlockProgress `mark_done`のLR block記録上書き是正、(3)`er011`コメント1行の旧記述修正。API 0中心、JA終端の実経路確認が必要な場合のみ≤¥5)。並行Agent: PM-SSOT-SYNC-17(SSOT)。あなたの所有=`er127_tts_block_policy_01.py`(+test)、JA leaf(`er003_v1_n3_01_tts_generate.py`の`generate_a2_japanese_with_fallback`終端部のみ)、`er011_human_review_lock_01.py`(コメント1行のみ)、`docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/{FOLLOWUP_01.md}`+evidence追記、`docs/pm/delegation_log/2026-10-26_TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01_DELEGATION_04.md`(+check.json)、`docs/pm/RESULT_PACKET_TRU4.md`。SSOT編集権なし。pathspec付きcommit。

## 性質/禁止

- 性質: 承認済み仕様(終端NG1件=HRQ1行、U-04)の実装漏れ確認・是正(B)。到達上限=FIXED+確認済み。
- 禁止: 回数・待機・Style・Gateの変更、Production hook/env追加、禁止Git操作。
- 費用: 上限¥5(Guardrail、T-3定型どおり)。JA終端の実経路確認はmock/偽generatorを優先し、実TTSが必要な場合のみ1 segment。
- 時間見込み: 約1.5h。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

従来どおり。T-0: 委任文保存+check、結果1行。T-2: 実TTS時は`TTS_EXECUTION_MODE=STANDARD`明示。T-3: 上記。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01_DELEGATION_04.md` をN=693から順に試し、先頭「## 管理ID」+「TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_04」のものを採用。

## 事前指定Read一覧

- `docs/pm/RESULT_PACKET_TRU3.md`(6)不具合・新規OPEN(2)(3)、`EVIDENCE_X_01.md` X-Std-7、`EVIDENCE_Z_01.md` Z-Adv-3
- `er127_tts_block_policy_01.py`: Grep `register_terminal_hr|mark_done|BlockProgress|blocks\[` ±20
- `er003_v1_n3_01_tts_generate.py`: Grep `generate_a2_japanese_with_fallback|STOPPED|register_terminal_hr|_post_slowdown_unified_judge|slot` ±20
- `er006*`HRQ書込(Grep `human_review_queue|append_hrq`)、`er011_human_review_lock_01.py` Grep `総4|4回目以降` → コメント行

## 実施事項

1. **JA終端HRQ**: JA leafで、判定器(unified judge)を経由しない終端NG(技術失敗を除く品質NG)が存在するかをコードで確定。存在すれば`register_terminal_hr`を終端に追加(「終端NG1件=HRQ1行」、重複登録防止)。存在しなければ「判定器経由で必ず1行」であることをtestで固定し、X-Std-7/Z-Adv-3のHRQ 0行がdriverの判定注入(判定器のslot書込を迂回)によるものだったことを記録。mock testで終端NG→HRQ 1行・Lock・STOPPEDを確認。
2. **BlockProgress**: `mark_done`で再読込+blocks merge(depth 0がdepth 1記録を消さない)。test: depth 0/1混在→両方残る、resume判定不変。
3. **er011コメント**: 旧「総4/4回目以降」記述を現行(統一: LRあり最大6、KP 4)へ1行修正(コード変更なし)。
4. 回帰: er127 test全件、er003 JA関連、er011。接続0。

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-26_TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01_DELEGATION_04.md --json-out ...\_check.json`
- 回帰: `.venv\Scripts\python.exe run_project_regression.py --pattern "er127*_test_*.py"`、`--pattern "er003*_test_*.py"`、`--pattern "er011*_test_*.py"`
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## Git

- commit message: `TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_04: JA終端HRQ登録の確認/是正+BlockProgress mark_done merge+er011コメント修正(test、API 0)`。trailer: `Delegation: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/04`。push `git push origin HEAD:main`。

## 報告

`docs/pm/RESULT_PACKET_TRU4.md`: (0)T-0、(1)JA終端の事実と是正、(2)BlockProgress是正、(3)er011、(4)test・回帰、(5)必須4行+「判定整合: 重大NG=<なし|あり>」、(6)SSOT文案(OPEN-540限定解除文案)、commit hash・raw URL。末尾5行要約。
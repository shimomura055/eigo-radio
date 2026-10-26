## 管理ID

FAMILY-Y-STYLE-PROFILE-FIX-01 委任_04(Std `y_voice_1`の再生成[Fable権限でapprove_regenerate]+`_03`のStd HR試聴節更新+take採用toolの`run_style_fix_01`対応版の準備。有料: 見積≤¥10)。並行Agent: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_02(`er127_*`・leaf、Y runner call siteは保留中の取り決め)。所有=`er121_output/family_y_production_01/redelivery_fee/run_style_fix_01/**`(本委任で書込可: approve_regenerateと再生成のみ)、`user_test/family_y_production_redelivery_fee_03/**`、`docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/{REGEN_RESULT_02,HR_REQUEST_STD_02,COST_02}.md`、`docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/tools/{build_page_03.py,hr_adopt_style_fix_01.py}`、`docs/pm/delegation_log/2026-10-26_FAMILY-Y-STYLE-PROFILE-FIX-01_DELEGATION_04.md`(+check.json)、`docs/pm/RESULT_PACKET_YSP4.md`。`er121_*.py`/`er011_*`/`er003_*`は編集禁止(toolは`docs/research/.../tools/`配下に置き、既存関数を呼ぶ)。SSOT編集権なし。pathspec付きcommit。

## 性質/到達上限Status/禁止事項

- 性質: 承認済み運用内の再生成(HR Lock中segmentの`approve_regenerate`=Fable権限、理由=両ASR[OpenAI/Azure]が`who was not home`を`who is not home`と転写し、1語の読み違いの疑いが高い。読み違いの疑いがあるtakeをユーザーに承認させない)。到達上限=「Std y_voice_1 新take取得・HR承認待ち(ユーザー)」。
- 禁止: 人間承認の代行(takeの採用はユーザー指定後の委任_05)、Gate/QA条件の変更、preview(`思いどおり`表記ゆれのみ)の再生成(無益)、Adv側の変更、旧`_01`/`_02`改変、禁止Git操作。
- 費用: 上限¥10(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- 費用/日次: 当日既使用約JPY594/本委任見積JPY5〜8(y_voice_1 TTS 2〜3 take+ASR)/改善見込み中(`was`の読み違いは確率的。ハイフン表記ゆれは再発するためHR承認は依然必要)/承認区分: C。
- 時間見込み: 約1h。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1/D-1/G-1/F-1: 従来どおり。T-0: 委任文保存+`check_delegation_prompt.py`実行、結果をRESULT_PACKETへ1行(FAILでも継続)。T-2: TTSを伴うため`TTS_EXECUTION_MODE=STANDARD`を環境変数とCLI引数で明示。T-2追記4点: (1)差分再生成=`--only-segments y_voice_1 --stage tts_a2 --regenerate-stage tts_a2`相当で可能か`--help`で確認、(2)cache=HR Lock中のため再利用なし、(3)`--approved-budget-jpy 10`、(4)全再生成と判明したらAPI前にSTOP。T-3: 上記定型文どおり。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_FAMILY-Y-STYLE-PROFILE-FIX-01_DELEGATION_04.md` をN=684から順に試し、先頭「## 管理ID」+「FAMILY-Y-STYLE-PROFILE-FIX-01 委任_04」のものを採用。

## 事前指定Read一覧

- `docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/{HR_REQUEST_STD_01,REGEN_RESULT_01,BUILD_03}.md`、`tools/build_page_03.py`
- `er011_human_review_lock_01.py`: Grep `approve_regenerate|def approve|regenerate_approval|consuming_regenerate_approval` → ±15(Lock解除の正式手順とrecord形式)
- `er121_e1_hr_adopt_r0_01.py` 全体(run_01固定の採用手続き先例: 減速・減速後ASR再検証・Style記録反映・`record_human_approval`/`record_y_human_approval`)
- `er121_family_y_audio_01.py`: Grep `record_y_human_approval|stamp_requested_voice|y_binding` → ±10(読み取りのみ)
- `run_style_fix_01/a2/audit/`のASR結果(y_voice_1 take1〜3の転写全文)、`a2/narration/attempts/`

## 事前指定Grep一覧+追記位置・更新位置の手順

- `py tools/stop_scope_check_01.py --managed-id FAMILY-Y-STYLE-PROFILE-FIX-01 --run-dir er121_output/family_y_production_01/redelivery_fee/run_style_fix_01 --out docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/stop_check_04.json` を有料run前に実行。
- 起動間隔150秒以上、同一run 5分3回禁止。

## 実施事項

1. **読み違いの事実確認**: y_voice_1 take1/take2/take3のASR転写(OpenAI/Azure両方)で`who was not home`の該当箇所を抜き出し、`is`/`was`を表にする(take3も確認)。両エンジンとも`is`なら読み違い濃厚と記録。
2. **approve_regenerate(Fable権限)**: `er011`の正式手順で`y_voice_1`(a2)のLockに再生成承認を記録(reason=「Fable許可: 両ASRで was→is の読み違い疑い。読み違い疑いのtakeを人間承認に回さない。2026-10-26 FAMILY-Y-STYLE-PROFILE-FIX-01 委任_04」)。previewには適用しない。
3. **再生成(1起動)**: `.venv\Scripts\python.exe er121_family_y_runner_01.py --mode real --slug redelivery_fee --run run_style_fix_01 --theme-package <run_01と同じ> --stage tts_a2 --only-segments y_voice_1 --regenerate-stage tts_a2 --approved-budget-jpy 10 --tts-execution-mode STANDARD`(実値は`--help`で確認し全文記録)。期待: 標準2回+fallback1回。各takeの転写で`was`の有無とハイフンNGを記録。全take再びHR Lock(ハイフン)は想定内。
4. **`_03`のStd HR試聴節を更新**(`build_page_03.py`): y_voice_1の新take(旧take1〜3は「読み違い疑い・非推奨」ラベルで残す)、各takeの転写(`was/is`強調)、previewのtake1/2は据置。`HR_REQUEST_STD_02.md`に推奨take(`was`が正しく読まれ、承認Styleのtake)を明記。
5. **採用tool準備(実行はしない)**: `tools/hr_adopt_style_fix_01.py --level a2 --segment y_voice_1 --take N`/`--segment preview --take M`。先例`er121_e1_hr_adopt_r0_01.py`を`run_style_fix_01`+take指定対応に一般化(6%減速+減速後ASR再検証[y_voice_1のみ]、`record_y_human_approval`[y_binding付き]、採用attemptのStyle記録をtop-level entryへ反映、Lock RESOLVED)。dry-run(`--dry-run`、API 0)で手順と対象ファイルを出力できること。
6. `COST_02.md`: raw_usage_log実績。`REGEN_RESULT_02.md`: 結果。

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-26_FAMILY-Y-STYLE-PROFILE-FIX-01_DELEGATION_04.md --json-out docs\pm\delegation_log\2026-10-26_FAMILY-Y-STYLE-PROFILE-FIX-01_DELEGATION_04.md_check.json`
- stop_scope_check(上記)、正式CLI(上記)
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## Git

- add対象: `user_test/family_y_production_redelivery_fee_03/`、`docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/{REGEN_RESULT_02,HR_REQUEST_STD_02,COST_02}.md`・`tools/`、delegation_log(wav/raw_usage_log/lock不追跡)。pathspec付きcommit。
- commit message: `FAMILY-Y-STYLE-PROFILE-FIX-01 委任_04: Std y_voice_1 再生成(Fable許可approve_regenerate、was→is読み違い疑い、実費¥X)+_03 HR試聴節更新+take採用tool準備(dry-run)`
- trailer: `Delegation: FAMILY-Y-STYLE-PROFILE-FIX-01/04`
- push: `git push origin HEAD:main`。

## 報告

`docs/pm/RESULT_PACKET_YSP4.md`: (0)T-0、(1)読み違いの事実表、(2)approve_regenerate記録、(3)再生成結果(take別転写・NG理由・推奨take)、(4)`_03`更新と検査(HTTP 200)、(5)採用toolのdry-run出力要約、(6)費用実績、(7)必須4行+「判定整合: 重大NG=<なし|あり>」、(8)commit hash・raw URL。末尾5行要約。
# F1_FIX_EVIDENCE_01 — KP外側retryの同一句反復の明示除外(OPEN-456 F1、KP-OUTER-RETRY-SAME-PHRASE-FIX-01)

Fable決定: 承認済み仕様の範囲内の不具合修正(Prompt 2本文・選定基準・件数・レベル基準は不変。機械診断noteの内容強化のみ)。

## 変更
- `er003_v1_n3_01_scaffold_generate.py` `run_kp_with_outer_retry`: canonicalization INVALID(項目別理由の句)/CMU post-canon NGの選定句(display_phrase)を理由付きで`excluded`へ累積。次周は(a)note末尾へ「次の語句は…不適合と確定しています(理由付き)」を後置、(b)`excluded_phrases`をer105 gateへ渡す。除外句が再び選ばれたらcanonicalization(Luna)呼出前に不適合化(gate内=再選定、select_fnがgateを通らない場合は外側guardで選定失敗扱い)。`outer_retry_log.json`に`excluded_phrases`(全周累積)・各周`excluded_phrases_in/added/reselected`。
- `er105_kp_fulltext_selector_01.py`: `phrase_key`/`build_exclusion_note`/`apply_exclusions`追加、`build_machine_note`をattempt間累積に(gate内retryでも以前のattemptの不適合句を併記)、`run_selection_gate/run_fulltext_selection`に`excluded_phrases`。最終attemptで除外句を落として1件以上残れば数合わせせずshortfall確定、残らなければ不適合のまま(外側retryの通算3回→`OUTER_RETRY_EXHAUSTED`、fail-closed)。`keywords_runtime_metadata.json`に`outer_excluded_phrases`と各attemptの`exclusion_hits/exclusion_dropped`。
- A/B/C: `strategy_l`に`excluded_phrases`を渡すとValueError。`_run_key_phrases_impl`は`run_kp_with_outer_retry`非経由・除外コード無し(testで検査)。Prompt 2 sha256 `a12896f4…3dc9a`不変、`prompt_prefix_intact` assert維持。

## test
新規`er003_test_kp_outer_retry_exclusion_01.py` 10件PASS(同一句反復の2周目除外+別句PASS/Prompt本文不変/全候補除外のfail-closed[canon呼出は1周目のみ]/最終attemptでのshortfall確定/外側guard/正規化一致/累積note/A-B-C無影響)。関連群(er105・er003_test_kp*・er062*・er019_family_x_kp*・er108*)342件OK。注: `run_project_regression.py`は単一glob専用で`|`区切りpatternは0件収集になるため、同じ対象ファイルを`unittest`で直接実行した。

## runtime evidence(X small_bag a2のKP段、新run dir `er019_output/family_x_audio_production_wiring_01/small_bag__run_f1fix_01`)
STOP確認rc=0(`f1fix_01/stop_check.json`)、`TTS_EXECUTION_MODE=STANDARD`、`--stage scaffold --scaffold-only kp --level a2 --slug small_bag --run run_jre_src`(kpq_02のsupport成果物を複製、key_phrases未複製、raw_usage_log空から開始)。
- 周1: 選定[`having a big moment`/`Catch the Eye`/`Carry the Load`]→canonicalization INVALID(有限助動詞)→`having a big moment`を理由付きで除外(`outer_retry_log.json` `excluded_phrases`)。
- 周2: noteに「「having a big moment」: 有限助動詞が含まれている」を後置(`f1fix_01/keywords_selector_prompt_attempt2.txt`末尾、note_sha a17602c9)。選定attempt1=[`minaudières`/carry the load/on the throne]→CMU未登録でM1再選定、attempt2=[carry the load/on the throne/spread through the whole market]で選定PASS→CANONICALIZATION_PASS→Redundancy PASS。最終KP=`Carry the Load`/`on the throne`/`spread through the whole market`(以前の2回は`having a big moment`が3周反復して`OUTER_RETRY_EXHAUSTED`)。
- 除外句の再選択(exclusion_hits)は今回の実走では発火せず(note後置だけで`having a big moment`は再選択されなかった)。再選択時の事前弾きはtestで確認。
- 費用: runner出力`[cost] so far=0.95 JPY`(openai、`small_bag__run_f1fix_01/raw_usage_log.jsonl` 8行)。案件上限10円内。
- 保存: `f1fix_01/{outer_retry_log.json,keywords_runtime_metadata.json,keywords_selector_prompt_attempt2.txt,scaffold_kp.log,stop_check.json}`。

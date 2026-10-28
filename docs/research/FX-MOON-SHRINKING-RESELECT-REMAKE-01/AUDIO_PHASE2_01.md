# AUDIO_PHASE2_01 (FX-MOON-SHRINKING-RESELECT-REMAKE-01 委任_02、2026-10-28)
run=`er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01`(source=run_reselect_01、本文正本run_ms_03と同sha)。実行はすべて`--slug moon_shrinking --run run_reselect_01`、Python=.venv。

## 結果
- **Advanced(b1b): 完成**(scaffold残り[Part1/文法finalize]→tts→assemble→player→ページ)。長さ314.03秒、assemble OK(clipping無し peak 0.953)、M3 Style Gate PASS(16 segment、blocked 0・warning 0)、ASR: 警告1件(kp2「porous」=PASS_WITH_WARNING `vote_2of3:secondary+whisper`、Azure「Porous.」一致=SECONDARY_CONFIRMED)、Human Review残0。LR/Fallback発動0(赤/濃青表示なし、正しい)。⏸は実Chunk境界(Full Story Part1〜3の3段落chunk)に表示。ページ=`user_test/family_x_moon_shrinking_reselect_01/index.html`(**現状Advancedのみ**。Std完成後に両level版で再生成して上書き)。
- **Standard(a2)**: Fable確定連絡(rev2、①2件)後にscaffold残り→tts実行済み(音声19 segment+KP等、ASR全PASS系)。**assemble段のM3 Gateで停止 = BLOCKED_STYLE_PROFILE_GATE**(kp1_english「shoving match」/kp2_english「hold heat in」が`ASR_RECORD_MISSING`)。ページ未生成。
## Std停止の原因(仮説→反証→再現)
- 観測: `a2/audit/style_profile_gate.json` blocked=kp1_english,kp2_english / reason ASR_RECORD_MISSING。当該2件はMaster Audio Storeの再利用(`key_phrases/{1,2}/english.reused=true`、`asr_verified=true`、`asr_judgement_inherited.state=PASS`)。
- 原因: `er130_adopted_take_classifier_01.py:221 adopted_asr_state`が`entry.asr_judgement`しか見ない。再利用時は`er019 runner:1124 _mark_asr_judgement_inherited`が`asr_judgement`→`asr_judgement_inherited`へ改名するため、store_reuse takeは常に(None,None)→`:398 ASR_RECORD_MISSING`。今日の委任_11統合配線(commit 4475cebf8、m3_assembly_gateが全clipで分類核を呼ぶ)で顕在化した回帰(旧M3 Gateは再利用entryを許容)。
- 再現/検証(API 0、ファイル非編集のmonkeypatch): `adopted_asr_state`がstore_reuseで`asr_judgement_inherited.state`を返すよう差し替えると`m3_assembly_gate("fx_20261017","a2",…,level_dir=a2)`=PASS(blocked 0)。ledger上kp1_en/kp2_enは`source=store_reuse, kind=NORMAL`。
- 修正案(6行程度、`er130`の`adopted_asr_state`末尾に: `aj=entry.get("asr_judgement_inherited")`があり`state`を持つ場合に限り`(state,"asr_judgement_inherited")`を返す。再利用clipのみ該当)。**er130は別worker(委任_15 B10)が未commit編集中のため、衝突回避で本worker編集せず**。修正後は`--level a2 --stage assemble`→`--level both --stage player`→`er019_family_x_listening_page_01.py --slug moon_shrinking --run-name run_reselect_01 --web user_test/family_x_moon_shrinking_reselect_01`(TTS再実行なし、API 0)。
## 検査(Adv)
- 確定①way off/②porous/③culprit(文法=疑似分裂文)・②over its entire history/puzzling がページに出現(grep 3/2/3/2/2件)。confirmed_selection rev1と整合。本文=変更なし(source sha一致)。公開`user_test/family_x_moon_shrinking_02`はgit差分0(不変)。
- 注: 11:03頃、別workerのgit stash/popでrun直下`entry_point.json`が一時的に旧内容(levels=[b1b],stage=assemble)へ戻った。a2側のKP/文法confirmed・tts_block_progress・results・raw_usage_logは健在(確認済み)、a2 TTSプロセスは継続し正常完了、assemble/playerは各段で再書込み。実害なし。
## 費用
累計(Phase1含む)¥20.78(openai 6.93/gemini 0.96/gemini_batch 7.15/openai_asr 3.84/azure 1.90)。本委任分≒¥15.5。Cap¥60内。

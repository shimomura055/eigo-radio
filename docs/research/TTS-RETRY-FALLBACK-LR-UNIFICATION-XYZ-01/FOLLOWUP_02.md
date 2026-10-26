# FOLLOWUP_02 (委任_06: JA終端HRQ二重登録の是正)

## 根本原因
(a) JA判定器(`er007_ja_secondary_asr_01._log_human_review`)は最終slotで**JA queue**(`HUMAN_REVIEW_LOG_PATH_JA`=er007_output/ja_asr_cascade_01/human_review_queue.jsonl)へ書く。disfluency/repetition単独NG・cascade打切り等では判定器は行を書かない。
(b) `register_terminal_hr`はEN用の`er006_secondary_asr_01._log_human_review`固定で、重複抑止(`is_duplicate_queue_entry(queue_path, wav_path, canonical_text)`)は**書込先queueファイル単位**。委任_04はJA終端をこのEN版へ流したため、JA queueの判定器行を検知できず、EN queueに2行目を作った(JA_01実測 HRQ 2行)。
(c) 単体testはfakeが判定器行もEN queue(同一ファイル)へ書いており、queueの分離を再現していなかったため見逃した(再発防止: fakeにJA queue別ファイルを導入)。
重複抑止キー=(wav_path, canonical_textのhash)で両queue共通。足りなかったのは書込先の一致のみ。

## 修正(案A)
- `er127_tts_block_policy_01.py`: `register_terminal_hr(..., log_fn=None)`(None=従来のEN版。英語部位の挙動不変)。`register_ja_terminal_hr`は`er007_ja_secondary_asr_01._log_human_review`を`log_fn`で渡す=判定器と同一queue・同一dedupe。`er006/er007`は無編集、`er003_*`の呼出も無変更。
- test基盤: `er127_test_fakes_01.py`にJA queue(`hr_path_ja`、`HUMAN_REVIEW_LOG_PATH_JA`をpatch)と`hr_rows_ja()`を追加。JA判定器fakeはJA queueへ書く。`er127_test_golden_01.py`のhr_rowsはEN+JAの合算(golden内容不変)。

## test
- (i)判定器が書いた終端 -> JA queue 1行・EN 0行(`test_ja_terminal_ng_with_judge_row_is_not_duplicated`)。(ii)判定器が書かない終端 -> JA queue 1行(`..._without_judge_row_...`)。(iii)EN queueへJA行なし(上記+`test_ja_third_after_180s`/`test_lr_not_for_ja_kp_and_dialogue`でJA=JA queue/EN=EN queueのみ)。(iv)英語部位の既存test不変。
- 負の対照: `log_fn`をNone(EN版)へ戻すと8 subTest FAIL(JA二重/EN混入を検出)を確認し復元。
- 回帰: er127 102/102、er003 1910 pass(skip1、failed0)、er011 292/292、er007 111/111、er006 75/75。
## evidence
`EVIDENCE_JA_TERMINAL_02.md`(JA_02: hrq_rows==1、JA queueのみ、EN 0、費用¥0.585)。

# FOLLOWUP_01 (委任_04: evidence後の残課題是正)

## 1. JA終端HRQ(U-04)
- 事実: `generate_a2_japanese_with_fallback`(L7)の終端(STOPPED / ASR_VALIDATION_UNCERTAIN)に`register_terminal_hr`呼出が無かった。HRQ行は判定器(`ja_secondary.evaluate_attempt_ja_with_cascade`、er007:778の`human_review_required`)が最終slotで書く経路のみ。
- 判定器を経由しない/行が出ない終端NG(品質NG)は存在しうる: disfluency/repetition単独NG・NO_NG_SPAN相当・cascade打切り(stop_retrying)でjudgeが`human_review_required`を立てない形。LR対象外(JA_STD lr=False)なのでLR経由の登録も無い。
- X-Std-7のHRQ 0行は、driverが判定戻り値のNGを注入し判定器自身のslot書込を迂回したため(上記の欠落と別の理由。ただし欠落の可能性自体は実在)。
- 是正: `er127.register_ja_terminal_hr`を追加し、JA終端(STOPPED / UNCERTAIN)で呼ぶ。最後のattemptがASR判定済み(status=OK)かつ不合格のときだけ`er127.register_terminal_hr`(技術STOP・TTS技術失敗は登録しない、重複はwav_path+canonical_textで抑止)。統一ブロック外(_blk=None)・depth>=1は登録しない。回数・待機・Style・Gateは不変。
- 同じ欠落が`generate_charon_japanese`(er003_v1_sing01_voice01_generate.py, L7b)にもあったため、共通helper `er127.register_ja_terminal_hr`を新設し両JA leafの3終端(標準stop_retrying/fallback stop_retrying/STOPPED)で呼ぶ。test: L7a/L7bの両方でfix無効化時にFAIL(負の対照確認)。

## 2. BlockProgress.mark_done
depth0の`mark_done`は自分のin-memory stateを書くため、別BlockProgress(depth1=LR block)が同fileへ書いたblocks["1"]を上書きで消していた。書込直前に再読込しblocks(n_started=max、attemptsはsetdefault、cooldown、lr)をmergeする。status/final_statusは従来どおりDONE。resume判定(key・IN_PROGRESS・期限・REGENERATE_APPROVED・verified済み)は不変。

## 3. er011コメント
literalな「総4/4回目以降」は現行ファイルに無い(G-9相当の旧記述はer011_tts_retry_selection_effect_reanalysis_01.py等の履歴分析側)。`PRODUCTION_MAX_TTS_ATTEMPTS`直前に現行(1ブロック3回+180秒、LRあり最大6、KP4、正本er127)の1行を追記(コード変更なし)。

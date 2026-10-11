# FIX_DESIGN_01(ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_04A、2026-10-12、Opusレビュー対象)

範囲: ユーザー承認(2026-10-12)の既存Production不具合3件の是正のみ。統一仕様(Secondary常時実行・minimal fallback撤去・LR拡張・C1廃止)は先行実装しない。branch `fix/asr-tts-prodfix-01`(mainへ未merge)。

## 1. OPEN-270 TTS生成回数の上限違反
- 問題: `generate_a2_segment_with_slowdown`の外側ループ(既定3周)が、6%減速後の再検証NGのたびに内側`generate_english_segment_with_fallback`へ満額予算(標準2+minimal1)を再付与。最大9回生成し得、CURRENT_SPEC「4回目以降は絶対にTTS生成しない」(`PRODUCTION_MAX_TTS_ATTEMPTS=3`)に違反(Coffee part2で5回)。
- 変更: 外側ループに生成回数の共有カウンタ(`generations_used`、上限=`PRODUCTION_MAX_TTS_ATTEMPTS`)を追加。内側呼び出しには残予算を`max_attempts`(標準は`min(2, 残)`)として渡し、内側が消費した回数(`count_tts_generations_in_result`=standard+fallbackのattempts_log長、最低1)を累計。残0なら取り直さずSTOPPED(既存STOPPED/Human Review経路)。減速後検証自体(OPEN-76)・外側ループの周回上限3・減速後の別ASR経路(Primaryのみ)は無変更。
- 改善: segment単位で生成総数<=3が構造的に保証される(runtime: 旧6回→新3回)。
- リスク: (a)旧設計コメント(`er011_human_review_lock_01.check_before_generation`のRESOLVED節)は「内側を最大3回取り直す正当なretry」を前提にしており、取り直し余地が縮む(CS L1692の遵守なのでユーザー承認済み是正の範囲)。(b)Local Rewrite回復経路の再TTSはattempts_log外のため生成数に数えない(従来から標準/fallbackの予算外、本是正では不変・統一設計側で扱う)。(c)残予算1での標準1回のみになるとfallbackが発火しない(予算内の厳守を優先)。

## 2. OPEN-271/275 Azure STT費用の集計漏れ
- 問題: 費用集計が`provider in (gemini/openai/openai_asr)`のtoken単価のみで、Azure(音声時間課金)は0円計上。11ファイルに複製、Budget Guardも同関数でAzureを数えず。
- 変更: 共通`er005_cost_logger.azure_stt_cost_usd(rec, price)`を1箇所追加(送信音声秒/3600 x pricing_snapshot登録単価[azure/audio_hour=$1]、単価未登録はRuntimeErrorでfail-closed)。11ファイルは各集計の分岐1箇所を`if provider == "azure": usd = cl.azure_stt_cost_usd(rec, price)`に寄せた(既存のtoken計算・try/except・cost_usd優先は無変更、新実装の複製なし)。Budget Guard(`assert_budget_ok`)は同じ`compute_cost_jpy_so_far`を参照するため自動的に反映。
- 改善: Azureが集計・Budget Guardに入る(実測: 13.611秒→0.605円、旧集計は同ログで0.0円)。Coffee Phase 2累計の補正値約31.03/50円はOPEN-275としてSSOT(OPEN_ITEMS/DECISION_LOG)へ反映が必要(merge後委任)。
- リスク: Azure契約tier(F0無料枠/S0)は**未確認**で、本値は登録単価での試算(実請求額の確認はユーザー)。過去runの費用報告の過少計上は遡及していない。新たにBudget Guardが止まるrunが出る可能性(意図どおり)。音声秒未記録のレコードは0円扱い。

## 3. 記録欠落(append-only)
- (a)減速後再検証の転写: `slowdown_attempts_log`各周に`post_slowdown_asr_text`・累計生成数を追加し、周ごとに既存`attempt_history.jsonl`へ`A2_SLOWDOWN_REVERIFY`を追記。
- (b)queue重複排除での転写消失: `_log_human_review`(EN/JA)は重複時に従来はreturnのみだった。queue表示(1行)の抑止はそのままに、steps(Primary/Secondary転写全文)を`attempt_history.jsonl`へ`HUMAN_REVIEW_QUEUE_DUPLICATE_SUPPRESSED`として追記。
- (c)`tts_generation_results.json`の再実行上書き: 上書き直前(n3 B1/A2、er019 B1/A2の計4箇所)に`archive_prior_tts_results`が既存ファイルの各attempts_log/slowdown_attempts_log/statusを`attempt_history.jsonl`へ追記(ファイル形式・正本の上書き挙動は不変)。
- (d)固定ラベル(OPEN-277): `generate_english_component_minimal_instruction`の固定文字列を、実際に使った指示の出所(`MINIMAL_INSTRUCTION_PREFIX`/`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`/+pronunciation_hints)と長さに置換し、`instruction_label`・`style_prefix`(len/sha256/先頭200字)を追加。標準経路にも`style_prefix`・`cascade_steps`(Primary/Secondary転写全文)を追加し、fallbackattemptは`_run_a2_minimal_fallback_attempt`が`detail_out`を渡して`cascade_steps`を保持。`record_outcome`が`attempts_detail`(attempt単位の転写/判定/Style/cascade steps)を`attempt_history.jsonl`へ追記。
- 改善: Primary/Secondary転写・実送信Style・attempt番号が全て追記専用の既存`attempt_history.jsonl`に残る(runtime確認済み)。
- リスク: (i)attempt_history.jsonlの1行が大きくなる(試算: 1 segmentで約2KB→標準+fallbackで約3KB)。(ii)`attempts_log`/結果dictへキー追加(additive)のため、厳密dict比較をするtestがあれば影響(関連suite全件で新規failure 0を確認)。(iii)`er012_b_family_voices_production_01`・`er012_editorial_b_voices_trial_09_audio`の別関数に同じ固定ラベルが残る(OPEN-277の別箇所、本是正では未変更)。(iv)ja側のStyle/Secondary(SCG)転写は本是正の対象外(英語経路中心、JAのqueue重複のみ対応)。

## 既存承認仕様との衝突
STOPなし。ただし1.の旧設計コメント(減速後NG時に内側を満額で再実行)は、CS L1692(総3回上限)と矛盾していたもの。CS L1692側を遵守する方向で統一(ユーザー承認2026-10-12)。

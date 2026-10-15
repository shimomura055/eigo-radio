# Guardrail(JPY16)到達の記録(T-3)
- bnarr(1回目・唯一の実行)の実費 JPY 16.1253(usage_log.jsonl token実測)。Guardrail JPY16を0.13超過。
- 原因(把握済み): (1)委任文の単価前提(1clip約1.4〜1.6)に対し、Family B A2 narrator/Voice A/Bは gemini-2.5-pro-preview-tts で、長い本文ほど音声出力token数が多く(point_one 1.82 JPY・point_two 1回目 4.62 JPY・同2回目 4.65 JPY)、Voice A/B本文(retry込み)で約11.7 JPY(TTS合計12.47+Azure 2.69+ASR 0.96)。(2)point_two 1回目は標準経路のTRUE_CONTENT_MISMATCH→Secondary(Azure 56秒 約2.5 JPY)→NG_BOTH→2回目PASS(正当な標準retry)。異常retryではない。
- bnarr終了理由: parts.json(E-family)に tension_body が無く run_tts_a2_2v_new_topic が `parts["tension_body"]` で KeyError(Hook/Tension/Closingを生成する前)。再起動は委任文の禁止事項(有料runの再起動)に従い実施せず(s6記録)。
- 残りpart(xkp_miss・ja_fresh)は承認済みscope内・原因把握済み・残作業明確・便益明らかのため、T-3に従い累計Guardrailを26.0へ引き上げて継続(想定追加 xkp 約1.5、ja_fresh 約3〜9)。

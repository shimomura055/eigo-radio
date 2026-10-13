# F1_RUNTIME_EVIDENCE_02 (委任_02、2026-10-13)

**F1のruntime evidence(新規TTS生成物のASRログ上の`connected_speech_info.f1_version`記録・判定)は今回取得できていない**(Std KP canonicalizationがINVALIDでSTOPしたため、有料TTS runを実行していない。TTS費用JPY0)。
F1=`WIRED_PENDING_RUNTIME_EVIDENCE`のまま(判定はFable)。

代わりに取得できたoffline証跡(OF-X6): 引継ぎ対象の保存済み`asr_text`を現行(F1後)判定関数`classify_asr_match`で再判定した結果。判定器version=`F1-2026-10-13`(`er011_b1_connected_speech_validator_01.F1_VERSION`)。
これは「新規生成」ではなく「過去の検証結果を現行判定器で再判定」であり、F1のruntime発火の代替ではない。

| level | segment | 同一性証拠 | F1再判定対象 | 再判定classification | f1_version | 元style_version | cross_version受入記録 | asr_text |
|---|---|---|---|---|---|---|---|---|
| a2 | preview | entry_sha256 | False | None | None | v3_j3_kp_meaning_and_explanati | - | コーヒーの値段を伝える数字は、何をいつ測ったものなのでしょうか。 数字が示す内容を確かめながら、ニュースの数字を身近なコ |
| a2 | comment_1 | entry_sha256 | False | None | None | v3_j3_kp_meaning_and_explanati | - | コーヒーの価格を示す数字がどう変わり、豆の供給がどう関係しているのかに注目してください。 |
| a2 | comment_2 | entry_sha256 | False | None | None | v3_j3_kp_meaning_and_explanati | - | コーヒー豆の市場価格は下がりましたが、お店の値札はすぐには変わらないようです。 では、豆の価格が変わってから、お店の値段 |
| a2 | comment_3 | entry_sha256 | False | None | None | v3_j3_kp_meaning_and_explanati | - | ここまで、コーヒー豆の価格が下がっても、店の価格がすぐに変わるとは限らないことを見てきました。 これからは、豆の価格の変 |
| a2 | comment_4 | entry_sha256 | False | None | None | v3_j3_kp_meaning_and_explanati | - | コーヒー豆の相場が動いても、店の値札にすぐ現れるとは限りません。カフェの値段には、豆以外の費用もかかわっています。最後に |
| a2 | topic_intro | entry_sha256 | True | NORMALIZED_MATCH | F1-2026-10-13 | v5_j2_e2upbeat_f15_tone_refres | yes | Today's topic is coffee bean prices fall. Are price tags sti |
| a2 | in_one_line | entry_sha256 | True | NORMALIZED_MATCH | F1-2026-10-13 | v5_j2_e2upbeat_f15_tone_refres | yes | Falling coffee bean prices may take at least nine months to  |
| b1b | topic_intro | witness_sha256_and_trimmed_duration | True | NORMALIZED_MATCH | F1-2026-10-13 | v5_j2_e2upbeat_f15_tone_refres | yes | Today's topic is coffee bean prices fall. Are price tags sti |
| b1b | in_one_line | witness_sha256_and_trimmed_duration | True | NORMALIZED_MATCH | F1-2026-10-13 | v5_j2_e2upbeat_f15_tone_refres | yes | Falling coffee bean prices may take at least nine months to  |

- 日本語segment(Std preview/comment)はF1(英語連結発音)の対象外のため再判定対象外(`JA_SEGMENT_F1_NOT_APPLICABLE`)。元の日本語ASR検証結果を引継ぎ(`REUSED_VALIDATED`)。
- 再判定NGはなし(4件の英語segmentすべて再判定OK)。NGが出た場合は引継ぎ不可(UNVALIDATED=再生成対象)になる仕組み(test: `test_f1_rejudge_ng_blocks_and_ok_records_version`)。
- 証跡: `a2_state_rebuilt_02.json` / `b1b_state_rebuilt_02.json`(各entryの`validation_inheritance.f1_rejudge`)。

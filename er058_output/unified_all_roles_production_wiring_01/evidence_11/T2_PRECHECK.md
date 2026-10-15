# T-2追記(1)〜(4) 事前記録(委任_11、有料run前)
(1) 差分再生成の可否: run_tts_a2_2v_new_topic は新規topic用で全segment(topic_intro/見出し2/Voice A/B本文/Hook1,2/Tension/Closing=9 clip)を生成する設計。segment単位のskip機構は無く、「新規topicの全生成」が仕様どおりの期待動作(想定外の全再生成ではない)。共有narrationはMaster Store(隔離コピー)から再利用。
(2) 音声再利用キャッシュ: Master Audio Store(er006_output/master_audio_store_01、33MB)を evidence_11/<part>/master_audio_store へコピーして使用(共有narration再利用)。X-B1-06は意図的にmiss(新規phrase)。
(3) 予算: 各partを --budget-jpy 16、累計Guardrail 16 JPY(spend_ledger、SDK wrapperでtoken実測)。
(4) 想定外の全再生成: 無し(上記は期待どおり)。9 clip以外の生成が見えた場合は実行前にSTOP。

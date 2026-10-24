# ISOLATION_EVIDENCE_01 (FX-PARAGRAPH-CHUNK-TTS-TRIAL-01 委任_02、Opus M1〜M3)

実行: JST 2026-10-25 07:26:10〜07:31:06、`er113_fx_paragraph_chunk_trial_01.py gen --arms B_r1 A_r2 B_r2`(1 launch、再起動0)。生データ=`er113_output/fx_paragraph_chunk_trial_01/isolation_01.json`・`ledger_preflight_01.json`。

## M1: Pronunciation Ledger

- **有料run前preflight**(全13入力=B 10 chunk+A_r2 3 part、現行Production ledger.jsonを読取のみ): hint注入(medium以上)=0件、低confidence再research対象=0件、ASR ledger phrase(low以上)=0件。`all_empty=true`、preflight前後でledger.jsonのsha256不変。A記録(`en_pronunciation_resolver_info.hints_applied=false`、`cache_hits=[]`)と条件一致。
- 実行中: `er006_pronunciation_ledger_01.LEDGER_PATH`を開始時点コピー(`er113_output/…/sinks/ledger_copy/ledger.json`)へ差替え。実行後、Production ledger.json sha256 = 実行前(`90633657ec4e…`)と同一、DEV側コピー sha256 = Production(upsert・書込みなし)。negative_cacheはLedgerと同dirのためDEV側へ追随、Production側`negative_cache.json`は存在せず(実行前後とも None)。
- test: `OpusConditionATests.test_m1_*`(Ledger path差替え・復元・DEV側書込み、negative_cache追随、preflight読取のみ)PASS。

## M2: Local Rewrite回復

- `er020.run_local_rewrite_recovery`をwrapperで包みout_dirをDEV側へ差替え(wrapper呼出記録`LR_EVENTS`)。今回の発火=**0件**(`local_rewrite_wrapper_events=[]`)。Production側`er011_output/local_rewrite_recovery/`のtree digest 実行前後で同一。
- `gen_result_01.json`に全chunkのinstruction_type(全て`english_style_prefix_wide_margin`)、minimal_fallback_used(全てfalse)、local_rewrite_recovery(null)、canonical_text_before_local_rewrite(null)、en_pronunciation_resolver_info、cooldown_events(全て空)、style_prefix_sha256/`style_prefix_equals_A_style`(全てtrue)、tts_model_id、所要時間(cool-down分離)を記録。`condition_diff_flag`=全23件false。

## M3: 監視網

- 保護store 10点+tree 3点のsha256(before/after)=**全て不変**(`protected_changed=[]`): attempt_history.jsonl / human_review_queue(er006) / er021 telemetry / er025 telemetry / master_audio_store manifest・reuse_telemetry / ledger.json / cost_summary.json / **negative_cache.json(追加)** / **er009 ja_foreign_token_gate human_review_queue.jsonl(追加)** / A run dir tree / 公開ページ`uk_train_speaker_playback_e2e_02` tree / **er011_output/local_rewrite_recovery tree(追加)**。
- 開始時刻以降のmtime走査(repo全体、`.venv`/`.git`/`__pycache__`/本Trial出力を除外): 該当2件。
  - `docs/pm/ACTIVE_TASK.md` … 自分の行更新(benign領域)
  - `er115_output/fx_numeric_retention_trial_01/calibration/blind_labels_01.json`(07:28:57 JST) … **並行agent FX-CORE-NUMERIC-RETENTION-TRIAL-01の成果物**(内容: `labeler: Sonnet(sonnet-worker)`、`created_jst: 2026-10-25T07:28:57`、blind判定protocolのlabel集)。本Trialのprocess・関数は`er115_output`を参照も書込みもしない(`grep er115 er113_fx_paragraph_chunk_trial_01.py`=0件)。→ 本Trialの隔離破れではなく**他agentの書込みによる誤検知**。scriptは`suspicious`扱いでrc=1(SystemExit)を返したが、生成・保存は完了後(`gen_result_01.json`/`isolation_01.json`保存済み)。自動再試行・再起動はしていない。
  - 今後の運用への注記: 並行agentがあると`suspicious`が誤検知しうる。Production sinkに該当する書込みかどうかを人手で帰属判定した(上記)。
- cwd==ROOTのassert: `gen`/`preflight`/`postprocess`起動時に実行(test PASS)。

## その他
- 公開済みAdvanced完成版・`A_THEME_DIR`のtree digestは実行前後で同一(上記tree)。Production code/Prompt/flag/閾値の変更0(`git status`でProduction file差分0、DEV script/testのみ変更)。
- `gen/b1b/`(OUT_DIR配下)に`pronunciation_alarms`のWARN(`tts_generation_results.json`不在、生成継続)。出力先はOUT_DIR内で、Production側への影響なし。

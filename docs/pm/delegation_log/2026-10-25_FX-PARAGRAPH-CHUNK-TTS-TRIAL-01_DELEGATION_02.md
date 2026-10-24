# 委任文(Fable→sonnet-worker)
管理ID: FX-PARAGRAPH-CHUNK-TTS-TRIAL-01 委任_02(Opus条件A必須修正M1〜M4+推奨R1〜R4の反映[無料]→preflight→Phase 2有料生成[3 arm、上限50円]→計測→A/B試聴ページ→Gate結果・文書・SSOT・Git)
前提: 委任_01(RESULT_PACKET_FXPC1.md、DESIGN_01.md、commit 09b01a287)。Opusレビュー結果は本委任文§1に全文転記(Opusはread-onlyのためファイル未作成)。**Fable判断: Opusレビューと設計は実質一致・承認範囲内・新仕様なし・予算内のため、M1〜M4反映後にPhase 2へ進んでよい(Fable Go)。Production採用判断は含まない。**

## 0. 最初に
- `docs/research/FX-PARAGRAPH-CHUNK-TTS-TRIAL-01/OPUS_REVIEW_01.md` を作成し、§1のOpusレビュー全文を保存する(先頭に「Fable転記、2026-10-25、条件A」と注記)。
- 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 500 --out docs/pm/delegation_log/2026-10-25_FX-PARAGRAPH-CHUNK-TTS-TRIAL-01_DELEGATION_02.md`。冒頭が「管理ID: FX-PARAGRAPH-CHUNK-TTS-TRIAL-01 委任_02」と一致するか確認、不一致なら index 498〜503 を順に試す(`--index -1`不可)。

## 1. Opusレビュー全文(逐語)
```
## Opus独立技術レビュー FX-PARAGRAPH-CHUNK-TTS-TRIAL-01 Phase 2前(条件A、read-only)

### 判定: 必須修正あり(設計の見直しは不要。Phase 2前に無料で直せる修正のみ)

Trialとしての必要性、方式(段落ごとにTTSを分ける・chunkごとにscalar RMSで音量をそろえる・固定無音でつなぐ・ヘッドルーム弁)、A/B対応表、3 arm構成の骨格はいずれも妥当です。ただし、Production関数の内部に、隔離されていない書込み先と、条件の同一性が崩れる経路が残っています。また、速度の分解には閾値由来の偏りがあります。

### 必須修正

**M1. Pronunciation Ledgerの書込み経路が隔離されていない**(論点d)
- 根拠1: `er025_entity_pronunciation_resolver_core_01.py:470-518`(`resolve_and_augment_en_style_prefix`)。TTS前に、Ledgerのconfidence=low entryが本文に含まれていると、Perplexityでの再research(有料)と`ledger.upsert`が起きます。
- 根拠2: `er006_secondary_asr_01.py:388,468`。Human Review経路の`_resolve_unresolved_entity_for_review`がresearchとupsertを行い、`negative_cache.json`(Ledgerと同じdirに置かれる付属ファイル、`:403,439`)にも書き込みます。
- 現状: `ledger.json`は事後のsha256で検知されるだけで、書込み自体は防げません。`negative_cache.json`は検知の対象外です。
- 対処: 開始時に現行の`ledger.json`をDEV dirへコピーし、`er006_pronunciation_ledger_01.LEDGER_PATH`をそのコピーへ向けます(`redirect_production_sinks`に追加)。読む内容は同一のまま書込みだけを隔離でき、negative_cacheも自動でDEV側へ移ります。
- 追加の無料preflight: 全chunkとA_r2の入力について`augment_style_prefix_with_pronunciation`のhitsと`get_low_confidence_entries_for_text`を事前計算し、A記録(hintなし。style sha一致から推定)と同じく空であることを確認します。空でなければ、Ledgerの状態がA作成時から変わっていて条件差があるため、Phase 2に入る前にFableへ報告してください。working treeの`ledger.json`は既に変更(M)状態です。

**M2. Local Rewrite回復の出力先と、本文・プロンプトの変化が記録されない**(論点b・d)
- 根拠: `er003_v1_sing01_news_tail_fix.py:300-334,381`。Connected Speech層が有効なとき、ASR NGで打ち切った後にLocal Rewriteが発火します。このとき次の3つが起きます。
  - 出力先が固定文字列の`er011_output/local_rewrite_recovery/{theme_id=chunk_id}/b1b`で、Production側のツリーに新しいdirができる(snapshotの対象外)
  - LLMで本文が書き換わる(費用増、Aとの同一本文が崩れる)
  - fallback時は`instruction_type=minimal_fallback`となり、Styleが別文字列になる(`:181-184`)
- 対処:
  1. `retry_primitive.run_local_rewrite_recovery`を、er021と同じwrapper方式で包み、`out_dir`をDEV側へ差し替える。
  2. `gen_result`に`instruction_type`、`local_rewrite_recovery`、`canonical_text_before_local_rewrite`、`en_pronunciation_resolver_info`、`cooldown_events`、`style_prefix`、`tts_model_id`を記録する(現状はstatus・attempts・classification・trimのみ)。
  3. 本文変更やfallbackが起きたchunkは「条件差異あり」としてページと集計に明示し、WPM比較から外すか別枠にする。自動再生成はしない。

**M3. 未知の書込み先を拾う検知網と、cwdの固定**(論点d)
- 現状: 監視は既知8 storeの列挙だけで、新規ファイルを検知できません。
- 対処:
  - 開始時刻以降にmtimeが新しい、または新規作成されたファイルをrepo全体で走査する(`.venv`・`er113_output/fx_paragraph_chunk_trial_01`・`user_test/fx_paragraph_chunk_trial_01`・`__pycache__`は除外)。該当があればSTOPする。
  - 個別監視にも次を追加する: `negative_cache.json`、`er009_output/ja_foreign_token_gate_01/human_review_queue.jsonl`(`er003_audio_tts_asr_safety.py:800`)、`er011_output/local_rewrite_recovery/`のtree。
  - sink差替え先は相対パス(`er113_output/...`)のため、起動時に`os.getcwd()==ROOT`をassertする。

**M4. 速度分解を閾値に依存しない形にする**(論点c)
- 問題: Aの段落境界gapは0.46/0.50/0.54/0.66/0.72/0.84秒で、500ms閾値をまたぎます。A側では段落間の一部が発話時間に含まれますが、B(約1.05秒)とB0(約0.55秒)ではほぼ全てが無音として除外されます。そのため`articulation_wpm_500`では、Bの実発話速度が系統的に「速く/変化なし」寄りに出ます。
- 対処(新しい品質基準ではなく計測方法の追加。すべてローカル・無料):
  1. A、A_r2、B_r1、B_r2(B0はBから0.5秒を除くだけなので同等)の全てで、同じfaster-whisper+difflib整列により段落ごとの発話区間長(段落内の最初の語の開始から最後の語の終了まで)を取る。
  2. これにより「Δ全長 = Σ段落内発話区間の差(実速度)+ Σ段落境界gapの差(ポーズ)+ 両端の差」と厳密に分解できる。
  3. Bの境界gapも、Aと同じ関数で測る(連結構造から計算した値と混ぜない)。
  4. 実速度の結論は、段落単位の比較とart300の両方で一致した場合に限って断定する。

### 強い推奨(費用0)

**R1. ページの公平性。** Aは承認済みの選ばれたtakeであり、B_r1は新規の1 takeです。品質比較で選択による偏りが出るので、A_r2(現行方式の新規take)も試聴行に載せることを推奨します(折りたたみで可)。ページで主に見せるBのtakeは、Phase 2前にB_r1と固定しておいてください(後からtakeを選ばない)。

**R2. 接続gapはBとB0を同格で並べる。**
- B(+0.5秒): C/Zの先例をそのまま再利用した承認済みの値。
- B0(追加0秒): 境界約0.55秒で、Aの約0.62秒に最も近い。
- Aの実測に合わせて秒数を調整する案(例: +0.07秒)は新しい独自の値になるため採りません。B0を「参考」扱いにせず両方を並べれば、ユーザーがポーズの好みと見かけの減速を自分で切り分けられます。

**R3. 声質差(過去P6Bの不合格理由)の評価の枠組み。**
- Aも既にpart1/2/3という独立した3回のTTS呼び出しを、1.0秒の間でつないでおり、ユーザーはそれを承認しています。
- 「Bの段落境界9か所」と「Aの既存part境界2か所」を同じ診断(境界音量差など)で並べると、許容済みの水準と比べやすくなります。
- 任意で、chunkごとの中央値F0とspectral centroidを、段落単位のAと並べて「参考値・判定なし」として表示するのは可です。閾値やGateにはしないでください。

**R4. QCDの記録上の注意。**
- Connected Speech層の10分固定cool-down(attempt3の前)は、所要時間から分けて記録する。
- 短いchunk(p1_2、14語)では、`max_extra_chars=15`の長さ許容が相対的に緩くなり(約19%。part全体では約4%)、`detect_duration_anomaly`も短文で効き方が変わり得る。これは既存規則をそのまま適用した結果の差として記録してください(規則は変えない)。

### 論点別の所見(要約)
- **(a) 接続・音量:** chunkごとのRMS正規化は、CURRENT_SPEC:2099の「独立TTS出力ごと」という適用単位の素直な延長で正しいです。段落末の弱まりなど、chunk内部の強弱はscalar gainでは潰れません。変わるのは段落間の相対的な音量だけで、それはcall間のばらつき(P6Bの問題そのもの)をそろえる方向に働きます。両端の無音(trim margin)がRMSに含まれるため、短いchunkはgainが約0.3〜0.5dB高めに出ます。軽微で既存の慣行と同じなので許容範囲です。peak 0.95で頭打ちになるchunkは、既に設計済みの診断で拾えます。
- **(b) 条件の同一性:** 対応表は良好です。見落としはM1(Ledgerの状態差とhint注入)、M2(Local Rewriteとminimal fallbackでの本文・Styleの変化)、R4です。段落ごとの文脈が切れること(段落頭でprosodyがリセットされる)は交絡ではなく、検証対象そのものです。
- **(c) 速度:** total/articulationの分離方針は正しいですが、500ms閾値に偏りがあります(M4)。take間ノイズは2 takeずつでは差分が1つしか取れませんが、M4で段落単位(10対)に下ろせば実用上十分です。
- **(d) Production非汚染:** 4つのsinkの差替えとsha256比較だけでは不十分です(M1〜M3)。Master Audio Storeは本文では使われないという判断は妥当で、検知も既にあります。Repetition QA moduleにファイル書込みは見当たりませんでした。
- **(e) 過去Trialの再導入:** ユーザー原文で明示された新Trialで、DEV専用・Production変更なしのため、無断の再導入には当たりません。21節B分類の明示も適切です。声質差の評価はユーザー試聴を主にし、R3を補助にすれば十分です。
- **(f) 独自加工・基準追加:** 確認した範囲ではありません。M4とR3は計測と表示の追加で、合否基準にはしません。

### Phase 2のarm構成と費用(B_r1、A_r2、B_r2の3 arm・約12.6円)
- 賛成です。段落単位の対比較(M4)を入れれば、takeを3つずつに増やす(+約8.4円)必要はありません。
- 3 armを1回の起動で直列実行する設計は妥当です。cost logとLedger・sinkを共有し、cool-downもあるため、並列化しない理由は正当です。
- 上限50円も妥当です。M1でresearchが発火した場合のPerplexity費用が、`raw_usage_log`経由で上限判定の集計に入ることだけ確認してください。

### リスクと対処
| リスク | 対処 |
|---|---|
| Ledger・Perplexityの書込みや費用、hint差による条件差 | M1 |
| Local Rewriteやfallbackで本文・Styleが変わり、A/Bの比較対象が崩れる | M2(記録して別枠化) |
| 未知の書込み先による汚染 | M3(mtime走査) |
| 速度を誤って結論づける | M4 |
| 選ばれたtakeとの比較による偏り | R1 |
| chunk失敗でBが成立しない | 既存設計どおり停止して報告(自動再実行しない)。妥当 |

### 関連ファイル
- er113_fx_paragraph_chunk_trial_01.py(`SINK_CONSTANTS`:47、`PROTECTED_STORES`:54、`measure_wav`:196、`redirect_production_sinks`:532、`generate_chunks_phase2`:608-659)
- er003_v1_sing01_news_tail_fix.py(:134-139、:181-184、:300-334、:381)
- er025_entity_pronunciation_resolver_core_01.py(:439-518)
- er006_secondary_asr_01.py(:388、:403、:437-439、:468、:481)
- er011_human_review_lock_01.py(:139-161 derive_segment_key、:593 save_tts_attempt_audio)
- er003_audio_tts_asr_safety.py(:800)
- er013_family_c_production_runner_01.py(:665-670)
```

## 2. Fable判断(反映指示)
- M1〜M4: 全て反映(無料、DEV script `er113_fx_paragraph_chunk_trial_01.py` とtestのみ変更。Production file編集禁止)。M1 preflightで hits/low-confidence が空でなければ、**有料run開始前にSTOPしてFableへ報告**(RESULT_PACKETに書き、最終回答で明示)。
- R1: 採用(A_r2を折りたたみで試聴行に載せる。Bの主表示take=B_r1に事前固定し、DESIGN_01.md追記で宣言してから生成)。
- R2: 採用(BとB0を同格で並べる。秒数の独自調整はしない)。
- R3: 境界診断(境界音量差等)でBの9境界とAの2 part境界を同一診断で並べる=採用。F0/spectral centroidの参考値は**任意**(工数が小さい場合のみ、判定なし・Gateにしない)。
- R4: 記録のみ採用(規則変更なし)。
- Phase 2 Go: `PHASE2_GO.json` を `managed_id=FX-PARAGRAPH-CHUNK-TTS-TRIAL-01`、`cap_jpy=50`、`approved_by="Fable(2026-10-25, Opus条件A反映後)"`、`arms=["B_r1","A_r2","B_r2"]` で作成してよい(M1 preflightが空の場合のみ)。1 launch直列、起動回数は1回を基本とし、再起動が必要な場合は同一run起動間隔150秒以上・RESTART_STORM(5分3回)厳守・再起動回数を記録。TTS直列化flagを尊重(他agentのTTS並走がある場合は待つ)。Cap到達・chunk失敗(HR Lock/ASR NG上限)は自動再実行せず停止して報告(品質Gateの迂回・approve_regenerate使用禁止)。
- 使用モデル: B側TTS=A同一(gemini-3.8-flash-lite-tts、Aoede、条件同一性のため最新原則の例外)。ASR=既存Gateのもの。評価用LLMは使わない(ユーザー試聴とローカル計測で評価)。

## 3. Phase 2後の作業
1. 計測(M4方式+既存のtotal/articulation): part別・全体のWPM(A/A_r2/B_r1/B_r2、B/B0両結合)、段落内発話区間差・境界gap差・両端差への分解、無音合計・ポーズ数、境界診断(音量差、R3)、Gate結果(ASR Gate/Repetition QA/Connected Speech/retry回数/HR Lock有無、chunk別)、条件差異chunk(M2)の明示。
2. A/B試聴ページ `user_test/fx_paragraph_chunk_trial_01/index.html`(既存ページ構造再利用): A(承認済み)/B(=B_r1、0.5秒gap)/B0(=B_r1、追加無音なし)の本文1・2・3個別+本文全体、折りたたみでA_r2/B_r2、比較表(WPM・ポーズ・境界診断・Gate・費用・TTS call数・所要時間)。mp3は `user_test/fx_paragraph_chunk_trial_01/` 配下のみ追跡。公開後にHTTP 200と既存のpage_verify(あれば)で確認し、ユーザー環境から開けるURLを報告(file://禁止)。
3. 文書: `docs/research/FX-PARAGRAPH-CHUNK-TTS-TRIAL-01/TRIAL_RESULT_01.md`(§9の1〜7に対応する事実: 音質[客観指標+Gate、主観はユーザー試聴待ち]、速度[実発話/ポーズ分離]、接続・音量の異常有無、再利用したFamily A/C方式、費用・処理時間、URL、Sonnet所見としてのStatus候補[VALIDATED/REJECTED/USER_DECISION_REQUIRED、最終はFable評価+ユーザー試聴])、`BUDGET_LOG_01.md`更新(実費、出典=raw_usage_log/cost logger)、`ISOLATION_EVIDENCE_01.md`(M1〜M3の実行前後比較結果、mtime走査結果)。
4. SSOT: OPEN-506 Status更新(TRIAL_DONE_PENDING_FABLE_AND_USER_LISTENING等、実態に合わせる)、`DECISION_LOG.md` 1件、`docs/pm/ACTIVE_TASK.md` 自行のみ更新(並行agent FX-CORE-NUMERIC-RETENTION-TRIAL-01 が同時編集中。編集直前に再Read・最小Edit・衝突時再試行)。SSOT編集前にscratchpadへバックアップ、編集後 `git diff --stat -- <file>` 確認。
5. Git: `git status` → 対象pathのみ `git add`(禁止: `-A/-u/-f/-N`、amend、rebase、force push、stash、clean、reset --hard、checkout -f/`git checkout -- <file>`) → `git diff --cached --name-status` で意図外D/Aなし・secret grep 0件・Production file差分0・telemetry/ledger/raw_usage_log/wav不混入(OPEN-490) → `git commit --only -- <path…>` → `git push origin HEAD:main`。他agent差分が同一SSOTに混在する場合は一時index方式。
6. 報告 `docs/pm/RESULT_PACKET_FXPC2.md`: ①M1〜M4/R1〜R4の反映内容とpreflight結果、②有料run記録(起動回数・開始終了JST・実費/上限50円・TTS call数・ASR回数・所要時間[cool-down分離])、③計測結果表、④Gate結果とchunk別異常、⑤隔離evidence、⑥試聴URL、⑦Sonnet所見としてのStatus候補と根拠、⑧変更ファイル・commit、⑨`check_delegation_prompt.py`結果、⑩問題点。

## 4. 禁止
Production code/Prompt/flag/閾値の変更、承認済み完成音声・公開ページ `uk_train_speaker_playback_e2e_02` の変更、独自音声加工の導入、品質基準の無断追加、Gate迂回、Cap超過、`.venv\Scripts\python.exe`以外の使用、自PID以外のprocess終了。Trial成功でもProduction採用・配線へ進まない。
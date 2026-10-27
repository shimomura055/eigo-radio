# B1_FINAL_ADOPTION_01: 採用take記録`final_adoption`(最小)+resume時LR根拠保存(M-4)(委任_06、Phase B / B1、2026-10-28)

実装委任(記録追記のみ・API 0)。設計=INTEGRATION_01 F-2/F-8、OPUS_REVIEW_01 (b)-2・(b)-7・M-4・M-5(Fable照合採用)。Gate判定・retry回数・待機・Fallback Style・LR範囲・ASR判定・Voice/速度・Prompt・TTS呼出は変更なし。

## 1. schema(`final_adoption`、全経路同形・Gate入力ではない)
`{depth, ordinal, slot, style_mode, sent_style_sha, attempt_audio_sha, source}`
- depth: 0=元ブロック / 1=LR後ブロック。ordinal: ブロック内の採用attempt番号(store_reuseはnull)。slot: ①②③(depth0) / ①'②'③'(depth1)(store_reuseはnull)。
- style_mode: `Step.style_mode`(PRIMARY/FALLBACK。er127 step()が決める値をそのまま記録)。Z会話はeffective_modeがctxならPRIMARY、それ以外(従来Dialogue/minimal)はFALLBACK。
- sent_style_sha: leaf結果の`style_prefix`(sha256)または最後の合格attempt行のstyle_prefix。取得不能はnull(推測しない)。Z ctx採用時はctx style sha。
- attempt_audio_sha: 記録時点のout wavのsha256(finish後の減速・連結で変わり得るためGate条件に使わない=Opus M-5(v))。
- source: `tts_attempt` / `store_reuse`。KP_EN key B hitのみ追加で`style_name:"ENGLISH_LOCK"`。
- 持たせないもの: `lr_applied`・`human_approval_superseded`・LR本文(Opus (b)-2)。

## 2. 書込み点
| # | 経路 | 場所(file:line) | 内容 |
|---|---|---|---|
| a | er127 BlockRun.finish(X/Y/Z narrator・KP・JA等、全leaf) | `er127_tts_block_policy_01.py:582`(`_record_final_adoption`)、呼出=`finish`内。`step()`が`_step_modes[ordinal]`を記録(:555) | 採用attempt(finish時にopenかつstatus OK)をBlockProgress`final_adoption`とleaf結果dictへ追記。LR採用時はdepth1 blockのfinishが記録し、depth0 finishは自blockに採用attemptが無いため(③をNGで閉じ済み)depth1の記録を引継ぎ(結果dictに無ければ付与)。失敗終了(status≠OK)は記録なし |
| b | Z会話ctx policy | `er122_fz_ctx_policy_01.py:390`(`_attach_final_adoption`、`finish` status OK時 :418) | 最後に実行したattemptを採用として追記(DONE_OK保存結果にも入る=`adopt_saved_done_ok`でも残る) |
| c | KP_EN Master Audio Store hit | `er019_family_x_kp_en_k2_store_01.py:55`(`_note_store_reuse_adoption`、`ensure_key_phrase_english_component_styled`の戻り直前) | key B hit=`FALLBACK`+ENGLISH_LOCK指示sha+`style_name`、key A hit=`PRIMARY`+K2 style sha、`source=store_reuse`。TTS生成採用(reused≠True)には触れない。er127.finishも`reused is True`なら`store_reuse`を付す(k2が上書き) |
| d | entryコピー | Z `build_entry`: `er063_family_z_audio_01.py:1281-1282`(透過コピー追加、無ければ付けない=旧entryと同形)。X/Y `_generate_or_reuse`(`er019 runner:1178-1188`)は丸コピー=変更不要(testで確認)。Y(`er121`)は`xr._generate_or_reuse`を使うので同じ |
| e | BlockProgress | `_carry_record_keys`(:290)=同一サイクルのdepth1書込みをdepth0の`_write`/`mark_done`が消さない(新規サイクル・DONE済みfileからは持ち越さない)。`final_adoption()`(:398) |

旧entry(記録なし)は現状のまま(再生成・遡及なし)。読取側導出はB2/B4(`er129`、委任_07)の責務。

## 3. M-4 resume時LR根拠保存
- `er020_tts_retry_local_rewrite_01.py:828`: `retts_fn`呼出の**前**に`_write_pre_retts_audit`(:862)。`build_lr_selection_audit`(:841)=純関数で{segment_id, canonical_text, ng_span, selected(id・書換え後文・changed_span before/after・7 Gate結果・各Gate理由・adoptable)、selection_rationale、全候補}。
  - (1)`<out_dir>/lr_selection_audit_<segment>.json`(既存`local_rewrite_recovery_<segment>.json`とは**別名**=上書きなし・既存glob(`er053_family_x_open256_replay`)に当たらない。再TTS後の既存書込みは従来どおり残す)。
  - (2)`retts_fn.pre_retts_audit_hook`属性があれば呼ぶ。`er127.lr_recover`が`_retts`にhook(`:779/796`)を付け、BlockProgress `lr.audit`へ保存(`save_lr_audit`:383。`save_lr_text`は`audit`を消さない)。関数シグネチャは不変(既存fake/mockの`run_local_rewrite_recovery`と互換)。書込失敗はLRを止めない。
- resume(`lr_recover`のstored分岐 :806): 保存済みauditがあれば`recovery["lr_selection_audit_restored"]`に復元(LR LLMは再実行しない・policy/Gate/候補選定/再入禁止は不変)。
- 既知の制約: resume時に`er020`は呼ばれないため、再TTS後の`local_rewrite_recovery_<seg>.json`は初回processが書いていなければ出ない(従来どおり)。根拠はBlockProgress `lr.audit`+`lr_selection_audit_<seg>.json`で保持される。

## 4. test
新規 `er127_final_adoption_b1_test_01.py` 18件(PASS): (a)finishで`final_adoption`がBlockProgress`verified`(depth,ordinal)と一意に整合(L1〜L4・①/③Fallback/LR後①')・失敗終了は記録なし・scope外は記録なし・最小キー(lr_applied等なし)・slot表記・sent_style_sha抽出 (b)Z ctx採用(ctx PRIMARY/従来Dialogue FALLBACK/NG記録なし・保存結果にも残る) (c)Store key B hit=store_reuse+ENGLISH_LOCK/key A hit/TTS生成は不触/er127.finishのreused (d)Z `build_entry`透過・X `_generate_or_reuse`再利用で保持 (e)resume後にLR根拠が読める(LR LLM再実行なし)・本物の`run_local_rewrite_recovery`でhook/監査fileが再TTS前・既存post fileは残る (f)旧entry/旧BlockProgress(記録なし)で例外なし。
既存test: `er127_tts_block_policy_01_test_01`+`er020_tts_retry_local_rewrite_01_test_01`=139 passed、golden A/B/C(`er127_test_golden_01`)byte同一=PASS、関連(er020/er122/er063/er019/er003_lr/er025/er007) 382 passed + 既知失敗1件。既知失敗`er020_tts_retry_local_rewrite_fullseg_test_01::RegressionCorpusTest::test_recorded_candidates`は変更前(`git stash`で5ファイルをHEADへ戻して実行)でも同一失敗=差分なし(OPEN-543系の保存corpus依存)。拡張回帰(er127/er020/er122/er063/er019/er121/er003_lr 全test)=変更後 1522 passed・10 failed・1 error / 変更前(5ファイルをHEADへstash、新test除外)1505 passed・9 failed・1 error。失敗は全て変更前にも存在(er020 fullseg corpus、er019 fx_20261016 AbcGolden、er019_x_std_chunk_opus R4Hunk、er121 Y no_network 5件+runner 2件+comment2 ERROR)。差の1件`er019_family_x_fx_20261016_wiring_01_test_01::AbcGoldenTests::test_k2_store_module_is_family_x_only`は変更前でも単独実行で失敗(subset実行で変更前3 failedに含まれる=実行順依存の既存失敗)。変更前後でtest本体の失敗集合に新規なし。Y no_network系は新test+Y testの単独組合せ(124 passed)では全PASS(実行順依存)。

## 5. 観測・未観測
- 観測: 上記offline test(fake backend、API 0)。
- 未観測: 実run(正式Production経路)での記録=次回run。実run前の既存BlockProgress・entryには記録が無い(読取側で導出)。
- 発見(修正せず報告): KP_EN key B hit時、`finish`は未closeの②を`status==OK`で`verified:true`にする(既存挙動。TTS未実行なのでBlockProgress上は「②採用」に見える)。`final_adoption`はこの場合`ordinal=null/source=store_reuse`とし、記録不一致検査の対象外とする(B4の「食い違い時のみ停止」規則で`source!=tts_attempt`は除外すること)。分類=修正へ進む(軽微・B4仕様に注記で吸収、policy変更なし)。

## 6. 既定動作不変の根拠
- 追加のみ: 新キー`final_adoption`/`lr.audit`/`lr_selection_audit_*.json`/`lr_selection_audit_restored`。既存キー・判定・回数・待機・Style・LR候補選定・TTS呼出を編集していない(diffはfinish/step内の1行記録、`_write`/`mark_done`の持越し、`retts_fn`前の書込み、leaf結果へのキー追加のみ)。
- 記録失敗は全て握り(例外で生成・採否を止めない)、scope外leaf(`_blk=None`)は経路が通らない(test)。
- ASR判定・Gate・HR・Lockは`final_adoption`を読まない(読取側はB2/B4で`er129`)。

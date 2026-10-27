# 委任_07(Phase B / B0+B2): 新module `er129_lr_display_reflection_01.py`(採用take解決・LR/Fallback台帳導出・anchor位置特定・三者一致・確定内容重なりT1-T3)=未配線の純module+test、保存LR entry 43件への適用(偽STOP 0確認)、Opus findings台帳登録。API 0

共通事項=`…_委任_00_COMMON.md`。設計=`INTEGRATION_01.md`(§1・F-1/F-3/F-6/F-11)+`OPUS_REVIEW_01.md`((b)1〜6、M-1〜M-6、R-1/R-4、Fable照合)+`W2_UD1_BODY_REFLECTION_DESIGN_01.md`(§4-§6、test計画U1-U8)+`W4_FINAL_HUMAN_REPORT_DESIGN_01.md` §3(読取規則→本moduleへ統合)+`W1_ROUTE_WIRING_AND_RECORDS_01.md`(記録所在表)。成果物=`docs/research/LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01/B2_LEDGER_MODULE_01.md`。**実装委任**(新module・新test・docs/pm/OPUS_FINDINGS_LEDGER.md追記のみ。既存Productionコードは編集しない=未配線)。

## 契約(B0)
`er129_lr_display_reflection_01.py`(純関数・読取専用・LLMなし・ファイル書込みは監査出力関数のみ):
1. `resolve_adopted_take(entry, block_progress, hr_records, store_info) -> AdoptedTake|UNKNOWN`: 優先順位=①人間承認の採用記録(`er121_e1_hr_adopt_r0_01.py:132-147`、X `record_human_approval`相当) ②再利用(Store key/ `_generate_or_reuse`) ③`final_adoption`(委任_06が追加中。schema=`{depth, ordinal, slot, style_mode, sent_style_sha, attempt_audio_sha, source}`)とBlockProgress `verified`(depth,ordinal)の突合(食い違い=`RECORD_MISMATCH`) ④旧記録からの導出(`retts_result`/attempts/`english_lock_attempts_log`/`fallback_attempts_log`命名逆転(W1 DR-6)/Z `dialogue_tts`) ⑤UNKNOWN。「記録完全」の定義はここに一本化。
2. `build_lr_ledger(run_dir, level) -> Ledger`(メモリ導出。clip毎: role/segment・chunk id/adopted take/lr{before,after,ops,changed_spans(anchor),reason,source}/fallback{used, adopted_style, from_style, slot}/text_parity{display, tts_input, asr_expected, verdict}/overlap{T1,T2,T3}/warnings)。人間承認で原文復帰は`er020.resolve_expected_text_after_local_rewrite`を唯一の参照点。`write_ledger_audit(ledger, path)`は監査用出力のみ(Gate/表示はメモリ導出を使う)。
3. anchor位置特定(M-1/M-2): 変更op(replace/insert/delete)を隣接一致語を取り込みreplaceへ正規化し、前後k語(k=2〜4、段階的)のanchorで表示文(正規化前`spec.text`/parts.json)中の一意位置を特定。句読点差は単語単位一致で判定(STOPにしない)。TTS正規化(数字語化・人名発音置換・PNAP)に依存しない。Z V2照合は`audio_text_after`。X chunk→親part写像検証(W2 §4-2-3)。
4. 三者一致 `check_text_parity(display_after_overlay, tts_input, asr_expected) -> verdict`(文単位、正規化差は上記規則)。
5. 重なり `check_confirmed_overlap(ledger_clip, confirmed_selection, grammar, facts) -> {T1,T2,T3}`: T1=`er128.lr_overlap`を純関数として再計算(`confirmed_kp_lr_overlap.json`は読まない、M-3)。T2=変更箇所を含む**1文**と確定項目・文法の出典文(M-6)。T3=表示側テキストで数字・固有名詞(M-6)。
6. `classify`はB4(別委任)が本moduleの出力を受け取る。本委任では分類核を作らない。

## 作業
1. 上記moduleとtest(`er129_lr_display_reflection_01_test_01.py`: W2 U1-U8+Opus M-1〜M-6の再現ケース[正規化差・insert/delete・句読点・resume形(`rewritten_segment`のみ)・HR原文復帰・Store再利用・旧記録・UNKNOWN・RECORD_MISMATCH・T2 1文定義・T3表示側])。
2. **保存LR entry 43件(W4 §3一覧)+Fallback採用entry(告げ口心臓Adv kp2_en・Y E-1・tru_ev evidence run群)へ`build_lr_ledger`を適用**し、結果表(clip/判定/位置特定/parity/overlap/警告)を成果物へ。偽STOP(正常LRがUNLOCATABLE/UNSUPPORTED/RECORD_INCOMPLETEになる)が0であること。0でなければ原因と規則修正を記録(規則修正はOpus (b)-6の範囲内)。AI島Std/AdvでLR記録から`AI agents`/`AI systems`が自動導出されること(R-7)。
3. `docs/pm/OPUS_FINDINGS_LEDGER.md`へOF-LRW-M01〜M10(OPUS_REVIEW_01 M-1〜M-10)を既存形式で追記(対応状況: M-1/2/3/6=本委任で対処、M-4/5=委任_06、M-7=B3、M-8=統合commit、M-9=B4差分監査、M-10=B4/B6後確認)。
4. 既存Productionコードは編集しない(委任_06がer127/er020/er122/er063/er019を編集中)。run dirを書き換えない(前後sha一致をtestで固定)。
5. Git: 新規ファイル+OPUS_FINDINGS_LEDGER+成果物のみ`git add`、commit「LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01 委任_07(B0/B2): er129 台帳導出module(未配線)+保存LR 43件適用+Opus findings登録(API 0)」+`Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`、`git push origin HEAD:main`(競合時`git pull --no-rebase origin main`)。
6. 最終応答: 成果物パス+要約10行(API面/test件数/43件適用結果[偽STOP数]/AI島導出結果/未観測)。

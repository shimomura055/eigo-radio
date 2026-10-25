# OPUS_REVIEW_REQUEST_01 (FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01 委任_01、条件A: 新しい処理フローの設計)

依頼元: Fable(PM)。レビュアー: opus-consultant(read-only)。Opus利用枠: 条件A(必須レビュー、回数上限の対象外)。
対象設計: `WIRING_DESIGN_01.md`、照合: `EXISTING_SPEC_CHECK_01.md`、ドラフト+test: `chunk_tts_core_draft_01.py` / `tests_draft_01.py`(24 PASS)。いずれも `docs/research/FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01/`。
背景: ユーザーがTrial方式(X=段落+0.2秒、Z=B_r1)を2026-10-25にAPPROVED_FOR_PRODUCTIONとした(`docs/pm/delegation_log/2026-10-25_FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01_USER.md`)。品質判断(境界音量差・減速)は**再審査の対象外**(ユーザー試聴済み)。依頼するのは**配線設計の技術妥当性**のみ。方式・ポーズ・対象の変更は不可(変更が必要と判断した場合は理由を示して差戻し=STOP)。

## 論点(それぞれ「妥当/修正必須/任意」で判定してほしい)
1. **既存clip単位Gate/Ledger/HR/Storeのchunk単位への写像**(EXISTING_SPEC_CHECK §4): chunkを通常segment entryにして共有Gate(`assemble:485`)・HR Lock(`er011:139,179`)・telemetryを無変更で効かせる設計に、取りこぼし(静かに弱まるGate)はないか。特に**role解決の拡張(C4)を入れ忘れるとConnected Speech層が外れる**点と、`_CLIP_ID_RE`(`er063:82`)の拡張範囲(7箇所)。他に`segment_id`/`clip_id`の完全一致・`fullmatch`に依存する箇所の見落としはないか(`er078`のpass_with_warning/reuse_value_guard、`er103`のPNAP/Run Entity Table、`er109`のhomophone scope、`er_user_listening_page_common_01`等)。
2. **親集約entryのstatus導出(C3)**: 共有Gateを変更せず、`refresh_parent_status`が共有の`_segment_gate_status`を呼んで導出する方式。人間承認後の再gateで親が通る、`pww`の二重表示を避ける(親へasr_judgementをコピーしない)、`prune_cached_to_plan`が親を落とすため毎回再構築する、の3点に矛盾はないか。代案(共有Gateへ分岐追加)との比較。
3. **target_rmsの基準(C2)**: 親wav=生chunkの0.2秒連結から`(preview+親)/2`を取る通常式。uk_train Trial wavでtarget 0.09149→0.0966/0.0975(+0.5dB)、peak cap発動1/20 chunkを実測。許容でよいか、より良い基準があるか(ただし新たな音量基準・独自LUFSは導入不可)。
4. **retry/resume/regenerationの整合**: (a)chunk失敗でそのchunkで停止し後続を生成しない (b)resumeはOK chunk再利用・失敗chunkのみ再生成 (c)plan再計画禁止(同一入力は決定論、保存planと不一致はSTOP、text変更時のみ再計画) (d)`--only-segments`/`--only-clips`の親→chunk展開 (e)Local Rewrite後のcanonical_textとplan語数の関係。既存retry上限(`PRODUCTION_MAX_TTS_ATTEMPTS`)・Local Rewrite・cool-down・RESTART_STORM/STOP sentinelを回避/二重化していないか。
5. **欠落・重複・順序変更の防止(C5)**: 5層(planner assert / chunk text全体ASR / 親集約整合検査 / 合成長検査 / 記録)で十分か。chunk境界の語欠けはASR(chunk text全体照合)のみで検出される点の妥当性(Trialではwhisper整列で全段落整列を確認済み。Productionは実行時の追加計測を課さない方針)。
6. **旧150語ルールとの整理(WIRING_DESIGN §Z-h)**: Fable方針の「Advのnarrator 100語超は新plannerに一本化」に対し、設計は**共存(150語ルール不変・後段に新ルール)**を推奨(plan stage出力・Family C共有コード・clip間gap 0.5→0.2変更=未承認の聴感変更、を理由)。この判断は妥当か。一本化が望ましい場合の最小変更と影響範囲。
7. **Std非適用の担保**: X a2・Z a2(6%減速)、Dialogue、短narrator、KP、Y(er110)にコード上chunk経路が入らないこと(`chunked=False`で分岐前に抜け出力バイト不変)の確認方法は十分か(「非対象の`reuse_key`変更前後バイト一致」test、`resolve_narrative_role`既存ID不変スナップショット)。
8. **runtime evidence計画と費用(WIRING_DESIGN X-j / Z-j)**: X=uk_train新out_dirでAdv TTS段(≈5〜10円)、Z=run_sf_prod_02複製+`tts_b1b`のみ(≈1.5〜3円。完全新規は≈15〜20円)。「正式初回経路での発火」の証拠として十分か。Zの複製方式で`assert_run_style_record`/provenance/RUN_LOCK/segment_planの`narration_path`(絶対的な旧run path)に問題が出ないか、Z完成段は`provision_shell`込み1起動(OPEN-480)。
9. **並行編集との衝突回避(WIRING_DESIGN C8)**: `er019`/`er026`/`er063`をuncommittedで他agent(FAMILY-Z-STUDY Part 1配線/FX-CORE-NUMERIC配線)が編集中。関数単位の追加+一時index方式commitで十分か。`git diff --cached`に他者hunkが混ざらない手順の追加提案。
10. **費用・原価**: X +0.30円/Adv本文、Z +0.12〜0.2円/Adv、時間+数十秒(Trial実測ベース)。記事セット70円目標への影響の見積(X約0.4%、Z 0.3%未満)に誤りはないか。

## 渡す観点・不要なもの
- 新方式の採否・音質評価・追加Trial提案は不要(ユーザー決定済み)。品質Gate緩和の提案は不可。
- 出力形式: 判定(必須修正あり/なし)、必須修正(根拠file:line付き)、任意提案、実装時の確認項目。Fableが照合し、11-3のSTOP条件に該当しなければ実装委任へ進む。

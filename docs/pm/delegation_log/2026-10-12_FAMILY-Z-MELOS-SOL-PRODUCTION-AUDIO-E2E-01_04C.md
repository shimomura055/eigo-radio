# FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_04C(2026-10-12)

範囲: er063 Audio(Role Style表・TTS stage・Dialogue Voice・Gate・Std減速検査・Z専用再利用helper・assembly・試聴ページ・evidence)。実装+mock tests(46件)+最小実smoke(2 clip、実費JPY1.91)。PRODUCTION_WIRED未達(er026統合は後続)。SSOT編集なし。共有module/X定数/er061/er062/er026は無編集。

## 1. Melos別Voice可否(STOP判定): STOPなし
`STORY_REGISTRY["melos"]["voice_tts_names_plan"]`にMelos用キーは無い(testで固定)。ただし既存機構(Family C `classify_quote_voice_window`は任意のvoice->keyword辞書、er012 `generate_voice_body_wide_margin`は任意voice_name)は**設定追加のみ**でmelosを載せられる(`check_melos_voice_mechanism()`で実関数検証、コード変更なし)。er063内に設定を置いた: `FAMILY_Z_DIALOGUE_VOICE_KEYWORDS`(melos/selinuntius/dionysius)、`FAMILY_Z_DIALOGUE_VOICE_TTS_NAMES`(narrator=Aoede, selinuntius=Erinome, dionysius=Charon は計画どおり)。
**要判断(USER_DECISION候補)**: `melos`のVoiceは計画に無かったため暫定`Algieba`(Family C 'brother'運用実績Voice)を置いた=`PROVISIONAL_UNAPPROVED`。新Voice割当に当たるため承認が必要。er062のspeaker語彙(king/friend/melos/other)は`normalize_speaker`でdionysius/selinuntius/melosへ写像、`other`はSTOP。

## 2. 実装概要(`er063_family_z_audio_01.py`)
- Style表`FAMILY_Z_ROLE_STYLE`+`FAMILY_Z_ROLE_STYLE_VERSION="z_v1_pd8_r2_e1_e2up_k2_m2_20261012"`。実装時に原典ファイルから逐語抽出しsha256一致を全件確認(`verify_styles_against_origin`、testにも組込み)。runtimeは`assert_style_table_integrity()`でZ定数自身のshaを検証(Trialファイル非依存)。X定数不変(copy一致をtest)。
- TTS stage `run_tts_stage`: 配置`<run>/{a2|b1b}/narration/<segment>.wav`(`_has_valid_narration_layout`True、segment_id導出をtest)。narrator Adv=`news_tail_fix.generate_news_narration_wide_margin`(X B1入口)、Std=`generate_a2_segment_with_slowdown`(6%)、Dialogue=`generate_voice_body_wide_margin`(Adv: `style_prefix_override`を渡さない / Std: `A2_ENGLISH_STYLE_PREFIX_SLOWER`+`apply_a2_slowdown_postprocess`、PD8混入なし)、Preview/Comment=`generate_charon_english`(Adv)/`generate_a2_japanese_with_reading_safety`(Std)、KP英語=K2 primary(`generate_narration_snippet_verified_strict`)+既存ENGLISH_LOCK fallback(Master Store非経由)、KP日本語意味=M2、topic_intro/japanese_title=X既存承認Style、shell/番号=`B1_SHARED_SOURCE_DIR`の読取コピー(Master Store書込なし)。retry/fallback/cool-down/Local Rewrite/Human Review Lockは共有module既存cascadeをそのまま使用。
- M4 `generate_or_reuse_z`(キー: canonical_text sha・`FAMILY_Z_ROLE_STYLE_VERSION`・voice・style prefix sha・tts_backend、+wav実在・sha一致)。X versionを変えても影響なし(test)。
- M6: LR発火clipは`audio_text_deviation`(before/after/diff)をentryとprovenanceに記録、`er061.revalidate_after_local_rewrite(text_before, text_after)`を遅延import・fail-closedで呼ぶ(実signatureをtestで固定)。PASS以外/未提供/原稿未指定はSTOP、STOP時も監査記録(results/evidence)を書いてから停止。M2は再検証未PASSのLR clipを不採択。cool-down発生をentryに記録。
- Gate `run_audio_gate`: M2(`assert_tts_results_complete`) -> M1(`verify_std_english_slowdown`、Std全Story clip=narrator/dialogue/`_cN`/Human Review採択、slowdown_applied True または現行/original長さ比[1.03,1.09]) -> 品質(peak/clipping/無音/長さ) -> 既存`verify_episode_audio_validation_gate`(KP source gate含む。`article_text`は原稿canonicalのまま)。
- M5: `assert_dialogue_attribution`(決定論 vs LLM、不一致1件でSTOP+`dialogue_override`記録)、`default_llm_attribution_fn`(FAMILY_Z_DIALOGUE_ATTRIBUTION)。
- Assembly: `build_z_sequence`(Family C `build_family_c_episode_sequence`再利用、In One Lineなし、Comment2=Part1最終clip後・Comment3=Part2最終clip後)、`run_assembly`(gain -> assemble_with_timeline -> headroom -> `assembly/timeline.json`)。
- 試聴ページ: `build_pages` -> `user_test/family_z_melos_01/{index,standard,advanced}.html`(file:///禁止/レベルラベル非表示/KP 2列/lint内蔵、静的ファイルのみ。実ページ生成はE2Eで実施)。`er063_family_z_page_verify_01.py`(Playwright、Gate 7 (a)〜(n))。tooling確認は偽音声ページで実施: `er063_output/family_z_audio_01/page_verify_tooling_check_01.json`。
- 追加成果物: `er063_family_z_audio_01_smoke_01.py`(実smoke)、`er063_family_z_page_verify_01.py`。

## 3. Style表(role x style sha x voice)
| role | style | sha256先頭12 | voice |
|---|---|---|---|
| Adv narrator Full Story | PD8逐語 | 329ff46a5ec3 | Aoede |
| Std narrator Full Story | PD8 + 改行 + A2_SLOWER_PACE_INSTRUCTION.strip() (+6%減速) | 74b456cacf74 | Aoede |
| Dialogue(Adv) | 既存Dialogue Style(override無し、実効=p9a.ENGLISH_STYLE_PREFIX) | 実効shaをeffective_style_prefix_sha256に記録 | per-speaker |
| Dialogue(Std) | 既存Dialogue Style + A2_ENGLISH_STYLE_PREFIX_SLOWER + 6%後処理(PD8なし) | 実行時算出 | per-speaker |
| Std JA Preview/Comment1-3 | R2逐語 | 625826c1187b | Aoede |
| Adv EN Preview | E1逐語 | 8862317ff766 | Charon |
| Adv EN Comment1-3 | E2_UPBEAT逐語(Coffee Adv Comment採用値) | 37c52d6ec237 | Charon |
| KP英語 | K2 | 9d905cfe6c04 | Aoede |
| KP日本語意味 | M2 | e7617e15c29e | Aoede |
| topic_intro / japanese_title | X既存承認(TOPIC_INTRO / J3) | X定数と一致をtest | Charon(Adv) / Aoede(Std) |
| shell・番号 | 既存Master/共有資産(Charon。A5/B5は照合のみ、Z未適用) | - | Charon |

OPEN-303: Coffee最終音声のStd Preview/CommentはP2だった。Zは決定どおりR2(R2原典と逐語一致を確認)。報告事項は「Coffee最終音声はP2でありR2と本文(Style)が異なる」点のみ。

## 4. smoke結果(実TTS、実費JPY1.91、上限JPY3以内)
証跡: `er063_output/family_z_audio_01/smoke_01/`(summary.json, cost_log.jsonl, narrator.mp3, king.mp3, melos/.../attempts/*.json)。Standard同期(TTS_EXECUTION_MODE=STANDARD)。
- narrator(Adv, PD8, Aoede): model実測=`gemini-3.8-flash-lite-tts`, voice=Aoede。attempt1でASR「mellows」(Melos誤認識、entity_only UNCERTAIN) -> Local Rewrite(", and Melos" -> ", as Melos")が発動して合格(4.27s)。この回はLR再検証フックの引数不一致(er061の実signature未反映)で結果保存前に停止したため、narrator証跡は既存artifact(attempts/*.json, LR json, cost_log)から集約(再生成による追加課金を避けた)。修正後はSTOP時も監査記録を書く設計に変更済み(testあり)。
- king(Adv dialogue, dionysius): voice=Charon、model実測=`gemini-2.5-pro-preview-tts`(attempt metadata)、attempt1でNORMALIZED_MATCH、3.50s。
- 判定: Dialogue Voice切替は期待どおり(narrator=Aoede / king=Charon)。**ただしmodelが異なる(下記リスクA)**。

## 5. er026統合時に必要なstage定義(提案)
`tts_<level>`(er062 segment_plan clips[id,speaker,text]+support/KP -> `build_level_plan` -> `run_tts_stage(run, level, plan, article_text=<原稿全文>)`)、`provision_shell_<level>`、`gate_<level>`(`run_audio_gate`)、`assemble_<level>`(`run_assembly`)、`pages`(`build_pages`)。順序: dialogue attribution(M5, 各level 1 call) -> tts_a2/tts_b1b -> provision -> gate -> assemble -> pages -> Playwright(`er063_family_z_page_verify_01.py`、公開URL版)。`--only-clips`相当=`run_tts_stage(only_clips=...)`。KP資産は`<run>/<level>/key_phrases/keywords_canonicalized.json`が必要(既存Gateの参照先。er062は`<run>/key_phrases/`に出すためcopyが必要)。budget集計はer026側(cost_logger install + `compute_cost_jpy_so_far`)。dry-runはplanのみ返しファイル/Master Store/telemetry/queue不変(testで監視ファイルshaを比較)。

## 6. 設計書との差異・判断(要確認)
1. entry `status`は既存Gate互換の`"OK"`等を維持し、設計4-4の`status`(adopted/...)は`z_adoption`として併記(既存Gateがstatus=="OK"を要求するため)。結果ファイルは既存形式`{"segments":{...},"key_phrases":{rank:{english,japanese_meaning}}}`の拡張。
2. 減速比は`現行/original`(約1.06)で判定(既存Gateと同じ向き。設計書の「original/current」は逆向きの記載)。
3. Std Dialogueは設計の「style_prefix_overrideを渡さない」ではなく`A2_ENGLISH_STYLE_PREFIX_SLOWER`を渡す(6%減速時の既存Voice A/B Std仕様。PD8は不混入)。Advは渡さない。
4. KP第3segmentは両levelとも`kp{n}_ja.wav`(日本語意味、M3対応表どおり)。X B1のAdv KPは英語解説だが、Z Advで英語解説を使うかは未決(er062/Fable判断)。
5. Gate (m)(公開URL)・Pages公開・実機試聴はE2E委任。`--local`検証は内部証跡で、`http.server`がRange非対応のため通し音声seekは偽陰性(GitHub Pagesは対応)。

## 7. 残リスク
- **A(モデル不一致)**: Dialogue clipは共有関数`generate_voice_body_wide_margin`が`p9a.ENGLISH_MODEL_NAME`(`gemini-2.5-pro-preview-tts`)固定でflash-lite化されておらず、narrator/他clip(flash-lite)と声質・Style反応が異なる可能性。flash-lite化は共有module変更が必要(本委任では禁止)。試聴で違和感が出た場合はFable/ユーザー判断(共有module変更の別委任)。
- **B(Melos固有名のASR誤認識)**: 実smokeでMelosが「mellows」に誤認識され、1文だけでLocal Rewrite(Perplexity + gpt-6-luna 2 call、約JPY1)が発動。本編(Melos頻出)では再発しやすく、cool-down(最大10分/clip)・LR・追加費用が見込みより増える可能性。Pronunciation Ledgerへの「Melos」登録(別承認)で緩和できるが本委任では未実施。
- C: Family C B1 assemblyは初実行(OPEN-305)。mockでsequence/headroom/timeline/pagesは通過。実音声のpeak/headroomはE2Eで確認。
- D: Melos Voice暫定(上記)。E1/E2_UPBEATのZ適用はXのCoffee決定の流用(Zへの明示承認は未確認)。
- E: LR再検証のanchorsは`validator_anchors.json`(04A作成)が前提。smokeはmockで通した。
- 副作用: smokeは共有関数経由で`er011_output/attempt_history.jsonl`・`er011_output/local_rewrite_recovery/run_smoke/`等へ追記/作成(共有機構の標準動作)。commit対象外。

## 8. テスト・Regression
`er063_family_z_audio_01_test_01.py` 46件PASS(課金0)。関連suite新規failure 0(全OK): er019 audio runner(49)/flash_lite_role_style(8)/variable_role_style/pointless(10)、er003 n3_tts(24)/standard_a2(27)、er011 human_review_lock(18)、er013 production(39)/future_qa_08、er020 retry_local_rewrite(23)、er026(19)、er060(9)、er012 variable_voice_count。共有module非編集のため既存結果と同一。

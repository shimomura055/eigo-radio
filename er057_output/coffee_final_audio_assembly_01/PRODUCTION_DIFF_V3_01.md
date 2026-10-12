# PRODUCTION_DIFF_V3_01(FAMILY-X-COFFEE-FINAL-AUDIO-ASSEMBLY-01 委任_02、2026-10-12)

Final v3 はTrial隔離経路の成果物であり、Production正式経路の成果物ではない(PRODUCTION_WIRED=未)。ユーザー決定「Coffee限定APPROVED_FOR_PRODUCTION」はStyle選択に対する承認で、配線の完了を意味しない。前回 `part_final/PRODUCTION_DIFF_03.md` からの差分を中心に記す。

| 項目 | Production正式経路 | 本Final v3(Trial) |
|---|---|---|
| 初回生成経路 | runner(`er019_family_x_audio_production_runner_01`)。Styleは `fl_styles.FAMILY_X_ROLE_STYLE_EN`(role別・全記事共通定数)から取得 | Trial専用 `er057_coffee_final_v3_gen_01.py`。Full Story=PD8逐語(sha 329ff46a…)、In One Line=既存承認Style(Std=A2減速指示付き既存prefix)、他roleは既存Trial音声/既存承認音声の再利用 |
| TTS方式/モデル | Batch既定 / gemini-3.8-flash-lite-tts | Standard同期(DEV) / 同モデル(最新原則上の例外なし) |
| retry/再生成 | Production retry機構(上限・cool-down、cascade、Local Rewrite、minimal fallback) | 同一Promptで最大2回再生成(Std Part2は3 attempt全てPrimary UNCERTAIN)。Local Rewrite/minimal fallbackは不使用 |
| ASR(Std Part2以外) | Primary→cascade→意味等価→LR 等 | Primary ASR+既存validatorのみ(Part1/3/IOLは初回合格) |
| ASR(Std Part2) | 同上 | Primary 3回UNCERTAIN→**Production既存`er006_secondary_asr_01.evaluate_attempt_with_cascade_detail`(cascade_enabled=True、enable_connected_speech_equivalence_layer=True、segment_id=full_story_part2、Phrase List無し)をTrial隔離で適用**。3候補とも `NORMALIZED_MATCH`(a1/a2=Secondary#1[Azure]、a3=Primary#2)。採択=a1(local whisper差分最少4語、長さ50.47秒)。これは既存承認経路の利用であり新仕様ではない。ledger書込(`_resolve_unresolved_entity_for_review`)は無効化、human_review_queue(`_log_human_review`はwrapper側のため不呼出)・telemetry・cost_logger(Trial専用ファイルへinit)はProductionへ書かず |
| F-5型偽NG(OPEN-272) | validatorの `us` vs `u s` 等entity_like判定でUNCERTAIN→blind retry | v3 Part2で3回再発(US/U.S.、cost/costs、9/nine、2/two、raw-bean/raw bean、大小文字、コロン)。Productionでも同条件ならretry消費・Human Review行きになり得る。cascade到達によりPASSできた(Secondaryコスト+約JPY4.4/呼出相当) |
| 6%減速 | `generate_a2_segment_with_slowdown`内 | 同一処理 `apply_a2_slowdown`。減速後ASRは参考記録のみ(OPEN-270の外側ループ未実装は維持) |
| assemble | `stage_assemble_family_x_{a2,b1}`(Gate・run dir書込) | Trial assembler(`er057_tone_trial_final_build_03_asm.py`)無改変、role→wav差替えのみ。Audio Validation Gate未呼出(`qa_v3_01.json`で同等計算) |
| 発音hint/Pronunciation Ledger | Style末尾にhint | 省略(PD8 Style逐語優先) |
| Master Store | shell/KP登録・再利用 | 未登録・未参照書込 |
| manifest/telemetry/human_review_queue/attempt_history/ledger | 書込あり | 書込なし(`production_sha_after_v3_02.txt`。8ファイルのmtimeは全て本タスク(委任_01開始)前=最終書込 10-11〜10-12 09:13、本タスクによる更新なし) |
| Gate記録・Human Approval | あり | なし(Trial)。Production採用承認は人間ユーザーのみ |

## Coffee限定でProduction経路へ反映する方法(共通Prompt/routingを変えずに)
- 現状Productionは role→Style を `FAMILY_X_ROLE_STYLE_EN`(全記事共通の定数)で解決する。**記事別(Coffee限定)にStyleを差し替える既存の仕組みは確認できない**(`style_prefix_override`は下位関数の引数だが、runnerが記事単位で値を渡す経路は無い)。
- 共通定数を変更せずにCoffee限定とするには、runnerへ記事ID(theme key)単位のStyle override層を新設する必要があり、**新しいコード経路の設計=条件A(Opus独立技術レビュー)対象**。本タスクでは実装していない。
- もう一つの方法は、完成音声をrunner外で組立てた後にCoffeeのepisodeとして取り込む運用(Master Store/Gate/manifestとの整合は未検証)。これも仕様未定。
- 結論: 方法は「新規override層の設計・承認」が必要で、現時点で無改変で実現する手段はない。

## PRODUCTION_WIRED判定に不足するevidence
1. Coffee限定Style overrideの設計・仕様化・人間承認(Opus独立レビュー含む)と実装
2. 実Production runner(Batch、初回経路)でPD8/IOL新原稿/各Styleが適用されたruntime evidence
3. 正式ASR cascade/retryを通した全Part合格(F-5偽NG対策OPEN-272の扱い含む)
4. Audio Validation Gate・Master Store登録・manifest/telemetry整合
5. In One Line 2文方針の仕様化(既存仕様「中心1文+補足2文程度」との整理)
6. 減速後検証の外側ループ(OPEN-270)の扱い

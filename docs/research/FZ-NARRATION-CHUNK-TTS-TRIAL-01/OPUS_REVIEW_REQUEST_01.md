# OPUS_REVIEW_REQUEST_01 (条件A: 新しい処理フローの設計レビュー依頼)

管理ID: FZ-NARRATION-CHUNK-TTS-TRIAL-01 委任_01 Phase 0。依頼者=Fable(本ファイルはSonnetが用意した依頼素案。Opusへ渡すのはFable)。
発火条件: `PM_GOVERNANCE.md` 11-3 条件A(Family Z本文narratorの生成単位・接続フローの新設計)。**有料生成(Phase 1)はこのレビュー後のFable Goまで開始しない。**
Opusは採用可否を宣言しない(Production採用は人間ユーザーのみ)。Status=`TRIAL_DESIGN_PENDING_OPUS_A`。

## (a) 論点(限定。以下6点のみ)

1. **分割閾値・優先順の根拠と文学的連続性への影響**: 『narrator clipが100語超のときだけ、段落境界>文境界(引用途中を除く)で`ceil(語数/100)`分割、最小chunk25語、固定文字数分割なし』は『必要十分』か。閾値100語(既存`target_words`と同値)の根拠=語数別WPM(<30語127/30〜59語156/60〜99語160/>=100語163、Adv narrator 59 clip、短clipは端の無音比率で低く出る交絡あり、`EXISTING_SPEC_CHECK_01.md` §2)は、閾値の正当化として十分か。『告げ口心臓』の一人称独白でクライマックス手前(『I rushed in.』の前、『I talked louder.』の前)を切ることが緊張感・心理描写の連続性を損なうリスクと、より良い切断位置(例: 場面の転換語、文境界)の有無。
2. **既存Dialogue分割・Voice割当・速度仕様v2との整合**: narrator内部のみ分割し、voice≠narratorのclip・話者切替境界は不変とする設計が`plan_clips`/`plan_story_segments`、速度仕様v2(Adv narrator=後処理なし)、`target_rms`(preview+最初のstory clip由来)、Comment挿入位置(`comment_after_segment_ids`)と矛盾しないか。Advのみ対象でStdを除外する判断(Std narratorの6%減速とchunk化の相互作用回避)の妥当性。
3. **A/B同一性**: DESIGN_01 §4対応表。特に(i)各chunkのspec(clip_id/segment role/style)をAと同じnarratorとして生成する方法(出力ファイル名を元clipと同一にしrole判定を保つ)、(ii)Aの既存take(1b_s1 Trial生成物、Gate/HR状態未確認)と新規takeの比較にtake間ばらつき基準A_r2を置く構成で十分か、(iii)『各chunkは文脈なし』の影響(chunk語数49〜78語に対する妥当性)。
4. **Production非汚染と並行案件との競合回避**: 対象本文の2案((i)正式再生成`run_sf_prod_02`後に読取専用で再利用 / (ii)Trial 1b_s1)の比較と推奨((ii)先行)の妥当性。DEV dir限定、Production sinkのプロセス内redirect、PROTECTED_STORES/TREESのsha比較、別案件Z TTSとの直列化運用(DESIGN_01 §3)で、Production store・音声Store・公開ページ・案A配線作業との衝突を防げるか。
5. **P6B不採用方式との関係**: ER-003-B1-P6B(2-Macrochunk、日本語・`gemini-2.5-pro-preview-tts`、ユーザー不合格=声質差・接続不自然、単一call凍結`CURRENT_SPEC.md:2052,2065,2074`)に対し、本Trialは英語・`gemini-3.8-flash-lite-tts`・Aoede固定・同Style・chunk間0.2秒・RMS正規化。条件差は十分か。Xの直前Trial(OPEN-506)結果(境界音量差<=5.8dB、実発話-5〜7%)をZへ外挿してよいか。再導入にならないよう、不合格理由(声質の一貫性)を最重点の試聴項目にする設計(DESIGN_01 §5③)で足りるか。
6. **費用対効果**: Trial費用約12〜14円(上限30円)と、採用時の量産単価増(約+0.12〜0.2円/Advanced、+0.3〜0.6%)に対し、効果(実発話約5〜7%減速見込み、ただし聴感改善は未検証)が見合うか。段階運用(B_r1+A_r2のみ→必要時B_r2)の妥当性。Xの結果で0.2秒間でも実発話が遅くなる(追加無音ではなく発話そのものの遅さ)ことの含意(目的である『速さの改善』が地の文の聴感上の速さに効くか)。

## (b) 背景・事実(Opusが追加ファイルを読まなくて済む最小限)

- ユーザー原文: `docs/pm/delegation_log/2026-10-25_FX-FZ-CHUNK-TTS-TRIAL-02_USER.md` §3〜§8(既存のセリフ・話者切替分割は維持、地の文が長く続く区間のみ追加分割、chunk間0.2秒、既存の音量正規化・trim・結合を再利用、新規独自音声加工/Validatorを安易に追加しない、Production配線禁止、別案件へ混入禁止)。
- 現行Z構造: 同一Voiceが続く限り段落をまたいで1 clipに結合され(`er013_family_c_production_01.py:202-248`)、語数目安は`target_words=100/soft_max=120/hard_avoid=150`でhard_avoid超過時のみ自動2分割(同:251-326)。『告げ口心臓』Advはほぼ全部が地の文(約431語中429語narrator)で最長clip 135語/47秒。
- 数値(`EXISTING_SPEC_CHECK_01.md` §2): 現行run_sf_prod_01 Adv clip 135/12/2/118/91/73語。Trial 1b_s1 Adv(案A一人称)は141/5/2/118/148語。
- planner出力(`er026_output/family_z_dev_trials/fz_narration_chunk_01/chunk_plan_*_01.json`): 1b_s1は3 clip→6 chunk(78/63、69/49、74/74語、全て段落境界、文・引用の途中での切断0)。
- X Trial実績(参考): A→B実発話-4.6〜-6.3%、B0.2の段落間gapはAの自然gapとほぼ同じ、境界音量差最大5.8dB、欠落・二重なし(`TRIAL_RESULT_02.md`)。
- 費用見積: 約12〜14円/3 arm(`DESIGN_01.md` §6)。

### 読むファイル(この順で十分)
`EXISTING_SPEC_CHECK_01.md` → `DESIGN_01.md` §2〜§5 → `er114_fz_narration_chunk_trial_01.py`(`plan_clip_chunks`、`_candidates`)→ `chunk_plan_tth_1b_s1_adv_01.json`。

## (c) 参照すべき既存仕様のGrep確認欄
- `er062_family_z_structure_01.py:851-893`(build_flat_chunks/plan_clips)、`er013_family_c_production_01.py:202-326`(base segments/語数目安)、`er013_family_c_production_runner_01.py:670`(clip gap 0.5/0.2)、`er063_family_z_audio_01.py:49-64,835-862,1743-1796`(速度v2、narrator生成、run_assembly/gain)、`CURRENT_SPEC.md:1630,1692`(速度仕様v2)、`CURRENT_SPEC.md:2052,2065,2074`(P6B)、`docs/research/FX-PARAGRAPH-CHUNK-TTS-TRIAL-01/`(X Trial一式)。

## (d) 固定観点(`docs/pm/templates/OPUS_INDEPENDENT_REVIEW_BLOCK.md` 12観点を独立に評価)
そもそも必要か / より単純な構造(例: `hard_avoid_words`相当の閾値パラメータ変更のみ、または会話速度のようなnarrator限定の後処理減速との比較) / 既存処理の利用 / 取得済み情報の喪失・再探索 / 不要なLLM処理(本Trialは0) / 非決定性(takeノイズ) / Human Review増 / 不要Rewrite増 / コスト / retry・fallback・regenerationとの整合 / Production非汚染 / 未承認仕様の隔離。

## (e) 結論の返し方
『必要/不要』→『推奨構造(閾値・優先順の修正案)』→『リスク』→『代替案』の順で簡潔に。代替案の方が良ければ明示。

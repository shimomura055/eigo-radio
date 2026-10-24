# OPUS_REVIEW_REQUEST_01 (条件A: 新しい処理フローの設計レビュー依頼)

管理ID: FX-PARAGRAPH-CHUNK-TTS-TRIAL-01 委任_01 Phase 1。依頼者=Fable(本ファイルはSonnetが用意した依頼素案。Opusへ渡すのはFable)。
発火条件: `PM_GOVERNANCE.md` 11-3 条件A(本文TTSの生成単位・接続フローの新設計)。**Phase 2(有料)はこのレビュー後のFable Goまで開始しない。**
Opusは採用可否を宣言しない(Production採用は人間ユーザーのみ)。

## (a) 論点(限定。以下5点のみ)

1. **接続・音量方式**: 『chunkごとRMS正規化(target_rms=A値0.09149固定、peak≤0.95)+段落間0.5秒(Family C/Z `er013_family_c_production_runner_01.py:670`)+`np.concatenate`』は承認済み仕様の正しい再利用か。段落境界の無音として『0.5秒を足す(B)』vs『追加なし=各chunkのtrim margin残置のみ(B0)』のどちらを主とすべきか(A実測の段落境界gapは平均約0.62秒、B0≈0.5–0.6秒、B≈1.0秒)。
2. **A/B条件の同一性**: 『段落分割以外固定』は担保されるか(DESIGN_01 §3対応表)。特に (i) Aの入力は`tts_safe_news_en`で段落改行が畳まれた1続き文であること、(ii) segment_idを`full_story_partN`に揃えることでrole Gate(ASR judge・Connected Speech・Semantic Equivalence)を同一適用していること、(iii) Style文字列をA記録から取りsha256検証していること、に見落としはないか。
3. **WPM・ポーズ計測**: `total_wpm`・`articulation_wpm_300/500`・Δ全長=Δ発話時間+Δ無音時間の分解は『実発話速度』と『ポーズ増による見かけ減速』を分離できているか。A内でpart間total WPMが168〜194とばらつく中、単一takeのB-A差を解釈する方法として**分散基準arm(A_r2・B_r2、各約4.2円)**は妥当か。他に必要な統制はあるか。
4. **Production汚染の防止**: `redirect_production_sinks()`(4 sinkのプロセス内override+`append_telemetry_log`のwrapper)+出力dir構造でのreview-lock store分離+before/after sha256で、Production store/telemetryを汚染しないと言えるか。見落としているsink(ledger negative_cache、他のjsonl等)はないか。
5. **過去Trial/不採用方式の再導入**: ER-003-B1-P6B(2-Macrochunk、日本語・`gemini-2.5-pro-preview-tts`)は『Macrochunk AとBで声質差があり接続が不自然』でユーザー不合格→単一call凍結(`CURRENT_SPEC.md:2052,2074`、`er003_output/b1_p7a/A01/audio_validation.md:5-8`)。本Trialは英語・`gemini-3.8-flash-lite-tts`・段落単位・chunk別RMS・C/Z接続で条件が異なるが、**無断再導入に当たらないか**(ユーザー原文で明示された新Trialとして許容されるか)。chunk間声質差の評価設計(DESIGN §6①)は十分か。

## (b) 背景・事実(Opusが追加ファイルを読まなくて済む最小限)

- 対象: Family X『英国の電車マナー』Advanced=`b1b`(委任文の『Advanced(A2)』は誤り、a2=Standard。`EXISTING_SPEC_CHECK_01.md` §0)。A=承認済み完成音声(ユーザー試聴PASS・正式承認済み。変更禁止)。
- 本文3 segment=part1/2/3(各1 TTS call)を、段落10 chunk(4+3+3、`parts.json`のparagraph_count=10)に分けて生成するのがB。
- A実測(`a_side_measure_01.json`): 本文計428語/139.92秒、total 183.5 WPM、articulation(≥500ms無音除外) 201.3 WPM。part1 168.3/183.5、part2 192.1/213.6、part3 194.1/210.9。
- A側の自然な段落境界gap(`a_boundary_gaps_01.json`、faster-whisper small、整列不能0.0を除く6点): 0.50/0.84/0.72/0.46/0.66/0.54秒。文境界平均0.545秒。
- TTS: `gemini-3.8-flash-lite-tts`/Aoede/`speech_metadata_flash_lite`/STANDARD、style `fx_20261017` FULL_STORY(速度指示なし、b1bに減速後処理なし)。
- 費用: 1 take≈4.2円(TTS 3.5+ASR 0.7)、3 arm≈12.6円、上限50円。Phase 1実費0円。
- Phase 1実測済みの安全性証拠: unit test 14件PASS(fake TTS注入のdry-runでProduction store不変)、A再構築がA完成wavと最大差5.7e-5で一致(`rebuild_check_01.json`)、`PROTECTED_*`のsha256変化0。
- 計測定義は既存`measure_wpm_01.py`の転記(importするとmain()が走るため)。原本関数とのAST実行による数値一致をtest済み。

### 読むファイル(この順で十分)
`EXISTING_SPEC_CHECK_01.md` → `DESIGN_01.md` §3-§6 → `er113_fx_paragraph_chunk_trial_01.py`(`join_chunks`, `redirect_production_sinks`, `generate_chunks_phase2`, `measure_wav`, `rebuild_full_episode`)。

## (c) 参照すべき既存仕様のGrep確認欄

- `CURRENT_SPEC.md:2099`(scalar RMS)、`:2100`(headroom弁)、`:2079`(Dynamics不使用)、`:2052,2065,2074`(単一call・P-series chunk HISTORICAL)、`:2133`(A2限定の減速invariant)。
- `er013_family_c_production_runner_01.py:665-670`(story clip gain+gap)、`er063_family_z_audio_01.py:1722,1743`。
- `er020_tts_retry_local_rewrite_01.py::resolve_narrative_role`(segment_id→role)。

## (d) 固定観点(`docs/pm/templates/OPUS_INDEPENDENT_REVIEW_BLOCK.md` 12観点を独立に評価)

そもそも必要か / より単純な構造 / 既存処理の利用 / 取得済み情報の喪失・再探索 / 不要なLLM処理 / 非決定性(takeノイズ)/ Human Review増 / 不要Rewrite増 / コスト / retry・fallback・regenerationとの矛盾(chunk別retryは既存`PRODUCTION_MAX_TTS_ATTEMPTS=3`をそのまま使用、独自回避なし)/ Failure時の安全側(chunk失敗でB不成立→REJECTED/USER_DECISION_REQUIRED、Aは不変で目的要件=ユーザーが比較できる状態を可能な限り維持)/ 個別パッチでなく再発防止か。

## (e) 結論の返し方

『必要/不要』→『推奨構造』→『リスク』→『代替案』の順で簡潔に。代替案の方が良ければ明示。

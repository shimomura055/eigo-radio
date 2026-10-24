# TRIAL_03_RESULT_01 (ASR-OOV-HOMOPHONE-ROOT-CAUSE-01 委任_03、2026-10-24) 修正後E2W(Opus条件C OF-OOV-07/08/11)の実測

Trial専用・Production変更0・SSOT編集0。コード: `trial_direct_ledger_phoneme_01.py`(v3: `judge_e2w`/`whisper_position_check`追加)、test=`trial_direct_ledger_phoneme_03_test_01.py`(E2W 15件)+既存`..._02_test_01.py`(18件)=**33件PASS**。実費=約3.2円(BUDGET_LOG_01.md)。

使用モデル(Production routingと同一・最新世代の推奨系): TTS=`gemini-3.8-flash-lite-tts`(speech_metadata_flash_lite、voice=Aoede/Charon/Erinome)/Primary ASR=`gpt-4o-mini-transcribe`/独立エンジン=Production既存の`_connected_speech_equivalence_local_asr_text`(faster-whisper small、API 0)/第3エンジン(切り分け)=Azure Speech STT(PhraseListなし)。旧世代モデル使用なし。

## 1. 修正内容(OF-OOV-07/08)
- **fail-closed(OF-OOV-07)**: 独立エンジン(ローカルWhisper)の転写が None/空 → 不受理(`WHISPER_UNAVAILABLE`)。『矛盾しない』では受理せず(旧`uncertain_no_agreement`受理を廃止)、**位置の正の一致**のみ受理。単体test: None→不受理、空→不受理、他語→不受理、位置の語が欠落→不受理、本番関数が例外→Noneを返す経路→不受理(monkeypatch、API 0)、同じ同音語→受理、正準綴りをWhisperが書く→受理。
- **1語位置判定(OF-OOV-08)**: 文全体の`classify_asr_match`ではなく、揃えた正準語の位置(canonical token index)だけで判定。その位置が`equal`なら正準綴り一致、そうでなければ**両隣のトークンがWhisper側でも一致**している範囲にWhisper側がちょうど1語だけ入る場合のみ、その語がLedger読み(CMU代表発音rank0、3音素以上)と一致するかを見る。隣が崩れる・範囲が確定しない・2語以上は不受理(fail-closed)。他箇所の小さな差(slowly/quickly等)は無視される(test)。
- `judge_direct`(E2単独)は比較用に無変更で残置(採用候補ではない)。

## 2. 本run長segment再評価(OF-OOV-08、API 0。`trial_run_e2w_03_stored.py`、結果=`work/trial03_stored_e2w.json`)
対象: word_gacha run_wg_01の`gacha`を含む全segmentの全attempt(A2+B1b、計20 attempt)。うちPrimary非PASS(PASS系以外)の12 attempt。Whisper=Production同関数、47〜50秒のwavあたり約11秒(CPU、warm)。
| segment/attempt | Primary | E2単独 | E2W(位置1語) | Whisperの位置の語 |
|---|---|---|---|---|
| B1b(Adv) full_story_part3 attempt **1** | TRUE_CONTENT_MISMATCH | 受理 | **受理** | gotcha(AGREE_LEDGER_CMU_PRON) |
| B1b full_story_part3 attempt **2** | 同 | 受理 | **受理** | gotcha |
| B1b full_story_part3 attempt **5** | 同 | 受理 | **受理** | gotcha |
| B1b full_story_part3 attempt 3,4,6,7 | 同 | 不受理(NOT_SINGLE_REPLACE: gacha以外にも差) | - | 正しいNG |
| A2 full_story_part3 attempt 1 | 同 | 不受理(NOT_SINGLE_REPLACE) | - | 同attempt2は通常PASS |
| B1b in_one_line attempt 1 | 同 | 不受理(POST_CHECK_FAIL) | - | 別の差 |
- **E2が受理した3 attempt全てでE2Wも受理(3/3、長segmentで救済は消えなかった)**。Opusが懸念した『文全体の転写で矛盾扱いになり救済が消える』は、旧方式(文全体`classify_asr_match`)ではこの3件すべてが `TRUE_CONTENT_MISMATCH`(gacha以外の差で)になり救済0になること、**位置1語判定にすると保持される**ことを実測で確認した(`whisper_whole_sentence_class`列)。
- **時系列(Ledger登録)**: gacha entry(`4e8e014185b79c53`)`updated_at`=18:06:09、A2 topic_intro attempt保存と同時刻(topic_intro cascadeで作成)。救済対象segmentの開始推定時刻はすべて18:06:24以降(A2 full_story_part1以降、B1b part3は18:13:44)=**entryより後**で、OF-179(segment開始前凍結)を満たす。**最初の発生(A2 topic_intro、大文字Gacha、Primary段で既に通過)は救えない**ので、旧計算で含めていた topic_intro のAzure削減0.36円を除外した。
- **費用再計算(`cost_cf_03.py`)**: 実績38.58円 → E2W適用16.38円 = **-22.19円**(旧-22.6円から-0.4円)。内訳: B1b part3 8attempt→1attempt(TTS 7.36→0.91円、ASR 0.81→0.10円、Azure 15.04→0円)。LR候補生成・HR待ち・cooldown 600秒×2・人間承認の時間は別(attempt1の確定時刻18:15:02に対し、実際の確定は18:48:40=約33分短縮)。
- **限界(正直)**: 本runでE2が効いたのは、A2 topic_intro(大文字`Gacha`のentity扱い)がcascadeで先にLedgerへ登録してくれたため。小文字のみ・full_storyにだけ現れる語は、同一run内では最初のsegmentが救えない(Ledger登録はreactive)。

## 3. 実音声Trial(OF-OOV-11、`trial_run_e2w_03_paid.py`、結果=`work/trial03/trial03_result.json`)
30 clip(Trial用Ledger[work/trial02/ledger_trial.json]、各clipを`cl.install`で実コスト記録、再起動0)。voice: 正例はAoede 1/Charon 5/Erinome 4(X Adv/Z Dionysius=Charon、Z Selinuntius=Erinome)、負例はAoede 9/Charon 6/Erinome 5ほか。
### 3-1. 正例10(正準=読み上げ)
| 結果 | 件数 | 内訳 |
|---|---|---|
| ASRが正準語を書いた=救済不要(BASE_PASS) | 4 | gacha_charon、gacha_erinome、lyft_charon、kewl_erinome |
| 救済が必要で**E2Wが受理** | **5** | gacha_aoede(Whisper=正準綴りgacha)、thicc_charon、skool_charon、skool_erinome、phat_charon(いずれもWhisperが同じ同音語を位置に書き、Ledger読みと一致)。**Charon 3件・Erinome 1件を含み、Aoedeだけではない** |
| 救済が必要だが不受理 | 1 | thicc_erinome(Primaryが`sick`と書いた=別語の聞き違い。同音語ではないので設計どおり不受理) |
- 救済率: 救済が必要だった6件中 **5/6**(取りこぼし1件は誤受理ではない)。
### 3-2. 負例20(1音素違いの近い語を読ませた音声)
| 結果 | 件数 | 内訳 |
|---|---|---|
| 正しく不受理(E2/E2W共に) | **14** | tick、thing、skull、vat、fit、fad、pat、curl、coil、keel、laughed、gift、grinders、gaucho(ASRが実際の別語を書き、Ledger読みと不一致) |
| 既存判定でBASE_PASS(Primaryが正準語を書いた誤PASS。E2到達前の既存挙動) | 3 | lyft→lived、grindr→grander、gacha→gotta |
| **E2/E2Wが受理(誤受理)** | **3** | **skool→scold、skool→spool、kewl→cull**(Primary・ローカルWhisper・**Azure(第3エンジン、PhraseListなし)の3エンジンすべてが同音語school/coolと書いた**=`work/trial03_azure_arbiter/azure_arbiter_result.json`) |
- **誤受理3件の意味**: ASR 3エンジン全てが `school`/`cool` と書いたため、ASR証拠だけでは『TTSが実際に近い別語を読んだがASRが文脈(old school uniforms/late for school/texted cool)で寄せた』のか『TTSが同音語を読んだ』のか判別できない(私は耳確認不可)。Opus論点5のとおり**E2Wの限界(全エンジン共通の事前知識による誤りは防げない)**。E2Wが防げたのは今回0件(Whisperは同系統でPrimaryと同じ誤りをする。Phase 2のkewl/coal #1[Primary単独の誤り]では防いだ)。ここで使った負例は文脈が近い語を支持するため意図的に厳しい(実Productionで『Ledger語を別の近い語として読み違える』頻度は未測定)。
- E2Wが受理した計8件(正例5+負例3)のうち、**3件が誤受理の疑い(37.5%)**という数字は、この厳しい負例設定での上限値であり、実運用の誤受理率ではない。実運用の目安は、『TTSが近い別語に読み違える頻度』×『ASRが文脈で寄せる確率』で、前者は本Trialでは測っていない。

## 4. 費用効果・頻度・適用範囲
- 費用効果(修正後): 本run -22.19円(`cost_cf_03.py`)。頻度: 保存全データ188 run中1件(0.53%、X/Z系62 runに限ると1.6%)。期待値 0.12〜0.35円/記事(70円目標の0.2〜0.5%)。**費用効果は小さい。主価値はD(確定を約33分短縮)とHR Lock/人間承認の連鎖の回避(ユーザー手間)**。
- E2が効く組合せ(`E2_ACCEPTABLE_PAIRS_01.md`): 現Ledger 43 entryで1組(gacha/gotcha)。Trial用に追加登録した語(Lyft/Grindr/thicc/kewl/skool/phat)は本Ledgerには無い。
- Family別: **X**=voiceはAoede(Std)/Charon(Adv)で動作確認(正例は両voice)。**Z**=narrator Aoede、Selinuntius Erinome、Dionysius Charonで動作確認(Erinome正例skool_erinomeを含む)。**Y**=未配線のため配線時に再判定(Trialでの適用は対象外)。A/B/C=対象外。
- 独立エンジンのコスト: ローカルWhisperはAPI 0、約11秒/47秒segment(E2が受理候補になったときのみ実行)。

## 5. 限界(申請文へ必ず記載。`ADOPTION_NOTE_01.md`)
(1)3エンジン一致時は判別不能(誤受理3件が実例)。(2)WhisperはPrimaryと同系統で完全独立ではない。(3)各語の最初の発生は救えない(Ledgerはreactive)。(4)取りこぼし: low confidence(meink型)・同一語の複数回出現・差分が2語以上(本runのattempt 3,4,6,7)。(5)Ledger読み自体が二次情報(NAME_IN_CITED_PAGE)で、別候補の読み(kewl型/kuːl)を経由した受理は#52の範囲内。(6)正例n=10・実負例n=20は少数(合成)。

## 6. Status案(最終判定はFable)
- **VALIDATED_LIMITED(E2W形、位置1語・fail-closed)** を提案。根拠: 本run長segmentで救済保持(3/3、-22.19円、約33分短縮)、合成正例5/6、X/Z voice含む。限定: 誤受理3/20(ASR 3エンジン共通の同音語化=判別不能領域、厳しい負例設定)、費用効果は小さい。
- E2単独は不採用相当(Phase 2で誤受理を実測)。(B)(現状維持+telemetry)への切替条件に当たるのは『長segmentで救済が消える』場合だったが、**消えなかった**ため(B)切替の根拠にはならない。Production採用はユーザー判断(`ADOPTION_NOTE_01.md`の選択肢A/B/C)。

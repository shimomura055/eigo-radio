# 委任文: B-FAMILY-VOICES-POSITION-AND-EVIDENCE-SPEC-01

管理ID: B-FAMILY-VOICES-POSITION-AND-EVIDENCE-SPEC-01(ユーザー正式承認2026-09-17
に基づくProduction wiring)。報告はdocs/pm/RESULT_PACKET_VOICES_SPEC_01.md
(新規、★★★★報告ここから/ここまで、累積Full Report)へ。
docs/pm/ACTIVE_TASK_VOICES_SPEC_01.mdを一時ファイルとして使う(ACTIVE_TASK.mdは
使わない)。現在main=origin/main=e08099ba。

## 並行Agent注意(重要)
別のsonnet-workerがUSER-TEST-NEWS-CONVENIENCE-AI-01(通常News、
er014_output/user_test_news_convenience_ai_01/**、TTS/ASR、DECISION_LOG/
ARTIFACT_REGISTRY追記)を並行実行中。衝突回避:
- 音声共有ストア(er006_output/master_audio_store_01/manifest.json、
  pronunciation_ledger_01/ledger.json、
  audio_retry_cascade_prod_01/human_review_queue.jsonl、
  er011_output/attempt_history.jsonl)を書く段階(TTS/ASR/Ledger登録)の前に
  docs/pm/locks/audio_stage.lock(内容: 管理ID+ISO時刻)を作成。他タスクのlockが
  存在すれば60秒ごとにpoll(最大60分)。音声段階終了後に削除。lockはcommitしない。
  テキスト段階(仕様・Prompt・Validator・テスト・Writer再生成)はlock不要で先行
  してよい。
- SSOT(CURRENT_SPEC.md/DECISION_LOG.md/OPEN_ITEMS.md/ARTIFACT_REGISTRY.md/
  docs/pm/PM_GOVERNANCE.md)編集は最後にまとめ、編集直前にgit fetch origin→
  git merge origin/main --no-edit(rebase/force禁止)→編集→即commit→push。
  push拒否時はfetch+merge再試行。conflict発生時は自力解決せずSTOP報告。
  Productionコード(er012_*.py)のcommitも同様にfetch+merge後に行う。
- user_test/unified.html・user_test/human_review.htmlは変更しない。

## 背景
Personalized News A2(er012_output/b_family_a2_new_topic_production_01/
personalized_news_2v_a2/)はユーザー試聴NG(Voiceが調査・統計を語る=問題A、
立場が曖昧=問題B)。read-only仕様レビューdocs/pm/RESULT_PACKET_VOICES_SPEC_REVIEW_01.md
(必読、特に3〜7節・9節)で原因と候補A〜Fを整理し、ユーザーが以下を正式承認
(APPROVED_FOR_PRODUCTION)した。ただしGate 3完了までPRODUCTION_WIREDではない。

## 承認済み仕様(そのまま実装)
- A: Voiceは自分の経験・価値観・立場に徹する。
- C: Voice内の数字は原則その人物自身の経験に属する数字のみ許可。
  survey/external statisticsをVoice自身の論証材料にしない。
- F: 反対側の中心的懸念・反論は別VoiceまたはTension等に置く(既存Tension設計の
  趣旨を明文化)。
- E: nuance(自分の立場の中の迷い・葛藤)は許すが、相手側の中心論点まで自分の
  Voiceに抱え込ませない。
- 追加承認: (i) Analytical Leakage Checkへ「立場越境」検知field(例
  leak_position_blur)を2V/3V両schemaへ追加。(ii) Leakage flag残存時(MAX_
  ATTEMPTS到達後も残存)は自動でUSER_LISTENING_PENDING/音声化へ進めずSTOP
  (Acceptance Gate)。(iii) 前例踏襲だけを理由にflag残存記事をユーザー試聴へ
  流さない。
- 恒久原則としてCURRENT_SPEC B-Family Voices節(L678「体験claimの根拠付け」行の
  直後)へ新規行を追加(Voice数・テーマ非依存)。Fact attribution A'
  (fact_attribution_mode)は既定OFF据え置き、Cとの整合はCURRENT_SPECに
  「A'をONにする場合はCとの両立条件を別途設計する(現状OFF)」と注記。

## 必須項目(全て確認するまでPRODUCTION_WIREDとしない)
1. CURRENT_SPEC正式仕様追記(上記原則行+A'注記+Acceptance Gate)。
2. Writer Prompt反映: er012_b_family_voices_writer_generic_01.pyのVoice rules
   (L270-275付近)・Tension(L297-305付近)・_voice_card_block_text()(L411〜、
   数字許可条件=本人経験由来のみ)・2V/3V共通template(2V L496-678、3V相当箇所)。
   A2側(er012_b_family_voices_a2_production_01.pyのA2_KAI1_INSTRUCTION経由で
   run_writer_stage_genericを使う経路)にも同一原則が効くことを確認。
3. Voice Card / Tension整合(Tensionが「両者の合理性」を扱う場所であることを
   明文化、Voice本文からTensionへの誘導)。
4. Analytical Leakage Validator: build_leakage_schema_2v/_3v・
   run_analytical_leakage_check_2v/_3v・build_leakage_corrective_note_2v/_3vへ
   leak_position_blur(相手側の中心論点の抱え込み)を追加。leak_numbers_foreground
   の基準文言をCに合わせ更新(本人経験由来でない数字=flag)。
5. 残存flag時Acceptance Gate: runner(er012_b_family_production_runner_01.pyの
   main_b1_2v L1254/main_b1_3v L1119/main_a2_2v L1947、およびrun_writer_stage_
   genericの戻り値)で、MAX_ATTEMPTS到達後もflag残存なら結果jsonに
   leakage_residual=true+status=LEAKAGE_RESIDUAL_STOPを記録し、後続stage
   (comment/key_phrases/japanese_title/voice_check/tts/assemble/player)へ進めず
   終了する。既存のREVIEW_REQUIRED等の扱いは変更しない。手動override(引数等)は
   作らない。
6. 2V/3V両方との整合(3V経路はPrompt変更を含むため、既存
   ThreeVoiceByteInvarianceAgainstHeadTests等のbyte不変テストは意図的変更関数を
   除外対象に更新し、除外理由を報告。behavior不変性が必要な箇所は別途確認)。
7. retry/fallback/regeneration時も同一仕様(corrective retryのnoteに新field
   を含める、regen経路で古いschemaを参照しない)。
8. Fact attribution A'とのDangling Reference Check(A' OFFで全経路動作、A' ON
   でも例外なし、削除した参照が残っていないこと)。
9. regression: run_project_regression.py全件+er012*_test_*.py+新規テスト
   (2V/3Vそれぞれ: 新fieldがschemaに存在、統計文がleak_numbers_foregroundで
   検知、立場越境サンプルがleak_position_blurで検知、残存flag時にrunnerが後続
   stageへ進まない、free_address型の低リスク本文が誤検知されない)。既知FAIL3件
   以外の新規FAIL 0。
10. runtime evidence: Personalized News A2をmain_a2_2v()経路で再生成(既存
    Ledger再利用、Research再実行なし。stage: write_new_theme→comment→
    key_phrases→japanese_title→voice_check→tts→assemble→player)。Leakage 0件
    で通過した場合のみTTS以降へ進む(lock手順)。TTS/ASRはCURRENT_SPEC
    L1277-1280のcascade・Human Review Route、Human Review提示はPM_GOVERNANCE
    9-12(確認ページ、raw mp3直リンク禁止)に従う。player=user_test/unified.html
    形式URL、Playwright E2E(docs/pm/closeout_136_e2e/型)evidence保存。残存flag
    で止まった場合はその事実がAcceptance Gateのruntime evidenceになる(記事は
    STOP、報告)。
11. Personalized News B1(er014_output/four_type_observation_01/voices/audio/
    b1_2v_v2/b1b/article.md、既知flag残存のまま音声化済み): 新Validatorで
    offline再評価→flagありならmain_b1_2v()経路で再生成(Ledger再利用)し、
    Leakage 0件なら音声化・player・E2Eまで(lock手順)。flag残存ならSTOP。
12. AI hiring 3V B1/A2の新Validatorでのoffline再評価(判定のみ、regenerateしない、
    結果報告)。free_address B1/A2 regression(新Validatorで誤検知0を確認)。
13. DECISION_LOG(## B-FAMILY-VOICES-POSITION-AND-EVIDENCE-SPEC-01、索引+本体)、
    OPEN_ITEMS(OPEN-151行に本タスク結果を追記、Personalized News A2のStatus
    更新。新規問題があれば登録)、ARTIFACT_REGISTRY(Personalized News A2/B1行
    更新)、commit/push(明示add、git add -A禁止、wav禁止)。

## 制約
- 候補B(Narrator/Evidenceレイヤー新設)・D(1 Voice=1 Primary Positionの恒久
  ルール化)は不採用、実装しない。
- MAX_ATTEMPTS・Gate基準の緩和禁止。既存voice_fact_safety_gate_mode(既定OFF)は
  変更しない。
- Production Writerの既存承認原則(L678等)を削らない。
- 費用上限900円(PN A2再生成約120円、PN B1再生成+音声約250円、offline再評価約30円
  目安)。超過見込みならSTOP。
- 承認代行(Human Approval記録)禁止。

## STOP条件
新仕様が既存正式仕様と衝突/regressionで既存Production破壊/Dangling Reference
発生/PN A2またはB1が再生成後も残存flag(そのレベルはSTOP、他は続行)/TTS・ASRで
Human Review必要(確認ページ作成後STOP)/費用超過/git conflict/新たなProduct
仕様判断が必要。

## T-0
委任文を保存しcheck_delegation_prompt.pyを実行、結果1行記録(FAILでも継続)。
E-1/D-1/G-1/F-1/T-1従来どおり。

## E-1 実行コマンド全文
- python docs/pm/tools/check_delegation_prompt.py --file "docs/pm/delegation_log/B-FAMILY-VOICES-POSITION-AND-EVIDENCE-SPEC-01.md" --json-out "docs/pm/delegation_log/B-FAMILY-VOICES-POSITION-AND-EVIDENCE-SPEC-01_check.json"
- python -m pytest er012_b_family_voices_writer_generic_01_test_01.py -q
- python -m pytest er012_b_family_voices_writer_generic_01_variable_voice_count_test_01.py -q
- python -m pytest er012_b_family_voices_a2_new_topic_production_01_test_01.py -q
- python run_project_regression.py

## D-1 事前指定Read
- docs/pm/RESULT_PACKET_VOICES_SPEC_REVIEW_01.md
- docs/pm/RESULT_PACKET_PN_A2_PHASE_B_FIX1.md
- er012_b_family_voices_writer_generic_01.py(L270-275, L297-305, L411以降,
  2V template L496-678)
- er012_b_family_production_runner_01.py(main_b1_2v L1254, main_b1_3v L1119,
  main_a2_2v L1947)
- er012_b_family_voices_a2_production_01.py
- er012_b_family_voices_theme_personalized_news_a2_01.py
- er012_b_family_voices_writer_generic_01_test_01.py
- er012_b_family_voices_writer_generic_01_variable_voice_count_test_01.py
- er012_b_family_voices_a2_new_topic_production_01_test_01.py
- CURRENT_SPEC.md L652-720, L676-678, L586
- docs/pm/PM_GOVERNANCE.md 9-12, 18節
- OPEN_ITEMS.md OPEN-151

## G-1 SSOT編集方針
CURRENT_SPEC.md/DECISION_LOG.md/OPEN_ITEMS.md/ARTIFACT_REGISTRY.mdは全作業完了後
最後にまとめて編集。編集直前にgit fetch origin→git merge origin/main --no-edit。

## F-1 費用上限
900円。超過見込みならSTOP。

## T-1
不要(該当なし)。

## 報告項目(★ブロック内)
0.T-0 1.APPROVED_FOR_PRODUCTION反映(CURRENT_SPEC行の全文) 2.Prompt変更点
(before/after要旨、2V/3V/A2) 3.Validator変更点(新field定義文言・基準)
4.Acceptance Gate変更点(runner挙動・結果json) 5.regression(件数・既知FAIL・
新規テスト) 6.runtime evidence(PN A2: attempt数・Leakage結果・Fact Checker・
Ledger Deviation・TTS/ASR・Gate・player URL・E2E。PN B1: 再評価結果・再生成
有無・同上。AI hiring 3V再評価結果。free_address regression) 7.CURRENT_SPEC
8.DECISION_LOG 9.OPEN_ITEMS/ARTIFACT_REGISTRY 10.PRODUCTION_WIRED判定(必須
項目1〜13のチェックリスト、未充足があればPARTIAL/WIRING_INCOMPLETEと明記)
11.cost実測 12.Git SHA 13.ユーザー判断 A(仕様・Product・実装判断待ち、なければ
「なし」)/B(ユーザー試聴・品質確認待ち、完成player/確認ページURLが出た項目
のみ) 14.無変更証跡(user_test/*.html無変更、A2/B1 News経路er003_*無変更)/
事前指定外Read/並行衝突回避の記録(lock・待機時間)。

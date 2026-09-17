# RESULT_PACKET: B-FAMILY-VOICES-POSITION-AND-EVIDENCE-SPEC-01(累積Full Report)

管理ID: `B-FAMILY-VOICES-POSITION-AND-EVIDENCE-SPEC-01`(ユーザー正式承認2026-09-17に基づく
Production wiring)

★★★★報告ここから★★★★

## 0. T-0(委任文検証)

`docs/pm/delegation_log/B-FAMILY-VOICES-POSITION-AND-EVIDENCE-SPEC-01.md`を保存し
`check_delegation_prompt.py`を実行。結果=`FAIL`(「性質」キーワード欠落、「事前指定Grep
一覧+追記位置・更新位置の手順」セクション欠落、pytestコマンド行に絶対パス/長形式引数が
無い、の3件。固定ブロックE-1/D-1/G-1/F-1/T-1は全てOK)。ルールどおりFAILでも継続。
JSON: `docs/pm/delegation_log/B-FAMILY-VOICES-POSITION-AND-EVIDENCE-SPEC-01_check.json`。

## 1. APPROVED_FOR_PRODUCTION反映(CURRENT_SPEC行の全文)

`CURRENT_SPEC.md`「B-Family(Voices)Editorial Type」節、既存「体験claimの根拠付け」行
(旧L678)の直後へ新規行を追加した。行タイトル: 「Writer原則: Voiceの立場境界(A/C/F、
B-Family Voices共通、Voice数・テーマ非依存の恒久原則)」。全文はCURRENT_SPEC.md該当行を
参照(候補A/C/E/Fの内容、`leak_position_blur`新設、Acceptance Gate[MAX_ATTEMPTS到達後も
flagged残存時は`leakage_residual=True`+`status=LEAKAGE_RESIDUAL_STOP`で後続stage停止]、
Fact attribution A'との関係[既定OFF据え置き、C採用時の両立条件は別途設計]を1行にまとめて
記載。Status列は`APPROVED_FOR_PRODUCTION`→Gate 3配線状況は本Reportの10節参照、と明記)。

## 2. Prompt変更点(before/after要旨、2V/3V/A2)

`er012_b_family_voices_writer_generic_01.py`の2V/3V共通template両方(A2は`main_a2_2v()`が
同じ2V templateを`instruction`引数のみ変えて使うため自動適用):
- 「Evidenceは脇役であること・Voice内の数字は最大1つ」段落: before=「必ずその人/その立場の
  人々の実感に折り込み」→after=「かつその数字は必ずその人物自身が実際に経験した数値(自分が
  経験した回数・期間・費用等)に限る。survey/report/study等の外部統計を実感の代わりに使わない」
  へ明確化。
- 新規段落追加: 「Voiceは自分の経験・立場に徹すること、相手側の中心的懸念はTensionへ」
  (候補A/E/F)。
- Tension役割文言へ「両Voiceの中心的懸念を公平に受け止める場所でもある」旨の一文を追加
  (候補F明文化)。
- 禁止事項まとめへ2行追加(外部統計の論証材料化禁止/相手側中心論点の先取り禁止)。
- `_voice_card_block_text()`: supporting_evidence数字使用条件を「本人経験由来の数値が
  含まれる場合に限る」へ更新(調査・統計等の数字はここで使わない旨を明記)。

## 3. Validator変更点(新field定義文言・基準)

`VOICE_LEAKAGE_FIELDS`(2V/3V共有)へ`leak_position_blur`を追加(全7項目化)。定義文言:
「このVoiceが、自分の立場の中の迷い・葛藤(nuance)の範囲を超えて、他のVoice(相手側)が
中心的に抱えている懸念・反論そのものを、自分の中心的な主張として代弁していない場合PASS」。
`leak_numbers_foreground`の基準文言を「数字は本人の経験に属する数値であること」へ更新
(Tensionセクションでは人物個人の経験ではなく複数人の力関係を扱うため、Tension用の
`leak_numbers_foreground`は本人経験限定を適用しない旨を注記として区別)。Tensionの
field集合(`TENSION_LEAKAGE_FIELDS_BASE`/`_2V`)自体は無変更(position blurはVoice限定)。
是正メモ(`build_leakage_corrective_note_2v/_3v`)へ「立場境界」優先事項1行を追加。

## 4. Acceptance Gate変更点(runner挙動・結果json)

`run_pipeline_2v()`/`run_pipeline_3v()`: MAX_WRITER_ATTEMPTS(3)到達後もAnalytical
Leakage Check flagged項目が残存する場合、`final_result["leakage_residual"]=True`+
`final_result["status"]="LEAKAGE_RESIDUAL_STOP"`を記録(summary.jsonにも反映)。
`main_a2_2v()`/`main_b1_2v()`/`main_b1_3v()`のwrite_new_theme stageは既存の
`final_result.get("status")=="OK"`判定をそのまま使っているため、この値変更のみで自動的に
後続stage(comment/key_phrases/japanese_title/voice_check/tts/assemble/player)へ進めず
終了する。MAX_ATTEMPTS自体・既存Gate基準(`voice_fact_safety_gate_mode`等)は無変更。手動
override引数は追加していない。「前例踏襲でPARTIAL扱いとしユーザー試聴へ進める」という
従来運用は本Decision以降廃止(DECISION_LOG明記)。

## 5. regression(件数・既知FAIL・新規テスト)

`run_project_regression.py`: 2897件収集・2894 PASS・既知FAIL3件のみ
(`er003_test_p2j_investigate`のテスト件数照合arithmetic、本タスクと無関係、`er003_test_bad`
はモジュール自体が存在しないため対象外)・新規FAIL0件(summary:
`docs/pm/delegation_log/voices_spec01_regression_summary.json`)。ターゲットテスト94件
(`er012_b_family_voices_writer_generic_01_test_01.py`/`er012_b_family_voices_variable_voice_count_test_01.py`/
`er012_b_family_voices_a2_new_topic_production_01_test_01.py`)は個別実行でも全PASS
(post-push再実行でも同一結果)。`ThreeVoiceByteInvarianceAgainstHeadTests`の
`build_focus_module_block_3v`/`build_leakage_schema_3v`/`build_leakage_check_prompt_3v`/
`build_leakage_corrective_note_3v`/`run_pipeline_3v`は意図的変更のためbyte不変性チェック
対象から除外し、新原則文言の存在確認・`leak_position_blur`がVoiceセクションのみに追加され
field集合が変わらないことの確認・Acceptance Gate sourceの確認、という5件の新規契約テストへ
置換。`er012_b_family_voices_writer_generic_01_test_01.py`側の`VoiceCardNumberOptionalRenderingTests`
も新文言に合わせて更新。

## 6. runtime evidence

**Personalized News A2**(`main_a2_2v()`全stage、既存Ledger再利用・Research再実行なし):
write_new_theme attempt1で確定(2/3attemptを消費せず1回目でLeakage 0件PASS)。Analytical
Leakage Check: voice_a/voice_bとも7項目全PASS(`leak_position_blur`含む)。Fact Checker
A' verdict=`REVIEW_REQUIRED`(推薦システムの「切り替えられない」という一般化claimの地域・
サービス限定不足、既存の複合Voice帰属パターン範囲内でnon-blocking)。Ledger Deviation
Checker=`LEDGER_COMPLIANT`(Local Rewrite cycle1で1件のLedger外claimを検出・自動修正)。
新タイトル"The Same Feed, Two Different Mornings"/「同じフィード、二つの違う朝」
(config更新)。comment/key_phrases(`REDUNDANCY_PASS`)/japanese_title/voice_check/tts/
assemble/player全stage完走。TTS/ASR: 14 segment全て`OK`(Human Review Lock発生なし、
前回FIX-01で整合させたretry policyが今回も機能)。Assembly: `status=OK`、
duration=331.192秒、peak=0.95492、clipping=False。player.html+web export
(episode.mp3+segments35件)完成。Playwright E2E(headless Chromium、rawcdn.githack
commit`a54d0201`)実再生確認: `after_play_4s`(currentTime=3.03秒、paused=false、
readyState=4、error=null、duration=331.1915[Assembly実測と一致])、`after_seek`
(60秒seek+1.5秒待機でcurrentTime=61.44秒)、Key Phrase表示・英日タイトル表示確認、
consoleエラーは既知の無害な広告ブロック1件のみ。player URL:
`https://rawcdn.githack.com/shimomura055/eigo-radio/a54d0201f667d3fa56d6422ddeaa9fc998b0d49a/user_test/unified.html?src=er012_output/b_family_a2_new_topic_production_01/personalized_news_2v_a2/player.html&level=A2&en=The%20Same%20Feed%2C%20Two%20Different%20Mornings&ja=%E5%90%8C%E3%81%98%E3%83%95%E3%82%A3%E3%83%BC%E3%83%89%E3%80%81%E4%BA%8C%E3%81%A4%E3%81%AE%E9%81%95%E3%81%86%E6%9C%9D`。
cost実測: ¥73.94。

**Personalized News B1**(`main_b1_2v()`のwrite_new_theme stage、既存theme module
`er014_output/four_type_observation_01/voices/voices_theme_personalized_news_01.py`の
THEME_CONFIG・Ledger再利用): 事前offline再評価(新Validatorで既存音声化済み記事を判定のみ
実行)でvoice_b 6項目FAIL+tension 2項目FAIL(`leak_position_blur`自体はPASS、既存の統計
前景化・Discovery構文由来の残存)を確認したため再生成を実施。attempt1でLeakage是正retryが
発火(voice_b numbers_foreground/discovery_syntax、tension evidence_subject/
discovery_syntax)。是正後のattempt2で**Fact Checker A'が`FAIL`と判定**(Ledger内の記述
「短期テストでは政治的態度の測定可能な変化は確認されていない」が、2026-02-18公開の新しい
Nature論文の知見と矛盾するとWeb Searchで検出。Voice立場境界の仕様変更とは無関係な、既存
Ledgerの内容鮮度の問題)。既存retry機構どおりFact Checker FAILは即座に`NG_REVIEW_REQUIRED`
として記事を確定させず、追加のリトライは発生しない(MAX_ATTEMPTS自体の変更・Gate緩和は
していない)。本タスクの制約「Research再実行なし」によりLedger自体の更新は範囲外のため、
ここでSTOP(記事未確定、音声化未実施、既存音声[known flag残存のまま]は無変更のまま維持)。
新規Open Item`OPEN-166`として登録。cost実測: ¥12.32。

**AI hiring 3V B1/A2 offline再評価**(判定のみ、regenerateなし): B1
(`editorial_b_voices_3v_audio_trial_01/b1b/article.md`)は新Validatorで**0件PASS**
(`leak_position_blur`含む全項目、仕様レビューが「中リスク」と指摘したOwner Voiceの言及も、
自分の立場の中のnuanceとして判定されFAILしなかった)。A2
(`user_test_voices_a2_minimal_01/ai_hiring_3v_a2/a2/article.md`)はvoice_2
(narrator_analysis/discovery_syntax)・voice_3(numbers_foreground/discovery_syntax)・
tension(discovery_syntax/evidence_memorable)でFAIL(`leak_position_blur`自体は両記事とも
全Voice PASS)。両記事とも再生成は実施していない。

**free_address B1/A2 regression**: B1(`editorial_b_family_production_phase1_02/b1b/article.md`)・
A2(`editorial_b_voices_a2_free_address_04/a2/article.md`)ともに新Validator(7項目)で
**0件FAIL**(誤検知なし、`leak_position_blur`含む)。

offline再評価・runtime evidenceの生JSONは`er012_output/b_family_voices_position_spec01_offline_reeval_01/`
(offline5記事分)、`er012_output/b_family_a2_new_topic_production_01/`(PN A2新版)、
`er012_output/b_family_voices_position_spec01_pn_b1_regen_01*`(PN B1再生成試行)に保存済み。

## 7. CURRENT_SPEC

新規行1件追加(B-Family(Voices)Editorial Type節、1節参照)。既存記述は削除・変更なし
(追記のみ)。

## 8. DECISION_LOG

`## B-FAMILY-VOICES-POSITION-AND-EVIDENCE-SPEC-01`エントリを新設(索引1行+本体、
「## 参照元」節の直前)。Prompt/Validator/Acceptance Gate変更点・regression・PN A2/B1
runtime evidence・AI hiring 3V/free_address offline評価結果・並行タスク衝突の記録を含む。

## 9. OPEN_ITEMS/ARTIFACT_REGISTRY

OPEN_ITEMS.md: OPEN-151行へ本タスク結果を追記(PN A2新版runtime evidence要約、PN B1再生成
STOP理由、AI hiring 3V/free_address評価結果)。新規`OPEN-166`登録(Verified Fact Ledgerの
内容が時間経過で新しい外部研究と矛盾しうる問題、Blocking対象なし、`OPEN/DEFERRED`)。
ARTIFACT_REGISTRY.md: 「Personalized News A2(旧版)」行を`REJECTED_AS_CURRENT_OUTPUT`の
旧記録として保持し、新規「Personalized News A2(新版)」行を追加(player URL・E2E evidence
パス付き)。新規「Personalized News B1(既知flag残存)」行を追加(既存音声無変更・再生成
試行STOP理由を記載)。

## 10. PRODUCTION_WIRED判定(必須項目1〜13チェックリスト)

1. CURRENT_SPEC正式仕様追記: ✓
2. Writer Prompt反映(2V/3V/A2): ✓
3. Voice Card/Tension整合: ✓
4. Analytical Leakage Validator`leak_position_blur`追加: ✓
5. 残存flag時Acceptance Gate: ✓
6. 2V/3V byte invariance test整合: ✓(意図的変更5関数を除外・契約テストへ置換、除外理由を
   本Reportおよびテストdocstringに明記)
7. retry/fallback整合: ✓(corrective noteへ新原則反映、regen経路[main_b1_2v/main_a2_2v]は
   常に最新schemaを参照する既存実装のまま)
8. Fact attribution A'とのDangling Reference Check: ✓(既定OFF、A' ON時の両立条件は
   「別途設計」注記のみ、コードのdangling referenceなし)
9. regression: ✓(2897件中2894 PASS、既知FAIL3件のみ、新規FAIL0件)
10. runtime evidence: **PARTIAL**(PN A2新版=Leakage0件・完全E2Eまで到達=✓。PN B1=
    Fact Checker FAIL[Voice立場境界と無関係のLedger鮮度問題]でSTOP、音声化未実施=未充足。
    AI hiring 3V/free_addressはoffline判定のみで規定どおり=✓)
11. PN B1再生成: **未達**(Fact Checker FAILでSTOP、item10参照)
12. AI hiring 3V/free_address評価: ✓
13. SSOT/Git反映: ✓

**総合判定: `PARTIAL`**。Personalized News A2(ユーザーNG判定を受けた当該記事)は新仕様下で
Leakage 0件・完全なE2E再生まで到達し、基盤配線・Prompt・Validator・Acceptance Gate自体は
`PRODUCTION_WIRED`と判断できる。ただしPersonalized News B1は新仕様適用前の残存flag状態の
まま(再生成試行は仕様と無関係な既存Ledger鮮度問題でSTOP)であり、必須項目11が未達のため
全体を`PRODUCTION_WIRED`とは呼ばない。`PRODUCTION_WIRED`とするか、PN B1を現状(既知flag
残存のまま据え置き)で許容するかはユーザー判断を仰ぐ(13節参照)。

## 11. cost実測

Personalized News A2再生成: ¥73.94。Personalized News B1再生成試行: ¥12.32。
offline re-eval(AI hiring 3V B1/A2・free_address B1/A2・PN B1、計5記事): ¥2.47。
**合計¥88.73**(予算上限¥900以内、目安¥400以内にも収まる)。

## 12. Git SHA

- コード+テスト+CURRENT_SPEC+delegation log: `9c642f16623db3ce80b734f3374ed8ae2015ed9d`
- Personalized News A2再生成+B1再生成試行+offline re-eval成果物: `a54d0201f667d3fa56d6422ddeaa9fc998b0d49a`
- SSOT反映(DECISION_LOG/OPEN_ITEMS/ARTIFACT_REGISTRY)+E2E evidence: `ec4b13bb16b3d9446c3b25105923fcfc16517a76`
- いずれもpush済み(`origin/main`と一致)。

## 13. ユーザー判断

**A(仕様・Product・実装判断待ち)**:
1. Personalized News A2新版(Leakage0件・完全E2E)をユーザーが試聴し、当初のNG判定
   (`REJECTED_AS_CURRENT_OUTPUT`)が解消したと判断するか。
2. Personalized News B1は新仕様下での残存flag状態のまま据え置く(現状維持)か、それとも
   Ledger内の古い記述(OPEN-166)を別タスクで再Researchしたうえで改めて再生成するか。
3. `OPEN-166`(Ledgerの内容鮮度問題)への恒久対応方針(定期再検証ルールの新設 vs 現状の
   偶発検出時のみ対応する運用の維持)。
4. 本タスク全体を`PRODUCTION_WIRED`として確定するか(PN B1未達のまま)、それとも`PARTIAL`
   のまま次タスクでPN B1対応を継続するか。

**B(ユーザー試聴・品質確認待ち)**:
- Personalized News A2新版: `https://rawcdn.githack.com/shimomura055/eigo-radio/a54d0201f667d3fa56d6422ddeaa9fc998b0d49a/user_test/unified.html?src=er012_output/b_family_a2_new_topic_production_01/personalized_news_2v_a2/player.html&level=A2&en=The%20Same%20Feed%2C%20Two%20Different%20Mornings&ja=%E5%90%8C%E3%81%98%E3%83%95%E3%82%A3%E3%83%BC%E3%83%89%E3%80%81%E4%BA%8C%E3%81%A4%E3%81%AE%E9%81%95%E3%81%86%E6%9C%9D`

## 14. 無変更証跡/事前指定外Read/並行衝突回避の記録

**無変更証跡**: `git diff --stat 9c642f16~1 ec4b13bb -- user_test/unified.html
user_test/human_review.html er003_v1_n3_01_tts_generate.py er003_v1_n3_01_assemble.py`は
空(無変更)。既存B1/3V固定記事経路(`main_a2()`/`main_b1_3v()`の既存stage、`main()`の
level="b1"/"a2"分岐)・A-Family経路は無変更(byte invarianceテストで確認済み)。

**事前指定外Read(理由付き)**: (1) `er012_b_family_production_runner_01.py`の
`run_writer_stage_generic`呼び出し箇所全体(main_b1_2v/main_b1_3v/main_a2_2v)——事前指定は
L1254/L1119/L1947付近のみだったが、Acceptance Gateの影響範囲を正確に把握するため周辺stage
呼び出しコードも確認。(2) `er014_output/four_type_observation_01/voices/voices_theme_personalized_news_01.py`・
`run_voices_2v_b1_v2.py`——PN B1の実際のtheme module/生成経路が事前指定になく、探索して
発見した(main_b1_2v()の呼び出しに必要)。(3)
`er012_output/editorial_b_family_production_phase1_02/b1b/article.md`(free_address B1)——
DECISION_LOGレビュー時に発見した実在パス、事前指定は具体パス未記載だったため探索。

**並行衝突回避の記録**: `docs/pm/locks/audio_stage.lock`は開始時点で存在せず(先行タスク
`USER-TEST-NEWS-CONVENIENCE-AI-01`が既に完了・commit済みと確認)、japanese_title stage
実行前に本タスクの識別子で新規作成、Personalized News A2全stage完了後に削除。**ただし
Key Phrase選定stage(`key_phrases`、text stageと想定していたが実際にはMaster Audio
Store/Pronunciation Ledgerへの参照・登録を伴う実装だった)をlock取得前に実行してしまい**、
同時並行していた別タスク(`USER-TEST-NEWS-CONVENIENCE-AI-01-FIX-01`)のcommit(`86cbd93d`)
に本タスクの追記分(manifest.json/ledger.json/attempt_history.jsonl等の追加エントリ)が
混在した(共有working tree/共有git checkoutのため)。`git diff --stat`で追記のみ(削除なし)
であることを確認し、データ破損・キー競合は無かった。相手タスクの委任文でも同一事象が独立に
報告・確認されている。加えて、DECISION_LOG.md編集時に相手タスクの未commit編集と同時に
ファイルが存在する状態を確認したが、Editツールの完全一致置換により上書き事故は発生せず、
最終的に相手タスクのcommit(`58885794`/`3847e97e`)後に自分のcommitが正常にfast-forward
された(共有ローカルリポジトリのため、相手のcommitが自分のブランチ先端を直接進める形に
なった)。**教訓**: 本環境では複数タスクが同一working directory/同一ローカルgit checkoutを
共有しており、`docs/pm/locks/audio_stage.lock`が対象とする音声共有ストアだけでなく、
SSOTファイル自体・Key Phrase選定のような一見text-onlyに見えるstageも衝突源になりうる。
恒久対応(worktree分離等)はFable/ユーザー判断。

★★★★報告ここまで★★★★

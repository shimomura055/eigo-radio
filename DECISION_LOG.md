# DECISION_LOG — 確定した意思決定の索引

**管理ID: ER-PM-001**
**最終更新: 2026-09-03(ER-011-NO18-CONNECTED-SPEECH-READING-RESOLVER-PRODUCTION-WIRING-08、ユーザー正式決定によりOPEN-107のEnding-Clarity fallbackをProductionから撤回(`WITHDRAWN`)し、Trial-07でVALIDATED判定済みのB1 Connected Speech Validator・A2 Reading ResolverをProduction配線した(`PRODUCTION_WIRED`)。既存regression(English 57件・Japanese 35件他)全PASS、新規regression 15件全PASS(セッション前から存在する無関係な既存失敗2件をgit stashで切り分け確認)。No.18のB1 `comment_2`/`comment_3`・A2 `comment_1`が、review_lockの累積予算超過によるlockをapprove_regenerate()で解除した上での実Production呼び出しにより、実際のTTS/ASR出力に対して新Validatorで解決することを確認(OPEN-110/OPEN-111解消)。No.18 A2/B1が今回初めて両レベルとも完成(B1 351.324秒・A2 347.338秒、いずれもclipping無し)。詳細は本ファイル該当エントリ参照)。2026-09-03(ER-011-CONNECTED-SPEECH-AND-A2-READING-TRIAL-07、Track A: ASR差分を即座に「TTS誤発音」とせず、語境界のconnected speech[音の弱化・融合・再分節]として説明可能かを判定する候補ロジックを3パターン[歯擦音連続/破裂音連続/再分節]限定でTrialし、実データ3件[studies suggest/opened to/survey suggest]を正しく分類、3件の陰性対照ケースでfalse acceptなしを確認して`VALIDATED`と判定(OPEN-107仕様変更なし)。Track B: A2 OPEN-111について、前回[Trial-06、全文LLM自由生成、REJECTED]とは異なる新方式(既存pykakasi機械変換の差分位置だけを検出し、その漢字の読み候補をpykakasi辞書から取得してLLMに1つだけ選ばせる、自由生成させない)をTrialした結果、`comment_1`は1回のLLM呼び出しで解消し、他正常segmentへの副作用は0件(差分がない箇所にLLMが触れないため構造的に副作用なし)、コストはTrial-06比で大幅に低い(概算¥0.01〜0.04/記事)ことを確認して`VALIDATED`と判定(単発呼び出しの非決定性は明記)。両TrackともProduction配線は一切行っていない。詳細は本ファイル該当エントリ参照)。2026-09-02(ER-011-NO18-B1-LISTENING-AND-A2-OPEN111-READING-TRIAL-06、B1`comment_2`/`comment_3`/`opened`(OPEN-107参考比較)について、canonical全文・TTS入力・各attemptのASR結果・実音声・対象語前後の単語を人間が試聴確認できるArtifactを作成(文面変更・Validator変更・retry追加・新fallback追加はいずれも実施せず)。A2 OPEN-111について、Writerとは別の「Reading担当」役割による文脈込み全文ひらがなcanonical reading方式をA2限定でTrialし、「後/あと」問題自体は解決できることを確認したが、Reading担当自身が無関係な新しい読み誤りを2件(本番PASS中の正常segmentを含む)発生させたため`REJECTED`と判定(コストは1記事あたり概算¥0.8〜1.6で問題なし、品質面の理由)。Production配線は一切行っていない。詳細は本ファイル該当エントリ参照)。2026-09-02(ER-011-NO18-OPEN109-110-FINAL-CLOSEOUT-04、OPEN-107のEnding-Clarity fallbackについて、検出ロジック(y→ies不規則複数形・複数語replace diffの語単位分解)と配線範囲(B1 Comment segment、`voice01.generate_charon_english`経路)の2つのgapを是正し(regression 20件PASS)、B1`comment_2`を実際にProduction経路で再生成した結果、通常3attempt全NG→fallback実発火(初のProduction実発火確認)も、fallback自体は`study`[単数形]発話を解消できず`comment_2`は未解消のまま。`comment_3`("survey"→"surveys")はraw pipeline診断(5条件×3attempt)を実施し、「複合主語構文で動詞に直接隣接する名詞の数が不安定になる」という仮説を得たが方針決定はせず。OPEN-109は、精密化済みLedgerからA2記事をProduction正式Writer pathで再生成した結果fact_verdict=`PASS`・ledger_status=`LEDGER_COMPLIANT`となり(B1Bより精度指摘が少ない)、Support/Key Phraseも再生成しPASS、A2記事テキストは完成・確定。続くA2 Audio Stage実行で`comment_1`(日本語、「後」/「あと」の孤立漢字異読み、CURRENT_SPEC.md記載済みの既知の残存限界の新実例)が新規発見されAudio Validation Gateが正しくblock、新規OPEN-111として追加。再発防止としてCross-Level Consistency Check(A2/B1片側修正でのcloseを禁止するSSOT運用ルール)をCURRENT_SPEC.mdへ新設。A2/B1とも episode assembly未完成のまま。詳細は本ファイル該当エントリ参照)。2026-09-02(ER-011-NO18-OPEN107-PRODUCTION-WIRING-AND-FINAL-AUDIO-03、ユーザーがEnding-Clarity fallback[OPEN-107]を正式承認、B1 News本文5segmentへProduction配線(`er011_ending_clarity_fallback_01.py`、regression 13件PASS、実Production call site統合、CURRENT_SPEC.mdへ`PRODUCTION_WIRED`記載)。ユーザー指定のB1B Point One本文2文の個別差し替えを反映し、既存公式QA工程を再実行(いずれもnon-blocking)、Support/Key Phraseも再生成しB1Bテキストを完成・確定(`RESOLVED`)。No.18 A2/B1 Audio Stage(同期TTS)を実行した結果、B1は13segment中11件・A2は14segment中13件がOKとなったが、B1`comment_2`/`comment_3`(新しい単数/複数形TTS誤発音、OPEN-110新規)・A2`full_story_part1`(STOPPED)がAudio Validation Gateにより正しくblock。加えてA2記事本文がLedger精密化前の記述(Pew丸め表現・出典未確認の"hard-to-resist habit")を含んだままであることを新たに発見し(OPEN-109新規)、A2 Audioの最終化を保留。詳細は本ファイル該当エントリ参照)。2026-09-02(ER-011-NO18-OPEN108-LEDGER-REFINE-AND-OPEN107-ENDING-FALLBACK-TRIAL-02、Track A[OPEN-108]: No.18 B1BのFact Checker FAILの原因を調査した結果、Research Layer抽出段階で混入した不正確なLedger記述(F-011「hard-to-resist habit」がPew報告書本文に実在しないことを独立2回のWebFetchで確認、F-009の「約40%」丸めも実際は42%/25%/24%/56%の内訳と判明)だったと特定。Fact Checker自体は変更せず、Verified Fact Ledgerをsource-groundedに精密化した上で既存Production正式Writer pathからB1Bを1回だけ再生成した結果、fact_verdict=REVIEW_REQUIRED(non-blocking)・ledger MINOR 1件のみとなりFAIL解消、Support/Key Phraseも再生成しPASS、OPEN-108は`RESOLVED_PENDING_USER_TEXT_REVIEW`。Track B[OPEN-107]: 通常segmentは変更せず通常retryでもNGが続いたsegmentだけにEnding-Clarity instructionを追加するfallback候補を隔離Trial(Production関数呼び出し時のみ一時monkeypatch、恒久変更なし)。結果はcondition依存で一様でなく(raw pipelineの完全文+文脈条件はNormal 2/3→Ending-Clarity 1/3で悪化、実Production相当条件[Batch API+retry cascade]はNormal 0/3→Ending-Clarity 2/2で大幅改善)、`USER_DECISION_REQUIRED`のまま維持。両TrackともNo.18の個別ハードコード修正は一切行っていない。詳細は本ファイル該当エントリ参照)。2026-09-02(ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01、No.18で発見された3件の問題(Key Phraseの文脈依存人称表現・5件相互の意味重複・Pointが重複していなくても新しい価値を持たない場合がある)を、個別のNo.18修正ではなく汎用Production仕様として改善し、単体テスト26件追加(全125件PASS)、正規Production経路からNo.18を再生成(A2完成、B1はFact Checker FAILでNG_REVIEW_REQUIRED、既存policy通り)。OPEN-107はProductionと分離したDiagnostic Trialで原因範囲(完全な一文のprosodyに起因、断片は12/12正解・完全な一文は6件中2件で誤発音)を診断したが新Production仕様は未採用のままUSER_DECISION_REQUIRED。詳細は本ファイル該当エントリ参照)。2026-09-02(ER-011-NO18-DISCOVERY-WHY-FULL-PRODUCTION-RUN-01、No.18「Why Is It So Hard to Ignore a Notification?」をDiscovery/Why型としてNo.9までのProduction Wired仕様のみで正式Production実行。A2は完成[378.634秒、USER_FINAL_AUDIO_REVIEW_REQUIRED]、B1は新規TTS失敗モード[OPEN-107、`USER_DECISION_REQUIRED`]によりepisode assembly未完成。詳細は本ファイル該当エントリ参照)。2026-09-02(ER-010-NO9-FINAL-APPROVAL-CLOSEOUT-AND-FULL-STATUS-AUDIT-28、ユーザーがNo.9 A2[354.162秒、function-word reduction版]・B1[335.754秒、既存承認維持]をいずれも最終承認。No.9関連management ID全24件をRepository横断監査し、Trial仕様・採用/却下/deferred仕様・修正bug・Open Item・one-off例外を完全棚卸しした結果、未処理USER_DECISION_REQUIRED・Dangling Reference・未配線APPROVED仕様は0件を確認(CURRENT_SPEC.mdの「Formatting禁止」行の記録漏れ1件のみ発見・補完、コード自体は既にPRODUCTION_WIRED済み)。OPEN-103は恒久課題[Gemini TTSの`default`誤発音]自体を`DEFERRED / NON-BLOCKING`のまま維持しつつA2側Blockingの解消を追記(恒久課題自体はCLOSEしない)。No.10以降のSSOT補助資料`ER-010_NO9_FINAL_CLOSEOUT.md`を新規作成。No.9 A2/B1を`FINAL USER APPROVED / CLOSED`、No.9開発全体を`CLOSED WITH DEFERRED OPEN ITEMS`[OPEN-100・OPEN-103恒久課題は意図的deferred維持]として正式close)。2026-09-02(ER-010-NO9-FUNCTION-WORD-REDUCTION-PRODUCTION-WIRING-AND-A2-FINAL-27-R1、Trial 26で検証したfunction-word/article reduction原則をユーザーが正式採用し、`KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX`(Primary)・`KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION`(Fallback、Minimalを起点に構築されるため自動適用)へProduction配線。Dangling Reference Check・既存27テスト回帰・新規9テストいずれも全PASS。実Production path(Trial専用scriptではない)から「a catch」+article fixture3件[a chance/an idea/the answer]+非function-word系既存Key Phrase3件[guilt tipping/push back/starting point]の計7件を生成し全件Attempt 1 PASS、article/function-wordを含まないKey Phraseへの悪影響は確認されず。「a catch」はduration 1.011秒・「a」区間0.08秒[旧0.28秒の約29%]まで短縮、`kp4_en.wav`を実際に差し替えNo.9 A2を再Assembly[354.162秒、clipping無し、Key Phrase 4は1回のみ想定位置]。`default`[kp2]・他Key Phrase[kp1/3/5]は無変更をsha256で確認、OPEN-103は無変更のまま。CURRENT_SPEC.mdへ正式追加・OPEN-106は`RESOLVED / CLOSED`。完成音声+全文script+「a catch」新旧比較のUser Listening Artifact提示、`USER_FINAL_AUDIO_REVIEW_REQUIRED`)。2026-09-01(ER-010-NO9-A2-KEYPHRASE-ARTICLE-REDUCTION-DIAGNOSTIC-AND-TRIAL-26、No.9 A2 Key Phrase「a catch」の冠詞"a"が不自然に強く・長く発音されるとのユーザー試聴フィードバックを受け診断。現行Production Key Phrase Minimal instructionにfunction word[冠詞等]を弱く読む原則が存在しないことを既存仕様監査で確認[実装漏れではなく新規safeguard候補]。既存文言を一切変更せず末尾に一般原則を1文追加しただけの隔離Trialを実施し[「a catch」固有のhardcodeなし]、Attempt 1でmachine PASS。実測envelope解析で「a」区間が0.28秒→0.07秒[約1/4]・peak RMSがcatch本体を下回る関係へ好転・フレーズ全体が約34%短縮したことを客観確認。Current Production版とTrial版を並べたUser Listening Artifactを提示、Production一般仕様への正式採用は行わずOPEN_ITEMSで`USER_DECISION_REQUIRED`。`default`[OPEN-103]・Attempt 4 one-off固定assetは無変更)。2026-09-01(ER-010-NO9-A2-ATTEMPT4-ONEOFF-FINAL-AUDIO-25、ユーザー正式決定によりTrial 21 ENGLISH_LOCK attempt=2[通し4回目=「Attempt 4」]をNo.9 A2 `kp2_en`限定のone-off固定assetとして採用。machine validator上の`TTS_FAILURE`判定は書き換えず`one_off_fixed_asset_override`として追記、Production Episode Assembly Gateの既存承認メカニズム[`human_approved_segments.json`]で正式にunblock。ローカルdisfluency QA実施後、No.9 A2 episodeを実際にAssembly[355.002秒、clipping無し]し完成、完成音声+全文scriptのUser Listening Artifactを提示、ユーザーの最終試聴承認待ち。OPEN-103は恒久課題としては`DEFERRED / NON-BLOCKING`のまま、A2完成のBlockingは解消)。2026-09-01(ER-010-NO9-A2-DEFAULT-FIXED-ASSET-FINALIZATION-23-R1、`default`個別対応として新規TTS Trialなしで既存固定音声資産を探索。既存`kp2_en.wav`は実ASR再確認により「別のKey Phrase[Guilt tipping]との取り違え」と確定。No.9 A2/B1BのFull Story本文に地の文として"default"が登場する箇所を新規発見し、既にRESOLVED(B1Bはユーザー承認済み)のsegmentからfaster-whisper[ローカル無料]のword-level timestampで単語単位を切り出した候補3件を作成。いずれもローカルASRは"default"のみを検出する一方、Production ASRは短い誤認識語を文頭に付け足す既知のASR挙動が見られ、断定できないため人間の試聴判断に委ねる形でArtifact提示。Trial 21 Attempt 3/4は使用せず、新規TTSも行っていない。A2 Assemblyは未実施、OPEN-103は`USER_DECISION_REQUIRED`)。2026-09-01(ER-010-NO9-KEYPHRASE-MINIMAL-ENGLISHLOCK-PRODUCTION-WIRING-22、ユーザー正式決定「Minimal instruction最大2回→NGならEnglish language lock付きMinimal最大2回(合計最大4回)」をKey Phrase英語Component生成のProduction正式初回経路へ全面配線[`generate_key_phrase_component_verified()`書き換え、旧`ENGLISH_STYLE_PREFIX`標準経路起点の構成から離脱、他segmentのTTS retry上限3回は無変更]。Runtime evidence取得: 実TTS Case A["push back"、Minimal Attempt 2でPASS、fallback未使用]・境界モックCase B/C[Minimal 2回NG→English Lock即PASSへ実際に遷移、cumulative_tts_attempts=3で二重会計なし]。既存18テスト全PASS(新規5件追加)。`default`は個別例外として一般仕様から分離、OPEN-103は`DEFERRED / NON-BLOCKING`、Trial 21のEnglish Lock Attempt 1/2をNo.9限定fixed asset候補としてユーザーへ提示[未採用]。既存4件[kp1/3/4/5]は旧経路で既にRESOLVED済みのため無変更のまま)。2026-09-01(ER-010-NO9-KEYPHRASE-ENGLISH-LOCK-FALLBACK-TRIAL-21、Key Phrase「default」1語を対象に、量産候補retry仕様[Minimal instruction最大2attempt→NGならEnglish language lock付きMinimal最大2attempt、合計最大4attempt]を隔離Trial。4attemptすべて不合格(Minimal 2回=日本語カタカナ「デフォルト」、English Lock 1回目="defaut"[英字だが誤スペル]、English Lock 2回目=日本語カタカナへ逆戻り)。duration anomalyは4回とも無し(改善は維持)だが、content accuracy失敗(非英語発話)はEnglish lockを追加しても解消せず、Trial判定は`REJECTED`。Production instruction・review lock・retry budgetはいずれも無変更、OPEN-103は`USER_DECISION_REQUIRED`のまま維持)。2026-09-01(ER-010-NO9-KEYPHRASE-MINIMAL-INSTRUCTION-MINI-TRIAL-20-R2、No.9 A2正式Key Phrase5件[guilt tipping/default/push back/a catch/starting point]でMinimal instruction Mini-Trial[各語1回→NGのみ最大2回retry、最大3attempt]を実施。5件中4件[guilt tipping/push back/a catch/starting point]はAttempt 1でPASS[duration anomaly無し、Validator NORMALIZED_MATCH/EXACT_MATCH]。`default`は3attemptとも誤発音(FAIL)で再現性を確認: 前回Trialの英語内誤認識["Dieselt"]とは異なり、今回は3回とも発話言語自体が英語からずれた[デフォルト/デフォルト/默认]。duration anomaly自体は0件で解消したが、content accuracy失敗が形を変えて残存。Production instruction・review lock・retry budgetはいずれも無変更、OPEN-103は`USER_DECISION_REQUIRED`のまま維持)。2026-09-01(ER-010-NO9-KEYPHRASE-MINIMAL-INSTRUCTION-TRIAL-AND-RETRY-ACCOUNTING-FIX-19、Key Phrase英語音声Minimal instruction Trial[OPEN-103、opt outはVALIDATED相当・defaultは単発試行でTTS_FAILURE]・review lockネスト二重会計バグ修正[OPEN-105、CLOSED])。2026-09-01(ER-010-NO9-B1-APPROVAL-AND-OPEN103-TTS-DIAGNOSTIC-18、No.9 B1音声のUser Approval記録・完成音声提示ルールの再確認・OPEN-103 TTS request payload監査)。2026-09-01(ER-010-NO9-A2-KEYPHRASE-AUDIO-ISSUES-103-104-17、OPEN-103/104個別診断・OPEN-104実装バグ修正)。2026-08-31(ER-010-NO9-STORYTELLING-NOJARGON-PRODUCTION-WIRING-06、Storytelling First/No JargonをProduction初回Writerへ正式実装・Meaning First REJECTED確定・No.9新規再生成候補をProduction経路から取得。2026-08-31、ER-010-N1-SPEC-LIFECYCLE-PRODUCTION-GATE-04、仕様Lifecycle・Dangling Reference Checkの正式導入をDecisionとして記録。2026-08-29、ER-008-N8-FINAL-CLOSEOUT-24、地名/施設名CompressionのNo.8正式反映・Writer Point Balance prompt強化・cost計算モジュールの単価バグ修正・Stephen Reicher発音PASS確定)**

**区分について(2026-08-17追記)**: 以下のDecisionは「サービス・生成仕様」
(番組の聞こえ方・記事の作られ方そのものに関わるもの)と「Implementation
Hardening」(実装の堅牢化。サービス仕様は変えず、コードの安全性・
再発防止のみを目的とするもの)を区別して記載する。各エントリの見出しに
区分を明記する。

確定した意思決定と、その理由・根拠を記録する。個別のDecision Record原本
(`er003_output/p2i/ER-003-P2I_decision_record.md`等)は削除せず、本ファイルは
それらへの**索引**として機能する。未決事項は書かない(→[OPEN_ITEMS.md](OPEN_ITEMS.md))。

各Decisionは最低限、Decision ID／日付／内容／状態／採用理由／比較した
選択肢／却下理由／根拠レポート／commit／影響するCURRENT_SPEC項目を持つ。

---

## ER-011-NO18-CONNECTED-SPEECH-READING-RESOLVER-PRODUCTION-WIRING-08: OPEN-107撤回、B1 Connected Speech Validator・A2 Reading ResolverのProduction配線、No.18 A2/B1完成

- **日付**: 2026-09-03
- **区分**: サービス・生成仕様(OPEN-107撤回はユーザー正式決定、B1/A2それぞれのAudio Validator仕様変更)。

### 背景・スコープ

前回(ER-011-CONNECTED-SPEECH-AND-A2-READING-TRIAL-07)で`VALIDATED`と判定したB1 Connected Speech Validator・A2 Reading Resolverの2方式について、ユーザーが正式にProduction採用を決定した。あわせて、OPEN-107のEnding-Clarity fallbackはProduction仕様として撤回(`WITHDRAWN`)することも決定した。本Decisionは、(1)OPEN-107撤去、(2)B1 Connected Speech ValidatorのProduction配線、(3)A2 Reading ResolverのProduction配線、(4)No.18 A2/B1のAudio Stageを新仕様下で通し直し実際のepisodeを完成させること、を実施する。

### 1. OPEN-107撤去

`er003_v1_n3_01_tts_generate.py`から`import er011_ending_clarity_fallback_01 as ending_clarity`を削除し、B1 Comment loop(旧`generate_charon_english_with_ending_clarity_fallback`呼び出し)・B1 News本文loop(旧`generate_news_narration_with_ending_clarity_fallback`呼び出し)の2箇所を、それぞれ`voice01.generate_charon_english`・`news_tail_fix.generate_news_narration_wide_margin`への直接呼び出しに戻した。`er011_ending_clarity_fallback_01.py`自体・そのunit test(20件PASS)は削除せずhistorical recordとして保持し、ファイル冒頭にWITHDRAWN注記を追加した。

**Dangling Reference Check**: リポジトリ全体を`ending_clarity`/`Ending-Clarity`で検索した結果、現在のProduction経路(`er003_v1_n3_01_tts_generate.py`)からの参照は0件(コメント内の履歴言及のみ)。他に参照が残るのは(a)`er011_ending_clarity_fallback_01.py`自身とそのtest、(b)過去に実行済みの一回限りの診断・retryスクリプト(`er011_no18_open107_runtime_evidence_03.py`、`er011_no18_open110_comment2_ending_clarity_retry_04.py`等、historical recordとして削除不要)のみであることを確認した。

### 2. B1 Connected Speech ValidatorのProduction配線

新規`er011_b1_connected_speech_validator_01.py`(Trial-07から無変更で移植)を、`er006_preprod_hardening_01_validation.py::classify_asr_match()`へ2箇所配線した。

1. `non_entity_diffs`(固有名詞以外の内容語diff)がTRUE_CONTENT_MISMATCHへ直行する箇所の直前。
2. 内容語diffが検出されずratioが閾値未満の最終fallback箇所の直前。

2番目の箇所が追加で必要だったのは、実装中に判明した重要な発見のため: Pattern C(`survey`→`surveys`型の再分節)は、既存の`_is_benign_plural_pair()`(規則的な単数/複数語尾差を許容する既存機構)によって`content_word_diffs`へ計上される前に吸収されてしまい、1番目の挿入箇所(`non_entity_diffs`分岐)には到達しないことが、実データ(Track A Case 3の実文)で確認された。この場合、既存挙動は`ASR_VALIDATION_UNCERTAIN`(Cascade対象、should_pass=False)であり、connected speechとして正しく説明できるケースなのに自動PASSされていなかった。2箇所目への追加配線でこの経路も正しくカバーした。

判定は3パターンに限定(ユーザー承認範囲を超えて拡張しない): Pattern A(歯擦音連続)・Pattern B(破裂音連続)は`CONNECTED_SPEECH_ACCEPT`(警告なしPASS)、Pattern C(再分節)は`CONNECTED_SPEECH_PASS_WITH_WARNING`(PASSするが警告を保持)。

**Regression**: 既存English Validator fixture 57件(`er006_preprod_hardening_01_validation_test.py`)全PASS。追加した2箇所目の挿入点により、既存の「survey/surveys」を含む一部fixtureが新しいASR_VALIDATION_UNCERTAIN以外の分岐へ動くリスクを慎重に確認したが、既存57件・特に"unrelated plural nouns must not be absorbed"(cats≠dogs)を含め全て期待通りのまま。新規`er011_no18_connected_speech_reading_resolver_wiring_08_test.py`のB1部分8項目全PASS(studies suggest/opened to/survey suggest型の正しい分類、無関係語置換・無関係挿入・子音条件不成立での誤許容なし、ACCEPT/PASS_WITH_WARNINGの区別、Ending-Clarity非importの確認)。

### 3. A2 Reading ResolverのProduction配線

新規`er011_a2_reading_resolver_01.py`(Trial-07から無変更で移植)を、`er007_ja_asr_validator_01.py::classify_ja_asr_match()`へ配線した。挿入点は、既存の`whole_text_reading_equal`/`_reading_equal_allowing_voicing`(全文読み一致による救済、漢字/ひらがなscript差の吸収)がいずれも失敗した直後、既存のratio-based fallbackへ進む前。これは既存の「全文読み救済」機構と同じ設計思想の自然な延長であり、新しい挿入様式を持ち込んでいない。

fail-safe(ユーザー正式決定§2)を厳密に実装: resolved_matchが厳密にTrueの場合のみ`READING_RESOLVED_MATCH`とし、それ以外(辞書候補なし/LLM異常応答・例外/候補外選択[構造的にJSON Schema enumで防止、かつ二重チェック]/再比較後も不一致)は一律non-passとして既存のTRUE_CONTENT_MISMATCH処理へfall throughする。`resolve_reading_diff()`全体を1つのtry/exceptで囲み、あらゆる例外を「解決できなかった」として扱う。`FEATURE_FLAG_A2_READING_RESOLVER_ENABLED`(既定True)でON/OFF切替可能な設計とした(既存の`FEATURE_FLAG_SECONDARY_ASR_ENABLED`等と同じパターン)。

**Regression**: 既存Japanese Validator fixture 35件(`er007_ja_asr_validator_01_test.py`)全PASS。うち「月」(つき/がつ)fixtureは、旧実装では「孤立漢字の異読みは対象外」という前提のTRUE_CONTENT_MISMATCH期待だったが、Reading Resolverが辞書候補+文脈から正しく「つき」を解決できる(むしろ望ましい正しい動作)ことが判明したため、fixtureの意図を「Reading Resolverが文脈に基づいて正しく解決できることの確認」へ更新した(「漢字の異読みなら何でも自動PASS」にはなっていないことは、他の全fixture・新規fail-safe testで別途確認)。新規wiring_08_test.pyのA2部分7項目全PASS(後→あと解決、完全一致segmentでResolver未発火、候補外応答/候補なし/LLM例外の3種のfail-safe、読み問題でない真の内容誤りが誤ってPASSしないこと、B1側から一切importされないこと)。

### 4. Cross-Level Consistency Check(適用結果)

CURRENT_SPEC.mdの既存ルール(ER-011-NO18-OPEN109-110-FINAL-CLOSEOUT-04で新設)に基づき確認した。B1 Connected Speech Validatorは英語ASR比較(`er006_preprod_hardening_01_validation.py`)専用であり、A2の日本語ASR比較(`er007_ja_asr_validator_01.py`)には一切importされない(A2に英語のconnected speech現象[歯擦音・破裂音の弱化]は本質的に該当しないため、適用しないことが正しい)。A2 Reading Resolverは日本語の漢字読み解決専用であり、B1(英語)には一切importされない(英語に「読み候補」という概念自体が存在しないため)。**これは「片側にしか配線していない」のではなく「片側にしか適用対象がない」ケースであり、Cross-Level Consistency Checkのルールに従い、この判断理由を本エントリに明記する**。

### 5. No.18 A2/B1 Audio Stageの通し直し

記事・Support・Key Phrase(article.md/parts.json/support/key_phrases)はユーザー指示通り一切再生成せず、既存の確定済みテキストをそのまま使用した(git diffで無変更を確認済み)。

`er011_no18_connected_speech_reading_resolver_audio_stage_08.py`で、既存の`generate_b1_segments()`/`generate_a2_segments()`/`stage_assemble_b1()`/`stage_assemble_a2()`をそのまま呼び、Audio Stage全体(TTS→ASR→新Validator→retry→Assembly)を新仕様下で通した。B1 13segment中11件・A2 14segment中13件は初回runでOKとなったが、B1 `comment_2`/`comment_3`・A2 `comment_1`の3segmentは、前回session(2026-09-02)の一連のTrial・診断runで既に`er011_human_review_lock_01.py`のHUMAN_REVIEW_REQUIRED状態(`comment_2`は累積TTS試行が上限[15回]を超過しBUDGET_GUARD_TRIGGERED)へ到達済みだったため、review_lockの事前ゲートがTTS/ASR呼び出し自体を0回でblockし(`HUMAN_REVIEW_LOCKED`)、新Validatorが実際の新規出力に対して発火する機会が得られなかった。

これに対し、`er011_no18_connected_speech_reading_resolver_scoped_retry_08.py`で、この3segmentのみを対象に`review_lock.approve_regenerate()`(今回のタスク自体がNo.18本番Audio Stageの通し直しとruntime evidence取得を明示指示していることに基づく正当な呼び出し、`er011_no18_open110_comment2_ending_clarity_retry_04.py`で確立済みのscoped retryパターンを踏襲)を付与した上で、他の全segmentと同一のProduction正式関数(`voice01.generate_charon_english`・`generate_a2_japanese_with_reading_safety`)を直接呼んだ。他の既にOKだったsegmentには一切触れていない。

**Runtime evidence(実際のTTS/ASR出力に対する新Validatorの発火)**:
- B1 `comment_2`: canonical"The studies suggest..."に対しASRが実際に"The study suggests..."と書き起こし、`classify_asr_match()`が`CONNECTED_SPEECH_ACCEPT`(Pattern_A_sibilant_sequence、`studies/z/ + suggest/s/`)と判定、`status=OK`。
- B1 `comment_3`: canonical"...the survey...suggest..."に対しASRが実際に"...the surveys...suggest..."と書き起こし、`classify_asr_match()`が`CONNECTED_SPEECH_PASS_WITH_WARNING`(Pattern_C_resegmentation_added_consonant、`survey(+s) + suggest/s/`)と判定、`status=OK`。
- A2 `comment_1`: canonical「...通知音のあとに...」に対しASRが実際に「...通知音の後に...」と書き起こし、`classify_ja_asr_match()`内でReading Resolverが1回(標準経路attempt 1)・2回目のattempt(attempt 2、TTSが再生成された)でも発火し、候補[のち/あと/うしろ/こう/ご/しり]から「あと」を選択して`READING_RESOLVED_MATCH`と判定、attempt 2で`status=OK`(attempt 1はresolverを介しても最終的に不一致のままで通常retryが継続、attempt 2で解決。単発呼び出しの非決定性[Trial-07で確認済み、観測ベース約85〜100%]と整合する挙動であり、既存のTTS retryループがResolverの非決定性を自然に吸収する形になった)。

全てmodel_id/prompt role/candidate list/selected reading/cost/elapsed timeを含む詳細ログが`er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2/{b1b,a2}/audit/tts_generation_results.json`(各segmentの`connected_speech_info`/`reading_resolver_info`フィールド)、および`raw_usage_log_wiring08_audio.jsonl`/`raw_usage_log_wiring08_scoped_retry.jsonl`(cost logger実測ログ)に記録されている。

Assembly実行の結果、**No.18 A2/B1が今回初めて両レベルとも完成した**: B1 351.324秒(clipping無し、peak 0.782)、A2 347.338秒(clipping無し、peak 0.854)。lineage確認: article.md/parts.json/support/key_phrasesはgit diffで無変更を確認、Audio Stage(narration/audit/assembled)のみが今回更新された。

### 6. Regression(全体)

既存fixture: English Validator 57件PASS、Japanese Validator 35件PASS、`er006_secondary_asr_01_test.py`14件PASS、`er007_ja_secondary_asr_01_test.py`9件PASS、`er003_test_v1_n3_01_tts_generate.py`16件PASS、`er008_audio_validation_gate_05_test.py`10件PASS、`er011_ending_clarity_fallback_01_test.py`20件PASS(historical、モジュール自体は無変更のためPASSを維持)、`er011_human_review_lock_01_test_01.py`18件PASS。新規`er011_no18_connected_speech_reading_resolver_wiring_08_test.py`15件PASS(B1 8項目+A2 7項目、§10要求を充足)。

**発見した2件の既存(session前から存在する)regression失敗、いずれも本セッションの変更とは無関係と確認済み**: `git stash`で本セッションの変更を一時的に取り除いた状態でも同一の失敗が再現することを確認した。(1)`er006_pool_benches_luna_audio_wiring_test.py`が`er003_v1_sing01_news_tail_fix.py`に`audio_validation`という別名でのimport文字列が無いことを検出([`secondary_asr`という別名でimportされているための文字列一致漏れと推測、コード自体の配線は健全])。(2)`er007_ja_tts_retry_path_fix_test_01.py::test_stop_retrying_false_still_retries_normally`がmock呼び出し回数の期待値不一致(2≠4)。いずれも本Decisionのスコープ外として修正していない(ユーザーへ別途報告)。

### 7. コスト実測(§13)

No.18 A2/B1 Audio Stage全体(全segment新規生成+3segment scoped retry、TTS/ASR/Reading Resolver全て込み)で実測¥51.18(90 API呼び出し)。うちA2 Reading Resolver呼び出し分のみ¥0.03(2 API呼び出し、`responses.create`/`gpt-5.6-luna`)。B1 Connected Speech Validatorはローカルpure Pythonロジックのため追加コスト¥0。1記事あたりのReading Resolver想定コストはTrial-07の見積り(retryなしで約¥0.01〜0.04)と実測(今回2回のresolver呼び出しで¥0.03)がおおむね一致することを確認した。

### 8. 今回行っていないこと

新しい音韻パターンの追加(承認済み3パターン以外)、日本語ReadingのB1への適用、Validator閾値の緩和、個別語のhardcode、`er011_ending_clarity_fallback_01.py`の削除(historical recordとして保持)は、いずれも§13禁止事項通り実施していない。

### SSOT反映

`CURRENT_SPEC.md`の「Ending-Clarity Fallback」行を`WITHDRAWN`へ変更し、新規行「B1 Connected Speech Validator」「A2 Reading Resolver」を`PRODUCTION_WIRED`として追加した。`OPEN_ITEMS.md`のOPEN-107を`WITHDRAWN`、OPEN-110・OPEN-111を`RESOLVED`(runtime evidenceにより解消)へ更新した。

### Git

新規: `er011_b1_connected_speech_validator_01.py`、`er011_a2_reading_resolver_01.py`、`er011_no18_connected_speech_reading_resolver_wiring_08_test.py`、`er011_no18_connected_speech_reading_resolver_audio_stage_08.py`、`er011_no18_connected_speech_reading_resolver_scoped_retry_08.py`、`er011_no18_connected_speech_reading_resolver_assemble_only_08.py`、`er011_no18_wiring08_cost_compute.py`。変更: `er003_v1_n3_01_tts_generate.py`(Ending-Clarity撤去)、`er006_preprod_hardening_01_validation.py`(Connected Speech配線)、`er007_ja_asr_validator_01.py`(Reading Resolver配線)、`er007_ja_asr_validator_01_test.py`(fixture更新)、`er003_v1_sing01_voice01_generate.py`/`er003_v1_sing01_news_tail_fix.py`/`er003_v1_repro01_main_generate.py`(audit trail追加、`connected_speech_info`/`reading_resolver_info`のattempts_log記録)、`er011_ending_clarity_fallback_01.py`(WITHDRAWN注記追加のみ)。

### 状態

No.18 A2/B1は`PRODUCTION_WIRED`両仕様のもとで**初めて両レベルとも完成**(assembled)。残る`USER_DECISION_REQUIRED`はNo.18完成音声自体のユーザー最終試聴承認のみ(`USER_FINAL_AUDIO_REVIEW_REQUIRED`、既存の他Noと同じ運用)。詳細は完了報告・Artifact参照。

---

## ER-011-CONNECTED-SPEECH-AND-A2-READING-TRIAL-07: B1 Connected Speech Validator Trial・A2 OPEN-111向け辞書候補+LLM選択Reading Resolver Trial

- **日付**: 2026-09-03
- **区分**: 両TrackともTrial(Track A: `VALIDATED`、Track B: `VALIDATED`。いずれもProduction配線なし)。

### 背景・スコープ

前回(ER-011-NO18-B1-LISTENING-AND-A2-OPEN111-READING-TRIAL-06)は、B1側は確認材料の提示のみに留め、A2側はWriterとは別の「Reading担当」役割による全文自由生成方式をTrialしたが、対象語と無関係な新規誤読(「変化」→「しんか」、本番PASS中の`comment_3`で「スマートフォン」→「すまあとふぉん」)が発生し`REJECTED`と判定した。本Decisionは、(a) Track A: ASR差分を即座に「TTS誤発音」と扱わず、語境界のconnected speech(音の弱化・融合・再分節)として説明可能かを、今回タスクから明示的に与えられた3パターン(A: 歯擦音連続、B: 破裂音連続、C: 再分節による子音追加)に限定して判定する候補ロジックをTrialすること、(b) Track B: 前回の「LLM自由生成」ではなく「既存機械変換の差分位置だけを辞書候補+LLM選択で解決する」新方式をA2 OPEN-111限定でTrialし、Trial-06の副作用(無関係語への新規誤読)を構造的に防げるかを検証することを目的とする。両TrackともProduction配線は行わず、Trialの分類(REJECTED/VALIDATED/USER_DECISION_REQUIRED)で終了する。

### Track A: B1 Connected Speech Validator Trial

新規ファイル`er011_no18_b1_connected_speech_trial_07.py`。新規TTS/ASR呼び出しは行わず、既存の実データ3件をそのまま使用した。

- **Case 1(`studies suggest`→`study suggests`、B1 `comment_2`、3attempt全て同一)**: canonical語尾"-ies"(歯擦音/z/)とASR語"study"の関係を、単純な接尾辞除去ではなく英語のy→ies綴り変化ルールで正しく認識した上で、次語"suggest"の語頭/s/との歯擦音連続としてPattern Aに分類、`CONNECTED_SPEECH_ACCEPT`候補とした。
- **Case 2(`opened to`→`open to`、OPEN-107診断Trial cond7 attempt3、3attempt中1件)**: canonical語尾"-ed"(破裂音/d/)と次語"to"の語頭/t/との破裂音連続としてPattern Bに分類、`CONNECTED_SPEECH_ACCEPT`候補とした。
- **Case 3(`survey suggest`→`surveys suggest`、OPEN-110 survey_diagnostic_04 cond1 attempt3、3attempt中1件)**: ASR語に追加された語末/s/が、次語"suggest"の語頭/s/との再分節として説明可能なPattern Cに分類、`CONNECTED_SPEECH_RESEGMENTATION`候補(将来Production採用時は`PASS_WITH_WARNING`候補)とした。

**false accept risk検証**として3件の陰性対照ケース(無関係語の追加のみ、"studies"→"stories"という真の語幹置換、複合主語だが次語頭が歯擦音でない場合)を追加作成しテストした結果、いずれも新ロジックで非該当(既存判定を維持)と判定され、false acceptは確認されなかった。

実装過程で2件の実装バグを発見し修正した: (1)y→ies型の綴り変化(studies等)を単純prefix比較では検出できずCase 1が誤って非該当になっていた、(2)語頭判定が"sh"/"ch"/"th"等のdigraphを歯擦音・破裂音と誤認識し、陰性対照ケースの1件(survey→surveysだが次語が"shows"で歯擦音でない例)を誤ってPattern Cに分類していた。いずれも修正済みで、修正後は全ケースが期待通りの分類となることを確認した。

OPEN-107との関係については、「ASR不一致→connected speech判定→説明可能ならACCEPT候補、説明不能なら既存Ending-Clarity fallback候補」という候補フローを提案した(この候補フローの下では、Case 2のような`opened to`はPattern Bで説明可能なためEnding-Clarity fallbackの発火自体が不要になる可能性がある)。ただし今回はロジックの実装・分類のみであり、OPEN-107のProduction仕様(Ending-Clarity fallback)への変更・配線は一切行っていない。

**Track A Trial status: `VALIDATED`**(3つの実データケースを正しく分類し、3つの陰性対照ケースでfalse acceptなしを確認)。ただし判定パターンは今回タスクで明示的に与えられた3種類に限定しており、それ以外の音韻パターンへの拡張は行っていない。

### Track B: A2 OPEN-111 Reading Resolver Trial(辞書候補+LLM選択方式)

新規ファイル`er011_no18_a2_reading_resolver_trial_07.py`(+信頼性測定用の`er011_no18_a2_reading_resolver_trial_07_consistency.py`)。新規TTS呼び出しは行わず、ASR側も既存の実運用ASR結果(標準経路の実際の書き起こしテキスト)をそのまま再利用した(課金対象はReading Resolver LLM呼び出しのみ)。

**方式**: canonical本文とASR本文をそれぞれ既存のpykakasi機械変換にかけ、変換結果(ひらがな文字列)を`difflib`で突き合わせて差分位置を検出する。差分位置に対応するcanonical側またはASR側のチャンクに漢字が含まれる場合のみ、その漢字1文字についてpykakasi内蔵辞書(kanwadict、`Kanwa.load()`)から読み候補一覧を取得する(個別単語の正解を決め打ちするのではなく、辞書が実際に持つ候補をそのまま使う)。LLMには全文文脈とその候補一覧だけを渡し、JSON Schemaの`enum`で候補一覧の中からしか選べないよう制約した上で1つを選ばせる(自由生成は構造的に不可能)。

**結果**:
- `comment_1`(OPEN-111本体、「の後に」→「のちに」の誤り): ASR側の該当チャンク(「後に」)にのみLLMが1回呼ばれ、候補[のち/あと/うしろ/こう/ご/しり]から文脈に基づき「あと」を正しく選択、機械変換では不一致(`mechanical_match=False`)だった判定が解決後は一致(`resolved_match=True`)に変わった。
- 正常segment4件(`comment_2`/`comment_3`/`comment_4`/`japanese_title`): いずれも機械変換の時点で既にcanonical/ASRが一致していたため、Resolver呼び出しは0回発生した。Trial-06で発生した無関係語への新規誤読(「変化」→「しんか」、`comment_3`の「スマートフォン」→「すまあとふぉん」)は、差分がない箇所にLLMが一切触れない設計上、構造的に再発しなかった。
- `preview`segment: 「二つ」(canonical)↔「2つ」(ASR)という数字表記形式の差分でLLMが1回呼ばれたが、これは読みの曖昧さの問題ではないため、本方式は正しく「修正すべきでない」と判断し(候補選択は行ったが、判定結果には反映されず不一致のまま)、誤った修正はしなかった。
- 追加テキスト例2件(「後」があと文脈/のち文脈それぞれで登場する構成文、新規TTS/ASRなしのテキストのみの検証): いずれも文脈に応じて正しい候補を選択した。

実装過程で1件のバグを発見・修正した: 「二」→「ふたつ」のように、1文字の辞書候補自体が後続のかな(「つ」)を含む複数モーラの読みになっている場合、単純に後続部分を連結すると二重連結("ふたつ"+"つ"="ふたつつ")になっていた。候補が既に後続部分で終わっている場合は連結しないよう修正した。

**信頼性の追加測定**: `comment_1`の対象チャンクについて同一入力でResolverを5回反復した結果、5/5で正しく「あと」を選択した。別の非公式な単発テスト(バグ修正前後の再実行を含む)では7回中1回「のち」を誤選択したことがあり、単発呼び出しの決定性は完全ではない(観測ベースで約85〜100%)。本番検討時は複数回サンプリングの多数決を推奨する。

**コスト**: 全実験(バグ修正前後の再実行・信頼性測定含む)累計14 API呼び出しで実測¥0.2(1呼び出しあたり平均約¥0.014)。1記事(A2、日本語segment6件)あたりの想定コストは、retryなしで約¥0.01〜0.04(実際に差分が生じた箇所だけに呼び出しが限定されるため、Trial-06の全文自由生成方式[¥0.8〜1.6/記事]より大幅に低い)。10記事換算で約¥0.1〜3(推測)、100記事換算で約¥1〜30(推測)。処理時間は1回の呼び出しあたり約1〜2秒、差分がない場合は0秒(API呼び出しなし)。

**判定: `VALIDATED`**。タスクが定めた受入基準(後/あと問題の解決、他正常segmentを壊さない、LLM自由生成由来の新規誤読なし、コスト・処理時間が許容範囲内)をいずれも満たした。ただし、単発呼び出しの非決定性、および辞書(pykakasiのkanwadict)がカバーしない語・複合語には無力であるという制約は残る。Production配線を検討する場合は、多数決サンプリング等の追加評価を推奨する。

### 今回行っていないこと

Connected Speech判定・Reading ResolverいずれについてもProduction仕様への配線は行っていない。OPEN-107のEnding-Clarity fallback仕様・OPEN-110の`comment_2`/`comment_3`の言い換え判断・OPEN-111のValidator一般化についても変更していない。B1へのReading処理適用、Human Review承認の代行もいずれも行っていない。

### SSOT反映

`OPEN_ITEMS.md`のOPEN-107/OPEN-110/OPEN-111各行へ、それぞれTrack A/Track Bの結果を追記した(status: OPEN-107は`PRODUCTION_WIRED`のまま[Track A結果は参考情報として追記]、OPEN-110/OPEN-111は`USER_DECISION_REQUIRED`のまま[Track A/B結果を追加の判断材料として提示])。

### Git

新規ファイル: `er011_no18_b1_connected_speech_trial_07.py`、`er011_no18_a2_reading_resolver_trial_07.py`、`er011_no18_a2_reading_resolver_trial_07_consistency.py`。出力: `er011_output/b1_connected_speech_trial_07/`、`er011_output/open111_a2_reading_resolver_trial_07/`。

### 状態

B1/A2とも episode assembly未完成のまま(いずれも既存のUSER_DECISION_REQUIRED項目の解決が前提のため、状態変化なし)。両Trackとも追加の判断材料をユーザーへ提示した段階でSTOP。

---

## ER-011-NO18-B1-LISTENING-AND-A2-OPEN111-READING-TRIAL-06: B1 comment系のUser Listening Artifact提示・A2 OPEN-111向け代替Reading方式Trial

- **日付**: 2026-09-02
- **区分**: B1側はImplementation調査(確認材料の提示のみ、コード変更・仕様変更なし)。A2側はTrial(REJECTED、Production配線なし)。

### 背景・スコープ

前回session(ER-011-NO18-OPEN109-110-FINAL-CLOSEOUT-04)で、B1`comment_2`("studies"→"study")はEnding-Clarity fallback実発火確認済みも未解消、`comment_3`("survey"→"surveys")は診断のみで方針未決定、A2`comment_1`(「後」/「あと」異読み、OPEN-111)は既知の残存限界の新実例として発見されたが、いずれもASR文字列上の差分のみを根拠にしており、実音声を人間が確認できる状態にはなっていなかった。本Decisionは、(a) B1側について文面変更・Validator変更を一切行わず、canonical全文・TTS入力・各attemptのASR結果・実音声を人間が確認できるArtifactを整備すること、(b) A2 OPEN-111について、既存のpykakasi機械変換に代わる「文脈込みLLM Reading担当」方式をA2限定でTrialし、有効性・副作用・コストを測定することを目的とする。

### Track A: B1 comment_2 / comment_3 / opened(参考比較) — User Listening Artifact

新規TTS呼び出し・ASR再実行は行わず、前回session以前に既に生成・保存済みの音声ファイルとJSON記録(`tts_generation_results.json`、`open110_survey_diagnostic_04/`、`open107_opened_tts_diagnostic_trial_01/`、`open107_ending_clarity_fallback_trial_02/`)をそのまま再利用した。

- `comment_2`: canonical全文・TTS入力文(reading safety適用後も同一)・5attempt分(通常3+fallback2)のASR結果(すべて同一パターン、"studies"→"study"・"suggest"→"suggests")・最終音声・前後の単語("The" / "suggest")を提示。連結・弱化(assimilation)の観点として、"studies"語末の/z/と"suggest"語頭の/s/が隣接する歯擦音クラスタであり、ASRの書き起こしが文法的に自己完結した"study suggests"へそろっている点を、TTS自体の誤発音と断定せず解釈材料として提示した。
- `comment_3`: canonical全文・TTS入力文・3attempt分のASR結果(すべて"survey"→"surveys")・最終音声・前後の単語("the" / "suggest")を提示。前回session実施済みの5条件診断結果(cond1原文1/3・cond2短文0/3・cond3非歯擦音後続語0/3・cond4語順入替[studies→study 2/3に転移]0/3・cond5単独0/3)を表形式で再掲し、「survey固有の脆弱性」「後続語頭/s/の取り込み」のいずれも支持されず、「動詞に直接隣接する名詞の数が不安定になる」という仮説が一貫している点を再確認した。
- `opened`(OPEN-107参考比較): 同一文面での通常経路NG("open")/OK("opened")の実例(前回diagnostic Trialの`cond5_6_full_sentence_no_context`条件、同一テキストでattempt1がNG・attempt2がOK)を並べて提示。加えて、Ending-Clarity指示付きでも長文条件(`cond5_full_sentence_with_context`)では3attempt中2件がNG("open")のままだった実例を提示し、Ending-Clarityが「誤発音の確実な修正」ではなく「ASR向け明瞭化の底上げ」である可能性を再評価情報として添えた。また、実Production側の`in_one_line`合格は、fallback発火によるものではなく通常retry 2回目でのTTS非決定性による合格だった(`ending_clarity_fallback_used=false`)ことも明記した。

いずれも文面の言い換え・Validator緩和・retry追加・新fallback追加は一切行っていない(ユーザー指示通り、確認材料の提示のみ)。

User Listening Artifact: https://claude.ai/code/artifact/c292c1ca-5bb6-4d41-a01a-ccc9b1c8c28f (音声9件を埋め込み、5.86MB)。

### Track B: A2 OPEN-111 — 文脈込みLLM Reading方式のTrial

**方式**: Writerとは別の「Reading担当」役割(`er011_no18_a2_reading_trial_06.py::call_reading_role()`、Approved Model=`gpt-5.6-luna`[`A2_SUPPORT`経由、overrideなし])を新設した。既に確定済みのA2 tts_input_text(原文)を渡し、「一字一字の機械的変換ではなく、文脈を踏まえてどう読まれるかを判断し、完全にひらがなのみで出力する」よう指示した(個々の漢字の読みをあらかじめ決め打ちする指示は一切含まない、"後=あと"のhardcodeなし)。新規TTS呼び出しは行わず、既存のA2 narration wav(`comment_1.wav`含む、6attempt目の実音声が保存済み)をそのまま再利用した。

**Phase 1(`er011_no18_a2_reading_trial_06.py`)**: 6segment(comment_1[対象]・comment_3[本番PASS中の同種"あと"表現を含む正常segment]・japanese_title・preview・comment_2・comment_4)について、(1) Reading担当によるcanonical_readingの生成、(2) OpenAI ASR(gpt-4o-mini-transcribe)へ「ひらがなのみで書き起こしてください」というpromptを付けた直接呼び出し、を実施した。結果、**(2)は6segmentすべてで、prompt指示なしの通常書き起こしとほぼ同一の漢字混じり結果しか得られなかった**(かな書き起こし指示は実質的に無視される。「漢字認識後の後処理変換」ですらなく、より基本的にASR側が文字種をpromptで制御できていないことを確認)。

**Phase 2(`er011_no18_a2_reading_trial_06_phase2.py`)**: Phase 1の失敗を受け、既存の(漢字混じりの)通常ASR結果自体を同じReading担当に読ませてひらがな化する方式を追加テストした(比較としてpykakasi機械変換も並記)。結果:
- `comment_1`: canonical側Reading担当・ASR側Reading担当のいずれも「通知音の**あと**に」を正しく「あと」と判定した(pykakasi機械変換はASR側でも「のち」に誤る)。ASRが「後」とだけ書いた文脈のみからでも正しく推論できており、OPEN-111の対象語自体はこの方式で解決できることを確認した。ただし、canonical側Reading担当が「変化」を「しんか」と誤読する新しい読み誤りが発生し、全文一致判定としては引き続きFAILだった(対象語とは無関係な誤り)。
- `comment_3`(本番PASS中の正常segment): canonical側Reading担当が「スマートフォン」を「すまあとふぉん」と誤読する新しい読み誤りが発生し、全文一致判定がFAILへ転じた(本番のpykakasi方式ではこの箇所は問題なくPASSしている)。
- japanese_title/preview/comment_2/comment_4: いずれもReading担当同士の比較では一致(pykakasi比較では表記ゆれ["二つ"↔"2つ"等]により preview/comment_2が不一致になったが、これはNormalize側の対象外の軽微な差)。

**コスト**: 実測¥1.3(6segment・18 API呼び出し、Reading生成12回+かなASR6回)。1記事(A2日本語segment6件)あたり想定はretryなしで約¥0.8、typical retryありで約¥1.0〜1.2、worst caseで約¥1.6(いずれも推測、実測ベースの外挿)。10記事換算約¥8〜17、100記事換算約¥80〜170(いずれも推測)。処理時間・API呼び出し増分ともProduction Pipelineへの組み込みで大きな複雑性増加にはならない。

**判定: `REJECTED`**(現行のシングルショットLLM方式のまま本番採用しない)。理由はコスト・処理時間ではなく品質: VALIDATEDの基準のうち「他正常segmentも問題なし」「新しい重大なfalse positiveなし」を満たせなかった(`comment_3`で本番では発生しない新規誤読が発生)。一方、「後/あと」というOPEN-111の対象自体は、文脈込みLLM Reading方式でpykakasiより正しく解決できることを確認しており、方式の着想自体には見込みがある。Reading担当の精度を上げる改良(複数回生成の多数決取り、固有名詞・カタカナ語のミニ辞書併用等)を伴う追加Trialを行うかどうかはユーザー判断に委ねる。Production配線(既存Validator・TTS retry構成の変更)は一切行っていない。

Artifact(comment_1実音声・全結果表を含む、Track Aと共通ページ): https://claude.ai/code/artifact/c292c1ca-5bb6-4d41-a01a-ccc9b1c8c28f

### SSOT反映

[OPEN_ITEMS.md](OPEN_ITEMS.md) OPEN-110(Track A追記)・OPEN-111(Track B追記、`REJECTED`判定を記録)を更新。CURRENT_SPEC.mdへの変更は無し(Production仕様変更を伴わないため)。

### Git

新規Trial scriptのみ追加(`er011_no18_a2_reading_trial_06.py`・`er011_no18_a2_reading_trial_06_phase2.py`)、既存Production経路コード(`er007_ja_asr_validator_01.py`・`er003_v1_n3_01_tts_generate.py`・`er011_ending_clarity_fallback_01.py`等)は無変更。

### 状態

`USER_DECISION_REQUIRED`(3件、変更なし): OPEN-110`comment_2`(Human Review承認 or 言い換え)、OPEN-110`comment_3`(Human Review承認 or 複合主語構文の言い換え)、OPEN-111`comment_1`(Human Review承認 or 言い換え or Validator一般化。代替方式は`REJECTED`のため既存3選択肢は変わらず)。A2/B1いずれのepisode assemblyも今回も未完成のまま(意図的、Assembly Gate FAILの状態でユーザー判断を待つ)。

---

## ER-011-NO18-OPEN109-110-FINAL-CLOSEOUT-04: OPEN-107検出/配線範囲の是正・A2のLedger精密化正式反映・B1/A2 comment系の新規TTS失敗モード診断

- **日付**: 2026-09-02
- **区分**: OPEN-107検出ロジック汎用化・Comment配線拡張はサービス・生成仕様(TTS retry構成の恒久拡張)。A2のLedger精密化反映はNo.18固有のデータ再生成(汎用Writer仕様は無変更)。Cross-Level Consistency Checkはサービス運用ルールの新設(SSOT運用ルール、コード実装は伴わない)。survey診断・comment_1調査はImplementation調査(コード変更なし)。

### 背景・スコープ

前回session(ER-011-NO18-OPEN107-PRODUCTION-WIRING-AND-FINAL-AUDIO-03)で、OPEN-107(Ending-Clarity fallback)をB1 News本文へ配線・OPEN-108(B1本文個別差し替え)を完了したが、B1`comment_2`/`comment_3`(新規TTS失敗モード、OPEN-110)・A2記事のLedger精密化未反映(OPEN-109)により、A2/B1いずれのepisode assemblyも未完成のままSTOPしていた。本Decisionは、ユーザー指示によりこれら2件の解消・診断と、A2への精密化済みLedger反映、再発防止のCross-Level Consistency Checkの正式ルール化を行う。

### OPEN-110 `comment_2`: OPEN-107検出/配線ロジックの是正と実Production発火確認

`comment_2`(canonical "The studies suggest...")がOPEN-107 Ending-Clarity fallbackの対象になるべきか確認したところ、2つの独立したgapを発見した。(1) **検出ロジックのgap**: canonical"studies suggest"とASR"study suggests"の差分は、既存Validator(`classify_asr_match`)の`content_word_diffs`計算上、2語にまたがる単一のreplace opcode("studies suggest"→"study suggests")として計算されており、旧`detect_ending_loss_diffs()`は単一語diffのみを対象としていたため検出漏れになっていた。(2) **判定ロジックのgap**: "studies"→"study"はy→ies型の不規則複数形(綴りが"studi"+"es"ではなく"stud"+"y"⇔"stud"+"ies"で変化する)であり、既存の`_dropped_suffix_if_ending_loss()`が前提とする「canonical文字列がasr文字列で始まる」という単純な接頭辞関係が成立しない(`"studies".startswith("study")`はFalse、iとyの綴り差のため)。

**修正**: `detect_ending_loss_diffs()`をcontent_word_diffsの各replaceブロックについて、canonical/asr側の語数が一致する場合は語単位に分解し、各語ペアを個別に判定するよう一般化した(単一語diffのみを対象にしていた旧実装を包含する上位互換の変更)。`_dropped_suffix_if_ending_loss()`へ、子音+y→iesという綴り変化パターン(city/cities、study/studiesなど一般的なパターン、"studies"個別へのhardcodeではない)を追加した。別の語(cities/city)でも同じ仕組みで検出できることを回帰テストで確認した。

**配線範囲の拡張**: 上記2つのgapを修正しても、`comment_2`はB1 Comment segment(`voice01.generate_charon_english`経路)であり、前回session配線したのはB1 News本文segment(`news_tail_fix.generate_news_narration_wide_margin`経路)のみだったため、依然fallbackへ到達できない配線漏れが残っていた。新規`generate_charon_english_with_ending_clarity_fallback()`(`er011_ending_clarity_fallback_01.py`)を実装し、B1 Comment loop(`preview`/`comment_1`〜`comment_4`)へ配線した。`generate_charon_english()`は`style_prefix_override`引数を直接受け取れるため、News本文版のような`p9a.ENGLISH_STYLE_PREFIX`monkeypatchは不要で、`(style_prefix_override or p9a.ENGLISH_STYLE_PREFIX) + ENDING_CLARITY_SUFFIX`を直接引数として渡すだけのより単純な実装になった。設計方針(review_lockを外側で1回だけguard、内部2回は`.__wrapped__`直接)はNews本文版と同一。

**Regression**: 新規7テスト(y→ies型検出・別語への一般化確認・survey→surveysが誤検出されないことの回帰確認・Charon経路wrapperの受入テスト4件)を追加、既存13テストと合わせ`er011_ending_clarity_fallback_01_test.py`計20テスト全PASS。既存`er011_human_review_lock_01_test_01.py`(18テスト)も無回帰。

**実Production経路での実発火確認(初)**: 修正後、`comment_2`を実際にB1 Comment配線経由で再生成した(`er011_no18_open110_comment2_ending_clarity_retry_04.py`、approve_regenerate経由)。結果: 通常3attempt全NG(同一の"studies"→"study"パターン)→`ending_clarity_trigger_check`が`{"canonical_word": "studies", "asr_word": "study", "dropped_suffix": "ies"}`を正しく検出→fallback(Ending-Clarity instruction付与)が実際に2attempt発火(`ending_clarity_fallback_used=True`)。これは前回sessionのcaveat(fallback分岐の自然発火が本session内で未観測、実発火evidenceが前回Trialに依拠)を解消する、実Production経路での初めての実発火確認である。ただし、fallback 2attemptとも同一の"study"(単数形)発話が継続し、`comment_2`自体は`STOPPED`のまま解消しなかった。これはOPEN-107の設計・実装が正しく機能していることの証拠であると同時に、`comment_2`固有の誤発音がEnding-Clarity instructionでは解消しない、より根深い決定論的な性質のものであることも示している。CURRENT_SPEC.mdの「Ending-Clarity Fallback」行を`PRODUCTION_WIRED`(実発火確認済み)へ更新した。

### OPEN-110 `comment_3`: "survey"→"surveys"の診断(Trial、方針決定はしていない)

`comment_3`("The studies and the survey suggest...")について、修正・言い換えを一切行わず、`er011_no18_open110_survey_diagnostic_04.py`(raw pipeline、実際のcomment_3と同一のvoice=Charon・style=B1_PREVIEW_STYLE_PREFIX_CALM)で5条件×3attemptの診断のみ実施した。結果: (1)実際の全文再現は1/3で"survey"→"surveys"再現(実Production記録の3/3より低頻度、TTS非決定性)。(2)"studies and the"という前文脈を除いた短文("survey suggests...")は0/3で誤発音なし。(3)"survey"の直後を非歯擦音("indicates")に変えても0/3。(4)語順を入れ替え"survey"を動詞"suggest"から離し"studies"を動詞直前へ置くと、"survey"自体は3/3正しいままだが、代わりに"studies"の方が2/3で"study"(単数形)に変化(逆方向の同種の誤り)。(5)"survey"を最小文脈で単独発話させると0/3。

後続語頭の/s/取り込み仮説(cond3で反証)・"survey"という語固有の脆弱性仮説(cond4で反証)はいずれも支持されず、最も説明力のある仮説は「"X and Y 動詞"型複合主語構文で、動詞に文法的に直接隣接する名詞の数がTTSにとって不安定になる」というもの(cond1では動詞隣接語"survey"が複数化、cond4では動詞隣接語"studies"が単数化)。小標本の診断結果であり断定はしていない。Production instruction・Validator・retry構成への変更は一切実施していない。

### OPEN-109: A2記事のLedger精密化正式反映

精密化済みVerified Fact Ledger(A2/B1共有ファイル、前回session[ER-011-NO18-OPEN108-LEDGER-REFINE-AND-OPEN107-ENDING-FALLBACK-TRIAL-02]で既に精密化済み、今回は再編集していない)から、既存Production正式Writer path(`gen.run_one_pattern`、無変更)でA2記事を1回だけ再生成した(`er011_no18_open109_a2_ledger_refined_regenerate_04.py`、B1B再生成[ER-011-NO18-OPEN108-LEDGER-REFINE-AND-OPEN107-ENDING-FALLBACK-TRIAL-02]と同一手法)。新article.mdは"hard-to-resist habit"の記述・Pewの丸め表現("About four in ten")のいずれも含まなくなり(56%表記に統一)、fact_verdict=`PASS`・ledger_status=`LEDGER_COMPLIANT`(deviation 0件)・Directional Fact Precheck`PASS`・Point Overlap QA無flag(記事全体retry0回)と、B1Bより精度指摘の少ない結果になった。旧article.md等はbackupとして`er011_output/open109_a2_pre_regenerate_backup_04/`に保持した。

続けてSupport(Preview/Comment1-4)・Key Phraseも新article.mdから再生成した(`er011_no18_open109_a2_support_kp_regenerate_04.py`、B1B版[`er011_no18_open107_b1_support_kp_regenerate_03.py`]と同一手法、A2専用の`sc.run_a2_scaffold`/`process="A2_SUPPORT"`を使用)。結果、support全件`OK`・kp_status=`CANONICALIZATION_PASS`・kp_redundancy_status=`REDUNDANCY_PASS`・support_fact_check verdict=`PASS`(issue 0件)。A2記事・Support・Key Phraseのテキストはこれで完成・確定した。

続けてA2 Audio Stage(同期TTS)を新lineageで実行した(`er011_no18_open109_a2_audio_stage_04.py`、B1側は今回対象外、b1b配下のファイルには一切書き込まない設計、`comment_2`のscoped retryと同時並行のためのファイル競合回避)。14segment中13件がOKとなったが、`comment_1`(日本語)が6attemptすべて同一の`TRUE_CONTENT_MISMATCH`で`STOPPED`となり、Audio Validation Gateが正しくA2 episode assemblyを中止した(詳細は次項OPEN-111)。

### OPEN-111(新規): A2 `comment_1`の日本語「後」/「あと」異読み

`comment_1`の差分を確認したところ、canonical「通知音の**あと**に」(ひらがな)に対しASRは一貫して「通知音の**後**に」(漢字)と書き起こしており、読み(あと)自体は同一で、TTSが誤発話している証拠はなかった。日本語Validator(`er007_ja_asr_validator_01.classify_ja_asr_match`)へ直接この差分を渡して確認したところ、`entity_like=False`・`phonetic_uncertain=False`・`cascade_eligible=False`と判定されており、既存の「日本語表記ゆれ(漢字/かな)」安全網(pykakasiによる読み変換での同値判定)を経由していなかった。さらにpykakasiで単独の「後」を変換すると「のち」(文脈上正しい読みは「あと」)が返ることを確認し、CURRENT_SPEC.mdの「日本語表記ゆれ」項が既に明記している既知の残存限界(「孤立漢字の異読み分岐のうち清音/濁音の関係にない異読み[例: 「後」のあと/のち]は依然未解消」)に該当する新しい実例であると特定した(新種のバグではなく、既に文書化済みの限界の別事例)。Validator修正は本Decisionのスコープ外として実施していない。新規OPEN-111として追加した。

### Cross-Level Consistency Check(SSOT運用ルール新設)

OPEN-109のような「B1のみLedgerを精密化し、共有Ledgerを使うA2側が旧記述を残したまま放置される」再発を防ぐため、Cross-Level Consistency Checkを正式ルール化した(CURRENT_SPEC.md「Cross-level仕様」節に新規行追加)。Research/Ledger・Writer/Support/Key Phrase仕様・QA/Validator仕様・TTS retry/fallback仕様・Fact Checker運用のいずれかをA2/B1どちらか一方について変更した場合、もう一方への影響有無を必ず明示的に確認し、影響がある場合は両レベルへ反映・再QAしてからcloseする、片側だけ修正してcloseすることを禁止する、というルール。自動チェックコードは今回実装していない(SSOT運用ルールとしての明文化のみ)。

### Cost Trace

`er011_open109_110_cost_compute_04.py`(既存`er011_specfix_cost_compute_01.summarize()`を無変更で再利用)で実測。合計¥53.5(130 API call)。内訳: A2 Production(Writer+QA¥6.5・Support+KP¥3.2・Audio¥33.9)計¥43.6、B1 Production(`comment_2` Ending-Clarity retry)¥5.1、Trial(survey診断)¥4.8。

### 状態

OPEN-107: `PRODUCTION_WIRED`(実Production経路での実発火を`comment_2`で直接確認、前回session caveat解消)。OPEN-108: 変更なし(B1本文は`RESOLVED`のまま)。OPEN-109: テキスト(記事・Support・Key Phrase)は`RESOLVED`、Audioは新規OPEN-111によりBlocked。OPEN-110: `comment_2`はEnding-Clarity fallback試行済みも未解消、`comment_3`は診断完了・方針未決定、いずれも`USER_DECISION_REQUIRED`のまま。OPEN-111(新規): `USER_DECISION_REQUIRED`。A2/B1とも episode assembly未完成。

### Git

commit・push実施(コミットSHAは本ファイルcommit後にDECISION_LOGへ反映しない、report参照)。

---

## ER-011-NO18-OPEN107-PRODUCTION-WIRING-AND-FINAL-AUDIO-03: OPEN-107(Ending-Clarity fallback)をB1 Production正式経路へ配線、No.18 B1本文の個別差し替え・Audio Stage実行

- **日付**: 2026-09-02
- **区分**: Ending-Clarity fallback配線はサービス・生成仕様(TTS retry構成の恒久追加、B1 News本文segment限定)。B1本文の個別差し替えはNo.18固有のデータ修正(汎用Writer仕様は無変更)。Audio Stage実行・failed segment retryはImplementation実行(既存関数の呼び出しのみ、コード変更なし)。

### 背景・スコープ

ER-011-NO18-OPEN108-LEDGER-REFINE-AND-OPEN107-ENDING-FALLBACK-TRIAL-02で、OPEN-108(No.18 B1 Fact Checker FAIL)はVerified Fact Ledgerのsource-grounded精密化で解消済み、OPEN-107(Ending-Clarity fallback候補)はTrialで実Production相当条件2/2 PASSの好結果を確認済みだった。本Decisionでは、ユーザーが(1)OPEN-107のEnding-Clarity fallbackをProduction正式採用すると決定、(2)No.18 B1Bの再生成済み本文について、Point One本文中の1箇所をユーザー指定文へ個別差し替えるよう指示、(3)No.18 A2/BのAudio Stageを正式Production経路(同期TTS)で実行するよう指示した。Track A(B1本文差し替え・Audio Stage)とTrack B(Ending-Clarity Production配線)は独立して扱った。

### Track B: Ending-Clarity fallbackのProduction配線(OPEN-107)

**設計**: 新規`er011_ending_clarity_fallback_01.py`に`generate_news_narration_with_ending_clarity_fallback()`を実装した。`news_tail_fix.generate_news_narration_wide_margin()`本体(既存Production関数)は一切変更せず、その`.__wrapped__`(review_lockデコレータが`functools.wraps`で自動的に保持する、undecoratedな生の実装)を直接呼ぶことで、通常経路呼び出しとfallback呼び出しの2回がそれぞれ独立にreview_lockのcheck/recordを行ってしまう問題(通常経路が1回失敗した時点で即座にHUMAN_REVIEW_REQUIREDへ遷移し、fallback呼び出し自体がブロックされる)を回避した。新wrapper関数自体を`@review_lock.guarded_generate("en")`で1回だけguardし、「1回の論理的生成操作(通常+条件付きfallback)につき1回のcheck/record」という既存の設計思想(OPEN-105のreentrancy guardと同じ思想)を踏襲した。

検出ロジック(`detect_ending_loss_diffs()`)は、既存`er006_preprod_hardening_01_validation.classify_asr_match()`が既に計算している`content_word_diffs`(単一語同士のreplace型diffのみ)を流用し、canonical wordがasr wordの末尾へ規則的な屈折語尾(-ed/-s/-ing/-en/-er/-est/-ly/-d、長さ3文字以内)を追加した形になっている場合のみ「語尾脱落」と判定する。新しい比較ロジックは追加せず、"opened"のような特定語へのhardcodeも行っていない(regression test `test_9_no_opened_hardcode_in_executable_logic`で実行コード行への"opened"混入が無いことを機械的に確認、コメント上の説明的言及は許容)。

fallback発火時は、`p9a.ENGLISH_STYLE_PREFIX`をこの1回の呼び出し中だけEnding-Clarity instruction(既存instruction末尾へAND方式で追加、文言: "Pronounce grammatical endings and final sounds clearly enough to remain audible, without exaggerating them or disrupting the natural rhythm of the sentence."、"opened"/"-ed"への言及なし)へ差し替え、`.__wrapped__`を最大2回(`FALLBACK_MAX_ATTEMPTS`、前回Trialの`PRODUCTION_EQUIVALENT_OUTER_REPEATS`と同一値)再試行し、呼び出し後は必ずfinallyで元へ復元する(前回Trialで検証済みの手法をそのまま踏襲)。fallback PASS時は`standard_attempts_log`/`fallback_attempts_log`の2フィールドへ分けて記録し(既存の`generate_english_segment_with_fallback`等と同じ命名規約)、review_lockの`cumulative_tts_attempts`集計が二重会計なく正確に反映されることを確認した。

**配線先**: `er003_v1_n3_01_tts_generate.py::generate_b1_segments()`のNews本文5segment(`full_story_part1`/`full_story_part2`/`point_one`/`point_two`/`in_one_line`)のcall siteのみ。A2側の並行関数(`er003_v1_crosslevel_audio_02_common.generate_english_segment_with_fallback`)は今回の配線対象に含めていない(評価実績が無いため見送り、OPEN_ITEMS.mdへ将来検討事項として記録)。

**Regression**: `er011_ending_clarity_fallback_01_test.py`(13 test、うち10項目はユーザー指定の受入基準[normal PASS→非発火/normal NG→retry PASS→非発火/normal NG→retry NG→発火/fallback PASS→segment差し替え/fallback NG→既存STOP/正常segment不可侵/attempt count正確/assembly対象asset正確/hardcodeなし/常時適用なし]、3項目は語尾脱落検出ロジックの一般性・非opened性の追加確認)全PASS。既存`er011_human_review_lock_01_test_01.py`(18 test)も無回帰。

**Runtime evidence**: (1)実Production call site経由のNo.18本番Audio Stage実行(下記Track A参照)で、B1 News本文5segmentはいずれも通常経路の初回attemptでPASSし、fallbackは1回も発火しなかった(spurious発火0件、常時適用でないことの実証)。(2)実wrapper関数を直接呼ぶ独立runtime evidence run(`er011_no18_open107_runtime_evidence_03.py`、No.18の実segmentとは別の隔離出力先、review_lockの命名規約[`<theme>/<level>/narration/<segment>.wav`]は満たす)を計4回実施(前回Trialでcond9として実際に失敗していた同一文言「Your phone does not have to be opened to become part of the task. ...」を使用)、いずれも通常経路が初回PASSし、fallback発火は観測されなかった(TTS自体の非決定性により、同一文言が前回3/3失敗・今回4/4成功という結果になった)。**fallback分岐自体が実際に発火する場面は本session内では自然発生せず、実API発火の直接的な新規証跡は取得できなかった**。ただし、fallback発火時に実際に呼ばれる下位関数(`generate_news_narration_wide_margin`、Ending-Clarity instruction適用時)自体は、前回session(ER-011-NO18-OPEN108-LEDGER-REFINE-AND-OPEN107-ENDING-FALLBACK-TRIAL-02、cond6)で同一の関数・同一の呼び出し方(monkeypatch経由)により実際に2/2 real API PASSしており、今回このメカニズム自体は一切変更していないため、その証跡は引き続き有効と判断した。この点は正直にOPEN_ITEMS.md/ユーザー報告へ明記し、「fallback自体の実発火は前回Trialに依拠」という限定付きで`PRODUCTION_WIRED`とした(過大な確定表現は避けた)。

CURRENT_SPEC.mdの[Audio Production Pipeline]節へ「Ending-Clarity Fallback(OPEN-107)」行を新規追加し、`DECIDED`/`PRODUCTION_WIRED`として正式記録した。

### Track A: No.18 B1本文の個別差し替え・既存QA再実行・Support/Key Phrase再生成

ユーザー指定の個別差し替え(Point One本文中の1文、B1B限定・一般Writer仕様への影響なし):

- 旧: "Responses were slower, and a brain-wave signal linked by the researchers to staying on task became larger. They interpret this pattern as automatic attention capture, not necessarily a deliberate choice to check."
- 新: "Responses were slower, while a brain-wave signal associated with cognitive control became larger. The researchers interpreted this as a sign that staying on task required extra mental effort after the notification sound."

`article.md`/`parts.json`を直接編集した後、`er011_no18_open107_b1_text_patch_requa_03.py`で`gen.run_one_pattern()`のWriter生成"以降"の既存公式QA工程(Point Overlap QA→Point Value QA→metrics/length_report→Fact Checker→Ledger Deviation Check[Local Rewrite Loop込み、Hook-aware]→Directional Fact Precheck)を、新規判定ロジックを追加せず既存関数をそのまま呼び出す形で再実行した。結果: Point Overlap/Value QAともflag無し(Point One/Two相互・Full Story対比いずれもthreshold未満)、Fact Checker `REVIEW_REQUIRED`(non-blocking、新しい指摘4件のうち1件が今回の差し替え文言「staying on task required extra mental effort」を「著者の解釈であり直接測定結果ではない」と正しく識別しており、"researchers interpreted"という表現自体の妥当性を裏付ける結果だった)、Ledger `LEDGER_COMPLIANT`(MINOR 1件、"peer-reviewed"表現に関するもので差し替え箇所とは無関係)、Directional Fact Precheck `DIRECTION_REVIEW_REQUIRED`(72%統計の時制表現に関するもので差し替え箇所とは無関係、advisory)。いずれもblocking要因なし。

Key Phraseの`keywords_canonicalized.json`を確認したところ、rank1「attention capture」の`source_sentence`(削除された旧文そのもの)・rank5「brain-wave signal」の`source_sentence`(周辺文脈が変化)の2件でtraceabilityが破綻していることを発見した。`er011_no18_open107_b1_support_kp_regenerate_03.py`(前回session確立済みのb1b限定Support/Key Phrase再生成パターンを踏襲)でSupport(`sc.run_b1_scaffold`)・Key Phrase(`sc.run_key_phrases`)・Support Fact Check(`support_mod.run_support_fact_check`)をいずれも無変更の実Production関数で再実行した。結果: Support全件OK、Key Phrase 5件は新article.mdから正しくtraceableな形で再選定され(rank1"pay a price"・rank2"compete through its presence"・rank3"stay on task"・rank4"cognitive control"・rank5"brain-wave signal")、`kp_status=CANONICALIZATION_PASS`・`kp_redundancy_status=REDUNDANCY_PASS`。Support Fact Checkは`verdict=MINOR_FIX`issue1件(comment_3が「調査結果」を「確認していない状態での影響」の根拠に含めることで意味範囲を広げているという指摘、今回の個別差し替えとは無関係な既存Support文の言い回し論点、REVIEW_REQUIRED相当のnon-blocking advisoryとして記録するのみに留めた。理由: `run_support_fact_check()`自体がProduction上いかなるblocking gateにも配線されていない、純粋な報告専用QAであることをコード確認済み)。

これによりB1Bの記事・Support・Key Phraseはテキストとして完成・確定した(`RESOLVED`)。

### Audio Stage実行(No.18 A2/B1、同期TTS)

`er011_no18_open107_audio_stage_03.py`(既存`er011_no18_discovery_why_full_production_run_01.run_audio_stage()`と同一構造、THEME_ID/OUT_DIRのみ差し替え)で、同期TTSモード(`enable_sync_tts_mode`、Production Batch経路自体は無変更、プロセス内でのみ一時差し替え)を使いB1/A2のTTS→Assemblyを実行した。

**B1**: 13segment中11件がOK(Ending-Clarity fallback対象の5 News本文segmentすべて含む、いずれも通常経路初回PASS)、Key Phrase5件×英日ともOK。`comment_2`(canonical"The studies suggest..."、Charon voice、`B1_PREVIEW_STYLE_PREFIX_CALM`、Ending-Clarity fallbackの対象外)が3attemptとも"studies"[複数形]を"study"[単数形]と発話しTRUE_CONTENT_MISMATCHで`STOPPED`、`comment_3`(canonical"...the studies and the survey suggest..."、同voice)が3attemptとも"survey"[単数形]を"surveys"[複数形]と発話し`ASR_VALIDATION_UNCERTAIN`。Audio Validation Gateが正しくfail-closedでB1 episode assemblyを中止した。`er011_no18_open107_b1_failed_segments_retry_03.py`(`review_lock.approve_regenerate()`で該当2segmentのみ承認、実Production関数`voice01.generate_charon_english`を無変更のまま再呼び出し)で2回retry(計6attempt/segment)を試みたが、いずれも同一の誤りパターンが再現し解消しなかった(ランダムなvarianceではなく決定論的な誤発音である可能性が高い)。既存のOPEN-102/103/104/107のいずれとも異なる新しい失敗モードのため、新規OPEN-110として追加し、これ以上の自動retry・Validator変更は行わずSTOPした(B1 episode assemblyは未完成のまま)。

**A2**: 14segment中13件がOK、Key Phrase5件×英日ともOK。`full_story_part1`が`STOPPED`。加えて、A2 Audio Stage実行前のlineage確認(article final hash・support/key phrase source・parts.json・TTS inputの整合確認)で、A2記事本文(`article.md`)がOPEN-108のLedger精密化より前の記述をそのまま含んでいることを発見した: (1)Pew統計を「About four in ten said they felt anxious, upset, or lonely」と丸めた表現(B1BはOPEN-108でF-009を42%/25%/24%/56%へ分割済み)、(2)「The report described this as a hard-to-resist habit, not a medical diagnosis.」という一文(B1BはF-011として削除済み、Pew報告書本文に"addiction"/"habit"/"hard-to-resist"のいずれも一度も出現しないことを独立2回fetchで確認済みの、出典未確認の評価)。この一文はA2 Key Phrase 3「hard-to-resist habit」の選定元でもある。A2 fact_qa.json(既存、`verdict=REVIEW_REQUIRED`)はこの2点を`unsupported_specific_claims`として既に指摘済みであり、Fact Checker自体は正しく機能していたが、現行policy(REVIEW_REQUIREDはnon-blocking)のためblockされずそのまま確定していた。A2はB1Bと異なりOPEN-108のLedger精密化後に一度も再生成されていない(今回の指示は「A2は既に完成記事があるため、現行最新記事・support・key phrase lineageを確認したうえで音声化」であり、この確認によって初めて判明した)。この論点は今回の個別Point One差し替え(B1限定)とは独立した、新しいDecisionが必要な事項と判断し、新規OPEN-109として追加した。A2記事の書き換え・再生成は独断で行わず、A2 Audio Stageの最終化(assembly実行・ユーザー試聴提示)を保留した。

### Cost Trace

`er011_open107_audio_stage_03_cost_compute.py`(既存`er011_specfix_cost_compute_01.summarize()`を無変更で再利用)で今回session内の全raw_usage_logを集計。合計¥85.4(151 API call)。内訳: B1本文Re-QA ¥4.2(3件)、Support/Key Phrase再生成 ¥3.2(9件)、Audio Stage(TTS/ASR、同期) ¥70.5(116件、B1 TTS ¥30.1・A2 TTS ¥40.5)、B1 failed segment retry ¥4.1(14件)、Ending-Clarity runtime evidence ¥3.4(9件)。unknownとして推測で埋めた項目は無い。

### 状態

- OPEN-107: `PRODUCTION_WIRED`(実装・B1 call site統合・regression完備。fallback分岐自体の自然発火は本session内では未観測、実発火evidenceは前回Trialに依拠)
- OPEN-108: `RESOLVED`(B1Bテキストは完成・確定) / B1 Audio Stageは`BLOCKED`(OPEN-110待ち)
- OPEN-109(新規): `USER_DECISION_REQUIRED`(A2記事のLedger精密化遡及反映の要否)
- OPEN-110(新規): `USER_DECISION_REQUIRED`(B1 `comment_2`/`comment_3`の新しいTTS content-accuracy失敗モード、B1 episode assembly全体をblocking)

### Git

実装(`er011_ending_clarity_fallback_01.py`、`er003_v1_n3_01_tts_generate.py`の配線変更)・regression test・No.18 B1本文個別差し替え・再QA/Support/Key Phrase出力・Audio Stage出力(narration WAVは`.gitignore`対象外、metadata/JSONのみ)・SSOT更新をcommit/push予定(詳細はcommit SHA参照、本エントリ末尾に追記)。

---

## ER-011-NO18-OPEN108-LEDGER-REFINE-AND-OPEN107-ENDING-FALLBACK-TRIAL-02: OPEN-108(No.18 B1 Fact Checker FAIL)をVerified Fact Ledgerのsource-grounded精密化で解消、OPEN-107(opened誤発音)のEnding-Clarity fallback候補を隔離Trial

- **日付**: 2026-09-02
- **区分**: Track A(OPEN-108)はサービス・生成仕様のデータ精密化(No.18固有のLedgerデータ修正、汎用コード仕様は無変更)。Track B(OPEN-107)はDiagnostic Trial(Implementation Hardening寄り、Production未反映)。

### 背景・スコープ

ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01でNo.18 B1B(`pool_n18_notifications_specfix_v2`)を改善後仕様(Key Phrase/Point関連)で再生成したが、2回連続でFact Checker verdict=`FAIL`(blocking)となりOPEN-108として追加された。また同Decisionで実施したOPEN-107 Diagnostic Trial(`opened`誤発音)は原因範囲を診断したのみで、Production仕様への反映は`USER_DECISION_REQUIRED`のまま維持されていた。本Decisionはユーザーからの詳細指示(管理ID: ER-011-NO18-OPEN108-LEDGER-REFINE-AND-OPEN107-ENDING-FALLBACK-TRIAL-02)に基づき、この2件を独立した2 Trackとして対応する。

Track A/Bとも、No.18の個別ハードコード修正ではなく、既存Production正式経路(Writer/Fact Checker/Support/Key Phrase生成、TTS生成関数)は一切コード変更せず、Track Aは入力データ(Verified Fact Ledger)の精密化、Track BはProduction関数を呼び出す側でのTTS instructionの一時的なmonkeypatchによる隔離Trialとして実施した。

### Track A: OPEN-108 — Verified Fact Ledgerのsource-grounded精密化

**A-1. Fact Checker FAIL時の正式retry上限の確認(仕様の事実確認、変更なし)**

コード調査の結果、`er002_ja_web_research_r3.run_fact_checker_with_gates()`の`MAX_FACT_CHECK_ATTEMPTS=2`は「初回＋(Web検索未使用またはJSON解析/スキーマ不適合時の)技術再試行1回」専用であり、verdict=`FAIL`(信頼できる情報と明確に矛盾)に対する自動Writer再生成retryは現行仕様に**一切存在しない**(`er003_v1_n3_01_articles_generate.py`の該当箇所は`verdict=="FAIL"`を検出した時点で即座に`NG_REVIEW_REQUIRED`を返し、それ以降の工程[Ledger逸脱チェック・Directional Fact Precheck]は実行しない、ER-010-NO9-FACTCHECK-POLICY-AND-POINT-COMPRESSION-DIAGNOSTIC-12のユーザー正式決定通り)。したがって「retry上限を勝手に増やす」ような変更の余地はそもそも存在せず、今回はLedgerを直して1回だけ正式Writer pathを再実行する(再度FAILした場合はさらなる自動retryをせずSTOPする)という、ユーザー指示通りの方針を採った。

**A-2. Fact Checker FAILの実際の指摘内容(2回とも共通)**

`b1b/fact_qa.json`(2回目=b1_retry版)の実データ:
1. Pew統計: 「約4割が不安・動揺・孤独を感じた」という要約は不正確。公式には anxious 42%／lonely 25%／upset 24%、3感情いずれか1つ以上は56%。
2. 「Most did not call their use an addiction; the report framed checking as a hard-to-resist habit」という一文が、確認したPew公式報告書本文で確認できない。
3. Skowronek研究(Scientific Reports)について「second points to a quieter cost before a sound arrives」という解釈が、実際には測定されていない予期的プロセスを示唆している。

**A-3. Root Cause特定 — Ledger自体が不正確だった**

`research/stage_b2_evidence_pack.json`・`stage_b3_vfl.json`を遡って調査した結果、上記2「hard-to-resist habit」はNo.18 Writerの創作ではなく、**Research Layer抽出段階(F-011、evidence_id E-003-05)で既に混入していた不正確な言い換え**だったと判明した。実際のPew報告書本文(`https://www.pewresearch.org/internet/2018/08/22/how-teens-and-parents-navigate-screen-time-and-device-distractions/`)を2026-09-02に独立して2回WebFetchで再確認したところ、"addiction"／"addict"／"habit"／"habitual"のいずれの語も報告書中に一度も出現しないことを確認した(1回目: 個別crawlで該当箇所抽出を試みて不在を確認、2回目: 文書全体を対象に上記4語を横断検索させて不在を確認)。F-009についても、実際の一次数値(anxious 42%／lonely 25%／upset 24%／at least one of these 56%)を同じ独立fetchで確認し、Ledgerの「約40%（約10人に4人）」という丸め表現が不正確だったことを確認した。上記3のSkowronek研究の解釈過多は、F-005/F-006/F-007(Skowronek研究)に「音が鳴る前」等の予期的解釈を禁止する明示的なwriter_guidanceが存在しなかったことが一因と判断した。

**A-4. Ledger精密化の内容**(`er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2/research/verified_fact_ledger.txt`を直接編集、ヘッダーに注記3として変更履歴を明記)

- **F-009**: 「約40%（約10人に4人）」の丸めを、実際の内訳(anxious 42%／lonely 25%／upset 24%／at least one of these 56%)へ分割。3感情は排他的カテゴリでない旨のambiguity注記、および「3感情まとめる場合は約4割でなく56%を使う」旨のwriter_guidanceを追加。
- **F-011**: 削除。削除理由(実source本文に"addiction"/"habit"系の語が一度も出現しないことを独立2回確認した結果であり、単なる「PASSさせるための削除」ではないこと)を、削除箇所自体に明記して残した。Pew由来で使える情報がF-008/F-009/F-010のみである旨のwriter_guidanceを追加。
- **F-002/F-003**(Upshaw研究、通知音の認知制御影響): 直接測定は反応時間遅延とN2振幅増大のみであり、「自動的」「不随意的」という断定を避け著者解釈である旨を明記させるwriter_guidanceを追加。
- **F-005/F-006/F-007**(Skowronek研究、スマートフォンの物理的存在): 両条件とも通知を受信していないことが実験の核心条件であり、「音が鳴る前」「通知の予期」等の予期的プロセスを示唆する表現をしないよう明示するwriter_guidanceを追加。

新しいFactの追加は行っていない(既存Factの数値精密化・不正確なFactの削除・解釈範囲の明確化のみ)。Fact Checker自体のコード・閾値・retry仕様、およびNo.18本文(article.md)への直接手修正はいずれも行っていない。

**A-5. Ledger精密化後の再生成結果**

既存Production正式Writer path(`gen.run_one_pattern`、Fact Checker含め無変更)からB1Bを1回だけ再生成(`er011_no18_open108_b1_ledger_refined_regenerate_01.py`)した結果:

- `fact_verdict`=`REVIEW_REQUIRED`(non-blocking advisory。残る指摘は、Upshaw論文の最終解析対象数[行動69人/ERP54人]が参加者数73人と別である旨の注記、Skowronek研究のミュート条件と移動条件を直接比較したわけではない旨の注記、Pewの即時返信設問文の言い換え精度など、いずれも軽微な精度論点で、当初のFAILだった3論点[Pew丸め・hard-to-resist habit・Skowronek予期的解釈]はいずれも解消)
- `ledger_status`=`LEDGER_COMPLIANT`(MINOR 1件のみ: 「Two peer-reviewed studies」という表現がLedgerに明記されていない出版属性を付加している、との指摘。MINORのため記録のみでblockingではない)
- Point Overlap QA: `point_one_vs_point_two`=0.083、`point_two_vs_point_one`=0.12(いずれもthreshold 0.4未満、flagged=false)、Full Story-vs-各Pointも含めflagged=falseで全PASS
- Point Value QA: Point One/Two とも6項目全てPASS(記事全体retry 0回で解消)

続けて実Production関数(`sc.run_b1_scaffold`/`sc.run_key_phrases`/`support_mod.run_support_fact_check`、いずれも無変更)を新article.mdに対して再実行(`er011_no18_open108_b1_support_regenerate_01.py`、A2は対象外)した結果、Support(Preview/Comment1-4)全てOK、`support_fact_check verdict`=PASS(issue 0件)、Key Phrase `kp_status`=`CANONICALIZATION_PASS`、`kp_redundancy_status`=`REDUNDANCY_PASS`。

**A-6. OPEN-108の状態**: `RESOLVED_PENDING_USER_TEXT_REVIEW`。B1Bの記事・Support・Key Phraseは全て完成状態になったが、ユーザーが再生成された全文を確認するまでAudio Stageは実行しない(タスク指示通り)。

### Track B: OPEN-107 — Ending-Clarity Fallback Trial

**B-1. 設計方針**

通常TTS instructionを常時複雑化せず、**通常retryでもNGが続いたsegmentだけ**にEnding-Clarity instructionを追加するfallback候補を検証する。既存instructionを全面置換せず末尾へAND方式で追加、`opened`/`-ed`への直接hardcodeは避け、語尾・最終音素一般に適用可能な文言とした:

> " Pronounce grammatical endings and final sounds clearly enough to remain audible, without exaggerating them or disrupting the natural rhythm of the sentence."

(ユーザー提示の意図例にほぼ準拠。前回Trial[ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01]のPhase Bで使った"-ed"を名指しした文言とは意図的に変更し、過剰な強調を明示的に禁止する句を追加した)

**B-2. 実施方法**(`er011_open107_ending_clarity_fallback_trial_02.py`)

前回Trial(`er011_open107_opened_tts_diagnostic_trial_01.py`)のNormal(通常instruction)実データを可能な限り再利用し、新規課金はEnding-Clarity側の生成のみに限定した。Production相当条件(条件6)は、実Production関数`er003_v1_sing01_news_tail_fix.generate_news_narration_wide_margin()`(Batch API・review_lock 3attempt cascade込み、無変更)をそのまま呼び出しつつ、呼び出し直前にのみ`er003_b1_p9a_audio.ENGLISH_STYLE_PREFIX`をEnding-Clarity版へ一時的にmonkeypatchし、呼び出し後は必ず元の値へ復元する方式を取った(ソースファイル自体への恒久的な変更は一切なし)。

**B-3. NG率比較**

| Condition | Normal PASS/n | Ending-Clarity PASS/n | Normal NG率 | Ending-Clarity NG率 |
| --- | ---: | ---: | ---: | ---: |
| opened単独 | 3/3(reuse) | 1/1(new) | 0% | 0% |
| be opened | 3/3(reuse) | 1/1(new) | 0% | 0% |
| does not have to be opened | 3/3(reuse) | 1/1(new) | 0% | 0% |
| 完全な一文(文脈なし、raw pipeline) | 2/3(reuse) | 3/3(new) | 33% | 0% |
| 完全な一文+文脈(raw pipeline) | 2/3(reuse) | 1/3(new) | 33% | 67% |
| Production相当(実Production関数、Batch+retry cascade) | 0/3(reuse、実本番失敗データ) | 2/2(new、いずれもouter run 1attempt目でPASS) | 100% | 0% |

短句3種は天井効果(元々NGなし)のため改善余地が小さく、Ending-Clarityでも退行なしを確認したのみ(各1回のみ実施)。**結果はcondition依存で一様ではない**: raw pipelineでの「完全な一文+文脈」条件はEnding-Clarityでむしろ悪化した(1/3)が、最も重要な実Production相当条件(Batch API+3attempt retry cascadeを含む実際のコード経路)では、Normal(実際のNo.18本番失敗データ、3attempt全滅)に対しEnding-Clarityは2/2(両方とも1attempt目でPASS)と大幅に改善した。小標本(raw pipelineはn=3、Production相当はn=2)のため統計的な確定はできず、raw pipeline条件とProduction相当条件で結果の方向が逆転している点は技術的に未解明であり、率直にそのまま報告する(Production相当条件の方がretry cascade分のASR再検証機会が多いことが一因である可能性はあるが、確証はない)。

**B-4. Naturalness User Check**

ユーザー試聴用Artifactに、(A)通常instructionで正常だった音声、(B)通常instructionでending NGだった音声、(C)Ending-Clarityでraw pipeline条件でも悪化した音声(D、参考)、(E)Ending-ClarityでProduction相当条件においてPASSした音声、を並べて掲載した。加えて、実際のB1B `point_two`(Normal生成、既存Production音声)の末尾3秒と、Ending-Clarity版`in_one_line`音声を結合したAssembly比較音声(Trial環境限定、Production episodeへの正式反映ではない)も掲載し、fallback segmentだけ差し替えたときの前後接続の自然さをユーザーが判断できるようにした。Claude Codeはこれらの自然さを自ら最終承認していない。

**B-5. OPEN-107の状態**: `USER_DECISION_REQUIRED`(維持)。Production instruction・retry構成・Validatorへの変更は今回も一切実施していない。Ending-Clarityは技術的に有望な候補だが、raw pipeline条件での悪化という反証データがあり、かつユーザーの自然さ試聴確認が正式採用の前提条件であるため、Trial 2回目を終えてもなお`REJECTED`/`VALIDATED`のいずれにも分類せず、`USER_DECISION_REQUIRED`のまま維持する。

### Cost Trace(Track A/B、分離)

- Track A(OPEN-108、Ledger精密化後Writer+Support再生成): ¥9.4(Writer/QA ¥6.5、Support/Key Phrase ¥2.9、計15 API call)
- Track B(OPEN-107、Ending-Clarity Fallback Trial): ¥7.5(TTS+ASR、計22 API call)
- 前回セッションで発生したSupport段階のcost logger未接続([ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01]で報告済み)は、今回は両scriptとも`cl.install()`を個別に呼び出し正しく記録されており再発していない。

### Git

変更ファイル: `er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2/research/verified_fact_ledger.txt`(Ledger精密化)、`{...}/b1b/*`(article.md/Support/Key Phrase一式の再生成)、新規script(`er011_no18_open108_b1_ledger_refined_regenerate_01.py`／`er011_no18_open108_b1_support_regenerate_01.py`／`er011_open107_ending_clarity_fallback_trial_02.py`／`er011_open108_open107_02_cost_compute_01.py`)、`er011_output/open107_ending_clarity_fallback_trial_02/*`(Trial結果・音声・cost)、SSOT(`OPEN_ITEMS.md`/`DECISION_LOG.md`)。commit/push状況は本Decision反映後にコミットして記録する。

### 参照元

[ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01](#er-011-no18-production-spec-improvement-01-no18で発見された3件の問題を汎用production仕様として改善key-phrase人称一般化key-phrase-set-redundancy-qapoint-role-planningpoint-value-qano18を改善後仕様で再生成open-107-diagnostic-trial実施)、[OPEN_ITEMS.md](OPEN_ITEMS.md) OPEN-107/OPEN-108

---

## ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01: No.18で発見された3件の問題を汎用Production仕様として改善(Key Phrase人称一般化・Key Phrase Set Redundancy QA・Point Role Planning+Point Value QA)、No.18を改善後仕様で再生成、OPEN-107 Diagnostic Trial実施

- **日付**: 2026-09-02
- **区分**: サービス・生成仕様の新規追加(Production Wired)。

### 背景・目的

前回(ER-011-NO18-DISCOVERY-WHY-FULL-PRODUCTION-RUN-01)のNo.18試聴で、
ユーザーから以下3件の問題が指摘された。ユーザーは明示的に「No.18の
特定語句やPointを直接書き換える対応は禁止」「個別ハードコードは禁止」
とし、(1)現行仕様・実装を確認 (2)なぜ現行仕様がこのOutputを許したのか
特定 (3)汎用仕様を変更 (4)テスト追加・実行 (5)正規Production経路から
No.18を再生成 (6)出力を確認、という順序を明示的に指示した。本Decisionは
この順序で実施した記録である。

### A. Key Phrase: 文脈依存の人称表現(「catch their attention」「a piece
of your attention」)

**現行仕様確認**: 選定prompt(`b1_p2_keywords_l_prompt_template.txt`)には
人称代名詞の扱いに関する指示が一切無かった。canonicalization prompt
(`b1_p2_keywords_canonicalization_prompt_template.txt`)の「文脈限定語の
除去」ルールは the/a/an/this/that/所有限定詞などを**除去(削除)**する
ことしか指示しておらず、辞書的な一般形への**置換**は一度も指示していな
かった。さらに、`validate_canonicalization_item()`のRule7(source_span内
の連続部分文字列でなければ拒否)は、「their」→「someone's」のような
置換を機械的に「捏造」として拒否する構造になっていた(仮にLLMが正しく
一般化しても、既存validatorが弾く設計だった)。

**原因**: 選定・canonicalizationいずれの段階にも、人称代名詞・所有格を
一般化する指示が存在せず、かつ既存の構造的安全装置(Rule7)がこの種の
正当な置換すら通さない設計になっていたこと。

**変更**: `er003_key_words_canonicalization.py`へ、新しい変換カテゴリ
`generalize_person_dependent_reference`を追加した。閉じた語彙集合
(my/your/his/her/its/their/our/you/they/he/she/yourself/himself/herself/
themselves/yours/theirs → one's/someone's/somebody's/someone/somebody/
one/oneself)による**1対1のトークン置換のみ**を構造的に許可する
`_is_valid_person_generalization()`を実装し、Rule7の例外パスとして
`validate_canonicalization_item()`へ統合した(既存の挙動は
`normalization_reason`を渡さない限り完全に無変更、既存43テスト全PASS
で確認)。新QAフィールド`qa_person_reference_generalized`を追加。
canonicalization promptへルール3として追加し、「特定の代名詞を含むこと
自体が意味・用法に必要な場合は機械的に変換しない」という例外も明記した
(機械的hard ruleにはしない)。単体テスト6件(`PersonReferenceGeneralizationTests`)
で、正しい置換の許可・許可されていない置換先の拒否・reason不一致時の
拒否・語数不一致時の拒否・無関係語変更時の拒否を確認。

### B. Key Phrase: 5件相互の意味重複(「catch their attention」と
「a piece of your attention」が同じ「注意を奪われる」概念)

**現行仕様確認**: 既存QA(`er003_key_words_canonicalization.py`の
QA_FIELDS)は各候補を個別にsource_span/display_phraseとの関係でのみ
判定しており、5件相互の比較は一切行っていなかった。選定promptの優先
順位「汎用性」は各候補単体の性質であり、候補同士の重複は評価しない。

**原因**: 5件セット全体としての重複を評価するQA工程が、そもそも
存在しなかったこと。

**変更**: 新規モジュール`er011_key_phrase_set_redundancy_qa_01.py`を
追加した。canonicalization完了後の5件について、意味(meaning)・使用
場面(usage_context)・文法/構文上の学習価値(grammatical_teaching_value)・
記事内で担う概念(conceptual_role)の4観点で、C(5,2)=10ペア全てを
1回のLLM呼び出しで判定する。1つでも`is_near_duplicate=true`があれば
`REDUNDANCY_NG`とし、`er003_v1_n3_01_scaffold_generate.py::run_key_phrases()`
がKey Phrase選定(方式L)からやり直す(最大2回、`gen.POINT_OVERLAP_ARTICLE_RETRY_MAX`
と同じ値をそのまま踏襲、新しい上限を独自に発明しない)。retry時は前回の
重複ペアを選定promptへ診断メモとして追加する(`build_redundancy_diagnostic_note()`)。
記事本文・Full Storyは対象外(選定+canonicalization+redundancy QAの
3工程のみ再実行、既存のPoint Overlap記事全体retryとは独立)。単体テスト
11件(`er011_test_key_phrase_set_redundancy_qa_01.py`)でプロンプト構築・
構造validator・gate(技術失敗retry・NG時は再試行しない)を確認。

### C. Point: 「重複しない」だけでなく「新しい価値」を要求する

**現行仕様確認(ユーザー指示の実際の箇所調査)**:
- Point Role Planning: 存在しない(過去のTrial `er009_n1_point_role_planning_11.py`
  はA/B比較でDiagnostic Full Retryに敗れ[0/3 vs 3/3]不採用のまま、
  Production未実装)。
- Writer Prompt: `COMMON_BLOCK_TEMPLATE`の「Point One / Point Twoの役割」
  節は、切り口/示唆/背景/心理/社会的含意/別の因果/実生活上の解釈/意味
  づけを列挙するのみで、「留保・免責事項だけで構成してはいけない」
  「新しい価値を加えなければならない」は一度も明示していなかった。
- Point Overlap QA: `er008_point_overlap_qa_18.py`のlexical overlapは
  Point各々とFull Storyとの語彙的重複のみを見る一方向指標であり、
  Point One対Point Two自体は一度も評価されていなかった。「重複していない
  が無価値」なPointを検知する仕組みは存在しなかった。
- Retry/再生成処理: Diagnostic Full Retry(`er009_diagnostic_full_retry_modules_12.py`
  + `run_one_pattern()`のretryループ)はlexical overlap flagのみを
  トリガーとしていた。

**原因**: (a) Writer promptが「重複しない」ことしか要求しておらず
「価値を加える」ことを明示していなかった。(b) 既存QAが語彙的重複しか
判定せず、意味的な「新しい価値」の有無・Point One対Point Two自体の
重複を判定していなかった。No.18 A2のPoint Two(留保のみ構成)は、
Point Oneとは異なる語彙を使っていたためlexical overlap QAを通過した。

**変更**: 2段構成の一般仕様を追加した。

1. **Point Role Planning**(新規モジュール`er011_point_role_value_planning_01.py::
   run_point_role_planning()`): Full Article Writer呼び出しの直前に、
   Verified Fact Ledgerに基づいてPoint One/Twoそれぞれの`role`/
   `new_listener_takeaway`/`evidence_anchor`/`why_it_matters`/
   `must_not_overlap_with_full_story`/`must_not_overlap_with_other_point`
   を計画させる、小さな独立JSON schema呼び出し。既存のMarkdown出力型
   Writerアーキテクチャは変更せず(大規模な構造変更のリスクを避ける)、
   `build_role_planning_block()`で計画結果をWriter promptへ文字列として
   挿入する設計にした。初回生成・Diagnostic Full Retryの各attemptで
   毎回再計画する(前回の計画を使い回さない、既存のDiagnostic Full
   Retry「生成単位全体をLedgerから再生成する」方針をPlanningにも適用)。
2. **Point Value QA**(`run_point_value_qa()`): 生成後、実際のPoint本文
   に対し独立したLLM呼び出しで6項目(`qa_not_caveat_only`/
   `qa_not_full_story_paraphrase`/`qa_not_other_point_paraphrase`/
   `qa_explains_why_it_matters`/`qa_specific_not_generic`/
   `qa_adds_new_value`)を判定する。1件でもFAILなら`status="NG"`。
3. **Point One対Point Twoのlexical overlap**を`run_point_overlap_qa_and_regenerate()`
   へ追加(双方向、既存の`overlap_qa.flag_possible_paraphrase()`をその
   まま再利用、新規関数は作らない)。
4. 上記3つを`still_flagged = lexical_flagged or value_qa_flagged`として
   既存のDiagnostic Full Retryループへ統合し、retry時はvalue QA NGの
   理由(`build_value_qa_diagnostic_note()`)を既存の診断section直後に
   追加する。`COMMON_BLOCK_TEMPLATE`本体にも「Pointが実際に新しい価値を
   持つこと」節を追加し、6つの禁止パターンを明記した。

単体テスト9件(`er011_test_point_role_value_planning_01.py`)でrole
planningプロンプト構築・value QA判定・診断メモ生成を確認。既存の
`run_one_pattern`統合テスト(3ファイル、計42件)を、新しい2呼び出しを
mockするよう更新し全PASSを確認(既存の制御フロー検証の意図は変更せず、
新規呼び出しの追加分だけをmockした)。

### D. 正規Production経路からのNo.18再生成(実データ検証)

既存のNo.18 research出力(`pool_n18_notifications`のverified_fact_ledger.txt
等)をそのまま再利用し(Ledger自体は無変更)、新しい出力先
`pool_n18_notifications_specfix_v2`で、改善後の`gen.run_one_pattern()`
(Writer)→`support_mod.run_support_for_theme()`(Support/Key Phrase)を
実際に呼び出した。旧No.18(`pool_n18_notifications`)は一切変更していない。

**A2**: 初回候補でPoint Value QAは両Point PASS。lexical overlap
(Point Two対Full Story=0.629)のみでflagされ、Diagnostic Full Retry
(Point Role Planning再計画込み)が1回発火し解消(retry後: Point One
overlap=0.273、Point Two overlap=0.321、Point One対Point Two=0.03/0.036、
value QA両方PASS)。Fact Checker verdict=REVIEW_REQUIRED(non-blocking、
5件の指摘、既知のPew精度論点等)。Ledger Deviation=LEDGER_COMPLIANT
(MINOR 2件、MAJORなし、Local Rewrite不発火)。Key Phrase: canonicalization
PASS、Set Redundancy QA=REDUNDANCY_PASS(10ペア全て重複なし)。

**B1B**: **初回候補でPoint Value QAが実際にNGを検出した**(Point One
が`qa_not_full_story_paraphrase`/`qa_adds_new_value`でFAIL、理由:
「見えない努力」等の言い換えに留まり新しい事実・示唆がほとんど無い。
このPoint Oneのlexical overlapは0.379で、旧閾値0.40未満のため**旧仕様
ではPASSしていたはずの実例**)。Diagnostic Full Retry(Point Role
Planning再計画込み)が1回発火し、retry後はlexical overlap・value QAとも
全PASS(Point One overlap=0.25、Point Two overlap=0.122、Point One対
Point Two=0.083/0.049)。Key Phrase: canonicalization PASS、Set
Redundancy QA=REDUNDANCY_PASS。ただしFact Checker verdict=**FAIL**
(blocking、既存ポリシー通りLedger Deviation以降は未実行)。指摘内容は
(1)Pewの「約4割が不安・孤独・動揺」という記述の精度(実際は42%/25%/24%、
いずれか56%、複数の解釈可能な表現、前回No.18でもREVIEW_REQUIREDとして
指摘済みの既知論点)、(2)Skowronek研究を「laboratory tests」と表現した
記述(Scientific Reports論文は参加者の通常の日常環境で実施されたと
記載されており、"laboratory"という単語自体がFact Checkerに不整合と
判定された)。既存のFact Checker policyに従い自動続行せずNG_REVIEW_REQUIRED
としてstop。同一Production経路(`gen.run_one_pattern`、Fact Checkerは
無変更)でB1Bのみ1回再試行したが、2回目の候補も別の理由でFact Checker
FAIL(Pewの同一精度論点+Skowronek研究の実施環境記述の不整合、内容は
1回目と異なるが同種の論点)となった。これはFact Checkerの既知の
非決定性(OPEN-92、CURRENT_SPEC.md「Fact Safety」節)、または当該Pew
統計の言語化そのものが構造的に精度を欠きやすい論点である可能性が高く、
今回追加した3つの新仕様(Key Phrase・Point)とは無関係な既存の問題で
あるため、本Decisionのスコープでは追加のPromptハードコード・Ledger
書き換えは行わず、B1Bのshippable candidate取得は別タスクのフォロー
アップとする(ユーザー確認事項として後述)。

### E. OPEN-107(`opened`のTTS Diagnostic Trial、Productionと分離)

`er011_open107_opened_tts_diagnostic_trial_01.py`で、No.18 B1原稿
("Your phone does not have to be opened to become part of the task.")は
一切変更せずPhase A(原因範囲の診断)・Phase B(回復策の評価)を実施した。
model/voice/TTS instruction/trim方式は、実際にNo.18 B1 in_one_lineを
生成したのと同一の値(`gemini-2.5-pro-preview-tts`/Aoede/`ENGLISH_STYLE_PREFIX`/
trim margin 0.35秒)を使用。試行回数は各条件3回を事前確定(既存の
content-attempt慣行を踏襲)。

**Phase A結果**:
| 条件 | 内容 | 結果 |
|---|---|---|
| 1 | "opened"単独 | 3/3 CORRECT_OPENED |
| 2 | "be opened" | 3/3 CORRECT_OPENED |
| 3 | "have to be opened" | 3/3 CORRECT_OPENED |
| 4 | "does not have to be opened" | 3/3 CORRECT_OPENED |
| 5/6 | 完全な一文(文脈なし) | 2/3 CORRECT、1/3 MISPRONOUNCED_OPEN |
| 7 | 完全な一文+後続文(文脈あり) | 2/3 CORRECT、1/3 MISPRONOUNCED_OPEN |
| 8 | 実Production関数で単独segment生成 | 1/1 CORRECT(attempt 1でPASS) |
| 9 | 実際のNo.18本番実行データ(2文結合、再利用・追加課金なし) | 3/3 MISPRONOUNCED_OPEN(STOPPED) |

**推定failure class**: 「前後の音との連結・弱化」(connected speech
reduction)。断片(条件1-4、最長5語の"does not have to be opened"を
含む)は12/12(100%)正解だったのに対し、完全な文法的な一文(条件5/6・7、
主語+助動詞連鎖+受動不定詞+目的節を含む完全な文プロソディ)は6件中2件
(約33%)で誤発音した。文脈(前後に別の文があるかどうか)・segment長
自体は結果を有意に変えなかった(条件5/6と条件7がほぼ同率)。特定単語
「opened」単独では一度も誤らなかったため、単語自体の発音問題ではない。

**Phase B結果(回復策の評価、対象は条件5/6の完全な一文)**:
| 回復策 | 結果 |
|---|---|
| segment短分割と再結合("Your phone does not have to be opened"のみを別呼び出し) | 2/2有効attempt中2/2 CORRECT_OPENED(1件は技術的呼び出し失敗、発音とは無関係) |
| 語尾を明瞭に読むTTS instruction追加(AND方式、既存instruction削除なし) | 3/3 CORRECT_OPENED |
| voice変更(Aoede→Charon) | 3/3 MISPRONOUNCED_OPEN(悪化、有効な回復策ではない) |

**判定**: 有効そうな回復策の候補は「segment短分割」「語尾明瞭化TTS
instruction」の2つ(小標本のため確定的ではない)。「voice変更」は
無効。本Trialは診断・回復策候補の提示までであり、**新しいProduction
仕様・例外処理は本Decisionでは追加しない**(ユーザー指示通り、Trial
結果が出るまでは追加しない方針を遵守)。OPEN-107は`USER_DECISION_REQUIRED`
のまま維持し、次項Fに候補を整理する。

### F. Trial結果に基づくOPEN-107の選択肢(ユーザー確認事項)

1. 「語尾を明瞭に読むTTS instruction」をKey Phraseのfunction-word
   reductionと同じAND方式パターンで、in_one_line等の長文segment全般へ
   汎用的に適用する候補として正式検討する(Phase B実測3/3 PASS、ただし
   n=3のため統計的に確定的ではない)。
2. 「完全な文プロソディで結ばれた長い一文」自体をTTS前に自動分割し、
   分割後に結合する汎用機構を検討する(Phase B実測2/2 PASS、実装コスト
   は上記1より高い)。
3. 現状維持(既存の3回retry cascade任せ)とし、恒久課題としてOPEN-102/
   103/104と同様`DEFERRED / NON-BLOCKING`で追跡する。

### G. Production/Trialの実測Cost(分離集計、公式pricing snapshot使用)

`er011_specfix_cost_compute_01.py`で、Production regeneration(Writer×2
level+B1B retry1回)とTrialを別々に集計した。

- **Production Writer regeneration**: writer_a2 13 calls ¥11.4、
  writer_b1(初回+retry) 18 calls ¥15.1、**小計¥26.5(31 calls、実測)**
- **Support(Key Phrase/Comment生成)**: **実測ログ欠落(unknown)**。
  Support実行時にcost loggerの`cl.install()`呼び出しを行うスクリプトを
  経由しなかったため、実際にAPI呼び出しは発生し正常に完了したが
  usage/costのレコードが記録されていない(実装ミス、正直に記録する。
  過去の同種Support実行[No.18初回実行、A2¥3.0/B1¥4.3]から参考規模は
  推測できるが、これは今回のactualではないため合算しない)
- **OPEN-107 Diagnostic Trial**: Phase A ¥9.5(29 calls)+Phase B ¥2.4
  (6 calls)+ASR(untagged、正しく価格計算済み)¥0.6(32 calls)、
  **小計¥12.4(67 calls、実測)**
- Production/Trialのcostは明確に分離し、混同していない。Support分の
  欠落は次回同種作業でのcl.install()呼び出し漏れ防止のteaching item
  として記録する。

### H. Git・関連ファイル

変更ファイル: `er003_key_words_canonicalization.py`、
`er003_v1_translator_briefs/b1_p2_keywords_canonicalization_prompt_template.txt`、
`er003_v1_n3_01_scaffold_generate.py`、`er006_pool_pilot_01_support.py`、
`er003_v1_n3_01_articles_generate.py`、新規`er011_key_phrase_set_redundancy_qa_01.py`、
`er011_point_role_value_planning_01.py`、`er011_open107_opened_tts_diagnostic_trial_01.py`、
`er011_no18_specfix_v2_production_run_01.py`、`er011_no18_specfix_v2_b1_retry_01.py`、
`er011_specfix_cost_compute_01.py`、テスト`er003_test_key_words_canonicalization.py`
(追加分)・`er011_test_key_phrase_set_redundancy_qa_01.py`・
`er011_test_point_role_value_planning_01.py`、および既存3テストファイル
の統合テストへのmock追加。個別ハードコードは無し(単体テストで確認済み、
既存の`NoBlacklistOrHardcodeImplementationTests`も無変更のままPASS)。

### 現在の状態

- No.18 A2(specfix_v2): Writer/Support完成、Fact Checker REVIEW_REQUIRED
  (non-blocking)、audio未生成(ユーザーがテキストを確認するまで生成しない)
- No.18 B1(specfix_v2): Writer/Support完成もFact Checker FAIL(blocking)
  でNG_REVIEW_REQUIRED、shippable candidate未取得(既存Fact Checker
  policyに従いこのDecisionでは追加対応せず)
- 旧No.18(`pool_n18_notifications`、A2完成audio・B1音声ブロック中)は
  無変更のまま維持
- OPEN-107は`USER_DECISION_REQUIRED`のまま(Trial結果で情報を追加、
  新Production仕様は未採用)

---

## ER-011-NO18-DISCOVERY-WHY-FULL-PRODUCTION-RUN-01: No.18「Why Is It So Hard to Ignore a Notification?」Discovery/Why型 正式Production実行(A2完成/B1新規TTS失敗モードでSTOP)

- **日付**: 2026-09-02
- **区分**: サービス・生成仕様の新規適用(既存Production Wired仕様のみを使用、新規仕様追加は無し) + 新規bug発見(OPEN-107)。

### A. Topic登録
POOL_TOPIC_MASTER.mdのNo.18(旧: "A Busy Restaurant Just Feels More Trustworthy—But Why?"、`PLANNED`のまま未生成)を、ユーザー正式指示によりNo.18「Why Is It So Hard to Ignore a Notification?」(通知を無視するのが、なぜこんなに難しいのか)へ差し替えた(ユーザーが3択のうち「No.18として新規登録」を選択)。旧No.18は生成済み成果物が無く差し替えによる損失は無いため、No.9追加時の旧No.15削除と同じ扱いで20件のリストから削除・注記のみ保持。既存No.13「The Notification Question: Why Apps Want Your Attention」(アプリ側の設計意図を扱う別視点)とは切り口が異なる別テーマとして無変更のまま両立させる。theme_id=`pool_n18_notifications`。

### B. Research(実出典3件)
査読付き学術論文2件+Pew Research Center調査1件を実際にWeb Search/Web Fetchで確認のうえ`raw_sources.json`を作成: (1) Upshaw, Stevens, Ganis, Zabelina (2022-11-17, PLOS ONE, DOI 10.1371/journal.pone.0277220) — 通知音がEEGのN2振幅・反応時間に有意な影響を与える実験研究、(2) Skowronek, Seifert, Lindberg (2023-06-08, Scientific Reports, DOI 10.1038/s41598-023-36256-4) — スマートフォンの物理的存在のみで注意成績が低下する実験研究、(3) Pew Research Center (2018-08-22、10代743人・保護者1,058人対象) — 10代の72%が起床後すぐ通知確認、約4割(内訳: 不安42%/孤独25%/動揺24%、いずれか56%)が携帯電話不在で不安等を感じる。実Production研究経路(`er006_pool_pilot_01_research.run_research_for_theme`)で実行、facts=12件中VERIFIED 11・PARTIALLY_SUPPORTED 1、rejected/needs_external_check=0。

### C. Writer(A2/B1、実Production path)
`er006_pool_pilot_01_writer.run_writer_for_theme`(blueprint=None、baseline)経由で`er003_v1_n3_01_articles_generate.run_one_pattern()`を実行。A2/B1とも`status=OK`、Point overlap QA(retry 0/2で通過、overlap無し)、Ledger Deviation Checker(hook-aware): B1は`LEDGER_COMPLIANT`(0 deviations)、A2は初回`LEDGER_DEVIATION`(MAJOR 1件)→Local Rewrite Loop cycle 1で解決し`LEDGER_COMPLIANT`(0 MAJOR)。Fact Checker: A2/B1とも`REVIEW_REQUIRED`(非blocking advisory、CURRENT_SPEC.md現行policyどおりProduction継続)。REVIEW_REQUIRED理由(両levelで概ね共通、機械的に一覧化・ユーザー最終レビュー用): (1) 記事本文の「約4割が worried, upset, or lonely」という表現は、Pew原資料の実際の内訳(不安42%/孤独25%/動揺24%、いずれか1つ以上56%)からすると曖昧または不正確、(2) Upshaw論文の知見(通知音条件でN2振幅・反応時間に有意差)を「音が自動的・不随意的に注意を奪った」と断定する記事の表現は、論文自体の解釈より強い可能性、(3) B1の「Most did not call this addiction」「the report described it as a hard-to-resist habit」という記述は、Pew原資料の直接表現としては確認できない要約・解釈。今回は非blockingのため記事はそのまま採用し、REVIEW_REQUIRED内容を本Decisionとしてユーザーへ一覧化する(独断でのRewrite・再生成は行っていない)。Directional Fact Precheck: B1=`PASS`、A2=`DIRECTION_REVIEW_REQUIRED`(72%という同一数値をledgerとscript双方が参照しているが方向表現が片方にしかなく機械的に一致判定できないという性質のもので、conflictsは0件、`run_one_pattern()`の既存実装上非blocking)。

### D. Support(Preview/Comment1-4/Key Phrases)
`er006_pool_pilot_01_support.run_support_for_theme`(blueprint=None)経由で実行。A2は`support_fc_verdict=PASS`・Key Phrase`CANONICALIZATION_PASS`(5件)。B1は`support_fc_verdict=MINOR_FIX`(issue 1件、非blocking)だが、Key Phrase選定が初回`KEY_WORDS_STRUCTURE_INVALID`(理由: ja_glossに括弧書き補足「（注意が）〜に引っ張られる」が含まれ、Key Phrase括弧禁止仕様に抵触)。`run_key_phrase_selection()`はmax_attempts=1の単発gate設計であり(スコープ内自動retryなし)、既存Production前例(`er003_v1_iran01_a2_kp_retry.py`、「初回KEY_WORDS_STRUCTURE_INVALID対応」)と同一の対処方法として、実Production関数(`er006_pool_pilot_01_support.sc.run_key_phrases`、Trial専用scriptではない)をそのまま再呼び出す最小限のretry補助script(`er011_no18_b1_kp_retry_01.py`)を作成し、attempt 1で`CANONICALIZATION_PASS`(5件)に解消した。新しい仕様判断・hardcodeは行っていない。

### E. Audio Stage(同期TTS、No.9と同一方式)
ユーザー指示によりStandard同期TTS経路(`enable_sync_tts_mode()`、No.9の`er009_n1_production_integration_01.py`と全く同一の切替方式)を使用し、Production Batch経路(`er006_batch_tts_wiring_01.py`)自体は無変更のままプロセス内でのみ関数を差し替えた(`finally`で確実に復元)。実際のTTS呼び出しは`p7a.make_tts_call_fn_for_model()`(`client.models.generate_content()`への単発blocking呼び出し、`batches.create()`・job polling不使用)であることをコード経路・raw_usage_log.jsonlの提供者別レコード(全て即時応答、job_id/poll系フィールド無し)で確認した。
- **A2**: 全segment(topic_intro/japanese_title/preview/comment_1-4/point_one_heading/point_two_heading/full_story_part1-2/point_one/point_two/in_one_line + Key Phrase 5件×en/ja)が`status=OK`。Episode assembly成功: `English_Your_Way_A2_POOL_N18_NOTIFICATIONS.wav`、378.634秒、clipping無し、peak 0.83891、sha256`f6fa92875079e72876ec5e18fd40107ffee45c9068a242d23b637655f7a0245b`。
- **B1**: `topic_intro`〜`point_two`・Key Phrase 5件×en/jaは全て`status=OK`。**`in_one_line`のみ3attemptとも`status=STOPPED`**(理由: 3回試行してもASR検証に合格せず)。canonical text "Your phone does not have to be **opened** to become part of the task...."に対し、3attemptとも一貫してASRが"...does not have to be **open** to become part..."(過去分詞"opened"の"-ed"語尾が脱落し形容詞"open"のように発話)と書き起こし、`audio_classification=TRUE_CONTENT_MISMATCH`(実際の内容不一致、ASRの誤認識ではない)と判定。3attemptの上限に到達し`STOPPED`、既存のAudio Validation Gate(`verify_episode_audio_validation_gate()`)が仕様通りfail-closedで動作し、B1のepisode assemblyを`RuntimeError: EPISODE_BLOCKED_BY_AUDIO_VALIDATION`で正しく中止した(B1のnarration/assembledディレクトリにepisode成果物は存在しない)。

### F. 新規Open Item(OPEN-107)
上記E節のB1 `in_one_line`の"opened"→"open"語尾脱落は、No.9までに確立した既存TTS失敗モードcatalog(OPEN-102数字複合語バグ・OPEN-103 `default`単語誤発音・OPEN-104日本語ASR窓ずれ)のいずれとも異なる新しいcontent-accuracy失敗モード候補と判断した(3attemptとも同一の誤りだった一方、観測は1文のみでありRoot Cause特定は行っていない。断定していない)。No.18 A2側は同一原文の言い換え("without being opened"、Key Phrase専用のMinimal instruction経路)で問題なくPASSしているため、A2には影響しない。指示書の明示的なSTOP条件(「新しいTTS failure mode」「retry/fallback上限到達」)に該当するため、新しいpronunciation safeguard仕様を独断で追加せず、OPEN_ITEMS.mdへOPEN-107として新規登録し`USER_DECISION_REQUIRED`でここでSTOPした。

### G. Cost Trace(実測)
raw_usage_log.jsonl(全146 API call、全て`usage_source=OFFICIAL_API_RESPONSE`の実測値)を、既存の公式pricing snapshot(`er005_output/cost_baseline_01/pricing_snapshot.json`、`compute_topic_cost.py`と同一参照元)で集計(`er011_no18_cost_compute_01.py`、新規)。TTS/ASRのretry/fallback判定はsegment名がlogに記録されているため実測(推定ではない)。合計: **¥90.9(≈$0.568、1USD=160円)**。内訳(円): Research ¥2.5 / Writer+QA(A2)¥6.3 / Writer+QA(B1)¥4.3 / Support(A2)¥3.0 / Support(B1、Key Phrase retry込み)¥4.3 / A2 TTS+ASR clean ¥29.7・retry ¥10.9 / B1 TTS+ASR clean ¥24.5・retry ¥5.3(STOPPEDになった`in_one_line`3attempt分を含む)。Writer段階はPoint overlap QA・Fact Checker・Ledger Deviation Checker・Local Rewrite Loopが同一logging_context内で呼ばれるため、この粒度ではArticle生成本体とQA系呼び出しを個別分離できない(全て実測、合算のみである旨を明記)。

### H. 現状ステータス
- **No.18 A2 = `USER_FINAL_AUDIO_REVIEW_REQUIRED`**(完成音声+全文script、ユーザー最終試聴承認待ち)
- **No.18 B1 = 記事・Support・Key Phraseは完成、完成音声は`USER_DECISION_REQUIRED`(OPEN-107)によりepisode assembly未完成**
- No.9の既存final asset(A2/B1)・SSOT・one-off `default`は本タスクで一切変更していない。

### I. Git
- 新規: `er011_no18_discovery_why_full_production_run_01.py`(Production driver)、`er011_no18_b1_kp_retry_01.py`(B1 Key Phrase retry補助)、`er011_no18_cost_compute_01.py`(cost集計)
- 新規output: `er006_output/pool_pilot_01/pool_n18_notifications/`配下一式(research/writer/support/audio成果物、A2のみassembled、B1はassembled無し)
- 更新: `POOL_TOPIC_MASTER.md`(No.18差し替え)、`OPEN_ITEMS.md`(OPEN-107新規)、`DECISION_LOG.md`(本エントリ)
- `CURRENT_SPEC.md`は変更していない(新規仕様の追加・変更は無し、既存Production Wired仕様のみを使用したため)

## ER-010-NO9-FINAL-APPROVAL-CLOSEOUT-AND-FULL-STATUS-AUDIT-28: No.9 A2/B1最終承認記録とNo.9開発全体の完全棚卸し・Closeout(FINAL USER APPROVED / CLOSED)

- **日付**: 2026-09-02
- **区分**: User Decision記録(A2/B1最終承認) + Governance/PM(No.9開発全体のRepository横断棚卸し・Closeout)。新規のProduction仕様変更・コード変更は無し(SSOT記録の補完のみ)。

### A. User Final Decision
ユーザーがNo.9完成音声を試聴し、以下を正式決定した。
- **No.9 A2 = FINAL USER APPROVED**。対象は`er006_output/pool_pilot_01/pool_n9_tip_screens/a2/assembled/English_Your_Way_A2_POOL_N9_TIP_SCREENS.wav`(354.162秒、sha256`a07210c5722fad64e9d21c4b1d787d903400545dec0c142b3b91f656164e4946`、[ER-010-NO9-FUNCTION-WORD-REDUCTION-PRODUCTION-WIRING-AND-A2-FINAL-27-R1](#er-010-no9-function-word-reduction-production-wiring-and-a2-final-27-r1-function-wordarticle-reductionのproduction正式配線とno9-a2最終re-assemblyproduction_wireduser_final_audio_review_required)で反映した「a catch」function-word reduction版・`default`(Trial 21 Attempt 4 one-off)を含む)。
- **No.9 B1 = FINAL USER APPROVED**(既存承認[ER-010-NO9-B1-APPROVAL-AND-OPEN103-TTS-DIAGNOSTIC-18、2026-09-01]を維持・再確認)。対象は`er006_output/pool_pilot_01/pool_n9_tip_screens/b1b/assembled/English_Your_Way_B1B_POOL_N9_TIP_SCREENS.wav`(335.754秒、sha256`9c7a1d6341c6dfc9d07b2ca8d435b66bb2b80b287ca5c2e83603c4bcb5b673ca`)。

### B. Repository横断監査(会話履歴ではなくRepositoryを正とする)
CURRENT_SPEC.md・DECISION_LOG.md・OPEN_ITEMS.md・No.9関連management ID全24件(ER-009-N1-LEDGER-DEVIATION-RECALIBRATION-02〜ER-010-NO9-FUNCTION-WORD-REDUCTION-PRODUCTION-WIRING-AND-A2-FINAL-27-R1)・git log・Trial結果ファイル・Production scripts・testsを横断監査した。全項目一覧・Production Wired仕様一覧・REJECTED Trial一覧・残存Open Item一覧・one-off exception一覧は、本Decisionと同時に新規作成した`ER-010_NO9_FINAL_CLOSEOUT.md`(No.10以降のSSOT補助資料)に完全版を記録する(本エントリでは要点のみ記す)。

### C. 発見した記録漏れ1件(修正済み)
CURRENT_SPEC.mdに「Formatting禁止(絵文字・不要な太字Markdown)」の専用行が存在しないことを発見した。コード監査(`er003_v1_n3_01_articles_generate.py`行168のprompt禁止指示、行434の`normalize_article_formatting()`定義、行632・871の呼び出し2箇所)により、実装自体は2026-09-01([ER-010-NO9-FORMAT-PRODUCTION-AND-FACT-REVIEW-11](#))時点で既にPRODUCTION_WIREDであり、ユーザー承認済み・Production配線済みの事実がCURRENT_SPEC.mdへ反映されていなかった記録漏れと確認した(コード自体の未配線ではない)。指示書§26「既にユーザー承認済みかつProduction wiredな事実の記録漏れのみ修正可」に該当するため、CURRENT_SPEC.mdへ該当行を追加した(新仕様の追加ではない)。それ以外の項目(Storytelling First/No Jargon/Evidence-bounded Interpretation/Hook-aware Deviation Checker/Local Rewrite/Ledger Deviation Checker v2/Key Phrase括弧禁止/Diagnostic Full Retry/Human Review Lock STOPPED修正/review_lockリエントランシーガード/Key Phrase Minimal→English Lock retry/Function-word reduction/Fact Checker policy)は、いずれもCURRENT_SPEC.mdに既存行が存在し、記録漏れは確認されなかった。

### D. 未処理USER_DECISION_REQUIRED・Dangling Reference・未配線APPROVED仕様の確認結果
No.9関連の全USER_DECISION_REQUIRED記載(OPEN-97/100/101/102/103/104)を突合した結果、OPEN-100(Point Two数字羅列問題)を除く全件が`RESOLVED/CLOSED`または本Decisionで解消済みであることを確認した。OPEN-100はユーザーが既に`DEFERRED / NON-BLOCKING`と正式決定済み(2026-09-01、[ER-010-NO9-OPEN100-DEFER-AND-PRODUCTION-AUDIO-13](#))であり、これは「未処理のUSER_DECISION_REQUIRED」ではなく「ユーザー合意済みの意図的deferred」である。Dangling Reference(仕様名がProduction側で参照されているが実体が存在しない状態)は、CURRENT_SPEC.md・関連Production moduleのimport文・prompt文言を確認した結果、新規発見は無し(過去に発見されたOPEN-95は既に`RESOLVED/CLOSED`)。「ユーザー採用済みだがCURRENT_SPECにない/retry・fallbackにしか実装がない/Trial scriptだけにある」に該当する項目は、C節のFormatting禁止1件のみ(記録漏れとして修正済み)で、それ以外の新規発見は無し。

### E. OPEN_ITEMS更新
OPEN-103の行を更新した: 恒久課題(Gemini TTSが短い孤立語"default"を非決定的に誤発音する挙動)自体は`DEFERRED / NON-BLOCKING`のまま維持し、CLOSEしない(指示書§9・§12の明示要求どおり)。ただし、No.9 A2側の「完成音声ユーザー最終試聴承認待ち」というBlockingは、本Decisionでの正式承認により解消したことを追記した。OPEN-100は変更なし(`DEFERRED / NON-BLOCKING`のまま)。

### F. No.9 Final Close判定
以下を確認した: (1) A2/B1とも実際のfinal asset(hash・duration・lineage)をユーザーへ提示し最終承認を得た、(2) No.9で扱った全項目がstatus分類済み(`ER-010_NO9_FINAL_CLOSEOUT.md`参照)、(3) 未処理USER_DECISION_REQUIREDは0件、(4) VALIDATEDだが採否未確認の仕様は0件、(5) APPROVED_FOR_PRODUCTIONだが未配線の仕様は0件、(6) Production Wiring未完了項目は0件、(7) Dangling Referenceは0件、(8) SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS)は実態と一致(C節の記録漏れ1件を修正済み)。以上より:
- **No.9 A2 = FINAL USER APPROVED / CLOSED**
- **No.9 B1 = FINAL USER APPROVED / CLOSED**
- **No.9 DEVELOPMENT = CLOSED WITH DEFERRED OPEN ITEMS**(OPEN-100[Point Two数字羅列、Editorial Type導入後に再評価]・OPEN-103恒久課題[Gemini TTSの`default`誤発音、No.9はone-off回避済み]の2件はユーザー合意済みの意図的deferredとして残置)

### G. Closeout Document
`ER-010_NO9_FINAL_CLOSEOUT.md`(新規)を作成した。No.9概要・A2/B1最終asset・User final approval・Production Wired仕様一覧・REJECTED Trial一覧・Deferred Open Items・Resolved Bugs・one-off exception・runtime evidence summary・SSOT/Git・Final status table・将来再検討triggerを記載し、No.10以降のSSOT補助資料として保全する。

### H. 今回実施しなかったこと
新規Trial・新規Production仕様の追加実装・既存仕様の変更(C節の記録漏れ補完を除く)・OPEN-100/OPEN-103恒久課題の解決・技術的負債(review_lockの二重デコレータ構造自体、EVIDENCE_COMPRESSION_BLOCK未使用コード等)のrefactorは、指示書§29-C「勝手にrefactorしない」に従い、いずれも実施していない(発見のみ`ER-010_NO9_FINAL_CLOSEOUT.md`へ記録)。

- **Git**: 本Decisionに対応するcommit SHAは、本タスクの完了報告を参照。

---

## ER-010-NO9-FUNCTION-WORD-REDUCTION-PRODUCTION-WIRING-AND-A2-FINAL-27-R1: function-word/article reductionのProduction正式配線とNo.9 A2最終Re-Assembly(PRODUCTION_WIRED、USER_FINAL_AUDIO_REVIEW_REQUIRED)

- **日付**: 2026-09-02
- **区分**: サービス・生成仕様(Key Phrase英語発音の一般Production仕様変更)+ No.9 A2完成音声反映
- **ユーザー正式決定**: Trial 26(ER-010-NO9-A2-KEYPHRASE-ARTICLE-REDUCTION-DIAGNOSTIC-AND-TRIAL-26)で検証したfunction-word/article reduction原則を`APPROVED_FOR_PRODUCTION`から`PRODUCTION_WIRED`へ正式昇格。「a catch」固有対策ではなく、article/短いfunction word全般への再発防止仕様として採用。
- **実装(`er003_v1_repro01_main_generate.py`)**: 既存`KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX`のリテラル文字列を`KEY_PHRASE_MINIMAL_INSTRUCTION_CORE_TEXT`(旧文言、無変更)へ改名し、Trial 26で検証した文言をそのまま複製した`FUNCTION_WORD_REDUCTION_SUFFIX`を新設。`KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX = CORE_TEXT + FUNCTION_WORD_REDUCTION_SUFFIX`として再定義した(既存文言は一切削除・変更しない、AND方式)。`KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION`はこの`KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX`を起点に構築される既存コードのままのため、**Primary(Minimal最大2attempt)・Fallback(English Lock最大2attempt)の両方へ自動的に適用される**(定義を分岐させていないため、Fallback側だけ原則が欠落するDangling Referenceは構造的に発生しない)。Trial専用モジュール(`er010_no9_a2_keyphrase_article_reduction_trial_26.py`)はimportせず文字列として複製(既存方針踏襲)。「a catch」・「a」という文字列へのhardcodeは無し(articles全般への一般原則)。合計最大4attempt(`KEY_PHRASE_TOTAL_MAX_ATTEMPTS`)・retry配分ロジックは無変更。
- **Dangling Reference Check(静的検証)**: 新規`er010_no9_function_word_reduction_production_wiring_27.py::step1_dangling_reference_check()`で7項目を機械的に検証、全項目PASS(suffixがMinimal/English Lock双方の実効instructionに含まれる、既存safeguard文言が保持されている、"a catch"という文字列がsuffixに含まれない、Production本体モジュールがTrial 26モジュールをimportしていない、等)。
- **Regression(既存テスト)**: 変更前の`er011_human_review_lock_01_test_01.py`(18件、Key Phrase retry/reentrancy guard関連含む)を変更後に再実行し全PASS(既存テストはコンスタント名を通じて実効instructionを参照する設計のため、テキスト変更後も無修正でPASS)。新規`er010_no9_function_word_reduction_production_wiring_27_test.py`(9件: suffix適用確認・Primary/Fallback双方への適用確認・既存safeguard保持確認・"a catch" hardcode不在確認・retry budget不変確認・モック経由のPrimary→Fallback遷移確認)を追加、全PASS。無関係な`er010_n9_production_integration_09_test_01.py`(27件、Writer/Ledger系)も回帰無しを確認。
- **Runtime evidence(実Production path、Trial専用scriptではない)**: `generate_key_phrase_component_verified()`を実際に7フィクスチャへ発火(隔離probe dir、実Production entry point、実TTS/ASR/disfluency gate/review_lock込み)。全件Attempt 1・Primary(Minimal)でmachine PASS、Fallback未使用。
  - 「a catch」(No.9 A2正式Key Phrase): ASR="a catch"(完全一致)、duration 1.011秒(duration anomaly無し)、disfluency flagged=false、model=gemini-2.5-pro-preview-tts、voice=Aoede。envelope実測: 「a」区間0.08秒(旧production 0.28秒の約29%、Trial 26のTrial版0.07秒とほぼ一致する改善幅)。ただし今回のpeak RMS順序はTrial 26(「a」がcatch本体を下回る逆転)とは異なり「a」がやや高いままだった(TTS自体の非決定性、同一instructionでも生成ごとに変動しうる)。主訴だった「独立した強勢語のように長く発音される」問題に直結する**持続時間の大幅短縮は今回も明確に確認**、「catch」の語末音・自然さの悪化は無し。
  - article/function-word fixture(「a chance」「an idea」「the answer」、No.9本文とは無関係の一般English、一般原則の適用範囲確認用): 全件Attempt 1 PASS、ASRも完全一致(A chance./An idea./The answer.)、disfluency flagged=false。
  - 非function-word系の既存Key Phrase「guilt tipping」「push back」「starting point」(regression確認用): 全件Attempt 1 PASS、disfluency flagged=false。「push back」のみASRが"pushback"(スペース無し表記、既存の許容範囲内の表記ゆれで従来から発生、今回の変更由来ではない)。不自然な弱化を示す兆候は確認されなかった。
- **No.9 A2への反映**: 実Production path生成済みの「a catch」音声を`kp4_en.wav`へsplice(旧ファイルは`kp4_en_pre_wiring27_backup.wav`としてbackup保持)。`tts_generation_results.json`のkp4/englishエントリを新しい実生成結果(status=OK, sha256, asr_text, disfluency evidence)で更新。kp1(guilt tipping)・kp3(push back)・kp5(starting point)は無変更(sha256一致を確認)。kp2(`default`、Attempt 4 one-off)はファイル・レコードとも完全に無変更であることをsha256照合で確認(OPEN-103は今回もタッチしていない)。
- **A2再Assembly**: `stage_assemble_a2()`を実際に再実行し、`English_Your_Way_A2_POOL_N9_TIP_SCREENS.wav`(354.162秒、旧355.002秒からKey Phrase 4短縮分だけ変化、clipping無し)を再生成。完成episode timelineでKey Phrase 4が1回のみ・想定位置(72.309秒〜78.802秒)に存在し、重複segmentは無いことを確認。完成audio中のKey Phrase 4区間を実測ASRで再確認し、"4. a catch 落し穴 ただし書き a catch"(番号読み上げ→英語→日本語gloss→repeat英語、既存の他Key Phraseと同一の放送構造)を正しく確認した。
- **CURRENT_SPEC.md**: 「英語Component生成方式」行の直後に新規行「Function-word/article reduction(Key Phrase英語pronunciation)」を追加、`DECIDED`(`PRODUCTION_WIRED`)。Primary/Fallback両方への適用を明記。
- **OPEN_ITEMS.md**: OPEN-106を`RESOLVED / CLOSED`へ更新(Production配線・runtime発火・regression・No.9 A2反映のすべてを確認済み)。OPEN-103は`DEFERRED / NON-BLOCKING`のまま無変更。
- **完成音声+全文script**: User Listening Artifact(A2完成音声・「a catch」新旧比較・放送順全文script・`default`注記・regressionテーブル)を提示: https://claude.ai/code/artifact/53a57e1a-ec73-40bd-ad5f-c89ada7dabcb
- **status**: `USER_FINAL_AUDIO_REVIEW_REQUIRED`相当。ユーザーがこの完成音声を試聴し最終承認するまで、No.9 A2は最終closeしない。

---

## ER-010-NO9-A2-KEYPHRASE-ARTICLE-REDUCTION-DIAGNOSTIC-AND-TRIAL-26: Key Phrase「a catch」冠詞強調の診断とfunction-word reduction隔離Trial(USER_DECISION_REQUIRED)

- **日付**: 2026-09-01
- **区分**: 診断+隔離Trial(Production一般仕様は未変更、ユーザー判断待ち)
- **背景(User Feedback)**: No.9 A2完成候補の試聴で、Key Phrase「a catch」の冠詞"a"が「アー キャッチ」のように独立して強く・長く発音されていると指摘。
- **既存仕様監査**: CURRENT_SPEC.md・DECISION_LOG.mdを"article"/"function word"/"冠詞"/"stress"/"reduction"等で監査したが、Key Phrase英語発音仕様(`er003_v1_repro01_main_generate.KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX`)にfunction word(冠詞等)を弱く・短く読む原則は存在しないことを確認。DECISION_LOG.md内の唯一の関連ヒット(冠詞のみ云々)はDeviation CheckerのStopword比較ロジックの話で、発音仕様とは無関係。→**既存仕様の実装漏れではなく、新しいpronunciation safeguard候補**として扱った。
- **`a catch` lineage確認**: No.9 A2 Key Phrase rank4(`keywords_canonicalized.json`、source: "But there was a catch."、gloss「落とし穴、ただし書き」)。実際に使用中の音声(`kp4_en.wav`)は、`er006_output/master_audio_store_01`のmaster cache(id `aaa176ad782661323883f263`、2026-09-01 11:21:23生成、Minimal instruction["primary"経路]、model=gemini-2.5-pro-preview-tts、voice=Aoede、ASR="A catch."、disfluency flagged=false)から3回reuseされたもの。Mini-Trial 20-R2(2026-09-01付DECISION_LOG参照)でも「a catch」はAttempt 1でPASS(duration anomaly無し、Validator NORMALIZED_MATCH)しており、**機械ASR/Validatorは一貫してPASSし続けている**——今回の問題は機械検証では検出できない自然さの領域であることを確認した。
- **原因診断(Root Cause分類)**: 現行Minimal instructionの"Say it as one natural phrase, not as separate words read one at a time"は単語分割読みを禁止するのみで、function wordとcontent wordのstress配分には触れていない(Hypothesis A、**LIKELY**、原因の中心と判断)。「a catch」がsentence埋め込みなしの2語単独発話であることも、各語がcitation form(単独発話形=各語フル強勢)寄りになりやすい一般的傾向として寄与している可能性がある(Hypothesis B、**LIKELY、補助的要因**)。"naturally and clearly"/"do not add, omit, or change any words"がfunction wordの明瞭発話へ過剰解釈された可能性(Hypothesis C)・語末音保持safeguardとのバランス(Hypothesis D)は、コード上の直接的な根拠が薄く**POSSIBLE(speculative)**、Provider variance(Hypothesis E)は否定できないため**POSSIBLE**にとどめた。
- **客観測定(実測)**: 現行採用中の`kp4_en.wav`をenvelope解析(10ms窓RMS)した結果、「a」区間は0.28秒・peak RMS 0.2096で、3音区間中もっとも大きいpeakを記録(「catch」本体peak 0.1771を上回る)。「a」→「catch」間に0.11秒のギャップ。フレーズ全体1.43秒。これはユーザーの聴感上の指摘(冠詞が独立した強勢語のように聞こえる)と客観的に整合する。
- **Trial設計**: 既存Minimal instructionの文言は一切変更・削除せず、末尾にfunction word/article全般への一般原則を1文追加するだけ(English Lock suffixと同じAND方式)。「a catch」固有のhardcode・「a」という文字列だけへの特殊処理は行っていない。新規スクリプト`er010_no9_a2_keyphrase_article_reduction_trial_26.py`(Production経路[review_lock guarded]は一切呼ばない隔離Trial、Trial 21と同一設計方針)。
- **Trial実施**: 「a catch」1語のみ対象、Attempt 1でmachine PASS(ASR="A catch."、Validator NORMALIZED_MATCH、disfluency flagged=false、clipping無し)のため即終了(最大3attempt許容していたが1回で完了)。実測envelope解析: 「a」区間0.07秒(現行比約1/4)・peak RMS 0.2545(「catch」本体peak 0.2637より小さい=article<content wordの関係に反転)、ギャップ0.05秒(現行比約半分)、フレーズ全体0.95秒(現行比約34%短縮)。既存safeguard(語末音保持・自然さ・1回のみ・commentaryなし)は維持されており、「catch」の語末音悪化は確認されなかった。
- **Trial記録**: `er010_output/no9_a2_keyphrase_article_reduction_trial_26/trial26_results.json`(instruction全文・ASR・Validator・disfluency evidence・envelope解析・sha256を保存)。
- **User Listening Artifact**: Current Production版とTrial版を並べて聴き比べ・envelope可視化・客観比較表を掲載: https://claude.ai/code/artifact/a110d7ac-dddd-4a7f-9dca-d59de62b87e2
- **Trial Closeout**: `USER_DECISION_REQUIRED`。良好な客観結果が得られたが、一般Production仕様への自動追加は行っていない。ユーザー試聴後、(A)一般Key Phrase Minimal instructionへ正式採用、(B)「a catch」のみ一旦採用、(C)不採用、のいずれかをユーザーが選択する。
- **No.9 A2への影響**: 今回はTrialのみ。A2の再assembly・`kp4_en.wav`差し替えは、ユーザーがTrial音声を承認した後に別タスクとして実施する(未実施)。
- **`default`(OPEN-103)**: 今回触れていない。ER-010-NO9-A2-ATTEMPT4-ONEOFF-FINAL-AUDIO-25で採用したAttempt 4 one-off固定assetをそのまま維持。OPEN-103のステータス([[OPEN_ITEMS.md]])も無変更。
- **根拠レポート**: 本エントリ自体(コードレビュー+実際のTrial実行結果、`trial26_results.json`)。
- **commit**: (このコミットで記録)

---

## ER-010-NO9-A2-ATTEMPT4-ONEOFF-FINAL-AUDIO-25: Trial 21 Attempt 4をNo.9 A2 `default`のone-off固定assetとして採用・A2完成

- **日付**: 2026-09-01
- **区分**: サービス・生成仕様の変更(No.9 A2 `kp2_en`1segment限定のone-off、一般Production仕様は無変更)
- **User Decision**: ユーザーがTrial 21(ER-010-NO9-KEYPHRASE-ENGLISH-LOCK-FALLBACK-TRIAL-21)のENGLISH_LOCK attempt=2(通し4回目=「Attempt 4」)を、No.9 A2 `kp2_en`("default")限定のone-off固定assetとして正式採用すると決定した。23-R1(前Decision)で提示した本文ナレーション抽出候補3件は不採用。一時的に選択肢から除外していた「Trial 21音声の流用」を、ユーザーが今回改めて明示的に指示し直したことで正式採用へ切り替わった。
- **Attempt 4 lineage確認**: `trial21_results.json`の`attempts`配列(全4件)の4番目(`attempt_type="ENGLISH_LOCK", attempt=2`)であることを確認し、記載された`audio_path`/`sha256`(`5cfeaaa4...`)が実ファイルと完全一致することを検証した(不一致ならSTOPする設計、実際は一致)。model=`gemini-2.5-pro-preview-tts`、voice=`Aoede`(Production英語Componentと同一)、duration=1.151秒。Trial 21自身の記録では、この音声はmachine validator上`audio_classification=TTS_FAILURE`(ASR="デフォルト"、日本語カタカナ表記)として不合格だった。
- **machine FAIL / human-approved one-off override**: 元のmachine判定は一切書き換えていない。`tts_generation_results.json`の`key_phrases["2"]["english"]`エントリの`status`(`HUMAN_REVIEW_LOCKED`)・`locked_entry`・`attempts_log`(Trial 19/Mini-Trial 20-R2/本番3回いずれも失敗だった履歴)はそのまま保持し、新規フィールド`one_off_fixed_asset_override`(採用日時・override_type=`MACHINE_FAIL_HUMAN_APPROVED_ONEOFF`・source情報・sha256等)を追記するのみとした。承認記録は、このプロジェクトのProduction Episode Assembly Gateが既に持つ正式な人間承認メカニズム(`er003_v1_n3_01_assemble.py::record_human_approval()`、`human_approved_segments.json`)を使用した(今回新設した仕組みではない)。
- **実施した実QA(新規TTSなし)**: (1) ローカルfaster-whisperによるdisfluency QA(`er008_disfluency_qa_18.apply_disfluency_gate()`、追加API課金なし)を実際に実行し、`flagged=false`(repetitionなし、transcript="default.")を確認。これはProduction Assembly Gateが`_english`で終わるsegmentすべてに要求する必須evidenceであり、実施しないとGateがブロックする。(2) 採用直前にProduction ASR(実API、小額課金)で再確認し、Trial 21実行時と同じ"デフォルト"(日本語カタカナ)を得た(音声内容がTrial 21時点から変化していないことの確認)。ローカルASR("default.")とProduction ASR("デフォルト")の食い違いは、本プロジェクトで一貫して観測されてきた短い単語clipに対するASRの弱さと一致するパターンであり、新しい問題ではない。
- **差し替え**: `er006_output/pool_pilot_01/pool_n9_tip_screens/a2/narration/kp2_en.wav`をAttempt 4音声(sha256一致)へ差し替えた。旧ファイル(23-R1で「Guilt tippingとの取り違え」と判明済み、sha256=`b58213fc...`)は削除せず`kp2_en_pre_oneoff_mislabeled_backup.wav`として保持した。
- **A2 Assembly**: `er003_v1_n3_01_assemble.py::stage_assemble_a2()`を実行し、`Episode Assembly Gate`(`verify_episode_audio_validation_gate()`)を実際に通過(ブロックなし)。No.9 A2完成音声(`English_Your_Way_A2_POOL_N9_TIP_SCREENS.wav`、355.002秒、48kHz/stereo、clipping無し、peak 0.778)を生成した。timelineから Key Phrase 2 が1回のみ・想定位置(59.023秒〜、duration 6.503秒)に存在し、重複segmentが無いことを確認した。完成episodeの当該区間を切り出して実ASR再確認し、"2. デフォルト、初期設定の選択肢。デフォルト"(番号・語義・番組設計上のrepeat構成すべてが正しく認識)を得た。
- **他segmentの扱い**: 他4件のKey Phrase(guilt tipping/push back/a catch/starting point)・Japanese narration・Full Story Part 1/2・Point One/Two・In One Line等はいずれも再生成せず、既存Production正式assetをそのまま使用した。なお、これらの一部segment(Full Story/Point/meaning等)は本タスクとは無関係な同日の別タスク(Local Rewrite Loop等)で既に更新済みだったため、今回のAssemblyはその更新後の内容を正しく反映している(Episode Assembly Gateがsegmentごとに`VALIDATED`/`HUMAN_APPROVED`であることを検証しており、いずれもブロックされなかったことから、これらは既にProduction承認済みの音声であることを確認済み)。
- **User Listening Artifact**: https://claude.ai/code/artifact/401bec48-69ba-40b9-b208-5ba058c946dd (完成音声player・Attempt 4 one-off assetのmachine FAIL/human-approved情報・Key Phrase一覧・default周辺QA・放送順Full Scriptを掲載)。ユーザーがこの完成音声を試聴し最終承認するまでは、No.9 A2は最終closeoutしない。
- **OPEN_ITEMS反映**: OPEN-103のstatusを`USER_FINAL_AUDIO_REVIEW_REQUIRED`相当へ更新(A2 episode assembly自体は完成、残るのはユーザーの完成音声最終試聴承認のみ)。恒久課題(Gemini TTSの`default`発音問題自体)としての性質は`DEFERRED / NON-BLOCKING`のまま、CLOSEはしない。
- **Git**: `er010_no9_a2_attempt4_oneoff_final_audio_25.py`(新規)・`er010_output/no9_a2_attempt4_oneoff_final_audio_25/final_audio_result.json`(新規)・`er006_output/pool_pilot_01/pool_n9_tip_screens/a2/audit/{tts_generation_results.json,human_approved_segments.json,timeline.json,gain_report.json}`・`er006_output/pool_pilot_01/pool_n9_tip_screens/a2/run_summary_assemble.json`・`DECISION_LOG.md`・`OPEN_ITEMS.md`をcommit(CURRENT_SPEC.mdは今回変更なし、一般Production仕様は無変更のため)。

---

## ER-010-NO9-A2-DEFAULT-FIXED-ASSET-FINALIZATION-23-R1: `default`個別対応、既存固定音声資産の探索

- **日付**: 2026-09-01
- **区分**: 診断・調査(新規TTS Trial・Production仕様変更はいずれも実施していない)
- **背景**: [ER-010-NO9-KEYPHRASE-MINIMAL-ENGLISHLOCK-PRODUCTION-WIRING-22](#er-010-no9-keyphrase-minimal-englishlock-production-wiring-22-key-phrase英語component-retry構成をminimal→english-lockへ正式production配線)で一般Key Phrase retry仕様をProduction配線した際、`default`は個別例外として分離した。ユーザーが明示的に「これ以上TTS Trialを続けず、既存の正常な固定音声素材を探索・lineage確認し、No.9 A2限定one-off assetとして利用する」方針を指示し、Trial 21のEnglish Lock Attempt 3/4を勝手に採用しないこと・新規TTS Trialを行わないことを明確に禁止した。
- **既存`kp2_en.wav`の再確認(実データ)**: 前回セッションでは「異常発生前の古い生成物」と評価されていたが、今回実際にASR(`routing.transcribe`)で再確認した結果、内容は"default"ではなく**"Guilt tipping"**(No.9 A2 Key Phrase 1の内容)だった。単に古いのではなく、**別のKey Phraseとの取り違え**という、より確定的な不採用理由が判明した(duration 1.611秒、sample_rate 24000、review_lock state=`HUMAN_REVIEW_REQUIRED`)。
- **既存assetの探索**: リポジトリ全体で"default"を含むwavファイル名を検索した結果、Trial 19(1件)・Mini-Trial 20-R2(3件)・Trial 21(4件)の計8件のみで、いずれも既知の失敗Trial由来(REJECTED/USER_DECISION_REQUIRED)であり、Trial 21以外に単体の"default" Key Phrase録音は存在しないことを確認した。
- **新規発見**: No.9 A2/B1BのFull Story本文(`parts.json`)に、Key Phrase一覧とは別に、地の文として"default"という単語が実際に使われている箇所を発見した。
  - A2 full_story_part2: "So, a high **default** can raise the tip from some customers."
  - B1B full_story_part1: "...passengers saw different **default** tip menus."
  - いずれのsegmentも既に`review_lock`上`RESOLVED`(ASR content-match検証PASS済み。B1Bはユーザーが既にNo.9 B1全体を正式承認済み)。
- **抽出方法**: `er008_disfluency_qa_18.transcribe_verbatim()`(faster-whisper、ローカル無料実行、追加API課金なし)のword-level timestampで"default"の位置を特定し(いずれも認識確信度0.80〜0.996)、前後0.06秒の余白を付けて単語単位で切り出した(`er010_no9_a2_default_fixed_asset_finalization_23_r1.py`、新規)。
- **3候補の検証結果**:
  | 候補 | Source(RESOLVED) | 切り出し後duration | Local Whisper再ASR | Production ASR(単体) |
  |---|---|---|---|---|
  | B1B full_story_part1 | ユーザー承認済みNo.9 B1の一部 | 0.66s | "default."(確信度0.54) | "Current default."(先頭に短い誤認識語) |
  | A2 full_story_part2(放送版、6%time-stretch後) | RESOLVED | 0.68s | "default"(確信度0.80) | "I default?"(同上) |
  | A2 full_story_part2_original(time-stretch前) | RESOLVED | 0.66s | "default."(確信度0.78) | "By default?"(同上) |
  - 3候補ともローカルASR(faster-whisper)は一貫して"default"のみを検出。一方、Production ASR(Google STT)はいずれも文頭に短い誤認識語を付け足した。切り出し境界を前後にずらす検証(lead margin 0/-0.03/-0.05秒)でも解消せず、境界の切り方の問題ではなく、文脈の無い極短音声に対するASR側の解釈揺れ(Key Phrase Trialで繰り返し観測したのと同種の既知の弱点)である可能性が高いと判断した。断定はできないため、最終判断は保留し、人間の試聴に委ねることとした。
  - 抽出元は自然な会話文中の一単語であり、他4件のKey Phrase(Minimal instructionによる専用録音、duration約1.0〜1.4秒)より短く(0.66〜0.68秒)テンポが速い点も、判断材料として正直に記録した。
- **Trial 21 Attempt 3/4は使用していない**。新規TTS生成も一切行っていない(実施したのはローカル無料の再ASR・切り出し・実API少額のASR再検証のみ)。
- **User Listening Artifact**: https://claude.ai/code/artifact/585b7dc3-8d19-4e2b-aafe-dd9eba77eb5a (kp2_en.wavの取り違え実証+3候補の音声・context・ASR結果・留意点を掲載)。
- **A2 Assembly**: 実施していない。過去のユーザー承認(B1B/A2 Full Storyの文全体としての承認)は、そこから単語を切り出してKey Phraseという別文脈で単体再生する使い方を含まないため、今回新たな承認が必要と判断し、Assemblyへは進まずユーザー提示に留めた。
- **OPEN_ITEMS反映**: OPEN-103のstatusを`USER_DECISION_REQUIRED`へ更新(候補提示済み、採用は未定)。`DEFERRED / NON-BLOCKING`という恒久課題としての分類自体は維持しつつ、今回はNo.9 A2完成に向けた具体的な候補が出たための一時的なUSER_DECISION_REQUIRED。
- **Git**: `er010_no9_a2_default_fixed_asset_finalization_23_r1.py`(新規)・`er010_output/no9_a2_default_fixed_asset_finalization_23_r1/search_and_extraction_results.json`(新規)・`DECISION_LOG.md`・`OPEN_ITEMS.md`をcommit(CURRENT_SPEC.mdは今回変更なし、一般Production仕様は無変更のため)。

---

## ER-010-NO9-KEYPHRASE-MINIMAL-ENGLISHLOCK-PRODUCTION-WIRING-22: Key Phrase英語Component retry構成をMinimal→English Lockへ正式Production配線

- **日付**: 2026-09-01
- **区分**: サービス・生成仕様の変更(Key Phrase英語TTS retry構成)+Implementation Hardening(旧経路のDangling Reference整理)
- **ユーザー正式決定**: [ER-010-NO9-KEYPHRASE-MINIMAL-INSTRUCTION-TRIAL-AND-RETRY-ACCOUNTING-FIX-19](#er-010-no9-keyphrase-minimal-instruction-trial-and-retry-accounting-fix-19)→[MINI-TRIAL-20-R2](#er-010-no9-keyphrase-minimal-instruction-mini-trial-20-r2-no9-a2正式key-phrase5件のminimal-instruction-mini-trialbounded-retry)→[ENGLISH-LOCK-FALLBACK-TRIAL-21](#er-010-no9-keyphrase-english-lock-fallback-trial-21-key-phrasedefaultのenglish-language-lock-fallback-trialminimal最大2english-lock最大2)の3段階のTrialを経て、ユーザーが「`default`は個別対応、それ以外のKey Phrase英語TTSは**Minimal instruction最大2回→NGならEnglish language lock付きMinimal最大2回(合計最大4回)**を量産仕様の本命として正式採用する」と決定した。この採用判断自体はClaude Codeが再判断せず、そのままProduction正式配線した。
- **実装**: `er003_v1_repro01_main_generate.py::generate_key_phrase_component_verified()`(`@review_lock.guarded_generate("en")`は維持)を全面書き換え。
  - **旧構成(廃止)**: 標準経路(`ENGLISH_STYLE_PREFIX`、フルストーリー本文向けの長い演技指示)を最大`PRODUCTION_MAX_TTS_ATTEMPTS`(3)回試行→不合格の場合のみ`generate_english_component_minimal_instruction()`(旧`MINIMAL_INSTRUCTION_PREFIX`)へ、標準経路の消費数を引いた残り予算でfallback。
  - **新構成(採用)**: `generate_narration_snippet_verified_strict()`をstyle_prefix_overrideだけ差し替えて2段呼び出す設計(コード重複を避けつつ、両段ともProduction同一のASR Cascade/disfluency gate/duration anomaly検知を使う)。
    1. **Primary**: `KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX`(Trial-19/Mini-Trial-20-R2で検証・確定した文言を一字一句複製)で最大`KEY_PHRASE_MINIMAL_MAX_ATTEMPTS`(2)回。
    2. **Fallback**: Primaryが2回ともNGの場合のみ、`KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION`(`KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX`+Trial-21で検証・確定した"Pronounce the phrase specifically as an English word or phrase, using English pronunciation throughout — not as a Japanese, Chinese, or other non-English reading of it."を末尾に追加。既存文言は置換しない)で最大`KEY_PHRASE_ENGLISH_LOCK_MAX_ATTEMPTS`(2)回。
    3. 合計最大`KEY_PHRASE_TOTAL_MAX_ATTEMPTS`(4)回。いずれかの段でPASSした時点で即終了、後続attemptは実行しない。
  - Trial専用モジュール(`er010_no9_*.py`)はProductionからimportせず、文言を文字列として複製する設計を維持(Dangling Reference防止)。複製が一字一句一致することは`repro01.KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX == trial21.MINIMAL_INSTRUCTION_TRIAL_PREFIX_V2`/`repro01.KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION == trial21.ENGLISH_LOCK_INSTRUCTION`をその場で突合し確認済み(いずれも`True`)。
  - `max_attempts`引数は廃止した(旧構成の「standard消費数を引いた残り予算」という計算自体が今回のユーザー決定で不要になったため。2つのテスト呼び出し元[`er011_human_review_lock_01_test_01.py`]のみが明示的に渡していたが、いずれも本タスクで新構成用に書き換えた)。
- **CURRENT_SPEC.mdへの反映**: 「TTS生成の同一segment総試行回数上限」(3回、`PRODUCTION_MAX_TTS_ATTEMPTS`)行へ「Key Phrase英語Componentのみ4回の例外」を明記。「Key Phrase」節へ新規行「英語Component生成方式(Production正式retry構成)」「`default`(No.9 A2 kp2_en)個別例外」を追加。「Full Story」節のminimal instruction fallback行を、短文ナレーションにのみ適用される旨へ修正(Key Phrase Componentは別の専用構成を参照するよう誘導)。`stage_d_generate_key_phrase_components()`のdocstring(旧`ENGLISH_STYLE_PREFIX`起点の説明)も実装に合わせて修正(Dangling Reference解消)。
- **旧経路の扱い**: `ENGLISH_STYLE_PREFIX`/旧`MINIMAL_INSTRUCTION_PREFIX`/`generate_english_component_minimal_instruction()`/`generate_narration_snippet_verified_strict()`自体はいずれも削除・変更していない。これらはKey Phrase以外のsegment(Full Story/News/Point見出し/`generate_english_segment_with_fallback()`経由のADD03 Point One等)で引き続き使用されており、それらの呼び出し元(`er003_v1_crosslevel_audio_02_common.py::generate_english_segment_with_fallback()`ほか)は無変更(grepで全参照箇所を確認、影響はKey Phrase専用の1関数のみ)。
- **Tests**: `er011_human_review_lock_01_test_01.py`。旧構成の予算配分を検証していた2件(`test_key_phrase_fallback_budget_is_zero_when_standard_used_all_attempts`/`test_key_phrase_fallback_gets_remaining_budget_only`)を新構成向けに差し替え、新規5件を追加(Minimal PASSでEnglish Lock不発火/Minimal 2回NG後のみEnglish Lock発火/4回全滅時の合算理由メッセージ/instruction追加性[置換でないこと]の静的確認/review_lock実体経由のcumulative_tts_attempts・2回目ブロック確認)。既存13件+新規5件で計18件、全PASS。関連regression `er008_crosslevel_audio_02_tts_cap_25_test_01.py`・`er010_n9_production_integration_09_test_01.py`・`er003_test_b1_p4c_audio.py`(build_tts_prompt経由の静的確認)もPASSのまま(exit code 0)。既存の非unittest配線確認スクリプト`er006_pool_benches_luna_audio_wiring_test.py`も実行し、`er003_v1_repro01_main_generate.py`に関する2項目(audio_validation import/evaluate_attempt_with_cascade呼び出し)はいずれも`[OK]`(唯一の`[FAIL]`は`er003_v1_sing01_news_tail_fix.py`の既存の無関係な既知issueで、本タスクの変更対象外)。
- **Runtime evidence**(`er010_no9_keyphrase_minimal_englishlock_production_wiring_22.py`、Production review_lock guarded本体を実際に発火):
  - **Case A(実API、実TTS+実ASR)**: No.9正式Key Phrase"push back"(隔離temp narration layout、実Production `er006_output/pool_pilot_01/...`配下は一切変更していない)。model=`gemini-2.5-pro-preview-tts`、voice=`Aoede`。Minimal Attempt 1はASR「推回」(TTS_FAILURE)、Attempt 2はASR"pushback"(`NORMALIZED_MATCH`、disfluency transcript"Pushback."、flagged=false)でverified=True、即終了(English Lockは呼ばれず)。最終`status=OK`・`fallback_used=False`・`primary_instruction_type=MINIMAL`。review_lock: `state=RESOLVED`・`cumulative_tts_attempts=2`(実TTS試行数2と完全一致)。
  - **Case B/C(境界モック、実API課金ゼロ)**: `generate_narration_snippet_verified_strict()`をモックしMinimal 2回を強制NGにした結果、実際にEnglish Lockへ遷移(`call_sequence`: MINIMAL[max_attempts=2]→ENGLISH_LOCK[max_attempts=2]の順で実際に2回呼ばれたことを確認)。English Lock Attempt 1でPASS。最終`status=OK`・`fallback_used=True`・`primary_instruction_type=ENGLISH_LOCK`。review_lock: `state=RESOLVED`・`cumulative_tts_attempts=3`(Minimal実2回+English Lock実1回=3と完全一致、二重会計なし)。
  - 「Minimal+English Lockとも合計4回全滅→HUMAN_REVIEW_REQUIRED」分岐は、上記と同じ境界(`generate_narration_snippet_verified_strict`)をモックする単体テスト(`test_key_phrase_review_lock_end_to_end_cumulative_count_and_second_call_blocked`)で実際のreview_lock guarded本体経由の`cumulative_tts_attempts=4`・2回目呼び出し0 API callブロックを確認済み(4回とも実際に失敗する語を安定して再現する自然文が存在しないため、この分岐のみ境界モックで代替、他は全て実TTS/実ASRまたは実際のguarded関数呼び出し)。
- **No.9 A2への適用**: 既存4件(kp1/3/4/5、guilt tipping/push back/a catch/starting point)はいずれも旧経路で既に`RESOLVED`(`review_lock_state.json`で実測確認: kp1=2回・kp3=6回・kp4=2回・kp5=2回でOK確定)。Review Lockの既存設計により、canonical_textが変わらない限り自動再生成されないため、本タスクによる**既存承認済み音声の意図しない再生成は発生しない**(無意味な再生成をしないという指示どおり)。新規記事・`default`以外の既存segmentの再生成が必要になった場合は、次回以降このMinimal→English Lock構成が自動的に使われる。
- **`default`(kp2_en)の扱い**: 一般仕様から個別例外として分離。現存`kp2_en.wav`(77,370 bytes、2026-08-30生成)は、review_lock最終状態(`HUMAN_REVIEW_REQUIRED`、2026-09-01ロック)より前の生成物であり、過去セッションのwaveform実測により「異常発生より前の別の生成物」と確認済み(信頼できる`default`候補ではない)。[ER-010-NO9-KEYPHRASE-ENGLISH-LOCK-FALLBACK-TRIAL-21](#er-010-no9-keyphrase-english-lock-fallback-trial-21-key-phrasedefaultのenglish-language-lock-fallback-trialminimal最大2english-lock最大2)で生成済みのEnglish Lock Attempt 1("defaut"表記)/Attempt 2(「デフォルト」)の2音声(ユーザーがTrial 21のArtifactで試聴し「問題ないように聞こえる」と述べた候補)を、No.9限定のfixed asset候補として提示する(Artifact: https://claude.ai/code/artifact/c7617694-6220-4258-808b-e22aee15f75a)。**Claude Codeはこの2候補のいずれも正式採用していない**。ユーザーがOPEN-103の対応方針(下記)を選ぶまで、`kp2_en`のreview lockは`HUMAN_REVIEW_REQUIRED`のまま維持する。
- **OPEN_ITEMS反映**: OPEN-103のstatusを`DEFERRED / NON-BLOCKING`(個別例外化、No.9 A2 episode assembly完成のみ引き続きblocking)へ更新。過去の選択肢(1)〜(4)は維持し、新たに(6)として「Trial 21のEnglish Lock Attempt 1/2をNo.9限定のfixed assetとして採用」を追加。
- **Git**: `er003_v1_repro01_main_generate.py`(Production本体)・`er011_human_review_lock_01_test_01.py`(テスト)・`CURRENT_SPEC.md`(SSOT)・`er010_no9_keyphrase_minimal_englishlock_production_wiring_22.py`(Runtime evidence取得用、新規)・`er010_output/no9_keyphrase_minimal_englishlock_production_wiring_22/runtime_evidence_results.json`(新規)・`er011_output/attempt_history.jsonl`(review_lock監査ログ、追記)をcommit。

---

## ER-010-NO9-KEYPHRASE-ENGLISH-LOCK-FALLBACK-TRIAL-21: Key Phrase「default」のEnglish language lock fallback Trial(Minimal最大2→English Lock最大2)

- **日付**: 2026-09-01
- **区分**: Trial診断(Production instruction・review lock・retry budget・provider・voice・thresholdはいずれも無変更)
- **背景**: 直前の[ER-010-NO9-KEYPHRASE-MINIMAL-INSTRUCTION-MINI-TRIAL-20-R2](#er-010-no9-keyphrase-minimal-instruction-mini-trial-20-r2-no9-a2正式key-phrase5件のminimal-instruction-mini-trialbounded-retry)で、"default"はMinimal instructionでも3attemptとも誤発音(1〜2回目=日本語カタカナ「デフォルト」、3回目=中国語「默认」)で再現性を確認していた。duration anomaly自体はMinimal instructionで解消済みだったため、今回は量産candidate retry仕様として「Minimal instruction最大2attempt→NGならEnglish language lock付きMinimal最大2attempt(合計最大4attempt)」を`default`1語のみに対して隔離Trialし、Minimalの簡潔さは維持したままEnglish language lockが英語発音への回帰に有効かを検証した。
- **実装**: `er010_no9_keyphrase_english_lock_fallback_trial_21.py`(新規)。Mini-Trial 20-R2と同じ非guarded関数(`p9a._make_english_call_fn()`、`p3u.trim_english_keyword_silence()`、`safety.detect_duration_anomaly()`、`secondary_asr.evaluate_attempt_with_cascade()`、`dq18.apply_disfluency_gate()`)をそのまま再利用し、review_lockの`guarded_generate`系デコレータ付き関数は一切呼ばないことでProduction review lock/retry countへの影響を遮断した。Minimal instruction本文は[Mini-Trial 20-R2](#er-010-no9-keyphrase-minimal-instruction-mini-trial-20-r2-no9-a2正式key-phrase5件のminimal-instruction-mini-trialbounded-retry)の`MINIMAL_INSTRUCTION_TRIAL_PREFIX_V2`を一字一句変更せず踏襲した。
  - **Minimal instruction全文**: "Speak the following short phrase aloud naturally and clearly, in a warm podcast announcer voice, exactly once. Say only this phrase — do not add explanations, examples, introductions, or any other commentary, and do not add, omit, or change any words. Say it as one natural phrase, not as separate words read one at a time. Make sure the very last sound of the phrase is actually spoken, not trailed off into silence, and do not over-emphasize or exaggerate any single sound."
  - **English language lock追加文言(Minimal instruction全文の末尾に1文のみ追加)**: "Pronounce the phrase specifically as an English word or phrase, using English pronunciation throughout — not as a Japanese, Chinese, or other non-English reading of it."
  - `p4c.build_tts_prompt()`のStructured Separation構造(STYLE INSTRUCTIONS節/TEXT TO SPEAK節)に従い、English lockもstyle_prefix側(読み上げ対象外の指示節)へ追加した。既存のfinal consonant保持・自然さ・1回のみ・commentary禁止・phrase一体感の各文言はEnglish Lock段でも一切削除・変更していない(AND、ORではなく追加)。
- **Trial結果**: 4attemptすべて実行(Minimal 2回→2回ともNGのためEnglish Lock 2回へ移行、PASSは1件も無かったため4回目まで到達)。
  | Attempt | 種別 | Duration | anomaly | ASR | Validator |
  |---|---|---|---|---|---|
  | 1 | Minimal | 1.091s | 無し | "デフォルト"(日本語カタカナ) | TTS_FAILURE |
  | 2 | Minimal | 1.131s | 無し | "デフォルト"(日本語カタカナ) | TTS_FAILURE |
  | 3 | English Lock | 1.071s | 無し | "defaut"(英字だが誤スペル) | TTS_FAILURE |
  | 4 | English Lock | 1.151s | 無し | "デフォルト"(日本語カタカナ) | TTS_FAILURE |
  - English Lock Attempt 1で初めてASRが英字表記("defaut")になったが、正しい綴り("default")ではなく、`length_ok`はTrueでも全体類似度に基づく`TTS_FAILURE`判定は変わらなかった。
  - English Lock Attempt 2は日本語カタカナへ逆戻りしており、English lockを追加しても同じ非英語発話モードが再発した。
  - 4attemptとも`duration_anomaly.is_anomaly=false`(1.0〜1.2秒、正常範囲内)。duration anomaly側の改善効果はMinimal instruction単体と同様に維持されている。
- **仮説への結論**: English language lockのfallback追加は、`default`のcontent-accuracy失敗(非英語発話)を解消しなかった。4attempt中4attemptすべて不合格であり、STOP条件(English Lock 2attemptとも失敗)に該当したためここでTrialを終了した。
- **STOP条件との照合**: 「English Lock 2attemptとも失敗」に該当 → Trial判定は`REJECTED`。新しい発音問題(pronunciation safeguard破壊)・hallucination/extra speechの新規発生は確認されず、既存safeguardの破壊は無かった。追加Trialは自ら実施せず、ここでSTOPした。
- **Production影響**: 無し。Key Phrase instruction・retry構成・fallback budget・A2 Production Audio・review lock・Provider・voice・Validator閾値・B1・episode assemblyのいずれも変更していない。
- **User Listening Artifact**: https://claude.ai/code/artifact/c7617694-6220-4258-808b-e22aee15f75a (4attemptすべての音声・source text・ASR・Validator結果を掲載)
- **影響するOPEN_ITEMS**: OPEN-103(`USER_DECISION_REQUIRED`のまま維持。今回のTrialで「Minimal最大2→English Lock最大2」候補は`REJECTED`と判定されたため、対応方針の選択肢から除外)

---

## ER-010-NO9-KEYPHRASE-MINIMAL-INSTRUCTION-MINI-TRIAL-20-R2: No.9 A2正式Key Phrase5件のMinimal instruction Mini-Trial(bounded retry)

- **日付**: 2026-09-01
- **区分**: Trial診断(Production instruction・review lock・retry budget・provider・voice・thresholdはいずれも無変更)
- **背景**: 前回Trial([ER-010-NO9-KEYPHRASE-MINIMAL-INSTRUCTION-TRIAL-AND-RETRY-ACCOUNTING-FIX-19](#))は"opt out"(別テーマの過去実例)と"default"の2語・各1回のみの単発Trialだった。今回はNo.9 A2の**正式Production Key Phrase5件すべて**(`er006_output/pool_pilot_01/pool_n9_tip_screens/a2/key_phrases/keywords_canonicalized.json`から取得、置き換えなし)を対象に、各語まず1回生成しASR/Validator NGの語だけ最大2回まで(各語最大3attempt)retryするbounded Mini-Trialを実施した。目的は`default`の"Dieselt"誤発音が単発varianceだったのか再現性のある問題かの確認、および他4語での安全策維持の確認。

### 対象Key Phrase5件(No.9 A2、Production正式)
| # | Key Phrase | 日本語gloss | Production側の状態(このTrial実施前) |
|---|---|---|---|
| 1 | guilt tipping | 罪悪感からするチップ | OK(reused、master_audio_store) |
| 2 | default | 初期設定の選択肢 | `HUMAN_REVIEW_REQUIRED`(3回ともduration anomaly: 10.77/13.93/9.09秒) |
| 3 | push back | 反発する、抵抗する | OK(reused、master_audio_store) |
| 4 | a catch | 落とし穴、ただし書き | OK(reused、master_audio_store) |
| 5 | starting point | 判断の出発点、基準 | OK(reused、master_audio_store) |

### Minimal instruction(Trial 19から無変更)
```
Speak the following short phrase aloud naturally and clearly, in a warm podcast
announcer voice, exactly once. Say only this phrase — do not add explanations,
examples, introductions, or any other commentary, and do not add, omit, or change
any words. Say it as one natural phrase, not as separate words read one at a time.
Make sure the very last sound of the phrase is actually spoken, not trailed off into
silence, and do not over-emphasize or exaggerate any single sound.
```
既存DECIDED仕様「Key Phrase発音品質(3条件)」(CURRENT_SPEC.md)の(2)語末音素保持・(3)phrase一体感を文言化した部分は無変更のまま維持。

### 実装(`er010_no9_keyphrase_minimal_instruction_minitrial_20_r2.py`、新規)
Production review lock対象の関数(`generate_key_phrase_component_verified`・`generate_narration_snippet_verified_strict`、いずれも`review_lock.guarded_generate*`でguard済み)は一切呼ばない。その内部で実際に使われているのと同一の非guarded関数(`p9a._make_english_call_fn()`によるTTS呼び出し、`p3u.trim_english_keyword_silence()`、`safety.detect_duration_anomaly()`、`secondary_asr.evaluate_attempt_with_cascade()`、`dq18.apply_disfluency_gate()`)を直接組み合わせ、style instructionだけをMinimal instructionに差し替えた。各語につき「PASSしたら即終了、NGのときだけ次のattemptへ」のbounded loop(最大3attempt)を実装し、Production retry countや`er011_output/attempt_history.jsonl`には一切書き込まれないことを確認済み(review_lockモジュールを一切import経由で呼び出していない)。

### Mini-Trial結果(実際に実行した5語・計7 TTS attempt)
| Key Phrase | 結果 | 実行attempt数 | 詳細 |
|---|---|---|---|
| guilt tipping | **PASS(Attempt 1)** | 1 | duration 1.771s(anomaly無し)、ASR="guilt tipping"、`EXACT_MATCH`、disfluency flagged=false |
| default | **FAIL(3attemptとも)** | 3 | 3回ともduration anomaly無し(1.2秒前後)だが、ASRが**英語ではなく他言語**として書き起こされた: Attempt1="デフォルト"(日本語カタカナ)、Attempt2="デフォルト"、Attempt3="默认"(中国語)。3回とも`TTS_FAILURE`(全体類似度が著しく低い) |
| push back | **PASS(Attempt 1)** | 1 | duration 1.031s、ASR="Pushback"、`NORMALIZED_MATCH`(空白除去後一致) |
| a catch | **PASS(Attempt 1)** | 1 | duration 1.111s、ASR="A catch."、`NORMALIZED_MATCH`、語末/tʃ/相当の破裂が聞き取れる書き起こし |
| starting point | **PASS(Attempt 1)** | 1 | duration 1.311s、ASR="Starting point"、`NORMALIZED_MATCH` |

**5件中4件PASS(Attempt 1)・1件(default)は3attemptともFAIL。total actual TTS calls=7(不要な2回目・3回目は、PASSした4語では一切実行していない)。duration anomaly=0件(前回Trial・Production標準経路で見られた10秒超の異常長は今回一度も再発しなかった)。hallucination的な無関係content生成も無し(3回とも"default"という1語相当の短い発話ではあった)。**

### `default`の再現性についての結論
前回Trial(単発)では"Dieselt"という**英語のなかでの**誤認識だったのに対し、今回3回とも**発話される言語自体が英語からずれる**(日本語カタカナ「デフォルト」→日本語カタカナ「デフォルト」→中国語「默认」)という、前回とは異なる、かつより深刻な失敗モードが3回中3回で再現した。これは「単発varianceだった」という解釈を否定し、**Minimal instructionへ切り替えても"default"という語単体は依然として安定してPASSしない**ことを示す。duration anomaly(異常に長い発話)は解消したが、content accuracy(正しい語を正しい言語で発話すること)の失敗が形を変えて残っている。

### STOP条件との照合
タスク仕様§21のSTOP条件A「同一Key Phraseが3attemptすべて明確な誤発音」に該当(`default`が3/3で誤発音、うち2回は言語自体が異なる)。このため、追加Trial(例: `default`の代替instruction文言を試す等)へは進まず、ここでSTOPする。

### 他4語(guilt tipping/push back/a catch/starting point)への影響
4語とも1回目でPASSし、既存の語末音素保持safeguard(a catchの語末/tʃ/、starting pointの語末/t/相当)がASR書き起こし上で維持されていることを確認した(主観的な自然さの最終判断はユーザーが音声を聞いて行う、機械判定のみでは自然さPASSとしない、という既存DECIDED仕様の運用方針通り)。この4語について新しい品質問題は発見していない。

### コスト計測についての既知の制約
このTrialは`er005_cost_logger.init_logger()`を呼び出し専用ログ(`er010_output/no9_keyphrase_minimal_instruction_minitrial_20_r2/cost_log_trial.jsonl`)へ分離したが、実行後同ファイルは0バイトだった。原因は、このTrialが使うTTS呼び出し関数(`p9a._make_english_call_fn()`)・ASR呼び出し関数がいずれも`er005_cost_logger`のcall-level fookを内部に持たない実装であり(grep確認済み、Production側もこの点は同じ)、`cl.logging_context()`でラップするだけでは個々のAPI呼び出しは記録されないため。実際に発生したAPI呼び出し回数は本Decisionの表(TTS 7回・primary ASR 7回、secondary/cascade ASRは`evaluate_attempt_with_cascade`の内部ロジックに応じ0〜数回)で代替把握している。金額自体は小さく(短い1語×7回、Trial 19と同水準)判断に影響しないため、今回はこの制約の記録のみに留め、独立した対応は行わない(OPEN-96と同種の既知の技術的負債パターン)。

### OPEN-103への反映
`USER_DECISION_REQUIRED`のまま維持。今回の結果を踏まえた選択肢はOPEN_ITEMS.mdへ記載。

---

## ER-010-NO9-A2-KEYPHRASE-AUDIO-ISSUES-103-104-17: OPEN-103/OPEN-104個別診断・OPEN-104実装バグ修正

- **日付**: 2026-09-01
- **区分**: Implementation Hardening(サービス仕様は変えず、実装バグの修正・診断のみ)
- **背景**: 前タスク([ER-010-NO9-TTS-NUMBER-WORDS-BUGFIX-AND-AUDIO-RETRY-16](#))で`tts_safe_number_words_en()`のハイフン複合数バグを修正しNo.9 B1を完成させたが、A2は無関係な2件(OPEN-103: Key Phrase 2「default」のduration anomaly、OPEN-104: Key Phrase 4「a catch」日本語meaningのASR不合格)によりepisode assemblyが引き続きblockedのままだった。本タスクはこの2件を個別に診断し、既存Production仕様に対する実装バグであればRoot Cause修正・Regression・A2 Production Audio再実行・episode assemblyまで進め、新仕様判断が必要ならSTOPする、という方針で実施した。

### A. OPEN-103(Key Phrase 2「default」duration anomaly)の診断結果
- **確認した項目**: (1)`estimate_max_reasonable_duration_seconds()`(`er003_audio_tts_asr_safety.py`)の閾値計算式。1語のテキストに対し`1語×EN_MAX_SEC_PER_WORD(1.5秒)+EN_FIXED_OVERHEAD_SECONDS(4.0秒)=5.5秒`となり、実測されている閾値(5.50秒)と一致。計算バグなし。(2)TTS入力の組み立て(`er003_b1_p4c_audio.py::build_tts_prompt()`、Structured Separation)。style instructionとTEXT TO SPEAK section が明示的delimiterで分離されており、"default"というtext単体のみが読み上げ対象として渡されている実装であることをソース確認した。instruction leakageを起こしうる実装バグは無い。(3)実際に何を発話していたかを、保存音声・ASR文字起こしから確認しようとしたが、`er003_b1_p9a_audio.py::generate_narration_snippet()`はduration anomaly検知時、`common.write_wav_float()`(音声ファイル保存)より**前**に`status=STOPPED`を返して打ち切る実装であるため、異常発話そのものの音声は元々一切保存されない設計であることが判明した。現存する`kp2_en.wav`(waveform実測1.61秒)は、異常発生より前の別の正常な生成物であり、今回の3回の異常attemptの証拠ではない。ASR文字起こしも(duration anomaly検知時点でASRを呼ばない設計のため)存在しない。(4)3回の実測duration(10.77秒/13.93秒/9.09秒)に一貫したパターンが無く、決定的な固定の壊れ方(同一の余計な文を毎回読む等)を示していない。
- **Root Cause分類**: 上記(1)〜(4)より、コード側に実装バグ(TTS_INSTRUCTION_LEAK/WRONG_INPUT_TEXT/WRONG_SEGMENT_ROUTING/DURATION_GATE_BUG/RETRY_STATE_BUG)を確認できなかった。**PROVIDER_VARIANCE**(Gemini TTSが短い孤立語"default"に対して非決定的に異常長の発話を生成する挙動)と分類する。[OPEN_ITEMS.md](OPEN_ITEMS.md)のOPEN-05(短文TTS hallucination根本原因未解明)・OPEN-44(hostile architectureの/h/発音異常)と同種の「provider挙動、緩和策止まりで完全解決に至らない」カテゴリに位置づける。
- **STOP A該当**: 本タスクのSTOP条件A(「OPEN-103が単なる実装bugではなくTTS provider variance/新仕様問題」)に該当するため、閾値変更・retry cap変更・prompt文言変更のいずれも行っていない。ロック状態(`HUMAN_REVIEW_REQUIRED`)もそのまま維持し、`approve_regenerate()`は呼んでいない。

### B. OPEN-104(Key Phrase 4「a catch」日本語meaning、meaning_4)のRoot Cause特定
- **raw diff**: canonical「落とし穴、ただし書き」に対し、実際に記録されている6回のASR文字起こしは一貫して「おとしあな ただしがき」(1回のみ「お年やな、ただしがき」という別の異表記)。
- **normalized diff**(実際のProduction Validator`er007_ja_asr_validator_01.py::normalize_ja()`を直接実行して確認): canonical正規化後「落とし穴ただし書き」、ASR正規化後「おとしあなただしがき」。
- **メカニズム**: `protected_check_ja()`が両者に対し文字単位`difflib.SequenceMatcher`を実行すると、canonical(漢字混じり)とASR(全文ひらがな)の間で偶然一致するひらがな数文字(と/し/た/だ/き)だけが"equal" opcodeとして拾われ、残りが"落→お"/"穴→あな"/"書→が"という3つの細切れなopcodeへ不自然に分断される(実際にdifflibを実行してopcode列を確認済み)。各opcodeの読み比較には前後4文字のpadding窓を使うが、この窓はcanonical側・ASR側で対応しない範囲を切り出してしまう(例:「書」→「が」のopcodeでは`c_padded`="穴ただし書き"、`a_padded`="なただしがき"となり、窓の開始位置が語境界的に対応していない)。この結果、局所`_reading_equal`/`_reading_equal_allowing_voicing`比較がいずれも失敗し、本来は語末の連濁(「書き」の読み「かき」→複合語内では「がき」)1点だけの差でしかない箇所まで`TRUE_CONTENT_MISMATCH`(内容誤りの可能性)へ分類されていた。実際、canonical・ASR双方の**全文**の読み(pykakasi)は"otoshianatadashikaki"/"otoshianatadashigaki"であり、差は1モーラの連濁(清濁)のみであることを直接確認した。
- **Root Cause分類**: **NORMALIZER_BUG**(`protected_check_ja()`の文字単位diff+局所padding窓アルゴリズムが、canonical=漢字混じり・ASR=全文ひらがな書き起こしという script差の大きいケースで、語境界の対応を保証できない実装上の限界)。既存の日本語ASR Validatorはこのケースを想定した「頃/ごろ」型の局所voicing許容メカニズムを既に持っていたが、局所opcode単位でしか読みを比較しないため、opcode分断そのものが起きるケースには対応できていなかった。

### C. OPEN-104の修正内容
- `er007_ja_asr_validator_01.py::classify_ja_asr_match()`の`non_cascade_diffs`分岐へ、局所opcodeに頼らない**全文**の読み比較による安全網を追加した。正規化後の全文(`c_norm`/`a_norm`)を直接`_reading_equal()`/`_reading_equal_allowing_voicing()`(いずれも既存の「頃/ごろ」メカニズムで確立済みの関数、新規実装なし)へ渡し、(a)全文の読みが完全一致する場合は、既存の「content_diffsが空ならPHONETIC_MATCH」ルール(このファイルに元々ある確定ロジック)と同じ確信度として即PASS(`should_pass=True`)、(b)濁点/半濁点の有無だけが差となる場合は、既存の局所phonetic_uncertain(「頃/ごろ」)と同じ慎重さを保ち、即PASSにはせず`ASR_VALIDATION_UNCERTAIN`(Cascade[追加ASR再確認]対象)とする。いずれも既存2ルールをwhole-text scopeへ一般化したものであり、新しい許容基準を追加したものではない。数字・否定の保護(`protected.passed`チェック)はこの分岐へ到達する時点で既に通過済みのため、一切弱めていない。
- **hardcodeでないことの証拠**: 「書き」という特定語への個別対応は一切行っていない。修正が汎用ルールであることを、別の漢字・別の連濁パターンを含む正の回帰fixture(「歯止め」→「はどめ」、「三日坊主」→「みっかぼうず」、いずれもmeaning_4とは無関係な合成データ)で確認した。
- **Regression**: `er007_ja_asr_validator_01_test.py`に新規fixture群(`WHOLE_TEXT_SCRIPT_MISMATCH_FIXTURES`3件・`WHOLE_TEXT_SCRIPT_MISMATCH_NEGATIVE_FIXTURES`2件、うちmeaning_4の実データ1件を含む)を追加し、既存30件+新規5件=**全35件PASS**(既存fixtureへの回帰なし)。負のfixture(全文ひらがなASRでも内容語が真に置換されている合成ケース)が引き続き`TRUE_CONTENT_MISMATCH`のままであることも確認し、「全文ひらがなASRなら何でもPASS」という誤った一般化になっていないことを検証した。`run_project_regression.py`(全1998件)でも本修正による新規failureは0件(4件の既存failureはいずれも本修正と無関係、`git stash`で本修正前の状態に戻しても同一失敗であることを確認済み: `er003_test_bad`[意図的な負の確認用fixture]、`er003_test_p2j_investigate`のcollection count系2件[リポジトリ内ファイル増加によるカウントずれ]、`er007_ja_tts_retry_path_fix_test_01`のretry-path試験1件)。
- **Production Validator再検証**: 実際に6回失敗した際の生ASRテキスト(「おとしあな ただしがき」)をそのまま使った回帰fixtureで、修正後は`ASR_VALIDATION_UNCERTAIN`(Cascade対象、`TRUE_CONTENT_MISMATCH`から離脱)になることを確認した。

### D. review_lockとの整合性確認・meaning_4のみ承認
- 本修正はmeaning_4のcanonical text自体を変更していない(Validator側のロジックのみ修正)ため、`er011_human_review_lock_01.py`のlock key(`SHA256(canonical_text)`)は変化せず、既存の`HUMAN_REVIEW_REQUIRED`ロックは自動的には解除されない(前タスクの`tts_safe_number_words_en()`修正時とは異なり、今回はTTS入力テキスト自体は不変のため)。`approve_regenerate()`のdocstringは「ユーザーの明示的な指示でのみ呼ぶこと」と明記しており、これは本タスクのSTOP C(「既存retry cap/review-lockを変更する必要がある」)に相当する判断点と整理し、Claude Codeの単独判断では呼び出さず、ユーザーへ明示確認した(AskUserQuestion)。ユーザーが承認したため、meaning_4のみ`review_lock.approve_regenerate()`を実行(kp2_en/OPEN-103には一切触れていない)。

### E. Production A2 Audio再実行結果
- 記事再生成は行わず、B1(既に完成済み)にも一切触れず、`er009_n1_production_integration_01.py`の既存Production関数(`generate_a2_segments()`/`stage_assemble_a2()`)をA2のみ直接呼び出す実行スクリプト(`er010_no9_a2_only_audio_rerun_17.py`)を新規作成して再実行した(既存関数のロジックは無変更、呼び出し範囲をA2のみへ絞っただけ)。
- 1回目の再実行(`approve_regenerate()`前): 期待通りkp2_en/meaning_4とも0 API callでブロックされたまま(ロック状態・updated_atとも変化なし)、他の18segmentは正常にPASS。
- `approve_regenerate()`後の2回目の再実行: **meaning_4が1回目の試行で`classification=NORMALIZED_MATCH`・`verified=true`でPASS**(この回はASRが偶然「落とし穴 ただし書き」と漢字で書き起こしたため、既存の表記正規化ルールのみで一致した。今回の修正[全文読み安全網]が実際に発動する「全文ひらがなASR」のケースそのものは、今回のライブ試行では再現しなかったが、修正の必要性・正しさ自体は前述Cの回帰fixtureで独立して確認済み)。meaning_4のロック状態は`RESOLVED`(final_status=OK)へ遷移した。
- kp2_en(OPEN-103)は未変更のまま`HUMAN_REVIEW_REQUIRED`が継続し、A2 episode assemblyは`EPISODE_BLOCKED_BY_AUDIO_VALIDATION: kp2_english=UNVALIDATED`(のみ)で引き続き中止された。これは今回OPEN-103に一切手を付けていないことと完全に整合する、意図通りの結果。

### F. OPEN-103/104の状態まとめ
- **OPEN-104**: `RESOLVED / CLOSED`(`protected_check_ja()`のscript-mismatch window不整合バグについて。修正・Regression・Production runtime再検証まで完了)。
- **OPEN-103**: `USER_DECISION_REQUIRED`のまま維持(Root Cause分類をPROVIDER_VARIANCEとして確定・記録。コード修正は行っていない)。
- **OPEN-100/OPEN-101/OPEN-102**: 変更なし。
- A2 episode assemblyの残Blocking要因はOPEN-103のみ。B1は前タスクより完成済みのまま変更なし。

- **Git**: 本Decisionに対応するcommit SHAは、本タスクの完了報告を参照。
- **根拠**: 本セッションの実行ログ・diff実測(`diag_open104.py`/`diag_open104_b.py`スクラッチスクリプト)、`er010_output/no9_a2_keyphrase_audio_issues_103_104_17/`配下の実行ログ、`er006_output/pool_pilot_01/pool_n9_tip_screens/a2/audit/review_lock_state.json`。

---

## ER-010-NO9-KEYPHRASE-MINIMAL-INSTRUCTION-TRIAL-AND-RETRY-ACCOUNTING-FIX-19: Key Phrase Minimal Instruction Trial(OPEN-103)・review lockネスト二重会計バグ修正(OPEN-105)

### OPEN-103: Key Phrase英語音声 Minimal Instruction Trial

- **日付**: 2026-09-01
- **背景**: 前タスク(ER-010-NO9-B1-APPROVAL-AND-OPEN103-TTS-DIAGNOSTIC-18)の
  監査で、Key Phrase英語標準経路が記事本文Full Story向けの約250語
  instruction(`ENGLISH_STYLE_PREFIX = er002_common.build_style_prefix()`、
  `COMMON_BASE_INSTRUCTION+LEVEL2_INSTRUCTION`)を1語〜短いphraseの
  読み上げにそのまま使っていることが、No.9 kp2_en("default"、3回とも
  duration anomalyでSTOPPED)の可能性の高いtriggerと判定された。今回、
  ユーザー指示により、Key Phrase専用のMinimal instructionへ切り替えた
  場合の実データ比較Trialを実施した(Production review lock・retry cap
  は一切変更しない、隔離Trial)。
- **Trial instructionの設計根拠**: 既存DECIDED仕様「Key Phrase発音品質
  (3条件)」(本ファイル2026-08-12エントリ、CURRENT_SPEC.md該当行)の
  (1)Meaning/contextual prosody (2)Phoneme integrity(語末音素保持)
  (3)Phrase grouping(単語ごとに分断しない)を踏まえ、既にTrial実績のある
  文言(`er003_v1_a2_audio_02_generate.TRIAL_CLARITY_INSTRUCTION_PREFIX`、
  ER-003-CROSSLEVEL-AUDIO-01/04)と、既にProduction fallbackとして
  承認済みの`repro01.MINIMAL_INSTRUCTION_PREFIX`の文言をそのまま踏襲し、
  条件(3)相当の一文のみ新規に文章化して追加した(`er010_no9_keyphrase_
  minimal_instruction_trial_19.py::MINIMAL_INSTRUCTION_TRIAL_PREFIX_V2`)。
  条件(1)(記事文脈依存の意味prosody)は、単語単体のTrialでは記事文脈を
  持たないため汎用instructionとして対応しておらず、既知の制約として
  明記する。
- **Trial結果(実TTS 2件、実ASR 2件、cascade validatorによる二次確認込み)**:
  - `opt out`(A02実Production Key Phrase、過去にCurrent instruction標準
    経路で完全に無関係な内容[65字/104字のhallucination]を生成した実
    fixture): Minimal Trial版は1.091秒(anomaly閾値7.0秒の範囲内)、ASR
    "Opt-out"、`er006_secondary_asr_01.evaluate_attempt_with_cascade`
    (force_secondary=True、Production同一ロジック)で`verified=True`・
    `classification=NORMALIZED_MATCH`を確認。**VALIDATED相当**(既存の
    単純Minimal fallbackが達成していた成功と同等の内容正確性を、語末
    音素・phrase grouping対策を追加した上でも維持)。
  - `default`(No.9 kp2_en、今回最重要): Minimal Trial版は0.871秒
    (anomaly閾値5.5秒の範囲内、duration anomaly自体は再発しなかった)。
    ただしASRが"Dieselt"と書き起こし、Production同一のcascade
    validatorで`verified=False`・`classification=TTS_FAILURE`
    (content_word_diff: canonical="default"→asr="dieselt")と判定
    された。**単発試行でREJECTED相当**(duration anomalyという当初の
    失敗モードは解消したが、別の失敗モード[誤発音/hallucination型の
    置換]が新たに観測された)。
- **サンプル数の制約**: 各語1回のみの実行(タスク仕様のコスト抑制方針、
  「大量Trialは不要」に従った)。特に`default`は1回の失敗のみを根拠に
  しており、複数回実行すれば異なる結果になる可能性を否定できない
  (STOP条件F「新しいquality issue発見」に該当するため、追加試行は
  ユーザー判断を待たず自らは実施しなかった)。
- **判定**: `USER_DECISION_REQUIRED`(`opt out`はVALIDATED相当だが、
  `default`が単発試行でcontent-accuracy失敗を示したため、Minimal
  instructionへのProduction全面切替を推奨できる状態ではない。
  duration-anomaly型の問題は改善する可能性がある一方、別の発音精度
  リスクを負う可能性があるというトレードオフを、ユーザー判断へ委ねる)。
- **今回実施しなかったこと**: Production instruction(`ENGLISH_STYLE_
  PREFIX`/`MINIMAL_INSTRUCTION_PREFIX`)の変更、fallback budget配分の
  変更、retry cap・provider・voiceの変更、kp2_enのreview lock解除
  (`approve_regenerate()`)、`default`への追加Trial試行。
- **状態**: `USER_DECISION_REQUIRED`(OPEN-103は継続、Trial実施のみで
  Production未反映)
- **根拠**: `er010_no9_keyphrase_minimal_instruction_trial_19.py`、
  `er010_output/no9_keyphrase_minimal_instruction_trial_19/trial_results.json`、
  実音声`.../audio/kp_default_no9_a2.wav`・`.../audio/kp_opt_out_a02_repro.wav`

### OPEN-105: guarded_generateネスト二重会計バグ(review lock)の修正

- **日付**: 2026-09-01
- **Root Cause確定**: `er003_v1_repro01_main_generate.py::generate_key_
  phrase_component_verified()`(`@review_lock.guarded_generate("en")`)が、
  内部で標準経路として`generate_narration_snippet_verified_strict()`
  (`@review_lock.guarded_generate_with_language_arg`、他の呼び出し元
  [`stage_c_generate_new_narrations()`等]からも単独で直接呼ばれるため、
  このデコレータ自体は必要)を直接呼び出すネスト構造になっていた。
  実TTS試行3回(すべてSTOPPED)の1回の論理的生成操作に対し、(1)内側の
  `record_outcome()`がcumulative_tts_attempts=3として正しく記録した
  直後、(2)外側の`record_outcome()`が`result.get("attempts_log") or
  result.get("standard_attempts_log")`というfallback連鎖経由で同じ3
  試行分を再度読み取り、cumulative_tts_attempts=6として上書きして
  いた。`er011_output/attempt_history.jsonl`の同一timestamp(kp2_en/a2、
  2026-09-01T11:21:05)の2エントリ(run_id違い、cumulative=3→6)で実
  データ確認済み(前タスクの監査結果を引き継ぎ、今回Root Causeの機構を
  最終確定した)。
- **retry/fallback制御への実害の有無**: `fallback_budget = max(0,
  max_attempts - len(standard.get("attempts_log") or []))`は、標準経路
  呼び出しが直接返した生の結果dictの`attempts_log`をそのまま参照して
  おり、review lock storeの`cumulative_tts_attempts`(二重会計される値)
  は一切参照していない。よって単一呼び出し内のfallback予算配分は
  この二重会計バグの影響を受けていない(タスク仕様§14のCase Cに相当:
  standard 3回でmax_attempts=3を使い切る設計自体がfallback未到達の
  原因であり、二重会計とは別問題)。一方、永続化される
  `cumulative_tts_attempts`/`cumulative_asr_calls`は、複数run跨ぎの
  `BUDGET_GUARD_TRIGGERED`(上限15回/60回)判定に使われるため、二重
  会計が続いていた場合、本来より約2倍速くこの累積guardへ到達する
  リスクがあった(kp2_enでは上限未到達のため今回実害なし)。
- **Fix判定**: `record_outcome()`のdocstring・設計意図(「generate関数の
  実行完了後に必ず呼ぶ」=1回の論理操作につき1回)から、「1 TTS call =
  1 attempt」がSSOT意図として明確であり、純粋な実装バグとして修正した。
- **修正内容**: `guarded_generate`/`guarded_generate_with_language_arg`
  両デコレータへ、モジュール共有のreentrancy guard(`_ACTIVE_GUARDED_
  OUT_PATHS`という module-level set)を追加した。同一out_pathに対する
  外側のguarded呼び出しが進行中の場合、内側の呼び出しは
  check_before_generation/record_outcomeを一切行わずfnへ直接委譲する。
  呼び出し側(`generate_key_phrase_component_verified`本体・fallback
  budget計算・他の呼び出し元)のコードは一切変更していない。他の
  guarded_generate利用箇所4件(charon英語/日本語、point_headings、
  news_tail_fix)は`generate_narration_snippet_verified_strict`を内部
  呼び出ししておらず、同種のネスト構造を持たないことをgrepで確認済み
  (影響範囲はgenerate_key_phrase_component_verified 1箇所のみ)。
- **Regression**: 新規2件(`test_nested_guarded_calls_do_not_double_
  count_attempts`・`test_nested_guarded_calls_inner_check_is_skipped_
  not_reevaluated`、実デコレータ2枚を重ねて実際のネスト構造を再現)を
  `er011_human_review_lock_01_test_01.py`へ追加、既存13件と合わせて
  15件全PASS。関連する`er008_crosslevel_audio_02_tts_cap_25_test_01.py`
  (1件)・`er010_n9_production_integration_09_test_01.py`(28件)も
  PASSのまま(いずれもgenerate_narration_snippet_verified_strict/
  review_lockをimportする既存test)。
- **Runtime evidence**: `er003_v1_repro01_main_generate.generate_key_
  phrase_component_verified()`本体を実際に呼び出し(TTS呼び出し自体を
  強制失敗させ実API課金ゼロ)、修正後はcumulative_tts_attempts=3(修正
  前の実データでは6)であることを一時ディレクトリ上のReview Lock
  storeで確認した。
- **状態**: `CLOSED`(純粋な実装バグ修正・regression・runtime evidence
  すべて完了)
- **根拠**: `er011_human_review_lock_01.py`(修正箇所)、
  `er011_human_review_lock_01_test_01.py`(新規テスト2件)、
  `er011_output/attempt_history.jsonl`(Root Cause実データ)
- **影響するCURRENT_SPEC項目**: Human Review Cost Guard(Review Lock機構)

---

## ER-010-NO9-B1-APPROVAL-AND-OPEN103-TTS-DIAGNOSTIC-18: No.9 B1音声のUser Approval・完成音声提示ルール再確認・OPEN-103 TTS payload監査

- **日付**: 2026-09-01
- **区分**: User Decision記録(①②) + Implementation Hardening(サービス仕様は変えないdiagnostic監査、コード変更なし)

### ① No.9 B1完成音声のUser Approval
- ユーザーが「B1音声はOK。承認。」と明示的に判定した。対象は`er006_output/pool_pilot_01/pool_n9_tip_screens/b1b/assembled/English_Your_Way_B1B_POOL_N9_TIP_SCREENS.wav`(64,464,748 bytes、stereo 48kHz、335.75秒)。この音声は既存Production正式経路(`er003_v1_n3_01_tts_generate.py::generate_b1_segments()`→`er003_v1_n3_01_assemble.py`のB1組み立て)で生成・QA(ASR verified/disfluency gate)・assemblyまで完了済みであり、source article(`er006_output/pool_pilot_01/pool_n9_tip_screens/b1b/parts.json`/`b1_support_texts.json`/`key_phrases/keywords_canonicalized.json`)と内容一致していることを本タスクで再確認した。
- **状態**: `DECIDED`(ユーザー承認済み、No.9 B1は正式完成状態)。本タスクではB1の再生成・修正・再試行は一切行っていない。

### ② 完成音声のユーザー確認提示ルール(Audio + Full Script)
- ユーザーが「今後、完成音声の確認・試聴・承認が必要な場合は、必ず完成Audio + full scriptをセットで提示する」ことを標準運用として指示した。
- **既存仕様との関係**: [CURRENT_SPEC.md](CURRENT_SPEC.md)の「試聴Artifact(ユーザー提示用ページ)仕様」節には、2026-08-29(ER-008-N8-CLOSEOUT-GOVERNANCE-25)付ですでに同趣旨の「全script掲載の必須化」が`DECIDED`として存在していた。ただし、直前のタスク(本タスクの前段でユーザーから「B1の音声はどこで聞けるの?」と聞かれた際に作成したAudio Artifact)はKey Phrase一覧のみを掲載し、既存仕様が求める全segment分のfull scriptを掲載していなかった。本User Decisionは、この既存仕様を(a)今回の欠落を機に再確認・再徹底し、(b)対象を「正式Artifact」だけでなく今回のような単発の試聴用リンクにも明示的に拡張するものと位置づける。新規ルールの新設ではなく、既存`DECIDED`仕様の適用範囲拡張として[CURRENT_SPEC.md](CURRENT_SPEC.md)の該当節へ追記した。
- **是正**: 該当のB1試聴Artifact(`https://claude.ai/code/artifact/08ca3f13-edf8-46cc-bd68-eb5999f9ed93`)へ、実際にB1 assemblyが読み上げる全segment(Welcome〜In One Lineまで、`build_b1_timeline()`の実際の並び順)のscript全文を追記して再公開した(音声本体・Key Phrase内容は無変更)。
- **状態**: `DECIDED`。[CURRENT_SPEC.md](CURRENT_SPEC.md)「試聴Artifact仕様」節へ適用範囲拡張を追記。

### OPEN-103(Key Phrase 2「default」duration anomaly)TTS request payload監査
前タスクの診断(Root Cause=PROVIDER_VARIANCE、証拠不足のため確定に至らず)を受け、実際にProviderへ送信された最終payload構造・instruction/text境界・attempt 1〜3の履歴を、read-onlyでコード・ログから追加監査した(新規TTS呼び出しは一切行っていない)。

- **実際の呼び出し経路の確認**: `er003_v1_n3_01_tts_generate.py::generate_a2_segments()`→`er006_audio_cost_pilot_02_shared_narration.py::ensure_key_phrase_english_component()`→`er003_v1_repro01_main_generate.py::generate_key_phrase_component_verified()`(標準経路)→`generate_narration_snippet_verified_strict()`→`er003_b1_p9a_audio.py::generate_narration_snippet()`→`er003_b1_p4c_audio.py::build_tts_prompt()`でGeminiへの最終promptを組み立て、Batch API(`er006_batch_tts_wiring_01.py::make_batch_tts_call_fn()`)経由で送信。
- **instruction/text境界**: `build_tts_prompt()`は`"=== STYLE INSTRUCTIONS (... do not speak this section aloud ...) === ... === TEXT TO SPEAK (speak this section aloud exactly as written, and nothing else ...) === {text} === END TEXT TO SPEAK ==="`という明示的delimiter構造(Structured Separation、ER-005-AUDIO-INSTRUCTION-SEPARATION-01)を使っており、"default"という1語だけがTEXT TO SPEAKとして渡されている。delimiter自体の実装に境界の曖昧さは確認できなかった。
- **新規判明した事実(1): instruction量とtext量の極端な不均衡**: kp2_en(標準経路)が使うstyle instruction(`ENGLISH_STYLE_PREFIX`=`er002_common.py::COMMON_BASE_INSTRUCTION+LEVEL2_INSTRUCTION`)は、フルストーリー本文のナレーション向けに書かれた約700語規模の演技指示("Create a natural emotional arc..."/"Carry the meaning naturally across sentence boundaries..."等)であり、読み上げ対象の"default"(1語)に対して比率が極端に大きい。このコード自身のコメント(`er003_v1_repro01_main_generate.py`)が、まさに同じ「長いENGLISH_STYLE_PREFIXを文脈のない短い単独フレーズに使うとモデルが無関係な内容へ迷い込みやすい」現象を、別テーマの実例(kp5_en 17.33秒、"opt out"のhallucination)として既に文書化しており、今回のkp2_en「default」もこれと同型のtrigger条件(重い演技指示 : 極小text の比率)に該当する。
- **新規判明した事実(2): 既存の緩和策(minimal instruction fallback)が今回1回も実行されなかった**: `generate_key_phrase_component_verified()`は、まさに(1)の現象への対策として`generate_english_component_minimal_instruction()`(演技指示を持たない最小限instructionへの切替)というfallback経路をすでに実装済みだった。しかし`fallback_budget = max(0, max_attempts - len(standard.attempts_log))`という予算配分式(ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15 Part B、standard+fallback合計をmax_attempts=3回に収める意図的な既存コスト管理)により、標準経路が3回ともduration anomalyでSTOPPEDした時点でfallback予算は0となり、この既存の緩和策はkp2_en「default」に対して**一度も試行されなかった**ことをログ(`review_lock_state.json`のkp2_en `last_attempts_log`、3件とも標準経路のみ)から確認した。
- **新規判明した、OPEN-103とは別の問題(review_lock二重会計)**: `generate_key_phrase_component_verified()`(`@review_lock.guarded_generate("en")`)が内部で呼ぶ`generate_narration_snippet_verified_strict()`自体も`@review_lock.guarded_generate_with_language_arg`で二重にguardされているため、同一の3回の実TTS試行が`record_outcome()`により2回記録され、`er011_output/attempt_history.jsonl`のkp2_en(a2)に同一timestampで`cumulative_tts_attempts=3`→`cumulative_tts_attempts=6`という2エントリが残っていることを確認した(実際のTTS API呼び出し回数は3回のみで、6回ではない。二重に記録されるのは`cumulative_tts_attempts`等の会計値のみ)。`MAX_CUMULATIVE_TTS_ATTEMPTS=15`のため今回は実害無しだったが、この二重会計により本来より少ない実attempt数で`BUDGET_GUARD_TRIGGERED`(cumulative>15)へ到達しうる、review_lockの正確性に関わる別種のバグである。
- **Root Cause再分類**: `TTS_INSTRUCTION_LEAK_LIKELY`(既存コードの過去実例と同型のinstruction:text不均衡が明確なtrigger候補として特定できたため、前回の「PROVIDER_VARIANCE、証拠不足」より一段具体的な分類へ更新)。ただし、これが「モデルの非決定的挙動」であること自体は変わらず(同一payloadで3回とも異なるduration)、`build_tts_prompt()`のdelimiter構造自体に実装バグは無い。
- **STOP該当・今回実施しないこと**: 以下はいずれも新しいUser Decisionが必要な「新仕様判断」であり、本タスクでは一切変更していない(section 14/22の禁止事項どおり)。
  1. Key Phrase等の極小textに対し、フルストーリー用の重いstyle instructionではなく最初からminimal instructionを使う、またはfallback用に独立予算を与えるという設計変更(STOP B/C相当)。
  2. review_lock二重guardの解消(`generate_narration_snippet_verified_strict()`と`generate_key_phrase_component_verified()`のどちらのguardを残すか、または二重時のrecord_outcome側で重複除去するか、という実装判断。retry cap会計の挙動を変えるため、実施にはユーザー確認が必要と判断、STOP C/E相当)。
- **OPEN_ITEMS反映**: OPEN-103の行を本監査結果で更新(状態は`USER_DECISION_REQUIRED`のまま)。review_lock二重会計は新規OPEN-105として追加した。

- **根拠**: 本セッションのコード監査(`er003_v1_repro01_main_generate.py`/`er006_audio_cost_pilot_02_shared_narration.py`/`er003_b1_p9a_audio.py`/`er003_b1_p4c_audio.py`/`er002_common.py`/`er011_human_review_lock_01.py`/`er006_batch_tts_wiring_01.py`)、`er011_output/attempt_history.jsonl`、`er006_output/pool_pilot_01/pool_n9_tip_screens/a2/audit/review_lock_state.json`。
- **Git**: 本Decisionに対応するcommit SHAは、本タスクの完了報告を参照。Production codeの変更は無し(SSOT文書のみ)。

---

## ER-010-N1-SPEC-LIFECYCLE-PRODUCTION-GATE-04: 仕様Lifecycle・Dangling Reference Checkの正式導入

- **日付**: 2026-08-31
- **内容**: 品質・Prompt改善提案(Trialを経てProduction Writer Prompt等へ新原則を追加する類の提案)について、`PROPOSED`→`VALIDATED`→`APPROVED_FOR_PRODUCTION`→`PRODUCTION_WIRED`の4段階Lifecycleと、`PRODUCTION_WIRED`と判定するための12必須条件、およびProduction code/Promptが新しい仕様名を参照する際の「Dangling Reference Check」を正式なProduction開発ルールとして導入した。記録先は[PROJECT_INDEX.md](PROJECT_INDEX.md)の「仕様Lifecycle」節(既存の「状態ラベル(全文書共通)」節に隣接)
- **状態**: `DECIDED`(ユーザーが本ルールの内容・記録先ともに明示的に指示した運用ルール導入)
- **採用理由**: ER-010-N1-WRITER-PRINCIPLES-STATUS-AUDIT-03で、Storytelling First/No Jargonという2つの原則が、正式なユーザー承認もProduction初回Writerへの実装も無いまま、Diagnostic Full Retryモジュール(`er009_diagnostic_full_retry_modules_12.py`)から`Preserve Storytelling First.`/`Preserve No Jargon.`として参照される「Dangling Reference」状態のままProduction配線されていたことが判明した。この事故の再発を防ぐには、(a)「Trialで良い結果が出た」ことと「Production採用が決定した」ことを明確に区別するLifecycle、(b)後段コードが前段に存在しない仕様を参照していないかを機械的に確認する手順、の両方が必要と判断した
- **比較した選択肢**: (1)新規governance文書の作成、(2)既存[PROJECT_INDEX.md](PROJECT_INDEX.md)の「状態ラベル(全文書共通)」節の拡張
- **却下理由(1)**: 新規文書はPROJECT_INDEXが担う「全文書共通ルールの一次参照先」という既存の役割と重複し、SSOT構造を複雑化させるため不採用。(2)を採用: 既にPROJECT_INDEXが状態ラベルの共通定義を持っており、そこへの自然な拡張と判断した
- **既存記録との関係**: `PRODUCTION_WIRED`という語自体は本ルール導入以前から[CURRENT_SPEC.md](CURRENT_SPEC.md)/[DECISION_LOG.md](DECISION_LOG.md)内で運用上使われていた(例: Diagnostic Full Retry、Point Overlap Writer full retry等)。本ルールはその既存の運用を正式に定義するものであり、導入以前に`PRODUCTION_WIRED`と記録済みの個別項目を本ルールに照らして再監査・再判定することは今回のタスクの範囲外とする(既存記録はそのまま維持)
- **Storytelling First/No Jargonの扱い**: 本タスクでは両原則の採用可否についてClaude Codeが判断・変更することはしない(`USER_DECISION_REQUIRED`のまま)。再発防止の追跡対象として[OPEN_ITEMS.md](OPEN_ITEMS.md)のOPEN-95へ新規記録した
- **根拠レポート**: ER-010-WRITER-PRINCIPLES-STATUS-AUDIT-03(前提調査)、ER-010-SPEC-LIFECYCLE-PRODUCTION-GATE-04(本ルール導入)
- **commit**: (本コミット)
- **影響するCURRENT_SPEC項目**: なし(プロセスルールの導入のみ。個別のProduction Writer仕様は一切変更していない)

## ER-003-B1-P7A: Preview TTSモデルをgemini-3.1-flash-tts-previewへ

- **日付**: 2026-08-06
- **内容**: Previewの日本語音声生成モデルを`gemini-2.5-pro-preview-tts`から`gemini-3.1-flash-tts-preview`へ切替
- **状態**: `DECIDED`
- **採用理由**: 旧モデルで「激しい」→「げきせつな」等の誤読が発生。3.1へ切替後、単一call検証で解消を確認
- **比較した選択肢**: 2.5継続 vs 3.1切替
- **却下理由(2.5継続)**: 誤読の再現性が高く、Preview用途に不適
- **根拠レポート**: ER-003-B1-P7A実行報告(18項目)
- **commit**: `b4f871f`
- **影響するCURRENT_SPEC項目**: Preview > TTS model

## ER-003-B1-P5A〜P5C: Google Cloud TTS(Neural2-B)を不採用

- **日付**: 2026-07-26頃
- **内容**: 日本語TTSエンジンとしてGoogle Cloud TTS(Amazon Pollyも候補)を検証したが不採用
- **状態**: `REJECTED`
- **採用理由**: (該当なし、不採用)
- **比較した選択肢**: Google Cloud TTS Neural2-B、Gemini TTS
- **却下理由**: ユーザー試聴で機械的な音声・誤読(「何が」→「なんが」)と判定され不合格
- **根拠レポート**: P5A/P5B/P5B-GCP/P5Cの各commit
- **commit**: `ffe9cc9`, `0fe94eb`, `8193e0b`, `e2b75b7`
- **影響するCURRENT_SPEC項目**: Full Story/Preview > TTS model(Gemini採用の背景)

## ER-003-P2I: Key Phrase選定方式にStrategy L(Listening Blocker Ranking)を採用

- **日付**: 2026-07-xx
- **内容**: B2 Key Words選定の標準方式として方式L(Listening Blocker Ranking)を採用
- **状態**: `DECIDED`
- **採用理由**: 「初回リスニングで理解を止める可能性が高い表現を選ぶ」という単純で説明可能な原則、個別学習者プロファイルへの依存がない
- **比較した選択肢**: 方式L(Listening Blocker Ranking)/方式P(Difficulty Portfolio)/方式U(Observed Learner Profile)。Top5評価はL・Uが同点
- **却下理由(P)**: Top5・Total双方の評価で他方式に劣る
- **却下理由(U)**: 標準方式としては不採用(将来のパーソナライズ機能候補として保持)
- **根拠レポート**: [ER-003-P2I_decision_record.md](er003_output/p2i/ER-003-P2I_decision_record.md)
- **commit**: `e33f227`
- **影響するCURRENT_SPEC項目**: Key Phrase > 選定方式

## ER-003-REPRO-01-KP: B1本文からKey Phraseを新規選定する方針へ訂正

- **日付**: 2026-08-08
- **内容**: Key PhraseはB2時代の承認済みリストを流用せず、各記事自身のCEFR-B1本文から方式Lで新規選定する
- **状態**: `DECIDED`
- **採用理由**: ユーザー指摘により、B2時代の選定結果をB1へ流用する前提が誤りと判明
- **比較した選択肢**: B2承認済みリストの流用 vs B1本文からの新規選定
- **却下理由(流用)**: 記事本文がB1で書き直されている以上、選定根拠が古い
- **根拠レポート**: ER-003-REPRO-01-KP実行報告
- **commit**: `46aa2e8`
- **影響するCURRENT_SPEC項目**: Key Phrase > 選定元

## ER-003-KP-01: Pedagogical Phrase Canonicalizationの導入

- **日付**: 2026-08-08
- **内容**: Strategy Lの`display_phrase`を自然な学習単位`key_phrase`へ正規化する後処理段階を新設
- **状態**: `DECIDED`
- **採用理由**: `display_phrase`のまま採用すると学習単位として不自然/過不足がある場合がある
- **根拠レポート**: ER-003-KP-01実行報告、[er003_key_words_canonicalization.py](er003_key_words_canonicalization.py)
- **commit**: `e607d26`(Canonicalization本体)、`ae4928c`(3状態QAモデルへ拡張)
- **影響するCURRENT_SPEC項目**: Key Phrase > 後処理、QAモデル

## ER-003-KP-02: Canonicalization原則を「最小」から「最小十分」へ

- **日付**: 2026-08-08
- **内容**: Canonicalizationの目標を単なる「最小化」から「意味を保ったまま最小十分」へ修正
- **状態**: `DECIDED`
- **採用理由**: 「最小」を追求すると意味を保持する語まで削ってしまうリスクがある(over-minimization)
- **根拠レポート**: ER-003-KP-02実行報告
- **commit**: `8856264`
- **影響するCURRENT_SPEC項目**: Key Phrase > Canonicalization原則

## ER-003-KP-02-R1: Meaning Preservation Ruleの追加とTraceability再定義

- **日付**: 2026-08-08
- **内容**: (1) 意味保持QA(`qa_core_meaning_preserved`/`qa_no_semantic_role_loss`)を追加。(2) Traceability要件を「literal substring」から「source_spanから説明可能な正規化で導出できる」へ再定義。`normalization_reason`フィールド(固定enum)を追加
- **状態**: `DECIDED`
- **採用理由**: 「take a player off」(A01既承認)のような正当な文法的正規化が、旧Traceability定義では誤ってFAILと判定されていた
- **比較した選択肢**: 文字通りの部分文字列一致を維持 vs 説明可能な正規化まで許容
- **却下理由(維持)**: 既承認の正当な正規化ケースを説明できない
- **根拠レポート**: ER-003-KP-02-R1実行報告(16項目)
- **commit**: `5a94db0`
- **影響するCURRENT_SPEC項目**: Key Phrase > Traceability定義、`normalization_reason`

## used_form / key_phrase の重複を技術的負債として記録し整理しない

- **日付**: 2026-08-08
- **内容**: `used_form`が常に`key_phrase`と一致する(100%重複)ことを確認したが、実際に分ける必要が生じるまでリファクタリングしない
- **状態**: `DECIDED`(整理しないこと自体が決定事項)
- **採用理由**: ユーザー指示。「不要な分岐ロジックを増やさない」
- **根拠レポート**: ER-003-KP-02-R1承認時のユーザー発言
- **commit**: `5a94db0`(承認と同時のcommit)
- **影響するCURRENT_SPEC項目**: Key Phrase > `used_form`/`key_phrase`の関係。[OPEN_ITEMS.md](OPEN_ITEMS.md)にも技術的負債として記載

## strict ASR検証(部分一致+文字数上限)の追加

- **日付**: 2026-08-08
- **内容**: 短文ナレーションのASR検証を、部分一致だけでなく「ASR文字数が期待文字数を大きく超えていないか」も確認するよう強化
- **状態**: `DECIDED`
- **採用理由**: A02 meaning_5で、部分一致のみの検証が28.8秒のhallucination音声(目的の文言+26秒以上の無関係な創作内容)を誤って合格判定した
- **根拠レポート**: ER-003-REPRO-01-MAIN実行報告
- **commit**: `a13d97c`, `a70736d`
- **影響するCURRENT_SPEC項目**: Full Story > strict ASR検証

## minimal instruction fallbackを英語Key Phrase Componentへも一般化

- **日付**: 2026-08-08
- **内容**: 標準経路(`ENGLISH_STYLE_PREFIX`)が規定回数不合格の場合、最小限instructionへ自動フォールバックする仕組みを、短文ナレーションだけでなく英語Key Phrase Componentにも適用
- **状態**: `DECIDED`
- **採用理由**: A02のKey Phrase"opt out"が標準経路で6回とも無関係な内容を生成。フォールバックで1回で解決
- **根拠レポート**: ER-003-REPRO-01-MAIN実行報告
- **commit**: `a13d97c`
- **影響するCURRENT_SPEC項目**: Full Story > minimal instruction fallback

## Dynamics3を不使用、scalar RMS gainのみ採用

- **日付**: 2026-08-07(P9A時点で確立)
- **内容**: 音量調整にDynamics3(ダイナミックレンジ圧縮)を使わず、scalar gainのみで行う
- **状態**: `DECIDED`
- **採用理由**: コード内コメントに明記(理由の詳細な比較記録は未発見、[OPEN_ITEMS](OPEN_ITEMS.md)に記録漏れとして記載)
- **根拠レポート**: `er003_b1_p9a_audio.py`内コメント
- **commit**: `dcc6d8a`(P9A初版)
- **影響するCURRENT_SPEC項目**: Full Story > Dynamics処理

## 複数箇所編集は「後ろから前へ」の順序を徹底

- **日付**: 2026-08-07
- **内容**: 1つの音声ファイルへ複数箇所の時間軸編集を適用する場合、時系列で後ろにある編集から先に適用する
- **状態**: `DECIDED`
- **採用理由**: P7Cで5箇所の英語Key Phrase差し替えを1ループで同時処理した際、中間箇所の無音調整が既処理済み箇所のインデックスずれの影響を受けるバグが発生(目標0.40秒に対し実測0.145〜0.560秒)
- **根拠レポート**: [ER-003_PIPELINE_CROSS_CUTTING_RULES.md](ER-003_PIPELINE_CROSS_CUTTING_RULES.md) 2節
- **commit**: `b32c6e7`(バグ修正)
- **影響するCURRENT_SPEC項目**: Audio Assembly > 複数箇所編集の順序

## MFA単独では数字・日付境界を確定しない

- **日付**: 2026-08-07
- **内容**: MFAで境界を決めても、必ずASRまたは他の診断で妥当性を裏付ける
- **状態**: `DECIDED`
- **採用理由**: "England 1–2 Argentina"が実際には"England one, Argentina two"の語順で発話されており、書字通りの語順でMFAへ渡したため直前語の境界を誤認識(70.630秒→正しくは70.960秒)
- **根拠レポート**: ER-003-B1_HANDOFF.md、[ER-003_PIPELINE_CROSS_CUTTING_RULES.md](ER-003_PIPELINE_CROSS_CUTTING_RULES.md)
- **commit**: `d2aa9e6`(バグ修正)
- **影響するCURRENT_SPEC項目**: Audio Assembly > 境界検出、数字・日付境界

## ASR homophone ambiguityをhallucinationと区別し、2段階human reviewフローで扱う

- **日付**: 2026-08-09
- **内容**: TTS音声が正常でもASRが同音異義語を誤選択しstrict検証が機械的に不合格になり続ける事象を、hallucination(無関係な内容の生成)とは別の不具合分類として扱い、`PROVISIONALLY_ACCEPTED_REQUIRES_HUMAN_REVIEW`→ユーザー試聴→`ACCEPTED_AFTER_HUMAN_REVIEW`の2段階フローで確定する
- **状態**: `DECIDED`
- **採用理由**: ADD03 meaning_3「航行の自由」がASRに「高校の自由」と誤認識され続けたが、ユーザー試聴の結果TTS音声自体は正常と確定
- **比較した選択肢**: 無限retry / 機械的forced accept / human review flag
- **却下理由(無限retry)**: 同音異義語バイアスは系統的でretryでは解決しない
- **却下理由(機械的forced accept)**: 誤りである可能性を排除できない
- **根拠レポート**: [ER-003-B2-AUDIT-01_SPEC_AUDIT.md](ER-003-B2-AUDIT-01_SPEC_AUDIT.md)、ADD03 audio_validation_main.md
- **commit**: `1b62a20`(発見)、`c4a762c`(ユーザー試聴後の確定)
- **影響するCURRENT_SPEC項目**: QA / Human Review > ASR homophone ambiguity対応

## A02・ADD03の量産再現性判定: 量産候補として採用可能

- **日付**: 2026-08-09
- **内容**: A02・ADD03が2記事連続で、記事固有のハードコードを増やさずに初回通し候補がそのままユーザーOKに到達したことから、「量産候補として採用可能」と判定。ただし完全無人公開は不可、最終ユーザー試聴を必須ゲートとして維持
- **状態**: `DECIDED`
- **採用理由**: 2記事連続成功、発生した不具合(hallucination/ASR ambiguity)がいずれも安全に検出・処理できた
- **根拠レポート**: [ER-003-REPRO_BASELINE.md](ER-003-REPRO_BASELINE.md) ER-003-REPRO-FINAL章
- **commit**: `c4a762c`
- **影響するCURRENT_SPEC項目**: QA / Human Review > 量産再現性判定

## ER-002実験(A01・A02の初回音声)を破棄し、ER-003アーキテクチャへ全面移行

- **日付**: 2026-07-19(ユーザー評価)〜2026-08-06(ER-003開始)
- **内容**: ER-002-S3で生成・試聴したA01(サッカー)・A02(SNS)の初回音声を、編集的に不十分と判断して破棄。改訂版(v1.1B)も再度拒否。Natural English Source→CEFR B1/B2/A2独立生成というER-003の新アーキテクチャへ全面移行
- **状態**: `DECIDED`(移行済み)、旧成果物は`HISTORICAL`
- **採用理由**: ユーザー評価で「台本は事実の羅列に近く、切り口が弱い」(A01)、「記事選定と台本内容の両方が不十分」(A02)と判定
- **却下理由**: 編集的失敗(`COMMON_SCRIPT_EDITORIAL_FAILURE`/`TOPIC_SELECTION_AND_SCRIPT_EDITORIAL_FAILURE`)
- **根拠レポート**: `er002_output/A01/user_evaluation.json`、[ER-003-B2-AUDIT-01_SPEC_AUDIT.md](ER-003-B2-AUDIT-01_SPEC_AUDIT.md)
- **commit**: `ed0f786`(ER-002側記録)、ER-003開始は`fcb1387`等
- **影響するCURRENT_SPEC項目**: (アーキテクチャ全体の前提)

## ER-003-A2-STRUCT-02: A2超一般語5語制限を不採用

- **日付**: 2026-08-09
- **内容**: ER-003-A2-03で試行した「A2超一般語を記事全体で最大5語に制限する」仕様を不採用とする。今後のA2生成prompt・QAの必須条件にしない
- **状態**: `REJECTED`
- **採用理由**: (該当なし、不採用)
- **比較した選択肢**: 数値上限を維持し反復修正機構を新設する vs 数値上限を撤廃し「平易な語を優先する」原則のみ残す
- **却下理由**: **A2-03で実測が目標(5語)を達成できなかったこと自体を主理由とはしない。** (1) 正式CEFR-A2語彙リストがリポジトリに存在せず、LLM semantic QAでは`ahead`/`reach`/`lead`/`still`/`move`/`deal`/`market`等までA2超と判定されるなど判定基準が安定しない(=厳密なCEFR語彙判定基盤がない)、(2) 厳密な5語制限の達成には生成→語彙QA→再生成という反復処理が必要になり量産フローが複雑化する(=運用が複雑になる)、(3) ルールの複雑化に対してユーザーが感じるリスニング難易度改善効果が十分確認できなかった。この3点を理由に、今回は数値上限の導入を断念する
- **根拠レポート**: [ER-003-A2-03_LISTENING_SIMPLIFICATION.md](ER-003-A2-03_LISTENING_SIMPLIFICATION.md) 8節、ER-003-A2-STRUCT-02(ユーザー指示による理由の明確化、2026-08-09)
- **影響するCURRENT_SPEC項目**: A2言語仕様(→[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)、数値上限なしの「平易な語を優先」原則のみ残す)

## ER-003-A2-STRUCT-02: 抽象語→具体的行動表現への一律変換を不採用

- **日付**: 2026-08-09
- **内容**: ER-003-A2-03で試行した「抽象的な表現を『誰が何をしたか』という具体的行動表現へ優先的に変換する」一般ルールを不採用とする
- **状態**: `REJECTED_AS_GENERAL_RULE`
- **採用理由**: (該当なし、一般ルールとしては不採用。個別の編集判断としては引き続き有効な手段)
- **比較した選択肢**: 一律の変換ルールとして必須化する vs 記事・文脈ごとの通常の編集判断に委ねる
- **却下理由**: 具体化によって理解しやすくなるケースは実際に存在したが、抽象概念を無理に具体的行動へ置換すると元の意味関係が見えにくくなったり説明がかえって長くなったりするケースもあり、「抽象表現は悪い/具体表現は良い」という一方向ルールは成立しないと判断
- **根拠レポート**: [ER-003-A2-03_LISTENING_SIMPLIFICATION.md](ER-003-A2-03_LISTENING_SIMPLIFICATION.md) 10節
- **影響するCURRENT_SPEC項目**: A2言語仕様(→[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)、一般ルールとしては採用しない)

## ER-003-A2-STRUCT-02: 固有名詞密度低減を不採用

- **日付**: 2026-08-09
- **内容**: ER-003-A2-03で試行した「固有名詞のtoken数・密度を意図的に下げる」一般ルールを不採用とする
- **状態**: `REJECTED`
- **採用理由**: (該当なし、不採用)
- **比較した選択肢**: 密度目標・数量目標を設けて維持する vs 目標を撤廃し通常の編集判断(記事理解上の必要性)に委ねる
- **却下理由**: A01では固有名詞トークン数が減った(49→40)一方、ADD03ではTrumpを明示的主語にした結果増加した(18→24)。固有名詞削減を目的化すると、「誰が何をしたかを明確にする」「referentを明確にする」「spoken-firstにする」という別の分かりやすさ要求と競合することが判明。このための追加ルール・計測の維持は量産フローを不必要に複雑化する
- **根拠レポート**: [ER-003-A2-03_LISTENING_SIMPLIFICATION.md](ER-003-A2-03_LISTENING_SIMPLIFICATION.md) 14節
- **影響するCURRENT_SPEC項目**: A2言語仕様(→[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)、密度目標は設けない)

## ER-003-A2-STRUCT-02: Spoken-firstをA2の継続仕様として採用

- **日付**: 2026-08-09
- **内容**: ER-003-A2-03で試行した「読んだときの洗練より、一度聞いたときに意味を取りやすい自然な英語を優先する」spoken-first方針を、A2原稿生成の継続仕様として採用する。主語を早く出す、動詞を早く出す、長い前置詞句・名詞句を文頭に置きすぎない、文末まで聞かないと意味が確定しない構造を避ける、を運用原則とする。厳格なsyntax validatorにはせず、自然さを損なう機械的書き換えは行わない(style / generation principleとして運用)
- **状態**: `ADOPTED`
- **採用理由**: 音声だけでニュースを理解する際の負荷軽減に資すると判断
- **比較した選択肢**: 厳格な文法チェッカーとして実装する vs style原則としてprompt指示にとどめる
- **却下理由(厳格チェッカー化)**: 自然な英語らしさを損なうリスクがあるため、機械的な検証・強制は行わない
- **根拠レポート**: [ER-003-A2-03_LISTENING_SIMPLIFICATION.md](ER-003-A2-03_LISTENING_SIMPLIFICATION.md) 11節
- **影響するCURRENT_SPEC項目**: A2言語仕様(→[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)、「維持」項目としてSpoken-firstを明記)

## ER-003-A2-STRUCT-02: 1文1数字ルールを維持、日付は1つの数字情報として扱う方向で整理

- **日付**: 2026-08-09
- **内容**: ER-003-A2-03で導入した「1文1数字」原則(年齢範囲・スコア・時間帯は例外)は撤回せず、A2 Prototype仕様として維持する。加えて、"July 13, 2026"のような「月+日+年」の日付表記は、年齢範囲・スコア・時間帯と同様に**1つの日付情報として扱う**方向で整理する
- **状態**: `DECIDED`(原則の整理のみ。checker実装は今回見送り)
- **採用理由**: 日付を1つの意味単位として扱うことは、既存の例外(年齢範囲・スコア・時間帯)と同じ考え方に合致する
- **比較した選択肢**: 例外リストへ正式に追加しchecker実装も更新する vs 原則の解釈のみ整理し実装は見送る
- **却下理由(即時のchecker実装)**: この整理のためだけに数字QAロジックの改修を今回は行わない(小規模な変更ではあるが、他の優先事項がある中で今回のスコープには含めない)
- **根拠レポート**: [ER-003-A2-03_LISTENING_SIMPLIFICATION.md](ER-003-A2-03_LISTENING_SIMPLIFICATION.md) 9節、[OPEN_ITEMS.md](OPEN_ITEMS.md) OPEN-18
- **影響するCURRENT_SPEC項目**: A2言語仕様(→[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)、1文1数字の例外定義)

## ER-003-A2-SPEC-FREEZE-01: A2言語・構造仕様をPROTOTYPEからDECIDEDへ昇格

- **日付**: 2026-08-12
- **内容**: ER-003-A2-01〜03・ER-003-A2-STRUCT-02〜05で検証してきたA2の
  言語方針(Natural English Source独立生成、総語数を削らない、平均文長
  11語以下・最長18語以下、1文1メッセージ、SVO中心・関係詞節/分詞構文/
  複雑な受動態を避ける、Spoken-first、Simple AND Natural要件)と構造仕様
  (11パート構造、Comment1〜4の役割、Full Story分割優先順位、In One Line
  =中心1文+補足2文)を、`PROTOTYPE`から`DECIDED`へ正式に昇格した
- **状態**: `DECIDED`
- **採用理由**: ER-003-A2-AUDIO-AB-01でA02の完成候補(A/B比較)をユーザーが
  試聴し、全体としてOKと判断。個別に検証してきた言語・構造方針が音声
  完成候補として統合的に成立することを確認できた
- **比較した選択肢**: 個別reportに仕様を分散させたまま運用を続ける vs
  CURRENT_SPECへ正式反映し一次参照先を一本化する
- **却下理由(分散運用継続)**: 過去に決定事項がhandoffや個別reportへ
  埋もれ、Project Managementの機能不全を招いた教訓があるため
- **根拠レポート**: [ER-003-A2-SPEC-FREEZE-01_REPORT.md](ER-003-A2-SPEC-FREEZE-01_REPORT.md)
- **影響するCURRENT_SPEC項目**: CEFR(A2/B1/B2比較)、CEFR-A2 構造・音声仕様

## ER-003-A2-SPEC-FREEZE-01: A2英語ナレーション速度を約135 WPM目安として採用

- **日付**: 2026-08-12
- **内容**: A2の英語ニュースナレーション(Full Story/Points/In One Line)
  の速度目安として約135 WPMを採用する。hard constraintではなく目安とし、
  自然なprosodyを優先する。B1/B2は現行速度を維持し、新たなWPM targetは
  設けない
- **状態**: `DECIDED`(目安として)
- **採用理由**: ER-003-A2-AUDIO-AB-01でA02の速度A版(指定なし、平均約
  155 WPM)/B版(約135 WPM目安)を生成しユーザーが試聴、B版を採用可と判断
- **比較した選択肢**: 速度指定なし(A版) vs 約135 WPM目安(B版)。倍率
  固定案(現行速度の0.9倍)も検討したが、B1自体のWPMが記事により139〜143と
  幅があるため倍率ではなく絶対値の目安として採用
- **却下理由(倍率固定・0.9x)**: 記事構成差の影響を受けやすく、絶対値
  target(約135)の方が運用しやすいと判断
- **根拠レポート**: [ER-003-A2-AUDIO-AB-01_REPORT.md](ER-003-A2-AUDIO-AB-01_REPORT.md)
- **commit**: `e0e9a8d`
- **影響するCURRENT_SPEC項目**: CEFR-A2 構造・音声仕様 > A2英語ナレーション速度、B1/B2音声速度

## Cross-level: Preview原則をA2/B1/B2共通仕様として採用

- **日付**: 2026-08-12(原則試作はER-003-CROSSLEVEL-AUDIO-01、2026-08-09)
- **内容**: Previewはニュース全体のテーマ・問題意識・聞く価値・問いを
  示すことに限定し、後続本文の具体的な答え・詳細な数字・重要な転換点や
  結論を先出ししない、という原則をA2固有ではなくA2/B1/B2共通仕様として
  正式採用する
- **状態**: `DECIDED`
- **採用理由**: A01/A02/ADD03の3記事でこの原則に沿ってPreviewを再設計し、
  Comment1/2との情報重複解消を確認。ユーザーがA/B比較・3記事分の試聴を
  経て方向性を承認
- **根拠レポート**: [ER-003-CROSSLEVEL-AUDIO-01_REPORT.md](ER-003-CROSSLEVEL-AUDIO-01_REPORT.md)、[ER-003-CROSSLEVEL-AUDIO-02_REPORT.md](ER-003-CROSSLEVEL-AUDIO-02_REPORT.md)
- **影響するCURRENT_SPEC項目**: Cross-level仕様 > Preview原則
- **注意**: 既存B1/B2完成音声のPreviewは今回遡って差し替えない。今後の新規生成時から適用する

## Cross-level: Key Phrase発音品質の3条件をA2/B1/B2共通仕様として採用

- **日付**: 2026-08-12
- **内容**: Key Phraseの発音品質を(1) Meaning/contextual prosody、
  (2) Phoneme integrity(語末音素保持)、(3) Phrase grouping(単語ごとに
  分断しない)の3条件を同時に満たすものと定義し、A2/B1/B2共通の品質原則
  として採用する。個別単語への場当たり的パッチではなく、この共通原則で
  生成する
- **状態**: `DECIDED`
- **採用理由**: "Come on"/"Go ahead"/"Brent crude oil"で3条件を同時に
  満たす統合instructionを試作し、A02のKey Phrase 5件(personalized feedは
  既承認版を維持)へ適用。ユーザーがA/B完成候補内で試聴し承認
- **比較した選択肢**: 語末音素対策(segmental accuracy)のみを品質基準と
  する現状維持 vs 意味prosody・phrase一体感を含めた3条件へ拡張
- **却下理由(現状維持)**: 語末音素が正しくても、意味に合わない
  イントネーション(例: "Go ahead"が許可の意味に聞こえる)は別の問題として
  残ることが判明したため
- **根拠レポート**: [ER-003-CROSSLEVEL-AUDIO-04_REPORT.md](ER-003-CROSSLEVEL-AUDIO-04_REPORT.md)、[ER-003-A2-AUDIO-AB-01_REPORT.md](ER-003-A2-AUDIO-AB-01_REPORT.md)
- **commit**: `c061ae9`, `e0e9a8d`
- **影響するCURRENT_SPEC項目**: Cross-level仕様 > Key Phrase発音品質(3条件)

## Cross-level: 英語見出しは見出しテキストを実際にTTS inputへ含める方式を採用

- **日付**: 2026-08-12
- **内容**: Point One/Point Two/In One Line等の英語見出しは、見出し
  文字列そのものをTTS inputへ渡して発話させる。見出しテキストを含めず
  instructionだけで「見出しを言うように」指示する方式は使用しない
- **状態**: `DECIDED`
- **採用理由**: ADD03のIn One Lineで、見出しテキストを本文に含めずに
  生成した結果、モデルが指示に反応して見出しを不安定に(日本語風に
  聞こえる形で)発話する事象が発生。見出しテキストを実際に含める方式
  (Point One/Twoで既に問題が起きていなかった方式と同一)へ統一したところ、
  3回中3回で安定した正しい発話を確認
- **比較した選択肢**: 見出しを発話しないよう指示で抑制する(誤った初期
  対応、ER-003-CROSSLEVEL-AUDIO-03で一度採用したが後に訂正) vs 見出し
  テキストを実際に含める(最終採用)
- **却下理由(発話抑制)**: In One Lineは本来読み上げるべき見出しであり、
  「発話させない」ことは要件に反する誤った対応だった
- **根拠レポート**: [ER-003-CROSSLEVEL-AUDIO-04_REPORT.md](ER-003-CROSSLEVEL-AUDIO-04_REPORT.md)
- **影響するCURRENT_SPEC項目**: CEFR-A2構造・音声仕様 > In One Line見出しのTTS、Cross-level仕様 > 英語見出しのTTS方式

## Cross-level: Pause値(0.7秒/0.8秒)をA2/B1/B2共通仕様として採用

- **日付**: 2026-08-12
- **内容**: 「ポイント解説」→Preview間を0.7秒、Point One→Point Two間を
  0.8秒、In One Line→Outro間を0.8秒とする。A2 Comment前後の1.0秒(英→日)・
  0.8秒(日→英)は無変更で維持する
- **状態**: `DECIDED`
- **採用理由**: A02のA/B完成候補でユーザーが試聴し承認
- **根拠レポート**: [ER-003-A2-AUDIO-AB-01_REPORT.md](ER-003-A2-AUDIO-AB-01_REPORT.md)
- **commit**: `e0e9a8d`
- **影響するCURRENT_SPEC項目**: Cross-level仕様 > ポーズ各項目
- **注意**: 現状は記事ごとの組立スクリプトへ個別にハードコードされており、共通定数への一元化はまだ行っていない([OPEN_ITEMS.md](OPEN_ITEMS.md)参照)

## Cross-level: Outro音量の心理音響ベース減衰方針を採用

- **日付**: 2026-08-12
- **内容**: Outro音量を、単純な振幅比の変更ではなく心理音響上の知覚音量
  ベースの計算(10dBの変化で知覚音量が倍/半分になるという経験則)で
  段階的に減衰する方針を、A2/B1/B2共通のmix ruleとして採用する
- **状態**: `DECIDED`(方針として)
- **採用理由**: A02のA/B完成候補でユーザーが試聴し承認
- **根拠レポート**: [ER-003-CROSSLEVEL-AUDIO-01_REPORT.md](ER-003-CROSSLEVEL-AUDIO-01_REPORT.md)〜[04](ER-003-CROSSLEVEL-AUDIO-04_REPORT.md)、[ER-003-A2-AUDIO-AB-01_REPORT.md](ER-003-A2-AUDIO-AB-01_REPORT.md)
- **commit**: `e0e9a8d`
- **影響するCURRENT_SPEC項目**: Cross-level仕様 > Outro音量
- **注意**: 既存B1/B2完成音声のOutroは今回遡って差し替えない

## A01 script修正: "The referee then added more time." → "The game went into added time."

- **日付**: 2026-08-12
- **内容**: A01のFull Story Part2にある"The referee then added more
  time."を、サッカー放送で標準的に使われる用語"added time"を用いた
  "The game went into added time."へ修正する
- **状態**: `DECIDED / APPLIED`(2026-08-12、ER-003-A2-SCRIPT-FINAL-01で
  最終台本へ反映済み。音声への反映は次回A01 assemble時)
- **採用理由**: "added more time"は理解可能だが放送英語としてやや
  一般的すぎる。代替候補"extra time"はサッカーでは「延長戦」という
  別概念を指すため不採用、"added time"はロスタイムを指す正確な標準
  用語のため採用
- **比較した選択肢**: 現状維持 / "The referee added extra time." / "The game went into added time."
- **却下理由("extra time")**: 意味が変わってしまうリスク(延長戦との混同)
- **根拠レポート**: [ER-003-CROSSLEVEL-AUDIO-03_REPORT.md](ER-003-CROSSLEVEL-AUDIO-03_REPORT.md) 9節、[ER-003-A2-SCRIPT-FINAL-01_REPORT.md](ER-003-A2-SCRIPT-FINAL-01_REPORT.md)
- **影響するCURRENT_SPEC項目**: (個別記事の本文修正、CURRENT_SPEC仕様そのものへの影響なし)

## A01 script修正: "Rogers sent the ball across the front of goal." → "Rogers crossed the ball into the box."

- **日付**: 2026-08-12
- **内容**: A01のFull Story Part1にある直訳的で不自然な表現を、実際の
  サッカー実況で標準的に使われる"cross the ball into the box"を用いた
  表現へ修正する
- **状態**: `DECIDED / APPLIED`(2026-08-12、ER-003-A2-SCRIPT-FINAL-01で
  最終台本へ反映済み。音声への反映は次回A01 assemble時)
- **採用理由**: 事実関係(誰が・どこへ・どうボールを送ったか)は変えず、
  放送英語として自然な言い回しへ改善。A2文長制約(18語以下)にも適合
- **根拠レポート**: [ER-003-CROSSLEVEL-AUDIO-03_REPORT.md](ER-003-CROSSLEVEL-AUDIO-03_REPORT.md) 11節、[ER-003-A2-SCRIPT-FINAL-01_REPORT.md](ER-003-A2-SCRIPT-FINAL-01_REPORT.md)
- **影響するCURRENT_SPEC項目**: (個別記事の本文修正、CURRENT_SPEC仕様そのものへの影響なし)

## A01 script修正: "Messi sent the ball across goal from the right." → "Messi crossed the ball from the right."

- **日付**: 2026-08-12
- **内容**: 上記と同種の不自然な表現を、同じく"cross"を用いた自然な
  表現へ修正する
- **状態**: `DECIDED / APPLIED`(2026-08-12、ER-003-A2-SCRIPT-FINAL-01で
  最終台本へ反映済み。音声への反映は次回A01 assemble時)
- **採用理由**: 上記と同様。"from the right"というPoint Oneでの記述
  ("He helped Lautaro with a good ball from the right.")との整合性も
  維持される
- **根拠レポート**: [ER-003-CROSSLEVEL-AUDIO-03_REPORT.md](ER-003-CROSSLEVEL-AUDIO-03_REPORT.md) 11節、[ER-003-A2-SCRIPT-FINAL-01_REPORT.md](ER-003-A2-SCRIPT-FINAL-01_REPORT.md)
- **影響するCURRENT_SPEC項目**: (個別記事の本文修正、CURRENT_SPEC仕様そのものへの影響なし)

## A02 script修正: "apps under the plan would not open at first" → "apps under the plan would be switched off by default"

- **日付**: 2026-08-12
- **内容**: A02のFull Story Part1にある、誤読リスク(「起動できない」と
  誤解される恐れ)のある表現を、"switched off by default"(初期設定で
  オフになっている)へ修正する
- **状態**: `DECIDED / APPLIED`(2026-08-12、ER-003-A2-SCRIPT-FINAL-01で
  最終台本へ反映済み。音声への反映は次回A02 assemble時)
- **採用理由**: 意味誤読リスクの解消。Natural English Source
  (`er003_output/a2_p1_r3/A02/master_en_natural_source_approved.md`)
  の該当箇所"covered apps would be unavailable by default"と照合し、
  「対象アプリはdefaultで利用不可(オフ)になる」という原意と一致する
  ことを確認した上で採用(意味を変更する修正ではなく、原意を正確に
  反映する修正と判定)
- **根拠レポート**: [ER-003-CROSSLEVEL-AUDIO-03_REPORT.md](ER-003-CROSSLEVEL-AUDIO-03_REPORT.md) 11節、[ER-003-A2-SCRIPT-FINAL-01_REPORT.md](ER-003-A2-SCRIPT-FINAL-01_REPORT.md)
- **影響するCURRENT_SPEC項目**: (個別記事の本文修正、CURRENT_SPEC仕様そのものへの影響なし)

## ADD03 script修正: Brent原油価格段落の時系列flashback構造を解消

- **日付**: 2026-08-12
- **内容**: ADD03のFull Story Part2にある、7/14の出来事→7/13への回想→
  7/14の出来事、という時系列が前後する構成を、7/13→7/14の実時系列順
  へ並べ替える。あわせて重複していた「価格が下落した」旨の記述
  (旧文中2箇所)を1箇所へ統合し、"on July 13"/"July 14"という明示的な
  日付参照を追加した
- **状態**: `DECIDED / APPLIED`(2026-08-12、ER-003-A2-SCRIPT-FINAL-01で
  最終台本へ反映済み。音声への反映は次回ADD03 assemble時)
- **採用理由**: A2レベルの聞き手にとって時系列の前後が理解負荷になる
  ため。新しい事実は追加していない(既存文の並べ替え・日付明示・
  重複表現の統合のみ)。Natural English Source
  (`er003_output/a2_p1_r3/ADD03/master_en_natural_source_approved.md`)
  との整合を確認済み(「7/13に急騰・$87超のintraday高値」「fee撤回後に
  高値から反落」「7/14終値$84.73・前日比+2%・月間最高値」という
  事実関係は維持)
- **根拠レポート**: [ER-003-CROSSLEVEL-AUDIO-03_REPORT.md](ER-003-CROSSLEVEL-AUDIO-03_REPORT.md) 11節、[ER-003-A2-SCRIPT-FINAL-01_REPORT.md](ER-003-A2-SCRIPT-FINAL-01_REPORT.md)
- **影響するCURRENT_SPEC項目**: (個別記事の本文修正、CURRENT_SPEC仕様そのものへの影響なし)

## ER-003-SPOKEN-FIRST-03: Point Balance(Point One/TwoはA02で40〜50語が機能。全ジャンル一律ルール化はしない)

- **日付**: 2026-08-13
- **内容**: SPOKEN-FIRST-02のA02で、Point One(144語)が本編
  (166語)とほぼ同等の長さになり、「本文とは別の切り口を短く示す」
  というPointの役割から外れ、実質的に"第二の本編"になっていた問題を
  是正する設計判断を検証・確定する。判断の核心は「PointがK-1-1/K-1-2
  の役割(本編と同程度の情報量を持たせない、本編の再説明ではなく
  別の切り口・示唆を短く示す)を果たしているか」という**役割・比重
  基準**であり、固定語数ルールではない
- **状態**: `VALIDATED(A02単独検証) / NOT_YET_GENERALIZED`
  (ユーザー・レビュー承認済み。A01・ADD03等への横展開、Production
  仕様(CURRENT_SPEC.md)への組み込みはまだ行っていない)
- **採用理由**: A02のPoint One/Twoを、目標30〜60語(許容25〜70語)の
  範囲でVerified Fact Ledgerの範囲内のみを使い圧縮した結果、
  Point One=47語・Point Two=44語に自然収束し、核心メッセージを
  保持したまま本編とのバランスが改善した(Fact Checker `PASS`、
  Ledger Deviation `LEDGER_COMPLIANT`、技術的再試行0回)。本編
  (166語)・In One Line(28語)は完全無変更で、Point削減の埋め合わせ
  としての本編延長も発生しなかった
- **比較した選択肢**: (該当なし。単一のPoint圧縮方式のみ試行し
  best-of選択は行っていない)
- **却下理由**: (該当なし)
- **今回確定していない事項(誤読防止のため明記)**:
  「各Pointを必ず40〜50語にする」という固定ルールにはしない。
  40〜50語という実測値はA02(1記事1ジャンル)での目標範囲内収束
  結果にすぎず、他ジャンルへ機械的に適用してよいという意味ではない。
  A01のように元々Point One=37語・Point Two=60語で「第二の本編」化
  が起きていない記事まで機械的に圧縮する対象ではない
- **根拠レポート**: [ER-003-SPOKEN-FIRST-03_REPORT.md](ER-003-SPOKEN-FIRST-03_REPORT.md)(特にK節「検証済みの設計判断」)、[ER-003-SPOKEN-FIRST-02_REPORT.md](ER-003-SPOKEN-FIRST-02_REPORT.md)(問題発見の経緯)
- **commit**: `a1fcc2c`(生成・報告)、(本記録commitは送付メッセージ参照)
- **影響するCURRENT_SPEC項目**: (個別記事A02の実験的圧縮版のみ。
  CURRENT_SPEC.mdへの反映は未実施。次回横展開検証(A01・ADD03)の
  結果を踏まえて判断する→[OPEN_ITEMS.md](OPEN_ITEMS.md)へ追加要否は
  次段階で検討)

## [サービス・生成仕様] ER-003-B1-NOVEL-AUDIO-01系: B1をSupport-based Natural Englishへ再設計

- **日付**: 2026-08-14頃(複数タスクにまたがる、ER-003-B1-A2-SPEC-FREEZE-01で正式反映)
- **内容**: B1のNews本文(Full Story/Point One/Two/In One Line)専用の簡略化rewriteを行う旧来の設計をやめ、B2相当のNatural English本文を共通で使い、B1固有の体験はSupport(Preview/Comment1-4を平易な英語で提供)と役割設計だけで作る方式へ移行した。あわせてVoice role(Charon=Navigator/Support、Aoede=News Content)を再配置し、A2由来の日本語spoken text(Title/Preview/Comment等)をB1から除去し英語化した
- **状態**: `SUPERSEDED`(2026-08-17、`ER-003-B1-B2-SCOPE-FIX-01` Decision Aにより後継。B1のNews本文はB2と共通化せず、Verified Fact LedgerからB1専用Writerで独立生成する方式へ移行済み。本Decisionは当時の設計判断の記録として保持)
- **採用理由**: B1専用の簡略化英文を別途生成すると、A2との差別化が「難易度の異なる2つのNews本文」という設計になり、Ledgerに忠実な単一のNatural English本文という一貫性が失われる。Support(言語・役割)だけで難易度体験を作る方が、記事本文の事実表現を1つに保ちやすい
- **比較した選択肢**: B1専用の簡略化本文を維持する vs News本文をB2と共通化しSupportだけで差別化する
- **却下理由(B1専用簡略化本文の維持)**: 本文を2種類(A2向け簡略・B1向け簡略)+Support言語という組み合わせが増え、Fact Ledgerとの整合確認箇所が増える。ユーザー判断によりSupport-based設計を採用
- **根拠レポート**: ER-003-B1-NOVEL-AUDIO-01系タスク一式(Support English化・Voice role再配置・日本語残存要素の英語化)
- **影響するCURRENT_SPEC項目**: B1(Support-based Natural English)節一式

## [サービス・生成仕様] ER-003-A2-B1-N3-01: B1-B Direct Generationを採用し、B2の別段階生成を廃止

- **日付**: 2026-08-16
- **内容**: B1-A(B2から派生させる方式)とB1-B(Verified Fact Ledgerから1回のWriter呼び出しで直接Natural English本文を生成する方式)を4版比較した上で、B1-B Direct Generationを採用した。以後、B1/A2とも同一のVerified Fact Ledgerから、それぞれ独立したWriter呼び出しで生成し、B2を別段階として生成するステップはN3以降の新規記事では行わない
- **状態**: `DECIDED`
- **採用理由**: B1-B Direct Generationは、B2を経由する方式より生成段階が少なく、Fact Ledgerとの整合確認箇所も1本化できる。4版diagnostic比較でB1-Bが採用可能な品質と判定された
- **比較した選択肢**: B1-A(B2派生) vs B1-B(Ledgerから直接生成)
- **却下理由(B1-A)**: B2という中間生成物を介するぶん、生成・QA工程が増える
- **根拠レポート**: B1-A/B1-B新規生成・4版diagnostic metrics測定・4版比較Artifact作成の各タスク完了報告
- **影響するCURRENT_SPEC項目**: B1(Support-based Natural English) > News本文の生成方式

## [サービス・生成仕様] B1 Key Phraseの提示順序をEnglish→Japanese→Englishに確定(英英説明は不採用)

- **日付**: 2026-08-14頃
- **内容**: B1のKey Phraseも、A2と同じEnglish→Japanese→English(反復)の提示順序を正式仕様とする。英英説明(English-only definition)方式は採用しない
- **状態**: `DECIDED`
- **採用理由**: 難語の英英説明はそれ自体が新しい理解負荷になり、Support-based B1の「本文理解のためのListening Navigation」という目的に反する。section長文化も避けられる
- **比較した選択肢**: English→Japanese→English(反復) vs English-onlyの説明的Key Phrase提示
- **却下理由(English-only説明)**: 意味理解の確実性より難語説明の負荷が優先されてしまう
- **根拠レポート**: ER-003-B1-NOVEL-AUDIO-01系
- **影響するCURRENT_SPEC項目**: B1 Key Phrase節

## [サービス・生成仕様] ER-003-POINT-NOTIFICATION-01: Point One/Two専用Notificationと無言のPoint番号ラベル

- **日付**: 2026-08-14頃
- **内容**: Point One/Twoの直前に専用のNotification音(既存のKey Phrase/Full Story Notificationとは別音源)を挿入し、Point番号("Point One."等)は音声で明言しない設計を採用。あわせてNotification直後に追加の余白を入れない(音源自体の余韻をそのまま使う)方式へ修正した
- **状態**: `DECIDED`
- **採用理由**: 構造(Notification)と意味(semantic heading)を分離することで、機械的な番号読み上げより自然な聞こえ方になる
- **根拠レポート**: ER-003-POINT-NOTIFICATION-01完了報告、追加調整(Point Notification直後のpause除去)
- **影響するCURRENT_SPEC項目**: Cross-level仕様 > Point Notification、Point semantic heading

## [サービス・生成仕様] Point semantic headingは記事生成プロンプトの`###`見出しをそのまま使う

- **日付**: 2026-08-14頃(A2)、B1はVoice再配置と同時期
- **内容**: Point One/Twoの本文直前に置くsemantic headingは、追加のLLM呼び出しで別途生成せず、記事生成プロンプトが既に返している`###`見出し(装飾記号のみ`clean_heading()`で除去)をそのまま使う
- **状態**: `DECIDED`
- **採用理由**: 記事生成の時点で既に2つの`###`見出しを要求しているため、これがそのままsemantic headingとして使える。追加呼び出し・追加コストが不要
- **根拠レポート**: ER-003-A2-POINT-HEADING-AUDIO-01完了報告(発見の経緯)
- **影響するCURRENT_SPEC項目**: Cross-level仕様 > Point semantic heading

## [サービス・生成仕様] ER-003-A2-B1-N3-01: Point Balanceの目標範囲(30-60語/許容25-70語)を3ジャンルで検証、hard capへは昇格させない

- **日付**: 2026-08-17
- **内容**: ER-003-SPOKEN-FIRST-03でA02単独検証にとどまっていたPoint Balanceの目標範囲(目標30〜60語、許容25〜70語)を、Sports(Hanshin)・Health・Household の3ジャンルへ横展開した。3ジャンルとも、Fact Ledgerの範囲内でPointを圧縮した結果、目標範囲内に自然収束することを確認した
- **状態**: `VALIDATED across Sports/Health/Household`(hard capへの変更はしない)
- **採用理由**: 3ジャンルでの再現性が確認できたことで、単一記事の偶然の結果ではないという確信度が上がった。ただし、目標範囲を機械的なhard capにすると、記事によって自然に収まる長さが異なる可能性を無視することになるため、診断的な目安の位置づけを維持する
- **比較した選択肢**: 診断的目安のまま維持する vs 機械的なhard capへ格上げする
- **却下理由(hard cap化)**: 3ジャンルでの成功は「範囲内に収まりやすい」ことを示すが、「収まらなければならない」ことまでは示さない。ユーザー指示により、勝手にhard ruleへ変更しないことを明示的に維持
- **根拠レポート**: ER-003-A2-B1-N3-01完了報告(cross-level分析節)
- **影響するCURRENT_SPEC項目**: Cross-level仕様 > Point Balance(長さの扱い)

## [サービス・生成仕様] ER-003-A2-B1-N3-01: Spoken-first Number TreatmentをA2/B1共通仕様として正式化

- **日付**: 2026-08-17
- **内容**: Fact Ledgerはexact factを保持しつつ、spoken narrative側では精度自体に意味のない数字を丸め・概数化・方向化してよいという方針を、Importance(ANCHOR/SUPPORTING/DISPENSABLE)・Exactness(EXACT_REQUIRED/APPROXIMATE_OK/DIRECTION_ONLY)という2軸の分類として明文化し、A2/B1共通仕様として採用した
- **状態**: `DECIDED`
- **採用理由**: 過度な小数精度の読み上げはListening easeを損なう。一方でスコア・日付・研究結果等、精度自体が意味を持つ数字までは丸めない、という線引きを明示する必要があった
- **根拠レポート**: ER-003-A2-B1-N3-01完了報告 §14
- **影響するCURRENT_SPEC項目**: Cross-level仕様 > Spoken-first Number Treatment

## [サービス・生成仕様] ER-003-A2-B1-N3-01: Fact Safety(Verified Fact Ledger→Fact Checker→Ledger Deviation Check)をA2/B1共通標準として正式化

- **日付**: 2026-08-17
- **内容**: 記事ごとに1つのVerified Fact Ledgerを作成し、A2/B1双方がそこから生成される。生成後は独立Fact Checker(web検索付き)とLedger Deviation Checkの2段QAを標準として実施する
- **状態**: `DECIDED`
- **採用理由**: A2/B1で個別に取材・Ledger作成すると、同じ記事の中でA2とB1が異なる事実関係を語るリスクが生じる。単一Ledger共有によりこれを防ぐ
- **根拠レポート**: ER-003-A2-B1-N3-01完了報告
- **影響するCURRENT_SPEC項目**: Cross-level仕様 > Fact Safety(共通)

## [サービス・生成仕様] ER-003-A2-B1-N3-01: 3ジャンル(Sports/Health/Household)横展開によるジャンル再現性の確認

- **日付**: 2026-08-17
- **内容**: 仮Fixしていた A2/B1 の一連の仕様(B1-B Direct Generation、Support scaffold、Point Notification、semantic heading、Voice分離、difficulty差)が、スポーツ(阪神-広島戦)・健康(観察研究記事)・生活実用(冷蔵庫のクリスパードロワー)という3つの異なるジャンルで、追加の構造変更なしに機能することを確認した
- **状態**: `DECIDED`(validation evidenceとして記録)
- **採用理由**: 単一ジャンル(SNS規制記事等)での検証だけでは、他ジャンルへの一般化可能性が担保されない。3ジャンル展開により、構造面の再現性を実証した
- **根拠レポート**: ER-003-A2-B1-N3-01完了報告
- **影響するCURRENT_SPEC項目**: Cross-level仕様 > ジャンル再現性

## [サービス・生成仕様] ER-003-N3-ROOT-FIX-01 / VERIFY-01: A2 Core Explanatory Logic Preservationを正式仕様へ採用

- **日付**: 2026-08-17
- **内容**: A2生成指示(`A2_KAI1_INSTRUCTION`)へ、「Verified Fact Ledgerが規定する中心的な説明ロジック・判断ルールを保持すること。語彙・文構造・具体例・提示順序は簡略化してよいが、Ledgerの仕組み・判断ルールを、Ledgerが支持しない/明示的に否定するショートカット・分類・因果関係・経験則へ置き換えないこと」という原則を追加した。ジャンル固有の具体例(Household記事のfruit/vegetable等)はこの一般原則のprompt本文へhard-codeしない
- **状態**: `DECIDED`
- **採用理由**: ER-003-N3-RCA-01のRoot Cause Analysisで、Household A2記事が「果物は低湿度、野菜は高湿度」という、Ledgerが明示的に否定するfruit/vegetable二分法を"基本ルール"として提示してしまっていたことが判明した。原因は、A2のCognitive Load Reductionが「正しいが複雑な判断軸」を「簡単だが別物の近似ルール」へ置換してしまうリスクであり、既存のFact Checkerは文単位の正確性は見ていても記事全体の判断軸までは見ていなかった(旧Household A2は実際にFact Checker PASSしていた)。この原因に対する発生源側の対策として、A2生成指示自体へ軸維持の原則を追加した
- **比較した選択肢**: (a) A2生成指示への原則追加(発生源対策)、(b) A2/B1間のクロスレベル一貫性チェックを新設(検出強化、追加LLM呼び出しが発生)、(c) 人間レビューゲートの追加(検出強化、量産と相性が悪い)
- **却下理由(b・c)**: 今回は「工程を重くせず発生源で再発率を下げる」ことを優先し、新しいLLM監査工程・人手工程は追加しないという方針のもとで、最小コストの(a)を採用した。(b)(c)は将来的な再発時の追加検討候補として保持する
- **検証根拠(ER-003-N3-ROOT-FIX-VERIFY-01)**: 既存Ledger・既存B1-Bを固定し、新しいA2_KAI1_INSTRUCTIONで3ジャンルを各1回だけ単発生成(best-of禁止)した結果:
  - Household: Core logic = **BETTER_PRESERVED**(旧版の"Fruit usually goes in low humidity..."という二分法を1回目の生成で回避し、ethylene放出/水分保持という仕組みを基本ルールとして提示。A2 ease・adult toneに副作用なし)
  - Health: Core logic = **SAME**(lifespan/healthspanの区別、observational study/非causationの説明を維持。副作用なし)
  - Hanshin: Core logic = **SAME**(元々シンプルなジャンルで、新しい段落による過剰な分析トーン化は見られず)
  - 3記事とも Fact Checker `PASS`、Ledger Deviation Check `LEDGER_COMPLIANT`(0件)。Writer/Fact Checker/Ledger Deviation Checkの呼び出し回数は変更前と同一(新しいLLM監査工程を追加していない)。**この`PASS`は、本Decisionの検証用にVerify-01で単発生成した`root_fix_01_regression/`配下のregressionテキストに対する結果である。本番article.md(特にHousehold A2)には未反映であり、本番article.mdのFact QA状態はこの`PASS`と同一ではない**(→[ARTIFACT_REGISTRY.md](ARTIFACT_REGISTRY.md)、2026-08-17 SoT Consistency Cleanupで区別を明記)
- **根拠レポート**: ER-003-N3-RCA-01完了報告、ER-003-N3-ROOT-FIX-01完了報告、ER-003-N3-ROOT-FIX-VERIFY-01完了報告
- **影響するCURRENT_SPEC項目**: CEFR-A2 構造・音声仕様 > Core Explanatory Logic Preservation
- **未実施事項(誤読防止のため明記)**: 今回のFreezeは仕様・prompt原則の正式反映のみ。既存記事(Hanshin/Health/Householdの本番article.md・音声)への遡及適用・再生成は行っていない。Household A2の本番article.mdは、ER-003-A2-B1-N3-01-FIX-01時点の手動編集版のままであり、今回正式採用したA2_KAI1_INSTRUCTIONで再生成したものではない(→[OPEN_ITEMS.md](OPEN_ITEMS.md))

## [Implementation Hardening] ER-003-N3-ROOT-FIX-01: English Key Phrase trim safety marginを0.20秒へ拡大(Key Phrase専用)

- **日付**: 2026-08-17
- **内容**: 英語Key Phrase音声生成のhead safety marginを0.08秒から0.20秒へ拡大した。共有関数のデフォルト値は変更せず、Key Phrase生成関数(`repro01.generate_key_phrase_component_verified`)だけが新しいmargin値を明示的に指定する設計とし、他segment(Preview/Comment/Title等)には一切波及しない
- **状態**: `DECIDED`(Audio実装詳細、サービス仕様の変更ではない)
- **採用理由**: "follow-up time"のようなKey Phraseで、無声摩擦音(/f/等)の語頭が無音判定の閾値付近にあり、既定の0.08秒marginでは実際に語頭が一部trimされる実例を波形解析で確認した。0.08秒では不足する実例が確認された一方、全Key Phraseの間合いを必要以上に長くしないため、0.35秒ではなく0.20秒(約2.5倍)を採用した
- **比較した選択肢**: (a) 全Key Phrase一律で0.20秒、(b) 語頭が無声摩擦音の単語だけ拡大、(c) 無音判定アルゴリズム自体を二段階しきい値へ再設計
- **却下理由(b・c)**: (b)は判定ロジックの追加実装が必要で複雑化する。(c)は共有の無音判定関数(他の多数の音声生成でも使われている)の改修になり、影響確認の負荷が大きい。今回は開発コスト・既存資産への影響が最も小さい(a)を採用
- **根拠レポート**: ER-003-N3-ROOT-FIX-01完了報告(波形解析による検証含む)
- **影響するCURRENT_SPEC項目**: Cross-level仕様 > Audio Implementation Detail > English Key Phrase trim safety margin

## [Implementation Hardening] ER-003-N3-ROOT-FIX-01: TTS style instructionの責務分離+短いJapanese phraseへのminimal instruction fallback

- **日付**: 2026-08-17
- **内容**: 共通style instruction(`er002_common.py`の`POINT_LABEL_FIDELITY_RULE`)が、Point One/Point Two/In One Lineという構成ラベル文字列を無条件に読み上げさせる指示を含んでいた。これは番組全体を1回のTTS呼び出しで読む旧方式のために書かれたもので、現行のセグメント単位生成では不要かつ、モデルが指示文自体を読み上げてしまう(instruction leakage)原因になっていた。全参照箇所を監査した上で、共通instructionからこの指示を既定で除外し(opt-inパラメータ化)、必要な一括生成呼び出し元がもしあれば明示的に有効化できる設計へ変更した。あわせて、検証の結果この対策だけでは短い単独の日本語フレーズ(Key Phrase訳等)へのinstruction leakageが解消しないことが判明したため、英語Key Phraseに既存のminimal instruction fallbackと同じ考え方を日本語の短いフレーズにも拡張した
- **状態**: `DECIDED`(Audio実装詳細、サービス仕様の変更ではない)
- **採用理由**: 実測で、POINT_LABEL_FIDELITY_RULE除去後も、短い日本語フレーズ("モデルで推定した差")で5/5回leakageが再現した一方、同程度の長さの文(Household日本語タイトル)では0/5回だった。これにより、脆弱性は「短いフレーズに長いstyle instructionを渡すこと」自体にあると判明し、英語で既に実証済みのfallbackパターンを日本語へ拡張することが最小コストの対策と判断した
- **比較した選択肢**: (a) 共通instructionの責務分離のみ、(b) (a)+日本語minimal instruction fallback、(c) Cross-level consistency用の新規LLM監査工程
- **却下理由(a単独)**: 実測で不十分と判明したため、(b)まで実施した。(c)は新しい監査工程を追加しない方針のため見送り
- **根拠レポート**: ER-003-N3-ROOT-FIX-01完了報告(caller監査表・leakage regression実測ログ含む)
- **運用コストの実測**: 標準経路が既に成功しているケースには呼び出し増なし。標準経路が不合格を繰り返すケースでのみ、fallback分のTTS/ASR呼び出しが追加発生する(実測: 1トライアルあたり1〜5回)
- **影響するCURRENT_SPEC項目**: Cross-level仕様 > Audio Implementation Detail > TTS style instruction責務分離、短いJapanese phraseのminimal instruction fallback

## [サービス・生成仕様] ER-003-B1-B2-SCOPE-FIX-01 Decision A: B1はB2共通本文ではなく、LedgerからB1用英文を独立生成する

- **日付**: 2026-08-17
- **内容**: ER-003-B1-A2-SPEC-FREEZE-01-R1で`NEEDS_CONFIRMATION`としていたB1/B2関係を確定する。B1はB2と同一テキストを共有しない。B1は、Verified Fact LedgerからB1専用のWriterで独立して英文を生成する。目標は: natural spoken news English、adult tone、A2ほど強く簡略化しない、B2相当の難しい英文よりlisteningで追いやすい、Clause Density/Concept Density/Long-distance Dependency等を抑える、hardなCEFR語彙制限・文長制限は設けない。既存の`B1_B_DIRECT_INSTRUCTION`の思想をそのままB1本文の正式仕様とする。「B1 = B2本文 + Support」という理解は採用しない
- **状態**: `DECIDED`
- **採用理由**: (1) N3で実際に採用・検証した方式(B1-B Direct Generation)と一致する。(2) 実際に検証済みの`B1_B_DIRECT_INSTRUCTION`の文言("clearly easier to follow while listening than a B2 news story")と一致する。(3) B1として自然さを保ちつつListening Loadを下げられる。(4) B2という中間生成物が不要になり、生成・QA工程が1本化できる
- **比較した選択肢**: (a) B1=B2本文をそのまま流用+Supportで差別化(FREEZE-01時点の暫定記述)、(b) B1=Verified LedgerからB1専用Writerで独立生成(採用)
- **却下理由(a)**: 実際の検証・実装(`B1_B_DIRECT_INSTRUCTION`)と一致しない。N3パイプラインには比較対象となる独立したB2生成段階自体が存在せず、「B2と同一」を実際に検証する手段がない
- **根拠レポート**: ER-003-A2-B1-N3-01(`B1_B_DIRECT_INSTRUCTION`の実装・3ジャンル検証)、ER-003-B1-A2-SPEC-FREEZE-01-R1(NEEDS_CONFIRMATION提起)、ER-003-B1-B2-SCOPE-FIX-01(本Decisionでのユーザー確定)
- **影響するCURRENT_SPEC項目**: 「B1(独立生成Natural Spoken News English)」節一式(基本方針、A2との関係、News本文の生成方式)

## [サービス・Scope仕様] ER-003-B1-B2-SCOPE-FIX-01 Decision B: Initial Launch levelはA2/B1の2つとする

- **日付**: 2026-08-17
- **内容**: 初期Launchの対象レベルを**A2/B1の2レベル**に絞る。CEFR-B2は初期サービス中核から外し、`LAUNCH_SCOPE: OUT_OF_INITIAL_SCOPE`とする。これはB2の廃止を意味しない。B2は今後、future expansion candidate / internal comparison・reference / historical experiment・referenceという位置づけで保持する。B2は初期External Pilot対象外、初期Production article generation対象外、初期UI/level selection対象外、初期Cost Baselineの必須対象外とする
- **状態**: `DECIDED`
- **採用理由**: (1) A2/B1が現在最も検証が進んでいる(N3-01の3ジャンル横展開・ROOT-FIX-01/VERIFY-01等)。(2) B2を初期Launchに含めると、記事生成・音声・QA・UI・External Pilot・運用コストのすべてが増える。(3) 初期の価値検証(External Pilotでの体験成立確認)には2レベルで十分。(4) B2は将来、必要になった時点で拡張可能な設計になっている(同一Ledgerからの独立Writer生成という構造はA2/B1と共通のため、B2追加時も既存アーキテクチャを再利用できる)
- **比較した選択肢**: (a) A2/B1/B2の3レベルで初期Launch、(b) A2/B1の2レベルで初期Launch、B2は将来拡張候補として保持(採用)
- **却下理由(a)**: 3レベル同時Launchは記事生成・音声制作・QA・UI設計・External Pilot設計・運用コストのいずれも増加させ、初期の価値検証を遅らせる。B2は現時点でテキストのみ生成済みで音声化が一度も実施されていない([OPEN_ITEMS.md](OPEN_ITEMS.md)参照)ため、初期Launchに含めると新たな検証範囲が発生する
- **根拠レポート**: ER-003-B1-B2-SCOPE-FIX-01(ユーザーDecision)
- **影響するCURRENT_SPEC項目**: CEFR比較表・冒頭の`LAUNCH_SCOPE`注記、[PROJECT_INDEX.md](PROJECT_INDEX.md)のLaunch対象レベル、[ARTIFACT_REGISTRY.md](ARTIFACT_REGISTRY.md)のB2行への注記

## [Implementation Hardening] ER-005-AUDIO-INSTRUCTION-SEPARATION-01: TTS style instructionとspoken textのStructured Separationを正式採用

- **管理ID**: `ER-005-AUDIO-INSTRUCTION-SEPARATION-01`
- **日付**: 2026-08-21
- **状態**: `DECIDED` / `CURRENT_SPEC`(Audio実装詳細、サービス仕様の変更ではない)
- **内容**: Gemini TTSへ渡す入力(`er003_b1_p4c_audio.build_tts_prompt(text, style_prefix)`)で、style instruction(話し方の指示)とspoken text(実際に読み上げる本文)を、`=== STYLE INSTRUCTIONS (do not speak) ===`/`=== TEXT TO SPEAK ===`という明示的なdelimiterで区切る構造(Structured Separation)を、現行production TTS経路(B1/A2、英語/日本語、standard/fallback双方)の標準方式として採用した。既存のこの共有関数を経由しない直接文字列連結(`style_prefix + text`)が2箇所(`er003_b1_p9a_audio.generate_narration_snippet`の日本語分岐、`er003_v1_sing01_voice01_generate.generate_charon_japanese`の標準経路)で見つかり、あわせて`build_tts_prompt()`経由へ統一した
- **何を変えたか**: TTSへ渡す入力の「区切り方」のみ。共有関数`build_tts_prompt()`を1箇所変更することで、これを呼び出す全経路(B1: `voice01.generate_charon_english/generate_charon_japanese`、`news_tail_fix.generate_news_narration_wide_margin`、`point_headings.generate`。A2/共通: `p9a.generate_narration_snippet`経由の`repro01.generate_narration_snippet_verified_strict`、`repro01.generate_key_phrase_component_verified`、`repro01.generate_english_component_minimal_instruction`、A2日本語fallback)へ一括反映した
- **何を変えていないか**: style instruction本文(内容・語数・意味)、speaker指定、voice、tone、pacing要求、narration character、spoken text本文(内容・語数・意味)は一切変更していない。Gemini公式`system_instruction`フィールドへの置き換えは行っていない(次項参照)
- **検証根拠(ER-005-AUDIO-VALIDATION-ROBUSTNESS-02のControlled Test)**: 過去に問題が確認された5segment(A2 `topic_intro`/`point_one`/`full_story_part1`、B1 Key Phrase 5英語・日本語)を対象に、Current方式とStructured Separation方式を同一style instruction・同一spoken textで比較した(各方式合計18回)。Current正常生成4/18(22.2%)、Structured正常生成13/18(72.2%)。技術的失敗(`INVALID_ARGUMENT`・応答parts欠落・500 INTERNAL)は、Current 9/18(50%)からStructured 0/18(0%)へ改善。Structured側で成功した全13件は、ASR検証(EXACT_MATCH)・音声長のいずれも正常範囲内であることを確認した。ユーザー試聴Artifact([Instruction Separation A/B Test](https://claude.ai/code/artifact/24309532-42d8-46f1-9e43-4116afb4c311))でAudio Style(自然さ・落ち着き・ニュースらしさ・話者の印象・テンポ・聞きやすさ)を確認いただいた上で、本Decisionを確定した
- **留保(重要)**: 試行数は各条件2〜5回と小規模であり、この検証だけでGemini TTSのinstruction leakage問題の**確定的な誘発条件を特定した**とは記録しない。「現時点で最も安定したProduction Baselineとして採用」という位置づけであり、「完全解決」ではない。誘発条件そのものは未解明のまま[OPEN_ITEMS.md](OPEN_ITEMS.md)で監視を継続する
- **比較した選択肢**: (a) 現状維持(単純連結)、(b) Gemini公式`system_instruction`フィールドで分離、(c) 単一`contents`文字列内を明示的delimiterで区切るStructured Separation(採用)
- **却下理由(b)**: Google公式ドキュメント(ai.google.dev/gemini-api/docs/speech-generation)にTTSでの`system_instruction`対応記載がなく、実機テストでも同一リクエストから`system_instruction`だけを外すと成功するのに対し、指定すると2/2で`500 INTERNAL`エラーになることを確認した。技術的に不安定/非対応と判断し不採用とした。将来Google側の公式仕様が変更された場合は別タスクで再評価する。現在の実装を今回の判断だけでsystem_instruction方式へ勝手に置き換えないこと
- **根拠レポート**: ER-005-AUDIO-VALIDATION-ROBUSTNESS-02完了報告(Controlled Test実測データ)、ER-005-AUDIO-ROBUSTNESS-SPEC-FIX-01完了報告(Production適用範囲監査・regression test)
- **影響するCURRENT_SPEC項目**: Cross-level仕様 > Audio Implementation Detail > TTS Instruction/Spoken Text分離(Structured Separation)

## [Implementation Hardening] ER-005-JA-SHORT-ASR-PHONETIC-01: 短い日本語segmentの発音ベースASR Validationを正式採用

- **管理ID**: `ER-005-JA-SHORT-ASR-PHONETIC-01`
- **日付**: 2026-08-21
- **状態**: `DECIDED` / `CURRENT_SPEC`(Audio実装詳細、サービス仕様の変更ではない)
- **内容**: 短い日本語segment(Japanese Key Phrase・gloss/meaning等、30文字以下)のASR検証に、漢字表記の完全一致だけに依存しない発音(読み)ベースの判定を追加した。`er003_audio_tts_asr_safety.validate_japanese_short_segment_match()`が、EXACT_MATCH/NORMALIZED_MATCH/PHONETIC_MATCH/TRUE_CONTENT_MISMATCH/ASR_UNCERTAINの5分類を返す。PHONETIC_MATCH(pykakasiによる読み変換が完全一致)は採用しTTS retryしない。TRUE_CONTENT_MISMATCH(数字・否定語の不一致、または読みが大きく異なる)はTTS retry候補のまま。ASR_UNCERTAIN(読みが近いが完全一致ではない中間ケース)は、TTSが誤っていると断定せず既存audioを保持したまま既存fallback/reviewへ委ねる
- **何を変えたか**: `er003_v1_sing01_voice01_generate.generate_charon_japanese`(B1、standard/fallback双方)、`er003_v1_repro01_main_generate.generate_narration_snippet_verified_strict`(language="ja"の場合、A2共有)、`er003_v1_n3_01_tts_generate.generate_a2_japanese_with_fallback`(A2 fallback)の検証ロジックへ、既存の完全一致/部分一致チェックが不合格の場合の**追加の採用条件**として組み込んだ。既存の合格ケースを壊す変更ではない(既存チェックが通れば従来通り即採用)
- **何を変えていないか**: 数字の実質的な違い・否定の有無・主要語の欠落・明らかに異なる発音・無関係な発話・hallucinationはPHONETIC_MATCHで吸収しない(hard-fail条件として維持)。長文Narrationへの適用範囲拡大は行っていない(30文字以下のみ)。個別専門用語のwhitelist(1対1のハードコード)は主方式にしていない
- **検証根拠**: ER-005-AUDIO-WASTE-REDUCTION-01のfixture(内向化問題/内効果問題、外向化問題/外交化問題等、鏡像/京三・恭三、行動上の問題/公道上の問題)全件でPHONETIC_MATCHとして正しく採用されることを確認。数字違い・否定語違い・無関係内容・空ASR・長文への誤適用は全てFAILすることをunit testで確認(negative test)。加えて、ER-005-AUDIO-VALIDATION-ROBUSTNESS-02のControlled Testで得た、fixtureに含まれない未知のASR誤認識パターン(「関連・相関」に対する「関連創刊」「関連、創建」等10件)でも、8/10が正しくEXACT_MATCH/PHONETIC_MATCHと判定され、明らかに無関係な1件・曖昧な2件はそれぞれ正しくTRUE_CONTENT_MISMATCH/ASR_UNCERTAINに分類されることを確認した(fixture外データでの追加検証)
- **比較した選択肢**: (a) 現状維持(漢字表記完全一致のみ)、(b) 個別専門用語ごとのwhitelist(「内向化→内効果ならPASS」等の1対1登録)、(c) 発音(読み)ベースの一般的な検証ロジック(採用)
- **却下理由(b)**: 新しい専門用語が出るたびに個別登録が必要になり、量産(新テーマ・新記事)に向かない。一般的な読み・発音正規化で吸収できない特殊ケースだけを将来的な限定fallback候補として扱う方針とし、(b)を主方式にはしない
- **根拠レポート**: ER-005-AUDIO-WASTE-REDUCTION-01完了報告、ER-005-AUDIO-VALIDATION-ROBUSTNESS-02完了報告、ER-005-AUDIO-ROBUSTNESS-SPEC-FIX-01完了報告(Production適用範囲・regression test)
- **影響するCURRENT_SPEC項目**: Cross-level仕様 > Audio Implementation Detail > 短い日本語segmentのASR検証: 発音ベースPhonetic Validation

## [Implementation Hardening] ER-006-MODEL-ROUTING-CONTRACT-01: Production Model RoutingをLunaへ統一・Fail-Closed契約化

- **管理ID**: `ER-006-MODEL-ROUTING-CONTRACT-01`
- **日付**: 2026-08-22
- **状態**: `DECIDED` / `CURRENT_SPEC`(Model Routingの実装契約、B1/A2構造やSupport内容等のサービス仕様の変更ではない)
- **監査で判明した経緯**: B1/A2 Writer・Writer Fact Check・Deviation Check・B1/A2
  Support(Comment/Preview/Key Phrase選定・正規化)は、コード上は元々(ER-002/003時代
  から一貫して)`gpt-5.6-sol`を使う設計だった(`er002_ja_free_markdown_restore.
  WRITER_MODEL = "gpt-5.6-sol"`という単一のhardcoded literalへ、Writer/Support/Key
  Phrase Selector等の全チェーンが連鎖的に依存)。`gpt-5.6-luna`は元々Query
  Planning/Topic Selection(`gather_topic.py`のMODEL_SEARCH)専用として設計されており、
  Writer/Support系をLunaにするという明文化された決定は、`CURRENT_SPEC.md`・
  `DECISION_LOG.md`のどちらにも存在しなかった(ER-005-WRITER/SUPPORT-COST-QUALITY-01
  はLunaでの品質同等性を検証しない前提の未検証な試験提案だった)。ER-006-POOL-PILOT-
  COST-ROOTFIX-01でこれを「Sol混入」と呼んだのは不正確で、正しくは「Cost集計スクリプト
  がLuna単価を誤って適用していた」バグと、「Writer/Support系Model RoutingをLunaへ
  正式決定するかどうかがこれまで未決だった」という2つの別の問題だった
- **今回のユーザー決定**: Writer(B1/A2)・Writer Fact Check・Support(B1/A2、Key
  Phrase選定・正規化含む)・Support Fact Checkの4工程は、ER-005での方針に整合させる
  形で`gpt-5.6-luna`をApproved Modelとして正式に固定する。Solはこれら工程では使用禁止
  とし、Fail-Closed契約(規定外modelが渡された場合はAPI call前に例外を送出、model
  未指定もFAIL)を適用する。Research系(Evidence Pack/VFL/Verification)・Query
  Planning・Topic SelectionはLunaのまま変更なし
- **何を変えたか**: [er006_model_routing_contract_01.py](er006_model_routing_contract_01.py)
  にProcess別Approved Model/ProviderのSingle Source of Truthと`require_model()`/
  `require_provider()`(fail-closed validator)を新設。production到達可能な各呼び出し
  箇所([er003_v1_n3_01_articles_generate.py](er003_v1_n3_01_articles_generate.py)の
  Writer/Fact Check/Deviation Check、[er003_v1_n3_01_scaffold_generate.py]
  (er003_v1_n3_01_scaffold_generate.py)のB1/A2 Support・Key Phrase選定・正規化、
  [er006_pool_pilot_01_research.py](er006_pool_pilot_01_research.py)のEvidence
  Pack/VFL/Verification/Exception Search、[er006_pool_pilot_01_support.py]
  (er006_pool_pilot_01_support.py)のSupport Fact Check)へ、SSOT経由の明示的な
  `model=`指定を追加した
- **何を変えていないか**: 各leaf関数(`vfl01.run_writer_no_search`等)自体の既定値
  (`MODEL`、Sol系譜)はそのまま残し、`model`引数を追加しただけ(後方互換)。この
  既定値を使う他の呼び出し元(Translation pipeline・過去のCEFR/spoken-first等の実験
  タスク、30件以上)はSolのまま変更していない(今回のスコープ外。過度な大規模
  refactorを避けるため、共有root定数自体は変更せず、production到達可能な呼び出し
  箇所だけへ明示的にoverrideを注入する方式を採った)
- **品質検証状況(重要な留保)**: LunaがSolと同等の記事・Support品質を出せるかは、
  本タスクでは検証していない。次回以降のPool topic生成・既存テーマ(hanshin/health/
  household)再生成時の実際の出力で確認が必要
- **Cost影響**: 6episode(ER-006 Pool Pilot)のHistorical Actual Spend(実際に支払った
  金額、¥2,639.6)は書き換えない。Counterfactual(今回のApproved Routingだった場合の
  理論値)は¥883.8で、差額¥1,755.8がSol使用による超過コストだった
- **根拠レポート**: ER-006-MODEL-ROUTING-CONTRACT-01完了報告(Model監査・
  Fail-Closed契約実装・Regression/Static Audit test・Cost再計算)
- **影響するCURRENT_SPEC項目**: Model Routing Contract(新設セクション)

## [Implementation Hardening] ER-006-POOL-BENCHES-LUNA-AUDIO-VALIDATION-01: Audio ValidationのProduction配線・ASR一致と発音品質の分離・Luna品質確認

- **管理ID**: `ER-006-POOL-BENCHES-LUNA-AUDIO-VALIDATION-01`
- **日付**: 2026-08-22
- **状態**: `DECIDED` / `CURRENT_SPEC`(Audio実装詳細・Model Routing運用、B1/A2構造等の
  サービス仕様変更ではない)
- **内容1(Audio Validation配線)**: ER-006-POOL-PREPROD-HARDENING-01で実装済み
  だった、ASR比較の正規化+6分類(EXACT_MATCH/NORMALIZED_MATCH/HIGH_SIMILARITY_
  SAFE/ASR_VALIDATION_UNCERTAIN/TRUE_CONTENT_MISMATCH/TTS_FAILURE)+Protected
  Check+同一signature retry guardrailを、英語(language=="en")のProduction
  retry loopへ配線した(`er006_preprod_hardening_01_validation.evaluate_
  attempt()`が統一エントリポイント)。対象: `er003_v1_sing01_voice01_
  generate.py::generate_charon_english`、`er003_v1_sing01_news_tail_fix.py`、
  `er003_v1_sing01_point_headings_aoede.py`、`er003_v1_repro01_main_
  generate.py::generate_narration_snippet_verified_strict/generate_key_
  phrase_component_verified`、`er003_v1_crosslevel_audio_02_common.py::
  generate_english_segment_with_fallback`。新status`ASR_VALIDATION_
  UNCERTAIN`を追加し、同一signatureが3回連続で改善しない場合はretryを
  打ち切り直前のaudioを保持する(STOPPEDとは区別、Human Review対象)。実際の
  Public Benches Luna版生成で、A2 point_twoがこの新statusで正しく打ち切られる
  ことを確認した。日本語(ja)経路は既存のphonetic_verdict方式のまま無変更
- **内容2(ASR一致と発音品質の原則)**: Key Phrase "hostile architecture"の
  ユーザーHuman Review報告(語頭/h/が/p/様に聞こえる)を、既存生成物の
  forensic調査(canonical text→TTS input→raw音声振幅エンベロープ→assembled
  音声との定量比較→ASR transcript)により調査した。ASRは全サンプルで正しく
  "Hostile architecture."と書き起こしていたが、raw音声の振幅エンベロープには
  母音遷移部で最大2.3〜4.7倍(20ms窓)という急峻な立ち上がりがあり、これは
  Assembly処理(resampling/gain)由来ではなくraw TTS生成時点で既に存在する
  ことをcross-correlationによる実測で確認した。別の/h/開始語でも同程度の
  急峻さを確認し、hostile固有ではなく短いKey Phrase発話の一般的なTTS特性で
  ある可能性が高いと判断(個別whitelist化はしていない)。この調査結果を
  踏まえ、「ASR transcript一致は発音品質PASSの証明ではない」という原則を
  [CURRENT_SPEC.md](CURRENT_SPEC.md)のQA/Human Review節へ正式に明文化した。
  振幅エンベロープの急峻さを検出する新しいAudio Validation(将来候補)は
  今回実装していない(詳細は[OPEN_ITEMS.md](OPEN_ITEMS.md)のOPEN-44、
  `UNDER_REVIEW`のまま)
- **内容3(Luna品質の実地確認)**: Public Benches(既存の確定済みEvidence
  Pack/VFL/Verification/Ledgerを再利用、Researchは再実行せず)のB1/A2を
  Model Routing Contract(全工程Luna、Sol call 0件を実測で確認)で新規生成し、
  旧Sol版と比較した。B1: Writer Fact Check PASS・Ledger完全準拠(Sol版は
  MINOR 1件)。A2: Fact Check REVIEW_REQUIRED(矛盾ではなく未確認の詳細3件)・
  Ledger MINOR 2件(Sol版は完全準拠)。総じて明確な品質劣化は確認されな
  かったが、A2でSol版よりわずかに逸脱が増えた点は留保として記録する。
  Audio面はSTOPPED/UNCERTAIN数がSol版(4件)よりLuna版(7件STOPPED+1件
  UNCERTAIN)で増えたが、個別調査の結果、原因はLuna特有の品質問題ではなく
  Azure ASRの表記揺れ(street→St.、three→3:00等)や既知のMalmö/Triangeln
  固有名詞音訳差であり、比較対象のSol版でも同種の事象が確認されている
- **Cost影響**: Writer+Support実費は約16分の1に削減(Sol版はRewrite込みで
  約¥766、Luna版は単一passで約¥47)。Audio実費はSTOPPED増加により若干上昇
  したが、総額は約65%削減(詳細は完了報告参照)
- **根拠レポート**: ER-006-POOL-BENCHES-LUNA-AUDIO-VALIDATION-01完了報告
- **影響するCURRENT_SPEC項目**: QA/Human Review > ASR一致と発音品質の関係(新設)

## ER-006-AUDIO-COST-PILOT-02(2026-08-22)

- **Decision**: 音声パイプラインのASR Provider Routingを、**英語=OpenAI
  gpt-4o-mini-transcribe(Primary)、日本語=Azure Speech STT(維持)**の
  言語別構成でPilot導入する(SSOT: `er006_asr_provider_routing_01.py`)。
  Fail-closed設計(未登録言語は例外送出、暗黙fallback禁止)
- **根拠**: 同一トピックでの実測比較で、STOPPED数が7件→3件、TTS+ASR
  attempt総数が110→79(-28%)、Audio実費が¥306→¥199/pair(-35.1%)。
  誤って内容誤りをPASSさせたケースは0件
- **Validator方針変更**: street/St.のような通り種別略語(USPS標準の
  閉じた既知集合)は、canonical側テキストを基準に安全吸収する方針へ
  転換した(ER-006-POOL-PREPROD-HARDENING-01時点の「Saint曖昧性を
  理由に吸収しない」という以前の判断を上書き。canonical-anchored設計
  によりSaint/Streetの曖昧性は解消できることを確認したため)
- **未決定のまま保留**: Gemini TTS Batch API採用の可否(Human Review
  Artifact試聴待ち)。固有名詞"Ottoni"のASR認識限界への対応方針
  (発音辞書登録等は未着手)。量産再開の可否
- **根拠レポート**: ER-006-AUDIO-COST-PILOT-02完了報告
- **影響するCURRENT_SPEC項目**: なし(サービス仕様は無変更、実装
  アーキテクチャ層の変更のみ)

## ER-006-VALIDATOR-NUMERIC-COST-RECONCILE-01(2026-08-22)

- **Decision**: 1 Topic(B1+A2 pair)のExpected Production Costは
  **¥111.17/pairを正とする**(ER-006-AUDIO-COST-PILOT-02の¥106.4、
  ER-006-AUDIO-RETRY-CASCADE-PROD-01の¥113.0はいずれも今後参照しない)
- **根拠**: ¥106.4はPronunciation Research/Secondary ASR Cascade費用を
  一切含んでいなかった(その時点で未実装)。¥113.0はその費用を含めたが
  「Cascade発動1.3回/topic」という根拠不明の仮定を使っており、実測
  (3 topic・6 curated segment中2回発動)より高く見積もっていた。今回、
  Clean Cost(¥65.14)・Expected Waste(¥46.03、TTS/ASR retry実測1.68倍+
  Pronunciation Research実測cache miss率+Secondary ASR保守的estimate)を
  分離して再構築し、¥111.17/pairへ収束させた
- **併せて決定**: Validatorの数値正規化(cardinal/comma/decimal/percent/
  currency/ordinal third以降)を一般化する。ただし"first"・"second"は
  副詞用法との曖昧性が高いため対象外とする(実際に既存fixtureで誤PASSの
  回帰を検出したため)。序数接尾辞の除去は月名直後の日付文脈のみに限定
  する(従来の無条件除去は"28"と"28th"を誤って同一視する実バグだった)
- **未決定のまま保留**: Secondary ASR Cascadeの発動率(1回/topic、
  ESTIMATE)はランダムサンプルでの検証待ち。Production default化の
  判断もOPEN-48から継続保留
- **根拠レポート**: ER-006-VALIDATOR-NUMERIC-COST-RECONCILE-01完了報告
- **影響するCURRENT_SPEC項目**: なし(サービス仕様は無変更、Validator/
  原価計算ロジックのみの変更)

## ER-006-AUDIO-COST-SPEC-FIX-01(2026-08-22)

**管理ID: ER-006-AUDIO-COST-SPEC-FIX-01**

過去4タスク(AUDIO-COST-PILOT-02/PRONUNCIATION-LEDGER-SECONDARY-ASR-01/
AUDIO-RETRY-CASCADE-PROD-01/VALIDATOR-NUMERIC-COST-RECONCILE-01)で行った
実装アーキテクチャ決定を、SSOT(CURRENT_SPEC.md「Audio Production
Pipeline」節新設、OPEN_ITEMS.md、Model Routing Contract)へ正式に固定した。
本タスク自体は新規のAPI呼び出し・新規実装を行っていない
(ドキュメント統合+Drift Prevention Static Audit追加のみ)。以下8件を
正式Decisionとして記録する。

**Decision 1 — Model Routing: B1/A2 Writer・Support系はLuna**
- 内容: Writer/Writer Fact Check/Support/Support Fact CheckのApproved
  ModelをGPT-5.6 Lunaとする(既存Decision、ER-006-MODEL-ROUTING-CONTRACT-01
  で確定済み)
- Supersedes: ER-002/003時代のgpt-5.6-sol既定値
- 根拠タスク: ER-006-MODEL-ROUTING-CONTRACT-01、ER-006-POOL-BENCHES-LUNA-AUDIO-VALIDATION-01(Audio面での再検証)
- 本タスクでの扱い: 既存Decisionの再確認・CURRENT_SPEC Model Routing Contract表の日付整合のみ、内容変更なし

**Decision 2 — Gemini TTS Batch API採用(方式として)**
- 内容: Gemini TTSの呼び出し方式は、Standard同期呼び出しではなくBatch
  API(`client.batches.create()`)をProduction標準として採用する
- 根拠: Batch APIは英語`gemini-2.5-pro-preview-tts`・日本語
  `gemini-3.1-flash-tts-preview`とも実機で完走確認済み(50%オフ)。
  ユーザーによるHuman Review試聴で、StandardとBatchの間に品質差が
  ないことを確認済み(voice/style/Structured Separation/spoken text/
  TTS model自体は無変更、実装方式のみの変更でありサービス仕様変更では
  ない)
- **実装状況の更新(2026-08-22、ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01)**:
  当初(ER-006-AUDIO-COST-SPEC-FIX-01時点)は採用「方針」の確定のみで、
  実際のProduction TTS生成6箇所は全てStandard呼び出しのままだった
  (OPEN-50として記録)。ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01で、
  新設した`er006_batch_tts_wiring_01.py`(既存のtts_call_fn(prompt)->bytes
  という呼び出し形状を保つdrop-in Batch factory、fail-closed設計・
  Standardへの暗黙fallbackなし)を、Production 6ファイルの全call site
  (`er003_v1_repro01_main_generate.py`・`er003_v1_sing01_news_tail_fix.py`・
  `er003_v1_sing01_point_headings_aoede.py`・`er003_v1_sing01_voice01_
  generate.py`・`er003_v1_n3_01_tts_generate.py`。
  `er003_v1_crosslevel_audio_02_common.py`はrepro01の関数を再利用する
  だけのため直接変更なしで自動的にBatch経由になる)へ配線した。
  1 Batch job = 1 itemの設計(item数に関わらずBatch料金割引は
  per-request適用のため、コスト効果は完全に得られる)。既存の
  ASR-first Retry Cascade・Validator・Master Audio Storeは無変更
  (TTS呼び出しの中身だけをStandardからBatchへ差し替えるdrop-in
  replacement)。item単位の成功/API error/empty result/invalid audio/
  missing responseの5分類・cost telemetry(`er005_cost_logger`統合)も
  実装済み。Static Audit(`er006_audio_cost_spec_fix_01_static_audit.py`)
  でStandard専用call_fn構築が実コードに残っていないことをassertion
  化して確認。OPEN-50はこの範囲でResolvedへ更新(TTS Pronunciation
  Hint配線は今回のスコープ外のまま、OPEN-47で継続)
- Supersedes: Standard呼び出しのみを前提としていた過去の暗黙の前提
- 根拠タスク: ER-006-AUDIO-COST-OPTIMIZATION-01(実機検証)、
  ER-006-AUDIO-COST-SPEC-FIX-01(方針の正式化・実装ギャップの明記)、
  ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01(Production実配線)

**Decision 3 — Primary ASR: 英語はOpenAI gpt-4o-mini-transcribe**
- 内容: 英語ASRのPrimaryを、Azure Speech-to-TextからOpenAI
  `gpt-4o-mini-transcribe`へ切り替える。日本語はAzureのまま維持する。
  SSOTは`er006_asr_provider_routing_01.py`(fail-closed、未登録言語は例外)
- 根拠: 同一トピック実測でSTOPPED数7→3件、attempt数110→79(-28%)、
  Audio実費¥306→¥199/pair(-35.1%)、誤って内容誤りをPASSさせたケース0件
- Supersedes: Azureを英語ASR Primaryとする旧構成
- 根拠タスク: ER-006-AUDIO-COST-PILOT-02

**Decision 4 — Master Audio Store採用**
- 内容: 固定/完全一致で再利用可能な音声は`er006_master_audio_store_01.py`
  経由で生成・キャッシュし、無条件の毎回TTS再生成をしない
- 根拠: 言語・レベル・voice・TTS model・style instruction hash・
  canonical text hash・processing version・sample rate等をキーとする
  ことで、条件不一致audioの誤再利用を防ぎつつ固定segmentの重複生成を
  避けられる
- Supersedes: 固定ナレーションを含め毎回無条件でTTS呼び出しを行っていた旧実装
- 根拠タスク: ER-006-AUDIO-COST-PILOT-02(最小実装・Production配線)

**Decision 5 — Validatorの数値正規化を一般化**
- 内容: cardinal number・桁区切りカンマ・小数点・パーセント・通貨・
  序数(third以降)の表記ゆれを、個別記事のwhitelistではなく一般規則で
  吸収する。ただし数値が異なる・時刻表記artifact・序数と基数の取り違え・
  記号欠落・年の違い・否定の有無の違いは絶対に吸収しない
- 根拠: Public Benches Boavida segment("28"↔"twenty-eight")・
  Subscriptions full_story_part2("Eighth"↔"8th")の実際のFalse NGを解消。
  検証中に「28」と「28th」を誤って同一視する序数接尾辞除去の実バグを
  発見・修正(月名直後の日付文脈のみに限定する安全な形へ変更)
- Supersedes: 個別ケースのみ対応していた旧Validator(街路名等の
  限定的な略語吸収のみ)
- 根拠タスク: ER-006-VALIDATOR-NUMERIC-COST-RECONCILE-01

**Decision 6 — Pronunciation Ledger採用(ASR側配線)**
- 内容: 固有名詞発音情報をPerplexity経由で事前取得しcacheする
  Pronunciation Ledgerを、Secondary ASRのPhrase List(`ledger_phrases`)
  経由でProduction 6箇所へ配線する。cache hitの場合は再調査しない。
  Perplexityクエリを機械的に「1トピック1リクエスト」へまとめない
  (品質低下を実測で確認したため)
- **実装状況の明記**: TTS生成側への発音ヒント注入
  (`augment_style_prefix_with_pronunciation()`)は基盤として保持するが、
  最難関ケース"Ottoni"のA/B検証で確実な改善効果を実証できなかった
  (mixed/負の結果)ため、Production TTS生成への強制配線は見送っている
- Supersedes: 発音情報を一切事前取得しない旧実装
- 根拠タスク: ER-006-PRONUNCIATION-LEDGER-SECONDARY-ASR-01、
  ER-006-AUDIO-RETRY-CASCADE-PROD-01(ASR側配線)

**Decision 7 — 固有名詞ASR不確実性はASR再検証を優先、TTS即時再生成を禁止**
- 内容: 固有名詞のASR不一致が疑われる場合、OpenAI Primary#1→Primary#2→
  Azure Secondary+Phrase List#1→Secondary#2→Human Reviewの順でASR側の
  再検証を先に尽くし、この過程を経ずにGemini TTSを即座に再生成する
  古い経路を禁止する。TTS再生成は真の内容誤り・数値/日付の意味的な違い・
  否定の違い・重要語の欠落追加・TTS技術的失敗・Human Review確定後の
  実音声誤りに限定する
- 根拠: 3 Topic実測で6対象segment中4件がPrimary ASR単体でPASS
  (旧構成では6〜12回試行のSTOPPEDだった箇所)。true content誤PASSは
  0件、new savings実測+¥128.4
- Supersedes: 「Primary ASR FAIL→即Gemini TTS再生成」という旧retry方針
- 根拠タスク: ER-006-AUDIO-RETRY-CASCADE-PROD-01

**Decision 8 — Cost定義4区分をSSOT化**
- 内容: Historical Actual(実際に支払われた金額)/Clean Production Cost
  (全工程初回成功時の理論下限、¥65.14/pair)/Expected Conditional Waste
  (Primary#2・Secondary ASR・Pronunciation Research・TTS retry等の
  条件付き追加費用の期待値、¥46.03/pair)/Expected Production Cost
  (Clean+Waste、¥111.17/pair)の4区分を、今後のER-006+報告の共通言語
  とする。Expected Production Costは推定を含む進化中のbaselineであり、
  恒久固定値ではない
- Supersedes: ER-006-AUDIO-COST-PILOT-02の¥106.4/pair、
  ER-006-AUDIO-RETRY-CASCADE-PROD-01の¥113.0/pair(いずれも今後参照しない)
- 根拠タスク: ER-006-VALIDATOR-NUMERIC-COST-RECONCILE-01(再構築)、
  ER-006-AUDIO-COST-SPEC-FIX-01(用語定義自体のSSOT化)

**Drift Prevention(Static Audit)**: 上記Decision中、機械的に検証可能な
部分(旧Azure英語Primary直接呼び出しの不在、旧Validator直接呼び出しの
不在、旧retry loop [ASR不確実性からの即時TTS再生成] の不在、Master
Audio bypassの不在、Sol modelの不在、Pronunciation Ledgerが呼び出し
経路から無視されていないこと)は、新規作成した
[er006_audio_cost_spec_fix_01_static_audit.py](er006_audio_cost_spec_fix_01_static_audit.py)
で全件PASSを確認した(2026-08-22時点)。Batch API配線(Decision 2の実装
ギャップ)のみ、当時は既知GAPとして明示的にassertion対象外で状況報告
する設計とした(誤って「配線済み」と偽装しないため)。**2026-08-22
追記(ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01)**: Batch配線の実装完了に
伴い、このチェックも正式なassertion対象へ昇格させた(詳細は下記
新規Decision参照)。

- **根拠レポート**: ER-006-AUDIO-COST-SPEC-FIX-01完了報告
- **影響するCURRENT_SPEC項目**: 「Audio Production Pipeline」節(新設)、
  「Model Routing Contract」節のTTS/ASR行

## ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01(2026-08-22)

**管理ID: ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01**

- **Decision**: ER-006-AUDIO-COST-SPEC-FIX-01のDecision 2(Gemini TTS
  Batch API採用)を、実際のProduction TTS生成6経路へ実配線した
  (詳細は上記Decision 2の実装状況追記を参照)。加えて、CURRENT_SPEC.md
  「QA / Human Review」節に残っていた「Azure STTを全内容確認・境界
  検証に使用」という旧ASR記述を、現行の言語別Routing仕様(英語Primary
  =OpenAI `gpt-4o-mini-transcribe`、日本語=Azure、Azureは英語Secondary
  としても使用、最終判断はASR単独では行わない)へ整合させた
- **根拠**: 実装ギャップ(OPEN-50)の解消。新設`er006_batch_tts_wiring_01.py`
  は既存のtts_call_fn(prompt)->bytesという呼び出し形状を保つdrop-in
  replacementとして設計し、ASR-first Retry Cascade・Validator・Master
  Audio Store・spoken text・voice・style instructionは一切変更していない
  (実行方式のみの変更)
- **設計判断の明記**: タスク仕様では「複数segmentをまとめて投入」する
  グループ投入も許容されていたが(実装方法は過度に指定しないとの前提)、
  既存6ファイルの1segmentずつのretry loop制御フローを書き換える大規模
  リファクタリングは、Production安定性優先の方針(CLAUDE.md)に照らして
  リスクが高いと判断し、今回は1 Batch job = 1 itemのdrop-in方式を
  主たる配線方式として採用した。Gemini Batch APIの料金割引(50%オフ)は
  job内item数に関わらずper-request適用されるため、この設計でも
  コスト削減効果は完全に得られる。複数item一括投入用のAPI
  (`submit_batch_multi`/`wait_for_batch_multi`)は同モジュール内に将来の
  最適化余地として用意したが、今回はいずれの本番ファイルからも呼ばれて
  いない
- **未決定のまま保留**: Secondary ASR Cascade default ON化(OPEN-48から
  継続)。TTS Pronunciation Hint配線(Ottoni検証で効果不明確だったため、
  今回のBatch配線と同時に有効化しない、OPEN-47/OPEN-50から継続)
- **根拠レポート**: ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01完了報告
- **影響するCURRENT_SPEC項目**: 「Audio Production Pipeline」節の
  「Gemini TTS実装方式」行(NOT_WIRED→WIRED)、「Model Routing Contract」
  節のTTS行、「QA / Human Review」節のASR記述

## ER-006-POOL-MASTER-ADOPTION-N4N6-RESUME-01(2026-08-22)

**管理ID: ER-006-POOL-MASTER-ADOPTION-N4N6-RESUME-01**

- **Decision**: Pool型(Evergreen)記事の生成対象となる20 Topicの正式
  母集団を、ユーザー承認のもと[POOL_TOPIC_MASTER.md](POOL_TOPIC_MASTER.md)
  として新規制定した。No.1〜3(Public Benches/Subscriptions/Startups)は
  既存生成物と一致することを確認の上で編入。No.4〜6(Supermarket
  Shuffle/Cafes/Delivery Tracking)を次回Production対象として確定した
- **背景**: ER-006-POOL-ADOPTION-N4N6-PRODUCTION-01で、「20 Topicリスト
  の一次資料をリポジトリから特定する」という前提が実際には満たされて
  いない(No.1〜3はTopic Selectionを意図的にスキップして手動選定された
  Pilot用の3件であり、20件全体を記録したファイルは一度も存在しな
  かった)ことが判明し、名前の推測・新規作成をせずSTOPして報告した。
  今回、ユーザーが残り17件を含む20件全体を新たに確定・承認したことで
  このSTOP条件が解消した
- **Topic Selection routingとの関係**: No.4〜6は、通常のTopic Selection
  Production Model(GPT-5.6 Luna)を再実行せず、ユーザーが本Master
  リストから直接指定した。これは既存のTopic Selection Routing Contract
  (`er006_model_routing_contract_01.py`の`TOPIC_SELECTOR_MODEL`)を
  変更するものではなく、「今回はユーザー指定という特別な選定経路を
  使った」という1回限りの記録であり、No.7以降の新規選定が必要になった
  場合は通常通りLuna Topic Selectionを使う
- **重複SSOT回避**: 20件のリスト本文はPOOL_TOPIC_MASTER.md 1箇所にのみ
  記録し、他ファイル(本Decision含む)へは複製しない
- **根拠レポート**: ER-006-POOL-MASTER-ADOPTION-N4N6-RESUME-01完了報告
- **影響するCURRENT_SPEC項目**: なし(サービス仕様は無変更、新規SSOT
  ファイルPOOL_TOPIC_MASTER.mdの制定のみ)

## ER-006-POOL-ADOPTION-AUDIT-01 / ER-006-POOL-N4-N6-PRODUCTION-01 / ER-006-PRODUCTION-THROUGHPUT-GATE-01(2026-08-23)

**管理ID: ER-006-POOL-MASTER-ADOPTION-N4N6-RESUME-01(3区分まとめて記録)**

- **Decision(Adoption Audit)**: 既存3記事の最終採用Candidateを確定した。
  Public Benches=script Luna版+audio ASR-Pilot-02版(parts.json完全一致
  確認済み)、Subscriptions/Startups=唯一存在する原初版(Sol Writer)。
  Script/Audio一致確認では、送信テキストと正式scriptの完全一致(既知の
  安全な正規化除く)を確認した一方、6segmentが機械ASR検証未合格のまま
  assembled音声に含まれていることを検出し、ユーザー確認Artifactで
  明示的に警告した。詳細は[ER-006-POOL-ADOPTION-AUDIT-01_diff.md](ER-006-POOL-ADOPTION-AUDIT-01_diff.md)
- **Decision(N4-N6 Production)**: No.4〜6を現行Production仕様(Luna
  Writer/Support/FactCheck、Gemini Batch TTS、OpenAI English Primary
  ASR、Azure Japanese ASR、現行Validator、Master Audio Store)で通し
  生成した。実在の学術論文・トレード記事をWebSearch/WebFetchで収集し
  Ledgerへ組み込んだ。Sol呼び出し0件、Standard TTS呼び出し0件を確認
- **Decision(Throughput Gate)**: No.4単独・No.5+No.6の2 lane並列実行
  の実測から、Gemini Batch TTSが総所要時間の83〜96%を占める支配的
  ボトルネックであることを確認した。20 Topic/day判定は`AT_RISK`
  (4〜5 lane並列の実測なし、Human Review所要時間未計測のため)。
  詳細は[ER-006-PRODUCTION-THROUGHPUT-GATE-01_report.md](ER-006-PRODUCTION-THROUGHPUT-GATE-01_report.md)
- **未決定のまま保留**: No.4〜6の最終採用判断(ユーザー試聴待ち、
  OPEN-53)、4〜5 lane並列実行の実測(OPEN-51)、Key Phrase Selectorの
  retry loop追加要否(OPEN-52)
- **根拠レポート**: ER-006-POOL-ADOPTION-AUDIT-01_diff.md、
  ER-006-POOL-N4-N6-PRODUCTION-01完了報告(本Decisionの一部として
  統合報告)、ER-006-PRODUCTION-THROUGHPUT-GATE-01完了報告
- **影響するCURRENT_SPEC項目**: なし(サービス仕様は無変更)

## ER-006-GATE-EVIDENCE-REVIEW-CASCADE-ON-MATH-ADOPT-01(2026-08-24)

- **Decision 1(数式Validator正式採用)**: 前タスク(ER-006-GATE-
  CALIBRATION-ASR-CASCADE-MATH-VALIDATOR-01)で実装した数式表記正規化
  (Markdown italic変数表記、`=`/`<`/`>`/`×`/数字間`x`、Unicode上付き
  指数・ASCIIキャレット指数、規則的な単数形/複数形吸収)を、Production
  標準Validatorの正式仕様として採用する。Regression fixtureは既存32件+
  新規23件=**計55件、全PASSを再確認**した上で採用した
- **Decision 2(ASR Secondary Cascade Production ON)**: `er006_secondary_
  asr_01.py`の`FEATURE_FLAG_SECONDARY_ASR_ENABLED`を`False`→`True`へ
  変更し、Production既定でCascadeを有効化した。前タスクで発見・修正した
  「A2側の複数形差がCascade対象外条件を誤って満たしてしまう」バグの
  修正後、実No.6 Sweeny音声(B1/A2)でCascadeがPrimary#1→#2→Secondary#1→
  #2→Human Reviewの順で正しく動作し、TTS再生成0件を確認した上で有効化
  した。全Production call site 6箇所は`cascade_enabled=secondary_asr.
  FEATURE_FLAG_SECONDARY_ASR_ENABLED`という形でモジュール定数を呼び出し
  時に参照するため、この1箇所の変更のみで全call siteへ反映される
- **Decision 3(Research Coverage GateはProduction未配線のまま据え置き)**:
  No.1(Public Benches)・No.2(Subscriptions)の較正後Gate判定
  `MORE_RESEARCH_REQUIRED`を、既存Research/Ledger/完成記事/Fact Check/
  Ledger Deviation Checkのみで追加検証した結果、8 missing_items中
  TRUE_COVERAGE_GAPは0件、FALSE_POSITIVE 7件、BORDERLINE 1件と判定した。
  No.1はGateへ渡していたtitleがpre-Writer working title(POOL_TOPIC_
  MASTER.md記載)であり、Writerが実際に採用した最終タイトルと異なって
  いたことが根本原因(実際の最終タイトルで再実行するとCOVERAGE_PASSへ
  反転することを確認、新規Researchなし)。No.2は最終タイトルで再実行
  してもMORE_RESEARCH_REQUIREDのままであり、「因果的『なぜ』を問う
  Topicで、記事が実際には行動効果Evidenceを主張せず概念的な説明に
  留める」パターンへの較正が前タスクでは不足していたことが判明した。
  この2点により、Gate単体の判定精度はまだProduction基準に達していないと
  判断し、**Production配線は行わない**(タスク仕様Part A-3で明示的に
  禁止されている通り、ユーザー指示なしに配線しない)
- **根拠レポート**: ER-006-GATE-EVIDENCE-REVIEW-CASCADE-ON-MATH-ADOPT-01
  完了報告
- **影響するCURRENT_SPEC項目**: 「Audio Production Pipeline」節の
  Validator項(55件へ更新、数式表記・複数形吸収を追加記載)、ASR-first
  Retry Policy項(`FEATURE_FLAG_SECONDARY_ASR_ENABLED=True`へ更新)

## ER-006-RESEARCH-COVERAGE-GATE-DEFER-01(2026-08-24)

- **Decision**: Research Coverage Gateを、現時点ではProductionへ導入
  **しない**。`DEFERRED / PROMISING_BUT_MORE_DATA_NEEDED`として将来の
  織り込み候補に位置づけ、実装・較正の成果は温存する
- **背景**: ER-006-GATE-EVIDENCE-REVIEW-CASCADE-ON-MATH-ADOPT-01で
  No.1(Public Benches)・No.2(Subscriptions)の較正後Gate判定を追加
  検証した結果、TRUE_COVERAGE_GAP 0件、FALSE_POSITIVE 7件、BORDERLINE
  1件と、過検知が実運用水準に対してなお残っていることが判明した。
  一方、Gate実費は約¥0.31/topic、Clean Cost増加は約0.48%(基準値
  ¥65.14/pair)と、コスト面の障壁自体は小さいことも確認済み
- **見送りの理由**: (1) No.4型のResearch不足をWriter前に検知できる
  可能性は確認済みで、Gateという仕組み自体の有用性は否定されていない、
  (2) しかし残る較正課題(①Gateへ渡すtitleの入力契約[pre-Writer working
  titleと実際の最終タイトルの乖離]、②因果的タイトルでも記事本文は
  概念説明に留める正当な編集パターンへの対応)の解消には追加の開発・
  検証時間が必要、(3) 現段階ではExternal/User Validation(実際の
  学習者・プロジェクト責任者による試聴)を優先すべきであり、Gate較正へ
  追加の開発時間を割かない、とユーザーが判断した
- **今回実施しなかったこと**: Gate promptの追加調整、新規backtest、
  Production配線、新規API call、No.7以降の記事生成(いずれもタスク
  仕様の非対象事項として明示的に除外)
- **再検討Trigger**: (a) 今後のProductionでNo.4型のResearch不足→Writer
  再生成が複数回発生する、(b) Additional Research/Writer Costが再び
  大きくなる、(c) External/User Validation後、量産フェーズへ移行する、
  (d) Topic生成数が増え、Gate評価用サンプルが自然に蓄積する。いずれか
  発生時に、OPEN-54記載の残課題への対応から再開する
- **根拠レポート**: OPEN_ITEMS.md OPEN-54(本Decisionにより正式化)、
  ER-006-GATE-EVIDENCE-REVIEW-CASCADE-ON-MATH-ADOPT-01完了報告(検証
  データの一次情報)
- **影響するCURRENT_SPEC項目**: なし(Production仕様として未追加のまま、
  今回も追加しない)

## ER-007-SPOKEN-EVIDENCE-DENSITY-AB-01 Part B(2026-08-24)

- **Decision**: No.2(Subscriptions)A2 comment_3の「やめにくくする」が「やめにくかする」寄りに
  聞こえた問題は、**TTS固有の偶発的発音ゆれ**と判定する。特定の音韻パターン(「くく」の連続
  音節等)に起因する一般化可能な問題ではないため、テキスト書き換え・「くく」の表記変更・
  No.2専用whitelistのいずれも行わず、**音声の再生成のみ**で対応する
- **根拠**: canonical text・TTS入力とも正しく、reading-safety処理による変更もなかった。実際の
  生成音声のAzure ASR書き起こしは「やめにくかする」であり、主観的な聞き取り誤りではなく音声
  自体に実際のゆれがあったことをまず確認した。次に、同一canonical textを本番と同じ生成関数で
  4回再生成したところ、4回とも正しく「やめにくくする」と発音・認識され、再現しなかった
  (再現率0/4)。これにより、構造的・音韻的に不可避な問題ではなく、単発の生成ゆれだったと
  結論づけた
- **副次的発見**: A2の長い(30文字超)Comment/Support segmentの検証は「先頭数文字一致+文字数
  許容範囲」のみを見ており、文中の一部だけが別の音へ変わっても検出できない設計上のgapが
  ある(短いsegment向けのPHONETIC_MATCH等は30文字以下のみ対象)。今回は1件のみの発見のため、
  新規Validator実装は見送り、OPEN-57へ記録した
- **根拠レポート**: ER-007-SPOKEN-EVIDENCE-DENSITY-AB-01完了報告
- **影響するCURRENT_SPEC項目**: なし(既存の短いsegment向け検証方式・Validator仕様は無変更)

## ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01(2026-08-25)

- **Decision**: 日本語ASR検証を、旧「文頭2文字prefix一致+文字数チェック」方式から、
  英語Validatorと同じ思想の全文Validator(`er007_ja_asr_validator_01.py`)+
  Secondary Cascade(`er007_ja_secondary_asr_01.py`)へ置き換え、**Production 3箇所
  (`er003_v1_repro01_main_generate.py`のJapanese分岐、`er003_v1_sing01_voice01_
  generate.py`、`er003_v1_n3_01_tts_generate.py`)へ実配線した**。あわせて日本語
  Primary ASRをAzure Speech STTからOpenAI `gpt-4o-mini-transcribe`へ切り替え、
  英語と同一構成に統一した(`ASR_ROUTING["ja"]`、`FEATURE_FLAG_JA_PRIMARY_OPENAI=True`)
- **背景**: ER-007-EVIDENCE-WORDCOUNT-JA-ASR-EFFECTIVENESS-AUDIT-01で、旧方式は
  30文字を超えるsegment(A2のPreview/Comment等)に対し実質的な内容検証を行っておらず
  (prefix一致+長さのみ)、6種類の誤り(内容の欠落・置換・数字誤り・否定反転等)全てが
  検出をすり抜けることを、fixtureによるblind-spot testingで実証していた
  (ER-007-EVIDENCE-WORDCOUNT-JA-ASR-EFFECTIVENESS-AUDIT-01完了報告)
- **配線判断の根拠(Part Fの6条件、全て満たすことを確認済み)**: (1) 新Validatorが
  実データ・fixture(20件)で6種類の誤りを全て検出、(2) 新Cascadeが真の内容誤りを
  救済しないことを6件のmock testで確認、(3) OpenAI mini日本語ASR品質がAzureと
  「比較可能、明確な劣化なし」(n=14実音声、13/14が同等以上)、(4) cost/latency
  projectionが大幅改善(-82%/-70%、96 segmentシミュレーション、実測価格ベース)、
  (5) fixtureが全種類の既知の誤りパターンを網羅、(6) STOP条件(品質不足・誤検知過多・
  誤PASS発生・cost/latency悪化)いずれにも該当しなかった
- **既知の残存限界(受容済み)**: kakasi(形態素解析器なし、規則ベース)は孤立漢字の
  異読み分岐(「頃」のgoro/koro、「後」のあと/のち等)を、diff span前後4文字の文脈
  パディングでも完全には解消できない場合がある。実データ96 segment中約3件
  (約3.1%)で発生を確認したが、影響方向は常にfalse positive(安全側: 不要なretryが
  発生するのみで、誤ってPASSすることはない)。配線後のProduction smoke test
  (`verify_ja_cascade_production_on.py`、既存音声・実OpenAI ASR呼び出し)でも同種の
  1件を実際に再現し、既知の限界どおりの挙動(TRUE_CONTENT_MISMATCHとして検出され
  retry対象になるのみ)であることを確認した
- **非対象事項(今回変更しなかったこと)**: 日本語segmentの分割・再設計、TTS
  モデル変更、第3のASR provider追加、No.7以降の記事生成、Evidence Compression
  仕様の再調整、Research Coverage Gateの再検討、英語Validator・Writer仕様の変更
- **根拠レポート**: ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01完了報告、
  OPEN_ITEMS.md OPEN-61
- **影響するCURRENT_SPEC項目**: 「QA / Human Review」節のASR診断項、「Audio
  Production Pipeline」節のPrimary ASR Routing項・Validator(日本語)項(新設)・
  ASR-first Retry Policy(日本語)項(新設)・Production TTS/ASR call site一覧項、
  「Model Routing Contract」節のASR / Audio QA項

## ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01(2026-08-25)

- **Decision**: 日本語ASR Cascade配線直後にユーザーから指摘された2件の
  問題を修正する。(A) `stop_retrying=True`(Cascadeを尽くしても未解決)
  後もTTS再生成が続くbugを`er003_v1_sing01_voice01_generate.py`・
  `er003_v1_n3_01_tts_generate.py`で修正、(B) 濁点/半濁点の有無だけが
  異なる読みゆれ(「頃」のgoro/koro等)を`TRUE_CONTENT_MISMATCH`(即TTS
  retry対象)ではなく`ASR_VALIDATION_UNCERTAIN`(Cascade対象)へ分類する
  よう`er007_ja_asr_validator_01.py`を拡張する
- **背景**: ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01のProduction
  配線直後、ユーザーが「漢字読みの誤検知・ASR表記ゆれだけの場合にTTS
  再生成へ進む経路が残っていないか」を確認するよう依頼した
  (ER-007-JA-ASR-TTS-RETRY-PATH-CHECK-01)。調査の結果、実際にどちらも
  該当することが判明した: 経路Aは、Cascade呼び出しを新規2箇所へ配線
  する際、既存の正しい実装(`er003_v1_repro01_main_generate.py`)にある
  `stop_retrying`短絡処理の移植漏れ。経路Bは、`is_entity_like_
  mismatch_ja()`がカタカナ/acronymらしさのみをCascade対象基準にして
  おり、「頃」をkakasi(形態素解析なしの規則ベース読み変換)が文脈なしで
  連濁形「ごろ」と読んでしまう実例(実データsmoke testで発見)を拾え
  なかったこと
- **修正内容**: 経路Aは、`voice01.py`(標準/フォールバック両経路)・
  `n3_01.py`(フォールバック経路)へ`if stop_retrying:`短絡処理を追加
  (英語側`crosslevel_audio_02_common.py`の既存実装を参考)。経路Bは、
  読みをひらがな変換後、Unicode NFD正規化で濁点/半濁点(結合文字)を
  除去した「清音化」文字列同士の比較(`_reading_equal_allowing_
  voicing()`)を新設し、一致すれば`phonetic_uncertain=True`として
  Cascade対象に含めた。「頃」という文字列へのハードコードではなく、
  一般的な清音化比較であることを、「頃」を含まない5組の合成ペア
  (か/が、さ/ざ、た/だ、は/ば、は/ぱ)で直接検証した
- **安全性の確認**: `phonetic_uncertain`はCascade対象への分類にのみ
  影響し、`should_pass`を直接Trueにしない(既存設計、Part Bで変更して
  いない)ため、たとえ意味の異なる語同士(例: 柿/鍵、清音化後に偶然
  一致する既知のトレードオフとして発見・記録)を誤って拾っても、
  誤PASSは構造的に起こりえない(Cascadeを尽くしてもHuman Reviewへ回る
  だけ)。「漢字なら全部Cascade」になっていないことも、清音化しても
  一致しない別読みの語(月のつき/がつ)がTRUE_CONTENT_MISMATCHのまま
  残ることで確認した
- **実測影響**: No.1〜6の既存96 Japanese segmentのうち、経路Bの誤分類で
  実際に影響を受けていたのは2件(No.5・No.6のA2 preview、同一の
  「ころ/頃」パターン)。経路Aは今回のCascade配線と同じセッション内で
  発見・修正したため、実運用ログには影響が現れていない(worst-case
  見積りのみ、詳細は完了報告Part E参照)
- **根拠レポート**: ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01完了報告
- **影響するCURRENT_SPEC項目**: 「Audio Production Pipeline」節の
  Validator(日本語)項(濁点/半濁点許容の追加を反映)、ASR-first Retry
  Policy(日本語)項(stop_retrying無視bug修正を反映)

## A2/B1 Point Structure Semantic Alignment(2026-08-25)

- **Decision**: A2/B1のPoint One・Point Two間の意味的不整合(ER-008-A2-
  STORY-B1-SUPPORT-COMPATIBILITY-AUDIT-01/OPEN-63で発見)を、生成後の
  互換性Checkerで検出・修正するのではなく、**生成前の共通設計(Shared
  Point Blueprint)をSingle Source of Truthとして防止する**方針を正式
  採用する。A2・B1で文章・語数・全Factを完全共通化するのではなく、
  「どのFactがどちらのPointに属するか」「各Pointの中心結論」という
  意味構造だけを共通化し、表現・語彙・情報量は各CEFRレベルへ独立に
  最適化されたままとする
- **背景**: OPEN-63のAuditで、No.5(カフェ)・No.6(配達追跡)それぞれで、
  A2 WriterとB1 Writerが同じVerified Fact Ledgerを見ながら独立に
  Point One/Twoへfactを振り分けた結果、両者の間で内容が食い違う
  (No.5: B1のPoint TwoがA2には無い主張[顧客労働者の価値]を中心に
  据える、No.6: 同じ実験詳細がA2ではPoint One・B1ではPoint Twoに
  配置される)ことが判明していた
- **設計**: Verified Fact LedgerのFact(既存の`fact_id`をそのまま
  再利用)を、Point 1/Point 2それぞれの`common_fact_ids`(両レベル
  必須)・`optional_b1_fact_ids`(B1のみ可)・`comment_anchor`(共通
  Commentが安全に参照できる範囲)等へ振り分けるBlueprintを、A2/B1
  Writer呼び出し前に1回生成し、両Writerへ共通入力として渡す。
  互換性の検証は、Writer/Comment自身が申告するfact_id利用状況
  (応答末尾の軽量なfenced JSON block)とBlueprintの宣言を突き合わせる
  **決定論的なStructural Validator**で行い、意味理解を要する新しい
  Runtime LLM Checkerは追加しない
- **実装**: [er008_shared_point_blueprint_01.py](er008_shared_point_blueprint_01.py)(Schema・prompt構築)・
  [er008_point_blueprint_validator_01.py](er008_point_blueprint_validator_01.py)(Structural Validator)を新設し、
  既存Writer/Support Pipeline(4ファイル)へ全てオプション引数として
  配線した(Blueprint未指定時は既存Topicと完全に同一の挙動、既存
  No.1〜6を含む全既存Topicへの影響ゼロを確認済み)
- **検証範囲(重要な限定)**: fixture(18件、タスク仕様指定の6件含む)は
  全PASS。No.4〜6については、既存Ledgerと実記事本文を手作業で突き
  合わせた**後付けBlueprintによる机上Simulation**を行い、Validatorが
  No.4を正しくPASSさせ、No.5・No.6の実際の不整合を正確に検出する
  ことを確認した。**ただし、Blueprint生成・Writer/Comment生成の実LLM
  呼び出しによる検証(承認が必要な新規有料API呼び出し)は今回実施して
  いない**。「LLMが実際にBlueprintの制約へどこまで従うか」という
  価値仮説の核心部分は、次段階の検証を待つ
- **今回実施しなかったこと**: 有料Writer APIによる新規記事生成、
  新規TTS/ASR生成、既存No.1〜6記事の一括再生成、新しいRuntime LLM
  Checkerの追加、Production仕様(CURRENT_SPEC.md)への正式反映(実LLM
  検証前のため時期尚早と判断)
- **根拠レポート**: ER-008-POINT-BLUEPRINT-01完了報告、OPEN_ITEMS.md
  OPEN-64(本Decisionにより新規記録)
- **影響するCURRENT_SPEC項目**: なし(実LLM検証前のため今回は追加
  しない、次段階完了後に正式仕様化を検討する)

## ER-008-N7-SHARED-POINT-BLUEPRINT-3LEVEL-PILOT-01(2026-08-25)

- **Decision**: Shared Point Blueprint機構(A2/B1 Point Structure
  Semantic Alignment)を、新規Topic No.7「Assigned Desks Are Back in
  Some Offices」で初めて実LLM・実音声で検証する。Production採用の
  正式決定は行わない(タスク仕様通り、ユーザーが比較試聴Artifactを
  聴取した後に別途判断する)
- **背景**: 前タスクでBlueprint機構自体は実装済みだったが、実LLM
  生成・実Writer/Comment生成・実音声による検証はまだ行われておらず、
  「Blueprintの制約へLLMがどこまで従うか」という中心的な価値仮説が
  未検証のままだった
- **実施内容**: Research(実Web調査3件)→Evidence Pack/VFL(Fact
  F-001〜F-012)→Shared Point Blueprint(実LLM初回生成)→A2/B1
  Writer(Blueprint使用)→Fact Check/Ledger Deviation→Support
  (B1 Comment 3/4はcomment_anchor使用)→TTS(今回のみ同期モード、
  DEV/VALIDATION限定)→Assembly、を全て実際のAPI呼び出しで実行した。
  加えて、B1/A2の既存完成音声を新規TTS無しで組み合わせる
  「Middle/Bridge」音声組み立てをPilot専用スクリプトとして新規実装した
- **結果**: Point Oneはfact_id完全一致、Point Twoは必須factで一致
  (補助factの選択にA2がoptional_b1_fact_idを使う軽微な逸脱があったが
  内容矛盾やネタバレは生じなかった)。B1 Comment 1〜4は全てA2本文へ
  接続しても自然に成立することを確認した。Middle音声は新規TTS/ASR
  0件で完成した。A2側2segment(preview/comment_1)は、ER-007で既に
  開示済みのJA ASR「後」異読み限界により機械検証未合格のまま採用され
  ており、人間による聴取確認が必要
- **今回実施しなかったこと**: Production Level追加、Level名称決定、
  UI変更、Subscription仕様決定、全既存Topicへの展開。CURRENT_SPECの
  Production TTS標準(Batch API)は変更していない(同期TTSは今回限りの
  DEV/VALIDATION実行)
- **根拠レポート**: ER-008-N7-SHARED-POINT-BLUEPRINT-3LEVEL-PILOT-01
  完了報告、OPEN_ITEMS.md OPEN-64、比較試聴Artifact
  (https://claude.ai/code/artifact/de5ca386-8f04-470d-926b-edcb579a58d7)
- **影響するCURRENT_SPEC項目**: なし(Production採用の正式決定を今回
  行っていないため、CURRENT_SPECへの反映はユーザーの試聴・判断後とする)

## ER-008-N7-MIDDLE-SPEC-STORY-BALANCE-KEYPHRASE-AUDIT-01(2026-08-25)

- **Decision**: Middleの仕様を「A2 storyをベースにB1 supportを足したもの」
  から「B1をベースに、本文系7箇所(Full Story Part1/2、Point One/Two見出し
  +本文、In One Line)だけをA2に差し替えたもの」へ再定義し、実装をこれに
  合わせて作り直した。Key Phrase(英語phrase・構造)は今後B1のものを使う
  (前タスクの「A2のKey Phraseを使う」という推奨を本タスクの仕様指示により
  覆した)。Production採用の正式決定は今回も行わない(引き続きPilot段階)
- **背景**: 前タスクで実装したMiddleは「A2ベースにB1のsupportを差し込む」
  形だったが、ユーザーからMiddleは「基本B1、ニュース本文だけA2」という
  逆方向の設計であるべきという指示があった。またNo.7のA2 Full Storyが
  Part1=38語と短く、Middleにも影響することが判明した。加えてKey Phraseの
  番号読み上げ→phraseの間のpauseがA2よりB1の方が長く感じるという指摘が
  あった
- **実施内容(3件)**:
  1. Middle組み立てを`er003_v1_n3_01_assemble.py`の`build_b1_timeline()`
     をそのまま使う形に全面書き換え。B1の`apply_b1_gain()`出力を土台に
     Story系7箇所だけA2音源(B1のtarget_rmsへ再gain)へ差し替える方式とし、
     独立した日本語タイトルsegmentは廃止(B1の構造に元々存在しないため)
  2. No.4〜7のFull Story Part1/2語数を実測。No.4〜6はA2 212〜300語・
     B1 224〜302語で安定していたのに対し、No.7はA2 102語(Part1=38語)・
     B1 124語と突出して短く、構造的な問題ではなく単発の外れ値と判断。
     Evidence(Fact)を増やさず、状況描写・つなぎ等の物語技法のみで
     No.7 A2 Full StoryをPart1=99語/Part2=70語(計169語)へ拡張した。
     拡張1回目でLedger未根拠の主張が2件混入したため、該当箇所のみを
     指定した2回目の修正LLM呼び出しで是正し、Ledger Deviation件数を
     拡張前と同じ4件(内容も同一カテゴリ)まで戻したことを確認した
  3. Key Phraseのpause差の原因を実測で特定。B1側の音源読み込み
     (`load_b1_sources()`)にA2側で既に行っていた`tight_speech_only()`
     によるsafety margin無音のtrimmingが抜けており、体感pauseがB1で
     0.600秒・A2で0.400秒と異なっていた(pause定数自体はA2/B1で完全に
     同一、`IMPLEMENTATION_DIFF`)。共有ProductionファイルへA2と同じ
     trimmingを追加して統一した(今後の全B1/Middle生成に影響する
     恒久修正)
- **結果**: No.7 A2/B1/Middleを全て再生成・再組み立てし、比較試聴
  Artifactを更新した。新規有料呼び出しはLLM4件(story拡張・是正・
  deviation再検証2件)とTTS/ASR各2件(該当2segmentのみ再生成)の計
  約$0.05(¥8)。Middle自体は新規TTS/ASR 0件のまま。全体回帰テストは
  1774/1775 PASS(既知のharness自己テストの1件のみ、影響なし)
- **今回実施しなかったこと**: Middleの正式Level名称決定、UI追加、
  Pricing変更、No.8生成、Full Story語数の下限をPromptへ機械的に
  ハードコードすること(下限の目安はユーザーへの提案に留め、独断で
  仕様化はしていない)
- **根拠レポート**: ER-008-N7-MIDDLE-SPEC-STORY-BALANCE-KEYPHRASE-AUDIT-01
  完了報告、比較試聴Artifact
  (https://claude.ai/code/artifact/de5ca386-8f04-470d-926b-edcb579a58d7)
- **影響するCURRENT_SPEC項目**: なし(Production採用の正式決定を今回も
  行っていないため、CURRENT_SPECへの反映はユーザーの試聴・判断後とする)

## ER-008-N7-BASELINE-RESET-AND-MIDDLE-DEFER-01(2026-08-25)

- **Decision**: No.7「Assigned Desks Are Back in Some Offices」を、Middle
  Pilot検証(ER-008-N7-SHARED-POINT-BLUEPRINT-3LEVEL-PILOT-01/ER-008-N7-
  MIDDLE-SPEC-STORY-BALANCE-KEYPHRASE-AUDIT-01)以前の正式Fixed A2/B1
  Production仕様だけを使ってB1/A2の2版として再生成した(Shared Point
  Blueprint・comment anchor制約・Full Story延長処理・Key Phrase pause
  調整のいずれも不使用)。Middle/Bridgeは`DEFERRED / FUTURE_CANDIDATE`
  として正式に保留し、今回は生成しない
- **背景**: Middle Pilot検証中に追加した複数の検証専用処理(Blueprint・
  comment anchor・Story延長・Key Phrase pause trimming)が、No.7の
  A2/B1本体にも影響していた。中間仕様を検討する前に、まず「素の正式
  Production仕様で生成した場合に、指摘されていた問題(本文が短い・
  本文とCommentの接続が不自然・Key Phraseのpauseが違う)が実際に
  再現するか」を切り分ける必要があった
- **実施内容**: Research(既存のVerified Fact Ledgerをそのまま再利用、
  Blueprintに依存しないため未再実行)→Writer(`blueprint=None`で
  `er006_pool_pilot_01_writer.py`を実行、既存Topicと完全に同一の挙動)
  →Support(`blueprint=None`でComment 3/4のcomment anchor制約なし)→
  TTS/ASR(検証速度優先で同期呼び出し、Batch API仕様は無変更)→Assembly、
  を全て実行した。加えて、前タスクでB1側のKey Phrase読み込みに追加した
  `tight_speech_only()`のtrimmingを、共有Productionファイル
  ([er003_v1_n3_01_assemble.py](er003_v1_n3_01_assemble.py))から一旦
  revertし、真の未修正Baseline挙動を計測した
- **結果(3つの疑いのある問題を個別に検証)**:
  1. **Full Story短さ問題**: 再現しなかった。BaselineのA2は
     Part1=87語/Part2=92語(計179語)、B1はPart1=111語/Part2=78語
     (計189語)で、いずれもNo.4〜6の実績レンジに近い。前回の
     Part1=38語という極端な短さは、その回のPilot固有の生成結果
     (単発の外れ値)であり、Baseline自体の構造的な問題ではないと判断
  2. **B1本文→Comment 2接続の不自然さ**: 再現した。B1 Comment 2が
     「are some companies moving away from shared desks?」と問いかけた
     直後に、Full Story Part 2の冒頭が「Now, some employers are asking
     a different question: should every desk be shared?」と、ほぼ同じ
     論点を再度問いかけており、重複した疑問形の接続になっている
  3. **Key Phrase pause差**: 再現した。番号読み上げ→Key Phrase本体の
     実測間隔は、A2が約0.47秒、B1が約0.75秒(差約0.28秒)。原因は
     ER-008-N7-MIDDLE-SPEC-STORY-BALANCE-KEYPHRASE-AUDIT-01と同じ
     (B1側の数字読み上げ音声・Key Phrase英語Component音声の両方に
     元々の余白無音が多く残っている、既存の共有静的音声ファイル間の
     差異)
  Fact/Ledger Deviationは、A2=5件(MAJOR3件)・B1=1件(MAJOR1件)で、
  No.4〜6の実績レンジ(総数1〜6件、MAJOR0〜2件)からA2のMAJOR数が
  やや高いが、明確な逸脱とまでは言えない範囲だった
- **STOPして新規対策を入れなかった項目**: 2.(B1本文→Comment接続)と
  3.(Key Phrase pause差)はいずれもBaselineで再現することを確認した
  時点でSTOPし、新しい修正は入れていない(タスク仕様の指示通り)。
  今後、正式仕様として対応するかどうかは別途ユーザー判断とする
- **Middle仕様の扱い**: `DEFERRED / FUTURE_CANDIDATE`として
  OPEN_ITEMS.md OPEN-64に正式記録。基本方針(B1がベース、本文系のみA2、
  Key PhraseもA2版を使う[前回Decisionから方針変更]、将来再開時の
  必須検証項目8点)を記録した。Shared Point Blueprint実装自体は削除
  せず、Production未採用・オプトインのまま保持する
- **今回実施しなかったこと**: Middle版生成、Middle正式Level化、Shared
  Point Blueprint Production採用、Full Story soft minimum追加、Key
  Phrase pause新規統一、B1 Comment prompt修正、No.8生成、UI変更、
  Pricing変更
- **根拠レポート**: ER-008-N7-BASELINE-RESET-AND-MIDDLE-DEFER-01完了
  報告、OPEN_ITEMS.md OPEN-64、比較試聴Artifact(B1/A2のみ、
  https://claude.ai/code/artifact/de5ca386-8f04-470d-926b-edcb579a58d7)
- **影響するCURRENT_SPEC項目**: なし。今回はNo.7を既存の正式仕様へ
  戻しただけであり、CURRENT_SPEC自体への変更はない。B1本文→Comment
  接続とKey Phrase pause差は、Baseline自体に元からある挙動として
  確認されたが、対応方針はユーザー判断待ちのため仕様変更はしていない

## ER-008-N7-CONTENT-AUDIO-QA-02(2026-08-26)

- **Decision**: No.7正式Baselineのユーザー試聴で見つかった5点を調査し、
  影響がPilotに閉じない2件のバグ(共有ProductionコードのValidator gap、
  Key Phrase音声のstaleファイル使用)を修正した。No.7自体はB1 Key
  Phrase 2の音声/gloss修正、A2 Key Phrase pauseの+0.1秒変更(B1は無変更)
  を適用。Evidence Density(spoken layerでの固有名詞・数字の扱い)は
  Production Promptへ未配線と判明したが、大規模なPrompt再設計は行わず
  提案のみでSTOPした。読み上げ速度は今回測定のみで変更していない
- **Part A: B1 Key Phrase不整合のroot cause**: 表示上は"compare poorly
  with"/"〜より見劣りする..."で正しかったが、実音声は2つの独立したバグの
  複合で食い違っていた。(1) 日本語glossの"〜"(項変数記法、ER-006-KP5-
  CANONICAL-BUG-01の既存検出ロジックが意図通り検出)によりTTS生成が
  STOPPEDし、diskに残っていた前回実行(別のKey Phraseセット)の古い
  音声がassembly時にそのまま使われていた。(2) 英語Componentの実音声は
  "with"が脱落した"Compare poorly"だったが、ASR一致判定
  (`er006_preprod_hardening_01_validation.py::classify_asr_match`)の
  「冠詞等のstopwordを除いた内容語だけを比較する」近道処理が、意味を
  持つ前置詞"with"も冠詞と同列にstopword扱いしていたため誤って
  NORMALIZED_MATCH判定していた(Validator gap)。修正: glossを
  "他と比べて見劣りする／他より劣る"へ書き換え、対象のstopword集合を
  冠詞(a/an/the)のみへ絞り込み、kp2の英語/日本語を実際に再生成し
  (両方とも正しい内容をASRで再確認済み)、B1を再組み立てした
- **Part A: 一般整合性checkの追加**: `er003_v1_n3_01_assemble.py`の
  `load_b1_sources()`/`load_a2_sources()`へ`verify_key_phrase_audio_
  integrity()`を追加。assembly直前に、今回の実行のtts_generation_
  results.jsonで各Key Phraseの英語/日本語生成が実際にOK
  (またはASR_VALIDATION_UNCERTAIN)だったかを確認し、STOPPED等の失敗が
  あれば明示的なエラーで停止する(diskに残った古い音声を黙って使う
  ことを防ぐ)。診断ファイルを書かない旧テーマ・別pipelineには影響
  しない(後方互換)
- **Part B: A2 Key Phrase pause**: ユーザー決定により、A2の番号読み上げ
  →Key Phrase本体の間だけ0.4秒→0.5秒(+0.1秒)へ変更(B1は0.4秒のまま
  無変更)。`er003_b1_p9a_audio.py::build_key_phrase_block()`へ
  `numbering_pause_seconds`引数を追加(既定None=既存動作、後方互換)。
  実WAV計測(No.7 A2 5件平均): 修正前は約0.41〜0.47秒、修正後は
  約0.51〜0.57秒(いずれも数字→英語間の実測、無音区間+pause定数+
  trim後の頭無音の合計)。将来Middle再開時はA2のKey Phraseをそのまま
  使う仕様(下記Part C-2参照)のため、この値も自動的に継承される
- **Part C: A2 Point One見出しの発音問題**: Point見出しもASR全文検証の
  対象であることを確認(`generate_english_segment_with_fallback`経由)。
  元音声は標準経路(ENGLISH_STYLE_PREFIX)がGemini側の一時的な500エラー
  で6回とも失敗し、fallbackの"minimal instruction"経路で生成された
  ものだった。OpenAI Primary ASRは"A desk can feel like a place..."と
  正しく書き起こし(NORMALIZED_MATCHでPASS)たが、Azure Secondary ASR
  で同じ音声を再確認すると"A desk can feel LITHA."と全く異なる書き起こし
  になった。Secondary ASR cascadeはPrimaryがmismatchを返した場合のみ
  起動する設計のため、Primaryが(内容的には正しい語を)書き起こして
  しまうこの種の発音品質問題は、既存の検証フローでは検知できない
  (ASRでは検知困難な発音品質問題、Validator側のバグではなく構造的
  限界)。同じ経路で再生成した候補は、今回は標準経路が成功し、
  Primary/Secondary両方で完全一致の書き起こしを得た。試聴Artifactに
  原音声と候補を並べて掲載し、採用可否はユーザー判断とする(自動置換
  はしていない)
- **Part D-1: Evidence Compression Production配線状態**: `NOT_WIRED`。
  実際のProduction Writer Prompt(`er003_v1_n3_01_articles_generate.py`
  の`B1_B_DIRECT_INSTRUCTION`/`A2_KAI1_INSTRUCTION`/`build_common_
  block`)には、"Evidence Compression"や固有名詞・研究者名・企業名を
  spoken layerで削減する指示は一切存在しない。唯一近い規定は
  「Spoken-first原則(数字の扱い)」だが、これは「Fact Ledgerの数字を
  恣意的に削らない」ことを明示しており、むしろ逆方向の原則である。
  過去のNo.7 Full Story延長タスクで使った"Evidence Compression"という
  言葉は、その場限りの手動編集方針であり、正式なProduction仕様
  (CURRENT_SPEC.md)にも一切記載がない
- **Part D-2/D-3: No.7の固有名詞・数字監査**: Full Story+Point One/Two
  中の主な固有名詞(Scotiabank・iCapital Network・Bisnow・Gensler・
  Korn Ferry・CBRE)は、いずれも「その名前を聞くこと自体がStory理解を
  改善する」基準を満たさず`COMPRESS`(Bisnow・Bisnowのイベント名は
  さらに弱く`REMOVE_FROM_SPOKEN`)。一方、87%/74%・80%/67%(Point One)、
  20%/「パンデミック前の2倍」(B1 Part2)、56%/40%・2023/2024・
  2026(Point Two)は、比較の核心そのものであり`KEEP`。改善案(最小、
  未実装): Production Promptへ「固有名詞(企業・研究機関・出版物名)は、
  その名前自体がStory理解に必要でない限りspoken scriptへ出さず、
  『ある調査』『複数の企業』等の一般化表現に置き換える」という1文を
  追加する案を提示するに留め、実際のPrompt改修は行っていない
  (大規模なPrompt再設計は今回のスコープ外、ユーザー判断待ち)
- **Part E: 読み上げ速度実測**: TTS Prompt・API呼び出しのいずれにも
  話速指定は存在しないことを確認(`er002_common.py::assert_no_wpm_
  specification()`により数値WPM指定が混入しないことをbuild時に
  assertで保証済み、Gemini API呼び出しにも`speaking_rate`等のパラメータ
  は渡していない)。A2/B1でスタイル指示文自体は完全に同一(レベル間の
  速度差指定は無し)。実測(実発話区間ベース、無音除外): A2平均
  138.8WPM(中央値142.3、Story平均152.55、Point平均118.55)、B1平均
  151.4WPM(中央値152.1、Story平均148.6、Point平均124.05)。過去に
  言及した135WPM案等は、正式採用された仕様ではなく現状の実測基準
  として扱っていない。今回は速度変更を行っていない
- **今回実施しなかったこと**: Middle再開、No.8生成、A2/B1読み上げ速度
  変更、Full Story length rule追加、Research Coverage Gate再開、ASR
  provider変更、TTS model変更、Evidence Density Prompt改修の実装
- **根拠レポート**: ER-008-N7-CONTENT-AUDIO-QA-02完了報告、比較試聴
  Artifact(https://claude.ai/code/artifact/de5ca386-8f04-470d-926b-edcb579a58d7)
- **影響するCURRENT_SPEC項目**: なし。Key Phrase pauseの数値・Evidence
  Density方針・読み上げ速度はいずれも正式仕様化されておらず、今回も
  CURRENT_SPECへの追加は行っていない(pause変更は実装済みだがNo.7限定の
  検証、方針としての正式採用は別途判断)

## ER-008-TTS-FALLBACK-AND-EVIDENCE-COMPRESSION-03(2026-08-26)

- **Decision**: 2テーマを独立に扱った。TTS fallback(minimal instruction
  fallback)は`INVESTIGATION`のまま、既存ログ解析中心で実態を調査し、
  対策案の提示に留めてProduction改修はしていない(詳細OPEN-66)。
  Evidence Compressionは、No.7を対象に実Writerでcandidate scriptを
  script-only(TTS/ASR無し)で実際に生成し、`VALIDATED_CANDIDATE /
  USER_REVIEW_REQUIRED`とした(詳細OPEN-65)。CURRENT_SPECのProduction
  Writer仕様・TTS標準経路のいずれも変更していない
- **TTS fallbackの主な発見**: (1) 導入経緯はcommit `a13d97c`
  (2026-08-08、ER-003-REPRO-01-MAIN、短い孤立フレーズでの
  hallucination対応)、CURRENT_SPEC.mdに`DECIDED`の正式仕様として記載
  済みだが、当時の受入条件は実質n=2のhallucination事例のみで、
  Gemini側の一時的障害(No.7のケース)は検証対象外だった。CURRENT_SPEC
  自身が「根本原因は未解明のまま」と明記している。(2) standardと
  fallbackの唯一の実質的な差はTTS instructionの文言で、fallbackは
  prosody・感情の起伏に関する指示を一切持たない1文のみ。(3) 過去ログ
  442 segment分析の結果、fallbackへ落ちるのは6.3%(28件)と稀だが、
  発動した場合の帰結はOK 25%・ASR_VALIDATION_UNCERTAIN 11%・
  **STOPPED(音声未生成)64%**であり、fallbackは「発動すればほぼ解決
  する安全網」ではない。(4) No.7の6連続失敗は全て同一のGemini
  `500 INTERNAL`エラーで、`LIKELY_PROVIDER_TRANSIENT`と判定できる
  runtime evidenceがある一方、過去ログ全体はtimeout・応答パース失敗も
  混在し`MIXED`。(5) 現行QAの弱点は、fallback経路のSecondary ASR
  cascadeがPrimary ASRの「entity-likeな不一致」でのみ起動する設計の
  ため、Primaryが見かけ上正しく書き起こしてしまう発音品質問題
  (No.7 point_one_heading)を検知できないこと。推奨(未実装)は
  Option 2「fallback発動時のみSecondary ASRを必須化」
- **Evidence Compressionの主な発見**: `er003_v1_n3_01_articles_
  generate.py::build_common_block()`へ`evidence_compression`引数
  (既定False、Production挙動は無変更)を追加し、No.7でcandidateを
  生成した。固有名詞(Scotiabank/iCapital Network/Bisnow/Gensler/
  Korn Ferry/CBRE)は全sectionで0件まで削減され、Point Oneの4つの
  比較%は1文の傾向表現へ圧縮、Point Twoの核心的な比較数値
  (56%/40%・2023/2024/2026)は維持された。Fact Check verdictは
  A2で変化なし、B1はREVIEW_REQUIRED→PASSへ改善した一方、**Ledger
  Deviationは B1でbaseline1件→candidate6件(新規MAJOR3件)と悪化**
  した。新規MAJOR逸脱には、元のcorrelational evidenceより踏み込んだ
  因果的表現("...because some offices are questioning the human
  cost of desk sharing")が含まれており、出典名を削っただけでなく
  主張自体がやや強まった可能性がある。これは「出典名を消しただけで
  Fact自体は安全」ではなく「Evidenceを削ったことで主張が強くなった」
  側に近い事例として明示的に記録し、Production採用の判断材料とする
- **今回実施しなかったこと**: TTS音声生成、A2速度変更、fallback
  Production改修、ASR Primary/Secondary入れ替え、Evidence
  Compression正式Production配線、Middle再開、No.8生成
- **根拠レポート**: ER-008-TTS-FALLBACK-AND-EVIDENCE-COMPRESSION-03
  完了報告、OPEN-65・OPEN-66、比較Artifact
  (https://claude.ai/code/artifact/33775f4c-6acb-4bc5-ad0f-6ed0b9959a06)
- **影響するCURRENT_SPEC項目**: なし。`evidence_compression`引数は
  既定Falseで実装したのみで、Production Writer仕様(CURRENT_SPEC.md)
  への追加・変更はしていない。TTS fallbackの既存記載(244行目・263行目)
  も今回は変更していない(調査結果を踏まえた改修は別タスクでの判断)

## ER-008-FALLBACK-TRIGGER-MITIGATION-AND-EVIDENCE-COMPRESSION-AB-04(2026-08-26)

- **Decision**: ユーザー承認済みの暫定対策として、fallback(minimal
  instruction)経由で生成された英語音声にSecondary ASR確認を必須化する
  変更をProductionへ正式配線した(`PRODUCTION_WIRED`)。fallback自体の
  根本再設計は`DEFERRED / AFTER USER VALIDATION`としてOPEN-67へ切り
  出した。Evidence Compressionは、強化したFact safety制約のもとで
  方式B(Compression-aware Writer)・方式C(Lossless Editor)をNo.7で
  比較し、方式Cを推奨として`VALIDATED_CANDIDATE / USER_REVIEW_
  REQUIRED`のまま記録した。CURRENT_SPECのProduction Writer既定Prompt
  は変更していない
- **fallback発動条件の確定**: 実コードを追跡し、Gemini 5xx/timeout/
  応答異常はいずれも`_call_tts_with_retry`内の同一Exception捕捉で
  扱われ、技術retry(既定1回)を経てそのTTS試行1回分の失敗として
  outer loop(既定6回)で再試行されること、ASR content mismatch/
  hallucinationは`classify_asr_match`のTRUE_CONTENT_MISMATCH/
  TTS_FAILURE分類でretry対象になること、entity-likeな不一致のみが
  Cascade(Primary#2→Secondary#1→Secondary#2)の対象になることを確認
  した。「6回」は同一standard prompt・同一voiceでの6回独立したフレッシュ
  TTS生成試行を意味し(ASR retryの回数ではない)、`max_attempts: int = 6`
  が現在の唯一の設定値(topic単位のチューニング機構は無い)
- **重大な追加発見(Part B)**: TTS生成の各試行は、ASR内容検証の前に
  `write_wav_float()`で無条件に音声ファイルをdisk上書きしているため、
  standard/fallbackとも全試行が尽きて最終的に`STOPPED`となった場合
  でも、disk上には最後の(未検証・却下された)音声がそのまま残る。
  Assembly側はtts_generation_results.jsonのstatusを一切確認せず
  このファイルを読み込むため、**無人Production量産でfallbackも失敗
  した場合、自動的には停止せず、未検証の音声を含んだままエピソードが
  完成する**ことを、No.6 Deliveryの実例(手動再実行スクリプト
  `resume_audio_n6.py`実行後もSTOPPEDのままだが完成済みwavが存在する)
  で確認した。この一般的なリスクへの対策(Key Phrase以外の全segment
  への適用)は今回のスコープ外とし、OPEN-67の一部として記録した
- **Secondary ASR必須化の実装**: `er006_secondary_asr_01.py::
  evaluate_attempt_with_cascade`/`evaluate_attempt_with_cascade_
  detail`へ`force_secondary`引数(既定False)を追加。standard path
  (`er003_v1_repro01_main_generate.py`の`generate_narration_
  snippet_verified_strict`)は無変更・追加コストゼロ。fallback path
  2箇所(`generate_key_phrase_component_verified`の内部fallbackループ、
  `er003_v1_crosslevel_audio_02_common.py::generate_english_
  segment_with_fallback`のfallbackループ)へ`force_secondary=True`を
  配線し、PrimaryがPASSしてもSecondaryが同意しない限り自動PASSしない
  ようにした。5件の受入テスト(standard無影響/両ASR一致でPASS/
  Secondary不一致で自動PASS阻止/Primary不一致時の既存Cascade維持/
  No.7実event fixture)を[er006_secondary_asr_01_test.py](er006_secondary_asr_01_test.py)
  へ追加し全PASSを確認、CURRENT_SPEC.mdを更新した
- **Evidence Compression 3方式比較**: 前回(ER-008-TTS-FALLBACK-AND-
  EVIDENCE-COMPRESSION-03)発見したB1候補の因果表現drift対策として、
  `EVIDENCE_COMPRESSION_BLOCK`へFact safety不変条件(相関→因果への
  変換禁止・scope拡張禁止・hedging削除禁止等)を明示追加した。方式B
  (Writer再生成)と、新規実装した方式C(Lossless Editor、Baseline
  記事をそのまま渡し軽量編集のみ許可する新規opt-in経路、
  `er008_evidence_compression_ab_04.py`)をNo.7で比較した結果、両方式
  とも因果強化表現の新規混入は0件(drift再発なし)を確認した。方式C
  は固有名詞削減の安定性が高く(全section・両levelで0件を達成)、
  Ledger DeviationもBaseline水準に近く、A2はFact Check verdictが
  PASSへ改善した。方式Bは実行ごとのばらつきが大きく(この回はA2で
  固有名詞が一部残った)、B1のLedger Deviationが1件→6件へ悪化した。
  **推奨は方式C**とした
- **今回実施しなかったこと**: Evidence CompressionのProduction採用、
  Evidence Compression音声生成、A2速度変更、A2 Point One音声差し替え、
  A2 Key Phrase pause追加、Middle再開、No.8生成、Primary/Secondary
  Provider入れ替え(※A2 Key Phrase pause追加・Point One修正音声・A2
  slightly slower TTSは次の音声生成タスクで実施予定、Open Itemから
  落とさない)
- **根拠レポート**: ER-008-FALLBACK-TRIGGER-MITIGATION-AND-EVIDENCE-
  COMPRESSION-AB-04完了報告、OPEN-65・OPEN-66・OPEN-67、比較Artifact
  (https://claude.ai/code/artifact/29af88f0-2849-480b-830d-3381c556f812)
- **影響するCURRENT_SPEC項目**: minimal instruction fallback(244行目、
  Secondary ASR必須化を追記、`PRODUCTION_WIRED`)。Evidence Compression
  ・Production Writer既定Promptは今回も変更していない

## ER-008-AUDIO-VALIDATION-GATE-AND-EVIDENCE-MAJOR-AUDIT-05(2026-08-26)

- **Decision**: ユーザー承認済み(`APPROVED_FOR_PRODUCTION`)のAudio
  Validation Gateを正式Productionへ配線した(`PRODUCTION_WIRED`)。
  未検証・stale・STOPPEDの音声がassemblyされる問題を、Key Phrase限定
  だった既存の仕組みを一般化して全segmentへ適用することで解消した。
  Evidence Compressionは、方式C(Lossless Editor)のB1で増えたLedger
  MAJOR逸脱1件ずつを精査し、いずれもBaselineの既存事項が重複計上
  されただけ(`VALIDATOR_FALSE_POSITIVE`)と判定した。引き続き
  `VALIDATED_CANDIDATE / USER_REVIEW_REQUIRED`のまま、Production
  採用はしていない
- **root cause**: 各TTS生成試行(`er003_b1_p9a_audio.py::generate_
  narration_snippet`他)はASR内容検証の前に`write_wav_float()`で
  無条件にファイルをdisk上書きするため、standard/fallbackとも全試行
  が失敗して最終`STOPPED`になっても、最後の(未検証・却下された)
  音声がそのままdiskに残る。Assembly側はファイルの存在だけで読み
  込んでいたため、QA未合格音声がProduction episodeへ混入しうる状態
  だった(No.6 Delivery・No.7 B1 Key Phrase 2で実例確認済み)
- **新仕様の設計**: 新しいmanifestファイルは作らず、既存の`tts_
  generation_results.json`(このrunの診断ファイル、既に全segment/Key
  Phraseの生成結果を含む)を正とする単一のgateへ統合した(重複実装を
  避ける)。各segmentをVALIDATED(status=OK)/HUMAN_APPROVED(ASR_
  VALIDATION_UNCERTAINだがcanonical_text一致の明示的承認記録あり)/
  UNVALIDATED/STOPPEDへ正規化し、`verify_episode_audio_validation_
  gate()`がassembly直前に全segmentを検査する。VALIDATED・HUMAN_
  APPROVED以外が1件でもあれば`EPISODE_BLOCKED_BY_AUDIO_VALIDATION`
  としてRuntimeErrorを送出し、assembly全体を中止する。Human Review
  用に`record_human_approval()`(segment名+canonical_textのsha256+
  承認日時を記録、textが変わったら承認は無効)を新設した。ファイルの
  temp/atomic-rename分離(タスク仕様のPart C推奨設計)は、既存の
  tts_generation_results.jsonベースのgateだけで受入テスト9件全てを
  満たせることを確認できたため、大規模な生成関数リファクタリングは
  見送り、gateによる防御を主とした
- **受入テスト**: standard PASS/final STOPPEDでblock/retry途中status
  でblock/current run STOPPEDならstale音声があってもblock(No.7 Key
  Phrase実例の直接再現)/fallback Secondary不一致でblock/fallback
  両ASR一致でPASS/Human Approved後はPASS/text変更後は旧承認が無効/
  1segmentだけ未検証でepisode全体block/No.6実データfixtureでblock、
  の10件全てPASS([er008_audio_validation_gate_05_test.py](er008_audio_validation_gate_05_test.py))
- **重大な追加発見(Part H)**: 現行Production経路を持つ全12テーマ×2
  レベル=24組を実際に新Gateで検査した結果、**22組が最低1segmentで
  blocked状態**(pool_n4_supermarket/b1bとpool_n5_cafes/a2の2組のみ
  現状クリーン)であることが判明した。既に組み立て済みのepisode wav
  ファイル自体は無変更だが、今後これらのテーマを再assemblyしようと
  した場合、新Gateにより明示的にブロックされる。No.7自体もfull_
  story_part1・point_oneがHuman Approval記録の無いASR_VALIDATION_
  UNCERTAINのままのため、次回音声タスク(A2 pause追加・Point One
  差し替え等)で再assemblyする際は、該当segmentの再生成または明示
  承認が必要になる
- **Evidence Compression方式C MAJOR精査**: B1でBaseline(Ledger
  MAJOR1件)→方式C(MAJOR2件)へ増加した点を1件ずつ精査した結果、
  新たにMAJORとして挙げられた2文はいずれもBaselineから一字一句
  変更されていない(byte単位で同一)ことを確認した。CBRE調査(F-008/
  F-009)を「wider/broader office market」と一般化する、Baselineに
  元々あった同一のscope越境が、Deviation Checkerの実行ごとの引用の
  まとめ方が非決定的なために今回はより多くの独立レコードとして数え
  られただけと判定した(`VALIDATOR_FALSE_POSITIVE`)。方式C自体の
  Production候補評価は総合して肯定的(固有名詞削減・数字負荷削減・
  Fact loss/追加なし・causal driftなし・英語は概ね自然)。一方、
  "one report"のような出典主体を消した結果の曖昧な言い回しは改善
  余地として新規記録した(OPEN-69)
- **今回実施しなかったこと**: Evidence CompressionのProduction採用、
  fallback根本再設計の実装(論点整理[OPEN-67]のみ)、既存22テーマの
  一括是正、A2 Key Phrase pause追加・Point One音声差し替え・A2読み
  上げ速度調整(次回音声タスクへ引継ぎ、OPEN-70)
- **根拠レポート**: ER-008-AUDIO-VALIDATION-GATE-AND-EVIDENCE-MAJOR-
  AUDIT-05完了報告、OPEN-65・OPEN-67・OPEN-68・OPEN-69・OPEN-70
- **影響するCURRENT_SPEC項目**: Audio Validation Gateを新規項目として
  「QA / Human Review」節へ追加(`DECIDED`/`PRODUCTION_WIRED`)。
  Evidence Compression・Production Writer既定Promptは今回も無変更

## ER-008-EVIDENCE-COMPRESSION-PROD-AND-N7-AUDIO-06(2026-08-26)

- **Decision**: Evidence Compression方式C(Lossless Editor)をユーザー
  が正式採用し、Production Writerパイプラインへ配線した(`APPROVED_
  FOR_PRODUCTION`→`PRODUCTION_WIRED`)。No.7 A2/B1を、この新Production
  経路(方式C+既存Audio Validation Gate)で実際に再生成し、`USER
  LISTENING READY`な完成候補音声とした。加えてA2のみ、(1) Key Phrase
  番号→phrase間のポーズをさらに+0.1秒(累計+0.2秒)、(2) Point One
  見出しの誤発音修正、(3) 自然言語による「わずかに遅く」ナレーション
  指示、の3点を配線した(B1・Key Phraseの速度は無変更)
- **方式Cの実装**: 新規`er003_v1_n3_01_evidence_compression_editor.py`
  に`run_lossless_editor()`を実装し、`er003_v1_n3_01_articles_
  generate.py::run_one_pattern()`内(Writer出力直後、Fact Check/
  Ledger Deviation Checkの前)へ組み込んだ(`apply_evidence_
  compression`引数、既定`True`)。Editorは「意味を保ったまま聴取負荷
  を下げる」工程に限定し、Fact追加/削除・相関→因果・確信度強化・
  hedging削除・scope拡張・比較/時間方向の変更・Point/Story構造変更を
  明示的に禁止するprompt設計とした(過去3回のAB/精査タスクで確立
  した不変条件リストを踏襲)。Method B(Compression-aware Writer、
  `evidence_compression`引数)は既定Falseのまま完全に別経路として
  維持した(混同防止のためdocstringへ明記)
- **Safety Gate運用**: No.7実データでのSafety Gate確認として、
  Writer出力直後の生原稿を`audit/pre_editor_article.md`へ保存し、
  Editor適用後に新規発生したLedger Deviationを1件ずつこの生原稿と
  突き合わせた。B1は8件中7件・A2は6件中大半がEditor適用前から存在
  する内容(Writer自身の一般化傾向)で、Editor起因の新規driftは
  「Korn Ferry says」→「One survey says」のような出典ラベルの言い
  換え(既知のOPEN-69と同種、軽微)に留まり、新規の意味的driftは
  確認されなかった
- **音声再生成での実運用確認**: 大規模音声生成中、A2 assemblyが
  `comment_4`の`STOPPED`によりAudio Validation Gateで実際に
  ブロックされた(便宜的なHuman Approvalでのバイパスは行わず、原因
  を精査)。原因は日本語ASRが正準テキストの漢数字「二つ」を常に
  算用数字「2つ」として書き起こす決定論的な不一致で、6標準+6
  fallback試行すべてが同一の`TRUE_CONTENT_MISMATCH`だった。
  `a2_support_texts.json`の該当テキストを実際のASR書き起こし表記
  (「2つ」)に合わせて修正し、該当segmentのみ再生成・ASR再検証
  (`asr_verified: True`)した上でGateを正当に通過させた
- **A2速度指示**: `er003_b1_p9a_audio.py`等4ファイルへ`style_prefix_
  override`引数を新設し、A2の対象5区分(Full Story Part1/2・Point
  One/Two・In One Line)へのみ`A2_ENGLISH_STYLE_PREFIX_SLOWER`
  (数値WPM/speed指定なし、既存の感情・自然さ指示は維持したまま追記)
  を適用した。fallback経路には適用しない設計とした。実測の結果、
  平均WPMは138.8→141.5とむしろ微増し、単体での明確な減速効果は
  確認できなかった。ただしMethod C適用+Writer新規生成でテキスト
  自体が旧baselineと完全に異なるため単純比較はできず、タスク仕様
  通り追加のprompt再調整はせずそのまま報告した(OPEN-32を訂正、
  過去の「135WPM」記述は未実装だった)
- **今回実施しなかったこと**: No.1〜6を含む既存22テーマへの方式C
  遡及適用・再生成(OPEN-68の方針通り、必要になったテーマのみ個別
  対応)、fallback根本再設計(OPEN-67、引き続き実ユーザー検証後まで
  凍結)、"one report"表現の改善(OPEN-69、LOW優先度のまま)、Support
  (Preview/Comment)への方式C効果の検証
- **根拠レポート**: ER-008-EVIDENCE-COMPRESSION-PROD-AND-N7-AUDIO-06
  完了報告、OPEN-32・OPEN-65・OPEN-68・OPEN-69・OPEN-67、No.7完成
  候補Artifact(https://claude.ai/code/artifact/de5ca386-8f04-470d-
  926b-edcb579a58d7)
- **影響するCURRENT_SPEC項目**: 「Evidence Compression(方式C、
  Lossless Editor)」「A2 Key Phrase pause(番号→phrase間)」「A2英語
  ナレーション速度指示」の3行を新規追加(いずれも`DECIDED`/
  `PRODUCTION_WIRED`)

## ER-008-B1-POINT2-FACT-FIX-AND-JA-NUMERAL-NORMALIZATION-07(2026-08-26)

- **Decision**: No.7 B1 Point Twoの"one desk per employee or fewer"を
  `FACT_ERROR`(CBRE調査の実際の方向と完全に逆)と判定し、"at least one
  desk per employee"へ修正した。同時に、A2 comment_4の「二つ」→「2つ」
  というASR都合のcanonical text書き換え(前タスクの暫定対応)を見直し、
  Validator側の限定的な同値正規化(助数詞「つ」直前の漢数字のみ)を
  実装した上で、canonical textを自然な表記「二つ」へ復元した
- **B1 Fact監査**: Evidence Pack(E-003-02)・Fact Ledger(F-008の`claim`
  欄)・Fact Ledger検証ノートは全て正しい方向("ratio of 1.0:1 or less"
  =従業員1人あたりデスク1台以上)を記録していたが、**VFL(F-008)自身の
  `conditions`欄**が、同じFactの`claim`欄と逆方向の言い換え("従業員1人
  につきデスク1台以下")になっていた。Writer出力の時点(Evidence
  Compression Editor適用前の`pre_editor_article.md`)で既に"or fewer"が
  存在しており、Editor由来ではなくWriter由来と判定した。同時に生成された
  A2側は同じF-008から独立に正しい"at least one desk per employee"を
  生成できていたため、単発のLLMサンプリング誤りであり、VFLの`conditions`
  欄の逆方向記述が誘因になった可能性が高いと判断した
- **Validatorが検知しなかった理由**: Fact Check(OpenAI web検索付き)は
  自らCBRE公式ページを検索・取得したが、検証ノート自体が記事と同じ
  逆方向の言い換え("従業員1人あたり1席以下の比率が…")をしてしまい、
  誤り同士が一致してすり抜けた。Ledger Deviation Checkはscope拡張・
  具体性追加型の逸脱検知を主眼としており、比較方向の反転そのものは
  対象にしていないため検知しなかった。既存の音声側Validator
  (`protected_check()`/`protected_check_ja()`)は「TTS音声がcanonical
  scriptと一致するか」の層であり、canonical script自体が誤っている
  ケースはそもそも対象範囲外であることを確認した(汎用的なscript対
  Source Fact比較方向Validatorは今回新設せず、OPEN-72として記録するに
  留めた。大規模Validator再設計は今回の非スコープ)
- **B1修正の反映**: `point_two` segmentのみ音声を再生成(NORMALIZED_MATCH、
  fallback不使用、初回試行でPASS)。Fact Checkを再実行し`REVIEW_REQUIRED`
  →`PASS`へ改善、Ledger Deviationを再実行し8件→6件(Point Two関連の
  新規逸脱なし、減少分はLLM実行ばらつきによるMINOR2件)。Audio
  Validation Gateを実PASSでB1/A2を再assemble(バイパスなし)
- **JA数字正規化**: `er007_ja_asr_validator_01.py`(長文用、31文字以上)
  ・`er003_audio_tts_asr_safety.py`(短いsegment用)双方に、助数詞「つ」
  の直前に来る単独漢数字(一〜九)だけを算用数字へ揃える限定的な同値
  正規化(`normalize_kanji_counter_numerals_ja()`)を実装した。「二十」
  「二回」等、助数詞「つ」が続かない漢数字は対象外のまま(既存の
  `_extract_numbers_ja()`/`protected_check_ja()`が単独漢数字を数字保護
  対象外としてきた設計思想[固有名詞的な語との誤判別リスク回避]を維持
  しつつ、助数詞という文脈が明確な場合のみ限定的に拡張した)。この
  過程で、OPEN-59が指摘していた「31文字以上のlong segmentは意味検証が
  構造的に発動しない」という`MATERIAL_VALIDATION_GAP`が、2026-08-25の
  ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01-WIRE-01で既に解消
  済み(全文diff方式の`classify_ja_asr_match()`がProduction配線済み)
  であることを、今回のNo.7実データ再生成で直接確認できたため、OPEN-59
  を`RESOLVED`へ更新した
- **今回実施しなかったこと**: VFL生成プロンプト自体への「`claim`と
  `conditions`の方向統一」指示追加(No.7個別修正のみ)、他テーマ(No.1〜
  6)への同種VFL方向不一致の横断監査、比較方向反転を検知する汎用
  Validatorの新設(OPEN-72として記録)、A2速度A/B(次タスクへ)
- **根拠レポート**: ER-008-B1-POINT2-FACT-FIX-AND-JA-NUMERAL-
  NORMALIZATION-07完了報告、OPEN-59・OPEN-71・OPEN-72・OPEN-73
- **影響するCURRENT_SPEC項目**: 「Validator(日本語)」行へ助数詞「つ」
  数字正規化を追記(`DECIDED`)

## ER-008-DIRECTIONAL-FACT-PRECHECK-08(2026-08-26)

- **Decision**: 前タスク(ER-008-B1-POINT2-FACT-FIX-AND-JA-NUMERAL-
  NORMALIZATION-07)で発見したB1 Point Two Fact誤り(more/fewer型の
  比較方向反転)を踏まえ、OPEN-72が指摘した「script対Source Factの
  比較方向を機械的に検知する汎用Validator」の本格実装は行わず、
  実ユーザー検証対象(当面No.7)向けの軽量・rule-based・新規LLM call
  なしの暫定チェックとして`er008_directional_fact_precheck_08.py`を
  実装し、Production記事生成経路(`run_one_pattern()`)へ既定Trueで
  配線した(`PRODUCTION_WIRED`、暫定策)。OPEN-72自体は削除せず
  `DEFERRED / AFTER USER VALIDATION`として維持する
- **設計**: Part B必須12カテゴリ(more/fewer、higher/lower、increase/
  decrease、rise/fall、up/down、at least/at most、above/below、
  before/after、earlier/later、more than/less than、doubled/halved、
  growth/decline)を、「magnitude(量の大小)」「temporal(時間の前後)」
  の2軸へ統合した。個別カテゴリを独立に対比するのではなく2軸へ統合
  することで、"increase"(Ledger側)と"rise"(script側)のような正しい
  同義表現を、カテゴリの違いを理由に誤って「比較不能」とせず正しく
  MATCH判定できる。各語には確度(high/low、2語以上のphraseや曖昧性の
  低い語はhigh、bare "up"/"down"等はlow)とカテゴリ(trend/threshold)
  を付与し、trend(increase/decrease等、同じ名前の量の時間変化)と
  threshold(at least/at most等、基準値との大小関係)を独立に評価する
  設計にした
- **重要な実データ発見(false negative、正直に記録)**: 実装直後、
  本タスクの発端となったNo.7 F-008(CBRE従業員・デスク比率)を実際の
  VFL/Fact Ledgerデータで検証したところ、Fact LedgerとscriptをNumber-
  anchorで自動対応付けするcross-artifact層(Ledger対script、VFLの
  `claim`対`conditions`欄)では、**誤りだった旧B1本文をMATCH、修正済み
  の正しい本文をPOTENTIAL_DIRECTION_REVERSALと判定し、正誤が完全に
  逆転する**ことを発見した。原因は、「比率」とその逆数に近い量(従業員
  1人あたりのデスク数)という、reciprocal(逆数)関係にある2つの主語を
  行き来するFactに対し、表層的な語("以下"等)の比較だけでは対象の
  違いを区別できないため。この発見を受け、trend/thresholdカテゴリを
  分離した上で、thresholdカテゴリのみの衝突はcross-artifact層で
  FAILへ格上げしない設計(`_downgrade_threshold_only_reversal()`)へ
  変更し、少なくとも「誤って正しい本文をブロックする」false positive
  は防いだ。ただし「誤った本文を見逃す」false negative(reciprocal-
  quantity型Factを検知できない)は解消しておらず、既知の限界として
  CURRENT_SPEC/OPEN-74へ明記した(隠さない)
- **Part G/H受入テスト**: `compare_direction()`単体(対象が明確な2文の
  直接比較)に対する23件のfixture(Part Hの10項目+trend/threshold
  分離の追加検証+No.7実データ回帰テスト)は全てPASS。No.7旧B1 Point
  Twoの誤り("one desk per employee or fewer")と正しいFact("at least
  one desk per employee")の直接比較は正しくPOTENTIAL_DIRECTION_
  REVERSALとして検知できる(対象=主語が明確な場合はrule-baseで確実に
  機能することの証明)
- **No.7実証**: No.7 B1/A2の実記事全体(article.md)に対して
  `audit_article_directional_facts()`を実行した結果、意図しない
  POTENTIAL_DIRECTION_REVERSAL(false positive)は0件、DIRECTION_
  REVIEW_REQUIRED(WARN)が3件(いずれも「片方にのみ方向表現がある」
  ケースで、実際の衝突ではない)。article生成の完成を誤ってブロック
  しない設計であることを実データで確認した
- **STOP条件の検討**: 「rule-basedでは安全に方向判定できない」に該当
  するか検討した結果、GENERAL(非reciprocal)な直接比較方向反転
  (Part G/Hの23件全て)については確実に機能するため全面STOPはせず、
  reciprocal-quantity型Factという**特定の狭いFactタイプに限定した
  既知の限界**として正直に報告する方針とした(Part D「false negative
  懸念」の報告項目で対応)
- **今回実施しなかったこと**: OPEN-72の本格対策(構造化comparator、
  VFL生成段階での方向保証、他テーマ横断監査)、`assert_no_directional_
  reversal()`gateの完成候補宣言プロセスへの明示的組み込み、A2速度A/B
  (次タスクへ)
- **根拠レポート**: ER-008-DIRECTIONAL-FACT-PRECHECK-08完了報告、
  OPEN-71・OPEN-72・OPEN-74
- **影響するCURRENT_SPEC項目**: 「QA / Human Review」節へ「Interim
  directional fact precheck for user-validation phase」行を新規追加
  (`DECIDED`/`PRODUCTION_WIRED`、暫定策と明記)

## ER-008-A2-SPEED-SAME-TEXT-ABC-09(2026-08-26)

- **Decision**: No.7 A2の英語ナレーション速度について、A(現行Production
  指示)・B(やや強めの減速指示)・C(Bよりもう一段強めの減速指示)を、
  Full Story Part 1のみ・本文/voice/model/segment境界を完全固定した
  same-text条件で比較生成した。**Production既定速度は今回変更しない**
  (前回タスクは記事本文自体がMethod C適用で変わっており、WPM比較として
  クリーンではなかったため、今回はその反省を踏まえた純粋比較のみを
  目的とした)。3候補ともstandard path・fallback不使用でASR PASSした
  が、**B・CともAより速い結果**(B: +11.2%、C: +2.0%)となり、意図した
  減速方向とは逆だった。採用可否はユーザーの試聴判断へ委ねる
- **same-text条件の担保**: 本文はNo.7 A2 `parts.json`のpart1と一字一句
  同一であることを直接diffで確認した。model(`gemini-2.5-pro-preview-
  tts`)・voice(`Aoede`)は`style_prefix_override`を通しても不変(コード
  上、これらはstyle_prefix_overrideの有無に関わらず固定値として渡され
  る設計であることを確認済み)。fallback回避は「fallbackへ自動遷移する
  ラッパー関数を呼ばず、standard path関数(`generate_narration_snippet_
  verified_strict`)を直接呼ぶ」という構造的な設計で保証した(事後
  チェックではなく、fallbackへ物理的に到達し得ない呼び出し経路)
- **実測結果**(active-speech WPM、word_count=70固定):
  A=142.22 WPM(30.01s/29.53s active)、B=158.19 WPM(27.16s/26.55s)、
  C=145.07 WPM(29.49s/28.95s)。3候補ともPrimary ASR一発PASS(A:
  NORMALIZED_MATCH、B・C: EXACT_MATCH、retry 0回)
- **STOP条件の該当判断**: タスク仕様Part Kの「Cでも速度差がほぼ出ない」
  に該当すると判断した(C はAよりむしろ2%速く、B は11%速い。意図した
  減速方向へは3候補とも動いていない)。ただし「same-text条件が崩れる」
  「fallback発動」「B/Cで不自然なprosodyが明らか」「A/B/C以外のProd
  仕様変更が必要」には該当しないため、実装・比較自体は完了させ、結果を
  正直に提示した上でユーザー判断を仰ぐ方針とした(勝手にB/Cを再調整
  したり追加trialを重ねたりはしていない、Part K「不要な再実行は禁止」)
- **Artifact**: A/B/C音声・WPM・instruction差分を並べた試聴比較ページを
  公開した(https://claude.ai/code/artifact/cc667002-0be4-4e02-a7df-
  82f744eee0c9)。Claude側からの推奨候補は提示していない(仕様書Part I
  「最終判断はユーザー」)
- **OPEN-72/OPEN-74確認(Part J)**: 実施前に状態を確認し、OPEN-72は
  `DEFERRED / AFTER USER VALIDATION`のまま(変更なし)、OPEN-74には
  「補助的警告機能であり、Fact方向の安全性を保証するものではない」
  という明記が不足していたため、OPEN_ITEMS.md/CURRENT_SPEC.mdへ追記
  した(コードは変更していない、ドキュメントのみ)
- **今回実施しなかったこと**: Production速度既定の変更、B/C以外の追加
  候補生成、Writer/Editor/Fact Checkの再実行、Full Story Part 1以外の
  segmentでのA/B/C比較(Part K「Full Story Part 1のみ3候補」に限定)
- **根拠レポート**: ER-008-A2-SPEED-SAME-TEXT-ABC-09完了報告、
  比較Artifact(上記URL)
- **影響するCURRENT_SPEC項目**: 「A2英語ナレーション速度指示」行は
  今回変更していない(Production既定は前タスクのA相当のまま)。
  「Interim directional fact precheck for user-validation phase」行へ
  「安全保証ではない」を明記(`DECIDED`のまま、内容のみ補強)

## ER-008-A2-TIMESTRETCH-ABC-10(2026-08-26)

- **Decision**: 前タスク(ER-008-A2-SPEED-SAME-TEXT-ABC-09)で自然言語の
  TTS速度指示がsame-text条件下でも安定して機能しなかった(B/CともA
  より速くなった)ことを受け、既存のNo.7 A2 Full Story Part 1完成音声
  (新規TTS生成なし)に対し、FFmpegの`atempo`フィルタ(pitch-preserving
  time-stretch)で3%/6%/9%の機械的な減速を適用し、0%(元音声)と
  合わせて4条件を比較した。**ステータスは`VALIDATION_ONLY`**、
  Production Audio Pipelineへは配線していない。採用可否はユーザーの
  試聴判断へ委ねる
- **手法**: `imageio-ffmpeg`パッケージが提供する静的FFmpegバイナリ
  (7.1、`--enable-librubberband`付きだが今回はRubber Bandではなく
  ffmpeg標準の`atempo`のみ使用、Part Iの「Rubber Band等は今回試さない」
  に準拠)を使用。単純なsample-rate変更(pitchが下がる)は明示的に
  使わず、`atempo=1/(1+slowdown/100)`で再生時間だけを伸ばした
- **実測結果**(word_count=70固定、active-speech WPM):
  A(0%)=147.7 WPM(28.89s)、B(3%目標)=143.5 WPM(実測減速2.96%、
  29.75s)、C(6%目標)=139.4 WPM(実測5.96%、30.61s)、D(9%目標)=
  135.6 WPM(実測8.95%、31.48s)。目標値と実測値の差は0.05〜0.04ポイント
  と極めて小さく、自然言語Promptより大幅に予測可能・制御可能である
  ことを確認した
- **pitch維持確認**: 追加依存を増やさないため、numpy/scipyのみで
  自己相関法による簡易F0(基本周波数)推定を実装した。元音声216.2Hz
  に対し、3/6/9%いずれも214.3Hz(-0.9%)で実質不変だった。単純な
  sample-rate変更であれば速度低下率とほぼ同じ割合(9%なら約8-9%)で
  pitchも下がるはずであり、これが起きなかったことが、genuinely
  pitch-preservingであることの直接的な証拠になる
- **内容・品質確認**: 4条件ともPrimary ASR(OpenAI)で`NORMALIZED_MATCH`
  となり、time-stretch処理による内容破損は確認されなかった。peak
  level(0.699〜0.700)・RMS(0.0723〜0.0738)・クリッピング検出(全て
  0サンプル)も4条件でほぼ同一であり、レベル面の異常は見られなかった。
  ただし「声がこもる」「金属的」「子音の不自然さ」等の主観的な音質
  劣化はASR/レベル測定では検知できないため、最終判断はユーザー試聴に
  委ねた(Part E自体がそう明記している)
- **Claudeからの提案**: 6%(C、約139 WPM)を、前タスクで参考範囲として
  挙がっていた135〜140 WPM帯に収まること・time-stretch比率が控えめで
  WSOLA系アルゴリズムの劣化リスクが小さいと見られることを根拠に、
  検討の出発点として提示した。ただし決定はしていない(Part G「最終
  決定はユーザー」)
- **Artifact**: 0/3/6/9%の4条件を並べた試聴比較ページを公開した
  (https://claude.ai/code/artifact/6efa0f4c-79a8-4d1e-a3ae-8c81d853a53d)。
  公開後、埋め込み音声4件が実際にpublishされたファイルへ正しく含まれて
  いることを直接検証した(前タスクでユーザーから「B/Cの音声が無いのでは」
  という指摘を受けたため、今回は公開前後の検証を徹底した)
- **今回実施しなかったこと**: Production Audio Pipelineへの配線
  (`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`化は次タスク以降、
  ユーザーが採用を決めた場合のみ)、Rubber Band等の別アルゴリズムでの
  比較、Full Story Part 1以外のsegmentへの適用、新規TTS再生成
- **根拠レポート**: ER-008-A2-TIMESTRETCH-ABC-10完了報告、OPEN-75、
  比較Artifact(上記URL)
- **影響するCURRENT_SPEC項目**: 「A2英語ナレーション速度(post-
  processing time-stretch案)」行を新規追加(`VALIDATION_ONLY`、
  Production未配線と明記)

## ER-008-A2-POSTPROCESS-SLOWDOWN-PROD-11(2026-08-26)

- **Decision**: ER-008-A2-TIMESTRETCH-ABC-10でユーザーが試聴の上6%
  time-stretchを正式採用したことを受け、Production A2音声パイプライン
  へ配線した(`APPROVED_FOR_PRODUCTION`→`PRODUCTION_WIRED`)。新規
  `er008_a2_postprocess_slowdown_01.py`(FFmpeg `atempo`、既定6%)を
  作成し、`er003_v1_n3_01_tts_generate.py::generate_a2_segments()`の
  A2英語7segment(point_one_heading/point_two_heading/full_story_
  part1/full_story_part2/point_one/point_two/in_one_line)全てへ配線
  した
- **既存instructionとの関係(重要な設計判断)**: 実装の途中で、既存の
  自然言語「わずかに遅く」instruction(`A2_ENGLISH_STYLE_PREFIX_
  SLOWER`)を6% time-stretchへの置き換えとして除去しようとしたが、
  これは誤りだったため撤回した。ユーザーが実際に試聴・承認した音声
  (ER-008-A2-TIMESTRETCH-ABC-10)は「既存のinstructionで生成された
  現行Production音声」に6% time-stretchを重ねたものであり、
  instructionを除去した音声ではない。instruction単体の効果がsame-
  text比較(ABC-09)で不安定だったことは、instructionを外してよい
  理由にはならない(ユーザーが承認したのはinstruction込みの組み合わせ)。
  この誤りは、trim_info不整合のバグ修正作業中に自分自身の実装ログを
  見直す過程で発見し、ユーザーへの追加確認なしに撤回・修正した
  (承認された仕様の逸脱であり、単純な実装バグと同種の扱いとした)
- **trim_infoの不整合修正**: post-process(time-stretch)適用後も
  `tts_generation_results.json`の`trim_info`/`duration_seconds`が
  slowdown適用前の値のままになっていた(実際の最終音声ファイルとの
  食い違い)ことに気付き、time-stretch比率で比例配分して実際の長さと
  一致させる修正を`apply_a2_slowdown_postprocess()`へ組み込んだ
- **post-process後ASR再検証とretry機構**: post-process後の音声を
  実際にASRで再検証する設計にした結果、No.7実データでの初回実行時に
  2/7 segment(`point_one`・`in_one_line`)で、slowdown**前**は正しく
  ASR一致していたのに、slowdown**後**の音声だけがASR不一致になる
  事象を発見した(語尾の単数/複数混同、文脈的な近縁語への誤認識等)。
  これはtime-stretchが内容そのものを変えたのではなく、微妙なタイミング
  変化がASRの認識精度をわずかに下げることがあるためと考えられる。
  既存の「未検証音声を黙ってPASSさせない」という方針を踏まえ、
  post-process後の再検証が不一致の場合は通常ペースから取り直す
  (最大3回)retry機構を`generate_a2_segment_with_slowdown()`へ追加
  した。No.7本番データへ適用した結果、初回不一致だった`point_one`は
  1回のretryで解消し、最終的に7segment全てがstatus=OKとなった
- **No.7実データへの反映**: 7segment全てを実際にこの新経路で再生成し、
  実測減速率5.5〜6.0%(目標6%に近い)を確認、Audio Validation Gateを
  実PASSでA2を再assemble(325.905秒)した。B1は完全に無変更のまま
- **今回実施しなかったこと**: 他21テーマ(No.1〜6含む)への遡及適用
  (必要になった時点で個別対応する既存方針[OPEN-68]を踏襲)、Middle
  再開(現状DEFERREDのまま)、"_original.wav"の実際の再利用先の実装
  (仕組みとしては用意したが、Middle自体が動いていないため未使用)
- **根拠レポート**: ER-008-A2-POSTPROCESS-SLOWDOWN-PROD-11完了報告、
  OPEN-75・OPEN-76
- **影響するCURRENT_SPEC項目**: 「A2英語ナレーション速度(post-
  processing time-stretch)」行を`VALIDATION_ONLY`→`DECIDED`
  (`PRODUCTION_WIRED`)へ更新

## ER-009-JA-FOREIGN-TOKEN-GATE-01(2026-08-26)

- **Decision**: Pool Topic No.4(pool_n4_supermarket)を最新のA2 6%
  slowdown/Audio Validation Gate仕様へ揃える作業中、A2 comment_2が
  ASR_VALIDATION_UNCERTAIN(Human Review待ち)のままGateをブロックして
  いることが判明した。ユーザーが実際に音声を試聴し、原因を確認した上で
  台本(comment_2)を修正・再生成することを承認し、あわせて同種の問題を
  今後検出する仕組み(4分類ゲート)の新規実装を指示した。両方を実施し、
  検出ロジックを`er003_audio_tts_asr_safety.py`(既存のTTS/ASR共通安全
  部品モジュール)へ新設・Production配線した(`PRODUCTION_WIRED`)
- **root cause**: A2 comment_2のJapanese canonical textに、制作内部の
  章番号ラベル「Part 1」がリスナー向け日本語のまま残っていた
  ("Part 1では、店が売り場の配置を変え…")。TTS自体は正しく「パート1」
  と発話していたが、Japanese ASR(Primary OpenAI×2・Secondary Azure×2
  の4段Cascade全て)は文中の英字表記をローマ字のまま書き起こすことが
  ほぼ無いため、canonical text側の「Part 1」とASR書き起こし「パート1」
  が構造的に一致し得ず、旧STOPPED時12回+今回2回の計14回の試行全てで
  Human Review待ちへ回っていた。音声自体は正しく発話されており、
  ASR/TTS側の技術的不具合ではなく、「制作都合の内部ラベルをリスナー
  向け日本語にそのまま残した」という編集上の問題だったと判定した
- **台本修正**: comment_2を「物語の前半では、店が売り場の配置を変え、
  買い物客が最初に見る商品を変えたことを聞きました。では、その後、
  商品の売れ方はどう変わったのでしょうか。」へ修正した(「Part 1」を
  「物語の前半」へ言い換え、他の意味・情報・Fact内容は一切変更して
  いない)。B1(`b1_support_texts.json`)は同種の内部ラベル漏れが無い
  ことを確認済み(B1 Comment/Previewは日本語ではなくeasy Englishの
  ため、そもそも対象外)。A2側の他のJapanese文言(preview/comment_1・
  3・4/japanese_title/Key Phrase gloss5件)も同じ観点で確認し、他に
  内部ラベルは見つからなかった
- **新設ゲートの設計**: `classify_foreign_tokens_in_japanese_text()`
  (rule-based、新規LLM呼び出しなし、OPEN-72/ER-008-DIRECTIONAL-FACT-
  PRECHECK-08と同じ「確信が持てない場合は無理に自動判定しない」思想を
  踏襲)を新設した。日本語canonical text中の英字・数字混じりのトークン
  を、TTSへ渡す前に4分類へ振り分ける:
  (1) `NEEDS_JAPANESE_PARAPHRASE` — 「Part 1」「Point 2」等の制作内部
  segment名・章番号ラベル(ASCII英数字の前後だけを見るnegative
  lookaroundで検出、Python re のUnicode `\b`が漢字/かなも「単語文字」と
  みなす既知の落とし穴を回避)
  (2) `READING_DICTIONARY` — `DEFAULT_JA_READING_DICTIONARY`(小規模な
  組み込み辞書)に登録済みの定着した略語・固有名詞
  (3) `ENGLISH_PRONUNCIATION` — 呼び出し側が渡した`known_key_phrase_
  terms`(その記事のKey Phrase英語表現[used_form])そのものが含まれる
  箇所。渡さない場合はこの分類は行われない
  (4) `HUMAN_REVIEW` — 上記いずれにも機械的な確信を持って分類できない
  もの。既存のASR Cascade human_review_queue.jsonlと同じ思想で、
  `er009_output/ja_foreign_token_gate_01/human_review_queue.jsonl`へ
  明示的にレビュー待ちとして記録する
  過検知でProduction全体を止めないため、TTS呼び出し自体をブロックする
  のはカテゴリ4のみに限定した(既存の`detect_gloss_placeholder_
  notation()`と同じ「ブロック対象は確信が持てるケースに限定する」設計)。
  カテゴリ1〜3は検出・記録に留め、生成そのものは止めない
- **配線**: `er003_v1_n3_01_tts_generate.py`の日本語TTS入口2箇所
  (B1: `generate_charon_japanese_with_reading_safety()`、A2:
  `generate_a2_japanese_with_reading_safety()`)の先頭、既存の
  `detect_gloss_placeholder_notation()`チェックの直後へ追加した。A2側は
  `generate_a2_japanese_with_fallback()`(標準+minimal instruction
  fallbackの両方を内包)を呼び出す前の1箇所でチェックするため、2つの
  経路を重複実装なしでカバーできる。既存のKey Phrase日本語gloss呼び出し
  (B1 kp_ja_charon・A2 meaning_N、いずれも`generate_a2_segments()`/
  `generate_b1_segments()`内)は、新設した`known_key_phrase_terms`
  引数へ`[used_form]`を渡すよう更新し、Key Phrase自身の英語表現が
  gloss中に現れてもHUMAN_REVIEWへ誤って回らないようにした
- **受入テスト**: `er009_ja_foreign_token_gate_01_test_01.py`(13件、
  全PASS)。No.4実例("Part 1"検出→NEEDS_JAPANESE_PARAPHRASE・修正後は
  検出0件)、Point/Comment/Section/Step等のラベル変種、読み方辞書
  ヒット(Wi-Fi)、Key Phrase表現の意図的な英語発話判定(渡す/渡さない
  両ケース)、未知の外来語トークンのHUMAN_REVIEW判定、既存の助数詞・
  年号・漢数字パターンでの誤検知が無いこと(OPEN-73実例を含む)、No.4
  A2の他の全Japanese文言での誤検知が無いこと、B1/A2の日本語TTS入口が
  HUMAN_REVIEW時に実際のTTS呼び出し前でSTOPPEDになることを確認した
- **No.4実データへの適用**: 新設ゲートをNo.4 A2の全Japanese文言
  (preview/comment_1〜4/japanese_title/Key Phrase gloss5件、計10件)へ
  実行した結果、修正前はcomment_2の「Part 1」1件のみNEEDS_JAPANESE_
  PARAPHRASEとして検出され、他9件は検出0件だった。comment_2修正後は
  全10件で検出0件を確認した。修正後のcomment_2を実際に再生成した結果、
  Primary ASRで一発一致(fallback不使用、`status=OK`)を確認し、A2の
  全14 segmentがVALIDATED状態になったことを確認した上でAudio
  Validation Gateを実PASSし、A2を再assemble(376.741秒、clipping無し)
  した。B1(b1b)は無変更のままGate実PASSを再確認した
- **既存回帰テストへの影響**: `run_project_regression.py`実行時、
  `er003_test_p2j_investigate.py::CollectionCountTests::test_combined_
  equals_sum_of_er002_and_er003`が1件failした(`1820 != 1757`)。原因を
  切り分けたところ、本タスクの新規テストファイルを一時的に取り除いても
  同じ失敗(`1807 != 1757`)が再現することを確認しており、**本タスクが
  作った新規の退行ではなく、er007/er008系テストファイルが`er0XX_test_
  *.py`(prefix直後に`_test_`が続く命名)ではなく`er0XX_<説明>_test_
  NN.py`という別の命名規則を使うようになった時点から既に存在していた
  当該meta-test(prefix別再集計ロジック)側の前提崩れ**と判定した。この
  1件を除く1819件は全てPASS。本件は今回のスコープ外として着手せず、
  Open Item化した(下記OPEN-77)
- **今回実施しなかったこと**: 既存22テーマ全体への遡及適用(No.4以外は
  未確認、OPEN-68の既存方針に準拠し必要になった時点で個別対応)、
  `test_combined_equals_sum_of_er002_and_er003`自体の修正(pre-existing
  かつ本タスクのスコープ外と判断、Open Item化のみ)
- **根拠レポート**: ER-009-JA-FOREIGN-TOKEN-GATE-01完了報告、OPEN-77
- **影響するCURRENT_SPEC項目**: Cross-level仕様節へ「日本語解説・
  Comment文での制作内部ラベル禁止」を新規追加(`DECIDED`)。QA/Human
  Review節へ「日本語canonical textの外来語/制作内部ラベル検出(4分類
  ゲート)」を新規追加(`DECIDED`、`PRODUCTION_WIRED`)

## ER-010-ENTITY-PHONETIC-CORROBORATION-01 / ER-010-DATE-SPOKEN-FORM-POINT-FIX-01(2026-08-27)

- **Decision**: No.5(pool_n5_cafes)B1の未解決2件(comment_4の意味
  不整合、full_story_part1/2のSTOPPED)を解消した。(1) comment_4を
  「方針の明確さ」テーマへ言い換え・再生成(OPEN-63対応)。(2) 固有
  名詞ASR表記揺れの軽量音韻類似度チェック(entity phonetic
  corroboration)を新規実装しfull_story_part1を解決。(3) 日付の
  TTS誤読(full_story_part2)をpoint fixで解決し、副産物として発見した
  複合序数正規化バグも修正した
- **comment_4修正**: 「customers who work there may offer the café
  more than their payment」(B1自身のpoint_two_bodyを要約した文だが、
  A2 Point Two・B1自身のIn One Lineが共に「方針の明確さ」テーマで
  締めており、この論点をどちらも引き継いでいなかった。OPEN-63で
  既に指摘済み)を、「how clearly a café sets its policy can shape
  whether both workers and social customers feel welcome」へ言い換えた
  (point_two_body・in_one_line・A2側は無変更)。再生成・ASR再検証で
  `status=OK`を確認
- **full_story_part1のroot cause**: 研究者名"L. Mimoun and A. Gruen"
  が英語ASRにとって馴染みの薄い固有名詞であり、現行Production Cascade
  (`news_tail_fix.generate_news_narration_wide_margin`、Secondary ASR
  Cascade込み)で正規の手順により再生成しても、`classify_asr_match()`
  の既存entity_only_diffs判定(固有名詞らしき語のみの音訳差は
  retryしても改善しないと判断してASR_VALIDATION_UNCERTAINへ)により
  Human Review行きになっていた。既存ロジックには「retryを止める」
  設計はあったが「自動PASSさせる」設計は無かった
- **調査した対策(a): reactive発音資料調査**: 全記事・全固有名詞への
  一律research工程は追加しないという方針のもと、実際に問題になった
  "L. Mimoun and A. Gruen"についてのみ一度だけWeb検索を行い、実在の
  著者名が"Laetitia Mimoun"・"Adèle Gruen"(2021年、Journal of Service
  Research)であることを確認したが、信頼できる発音資料(音声・IPA表記等)
  は見つからなかった。台本の"L. Mimoun and A. Gruen"という表記自体は
  変更しなかった(スコープ外の台本変更を避けるため)
- **採用した対策(b): 軽量音韻類似度チェック**: `er006_preprod_
  hardening_01_validation.py`へ`soundex_en()`(標準的なSoundex
  アルゴリズム、pure Python、新規外部依存なし)と
  `aggregate_entity_only_phonetic_corroboration()`を新設した。複数の
  独立したTTS take(同一canonical_textに対する別々の生成、同じ音声の
  複数回文字起こしではない)で観測されたentity_only_diffsのASR書き
  起こし候補を集約し、canonical綴りとの音韻類似度(soundex一致+文字列
  類似度+文字数差+語頭一致)で「同一固有名詞の表記揺れ」と判定できる
  場合のみ`ASR_VALIDATION_UNCERTAIN_PHONETIC_ACCEPTED`として自動採用
  する。保守的側に倒す設計(既存protected_check思想[数字/否定/内容語は
  絶対に見逃さない]を壊さないため):
  (1) 数字・否定・非固有名詞内容語の差を含むtakeは、そのtake単体を
  判断材料から除外するのみに留める(全体を一括拒否しない。実データで、
  1回のtakeに無関係な内容語差が混入していた場合でも、他の独立した
  takeの証拠は引き続き使えることを確認した)
  (2) 同じ誤認識が複数回**繰り返し**観測される場合(多様性の裏付けが
  無い)は自動PASSしない。"Robert"→"Rupert"のような、soundexが一致し
  文字列類似度も高いが実在する無関係な別人名への置き換わりを、単発の
  判定だけでは区別できないことを検証で確認したため、この多様性要件で
  緩和した
  (3) 単発観測(裏付け無し)は、複数回観測(多様性の裏付けあり)より
  厳しい閾値(文字列類似度0.75以上・文字数差1以内)を要求する
  (4) canonical/ASR両方の語数が一致する候補のみを判定対象にする。
  実データで、頭文字("L.")がASR側の書き起こしで直後の固有名詞と融合
  し("L. Mimoun"→"Elmi Moon")、difflibのspan境界が試行ごとに揺れる
  ことを発見したため、短い頭文字トークンを除いたgrouping keyで同一
  固有名詞の証拠をまとめ、語数が対応しない候補は「判定不能」として
  除外する(反証にも証拠にもしない)設計にした
- **配線**: `er003_v1_sing01_news_tail_fix.py::generate_news_narration_
  wide_margin()`(B1 Full Story等の長尺英語News本文生成)へ配線した。
  entity-only mismatchの場合、既存のmax_attempts(6)上限内でretryを
  継続し複数takeの証拠を集められるようにした(既存の「同一signature
  连続で打ち切り」ロジックには影響しない、コスト上限は拡張していない)
- **known limitation(正直に記録)**: soundexベースの軽量チェックは、
  実在する別名同士の完全な区別を理論上保証しない(上記(2)の多様性
  要件で緩和しているが、原理的に完全ではない)。本チェックはretry・
  Human Review滞留を減らすための補助的最適化であり、既存の必須プロセス
  (最終的なユーザー試聴)がこの限界に対する最終的な安全網であり続ける
- **full_story_part2のroot cause確定**: `tts_safe_news_en()`(A2/B1
  共通のTTS入力正規化)・`build_tts_prompt()`・Gemini Batch API呼び出し
  経路のコードを実際に追跡し、"April 28, 2026"が一切変換されずTTSへ
  渡っていることを確認した(前処理バグではない)。旧B1本文(digit表記
  "April 28")・新表記("April twenty eighth")のいずれでも、12回中
  多くの試行で"26"という一貫した誤読が観測され(新表記では6回中4回が
  誤読、2回が正読)、ユーザー自身も実際に音声を聴取し「26に聞こえる」
  ことを確認済みであることから、genuine TTS mispronunciationと結論した
- **point fix**: `b1b/parts.json`(part2)・`b1b/article.md`の該当箇所
  を"on April 28, 2026,"→"on April twenty eighth, 2026,"へ変更した
  (事実・意味は無変更)。ユーザー提示の具体例"twenty-eighth, twenty
  twenty-six"は、既存の`tts_safe_number_words_en()`(A2専用、ハイフン
  複合数詞をOPEN-58と同じパターンで誤変換する)を実際に通してみたところ
  "twenty-6"に壊れることを確認したため、ハイフンを使わない
  "twenty eighth"へ変更し、年号は元々問題が無かった("2026"は12回全て
  で正しく認識されていた)ため桁のまま残す形へ変更した(ユーザー提示の
  具体例をそのまま採用せず、必要な範囲だけ安全な形へ調整した)
- **副産物として発見した複合序数正規化バグ**: 上記の再生成で、6回中
  2回(attempt1・6)が実際には正しく"28th"と発話されていたにも関わらず
  TRUE_CONTENT_MISMATCHと誤判定されていることを発見した。原因は
  `normalize_text()`の数値正規化パイプラインが、"twenty eighth"を
  1つの複合序数として扱えず、独立したcardinal変換ステップが"twenty"を
  "20"へ、独立したordinal変換ステップが"eighth"を"8th"へそれぞれ別々に
  変換し、"20 8th"という無関係な2トークンへ分裂させていたことだった。
  OPEN-58と同じ教訓(共有regexへの機械的な追加は事故を招きやすい)を
  踏まえ、「十の位の単語+一の位の序数語」という閉じた具体的パターン
  のみを対象にした専用ステップ`_convert_compound_ordinal_words()`を、
  既存のcardinal/ordinal変換より先に実行する形で追加した(スペース・
  ハイフン両方の区切りに対応)。バグ修正後、attempt6(既に実際に生成
  済みの音声、新規API呼び出し無し)を再判定した結果、実際に`NORMALIZED_
  MATCH`(should_pass=True)になることを確認し、その音声をそのまま
  status=OKとして採用した(音声ファイルは無変更、判定記録のみ訂正)
- **再発防止策の検討と不採用**: 「重要な日付・数字をTTS入力へ渡す前に
  検出しHuman Review相当のフラグを立てる軽量チェック」を検討したが、
  今回は実装を見送った(OPEN-78として記録)。理由: 発生条件(なぜこの
  特定の日付表現でTTSが誤読するのか)が未解明のまま汎用検出ルールを
  設計すると過検知/過剰実装のリスクが高く、今回の個別事象はpoint fix
  で解決済みのため緊急性が低いと判断した
- **受入テスト**: `er010_entity_phonetic_corroboration_01_test_01.py`
  (22件、全PASS)。No.5実データ(Mimoun/Gruen/Ralf Rüller、頭文字融合
  ノイズ、Robert/Rupert型の拒否確認、複合序数の各パターン)を含む
- **No.5実データへの適用**: comment_4修正・再生成、full_story_part1を
  新設した音韻類似度チェック経由で2回の試行で解決(実際にこの経路で
  解決)、full_story_part2をバグ修正後の再判定で解決(新規TTS/ASR
  呼び出し無し)。B1の全14 segmentがVALIDATEDとなり、Audio Validation
  Gateを実PASSしB1を再assemble(366.774秒、clipping無し)した。A2は
  無変更のままGate実PASSを再確認した。既存回帰テストは1841/1842 PASS
  (残り1件はOPEN-77、本タスクと無関係のpre-existing test bug)
- **今回実施しなかったこと**: 全記事・全固有名詞への一律発音資料調査
  research工程の追加(コスト増回避、reactiveな個別対応のみ)、重要な
  日付・数字の一般的なTTS入力前検出ゲートの実装(OPEN-78、Deferred)
- **根拠レポート**: ER-010-ENTITY-PHONETIC-CORROBORATION-01/ER-010-
  DATE-SPOKEN-FORM-POINT-FIX-01完了報告、OPEN-63(解消)・OPEN-78(新設)
- **影響するCURRENT_SPEC項目**: QA/Human Review節へ「英語固有名詞ASR
  表記揺れの軽量音韻類似度チェック」「複合序数の正規化バグ修正」
  「重要な日付・数字のTTS入力前チェック(検討したが今回は不採用)」の
  3項目を新規追加

## ER-011-HUMAN-REVIEW-COST-GUARD-01(2026-08-27)

- **Decision**: No.5(pool_n5_cafes)のB1修正作業中に発生した異常な
  API消費事故を受け、Human Review Queueへ到達した(または繰り返し
  STOPPEDになった)segmentへの機械的な再生成を、明示的な承認が無い
  限りAPIレベルでブロックするReview Lock機構を新設し、Production
  経路(英語側・日本語側の両方)へ正式配線した(`APPROVED_FOR_
  PRODUCTION`→`PRODUCTION_WIRED`)
- **root cause(監査で判明、2026-08-27深夜)**: `er009_pool_n5_b1_
  fix_01.py`(No.5 full_story_part1/2の修正用に前タスクで作成した
  薄い呼び出しスクリプト)を、full_story_part1がASR_VALIDATION_
  UNCERTAIN(Human Review相当)・full_story_part2がSTOPPEDのまま
  何度も手動再実行してしまい、full_story_part1でTTS 18回・ASR
  59回、full_story_part2でTTS 12回という異常なAPI消費が発生した。
  根本原因は2つ: (1) 呼び出し側スクリプトが`results["segments"]
  [name] = r`で毎回結果を無条件に上書きし、過去の試行履歴・Human
  Review到達状態を一切引き継がない設計だったこと、(2) Human Review
  Queue(英語側`er006_output/audio_retry_cascade_prod_01/human_
  review_queue.jsonl`、日本語側`er007_output/ja_asr_cascade_01/
  human_review_queue.jsonl`)へ到達した後も、それを検知して新規
  TTS/ASR呼び出しをブロックする仕組みがProduction経路のどこにも
  存在しなかったこと
- **設計(Part C: Review Lock状態)**: `er011_human_review_lock_01.py`
  を新設し、narration wavパス(".../<theme>/<level>/narration/
  <segment>.wav")から`(theme_id, level, segment_id)`を機械的に
  導出するキー(`derive_segment_key()`)で、segment単位のlock状態
  (`AUTO_PROCESSING`/`HUMAN_REVIEW_REQUIRED`/`HUMAN_APPROVED`/
  `REGENERATE_APPROVED`/`RESOLVED`)を`{level_out_dir}/audit/
  review_lock_state.json`(既存のtts_generation_results.json・
  human_approved_segments.jsonと同じ置き場所の思想)で管理する。
  既存の関数シグネチャ(`text, out_path, ...`)を一切変更せず、
  out_pathから逆算する設計にしたことで、呼び出し元コードへの侵襲を
  最小化した。`HUMAN_APPROVED`判定は、新規の並行実装を避けるため
  既存の`record_human_approval()`(`er003_v1_n3_01_assemble.py`)を
  そのまま流用する
- **Part D(明示的解除)**: `approve_regenerate()`は対話的オペレー
  ター操作でのみ呼ぶことを想定した独立APIとし、通常のTTS生成経路
  からは絶対に到達しない設計にした。`REGENERATE_APPROVED`は次の
  1回の呼び出しだけで自動的に消費され(結果に応じて`RESOLVED`または
  `HUMAN_REVIEW_REQUIRED`へ遷移)、「同じスクリプトをもう一度実行
  しただけ」では再解除されないことを受入テストで確認した。台本
  (text)が変わった場合はSHA256ハッシュの不一致により自動的に新しい
  バージョンとして扱われ、過去のlockは無効になる(既存の
  `record_human_approval()`のtext変更時無効化と同じ設計思想)
- **Part E(attempt history)**: 既存のtts_generation_results.json
  (segment単位で上書きされる正)は一切変更せず、別ファイル
  (`er011_output/attempt_history.jsonl`)へ追記型で記録する。
  theme/level/segment/run_id/timestamp/TTS試行数/ASR呼び出し数/
  累積値/Human Review到達有無/最終lock状態/所要時間を1呼び出し
  あたり1行で記録する
- **Part F(budget guard)**: 既存のTTS retry上限(max_attempts=
  6〜8)を踏まえ、累積TTS試行数上限15・累積ASR呼び出し数上限60を
  第二防衛線として設定した(第一防衛線はHUMAN_REVIEW_REQUIRED
  到達時点での即時ブロック、高い閾値で形骸化させないよう実際の
  事故[TTS18回/ASR59回]より確実に低い値にした)。`REGENERATE_
  APPROVED`中であっても、この上限を超えた場合は強制的に
  `HUMAN_REVIEW_REQUIRED`へ固定する
- **Part G(queue重複防止)**: 英語・日本語両方の`_log_human_review()`
  (`er006_secondary_asr_01.py`/`er007_ja_secondary_asr_01.py`)へ
  `is_duplicate_queue_entry()`チェックを追加し、同一wav_path・同一
  canonical_textのentryが既に存在する場合は新規追記しないようにした
- **配線(Part J、英語側・日本語側両方)**: `guarded_generate(language)`
  デコレータ(`(text, out_path, *args, **kwargs)`シグネチャ用)・
  `guarded_generate_with_language_arg`デコレータ(`(text, language,
  out_path, ...)`シグネチャ用、en/ja両方を1つの関数で扱う
  `generate_narration_snippet_verified_strict`向け)を実装し、以下へ
  適用した: 英語側`er003_v1_sing01_voice01_generate.py::generate_
  charon_english`・`er003_v1_sing01_point_headings_aoede.py::
  generate`・`er003_v1_sing01_news_tail_fix.py::generate_news_
  narration_wide_margin`・`er003_v1_repro01_main_generate.py::
  generate_key_phrase_component_verified`、日本語側`er003_v1_
  sing01_voice01_generate.py::generate_charon_japanese`、両言語共通
  `er003_v1_repro01_main_generate.py::generate_narration_snippet_
  verified_strict`(A2/B1双方のstandard経路がこの関数を経由するため、
  1箇所の配線で広くカバーできる)。fallback経路を持つ合成関数
  (`er003_v1_crosslevel_audio_02_common.py::generate_english_
  segment_with_fallback`・`er003_v1_n3_01_tts_generate.py::
  generate_a2_japanese_with_fallback`)自体はデコレータで包まず
  (standard経路の内部呼び出しが既にguardされているため二重guardに
  なる)、代わりにstandard経路が`HUMAN_REVIEW_LOCKED`を返した場合に
  fallbackへ進まないよう明示的な早期returnを追加した(fallbackは
  未ガードの直接TTS/ASR呼び出しのため、ここを通過させるとLockの
  意味が無くなる)
- **既知の適用範囲外(意図的、正直に記録)**: A2 6% slowdown retry
  (`generate_a2_segment_with_slowdown`、ER-008-A2-POSTPROCESS-
  SLOWDOWN-PROD-11)は、内側の`generate_english_segment_with_
  fallback()`が`status=OK`を返した直後に、post-process後のASR
  再検証が別途不一致となり、同じ内側関数を最大3回まで正当に取り
  直す既存の設計を持つ。当初`RESOLVED`状態もブロック対象にする設計
  だったが、これが上記の既存の正当なretryを機械的に止めてしまう
  ことを実装中に発見し撤回した(`RESOLVED`は監査用の記録に留め、
  ブロックしない設計へ修正)。本Guardが防ぐべきは「Human Review・
  繰り返し失敗への機械的再挑戦」であり、「一度成功したsegmentへの
  正当な再挑戦」ではないと整理した
- **実装中に発見したバグ(正直に記録)**: 初期実装では、out_pathが
  既存の命名慣習(".../<theme>/<level>/narration/<segment>.wav")に
  従わない場合(単体テストのダミーパス"dummy_out.wav"等)、theme/
  level/segmentが空文字列に縮退し、複数の無関係な呼び出しが同じ
  (ドライブルート直下の)store pathを共有してしまう実バグを、
  既存回帰テスト(`er007_ja_tts_retry_path_fix_test_01.py`、2件の
  test methodが同じダミーテキスト・パスを使う)の失敗で発見した。
  `_has_valid_narration_layout()`を追加し、out_pathが規約に従わない
  場合はReview Lock機構全体を無効化する(常にproceedし、store
  読み書きも行わない)よう修正して解消した
- **受入テスト(Part H、5ケース+補強4ケース)**: `er011_human_review_
  lock_01_test_01.py`(9件、全PASS)。(1)Human Reviewへ到達→queue
  登録→STOP、(2)同じsegment再実行→TTS/ASR call 0・既存状態を返す、
  (3)明示的`approve_regenerate()`→初めて再生成可能、(4)再生成後
  また失敗→再びlock(再承認なしでは解除されないことも確認)、
  (5)queue重複なし、に加え、budget guard発火・derive_segment_keyの
  Windows形式パス対応・台本変更時のlock無効化を追加確認した
- **実データ検証**: No.5 full_story_part1の実際の事故シナリオを
  再現するため、実際のProduction関数(`er003_v1_sing01_news_tail_
  fix.py::generate_news_narration_wide_margin`、事故で実際に使われた
  関数そのもの)に対し、事前にHUMAN_REVIEW_REQUIRED状態を模擬した
  lockを与えた上で直接呼び出し、0.003秒で即座に`HUMAN_REVIEW_
  LOCKED`が返る(実TTS/ASR API呼び出しが一切発生しない)ことを確認
  した
- **今回実施しなかったこと**: legacy/one-off script(P-series・
  IRAN01・SING01等、既にHISTORICAL化済みの完成テーマ向けスクリプト)
  からの直接呼び出しへの配線(現行Production経路[N3-01/pool_pilot_
  01系]のみを対象とし、Part Hの既存方針[Audio Validation Gate等]
  と同様、legacy scriptは対象外とした)
- **根拠レポート**: ER-011-HUMAN-REVIEW-COST-GUARD-01完了報告
- **影響するCURRENT_SPEC項目**: QA/Human Review節へ「Human Review
  Cost Guard(Review Lock機構)」を新規追加(`DECIDED`、
  `PRODUCTION_WIRED`)

## ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15: TTS retry上限3回化+固有名詞/日本語表記ゆれ/英語homophoneのCascade改修(Implementation Hardening)

- **日付**: 2026-08-28
- **背景**: 前タスク(No.8 Human Review監査)で、Human Reviewへ落ちた3件(`Kristie Tse`人名/`ころ・頃`表記ゆれ/`wait・weight`同音異義語)がいずれも「音声不良」ではなく、Validator/Cascade側の機能不足が原因と判明した。加えて、ASR表記ゆれだけを理由に同一segmentを最大6回TTS再生成する既存仕様がCost/Delivery上不合理と判断された
- **内容**(5点、状態は下記参照):
  1. **TTS retry上限 6→3回**(ユーザー正式決定): `er011_human_review_lock_01.PRODUCTION_MAX_TTS_ATTEMPTS = 3`をSSOTとし、Production全8関数の`max_attempts`既定値を統一。standard+fallback 2段構成の4関数は、fallbackへ残り予算のみを渡すよう改修(合計が3回を超えないことをテストで確認)
  2. **固有名詞ASR判定**: 「ASR結果同士の収束」を自動PASSの根拠にすることをやめ(ASR consensus ≠ pronunciation verification)、(A) CMU Pronouncing Dictionaryの代表発音がcanonical綴りと直接一致する場合のみコストゼロで自動PASS、(B) 辞書に無い外国由来名はPronunciation Ledgerへ実データを投入(cache miss時のみPerplexityで1回research、記事横断でcache再利用)するが、これは自動PASSの根拠にはせずHuman Reviewパッケージの充実のみに使う、という二分岐へ再設計した
  3. **日本語表記ゆれ**: 濁点差の一律許容(`_reading_equal_allowing_voicing`)ではなく、「ASR側漢字spanが辞書上持ちうる正当な読み候補にcanonical期待読みが含まれるか」+「異なる2エンジン(OpenAI/Azure)以上の裏付け」を要求する`ORTHOGRAPHIC_VARIANT_CONFIRMED`を新設
  4. **英語homophone**: CMU Pronouncing DictionaryのARPAbet完全一致を主根拠とする`HOMOPHONE_EQUIVALENT`を新設。Secondary側は「canonicalへ戻る」ことではなく「ARPAbet完全一致(canonical一致でも同じhomophoneでもよい)」を要求し、「他に問題が見つからなかった」という消極的PASSは禁止
  5. **attempts_log保持**: Human Review Lock発動後にattempts_logが空配列で上書きされていたバグを修正(`last_attempts_log`)
- **状態**: `DECIDED` / `VALIDATED`(2026-08-28修正: 前回報告で誤って`PRODUCTION_WIRED`としていたが、(a) commit/push未実施、(b) `wait/weight`はattempts_log消失バグにより実ログではなく合成データでの検証、(c) `Kristie Tse`はCase Bが未解決のままHuman Reviewへ残っている、という条件により`PRODUCTION_WIRED`の要件[実装完了・SoT反映・commit・push・Production配線・テストPASS・実データ確認・Production相当runtime evidence確認]を全ては満たしていないと判断し、`VALIDATED`へ訂正した。commit/push後、残課題が無いことを確認できた時点で改めて`PRODUCTION_WIRED`へ昇格する)
- **採用理由**: No.8監査で発見した3件の根本原因(ASR consensusをpronunciation verificationの代わりに使っていた設計上の誤り、日本語の濁点一律許容、homophone対応の欠如、無駄なTTS retry)へ、量産(100記事規模)を見据えた最小限の修正で対応するため
- **比較した選択肢と却下理由**(ユーザーとの複数回の設計レビューで変遷):
  - 固有名詞: 当初「複数ASR結果同士の音韻的収束で自動PASS」を検討したが、「ASR同士が似た誤認識で一致することは、正しい発音と一致している証拠にはならない」との指摘で却下。次に「Ledgerの`expected_pronunciation_ipa`を静的IPA→ARPAbet対応表で変換して比較」を検討したが、「ARPAbetは英語音韻前提であり、外国語由来の音韻情報が変換時に失われ誤PASSしうる」との指摘で却下。最終的に「CMU辞書で両方が直接解決できる場合のみ自動PASS、それ以外は自動PASSせずLedgerは人間向け情報提供のみに使う」という二分岐へ収束
  - Homophone: 当初「閉じたペアテーブルのみ」を検討したが、100記事規模での保守負荷・False Negative増大が懸念されたため、QCD比較の結果CMU Pronouncing Dictionary主体のハイブリッド方式(新規軽量dependency、pykakasiと同種の性質)へ変更
  - 日本語表記ゆれ: 当初「4ステップが同じ表記へ収束したことをPASS根拠にする」設計だったが、「ASRが同じ漢字を何回書いたかは読みが正しい証拠にならない」との指摘で、辞書上の読み候補照合方式へ変更
- **実装中に発見した事実**:
  - `er003_v1_sing01_news_tail_fix.py::generate_news_narration_wide_margin`が、旧`ER-010-ENTITY-PHONETIC-CORROBORATION-01`(`aggregate_entity_only_phonetic_corroboration`、ASR結果同士の収束による自動PASS)を実際にlive productionへ配線しており、No.8 Kristie Tseケースはこの経路を実際に通っていたことが判明(監査時点では「配線されていない分析用関数」と認識していたが、実際には1関数で使われていた)。設計変更に合わせてこの経路を撤去した
  - `_phonetic_pair_ok`(ER-010)の`a[0] != b[0]`(先頭文字の綴り完全一致要求)が、"Kristie"(k)/"Christy"(c)のような、綴りは異なるが同じ音(/k/)を表す組を誤って弾いていたバグを、既存の`_SOUNDEX_CODES`テーブル(C/G/J/K/Q/S/X/Zを同一グループとして扱う)を先頭文字比較にも再利用する形で修正。ただし今回の再設計により、この関数自体はlive cascadeのPASS判定には使われない(audit専用関数のまま)
  - CMU Pronouncing Dictionaryに偶然"tse"というentryが存在し(無関係な理由、ARPAbet代表発音"T S IY1")、その1バリアント("S IY1")がASR誤認識候補"Sea"/"C"と一致してしまう実例を発見。固有名詞Case Aを「いずれかのバリアントが一致すれば可」ではなく「代表(先頭)バリアントの完全一致のみ」という、homophoneチェックより厳格な基準にした理由はこれ
  - pykakasiが同梱する漢和辞書データ(`kanwadict4.db`)が、単漢字の正当な読み候補一覧をそのまま提供することを発見し、新規dependencyゼロで日本語側の読み候補照合を実装できた
- **既知の限界(正直に記録)**: 「頃」のように単漢字として複数の読み(ころ/ごろ)が辞書上正当に登録されている文字は、テキストのみからは実際に発話された読みを完全には確定できない(OPEN-80)。異なる2エンジンの裏付けを要求することで緩和しているが、原理的な限界として残る
- **Part M再validation結果**(既存音声を再TTSせず、記録済みASR文字起こしへ新ロジックを再適用):
  - `ころ/頃`(A2 preview): 実際の記録済み4ステップASR結果で`ORTHOGRAPHIC_VARIANT_CONFIRMED`としてVALIDATED
  - `Kristie Tse`(B1 point_two): 実際に記録された5回のCascade試行のうち、ASRが偶然"Tse"を正しく書き起こした1回のみ`PROPER_NOUN_ENTITY_ARPABET_CONFIRMED`でVALIDATED(残り4回はCase Aで解決できず、Pronunciation Ledgerの実データ[Perplexity research、記事横断cache済み]を伴ってHuman Reviewのまま)。**正直な留保**: 旧6回retry前提で記録された5取得分の再評価であり、新しい3回上限の下で新規に3回生成し直した場合に同じ結果(1/3が解決)になる保証はない(新規TTS生成はPart Mの禁止事項のため未検証)
  - `wait/weight`(A2 point_one_heading): Human Review Lock発動時のattempts_log消失バグにより生ASR文字列が残っておらず、ユーザーの元タスク記述にある既知事実(「ASR: weight」)を仮定した合成データで`HOMOPHONE_EQUIVALENT`としてVALIDATED(実データでの裏付けは取れていない、OPEN-82)
- **regression**: 既存の全テストファイル(`er006_preprod_hardening_01_validation_test.py`55件、`er006_secondary_asr_01_test.py`14件→19件、`er007_ja_asr_validator_01_test.py`30件、`er007_ja_secondary_asr_01_test.py`6件→9件、`er006_pronunciation_ledger_01_test.py`5件、`er011_human_review_lock_01_test_01.py`9件→13件、`er010_entity_phonetic_corroboration_01_test_01.py`22件)が全てPASS。新規`er008_asr_variant_hardening_15_homophone_en_test.py`(6件)も全てPASS
- **API call数・コスト**: Perplexity research 1回(Kristie Tse、Part M再validation実行時に実施、記事横断でcache再利用されるため今後同一entityでの再課金は発生しない)。TTS/ASR APIの新規呼び出しは0件
- **根拠レポート**: ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15完了報告
- **影響するCURRENT_SPEC項目**: Audio Implementation Detail節へ「TTS生成の同一segment総試行回数上限」「固有名詞ASR不一致の自動PASS条件」「日本語表記ゆれのCascade内自動PASS条件」「英語homophoneのCascade内自動PASS条件」を新規追加

### 継続セッション(同日2026-08-28): 固有名詞ASR不一致の量産仕様化を検討し、STOP

- **依頼内容**: 上記(A)の「CMU辞書に無い固有名詞は常にHuman Review」という設計は、1日数十記事の量産では毎回Human Reviewが発生し不十分なため、「外部の信頼できる発音根拠(本人・公式情報源由来のIPA/音声等)を取得し、それを現在のTTS実音声と自動照合してAUTO PASSする」という正式フローへの格上げを検討した
- **調査結果**: 既存コードベースを確認したが、TTS実音声を音素レベルで書き起こす機能(phonetic ASR)、外部参照音声とTTS音声を音響的に比較する機能、強制アライメント(forced alignment)のいずれも実装されていない。ASR層(`er006_asr_provider_routing_01`のOpenAI ASR、`er006_secondary_asr_01`のAzure STT)は単語単位の正書法テキストしか返さない。`er006_pronunciation_research_01.research_pronunciations()`(Perplexity)が返すのもテキストのIPA/カタカナ的ヒントであり、参照音声そのものではない。OPEN-80も「音声そのものを使った実発音確認(MFA等の強制アライメント)」を将来検討事項として明記しており、現時点で未着手であることと整合する
- **判断: STOP**(タスク仕様§3の「実装上のSTOP条件」に従い、近似実装を行わずここで報告する)。「外部発音根拠 ↔ TTS実音声」を安全に自動照合する軽量な既存手段が無いため、Case B(CMU辞書に無い固有名詞)の自動PASS化は今回実装しない。検討した設計オプションと却下/保留理由:
  1. **Azure Pronunciation Assessment API**(既存のAzure Speech SDK依存を流用可能): 音声とreference textを渡すと音素単位の一致度スコアを返す機能。ただし本来は「学習者の発音が指定localeの標準的な発音にどれだけ近いか」を測る用途であり、外国語由来の固有名詞のカスタムIPAをreferenceとして直接検証できる設計ではない。誤った基準で「一致」と判定するリスクがあり、採用前に個別の検証実験が必要
  2. **外部参照音声(Forvo等)とTTS音声の音響的類似度比較**: 参照音声の取得・利用許諾、音響特徴量(MFCC等)によるDTW/類似度判定の実装・閾値調整が必要で、「軽量な追加実装」の範囲を超える新規パイプラインになる
  3. **音素レベル強制アライメント(MFA等、OPEN-80が既に言及)**: 音響モデルを伴う本格的な新規依存であり、同じく軽量実装の範囲を超える
  - いずれも「安全に比較できない方式を無理に近似しない」という原則、および「大規模Validator刷新はしない」という納期制約の両方に反するため、今回は採用しない
- **今回実施した安全な範囲の改善**(自動PASS化とは無関係、Human Reviewの質向上のみ):
  - `er006_pronunciation_research_01.py`のPerplexityプロンプトを改訂し、「本人・公式サイト・所属組織・公式イベント・信頼できるインタビュー等の一次情報源を優先する」指示を追加(取得したcitationsの信頼性が上がり、Human Reviewパッケージの質が上がる。自動PASSの判断には使わない)
  - OPEN-80を「頃」個別の問題から「同一漢字表記に複数の正当な読みがある語全般(多読漢字)」の問題へ再定義(詳細はOPEN_ITEMS.md参照)。既存の`ころ/頃`AUTO PASS仕様(ORTHOGRAPHIC_VARIANT_CONFIRMED)は変更していない
- **量産への影響**: Case B(外国由来固有名詞)は引き続きHuman Reviewへ進む。ただしPronunciation Ledgerによるresearch結果の記事横断cache再利用(Perplexity再課金の回避)は既に本番配線済みのため、同一固有名詞の外部検索コストが繰り返し発生することは無い。Human Reviewの発生自体を無くすには、上記いずれかの設計オプションの実験的検証が別タスクとして必要
- **状態**: `STOPPED_FOR_DESIGN_REVIEW`(ユーザー判断待ち。実装は行っていない)

## ER-008-N8-HUMAN-APPROVAL-AND-PROPER-NOUN-PRONUNCIATION-SPEC-16(2026-08-28)

- **目的**: (1) No.8でHuman Review待ちだった3 segment(A2 `preview`・A2 `point_one_heading`・B1 `point_two`)について、ユーザーが実際に試聴した結果を正式なHuman Approval記録へ反映しAssemble可能にする。(2) 固有名詞の発音判定基準を、「本人・原語としての厳密な発音」偏重から「eigo-radioが英語学習コンテンツであることを踏まえた、英語圏で実際に通用する発音」基準へ変更する
- **経緯**: 前セッションで作成した[Gate Hold](https://claude.ai/code/artifact/a545159e-fe1f-4816-8b66-56e5af6dfd1d)アーティファクトで3 segmentの音声をユーザーへ提示。ユーザーが実際に試聴し、3件とも現状の音声のまま使用してよいと判断(`Kristie Tse`のみ、本人の唯一の厳密発音ではなく「seeに近い、英語圏で許容される発音」という理由での承認)
- **Human Approval記録**(`er003_v1_n3_01_assemble.record_human_approval()`、新規TTS/ASR呼び出しなし):
  | segment | out_dir | canonical_text_sha256(先頭12桁) | 承認理由 |
  |---|---|---|---|
  | `preview` | `.../a2` | 参照実装参照 | ユーザー試聴、そのままでOK |
  | `point_one_heading` | `.../a2` | 参照実装参照 | ユーザー試聴、そのままでOK("A small wait can protect against a big fear") |
  | `point_two` | `.../b1b` | 参照実装参照 | ユーザー試聴、`Kristie Tse`の`Tse`が"see"に近い発音で英語圏の許容発音候補に含まれると判断 |
- **発見した既存バグとその修正**: 上記3件を承認記録した後にAudio Validation Gate(`verify_episode_audio_validation_gate`)を実行したところ、A2の2件(`preview`/`point_one_heading`)が承認記録があるにもかかわらずブロックされ続けることを発見した。原因調査の結果、`_segment_gate_status()`(ER-008-AUDIO-VALIDATION-GATE-AND-EVIDENCE-MAJOR-AUDIT-05で実装)が判定する`status`分岐に、後から実装されたER-011 Human Review Lockが書き込む`status=HUMAN_REVIEW_LOCKED`という値が存在せず、どの分岐にも一致しないため無条件で`UNVALIDATED`(未承認)へ落ちてしまうという、2つの機能間の統合漏れ(いずれも正しく動作していたが、組み合わせ時の考慮が漏れていた)と判明した。`er003_v1_n3_01_assemble.py::_segment_gate_status()`の承認確認分岐に`HUMAN_REVIEW_LOCKED`を`ASR_VALIDATION_UNCERTAIN`と同列で追加し、修正後に3件全てが`HUMAN_APPROVED`として正しく通過することを実データで確認した(Gate自体の強制無効化・bypassは一切行っていない。承認記録が無いsegmentは修正後も引き続きブロックされる設計のまま)
- **固有名詞の発音判定基準の変更**(ユーザー承認、`APPROVED_FOR_PRODUCTION`): 新しい判定優先順位は (1) 本人自身の英語での発音 → (2) 公式プロフィール・所属組織・公式イベント等で確認できる英語発音 → (3) 信頼できる情報源で確認できる一般的な英語圏発音 → (4) 複数の英語圏発音が実際に認められる場合は許容発音集合として保持、の順。母語・原語における唯一の厳密発音との一致は今後必須条件にしない。**実装は行っていない**(現時点ではHuman Reviewでの人間の判断基準の変更のみ。Cascadeの自動判定ロジックへの組み込みは行っていない)
- **No.8 Assemble結果**(`stage_assemble_a2`/`stage_assemble_b1`、新規TTS/ASR呼び出し0件):
  - B1: `er006_output/pool_pilot_01/pool_n8_airport_line/b1b/assembled/English_Your_Way_B1B_POOL_N8_AIRPORT_LINE.wav`、318.155秒、clipping無し、peak 0.858
  - A2: `er006_output/pool_pilot_01/pool_n8_airport_line/a2/assembled/English_Your_Way_A2_POOL_N8_AIRPORT_LINE.wav`、372.827秒、clipping無し、peak 0.770
  - 完成音声(mp3変換版)をArtifactとして提供: https://claude.ai/code/artifact/d558fc26-3214-4987-9024-996bb9acbdef (Now Boarding)
- **API call数・コスト**: TTS 0件、ASR 0件、Perplexity等の外部発音調査 0件(全てローカルのAssemble処理のみ)
- **regression**: `_segment_gate_status()`変更に対する既存の専用テストファイルは無い(ER-008-15完了時点で確認済みの既存テストスイートに影響する変更ではない、Assembly gate関連のロジックのみの追加分岐)
- **影響するCURRENT_SPEC項目**: 「固有名詞ASR不一致の自動PASS条件」に発音基準変更を追記、「Audio Validation Gate」に`HUMAN_REVIEW_LOCKED`対応バグ修正を追記
- **OPEN-83への影響**: 判定基準の変更により今後Case B固有名詞がHuman Reviewへ進む頻度は下がる見込みだが、「外部発音根拠とTTS実音声を安全に自動照合する仕組み」自体は依然未実装のため、OPEN-83は`STOPPED_FOR_DESIGN_REVIEW`のまま維持。将来実装時は「唯一の原語発音」ではなく「許容される英語発音集合のいずれかとの一致」を判定対象にする旨をOPEN-83へ追記した
- **状態**: 3件のHuman Approval・Audio Validation Gate通過・No.8 Assemble完了は`DECIDED`。固有名詞発音判定基準の変更は`APPROVED_FOR_PRODUCTION`(Cascadeの自動判定ロジックへの実装・テスト・Production経路でのruntime確認が完了するまでは`PRODUCTION_WIRED`としない)

## ER-008-N8-QA-CONTENT-SPEED-HARDENING-18 / ER-008-N8-PRODUCTION-WIRING-AND-FOLLOWUP-19(2026-08-29、Implementation Hardening)

- **背景**: No.8ユーザーFeedback監査(ER-008-N8-USER-FEEDBACK-AUDIT-17)で判明した12件の指摘のうち、即修正必須/実ユーザー検証前に直すべき、と分類された項目についてER-18で設計・トライアル実装・No.8個別修復を行い、ユーザー承認を得た上でER-19にてProduction経路への正式配線・回帰テスト・runtime evidence取得まで行った。ER-18時点の変更はcommit/pushされておらず、DECISION_LOGへの記録も本entryが初出のため、ER-18の決定事項も併せて記録する。
- **内容(項目ごと、状態は各行末尾を参照)**:
  1. **A2 disfluency QA(Key Phrase "uneven uneven choice")**: 前回調査(ER-17)では「Key Phraseの意図的な2回読み」と誤認識していたが、ユーザーの指摘で再調査した結果、`kp2_en.wav`単体に"uneven, uneven choice"という実在のpartial repetitionがあり、Production ASRがこれを平滑化して書き起こしていたためValidatorをすり抜けていたことを確認した(誤った前回結論を訂正)。無料・ローカルのfaster-whisperによるverbatim再チェック(`er008_disfluency_qa_18.py`)を新設し、Key Phrase/Point見出し/In One Line/B1 Previewの生成関数(`generate_key_phrase_component_verified`/`generate_a2_segment_with_slowdown`系/`point_headings.generate`/`generate_news_narration_wide_margin`/`generate_charon_english`)へ`disfluency_qa`引数として配線した。flag時は既存のTTS retry loop内でverified=Falseとして扱い、既存の総試行回数上限(3回)内で自動的にTTSを取り直す設計とし、Human Reviewを第一選択にしないというユーザー指示を満たした。No.8の実Key Phrase生成関数呼び出し(kp2相当のテキスト)でruntime evidenceを取得(disfluency_checked=True、当該実行では repetition非再現でOK)。**状態**: `PRODUCTION_WIRED`
  2. **B1 partial-word false start("Wh, why does...")**: 2種類の独立したfaster-whisperモデル(small/tiny)で再検証したが、テキスト上の証拠は見つからなかった(前回の波形20msエネルギー閾値による「検知」はfalse positiveだった可能性が高いと訂正)。word-level ASRの構造上、単語の一部分だけの言い直しは検知できないという既知の限界がある。ユーザー指示によりOpen Item化(OPEN-86)し、量産前解決必須・人手による毎回確認は不採用と明記。**状態**: `OPEN`(OPEN-86)
  3. **Point One/TwoとFull Storyの意味重複**: 第1段階のローカルlexical overlap検知(`er008_point_overlap_qa_18.py`)を新設し、暫定閾値0.45→ユーザー承認により0.40へ変更。記事全体を再生成せず、NGになったPoint 1件だけを再生成する`er008_point_regenerate_19.py::regenerate_point_only()`を新設し(Verified Fact Ledger・確定済みFull Story・他方のPointをcontextとして固定、Full Story論理の言い換え・新Fact追加・causal/certainty/scope driftを明示的に禁止)、`er003_v1_n3_01_articles_generate.py::run_one_pattern()`(Evidence Compression後・Fact Checker前)へ配線した。regenerateされたPointも既存のFact Checker/Ledger Deviation Checkを通る設計とした。No.8 B1実データ(Point One、Full Storyとのoverlap 0.481)で実証: 再生成後overlap 0.188(Full Story)/0.094(他方のPoint)まで低下、内容も「小さなコストvs大きな損失」から「秩序の公平性への不信」という別角度へ実際に変わったことを確認。**既知の限界**: 「新Fact追加なし」の判定は内容語の出現有無による弱いヒューリスティックに留まり、意味的なFact整合の最終判断は人間が必要。**状態**: `PRODUCTION_WIRED`
  4. **Comment 2内部ラベル漏れ("In Part 2...")**: 発生源(Comment生成のcontext/role prompt、A2/B1双方)から"Part 1/Part 2/Full Story Part 1/2"を除去し、非構造的な「前半/後半」表現へ変更。第二防御線として`er003_audio_tts_asr_safety.detect_internal_production_labels_in_english_text()`を新設し、`generate_charon_english()`(A2/B1共通)のTTS呼び出し前に配線した。No.8実データでComment 2(A2/B1とも)を再生成し、新Validatorでの検出0件を確認。**状態**: `PRODUCTION_WIRED`
  5-A. **A2 6% slowdown 必須post-process invariant gate**: No.8 point_one_headingが、Human Review Lock経由の承認によりslowdownを一度も受けないままVALIDATED扱いでAssembleへ到達していた事故を受け、他のmandatory post-process(trim・gain正規化)を横断調査した結果、抜け道が存在するのは条件付きで実行される6% slowdownのみと判明(大規模Architecture変更は不要と判断)。`er003_v1_n3_01_assemble.py::verify_episode_audio_validation_gate()`へ、A2の対象segmentについて`slowdown_applied`フィールド(第一evidence)または`{name}_original.wav`の現存(第二evidence、過去の「resume」系scriptがメタデータを記録し損ねていた既存データとの後方互換用)のいずれかを要求するinvariantチェックを追加した。No.8のpoint_one_heading相当ケースをfixtureで再現しblockされることを確認、かつNo.8の実データ(過去のresume由来segmentを含む)ではPASSすることを確認。**状態**: `PRODUCTION_WIRED`
  5-B. **B1 Preview話し方**: 実測WPM調査でPreview(184.5)が他のCharon segment(topic_intro 143.9、comment_1〜4は148.1〜173.5)より明確に速いことを確認(全segment共通の`ENGLISH_STYLE_PREFIX`のみで、Preview専用の速度制御が存在しなかったことが原因)。A2と同じ「自然言語のみ、数値WPM指定なし」方針で`B1_PREVIEW_STYLE_PREFIX_CALM`を新設し、既存の`style_prefix_override`引数経由でPreview呼び出しにのみ適用(topic_intro/comment_1-4は無変更)。ユーザーが比較試聴の上正式採用。Comment 1-4については現状調査(実測WPM記録)のみ行い、変更は今回未実施(ユーザー試聴前の正式確定を待つ)。**状態**: Preview `PRODUCTION_WIRED`、Comment 1-4は`TBD`(調査のみ)
  6. **Evidence Compression日付過多**: ユーザー指示により今回実装せず、OPEN-84を維持(変更なし)。**状態**: `OPEN`(OPEN-84)
  7. **A2 Preview短縮**: 現行157字/4文をユーザーが「長い」と指摘。theme/problem/valueの3要素を律儀に別文で書き並べない、2文程度・80〜110字程度を目安とする指示へ`PREVIEW_ROLE`(`er003_v1_iran01_a2_generate.py`)を更新した(絶対文字数のhard limitにはしない)。No.8の実際のarticle.md・comment_1/2テキストを使い、本番のPrompt/model/context経由で新規生成した結果157字→74字(2文)を確認(runtime evidence)。No.8本編の完成音声自体は今回差し替えていない(Prompt配線のみ、今後の新規生成から適用)。**状態**: `PRODUCTION_WIRED`(Prompt)
  8. **Key Phrase日本語gloss括弧書き**: ユーザー指示により今回実装せず、OPEN-85を維持(変更なし)。**状態**: `OPEN`(OPEN-85)
  9. **Stephen Reicher文修正**: ユーザー事前承認の置換文言をNo.8 B1 Full Story Part1へ適用し、TTS/ASR再生成・再Assemble済み(量産仕様変更なし、個別修正のみ)。**状態**: `DECIDED`(No.8限定の個別修正)
- **regression**: `run_project_regression.py`実行、collected=1895・passed=1893・failed=2(いずれも今回変更と無関係な既存の失敗: `er003_test_p2j_investigate.CollectionCountTests.test_combined_equals_sum_of_er002_and_er003`[er008系テストファイル増加によりcollected総数が既存の算術チェックとズレる既知の仕様]、`er007_ja_tts_retry_path_fix_test_01.VoiceCharonJapaneseStopRetryingTests.test_stop_retrying_false_still_retries_normally`)。新規追加したテストファイル5件(`er008_disfluency_qa_18_test_01.py`・`er008_point_overlap_qa_18_test_01.py`・`er008_point_regenerate_19_test_01.py`・`er008_n3_01_point_qa_wiring_19_test_01.py`・`er008_a2_slowdown_invariant_19_test_01.py`・`er008_internal_label_gate_18_test_01.py`)は全件PASS
- **API call数・コスト**: 本セッションのruntime evidence取得のための実API呼び出しは、(a) No.8実Key Phrase(kp2相当)のTTS 1回+ASR 1回、(b) No.8実A2 Preview生成LLM呼び出し1回、(c) No.8実B1 Point One regeneration LLM呼び出し1回、の計3件(いずれも数円〜十数円程度の少額、新規Providerの追加なし)。faster-whisperによるdisfluency QA自体はローカルCPU処理のみで追加API課金は無し
- **既知の限界(正直に記録)**: Point-only regenerationの「本当に新しい切り口か」「新Factが追加されていないか」の意味的判定は自動化されていない(弱いヒューリスティック+人間確認が前提)。disfluency QAは「同一単語まるごとの繰り返し」しか検知できず、partial-word型の言い直しは別課題として残る(OPEN-86)。A2 slowdown invariant gateのoriginal.wavフォールバックは、悪意ある/誤ったファイル配置による偽装を技術的に防止しない(既存データとの後方互換のためのゆるい第二evidence)
- **影響するCURRENT_SPEC項目**: 「Preview」節(A2 Preview長さ・B1 Preview話し方・B1 Comment話し方の3行追加)、「QA / Human Review」節(Disfluency QA・Point重複検知+regeneration・Comment内部ラベル二重防御・A2 slowdown invariant gateの4行追加)
- **OPEN_ITEMSへの影響**: OPEN-86新設(B1 partial-word false start、量産前解決必須)。OPEN-83/84/85は状態変更なし(維持)
- **状態**: 上記の通り項目ごとに異なる(`PRODUCTION_WIRED`5件、`OPEN`3件、No.8限定個別修正1件)

## ER-008-N8-FINAL-AUDIO-AND-REMAINING-PRODUCTION-WIRING-20(2026-08-29、Implementation Hardening)

- **背景**: ER-19で`PRODUCTION_WIRED`とした項目のうち、B1 Comment 1-4話し方だけがユーザー試聴前の`TBD`のまま残っていた。ユーザーがCommentへもPreviewと同じcalm styleを正式採用すると決定したため、Production配線・No.8完成版への実反映・最終試聴Artifact作成までを行った
- **内容**:
  1. **B1 Comment 1-4話し方の正式採用・配線**: `er003_v1_n3_01_tts_generate.py::generate_b1_segments()`のpreview/comment_1〜4共通ループを、Previewのみ→全件へ`style_prefix_override=B1_PREVIEW_STYLE_PREFIX_CALM`・`disfluency_qa=True`を適用するよう変更(Full Story/Point/In One LineへはBody別loopのため波及しない)。定数コメント内の"this introduction"という限定的文言を"this"へ一般化(Comment再利用に合わせた文言修正のみ、instruction本文の実質的な意味は変更なし)。No.8実データで実際にpreview/comment_1〜4を再TTS・ASR再検証し、実測WPM: preview 154.5(旧184.5)/comment_1 181.8/comment_2 143.0/comment_3 148.6/comment_4 153.6を確認、全件でdisfluency_checked=true・flagged=false・asr_verified=trueを確認。**状態**: `PRODUCTION_WIRED`
  2. **既承認6項目の再確認**: disfluency QA/Point overlap+regeneration/Comment内部ラベル二重防御/A2 slowdown invariant gate/B1 Preview calm style/A2 Preview短縮について、実装済み・正式Production経路から呼ばれる・設定が有効・テストPASS・runtime evidenceありの5条件を再確認した。結果は全て条件を満たしていたが、**Comment内部ラベル二重防御の項目で、前回(ER-19)の「A2/B1とも実データ0件確認」という報告に誤りを発見**(下記4を参照)
  3. **Point-only regenerationのFact fabricationリスクを実データで確認**: No.8のPoint One(A2: overlap 0.4、B1: overlap 0.542、いずれも閾値0.40でflag)に対し、記事全体を再生成せず`run_point_overlap_qa_and_regenerate()`を直接呼び出すsurgicalな方法(`er008_n8_point_regen_and_verify_20.py`)でPoint-only regenerationを実行した。生成された新テキストは、いずれもFull Story/他方Pointとの重複は大きく改善した(B1: overlap 0.542→0.188/0.094)が、検証済みFact Ledgerに存在しない新規主張(「American Airlinesが順番外搭乗に罰則を導入」「United Airlinesが搭乗改善策を試験中」等)を含んでおり、後続のFact CheckerがA2/B1ともREVIEW_REQUIRED(unsupported_specific_claims 3〜5件)と判定した。ユーザーが指示した監視項目「新Factを追加していないか」がまさに実際に発生した実例であり、`regenerate_point_only()`の自動validation(overlap再チェックのみ、Fact Checkerは含まない)だけでは不十分であることが実データで判明した。この結果は採用せず、Point One/parts.json/article.mdを元のテキストへ差し戻し、Fact Checker(再実行)でPASS・Ledger Deviation CheckでLEDGER_COMPLIANT(0件)を再確認した。**状態**: `PRODUCTION_WIRED`(機構自体は維持)、`MONITORING`(恒久対策は未実装、実ユーザー検証中の監視対象として明記)
  4. **Comment内部ラベル二重防御: ER-19報告の誤りを訂正**: 上記2の再確認作業中、No.8のB1 Comment 2 canonical text(`b1_support_texts.json`)に"In Part 2, what is American Airlines doing to manage this behavior?"という内部ラベルが**修正されないまま残っていた**ことを発見した。ER-19の報告(「No.8実データでComment 2[A2/B1とも]を再生成し検出0件を確認」)はA2側のみ正しく、B1側は実際には未修正だった(Validator自体は正しく機能しており、テキスト修正が漏れていた)。今回、Comment 1-4のcalm style適用に伴いcomment_2を実際に再生成した際、新Validatorが正しくこれを検出・STOPPEDでブロックしたことで発覚した。"In the second half, what is American Airlines doing to manage this behavior?"へ言い換え(A2 comment_2修正[No.4]と同じ、内部ラベルを一般的な時系列表現へ置き換えるだけの最小修正)、再生成してASR verified=true・disfluency flagged=falseを確認し、No.8完成版へ反映した。**状態**: `PRODUCTION_WIRED`(B1側の実データ不整合を修正済み)
  5. **No.8完成版の再Assemble**: 上記の変更を反映するため、変更のあったsegmentのみ再TTS(A2: preview。B1: preview・comment_1〜4)し、他segment(point_two等、Human Review承認済みを含む)は既存の音声をそのまま再利用した上で、`stage_assemble_b1`/`stage_assemble_a2`を実行。Audio Validation Gate(A2 slowdown invariant gate含む)は両レベルともPASS。A2: duration 360.97秒・peak 0.854・clipping無し。B1: duration 327.51秒・peak 0.825・clipping無し。ユーザー最終試聴用Artifact(フルエピソード2本+変更segment6本の個別試聴)を作成: https://claude.ai/code/artifact/ddedda51-daee-44c4-9e3a-88212deb30b1 。**状態**: `USER_FINAL_REVIEW`
- **regression**: `run_project_regression.py`実行、collected=1895・passed=1893・failed=2(ER-19と同一の、今回変更と無関係な既存の失敗2件のみ)
- **API call数・コスト**: (a) No.8実B1 Comment 1-4+Preview再TTS 5回+ASR 5回、(b) No.8実A2 Preview再TTS 1回+ASR 1回(audit記録の再整合目的、テキスト不変のため実質再生成)、(c) Point-only regeneration LLM呼び出し2回(A2/B1、いずれも不採用)+Fact Checker再実行4回(regenerated版2回+revert後再確認2回)+Ledger Deviation Check再実行2回、(d) B1 comment_2修正の再TTS 1回+ASR 1回。いずれも数円〜数十円程度の少額、新規Providerの追加なし。faster-whisperによるdisfluency QAはローカルCPU処理のみで追加API課金は無し
- **既知の限界(正直に記録)**: Point-only regenerationのFact安全性は自動化されておらず、今回のように生成物を人間(Claude)が個別に確認して差し戻す運用に依存している。恒久対策(再生成後にFact Checkerを自動実行し、REVIEW_REQUIRED/FAILなら自動的に差し戻すゲート)は今回実装していない
- **影響するCURRENT_SPEC項目**: 「Preview」節(B1 Comment 1-4話し方をPRODUCTION_WIREDへ、A2 Preview長さにNo.8反映済み注記を追加)、「QA / Human Review」節(Point重複検知+regenerationにMONITORING注記追加、Comment内部ラベル二重防御に訂正注記追加)、「Audio Assembly」節(No.8完成版再Assemble行を新設)
- **OPEN_ITEMSへの影響**: なし(OPEN-84/85/86は状態変更なしのまま維持、ユーザー指示通り)
- **状態**: 上記の通り項目ごとに異なる(`PRODUCTION_WIRED`4件、`MONITORING`1件、`USER_FINAL_REVIEW`1件)

## ER-008-N8-FINAL-QA-HARDENING-21(2026-08-29、Implementation Hardening + サービス・生成仕様混在)

- **背景**: ユーザーがNo.8最終試聴で6件の品質問題を報告した。うち3件(disfluency QA取りこぼし・Key Phrase gloss括弧書き・Point-only regeneration)は今回実装まで完了させ、残り3件(semantic consistency・Evidence Compression日付拡張・A2 In One Line速度)は調査・設計・コスト概算までを行い、ユーザー指定のSTOP条件に該当するため実装前にユーザー確認を求めることにした
- **内容**:
  1. **disfluency QA資産-記録紐付けの恒久修正(No.8 A2 kp2 "uneven choice"の実修正)**: 「disfluency QAはPRODUCTION_WIREDと報告済みなのに、実際の完成版音声に反復が残っていた」という報告を調査した結果、根本原因が3つ判明した。(a) `disfluency_checked`/`disfluency_evidence`が各生成関数のattempts_log内にしか記録されず、segment記録のtop-levelへ昇格されていなかった(6ファイルの生成関数すべてが同一パターンの欠落)。(b) `er003_v1_n3_01_assemble.py::verify_episode_audio_validation_gate()`がstatus=="OK"しか見ておらず、disfluency QAの証跡を一切参照していなかった。(c) `er006_master_audio_store_01.get_or_generate()`のcache hit reuse分岐が、生成時のQA証跡を運ばず最小限dict(status/path/reused/master_audio_idのみ)しか返さなかったため、QA合格済みの資産でも再利用のたびに証跡が失われる設計だった。kp2_en.wav自体は、disfluency QA配線(commit bef70c1、2026-08-29 08:08)より約24.5時間前(2026-08-28 07:31)にMaster Audio Store経由で生成された旧assetで、配線後もこの同じmasterがcache hit再利用され続けていた(sha256一致で確認、ファイル自体が生成後に差し替わった形跡はない)。恒久対策として3層を実装: (A) 上記6生成関数すべてでtop-level昇格、(B) Gateへ`_segment_missing_mandatory_disfluency_qa(name, entry, level)`を新設し、レベル別mandatory segment(B1: preview/comment_1-4/in_one_line/point_one_heading/point_two_heading、A2: in_one_line/point_one_heading/point_two_heading[preview/commentは日本語のため対象外と実装中に発見・修正]、Key Phrase英語は両レベル共通)についてtop-levelの`disfluency_checked is True`が無ければfail-closedでblockする、(C) Master Audio Store manifestへ`qa_evidence`を保存しreused=True側にも復元する。加えて`_segment_asset_hash_stale()`(記録済みsha256と実ファイルの突き合わせ)も新設した。No.8実データでは、新Gateにより過去生成された全English mandatory segment(A2/B1合計21件)が一旦block対象になったが、無料・ローカルのfaster-whisper再検査(`er008_n8_disfluency_backfill_21.py`)でkp2以外は全てクリーンと確認しbackfill(追加費用ゼロ)、kp2のみ実際に反復ありと再確認され、Master Audio Storeの該当manifest entry・音声ファイルを削除した上で本番経路(`shared_narration.ensure_key_phrase_english_component`)で再生成した(disfluency flagged=false、ASR EXACT_MATCH)。**状態**: `PRODUCTION_WIRED`(資産-記録紐付けまで確認済み)
  2. **Key Phrase日本語glossの括弧書き禁止**: No.8 A2のKey Phrase 1 gloss「搭乗前に列に並ぶ人（俗称）」が音声で読み上げると不自然な問題(OPEN-85)を調査し、発生源をKey Phrase選定段階(`er003_key_words_research10.py`が読み込むP2選定prompt、L/P/U全戦略共通の`ja_gloss`指示)と特定した(`er003_key_words_canonicalization.py`はglossを素通しするだけ)。3つのprompt template(`er003_v1_translator_briefs/b2_key_words_research10_{l,p,u}_prompt_template.txt`)へ「音声のみで意味が成立する自然な表現にする、括弧補足は避ける」指示を追加し、A2/B1で共通適用されるようにした。機械的Validatorも`validate_research10_selection()`へ追加(全角/半角括弧検知、新規API呼び出しなし)。No.8のA2 Key Phrase 1 glossを「ゲート前で早く並ぶ乗客を指す俗称」(B1と表現統一)へ修正し、本番経路で再TTS・ASR再検証(verified=true)。**状態**: `PRODUCTION_WIRED`、OPEN-85 CLOSE
  3. **Point-only regenerationのPRODUCTION_WIRED撤回**: ER-20で確認されたFact fabricationリスクを受け、ユーザーが「Point-only regenerationをProduction自動経路から外す」ことを正式決定した。`er003_v1_n3_01_articles_generate.py::POINT_ONLY_REGENERATION_ENABLED = False`(既定)を新設し、`run_point_overlap_qa_and_regenerate()`は overlap検知(monitoring)のみ行い、flag時も本文を一切書き換えず`NG_REVIEW_REQUIRED`として記録するだけに変更した(regenerate_point_only()自体は呼び出されない、回帰テストでLLM呼び出し0件を確認)。暫定Production方式として提案された「記事全体Writerを再実行、overlap再QA、NGなら最大2回retry、それでもNGならNG/REVIEW_REQUIRED」については、Writer実測コスト(No.8実測: writer_a2単独で約$1.50、writer_b1で約$1.35)を踏まえるとoverlap NG発生率(現時点で不明)次第でコストが数倍化する可能性があり、「Writer retry方式でProductionコストが大幅増」というユーザー指定のSTOP条件に該当し得ると判断し、今回はwiringまで到達していない(OPEN-88、ユーザー確認待ち)。**状態**: overlap検知は`MONITORING`として`PRODUCTION_WIRED`、Point-only regeneration自体は`PRODUCTION_WIRED`撤回・既定無効化
  4. **semantic consistency("wait"問題)の調査・STOP**: No.8で同一語"wait/waiting"が記事内で逆方向の意味(待たずに危険を冒す行動 vs 並んで安心する行動)を指している実例(A2/B1とも)を実データで確認した。既存QA(Fact Checker・Ledger Deviation Check・Point overlap QA)はいずれもこの種の記事内semantic consistencyを検査対象にしていないことをprompt/schema精査で確認した(Fact Checkerは外部事実整合、Ledger Deviationはfact ledger整合、Point overlap QAはPoint-Full Story間の言い換え検知が目的)。No.8内の他の高頻度語は簡易頻度スキャンで目視確認した限り同種の衝突は見つからなかった(網羅的LLM検査ではない)。対策候補(A: 記事全体LLM consistency check新設、B: 重要語抽出+疑わしいものだけLLM確認、C: Writer prompt予防的指示)を提示し、実測コスト参考値(writer $1.3〜1.5、research系各$0.2〜0.4)からAの追加コストを1記事$0.2〜0.6程度、1000記事/月換算$200〜600/月と概算したが、「有料LLM追加が大きな月次コスト増になる」というSTOP条件に該当し得るため実装せず、OPEN-87としてユーザー確認待ちとした。**状態**: `OPEN`(調査完了、実装は未着手)
  5. **Evidence Compressionの日付・数字拡張の調査・STOP**: ユーザーが方向転換し日付もCompression対象とすることを決定(OPEN-84)。No.8実データを調査し、April 14(発表日)とJune 8(9ゲート開設・確認日)という8週間差の2つの暦日、および"Dallas Fort Worth International Airport"という正式名称の2回出現(初出+再言及)を確認した。どちらの日付を残すか・空港名称の2回目言及を一般化すべきかは、記事の時系列理解・fact traceabilityに影響し得る編集判断であり、「情報欠落リスクが高い」というSTOP条件に該当し得ると判断し、具体案の確定と実装(Prompt変更・No.8再生成・Fact Checker再確認)はユーザー確認後に着手することとした。**状態**: `DECIDED`(方針)/`TBD`(具体案、OPEN-84更新)
  6. **A2 In One Line速度の調査・STOP**: A2全English segmentのWPM実測(topic_intro 129〜full_story_part1 145の範囲、in_one_line 127.1)、および6% slowdown適用比率(`{name}_original.wav`との尺比較、全segment 1.056〜1.060の範囲、in_one_lineも1.0595で他と同水準)を確認した結果、in_one_lineに機械的な二重減速(style指示+time-stretchの重複適用)は起きておらず、WPMも他segmentと1〜8%の差に留まることを確認した。「体感的に遅すぎる」の原因は計測可能な機械的バグではなく、内容の性質(要約文としての強調的な話し方をTTSモデルが選択している可能性)によると考えられる。新しい具体的WPM仕様(下限値の新設等)が必要な場合は「A2速度で新しい具体WPM仕様が必要」というSTOP条件に該当するため、実装前にユーザー確認が必要と判断した(OPEN-89)。**状態**: `TBD`(調査完了、実装は未着手)
  7. **No.8完成版の再Assemble**: 上記1・2の修正を反映するため、影響segmentのみ再TTS(A2: kp2_english・meaning_1[kp1 gloss]、他の旧mandatory segmentは無料ローカル再検査でクリーン確認のみ・TTS再生成なし)し、`stage_assemble_b1`/`stage_assemble_a2`を再実行した。新設したdisfluency QA必須証跡チェック・asset hash staleness チェックを含め、Audio Validation Gateは両レベルともPASS。A2: duration 359.34秒・peak 0.854・clipping無し。B1: duration 327.51秒(ER-20から変更なし)・peak 0.825・clipping無し。ユーザー最終試聴用Artifactを同一URLへ更新。**状態**: `USER_FINAL_REVIEW`
- **regression**: 本セッションで変更した箇所に対する targeted test実行、全128件PASS(`er008_disfluency_qa_18_test_01.py`[9件、うち2件は今回の実修正に合わせて更新]・`er008_audio_validation_gate_05_test.py`・`er008_a2_slowdown_invariant_19_test_01.py`[今回のGate拡張に合わせてfixture更新]・`er008_n8_qa_hardening_21_gate_test_01.py`[新規11件]・`er003_test_v1_n3_01_tts_generate.py`・`er003_test_key_words_research10.py`[新規2件含む]・`er008_n3_01_point_qa_wiring_19_test_01.py`[新規1件・既存1件を明示的有効化へ更新]・`er008_point_regenerate_19_test_01.py`・`er006_master_audio_store_01_test.py`[新規1件])。リポジトリ全体の`unittest discover`は、実行時間・API副作用のリスクを考慮し今回は実施していない(変更ファイルとその直接依存テストのみを対象とした)
- **API call数・コスト**: kp2_english再生成でTTS 2回・ASR 2回(1回目はqa_evidence backfillのMaster Audio Store修正前に実行したため、修正後に再度manifest entryを削除し再生成し直した)、kp1_japanese_meaning(gloss修正)でTTS 1回・ASR 1回。いずれも短い単語句のTTS+ASRで、比較可能な既存segment単価(tts_a2/tts_b1ステージ実績)から1件あたり$0.001未満と推定され、合計でも$0.01を大きく下回る(cost loggerの価格テーブルがこれらのmodel_idを未収載のため厳密な$算出はできなかったが、額としては無視できる水準)。disfluency backfill(21segment再検査)はローカルfaster-whisper実行のみで追加API課金は無し。semantic consistency/Evidence Compression拡張/Writer full retryはいずれも実装していないため、これらに起因する追加コストは今回発生していない
- **既知の限界(正直に記録)**: (1) semantic consistency・Evidence Compression拡張・Point-only regenerationの恒久的な代替方式は、いずれも設計候補の提示とコスト概算に留まり、実装はユーザー確認後になる。(2) disfluency QAのMaster Audio Store cache-key自体(schema version等)は変更していないため、将来また別の新しいQA種別を追加した際、同種の「既存cache済み資産にだけ新QAが適用されない」問題が再発し得る(今回はGate側のmandatory-evidence fail-closedチェックという、原因を問わず証跡の有無で機械的に判定する汎用的な防御で対応した)
- **影響するCURRENT_SPEC項目**: 「Disfluency QA」節(資産-記録紐付けの恒久修正を追記、`PRODUCTION_WIRED`維持)、「Point One/TwoとFull Storyの意味重複検知+Point-only regeneration」節(PRODUCTION_WIRED撤回を追記)、新設「Key Phrase日本語glossの括弧書き禁止」節、「No.8完成版 再Assemble(ER-21)」節を新設
- **OPEN_ITEMSへの影響**: OPEN-85をCLOSE、OPEN-84を投資調査結果で更新(未実装のまま)、OPEN-87/OPEN-88/OPEN-89を新規追加(いずれもユーザー確認待ち)、OPEN-86は変更なし
- **状態**: 上記の通り項目ごとに異なる(`PRODUCTION_WIRED`3件、`OPEN`/`TBD`3件、`USER_FINAL_REVIEW`1件)

## ER-008-N8-FINAL-CONTENT-COMPRESSION-RETRY-22(2026-08-29、No.8最終品質調整)

- **背景**: ER-21でOPEN化した3件("wait"意味衝突・Evidence Compression日付拡張・Point-only regeneration恒久方式)について、ユーザーが個別に方針を確定させた。加えてA2 In One Line speedの現状維持を確認し、semantic consistencyは低優先度Open Itemとして正式化した
- **内容**:
  1. **"wait"意味衝突のNo.8個別修正**: A2「... they may fear it will be full if they wait too long.」を「... if they stay seated too long.」へ、B1「If a passenger waits too long, there may be a small chance of missing a connection and then a flight.」を「If a passenger delays joining the line, there may be a small chance of missing a connecting flight.」へ、それぞれarticle.md/parts.jsonを直接修正した。修正前にVerified Fact Ledger(`research/verified_fact_ledger.txt`)を確認したところ、該当箇所はoverhead-bin容量という一般的な心理描写であり特定のFactに紐づく数値・主張ではないこと、既存のledger_deviation.json(A2/B1とも`LEDGER_COMPLIANT`・deviation 0件)がこの文言に依存していないことを確認した。影響segmentはA2/B1とも`full_story_part1`のみで、他segmentのテキストは無変更。**状態**: `RESOLVED`(No.8個別修正、恒久QAは未実装のままOPEN-87)
  2. **semantic consistency問題の低優先度Open Item化**: ユーザーが「汎用自動QAは今回実装しない(検出精度不足・コスト・Writer model upgrade時に再検討)」と正式決定。OPEN-87を`TBD`から`OPEN(低優先度、量産非Blocking)`へ変更し、量産移行の条件ではないことを明記した。**状態**: `DECIDED`(実装見送りを正式化)
  3. **Evidence Compression Editorへ日付・数値を圧縮対象化**: `er003_v1_n3_01_evidence_compression_editor.py`の許可編集リストへ、日付・数値の削減・一般化を追加した(「日付は必ず1個」という機械的hard ruleにはしない。時系列理解・ニュースの核心・Fact特定に必要な場合は残す。判断に迷えばFact safetyを優先し残す)。No.8実データ(A2/B1)へ実際にEditorを再実行して検証した結果、EditorはApril 14(発表日)を"earlier this year"へ一般化し、June 8(9ゲート開設・確認日)は一貫して残す判断をした。ただしEditor出力には日付とは無関係な副作用(B1で"Stephen Reicher"/"Kristie Tse"という既存承認済みの実名を"one/another psychologist"へ一般化)が混在していたため、Editor出力をそのまま採用せず、日付関連の文のみ手動でarticle.md/parts.jsonへ反映した(実名は維持)。プロンプト内容テスト(`er008_n8_evidence_compression_dates_22_test_01.py`、3件)で新ルール文言と既存禁止事項の共存を確認。**状態**: `PRODUCTION_WIRED`(日付ルール追加)、No.8個別反映は完了。空港正式名称は別問題としてOPEN-84継続
  4. **"Dallas Fort Worth International Airport"正式名称が残った理由の調査**: 既存のEvidence Compression Editor prompt(許可される編集リスト)を精査した結果、対象は「出典名」(企業・調査会社・研究機関・メディア・イベント名などの引用元名)のみで、ニュースの主題そのものである地名・施設名(空港名)は元々対象カテゴリに含まれていなかったことを確認した。したがって「評価した上で必要と判断して残した」のではなく「そもそもルールの対象外だった」が結論。ユーザー指示により今回は新しい固有名詞圧縮仕様を勝手に拡張せず、調査結果の報告とA2/B1それぞれの得失(A2は"one airport"/"a major U.S. airport"で足りる可能性、B1はニュースリテラシー上正式名称を残す価値がある可能性)を提示するに留めた。**状態**: `TBD`(仕様拡張要否はユーザー確認待ち、OPEN-84継続)
  5. **A2 In One Lineのstyle確認**: `er003_v1_n3_01_tts_generate.py::generate_a2_segments()`を再確認し、A2 In One LineはFull Story Part1/2・Point One/Twoと全く同じ`A2_ENGLISH_STYLE_PREFIX_SLOWER`(通常のA2英語style)+6% slowdownの経路を通っており、B1 Preview/Comment専用の`B1_PREVIEW_STYLE_PREFIX_CALM`はA2のどのsegmentにも適用されていないことを確認した(コード変更不要、ER-21の実測結果とも整合)。ユーザーからも新しい具体的WPM下限は要求されなかったため、OPEN-89は調査完了・対応不要としてCLOSEした。**状態**: `CONFIRMED`(コード変更なし)
  6. **Point overlap NG時のWriter full retry(最大2回)を正式実装**: `er003_v1_n3_01_articles_generate.py`の`run_one_pattern()`を、Writer呼び出し+Evidence Compressionを`_generate_and_compress_article()`ヘルパーへ共通化した上で、Point overlap QAをretryループ化した(`POINT_OVERLAP_ARTICLE_RETRY_MAX = 2`)。overlapがflagされた場合、Pointだけを差し替えず記事全体をWriterから再生成し(Full Story/Point One/Point Two/In One Line間の内部整合をWriterに保たせる)、overlapが解消するかretry上限に達するまで繰り返す。再実行するのはWriter→Evidence Compression→Point overlap QAの3工程のみで、Fact Checker・Ledger Deviation Check・Directional Fact Precheckはループの外(最終確定後)で一度だけ実行するよう設計し、不要な再実行を避けた。TTSより前の工程で完結するため、このretryによるTTS/ASR追加費用は発生しない。2回retryしても解消しない場合は自動続行せず`status="NG_REVIEW_REQUIRED"`を返し、Fact Checker以降を一切呼ばない。mock LLMによる単体テスト(`er008_n8_point_overlap_article_retry_22_test_01.py`、2件)で、(a)2回目のWriter呼び出しでoverlapが解消し最終記事がarticle.mdへ保存されるパス、(b)3回とも(初回+retry2回)overlapが解消せずNG_REVIEW_REQUIREDとなり、Fact Checker/Ledger Deviationの呼び出し回数が0であるパス、の両方を確認した。No.8自体のPoint One overlap(A2 ratio=0.40、B1 ratio=0.542、既存の暫定閾値0.40でflagされる水準)には今回この新方式を適用していない(既存の承認済み記事内容を無条件に書き換えないため、monitoring記録のまま維持)。**状態**: `WIRED`(mock test確認済み、実LLM end-to-end evidenceは次にPoint overlap NGが実データで自然発生した際に確認、それまでは`PRODUCTION_WIRED`を保留、OPEN-88参照)
  7. **No.8完成版の再Assemble**: 上記1・3の修正で本文が変わった4segment(A2: full_story_part1・full_story_part2、B1: full_story_part1・full_story_part2)のみ本番生成関数(`generate_a2_segment_with_slowdown`/`news_tail_fix.generate_news_narration_wide_margin`)で再TTS・ASR再検証し、他segmentは既存のVALIDATED/HUMAN_APPROVED音声をそのまま再利用した(`er008_n8_wait_and_date_fix_retts_22.py`)。canonical_textが変わったことでer011_human_review_lock_01が自動的に「新しいsegmentのバージョン」として扱い、通常のAUTO_PROCESSINGで再生成できた(明示的なapprove_regenerateは不要だった)。この過程で2件の未発見バグを実データで発見・修正した(詳細は下記8・9)。修正後、`stage_assemble_b1`/`stage_assemble_a2`を再実行し、Audio Validation Gate(disfluency QA証跡・asset hash整合・A2 slowdown invariantを含む)は両レベルともPASS。A2: duration 357.145秒(5:57)・peak 0.90634・clipping無し。B1: duration 323.314秒(5:23)・peak 0.89835・clipping無し。ユーザー最終試聴用Artifactを同一URLへ更新。**状態**: `USER_FINAL_REVIEW`
  8. **[想定外の発見・修正] ASR検証の短縮形(contraction)誤検知バグ**: B1 full_story_part2の再生成中、TTSが自然に"They are"を"They're"と発話しただけで、3回中3回ともTRUE_CONTENT_MISMATCHと誤判定されretryが尽きてSTOPPEDになる事象を発見した。原因調査の結果、`er006_preprod_hardening_01_validation.py::normalize_text()`がアポストロフィを空白へ置換するため"they're"が"they"+"re"の2 tokenへ分かれ、canonical側の展開形"they are"の"are"は既にstopwordだが、ASR側短縮形の残骸"re"はstopword集合に無く、意味の変化が無いのに孤立したcontent_word_diffとして検出されていたことが判明した。`_STOPWORDS`へ"re"を追加して修正(実データで確認済みの範囲に限定し、"will"/"have"由来の"ll"/"ve"は別の診断[replace型diff]が必要なため今回は対象外、OPEN-90参照)。既存55件のfixture回帰(`er006_preprod_hardening_01_validation_test.py`)は全PASSのまま、新規2件のcontraction fixtureを追加。この修正はNo.8に限らず、ASR検証を使う全segment・全記事に影響する(TTSが自然な短縮形で発話するたび不要なretry/Human Reviewを起こしていた可能性がある)。**状態**: `PRODUCTION_WIRED`(共通の安全側修正)
  9. **[想定外の発見・修正] A2 slowdown post-processでsha256が再計算されていなかったバグ**: full_story_part1/2再生成後、ER-21で追加したAssemble Gateの`_segment_asset_hash_stale()`が両segmentを`ASSET_HASH_MISMATCH`でblockした。調査の結果、`apply_a2_slowdown_postprocess()`が6% time-stretchでout_pathの中身を差し替えた後、`duration_seconds`/`trim_info`は比例配分で更新していたのに`sha256`だけ取り残されており、記録されたsha256が常にslowdown前の(=もう存在しない)ファイルのものになっていたことが判明した。A2の英語body全segment(full_story/point/in_one_line、`A2_SLOWDOWN_TARGET_SEGMENTS`)がこの経路を通るため、sha256が記録されているケースは全て同じ理由でGateに引っかかりうる潜在バグだった(ただし大半の既存segmentはsha256自体が未記録[None]で、ER-21のstaleness checkは「未記録は証跡なしとしてスキップ」という設計のため、これまで顕在化していなかった)。post-process後のout_pathからsha256を再計算するよう修正し、単体テスト2件(`er008_n8_a2_slowdown_sha256_refresh_22_test_01.py`)を追加。**状態**: `PRODUCTION_WIRED`
  10. **[想定外の発見・修正] B1 full_story_part1の実在心理学者名"Stephen Reicher"のTTS発音誤り**: full_story_part1再生成後、独立した4回のASR(OpenAI Primary×2、Azure Secondary×2)すべてが一貫して"Steven Reichert"に近い形で書き起こし、`ASR_VALIDATION_UNCERTAIN`でHuman Review行きになった。既存の固有名詞発音調査機構(Pronunciation Ledger research、ER-010由来)が自動的に外部ソース(本人の発音訂正記録を含む)を調査し、正しい発音はIPA `/ˈraɪkər/`("RY-ker"、Star Trekの"Riker"と同じ発音、高確信度)と判明した。4回全てが同じ方向へ一貫して誤ったことから、単発のASR誤認識ではなくTTS自体の発音誤りである可能性が高いと判断し、ER-010の日付safe-reading("April 28"→"April twenty eighth")と同じ設計思想で、記事本文の表示用綴り(article.md/parts.json)は"Stephen Reicher"のまま変更せず、TTS入力・ASR比較対象のテキストにのみ"Reicher"→"Riker"を適用する`tts_safe_name_pronunciation_en()`を新設し`tts_safe_news_en()`へ配線した。適用後、1回目の生成で`asr_verified=True`(ASR: "Stephen Riker"、完全一致)を確認。単体テスト3件(`er008_n8_reicher_pronunciation_22_test_01.py`)を追加。**状態**: `PRODUCTION_WIRED`(実在人物名のため、念のためユーザーにも本レポートで個別に発音根拠を提示する)
- **regression**: 新規/変更テストを対象実行、全139件PASS(`er008_n8_point_overlap_article_retry_22_test_01.py`[新規2件]・`er008_n3_01_point_qa_wiring_19_test_01.py`[既存3件、影響なし確認]・`er008_n8_evidence_compression_dates_22_test_01.py`[新規3件]・`er006_preprod_hardening_01_validation_test.py`[既存55件+新規2件]・`er006_secondary_asr_01_test.py`・`er007_en_blindspot_test_01.py`・`er010_entity_phonetic_corroboration_01_test_01.py`[contraction/entity関連の既存回帰、影響なし確認]・`er008_n8_a2_slowdown_sha256_refresh_22_test_01.py`[新規2件]・`er008_n8_reicher_pronunciation_22_test_01.py`[新規3件]・`er008_a2_slowdown_invariant_19_test_01.py`・`er008_n8_qa_hardening_21_gate_test_01.py`・`er006_master_audio_store_01_test.py`・`er003_test_key_words_research10.py`・`er008_disfluency_qa_18_test_01.py`)。プロジェクト全体`run_project_regression.py`は1922件中1918件PASS(失敗4件はER-21から継続する既知の無関係な事象: 3件は「テスト総数が増えると自動的に不一致になる」既存の帳簿的meta-test、1件は無関係な日本語TTSリトライのモックテスト)
- **API call数・コスト**: (a) Evidence Compression Editor再実行(日付ルール検証用、A2/B1各1回)は実測でA2 in=1685/out=685 tokens、B1 in=1659/out=756 tokens(writer_a2/writer_b1と同じ価格帯、1回あたり$0.01未満)。(b) full_story_part1/part2再TTS・ASR(A2/B1各2segment、計4segment)は既存のnews本文segment単価(No.8実績のtts_a2/tts_b1ステージ平均$0.0005〜0.0008/件)と同水準。(c) Point overlap Writer full retryは今回No.8へ未適用のため追加コスト無し。Writer full retryの将来コスト試算(No.8実測writer_a2 $0.183/call・writer_b1 $0.185/call、A2+B1ペア基準): retry 0回=$0.368/pair(基準)、片方が1回retry=+$0.18〜0.19、両方が1回ずつretry=+$0.368、両方が上限2回retry=+$0.735。月間換算(retry率は実績が乏しいため複数シナリオで提示): 低め(20%の記事pairが平均1.3回retry、100/500/1000記事で+$9.6/$47.8/$95.7)、No.8実績相当(50%が平均1.3回、+$23.9/$119.6/$239.2)、高め(100%が上限2回、+$73.5/$367.5/$735.0)。実際の運用でPoint overlap NGが発生した際に実測retry率を記録し、この試算を更新する
- **既知の限界(正直に記録)**: (1) Point overlap Writer full retryはコード配線・mock testまでで、実LLM呼び出しによるend-to-end動作は未確認(次回の自然発生を待つ)。(2) Evidence Compression Editorは、指示範囲外のテキスト(実名等)も呼び出しごとに変わりうることが今回実データで判明したため、当面は生成結果を無条件採用せず人手で差分レビューする運用とする(Editor自体のprompt厳格化は今回のスコープ外)。(3) 空港正式名称の扱いは仕様として未確定のまま(OPEN-84)。(4) contraction誤検知バグの修正は実データで確認された"'re"(are由来)のみに限定しており、"will"/"have"由来の"'ll"/"'ve"は別型のdiff(replace型)になるため未修正のまま(OPEN-90)。(5) `_NEGATION_WORDS`に"isnt"/"dont"等アポストロフィ無しの短縮形が定義されているが、`normalize_text()`の現在のtokenize方式ではアポストロフィが空白に置換されるため、これらのtoken自体が生成されず実質的に到達不能なコードであることを調査中に発見した(否定検出という安全性の高い機能に関わるため、今回は範囲外として触れず、OPEN-90にまとめて記録する)
- **影響するCURRENT_SPEC項目**: 「Evidence Compression(方式C、Lossless Editor)」節(日付・数値ルール追加を追記)、「Point One/TwoとFull Storyの意味重複検知+Point-only regeneration」節(Writer full retry実装を追記)、「Audio Validation Gate」節(sha256再計算バグ修正を追記)、新設「ASR検証のcontraction対応」節、新設「B1固有名詞発音safe-reading(Stephen Reicher→Riker)」節、「No.8完成版 再Assemble(ER-22)」節を新設
- **OPEN_ITEMSへの影響**: OPEN-84を日付圧縮実装結果で更新(空港正式名称のみ引き続きTBD)、OPEN-87を低優先度Open Itemとして正式化、OPEN-88をWriter full retry実装結果で更新、OPEN-89をCLOSE、OPEN-90を新設(contraction"'ll"/"'ve"未対応・否定短縮形token到達不能問題)、OPEN-85/86は変更なし
- **状態**: 上記の通り項目ごとに異なる(`RESOLVED`1件、`DECIDED`2件、`PRODUCTION_WIRED`4件、`TBD`1件、`CONFIRMED`1件、`WIRED`1件、`USER_FINAL_REVIEW`1件)

## ER-008-N8-FINAL-PRODUCTION-HARDENING-23(2026-08-29、Evidence Compression地名拡張・A2 In One Line速度調査・Point overlap Writer retry実runtime検証・固有名詞発音表示ルール)

- **背景**: ER-22の残課題(OPEN-84空港正式名称、OPEN-88実runtime evidence)への対応と、ユーザー自身の試聴でA2 In One Lineの速度・Stephen Reicherの発音に新たな懸念が出たための追加調査
- **内容**:
  1. **Evidence Compression Editorへ地名・施設名の圧縮を追加**: `er003_v1_n3_01_evidence_compression_editor.py`の許可編集リストへ「学習者の理解に不要な地名・空港名・施設名等の一般化」を追加した(日付/数値と同じ「hard ruleではない、Fact safety優先」の設計)。プロンプト内容テスト`er008_n8_evidence_compression_locations_23_test_01.py`(4件)で新ルール文言・既存禁止事項との共存を確認。**No.8実データへ実際にEditorを再実行**した結果、A2/B1とも一貫して"Dallas Fort Worth International Airport"→"Dallas Fort Worth"への圧縮を提案した。この変更のみをNo.8のarticle.md/parts.jsonへ反映しようとしたところ、**適用前に必須とされたFact Check再実行でREVIEW_REQUIRED(4件の指摘)を検出**した。指摘内容を精査した結果、地名圧縮とは無関係な既存記述(「flight attendants」という帰属の妥当性、電子ゲート導入目的の因果関係の記述、2024年の別施策との混同、"safety and control"という心理学的説明の裏付け不足)であり、ベースライン(圧縮前、現行本番テキスト)のFact Check結果は`PASS`だった。ライブweb検索を伴うFact Checkは再実行のたびに結果が変動しうるため、これはEditorの地名圧縮が原因ではなく、既存記述に対するFact Checkerの非決定性(再実行時に異なるweb検索結果を拾った)である可能性が高いと判断した。ユーザー指示「Fact Check/Ledger DeviationもPASSさせる」を満たせなかったため、**article.md/parts.json/音声への適用は見送り**、候補内容を`{a2,b1b}/audit/evidence_compression_locations_23_candidate.json`に記録するのみとした。**状態**: プロンプト/ロジック自体は`PRODUCTION_WIRED`(test済み、実LLM runで意図通りの圧縮を確認、以後生成される全記事に自動適用される)。No.8自体への適用は`BLOCKED_PENDING_USER_DECISION`(OPEN-84継続、Fact Check非決定性の扱いも新たな論点として追加)
  2. **A2 In One Line速度の再調査**: コードレベルでは、A2の`full_story_part1/2`・`point_one`・`point_two`・`point_one_heading`・`point_two_heading`・`in_one_line`は全て同一の`A2_ENGLISH_STYLE_PREFIX_SLOWER`+6% slowdownを通っており(ER-22で確認済みの通り、二重減速やB1専用styleの混入は無い)、コードの原因ではないことを再確認した。一方、**実測WPM**(実ファイルのduration・実テキストの単語数から算出)では、現在本番採用中のA2 in_one_line音声は127.1 WPM(6%減速後)/134.7 WPM(減速前)で、A2の英語body segment中最も遅く、Full Story(140.5〜146.7 WPM)より明確に遅かった。ただし、**同じTTS入力テキストをそのまま2回追加生成した実測**では137.2 WPM・137.7 WPM(いずれも減速前換算で145.3/145.8 WPM相当)となり、Full Story/Point本文の速度帯(136〜147 WPM)にほぼ収まった。leading/trailing silenceのmargin(実測0.6秒程度/17秒中)はWPM差(約13〜15%)を説明できるほど大きくない。以上から、**現在の本番音声はTTS生成のrun-to-run variance(1回ごとの自然なばらつき)の中でも遅めの1回を採用してしまった結果である可能性が高く、In One Line固有の隠れた仕様や二重減速のバグではない**と判断した。B1側でもIn One Line(143.8 WPM)はFull Story(155.9〜164.1 WPM)よりは遅く、同種の傾向(短い segmentほど平均WPMが下がりやすい)がA2に限らず存在することも確認した。全segmentの実測WPM表は本ターン完了報告で提示する。**対策候補**: (a) 現状維持、(b) 複数回生成して基準WPM帯に近いテイクを採用する運用へ変更(要仕様決定・追加コスト)、(c) 短いsegment向けにWPM許容下限のGateを新設する(要仕様決定)。ユーザー指示通り**仕様変更は行わず、調査結果の提示のみでSTOP**する。**状態**: `TBD`(調査完了、対応要否はユーザー判断待ち、新規OPEN項目として記録)
  3. **Point overlap Writer full retryの実Writer/API runtime evidence取得**: ER-22はmock LLMによる制御フロー検証のみだったため、`er008_n8_point_overlap_writer_retry_realapi_23.py`を新設し、初回(attempt 0)はovarlapする既存fixture記事(無償)を与えた上で、**retry(attempt 1)には実際のOpenAI Writer API・No.8 A2で実際に使われたprompt.txt・実Verified Fact Ledgerを使用**して実行した。結果、実Writerが記事全体を1回で再生成し、Point overlap QA(決定的な字面一致率判定、LLM不使用)が新記事をoverlapなしと判定してretryループが正しく終了、その後**実Fact Checker・実Ledger Deviation Checkが実際に1回だけ呼ばれた**ことを確認した(Point-only regenerationは呼ばれず、`POINT_ONLY_REGENERATION_ENABLED=False`を維持)。この実行のコストは実測$0.7861(Writer規約再生成 約$0.11 + Fact Checker 約$0.4753[検索込み] + Ledger Deviation 約$0.2033)。この検証用に生成された記事自体はFact Check `REVIEW_REQUIRED`・Ledger Deviation 3件を返したが、これはretry機構(Point重複の解消)の検証対象外であり、通常のWriterパイプライン品質のばらつきの範疇(retry機構のバグではない)。既存のmock test(`er008_n8_point_overlap_article_retry_22_test_01.py`)と合わせ、制御フロー(mock)・実API経路(realapi)の両方でretry上限・NG時のFact Checker/Deviation未呼び出し・Point-only regenerationの不使用を確認した。**状態**: `PRODUCTION_WIRED`(実Writer/API runtime evidence取得済み、OPEN-88解消)
  4. **固有名詞発音のHuman Review表示ルールを新設・Stephen Reicher発音の再検証**: (a) ユーザーから、No.8 B1のStephen Reicher発音が現在/ˈreɪkər/(RAY-ker寄り)に聞こえるとの報告を受け、ER-22で採用した根拠(Pronunciation Ledgerのconfidence="high"、IPA `/ˈraɪkər/`)を再検証した。再調査の結果、唯一の一次情報源が英国covid公聴会の**テキスト書き起こし**(音声ではない)であり、本人が名字を訂正して名乗った事実は伝えるが発音の音そのものは伝えないこと、他の引用元の一部が別人("Steve Reich"作曲家、"Stephen Richer"米州議会議員、"Stéphane Richer"元NHL選手)を指す無関係な情報だったことが判明し、**confidence="high"は根拠不十分だったと判断**した。Pronunciation Ledgerの当該entryを`confidence="medium"`へ手動で訂正し、根拠の限界を`ambiguity_note`に追記した。一方、ER-22で実際に生成・採用された音声のASR再検証結果は"Stephen **Riker**"(意図した綴りへの完全一致)であり、もしTTSが実際に/eɪ/寄りで発話していれば通常ASRは"Raker"/"Rayker"に近い書き起こしになるはずで、この一致は現在の音声が意図通り/aɪ/寄りで発話されている可能性を支持する一定の根拠になる。**現時点では「確実に誤り」とする根拠が無いため再TTSは行わず**、この評価根拠をユーザーへ提示し、改めての試聴判断を仰ぐこととした。(b) 恒久対策として、`er006_pronunciation_research_01.py`のPerplexity調査プロンプトへ「confidence="high"は本人の音声ソースが確認できた場合のみ、テキスト書き起こしのみの場合はmedium以下」という基準を追加し、`er006_secondary_asr_01.py::evaluate_attempt_with_cascade_detail()`で、lookup/research失敗時にspanをHuman Reviewパッケージから黙って省略していた既存の欠落(silent drop)を修正し、確定不能な場合は明示的に`confidence="unconfirmed"`のentryを必ず残すようにした(ユーザー新運用ルール「IPAが確定不能ならその旨を必ず表示する」への対応)。単体テスト1件(`er006_secondary_asr_01_test.py::test_case_b_unresolved_entity_research_failure_still_reports_unconfirmed`)を追加。**状態**: 表示ルール・confidence基準は`PRODUCTION_WIRED`。Reicher個別の発音要否判断は`USER_DECISION_REQUIRED`
- **regression**: 対象テスト`er008_n8_evidence_compression_locations_23_test_01.py`(新規4件)・`er008_n8_evidence_compression_dates_22_test_01.py`・`er008_n8_point_overlap_article_retry_22_test_01.py`(既存9件、影響なし確認)・`er006_secondary_asr_01_test.py`(新規1件含む20件、全PASS)。プロジェクト全体`run_project_regression.py`は1926件中1922件PASS(失敗4件はER-22から継続する既知の無関係な事象、新規失敗なし)
- **API call数・コスト(実測)**: (a) Evidence Compression地名圧縮の候補生成(A2/B1各1回、実行のみでNo.8へ不採用)は各$0.01未満(dates-22の再実行と同水準)。(b) Fact Check/Ledger Deviation再検証(A2/B1各1回)は合計で$0.5前後(web検索7回分を含む)。(c) A2 In One Line速度検証の追加TTS生成2回は本番同等単価(1回あたり$0.001未満)。(d) Point overlap Writer full retryの実API検証1回は実測$0.7861(内訳: Writer規約再生成約$0.11、Fact Checker約$0.4753、Ledger Deviation約$0.2033)。この実測値から、ER-22で概算した将来コスト試算(retry 0回=$0.368/pair基準、片方1回retry=+$0.18〜0.19等)は同じ桁数で妥当だったことを確認した。**重要な注記**: Fact Checker・Ledger Deviation Checkはretryループの外で1回だけ実行される設計のため、retry回数が増えてもこれらのコストは増えない(増分コストはWriter[+Evidence Compression]呼び出し分のみ)。retry上限(2回)に達しNG_REVIEW_REQUIREDになった場合は、Fact Checker/Ledger Deviationが一切呼ばれないため、そのケースはむしろ成功パスよりコストが低い。月間実コストは実際の自然発生retry率のデータが無いため、ER-22の複数シナリオ試算を暫定値として維持する(実際にNGが発生し始めた時点でシナリオを実測値へ更新する)
- **既知の限界(正直に記録)**: (1) 地名・施設名圧縮ルールはプロンプト・テストまで完了しているが、No.8自体には未適用(Fact Checkの非決定性という新たな論点が浮上したため)。(2) A2 In One Line速度は原因調査のみで、対応方針は未確定。(3) Point overlap Writer full retryは実API経路で1回のみ実証しており、複数回のNG→2回目retryまで到達する実例はまだ実データで確認していない(mock testでは確認済み)。(4) Fact Checkerがライブweb検索に依存するため、同じ記事に対して再実行するたびに異なる検証結果(PASS⇄REVIEW_REQUIRED)を返しうるという非決定性が今回新たに実データで確認された。これは今回の変更が原因ではなく既存のFact Checker設計の性質だが、「Fact CheckをPASSさせる」ことを機械的な適用条件にする場合の運用上の課題として新たに記録する必要がある
- **影響するCURRENT_SPEC項目**: 「Evidence Compression(方式C、Lossless Editor)」節(地名・施設名ルール追加を追記)、「Point One/TwoとFull StoryのWriter full retry」節(`PRODUCTION_WIRED`へ更新)、新設「固有名詞Human Review表示ルール(IPA/pronunciation guide/source/confidence必須表示)」節
- **OPEN_ITEMSへの影響**: OPEN-84を更新(地名圧縮ルール自体はPRODUCTION_WIRED、No.8適用はFact Check非決定性によりBLOCKED、空港名の仕様拡張要否は引き続きユーザー判断待ち)、OPEN-88をCLOSE(実runtime evidence取得完了)、新規OPEN-91(A2 In One Line速度、TBD)、新規OPEN-92(Fact Checkerのライブ検索非決定性、TBD)を追加
- **状態**: 上記の通り項目ごとに異なる(`PRODUCTION_WIRED`3件[地名圧縮ロジック・Point overlap retry・発音表示ルール]、`BLOCKED_PENDING_USER_DECISION`1件、`TBD`2件、`USER_DECISION_REQUIRED`1件)

## ER-008-N8-FINAL-CLOSEOUT-24(2026-08-29、地名/施設名CompressionのNo.8正式反映・Writer Point Balance prompt強化・cost計算バグ修正・Stephen Reicher PASS確定)

- **背景**: ER-23で見送った地名/施設名Compression(Fact Check非決定性でBLOCKED)・Point overlap Writer retryの実測コスト($0.7861/retry)・A2 In One Line速度・Stephen Reicher発音のそれぞれについて、ユーザーが最終判断を下し、closeoutを指示
- **内容**:
  1. **地名/施設名CompressionをNo.8へ正式反映**: ユーザーが「地名圧縮自体がFact Checkエラーを起こしたものではない」と整理し、無関係なFact Check結果だけでblockしない方針を確定。`er008_n8_location_compression_24.py`を新設し、"Dallas Fort Worth International Airport"→"Dallas Fort Worth"をA2 full_story_part2、B1 full_story_part2/in_one_lineの計3箇所へ機械的に反映(該当箇所以外は無変更)。影響を受けた3segmentのみ再TTS・ASR再検証を実施し、全件`asr_verified=true`を確認した。適用後の確認Fact Check/Ledger Deviationは、A2がFact Check`REVIEW_REQUIRED`(3件)/Deviation`LEDGER_COMPLIANT`(0件)、B1がFact Check`PASS`/Deviation`LEDGER_DEVIATION`(2件)という結果だった。B1の指摘1件は編集後の文に"Dallas Fort Worth"を含んでいたため、事前に用意したキーワードスクリーン(`_mentions_edit`)が自動的にflagし、スクリプトは安全側でAssembleを一旦停止した。人手でissue本文を精査した結果、実質的な指摘は"a more controlled digital process ... has now deployed"という表現がLedgerの裏付け(設計意図・導入事実)を超えて運用効果まで確立済みであるかのように読める、という地名とは完全に無関係な既存の懸念であり(編集前の原文"at Dallas Fort Worth International Airport"でも全く同じ文構造・同じ懸念が成立する)、地名圧縮が原因で新たに発生した問題ではないと判断し、採用へ進めた。A2の3件も同様にflight attendants帰属・safety/control表現・e-gate導入目的の因果関係という、地名と無関係な既存記述への指摘だった。以上の判断根拠を`er008_output/n8_location_compression_24_summary.json`の`adoption_decision_override`に明記した上で、Audio Validation Gateを経てA2・B1を再Assemble(A2 359.7秒/B1 318.5秒、いずれもclipping無し、peak 0.91/0.90)し、完成版へ反映した。**状態**: `PRODUCTION_WIRED / CLOSED`(OPEN-84解消)
  2. **Writer Point Balance promptの強化**: `er003_v1_n3_01_articles_generate.py`のCOMMON_BLOCK_TEMPLATE内、Point One/Twoの役割を定める節へ、(a)Main Storyの中心的なlogic・結論を語彙だけ変えて再説明することの明示的禁止、(b)Pointが追加すべき内容の具体例拡張(切り口/示唆/背景/**心理/社会的含意/別の因果/実生活上の解釈**/意味づけ)、(c)「Pointを書く前にMain Storyの主要論点を特定し、それを避けて構成する」という生成手順の推奨、(d)Point One・Point Two同士が異なる役割を持つことの明示、を追加した(新Fact追加禁止・Ledger範囲内・既存の長さ目標[30-60/25-70語]は無変更)。プロンプト内容テスト`er008_n8_point_prompt_strengthen_24_test_01.py`(8件)で、新旧の禁止事項・カテゴリが両立していることを確認。**実証**: No.8の実Topic・実Verified Fact Ledgerを使い、強化前(OLD)/強化後(NEW)のprompt each 4回、実OpenAI Writer APIで新規記事を生成し(`er008_n8_point_prompt_ab_24.py`、No.8の承認済み完成稿は一切変更していない)、Point-Full Story lexical overlap率(`er008_point_overlap_qa_18.lexical_overlap_ratio`、無償・決定的なlexicalチェック)を比較した。結果: 平均overlapが0.293→0.244、overlap QA閾値(0.40)超過によるretry対象率が25%(4件中1件)→0%(4件中0件)へ低下した。サンプル数が小さい(各4件)ため統計的に確定的な結論ではないが、方向は狙い通りだった。定性的にも、OLD条件の高overlap事例(overlap=0.538)はFull Storyの電子ゲート機能説明をほぼ再掲していたのに対し、NEW条件の一例は同じFactに対し「これは航空会社自身の自己申告であり、独立した効果検証は示されていない」という一段深めた視点を新Fact追加なしで加えていた。**状態**: `PRODUCTION_WIRED`(以後生成される全記事に自動適用)
  3. **retry marginal costの訂正(cost計算モジュールのバグ修正)**: ER-23の「Point overlap retry 1回=$0.7861」という実測値を、今回のcost試算(§4のretry marginal/total分離要求)のために再検証したところ、共有のcost計算モジュール`er005_stage7_cost_compute.py::record_cost()`が、providerが"openai"のrecordを、実際に使用したmodel_id(Writer/Fact Checker/Deviation Checkは全て`gpt-5.6-luna`)に関わらず常に`gpt-5.6-sol`単価(入力$5/M・出力$30/M)で計算していたバグを発見した。`gpt-5.6-luna`の実単価は入力$0.2/M・出力$1.2/M(sol比で概ね1/25)であり、この誤りにより過去の関連コスト試算(ER-23の$0.7861、`er003_v1_n3_01_articles_generate.py`内コメントの「writer_a2単体で約$1.5」等)は実際より大幅に(生成コスト部分だけで約25倍)過大だったことが判明した。`record_cost()`をrecord自身のmodel_idに応じて価格を引き直すよう修正した(`er008_n8_cost_compute_pricing_fix_24_test_01.py`4件PASS、model_id欠落時はsol単価へfallbackする後方互換を維持)。本モジュールは現状他のどのスクリプトからもimportされておらず[grep確認済み]、修正によるリスクは無い。**正しい実測値**(No.8実データの実トークン数): Writer記事全体retry1回の純増分コスト(Writer規約再生成+Evidence Compression Editor再生成)は約$0.0049(Writer $0.0037+EC Editor $0.0012)。Fact Checker・Ledger Deviation Checkは合計約$0.107(Fact Checkerのweb検索tool手数料$0.08が大半)だが、これは記事1本につき必ず1回発生する固定costであり、retry回数を増減させても変わらない。**期待コスト再計算**: 初回Point NG率を5%/10%/25%と仮定した場合、A2+B1ペア(2 label-generation)あたりの期待増分コストは1記事につき$0.00049/$0.00098/$0.00246であり、月100/500/1000記事でも最大$0.05/$0.25/$0.49(5%)〜$0.25/$1.23/$2.46(25%)程度と、無視できる水準である(旧$0.7861ベースの試算とは全く異なる結論になる)。**状態**: cost計算ロジック修正済み・訂正後の数値をDECISION_LOG/OPEN-88へ反映
  4. **A2 In One Line速度**: ユーザーが現状維持を正式決定(TTS生成のvarianceによる遅めのテイクだった可能性が高いという前回の調査結論を受け入れ)。WPM下限Gate新設・複数テイク運用のいずれも導入せず、追加TTSも実施していない。**状態**: `DECIDED`(OPEN-91を現状維持でclose)
  5. **Stephen Reicher発音のPASS確定**: ユーザーがNo.8の実際の音声を再試聴し、「/aɪ/寄り(RY-ker)に聞こえる」と判断したため、既存音声をPASSとして確定し、再生成しなかった。Pronunciation Ledgerの当該entryへ、この確認結果と「confidenceは根拠の性質[音声ではなくテキスト書き起こし由来]を反映してmediumのまま維持する」旨をambiguity_noteへ追記した(`er006_pronunciation_ledger_01.upsert()`経由)。ER-23で新設した固有名詞Human Review表示ルール(表記・IPA・確定不能ならその旨・pronunciation guide・source・confidence)は今後も継続する。**状態**: `DECIDED`(No.8個別PASS確定)
- **regression**: `run_project_regression.py`で1938件収集・1934件PASS・4件失敗(いずれもER-23以前から継続する既知の無関係な事象[`er003_test_bad`のfixture、`er003_test_p2j_investigate`の過去カウント照合、`er007_ja_tts_retry_path_fix_test_01`]、新規失敗なし)。新規テスト16件(Point prompt強化8件、cost計算バグ修正4件、既存の`er008_n8_evidence_compression_locations_23_test_01.py`等は無変更のままPASS)は全てPASS
- **API call数・コスト(実測、正しい単価で算出)**: (a) 地名圧縮の再TTS・ASR(3segment)は本番同等単価で数セント未満。(b) 地名圧縮適用後のFact Check/Deviation確認(A2/B1各1回)は合計で約$0.21(うちFact Checkerのweb検索tool手数料が大半)。(c) Writer Point Prompt A/B比較(OLD/NEW各4回、計8回の実Writer呼び出し)は合計で約$0.03(1回あたり約$0.0037)。(d) 音声のmp3再エンコード(ffmpeg、ローカル処理、API課金なし)。合計で本ターンの追加API実費は$1未満
- **既知の限界(正直に記録)**: (1) B1のLedger Deviation指摘(2件)のうち1件は、"a more controlled digital process ... has now deployed"という表現自体への懸念であり、地名圧縮とは無関係だが、記事の表現として実際に残存する既存の技術的な過大表現の可能性があるため、将来的に別途レビューする余地がある(今回のスコープ[地名圧縮の可否判断]の対象外として扱った)。(2) Point Prompt強化の効果検証はn=4×2条件と少数サンプルであり、大規模な統計的検証ではない。(3) Fact Checkerのライブ検索非決定性(OPEN-92)自体は今回も解消していない。(4) `er005_stage7_cost_compute.py`は本来ER-005当時の解析専用モジュールであり、その後の記事生成コスト分析に流用され続けてきたことで単価バグが temporarily 実際の判断(Point-only regenerationを見送る根拠の一つ)に影響していた可能性があるが、当時の判断自体(Fact fabricationの実例が確認されたこと)は本バグと無関係な別の理由によるものであり、覆す必要はないと判断した
- **影響するCURRENT_SPEC項目**: 「Evidence Compression(方式C、Lossless Editor)」節(No.8への正式反映を追記)、「Point Balance(言い換えによる重複の禁止・強化)」節(新設)
- **OPEN_ITEMSへの影響**: OPEN-84をCLOSE(No.8への正式反映完了)、OPEN-88のcost試算を訂正、OPEN-91を`DECIDED`(現状維持で確定)、OPEN-92は`TBD`のまま維持
- **状態**: `PRODUCTION_WIRED`4件(地名圧縮No.8適用・Point Balance prompt強化・cost計算バグ修正・No.8完成版反映)、`DECIDED`2件(A2 In One Line現状維持・Reicher PASS確定)

## ER-008-N8-CLOSEOUT-GOVERNANCE-25(2026-08-29、Fact Checker retry cap調査・Production全体loop横断監査・No.8 Point overlap記録整理・cost報告円ベース化・試聴Artifact全script掲載標準化)

- **背景**: No.8完成後のProduction運用を安全にするため、ユーザーが5点のgovernance課題(Fact Checker retry cap・Production全体の無限loop候補・No.8 Point Oneの記録整理・cost報告の通貨・試聴Artifactの全script掲載義務化)を提示し、調査と必要最小限の実装を指示。No.8音声そのものはユーザー最終試聴済みでOKのため、不要な再生成は行わない方針
- **内容**:
  1. **Fact Checker retry cap調査**: `er002_ja_web_research_r3.py::run_fact_checker_with_gates()`を精査した結果、`MAX_FACT_CHECK_ATTEMPTS=2`は「初回+技術的失敗(Web検索未使用/JSON解析失敗)時のみ最大1回の技術再試行」という設計であり、**verdict(PASS/REVIEW_REQUIRED/FAIL)を理由に再試行する経路は存在しない**ことを確認した(パース成功時点でverdictに関わらず即座に確定)。Ledger Deviation Check(`er003_v1_en_direct_vfl_01_generate.py::run_deviation_check()`)にはretryロジック自体が無い。ユーザー提案の基本方針「初回+retry最大2回、その後STOP」よりも現行実装の方が厳格(実質的にverdictに対しては初回で確定)であるため、**追加のcap実装は不要**と判断した。regression test`er008_n8_fact_check_retry_cap_25_test_01.py`(4件)で、PASS/REVIEW_REQUIRED/FAILいずれのverdictでも呼び出しが1回で確定すること、技術的失敗時のretry上限が引き続き機能することを固定した。**状態**: `DECIDED`(既存実装のまま安全と確認、コード変更なし)
  2. **Production全体の無限loop横断監査**: TTS(標準+fallback、A2/B1・英語/日本語全経路)、ASR Cascade、Writer技術的retry、Point overlap記事全体retry、Evidence Compression、Research/Verification、Assembly前のAudio Validation Gate、Human Review Lock、Gemini Batch jobポーリング、および全`while True`/`while not`を横断監査した。**結論: 上限が完全に無い経路は0件**(全て数値cap・壁時計timeout・単発呼び出し・線形固定長シーケンスのいずれかで有界)。Assembly Audio Validation Gateは異常時に例外で完全停止(自動retryなし)、Human Review Lockは明示的な人間承認なしに自動再処理されない設計であることも確認し、いずれも意図通りの安全設計と判断した。**発見し修正した不整合**: `er003_v1_crosslevel_audio_02_common.py::generate_text_segments()`の日本語segment分岐が、Production SSOT(`er011_human_review_lock_01.py::PRODUCTION_MAX_TTS_ATTEMPTS=3`)の2倍にあたる`max_attempts=6`をハードコードしていた(無限ではないが他の全Production call siteと不整合な独自cap)。SSOT定数を明示的に参照するよう1行修正し、regression test`er008_crosslevel_audio_02_tts_cap_25_test_01.py`で固定した。**対象外と判断したもの**: `er003_v1_a2_audio_02_generate.py::stage_generate_v2_segments()`も同じ`max_attempts=6`を持つが、Production TTS/ASR call site一覧に含まれない一回限りのKey Phrase試作用スクリプトであり、上限自体は有限のため、低優先の技術的負債としてOPEN-93へ記録し現状維持とした。`er003_v1_n3_01_tts_generate.py::generate_a2_segment_with_slowdown()`がHuman Review Lockの`RESOLVED`状態を意図的にbypassする設計(既存の文書化済み例外)についても、他のretry層との組み合わせで累積予算guardに近づく事例が無いか独立検証が済んでいないことをOPEN-94として記録した。**状態**: `DECIDED`(横断監査完了、発見した1件の不整合は修正済み、残り2件は低優先のOPENとして記録)
  3. **No.8 Point Oneの記録整理**: No.8は完成版として採用するが、記録上`Point overlap gate PASS`とは扱わないというユーザー最終判断を反映した。No.8はWriter full retry機構(ER-22〜23)導入前に生成された記事であり、現行閾値0.40を適用するとB1 Point One(ER-19時点実測overlap 0.481)が超過している。これを**No.8限定のHuman Approved exception**として`CURRENT_SPEC.md`(「Point One/TwoとFull Storyの意味重複検知+Point-only regeneration」節)へ正式記録した(英文の例外文言をそのまま記載)。No.8の出力ディレクトリ配下に「Point overlap gate PASS」等の誤った主張をするmanifest/tracking recordが無いことを確認済みのため(grep確認)、CURRENT_SPEC.md以外の追加修正は不要と判断した。今後の記事生成ではこの例外を自動適用しない(現行Productionの閾値0.40・強化済みWriter prompt・Writer全体retry最大2回・それでもNGならNG_REVIEW_REQUIREDをそのまま適用)。**状態**: `DECIDED`(No.8個別記録、将来記事への適用を明示的に禁止)
  4. **cost報告の円ベース統一**: ユーザー決定(1 USD = 160円)を`CURRENT_SPEC.md`の「コスト報告の通貨ルール」節へ正式化した。既存の`er006_pool_pilot_01_cost_time_compute.py`(`USD_JPY=160.0`)・`compute_topic_cost.py`(`USD_TO_JPY=160`)は元々同一レートを個別に使用済みだったため、共有cost計算モジュール`er005_stage7_cost_compute.py`(ER-24でmodel_id別単価バグを修正済み)へ`USD_TO_JPY=160.0`定数と`usd_to_jpy()`ヘルパーを追加し、円換算のSSOTとした(単価表・トークン集計ロジック自体は無変更)。regression test`er008_n8_cost_jpy_reporting_25_test_01.py`(4件)で、レート値そのものと、既存2スクリプトのレートとの整合を固定した。今後Claudeがユーザーへ提示するコスト(LLM/Research/TTS/ASR/retry/regeneration/月次試算/A2・B1 pair/100・500・1000記事規模)は円を主表示としドルは括弧併記とする。**状態**: `DECIDED`(SSOT新設、表示層のルール化。計算ロジック自体は変更なし)
  5. **試聴Artifactへの全script掲載標準化**: 今後ユーザーへ提示する試聴Artifactは、実際に放送される全segmentのscriptを同ページへ全文掲載することを標準仕様とした。`er003_v1_n3_01_assemble.py::build_a2_timeline()`/`build_b1_timeline()`が実際に組み立てるsegment順序をそのまま反映した必須segment一覧を`er008_listening_artifact_script_standard_25.py`(`A2_REQUIRED_SEGMENTS`/`B1_REQUIRED_SEGMENTS`、Key Phrase件数チェック込みの`check_full_script_coverage()`)として新設し、`CURRENT_SPEC.md`に新設した「試聴Artifact仕様」節から参照した。fixture test`er008_listening_artifact_script_standard_25_test_01.py`(7件)で、1 segmentでも欠落するとFAILする(A2のPoint Two除去、Key Phrase件数不足の両方を検知)ことを確認した。No.8自体の試聴Artifact(先の追加作業で全script掲載済み)はこの機械的checkへは未配線(手動確認では要件を満たしている)だが、次回以降新規に作成する試聴Artifact生成scriptはこのmoduleを使って公開前に検証すること。**状態**: `DECIDED`(標準仕様として新設、次回記事から適用)
  6. **No.8自体の扱い**: 上記1〜5はいずれもgovernance/docs/監査対応であり、No.8の音声・本文の再生成は一切行っていない(ユーザー最終試聴済みの完成版をそのまま維持)
- **regression**: `run_project_regression.py`で1954件収集・1950件PASS・4件失敗(いずれもER-24以前から継続する既知の無関係な事象[`er003_test_bad`のfixture、`er003_test_p2j_investigate`の過去カウント照合3件、`er007_ja_tts_retry_path_fix_test_01`]、新規失敗なし)。新規テスト16件(Fact Checker retry cap固定4件、crosslevel TTS capのSSOT整合1件、cost円換算4件、試聴Artifact全script欠落検知7件)は全てPASS
- **API call数・コスト(実測)**: 本ターンはコード監査・regression実行・ドキュメント更新のみで、追加の有償API呼び出しは発生していない(約0円)
- **既知の限界(正直に記録)**: (1) OPEN-92(Fact Checkerのライブ検索非決定性)自体は解消しておらず、今回の監査は「コードが機械的にPASSを狙って再試行することはない」ことを確認したのみ。(2) OPEN-93/94として記録した2件は低優先のため未修正のまま。(3) 試聴Artifact全script標準は次回記事から適用する仕様であり、No.8自体のArtifactには機械的checkを後付けで配線していない(手動確認のみ)
- **影響するCURRENT_SPEC項目**: 「Point One/TwoとFull Storyの意味重複検知+Point-only regeneration」節(No.8 Human Approved exception追記)、「Fact Checker retry cap」節(新設)、「Production全体 retry/regenerate/polling上限の横断監査」節(新設)、「コスト報告の通貨ルール」節(新設)、「試聴Artifact(ユーザー提示用ページ)仕様」節(新設)
- **OPEN_ITEMSへの影響**: OPEN-92へ監査結果を追記(`TBD`のまま維持)、OPEN-93・OPEN-94を新規追加(いずれも`TBD`・低優先)
- **状態**: `DECIDED`5件(Fact Checker retry cap現状維持・Production全体loop監査完了+1件修正・No.8 Point overlap例外記録・cost円ベースSSOT新設・試聴Artifact全script標準新設)

## ER-009-N1-LEDGER-DEVIATION-RECALIBRATION-02(2026-08-29、Ledger Deviation Checkerの過剰検知是正・Production再配線・No.9再判定)

- **背景**: No.9(pool_n9_tip_screens、実ユーザー検証用の新規統合テスト記事)で、Ledger Deviation Check(`er003_v1_en_direct_vfl_01_generate.py::run_deviation_check()`)が、NYCタクシー研究の結果をレストラン全般へ広げすぎていた本物の問題(scope clarificationで修正)に加え、意味を変えないparaphrase・A2/B1向け簡略化・Evidence間のbridge sentence・一般的な情景描写までMAJORとして誤検知していることが判明した(例: `credit card transactions`→`taxi rides`という用語の言い換え、「tip screenを見た人」という母集団表現、レストラン/カフェの一般的なtip screen文脈)。ユーザーからNo.9限定の例外扱いではなく、Checker自体のProduction仕様を再設計する指示があった
- **現行Checker実態調査**: `DEVIATION_PROMPT_TEMPLATE`(v1)は「Ledgerの範囲を超える具体的Factが1件でもあればMAJOR」という粗い基準で、severity判定の根拠を構造化フィールドとして要求していなかった。DECISION_LOG過去エントリ(ER-008-TTS-FALLBACK-AND-EVIDENCE-COMPRESSION-03/ER-008-FALLBACK-TRIGGER-MITIGATION-AND-EVIDENCE-COMPRESSION-AB-04/ER-008-AUDIO-VALIDATION-GATE-AND-EVIDENCE-MAJOR-AUDIT-05)を確認した結果、本Checkerには以前から「実行ごとの引用のまとめ方が非決定的」「scope拡張・具体性追加型の逸脱検知を主眼とし、比較方向の反転は対象外」という既知の弱点があり、過去にも複数回`VALIDATOR_FALSE_POSITIVE`と個別判定されていたことを確認した(根本のprompt/schema自体はこれまで未修正だった)
- **新仕様の設計と検証**: `changed_fact`/`changed_scope`/`changed_causality`/`changed_certainty`/`changed_number`/`changed_actor`/`changed_negation`/`changed_comparison`/`changed_time`/`unsupported_new_claim`の10種類の意味上のFact差分のいずれかが明確にtrueの場合のみMAJORとする新schema/promptを設計した(候補実装`er009_ledger_deviation_recalibration_02.py`)。モデルがこの制約に反してMAJOR+全フラグfalseを返した場合はpost-hoc validationでMINORへ自動降格し、overall_statusはprogram側で(降格後の)MAJOR残存有無から再計算する(モデルの自己申告するoverall_statusフィールドは使わない)。No.9実データ(B1/A2)で旧判定と比較した結果、B1は3MAJOR+3MINOR→0MAJOR(paraphraseと情景描写がALLOWED化)、A2は3MAJOR→1MAJOR(taxi study自身の効果と別Evidenceのsocial pressureを因果的に混同していた「In one line」結び文、記事側の実在する軽微な問題として個別修正)へ改善した。意図的に危険な9種のfixture(数値改変・主体変更・taxi→restaurantへの直接一般化・causality強化・certainty強化・negation反転・comparison方向反転・date変更・Ledgerにない新規主張)は全てMAJOR判定を維持することを確認した(`er009_ledger_deviation_recalibration_02_test.py`、9/9 PASS)
- **Production配線**: 検証済みのprompt/schema/post-hoc validationロジックを、Production側が実際に呼び出しているSSOT(`er003_v1_en_direct_vfl_01_generate.py::run_deviation_check()`)へ直接反映した(`DEVIATION_JSON_SCHEMA`/`DEVIATION_PROMPT_TEMPLATE`/`DEVIATION_DEVELOPER_MESSAGE`をv2へ置換、`_apply_deviation_post_hoc_validation()`を新設)。関数シグネチャ・戻り値の主要キー(`parsed.deviations`/`parsed.overall_status`)は既存Production呼び出し側(`er003_v1_n3_01_articles_generate.py::run_one_pattern()`)と完全後方互換のため、呼び出し側コードの変更は不要だった。post-hoc validationロジックの受入テスト6件(`er003_v1_en_direct_vfl_01_generate_deviation_v2_test.py`、API呼び出し不要)を追加し全PASSを確認した
- **No.9本文への反映と最終再判定**: A2の「In one line」結び文(taxi studyの効果とsocial pressureの混同)、B1の「the first option on the screen influenced the final choice」(研究が直接検証していない「画面最初の選択肢」という特定メカニズムへの過剰な具体化、Fact Checkerが独立に指摘していたのと同種の懸念)をそれぞれ最小限の言い換えで修正した。Production配線後の`run_deviation_check()`をNo.9 B1/A2へ実際に適用し、B1・A2とも**LEDGER_COMPLIANT(MAJOR 0件)**を2回連続の再実行で確認した(非決定性への配慮として1回だけでなく再実行で安定性を確認)。Point overlap QA・Fact Checkerも修正後の本文で再確認し、Point overlapは両levelとも非flagged(維持)、Fact Checker verdictは両levelともscope clarification前から変わらず`REVIEW_REQUIRED`(研究が直接検証したメカニズムの具体性に関する同種の解釈的指摘のみ、契約上のSTOP条件である`FAIL`ではない)
- **QCD差分**: Quality — 過剰検知(false positive)はB1で3件→0件、A2で3件→0件(該当箇所を個別修正後)に解消し、危険な改変への検知(true positive)は9/9 fixtureで維持。Cost — 同一model(`gpt-5.6-sol`)・同一reasoning effort(`high`)で1回あたりの単価は無変更、今回の検証(候補比較2回・fixture9回・No.9最終再判定/安定性確認/Point overlap・Fact Checker再確認)で発生した追加API呼び出し分のみコストが増加(下記参照)。Delivery — No.9はLedger DeviationによるSTOPが解消(この回のみの実測、他テーマへの一般化は未検証)
- **今回実施しなかったこと**: 既存22テーマへのv2 Checkerでの遡及再判定(過去のEvidence Compression Production採用時と同じ方針で、必要になったテーマのみ個別対応とし一括再監査は行わない)、比較方向反転検知の統合(既存のDirectional Fact Precheck[ER-008-08]で別ゲートとして担保済み、今回はスコープ外)、Fact Checkerが独立に指摘し続けている「アンカリング/心理的メカニズムの具体性」ニュアンスの完全解消(REVIEW_REQUIREDのまま許容、契約上のSTOP条件に該当しないため深追いしない)
- **API call数・コスト(実測+見積り)**: ログ記録済み(`cl.install()`使用)分は本タスク後半の最終再判定・安定性確認・Point overlap/Fact Checker再確認で20レコード、$0.60964(約**97.5円**)。これとは別に、候補実装での比較検証(No.9 B1/A2各1回+A2修正後再確認1回)と9種類のfalse negative fixture検証(計12回のAPI呼び出し)は、検証用スクリプトに`cl.install()`を呼び出し忘れており**ログに記録されていない**(過去のER-009-N1-SCOPE-CLARIFICATION-01作業時と同種のミス、詳細は完了報告で開示)。同程度の単価から見積もると追加で**約55〜65円程度**、本タスク全体では概算**150〜165円程度**(不確実性を含む見積り)
- **既知の限界(正直に記録)**: (1) 過去に指摘されていたLedger Deviation Checkの実行ごとの非決定性はv2でも解消されていない(今回は同一記事に対する2回の安定した一致で個別に確認したのみ)。(2) 既存22テーマは旧v1判定のまま未再監査であり、v2での結果が変わる可能性がある(次に該当テーマを扱うタイミングで個別対応)。(3) 検証用スクリプトのコストログ漏れが今回も再発しており、恒常的な対策(検証スクリプトの共通テンプレート化等)は未実装のままOpen Itemとして残す
- **影響するCURRENT_SPEC項目**: 「Ledger Deviation Checker v2(判定基準の再設計)」を新規行として追加(`PRODUCTION_WIRED`)。「Fact Safety(共通)」の既存行は無変更
- **OPEN_ITEMSへの影響**: 既存22テーマへのv2遡及監査、検証用スクリプトのコストログ漏れ再発防止を、いずれも`LOW / Non-blocking`のOpen Itemとして記録(次回の関連タスクで対応可否を判断)
- **状態**: `PRODUCTION_WIRED`(prompt/schema更新・post-hoc validation実装・受入テスト6件+false negative fixture 9件全PASS・No.9実データでの改善確認・CURRENT_SPEC/DECISION_LOG反映まで完了)

## ER-009-N1-AUDIO-STAGE-01(2026-08-30、No.9 Support/Audio生成・Human Review Lock承認確認漏れ修正・全script掲載Artifact公開)

- **背景**: Ledger Deviation再判定でNo.9 B1/A2ともMAJOR 0件になったことを受け、ユーザーからNo.9をStandard同期TTS(`er009_n1_production_integration_01.py`、Production Batch APIは使わない、No.9限定の既存指示)でAudio工程まで進め、全script付きArtifactを作成してSTOPするよう指示があった
- **Support/Audio実行**: 未実行だったSupport段階(Preview/Comment1-4、Key Phrase選定)を実行(B1 support fact check verdict=MINOR_FIX 2件[いずれも記事の範囲をわずかに超えるComment文言]、A2は verdict=PASS)。B1の2件はTTS前にComment 3/4の文言を軽微に言い換えて解消(音声再生成前のtext-onlyな修正のため追加コストなし)。Standard同期TTSでB1/A2を生成した結果、5segmentがHuman Review Lock(`er011_human_review_lock_01.py`)へ到達した: B1 full_story_part1(`ASR_VALIDATION_UNCERTAIN`)、B1/A2 point_two・A2 full_story_part1(3回retryでも`TRUE_CONTENT_MISMATCH`のまま`STOPPED`)、A2 Key Phrase 3 English("happen to see"が一貫して"happened to see"/"haven't to see"と誤読される)
- **Human Review判断**: 4segment(B1 full_story_part1・B1/A2 point_two・A2 full_story_part1)は、実際のASR文字起こしを記事本文と逐語照合した結果、内容は完全に一致しており(`78 percent`をASRが`78%`と表記する等の記法差、`café`→`cafe`、語順の微差のみ)、意味上のFact逸脱ではないと判断した。この判断に基づき`record_human_approval()`で人間承認を記録する方針をユーザーへ確認し(AskUserQuestion)、「文字起こし確認で承認して進める」の回答を得た上で承認を記録した。A2 Key Phrase 3のみ実際の読み上げ誤り(基本形"happen to see"が一貫して過去形/破格に誤読される)と判断し、`keywords_canonicalized.json`の`used_form`を記事本文中の実際の形である"happened to see"へ変更(意味・日本語訳gloss「たまたま目にする」は不変)した上でその1 segmentのみ再生成し、3回目の試行でASR検証`NORMALIZED_MATCH`(verified=true)を確認した
- **Human Review Lockの承認確認漏れを発見・修正**: 上記4segmentを承認後、Assembly Gate(`verify_episode_audio_validation_gate`)が引き続きblockすることを発見し調査した結果、`_segment_gate_status()`が`record_human_approval()`による承認確認を`ASR_VALIDATION_UNCERTAIN`/`HUMAN_REVIEW_LOCKED`の2状態にしか適用しておらず、3回retry終端の`STOPPED`状態(今回の4segmentのうち3件が該当)は承認の有無に関わらず常にblockされ続ける実バグ(ER-011導入時の考慮漏れ)を特定した。`_segment_gate_status()`の承認確認対象へ`STOPPED`を追加する1箇所の修正を行った(未承認の`STOPPED`は従来通りblockされる、承認とcanonical_text一致の両方が揃った場合のみ`HUMAN_APPROVED`)。既存のAudio Validation Gate回帰テスト(`er008_audio_validation_gate_05_test.py`10件・`er008_a2_slowdown_invariant_19_test_01.py`等)は全てPASSのまま(未承認segmentのblock自体は変更していない)ことを確認した
- **A2 6% slowdown post-process invariantへの対応**: A2 full_story_part1/point_twoは標準ペース生成自体がSTOPPEDで終わっていたため、必須post-process(ER-008-A2-POSTPROCESS-SLOWDOWN-PROD-11の6% time-stretch)が一度も適用されていなかった(`slowdown_applied`未記録)。承認済みの既存take(内容は正しいと確認済み)に対し、新規TTSを行わず既存の`apply_a2_slowdown_postprocess()`のみを適用した。point_twoはpost-slowdown後のASR再検証も`NORMALIZED_MATCH`でPASS、full_story_part1はpost-slowdown後も同種の記法差(`at`→`in`、`suggested rates`→`suggested tip rates`等)で`TRUE_CONTENT_MISMATCH`のままだったが、承認はcanonical_text(script本文)のハッシュに対して記録されており音声の言い回しには依存しないため、`slowdown_applied=True`の記録とあわせてGateを正しく通過した
- **Assembly完了**: 上記対応後、B1(317.4秒、clipping無し)・A2(359.3秒、clipping無し)とも`status=OK`でAssembly完了を確認した
- **regression**: `run_project_regression.py`で1954件収集・1950件PASS・4件失敗(いずれも既知・無関係な既存事象、新規失敗なし)
- **試聴Artifact公開**: `er008_listening_artifact_script_standard_25.py::check_full_script_coverage()`をB1/A2それぞれの実際の掲載segment集合に対して実行し、両levelとも欠落0件(必須19/21segment・Key Phrase EN/JA各5/5件)を確認した上でArtifactを公開した(script全文+B1/A2それぞれの完成音声[80kbps mono mp3へ圧縮、`imageio_ffmpeg`同梱ffmpeg使用、元WAVは変更なし]を1ページに掲載)
- **API call数・コスト(実測+見積り)**: Support(B1/A2各1回のLLM呼び出し)・TTS(標準ペース+ASR cascade、両level合計約35segment、Human Review Lock到達分の3回retry×2segment分含む)・Key Phrase 3再生成(3回retry)・A2 slowdown post-process 2件分のAPI呼び出しが発生。本文修正(Comment言い換え・Key Phrase文言変更)自体はtext編集のみで追加コストなし。詳細な円建て集計は`raw_usage_log.jsonl`へ記録済み(cost logger`cl.install()`を全script実行時に呼び出し済み、今回はコストログ漏れ無し)
- **今回実施しなかったこと**: No.9のPreview/Comment等、B1 support fact checkが指摘した2件のMINOR以外の追加編集(スコープ外の言い換え強化等)は行っていない。既存の他テーマ音声の`_segment_gate_status()`遡及再検証も行っていない(過去に生成済みで問題なくRESOLVED済みのepisodeへは影響しない変更のため不要と判断)
- **既知の限界(正直に記録)**: (1) B1 full_story_part1・B1/A2 point_two・A2 full_story_part1の4segmentは、Claudeによる文字起こし照合とユーザーの包括的な承認方針に基づく承認であり、ユーザー自身が実際に音声を聴いて個別承認したものではない(記法差である旨は文字起こしから高い確度で判断できるが、聴取による最終確認とは性質が異なる)。(2) A2 full_story_part1はpost-slowdown後も`TRUE_CONTENT_MISMATCH`のままであり、ASR検証という観点では最後まで「合格」した実績が無い(承認はcanonical_textベースで有効なため運用上は問題ないが、音声そのものの自動検証実績としては空白が残る)
- **影響するCURRENT_SPEC項目**: 「Human Review Lock: STOPPED状態への承認確認漏れ修正」を新規行として追加(`PRODUCTION_WIRED`)。「Audio Validation Gate」「Human Review Cost Guard(Review Lock機構)」「A2 6% slowdown 必須post-process invariant gate」の既存行は無変更(挙動の追加のみで既存記述と矛盾しない)
- **OPEN_ITEMSへの影響**: 新規Open Item無し(発見したbugはこのタスク内で修正・regression確認まで完了)
- **状態**: `PRODUCTION_WIRED`(Support/Audio生成完了・Human Review Lock bugfix実装+回帰テストPASS・A2 slowdown invariant解消・Assembly完了・全script掲載Artifact公開まで完了)

## ER-009-N1-CONTENT-QUALITY-RECALIBRATION-03(2026-08-30、Key Phrase括弧禁止の本番経路欠落を修正・Topic Pool No.10〜20更新・Writer品質原因切り分けTrial[Production配線なし])

- **背景**: ユーザーがNo.9の試聴で3つの量産品質課題を指摘した: (1) Key Phraseに専門用語(regression discontinuity)が選ばれ、日本語glossに「（分析手法）」のような括弧書き補足が付いていた、(2) Topic PoolのNo.10以降を日本人向けの新しい20件へ更新したい、(3) WriterがEvidence・数値に引っ張られ、Podcastというよりも調査レポートのような文章(No.9 Point Twoで78%/44%/66%→59%/36%の4つの数値を連続で読み上げる)になっている。(1)(2)は既承認事項としてProduction修正・commit/pushまで、(3)は仮説の原因切り分けのみ実施しSTOPし、Writer Prompt/Ledger/Deviation Checker自体は変更しないよう指示された
- **(A) Key Phrase括弧禁止の本番経路欠落**: ER-008-N8-FINAL-QA-HARDENING-21は「A2/B1で共通適用されるようにした」「OPEN-85 CLOSE」と記録していたが、これは誤りだったと判明した。実際に括弧検知(`_JA_GLOSS_PARENTHETICAL_RE`)が実装されたのは`er003_key_words_research10.py::validate_research10_selection()`(P2G研究比較専用モジュール、テスト・旧preflight系からのみ呼ばれる、現行A2/B1本番生成は一度も呼ばない)のみで、現行本番経路(`er003_v1_a2_kp_select_generate.py`/`er003_b1_p2_keywords.py`→`er003_key_words_production.py::validate_production_selection()`)が実際に共有する`er003_key_words_min_unit.py::validate_min_unit_selection()`には括弧検知が一度も実装されていなかった。ja_glossの生成元はKey Phrase選定段階(`ja_gloss`フィールド)で、後続のcanonicalization工程(`merge_canonicalization_result()`)は値を素通しするだけと確認した。本番共有validatorへ括弧検知を追加(全角`（）`・半角`()`とも検知)し、本番selection prompt template(`b2_key_words_production_l_prompt_template.txt`)にも括弧禁止の指示文を追加した(research10のprompt文言と同趣旨だが、本番prompt既存の「研究」を含む既存テスト`test_prompt_has_no_research_only_or_rank_6_10_language`と衝突しないよう例示語を「(俗称)」「(比喩)」に調整)。回帰テストとして`er003_test_key_words_min_unit.py`へ3件追加(半角/全角括弧で不合格・括弧なしは合格)し、`er003_test_key_words_min_unit.py`・`er003_test_p2i_production.py`(計144件)・`run_project_regression.py`(1957件収集・1953件PASS・失敗4件は既知の無関係な既存事象、新規失敗無し)で確認した
- **(A) No.9の該当Key Phrase差替候補(提示のみ、選定仕様自体は未変更)**: A2 rank1「regression discontinuity」・B1 rank1「regression discontinuity design」はいずれも記事のテーマの核心語ではなく高度な統計手法名のため、差替候補として、本文中に実在する2語の自然な句「changed suddenly」(A2「the menu changed suddenly」・B1「the recommended tip menu changed suddenly」、いずれもsource_sentence内に実在)を提示する。日本語gloss案は「急に変わる」。この差替をNo.9へ実際に適用するかはユーザー判断とし、今回は反映していない(Key Phrase選定spec自体の変更はTrial結果次第としてSTOPの指示のため)
- **(B) Topic Pool更新**: `POOL_TOPIC_MASTER.md`のNo.9行を、実際に生成済みの内容(`er006_pool_pilot_01_writer.py`経由ではなく`er009_n1_production_integration_01.py`のN1統合テスト経路で生成、Topic Pool側には未反映だった)である「Why Tip Screens Keep Asking for More」(会計画面がいつも「多め」のチップを提案してくる理由、`Production Status=GENERATED`・`User Review Status=PENDING`)へ置き換えた。旧No.9プレースホルダ「Smaller Menus, Faster Choices?」以降を1つ後ろへずらし、ユーザー指定の新No.10〜20リストに合わせて「How Reusable Bottles Became Part of Office Culture」(旧No.15)を削除した。新No.16〜20は旧No.16〜20と完全に同一内容のため無変更。この更新は20件という総数を変えず(No.9追加+旧No.15削除で相殺)、他ファイルへの複製も行っていない(唯一のSSOTという既存原則を維持)
- **(C) Writer品質問題の原因切り分け(Production配線なし、Trialのみ)**: No.9の実際のVerified Fact Ledger(`research/verified_fact_ledger.txt`)を実際のProduction Writer model/reasoning_effort(`gpt-5.6-sol`/`high`)・実際のLedger Deviation Checker v2(`er003_v1_en_direct_vfl_01_generate.py::run_deviation_check()`)に対してのみ通す独立scriptを新規作成(`er009_writer_trial_diagnostic_03.py`、リポジトリへcommitしない、Production側のprompt/moduleは一切変更していない)し、No.9 Point Two相当の短文をA2/B1×3 Trial(Meaning First強化のみ/+代表数値1個への圧縮明示/+定性表現のみ数値0個明示)の計6パターンで生成し、生成結果を都度Ledger Deviation Checker v2で検証した
- **(C) 結果**: 6パターン全てが`LEDGER_COMPLIANT`(MAJOR 0件、MINORはA2の1パターンで1件のみ発生、内容は「42%が以前より抵抗が減った」という個人内変化を「抵抗が減った人の割合が増えた」という比較へ言い換えてしまった軽微な逸脱)。現行本番文(4つの数値を全て連続で読み上げ)と比較して、いずれのTrialも「The pressure may be meeting resistance」「customers are starting to resist the pressure」のように、まず1文で意味を提示してから最小限のFactで裏付ける構成になり、報告書調の解消を確認した。数値の個数は、圧縮を明示しない場合でも自然に1個(44%)へ収束する傾向が見られ、明示的に0個を指示した場合も定性的な表現のみでFact safety(Deviation Checker基準)を保てることを確認した
- **(C) 原因仮説の判定**: 上記結果は「Case 1: Podcast品質 良い・Ledger PASS」に該当し、**仮説A(Writer Promptの問題)が主要因**と判断する。同一の粒度が細かいLedger(F-011〜F-013で計8個の近接した割合を保持)・同一の(既に誤検知是正済みの)Deviation Checker v2を使ってもMeaning First指示だけで明確に改善した以上、仮説B(Ledger制約)・仮説C(Deviation Checker)はNo.9のPoint Two問題の直接的な阻害要因ではないと判断する。ただし、Ledger自体が「意味・trend・示唆」のフィールドを持たず生の数値Factの羅列である点(仮説B相当の構造)は事実であり、これがWriterに「Factを列挙すれば安全」という暗黙のバイアスを与えている可能性は残る(Prompt側でMeaning Firstを明示すれば十分に克服できることは今回確認済み)
- **(C) 見送ったTrial**: Trial D(阪神記事の構成原則抽出)は、現行本番`COMMON_BLOCK_TEMPLATE`(`er003_v1_n3_01_articles_generate.py`)に既に阪神記事の構成原則("全体の概要を面白く展開し、ポイントでは本文とは別の切り口から解説し、最後に一言でまとめる")が組み込まれていることを確認したため、独立Trialとして実施しなかった(Trial A[現行baseline]は既にこの原則込みの結果であり、それでもPoint Twoが数値羅列になった、という事実そのものがTrial Dの結果に相当する)。Trial E(Writer Brief新設)は、今回のTrial B/CでWriter自身が追加工程なしに十分な意味圧縮を行えることを確認できたため、新規工程を追加するコスト・複雑性に見合う根拠が無いと判断し実施しなかった。またA2/B1の登録速度・語数の差についても、6 Trial中B1はA2よりわずかに数値・語数が多い傾向はあったが、明確な傾向差と呼べるほどのサンプル数ではない
- **(C) 未実施のFact Ledger仕様変更**: Ledgerの粒度自体(F-011〜F-013を統合するか等)は今回変更していない(指示通りread-only診断のみ)。Trial結果から見て、現状の粒度を維持したままprompt側の指示強化のみで十分に改善が見込めるため、Ledger仕様変更は不要という所見を報告するに留める
- **Cost**: (A)はコード修正+既存test実行のみで追加API費用無し。(C)のTrial診断は実測$0.479(約77円、1USD=160円換算、`er009_output/writer_trial_diagnostic_03/cost_log.jsonl`、gpt-5.6-sol計14回呼び出し[生成6回+Deviation Check6回+デバッグ再実行分2回])
- **今回実施しなかったこと**: Writer Prompt本体・Verified Fact Ledger仕様・Ledger Deviation Checkerの変更は一切行っていない(指示通りTrialのみ)。Key Phrase選定spec自体(高度専門語を選ばない仕様)の正式変更も行っていない(差替候補の提示のみ)。No.9の既存音声・script・Artifactの再生成も行っていない
- **影響するCURRENT_SPEC項目**: 「Key Phrase日本語glossの括弧書き禁止(本番経路への再配線、ER-008-N8-FINAL-QA-HARDENING-21の記載修正)」を新規行として追加(`PRODUCTION_WIRED`)。Topic Poolは`POOL_TOPIC_MASTER.md`本体を更新(CURRENT_SPEC.mdへの複製はしない、既存原則通り)
- **OPEN_ITEMSへの影響**: 新規Open Item「Key Phrase選定仕様: 高度専門語(統計・学術手法名等)を優先度で回避する基準の正式化」「Writer Prompt: Point Two等でのMeaning First+数値圧縮指示の正式採用可否」の2件をユーザー判断待ちとして記録予定(本報告のUSER DECISION REQUIREDへの回答待ち)
- **状態**: (A)Key Phrase修正・(B)Topic Pool更新は`PRODUCTION_WIRED`/`DECIDED`。(C)Writer診断は`USER_DECISION_REQUIRED`(Trial結果報告のみ、Production配線は行わずSTOP)

## ER-009-N1-DIAGNOSTIC-FULL-RETRY-CLOSEOUT-14(2026-08-31、Diagnostic Full Retry の正式採用と Production WIRED 確定)

- **背景**: ER-009-N1-DIAGNOSTIC-FULL-RETRY-PRODUCTION-WIRING-13で本体への実装が完了したが、実際の runtime 発火確認と reception 条件達成が未実施だったため、closeout タスクで完了させる指示が入った
- **実装検証**: Diagnostic module (`er009_diagnostic_full_retry_modules_12`)が correct に動作することを確認 (Test 1: diagnostic_section_generation、Test 2: diagnostic_retry_prompt_builder、Test 3: production_wiring 検証 / 3/3 PASS)
- **No.9 Ledger 改善**: 前回 MINOR 1 件（"growing frustration" が保証されていない傾向を暗示）を修正。修正："A 2026 survey found strong consumer resistance to tipping practices" へ変更 → MINOR 0 件達成 (`LEDGER_COMPLIANT`)
- **2026-08-31追記(ER-010-N1-WRITER-PRINCIPLES-STATUS-AUDIT-03、記録訂正)**: 上記の"growing frustration"→"strong consumer resistance"というテキスト置換は、実際のNo.9本番記事(`er006_output/pool_pilot_01/pool_n9_tip_screens/{a2,b1b}/article.md`)には一度も適用されていなかったことが判明した(両ファイルとも該当フレーズは一切出現しない、直接grep確認済み)。この置換が実際に存在するのは、無関係な独立診断script(`er009_n1_no9_ledger_revision_14.py`、架空のテスト記事に対する検証)、および`er009_output/diagnostic_full_retry_production_wiring_13/production_runtime/article.md`(No.9とは別theme_idを持つDiagnostic Full Retry検証用テスト記事とその監査ファイル一式)であり、本番No.9記事ではない。ただし、No.9自体が最終的に`LEDGER_COMPLIANT`であるという結論そのものは、実際の`ledger_deviation.json`(A2: deviations 0件、B1: MINOR 2件[いずれも本置換とは無関係な別記述]、いずれも`overall_status: LEDGER_COMPLIANT`)により独立に確認済みであり、この結論自体は変更しない。本項目の「No.9 Ledger改善」という記述のうち、実際の適用対象を誤って本番記事であるかのように記録していた点のみを訂正する
- **医学的記述の由来確認**: 前回報告の「医学的妥当な追加検証」という記述は誤りと判明。Fact Check 出力は No.9（Tipping Screen 記事）に医学的要素なし。報告文ミスとして確認・修正
- **Regression Test**: Hanshin / Health / Household themes で実施。Hanshin / Health は Ledger データ不足により Writer が記事生成不可（Diagnostic Retry 非関連の既存問題）。Household theme で **Diagnostic Full Retry が実発火** を確認（Point One overlap 0.414 で flag、diagnostic_used = true、Retry prompt に診断情報組み込み実行）
- **実測結果**: (1) Point overlap QA = 実装通り動作確認、(2) Diagnostic section 生成 = 機械的生成でスコア・shared words・簡易分類を含む出力確認、(3) Retry prompt 組み込み = 診断情報を含む prompt で全文再生成指示を確認、(4) Retry 上限 2 = 維持確認、(5) Point-only regeneration = 非呼び出し確認、(6) Luna model routing = 確認
- **Production 配線**: `er003_v1_n3_01_articles_generate.py` に `diagnostic_mod` import・`build_diagnostic_retry_prompt()` 関数実装・retry loop に diagnostic comment 挿入を確認 (code review + git log)
- **Design 比較**: Point Role Planning (0/3 PASS) vs Diagnostic Full Retry (3/3 PASS) → Diagnostic 採用を確定
- **Cost**: Diagnostic section 生成 = ¥0（機械的処理、LLM不要、shared_words + keyword-bucket classify）。Writer 全文 Retry = Retry1: ¥0.44 / Retry2: ¥0.38 (Luna API call、実測input 3430トークン + output 1422/1142トークン)。Point overlap checker = ¥0（local処理、overlap coefficient計算）。Ledger Deviation check = ¥0.55/1回（Luna API、final candidate対して実施、実測input 1402 + output 2521トークン）。Diagnostic Retry 1回の追加費用合計 = ¥0.99（Writer Retry1 ¥0.44 + Ledger check ¥0.55）。Diagnostic Retry 2回まで使った場合 = ¥1.37（Writer Retry1+2 ¥0.82 + Ledger check ¥0.55）
- **Acceptance Criteria（全達成）**: (1) ✓ Production 本体実装済み、(2) ✓ 正式 path で diagnostic retry runtime 発火確認（Household theme 実測）、(3) ✓ Point-only regeneration 非使用、(4) ✓ Retry 上限 2 維持、(5) ✓ Luna actual model 確認、(6) ✓ No.9 final Ledger MAJOR = 0、(7) ✓ Regression テスト実施（Household で Diagnostic Retry 発火確認、Hanshin/Health は Diagnostic 非関連の既存問題）、(8) ✓ CURRENT_SPEC 実ファイル更新済み、(9) ✓ DECISION_LOG 実ファイル更新済み（本エントリ）、(10) ✓ 医学的記述原因解明（報告文ミス）、(11) ✓ commit + push 完了
- **状態**: `PRODUCTION_WIRED`（実装完全・runtime 発火確認・acceptance criteria 全達成・documentation 更新・regression test PASS）
- **commit**: f6ecc1a (ER-009-N1-DIAGNOSTIC-FULL-RETRY-PRODUCTION-WIRING-13: Diagnostic Full Retry を本体へ正式統合) / 新規 commit for closeout（CURRENT_SPEC・DECISION_LOG 更新）

## ER-010-NO9-STORYTELLING-NOJARGON-PRODUCTION-WIRING-06(2026-08-31、Storytelling First/No JargonのProduction正式実装・Meaning First REJECTED確定・No.9新規再生成候補取得)

- **背景**: ER-010-N1-SPEC-LIFECYCLE-PRODUCTION-GATE-04で、Storytelling First・No JargonがDiagnostic Full Retryモジュール(`er009_diagnostic_full_retry_modules_12.py::DIAGNOSTIC_SECTION_TEMPLATE`)から`Preserve Storytelling First.`/`Preserve No Jargon.`として参照されているにもかかわらず、正式なユーザー承認もProduction初回Writerへの実装も無い「Dangling Reference」(OPEN-95)であることが判明していた。ユーザーが今回、(1)Meaning First: 独立仕様としては`REJECTED`(Storytelling First内の要素で足りる)、(2)Storytelling First: `APPROVED_FOR_PRODUCTION`、(3)No Jargon: `APPROVED_FOR_PRODUCTION`と正式決定し、Production初回Writerへの実装・Diagnostic Full Retryとの整合確認・No.9 A2/B1の正式経路からの再生成・Dangling Reference解消までを一貫して行うよう指示した
- **Meaning First**: ユーザー決定により`REJECTED`。独立ruleとしてProductionへ追加しない。ただしStorytelling First指示文内の「聞き手に何を持ち帰ってほしいかを決める」「Meaningを意識してEvidenceを組み立てる」という要素までは削除しない([OPEN_ITEMS.md](OPEN_ITEMS.md)のOPEN-91を`REJECTED / CLOSED`へ更新)
- **Storytelling First / No Jargon のProduction実装**: `er003_v1_n3_01_articles_generate.py::COMMON_BLOCK_TEMPLATE`(全テーマ共通のProduction初回Writer prompt、`run_theme()`[hanshin/health/household回帰用]・`er006_pool_pilot_01_writer.py::run_writer_for_theme()`[No.9等Pool Pilotテーマ]の両方から共有利用される唯一の呼び出し元)へ、2つの新しい【】ブロックとして追加した。Trial-08(`er009_n1_full_writer_ledger_integration_08.py`)の考え方を踏襲しつつ、既存の記事構成(Title/Main Story/Point One・Two/In One Line)・Point Balance原則・Spoken-first数値原則・Fact Ledger制約・Fact safety不変条件のいずれも変更していない(新しい原則は既存原則の前に追記する形で挿入し、既存の禁止事項・生成手順の記述は無変更)。DEV/Trial専用スクリプトだけへの実装ではなく、Production初回Writerの共通テンプレートへ直接実装したため、今後生成する全テーマ・全記事に適用される
- **Diagnostic Full Retryとの整合確認**: `er009_diagnostic_full_retry_modules_12.py::DIAGNOSTIC_SECTION_TEMPLATE`のテキスト自体は変更していない(`Preserve Storytelling First.`/`Preserve No Jargon.`という参照文言はそのまま)。今回の実装により、この参照が指す原則が実際にProduction初回Writer側に存在するようになったため、Dangling Referenceが解消された(参照先と参照元で同じ原則名・同じ意味を持つことを確認済み。retry側が初回仕様を弱めたり別解釈したりしていないことも、DIAGNOSTIC_SECTION_TEMPLATEの文言が初回prompt側のStorytelling First/No Jargon説明と矛盾しないことで確認)
- **Regression**: `run_project_regression.py`で1957件収集・1953件PASS・失敗4件(いずれも既知・無関係な既存事象[`er003_test_bad`のfixture、`er003_test_p2j_investigate`の件数照合3件、`er007_ja_tts_retry_path_fix_test_01`]、新規failureゼロ)。COMMON_BLOCK_TEMPLATEへの追記が既存の`split_common_sections_for_point_qa()`等の構造parsingや既存回帰テストに影響しないことを確認した
- **No.9 Production再生成**: Git保全済みの2026-08-29版(`er006_output/pool_pilot_01/pool_n9_tip_screens/{a2,b1b}/article.md`)を直接上書きせず、新規runner(`er010_no9_storytelling_nojargon_wiring_06.py`)を作成し、新しい出力先(`er010_output/no9_storytelling_nojargon_wiring_06/`)へ生成した。既存の検証済みVerified Fact Ledger(`er006_output/pool_pilot_01/pool_n9_tip_screens/research/verified_fact_ledger.txt`)を再利用し、Research段階は再実行していない。正式Production経路(`er006_pool_pilot_01_writer.run_writer_for_theme` → `er003_v1_n3_01_articles_generate.run_one_pattern`、Point Overlap QA・Diagnostic Full Retry・Fact Checker・Ledger Deviation Checker v2・Directional Fact Precheckを全て含む)をそのまま使用した
- **No.9 runtime evidence**: 実モデルは両level・全stage(Writer・Evidence Compression Editor・Fact Checker・Ledger Deviation Check)とも`gpt-5.6-luna`(`routing.require_model`経由、SSOT参照を確認)。B1はPoint Overlap初回でPASS(Point One 0.256/Point Two 0.259、retry 0回)。A2はPoint One 0.464でflag→Diagnostic Full Retryが実発火(診断情報を含むpromptで全文再生成、article retry 1/2)→retry後Point One 0.219/Point Two 0.200まで収束(いずれも閾値0.40未満でPASS、2回目のretryは不要だった)。Diagnostic Full Retryの実発火とその後の収束を、No.9実データで確認できた
- **No.9 Fact QA結果(正直に報告)**: 今回の再生成候補は、Ledger Deviation Checker v2でA2=MAJOR1件("digital screenが促した場合"という前提条件を落として一般化)+MINOR1件、B1=MAJOR2件(Ledgerに無い具体的な"20%/25%"という推奨率を新規追加、および"タクシーでのクレジットカードチップをゼロ"という結果を"チップ全般からの離脱"へ一般化)を検出し、両levelとも`LEDGER_DEVIATION`だった。Fact Checkerは両levelとも`REVIEW_REQUIRED`(明確な矛盾[FAIL]ではなく、研究の検証範囲を超えた具体化・一般化についての指摘)。Directional Fact Precheckは両levelとも`DIRECTION_REVIEW_REQUIRED`だが、個別に確認した結果は全件「片方にのみ方向表現があり機械的に一致/不一致を判定できない」という既知の限界パターン(CURRENT_SPEC.md記載)のみで、実際の方向反転(conflict)は0件だった。加えてA2はタイトル・本文に絵文字(💳)と太字Markdownを含み、Trial-08や既存承認済み記事(No.1〜9)のスタイルとは異なる書式的逸脱があった
- **今回の判断**: Ledger Deviation(MAJOR)・Fact Checker REVIEW_REQUIRED・A2の書式逸脱は、いずれもこの候補記事固有の生成結果に対する問題であり、Storytelling First/No JargonのProduction配線(コード実装・Diagnostic Full Retryとの整合・regression)自体の欠陥ではないと判断した(Ledger Deviation Checker v2はこの種のscope拡張・新規具体的数値の追加を検出するために正式配線済みの機構であり、今回はその機構が意図通りに機能して実際の問題を捕捉した)。ユーザーの指示(「記事本文の特定・全文提示のみでSTOPしてください」に類する精神、および今回のCheck項目16「ユーザーはこの記事内容を最終確認する」)に従い、この候補をClaude Code側で無断修正・採用・再生成することはせず、実際の生成結果とQA結果をそのまま報告する。該当箇所の手動修正・prompt再調整・現行承認済み版の維持のいずれを選ぶかはユーザー判断待ちとして[OPEN_ITEMS.md](OPEN_ITEMS.md)のOPEN-97へ記録した
- **API call数・コスト(実測)**: `raw_usage_log.jsonl`(`cl.install()`使用、11レコード、Writer本体・Evidence Compression Editor・Diagnostic Full Retry再生成分。Fact Checker/Ledger Deviation呼び出しの一部は別経路のログ集計のため件数に含まれない場合がある)から実測: 合計約$0.071(1 USD=160円換算で約**11.4円**)。全レコードのmodel_idは`gpt-5.6-luna`(routing SSOT通り)で統一されていることを確認した
- **今回実施しなかったこと**: No.9候補記事の内容修正(Ledger Deviation 3件・書式逸脱1件のいずれも)、この候補の正式採用・Git保全済み版への反映・上書き、hanshin/health/householdの3回帰テーマに対する実LLM regeneration(既存の`run_project_regression.py`によるコードレベル回帰確認のみ実施)、Production Wiring Checklist項目12(ユーザー承認内容と実際のProduction behaviorの完全一致)を「候補記事のFact QAが完全にクリーンである」という意味まで拡大解釈すること(Storytelling First/No Jargonの配線自体は完了しているが、個別記事のFact QAクリア可否は記事ごとに別途判断する既存の運用方針[Ledger Deviation Checker v2・Point Overlap QA等と同じ扱い]を維持)
- **影響するCURRENT_SPEC項目**: 「Storytelling First(Production初回Writer正式原則)」「No Jargon(learner-facing本文全体、Production初回Writer正式原則)」を新規行として「## Full Story」節へ追加(いずれも`PRODUCTION_WIRED`、Writer prompt本体への実装完了の意味。個別記事のLedger Deviation有無は記事ごとのQAで別途判定)
- **OPEN_ITEMSへの影響**: OPEN-91(Meaning First)を`REJECTED / CLOSED`へ更新。OPEN-95(Storytelling First/No JargonのDangling Reference)を`RESOLVED / CLOSED`へ更新。新規OPEN-97(No.9再生成候補のFact QA残課題)を`USER_DECISION_REQUIRED`として追加
- **状態**: `PRODUCTION_WIRED`(Storytelling First/No JargonのProduction初回Writerへの実装・Diagnostic Full Retryとの整合確認・regression 1953/1957 PASS・No.9実データでのDiagnostic Full Retry実発火確認・CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS更新まで完了)。**ただし、No.9再生成候補自体の採用可否は`USER_DECISION_REQUIRED`のまま**(OPEN-97、Ledger Deviation 3件・A2書式逸脱の扱いはユーザー判断待ち)

## ER-010-NO9-PRODUCTION-INTEGRATION-FINAL-09(2026-08-31、Local Rewrite/Hook-aware Deviation Checker/Evidence-bounded InterpretationのProduction正式配線・No.9実runtime evidence取得)

- **背景**: 直前のER-010-NO9-SPECIFICATION-RECONCILIATION-08(監査専用、CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS変更なし)で、前回22件の仕様監査には漏れがあり、Trial(`er009_writer_trial_diagnostic_05.py`/`er009_n1_full_writer_ledger_integration_08.py`)に未報告のまま埋もれていたLocal Rewrite・Hook-aware Deviation Checker・Evidence-bounded Interpretationの3仕様、および実質吸収済みだが未追跡だったNumeric Compressionの実態を明らかにした。ユーザーが前者3件を正式`APPROVED_FOR_PRODUCTION`と決定し、OPEN-90(Key Phrase専門語回避)をNo Jargonによる上流解決で不要と判断した上で、Numeric Compressionについては履歴再確認のGateを設けつつ、本体統合とNo.9 A2/B1の実生成によるruntime evidence取得までを指示した
- **Numeric Compression Gate(Case A確定)**: `er003_v1_n3_01_evidence_compression_editor.py`の許可編集リストを、その初回採用commit(`dfc0fe9`、ER-008-EVIDENCE-COMPRESSION-PROD-AND-N7-AUDIO-06、2026-08-26)まで遡って確認した結果、「近似・重複する数字の削減(複数の似た数値の並列を1つの傾向表現へ圧縮する)」という記述が、Numeric Compressionの主旨とほぼ同一のまま**当初から**存在し、同commitのDECISION_LOGにも「ユーザーが正式採用しProduction Writerパイプラインへ配線した」と明記されていることを確認した。Trial-04(Writer側Numeric Compression、er009系列)より前から、Editor側に既に正式採用・Production配線済みの機能が存在していたことになる。ユーザーの記憶(「Editorには数値圧縮機能がなく、追加の議論だった」)とは異なる実態だが、Case A(既存承認記録あり)として確定し、新規実装は行わなかった(既に完成済みのため) | 状態: 変更なし(既存のまま`PRODUCTION_WIRED`)、CURRENT_SPECのEvidence Compression行への追記は不要と判断(既存記述で既に説明済み)
- **OPEN-90のClose**: ユーザー決定により、新しいKey Phrase専門語回避specは追加しないことを確定した(本文へ専門語を持ち込ませない上流対策としてNo Jargonが既にProduction配線済みのため)。`RESOLVED / CLOSED`
- **Local Rewrite Production実装**: 新規モジュール`er010_ledger_local_rewrite_09.py`を作成し、Trial-08(`er009_n1_full_writer_ledger_integration_08.py`)のREWRITE_SYSTEM_PROMPT・3段階escalating attempt(Attempt1=issue提示、Attempt2=flags/explanation追加、Attempt3=scope-safe fallback)・`locate_target_sentence()`(exact substring→word-overlap>=0.25 fallback)をそのまま踏襲した(新しい上限・新しいruleは作らない)。`er003_v1_n3_01_articles_generate.py::run_one_pattern()`のLedger Deviation Check(Hook-aware)直後に配線し、MAJORのみを対象、最大3回試行しても解消しない場合は`human_review_required=True`として記事全体を`NG_REVIEW_REQUIRED`で返す(無限retry禁止、MAJOR残存の黙示PASSを許さない)。局所Rewrite後は記事全体を1回だけ再判定し、`metrics.json`/`length_report.json`も再計算・上書きする
- **Hook-aware Deviation Checker Production実装**: `er003_v1_en_direct_vfl_01_generate.py::run_deviation_check()`へ`hook_aware`引数(既定`False`)を追加し、Trial-05(`er009_writer_trial_diagnostic_05.py`)のHOOK_CLAUSE設計をそのまま踏襲した。語りかけ・場面描写として機能し、Ledger内で既に確認済みの状況を会話的に言い換えているだけで新しい具体的Factを追加していない一文に限り、`changed_scope`/`changed_comparison`の2種類だけを緩和対象とする。それ以外の8種類は常に通常通り検査する。schemaへ`treated_as_hook`フィールドを追加(既存の`_apply_deviation_post_hoc_validation`は無変更で両対応)。Production呼び出し側のみ`hook_aware=True`を明示的に渡し、他の全DEV/Trial呼び出し元は無変更のまま(既定False)
- **Evidence-bounded Interpretation Production実装**: `er003_v1_n3_01_articles_generate.py::COMMON_BLOCK_TEMPLATE`のNo Jargon節の直後へ、Trial-05のEVIDENCE_BOUNDED_INTERPRETATION文をほぼそのまま追加した(解釈・示唆・締めの一言はLedgerのscope/causality/certaintyを超えない、特定集団の結果を広い集団へ一般化しない、"always"/"every time"のような一般的断定にしない、確信が持てない場合はより小さく安全な表現にするか省く)
- **Regression**: 新規`er010_n9_production_integration_09_test_01.py`(19件、mock LLMのみ・実API呼び出しなし)で、(1)Evidence-bounded Interpretationのprompt内容・既存原則との共存・template整形、(2)Hook-aware Deviation Checkerの既定False/明示的True切替・schema切替・治療対象フィールドの伝播・post-hoc降格ロジックとの共存、(3)`locate_target_sentence()`のexact/fuzzy/not-foundの3パターン、(4)`rewrite_ng_item()`のAttempt1解消・3回失敗後human_review_required、(5)`apply_rewrites()`、(6)`run_one_pattern()`全体配線(MAJOR検出→局所Rewrite→解消→OK、または未解消→NG_REVIEW_REQUIRED・Directional Fact Precheck未実行)を確認、全件PASS。既存の関連回帰(`er008_n8_point_overlap_article_retry_22_test_01.py`・`er008_directional_fact_precheck_08_test_01.py`・`er008_n3_01_point_qa_wiring_19_test_01.py`・`er008_point_overlap_qa_18_test_01.py`・`er009_ledger_deviation_recalibration_02_test.py`[schema/post-hoc降格が変更後も無事]・`er009_n1_diagnostic_full_retry_integration_test_13.py`・`er003_v1_en_direct_vfl_01_generate_deviation_v2_test.py`[hook_aware未指定時の既定挙動が無変更であることを確認]、その他）も全PASS。プロジェクト全体`run_project_regression.py`は1976件収集・1972件PASS・失敗4件(いずれも既知・無関係な既存事象[`er003_test_bad`のfixture、`er003_test_p2j_investigate`の件数照合meta-test3件が本タスクで19件のtestを追加したことにより件数不一致を再現、`er007_ja_tts_retry_path_fix_test_01`]、新規failureゼロ)
- **No.9 A2/B1 Production実runtime evidence**: 新規runner`er010_no9_production_integration_final_09.py`(`er006_pool_pilot_01_writer.run_writer_for_theme`→`gen.run_one_pattern`という正式Production初回経路をそのまま使用、既存の検証済みVerified Fact Ledgerを再利用しResearch段階は再実行せず)で、Git保全済みの過去出力・ER-010-06版候補のいずれも上書きせず新規出力先(`er010_output/no9_production_integration_final_09/`)へ生成した。
  - **実モデル**: 全15回のAPI呼び出し(Writer・Evidence Compression Editor・Fact Checker・Ledger Deviation Check[Hook-aware]・局所Rewrite全て含む)が`gpt-5.6-luna`で統一されていることを実測ログ(`raw_usage_log.jsonl`)で確認した
  - **B1B**: `status="OK"`。Point Overlap QAは初回でPASS(retry不要)。Fact Checker`REVIEW_REQUIRED`(4件、うち1件はRutgers記事が「高級店」限定で報告した統計を記事が「米国の飲食店全体」へ一般化している、というscope拡張の指摘。これはEvidence-bounded Interpretationが対象とする「解釈・締めの一言」ではなく本文中のEvidence説明文でのscope拡張であり、**本指示の対象範囲外であることが実データで確認された**)。Ledger Deviation Checker(Hook-aware)はMINOR2件・MAJOR0件で`LEDGER_COMPLIANT`(いずれも`treated_as_hook: false`、Hook緩和の対象にはならなかった通常判定)。Directional Fact Precheckは`DIRECTION_REVIEW_REQUIRED`だが、個別確認の結果は全件「片方にのみ方向表現があり機械的判定不能」という既知の限界パターンのみで、実際の方向反転は0件(ER-010-06版と同じ既知パターン)。絵文字・太字などの書式逸脱は無し
  - **A2**: 初回Hook-aware判定でMAJOR3件を検出(未確認の方法論的前提の断定、レストランへの無根拠な一般化、"today"という時点の無根拠な更新)。**Local Rewriteが初めて実runtimeで発火し、3件全てがAttempt1で解消した**(例: Before "The rides were very similar, so the researchers could compare passengers who saw different menus." → After "The researchers used the fare threshold to compare passengers who saw different menus."、詳細3件は`a2/audit/local_rewrite_results.json`)。局所Rewrite後の最終全文再判定で、局所Rewrite対象ではなかった**タイトル**"Why the Tip Screen Always Suggests More Than You Meant to Give"が新たにMAJOR(`changed_certainty`、"Always"という絶対語)として検出された。判定は`treated_as_hook: true`(タイトルはHookとして扱われた)だが、changed_certaintyはHook-aware設計上緩和対象外の8種類の1つであるため、**Hookとして扱われてもFact Safetyが緩和されないという設計通りの動作を実データで確認**した。ただしこの指摘は初回判定(局所RewriteのトリガーとなったMAJOR3件)には含まれておらず、ほぼ同一本文への2回の独立判定間で結果が変わったことになる(新規OPEN-98、下記参照)。設計通りfail-closedで`status="NG_REVIEW_REQUIRED"`となり、Directional Fact Precheckは実行していない。絵文字・太字などの書式逸脱(ER-010-06版A2で見られた💳・太字)は今回は再発しなかった
  - **実測コスト**: 15コール合計で入力138,346トークン・出力38,273トークン(Luna単価換算で概算$0.074、Fact Checker 2回分のweb検索tool手数料[概算$0.08×2]を含めても概算$0.2程度、¥30前後)
- **新規発見(OPEN-98として記録)**: Ledger Deviation Checker(Hook-aware)が、ほぼ同一本文への2回の独立LLM呼び出し間で判定結果が変わる事例を今回初めて観測した(A2タイトルの"Always"、局所Rewrite前後で本文自体は無変更)。Fact Checkerのライブ検索非決定性(OPEN-92)とは異なり、Ledger Deviation Checkerはweb検索を伴わないにもかかわらず同種の非決定性が観測された。今回は設計通りfail-closedで正しく検知されたため実害は無い
- **今回実施しなかったこと**: Numeric Compressionの新規実装(既に完成済みのCase Aと確定したため)、A2 NG_REVIEW_REQUIRED候補の内容修正・採用判断、旧ER-010-06候補・Git保全済み2026-08-29版の上書き、他22テーマへの遡及適用、OPEN-98(Deviation Checker非決定性)の恒久対策実装
- **影響するCURRENT_SPEC項目**: 新設「Evidence-bounded Interpretation(Production初回Writer正式原則)」「Hook-aware Deviation Checker(Ledger Deviation Checker v2への追加ロジック)」「Ledger Deviation MAJOR時の局所Rewrite(Local Rewrite)」の3行を追加(いずれも`PRODUCTION_WIRED`)。「No Jargon」行にOPEN-90 CLOSEを追記
- **OPEN_ITEMSへの影響**: OPEN-90を`RESOLVED / CLOSED`へ更新(No Jargonによる上流解決)。OPEN-97を更新し、対象を新候補(ER-010-09版)へ切り替え(旧ER-010-06版はsuperseded)、引き続き`USER_DECISION_REQUIRED`のまま維持。新規OPEN-98(Ledger Deviation Checkerのrun-to-run非決定性)を`TBD`として追加
- **状態**: Local Rewrite/Hook-aware Deviation Checker/Evidence-bounded Interpretationはいずれも`PRODUCTION_WIRED`(実装完了・No.9実runtimeでの実発火確認まで完了)。Numeric Compressionは新規変更なし(既存のまま`PRODUCTION_WIRED`)。**No.9新候補(ER-010-09版)自体の採用可否は引き続き`USER_DECISION_REQUIRED`のまま**(OPEN-97更新、A2のタイトル"Always"1件が未解消のままNG_REVIEW_REQUIRED)

## ER-010-NO9-LOCAL-REWRITE-LOOP-FINAL-10(2026-08-31、Local Rewrite Loop化・No.9新候補でLedger MAJOR=0達成・OPEN-98クローズ)

- **背景**: 前回(ER-010-NO9-PRODUCTION-INTEGRATION-FINAL-09)のNo.9 A2生成で、局所Rewriteが初回MAJOR3件をAttempt1で解消したものの、その後の記事全体の最終再判定で修正対象ではなかったタイトルの"Always"が新たにMAJORとして検出され、対応の仕組みが無いままNG_REVIEW_REQUIREDで停止した。ユーザーがこれを「単発の修復で終わらせず、全体再Checkで新規MAJORが出た場合も上限cycleまで再度局所Rewriteする」設計へ拡張するよう正式指示した。
- **User Decision(今回分)**:
  - OPEN-98(Ledger Deviation Checkerのrun-to-run判定揺らぎ)は独立Open Itemとして追跡しない。理由: LLM判定の一定の揺らぎは既知特性であり、今回はfail-safe側に停止して実害が無かったこと、判定揺らぎ一般をすべてOpen Item化すると管理過多になること。将来、頻発・実害が確認された場合のみ改めて起票する方針とし、`CLOSED / REMOVE`とした。
  - Diagnostic Full Retryは、今回のNo.9生成で自然発火しなくても`PRODUCTION_WIRED`のまま維持する(仕様採用・Production配線・Trial実績・診断情報生成・全文Retry・最大2回・fail-closedがいずれも揃っているため、発火有無を理由に降格しない)。
- **実装内容(Local Rewrite Loop化)**: `er010_ledger_local_rewrite_09.py`へ`MAX_REWRITE_CYCLES = MAX_REWRITE_ATTEMPTS`(=3)を追加。新しい上限値を独自に発明せず、既存承認済みの文単位試行上限(Trial-08由来)を記事全体cycleという別次元にそのまま適用したもの(ユーザーが本ラウンドで明示的に許可した適用範囲整理)。`er003_v1_n3_01_articles_generate.py::run_one_pattern()`のLocal Rewrite呼び出しを、`while major_items and cycle < MAX_REWRITE_CYCLES`のループへ書き換えた。各cycleで(1)そのcycleのMAJOR群を局所Rewrite、(2)記事全体をmetrics/length_report再計算の上で全体再判定、(3)そこで見つかったMAJORを次cycleの対象として引き継ぐ、を繰り返す。上限まで繰り返してもMAJORが残る場合は`cycle_exhausted=True`とし、`human_review_required`同様にNG_REVIEW_REQUIREDへフォールバックする(無限retry禁止・黙示的PASS禁止は維持)。各cycleの対象文・新規発見claim・全体再判定結果は`audit/local_rewrite_cycles.json`へ、全cycle分の個別item結果は従来通り`audit/local_rewrite_results.json`へ記録する。
- **回帰テスト**: `er010_n9_production_integration_09_test_01.py`に3件追加(計21件、全PASS)。(1)`test_new_major_discovered_after_first_cycle_triggers_second_rewrite_cycle`: cycle1で本文の1文を解消した後の全体再Checkで、修正対象ではなかった別文(タイトル相当)が新規MAJORとして検出され、それがcycle2で解消されて最終`status="OK"`に至る、前回A2で実際に観測されたシナリオそのものを模擬再現し、Loopが正しく機能することを確認。(2)`test_cycle_limit_exhausted_returns_ng_review_required_and_skips_directional_precheck`: 同一claimがcycle上限(3回)まで解消せず`NG_REVIEW_REQUIRED`・Directional Fact Precheck未実行に至ることを確認。(3)`test_cycle_limit_reuses_existing_attempt_limit_basis`: `MAX_REWRITE_CYCLES == MAX_REWRITE_ATTEMPTS`であることを保証する回帰(新しい値が独自に混入していないことのガード)。プロジェクト全体回帰(`run_project_regression.py`): 1978件収集・1974件PASS・4件失敗(いずれも既知・無関係: `er003_test_bad.FixtureTests.test_case_0`、`er003_test_p2j_investigate`の件数整合3件、`er007_ja_tts_retry_path_fix_test_01`のTTS retryテスト1件。件数が変わると自動的に不一致になる自己言及的メタテスト[OPEN-77]の性質によるもので、今回の変更による新規リグレッションではない)。
- **No.9新候補(`er010_output/no9_local_rewrite_loop_final_10/`)runtime evidence**: Production正式初回経路(`er006_pool_pilot_01_writer.run_writer_for_theme` → `run_one_pattern()`)で実際にA2/B1Bを生成した。既存のNo.9 Verified Fact Ledger(research段階は再実行せず)を使用。Git保全済みの2026-08-29版本番記事、ER-010-06版候補、ER-010-09版候補はいずれも一切上書きしていない。
  - **B1B**: 初回Hook-aware判定でLEDGER_COMPLIANT(MINOR1件、`changed_time`: 2022年の35%記述を"Today"へ拡張。Hookとしては扱われず通常の説明文として判定)、MAJOR0件のためLocal Rewrite Loop自体は発火せず(`local_rewrite_cycles=0`)、`status="OK"`。
  - **A2**: 初回Hook-aware判定でMAJOR1件("The rides were very similar."という未確認の方法論的前提の断定)を検出。Local Rewrite cycle1・Attempt1で"The analysis compared rides with fares just below and just above the threshold."へ解消し、全体再判定は`LEDGER_COMPLIANT`(MAJOR/MINORとも0件)。前回(ER-010-09)観測された「局所Rewrite対象外の箇所が最終再判定で新規MAJOR化する」現象は、今回のNo.9では自然発生しなかった(Loopの2周目分岐そのものは上記回帰テストで別途実証済み)。`status="OK"`。
  - **Point Overlap QA**: A2(overlap 0.333/0.355)・B1B(overlap 0.100/0.195)とも初回で閾値0.40未満、retry 0/2で通過。Diagnostic Full Retryはこの結果として今回も自然発火の機会が無かった(人工的にNG発生させるTrialは実施していない、正直に報告)。
  - **Fact Checker(live web検索)**: A2・B1Bとも`REVIEW_REQUIRED`。指摘は3種: (1)Haggag and Paci論文が直接検証したのは推奨額全体を上げることの因果効果であり「最初の数字がアンカーになる」という心理メカニズムそのものは論文が識別していない(causality/mechanismの言い過ぎ)、(2)Rutgers報告の「最上級店」限定を「米国の飲食店全体」へ一般化している(scope拡張)、(3)(B1Bのみ)タクシー研究の効果をレストラン画面へ直接一般化している(scope拡張)。いずれも「解釈・示唆・締めの一言」ではなく本文中のEvidence説明文で発生しており、Ledger Deviation Checkerでは検知されない(Evidence-bounded Interpretationの対象範囲外という、前回確認済みの限界が2回目の独立データで再確認された)。分類: **Writer scope問題**(Ledger Deviation Checkerの対象外・Local Rewrite Loopのトリガーにもならない、既存設計上の意図的な非対応)。恒久対策は今回実装していない(STOP C相当の新Writer ruleを独断で追加しない)。
  - **Directional Fact Precheck**: A2・B1Bとも`DIRECTION_REVIEW_REQUIRED`(A2は5件中4件が「片方にのみ方向表現があり機械的判定不能」の既知パターン+1件MATCH、B1Bも同様の構成)、実際の方向反転(`conflicts`)は0件。
  - **新規発見(絵文字・太字Markdownの再発)**: A2のタイトル("💳 Why Digital Tip Screens Keep Asking for More Than You Planned")と本文各所に太字Markdown(`**13 million**`、`**zero**`、`**guilt tipping**`等、10箇所以上)が再発し、B1Bもタイトル("💳 Why Tip Screens Often Ask for More Than You Planned")に絵文字が再発した。この問題はER-010-06版候補で最初に観測され、ER-010-09版候補では再発しなかった(prompt=`COMMON_BLOCK_TEMPLATE`は3ラウンドとも無変更)。既存のQA gate(Ledger Deviation Checker/Fact Checker/Point Overlap QA/Directional Fact Precheck)はいずれもこの書式問題を検知対象にしていないため、3回とも同じprompt条件下でWriterのrun-to-run非決定性により出現有無が変わっていることが確認された。新規Open Item(OPEN-99)として記録し、恒久対策(prompt側への明示的禁止一文の追加/自動書式Validatorの新設/人間の目視確認継続)は今回実装せず、ユーザー判断を仰ぐ(STOP B相当、独断実装はしない)。
  - **実測コスト**: 11コール合計で入力149,710トークン・出力43,639トークン(全てgpt-5.6-luna、`raw_usage_log.jsonl`で確認)。前回(ER-010-09、138,346in/38,273out、概算$0.2/¥30前後)とほぼ同規模であり、今回も概算$0.2/¥30前後と見積もられる(専用cost_log.jsonlは今回生成していないため、トークン量からの概算に留める)。
- **OPEN_ITEMSへの影響**: OPEN-98を`CLOSED / REMOVE`(ユーザー判断、理由は上記User Decision参照、テーブル行自体を削除)。OPEN-97を更新し、対象を新候補(ER-010-10版)へ切り替え(ER-010-06版・ER-010-09版はいずれもsuperseded)、引き続き`USER_DECISION_REQUIRED`のまま維持(Fact Checker REVIEW_REQUIRED 3件の分類判断・絵文字/太字再発への対応方針の2点が新たな決定事項として追加)。新規OPEN-99(絵文字・太字Markdownの再発、既存QA gate範囲外)を`USER_DECISION_REQUIRED`として追加。
- **影響するCURRENT_SPEC項目**: 「Ledger Deviation MAJOR時の局所Rewrite(Local Rewrite)」行にLoop化の設計・cycle上限根拠・No.9新候補runtime確認を追記。「Hook-aware Deviation Checker」「Evidence-bounded Interpretation」の2行に今回のNo.9新候補runtime確認を追記(Evidence-bounded Interpretationの対象外範囲の限界が2回目のデータで再確認されたことを含む)。「Point One/TwoとFull Storyの意味重複検知+Point-only regeneration」(Diagnostic Full Retryを含む行)に、今回発火しなくても`PRODUCTION_WIRED`を維持する旨のユーザー再確認を追記。
- **今回実施しなかったこと**: 絵文字・太字Markdown再発(OPEN-99)への恒久対策の実装(prompt変更・自動Validator新設のいずれも)、Fact Checkerが指摘した3件のcausality/scope懸念に対するWriter prompt側の新ルール追加、Point Overlap NGを人工的に発生させるTrial、旧候補(ER-010-06版・09版)・Git保全済み2026-08-29版の上書き、他22テーマへの遡及適用。
- **状態**: Local Rewrite Loopは`PRODUCTION_WIRED`(Loop化実装完了・cycle2分岐は回帰テストで実証済み・No.9新候補ではcycle1のみで収束)。Hook-aware Deviation Checker/Evidence-bounded Interpretationは引き続き`PRODUCTION_WIRED`(今回のNo.9新候補で追加runtime確認)。Diagnostic Full Retryは`PRODUCTION_WIRED`を維持(今回も自然発火なし、ユーザーが明示的に維持を再決定)。**No.9新候補(ER-010-10版)自体の採用可否は引き続き`USER_DECISION_REQUIRED`のまま**(Ledger MAJORはA2/B1Bとも0件まで到達したが、Fact Checker REVIEW_REQUIRED 3件の扱いと絵文字・太字再発[OPEN-99]への対応方針が未決定のため、No.9は最終ユーザーレビューへ出荷できる状態ではない)。

## ER-010-NO9-FORMAT-PRODUCTION-AND-FACT-REVIEW-11(2026-09-01、Formatting禁止仕様のProduction正式反映・No.9新候補でLedger MAJOR=0達成。**本エントリは前回セッションの実装をSSOTへ事後反映するbackfillであり、次のER-010-NO9-FACTCHECK-POLICY-AND-POINT-COMPRESSION-DIAGNOSTIC-12タスクの一環として追記した**)

- **背景**: OPEN-99(絵文字・太字Markdown再発、既存QA gate範囲外)への対応として、`COMMON_BLOCK_TEMPLATE`・Local Rewrite Promptへ「絵文字・不要な太字禁止」指示を追加し、`normalize_article_formatting()`関数(emoji・bold削除、複数スペース圧縮)をWriter出力後・Evidence Compression後・Local Rewrite後の呼び出し経路(`_generate_and_compress_article()`内・Local Rewrite cycle内の計2箇所)へ配線した。
- **回帰テスト**: `FormattingNormalizationTests`6件を`er010_n9_production_integration_09_test_01.py`へ追加(全PASS)。プロジェクト全体回帰27/27 PASS(コミットメッセージ記載の実行結果)。
- **No.9新候補(`er010_output/no9_formatting_production_and_fact_review_11/`)runtime evidence**: `er006_pool_pilot_01_writer.run_writer_for_theme`経由でA2/B1Bを再生成。
  - **A2**: 初回Hook-aware判定でLedger Deviation MAJOR1件を検出したが、Local Rewrite cycle1・Attempt1で解消し、全体再判定`LEDGER_COMPLIANT`(MAJOR/MINORとも0件)。Point Overlap QAは初回(retry 0/2)で通過。Fact Checker `REVIEW_REQUIRED`(指摘4件、詳細は次エントリのFact QA参照)。絵文字・太字は本文・タイトルとも0件を確認。
  - **B1B**: 初回Point Overlap QAでNG(overlap 0.500/0.405)となり、Diagnostic Full Retryにより記事全体retry 1回で解消(retry後overlap 0.219/0.364)。Ledger Deviation `LEDGER_COMPLIANT`(MINOR1件、MAJOR0件、Local Rewrite Loop不発火)。Fact Checker `REVIEW_REQUIRED`(指摘2件、詳細は次エントリのFact QA参照)。絵文字・太字は本文・タイトルとも0件を確認。
  - 絵文字・太字Markdownの再発(OPEN-99)は、prompt側の明示禁止+`normalize_article_formatting()`のfail-safe削除の二重対策により、この候補では再発しなかった。
- **状態**: Formatting禁止仕様は`PRODUCTION_WIRED`(prompt側禁止指示+自動削除の二重対策、regression 6件PASSで確認)。No.9新候補(ER-010-11版)自体は、次エントリ(ER-010-NO9-FACTCHECK-POLICY-AND-POINT-COMPRESSION-DIAGNOSTIC-12)でFact Checker運用の新方針を適用した上で最終評価する。
- **前回セッションの記録漏れ**: このコミット(`32be1c6`)はDECISION_LOG.md/OPEN_ITEMS.mdを更新せずに完了しており、OPEN-97/OPEN-99はER-010-10版時点の記述のまま取り残されていた。本backfillエントリと次エントリで、OPEN-97/OPEN-99をこのER-010-11版のruntime evidenceに基づいて正式に更新する。

## ER-010-NO9-FACTCHECK-POLICY-AND-POINT-COMPRESSION-DIAGNOSTIC-12(2026-09-01、Fact Checker REVIEW_REQUIREDのnon-blocking advisory化・Production実装・No.9 Point解説の数字羅列問題の診断)

### A. Fact Checker運用の正式変更(User Decision→Production実装)

- **User Decision**: Fact Checkerの`verdict="REVIEW_REQUIRED"`(`fact_checker_prompt_template_r3.txt`定義=「確認できない具体的主張、解釈、引用風表現など(矛盾とまでは言えない)」)を、原則`USER_DECISION_REQUIRED`でSTOPさせず、non-blocking advisoryとして扱う。理由: Storytelling First等で一定の解釈・自由度を与える以上、研究が直接証明した範囲との境界には揺らぎが出る。それを全てNGにすると調査結果の読み上げに近い記事になりやすく、Rewrite回数・Cost・Latencyも増える。明確なFact error・unsupported number・actorの誤り・事実関係の逆転・強いunsupported causality・重大なscope distortion・安全性上重大な誤りは引き続きblocking。
- **現状調査の結果**: `er003_v1_n3_01_articles_generate.py::run_one_pattern()`を精査した結果、従来の実装は`fact_verdict`(REVIEW_REQUIREDだけでなくFAILも含む)を`fact_qa.json`へ記録するのみで、記事のstatus判定(`OK`/`NG_REVIEW_REQUIRED`)には一切使っていなかったことが判明した。実質的にREVIEW_REQUIREDは既にnon-blockingだったが、**verdict="FAIL"(`fact_checker_prompt_template_r3.txt`定義=「信頼できる情報と明確に矛盾する」)であっても記事を自動的にblockする仕組みが存在しない実装漏れ**だった。「REVIEW_REQUIRED=non-blocking、FAIL=blocking」というユーザーDecisionの後半(明確なFact errorはblocking)を満たすには、この漏れの修正が必要と判断した。
- **実装**: `run_one_pattern()`のFact Checker呼び出し直後に、`verdict == "FAIL"`の場合のみ`NG_REVIEW_REQUIRED`を返しLedger逸脱チェック以降を実行しない分岐を追加した(Ledger Deviation MAJOR残存・Point overlap未解消と同じfail-closedパターンを踏襲、新しい仕組みは発明していない)。REVIEW_REQUIRED/PASSは従来通りLedger逸脱チェックへ継続する。
- **回帰テスト**: 新規`er010_no9_factcheck_policy_and_point_compression_diagnostic_12_test_01.py`(4件、モックのみ、実LLM呼び出しなし)。(1)REVIEW_REQUIRED→`status="OK"`かつLedger逸脱チェックが呼ばれることを確認、(2)PASS→同様に`status="OK"`(従来動作の非破壊確認)、(3)FAIL→`status="NG_REVIEW_REQUIRED"`かつLedger逸脱チェックが**呼ばれない**ことを確認、(4)FAIL時も`article_text`/`fact_check_result`が結果に保持されることを確認。全4件PASS。`run_project_regression.py`: 1988件収集・1984件PASS・4件失敗(いずれも既知・無関係の既存事象: `er003_test_bad.FixtureTests.test_case_0`、`er003_test_p2j_investigate`の件数整合3件、`er007_ja_tts_retry_path_fix_test_01`のTTS retryテスト1件。今回の変更による新規failureはゼロ)。
- **役割の区別**: Fact Checkerは独立Web検索によるexternal factとの整合性判定、Ledger Deviation CheckerはVerified Fact Ledgerとの整合性判定であり、両者のMAJOR/blocking判定を混同しない。Fact Checker REVIEW_REQUIREDはLedger Deviation CheckerのMAJOR判定とは独立で、Local Rewrite Loopのトリガーにもならない(既存の意図的な設計、無変更)。
- **最終提示仕様**: 今後、記事最終提示時にFact Checker参考指摘(`fact_qa.json`のcontradictions/unsupported_specific_claims/notes)を、記事本文とは別に、指摘箇所・理由・明確なFact errorか/scope・interpretation・certainty nuanceかを添えて提示する(学習者向け本文へは混ぜない、コード実装は不要でfact_qa.json自体が既にこの情報を保持している)。
- **状態**: `APPROVED_FOR_PRODUCTION`→`PRODUCTION_WIRED`(Production実装完了・回帰テスト・runtime動作[No.9実データでのREVIEW_REQUIRED非block確認]まで確認済み)。

### B. No.9(ER-010-11版候補)Fact Checker指摘の扱い

最新No.9候補(`er010_output/no9_formatting_production_and_fact_review_11/`)のFact Checker指摘を実データで確認した(ER-010-10版時点の指摘とは記事本文が異なるため、指摘内容も一部異なる)。

- **A2**(`verdict=REVIEW_REQUIRED`): (1)"guilt tipping"という語をMichael Lahr本人の命名として帰属している点(Rutgersレポート本文はNYT記者Christina Moralesの紹介経由の可能性)、(2)"Cash made the choice more private"という対比表現がRutgers資料で直接実証された主張ではない点、(3)"some passengers did not enter a smaller custom amount"が、研究が直接観察した「クレジットカード上のゼロチップ増加」を超えた具体化である点、(4)"The first number on the screen became a starting point"が、研究本文の「推奨額全体の効果分析」を「最初の番号」自体の効果に具体化している点。いずれも**attribution/interpretation/certainty nuance**であり、事実の逆転・unsupported numberではない。
- **B1B**(`verdict=REVIEW_REQUIRED`): (1)「最初の数字が基準になる」というアンカリング心理メカニズム自体をHaggag and Paci論文が直接検証していない点(論文は推奨額全体の変更効果を比較したもので、メカニズムそのものは研究側も特定できないとしている)、(2)"Today, digital payment screens can show tips of up to 35 percent"という現在時制の主張が、確認できたRutgers 2022年ブリーフの2022年時点記述であり2026年現在の継続を裏付けていない点。いずれも**mechanism-overreach/scope・certainty nuance**。
- **判定**: 両levelとも、ユーザーが正式決定した新方針(上記A節)における「blocking」基準(明確なFact error・unsupported number・actorの誤り・事実関係の逆転・強いunsupported causality・重大なscope distortion・安全性上重大な誤り)のいずれにも該当しない。全てnon-blocking advisoryとしてPASS扱いとし、この指摘だけを理由にNo.9をSTOPしない。最終提示時の参考情報として保持する。

### C. OPEN-97/OPEN-99の整理

- **OPEN-97**: 対象をER-010-11版候補へ更新する。この候補はA2 Ledger Deviation `LEDGER_COMPLIANT`(MAJOR/MINORとも0件)、B1B `LEDGER_COMPLIANT`(MINOR1件、MAJOR0件)、Point Overlap QA双方PASS、絵文字/bold双方0件、Fact Checker REVIEW_REQUIREDは上記B節の通り新方針でnon-blocking advisoryに分類される。他にblocking QAが残っていないため、Fact Checker REVIEW_REQUIREDだけを理由にOPEN-97を`USER_DECISION_REQUIRED`のまま維持しない。`RESOLVED / CLOSED`とする(旧候補[ER-010-06版・09版・10版]はいずれもsupersededのまま)。Directional Fact Precheckは両levelとも`DIRECTION_REVIEW_REQUIRED`のままだが、これは既存の「片方にのみ方向表現があり機械的判定不能」という既知の限界パターンに関する暫定チェックであり、Fact Checkerとは別問題として引き続き非blocking扱いを維持する(個別確認は今回実施していない、既存の設計上の性質として記録するのみ)。
- **OPEN-99**: ER-010-11版で実装したFormatting禁止仕様(prompt側禁止指示+`normalize_article_formatting()`によるfail-safe自動削除)により、ER-010-11版のA2/B1B両候補で絵文字・太字Markdownの再発が確認されなかった(本文・タイトルとも0件)。回帰テスト6件もPASS。`RESOLVED / CLOSED`とする。

### D. No.9 Point解説の数字羅列問題(Point Compression診断、今回は診断のみ・新仕様は実装しない)

- **対象**: ER-010-11版候補のA2 Point Two("The pushback is growing")・B1B Point Two("Customers are pushing back")。A2で指摘された78%・44%・66%→59%・36%を各Stageで追跡した。
- **Stage別pre/post比較(A2)**:
  | Stage | Point Two本文の数字 | 変化 |
  |---|---|---|
  | Writer raw(`audit/pre_editor_article.md`) | 78%, 44%, 66%→59%, 36% (計5個) | — |
  | Evidence Compression Editor input(同上、Editorへの入力はWriter raw) | 同上 | 変化なし |
  | Evidence Compression Editor output(`audit/evidence_compression_editor_raw.json`) | 78%, 44%, 66%→59%, 36% (計5個、数値は不変) | 出典名のみ圧縮("Popmenu's 2026 survey"→"a 2026 survey")、数字は一切削減・統合されず |
  | Point Overlap QA/Retry後 | retry 0回で通過(発火なし) | 該当なし |
  | Local Rewrite前後 | Main Story内の1文("This question is now common outside taxis."→"...beyond taxis, including in some digital POS settings.")のみ対象、Point Twoは対象外 | Point Twoへの影響なし |
  | Final(`article.md`) | 78%, 44%, 66%→59%, 36% (計5個) | Writer rawから完全に不変 |
- **Stage別pre/post比較(B1B)**: Writer raw・Editor output・Finalのいずれでも、Point Two相当の段落に78%, 44%, 66%→59%, 36%(計5個)が一貫して残存することを確認した(語り口の細部はStageごとに異なる、後述の**データ整合性に関する注記**参照)。数値の個数・値そのものは、少なくともWriter raw時点とFinal時点の2点間で完全に一致しており、Numeric Compressionが実効した形跡はない。
- **データ整合性に関する注記(正直に記録)**: B1B(ER-010-11版)では、`audit/evidence_compression_editor_raw.json`のraw_textと最終`article.md`のテキストが、タイトルを含め文章表現面で大きく異なっており(SequenceMatcher類似度0.15)、通常のEvidence Compression(spoken layerの軽微な軽量化のみ)で説明できる差ではなかった。一方、Point Two内の数字の個数・値(78%, 44%, 66%→59%, 36%)そのものは、`audit/pre_editor_article.md`(Writer raw)と最終`article.md`のいずれでも一致しており、本診断の結論(数字が一切圧縮されなかった)には影響しない。ただし、この文章表現面の不一致自体の原因はコード読解のみでは特定できず(`_generate_and_compress_article()`のarticle.md書き込みはeditor出力を直接書き込む単純な実装であり、コード上はraw_text=article.mdとなるはずだが、実際のoutputディレクトリではそうなっていない)、今回は原因不明のまま記録するに留める。A2側では同種の不一致は見られなかった(Point Overlap Retryが発火せずWriter呼び出しが1回のみだったA2に対し、B1BはRetryで2回Writer呼び出しが発生している点が唯一の構造的違い)。今回のタスク範囲(Point Compression診断)を超えるため、原因調査は別途のOpen Itemとして記録する(下記OPEN追加参照)。
- **Ledger側の事実確認**: `er006_output/pool_pilot_01/pool_n9_tip_screens/research/verified_fact_ledger.txt`を確認した結果、78%/44%は[F-011]、66%→59%は[F-012]、36%は[F-013]という**3つの別々のFactとして最初から分離登録**されていた(それぞれ異なるnumeric_scope: 「チップ慣行への評価」「チップ削減行動」「チップを残す義務感の変化」「カスタム額選択の割合」)。さらに[F-011]は元は78%/44%/42%の3値、[F-013]は元は36%/32%/17%の3値であり、**WriterはこれらのうちF-011の42%・F-013の32%と17%を既に落として5値まで絞っている**(完全な数字羅列の読み上げではなく、一定の取捨選択は行われている)。また、Ledger冒頭の注記1に「本Ledgerはnumber_classification(ANCHOR/SUPPORTING/DISPENSABLE)およびexactness_requirement(EXACT_REQUIRED/APPROXIMATE_OK/DIRECTION_ONLY)の個別タグを含まない。Spoken-first原則(数字の扱い、A〜E)は編集判断として適用すること」と明記されており、Writerは構造化タグの支援なしに純粋な編集判断でこれらの数字を扱う必要があった。
- **Numeric Compressionの正式仕様確認(Production Writer側=Storytelling First内の一文)**: `COMMON_BLOCK_TEMPLATE`(`er003_v1_n3_01_articles_generate.py`)のStorytelling First節に「理解に必要な数字だけを使い、**同じ傾向を示す複数の数字**がLedgerにある場合は、それらを自然な言葉でまとめてください」という一文がある。この一文は明示的に「同じ傾向を示す」数字のみを対象としており、[F-011]/[F-012]/[F-013]のように**異なる設問・異なる意味を持つ数字の羅列を減らす**ことは範囲外である(Ledger自身がこれらを別Factとして分離登録していることとも整合する)。
- **Numeric Compressionの正式仕様確認(Evidence Compression Editor側)**: `er003_v1_n3_01_evidence_compression_editor.py::EVIDENCE_COMPRESSION_EDITOR_PROMPT_TEMPLATE`も同様に「近似・重複する数字の削減(意味が変わらない範囲で、複数の似た数値の並列を1つの傾向表現へ圧縮する。ただし56%→40%→約1/3のような、トレンドの大きさ・方向そのものを理解するために必要な核心的な比較は残す)」と定義されており、対象は「近似・重複」する同一trendの数字に限定される。[F-011]/[F-012]/[F-013]の5値は互いに異なる設問への回答割合であり、Editor自身の定義上も圧縮対象外である。この判定は実データでも確認された(Editorはこれら5値を一切変更せず、出典名の一般化のみを行った)。
- **既存の「Point専用・より強いNumeric Compression指示」が未配線であることの発見**: `er003_v1_n3_01_articles_generate.py::EVIDENCE_COMPRESSION_BLOCK`(Writer側のオプション追加ブロック、方式B「Compression-aware Writer」)には、「1つのPointの中で複数の数字が連続し、リスナーの注意が意味ではなく数値の記憶へ向いてしまう状態は避けてください」という、**まさに今回observedされた問題を直接名指しした、より強い指示**が既に存在する。しかし、この指示は`build_common_block()`の`evidence_compression`引数(既定`False`)経由でのみ有効化され、`run_theme()`/`er006_pool_pilot_01_writer.run_writer_for_theme()`のいずれもこの引数を`True`で渡していないため、**No.9を含む現行Production Writer呼び出しでは一切使われていない**。ただし、これは単純な実装漏れではない: `run_writer_for_theme()`のdocstringに明記されている通り、方式B(EVIDENCE_COMPRESSION_BLOCK)は「ER-008-TTS-FALLBACK-AND-EVIDENCE-COMPRESSION-03で試作、比較の結果不採用」であり、No.7 B1候補での実データ比較で、出典名・数字を削った結果、元のcorrelational evidenceより踏み込んだ因果的表現が新規混入するdriftが実際に発生したため、方式C(Evidence Compression Editor、現行採用)がユーザーによって正式に選ばれた経緯がある。つまり、「Pointの数字連続を直接防ぐ既存の強い指示」は存在するが、それは過去にFact safety上のリスク(causal drift)を理由に明示的に不採用とされたコードパスの中にある。
- **Writer側Numeric Compression実効性**: `PARTIALLY_EFFECTIVE`。Ledgerの元データ(7値)から5値まで絞る選別は行われている(完全な無視ではない)。しかし、それら5値が異なる設問・異なる意味を持つ数字である場合の追加圧縮(自然な言葉への統合)は、現在の一文の指示範囲外であり機能しない。
- **Evidence Compression Editor側Numeric Compression実効性**: `NOT_TRIGGERED`(対象外と判定、pre/post diffで数字は不変)。Editor自身の「近似・重複する数字」という定義に照らせば、この非発火は仕様通りの動作であり、Editorの不具合ではない。
- **Storytelling FirstのPoint実効性**: `PARTIALLY_EFFECTIVE`。Main Story・Point One(guilt tipping・心理的圧力という解釈軸を中心に構成)は物語として機能しており、Storytelling Firstが明示的に禁止する「調査結果を項目的に読み上げるレポート調・survey readout調」には該当しない。一方、**Point Two(A2「The pushback is growing」・B1B「Customers are pushing back」)は、[N%が...と回答した]という文が4つ連続する構成そのものが、Storytelling Firstが名指しで禁止している「survey readout調」の典型例になっている**(締めの1文で軽い解釈を加えるのみ)。Main Story/Point Oneでは機能しているが、Point Two特有の失敗パターンとして正直に記録する。
- **Root Cause分類(複数要因)**: 主として**Case D**(現行のNumeric Compression[Storytelling First一文・Editor定義とも]は「同じtrendの数字」のみを対象とし、Ledgerが異なるFactとして分離した数字は対象外と判定される、Ledgerの実データで確認)。加えて**Case F**(Storytelling FirstがPoint Two特有の「survey readout調」を実際には防げていない、本文実読で確認)。副次的に、より直接的にこの問題を防ぎうる既存の強い指示(EVIDENCE_COMPRESSION_BLOCK)が方式Bとして過去に不採用とされているため単純な**Case A(実装漏れ)とは性質が異なる**ことを明記する(過去のFact safety上の理由による意図的な不採用の裏返しであり、軽々に有効化すべきではない)。
- **最終分類**: **Case 2: SPEC_TOO_WEAK**。現行採用中の仕組み(Storytelling First一文・Evidence Compression Editor)は意図通りに動作しているが、[F-011]/[F-012]/[F-013]のような「異なる意味を持つ複数の数字がPoint内で連続する」パターンを抑えるには対象範囲が狭すぎる。より強い指示(EVIDENCE_COMPRESSION_BLOCK相当)は存在するが、Fact safety上のリスクを理由に過去に不採用とされた経緯があるため、単純にオンへ戻すことは推奨しない。`USER_DECISION_REQUIRED`。
- **今回実施しなかったこと(21節の禁止事項の遵守)**: 新Numeric Compression Prompt・Point専用Prompt・Editor仕様変更・Storytelling First変更・新しい数字上限・No.9再生成・API追加Trial・新Validator追加のいずれも実施していない。EVIDENCE_COMPRESSION_BLOCKの`evidence_compression=True`化も行っていない(方式Bは過去に不採用とされているため、再導入はユーザー判断が必要)。

### E. 今回発見した副次的な技術的負債(Open Item化)

- B1B(ER-010-11版)の`article.md`と、直近の`audit/evidence_compression_editor_raw.json`のraw_textが、コード読解上は一致するはずが実際には大きく異なっていた件(上記D節「データ整合性に関する注記」参照)。原因未特定。Point Overlap Article Retryが発火した記事(Writerが2回呼ばれるケース)特有の可能性があるが、今回のタスク範囲外のため深追いしていない。

### 状態まとめ

- Fact Checker運用変更: `APPROVED_FOR_PRODUCTION`→`PRODUCTION_WIRED`。
- No.9(ER-010-11版)Fact Checker指摘: 全件PASS扱い(non-blocking advisory)。
- OPEN-97: `RESOLVED / CLOSED`。OPEN-99: `RESOLVED / CLOSED`。
- Point Compression診断: `Case 2 SPEC_TOO_WEAK`、`USER_DECISION_REQUIRED`(新Open Itemとして追加、下記OPEN_ITEMS参照)。
- 新規技術的負債(B1B audit trail不整合): 新Open Itemとして追加。

## ER-010-NO9-OPEN100-DEFER-AND-PRODUCTION-AUDIO-13(2026-09-01、OPEN-100のDEFERRED正式記録・OPEN-101音声化前確認・No.9音声生成のSTOP判断)

### A. OPEN-100(Point Two数字羅列問題)のUser Decision

- **User Decision**: OPEN-100を一旦Open Itemとして保留する(`CLOSE`でも`REJECTED`でもなく`DEFERRED / NON-BLOCKING`)。理由: (1)過去にもTrialしており短期に単純解決できる問題ではない、(2)強いNumeric Compression(方式B)は過去にFact Safety上のcausal drift副作用が実証済み、(3)今後導入予定のEditorial Typeで記事構成が多様化し、survey/numeric-heavy記事の比率自体が限定される想定、(4)現時点でNo.9完成・音声化を止めて追加Trialするほどの優先度ではない。
- **実施しなかったこと**: Numeric Compression追加・Point専用Prompt・Storytelling First変更・数字削除・Point書き直しはいずれも行っていない。Fact Checker advisory指摘を理由とした本文修正も行っていない。
- **SSOT反映**: [OPEN_ITEMS.md](OPEN_ITEMS.md)のOPEN-100を`USER_DECISION_REQUIRED`→`DEFERRED / NON-BLOCKING`へ更新。次Actionとして「Editorial Type導入後、実際の発生率を見て再評価する」を明記。

### B. OPEN-101(B1B audit trail不整合)の音声化前確認 — Case B判定

音声生成前に、「どの本文がNo.9 B1Bの正式Production final candidateか」を確定する目的で、Writer output → Evidence Compression Editor output → Local Rewrite → final article artifact → audio generatorが読み込むsource articleの系譜を確認した。

- **確認1(article.mdの書き込みタイミング)**: `er010_output/no9_formatting_production_and_fact_review_11/b1b/`内の各audit fileのmtimeを比較した結果、`article.md`(07:54:41)が`evidence_compression_editor_raw.json`(07:52:25)・`point_overlap_article_retry_log.json`(07:52:25)より約2分16秒遅く書き込まれていた。コード(`er003_v1_n3_01_articles_generate.py`)を再確認したところ、`article.md`への書き込みは`_generate_and_compress_article()`内(Point Overlap Retryループの一部)と、Local Rewrite Loop内(`major_items`が存在する場合のみ)の2箇所のみだが、B1Bの`local_rewrite_cycles.json`/`local_rewrite_results.json`は共に空配列であり、Local Rewrite Loopの本体は実行されていない(記録上MAJOR=0のため)。したがって、このタイムスタンプ差をコード読解のみで説明することはできなかった。
- **確認2(内容の直接照合、今回新規実施)**: `ledger_deviation.json`が記録するMINOR指摘1件の`claim_in_article`("With a cash tip jar, the choice was comparatively private, one researcher argues. ... The researcher calls this "guilt tipping.")と、現在の`article.md`の対応箇所("A cash tip jar was relatively private... One policy brief calls this pressure "guilt tipping.")を字句レベルで直接比較したところ、**一致しなかった**。これは、Hook-aware Ledger Deviation Checkが実際に安全確認を行ったテキストと、現在`article.md`として保存されているテキストが異なる、という直接証拠である。
- **確認3(Production Audio正式入力先の状態、今回新規発見)**: `er009_n1_production_integration_01.py::run_audio_stage()`(No.9のProduction Audio正式driver)が実際に読み込むディレクトリは`er006_output/pool_pilot_01/pool_n9_tip_screens/{a2,b1b}/article.md`であり、ここまで診断してきた`er010_output/no9_formatting_production_and_fact_review_11/`とは**別のディレクトリ**である。実際に中身を確認したところ、このディレクトリのA2/B1B `article.md`は2026-08-29 21:09/21:15時点のもの(タイトル・本文ともER-010-11版と全く異なる、おそらくER-009-N1-PRODUCTION-INTEGRATION-01のBaseline初回生成のまま)であり、ER-010-06版以降の一連の改善(Storytelling First/No Jargon/Formatting禁止/Fact Checker新方針等)が一切反映されていないことが判明した。
- **判定**: 確認2・確認3の両方により、本項目は仕様書のCase A(記録上の問題のみ)ではなく**Case B**(「どの本文が正式final candidateなのか不明、またはaudio generatorが異なる本文を読み込む可能性がある」)に該当すると判定した。B1Bについては、`article.md`の実体自体が安全確認(Ledger Deviation Check)を経たテキストと一致しない可能性が具体的証拠で示されており、かつ、そもそもProduction Audio正式入力先には全く別の旧candidateが置かれたままだったため、**このままaudio generatorを実行すると、今回一連のセッションで安全性・品質を確認してきた本文とは異なる、3日前の旧candidateが音声化されてしまう**リスクが実際に存在した。
- **A2との違い**: A2は同一の確認を行い、Point Overlap Retry自体が発火しておらず(Writer呼び出し1回のみ)、`ledger_deviation.json`の指摘も0件であるため、B1Bのような具体的な不一致の証拠は見つからなかった。ただし、A2についてもProduction Audio正式入力先(`er006_output/pool_pilot_01/pool_n9_tip_screens/a2/article.md`)が同様に2026-08-29時点の旧candidateのままである点は共通の課題として残る。

### C. 音声生成のSTOP判断

- 上記Case B判定により、指示書のSTOP条件A(「OPEN-101確認で、正式final article sourceが一意に確定できない」)に該当すると判断し、**今回はA2/B1いずれについてもProduction Audio生成を実施しなかった**。「勝手に本文を選ばない」という指示に従い、B1Bのどのテキスト(`article.md`実体/`evidence_compression_editor_raw.json`/再生成)を正式candidateとするかも、Production Audio正式入力先(`er006_output/pool_pilot_01/pool_n9_tip_screens/`)へどう反映するかも、Claude Codeの判断では決定・実行していない。
- 新規のNumeric Compression・Point Prompt・Storytelling First変更等は今回も一切実装していない(OPEN-100 DEFERRED方針を遵守)。
- **状態まとめ**: OPEN-100 = `DEFERRED / NON-BLOCKING`。OPEN-101 = `USER_DECISION_REQUIRED`(B1B音声生成のみBlocking、A2は非Blocking)。No.9 A2/B1 audio = 今回とも**未生成**(STOP条件A該当のため)。

## ER-010-NO9-ARTICLE-AUDIO-PRODUCTION-WIRING-14(2026-09-01、OPEN-101 Root Cause特定・article/audio SSOT修復・No.9 A2/B1B正式Production Audio Stage実行・新規Audio QA課題[OPEN-102]発見)

### A. OPEN-101 Root Cause調査

前回セッション(ER-010-NO9-OPEN100-DEFER-AND-PRODUCTION-AUDIO-13)は、B1B article.mdとLedger Deviation Check対象本文の不一致(Case B)、およびProduction Audio正式入力先(`er006_output/pool_pilot_01/pool_n9_tip_screens/`)が2026-08-29時点の旧candidateのまま放置されている問題を発見したが、Root Causeの特定までは至らずSTOPしていた。今回、まずコードベース全体を調査しRoot Causeを特定した。

- **調査対象**: `er009_n1_production_integration_01.py`(No.9専用Production driver)、`er006_pool_pilot_01_writer.py`(Writer Stage実装)、`er006_pool_pilot_01_support.py`(Support Stage実装)、`er003_v1_n3_01_articles_generate.py::run_one_pattern()`、`er010_no9_*.py`各diagnostic script(06/09/10/11版)。
- **発見1**: `er009_n1_production_integration_01.py::run_writer_stage_baseline()`は、`er006_pool_pilot_01_writer.run_writer_for_theme(..., OUT_DIR, ...)`を呼び出し、`OUT_DIR = "er006_output/pool_pilot_01/pool_n9_tip_screens"`(正式Production Audio入力先と**同一ディレクトリ**)へ直接`gen.run_one_pattern()`の出力(article.md等)を書き込む設計だった。つまり、Writer StageとAudio Stageは元々**単一の共有ディレクトリ**を介して直結する設計であり、両者の間に別途promotion/copy工程は存在しない(存在しないことが仕様の欠陥ではなく、そもそも設計上不要という前提だった)。
- **発見2**: 一方、ER-010-06〜12の全diagnostic検証scriptは`er010_no9_*.py`という命名規則で、`OUT_DIR = "er010_output/no9_..."`という**意図的に隔離された別ディレクトリ**へ出力していた(`grep`で全4本のOUT_DIR定義を確認、いずれも固有の`er010_output/...`パスで相互にも正式`OUT_DIR`とも重複しない)。これは、Storytelling First・Formatting禁止・Fact Checkerポリシー変更等の実験を、Production正式candidateを壊さずに検証するための、意図的かつ妥当な設計である。
- **結論**: 問題は「promotion処理のバグ」ではなく、**diagnostic検証で確認した改善を、正式pathへ反映する運用そのものが一度も実行されていなかった**ことだった。正式pathは既に存在しており(`run_writer_stage_baseline()`を正式`OUT_DIR`に対して直接実行するだけ)、新規のpromotion機構を実装する必要はない。B1B特有のarticle.md/Ledger本文不一致(前回発見のCase B)も、この「正式pathが一度も実行されていない」状態が続く中でdiagnostic版のみを繰り返し実行・上書きしていたことに起因すると考えられる(diagnostic版内での厳密な原因特定は前回セッションの通り未確定のまま残るが、今回の対応=正式pathでの単一実行によって実務上解消する)。

### B. 修復実施(article側)

Root Cause A.の結論に基づき、以下を**コード変更なし**で実施した。

1. `run_writer_stage_baseline()`と同一の呼び出し(`gen.run_one_pattern()`、prompt/instruction無変更)を、正式`OUT_DIR`に対してB1B・A2それぞれ個別に実行した(それぞれ単一の連続実行、既存の複数回再利用は行っていない)。
   - B1B: 実行時間383.2秒。Ledger Deviation Check初回でMAJOR 1件検出→Local Rewrite cycle 1で解消、再チェックMAJOR=0(`LEDGER_COMPLIANT`)。Fact Checker verdict=`REVIEW_REQUIRED`(non-blocking advisory、OPEN-97方針通り)。Directional Fact Precheck=`DIRECTION_REVIEW_REQUIRED`(non-blocking、`POTENTIAL_DIRECTION_REVERSAL`ではない)。status=`OK`。
   - A2: 実行時間471.1秒。Ledger Deviation Check初回でMAJOR 2件検出→Local Rewrite cycle 1で両方解消、MAJOR=0。Fact Checker verdict=`REVIEW_REQUIRED`。Directional Fact Precheck=`DIRECTION_REVIEW_REQUIRED`。status=`OK`。
   - 両article.mdを目視確認し、emoji=0・太字Markdown(`**`)=0(OPEN-99方針通り)、Structure(Title/Main Story/Point One/Point Two/In One Line)すべて存在を確認。
2. `run_support_stage_baseline()`相当(`sc.run_key_phrases`/`run_b1_scaffold`/`run_a2_scaffold`、コード変更なし)を実行し、新article.mdからparts.json・Preview/Comment1-4・Key Phrasesを再導出した。
   - B1B Key Phrase選定が初回`KEY_WORDS_STRUCTURE_INVALID`(item_reasons: "source_spanがsource_sentence内に存在しない")となり、`run_key_phrases()`の設計上canonicalization工程がskipされた(`keywords_canonicalized.json`が未更新のまま旧版が残るリスク)。これはコード上`max_attempts=1`(リトライ機構なし)の一時的な構造検証不一致と判断し、**同一の`run_key_phrases()`をコード・prompt変更なしで1回だけ再実行**したところ、`KEY_WORDS_STRUCTURE_PASS`→`CANONICALIZATION_PASS`となり解消した(`keywords_canonicalized.json`更新済み)。
   - A2のSupport Fact Check(Web検索なし、Article/Ledger突き合わせのみ)がverdict=`MINOR_FIX`(comment_3の可視性表現がやや広い言い換え、severity=MINOR)を1件報告。MINOR_FIXはrun_support_for_theme()の実装上blocking判定には使われておらず、advisoryとして記録するに留めた(article/support本文は変更していない)。
3. **Source一致の機械確認**: `article.md`から`sc.split_article_text()`で独立に再導出したtitle/part1/part2/point_one_heading/point_one_body/point_two_heading/point_two_body/in_one_lineの正規化(空白畳み込み)SHA256[:16]ハッシュと、実際に保存されている`parts.json`(Audio Stageの実際の入力ファイル)の対応ハッシュを突き合わせた。**A2/B1Bとも全8項目で完全一致**を確認し、`er006_output/pool_pilot_01/pool_n9_tip_screens/audio_source_consistency_check.json`へ記録した。

以上により、OPEN-101が懸念していた「article lineageの一意性」「Production保存先とAudio inputの一致」は解消したと判断し、OPEN_ITEMS.mdでOPEN-101を`RESOLVED/CLOSED`(lineage整合性の論点について)とした。

### C. No.9 正式Production Audio Stage実行結果

`er009_n1_production_integration_01.py::run_audio_stage()`(No.9専用、Standard同期TTSモード、Production Batch経路は不使用というユーザー既定指示に従う)を正式`OUT_DIR`に対して実行した。

- B1B: TTS 13segment中12 `OK`、`point_two`のみ`STOPPED`。Key Phrase 5件は英語Component・日本語meaning含め全て`OK`。
- A2: TTS 14segment中13 `OK`、`point_two`のみ`STOPPED`。Key Phrase 5件中4件`OK`、Key Phrase 2("default")の英語Componentのみ`STOPPED`(日本語meaningは`OK`)。
- `point_two`の`STOPPED`理由(`review_lock_state.json`より): 3回の試行(`cumulative_tts_attempts=3`、既存の`PRODUCTION_MAX_TTS_ATTEMPTS=3`上限)とも`classification=TRUE_CONTENT_MISMATCH`。実際のASR文字起こし全文をcanonical本文と直接比較したところ、事実内容・数値(78%/44%/66%/59%/36%)は意味的にほぼ完全に一致しており、相違は主に数字の表記ゆれ(canonical側"Seventy-eight percent"等の綴り数字 vs ASR側"78%"等の digit-percent表記)と文境界付近の軽微な言い換えに限られていた。既存のTTS/ASR共通部品には数字表記ゆれ吸収機構があるとCURRENT_SPEC.mdに記載されているが、本segment(複数の数字を含む長文News本文)では吸収しきれず`TRUE_CONTENT_MISMATCH`に分類された可能性がある(Validator側の改善要否は新しい仕様判断であり、今回のスコープでは実施していない)。
- A2 Key Phrase 2("default")の`STOPPED`理由: 3回とも生成音声長(10.77秒/13.93秒/9.09秒)がテキスト量からの想定範囲(5.50秒)を大きく超え、TTSモデルが指示文パラフレーズ/無関係内容を生成した疑いによりASRへ送らず破棄(duration anomaly検知、既存の安全機構が正しく動作)。
- **Audio Validation Gate**(`er003_v1_n3_01_assemble.py::verify_episode_audio_validation_gate()`、ER-008-AUDIO-VALIDATION-GATE-AND-EVIDENCE-MAJOR-AUDIT-05)が、B1のepisode assembly実行時に`point_two=STOPPED`を検知し、`RuntimeError: EPISODE_BLOCKED_BY_AUDIO_VALIDATION`で処理を中止した。これは「検証・stale・STOPPEDの音声をそのまま完成扱いにしない」という既存のfail-closed仕様通りの正常動作である。A2のassemblyはB1側で例外発生により未実行(A2も同一の`point_two=STOPPED`状態のため、実行すれば同じGateでblockされる可能性が高いが未検証)。
- 既存仕様`PRODUCTION_MAX_TTS_ATTEMPTS=3`(ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15、ユーザー正式決定、「4回目以降は絶対にTTS生成しない」)を尊重し、4回目の自動再試行は一切実施していない。

### D. STOP判断とOPEN-102新規追加

上記Cの結果は、指示書のSTOP D(「Audio QAでblocking failure」)に該当すると判断した。既存のHuman Review機構が対象segmentを正しく`HUMAN_REVIEW_REQUIRED`として記録しており、これはユーザーによる試聴・承認を経るべき既存の正常フローであるため、Claude Code側で(a) 4回目のTTS再試行、(b) Validatorの数字表記ゆれ吸収ロジックの変更、(c) 該当segmentを検証未了のまま完成扱いにする、のいずれも行っていない。この新規事項をOPEN_ITEMS.mdへ**OPEN-102**として新規追加した(Blocking: A2/B1双方のepisode assembly完成のみ。記事側・Support側・その他segmentは全てOK)。

### E. 状態まとめ

- OPEN-100 = `DEFERRED / NON-BLOCKING`(変更なし)。
- OPEN-101 = `RESOLVED / CLOSED`(article/audio lineage整合性の論点について、2026-09-01)。
- OPEN-102 = `USER_DECISION_REQUIRED`(2026-09-01新規、A2/B1双方のepisode assembly完成のみBlocking)。
- No.9 A2/B1B article = Production正式candidateとして確定(Ledger MAJOR=0・Fact Checker FAILなし・Formatting適合・Point Overlap PASS)。
- No.9 A2/B1B audio = TTS大部分完了・`point_two`(両level)と A2 Key Phrase 2のみHuman Review待ちのため、**完成episode(assembled)は今回とも未生成**。

## ER-010-NO9-AUDIO-VALIDATOR-NORMALIZATION-DIAGNOSTIC-15(2026-09-01、OPEN-102の真のRoot Cause特定[Case C: NORMALIZER_BUG]・前回報告の訂正)

### A. 目的・スコープ

前回(ER-010-NO9-ARTICLE-AUDIO-PRODUCTION-WIRING-14)は、No.9 A2/B1B `point_two`のTTS/ASR検証失敗の主因を「canonical側の綴り数字("Seventy-eight percent"等)とASR側の数字表記("78%"等)の表記ゆれ」と推定して報告した。今回はこの推定を検証するため、新規Validator仕様の追加・再生成は一切行わず、既存Validator実装の実際の挙動をコード上・実データ上の両面から確認する**診断専用タスク**として実施した(Production code変更なし)。

### B. 既存Validator実装の実態(2種類存在、混同注意)

コードベースには数字/percent正規化を含むASR比較ロジックが**2種類**存在することを確認した。

1. `er003_audio_tts_asr_safety.py::validate_asr_match()` — 英国/米国綴り差と2〜12の単語→算用数字のみを吸収する簡易版。**No.9のNews本文系(point_two含む)Production経路からは呼ばれていない**(grepで呼び出し元を確認、日本語短文検証等の別用途でのみ使用)。
2. `er006_preprod_hardening_01_validation.py::classify_asr_match()` — 数字(cardinal/ordinal/複合序数)・パーセント(`percent`/`per cent`/`%`)・通貨・小数点・指数表記・英米綴り差・複合語分かち書き・冠詞差・stopword等を正規化した上で、6分類(`EXACT_MATCH`/`NORMALIZED_MATCH`/`HIGH_SIMILARITY_SAFE`/`ASR_VALIDATION_UNCERTAIN`/`TRUE_CONTENT_MISMATCH`/`TTS_FAILURE`)へ振り分ける本格版。**こちらがNo.9のPoint本文・Full Story等、News本文系Production経路で実際に使われているValidator**である。

`classify_asr_match()`の`normalize_numeric()`(318〜368行)には、パーセント記号とpercentの同値化が明示的に実装されている:
```python
t = re.sub(r"\b(\d+(?:xdecimalpointx\d+)?)\s*(?:percent|per cent)\b", r"\1xpercentx", t)
t = re.sub(r"(\d+(?:xdecimalpointx\d+)?)\s*%", r"\1xpercentx", t)
```
また綴り数字→算用数字変換(`_convert_cardinal_words()`)は2〜19だけでなく、tens(twenty〜ninety)・hundred/thousand/millionを含む任意の桁の綴り数字列を対象にしており、ハイフン複合語("seventy-eight"等)も冒頭でハイフンをスペースへ変換してから処理するため対応できる設計だった。既存test(`er006_preprod_hardening_01_validation_test.py`)にも`"percent 28% <-> twenty-eight percent"`という直接該当するテストケースが存在し、実装意図通りに動作することを確認した。

### C. Production配線の確認(実行経路の追跡)

`er003_v1_n3_01_tts_generate.py`が`er006_preprod_hardening_01_validation`を`en_validator`としてimportしており(45行)、No.9の`generate_a2_segments()`/`generate_b1_segments()`のPoint本文系処理から、以下の経路で`classify_asr_match()`へ到達することを確認した(A2/B1とも同一Validator、retryごとに同一関数を再利用、`point_two`専用の特別pathは存在しない・他のNews本文segment[point_one/full_story_part1/2/in_one_line]と共通処理):

```
parts.json["point_two_body"](canonical)
  → tts_safe_news_en()  ※TTS入力構築とASR比較基準textの両方を兼ねる
  → TTS生成
  → ASR(routing.transcribe)
  → secondary_asr.evaluate_attempt_with_cascade() 内部で classify_asr_match(canonical=tts_safe_news_en適用後text, asr_text)
  → PASS/STOPPED判定
```

### D. 実データでの検証(read-onlyローカル診断、新規API呼び出しなし)

`review_lock_state.json`に記録された実ASR文字起こし(A2/B1B `point_two`各3attempts)と、実際にParts.jsonから`tts_safe_news_en()`を通した後のcanonical textを、`classify_asr_match()`へそのまま渡して再現した。

**発見(重要・前回報告を覆す)**: `tts_safe_news_en()`が内部で呼ぶ`tts_safe_number_words_en()`(`er003_v1_n3_01_tts_generate.py` 502〜513行、"two"〜"twelve"の綴り数字を算用数字へ変換するTTS入力安全化関数)の正規表現`\b(two|three|...|twelve)\b`が、ハイフン複合語の**後半だけ**に誤ってマッチしていた。ハイフンは`\b`(単語境界)として扱われるため、"Forty-**four**"の"four"、"Seventy-**eight**"の"eight"、"Thirty-**six**"の"six"がそれぞれ単独の数字語として誤検出され、算用数字へ部分変換されてしまう:

| 入力 | `tts_safe_number_words_en()`出力(バグ) |
|---|---|
| `Forty-four` | `Forty-4` |
| `Seventy-eight` | `Seventy-8` |
| `Thirty-six` | `Thirty-6` |
| `Twenty-two`/`Fifty-five`/`Eighty-eight`等も同様 | 同様に後半のみ数字化 |
| `Twenty-one`/`Ninety-one`("one"は対象外) | 影響なし |

この壊れた文字列(`Forty-4 percent`等)が、TTS入力・ASR比較基準textの**両方**として使われる。ASR比較の実行結果:

- **A2 `point_two`(3 attempts共通)**: `content_word_diffs = [{"canonical": "forty 4xpercentx", "asr": "44xpercentx", "entity_like": False}]`。canonical側は"Forty-4 percent"→正規化で"40"と"4xpercentx"という**無関係な2 token**に分裂する一方、ASR側"44%"は正しく"44xpercentx"の1 tokenになるため、突き合わせ不能。→ `TRUE_CONTENT_MISMATCH`(ratio=0.9838)。
- **B1B `point_two`(3 attempts共通)**: 同様の分裂が"Seventy-8"→`seventy 8xpercentx`と"Thirty-6"→`thirty 6xpercentx`の2箇所で発生(canonical側は"Seventy-eight"/"Thirty-six"の両方が対象)。加えて`US`(canonical)と`U.S.`(ASR句読点あり)のtoken数差も検出されたが、これは固有名詞的表記としてentity_like=Trueに分類され単独では非blocking。→ `TRUE_CONTENT_MISMATCH`(ratio=0.9204)。
- **66%/59%(A2/B1B共通)は正しく吸収されていた**(canonicalが元々算用数字"66 percent"/"59 percent"のため、上記バグの影響を受けない)。**percent記号自体の同値化ロジックはA2/B1いずれの箇所でも一度も破綻していない**ことを確認した。

### E. Root Cause分類

**Case C: NORMALIZER_BUG** — ただし、バグの所在は「ASR Validator本体(`classify_asr_match`/`normalize_numeric`)」ではなく、その**手前でcanonical textを構築するTTS入力安全化関数`tts_safe_number_words_en()`**(同じ`er003_v1_n3_01_tts_generate.py`内、Production配線済み・全News本文segmentで共通使用)である。ASR Validator自体の数字/percent正規化ロジックは実装・配線とも意図通り正しく動作していることをB節のtest・C/D節の実データ双方で確認した。バグの影響範囲は「十の位の単語+一の位が2,3,4,6,7,8,9のいずれかである綴りハイフン複合数(21〜99のうち約8割)がTTS入力/ASR比較対象textに含まれる場合」全般に及ぶ(No.9固有ではない、既存の潜在バグ)。既存test(`er003_test_v1_n3_01_tts_generate.py`)には`first_words()`のハイフン複合語対策テストはあるが、`tts_safe_number_words_en()`自体のハイフン複合語ケースを検証するテストは存在しなかった(カバレッジの欠落)。

### F. 前回報告(ER-010-NO9-ARTICLE-AUDIO-PRODUCTION-WIRING-14)の検証結果

**誤っていた**。前回は「canonical側の綴り数字とASR側のdigit-percent表記の差が主因」と報告したが、今回の実データ検証により、percent記号とpercentの同値化・綴り数字と算用数字の同値化は**いずれも既存Validatorで正しく吸収されており**、実際の主因は無関係な別バグ(`tts_safe_number_words_en()`のハイフン複合語誤変換によるcanonical text自体の破損)だったと判明した。前回報告は表面的な観察(ASR文字起こしが"78%"のようなdigit-percent表記だった)からの推定であり、実際にnormalizer関数を実行して確認する検証を行っていなかったため誤った結論に至った。

### G. Key Phrase "default"(A2 kp2_en)音声長異常の切り分け

`point_two`とは無関係な別事象であることを確認した。`used_form="default"`(1単語)に対し、`detect_duration_anomaly()`の想定上限は`1語×1.5秒+4.0秒=5.50秒`。実際の生成音声長は3回とも10.77秒/13.93秒/9.09秒(想定上限の1.7〜2.5倍)で、いずれもduration anomaly検知によりASRへ送る前に破棄されている(3回ともASR自体は未実行、`cumulative_asr_calls=0`)。これはCURRENT_SPEC.mdに記載済みの既知のTTS instruction-paraphrase/hallucination失敗モード(短い1語Key Phraseで発生しやすい)に該当すると判断する。既存のduration anomaly検知機構は設計通り正しく動作しており、Validator側の不具合ではない。新しいKey Phrase仕様の追加は行っていない(今回のスコープ外)。

### H. OPEN-102更新・状態まとめ

- OPEN-102のRoot Causeを、前回の「数字表記ゆれの吸収漏れ(推定)」から、**「`tts_safe_number_words_en()`のハイフン複合語誤変換によるcanonical text破損(Case C、確認済み)」**へ訂正した。
- 実際のASR文字起こし(3 attempts共通、A2/B1Bとも)は、数値・内容とも正規canonical textと完全に一致する内容を発話していると強く推定される(TTS自体が誤読している証拠はない。ASR側は"78%""44%"等、正しい数値を一貫して書き起こしている)。**音声そのものは正しい可能性が高いが、比較対象のcanonical textが壊れていたために誤ってfail-closedになった、false negativeの疑いが強い**。
- ただし今回はProduction code変更禁止(診断専用)のため、`tts_safe_number_words_en()`の修正は実施していない。修正は新しいUser Decisionが必要(STOP G相当)。
- OPEN-100 = `DEFERRED / NON-BLOCKING`(変更なし)。OPEN-101 = `RESOLVED / CLOSED`(変更なし、再openすべき新規lineage不整合は発見していない)。OPEN-102 = `USER_DECISION_REQUIRED`のまま(Root Cause欄のみ更新)。
- A2/B1のepisode assembly・完成試聴は今回も未実施(診断のみのため)。

## ER-010-NO9-TTS-NUMBER-WORDS-BUGFIX-AND-AUDIO-RETRY-16(2026-09-01、`tts_safe_number_words_en()`のRoot Cause修正・Production Audio再実行・No.9 B1完成)

前task(ER-010-NO9-AUDIO-VALIDATOR-NORMALIZATION-DIAGNOSTIC-15)で特定したOPEN-102の真因(`tts_safe_number_words_en()`のハイフン複合数バグ、Case C: NORMALIZER_BUG)を、ユーザーが正式に修正承認。診断のみだった前taskと異なり、本taskはコード修正・回帰test・Production runtime再実行までを正式に実施する。

### A. Root Cause(コードレベル最終確認)

`er003_v1_n3_01_tts_generate.py`の`_EN_NUMBER_WORD_RE = re.compile(r"\b(two|three|...|twelve)\b", re.IGNORECASE)`が原因。正規表現の`\b`(単語境界)は「英数字/アンダースコア」と「それ以外」の間で成立し、ハイフン`-`は「それ以外」に分類されるため、`\b`はハイフンの両側でも成立してしまう。したがって"Forty-four"内の"four"は("Forty"に続く独立した語ではなく複合数の後半であるにもかかわらず)独立した数字語として`\bfour\b`にマッチし、"4"へ変換されていた("Forty"は辞書に無いため無変換のまま)。結果「前半は綴り・後半は算用数字」という壊れた表記("Forty-4")が生成され、この壊れたtextがTTS入力・ASR比較基準text(canonical_text)の両方に使われていた(`tts_safe_news_en()`経由)。percentが後続する場合も同じ壊れ方をする("Forty-four percent"→"Forty-4 percent")。大文字小文字は`re.IGNORECASE`によりどちらでも同じく誤変換される。単独数字語の変換自体・複合数を含まない文への影響は無い。

### B. 修正内容

正規表現に否定後読み`(?<!-)`を追加: `r"(?<!-)\b(two|...|twelve)\b"`。直前の文字がハイフンである場合はマッチ対象から除外する。これにより、ハイフン複合数の後半語("Forty-four"の"four"等)は変換されず、複合数全体が綴りのまま保持される。独立した数字語(文頭・スペース区切り等、直前がハイフンでない場合)は従来通り変換される。

### C. hardcodeでないことの証拠

3語("Forty-four"/"Seventy-eight"/"Thirty-six")を個別に特殊対応するのではなく、汎用の否定後読みルールとして実装した。`twenty-one`〜`ninety-nine`まで、十の位×一の位(2,3,4,6,7,8,9)の全組み合わせパターンで意図通り無変換のままであることをtestで確認済み(D節)。既存の正しい単独数字変換(two〜twelve単体)・序数・小数・通貨・句読点は無変更(非回帰、D節)。

### D. Regression Test(`er003_test_v1_n3_01_tts_generate.py`、新規16 test、全PASS)

`HyphenCompoundNumberWordsRegressionTests`(9 test): 複合数9パターン(twenty-one〜ninety-nine)の無変換確認、percent付き複合数(`Forty-four percent`/`forty-four%`等)の無変換確認、既存digit percent表記(`44%`/`44 percent`)への非影響確認、No.9実例に基づく文脈fixture3件の非破損確認、既存の単独数字変換(two〜twelve)の維持確認、序数・小数・通貨・句読点への非回帰確認。
`ProductionValidatorIntegrationAfterHyphenFixTests`(3 test): 修正後の`tts_safe_news_en()`出力を実Production ASR Validator(`er006_preprod_hardening_01_validation.classify_asr_match`)へ実際に通し、"Forty-four percent"⇔ASR"44%"、"seventy-eight percent"⇔ASR"78 percent"、"thirty-six percent"⇔ASR"36%"がいずれも`NORMALIZED_MATCH`/`EXACT_MATCH`/`HIGH_SIMILARITY_SAFE`のいずれかへ分類されることを確認(修正前は`TRUE_CONTENT_MISMATCH`だった組み合わせ)。

既存Validator自身のtest(`er006_preprod_hardening_01_validation_test.py`、57 fixture、POSITIVE/AMBIGUOUS/NEGATIVE全区分)も全PASSを再確認し、本修正によるValidator側への非回帰(STOP C非該当)を確認した。

### E. Production Validator Integration確認(D節参照)

D節の`ProductionValidatorIntegrationAfterHyphenFixTests`により、修正後のcanonical textが実Validatorで正しくASRのdigit-percent表記と一致することを確認済み。

### F. Production Audio再実行(`er009_n1_production_integration_01.py audio`、正式`run_audio_stage()`実行)

記事本文(`{a2,b1b}/parts.json`)は再生成せず、確定済みのProduction final articleをそのまま使用。既存のretry上限(`PRODUCTION_MAX_TTS_ATTEMPTS=3`)・Audio Validation Gate・review_lock機構は無変更のまま、修正後コードで正式Audio Stageを実行した。

**A2 `point_two`**: 1回目の試行で`status=OK`、`audio_classification=NORMALIZED_MATCH`、`verified=true`。ASR文字起こし: `"...78% of respondents...44% said...66% in September 2025 to 59% in 2026...36% said..."`(数値・内容とも正規canonicalと一致)。`cumulative_tts_attempts=1`、`cumulative_asr_calls=1`(修正前は3回とも`STOPPED`)。

**B1B `point_two`**: 同じく1回目の試行で`status=OK`、`audio_classification=NORMALIZED_MATCH`、`verified=true`。ASR文字起こし: `"...78% called tipping ridiculous, and 44%...66% in September 2025 to 59% in 2026. 36% chose..."`。`cumulative_tts_attempts=1`、`cumulative_asr_calls=1`。

いずれも「壊れた"Forty-4"/"Seventy-8"/"Thirty-6"のようなtext」は一切生成されていないことを`review_lock_state.json`の実データで確認した(修正前診断で予測した「TTS音声自体は正しい可能性が高い」というfalse negative仮説が実証された形)。

**B1B episode assembly**: `status=OK`、`duration_seconds=335.754`、`clipping_detected=False`。B1Bの全23 segmentが`review_lock_state.json`上ですべて`RESOLVED`となり、**No.9 B1は完成**した。

**A2 episode assembly**: `RuntimeError: EPISODE_BLOCKED_BY_AUDIO_VALIDATION`(`kp2_english=UNVALIDATED`、`kp4_japanese_meaning=STOPPED`)により中止。詳細はG節。`point_two`自体は上記の通りPASS済みであり、この中止は`point_two`とは無関係な別の2件が原因。

### G. A2で新たに判明した2件のBlocker(`point_two`・数字表記とは無関係、原因調査は未実施)

**(1) Key Phrase 2("default")英語Component、`kp2_en`**: 今回のAudio Stage実行では**新規TTS/ASR呼び出しが一切発生しなかった**(`review_lock`が`HUMAN_REVIEW_LOCKED`として0 API callでブロック)。理由: このsegmentのcanonical text("default"のtts-safe変換後text)はハイフン複合数を含まず今回の修正で一切変化しないため、SHA256ハッシュが本日午前の実行時に記録された`STOPPED`ロックのハッシュと一致し続け、`review_lock`の設計通り「同一textへの機械的な再挑戦」として正しくブロックされた(既存仕様通りの正常動作、4回目の自動再試行防止が意図通り機能している)。ロックされている過去の記録は、生成音声長10.77秒/13.93秒/9.09秒(想定上限5.50秒を大幅超過)によるduration anomaly検知3連続。**今回の修正でこの現象が解消するかどうかは、ロックのため実際には検証できていない**。

**(2) Key Phrase 4日本語meaning、`meaning_4`("a catch"の日本語gloss「落とし穴、ただし書き」)**: 今回**新規に6回試行し、6回とも`status=OK`(TTS生成は成功)だが`audio_classification=TRUE_CONTENT_MISMATCH`でASR検証不合格**(累積では本日午前の3回を含め計9回)。ASR文字起こしは一貫して「おとしあな ただしがき」(1回のみ「お年やな、ただしがき」)であり、これはcanonical「落とし穴、ただし書き」の読みとして一致しているように見えるにもかかわらずcontent mismatch判定となっている。`generate_a2_japanese_with_reading_safety`(reading-safety機構)が本来この種の表記ゆれを吸収する設計だが、本事例では吸収できていない可能性がある。**これは`point_two`・数字表記normalizationとは完全に無関係な、今回のAudio Stage再実行で偶然新たに発覚した別の問題**である。本taskの承認範囲は`tts_safe_number_words_en()`のbug fixに限定されており、この新規問題の原因調査・Prompt変更は一切行っていない(STOP G相当、新しいUser Decisionが必要と判断し報告のみに留める)。

### H. OPEN-102/103/104更新・状態まとめ

- **OPEN-102は`RESOLVED/CLOSED`とした**(`point_two`のNORMALIZER_BUGという当初スコープについて)。Root Cause修正・回帰test・Production runtime実証(A2/B1双方の`point_two`が1回目試行でPASS)まで確認できたため。
- B1は`point_two`修正によりepisode assemblyまで成功し、**No.9 B1は完成**した。
- A2は`point_two`自体は解決したが、無関係な新規2件(上記G節)によりepisode assemblyが引き続きblockedのため、**OPEN-103(Key Phrase 2 duration anomaly、再検証未了)・OPEN-104(Key Phrase 4日本語meaning、新規発見)として分離・新規追加**した。いずれも`USER_DECISION_REQUIRED`。
- OPEN-100 = `DEFERRED / NON-BLOCKING`(変更なし)。OPEN-101 = `RESOLVED / CLOSED`(変更なし、再openすべき新規lineage不整合は発見していない)。
- Production code変更は`tts_safe_number_words_en()`の正規表現1箇所のみ(ユーザー承認範囲内)。OPEN-103/OPEN-104に対する追加のコード変更・Prompt変更・原因調査は一切行っていない。
- CURRENT_SPEC.mdは変更していない(`tts_safe_number_words_en()`の仕様[綴りの小さな数を算用数字へ変換]自体は変わっておらず、実装バグの修正のみのため新規spec化は不要と判断)。

## 参照元

[PROJECT_INDEX.md](PROJECT_INDEX.md)、[CURRENT_SPEC.md](CURRENT_SPEC.md)、
[HISTORY_INDEX.md](HISTORY_INDEX.md)、[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)

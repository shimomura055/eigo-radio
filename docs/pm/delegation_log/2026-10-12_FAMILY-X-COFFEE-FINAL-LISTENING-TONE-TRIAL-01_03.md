# FAMILY-X-COFFEE-FINAL-LISTENING-TONE-TRIAL-01 委任_03(2026-10-12、Final Listening Phase)
範囲: ユーザー選択Style反映のCoffee Standard/Advanced最終試聴版の作成・異音確認・SSOT記録・STOP。Trial限定、Production(共通Prompt・Master Store・manifest・telemetry・CURRENT_SPEC)変更なし、共通Styleは`APPROVED_FOR_PRODUCTION`にしていない。詳細証跡: `er057_output/coffee_final_listening_tone_trial_01/part_final/`。

## (1) 試聴URL
- 両Level一覧: https://shimomura055.github.io/eigo-radio/user_test/coffee_tone_trial_01/final_v2/index.html
- Standard単独: https://shimomura055.github.io/eigo-radio/user_test/coffee_tone_trial_01/final_v2/standard/index.html
- Advanced単独: https://shimomura055.github.io/eigo-radio/user_test/coffee_tone_trial_01/final_v2/advanced/index.html

## (2) 選択Styleの適用証拠(`STYLE_APPLICATION_EVIDENCE_03.md`)
最終版に使った各wavのsha256が、生成時記録(01A/01B/03のログ)と全項目一致、Full StoryはF5 style sha256(先頭12桁 9228209bec75)一致。要約: Welcome=A5(Charon、Std/Adv共通)、Preview intro=B5(同)、Advanced Preview=E1(Charon)、KP英語=K2(Aoede、Standard5件)、KP日本語意味=M2(Std5件)、Std Preview・Comment1〜4=P2(Aoede)、Full Story=F5(Aoede、両Level。Stdは+6%減速)。model_version: 01A(A5/B5/E1)と03(F5/topic)は応答`gemini-3.8-flash-lite-tts`を実測。01B(K2/M2/P2)は応答model_versionを記録していない(要求modelのみ)。
**前提差(要判断、OPEN-280)**: StandardとAdvancedでKey Phraseが異なる(Std: raw bean/push prices up/take time/right away/on a regular basis、Adv: lag/price tag/show up/come down/come with)。K2×5はStandard分のみ生成済みのため、**Advanced KP英語はK2未適用(既存承認音声)**。適用には新規TTS 5 call(約JPY0.3)が必要で、指示範囲外のため未実施。

## (3) 再生成/再利用segment一覧(`SEGMENT_PROVENANCE_03.md`、全role×由来sha)
- 再生成(R): Std full_story_part1/2/3(F5+6%減速、sha 先頭12は provenance参照)、Adv full_story_part1/2/3(F5)、Std topic_intro(異音STD-24対処、既存承認Style・原稿無変更で1回)。全6 Full Story segmentは初回でPrimary ASR合格、**同一Prompt再生成0回**。
- 再利用(T): Welcome=A5、Preview intro=B5(両Level)、Adv Preview=E1、Std KP英語K2×5、KP日本語意味M2×5、Std Preview+Comment1〜4=P2。
- 再利用(P、既存承認音声、変更なし): topic_intro(Adv)、japanese_title、in_one_line(Std/Adv)、Adv Comment1〜4(E2_UPBEAT)、Adv KP英語(K2未適用)+KP英語解説、shell(key_phrases_intro/num_one〜five/full_story_intro)、固定音源。集計(role数): Std R4/T17/P9、Adv R3/T3/P23。
- 内容QA(Primary ASR gpt-4o-mini-transcribe+既存validator `val.evaluate_attempt`、segment_id=role、長さ条件): std part1/2/3=NORMALIZED_MATCH×3、adv part1/2=NORMALIZED_MATCH、adv part3=HIGH_SIMILARITY_SAFE、topic再生成=NORMALIZED_MATCH。全てlength_ok・verified。

## (4) Standard 6%減速の最終納品音声への適用証拠
`er008_a2_postprocess_slowdown_01.apply_a2_slowdown`(FFmpeg atempo=1/1.06)を、OK判定後のF5音声へ適用。処理前→後(秒): part1 39.28→41.624(比1.0597、+5.97%)、part2 49.63→52.593(1.0597、+5.97%)、part3 39.76→42.142(1.0599、+5.99%)。最終Standard完成版のtimeline上のFull Story Part1/2/3長は 41.62/52.59/42.14秒で上記減速後wavと一致し、provenanceのsha256も減速後wavのshaと一致(最終納品に減速版が使われている)。**旧part2(Attempt 4)のような減速漏れは今回のpart2に無い**。減速後Primary ASR(参考記録): part1・part3=NUMERIC_EQUIVALENCE_MATCH、**part2のみASR_VALIDATION_UNCERTAIN**(entity_only、減速前は同一音声でNORMALIZED_MATCH。OPEN-270と同型の観測で、再生成根拠にせず試聴確認へ回す)。in_one_line(既存)は既に減速済み(再利用)。

## (5) 異音確認結果と残存箇所(`ANOMALY_RECHECK_03.md`)
- ユーザー試聴: FOCUS1=異音あり、FOCUS2=なし、STD-02/20/24=異音あり、STD-06=軽微(許容)、他Std=なし。
- (a)再生成segment(FOCUS1=Std part3、STD-02/20/06=Std part2、FOCUS2=Adv part3)は別takeになり旧take固有のTTS不具合は持ち越されない。検知器は旧FOCUS1を元から検出できないため「検知器が出さない」ことは解消証拠にならない。語位置ベースでは、旧part2の`raw bean(s)`のlocal whisper転写が`robbing(s)`→新`raw`/`bean(s)`(確率0.96〜0.99)に改善、coffee/earlierの窓指標は旧新とも通常範囲。
- (b)再利用segmentのSTD-24(Std topic_intro): 完成版区間は元segmentの線形変換(最大差3.05e-05)でassembled由来ではない→TTS由来→規定どおり既存承認Style・原稿無変更で1回再生成(上限3以内、1 segment)。**新takeにも`Coffee`直前に約80msの深い無音が残る**(旧は約120ms)。解消は試聴判断。旧takeを試聴ページへ併載。
- 新完成版への検知器実行(閾値不変): clip 0/abrupt dropout 0/edge 0、新規medium以上は**Std part3 seg 18.77s(episode 244.03s)の`three`付近click 1件のみ**(自動検知のみを根拠に再生成せず、OPEN-281で試聴確認待ち)。assembled(固定音源除く)はlowのみ(Std 11/Adv 8)。

## (6) 実費・実行時間・QA結果
- 実費: 新規TTS 7 call(F5 6+topic 1、技術失敗retry 0)約JPY6.50(usage実測tokens×Standard単価$0.5/$6.0 per M、USD/JPY160)+Primary ASR推定約JPY2.1(duration/文字数から推定、請求画面未確認)=**約JPY8.6**(上限JPY20内。ASR推定のため確定値でない)。Trial累計(01A 5.16+01B約9.55+03約8.6)約JPY23.3。
- 実行時間: F5 6 segment並列生成+ASR+減速 17.9秒(6並列)。topic再生成約数秒。検知器再実行(local whisper small含む)52秒。
- 最新モデル原則: TTS=`gemini-3.8-flash-lite-tts`(最新世代、現行Production同一固定、例外なし)、ASR=`gpt-4o-mini-transcribe`(Production既存Primary route、ASR_ROUTING固定のため変更せず)。
- Audio QA(`qa_03.json`): Standard 295.555秒/Advanced 288.45秒、wav長=timeline合計(差<0.02秒)、mp3長一致、48kHz stereo、peak 0.9504/0.9594(headroom閾値0.98以内、安全弁未適用)、clipping(|x|>=0.999)0/0、Key Phrase内の1.0秒超の無音はKey Phrase block内の設計済み区間(Production assembleと同一構造)のみ。assembler回帰: 既存音声のみで組立てた結果が既存完成版wavと**byte-identical**(Standard sha 8f085ef4e8a4…、Advanced 4b2a30d7c0fb…、`regression_check_03.json`)。target RMS: Std 0.10621/Adv 0.11604(既存完成版0.09932。素材差による同一式の結果)。
- Playwright(公開Pages、`PLAY_EVIDENCE_03_final_v2.md`): 一覧52/52、Standard27/27、Advanced25/25 audio実再生PASS、ジャンプ全PASS、HTTP>=400 0、console error 0、Gate 7 (a)〜(n)確認。

## (7) Production正式反映前に残る判断事項(全て未実装・未承認)
共通Style(A5/B5/E1/F5/K2/M2/P2)の正式採用可否(人間ユーザーのみ)、Master Store登録、KP発音hint(resolver)付与の要否、Batch・Productionのassemble・Gate・内容QA(Secondary/意味等価)での再生成再検証の要否(OPEN-279)、Advanced KP英語へのK2適用(OPEN-280、約JPY0.3)、残存異音の試聴判断(OPEN-281)、OPEN-270(減速後検証の外側ループ)、OPEN-276(減速漏れ・Gate穴、Production不具合は未修正)、OPEN-278(DEFERRED)。Production差異一覧: `PRODUCTION_DIFF_03.md`。

## (8) 禁止遵守自己申告
git add -A/-f、amend、rebase、force push、stash、clean、reset --hard、checkout -f: 不使用(作成/編集ファイルのみ`git add <path>`、fetch→ff-only→push)。Production runner経由生成なし(Trial専用script)、Master Store/manifest/telemetry/human_review_queue/attempt_history/ledger書込なし(sha256前後一致: `production_sha_before_03.txt`/`production_sha_after_03.txt`)、既存完成音声・worktree変更なし(read-only import、`-B`)、minimal fallback/Local Rewrite/Secondary ASR/Prompt変更なし、再生成上限遵守(Full Story追加再生成0、異音対処1 segment/上限3)、日英ASR統一案・異音検知アルゴリズム追加開発・Validator変更・CURRENT_SPEC編集・共通Style`APPROVED_FOR_PRODUCTION`化・他未決事項への着手なし。**範囲判断**: Advanced KP英語のK2適用は指示範囲外のため実装せずOPEN-280として報告(依頼文の「K2×5は両レベル」前提の訂正)。注意: validatorが失敗時に書くtelemetryはプロセス内でTrial用メモリへ退避(1件=std part2減速後ASR、Production telemetry不変)。ACTIVE_TASK.md先頭を更新(gitignore対象のため非commit)。

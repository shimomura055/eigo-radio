# TRIAL_RESULT_01 (委任_27: 『宅配の再配達は有料にすべきか?』音声化Trial 結果。ユーザー原文§9の7項目)

作成: 2026-10-25。DEV/Trial専用。**`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`ではない**(Y正式Production入口は存在しない=OPEN-484)。管理: commit 803882ded(Phase 1成果物)、c9083894a(Phase 0)。ユーザー原文=docs/pm/delegation_log/2026-10-25_FAMILY-Y-VOICES-DESIGN-01_USER_09.md。

## 0. 要約
- 日本語R0(3 Voice、無変更)にリードとTension+Closingだけ補い、日本語5パート→英訳Adv/Std→Comment1〜3/Preview/Key Phrase→音声(Std・Adv両方の通し)→限定試聴ページまで**完成**。有料launch 4回(再起動0)、実費**33.40円**(案件Cap55円・見積最大40.4円内)、日次831.3円(1,000円内)。
- 音声は全segmentが正式Gate通過(HR Lock 0・局所Rewrite 0・fallback 0・Y style gate PASS・Audio Validation Gate PASS)。再生成はAdv Voice 2の1回のみ(ASRが『wrong→right』の意味反転を検出)。
- **耳による自然さ・過剰演技・ニュースナレーター化・V1/V3の聞き分けの最終判断は未実施**(機械指標のみ。Fable/ユーザー試聴で確認)。

## 1. Standard／Advancedの完成状態と試聴方法
| | Standard | Advanced |
|---|---|---|
| 通し音声 | 342.8秒(約5分43秒)、Y style gate PASS、clipping無し、peak 0.951 | 321.5秒(約5分21秒)、PASS、clipping無し、peak 0.916 |
| 構成 | 5パート(リード/V1/V2/V3/Tension+Closing)+Preview+Comment1〜3+Key Phrase 3+In One Line+日本語タイトル/Comment(Std) | 同(日本語要素なし、英語のみ) |
| 参考 | Std「3人の語りのみ減速なし」版 334.4秒(既存の比較arm、同ページに併置) | — |
- **限定試聴URL(unlisted・noindex。ユーザーのみに提示)**: https://shimomura055.github.io/eigo-radio/user_test/family_y_redelivery_audio_01/index.html
  - Standard/Advancedボタンで切替、通し再生、パート別再生(リード/人物1〜3/まとめ/Preview/Comment/In One Line/Key Phrase)、全スクリプト+各パートの日本語元原稿、3人の人物ラベルと立場要点、冒頭に『Trial・限定試聴・権利確認前のため転載不可』注記。
  - 検査: 公開URL上でHTTP 200、53音声すべて実再生OK・seek OK・console error 0・タブ切替OK・`noindex,nofollow`・外部リンク0(`er110_output/family_y_redelivery_audio_01/play_verify_public.json`)。標準検査PASS(`page_standard_check_tool.json`、`tools/user_test_page_standard_check_01.py`)。どのindex・一覧からもリンクしない。
- ローカル成果物(gitignoreのwav): `C:\Users\tensh\eigo-radio\er110_output\family_y_redelivery_audio_01\audio\r0\a2\assembled\Family_Y_Trial_A2_R0.wav` / `...\b1b\assembled\Family_Y_Trial_B1_R0.wav`(同内容のmp3は`user_test/family_y_redelivery_audio_01/audio/`)。

## 2. 英訳で3人の人物像・主観性が保持されたか
本文全文の対応表=`COMPARISON_01.md`(無編集)。決定論確認(`english_r0/mapping_check.json`): 日本語/Adv/Stdの3言語とも、5段落・順序、段落2〜4の一人称、各人物固有のアンカー語(V1=不在票・送料・料金全体、V2=午前・夫・指定、V3=営業所・ロッカー)、段落1/5が一人称で始まらない、全PASS。
| 人物 | 保持された要素(Adv・Std両方で確認、原文は COMPARISON_01) |
|---|---|
| V1 現役ドライバー(留保型) | 冒頭の「不在票を入れて帰る→少し気持ちが沈む。でも次の家へ向かう」(Adv: `When I leave a delivery notice and head off, I do feel a little down. But then I go on to the next house.`)、葛藤の一か所「それでも…割り切れないんだ」(`Even so, I can't just say customers should pay for them.`)、結びの注文(送料の見直し・運ぶ人に回る)。Stdは文を短く分けつつ`They really are hard on us.`/`I want the money to really go to the people delivering the packages.`を保持 |
| V2 共働きの受取人 | 具体的な出来事1つ(午前指定で来ず、戻ると不在票)、配達員への配慮と引っかかり、結びの問い返し(`Am I wrong to feel that way?`、Adv・Stdとも)。在宅中の不在票を自分の出来事にしていない |
| V3 受取方法を工夫する受取人 | 経験(ロッカー不可・営業所経由の遅れ)→不公平感→賛成→段階案(最初は無料)→引け目(`Maybe that's only my view, though, because the delivery office is nearby…`) |
- 機械指標(`en_monitors.json`、記録のみ): 一人称語数 Adv 8/12/14、Std 9/13/14(3人とも保持)。Stdの方が1文が短い(1文あたり一人称: V1 0.82、V2 0.93、V3 1.17 / Adv 1.14/1.33/2.0)が、人物の疑問符・ヘッジ・葛藤文は残っている。Std 646語・Adv 647語でほぼ同量(人物の個性・意見を削る方向の短縮はなし)。
- 新しい事実・主張・経験の追加: 目視ではなし(KPの`short-staffed`は本文語)。英語Ledgerは『事実台帳なし』を明示し、IOLも事実主張を追加していない(In One Lineは「誰が払うかで意見が分かれる」の要約)。監視Leakage(S3、記録のみ)はAdv・Stdとも指摘0。
- 人物像・主観性の最終的な判定(自然さ・個性の濃さ)は**Fable/ユーザーの読解・試聴**に委ねる(私は機械確認と原文提示まで)。

## 3. Voiceの聞き分けと音声品質
- 割当(新規Voice選定なし): V1=Algieba(男) / V2=Zephyr(女) / V3=Schedar(男) / リード・Tension+Closing・In One Line=Aoede。Z正式表の`assign_dialogue_voices`結果とユーザー決定の固定割当が一致(`voice_assignment_check.json`、match=true)。実使用Voiceはraw_usage_logのvoice欄・各segmentの`y_tts_voice_requested`で一致。
- 機械指標(`QA_RESULT_01.md`のVoice別実測表、`voice_timbre_distance.json`):
  - V1(Algieba)対V3(Schedar): 帯域スペクトル重心 Adv 2,488 vs 3,791Hz / Std 2,348 vs 3,166Hz(V3の方が明るい)。話速 Adv 195.9 vs 204.9語/分、Std 184.1 vs 177.8。1/3オクターブ平均スペクトルの差 Adv 3.37dB / Std 2.97dB(同一Voiceのレベル間のぶれ 1.1〜2.2dB、男女間 3.8〜5.8dB)。
  - **F0中央値**: Advで V1 104.8Hz / V3 103.4Hz(ほぼ同一)、Stdで V1 106.7 / V3 139.5Hz。簡易自己相関法のためオクターブ誤りの可能性があり(V3のレベル間差が大きいのはその影響と推定)、**ピッチ差だけでは聞き分けを保証しない**。過去のY Trialでも男性2声はF0差1.9〜2.6半音で、重心・話速で差が出るという同じ傾向(OPEN-463 委任_05)。
  - 判定: 男性2声は**音色の明るさと話速で差が出ている(弱〜中)**。V1/V3の聞き分けは**耳での確認が必須**(FABLE_EVAL_03限定条件(f)の宿題は未了。判断材料=ページのパート別再生で人物1と人物3を聴き比べる)。
- 品質面の観察(耳ではなく記録): Std本文は6%減速が全5本文segment+In One Lineで適用(Y style gate確認)。3人の語りの語/分はAdv 196〜205、Std 178〜189。ナレーター(Aoede)の語/分はAdv 159〜191・Std 145〜182。過剰演技・ニュースナレーター化は機械指標では判断しない(Styleは既存のまま変更せず)。

## 4. TTS/ASR等の品質検査結果と残存問題
`QA_RESULT_01.md`(clip別)参照。要点:
| 項目 | Adv | Std |
|---|---|---|
| 全segment status | 20/20 OK(本文5・Comment3・Preview・In One Line・topic_intro・KP9[英語/解説/phrase_repeat×3]) | 18/18 OK(日本語タイトル・Comment/KP意味 日本語を含む) |
| 統一ASR判定 | 全てasr_verified(EXACT/NORMALIZED/NUMERIC_EQUIVALENCE) | 同 |
| Repetition QA(method D') | 本文5segmentすべてPASS | 同 |
| 再生成(retry) | Voice 2が1回(1回目: ASRが原稿の`Am I wrong to feel that way?`を`Am I right…`と転写=意味反転を検出→再生成で解消) | 0 |
| 局所Rewrite / fallback / HR Lock | 0 / 0 / 0 | 0 / 0 / 0 |
| Y style gate / Audio Validation Gate / Assembly | PASS / PASS / OK(clipping無し) | PASS / PASS / OK |
| Key Phrase音声(canonical+KP vote audit) | 3/3 vote evidence、blocking 0 | 3/3 vote evidence、blocking 0 |
| pass_with_warning(事後試聴の参考、非ブロッキング) | 1件: Voice 2本文(secondary ASRのみ`do something about.Showing up`と句の切れ目を転写、primaryは原稿どおり=SECONDARY_CONFIRMED) → 該当文付近(Voice 2後半「Before charging us…」)を聴いて不自然な間がないか確認を推奨 | 0件 |
- **残存問題・未確認**: (a) 耳による自然さ・感情表現・V1/V3聞き分けの判定は未実施。(b) pass_with_warning 1件(上記)。(c) Adv Voice 1/3のF0がほぼ同一(音色・話速で差)。(d) Risk Flaggerは未実施(意見ベースで検証済み事実台帳がなく、Y列は『未定』)。(e) 局所Rewriteは発動0のため『一人称・立場・口調が保持されるか』の確認は不要(発動時のみ必須としていた確認項目の実例なし)。(f) 日本語リードの『開示文』(R0の既存文)と生成リードの語尾・言い回しの連結が自然かは耳/目の確認が必要。
- 再起動0・STOP通知0・HR/RESTART_STORM 0。

## 5. 実費・所要時間・量産単価への示唆
- 実費(`BUDGET_LOG_01.md`): **33.40円**(日本語補完10.59、英訳+監視1.58、scaffold 1.52、音声19.72)。見積最大40.4円・案件Cap55円内。**最大の見積外れ=Tension+Closing生成9.37円**(見積1.2〜2.4円。既存関数の既定effort=highで出力5,525 token)。日次累計: 着手時721.68円→完了時831.30円(1,000円内)。
- 所要時間: 着手(10:50頃)〜完了(約13:00)。有料launchの実時間=日本語2分、英訳2.5分、scaffold 2分、**音声86分**(TTSがbatch API=1 segment約2.5分×約45 clip、直列)。音声以外は計7分程度。
- 量産単価の目安: R0側25.49円+本Trial 33.40円=**約58.9円/セット**(情報収集・整理のLLM化は未測定[人手約25分]のため含まず、RFも未実施)。70円目標は、情報収集のLLM化が約11円以下であれば範囲内、超えれば超過。削減余地: Tension+Closingのeffort(未測定)、音声は他Familyと同水準。**測定値であり確定値ではない**(n=1テーマ)。

## 6. Fableの独立受入評価とTrial Closeout Status
- Fable独立評価はFableが実施(私は記入しない)。**Status候補(私の提案、判定はFable)**: `TRIAL_DONE_PENDING_FABLE_EVAL`(技術受入条件=PASS: 5パート順序・話者対応、全Gate、費用、隔離、公開ページ検査。到達上限=`VALIDATED`[音声化Trial、限定条件付き]。`APPROVED_FOR_PRODUCTION`は書かない)。
- VALIDATED(音声化Trial)とするための残件(耳が要るもの): 人物像の自然さ、V1/V3聞き分け、ナレーターの語り口(ニュース調でないか)、pass_with_warning箇所。
- 限定条件(FABLE_EVAL_03から継承・追加): 1テーマ、V1根拠のR2+(許諾なし)、公開は限定共有のみ、男性2声の聞き分けは耳で確認、Production入口なし。

## 7. 今後Production化する場合の未完了事項(OPEN-484受入条件との対応)
| OPEN-484の受入条件 | 現状(本Trial) | Production化時の残件 |
|---|---|---|
| (a) Y正式初回Production経路のKP段が`sc.run_key_phrase_canonicalization`(hook付き)を通る | Trial scaffold(`cmd_scaffold`)が共通関数を呼ぶ。今回のKPは`CANONICALIZATION_PASS`(Adv・Std) | Y正式経路(Writer/Plan/Support/KP/TTS/Assemble/Page)の新設が前提 |
| (b) retry/fallback/regeneration/resumeで同じ関数 | Trialでは再生成0のため未検証 | 正式経路で検証 |
| (c) Y正式経路のruntime evidence(model_id・routing・template sha・possessor_roles・person_role_repair・before/after) | Trial経路のevidenceのみ(KP: `key_phrases/*.json`) | 正式経路で取得 |
| (d) 必須Regression・Validator・integration test | Y用test 14件(本Trial)+既存58件PASS | 正式経路のtest |
| (e) Dangling Reference 0 | 未確認(Trial) | 確認 |
| (f) `production_reachable`の解消 | `False`のまま | 入口新設時 |
- 本Trialで追加で判明した「Production化時の未完了事項」: (1) **リード生成の正式仕様化**(今回はY_R0_HEADのリード仕様で1 call、決定論検査のみ。LeakageにリードのItemが無い)、(2) **Tension+Closingのeffortと費用**(9.4円、70円目標への影響)、(3) **英語Ledgerの扱い**(意見ベースは事実台帳が無い。IOL/RFの入力をどうするか)、(4) **Risk Flagger**(Y列『未定』)、(5) **5パート対応確認(`mapping_check`)をGate化するか**(今回は記録のみ)、(6) **権利**: V1根拠のR2+(許諾なし)の許諾取得/出典置換と、収集方針(再利用可能出典を中心に)、公開は許諾後、(7) **男性2声の聞き分けの耳確認と、不足ならVoice設計の再判断**(新Voice選定はユーザー判断)、(8) **TTS時間**(batch直列で86分/セット。並列化の可否は共有store・直列化規則の設計次第)、(9) Yの会話高速化(`z_speed_v2`相当)は未採用(OPEN-484 SHORT-CLIP-SPEED-GATE追記どおり、採用は別判断)、(10) scopeリテラルへの"Y"追加(er109/PNAPはY非活性のまま)。
- 既存の古いY試聴ページ部品の不具合(新規発見、本Trialでは変更せずwrapperで回避): `er110_family_y_audio_page_01.py::_ja_original`が`#`付きタイトルを前提にしており、`article_final.md`(タイトル行が`#`なし)では「日本語の元原稿」が1段落ずれる。公開済み`user_test/family_y_trial_01/index.html`の「日本語の元原稿」表示がずれている(補助表示のみ、音声・英語本文には影響なし)。分類=実害なし(旧Trial 01の補助表示。置換済みの旧ページ)。直す場合は`_ja_original`をタイトル行の有無に依存しない形に修正(DEV専用、API 0・小修正)。

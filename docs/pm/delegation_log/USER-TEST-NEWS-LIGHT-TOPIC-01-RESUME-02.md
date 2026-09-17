## 管理ID

`USER-TEST-NEWS-LIGHT-TOPIC-01-RESUME-02`(+付随の恒久運用ルール正式化)。前回`USER-TEST-NEWS-LIGHT-TOPIC-01`の続き。現在main=origin/main=`25062bac`。報告は`docs/pm/RESULT_PACKET_NEWS_LIGHT_02.md`(新規、累積Full Report、★★★★報告ここから/ここまでブロック)へ。並行Agentなし(本タスク単独)。

## 前提(前回到達点、`docs/pm/RESULT_PACKET_NEWS_LIGHT_01.md`参照)

- 記事A2/B1完成、driver=`er014_output/user_test_news_light_01/tiny_bags/run_pipeline.py`、成果物`er014_output/user_test_news_light_01/tiny_bags/{a2,b1b}/`。
- B1 `point_one`: canonical "with room for only a few essentials" の "only" が3attemptとも実音声で脱落(`TRUE_CONTENT_MISMATCH`、`STOPPED`、Human Review Lock)。**ユーザーが音声を確認し、ASR誤認ではなく実際に脱落していると判断済み。現音声の承認案は却下。**
- A2 `full_story_part2`: ブランド名 Toteme / Kallmeyer のPrimary ASR不一致(Totem / Kalmeyer等)が継続、`ASR_VALIDATION_UNCERTAIN`、Human Review Lock。
- 費用上限: 本タスク合計¥300(TTS再生成はB1 point_oneの1〜2 cycle+A2は原則TTS再生成なし)。

## ユーザー決定(2026-09-17、そのまま実行してよい)

### 1. B1 `point_one`

**Step 1**: canonicalは変更せず、時間をあけた状態で**正式TTS→ASR経路で再生成を1 cycle**行う(`er011_human_review_lock_01.approve_regenerate()`で承認記録→前回と同じProduction関数[`er003_v1_n3_01_tts_generate.generate_b1_segments`が使うB1 News本文経路、`news_tail_fix.generate_news_narration_wide_margin`]でpoint_oneのみ再生成。Space Weapons/AI Controlで使ったsegment単位regenスクリプト[`er014_output/user_test_news_2ep_01/*/b1b/regen_*.py`等]の型を踏襲)。内部attempt上限はProduction既定(`PRODUCTION_MAX_TTS_ATTEMPTS=3`)のまま、cycleは1回のみ。"only"が実際に発音されたことを、ASR分類(EXACT/NORMALIZED_MATCH)に加え、local faster-whisper verbatim(`er008_disfluency_qa_18.transcribe_verbatim`、無料)でも確認して証跡化。PASSならその版を採用。

**Step 2**(Step 1で全attemptとも"only"脱落の場合のみ): canonicalを `with room for just a few essentials` へ最小変更(ユーザー承認済み)。対象はB1 point_oneの当該文のみ。`article.md`/parts/scaffold等、canonicalを保持する全ファイルを同期(player scriptにも反映されるよう)。意味変更なしを確認し、Ledger Deviation Check(`er003_v1_en_direct_vfl_01_generate.run_deviation_check`、B1記事に対して1回)を再実行、Fact Checkerは再実行不要(数値・事実変更なし)。その後同じ正式経路でTTS→ASR。**記事全体の再生成は禁止。**

Step 2でも不整合ならSTOP(音声出力せず報告)。

### 2. A2 `full_story_part2`(Toteme / Kallmeyer)

**TTS再生成はしない。** 正式ASR cascade(`er006_secondary_asr_01.evaluate_attempt_with_cascade_detail`、CURRENT_SPEC L1277「ASR-first Retry Policy」①Primary#1→②Primary#2→③Azure Secondary+Phrase List→④Secondary#2)を、既存attempt音声(`audit/`配下のattempt wav、最終attemptを優先)に対して**Secondary ASRまで必ず実行**する。前回のcascade記録(`human_review_queue.jsonl`該当行、`tts_generation_results.json`)でSecondaryが実行済みか先に確認し、未実行なら実行、実行済みならその結果を再検証(Phrase List使用有無`phrase_list_used`を必ず確認)。

**正しい発音の確定(必須)**: Pronunciation Ledger正式経路(`er006_pronunciation_ledger_01`、Perplexity調査、固有名詞ごと個別クエリ、cache hitなら再調査しない)で Toteme(スウェーデン発ブランド Totême)と Kallmeyer(NYデザイナー Daniella Kallmeyer)の発音を取得し、以下をセットで確定: canonical spelling / IPA / 簡易カタカナ(learner cue) / 根拠source(URL) / Primary ASR結果(全attempt) / Secondary ASR結果(Phrase List有無別) / TTSが実際にどう読んでいるか(local verbatim ASR+ASR転写の音素的解釈。例: Primaryの"Totem"はTTSが/toʊˈtɛm/相当で読んでいる可能性を示す、等を根拠付きで記述)。Ledgerへ登録した場合はそのentry(surface/hint/source)を報告。**注意**: OPEN-159で`get_hint_for_text`の大文字小文字不一致bugが既知。Phrase Listへ実際に語が渡ったかを`phrase_list_used`と渡したphrase一覧で証跡化(bugが発火する場合はledger_phrasesを明示的に渡してよい。bugの修正はスコープ外、報告のみ)。

**判定**: (a) Secondary+Phrase Listで`SECONDARY_ASR_MATCH`等should_pass→Lock解消(`record_outcome`/所定手順)、Human Review不要、Assemblyへ。(b) Secondaryでも未解決だが、正しい発音情報とTTS実読の突合で「TTSは正しい発音で読んでおりASR表記ゆれのみ」と根拠付きで判断できる→**Human Review確認ページ**を作りユーザー確認へ(承認代行はしない、Assemblyは止めたままSTOP)。(c) 正しい発音sourceが確定できない/TTSの読みが明らかに誤り→STOP報告。

### 3. Human Review確認ページ(恒久運用、raw mp3/wav直リンク禁止)

ユーザーに音声確認を依頼する場合(今回はA2の(b)ケース、B1のStep 2失敗時は不要=STOP)、**raw mp3ダウンロードリンクは提示禁止**。以下の簡易確認ページを作る(凝ったUI不要):
- 配置: `er014_output/user_test_news_light_01/tiny_bags/a2/human_review/index.html` + 同ディレクトリにmp3(wavは絶対にcommitしない)。相対パスで音声参照。
- 表示: Play button(`<audio controls>`最低幅360px、Gate 7(l))、該当segment音声、canonical script全文、問題箇所highlight(`<mark>`)、正しいIPA+カタカナcue+source、確認ポイント(何を聴いて何を判断するか、選択肢: 許容/再生成)、Primary/Secondary ASR結果の要約。
- できれば再利用可能に: `user_test/human_review.html`(query param `src=<json path>`でJSONを読む方式、`user_test/unified.html`と同型)を新設し、JSONに上記情報を置く形が望ましい。既存`unified.html`は変更しない。どちらの方式でも可、判断理由を報告。
- **実ブラウザE2E必須**: Playwright headless Chromium(既存`docs/pm/closeout_136_e2e/`の型)で、rawcdn.githack URL(commit/push後のSHA)に対し page load / Play開始 / currentTime進行(≥2秒) / `audio.error`なし / script表示(DOM text検証)を確認し、evidence JSONを`human_review/e2e_evidence.json`へ保存。HTTP 200だけでは不可。
- URL形式: `https://rawcdn.githack.com/shimomura055/eigo-radio/<SHA>/<path>`。

### 4. 完成処理(Lock解消したレベルごと)

Assembly(`er003_v1_n3_01_assemble`、Audio Validation Gate、override禁止)→`build_web_player_common.py`でplayer.html(記事dir root、`web/episode.mp3`)→`user_test/unified.html?src=...&level=...&en=...&ja=...`形式URL(前回と同じ)→Playwright E2E(既存型、evidence保存)→Sheet行(記事タイトル(English)/記事タイトル(日本語)/記事の概要(日本語)/ノーマル(A2)/Advanced(B1)/備考=最新ニュース(ライト系))。片方のみ完成でも、そのレベルは完成まで進める。

### 5. 恒久運用ルールのSSOT反映(最小限、重複確認のうえ)

`docs/pm/PM_GOVERNANCE.md`に新設「9-9. Human Review試聴提示ルール(2026-09-17、ユーザー正式決定、`USER-TEST-NEWS-LIGHT-TOPIC-01-RESUME-02`)」: (1)Human Review/pronunciation/segment品質確認の依頼は、raw mp3/wavのダウンロード直リンクではなく、ブラウザ上でPlay可能+canonical script同一ページ表示+確認ポイント明示の確認ページ(segment単位簡易playerで可)で提示する。(2)最低要件: Play button/該当segment音声/canonical script/問題箇所highlight/発音問題なら正しいIPA/確認ポイント。(3)提示前に実ブラウザE2E(page load/Play開始/currentTime進行/audio errorなし/script表示)必須、HTTP 200のみ不可(Gate 7 E2E要件の適用)。(4)**発音判断を求める場合、正しい発音情報(canonical spelling/IPA/カタカナcue/source/Primary・Secondary ASR結果/TTS実読)を事前提示せずに「この読みでいいですか」だけを聞くことは禁止**。(5)Primary ASR mismatchだけでproper nameをHuman Reviewへ上げない(CURRENT_SPEC「ASR-first Retry Policy」の再確認)。既存9-5(Artifact/playerリンク必須)・9-7(`file:///`禁止、GitHub raw配布)・Gate 7(m)との関係を明記: 9-7(4)のGitHub raw配布は「HTML確認ページの配布経路」として引き続き有効だが、**音声ファイル自体のraw直リンク提示はHuman Review用途では不可**とする(9-7の更新ではなく本節による具体化)。適用範囲: 今後のPR/Trial/Production QA全般。PM_GOVERNANCE末尾の変更履歴節があれば1行追記。`CURRENT_SPEC.md`「Human Review Route」行(L1280付近)末尾に「ユーザー提示形式はPM_GOVERNANCE 9-9に従う(2026-09-17)」の短い注記を追記(仕様本文は変更しない)。競合があればSTOP報告。

### 6. SSOT/Git

- `DECISION_LOG.md`: `## USER-TEST-NEWS-LIGHT-TOPIC-01-RESUME-02`エントリ(索引+本体、`## 参照元`直前)。B1 only判断(Step1/2結果)、A2発音確定内容、9-9新設、Status。
- `OPEN_ITEMS.md`: 新規仕様問題が出た場合のみ登録(例: "only"脱落が時間差再生成で改善したか否かの観測記録はDECISION_LOGで足りる)。OPEN-159へcase bug再発時の追記のみ可。
- `ARTIFACT_REGISTRY.md` News-familyセクションへTiny Bags A2/B1行(完成したもののみ、未完成はStatus明記)。
- 明示add、`git add -A`禁止、wav禁止、fetch→merge(rebase/force禁止)。commit分割可(成果物→SSOT)。commit message例`USER-TEST-NEWS-LIGHT-TOPIC-01-RESUME-02: Tiny Bags B1 only再TTS+A2 Secondary ASR/発音確定+Human Review試聴ページ+PM_GOVERNANCE 9-9`、trailer `Task-ID: ...`。

## STOP条件(STOPしたら他レベルの完了処理は続けたうえで報告)

B1: Step 2後も音声不整合。A2: Secondaryまで実行しても読みが確定できない/正しい発音sourceが確定できない。共通: 新しいProduct仕様判断が必要、9-9が既存PM governanceと競合、費用¥300超過見込み。承認代行(Human Approvalの記録)は一切しない。

## 手順の固定事項

T-0: 委任文を`docs/pm/delegation_log/USER-TEST-NEWS-LIGHT-TOPIC-01-RESUME-02.md`へ保存し`.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file <path> --json-out <path>_check.json`、結果1行記録(FAILでも継続)。E-1/D-1/G-1/F-1/T-1従来どおり。事前指定Read: 上記driver・前回RESULT_PACKET・`human_review_queue.jsonl`該当行・`er006_secondary_asr_01.py`(cascade API)・`er006_pronunciation_ledger_01.py`(登録API)・`er011_human_review_lock_01.py`(approve_regenerate/record_outcome)・Space Weapons regenスクリプト・`docs/pm/closeout_136_e2e/`・PM_GOVERNANCE 9-5/9-7/Gate 7(a)-(m)。事前指定外Readは理由付きで報告。

## 報告項目(`docs/pm/RESULT_PACKET_NEWS_LIGHT_02.md`、★ブロック内、累積Full Report=前回の1〜17項目の到達点も要約再掲)

0. T-0
**B1**: 1.時間をあけた再TTS結果(attempt数・分類) 2.onlyが実際に発音されたか(ASR+local verbatim) 3.ASR結果 4.fail時justへ変更したか 5.Ledger/QA結果 6.final segment status 7.player URL+E2E evidence
**A2**: 1.Totemeの正しい発音 2.Toteme IPA 3.Kallmeyerの正しい発音 4.Kallmeyer IPA 5.source 6.Primary ASR結果 7.Secondary ASR結果(phrase_list_used/phrases) 8.final判断(a/b/c) 9.Human Review必要なら確認ページURL+E2E evidence 10.raw mp3リンクを使っていないこと 11.Assembly/Gate/player URL(解消時)
**共通**: 12.Sheet行 13.cost実測(内訳) 14.PM_GOVERNANCE 9-9/CURRENT_SPEC注記の反映箇所 15.DECISION_LOG/OPEN_ITEMS/ARTIFACT_REGISTRY 16.Git SHA 17.ユーザー判断 A(仕様・Product・実装判断待ち)/B(ユーザー試聴・品質確認待ち。確認ページまたは完成playerができた項目のみ) 18.無変更証跡(`git status --porcelain`でer0*.py Production変更なし、`user_test/unified.html`無変更)/事前指定外Read。

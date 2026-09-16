## 管理ID

`USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-02`(親: `USER-TEST-NEWS-2EP-COMPLETION-01`、前段: `-CORRECTION-01`。現在main=`0f6014de`、並行タスクなし)。報告は`docs/pm/RESULT_PACKET_NEWS_2EP_RESUME.md`(新規)へ。`docs/pm/ACTIVE_TASK.md`は固定ヘッダ形式で上書き可。前回RESULT_PACKET(`docs/pm/RESULT_PACKET_NEWS_2EP.md`、`docs/pm/RESULT_PACKET_NEWS_2EP_CORRECTION.md`)の内容は既知としてよい(必要箇所のみGrep)。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー正式判断(2026-09-17)を受け、Space Weapons A2 `full_story_part1`を既存standard route音声の再利用で解決し、親タスク(2テーマ×A2/B1=4完成episode+user-test player+URL+Sheet投入情報)を既存Production正式経路で完成させる。あわせて固有名詞発音基盤の課題をOpen Item登録のみ(DEFERRED)で記録する。
- 到達上限Status: 記事処理=USER_TEST_READY(受入条件17項目をすべて満たした場合のみ)。固有名詞・人名Production改善=DEFERRED / Open Item(PRODUCTION_WIRED扱い禁止)。APPROVED_FOR_PRODUCTION/PRODUCTION_WIREDへの変更禁止。
- 禁止: 不要なTTS再生成(特にMeink segmentの再生成)、不要なWriter/Research/Fact Checker再実行、新モデル試行、Prompt改善Trial、Productionコード改修(er003_*.py/er006_*.py/er011_*.py等root直下module)、固有名詞基盤改善Trial、新validator、新しいProduction rule名・原則名の追加、CURRENT_SPECへの未承認新仕様追記、user_test/unified.htmlの改修、Google Sheet編集、複数案検証、git add -A/stash/amend/rebase/force push、wavのcommit。
- コスト: B1音声+Theme 2一式で300〜450円想定。累計(本タスク分)が900円を超える見込みならSTOP。

## STOP条件(即STOP・報告、別案/別モデル/追加Trialへ進まない)

- Troy Minkと認識された既存standard route音声の実体が確認できない/artifactとASR証跡(sha256)が一致しない/破損
- 既存音声再利用にProductionコード変更が必要
- 新しいHuman判断が必要(Theme 2でのHuman Review Lock発火・retry上限到達を含む)
- Theme 2で新しい仕様判断が必要(現行正式pathが複数・Researchでテーマ前提が誤り等)
- Audio Gate等で新しいblocker発生
- 新規Production改修が必要/想定外のAPI再実行が必要
- unified.html互換性問題(UI改修せずSTOP)
- コスト900円超見込み

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない。
D-1: Grep→該当行範囲Read、全文Readは構造変更時のみ。
G-1: git出力は--porcelain/--stat/--shortで最小化。
F-1: transcript退避不要。
T-1: 事前指定Read/Grep一覧に従い、一覧外の追加Readは理由をRESULT_PACKETに1行記録。
T-0: 委任文をdocs/pm/delegation_log/USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-02.mdへ保存し.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file <path> --json-out <path>_check.jsonを実行、結果をRESULT_PACKETへ1行記録(FAILでも継続)。

## ユーザー正式判断(原文要旨、忠実転記)

### 1. Space Weapons A2 / Troy Meink
本人の固有発音は確認できないため、今回は一般的な姓Meinkの読みとして /mɪŋk/ を採用。現在finalのfallback音声(ASR Troy Mike)は不採用。以前のstandard route音声(ASR Troy Mink)は/mɪŋk/と整合する可能性が高いため、既存standard route音声の再利用を最優先。対象候補: full_story_part1_attempt2_custom35d6860b.wavまたは実際にTroy Minkと認識された既存standard route artifact。
実施順: (1)既存standard route音声の実体・sha256・対応ASR証跡を確認 (2)その音声がTroy Minkと認識された対象と一致することを確認 (3)問題なければTTS再生成せず既存音声を採用 (4)正式経路でHuman Review Lock/review stateを整合 (5)A2 Assembly (6)Audio Validation Gate (7)PASSなら親タスク再開。既存音声が存在しない・破損・証跡と対応しない場合のみSTOP。今回はMinkというASR綴り自体を誤発音扱いしない(採用読み/mɪŋk/と整合するものとして扱う)。

### 2. Production固有名詞・人名発音基盤(今回修正しない、Open Item登録のみ)
- Pronunciation LedgerのIPAがSecondary ASRの自動PASS判定に使われていない
- research経由Ledger entryの大文字小文字不整合によりget_hint_for_textで拾えない
- fallback final wavとHuman Review証跡transcriptの不一致
- Pronunciation Ledger→TTS hint→Secondary ASR→pronunciation validation全体の設計ギャップ
Open Itemには「ユーザ実検証終了後、固有名詞・人名の発音処理を、research→Ledger→TTS hint→ASR→判定→review evidenceまで一括して徹底改善する」を明記。今回の記事完成をブロックしないdeferred itemとして管理。

### 3. 親タスク再開(A2 Assembly/Gate PASS後、既存Production正式経路で)
(1)Space Weapons B1音声完成 (2)Theme 2「AIは本当に人間の制御を超える可能性があるのか」Research→Ledger→A2/B1本文→Scaffold→TTS→Assembly→Audio Validation Gate (3)4本のuser-test player完成 (4)参照可能なURL作成 (5)Sheet投入用情報作成 (6)commit/push。B1 Fact Checker REVIEW_REQUIREDは既存CURRENT_SPEC/ER-010-NO9どおりnon-blocking advisory、追加修正しない。

### Open Item登録要件(最低限)
1. Pronunciation Ledger IPAがSecondary ASR自動判定に未使用 2. research登録entryのcase normalization不整合 3. fallback final wavとHuman Review evidenceの紐付け不整合 4. TTS pronunciation hintへの正式利用方法 5. /mɪŋk/のようにASR spellingがcanonical spellingと異なっても発音上正しいケースの判定方法 6. ユーザー実検証終了後に固有名詞・人名処理を包括的に再設計・検証すること。
CURRENT_SPECには未承認の新仕様を書かない。DECISION_LOGには今回のユーザー判断(/mɪŋk/採用・standard route音声再利用・基盤改善defer)とdefer方針を記録。OPEN_ITEMSに上記未解決事項を登録。

### Dangling Reference Check
新しいProduction rule名・原則名を追加しない。既存のPronunciation Ledger/Secondary ASR/Human Review Lock/Audio Validation Gate/Production正式News pathのみ利用。

### 受入条件(17)
1. Troy Mink認識の既存standard route音声の実体確認 2. sha256/ASR証跡確認 3. TTS再生成なしで再利用 4. Human Review/review stateを正式経路で整合 5. Space Weapons A2 Assembly PASS 6. Audio Validation Gate PASS 7. Space Weapons B1完成 8. Theme 2 A2/B1完成 9. 4 player完成 10. URL 4本確認 11. Sheet投入情報作成 12. Open Item登録 13. DECISION_LOG更新 14. CURRENT_SPECに未承認仕様を追加していない 15. commit/push確認 16. actual runtime evidence確認 17. 未処理USER_DECISION_REQUIREDなし

## Fableからの補足

- Theme 2の要件(親委任文docs/pm/delegation_log/USER-TEST-NEWS-2EP-COMPLETION-01.mdの「Theme 2」「Research/Fact方針」「A2/B1」「完成episode」「Key Phrase」「Audio」「user-test player」節を再読して従う): 直近AI safety/capabilityニュース起点、実証済み能力/確認済み事実/企業・研究者の将来リスク発言/Singularity等の仮説/未確認推測を分離、「AIが人間の制御を超える」と事実認定しない、恐怖を煽らない、Research 1回でA2/B1共有、タイトルは"Could AI eventually become difficult for humans to control — and what evidence do we actually have today?"に近い構造(Research結果で自然に調整可)。Space Weaponsと同じdriver構造(er014_output/user_test_news_2ep_01/space_weapons/run_pipeline.pyをai_control/へ複製・topicのみ差替え、Prompt本文変更なし)。
- Meink segment再利用の実務: review_lock_state.jsonのfull_story_part1はHUMAN_REVIEW_REQUIRED、final wav=fallback attempt3(sha256 5f5632e6…)。standard route候補=.../a2/narration/attempts/full_story_part1_attempt2_custom35d6860b.{wav,json}(json内transcript Troy MinkをGrepで確認、wavのsha256を実測してjson記録と照合)。採用時は当該wavをfull_story_part1.wavとして配置(元fallback wavは_fallback_rejected.wav等に退避、上書き削除しない)し、Audio Validation Gateが要求する必須post-process(6% slowdown等)のevidenceが当該attemptに紐づいているかを確認(なければ既存正式post-process関数で適用しevidence記録。TTS再生成ではない)。review stateの整合はer011_human_review_lock_01の正式関数(record_human_approval相当、reason="ユーザー判断2026-09-17: /mɪŋk/採用、standard route attempt2再利用")で行い、Human Review Queue(er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl)にも既存形式で解決記録があるなら追記。ユーザー判断は既に確定済みなので、この承認記録はSonnetが実行してよい。
- URL: 親タスク指定の形式 https://rawcdn.githack.com/shimomura055/eigo-radio/<FINAL_MAIN_SHA>/user_test/unified.html?src=<PLAYER_PATH>&level=<LEVEL>&en=<URL_ENCODED_EN_TITLE>&ja=<URL_ENCODED_JA_TITLE> を必須とする。今回ユーザーは「GitHub Pagesで参照可能なURL」とも記載しているため、repoにGitHub Pages設定の実体(.nojekyll/docs/index.html/gh-pagesブランチ/CNAME/既存Pages URLの記録)が既に存在する場合のみPages URLも併記する。存在しなければPages設定は変更せず(repo設定変更はユーザー操作)、rawcdn URLで報告し「Pages未設定」と明記する。
- Open Item番号: OPEN_ITEMS.mdをGrep ^## OPEN-|^\| OPEN-|OPEN-15[0-9]で最終番号を確認し次番号(OPEN-159〜想定)。既存OPEN-154/155(DEFERRED)の書式に合わせる。DECISION_LOGは直近エントリ(Grep USER-TEST-)の書式に合わせ、管理IDUSER-TEST-NEWS-2EP-COMPLETION-01-RESUME-02で1エントリ。DECISION_LOG/OPEN_ITEMSの追記位置はGrep結果の行番号を記録。
- 語数報告義務(9-11): Theme 2の各本文語数を報告し、280未満/500超なら明記。
- 前回T-0 FAIL理由(見出し文言不一致)は形式差、今回も継続扱い。

## 事前指定Read/Grep一覧

- docs/pm/delegation_log/USER-TEST-NEWS-2EP-COMPLETION-01.md: Theme 2/Research/A2B1/完成episode/Key Phrase/Audio/player/Sheet節
- er014_output/user_test_news_2ep_01/space_weapons/run_pipeline.py: 全体(driver複製のため、構造変更時扱いで全文Read可)
- .../space_weapons/a2/narration/attempts/full_story_part1_attempt2_custom35d6860b.json: Grep Mink|sha256|wav|status|classification|slowdown|post_process
- .../space_weapons/a2/audit/review_lock_state.json L374-393、.../a2/audit/assembly_and_gate_summary.json(Gate要求事項の文言)
- er011_human_review_lock_01.py: Grep def |HUMAN_APPROVED|record_human_approval|approve→正式承認関数のみ
- er003_v1_n3_01_assemble.py/Gate module: Grep slowdown|post_process|evidence|HUMAN_APPROVED|VALIDATED→Gateが受理する状態と必須evidenceの条件のみ
- OPEN_ITEMS.md: Grep OPEN-15[4-9]|DEFERRED_UNTIL→書式・最終番号行のみ。DECISION_LOG.md: Grep USER-TEST-NEWS|USER-TEST-LEGACY→直近エントリ書式のみ。CURRENT_SPEC.md: 変更しない(Grep不要)
- docs/pm/PM_BRIEF.md L135-159(固定ヘッダ)
- Pages設定確認: Glob .nojekyll、CNAME、docs/index.html; git branch -r --list "*pages*"

## 手順

1. T-0。
2. Meink既存音声再利用(上記実務)→A2 Assembly→Audio Validation Gate。PASSしなければSTOP(受入1〜6)。
3. Space Weapons B1音声(Scaffold済み→TTS→ASR/Validation→Assembly→Gate)。
4. Theme 2(ai_control/)Research→Ledger→A2/B1→Fact Checker/Ledger Deviation→Scaffold→TTS→Assembly→Gate。Human Review Lock/retry上限/仕様判断が出たらSTOP(Space Weaponsの完成分は保持)。
5. player 4本(unified.html srcの互換形式、Key Phraseは英語+日本語意味のみ、内部情報・SFX/jingle非表示、local path参照なし)。
6. SSOT: OPEN_ITEMS登録(6要件を1〜2件のOpen Itemに整理可、Status=DEFERRED、ブロック対象外と明記)、DECISION_LOG 1エントリ。CURRENT_SPEC無変更。
7. Git: 成果物commit(明示add、wav除外)→push→FINAL_MAIN_SHAでrawcdn URL 4本組み立て→User-Agent付きGET(unified.html/src対象/episode mp3 Range)で200/206確認(CDN遅延60秒×最大3回)→RESULT_PACKET/ACTIVE_TASK/SSOTを別commitでpush。メッセージ: USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-02: Meink standard route音声再利用+Space Weapons B1+AI Control A2/B1完成+player 4本+Open Item登録、trailer Task-ID: USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-02。

## 報告(docs/pm/RESULT_PACKET_NEWS_2EP_RESUME.md、簡潔に)

0. T-0結果
1. Meink既存音声の再利用結果(採用attempt、退避先)
2. sha256/ASR evidence(attempt json記録値と実測値、transcript)
3. Space Weapons A2 Assembly/Gate結果(duration)
4. Space Weapons B1完成結果(Audio Validation/Assembly/duration)
5. Theme 2 A2/B1完成結果(EN/JAタイトル、語数、Fact Checker/Ledger Deviation/Cross-level、Audio Validation/Assembly/duration、Human Review Lock有無)
6. URL 4本(rawcdn必須、Pagesは設定実体がある場合のみ)+到達確認結果
7. Sheet投入内容(2行: 記事タイトル(English)/記事タイトル(日本語)/記事の概要(日本語)/ノーマル(A2)/Advanced(B1)/備考=最新ニュース)
8. 追加APIコスト(cost logger実測、model_id)
9. Git commit/push(SHA)
10. Open Item登録内容(番号・要旨)
11. CURRENT_SPEC(無変更証跡)/DECISION_LOG/OPEN_ITEMS更新結果(行番号)
12. 現在Status(記事処理/固有名詞基盤)
13. 未決事項一覧
14. 無変更証跡(git status --porcelain er003_*.py er006_*.py er011_*.py CURRENT_SPEC.mdが空[ledger.json等の既存未commit差分は別記])/事前指定外Read(理由付き)

ユーザー向け表記はB1に統一(内部識別子b1bはpathにのみ可)。

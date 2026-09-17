## 管理ID

`PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01-PHASE-B-FIX-01`(前段: Phase B `docs/pm/RESULT_PACKET_PN_A2_PHASE_B.md`[既読扱い可、Status=WIRING_INCOMPLETE、Narrator見出し2 segmentがHuman Review Lock])。現在main=`5740f747`以降。報告は`docs/pm/RESULT_PACKET_PN_A2_PHASE_B_FIX1.md`(新規、累積Full形式=Phase Bの結果も統合)へ。

**並行タスクあり(衝突回避ルール)**: `USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-04`(AI Control音声stage=TTS/ASR/Assembly実行中→player→SSOT→commit)が実行中。(1)**本タスクのTTS/ASR/Assembly/Gate(共有store書き込み)は、marker `docs/pm/RESULT_PACKET_NEWS_2EP_RESUME4.md` が存在するまで開始しない**(5分間隔で最大120分。超過時はコード是正+test完了までで停止し報告)。コード確認・是正・unit test・regressionは即実行可(regressionのうち共有storeへ書くtestが無いことを確認して実行)。(2)SSOT編集・git操作は最後にまとめ、`git status --porcelain CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md docs/pm/PM_GOVERNANCE.md`で自分以外の未commit変更が無いことを確認(あれば5分間隔で最大30分待つ)。commit前に`git fetch origin`→`git merge origin/main --no-edit`(rebase/force push禁止、競合時STOP)。全文Write禁止。`docs/pm/ACTIVE_TASK.md`は最後に1回だけ固定ヘッダで上書き(他タスク状態を保持)。(3)`er014_output/`・root `er003_*.py`/`er006_*.py`/`er011_*.py`には触れない。

## 性質/到達Status/禁止事項

- 性質: Phase Bで新設した`main_a2_2v()`経路の**retry/regeneration整合の是正**(下記Fable判断)と、Personalized News A2の完成(見出し2 segment再検証→Assembly→Gate→player→web export→E2E再生確認→URL)。
- 到達Status: `PRODUCTION_WIRED`(Phase Bの全条件+本是正+Personalized News A2 runtime evidence完備時)/`WIRING_INCOMPLETE`(理由明記)/`USER_DECISION_REQUIRED`(本当に新しい判断が必要な場合のみ)。記事としての最終OKは**ユーザー試聴待ち**(USER_TEST_READY確定扱いにしない)。
- 禁止: Gate緩和、Human Approvalの代行(ASR_VALIDATION_UNCERTAINのまま承認記録しない)、承認済み仕様の変更、新Editorial原則、Trial import、不要なTTS再生成(是正後の正式retry policy内の再生成のみ可)、`git add -A`/`stash`/`amend`/`rebase`/`force push`、wavのcommit。

## Fable判断(PM自律判断方針: 承認済み仕様への整合是正であり新仕様判断ではない)

**事実**: Phase Bの`point_one_heading`/`point_two_heading`は、canonical "One Voice: My morning news route." / "Another Voice: What is missing?" に対しASRが接頭ラベル("One Voice:"/"Another Voice:")を脱落した状態で`ASR_VALIDATION_UNCERTAIN`となり、**attempt1のみでHuman Review Lockへ遷移**(`.../personalized_news_2v_a2/narration/attempts/point_*_heading_attempt1_englishstyleprefix.json`のみ存在)。一方、**承認済み既存A2固定記事経路(free_address、`er012_output/editorial_b_family_voices_a2_production_wiring_01/a2/audit/tts_generation_results.json` L404-456)では同一パターン**(attempt1 "A desk that helps me start."=ASR_VALIDATION_UNCERTAIN)に対し**attempt2でTTS再生成が行われ "One voice, a desk that helps me start."=NORMALIZED_MATCH→status OK**で通過している(Pronunciation Ledgerにも"one voice"/"another voice"が2026-09-07にcascade_unresolved_entityとして登録済み=既知パターン)。
**判断**: 新経路の見出しTTS関数(`generate_narrator_heading_with_a2_slowdown`等、`review_lock.guarded_generate`のラップ方法・retry policy・`max_attempts`・UNCERTAIN時の再生成有無)を、**既存承認済み`main_a2()`経路(free_address)の見出しsegmentが実際に辿ったretry/regeneration policyと同一**に揃える(Production Wiring Checklist「retry/fallback/regeneration整合」の未充足是正。Gate緩和ではなく、承認済み経路との整合)。是正後、見出し2 segmentのみ正式経路で再実行(TTS再生成は正式retry policy内、想定¥5〜10)。NORMALIZED/EXACT_MATCHでOKになれば`assemble`→Gate→`player`→web exportへ進む。正式retry policyを尽くしてもUNCERTAINならHuman Review Lockのまま**STOP**し、当該wavをmp3にexport(API 0)してraw URLを提示(ユーザー試聴判断用)。
**Analytical Leakage残存flag(voice_a 1/voice_b 2、3 attempt上限)**: 既存B1 Personalized News(同じく残存flag付きで`PARTIAL / USER TEST READY`としてユーザー試聴へ回した前例)と同じ扱いとし、記事は再生成せず、Status=`PARTIAL`相当として残存内容を報告に明記(ユーザー試聴時の確認事項に含める)。記事完成をこれでブロックしない。

## 手順

1. T-0(委任文を`docs/pm/delegation_log/PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01-PHASE-B-FIX-01.md`へ保存、`.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file <path> --json-out <path>_check.json`、結果1行記録、FAILでも継続)。
2. 既存承認経路の見出しretry policyの特定: `er012_b_family_production_runner_01.py::run_tts_a2()`(free_address用)と、そこから呼ばれる見出し生成関数(`a2prod.load_a2_sources_for_b_family`/`n3_tts.generate_*`/`review_lock.guarded_generate`の引数、`max_attempts`、UNCERTAIN→再生成の分岐)をGrep→Read。free_addressの`tts_generation_results.json` L404-500のattempt構造(attempt1 UNCERTAIN→attempt2 regen)から実際のpolicyを確認。
3. 新経路`run_tts_a2_2v_new_topic()`/`generate_narrator_heading_with_a2_slowdown()`との差分を特定し、既存policyと同一になるよう最小修正(`er012_b_family_voices_a2_production_01.py`/`er012_b_family_production_runner_01.py`のみ)。既存`main_a2()`・`main_b1_2v()`は無変更。
4. unit test追加(新経路の見出しsegmentが既存経路と同じretry policy[max_attempts/UNCERTAIN時regen]を持つことをmock等で検証)+regression(`er012_*test*.py`全件、`er013_family_c_production_test_01.py`、project regression `run_project_regression.py`)。
5. marker確認→`tts`stage(見出し2 segmentのみ再実行、他segmentは既存OK音声を再利用[再生成しない])→`assemble`→Gate→`player`→web export(`web/episode.mp3`+segments)。**player.html配置**: `user_test/unified.html`の`src`互換のため、player内のaudio相対参照がplayer.htmlの位置基準で正しく解決される配置にする(RESUME-05で判明した不具合: player.htmlを`web/`内に置くと`web/web/episode.mp3`になる。householdと同じく記事dir直下に置く)。
6. E2E再生確認(RESUME-05と同手順、Playwright headless Chromium: 最終SHAのrawcdn unified.html URLでPlay→`currentTime`進行/`paused=false`/`readyState>=3`/`error=null`/seek/script・Key Phrase表示、evidence JSON+png保存。Playwrightは`.venv`に導入済みのはず、無ければ導入可)。
7. URL: `https://rawcdn.githack.com/shimomura055/eigo-radio/<SHA>/user_test/unified.html?src=er012_output/b_family_a2_new_topic_production_01/personalized_news_2v_a2/player.html&level=A2&en=<URL_ENCODED "The News You See, and the News You Miss">&ja=<URL_ENCODED 見えているニュースと、見えていないニュース>`(+raw.githack player.html直URL)。
8. SSOT: CURRENT_SPEC「新規topic A2 Production経路」行のStatusを実測に応じ更新(`PRODUCTION_WIRED`は判定条件全充足時のみ)、retry policy整合の記述を追記。DECISION_LOG 1エントリ(本ID: Fable判断の内容・根拠、是正差分、runtime結果、E2E evidence、Leakage残存の扱い)。OPEN_ITEMS: 新規登録は不要(見出し接頭ラベルASR脱落パターンはOPEN-159[固有名詞・発音基盤]のサブ項目として1行追記、既知パターン2026-09-07/09-17)。PM_GOVERNANCE無変更。
9. Git: 成果物commit(明示add、wav除外、mp3/json/html/png[小]可)→push→SSOT/RESULT_PACKET commit→push。メッセージ`PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01-PHASE-B-FIX-01: 新規topic A2見出しTTS retry policyを承認済み経路と整合+Personalized News A2 episode完成+E2E再生確認`、trailer `Task-ID: PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01-PHASE-B-FIX-01`。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)
E-1: 同一ファイル再読禁止。D-1: Grep→該当行範囲Read(対象関数本体は全文可)。G-1: git出力最小化。F-1: transcript退避不要。T-1: 事前指定外Readは理由をRESULT_PACKETに1行記録。

## 事前指定Read/Grep一覧
- `er012_b_family_production_runner_01.py`: Grep `def run_tts_a2\b|def run_tts_a2_2v_new_topic|guarded_generate|max_attempts|ASR_VALIDATION_UNCERTAIN|heading`
- `er012_b_family_voices_a2_production_01.py`: Grep `def generate_narrator_heading|def generate_narration_wide_margin|def generate_voice_body|guarded_generate|max_attempts|regenerate|uncertain`
- `er011_human_review_lock_01.py`: Grep `def guarded_generate|max_attempts|ASR_VALIDATION_UNCERTAIN|same_signature`(policyの既定値)
- `er003_v1_n3_01_tts_generate.py`: Grep `def generate_narration_snippet_verified_strict|max_attempts|ASR_VALIDATION_UNCERTAIN|retry`(共通TTS retry policyの既定)
- `er012_output/editorial_b_family_voices_a2_production_wiring_01/a2/audit/tts_generation_results.json` L404-600(free_address見出しのattempt履歴)
- `er012_output/b_family_a2_new_topic_production_01/personalized_news_2v_a2/audit/tts_generation_results.json`(見出し2 segmentの現状)、同`narration/attempts/point_*_heading_attempt1_*.json`
- `docs/pm/RESULT_PACKET_NEWS_2EP_RESUME5.md` 1-3節(player配置規約・E2E手順)
- `CURRENT_SPEC.md`: Grep `新規topic A2 Production経路`、`OPEN_ITEMS.md`: Grep `OPEN-159`、`DECISION_LOG.md`: Grep `^## PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01-PHASE-B`
- `docs/pm/PM_BRIEF.md` L135-159

## 報告(`docs/pm/RESULT_PACKET_PN_A2_PHASE_B_FIX1.md`、★★★★報告ここから/ここまで★★★★、累積Full形式)
0. T-0 1. 現在Status 2. retry policy差分(既存経路 vs 新経路、ファイル:行)と是正内容 3. 見出し2 segment再実行結果(attempt数、ASR text/分類、最終status) 4. Assembly/Gate(duration/peak/clipping) 5. player配置・web export・E2E再生evidence(path、数値) 6. URL(unified rawcdn+raw.githack player) 7. Leakage残存flagの内容(voice_a/voice_b各項目の要旨)と扱い 8. regression(件数、新規test) 9. cost(本タスク+Phase B累計、model_id) 10. Git SHA 11. SSOT更新(CURRENT_SPEC行/DECISION_LOG/OPEN-159追記) 12. Production Wiring Checklist(Phase B 15条件の○×) 13. Dangling Reference Check(6項目) 14. 未決事項/ユーザー試聴時の確認事項 15. 無変更証跡(`git status --porcelain er003_*.py er006_*.py er011_*.py er013_*.py`が空[共有ログ差分は別記])/事前指定外Read(理由付き)。ユーザー向け表記は「B1」に統一。

## 管理ID

`USER-TEST-FINAL-AUDIO-BATCH-06`(委任A: Discovery B1/A2+Home robots Status記録)
並行タスクなし。`docs/pm/ACTIVE_TASK.md`は本タスクで上書き、報告は`docs/pm/RESULT_PACKET_UT06_A.md`へ書く(`RESULT_PACKET.md`は上書きしない、後続委任B/Cと分離するため)。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー実検証用episodeの完成優先バッチ。**週間Token利用枠約86%使用済み**のため、新規仕組み開発・横断監査・A/B Trial・複数案生成・Prompt改善・Validator新設・architecture再設計を一切しない。read-only確認は必要最小限。既存音声・Support・SFX・Voice assetを最大限再利用。問題は記事単位・segment単位の個別対応、恒久対策はOpen Item化のみ(実装しない)。
- 到達上限Status: Discovery B1=音声PASSまで(Human Review必要なら`USER_LISTENING_PENDING`)。Discovery A2=音声完成まで、`USER_LISTENING_PENDING`。Family C Home robots A2=`VALIDATED`(Trial成果物Gate 1分類、**APPROVED_FOR_PRODUCTIONではない**、Family C全体のProduction採用判断は未実施)。Home robots B1=`VALIDATED候補/USER_LISTENING_PENDING`(不変)。
- 対象外: Family C 2記事(委任B/C)、Trend/Voices、OPEN-154/155(Status`DEFERRED / USER_DECISION_REQUIRED`を維持、Prompt変更・Trial・PM_GOVERNANCE変更・新Gate追加をしない)、`CURRENT_SPEC.md`(仕様追加なし)、Production経路コードの変更。
- 禁止: Discovery A2本文再生成(530語版はユーザー採用済み)、旧604語版の使用、Home robots A2/B1の音声・テキスト変更(**B1 Support voice Charon化はFIX-05[commit `edd85685`]で完了済み。再TTS・再ASRを行わない**)、Discovery B1本文・Fact変更、`git add -A`/`stash`/`amend`、wavのcommit、Opus使用。
- 費用上限: Part 2(Discovery B1 retry)¥20、Part 3(Discovery A2音声化)¥80。合計¥100。超過見込みならその Partのみ STOP(完了済みPartはcommit)。
- STOP条件(該当Partのみ停止、自動再試行しない): (1)Discovery B1 retryで再び内容ブロック丸ごと欠落(1回で止め、個別対応候補のみ提示)、(2)費用上限超過見込み、(3)Fact意味変更/Story core変更/新正式仕様/大幅Prompt変更が必要、(4)既存仕様同士の明確な衝突、(5)Audio Validation Gate FAIL 2回連続、(6)人間評価が必要。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
(保存名: `docs/pm/delegation_log/USER-TEST-FINAL-AUDIO-BATCH-06_A.md`)

## ユーザー指示(原文)

ユーザー原文(2026-09-15)のうち本委任該当部分を引用:

---
0. 最重要:週間Token Cost Guard。現在、Claude週間利用枠は約86%使用済み。今回の目的は新しい仕組みの開発ではなく、ユーザー実検証用episodeを完成させることである。したがって以下を厳守。不要な横断監査をしない/新規A/B Trialをしない/Opusを使わない/不要な再生成をしない/同じ成果物を複数案生成しない/大規模Prompt改善をしない/Validator新設をしない/Production architecture再設計をしない/read-only確認は必要最小限/既存音声・既存Support・既存SFX・既存Voice assetは最大限再利用/問題は原則記事単位・segment単位の個別対応/恒久対策が必要な問題はOpen Item化して今回実装しない。

1. Discovery B1。現状: Human Reviewの結果、既存音声では以下の内容が欠落していることをユーザーが確認した。欠落部分: 「a study of about 2,500 college students in 11 countries, an everyday activity was enjoyed more than thinking for pleasure. This was true in every country tested. Still, differences between countries were linked with personal factors such as openness, meditation experience, starting mood, and phone use.」したがって既存attemptはHuman Review FAIL。ユーザー判断: TTSをもう1回実行する。実施: 現在確定済みcanonical B1本文を使う。本文・Factを変更せず、full_story_part2を追加再生成。今回ユーザーが明示的に追加retryを承認しているため、Human Review Lockを解除して1回実行してよい。確認: canonical全文が音声に含まれている/特に2,500人 / 11か国研究段落の欠落がない/ASR・canonical・実音声・player表示を照合。PASSしたら、Assembly/Audio Validation/player更新まで完了。STOP: この追加retryでも同じような内容ブロック丸ごと欠落が発生した場合は、自動で何回も再試行しない。その時点でSTOPし、個別対応候補だけ提示。恒久TTS対策は今回行わない。

2. Discovery A2。ユーザー判断: 旧604語版は不採用。現在の530語版はユーザーが許容・採用。したがって記事本文を再生成しない。530語で音声化へ進む。実施: 現在のcanonical: er014_output/four_type_observation_01/discovery/a2/article.md を固定して使用。必要工程: Key Phrase再選定/Canonicalization/Redundancy QA/Support生成/TTS/Assembly/Audio Validation/Web player生成。既存正式A2 episode構成を使用。Word count: 530語なので、500語以上の完成報告義務対象であることを最終REPORTに明記。ただし今回はユーザー承認済みなので、530語を理由に再生成しない。

3. Family C / Home robots A2。ユーザー最終試聴: OK。したがってTrial成果物としてGate 1分類を、VALIDATEDとして記録してよい。注意: APPROVED_FOR_PRODUCTIONではない。Family C全体のProduction採用判断はまだ行われていない。A2は今回一切変更しない。

4. Family C / Home robots B1。ユーザー判断: Preview / Comment 1〜3は、Charon voiceへ修正。現在のAoedeは不採用。RobotもCharonのままでよい。(中略)修正後Status: VALIDATED候補 / USER_LISTENING_PENDING。ユーザー再試聴前にVALIDATED確定しない。

12. STOP条件: 以下の場合のみSTOP。Factの意味を変える必要がある/Story core変更が必要/新しいFamily C正式仕様が必要/大幅なPrompt変更が必要/追加API/Token消費が大きい/同じTTS失敗が規定回数を超えて繰り返す/ユーザーの人間評価が必要/既存仕様同士が明確に衝突。軽微な個別問題で毎回ユーザー判断へ戻さない。

15. Token節約の報告: 最終REPORTで必ず、使用したClaude model/Sonnet委任回数/Opus使用有無/不要な再生成を回避した箇所/再利用した既存asset/API実費を簡潔に報告。

17. Closeout: 各記事ごとに報告: article status/word count/Audio Validation/duration/player URL/direct audio URL/追加費用/再生成回数/個別対応内容/新規Open Item有無/USER_LISTENING_PENDINGかどうか。
---

Fable補足: 項目4はFIX-05(commit `a1ea6df6`/`edd85685`、2026-09-15)で**完了済み**(4 segmentのみCharon再TTS、現物ASR 4/4一致、Audio Validation PASS 395.105秒、¥4.80)。本委任では「完了済みである事実の確認(git logとRESULT_PACKET/REPORTの存在確認のみ、read-only)」と報告への記載だけを行い、作業を重複させない。

## 事前指定Read一覧

- `docs/pm/RESULT_PACKET_FU03_DISCOVERY.md`: 1-30行(Part A/B/C・費用の前回状態。Part C未着手の内訳=Key Phrase再選定・TTS・Assembly・Audio Validation・player・web_delivery.json)
- `USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02_REPORT.md`: Grepで`full_story_part2|attempt|Human Review Lock|review_lock`→該当範囲Read(Discovery B1 part2の過去3attemptの経緯とLock状態)
- `er014_output/four_type_observation_01/discovery/audio/b1b/human_review_diff.json`: Grepで`attempt2`→該当entry範囲Read(欠落なし版attempt2の差分内容。参考: attempt2は欠落なしだが言い回し差あり[six→6等]で不採用だった経緯を確認)
- `er014_output/four_type_observation_01/discovery/`: Glob`run_discovery_*.py`→スクリプト一覧を取得し、B1 part2再TTS用(`run_discovery_fix_b1b_kp.py`等)とA2音声化用(`run_discovery_a2.py`等)のargparse/`__main__`部分のみGrep→範囲Read(全文Read禁止)
- `er014_output/four_type_observation_01/discovery/audio/b1b/audit/review_lock_state.json`(存在すれば全文、小ファイル)
- `er014_output/four_type_observation_01/discovery/production_set_cost.json`: Grepで`fu03_running_total_after_part_b_jpy|production_set_total_cost_including_audio_jpy`→該当行のみ
- `docs/pm/PM_GOVERNANCE.md`: Grepで`15-8`→該当節Read(費用報告形式)、Grepで`9-11`→該当節Read(語数報告義務)
- `docs/pm/PM_BRIEF.md`: 135-159行(ACTIVE_TASK固定ヘッダ)

## 事前指定Grep一覧+追記位置・更新位置の手順

1. Home robots完了確認(read-only): `git log --oneline -6`で`edd85685`/`a1ea6df6`(FIX-05)の存在確認、`Glob FAMILY-C-HOME-ROBOTS-B1-SUPPORT-VOICE-FIX-05_REPORT.md`存在確認。作業なし。
2. Discovery B1 Lock: `Grep pattern="lock|LOCK|human_review" path=er014_output/four_type_observation_01/discovery/audio/b1b/audit/ output_mode=files_with_matches`→Lock状態ファイルを特定し、解除方法(フィールド更新 or スクリプト引数`--unlock`等)をスクリプト側Grep`review_lock|unlock|HUMAN_REVIEW`で特定。解除は「ユーザー明示承認(2026-09-15、USER-TEST-FINAL-AUDIO-BATCH-06 項目1)による1回限り」を理由フィールドに記録。
3. Discovery B1 canonical: `Grep pattern="2,500 college students" path=er014_output/four_type_observation_01/discovery/ glob=*.{json,md,txt}`→canonical part2テキストの所在確認(本文変更なし)。
4. Discovery A2 既存artifact: `Glob er014_output/four_type_observation_01/discovery/audio/a2/**`および`discovery/key_phrases/a2/**`→旧604語版由来のartifactを`discovery/audio/a2_before_regeneration_604w/`・`discovery/key_phrases/a2_before_regeneration_604w/`へ退避(PM_GOVERNANCE 2-3、上書き禁止)してから530語版で生成。Support(Preview/Comment)・Key Phraseは530語版本文に対して再生成が必要(本文が変わっているため旧版流用不可。ただしIntro/Outro/SFX/Notification等の共通assetは既存再利用)。
5. SSOT追記位置: `Grep pattern="^## FAMILY-C-HOME-ROBOTS-B1-SUPPORT-VOICE-FIX-05" path=DECISION_LOG.md`→そのエントリ末尾直後に新エントリ、索引行直後に索引1行。`OPEN_ITEMS.md`はpythonで行末追記(Readツール不可): OPEN-135(Discovery A2)、OPEN-147(Family C: Home robots A2=VALIDATED記録)、OPEN-153(Discovery B1 Human Review→retry結果)。OPEN-154/155は追記しない(Status維持)。
6. `docs/pm/MODEL_ROUTING_TRIAL_LOG.md`末尾: Discovery A2 Support生成・B1 part2 TTSの行を既存形式で追加。

## 実行コマンド全文

作業ディレクトリ`C:\Users\tensh\eigo-radio`、pythonは`.venv\Scripts\python.exe`。

T-0:
```
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\USER-TEST-FINAL-AUDIO-BATCH-06_A.md --json-out docs\pm\delegation_log\USER-TEST-FINAL-AUDIO-BATCH-06_A_check.json
```

Part 1(Home robots記録、¥0): SSOT追記のみ(下記SSOT追記文)。

Part 2(Discovery B1 part2追加TTS 1回、上限¥20): 既存スクリプトでLock解除→`full_story_part2`のみ再TTS(attempt4)→現物ASR→canonical全文包含チェック(特に「a study of about 2,500 college students in 11 countries … phone use.」ブロックがASRに含まれること。difflib語単位でdelete blockが0であること)→PASSならAssembly→Audio Validation→`discovery/audio/b1b/player.html`更新+`human_review_player.html`にattempt4を追加(既定表示=attempt4)。実行例(実スクリプト名・引数はGrep結果で確定し実引数全文を報告):
```
.venv\Scripts\python.exe er014_output\four_type_observation_01\discovery\run_discovery_fix_b1b_kp.py --retry-segment full_story_part2 --unlock-human-review --unlock-reason "USER-TEST-FINAL-AUDIO-BATCH-06 item1 user-approved single retry 2026-09-15" --max-attempts 1
```
STOP条件(1)該当時: attempt4のASR diff(delete block内容)を報告し、個別対応候補(例: part2をさらに2分割してTTS/欠落文のみ別segment生成して結合/attempt2[欠落なし・言い回し差]の言い回し差をcanonical側で許容するか)を3件以内で提示、実装しない。

Part 3(Discovery A2 530語版音声化、上限¥80): `discovery/a2/article.md`固定。Grep 4の退避後、既存A2正式構成のスクリプトでKey Phrase再選定→Canonicalization→Redundancy QA→Support生成(Preview/Comment、既存A2正式言語仕様=日本語)→TTS→Assembly→Audio Validation→player→`web_delivery.json`。実行例(実名・引数はGrep結果で確定):
```
.venv\Scripts\python.exe er014_output\four_type_observation_01\discovery\run_discovery_a2.py --article er014_output\four_type_observation_01\discovery\a2\article.md --stage audio --budget-jpy 80
```
word_count=530(`WORD_COUNT_GE_500`該当、報告義務のみ・再生成しない)。`production_set_cost.json`の`production_set_total_cost_including_audio_jpy`を¥761.14+Part C実費へ更新。

Web到達確認(push後、raw.githackはUser-Agent付きGET、CDN遅延時60秒待ち最大3回):
```
.venv\Scripts\python.exe -c "import urllib.request as u;[print(u.urlopen(u.Request(x,headers={'User-Agent':'Mozilla/5.0'})).status,x) for x in ['https://raw.githack.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/discovery/audio/b1b/player.html','https://raw.githack.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/discovery/audio/a2/player.html']]"
```
episode mp3のdirect URL(B1/A2各1件)は`web_delivery.json`から実ファイル名を取得し同様にGET確認、計4件のstatusを報告。

回帰: Discovery配下にテストがあれば`run_project_regression.py --pattern "er014*_test_*.py"`を1回。無ければ「該当テストなし」と報告(新規テストは作らない)。

## SSOT追記文

`DECISION_LOG.md`(新エントリ、FIX-05エントリ末尾直後):
```
## USER-TEST-FINAL-AUDIO-BATCH-06(委任A: Discovery B1/A2+Home robots Status)

- 日付: 2026-09-15
- 種別: ユーザー実検証用episode完成バッチ(週間Token枠逼迫下、恒久改善・追加Trialなし、Sonnetのみ・Opus不使用)
- Family C Home robots A2 v2: ユーザー最終試聴OK→Trial成果物Gate 1分類=**VALIDATED**(APPROVED_FOR_PRODUCTIONではない。Family C全体のProduction採用判断は未実施)。音声・テキスト無変更。
- Family C Home robots B1: FIX-05(commit edd85685)でSupport voice Charon化完了済み、本バッチで作業なし。Status=VALIDATED候補/USER_LISTENING_PENDING(不変)。
- Discovery B1: Human Reviewで2,500人/11か国研究段落の丸ごと欠落をユーザー確認(attempt1/3)→Human Review FAIL。ユーザー明示承認によりHuman Review Lockを1回限り解除しfull_story_part2をattempt4として再TTS。結果: <PASS(canonical全文包含、delete block 0)/STOP(欠落再発)>。Audio Validation <PASS/FAIL、duration秒>。費用¥<実測>。
- Discovery A2: 旧604語版不採用、530語版(ユーザー採用)を本文固定で音声化(Key Phrase再選定→Canonicalization→Redundancy QA→Support→TTS→Assembly→Audio Validation→player)。word_count=530(WORD_COUNT_GE_500報告義務該当、ユーザー承認済みのため再生成なし)。Audio Validation <PASS/FAIL、duration秒>。費用¥<実測>。Discovery Production 1生成セット総原価=¥761.14+¥<実測>=¥<合計>。Status=USER_LISTENING_PENDING。
- OPEN-154/155: DEFERRED / USER_DECISION_REQUIRED維持、本バッチで変更なし。
- 参照: `docs/pm/RESULT_PACKET_UT06_A.md`、commit <hash>
```
索引1行(FIX-05索引行直後)。

`OPEN_ITEMS.md`行末追記(python):
- OPEN-147: ` 2026-09-15追記(UT-06 A): Home robots A2 v2=ユーザー最終試聴OK→VALIDATED(Trial成果物、Production未採用)。B1はFIX-05完了済み・USER_LISTENING_PENDING。`
- OPEN-153: ` 2026-09-15追記(UT-06 A): Human Review結果=attempt1/3欠落をユーザー確認→FAIL。ユーザー承認でLock1回解除、attempt4再TTS→<結果>。`
- OPEN-135: ` 2026-09-15追記(UT-06 A): 530語版を本文固定で音声化→<結果、duration、費用>。Status=USER_LISTENING_PENDING。`

`docs/pm/ACTIVE_TASK.md`: 固定ヘッダ形式で上書き(管理ID=USER-TEST-FINAL-AUDIO-BATCH-06、報告単位Status: 委任A=<状態>、委任B/C=未着手。UDR-deferred: OPEN-154/155/Discovery B1 Human Review再試聴/Discovery A2試聴/Home robots B1再試聴)。

## Git(明示add対象・コミットメッセージ・trailer)

- Part 2完了時とPart 3完了時で分けてcommitしてよい(各Partの完了単位)。明示add対象(wav除外、mp3必須): `er014_output/four_type_observation_01/discovery/`配下の本タスク更新・新規ファイル(audio/b1b/{player.html,human_review_player.html,human_review_diff.json,web/**/*.mp3,audit/*.json}、audio/a2/**[player.html/web/*.mp3/audit/*.json/web_delivery.json]、audio/a2_before_regeneration_604w/**、key_phrases/a2/**、key_phrases/a2_before_regeneration_604w/**、production_set_cost.json、変更したrunスクリプト)、`DECISION_LOG.md`、`OPEN_ITEMS.md`、`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`、`docs/pm/delegation_log/USER-TEST-FINAL-AUDIO-BATCH-06_A.md`、同`_check.json`、`docs/pm/RESULT_PACKET_UT06_A.md`。
- `er006_output/`・`er011_output/`の既存M、`docs/pm/ACTIVE_TASK_*.md`/`RESULT_PACKET_*.md`の既存??、`er013_output/`は触らない。
- コミットメッセージ: `USER-TEST-FINAL-AUDIO-BATCH-06 (A): Discovery B1 part2 retry(attempt4)+Discovery A2 530語版音声化+Home robots A2 VALIDATED記録`(Partごとに分ける場合は`(A-2)`/`(A-3)`を付ける)
- trailer: `Task-ID: USER-TEST-FINAL-AUDIO-BATCH-06`
- push: `git push origin main`。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_UT06_A.md`(新規)に:
1. T-0結果
2. Part 1: Home robots A2 VALIDATED記録位置、B1 FIX-05完了済み確認結果(commit hash・REPORT存在)
3. Part 2 Discovery B1: Lock解除の方法と記録、attempt4のTTS結果、ASR全文とcanonicalのdiff(delete/insert/replace block一覧、特に2,500人/11か国段落の包含)、PASS/STOP判定、Assembly・Audio Validation(PASS/FAIL、duration)、player/human_review_player更新内容、費用(TTS/ASR/その他)、再生成回数(=1)、STOP時は個別対応候補3件以内
4. Part 3 Discovery A2: 退避先、Key Phrase 5件、Redundancy QA結果、Support(Preview/Comment)生成結果、TTS segment数、Assembly・Audio Validation(PASS/FAIL、duration)、word_count=530(WORD_COUNT_GE_500明記)、費用(LLM/TTS/ASR/その他)、Production 1生成セット総原価更新値、再生成回数
5. 各記事のClosout項目(ユーザー指示17: article status/word count/Audio Validation/duration/player URL/direct audio URL/追加費用/再生成回数/個別対応内容/新規Open Item有無/USER_LISTENING_PENDING)
6. Token節約報告(ユーザー指示15: 使用model=Sonnet、本委任のSonnet委任回数=1、Opus使用なし、不要な再生成を回避した箇所[Home robots B1再TTS回避、Discovery A2本文再生成回避、attempt2再利用検討結果等]、再利用した既存asset、API実費合計)
7. Web到達確認(4 URL status)
8. 回帰結果(または該当なし)
9. commit hash・push結果・残差分要約
10. unresolved issue・新規Open Item候補(症状/原因/今回の個別対応/将来の恒久対応候補の4点のみ、登録は`OPEN_ITEMS.md`末尾に新番号で行い番号を報告。恒久対策は実装しない)
11. 事前指定外Read(理由付き1行ずつ)

ユーザー向け表記は「B1」に統一(「B1B」不使用、内部識別子`b1b`はそのまま)。

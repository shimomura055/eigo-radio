## 管理ID

`USER-TEST-FINAL-AUDIO-BATCH-06`(委任C: Family C「Digital twins」A2+B1)+`USER-TEST-FINAL-AUDIO-BATCH-06-FOLLOWUP-01`項目1(Home robots B1=VALIDATED記録、¥0)
並行タスクなし(委任Bは完了・push済み、commit `ab41d141`)。報告は`docs/pm/RESULT_PACKET_UT06_C.md`(新規)へ。`docs/pm/ACTIVE_TASK.md`は本タスクで上書き可。

## 性質/到達上限Status/禁止事項

- 性質: 委任B(The future of memory、`docs/pm/RESULT_PACKET_UT06_B.md`)と同一方式で、Family C Trial記事「Digital twins」のA2/B1 episodeを音声完成まで持っていく。**委任Bで作成した`er013_family_c_episode_trial_10_memory_run.py`/`_memory_b1_run.py`/`_memory_test_01.py`を複製元として使う**(Home robots用スクリプトからの再複製はしない。memory用スクリプトは編集しない)。1記事完結原則: A2完成→commit→B1完成→commit。
- 到達上限Status: A2/B1とも最大`VALIDATED候補 / Trial / USER_LISTENING_PENDING`。`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`へ昇格しない。
- **本文固定(ユーザー指示)**: `er013_output/family_c_future_trial_08/digital_twins/reader_facing_article.txt`を正本候補として固定。音声化の都合で本文を再生成・書き換えない。明確な誤り(Fact・整合性の明白な誤記)のみ最小限で個別修正し、前後テキスト・理由・sha256前後を記録。本文再生成・新規Writer Trial禁止。B1本文はA2本文をStory coreとしてB1 Writerで独立生成する既存経路(A2本文は不変)。
- 禁止: 新規A/B Trial、複数案生成、Prompt改善、Validator/QA Gate新設、architecture再設計、共通Voice router変更、新Voice探索・Voice比較Trial、新規演出、Comment 4、B1日本語タイトル、B1 Support日本語、B1 Support voice Aoede、Opus使用、`er012_*`/`er003_*`/`er011_*`Production経路の編集、Home robots用・memory用スクリプトの編集、`CURRENT_SPEC.md`編集、`git add -A`/`stash`/`amend`、wavのcommit。
- 費用上限: A2 ¥80、B1 ¥120(合計¥200)。超過見込みならそのlevelのみSTOP(完了分はcommit)。
- STOP条件: Factの意味変更が必要/Story core変更が必要/新しいFamily C正式仕様が必要/大幅Prompt変更が必要/上限超過/同じTTS失敗が既存規定回数(標準2+fallback1)を超えて繰り返す/人間評価が必要/既存仕様同士の明確な衝突。**軽微な個別問題(TTS読み飛ばし・ASR表記揺れ・Voice assignment例外・Support軽微不整合・Story区切り・特定文の発音・player表示不一致・Trial scriptの非冪等性)は既存仕様範囲で最小の個別修正を行い進める。毎回ユーザー判断へ戻さない。**恒久対策はOpen Item化(症状/原因/今回の個別対応/将来の恒久対応候補の4点)し実装しない。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
(保存名: `docs/pm/delegation_log/USER-TEST-FINAL-AUDIO-BATCH-06_C.md`)

## ユーザー指示(原文)

ユーザー原文(2026-09-15、USER-TEST-FINAL-AUDIO-BATCH-06 項目5〜12・15・17)は委任B(`docs/pm/delegation_log/USER-TEST-FINAL-AUDIO-BATCH-06_B.md`「ユーザー指示(原文)」節)と同一。本委任ではそれをそのまま適用する(Read一覧に含める)。追加のユーザー原文(FOLLOWUP-01、2026-09-15):

---
1. Family C / Home robots B1: ユーザーが再試聴し、OKと判断しました。したがってGate 1分類を、VALIDATEDへ更新してください。注意: Trial成果物としてVALIDATED/APPROVED_FOR_PRODUCTIONではない/Family C全体のProduction採用判断ではない/A2も既にVALIDATED済み。必要な範囲でDECISION_LOG / OPEN_ITEMS / REPORTへ反映してください。Home robots A2/B1への追加修正・再TTSは不要です。

3. Family C残り2記事: 既存方針を維持。Trial-08 reader_facing_article.txtを正本候補として固定/Writer再実行しない/音声化の都合で本文を書き換えない/明確な誤りだけ最小個別修正/恒久対策はOpen Item化/新規architecture / Validator / Prompt principleを作らない/A2/B1とも試聴可能なepisodeまで完成させる。到達上限: VALIDATED候補 / USER_LISTENING_PENDING。ユーザー試聴前にVALIDATED確定しない。

7. Token / Cost Guard: Opus禁止/不要な再生成禁止/不要な横断監査禁止/同一記事の複数候補生成禁止/既存asset再利用/個別segment対応優先。
---

## 事前指定Read一覧

- `docs/pm/delegation_log/USER-TEST-FINAL-AUDIO-BATCH-06_B.md`: 「ユーザー指示」節のみ(Grepで`## ユーザー指示`→次の`## `まで)
- `docs/pm/RESULT_PACKET_UT06_B.md`: 全文(委任Bの手順・Voice割当・Comment位置決定・個別対応・費用の前例。本委任はこれを踏襲)
- `er013_output/family_c_future_trial_08/digital_twins/reader_facing_article.txt`: 全文(正本候補、固定)
- `er013_output/family_c_future_trial_08/digital_twins/{word_count.json,safety_result.json,core_idea.json}`: 全文
- `er013_family_c_episode_trial_10_memory_run.py`: 1-120行(設定定数ブロック)、Grepで`memory|Lena|brother|screen|storage|記憶の未来|classify_quote_voice`→記事固有箇所を全て特定し範囲Read(複製後に差し替える箇所の網羅が目的。構造は委任Bで確立済みのため全文Read不要)
- `er013_family_c_episode_trial_10_memory_b1_run.py`: 1-120行、Grepで`memory|Lena|brother|screen|storage|robot|storage unit|import er013_family_c_episode_trial_10_memory_run|a2m`→同上
- `er013_family_c_episode_trial_10_memory_test_01.py`: 全文(複製してtwins用に差し替え)
- `er013_output/family_c_episode_trial_09/home_robots_v2/spec/episode_spec_v2.md`: 全文(Comment位置決定原則)
- `docs/pm/PM_BRIEF.md`: 135-159行(ACTIVE_TASK固定ヘッダ)

## 事前指定Grep一覧+追記位置・更新位置の手順

1. 既存asset確認: `Glob er013_output/**/digital_twins*/**/*.{wav,mp3}`、`Grep pattern="digital twin" path=er013_output/ glob=*.{json,md} output_mode=files_with_matches -i`→再利用可能なSupport/Key Phrase/音声assetの有無(委任Bと同様、無ければ新規生成)。
2. 登場人物・直接発話: `Grep pattern="“|”|\"" path=er013_output/family_c_future_trial_08/digital_twins/reader_facing_article.txt output_mode=content`→話者分類(主人公の女性/digital twin/その他)。Voice割当は委任Bの設計を踏襲: narrator=Aoede(主人公の地の文・台詞)、**digital twin=既存承認Voiceから1つ選択(既定: Erinome。理由: narratorのAoedeと明確に区別でき、Charonは装置・Support voiceの慣例に使用中のため。twinが「機械的存在」として描かれ装置voiceが適切と判断する場合のみCharonでも可。選択理由を1行記録、Voice比較Trialはしない)**、その他人物がいれば残りの承認Voice。割当表を`speaker_map.json`と報告に記録。引用符なしの機械表示文があれば個別に話者指定(汎用機構は作らない)。
3. Comment位置: `episode_spec_v2.md`の原則に従い、本Storyの段落構造からComment 1(Full story intro直後、固定)・Comment 2(中盤の転換点)・Comment 3(後半、結末を先に言わない)を決定し`comment_placement.json`に理由付きで記録。
4. スクリプト作成: memory用3ファイルを複製して`er013_family_c_episode_trial_10_twins_run.py`/`er013_family_c_episode_trial_10_twins_b1_run.py`/`er013_family_c_episode_trial_10_twins_test_01.py`を作成。差し替えは設定(ARTICLE_PATH=`er013_output/family_c_future_trial_08/digital_twins/reader_facing_article.txt`、OUT_DIR=`er013_output/family_c_episode_trial_10/twins_a2`/`twins_b1`、ARTICLE_ID=`family_c_twins_trial_10`/`..._b1`、日本語タイトル=theme名の直訳1件登録[例「デジタルツイン」、LLM不使用]、Voice割当・`classify_quote_voice`のキーワード[本記事の登場人物呼称]、Comment位置)に限定。B1スクリプトのimport先を新A2スクリプトへ差し替え。memory固有の個別対応(`"robot"/"storage unit"`キーワード)は本記事に不要なら除去し、本記事用の呼称に置き換える。
5. B1 Support 4 segment(Preview/Comment 1〜3)はCharon経路で生成し、`tts_generation_results.json`・player表示に`Charon(support)`が記録されること。再実行が必要になった場合は再生成segmentのASRを現物で取り直す(名前キャッシュ盲信禁止)。
6. 語数報告: A2が280語以下/500語以上なら`WORD_COUNT_LE_280`/`WORD_COUNT_GE_500`として明記(再生成しない)。B1は目安約400語比の%を報告(超過しても再生成しない)。
7. Home robots B1 VALIDATED記録(¥0、FOLLOWUP-01): `Grep pattern="^## USER-TEST-FINAL-AUDIO-BATCH-06(委任B" path=DECISION_LOG.md`→そのエントリ末尾直後に下記FOLLOWUP-01エントリを追加(索引1行も)。`OPEN_ITEMS.md`OPEN-147行末にpythonで追記。`FAMILY-C-HOME-ROBOTS-B1-SUPPORT-VOICE-FIX-05_REPORT.md`の「final status」節末尾に1行追記(「2026-09-15 ユーザー再試聴OK→VALIDATED(Trial成果物、Production未採用)」)。Home robots音声・スクリプトは触らない。
8. 委任C SSOT: FOLLOWUP-01エントリの直後に「委任C」エントリ追加(索引1行も)。`OPEN_ITEMS.md`OPEN-147行末追記。新規Open Itemが必要なら末尾に新番号(既存最大番号をGrep`^\| OPEN-1[0-9][0-9]`で確認)で4点のみ。委任Bで記録した恒久対応候補2点(B1装置呼称のWriter非保証/B1語数目安の正式値未確定)が本記事でも再現した場合は、同じ候補として件数を追記するだけにする(新番号を乱立させない)。
9. `docs/pm/MODEL_ROUTING_TRIAL_LOG.md`末尾に本記事の行を既存形式で追加。

## 実行コマンド全文

作業ディレクトリ`C:\Users\tensh\eigo-radio`、pythonは`.venv\Scripts\python.exe`。

T-0:
```
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\USER-TEST-FINAL-AUDIO-BATCH-06_C.md --json-out docs\pm\delegation_log\USER-TEST-FINAL-AUDIO-BATCH-06_C_check.json
```

A2(上限¥80、memory用と同じ引数体系):
```
.venv\Scripts\python.exe er013_family_c_episode_trial_10_twins_run.py --budget-jpy 80
```
B1(上限¥120、A2完成・commit後):
```
.venv\Scripts\python.exe er013_family_c_episode_trial_10_twins_b1_run.py --budget-jpy 120
```
(memory用スクリプトの実際のargparseに合わせて実引数を確定し全文報告。工程は委任Bと同一。)

TTS失敗時: 既存retry cascade(標準2+fallback1)内で自動処理。それでも不合格のsegmentがあれば、句読点/表記揺れのみ(NORMALIZED_MATCH)なら既存Gate判定に従い、意味差がある場合のみSTOP条件「規定回数超過」として当該levelを停止し、失敗segmentのcanonical/ASR diffを報告(自動で追加retryしない)。

回帰:
```
.venv\Scripts\python.exe run_project_regression.py --pattern "er013_family_c_episode_trial_10_twins*_test_*.py"
```
memory用・Home robots用テストは本タスクで触っていないため再実行不要。

Web到達確認(各commit・push後、raw.githackはUser-Agent付きGET、CDN遅延時60秒待ち最大3回):
```
.venv\Scripts\python.exe -c "import urllib.request as u;[print(u.urlopen(u.Request(x,headers={'User-Agent':'Mozilla/5.0'})).status,x) for x in ['https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_10/twins_a2/player.html','https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_10/twins_b1/player.html']]"
```
episode mp3 direct URL(A2/B1各1件、`web_delivery.json`の実ファイル名)も同様にGET確認、計4件のstatusを報告。

## SSOT追記文

`DECISION_LOG.md`(委任Bエントリ末尾直後):
```
## USER-TEST-FINAL-AUDIO-BATCH-06-FOLLOWUP-01(Home robots B1 VALIDATED記録)

- 日付: 2026-09-15
- ユーザー判断: Family C Home robots B1(FIX-05 Support voice Charon版)をユーザーが再試聴しOK→Trial成果物Gate 1分類=**VALIDATED**(APPROVED_FOR_PRODUCTIONではない。Family C全体のProduction採用判断ではない。A2 v2も既にVALIDATED)。追加修正・再TTSなし(¥0)。
- 作業順序のユーザー判断: Family C残り2記事(memory/digital twins)完成→Discovery B1(part2を意味単位で2 segment分割、個別対応)→Discovery A2(NG 2 segmentのみ追加retry、2,557正読必須)。Family C完成前にDiscoveryを割り込ませない。
- 参照: `FAMILY-C-HOME-ROBOTS-B1-SUPPORT-VOICE-FIX-05_REPORT.md`、`docs/pm/RESULT_PACKET_UT06_C.md`
```
続けて:
```
## USER-TEST-FINAL-AUDIO-BATCH-06(委任C: Family C「Digital twins」A2+B1)

- 日付: 2026-09-15
- 種別: Family C Trial記事のepisode完成(ユーザー実検証用、Home robots確認済み構成、Trial・Production正式仕様ではない)
- 本文: Trial-08 `digital_twins/reader_facing_article.txt`を正本候補として固定。再生成・書き換え<なし/明確な誤り1件を最小修正: 前後テキスト・理由>。A2本文sha256 <値>。
- A2: 語数<n>(<WORD_COUNT_*該当/非該当>)、Voice割当<表>、Comment 1〜3位置<要約>、Comment 4なし、日本語タイトル「<訳>」、Audio Validation <PASS/FAIL、duration秒>、再生成回数<n>、個別対応<内容/なし>、費用¥<実測>。Status=VALIDATED候補/Trial/USER_LISTENING_PENDING。
- B1: 語数<n>(目安約400語比<±n%>)、Support=easy English/Charon、日本語タイトルなし、Comment 4なし、Audio Validation <PASS/FAIL、duration秒>、再生成回数<n>、個別対応<内容/なし>、費用¥<実測>。Status=VALIDATED候補/Trial/USER_LISTENING_PENDING。
- 新規Open Item: <なし/OPEN-xxx(4点)>
- 費用合計¥<実測>。Family C累計¥<委任B後の値>+¥<実測>=¥<合計>。
- 参照: `docs/pm/RESULT_PACKET_UT06_C.md`、commit <A2 hash>/<B1 hash>
```
索引2行。`OPEN_ITEMS.md` OPEN-147行末: ` 2026-09-15追記(FOLLOWUP-01): Home robots B1=ユーザー再試聴OK→VALIDATED(Trial成果物、Production未採用)。A2/B1ともVALIDATED。 2026-09-15追記(UT-06 C): Digital twins A2/B1完成(<結果>)、Status=VALIDATED候補/USER_LISTENING_PENDING、費用¥<実測>、Family C累計¥<合計>。本文はTrial-08正本固定<・修正なし/・最小修正1件>。`
`docs/pm/ACTIVE_TASK.md`: 固定ヘッダ形式で上書き(報告単位Status: 委任A=USER_DECISION済み・Discovery個別対応はFamily C完了後、委任B=完了/USER_LISTENING_PENDING、委任C=<状態>、Home robots A2/B1=VALIDATED)。

## Git(明示add対象・コミットメッセージ・trailer)

- A2完成時とB1完成時で分けてcommit(FOLLOWUP-01のSSOT記録はA2 commitに同梱可)。明示add対象(wav除外、mp3必須): 新規スクリプト2件+テスト1件、`er013_output/family_c_episode_trial_10/twins_a2/`・`twins_b1/`配下(委任Bと同種のファイル)、`DECISION_LOG.md`、`OPEN_ITEMS.md`、`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`、`FAMILY-C-HOME-ROBOTS-B1-SUPPORT-VOICE-FIX-05_REPORT.md`、`docs/pm/delegation_log/USER-TEST-FINAL-AUDIO-BATCH-06_C.md`、同`_check.json`、`docs/pm/RESULT_PACKET_UT06_C.md`。
- `er006_output/`・`er011_output/`の既存M、`docs/pm/ACTIVE_TASK_*.md`/`RESULT_PACKET_*.md`の既存??、`home_robots*/`・`memory_*/`・`er014_output/`は触らない。
- コミットメッセージ: `USER-TEST-FINAL-AUDIO-BATCH-06 (C-A2): Family C digital twins A2 episode完成(Trial-08本文固定)+Home robots B1 VALIDATED記録` / `USER-TEST-FINAL-AUDIO-BATCH-06 (C-B1): Family C digital twins B1 episode完成(Support easy English/Charon)`
- trailer: `Task-ID: USER-TEST-FINAL-AUDIO-BATCH-06`
- push: 各commit後`git push origin main`。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_UT06_C.md`に委任Bと同じ12項目(T-0/既存asset/本文固定証跡/A2結果/B1結果/Closeout項目[ユーザー指示17]/Token節約報告[ユーザー指示15]/Web到達確認/回帰/commit・push/unresolved issue・新規Open Item/事前指定外Read)+FOLLOWUP-01記録の反映位置(DECISION_LOG行、OPEN-147、REPORT追記行)。B1 Preview/Comment 1〜3の全文とdigital twinのVoice選択理由を必ず含める。

ユーザー向け表記は「B1」に統一(「B1B」不使用)。
</content>
</invoke>

## 管理ID

`USER-TEST-FINAL-AUDIO-BATCH-06`(委任B: Family C「The future of memory」A2+B1)
並行タスクなし(委任Aは完了・push済み、commit `9d4dc12d`)。報告は`docs/pm/RESULT_PACKET_UT06_B.md`(新規)へ。`docs/pm/ACTIVE_TASK.md`は本タスクで上書き可。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー実検証用Trial episodeの完成優先(週間Token枠約86%使用済み)。Family C Trial記事「The future of memory」のA2 episodeとB1 episodeを、Home robotsでユーザーが確認したFamily C構成で音声完成まで持っていく。**1記事完結原則: A2完成→commit→B1完成→commit**。
- 到達上限Status: A2/B1とも最大`VALIDATED候補 / Trial / USER_LISTENING_PENDING`。`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`へ昇格しない(Family CはTrial、Production正式仕様と誤認しない)。
- **本文固定(ユーザー指示、2026-09-15追加)**: `er013_output/family_c_future_trial_08/memory/reader_facing_article.txt`を正本候補として固定。音声化の都合(TTS読み飛ばし・ASR揺れ・segment分割・Voice割当等)を理由に本文を再生成・書き換えない。明確な誤り(Fact・整合性の明白な誤記)が見つかった場合のみ、その箇所を最小限で個別修正し、修正前後テキスト・理由・本文sha256前後をRESULT_PACKETに記録。本文再生成・新規Writer Trial・Local Rewrite以外の書き換えは禁止。B1本文はHome robots B1と同じく「A2本文をStory coreとしてB1 Writerで独立生成」する既存経路を使う(これはB1版の生成であり、A2本文の書き換えではない。A2本文は不変)。
- 禁止: 新規A/B Trial、複数案生成、Prompt改善、Validator/QA Gate新設、Production architecture再設計、共通Voice router変更、新Voice探索・Voice比較Trial、新規演出(Intro/Outro/SFX/pauseはFamily A既存正式assetをHome robotsと同様に再利用)、Comment 4、B1日本語タイトル、B1 Support日本語、Support voice Aoede(B1)、Opus使用、`er012_*`/`er003_*`/`er011_*`Production経路の編集、`er013_family_c_episode_trial_09b_run.py`/`_b1_run.py`(Home robots用)の編集(複製して記事用に設定差し替えは可)、`CURRENT_SPEC.md`編集、`git add -A`/`stash`/`amend`、wavのcommit。
- 費用上限: A2 ¥80、B1 ¥120(合計¥200)。超過見込みならその levelのみSTOP(完了分はcommit)。
- STOP条件(ユーザー指示12): Factの意味変更が必要/Story core変更が必要/新しいFamily C正式仕様が必要/大幅Prompt変更が必要/追加API消費が大きい(上限超過)/同じTTS失敗が既存規定回数(標準2+fallback1=3回)を超えて繰り返す/人間評価が必要/既存仕様同士が明確に衝突。**軽微な個別問題(TTS読み飛ばし・ASR表記揺れ・Voice assignment例外・Support軽微不整合・Story区切り・特定文の発音・player表示不一致・Trial scriptの非冪等性)は既存仕様範囲で最小の個別修正を行い進める。毎回ユーザー判断へ戻さない。**恒久対策が必要なものはOpen Item化(症状/原因/今回の個別対応/将来の恒久対応候補の4点のみ)し実装しない。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
(保存名: `docs/pm/delegation_log/USER-TEST-FINAL-AUDIO-BATCH-06_B.md`)

## ユーザー指示(原文)

ユーザー原文(2026-09-15)の本委任該当部分:

---
0. 最重要:週間Token Cost Guard。(中略)不要な横断監査をしない/新規A/B Trialをしない/Opusを使わない/不要な再生成をしない/同じ成果物を複数案生成しない/大規模Prompt改善をしない/Validator新設をしない/Production architecture再設計をしない/read-only確認は必要最小限/既存音声・既存Support・既存SFX・既存Voice assetは最大限再利用/問題は原則記事単位・segment単位の個別対応/恒久対策が必要な問題はOpen Item化して今回実装しない。Family C残り2記事を完成させることを優先し、Tokenを温存する。

5. Family C 残り2記事。対象: The future of memory/Digital twins。Trial-08でユーザー検証候補として選ばれていた2記事。今回、この2本を音声完成episodeまで持っていく。

6. 既存資産の再利用。最初にRepoを確認し、Trial-08記事本文/canonical candidate/Ledger / research/Support/Key Phrase/audio assetが既に存在する場合は最大限再利用する。既存記事本文が使用可能なら、新たにWriterで作り直さない。Fact上の問題や明確な不整合がない限り、既存Trial-08 candidate textをベースに進める。Token・API費用を節約する。

7. Family C episode構成。Home robotsで今回ユーザーが確認したFamily C構成を、残り2記事にも適用する。ただしFamily CはまだTrialであり、Production正式仕様と誤認しない。構成: Intro/Welcome/English Title/A2の場合は既存A2構成に従った日本語タイトル/Preview/Key Phrase/Story/Comment 1/Comment 2/Comment 3/Comment 4なし/Outro/既存SFX/既存pause。Intro / Outro / SFX / pause等はFamily A既存正式episode assetを可能な限り再利用。新規演出を作らない。

8. Comment位置。Family CのComment位置はsegment番号固定ではない。Storyごとに、semantic break/scene transition/turning point/前後text volume/前後audio durationを見て自然な位置へ配置。目的はStory理解補助。過剰な解説・研究記事化は禁止。Comment 1〜3のみ。

9. A2 / B1 Support言語。A2: 既存A2正式episode仕様に従う。Preview / Comment等はA2側の正式言語仕様を使用。B1: B1 Supportは、easy Englishを使用。Preview = English/Comment 1〜3 = English/日本語タイトルなし/Comment 4なし。Support voiceは既存B1正式仕様に従い、Charonを使用。今回Home robotsでユーザーが再確認した方針を維持。

10. Character Voice。Story中に複数人物が登場する場合は、Home robots同様、明確な直接発話は可能な範囲で人物Voiceを分離する。ただし、新Voice探索/Voice比較Trial/大規模Voice最適化はしない。既存4Voice候補・既存承認Voiceから選ぶ。問題があれば記事単位で個別対応。恒久Voice routing改善はOpen Item化。

11. Family Cで問題が起きた場合。今回の基本方針: 完成優先。恒久改善は後回し。(TTS読み飛ばし/ASR表記揺れ/Voice assignment例外/Support生成の軽微な不整合/Story区切り/特定文の発音/player表示不一致/Trial scriptの非冪等性)まず既存仕様範囲で最小の個別修正を行う。その修正でepisodeを完成できるなら進めてよい。恒久化禁止: 新Validator/新retry policy/新Prompt原則/Family C Production architecture/共通Voice router変更/Production-wide normalization/新しいQA Gate。Open Item登録時は、症状/原因/今回の個別対応/将来の恒久対応候補だけ残す。

12. STOP条件(上記「性質」欄に転記済み)。軽微な個別問題で毎回ユーザー判断へ戻さない。

15. Token節約の報告(使用model/Sonnet委任回数/Opus使用有無/不要な再生成を回避した箇所/再利用した既存asset/API実費)。

17. Closeout: 各記事ごとに報告: article status/word count/Audio Validation/duration/player URL/direct audio URL/追加費用/再生成回数/個別対応内容/新規Open Item有無/USER_LISTENING_PENDINGかどうか。

追加指示(2026-09-15): 委任B/Cでは、既存Trial-08のreader_facing_article.txtを正本候補として固定し、音声化の都合だけで本文を再生成・書き換えないでください。明確な誤りが見つかった場合のみ、その箇所を最小限で個別修正してください。恒久対策が必要な問題は今回は実装せずOpen Item化し、本文再生成や新規Writer Trialには進まないでください。
---

## 事前指定Read一覧

- `er013_output/family_c_future_trial_08/memory/reader_facing_article.txt`: 全文(正本候補、固定)
- `er013_output/family_c_future_trial_08/memory/{word_count.json,safety_result.json,core_idea.json}`: 全文(小ファイル。語数・Fact Safety結果・Core Provocation)
- `er013_output/family_c_episode_trial_09/home_robots_v2/spec/episode_spec_v2.md`: 全文(Family C構成・Comment位置決定原則の記録、ユーザー確認済み構成の正本)
- `er013_family_c_episode_trial_09b_run.py`: 1-70行(ヘッダ・定数: ARTICLE_PATH/OUT_DIR/ARTICLE_ID/Voice名/コスト単価)、Grepで`def main|argparse|add_argument`→main/argparse範囲、Grepで`speaker_map|def assign_speaker|ROBOT|MOTHER|Maya`→話者判定・Voice割当ロジック範囲、Grepで`COMMENT_NUMBERS|comment_placement|def place_comments|semantic`→Comment位置決定ロジック範囲、Grepで`JAPANESE_TITLE|TOPIC_INTRO|def build_timeline|seq.append`→timeline構築範囲(全文Read禁止、構造把握はGrep→範囲Read)
- `er013_family_c_episode_trial_09b_b1_run.py`: 1-120行(ヘッダ・定数・role定数)、Grepで`--drop-japanese-title|--comments-en|--preview-en|--support-voice-charon|--keep-robot-audio|--fix-robot-choice`→各フラグ実装範囲(新スクリプトではこれらを**既定動作**として組み込む: 日本語タイトルなし・Preview/Comment英語・Support voice Charon)、Grepで`PREVIEW_ROLE_EN|COMMENT_ROLES|er003_v1_b1_scaffold_01_generate`→B1 Support role範囲、Grepで`def stage_writer_and_safety|reference_article|story core`→B1本文独立生成範囲
- `docs/pm/RESULT_PACKET_FU03_FAMILYC_B1.md`: 73-110行(B1 timeline構成・成果物パス)
- `docs/pm/RESULT_PACKET.md`(FIX-05): 1-30行(Charon経路の実装関数`v2run.tts_robot`とASRキャッシュbypassの要点)
- `docs/pm/PM_GOVERNANCE.md`: Grepで`15-8`→該当節、Grepで`9-11`→該当節(語数報告義務: A2が280語以下/500語以上なら明記)
- `docs/pm/PM_BRIEF.md`: 135-159行(ACTIVE_TASK固定ヘッダ)

## 事前指定Grep一覧+追記位置・更新位置の手順

1. 既存asset確認(ユーザー指示6): `Glob er013_output/family_c_future_trial_08/memory/**`(既読)、`Glob er013_output/**/memory*/**/*.{wav,mp3}`および`Grep pattern="future of memory|Lena" path=er013_output/ glob=*.{json,md} output_mode=files_with_matches`→既存のSupport/Key Phrase/音声assetの有無を確認(存在すれば再利用、無ければ新規生成)。結果を報告。
2. 登場人物・直接発話の把握: `Grep pattern="“|”|\"" path=er013_output/family_c_future_trial_08/memory/reader_facing_article.txt output_mode=content`→引用符付き発話の話者(Lena本人/兄/記憶保管装置の画面等)を分類。Voice割当はHome robots設計を踏襲: Narrator=Aoede(主人公Lenaの台詞は地の文と同様narrator扱い、Home robotsのMaya台詞設計と同じ)、装置・機械音声=Charon(Robotと同型)、他人物(兄など)=Erinome等の既存承認Voice。既存4 Voice候補以外を使わない。割当表を`speaker_map.json`と報告に記録。引用符なしの機械/装置表示文(Home robots `story_017`型)があれば個別に話者指定(汎用機構は作らない)。
3. Comment位置(ユーザー指示8): `episode_spec_v2.md`の原則(semantic break/scene transition/turning point/前後text volume/前後audio duration)に従い、本Storyの段落構造からComment 1(導入直後)・Comment 2(中盤の転換点)・Comment 3(後半、結末を先に言わない)の挿入位置を決定し、`comment_placement.json`に理由付きで記録。Home robotsのsegment番号を流用しない。
4. スクリプト作成: `er013_family_c_episode_trial_09b_run.py`を複製して`er013_family_c_episode_trial_10_memory_run.py`(A2)、`er013_family_c_episode_trial_09b_b1_run.py`を複製して`er013_family_c_episode_trial_10_memory_b1_run.py`(B1)を作成。差し替えは設定(ARTICLE_PATH=`er013_output/family_c_future_trial_08/memory/reader_facing_article.txt`、OUT_DIR=`er013_output/family_c_episode_trial_10/memory_a2`/`memory_b1`、ARTICLE_ID=`family_c_memory_trial_10`/`..._b1`、Voice割当、日本語タイトル=既存A2規約どおり原文タイトル直訳を1件登録、Comment位置、Home robots固有の固定文override[Comment 3固定文・Robot二人称文]の除去)と、FIX-04/05で追加したB1修正の既定化に限定。Home robots用スクリプトは編集しない。B1スクリプトが`v2run`をimportしている構造は、新A2スクリプトをimportするよう差し替え。
5. Voice evidence/ASR: B1 Support 4 segment(Preview/Comment 1〜3)はCharon経路(`tts_robot`相当)で生成し、`tts_generation_results.json`・player表示に`Charon(support)`が記録されること。名前ベースASRキャッシュは新規OUT_DIRのため初回は空だが、再実行が必要になった場合は再生成segmentのASRを現物で取り直す(キャッシュ盲信禁止)。
6. 語数報告: A2本文の語数(`word_count.json`)が280語以下または500語以上なら`WORD_COUNT_LE_280`/`WORD_COUNT_GE_500`として報告(報告義務のみ、再生成しない)。B1は目安約400語超過時に%を報告。
7. SSOT追記位置: `Grep pattern="^## USER-TEST-FINAL-AUDIO-BATCH-06" path=DECISION_LOG.md`→委任Aエントリ末尾直後に「委任B」エントリ追加(索引1行も)。`OPEN_ITEMS.md`はpythonで行末追記: OPEN-147(Family C全体)に「memory A2/B1完成、Status、費用」。新規Open Itemが必要な場合は末尾に新番号(OPEN-156以降、既存最大番号をGrep`^\| OPEN-1[0-9][0-9]`で確認)で4点のみ記載。
8. `docs/pm/MODEL_ROUTING_TRIAL_LOG.md`末尾に本記事のA2 Support/B1 Writer/B1 Supportの行を既存形式で追加。

## 実行コマンド全文

作業ディレクトリ`C:\Users\tensh\eigo-radio`、pythonは`.venv\Scripts\python.exe`。

T-0:
```
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\USER-TEST-FINAL-AUDIO-BATCH-06_B.md --json-out docs\pm\delegation_log\USER-TEST-FINAL-AUDIO-BATCH-06_B_check.json
```

A2(上限¥80):
```
.venv\Scripts\python.exe er013_family_c_episode_trial_10_memory_run.py --budget-jpy 80
```
(複製元のargparseに合わせて実引数を確定し全文報告。工程: 本文固定→normalize→話者判定/Voice割当→Key Phrase選定・正規化→Support[Preview/Comment 1〜3、A2正式言語=日本語、Aoede]→日本語タイトル→TTS→Comment位置決定→Assembly[Intro/Welcome/English Title/Japanese Title/Preview/Key Phrase/Story/Comment1-3/Outro、既存SFX・pause]→Audio Validation→player→web_delivery.json。)

B1(上限¥120、A2完成・commit後):
```
.venv\Scripts\python.exe er013_family_c_episode_trial_10_memory_b1_run.py --budget-jpy 120
```
(工程: A2本文をStory coreとしてB1 Writer独立生成[既存経路、Fact Safety/Story core check含む]→Key Phrase→Support[Preview/Comment 1〜3、easy English、Charon]→TTS[Narrator/人物Voice分離、A2と同一割当]→Comment位置→Assembly[英語タイトルのみ、日本語タイトルなし、Comment 4なし]→Audio Validation→player→web_delivery.json。)

TTS失敗時: 既存retry cascade(標準2+fallback1)内で自動処理。それでも不合格のsegmentがあれば、句読点/表記揺れのみ(NORMALIZED_MATCH)なら既存Gateの判定に従い、意味差がある場合のみSTOP条件「規定回数超過」として当該levelを停止し、失敗segmentのcanonical/ASR diffを報告(自動で追加retryしない)。

回帰: 新規テスト`er013_family_c_episode_trial_10_memory_test_01.py`(A2: Comment 4不在・日本語タイトル存在・Story本文sha256=正本一致、B1: 日本語タイトル不在・Comment/Previewに日本語なし・Support voice=Charon、計6件程度、Home robots用テストの複製で可)を作成し:
```
.venv\Scripts\python.exe run_project_regression.py --pattern "er013_family_c_episode_trial_10*_test_*.py"
```
Home robotsテスト(`trial_09*`)は本タスクで触っていないため再実行不要。

Web到達確認(各commit・push後、raw.githackはUser-Agent付きGET、CDN遅延時60秒待ち最大3回):
```
.venv\Scripts\python.exe -c "import urllib.request as u;[print(u.urlopen(u.Request(x,headers={'User-Agent':'Mozilla/5.0'})).status,x) for x in ['https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_10/memory_a2/player.html','https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_10/memory_b1/player.html']]"
```
episode mp3 direct URL(A2/B1各1件、`web_delivery.json`の実ファイル名)も同様にGET確認、計4件のstatusを報告。

## SSOT追記文

`DECISION_LOG.md`(委任Aエントリ末尾直後):
```
## USER-TEST-FINAL-AUDIO-BATCH-06(委任B: Family C「The future of memory」A2+B1)

- 日付: 2026-09-15
- 種別: Family C Trial記事のepisode完成(ユーザー実検証用、Home robots確認済み構成を適用、Trial・Production正式仕様ではない)
- 本文: Trial-08 `memory/reader_facing_article.txt`を正本候補として固定(ユーザー指示)。再生成・書き換え<なし/明確な誤り1件を最小修正: 前後テキスト・理由>。A2本文sha256 <前>→<後>。
- A2: 語数<n>(<WORD_COUNT_*該当/非該当>)、Voice割当<表>、Comment 1〜3位置<segment/理由要約>、Comment 4なし、日本語タイトル「<訳>」、Audio Validation <PASS/FAIL、duration秒>、再生成回数<n>、個別対応<内容/なし>、費用¥<実測>。Status=VALIDATED候補/Trial/USER_LISTENING_PENDING。
- B1: 語数<n>(目安約400語比<±n%>)、Support=easy English/Charon、日本語タイトルなし、Comment 4なし、Audio Validation <PASS/FAIL、duration秒>、再生成回数<n>、個別対応<内容/なし>、費用¥<実測>。Status=VALIDATED候補/Trial/USER_LISTENING_PENDING。
- 新規Open Item: <なし/OPEN-xxx(症状/原因/今回の個別対応/将来の恒久対応候補)>
- 費用合計¥<実測>(A2¥<x>+B1¥<y>)。Family C累計¥289.80+¥<実測>=¥<合計>。
- 参照: `docs/pm/RESULT_PACKET_UT06_B.md`、commit <A2 hash>/<B1 hash>
```
索引1行。`OPEN_ITEMS.md` OPEN-147行末: ` 2026-09-15追記(UT-06 B): The future of memory A2/B1完成(<Audio Validation結果>)、Status=VALIDATED候補/USER_LISTENING_PENDING、費用¥<実測>、Family C累計¥<合計>。本文はTrial-08正本固定<・修正なし/・最小修正1件>。`
`docs/pm/ACTIVE_TASK.md`: 固定ヘッダ形式で上書き(報告単位Status: 委任A=USER_DECISION_REQUIRED[Discovery B1/A2 STOP]、委任B=<状態>、委任C=未着手)。

## Git(明示add対象・コミットメッセージ・trailer)

- A2完成時とB1完成時で分けてcommit。明示add対象(wav除外、mp3必須): 新規スクリプト2件+テスト1件、`er013_output/family_c_episode_trial_10/memory_a2/`・`memory_b1/`配下(player.html、web/**/*.mp3、segments.json、speaker_map.json、comment_placement.json、key_phrases/**、audit/*.json、各consistency/validation/cost json、spec/*.md、comments_*.md、preview*.txt、reader_facing_article_b1.txt等)、`DECISION_LOG.md`、`OPEN_ITEMS.md`、`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`、`docs/pm/delegation_log/USER-TEST-FINAL-AUDIO-BATCH-06_B.md`、同`_check.json`、`docs/pm/RESULT_PACKET_UT06_B.md`。
- `er006_output/`・`er011_output/`の既存M、`docs/pm/ACTIVE_TASK_*.md`/`RESULT_PACKET_*.md`の既存??、`home_robots*/`・`er014_output/`は触らない。
- コミットメッセージ: `USER-TEST-FINAL-AUDIO-BATCH-06 (B-A2): Family C memory A2 episode完成(Trial-08本文固定)` / `USER-TEST-FINAL-AUDIO-BATCH-06 (B-B1): Family C memory B1 episode完成(Support easy English/Charon)`
- trailer: `Task-ID: USER-TEST-FINAL-AUDIO-BATCH-06`
- push: 各commit後`git push origin main`。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_UT06_B.md`に:
1. T-0結果
2. 既存asset確認結果(再利用したもの/新規生成したもの)
3. 本文固定の証跡(正本sha256、修正の有無。修正した場合は箇所・前後・理由)
4. A2: 語数(報告義務該当有無)、Voice割当表、Comment位置と理由、日本語タイトル、TTS segment数と失敗/retry内訳、Audio Validation(PASS/FAIL、duration)、4者一致(canonical/TTS input/ASR/player)結果、費用(LLM/TTS/ASR/その他)、個別対応内容
5. B1: 語数(目安比)、Fact Safety/Story core check結果、Support(Preview/Comment 1〜3全文)とvoice evidence(Charon)、日本語タイトル不在・Comment 4不在の確認、TTS内訳、Audio Validation(PASS/FAIL、duration)、4者一致、費用、個別対応内容
6. ユーザー指示17のClosout項目(A2/B1各: article status/word count/Audio Validation/duration/player URL/direct audio URL/追加費用/再生成回数/個別対応内容/新規Open Item有無/USER_LISTENING_PENDING)
7. Token節約報告(ユーザー指示15)
8. Web到達確認(4 URL)
9. 回帰結果
10. commit hash・push結果・残差分要約
11. unresolved issue・新規Open Item(4点形式)
12. 事前指定外Read(理由付き)

ユーザー向け表記は「B1」に統一(「B1B」不使用)。

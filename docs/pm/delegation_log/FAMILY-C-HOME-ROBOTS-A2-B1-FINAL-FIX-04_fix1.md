## 管理ID

`FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04`(Fable修正指示1回目)
並行タスクなし。前回Sonnet実行(commit `a417fab3`、SSOTコミット`8b941190`とされる)の続き。`docs/pm/RESULT_PACKET.md`/`docs/pm/ACTIVE_TASK.md`は本タスクで更新してよい。

## 性質/到達上限Status/禁止事項

- 性質: 前回成果のFable受入照合で見つかった3点の是正。(1) B1 Previewが日本語のまま(`audit/tts_generation_results.json` 422-426行`preview_ja` canonical_textが日本語であることをFableが実測確認)→CURRENT_SPEC 626行「Preview、Comment 1〜4を平易な英語で提供する」(`DECIDED`)との明確な不整合であり、ユーザー指示4「既存B1正式仕様との明確な不整合なら、その範囲内で最小修正してよい」の範囲内。前回Comment英語化と同じ原因(b)(`a2gen.PREVIEW_ROLE`流用)。(2) 回帰が`09b*`パターンでv1(trial_09、22件)未実行→委任どおり`09*`で全件実行。(3) SSOTコミット(`8b941190`?)がRESULT_PACKET 13項・ACTIVE_TASKに「次コミット予定」のまま未記録→実hashを確認して記録。
- 到達上限Status: 前回と同じ(A2 v2・B1とも`VALIDATED候補/Trial`、`USER_LISTENING_PENDING`、Production未採用)。
- 対象外: A2 v2(前回完了、触らない)、Trend/Discovery/Voices/OPEN-154/155、`er012_*`/`er003_*`/`er011_*`Production経路、`CURRENT_SPEC.md`。
- 禁止: Preview以外のB1 segmentの再TTS(Comment 1〜3・Robot文・Story本文は前回確定済み、sha256不変を検証)、新恒久仕様の新設、`git add -A`/`stash`/`amend`、wavのcommit、Comment 4復活、日本語タイトル復活。
- 費用上限: ¥20(Preview LLM生成1件+TTS 1件+ASR。**必ず`--reassemble`相当の単一segment再生成モードを使い、全segment再ASRを発生させない**。前回の逸脱[A2 ¥14.10/B1 ¥17.70の不要ASR]を繰り返さない)。超過見込みならSTOP。
- STOP条件: (1)費用上限超過見込み、(2)既存B1 Support経路(`er003_v1_b1_scaffold_01_generate.py`)にPreview用英語roleが存在せず新規role文の作成が必要な場合(新仕様相当→STOPし報告)、(3)Audio Validation Gate FAIL 2回連続、(4)Preview以外のsegment sha256が変化した場合。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
(本委任のdelegation_log保存名: `docs/pm/delegation_log/FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04_fix1.md`)

## ユーザー指示(原文)

ユーザー原文(2026-09-15、該当部分のみ引用):
「2-1. 日本語タイトルを削除: B1は既存仕様どおり、タイトル周辺は英語のみとする。」
「2-2. (中略)英語の難易度: 既存B1 Support仕様に従う: very clear/easy spoken English/first-listenで理解しやすい/one simple idea at a time/adult tone/Storyを説明しすぎない/新しいFactを追加しない。単なる日本語Commentの機械翻訳ではなく、B1 Supportとして自然な英語にする。QA: canonical/TTS input/ASR/player表示を一致確認。」
「3. 回帰確認: (中略)B1: 英語タイトルのみ、Preview、Key Phrase、Comment 1〜3 = easy English、Comment 4なし、Mother voice、Robot voice、Story本文、Intro / Outro / SFX / pause」
「4. (中略)もし既存B1正式仕様との明確な不整合なら、その範囲内で最小修正してよい。新しい仕様が必要ならSTOP。」

Fable判断: B1 Preview日本語はCURRENT_SPEC 626行との明確な不整合であり、指示4の範囲内で最小修正する(Commentと同じfailure modeを個別に残さない、PM_GOVERNANCE 14-1)。

## 事前指定Read一覧

- `docs/pm/RESULT_PACKET.md`: 全文(前回の自分の報告、現状把握)
- `er013_family_c_episode_trial_09b_b1_run.py`: Grepで`PREVIEW_ROLE|def generate_preview|preview_ja|--comments-en|comments_en|--reassemble|reassemble`を位置特定→各該当関数/argparse範囲Read(前回追加した`--comments-en`の実装をPreviewへ横展開する)
- `er003_v1_b1_scaffold_01_generate.py`: Grepで`PREVIEW_ROLE|PREVIEW|def .*preview`を位置特定→該当定数/関数範囲Read(既存B1 Support Preview英語roleの所在。前回Comment roleは同ファイル114-191行を使用)
- `er013_output/family_c_episode_trial_09/home_robots_b1/audit/tts_generation_results.json`: 415-435行(`preview_ja`エントリ)
- `er013_output/family_c_episode_trial_09/home_robots_b1/player.html`: Grepで`preview`(大小無視)を位置特定→該当表示箇所Read

## 事前指定Grep一覧+追記位置・更新位置の手順

1. SSOTコミット確認: `git log --oneline -3`で`a417fab3`以降のcommitを確認し、`8b941190`(またはそれに相当するSSOTコミット)が存在しpush済み(`git status -sb`で`ahead 0`)かを確認。存在しなければ、前回のSSOT変更(DECISION_LOG/OPEN_ITEMS/MODEL_ROUTING_TRIAL_LOG/REPORT/delegation_log)を明示addでcommit・push。
2. Preview残存確認(修正後): `Grep pattern="[\u3040-\u30ff\u4e00-\u9fff]"`相当のpython検証(下記コマンド)で、B1 `audit/tts_generation_results.json`のPreview・Comment 1〜3・title系entryのcanonical_textに日本語が無いこと(Key Phraseの日本語gloss[`*_ja`のgloss]は既存B1仕様どおり日本語で正しいため除外。除外したentry名を報告)。
3. sha256不変確認: 修正前後で`audit/tts_generation_results.json`のsha256を比較し、Preview entry以外のすべてのsegment sha256が同一であることをpythonで検証・報告。
4. SSOT追記位置: `Grep pattern="^## FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04" path=DECISION_LOG.md`(7572行付近)→同エントリ末尾に「修正1回目」の追記行を追加。`OPEN_ITEMS.md`のOPEN-147行はpythonで行末追記(Readツール不可)。
5. 前回REPORT`FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04_REPORT.md`: 3節(Comment英語化)の直後に「3b) B1 Preview英語化」節を追加、7節(回帰)を`09*`結果へ更新、8節(費用)に本修正分を追加、10節unresolved issueの「B1 Preview日本語の可能性」項目を「修正済み」へ更新(削除ではなく経緯を残す)。

## 実行コマンド全文

作業ディレクトリ`C:\Users\tensh\eigo-radio`、pythonは`.venv\Scripts\python.exe`。

T-0:
```
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04_fix1.md --json-out docs\pm\delegation_log\FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04_fix1_check.json
```

Preview英語化: `er013_family_c_episode_trial_09b_b1_run.py`へ`--preview-en`フラグを追加(`--comments-en`と同型: `er003_v1_b1_scaffold_01_generate`のPreview英語roleを使用[Family C Story形式向けにNews/Point言及があれば最小調整し報告]、Charon voiceで再TTS→ASR→単一segment差し替えで再Assembly→Audio Validation→player再生成。segment名は`preview_en`とし`preview_ja`は`audio/prev/`へ退避)。旧episode mp3/playerは`home_robots_b1/web/prev/family_c_home_robots_trial_09b_b1_preview_ja.mp3`・`home_robots_b1/player_prev_preview_ja.html`へ退避(既存の`_ja_support`退避は上書きしない)。
```
.venv\Scripts\python.exe er013_family_c_episode_trial_09b_b1_run.py --drop-japanese-title --comments-en --fix-robot-choice-second-person --preview-en --reassemble
```
(既存argparseで`--reassemble`の実名・組み合わせが異なる場合は、前回確定済みsegmentを再TTS/再ASRしない引数に調整し、実引数全文を報告。)

日本語残存検証:
```
.venv\Scripts\python.exe -c "import json,re;d=json.load(open('er013_output/family_c_episode_trial_09/home_robots_b1/audit/tts_generation_results.json',encoding='utf-8'));ents=d.get('segments',d);bad=[(k,v.get('canonical_text','')[:50]) for k,v in ents.items() if isinstance(v,dict) and re.search(r'preview|comment|title|intro',k,re.I) and not k.endswith('_gloss') and re.search(r'[\u3040-\u30ff\u4e00-\u9fff]',v.get('canonical_text',''))];print('JA_IN_SUPPORT=',len(bad));[print(b) for b in bad]"
```
(実構造に合わせてキー名を修正可、修正後コマンド全文を報告。Key Phrase日本語glossはB1仕様どおりのため除外対象として明記。)

回帰(**必ず`09*`**、v1 22件を含む全件):
```
.venv\Scripts\python.exe run_project_regression.py --pattern "er013_family_c_episode_trial_09*_test_*.py"
```
B1テストへ`test_preview_contains_no_japanese_characters`1件追加。見込み: v1 22+v2 19+B1 28=69件。

Web到達確認(push後、raw.githackはGET):
```
.venv\Scripts\python.exe -c "import urllib.request as u;[print(u.urlopen(x).status,x) for x in ['https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_09/home_robots_b1/player.html','https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_09/home_robots_b1/web/family_c_home_robots_trial_09b_b1.mp3']]"
```

## SSOT追記文

`DECISION_LOG.md` `## FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04`エントリ末尾に追記:
```
- 2026-09-15 Fable修正指示1回目: Fable受入照合でB1 Previewが日本語のまま(A2用`a2gen.PREVIEW_ROLE`流用、Comment 1〜3と同一原因)と判明。CURRENT_SPEC「B1 Support」対象要素(Preview、Comment 1〜4を平易な英語で)との明確な不整合としてユーザー指示4の範囲内で最小修正(既存B1 Support経路`er003_v1_b1_scaffold_01_generate`のPreview roleを使用、Charon voice、`--preview-en`)。Preview以外のsegment sha256不変。Audio Validation B1 <PASS/FAIL、duration秒>。回帰`09*`全件 collected=<n> passed=<n> failed=0。追加費用¥<実測>、本タスク累計¥41.70+¥<実測>=¥<合計>、Family C累計¥<合計>。commit <hash>。
```
`OPEN_ITEMS.md` OPEN-147行末追記: ` 2026-09-15追記(FIX-04修正1回目): B1 Previewも英語化(同一原因)。本タスク実費累計¥<合計>、Family C累計¥<合計>。`
`docs/pm/ACTIVE_TASK.md`: 固定ヘッダ形式で更新(commit hash確定値を記載、「次コミット予定」表記を解消)。
`docs/pm/RESULT_PACKET.md`: 末尾に「## 修正1回目」節を追加(下記項目)。

## Git(明示add対象・コミットメッセージ・trailer)

- 明示add対象(wav除外): `er013_family_c_episode_trial_09b_b1_run.py`、`er013_family_c_episode_trial_09b_b1_test_01.py`、`er013_output/family_c_episode_trial_09/home_robots_b1/`配下の更新・新規(player.html、player_prev_preview_ja.html、web/*.mp3、web/prev/*_preview_ja.mp3、web/segments/preview_en.mp3等、segments.json、audit/*.json、各consistency/validation/cost json、preview_en.md等)、`DECISION_LOG.md`、`OPEN_ITEMS.md`、`FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04_REPORT.md`、`docs/pm/delegation_log/FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04_fix1.md`、同`_check.json`。
- `er006_output/`・`er011_output/`の既存M、`docs/pm/ACTIVE_TASK_*.md`/`RESULT_PACKET_*.md`の既存??は触らない。
- コミットメッセージ: `FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04 (fix1): B1 Preview英語化(B1 Support仕様整合)+回帰09*全件+SSOTコミット記録`
- trailer: `Task-ID: FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04`
- push: `git push origin main`。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`末尾「## 修正1回目」に:
1. T-0結果
2. SSOTコミット確認結果(`8b941190`の実在・push状態、無ければ新規commit hash)
3. B1 Preview旧文(日本語)/新文(英語全文)、使用role定数名と出典ファイル:行、Family C向け調整の有無、canonical/TTS input/ASR/player表示4者一致、日本語残存検証コマンドと結果(除外entry明記)
4. Preview以外のsegment sha256不変の検証結果(比較件数・差分0件)
5. Audio Validation(B1 PASS/FAIL、duration、前回389.175秒との差)
6. 回帰`09*`結果(collected/passed/failed、v1/v2/B1の内訳)
7. 費用(本修正実費内訳LLM/TTS/ASR、`--reassemble`適用の有無、本タスク累計、Family C累計)
8. commit hash・push結果・Web到達確認(2件のHTTP status)
9. unresolved issue(残るもの: speaker判定UI特例なし、A2スクリプトの退避無条件上書し挙動、その他)
10. final status(A2 v2/B1とも`VALIDATED候補/Trial、Production未採用、USER_LISTENING_PENDING`)
11. 事前指定外Read(理由付き)

ユーザー向け表記は「B1」に統一。

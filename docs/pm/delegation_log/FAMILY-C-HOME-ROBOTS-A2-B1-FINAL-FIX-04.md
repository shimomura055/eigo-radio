## 管理ID

`FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04`
並行タスクなし(本委任が唯一の実行中タスク。`docs/pm/ACTIVE_TASK.md`/`docs/pm/RESULT_PACKET.md`は本タスクで上書きしてよい)。

## 性質/到達上限Status/禁止事項

- 性質: Family C(Home robots)Trial記事のユーザー試聴Feedback反映(A2 1箇所、B1 3点)+原因確認+回帰。
- 到達上限Status: Family C A2 v2・B1とも**VALIDATED候補/Trial**のまま。`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`へ昇格しない。
- 対象外(触らない): Trend/Discovery/Voices/OPEN-154/OPEN-155、`er012_*`Production経路、Family C以外の全artifact、`CURRENT_SPEC.md`(本タスクでは仕様追加しない)。
- 禁止: 新恒久仕様の新設(A2二人称修正は「今回の文脈上の整合修正」であり仕様化しない)、Production-wide architecture変更、Story本文(ユーザー指定箇所以外)の変更、A2 v2のユーザー承認済み他箇所の変更、Comment 4の復活、`git add -A`/`stash`/`amend`、wavのcommit。
- 費用上限: 合計¥60(LLM Comment英語生成+TTS再生成[A2 Robot 1 segment、B1 Robot 1 segment、B1 Comment 3 segment]+ASR)。超過見込みならSTOPし理由を報告。
- STOP条件: (1)費用上限超過見込み、(2)B1に日本語タイトル/日本語Commentを含めることが既存正式仕様で定義されていると判明した場合(仕様矛盾)、(3)原因修正に既存B1正式仕様の範囲を超える新仕様が必要な場合、(4)Audio Validation Gate FAILが2回連続、(5)ASR/canonical/player表示の不一致が修正後も解消しない場合。STOP時は完了分をcommitせず状態をRESULT_PACKETへ記録し停止。
- 実行順序: Part 1(A2)→Part 2(B1)→Part 3(回帰)→Part 4(原因確認)→SSOT→Git。Part 1完了時点でPart 2がSTOPになった場合はPart 1のみcommitしてよい(1記事ずつ完結原則)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。

## ユーザー指示(原文)

以下ユーザー原文(2026-09-15)を要約せず引用する:

---
目的: Family C / Home robots のユーザー試聴Feedbackを反映する。今回はFamily Cのみ対象。Trend / Discovery / Voices / OPEN-154 / OPEN-155には触れない。

1. Family C A2
ユーザー評価: A2は、以下1箇所以外はOK。
現状: `CARE HOUSE: more sleep for Maya. HOME: more time with her mother.`
これはロボットがMaya本人に選択肢として提示しているため、三人称ではなく二人称にする。
修正後: `CARE HOUSE: more sleep for you. HOME: more time with your mother.`
実施内容: 上記箇所のみcanonical textを差し替える/Storyのその他部分は変更しない/Robot voiceで再TTS/ASR / canonical / player表示の一致を確認/episodeを再Assembly/Audio Validation/Web player更新
注意: この修正は今回の文脈上の自然な整合修正。新しい恒久仕様は作らない。A2の他箇所はユーザー承認済みなので触らない。

2. Family C B1: ユーザー試聴で3点修正。
2-1. 日本語タイトルを削除: B1は既存仕様どおり、タイトル周辺は英語のみとする。現在、英語タイトルの後に日本語タイトルが続いている場合は削除。Family A/B1既存episode構成を確認し、それに合わせること。
必須確認: B1で日本語タイトルを読む正式仕様になっていないことを確認/A2の日本語タイトル構成を誤ってB1へ流用していないか確認
2-2. Commentをすべて英語へ修正: 現在B1のComment 1〜3が日本語になっている。B1では既存仕様どおり、Comment 1〜3はeasy Englishにする。目的は従来どおりStory理解補助。
Comment設計: Comment 1:導入理解補助/Comment 2:Story途中の自然な節目/Comment 3:後半の理解補助/Comment 4なし。位置は今回の既存B1構成を維持。
英語の難易度: 既存B1 Support仕様に従う: very clear/easy spoken English/first-listenで理解しやすい/one simple idea at a time/adult tone/Storyを説明しすぎない/新しいFactを追加しない。単なる日本語Commentの機械翻訳ではなく、B1 Supportとして自然な英語にする。
QA: 全Commentについて、canonical/TTS input/ASR/player表示を一致確認。
2-3. Robot表示文の三人称→二人称修正:
現状: `CARE HOUSE — more sleep and privacy for Maya` / `HOME — more time with her mother`
修正後: `CARE HOUSE — more sleep and privacy for you` / `HOME — more time with your mother`
理由: ロボットがMaya本人へ選択肢として提示しているため。A2と同じ考え方。
実施: canonical差し替え/Robot voice再TTS/ASR一致確認/player表示更新/episode再Assembly

3. 回帰確認: 今回の修正で以下が壊れていないことを確認。
A2: Intro / Outro / SFX、Key Phrase、Comment 1〜3、Mother voice、Robot voice、Story本文、Comment 4なし
B1: 英語タイトルのみ、Preview、Key Phrase、Comment 1〜3 = easy English、Comment 4なし、Mother voice、Robot voice、Story本文、Intro / Outro / SFX / pause

4. 原因確認: B1で、日本語タイトル/日本語Commentが入った原因を簡潔に特定すること。
確認観点: A2 assembly templateをB1へ流用したのか/B1 Support生成経路を使わずA2側Supportを再利用したのか/Family C Trial用scaffoldにlevel分岐が無いのか
ただし、今回勝手にProduction-wide architecture変更はしない。原因と再発可能性のみREPORTする。もし既存B1正式仕様との明確な不整合なら、その範囲内で最小修正してよい。新しい仕様が必要ならSTOP。

5. Status: Family C A2: 今回の修正後も、VALIDATED候補 / Trial。Production採用ではない。Family C B1: 今回の修正後も、VALIDATED候補 / Trial。Production採用ではない。

6. Closeout: 最終報告では最低限、A2修正前後/B1日本語タイトル削除/B1 Comment英語化/B1 Robot文言修正/原因/Audio Validation/duration/追加費用/player URL/direct audio URL/unresolved issue/final statusを報告。ユーザーが再試聴すべきURLは、Family C A2 / B1の2本だけ最後に再掲すること。
---

Fable補足(仕様照合の前提): CURRENT_SPEC 622-628行「B1 Support(Preview / Comment 1-4)」は「Preview、Comment 1〜4を平易な英語で提供する」「Comment役割はA2を維持し言語だけJapanese→easy English」を`DECIDED`としている。日本語タイトルはCURRENT_SPEC 667行でVoices **A2**の規約(`PRODUCTION_WIRED`)であり、B1側の規約ではない。Fableの事前Grepでは`er013_family_c_episode_trial_09b_b1_run.py`が(a)91行`JAPANESE_TITLE_TEXT`をv2から流用し744/841/961行でtimelineへ挿入、(b)114-142行`COMMENT_*_ROLE_JA`(A2の日本語Comment role)を`COMMENT_ROLES`として`a2gen.run_support_text`(419行)に渡している痕跡がある。これは原因候補であり、Sonnetが実コードで確定させること。

## 事前指定Read一覧

- `docs/pm/RESULT_PACKET_FU03_FAMILYC_A2.md`: 全文(A2 v2の修正手順・artifact構成・Gate結果の前例)
- `docs/pm/RESULT_PACKET_FU03_FAMILYC_B1.md`: 41-70行(Preview/Comment生成経路)、73-110行(timeline構成・成果物パス)、150-175行(スクリプト一覧)
- `docs/pm/RESULT_PACKET_FU03_FAMILYC_B1_2.md`: 全文(Comment 3固定文差し替え+再TTSの前例手順)
- `CURRENT_SPEC.md`: 600-606行(B1基本方針)、622-628行(B1 Support)、1040-1050行(B1 Support言語・Charon voice記述)
- `er013_family_c_episode_trial_09b_b1_run.py`: 1-40行(ヘッダコメント)、85-160行(定数: JAPANESE_TITLE_TEXT/COMMENT_*_ROLE_JA/COMMENT_3_FIXED_TEXT_OVERRIDE)、410-440行(Comment/Preview生成)、540-560行(argparse)、625-660行(comment差し替えロジック)、735-750行・835-850行・955-965行・1070-1090行(Japanese title timeline/audit/player表示)
- `er013_family_c_episode_trial_09b_run.py`: Grepで`COMMENT_3_FIXED_TEXT_OVERRIDE`/`fix_comment3`を位置特定→該当関数範囲Read(A2側のsegment固定文差し替え+単一segment再TTSの実装。同じ機構をRobot segmentへ流用する)
- `er013_output/family_c_episode_trial_09/home_robots_b1/segments.json`: 175-195行(Robot表示文segment、185-186行に対象文字列)
- `er013_output/family_c_episode_trial_09/home_robots_v2/segments.json`: Grepで`more sleep for Maya`を位置特定→前後10行Read
- `docs/pm/PM_GOVERNANCE.md`: Grepで`## 15-8`または`15-8`を位置特定→該当節Read(費用報告形式)、Grepで`2-3`+`supersession`を位置特定→該当節Read(旧artifact退避ルール)

## 事前指定Grep一覧+追記位置・更新位置の手順

1. B1正式仕様に日本語タイトルが無いことの確認: `Grep pattern="Japanese title|japanese_title|日本語タイトル" path=er012_b_family_voices_production_01.py`および`path=er012_b_family_production_runner_01.py`(B1Bのlevel分岐にJapanese titleが含まれないことを確認)、`Grep pattern="Japanese title|日本語タイトル" path=CURRENT_SPEC.md output_mode=content`(全ヒットがA2文脈であることを確認、B1文脈のヒットがあれば行番号付きで報告しSTOP条件(2)判定)。
2. 既存B1 Support英語Comment roleの所在: `Grep pattern="COMMENT_1_ROLE|COMMENT_ROLE_EN|B1_COMMENT|easy English|Listening Focus" glob="er003_v1_*b1*.py|er012_b_family_*b1*.py|er011_*b1*.py"`→ヒットしたB1用英語Comment role定数(C1: Listening Focus/C2: Mid-story Recovery/C3: Story Meaning、C4は使わない)を特定し、B1 runスクリプトの`COMMENT_ROLES`をそれへ差し替える(既存正式B1 Support経路の再利用。新規role文を独自作成しない。Family C固有のStory文脈は`context`引数で渡す)。既存B1 roleにNews固有文言(Point One/Two等)が含まれる場合は、Family C(Story形式、Point節なし)に合わせ最小限の文言調整をし、調整箇所をRESULT_PACKETへ記載。
3. A2 Robot文の位置: `Grep pattern="more sleep for Maya" path=er013_output/family_c_episode_trial_09/home_robots_v2/ output_mode=content`および`Grep pattern="more sleep for Maya" path=er013_family_c_episode_trial_09b_run.py`(Story本文がスクリプト内定数かartifact読み込みかを特定)。
4. B1 Robot文の位置: `Grep pattern="more sleep and privacy for Maya" path=er013_output/family_c_episode_trial_09/home_robots_b1/ output_mode=content`および`path=er013_family_c_episode_trial_09b_b1_run.py`。
5. Comment 4混入再確認(修正後): `Grep pattern="comment_4|Comment 4" path=er013_output/family_c_episode_trial_09/home_robots_b1/segments.json`および`home_robots_v2/segments.json`→0件であること。
6. 日本語タイトル残存確認(修正後): `Grep pattern="japanese_title|ホームロボット" path=er013_output/family_c_episode_trial_09/home_robots_b1/segments.json`および`home_robots_b1/player.html`→0件であること。
7. Comment日本語残存確認(修正後): B1 `segments.json`のComment 1〜3 segmentの`tts_text`に日本語文字(`[\u3040-\u30ff\u4e00-\u9fff]`)が含まれないことをpythonで検証(コマンドは下記)。
8. SSOT追記位置: `Grep pattern="^## PM-CLOSEOUT-CONSOLIDATION-135" path=DECISION_LOG.md`→そのエントリ末尾直後(`## 参照元`の直前)に新エントリ追加、`Grep pattern="^## PM-CLOSEOUT-CONSOLIDATION-135|PM-CLOSEOUT-CONSOLIDATION-135\]" path=DECISION_LOG.md`で索引行を特定→直後に索引1行追加。`OPEN_ITEMS.md`はBash(python)で`OPEN-147`行を特定し行末に追記(Readツールは単一行長超過でエラーになるため、FU-03と同じくpythonで処理)。

## 実行コマンド全文

作業ディレクトリ: `C:\Users\tensh\eigo-radio`。pythonは必ず`.venv\Scripts\python.exe`。

T-0:
```
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04.md --json-out docs\pm\delegation_log\FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04_check.json
```

Part 1(A2): `er013_family_c_episode_trial_09b_run.py`へ`--fix-robot-choice-second-person`フラグを追加(既存`--fix-comment3`と同じ「固定文差し替え→当該segmentのみRobot voice[Charon]で再TTS→ASR→再Assembly→Audio Validation→player再生成」機構を流用)。Story本文のsha256は当該segment以外不変であることを検証に含める。旧episode mp3/playerはPM_GOVERNANCE 2-3に従い`home_robots_v2/web/prev/family_c_home_robots_trial_09b_third_person.mp3`・`home_robots_v2/player_prev_third_person.html`へ退避(上書き禁止)。
```
.venv\Scripts\python.exe er013_family_c_episode_trial_09b_run.py --fix-comment3 --fix-robot-choice-second-person
```
(既存フラグとの組み合わせ方は既存argparse実装を確認し、Comment 3修正済み状態を維持したまま再Assemblyされる引数に調整する。実際に実行した引数全文をRESULT_PACKETに記載。)

Part 2(B1): `er013_family_c_episode_trial_09b_b1_run.py`へ以下を追加: `--drop-japanese-title`(timeline/audit/player表示/segments.jsonからJapanese title segmentを除去、直後のpause値は既存A/B Family B1構成に合わせる)、`--comments-en`(`COMMENT_ROLES`をGrep 2で特定した既存B1 easy English roleへ差し替え、Comment 1〜3をLLMで再生成→Charon voice(既存B1 Support voice、CURRENT_SPEC 1048行)で再TTS→ASR。`COMMENT_3_FIXED_TEXT_OVERRIDE`[日本語]は`--comments-en`時は適用しない。Comment 3の役割「後半の理解補助」は維持しつつ、A2 v2/B1 CONT1で修正した主語明確化[ロボット/マヤ]を英語でも保つこと)、`--fix-robot-choice-second-person`(185-186行segmentの固定文差し替え→Robot voice再TTS→ASR)。旧episode mp3/playerは`home_robots_b1/web/prev/family_c_home_robots_b1_ja_support.mp3`・`home_robots_b1/player_prev_ja_support.html`へ退避。
```
.venv\Scripts\python.exe er013_family_c_episode_trial_09b_b1_run.py --drop-japanese-title --comments-en --fix-robot-choice-second-person
```
(同上、実引数全文を報告。)

Part 2 QA(日本語残存検証、Grep 7):
```
.venv\Scripts\python.exe -c "import json,re;s=json.load(open('er013_output/family_c_episode_trial_09/home_robots_b1/segments.json',encoding='utf-8'));segs=s if isinstance(s,list) else s.get('segments',s);bad=[x for x in segs if isinstance(x,dict) and re.search(r'comment',str(x.get('segment_id',x.get('id',''))),re.I) and re.search(r'[\u3040-\u30ff\u4e00-\u9fff]',x.get('tts_text',''))];print('JA_IN_COMMENT_TTS=',len(bad));[print(x.get('segment_id',x.get('id')),x.get('tts_text')[:60]) for x in bad]"
```
(segments.jsonの実構造に合わせてキー名を修正してよい。修正後コマンド全文を報告。)

Part 3(回帰): 既存テストへ以下を追加: A2側1件(Robot choice segmentが二人称固定文と一致)、B1側3件(Japanese title segment不在、Comment 1〜3のtts_textに日本語文字なし、Robot choice segmentが二人称固定文と一致)。
```
.venv\Scripts\python.exe run_project_regression.py --pattern "er013_family_c_episode_trial_09*_test_*.py"
```
全件PASSを確認(前回64件+新規4件=68件見込み)。

Part 3(Web到達確認、push後):
```
.venv\Scripts\python.exe -c "import urllib.request as u;[print(r.status,x) for x in ['https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_09/home_robots_v2/player.html','https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_09/home_robots_v2/web/family_c_home_robots_trial_09b.mp3','https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_09/home_robots_b1/player.html'] for r in [u.urlopen(u.Request(x,method='HEAD'))]]"
```
B1 episode mp3のdirect URLは`home_robots_b1/web_delivery.json`から実ファイル名を取得して同様にHEAD確認し、4件全件200を報告(CDN遅延時は60秒待って最大3回再試行)。

Part 4(原因確認): 上記Grep 1-2とスクリプトReadの結果から、(a)A2 assembly template流用の有無、(b)B1 Support生成経路を使わずA2側Support roleを再利用したか、(c)Family C Trial scaffoldにlevel分岐が無いか、を各1〜3行で事実ベースで記述。再発可能性(Family C次記事・他Family Trialへの波及)を1段落で評価。修正はB1正式仕様(CURRENT_SPEC 622-628)の範囲内の本Trialスクリプト内に留め、`er012_*`/`er003_*`/`er011_*`は編集しない。

## SSOT追記文

`DECISION_LOG.md`(新エントリ、`## PM-CLOSEOUT-CONSOLIDATION-135`エントリ末尾直後):
```
## FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04

- 日付: 2026-09-15
- 種別: Trial記事修正(ユーザー試聴Feedback反映)、Status不変(A2 v2・B1ともVALIDATED候補/Trial、Production未採用)
- 決定/実施: (1) Family C A2 v2: Robot提示の選択肢文を三人称→二人称へ差し替え(`CARE HOUSE: more sleep for you. HOME: more time with your mother.`、Robot voice再TTS、当該segment以外のStory本文sha256不変)。今回の文脈上の整合修正であり恒久仕様ではない。(2) Family C B1: 日本語タイトル削除(B1正式仕様[CURRENT_SPEC「B1 Support」節]にはJapanese titleが無く、A2 v2からの流用が原因)、Comment 1〜3を既存B1 Support easy English roleで再生成(A2日本語roleの流用が原因)、Robot提示文を二人称へ差し替え。(3) 原因: <Sonnetが確定した原因を1〜2行で>。再発可能性: <1行>。
- Audio Validation: A2 <PASS/FAIL、duration秒>、B1 <PASS/FAIL、duration秒>
- 費用: 本タスク実費¥<実測>(内訳: LLM¥<x>/TTS¥<y>/ASR¥<z>)。Family C累計¥235.50+¥<実測>=¥<合計>。
- 回帰: `run_project_regression.py --pattern "er013_family_c_episode_trial_09*_test_*.py"` collected=<n> passed=<n> failed=0
- 参照: `docs/pm/RESULT_PACKET.md`(本タスク)、commit <hash>
```
索引行(`PM-CLOSEOUT-CONSOLIDATION-135`索引行の直後、既存索引と同形式)。

`OPEN_ITEMS.md` OPEN-147行末追記:
```
 2026-09-15追記(FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04): ユーザー試聴Feedback反映。A2 v2はRobot選択肢文を二人称へ修正(1箇所のみ、他箇所ユーザー承認済み)。B1は日本語タイトル削除・Comment 1〜3をeasy Englishへ再生成・Robot選択肢文を二人称へ修正。原因=<1行>。A2 v2・B1ともVALIDATED候補/Trialのまま(Production未採用)、再試聴待ち。実費¥<実測>、Family C累計¥<合計>。
```

`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`末尾: Family C B1 Comment英語再生成の行を既存行と同形式で1行追加。

`docs/pm/ACTIVE_TASK.md`: 本タスク内容で上書き(`docs/pm/PM_BRIEF.md`135-159行の固定ヘッダ形式。Status: A2/B1修正完了・再試聴待ち[USER_LISTENING_PENDING]、UDR-deferred: Discovery Part C/Discovery B1人間承認/OPEN-154/OPEN-155は前回のまま引き継ぐ)。

## Git(明示add対象・コミットメッセージ・trailer)

- 明示add対象(wav除外、mp3必須): `er013_family_c_episode_trial_09b_run.py`、`er013_family_c_episode_trial_09b_test_01.py`、`er013_family_c_episode_trial_09b_b1_run.py`、`er013_family_c_episode_trial_09b_b1_test_01.py`、`er013_output/family_c_episode_trial_09/home_robots_v2/`配下の更新・新規ファイル(player.html、player_prev_third_person.html、web/*.mp3、web/prev/*.mp3、web/segments/*.mp3、segments.json、各種consistency/validation/audit/cost json)、`er013_output/family_c_episode_trial_09/home_robots_b1/`配下の同種ファイル(comments_en.md等の新規含む)、`DECISION_LOG.md`、`OPEN_ITEMS.md`、`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`、`docs/pm/delegation_log/FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04.md`、`docs/pm/delegation_log/FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04_check.json`、`FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04_REPORT.md`(root直下、新規)。
- add前に`git status --porcelain er013_output/family_c_episode_trial_09/`で対象を確認し、ファイル名を個別またはディレクトリ限定で指定(`-A`禁止)。`er006_output/`・`er011_output/`の既存`M`と`docs/pm/ACTIVE_TASK_*.md`/`RESULT_PACKET_*.md`の`??`は触らない。
- コミットメッセージ: `FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04: A2 Robot選択肢二人称化+B1日本語タイトル削除・Comment英語化・Robot選択肢二人称化`
- trailer: `Task-ID: FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04`
- push: `git push origin main`。結果を`--short`相当で報告。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`を上書きし、以下を記載:
1. T-0結果(PASS/FAIL・reasons)
2. A2修正前後(旧文/新文、segment id、sha256[当該segment以外不変の証跡]、再TTS voice、ASR一致、player表示一致)
3. B1日本語タイトル削除(削除segment、pause調整値、Family A/B1既存構成との照合結果、B1正式仕様にJapanese titleが無いことの根拠行番号)
4. B1 Comment英語化(Comment 1〜3の新英文全文、使用したB1 role定数名と出典ファイル:行、Family C向け文言調整の有無、canonical/TTS input/ASR/player表示の4者一致、日本語残存検証コマンドと結果)
5. B1 Robot文言修正(旧文/新文、ASR一致、player表示一致)
6. 原因確認(観点(a)(b)(c)の事実、再発可能性、本タスクで行った最小修正の範囲、STOP該当有無)
7. Audio Validation結果(A2/B1それぞれPASS/FAIL、duration秒、旧durationとの差)
8. 回帰結果(collected/passed/failed、新規テスト4件の名前)
9. 追加費用(PM_GOVERNANCE 15-8形式: 本タスク実費内訳[LLM/TTS/ASR]、開発・Trial/検証費、Family C累計、Production 1生成セット総原価への影響)
10. player URL・direct audio URL(A2/B1各2件、raw.githack player+raw.githubusercontent mp3)+Web到達確認結果(HTTP status)
11. unresolved issue
12. final status(A2 v2/B1とも`VALIDATED候補/Trial、Production未採用、USER_LISTENING_PENDING`)
13. commit hash・push結果・push後`git status --porcelain | wc -l`相当の残差分要約
14. 事前指定外Read(理由付き1行ずつ)
15. 最終REPORT(`FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04_REPORT.md`)にはユーザー指示6の項目すべてを含め、末尾にFamily C A2/B1のplayer URL 2本のみを再掲。

ユーザー向け表記は「B1」に統一(「B1B」不使用)。

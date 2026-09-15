## 管理ID

`USER-TEST-FINAL-AUDIO-BATCH-06`(委任D: Discovery B1 part2分割TTS→Discovery A2 NG 2 segment個別retry)+`USER-TEST-FINAL-AUDIO-BATCH-06-FOLLOWUP-01`項目4・5
並行タスクなし(委任A/B/Cは完了・push済み、最新commit `0bfb524d`)。報告は`docs/pm/RESULT_PACKET_UT06_D.md`(新規)へ。`docs/pm/ACTIVE_TASK.md`は本タスクで上書き可。

## 性質/到達上限Status/禁止事項

- 性質: Discovery記事(er014 four_type_observation_01)のB1/A2音声を、ユーザー判断済みの個別対応で完成させる。**順序: Part 1(B1)完了→commit→Part 2(A2)完了→commit**。週間Token枠逼迫のため、恒久対策・横断監査・複数案生成・Prompt改善・Validator新設・Gate緩和を一切しない。
- 到達上限Status: Discovery B1=音声PASSまで、`USER_LISTENING_PENDING`。Discovery A2=音声完成まで、`USER_LISTENING_PENDING`。
- 禁止: canonical本文・Fact・Support・Key Phraseの変更(B1/A2とも)、Gate判定の緩和、Fact誤り(数字)のHuman Approval、恒久Assembly仕様化・Production-wide対策、`er003_*`/`er011_*`/`er012_*`Production関数の編集、規定回数を超える自動retry、Opus使用、`git add -A`/`stash`/`amend`、wavのcommit。
- 費用上限: Part 1 ¥25、Part 2 ¥15(合計¥40)。超過見込みならそのPartのみSTOP。
- STOP条件(該当Partのみ、自動再試行しない): (1)Part 1で分割後も内容ブロック欠落(delete block)が発生、(2)Part 2で個別retry後も「2,557」が誤読される、または新しいcontent mismatchが出る、(3)費用上限超過見込み、(4)Audio Validation Gate FAIL 2回連続、(5)既存仕様同士の明確な衝突。STOP時は当該Partの状態・diff・個別対応候補(3件以内)を報告し、恒久設計変更へ進まない。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
(保存名: `docs/pm/delegation_log/USER-TEST-FINAL-AUDIO-BATCH-06_D.md`)

## ユーザー指示(原文)

ユーザー原文(USER-TEST-FINAL-AUDIO-BATCH-06-FOLLOWUP-01、2026-09-15):

---
4. Discovery B1: Family C 2記事完了後に対応。現状: full_story_part2で「2,500人 / 11か国」段落欠落が複数回再発/追加retryは既に実施済み/自動retry継続は禁止。ユーザー判断: 個別対応で完成を目指す。第一候補として、full_story_part2を自然な意味単位で2segmentへ分割してTTSする。目的は、長segment後半のblock omissionを避けること。条件: canonical本文の意味・内容を変更しない/2,500人 / 11か国段落を必ず保持/分割点は自然なparagraph / semantic boundary/新しい恒久Assembly仕様にはしない/Discovery B1当該記事だけの個別対応として実施。分割後、TTS/実音声ASR/canonical照合/Assembly/Audio Validation/player更新まで進める。STOP: 分割後も内容ブロック欠落が起きた場合は、その時点でSTOP。追加の自動retryや恒久設計変更へ進まない。

5. Discovery A2: Family C 2記事完了後、B1対応の次に実施。現状: 530語版本文はユーザー承認済み/16segment中14件OK/NG: full_story_part1: silence → pause、point_two: 2,557 → 2,527/Assemblyは未実施。ユーザー判断: NGの2segmentだけ個別追加retryする。本文・Support・Key Phrase等は変更しない。実施: full_story_part1のみ再TTS/point_twoのみ再TTS/実音声に対して再ASR/canonical一致確認。特に 2,557 はFact値なので、数字が正しく読まれることを必須とする。PASS後、Assembly/Audio Validation/player生成まで進める。STOP: 個別retryでもFact数字が誤る、または新しいcontent mismatchが出る場合はSTOP。Gate緩和やFact誤りのHuman Approvalは行わない。

6. 恒久課題の扱い: 今回Discoveryで判明した、長segment後半block omission/TTSの数字誤読/ASR表記差/segment分割の必要性について、今回Production-wide対策を作らない。必要ならOPEN-153等の既存Open Itemへ事実を追記し、恒久対策はdefer。

7. Token / Cost Guard: Opus禁止/不要な再生成禁止/不要な横断監査禁止/同一記事の複数候補生成禁止/既存asset再利用/個別segment対応優先。
---

## 事前指定Read一覧

- `docs/pm/RESULT_PACKET_UT06_A.md`: 12-35行(Part2/Part3の前回状態: Lock解除API、attempt4結果、A2の失敗2 segmentのdiff、使用したdriver名)
- `er014_output/four_type_observation_01/discovery/run_discovery_b1b_part2_retry_ut06.py`: 全文(委任Aで作成したB1 part2 retry driver。分割版driverの複製元)
- `er014_output/four_type_observation_01/discovery/run_discovery_a2_ut06_regen.py`: Grepで`run_tts|approve_regenerate|full_story_part1|point_two|def main|argparse`→該当範囲Read(A2 driver、2 segment限定retryの組み込み先)
- `er014_output/four_type_observation_01/discovery/audio/parts.json`(またはB1 part分割定義ファイル、Grep`full_story_part2`で特定): 該当entry(canonical part2テキスト)
- `er014_output/four_type_observation_01/discovery/audio/tts_reading_transforms.json`: Grepで`full_story_part2`→該当entry(TTS入力の読み整形後テキスト)
- `er014_output/four_type_observation_01/discovery/audio/b1b/audit/review_lock_state.json`: 全文(小ファイル)
- `er011_human_review_lock_01.py`: Grepで`def approve_regenerate|def check_before_generation|def guarded_generate`→シグネチャ範囲のみ(委任Aで確認済み内容の再確認は最小限)
- `er014_output/four_type_observation_01/discovery/run_discovery_audio_completion.py`: Grepで`def run_assembly|def run_tts|segment_order|SEGMENT_ORDER|full_story_part`→Assemblyがsegment一覧をどこから読むか(分割後の`full_story_part2a`/`part2b`をAssembly順序に組み込む箇所)を範囲Read
- `docs/pm/PM_GOVERNANCE.md`: Grepで`15-8`→該当節(費用報告)
- `docs/pm/PM_BRIEF.md`: 135-159行(ACTIVE_TASK固定ヘッダ)

## 事前指定Grep一覧+追記位置・更新位置の手順

1. B1 part2分割点: `Grep pattern="2,500 college students" path=er014_output/four_type_observation_01/discovery/ glob=*.json output_mode=content -B 3 -A 3`→canonical part2内の段落構造を確認し、自然なparagraph/semantic boundary(「2,500人/11か国」段落の**直前の段落境界**が第一候補。当該段落が後半segmentの**先頭または前半**に来るように分割し、末尾に置かない)で`full_story_part2a`/`full_story_part2b`に分割。分割はTTS入力の分割のみで、canonical本文(parts.json等)の文字列は一切変更しない(2a+2bの連結=元part2と完全一致することをpythonで検証・報告)。
2. Lock: `review_lock_state.json`はcumulative_tts_attempts=6・HUMAN_REVIEW_REQUIRED。分割版はsegment名が変わるため、新segment(2a/2b)に対してLockがどう働くかを`check_before_generation`のhash照合対象から確認。既存Lock機構を迂回せず、`approve_regenerate`をユーザー承認(FOLLOWUP-01項目4、2026-09-15)を理由として2a/2bそれぞれ1回ずつ呼ぶ(各segmentの既存cascade[標準2+fallback1]内は許容、それを超える自動retryは禁止)。
3. B1検証: 2a/2bそれぞれ現物音声でASR→canonical(読み整形後テキスト)とのdifflib語単位diffでdelete blockが0、特に「a study of about 2,500 college students in 11 countries … phone use.」が全文含まれること。軽微な表記差(数字表記・ダッシュ・句読点)は既存Gate判定に従う(Gate緩和はしない)。PASS後、Assembly順序に2a→2bを`full_story_part2`の位置へ組み込み(本記事driver内の個別対応、共通Assembly関数は編集しない)→Audio Validation→`audio/b1b/player.html`生成(B1標準playerは未生成のため新規)+`web_delivery.json`+`human_review_player.html`に「attempt5(分割版、採用)」を追記。
4. A2 retry: `run_discovery_a2_ut06_regen.py`に「対象segment限定retry」引数(`--only-segments full_story_part1,point_two`)を追加し、他14 segmentの音声・Support・Key Phraseは`.ok`/resumable機構で再利用(再TTS・再ASRしない。他segmentのwav sha256が不変であることを実行前後で比較・報告)。2 segmentは`approve_regenerate`(ユーザー承認FOLLOWUP-01項目5)で既存cascade 1周(標準2+fallback1)を許可。検証: 現物ASRで`point_two`に「2,557」(ASR表記が"2,557"/"2557"/"two thousand five hundred fifty-seven"のいずれかで数値一致)が含まれること必須、`full_story_part1`に語の置換(silence→pause等)がないこと。句読点・文境界のみの差はGate判定に従う。PASS後、Assembly→Audio Validation→`audio/a2/player.html`更新(530語版)+`web_delivery.json`更新。旧604語版のplayer/mp3は委任Aで`audio/a2_before_regeneration_604w/`へ退避済みであることを確認(上書きしない)。
5. `production_set_cost.json`: `production_set_total_cost_including_audio_jpy`を¥822.07(委任A後)+本Part 2実費へ更新(Part 1のB1費用も同様に記録フィールドがあれば加算)。
6. SSOT追記位置: `Grep pattern="^## USER-TEST-FINAL-AUDIO-BATCH-06(委任C" path=DECISION_LOG.md`→そのエントリ末尾直後に「委任D」エントリ追加(索引1行も)。`OPEN_ITEMS.md`はpythonで行末追記: OPEN-153(B1: 分割対応の事実・結果、恒久対策[長segment後半block omission/segment分割の必要性]はdefer)、OPEN-135(A2: 2 segment retry結果、TTS数字誤読の事実、恒久対策defer)。新番号は起票しない。
7. `docs/pm/MODEL_ROUTING_TRIAL_LOG.md`末尾に該当行を既存形式で追加(LLM未使用なら追記不要)。

## 実行コマンド全文

作業ディレクトリ`C:\Users\tensh\eigo-radio`、pythonは`.venv\Scripts\python.exe`。

T-0:
```
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\USER-TEST-FINAL-AUDIO-BATCH-06_D.md --json-out docs\pm\delegation_log\USER-TEST-FINAL-AUDIO-BATCH-06_D_check.json
```

Part 1(B1、上限¥25): `run_discovery_b1b_part2_retry_ut06.py`を複製して`run_discovery_b1b_part2_split_ut06.py`を作成(分割・2a/2b TTS・ASR照合・Assembly順序組み込み・Audio Validation・player生成を本記事専用に実装)。
```
.venv\Scripts\python.exe er014_output\four_type_observation_01\discovery\run_discovery_b1b_part2_split_ut06.py --split-at-paragraph-before "a study of about 2,500 college students" --approve-reason "USER-TEST-FINAL-AUDIO-BATCH-06-FOLLOWUP-01 item4 user-approved split TTS 2026-09-15" --budget-jpy 25
```
(実引数はGrep 1で確定した分割点に合わせて調整し全文報告。)

Part 2(A2、上限¥15、Part 1のcommit後):
```
.venv\Scripts\python.exe er014_output\four_type_observation_01\discovery\run_discovery_a2_ut06_regen.py --only-segments full_story_part1,point_two --approve-reason "USER-TEST-FINAL-AUDIO-BATCH-06-FOLLOWUP-01 item5 user-approved 2-segment retry 2026-09-15" --budget-jpy 15
```

分割検証(Part 1、実構造に合わせてキー名調整可):
```
.venv\Scripts\python.exe -c "import json;p=json.load(open('er014_output/four_type_observation_01/discovery/audio/parts.json',encoding='utf-8'));print('PART2_LEN=',len(p['full_story_part2']) if isinstance(p,dict) and 'full_story_part2' in p else 'KEY?')"
```
(2a+2b連結==元part2の検証結果`SPLIT_CONCAT_EQUAL=True`を必ず報告。)

Web到達確認(各commit・push後、raw.githackはUser-Agent付きGET、CDN遅延時60秒待ち最大3回):
```
.venv\Scripts\python.exe -c "import urllib.request as u;[print(u.urlopen(u.Request(x,headers={'User-Agent':'Mozilla/5.0'})).status,x) for x in ['https://raw.githack.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/discovery/audio/b1b/player.html','https://raw.githack.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/discovery/audio/a2/player.html']]"
```
episode mp3 direct URL(B1/A2各1件、`web_delivery.json`の実ファイル名)も同様にGET確認、計4件のstatusを報告。

回帰: Discovery配下に該当テストなし(委任Aで確認済み)。新規テストは作らない。

## SSOT追記文

`DECISION_LOG.md`(委任Cエントリ末尾直後):
```
## USER-TEST-FINAL-AUDIO-BATCH-06(委任D: Discovery B1 part2分割TTS+A2 NG 2 segment retry)

- 日付: 2026-09-15
- 種別: Discovery記事の音声完成(ユーザー判断FOLLOWUP-01項目4・5による個別対応、恒久対策なし)
- Discovery B1: full_story_part2を<分割点の説明>で2a/2bに分割してTTS(canonical不変、2a+2b連結=元part2一致)。ユーザー承認によりLock解除(各1回)。結果: <PASS(delete block 0、2,500人/11か国段落包含)/STOP(欠落再発: 内容)>。Audio Validation <PASS/FAIL、duration秒>。B1標準player<新規生成/未生成>。費用¥<実測>(TTS/ASR)。Status=<USER_LISTENING_PENDING/USER_DECISION_REQUIRED>。恒久対策(長segment後半block omission/segment分割の必要性)はOPEN-153へ事実追記のみ、defer。
- Discovery A2: full_story_part1/point_twoのみ個別retry(他14 segment・Support・Key Phrase不変、wav sha256一致<n>件)。結果: <PASS(2,557正読、語置換なし)/STOP(内容)>。Audio Validation <PASS/FAIL、duration秒>。530語版player公開(WORD_COUNT_GE_500報告義務該当、ユーザー承認済み)。費用¥<実測>。Discovery Production 1生成セット総原価=¥822.07+¥<実測>=¥<合計>。Status=<USER_LISTENING_PENDING/USER_DECISION_REQUIRED>。恒久対策(TTS数字誤読/ASR表記差)はOPEN-135へ事実追記のみ、defer。
- 参照: `docs/pm/RESULT_PACKET_UT06_D.md`、commit <B1 hash>/<A2 hash>
```
索引1行。`OPEN_ITEMS.md`行末追記(python): OPEN-153 ` 2026-09-15追記(UT-06 D): part2を2 segment分割してTTS→<結果>。恒久対策defer(長segment後半block omission、segment分割の必要性)。`、OPEN-135 ` 2026-09-15追記(UT-06 D): NG 2 segment個別retry→<結果、2,557正読有無>。530語版player<公開/未公開>。恒久対策defer(TTS数字誤読、ASR表記差)。`
`docs/pm/ACTIVE_TASK.md`: 固定ヘッダ形式で上書き(報告単位Status: Family C 4 episode=USER_LISTENING_PENDING、Home robots A2/B1=VALIDATED、Discovery B1=<状態>、Discovery A2=<状態>)。

## Git(明示add対象・コミットメッセージ・trailer)

- Part 1・Part 2で分けてcommit。明示add対象(wav除外、mp3必須): 新規/更新driver(`run_discovery_b1b_part2_split_ut06.py`、`run_discovery_a2_ut06_regen.py`)、`er014_output/four_type_observation_01/discovery/audio/b1b/`配下(player.html、human_review_player.html、web/**/*.mp3、audit/*.json、narration/attempts/*.json、web_delivery.json)、`audio/a2/`配下(player.html、web/*.mp3、audit/*.json、web_delivery.json)、`production_set_cost.json`、`audio/raw_usage_log_audio_completion.jsonl`、`DECISION_LOG.md`、`OPEN_ITEMS.md`、`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`(更新時)、`docs/pm/delegation_log/USER-TEST-FINAL-AUDIO-BATCH-06_D.md`、同`_check.json`、`docs/pm/RESULT_PACKET_UT06_D.md`。
- `er013_output/`・`er006_output/`・`er011_output/`の既存M、`docs/pm/ACTIVE_TASK_*.md`/`RESULT_PACKET_*.md`の既存??は触らない。
- コミットメッセージ: `USER-TEST-FINAL-AUDIO-BATCH-06 (D-B1): Discovery B1 part2分割TTS(個別対応)` / `USER-TEST-FINAL-AUDIO-BATCH-06 (D-A2): Discovery A2 530語版 NG 2 segment個別retry+player公開`
- trailer: `Task-ID: USER-TEST-FINAL-AUDIO-BATCH-06`
- push: 各commit後`git push origin main`。STOP時は完了分のみcommit。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_UT06_D.md`に:
1. T-0結果
2. Part 1 B1: 分割点(前後段落の先頭文)、`SPLIT_CONCAT_EQUAL`結果、Lock解除記録、2a/2b各TTS attempt数、ASR diff(delete/insert/replace一覧、2,500人段落包含)、PASS/STOP判定、Assembly順序、Audio Validation(PASS/FAIL、duration)、player URL/direct audio URL、費用(TTS/ASR/その他)、再生成回数、STOP時は個別対応候補3件以内
3. Part 2 A2: 対象2 segmentのattempt数、ASR全文とcanonical diff、「2,557」の読み結果、他14 segment sha256不変件数、PASS/STOP判定、Assembly・Audio Validation(PASS/FAIL、duration)、player URL/direct audio URL、費用、word_count=530(WORD_COUNT_GE_500明記)、Production 1生成セット総原価更新値
4. ユーザー指示17のClosout項目(B1/A2各)
5. Token節約報告(Sonnet委任回数=1、Opus不使用、再利用asset、回避した再生成)
6. Web到達確認(4 URL)
7. commit hash・push結果・残差分要約
8. unresolved issue(恒久defer事項の追記先)
9. 事前指定外Read(理由付き)

ユーザー向け表記は「B1」に統一(「B1B」不使用、内部識別子`b1b`はそのまま)。

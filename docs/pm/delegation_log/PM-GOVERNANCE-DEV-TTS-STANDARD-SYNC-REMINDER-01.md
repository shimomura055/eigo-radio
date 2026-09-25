## 管理ID(2件を1委任で直列実施。SSOT衝突回避のため)
(A) `PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`(既存ガバナンスの再確認・運用是正、新仕様ではない)
(B) `TOPIC-DISCOVERY-MANUAL-SELECTION-OPERATING-POLICY-01`(記録のみ、`DECIDED / OPERATING_POLICY_ONLY`)
**並行タスクあり**: 別sonnet-workerが`KEY-PHRASE-LEVEL-SPEC-TRIAL-01_REPORT.md`と`_KP`一時ファイルのみ編集中(SSOT・er0*には触れない)。本タスクは標準`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`。commit時`index.lock`は10秒待ち再試行(最大3回)。他タスクのstaged変更が混在していれば自タスクのパスだけを`git commit <paths>`で対象指定。`ACTIVE_TASK*`/`RESULT_PACKET*`/`.env`はaddしない。履歴操作禁止。trailer必須(commitは(A)(B)で分け、各trailerを付ける)。API呼び出し・TTS実行・Search実装・フォーム/UI作成・自動選定ロジック・新Trial・Production wiring・rerank再実行は禁止。実行済みE2E Run(`er012_output/e_family_two_level_wiring_01/`)の成果物は変更・再実行しない。

## 固定ブロック
E-1/D-1/G-1/F-1(前回同一)。T-0: 本委任文を`docs/pm/delegation_log/PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01.md`へ保存し`check_delegation_prompt.py`実行、結果をRESULT_PACKETへ1行(FAILでも継続)。(B)の指示全文は同ファイル末尾に併記。

## (A) TTS Standard同期の是正
### ユーザー指示(逐語要点)
正式リリース前の開発・Trial・検証・Production wiring・runtime evidence取得では、特別な理由やユーザー指示がない限り必ずStandard同期TTSを使用。`TTS_EXECUTION_MODE=STANDARD`を明示/低レベル実装の`DEFAULT_TTS_EXECUTION_MODE=BATCH`に依存しない/「Production経路だからBatch」と解釈しない/「Production相当」「runtime evidence」でも正式リリース前はStandard同期/Batchを使う場合はPM_GOVERNANCEの例外条件に該当する理由を事前明示。今回のE2E runner・今後新設する開発用runner・Trial harnessについてStandard同期指定漏れを確認し、必要なら既存ルールに沿って是正。実行済みBatch Runは変更・再実行しない。

### 事前指定Read
- `docs/pm/PM_GOVERNANCE.md`: Grep `## 7\.|7-1|7-2|7-3|Standard同期|例外`→§7本文(既存ルール、変更しない)。
- `er006_batch_tts_wiring_01.py`: Grep `TTS_EXECUTION_MODE|DEFAULT_TTS_EXECUTION_MODE|def resolve_tts_execution_mode|def make_batch_tts_call_fn`(**既定値は変更しない**=量産Production既定を守る)。
- `er012_e_family_entertainment_two_level_runner_01.py`: Grep `tts|TTS_EXECUTION_MODE|argparse|def main|environ`→TTS呼び出し箇所。
- 横展開点検: `Grep pattern="tts_generate|make_batch_tts_call_fn|run_tts|TTS_EXECUTION_MODE" glob="er0*.py" -l`→TTSを呼ぶrunner/harness一覧。各ファイルで`TTS_EXECUTION_MODE`を明示しているかをGrepで判定し一覧化(`docs/pm/tts_mode_audit_2026-09-25.md`: ファイル/種別[Production量産経路・開発runner・Trial harness・テスト]/明示有無/是正要否)。
- `docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.md`: Grep `固定ブロック|T-0|E-1`→固定ブロック位置。`docs/pm/tools/check_delegation_prompt.py`: Grep `def |REQUIRED|warn`→警告追加位置。

### 実装
1. **E2E runner是正**: `er012_e_family_entertainment_two_level_runner_01.py`に `--tts-mode {STANDARD,BATCH}`(既定`STANDARD`)を追加し、実行時に`os.environ["TTS_EXECUTION_MODE"]`へ明示設定。`BATCH`指定時は`--batch-reason "<PM_GOVERNANCE §7の例外条件>"`必須(未指定ならエラー)。runtime evidence(`entry_point.json`等)に`tts_execution_mode`と理由を記録。既存テスト`er012_e_family_entertainment_two_level_runner_test_01.py`に既定STANDARD・BATCH理由必須のテストを追加。
2. **横展開是正**: 点検一覧で「開発runner/Trial harness」に分類され明示が無いものは、同じ方式(既定STANDARD、BATCHは理由必須)で是正。**Production量産経路(既存Family A/Bの正式runner)は挙動を変えない**(点検一覧に「量産経路のため既定BATCH維持」と記録)。分類に迷うものは是正せず一覧に「要判断」と記録。
3. **委任テンプレート**: 固定ブロックに `T-1(2026-09-25、PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01): TTSを伴う委任は、正式リリース前である限り \`TTS_EXECUTION_MODE=STANDARD\` を実行コマンドに明示する(PM_GOVERNANCE §7)。Batchは§7例外条件の理由を委任文に明示した場合のみ。` を追加。`check_delegation_prompt.py`に、委任文に`TTS|tts|音声化|narration`を含み`TTS_EXECUTION_MODE=STANDARD`も`batch-reason`も含まない場合の**警告(FAILにしない、reasonsに記録)**を追加。テストがあれば追加。
4. **記録**: DECISION_LOGに本ID(A)で「既存§7の再確認・運用是正。E2E-WIRING-01で既定BATCH依存により約4時間のBatch待ちが発生したことを契機。実施内容1〜3。新仕様ではない」を追記。PM_GOVERNANCE本文は変更しない(§7末尾に「運用是正履歴: 2026-09-25 本ID」の1行追記のみ可)。

## (B) Topic Selection量産初期運用方針の記録(記録のみ)
### 事前指定Read
- `CURRENT_SPEC.md`: Grep `Topic Selection|Topic Search|TOPIC-DISCOVERY|Sensor`→既存記載位置(あれば隣接、無ければ適切な章末に新設)。`DECISION_LOG.md`末尾形式。`OPEN_ITEMS.md`: Grep `OPEN-17[7-9]|OPEN-18`→最大番号。
### 追記内容
- **CURRENT_SPEC**(見出し「Topic Selection量産初期運用方針(Production仕様ではない、DECIDED / OPERATING_POLICY_ONLY、2026-09-25ユーザー決定)」として1エントリ、逐語要約): 1.完全自動Topic Selectionは未実施(AI単独の選定精度が未安定。数十件の教師例でPromptを複雑化せず、実運用で数百件規模のユーザー選定データを蓄積してから自動化精度を高める)。2.量産初期の基本フロー(AIが複数の定点Sensorサイトを巡回→各サイト原則3記事程度+日本トップ3件+世界トップ3件を候補へ→AIが候補ごとにHook/仮タイトル・概要・切口を提示→ユーザーがフォーム等で10記事程度を選定→AIが記事生成。ユーザー対応不可時はAI自動選定fallbackを将来用意。選定実績を蓄積し十分なデータ後に完全自動化を再検討。フォーム仕様・実行タイミング・自動化条件は未設計)。3.学習データ(選択された候補=Positiveと、候補に出たが未選択=Negativeの両方を保存。数百例蓄積後に改善)。4.Sensorサイト候補(海外: 404 Media/Oddity Central/PsyPost/Axios/Semafor/Ars Technica。国内: GIGAZINE/ナゾロジー/デイリーポータルZ/カラパイア/Togetter/ITmedia NEWS/東洋経済オンライン。除外済み: Know Your Meme/まいどなニュース/Jタウンネット。Pool は今後変更可、恒久固定仕様ではない)。5.候補抽出の優先順位(優先1: サイト自身の人気・注目シグナル[24時間ランキング/Access Ranking/Most Read/Popular/Editor's Pick/Top Stories等]を入口に。優先2: 無ければAIが直近記事から判断[Hookの強さ/一般読者への広さ/Self relevance/「え、そうなの？」感/自然なAngle展開/話したくなるか/日本人読者との接点/教育的説明で終わらないか]。人気ランキングをそのまま採用せず、その中からeigo-radio向け候補を選ぶ)。6.直近性(原則直近24時間中心。更新頻度が低い媒体・Evergreen媒体・非常に強い題材の扱いは後日。厳格な24時間ルールをProduction仕様として固定しない)。7.タイトル/Hookの固有名詞方針(不要な固有名詞を避ける。例: freeeが止まったら？→給料日に会計ソフトが止まったら、会社はどうなる？/美味しんぼの海原雄山→昔の人気漫画の"厳しい名物キャラ"、今ならカスハラ？/GoogleがAIデータセンターを宇宙へ→AIデータセンターは、ついに宇宙へ行く？。理由: 固有名詞を知らない読者は自分に関係ないと判断しやすい。完全禁止ではなくTrump/ChatGPT/iPhone/大谷翔平のように広い認知・集客力がある場合は可。判断原則: その固有名詞を知らなくてもTopicの魅力が伝わるか)。8.Topic Discovery思想(記事は完成TopicではなくSeed。Source発見→面白いAngle→必要なら追加検索→一般人との接点→Hook/Topic Package化。記事タイトルをそのまま採用しない。Big News→自分事へ/科学→驚き・人間との接点へ/Tech→技術説明ではなく生活変化へ/SNS→Fact SourceではなくTopic Sensor/小ネタ→可愛い・珍しいで終わらずWhyへ)。9.日本/世界トップニュース枠(毎回日本3件+世界3件を候補に追加。Sensorサイトの取りこぼし補完。Big Newsもそのまま採用せず「なぜ一般人に関係するのか」までAngle化)。10.今回確認できた好例12件(悪い言葉でも、笑えると集中を邪魔しなくなる？/人は「いいね」より「イマイチ」に流されやすい？/自己主張が強い人ほどリーダーになる。でも実力とは別？/憧れの車中泊、実際にやったら一睡もできなかった？/イランは戦争を終わらせる道筋を米国に示した？/40年間禁止だったサッカー観戦中のビールが復活する？/アルツハイマーの兆候は、検査で見つかる7年前から脳に出ている？/量子コンピュータが来る前に、暗号をもっと速く破る方法が見つかった？/火事なのに、鳥は炎へ向かって飛んでいく？/金星は、自分の月を食べてしまった？/AIデータセンターを宇宙へ？/80歳まで住宅ローンを払うのが普通になる？。固定ルールや少数Teacherだけで過学習させない)。11.未決(フォーム具体設計/入力タイミング/候補件数の正式値/選定件数の正式値/自動選定fallback条件/完全自動化へ移行する件数・基準/Sensor巡回頻度/24時間条件の厳密性/人気ランキング取得方式/保存schema/自動学習・rerank実装方式。勝手に仕様化・実装しない)。
- **DECISION_LOG**: 本ID(B)でユーザー決定(2026-09-25)を記録(Status `DECIDED / OPERATING_POLICY_ONLY`、Production Search実装ではない、既存Topic Discovery Trial結果・OPEN-178/179は上書きしない)。
- **OPEN_ITEMS**: 新規1件(次番号)「Topic Selection量産初期運用の未設計項目(11点)」として上記11点を列挙、Status OPEN(設計待ち)。既存OPEN-178/179は変更しない。

## 実行コマンド全文
```
cd C:\Users\tensh\eigo-radio
.venv\Scripts\python.exe -m unittest er012_e_family_entertainment_two_level_runner_test_01 -v
.venv\Scripts\python.exe -m unittest discover -s . -p "*_test_01.py"
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01.md --json-out docs\pm\delegation_log\PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01.md_check.json
git status --short
```

## Git(2 commit)
(A) 明示add: 是正したrunner/harness・テスト、`docs/pm/tts_mode_audit_2026-09-25.md`、`docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.md`、`docs/pm/tools/check_delegation_prompt.py`(+テスト)、`DECISION_LOG.md`、`docs/pm/PM_GOVERNANCE.md`(1行追記時のみ)、delegation_log+`_check.json`。メッセージ: `PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01: 正式リリース前TTSはStandard同期(PM_GOVERNANCE §7)の運用是正—E2E runner/開発runner/Trial harnessにTTS_EXECUTION_MODE=STANDARD既定とBATCH理由必須を追加、委任テンプレートT-1追加、点検一覧記録(量産経路の既定は不変)` trailer `Management-ID: PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`。
(B) 明示add: `CURRENT_SPEC.md`、`DECISION_LOG.md`、`OPEN_ITEMS.md`。メッセージ: `TOPIC-DISCOVERY-MANUAL-SELECTION-OPERATING-POLICY-01: Topic Selection量産初期運用方針(手動選定・Sensor Pool・候補抽出優先順位・固有名詞方針・学習データ保存)をDECIDED / OPERATING_POLICY_ONLYとしてSSOTへ記録、未設計11項目をOPEN_ITEMSへ(実装なし)` trailer `Management-ID: TOPIC-DISCOVERY-MANUAL-SELECTION-OPERATING-POLICY-01`。

## 報告(RESULT_PACKET)
0. T-0 1. (A)点検一覧の要約(件数・是正した/しない/要判断) 2. (A)runner・テンプレート・checkerの変更点、テスト結果(新規+regression) 3. (A)DECISION_LOG逐語 4. (B)CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS追記逐語(OPEN番号) 5. commit SHA×2・push 6. `git status --short` 7. 一覧外Read理由、要判断項目(事実列挙)。

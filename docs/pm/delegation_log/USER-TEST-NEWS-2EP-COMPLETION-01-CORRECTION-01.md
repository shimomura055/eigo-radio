# Delegation Prompt: USER-TEST-NEWS-2EP-COMPLETION-01-CORRECTION-01

## 管理ID

`USER-TEST-NEWS-2EP-COMPLETION-01-CORRECTION-01`(親: `USER-TEST-NEWS-2EP-COMPLETION-01`、現在main=`36781ebc`)。並行タスクなし。報告は`docs/pm/RESULT_PACKET_NEWS_2EP_CORRECTION.md`(新規)へ。`docs/pm/ACTIVE_TASK.md`は固定ヘッダ形式で上書き可(UDR-deferred/APPROVED未配線欄は前回内容を引継ぎ)。

## 性質/到達上限Status/禁止事項

- 性質: Space Weapons A2 `full_story_part1`のHuman Review Lockについて、Human承認へ進む前に、既存Production仕様「Pronunciation Ledger → Azure Secondary ASR + Phrase List」経路が正しく実行されたかを是正・確認する。**新仕様Trialではない。既存Production仕様の本来の経路を正しく実行することだけが目的。**
- 到達上限Status: **`CORRECTION_VERIFIED`**まで。Phrase List付きSecondary ASRで後続処理が自動的に正常化できる場合のみ、既存Production仕様に従ってA2 Assembly/Audio Validation Gateまで進めてよい。`USER_DECISION_REQUIRED`は是正確認待ちとして扱い、**ユーザーへ`HUMAN_APPROVED`を求めない・Human Reviewを通過させない・`HUMAN_APPROVED`を勝手に記録しない**。
- 禁止: TTS再生成、Writer再実行、Research/Fact Checker再実行、別モデル切替、Prompt変更、新validator開発、新辞書方式、IPA等をAzureへ直接渡す新仕様、無関係な追加Trial、「念のため」の複数案検証、Productionコード改修(`er006_*.py`/`er003_*.py`/`er011_*.py`等)、SSOT変更、Theme 2(AI Control)着手、Space Weapons B1音声着手、DEV/Trial専用機構のProduction仕様としての暗黙利用、DEV手作り判定での代用、`git add -A`/`stash`/`amend`/`rebase`/`force push`、wavのcommit。
- 必要なのは **既存音声 × 正式Secondary ASR × Phrase List** の再検証のみ。問題が出たら追加トライせずSTOP。

## STOP条件(該当したらその場でSTOPし報告、別案・別モデル・Prompt変更・追加Trialへ進まない)

- Phrase List付きでも解決しない(→ケースB: `USER_DECISION_REQUIRED`、HUMAN_APPROVED記録禁止・TTS再生成禁止)
- Production正式経路からPhrase List付きSecondary ASRを実行できない(→ケースC: 承認済みProduction仕様の配線不備候補として報告、独自修正禁止)
- 新仕様やコード改修が必要
- CURRENT_SPECと実装が矛盾(Dangling Reference)
- Human Review以外の新しいblocker発生
- ユーザー判断が必要/想定外のAPI再実行が必要
- B1 Fact Checker REVIEW_REQUIREDの「non-blocking advisory」定義が既存CURRENT_SPEC/DECISION_LOGで確認できない

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Readを基本、全文Readは構造変更時のみ。G-1: git出力は`--porcelain`/`--stat`/`--short`で最小化。F-1: transcript退避不要。T-1: 事前指定Read/Grep一覧に従い、一覧外の追加Readは理由をRESULT_PACKETに1行記録。T-0: 委任文を`docs/pm/delegation_log/USER-TEST-NEWS-2EP-COMPLETION-01-CORRECTION-01.md`へ保存し`.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行、結果をRESULT_PACKETへ1行記録(FAILでも継続)。

## ユーザー指示(原文要旨、忠実転記)

### 現在確認できている事実
対象: `er014_output/user_test_news_2ep_01/space_weapons/a2/narration/attempts/full_story_part1_attempt2_custom35d6860b.json`。primary_1/primary_2=`Troy Mink`、secondary_1/secondary_2=provider `azure`・`Troy Mink`・**`phrase_list_used=false`**。したがって「Primary/Secondary双方でMeink→MinkとなったためHuman Review」では不十分で、正確には「Azure Secondary ASRは実行されたが、Troy Meink/MeinkをPhrase Listへ渡していない状態で2回実行され、その後Human Review Lockへ進んだ」状態。

### 1. 現行Production仕様を再確認
CURRENT_SPEC.mdにおける固有名詞ASR fallback仕様/ProductionでSecondary ASRが有効であること/Azure PhraseListGrammarの実装/Pronunciation Ledger→Phrase Listへの入力経路/retry・fallback・regenerationで同仕様がどう呼ばれるか。実ファイル・関数名付きで報告。特に`get_hint_for_text()`等から既存Ledgerの候補をSecondary ASRへ渡す経路と、未登録entityをHuman Review用に調査する経路の**実行順序**を確認。

### 2. `Troy Meink / Meink`のPronunciation Ledger状態
Secondary ASR実行時点で登録されていたか確認。未登録だった場合「なぜProduction cascade開始前にLedger候補として取得されなかったのか」を特定(広範な改修はしない)。

### 3. 既存仕様の範囲でPhrase Listを準備
既存Productionの正式なPronunciation Ledger/pronunciation research機構だけを使い、`Meink`をAzure Secondary ASRへ渡せる状態にする。新辞書方式・新Prompt・新validator・IPA直接渡し禁止。

### 4. 現在の音声をそのまま再検証
**TTS再生成禁止。**既存`full_story_part1`音声でAzure Secondary ASRをPhrase List付きで再実行。runtime evidenceとして provider=azure/phrase list内容/`Meink`が含まれること/`phrase_list_used=true`/ASR transcript/classification・verdict を保存・報告。**既存Production cascadeの正式関数から実行**(DEV専用手作り判定で代用しない)。

### 5. 結果に応じた処理
A. 正常解決: 既存Production仕様に従ってHuman Review Lockを解除できるか確認し、正式経路で解除可能ならそれを使い、A2 Assembly→Audio Validation Gateまで進める。PASS時はruntime evidenceを報告。
B. Phrase Listでも`Meink`が解決しない: STOP。HUMAN_APPROVED記録禁止、TTS再生成禁止。報告=Phrase List付きSecondary ASRを正しく実行した証拠/実際のASR transcript/Ledger内容/なぜHuman Reviewがなお必要か。この場合のみ再度`USER_DECISION_REQUIRED`。
C. Phrase List付きSecondary ASR経路自体がProductionで正しく呼べない: STOP。記事個別の問題ではなく**承認済みProduction仕様の配線不備候補**として報告。コード修正・仕様変更禁止。

### B1 Fact Checker
是正対象外。Space Weapons B1の`Fact Checker REVIEW_REQUIRED`が既存CURRENT_SPEC/DECISION_LOGで本当にnon-blocking advisoryとして定義されていることだけ再確認(行番号付き)。既存仕様どおりなら扱い維持。不一致があればSTOP。

### Theme 2
是正確認が終わるまでAI Control記事作成を開始しない(PM Gate 6)。

### Dangling Reference Check
Pronunciation Ledger/Secondary ASR/Phrase List/Human Review Lockについて、CURRENT_SPEC上の正式Production仕様と実コードの参照先が一致していることを確認。

### 受入条件
1. 現行Production仕様のSecondary ASR+Phrase List経路を確認 2. `Troy Meink/Meink`のLedger状態を確認 3. `Meink`をPhrase Listへ含めているruntime evidenceあり 4. `phrase_list_used=true`の証跡あり 5. 既存音声でSecondary ASR再実行 6. TTS再生成なし 7. 新仕様・新Prompt・新validatorなし 8. 解決なら正式経路でA2 Assembly/Gateまで確認 9. 未解決ならHuman承認せずUSER_DECISION_REQUIREDでSTOP 10. Production配線問題なら独自修正せずSTOP

## Fableからの補足(事前調査、read-only)

- `er006_output/pronunciation_ledger_01/ledger.json` L557-576付近に**`Meink`エントリが現時点で存在**: `entity_type="cascade_unresolved_entity"`、`canonical_spelling="Meink"`、`expected_pronunciation_ipa="/ˈmeɪŋk/"`、`pronunciation_hint="MAY-ngk"`、`alternate_pronunciations=["/ˈmɪŋk/ (possible…not directly verified)"]`、**`confidence="low"`**。entity_typeから、cascade未解決後のpronunciation research(Perplexity `sonar`)で**事後登録**された可能性が高い(=Secondary ASR実行時点では未登録→`phrase_list_used=false`という順序問題の仮説)。この仮説を実コードの実行順序で検証すること。
- Phrase List実装: `er006_secondary_asr_01.py`(L74-98 `PhraseListGrammar.from_recognizer`、L304-318/L331/L375/L444/L527/L574-600/L662-696で`ledger_phrases`→`phrases=`、`"phrase_list_used": bool(ledger_phrases)`)。Ledger取得: `er006_pronunciation_ledger_01.py` L93 `get_hint_for_text(text, min_confidence)`(既存呼び出し例は`min_confidence="low"`、例: `er003_v1_crosslevel_audio_02_common.py` L126-133)。
- **未確認(Sonnetが確認)**: 本記事の音声生成に使われた`er003_v1_n3_01_tts_generate.py`(および実際に呼ばれたcascade入口)が`ledger_phrases=`を渡しているか、`min_confidence`は何か、そして`confidence="low"`の現Ledgerエントリが`get_hint_for_text`で拾われるか。`er006_audio_cost_spec_fix_01_static_audit.py`(LEDGER_PHRASES_MARKER監査)も参考。
- CURRENT_SPEC.md: Secondary ASR/Phrase List関連行はL1121・1191・1225・1239・1273-1284(Human Review Route L1278)付近、ER-006-PRONUNCIATION-LEDGER-SECONDARY-ASR-01参照L1392付近。Fact Checker REVIEW_REQUIREDの扱いはGrep `REVIEW_REQUIRED`(L403/1094/1224付近)+DECISION_LOG.md Grep `ER-010-NO9`。
- 前回runのHuman Review Lock状態: `er014_output/user_test_news_2ep_01/space_weapons/a2/audit/review_lock_state.json` L374-393、Gate結果: `.../a2/audit/assembly_and_gate_summary.json`。前回driver: `er014_output/user_test_news_2ep_01/space_weapons/run_pipeline.py`。

## 事前指定Read/Grep一覧

- `CURRENT_SPEC.md`: 上記行番号周辺のみ+Grep `Human Review|HUMAN_APPROVED|record_human_approval|approve_regenerate|Phrase|Secondary ASR|min_confidence|pronunciation research|Pronunciation Research`
- `er006_secondary_asr_01.py`: Grep `def |ledger_phrases|phrase_list_used|FEATURE_FLAG|is_entity_like_mismatch|research|Human`→該当関数のみRead
- `er006_pronunciation_ledger_01.py`: L93前後(`get_hint_for_text`のconfidence filter)+Grep `def |confidence|cascade_unresolved_entity|research`
- `er003_v1_n3_01_tts_generate.py`: Grep `ledger_phrases|get_hint_for_text|evaluate_attempt_with_cascade|secondary_asr|review_lock|pronun`→該当箇所のみ
- `er011_human_review_lock_01.py`: Grep `def |HUMAN_APPROVED|VALIDATED|state`→解除の正式経路(再検証結果でVALIDATEDへ戻す正式関数があるか、HUMAN_APPROVED以外の遷移が仕様上許されるか)
- `er006_output/pronunciation_ledger_01/ledger.json`: Meinkエントリ(L557-576)+同エントリの`created_at`/`source`系フィールド(登録時刻と前回cascade実行時刻の前後関係)
- `er014_output/user_test_news_2ep_01/space_weapons/a2/narration/attempts/full_story_part1_attempt*.json`: cascade evidence(timestamps含む)
- DECISION_LOG.md: Grep `ER-010-NO9|REVIEW_REQUIRED.*advisory|non-blocking`該当行のみ
- `docs/pm/PM_BRIEF.md` L135-159(固定ヘッダ書式)

## 手順

1. T-0。
2. 仕様・コード確認(上記一覧)→実行順序(Ledger hint取得→Secondary ASR→未解決entity research→Ledger登録)と、今回`phrase_list_used=false`になった**直接原因**を特定(例: 実行時点でLedger未登録/`min_confidence`でlowが除外/呼び出し側が`ledger_phrases`を渡していない、のいずれか)。
3. 現Ledger状態で`get_hint_for_text(<full_story_part1 canonical text>, min_confidence=<Production経路と同じ値>)`が`Meink`を返すか確認(read-only、API 0)。返さない場合、既存Production機構の範囲でPhrase Listへ渡せる方法があるか(既存の正式`min_confidence`設定・既存research再取得機構等)を確認。既存機構で不可ならケースCとしてSTOP。
4. **既存wav** `er014_output/user_test_news_2ep_01/space_weapons/a2/narration/full_story_part1.wav`(または当該attemptのwav、review_lock_stateの`wav_path`と一致するもの)に対し、**正式cascade関数**(`er006_secondary_asr_01.evaluate_attempt_with_cascade_detail`等、Productionで使われている入口)を`ledger_phrases`に`Meink`を含めて実行。evidenceを`er014_output/user_test_news_2ep_01/space_weapons/a2/audit/correction_01_secondary_asr_phrase_list.json`に保存(provider/phrase list/phrase_list_used/transcripts/classification/verdict/timestamps/API call数)。想定API: Azure STT 1〜2回+必要ならPrimary ASR(既存関数が内包する場合のみ)。TTSは呼ばない。
5. 結果分岐A/B/Cは上記どおり。Aの場合、Human Review Lockの解除は**正式関数**でのみ(`record_human_approval`によるHUMAN_APPROVEDは使用禁止。再検証VALIDATEDを反映する正式経路が存在しない場合はケースC相当としてSTOP)。解除後は前回driverの既存assembly/gate段(`run_pipeline.py`の該当段、再TTSしないresume)でA2 Assembly→Audio Validation Gate。
6. Git: 明示add(evidence json/更新されたreview_lock_state・gate summary/assembly成果物のmp3・timeline[wav除外]/delegation_log/RESULT_PACKET/ACTIVE_TASK)。メッセージ`USER-TEST-NEWS-2EP-COMPLETION-01-CORRECTION-01: Phrase List付きSecondary ASR是正確認(TTS再生成なし)`、trailer `Task-ID: USER-TEST-NEWS-2EP-COMPLETION-01-CORRECTION-01`。push。Ledger.jsonに変更が生じた場合はその差分(`git diff --stat`)を報告(commit対象に含めてよい)。

## 報告(`docs/pm/RESULT_PACKET_NEWS_2EP_CORRECTION.md`、簡潔に)

0. T-0結果
1. CURRENT_SPEC上の正式仕様(行番号)
2. 関連Productionコード・関数(ファイル:行)と実行順序
3. 今回`phrase_list_used=false`になった直接原因
4. `Meink`のPronunciation Ledger状態(Secondary ASR実行時点/現在、登録時刻の根拠)
5. 是正再検証のruntime evidence(Phrase List/`phrase_list_used`/Azure transcript/classification・verdict/evidence path)
6. A2 Assembly/Audio Gate結果(解決時のみ、duration含む)
7. API追加コスト(cost logger実測+call数)
8. Git変更有無(SHA、Ledger差分有無)
9. 現在Status(`CORRECTION_VERIFIED`/`USER_DECISION_REQUIRED`(ケースB)/配線不備候補STOP(ケースC))
10. 未決事項+B1 Fact Checker REVIEW_REQUIRED定義の再確認結果(行番号)+Dangling Reference Check結果
11. 無変更証跡(`git status --porcelain CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md er006_*.py er003_*.py er011_*.py`が空)/事前指定外Read(理由付き)

ユーザー向け表記は「B1」に統一。

## 管理ID

USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-SPEC-AUDIT(OPEN-154 B1 Preview長さ仕様/OPEN-155 User Decision→正式仕様反映漏れ、read-only調査+登録案)
並行タスク衝突確認: 並行して Discovery、Family C、Trend命名整理が走る。本タスクは`docs/pm/spec_traceability_audit_03.md`(新規)と`docs/pm/RESULT_PACKET_FU03_SPEC_AUDIT.md`(新規)のみを書く。SSOT・コード・Git・ACTIVE_TASK・RESULT_PACKET.mdを触らない。API不使用(費用¥0)。

## 性質/到達上限Status/禁止事項

### OPEN-154(B1 Preview長さ仕様、Status USER_DECISION_REQUIRED、優先度MEDIUM)— 登録案作成
- 事実関係整理(read-only): 過去にユーザーが「長すぎるPreviewを短くする」よう指示し、Trialで 旧67語/4文→Trial 38語/2文→Production wiring runtime evidence 46語/2文 まで短縮された。一方、正式Production仕様は最終的に「2〜3文程度の短い導入」というsoft guidanceのみで、具体的word-count目安が残っていない。結果、Voices 2V v2で約65語・3文のPreviewが生成され、文数条件上は仕様内だが「短いPreview」意図から乖離。
- 確認事項: (1) 該当Trial/Decision/REPORTの管理IDと日付、67/38/46語の実績記録の所在(ファイル・行)。(2) 現Production Prompt(B1 Preview生成の`role_instruction`/prompt: `er003_v1_iran01_a2_generate.py`・B1 scaffold・`er012`のPreview生成)の実際の長さ指示文言(「2〜3文」のみか)を引用。(3) CURRENT_SPECのPreview仕様行の引用。(4) Voices 2V v2 Previewの実測語数・文数(`er014_output/four_type_observation_01/voices/audio/b1_2v_v2/`のsupport/comment JSONまたは`comment_fact_safety_evidence.json`から)。(5) 今回のVoices v2 Previewは**ユーザーが個別例外として特別承認**(約65語をそのまま使用、将来の前例にしない)—この記録文案。
- 禁止: 40/45/50語等を正式上限として提案文に「決定」として書かない(候補として並記は可)/Prompt変更/Validator追加/Voices v2 Preview再生成。

### OPEN-155(User Decision→Formal Spec反映漏れ、Status USER_DECISION_REQUIRED[Open Item管理自体はユーザー承認済み]、優先度HIGH、種類 PM Governance/Specification lifecycle/Production wiring traceability)— 登録案+限定監査
- 内容: ユーザーが仕様変更・恒久方針を指示/承認したのに、Trial Prompt/DEV script/局所実装/REPORTには残る一方、CURRENT_SPEC/Production初回path/retry・fallback/DECISION_LOG/Open Item closeoutへ正式反映されず「決めたはずの仕様が存在しない」状態になる再発リスク。B1 Previewが具体例。
- **限定監査(read-only、全Repo監査はしない)**: 対象=(a) Preview length、(b) Family C(Trial-09/v2の決定: Comment構成、Voice構成、AI固有名・語数clarification等がSSOTのどこにあるか)、(c) Voices 2V/3V(一人称仕様のPrompt欠落[今回修正済み]、Comment Contract接続、Key Phrase音声未生成等)、(d) Discovery S2(Point-only regeneration除外、STAGE1_MAX_REGENERATIONS、length記録未配線)、(e) Audio/TTS関連(読み整形・Human Review Lock運用・mp3配信・Gemini version方針)。各項目について「ユーザー承認/指示 → Trial・実装 → CURRENT_SPEC → Production path → DECISION_LOG → Open Item closeout」のどこまで到達しているかを表にし、途切れ箇所を明記(根拠: ファイル・行/管理ID)。**判断保留の項目は「未確認」と書き、推測で「反映済み」と書かない**。
- 再発防止案(実装しない、候補整理のみ): User Decision受領時の「Decision ID/Status/SSOT反映先」必須化/APPROVED_FOR_PRODUCTION未配線一覧の自動・半自動チェック/Closeout時の「ユーザー承認事項→CURRENT_SPEC存在確認」必須化/Trial REPORTに「正式仕様反映済/未反映」必須記載/Dangling Reference Checkの逆方向版(Approved Decision Missing from SSOT Check)。各案について、既存PM_GOVERNANCEのどの節に接続しうるか・新しい強制Gateに当たるか(当たる場合は「案の提示のみ、STOP対象」と明記)を整理。
- 禁止: PM_GOVERNANCEへの新Gate追加/SSOT編集/コード変更。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
---

## ユーザー指示(原文・要点)

> OPEN-154: B1 Preview長さ仕様(67語/4文→38語/2文→46語/2文の実績、正式仕様は「2〜3文程度」のみ、Voices 2V v2は約65語・3文)。Status USER_DECISION_REQUIRED、MEDIUM。やってよい: Open Item登録/事実関係整理/実績記録/現Promptが「2〜3文」のみであることの記録。やってはいけない: 勝手に上限決定/Prompt変更/Validator追加/Voices v2 Preview再生成。今回のVoices v2はユーザー個別例外として特別承認、将来の前例にしない。
> OPEN-155: User Decision→Formal Spec反映漏れ。HIGH。調査は最近の重要仕様に限定(Preview length/Family C/Voices 2V-3V/Discovery S2/Audio-TTS)。再発防止案を候補整理(実装しない)。PM_GOVERNANCE自体の新しい強制Gateを追加する場合は案を提示してSTOP。

## 事前指定Read一覧

1. `CURRENT_SPEC.md`: Grep `Preview` → Preview仕様の該当行のみ(A2/B1/B-Family)。Grep `Family C|Trial-09|Comment 4|Comment構成` → 該当行(存在しなければ「なし」)。Grep `一人称|Comment Contract|Key Phrase音声|2V` → Voices該当行。Grep `Point-only|STAGE1_MAX_REGENERATIONS|length_report` → Discovery S2該当行。Grep `読み整形|Human Review|mp3|Gemini 3.1|2.5 Flash` → Audio/TTS該当行。
2. `DECISION_LOG.md`: Grep `Preview.*(語|words|短)|短縮.*Preview` → Preview短縮のDecision行。Grep `PM-CLOSEOUT-CONSOLIDATION-13[1-4]|Trial-09|Comment 4|一人称|Human Review Lock|Gemini` → 直近Decision行のみ。
3. `OPEN_ITEMS.md`: Grep `^\| OPEN-(120|135|147|148|151|152|153) \|` → 該当行(長い場合は先頭300字+末尾300字)。
4. Preview実績: Grep `38語|38 words|46語|46 words|67語|67 words` in `*_REPORT.md`・`DECISION_LOG.md`・`DECISION_LOG_HISTORY.md`・`OPEN_ITEMS_HISTORY.md` → 該当行。
5. Production Prompt: `er003_v1_iran01_a2_generate.py`: Grep `PREVIEW|preview|2〜3|two to three|sentences` → Preview role指示の該当行。`er003_v1_n3_01_scaffold_generate.py`・`er012_b_family_editorial_type_registry_01.py`・`er012_b_family_production_runner_01.py`: 同Grep。
6. Voices v2 Preview実測: `er014_output/four_type_observation_01/voices/audio/b1_2v_v2/comment_fact_safety_evidence.json`: Grep `preview` -A 3 → 本文のみ(語数・文数を自分で数える)。
7. `docs/pm/PM_GOVERNANCE.md`: Grep `^## |^### ` → 節構成のみ(再発防止案の接続先特定)。
8. `docs/pm/RESULT_PACKET_FIX02_FAMILYC.md`・`RESULT_PACKET_FIX02_VOICES.md`: Grep `SSOT|CURRENT_SPEC|追記案` → SSOT反映提案の所在のみ。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 出力: `docs/pm/spec_traceability_audit_03.md`(1. OPEN-154事実関係+登録行案[既存6列表形式、Status USER_DECISION_REQUIRED、優先度MEDIUM]+Voices v2個別例外の記録文案、2. OPEN-155登録行案[HIGH]+限定監査表+途切れ箇所一覧+再発防止案(接続先・Gate該当性)、3. DECISION_LOG追記案)。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-SPEC-AUDIT.md --json-out docs\pm\delegation_log\USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-SPEC-AUDIT_check.json`
(他コマンドなし。Grep/Readのみ。)

## SSOT追記文

本タスクではSSOTを編集しない。登録行案・追記案は`spec_traceability_audit_03.md`とRESULT_PACKETに記載(統合タスクが反映)。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作を行わない。RESULT_PACKETに「commit対象候補(監査文書・delegation_log)」を列挙。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_FU03_SPEC_AUDIT.md`に: 1) OPEN-154: 事実関係(管理ID・日付・語数実績の所在・現Prompt文言引用・CURRENT_SPEC引用・Voices v2実測)、登録行案、個別例外記録文案、2) OPEN-155: 登録行案、限定監査表(5領域×到達段階)、途切れ箇所一覧(根拠付き)、未確認項目、再発防止案5件(接続先・新Gate該当性・STOP要否)、3) DECISION_LOG追記案、4) commit対象候補、5) T-0・事前指定外Read・STOP有無(新Gate提案があれば「案提示のみ」と明記)。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥0)
- [x] 並行タスク衝突回避あり(調査文書のみ・Git操作なし)

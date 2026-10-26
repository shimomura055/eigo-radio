## 管理ID

CHUNK-TTS-PRODUCTION-AUDIT-XYZ-01 委任_01(案件B。新規案件、ユーザーGoあり=下記「ユーザー指示(原文)」)。並行Agent: (1)KP-GATE-EXCLUSION-RESCUE-DESIGN-01(所有=`docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-01/**`・`docs/pm/ACTIVE_TASK.md`・`RESULT_PACKET_KPRS1.md`) (2)FAMILY-Y-VOICE1-PAUSE-CAUSE-TRIAL-01(案件A、所有=`docs/research/FAMILY-Y-VOICE1-PAUSE-CAUSE-TRIAL-01/**`・`er121_output/family_y_voice_pause_trial_01/**`・`user_test/family_y_voice_pause_trial_01/**`、有料TTS実行中。`er121_family_y_*.py`を読取のみで使用)。**本委任は`docs/pm/ACTIVE_TASK.md`・SSOT本体を編集しない。** 本委任の所有=`docs/research/CHUNK-TTS-PRODUCTION-AUDIT-XYZ-01/**`、`docs/pm/delegation_log/2026-10-26_CHUNK-TTS-PRODUCTION-AUDIT-XYZ-01_*`、`docs/pm/RESULT_PACKET_CHK1.md`、および是正が許可条件を満たす場合のみchunk関連Production code+test(`er117_chunk_tts_production_01.py`、X/Z/Yのchunk呼出箇所、対応test)。`er121_family_y_*.py`を編集する場合は案件Aが生成関数をimport中のため、**生成関数のシグネチャ・挙動を変えない**こと。

## 性質/到達上限Status/禁止事項

- 性質: Production監査(既存ログ・artifact・コード・SSOT照合、API 0)。Family X/Z/Y×Standard/Advancedで「段落境界Chunk分割+0.2秒ポーズ」のユーザー承認内容と正式Production実装・実音声の一致を確認。不一致が「既存の明示承認と完全に一致させるだけの不具合修正」と確認できる場合に限り自律是正(コード+test、有料run 0)。
- 到達上限Status: 監査=AUDITED(一致)/MISMATCH_FIXED_PENDING_EVIDENCE(是正済み・runtime evidence未)/判断候補(Fableが`USER_DECISION_REQUIRED`化)。**PRODUCTION_WIRED判定はFable。runtime evidence無しでPRODUCTION_WIREDと書かない。**
- 禁止: 有料API 0(有料run起動禁止。test/検証は`py`+`netblock_harness_01/sitecustomize.py`遮断下)/新しい分割規則(例: 文境界分割、語数閾値変更、Std専用規則)の追加禁止=ユーザー判断事項として報告/承認記録に曖昧さ・矛盾がある場合は是正せず判断候補として報告/既存公開音声・manifestの変更禁止/Git禁止操作: `git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・`reset --hard`・`checkout -f`・`git checkout -- <file>`。
- 是正の許可条件(すべて満たす場合のみ実装): (a)ユーザー承認原文(delegation_log/DECISION_LOGのユーザー原文引用)にStandard/Advanced双方を対象とする記述、または一方を除外する記述が無いことが確認できる (b)Standard除外がユーザー承認なしに設計判断・実装都合で入った経緯が特定できる (c)是正が「既存の承認済み分割規則(X: 段落境界・B0.2、Z: 約70語目安の段落境界・B_r1、Y: X方式)をStandardにも同一条件で適用する」だけで、新規則・閾値変更・Prompt変更を伴わない (d)X/Z/Yの他Family・他レベルの既存挙動を変えない(回帰test PASS)。1つでも欠ければ実装せず判断候補。
- 修正範囲の線引き(11-8): 範囲内=承認済み仕様(表の3行)と実装の乖離の是正とそのRegression・検証。範囲外=受理面・閾値・方式の新設/拡大(文境界分割・語数閾値変更・Std専用規則・0.2秒以外のポーズ)。
- Opus独立技術レビューGate(11-3): 非該当(新構造なし)。ただし是正がchunk判定の分岐構造を変える場合はFableが条件A/Bを再判定するため、実装前にRESULT_PACKET(中間)へ差分案を書きFableの指示を待たずに進めてよいのは「レベル条件の除外を外すだけ」の1〜数行変更に限る。
- 時間見込み: 全体2〜3時間(承認履歴照合40分、配線確認40分、実音声・ログ証拠40分、是正+test 0〜40分、報告20分)。並列化: 案件Aと並列。本委任内はFamily X→Z→Yの順で直列(同一関数群の読解を共有)。
- 費用/日次: 当日(JST 2026-10-26)既使用JPY約123(出典: docs/pm/ACTIVE_TASK.md固定ヘッダ)+案件A進行中(Cap 150)/本委任見積JPY0/改善見込み高/承認区分: C(JPY0、承認済みScope内)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし)
T-3: 本委任は費用上限[Cap]を伴わない(JPY0)。有料API呼出が必要と判明した場合は実行せず「必要最小限の検証方法・見積」を報告する(ユーザー原文「実際の発火証拠が不足する場合は、確認済みと誤認せず、必要な最小限の検証方法を示すこと」)。

委任文保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 631 --out docs\pm\delegation_log\2026-10-26_CHUNK-TTS-PRODUCTION-AUDIT-XYZ-01_DELEGATION_01.md`(`--index -1`不可。先頭が「## 管理ID」+「CHUNK-TTS-PRODUCTION-AUDIT-XYZ-01 委任_01」でなければ629〜642を順に試し、一致indexを記録)→`py docs/pm/tools/check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-26_CHUNK-TTS-PRODUCTION-AUDIT-XYZ-01_DELEGATION_01.md --json-out docs\pm\delegation_log\2026-10-26_CHUNK-TTS-PRODUCTION-AUDIT-XYZ-01_DELEGATION_01.md_check.json`。
ユーザー原文: 案件A/B共通の全文は案件A Agentが`docs/pm/delegation_log/2026-10-26_FAMILY-Y-VOICE1-PAUSE-CAUSE-TRIAL-01_USER.md`へ保存する。本委任は下記「ユーザー指示(原文)」節(案件Bに関係する§1・§3・§4・§5・§6案件B・§7案件Bの逐語)を一字も変えず`docs\pm\delegation_log\2026-10-26_CHUNK-TTS-PRODUCTION-AUDIT-XYZ-01_USER.md`へ保存する(先頭に`<!-- ユーザー指示原文(2026-10-26)のうち案件B関連節の逐語抜粋。全文は 2026-10-26_FAMILY-Y-VOICE1-PAUSE-CAUSE-TRIAL-01_USER.md -->`の1行可)。

## ユーザー指示(原文)

# Family Y Voiceポーズ原因切り分けTrial ＋ Family X/Z/Y Chunk TTS Production監査

## 1. 目的・実施方針

以下の2案件を並列実施してください。

**案件A：Family Y Voice 1のポーズ過多の原因切り分け**

Voice 1（Algieba）の長いポーズが、Voice固有の特性、本文、生成時のばらつき、TTS設定のどこから生じているかを特定する。

**案件B：Family X/Z/YのChunk分割仕様・Production実動作の監査**

ユーザー承認内容と、Standard／Advancedそれぞれの正式Production実装・実音声が一致しているかを確認する。

両案件とも、品質を守りながら最速で完了すること。独立作業は並列化し、不必要な待機・日付分割は行わない。

---

## 3. 案件B｜Family X/Z/Y Chunk分割仕様・Production監査

### ユーザーが明示した承認意図

| Family | 分割方式 | 追加ポーズ | 対象 |
|---|---|---|---|
| X | 段落境界分割（Trial B0.2） | 0.2秒 | Standard／Advanced |
| Z | 約70語を目安に段落境界分割（B_r1） | 0.2秒 | Standard／Advanced |
| Y | X方式を導入 | 0.2秒 | Standard／Advanced |

**ユーザーはStandard／Advancedの一方を対象外にする指示をした認識がありません。**

この表をユーザーの明示意図として扱い、当初承認記録との不一致を調査してください。

### ① 承認履歴の確認

CURRENT_SPEC、DECISION_LOG、ユーザー承認原文、過去TrialおよびProduction Wiring報告を照合する。

- X/Zで各方式を正式採用した記録
- Standard／Advancedの適用範囲
- Standardを対象外にする承認が存在するか
- YへのX方式展開時、適用範囲がどう解釈されたか
- 当初仕様と実装仕様に食い違いが生じた原因

ユーザー承認のないレベル除外を、実装上の都合や過去の設計判断だけで正当化しないこと。

### ② Production配線確認

Family X/Z/Yそれぞれ、Standard／Advancedについて次を確認する。

- 正式初回Production経路
- TTS Chunk分割条件
- 分割位置の決定方法
- 0.2秒ポーズの挿入・組立方法
- retry／fallback／regeneration／resume
- Validator・回帰テスト
- DEV／Trial専用経路との差異

「関数が存在する」「設定がON」という理由だけでPRODUCTION_WIREDと判定しない。

### ③ 実際のProduction音声を確認

既存の正式記事・生成ログ・音声artifactを再利用し、各Family・各レベルについて、次を示すこと。

- 本文の語数・段落構成
- 分割条件に該当するか
- 実際の分割回数
- 具体的な分割位置
- 追加0.2秒ポーズの位置・回数
- 実際のTTS call数
- 分割が発動しなかった場合、その理由

対象となる分割箇所が存在しない記事では「正常な不発火」と「配線漏れ」を区別する。

実際の発火証拠が不足する場合は、確認済みと誤認せず、必要な最小限の検証方法を示すこと。

### ④ Family YのStandard対象外問題

特に優先して確認すること。

Claude前回報告では、Family YのStandardは「X方式どおり対象外」とされていた。

しかしユーザーはStandard／Advanced双方への導入を意図している。

- なぜStandardが除外されているのか
- X自身もStandard対象外なのか
- Yへの移植時だけ除外されたのか
- 承認履歴に根拠があるのか
- 不一致の場合、影響範囲と是正方法は何か

これらを明確にしてください。

---

## 4. 不一致への対応・承認境界

案件Bで承認済み仕様との不一致を発見した場合は、原因・影響・修正内容を整理する。

**既存の明示承認と完全に一致させるだけの不具合修正**であり、品質基準や新規仕様を変更しないことが確認できる場合は、既存の承認範囲・予算・STOP条件内で自律修正・検証してよい。

ただし、承認記録に曖昧さや矛盾があり、実質的な新仕様決定を要する場合はUSER_DECISION_REQUIREDとして報告し、無断変更しないこと。

正式なPRODUCTION_WIRED判定には、正式経路・後続経路・runtime evidence・テスト・SSOT/Git・ユーザー承認内容との一致を必要とする。

新しい分割規則を独断で採用しないこと。

---

## 5. QCD・予算管理

- 品質 ＞ 完成速度 ＞ 量産単価
- 量産単価の目標：70円／記事セット
- 開発費：既存の承認済み予算内、原則1,000円／日（JST）
- 案件AのTrialは既存音声を最大限再利用し、比較に必要な生成だけ実施
- 案件Bは既存ログ・artifact・コードの調査を優先し、原則API費用0円
- 独立作業は並列実施
- 成果の見込めない同一条件の反復を行わない
- 追加費用が既存承認枠を超える場合や重大な品質・安全問題が発生した場合はSTOP

## 6. Fable独立評価

Fableは以下を独立確認すること。

案件B：
- 承認原文と実装の照合に漏れがないか
- Standard／Advancedを各Familyで個別検証したか
- 正式初回経路とretry等の後続経路を確認したか
- runtime evidenceは十分か
- Production WiringやSSOTの未完了を見落としていないか

## 7. 最終報告

### 案件B

Family×レベル別に、以下の形式で報告すること。

| Family | レベル | 承認仕様 | 実装 | 実際の発火 | Status |
|---|---|---|---|---|---|
| X | Standard | | | | |
| X | Advanced | | | | |
| Z | Standard | | | | |
| Z | Advanced | | | | |
| Y | Standard | | | | |
| Y | Advanced | | | | |

不一致については、原因、修正・検証結果、残るOpen Itemを明記すること。

**報告の最重要点は、案件Aでは原因の切り分けが成立したか、案件Bではユーザー承認どおりに正式Productionが動いているか、の2点です。**

既存仕様で解決可能な問題は自律的に解決し、新たな仕様判断が必要な事項だけをユーザーへ提示してください。

## KPI provenance欄

発火実績=reuse(既存Production run audit/ログ/音声)。是正後の挙動=offline test(synthetic)。production_formal_pathのfresh evidenceは本委任では取得しない(有料run 0)。E2E自己確認=No。

## Opus台帳更新

該当なし(関連: Chunk TTS Production配線時のOpus指摘があれば`docs/pm/OPUS_FINDINGS_LEDGER.md` Grep `chunk|Chunk`で確認し、Std除外がOpus指摘由来か否かをSPEC_CHECKに記す)。

## Fableからの前提・既知事実(前回報告の内容。鵜呑みにせず再検証すること)

- X: `er117_chunk_tts_production_01.py:90-93`付近「段落2未満は分割しない」。前回報告では「Advanced(b1b)のみ対象、Standard(a2)は対象外」と記した。この**Std対象外の根拠(ユーザー承認原文があるか/設計判断か)が本監査の核心**。
- Y: Y本文はVoice 1〜3が各1段落(`er121_family_y_text_core_01.py:175,1266`付近の1段落契約)→X方式(段落境界)では分割不発火。DECISION_LOG:22449付近/OT-42に10/25記録。`docs/research/FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01/CHUNK_WIRING_CHECK_01.md`に前回の配線確認あり(全文Read必須、前提として扱い再検証)。CURRENT_SPECのChunk TTS節にY不発火追記あり。
- Z: `er063_family_z_audio_01.py`(`run_assembly`/`build_entry`)、B_r1=約70語目安の段落境界。正式run例=`er026_output/family_z_production_e2e_01/the_monkeys_paw/run_sf_prod_01`、`er026_output/family_z_production_e2e_01/melos/run_e2e_06`。
- X正式run例=`er019_output/family_x_audio_production_wiring_01/<slug>__<run>/{a2,b1b}/audit/chunk_tts_decision.json`、`chunk_plan_b1b.json`(ファイル名に`b1b`が付いていること自体がレベル限定の痕跡。a2側の対応物の有無を確認)。
- 「X方式」「B0.2」「B_r1」「0.2秒」「段落境界」「chunk」のユーザー承認原文はdelegation_logの`*_USER*.md`(2026-10-1x〜10-2x)にある可能性が高い。Grepで全件特定し、Standard/Advancedへの言及を逐語引用する。

## 事前指定Read一覧

1. `docs/research/FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01/CHUNK_WIRING_CHECK_01.md` 全文。
2. `er117_chunk_tts_production_01.py`: Grep `def |level|a2|b1b|paragraph|段落|0\.2|pause|gap|silence|min_par|threshold`→該当範囲(判定関数と定数は全体)。
3. X: `er019_family_x_audio_production_runner_01.py` Grep `chunk|er117`→呼出箇所±20行。
4. Z: `er063_family_z_audio_01.py`・`er026_*`runner Grep `chunk|er117|70|B_r1|paragraph`→呼出箇所±20行。
5. Y: `er121_family_y_audio_01.py`・`er121_family_y_runner_01.py` Grep `chunk|er117|chunk_tts_decision`→呼出箇所±20行(読取のみ)。
6. test: Glob `er117*_test_*.py`、Grep `chunk` in `er019*_test_*.py`/`er063*_test_*.py`/`er121*_test_*.py`→レベル条件を固定しているtestを特定(是正時に更新対象)。
7. SSOT: `CURRENT_SPEC.md` Grep `Chunk TTS|B0\.2|B_r1|段落境界|0\.2秒`→該当節±20行。`DECISION_LOG.md` Grep 同→該当行(22449付近を含む)。`OPEN_ITEMS.md` Grep `chunk|Chunk|OT-42|OPEN-527`。
8. ユーザー承認原文: Grep `B0\.2|B_r1|0\.2秒|段落境界|chunk|Chunk|X方式` in `docs/pm/delegation_log/*_USER*.md`→該当ファイルの該当段落(前後10行)。
9. 実run: 上記X 2run(最新の正式X記事2本。例: ai_island_temple__run_ai_01とEV R1相当)・Z 2run・Y run_01の`audit/chunk_tts_decision.json`、`chunk_plan*.json`、TTS call記録(`raw_usage_log.jsonl`/manifestのsegment数)、本文(語数・段落数を自分で数える。scriptで可)。
10. `docs/pm/PM_GOVERNANCE.md` Grep `11-8`→分類語彙。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 新規OPEN番号候補=`OPEN_ITEMS.md`最大+1(現時点OPEN-528。並行Agent 2件も候補を出すため「候補番号・Fable確定」と明記)。
- SSOT追記はしない(文案のみ)。是正を実装した場合でも`CURRENT_SPEC.md`は編集せず、文案をRESULT_PACKETへ。

## 実行コマンド全文

- 本文語数・段落数・分割計画の集計script(新規、read-only): `py docs\research\CHUNK-TTS-PRODUCTION-AUDIT-XYZ-01\tools\chunk_audit_inventory_01.py --out docs\research\CHUNK-TTS-PRODUCTION-AUDIT-XYZ-01\inventory_01.json --md docs\research\CHUNK-TTS-PRODUCTION-AUDIT-XYZ-01\RUNTIME_EVIDENCE_01.md`(対象run一覧はscript内定数に実pathで列挙。LLM/TTS clientをimportしない)。
- 是正を実装する場合の回帰(遮断下、無料): `$env:PYTHONPATH="netblock_harness_01"; py run_project_regression.py --pattern "er117*_test_*.py"`、同`"er019*_test_*.py"`、`"er063*_test_*.py"`、`"er121*_test_*.py"`(`run_project_regression.py`の実引数は`--help`で確認し実値で記録。既存失敗はHEADでも同じかを`git stash`なしで判定=変更前に1回、変更後に1回実行して差分比較)。
- 接続試行0の確認: 遮断harnessの出力/ログをRESULT_PACKETへ。
- Production不変確認(是正なしの場合): `git status --short -- er117_chunk_tts_production_01.py er019_family_x_audio_production_runner_01.py er063_family_z_audio_01.py er121_family_y_audio_01.py er121_family_y_runner_01.py`(新規差分なし)。
- secret grep: `git diff --cached | findstr /R /C:"sk-[A-Za-z0-9]" /C:"AIza[A-Za-z0-9_-]" /C:"BEGIN PRIVATE KEY"`(0件)。

## 成果物

`docs/research/CHUNK-TTS-PRODUCTION-AUDIT-XYZ-01/`: `APPROVAL_TRACE_01.md`(承認原文の逐語引用+出典行、Family×レベルの承認範囲判定、Std除外の出所[ユーザー承認/Opus指摘/Fable設計判断/実装都合]、食い違いの原因)、`WIRING_CHECK_01.md`(Family×レベル×経路[初回/retry/fallback/regeneration/resume]の分割条件・位置決定・0.2秒挿入・validator・test・DEV/Trial差異)、`RUNTIME_EVIDENCE_01.md`(ユーザー§3の7項目をFamily×レベル×runで表、正常な不発火/配線漏れの区別、不足evidenceと最小検証方法・見積)、`FIX_01.md`(是正した場合: 差分・test結果・影響範囲。しない場合: 許可条件のどれが欠けたか)、`tools/`。

## SSOT追記文

編集権なし。RESULT_PACKETへ文案: (1)`OPEN_ITEMS.md`新規行候補(本管理ID、Status、11-8分類)(2)是正した場合の`CURRENT_SPEC.md` Chunk TTS節の修正文案と`DECISION_LOG.md`エントリ文案(Fable判断後に転記)(3)OPEN-527(UDR-YFB-1 分割方式)との関係1行。

## Git(明示add対象・コミットメッセージ・trailer)

- SSOT編集権: なし。`docs/pm/ACTIVE_TASK.md`も編集しない。
- 明示add: `docs/research/CHUNK-TTS-PRODUCTION-AUDIT-XYZ-01/**`、`docs/pm/delegation_log/2026-10-26_CHUNK-TTS-PRODUCTION-AUDIT-XYZ-01_{USER,DELEGATION_01}.md`+`_check.json`、是正した場合のcode/testファイル(pathを個別に)。
- commit: `git commit --only <paths…> -m "CHUNK-TTS-PRODUCTION-AUDIT-XYZ-01 委任_01: X/Z/Y×Std/Adv Chunk分割+0.2秒ポーズの承認・配線・実発火監査(API 0<、是正あり/なし>)"`→`git push origin HEAD:main`(non-fast-forwardは`git fetch origin`→`git merge --no-edit origin/main`→再push。競合は両方残してSTOP)。是正ありの場合は監査commitと是正commitを分ける。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_CHK1.md`: (0)T-0結果 (1)結論1段落(ユーザー承認どおりに正式Productionが動いているか、Family×レベルで一致/不一致) (2)ユーザー§7の6行表(承認仕様/実装/実際の発火/Status。各セルに出典ファイル:行) (3)§①承認履歴の照合結果(逐語引用付き。Std除外の承認有無を明言) (4)§②配線確認(経路別) (5)§③runtime evidence表+不足分の最小検証方法と見積(出典ある単価のみ) (6)§④ YのStandard対象外問題の回答(5問に番号対応) (7)不一致の分類: 範囲内是正(実施済み/未実施と理由)・判断候補(承認の曖昧さ・新規則が必要なもの) (8)是正した場合のtest結果・接続試行0・影響範囲、PRODUCTION_WIRED判定に不足するもの(runtime evidence等) (9)SSOT文案 (10)API 0・費用0の確認 (11)commit/push・raw URL (12)一覧外Readと理由 (13)Fable向け懸念。最終行に10行以内の要約。
# GATE_MECHANISM_MAP_01: G1〜G4の既存機構対応表(未承認機能の既定ON防止、Opus監査7項目の反映方式)
管理ID: PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 / Day2 Phase A 委任_B / 2026-10-15
性質: read-only調査+設計文書。規則・設定・Agent定義・SSOT・Production・Prompt・Gate・flag無変更、JPY0。Status上限: ROLE_GATE_DRAFT(Fable受入・Opus条件Aレビュー待ち)。**以下の是正案はすべて提案で未適用**。新規Hook/Validator/台帳/scriptの作成は行っていない。
表記: [確認]=一次ファイルで確認、[推定]=推論、[未確認]=確認できず。

## §0 前提
1. G1〜G4の定義(ユーザー2026-10-15 Day2設計案v1): G1=変更前の仕様整合・影響範囲・未承認仕様隔離 / G2=Trial終了時のFable独立受入・Status分類 / G3=Production有効化前のユーザー承認と実装差分照合 / G4=Production完成時の初回・retry・fallback・runtime・Regression・SSOT・Git確認。「新しい4種類のシステムを作ることではない」。
2. 強制の種類: **RT**=違反時に処理が止まる/拒否される、**WARN**=警告のみ(非ブロッキング)、**DOC**=文書の規定のみ(人が守る)、**NONE**=対応する機構・規定が無い。
3. 既存機構の正本棚卸: `DAY1_C_MECHANISMS_01.md`(STOP 8通り、Git hook/Claude hook/CI、`check_delegation_prompt.py`、Regression手動、費用ガードのコピー群)。本書はそれを再掲せず、G1〜G4の要件に当てはめる。
4. 文書側の主要所在(PM_GOVERNANCE): 2-1(既存対策Reconciliation)、Gate 1〜7(L132-246)、11(Gatekeeper)、11-3(Opus条件A〜D)、11-5(Opus台帳)、14、21(A/B/C分類)、22(ユーザー指示優先)、24(KPI provenance)、26(STOP)。

## §1 G1〜G4対応表
凡例: 充足 ○=実効 / △=部分的・機能不全あり / ×=実効しなかった実績または機構なし。

### G1: 変更前の仕様整合・影響範囲・未承認仕様隔離
| # | 要件 | 担う機構(文書/コード) | 種類 | 充足 | 機能不全・重複・矛盾 | 最小是正 | 必要test・証拠 |
|---|---|---|---|---|---|---|---|
| 1a | 承認済み仕様との整合確認 | PM_GOVERNANCE 2-1、21節(A/B/C分類、入口5つ)、Gate 6 | DOC | △ | 21節の入口は『新仕様提案前・新Trial起票前・UDR提示前・Production修正方針決定前・新Open Item前』のみ。**新しい検査ルール/Prompt文言を既存承認規則と併用する場面が入口に無い**(KGORA欠陥1: 「〜」規則と「辞書的に自然なら〜可」の矛盾、`REVIEW_AUDIT_01.md` 観点4: 提案前A/B/C記載なし) | 21節の入口6として「既存の承認済み規則・Prompt文言と併用される新しい検査ルール/文言の採用前」を1行追加。委任文の報告節に『既存仕様整合:A/B/C+照合ファイル:行』(`AGENT_ROLE_DELTA_01.md` §2-2)。F3のS5で承認原文と実装文言を並べて読む | KGORAのPrompt/規則文面ペアをS5手順で再読し、矛盾が検出できること(Day5リプレイ) |
| 1b | 影響範囲(上流・下流・他Family) | 2-2(コスト影響)、Gate 6補足(汎用化時のRegression提案)、11-3 観点10 | DOC | △ | 必須記載欄がなく、記載の有無を誰も確認しない。KGORAは失敗後の下流(TTS入力・assemble)を誰も評価せず(AUDIT §1②) | Opus packet(a)欄に「他Family・他経路への影響」(`AGENT_ROLE_DELTA_01.md` §3-1 ③)。Sonnet報告の3行に最終成果物の実例 | Sonnet報告の3行がGrepで存在すること(F3) |
| 1c | 未承認仕様の隔離 | flag既定OFFの慣行(例 `er003_key_words_gloss_alignment.py:45` `EIGO_KP_GLOSS_ALIGNMENT`既定"0")、`DefaultOffIsolation` test、Gate 3項目「DEV・Trial-onlyではない」、Gate 4 Dangling Reference(定義はCURRENT_SPEC) | RT(部分) | △ | **flagの規約が文書化されていない**(PM_GOVERNANCEの`flag`記述は無関係な1件のみ)。flag以外の入口(モード引数・定数・Prompt文面直接編集)は対象外(§2) | §2のP1〜P4(既存機構の運用) | `DefaultOffIsolation`型test(flag未設定でAPI 0・出力不変・副作用ファイル0)。実例: `er003_test_key_words_gloss_alignment.py` 78 passed |
| 1d | Opus条件A「実装前」 | PM_GOVERNANCE 11-3、DELEGATION_STANDARD_TEMPLATEの「Opus Gate判定」行(判定結果の記載)、`check_delegation_prompt.py`(Opusに言及しているのに台帳欄が無い場合の警告のみ) | DOC(+WARN) | × | **実装・配線・push後にOpus依頼**(push 20:47 → 依頼 20:58)。委任文の判定行は『該当/非該当』だけで、実施時期を問わない | テンプレ「Opus Gate判定」を『条件A該当/非該当、該当なら実装着手前の実施予定』にし、配線済みの場合は配線OFFにして実施(AUDIT A2) | 委任文でGrep可能な1行。Fable自己チェック欄の1項目 |
| 1e | retry/fallback/regeneration整合 | `sonnet-worker.md` L21-22、11-3 観点10・11 | DOC | △ | 観点11「Failure時に安全側」の『安全側』が品質欠陥を残す側を排除すると明記されていない(`REVIEW_AUDIT_01.md` 観点1)。失敗経路のtestが不整合出力をassertした(観点3) | 観点11へ注記1行(「安全側=最終成果物が目的要件を満たす側」)。『不整合出力をassertするtest禁止、検出して止めるtestは可』をGate 3項目へ | 失敗経路の実データ1例(D1)、assert内容のGrep(S2) |

### G2: Trial終了時のFable独立受入・Status分類
| # | 要件 | 担う機構 | 種類 | 充足 | 機能不全・重複・矛盾 | 最小是正 | 必要test・証拠 |
|---|---|---|---|---|---|---|---|
| 2a | Fable独立受入 | Gate 7(L243-246)、§1 L137-138、§11 Gatekeeper、sandwich-pm.md L36-40 | DOC | × | 5か所に分散して規定されるが、手段・リスク別の選び方・記録先・受領との区別が無い。L29が証跡読取を妨げる。KGORA: hand-back後37秒・tool_use 0 | `AGENT_ROLE_DELTA_01.md` §1 F3(S1〜S5+D1、リスク階層、受入記録を次委任文冒頭へ)。正本はGate 7に集約し他は参照のみ | 受入記録が次委任文に存在(delegation_logでGrep可)、記録内の証拠にファイル:行 |
| 2b | Status分類(VALIDATED/APPROVED/PRODUCTION_WIRED/UDR) | Gate 1、PM_BRIEF「正式Status語彙」、sandwich-pm.md手順5、UDR_REGISTER | DOC | ○ | KGORAでは『既定OFF=PRODUCTION_WIRED、工程は未採用』とFableが区別した(VALIDATION_OFF_01 §8)。UDR台帳のズレ(行59/集計55/見出し35)は別問題 | 変更不要。台帳ズレは別委任 | VALIDATION_OFF_01 §8の受入条件①〜⑥の表が実例 |
| 2c | Opus所見原文と台帳の一致 | 11-5、OPUS_FINDINGS_LEDGER | DOC | × | **11行中4行(OF-226/227/228/232)が原文とずれ**(AUDIT §5)。『Opus総評を採用』の一括記述で所見ごとの理由なし | 原文VERBATIM保存+採否理由1行+再レビュー要否(`AGENT_ROLE_DELTA_01.md` §3-2,3-3)。F3のS3で突合 | 台帳行の判定語・推奨・方向が原文と一致(Grep)。ずれが再発したら自動抽出(C1)を再検討 |
| 2d | KPI provenance・数値の経路 | PM_GOVERNANCE 24節、委任文テンプレ欄、`check_delegation_prompt.py`の警告 | WARN | △ | 非ブロッキング。`_check.json`は587件中PASS 284/FAIL 277(DAY1_C)でFAILが常態、信号として弱い | 変更なし(ブロッキング化はしない)。要点保存の委任文は検査対象外とする1行修正はDAY1_C提案どおり | F3 S4(報告数値と生証跡の照合) |
| 2e | 失敗終了時の最終成果物の確認 | **なし** | NONE | × | 受入Gate・12観点に項目なし。失敗系testが欠陥を固定(AUDIT) | Gate 3/7に1項目:『失敗終了パスの最終成果物が目的要件を満たす実例を実データ/実行ログで1件』 | D1(検証専用sonnet-worker委任)で失敗経路を1例再現し最終成果物を貼付 |

### G3: Production有効化前のユーザー承認と実装差分照合
| # | 要件 | 担う機構 | 種類 | 充足 | 機能不全・重複・矛盾 | 最小是正 | 必要test・証拠 |
|---|---|---|---|---|---|---|---|
| 3a | ユーザー正式承認 | Gate 2(承認原文全文をDECISION_LOGへ)、手順5、PM_BRIEF | DOC | △ | 無言承認(『異議なければ承認』扱い)を禁じる明文が常駐規則に無い(DAY1 T11)。承認の範囲(採用か、安全措置か)が要約引用になりやすい | Charter(Day3)に無言承認禁止+承認スコープの1文記録。DECISION_LOGへ承認原文+『承認範囲』1行 | DECISION_LOGに原文全文と範囲行(Grep) |
| 3b | 承認仕様と実装差分の照合 | Gate 3項目「approved specとProduction挙動の一致」 | NONE(手段なし) | × | **Fableは差分を見られない**(Bash無し)。Sonnetの自己申告のみ | F3: S5(承認原文と実装文言を並べて読む)+D1(`git diff <base>..HEAD --stat/-U0`の出力を検証専用委任で取得)。差分に含まれる『承認範囲外』のファイル・flag・Prompt文面を列挙させる | D1出力(ファイル一覧とflag・Prompt差分)と承認原文の突合記録 |
| 3c | Opus条件C(Production採用提案前) | 11-3、Gate 2 | DOC | △ | 条件C用レビューの再利用条件(5条件)の判定が記録されない(AUDIT §6)。KGORAでは修正後の再レビュー要否の記録なし | 台帳のFable採否セルに『再レビュー要否:要/不要+理由』を1行(運用)。高リスク変更(retry/fallback既定変更、Pass/Fail変更ルール)のみ差分+失敗経路の軽量確認 | 台帳セルの記載(Grep) |
| 3d | approved-but-unwired追跡 | ACTIVE_TASK固定ヘッダ「APPROVED未配線」、Gate 5、OPEN_ITEMS | DOC | △ | ACTIVE_TASKは`.gitignore`済みで履歴が残らない。台帳の手更新がズレ(UDR) | 追跡先はOPEN_ITEMS/DECISION_LOG(永続)を正とし、ACTIVE_TASKヘッダは写し。新台帳は作らない | OPEN_ITEMS行のStatusとACTIVE_TASKヘッダの一致(Grep) |
| 3e | 未承認機能の既定ON防止 | flag既定OFFの慣行+`DefaultOffIsolation` test、Gate 4(Dangling) | RT(部分) | △ | §2。flagだけでは防げない違反が多数 | §2のP1〜P5 | §2、§5 |

### G4: Production完成時の初回・retry・fallback・runtime・Regression・SSOT・Git確認
| # | 要件 | 担う機構 | 種類 | 充足 | 機能不全・重複・矛盾 | 最小是正 | 必要test・証拠 |
|---|---|---|---|---|---|---|---|
| 4a | 初回・retry・fallback整合 | Gate 3(Production正式初回経路/retry・fallback整合)、各erテスト | DOC | △ | どのテストを回すかは人が選ぶ | Gate 3項目の『失敗終了パス最終成果物』追加(2e)。Sonnet報告に回したテスト名と件数 | `run_project_regression.py`の対象patternとpass件数(S4) |
| 4b | runtime evidence | Gate 3、24節(provenance 6区分)、25-3 | WARN | △ | 委任文の警告のみ。fresh/synthetic/frozenの区別は報告者の記載次第 | F3 S4(evidence JSONの`status`・API呼出数・経路タグを生で読む) | `evidence_*.json`の値(例: `gloss_alignment_status="DISABLED"`、`kp_gloss_alignment`タグ0) |
| 4c | Regression | `run_project_regression.py`(pattern `er0*_test_*.py`、259ファイル)、CI(`ci-test.yml`はAUTO-001ブランチ/PR時のみ) | DOC(手動) | △ | mainへ直接push運用ではCI不発動。強制Regression(commit毎)は速度を落とすため新設しない(DAY1_C) | 現状維持。変更範囲に応じてSonnetが回す対象patternを委任文に列挙し、F3で結果ファイルを読む | `regression/reg*_*.txt`(例 er003* 1667件/1663 pass…既存集合と同一、新規failure 0) |
| 4d | SSOT整合 | 12節、REPORT_LEDGER、SSOT追記委任 | DOC | △ | UDR台帳の行数・集計・見出しがズレ(DAY1)。SSOT偽記載(台帳不一致)はflagと無関係 | SSOT記録委任の文案をFableが書き、F3でS3(原文と台帳)突合 | SSOT行と証跡の一致(Grep) |
| 4e | Git安全(secret scan・add範囲・push) | CLAUDE.md、10節、26-X(`tools/secret_scan_01.py --staged`)、`-A`禁止 | DOC | △ | Git hook無し(DAY1_C)。2026-10-12にAzure Key混入。pre-commit導入(DAY1 §9 #3)はユーザー判断待ち | DAY1 §8 #7どおりpre-commit 1本(ユーザー承認後)。それまでは委任文のGit節に`--staged`実行と`hits=0`記録を必須化 | `secret_scan_01.py --staged`の出力(`hits=0`) |
| 4f | STOP・予算の実行時安全装置 | Family Z: `er062` `check_stop_sentinel`/`install_api_stop_guard`/RUN_LOCK/RESTART_STORM、`tools/stop_all_family_z.py`。他: `tools/stop_scope_check_01.py`(3ファイルで使用)。費用: `assert_budget_ok`等のコピー(run単位) | RT | △ | Z以外はrunnerごとにSTOP確認が8通り。STOP_NOTICEの適用範囲定義が3種(`AGENT_ROLE_DELTA_01.md` §4 C4)。予算はタスク横断・日次の機構なし | C4の文言一本化(`stop_scope_check_01.py`を正本)。日次集計は読取script1本(DAY1 §8 #8、別委任) | `tools/stop_scope_check_01_test_01.py`、`er026_family_z_stop_sentinel_test_01.py` |

### 集計
| 区分 | 件数(全21要件) | 内訳 |
|---|---|---|
| **RT(実行時強制)** | **3** | 1c, 3e, 4f(いずれも「部分的」) |
| **WARN(警告のみ)** | **2** | 2d, 4b |
| **DOC(文書のみ)** | **14** | 1a, 1b, 1d, 1e / 2a, 2b, 2c / 3a, 3c, 3d / 4a, 4c, 4d, 4e |
| **NONE(機構・手段なし)** | **2** | 2e, 3b |
| 充足 ○ / △ / × | **1 / 15 / 5** | ○=2b。×=1d, 2a, 2c, 2e, 3b |
結論: 21要件中、実行時に違反が止まるのは3件(いずれも部分的)。5件は実効しなかった実績または手段なし。**ただし是正の大半は新機構でなく、既存規則への1行追加、Fableの受入手順(S1〜S5+D1)、委任文テンプレの項目追加で足りる**(§5)。

## §2 未承認機能が既定ONになる問題の防止(新しい大規模承認システムを作らない)
### 2-1 他事例の調査(Grep: `ENABLED\s*=\s*os\.environ|_ENABLED\s*=\s*"1"|ENABLED\s*=\s*True|default.*ON|既定ON`、`--glob "*.py"`)
| 事例 | 既定値 | 根拠(コメント上の主張) | 承認との突合 |
|---|---|---|---|
| `GLOSS_ALIGNMENT_ENABLED`(`er003_key_words_gloss_alignment.py:45`) | **旧: 既定ON(未承認のまま配線、3b64e5632)→ 2026-10-15に既定OFF化(c21cce27a/e80360add)** | Opus OF-235が『承認前配線: flag(既定ON)』を推奨し採用(AUDIT §5) | **未承認既定ONの確認済み事例(是正済み)** |
| `FEATURE_FLAG_SECONDARY_ASR_ENABLED`(`er006_secondary_asr_01.py:227`) | ON | 「ER-006-GATE-EVIDENCE-REVIEW-CASCADE-ON-MATH-ADOPT-01」 | 管理ID名は採用を示すが、SSOT突合は未実施[未確認] |
| `FEATURE_FLAG_JA_SCG_ENABLED`(`er007_ja_secondary_asr_01.py:88`) | ON | 「既定ON(PRODUCTION_WIRED)」 | 同上[未確認] |
| `FEATURE_FLAG_JA_ASR_VARIANT_LAYER_ENABLED`(`er011_ja_asr_variant_layer_01.py:52`) | ON | OPEN-145のProduction wiring | 同上[未確認] |
| `VOICE_FACT_SAFETY_GATE_MODE_DEFAULT`(`er012_b_family_editorial_type_registry_01.py:464`) | ON | 「Status=APPROVED_FOR_PRODUCTION…B-Family限定、2026-09-13」 | 同上[未確認] |
| target-sentence-matching(`er003_v1_n3_01_articles_generate.py:1208`ほか) | ON | 「正式判断2026-09-13…既定ON」 | 同上[未確認] |
| `er052_open233_self_recovery_flow_runner_01.py:447`以降の『既定ONの新スイッチ』7件(`STAGE4_ALLOWLIST`等) | ON | 「委任_11(Opus#14後のFable評価)」。同ファイルの別箇所に「Trial専用・Production未配線・`APPROVED_FOR_PRODUCTION`ではない」と書かれた構成(L463付近)があり、**どのスイッチがどの承認に基づくかが一目で分からない** | **突合不能[未確認]。要確認候補** |
結論: 未承認の既定ONが**確認できたのはKGORAの1件のみ**(是正済み)。他は『承認済み』の記述がコード側にあるが、SSOTとの機械的突合の仕組みが無く、本調査では未突合。**既定ONの総数(約12ファイル)を無差別に疑うのでなく、『Productionに到達する未承認機能』を判定する入口を作る方が効率的**。

### 2-2 既存機構での防止策(新制度なし)
| # | 防止策 | 使う既存機構 | 誰が実行 | 種類 |
|---|---|---|---|---|
| P1 | Production到達経路(共通到達点)に入る新規機能は**既定OFF(明示opt-in)**で書く。既定値の行をRESULT_PACKETに引用する | 委任文テンプレ報告節+既存の慣行(`GLOSS_ALIGNMENT_ENABLED`) | Fableが委任文に書く、Sonnetが従う | DOC(運用) |
| P2 | 未承認機能の**既定値をFableが自分でGrepで確認**(S1)。変更/新規の`ENABLED`/`FEATURE_FLAG`/`os.environ.get`行を、検証専用sonnet-worker委任で`git diff <base>..HEAD -U0 | rg "ENABLED|FEATURE_FLAG|os\.environ"`の出力として取得(D1) | Gate 3、F3 | Fable(Grep)+検証専用Sonnet | 運用(F3の一部) |
| P3 | `DefaultOffIsolation`型test:flag未設定でAPI 0・出力不変・副作用ファイル0。**flag以外の入口(モード引数、設定dict)も同じtestで検査**(KGORAではmode=correctedがflagを迂回していた→`flag_enabled()`へ一元化で是正) | 既存test形式(`er003_test_key_words_gloss_alignment.py`) | Sonnet | test(実行時ではないが再現可能) |
| P4 | 承認の記録:承認原文+**承認範囲1行**(採用か、安全措置か、対象Family/経路)をDECISION_LOGに残し、Gate 3のS5で承認範囲と実装を照合 | Gate 2、DECISION_LOG | Sonnet(記録)、Fable(S5) | DOC(運用) |
| P5 | (任意・後回し)runner summary/起動ログに**有効なfeature flag値の一覧**を出す。環境変数・起動script経由の暗黙ONを事後検出できる(VALIDATION_OFF_01 §8は『runner summaryに`gloss_alignment_mode`欄なし』を未記録事項とした) | 既存summary出力への項目追加 | Sonnet(コード変更=別委任・ユーザー承認後) | 機構変更(小、任意) |
**新しい承認システムは作らない**。上記は既存のGate 2/3/4、委任文テンプレ、`DefaultOffIsolation`型test、F3受入手順の使い方の明確化。

### 2-3 flag既定OFFだけでは防げないGate違反(列挙)
| # | 違反の型 | なぜflagで防げないか | 実例/根拠 | 防ぐ既存手段 |
|---|---|---|---|---|
| V1 | Trial専用mode・Python引数・設定値でのProduction混入 | flagを参照しない入口が別にある | KGORA: `mode=corrected`は`enabled=True`直書きでflagを迂回(`flag_enabled()`へ一元化して是正、VALIDATION_OFF_01 §7') | P3(全入口を同じtestで検査) |
| V2 | プロセス内のmodule global書換え(Trial scriptのmonkeypatch) | 同一プロセスでProduction経路が呼ばれれば影響 | `er006_retry_cascade_prod_01_eval.py:28`、`er011_open145…_run.py:52,113,161`等がモジュール定数を`True`に書換え(実害の有無は[未確認]) | Trial scriptは別プロセス・Production runnerからimportしない(運用)。P2のdiff確認 |
| V3 | 環境変数・`.env`・起動script・シェルによる暗黙ON | 値がコードの外にある | VALIDATION_OFF_01 §1: 起動scriptに設定なしを`rg`で確認(一時点のみ)。summaryに欄なし | P5、委任文のコマンド全文にenv指定の有無を明記 |
| V4 | flagの無い変更:Prompt文面・正規表現・閾値・辞書の直接編集(『既存仕様内のバグ修正』を装った仕様変更) | 切替機構が無い | 21節A/B/C分類が唯一の防御(DOC)。11-1は既存仕様内修正を自律実施とするため、**仕様変更かの判定を誰がするか**が空白 | 1a(21節入口6)、F3のS5。T-midで新規Prompt/検査ルールを必ず階層化 |
| V5 | flagが複数の命名(`*_ENABLED`/`FEATURE_FLAG_*`/設定dict/定数/モード引数)で、Grepで網羅できない | 規約がない | 2-1のGrep結果が命名ばらばら | P1(Production到達経路に入る機能は`os.environ.get("EIGO_...")`形式に統一…は新規規約となるため**採用は任意**。まずGrep `-U0` diff確認で十分) |
| V6 | 承認範囲の拡大解釈 | flag値は承認の範囲を表さない | 安全措置(案a)の承認を工程採用と混同/逆(AUDIT/VALIDATION_OFF_01 §8は区別を記録) | P4 |
| V7 | SSOT・台帳の偽記載(実装とのずれ) | 記録側の誤り | OF-226/227/228/232(4/11)、PRODUCTION_WIREDの根拠表 | F3のS3/S5、受入記録 |
| V8 | 欠陥を期待値に固定したtest | flag OFFならtestが走らず見えない/ONでテスト自体が欠陥を保証 | `test_failed_alignment_keeps_kp_flags_failed_not_human_review`(AUDIT/REVIEW_AUDIT 観点3) | S2、Gate 3の『不整合をassertするtest禁止』 |
| V9 | 共通到達点での一括ON | 約65のrunner/Trial scriptが同じ到達点を通る | `corrected`分岐の`enabled=True`直書き(上記V1) | 共通到達点のtestとP2 |
| V10 | STOP・予算の迂回(別名ラッパ、監督ループ) | 機能の有効化ではなく実行制御の問題 | 2026-10-12事故(§26-1) | 26節の実行時安全装置(Zのみ。他Familyは各runner) |
| V11 | 無言承認・要約引用による承認 | 人の判断の記録 | DAY1 T11、Gate 2の要約引用事例 | Charter、P4 |
| V12 | Opus/Fableの推奨が『承認前配線』を含む(Gate 2/3と衝突) | 設計の推奨そのもの | OF-235(Opus推奨→Fable採用) | 1a/1d(委任文に『承認前にProduction経路へ配線しない。必要なら既定OFF』を明記)、Opus packet(a)欄の目的・承認状況欄 |

## §3 Opus監査7項目の反映方式(既存機構の変更か運用改善か)
(`AUDIT_REPORT_01.md`の指摘を、ユーザー指示§4Dの7項目に当てはめる。レビュー回数や文書量を増やさない)
| # | 項目 | 現状(既存機構) | 区分 | 最小是正 | 証拠 |
|---|---|---|---|---|---|
| 1 | 変更目的と既存仕様の整合 | 21節A/B/C(入口5つ)、2-1。新規検査ルール/文言の入口なし | **運用徹底+規則文面1行**(21節の入口6)。機構変更なし | 委任文の『目的1文』欄、報告節の『既存仕様整合』3行、F3 S5 | 報告に照合ファイル:行、受入記録のS5行 |
| 2 | 不要になった機械NGルールの撤去確認 | なし(Gate 3に項目なし)。KGORAでは「～」条件が撤回された(608f5e866)が、`SLOT_TOKENS`等はlegacy用に残置(`er003_key_words_gloss_alignment.py:499`コメント『correctedで不使用(legacyでは残す)』) | **規則修正(軽微)**: Gate 3に『不要になった旧ルール・旧機械NG・旧testの撤去または残置理由』1項目 | Grepで識別子(例`SLOT_TOKENS`)の残存を列挙し、残す場合は理由を記録 | S1/S2のGrep結果(残存箇所と理由) |
| 3 | 異常終了時の最終成果物 | なし | **規則修正(軽微)**: Gate 3/7に1項目(実データ/実行ログ1例)+『不整合をassertするtest禁止』 | D1で失敗経路を再現し最終成果物を貼付 | 検証専用委任の出力 |
| 4 | Opus所見原文と台帳の一致 | 11-5(台帳運用)。原文保存の規定なし | **運用改善**(11-5の徹底) | VERBATIMを委任文に貼り保存。F3 S3で突合。C1スクリプトは見送り | 台帳行とVERBATIMのGrep一致 |
| 5 | 所見採否の根拠 | 台帳『Fable採否』列。理由の記載規定なし | **運用改善**(列追加なし。セルに理由1行) | 所見ごとに採否+理由。一括採用禁止 | 台帳セルの記載 |
| 6 | 高リスク修正後の必要な差分レビュー | 11-3の5条件(再レビュー)、重複禁止。要否判定の記録規定なし | **運用改善**(11-3の(2)(3)に適用例を1行例示のみ) | 再レビュー要否を毎回1行判定。実施は(i)retry/fallback既定変更(ii)Pass/Fail変更ルール導入の場合のみ、差分+失敗経路2〜3論点の軽量確認 | 台帳セルの『再レビュー要否』行 |
| 7 | Fable独立受入の実行証拠 | Gate 7(文書のみ)。記録先なし | **規則修正(Agent定義)**: sandwich-pm.md L29修正+手順4-2。受入記録は次委任文冒頭(運用) | 受入記録5行。T-highではD1必須。ユーザー報告に受入記録を要約 | delegation_logの受入記録、記録内のファイル:行 |
区分の集計: 機構変更(コード・script・hook)=**0件**(任意のP5と`check_delegation_prompt.py`警告は任意)。規則修正(文書)=3件(#2,#3,#7)+#1の1行。運用改善・徹底=3件(#4,#5,#6)。

## §4 機能不全・重複・矛盾の一覧
| # | 内容 | 該当 | 影響 | 是正案 |
|---|---|---|---|---|
| X1 | 受入規定が5か所に分散(Gate 7、§1、§11 Gatekeeper、sandwich-pm手順4、2-1)で実行主体の手段が無い | PM_GOVERNANCE L137-246,1757 / sandwich-pm L36-40 | 受入の形骸化(KGORA 37秒) | Gate 7に集約し他は参照(§5 #5) |
| X2 | 条件Aが文書のみで、実施時期を確認する欄が無い | 11-3、テンプレ | 実装・配線後にレビュー | 判定行を『実装前実施』形式に |
| X3 | `check_delegation_prompt.py`が非ブロッキングでFAIL 277(PASS 284と合わせ約49%がFAIL)が常態。形式のみで中身を見ない | DAY1_C | 信号が弱い。ただし本委任の委任文要点保存で実際に必須節欠落を検出した(「実行コマンド全文」節名の省略)ので、形式漏れ検出には有効 | ブロッキング化しない。要点保存は検査対象外にする1行修正(DAY1_C提案) |
| X4 | STOP_NOTICEの適用範囲が3定義、`stop_scope_check`は規則側に言及0件 | `AGENT_ROLE_DELTA_01.md` §4 C4 | agentがscope外のNOTICEで不要停止/逆に見逃し | 一本化 |
| X5 | `ACTIVE_TASK.md`/`RESULT_PACKET*.md`が`.gitignore`済みで、APPROVED未配線・受入の原本にならない | .gitignore L49-56 | 状態の再現性なし | 正とする保存先をOPEN_ITEMS/DECISION_LOG/delegation_logに固定 |
| X6 | UDR台帳のズレ(行59/集計55/見出し35) | DAY1_REPORT T7 | 判断済みの再質問 | 台帳是正(別委任)。docs_lintは任意 |
| X7 | haiku-workerの許可リスト不一致 | sandwich-pm L4 vs L12-21 | 実行不能な指示が残る | 削除推奨 |
| X8 | CIはPR/AUTO-001のみ。main直接push運用では不発動 | DAY1_C | Regressionは手動依存 | 現状維持(強制Regressionは新設しない) |
| X9 | flag命名・規約が無く網羅Grep不能 | §2 V5 | 既定値の検査漏れ | P2のdiff Grep(`-U0`)で足りる。規約化は任意 |
| X10 | 費用ガードが約38/26ファイルにコピー(run単位のみ)。タスク横断なし | DAY1_C | OPEN-315型の穴 | DAY1 §8 #8(読取script) |
| X11 | 重複: 1e(retry/fallback整合)と3b(差分照合)と4a(初回・retry・fallback整合)が同じ『Production挙動の一致』を別Gateで述べる | Gate 3 | 責任の曖昧さ | Gate 3の1項目に統合(『承認仕様との一致と失敗経路の最終成果物』) |
| X12 | Opusの推奨にGate 2/3と衝突するもの(承認前配線既定ON)が含まれても検出する仕組みが無い | OF-235 | 未承認機能のON | Opus packet(a)欄の『承認状況』+F3 S1 |

## §5 必要なtest・証拠(是正案ごと)
| 是正案 | 確認方法 | 時期 | 費用 |
|---|---|---|---|
| 規則・Agent定義の文面変更(AGENT_ROLE_DELTA §5 #1〜#9) | 変更後の文面を`rg`で存在確認。**Agent定義の変更は次回`claude --agent sandwich-pm`起動から有効**(DAY1 §8リスク)。変更前を保持し新旧比較 | Day3〜4(承認後) | 0 |
| F3受入手順(S1〜S5+D1) | **リプレイ試験**: KGORAの成果物(`er071_output/m2p0_n01_production_wiring_01/`)に新手順を適用し、(a)S2で不整合assertのtestが見つかる (b)S5で「～」規則と承認規則の矛盾が見つかる (c)S3でOF-226/227/228/232の不一致が見つかる (d)S1で旧commitの既定ONが見つかることを確認 | Day5〜6(Trial) | 0〜小(読取のみ) |
| D1(検証専用sonnet-worker委任) | 既存の1件で実施し、委任文が『実装・編集しない、コマンドと出力原文のみ』を守ること、出力に生ログが含まれることを確認 | Day5〜6 | 小(トークンのみ) |
| 未承認機能の既定OFF(P1〜P4) | `rg -n "ENABLED\s*=\s*os\.environ|FEATURE_FLAG" --glob "*.py"`の基準一覧を1回取得し、変更時のdiff Grepと比較。`DefaultOffIsolation`型test(flag未設定でAPI 0) | 常時 | 0 |
| Opus所見・台帳(§3 #4〜#6) | 次回Opusレビュー1件でVERBATIM保存→台帳転記→S3突合を実施し、不一致0を確認 | 次回Opus発火時 | 0 |
| STOP文言一本化(C4) | 新旧文言のGrep、`tools/stop_scope_check_01_test_01.py`のPASS | Day3〜4 | 0 |
| (任意)P5・`check_delegation_prompt.py`警告 | 小規模testで警告/summary出力を確認 | 採用時のみ | 0 |
共通: 新規API・TTS不要。これらはすべて読取・Grep・既存test実行で確認できる(JPY 0〜トークンのみ)。

## §6 未確認事項
1. `Agent(sonnet-worker, opus-consultant)`が許可リストとして働き、`haiku-worker`の起動が実際に拒否されるか(実機未検証)。
2. `claude --agent sandwich-pm`で新Agent定義(L29修正・手順4-2)が主スレッドに実際に効くか、Fableがtool_useを実際に行うかの遵守は**文面だけでは強制できない**(強制手段はなく、リプレイ試験と受入記録の存在確認で事後確認する)。Stop hookは`--agent`で効くか未確認(DAY1_C §3)。
3. 2-1表の「承認済み」記述(ER-006/ER-007/ER-011/ER-012/target-sentence-matching)のSSOT突合は未実施。er052の『既定ONの新スイッチ』7件の承認根拠は未突合。
4. V2(module global書換え)の実害有無、およびProduction runnerが同一プロセスでTrial scriptをimportする経路の有無。
5. Fableの各判断時の内部思考・読んだファイル(会話記録上redacted)。KGORAで『確認しなかった』と『確認したが記録しなかった』の区別は付かない。
6. D1の検証専用委任がSonnetの自己申告よりどの程度独立と言えるか(同一モデル系統)。最終的な独立性はG3のユーザー承認に依存する。
7. `docs/pm/delegation_log`の約1,560ファイルが今後も受入記録の保存先として十分に検索可能か(命名規則: 管理ID+日付。受入記録を探すGrepパターンは未設計)。

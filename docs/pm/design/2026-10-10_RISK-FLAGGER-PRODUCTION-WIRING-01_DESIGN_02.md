# RISK-FLAGGER-PRODUCTION-WIRING-01 設計書 DESIGN_02(設計v2: 新Writer配線+RF配線+旧Checker撤去の一括Production Wiring)

- 管理ID: RISK-FLAGGER-PRODUCTION-WIRING-01 委任_03(2026-10-10)。**DESIGN_01(1〜13節+14節Opusレビュー)は変更しない。本書はその上書きではなく追補・改訂版**。
- Status: **DESIGN_READY / USER_DECISION_REQUIRED(STOP候補あり、12節。最重要=1節「新Writer正式仕様が一意に特定できない」)**。読み取り・設計のみ。**Productionコード・CURRENT_SPEC・Promptは変更していない。課金API 0件。**
- 調査基準: git HEAD `635111bf`のワーキングツリー(行番号は同時点)。「確認済み」=今回Grep/Readで実在を確認、「未確認」=確認できていない。
- ユーザー方針更新(2026-10-10、正式決定)を前提: 段階案不採用/新Writer(Fact Lock)配線+RF配線+旧Fact Checker撤去を1つのProduction Wiringとして一括/Standard・Advanced両方にRF適用・旧Checker撤去(R2後JA Fact Check含む)/OPEN-233系Checkerは配線しない/技術QA維持/runnerにgit責務なし/RF非Blocking/splitter共通module/費用3ギャップ修正承認/git revert+tagで戻せる形/最終Evidence=L3(テーマ未指定ならSTOP)/Opus必須修正8点を全取り込み。
- 使用モデル(PM_GOVERNANCE 25節): 本書はLLM呼び出し0件。Phase 2で使うRF=Luna `gpt-6-luna`・Gemini `gemini-3.5-flash-lite`(ユーザー指定、DESIGN_01冒頭と同じ)。新Writerのモデルは**未決**(1節)。
- 委任文の「ユーザー16条件」の原文は本委任文に含まれていなかったため、12節は「ACTIVE_TASK固定STOP条件+委任_01のSTOP節+今回の委任文のSTOP候補指定」で照合した(Fableが16条件原文と突合すること)。

---

## 0. 結論サマリ(非エンジニア向け)

1. **「新Writer(Fact Lock)」として人間ユーザーが正式承認した仕様は、文書上は一意に特定できない(STOP)**。承認されているのは運用コンセプト「新Writer+Production Checkerなし+A3/A4+Human Review」(OPEN-244、`APPROVED_FOR_PRODUCTION`)だけで、どのWriter構成か・どのモデルか・Trial限定要素(M1/M3/B1/B3注記)をどこまで採るかは、承認記録に書かれていない。候補は4つ(1-2節)。さらに、新Writerが前提とする**B3注記(事実番号・中核数値の印付け)はTrialでは「Claude側Sonnet worker 2名+決定論統合」という方式で、Productionで自動化する仕様・精度測定が存在しない**(注記仕様v2自身が「注記の自動化は範囲外・精度未測定」と明記)。→ このままではPhase 2に進めない。
2. 配線設計自体は「Writerの中身(R0/R1/R2のモデル・プロンプト)をパラメータ化」すれば、どの候補でも同じ骨格で書ける(2節)。ただし**Production Prompt(Fact Lock R0ブロック等)の採用はPrompt変更**に当たり、承認はコンセプト単位でprompt逐語承認ではない(STOP)。
3. Standard/Advanced非対称棚卸は16行(委任文の列挙語が16個。「15項目」表記と1つ違い)。②=4件(既存承認仕様で説明可=2・撤去で消滅=1・新仕様判断=1[M1(a)の適用範囲、1節と連動])。新規Prompt/仕様の追加なしで解消できないものはM1(a)のみ。
4. 旧Checker撤去リスト=**28行**(DESIGN_01の22行+新規6行)。T-17/T-18は維持を明記。`OPEN243_M1`等の環境変数依存はFamily X経路から全て除去。
5. **L2(既存METAで代替)は技術的に同等と言えない**(9-3節)。L3(新規1本、Standard+Advanced)が必要。テーマ未指定のため、L3の課金開始の直前でSTOP。
6. Phase 2規模は新規コード約+1,700〜2,100行(注記moduleは見積不能部分あり)・テスト約+1,200行・削除約−500行(11節)。**Opus独立レビュー(条件A: 新しい処理フロー設計)が内容変更(一括化・新Writer配線追加)により再度必要**。

---

## 1. 新Writer正式仕様の一意性確認(最重要・STOP候補)

### 1-1. 照合した正本と結果(Grep実測)

| 正本 | 「新Writer」「Fact Lock」の記述 | 判定 |
|---|---|---|
| `CURRENT_SPEC.md`(2,571行) | `Fact Lock`/`FACTLOCK`のGrep=**0件**。Writer仕様は旧Writer(Luna R0→R1→R2、Fact Check込み)のまま | 新Writerは正式仕様書に**未記載** |
| `OPEN_ITEMS.md` OPEN-244(L746) | 「運用コンセプト『新Writer+Production Checkerなし+A3/A4 Risk Flagger+Human Review』は`APPROVED_FOR_PRODUCTION`だが未配線(closeしない)」。Writer構成・モデル・Trial要素の記述なし。OPEN-241(L743)は別commitでFact Lock配線と明記 | **コンセプトのみ承認**。構成は未定義 |
| `DECISION_LOG.md` L20472〜L20478(2026-10-10ユーザー決定) | 同コンセプト`APPROVED_FOR_PRODUCTION`。ユーザー所見「旧Writer+Checkerより、新Writer+Checkerなしの方が実質品質は高い」。R0後/翻訳後Hard STOP除去=APPROVED_FOR_PRODUCTION | 「新Writer」はFACTLOCK-ASTRA-E2E-TRIAL-01の新仕様腕を指している可能性が高いが、**決定文に腕・構成の明示なし**(推測) |
| `DECISION_LOG.md` FACTLOCK-ASTRA-E2E-TRIAL-01(L20341〜L20436) | ユーザー決定1〜9=E2E Trialの設計・規模・B3注記仕様v2固定(L20370)・M1(Adv)/M3 ON・M2 OFF・Astra Standard同期。**Fable最終判定(L20403〜)=総合「同等・混在」、事実安全の良化は示されず、費用約6倍(新約¥43.9対旧約¥7.1/記事)、VALIDATED/APPROVED_FOR_PRODUCTION未宣言。方向判断(a)〜(e)はユーザー回答待ち(USER_DECISION_REQUIRED)** | **Trialは未決着のまま** |
| `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md` §111(L5913) | 新腕=B3注記版+Fact Lock R0+gpt-6-astra R1/R2+B1回復+M1(Adv)/M3+Checker。限界: n=9、各腕n=1、Production採用提案前にOpus条件C必要 | 同上 |
| 同 §114(L5980) | R0モデル(Luna/Sol/Astra)差Trial。FIX01/02追補。Closeout=USER_DECISION_REQUIRED。優劣は確定せず | **R0モデルは未決** |
| `DECISION_LOG.md` L20237 | 6-luna配線は「Fact Lock Trial生成完了後」に段階実施、「Fact Lock配線は別commit」(L20250) | Fact Lock配線の正式仕様は6-luna配線時点でも未確定と記録 |
| `docs/pm/PM_BRIEF.md` | Fact Lock/Astraの記述0件 | - |

### 1-2. 「新Writer」の候補一覧(いずれも未承認の構成。勝手に選ばない)

| 候補 | 構成 | 実装の所在(Trial) | R0モデル | R1/R2モデル | 到達Status |
|---|---|---|---|---|---|
| **W-1(E2E新仕様腕)** | 注記版B3 →【Fact Lock R0ブロック(構造a: 同一LLM呼出内で【事実N】タグ付け、AN3第1文を数字規則に置換)】→ R1(Astra、developer無し、userに系列X逐語)→ R2(同)→後処理(タグ除去・R0復唱検出)→EN(M1(a)あり)。回復=B1(Checker起点)、Checker=M3付き | `er052_factlock_astra_e2e_runner_01.py`(`worker_new_r0` L643、`worker_new_astra` L700、`ARM_FLAGS` L58) | gpt-6-luna(`vfl01`既定=`routing.WRITER_MODEL`) | gpt-6-astra(reasoning high、Standard同期) | MEASURED。Fable最終判定=同等・混在。ユーザー所見(2026-10-10)「新Writer+Checkerなしの方が実質品質は高い」は文脈上この腕を指す可能性(推測) |
| **W-2(Fact Lock v1、全Luna)** | 注記版B3→Fact Lock R0→R1→R2(`previous_response_id`連鎖、`FACTLOCK_REVISION_BLOCK`をR1/R2指示へ追記)。全段gpt-6-luna | `er052_factlock_writer_trial_01_run.py`(`FACTLOCK_R0_BLOCK_HEAD` L53、`FACTLOCK_REVISION_BLOCK` L84、`apply_factlock_patches` L568) | gpt-6-luna | gpt-6-luna | MEASURED(§104)。v1: 軽微/記事 JA R2 0.21(baseline 0.55)等(DECISION_LOG L20274) |
| **W-3(Astra Revise Matrix)** | Fact Lock R0→Astra R1→R2→R3(系列A/B、developerなし/F2 developer文) | `er052_output/factlock_writer_trial_01/astra_revise_matrix_0{1,2}/` | gpt-6-luna(既存R0流用) | gpt-6-astra | MEASURED(§107/108)。人間確認待ち |
| **W-4(R0のみ、モデル差)** | Fact Lock付きR0単独。R1/R2/EN/Checkerなし | `er052_output/writer_r0_model_impact_trial_01/` | Luna/Sol/Astra比較(**未決**) | - | MEASURED(§114)、Closeout=USER_DECISION_REQUIRED |

### 1-3. 項目別の一意性判定

| 論点 | 判定 | 根拠・状況 |
|---|---|---|
| Fact Lock block構造(構造a) | **ほぼ一意**(Trialで固定: 同一LLM呼出内、タグ【事実N】+【中核数値】/【周辺数値】) | REPORT §114「Fact Lockは同一LLM呼び出し内(構造a)」。ただしprompt逐語のProduction承認はない |
| R0/R1/R2の段構成 | **非一意**(W-1/W-2はR0→R1→R2、W-3はR3まで、W-4はR0のみ) | 1-2表 |
| 使用モデル | **未決**(R0=Luna/Sol/Astra、R1/R2=Astra[W-1,W-3]かLuna[W-2]) | §114未決。W-1のAstraは`pricing_snapshot.json` L339-357の`note`が「登録=astra採用ではない、Production採用は人間ユーザーのみ承認」。Production routingの`B1_WRITER`等は全て`WRITER_MODEL`(gpt-6-luna)で、Astraは`require_model_or_override`のTrial用overrideでのみ使用(`er052_factlock_astra_e2e_runner_01.py` `worker_new_astra`) |
| B3注記仕様 | **v2はE2E Trial用にユーザー確認済み(L20370「注記仕様v2固定」)。ただしProductionの注記手段が未定義** | 仕様v2 §範囲外「注記の自動化(Production化にはB3自身が同等の注記を自動で付ける必要があり、その精度は未測定)」。Trialの注記は「注記者(Sonnet同系の別worker)A・B+決定論統合スクリプト」(同§C)。OPEN候補「B3自動注記」は**起票未**(DECISION_LOG L20356,L20362)。Production runnerのB3(`er019 entertainment runner run_storyline_b3` L141)は注記を付けない |
| M1/M3/B1/M2の正式採用範囲 | **未決** | M1(a)=EN「In one line」生成入力へJA R2本文+Ledgerを追加(`er003_v1_n3_01_advanced_adaptation_generate.py` L577-605のPrompt変更、Advancedのみ、Standardは未実装)/M1(b)=要約のみ再生成(Checker由来)/M3=Checkerのreclassify保護(`OPEN233_RECLASSIFY_PROTECT_FLAGS`)/B1=Checker起点のWriter再実行/M2=OFF。M1(b)・M3・B1はCheckerが消えるので不要。**M1(a)だけがChecker無関係のEN段Prompt変更**で、承認範囲が決まっていない |
| Fact Lock適用範囲(Standard/Advanced) | **構造上、両方に及ぶ**(JA段で適用→両ENが同じJA R2から派生) | `er012_e` L488(Advanced入力=`ja_text`)、L617(Standard入力=Advanced EN)。ユーザー決定で両方RF対象 |
| 英訳経路 | **既存のer003/er012_e経路(JA→Advanced忠実英訳→Standard A2)が正。Fact Lock EN directは存在しない** | `er012_e._run_writer_stage_once` L467〜(W1 2026-09-29正式)。E2E新腕も同経路を再利用(`worker_er019_shim`) |
| 回復手段 | W-1のB1(Checker起点)は撤去対象。Checkerなしの運用でWriterが重大Fact誤りを作った場合の回復はRF→Human Review→人手 | 12節S2-1 |

### 1-4. FACTLOCK-ASTRA-E2E-TRIAL-01(方向判断(a)〜(e)未回答)との関係

- 今回のユーザー決定(新Writer配線を一括に含める)は、W-1の採用を**暗黙に示唆する可能性はあるが、明示されていない**。(a)人間確認+pairwise(面白さ)/(b)OC-1/3/8のOPEN化とEN段+Checker再実行/(c)指示文の本文化対策(OC-11、semiconductorの新腕固有STOP事例)/(d)保留/(e)判定基準組替え のどれも未回答。特に(c)は新Writer固有の欠陥(brief内の指示文がFact Lock R0に事実扱いされる、REPORT §111訂正(1))で、**未対策のままProduction配線すると既知欠陥を実運用に持ち込む**。
- よって本書は、W-1〜W-4のどれかをユーザーが指定するまで、**新Writer配線部(2節)をパラメータ化した骨格設計に留め、Phase 2を開始しない**(STOP S2-1〜S2-4)。

---

## 2. 新Writer配線設計(骨格。値はW候補確定後に埋める)

### 2-1. 現行Production経路と変更点(ファイル:関数)

現行: `er019 entertainment runner main`(L295)→ research/ledger(`run_research_and_ledger`)→ `run_storyline_b3`(L141)→ `run_ja_writer`(L185 → `jaw.run_ja_writer_o_r1_r2` L242〜、Luna R0→R1→R2連鎖)→ `efam.run_writer_stage(only="advanced")`(L378)→ `only="standard"`(L389)→ Mandatory STOP(L396付近)。

| # | 変更点 | 初回 | retry | fallback | regeneration | resume |
|---|---|---|---|---|---|---|
| N-1 | 新Production module `er053_family_x_factlock_ja_writer_01.py`(仮): R0ブロック定数・Revise段・タグ処理(`strip_tags`/`assert_no_tag_leak`/R0復唱検出)・注記版brief parse。**Trial scriptをimportしない**(2-2)。戻り値は`jaw.run_ja_writer_o_r1_r2`と同形(`stages.original/r1/r2`、`final_text`)にして下流保存(`original.md`/`revision1.md`/`revision2.md`)を無変更で通す | `er019 run_ja_writer` L185が新moduleを呼ぶ | 技術retryのみ(Astra API transient 2回、Trial `call_astra`と同値) | `previous_response_id`連鎖はAstra段で不使用(Trial `previous_response_id_used=False`)のため、現行のJA chain fallback(T-03)は新moduleで不要。R0は単発`call_fresh` | `--regenerate-stage writer`(L352-357)でR0から全段再実行 | JA再利用分岐(L354-357)は技術的に残す |
| N-2 | `run_storyline_b3`(L141)の後に**注記stage**を新設(S2-2が決着後): `storyline_b3/selected_brief_annotated.md`+サイドカー。再利用分岐(L330-336)は注記済みの有無も判定 | ○ | 注記format/検査FAIL時の扱いは**未決**(Trialは「1回再委任後STOP」、Productionの手段が未定義) | - | `--regenerate-stage storyline_b3`で注記も再実行 | ○ |
| N-3 | `er012_e._run_writer_stage_once`(L467)/`run_writer_stage`(L737): 旧Checker全撤去(4節)。入力`ja_text`は新Writerの`revision2.md`(タグ除去済み)のまま | - | 段落3分割retry(T-04)は維持 | `fallback_detected`(T-05)は維持 | `only="advanced"/"standard"`は維持 | - |
| N-4 | `er006_model_routing_contract_01.py` `PROCESS_MODEL_MAP`(L80〜)へ追加のみ: `FAMILY_X_FACTLOCK_R0`・`FAMILY_X_FACTLOCK_REVISE`(値はW確定後。W-1ならLuna/`gpt-6-astra`)。環境変数上書きなし、`require_model`でAPI call前にfail-closed | ○ | - | Astra段のmodel不一致(`resp.model`が要求modelで始まらない)は**fail-closed STOP**(Trial `call_astra`のProvenanceViolation相当) | - | - |
| N-5 | 記号QA(T-01/T-02)は維持: R0直後・R2直後に`safety.detect_prohibited_symbols`、必要なら**1回だけ**再生成→なお残ればSTOP(`JASymbolCheckStopError`、4節B-1)。Trial E2E新腕ではR2の記号検査はer019再利用分岐に乗せるため**迂回されていた**(`worker_new_astra`はfindingsを記録のみ)。Productionでは既存安全装置を回避しない設計(Astra段の再生成1回=既存T-02と同じ上限1、追加Promptは既存`safety.build_symbol_violation_prompt_note`のみ) | ○ | 上限1回 | - | - | - |
| N-6 | `er019 entertainment runner main`: 旧Checker関連引数(`full_ledger_text=`、`storyline_line=`/`selected_fact_brief_text=`によるJA差し戻し有効化 L375-L396)の削除 | ○ | - | - | - | - |

### 2-2. Trial専用scriptへのimport禁止の担保

1. Production moduleのPrompt・ユーティリティは**byte-identicalな定数/関数としてProduction module内に保持**(Trial moduleからimportしない。`fl.build_r0_block`/`parse_annotated_facts`/`strip_tags`等を移植)。
2. 静的test: 新module群(`er053_*`、変更した`er012_e`/`er019 *`)に対し、AST解析で`import er050*`/`er051*`/`er052*`/`*trial*`/`er052_output`パス参照が0件。`sys.modules`に`er052*`が載らないruntimeテストを併設。
3. 移植の同一性test(test内でのみTrial moduleを読む。Production runtimeはimportしない): Production定数のsha256 == Trial定数のsha256(`FACTLOCK_R0_BLOCK_HEAD`等)。Promptを変えていないことの機械証明。
4. `er052_factlock_astra_e2e_runner_01.py`はTrial参照用に残置し、撤去後は**git tag固定のworktree**で再現(8節)。同runner L372の`_SCRIPTS` sha・L896-914のmonkeypatchはtag時点のtreeでのみ整合(Opus論点2)。

### 2-3. Fact Lock入力(台帳)の構築経路

- Writerへの入力は**完全台帳ではなく「注記版B3 Selected Fact Brief」**(`storyline_b3/selected_brief.md`に【事実N】行頭番号と【中核数値】/【周辺数値】印)。完全台帳(`research_ledger/verified_fact_ledger.txt`)はWriterに入らず、**RF(5節)の入力**になる(TrialのFact Lock Writer→RFの関係と同じ)。
- 注記版briefの作り方が未決(S2-2)。注記仕様v2の機械規則(`b3_annotation_check_01.py`の`compute_expected`: 数値の中核/周辺をスクリプトが計算、台帳ID境界での事実分割、サイドカー宣言との完全一致検査、`b3_annotation_merge_01.py`の決定論統合)は**Production moduleへ移植可能な決定論部分**。移植不能なのは「注記者(LLM)の判断部分」の方式(Production APIで何を使うか・精度)で、これが未測定。
- **STOP**: 注記の自動化方式(LLM注記+決定論検査か、決定論のみか)と精度閾値の設計は新仕様。本書は決めない。

### 2-4. 英訳(Standard/Advanced)の経路

既存`er012_e._run_writer_stage_once`(JA R2→Advanced忠実英訳[`adv_gen.generate_family_x_faithful_translation` L488]→「In one line」生成→段落3分割検査→Standard[`std_gen.generate_family_x_standard_a2_no_heading(advanced_text)` L617]→段落検査)を**そのまま使う**(旧Checkerの9呼出+retry/STOPのみ撤去)。「In one line」生成は`adv_gen.generate_family_x_in_one_line(client,title,body)`をM1なしで直接呼ぶ(M1(a)の扱いが決まるまで既存挙動を維持=Opus必須修正1の`_open243_iol`非依存化と一致)。**M1(a)を新Writer仕様に含める決定がなされた場合は、Standard側に同等処理が無い(M1 Standard未実装・未測定)点が新たな非対称になる**(3節行3)。

---

## 3. Standard/Advanced非対称棚卸表(16行)

委任文の列挙語は16個(Writer入力・経路/翻訳経路/Fact Lock適用/RF/Fact Checker/retry/fallback/regeneration/Review Queue/TTS前Gate/TTS routing/Key Phrase処理/audio QA/technical validators/model routing/runtime exception handling)。「15項目」表記とずれるため16行で作成。分類: **①意図的Level差**(英語難易度・KP説明・語彙文構造)/ **②Level差で説明できない非対称**(②-a既存承認仕様で説明可/②-b実装漏れ/②-c新仕様判断が必要=STOP候補)。

| # | 項目 | 現状(Advanced=b1b / Standard=a2) | 配線後 | 分類 | 根拠 |
|---|---|---|---|---|---|
| 1 | Writer入力・経路 | Adv: JA R2全文→忠実英訳。Std: **Adv EN全文**→A2(JAは直接入らない) | 同じ(新WriterはJA R2の中身のみ変える) | ①(CURRENT_SPEC L829-830のAdv/Std定義) | `er012_e` L488,L617 |
| 2 | 翻訳経路 | Adv=`NATURAL_ENGLISH_ADAPTATION`、Std=`STANDARD_A2_ADAPTATION`。いずれも`WRITER_MODEL`(gpt-6-luna)、max_attempts=2の技術retry・構造(Title+Body)gate | 同じ | ① | `er003_v1_n3_01_advanced_adaptation_generate.py` L69,L440,L664〜、`er003_v1_n3_01_standard_a2_generate.py` L89,L415,L541〜 |
| 3 | Fact Lock適用 | Fact Lockは未配線。Trial新腕ではJA段で適用(両ENが派生)。**M1(a)はAdvancedの「In one line」だけ(Standard未実装)** | Fact Lock=両Level継承(①)。M1(a)を採るなら**Advとの非対称が新規発生** | ①(Fact Lock)/ **②-c(M1(a)の適用範囲、新仕様判断=STOP候補S2-4)** | `er012_e` L459-464、`adv_gen` L577-605 |
| 4 | RF | 現状なし。Trial=Advancedのみ検証(11本) | **両Levelに適用**(ユーザー決定)。Standardは検証母集団外=`MODEL_STATS`を`article_level`層別に出し経過観察 | ①(新規、対称) | DESIGN_01 7節差1、本書5節 |
| 5 | Fact Checker(旧) | 両方にdeviation check。**AdvancedのみM1要約再生成経路あり(env既定OFF)**、StandardにM1なし | 両方撤去(非対称ごと消滅) | ②-a(M1はTrial専用・既定OFF・CURRENT_SPEC未採用=既存承認仕様で説明可) | `er012_e` L530-557(Adv)、L634-680(Std) |
| 6 | retry | 両方: 段落3分割retry(1回、`_FAMILY_X_PARAGRAPH_RETRY_MUST_FIX`)+技術retry2。Adv段落retryは「In one line」も再生成(Stdは本文のみ) | 同じ(Checker由来must-fix retryは撤去) | ①(Advは「In one line」を別生成する構造) | `er012_e` L491-507,L617-632 |
| 7 | fallback | 両方: `fallback_detected`(`model_actual != requested`)記録。JA chainの`previous_response_id` fallbackはJA段のみ(共通上流) | Luna chain fallbackは新Writerで不要(N-1)。Astra段はmodel不一致=STOP | ①(対称) | adv_gen/std_gen `fallback_detected` |
| 8 | regeneration | `--regenerate-stage advanced/standard`が各々存在。**`advanced`単独再生成後にStandardは自動追従しない(古いAdvancedから派生したまま)可能性**(`--stage all`既定なら両方再実行) | 同じ。RFはtts前に記事sha照合で古いQueueを検知(5節) | ②-a(`--stage`個別指定は既存仕様[delegation D4]。Std派生元がAdvである構造で説明可。ただしstale警告が無い点は運用注意) | `er019 entertainment runner` L378,L389,L288-290 |
| 9 | Review Queue | 新規 | 両Level、1 path=1(article,level)(5節) | ①(新規、対称) | 本書5節 |
| 10 | TTS前Gate | 両方: scaffold前のparagraph_count<3 STOP(L304-325)、shared narration Gate(L699,L1001)、assemble前Audio Validation Gate(B1 L1097/A2 L1319)。**A2のみ`japanese_title`取得WARN** | 同じ + RF tts前保険(両Level) | ①(A2はJA title segmentあり) | `er019 audio runner` L1855 |
| 11 | TTS routing | B1: Comment/Preview=Charon英語、本文/In One Line=Aoede。A2: JA title・JA Comment/Preview(JA style)・本文は`generate_a2_segment_with_slowdown`。`--tts-backend speech_metadata_flash_lite`が承認済み正式backend、両Level共通で`assert_production_tts_backend`(L1823) | 無変更 | ①(英語難易度・JA解説差) | L554-704,L820-1006 |
| 12 | Key Phrase処理 | Adv: 英語解説+phrase_repeat+text-gate(W4 2026-09-29承認)。Std: 日本語意味(`generate_a2_japanese_with_reading_safety`、W5 J3) | 無変更 | ①(承認済みLevel差。L729コメント「Standard側は対象外」) | L729-819,L1007-1068 |
| 13 | audio QA | 両方: disfluency_qa(`in_one_line`)、repetition_qa(本文3段)、記号normalizer。ASR cascadeはAdv=EN、StdのJA segment=JA ASR | 無変更 | ①(JA segmentの有無) | L654-668,L970-985 |
| 14 | technical validators | 両方: 構造Gate、Audio Validation Gate。**Stdのみ`run_checks`(数字追加/欠落をAdvとの差分で記録。観測のみ・非blocking、evidence保存のみ)** | 無変更 | ①(Stdは派生元Advがある) | `std_gen` L325-355、`er012_e` L700 |
| 15 | model routing | WRITER=gpt-6-luna、SUPPORT(B1_SUPPORT/A2_SUPPORT)=gpt-6-luna、WRITER_FACT_CHECK=gpt-6-luna。RFは追加(両Level同じ2キー) | + FACTLOCK_*(N-4)+ RF 2キー | ①(対称) | `er006_model_routing_contract_01.py` L80-92 |
| 16 | runtime exception handling | 両方`RuntimeError("[STOP] ...")`。**AdvancedのみSTOP時に`audit/rejected_advanced_attempt2.md`/`rejected_advanced_m1_summary_retry.md`を保存、Standardは保存しない** | 旧Checker撤去でdeviation由来STOP自体が消え、残る段落数STOPは両方証跡なしで対称 | **②-b(実装漏れ型。撤去対象内で消滅するため追加修正不要)** | `er012_e` L549-583(Adv)、L670-680(Std) |

**集計**: ①=12行、②=4行(②-a=2[行5・8]、②-b=1[行16]、②-c=1[行3のM1(a)])。②-cのみ新仕様判断(STOP候補S2-4)。他は勝手に修正していない(撤去・無変更・既存仕様で説明がつく)。

---

## 4. 旧Checker撤去リスト v2(Family X Production、行番号はHEAD `635111bf`)

DESIGN_01 2節のR-01〜R-22(再掲せず、そのまま有効。R2後JA Fact Check=R-02、Standard側=R-15〜R-17、retry/regeneration/fallback側=R-03/04/09/10/13/14/17/18/19、resume側=R-06/07/19/22を含む)+以下6件。**合計28行**。

| ID | ファイル:関数:行 | 到達 | 動作 | 備考 |
|---|---|---|---|---|
| R-23 | `er012_e` `open243_m1_enabled`ラッパ L369-L370 | 初・R | `adv_gen.open243_m1_enabled`(環境変数`OPEN243_M1`)の薄いラッパ | 削除 |
| R-24 | `er012_e` `_open243_iol` L459-L464(呼出L497,L500,L562) | 初・R・G | `OPEN243_M1=1`時のみ「In one line」入力へJA+Ledgerを追加 | **常にM1なし(`adv_gen.generate_family_x_in_one_line(client,title,body)`直呼び)へ**。環境変数依存を除去(Opus必須修正1) |
| R-25 | `er012_e` env`OPEN243_G3_TELEMETRY_PATH`参照 L441(R-10のG3入口) | 初 | translation起源MINORの観測telemetry | 削除(R-10と同時) |
| R-26 | `er003_v1_n3_01_advanced_adaptation_generate.py` `OPEN243_M1_ENV`/`open243_m1_enabled` L583-L602、`generate_family_x_in_one_line`のM1引数分岐 | - | M1 Prompt切替 | **Trial用として残置**(Prompt文字列・テストはTrial参照用)。Production呼出元(R-24)が消えるため不到達。静的testで保証 |
| R-27 | `er003_v1_en_direct_vfl_01_generate.py` `OPEN243_M2`環境変数 L685-L723 | - | `run_deviation_check`のprompt差替え | **共有関数のため残置**(legacy A/B/C用)。Family X経路が`run_deviation_check`を呼ばなくなるため不到達 |
| R-28 | Trial runner `er052_factlock_astra_e2e_runner_01.py` `ARM_FLAGS`/`FLAG_KEYS`(L58-59、環境変数`OPEN243_M1`/`OPEN233_RECLASSIFY_PROTECT_FLAGS`を子processへ渡す) | - | Trial専用 | **無変更で残置**。Production到達性なし。tag worktreeで再現(8節) |

**維持の明記(Opus必須修正1)**: **T-17**=`er019_family_x_storyline_b3_fact_selection_01.py`のFact ID整合STOP(L20-23,L242)、**T-18**=research_ledgerの`run_verification_for_topic`(`er019 entertainment runner` L91付近のResearch/Verification経路)。これらは「Fact Checker」ではなく入力側のFact整合Gateであり**撤去しない**。T-01〜T-16(DESIGN_01 3節)も維持。計技術QA維持18行。

**環境変数依存の除去まとめ**: Productionコード上の`OPEN243_M1`/`OPEN243_M2`/`OPEN243_G3_TELEMETRY_PATH`参照を、Family X経路(`er012_e`/`er019 *`)から全撤去(`OPEN233_RECLASSIFY_PROTECT_FLAGS`はTrial runner側のみで、Production module内に参照なし=Grep確認済み)。`os.environ.get("OPEN243_*")`を静的testで0件(`er012_e`/`er019 *`範囲)にする。

**境界の解決案(DESIGN_01 S-4/B-1,B-2を継承)**: B-1=記号QAの例外を`JASymbolCheckStopError`へ分離、B-2=`must_fix`受け口は段落retry専用として維持(`_must_fix_from_deviations`のみ削除)。Opusレビュー(DESIGN_01 14節 論点1)で妥当性確認済み。

**R2後JA Fact Check(R-02)**: ユーザー決定により**確定的に撤去**(DESIGN_01 S-2は解決)。

---

## 5. RF配線設計 v2(Opus必須修正3〜6・8を取り込み)

### 5-1. 挿入位置(Opus論点4)

- **主**: `er019 entertainment runner`の**各Level生成直後**。`efam.run_writer_stage(...only="advanced")`の後(L378-L387)で`risk_flag(level="b1b")`、`only="standard"`の後(L389-L396)で`risk_flag(level="a2")`。いずれも**Mandatory STOPの前**。`--stop-after advanced`で早期returnする場合もAdvanced分は実行済み。
- **保険**: `er019 audio runner main`の`tts`分岐(L1908)内、`assert_production_tts_backend`(L1911)の直後・各`generate_family_x_*_segments`の前に`ensure_rf_record(source_dir, level)`: `article.md`のsha256を計算→`review_queue/post_en/index.jsonl`に同(article_id,article_level,sha)のレコードがあればOK、無ければ**その場でRFを実行**(非Blocking、RF_UNAVAILABLEでもTTSへ進む)。audio側`all`は`plan`を含まない(L1876のplan分岐は`--stage plan`/`--dry-run`のみ)ため、`--stage tts`単独や`all`でも保険が効く。
- **非採用**: DESIGN_01のD-1推奨(audio runnerの`risk_flag` stageを`all`に追加)は、Opus指摘どおり個別stage実行で抜けるため主にしない。

### 5-2. 入力・実行・保存

- 対象: **Advanced(`b1b/article.md`)とStandard(`a2/article.md`)の両方**、完全台帳=`research_ledger/verified_fact_ledger.txt`(B3 Briefは使わない)。
- **4条件を逐次実行**(Luna A3→Luna A4→Gemini A3→Gemini A4。約25秒/Level、2Levelで約50秒、DESIGN_01 8-4実測値ベース)。`er005_cost_logger._CONTEXT`がglobal(L27,L42,L79)で並列だと競合するため(Opus論点7)。
- Luna=OpenAI Responses(`reasoning.effort=medium`、`max_output_tokens=8000`)。SDK patch(`er005_cost_logger` L110-146)が自動で`raw_usage_log.jsonl`へ記録するため**RF側で二重記録しない**(test: Luna 1callにつき記録1件)。Gemini=REST(Trial同一body、DESIGN_01 7節)。GeminiのRFレコードは`er005_cost_logger.record()`(L76)で`provider="gemini"`・`model_id`=pin値・`input_tokens`・`output_tokens`=`candidates+thoughts`・`reasoning_tokens`=`thoughts`・`cost_usd`併記・stage tag=`risk_flag.<model_key>.<A3|A4>`を書く。
- A3/A4 prompt: Production moduleにbyte-identical定数で保持、起動時sha assert(`9d995042…`/`c87b95e5…`)。不一致=`RF_UNAVAILABLE(prompt_sha_mismatch)`。Prompt変更なし。
- 完全台帳parser: 補正済みHDR regex(`^\[(?P<st>[A-Z_]+)(?:\s+-\s+[^\]]*)?\]\s+(?P<id>[^\s:]+):\s*(?P<text>.*)$`)。**台帳完全性assert**=行頭`[`行数==regex見出し数==parsed件数==ID一意。不一致=`RF_UNAVAILABLE(ledger_incomplete)`(Opus論点4)。**実装前に既存全台帳の¥0走査test**(10節T-4)。
- **記事sha不変assert**: RF開始前後で`article.md`のsha256が一致(RF moduleはarticleを書き込まない。書込先allow-listは`review_queue/post_en/**`と`<out_dir>/risk_flag_fallback/**`のみ)。
- splitter: 共通module(7節)。`sentences.json`(全文ID対応表)を同梱。

### 5-3. 保存先・schema(Opus論点5の修正a〜dを反映)

- パス: `review_queue/post_en/<article_id>__<article_level>__<sha8>__<rf_run_short>/`(**1 path = 1(記事,Level)**、levelは`b1b`/`a2`)。`index.jsonl`は1行=1 path(追記専用)。tts前保険の照合は(article_id,article_level,article_sha256)で行い、同shaで`RF_UNAVAILABLE`があっても自動再実行しない(支出増の抑止、手動再実行のみ)。
- フィールド(ユーザー必須項目を網羅): `article_id`/`article_level`(旧`level`、A3/A4と区別)/`sentence_id`/`sentence_text`/`context`(before/after各最大2文、**Queue生成時のみ付与しLLM入力に入れない**)/`related_fact_ids`/`facts[]`(Fact本文=台帳ブロック全文)/`flag_reasons[]`/`detected_by[]`(model_key・condition[A3/A4]・confidence)/`model_id_requested`・`model_id_returned`/`confidence`/`raw_flag_source`(`raw/`内の各条件API生応答)/`run_id`/`timestamp`。追加: `issue_id`=`<article_id>__<article_level>__<sha8>__<sentence_id>`(同記事の再生成・再実行と衝突しない、Opus(b))/`inputs/{article.md,ledger_full.txt,sentences.json}`同梱(Opus(d))。
- **`review_state`は削除**(Opus(c)。Human Reviewの判定はChatGPT側が保持し、Queueは候補一覧に徹する。書き戻し先は別ファイルで定義するまで持たない)。
- 重複統合: OR統合、キー=(article_id,article_level,sentence_id)、同一文のA3/A4・Luna/Geminiは1 issue。文ID不一致のFlagは`unlocated_flags`へ別掲。
- `index.jsonl`: ロックファイル(`index.jsonl.lock`、O_EXCL+retry/timeout)で排他、追記は1行1write+fsync、既存行不変。**保存path・`review_queue`ルートは`__file__`基準**(`os.getcwd()`非依存、Opus必須修正6)。
- **S-9運用(Open Item化)**: runnerはgitを触らない。RF実行後にClaude Codeが当該dirと`index.jsonl`だけを明示`git add`→commit→push(Closeout必須項目: push漏れ検知=`git status --porcelain review_queue/`が空かつ`git ls-files review_queue/post_en/`に当該dirがあること)。量産時にこの責務を誰がどの粒度で担うかが曖昧(運用Open Item、実装範囲外)。

### 5-4. RF_UNAVAILABLE・障害・失敗時fallback

- 記事Levelの状態: 4/4成功=`OK`、1〜3成功=`PARTIAL`、0成功/入力不整合=`RF_UNAVAILABLE`。どの状態でもTTS以降へ進む(STOP・article再生成・Rewrite・削除なし)。API技術retryは有界(transient 2回+format 1回、DESIGN_01 6-2。ユーザー方針「API technical retryは維持」)。
- **RF_UNAVAILABLE可視化4点(Opus必須修正4)**: ①標準エラー出力に`[RF][WARN] RF_UNAVAILABLE ...`バナー ②`entry_point.json`に`risk_flag.<level>={status,reason,queue_path,article_sha256}`を追記 ③`MODEL_STATS`にUNAVAILABLE/PARTIAL件数を表示 ④報告時列挙(集計scriptが非OK Queue一覧を`UNAVAILABLE_LIST`へ、Closeoutチェックリスト化)。
- **Queue保存失敗時**: `except Exception`(`BaseException`は捕まえない)の範囲でTTS継続+`<out_dir>/risk_flag_fallback/<…>`へ同内容を保存+WARN+`entry_point.json`記録。out_dirにも書けない場合は標準エラーにJSON要約を出し`RF_UNAVAILABLE(save_failed)`。古いQueueはtts前sha照合で検知。
- モデル自動切替・`ModelContractViolation`/`PricingNotFoundError`の自動回避なし(Fail-Closed維持、当該条件を`FAILED`記録)。
- 台帳完全性・prompt shaなどの入力不整合も同じ`RF_UNAVAILABLE`として可視化。

---

## 6. 費用機構修正設計(ユーザー承認3ギャップ+Opus必須修正7)

| # | ギャップ | 修正 | 計算式・出典 |
|---|---|---|---|
| G-1 | `gemini-3.5-flash-lite`単価未登録(DESIGN_01 8-2) | `er005_output/cost_baseline_01/pricing_snapshot.json`へ`provider="gemini"`、`model="gemini-3.5-flash-lite"`、meter `input_tokens`/`cached_input_tokens`/`output_tokens`、tier Standard、`source_url`、取得日、確認方法を登録 | **$0.30 input / $0.03 cached / $2.50 output(per 1M tokens、出力はthinking tokens含む)**。出典: `https://ai.google.dev/gemini-api/docs/pricing`、取得2026-10-10T04:50Z(`er052_output/writer_dev_risk_flagger_01/meta_rollback_crossmodel_01/xm_prices_01.json`)。**Phase 2実装時に再確認して登録**(価格は出典付き確認済みのみ。fallback単価の自動使用は禁止)。単価キーはpinしたmodel_id、返却`modelVersion`は別フィールド |
| G-2 | Gemini thinking token未計上(`er005_cost_logger._gemini_usage_to_dict` L152-159が`candidates_token_count`のみ) | RFのGemini呼出はREST(同loggerのSDK patchを経由しない)→RF moduleが`cl.record()`で互換レコードを書く。**SDK patch側へ`thoughts_token_count`を足す案**は同loggerを使う他経路(TTS等)の費用計上が変わりうるため本Wiringでは採らず、RF側だけでcandidates+thoughtsを`output_tokens`に入れる(最小変更) | `cost_usd = input×0.30/1e6 + cached×0.03/1e6 + (candidates+thoughts)×2.50/1e6`、JPY=`×efam.USD_JPY` |
| G-3 | stage集計がopenai限定(`er019 entertainment runner.compute_stage_cost_breakdown` L240-L271、`provider=="openai"`のみ) | `gemini`を集計対象へ追加(stage tag=`risk_flag.<model_key>.<condition>`で4条件別に出る)。audio側`compute_cost_jpy_so_far`(L1528)は既に`by_provider`集計 | 条件別call数/token/costを`queue.json.conditions[]`・`runtime_evidence.json`・`raw_usage_log.jsonl`の3点で追跡可能 |
| G-4(Opus) | audio側`compute_cost_jpy_so_far` L1557-1564は単価未登録を0円扱い(fail-open)、efam側`_load_pricing`(L106-121)はfail-closed。RFレコードが`<out_dir>/raw_usage_log.jsonl`にあると`--regenerate-stage`→`assert_budget_ok`で`PricingNotFoundError`STOPとなりうる | G-1の単価登録を**Phase 2の前提条件**にする。audio側をfail-closed化(未登録→`PricingNotFoundError`)し、`er006_model_routing_pricing_coverage_test_01.py`で現行Production全model(TTS含む)の単価網羅を回帰保証してから変更 | 既存TTS経路に未登録modelがあればSTOPで露呈する(¥0 testで事前確認。S2-8) |
| G-5 | Luna二重記録 | RFは**Lunaを手動記録しない**(SDK patchが自動記録) | test: Luna 1callにつき記録1件 |

- 新Writerのモデル費用(Astra等)はW確定後。Astra単価は登録済み(`pricing_snapshot.json` L339-357、「Trial/DEV用、採用ではない」noteをProduction採用時に更新)、請求ダッシュボード照合は未実施(ガードは安全係数×1.5、DECISION_LOG L20372付近)。
- Gemini A4経過観察(`MODEL_STATS`、モデル別×`article_level`別): articles processed/A3 flag count/A4 flag count/unique issue count/overlap count/zero-flag article count/UNAVAILABLE・PARTIAL件数。Gemini A4が0件でも停止・削除・モデル変更なし。

---

## 7. splitter共通module設計

- **所在**: `er053_en_sentence_splitter_01.py`(新設、Production module)。依存は標準ライブラリ`re`のみ。**Trial module・er052をimportしない**。RF module・Queue writer(将来は他のProduction経路も)が使う**共通実装は1箇所**。
- **略語リスト出典**: `er052_open233_self_recovery_flow_runner_01.py` `_VS_L6_ABBREV` L5477-L5480(33語: `u.s` `u.k` `u.n` `mr` `mrs` `ms` `dr` `prof` `sr` `jr` `jan` `feb` `mar` `apr` `jun` `jul` `aug` `sep` `sept` `oct` `nov` `dec` `st` `no` `vs` `e.g` `i.e` `inc` `co` `ltd` `corp` `a.m` `p.m`)、補助`_vs_l6_abbrev_period` L5486(`no`は直後が数字、`st`は直後が大文字のときだけ略語扱い)、`_VS_SENT_END_RE` L4944。**Trialからの「切り出し」=Production moduleへの移植(コピー)**(Productionからimportできないため。Trial runnerは無変更)。**注記**: ユーザー決定の「複製禁止」は「Production内に実装を2つ持たない」意味に解釈(Production内ではこのmoduleがRF用の唯一の実装)。Trial側とのコード重複は依存方向規則上避けられないため、**等価性testで乖離を機械的に検出**する。解釈違いがあればユーザー確認(軽微、STOPにしない=S2-10)。
- **出力契約**: DESIGN_01 4-3どおり(見出し行`# `も1文、`\n`でも分割、文字列list+`sid`=`s1…`出現順)。`splitter_version="en_split_v1"`をQueue/runtime evidenceへ記録。
- **golden test**: (1) Regression必須6件(`U.S. officials said…`/`The U.K. government announced…`/`U.N. officials…`/`Mr. Trump spoke.`/`Dr. Smith agreed.`/`…on Jan. 5.`)が途中分割されない+通常の文末分割(`It rose 5%. Prices fell.`→2文)、閉じ引用符、`No. 5`/`St. Louis`/`a.m.`/`USA TODAY Co. said`/`Inc.`/`e.g.`、見出し行、`...`。(2) 33語の網羅(リストを表で固定し、test内でTrial側リストと同一性を比較)。(3) **等価性**: `vs_sentence_segments_l6`の出力(テキスト化)とTrial 11入力で一致(test内のみTrial import)。(4) **他経路不変**: `er003_ja_to_en_translation.split_sentences`(C)・`er010 split_sentences`・Trial(A)/(B)のファイルdiff 0、同一fixtureで出力不変。(5) 実データ: Trial 11入力で略語終わり文0件+それ以外は旧(A)と同一(差分は略語結合のみ、U03/U06/U07/X09/X10/X11)。
- **文ID変更**: 承認済み(ユーザー決定)。Trial照合済み文IDとズレるため、照合は`sentence_text`+`splitter_version`で行える(Queueに両方保持)。LLMへ渡すsentence listが変わる点はRESULT/REPORTに明記。
- **依存方向**: Production(RF module)→splitter。splitter→他へ依存なし。Trial→splitter(将来Trialが採用する場合)は許可方向だが本Wiringでは変更しない。

---

## 8. Rollback設計

- **隠れswitchは作らない**(`fact_check_mode`/`LEGACY_CHECKER`等の環境変数・CLI引数なし)。撤去はProduction pathからの**物理削除**(案P)、旧コードは**Git履歴とTrial artifactに保持**。Opus論点2(凍結コピーは不可)どおり、**git tag+worktree**。
- **tag名**: 撤去直前commit=`rollback/pre-factlock-rf-wiring-01-20261010`(実装開始時にFableが`git tag`で付与。`git tag`で現在tagは0件を確認済み)。Wiring完了時に`post-wiring-01`を付与し範囲を明確化。
- **commit分割(revert容易化)**: C1=追加のみ(RF module/splitter/新Writer module/集計script/README/routing・pricing追加)、C2=Writer差替え+旧Checker撤去(`er019 ja_writer`/`er012_e`/`er019 entertainment runner`)、C3=audio runner tts前保険+費用機構修正。**revert順 C3→C2→C1**(いずれも`git revert <hash>`の明示変更。force push・履歴書換えなし)。
- **旧腕再現(Trial旧Checker経路を動かす場合)**: `git worktree add ../eigo-radio-legacy rollback/pre-factlock-rf-wiring-01-20261010`で旧treeを展開し、そこで`er052_factlock_astra_e2e_runner_01.py`等を実行(L372の`_SCRIPTS` shaがtag時点のファイルと一致する)。
- **復旧の判断**: 戻す場合は明示的な復旧変更(ユーザー判断→C1〜C3のrevert)。環境変数のON/OFFでは戻らない設計で、誤作動(旧Checkerの意図しない復活)を担保。
- **静的test**: Production module群に`fact_check_mode`/`legacy_checker`/`OPEN243_*`/`OPEN233_*`のenv参照・CLI引数が0件。

---

## 9. Runtime evidence計画

### 9-1. L3(最終Evidence)

- **内容**: 新規記事1本の完全経路(research→ledger→B3→**(注記)**→新Writer JA→EN Advanced→EN Standard→RF(両Level)→Queue保存→git push→scaffold→TTS→assemble→player)を**Production正式path**(`er019 entertainment runner --stage all` → `er019 audio runner --stage all --tts-backend speech_metadata_flash_lite`)で実行。Trial runner経由は不可。
- **テーマ**: **未指定のためSTOP**。開始前チェックで`--theme`/`--slug`がユーザー指定でなければ**課金前に停止**する。候補(PM_GOVERNANCE 13節、英語+日本語+選定理由。DESIGN_01 11-2から未選定5件を再掲。**現在のニュース性・一次情報取得可否・台帳が3件以上育つかは未確認**): a. Japan's Minimum Wage Increase Takes Effect(最低賃金の引き上げが各地で始まる。都道府県別金額・上げ幅の混同でRFの効きを見られる)/ b. Coffee Prices Surge: Why Your Cup Costs More(コーヒー価格の高騰、なぜカップが高くなるのか。因果断定と「要因の一つ」の書き分け)/ c. A Crewed Moon Mission Schedule Update(有人月探査ミッションの日程見直し。計画/目標/決定の確からしさ段階)/ d. A New Study Links Sleep Habits to Health Outcomes(睡眠習慣と健康の関連を示す新しい研究。相関と因果・対象者範囲)/ e. Record Heat and the Strain on a Power Grid(記録的な暑さと電力需給のひっ迫。需要記録・予備率の数字)。選ぶのはユーザー。
- **証明項目15件とチェック方法・ログ所在**(`runtime_evidence.json`+`review_queue/…`+`raw_usage_log.jsonl`):

| # | 証明項目 | チェック方法 | ログ所在 |
|---|---|---|---|
| E1 | 新Writer(Fact Lock R0→R1→R2)がProduction moduleで実行された(Trial module非import) | `ja_writer/`のstage meta(model_id requested/returned、prompt sha)、`sys.modules`にer052なし | `ja_writer/audit/`、entry_point.json |
| E2 | 使用model_idが承認値で、mismatch 0 | requested vs returned | 同上+`runtime_evidence.json` |
| E3 | 旧Checker呼出0(JA R0後/R2後・EN Adv/Std・must-fix・案B) | `raw_usage_log.jsonl`のstage tagに`ja_*_check`/`*_must_fix`/deviation系なし、`audit/deviation_check*.json`が生成されない | raw_usage_log.jsonl |
| E4 | RFが英訳完了後・TTS開始前に実行(Adv・Std両方) | timestamp順(entertainment runner内、audio tts前保険の照合ログ) | entry_point.json、queue.json.generated_at |
| E5 | 4条件×2Levelのcall完了、model_id_returned記録 | `queue.json.conditions[]` | review_queue |
| E6 | 条件別call数/token/cost(Gemini thinking込み)記録 | conditions[]とraw_usage_logの突合 | 同左 |
| E7 | 台帳完全性assert PASS(実台帳) | `inputs.ledger_fact_count`==expected | queue.json |
| E8 | 記事sha不変 | RF前後のsha一致 | queue.json.inputs |
| E9 | OR統合・重複統合・detected_by保持(実例なければfixtureで補完を明記) | issues[] | queue.json |
| E10 | 略語文の途中分割0 | sentences.jsonに略語終わり文なし | review_queue |
| E11 | Queueのcommit/push完了+raw URLで取得可能+push漏れ検知 | `git ls-files`/`git status`/raw URL取得 | Git |
| E12 | RF_UNAVAILABLE fault injection(¥0)でTTS以降へ進む | 4可視化点が出る | entry_point.json |
| E13 | TTS以降の技術QA(Audio Validation Gate・KP source整合・Review Lock)が従来どおり | assemble完了/Gate出力 | audio out_dir |
| E14 | Standard/Advanced非対称棚卸②項目が実行で差を生んでいない | 3節②行(3,5,8,16)のログ確認 | audit/ |
| E15 | 費用が見積範囲内、Gemini A4 0件でも停止/変更なし、MODEL_STATS出力 | cost.json、MODEL_STATS.json/.md | review_queue |

### 9-2. 費用見積(根拠行=既存実測。未確認は未確認)

| 工程 | 値 | 根拠 |
|---|---|---|
| research+ledger+B3 | ¥13.5〜¥57.4/テーマ(中央値¥27.6) | `er052_output/factlock_astra_e2e_trial_01/stage_r/COST_STAGE_R.md` |
| B3注記 | **未確認**(Production手段が未定義) | S2-2 |
| 新Writer JA(W-1の場合) | R0 Luna約¥1.5(見積、runner `EST`定数)+Astra R1+R2 約¥30.6/生成(raw、×1.5ガードで約¥45.9) | REPORT §111「Astra R1+R2は1生成raw ¥30.6」。Production単価は**未確認**、請求照合未実施 |
| EN Advanced+Standard(Checkerなし) | **未確認**(既存¥4.22はChecker込みでstage内訳なし。Checker分を除いた値は未測定) | DESIGN_01 11-3 |
| RF(両Level) | 約¥1.49(Adv実測¥0.747、Stdは外挿=未確認) | DESIGN_01 8-4 |
| 音声 | ¥23.98(meta run_03実測、openai 5.09+gemini 15.58+asr 3.31)〜¥89.03(別run、条件差未確認) | DESIGN_01 11-3 |
| **L3合計(W-1仮定、単純和の推定)** | 下限≈¥13.5+¥1.5+¥30.6+¥1.5+¥24≈**¥71**、上限≈¥57.4+¥1.5+¥45.9+¥1.5+¥89≈**¥195+**(注記・EN分は未確認で含まず) | W-2(全Luna)なら新Writer分が約¥3〜5に下がる見込み(Luna R0実測¥1.24[§114]からの推測)。runner既定`--budget-jpy 150`ではW-1上限を超えうる→**Cap設定はFable/ユーザー判断**(S2-6) |

### 9-3. L2(既存METAで代替)の技術的同等性判定: **言えない**

DESIGN_01 11-1のL2は旧Writer前提だった。今回は新規経路が増えるため再判定した。既存METAで再実行できるのは(a)新Writer JA段(research_ledger・storyline_b3を再利用し、JAは再生成)、(b)EN Advanced/Standard、(c)RF、(d)tts前保険、(e)音声。**同等と証明できない理由**:
1. **注記stage(N-2)の入力が新規B3出力ではない**: 既存META `storyline_b3/selected_brief.md`は旧B3の未注記出力。注記の自動化方式が未定義(S2-2)のため、「注記済みB3を新B3出力から作る」という初回pathの核を通せない。
2. **research→ledger→B3の新規生成path・fresh out_dir(resume分岐を通らない初回path)を通らない**。台帳の`[AMBIGUOUS - …]`見出し・数値混在の出現条件は記事依存で、META 1本では網羅できない。
3. **METAはE2E Trialの開発テーマ(旧4テーマ)**で、新Writerの汎化の証拠にならない(REPORT §111「旧4=開発テーマ、新5=out-of-sample。新5の新腕介入5/10対1/10が汎化性能の正直な推定値」)。
4. Metaは過去Trial(Meta rollback等)の題材で、新Writer出力が既に評価パックに存在し、「新規記事と差がない」ことを技術的に示せない(同一テーマのため差の分離不能)。
→ **L3が必要**。L2案は提示しない(技術的同等性を証明できないため)。L1(RFのみ、既存記事)は予備確認として維持可能(約¥0.75〜1.5)。

---

## 10. テスト計画(全て¥0、mock/fixture/既存artifact)

| # | test | 内容 |
|---|---|---|
| T-1 | splitter regression+golden | 7節 |
| T-2 | 旧Checker不到達static test | AST+`git grep`: `er012_e`/`er019 ja_writer`/`er019 entertainment runner`/新Writer module/`er019 audio runner`に`run_deviation_check`・`JARecheckRequiredError`・Fact用`JAFactCheckStopError`・`_must_fix_from_deviations`・`open243_*`・`OPEN243_`/`OPEN233_` env・`ja_original_check`/`ja_r2_check`/`deviation_check`の参照0件。**retry/fallback/regeneration/resume各経路**(`--regenerate-stage advanced/standard/writer/storyline_b3`、JA再利用分岐、段落retry、`run_writer_stage(only=)`、記号QA retry、Astra技術retry)をmock実行し`vfl01.run_deviation_check`が呼ばれないことをspyで確認 |
| T-3 | 技術QA維持test | T-01〜T-18に対応する既存testの回帰(記号Validator→`JASymbolCheckStopError`、段落retry→STOP、予算ガード、`fallback_detected`、Audio Validation Gate、KP source整合Gate、T-17/18の整合STOP) |
| T-4 | 台帳全件走査(¥0) | `git ls-files '**/verified_fact_ledger.txt'`全件で expected==regex==parsed==ID一意。失敗件は一覧化し、補正parserで通るか/新形式の存在を確認(Opus必須修正4) |
| T-5 | Queue保存test | schema validator(手書き)、OR統合・重複統合、`unlocated_flags`、`context`はLLM入力に不含、`index.jsonl`排他・追記専用、`__file__`基準path、非ignore(`git check-ignore` rc=1)、**Queue保存失敗時のfallback**(except範囲、`entry_point.json`記録)、古いQueue検知(tts前sha) |
| T-6 | 記事sha不変test | RF前後のsha一致、RF moduleの書込先allow-list静的検査 |
| T-7 | 費用計上test | Gemini単価登録後の`cost_usd`==`in×0.30+cached×0.03+(cand+thoughts)×2.50`(per 1M)、4条件別集計、Luna二重記録0、`compute_stage_cost_breakdown`がgemini集計、audio側fail-closed(未登録model→`PricingNotFoundError`)、既存全model単価網羅 |
| T-8 | 新Writer module test | Prompt定数sha==Trial(test内のみTrial読込)、R0→R1→R2のmock実行、タグ除去・`assert_no_tag_leak`・R0復唱検出、Astra model不一致→STOP、記号QA再生成上限1、`routing.require_model`のfail-closed、Trial script非import(AST+`sys.modules`) |
| T-9 | 障害系fault injection | 4条件全失敗/1条件失敗/format不正/`ModelContractViolation`/`PricingNotFoundError`→`RF_UNAVAILABLE`/`PARTIAL`が記録され、例外が伝播せずscaffold/ttsへ進む |
| T-10 | 非対称棚卸回帰 | 3節②行(3,5,8,16)が配線後に意図どおり(Adv/Stdで同じ撤去・同じ保存)かをmockで確認 |
| T-11 | Dangling reference grep list | `OPEN243_M1`/`OPEN243_M2`/`OPEN243_G3_TELEMETRY_PATH`/`OPEN233_RECLASSIFY_PROTECT_FLAGS`/`open243_m1_enabled`/`_open243_iol`/`JARecheckRequiredError`/`JAFactCheckStopError`/`_must_fix_from_deviations`/`_major_deviations`/`build_must_fix_block`(JA)/`original_must_fix`/`ja_original_check`/`ja_r2_check`/`deviation_overall_status`/`must_fix_used`/`retried_for_deviation`/`ja_recheck`/`fact_checks_summary`/`full_ledger_text=`(JA writer)/`er019_writer_run_summary_reconstruction`、docs(CURRENT_SPEC項目4/5 L1230-L1262付近、OPEN-189/233/243/244、PM_BRIEF)の更新漏れ。残るのはTrial参照・legacy・`SUPERSEDED`注記済みに限る |
| T-12 | Standard/Advanced対称test | RF・Queue・撤去・保険がb1b/a2で同一の呼出しで動くこと |

---

## 11. Phase 2 実装順序・規模・Gate 3

### 11-1. 変更ファイル一覧(番号`er053_*`は仮。★=DESIGN_01から追加)

| # | ファイル | 種別 | 規模(見込み) |
|---|---|---|---|
| 1 | `er053_family_x_risk_flagger_production_01.py` | 追加(RF本体) | +700〜900行 |
| 2 | `er053_en_sentence_splitter_01.py` | 追加 | +100〜150 |
| 3 | `er053_risk_flagger_aggregate_01.py` | 追加 | +120〜180 |
| 4 | `review_queue/post_en/README.md` | 追加 | 小 |
| ★5 | `er053_family_x_factlock_ja_writer_01.py` | 追加(新Writer、W確定後) | +400〜600 |
| ★6 | 注記stage module(S2-2決着後、方式未定) | 追加 | +300〜500(未確定、見積不能な部分あり) |
| 7 | `er006_model_routing_contract_01.py` | 追加のみ(RF 2キー+FACTLOCK 2キー) | +15 |
| 8 | `pricing_snapshot.json` | 追加(Gemini 3エントリ) | +3 |
| 9 | `er019_family_x_audio_production_runner_01.py` | 変更(tts前保険+費用fail-closed) | +80〜120 |
| 10 | `er019_family_x_ja_writer_o_r1_r2_01.py` | 変更(削除中心+例外分離) | −150〜200 |
| 11 | `er012_e_family_entertainment_two_level_runner_01.py` | 変更(削除中心) | −300〜350 |
| 12 | `er019_family_x_entertainment_production_runner_01.py` | 変更(新Writer呼出+Checker引数削除+RF呼出+gemini集計) | ±100 |
| 13 | tests(10節) | 追加・更新 | +1,200(既存8本前後の更新含む) |
| 14 | `er019_writer_run_summary_reconstruction_01.py`(+test) | 無効化(legacy注記) | 小 |
| 15 | CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/PM_BRIEF | Gate 3完了後 | 小〜中 |

合計: 新規約+1,700〜2,100行(注記moduleの規模は未確定)、テスト約+1,200、削除約−500。**変更しない**: A3/A4 Prompt、`vfl01`共有関数、legacy A/B/C、既存splitter(A)(B)(C)、Trial dir。

### 11-2. 順序・並列(PM_GOVERNANCE 8-X)

1. **前提(直列、STOP解除待ち)**: ユーザーが新Writer仕様(W候補・モデル・M1(a)等・Prompt採用・B3注記方式)を指定 → **Opus独立レビュー(条件A: 本書の一括化・新Writer配線という新しい処理フロー設計)** → Fable照合。直列理由=前工程出力依存+PM Gate。
2. **並列可(独立ファイル・独立test、同一ファイルの並行編集は禁止)**: RF module+Queue/aggregate、splitter+golden、新Writer module+Prompt同一性test、routing/pricing(Gemini単価再確認含む)、台帳全件走査test(T-4)、静的test枠。
3. **直列**: C1(追加のみ)→C2(Writer差替え+撤去、`er019 ja_writer`/`er012_e`/`er019 entertainment runner`は1ファイル1担当)→C3(audio tts前保険+費用fail-closed)→static/unit回帰→L3(API支出、予算Guardrail、RF/Writer完成が前提)→SSOT更新・commit。
4. クリティカルパス: ユーザー判断(S2-1〜4)→Opus条件A→C1(新Writer module+注記stage)→C2→L3。実工数は未見積。

### 11-3. Gate 3チェックリスト(PM_GOVERNANCE Gate 3/4、PRODUCTION_WIREDはGate 3全充足時のみ)

**Static(10項目)**: S1 Production moduleが`er050`/`er051`/`er052*`をimportしない / S2 旧Checker呼出0(AST+grep、10節T-2、Standard・R2後JA・retry/fallback/regeneration含む) / S3 各経路で旧Checker不到達(spy) / S4 A3/A4 prompt sha一致+新Writer Prompt定数がTrialと同一 / S5 model固定(routing 4キー・env上書きなし・fail-closed・pricing登録) / S6 RF非Blocking(RF結果から分岐するSTOP/Rewrite/削除/再生成/自動retry 0) / S7 splitter golden+他経路diff 0 / S8 Dangling Reference 0 or `SUPERSEDED` / S9 隠れswitch0(8節) / S10 Standard/Advanced対称test PASS。

**Runtime(15項目)**: 9-1のE1〜E15(L3、Production正式path)。

**Model evidence**: 実際のmodel_id(requested/returned)・routing key・単価出典(URL・取得日)・1記事費用・Astra請求照合状況を`runtime_evidence.json`+REPORTへ。Opus条件A/C所見の反映状況。`CURRENT_SPEC`/`DECISION_LOG`/`OPEN_ITEMS`更新・Git反映・approved specとProduction挙動の一致確認、OPEN-233系`SUPERSEDED`整理、tag付与。

**Status**: 新Writer+Checkerなし+RF+Human Review/Luna A3A4+Gemini A3A4/Standard+Advanced RF適用/両Level旧Checker撤去/R2後JA Fact Check撤去=`APPROVED_FOR_PRODUCTION`(ユーザー決定)。Gate 3全充足まで`PRODUCTION_WIRED`にしない。**ただし新Writerについては「どの仕様を承認したか」が特定されていないため、Production採用の範囲は1節決着後に確認が必要**(Production採用は人間ユーザーのみ承認)。

---

## 12. STOP候補一覧

固定STOP条件: 入力/prompt sha不一致 / Production変更が必要 / Prompt変更が必要 / 新仕様候補 / 累計JPY60到達 / 価格未確認モデル / 結果を見た再実行。委任文の指定: 新Writer仕様の一意性/モデル未決/Trial限定要素範囲曖昧。

| ID | 内容 | 該当条件 | 推奨・必要な判断 |
|---|---|---|---|
| **S2-1** | 新Writer正式仕様が一意でない(W-1〜W-4)。R0モデル(Luna/Sol/Astra)未決、R1/R2モデル未決、Astra Production routing・Production採用未承認、FACTLOCK-ASTRA-E2E(a)〜(e)未回答、Fable判定「事実安全の良化は示されず・費用約6倍」 | 新仕様判断/モデル未決 | **ユーザーがW候補・モデルを指定**。Fableは勝手に選ばない |
| **S2-2** | B3注記のProduction自動化が未設計・未測定(Trialは注記者worker2名+決定論統合。OPEN候補未起票) | 新仕様候補 | 注記方式(LLM+決定論検査/決定論のみ)・精度基準をユーザー判断。OPEN起票はFable |
| **S2-3** | 新Writer Production Prompt(Fact Lock R0ブロック、AN3第1文の置換、Astra user template、W-2なら`FACTLOCK_REVISION_BLOCK`)の採用=Production Prompt変更。承認はコンセプト単位でprompt逐語承認なし | Prompt変更が必要 | 採用Promptの明示承認 |
| **S2-4** | Trial限定要素の範囲: M1(a)(Advancedのみ「In one line」入力変更、Standard未実装)=不採用を既定提案(既存挙動維持)、M1(b)・M3・B1=Checker起点のため撤去、M2=OFF。M1(a)を採るとStandard側に非対称が新規発生 | 新仕様判断(3節②-c) | 「M1(a)なし」を推奨。ユーザー確認 |
| **S2-5** | Astra単価はTrial/DEV登録。Production採用には単価・請求照合(未実施、×1.5ガード)確認が必要。Gemini単価は取得済み・実装時再確認 | 価格未確認(Astra請求照合) | 請求ダッシュボード照合(Fable/ユーザー) |
| **S2-6** | 費用: W-1採用だと記事あたり約¥44(旧約¥7)、L3上限約¥195+ | 累計費用ガードレール | L3のCap(既定`--budget-jpy 150`では不足しうる)をFable/ユーザー判断 |
| **S2-7** | L3テーマ未指定 | 新規記事テーマ選定ルール(PM_GOVERNANCE 13節) | 9-1候補からユーザー選定。**未指定なら課金前に停止** |
| **S2-8** | audio側`compute_cost_jpy_so_far`をfail-closed化(Opus必須修正7由来)。既存TTS等の単価未登録があれば露呈 | Production変更(費用機構。ユーザー承認の3ギャップに「fail-open→closed」は明示されていない追加解釈) | 既存全model単価網羅testで事前確認、承認確認 |
| **S2-9** | Opus独立レビュー: 内容が変わった(一括化・新Writer配線・注記stage)ため条件A再実施が必要(PM_GOVERNANCE 11-3「内容が変われば再レビュー」)。Opusレビュー後はFable判断で次工程へ | Gate(必須) | Fableがレビュー依頼 |
| S2-10 | splitterの「複製禁止」解釈(Productionで1実装+等価性test、Trialは無変更) | 軽微 | 確認のみ |
| S2-11 | Queueのcommit/pushを量産時に誰が担うか(Open Item化) | 運用(実装範囲外) | OPEN_ITEMS起票はFable |
| S2-12 | OPEN-233系Checker=superseded整理。Status文言の更新(SSOT) | SSOT整合 | Gate 3後に`SUPERSEDED`注記 |

**STOP条件の該当判定(固定条件)**: 入力/prompt sha不一致=なし(RFは同一Prompt/schema、新Writer Promptは移植同一性test) / Production変更が必要=Phase 2で必然(承認範囲内、S2-8のみ追加確認) / **Prompt変更が必要=該当(S2-3)** / **新仕様候補=該当(S2-1,2,4)** / 累計JPY60到達=本委任は¥0・累計は他タスク台帳(未確認) / 価格未確認=Astra請求照合のみ(S2-5) / 結果を見た再実行=なし。

**DESIGN_01 S-1との関係**: 「新Writer未配線」はユーザー決定(一括配線)で方向が決まった。ただし配線する**内容**が未特定(S2-1〜4)のため、実質的にSTOPは継続。S-2(R2後JA FC)・S-3(Standard適用)・S-10(legacy不変)・D-1(挿入位置)はユーザー方針更新と本書5節で解決済み。S-4〜S-9は本書4〜8節に取り込み済み。

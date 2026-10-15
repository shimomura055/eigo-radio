# VALIDATION_WIRING_03: KP gloss再整合(修正版corrected)Production正式runner runtime evidence(KGCPW 委任_03、2026-10-15)

管理ID: KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01 委任_03。到達Status: **EVIDENCE_COMPLETE_PENDING_FABLE_JUDGMENT**(配線・evidence取得済み、`PRODUCTION_WIRED`判定はFable=委任_04。本書は`PRODUCTION_WIRED`を宣言しない)。
対象コミット: `93f4dec16`(Productionコード差分は本委任で0: `git diff --stat -- er003_key_words_gloss_alignment.py er003_v1_n3_01_scaffold_generate.py er019_family_x_audio_production_runner_01.py er026_family_z_fiction_production_runner_01.py er062_family_z_writer_01.py er063_family_z_audio_01.py`が空)。
evidence置場: `er071_output/m2p0_n01_production_wiring_01/gloss_alignment_production_wiring_01/evidence/`。X run dir=`er019_output/family_x_audio_production_wiring_01/kgcpw_evidence_01/`、Z run dir=`er026_output/family_z_production_e2e_01/melos/run_kgcpw_z_*`(wav等の大容量はgit管理外)。Coffee完成版dir・`user_test/`・Melos原本は変更0(Coffee dirは`find -newermt`で本日更新ファイル0を確認)。

## §0 超サマリ(非エンジニア向け)
1. 「記事の英語キーフレーズと日本語の意味がズレていたら直す」新しい工程(corrected)を、本番の正式runnerで実際に動かして確認した。
2. **Family X Standardで、本番の記事(Coffee)から自然に不整合が見つかり、AIが自動で直した**(「焙煎前のコーヒー豆」→「焙煎前のコーヒー豆の価格」、1回で成功、約0.056円、約4秒)。他の4件は触らなかった。
3. Family X Advanced・Family Z(Std/Adv)の自然なrunでは対象が0件で「何もしない」が正しく動いた(API呼出0)。
4. 確実に直す場面を作るため、合成した対象(X Std/Adv、Z Std/Adv)で実際のAIに直させたところ、4つとも1回で成功。「直すべきでない対照」は書き換わらなかった。
5. わざと2回失敗させると、人間確認(HR)の報告書ができ、音声作成・解説AI・完成処理・ページ化に進まず(API呼出0)、終了コード2と最終行の警告が出た(Xは正式CLIで確認)。
6. 人間がglossを確定すると再開でき、Xでは該当の音声だけを実際に作成して通過、Zは選定をやり直さず保存結果から再開した(mock context)。
7. X Std・Advで「KP→音声→完成」まで通した(KP音声は新規、それ以外は再利用)。**Family Zの完成まで通すE2Eは実行できなかった**(既存Melos完成runが旧ナレーター様式[N01未適用]で、既存の安全装置が新規音声作成を止めたため。新規作成すると約JPY60以上かかるため実行せず報告)。
8. 追加費用は自然発生分で1記事セットあたり約0.056円(見込み0.014〜0.08円の範囲内、70円目標の約0.08%)。今回のevidence全体の実費は約JPY8.35。
9. 想定外の不具合は見つからなかった(harness側の誤り1件は修正)。ただし未確認事項(Z E7、Zの正式CLIによるHR停止、Adv解説phraseの食い違い等)が残る。
10. 判定は「条件1〜3・5・6(X)・8・10は確認、4・6(Z)は部分確認、7は確認(軽微)、9は本書のコミット・push後」。詳細は§2。

## §1 evidence表 E1〜E10
provenanceの記号: F=fresh(今回新規取得)、R=reuse、S=synthetic(mock・失敗注入・合成入力)、P=production_formal_path(Production正式runner関数・CLIを通過)。全run `TTS_EXECUTION_MODE=STANDARD`明示、Batch不使用、Human Review queue/Lock不使用。

| # | 内容 | provenance | 実行コマンド(逐語は`RESULT_PACKET_KGCPW3.md` (3)) | 観測値 | 期待との一致 |
|---|---|---|---|---|---|
| E1 | X Std(a2) KP段 実LLM | F+P。**自然発生・fresh初回path**(KP選定→canonicalization→redundancy QA→gloss再整合、Coffee実記事) | `er019 ... --level a2 --stage scaffold --scaffold-only kp --budget-jpy 3` | rc=0、204秒、`gloss_alignment_status=ALIGN_PASS`、targets 1/5、attempts 1、`kp_gloss_alignment`タグ1件+scaffold 3件(raw_usage_log)、model_id `gpt-6-luna`、align cost JPY0.0558(in 1840/out 330 token)、align所要3.877秒、rank2 `raw-bean prices`: gloss『焙煎前のコーヒー豆』→『焙煎前のコーヒー豆の価格』(`GLOSS_REALIGNED`、追加語prices↔価格、`mapping_gate=false`=記録のみ)。他4件は`gloss_alignment`無し(書換0)。起動時`[GLOSS-ALIGN] 実効flag=ON (source=default)`、`entry_point.json`/summaryに`gloss_alignment_flag`記録。run総費用JPY1.14 | 一致(期待: 約7%の自然発生を1回目で観測) |
| E2 | X Adv(b1b) KP段 実LLM | F+P(自然) | 同上`--level b1b --budget-jpy 4` | rc=0、164秒、`NO_TARGETS`(targets 0/5、attempts_max 0、API 0)、`kp_gloss_alignment`タグ0、総費用JPY0.84 | 一致(対象無しは仕様どおり何もしない) |
| E3 | Z KP段 実LLM(Std/Adv) | F+P(自然)。`run_e2e_02`のcopy | (a)`--stage kp --regenerate-stage kp_a2` (b)`--regenerate-stage kp_b1b` (c)`--regenerate-stage kp_expl_b1b`、各`--mode real --approved-budget-jpy 8` | (a)rc=0 131秒 a2 `NO_TARGETS`。(b)rc=2 `FamilyZProvenanceMismatchStop: kp_expl_b1b: 親sha不一致`(設計どおり、申し送りの予告と一致)、b1b KP再生成は`NO_TARGETS`。(c)rc=0 8秒、解説1 call。Z cost_log 7件全て`stage=kp`、model_id `gpt-6-luna`、Z総費用JPY1.9855。`gloss_alignment_flag.json`={"enabled":true,"source":"default"}。**Zの実LLM alignは自然発火せず(対象0件)**。b1bのON化前KPは対象0件のため未評価検出は発火しない(設計どおり) | 一致(b rc=2は予告された設計停止) |
| E4 | 合成対象+実LLM align(X a2/b1b、Z a2/b1b) | S(入力はharness固定のselection/canonicalization録画)+F(alignは実LLM)+P。**fresh初回pathとは主張しない** | `harness_kgcpw_01.py --synth-target --level a2|b1b --align-mode real --allow-paid`(X)、`--scenario z_a2|z_b1b --align-mode real --allow-paid`(Z) | 全4件`ALIGN_PASS`・attempts 1・model `gpt-6-luna`。X a2: rank2『～をもとにした』→『インタビューをもとにした』(`GLOSS_REALIGNED`)、rank4対照『簡単にあきらめる』は`GLOSS_ALREADY_CONSISTENT`で**書換0**、cost 0.0295、6.7秒。X b1b: 同結果、cost 0.0493、5.8秒。Z a2: rank2『ふさぐ』→『三人の男が道をふさいだ』cost 0.0472。Z b1b: cost 0.0488。対象外itemはAPI入力に含まれない(targets=[2,4]のみ) | 一致(P1型反映・P2型不変) |
| E5 | 失敗注入(2回失敗→HR→完成禁止) | S(失敗注入、案B'=本物のmake_alignment_fnにfake client)+P。API 0 | harness`--scenario x_a2|x_b1b|z_a2|z_b1b --align-mode fail2`+X正式CLI `--stage tts --only-segments <KP10segment> / --stage assemble / --stage player`(HR状態artifactを入れたrun dir copy) | harness全4件rc=0、`kp_run_status=gloss_alignment_run_status=STOPPED_GLOSS_ALIGNMENT_FAILED`、rank2のみHR・rank4不変。X正式CLI(a2/b1b): tts rc=2「KP gloss Human Review待ち(rank=[2]): KP TTSを実行しません(0 API call)」、assemble rc=2 `EPISODE_BLOCKED_BY_GLOSS_ALIGNMENT`、player rc=2(`player.html`は2.6KBの空殻、音声・assembled無し)、各stdout最終行`[GLOSS-ALIGN][HUMAN-REVIEW-REQUIRED][FINAL] levels={...: [2]} ...ユーザーへ必ず報告してください。`。raw_usage_log=0件(TTS/ASR/解説LLM 0)。B1解説LLM 0 call・assemble拒否はharness `downstream`でも確認 | 一致(X)。Zは§3参照(正式CLIでは別の既存STOPが先に発火) |
| E6 | HR解決後の再開 | S+P(X: TTSは実API) | X: `ga.resolve_gloss(...,2,'インタビューをもとにした',...)`→`--stage tts --only-segments kp2_japanese_meaning`。Z: `z_resume_01.py`(resolve→`run_stage(ctx,"kp")`再実行) | X: `HUMAN_RESOLVED`、TTS 1 clip実行(gemini-3.8-flash-lite-tts+ASR)、cost JPY0.06、rc=0、最終HR行なし(出力に`HUMAN-REVIEW`0件)、`kp2_japanese_meaning=OK`。Z(a2/b1b): `HUMAN_RESOLVED`、`stage_kp=OK`、HR対象levelの選定再実行0、`gloss_alignment_pending_result.json`→`.consumed.json`、deploy済みassetのgloss更新、未解決0、次のtts stage(mock)通過。副次観測: `resolve_gloss`は括弧入りglossを`GlossResolveRejected`で拒否(書込0) | 一致 |
| E7 | E2E完成(KP→TTS→assemble→player) | **X a2: F+P+R**(KP段=E1の自然artifact、KP TTS=fresh/一部reuse、他segment=Coffee copyから再利用)。**X b1b: 合成KP[E4]はTTSのみ(assembleはsource gateが合成KPを拒否)、assembleまで完走は自然KP[E2]で別実施**(b1b_nat)。**Zは未実施** | `--stage tts --only-segments ...`→`--stage assemble`→`--stage player`(`--tts-backend speech_metadata_flash_lite --style-profile coffee_n01_r2_p3_e1`が必要) | X a2: tts rc=0(新規はrank2/4/5、rank1/3は再利用)、assemble `OK`(316.5秒wav、clipping無し)、player rc=0。KP rank2の日本語音声は新gloss『焙煎前のコーヒー豆の価格』、費用JPY0.32。X b1b(合成KP): KP english/explanation/phrase_repeat 15 clip全て`OK`(解説LLM文は新KP対応)、費用JPY2.71(試行錯誤分を含む)、assembleは`KEY_PHRASE_SOURCE_MISSING`(合成KPが実記事に無い=Productionのsource gateが正しく拒否)。X b1b(自然KP、E2のArtifact): tts rc=0、assemble `OK`、player rc=0、費用JPY1.12。Z: 未実施(下記) | X a2・b1b(自然)完走。合成KPのb1b assembleは拒否(期待どおり)。Z E2Eは未確認 |
| E8 | Regression(単独直列) | F。OPENAI_API_KEY=""、委任_02と同条件 | `run_project_regression.py --pattern er003*/er019*/er026*`(`E8_regression/_run_regression_03.sh`) | er003: 1682件 passed 1678/failed 3/errors 1、er019: 421件 passed 420/errors 1、er026: 86件 passed 79/failed 7。**失敗名の集合は3 suiteとも委任_02と完全一致**(`diff`差分0)=新規failure 0(既存p2j 4件・キー無し1件・既存er026 7件)。Production差分0 | 一致 |
| E9 | actual model_id・routing | F | `E9_routing.txt`、raw_usage_log/cost_log/runtime metadata | `require_model("A2_SUPPORT"/"B1_SUPPORT", SUPPORT_MODEL)`=`gpt-6-luna`(両方)。実際のresponse.modelはalign全5 call(E1×1、E4×4)で`gpt-6-luna`(`GlossAlignmentModelMismatchError`が照合)。Productionラインのため最新モデル原則の評価対象外(モデル選定は別判断、最新性の再確認は未実施) | 一致 |
| E10 | 量産費・追加時間 | F | `E9_E10_summary.json` | §4 | 見込み範囲内 |
| (補) | `.env` kill switch(JPY0) | F(観測のみ) | `python -X importtime -c "import er019..."`、`E8_regression/envkill_observe.txt` | X import順: dotenv→`er003_v1_en_direct_vfl_01_generate`(モジュール直下`load_dotenv()`、:39)→`er003_key_words_gloss_alignment`(初回import)。**委任_02の「Xで.envが効かない可能性」推定とは逆で、gloss alignmentのflag評価前に`.env`が読み込まれる順序**。`.env`には当該キーが無く未変更のため実適用は未実測(推定) | 事実として記録 |

### E3/E7でZ E2Eを実行しなかった理由(事実)
- Z `--stage tts_a2`(Melos `run_e2e_02`のcopy)は`FamilyZNarratorStyleMismatchStop`(`LEGACY_NARRATOR_ENTRIES_MISMATCH`、`er063_family_z_audio_01.py:517-541`、期待=N01、記録=旧`PD8+A2_SLOWDOWN_INSTRUCTION`)で**課金前に停止**した(`E5_fail2/cli_z_a2_tts_a2.log`、b1bも同じ)。既存の安全装置であり回避していない。
- 突破には全narrator clipの新規生成が必要=Melos実績JPY62.83級となり、委任のE7上限(JPY30)を超えるため実行せず。見積: Z E7再生成clip数=narrator全clip(約200)×JPY1.0=約JPY200(guard上限)、実単価ベース(X実測0.06〜0.1円/clip)でも約JPY12〜20だがZは別単価で未実測。判断はFable。

## §2 10条件対応表(ユーザー§8)
| # | 条件 | 判定 | 証拠 |
|---|---|---|---|
| 1 | 承認済みcorrected仕様が正式初回Production経路で動作 | **確認済み(X)、部分(Z)** | X Std: E1(自然・fresh、`run_key_phrases`→`align_glosses`→ALIGN_PASS、`kp_gloss_alignment`タグ、`entry_point.json`/summaryにflag/metrics)。X Adv: E2(NO_TARGETS=正常な非発火)+E4 x_b1b(実LLM)。Z: E3(自然は対象0件で非発火のみ)+E4 z_a2/z_b1b(`stage_kp`ではなくharnessのkp_fnがProduction関数`ga.align_glosses`+実`make_alignment_fn`を呼ぶ=P)。**Zの自然発火は未観測** |
| 2 | retry/fallback/regenerationと整合 | **確認済み** | item単位retry: E5(attempt1不正JSON→attempt2 qa FAIL→HR、API fake)。外側retry/fallback/regeneration: E1/E2/E3の`raw_usage_log`/cost_logのscaffold/kp attempt 1〜3は既存外側retry(alignは各1 call)。regeneration: E3(a)(b)(c)の`--regenerate-stage`で`kp_a2`/`kp_b1b`再生成+snapshot優先+`kp_expl_b1b`署名不一致STOP→再生成。E6 Z(snapshot復元・`.consumed.json`)。上限回数・既存安全装置を変更していない |
| 3 | DEV/Trial専用実装ではない | **確認済み** | 実行は全て正式runner/Production関数(E1〜E3、E5 CLI、E6 X CLI、E7)。harnessはevidence配下の新規ファイルでProduction差分0(`git diff --stat`空)。legacy撤去済み(委任_02)。Trial専用定義への依存なし |
| 4 | Family X/Z、Standard/Advancedで必要なruntime evidence | **部分確認** | X Std: E1/E5/E6/E7。X Adv: E2/E4/E5/E7(自然KP完走)。Z Std/Adv: E3(自然NO_TARGETS)/E4/E5(harness)/E6(harness)。**未確認**: Z Std/Adv自然発火、Z正式CLIによるHR停止(狭義は別の既存STOPが先に発火)、Z E2E完成(narrator style guard)、Adv解説phrase(OF-KGCPW-18、ユーザー判断) |
| 5 | 必要テストPASS、既存failureの影響評価 | **確認済み** | E8: er003/er019/er026で失敗名集合が委任_02と一致=新規failure 0(既存: er003 p2j 4件、er019 キー無し1件、er026 7件。撤去前HEADでも同一と委任_02で確認済み)。委任_02で er062 64/64、er063 59/59、er030 37/37、er008 10/10(本委任では未再実行=コード差分0のため) |
| 6 | 失敗時の完成禁止とHuman Review通知 | **X確認済み、Z部分** | X(正式CLI): E5 tts/assemble/player 全rc=2・API 0・EPISODE_BLOCKED_BY_GLOSS_ALIGNMENT・最終行・HR報告書(json+md、再読検証済み、`report_schema_validated=true`、`queue_used=false`/`human_review_lock_used=false`)。Z: harness `FamilyZE2EStop`(stage_kp+tts_a2、mock context)。**Z正式CLIのHR停止は未確認**(既存narrator guardが先)。公開ページ: Xは`player.html`が空殻(音声無し)で、HTMLの解説table生成拒否の直接観測は未実施 |
| 7 | QDC上の重大な悪化なし | **確認済み(軽微な前提つき)** | §4。追加費用 自然発生JPY0.0558/記事セット(見込み0.014〜0.08内)、追加秒 約4〜7秒/level、70円目標の約0.08%、HR 0件(自然)。品質: 書換は不整合1件のみで、対照・対象外は不変 |
| 8 | CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS反映 | **確認済み(本委任)** | `RESULT_PACKET_KGCPW3.md` (9)の差分一覧 |
| 9 | Git反映完了 | **本委任のcommit・push後に確認**(`RESULT_PACKET_KGCPW3.md` (11)) | commit hash |
| 10 | ユーザー承認内容と実際のProduction挙動が一致 | **確認済み** | 承認3件: (1)機械検査=記録のみ→E1/E4 `mapping_gate=false`、`machine_check_record_only`(pass記録のみ)。(2)HR通知先=報告書+run summary event+最終stdout+STOP status、音声HR queue/Lock不使用→E5(`queue_used=false`、`human_review_lock_used=false`)。(3)規則15行型=選定段責務→gloss段は対象外としない設計をSSOT明記(委任_01/02)。corrected唯一化・既定ON=E1〜E3で`flag source=default enabled=true`。**既知の乖離**: 完成禁止の保証はX/Zのみ(A/B/C等は関所なし、ユーザー判断事項)、OPEN-359本体(b)(c)は別承認待ち |

**結論**: 条件4(Z自然発火・Z E2E)・6(Z正式CLI)は未確認が残る。`PRODUCTION_WIRED`判定はFable(委任_04)。

## §3 異常系(E5/E6)詳細
- HR報告書(X、HR状態artifact): `E5_fail2/cli_x_a2_artifacts/a2/key_phrases/`(元: `E5_fail2/x_a2/out/a2/key_phrases/GLOSS_ALIGNMENT_HUMAN_REVIEW_01.{json,md}`)。harness `events[0]`: `reason_code=GLOSS_ALIGNMENT_HUMAN_REVIEW_REQUIRED`、`ranks=[2]`、`report_sha256`、`report_schema_validated=true`、`queue_used=false`、`human_review_lock_used=false`。
- stdout最終行(X正式CLI実出力): `[GLOSS-ALIGN][HUMAN-REVIEW-REQUIRED][FINAL] levels={'a2': [2]} events=1 reports=['...E5_cli_x_a2\\a2\\key_phrases\\GLOSS_ALIGNMENT_HUMAN_REVIEW_01.md'] gloss再整合が成立せず対象levelのKP segment/完成を停止中です。ユーザーへ必ず報告してください。`(b1b同様 `levels={'b1b': [2]}`)。tts stage途中表示: `[FAMILY-X-AUDIO][STOP] KP gloss Human Review待ち(rank=[2]): KP TTSを実行しません(0 API call)。`
- rc: X tts/assemble/player全て2。Z: harness mock contextは`FamilyZE2EStop`(`FAMILY_Z_KP_GLOSS_ALIGNMENT_HUMAN_REVIEW_REQUIRED(a2): rank=[2] ... (TTS/Gate/Assemblyへ進まない)`)。
- 解説LLM: harness `x_downstream_checks`で`expl_llm=0`、TTS=0。assemble level単位拒否(a2/b1b別)。
- resolve後の再開: §1 E6。Z: `.consumed.json`改名、HR対象levelの`kp_fn`再実行0回、他level初回選定は正当(a/b scenarioで観測)。`resolve_gloss`が括弧入りglossを拒否(`E6_resume/resolve_rejects_parentheses.json`)。
- **副次事象(事実・不具合ではない)**: Z実CLIの`--stage gate/assemble/pages`を同一run dirに短時間で連続起動すると`FAMILY_Z_RESTART_STORM`(300秒に3回起動)でrun dirに`STOP`が自動作成された(`run_kgcpw_z_e5_a2_01`/`..._b1b_01`、いずれもAPI 0のevidence用copy dir)。STOPは削除・回避していない(解除は`--clear-stop --reason`でFable/ユーザーのみ)。**以後これらのdirは使わない**。

## §4 QDC
- align call単価(実測): 自然E1 JPY0.0558(1 target)、合成E4 0.0295/0.0493/0.0472/0.0488(平均0.0437)。VALIDATION_03の0.114/call(平均)より低い(in 1.4〜1.8k/out 0.2〜0.3k token)。
- 1記事セット(Std+Adv)の追加費用: 自然E1(Std 0.0558)+E2(Adv 0)=**JPY0.0558** vs Trial見込み0.014〜0.08(範囲内)。70円目標に対し約0.08%(最悪見込み0.57でも0.8%)。
- 追加時間: align段 3.9〜6.7秒/level(見込み15〜50秒より小さい)。KP段全体は204秒(Std)/164秒(Adv、align無し)。
- HR 0件(自然)。監視指標の初期値(E1): targets=1/5(20%、基準7%は記事単位・サンプル1のため判断不可)、attempts_max=1、cost 0.0558(0.6円の閾値未満)、DISABLED 0、align所要3.877秒(閾値60秒未満)。
- 今回evidence総費用: JPY8.35(E1 1.14/E2 0.84/E3 1.99/E4 0.17/E6 0.06/E7 4.15、E5・E8は0)。Guardrail JPY60に対し13.9%、当日累計は約JPY15.4(日次1,000円内)。
- TTS実単価(参考): 1 clip(gemini-3.8-flash-lite-tts+ASR)=約0.06円。`E2E_TTS_CLIP_EST_JPY=1.0`はguard見積で実費の約16倍の保守値。

## §5 mock・失敗注入・実LLMの区別
| 区分 | 該当 |
|---|---|
| 実LLM+Production正式runner(自然) | E1(ALIGN_PASS)、E2(NO_TARGETS)、E3(Z、NO_TARGETS) |
| 実LLM align+合成入力(selection/canonicalization録画固定) | E4(X a2/b1b、Z a2/b1b)。Zはharnessのkp_fnがProduction `ga.align_glosses`+実`make_alignment_fn`を呼ぶ(stage_kp自体は`mock` context) |
| 失敗注入(fake client、API 0) | E5 harness(X/Z全4)、E5 X正式CLI(HR状態artifactを手で配置したcopy dir)、E5 Z(HR状態を注入したcopy。narrator guardに阻まれた) |
| mock context | Z E4/E5/E6のstage関数駆動(`build_mock_context`)。TTSはmock |
| 実TTS(Production正式CLI) | E6 X(1 clip)、E7 X(a2 10、b1b合成15+自然15程度、費用は§4) |
| 再利用 | E7のX non-KP segment(Coffee copyから`REUSED_VALIDATED`継承/b1b preview・commentはcopyでの継承不成立のため再生成=§6参照)、E3のZ b1b KP(1回目) |

## §6 残存リスク(Opus §6の6項目の現状)と不具合・想定外
1. **harness側の誤り(修正済み)**: `run_z`のreal時に`model="synthetic-model"`固定で404(API課金0)→real時のみ`require_model`の実モデルとrank2のgloss『ふさぐ』に修正(`harness_kgcpw_01.py`の`_z_gloss`/`_z_model`、fail2経路は不変、`--self-test`は修正後もPASS)。旧結果は`E4_synth/attempt0_z_a2_harness_model_bug/`。
2. **E7 X b1b copyの前提不整合(Production不具合ではない)**: Coffee完成b1b copyのpreviewキャッシュは旧style(E1非前置)で、`--only-segments`では継承に失敗し`BLOCKED_STYLE_PROFILE_GATE`(preview)→`UNVALIDATED`(comment_1-4)→合成KP時`KEY_PHRASE_SOURCE_MISSING`と段階的に既存関所が正しく拒否。preview+comment_1-4を`--only-segments`に含めて(preview.wavを退避して)再生成することで自然KPのAdv assembleは完走した。Gateは回避していない。
3. **Adv解説phrase(OF-KGCPW-18)**: `er019_family_x_kp_explanation_01.py:152-155`/`er026:1285-1287`は解説LLM入力のphraseがdisplay_phrase基準でglossは参考=既存構造。今回のE7 b1b(合成)では解説文が『based on interviews』に対し『using something as the main support for an idea or decision』となりdisplay_phrase『based on』基準と整合した可能性があるが、gloss(インタビューをもとにした)との食い違いの有無は評価していない。ユーザー判断。
4. **Zの自然発火は未観測**。E3 Z(a2/b1b)は対象0件。
5. **OPEN-359本体(b)(c)**: gloss HRは迂回されないことをtestで固定(`er003_test_kp_gloss_alignment_wiring.py`、E8でPASS)。冗長/記号NGのKPがXで完成へ進む疑いは未解決(別承認)。
6. Z正式CLIのgloss HR停止は、既存narrator-style guard(N01未適用の旧run)に先を越され直接観測できず(harness `stage_kp`/`tts_a2`のFamilyZE2EStopで代替)。
7. 再生成後にTTSを飛ばしてassembleすると旧音声で通過する可能性(OF-KGCPW-19前者)は未検証・OPEN候補。
- E7 b1b(合成)の費用JPY2.71は、Coffee copy起因の前述の再試行(同dirで4回のTTS起動)の累積。いずれも原因説明済みの関所拒否であり暴走ではない。

## §7 確認できなかった事項
- 事実として未確認: Z Std/Adv自然発火、Z E2E完成(KP→TTS→gate→assemble→pages→page_verify)、Z正式CLIのHR停止、Adv解説phraseとglossの食い違い頻度、`.env`経由kill switchの実適用、X解説cache署名・未評価検出の実走(testのみ)、`--level both`でのa2 HR時b1b assemble巻き添え、Xの公開ページtable省略の直接観測。
- 推定: `.env`のkill switchはXで効く順序(import順観測+vfl01:39)。Z実単価(narrator全再生成の見積)。

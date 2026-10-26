## 管理ID

PM-SSOT-SYNC-05(CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 Closeout: Fable判定PRODUCTION_WIRED(X/Y/Z Std/Adv 6行)のSSOT反映。CURRENT_SPEC Chunk節是正を含む。API 0・JPY0)。並行タスク衝突確認: 並行Agent 4件(TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01 委任_01X/01Y/01Z[`docs/research/TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01/`・delegation_log]、KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01 委任_01[`er124_*`・`docs/research/KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01/`])。いずれもSSOT編集権なし。**SSOT編集権は本Agentのみ**(`CURRENT_SPEC.md`/`OPEN_ITEMS.md`/`DECISION_LOG.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/USER_DECISION_REGISTER_01.md`/`docs/pm/OPUS_FINDINGS_LEDGER.md`/`docs/pm/ACTIVE_TASK.md`)。これ以外は編集しない。git index.lock競合時は10秒待って再実行(最大3回)。

## 性質/到達上限Status/禁止事項

- 性質: SSOT転記(Closeout記録)。到達上限Status: 転記完了。転記内容のStatusはFable判定どおり(格上げ・格下げ禁止)。
- 禁止: Production/コード/Prompt変更、API支出、`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。
- **前委任(PM-SSOT-SYNC-04)の報告事実**: 作業ツリーのSSOT 5ファイル(`OPEN_ITEMS.md`/`DECISION_LOG.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/USER_DECISION_REGISTER_01.md`/`docs/pm/OPUS_FINDINGS_LEDGER.md`)はHEADより古い内容で、SYNC-04はindexだけでcommitしworktreeを触っていない。本委任では各SSOTファイルについて(1)`git diff HEAD --stat -- <path>`と`git diff HEAD -- <path> | Select-String "^\+" | Select-String -NotMatch "^\+\+\+"`で**worktree側にしかない追加行**があるか確認、(2)追加行が無い(=worktreeがHEADの旧版/CRLF差分のみ)なら、`git show HEAD:<path>`の内容をそのpathへ書き戻してworktreeをHEADと一致させたうえで自分の追記を加える(これはファイル書込みであり禁止git操作ではない)、(3)worktree側にしかない追加行がある場合はその内容を`RESULT_PACKET_SSOT5.md`に記録し、HEAD blob+自hunk方式(scratchpad経由)でcommitし、worktreeは触らない。`CURRENT_SPEC.md`も同じ手順。
- 費用/日次: JPY0。
- Opus独立技術レビューGate(11-3): 非該当(転記のみ。条件A相当のOpusレビューは`OPUS_REVIEW_01.md`で実施済み・M/R全採用)。
- 時間見込み: 約45分。並列化: なし(SSOT直列ルール8-Y)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし)
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。

T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_PM-SSOT-SYNC-05_DELEGATION_01.md` をN=654から順に試し、先頭が「## 管理ID」+「PM-SSOT-SYNC-05」で始まるものを採用(`--index -1`不可。直前に別委任3件が送られているため先頭一致を必ず確認)。

## ユーザー指示(原文)

該当なし(Fable判定の転記。ユーザー承認原文=`docs/pm/delegation_log/2026-10-26_CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01_USER.md`。転記文中で引用する承認文「Standardを除外することは認めない」「ユーザーへの再確認を求めず是正すること」「コード配線済み・テストPASSだけで…runtime evidenceを取得済みと扱わないこと」「Yは複数段落入力で発火検証・実記事不発火は記録」はこのファイルからGrepで原文を確認し、逐語で引用する)。

## Fable判定(転記する内容。文言はこのまま使う)

**CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 = PRODUCTION_WIRED(2026-10-26、Fable判定。承認=ユーザー APPROVED_FOR_PRODUCTION[Chunk分割のStd拡張、X/Y/Z Std/Adv])**

| Family/レベル | 判定 | 根拠(正式runtime evidence) |
|---|---|---|
| X Std | PRODUCTION_WIRED | 正式CLI実run `er019_output/family_x_audio_production_wiring_01/uk_train_speaker_playback__run_stdchunk_ev_01`: 10 chunk(語数[66,14,31,34]/[56,49,42]/[35,52,36]、全て段落境界)、chunk別6%減速比1.0568〜1.0600、0.2秒無音=4800サンプル整数一致(3/3)、組立後gap 7箇所0.200秒、再起動で新規API 0回、style_profile_gate/共有Gate PASS、組立321.9秒。実費6.20円。`EVIDENCE_01.md` |
| X Adv | PRODUCTION_WIRED(維持) | 旧(bb578265c)新で results/narration wav/chunk plan/gain/timeline/合成wavバイト一致。既存evidence `FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01/RUNTIME_EVIDENCE_01.md` |
| Y Std | PRODUCTION_WIRED(配線済み。**現行本文契約では正式経路で構造的に不発火**) | 複数段落dev入力(`y_voice_2`文境界3段落化)で正式生成関数・Gate・組立をrunner同条件(STOP確認・RUN_LOCK・予算guard・cost logger・STANDARD・only_segments)で直接呼出: 3 chunk[54,67,36]、減速比1.0585〜1.0595、gap 0.200秒、Gate PASS。実費1.77円。実記事run_01は全8 segment `chunked:false, paragraphs:1`(API 0)。正式CLIは`write_level_inputs`で本文を記事から再生成し、記事契約(段落5固定・Voice本文1行)により本文内空行は`Y_ARTICLE_PARAGRAPH_COUNT`違反STOP(実演済み)。`EVIDENCE_01.md` §3 |
| Y Adv | PRODUCTION_WIRED(同上) | 同条件3 chunk[55,63,37]、gap 0.200秒、Gate PASS。実費1.50円 |
| Z Std | PRODUCTION_WIRED | 正式run `er026_output/family_z_production_e2e_01/melos/run_stdchunk_ev_01`: narrator 134語→2 chunk(76/58語、段落境界)、減速比1.0597/1.0592、0.2秒=4800サンプル全0、厳格Gate(chunk id: slowdown_applied+比率[1.03,1.09])PASS、共有Audio Validation Gate PASS、speed profile 24 clip PASS、dialogue TTS 0回、再起動で新規API 0回(chunk再利用)。実費1.67円。`EVIDENCE_Z_01.md` |
| Z Adv | PRODUCTION_WIRED(維持) | 2 run(melos e1_01 b1b、tell_tale run_chunk_01 b1b)のplan/chunk plan/親display/meta/reuse_keyが実装前HEAD goldenとバイト一致 |

- 合成方式(確定): chunkごとTTS→6%減速(Stdのみ)→減速後ASR再検証→減速後に4800サンプル(0.2秒)無音→連結。連結後減速は不採用(ゼロ連続長4569で0.2秒が崩れるため)。B_r1=100語超でk=ceil(語数/100)・等分割・最小25語・段落境界優先(「約70語目安」はこの結果)。`CHUNK_PLANNER_VERSION`不変。
- Opus指摘(OPUS_REVIEW_01.md、条件A): M1(旧方式Std結果への本文以外`--only-segments`で本文喪失)・R1〜R5=実装済みd00f41c8b/evidence c00a20ed9。M2(Z速度Gate `_CLIP_ID_RE`2箇所fail-open→`_CLIP_OR_CHUNK_ID_RE`+厳格検査)・M3(レベル条件2箇所同時撤去・`attach_chunk_meta(level=)`・a2のみ親集約・`drop_cached_std_chunks_without_slowdown`をload_results直後)・R6(Zセリフ経路不変test)・R7(Local Rewrite経由も減速+厳格Gate)=実装済み3fc684c37/evidence e16e67f60。
- test: 新規 er117 17+er019 18+17+er121 14+7+er063 15=約88件、回帰 er117 106/er019 595/er121 297+1skip/er063 130/er026 222(2 skip)/er122 69 全PASS。
- 実費合計11.15円(X 6.20+Y 3.27+Z 1.67、Cap 100+60)。
- 運用逸脱(記録): (1)R4 driver初版で遮断前に実LLM呼出し1回0.0084円、(2)X Std 1回目課金前STOP後26秒で再起動(150秒規律違反、課金0)。
- 残件(任意・非blocking、Fable判断=必須ではない): Z Stdの2作品目実run、強制NG/Local Rewrite/exhaust経路のZ Std実run(offline testで固定済み・Gateはfail-closed)。既存非冪等test `er063_family_z_audio_01_test_01.py::WiringTest::test_preview_comment_kp_styles`(repo root `x/`にReview Lock残置、HEAD既存、実害なし)。
- Std除外の出所(是正済み事実として記録): FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01 Phase 0でのFable/Sonnet設計判断(Trial指示「Advancedのみ」、配線指示「未承認の対象拡大を行わない」、Z最終版「Standardは承認済み仕様どおり維持する」を根拠にStdを対象外とした)。ユーザー承認なしの限定であり、2026-10-26ユーザー正式指示で是正。再発防止=対象レベル限定はユーザー承認必須(DECISION_LOGに明記)。
- OPEN-527(Y分割方式)との関係: YのChunkは配線済みだが現行契約では休眠。Y本文契約の変更(文境界分割/複数段落化/現状維持)はOPEN-527でユーザー判断待ちのまま。

## KPI provenance欄

該当なし(転記。数値出典=`docs/pm/RESULT_PACKET_CHKW2.md`・`RESULT_PACKET_CHKW3.md`・`docs/research/CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01/{EVIDENCE_01,EVIDENCE_Z_01,COST_01,COST_Z_01}.md`)。

## Opus台帳更新

`docs/pm/OPUS_FINDINGS_LEDGER.md`: Grep `OF-CHKW` → M1,R1〜R5=CLOSEOUT_CONFIRMED(PRODUCTION_WIRED判定2026-10-26)、M2,M3,R6,R7=FABLE_DECIDED→IMPLEMENTED→EVIDENCED→CLOSEOUT_CONFIRMED(3fc684c37/e16e67f60)。

## 事前指定Read一覧

- `docs/pm/RESULT_PACKET_CHKW2.md`: (9)SSOT文案の節のみ(Grep `^\(9\)|SSOT文案` → ±30)
- `docs/pm/RESULT_PACKET_CHKW3.md`: Grep `SSOT文案|\(6\)` → ±20
- `docs/pm/RESULT_PACKET_SSOT4.md` 全文(前委任の更新箇所・worktree状態の記録)
- `docs/pm/ACTIVE_TASK.md` 全文
- `docs/pm/delegation_log/2026-10-26_CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01_USER.md`: Grep `Standardを除外|再確認を求めず|runtime evidence|複数段落|再発防止|対象レベル` → ±3(逐語引用用)

## 事前指定Grep一覧+追記位置・更新位置の手順

- `CURRENT_SPEC.md`: Grep `Chunk|chunk|段落境界|B_r1|0\.2秒|CHUNK_PLANNER` → Chunk TTS節(X方式/Z方式の既存記述)を特定。既存記述のうち「Advancedのみ」「Standardは対象外」等の限定表現を**是正**(履歴として「(旧: Advanced限定=2026-10-26是正)」の形で残し、削除しない)。同節に上記6行表の要約(Std/Adv両対象、合成方式、Y構造的不発火、Z Std厳格Gate、Status=PRODUCTION_WIRED 2026-10-26、evidence path)を追記。Chunk節が無ければFamily X/Z音声節の末尾に「Chunk TTS(X/Y/Z Std/Adv)」小節を新設。Family Y節にも1行(配線済み・現行契約では不発火・OPEN-527参照)。
- `OPEN_ITEMS.md`: Grep `OPEN-532` → Status=PRODUCTION_WIRED(2026-10-26)へ更新、残件(任意)を記載。Grep `OPEN-527` → 「Chunk配線済みだが現行契約で休眠」の1文が前委任で追記済みか確認(重複追記しない)。
- `DECISION_LOG.md`: Grep `2026-10-26` 本日エントリ末尾 → 1件追記(PRODUCTION_WIRED判定6行の要約・合成方式確定・Opus M/R全採用・Std除外の出所と再発防止・実費・逸脱)。
- `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `OPEN-532` → 「PRODUCTION_WIRED報告済み。ユーザー判断不要(承認済み範囲)」へ更新。
- `docs/pm/REPORT_LEDGER.md`: CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01=Fable報告済み(2026-10-26、PRODUCTION_WIRED 6行表)、TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01=受領・委任_01X/Y/Z開始、PM-SSOT-SYNC-05=本件。
- `docs/pm/ACTIVE_TASK.md`: 上書き(並行=TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01 委任_01X/Y/Z(JPY0)+KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01 委任_01(Cap80)、UDR-blocking=OPEN-526・527・529(区分2)・531(Puck推奨)、OPEN-532=PRODUCTION_WIRED完了、STOP条件=猿の手run_fzcw_e1_01残置のまま、QDC=当日約510円+KP Trial Cap80/1,000)。

## 実行コマンド全文

- worktree状態確認(各SSOTファイル): `git diff HEAD --stat -- CURRENT_SPEC.md OPEN_ITEMS.md DECISION_LOG.md docs/pm/REPORT_LEDGER.md docs/pm/USER_DECISION_REGISTER_01.md docs/pm/OPUS_FINDINGS_LEDGER.md`
- HEAD blob取得例: `git show HEAD:CURRENT_SPEC.md > C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\scratchpad\CURRENT_SPEC.head.md`
- stage確認: `git diff --cached --stat`(自分の追記行数のみであること)
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件
- commit存在確認: `git log --oneline -1 3fc684c37`、`git log --oneline -1 e16e67f60`、`git branch -r --contains e16e67f60`

## SSOT追記文

上記「Fable判定」の文言をそのまま使う。

## Git(明示add対象・コミットメッセージ・trailer)

- add対象: `CURRENT_SPEC.md`、`OPEN_ITEMS.md`、`DECISION_LOG.md`、`docs/pm/USER_DECISION_REGISTER_01.md`、`docs/pm/REPORT_LEDGER.md`、`docs/pm/OPUS_FINDINGS_LEDGER.md`、`docs/pm/delegation_log/2026-10-26_PM-SSOT-SYNC-05_DELEGATION_01.md`(+`_check.json`)。`docs/pm/ACTIVE_TASK.md`・`RESULT_PACKET_*`はgitignored(addしない)。
- commit message: `PM-SSOT-SYNC-05: Chunk分割 X/Y/Z Std拡張 Fable判定PRODUCTION_WIRED(6行、CURRENT_SPEC Chunk節是正[Advanced限定表記の是正・合成方式確定・Y構造的不発火]、OPEN-532、DECISION_LOG、Opus台帳OF-CHKW CLOSEOUT、UDR、報告台帳、API 0)`
- trailer: `Delegation: PM-SSOT-SYNC-05/01`
- push: `git push origin HEAD:main`(non-ffなら`git fetch origin`→`git merge --no-edit origin/main`→push。競合はSTOPし報告)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_SSOT5.md`: (0)T-0結果、(1)各SSOTのworktree状態(HEAD差分の有無・worktree固有追加行の有無・取った方式[書き戻し/HEAD blob+hunk])、(2)更新したSSOT行(ファイル:行、CURRENT_SPECは是正前後の文を引用)、(3)`git diff --cached --stat`、(4)commit hash・push結果・raw URL(CURRENT_SPEC.md/OPEN_ITEMS.md/DECISION_LOG.md)、(5)RESULT_PACKET必須4行+「判定整合: 重大NG=<なし|あり>」1行、(6)一覧外Read。末尾に10行以内の要約。
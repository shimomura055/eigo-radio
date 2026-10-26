## 管理ID

PM-SSOT-SYNC-12(KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01 Closeout: Fable判定PRODUCTION_WIRED(X/Y/Z Std/Adv)のSSOT反映。CURRENT_SPEC新節を含む。API 0・JPY0)。並行タスク衝突確認: 並行Agent 1件(TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_01[設計・read-only、SSOT編集権なし])。**SSOT編集権は本Agentのみ**(`CURRENT_SPEC.md`/`OPEN_ITEMS.md`/`DECISION_LOG.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/USER_DECISION_REGISTER_01.md`/`docs/pm/OPUS_FINDINGS_LEDGER.md`/`docs/pm/ACTIVE_TASK.md`)。pathspec付きcommit。git index.lock競合時は10秒待って再実行(最大3回)。

## 性質/到達上限Status/禁止事項

- 性質: SSOT転記。到達上限Status: 転記完了。
- 禁止: Production/コード変更、API支出、`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。編集前に`git diff HEAD --stat -- <path>`で差分なしを確認(差分があればHEAD blob+自hunk方式)。CURRENT_SPECはCRLF保持。
- 費用/日次: JPY0。
- Opus独立技術レビューGate(11-3): 非該当(転記。条件Aレビューは実施済み=OPUS_REVIEW_03)。
- 時間見込み: 約40分。並列化: なし。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし)
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。

T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_PM-SSOT-SYNC-12_DELEGATION_01.md` をN=670から順に試し、先頭が「## 管理ID」+「PM-SSOT-SYNC-12」で始まるものを採用(`--index -1`不可)。

## ユーザー指示(原文)

`docs/pm/delegation_log/2026-10-26_KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01_USER.md` §2採用表・§3検証要件(Grep `APPROVED_FOR_PRODUCTION|時制・活用形|慣用句|5語以下|本文にない語|分解救済|実装条件4件|27件の固定例外|Humanが明示的にNG` で逐語引用)。

## Fable判定(転記する内容。文言はこのまま使う)

**KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01 = PRODUCTION_WIRED(2026-10-26、Fable判定。X/Y/Z Std/Adv。ユーザー承認=APPROVED_FOR_PRODUCTION 2026-10-26)**
- 採用表の実装: 時制・活用形=revert(表層形維持)+M1窓内再導出(display語/LLM提案語のみ、例`rose above→rise above`・`held out→hold out`)+D1再アンカー(例`catch their interest`→本文`catches their interest`→正規canonicalization)。慣用句=一般機構(Wiktionary English idioms見出し10,674件のvendoring辞書[CC BY-SA 4.0、`data/kp_idiom_lexicon_01/`、sha二重ピン、不一致/欠落はfail-closed=救済なし]+構造条件[助動詞始まり・be系除外・倒置疑問文/名詞主語完全文/中身語なし断片除外・主語`it`のみ除去]+denylist 14件。27件固定表は不使用)。5語以下=維持(**短縮救済は不採用**=Fable解釈「6語以上を意味のない短縮で救済しない」を保守側に適用、Opus確認済み。`too soon to wave a flag`は除外のまま)。本文にない語の追加=不採用。CMU分解救済=不採用。既存仕様違反4件=全件是正(副詞前原形化・動詞have役割判定・過去形表補完=845cfcb0a、量化詞限定詞guard=6133aa6d6)。Human NG=救済経路でも復活不可(元句・救済後句の両方を照合)。
- 配線(既定ON、kill switch `EIGO_KP_RESCUE=0`のみOFF、読取1関数): H1 `er105:961-979`(有限助動詞guardの慣用句例外)、H2 `er105:245-267`(選定段救済、救済後句の重複再照合=Opus M1)、H3 `er003_v1_n3_01_scaffold_generate.py:475-567`(canonicalization段)、H4 `er119_kp_candidates_01.py`/`er119_kp_human_review_01.py`(候補ファイル永続化・`RESCUED`旗・`candidates_sha256`包含・doc単位`rescue_provenance`)。発火は`generate_candidates`実行中のみ(contextvar=Opus M2。旧経路`er062:1364`/`er121`旧kp_fn/他`run_selection_gate`呼出元は不発火、A/B/C golden 1002件BYTE_IDENTICAL)。HRあり=`RESCUED`旗+元句+理由コードで人間が選択。HRなし=gloss強制再整合成功かつQA 12項目再判定PASSのときのみ`auto_eligible`(revertは再判定keyがほぼ不一致=HR限定になる見込み、実測0/1)。外側retry=`n_auto<3 and (gate_dropped or 救済済みauto不可あり)`(Opus M3)、auto不可の救済候補はF1累積除外に入れない。resume=再計算せず読み戻し、provenance差はlogのみ。既存run `run_ai_01`のHR候補不変(resume統合test)。
- test: er125 58、er105 52(rule_compliance改訂=旧規則撤去を明記)、新規`er119_kp_rescue_wiring_test_01.py` 15、er119 146/148(HEAD既存失敗2)、er003 1910、er123 154、敵対的85件PASS、実データ351対で合格348に救済変化0、量化詞parity不一致0。接続試行0。
- runtime evidence(fresh、正式runner KP stage限定、新規run dir、TTS/本文生成なし): X `uk_train_speaker_playback__run_kprescue_ev_01`(a2 7/7・b1b 6/6、自然発火なし)、Y `redelivery_fee/run_kprescue_ev_01`(a2 5/5[`redelivery fee`はCMU除外・分解救済せず]、b1b 8/7、**自然発火2件**=`it can’t be helped→can’t be helped`[慣用句の核]・`takes steps`[revert、QA key不一致でHR限定])、Z `melos/run_kprescue_ev_01`(a2 7/6・b1b 6/6、自然発火なし、SRC D1全PASS)。同引数再起動でsha不変・API 0。actual model_id=gpt-6-luna全call、Prompt 2/2-V sha一致、canonicalization prompt/schema無変更。replay(正式`generate_candidates`経由、選定・canonicalization 1回目はfixture、gloss/QAは実LLM)=X(`studied separately`通常通過/`too soon to wave a flag`非救済)、Y(`it can’t be helped`核へ/`catch their interest`→`catches their interest`/`redelivery fee`非救済)、Z(`rose above→rise above`/`held out→hold out`、gloss REALIGNED・QA PASS)。R3 key一致率: M1 2/2、revert 0/1。
- Family別判定: **Y=PRODUCTION_WIRED(自然発火の実走あり)**、**X=PRODUCTION_WIRED**・**Z=PRODUCTION_WIRED**(fresh runでは救済対象の候補が出現せず自然発火0=経路到達と正式関数経由replay[実LLM gloss/QA]で確認。次の自然発火をOPENで記録=非blocking)。
- 費用: 実費約11.2円(fresh X 3.26/Y 3.25/Z 2.95、replay 1.71)。単価影響=救済発火時のみ+約0.2〜0.8円/記事セット、非発火時0。
- 運用逸脱(記録): Z初回起動がY初回起動の101秒後(別run dir・別Family、STOPなし)。
- 新規OPEN(11-8分類): (a)縮約形の非対称(ASCII `can't`主語付き受理/curly `can’t`のみ核へ救済)=修正へ進む(影響測定後にguard是正)、(b)`a can of beans`型(名詞canが`aux_start`で通る既存guard)=修正へ進む・低、(c)HEAD既存test失敗4件(er119 2・er108 Importers・er019 R4 hunk classifier)=実害なし・test整備、(d)X/Zの救済自然発火の初回記録=追跡(非blocking)。
- Fable判断(B、承認範囲内・未実施): revertではQA再判定callを省く案(節約約0.16円/件)=次回KP関連変更時に合わせて判断。
- Opus台帳: OF-KPRW-M1〜M4/R1〜R7=RAISED→FABLE_DECIDED→IMPLEMENTED(2910e859b)→EVIDENCED(d2269a26b)→CLOSEOUT_CONFIRMED。OF-KPRS-M1〜M6/R1〜R4・OF-KPRS2系=CLOSEOUT_CONFIRMED(PRODUCTION_WIRED 2026-10-26)。
- commit: 6133aa6d6、1701dfc4d、2910e859b、d2269a26b。

## KPI provenance欄

該当なし(転記。出典=`docs/pm/RESULT_PACKET_KPRW1.md`・`RESULT_PACKET_KPRW2.md`、`docs/research/KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01/{EVIDENCE_01,WIRING_01,FIX_01,SPEC_LEDGER_02,COST_01,OPUS_REVIEW_03}.md`)。

## Opus台帳更新

`docs/pm/OPUS_FINDINGS_LEDGER.md`: Grep `OF-KPRS|OF-KPRW` → 既存OF-KPRS行をCLOSEOUT_CONFIRMEDへ、OF-KPRW-M1〜M4/R1〜R7の新規11行を追加(各1行: ID・指摘要旨・遷移・commit・根拠path)。

## 事前指定Read一覧

- `docs/pm/RESULT_PACKET_KPRW2.md`: Grep `^\(9\)|SSOT文案|OPEN案|^\*\*8` → ±40(SSOT文案・OPEN案・Opus台帳文案)
- `docs/pm/RESULT_PACKET_KPRW1.md`: Grep `^\(9\)|CURRENT_SPEC新節` → ±30
- `docs/pm/ACTIVE_TASK.md` 全文
- `CURRENT_SPEC.md`: Grep `Key Phrase候補|先頭またはto直後|2015|OPEN-530|KP_CANDIDATE_MAX` → 該当行±8(新節の挿入位置=KP候補仕様の節末尾)
- `docs/pm/OPUS_FINDINGS_LEDGER.md`: Grep `OF-KPRS` → 既存行の書式

## 事前指定Grep一覧+追記位置・更新位置の手順

- `CURRENT_SPEC.md`: KP候補仕様の節末尾に新節「Key Phrase Gate除外救済方式(2026-10-26 APPROVED_FOR_PRODUCTION→PRODUCTION_WIRED)」を追加(上記Fable判定の採用表・配線・HRあり/なし・resume/retry・kill switch・evidence・費用・不採用事項・Fable解釈)。既存の「CMU代替合格禁止」「Human NG復活禁止」「最大8」行は維持。
- `OPEN_ITEMS.md`: Grep `OPEN-529` → Status=PRODUCTION_WIRED(CLOSED)。Grep `OPEN-530` → 文書是正済み・関連CLOSE可否を記載(是正済みならCLOSED)。Grep `OPEN-152` → 「fulltext経路の救済はOPEN-529で配線。A/B/C共有validator問題は別」と1文追記。Grep `OPEN-526` → 「救済方式がPRODUCTION_WIRED。AI島run_ai_01の既存候補は不変(新runから適用)」追記。Grep `^\| OPEN-5[34][0-9]` → 最大番号(OPEN-540まで)→ 新規OPEN-541(縮約形非対称)、OPEN-542(`a can of beans`型)、OPEN-543(HEAD既存test失敗4件)、OPEN-544(X/Z自然発火の初回記録・追跡)。
- `DECISION_LOG.md`: 本日末尾に1件。
- `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `OPEN-529` → 「区分2はユーザー採用(2026-10-26)→PRODUCTION_WIRED反映済み」。
- `docs/pm/REPORT_LEDGER.md`: KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01=Fable報告予定(A/B分離報告)、本件。
- `docs/pm/ACTIVE_TASK.md`: 上書き(並行=TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_01(JPY0)→Opus→委任_02、UDR-blocking=OPEN-526・527・534・537・539(試聴)、STOP条件=猿の手run_fzcw_e1_01残置、QDC=当日約563円/1,000)。

## 実行コマンド全文

- `git diff HEAD --stat -- CURRENT_SPEC.md OPEN_ITEMS.md DECISION_LOG.md docs/pm/REPORT_LEDGER.md docs/pm/USER_DECISION_REGISTER_01.md docs/pm/OPUS_FINDINGS_LEDGER.md`(編集前)
- `git diff --cached --stat`
- Secret grep: `git diff --cached -- CURRENT_SPEC.md OPEN_ITEMS.md DECISION_LOG.md docs/pm/REPORT_LEDGER.md docs/pm/USER_DECISION_REGISTER_01.md docs/pm/OPUS_FINDINGS_LEDGER.md | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

上記Fable判定の文言+RESULT_PACKET_KPRW1/2の文案を使う。

## Git(明示add対象・コミットメッセージ・trailer)

- add対象: `CURRENT_SPEC.md`、`OPEN_ITEMS.md`、`DECISION_LOG.md`、`docs/pm/USER_DECISION_REGISTER_01.md`、`docs/pm/REPORT_LEDGER.md`、`docs/pm/OPUS_FINDINGS_LEDGER.md`、`docs/pm/delegation_log/2026-10-26_PM-SSOT-SYNC-12_DELEGATION_01.md`(+`_check.json`)。pathspec付きcommit。
- commit message: `PM-SSOT-SYNC-12: KP Gate除外救済方式 Fable判定PRODUCTION_WIRED(X/Y/Z Std/Adv、CURRENT_SPEC新節、OPEN-529 CLOSED、OPEN-541〜544起票、Opus台帳OF-KPRW/OF-KPRS CLOSEOUT、UDR、API 0)`
- trailer: `Delegation: PM-SSOT-SYNC-12/01`
- push: `git push origin HEAD:main`(non-ffなら`git fetch origin`→`git merge --no-edit origin/main`→push。競合はSTOPし報告)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_SSOT12.md`: (0)T-0、(1)編集前状態、(2)更新行(CURRENT_SPEC新節は見出しと行範囲)、(3)`git diff --cached --stat`、(4)commit hash・push・raw URL(CURRENT_SPEC.md/OPEN_ITEMS.md/DECISION_LOG.md)、(5)必須4行+「判定整合: 重大NG=<なし|あり>」、(6)一覧外Read。末尾に要約5行以内。
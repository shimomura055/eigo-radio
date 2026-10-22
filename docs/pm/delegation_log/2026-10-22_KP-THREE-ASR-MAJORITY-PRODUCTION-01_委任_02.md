FABLE-DELEGATION-MARKER: KP3V-IMPL-委任_02-20261022

# 委任(KP-THREE-ASR-MAJORITY-PRODUCTION-01 委任_02: Opus条件Aレビュー(OF-KP3V-P-01〜12)の必須項目を設計・moduleへ反映→保存音声を本番adapter経路で再評価(0円)→**PNAP配線commit後に**Family X/Z正式経路へ配線(旧「両方PASS必須」置換、`dual→vote`は混合方式)→Regression→runtime evidence(≤¥5)→SSOT。ユーザー承認済み`APPROVED_FOR_PRODUCTION`。`PRODUCTION_WIRED`判定はFable)

## 管理ID
KP-THREE-ASR-MAJORITY-PRODUCTION-01 委任_02(OPEN-451。並行: **`PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01 委任_02`(PNAP)が`er006_secondary_asr_01.py`1146-1176付近・`er019`・`er063`・`er006_master_audio_store_01.py`・`er019_family_x_validation_inheritance_01.py`を配線中。Opusの推奨順(本件先)に反して既にPNAPが先行しているため、本件の**Production .py編集はPNAPの配線commit(`git log --oneline -30`で`PNAP 委任_02b`[配線]を確認)後に開始**し、それまでは設計反映・module・test・0円再評価を先行する。配線時はPNAPの差分(adapter挿入点・KP除外`dual_required`参照)を取り込み、KP除外を新flag(`vote_required`)へ追従+testを追加(Opus P-05/P-12)。`FAMILY-X-KP-MINIMIZATION-PRODUCTION-PATH-TRIAL-03 委任_03`はer019 KP stage(約:400-440)を編集中(commit確認後)。`KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01`(er105)は設計のみ。共有SSOTは`git status`→該当行再Grep→自分の行だけ→即add+commit、`index.lock`は30秒待ち)。

## 性質/到達上限Status/禁止事項
- 性質: Production配線(ユーザー承認済み)。到達Status: `WIRED_PENDING_FABLE`(X runtime evidence+Z正式経路evidence取得後)。`PRODUCTION_WIRED`宣言はFable。
- Opus Gate: 条件A実施済み(本委任で反映)。
- 修正範囲(11-8): 範囲内=設計書更新、`er104_*`改修+test、配線点(er078 `done()`→純粋集計関数、er006 adapter[PNAP差分の上]、er003_v1_repro01 kwarg、X: er019 runner/K2 store/validation inheritance、Z: er063、Store[混合方式=容器名維持・version `kp_vote_check_v1`]、Whisper preflight/circuit)、旧識別子の整理(`NG_DUAL_PRIMARY_NOT_PASS`撤去、意味名をvoteへ、er096はProduction importなしをAST testで固定し履歴scriptとして残置)、CURRENT_SPEC(2818/2819/2820/2827/2828/2922/1839注記の3-ASR版置換、2819「ローカルWhisper不採用(UDR #136)」の本承認による上書き明記)/DECISION_LOG/OPEN_ITEMS更新。範囲外=KP解説文・その他音声の判定、Primary単独への降格スイッチ、er008共有loaderの編集、HR Lockの迂回・人工entry作成。
- 時間見込み(8-X): 約6〜8時間(Opus反映+再評価2.5h/配線2.5h[PNAP commit待ちを含む]/Regression 1h/evidence 1h/SSOT 0.5h)。
- 費用/日次: 当日既使用 約JPY878+PNAP evidence(≤100、進行中)。本委任の有料=runtime evidence(X: byUs Store再利用でPrimary/Azure再呼出0=¥0+新規1KP、Z: dual導入前entryのS1経路再利用[Azure約0.01円/KP]+新規KP≤20本[≈2.4円])、**Guardrail(T-3) Cap JPY10**。実行前に日次合計(878+PNAP実費+本件)が1,000円以内か確認し、超える見込みなら翌JST日に実行。承認区分: C。`TTS_EXECUTION_MODE=STANDARD`。
- 禁止: `git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f。secret_scan hits=0。push=`git push origin HEAD:main`。ACTIVE_TASK/RESULT_PACKETはgitignore。SSOT全文読込禁止。他agentの未commit差分を混ぜない。有料runの再起動禁止・STOPセンチネル確認(rc≠0なら起動しない)。Whisper失敗/未実行でPASSにしない。HR Lock済みKPを新判定で自動解除しない。

## 前委任(委任_01)の受入記録(Gate 7、Fable記入)
- 当初目的(ユーザー原文逐語、`docs/pm/delegation_log/2026-10-22_KP-THREE-ASR-MAJORITY-PRODUCTION-01_USER.md`): 「Key Phrase英語フレーズの発音判定について、OpenAI・Azure・Whisperの3-ASR多数決方式を正式採用する。…既存の「OpenAI・Azure両方PASS必須」を置き換え、Production配線・テスト・runtime evidence・SSOT/Git反映まで完了させる。」
- 最終成果物: `docs/research/KP-THREE-ASR-MAJORITY-PRODUCTION-01/{IMPLEMENTATION_DESIGN_01,INVESTIGATION_01}.md`、`whisper_env_check_01.json`、`stored_audio_reeval_01.json`、`er104_kp_three_asr_vote_01.py`(+test 28)、`er104_whisper_env_check_01.py`、`er104_stored_audio_reeval_01.py`。commit c2f6f808c。Production未編集。
- 証拠: 真理値表6行test固定、Whisper small既存依存・1clip約2秒、保存音声で新規誤PASS 0(ただしOpus P-01により本番adapter経路での再評価が必要)。
- 一致・不一致: 設計範囲=一致。Opusで必須6+解釈1が検出。
- 判定: ACCEPTED(設計段階)。判定整合: 重大NG=なし/是正対象=Opus必須項目/STOP理由=なし/提示=なし。

## Opusレビュー(OF-KP3V-P-01〜12)のFable採否(全文を`docs/research/KP-THREE-ASR-MAJORITY-PRODUCTION-01/OPUS_REVIEW_COND_A_01.md`へ逐語保存[本委任文末尾に転記]、`docs/pm/OPUS_FINDINGS_LEDGER.md`にOF-KP3V-P-01〜12登録)
- **必須(全て採用)**: P-01(再利用6点の再判定を本番adapter経由[er096方式: `vote_required=True`+保存Secondary転写cache+保存Whisper転写(同sha)]に統一。`rejudge_stored`はtest専用化/削除。問題音声21件+判定変化4件を本番adapter経路で再評価し一致を受入条件に。旧`asr_judgement.dual`からの証跡経路維持)/P-02(Whisper票にも呼出元と同じ`max_len`長さ判定、値ガードAMBIGUOUSはPASS票にしない、test)/P-03(表4行目 P NG/S PASS/W PASS=`PASS_WITH_WARNING`+`SECONDARY_CONFIRMED`で事後試聴リストへ。2行目はPASS。adapterのclassification上書き処理を行ごとに整理)/P-04(戻しスイッチは`KP_WHISPER_TIEBREAK_ENABLED=False`=旧両方PASS必須に一本化。Primary単独へ落とすスイッチは置かない。定数読み取りは単一関数)/P-05(**混合方式**: 意味名[flag関数・kwarg・ctx・state・step名]は`vote`へ、`NG_DUAL_PRIMARY_NOT_PASS`撤去、保存容器名`kp_dual_check`・telemetry名は維持し`version="kp_vote_check_v1"`で区別、共有Store無編集。Store key `+vote1`化は可(manifest全件を配線時scriptで実測)。er096はProduction importなしをAST testで固定し履歴として残置[er019 test群/er096 evidence/er099が読むため削除しない]。PNAPのKP除外を新flagへ追従+test)/P-06(Zのevidenceは正式経路のみ: dual導入前のZ KP entryを再利用点6のS1経路に通す+新規KP≤20本、人工entry・Lock迂回禁止。発火が観測できなければ「Xで発火観測+Zが同じadapterを通ることをtestで固定+Zの正式runで`kp_vote_check_v1`記録が出ること」を事実として記録)/P-07(解釈の明記: (a)Azure障害時は技術STOP維持、(b)`NG_PROTECTED_DISSENT`=承認済み値/否定ガード(P1)の対称適用で既定ON、(c)WhisperにM1非適用、(d)救済PASSはPrimary NG票。SSOTとcloseoutに「解釈」として明記、ユーザー承認依頼ではない)。
- **配線中に対応(採用)**: P-08(空転写=NG票[通常再生成]、例外/import失敗/timeout=技術STOP。timeout時はcircuitを閾値1で即open。preflight+English Lock前のcircuit確認をWhisperにも拡張。OPEN-371へ露出増を追記。キャッシュ有無をpreflight記録)/P-09(judge `done()`から純粋集計関数`tally(...)`を1つ呼ぶ形に。`decide()`も同関数。状態変換はPASS→PASS_WITH_WARNING変換とLR_REWRITTEN付与より前。除外確定状態4つ)/P-10(`kp_vote_check`にどの行で合格したか記録[2行目=P+W/4行目=S+W]。think up・blurt・cause a stir#3/#4の4本を**運営者向け試聴ページ**`user_test/kp3v_vote_evidence_01/index.html`に載せる[Fableは聴けないためユーザーが任意で確認])/P-11(SSOT更新範囲)/P-12(test追加全項目)。

## 実行内容
1. 設計書更新+`er104_*`改修+test(P-12全項目)。本番adapter経路での再評価script(`er104_stored_audio_reeval_02.py`、0円: 21+4件、X/Z経路、結果json)。
2. PNAP配線commit確認後に配線(er078 tally→er006 adapter[PNAP差分の上、KP除外追従]→er003 kwarg→X[runner/K2 store/inheritance]→Z[er063]→Store version→preflight/circuit)。既定`KP_THREE_ASR_VOTE_ENABLED=True`/`KP_WHISPER_TIEBREAK_ENABLED=True`。
3. Regression: `run_project_regression.py --pattern "er078*_test*.py"`,`"er006*_test*.py"`,`"er096*_test*.py"`(履歴test、Production import不可を確認),`"er019*_test*.py"`,`"er063*_test*.py"`,`"er003*_test*.py"`,`"er104*_test*.py"`,`"er103*_test*.py"`。4,032ペア/HR79行のON/OFF差分(KP以外で0)。旧識別子Grep(混合方式の方針どおり: 意味名の残存0、容器名は維持)。
4. runtime evidence(費用条件確認後): X=byUs Store再利用(事前に`kp_dual_check`NG記録の存在確認)→think up/blurtがWhisperのみでPASS(Primary/Azure再呼出0)+新規1KP。Z=P-06方式。actual model ID(Primary/Azure/Whisper model name+compute type)・routing・判定記録・処理時間を保存。
5. SSOT: CURRENT_SPEC(KP PASS条件表を3-ASR版へ置換、2819上書き明記、P-07解釈)、DECISION_LOG、OPEN-451=`WIRED_PENDING_FABLE`、OPEN-440に「3-ASR多数決で置換(OPEN-451)」注記、OPEN-371露出追記、OPUS_FINDINGS_LEDGER、REPORT_LEDGER。T-0: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_KP-THREE-ASR-MAJORITY-PRODUCTION-01_委任_02.md`(Nは`FABLE-DELEGATION-MARKER: KP3V-IMPL-委任_02-20261022`を含むAgent tool_useの通番、287前後。先頭行で一致確認)。
6. 段階commit(a: Opus反映+再評価 / b: 配線+Regression / c: evidence+SSOT)→push→到達確認。`ACTIVE_TASK.md`固定ヘッダ。`RESULT_PACKET_KP3V2.md`(ユーザー§7の1〜8順、8のFable欄は空ける)。

## 事前指定Read/Grep
- Read: Opus指摘箇所(`er104_kp_three_asr_vote_01.py:170-240`、`er096_kp_dual_pass_01.py:95-175`、`er078_asr_unified_judge_01.py:430-485,540-605`、`er006_secondary_asr_01.py:1050-1125,1140-1180`、`er006_master_audio_store_01.py:105-250`、`er003_v1_repro01_main_generate.py:780-850`、`er063_family_z_audio_01.py:730-760`、`er103_proper_noun_alarm_policy_01.py:250-270`)、PNAP配線後の差分(`git show <PNAP commit> -- er006_secondary_asr_01.py`)。
- Grep: `kp_dual_check|reuse_blocked_by_kp_dual_gate|kp_dual_gate` in `er006_master_audio_store_01.py`(容器名維持の確認)、`import er096|from er096` in `er0*.py`(Production import 0)、CURRENT_SPEC `2818|2819|2820|2827|2828|2922|1839`。

## Git
- 明示add: 変更各ファイル(他agentの差分を含めない)。commit例: (a)`KP3V 委任_02a: Opus条件A反映(P-01〜P-12)+本番adapter経路での保存音声再評価、Production未編集` (b)`KP3V 委任_02b: KP英語フレーズ判定を3-ASR多数決へ置換(X/Z配線、混合改名、Whisper preflight/circuit、PNAP KP除外追従)、Regression PASS` (c)`KP3V 委任_02c: runtime evidence X/Z+運営者試聴ページ+SSOT、WIRED_PENDING_FABLE`。

## 報告(RESULT_PACKET_KP3V2.md)
ユーザー§7順(1 X/Z配線Status/2 think up・blurt・take partの新旧判定/3 Whisperのruntime発火証拠/4 誤PASS検証[本番adapter経路での再評価結果]/5 追加コスト・処理時間・再生成削減/6 retry/fallback/Store再利用の整合/7 SSOT・Git/8 Fable欄)+Opus反映一覧・P-07解釈文・旧識別子整理結果・費用実測・実行コマンド・RESULT_PACKET 4行・raw URL。

## 付録: Opusレビュー要旨(全文は`docs/research/KP-THREE-ASR-MAJORITY-PRODUCTION-01/OPUS_REVIEW_COND_A_01.md`へ、本委任文の「Fable採否」節に記載の所見P-01〜P-12の内容を逐語で転記すること。Fable注: Opus全文はFableが受領済みで、要点は上記採否節に漏れなく反映している。保存ファイルには「Fable転記・要旨」と明記)
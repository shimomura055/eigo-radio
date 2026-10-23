FABLE-DELEGATION-MARKER: ASR-QUALITY-2ITEMS-COMPREHENSIVE-01-PN-委任_03-WIRING-DESIGN-20261023

# 委任_03(①RET): APPROVED_FOR_PRODUCTION(ユーザー承認2026-10-23、UDR #168)を受けたProduction配線設計(Opus条件Cレビュー前まで)。設計のみ、コード変更0、API 0。

## 背景
ユーザーは ①RET(OPEN-472)・②UKUS(OPEN-471)のX/Z共通Production採用を承認、到達目標=X/Z双方PRODUCTION_WIRED。必須受入条件9項目(原文§2)。**原文を保存して読むこと**。②は別agent(…-UKUS-委任_03)が並行設計。『開いた窓』再開(B)はA配線後。

## T-0
1. **ユーザー原文を逐語保存**: jsonl `C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl` の最新userメッセージ(「# 指示｜ASR品質改善2件のProduction Wiring・Family Z『開いた窓』完成・Perplexity調査」)を `docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_USER_02.md` へ無改変保存(②/C agentも参照。最初にcommit/push)。
2. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl <同jsonl> --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_PN_委任_03.md`(index 361以降、先頭MARKER一致)。
3. ACTIVE_TASK自分の行のみ(並行: UKUS-委任_03、PERPLEXITY-401、FAMILY-Y 委任_08[有料run中の可能性、pythonプロセスをkillしない])。OPEN-472 Status=`APPROVED_FOR_PRODUCTION(2026-10-23 UDR #168)_WIRING_DESIGN_IN_PROGRESS`、UDR #168=判断済み(①②採用、③採用後に正式経路で再開、④speciality復元)。共有SSOTは編集直前`git status`→自分の行のみ→即commit。

## 設計(`docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/PN/WIRING_DESIGN_01.md` + `OPUS_REVIEW_REQUEST_02.md`)
Trial成果(`er111_pn_entity_table_trial_01.py`/`er111_pn_trial_evaluate_01.py`、DESIGN_02、OPUS_REVIEW_01 OF-PN2-01〜13、TRIAL_RESULT_01)を正式経路へ移す設計。
1. **配線点(X/Z別、file:line)**: 実体表の構築タイミング(脚本確定直後=X scaffold/plan段、Z plan段。TTS前に並行)、保存先(run audit `entity_table.json`)、PNAP `evaluate_alarm_eligibility`/`_noun_checks` への証拠供給(位置紐づけ、`ledger_surfaces` の集合渡しではなく出現位置)、RET-3(既存G3の変更=er103本体の直接変更。11-7限定例外対象外のため**承認済み正式採用に基づくProduction実装**として明記)、継承再判定(`er019_family_x_validation_inheritance_01.py:349-366`: 受理に使ったentryをアラームblockへ保存し逐語出現のみで再利用、LLMを呼ばない)、Local Rewrite時の和集合追加、Store再利用guard(`ortho_contributed` 相当の `entity_contributed` が必要か)、resume/regen(表の再構築条件、sha)、retry/fallback、kp_vote_check(KPはG0除外)、HR Lock経路残置。
2. **flag設計**: 単一定数(`RUN_ENTITY_TABLE_ENABLED=True` 既定ON、run scope内のみ有効=`er109_xz_scope_01` の `run_scope("X"/"Z")` を再利用、A/B/C・単体は従来どおり)。LLM失敗時は現行同一挙動(SC-6)。
3. **Trial→Productionの差分**: Trialの複製関数(G3複製+drift guard)を本体へ統合する方法(er103の該当関数を変更し、Trial複製は撤去)、DEV専用コードへの暗黙依存0(`er111_pn_*` をProductionからimportしない。共通ロジックは新Productionモジュール `er103_run_entity_table_01.py` へ移植し、`er111_*` はTrial資料として残置または撤去)。
4. **安全条件の不変**(受入条件6): 類似度≥0.40、R_GENERAL_WORD、P-03、G3二重ASR、数値/否定/脱落、KP/JA除外、差分≤3、HR Lock。表が空のときer103とバイト一致を保つtest。
5. **test計画**: 既存er103/er019/er063 test、golden signature、新規(位置紐づけ・RET-3厳密・負例・drift guard撤去後の等価test・DefaultOn scope isolation)、必須Regression。
6. **runtime evidence計画(受入条件4・9)**: Z=『開いた窓』Bertie 4clip再生成(B工程で取得、約2〜5円)。X=固有名詞を含む既存X記事の少数segmentを正式経路で再生成(候補: `kristie tse`/`stephen reicher`を含むrun、または直近記事の人名segment。`--only-segments`相当で2〜4clip、費用見込み)。各々で entity_table構築・証拠供給・ENTITY_ONLY_ACCEPT/アラーム記録・HR 0・Store反映を確認する手順。
7. **費用・時間**: 実装半日見込み、NER 0.06〜0.17円/記事セット、evidence合計≤15円。
8. **②UKUSとの順序・競合**: 同じer109_xz_scope/judge hookを触るか、競合ファイルの切り分け、commit順。
9. **撤去**: Trial複製・許可リスト・旧状態名。
Opus論点(条件C): 配線点の抜け(resume/regen/Store/LR/継承)、RET-3本体変更の安全性、既定ONの妥当性と隔離、X evidence設計の妥当性、②との干渉。

## 禁止
コード変更、Production実行、有料run、`er111_*`変更、②側ファイル編集。

## 報告(docs/pm/RESULT_PACKET_ASRQ_PN3.md)
(1)配線点表 (2)flag/隔離 (3)Trial→Production差分と撤去 (4)test/evidence計画と費用 (5)②との競合整理 (6)Opus論点 (7)commit・raw URL・SSOT + RESULT_PACKET 4行 + 「判定整合: 重大NG=なし」。
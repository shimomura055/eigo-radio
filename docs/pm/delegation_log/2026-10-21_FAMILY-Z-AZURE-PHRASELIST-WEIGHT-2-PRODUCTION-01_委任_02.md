# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01 委任_02(事実確認のみ・API 0・コード/仕様/Trial変更なし): Azure Phrase List重み2.0が正式Productionに採用されているか、Family X/Zの正式経路で実際に設定・発火しているかを、SSOT・コード・runtime evidenceで確認する。Git操作はT-0・原文保存・回答書のcommitのみ。SSOTは編集しない。

## ユーザー指示(原文・2026-10-21、全文)
`docs/pm/delegation_log/2026-10-21_FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01_FACTCHECK_USER.md`へ逐語保存(先頭に`# ユーザー指示原文(2026-10-21)`と`管理ID: FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01 委任_02(重み2.0採用・実動作の事実確認)`の2行、以降一字一句変えない。文字数・sha256[本文のみ]を報告)。
--- 原文ここから ---
**Phrase Listの重み2.0が正式Productionに採用されているか、事実確認してください。**

1. CURRENT_SPEC・DECISION_LOGで、重み2.0の正式採用判断を確認。
2. Family X／Zの正式Production経路で、実際に設定されている重みを確認。
3. 正式runtime evidenceで、重み2.0が発火しているか確認。
4. 過去の重み比較Trialとの関係を整理し、採用済み・未採用・Trial限定を明確に区別。

**回答は「重み2.0は正式採用済みか」「Productionで実際に動いているか」を最初に明記してください。**

根拠となるファイル・コード・実行記録を示してください。

今回は調査のみ。仕様変更・コード修正・Trialは不要です。
--- 原文ここまで ---

## 固定ブロック
E-1/D-1/G-1/F-1: 標準(SSOT全文読込禁止、Grep→該当行)。T-0: 本委任文を`docs/pm/delegation_log/2026-10-21_FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01_委任_02.md`へ逐語保存(`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`、N=「PHRASELIST-WEIGHT-2-PRODUCTION-01 委任_02」を含む最新index)。check結果1行。T-2: TTSなし。

## Fableが把握している手がかり(鵜呑みにせず原文で再確認・行番号付きで引用)
- 採用判断: `docs/pm/USER_DECISION_REGISTER_01.md` #126「判断済み 2026-10-20 Azure Phrase List重み2.0 APPROVED_FOR_PRODUCTION(Trial FAMILY-Z-AZURE-PHRASELIST-WE…)」。OPEN_ITEMS OPEN-426=CLOSED・PRODUCTION_WIRED。CURRENT_SPEC.md:2089付近のPRODUCTION_WIRED注記。DECISION_LOGの該当エントリ(`FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01` 委任_01、2026-10-20)。重み比較Trial=`er084_azure_phraselist_weight_trial_01_lib.py`(`docs/research/FAMILY-Z-AZURE-PHRASELIST-WEIGHT-*`配下、PHASE_B_RESULT_01等)と、その前のPhrase List導入Trial。
- 実装: `er006_secondary_asr_01.py:75`(`AZURE_PHRASE_LIST_WEIGHT=2.0`)、`:106-111`(`if phrases:`→PhraseListGrammar+`setWeight`)。X(er003/er006 cascade)/Z(er012経由)が同一関数を使うこと(委任MDJF1で証明済み: `er003_v1_repro01_main_generate.py:356`、`er012_b_family_voices_production_01.py:553`)。Family Z側のPhrase List供給元(何を入れているか: `er063`/`er012`のphrase list構築、Pronunciation Ledgerの`get_hint_for_text`、Melos等の人名entry)。Family X側はLedger英語hint由来(記事A/Bでは空=`phrase_list_size=0`、`PROPER_NOUN_PHRASELIST_INVESTIGATION_01.md`)。
- runtime evidence: Z=`FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01`のwire evidence(`dgi.bias=2.0`、メロス run_e2e_06、test 7件)。X=正式runでは未発火(Phrase List空)。er089 Trial(Trial専用、Production関数経由)で`bias=[2.0]`を観測(`er089_output/.../phrase_list_evidence.jsonl`)=Production配線の機構証拠だが正式runの証拠ではない。開いた窓はまだ音声未生成。
- 2026-10-20以前の状態(重み既定値/未設定、Trial限定期間)と、採用後の差分(commit)。

## 回答書(`docs/research/FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01/WEIGHT_2_0_FACTCHECK_01.md`)
先頭2行で「重み2.0は正式採用済みか: Yes/No(日付・ID)」「Productionで実際に動いているか: Family Z=…/Family X=…(発火条件付き)」。続けて1〜4の根拠(file:行、runtime evidence path、Trial名と区別[採用済み/未採用/Trial限定])。
secret scan→明示add(回答書・delegation_log 2件)→commit(`FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01 委任_02: 重み2.0の採用・実動作 事実確認(API 0)`)→`git push origin HEAD:main`。

## 報告(docs/pm/RESULT_PACKET_PLW2.md 上書き)
先頭2行の結論→1〜4→commit・raw URL→4行判定。
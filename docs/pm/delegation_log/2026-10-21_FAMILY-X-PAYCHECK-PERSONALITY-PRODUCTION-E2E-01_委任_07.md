# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01 委任_07(調査のみ・API 0・コード/仕様/成果物変更なし・Git操作はT-0と原文保存のcommitのみ): 記事A「収入と性格」の `134,515 people` が「中核数値(core number / protected number)」に選ばれているか、および中核数値の選定基準(CURRENT_SPEC+Production実装、X/Zの違い)を、実データと実装で確認して回答する。

## ユーザー指示(原文・2026-10-21、全文)
`docs/pm/delegation_log/2026-10-21_FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01_CORE-NUMBER-QUERY_USER.md`へ逐語保存(先頭に`# ユーザー指示原文(2026-10-21)`と`管理ID: FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01 委任_07(中核数値調査)`の2行、以降一字一句変えない。文字数・sha256[本文のみ]を報告)。
--- 原文ここから ---
以下の2点を、Repoの現行仕様・実データ・生成経路を確認して回答してください。

**1. `134,515 people` は中核数値に選ばれているのか？**
- 記事AのFact Ledger、Writer入力、生成Promptを照合し、事実を確認。
- 中核数値であれば、どの工程で、どのような理由で選ばれたのかを説明。
- 中核数値でなければ、なぜ正確な数字が維持されたのかを調査。

**2. 中核数値に選べる基準は何か？**
- CURRENT_SPECおよびProduction実装に基づき、選定基準・判断主体・選定件数の制限を説明。
- 明文化された基準とAIの裁量判断を区別する。
- Family X／Zで仕様が異なる場合は、その違いも示す。

**今回は調査・報告のみ。コード修正、仕様変更、追加Trialは行わないこと。**

回答は根拠となるファイル・該当箇所を明示し、簡潔にまとめてください。
--- 原文ここまで ---

## 固定ブロック
E-1/D-1/G-1/F-1: 標準。`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`全文読込禁止(Grep→該当行)。T-0: 本委任文を`docs/pm/delegation_log/2026-10-21_FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01_委任_07.md`へ逐語保存(`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`、N=「PAYCHECK-PERSONALITY-PRODUCTION-E2E-01 委任_07」を含む最新index)。check結果1行。T-2: TTSなし。

## 調査の手がかり(用語の候補。実装での正式名称を特定して報告)
- 「中核数値」に相当しうる概念: (a)B3(Selected Fact Brief)の中核Fact/周辺Fact区分(`c_core_peripheral`検査、`er053_b3_deterministic_producer_01.py`の注記: `b_numbers`=数値注記、sidecar)、(b)Fact Lock(W-1 R0、`er053_family_x_factlock_ja_writer_01.py`、Ledger外数値の禁止・数値の帰属)、(c)ASR側の保護数値(`protected_number`/`NG_PROTECTED`、`er006_preprod_hardening_01_validation.py`の数値token保護、Family X/Z共通)、(d)Risk Flagger(数値の帰属チェック)、(e)Key Phrase/IOLの数値扱い。ユーザーの「中核数値」がどれを指すか断定せず、該当しうる各層で「134,515」がどう扱われたかを示す。
- 記事A実データ: `er019_output/paycheck_personality/run_pp_01/`配下: `research_ledger/verified_fact_ledger.txt`(F04「最大134,515人、解析ごとにN異なる」)、`storyline_b3/`(selected_fact_ids=[F02,F04,F07,F08,F15]、fact_selection_evidence.json、selected_brief.md、注記済みmd・sidecar[数値注記=b_numbers、core/peripheral tag])、`ja_writer/`(R0 Fact Lock入力・R0/R1/R2出力、Prompt dump/構築関数の入力)、`b1b/article.md`・`a2/article.md`(本文「as many as 134,515 people」「up to 134,515 people」)、RF結果(`review_queue/post_en/paycheck_personality__run_pp_01/`)、audit(`audit_stop_scope`等)。
- 仕様: CURRENT_SPEC.mdをGrep(`中核|core_peripheral|周辺Fact|数値注記|b_numbers|protected_number|保護数値|Fact Lock|Ledger外`)し、選定基準・判断主体(決定論producer/LLM[B3=gpt-6.1-sol]/Writer)・件数制限(例: B3の採用Fact数min2/上限、中核Fact数)・Family Zとの違い(Family ZはFiction=Research/Ledger/B3なし、数値保護はASR側のみ等。`er026`/`er062`でGrep)。
- 「なぜ正確な数字が維持されたか」: Fact Lock(Ledger内数値の逐語維持指示)、R1/R2での数値改変禁止、決定論的注記、ASRの保護数値判定(TTS音声でも"134,515"が正しく読まれたかの検証ログ)の各層を実ログで追う。

## 手順
S1. 用語の実装名特定(上記a〜e)。S2. 記事Aの各工程で「134,515」の扱いを実ファイル行で追跡(Ledger→B3注記/sidecar→R0 Fact Lock→R1/R2→Adv/Std本文→RF→TTS/ASR保護数値判定)。S3. 選定基準・判断主体・件数制限をCURRENT_SPEC該当行+実装file:行で整理(明文基準/AI裁量を区別)。S4. Family X/Zの違い。S5. 回答書`docs/research/FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01/CORE_NUMBER_QUERY_01.md`(簡潔、根拠file:行付き)。S6. secret scan→明示add(回答書・delegation_log 2件)→commit(`FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01 委任_07: 中核数値(134,515)の選定有無と基準の調査(API 0)`)→`git push origin HEAD:main`。SSOT(OPEN_ITEMS等)は編集しない。

## 報告(docs/pm/RESULT_PACKET_FXPP7.md 上書き)
1.結論(134,515は「中核数値」か: 層ごとにYes/No+理由+根拠行) 2.選ばれた/維持された工程と理由 3.選定基準(明文/裁量、判断主体、件数制限)の表 4.X/Zの違い 5.用語の注意(ユーザーの「中核数値」と実装用語の対応) 6.commit・raw URL 7.4行判定。
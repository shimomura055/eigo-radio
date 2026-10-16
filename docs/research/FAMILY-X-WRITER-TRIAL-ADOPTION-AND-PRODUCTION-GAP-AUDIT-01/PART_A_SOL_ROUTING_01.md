# Part A: B3→R2 Sol統一の実装・runtime照合 (FAMILY-X-WRITER-TRIAL-ADOPTION-AND-PRODUCTION-GAP-AUDIT-01 委任_01A)

2026-10-16 / read-only監査 / JPY0 / 到達上限Status=PART_A_COMPLETE。調査時点: branch `work/post-merge-01` HEAD `168a2ebf1`(adb15c30はHEAD・mainの双方に含まれる。`git diff main HEAD`で対象4ファイルの差分なし)。未commitの作業ツリー差分も対象ファイルにはなし(`git status --porcelain`で対象py無し)。

## 結論(先出し)
Family Xの日本語正式初回経路(B3→R0→R1→R2)は、現在のmain/HEADでも `gpt-6.1-sol` 固定で、コード・routing・実行証跡(1回、META run_sol61_01)の3点が一致。モデル変更commit(adb15c30)でPrompt本文は変わっていない。retry/regeneration/resumeで旧モデル(Luna/Astra)へ戻る経路は、正式経路には見つからなかった。未確認は「Sol配線後にretry系(B3 attempt2・R0記号再生成・R2再実行)が実際に発火した実行証跡」と「Production runnerを通ったCoffee記事の実行証跡」(後述§5、§7)。

## §1 承認原文(2026-10-11、逐語)
出典 `DECISION_LOG.md:20571`(`FAMILY-X-JA-MODEL-ALLOCATION-SOL61-PRODUCTION-WIRING-01 委任_01 ユーザー正式決定`)。
> 「Family X日本語記事生成において、TrialのE案を正式採用する。Status：APPROVED_FOR_PRODUCTION。正式モデル配置: B3(Fact選定・ストーリーライン構築)=gpt-6.1-sol / B3後段(決定論的注記・制約付与)=現行仕様を維持(LLMなし) / R0=gpt-6.1-sol / R1=gpt-6.1-sol / R2=gpt-6.1-sol。B3→R0の入力契約は現行の新仕様を維持する。追加の個別品質Trial・モデル比較Trialは不要。今回のBlind評価を正式採用の根拠とする。ただし、Production Wiringに必要な技術テスト・統合テスト・runtime evidenceは省略しない。」
範囲注記(逐語): 「OKマスターは記事品質の承認であり、音声・翻訳・TTS・RF等の承認を意味しない。特にMETAの完成音声は引き続き保留する。」
Closeout=`DECISION_LOG.md:20574`(Status=PRODUCTION_WIRED、merge adb15c30、rollback tag `rollback/pre-sol61-ja-allocation-01-20261011`)。

## §2 CURRENT_SPECの現行記載と履歴記載の区別
| 行 | 内容 | 判定 |
|---|---|---|
| CURRENT_SPEC.md:1157 | 「2026-10-11追記: E案更新」(B3/R0/R1/R2=gpt-6.1-sol、旧記述はmerge前の旧配置と明記)。ただし文中「main未merge・PRODUCTION_WIREDではない」と書かれた当時の記述 | 現行(E案内容)。Status部分は次行で更新済み(履歴) |
| CURRENT_SPEC.md:1159 | 「Status更新: PRODUCTION_WIRED(2026-10-11、merge adb15c30)」 | 現行Status |
| CURRENT_SPEC.md:1169 | `W-1 Writer: PRODUCTION_WIRED`、「R0=gpt-6-luna」「R1・R2=gpt-6-astra」 | **履歴(旧配置)**。1157行の明記で旧と宣言されているが、1169行自体にはE案への注記がなく、本節だけ読むと旧モデルが現行に見える(誤読リスク) |
| CURRENT_SPEC.md:1194, 1199 | `gpt-6-astra`/`gpt-6-luna`の記述(旧配置時のcost/evidence記録) | 履歴 |
| CURRENT_SPEC.md:1529 | Advanced英語新規生成=gpt-6.1-sol(R0→R1→R2)、Standardは別(Family Z/該当節) | 別系統の現行記述 |
判定根拠: 1157行が「本節本文中の『R0=gpt-6-luna』『R1・R2=gpt-6-astra』はmerge前の旧配置の記述」と明記。コード側の値(§3)が正。**所見(要是正候補、編集はしていない)**: 1169行に「(旧配置: E案で置換済、1157行参照)」の旧記述マークがない=読み違いリスク。SSOT編集は委任_02以降でFable判断。

## §3 工程別routing表
モデル決定の単一出所: `er006_model_routing_contract_01.py:134,137,138` `PROCESS_MODEL_MAP` の `FAMILY_X_STORYLINE_B3` / `FAMILY_X_FACTLOCK_R0` / `FAMILY_X_FACTLOCK_REVISE` = リテラル `"gpt-6.1-sol"`。環境変数での上書き: `os.environ`/`getenv`はこのファイルに0件(Grep確認)。`require_model()`(:170-190)は不一致・未指定でModelContractViolation(fail-closed、SDK default fallback禁止)。実値を`.venv`でimport確認(read-only): 3キーとも`gpt-6.1-sol`、`w1.R0_MODEL`=`w1.ASTRA_MODEL`=`gpt-6.1-sol`、effort R0/R1/R2=high。

| 工程 | モデル決定箇所(ファイル:行) | 既定model_id | 上書き経路 |
|---|---|---|---|
| B3(初回) | `er019_family_x_entertainment_production_runner_01.py:153` `routing.require_model("FAMILY_X_STORYLINE_B3", ...)` → `b3.run_storyline_b3_selection(model=b3_model)`(:154)、返却model不一致で`RuntimeError [STOP]`(:156-157) | gpt-6.1-sol | なし(runner内にoverride無し) |
| B3 retry | `er019_family_x_storyline_b3_fact_selection_01.py:217` `for attempt in (1,2)` が同一`model`引数で`_call_once`。モデル変更なし | gpt-6.1-sol(同一引数) | なし |
| R0(初回) | `er053_family_x_factlock_ja_writer_01.py:40` `R0_MODEL=routing.PROCESS_MODEL_MAP[...]`、`call_luna_r0 :280-291`(`require_model`、developer=DEVELOPER_MESSAGE、返却model不一致でProvenanceViolation) | gpt-6.1-sol | なし |
| R0 記号再生成(retry相当) | `:360-361` 同じ`call_luna_r0`を再利用 | gpt-6.1-sol(同関数) | なし |
| R1 | `:401` `astra_stage("r1", r0.md)` → `call_astra :200`(`require_model("FAMILY_X_FACTLOCK_REVISE")`、返却model検査) | gpt-6.1-sol | なし |
| R2(初回) | `:407` `astra_stage("r2", r1.raw.md)` | gpt-6.1-sol | なし |
| R2 記号再実行(retry相当) | `:421` 同`astra_stage("r2", r1.raw.md, ...)`、同一R1 raw | gpt-6.1-sol | なし |
| call_astra 一時エラー再試行 | `:200-219` ループは同一`ASTRA_MODEL`のみ。ProvenanceViolationは再試行せず伝播 | gpt-6.1-sol | なし |
| regeneration(`--regenerate-stage storyline_b3` / `writer`) | runner `:364`、`need_writer :429`、`run_ja_writer :437`→`w1.run_w1_writer`(同一初回関数)。storyline_b3は`run_storyline_b3 :153`(同一) | gpt-6.1-sol | なし |
| resume / 既存記事再利用 | runner `:430-435` `load_reused_ja_text`(`:233-`): LLM呼出なし。`chain_method=="W-1"`かつ注記md sha一致の場合のみ再利用、他は`LegacyWriterProvenanceStop`でSTOP(旧Writer記事の黙示再利用を防止) | (呼出なし) | なし |
| Local Rewrite / self recovery / precheck retry(JA Writer) | JA W-1経路(上記ファイル)にこれらの呼出は存在しない。`er019_family_x_ja_recheck_retry_01`はtest(`_test_01.py`)のみでproduction moduleなし(Glob確認)。Local Rewrite(OPEN-256)はTTS/ASR側(`er053_family_x_open256_*`)でWriterモデルとは別系統(本Partの範囲外、委任_01C/Fable確認) | 該当経路なし | - |
旧モデルが残る箇所(正式経路外):
- `er019_family_x_ja_writer_o_r1_r2_01.py:45` `WRITER_MODEL = vfl01.MODEL`(Luna)、`call_fresh :157-173`。これは旧Writerで、`er053_family_x_factlock_ja_writer_01.py:33`が`import ... as jaw`して**Prompt定数だけ**流用(使用箇所: `jaw.build_original_prompt`/`R0_PROMPT`/`DEVELOPER_MESSAGE`/`SYMBOL_PREVENTION_BLOCK_JA`/`CONCRETENESS_CONTROL_AN3_BLOCK`/`_extract_title`/`vfl01.get_client`)。`jaw.call_fresh`は`:39`のコメントに「流用しない」と書かれるのみで呼出なし(Grep確認)。旧モジュールはimportされるだけで、旧モデルでAPIは呼ばれない。
- 正式runnerからは `ja_writer_o_r1_r2`を直接importしていない(runner `:52`はw1のみ)。
- Trial driver(`er052_output/*/maq_driver_*.py`, `b3sep_driver_01.py`, `b3r2_driver_01.py`)は`vfl01.MODEL`(Luna)や`require_model_or_override`で別モデルを使うがTrial専用で正式runnerから呼ばれない。`er036_family_y_voice_structure_trial_01.py:141`はFamily Y Trial。→「Trial実装のProduction混入」は検出されず。
- 英語側のAdvanced/Standard生成(`NATURAL_ENGLISH_ADAPTATION`/`STANDARD_A2_ADAPTATION`)は`er006...:104-110`で`WRITER_MODEL`=`gpt-6-luna`(`:48`)。今回のSol統一の対象(日本語B3/R0/R1/R2)外。CURRENT_SPEC:1529の「Advanced英語をgpt-6.1-solで新規生成」はFamily Z/新仕様側の記述で、Family X英語化がLunaのままである点は委任_01B/Fableで仕様との整合確認が必要(本Partでは判定しない)。

## §4 入出力契約の実装確認
- R0入力=注記済みB3: `run_w1_writer :318-`の入口で`validate_annotated_b3(out_dir)`(契約違反はAPI前STOP)、`parse_brief_md`→`news_text = annotated.news_field_text`。注記なしB3へのfallback経路なし(docstring + 実装)。
- R1入力=R0のtag除去済み本文: `:401` `astra_stage("r1", .../r0.md)`。
- **R2入力=R1 raw**: `:402` `r1.raw.md`に生出力(後処理前)を書き、`:407` と再実行側`:421`の双方が`r1.raw.md`を読む。承認契約(CURRENT_SPEC:1169「R2入力=R1のraw出力」)と一致。再実行時も同一R1 raw。
- 記号QA案A(R2の判定は最終文、1回のみ再実行、残ればSTOP): `:411-433`。R0記号QAは1回のみ再生成後STOP(`:355-368`)。
- B3後段=決定論producer(`deterministic_v2`、llm_calls=0): runtime_evidence_01.mdとrunner `run_annotation_producer`(`:199-`)。

## §5 runtime evidence
| 項目 | 状態 | 出典 |
|---|---|---|
| B3/R0/R1/R2 actual model_id(META run_sol61_01) | 確認済み: 全4 stage `gpt-6.1-sol`、model_mismatch=false、18.499円、173秒 | `er053_output/sol61_production_wiring_01/runtime_evidence_01.md`、`er019_output/meta/run_sol61_01/raw_usage_log.jsonl`(storyline_b3/w1_r0/w1_astra_r1/w1_astra_r2 各1件を再集計: 全て`gpt-6.1-sol`) |
| META run_sol61_01 `ja_writer/runtime_evidence.json` | 確認済み: chain_method=`W-1`、chain_method_detail=`factlock_r0__r1_r2_independent_sol61`、r0/r1/r2 model=`gpt-6.1-sol`、mismatch=false | 同ファイル |
| 現在のPrompt定数と実行時Prompt sha | 確認済み(今回read-only再計算): `w1.verbatim_shas()`14キーが、run_sol61_01実行時記録の`verbatim_shas` 14キーと全一致(差分キー0) | `er019_output/meta/run_sol61_01/ja_writer/runtime_evidence.json`の`verbatim_shas` |
| retry系の実発火(B3 attempt2 / R0 symbol regen / R2 symbol rerun)がSol下で動いた証跡 | **未確認**: run_sol61_01では「R0再生成なし・R2再実行なし」(runtime_evidence_01.md)。コード上は同一モデル関数を再利用(§3)だが、実発火の実行証跡はない。testはDECISION_LOG:20574に「関連171 passed」の記載(今回は再実行していない) | - |
| Production runner経由のCoffee記事のSol生成 | **未確認**: Coffee最新run `er019_output/coffee_prices/run_v5_ms_01`の`ja_writer/runtime_evidence.json`は`chain_method="MAQ_TRIAL_W-1"`(Trial armのE案マスター。`a2/audit/ja_source.json`=`approved_quality_master:coffee_prices@742e7b6a7fe4`、`approved_master_acceptance.jsonl`のallowlist=`MAQ_TRIAL_W-1`)。中身のmodelはr0/r1/r2・storyline_b3とも`gpt-6.1-sol`(model_mismatch=false)だが、正式runnerの`W-1`経路ではなくTrial driver出力を承認マスターとして再利用したもの。DECISION_LOGの決定(`FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01 ユーザー決定①(案b)2026-10-11`)に基づく扱い | 上記ファイル |
| 同Coffee音声wiring run `coffee_prices__run_m2p0_n01_01/raw_usage_log.jsonl` | 確認済み: scaffold(`gpt-6-luna` 15件)/tts(gemini-flash-lite-tts等)のみ。Writer工程(B3/R0/R1/R2)のログは含まない → Writer段のmodel_idはこのファイルからは証明できない | 同ファイル(Counterで集計) |
| writer_result.json(10月以降のFamily X) | Globでは`er012_output/*`のA2系4件のみ(Family X JA W-1の証跡ではない)。JA W-1の証跡は`ja_writer/runtime_evidence.json`側 | Glob |
| 再取得(API呼出) | 行っていない(JPY0) | - |

## §6 Writer品質改善Promptの欠落有無(予備確認)
- `git diff adb15c30~1 adb15c30 --stat`(47ファイル)に含まれるWriter関連pyは `er053_family_x_factlock_ja_writer_01.py`(+14/-)、`er053_family_x_factlock_ja_writer_01_test_01.py`、`er019_family_x_entertainment_production_runner_01.py`、`er006_model_routing_contract_01.py` 等。`er019_family_x_storyline_b3_fact_selection_01.py`と`er019_family_x_ja_writer_o_r1_r2_01.py`(Prompt定数の所在)は**変更なし**。
- `er053_family_x_factlock_ja_writer_01.py`のadb15c30差分(`git diff adb15c30~1 adb15c30`の+/-行)は、docstringのモデル名、`CHAIN_METHOD_DETAIL`、`R0_MODEL`/`ASTRA_MODEL`の出所(リテラル→routing参照)、docstringの「リテラル固定」記述のみ。Prompt本文・正規表現・閾値の変更行なし。
- adb15c30以降(~HEAD)に上記4ファイル+`ja_writer_o_r1_r2`・`b3_deterministic_producer`・`b3_annotation_contract`のdiffは0(`git diff --stat adb15c30 HEAD -- <6ファイル>`の出力が空)。
- 上記sha一致(§5)と合わせ、「モデル変更によるW-1 Prompt/AN3/Fact Lock定数の欠落」は検出されず。**範囲外(委任_01C)**: Prompt本文と承認済み改善要素の網羅突合、E(Dangling)判定。

## §7 判定
- 問題なし(根拠付き): (a)B3/R0/R1/R2の正式初回経路がSol固定(§3、routing.py:134-138、runner:153、w1:40-42)。(b)env/flag上書きなし、`require_model`fail-closed、返却model不一致STOP。(c)retry/regeneration/resumeで旧モデルへ戻る正式経路なし(同一関数再利用、resumeはLLM呼出なしでLegacy provenanceをSTOP)。(d)R2入力=R1 rawを実装(w1:402,407,421)。(e)Prompt sha一致、adb15c30でPrompt本文不変。(f)runtime evidence 1件(META)で4工程のmodel_idがSol。
- 問題あり/要注意(開発側是正候補、いずれも編集していない): (1)CURRENT_SPEC:1169の旧配置記述に旧マークなし(誤読リスク)。(2)旧`ja_writer_o_r1_r2`モジュールの`WRITER_MODEL=Luna`定数が残存(未使用だがimportされる。誤配線時の巻戻りリスクは低〜中。撤去要否はFable判断)。
- 未確認(推測でPASSにしない): retry系のSol下実発火証跡、Production runner(W-1 chain)経由のCoffee記事Writer実行、Sol配線後の複数テーマ実行(Sol配線後の正式runnerによるW-1実行はMETA N=1のみ)、unit test再実行(今回は実施せず)。
- 新規のUSER_DECISION_REQUIRED候補: なし(本PartでSol統一の再判断は不要。ユーザー決定済み)。

## §8 Fable確認要の箇所
1. Coffeeの記事が `MAQ_TRIAL_W-1`(Trial driver出力の承認マスター)であり、正式runnerのW-1 chain経由ではない点。「ResearchからCoffee全面再制作」(ユーザー決定済み)の際は正式runnerで`chain_method=W-1`の実Sol実行が初めて取れる=その時のrouting確認項目になる。
2. 英語Advanced/Standard生成(`WRITER_MODEL`=Luna)とCURRENT_SPEC:1529(Advanced英語gpt-6.1-sol)の整合は委任_01B/Fableで確認。
3. CURRENT_SPEC:1169の旧配置注記是正の要否。
4. `ja_writer_o_r1_r2`のLuna定数の扱い。

## §9 T-0結果・所要・受入記録
- T-0: 委任文を`docs/pm/delegation_log/2026-10-16_FAMILY-X-WRITER-TRIAL-ADOPTION-AND-PRODUCTION-GAP-AUDIT-01_01A.md`に保存(固定ブロック・事前指定等は要約化、ユーザー指示原文は`_USER.md`と本文内に一字一句保存)。`check_delegation_prompt.py`=FAIL(理由=必須セクション「事前指定Grep一覧+追記位置・更新位置の手順」「実行コマンド全文」の見出しを保存時に統合・省略したため。内容は保存ファイルに要約記載)。作業は継続。
- stop_scope_check: `--run-dir er019_output/meta/run_sol61_01`で実行 rc=0(stop=false、Family Z STOP_NOTICEは適用外)。なお最初の実行はrun-dir未指定のためusage errorで空振り(rc=2)。
- 受入記録: (1)当初目的=ユーザー指示原文§2「B3→R2: 現在のmainでも正式初回経路がSolを使用するか/B3・R0・R1・R2のrouting・model_id証跡/R2入力=R1 raw/retry・fallback・regeneration・resumeで旧モデルへ戻らないか/Luna・Astra履歴の誤読/Prompt欠落」 (2)最終成果物=本ファイル、`docs/pm/RESULT_PACKET_FXWA1A.md`、delegation_log 3ファイル (3)証拠=§3(コード行)・§5(実行証跡)・§6(git diff・sha一致) (4)一致/不一致=Sol統一とR2入力契約は一致、retry実発火証跡とCoffee正式W-1実行は未確認、CURRENT_SPEC:1169は表記不整合 (5)判定=PART_A_COMPLETE(重大な問題なし、未確認事項あり)

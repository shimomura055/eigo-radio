## 管理ID

GRAMMAR-PREGEN-ALL-LEVELS-01 委任_05A(ユーザー正式決定2026-10-27「文法選定仕様の正式変更【全Family共通】」APPROVED_FOR_PRODUCTION: AI評価のTop 1・Top 2の**最大2件のみ提示**(順位順)、各候補に文法名+解説全文を選定前表示、**ユーザーは原則1件選択・0件可・2件同時選択禁止**、確定後不変。事前生成はTop 1・Top 2の2候補分のみ(費用削減、Trial-08選定方式・品質仕様は不変)。旧「文法最大2件選定可」を置換。本委任=共通核(er120/er119_grammar_review)・確定内容保護(er128)・CLI・exporterの仕様変更+KP先行確定モード(`--grammar-pending`)。API 0・JPY0)。ユーザー原文=並行Agent(AI-ISLAND-FORM-PRODUCTION-01 委任_02)が`docs/pm/delegation_log/2026-10-27_AI-ISLAND-FORM-PRODUCTION-01_USER_02.md`へ保存(未作成なら本委任文の引用§5で足りる)。並行Agent: (a)GRAMMAR-PREGEN-ALL-LEVELS-01 委任_03(X/Y/Z runner・ページbuilder・`er120_part2_wiring_01.py`薄い追加・integration test=**これらは編集しない**)、(b)AI-ISLAND-FORM-PRODUCTION-01 委任_02(フォームUI/データ=`user_test/selection_form_v3/**`・`build_data_01.py`=**編集しない**。exporterは本委任所有、(b)は読むのみ)。あなたの所有=`er120_part2_grammar_production_01.py`(核)、`er119_grammar_review_01.py`、`er128_kp_confirmed_content_01.py`+test、`er119_kp_human_review_cli_01.py`、`docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py`、`er120_part2_pregen_test_01.py`/`er120_part2_grammar_production_01_test_01.py`/`er119_grammar_review_test_01.py`/`er128_*_test_*.py`、`docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/{SCHEMA_CONTRACT_02,DESIGN_03,IMPLEMENTATION_05A}.md`、`docs/pm/delegation_log/2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_DELEGATION_05A.md`(+check.json)、`docs/pm/RESULT_PACKET_GPG5A.md`(gitignore、`-f`禁止)。SSOT編集権なし。pathspec付きcommit(他Agentのstage分を巻き込まない)。

## 性質/禁止

- 性質: 承認済み仕様変更(選定数・表示数)の実装。Opus条件A: 直前の設計(DESIGN_02)のレビュー済み骨格を変えず「件数・提示範囲」のみ変更=再レビュー不要(内容が変われば再レビューの原則に照らし、Fable判断で省略。DESIGN_03に差分を明記)。到達上限=IMPLEMENTED(核・保護・CLI・exporter)。
- 禁止: Trial-08順位付け・Prompt・解説品質の変更、2件pickの残置、Top2以外の候補の事前生成(全候補opt-in `--all-candidates`は撤去または明示的に「旧仕様・使用禁止」化=撤去を推奨)、runner/wiring/ページ/フォームUIの編集、禁止Git操作(`add -f`/`pull --rebase`/pathspecなしcommit)。
- 時間見込み: 約3h。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文保存+check、結果1行。T-2/T-3: なし。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_DELEGATION_05A.md` をN=724から順に試し、先頭「## 管理ID」+「GRAMMAR-PREGEN-ALL-LEVELS-01 委任_05A」のものを採用(同時刻にAI-ISLAND 委任_02あり)。

## ユーザー指示(該当部・逐語)

## 5. 文法選定仕様の正式変更【全Family共通】

対象：Family X/Y/Z × Standard/Advanced。

新仕様：

1. AIが文法候補を評価して順位付けする。
2. **ユーザーにはTop 1・Top 2の最大2件のみ提示する。**
3. 表示順はAI評価の順位順（Top 1 → Top 2）。
4. 各候補の文法名と、エンドユーザー向け解説全文を選定前に表示する。
5. **ユーザーは原則1件を選ぶ。**
6. 適切な候補がない場合、0件も選択できる。
7. 2件同時選択は禁止。
8. 確定した文法名・解説全文は後続工程で変更しない。

候補が1件しかない場合は1件、0件の場合は0件を提示する。数合わせのための候補追加は行わない。

既存のTrial-08選定方式・品質基準を尊重し、今回承認された選定数・表示数の変更以外を独断で変更しない。

### 事前生成との整合

別途正式承認済みの「選定前に文法解説全文を生成する」方式を維持する。

AI評価Top 1・Top 2が特定できた後に、その2候補の解説全文だけを生成する方式が合理的であれば採用し、不要なAPI費用を削減する。ただし既存の品質仕様・Trial-08選定方式との整合を必須とする。

ユーザーが選んだ解説全文を後から生成し直すことは禁止。

### 旧仕様の整理

旧「文法最大2件を選定可能」という制約を新仕様に置換する。

対象には以下を含める。

- V3フォームのUI・選定状態・件数表示
- フォーム送信内容・schema・Validator
- 文法Human Review
- 確定保存データ
- 文法finalize
- 組立・公開表示
- retry／fallback／regeneration／resume
- CURRENT_SPEC・関連テスト・既存の旧規則参照

文法解説の公開対象は、承認済みどおり**X/Y/ZのStandard／Advancedすべて**とする。

## 4. ユーザー確定内容の保存・保護(抜粋)

英語表現、日本語訳、①②③区分、candidate_idを変更しない。StandardとAdvancedで同じ英語表現の日本語訳が異なる場合も、今回確定したレベル別の訳をそのまま保持する。候補ID、本文SHA、候補集合SHAを元データと照合し、不一致があればfail-closedとする。(AI島Std/AdvはKP/KW 10件ずつUSER_CONFIRMED、**文法のみ再選定待ち=0件として最終確定しない**)

(引用ここまで)

## 実施事項

1. **`SCHEMA_CONTRACT_02.md`/`DESIGN_03.md`**(DESIGN_02からの差分のみ): 提示=Trial-08順位のTop1/Top2(`presented_ids`最大2、順位付き)、pregen対象=`presented_ids`のみ(PREGEN_MAX→2、候補1件なら1、0件なら0)、review v2 `pick`=最大1(`selected_ids`長さ≤1、2件はValidatorで拒否)、`omit`=0件、result v2 items[]≤1、frozen≤1、sidecar≤1、フォームpayload `grammar[]`≤1+`rank`、**KP先行確定モード**(`confirm --from-form --grammar-pending`: KP/KW 10件を確定・保護し、文法reviewはPENDINGのまま再選定待ち=0件確定にしない。後から`confirm --grammar-from-form <payload>`で文法のみ追加確定(KPレコードは不変、revisionに文法追加を記録、冪等))、`--all-candidates`撤去。
2. **核(er120/er119_grammar_review)**: `pregen_stage`はTop1/Top2のみ生成(`candidate_and_pregen_stage`経由。順位はTrial-08既存ロジック=無変更)、HR依頼書はTop1/Top2を順位明示で提示(3位以降は非表示・件数のみ「他N件」表示可)、`apply_form_selection(ids)`は`len(ids)≤1`(2件はValidatorエラー)、finalize/result v2≤1、`grammar-show`も同様。旧「最大2件」参照の撤去(Grep `<= 2|max 2|2件|TOP_N`で確認。`TOP_N=2`は提示数として維持=意味を「提示上限」と注記)。
3. **er128**: `cmd_from_form`文法≤1(2件→ISSUE)、`--grammar-pending`(文法未確定でKPのみ確定、sidecarは`status=pending`で作成し「0件確定」と区別)、`confirm --grammar-from-form`(文法のみ追加確定、Top1/Top2の`presented_ids`に含まれること・解説全文逐語一致・1件以下)、frozen/sidecar/G4≤1、`guard_grammar`≤1。既存test更新+新規(2件ISSUE、pending→後から1件、pending→後から0件omit、pendingのままfinalize試行→rc=4待機、冪等)。
4. **exporter**: `--grammar-study-dir`出力を`presented_ids`(Top1/Top2・rank付き)に限定、`grammar_max_select=1`をデータJSONへ。`candidates_sha256`/`text_sha256`の出力を確認(AI島Std/Advの照合に使う)。
5. test全体(er120/er119_grammar/er128/form1)。GPG4の既知不具合(wiring側: 凍結済みでも`explain_signature`検査でPart2Stale)は委任_03所有のwiringのため**本委任では触らず**、再現testの`expectedFailure`を維持し引継ぎに明記。
6. `IMPLEMENTATION_05A.md`。

## 事前指定Read一覧

- `docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/{SCHEMA_CONTRACT_01,DESIGN_02,IMPLEMENTATION_02,IMPLEMENTATION_04}.md`
- `er120_part2_grammar_production_01.py`(Grep `TOP_N|pregen|presented|pick|select|PREGEN_MAX|all_candidates|rank|Tier` ±8)、`er119_grammar_review_01.py`(Grep `apply_form_selection|pick|omit|render_request_md|form_grammar_bundle|TOP` ±8)、`er128_kp_confirmed_content_01.py`(Grep `cmd_from_form|grammar|sidecar|frozen|guard_grammar` ±8)、`er119_kp_human_review_cli_01.py`(Grep `grammar|confirm` ±5)、`export_form_data_01.py`(Grep `grammar|study_dir|sha256` ±5)
- `docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/DATA_MODEL_02.md`(grammar schema)

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_DELEGATION_05A.md --json-out ...\_check.json`
- test: `.venv\Scripts\python.exe run_project_regression.py --pattern "er120_*_test_*.py"`、`--pattern "er119_grammar_review_test_01.py"`、`--pattern "er128_*_test_*.py"`、`--pattern "form1_selection_form_v3_test_01.py"`
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

編集権なし。`RESULT_PACKET_GPG5A.md`にOPEN-559/556更新文案、CURRENT_SPEC文法選定仕様(Top1/Top2提示・1件選択・0件可・2件禁止・事前生成はTop2のみ)文案、DECISION_LOG文案、旧「最大2件」記述の履歴化文案(CURRENT_SPEC/DATA_MODEL/PM_GOVERNANCE参照箇所一覧)。

## Git

- commit message: `GRAMMAR-PREGEN-ALL-LEVELS-01 委任_05A: 文法選定仕様変更(Top1/Top2のみ提示・1件選択・0件可・2件禁止・事前生成はTop2のみ)を核/確定内容保護/CLI/exporterへ実装+KP先行確定(grammar-pending)モード+test(API 0)`。trailer: `Delegation: GRAMMAR-PREGEN-ALL-LEVELS-01/05A`。push。

## 報告

`docs/pm/RESULT_PACKET_GPG5A.md`: (0)T-0、(1)差分(ファイル:行)、(2)KP先行確定モードの使い方(AI島委任_02向けコマンド列)、(3)test、(4)委任_03/05Bへの引継ぎ(wiring/ページ/Validatorの≤1化、GPG4既知不具合)、(5)判断候補、(6)必須4行+「判定整合: 重大NG=<なし|あり>」、(7)SSOT文案、commit hash・raw URL。末尾10行要約。
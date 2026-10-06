# 01 現行Fact台帳パイプライン調査(OPEN-233-LEDGER-CLARITY-DESIGN-01 委任_01a、read-only、¥0)

凡例: 【確認】=ファイル・行で確認済、【推測】=未確認の推論。

## A. 生成工程
- 【確認】台帳は2段API(Responses API、model=`gpt-5.6-luna`、reasoning=high、tools=web_search): ①Researcher(Webで調査しfact構造化JSON `fact_ledger_draft.json`) ②独立Verification(別call、Webで再照合、`fact_ledger_verification.json`)。③決定論Python `build_verified_ledger_text`が整形して`verified_fact_ledger.txt`を出力。
- 根拠: `er019_family_x_entertainment_production_runner_01.py` L91-135(`run_research_and_ledger`)、`er012_e_family_entertainment_two_level_runner_01.py` L161-205、`er003_v1_en_direct_vfl_01_generate.py` L128-167(Researcher prompt)・L275-305(整形)。
- 【確認】原資料=Web検索結果(一次資料優先)。ユーザー提供テキストではない。
- 【確認】JSON fieldは `fact_id, claim, subject, date_or_period, scope, conditions, numeric_value, numeric_scope, causal_strength, source_title, source_url, source_type, support_level, ambiguity, notes_for_writer`(同 L91-116)。txtへ出るのは claim/scope/conditions/numeric_value/date_or_period/causal_strength(NOT_APPLICABLE以外)/ambiguity_note(AMBIGUOUSのみ)/notes_for_writer。subject・support_level・source_urlはnotes末尾リンク以外txtに出ない。
- 【確認】txt形式: `[VERIFIED] MUSE-HC-012: <claim本文1文>` + インデント付き`key: value`行、factは空行区切り(例 `er019_output/meta/run_03/ledger/verified_fact_ledger.txt` L74-78)。AMBIGUOUSは見出しが`[AMBIGUOUS - 断定禁止、曖昧さを保持すること]`。
- 【確認】fact数: Meta run_03=15件(VERIFIED15/AMBIGUOUS0/REJECTED0)。
- 【確認】実測(`er019_output/family_x_b3_production_wiring_01/run_01/raw_usage_log.jsonl`+`cost.json`): Researcher ¥14.47 / 85.7秒 / 入力51k・出力8.5k token / web検索7回。Verification ¥14.27 / 63.4秒 / 入力62k・出力5.6k / web検索7回。台帳生成計約¥28.7・約149秒(同run総額¥44.66の64%)。
- 【確認】既存台帳の再利用経路あり: `run_research_and_ledger`は`verified_fact_ledger.txt`が既存ならAPIを呼ばず再利用(L92-97)。fixture台帳(例 `er019_output/meta/run_03/ledger/`)は`reuse_source.json`に`reused_from`+sha256を記録(er012 L243)。sha256を後工程で強制照合しているかは【未確認】。

## B. 検証工程
- 【確認】台帳段の検証=上記②のAI(同一model luna、別call)。観点は9点(Source存在/数字scope/対象群と全体の混同/日付/制度適用範囲/条件抜け/因果過剰/Source間矛盾/曖昧Factの無理な確定)、verdict=VERIFIED/AMBIGUOUS/REJECTED(`er003_v1_en_direct_vfl_01_generate.py` L220-245)。REJECTEDは台帳から除外、検証結果欠落はAMBIGUOUS扱い(L282-287)。
- 【確認】人間検証は台帳段にはない。決定論の原資料照合もない(AI再照合のみ)。
- 【確認】記事段の検証: JA記事に対し台帳全文とのdeviation check(`vfl01.run_deviation_check`、MAJORなら must_fix で1回Rewrite、`er019_family_x_ja_writer_o_r1_r2_01.py` L125-165, L276-300)。さらにOPEN-233のStage1 Checker(記事unit単位 SUPPORTED/CANDIDATE判定、`support_fact_ids`と台帳逐語引用`ledger_quotes`必須、`er052_open233_stage1_coverage_checker_01.py` L224-226)と決定論floor(floor_verify)。`fact_check.json`(er012 audit)は記事↔台帳のcheck出力であり台帳自体の検証ではない【推測: 生成元はdeviation check系。生成コード行は未特定】。

## C. 既存ルール(台帳側)
- 【確認】Researcher prompt(L152-157)に4観点: 対象範囲(scope)を母集団と混同しない/制度・仕様の適用条件(時間的・条件的scope、揺れる場合は追加検索、確定不能ならambiguityへ)/数値の内訳(推測で数字を作らずnull+ambiguity)/観察・相関・因果の区別(causal_strengthとnotes_for_writerでSourceより強い因果表現を後工程に使わせない)。
- 【確認】時系列専用ルール・「主体(誰が何をしたか)」を1factに1つへ限る分割ルール・多義語(「止めた」等)の言い換え規則は台帳生成promptに無い(`date_or_period`欄はあるが整形指針なし)。CURRENT_SPECのGrepで台帳生成に関する曖昧/時系列/因果の専用規定は見つからず(ヒットは分割位置・Main Story・A2 Voice等、別論点)。
- 【確認】AMBIGUOUS見出しの「断定禁止、曖昧さを保持すること」は決定論で付与(L288)。

## D. Writer側の台帳の使い方
- 【確認】Storyline/B3(`er019_family_x_storyline_b3_fact_selection_01.py`)は台帳全文を渡して全fact_idをテストし`selected_fact_ids`を選ぶ。「Ledgerに存在しないfact_idを作らない」+ validate(L81, L155-176)。fact_id抽出は`FACT_ID_LINE_RE`(L129、文字種 `[A-Za-z0-9_-]`)。
- 【確認】JA Writer後のdeviation checkと must_fix Rewriteへは台帳全文(`full_ledger_text`)をそのまま渡す。must_fix文言「Ledgerにない断定・因果・数値・主体・時期・比較・否定・一般化を残さない」(`er019_family_x_ja_writer_o_r1_r2_01.py` L132-133)。EN Writer stageも`ledger_text`全文(runner L386, L397)。
- 【確認】notes_for_writerは台帳txtにそのまま含まれ、Writer・Checkerの両方へ渡る。Writer自体への「推測禁止」指示の逐語は上記must_fix文言とJA writer promptの有無を本調査では全文確認していない【未確認】。

## E. fact_id参照箇所と変更影響
参照箇所【確認】: ①`SAFETY_CRITICAL_CLAIM_DEFS`(`er052_open233_self_recovery_flow_runner_01.py` L9817-、`related_fact_id`例 MUSE-HC-006/HC-012/HF-003/HF-007) ②Checker r3出力`support_fact_ids`/`ledger_quotes`(逐語引用が台帳本文に存在する必要、`er052_open233_stage1_coverage_checker_01.py` L224-226,L275-280) ③Stage2候補`related_fact_id`(カンマ・空白区切りの複数可、L224-226,L600) ④`floor_verify_fact_block`(runner L3003-3024、見出し規則V1/V2でfact_id→ブロック逐語取得、無ければ確認不能=None、全文へはフォールバックしない) ⑤`ledger_fact_blocks`(checker L174) ⑥B3の`selected_fact_ids`と全fact test ⑦fixture台帳(er019_output/*/ledger、reuse_source.jsonにsha256)・gold・labels(`MUSE-HC-012`は23ファイル65箇所で参照)。

| 変更案 | 壊れる/影響する箇所 |
|---|---|
| ID維持・本文のみ明確化(HC-012の文言を直す) | ID参照は壊れない(②③④⑥⑦のID部)。影響=逐語`ledger_quotes`が旧本文基準のgold・既存labelsと不一致、`SAFETY_CRITICAL_CLAIM_DEFS`のtext_substringは記事側のため無影響、台帳sha256変化(fixture再現性・過去Trialとの比較条件が変わる)、Checker判定基準が変わるため過去実測(HC-012/A5-0等)との比較が不連続になる。 |
| 子ID分割(HC-012→HC-012a/b、親削除) | 上記全部+親ID参照が全て無効: gold/`related_fact_id`(floor_verify_fact_blockが親IDで見つからず=確認不能→floorが機能しない)、labels、B3全factテスト(fact数が増え`missing_ids`検証がfact_tests全件を要求、L165)、Checker`support_fact_ids`のlabel照合。 |
| 子ID分割+親IDを残す(親=原文、子=明確化版を追加) | 親参照は無傷。fact数増(B3 fact_tests/Writer入力量増)、同内容が親子で重複しWriterが両方を拾う余地、Checkerの`related_fact_id`先頭1件しか使わない箇所(runner L670-684近似)で子が見落とされうる。ID形式`MUSE-HC-012a`は正規表現上は有効(`[A-Za-z0-9_-]`)。 |
- 【推測】ID維持・本文明確化が参照整合上は最小影響。ただしID維持でも「Fact数不変・fixtureのsha256変化」は発生する。

## F. 安全経路(fail-safe位置)
- 【確認】分岐点候補: ②Verification直後〜③`build_verified_ledger_text`の間(draft JSON+verdictが揃い、txtを書く前)。ここで明確化に失敗(API失敗/schema不一致/検証NG)したら従来の`build_verified_ledger_text`出力(既存挙動)で`verified_fact_ledger.txt`を書けば従来台帳のまま進行できる。runnerは既に「txtが既存なら再利用」「verdict欠落はAMBIGUOUS」という安全側の既存挙動を持つ(L92-97、L282-287)。
- 【確認】明確化後txtをfixture/既存台帳に適用する場合は、旧txtを別名保持(sha256記録済の既存方式)で戻せる。【推測】新規生成のみ対象にする案は既存fixtureに影響しない。

## G. 費用・時間
- 【確認】台帳生成現状=約¥28.7・約149秒/run(A参照、web search込み)。web検索が費用主因【推測: 入力token大・検索7回×2段】。
- 【推測】明確化を追加する場合: 台帳全体1回(Webなし、入力≈draft JSON数k〜十数k token+出力≈台帳量)なら、Writer系の1call(例 ja_original ¥0.2〜0.9、cost.json by_stage)と同オーダーの¥1前後・30〜60秒増。fact数15件×1callなら15倍で¥10〜15・並列化しても数十秒(いずれも実測なし、設計で確定要)。Web再照合を伴う検証を追加する場合は既存Verification相当(¥14.3/63秒)増。

## H. Prompt改善のみで足りるか(事実のみ)
- 【確認】Prompt変更だけで済む範囲: Researcher promptへの観点追加(L152-157に1項目追加)・ambiguity/notes_for_writerの記入指針。ID・fact数・txt形式・参照箇所は変わらない。ただし台帳生成は約¥28.7/runかつ新規生成のみ(既存fixtureは再利用経路でpromptが効かない、L92-97)。
- 【確認】prompt外の手を入れる必要がある範囲: 既存fixture台帳の書き換え(sha256・gold/labels整合)、fact分割時のID整合(E表)、明確化結果の検証(現状は台帳段にAI再照合しかなく、明確化後の本文と原資料の一致を見る工程が無い)、fail-safe分岐(F)。
- 【確認】既存検証(Verification AI+記事段のdeviation check/Stage1 Checker)は、明確化後台帳を原資料と照合する専用工程にはなっていない。

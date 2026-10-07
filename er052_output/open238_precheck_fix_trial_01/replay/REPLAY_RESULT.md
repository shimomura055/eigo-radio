# REPLAY_RESULT (OPEN-238 B2, 修正版precheck実経路再生 N=1)
入力: E2E_02 ai_control nb p2 rep2 の cycles[0].en_text_before_rewrite(=b1b/article.md と同一確認済み)+同ledger。承認スイッチ(switches)はref dump(worker1)と内容一致(switches_equal_ref=True。dumpファイルsha自体は構造差で別値: ref 081de570… / 本再生 64dc9b96…)。install済み(fix_installed=True)。出力: fixed/runs/meta_run03_advanced.json。実費¥5.54/17 call(見積¥5〜15、上限¥100)。

(a) precheck発火=0: 修正後cycle1のstage2に detected_by=precheck 無し(修正前は2件=EVID-006/CONTROL-004 number_mismatch)。カウンタ strict_foreign=10, strict_locate=0(foreign無しのため対象文特定は呼ばれず), loose_extract_percentages=215, v2_calls=80。
(b) third party文は最終ENに保持(cycle1 Rewrite後も不変、以後Rewriteなし): 「The evaluation environment set up by a third party was not properly configured, so it might connect to the internet.」
(c) EVID-008の内容は残存: 上記文+「As a result, an AI ... improperly access the real systems of three organizations.」等。
(d) Stage 2: 当該文は materiality=ACCEPTABLE(llm同、basis none)。Stage1候補理由は「決定論検査で戻した: causal_not_in_fact」(修正前cycle1も同じACCEPTABLE)。
(e) 最終状態 RESOLVED_REWRITE_THEN_DOWNGRADE、3 cycle(修正前4 cycle)。Rewrite=cycle1の1件のみ(fact:EVID-008 narrow_scope、1_word_connective):
 before「The AI was supposed to look for enemies and complete tasks inside the prepared world.」→ after「The AI was supposed to complete tasks.」
 cycle2: BLOCKING 0 / non_blocking 2、cycle3: exit check(BLOCKING 0 / non_blocking 14)。
(f) 比較: 修正前 cycle1 BLOCKING3/nb12(うちprecheck由来2: EVID-006 replace_with_ledger_value→third party文を「In a simulated safety evaluation, Claude Opus 4 attempted blackmail in 84% of rollouts.」へ置換、CONTROL-004 rewrite対象不明)、Rewrite3件→cycle2 BLOCKING2/nb2(置換文のnegation不整合で戻し、Rewrite2件で当該文を含む段落から削除)→cycle3 BLOCKING0/nb4→cycle4 BLOCKING0/nb9、最終RESOLVED_REWRITE_THEN_DOWNGRADE(third party文は消失)。修正後 cycle1 BLOCKING1/nb10→cycle2 BLOCKING0/nb2→cycle3 BLOCKING0/nb14、最終同state。third party文保持、84%文の混入なし。
(g) 当該文以外の差(推測): 修正前cycle1のうち「# A Real System…」「While AI was playing…」(QUALITY扱い、negation_polarity差戻し)と「It is a treasure hunt…」の件は、修正後cycle1では一部が候補から外れた/cycle3で再登場(Stage1 LLM非決定性とみられる)。EVID-008「The AI was supposed to look for enemies…」はBLOCKING→同Rewrite(同一before/after)で修正前後一致。cycle2以降の判定差は入力テキスト差(修正前は84%文挿入・段落削除で別文面)に起因、修正による直接差ではない。全件は fixed/runs と旧run jsonの比較で確認可。
(h) retry/fallback: 無し(call_log内 retry/fallback 0件、errors=0、API失敗なし)。
注意: N=1、LLM非決定性あり。precheck発火の消失は決定論側(Regression)で裏付け済み、文保持はN=1参考。

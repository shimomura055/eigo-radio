# A1 notes_for_writer 伝達経路 事実確認 (OPEN-233-LEDGER-POLYSEMY-NOTE-DESIGN-01, read-only, 2026-10-06)

## 表: 工程 / 入力 / ファイル:行 / 根拠
| 工程 | 入力(notes有無) | 場所 | 根拠 |
|---|---|---|---|
| Researcher生成 | schema notes_for_writer=string/null(自由文、required) | er003_v1_en_direct_vfl_01_generate.py:111,116,157,162 | "notes_for_writer": {"type": ["string","null"]} |
| Verification->txt化 | notesは非空なら常時出力(verdict無関係、REJECTED除く) | er003...:302-303 | if fact.get("notes_for_writer"): lines.append(...) |
| ambiguity_note | AMBIGUOUSのみ | er003...:300-301 | if verdict == "AMBIGUOUS" |
| B3 | 台帳txt全文を{ledger_text}で入力(notes含む)。notes転記指示は無い(grep notes 0件) | er019_..._b3_fact_selection_01.py:57,148-150 | "【Full Fact Ledger】{ledger_text}" |
| JA R0 | briefのみ([ニュース]+brief)。台帳txtは渡さない | er019_..._ja_writer_o_r1_r2_01.py:149-163 | prompt += "[ニュース]\n" + selected_fact_brief_text |
| JA R1/R2 | previous_response_id連鎖(or前記事全文)+REVISION_INSTRUCTIONS。台帳なし | 同:355-375 | fallback_user=f"以下の記事:\n\n{prev_text}\n\n{instruction}" |
| JA must_fix(Original/R2) | Fact Check MAJOR時のみ「Full Ledger原文(再掲)」=台帳txt全文(notes含む)を付加 | 同:125-145,404-413 | lines.append(full_ledger_text) |
| JA deviation check | 台帳txt全文 | 同:278,391 | run_deviation_check(client, full_ledger_text,...) |
| EN b1b/a2 | JA R2本文のみ。台帳なし | er012_..._runner_01.py:340-380; er003_v1_n3_01...:625 | generate_family_x_faithful_translation(ja_text, client=client) |
| EN deviation check | 台帳txt全文(検査のみ) | er012:382,415,478,509 | run_deviation_check(client, ledger_text, advanced_text...) |
| retry: EN paragraph retry | ja_textのみ+固定must_fix。台帳なし | er012:~360-372 | generate_...(ja_text, must_fix=_FAMILY_X_PARAGRAPH_RETRY_MUST_FIX) |
| retry: JA recheck(案B) | 同一brief+台帳(must_fix用)でJA O/R1/R2を再実行。briefは再生成しない | er012:581-655 | run_ja_writer_o_r1_r2(client, storyline_line, selected_fact_brief_text, full_ledger_text=ledger_text, original_must_fix=...) |
| --regenerate-stage | storyline_b3: 台帳全文でB3再実行/writer: brief+台帳(must_fix用)/advanced,standard: ja_textのみ | er019_..._production_runner_01.py:336-399 | 同上 |
| Checker後Rewrite(er052) | E1テンプレに[Verified Fact Ledger]全文+対象文+issue+rewrite_hint。hintにLedger notes_for_writer(400字上限)合成 | er052_..._runner_01.py:4572,6302-6335,3274,3635-3648 | "Ledgerのnotes_for_writer: " + ... [:400] |
| Rewrite後再Check | 台帳全文でChecker再実行 | er052:6462,6660 | ledger_text=fixture["ledger_text"] |
(L:行は概数、grepで確認した行を記載。EN/Rewriteの網羅はコード読みのみ=実行ログでの確認ではない)

## P-TRIAL-01実証 (er052_output/open233_ledger_clarity_p_trial_01/after_pprime_01/)
- research_ledger/verified_fact_ledger.txt:47 に「notes_for_writer: 語義: 原語=rolled back this feature ... 「当面」または「for now」」あり(txt側は届いている)。
- storyline_b3/selected_brief.md:9 「human concierge機能を当面ロールバックした」。「語義:」「原語=」の文言自体は転記0件。原語と「当面」は内容として反映(B3がLLM要約で取捨)。
- ja_writer/revision2.md:17 にも「human concierge機能を当面ロールバッ…」(JA側はbrief経由で反映)。original.md:11 も同系統。
- raw_usage_log.jsonl(23行)はメタ(トークン等)のみでprompt本文なし。B3/Writerへ実送信した入力の逐語確認は「未確認」(コード上はB3=台帳全文入力、R0=briefのみ)。
- 台帳にあるnotes全部がbriefへ載る保証は無い(briefはB3が3〜5件に絞って作文)。

## 判定
- (a) YES: notesは非空なら常時txt出力(er003:302)。空はnull時のみ出ない。
- (b) B3 prompt台帳全文を見る=YES / briefにnotesが届く=部分的(転記指示なし。P-TRIAL-01では内容は反映・文言は非転記。保証なし)。
- (c) NO: JA R0は台帳全文を見ない(briefのみ)。
- (d) 部分YES: R1/R2通常=NO。must_fix発動時(Fact Check MAJOR)のみ台帳全文を見る。deviation checkは常にYES(検査用、生成ではない)。
- (e) 生成=NO(JAのみ)。検査=YES。
- (f) 部分: JA recheckは同じbrief+台帳(must_fix用)。EN retryはja_textのみ。regenerate B3は台帳全文で再実行。
- (g) YES(Rewrite時): 台帳全文+rewrite_hint内notes(400字上限)。ただし対象箇所のみの局所Rewrite。
- (h) YES(コード上): schemaは自由文string|null。Researcher prompt(er003:157,162)の文言変更だけでFact本文・schema不変。ただし(b)(c)の届き方は変わらない。

## STOP判定
- (b)〜(d)全てNOではない。届く経路: (1)B3経由でbrief内に載る(確率的)、(2)must_fix時のR0/R2へ台帳全文、(3)Rewrite時の台帳+hint、(4)Checker(検査)。
- ただしJA R0/R1/R2初回生成は台帳notesを直接見ず、briefに載らなければ届かない。「notesだけで確実にWriterへ届く」は成立しない(B3任せ)。確実化にはB3 prompt変更(転記指示)等が必要=Production仕様変更に該当し得るため、設計側でSTOP要否を判断(私は実装せず)。

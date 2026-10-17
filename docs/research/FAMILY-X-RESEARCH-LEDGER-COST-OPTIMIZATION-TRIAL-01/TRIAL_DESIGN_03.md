# TRIAL_DESIGN_03(TRIAL_DESIGN_02からの差分のみ。最終B3確認パス追加)

> 管理ID: FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 / 委任_07(2026-10-17、JPY0、harness是正+dry-runのみ)
> 根拠: ユーザー判断#107(選択肢(b)正式承認。原文=`docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_DESIGN-FIX-1B_USER.md`)
> 性質: **Trial専用harness(`er082_rlct_trial_01_*.py`)の設計是正。新しいProduction仕様の採用ではない。** 既存Family X仕様「AMBIGUOUSは断定禁止」「REJECTEDは使用禁止」を、案2/案1+2のTrial内でも守るための是正。
> Status上限: `HARNESS_CORRECTED_DRYRUN_PASS_PENDING_OPUS_A`。Opus独立技術レビュー(11-3 条件A、LLM出力を後段で解釈し再度LLMへ返す処理フローの変更)通過前に有料実行しない。
> 本書はTRIAL_DESIGN_02(v2)の項番に対する差分。記載のない項(4-1のM0/M0b/M0p/M1定義、4-2のVerifier複製、4-5契約検証、4-7隔離、4-8のSTOP条件など)は02のとおり。

## 0. 是正の理由(測定された事実)
- Stage 1a評価(`STAGE_1A_EVAL_01.md`、`RESULT_PACKET_RLCT6.md` L5-6): 02の4-3は「AMBIGUOUSは再選定トリガーにしない」「REJECTEDが出なければ検証前のB3がそのまま確定」だった。inbound M2/M3は再選定0回で、検証前に選ばれたBriefが確定し、F05(AMBIGUOUS)が断定されたまま残った(中心Fact断定1件。Brief全文がM2/M3で同一)。
- ユーザー§2(逐語): 「選定Factの検証完了後、最終B3の確定前に検証結果との整合を必ず確認すること。」「REJECTEDを単純削除しただけの不完全なBriefや、AMBIGUOUSを断定したBriefを最終確定してはならない。」「再選定上限は既存Trial設計の最大2回を維持する。上限到達時に品質条件を満たせなければ未成立として扱う。」
- **02 4-3の「AMBIGUOUSは再選定トリガーにしない」は本書D1で廃止(置換)する**(ユーザー#107による明示変更)。それ以外の4-3(1〜6、REJECTED機械削除禁止、最終Ledgerは選定Factの検証済み分のみ)は維持。

## 1. 設計差分 D1〜D5(`select_then_verify`、lib.py)
**D1 確定条件**: 各roundで選定Factの検証後、次の両方を満たすときだけ`_finalize_sel`へ進む。
 (i) 選定FactにREJECTEDが無い。
 (ii) 選定FactのうちAMBIGUOUSの全てが、「そのselを生成したB3呼出」の候補Ledger上で既に`[AMBIGUOUS - 断定禁止…]`タグ+verification_notes付きで提示されていた(B3がAMBIGUOUSを知った上で選んだ)。
 選定Factが全てVERIFIEDなら(ii)は自動的に満たし、B3追加呼出なし(`confirm_pass="NOT_NEEDED_ALL_VERIFIED"`)。AMBIGUOUSが既提示なら`NOT_NEEDED_AMBIGUOUS_ALREADY_VISIBLE`。
 実装: `_ambiguous_unseen`(lib.py)と`select_then_verify`内の`confirm`判定。判定に使う「見えていた判定」は、B3呼出の直前に`copy.deepcopy(verdicts)`したスナップショット(`sel_visible`)。初回B3は検証前なので常に空。
 防御: `_finalize_sel`はREJECTED混入またはAMBIGUOUS未提示を検出したらAssertionError(構造上起きないはずの実装バグ検知)。
**D2 確認パス**: (i)(ii)のどちらかを満たさないとき、既存の再選定入口`select_b3_trial(... extra_note=...)`でB3へ返す(新しいB3関数は作らない)。noteは`build_confirm_note(rejected, ambiguous_new, verdicts, draft, unverified_ids)`。
 - REJECTEDのみ: 既存`build_reselect_note`と同一文面(02の再選定と挙動不変)。
 - AMBIGUOUS(未提示分)を含む場合: ①REJECTED各ID+理由+「選定禁止」 ②AMBIGUOUS各ID+verification_notes+使用上の制約「このFactを使う場合、Storyline・Briefでは不確実性・留保条件を明示し、無条件の断定をしてはならない」 ③検証済み他Factの判定 ④未検証候補一覧+「新たに選んだFactだけを選定後に独立検証します」 ⑤「Storylineの構成を再評価し、必要ならFactを選び直してください」。
 - 候補Ledgerは`render_candidate_ledger(draft, verdicts)`で現在の判定タグを反映(REJECTEDは本文から外す=02どおり)。B3 Prompt本体・Developer message・出力schemaは02と同一(`allow_unverified=True`の語置換のみ)。
 - 新規選定Factだけ検証(検証済みは`verdicts`から再利用。cap有無はmethodに従う)。
**D3 回数上限**: 初回B3後のB3呼出(REJECTED起因の再選定+AMBIGUOUS起因の確認パス)を**合算して最大2回**(`max_reselect=2`)。2回使い切っても(i)(ii)未達なら`UNRESOLVED / RESELECT_LIMIT_REACHED`(`unmet=["REJECTED_SELECTED"|"AMBIGUOUS_NOT_CONFIRMED"]`)。確定ファイル(`research_ledger/`、`storyline_b3/`)は出さない(02 4-3維持)。品質条件の緩和はしない。
**D4 記録**: `rounds[*]`に`trigger`(`INITIAL`/`RESELECT_REJECTED`/`CONFIRM_AMBIGUOUS`/`RESELECT_REJECTED+CONFIRM_AMBIGUOUS`/補正時`RESUMED_FROM_SOURCE_FINAL`)、`b3_label`、`ambiguous_selected`、`ambiguous_unseen`、`ambiguous_visible_to_b3`、`confirm_pass`。`result.json`の`reselect`に`reselect_count`(REJECTED起因)/`confirm_pass_count`(AMBIGUOUSのみ起因)/`b3_calls_after_initial`(合計)/`b3_calls_before_this_run`/`final_confirm_pass`/`unmet`。REJECTEDとAMBIGUOUSが同時に原因のB3呼出は`reselect`に計上。費用はstage_tag(`b3_initial` / `b3_reselectN` / `b3_confirmN` / `verify_sel_rN`)で分離され、aggregateが「再選定B3 JPY」「確認B3 JPY」列で別掲(§5「再選定・最終B3確認パスの追加費用」)。
**D5**: UNKNOWN_FACT_ID検知・`B3_TECHNICAL_FAILURE_REJECTED_ID_RESELECTED`は無変更。REJECTEDは候補本文から外れるためB3が選ぶとID検証エラー=02と同じ入口。

## 2. 1a補正(D6、`er082_rlct_trial_01_run.py` `--correct-from M2|M3|M2,M3 [--correct-source-root ROOT]`)
対象=Stage 1a inbound_tourismのM2/M3(適合照合D7でFAILの方式のみ)。出力method名`M2c`/`M3c`。
1. **既存`<article>/M2`,`M3`は一切変更しない**。`ROOT`(既定=`--out`)は読み取り専用。`M2c`/`M3c`だけを新規作成(`mdir`が既存ならSTOP=有料二重実行防止。補正元と出力先が重なればSTOP)。
2. 復元(`_restore_source`): ①`M2/_work/initial_b3.json`(M3cもM2の初回B3を共有=02 4-1維持、sha256を`reused_initial_b3_sha256`に記録) ②元methodの`_work/verify_r*.json`の`parsed`からverdict+verification_notes+round番号を復元(`result.json`の`final_verdicts`と全件一致を確認。不一致・欠落はSTOP、推測で補わない) ③最終selを生成したB3の保存物(初回=`initial_b3.json`、以降=`b3_<label>.json`)で選定Fact一致を確認 ④sel生成時の候補Ledgerに見えていた判定=`round < 最終round`で検証されたFact。
3. `select_then_verify(resume=…)`: D1判定→(必要なら)D2確認パス→新規選定Factのみ検証(capは元methodに従う)→D1→確定/未成立。**元の追加B3呼出回数(`len(rounds)-1`)は上限2回に合算**(inbound M2/M3は0なので残り2回)。
4. `result.json`: `corrected_from`, `reused_initial_b3_sha256`, `reused_verdict_ids`, `pre_correction_selected_fact_ids`, `pre_correction_storyline_sha256`, `pre_correction_brief_sha256`, `brief_changed_vs_pre_correction`, `cost_correction_only`, `cost_production_equivalent{source_method_total_jpy, correction_total_jpy, total_jpy}`。Budget stage tag=`1a`(1a上限493の残で管理)。
5. 有料実行コマンド(**Opus条件A後の次委任のみ**): `.venv\Scripts\python.exe er082_rlct_trial_01_run.py --paid-confirm <TOKEN> --article inbound_tourism --correct-from M2,M3 --out er082_output/rlct_trial_01 --other-spend-today-jpy <当日他支出>`。
6. 修正前後の差(Brief・採用Fact・品質・費用)は、`M2`↔`M2c`・`M3`↔`M3c`をaggregateが並記し、構成差/品質は`STAGE_1A_EVAL_01.md`と同じ手順(ブラインド・3段階、構成差と品質は別軸)で再評価する。

## 3. Coffee適合照合(D7、JPY0、`er082_rlct_trial_01_conform_check.py`)
全12 method(1a: coffee/inbound × M0,M0b,M0p,M1,M2,M3)に`conform_d1 = PASS|FAIL|N/A`を付ける。M0/M0b/M0p/M1はN/A(全Fact検証後にB3を呼ぶため)。M2/M3は`reselect.rounds`で、最終selを生成したB3呼出の候補Ledgerに選定AMBIGUOUSが見えていたかを判定し、保存済みB3 promptの`[AMBIGUOUS`タグで裏取りする。結果(`_conform_check_1a_01.json`): **Coffee M2/M3=PASS(選定Fact全てVERIFIED。再生成不要)、inbound M2/M3=FAIL(F05 AMBIGUOUS、初回B3では[UNVERIFIED]で提示)**。

## 4. 1b手順(ユーザー§4。02の4-8 CP3を以下で置換)
- 別JST日(2026-10-18以降)。順序: streaming_price → openai_copyright → central_bank_mortgage。各記事M0,M0b,M0p(streamingのみ),M1,M2,M3(PLANどおり)。M2/M3は新設計(確認パス込み)として通常列。
- 実行: `.venv\Scripts\python.exe er082_rlct_trial_01_run.py --paid-confirm <TOKEN> --plan 1b --out er082_output/rlct_trial_01 --other-spend-today-jpy <当日1b以外の支出>`(Fableが当日実績を渡す)。実行は1記事ずつ区切り、記事単位でFable確認を挟む。
- 比較表はM0(過去Production基準)/M0b(B3自然ばらつき)/M0p(同日・上限なし再検証。B3を含まない限界あり=M0pは完全な同日E2E基準ではない)/M1/M2/M3を分けて報告。**案1の3回上限の効果は、検索削減をそのまま上限の効果と断定しない(Fact別の上限到達はソフト上限のためログからの推定)**。検索ツール呼出回数・クエリ数・LLM費用は別列。
- Verifier判定ばらつき(M0p含む)と方式固有の問題を区別し、Coffee F12・inbound F12等の既知誤判定は原因・影響・最終採用の有無を記録(Production Verifier改修はしない=OPEN-409)。
- 任意A(故障注入)は承認済み範囲を維持。Coffeeは実施済み・再利用、未実施分は承認枠JPY54内。任意B/C/Stage 2は自動実施しない。

## 5. 費用見積の増分
- B3 1回の実測単価(`er082_output/rlct_trial_01/raw_usage_log.jsonl`、`lib.cost_by_stage_tag`): inbound `1a|inbound_tourism|M0|b3`=JPY8.465, `M0b|b3`=8.328, `M1|b3`=10.102, `M2|b3_initial`=10.467(同M2/M3のB3入力は約5.4k token)。確認パスのB3はnoteで入力が約+0.5〜1k token増えるため**1回約JPY11**(出力token次第で8〜12)。
- 1a補正(inbound M2c/M3c): 各B3確認1回≒JPY11 + 新規Fact検証(B3がF05以外を選んだ場合のみ。1検証=web_search 4〜5回≒JPY7〜9、`M2|verify_sel_r0`=7.311, `M3|verify_sel_r0`=9.001) → **期待 2×11≒JPY22(ユーザー見込み約22と一致)、新規Fact検証ありで最大約JPY40、確認パスが2回なら最大約JPY60**。1a残=493−212.80=JPY280.2(余裕あり)。当日(JST 2026-10-17)既使用約JPY284.1(ACTIVE_TASK.md L4)に加算しても1,000円内。
- 1b増分(02のCOST_ESTIMATE_02: 期待235.0/上限493.3に対し): 3記事×(M2+M3)で確認パスが各1回発火すると+6×11≒JPY66、新規Fact検証を加えて約+85。全て2回発火なら約+130〜190。**上限(1b=493)内に収まらない見込みが生じた場合は実費ガード(`Budget`)が呼出前に停止する=STOPして報告**。1bは別日実行なので日次1,000円のsoftは別枠。Trial全体上限JPY1,040(1a+任意A実測223.7 + 補正≦60 + 1b ≦493)は守れる見込み(223.7+60+493=776.7)。
- 本委任のdry-run費用=JPY0(StubClient、`raw_usage_log.jsonl`への追記なし、`dryrun_summary.json`の`real_usage_log_rows`=0)。

## 6. test / dry-run(委任_07の検証)
`er082_rlct_trial_01_test_01.py`にtest_r1〜r7を追加(合計25件)。StubClientに`b3_script`(B3呼出順に返すFact ID列)を追加して確認パス経路(AMBIGUOUS判定・新規Fact選定・2回目確認・上限到達)を再現する。既存test_e/e2/f/j/n/qは維持され全PASS。

## 7. Opusレビュー観点案(条件A)
1. D1(ii)の妥当性: 「AMBIGUOUSが候補Ledgerに見えていた」だけで十分か。B3が見た上でなお断定する危険は残る(機械判定不能。中心Fact断定の人手判定=R-07を継続)。
2. 上限合算(再選定+確認パス=計2回)の妥当性: 確認パスがREJECTED再選定の枠を食い、本来成立し得た記事が未成立になる懸念。
3. UNRESOLVED時の安全側: 確定ファイル無し・品質条件緩和なしで足りるか。
4. 1a補正の再利用忠実性: verify_*.jsonから復元した判定をそのまま使い、B3はsel生成時と同一Prompt/modelか。再実行時のWeb更新・Verifierばらつきは扱わない(判定は再検証しない)。
5. M3cがM2の初回B3を共有してよいか(M2cとM3cのB3確認は独立呼出になり、相関はM2の初回選定経由のみ)。
6. 確認パスの介入自体がB3構成を変える(特に新規Fact選定)ため、構成差と品質低下を混同しない評価手順。

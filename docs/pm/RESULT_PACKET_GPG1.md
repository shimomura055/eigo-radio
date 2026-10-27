# RESULT_PACKET_GPG1(GRAMMAR-PREGEN-ALL-LEVELS-01 委任_01、一時ファイル・正式記録ではない)

到達Status: **DESIGN_READY**(read-only・コード/SSOT編集なし・API 0・JPY0)。次=Opus条件A(`OPUS_REVIEW_REQUEST_01.md`)。成果物=`docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/{CURRENT_FLOW_01,ADV_ONLY_INVENTORY_01,DESIGN_01,IMPL_PLAN_01,TEST_PLAN_01,EVIDENCE_PLAN_01,COST_ESTIMATE_01,OPUS_REVIEW_REQUEST_01}.md`。基準=`origin/main`/HEAD 44f3b48d7(文法関連fileは93915b971以降差分0)。

## (0) T-0
- 委任文: jsonl index N=711を採用(先頭「## 管理ID」+「GRAMMAR-PREGEN-ALL-LEVELS-01 委任_01」一致)→`docs/pm/delegation_log/2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_DELEGATION_01.md`。ユーザー原文逐語→`..._USER.md`(委任文18-244行を転記)。
- check結果1行: `check_delegation_prompt.py` **status=FAIL(rc=0)** 理由=「事前指定Grep一覧+追記位置・更新位置の手順」キーワード欠落(委任文は「事前指定Read一覧」内にSSOT Grep指定を含み実質的に充足。キーワード見出しの不在のみ。warning=Opus台帳更新の記載なし)。固定ブロックE-1/D-1/G-1/F-1=全てOK、実行コマンド検査=missing 0。check.json=`..._DELEGATION_01_check.json`。委任実行は継続(軽微な見出し不足で作業は妨げない)。
- stop_scope_check: `tools/stop_scope_check_01.py --managed-id GRAMMAR-PREGEN-ALL-LEVELS-01 --run-dir <scratch空dir>`を実行 → rc=0(stop=false、唯一のNOTICE[2026-10-12 FAMILY-Z-MELOS-SOL]は非適用)。run-dirを持たない作業のため`--run-dir`はscratchの空dirを指定。STOP_ALL不在。本作業はread-only・API 0。

## (1) 現行フロー要点(詳細CURRENT_FLOW_01)
- 共通核=`er120_part2_grammar_production_01.py`(Prompt sha固定・`LEVEL="Advanced"`:42)/`er119_grammar_review_01.py`(`LEVEL_KEY="b1b"`:24)/`er120_part2_wiring_01.py`。X/Y/Zとも**Advのみ**: 候補抽出(Step A''、KP候補生成の前)→HR(英文1つ選択、構文名/教える価値のみ提示=**解説本文なし**)→Part 1後にStep B(選定1件のみ)→Part 1直後に1ブロック。
- Std(a2)は候補抽出・HR・Step B・ページブロックのいずれも無し。Stdの節には学習テキストブロックが無い(Part 1もAdvのみ)。
- 共有ページ構造(`er_user_listening_page_common_01.py:51-70`)はlevel別`study_html`を既に受ける → Stdへの追加は条件(Y:1113 / Z `er063:2588` / X `build_player_html`:3022・player:3649)を外し`compose_study_html`を再利用すれば足りる。Xのみ公開ページが記事別script(共通builderなし)=Family差。
- 実測(既存run): 候補数 X平均3.0/Y約2.3/Z約0.73(Adv)、Step B JPY0.05-0.11/call、Step A'' JPY0.26-0.88/call(`gpt-6-luna`)、候補文とPart 1引用文の重なり0/28。**Std候補数は未観測**。

## (2) Advanced限定の棚卸し(詳細ADV_ONLY_INVENTORY_01)
- **重要事実**: 「Part 2はAdvancedのみ」はユーザー原文(2026-10-25 `..._PART2-GRAMMAR-PRODUCTION-WIRING-01_USER.md`:90は「Standard／Advancedなど」)ではなく**AI設計判断**(`PART2-GRAMMAR-PRODUCTION-WIRING-01/DESIGN_02.md:5,77`、`er120:42`コメント、`DECISION_LOG.md:21`)。今回のユーザー決定で置換。
- **更新**: CURRENT_SPEC:2099、OPEN-519本体の「Advancedのみ/Standard非適用」、OPERATIONS_01:133、KCP DESIGN_02 §10-1/付録3(`stepB_generated_frozen`前提→事前生成+`form_displayed`)、コード条件C1-C8(`LEVEL`/`LEVEL_KEY`/`pending_summary`/`discover_dirs`/stage名/Xの`b1b`条件(:760,:3525,:3548,:3585,:715,:3649)/Y(:34-48,:583,:1016,:1113,:925)/Z(:1554-1566,:2307,er063:2588,er062:64-72)/er128:848,1253,862)、統合依頼書/banner/CLIのlevel表示、test T1-T7、Validator `require_fresh_part2`等。
- **撤去(置換)**: `FAMILY_Y_PART2_ON_STANDARD_PAGE`(Y:945)/`FAMILY_Z_PART2_ON_STANDARD_PAGE`(Z:1708)→「自levelの節にだけ」検査、`parser.error` Adv限定(X:3548)、`run_part2`内の選定後Step B(er120:1202)。
- **履歴化**: CURRENT_SPEC:3104、DECISION_LOG:21、DESIGN_02.md、RESULT_PACKET_YPL9。**解消**: UDR-FORM-1。
- **維持**: Part 1のAdv限定(CURRENT_SPEC:2080、er119:525、er003 Part 1 test)=今回の対象外、Prompt/閾値/`_run_llm`のretry/モデル不一致STOP、reselect/reextract上限、`er119_isolation_test_01`。
- 現行コードGrep(未編集の事実): `ON_STANDARD_PAGE` 2件/`Standardには出さ` 1件/`Advanced=b1bのみ` 5件/`LEVEL = "Advanced"` 1件/`LEVEL_KEY = "b1b"` 1件/`label == "Advanced"` 1件/`== "advanced" and study_html` 1件/`generate_explanation(`呼出 1件(`run_part2`内)。実装後は上記が置換済みになること(IMPL_PLAN §4)。

## (3) 設計要点(詳細DESIGN_01)
- (a)工程順: 候補抽出 → **全候補Step B事前生成(新、`grammar_explanations.json`、上限`PREGEN_MAX=8`、直列、`explain_signature`一致で再利用)** → 統合HR/フォーム(文法名+解説全文) → 最大2件確定 → 凍結 → finalize(**LLM 0 call**) → 公開(Adv=Part 1直後、Std=Stdの節に文法のみ)。Std候補0件=正常(`NO_CANDIDATE_UNREVIEWED`・固定文面)。
- (b)重複防止: Step B呼出点を`pregen_stage`1か所に集約、`run_part2`/finalizeは生成せず無ければ`Part2Stale`(旧runのみ`legacy_postselect`)。`--regenerate-stage`行列(未確定/確定済み)。run内Step B総数=候補数をspy testで固定。
- (c)HR/フォーム: 提示物を`form_grammar_items`(`{id,title=construct_ja,body=explanation_md,example}`)に一本化。HR CLIは`pick --ids`、依頼書に解説全文。フォームは文法`body`/`grammar_status` 3値(`no_candidates_found`追加依頼)。選定基準(Trial-08 Tier順位)は無変更、AI推奨=rank1。
- (d)Family共通核: 核を`level`引数化、X/Y/Zはadapter(入力本文・stage台帳・ページ差込)のみ。study dir: Adv既存path不変/Std=`<out>/a2/study_text`。Y/Z provenanceに`part2_{cand,expl,}_a2`等を追加。
- (e)KCP M6接続: `explanations_sha256`を`decision`に固定、`cmd_from_form`に文法照合(id/title/body一致/件数<=2→不一致はISSUE)、level別sidecar、凍結v2(`items[]`、v1読取互換)、`guard_grammar`をStd/`part2_expl`にも適用。
- (f)Trial-08: Prompt/`eligible7`/`select_tiered`/`rank_eligible`無変更、提示物に解説全文が加わるだけ。(g)費用: 下記。(h)旧参照: ADV_ONLY_INVENTORY §1,§6。
- **Fable設計判断事項(推奨付き、いずれも承認範囲内・新仕様ではない)**: D-a Prompt無変更でStd本文へ適用(推奨)/D-b 事前生成失敗はSTOP・再開で未生成分のみ(推奨)/D-c `PREGEN_MAX=8`/D-d StdのZEROも同一固定文面/D-e 2件の表示順=本文出現順/D-f 事前生成は`ref_ja=None`(重なり稀、食い違いはKCPのISSUE)/D-g Std文法ブロックはStd節に差込/D-h auto=TOP1のみ。

## (4) 計画・費用
- 実装(IMPL_PLAN_01): F-1共通核→F-2/F-3並行→F-4X/Y/Z並行→F-6(KCP改修、KCP/FORM所有fileは担当確認)→F-9 evidence→F-10 SSOT。クリティカルパス約12h(直列24h)。新flagなし(承認済みProduction配線)。
- test(TEST_PLAN_01): T1-T15(Trial-08回帰/重複防止spy/事前生成/pick/結果v2改ざん検出/描画golden/HR/Family負例/KCP/隔離/retry行列/フォーム契約/費用/Dangling Grep)+回帰一覧。
- evidence(EVIDENCE_PLAN_01): 方式A=既存KP75 evidence runのcopy-runで3run x 両level=6経路、本文・音声再利用、**見積JPY12-27・上限JPY40**。Std候補率を既存Std本文<=8本で計測。方式B(新規記事E2E)は別Scope。
- 費用(COST_ESTIMATE_01): 実測ベース増分/記事セット X約JPY0.9・Y約0.8・Z約0.34(70円目標比0.5-1.9%)、ユーザー式(JPY0.3x候補数)保守でX約2.7・Y約2.1・Z約0.9(<=約4%)。Std候補数は未観測(evidenceで計測)。

## (5) Opus論点(OPUS_REVIEW_REQUEST_01の10観点)
1工程順変更の副作用(位置・直列/並列・ref_ja喪失)/2Std本文への候補抽出の妥当性(Prompt無変更)/3事前生成とM6凍結の整合(v1互換・atomic適用・据え置きinput_sha)/4重複生成防止(`legacy_postselect`の抜け穴)/52件採用の公開表示と選定モデル/6Family差解消とadapter境界・検査力維持/7費用外挿/8evidence十分性(方式A)/9旧仕様撤去・Dangling/10A/B/C隔離。

## (6) 判断候補
- **ユーザー判断が要る新仕様事項: なし**(D該当なし)。以下はFable判断(区分B=承認範囲内で自己解決可)で、念のため記載:
  - 判断候補1(区分B): evidenceの「正式初回Production」を方式A(copy-run、<=JPY40)で満たすとみなすか、方式B(新規記事E2E、概算JPY200超)を別Scopeで行うか。推奨=A+Bは次の通常制作に相乗り。根拠: ユーザー§8-1/§9(不要な再生成を避ける)、先例KCP/KP75 evidence。
  - 判断候補2(区分B→Dに転じ得る): Std候補の質が許容外(偽陽性/ZERO常態)とevidenceで判明した場合のみ、Promptのlevel差込(sha変更=Production Prompt編集)が別承認事項になる。現時点は推奨D-a(無変更)で進め、事実を報告。
  - Fable確認事項(新仕様候補ではなく意図確認): Std学習ページが「文法のみ(Part 1なし)」になる点(DESIGN §7 Q3)。Part 1をStdへ広げる提案はしない。
- 新規OPEN分類: GRAMMAR-PREGEN-ALL-LEVELS-01 = **修正へ進む**(同一承認内で実装。次委任案は下記)。

## (7) 必須4行
(1) 既存仕様整合(照合したfile:line): 原文`..._USER.md`§1,§3,§5,§6 / `2026-10-25_PART2-GRAMMAR-PRODUCTION-WIRING-01_USER.md:90` / `er120_part2_grammar_production_01.py:42,55,118,417,909,968,1117,1163,1272` / `er120_part2_wiring_01.py:26-27,111,237` / `er119_grammar_review_01.py:24,110,148,364,411` / `er128_kp_confirmed_content_01.py:835-1000,1244,1253` / X runner:628-720,760,3022,3525,3585,3649 / Y runner:34-48,583,848,925-947,1113 / Z runner:1548-1710,2275-2307,2408; `er063:2588`; `er062:64-72` / `er_user_listening_page_common_01.py:51-70` / CURRENT_SPEC:2096-2099,2080,3104 / DECISION_LOG:21 / OPEN_ITEMS:1034 / USER_DECISION_REGISTER_01.md:489 / KCP DESIGN_02 §10・付録 / FORM DATA_MODEL_02.md §B,C。
(2) Production到達経路に入る未承認機能の既定値: **本委任はコード無変更のため入る機能なし**。実装時も新flagなし(ユーザー`APPROVED_FOR_PRODUCTION`の本配線)。確認方法=DefaultOff該当せず、`er119_isolation_test_01`(A/B/Cへ文法kindを持ち込まない)・Prompt sha不変test・既定=Human Review待機(rc=4)維持testで固定(TEST_PLAN T1,T11)。
(3) 失敗終了時の最終成果物: 本委任は正常終了(DESIGN_READY)。最終成果物=上記8文書+本packet+`..._USER.md`/`..._DELEGATION_01.md`(+check.json)。目的適合: ユーザー原文§1(全6経路・範囲を狭めない)に対し、Std/Advとも対象に含め、Advanced限定を維持する判定は文法解説について0(維持はPart 1のみ、原文が文法解説のみを対象とするため)。設計の失敗終了時成果物(事前生成STOP/ISSUE時の残存物)はDESIGN_01 §5に定義し、不完全なフォーム・部分公開物を出さない設計。原文取得済み。
(4) 撤去・残置した規則・検査・testの識別子と残存Grep: **本委任で撤去したものなし**(read-only)。撤去予定識別子=`FAMILY_Y_PART2_ON_STANDARD_PAGE`/`FAMILY_Z_PART2_ON_STANDARD_PAGE`/`parser.error` Adv限定(X)/`run_part2`内`generate_explanation`呼出/`m.LEVEL=="Advanced"`assert。残存Grep(HEAD、test除く、上記(2)末尾): ON_STANDARD_PAGE 2、Standardには出さ 1、Advanced=b1bのみ 5、`LEVEL = "Advanced"` 1、`LEVEL_KEY = "b1b"` 1、`label == "Advanced"` 1、`== "advanced" and study_html` 1、`generate_explanation(`呼出 1。実装後に置換済みを再Grepで確認(IMPL_PLAN §4)。

判定整合: 重大NG=なし

## (8) SSOT文案(編集権なし。Fable反映用)
- **OPEN新規起票文案**(番号はFable採番。仮=OPEN-559): 「**GRAMMAR-PREGEN-ALL-LEVELS-01 文法解説の事前生成(Family X/Y/Z x Standard/Advanced全6経路) [種別=ユーザー正式採用の実装、Status=APPROVED_FOR_PRODUCTION(2026-10-27、原文`docs/pm/delegation_log/2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_USER.md`)・DESIGN_READY(委任_01、Opus条件A待ち)・PRODUCTION_WIRED未判定(全6経路が揃うまで一括判定しない)、11-8分類=修正へ進む(次委任で実装)]** 旧Part 2『Advancedのみ・選定後に解説生成・最大1件』を、候補ごとの解説事前生成+最大2件選定+Std/Adv公開に置換。設計=docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/DESIGN_01.md、旧Adv限定棚卸し=ADV_ONLY_INVENTORY_01.md、費用=COST_ESTIMATE_01.md(増分実測JPY0.3-1.3/記事セット)。Advanced限定はユーザー原文に無いAI設計判断(DESIGN_02.md:5,77)でありユーザー決定で置換。関連: OPEN-519(Part 2)、OPEN-545(フォーム)、OPEN-556(確定内容保護)。」
- **CURRENT_SPEC旧記述の履歴化文案**(:2099の末尾に追記、本文は削除しない): 「【2026-10-27 GRAMMAR-PREGEN-ALL-LEVELS-01: 本節の『Part 2はAdvancedのみ』は旧AI設計判断(ユーザー原文に無し、DESIGN_02.md:5,77)であり、ユーザー正式決定により、文法解説は全6経路(X/Y/Z x Standard/Advanced)で『事前生成→フォームで選定(最大2件)→確定→公開』に置換される。旧記述は履歴。現行仕様=OPEN-559/DESIGN_01。Part 1(Vocabulary & Expressions)のAdvanced限定は変更なし】」。:3104(Y接続状況)・DECISION_LOG:21・OPEN-519本体も同旨の1行を追記。
- **UDR-FORM-1解消文案**: 「UDR-FORM-1=解消(2026-10-27ユーザー正式決定[GRAMMAR-PREGEN-ALL-LEVELS-01原文§3、全面修正版]: 文法候補ごとに解説全文を選定前に生成し、フォームで確認して最大2件を確定・公開する。Fable推奨(a)と同一方向)。UDR-blockingから除外」。
- **DECISION_LOG追記案**: 「2026-10-27 | GRAMMAR-PREGEN-ALL-LEVELS-01 委任_01(DESIGN_READY、API 0) | ユーザー正式決定(APPROVED_FOR_PRODUCTION)=フォームv3・文法解説事前生成(全6経路)・全候補AI理由・確定内容保護。調査: Advanced限定はAI設計判断と判明。設計: 事前生成+最大2件+Std適用(Prompt無変更)。費用実測増分JPY0.3-1.3/記事セット。次=Opus条件A→実装。」

## 次委任案(修正へ進む)
委任_02: Opus条件A反映→F-1(共通核)/F-2/F-3を実装(API 0、mock test)。委任_03: X/Y/Zadapter・ページ・Validator置換・test更新。委任_04: KCP/FORM接続(F-5/F-6、担当Agentとfile所有を調整)。委任_05: evidence(方式A、<=JPY40)→SSOT→Fable受入。並列化可能: F-2/F-3、F-4X/Y/Z、F-8 test。

## 原因仮説・根拠・次の一手(QDC記録材料)
- 仮説: 現行は「Part 2=Adv限定・選定後1件生成」の骨格が全層(核・HR・runner・ページ・検査・test)に散在、ただし共通核は`level`/件数の2軸の汎化で足り、ページ側は既にlevel別`study_html`を持つため、変更量は中(約12h wall)で済む。
- 根拠値: Step B JPY0.05-0.11、候補数X3.0/Y2.3/Z0.7、重なり0/28、共有page構造 `er_user_listening_page_common_01.py:51-70`、Advanced限定の出所=DESIGN_02.md:77。
- 前回との差分: 新規(本件初回)。次の一手: Opus条件A(改善見込み=設計欠陥の事前除去)→実装。回数を理由とした打切りなし。

## 末尾10行要約
1. 到達=DESIGN_READY(read-only・API 0・JPY0)。成果物8文書=docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/、packet=本ファイル。
2. T-0: 委任文N=711採用。check_delegation_prompt=FAIL(Grep一覧見出しの文言欠落のみ、実質充足)で継続。
3. 「Part 2はAdvancedのみ」はユーザー原文に無いAI設計判断(DESIGN_02.md:77)と判明、全6経路へ置換。
4. 新工程順=候補抽出→全候補Step B事前生成→HR/フォーム(解説全文)→最大2件確定・凍結→finalize(LLM 0)→公開(Std=文法のみ/Adv=Part 1直後)。
5. 重複防止=Step B呼出点をpregen 1か所に集約、旧run互換のみlegacy。M6凍結はitems[]化(v1互換)。
6. 共有ページ構造は既にlevel別study_html対応、Xのみ公開builderが記事別script(Family差)。
7. 費用=実測増分JPY0.3-1.3/記事セット(70円比<=1.9%)、保守<=約4%。Std候補数は未観測(evidenceで計測)。
8. evidence=方式A(copy-run、3run x 両level=6経路)JPY12-27、上限JPY40。
9. 判断候補=ユーザー判断が要る新仕様なし。Fable設計判断D-a〜D-h(推奨付き)、evidence方式A/Bの区分B判断。
10. 重大NG=なし。次=Opus条件A→委任_02(F-1〜F-3実装)。commit hash/raw URLは最終報告に記載。

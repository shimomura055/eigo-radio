# 04 Fact台帳 明確化 設計案(OPEN-233-LEDGER-CLARITY-DESIGN-01 委任_02、¥0、2026-10-06)
性質: 設計案。Status=DESIGN_READY_FOR_REVIEW(Opus条件A前)。実装・API・SSOT変更なし。【確認】=ファイル確認済、【推測】=未確認、【案】=原資料との意味一致を未照合。入力: 01_current_pipeline.md(以下①)、02_cases.md(②)、03_trial_eval_design_draft.md(③)(同ディレクトリ)。

## §0 要約
- 推奨: 案C+V(Verification直後に台帳全体1回の明確化パス+意味一致self-check)。ID・fact数は不変、1 fact内に`events[]`構造を持たせる。案S(子ID分割)は不採用。
- Opus反映(訂正、§13参照): 本番推奨経路は案C+VではなくP'(Researcher/Verification拡張、追加callなし)。案C+Vは既存台帳のoffline適用(Trial用)に限定。以下の「推奨: 案C+V」はSonnet初版の記述として残す。
- 期待効果: HC-012型(多義語)・HF-009型(途中/最終)のWriter誤読予防。ただし効果は未測定(Trialで確認が必要)。
- 費用・時間増【推測】: 案C≈¥1・30〜60秒、V追加≈¥1。台帳費¥28.7→約¥30.7(+5〜7%)。
- 重大な制約【確認】: 台帳JSONにsource原文quote欄が無く(`er003_v1_en_direct_vfl_01_generate.py` L91-116)、self-checkは「元claim等」との照合止まり。原資料(Web)との一致までは見ない(§5・§12の選択肢)。
- Status: DESIGN_READY_FOR_REVIEW→Opus条件A→USER_DECISION_REQUIRED(Trial承認・新Product仕様候補)。

## §1 現行仕様の確認(根拠=①)
- 工程: Researcher(Web、luna、`fact_ledger_draft.json`)→独立Verification(別call、Web、VERIFIED/AMBIGUOUS/REJECTED)→決定論`build_verified_ledger_text`(`er003_v1_en_direct_vfl_01_generate.py` L275)がtxt化→Storyline/B3(全factテスト、fact_id選択)→Writer→deviation check→Stage1/2 Checker→floor_verify。
- 台帳実測: 約¥28.7・約149秒/run(全体の64%)。fact数15(Meta)/12(Hormuz)/17(small_bag)。
- 既存ルール: Researcher promptに4観点(scope/適用条件/数値内訳/因果区別、L152-157)。時系列・主体1つ・多義語言い換えの規則は無い。
- 検証: 台帳段はAI再照合のみ(人間・決定論の原資料照合なし)。明確化後本文を原資料と照合する工程は無い。
- txt出力【確認】(L289-303): `[VERIFIED] id: claim`+scope/conditions/numeric_value/date_or_period/causal_strength/ambiguity_note/notes_for_writer。subject・support_levelはtxtに出ない。
- fail-safe位置: Verification直後〜txt化の間。txt既存なら再利用する既存挙動あり(L92-97)。
- Prompt改善のみの限界: 新規生成にだけ効く。既存fixtureは再利用経路でpromptが効かない(①H)。

## §2 問題の定義(根拠=②)
- HC-012 Before(逐語): 「…契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。」(`er019_output/meta/run_03/ledger/verified_fact_ledger.txt` L74-78)。誤読例: "restored the human concierge feature to the way it had been before"(`er052_output/open233_prod_e2e_02/runs/meta_run03_advanced.json` L331、重大)。「ロールバック」=取り下げ(正)と復元(誤)の両義。
- HF-009 Before(逐語): 「…Brent先物が一時的に上げ幅を縮小したものの、ほどなく発表前に近い高い水準へ戻ったと報じた。」1 factに途中(縮小)+最終(高水準)。誤読例: "After the plan was withdrawn, oil prices fell."(G-03、重大)。
- 同型: 27 fact中、曖昧度 高3(HC-012/HF-009/HF-012)・中14・低10(②C、目視判定)。
- 共通構造: (a)多義語・抽象動詞(ロールバック/置き換える) (b)1 factに途中/最終の複数事象(HF-009/HF-012/HC-005/HF-006) (c)主体・対象の省略(HF-004「別の専門家試算」/HC-014「商業者」) (d)因果確認の有無が本文から読めない(causal_strength欄はあるがtxtでNOT_APPLICABLE時は非表示)。

- Opus反映(訂正M1): (1)HF-009の「Writer誤読例 After the plan was withdrawn, oil prices fell.」(G-03)は合成文(testset_01 L1204「合成(委任_60)」)であり、実Writer出力ではない。本番hormuz/run_03のR0・R2・ENは途中/最終を正しく記述している("did not fall across the board"まで)。HF-009は台帳側の誤読原因ではなく、Checker側(1 factに1状態しか持たない)の課題として整理する。(2)HC-012の誤りの発生段(実本番): 台帳「ロールバック」→B3 brief逐語(`er019_output/meta/run_03/storyline_b3/selected_brief.md` L11)→JA R0「以前の状態に戻しました」(`.../ja_writer/original.md` L13)→R1/R2で維持→EN "restored…"(`.../b1b/article.md` L17)。台帳の曖昧語がWriter段で誤訳に固定された例。既存Meta R0の4系統すべてが曖昧訳で、基準発生率が高い(Trial Phase 0で集計)。

## §3 設計案
### 案P: Prompt強化のみ
Researcher/Verification promptへ「主体・対象・変化・時点・因果確認有無を明示、途中/最終を分けて書く、多義語回避」を追加。利点=最小変更・追加費用≈0。欠点=新規生成のみ有効(既存fixture不変)、出力の構造保証なし、Verification AIが明確化の意味一致を見る保証もない。
### 案C: 明確化パス追加
Verification直後(`build_verified_ledger_text`の前)に台帳全体を1回のLLM call(Webなし、別prompt)で処理。入力=kept_facts(claim/scope/conditions/date/numeric/causal_strength/ambiguity/notes_for_writer/verification_notes)。出力はfact_id維持で:
`statement`(明確化1〜2文)、`events[]`(subject/action/object/change/phase=INTERIM|FINAL|SINGLE/time)、`causal_confirmed`(yes/no/unknown)、`uncertainty`(元の不確実性を保持)。notes_for_writerは既存維持。
分割は「ID内のevents構造」で表現。Writer向けtxtは`statement`(必要時「途中:/最終:」)を`claim`の位置へ出す(表現は拘束しない)。元claimは`claim_original`として保持。
### 案C+V(推奨): 案C+意味一致検証
別call(推奨。同call self-checkは同一model相関が最大)で、新(statement+events)と元claim+notes+verification_notesを双方向照合。判定=YES/NO: (i)追加情報なし(新⊆元) (ii)欠落なし(元⊆新) (iii)関係(時系列・因果・条件・対象範囲)維持。NO/schema不一致/API失敗のfactはfact単位で元claimのまま、台帳全体失敗は従来txt化(工程fail-safe)。
### 案S: 子ID分割(不採用)
HC-012→HC-012a/b等。参照が壊れる(①E): HC-012は23ファイル65箇所、gold(`SAFETY_CRITICAL_CLAIM_DEFS` L9830/9836がrelated_fact_id=MUSE-HC-012)、`floor_verify_fact_block`は親ID不在で確認不能、B3全factテストのfact数増、Checkerが`related_fact_id`先頭1件のみ使う箇所で子の見落とし。親IDを残す変形は重複・Writer二重拾いの余地。
### 比較表(○=充足、△=条件付、×=不足)
| 観点 | P | C | C+V | S |
|---|---|---|---|---|
| ①事実を追加改変しない | △保証なし | △未検証 | ○(照合は元claim基準) | △ |
| ②関係維持 | △ | △ | ○(iii判定) | × a/b連結が消えやすい |
| ③Quality維持 | ○ | △Trial要 | △Trial要 | △ |
| ④量産自動 | ○ | ○ | ○ | △ |
| HC-012/HF-009予防 | △新規のみ | ○見込み | ○見込み | ○見込み |
| 既存fixture適用 | × | ○(offline) | ○ | ×(gold再作成) |
| ID整合 | ○ | ○ | ○ | × |
| Writer/Checker影響 | 小 | 中(本文変化) | 中 | 大 |
| 費用増 | ≈0 | +¥1 | +¥2 | +¥1〜2+再作成 |
| 時間増 | 0 | +30〜60秒 | +60〜120秒 | 同左 |
| 実装規模/保守 | 小 | 中 | 中 | 大 |
案Pは案C+Vと併用可(新規生成時の初期品質向上)。ただしPのみでは既存fixtureが検証できない。

### Opus反映(訂正M3/M4/M5/M6/R1〜R3、すべて【案】)
- M5(原資料原則): 多義語の意味確定、主体・因果の補完は原資料を参照できる工程(Researcher/Web付きVerification)でのみ許可。台帳テキストだけを見る案C/Vの工程は、原資料にない意味確定(例「取り下げ」)を加えうる(§4自己チェックでも指摘済み)。本番推奨経路=**P'**: Researcherスキーマ・prompt拡張(events/phase/多義語の意味確定欄)+既存Verification 9観点に「多義語の意味確定/途中と最終の区別が原資料と一致」を追加。追加callなし、費用≈出力token分<¥1。案C+Vは既存台帳のoffline適用(Trial用)に限定。C+Vを本番に採る場合は多義語factにWeb再Verification(選択肢B、+≈¥14/run)必須。
| 観点 | P'(推奨) | C+V | C+V+B | S |
|---|---|---|---|---|
| 原資料との一致 | ○(Web工程内) | ×(台帳のみ照合) | ○(Bで確認) | △ |
| 既存fixture適用 | ×(新規のみ) | ○(offline) | ○ | × |
| ID整合 | ○ | ○ | ○ | × |
| 追加call/費用 | なし/<¥1 | +1〜2call/+¥2 | +¥2+≈¥14 | +再作成 |
| 時間増 | ≈0 | +60〜120秒 | +約2〜3分 | 大 |
| 実装規模 | 中(スキーマ・prompt) | 中 | 大 | 大 |
| Trial用途 | Phase 2は既存台帳へC適用で代替 | 可 | 可 | 不可 |
- M3(Vに決定論検査を必須追加): fact_id集合・fact数・数値・日付・固有名・否定語・因果語の集合が元と新で一致すること。否定語・因果語はChecker正規表現(`er052_open233_stage1_coverage_checker_01.py` L437-526、`numbers_not_in_facts` L478・`facts_have_causal` L492等)を再利用。LLM Vは補強(単独で合否にしない)。
- M4(txt書式制約): claim行(1行目)に新しい否定語・因果語・番号・括弧を入れない。否定ガイドはnotes_for_writerに一本化。途中/最終は英字キーの字下げタグ行(例`  phase_interim:`/`  phase_final:`、空行なし)。`parse_ledger_text`(precheck L65)は英字キーのみ解釈し日本語キー行は捨てる(`TAG_LINE` L60、L92-96)。ブロック区切りは空行(L3012/L177)なので空行を入れない。uncertaintyもタグ行(`uncertainty:`)。
- M6(phase定義の一本化): phase定義は台帳側に一本化。同一主体・同一指標の時系列変化のみINTERIM/FINAL、別事象は別event(SINGLE)。食い違い記載: §4のHC-012は「両方SINGLE」、TRIAL-03(REPORT §86)では「テスト=INTERIM/機能=FINAL」と扱われ定義が揺れた。M6定義ではHC-012は別事象=SINGLE 2件。**F1(方針案、新Product仕様候補)**: 凍結した台帳eventsをCheckerの比較基準として共有し、Checker側のLedger event抽出(TRIAL-03で揺れた)を廃止する。実装は台帳Trial合格後、ユーザー判断。
- F2: 「限定語なし方向表現→最終状態と比較」はChecker側labeling_guideの比較手順として扱える(新Product原則にしない)。
- 任意R1〜R3: R1=`ambiguity`をVERIFIEDでもtxtに出す(¥0)。R2=明確化対象を曖昧度高・中に限定(低10件は触らず悪化リスク減)。R3=30 fact以上は分割処理。

## §4 Before/After具体例【案】(原資料との意味一致は未照合。台帳は未変更。②Eの案1に対応)
### HC-012
- statement【案】: 「MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、人間コンシェルジュ機能(契約スタッフが電話を担当する機能)を当面取り下げたと社内投稿で説明した。」
- events【案】: [{subject:副社長, action:認めた, object:開示なしテスト開始, change:なし, phase:SINGLE, time:〜2026-09-22}, {subject:Meta, action:取り下げた(rollback), object:人間コンシェルジュ機能, change:提供停止(当面)=以前の状態への復元ではない, phase:SINGLE}]
- causal_confirmed: unknown(「ミス認定→取り下げ」の因果は台帳に明記なし)。uncertainty: 再開時期・対象範囲・代替方式は未公表(元ambiguity保持)。
- Writer向けtxt【案】: `[VERIFIED] MUSE-HC-012: <statement>`+既存scope/conditions/date/notes。
- 自己チェック: 追加情報=「以前の状態への復元ではない」は台帳内根拠(HC-014 notes・testset rationale)派生で、原文に無ければ追加情報。原文の語(rolled back/pulled等)が未保存のため「取り下げ」が原文と一致するかも未確認。欠落=「当面」維持、因果は断定せず。関係=同一投稿内の2事項(同時性)を維持。
### HF-009
- statement【案】: 「Yahoo Financeは、7月14日の撤回・投資案件への置換発表後、Brent先物が(1)まず一時的に上げ幅を縮小したが、(2)ほどなく発表前に近い高い水準へ戻ったと報じた。記事掲載時点では約2.6％高、85ドル超だった。」
- events【案】: [{phase:INTERIM, subject:Brent先物, action:上げ幅縮小(下落ではない), time:発表直後・一時的}, {phase:FINAL, subject:Brent先物, action:発表前に近い高水準へ復帰, numeric:約+2.6%・$85超(スナップショット), time:ほどなく}]。causal_confirmed: yes(CAUSAL_STATED_BY_SOURCE、原因は撤回発表以外にも攻撃等が継続=conditions維持)。
- 自己チェック: 追加情報=「(下落ではない)」はnotes由来で原文確認要。欠落=conditions・numeric_scopeを維持する必要。関係=INTERIMがFINALより前、全面下落ではない点を維持。
- 上記は【案】。実際はmodel出力で、V判定+Fable/Sonnet offline照合(§5)で検証する。
- Opus反映(訂正M4/M6): HF-009のeventsはHF-009固有の「同一主体・同一指標の時系列変化」でINTERIM/FINAL(M6定義に合致)。HC-012は別事象のためSINGLE 2件(M6定義)。txt化時、claim行に「(下落ではない)」等の新しい否定語・括弧を入れず、notes_for_writerと英字タグ行(`phase_interim:`/`phase_final:`)へ出す(M4)。

## §5 検証責任と段階
1. 自動(量産): 案Vの別call判定(新⊆元/元⊆新/関係維持)。照合基準は元claim+notes+verification_notes【確認: source quote欄なし】。
2. 既存AI Verification結果(VERIFIED/AMBIGUOUS)を引継ぎ。AMBIGUOUSは断定禁止見出しを維持し、明確化でambiguityを消さない(prompt規則+Vの(ii)で検査)。
3. Trial段階: Fable/Sonnet offlineで原資料(URL再取得は別委任、Web費用あり)と照合。
4. Production: 人間編集なし(④)。事実の追加防止は1.のVと2.のみ=原資料との一致は保証されない。強化選択肢=Web付き再Verification(+約¥14・63秒、既存Verification相当【確認】)を明確化済みfactのうち変更ありのfactだけに対して実行(選択肢B)。
- Opus反映(訂正M3/M5): 上記1.のVは決定論検査(fact_id集合・fact数・数値・日付・固有名・否定語・因果語の一致)を必須とし、LLM Vは補強。原資料との一致を保証できるのはWeb付き工程(P'のVerification拡張、またはC+V+Bの再Verification)のみ。台帳テキスト基準のVは「追加・欠落の検出」止まり。
- 失敗時: V=NO/API失敗/schema不一致→当該factは元claim(fact単位)。明確化パス自体の失敗→従来`build_verified_ledger_text`出力(工程単位)。どちらもID・fact数は不変。

## §6 Writer/Checkerとの整合
- Writer prompt【案】: 「statement/eventsに基づく。台帳にない主体・時点・因果を足さない。phase=INTERIMとFINALは混ぜない」。既存指示の逐語(`er019_family_x_ja_writer_o_r1_r2_01.py` L132-133 must_fix文言「Ledgerにない断定・因果・数値・主体・時期・比較・否定・一般化を残さない」)は引用可。JA writer prompt全文は【未確認】。
- Checker: Stage1 r3/r5の`ledger_quotes`は台帳逐語必須(`er052_open233_stage1_coverage_checker_01.py` L224-226)。本文がstatementに替わるため、quoteは新txt基準で再取得される(旧labelsとの逐語不一致は想定内)。`floor_verify_fact_block`はfact_idの見出しでブロック取得【確認 runner L3003】、ID不変なので動作。
- gold【確認】: `SAFETY_CRITICAL_CLAIM_DEFS`(runner L9817-)の`text_substring`は記事側の英文(例"temporarily put back the feature")、台帳側は`related_fact_id`のみ。台帳変更で不変。
- 過去labels・実測との比較は不連続。Trialは従来台帳runと明確化台帳runを別集計(③§1)。
- 注意: 台帳が明確化されても、HC-012/A5-0型(TRIAL-03で退行)は記事側文の誤読検出の問題であり、ledger側のphase情報がChecker側へ新しい判定材料になるかは§9で論点化。

- Opus反映(訂正M2): 上記「Writer prompt【案】」は前提が誤り。WriterはB3の要約briefを読む(`er019_family_x_storyline_b3_fact_selection_01.py` L78)ため台帳を直接読まない。B3 briefには台帳にない因果が加わる例がある(`selected_brief.md` L4)。R1/R2は台帳を参照しない。よって台帳の明確化だけではWriterの語選択まで保証されず、評価は台帳→B3 brief→R0→R1/R2→ENの各段で対象factの意味保持を測る。B3 prompt側へのphase/uncertainty引継ぎ要否は別論点(新Product仕様候補、ユーザー判断)。

## §7 既存fixtureへのoffline適用(Trial用DEV経路)
- 保存済み`verified_fact_ledger.txt`+`research_ledger/fact_ledger_draft.json`・verification.jsonへ案Cをoffline適用→`verified_fact_ledger_clarified.txt`(元は不変・別名保持、sha256記録は既存方式踏襲)。
- runnerには台帳パス差替え引数が無い【確認 ③§0】。DEV限定の`--ledger_path`追加が必要(Production既定=従来。DEV引数使用時のみ有効、Production経路への混入を防ぐ)。Writer初稿のDEV経路とC_w未実測(③)も要。
- 【推測】既存fixtureにはdraft JSONが無い場合があり、その場合はtxtのみから明確化(情報量が少なく、スコープ・numeric_scope等は元txtの項目に限る)。

## §8 費用・時間
- 案C: 台帳全体1回、Webなし。入力数k〜十数kトークン、出力は台帳量。≈¥1・30〜60秒/fixture【推測。実測なし】。V追加≈¥1・30〜60秒。fact単位callは15 fact×¥0.7〜1=¥10〜15のため不採用(並列でも数十秒)。
- 量産: 台帳費¥28.7→≈¥30.7(+5〜7%)、時間+1〜2分/run(149秒→約4〜5分、+約40〜80%は台帳段のみ。run総額¥44.66に対し約+4%)。【全て推測、Trial前に1回実測】
- 選択肢B(Web再Verification追加)を採ると+約¥14/run(+31%)・+63秒。Trial費用は③§5(low¥30/mid¥64/high¥127、C_w仮置き)。

## §9 Opusレビュー論点
ユーザー7観点(正確性検証者・追加情報防止・関係維持・Quality・量産自動・fail-safe・費用時間)に加え:
1. phase(INTERIM/FINAL)構造が方向反転Checker(TRIAL-03で退行、REPORT §86)の判定軸(Opus REVIEW-03推奨のphase次元)と整合/干渉しないか。台帳側phaseと記事側phaseの揺れ(TRIAL-03「Ledger側ラベル揺れ」)を再現しないか。
2. 逐語quote変更がChecker(`ledger_quotes`必須)とfloor_verifyに与える影響、過去labelsとの比較不能性の扱い。
3. self-check(V)が同一model(luna系)で相関し、同じ誤読を見逃す懸念。別model・別prompt・決定論の語彙差分検査(数値・固有名・日付のtoken集合比較)の併用要否。
4. source quote欄が無いため原資料一致を保証できない点を許容するか(選択肢B)。
5. 案Pとの併用/分離、Writerが明確化で台帳丸写しに寄る副作用(③品質③の逐語コピー率)。

## §10 Trial計画との接続(③の要約+修正点)
- ③: 品質①重大Fact誤認、②Checker精度(構成固定)、③自然さ・面白さ(決定論指標+pairwise+Fable確認)。fixtureは開発例(HC-012/HF-009)/検証例/held-out(候補HF-012等8件)に事前固定、promptに固有名を埋めない。
- 修正点: (1)Writer初稿のDEV経路が前提(runner¥3.5/runはChecker側のみ、C_w未実測)。(2)明確化台帳は事前に1回生成し両条件・全seedで固定。(3)Quality rubricは新規。(4)従来側で重大0件なら「悪化なしのみ、改善未証明」。(5)明確化の正確性(V判定通過率・Fable照合のNG件数)を第4の指標に追加。(6)Trial VALIDATEDはProduction仕様ではない。

- Opus反映(訂正): Trial計画は`05_trial_plan.md`へ確定案として分離(Phase 0〜3、上限¥100案)。Writer初稿のDEV経路は全フローChecker runではなくB3+JA R0〜R2+ENのみ。

## §11 Dangling Reference確認(Grep/Glob、実在のみ。本docが参照する対象)
- `build_verified_ledger_text`: 実在(`er003_v1_en_direct_vfl_01_generate.py` L275)。
- `er003_v1_en_direct_vfl_01_generate.py`: 実在。
- `floor_verify_fact_block`: 実在(`er052_open233_self_recovery_flow_runner_01.py` L3003)。
- `ledger_block_fields`: 実在(同runner L3431)。
- `SAFETY_CRITICAL_CLAIM_DEFS`: 実在(同runner L9817)。
- `er019_family_x_ja_writer_o_r1_r2_01.py`: 実在(Glob)。
- 未確認(①の記載を引用、本委任で再確認せず): `er052_open233_stage1_coverage_checker_01.py` L224-226、`FACT_ID_LINE_RE`、`labeling_guide_01.md`。
- 本docが新規に提案する名称(`statement`/`events[]`/`--ledger_path`/`claim_original`等)は未実装の【案】であり実在参照ではない。

## §12 Status案と選択肢
- Status: DESIGN_READY_FOR_REVIEW。次: Opus条件Aレビュー(Fable依頼)→USER_DECISION_REQUIRED(Trial承認)。
- 新Product仕様に当たる候補(決定ではなく選択肢): (1)台帳スキーマ拡張(events/causal_confirmed等)の採否と、見える範囲(txtにphaseを出すか/statementのみか)。(2)Writer向け出力形式: a=statementのみ、b=statement+「途中:/最終:」2文、c=events全表示。(3)検証強度: A=内部Vのみ、B=変更factのみWeb再Verification追加(+約¥14)、C=決定論token差分併用。(4)適用範囲: 新規のみ/既存fixtureoffline含む。(5)案P併用の有無。
- 推奨: 1=statement+events(内部)、2=b、3=A+決定論差分、4=既存fixtureにoffline適用、5=併用。ただしOpus・ユーザー判断前提。
- Opus反映(訂正): 上記推奨は§13で更新。3の検証強度は「決定論差分必須(M3)」、本番経路はP'(M5)。Status=USER_DECISION_REQUIRED(Trial計画承認+新Product仕様候補の判断)。

## §13 Opus条件Aレビュー要約とFable照合(新設)
- 総合判定: 設計の方向(ID・fact数不変、案S不採用)は妥当。ただし必須修正6件(M1〜M6)あり。逐語は`docs/pm/opus_l2_review_lc_design_01.md`(作成済み(2026-10-06、委任_03f、セッション記録から機械抽出・改変なし))。
- M1〜M6の反映状況: M1=§2へ追記済(HF-009誤読例は合成文、HC-012の発生段)。M2=§6へ追記済(WriterはB3 briefを読む)。M3=§3末尾・§5へ追記済(決定論検査必須)。M4=§3末尾・§4へ追記済(txt書式制約)。M5=§0・§3末尾へ追記済(P'推奨、比較表再掲)。M6=§3末尾・§4へ追記済(phase一本化、F1)。任意R1〜R3・F2も§3末尾に記載。
- Fable照合(Sonnet初版案との対立ではなく訂正・精緻化): 特にM1はSonnetが合成文を実出力として扱った事実誤認の訂正、M2は読取経路の誤認の訂正。P'(本番推奨)とC+V(Trial用offline)の使い分け、および台帳スキーマ拡張(events/phase/uncertainty)・F1(Checkerとの比較基準共有)は新Product仕様候補であり、決定ではなく選択肢。ユーザー判断が必要(採用・Production化は人間ユーザーのみ)。
- 決定ではない事項: P'採用、スキーマ拡張、F1、Trial実行はいずれも未承認。


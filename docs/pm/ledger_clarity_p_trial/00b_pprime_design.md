# 00b P'設計案(Phase 0、調査+設計のみ、実装・API・Production変更なし。全て【案】、未承認)
## 1 実装調査結果(【確認】=コード読取)
- Researcher=`er003_v1_en_direct_vfl_01_generate.py`(vfl01) L170-189。**1 callで検索と構造化を同時実行**(`tools=[web_search]`+`text.format=json_schema strict`、model=vfl01.MODEL、reasoning high)。検索と記述は分離不可。P'=同一callのprompt追記、検索自体は従来どおり走る(検索結果の時間ずれは避けられない)。
- factキー15個(fact_id/claim/subject/date_or_period/scope/conditions/numeric_value/numeric_scope/causal_strength/source_title/source_url/source_type/support_level/ambiguity/notes_for_writer)。schemaは`strict:True`+`additionalProperties:False`+全キーrequired(L113-118)。
- 追加キー(events/phase等): schema自体は変更可だが、(a)`build_verified_ledger_text`(L275-305)はキーを明示列挙で拾うだけなので**新キーはtxtに出ない**(kept_facts jsonにのみ残る=Writer/Checkerに届かない)、(b)届かせるにはtxt生成の変更が必要=決定論処理の変更。→追加キー案は不採用。
- txtに出る欄: claim(1行目)/scope/conditions/numeric_value+numeric_scope/date_or_period/causal_strength(非N/A)/ambiguity_note(**AMBIGUOUS判定時のみ**)/notes_for_writer(常時)。
- Production経路: er019 runner(`run_research_and_ledger` L89-)→`efam.run_researcher_for_topic`(er012 L164)→`vfl01.build_researcher_prompt`/`FACT_LEDGER_JSON_SCHEMA`/`build_verification_prompt`をモジュール属性として呼ぶ。既存txtがあれば再利用(L92-97、promptは効かない)。er052 runnerはledgerを生成せずfixtureのtxtを読む(vfl01はDeviation検査関数のみ利用)。
## 2 採用案: 既存フィールドのみで明確化(追加キーなし、schema不変)
- claim: 主体・動作・対象・時点が明示された1〜2文(新たな否定語・因果語・括弧・番号を入れない=M4)。
- date_or_period: 時点/順序。conditions: 「途中経過→最終状態」の順序を語で。
- notes_for_writer(常時txt出力): 途中/最終の区別、多義語の確定意味、断定の強さの上限。ambiguity: 不確実点(ただしtxtにはAMBIGUOUS時のみ出る→重要な不確実点はnotes_for_writerにも1行残す)。
- 制約: M4が想定した`phase_interim:`等の英字タグ行は**txt生成の変更が要る**ため本案では出せない(自由文で代替)。→ユーザー判断事項(下記5)。
## 3 決定論処理の変更要否: **不要**(上記の範囲では)。`build_verified_ledger_text`・schema・enum・fact_id/fact数の扱いは無変更。**STOP_RECOMMENDED条件**=phase/eventsタグ行やambiguity常時出力(R1)をtxtへ出したい場合のみ(その時点で設計を止めユーザー判断)。
## 4 P'プロンプト追記案(一般規則、固有名なし、Researcherのprompt末尾の追記ブロック。日本語10行)
【Factの記述規則(明確化)】
1. claimは「誰/何が・何をした/どうなった・対象・時点」が分かる1〜2文で書き、原資料の語を要約で曖昧にしない。
2. 途中経過と最終状態が両方ある場合は、時点・順序を分けて書く(date_or_period/conditions/notes_for_writerに順序を明記)。
3. 多義的な動詞・名詞は、原資料が示す具体的な動作・状態に置き換えるか、原資料の語をそのまま添える(notes_for_writer)。
4. 原資料にない主体・因果・時系列・数値・事実を足さない。新しいFactを追加しない。
5. 解釈に不確実さが残る点は断定せずambiguityに書き、notes_for_writerにも1行残す。
6. 断定の強さ(確定/報道/予定/可能性)を原資料より強めない。
7. claimに新しい否定語・因果語・括弧・番号を足さない(注意はnotes_for_writerへ)。
8. 検索対象・検索方法・Source優先順位は変えない(本ブロックは記述だけの規則)。
## 5 Verification追記案(9観点の後ろに追加、10観点目〜。enum VERIFIED/AMBIGUOUS/REJECTEDは不変。`VERIFICATION_PROMPT_TEMPLATE` L233-242)
- 明確化された意味(主体・動作・対象・時系列・多義語の確定)が原資料の記述と一致するか。
- 途中経過と最終状態の区別・順序が原資料と一致するか、原資料にない主体・因果・時系列が足されていないか。
- 一致が確認できない・原資料が曖昧な場合は無理にVERIFIEDとせずAMBIGUOUSとし、verification_notesに理由を書く。
## 6 DEV限定切替(Production無改変の最小差分)
- 新規DEV script 1本(例`er052_open233_ledger_clarity_pprime_dev_01.py`、新規作成のみ)。環境変数`OPEN233_RESEARCHER_VARIANT`(既定=未設定=従来)が`pprime`の時だけ、プロセス内で`vfl01.build_researcher_prompt`/`build_verification_prompt`を「元の戻り値+追記ブロック」に差し替え(monkeypatch)、その後er019 runnerの`main()`を呼ぶ。er003/er012/er019のファイルは**1行も変更しない**(変更予定ファイル=新規DEV scriptと新規test 1本のみ)。
- 既定不変の保証: (a)Production fileのgit diffが空、(b)unit test: env未設定でprompt/schema/DEV scriptがpatchしない状態で`build_researcher_prompt(topic)`が元とバイト同一、`pprime`時は元prompt+追記ブロックの完全一致、schema/enum不変、(c)¥0で実行可(API無し)。不正値はValueError(黙って既定へ戻さない)。
## 7 runner接続・state非混入
- 台帳生成=er019 runner(`--stage ledger --stop-after ledger`相当、`--out-dir`必須)。出力先は新規`er052_output/open233_ledger_clarity_p_trial_01/<slug>/`を指定(既存E2E `open233_prod_e2e_*`と別dir)。er019 runnerは`cl.install(<out-dir>/raw_usage_log.jsonl)`でout-dir内にだけ書き、`attempt_history.jsonl`(er011_output)・`budget_state_*.json`(er052 runner定数)を参照しないので混入しない【確認: grep結果】。後段のCheck/er052 runner実行時は`BUDGET_STATE_PATH`/OUT_DIR(定数)を新規dirへ向ける必要あり(別委任で設計)。既存txt再利用(L92-97)を避けるため出力先は必ず新規dir。新run用テーマは新規記事=ユーザー選定が必要(PM_GOVERNANCE 13節)。
## 8 費用見積(【推測】、Trial前に実測)
- 実測(Meta run、`01_current_pipeline.md`L12): Researcher ¥14.47(入51k/出8.5k/検索7回)+Verification ¥14.27(入62k/出5.6k/検索7回)=¥28.7、run総額¥44.66(B3+Writer+Checker等≈¥16)。cost記録は`raw_usage_log.jsonl`、`cost.json`はJA段のみ。
- P'増分: prompt追記は入力+~0.5k token、claim長文化・notes増で出力+10〜25%(Researcher出力+1〜2k)=約+¥1〜3、Verification追記観点は+¥0.5以下。**台帳のみ≈¥30〜32、1 run全体≈¥46〜50**。¥50上限に対し全体runは余裕≈¥0〜4で**tight**(検索回数のブレで超過あり得る)。推奨=台帳段のみ先行(≈¥32)。全体runは上限引上げ(例¥60)の判断が必要。
## 9 リスク
- 検索の再実行で別Fact集合になり、Before/Afterの純粋比較ができない(台帳はnew生成のため、同一fact集合でのA/Bは不可)。
- claim長文化でM4(否定語・因果語・括弧)違反や情報過剰が生じうる→M3の決定論検査(fact数/ID/数値/否定語/因果語)を生成後に実施。
- ambiguity(VERIFIED時は不出力)に頼るとWriterに届かない→notes_for_writer運用で回避済み。
- phase/eventsタグ行(M4/F1)はtxt生成変更が要る→STOP_RECOMMENDED扱い、ユーザー判断。
- 本案は新Product仕様候補で未承認(APPROVED_FOR_PRODUCTIONではない)。

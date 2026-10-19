# B3_MIN2_DESIGN_01(FAMILY-X-B3-FACT-MIN2-PRODUCTION-01 委任_01、2026-10-19、Phase 1、JPY0)

- Status: `B3MIN2_DESIGN_READY_PENDING_OPUS_A`。コード変更0・有料API呼出0・`run_mey_01`配下の変更0(読取のみ)。
- 根拠となるユーザー決定: `docs/pm/delegation_log/2026-10-19_FAMILY-X-B3-FACT-MIN2-PRODUCTION-01_USER.md`(2418文字、sha256 `a6a04d3d843d4dedab3820b1da15591a792066a2c9b26eafbc1b9fc437b29716`)。B3採用Fact下限2件=`APPROVED_FOR_PRODUCTION`(未配線)。
- 作業開始時のstop_scope_check: rc=0、stop=false(`docs/pm/delegation_log/2026-10-19_XB3M1_stop_check.json`)。`run_mey_01`直下に`STOP`/`STOP_ALL`/`*STOP_NOTICE*`は無い(`ls`で確認。`_stop_scope_check_01_s*.json`は過去の判定記録)。
- 現行baseline: `er019_family_x_b3_production_wiring_01_test_01.py` 30 passed(読取確認のみ)。

## §1 現行B3経路マップ(Family X)

### 1-1 モジュール内(`er019_family_x_storyline_b3_fact_selection_01.py`)
| 要素 | 場所 | 内容 |
|---|---|---|
| 4テスト定義(ユーザー確定事項5、逐語・変更禁止) | :37-42 `FACT_TEST_DEFINITIONS_JA` | Test1〜4とも「YESなら/NOなら**原則除外**」。除外寄りの設計 |
| Developer message | :44-49 `DEVELOPER_MESSAGE` | 「本当に必要な最小限のFactだけを選び出して」 |
| User prompt | :51-81 `USER_PROMPT_TEMPLATE` | 中心Storyline1つ決定→全Factに4テスト→selected/excluded→Selected Fact Brief |
| **採用数の指示(現状の決定箇所その1)** | :70-71 | 「目安は3〜5件です。Hard ruleではありません…6件以上はrecheck_note…**3件未満でも、Storylineが単独で成立するなら構いません**」 |
| JSON schema | :90-127 | `selected_fact_ids`は配列(minItems等の件数制約なし) |
| Fact ID抽出 | :129,:144-145 | `[VERIFIED]`と`[AMBIGUOUS...]`の行からID抽出(REJECTEDはLedgerに載らない) |
| Validator | :155-184 `validate_selection_output` | 技術整合のみ: unknown ID/全ID検査網羅/selected_fact_ids==decision=selected/空Storyline/空Brief/**6件以上でrecheck_note無し(softのみ)**。**件数の下限チェックは無い(0件でも通る)。上限もhard cap無し** |
| 1回呼出 | :187-206 `_call_once` | `client.responses.create(json_schema, strict)` |
| 選定+技術retry | :209-245 `run_storyline_b3_selection` | attempt 1,2(2回目は:83-88 `RETRY_APPEND_NOTE`を付加)。技術不正(JSON不正・ID不整合)のみretry。内容の善し悪しではretryしない(:20-24方針)。2回失敗で`RuntimeError("[STOP] ...")` |
| Brief組立 | :252-278 `build_selected_brief_markdown` | 「# Selected Fact Brief / ## Storyline / ## Selected Facts」 |

### 1-2 runner(`er019_family_x_entertainment_production_runner_01.py`)
| 経路 | 場所 | 挙動 |
|---|---|---|
| B3 stage本体 | :147-190 `run_storyline_b3` | `routing.require_model("FAMILY_X_STORYLINE_B3")`(gpt-6.1-sol, effort high)→`b3.run_storyline_b3_selection`→`full_ledger.json`/`selected_brief.md`/`fact_selection_evidence.json`/`runtime_evidence.json`保存。返却model不一致はSTOP(:156) |
| 初回 | :408-419 | `selected_brief.md`が無ければ`run_storyline_b3` |
| `--regenerate-stage storyline_b3` / `--stage storyline_b3` | :411-418 | 既存briefがあっても再実行(`regenerate_stage=="storyline_b3"`または`stage=="storyline_b3"`) |
| resume/再利用 | :412-416 | `selected_brief.md`が存在し再生成指定なし→**B3を呼ばず再利用(`storyline_result=None`)**。**この分岐ではb3 moduleのValidatorは通らない** |
| 決定論producer(全分岐の合流点) | :420 → :200-215 `run_annotation_producer` | 初回/regeneration/resume/再利用すべてで`storyline_b3`確定直後に呼ぶ(CURRENT_SPEC:1169も同旨)。`er053_b3_deterministic_producer_01.py:717-` `_check_inputs`が`selected_fact_ids`の**非空**・重複なし・Ledger存在・Storyline一致を検査(**件数下限は1**)。LLM call 0 |
| 契約検証 | `er053_b3_annotation_contract_01.py:225-235` V5 | Fact行`【事実N】`が1..Kで連番、**K<1でfail**(下限1)。W-1入口で課金前fail-closed |
| W-1 Writer | runner:218-230 `run_ja_writer`→`er053_family_x_factlock_ja_writer_01.py:318 run_w1_writer` | 入力は**注記済みB3 artifactのみ**(契約検証V1-V10後)。`selected_fact_brief_text`を直接渡す経路は無い。タグ`【事実N】`は本文から除去(`strip_tags`:108、`assert_no_tag_leak`:168)。**各採用Factが本文で使われたかの照合は無い**(Fact Lockは数字規則・来歴・タグ漏れ)。`verified_fact_ledger.txt`はRisk Flagger(RF)が完全台帳として照合に使う(runner:281) |
| JA再利用(U-1) | runner:233-256 `load_reused_ja_text` | `chain_method=="W-1"`かつ`annotated_md_sha256`一致でのみ再利用。B3再生成後にWriterをreuseすると`PROVENANCE_MISMATCH`でSTOP(:246-254)=下流自動再生成なし(安全側) |
| 下流 | runner:449-466 | `advanced`/`standard`は`efam.run_writer_stage`+RF(非Blocking) |

### 1-3 「採用Fact数」を決めている箇所と現状の下限・上限(事実)
- 決めているのは**LLM(Prompt指示文:70-71)のみ**。コード側に採用数のgate/上限/下限は無い。`excluded`はLLMの`fact_tests[].decision`で決まり、コードは`selected_fact_ids==decision=selected`の一致しか見ない。
- **下限**: b3 module=0件でも技術的に有効。producer`_check_inputs`と契約V5は**1件以上**。Promptは「3件未満でも構わない」と明示。すなわち**実効下限=0(module)/1(下流)**。
- **上限**: hard cap無し。Promptの目安は5件、6件以上はrecheck_note義務(欠落はsoft warningでありretry対象外)。
- 重要: Promptの4テストは全て「原則除外」へ傾く構造(:38-42)で、Prompt:71が「3件未満でも構わない」と許す。これが`run_mey_01`で同一ledger 11件から**2回連続F11のみ**になった構造要因(事実: 2回とも他10件のTest2=NO, Test3=NO)。因果の断定ではなく観測。

### 1-4 Family固有か共通か(照合結果)
- B3選定moduleは**Family X固有**(ファイル名`er019_family_x_*`)。`run_storyline_b3_selection`のProduction呼出元は**runner:154の1箇所のみ**(Grep全py)。
- **Family Z**: B3を使わない(CURRENT_SPEC:1604「Sol R0->R2を採用(B3Zは不採用)」)。`er0xx` ZのProduction pathにstoryline_b3 importなし(Grep)。
- **Family Y**: `er036_family_y_voice_structure_trial_01.py:33,141`が`run_storyline_b3_selection`を**無変更import**(Trial専用、Production未配線)。→ module変更はY Trialの挙動に波及しうる(既定をどうするかOpus観点)。`er037`はX run evidenceを読むだけ(:71)。
- 注記producer/契約(`er053_b3_*`)のimportはX runner・test・`er053_c*_test`のみ(Grep)。
- `er082_rlct_trial_01_lib.py:561`の`run_storyline_b3_selection`複製はRLCT Trial専用(**混入禁止**。本件は触れない)。
- 結論: **Family X固有の仕様変更**。共通moduleは存在せず、共通化の必要は今回無い(Y導入時に流用される点のみ注記)。

## §2 採用Fact数の実績表(read-only、`er019_output/**/storyline_b3/fact_selection_evidence.json`全22件。実測値)

| 採用数 | 件数 | run(Ledger件数) |
|---|---|---|
| **1** | 2 | `middle_east_yemen_saudi/run_mey_01`(現行・再生成後)(11)/`.../run_mey_01/_before_regen_01`(初回)(11) |
| 2 | 2 | `boredom_aggression/run_bape_01`(11)/`meta/run_regen_01`(15) |
| 3 | 13 | `family_x_b3_diversity_trial_01/hormuz/run_01,run_02`(12)、`.../small_bag/run_01,run_02`(17)、`family_x_b3_production_wiring_01/run_01,run_02`(15)、`family_x_entertainment_production_runner_01/an3_t0_wiring_regression_01/hormuz`(12)・`/meta`(15)、`family_x_refresh_e2e_01/hormuz/run_02,run_03`(12)・`meta/run_03`(15)、`meta/run_03`(15)、`meta/run_sol61_01`(15) |
| 4 | 1 | `coffee_prices/run_fxpw_01`(17) |
| 5 | 4 | `coffee_prices/run_l3_01`・`run_l3_01_stdregen`・`run_v5_ms_01`(19)、`semiconductor_earnings/run_devconfirm_01`(6) |

- 取得範囲: `er019_output`配下のfact_selection_evidence.json全件(glob)。他output(er052/er082のTrial)は対象外(Production実績ではない)。`family_x_audio_production_wiring_01/*`にはB3 evidenceは無い(音声側runnerでB3を再実行しない)。
- 読み取り: 現行B3方式の**Production的実績では1件はmeyのみ(2/22、ただし同一Ledgerの再生成)**。最頻は3件。**1件選定は当該1テーマに偏っている**(実績の根拠は上表、因果は未確定)。
- **mey詳細(現行=再生成後)**: Ledger F01〜F11、全`[VERIFIED]`、採用=F11のみ。Storyline=「サウジの民間空港への相次ぐ攻撃と民間人被害を受け、国連イエメン担当特使は10月11日、攻撃を非難し、地域の安全保障とイエメン和平への悪影響を警告した。」。F01〜F10は全て(Test1=YES, Test2=NO, Test3=NO, Test4=YES)でexcluded(例: F04「10/10の12人死亡309人負傷」はF11が引用済みとして除外、F01「全面戦闘」は背景のみ)。**初回(`_before_regen_01`)も採用=F11のみ**(F09/F10はTest4=NO。Storylineは「継続的な攻撃で死傷者…特使が和平努力を一層困難にすると評価」)。`recheck_note=null`、`soft_warnings=[]`、attempts=1。
- 日本語記事: `ja_writer/revision2.md`(題「空港への攻撃、被害の数字だけでは見えない『もう一つの危機』」)。

## §3 最小変更設計案

### 3-0 共通の設計原則(全案)
1. **コードはFactを選ばない**。件数が2未満のとき、LLMに再評価を1回だけ依頼し、結果を検査するだけ(数合わせのコード側補完は構造的に無い)。
2. 下限の算定は「**当該Ledgerに実在する`[VERIFIED]`のFact ID**」のみを数える(`[AMBIGUOUS...]`が選ばれること自体は現行どおり可、ただし**下限の2件には数えない**。ユーザー§2「検証済みFactから最低2件」の保守的解釈。候補Bだが解釈事項としてOpus観点②に記載)。Ledgerの`[VERIFIED]`が2件未満なら**API呼出前に**`B3MinFactsStop`(理由`LEDGER_VERIFIED_FACTS_BELOW_MIN2`)=無駄な課金なし。
3. 再評価は**最大1回**(技術retry最大2回とは別枠。最悪合計3 call)。再評価後も<2、または再評価の技術不正→**原因を記録してSTOP**(無制限retry・補完なし。ユーザー§2)。
4. 再評価Promptに入れるもの(案により所在が異なる): 「中心テーマ(`topic`)に関連するFactを再評価。数合わせのために関連性の低いFactや未検証Factは追加しない。Ledgerに実在し`[VERIFIED]`のIDのみ。下限2件を満たせない場合は満たせない理由をreasonに書く(≠無理に選ばない)」。4テスト定義(逐語・sha固定)は不変のまま。
5. 記録: `fact_selection_evidence.json`に追加キー(既存キーは不変): `min2_policy`={floor:2, counted:"VERIFIED", first_pass_selected_ids, first_pass_n, reevaluated:bool, final_n}。STOP時は`storyline_b3/audit/b3_min2_stop_record.json`に原因(first-pass fact_tests・reason・下限未達理由)を保存してからSTOP(runnerで例外を捕捉し保存→再送出)。
6. 不変とするもの(変更しない): 4テスト定義、`DEVELOPER_MESSAGE`、ID網羅検査、モデル/effort、決定論producer規則(`rules_sha256`はporting対象の規則のshaで、`_check_inputs`は`_PORTED_NAMES`外か**実装時に要確認**)、W-1 Fact Lock、RF、U-1、Gate、予算ガード。

### 3-1 案I: Prompt本文変更 + moduleで下限強制(再評価1回)+ STOP
- 変更箇所: (a) `USER_PROMPT_TEMPLATE`:70-71の「3件未満でも…構いません」を「原則最低2件(検証済みFactから)。2件未満の場合はStoryline上の理由を明記」へ変更(**Prompt変更=Production Gate対象**。`prompt_shas`が変わり`test_b3_prompt_shas_pinned_unchanged_by_model_change`の固定shaを更新)、(b) `validate_selection_output`に`SELECTED_BELOW_MIN2`(hard、ただし技術retryには使わず再評価分岐へ)、(c) `run_storyline_b3_selection`に再評価1回+`B3MinFactsStop`、(d) `REEVAL_APPEND_NOTE`新設、(e) runner:`run_storyline_b3`で`B3MinFactsStop`を捕捉しaudit記録後に再送出、evidence追記。
- retry/regeneration/resume/再利用への反映: 初回・`--regenerate-stage`は`run_storyline_b3`経由で必ず評価。resume/再利用(runner:412-416)は**B3を呼ばないので評価されない**→ (f) 再利用分岐で既存`fact_selection_evidence.json`の`selected_fact_ids`(VERIFIED数)を読み<2なら`B3MinFactsStop`(「`--regenerate-stage storyline_b3`で再選定」を案内、API呼出0)。
- 不変性: Fact Lock・帰属・因果・時点・AMBIGUOUS・安全条件は触れない(4テスト・producer・契約・W-1・RFは不変)。
- 下流Writer: 現行Writerは採用Factの本文使用を照合しない(§1-2)。2件以上渡ること自体は契約V5(K連番)・V10(再導出一致)・W-1がそのまま扱える(Kに上限なし。K=3〜5の実績あり)。**本文で使われたか**はユーザー§4の受入条件→再生成後に**手動突合**(運用)。恒久的な自動照合の新設は新品質基準=範囲外(候補のみ、§3-5)。
- 副作用: 関連性の低いFactの混入リスクは残る(LLMが数合わせで選ぶ)。防止=①4テスト・reason必須の維持 ②再評価noteの禁止文 ③下限算定をVERIFIED限定 ④evidenceに初回選定と再評価後の差分を保存し人が検査可能。機械的な関連性判定は新設しない。
- 費用: 初回で2件以上なら増加0(Prompt変更により再評価頻度が下がる見込み)。再評価1回あたり≈B3 call 1回分(実績: 初回5.993/再生成6.673、`E2E_PLAN_01.md` §13・§14、`run_mey_01/raw_usage_log.jsonl`のstage=storyline_b3の2 call: in 3833 tok・out 2979/3404 tok)+再評価note分の入力増=**見積≈6.7〜7.5 JPY/回**(推定)。
- 区分: **承認済み範囲内**(ユーザー§2「最低2件」「初回≤1なら再評価」「未達STOP」「最小変更」に合致。Prompt文面1か所変更はユーザー§2/§3が「既存のFact選定Prompt…の必要十分な修正」を明示承認済み)。

### 3-2 案II: Prompt本文不変 + moduleで下限強制(再評価1回、再評価noteのみ追記)+ STOP
- 変更箇所: 案Iの(b)〜(f)のみ。`USER_PROMPT_TEMPLATE`は不変(prompt sha固定test維持)。再評価時のみ`REEVAL_APPEND_NOTE`を付加。
- 欠点: 初回Promptに「3件未満でも構わない」が残り**仕様(原則最低2件)と矛盾**する。現行挙動(2/2回で1件)から、**ほぼ毎回再評価callが発生する見込み**(推定。実績根拠はmey 2/2のみ)で、再評価1回分(≈+7)が常時コスト。Prompt本文は変えないが、再評価noteはPrompt文面の追加=Gate対象外とはならない(「Prompt不変」ではなく「基底Prompt不変」)。
- 区分: 承認済み範囲内だが仕様矛盾が残る。

### 3-3 案III(推奨): 案I + 下流choke pointでの二重ガード
- 案I全体に加え、(g) `er053_b3_deterministic_producer_01.py::_check_inputs`(全分岐合流点=runner:420、CURRENT_SPEC:1169)で`selected_fact_ids`のVERIFIED数<2をproducer errorに(`AnnotationProducerError`、課金前STOP)、(h) `er053_b3_annotation_contract_01.py` V5の`K<1`を`K<2`へ(W-1入口。**契約sha/producer規則sha(`rules_sha256`)への影響を実装時に確認**)。これで「B3 moduleを通らない経路(resume/再利用/手動で置いたbrief/将来の別caller)」もW-1に到達する前に必ずSTOP。(f)のrunner側再利用チェックは(g)で代替できるため省略可(Opusに確認)。
- リスク: 既存の1件artifact(mey初回/現行)を再利用しようとするとSTOPする=**意図どおり**。既存testのうち「1件を有効例とするfixture」は更新が必要(下記§3-6)。
- 区分: **承認済み範囲内**(ユーザー§3「B3のretry/regeneration/resume/再利用経路にも適用」「Validator・決定論B3 producer・下流Writerとの整合を確認し必要十分な修正」に直接対応)。

### 3-4 比較
| 観点 | 案I | 案II | 案III(推奨) |
|---|---|---|---|
| 仕様矛盾(Prompt「3件未満でも可」) | 解消 | **残る** | 解消 |
| 再評価callの頻度(推定) | 低(初回で満たす見込み) | 高(常時+1) | 低 |
| resume/再利用経路の下限評価 | (f)で評価 | (f)で評価 | **(g)(h)で必ず評価(単一合流点)** |
| 変更ファイル数 | 2(b3 module, runner)+test | 2+test | 4(+producer, contract)+test |
| Prompt Gate対象変更 | あり(1か所) | 追記noteのみ | あり(1か所) |
| 新品質基準の混入 | なし | なし | なし(下限値2はユーザー決定) |
| 推奨 | 〇 | × | **◎** |

### 3-5 新品質基準(USER_DECISION_REQUIRED候補)として**採用しない**ものの候補列挙
- 採用FactがWriter本文で使用されたかの恒久的自動照合(現行に無し。再生成時の手動突合で足りるため新設しない)。
- Factの関連性スコア・最小スコア閾値の新設/上限件数hard cap。
- 再評価時にStorylineを再決定してよいか: 現Promptは「Storyline決定→Fact選定」の1call内。案I〜IIIの再評価noteは「`topic`の範囲内でStorylineを見直してよい」と書くか「初回Storyline固定でFactのみ再評価」かが未決。**後者だとmeyでは再びF11のみ→STOPになるおそれ**(初回F02/F04等が「F11で説明可」と除外されたため)。ユーザー§2「中心テーマに関連するFactを再評価」は「Storyline固定」とは書いていない→前者(topic範囲内で見直し可)を既定案とするが、**Opus観点①でレビュー**。

### 3-6 Regression設計(モックLLM、決定論。ユーザー§3の6項目)
既存の`_make_parsed`/`_mock_client`(`er019_family_x_b3_production_wiring_01_test_01.py:35-60,118-128`)を流用。`SAMPLE_LEDGER_TEXT`はVERIFIED 2件+AMBIGUOUS 1件で下限境界・AMBIGUOUS非算入のテストに好適。
| §3項目 | テスト | 期待 |
|---|---|---|
| ①検証済み十分→≥2 | Ledger VERIFIED≥4、初回2件/3件/5件のモック | `result.attempts`不変・再評価0回・`final_n>=2`・callは1回 |
| ②旧挙動(1件)の検出 | 初回1件(`_make_parsed(["F1"],…)`)モック→validatorが`SELECTED_BELOW_MIN2`を返す。再評価モックが同じ1件→`B3MinFactsStop` | 1件で成功扱いにならない(現行の`test_success_on_first_attempt`は1件を成功と主張→**更新対象**) |
| ③既存2件正常例の不変 | 初回ちょうど2件(BAPE/`meta/run_regen_01`型)→再評価0回、`parsed`が入力と完全一致 | callは1回、evidence追記以外不変 |
| ④無関係/未検証Factを採用しない | 再評価モックがLedger外ID(`F99`)/`[AMBIGUOUS]`のみ追加→不採用扱い(`UNKNOWN_FACT_ID`技術エラーまたは下限非算入)。コードがFactを補完しないこと(再評価応答の`selected_fact_ids`をそのまま使い、コード側でIDを足さない)を、モック応答2件のIDと最終`selected_fact_ids`の集合一致で確認 | STOPまたは2件確保のみ。コード追加ID=0 |
| ⑤下限未達STOP | 再評価後も1件→`B3MinFactsStop`+`b3_min2_stop_record.json`生成、runnerは例外伝播し`selected_brief.md`/`annotation`を作らない(失敗終了時の最終成果物=audit記録のみ)。Ledger VERIFIED<2→APIモックcall数0でSTOP | `client.responses.create.call_count`==1(初回)+1(再評価)以下。無制限retryなし(call上限3を超えない) |
| ⑥Fact Lock・Writer・安全Gate維持 | 既存`er053_*_test`(contract/producer/c2/c4/c5/wiring)、`er019_family_x_entertainment_production_runner_01_test_01.py`、W-1 factlock testを**全件実行**し、1件fixtureの更新のみで他はPASSを確認。U-1(PROVENANCE_MISMATCH)・予算ガード・routingのtestが無変更でPASS | 差分はfixtureの件数更新のみ |
| 経路: resume/再利用/regenerate | runnerテスト: (i)`selected_brief.md`+1件evidenceありで再利用→producer`_check_inputs`(案III)でSTOP(API call 0) (ii)`--regenerate-stage storyline_b3`で再評価が走る (iii)初回経路で走る | 全経路で下限評価 |
| Prompt固定 | `test_b3_prompt_shas_pinned…`を新shaへ更新(案I/III)。`fact_test_definitions_sha256`・`developer_message_sha256`は**不変であることを維持assert** | 4テスト定義が不変 |
| DefaultOff | 本件はユーザー承認済みProduction仕様(11-7限定例外ではない)のため、flag無し・既定でON。flagを新設しない | — |

### 3-7 更新・撤去対象(旧規則・旧testの識別子)
- 更新: `test_success_on_first_attempt`(:130-138、1件を成功とassert)、`test_retries_once_then_succeeds_on_invalid_fact_id`(:140、good=1件)、`test_stops_after_two_failed_attempts`(:151)のfixture(selected 1件)。1件を有効出力として期待するtestは書き換える(不整合出力を期待値にしない)。
- 更新: Prompt:70-71の文言、`test_b3_prompt_shas_pinned_unchanged_by_model_change`のsha(案I/III)。
- 他のfixtureで1件selectedを有効とするtest(`er053_*_test`等)は**未確認**(実装時に全test実行で洗い出す)。
- 撤去する旧ルール文言: 「3件未満でも、Storylineが単独で成立するなら構いません」(:71)。実装後にGrepで残存0を確認。

### 3-8 推奨
**案III**。理由: (1)Prompt矛盾を解消し再評価頻度と費用を抑える (2)resume/再利用を含む全経路を単一合流点(producer/契約)で必ず評価 (3)全てユーザー§2・§3の範囲内で、新品質基準・別方式を含まない (4)再評価は最大1回・call上限3でユーザー「無制限retryなし」を満たす。USER_DECISION_REQUIRED候補は**なし**(A:既判断=ユーザー§2に承認原文。再評価時のStoryline見直し可否はB:承認範囲内で自己解決だがOpus観点①で確認)。

## §4 中東記事再生成計画(実装・Opus後の委任_02以降、本Phaseでは実行しない)
- 前提: Prompt/コード実装・test PASS・Opus条件AレビューGO後。`cd C:\Users\tensh\eigo-radio`、`TTS_EXECUTION_MODE=STANDARD`(音声は走らせないが従来どおり設定)、`PYTHONIOENCODING=utf-8`。各stageの**直前に**`tools/stop_scope_check_01.py --managed-id FAMILY-X-B3-FACT-MIN2-PRODUCTION-01 --run-dir <run_mey_01> --out <json>`でrc=0確認(rc=3なら新規API呼出なし)。
- 旧成果物の退避(PM_GOVERNANCE 2-3 Artifact supersession、新版が旧版をsupersede): 再生成前に`run_mey_01/_before_regen_02/`へ**copy**(`research_ledger`は除く=Ledger不変のため)。copy対象=`storyline_b3 ja_writer b1b a2 audit cost.json entry_point.json raw_usage_log.jsonl writer_run_summary.json console_regen_*_02.txt`。`_before_regen_01`は触らない。注意: `entry_point.json`は各run冒頭で上書きされる(runner:379)ため退避必須。`raw_usage_log.jsonl`はappend(`cl.install`)なのでcopyを保全(累計はcost.jsonとlogで引き継ぐ)。
- Ledger不変の保証: `research_ledger/verified_fact_ledger.txt` sha256=`4f7d28b0bb7c280a34715215bc6c3d8b3c6b9127899a342c97cb1e6924cb8cf6`(現在値、Phase 1で取得)。runnerは毎回`run_research_and_ledger`を呼ぶが`verified_fact_ledger.txt`が存在すれば`reused:true`で戻る(runner:98-103)。各stage後にshaを再計算して一致、かつ`raw_usage_log.jsonl`の新規行に`stage=research`/`ledger`が無い・`web_search_call`=0を確認。`research_ledger/`内ファイルのmtime不変も確認。
- 実行(各1回、E2E_PLAN §14の形式を踏襲):
  1. `--theme "中東情勢が悪化、イエメン・サウジ周辺で攻撃続く" --slug middle_east_yemen_saudi --out-dir C:\Users\tensh\eigo-radio\er019_output\middle_east_yemen_saudi\run_mey_01 --run-label MEY-E2E-01 --budget-jpy <後述> --stage storyline_b3 --regenerate-stage storyline_b3`(theme/run-labelは`entry_point.json`のargsから取得した現行値)。完了後に**採用Factが≥2か、evidenceの`min2_policy`、`b3_min2_stop_record.json`の有無を確認**。≥2でなければここで停止(STOP、原因記録、再実行しない)。
  2. `--stage writer --regenerate-stage writer`(新注記版のW-1。U-1 PROVENANCE_MISMATCH回避のため必須)。
  3. `--stage advanced --regenerate-stage advanced`(Advanced+RF b1b)。
  4. `--stage standard --regenerate-stage standard`(Standard+RF a2)。
  - 各コマンドで`--stop-after`既定=standard。音声工程はrunnerに存在しない(Mandatory STOP)。`tee`でconsoleを`console_regen_*_03.txt`に保存(`_02`は前回分)。
- テキストQA: runner内QA(STRUCTURE_PASS、numbers_missing/added、IOL、記号QA、RF)の結果を`a2/audit`・`b1b`・`ja_writer/runtime_evidence.json`から取得。**採用Factの本文使用の突合**(ユーザー§4)=採用各Factの固有名詞・数字・帰属が`ja_writer/revision2.md`・`b1b/article.md`・`a2/article.md`に現れるかを手動表で照合(§3-5のとおり自動gateは新設しない)。Ledger外の具体描写の突合は§14の手法(14項目突合)を踏襲。
- 費用見積(出典付き):
  - 前回再生成実費23.260(B3 6.673/W-1 R0-R2 14.264/Adv 0.343+RF 0.92/Std 0.270+RF 1.03、`E2E_PLAN_01.md` §14表、`run_mey_01/cost.json`のstage別合計と整合)。
  - **最小**(初回で≥2): 23.3(下流の入力増分は小さいと仮定。推定)。**再評価1回あり**: +6.7〜7.5(B3 call 1回分、出典=B3初回5.993/再生成6.673)=約30.3。**上限見込み**: 下流の入力増+再評価で≈33(推定、実績はFact 3〜5件のrun比較で確認可)。
  - 累計: 前回79.881 → 103.2〜112.9(≤180、残67〜77)。**個別Cap180内**。音声が将来承認されれば+25〜30(E2E_PLAN §15記載の見込み)で約129〜143、180内。
  - **予算ガード注意(事実)**: `efam.assert_budget_ok`は`raw_usage_log.jsonl`の累計(現在79.881、`compute_cost_jpy_so_far`実測)と`--budget-jpy`を比較する。前回の110では上限見込み112.9を超えうるため、`--budget-jpy`は**少なくとも120〜130(≤180)**とする必要がある。これは個別Cap内の運用値でありFable決定(Cap自体は不変)。
  - 当日(JST 2026-10-19)の累計はFZQI等の別案件費用を含むため**未確認**(Phase 2開始前に`daily_dev_cost`相当で再集計)。
- Research再実行が起動しないことの保証: 上記ledger sha不変・research/ledger stageの新規API行0・`web_search`行0。

## §5 ユーザー提示物(§5の8項目)の取得元対応表
| # | 項目 | 取得元artifact |
|---|---|---|
| 1 | 新B3のFact数 | `storyline_b3/fact_selection_evidence.json`の`selected_fact_ids`長、`min2_policy` |
| 2 | 採用FactのIDと具体的内容 | 同`selected_fact_ids`+`research_ledger/verified_fact_ledger.txt`の該当ID行(claim/scope/conditions/numeric_value)、`storyline_b3/selected_brief_annotated.md` |
| 3 | 不採用FactのID(重要な理由) | 同`fact_tests[]`のdecision=excluded + reason |
| 4 | 前回とのFact選定差分 | `_before_regen_02/storyline_b3/fact_selection_evidence.json`(前回=現行、F11のみ)と新evidenceの差分。初回(`_before_regen_01`、F11のみ)も参考 |
| 5 | 再生成された**日本語記事の全文** | **存在する**: `ja_writer/revision2.md`(W-1 R2最終JA、1行目が題)。R0/R1は`ja_writer/original.md`・`revision1.md`(中間)。Family Xは日本語記事がProduction成果物 |
| 6 | Standard/Advanced英文 | Advanced=`b1b/article.md`(+`b1b/parts.json`)、Standard=`a2/article.md`(+`a2/parts.json`)。確認結果=`a2/audit`のQA(STRUCTURE_PASS等)、RF結果(Review Queue)、`writer_run_summary.json` |
| 7 | Fable評価 | Fableが§4突合表とユーザー§4条件で作成(本Phaseでは作らない) |
| 8 | 実費・残予算・配線状況 | `cost.json`、`raw_usage_log.jsonl`、OPEN-420/CURRENT_SPECのStatus |

- 英文リンクの提示方法(**既存の仕組みの事実**): 音声なしのテキスト確認ページは**既存に無い**(`er019_*_page_*.py`はいずれも音声付き試聴ページ。`tools/build_family_z_hr_review_page.py`はZ HR用)。ユーザー§5が「試聴ページ生成へ進まない」と禁止しているため、候補(Fable判断):
  - 候補(a): Pagesに**音声なし・テキストのみ**の確認ページを新設(`user_test/<名>/index.html`、日本語全文+Advanced/Standard英文+採用Fact表)。既存`build_family_z_hr_review_page.py`のHTML構造が流用可。ただし「試聴ページ」の定義との境界が曖昧→Fableが禁止範囲に含まれるか判断。
  - 候補(b): Fableがユーザー報告本文に日本語記事全文・英文を直接掲載し、リンクは付けない/GitHub上の`b1b/article.md`等のblobリンクのみ併記(blobは「raw/blob以外」要件に反するため補助扱い)。
  - 候補(c): Claude artifact等の別媒体(メモリ上「音声はartifactで」とあるが本件は文章)。
  - 本Phaseでは作成しない。

## §6 Opus独立技術レビュー観点案(条件A: 新しい構造・処理フロー、5件以内)
1. **再評価の定義**(§3-5): 再評価noteが「`topic`範囲内でStorylineを見直してよい」か「Storyline固定」か。固定だとmeyで再びF11のみ→STOPの恐れ、見直し可だと「数合わせ/関連性の低いFactを引き込む」リスク。4テスト(原則除外寄り)と下限2件の相互作用(LLMが除外寄りの判定と下限強制の板挟みで不整合なfact_testsを返さないか)。
2. **「検証済み」の定義**: 下限算定を`[VERIFIED]`限定とし`[AMBIGUOUS]`を数えない解釈の妥当性、およびLedgerの`[VERIFIED]`が2件未満のとき即STOP(API呼出前)の妥当性。ユーザー§2「AMBIGUOUS取扱い維持」との整合。
3. **全経路評価の完全性**: resume/再利用/`--stage storyline_b3`/手動brief差し替えの全てが、producer`_check_inputs`(下限2)+契約V5を通ること、およびb3 module側の再評価との二重評価で不整合(再評価済みevidenceとproducer判定のズレ)が出ないこと。契約V5変更の影響範囲(`rules_sha256`、既存artifact、`er053_*_test`のK=1 fixture)。
4. **call上限と失敗終了時の成果物**: 最悪3 call、STOP時に`b3_min2_stop_record.json`のみ残り`selected_brief.md`/注記/下流を作らないこと、runner:412-416の再利用分岐が「STOP後に不完全なbriefを再利用」しないこと(failed-run artifactの再利用防止)。
5. **波及範囲**: `er036`(Family Y Trial)が同関数を無変更importしている点。floorを既定ONにするとY Trialの挙動が変わる→Xのみ強制する引数化(`min_selected`既定)かの設計、RLCT(er082)複製を触らないこと、Family Z無影響の確認。

## §7 E-1 既存仕様・過去Trial照合(Grep結果と分類)
| 項目 | 結果 | 分類 |
|---|---|---|
| B3 Fact選定のProduction仕様(4テスト・Selected Fact Brief・LLM1 call) | CURRENT_SPEC:1157-1171(Family X Production経路、`PRODUCTION_WIRED`)、:1167-1169(経路図: storyline_b3→決定論B3 producer→契約V1-V10→W-1)、:1190(U-1)、:1213・:1230(B3/R0〜R2 Sol統一) | **A**(既存仕様あり=今回変更の基底) |
| 採用数の**下限**を規定する既存仕様 | CURRENT_SPEC/DECISION_LOG/OPEN_ITEMSに「3〜5件目安」「下限」の仕様行は**無い**(Grep `3〜5件|採用Fact数|3件未満`=該当0)。唯一の規定はmodule内Prompt:70-71 | **C**(下限2件はユーザー2026-10-19の真に新規の承認済み仕様) |
| 決定論B3 producer | CURRENT_SPEC:1169。`llm_calls=0`、全分岐合流点 | A |
| Fact Lock | CURRENT_SPEC:1157-1171(W-1 Fact Lock Writer)、:1172以降 | A(不変) |
| Select-then-Verify(RLCT) | `TRIAL_FINAL_REPORT_01.md`:52,59-60,67,77,83,102-103。案2/案1+2=REJECTED。再選定/確認B3(35.354費用)の記述はあるが**「採用数の下限」は扱わない**。OPEN-410/411(Trial専用) | **B**(過去Trialあり・REJECTED。本件は検証後の再選定ではなく採用数下限で別物。RLCT方式は混入しない) |
| B3の件数に関する過去Trial | `er019_output/family_x_b3_diversity_trial_01`(hormuz/small_bag 各run 3件)、`er052_output/b3_*`(B3変種Trial、OPEN-233系)。下限2の検討は**無い** | B |
| mey実績 | `E2E_PLAN_01.md` §13(S2 B3: F11の1件のみ)、§14(再生成後もF11のみ)、§15(USER_DECISION_REQUIRED #112)。ファイルで再確認済み | A(事実) |
| OPEN_ITEMS関連行(Grep `B3|Fact選定`) | OPEN-177,183,187,219,233,237,240,243,244,247,248,249,255,257,297,363,403,404,407,410,411,416(`OPEN_ITEMS.md`:358〜928)。直接関連=OPEN-416(:928、#112)、OPEN-410/411(RLCT Trial専用)、OPEN-403/404/407(B3を含むが内容は未確認) | 新規OPEN-420起票対象 |
| CURRENT_SPEC該当行(Grep `B3|Fact選定|Fact Lock|fact_tests|Select-then-Verify`) | :4, :829, :905-907, :1157-1171, :1190, :1213, :1224-1230, :1256, :1263, :1308, :1600-1604, :1672-1677, :1962, :2564, :2590 | 編集しない(仕様文追記は実装委任) |
| Family固有/共通 | §1-4: **Family X固有**(Y Trialが無変更import、Z不使用) | — |

SSOT: OPEN-420を`OPEN_ITEMS.md`へ新規起票(番号はcommit直前に再Grepで確定)、OPEN-416へ追記、DECISION_LOGへ末尾追記、`USER_DECISION_REGISTER_01.md`の#112を判断済みへ更新し新決定を次番号で登録、`REPORT_LEDGER.md`へ1行、`ACTIVE_TASK.md`先頭に固定ヘッダ。

## §8 費用見積(JPY0=本Phase。以下は将来Phaseの見積。出典付き)
| 段階 | JPY | 出典/根拠 |
|---|---|---|
| Phase 2 実装・test(モックのみ) | 0 | 有料API無し |
| Phase 3 B3(初回で≥2) | ≈6.7 | `E2E_PLAN_01.md` §14: B3再生成6.673(初回5.993) |
| B3再評価(必要時のみ) | ≈6.7〜7.5 | 同上+再評価note入力分(推定) |
| W-1 R0-R2 | ≈14.3(Fact増で≈15〜16の可能性) | §14: 14.264 |
| Advanced+RF b1b / Standard+RF a2 | 0.343+0.92 / 0.270+1.03 = 2.563 | §14 |
| 合計 | 23.3(再評価なし)〜30.3(再評価1回)、上限見込み≈33 | 上記合算(推定) |
| 累計(前回79.881) | 103.2〜112.9 / 個別Cap180 | `cost.json` total_jpy=79.881(実測)、`compute_cost_jpy_so_far`=79.881 |
| `--budget-jpy` | 120〜130を推奨(旧110では不足しうる) | `efam.assert_budget_ok`は累計log実測と比較 |
| 実LLM Regression(任意) | 0〜(必要ならFable判断) | モックで決定論的に足りる設計。実LLM確認はmey再生成自体がruntime evidenceになる |

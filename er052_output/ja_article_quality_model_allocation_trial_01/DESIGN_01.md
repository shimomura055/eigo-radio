# DESIGN_01: JA記事品質 工程別モデル配置Trial(Phase 1 設計・実現性確認)

管理ID: FAMILY-X-JA-ARTICLE-QUALITY-MODEL-ALLOCATION-TRIAL-01 委任_02
Status: DESIGN_ONLY(コード・API呼出なし。課金0円。Production/Prompt/Routing/SSOT不変)
区分: DEV/Trial専用。Production正式path(`er019_family_x_entertainment_production_runner_01.py`)には何も混入しない。
前提: 現行B3仕様(LLMのFact選定+決定論の注記producer)、W-1 Writer(R0 Fact Lock / R1 / R2)。OPEN-255(META記事品質懸念)の原因切り分け用。
関連(触らない): 並行委任_01の `AB_BASELINE_01.md` / `COST_VERIFICATION_01.md`。

## 0. 結論(要点)
- 指定構成(C/D/E)は**Production codeを1行も変えずに**Trial driverで実現できる見込み。ただし**Sol系の2点(effort=high受理、B3のjson_schema受理)は既存artifactで未確認**(3節・10節)。Astraも**B3のjson_schemaは未確認**。
- Writerのモデル差替は、`run_w1_writer`を呼ぶのではなく、**同moduleの純関数・Prompt定数をimportして、driver側で同一手順を組み直す**方式(方式Y)を推奨。`routing.require_model`は**変更せず**、既存のDEV/Trial用の正式口 `routing.require_model_or_override(process, model, override_reason)` を使う。
- 組み直しによる手順ドリフトは、**A構成(Luna/Astra)でstub clientに対してrequest payloadが`run_w1_writer`と完全一致する無課金テスト**で機械的に防ぐ。
- Sol model idは**`gpt-6.1-sol`を推奨**(価格登録・過去API実績あり)。ただし過去には `gpt-6-sol`(別id)をAPI呼出した実績もあり、**どちらを指すかをFable/ユーザーが確定**する必要あり(3節)。

## 1. 工程分割と、各工程の担当・固定/可変

| 工程 | 内容 | 実体(Production module) | モデル | A/C/D/E間 |
|---|---|---|---|---|
| ①B3-LLM | Fact選定+Storyline構築(LLM 1 call、json_schema) | `er019_family_x_storyline_b3_fact_selection_01.run_storyline_b3_selection(client, topic, ledger_text, model, effort)` | 案ごと | **modelのみ可変**。developer message / user template / fact test定義 / JSON schema は同一 |
| ②B3-決定論 | 注記・制約付与(LLM 0) | `er053_b3_deterministic_producer_01.produce_annotated_b3(out_dir)` | なし | Production同一(A/C/D/E、コード・規則とも同一) |
| ③R0 | Fact Lock初稿 | `er053_family_x_factlock_ja_writer_01`のPrompt構築関数 | 案ごと | modelのみ可変 |
| ④R1 | Revise(R0を入力) | 同上(`USER_TMPL`) | 案ごと | modelのみ可変 |
| ⑤R2 | Revise(**R1の生出力**を入力) | 同上 | 案ごと | modelのみ可変 |

- ①は`run_storyline_b3_selection`が`model`/`effort`を引数で受ける設計なので、**差替えにProductionの変更は不要**(Production呼出側は`vfl01.MODEL`=Lunaを渡しているだけ。B3関数内に`require_model`は無い)。
- ②は`produce_annotated_b3(out_dir)`が`out_dir/research_ledger/verified_fact_ledger.txt`と`out_dir/storyline_b3/{selected_brief.md,fact_selection_evidence.json}`から決定論で生成。案ごとにout_dirを分ければそのまま使える(LLM call 0、¥0)。

### 1-1. C案のB3は「A案のB3出力を再利用」を推奨(要Fable判断)
C案のB3はLuna、Aと同一モデル・同一Prompt・同一入力。B3を再実行すると(Lunaの非決定性で)選択Factが変わり、「R0/R1/R2のモデル配置だけの比較」にならなくなる。**A案の`storyline_b3`(b3_raw相当、selected_fact_ids、storyline)を複製して使う**ことで(a)交絡を除去、(b)約¥0.4節約。D/EはB3モデル自体が条件なので新規実行。これを設計上の既定とする。反対なら委任_03前に指示を。

## 2. W-1 Writer(R0/R1/R2)のモデル差替方式

### 2-1. 現状の固定箇所(`er053_family_x_factlock_ja_writer_01.py`、sha256 87339033ee0d8e1b84a989fad73819012e25d6b5ad9beac1a38ca4e93f2e4a38)
- module定数: `R0_MODEL="gpt-6-luna"`、`ASTRA_MODEL="gpt-6-astra"`(リテラル固定)
- `call_luna_r0`: `routing.require_model("FAMILY_X_FACTLOCK_R0", R0_MODEL)`、返却modelが`R0_MODEL`で始まらなければ`ProvenanceViolation`
- `call_astra`: `routing.require_model("FAMILY_X_FACTLOCK_REVISE", ASTRA_MODEL)`、同様のProvenance検査
- `run_w1_writer`: 冒頭で両require_model、`client.responses.create(model=<定数>, reasoning={"effort":"high"}, input=[...])`。previous_response_idなし。R0のみdeveloper=`DEVELOPER_MESSAGE`、R1/R2はdeveloperなし。
- 関数が定数をmodule globalとして直接参照するため、**引数でmodelを注入する口は無い**。

### 2-2. 検討した3方式
| 方式 | 内容 | 判定 |
|---|---|---|
| X: in-process monkeypatch | driver内で`w1.R0_MODEL`/`w1.ASTRA_MODEL`と`routing.PROCESS_MODEL_MAP`を一時的に書換えて`run_w1_writer`をそのまま呼ぶ | **不採用**。orchestrationは完全同一になるが、Model Routing Contractのfail-closed保護をprocess内で書換える=既存安全装置を迂回する形になる。 |
| **Y: 純関数import+driver側で同手順を再構成(推奨)** | Prompt構築・後処理・QA関数・定数をimportして再利用。API呼出部のみdriver側に持ち、modelは引数。modelゲートは`routing.require_model_or_override(process, model, override_reason)`(DEV/Trial用の既存正式口)で通す | **採用**。Production不変。ドリフトは2-5の等価テストで封じる。 |
| Z: Production moduleのコピー改変 | Writerをコピーして別モデル版を作る | 不採用(Prompt文字列の二重管理・byte一致の保証が弱い)。 |

### 2-3. 方式Yで再利用する(importのみ・複製しない)もの
`build_r0_prompt` / `build_r0_symbol_regen_prompt` / `USER_TMPL` / `postprocess_ja` / `clean_ja_for_next` / `detect_r0_echo` / `parse_brief_md` / `extract_title` / `verbatim_shas` / `er019_family_x_ja_writer_o_r1_r2_01`のDEVELOPER_MESSAGE・R0_PROMPT・SYMBOL_PREVENTION_BLOCK_JA・CONCRETENESS_CONTROL_AN3_BLOCK / `er003_audio_tts_asr_safety`の記号QA(`detect_prohibited_symbols`/`symbol_gate_requires_stop`/`build_symbol_violation_prompt_note`) / `er053_b3_annotation_contract_01.validate_annotated_b3`(W-1入口の契約検証。案ごとのout_dirで同じく通す)。
Prompt本文はmodule定数から**そのまま**使うため、byte-identicalが構造上保証される(別途Prompt shaを事前登録に記録、PREREGISTRATION_01 3節。無課金のimportで現在値を取得済み)。

### 2-4. driver側で持つもの(最小)
1. `call_writer(client, model, user, stage, developer=None)`: `responses.create(model=model, reasoning={"effort":"high"}, input=[...])`のみ。developerはR0のみ`DEVELOPER_MESSAGE`、R1/R2はなし。`previous_response_id`、temperature、max_output_tokens、service_tier、text.format は**送らない**(Productionと同条件)。返却model Provenance検査(`startswith(requested)`、不一致はSTOP)を同じ基準で実装。
2. orchestration(`run_w1_writer`と同順): 予算check → R0(+記号QA 1回再生成、残ればSTOP)→ `clean_ja_for_next` → `r0.md`保存 → R1(入力=`USER_TMPL.format(body=r0.md読戻し.strip())`、ファイル往復でCRLF→LFも同一)→ `r1.raw.md`保存(R1の生出力)→ R2(入力=`r1.raw.md`読戻し)→ `postprocess_ja`→`clean_ja_for_next`→記号QA(R2のみ同一R1 rawで1回再実行、残ればSTOP)。**`run_w1_writer`のこの手順を1対1で写す**。
3. 上限回数: 記号QA再生成はR0/R2各1回まで(Productionと同じ)。それ以上の自動追加なし。

### 2-5. Production不変・ドリフト防止の担保
- driver新規ファイルのみ追加(`er052_output/ja_article_quality_model_allocation_trial_01/`配下)。`er0*.py`のProduction/共有moduleは編集しない。実行前後に主要module shaを再計算して一致を`runtime_evidence`に記録。
- **等価テスト(無課金、実装委任で必須)**: stub clientで ①`run_w1_writer`(A設定=Luna/Astra)、②driver(A設定)を同じ入力out_dirに対し実行し、`responses.create`に渡る全request(model/reasoning/input/previous_response_id有無/追加kwarg有無)の列が完全一致、書出ファイル(r0.md/r1.raw.md/r2.raw.md)が一致することをassert。さらに記号QAの再生成/再実行/STOPの分岐もstubで同一になることを確認。
- `routing.require_model_or_override`を使う点: Production契約の既定は不変。overrideは理由文字列つきでログに出る(既存仕様)。override理由は「JA-ARTICLE-QUALITY-MODEL-ALLOCATION-TRIAL-01 DEV/Trial。Production不変」。
- driverは`er019_family_x_entertainment_production_runner_01`を**importしない**(Production経路への混入防止)。出力ディレクトリはProduction配下(`er019_output/`)ではなく`er052_output/ja_article_quality_model_allocation_trial_01/runs/`。

主要module sha256(A run_regen_01時点の`entry_point.json`記録と一致を確認済み。Writer/B3/producer/contractの4つが一致、jaw/routingは記録なしで現在値のみ):
| module | sha256 |
|---|---|
| er053_family_x_factlock_ja_writer_01.py | 87339033ee0d8e1b84a989fad73819012e25d6b5ad9beac1a38ca4e93f2e4a38 |
| er019_family_x_storyline_b3_fact_selection_01.py | 93d0e31e735057ae874bbf27be48449fdd5bd5188e535b0a280eada9d314b758 |
| er053_b3_deterministic_producer_01.py | 8899d0fa4a9b2274fcd79165b447ab02988d40f799cbca01e06df51a6f7155f2 |
| er053_b3_annotation_contract_01.py | 5f4c725e0b332e028b8285389532dedc28e067f29caf6c63863b0be4f0017885 |
| er019_family_x_ja_writer_o_r1_r2_01.py | a696d8f261033bc6d49054ce9805c32479abfd0b23825c21f93c5365d21cb8b0 |
| er006_model_routing_contract_01.py | 438df87d959fad3af7085c198c09bd2344d5ed308c98d78e574583373ab5c285 |

## 3. モデルid・対応状況(出典、新規課金呼出なし)
| 配置名 | model id | 単価 USD/1M(in/cached/out) | 出典 | effort=high | json_schema(B3) | 返却model実績 |
|---|---|---|---|---|---|---|
| Luna | `gpt-6-luna` | 0.10 / 0.01 / 0.50 | `er005_output/cost_baseline_01/pricing_snapshot.json`、`xm_prices_01.json`、routing contract | **確認済**(A run、Production) | **確認済**(Production B3、A run storyline_b3) | `gpt-6-luna`(A run `r0_meta.json`) |
| Astra | `gpt-6-astra` | 10.0 / 1.0 / 50.0 | 同snapshot(OFFICIAL_PRICING_PAGE_FETCHED、2026-10-08) | **確認済**(A run R1/R2) | **未確認**(B3での使用実績なし) | `gpt-6-astra`(A run `r1.response.json`) |
| Sol | **`gpt-6.1-sol`(推奨)** | 2.00 / 0.10 / 10.00 | 同snapshot(OFFICIAL_PRICING_PAGE_FETCHED、2026-10-09取得)、`xm_prices_01.json`(2026-10-10)。Standard short contextのみ | **未確認**(`gpt-6.1-sol`は過去に`medium`のみ使用) | **未確認**(Sol系のjson_schema実績なし。antenna Trialは自由JSON出力) | `gpt-6.1-sol`(antenna_trial_01のraw log `model_id`) |

補足と注意:
- **idの曖昧性**: 既存資料に`gpt-6.1-sol`(価格登録・antenna/b3 annotation Trialで使用、返却model_id実績)と、`gpt-6-sol`(FACTLOCK委任_07 `r3_minimal_01/sol_n1`でAPI呼出、返却model=`gpt-6-sol`、effort=high受理、1call ¥1.72)の2つがある。後者は価格がpricing_snapshotに未登録(`gpt-5.6-sol`のみ旧)。**PM_GOVERNANCE 25節(最新世代の原則)と価格登録の有無から`gpt-6.1-sol`を既定とする**。`gpt-6-sol`との関係(別物/旧alias)は**未確認**。
- `gpt-6.1-sol`の存在確認は、実装委任の最初に**無料のmodels取得**(`client.models.list()`、鍵は出力しない)で行う。effort=highとB3 json_schemaは本実行の最初のSol call(B3)自体で確認。受理されない場合は**STOP**し、**自動でmedium等へ降格しない**(過去`run_sol_n1.py`にあった「high失敗→medium再試行」は比較条件を崩すため踏襲しない)。
- 今回の委任ではモデル一覧取得を**行っていない**(不要な外部呼出を避け、実装前提確認の無料ステップとして実装委任へ回す)。

## 4. 入力固定
- Ledger: `er019_output/meta/run_regen_01/research_ledger/verified_fact_ledger.txt`、sha256 `ea0ce587e605beeac8f02315ae4520899156393bbba2e059d99f45988b7c5f56`(A run `entry_point.json`のledger_sha256と一致を確認)。driverは各案out_dirの`research_ledger/verified_fact_ledger.txt`へ**バイト複製**し、実行前にshaをassert。
- B3①入力: `topic`=A runと同一(`Meta Muse AI電話代行「人間コンシェルジュ」実験`、`entry_point.json` args.theme)、`ledger_text`同一、Prompt sha: developer `b4391b0387c54d39cf2ed095e7c00e028b13f173065ed0077b3a16f0fe37981a`、user template `d6fe9bc33ceccf4c4af3a44ce12b9d83ef7c2efe04de4dfbb2cf17adb02ff333`、fact test定義 `91513c8999a63439adb40d5c28a253e4cdbb438228ba1deda199d2ae6c6c5a8a`(A runの`storyline_b3/runtime_evidence.json`記録値と現在のmodule値が一致を確認)。
- B3: 全案`effort="high"`(Production `vfl01.REASONING_EFFORT`と同一)、retryは既存の技術retry(最大2試行、同一Prompt+RETRY_APPEND_NOTE)のみ。

## 5. 出力構造(案ごと `runs/<案>/`)
`runs/<A|C|D|E>/`(B旧仕様は委任_01の領分)。out_dirはW-1契約のlayoutに合わせ、依頼の平置きファイルは最後にexportする。
```
runs/<案>/
  research_ledger/verified_fact_ledger.txt          (sha assert)
  storyline_b3/ {selected_brief.md, fact_selection_evidence.json, selected_brief_annotated.md, annotation*.json, writer_constraints.txt, audit/}
  ja_writer/ factlock/ {r0.md, r0_with_tags.md, r1.raw.md, r2.raw.md, *.response.json}, original.md, revision1.md, revision2.md, runtime_evidence.json
  export/   # 依頼書どおりの名前へコピー
    b3_raw.json (response.output_text逐語), selected_fact_ids (1行1ID), storyline (1行), selected_brief_annotated.md,
    writer_constraints.txt, r0.md, r1.md, r2.md,
    usage.json, runtime_evidence.json
```
- `r0.md`=タグ除去後R0、`r1.md`=R1後処理後(`r1.p1.md`相当)、`r2.md`=最終R2。生出力は`ja_writer/factlock/`に残す。
- `usage.json`: stage別(b3/r0/r0_symbol_regen/r1/r2/r2_symbol_rerun) `input_tokens/cached/output_tokens/reasoning_tokens/usd/jpy/sec`、model requested/returned、合計。単価は`pricing_snapshot.json`登録値、為替160(既存`USD_JPY`と同じ。実装時に既存定数を参照して一致確認)。
- `runtime_evidence.json`: `model_id_requested`/`model_id_returned`(stage別)、response_id、prompt shas(事前登録項目)、module shas(実行前後)、ledger sha、override理由、開始/終了時刻、STOP有無。
- **A案**: `er019_output/meta/run_regen_01/`から上記構造へ**複製のみ**(新規課金0。usageは`raw_usage_log.jsonl`、model idは各`*.response.json`/`r0_meta.json`/`storyline_b3/runtime_evidence.json`から再構成)。複製後にsha一致を記録。注意: A runのB3 raw生文字列(response.output_text逐語)は既存artifactに無い場合があり(`fact_selection_evidence.json`は構造化済み)、その場合A/Cの`b3_raw.json`はparsed再構成であることを明記する(実装時に確認)。
- **C案**: `storyline_b3/`をAから複製(1-1)、`produce_annotated_b3`を新out_dirで再実行(決定論・¥0。結果がAの`selected_brief_annotated.md`とバイト一致することをassertして、再利用の健全性を確認)→R0(Astra)→R1(Luna)→R2(Luna)。
- **D案**: B3(Astra)新規→決定論②→R0(Luna)→R1(Luna)→R2(Luna)。
- **E案**: B3(Sol)新規→決定論②→R0/R1/R2(Sol)。

## 6. Blind提示
- 出力先: `user_test/ja_quality_model_allocation_01/index.html`(GitHub Pages、既存`user_test/`配下の慣習。音声なし。単一HTML、JSのタブ切替=同一画面)。
- 5本(A,B,C,D,E)のR2最終文のみ(タイトル+本文。`export/r2.md`の逐語)を「記事①〜⑤」へ割当。割当は`random.Random(<固定seed>).shuffle`(seedは実装時に定数化、BLIND_MAP_01に記録)。
- 画面・HTML・ファイル名・JS変数名・`<title>`・コメントに**モデル名/案名/stage名を出さない**(生成後に`gpt|luna|astra|sol|案`等をgrepして0件をassert)。「①〜⑤は順不同」の旨の一文のみ。
- 対応表は`er052_output/ja_article_quality_model_allocation_trial_01/BLIND_MAP_01.json`(seed、割当、各R2 sha)に**別保存**。**チャット報告には対応表・どの記事がどの案かを出さない**(ユーザー評価の後に開示)。リポジトリには保存(消失防止)、Pagesの公開対象path(`user_test/`)には置かない。
- 漏洩リスクの限界: 文字数・文体の差から案が推測される可能性は排除できない(機械的に均す改変はしない=比較対象を変えないため)。
- ユーザー評価の取り方(案): 5本の順位+各記事の「公開してよい水準か」+自由コメント。Pageに保存機能は付けず、チャットで回答してもらう。

## 7. 費用ガード・見積(JPY、為替160)
上限: **B3〜R2の5案合計 ¥200**(A/B再利用分は¥0。C/D/E**各1回のみ**、自動追加なし)。

A run実測tokenを基にした点見積(input/output。reasoning含むoutput。モデルでreasoning量は変わるため不確実性あり):
| stage | token(Aの実測 in/out) | Luna | Astra | Sol |
|---|---|---|---|---|
| B3 | 4078 / 4254 | ¥0.41 | ¥40.6 | ¥8.1 |
| R0 | 1772 / 3567 | ¥0.31 | ¥31.4 | ¥6.3 |
| R1 | 475 / 2236 | ¥0.19 | ¥18.7 | ¥3.7 |
| R2 | 723 / 1890 | ¥0.16 | ¥16.3 | ¥3.3 |

| 案 | 構成 | 点見積 | ×1.5(reasoning変動) |
|---|---|---|---|
| C | B3 Luna(再利用) / R0 Astra / R1 Luna / R2 Luna | ¥31.8(B3新規なら+¥0.4) | ¥47.7 |
| D | B3 Astra / R0 Luna / R1 Luna / R2 Luna | ¥41.3 | ¥62.0 |
| E | B3 Sol / R0 Sol / R1 Sol / R2 Sol | ¥21.4 | ¥32.1 |
| 合計 | | **約¥94.5** | **約¥142** |
(A参考: ¥35.6(実測合計)、実測`run_regen_01/cost.json`のB3〜R2。R1/R2のinput tokenは前段出力に依存して変動。出力tokenはモデル別のreasoning量で大きくぶれうる。)

ガード設計:
- **案ごとcap(3案を並列実行しても合計200を超えないよう案別に配分)**: C ¥65 / D ¥85 / E ¥50(=¥200)。各案を別processで走らせるため共有台帳を使わず、process単位で厳守。
- **実行前チェック(各API call直前)**: 当該案の累計実測+当該stageの保守見積(上表×1.5)が案capを超える場合は**実行せずSTOP**。`run_w1_writer`の`budget_check`と同じ位置(R0前/R1前/R2前/再生成前/再実行前)に置く。
- **事前ゲート**: 実行前に点見積×1.5の合計≤¥200、各案×1.5≤各capをassertして`estimate_01.json`に保存。超過見込みなら実行しない。
- **実測記録**: `usage.json`と`er005_cost_logger`のraw usage log(案別path)。累計をstage毎に`runs/<案>/budget_state.json`へ。
- 到達時の挙動: capまたは記号QA STOPで案が未完でも**その案の追加呼出はしない**(再実行はユーザー/Fable判断)。最大の単独支出はD案のB3(Astra、約¥41、技術retryで約¥81)とC案のR0(Astra、約¥31、記号QA再生成で約¥63)。

## 8. 補助評価(Fable/Claude側、人間判断の代替ではない)
機械チェック(無課金、export済みR2とLedgerに対して):
1. 文字数(タイトル除く本文)・文数・です/ます率、選択Fact数(`selected_fact_ids`)、使用tag数(`r0_meta.tags_used`)。
2. Fact忠実性: 数値・固有名詞のLedger照合(Trial専用の簡易照合scriptを実装委任で作成。`【中核数値】`対象外の数値が本文にあれば列挙)。
3. 制約文混入grep: `writer_constraints.txt`の各文(「この点は確定していない。」等)がR2本文にそのまま入っていないか。
4. 記号QA(`detect_prohibited_symbols`、ja)の結果、タグ残存(`TAG_LEAK_RE`)・R0復唱(`detect_r0_echo`)。
5. 生成時間(stage別sec合計)。
補助評価の結果は**ユーザーのBlind評価に先立って提示しない**(評価の誘導を避ける。Fable内部資料)。

## 9. 並列化(依存関係とクリティカルパス)
- 案内は**直列**(B3→②→R0→R1→R2。前工程出力依存)。
- C/D/Eの3案は**独立**: 別out_dir、別cost log path、別process。**同一processのスレッド並列は不可**(理由: `er005_cost_logger`の`_CONTEXT`・`_LOG_PATH`・`_ATTEMPT_COUNTERS`がmodule globalで、`logging_context`がスレッド間で競合しraw usage logのstage/themeが混線する)。**3 process並列は可**(各processが独自のglobalを持つ)。同時call数は3本程度でrate limit懸念は小さい(上限値自体は未確認)。
- 並列の副作用: 同時実行で経過秒が相互に影響しうる→`sec`は参考値扱い(補助評価5)。
- 直列化すべき箇所: 無課金の等価テスト→(合格後に)課金実行。Blind page生成は3案完了後(Aは既存、Bは委任_01)。
- 見込み: 1案の連鎖はAの実測で B3 約30秒+R0+R1 約42秒+R2 約33秒(合計約2〜3分、Sol/Astraで変動)。3案直列で約8〜10分、並列で約3〜4分。実装・テスト待ちの間に評価script/Blind page generatorを先行作成可。

## 10. 実現性の不明点・STOP候補
1. **`gpt-6.1-sol`のeffort=high受理**: 未確認(6.1-solではmediumのみ実績)。非受理ならE案が**指定構成(effort high)で成立しない**→STOP、降格せずFable/ユーザー判断。
2. **Sol/Astra のB3 json_schema(structured output)受理**: 未確認。非受理(400)ならD/E案のB3が成立しない→STOP。通常、受理されない呼出は課金されない見込みだが未確認。
3. **Sol id**: `gpt-6.1-sol` vs `gpt-6-sol`。確定してから実装委任へ。
4. **B3モデルがD/Eで変わるとFact選定が変わる**ため、D/EはR0入力が案ごとに異なる。比較は「配置全体の比較」であり、単一因子の効果分離ではない(PREREGISTRATION_01 6節)。
5. N=1(各案1サンプル)。モデルの非決定性と配置効果を分離できない。
6. Pages公開はpublic。META記事本文(R2)のBlind公開は既存`user_test/`と同運用だが念のためFable確認。
7. ユーザー指示の「STOP条件6点」原文を本委任で受け取っていない(PREREGISTRATION_01の草案は推定、差替え要)。
8. A案のB3 raw逐語(`output_text`)が既存artifactに無い可能性(5節)。無ければ`b3_raw.json`はparsed再構成の旨を明記(Aは課金0のため再取得しない)。

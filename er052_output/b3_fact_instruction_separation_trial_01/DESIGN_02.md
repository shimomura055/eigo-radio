# DESIGN_02: 確定した案Dの設計(Phase 2、Opus是正R1〜R5反映。Production不変更)

管理ID: B3-FACT-INSTRUCTION-SEPARATION-ROOTFIX-TRIAL-01 委任_03。DESIGN_01.mdを置換せず追記する(DESIGN_01の比較表は履歴として保持)。実装はTrial module(`b3sep_build_01.py`)のみ。

## 1. 確定した組立規則(PREREGISTRATION_02 2節と同一)
| 項目 | 規則 |
|---|---|
| Facts行 | 1 fact=1行 `- {claim}`、出典リンク除去。**並び順=B3の`selected_fact_ids`順**(R4) |
| AMBIGUOUS(R1) | Fact行末に決定論の固定限定文「この点は確定していない。」。台帳の`[AMBIGUOUS - …]`タグ原文はFact側に入れない(指示調のため)。比較用のDtag変種(原文保持)はpreviewのみでE1に4件ヒット→不採用 |
| `ambiguity_note` | 制約ブロックへ(`事実Nについて：…`) |
| 制約ブロック(R5) | 見出し`Writerへの注意(事実ではありません)：`+`- 事実{N}について：{notes_for_writer逐語}`。**台帳IDなし・【】なし**。Nは対応するFact行の番号(後工程の【事実N】と一致) |
| D-min | claimのみ |
| D-full(R4) | `（範囲：{scope}。条件：{conditions}）`をFact行へ追記。scope/conditionsが指示調検出器`IMP`に該当する場合は**Fact側に入れず**、制約側へ`事実Nの範囲/条件について：…`(実測: 9テーマのC0 idsで3件、openai F4/F7とstreaming F07の条件欄が実際に該当=「…として扱う」「…扱わない」「否定しない」) |
| 連結(R2) | `compose_news_field(facts_text, constraints_text)`の**1関数**がR0ニュース欄(=Writerが読む文字列)を作る(P-out)。注記済みFacts(【事実N】付き)も同じ関数に渡す |

## 2. evidence JSON設計(R2)
Productionの`fact_selection_evidence.json`の`selected_fact_brief_text`欄は**維持**し、中身を「LLM自由記述」から「決定論のFacts部」に置換する。新欄を2つ追加:
| 欄 | 内容 | 読む側 |
|---|---|---|
| `selected_fact_brief_text` | 決定論のFacts部(Storylineなし。`md_facts_of_json`が先頭Storyline除去規則に該当せずそのまま返す) | W-1注記工程(`annotated_json_from`/`md_facts_of_json`/`parse_brief_md`)。注記契約V1〜V10は無変更 |
| `writer_constraints_text` | 制約ブロック | Writer R0入力の組立のみ |
| `writer_news_field_text` | `compose_news_field`の結果(未注記版) | 再生成経路など、Writerへ渡す文字列を直接使う経路 |

## 3. 消費経路の網羅(E6、Productionは読むだけ)
| 経路 | Production箇所(読んだ範囲) | 採用時に必要な変更 | Trial moduleでの乾式結果 |
|---|---|---|---|
| (a) R0ニュース欄 | `er019_family_x_ja_writer_o_r1_r2_01.py` `build_original_prompt` L148-161(末尾に`"[ニュース]\n"+facts`)、W-1 R0 `er052_factlock_astra_e2e_runner_01.py` `worker_new_r0` L643-650(注記版briefのFactsを`run_ja_writer_o_r1_r2`へ渡す) | factsに制約ブロックを連結する**1箇所**(`compose_news_field`呼び出し。R0 Prompt文言は不変) | PASS 54/54(D-min/D-full x 27): R0 promptのPrompt前後部(テンプレート部)がProduction `build_original_prompt`と一致、制約見出しがちょうど1回 |
| (b) er019 entertainment runner | `er019_family_x_entertainment_production_runner_01.py` L159/174(evidence作成・戻り値)、L339(既存brief再利用)、L361(`run_ja_writer`へ)、L382/393(`efam.run_writer_stage`のadvanced/standardへ) | evidence作成時に`writer_news_field_text`も保存し、L339/361/382/393がそれを渡す(4〜5箇所) | PASS 54/54(同一文字列がR0 promptに入る) |
| (c) er012_e再生成経路 | `er012_e_family_entertainment_two_level_runner_01.py` L740-772(`run_writer_stage(…selected_fact_brief_text)`が`run_ja_writer_o_r1_r2`へ)、L1176-1195(`fact_evidence.get("selected_fact_brief_text")`) | L1185が`writer_news_field_text`を読む(1箇所) | PASS 54/54(JSON round trip後も同一) |
| (d) W-1注記系 | runner L225-239 `md_facts_of_json`/`annotated_json_from`、L212 `parse_brief_md`、L242 `dryrun_annotate`、dev adapter `er052_open233_polysemy_nb_dev_01.parse_brief_md` | なし(注記対象はFacts部のみ=制約はbrief外) | PASS 54/54: `md_facts_of_json`==決定論Facts、`annotated_json_from`+`compose_news_field`==dry-run注記+制約、dev adapterと`parse_brief_md`が同一結果 |
| (e) R1/R2・Astra | briefも台帳も渡らない(前段本文のみ) | なし | 静的確認のみ |
| (f) JA Fact Check(旧)/Lane A撤去対象 | `full_ledger_text`(台帳全文)を使用。briefは使わない | なし(Lane Aで撤去予定) | 静的確認のみ |
| 追加でProduction変更が要る固定箇所 | `build_selected_brief_markdown`(er019 L252)の置換、B3 Prompt手順5・schema `selected_fact_brief`の不使用化(Dはschema欄を残して無視してもよい=LLM出力は不変) | Production Prompt/code変更=ユーザー承認必須 | - |

## 4. 数値印(【中核数値】/【周辺数値】)と制約内の数字
Trialでは数値印を付けない(未解決)。制約ブロックにも数字が含まれる(例: 「約24時間48分」「183,211台」)が、Fact Lock規則5「印の無い数字は使わない」と整合する扱い(E9で制約由来の数字の記事転記は0件)。注記工程の数値印担当(Lane B)との分担はRESULT_01参照。

## 5. 既存仕様との整合(RESULT_01 8節に要約)
Fact Lock R0 Prompt・W-1 Trial構造・注記契約V1〜V10・B3 4テスト・Fact数目安・recheck_noteは不変。B3 Prompt(Production)は不変(Dは`selected_fact_ids`だけ使う)。ユーザー確定事項(7)「LLM出力はJSON Evidence必須(…最終Selected Fact Brief)」の読み方(briefをLLM出力とするか)が論点=新仕様候補Q1。

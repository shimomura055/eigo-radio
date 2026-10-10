# AB_BASELINE_01: A案(現行Production)・B案(旧仕様)の比較元artifact調査(Phase 1 read-only)

管理ID: FAMILY-X-JA-ARTICLE-QUALITY-MODEL-ALLOCATION-TRIAL-01 委任_01。API呼び出し・課金・生成・Production変更・SSOT編集なし(既存ファイルの読取とsha/トークン再計算のみ、費用0円)。

## 1. A案(現行Production W-1)の比較元artifact: META再生成run
run: `er019_output/meta/run_regen_01/`(2026-10-10 15:29:58Z開始、Ledger sha256=`ea0ce587e605beeac8f02315ae4520899156393bbba2e059d99f45988b7c5f56`)

| 項目 | 値 |
|---|---|
| Fact Ledger | `research_ledger/verified_fact_ledger.txt`(15 fact、MUSE-HC-001〜015) |
| 選択Fact | 2件(MUSE-HC-006, MUSE-HC-012)。`storyline_b3/fact_selection_evidence.json`の`selected_fact_ids` |
| storyline | 「Metaは…人間契約スタッフに任せるテストをしたが、適切な開示なしに始めたことを「ミス」と認め、人間コンシェルジュ機能を当面ロールバックした」 |
| B3出力 | `storyline_b3/selected_brief.md`(sha cc837162...)、決定論producer出力`selected_brief_annotated.md`(sha 55577fed...、producer=deterministic_v2)、`writer_constraints.txt`(2行の注意、sha 0b65e648...)、`annotation_manifest.json`(checks a〜e全PASS) |
| W-1 R0 / R1 / R2 | `ja_writer/original.md`(617字)、`revision1.md`、`revision2.md`(**A案R2全文**、990字) |
| runtime evidence | `ja_writer/runtime_evidence.json`: chain_method=W-1(`factlock_r0_luna__astra_r1_r2_independent`)。R0=gpt-6-luna、R1/R2=gpt-6-astra reasoning effort=high、developer_message=null、previous_response_id未使用(R2入力=R1生出力)、service_tier未指定(Standard同期) |
| Prompt sha | R0_PROMPT `6108a7cd...`、DEVELOPER_MESSAGE `d1fbb042...`、R0_BLOCK `74b94871...`、USER_TMPL(R1/R2) `313120e9...`、AN3 block `067030ff...`、記号防止block `0629ab47...` |
| 記号QA | R0/R2とも findings 0、再生成なし |

### stage別 token・費用・時間(raw_usage_log.jsonl・cost.json。円=USD×160)
| stage | model | in | out(reasoning込) | うちreasoning | 円 | 秒 |
|---|---|---|---|---|---|---|
| B3(storyline_b3) | gpt-6-luna | 4,078 | 4,254 | 2,293 | 0.406 | 32.3 |
| R0(w1_r0) | gpt-6-luna | 1,772 | 3,567 | 3,106 | 0.314 | 27.1 |
| R1(w1_astra_r1) | gpt-6-astra | 475 | 2,236 | 1,552 | 18.648 | 42.4 |
| R2(w1_astra_r2) | gpt-6-astra | 723 | 1,890 | 1,200 | 16.277 | 33.1 |
| 4 stage合計 | | | | | 35.645 | 134.9(timestamp 15:29:58→R2完了約15:32:14) |

(同runのcost.json total 38.462円にはAdvanced/Standard英訳・Risk Flaggerが含まれる。本Trialの比較対象外。)

参考: coffee run `er019_output/coffee_prices/run_l3_01/`(別テーマ。B3 0.696円/R0 0.543/R1 18.162/R2 19.664=計39.065円、R2 954字、秒: B3 58.8/R0 42.2/R1 32.9/R2 36.6)。

### 判断: A案は既存成果物の再利用(新規課金0円)で比較可能
- A案R2全文・各stage token・時間・prompt shaが全て既存artifactにある。再利用可。
- 注意: A案のB3選択は2 Factで、後述B案のB3選択(3 Fact)と**選択Factが異なる**(B3 LLM出力の揺らぎ)。5案を同一選択Factで比べたい場合、C/D/EでどのB3出力を固定するかの設計が必要(委任_02側)。

## 2. B案(旧仕様)の特定
### 2-1. 「X系統」の一次資料での確定
- 出典: `er052_output/factlock_writer_trial_01/astra_revise_matrix_02/DESIGN.md`および`tools/run_matrix2.py`。**系列A(=X) = ユーザーPromptのみ、developer/systemメッセージなし**、系列B(=Y) = 熟練編集者developer(Step1 F2文)。共通user message=`以下の記事:\n\n{前段本文}\n\n事実は変えずにエンターテイメント性をもっと上げた記事にReviseください。長さは800〜1000字程度でお願いします。`、gpt-6-astra、reasoning effort=high、R1入力=R0(タグ除去済)、R2入力=R1生出力、`previous_response_id`不使用、R3なし、記号禁止リストなし。
- `docs/pm/delegation_log/2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_18_result.md`も「Astra X系列=系列A」と記載。
- **重要**: 現行Production W-1のR1/R2 PromptはX系列と同一(`er053_family_x_factlock_ja_writer_01.py` L60-61 USER_TMPL、コメントに「系列Xユーザーメッセージ逐語。変更禁止」。USER_TMPL文字列のsha256 `313120e9...`を本調査で独立再計算し、runtime_evidenceのsha一致を確認)。よってA案とB案のR1/R2段は同一であり、**A/Bの差はB3→R0入力契約(とR0へ渡るFact選択)のみ**。

### 2-2. 5点の特定結果
| # | 項目 | 特定結果 | 出典 |
|---|---|---|---|
| 1 | 旧B3の選択Fact(META) | **MUSE-HC-006/010/012の3件**(010=従業員の機微情報共有の懸念が追加)。B3 LLM Prompt自体は現行と同一module(`er019_family_x_storyline_b3_fact_selection_01.py` sha 93d0e31e...がTrial provenanceと現行HEADで一致)。差は選択の揺らぎ+後段の組立方式 | `er052_output/factlock_astra_e2e_trial_01/runs/meta/shared/fact_selection_evidence_original.json` |
| 2 | 旧B3→R0入力形式 | `selected_brief.md`=Storyline+Selected Facts。**B3 LLMが書いたbrief文そのもの**(Fact文内に「これは機能の試験に関する話であり、Muse全体の停止ではない。」のようなWriter向け注意書きが混在)。これを注記仕様v2で`- 【事実N】`化(`runs/meta/new/storyline_b3/selected_brief.md` sha 6371e102...、3事実)。決定論assembler・別ブロックのwriter_constraintsなし | 同`runs/meta/old/storyline_b3/selected_brief.md`(sha 83c29bc2...)、`new/storyline_b3/selected_brief.md`、DECISION_LOG「B3-FACT-INSTRUCTION-SEPARATION-ROOTFIX」群(L20509〜20518) |
| 3 | 当時のR0 Prompt | `er019_family_x_ja_writer_o_r1_r2_01.py`のR0_PROMPT/DEVELOPER_MESSAGE+Fact Lock R0ブロック(`factlock_r0_block_sha256`=74b94871...で現行Production R0_BLOCK shaと**一致**)、gpt-6-luna、effort=high。C2(commit 11db202b)の差分にR0_PROMPT/DEVELOPER_MESSAGE/AN3/記号防止ブロック行の変更なし(git diff grep確認)。byte一致の機械照合は未実施 | `runs/meta/new/new_writer/r0_meta.json` |
| 4 | Astra R1/R2 X系統Prompt | 2-1のとおり(developer message**なし**、effort=high、sha 313120e9...)。当該META runの`r1.response.json`でもdeveloper_message null、previous_response_id_used false、model=gpt-6-astra | `runs/meta/new/new_writer/r1.response.json`/`r2.response.json` |
| 5 | R1→R2受け渡し | previous_response_idなし。R2入力=R1生出力。現行A案と同一方式 | 同上 |

### 2-3. METAで旧構成のR2日本語記事は既に存在するか
**存在する**(既存成果物の再利用=新規課金0円で比較可能)。

| 項目 | 値 |
|---|---|
| 場所 | `er052_output/factlock_astra_e2e_trial_01/runs/meta/new/new_writer/r2.raw.md`(R0=`r0.md`、R1=`r1.raw.md`、`r1.response.json`/`r2.response.json`) |
| 生成日時 | 2026-10-09(R0 00:33:17Z、R1 00:34:14Z、R2 00:34:58Z) |
| model | R0=gpt-6-luna、R1/R2=gpt-6-astra(effort=high) |
| Ledger | sha256 `ea0ce587...`=A案と**同一**(sha比較済) |
| 字数(R2) | 1,031字(A案990字) |
| B3 | 3 Fact(HC-006/010/012)、brief sha 6371e102...(A案のcc837162.../annotated 55577fed...と別物) |
| tokens | R0 in1,673/out1,922(reas1,362)、R1 in574/out2,508(reas1,820)、R2 in727/out1,597(reas855) |
| 円(登録単価で再計算) | R0 0.18 / R1 20.98 / R2 13.94 = 約35.1円(B3費用は当該Stage Rログ未集計) |
| 時間 | R0 18.2s / R1 47.6s / R2 34.6s |
| R2 Luna FC | LEDGER_COMPLIANT、MAJOR0/MINOR0(shadow_stop=false、記号Gate findings 0) |
| 付随 | 同runに旧Production腕(`runs/meta/old/`=Luna R0→R1→R2、Fact Lockなし)も存在。本Trialの「B案」は旧B3+X系統Astraのため`new/`側が該当 |

### 2-4. 再現可否と制約(新規生成でB案を再現する場合)
- 既存R2の再利用で足りるなら再現不要。ただしA案とB3の選択Fact数・内容が異なる(3 vs 2)ため、Fact集合が違う記事同士の比較になり、差の主因をB3出力方式へ帰属しにくい(交絡)。要設計判断(Fableへ)。
- 同一Fact集合で再生成したい場合の制約:
  1. **旧Fact Checker(`jaw.run_ja_fact_check`/must-fix系)がC2(commit 11db202b、2026-10-10)で物理削除**。旧Trial runner `er052_factlock_astra_e2e_runner_01.py` L645-680は`jaw.run_ja_writer_o_r1_r2(..., full_ledger_text=, original_must_fix=)`・`jaw.JAFactCheckStopError`・`jaw.call_fresh`のmonkey patchに依存しており、現行HEADでは動かない可能性が高い(**未実行・推測**)。旧構成のコードは`git show 11db202b^`(f71dbb41)から参照可能。
  2. METAの旧R0はmust_fix_applied=false(FCは本文を変えていない)ため、R0本文は「R0_PROMPT+Fact Lockブロック+注記済み旧brief→Luna」で再現可能で、FC撤去の影響は小さい。R1/R2は現行`er053`のUSER_TMPL/call_astraをそのまま使える。
  3. 現行W-1入口は`validate_annotated_b3`(決定論producerのmanifest付きartifactのみ受理、「注記なしB3の入力禁止」)。旧B3形式briefは契約検証で弾かれる見込みのため、R0単発関数を別途呼ぶTrial driver側設計が必要(委任_02)。
  4. B3 LLM出力は揺らぐため、再実行しても同じ選択は保証されない。固定するなら既存の旧brief(sha 83c29bc2 / 注記後 6371e102)を凍結入力にする(B3新規call不要)。
- 代替仕様への変更提案はしていない。

### 2-5. A案とB案の「B3→R0入力契約」の違い
| 項目 | B案(旧) | A案(現行Production) |
|---|---|---|
| Fact選択 | B3 LLM(同module)。META実績3 Fact | 同LLM。META実績2 Fact(揺らぎ) |
| brief文の作り方 | B3 LLMが書いたbrief文を採用。Fact文内にWriter向け注意書きが混在し得る | 決定論assembler(`er053_b3_deterministic_producer_01`、deterministic_v2)が選択Factの台帳文から再組立。注意書きは`writer_constraints.txt`へ別ブロックで逐語複写 |
| 注記(【事実N】・数値中核/周辺) | 注記仕様v2に基づく注記者が付与 | 同仕様を決定論producerが付与(LLM call 0、manifest a〜e検査PASS) |
| R0入力 | 注記済みbriefのみ | 注記済みbrief(範囲・条件の括弧付き)+writer_constraints連結 |
| 入口検査 | Trial用検査script | `validate_annotated_b3`(契約検証、課金前fail-closed) |
| R0/R1/R2 Prompt・model | 同一(Luna R0 / Astra X系列) | 同一 |
| R0後の旧Fact Checker | あり(FC+must-fix 1回) | 撤去済み(C2) |

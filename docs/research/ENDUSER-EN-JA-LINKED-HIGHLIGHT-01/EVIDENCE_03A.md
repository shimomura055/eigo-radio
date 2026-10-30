# ENDUSER-EN-JA-LINKED-HIGHLIGHT-01 委任_03A EVIDENCE(2026-10-30)

対象=X/Y/Z x Story/Comment/Preview/In One Line(Std/Adv、存在するパート)の英日連動ハイライトの全パート適用。asset=rev01-f(変更なし)。ユーザー原文=`docs/pm/delegation_log/2026-10-30_ENDUSER-EN-JA-LINKED-HIGHLIGHT-01_USER{,_02}.md`、設計=DESIGN_01/DESIGN_02_DELTA/INTEGRATION_03_01/**INTEGRATION_03_02**(本委任の統合結果と03Bへの申し送り)。

## 1. 実装(file:line)
- `er135_enduser_align_01.py`: method `tiered_dp_embed_v2`(:27)、構造確定`structural_groups`(:477)・順序対応`screen_equal`(:431)・DP周辺確率`_Para.marg`(:361)・`align_paragraph`(:502、judge引数は既定None)、埋め込みが要るテキストだけ`part_texts`(:588)、生成訳の構造検査`check_generated_part`(:772)、judge群の検証`_equal_except_judge`(:801)、`verify_article_align`(:819)。PARAMSに追加: det_len_lo/hi・eq_tau/eq_margin/tau_para_eq・soft_T/soft_p・judge_tau(:34-)。撤去: `eq_delta_ja/eq_delta_en`。
- `er135_enduser_page_01.py`: `GENERATE_KINDS`(:820)・`make_translator`(:828)・`generate_missing_translations`(:839)・`translation_coverage_of`(:869)・`build_link_targets`(:886)・`build_enduser(translate_llm=None)`(:1306)・`verify_consistency`の生成訳/link_targets検査(:1400-1420)。schema: `how`・`ja_source=generated`・`link_targets`・`generated_translation`・cost(`translate_*`)。
- `er135_enduser_translate_01.py:456` `build_ja_fields`(生成訳→ja段落+UTF-16オフセットのja_align)。`er135_enduser_align_judge_01.py`(M8のLLM確認。実装のみ・既定OFF)。`er006_model_routing_contract_01.py`に`ENDUSER_JA_ALIGN_JUDGE`追加。`er135_enduser_rules_01.py`: `JA_SOURCES_ALL`・`ASSET_TRANSLATION_KINDS`。
- `er135_enduser_page_verify_01.py:480` J3b(story以外のpartのクリック点灯検査)。`tools/ejh02_gold_eval_01.py`(soft採否の合成ずらし評価・det別計上)、`tools/ejh02_diff_gate_01.py`(許可keyにlink_targets/generated_translation)。
- test: align 49 + 新規link 17 + judge 7 ほか、合計 **290 PASS**(`.venv`、`pytest er135_enduser_{align,page,hook,translate,sync,sync_dropout,link,align_judge}_test_01.py`)。

## 2. 精度(gold=原文を読んで人手作成。M8なし・API 0)
| 集合 | 段落/EN文 | emit群 | 誤対応 | 合成ずらし受理 | 文数一致modeの誤ペア受理 | coverage(委任_02時点) |
|---|---|---|---|---|---|---|
| 調整用3記事(moon/fee/sur) | 50/265 | 190 | 0 | 0/336 | 0/67 | **83.0%**(Std 72.9 / Adv 96.5)<-71.3%(61.6/84.2) |
| 未見(pp+mg+ig) | 56/223 | 183 | 0 | 0/282 | 0/79 | **91.9%**(Std 96.0 / Adv 88.6)<-85.2% |
| held-out ig | 22/76 | 64 | 0 | 0/94 | 0/33 | **93.4%**<-88.2% |
段落取り違え(別段落JAと組合せ): 埋め込み経路 1/368・0/476・0/220。`det`(片側1文)は設計上意味検査をしない(段落対応は上流が保証)ため別計上(調整16/未見1/ig 0)。
新規X2記事(②AI広告・④散らかり、gold無し)の採用群を目視確認: ②59群・④62群(計121群)を読み、誤対応0(`evidence_03a/review_x2_x4_emitted_groups.txt`)。同一Agentの確認で、別Agent二重確認ではない。
開示: (1)soft_T/soft_pは調整3記事で決定(T=0.20,p=0.95。T=0.15でwrong 1が出る)。未見・igは同一値で誤0。(2)igは前委任でEN側veto調整に使用済み=準未見。(3)equal modeのeq_marginは0.06で合成誤ペア1件を受理したため0.03へ(受理0・正解ペア受理は同数197/203)。

## 3. 公開7dirの再produce(API 0、埋め込み新規call 0)
`hook_run`(正式produce+verify+Playwright PC/mobile)。ASR/埋め込みは既存キャッシュ再利用。dev index.html・音声・sync_*.json・assetは不変(diff Gate OK)。

| 記事 | Level | パート | 訳の状態(partsの内訳) | 英文数 | 連動(点灯可)文数 | 点灯率 | 方式 |
|---|---|---|---|---|---|---|---|
| X月 | std | story | approved_ja_manuscriptx3 | 46 | 33 | 71.7% | dp/order/soft |
| X月 | adv | story | approved_ja_manuscriptx3 | 35 | 33 | 94.3% | order |
<!-- X月: story coverage {'std': (0.7174, {'dp': 23, 'soft': 7, 'order': 3}), 'adv': (0.9429, {'order': 33})} / embedding api_calls=0 tokens=0 cost_jpy=0.0 degraded=[] asset=rev01-f -->
| X②AI広告 | std | story | approved_ja_manuscriptx3 | 39 | 36 | 92.3% | det/dp/order/soft |
| X②AI広告 | adv | story | approved_ja_manuscriptx3 | 34 | 34 | 100.0% | det/dp/order/soft |
<!-- X②AI広告: story coverage {'std': (0.9231, {'det': 3, 'dp': 14, 'soft': 7, 'order': 12}), 'adv': (1.0, {'det': 3, 'dp': 8, 'soft': 5, 'order': 18})} / embedding api_calls=0 tokens=0 cost_jpy=0.0 degraded=[] asset=rev01-f -->
| X④散らかり | std | story | approved_ja_manuscriptx3 | 47 | 32 | 68.1% | dp/order/soft |
| X④散らかり | adv | story | approved_ja_manuscriptx3 | 36 | 35 | 97.2% | dp/order |
<!-- X④散らかり: story coverage {'std': (0.6809, {'dp': 14, 'soft': 8, 'order': 10}), 'adv': (0.9722, {'order': 32, 'dp': 3})} / embedding api_calls=0 tokens=0 cost_jpy=0.0 degraded=[] asset=rev01-f -->
| Y再配達 | std | story | approved_ja_original_in_dev_pagex8 | 51 | 39 | 76.5% | det/dp/soft |
| Y再配達 | adv | story | approved_ja_original_in_dev_pagex8 | 37 | 37 | 100.0% | det/dp/order/soft |
<!-- Y再配達: story coverage {'std': (0.7647, {'dp': 25, 'det': 4, 'soft': 10}), 'adv': (1.0, {'order': 11, 'det': 3, 'dp': 15, 'soft': 8})} / embedding api_calls=0 tokens=0 cost_jpy=0.0 degraded=[] asset=rev01-f -->
| Y姓 | std | story | approved_ja_original_in_dev_pagex8 | 54 | 38 | 70.4% | det/dp/order |
| Y姓 | adv | story | approved_ja_original_in_dev_pagex8 | 42 | 40 | 95.2% | det/dp/order |
<!-- Y姓: story coverage {'std': (0.7037, {'dp': 30, 'det': 3, 'order': 5}), 'adv': (0.9524, {'order': 32, 'det': 2, 'dp': 6})} / embedding api_calls=0 tokens=0 cost_jpy=0.0 degraded=[] asset=rev01-f -->
| Zメロス | std | story | missingx3 | 53 | 0 | N/A | - |
| Zメロス | adv | story | missingx3 | 62 | 0 | N/A | - |
<!-- Zメロス: story coverage {'std': (None, {}), 'adv': (None, {})} / embedding api_calls=0 tokens=0 cost_jpy=0.0 degraded=[] asset=rev01-f -->
| Z雪女 | std | story | missingx3 | 47 | 0 | N/A | - |
| Z雪女 | adv | story | missingx3 | 48 | 0 | N/A | - |
<!-- Z雪女: story coverage {'std': (None, {}), 'adv': (None, {})} / embedding api_calls=0 tokens=0 cost_jpy=0.0 degraded=[] asset=rev01-f -->

Playwright(local、PC+mobile): X月 222 / X② 226 / X④ 224 / Y再配達 218 / Y姓 226 / Zメロス 174 / Z雪女 182 = 全件NG 0(`evidence_03a/repro/*_result_browser.json`)。注: X月は並行実行(2 Playwright+pytest同時)の初回に`adv_M7_kp_mode_no_ja_lit`が1件タイミング不一致(クリック後のmode遷移待ち、`x_moon_FIRST_RUN_flake_...json`)。単独再実行で222/0。
diff Gate(`tools/ejh02_diff_gate_01.py`、git HEAD比): 7dirともja_align・build_info(cost/files/ja_align/link_targets)以外の差分0。`evidence_03a/diff_gate.jsonl`。

## 4. Family x level x part 対象表(訳の有無・点灯率・方式)
`evidence_03a/link_targets_table.md`(全行)。要約:
- **訳あり(承認済み)=X/Y story のみ**: 点灯率は上表。方式=det/order/dp/soft(埋め込みは det 以外の段落のみ)。
- **日本語本文=英語対なし(`na_ja_only`、連動N/A)**: X/Y/Z Std の Preview・Comment(日本語で生成・表示済み。英語を新設しない)。
- **訳なし(`missing`、連動N/A・英語のみ表示)**: Adv Preview・Adv Comment・In One Line(X Std/Adv)・Z story(Std/Adv)。Y/Z に In One Line は無い(パート自体無し)。Y Adv に Comment 2 は無い。
- 03Bで生成すると `generated`(1文=1群、埋め込み0)になる。Previewは現行assetが訳を描画しないため asset 更新(J26)まで生成対象外(INTEGRATION_03_02 §3)。

## 5. 不具合是正(11-8)
ja_align初回取得直後の`verify_consistency`が1回不一致(②std_19/adv_18)。原因=`EmbedStore.ensure`のメモリ上ベクトルが丸め前float32、保存は6桁丸め。再読込後は別値になり、境界値の採否が食い違う(old: 20/20テキストでメモリ!=再読込、最大差5.0e-7。new: 0/20)。是正=メモリ上も保存値と同一に(`er135_enduser_align_01.py:268`)。test=`L2_EmbedStoreRoundingAndVerify`(2件)。

## 6. 可視性(UI変更なし、現状実測)
点灯した日本語訳が画面内に全体で見えた割合(再生中シーク後、ページの自動追従適用後。英語文は全サンプルで画面内)。サンプルは各level最大16群を等間隔(`tools/ejh03a_visibility_01.py`、`evidence_03a/visibility_local.json`)。
| 記事 | PC Std | PC Adv | mobile Std | mobile Adv |
|---|---|---|---|---|
| X月 | 5/13(38%) | 2/12(17%) | 0/13(0%) | 0/12(0%) |
| X② | 4/14(29%) | 1/16(6%) | 0/14(0%) | 0/16(0%) |
| X④ | 7/13(54%) | 4/13(31%) | 0/13(0%) | 0/13(0%) |
| Y再配達 | 14/15(93%) | 10/12(83%) | 2/15(13%) | 4/12(33%) |
| Y姓 | 12/16(75%) | 9/14(64%) | 1/16(6%) | 2/14(14%) |
mobile(390x844)ではX記事で0%(訳ブロックが英文の下=画面外)。PCでもAdv/X記事は6-31%。UI案(段落直後挿入/浮動キャプション/自動scroll)はユーザー判断(D)。

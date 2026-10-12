# FROZEN_PLAN_01 (Phase D 事前凍結、委任_03)

- frozen_at: **2026-10-12T21:06:53+0900** (epoch 1791806813.549)。この時刻より後にのみ有料callを開始する(各callの `started_at` を `cost.json` に記録し、報告で照合する)。
- モデル: gpt-6-luna、残予算上限 JPY35.56、caps={'ITEM_CAP': 3, 'RESERVED_SLOT_CAP': 3}
- 正解表本体: `GOLD_TABLE_02.md`(sha下記)。machine可読な正解(target)は `FROZEN_PLAN_01.json` の `m1`/`articles[].targets`。

## variant定義
- V0: Production現行shortlist + Production guidance
- V1+d: V0 + placeholder予約枠 + Trial guidance(b1抽出なし)
- V2: a(placeholder) + b1(extractor v2: cap3/transparency/core_span/包含重複除外) + 予約枠cap3(cap15外) + Trial guidance(d, M4反映)
- V3: shortlistのみ(b2ルール候補+c)。最終選定なし

## 受入基準
- negative_control_fail: N1/D6/D5/R3 の run単位で、最終5件の llm_noncompositional/placeholder_title 由来件数 == 0 をPASS。1件でもあればFAIL。
- negative_control_extraction: 陰性対照4記事×n=3のaccepted件数の1回あたり平均 <= 1 を合格(2.0超は枠埋め偏りと判定)
- D2_shortlist: V2 shortlistのexact再現 >=5/6(V0は2/6。予約枠cap3のため(a)placeholder 4件のうち最大3件が回復対象。cap3と抽出候補で押し出された件数も別途報告)
- D2_final: run単位: gold6件のうち >=2件が最終5件(exact or partial)。V2 n=2の両runでPASS
- D3_shortlist: run単位: b1_only 3件のうち>=1件がshortlist(exact or partial)。両runでPASS
- D3_final: run単位: gold6件のうち >=2件が最終5件(partial可)。両runでPASS
- D4_final: run単位: gold8件のうち >=2件が最終5件(partial可) かつ CD(cd=true)5件の最終内件数 >= V0最終のCD件数-1。両runでPASS
- M1_must1: Coffee Std/Adv n=3: pump&fistが抽出accepted 6/6 かつ V2 shortlist 6/6。未達ならSTOP
- MUST3_unit: MUST-3(正規化PASS・重複QA PASS・source_span整合)の判定単位は item単位(対象項目)とrun単位(run最終のgate全PASS)を分けて報告する。run単位=retry後の最終状態

## retry: Redundancy QA NGの場合のみ、Productionのretry方式(診断メモ追記、選定からやり直し)を1回(Production上限2回のうち1回)。V0はretryしない
## 主語込み近似: 近似: 限定詞/所有格で始まり3語以上で後続にbe動詞または-s/-ed/-es/-ing語尾語を含む、またはcore_span縮約が発生した場合を主語込みとみなす
## 実行順: m1 -> extract(全記事) -> final: [N1,D6] -> [D2] -> [D5] -> [D3] -> [R3] -> [D4] -> 任意 V1+d Coffee Adv n=2 (残額>=3)

## 記事・run数
- N1 (std, negative_control): 抽出n=3, 最終={'V0': [1], 'V2': [1, 2]}
- D6 (adv, negative_control): 抽出n=3, 最終={'V0': [1], 'V2': [1, 2]}
- D2 (std, positive): 抽出n=2, 最終={'V0': [1], 'V2': [1, 2]}
- D5 (std, negative_control): 抽出n=3, 最終={'V0': [1], 'V2': [1, 2]}
- D3 (adv, positive): 抽出n=2, 最終={'V0': [1], 'V2': [1, 2]}
- R3 (adv, negative_control): 抽出n=3, 最終={'V2': [1]}
- D4 (adv, regression_watch): 抽出n=2, 最終={'V0': [1], 'V2': [1, 2]}
- R1 (adv, shortlist_only): 抽出n=0, 最終={}
- R2 (std, shortlist_only): 抽出n=0, 最終={}

## sha256(凍結対象ファイル)
- `er064_kp_idiom_trial_01_extractor.py`: 834be4e26ab9b8916052e63b6841c7e9dfa009b72e15fc8ed90fc634fa645a85
- `er064_kp_idiom_trial_01_matcher.py`: 91ece944c42cdf075e4f076138d8b9045047b99e72852ae38bdca9633ff2def2
- `er064_kp_idiom_trial_01_pipeline.py`: 42b15c358d7c412b675a3eb6497299cde69bc376f763bb6444de30d1f6b3da28
- `er064_kp_idiom_trial_01_select.py`: e90db1719ffd83fff16d2007f109af749180fd2f41065beface7f970d1758793
- `er064_kp_idiom_trial_01_phase_d_run.py`: 3bfce4508f921a11b055cb087975adfa8090b690f227b5f8998f9ffc52fe9761
- `er064_kp_idiom_trial_01_test_01.py`: 34acf7e2754bb33f4efea397384ff9b473e6d60129c333b0ae7bab60700f8b7a
- `er064_output/kp_idiom_trial_01/prompts/extractor_prompt_v2.txt`: 168f682ee40e4a456740881eff3a94743dfaecf3f57b921ff55785003d953ee5
- `er064_output/kp_idiom_trial_01/prompts/trial_guidance_std_v2.txt`: ec88f2012433b4ff1f08f462c73109a8ae72a7ae0698b5f329e3d84b1760d467
- `er064_output/kp_idiom_trial_01/prompts/trial_guidance_adv_v2.txt`: 5488c8952b83c6ddbad7e7194130dc2f975efd3958a02d6692108156ec053455
- `er064_output/kp_idiom_trial_01/prompts/production_guidance_before.txt`: dadc60fe59fe1b05bc7cecfe04275fccadebf817f125a1d00dcbdf3c496084db
- `er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt`: 69d0e6ff548987896b561c0684e7aca10eae5b35a4974490fe92d42933d2e8f6
- `er064_output/kp_idiom_trial_01/phase_d/GOLD_TABLE_02.md`: 3d5e9227ed36767fb05e01743b83aed9ebc8e9998ad76660406dcfbdf49636c5
- `er064_output/kp_idiom_trial_01/phase_d/inputs\d2_std.md`: 4c4e8b177ecb5528b5778c8236c9871dbddd3e33f63a8cb32a0f235283ce0f54
- `er064_output/kp_idiom_trial_01/phase_d/inputs\d3_adv.md`: 7f584ce1ac50e38dde4155c618c248459f6793177f662b0888ebf59c418f8278
- `er064_output/kp_idiom_trial_01/phase_d/inputs\d4_adv.md`: 68d0c86750d69099761a8f5900ee35ee2345620e2109f9b9a2c16870a16c3e24
- `er064_output/kp_idiom_trial_01/phase_d/inputs\d5_std.md`: 5485ead5adf9a0559691c5fa62d1cbde9a5ad00ba53d50cd54d354e6116a986b
- `er064_output/kp_idiom_trial_01/phase_d/inputs\d6_adv.md`: 831fc54ac7eae1a719fc046f6a4c79ce4c285abfefc32405272ca7da459d9d63
- `er064_output/kp_idiom_trial_01/phase_d/inputs\n1_std.md`: 4392d8f2faf8bc0fd14ee50807ce9a95074daa91d00b2100d80486ab875bd680
- `er064_output/kp_idiom_trial_01/phase_d/inputs\r1_adv.md`: fd9193d7fa85cd156f165c724a20b0720ba848242b971dc3a3f329098fc9b71d
- `er064_output/kp_idiom_trial_01/phase_d/inputs\r2_std.md`: b58adac6fda7035ebd35e61598e51315edc45eb4cfe455c10dbfbde3e829e9d8
- `er064_output/kp_idiom_trial_01/phase_d/inputs\r3_adv.md`: a7b62938eb30eecd589a5fb617eba36f65b462b31a8d4384d8c1218daa73220d
- `er064_output/kp_idiom_trial_01/phase_a/inputs/v4_std_article.md`: a3cc7bb98af7526f55485b6a589354eeb36eb74a80bbd43a5e5be151915e4ff7
- `er064_output/kp_idiom_trial_01/phase_a/inputs/v4_adv_article.md`: d9b77190905d9060d578b2b21d634d48193decfd4c4eb90f1ae9bdb7da028e67

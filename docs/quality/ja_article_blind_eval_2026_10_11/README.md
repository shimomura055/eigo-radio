# JA記事 Blind評価 正式記録(2026-10-11)

管理ID: FAMILY-X-JA-MODEL-ALLOCATION-SOL61-PRODUCTION-WIRING-01 委任_01(元Trial: FAMILY-X-JA-ARTICLE-QUALITY-MODEL-ALLOCATION-TRIAL-01)。機械可読版: `blind_eval_record_01.json`。

## 0. ステータス
- E案(全段gpt-6.1-sol)=ユーザー正式採用(`APPROVED_FOR_PRODUCTION`、2026-10-11)。Production配線は別委任で実施。本書時点では`PRODUCTION_WIRED`ではない。
- C案=次点の比較基準(`SECONDARY_QUALITY_REFERENCE`)。
- 評価者=ユーザー(人間)、評価日=2026-10-11。検証範囲=N=1×3テーマ(結果を過大解釈しない)。

## 1. Trial目的・条件・モデル配置・入力仕様
- 目的: Family X日本語R2記事を工程別モデル配置で比較し、人間Blind評価で良い配置を調べる(出典: PREREGISTRATION_01/RESULT_01/RESULT_02)。
- 区分: DEV/Trial(Production code・Prompt・Routing不変、Research/Ledger再実行なし、英訳・RF・TTS・Audioなし)。
- モデル: Luna=`gpt-6-luna` / Astra=`gpt-6-astra` / Sol=`gpt-6.1-sol`。reasoning effort=high(全stage)。B3後段(注記・制約付与)は全案Production同一の決定論(deterministic_v2、LLMなし)。
- 呼出: developerはR0のみ、previous_response_idなし、R2入力=R1 raw、記号QA(R0再生成最大1回、R2再実行最大1回、残ればSTOP)。USD/JPY=160。
- Fact Ledger(固定): META=`er052_output/ja_article_quality_model_allocation_trial_01/runs/E/research_ledger/verified_fact_ledger.txt` sha256 `ea0ce587e605beeac8f02315ae4520899156393bbba2e059d99f45988b7c5f56`(15 Fact)。他2テーマは4節。
- Promptのsha256(PREREGISTRATION_01 3節、全テーマ同一Prompt定数):
  - b3_developer: `b4391b0387c54d39cf2ed095e7c00e028b13f173065ed0077b3a16f0fe37981a`
  - b3_user_template: `d6fe9bc33ceccf4c4af3a44ce12b9d83ef7c2efe04de4dfbb2cf17adb02ff333`
  - b3_fact_test: `91513c8999a63439adb40d5c28a253e4cdbb438228ba1deda199d2ae6c6c5a8a`
  - b3_json_schema: `ccfef73de9a12a232284786d9a52d935fcb3d66357e7f123febd2665c4903d51`
  - USER_TMPL_R1_R2: `313120e94232497290e7efac2df1210dc628a8a1b497bb04e7174b5a98442f7f`
  - R0_PROMPT: `6108a7cddaa9eaf31262354ba32d33e4683ccaf810d861f27e3dcc8972028366`
  - DEVELOPER_MESSAGE_R0: `d1fbb04224d346e79c588b8e69da4dcfe26e758ceefc71aa83d13ff7f216ed8d`
  - SYMBOL_PREVENTION_BLOCK_JA: `0629ab47a18ccb986844d8cff4ea087a9690eb8a7b8aefb28039496eec603b73`
  - CONCRETENESS_CONTROL_AN3_BLOCK: `067030ff53ecb76a4d1477a3deace07b3e1fac438a33cb873edbe045cf6927fe`
  - R0_BLOCK: `74b948719e14fd7184ff3719d36639ede7905e45cef95b97c1cca1a5638b2bf1`
- 比較配置:

| 案 | 配置(B3/R0/R1/R2) |
|---|---|
| A | B3 Luna / R0 Luna / R1 Astra / R2 Astra(現行Production、既存複製) |
| C | B3 Luna(A再利用) / R0 Astra / R1 Luna / R2 Luna |
| D | B3 Astra / R0 Luna / R1 Luna / R2 Luna |
| E | B3 Sol / R0 Sol / R1 Sol / R2 Sol(全段gpt-6.1-sol) |

注: B案(旧仕様)は旧仕様を正確に再現できず課金前STOP、ユーザー決定により比較Trial不要=**B案は実施せず(Trial終了)**。各案は複数stageが同時に変わるため、どの工程のモデルが効いたかは単一因子として特定できない。

## 2. Blind番号とモデル配置の対応表(評価後開示)

| テーマ | 記事① | 記事② | 記事③ | 記事④ | 出典 |
|---|---|---|---|---|---|
| meta | A | D | C | E | `er052_output/ja_article_quality_model_allocation_trial_01/BLIND_MAP_01.json` (sha `28ffe08f27360256…`) |
| hormuz | A | D | E | C | `er052_output/ja_article_quality_model_allocation_trial_01/BLIND_MAP_02_hormuz.json` (sha `06296d8210b20fb5…`) |
| coffee_prices | C | A | E | D | `er052_output/ja_article_quality_model_allocation_trial_01/BLIND_MAP_02_coffee_prices.json` (sha `d96dd27e9902fbc1…`) |

対応表は一次記録(BLIND_MAP)と照合し、ユーザー記載の対応と全件一致を確認済み。coffee_pricesのD案(記事④)は**記号QA不合格(全角括弧「USDA（米農務省）」残存、R2再実行1回後も残存、JASymbolCheckStopError)の評価専用R2**で、Production経路ではSTOPとなる。正式完成品ではなく、本記録のマスター/参照保存の対象外。META A/D・ホルムズA/Dも保存対象外(R2はTrial dirに残存)。

## 3. ユーザー評価結果(逐語)

- META 記事④＞記事③＞記事①・②
- ホルムズ海峡 記事③＞記事④＞＞記事①・②
- コーヒー 記事①・③＞記事④＞記事②

- モデル構成での評価: META E＞C＞A・D
- モデル構成での評価: ホルムズ E＞C＞＞A・D
- モデル構成での評価: コーヒー C・E＞D＞A

「＞」「＞＞」の評価差表記・同順位(・)はユーザー記載のまま。

結論(ユーザー逐語): E案は3記事すべてで最高評価グループ。C案も3記事すべてで上位評価。D案はB3をAstraにしても品質優位を示さず、費用も高い。E案は品質とコストの両面から正式採用。C案は次点の比較基準として保存。N=1×3テーマという検証範囲も明記し、結果を過大解釈しない。

## 4. 各記事の生成結果(path・actual model_id・選択Fact・文字数・stage別コスト)

### meta(Meta Muse AI電話代行「人間コンシェルジュ」実験)
- Fact Ledger: `er052_output/ja_article_quality_model_allocation_trial_01/runs/E/research_ledger/verified_fact_ledger.txt` sha256 `ea0ce587e605beeac8f02315ae4520899156393bbba2e059d99f45988b7c5f56`(15 Fact)

| 案(Blind) | R2 path | R2 sha256 | 返却model_id | 選択Fact ID | 本文字数(空白除く) | stage別円 | 新規合計円 |
|---|---|---|---|---|---|---|---|
| A(①) | `er052_output/ja_article_quality_model_allocation_trial_01/runs/A/export/r2.md` | `5437f68cc0a2ba0c3adfa5dc9d2ec5fe05ce3106e0513f6690ee3b6f2dc7cf90` | gpt-6-astra, gpt-6-luna | MUSE-HC-006, MUSE-HC-012 | 943 | B3=0.406, R0=0.314, R1=18.648, R2=16.277 | 35.6441 |
| D(②) | `er052_output/ja_article_quality_model_allocation_trial_01/runs/D/export/r2.md` | `31119baaf7cef145ff659d812f209b47fc29f2deaeea225a20aa4648f8b39fa5` | gpt-6-astra, gpt-6-luna | MUSE-HC-010, MUSE-HC-012 | 777 | B3=49.469, R0=0.464, R1=0.081, R2=0.154 | 50.1676 |
| C(③) | `er052_output/ja_article_quality_model_allocation_trial_01/runs/C/export/r2.md` | `4a64d7ade0549ee5f22cd5951eac114657a0231ae5b2f07732558824ede15705` | gpt-6-astra, gpt-6-luna | MUSE-HC-006, MUSE-HC-012 | 797 | R0=37.147, R1=0.095, R2=0.157 | 37.3988 |
| E(④) | `er052_output/ja_article_quality_model_allocation_trial_01/runs/E/export/r2.md` | `c34bdfb766f3e22d742d405180072ec3a1927f1d81baace583be33f6aa6d3a48` | gpt-6.1-sol | MUSE-HC-006, MUSE-HC-010, MUSE-HC-012 | 920 | B3=7.107, R0=8.373, R1=2.195, R2=3.871 | 21.545 |

### hormuz(ホルムズ海峡を通航する船舶への20％通航料をめぐる発言の撤回と市場反応)
- Fact Ledger: `er052_output/ja_article_quality_model_allocation_trial_01/runs_02/hormuz/E/research_ledger/verified_fact_ledger.txt` sha256 `9bd6834e68e7e4378ba0ebccdd84c0128df2a5cd0aca7c1e84df612ae77ae1a6`(12 Fact)

| 案(Blind) | R2 path | R2 sha256 | 返却model_id | 選択Fact ID | 本文字数(空白除く) | stage別円 | 新規合計円 |
|---|---|---|---|---|---|---|---|
| A(①) | `er052_output/ja_article_quality_model_allocation_trial_01/runs_02/hormuz/A/export/r2.md` | `cd70b53e38ff05a179cc4de901502fe9cff85aa85f4395051df99d6071052dc6` | gpt-6-astra, gpt-6-luna | HF-002, HF-006, HF-007, HF-009 | 900 | B3=0.41, R0=0.325, R1=15.27, R2=13.939 | 29.9445 |
| D(②) | `er052_output/ja_article_quality_model_allocation_trial_01/runs_02/hormuz/D/export/r2.md` | `5192f9d71f0fec1df14dc95d06f76369e51db958ea3fae1bb9101a08bbd59d01` | gpt-6-astra, gpt-6-luna | HF-002, HF-007, HF-009 | 719 | B3=51.731, R0=0.496, R1=0.087, R2=0.088 | 52.4026 |
| E(③) | `er052_output/ja_article_quality_model_allocation_trial_01/runs_02/hormuz/E/export/r2.md` | `64dfa062e8bbf5c7776b8077c8be83e84c8070fadf9e5e8ef46e178582c1951b` | gpt-6.1-sol | HF-002, HF-007, HF-009 | 1005 | B3=7.209, R0=7.332, R1=2.284, R2=2.59 | 19.415 |
| C(④) | `er052_output/ja_article_quality_model_allocation_trial_01/runs_02/hormuz/C/export/r2.md` | `5d5b2cd5f7707c59a1d5e5ec4bc5a887a1b10a0bd3db001125fd5ebf5566d099` | gpt-6-astra, gpt-6-luna | HF-002, HF-006, HF-007, HF-009 | 770 | R0=46.126, R1=0.092, R2=0.104 | 46.3226 |

### coffee_prices(コーヒー価格(coffee_prices))
- Fact Ledger: `er052_output/ja_article_quality_model_allocation_trial_01/runs_02/coffee_prices/E/research_ledger/verified_fact_ledger.txt` sha256 `e94a50c1d22686d52bd65beca4272650ecc8286de54629c3d8dfb42fa397ef7b`(18 Fact)

| 案(Blind) | R2 path | R2 sha256 | 返却model_id | 選択Fact ID | 本文字数(空白除く) | stage別円 | 新規合計円 |
|---|---|---|---|---|---|---|---|
| C(①) | `er052_output/ja_article_quality_model_allocation_trial_01/runs_02/coffee_prices/C/export/r2.md` | `2aa37319abbd4474c338d3a31a4fdb9809ad914bc8a464c2678efdfb93b0ae50` | gpt-6-astra, gpt-6-luna | COFFEE-003, COFFEE-009, COFFEE-010, COFFEE-014, COFFEE-015 | 823 | R0=42.499, R1=0.08, R2=0.08 | 42.6596 |
| A(②) | `er052_output/ja_article_quality_model_allocation_trial_01/runs_02/coffee_prices/A/export/r2.md` | `48fc4aeaffda5c97e63d6887caa9c1edf59f604b2c89c8a4937d46507e63d565` | gpt-6-astra, gpt-6-luna | COFFEE-003, COFFEE-009, COFFEE-010, COFFEE-014, COFFEE-015 | 908 | B3=0.696, R0=0.543, R1=18.162, R2=19.664 | 39.0646 |
| E(③) | `er052_output/ja_article_quality_model_allocation_trial_01/runs_02/coffee_prices/E/export/r2.md` | `742e7b6a7fe43f1bd8e6106fc5892720124e0a174c6bb1e0b63e70a5b3eb248a` | gpt-6.1-sol | COFFEE-001, COFFEE-010, COFFEE-014, COFFEE-015, COFFEE-018 | 872 | B3=11.533, R0=6.741, R1=4.184, R2=4.482 | 26.9401 |
| D(④) | `er052_output/ja_article_quality_model_allocation_trial_01/runs_02/coffee_prices/D/export/r2.md` | `7883dc289ee0f296958f201001a1ea161d49e3ab7a4fc49eb8ab088c184e310f` | gpt-6-astra, gpt-6-luna | COFFEE-009, COFFEE-010, COFFEE-014, COFFEE-015, COFFEE-019 | 849 | B3=75.514, R0=0.681, R1=0.101, R2=0.106, R2再実行=0.106 | 76.508 |

注: 円=USD×160。C案のB3はA案の再利用(新規0円、A側B3は約0.4〜0.7円)。coffee Aは既存run再利用。coffee Dは評価専用(R2再実行分を含む)。E案のみ全段gpt-6.1-sol。META/ホルムズ/コーヒーのE案新規費用は21.55/19.42/26.94円。出典: RESULT_01.md/RESULT_02.md/AUX_METRICS_*。

## 5. E案正式採用のユーザー決定(逐語)

> Family X日本語記事生成において、TrialのE案を正式採用する。Status：APPROVED_FOR_PRODUCTION。正式モデル配置: B3(Fact選定・ストーリーライン構築)=gpt-6.1-sol / B3後段(決定論的注記・制約付与)=現行仕様を維持(LLMなし) / R0=gpt-6.1-sol / R1=gpt-6.1-sol / R2=gpt-6.1-sol。B3→R0の入力契約は現行の新仕様を維持する。追加の個別品質Trial・モデル比較Trialは不要。今回のBlind評価を正式採用の根拠とする。ただし、Production Wiringに必要な技術テスト・統合テスト・runtime evidenceは省略しない。

> 人間によるBlind評価結果: META 記事④＞記事③＞記事①・② / ホルムズ海峡 記事③＞記事④＞＞記事①・② / コーヒー 記事①・③＞記事④＞記事②。モデル構成での評価: META E＞C＞A・D / ホルムズ E＞C＞＞A・D / コーヒー C・E＞D＞A。重要な結論: E案は3記事すべてで最高評価グループ。C案も3記事すべてで上位評価。D案はB3をAstraにしても品質優位を示さず、費用も高い。E案は品質とコストの両面から正式採用。C案は次点の比較基準として保存。N=1×3テーマという検証範囲も明記し、結果を過大解釈しない。

> OKマスターは記事品質の承認であり、音声・翻訳・TTS・RF等の承認を意味しない。特にMETAの完成音声は引き続き保留する。

## 6. C案は次点
C案(B3 Luna[A再利用] / R0 Astra / R1 Luna / R2 Luna)は3記事すべてで上位評価。次点の比較基準として保存(`ja_quality_masters/<slug>/C_reference_r2.md`、Status=SECONDARY_QUALITY_REFERENCE)。E案マスターとは区別する。D案はB3をAstraにしても品質優位を示さず費用も高かった。

## 7. 成果物path+SHA-256

(`docs/quality/`配下は`docs/quality/`相対、他はリポジトリroot相対)

| ファイル | SHA-256 |
|---|---|
| `docs/quality/ja_quality_masters/meta/E_master_r2.md` | `c34bdfb766f3e22d742d405180072ec3a1927f1d81baace583be33f6aa6d3a48` |
| `docs/quality/ja_quality_masters/meta/E_master_meta.json` | `0e4dfda93e7f9f11d28239e708a2a54eb1bfc77baa9f9ca5872172c0bc15ce4d` |
| `docs/quality/ja_quality_masters/meta/C_reference_r2.md` | `4a64d7ade0549ee5f22cd5951eac114657a0231ae5b2f07732558824ede15705` |
| `docs/quality/ja_quality_masters/meta/C_reference_meta.json` | `738df9558737f3edd03a7f3e4dbcb39f84bff2c48041d8a1ff1fc3e76da19f48` |
| `docs/quality/ja_quality_masters/hormuz/E_master_r2.md` | `64dfa062e8bbf5c7776b8077c8be83e84c8070fadf9e5e8ef46e178582c1951b` |
| `docs/quality/ja_quality_masters/hormuz/E_master_meta.json` | `3ef3d674f5926a9a65a985a87b53e0995e7de054a9d749af7fd1f1a5eba560a2` |
| `docs/quality/ja_quality_masters/hormuz/C_reference_r2.md` | `5d5b2cd5f7707c59a1d5e5ec4bc5a887a1b10a0bd3db001125fd5ebf5566d099` |
| `docs/quality/ja_quality_masters/hormuz/C_reference_meta.json` | `06884219a0857d0217f94d815f666f6bcbf4fe7e042c2a2c79e371251523e69c` |
| `docs/quality/ja_quality_masters/coffee_prices/E_master_r2.md` | `742e7b6a7fe43f1bd8e6106fc5892720124e0a174c6bb1e0b63e70a5b3eb248a` |
| `docs/quality/ja_quality_masters/coffee_prices/E_master_meta.json` | `4b5332203781191da362cfd5892dc4a44a1e46841ee93098e8531d3dd5ee8939` |
| `docs/quality/ja_quality_masters/coffee_prices/C_reference_r2.md` | `2aa37319abbd4474c338d3a31a4fdb9809ad914bc8a464c2678efdfb93b0ae50` |
| `docs/quality/ja_quality_masters/coffee_prices/C_reference_meta.json` | `461e6ed51771f9120ba573f06737a7e1064319f780b95c09eb2c1c60c5c76fe9` |
| `er052_output/ja_article_quality_model_allocation_trial_01/PREREGISTRATION_01.md` | `8b23b320cfbcf4fe789144a5c056271d9b359904988b41093a56dc9118a4d3e6` |
| `er052_output/ja_article_quality_model_allocation_trial_01/RESULT_01.md` | `8f2bf98fb8f5854f088c9ab2bc182c2be90d0333ffcff3f6aa1bd520c7bc8ab6` |
| `er052_output/ja_article_quality_model_allocation_trial_01/RESULT_02.md` | `55a2c7d5626f9a3a399fafe9f8f924a0879a514cdec0ceff0884c9d5aa7aee5c` |
| `er052_output/ja_article_quality_model_allocation_trial_01/BLIND_MAP_01.json` | `28ffe08f273602567cca80a8c31132abe004621fe4ad65d4bfa4e506be55e17f` |
| `er052_output/ja_article_quality_model_allocation_trial_01/BLIND_MAP_02_hormuz.json` | `06296d8210b20fb5df212f1160b4e4824b71518a5a7cf17e3b3ec803cfff35da` |
| `er052_output/ja_article_quality_model_allocation_trial_01/BLIND_MAP_02_coffee_prices.json` | `d96dd27e9902fbc1353e67ed4610c2e80515019907136150a744ecf81e84e1bf` |
| `er052_output/ja_article_quality_model_allocation_trial_01/AUX_METRICS_01.json` | `fcaa24f2c1cf38756037da0d17959ec101a76a30100d4240c25136f7ca950463` |
| `er052_output/ja_article_quality_model_allocation_trial_01/AUX_METRICS_02_hormuz.json` | `92e35114c96852f91290119a8c496998efc4c8f42af7bd2a557a8b7a81733136` |
| `er052_output/ja_article_quality_model_allocation_trial_01/AUX_METRICS_02_coffee_prices.json` | `610b2ed86517271ab5413f27f32139ca2772edc076cd02090a452ea307bbbac8` |
| `er052_output/ja_article_quality_model_allocation_trial_01/runs/A/export/r2.md` | `5437f68cc0a2ba0c3adfa5dc9d2ec5fe05ce3106e0513f6690ee3b6f2dc7cf90` |
| `er052_output/ja_article_quality_model_allocation_trial_01/runs/D/export/r2.md` | `31119baaf7cef145ff659d812f209b47fc29f2deaeea225a20aa4648f8b39fa5` |
| `er052_output/ja_article_quality_model_allocation_trial_01/runs/C/export/r2.md` | `4a64d7ade0549ee5f22cd5951eac114657a0231ae5b2f07732558824ede15705` |
| `er052_output/ja_article_quality_model_allocation_trial_01/runs/E/export/r2.md` | `c34bdfb766f3e22d742d405180072ec3a1927f1d81baace583be33f6aa6d3a48` |
| `er052_output/ja_article_quality_model_allocation_trial_01/runs_02/hormuz/A/export/r2.md` | `cd70b53e38ff05a179cc4de901502fe9cff85aa85f4395051df99d6071052dc6` |
| `er052_output/ja_article_quality_model_allocation_trial_01/runs_02/hormuz/D/export/r2.md` | `5192f9d71f0fec1df14dc95d06f76369e51db958ea3fae1bb9101a08bbd59d01` |
| `er052_output/ja_article_quality_model_allocation_trial_01/runs_02/hormuz/E/export/r2.md` | `64dfa062e8bbf5c7776b8077c8be83e84c8070fadf9e5e8ef46e178582c1951b` |
| `er052_output/ja_article_quality_model_allocation_trial_01/runs_02/hormuz/C/export/r2.md` | `5d5b2cd5f7707c59a1d5e5ec4bc5a887a1b10a0bd3db001125fd5ebf5566d099` |
| `er052_output/ja_article_quality_model_allocation_trial_01/runs_02/coffee_prices/C/export/r2.md` | `2aa37319abbd4474c338d3a31a4fdb9809ad914bc8a464c2678efdfb93b0ae50` |
| `er052_output/ja_article_quality_model_allocation_trial_01/runs_02/coffee_prices/A/export/r2.md` | `48fc4aeaffda5c97e63d6887caa9c1edf59f604b2c89c8a4937d46507e63d565` |
| `er052_output/ja_article_quality_model_allocation_trial_01/runs_02/coffee_prices/E/export/r2.md` | `742e7b6a7fe43f1bd8e6106fc5892720124e0a174c6bb1e0b63e70a5b3eb248a` |
| `er052_output/ja_article_quality_model_allocation_trial_01/runs_02/coffee_prices/D/export/r2.md` | `7883dc289ee0f296958f201001a1ea161d49e3ab7a4fc49eb8ab088c184e310f` |

(R2のsha256はファイルバイト列のもの。BLIND_MAPのr2_sha256は前後空白除去後テキストのsha256で値が異なるが、内容一致は照合済み(`blind_eval_record_01.json`の`blindmap_stripped_text_sha256`)。)

(`blind_eval_record_01.json`と本README自身のsha256は自己参照になるため記載しない。Git履歴で保証)

## 8. 再利用のための管理情報
- 管理ID: FAMILY-X-JA-MODEL-ALLOCATION-SOL61-PRODUCTION-WIRING-01(委任_01) / 元Trial: FAMILY-X-JA-ARTICLE-QUALITY-MODEL-ALLOCATION-TRIAL-01
- 評価日: 2026-10-11、評価者: ユーザー(人間)、検証範囲: N=1×3テーマ。
- 本評価を正式採用の根拠とし、**再評価・追加の個別品質Trial・モデル比較Trialは要求しない**。
- 品質回帰時の使い方: 新配線(E配置)で同テーマ/同Ledgerを再生成した場合、`E_master_r2.md`を第一基準として比較する。大きく劣化した場合は次点`C_reference_r2.md`とも比較し、原因調査を起票する。N=1のため、単一回の差を即「退行」と断定せず非決定性を考慮する。
- OKマスターは記事品質の承認であり、音声・翻訳・TTS・RFの承認ではない。METAの完成音声は引き続き保留。

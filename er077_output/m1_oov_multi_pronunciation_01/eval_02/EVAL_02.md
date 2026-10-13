# EVAL_02 M1 複数発音候補 Production module(OF-178 反映後)offline評価(API 0 / JPY0 / 既存Production無変更 / Ledger読取のみ)

- module=M1-MULTI-2026-10-13 / Ledger md5 前後一致: True
- 判定経路: Production 分類→_step_alternate_pass→M1 module(凍結候補注入、置換後 F1 再実行、置換位置が f1_explained に含まれること必須)

## 1. Melos said 12件 Before / F1のみ / 本module

| # | level/target/take | OpenAI転写 | Azure転写 | Before(OR) | F1のみ(OR) | module(OR) | module(両エンジン同意) | 理由(OpenAI / Azure) |
|---|---|---|---|---|---|---|---|---|
| 1 | std/raw/t1 | Mello said. | Mellow said. | NG | NG | PASS | PASS | m1:M1_MULTI_CANDIDATE_ACCEPT() / m1:M1_MULTI_CANDIDATE_ACCEPT() |
| 2 | std/raw/t2 | Mello said. | Mellow said. | NG | NG | PASS | PASS | m1:M1_MULTI_CANDIDATE_ACCEPT() / m1:M1_MULTI_CANDIDATE_ACCEPT() |
| 3 | std/raw/t3 | Mello said. | Melos said. | PASS | PASS | PASS | PASS | m1:M1_MULTI_CANDIDATE_ACCEPT() / prod:should_pass() |
| 4 | std/raw/t4 | Mello said, | Melo said. | PASS | PASS | PASS | PASS | m1:M1_MULTI_CANDIDATE_ACCEPT() / prod:should_pass() |
| 5 | std/slow6/t1 | Mellow said. | Mellow said.  | NG | NG | PASS | PASS | m1:M1_MULTI_CANDIDATE_ACCEPT() / m1:M1_MULTI_CANDIDATE_ACCEPT() |
| 6 | std/slow6/t2 | Mello said. | Mellow said. | NG | NG | PASS | PASS | m1:M1_MULTI_CANDIDATE_ACCEPT() / m1:M1_MULTI_CANDIDATE_ACCEPT() |
| 7 | std/slow6/t3 | Mello said. | Melos said.  | PASS | PASS | PASS | PASS | m1:M1_MULTI_CANDIDATE_ACCEPT() / prod:should_pass() |
| 8 | std/slow6/t4 | Mello said, | Mellow said. | NG | NG | PASS | PASS | m1:M1_MULTI_CANDIDATE_ACCEPT() / m1:M1_MULTI_CANDIDATE_ACCEPT() |
| 9 | adv/raw/t1 | Mello said. | Mellow said. | NG | NG | PASS | PASS | m1:M1_MULTI_CANDIDATE_ACCEPT() / m1:M1_MULTI_CANDIDATE_ACCEPT() |
| 10 | adv/raw/t2 | Mello said. | Mello said. | NG | NG | PASS | PASS | m1:M1_MULTI_CANDIDATE_ACCEPT() / m1:M1_MULTI_CANDIDATE_ACCEPT() |
| 11 | adv/raw/t3 | Mella said. | Mello said. | NG | NG | PASS | NG | m1:MULTI_CANDIDATE_NO_MATCH(no_phoneme_match_with_any_candidate) / m1:M1_MULTI_CANDIDATE_ACCEPT() |
| 12 | adv/raw/t4 | Mello said. | Melos said. | PASS | PASS | PASS | PASS | m1:M1_MULTI_CANDIDATE_ACCEPT() / prod:should_pass() |

集計: Before 4/12、F1のみ 4/12、module(OR) 12/12、module(両エンジン同意) 11/12。
委任_01(OF-178前)は module相当で 12/12 だった。差は『置換位置が Pattern A/B/C[f1_explained]で説明できること』を必須にした結果で、次語が歯擦音でない文(`Melos left`型)で F1 の benign(規則単複)に吸収される置換を不受理にしたため。

## 2. 合成24ケース(委任_01の期待との比較)

| 類型 | canonical | ASR | 委任_01期待 | module結果 | basis |
|---|---|---|---|---|---|
| T1 複数候補のうち1つ一致(Ledger別読み) | Melos said. | Mello said. | PASS | PASS | m1:M1_MULTI_CANDIDATE_ACCEPT |
| T1 複数候補のうち1つ一致(Ledger別読み) | Melos said. | Mellow said. | PASS | PASS | m1:M1_MULTI_CANDIDATE_ACCEPT |
| T1 複数候補のうち1つ一致(主発音) | Melos said. | Melos said. | PASS | PASS | prod:should_pass |
| T1 複数候補のうち1つ一致(CMU異読) | The tomatoes were red. | The tomatoes were red. | PASS | PASS | prod:should_pass |
| T1b 一般化(fake Ledger・別語) | Cleos said. | Clio said. | PASS | PASS | m1:M1_MULTI_CANDIDATE_ACCEPT |
| T1c 一般化の限界(fake Ledger・語幹がCMU未収録) | Zabelinas said. | Zabellina said. | NONPASS | NONPASS | m1:MULTI_CANDIDATE_NO_MATCH |
| T2 どの候補も不一致 | Melos said. | Milo said. | NONPASS | NONPASS | m1:MULTI_CANDIDATE_NO_MATCH |
| T2 どの候補も不一致 | Melos said. | Mellon said. | NONPASS | NONPASS | m1:MULTI_CANDIDATE_NO_MATCH |
| T2 どの候補も不一致 | Melos said. | Melas said. | NONPASS | NONPASS | m1:MULTI_CANDIDATE_NO_MATCH |
| T3 綴り近いが発音異なる(候補なし) | Cleos said. | Clio said. | NONPASS | NONPASS | m1:MULTI_CANDIDATE_NO_MATCH |
| T3 綴り近いが発音異なる(fake Ledger) | Cleos said. | Clio said. | NONPASS | NONPASS | m1:MULTI_CANDIDATE_NO_MATCH |
| T3 綴り近いが発音異なる(既存Pattern A・M1非関与) | Brontes said. | Bronte said. | PASS | PASS | prod:should_pass |
| T4 ASRが別の実在語へ誤転写 | Melos said. | Mellow said. | PASS(論点) | PASS | m1:M1_MULTI_CANDIDATE_ACCEPT |
| T4 ASRが別の実在語へ誤転写 | Melos said. | Sad. | NONPASS | NONPASS | m1:BASE_CLASSIFICATION_NOT_UNCERTAIN |
| T5 連結発音 vs 語句欠落 | The studies suggest cats today. | The study suggests cats today. | PASS | PASS | prod:should_pass |
| T5 連結発音 vs 語句欠落 | He planned a US sea blockade. | He planned a U S blockade. | NONPASS | NONPASS | m1:BASE_CLASSIFICATION_NOT_UNCERTAIN |
| T5 連結発音 vs 語句欠落 | Melos said he left. | Mello said. | NONPASS | NONPASS | m1:BASE_CLASSIFICATION_NOT_UNCERTAIN |
| T6 後半に別差分 | Melos said cats sleep. | Mello said dogs sleep. | NONPASS | NONPASS | m1:BASE_CLASSIFICATION_NOT_UNCERTAIN |
| T6 後半に別差分 | Melos said he did not go. | Mello said he did go. | NONPASS | NONPASS | m1:BASE_CLASSIFICATION_NOT_UNCERTAIN |
| T6 後半に別差分 | Melos said 5 cats sleep. | Mello said 6 cats sleep. | NONPASS | NONPASS | m1:BASE_CLASSIFICATION_NOT_UNCERTAIN |
| T6 後半に別差分 | Melos said cats slept. | Mello said cats sleep. | NONPASS | NONPASS | m1:BASE_CLASSIFICATION_NOT_UNCERTAIN |
| T7 M1成立+後半同一 | Melos said cats sleep. | Mello said cats sleep. | PASS | PASS | m1:M1_MULTI_CANDIDATE_ACCEPT |
| T8 同一語が文中に2回 | Melos said Melos left. | Mello said Mellow left. | PASS | NONPASS | m1:SUBSTITUTION_NOT_F1_EXPLAINED |
| T8 2回のうち片方が別語 | Melos said Melos left. | Mello said Milo left. | NONPASS | NONPASS | m1:POST_REPLACEMENT_F1_RESIDUAL |

## 3. F1反例19件: 期待どおり 19/19

## 4. 674ペア: {"legacy=False|module=False": 626, "legacy=True|module=True": 30, "legacy=False|module=True": 18}
- 新規PASS(M1起因)=18件 / 既存PASS→非PASSの回帰=0件

| src | canonical | ASR | 置換(from,to,canonical,source,conf,rule) |
|---|---|---|---|
| human_review_queue | At the river, he stopped. The bridge was gone. Brown water rushed through the em | At the river, he stopped. The bridge was gone. Brown water rushed through the em | [('mellow', 'melo', 'melos', 'C2_ledger_alt', 'low', 'drop_final_S_or_Z')] |
| human_review_queue | Beyond the river, attackers blocked the road. One grabbed his arm. Another swung | Beyond the river, attackers blocked the road. One grabbed his arm. Another swung | [('mello', 'melo', 'melos', 'C2_ledger_alt', 'low', 'drop_final_S_or_Z')] |
| human_review_queue | Melos said. | Mello said. | [('mello', 'melo', 'melos', 'C2_ledger_alt', 'low', 'drop_final_S_or_Z')] |
| human_review_queue | Melos said. | Mellow said. | [('mellow', 'melo', 'melos', 'C2_ledger_alt', 'low', 'drop_final_S_or_Z')] |
| er021_telemetry | The guards went still when Melos spoke. | The guards went still when Mello spoke. | [('mello', 'melo', 'melos', 'C2_ledger_alt', 'low', 'drop_final_S_or_Z')] |
| er021_telemetry | At the wedding, Melos smiled whenever his sister smiled. He watched her join han | At the wedding, mellow smiled whenever his sister smiled. He watched her join ha | [('mellow', 'melo', 'melos', 'C2_ledger_alt', 'low', 'drop_final_S_or_Z')] |
| er021_telemetry | At the river, he stopped. The bridge was gone. Brown water rushed through the em | At the river, he stopped. The bridge was gone. Brown water rushed through the em | [('mellow', 'melo', 'melos', 'C2_ledger_alt', 'low', 'drop_final_S_or_Z')] |
| er021_telemetry | At the river, he stopped. The bridge was gone. Brown water rushed through the em | At the river, he stopped. The bridge was gone. Brown water rushed through the em | [('mello', 'melo', 'melos', 'C2_ledger_alt', 'low', 'drop_final_S_or_Z')] |
| er021_telemetry | At the river, he stopped. The bridge was gone. Brown water rushed through the em | At the river he stopped. The bridge was gone. Brown water rushed through the emp | [('mellow', 'melo', 'melos', 'C2_ledger_alt', 'low', 'drop_final_S_or_Z')] |
| er021_telemetry | Melos said. | Mello said | [('mello', 'melo', 'melos', 'C2_ledger_alt', 'low', 'drop_final_S_or_Z')] |
| er069_results_02 | Melos said. | Mellow said.  | [('mellow', 'melo', 'melos', 'C2_ledger_alt', 'low', 'drop_final_S_or_Z')] |
| er069_results_02 | Melos said. | Mello said, | [('mello', 'melo', 'melos', 'C2_ledger_alt', 'low', 'drop_final_S_or_Z')] |
| er069_results_02 | Melos says. | Mello says | [('mello', 'melo', 'melos', 'C2_ledger_alt', 'low', 'drop_final_S_or_Z')] |
| er069_results_02 | Melos says. | Mellow says. | [('mellow', 'melo', 'melos', 'C2_ledger_alt', 'low', 'drop_final_S_or_Z')] |
| er069_results_02 | Melos says. | Mellow says, | [('mellow', 'melo', 'melos', 'C2_ledger_alt', 'low', 'drop_final_S_or_Z')] |
| er069_results_02 | Melos says. | Mellow says.  | [('mellow', 'melo', 'melos', 'C2_ledger_alt', 'low', 'drop_final_S_or_Z')] |
| er069_results_02 | Melos sighed. | Mello sighed. | [('mello', 'melo', 'melos', 'C2_ledger_alt', 'low', 'drop_final_S_or_Z')] |
| er069_results_02 | Melos sighed. | Mellow sighed. | [('mellow', 'melo', 'melos', 'C2_ledger_alt', 'low', 'drop_final_S_or_Z')] |

ledger_key別集計: {"ec716e185835dba3": {"accept_count": 18, "canonical_words": ["melos"], "confidences": ["low"], "sources": ["C2_ledger_alt"], "updated_at": ["2026-10-12T13:17:58"], "candidate_set_hashes": ["23d911bd718b3d4e", "4465da631574fc7e", "8d0890e6325caabf", "9813adfaa551fdef", "ce8b5bdf9511b379", "d1a293e966ed1f5c", "dd523dae64e80f65"], "secondary_agree_true": 0}}

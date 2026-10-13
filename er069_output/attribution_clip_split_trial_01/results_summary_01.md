# results summary (Phase 2)

obs=216 gen_tts_jpy=9.0106 total_jpy=36.4913


## OOV names only (Melos/Brontes/Pelias)
| level/target | boundary | length | n | OpenAI PASS | Azure PASS | OR PASS | HR proxy | spell OA | spell Az | spell WH |
|---|---|---|---|---|---|---|---|---|---|---|
| adv/raw | nss | L2 | 9 | 5 | 9 | 9 | 0 | 4 | 9 | 6 |
| adv/raw | ss | L2 | 9 | 3 | 7 | 7 | 2 | 1 | 7 | 3 |
| adv/raw | nss | L4 | 9 | 6 | 9 | 9 | 0 | 6 | 9 | 5 |
| adv/raw | ss | L4 | 9 | 2 | 7 | 7 | 2 | 0 | 7 | 0 |
| adv/raw | nss | L7 | 9 | 4 | 9 | 9 | 0 | 4 | 9 | 6 |
| adv/raw | ss | L7 | 9 | 2 | 7 | 7 | 2 | 1 | 7 | 0 |
| std/raw | nss | L2 | 9 | 3 | 8 | 8 | 1 | 1 | 8 | 4 |
| std/raw | ss | L2 | 9 | 3 | 7 | 7 | 2 | 1 | 6 | 1 |
| std/raw | nss | L4 | 9 | 2 | 9 | 9 | 0 | 2 | 9 | 3 |
| std/raw | ss | L4 | 9 | 4 | 9 | 9 | 0 | 2 | 8 | 2 |
| std/raw | nss | L7 | 9 | 5 | 8 | 8 | 1 | 5 | 8 | 4 |
| std/raw | ss | L7 | 9 | 3 | 7 | 7 | 2 | 1 | 6 | 0 |
| std/slow6 | nss | L2 | 9 | 3 | 8 | 8 | 1 | 3 | 8 | 5 |
| std/slow6 | ss | L2 | 9 | 3 | 6 | 6 | 3 | 0 | 6 | 2 |
| std/slow6 | nss | L4 | 9 | 2 | 9 | 9 | 0 | 2 | 9 | 4 |
| std/slow6 | ss | L4 | 9 | 5 | 9 | 9 | 0 | 2 | 8 | 2 |
| std/slow6 | nss | L7 | 9 | 2 | 8 | 8 | 1 | 2 | 8 | 5 |
| std/slow6 | ss | L7 | 9 | 3 | 6 | 6 | 3 | 1 | 6 | 0 |

## Control name (Kallis, CMU-registered)
| level/target | boundary | length | n | OpenAI PASS | Azure PASS | OR PASS | HR proxy | spell OA | spell Az | spell WH |
|---|---|---|---|---|---|---|---|---|---|---|
| adv/raw | nss | L2 | 3 | 0 | 3 | 3 | 0 | 0 | 3 | 0 |
| adv/raw | ss | L2 | 3 | 0 | 3 | 3 | 0 | 0 | 3 | 0 |
| adv/raw | nss | L4 | 3 | 0 | 3 | 3 | 0 | 0 | 3 | 0 |
| adv/raw | ss | L4 | 3 | 0 | 2 | 2 | 1 | 0 | 2 | 0 |
| adv/raw | nss | L7 | 3 | 0 | 3 | 3 | 0 | 0 | 3 | 0 |
| adv/raw | ss | L7 | 3 | 0 | 3 | 3 | 0 | 0 | 3 | 0 |
| std/raw | nss | L2 | 3 | 0 | 2 | 2 | 1 | 0 | 2 | 0 |
| std/raw | ss | L2 | 3 | 0 | 2 | 2 | 1 | 0 | 2 | 0 |
| std/raw | nss | L4 | 3 | 0 | 3 | 3 | 0 | 0 | 3 | 0 |
| std/raw | ss | L4 | 3 | 0 | 3 | 3 | 0 | 0 | 3 | 0 |
| std/raw | nss | L7 | 3 | 0 | 3 | 3 | 0 | 0 | 3 | 0 |
| std/raw | ss | L7 | 3 | 1 | 3 | 3 | 0 | 1 | 3 | 0 |
| std/slow6 | nss | L2 | 3 | 0 | 2 | 2 | 1 | 0 | 2 | 0 |
| std/slow6 | ss | L2 | 3 | 0 | 2 | 2 | 1 | 0 | 2 | 0 |
| std/slow6 | nss | L4 | 3 | 0 | 3 | 3 | 0 | 0 | 3 | 0 |
| std/slow6 | ss | L4 | 3 | 0 | 3 | 3 | 0 | 0 | 3 | 0 |
| std/slow6 | nss | L7 | 3 | 0 | 3 | 3 | 0 | 0 | 3 | 0 |
| std/slow6 | ss | L7 | 3 | 0 | 3 | 3 | 0 | 0 | 3 | 0 |

## Effects (OOV names; metric = OR PASS / OpenAI PASS; Fisher two-sided p; pooled over level/target)


### metric=or_pass
- length effect within nss: L7 vs L2: 25/27 vs 25/27  Fisher p=1.0000
- length effect within ss : L7 vs L2: 20/27 vs 20/27  Fisher p=1.0000
- s+s effect within L2: nss vs ss: 25/27 vs 20/27  Fisher p=0.1415
- s+s effect within L7: nss vs ss: 25/27 vs 20/27  Fisher p=0.1415
- s+s effect within L4: nss vs ss: 27/27 vs 25/27  Fisher p=0.4906
- length effect within nss: L4 vs L2: 27/27 vs 25/27  Fisher p=0.4906
- 2x2 rates: ss/L2=0.74 ss/L7=0.74 nss/L2=0.93 nss/L7=0.93; 交互作用(差の差: 長さ効果[nss]-長さ効果[ss])=+0.00

### metric=openai_verified
- length effect within nss: L7 vs L2: 11/27 vs 11/27  Fisher p=1.0000
- length effect within ss : L7 vs L2: 8/27 vs 9/27  Fisher p=1.0000
- s+s effect within L2: nss vs ss: 11/27 vs 9/27  Fisher p=0.7786
- s+s effect within L7: nss vs ss: 11/27 vs 8/27  Fisher p=0.5694
- s+s effect within L4: nss vs ss: 10/27 vs 11/27  Fisher p=1.0000
- length effect within nss: L4 vs L2: 10/27 vs 11/27  Fisher p=1.0000
- 2x2 rates: ss/L2=0.33 ss/L7=0.30 nss/L2=0.41 nss/L7=0.41; 交互作用(差の差: 長さ効果[nss]-長さ効果[ss])=+0.04

### metric=spell_openai
- length effect within nss: L7 vs L2: 11/27 vs 8/27  Fisher p=0.5694
- length effect within ss : L7 vs L2: 3/27 vs 2/27  Fisher p=1.0000
- s+s effect within L2: nss vs ss: 8/27 vs 2/27  Fisher p=0.0764
- s+s effect within L7: nss vs ss: 11/27 vs 3/27  Fisher p=0.0276
- s+s effect within L4: nss vs ss: 10/27 vs 4/27  Fisher p=0.1188
- length effect within nss: L4 vs L2: 10/27 vs 8/27  Fisher p=0.7734
- 2x2 rates: ss/L2=0.07 ss/L7=0.11 nss/L2=0.30 nss/L7=0.41; 交互作用(差の差: 長さ効果[nss]-長さ効果[ss])=+0.07

## by name x boundary x length (OR PASS / n)
- Brontes: L2/ss=9/9 L2/nss=9/9 L4/ss=9/9 L4/nss=9/9 L7/ss=9/9 L7/nss=9/9
- Kallis: L2/ss=7/9 L2/nss=7/9 L4/ss=8/9 L4/nss=9/9 L7/ss=9/9 L7/nss=9/9
- Melos: L2/ss=2/9 L2/nss=7/9 L4/ss=7/9 L4/nss=9/9 L7/ss=2/9 L7/nss=9/9
- Pelias: L2/ss=9/9 L2/nss=9/9 L4/ss=9/9 L4/nss=9/9 L7/ss=9/9 L7/nss=7/9

## Std: raw(減速前) -> slow6(減速後)
- raw: OpenAI PASS 20/54, Azure PASS 48/54, OR 48/54
- slow6: OpenAI PASS 18/54, Azure PASS 46/54, OR 46/54
- adv(raw): OpenAI PASS 22/54, Azure PASS 48/54, OR 48/54

## transcript samples (OpenAI / Azure) L2 ss vs nss, OOV names, raw
- Brontes_ss_L2_adv_t1: OA='Bronte said' AZ='Brontes said.' WH='Brontes said.'
- Brontes_ss_L2_adv_t2: OA='Brontë said,' AZ='Brontes said.' WH='Bronte said.'
- Brontes_ss_L2_adv_t3: OA='Bronte's said,' AZ='Brontes said.' WH='Brontes said.'
- Brontes_ss_L2_std_t1: OA='Bronte's said.' AZ='Brontes said.' WH='Brontes said.'
- Brontes_ss_L2_std_t2: OA='Bronte said,' AZ='Brontes said.' WH='Brontese said,'
- Brontes_ss_L2_std_t3: OA='Bronte said.' AZ='Brontes said.' WH='Bronte said.'
- Melos_ss_L2_adv_t1: OA='Mello said.' AZ='Mellow said.' WH='Mello said.'
- Melos_ss_L2_adv_t2: OA='Mellos said.' AZ='Melos said.' WH='Melos said.'
- Melos_ss_L2_adv_t3: OA='Mallow said.' AZ='Mellow said.' WH='Mellow said.'
- Brontes_nss_L2_adv_t1: OA='Brontes replied.' AZ='Brontes replied.' WH='Bronte's replied.'
- Brontes_nss_L2_adv_t2: OA='Brontë's replied.' AZ='Brontes replied.' WH='Bronte's replied.'
- Brontes_nss_L2_adv_t3: OA='Bronte's replied.' AZ='Brontes replied.' WH='Bronte's replied.'
- Brontes_nss_L2_std_t1: OA='Brontë's replied.' AZ='Brontes replied.' WH='Brontes replied.'
- Brontes_nss_L2_std_t2: OA='Brontë's replied.' AZ='Brontes replied.' WH='Bronte's replied.'
- Brontes_nss_L2_std_t3: OA='Bronte's replied.' AZ='Brontes replied.' WH='Bronte's replied.'
- Melos_nss_L2_adv_t1: OA='Mallos replied.' AZ='Melos replied.' WH='Melos replied.'
- Melos_nss_L2_adv_t2: OA='Melos replied.' AZ='Melos replied.' WH='Melos replied.'
- Melos_nss_L2_adv_t3: OA='Melos replied.' AZ='Melos replied.' WH='Melos replied.'
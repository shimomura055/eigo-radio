## B-1. Melos target take x recipe x engine: 正認識率(target領域がcanonical 'Melos said.' と一致)

### engine=openai (base variant) — exact_tokens(領域=melos said) / focus(Melos)語一致 / Production判定PASS(領域, CS受理含む)

| recipe | n | exact_tokens | focus(Melos)一致 | Prod classify PASS | strict(EXACT/NORMALIZED) | 平均秒 |
|---|---|---|---|---|---|---|
| R00_alone | 13 | 0/13 (0%) | 0/13 (0%) | 0/13 (0%) | 0/13 (0%) | 1.4 |
| Npre3 | 13 | 0/13 (0%) | 0/13 (0%) | 2/13 (15%) | 0/13 (0%) | 4.3 |
| Npre8 | 13 | 0/13 (0%) | 0/13 (0%) | 3/13 (23%) | 0/13 (0%) | 8.9 |
| Npre14 | 13 | 0/13 (0%) | 0/13 (0%) | 6/13 (46%) | 0/13 (0%) | 14.8 |
| Npre27 | 13 | 2/13 (15%) | 2/13 (15%) | 5/13 (38%) | 2/13 (15%) | 27.5 |
| Npost3 | 13 | 0/13 (0%) | 0/13 (0%) | 1/13 (8%) | 0/13 (0%) | 4.3 |
| Npost8 | 13 | 5/13 (38%) | 6/13 (46%) | 6/13 (46%) | 5/13 (38%) | 9.3 |
| Npost14 | 13 | 0/13 (0%) | 0/13 (0%) | 0/13 (0%) | 0/13 (0%) | 14.8 |
| Nboth | 13 | 0/13 (0%) | 0/13 (0%) | 2/13 (15%) | 0/13 (0%) | 11.8 |
| Dpre3 | 13 | 0/13 (0%) | 0/13 (0%) | 0/13 (0%) | 0/13 (0%) | 4.5 |
| Dpre5 | 13 | 1/13 (8%) | 1/13 (8%) | 2/13 (15%) | 1/13 (8%) | 5.9 |
| Dpre6 | 13 | 2/13 (15%) | 2/13 (15%) | 3/13 (23%) | 2/13 (15%) | 7.3 |
| Dpre8 | 13 | 0/13 (0%) | 0/13 (0%) | 1/13 (8%) | 0/13 (0%) | 9.2 |
| Dpre11 | 13 | 2/13 (15%) | 2/13 (15%) | 4/13 (31%) | 2/13 (15%) | 11.8 |
| Dpre14 | 13 | 1/13 (8%) | 1/13 (8%) | 5/13 (38%) | 1/13 (8%) | 15.2 |
| Dpre25 | 13 | 4/13 (31%) | 4/13 (31%) | 9/13 (69%) | 4/13 (31%) | 26.0 |
| Dpost3 | 13 | 0/13 (0%) | 0/13 (0%) | 0/13 (0%) | 0/13 (0%) | 4.5 |
| Dpost8 | 13 | 0/13 (0%) | 0/13 (0%) | 0/13 (0%) | 0/13 (0%) | 9.2 |
| Dboth | 13 | 2/13 (15%) | 2/13 (15%) | 3/13 (23%) | 2/13 (15%) | 9.1 |
| Rpre | 13 | 2/13 (15%) | 2/13 (15%) | 4/13 (31%) | 2/13 (15%) | 5.9 |
| Rpost | 13 | 0/13 (0%) | 0/13 (0%) | 0/13 (0%) | 0/13 (0%) | 4.7 |
| Rboth | 13 | 2/13 (15%) | 2/13 (15%) | 6/13 (46%) | 2/13 (15%) | 9.3 |
| Rwin5 | 13 | 2/13 (15%) | 2/13 (15%) | 5/13 (38%) | 2/13 (15%) | 19.7 |
| Rwin7 | 12 | 8/12 (67%) | 8/12 (67%) | 8/12 (67%) | 8/12 (67%) | 28.6 |

### engine=azure (base variant) — exact_tokens(領域=melos said) / focus(Melos)語一致 / Production判定PASS(領域, CS受理含む)

| recipe | n | exact_tokens | focus(Melos)一致 | Prod classify PASS | strict(EXACT/NORMALIZED) | 平均秒 |
|---|---|---|---|---|---|---|
| R00_alone | 14 | 2/14 (14%) | 2/14 (14%) | 6/14 (43%) | 2/14 (14%) | 1.4 |
| Npre3 | 11 | 2/11 (18%) | 2/11 (18%) | 6/11 (55%) | 2/11 (18%) | 4.3 |
| Npre8 | 4 | 1/4 (25%) | 1/4 (25%) | 2/4 (50%) | 1/4 (25%) | 9.0 |
| Dpre3 | 7 | 1/7 (14%) | 1/7 (14%) | 2/7 (29%) | 1/7 (14%) | 4.5 |
| Dpre8 | 4 | 1/4 (25%) | 1/4 (25%) | 3/4 (75%) | 1/4 (25%) | 8.8 |
| Rpre | 4 | 1/4 (25%) | 1/4 (25%) | 3/4 (75%) | 1/4 (25%) | 5.6 |
| Rpost | 4 | 1/4 (25%) | 1/4 (25%) | 2/4 (50%) | 1/4 (25%) | 5.0 |
| Rboth | 11 | 2/11 (18%) | 2/11 (18%) | 7/11 (64%) | 2/11 (18%) | 9.3 |
| Rwin5 | 4 | 1/4 (25%) | 1/4 (25%) | 2/4 (50%) | 1/4 (25%) | 19.7 |

### engine=whisper-small (base variant) — exact_tokens(領域=melos said) / focus(Melos)語一致 / Production判定PASS(領域, CS受理含む)

| recipe | n | exact_tokens | focus(Melos)一致 | Prod classify PASS | strict(EXACT/NORMALIZED) | 平均秒 |
|---|---|---|---|---|---|---|
| R00_alone | 7 | 0/7 (0%) | 0/7 (0%) | 4/7 (57%) | 0/7 (0%) | 1.4 |
| Npre3 | 7 | 0/7 (0%) | 0/7 (0%) | 3/7 (43%) | 0/7 (0%) | 4.3 |
| Npre8 | 7 | 0/7 (0%) | 0/7 (0%) | 1/7 (14%) | 0/7 (0%) | 8.9 |
| Npre14 | 7 | 4/7 (57%) | 7/7 (100%) | 4/7 (57%) | 4/7 (57%) | 14.9 |
| Npre27 | 7 | 1/7 (14%) | 6/7 (86%) | 1/7 (14%) | 1/7 (14%) | 27.4 |
| Npost3 | 7 | 0/7 (0%) | 0/7 (0%) | 0/7 (0%) | 0/7 (0%) | 4.3 |
| Npost8 | 7 | 7/7 (100%) | 7/7 (100%) | 7/7 (100%) | 7/7 (100%) | 9.3 |
| Npost14 | 7 | 3/7 (43%) | 3/7 (43%) | 3/7 (43%) | 3/7 (43%) | 14.9 |
| Nboth | 7 | 0/7 (0%) | 0/7 (0%) | 1/7 (14%) | 0/7 (0%) | 11.8 |
| Dpre3 | 7 | 0/7 (0%) | 0/7 (0%) | 1/7 (14%) | 0/7 (0%) | 4.5 |
| Dpre5 | 7 | 0/7 (0%) | 0/7 (0%) | 4/7 (57%) | 0/7 (0%) | 5.8 |
| Dpre6 | 7 | 0/7 (0%) | 0/7 (0%) | 6/7 (86%) | 0/7 (0%) | 7.3 |
| Dpre8 | 7 | 0/7 (0%) | 0/7 (0%) | 5/7 (71%) | 0/7 (0%) | 9.0 |
| Dpre11 | 7 | 0/7 (0%) | 0/7 (0%) | 1/7 (14%) | 0/7 (0%) | 11.7 |
| Dpre14 | 7 | 0/7 (0%) | 0/7 (0%) | 0/7 (0%) | 0/7 (0%) | 15.1 |
| Dpre25 | 7 | 0/7 (0%) | 0/7 (0%) | 2/7 (29%) | 0/7 (0%) | 25.8 |
| Dpost3 | 7 | 0/7 (0%) | 0/7 (0%) | 0/7 (0%) | 0/7 (0%) | 4.5 |
| Dpost8 | 7 | 0/7 (0%) | 0/7 (0%) | 0/7 (0%) | 0/7 (0%) | 9.0 |
| Dboth | 7 | 0/7 (0%) | 0/7 (0%) | 0/7 (0%) | 0/7 (0%) | 8.9 |
| Rpre | 7 | 0/7 (0%) | 0/7 (0%) | 4/7 (57%) | 0/7 (0%) | 5.8 |
| Rpost | 7 | 0/7 (0%) | 0/7 (0%) | 1/7 (14%) | 0/7 (0%) | 4.9 |
| Rboth | 7 | 0/7 (0%) | 0/7 (0%) | 1/7 (14%) | 0/7 (0%) | 9.3 |
| Rwin5 | 7 | 0/7 (0%) | 0/7 (0%) | 2/7 (29%) | 0/7 (0%) | 19.7 |
| Rwin7 | 7 | 3/7 (43%) | 3/7 (43%) | 3/7 (43%) | 3/7 (43%) | 28.5 |

## B-2/C. 文脈量・同一/異ナレーター別(Melos main, base)

| engine | 条件群 | 文脈秒(前後合計) | n | exact_tokens | focus一致 | Prod PASS |
|---|---|---|---|---|---|---|
| openai | alone | 0-0.01 | 13 | 0/13 (0%) | 0/13 (0%) | 0/13 (0%) |
| openai | same_voice | 2-4 | 26 | 0/26 (0%) | 0/26 (0%) | 3/26 (12%) |
| openai | same_voice | 7-11 | 39 | 5/39 (13%) | 6/39 (15%) | 11/39 (28%) |
| openai | same_voice | 11-16 | 26 | 0/26 (0%) | 0/26 (0%) | 6/26 (23%) |
| openai | same_voice | 22-30 | 13 | 2/13 (15%) | 2/13 (15%) | 5/13 (38%) |
| openai | diff_voice | 2-4 | 27 | 0/27 (0%) | 0/27 (0%) | 0/27 (0%) |
| openai | diff_voice | 4-7 | 28 | 3/28 (11%) | 3/28 (11%) | 6/28 (21%) |
| openai | diff_voice | 7-11 | 49 | 4/49 (8%) | 4/49 (8%) | 7/49 (14%) |
| openai | diff_voice | 11-16 | 13 | 1/13 (8%) | 1/13 (8%) | 5/13 (38%) |
| openai | diff_voice | 16-22 | 1 | 0/1 (0%) | 0/1 (0%) | 0/1 (0%) |
| openai | diff_voice | 22-30 | 12 | 4/12 (33%) | 4/12 (33%) | 9/12 (75%) |
| openai | mixed_real | 2-4 | 13 | 0/13 (0%) | 0/13 (0%) | 0/13 (0%) |
| openai | mixed_real | 4-7 | 13 | 2/13 (15%) | 2/13 (15%) | 4/13 (31%) |
| openai | mixed_real | 7-11 | 13 | 2/13 (15%) | 2/13 (15%) | 6/13 (46%) |
| openai | mixed_real | 16-22 | 13 | 2/13 (15%) | 2/13 (15%) | 5/13 (38%) |
| openai | mixed_real | 22-30 | 12 | 8/12 (67%) | 8/12 (67%) | 8/12 (67%) |
| azure | alone | 0-0.01 | 14 | 2/14 (14%) | 2/14 (14%) | 6/14 (43%) |
| azure | same_voice | 2-4 | 11 | 2/11 (18%) | 2/11 (18%) | 6/11 (55%) |
| azure | same_voice | 7-11 | 4 | 1/4 (25%) | 1/4 (25%) | 2/4 (50%) |
| azure | diff_voice | 2-4 | 7 | 1/7 (14%) | 1/7 (14%) | 2/7 (29%) |
| azure | diff_voice | 4-7 | 1 | 0/1 (0%) | 0/1 (0%) | 1/1 (100%) |
| azure | diff_voice | 7-11 | 3 | 1/3 (33%) | 1/3 (33%) | 2/3 (67%) |
| azure | mixed_real | 2-4 | 4 | 1/4 (25%) | 1/4 (25%) | 3/4 (75%) |
| azure | mixed_real | 4-7 | 4 | 1/4 (25%) | 1/4 (25%) | 2/4 (50%) |
| azure | mixed_real | 7-11 | 11 | 2/11 (18%) | 2/11 (18%) | 7/11 (64%) |
| azure | mixed_real | 16-22 | 4 | 1/4 (25%) | 1/4 (25%) | 2/4 (50%) |
| whisper-small | alone | 0-0.01 | 7 | 0/7 (0%) | 0/7 (0%) | 4/7 (57%) |
| whisper-small | same_voice | 2-4 | 14 | 0/14 (0%) | 0/14 (0%) | 3/14 (21%) |
| whisper-small | same_voice | 7-11 | 21 | 7/21 (33%) | 7/21 (33%) | 9/21 (43%) |
| whisper-small | same_voice | 11-16 | 14 | 7/14 (50%) | 10/14 (71%) | 7/14 (50%) |
| whisper-small | same_voice | 22-30 | 7 | 1/7 (14%) | 6/7 (86%) | 1/7 (14%) |
| whisper-small | diff_voice | 2-4 | 15 | 0/15 (0%) | 0/15 (0%) | 1/15 (7%) |
| whisper-small | diff_voice | 4-7 | 16 | 0/16 (0%) | 0/16 (0%) | 10/16 (62%) |
| whisper-small | diff_voice | 7-11 | 25 | 0/25 (0%) | 0/25 (0%) | 6/25 (24%) |
| whisper-small | diff_voice | 11-16 | 7 | 0/7 (0%) | 0/7 (0%) | 0/7 (0%) |
| whisper-small | diff_voice | 16-22 | 1 | 0/1 (0%) | 0/1 (0%) | 1/1 (100%) |
| whisper-small | diff_voice | 22-30 | 6 | 0/6 (0%) | 0/6 (0%) | 1/6 (17%) |
| whisper-small | mixed_real | 2-4 | 7 | 0/7 (0%) | 0/7 (0%) | 1/7 (14%) |
| whisper-small | mixed_real | 4-7 | 7 | 0/7 (0%) | 0/7 (0%) | 4/7 (57%) |
| whisper-small | mixed_real | 7-11 | 7 | 0/7 (0%) | 0/7 (0%) | 1/7 (14%) |
| whisper-small | mixed_real | 16-22 | 7 | 0/7 (0%) | 0/7 (0%) | 2/7 (29%) |
| whisper-small | mixed_real | 22-30 | 7 | 3/7 (43%) | 3/7 (43%) | 3/7 (43%) |

## B-3. take別: 単独clip(R00_alone)のASR結果分布(全エンジン・全rep、target領域転写)

| target | Prod判定(本番ログ) | engine | 転写の内訳(回数) |
|---|---|---|---|
| a2_att1 | Std OK take(Prod: Tier3 Azure=Melos said | openai | `mello said` x2 |
| a2_att1 | Std OK take(Prod: Tier3 Azure=Melos said | azure | `melos said` x2; `(nophrase)mellow said` x1 |
| a2_att1 | Std OK take(Prod: Tier3 Azure=Melos said | whisper-small | `mello said` x1 |
| a2_att1 | Std OK take(Prod: Tier3 Azure=Melos said | whisper-medium | `mellow said` x1 |
| a2_att2 | Std NG take(Prod: UNCERTAIN, Azure=Mello | openai | `mello said` x2 |
| a2_att2 | Std NG take(Prod: UNCERTAIN, Azure=Mello | azure | `mellow said` x2; `(nophrase)mellow said` x1 |
| a2_att2 | Std NG take(Prod: UNCERTAIN, Azure=Mello | whisper-small | `mello said` x1 |
| a2_att2 | Std NG take(Prod: UNCERTAIN, Azure=Mello | whisper-medium | `mellow said` x1 |
| a2_att3 | Std fallback take(Prod: Pattern A ACCEPT | openai | `mello said` x2 |
| a2_att3 | Std fallback take(Prod: Pattern A ACCEPT | azure | `melo said` x2; `(nophrase)melo said` x1 |
| a2_att3 | Std fallback take(Prod: Pattern A ACCEPT | whisper-small | `melo said` x1 |
| a2_att3 | Std fallback take(Prod: Pattern A ACCEPT | whisper-medium | `mellow said` x1 |
| a2_att4 | Std NG take(Prod ASR: 'Mellis said') | openai | `mellis said` x2 |
| a2_att4 | Std NG take(Prod ASR: 'Mellis said') | azure | `mallow said` x2; `(nophrase)mallow said` x1 |
| a2_att4 | Std NG take(Prod ASR: 'Mellis said') | whisper-small | `melo said` x1 |
| a2_att4 | Std NG take(Prod ASR: 'Mellis said') | whisper-medium | `mellow said` x1 |
| a2_att5 | Std NG take(Prod ASR: 'melloset' TTS_FAI | openai | `mellowset` x1; `melloset` x1 |
| a2_att5 | Std NG take(Prod ASR: 'melloset' TTS_FAI | azure | `melo said` x2; `(nophrase)melo said` x1 |
| a2_att5 | Std NG take(Prod ASR: 'melloset' TTS_FAI | whisper-small | `melo said` x1 |
| a2_att5 | Std NG take(Prod ASR: 'melloset' TTS_FAI | whisper-medium | `mellow said` x1 |
| a2_att6 | Std NG take(Prod ASR: 'Mellowset' TTS_FA | openai | `meloset` x2 |
| a2_att6 | Std NG take(Prod ASR: 'Mellowset' TTS_FA | azure | `mellow said` x2; `(nophrase)mellow said` x1 |
| a2_att6 | Std NG take(Prod ASR: 'Mellowset' TTS_FA | whisper-small | `melo said` x1 |
| a2_att6 | Std NG take(Prod ASR: 'Mellowset' TTS_FA | whisper-medium | `mellow set` x1 |
| b1b_att1 | Adv take(Prod: UNCERTAIN 'Mello said.';  | openai | `mello said` x1 |
| b1b_att1 | Adv take(Prod: UNCERTAIN 'Mello said.';  | azure | `mellow said` x2; `(nophrase)mellow said` x1 |
| b1b_att1 | Adv take(Prod: UNCERTAIN 'Mello said.';  | whisper-small | `mellow said` x1 |
| b1b_att1 | Adv take(Prod: UNCERTAIN 'Mello said.';  | whisper-medium | `mello said` x1 |

## B-4. 非決定性(同一音声・同一条件で2回呼出した結果の一致)

| engine | variant | 比較ペア数 | target領域転写が2回で一致 | 全文転写が一致 | 領域の判定(exact)が不一致 |
|---|---|---|---|---|---|
| openai | base | 205 | 148/205 (72%) | 114/205 (56%) | 17 |
| openai | prompt_word | 11 | 9/11 (82%) | 8/11 (73%) | 1 |
| openai | prompt_prev | 11 | 5/11 (45%) | 5/11 (45%) | 1 |
| azure | base | 15 | 15/15 (100%) | 15/15 (100%) | 0 |

## B-5. 誤認識の種類(target領域のfocus語トークンの内訳、Melos main、全文脈条件、base)

| engine | recipe群 | exact | spelling_variant | final_char_loss | extra_final_char | other/missing |
|---|---|---|---|---|---|---|
| openai | alone (n=13) | 0 | 11 | 0 | 2 | 0 |
| openai | 文脈あり(全て) (n=298) | 34 | 185 | 42 | 4 | 33 |
| azure | alone (n=14) | 2 | 6 | 4 | 0 | 2 |
| azure | 文脈あり(全て) (n=49) | 10 | 19 | 17 | 0 | 3 |
| whisper-small | alone (n=7) | 0 | 3 | 4 | 0 | 0 |
| whisper-small | 文脈あり(全て) (n=161) | 26 | 101 | 32 | 0 | 2 |

## E-3. ASRへ文脈情報を与える(OpenAI prompt) vs 与えない

| variant | recipe | n | exact_tokens | focus一致 | Prod PASS |
|---|---|---|---|---|---|
| base | R00_alone | 13 | 0/13 (0%) | 0/13 (0%) | 0/13 (0%) |
| base | Npre3 | 7 | 0/7 (0%) | 0/7 (0%) | 0/7 (0%) |
| prompt_word | R00_alone | 14 | 5/14 (36%) | 5/14 (36%) | 7/14 (50%) |
| prompt_word | Npre3 | 8 | 6/8 (75%) | 6/8 (75%) | 6/8 (75%) |
| prompt_prev | R00_alone | 14 | 3/14 (21%) | 3/14 (21%) | 5/14 (36%) |
| prompt_prev | Npre3 | 8 | 0/8 (0%) | 0/8 (0%) | 2/8 (25%) |
| azure base (PhraseList=Melos) | R00_alone | 14 | 2/14 (14%) | 2/14 (14%) | 6/14 (43%) |
| azure nophrase (PhraseList=なし) | R00_alone | 7 | 0/7 (0%) | 0/7 (0%) | 2/7 (29%) |

## D. 反例セット: 単独 vs 文脈結合(誤PASSリスク)

| group | engine | target群 | 条件 | n | 領域=canonical(exact_tokens) | Prod classify PASS(領域) | 全文Prod PASS |
|---|---|---|---|---|---|---|---|
| synthetic | openai | 全 | 単独 | 33 | 20/33 (61%) | 20/33 (61%) | 20/33 (61%) |
| synthetic | openai | 全 | 同一voice文脈 | 48 | 24/48 (50%) | 27/48 (56%) | 18/48 (38%) |
| synthetic | openai | 全 | 異voice文脈 | 44 | 25/44 (57%) | 26/44 (59%) | 26/44 (59%) |
| synthetic | azure | 全 | 単独 | 5 | 0/5 (0%) | 0/5 (0%) | 0/5 (0%) |
| natural_ng | openai | 全 | 単独 | 22 | 5/22 (23%) | 5/22 (23%) | 5/22 (23%) |
| natural_ng | openai | 全 | 同一voice文脈 | 38 | 15/38 (39%) | 15/38 (39%) | 15/38 (39%) |
| natural_ng | openai | 全 | 異voice文脈 | 8 | 2/8 (25%) | 2/8 (25%) | 2/8 (25%) |
| natural_ng | azure | 全 | 単独 | 11 | 6/11 (55%) | 7/11 (64%) | 7/11 (64%) |

### D-2. 反例target別(OpenAI、全rep・全文脈): 領域がcanonical一致した回数

| group | target | category/defect | 単独 PASS | 同voice文脈 PASS | 異voice文脈 PASS | 単独の転写例 |
|---|---|---|---|---|---|---|
| natural_ng | nat_bements | context_guessable_homophone / NG ASR 'Bements to protect.' | 1/2 (50%) | 3/3 (100%) | - | `be meant to protect`x1; `bement to protect`x1 |
| natural_ng | nat_counts | final_consonant_added / NG ASR 'Counts as success.' (+s) | 0/2 (0%) | 0/4 (0%) | - | `counts as success`x2 |
| natural_ng | nat_design | context_guessable_homophone / NG ASR '...fabric and design join forces' | 1/2 (50%) | 3/3 (100%) | 1/1 (100%) | `when fabric and design join forces`x1; `when fabric and drying join forces`x1 |
| natural_ng | nat_feet | context_guessable_homophone / NG ASR '...her feet is closing in' (context 'feed' | 1/2 (50%) | 3/3 (100%) | 1/1 (100%) | `another voice the reader who worries her feed is closing in`x1; `another voice the reader who worries her feet is closing in`x1 |
| natural_ng | nat_forced | final_consonant_added / NG ASR "Forced one's way through." (+d) | 2/2 (100%) | 4/4 (100%) | 0/1 (0%) | `force one's way through`x2 |
| natural_ng | nat_melus_hand | proper_noun_mispronounced / NG ASR "His friends took Melus's hand" | 0/2 (0%) | 0/4 (0%) | 0/1 (0%) | `his friends took melis's hand his fingers were warm and steady`x2 |
| natural_ng | nat_milo | proper_noun_mispronounced / NG ASR 'Milo spoke' | 0/2 (0%) | 0/4 (0%) | 0/1 (0%) | `the guards went still when milo spoke`x2 |
| natural_ng | nat_milos_hand | proper_noun_mispronounced / NG ASR "Milos's hand" (+friends') | 0/2 (0%) | 0/4 (0%) | 0/1 (0%) | `his friend's warm steady fingers closed around milos' hand`x2 |
| natural_ng | nat_paused | final_consonant_added / NG ASR 'Paused the feature.' (+d) | 0/2 (0%) | 2/4 (50%) | - | `paused the feature`x2 |
| natural_ng | nat_reduce | final_consonant_drop / NG ASR 'reduce the feeling of connection.' (-d dro | 0/2 (0%) | 0/4 (0%) | 0/1 (0%) | `reduce the feeling of connection`x2 |
| natural_ng | nat_turnout | content_mispronounced / NG ASR 'Turn out not today.' | 0/2 (0%) | 0/1 (0%) | 0/1 (0%) | `turn out not today`x2 |
| synthetic | ctl_B1_intact | intact_control / none (unmodified base) | 0/1 (0%) | 0/2 (0%) | 0/2 (0%) | `mallow said`x1 |
| synthetic | ctl_B2_intact | intact_control / none (unmodified base) | 1/1 (100%) | 2/2 (100%) | 2/2 (100%) | `the ruler smiled and said`x1 |
| synthetic | ctl_B4_intact | intact_control / none (unmodified base) | 1/1 (100%) | 2/2 (100%) | 2/2 (100%) | `silence came and guards grabbed the young shepherd the ruler ordered his death`x1 |
| synthetic | sweep_B2_trunc300 | synthetic_final_consonant_loss / last 300 ms of speech removed (speech_end=2.57s),  | 2/2 (100%) | 1/1 (100%) | 1/1 (100%) | `the ruler smiled and said`x2 |
| synthetic | sweep_B2_trunc380 | synthetic_final_consonant_loss / last 380 ms of speech removed (speech_end=2.57s),  | 2/2 (100%) | 1/1 (100%) | 1/1 (100%) | `the ruler smiled and said`x2 |
| synthetic | sweep_B2_trunc460 | synthetic_final_consonant_loss / last 460 ms of speech removed (speech_end=2.57s),  | 2/2 (100%) | 1/1 (100%) | 1/1 (100%) | `the ruler smiled and said`x2 |
| synthetic | syn_B1_dropmelos | synthetic_missing_word / word 'Melos' removed (azure word ts: melos 0.35-0. | 0/2 (0%) | 0/3 (0%) | 0/3 (0%) | `said`x2 |
| synthetic | syn_B1_dropsaid | synthetic_missing_word / word 'said' removed (azure word ts: melos 0.35-0.7 | 0/2 (0%) | 0/3 (0%) | 0/3 (0%) | `mellos`x2 |
| synthetic | syn_B1_trunc140 | synthetic_final_consonant_loss / last 140 ms of speech removed (speech_end=1.37s),  | 0/2 (0%) | 0/3 (0%) | 1/3 (33%) | `mello said`x2 |
| synthetic | syn_B1_trunc220 | synthetic_final_consonant_loss / last 220 ms of speech removed (speech_end=1.37s),  | 0/2 (0%) | 1/3 (33%) | 0/3 (0%) | `mello said`x2 |
| synthetic | syn_B1_trunc70 | synthetic_final_consonant_loss / last 70 ms of speech removed (speech_end=1.37s), f | 0/2 (0%) | 1/3 (33%) | 0/3 (0%) | `mello said`x2 |
| synthetic | syn_B2_trunc140 | synthetic_final_consonant_loss / last 140 ms of speech removed (speech_end=2.57s),  | 2/2 (100%) | 3/3 (100%) | 3/3 (100%) | `the ruler smiled and said`x2 |
| synthetic | syn_B2_trunc220 | synthetic_final_consonant_loss / last 220 ms of speech removed (speech_end=2.57s),  | 2/2 (100%) | 3/3 (100%) | 3/3 (100%) | `the ruler smiled and said`x2 |
| synthetic | syn_B2_trunc70 | synthetic_final_consonant_loss / last 70 ms of speech removed (speech_end=2.57s), f | 2/2 (100%) | 3/3 (100%) | 3/3 (100%) | `the ruler smiled and said`x2 |
| synthetic | syn_B4_trunc140 | synthetic_final_consonant_loss / last 140 ms of speech removed (speech_end=7.03s),  | 2/2 (100%) | 3/3 (100%) | 3/3 (100%) | `silence came and guards grabbed the young shepherd the ruler ordered his death`x2 |
| synthetic | syn_B4_trunc220 | synthetic_final_consonant_loss / last 220 ms of speech removed (speech_end=7.03s),  | 2/2 (100%) | 3/3 (100%) | 3/3 (100%) | `silence came and guards grabbed the young shepherd the ruler ordered his death`x2 |
| synthetic | syn_B4_trunc70 | synthetic_final_consonant_loss / last 70 ms of speech removed (speech_end=7.03s), f | 2/2 (100%) | 3/3 (100%) | 3/3 (100%) | `silence came and guards grabbed the young shepherd the ruler ordered his death`x2 |
| synthetic | syn_name_ruler | synthetic_wrong_name / first word replaced by 'ruler' (spliced from anoth | 0/2 (0%) | 0/6 (0%) | 0/2 (0%) | `rulers said`x2 |

### D-3. false accept(既知欠陥を含むsynthetic音声が、文脈付きASRでcanonical一致扱い)と防止条件の評価

| engine | 条件 | n | false accept (領域Prod PASS) | strict一致(EXACT/NORMALIZED) |
|---|---|---|---|---|
| openai | 単独 | 33 | 20/33 (61%) | 20/33 (61%) |
| openai | 文脈あり | 92 | 53/92 (58%) | 49/92 (53%) |
| azure | 単独 | 5 | 0/5 (0%) | 0/5 (0%) |
| whisper-small | 単独 | 18 | 14/18 (78%) | 11/18 (61%) |
| whisper-small | 文脈あり | 80 | 60/80 (75%) | 53/80 (66%) |

### D-4. 単独ではNGなのに文脈付きでPASSに反転した観測(flip = false accept候補)

| label | engine | 単独NGのtarget数 | 文脈付き観測数(単独NG target) | うちPASS反転 | 反転したtarget:recipe |
|---|---|---|---|---|---|
| known_defect_word | openai | 3 | 20 | 0 |  |
| known_defect_word | azure | 2 | 0 | 0 |  |
| known_defect_word | whisper-small | 3 | 14 | 0 |  |
| natural_ng_proxy | openai | 10 | 41 | 13 | nat_bements:SSpost, nat_bements:SSpre, nat_design:SDpre, nat_design:SSpost, nat_design:SSpre, nat_feet:SDpre, nat_feet:SSpost, nat_feet:SSpr |
| natural_ng_proxy | azure | 4 | 0 | 0 |  |
| natural_ng_proxy | whisper-small | 5 | 18 | 0 |  |

### D-4b. (委任_02追加) natural_ng_proxy(OpenAI)のPASS反転観測をtarget別に集計(D-4の単位=全rep観測。D-5のG0=target x recipe単位[rep1のみ]で母集団が異なる)

| target | 単独 | 文脈付き観測数 | 反転(PASS)観測数 |
|---|---|---|---|
| nat_bements | NG | 3 | 3 |
| nat_counts | NG | 4 | 0 |
| nat_design | NG | 4 | 4 |
| nat_feet | NG | 4 | 4 |
| nat_forced | PASS | 5 | 4 |
| nat_melus_hand | NG | 5 | 0 |
| nat_milo | NG | 5 | 0 |
| nat_milos_hand | NG | 5 | 0 |
| nat_paused | NG | 4 | 2 |
| nat_reduce | NG | 5 | 0 |
| nat_turnout | NG | 2 | 0 |

単独NG target合計: 文脈付き観測 41件、反転 13件(D-4と同一母集団)。

### D-5. false accept防止条件の評価(OpenAI文脈付きASRを一次、条件を重ねたときの受理数)

| 条件 | known_defect_word(語欠落/誤語) 受理=false accept | known_defect_trunc(語末切詰) 受理=false accept | good_control 受理=true accept | natural_ng_proxy 受理 |
|---|---|---|---|---|
| G0 文脈付きOpenAI領域が受理(無対策。受理=切詰/対照synthetic[category]は最終語の綴り一致[focus_exact]、それ以外はProduction classify_asr_match PASS) | 0/12 (0%) | 42/42 (100%) | 12/12 (100%) | 13/36 (36%) |
| G1 +単独clipもPASS(単独整合) | 0/12 (0%) | 42/42 (100%) | 12/12 (100%) | 3/36 (8%) |
| G2 +2回呼出し両方PASS | 0/8 (0%) | 18/18 (100%) | - | 4/10 (40%) |
| G3a +領域token min logprob >= -0.5 | 0/12 (0%) | 35/42 (83%) | 11/12 (92%) | 11/36 (31%) |
| G3b +領域token min logprob >= -1.5 | 0/12 (0%) | 42/42 (100%) | 12/12 (100%) | 11/36 (31%) |
| G4 +独立engine(whisper-small, 領域timestamp)もPASS | 0/12 (0%) | 42/42 (100%) | 12/12 (100%) | 12/36 (33%) |
| G5 +単独整合 かつ whisperもPASS | 0/12 (0%) | 42/42 (100%) | 12/12 (100%) | 2/36 (6%) |

### D-6. 語末子音を切り詰めた既知欠陥音声(synthetic)の単独ASR(OpenAI/whisper-small/Azure)

| target | defect | OpenAI単独 | Azure単独 | whisper単独 |
|---|---|---|---|---|
| ctl_B1_intact | none (unmodified base) | `mallow said`(P) | - | `mello said`(P) |
| ctl_B2_intact | none (unmodified base) | `the ruler smiled and said`(P) | - | `the ruler smiled and said`(P) |
| ctl_B4_intact | none (unmodified base) | `silence came and guards grabbed the young shepherd the ruler ordered his death`(P) | - | `silence came and guards grabbed the young shepherd the ruler ordered his death`(P) |
| sweep_B2_trunc300 | last 300 ms of speech removed (speech_end=2.5 | `the ruler smiled and said`(P); `the ruler smiled and said`(P) | - | `the ruler smiled and said`(P) |
| sweep_B2_trunc380 | last 380 ms of speech removed (speech_end=2.5 | `the ruler smiled and said`(P); `the ruler smiled and said`(P) | - | `the ruler smiled and said`(P) |
| sweep_B2_trunc460 | last 460 ms of speech removed (speech_end=2.5 | `the ruler smiled and said`(P); `the ruler smiled and said`(P) | - | `the ruler smiled and said`(P) |
| syn_B1_dropmelos | word 'Melos' removed (azure word ts: melos 0. | `said`(NG); `said`(NG) | `said`(NG) | `said`(NG) |
| syn_B1_dropsaid | word 'said' removed (azure word ts: melos 0.3 | `mellos`(NG); `mellos`(NG) | `mellows`(NG) | `melo's`(NG) |
| syn_B1_trunc140 | last 140 ms of speech removed (speech_end=1.3 | `mello said`(P); `mello said`(P) | `mellow said`(P) | `melo said`(P) |
| syn_B1_trunc220 | last 220 ms of speech removed (speech_end=1.3 | `mello said`(P); `mello said`(P) | `mellow said`(P) | `melo said`(P) |
| syn_B1_trunc70 | last 70 ms of speech removed (speech_end=1.37 | `mello said`(P); `mello said`(P) | `mellow said`(P) | `melo said`(P) |
| syn_B2_trunc140 | last 140 ms of speech removed (speech_end=2.5 | `the ruler smiled and said`(P); `the ruler smiled and said`(P) | - | `the ruler smiled and said`(P) |
| syn_B2_trunc220 | last 220 ms of speech removed (speech_end=2.5 | `the ruler smiled and said`(P); `the ruler smiled and said`(P) | - | `the ruler smiled and said`(P) |
| syn_B2_trunc70 | last 70 ms of speech removed (speech_end=2.57 | `the ruler smiled and said`(P); `the ruler smiled and said`(P) | - | `the ruler smiled and said`(P) |
| syn_B4_trunc140 | last 140 ms of speech removed (speech_end=7.0 | `silence came and guards grabbed the young shepherd the ruler ordered his death`(P); `silence came and guards grabbed the young shepherd the ruler ordered his death`(P) | - | `silence came and guards grabbed the young shepherd the ruler ordered his death`(P) |
| syn_B4_trunc220 | last 220 ms of speech removed (speech_end=7.0 | `silence came and guards grabbed the young shepherd the ruler ordered his death`(P); `silence came and guards grabbed the young shepherd the ruler ordered his death`(P) | - | `silence came and guards grabbed the young shepherd the ruler ordered his death`(P) |
| syn_B4_trunc70 | last 70 ms of speech removed (speech_end=7.03 | `silence came and guards grabbed the young shepherd the ruler ordered his death`(P); `silence came and guards grabbed the young shepherd the ruler ordered his death`(P) | - | `silence came and guards grabbed the young shepherd the ruler ordered his death`(P) |
| syn_name_ruler | first word replaced by 'ruler' (spliced from  | `rulers said`(NG); `rulers said`(NG) | - | `rulers said`(NG) |

### 処理時間(ASR 1呼出あたり秒、中央値)

| engine | 音声長 | 中央値秒 | n |
|---|---|---|---|
| openai | 0-3s | 0.41 | 79 |
| openai | 3-8s | 0.48 | 219 |
| openai | 8-16s | 0.58 | 196 |
| openai | 16-40s | 0.96 | 54 |
| azure | 0-3s | 0.60 | 32 |
| azure | 3-8s | 1.00 | 32 |
| azure | 8-16s | 2.40 | 18 |
| azure | 16-40s | 7.61 | 4 |
| whisper-small | 0-3s | 2.84 | 27 |
| whisper-small | 3-8s | 3.04 | 122 |
| whisper-small | 8-16s | 3.52 | 133 |
| whisper-small | 16-40s | 5.02 | 31 |

### D-7. OpenAI target領域token logprob(min)の分布: 領域PASS観測のうち good_control vs known_defect vs Melos

| label | PASS観測n | min_logprob 中央値 | 5%点 | 最小 |
|---|---|---|---|---|
| good_control | 15 | -0.01 | -2.48 | -2.48 |
| known_defect_trunc | 84 | -0.01 | -1.00 | -1.38 |
| natural_ng_proxy | 22 | -0.07 | -2.53 | -2.82 |

### C-2. 文脈clipに作品固有語(Melos)が含まれるか否かの効果(Melos main, base, 文脈あり条件のみ)

| engine | 文脈にMelos語を含む | n | focus(Melos)一致 | exact_tokens | Prod PASS |
|---|---|---|---|---|---|
| openai | 含まない | 234 | 18/234 (8%) | 18/234 (8%) | 50/234 (21%) |
| openai | 含む | 64 | 16/64 (25%) | 15/64 (23%) | 25/64 (39%) |
| azure | 含まない | 49 | 10/49 (20%) | 10/49 (20%) | 27/49 (55%) |
| whisper-small | 含まない | 126 | 0/126 (0%) | 0/126 (0%) | 32/126 (25%) |
| whisper-small | 含む | 35 | 26/35 (74%) | 18/35 (51%) | 18/35 (51%) |

### B-6. 領域抽出の整合性: timestamp領域(Azure/whisper) と 文字列整列領域の一致率

| engine | 文脈あり観測数 | 領域が一致 |
|---|---|---|
| azure | 49 | 49/49 (100%) |
| whisper-small | 277 | 255/277 (92%) |
| whisper-medium | 28 | 28/28 (100%) |

### D-8. 語末子音を切り詰めた既知欠陥(B2『The ruler smiled and said,』)のASR結果: 切り詰め量別

| 切り詰め(ms) | engine | 条件 | 領域転写 | Prod判定 |
|---|---|---|---|---|
| 0 | openai | R00_alone | `the ruler smiled and said` | P |
| 0 | openai | SSpre | `the ruler smiled and said` | P |
| 0 | openai | SDpre | `the ruler smiled and said` | P |
| 0 | whisper-small | R00_alone | `the ruler smiled and said` | P |
| 0 | whisper-small | SSpre | `the ruler smiled and said` | P |
| 0 | whisper-small | SDpre | `ruler smiled and said` | P |
| 70 | openai | R00_alone | `the ruler smiled and said`; `the ruler smiled and said` | P; P |
| 70 | openai | SSpre | `the ruler smiled and said`; `the rulers smiled and said` | P; P |
| 70 | openai | SDpre | `the ruler smiled and said`; `the ruler smiled and said` | P; P |
| 70 | whisper-small | R00_alone | `the ruler smiled and said` | P |
| 70 | whisper-small | SSpre | `the ruler smiled and said` | P |
| 70 | whisper-small | SDpre | `ruler smiled and said` | P |
| 140 | openai | R00_alone | `the ruler smiled and said`; `the ruler smiled and said` | P; P |
| 140 | openai | SSpre | `the rulers smiled and said`; `the ruler smiled and said` | P; P |
| 140 | openai | SDpre | `the ruler smiled and said`; `the ruler smiled and said` | P; P |
| 140 | whisper-small | R00_alone | `the ruler smiled and said` | P |
| 140 | whisper-small | SSpre | `the ruler smiled and said` | P |
| 140 | whisper-small | SDpre | `ruler smiled and said` | P |
| 220 | openai | R00_alone | `the ruler smiled and said`; `the ruler smiled and said` | P; P |
| 220 | openai | SSpre | `the ruler smiled and said`; `the ruler smiled and said` | P; P |
| 220 | openai | SDpre | `the ruler smiled and said`; `the ruler smiled and said` | P; P |
| 220 | whisper-small | R00_alone | `the ruler smiled and said` | P |
| 220 | whisper-small | SSpre | `the ruler smiled and said` | P |
| 220 | whisper-small | SDpre | `ruler smiled and said` | P |
| 300 | openai | R00_alone | `the ruler smiled and said`; `the ruler smiled and said` | P; P |
| 300 | openai | SSpre | `the rulers smiled and said` | P |
| 300 | openai | SDpre | `the ruler smiled and said` | P |
| 300 | whisper-small | R00_alone | `the ruler smiled and said` | P |
| 300 | whisper-small | SSpre | `the ruler smiled and said` | P |
| 300 | whisper-small | SDpre | `ruler smiled and said` | P |
| 380 | openai | R00_alone | `the ruler smiled and said`; `the ruler smiled and said` | P; P |
| 380 | openai | SSpre | `the ruler smiled and said` | P |
| 380 | openai | SDpre | `the ruler smiled and said` | P |
| 380 | whisper-small | R00_alone | `the ruler smiled and said` | P |
| 380 | whisper-small | SSpre | `the ruler smiled and said` | P |
| 380 | whisper-small | SDpre | `ruler smiled and said` | P |
| 460 | openai | R00_alone | `the ruler smiled and said`; `the ruler smiled and said` | P; P |
| 460 | openai | SSpre | `the ruler smiled and said` | P |
| 460 | openai | SDpre | `the ruler smiled and said` | P |
| 460 | whisper-small | R00_alone | `the ruler smiled and said` | P |
| 460 | whisper-small | SSpre | `the ruler smiled and said` | P |
| 460 | whisper-small | SDpre | `ruler smiled and said` | P |

### D-9. 誤った語(Melos→ruler)に差し替えた既知欠陥: 文脈に正しい名前『Melos』が有る/無いとき

| 条件 | engine | 領域転写 | Prod判定 |
|---|---|---|---|
| R00_alone | openai | `rulers said`; `rulers said` | NG; NG |
| R00_alone | whisper-small | `rulers said` | NG |
| NMpre_name3 | openai | `rulers said`; `rulers said` | NG; NG |
| NMpre_name3 | whisper-small | `rulers said` | NG |
| NMpre_name14 | openai | `rulers said`; `rulers said` | NG; NG |
| NMpre_name14 | whisper-small | `rulers said` | NG |
| NMpre_noname7 | openai | `rulers said`; `rulers said` | NG; NG |
| NMpre_noname7 | whisper-small | `rulers said` | NG |
| NMpre_diffvoice | openai | `rulers said`; `rulers said` | NG; NG |
| NMpre_diffvoice | whisper-small | `rulers said` | NG |

### C-3. 同じ付加秒数での 同一ナレーター文脈 vs 異ナレーター文脈 (前置文脈、Melos main、base)

| 付加秒(約) | 同一voice recipe(秒) | 異voice recipe(秒) | engine | 同一voice: Prod PASS / focus一致 | 異voice: Prod PASS / focus一致 |
|---|---|---|---|---|---|
| 3s | Npre3(2.2) | Dpre3(2.7) | openai | 2/13 (15%) / 0/13 (0%) | 0/13 (0%) / 0/13 (0%) |
| 3s | Npre3(2.2) | Dpre3(2.7) | azure | 6/11 (55%) / 2/11 (18%) | 2/7 (29%) / 1/7 (14%) |
| 3s | Npre3(2.2) | Dpre3(2.7) | whisper-small | 3/7 (43%) / 0/7 (0%) | 1/7 (14%) / 0/7 (0%) |
| 7-8s | Npre8(7.6) | Dpre8(5.5) | openai | 3/13 (23%) / 0/13 (0%) | 1/13 (8%) / 0/13 (0%) |
| 7-8s | Npre8(7.6) | Dpre8(5.5) | azure | 2/4 (50%) / 1/4 (25%) | 3/4 (75%) / 1/4 (25%) |
| 7-8s | Npre8(7.6) | Dpre8(5.5) | whisper-small | 1/7 (14%) / 0/7 (0%) | 5/7 (71%) / 0/7 (0%) |
| 13s | Npre14(14.4) | Dpre14(12.3) | openai | 6/13 (46%) / 0/13 (0%) | 5/13 (38%) / 1/13 (8%) |
| 13s | Npre14(14.4) | Dpre14(12.3) | whisper-small | 4/7 (57%) / 7/7 (100%) | 0/7 (0%) / 0/7 (0%) |
| 23-26s | Npre27(23.8) | Dpre25(20.5) | openai | 5/13 (38%) / 2/13 (15%) | 9/13 (69%) / 4/13 (31%) |
| 23-26s | Npre27(23.8) | Dpre25(20.5) | whisper-small | 1/7 (14%) / 6/7 (86%) | 2/7 (29%) / 0/7 (0%) |

### C-4. Standard(a2) vs Advanced(b1b): 同一recipe・OpenAI/Azure/whisper (base)

| recipe | engine | Std a2(6take) Prod PASS | Adv b1b(1take) Prod PASS |
|---|---|---|---|
| R00_alone | openai | 0/12 (0%) | 0/1 (0%) |
| R00_alone | azure | 6/12 (50%) | 0/2 (0%) |
| R00_alone | whisper-small | 4/6 (67%) | 0/1 (0%) |
| Npre3 | openai | 2/12 (17%) | 0/1 (0%) |
| Npre3 | azure | 4/9 (44%) | 2/2 (100%) |
| Npre3 | whisper-small | 3/6 (50%) | 0/1 (0%) |
| Dpre3 | openai | 0/12 (0%) | 0/1 (0%) |
| Dpre3 | azure | 2/6 (33%) | 0/1 (0%) |
| Dpre3 | whisper-small | 1/6 (17%) | 0/1 (0%) |
| Rboth | openai | 6/12 (50%) | 0/1 (0%) |
| Rboth | azure | 5/9 (56%) | 2/2 (100%) |
| Rboth | whisper-small | 1/6 (17%) | 0/1 (0%) |
| Rwin5 | openai | 5/12 (42%) | 0/1 (0%) |
| Rwin5 | azure | 2/3 (67%) | 0/1 (0%) |
| Rwin5 | whisper-small | 2/6 (33%) | 0/1 (0%) |

### D-10. Melos各take(本番判定つき): 単独ASRと文脈付きASRの比較(OpenAI。単独で『Melos said』にならないtakeが文脈で『Melos said』と書かれる=masking候補)

| target | 本番判定 | OpenAI単独の領域転写 | 文脈付き観測数 | 『melos said』一致 | Prod classify PASS(CS受理含む) | 『melos said』になったrecipe |
|---|---|---|---|---|---|---|
| a2_att1 | Std OK take(Prod: Tier3 Azure=Melo | mello said | 46 | 4 | 6 | Dpre6, Npost8, Rwin7 |
| a2_att2 | Std NG take(Prod: UNCERTAIN, Azure | mello said | 46 | 1 | 23 | Rwin7 |
| a2_att3 | Std fallback take(Prod: Pattern A  | mello said | 46 | 3 | 9 | Dpre25, Rwin7 |
| a2_att4 | Std NG take(Prod ASR: 'Mellis said | mellis said | 46 | 5 | 7 | Npost8, Npre27, Rwin7 |
| a2_att5 | Std NG take(Prod ASR: 'melloset' T | melloset; mellowset | 46 | 3 | 7 | Dpre25, Rwin7 |
| a2_att6 | Std NG take(Prod ASR: 'Mellowset'  | meloset | 45 | 17 | 20 | Dboth, Dpre11, Dpre14, Dpre25, Dpre5, Dpre6, Npost8, Npre27, Rboth, Rpre, Rwin5 |
| b1b_att1 | Adv take(Prod: UNCERTAIN 'Mello sa | mello said | 23 | 0 | 3 |  |

### C-2b. (委任_02追加) C-2をa2_att6除外で再集計(Melos main, base, 文脈あり条件のみ。att6は文脈付き『melos said』の真値が未確定のため分離)

| engine | 文脈にMelos語を含む | n(att6除外) | focus(Melos)一致 | exact_tokens | Prod PASS |
|---|---|---|---|---|---|
| openai | 含まない | 198 | 3/198 (2%) | 3/198 (2%) | 34/198 (17%) |
| openai | 含む | 55 | 13/55 (24%) | 13/55 (24%) | 21/55 (38%) |
| azure | 含まない | 39 | 10/39 (26%) | 10/39 (26%) | 25/39 (64%) |
| whisper-small | 含まない | 108 | 0/108 (0%) | 0/108 (0%) | 25/108 (23%) |
| whisper-small | 含む | 30 | 22/30 (73%) | 15/30 (50%) | 15/30 (50%) |

### C-2c. (委任_02追加) a2_att6のOpenAI文脈付き『melos said』(exact_tokens)観測の内訳: 文脈clipに『Melos』語を含むか / recipe別

- att6 文脈付き観測 45件、うち『melos said』 17件。このうち ctx_has_focus_word=true は 2件、false は 15件。
- 『melos said』になったdistinct recipe 11件: Dboth(ctx_has_focus=F, x2), Dpre11(ctx_has_focus=F, x2), Dpre14(ctx_has_focus=F, x1), Dpre25(ctx_has_focus=F, x2), Dpre5(ctx_has_focus=F, x1), Dpre6(ctx_has_focus=F, x1), Npost8(ctx_has_focus=T, x1), Npre27(ctx_has_focus=T, x1), Rboth(ctx_has_focus=F, x2), Rpre(ctx_has_focus=F, x2), Rwin5(ctx_has_focus=F, x2)
- distinct recipeのうち ctx_has_focus_word=false は 9/11

### C-2d. (委任_02追加) Dpre25(異voice前置25秒)の各take(OpenAI, base)

- a2_att1: n=2, ctx_has_focus=False, 転写=['mello said', 'melo said'], melos said=0
- a2_att2: n=2, ctx_has_focus=False, 転写=['melo said'], melos said=0
- a2_att3: n=2, ctx_has_focus=False, 転写=['melo said', 'melos said'], melos said=1
- a2_att4: n=2, ctx_has_focus=False, 転写=['malice said'], melos said=0
- a2_att5: n=2, ctx_has_focus=False, 転写=['melo said', 'melos said'], melos said=1
- a2_att6: n=2, ctx_has_focus=False, 転写=['melos said'], melos said=2
- b1b_att1: n=1, ctx_has_focus=False, 転写=['mello said'], melos said=0

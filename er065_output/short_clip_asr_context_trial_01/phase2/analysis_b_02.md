## B-P2-1. 長さ vs s+s融合: Melosの後ろがs始まりでない短尺clip(2語cut)・元clip全体の単独ASR (phase2新規)

target = `Melos X`の2語cut(語末sの後ろが c/t/h/l/f=非歯擦音) または元clip全体。canonicalは各行。

| target | canonical | engine | n | exact(綴り全一致) | Melos語が`melos`で一致 | 出力例(focus語の内訳) | Production判定PASS | 音韻説明可(FUSION/HOMOPHONE) |
|---|---|---|---|---|---|---|---|---|
| en:a2_c1whole | Melos called across the hall, | azure | 1 | 1/1 (100%) | 1/1 (100%) | {'melos': 1} | 1/1 (100%) | 0/1 (0%) |
| en:a2_c1whole | Melos called across the hall, | openai | 2 | 0/2 (0%) | 0/2 (0%) | {'mellos': 2} | 0/2 (0%) | 2/2 (100%) |
| en:a2_c1whole | Melos called across the hall, | whisper:medium | 1 | 0/1 (0%) | 0/1 (0%) | {'mellos': 1} | 0/1 (0%) | 1/1 (100%) |
| en:a2_c1whole | Melos called across the hall, | whisper:small | 1 | 0/1 (0%) | 0/1 (0%) | {'mellos': 1} | 0/1 (0%) | 1/1 (100%) |
| en:a2_called2 | Melos called. | azure | 1 | 0/1 (0%) | 1/1 (100%) | {'melos': 1} | 0/1 (0%) | 0/1 (0%) |
| en:a2_called2 | Melos called. | openai | 2 | 0/2 (0%) | 0/2 (0%) | {"mellow's": 1, "mello's": 1} | 0/2 (0%) | 0/2 (0%) |
| en:a2_called2 | Melos called. | whisper:medium | 1 | 0/1 (0%) | 0/1 (0%) | {'mellows': 1} | 0/1 (0%) | 0/1 (0%) |
| en:a2_called2 | Melos called. | whisper:small | 1 | 0/1 (0%) | 0/1 (0%) | {"melo's": 1} | 0/1 (0%) | 0/1 (0%) |
| en:a2_fell2 | Melos fell. | azure | 1 | 0/1 (0%) | 1/1 (100%) | {'melos': 1} | 0/1 (0%) | 0/1 (0%) |
| en:a2_fell2 | Melos fell. | openai | 2 | 0/2 (0%) | 2/2 (100%) | {'melos': 2} | 0/2 (0%) | 2/2 (100%) |
| en:a2_fell2 | Melos fell. | whisper:medium | 1 | 0/1 (0%) | 0/1 (0%) | {'mellows': 1} | 0/1 (0%) | 0/1 (0%) |
| en:a2_fell2 | Melos fell. | whisper:small | 1 | 0/1 (0%) | 0/1 (0%) | {'mellows': 1} | 0/1 (0%) | 1/1 (100%) |
| en:a2_had2 | Melos had. | azure | 1 | 1/1 (100%) | 1/1 (100%) | {'melos': 1} | 1/1 (100%) | 0/1 (0%) |
| en:a2_had2 | Melos had. | openai | 2 | 1/2 (50%) | 1/2 (50%) | {'mellos': 1, 'melos': 1} | 1/2 (50%) | 1/2 (50%) |
| en:a2_had2 | Melos had. | whisper:medium | 1 | 0/1 (0%) | 0/1 (0%) | {'mellos': 1} | 0/1 (0%) | 1/1 (100%) |
| en:a2_had2 | Melos had. | whisper:small | 1 | 1/1 (100%) | 1/1 (100%) | {'melos': 1} | 1/1 (100%) | 0/1 (0%) |
| en:a2_listened2 | Melos listened. | azure | 1 | 0/1 (0%) | 1/1 (100%) | {'melos': 1} | 0/1 (0%) | 0/1 (0%) |
| en:a2_listened2 | Melos listened. | openai | 2 | 0/2 (0%) | 0/2 (0%) | {None: 2} | 0/2 (0%) | 0/2 (0%) |
| en:a2_listened2 | Melos listened. | whisper:medium | 1 | 0/1 (0%) | 0/1 (0%) | {'mellows': 1} | 0/1 (0%) | 1/1 (100%) |
| en:a2_listened2 | Melos listened. | whisper:small | 1 | 0/1 (0%) | 0/1 (0%) | {'mellows': 1} | 0/1 (0%) | 1/1 (100%) |
| en:a2_p3c3whole | His friend turned around, and Melo | azure | 1 | 1/1 (100%) | 1/1 (100%) | {'melos': 1} | 1/1 (100%) | 0/1 (0%) |
| en:a2_p3c3whole | His friend turned around, and Melo | openai | 2 | 2/2 (100%) | 2/2 (100%) | {'melos': 2} | 2/2 (100%) | 0/2 (0%) |
| en:a2_p3c3whole | His friend turned around, and Melo | whisper:medium | 1 | 1/1 (100%) | 1/1 (100%) | {'melos': 1} | 1/1 (100%) | 0/1 (0%) |
| en:a2_p3c3whole | His friend turned around, and Melo | whisper:small | 1 | 1/1 (100%) | 1/1 (100%) | {'melos': 1} | 1/1 (100%) | 0/1 (0%) |
| en:a2_turned2 | Melos turned. | azure | 1 | 0/1 (0%) | 1/1 (100%) | {'melos': 1} | 0/1 (0%) | 0/1 (0%) |
| en:a2_turned2 | Melos turned. | openai | 2 | 0/2 (0%) | 0/2 (0%) | {"mellow's": 2} | 0/2 (0%) | 0/2 (0%) |
| en:a2_turned2 | Melos turned. | whisper:medium | 1 | 0/1 (0%) | 0/1 (0%) | {'mellos': 1} | 0/1 (0%) | 0/1 (0%) |
| en:a2_turned2 | Melos turned. | whisper:small | 1 | 0/1 (0%) | 0/1 (0%) | {'mellows': 1} | 0/1 (0%) | 0/1 (0%) |
| en:b1b_c1whole | Melos's voice rang through the hal | azure | 1 | 1/1 (100%) | 0/1 (0%) | {"melos's": 1} | 1/1 (100%) | 0/1 (0%) |
| en:b1b_c1whole | Melos's voice rang through the hal | openai | 2 | 0/2 (0%) | 0/2 (0%) | {"mello's": 2} | 0/2 (0%) | 0/2 (0%) |
| en:b1b_c1whole | Melos's voice rang through the hal | whisper:medium | 1 | 0/1 (0%) | 0/1 (0%) | {"melos'": 1} | 0/1 (0%) | 0/1 (0%) |
| en:b1b_c1whole | Melos's voice rang through the hal | whisper:small | 1 | 0/1 (0%) | 0/1 (0%) | {"melos'": 1} | 0/1 (0%) | 0/1 (0%) |
| en:b1b_fell2 | Melos fell. | azure | 1 | 1/1 (100%) | 1/1 (100%) | {'melos': 1} | 1/1 (100%) | 0/1 (0%) |
| en:b1b_fell2 | Melos fell. | openai | 2 | 0/2 (0%) | 0/2 (0%) | {'mellos': 2} | 0/2 (0%) | 2/2 (100%) |
| en:b1b_fell2 | Melos fell. | whisper:medium | 1 | 1/1 (100%) | 1/1 (100%) | {'melos': 1} | 1/1 (100%) | 0/1 (0%) |
| en:b1b_fell2 | Melos fell. | whisper:small | 1 | 1/1 (100%) | 1/1 (100%) | {'melos': 1} | 1/1 (100%) | 0/1 (0%) |
| en:b1b_listened2 | Melos listened. | azure | 1 | 0/1 (0%) | 1/1 (100%) | {'melos': 1} | 0/1 (0%) | 0/1 (0%) |
| en:b1b_listened2 | Melos listened. | openai | 2 | 0/2 (0%) | 1/2 (50%) | {'mellos': 1, 'melos': 1} | 0/2 (0%) | 0/2 (0%) |
| en:b1b_listened2 | Melos listened. | whisper:medium | 1 | 0/1 (0%) | 1/1 (100%) | {'melos': 1} | 0/1 (0%) | 0/1 (0%) |
| en:b1b_listened2 | Melos listened. | whisper:small | 1 | 0/1 (0%) | 1/1 (100%) | {'melos': 1} | 0/1 (0%) | 0/1 (0%) |
| en:b1b_p3c3whole | His friend turned. Melos fell agai | azure | 1 | 1/1 (100%) | 1/1 (100%) | {'melos': 1} | 1/1 (100%) | 0/1 (0%) |
| en:b1b_p3c3whole | His friend turned. Melos fell agai | openai | 2 | 0/2 (0%) | 0/2 (0%) | {None: 1, 'mellows': 1} | 0/2 (0%) | 1/2 (50%) |
| en:b1b_p3c3whole | His friend turned. Melos fell agai | whisper:medium | 1 | 1/1 (100%) | 1/1 (100%) | {'melos': 1} | 1/1 (100%) | 0/1 (0%) |
| en:b1b_p3c3whole | His friend turned. Melos fell agai | whisper:small | 1 | 1/1 (100%) | 1/1 (100%) | {'melos': 1} | 1/1 (100%) | 0/1 (0%) |
| en:b1b_turned2 | Melos turned. | azure | 1 | 0/1 (0%) | 1/1 (100%) | {'melos': 1} | 0/1 (0%) | 0/1 (0%) |
| en:b1b_turned2 | Melos turned. | openai | 2 | 0/2 (0%) | 0/2 (0%) | {None: 2} | 0/2 (0%) | 0/2 (0%) |
| en:b1b_turned2 | Melos turned. | whisper:medium | 1 | 0/1 (0%) | 0/1 (0%) | {'mellows': 1} | 0/1 (0%) | 0/1 (0%) |
| en:b1b_turned2 | Melos turned. | whisper:small | 1 | 0/1 (0%) | 0/1 (0%) | {'mellows': 1} | 0/1 (0%) | 0/1 (0%) |
| v2:a2_called2 | Melos called. | azure | 1 | 0/1 (0%) | 1/1 (100%) | {'melos': 1} | 0/1 (0%) | 0/1 (0%) |
| v2:a2_called2 | Melos called. | openai | 2 | 0/2 (0%) | 0/2 (0%) | {'mellos': 2} | 0/2 (0%) | 0/2 (0%) |
| v2:a2_called2 | Melos called. | whisper:small | 1 | 0/1 (0%) | 0/1 (0%) | {"melo's": 1} | 0/1 (0%) | 0/1 (0%) |
| v2:a2_fell2 | Melos fell. | azure | 1 | 0/1 (0%) | 1/1 (100%) | {'melos': 1} | 0/1 (0%) | 0/1 (0%) |
| v2:a2_fell2 | Melos fell. | openai | 2 | 0/2 (0%) | 0/2 (0%) | {"mello's": 1, 'mellosfel': 1} | 0/2 (0%) | 0/2 (0%) |
| v2:a2_fell2 | Melos fell. | whisper:small | 1 | 0/1 (0%) | 0/1 (0%) | {'mellows': 1} | 0/1 (0%) | 1/1 (100%) |
| v2:a2_had2 | Melos had. | azure | 1 | 1/1 (100%) | 1/1 (100%) | {'melos': 1} | 1/1 (100%) | 0/1 (0%) |
| v2:a2_had2 | Melos had. | openai | 2 | 0/2 (0%) | 0/2 (0%) | {'mellos': 2} | 0/2 (0%) | 1/2 (50%) |
| v2:a2_had2 | Melos had. | whisper:small | 1 | 1/1 (100%) | 1/1 (100%) | {'melos': 1} | 1/1 (100%) | 0/1 (0%) |
| v2:a2_listened2 | Melos listened. | azure | 1 | 0/1 (0%) | 1/1 (100%) | {'melos': 1} | 0/1 (0%) | 0/1 (0%) |
| v2:a2_listened2 | Melos listened. | openai | 2 | 0/2 (0%) | 0/2 (0%) | {None: 2} | 0/2 (0%) | 0/2 (0%) |
| v2:a2_listened2 | Melos listened. | whisper:small | 1 | 0/1 (0%) | 1/1 (100%) | {'melos': 1} | 0/1 (0%) | 0/1 (0%) |
| v2:a2_turned2 | Melos turned. | azure | 1 | 0/1 (0%) | 0/1 (0%) | {"mellow's": 1} | 0/1 (0%) | 0/1 (0%) |
| v2:a2_turned2 | Melos turned. | openai | 2 | 0/2 (0%) | 0/2 (0%) | {"mellow's": 1, "mello's": 1} | 0/2 (0%) | 0/2 (0%) |
| v2:a2_turned2 | Melos turned. | whisper:small | 1 | 0/1 (0%) | 0/1 (0%) | {'mellows': 1} | 0/1 (0%) | 0/1 (0%) |
| v2:b1b_fell2 | Melos fell. | azure | 1 | 1/1 (100%) | 1/1 (100%) | {'melos': 1} | 1/1 (100%) | 0/1 (0%) |
| v2:b1b_fell2 | Melos fell. | openai | 2 | 0/2 (0%) | 1/2 (50%) | {'mellos': 1, 'melos': 1} | 0/2 (0%) | 2/2 (100%) |
| v2:b1b_fell2 | Melos fell. | whisper:small | 1 | 0/1 (0%) | 0/1 (0%) | {'mellows': 1} | 0/1 (0%) | 1/1 (100%) |
| v2:b1b_listened2 | Melos listened. | azure | 1 | 0/1 (0%) | 0/1 (0%) | {'melosistic': 1} | 0/1 (0%) | 0/1 (0%) |
| v2:b1b_listened2 | Melos listened. | openai | 2 | 0/2 (0%) | 0/2 (0%) | {'mellowslis': 1, 'melloslis': 1} | 0/2 (0%) | 0/2 (0%) |
| v2:b1b_listened2 | Melos listened. | whisper:small | 1 | 0/1 (0%) | 1/1 (100%) | {'melos': 1} | 0/1 (0%) | 0/1 (0%) |
| v2:b1b_turned2 | Melos turned. | azure | 1 | 0/1 (0%) | 1/1 (100%) | {'melos': 1} | 0/1 (0%) | 0/1 (0%) |
| v2:b1b_turned2 | Melos turned. | openai | 2 | 0/2 (0%) | 0/2 (0%) | {"mellow's": 2} | 0/2 (0%) | 0/2 (0%) |
| v2:b1b_turned2 | Melos turned. | whisper:small | 1 | 0/1 (0%) | 0/1 (0%) | {'mellow': 1} | 0/1 (0%) | 0/1 (0%) |

## B-P2-2. 総括: 評価単位(長さ・s+s有無・文脈)別の正認識率 (Melos main, 新規+委任_01既存実測)

exact=target領域が canonical と綴り全一致 / melos語=focus語が`melos`と綴り一致 / Prod PASS=Production classify_asr_match(role無)でshould_pass。
| 評価単位 | engine | n観測 | exact | Melos語が`melos` | Production PASS |
|---|---|---|---|---|---|
| 2語cut v2 `Melos X`(X=非s始まり, 0.75-1.2秒, 終端=次語直前) | openai | 16 | 0/16 (0%) | 1/16 (6%) | 0/16 (0%) |
| 2語cut v2 `Melos X`(X=非s始まり, 0.75-1.2秒, 終端=次語直前) | azure | 8 | 2/8 (25%) | 6/8 (75%) | 2/8 (25%) |
| 2語cut v2 `Melos X`(X=非s始まり, 0.75-1.2秒, 終端=次語直前) | whisper:small | 8 | 1/8 (12%) | 3/8 (38%) | 1/8 (12%) |
| 2語cut v1(終端が語末+0.06秒: -ed等が欠け得る。参考) | openai | 16 | 1/16 (6%) | 4/16 (25%) | 1/16 (6%) |
| 2語cut v1(終端が語末+0.06秒: -ed等が欠け得る。参考) | azure | 8 | 2/8 (25%) | 8/8 (100%) | 2/8 (25%) |
| 2語cut v1(終端が語末+0.06秒: -ed等が欠け得る。参考) | whisper:small | 8 | 2/8 (25%) | 3/8 (38%) | 2/8 (25%) |
| 2語cut v1(終端が語末+0.06秒: -ed等が欠け得る。参考) | whisper:medium | 8 | 1/8 (12%) | 2/8 (25%) | 1/8 (12%) |
| 元clip全体(Melos+非s始まり, 2.7-4.6秒) | openai | 8 | 2/8 (25%) | 2/8 (25%) | 2/8 (25%) |
| 元clip全体(Melos+非s始まり, 2.7-4.6秒) | azure | 4 | 4/4 (100%) | 3/4 (75%) | 4/4 (100%) |
| 元clip全体(Melos+非s始まり, 2.7-4.6秒) | whisper:small | 4 | 2/4 (50%) | 2/4 (50%) | 2/4 (50%) |
| 元clip全体(Melos+非s始まり, 2.7-4.6秒) | whisper:medium | 4 | 2/4 (50%) | 2/4 (50%) | 2/4 (50%) |
| Melos said. 単独2語 (R00_alone, 7 take) [委任_01] | openai | 13 | 0/13 (0%) | 0/13 (0%) | 0/13 (0%) |
| Melos said. 単独2語 (R00_alone, 7 take) [委任_01] | azure | 14 | 2/14 (14%) | 2/14 (14%) | 6/14 (43%) |
| Melos said. +直前台詞 gap300 (Rpre) [委任_01] | openai | 13 | 2/13 (15%) | 2/13 (15%) | 4/13 (31%) |
| Melos said. +直前台詞 gap300 (Rpre) [委任_01] | azure | 4 | 1/4 (25%) | 1/4 (25%) | 3/4 (75%) |
| Melos said. +直後台詞 gap300 (Rpost) [委任_01] | openai | 13 | 0/13 (0%) | 0/13 (0%) | 0/13 (0%) |
| Melos said. +直後台詞 gap300 (Rpost) [委任_01] | azure | 4 | 1/4 (25%) | 1/4 (25%) | 2/4 (50%) |
| Melos said. 前後台詞 gap300 (Rboth) [委任_01] | openai | 13 | 2/13 (15%) | 2/13 (15%) | 6/13 (46%) |
| Melos said. 前後台詞 gap300 (Rboth) [委任_01] | azure | 11 | 2/11 (18%) | 2/11 (18%) | 7/11 (64%) |
| Melos said. 前後2-3clip (Rwin5/Rwin7 28秒) [委任_01] | openai | 25 | 10/25 (40%) | 10/25 (40%) | 13/25 (52%) |
| Melos said. 前後2-3clip (Rwin5/Rwin7 28秒) [委任_01] | azure | 4 | 1/4 (25%) | 1/4 (25%) | 2/4 (50%) |
| Melos said. Rpre gap80 [委任_03新規] | openai | 14 | 0/14 (0%) | 0/14 (0%) | 2/14 (14%) |
| Melos said. Rpre gap80 [委任_03新規] | azure | 7 | 0/7 (0%) | 0/7 (0%) | 4/7 (57%) |
| Melos said. Rpre gap80 [委任_03新規] | whisper:small | 7 | 0/7 (0%) | 0/7 (0%) | 2/7 (29%) |
| Melos said. Rpost gap80 [委任_03新規] | openai | 14 | 0/14 (0%) | 0/14 (0%) | 0/14 (0%) |
| Melos said. Rpost gap80 [委任_03新規] | whisper:small | 7 | 0/7 (0%) | 0/7 (0%) | 0/7 (0%) |
| Melos said. Rboth gap80 [委任_03新規] | openai | 14 | 0/14 (0%) | 0/14 (0%) | 4/14 (29%) |
| Melos said. Rboth gap80 [委任_03新規] | whisper:small | 7 | 0/7 (0%) | 0/7 (0%) | 1/7 (14%) |

## B-P2-3. 『1文単位』(直前の台詞+attribution `Melos said.`) gap80ms vs gap300ms: take別 (OpenAI/Azure/whisper-small, Rpre)

| take | engine | gap300(委任_01) exact/n | gap80(新規) exact/n | gap80 region出力 |
|---|---|---|---|---|
| a2_att1 | openai | 0/2 (0%) | 0/2 (0%) | mello said |
| a2_att1 | azure | 1/1 (100%) | 0/1 (0%) | mellow said |
| a2_att1 | whisper:small | 0/1 (0%) | 0/1 (0%) | melo said |
| a2_att2 | openai | 0/2 (0%) | 0/2 (0%) | mello said; melo said |
| a2_att2 | azure | - | 0/1 (0%) | mellow said |
| a2_att2 | whisper:small | 0/1 (0%) | 0/1 (0%) | mello said |
| a2_att3 | openai | 0/2 (0%) | 0/2 (0%) | mello said |
| a2_att3 | azure | 0/1 (0%) | 0/1 (0%) | melo said |
| a2_att3 | whisper:small | 0/1 (0%) | 0/1 (0%) | mello said |
| a2_att4 | openai | 0/2 (0%) | 0/2 (0%) | mello said |
| a2_att4 | azure | - | 0/1 (0%) | melo said |
| a2_att4 | whisper:small | 0/1 (0%) | 0/1 (0%) | mellow said |
| a2_att5 | openai | 0/2 (0%) | 0/2 (0%) | mello said; melo said |
| a2_att5 | azure | - | 0/1 (0%) | mellow said |
| a2_att5 | whisper:small | 0/1 (0%) | 0/1 (0%) | mellow said |
| a2_att6 | openai | 2/2 (100%) | 0/2 (0%) |  |
| a2_att6 | azure | 0/1 (0%) | 0/1 (0%) | melo said |
| a2_att6 | whisper:small | 0/1 (0%) | 0/1 (0%) | melo said |
| b1b_att1 | openai | 0/1 (0%) | 0/2 (0%) | mello said; mellow said |
| b1b_att1 | azure | 0/1 (0%) | 0/1 (0%) | melo said |
| b1b_att1 | whisper:small | 0/1 (0%) | 0/1 (0%) | mellow said |

## B-P2-4. 一般語(Production音声の実境界)2語窓の単独ASR: 子音連続の型別 正認識率 (phase2新規)

型: SS=s/z+s/z, TT=t+t, DD=d+d, NN=n+n, YOD=t/d/s/z+y, SHS=s/z+sh/ch/jh, CTRL=融合しない子音境界(対照)。窓は0.5-1.6秒の2語。exact=2語が綴り全一致。観測=target x engine x rep(OpenAIは3rep)。
| 型 | engine | 観測 | exact | 不一致のうち 音韻説明可(FUSION/HOMOPHONE/VOICING) | 不一致のうち 説明不能 | Production PASS |
|---|---|---|---|---|---|---|
| SS | openai | 24 | 12/24 (50%) | 0 | 12 | 12/24 (50%) |
| SS | azure | 8 | 3/8 (38%) | 1 | 4 | 4/8 (50%) |
| SS | whisper:small | 8 | 2/8 (25%) | 1 | 5 | 3/8 (38%) |
| SS | whisper:medium | 8 | 3/8 (38%) | 1 | 4 | 4/8 (50%) |
| TT | openai | 24 | 9/24 (38%) | 0 | 15 | 9/24 (38%) |
| TT | azure | 8 | 3/8 (38%) | 0 | 5 | 3/8 (38%) |
| TT | whisper:small | 8 | 2/8 (25%) | 0 | 6 | 2/8 (25%) |
| TT | whisper:medium | 8 | 4/8 (50%) | 0 | 4 | 4/8 (50%) |
| DD | openai | 24 | 7/24 (29%) | 2 | 15 | 9/24 (38%) |
| DD | azure | 8 | 6/8 (75%) | 0 | 2 | 6/8 (75%) |
| DD | whisper:small | 8 | 8/8 (100%) | 0 | 0 | 8/8 (100%) |
| DD | whisper:medium | 8 | 7/8 (88%) | 0 | 1 | 7/8 (88%) |
| NN | openai | 24 | 16/24 (67%) | 0 | 8 | 16/24 (67%) |
| NN | azure | 8 | 3/8 (38%) | 0 | 5 | 4/8 (50%) |
| NN | whisper:small | 8 | 2/8 (25%) | 0 | 6 | 2/8 (25%) |
| NN | whisper:medium | 8 | 3/8 (38%) | 0 | 5 | 3/8 (38%) |
| YOD | openai | 24 | 10/24 (42%) | 0 | 14 | 10/24 (42%) |
| YOD | azure | 8 | 1/8 (12%) | 0 | 7 | 2/8 (25%) |
| YOD | whisper:small | 8 | 3/8 (38%) | 0 | 5 | 3/8 (38%) |
| YOD | whisper:medium | 8 | 3/8 (38%) | 0 | 5 | 3/8 (38%) |
| SHS | openai | 24 | 3/24 (12%) | 0 | 21 | 6/24 (25%) |
| SHS | azure | 8 | 4/8 (50%) | 0 | 4 | 5/8 (62%) |
| SHS | whisper:small | 8 | 2/8 (25%) | 0 | 6 | 2/8 (25%) |
| SHS | whisper:medium | 8 | 1/8 (12%) | 0 | 7 | 2/8 (25%) |
| CTRL | openai | 24 | 12/24 (50%) | 0 | 12 | 15/24 (62%) |
| CTRL | azure | 8 | 3/8 (38%) | 0 | 5 | 4/8 (50%) |
| CTRL | whisper:small | 8 | 5/8 (62%) | 0 | 3 | 7/8 (88%) |
| CTRL | whisper:medium | 8 | 5/8 (62%) | 0 | 3 | 7/8 (88%) |

不一致の全列挙(canonical -> region : 音韻判定 / Production):

- CTRL/g_CTRL_00 [azure] rep1 `Small Refrigerator` -> `small` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- CTRL/g_CTRL_00 [whisper:medium] rep1 `Small Refrigerator` -> `a small refrigerator` : NOT_EXPLAINED / NORMALIZED_MATCH
- CTRL/g_CTRL_00 [whisper:small] rep1 `Small Refrigerator` -> `a small refrigerator` : NOT_EXPLAINED / NORMALIZED_MATCH
- CTRL/g_CTRL_01 [openai] rep2 `feel personal` -> `if feel personal` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- CTRL/g_CTRL_01 [openai] rep3 `feel personal` -> `if feel personal` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- CTRL/g_CTRL_01 [openai] rep1 `feel personal` -> `if feel personal` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- CTRL/g_CTRL_02 [azure] rep1 `for factories` -> `` : NOT_EXPLAINED / EMPTY
- CTRL/g_CTRL_02 [openai] rep2 `for factories` -> `and for factories` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- CTRL/g_CTRL_02 [openai] rep3 `for factories` -> `and for factories` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- CTRL/g_CTRL_02 [openai] rep1 `for factories` -> `and for factories` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- CTRL/g_CTRL_04 [azure] rep1 `stomach felt` -> `fell` : NOT_EXPLAINED / TTS_FAILURE
- CTRL/g_CTRL_04 [openai] rep2 `stomach felt` -> `starmek far` : NO_PHONOLOGICAL_EVIDENCE / TTS_FAILURE
- CTRL/g_CTRL_04 [openai] rep3 `stomach felt` -> `starmac parle` : NOT_EXPLAINED / TTS_FAILURE
- CTRL/g_CTRL_04 [openai] rep1 `stomach felt` -> `c'estomac faim` : NO_PHONOLOGICAL_EVIDENCE / TTS_FAILURE
- CTRL/g_CTRL_04 [whisper:medium] rep1 `stomach felt` -> `his stomach fell` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- CTRL/g_CTRL_04 [whisper:small] rep1 `stomach felt` -> `` : NOT_EXPLAINED / EMPTY
- CTRL/g_CTRL_06 [azure] rep1 `from one` -> `from 1 00` : NO_PHONOLOGICAL_EVIDENCE / TRUE_CONTENT_MISMATCH
- CTRL/g_CTRL_07 [azure] rep1 `job The` -> `job` : NOT_EXPLAINED / NORMALIZED_MATCH
- CTRL/g_CTRL_07 [openai] rep2 `job The` -> `job` : NOT_EXPLAINED / NORMALIZED_MATCH
- CTRL/g_CTRL_07 [openai] rep3 `job The` -> `job` : NOT_EXPLAINED / NORMALIZED_MATCH
- CTRL/g_CTRL_07 [openai] rep1 `job The` -> `job` : NOT_EXPLAINED / NORMALIZED_MATCH
- CTRL/g_CTRL_07 [whisper:medium] rep1 `job The` -> `job` : NOT_EXPLAINED / NORMALIZED_MATCH
- CTRL/g_CTRL_07 [whisper:small] rep1 `job The` -> `job` : NOT_EXPLAINED / NORMALIZED_MATCH
- DD/g_DD_00 [azure] rep1 `and drying` -> `and dry` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- DD/g_DD_00 [openai] rep2 `and drying` -> `and dry` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- DD/g_DD_00 [openai] rep3 `and drying` -> `quick and dry` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- DD/g_DD_00 [openai] rep1 `and drying` -> `and dry` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- DD/g_DD_00 [whisper:medium] rep1 `and drying` -> `and dry` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- DD/g_DD_02 [openai] rep2 `shared desks` -> `to your desks` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- DD/g_DD_02 [openai] rep3 `shared desks` -> `sheer deaths` : NOT_EXPLAINED / TTS_FAILURE
- DD/g_DD_02 [openai] rep1 `shared desks` -> `sheer deaths` : NOT_EXPLAINED / TTS_FAILURE
- DD/g_DD_03 [azure] rep1 `assigned desks` -> `assigns desks` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- DD/g_DD_03 [openai] rep2 `assigned desks` -> `assign desks` : PHON_EXPLAINED_FUSION / CONNECTED_SPEECH_ACCEPT
- DD/g_DD_03 [openai] rep3 `assigned desks` -> `assign desk` : NOT_EXPLAINED / TTS_FAILURE
- DD/g_DD_03 [openai] rep1 `assigned desks` -> `assign desks` : PHON_EXPLAINED_FUSION / CONNECTED_SPEECH_ACCEPT
- DD/g_DD_05 [openai] rep2 `shared desks` -> `shared desk` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- DD/g_DD_05 [openai] rep3 `shared desks` -> `shared desk` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- DD/g_DD_05 [openai] rep1 `shared desks` -> `shared desk` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- DD/g_DD_06 [openai] rep2 `and daily` -> `late and daily` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- DD/g_DD_06 [openai] rep3 `and daily` -> `ate and daily` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- DD/g_DD_06 [openai] rep1 `and daily` -> `ate and daily` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- DD/g_DD_07 [openai] rep2 `and do` -> `and do you` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- DD/g_DD_07 [openai] rep3 `and do` -> `and do you` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- NN/g_NN_00 [azure] rep1 `listen notice` -> `listen no` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- NN/g_NN_00 [openai] rep2 `listen notice` -> `listen no` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- NN/g_NN_00 [openai] rep3 `listen notice` -> `listen no` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- NN/g_NN_00 [openai] rep1 `listen notice` -> `listen no` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- NN/g_NN_00 [whisper:medium] rep1 `listen notice` -> `you listen` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- NN/g_NN_00 [whisper:small] rep1 `listen notice` -> `listen note` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- NN/g_NN_01 [whisper:small] rep1 `pattern not` -> `pattern` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- NN/g_NN_02 [azure] rep1 `expectation not` -> `expectation` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- NN/g_NN_02 [whisper:medium] rep1 `expectation not` -> `and expectation` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- NN/g_NN_03 [azure] rep1 `design needs` -> `design need` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- NN/g_NN_03 [whisper:small] rep1 `design needs` -> `design need` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- NN/g_NN_04 [openai] rep2 `win Next` -> `next` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- NN/g_NN_05 [azure] rep1 `association not` -> `an association not` : NOT_EXPLAINED / NORMALIZED_MATCH
- NN/g_NN_05 [openai] rep2 `association not` -> `association non` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- NN/g_NN_05 [openai] rep3 `association not` -> `association` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- NN/g_NN_05 [openai] rep1 `association not` -> `association` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- NN/g_NN_05 [whisper:medium] rep1 `association not` -> `association` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- NN/g_NN_05 [whisper:small] rep1 `association not` -> `association` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- NN/g_NN_06 [azure] rep1 `pattern not` -> `` : NOT_EXPLAINED / EMPTY
- NN/g_NN_06 [openai] rep2 `pattern not` -> `pattern` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- NN/g_NN_06 [whisper:medium] rep1 `pattern not` -> `pattern` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- NN/g_NN_06 [whisper:small] rep1 `pattern not` -> `pattern` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- NN/g_NN_07 [whisper:medium] rep1 `listen notice` -> `if you listen notice` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- NN/g_NN_07 [whisper:small] rep1 `listen notice` -> `listen no` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- SHS/g_SHS_00 [azure] rep1 `researchers changed` -> `researchers change` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- SHS/g_SHS_00 [openai] rep2 `researchers changed` -> `researchers change` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- SHS/g_SHS_00 [openai] rep3 `researchers changed` -> `researchers change` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- SHS/g_SHS_00 [openai] rep1 `researchers changed` -> `researchers change` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- SHS/g_SHS_00 [whisper:medium] rep1 `researchers changed` -> `the researchers changed their minds and decided to go back to the lab` : NOT_EXPLAINED / TTS_FAILURE
- SHS/g_SHS_00 [whisper:small] rep1 `researchers changed` -> `researchers change` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- SHS/g_SHS_01 [azure] rep1 `evidence shows` -> `the evidence shows` : NOT_EXPLAINED / NORMALIZED_MATCH
- SHS/g_SHS_01 [openai] rep2 `evidence shows` -> `the evidence shows` : NOT_EXPLAINED / NORMALIZED_MATCH
- SHS/g_SHS_01 [openai] rep3 `evidence shows` -> `the evidence shows` : NOT_EXPLAINED / NORMALIZED_MATCH
- SHS/g_SHS_01 [openai] rep1 `evidence shows` -> `the evidence shows` : NOT_EXPLAINED / NORMALIZED_MATCH
- SHS/g_SHS_01 [whisper:medium] rep1 `evidence shows` -> `the evidence shows` : NOT_EXPLAINED / NORMALIZED_MATCH
- SHS/g_SHS_02 [openai] rep2 `use shared` -> `will you share` : NOT_EXPLAINED / TTS_FAILURE
- SHS/g_SHS_02 [openai] rep3 `use shared` -> `will you share` : NOT_EXPLAINED / TTS_FAILURE
- SHS/g_SHS_02 [openai] rep1 `use shared` -> `i'll use share` : NOT_EXPLAINED / TTS_FAILURE
- SHS/g_SHS_02 [whisper:medium] rep1 `use shared` -> `we'll use share` : NOT_EXPLAINED / TTS_FAILURE
- SHS/g_SHS_02 [whisper:small] rep1 `use shared` -> `` : NOT_EXPLAINED / EMPTY
- SHS/g_SHS_03 [azure] rep1 `choice changes` -> `choice change` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- SHS/g_SHS_03 [openai] rep2 `choice changes` -> `all choices change` : NOT_EXPLAINED / TTS_FAILURE
- SHS/g_SHS_03 [openai] rep3 `choice changes` -> `all choice change` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- SHS/g_SHS_03 [openai] rep1 `choice changes` -> `all choice changed` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- SHS/g_SHS_03 [whisper:medium] rep1 `choice changes` -> `all choice changes` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- SHS/g_SHS_03 [whisper:small] rep1 `choice changes` -> `all choice change` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- SHS/g_SHS_04 [openai] rep2 `coverage Small` -> `in coverage` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- SHS/g_SHS_04 [openai] rep3 `coverage Small` -> `in coverage` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- SHS/g_SHS_04 [openai] rep1 `coverage Small` -> `in coverage` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- SHS/g_SHS_04 [whisper:medium] rep1 `coverage Small` -> `coverage` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- SHS/g_SHS_04 [whisper:small] rep1 `coverage Small` -> `in coverage` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- SHS/g_SHS_05 [azure] rep1 `makes checking` -> `makes check` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- SHS/g_SHS_05 [openai] rep2 `makes checking` -> `he makes checking` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- SHS/g_SHS_05 [openai] rep3 `makes checking` -> `he makes check` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- SHS/g_SHS_05 [openai] rep1 `makes checking` -> `he makes check` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- SHS/g_SHS_05 [whisper:medium] rep1 `makes checking` -> `he makes check` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- SHS/g_SHS_05 [whisper:small] rep1 `makes checking` -> `he makes checking` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- SHS/g_SHS_07 [openai] rep2 `use shared` -> `will you share` : NOT_EXPLAINED / TTS_FAILURE
- SHS/g_SHS_07 [openai] rep3 `use shared` -> `i'll use share` : NOT_EXPLAINED / TTS_FAILURE
- SHS/g_SHS_07 [openai] rep1 `use shared` -> `will you share` : NOT_EXPLAINED / TTS_FAILURE
- SHS/g_SHS_07 [whisper:medium] rep1 `use shared` -> `we'll use share` : NOT_EXPLAINED / TTS_FAILURE
- SHS/g_SHS_07 [whisper:small] rep1 `use shared` -> `` : NOT_EXPLAINED / EMPTY
- SS/g_SS_00 [azure] rep1 `this small` -> `by this small` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- SS/g_SS_00 [openai] rep2 `this small` -> `by this small` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- SS/g_SS_00 [openai] rep3 `this small` -> `by this small` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- SS/g_SS_00 [openai] rep1 `this small` -> `by this small` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- SS/g_SS_01 [whisper:small] rep1 `These studies` -> `these study` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- SS/g_SS_02 [azure] rep1 `his sister's` -> `his sisters` : PHON_HOMOPHONE_ONLY / NORMALIZED_MATCH
- SS/g_SS_02 [whisper:small] rep1 `his sister's` -> `his sisters` : PHON_HOMOPHONE_ONLY / NORMALIZED_MATCH
- SS/g_SS_03 [azure] rep1 `users stayed` -> `top users state` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- SS/g_SS_03 [openai] rep2 `users stayed` -> `top users state` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- SS/g_SS_03 [openai] rep3 `users stayed` -> `top users state` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- SS/g_SS_03 [openai] rep1 `users stayed` -> `top users stay` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- SS/g_SS_03 [whisper:medium] rep1 `users stayed` -> `top users stay` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- SS/g_SS_03 [whisper:small] rep1 `users stayed` -> `users state` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- SS/g_SS_04 [azure] rep1 `affects someone` -> `` : NOT_EXPLAINED / EMPTY
- SS/g_SS_04 [openai] rep2 `affects someone` -> `the facts someone` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- SS/g_SS_04 [openai] rep3 `affects someone` -> `the facts someone` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- SS/g_SS_04 [openai] rep1 `affects someone` -> `the effects someone` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- SS/g_SS_04 [whisper:medium] rep1 `affects someone` -> `affect someone` : PHON_EXPLAINED_FUSION / CONNECTED_SPEECH_ACCEPT
- SS/g_SS_05 [openai] rep2 `tests some` -> `altaz some` : NO_PHONOLOGICAL_EVIDENCE / TRUE_CONTENT_MISMATCH
- SS/g_SS_05 [openai] rep3 `tests some` -> `altas` : NOT_EXPLAINED / TTS_FAILURE
- SS/g_SS_05 [openai] rep1 `tests some` -> `multitasks some` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- SS/g_SS_05 [whisper:medium] rep1 `tests some` -> `` : NOT_EXPLAINED / EMPTY
- SS/g_SS_05 [whisper:small] rep1 `tests some` -> `tests` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- SS/g_SS_06 [whisper:medium] rep1 `times so` -> `different times so let's get started` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- SS/g_SS_06 [whisper:small] rep1 `times so` -> `times` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- SS/g_SS_07 [azure] rep1 `these situations` -> `in these situations` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- SS/g_SS_07 [whisper:medium] rep1 `these situations` -> `in these situations change is necessary` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- SS/g_SS_07 [whisper:small] rep1 `these situations` -> `in these situations` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- TT/g_TT_00 [openai] rep2 `meant to` -> `meant to be` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- TT/g_TT_00 [openai] rep3 `meant to` -> `meant to be` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- TT/g_TT_00 [openai] rep1 `meant to` -> `meant to be` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- TT/g_TT_00 [whisper:small] rep1 `meant to` -> `meant` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- TT/g_TT_01 [azure] rep1 `different to` -> `different different differe` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- TT/g_TT_01 [openai] rep2 `different to` -> `is different to you` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- TT/g_TT_01 [openai] rep3 `different to` -> `is different to` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- TT/g_TT_01 [openai] rep1 `different to` -> `is different to` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- TT/g_TT_01 [whisper:medium] rep1 `different to` -> `different` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- TT/g_TT_01 [whisper:small] rep1 `different to` -> `different` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- TT/g_TT_02 [azure] rep1 `restaurant tipping` -> `restaurant tip` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- TT/g_TT_02 [whisper:medium] rep1 `restaurant tipping` -> `restaurant tip` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- TT/g_TT_02 [whisper:small] rep1 `restaurant tipping` -> `restaurant tip` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- TT/g_TT_04 [azure] rep1 `without telling` -> `` : NOT_EXPLAINED / EMPTY
- TT/g_TT_04 [openai] rep2 `without telling` -> `this without telling` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- TT/g_TT_04 [openai] rep3 `without telling` -> `this without telling` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- TT/g_TT_04 [openai] rep1 `without telling` -> `this is without telling` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- TT/g_TT_04 [whisper:small] rep1 `without telling` -> `news without telling` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- TT/g_TT_05 [azure] rep1 `market to` -> `` : NOT_EXPLAINED / EMPTY
- TT/g_TT_05 [whisper:medium] rep1 `market to` -> `market` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- TT/g_TT_05 [whisper:small] rep1 `market to` -> `market` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- TT/g_TT_06 [openai] rep2 `what to` -> `decide what to` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- TT/g_TT_06 [openai] rep3 `what to` -> `decide what to believe` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- TT/g_TT_06 [openai] rep1 `what to` -> `decide what to believe` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- TT/g_TT_07 [azure] rep1 `sunlight touched` -> `sunlight touch` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- TT/g_TT_07 [openai] rep2 `sunlight touched` -> `sunlight touch` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- TT/g_TT_07 [openai] rep3 `sunlight touched` -> `sunlight touches` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- TT/g_TT_07 [openai] rep1 `sunlight touched` -> `sunlight touch` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- TT/g_TT_07 [whisper:medium] rep1 `sunlight touched` -> `sunlight touch` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- TT/g_TT_07 [whisper:small] rep1 `sunlight touched` -> `sunlight touch` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- YOD/g_YOD_00 [azure] rep1 `what you` -> `` : NOT_EXPLAINED / EMPTY
- YOD/g_YOD_01 [azure] rep1 `what users` -> `and what use` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- YOD/g_YOD_01 [openai] rep2 `what users` -> `and what you` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- YOD/g_YOD_01 [openai] rep3 `what users` -> `and what use` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- YOD/g_YOD_01 [openai] rep1 `what users` -> `and what use` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- YOD/g_YOD_01 [whisper:medium] rep1 `what users` -> `and what use` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- YOD/g_YOD_01 [whisper:small] rep1 `what users` -> `and what use` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- YOD/g_YOD_02 [azure] rep1 `what you` -> `` : NOT_EXPLAINED / EMPTY
- YOD/g_YOD_02 [whisper:medium] rep1 `what you` -> `but what you` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- YOD/g_YOD_03 [openai] rep2 `not use` -> `not using` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- YOD/g_YOD_03 [openai] rep3 `not use` -> `not using` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- YOD/g_YOD_03 [openai] rep1 `not use` -> `not using` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- YOD/g_YOD_03 [whisper:small] rep1 `not use` -> `not used` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- YOD/g_YOD_04 [azure] rep1 `end you` -> `the end you` : NOT_EXPLAINED / NORMALIZED_MATCH
- YOD/g_YOD_04 [openai] rep2 `end you` -> `in the end you` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- YOD/g_YOD_04 [openai] rep3 `end you` -> `in the end you` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- YOD/g_YOD_04 [openai] rep1 `end you` -> `in the end you` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- YOD/g_YOD_04 [whisper:medium] rep1 `end you` -> `in the end you` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- YOD/g_YOD_04 [whisper:small] rep1 `end you` -> `the end` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- YOD/g_YOD_05 [azure] rep1 `that users` -> `that use` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- YOD/g_YOD_05 [openai] rep2 `that users` -> `it's that you` : NOT_EXPLAINED / TTS_FAILURE
- YOD/g_YOD_05 [openai] rep3 `that users` -> `that use` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- YOD/g_YOD_05 [openai] rep1 `that users` -> `it's that you` : NOT_EXPLAINED / TTS_FAILURE
- YOD/g_YOD_05 [whisper:medium] rep1 `that users` -> `is that use` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- YOD/g_YOD_05 [whisper:small] rep1 `that users` -> `is that you` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- YOD/g_YOD_06 [azure] rep1 `end you'll` -> `` : NOT_EXPLAINED / EMPTY
- YOD/g_YOD_06 [openai] rep2 `end you'll` -> `and you'll` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- YOD/g_YOD_06 [openai] rep3 `end you'll` -> `in the end you'll` : NOT_EXPLAINED / ASR_VALIDATION_UNCERTAIN
- YOD/g_YOD_06 [whisper:medium] rep1 `end you'll` -> `and you'll` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- YOD/g_YOD_06 [whisper:small] rep1 `end you'll` -> `the end you're` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH
- YOD/g_YOD_07 [azure] rep1 `It used` -> `it use` : NOT_EXPLAINED / TRUE_CONTENT_MISMATCH

## B-P2-5. Melos said 編集音声(融合長の摩擦区間を単独s相当80msまで短縮)のASR: 元音声との比較

| take | engine | 元音声の出力(委任_01, R00_alone) | 編集後の出力(phase2) |
|---|---|---|---|
| a2_att1 | openai | ['mello said'] | ['mello said', 'mellow said'] |
| a2_att1 | azure | ['melos said'] | ['mello said'] |
| a2_att1 | whisper:small | ['mello said'] | ['melo said'] |
| a2_att3 | openai | ['mello said'] | ['mello said'] |
| a2_att3 | azure | ['melo said'] | ['melo said'] |
| a2_att3 | whisper:small | ['melo said'] | ['mello said'] |
| a2_att4 | openai | ['mellis said'] | ['mello said'] |
| a2_att4 | azure | ['mallow said'] | ['mallow said'] |
| a2_att4 | whisper:small | ['melo said'] | ['mellow said'] |
| a2_att5 | openai | ['melloset', 'mellowset'] | ['mello sed', 'melloset'] |
| a2_att5 | azure | ['melo said'] | ['melo said'] |
| a2_att5 | whisper:small | ['melo said'] | ['melo said'] |
| a2_att6 | openai | ['meloset'] | ["mellow's that", 'mellows at', 'mellows that'] |
| a2_att6 | azure | ['mellow said'] | ['melosat'] |
| a2_att6 | whisper:small | ['melo said'] | ['melozet'] |
# PHASE_B_RESULT_01 — Azure PhraseList重み比較 Phase B結果(自動生成: eval_v02、raw全行・除外なし)

eval機械判定: **REJECTED**(Fable最終ラベル前。到達上限Status=`PLW_TRIAL_CLOSEOUT_PENDING_FABLE`)  /  R(FULL_STORY role、Primary-NGかつベースラインNGの正例)= **9**

Azure raw行数(Phase B)= 410、err行=0(別集計、母数から除外)。使用: Azure en-US(SDK 1.50.0、連続認識、`PhraseListGrammar`+`setWeight`)、Primary=OpenAI `gpt-4o-mini-transcribe`(prompt無し、本番同一関数)、TTS=`gemini-3.8-flash-lite-tts`(最新世代flash-lite、Production同一)。

## 1 本番判定のflip(主要指標)

| 重み | role | Primary-NG正例のうち up(NG→PASS系) | down(PASS→NG) | 変化なしNG | 変化なしPASS | 不安定(除外) | Primary PASS(除外) | 片側符号検定p | α |
|---|---|---|---|---|---|---|---|---|---|
| pl_w1.5 | full_story | 1 | 0 | 8 | 26 | 0 | 15 | 0.5000 | 0.05 |
| pl_w1.5 | no_tier3 | 1 | 0 | 8 | 26 | 0 | 15 | 0.5000 | 0.05 |
| pl_w2.0 | full_story | 2 | 0 | 7 | 26 | 0 | 15 | 0.2500 | 0.025 |
| pl_w2.0 | no_tier3 | 2 | 0 | 7 | 26 | 0 | 15 | 0.2500 | 0.025 |

## 2 判定基準(§3-v02)と機械判定

| 重み | 1識別力(R≥6) | 2効果量 | 3符号検定 | 4広がり | 5副作用なし | 6悪化なし | 7 Tier3なし非逆転 | 状態 | up cluster数 / Voice話速数 |
|---|---|---|---|---|---|---|---|---|---|
| pl_w1.5 | True | False | False | False | False | True | True | **REJECTED** | 1 / 1 |
| pl_w2.0 | True | False | False | False | False | True | True | **REJECTED** | 2 / 1 |

up wav(FULL_STORY role):
- pl_w1.5: up=['P1_nonsib_Aoede_take3'] / down=[] / melos_degraded_extra=[]
- pl_w2.0: up=['P1_nonsib_Aoede_take3', 'P5_repeat_Aoede_take1'] / down=[] / melos_degraded_extra=[]

## 3 副指標: Melos正認識率(wav単位、rep1)

| 集合 | 条件 | Melos正認識/n | 率 |
|---|---|---|---|
| 正例(合成30) | no_pl | 8/30 | 27% |
| 正例(合成30) | pl_unspecified | 20/30 | 67% |
| 正例(合成30) | pl_w1.5 | 22/30 | 73% |
| 正例(合成30) | pl_w2.0 | 25/30 | 83% |
| 正例(本番take20) | no_pl | 8/20 | 40% |
| 正例(本番take20) | pl_unspecified | 14/20 | 70% |
| 正例(本番take20) | pl_w1.5 | 14/20 | 70% |
| 正例(本番take20) | pl_w2.0 | 16/20 | 80% |
| 正例(合算50) | no_pl | 16/50 | 32% |
| 正例(合算50) | pl_unspecified | 34/50 | 68% |
| 正例(合算50) | pl_w1.5 | 36/50 | 72% |
| 正例(合算50) | pl_w2.0 | 41/50 | 82% |

### 3b 文脈別・Voice/話速別・長さ別のMelos正認識数(rep1。n中の正認識wav数)

| グループ | n | no_pl | pl_unspecified | pl_w1.5 | pl_w2.0 |
|---|---|---|---|---|---|
| 合成/文脈=P1_nonsib | 12 | 3 | 8 | 9 | 9 |
| 合成/Voice話速=Aoede | 10 | 2 | 6 | 8 | 9 |
| 合成/Voice話速=Aoede+減速 | 10 | 2 | 6 | 6 | 7 |
| 合成/Voice話速=Charon | 10 | 4 | 8 | 8 | 9 |
| 合成/文脈=P2_sib | 3 | 0 | 0 | 1 | 3 |
| 合成/文脈=P3_final | 3 | 2 | 3 | 3 | 3 |
| 合成/文脈=P4_mid | 3 | 2 | 3 | 3 | 3 |
| 合成/文脈=P5_repeat | 3 | 0 | 0 | 0 | 1 |
| 合成/文脈=P6_long | 3 | 1 | 3 | 3 | 3 |
| 合成/文脈=P7_compete | 3 | 0 | 3 | 3 | 3 |
| 本番take/長さ=5〜15秒 | 5 | 2 | 5 | 5 | 5 |
| 本番take/segment=full_story_part1 | 11 | 4 | 8 | 8 | 9 |
| 本番take/長さ=≤5秒 | 11 | 6 | 9 | 9 | 10 |
| 本番take/長さ=>15秒 | 4 | 0 | 0 | 0 | 1 |
| 本番take/segment=full_story_part2 | 2 | 0 | 0 | 0 | 1 |
| 本番take/segment=full_story_part3 | 4 | 3 | 3 | 3 | 3 |
| 本番take/segment=comment_1 | 1 | 0 | 1 | 1 | 1 |
| 本番take/segment=comment_2 | 1 | 0 | 1 | 1 | 1 |
| 本番take/segment=comment_3 | 1 | 1 | 1 | 1 | 1 |

## 4 負例(誤PASS・誤Melos)と境界例

有効負例=N1・N3の6wav+minimal pair 27wav=33wav。rule of three(0件のとき95%上限≈3/n)を併記。

| 条件 | role | n | 誤PASS(canonical=Melos文を注入した本番判定がPASS系) | 誤PASS率 | 0件のとき95%上限(3/n) |
|---|---|---|---|---|---|
| no_pl | full_story | 33 | 8 ['N1_mellow_Aoede_take1', 'N1_mellow_Aoede_take1_slow6', 'N1_mellow_Charon_take1', 'N3_mello_Aoede_take1', 'N3_mello_Aoede_take1_slow6', 'N3_mello_Charon_take1', 'NM_P3_mullos_Aoede_take1', 'NM_P3_mullos_Aoede_take1_slow6'] | 24% | - |
| pl_unspecified | full_story | 33 | 8 ['N1_mellow_Aoede_take1', 'N1_mellow_Aoede_take1_slow6', 'N1_mellow_Charon_take1', 'N3_mello_Aoede_take1', 'N3_mello_Aoede_take1_slow6', 'N3_mello_Charon_take1', 'NM_P3_mullos_Aoede_take1', 'NM_P3_mullos_Aoede_take1_slow6'] | 24% | - |
| pl_w1.5 | full_story | 33 | 9 ['N1_mellow_Aoede_take1', 'N1_mellow_Aoede_take1_slow6', 'N1_mellow_Charon_take1', 'N3_mello_Aoede_take1', 'N3_mello_Aoede_take1_slow6', 'N3_mello_Charon_take1', 'NM_P3_mullos_Aoede_take1', 'NM_P3_mullos_Aoede_take1_slow6', 'NM_P4_mullos_Charon_take1'] | 27% | - |
| pl_w2.0 | full_story | 33 | 11 ['N1_mellow_Aoede_take1', 'N1_mellow_Aoede_take1_slow6', 'N1_mellow_Charon_take1', 'N3_mello_Aoede_take1', 'N3_mello_Aoede_take1_slow6', 'N3_mello_Charon_take1', 'NM_P3_mullos_Aoede_take1', 'NM_P3_mullos_Aoede_take1_slow6', 'NM_P4_mullos_Aoede_take1', 'NM_P4_mullos_Aoede_take1_slow6', 'NM_P4_mullos_Charon_take1'] | 33% | - |
| no_pl | no_tier3 | 33 | 8 ['N1_mellow_Aoede_take1', 'N1_mellow_Aoede_take1_slow6', 'N1_mellow_Charon_take1', 'N3_mello_Aoede_take1', 'N3_mello_Aoede_take1_slow6', 'N3_mello_Charon_take1', 'NM_P3_mullos_Aoede_take1', 'NM_P3_mullos_Aoede_take1_slow6'] | 24% | - |
| pl_unspecified | no_tier3 | 33 | 8 ['N1_mellow_Aoede_take1', 'N1_mellow_Aoede_take1_slow6', 'N1_mellow_Charon_take1', 'N3_mello_Aoede_take1', 'N3_mello_Aoede_take1_slow6', 'N3_mello_Charon_take1', 'NM_P3_mullos_Aoede_take1', 'NM_P3_mullos_Aoede_take1_slow6'] | 24% | - |
| pl_w1.5 | no_tier3 | 33 | 9 ['N1_mellow_Aoede_take1', 'N1_mellow_Aoede_take1_slow6', 'N1_mellow_Charon_take1', 'N3_mello_Aoede_take1', 'N3_mello_Aoede_take1_slow6', 'N3_mello_Charon_take1', 'NM_P3_mullos_Aoede_take1', 'NM_P3_mullos_Aoede_take1_slow6', 'NM_P4_mullos_Charon_take1'] | 27% | - |
| pl_w2.0 | no_tier3 | 33 | 11 ['N1_mellow_Aoede_take1', 'N1_mellow_Aoede_take1_slow6', 'N1_mellow_Charon_take1', 'N3_mello_Aoede_take1', 'N3_mello_Aoede_take1_slow6', 'N3_mello_Charon_take1', 'NM_P3_mullos_Aoede_take1', 'NM_P3_mullos_Aoede_take1_slow6', 'NM_P4_mullos_Aoede_take1', 'NM_P4_mullos_Aoede_take1_slow6', 'NM_P4_mullos_Charon_take1'] | 33% | - |

| 条件 | n | Azure誤`Melos`(Melosと出力) | 率 | 0件のとき95%上限 |
|---|---|---|---|---|
| no_pl | 33 | 2 ['NM_P3_mullos_Aoede_take1', 'NM_P3_mullos_Aoede_take1_slow6'] | 6% | - |
| pl_unspecified | 33 | 2 ['NM_P3_mullos_Aoede_take1', 'NM_P3_mullos_Aoede_take1_slow6'] | 6% | - |
| pl_w1.5 | 33 | 3 ['NM_P3_mullos_Aoede_take1', 'NM_P3_mullos_Aoede_take1_slow6', 'NM_P4_mullos_Charon_take1'] | 9% | - |
| pl_w2.0 | 33 | 5 ['NM_P3_mullos_Aoede_take1', 'NM_P3_mullos_Aoede_take1_slow6', 'NM_P4_mullos_Aoede_take1', 'NM_P4_mullos_Aoede_take1_slow6', 'NM_P4_mullos_Charon_take1'] | 15% | - |

### 境界例(N2 mellows / N4 Milos。判定には使わず別枠)

| role | 条件 | n | 本番判定PASS系 | Azureが`Melos`と出力 |
|---|---|---|---|---|
| full_story | no_pl | 6 | [] | [] |
| no_tier3 | no_pl | 6 | [] | [] |
| full_story | pl_unspecified | 6 | [] | [] |
| no_tier3 | pl_unspecified | 6 | [] | [] |
| full_story | pl_w1.5 | 6 | ['N4_milos_Aoede_take1', 'N4_milos_Aoede_take1_slow6', 'N4_milos_Charon_take1'] | ['N4_milos_Aoede_take1', 'N4_milos_Aoede_take1_slow6', 'N4_milos_Charon_take1'] |
| no_tier3 | pl_w1.5 | 6 | ['N4_milos_Aoede_take1', 'N4_milos_Aoede_take1_slow6', 'N4_milos_Charon_take1'] | ['N4_milos_Aoede_take1', 'N4_milos_Aoede_take1_slow6', 'N4_milos_Charon_take1'] |
| full_story | pl_w2.0 | 6 | ['N4_milos_Aoede_take1', 'N4_milos_Aoede_take1_slow6', 'N4_milos_Charon_take1'] | ['N4_milos_Aoede_take1', 'N4_milos_Aoede_take1_slow6', 'N4_milos_Charon_take1'] |
| no_tier3 | pl_w2.0 | 6 | ['N4_milos_Aoede_take1', 'N4_milos_Aoede_take1_slow6', 'N4_milos_Charon_take1'] | ['N4_milos_Aoede_take1', 'N4_milos_Aoede_take1_slow6', 'N4_milos_Charon_take1'] |

### 重みが新たに作った誤PASS(ベースラインNG→重みwでPASS系、有効負例。FULL_STORY role)

| 重み | wav | TTSに渡した文 | Primary転写 | ベースラインAzure | 重みwのAzure |
|---|---|---|---|---|---|
| pl_w1.5 | NM_P4_mullos_Charon_take1 | Then Mullos walked away. | Then Moloss walked away. | Then Molos walked away. | Then Melos walked away. |
| pl_w2.0 | NM_P4_mullos_Aoede_take1 | Then Mullos walked away. | Then Molos walked away. | Then Molos walked away. | Then Melos walked away. |
| pl_w2.0 | NM_P4_mullos_Aoede_take1_slow6 | Then Mullos walked away. | Then Mulos walked away. | Then Molos walked away. | Then Melos walked away. |
| pl_w2.0 | NM_P4_mullos_Charon_take1 | Then Mullos walked away. | Then Moloss walked away. | Then Molos walked away. | Then Melos walked away. |

### 参考: PhraseList自体(現行の重み未指定)の価値 = no_pl → pl_unspecified の本番判定flip

| role | up(NG→PASS系) | down | 変化なしNG | 変化なしPASS | 不安定 | Primary PASS(除外) |
|---|---|---|---|---|---|---|
| full_story | 15 | 0 | 9 | 11 | 0 | 15 |
| no_tier3 | 15 | 0 | 9 | 11 | 0 | 15 |
有効負例の誤PASS(no_pl→pl_unspecified): {'full_story|no_pl': 8, 'full_story|pl_unspecified': 8, 'no_tier3|no_pl': 8, 'no_tier3|pl_unspecified': 8}

## 5 他語perturbation(副作用、M-5)

| 重み | 比較wav数 | 新規誤り語数合計 | うち保護対象diff数 | 保護種別 | Melosからの平均語距離 |
|---|---|---|---|---|---|
| pl_w1.5 | 89 | 2 | 1 | ['content_word'] | 5.0 |
| pl_w2.0 | 89 | 2 | 1 | ['content_word'] | 5.0 |
| no_pl | 89 | 0 | 0 | [] | - |

## 6 決定論の抜き打ち(S-2)

| 条件 | rep1/rep2ペア数 | 転写一致 | 不一致wav |
|---|---|---|---|
| no_pl | 9 | 9 | [] |
| pl_unspecified | 9 | 9 | [] |
| pl_w1.0 | 9 | 9 | [] |
| pl_w1.5 | 9 | 9 | [] |
| pl_w2.0 | 9 | 9 | [] |

`pl_w1.0` vs `pl_unspecified`(送信バイト同一): 9/9転写一致、不一致=[]

## 7 5分類(S-8)の機械フラグ

```json
{
 "primary_ng_positive_wavs": 35,
 "baseline_pass_fraction_among_primary_ng": 0.7428571428571429,
 "no_pl_pass": 11,
 "pl_unspecified_pass": 26,
 "transcript_change_rate_w1.5": {
  "n": 83,
  "changed": 4,
  "rate": 0.04819277108433735
 },
 "transcript_change_rate_w2.0": {
  "n": 83,
  "changed": 11,
  "rate": 0.13253012048192772
 },
 "residual_ng_after_w2.0": {
  "n": 7,
  "of_R": 9,
  "fraction": 0.7777777777777778
 },
 "transcript_change_rate_pl_unspecified_vs_no_pl": {
  "n": 83,
  "changed": 19,
  "rate": 0.2289156626506024
 },
 "w1.5_up_top_cluster_share": 1.0,
 "flags": {
  "a_条件が簡単すぎた": true,
  "b_PLが効いていない": false,
  "c_1.0(現行)で既に十分": true,
  "d_文脈・音声品質で変わる": false,
  "e_重みでは解決できない": true
 }
}
```

## 8 flipしたwavの転写(試聴ページと対応)

- pl_w1.5/full_story/up `P1_nonsib_Aoede_take3`: 原稿=`Melos drank deeply from the cold stream.` Primary=`Mellos drank deeply from the cold stream.` ベースラインAzure=`Mellows drank deeply from the cold stream.` w=`Melos drank deeply from the Coldstream.`
- pl_w1.5/no_tier3/up `P1_nonsib_Aoede_take3`: 原稿=`Melos drank deeply from the cold stream.` Primary=`Mellos drank deeply from the cold stream.` ベースラインAzure=`Mellows drank deeply from the cold stream.` w=`Melos drank deeply from the Coldstream.`
- pl_w2.0/full_story/up `P1_nonsib_Aoede_take3`: 原稿=`Melos drank deeply from the cold stream.` Primary=`Mellos drank deeply from the cold stream.` ベースラインAzure=`Mellows drank deeply from the cold stream.` w=`Melos drank deeply from the Coldstream.`
- pl_w2.0/full_story/up `P5_repeat_Aoede_take1`: 原稿=`Melos spoke, and Melos listened.` Primary=`Mella spoke, and Mella listened.` ベースラインAzure=`Melo spoke and Mellos listened.` w=`Melos spoke, and Melos listened.`
- pl_w2.0/no_tier3/up `P1_nonsib_Aoede_take3`: 原稿=`Melos drank deeply from the cold stream.` Primary=`Mellos drank deeply from the cold stream.` ベースラインAzure=`Mellows drank deeply from the cold stream.` w=`Melos drank deeply from the Coldstream.`
- pl_w2.0/no_tier3/up `P5_repeat_Aoede_take1`: 原稿=`Melos spoke, and Melos listened.` Primary=`Mella spoke, and Mella listened.` ベースラインAzure=`Melo spoke and Mellos listened.` w=`Melos spoke, and Melos listened.`

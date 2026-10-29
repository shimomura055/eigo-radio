# repetition_qa method_d prime(短lag) Algieba声 偽陽性分析 01 (2026-10-29)

範囲: 読み取り・再計測のみ(API 0、Production/閾値/Prompt/台帳変更0、runner起動なし)。集計は `attempts/*.json` の `repetition_qa_evidence.method_d_prime_spectral_short_lag` を走査(scratchpad script)。実装=`er011_open121_repetition_qa_production_01.py:310`(analyze_profile_d_prime_short_lag、lag 0.5〜2.0秒、sim>=0.7のrun長>=0.6秒でflag)。

## 1. 集計(過去全attempt、`**/attempts/*.json`、method_d'記録あり3036件・flagged 171)
| 声 | 試行 | flagged | 率 |
|---|---|---|---|
| Algieba | 517 | 124 | 24.0% |
| Iapetus | 25 | 15 | 60% |
| Orus / Charon / Sadaltager | 53 / 161 / 18 | 9 / 8 / 6 | 17% / 5% / 33% |
| Zephyr / Schedar / Fenrir / Puck | 198/119/56/47 | 3/2/2/1 | 0.9〜2.1% |
| Aoede | 1683 | 1 | 0.06% |
| Erinome / Kore | 107 / 52 | 0 / 0 | 0 |

Algieba flagged 124件の内訳(同一dir・同segment_idの後続attemptで判定。人間ラベルは存在しない):
- method_d'のみflag(method_a n-gram=ASR上の語句反復なし、method_d長lagも非flag): **122件**。別方式も同時flag: 2件(NUMERIC_EQUIVALENCE、後続attemptでPASS)。ASR全文は全件が原文一致系(NORMALIZED/EXACT/高類似)。
- 後続attemptで**verified=true(再生成でPASS)になったもの: 59件**。後続はあるが最後まで未verified: 41件。後続なし(最終attempt): 24件。
- segment単位(Algieba声でflagが1回でも出たsegment 51件): 最終verified(再生成で解消)25、最終もflag/未verified 26。
- **真の反復と確認された件数: 0件(過去に聴取ラベルが無く確認手段なし)**。ASR語句の二重出現が無い(method_a非flag)122/124は、「同じ語句の二重発声」を示す証拠なし。確定には聴取が必要(聴取済み0件=不明124件)。
- 注: 後続PASSは「偽陽性だった」ことの証明ではない(再生成で別の声が出ただけの可能性)。flagはHard blockのため、flagのまま採用された例もない。

## 2. 再計測(読み取り専用、同一実装を呼出)
藪の中part1_c3の3試行wavで `compute_shared_self_similarity` + `analyze_profile_d_prime_short_lag` を再実行: run/lag/sim = 1.24/0.72/0.828、0.82/0.76/0.839、0.80/0.59/0.715。**全て記録値と一致(再現性OK)**。
run長分布(全試行、秒): Algieba min0.04/中央0.41/p90 0.70/p95 0.77/max1.24(n=517)、非Algieba 0.05/0.31/0.45/0.52/1.18(n=2519)。
| run長帯 | Algieba | 非Algieba |
|---|---|---|
| <0.2 | 59 | 300 |
| 0.2-0.4 | 183 | 1730 |
| 0.4-0.5 | 94 | 327 |
| 0.5-0.6 (flag直下) | 57 | 115 |
| 0.6-0.8 | 101 | 40 |
| 0.8-1.0 | 21 | 6 |
| >=1.0 | 2 | 1 |

Algieba分布は非Algieba より全体に約0.1秒右にシフト(中央0.41 vs 0.31)。閾値0.6の上下に集中(0.5-0.6が57、0.6-0.8が101)。
較正根拠(`er011_open121_repetition_qa_production_01.py:106-110`): Trial-02の陰性最大0.5秒/陽性最小0.7秒、閾値0.6はその中間(マージン0.1〜0.2)。Algieba flagの多く(101/124)は0.6-0.8帯=較正の「陰性最大0.5〜陽性最小0.7」の曖昧帯に入る。0.8秒以上は23件。Trial-02較正データの声構成は本分析では未確認。

## 3. 藪の中 part1_c3 (woodcutter/Algieba/pro) 3試行の所見
対象: `er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01/a2/narration/attempts/full_story_part1_c3_attempt{1,2,3}_*.wav`(24kHz)。
- 先頭: 無音(RMS<0.005)が約0.25〜0.3秒、以後RMS 0.08〜0.19で発声が安定。
- flag区間: 試行1 t=0.45s lag0.72s run1.24s / 試行2 t=0.29s lag0.76s run0.82s / 試行3 t=0.70s lag0.59s run0.80s。いずれも発声開始直後〜2語目付近。
- 波形レベル相関(区間a vs b、正規化相互相関ピーク): 0.51 / 0.20 / 0.09。振幅スペクトルcos: 0.58 / 0.80 / 0.48。同一音声の複製なら波形相関は高い(目安>0.8)はずで、**波形は一致せず、スペクトル包絡の自己類似(声質・母音の持続)と整合**。区間間のF0推定も異なる(約116/110Hz、105/83Hz、70/103Hz)=同一断片の再生ではない。
- local whisper(small、語単位timestamp、`er008_disfluency_qa_18.transcribe_verbatim`): 3試行とも先頭は「He(0.0) lay(0.4-0.56) near(0.7-0.96) the mountain(1.1-1.5) road,(1.4-1.8)」の順で**同語の二重出現なし**。flag区間は lay/near/the mountain 付近=異なる語の連なり。
- 所見(断定しない): 真の語句反復の証拠は得られず、声質の自己類似の可能性が高い。ただし聴取は未実施。確定手段=ユーザー聴取(`user_test/family_z_in_a_grove_hr_01/`)。

## 4. 閾値変更の是非を判断するための材料(提案のみ・**適用しない**。閾値/Gate変更=ユーザー承認事項)
- 影響: Algieba声はflag率24%。藪の中part1_c3は3試行すべてflag。Algieba 51 segment中26 segmentが最終までflag。1試行pro TTS約¥1.5(part1_c3実績: 3試行¥4.73)として、flag 124試行分の再生成は累計約¥190相当(概算)。費用よりSTOP/HR化(納期)の影響が大きい。
- 選択肢案(いずれも未実施・要ユーザー承認): (a) 閾値据置+Algieba flagを試聴確認(HR)へ回す運用 (b) 声別閾値のTrial(既存陽性ラベル+聴取ラベルで再較正) (c) method_d'のflagを「ASR語句二重出現でconfirm」する局所確認(方式Dの`confirm_by_local_asr_overlap`:177と同型、先例OPEN-128)に揃える。(c)は閾値を変えず、語句反復を伴う真陽性は維持できる見込み。
- 閾値変更しない場合のリスク: Algieba声を使う作品で同様のSTOPが再発。変更する場合のリスク: 声質由来でない真の短lag反復の見逃し(誤PASS)。

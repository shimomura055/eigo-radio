# EVAL_01 M1 OOV 複数発音候補方式 offline評価(API 0 / JPY0 / Production無変更 / Ledger読取のみ)

- Ledger md5 前後一致: True / 候補上限 CAP=6 / 評価=既存転写の再判定のみ

## 1. Melos said 12件 Before / F1のみ / 本設計(C1+C2)

候補(事前固定・ASR非依存): [C2_ledger_expected conf=low] M IY L AA S; [C2_ledger_alt conf=low] M IH L AA S; [C2_ledger_alt conf=low] M EH L AA S; [C2_ledger_alt conf=low] M EH L OW S

| # | level/target/take | OpenAI転写 | Azure転写 | Before(OR) | F1のみ(OR) | 本設計(OR) | 本設計(両エンジン同一候補) | 一致候補(出典) | 残差/判定理由 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | std/raw/t1 | Mello said. | Mellow said. | NG | NG | PASS | PASS | op:mello->melo[C2_ledger_alt,conf=low,M EH L OW S]<br>az:mellow->melo[C2_ledger_alt,conf=low,M EH L OW S] | op=ACCEPT_M1; az=ACCEPT_M1 |
| 2 | std/raw/t2 | Mello said. | Mellow said. | NG | NG | PASS | PASS | op:mello->melo[C2_ledger_alt,conf=low,M EH L OW S]<br>az:mellow->melo[C2_ledger_alt,conf=low,M EH L OW S] | op=ACCEPT_M1; az=ACCEPT_M1 |
| 3 | std/raw/t3 | Mello said. | Melos said. | PASS | PASS | PASS | PASS | op:mello->melo[C2_ledger_alt,conf=low,M EH L OW S] | op=ACCEPT_M1; az=EXACT |
| 4 | std/raw/t4 | Mello said, | Melo said. | PASS | PASS | PASS | PASS | op:mello->melo[C2_ledger_alt,conf=low,M EH L OW S] | op=ACCEPT_M1; az=PROD_PASS_UNCHANGED |
| 5 | std/slow6/t1 | Mellow said. | Mellow said.  | NG | NG | PASS | PASS | op:mellow->melo[C2_ledger_alt,conf=low,M EH L OW S]<br>az:mellow->melo[C2_ledger_alt,conf=low,M EH L OW S] | op=ACCEPT_M1; az=ACCEPT_M1 |
| 6 | std/slow6/t2 | Mello said. | Mellow said. | NG | NG | PASS | PASS | op:mello->melo[C2_ledger_alt,conf=low,M EH L OW S]<br>az:mellow->melo[C2_ledger_alt,conf=low,M EH L OW S] | op=ACCEPT_M1; az=ACCEPT_M1 |
| 7 | std/slow6/t3 | Mello said. | Melos said.  | PASS | PASS | PASS | PASS | op:mello->melo[C2_ledger_alt,conf=low,M EH L OW S] | op=ACCEPT_M1; az=EXACT |
| 8 | std/slow6/t4 | Mello said, | Mellow said. | NG | NG | PASS | PASS | op:mello->melo[C2_ledger_alt,conf=low,M EH L OW S]<br>az:mellow->melo[C2_ledger_alt,conf=low,M EH L OW S] | op=ACCEPT_M1; az=ACCEPT_M1 |
| 9 | adv/raw/t1 | Mello said. | Mellow said. | NG | NG | PASS | PASS | op:mello->melo[C2_ledger_alt,conf=low,M EH L OW S]<br>az:mellow->melo[C2_ledger_alt,conf=low,M EH L OW S] | op=ACCEPT_M1; az=ACCEPT_M1 |
| 10 | adv/raw/t2 | Mello said. | Mello said. | NG | NG | PASS | PASS | op:mello->melo[C2_ledger_alt,conf=low,M EH L OW S]<br>az:mello->melo[C2_ledger_alt,conf=low,M EH L OW S] | op=ACCEPT_M1; az=ACCEPT_M1 |
| 11 | adv/raw/t3 | Mella said. | Mello said. | NG | NG | PASS | NG | az:mello->melo[C2_ledger_alt,conf=low,M EH L OW S] | op=DEFER_NOT_EXPLAINED(NOT_EXPLAINED); az=ACCEPT_M1 |
| 12 | adv/raw/t4 | Mello said. | Melos said. | PASS | PASS | PASS | PASS | op:mello->melo[C2_ledger_alt,conf=low,M EH L OW S] | op=ACCEPT_M1; az=EXACT |

集計: Before 4/12、F1のみ 4/12、本設計(OR) 12/12、本設計(両エンジン同一候補で同意) 11/12。
注: 12件の実際の発音は独立に確認されていない(同一12音声・既存ASR転写)。一致した候補は全て `C2_ledger_alt`(confidence=low、Tier3が自動生成した『音楽用語としての別読み』)であり、システムが書いた低信頼推測である。ユーザー承認(複数の合理的候補のいずれか1つで可)の下で評価対象にしているが、高信頼へ書き換えてはいない。

## 2. 674ペア(HR queue / er021 telemetry / er069 results_02)への適用

{"legacy_pass=False|multi_pass=False": 627, "legacy_pass=True|multi_pass=True": 30, "legacy_pass=False|multi_pass=True": 17, "new_m1_accept": 13, "harness_EXACT_artifact_not_m1": 4}
新規PASS=13件(全件):

| src | canonical | ASR | 置換 | 一致候補(出典) |
|---|---|---|---|---|
| human_review_queue | Melos said. | Mello said. | mello->melo (melos) | multi_candidate|C2_ledger_alt|conf=low|pron=M EH L OW S|ledger_key=ec716e185835dba3 |
| human_review_queue | Melos said. | Mellow said. | mellow->melo (melos) | multi_candidate|C2_ledger_alt|conf=low|pron=M EH L OW S|ledger_key=ec716e185835dba3 |
| er021_telemetry | The guards went still when Melos spoke. | The guards went still when Mello spoke. | mello->melo (melos) | multi_candidate|C2_ledger_alt|conf=low|pron=M EH L OW S|ledger_key=ec716e185835dba3 |
| er021_telemetry | At the wedding, Melos smiled whenever his sister smiled. He watched her join han | At the wedding, mellow smiled whenever his sister smiled. He watched her join ha | mellow->melo (melos) | multi_candidate|C2_ledger_alt|conf=low|pron=M EH L OW S|ledger_key=ec716e185835dba3 |
| er021_telemetry | Melos said. | Mello said | mello->melo (melos) | multi_candidate|C2_ledger_alt|conf=low|pron=M EH L OW S|ledger_key=ec716e185835dba3 |
| er069_results_02 | Melos said. | Mellow said.  | mellow->melo (melos) | multi_candidate|C2_ledger_alt|conf=low|pron=M EH L OW S|ledger_key=ec716e185835dba3 |
| er069_results_02 | Melos said. | Mello said, | mello->melo (melos) | multi_candidate|C2_ledger_alt|conf=low|pron=M EH L OW S|ledger_key=ec716e185835dba3 |
| er069_results_02 | Melos says. | Mello says | mello->melo (melos) | multi_candidate|C2_ledger_alt|conf=low|pron=M EH L OW S|ledger_key=ec716e185835dba3 |
| er069_results_02 | Melos says. | Mellow says. | mellow->melo (melos) | multi_candidate|C2_ledger_alt|conf=low|pron=M EH L OW S|ledger_key=ec716e185835dba3 |
| er069_results_02 | Melos says. | Mellow says, | mellow->melo (melos) | multi_candidate|C2_ledger_alt|conf=low|pron=M EH L OW S|ledger_key=ec716e185835dba3 |
| er069_results_02 | Melos says. | Mellow says.  | mellow->melo (melos) | multi_candidate|C2_ledger_alt|conf=low|pron=M EH L OW S|ledger_key=ec716e185835dba3 |
| er069_results_02 | Melos sighed. | Mello sighed. | mello->melo (melos) | multi_candidate|C2_ledger_alt|conf=low|pron=M EH L OW S|ledger_key=ec716e185835dba3 |
| er069_results_02 | Melos sighed. | Mellow sighed. | mellow->melo (melos) | multi_candidate|C2_ledger_alt|conf=low|pron=M EH L OW S|ledger_key=ec716e185835dba3 |

## 3. F1反例19件(COUNTER: 非PASS11/PASS維持6+参考2)

期待どおり: 19/19

## 4. 合成ケース

| 類型 | canonical | ASR | 期待 | 結果 | verdict | 備考 |
|---|---|---|---|---|---|---|
| T1 複数候補のうち1つ一致(Ledger別読み) | Melos said. | Mello said. | PASS | PASS | ACCEPT_M1 | 別読み /ˈmɛloʊs/ が一致(Ledger 低信頼・自動生成) |
| T1 複数候補のうち1つ一致(Ledger別読み) | Melos said. | Mellow said. | PASS | PASS | ACCEPT_M1 | 同上 |
| T1 複数候補のうち1つ一致(主発音) | Melos said. | Melos said. | PASS | PASS | EXACT | 綴り一致(EXACT) |
| T1 複数候補のうち1つ一致(CMU異読) | The tomatoes were red. | The tomatoes were red. | PASS | PASS | EXACT | EXACT |
| T1b 一般化(fake Ledger・別語) | Cleos said. | Clio said. | PASS | PASS | ACCEPT_M1 | fake Ledger /ˈkliːoʊs/(K L IY OW S)なら Clio(K L IY OW)と音素一致→受理。Ledger に根拠がある場合のみ [fake Ledger] |
| T1c 一般化の限界(fake Ledger・語幹がCMU未収録) | Zabelinas said. | Zabellina said. | NONPASS | NONPASS | DEFER_NOT_EXPLAINED | ASR 側が CMU 未収録語→音素を持たず不成立(誤PASSではなく取りこぼし側) [fake Ledger] |
| T2 どの候補も不一致 | Melos said. | Milo said. | NONPASS | NONPASS | DEFER_NOT_EXPLAINED | Milo=M IY L OW は候補に無い |
| T2 どの候補も不一致 | Melos said. | Mellon said. | NONPASS | NONPASS | DEFER_NOT_EXPLAINED |  |
| T2 どの候補も不一致 | Melos said. | Melas said. | NONPASS | NONPASS | DEFER_NOT_EXPLAINED | Melas は CMU 未収録 |
| T3 綴り近いが発音異なる(候補なし) | Cleos said. | Clio said. | NONPASS | NONPASS | HR_CANDIDATE_EXPLAINED | Cleos は Ledger 無し→候補0→C3 不採用で非PASS(Trial fallback なら PASS だった) |
| T3 綴り近いが発音異なる(fake Ledger) | Cleos said. | Clio said. | NONPASS | NONPASS | HR_CANDIDATE_EXPLAINED | fake Ledger /ˈkliːəs/(K L IY AH S): Clio=K L IY OW と不一致 [fake Ledger] |
| T3 綴り近いが発音異なる(既存Pattern A・M1非関与) | Brontes said. | Bronte said. | PASS | PASS | PROD_PASS_UNCHANGED | 既存 Production Pattern A(綴り基準、OPEN-330)が PROD_PASS_UNCHANGED で受理。M1/本設計とは無関係の既存挙動(参考) [fake Ledger] |
| T4 ASRが別の実在語へ誤転写 | Melos said. | Mellow said. | PASS(論点) | PASS | ACCEPT_M1 | 実在語 mellow へ誤転写でも、候補 /ˈmɛloʊs/ と音素一致なら受理される。真の発音は ASR だけでは判別不能=Ledger 候補の質に依存(要論点) |
| T4 ASRが別の実在語へ誤転写 | Melos said. | Sad. | NONPASS | NONPASS | DEFER_NOT_EXPLAINED |  |
| T5 連結発音 vs 語句欠落 | The studies suggest cats today. | The study suggests cats today. | PASS | PASS | PROD_PASS_UNCHANGED | 正常な連結発音(F1維持) |
| T5 連結発音 vs 語句欠落 | He planned a US sea blockade. | He planned a U S blockade. | NONPASS | NONPASS | DEFER_NOT_EXPLAINED | sea 欠落(F1是正の維持) |
| T5 連結発音 vs 語句欠落 | Melos said he left. | Mello said. | NONPASS | NONPASS | DEFER_NOT_EXPLAINED | Melos 以外の語句欠落 |
| T6 後半に別差分 | Melos said cats sleep. | Mello said dogs sleep. | NONPASS | NONPASS | DEFER_NOT_EXPLAINED | M1成立でも dogs/cats でF1非PASS |
| T6 後半に別差分 | Melos said he did not go. | Mello said he did go. | NONPASS | NONPASS | DEFER_PROTECTED_FAIL | 否定不一致 |
| T6 後半に別差分 | Melos said 5 cats sleep. | Mello said 6 cats sleep. | NONPASS | NONPASS | DEFER_PROTECTED_FAIL | 数値不一致 |
| T6 後半に別差分 | Melos said cats slept. | Mello said cats sleep. | NONPASS | NONPASS | DEFER_NOT_EXPLAINED | 時制不一致 |
| T7 M1成立+後半同一 | Melos said cats sleep. | Mello said cats sleep. | PASS | PASS | ACCEPT_M1 | M1成立+残差0 |
| T8 同一語が文中に2回 | Melos said Melos left. | Mello said Mellow left. | PASS | PASS | ACCEPT_M1 | 両出現とも候補一致 |
| T8 2回のうち片方が別語 | Melos said Melos left. | Mello said Milo left. | NONPASS | NONPASS | DEFER_NOT_EXPLAINED | 片方不一致 |

## 5. Ledger規模(候補が無制限にならない根拠)

{"entries": 37, "confidence": {"medium": 12, "high": 11, "low": 14}, "usable_oov_single_token_words": 11, "max_candidates_per_word": 4}

候補が使える単一語(CMU未収録・IPA変換可)の一覧: Malmö(1候補/high), Triangeln(2候補/medium), MTA(1候補/high), zabelina(1候補/low), meink(2候補/low), toteme(2候補/low), canele(1候補/low), oimo(1候補/low), familymart(1候補/medium), altuzarra(1候補/low), melos(4候補/low)

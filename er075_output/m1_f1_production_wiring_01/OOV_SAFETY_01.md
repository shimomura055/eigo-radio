# OOV_SAFETY_01 辞書未収録語(OOV)の安全な扱い: 承認済みM1との整合確認

管理ID: ASR-PHONETIC-EQUIVALENCE-M1-F1-PRODUCTION-WIRING-01 委任_02 / 費用JPY0 / 既存転写のread-only再判定(API 0)
script: `er075_m1_f1_production_wiring_01_oov_options.py` / 結果: `oov_options_12take_01.json`(12件×2エンジン×6方式、ほか汎化probe15件)

## 結論(最重要)
**STOP条件「辞書未収録語の安全な扱いが確定できない」に該当する(`USER_DECISION_REQUIRED`)。**
- ユーザー承認の必須条件3(綴り類似だけで無条件PASSしない)・5(発音辞書未収録語は信頼できる発音情報の利用可能性を確認)・6(発音を確証できない語を無制限な綴り近似で救済しない)と、重要注記(辞書未収録語を任意の綴り近似で許容する新安全基準は未承認)に照らし、**既存TrialのOOV fallbackはそのままProductionへ移せない**。
- 承認済みの範囲で実装できる選択肢((i)(ii-a)(ii-b))では、`Melos said` 12件のPASSは **4/12で現行と同一**。「改訂M1 12/12」はOOV fallback((iii))またはlow信頼別読み使用((ii-c))に**のみ**依存する。
- よって承認済みM1の**主目的(Melos 12件の4/12→12/12)は、新たなユーザー判断なしには実現できない**。未承認の代替仕様は独自実装しない。設計の他部分(CMU収録語のM1・F1)は継続可能。

## 事実
1. CMUに `melos` は無い(OOV)。`mello`/`mellow`/`melo` は全て `M EH L OW`(CMU)。
2. Pronunciation Ledger(`er006_output/pronunciation_ledger_01/ledger.json`)の `melos` は2エントリ: (a) `ja_reading_katakana` メロス(`expected_pronunciation_ipa` 空=英語発音情報なし)、(b) `cascade_unresolved_entity` 英語: 主発音 `/ˈmiː.lɑːs/`(米国暫定、= `M IY L AA S`)、別読み `/ˈmɛloʊs/`(音楽用語の別読み、= `M EH L OW S`)等。**confidence=low**、`ambiguity_note` は「本人の音声確認なし・辞書ベースの推定・medium以下」と明記。IPA→ARPAbet変換は未導入(本scriptが検証用に簡易変換)。
3. 主発音 `M IY L AA S` から S を除いても `M IY L AA` で、ASRの `Mello/Mellow`(`M EH L OW`)とは不一致 → **Ledgerの主発音を基準にするとMello/Mellowは『別の発音』であり、許容できない**。一致するのは low信頼の別読み `/ˈmɛloʊs/` のみ。
4. 現行Pattern A(`Melos`→`Melo`)も**綴り基準**(canonical語から末尾 `s/es` を除いた綴りとASR語が完全一致)である(OPEN-330でスコープ疑義が既に起票済み)。
5. 12件のM1 PASSは全て Trial の `oov_spelling_fallback`(canonical語がCMUに無い場合、語幹の綴り `melo` 等から期待綴りを推定し、CMU同音綴り `mello/mellow` を許容)経由。

## 選択肢別の12件再判定(OpenAI/Azure の少なくとも1系統が受理=現行と同じ集計)
| 選択肢 | 内容 | 12件PASS | 備考 |
|---|---|---|---|
| (0) 現行Production | Pattern A(綴り)+同音語+Tier3 | **4/12** | 4/12が再現(Std減速前t3,t4・減速後t3・Adv t4) |
| (i) OOV fallback非移行 | M1はCMU収録語のみ | **4/12** | OOV canonical(Melos)には適用されず現行と同じ |
| (ii-a) Ledger高信頼発音のみ音素基準 | confidence=highのIPAのみ | **4/12** | Melosの英語エントリはlowで該当なし |
| (ii-b) Ledger主発音のみ(信頼度不問) | `/ˈmiː.lɑːs/` のみ | **4/12** | Mello/Mellowは主発音と不一致 |
| (ii-c) Ledger別読み含む(感度分析) | low信頼の `/ˈmɛloʊs/` も使用 | 12/12 | **推奨外**: 同じLedger内の主発音(`M IY L AA S`)と矛盾する low 別読みを根拠にしており、「確証」ではない |
| (iii) Trial同等OOV fallback | 語幹綴りから期待綴りを推定 | 12/12 | **新基準の承認申請が必要**(下記) |

### 12件の内訳(OR判定)
| # | 条件 | take | OpenAI | Azure | (0) | (i) | (ii-a/b) | (ii-c) | (iii) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Std減速前 | 1 | Mello said. | Mellow said. | NG | NG | NG | PASS | PASS |
| 2 | Std減速前 | 2 | Mello said. | Mellow said. | NG | NG | NG | PASS | PASS |
| 3 | Std減速前 | 3 | Mello said. | Melos said. | PASS | PASS | PASS | PASS | PASS |
| 4 | Std減速前 | 4 | Mello said, | Melo said. | PASS | PASS | PASS | PASS | PASS |
| 5 | Std減速後 | 1 | Mellow said. | Mellow said. | NG | NG | NG | PASS | PASS |
| 6 | Std減速後 | 2 | Mello said. | Mellow said. | NG | NG | NG | PASS | PASS |
| 7 | Std減速後 | 3 | Mello said. | Melos said. | PASS | PASS | PASS | PASS | PASS |
| 8 | Std減速後 | 4 | Mello said, | Mellow said. | NG | NG | NG | PASS | PASS |
| 9 | Adv | 1 | Mello said. | Mellow said. | NG | NG | NG | PASS | PASS |
| 10 | Adv | 2 | Mello said. | Mello said. | NG | NG | NG | PASS | PASS |
| 11 | Adv | 3 | Mella said. | Mello said. | NG | NG | NG | PASS | PASS |
| 12 | Adv | 4 | Mello said. | Melos said. | PASS | PASS | PASS | PASS | PASS |

注: 12件の正否(実際に何と発音されているか)は独立に確認されていない(同一12音声・既存ASR転写に基づく。承認時の注記を維持)。#11 は OpenAI=`Mella`(別の語)だがAzure=`Mello` のOR判定。

## 現行Pattern A(綴り基準)と(iii)の違い
- Pattern A: ASR語 == canonical語から `s/es` を除いた**綴りが完全一致**(`Melos`→`Melo`)。ASRが返した綴りが期待綴りとそのまま一致することを要求する。
- (iii): ASR語が期待綴り(`melo`)と**別の綴り**(`mello`/`mellow`)でも、**CMUで `melo` と同じ音素列**であれば期待綴りとみなす。つまり「canonical語(OOV)の語幹の発音 = その語幹綴りをCMU同様に読んだもの」という**未確認の仮定**を新たに置く。
- 追加の危険(probe結果): `Cleos said.`→`Clio said.` を(iii)のみPASSにする(0/i/ii は NG)。語幹 `cleo` と `clio` がCMUで同一音素のため。Cleosの実際の読みは確認されていない。`Melos said.`→`Mellon/Melas/Milo/Sad` は全方式でNG(良好)。
- 実害の構図: Ledgerの主発音(`MEE-lahs`)が正しいなら、TTSが `Mello/Mellow`(EH-L-OW)と読んだ音声は**発音誤り**であり、(iii)はそれを機械的に通す。逆にTTSが `MEE-lahs` と読んだ音声をASRが `Mellow` と書くことは考えにくく、ASRの綴りは発音の証拠として扱える(が、独立確認なし)。いずれにせよ(iii)は「発音誤りを区別できない」点が OPEN-318 と同じ未解決として残る。

## 推奨とユーザー判断
- **既定(承認済み範囲のみ)**: (i)。CMU収録語のM1(例 `wait/weight` 系の既存同音語経路との整合、`studies/study` + `Pattern A` の同音綴り)とF1是正を進め、OOVは現行どおり(`Melos said` は4/12のまま)。
- **USER_DECISION_REQUIRED候補(判断はユーザー、Fableが提示)**:
  - A: (iii) を「OOV語の綴り推定基準」として新たに承認する(承認文に: 誤許容の例=`Cleos→Clio`、適用上限、audit trailでの区別、HR降格の要否を明記)。
  - B: 作品単位で英語読みを1回試聴確定(OPEN-318 C-a)し、確定発音をLedger `confidence=high` で登録 → (ii-a) が使える形にする。この場合Melosの12件が通る条件は、確定発音が `mello` 系(`M EH L OW S`)であること。
  - C: (i)で止め、`Melos said` 型の短いclipは別手段(OPEN-318 C案)で扱う。
- いずれも**ユーザーの判断なしに追加Trial・仕様変更は進めない**。

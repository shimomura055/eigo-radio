# SSOT_DRAFT_TEXT_01 委任_03(SSOT担当)向け追記文案(本委任はSSOT編集権なし。文案のみ)

Status記載の注意: M1/F1とも `APPROVED_FOR_PRODUCTION`(2026-10-13ユーザー正式決定)。`PRODUCTION_WIRED` ではない(配線・runtime evidence・OOV判断が未完)。

## CURRENT_SPEC(Connected Speech/ASR検証の節へ)
「M1(連結発音におけるASR表記揺れの発音同等性判定、`APPROVED_FOR_PRODUCTION`、2026-10-13、未配線)承認範囲: 原稿`Melos said`に対しASRが`Mello`/`Mellow`と転写した場合、`Melo`と**発音上同等であることを確認できれば**既存Pattern Aと同じ連結発音ルールで判定する。条件: Melos専用hardcode/allow-listにしない、固有名詞・一般語共通、綴り類似のみで無条件PASSしない、Pattern A/B/Cの許容範囲を未承認拡張しない、辞書未収録語は信頼できる発音情報(Pronunciation Ledger等)の利用可能性を確認、発音確証のない語は無制限な綴り近似で救済しない、判定理由・元ASR・正規化内容を追跡可能にする。**辞書未収録語を綴り近似で許容する基準は未承認**(`USER_DECISION_REQUIRED`、OOV_SAFETY_01.md)。実測(同一12音声・既存ASR転写、12本の正否の独立確認ではない): 従来4/12、改訂M1(Trial OOV fallback使用)12/12。承認済み範囲のみ(OOV fallback非移行)では4/12。
F1是正(`APPROVED_FOR_PRODUCTION`、未配線): 連結発音Validator(Pattern A/B/C)は最初の食い違いだけでなく**全差分を確認**し、連結発音で説明できる差分のみ許容、他は既存の通常Validatorで判定する(内容語・否定・数値・時制・欠落・追加・別固有名詞を見逃さない)。M1の正規化後も同じ全文検証を適用。」

## DECISION_LOG(2026-10-13)
「ユーザー正式決定: M1とF1是正を`APPROVED_FOR_PRODUCTION`。到達目標は`PRODUCTION_WIRED`、未確認項目があれば完了扱いにしない。非対象: R1/V2/個別allow-list/既存ASR品質Gate緩和/無関係Prompt変更。Family Z再生成・音声化はPreview正式確定までSTOP継続。辞書未収録語の新安全基準は未承認(承認済み連結発音原則と整合しない場合は未承認の代替を実装せずSTOPして報告)。」
追記(委任_02結果): 「OOV選択肢別の12件再判定: 現行4/12、(i)4/12、(ii-a)4/12、(ii-b)4/12、(ii-c, low別読み使用)12/12、(iii, Trial OOV fallback)12/12。(iii)は`Cleos→Clio`も受理(語幹綴りに基づく未確認仮定)。F1影響集計: 実データ674ペアでPASS→非PASS0・非PASS→PASS0、`US sea blockade` 4窓が現行PASS→非PASS(要聴取確認)。」

## OPEN_ITEMS 更新案
- OPEN-339(ASR-PHONETIC-EQUIVALENCE-GENERALIZED-DECISION-IMPLEMENTATION-AND-SAFETY-01): 「M1は`APPROVED_FOR_PRODUCTION`(OOV除く)。Production配線設計=`er075_output/m1_f1_production_wiring_01/M1_WIRING_DESIGN_01.md`(WIRING_DESIGN_DRAFT、Opus条件A/C待ち)。OOV扱いが`USER_DECISION_REQUIRED`(UDR-1: A=(iii)新基準承認 / B=作品単位の英語読み確定でLedger高信頼化 / C=(i)で止める)。承認済み範囲のみではMelos 12件は4/12。」
- OPEN-340(PATTERN-ABC-FIRST-DIFF-ONLY-JUDGMENT-SAFETY-GAP-01): 「F1是正は`APPROVED_FOR_PRODUCTION`。最小変更設計=`F1_FIX_DESIGN_01.md`(`classify_connected_speech` 1関数、全差分列挙+Pattern個別判定+通常Validator委任)。影響集計=`F1_IMPACT_CENSUS_01.md`(緩和0・実データPASS→非PASS 0)。残: Eq Layerの同種不備の扱い(UDR-2)、`US sea blockade` 4窓の聴取確認(UDR-3)。」
- OPEN-341/342: 内容は`OPEN_ITEMS.md`本文を確認のうえ、M1/F1配線の進捗(設計完了・実装未了)と相互参照のみ追記(委任_02は本文未読。要整合確認)。
- OPEN-318/327/328/330: 相互参照(OOV・Pattern A綴り基準・観測性=layer_invoked)。

## USER_DECISION_REGISTER 更新案
UDR-M1F1-1 OOV語の扱い(A/B/C)、UDR-M1F1-2 Eq Layer同種F1不備の是正範囲、UDR-M1F1-3 `US sea blockade` 4件の扱い、UDR-M1F1-4 `PRODUCTION_WIRED`宣言はUDR-1決着まで保留。

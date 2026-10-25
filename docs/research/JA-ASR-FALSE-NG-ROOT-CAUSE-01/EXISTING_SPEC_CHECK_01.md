# EXISTING_SPEC_CHECK_01(既存仕様・過去対策・OPEN一覧・X/Z差分。照合のみ、全文読込なし=Grep)

## 1. 日本語ASRの現行仕様(Production)
| 項目 | 現行仕様(出典) |
|---|---|
| Primary/Secondary | Primary=OpenAI gpt-4o-mini-transcribe(`er006_asr_provider_routing_01.py:31`)、Secondary=Azure Speech STT ja-JP。UDR #136で入替・追加ASR導入は不採用(`CURRENT_SPEC.md` L2850周辺「Primary/Secondary入替なし」)。KP英語phraseのみ3-ASR多数決(KP3V) |
| PASS条件 | Primary PASSなら最終ANDゲート(値DIFF/否定差)後PASS。Primary NGは原則Secondary 1回(SecondaryCacheで同一wav1回)。Secondary受理=`EXACT_MATCH`/`NORMALIZED_MATCH`のみ(+2エンジン確認の`ORTHOGRAPHIC_VARIANT_CONFIRMED`)(`CURRENT_SPEC.md` L2865、`er007_ja_secondary_asr_01.py:83`) |
| P1(保護差) | Primary NGかつ値DIFF/否定差=`NG_PROTECTED`・**Secondary不呼出**(`er078_asr_unified_judge_01.py:566-570`、`CURRENT_SPEC.md` L2852)。KP英語voteのみP1をskip(同:566の`vote is None`条件) |
| Primary側の日本語救済 | `classify_ja_asr_match`(正規化→opcode差の読み一致=PHONETIC_MATCH→全文読み一致→Variant Layer B/C/D-1/E→Reading Resolver[LLM])(`er007_ja_asr_validator_01.py:333-505`, `er011_ja_asr_variant_layer_01.py:289-372`)。+adapterの値等価層`_numeric_value_equivalence`(値ガードEQUAL∧残り文字が`normalize_ja`後に**完全一致**)(`er007_ja_secondary_asr_01.py:511-530`) |
| 数値保護 | 値ガード5値 NO_VALUES/EQUAL/DIFF/AMBIGUOUS/UNKNOWN(`er078_asr_value_guard_01.py`、`CURRENT_SPEC.md`「値ガード5値」)。「表記ではなく値と単位で比較」(三人=3人、三十人=30人、100円=百円は許容。値違いは不許容) |
| 再試行/fallback/HR | 通算TTS3回(標準2+minimal fallback1)、3NG→STOPPED→HR Lock(JAはLocal Rewrite無し)(`CURRENT_SPEC.md` L1843、L2862) |
| 英語の同音救済 | `er109`(ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01、X/Z限定、ユーザー承認2026-10-23)。**英語専用**(`lang=="en"`、`DESIGN_PROPOSAL_01.md:93`)。日本語は対象外 |
| 中核数値v4/J2 | `er116_fx_core_numeric_retention_01.py`は**Writer/R1R2段の数値保持**(Family X Std/Adv)で、音声ASR判定とは別工程(OPEN-507)。今回の月題『8,900本超』は非E中核でタイトルに使われた数値(`RESULT_PACKET_FXNR7.md`)。ASR判定側の数値保護(値ガード)とは独立で矛盾なし |

## 2. 仕様と実装の不一致(11-8: 不具合候補)
| ID | 内容 | 根拠 |
|---|---|---|
| D-1 | Secondary受理は「値等価正規化後の一致を含む」(`CURRENT_SPEC.md` L2865)のに、実装は値等価層を通さない | `er007_ja_secondary_asr_01.py:643-650`、mock再現`mock_secondary_gap_01.out.txt` |
| D-2 | 「読み一致=PHONETIC_MATCHでPASS」と「値・単位比較」を両立する設計なのに、(a)助詞は→わ、(b)桁区切り`,`、(c)値atomを含む文の読み比較、が未対応 | `er011_ja_asr_variant_layer_01.py:96-100`、`er007_ja_asr_validator_01.py:55-59`、再現`trace_moon_classify_01.out.txt` |
| 注 | A7(登録読み辞書不一致=Secondary事前除外)、A4(C2同形異音)は2026-10-11安全条件=維持。本件はいずれにも該当しない(moon題はentity_like/辞書読み/同形異音に非該当) | `CURRENT_SPEC.md` L2856 |

## 3. 過去の同種OPEN・対策(Grep: ja_asr/日本語ASR/数値保護/同音)
| OPEN | 結論 | 本件との関係 |
|---|---|---|
| OPEN-61/62 | JA Validator全文化+Cascade、retry path修正 | 現行判定の基盤 |
| OPEN-73 | 二つ→2つ(閉じた助数詞リストの漢数字→算用数字) | 本件の`八千九百本`は`本`が閉リスト外のため効かない(R1/2の一因) |
| OPEN-145 | Variant Layer(形態素読み)Production採用 | 助詞`kana`優先(`ハ`)が欠陥(R1) |
| OPEN-199 | 句読点・引用符正規化 | 同系(`,`未対応=R3) |
| OPEN-258 | SCG(Secondary Confirm Gate)採用 | Secondary受理=EXACT/NORMALIZEDのみ |
| OPEN-287/319 | 漢数字・表記差でS1が誤発火(三人=3人、三日間) | **EXPERIMENTAL止まり**: `er066`(署名一致Stage1/1'/2)はTrial、**Production未配線・USER_DECISION_REQUIRED継続**。AUWの`_numeric_value_equivalence`がPrimaryのみ部分的に吸収(残りは完全一致必須) |
| OPEN-296 | JA Style候補のNGは誤認か読み違いか試聴待ち | 判定の真偽を試聴で確かめる運用の前例 |
| OPEN-333/334 | Candidate E過許容(三日間→三日目PASS)、`〜`/`、`除去による数字結合の誤PASS | **誤PASS側の既知リスク**。本設計は“厳格な発音一致”に限定し、E・Resolverには依存しない |
| OPEN-371(U4)等 | HR Lock/技術STOP | 変更なし |
| 英語: er109/KP3V/ASR-TIME-NUMERAL | 英語の同音・数詞は音素/値で救済済み | JA側は同等の“音(かな)”基準が部分的にしか無い |

## 4. Family X / Z の差分
- JA音声の判定は**X/Z共通の同一経路**(`repro01.generate_narration_snippet_verified_strict`→`ja_secondary.evaluate_attempt_ja_with_cascade`)。Zはclip計画(`er063_family_z_audio_01.py:545-564`)が違うだけで判定は同じ。**Family固有の例外は不要**(Y/A/B/Cは委任範囲外=変更しない)。
- 開発対象はX・Z(将来Y)のみ。Productionの`er007_*`/`er011_*`/`er078_*`は共有ファイルで、A/B/Cにも波及するため、配線時は`er109_xz_scope_01`型のrun-scope限定(X/Z)にするか、A/B/Cへの波及を許容するかをFableが決める(Phase 4)。

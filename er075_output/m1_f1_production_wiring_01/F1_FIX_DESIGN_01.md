# F1_FIX_DESIGN_01 F1是正(連結発音Validatorの『最初の食い違いだけでPASS』)最小変更設計

Status: `WIRING_DESIGN_DRAFT`(Opus条件A/C待ち)。Production code無変更。プロトタイプ=`er075_m1_f1_production_wiring_01_census.py::f1_classify`(プロセス内差替えのみ、ファイル非変更)。

## 1. 原因(確認済み)
- `er011_b1_connected_speech_validator_01.py::word_diff` が**最初の食い違い語だけ**を返し、`classify_connected_speech` がそれがPattern A/B/Cで説明できればACCEPT/RESEGMENTATIONを返す。後続の食い違い・語数差は見ない。
- 呼出: `er006_preprod_hardening_01_validation.py::classify_asr_match` L1076(`non_entity_diffs` がある=内容語差ありのとき)と L1119(最終fallback)。**内容語差(`cats→dogs`)があるからこそ L1076 に入り、先頭の `studies→study` だけで救済してしまう**のが本件の構造。
- 実測(本委任): `The studies suggest cats today.` / `The study suggests dogs today.` → 現行 `CONNECTED_SPEECH_ACCEPT`(PASS)。Pattern B(`opened…closed→closes/people`)・Pattern C(`survey…dogs`)でも同様に再現(F1_IMPACT_CENSUS_01.md 反例表)。KP検証も同関数を共有するため同様。

## 2. 最小変更設計(新しい許容ルールは作らない)
`classify_connected_speech` の判定を「最初の1か所」から「**全差分**」へ:
1. canonicalとASRのトークン列(既存 `tokenize`、小文字化)を `difflib.SequenceMatcher` で比較し、**全ての差分ブロック**を列挙する。
2. 各差分(1:1置換ブロックは位置ごとに)を、**既存のPattern A/B/C判定をそのまま**(canonical側の後続語をnext_wordとして)個別に適用し、説明できる差分を確定する。
3. 説明できない差分は、**既存の通常Validator(`protected_check`)に委ねる**: その差分ブロックに内容語差・数字不一致・否定不一致が無い(機能語のみ/規則的な単複ゆれ=既存が元々吸収する差)なら残差としない。内容語の置換・追加・欠落、数値、否定、時制、別の固有名詞が残るなら**残差あり**。
4. **残差が1つでもあれば `UNCLASSIFIED_FALLS_THROUGH_TO_EXISTING` を返す**(=既存の通常判定へ。`TRUE_CONTENT_MISMATCH`/Eq Layer fallthrough等、既存のretry/fallback/HR上限をそのまま通る)。残差が無く全差分が説明できる場合のみ、ACCEPT(RESEGMENTATION含む場合はRESEGMENTATION)。
5. M1の正規化後の文にも同じ関数を適用(M1は置換トークンのみを許容し、残差があれば不受理: `m1_try` の `_f1_guard_ok` と同趣旨を共有関数に一本化)。
- 変更箇所: `classify_connected_speech`(+必要なら小さな補助関数)の1関数のみ。呼出側(L1076/L1119)・Pattern A/B/C本体・閾値・retry上限は無変更。
- 戻り値は後方互換(既存キー `diff`/`rule`/`expected_phoneme_boundary`/`new_judgment`/`false_accept_risk` を維持、`f1_all_diffs`/`f1_residual` を追加)。

## 3. 新たな誤PASSを生まないことの論拠
- 判定は**厳しくなる方向のみ**: 以前PASSだったもののうち「全差分が説明できる」ものだけPASSを維持。以前NG/UNCERTAINのものは変わらない(census: `nonpass_to_pass=0`)。
- 通常Validator(`protected_check`)の吸収対象(機能語・規則的な単複)は従来どおり残差にならないため、`The studies suggest cats today.` ↔ `The study suggest/suggests cats today.` のような**正常な連結発音は不必要にNGにならない**(反例表で確認)。

## 4. 点検表(同種不備の有無)
| 対象 | 同種不備(最初の食い違いのみ) | 根拠 | 扱い |
|---|---|---|---|
| Pattern A(`classify_connected_speech`) | **あり** | 実測(反例表) | 本是正の対象 |
| Pattern B | **あり**(同じ `word_diff` を共有) | 実測 | 本是正の対象(同一関数) |
| Pattern C | **あり**(同上、`PASS_WITH_WARNING`でも残差を見逃す) | 実測 | 本是正の対象 |
| L1119最終fallback | 同じ関数のため是正で同時に解消 | コード | 呼出側変更不要 |
| `_is_benign_plural_pair`(protected_check) | 不備なし(ペアごとの単複判定。位置は全ブロックを走査) | コード | 変更なし。ただしF1新設計の「通常Validatorに委ねる」の前提として利用 |
| Equivalence Layer(`classify_connected_speech_equivalence`) | **あり得る**: `existing["diff"]`(最初の食い違い)のみでカテゴリ判定+corroborationも同一index位置のみ(`_word_at_diff_matches_canonical`)。UNCLASSIFIED経由の場合、その位置以外の食い違いは見ない | コード読み(未実行。`protected_check`通過は前提だが内容語差が`non_entity_diffs`に入った場合は通過しない可能性があり、実際の発火経路は要実測) | **要判断**: F1是正の範囲に含めるか。今回の最小変更は上記1関数のみとし、Eq Layerは別承認(OPEN-122)のため、同じ「全差分ガード」の追加をUSER_DECISION_REQUIRED候補として提示 |
| er021(semantic equivalence) | 点検未実施の範囲(別機構。`classify_asr_match`の下流ではない) | — | 別Open Itemで点検を提案 |
| Key Phrase検証 | 同関数共有のため是正が自動適用。KP実データは今回のcensusに含まれず | — | EVIDENCE_PLANでKP実データの追加集計を提案(要ユーザー判断なし、既存データのread-only) |

## 5. 受け入れ基準との対応
| 受入条件 | 結果 |
|---|---|
| 誤PASS解消 | 反例11件が非PASS化(F1_IMPACT_CENSUS_01.md) |
| 正常な連結発音をNGにしない | 反例表のpass期待6件(pass?含む)は全てPASS維持。実データ674件: PASS→非PASS 0件。真値付きデータでは**4件**(`US sea blockade` 窓のASR `U S …`)がPASS→非PASS(下記「誤NG候補」) |
| 既存成果物のPASS→非PASS事前調査 | F1_IMPACT_CENSUS_01.md |
| 他Pattern/関連Validatorの点検 | 上表 |
| 新たな誤PASSを生む緩和は禁止 | `nonpass_to_pass=0` |

## 6. 誤NG候補(要判断)
`a US sea blockade` に対するASR `a U S blockade` / `a U S se blockade` / `a U S C blockade` / `planned U S blockade`(er021 telemetry、Family X実ASR)が、現行ではPattern A(`US→U` + 次語 `sea`)で偶然PASSしていた。F1後は**非PASS**(`sea` の欠落、または `S`/`C` の余り)。これはF1の意図どおりの是正(`U S` + `sea` 欠落/`C` は連結発音では説明されない)だが、元データの `truth=normal`(窓の目視未実施の仮ラベル)と食い違う。音声は未聴取のため「真の誤NG」とは断定しない。アクロニム(`US`→`U S`)表記の扱いを許容するには新規ルールが必要=承認範囲外。

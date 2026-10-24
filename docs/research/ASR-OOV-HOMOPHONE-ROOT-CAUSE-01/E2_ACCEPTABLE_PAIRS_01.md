# E2_ACCEPTABLE_PAIRS_01 (OF-OOV-03) E2が受理しうる『Ledger読み x CMU語』全件

生成: `e2_acceptable_pairs_01.py`(API 0)。Ledger=er006_output/pronunciation_ledger_01/ledger.json(43 entry)。条件=ledger_disabled無/sources非空/canonical_spelling==surface/surface CMU未収録/medium以上/3音素以上。
CMU語の代表発音(rank0)と完全一致する語がある候補読み: **1件**/対象候補読み7件。除外内訳: {'confidence_low': 7, 'surface_in_cmu(C2対象外)': 9, 'multi_word': 6, 'ledger_disabled': 3, 'canonical_spelling_differs': 1, 'ja_reading_katakana': 10}

| ledger_key | surface | entity_type | conf | evidence_tier | 読みの別 | IPA | 音素 | 一致するCMU語 |
|---|---|---|---|---|---|---|---|---|
| bf66057e0e39f011 | Malmö | place | high | None | expected | ˈmæl.məʊ | M AE L M OW | (なし=E2が発火しない) |
| 96e00801024222ed | Triangeln | place | medium | None | alt | ˈtri.ɑŋ.ɡələn | T R IY AA NG G AH L AH N | (なし=E2が発火しない) |
| 96e00801024222ed | Triangeln | place | medium | None | alt | ˈtri.æŋ.ɡələn | T R IY AE NG G AH L AH N | (なし=E2が発火しない) |
| b087a8c8abd5de49 | MTA | abbreviation | high | None | expected | ˌɛm tiː ˈeɪ | EH M T IY EY | (なし=E2が発火しない) |
| 69a376df8d6b5445 | familymart | cascade_unresolved_entity | medium | None | expected | ˈfæməli mɑːrt | F AE M AH L IY M AA R T | (なし=E2が発火しない) |
| 4e8e014185b79c53 | gacha | cascade_unresolved_entity | medium | NAME_IN_CITED_PAGE | expected | ˈɡɑː.tʃə | G AA CH AH | gotcha |
| 4e8e014185b79c53 | gacha | cascade_unresolved_entity | medium | NAME_IN_CITED_PAGE | expected | ˈɡætʃ.ə | G AE CH AH | (なし=E2が発火しない) |

## 再生成手順(Ledger増加時)
`.venv\Scripts\python.exe docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/e2_acceptable_pairs_01.py`(Ledger path引数で別snapshotも可)。Production化後は、Ledger登録のたびに自動再生成するか、新規entryの一致CMU語を登録時に監査ログへ残すことを推奨。

## Fable精査用の所見(委任_02、現Ledger 43 entry時点)
- **受理しうる組合せは gacha(米 /ɡɑː.tʃə/) × gotcha の1組のみ**。gacha(英 /ɡætʃ.ə/ [G AE CH AH])にはCMU側の一致語なし=UK読みでは発火しない(US読みのみ)。
- 他の候補読み5件(Malmö、Triangeln×2、MTA、familymart)はCMUに完全一致する代表発音の語が無く、E2は発火しない。
- 除外内訳: confidence low 7(Melos 等の low entry)、surface CMU収録9(C2対象外)、複数語6、ledger_disabled 3、canonical_spelling差異1、ja_reading_katakana 10。
- 誤受理リスクの所感: gotcha は一般語で『gacha以外の文脈で gotcha が正しく読まれた』場合も、正準が gacha の位置に限り・他に差がなく・独立エンジン非矛盾を要求するため、受理されるのは正準側がgachaと決まっている箇所に限る。音素が同一の別語は音では区別不能(定義上同等)。UK読みで発音された gatcha は ASR が CMU外綴りになり不受理(Trial負例)。
- 参考(この一覧の外、trial02のTrial用Ledgerに登録した8語): E2が発火しうる組合せは lift/thick/cool/school/fat/love/fire/grinder。これらはTrial用Ledger(共有Ledgerには未登録)のため一覧には含めない。

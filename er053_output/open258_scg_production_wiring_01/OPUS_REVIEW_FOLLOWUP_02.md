# OPUS_REVIEW_FOLLOWUP_02 (委任_03: C2・推奨4の実装、2026-10-11)

ユーザー正式採用(2026-10-11): C2 同形異音語ガード=`APPROVED_FOR_PRODUCTION`、推奨4 否定マーカー追加=`APPROVED_FOR_PRODUCTION`。branch `feature/scg-ja-secondary-01`、変更は`er007_ja_secondary_asr_01.py`のSCG内部(`_scg_exclusion_reason`と補助関数)のみ。共通ASR判定(`protected_check_ja`/`safety._has_negation_ja`/`classify_ja_asr_match`)・呼出元4か所・retry/fallback/regeneration機構は無変更。

## Opus指摘対応一覧
| 項目 | 状況 | 実装/証跡 |
|---|---|---|
| 必須1 C1(固有名詞/entity_like除外) | 対応済(委任_02) | `_scg_exclusion_reason` |
| 必須2 Azure Error cancel厳密化 | 対応済(委任_02) | `_azure_stt_strict` |
| 必須3 本番条件Phase 0回帰 | 対応済(委任_02)、本委任で期待値更新 | `ProductionConditionRegression` |
| 推奨4 否定マーカー | **対応済(委任_03)** | `_scg_negation_ranges`/`_scg_negation_marker_diff` |
| 推奨5 Secondary判定でResolver不呼出 | 対応済(委任_02) | `allow_reading_resolver` |
| 推奨6 length_ok=FalseでSCG不実行 | 対応済(委任_02) | 呼出元4か所 |
| 推奨7 master store併記 | 対応済(委任_02) | manifest追加キー |
| 推奨8 NORMALIZEDに既存承認済み正規化を含む旨の明記 | 対応済(委任_02) | `OPUS_REVIEW_FOLLOWUP_01.md` |
| C2 同形異音語ガード | **対応済(委任_03)** | `_scg_heterophone_candidate` |

## C2 同形異音語ガード
- 判定: SCG実行直前(`_scg_exclusion_reason`、C1判定の後)に、Primary側のcontent_diffs各差分について `reading_is_candidate(原稿側漢字span, hira_reading(Primary転写側span)) is True` ならSCG不実行(`exclusion_reason=heterophone_reading_candidate:原稿->転写`)=従来の再生成へ(誤PASSにしない)。
- 過剰除外防止: (1)辞書に候補が無い/判定不能(None)は除外しない。(2)読みが一致する漢字差(同音)はそもそもcontent_diffにならない。(3)Phase 0救済事例(出演/出現、拒絶/強制、理屈/肉)は読み候補に含まれず除外されない(unit+Phase 0回帰で確認)。
- 実測(分類):「市場/いちば・しじょう」「生物/なまもの」「上手/うわて・かみて」「日/ひ」「人気/ひとけ」はPrimary判定が既にPHONETIC_MATCHで、そもそもSCGに到達しない(既存挙動不変)。TRUE_CONTENT_MISMATCHまで落ちる「一日/ついたち」はC2で除外される。
- 既知の限界(辞書依存): `行った`->`おこなった`は辞書(行: ぎょう/あん/こう/ゆき/いき)に「おこな」が無く検知できない(除外されずSCGが実行される)。辞書補強は新たな仕様判断のため未実装。test `test_unknown_reading_dictionary_missing_is_not_excluded`で現状を明示。
- 影響(Phase 0): g5(程->亭、C群NG)がC2で不実行化(Azure呼出を省略、結果NGは同じ)。救済13件は不変。

## 推奨4 否定マーカー(ず/ません/ぬ/ざる/まい)
- 判定: 部分文字列判定は使わない。fugashi(unidic)で「助動詞-ヌ/助動詞-マイ」かつ表層が`ず/ぬ/ん/ざる/ざら/ざれ/ざり/まい`のtokenを否定とみなし、原稿とPrimary転写の文字差分(opcode)の範囲に重なる否定tokenが**片側にのみ**ある差分があればSCG不実行(`exclusion_reason=negation_marker_diff:...`)。両側に否定がある差分、差分範囲外の否定語、「ませんか」(疑問・勧誘)の「ん」、名詞の一部の「まい」(まいにち/まいご)、「ずっと」「ぬいぐるみ」の「ず/ぬ」は対象外。形態素解析不能時は除外しない(従来挙動)。
- 共通判定(`protected_check_ja`等)は変更せず、`_scg_exclusion_reason`にオプション引数(原稿・Primary転写)を追加しただけ(省略時は従来どおり)。
- 影響(Phase 0): g12(縛られず->縛られる、C群NG)がSCG不実行化(Azure呼出を省略、結果NGは同じ)。g23はmorph判定では否定差分とならず従来どおりAzure実行->NG。救済13件は不変。

## test
- 新規 `er007_ja_scg_c2_neg_test_01.py` 17件PASS(C2: 市場/一日/生物/上手 unit、誤認識の非除外、辞書欠落の非除外、end-to-end一日、Phase 0救済例のPASS維持、PHONETIC_MATCH非到達。推奨4: 片側否定の除外[原稿側/Primary側]、両側同一否定・ませんか・差分外否定・まい名詞・ずっと/ぬいぐるみの非除外、g12型end-to-end、morph不能時fail-open、共通判定不変)。
- 更新 `er007_ja_scg_phase0_regression_test_01.py` 12件PASS(g12=negation_marker_diff・g5=heterophone_reading_candidateはNOT_APPLIED(Azure 0)、実行件数23->21)。
- Phase 0回帰: 救済13件PASS(META3+要試聴6+g11/g17/g20/g31/g33x2等)、g8はC1除外、C群5件verified=False(誤PASS 0)、PHONETIC 3件NG、「出演/出現」META 3 attempt PASS維持。本番条件版も同一。

# OPEN517_DESIGN_01(OPEN-517「READING_MATCH PASSが最終ANDゲートの値・否定の再確認をskipする」是正設計。JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_05、2026-10-25。DEV/proto・API 0・Production変更0)
## 1. 矛盾の定義と該当箇所
**承認済み安全条件(逐語)**: `CURRENT_SPEC.md:2855`「**最終ANDゲート**: 採用しようとする転写(Primary/Secondary/M1・Tier3等の根拠転写)すべてに値ガードDIFF・否定差が無いことを独立に再確認する。**重大内容差(数値・否定)を警告だけで解放する仕様にはしない**(原文L97)。」。値ガード5値の定義は`CURRENT_SPEC.md:2857`、JA Validatorの安全性は`CURRENT_SPEC.md:2178`。
**矛盾する実装**:
| 箇所 | 内容 |
|---|---|
| `er007_ja_asr_validator_01.py:441,502` / `er011_ja_asr_variant_layer_01.py:347-372`(Candidate E) | 分類`PHONETIC_MATCH`の生成(全文読み一致/漢字候補総当たり) |
| `er007_ja_secondary_asr_01.py:427,603` | `PHONETIC_MATCH`/`READING_RESOLVED_MATCH`のPASSに`equivalence_basis="READING_MATCH"`を付与 |
| `er078_asr_unified_judge_01.py:68-73`(`APPROVED_EQUIVALENCE_BASES`に`READING_MATCH`)、`:526-530`(approvedなら`final_gate.applied=False`) | **最終ANDゲートの値DIFF・否定差の再確認をskip**(= 安全条件との矛盾) |
- skipの出自: `er058_output/unified_all_roles_production_wiring_01/IMPLEMENTATION_02b.md:19`「承認済みequivalence根拠…`READING_MATCH`は再否定しない」。Sonnet実装時の設計判断で、`READING_MATCH`のskipを個別に承認したユーザー決定原文は**見つからない**(DECISION_LOG/CURRENT_SPEC Grep: CURRENT_SPECに`READING_MATCH`語なし)。他の3根拠(`HOMOPHONE_MATCH_NUMBER_EXCEPTION`=数詞例外の承認、`TIER1_*`)は値の扱いを含めて承認された根拠で、`READING_MATCH`だけが『値に無関係な読み一致』であるため値を素通しにする。
- 実害(実測、本委任の`open517_api0_eval_03.out.json`): 現行PASSの`READING_MATCH`(PHONETIC_MATCH)のうち、値/助数詞が違うまま通る既知負例9件(`三日間`↔`三日目`×4、`3~5日`↔`35日`×2、`三日`↔`さんにち`、`一分`↔`いちふん`、N3-02[実音声89,000が原稿8,900をPASS])+Phase 3 月題転写1件(`8000九百本超`)。
## 2. 是正案(DEV/protoで検証済み。Production未適用)
**F1(本体)**: `READING_MATCH`のPrimary PASSにも最終ANDゲートを適用する(値ガードDIFF・否定差=NG_PROTECTED、AMBIGUOUS=P3[Secondary]降格)。**分岐は他の非承認PASSと同一**(`er078_asr_unified_judge_01.py:538-553`)。他の承認根拠のskipは触らない。Production差分=`APPROVED_EQUIVALENCE_BASES`から`"READING_MATCH"`を除く1行(+コメント)。
**F2(副作用の除去。F1だけだと正常な転写を誤NGにするため必須)**: 単純にF1だけを入れると、正常音声を誤NGにする。実測(F1のみ、`open517_value_gate_probe_01`+本評価): (a)P4実attempt 133中1件(`いちばん低い`↔`一番低い`)、(b)正例対照47中の現行PASS10件のうち6件(`みっかかん`/`しがつ`/`さんにん`/`ひゃくえん`/`しちがつ`/`じゅうだい`の『かな書き数詞』)。原因は数詞/序数/慣用語が誤検出されたのではなく、**片側がかな書きの数詞で値atomが脱落扱い(`_drop_verdict_ja`→DIFF)になること**。
- 『数詞でない`一番/一部/一方/一度/一緒`等を除外する閉集合』は採らない。実測(`extract_atoms_ja`の全走査): `一部/一方/一緒/一般/一体/一気/一生/一切/一定/一同/一旦/一応/一種/一面/一律/一斉/一連`は助数詞を含まず**atomにならない**(除外不要)。atom化されるのは`一番`(ban)・`一度`(do)等の『一+助数詞』のみで、これらは慣用語でも値は同じ(`一番`=1番)。除外ではなく**等価表記の統一**が正しい設計(`二番`↔`にばん`などの値違いを隠さないため)。
- F2の規則(汎用、ID特例なし): 相手側テキストに数値atom(値n, 助数詞c)があり、こちら側にその**期待読み**(`_cands(n,c)`、`みっか`/`ついたち`/`しがつ`/`ひゃくえん`/`いちばん`…)に完全一致するかな列があれば、そのかな列をatomの表層へ置換して値ガードに渡す。**期待読みに無い読み(`三日`↔`さんにち`、`一分`↔`いちふん`)は置換されずNGのまま**(不規則読みの保護=2026-10-11安全条件は維持)。F2を適用するのはPrimary PASS(根拠READING_MATCH)の最終ゲートだけ(Primary NGのP1、Secondary gateは現行のまま=Production挙動を広げない)。置換で既存atomを壊さない(KANA_NUMERALS等で既atom化済みの位置は触らない)。統一前の警告を併合し、統一で認識した不規則読み署名にはJA_NUMERIC_IRREGULAR_READING警告(非ブロッキング・試聴リスト行き)を付ける。
- 期待読み表の出所: `er066_ja_asr_orthographic_equivalence_01_trial._cands`(Production vgの『移設元』module)。**Production適用時は表の移設(約100行)+parity testが必要**(Trial moduleをProductionがimportする構造は避ける)。
## 3. 対象外(別件。Candidate Eの承認範囲確認)
- N3-07(`しわ`→`すわ`、`月の巣は`)はCandidate E(漢字候補総当たり、`er011_ja_asr_variant_layer_01.py:347-372`)の近音PASSで、**値ガードでは原理的に検出不能**(値がEQUAL/NO_VALUES)。F1/F2の対象外。
- Candidate Eの承認状況(DECISION_LOG Grep): `PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01` Phase 2(`DECISION_LOG.md:10208-10215`、Status=`APPROVED_FOR_PRODUCTION`[ユーザー承認済み設計、Phase 1 recon経由])の一部として実装され、Hormuz B1B『海からの封鎖』の3回STOPPED是正に使われた(`RESULT_PACKET_PRN2.md:15,28`)。**Candidate E固有のスコープ(非数値の同音過許容)を個別に承認したユーザー決定原文は見つからない**。過許容は`OPEN-333`(JA-ASR-CANDIDATE-E-OVERPERMISSIVE…、重大度低、USER_DECISION_REQUIRED・未実装・未承認)として既に登録済み。N3-07型はCandidate Eの設計上の許容であり『値・否定の最終確認との矛盾』ではないため、OPEN-517では扱わずOPEN-333の判断(取消ガード採否)に委ねる(Fable/ユーザー判断。ここでは対応方向のみ=署名/近音取消ガード案はOPEN-333に既出)。
- その他の既存誤PASS(同形異音・助詞誤読・同音異義`七晩`↔`七番`[`晩`が助数詞表になくUNKNOWN素通し]・N3-24)は値ガードの対象外=既知の限界(O3)として据置。
## 4. 影響範囲
- **ファミリー**: 統一judge(`er078_asr_unified_judge_01.py`)はJA経路でX・Z・Y・legacy A/B/C共通。X・Z・Yの日本語narration/タイトル/Voices等のPrimary PASSが対象(英語は`READING_MATCH`を付与しないため不変)。
- **挙動の変化**: Primary PASS(READING_MATCH)が値DIFF/否定差を含むとき `PASS → NG_PROTECTED` となり、**Secondary(Azure)を呼ばず次slotへ=TTS再生成**(retry消費)。AMBIGUOUSは`P3`=Secondary 1回。slot3(最終)でNG_PROTECTEDなら既存どおり`HUMAN_REVIEW_REQUIRED`のHR Lock(U4を含む既存仕様は不変)。Local Rewriteは英語のみ=JA無関係。
- **retry/HR増の見積**: 実attempt P4 421(READING_MATCH PASS 133)で、F1+F2適用後のNG化/降格は**0件**。コストはゼロに近い(誤PASSを通していた分だけ、真の誤読の再生成が増える方向=品質向上)。
- **HR Lock**: 新規に Lock へ入るのは、最終slotでも値DIFF/否定差が残る真の誤読のみ。正常音声のLock入りは実測0。
- **warning**: 不規則読みのかな書き数詞に`JA_NUMERIC_IRREGULAR_READING`が新たに付く場合あり(PASS→PASS_WITH_WARNING、非ブロッキング。正例対照3件。不要ならF2の警告付与のみ外せる)。
## 5. Production適用に必要な作業(ユーザー判断後の別委任)
(1)期待読み表の移設+parity test (2)`er078_asr_value_guard_01.py`に`unify_kana_numerals`追加、`er078_asr_unified_judge_01.py`の`APPROVED_EQUIVALENCE_BASES`から`READING_MATCH`除去+Primary最終ゲート(READING_MATCH時)でF2適用 (3)既存testの更新(`er078_asr_unified_ja_wiring_test_01.py:194`ほかが`approved_equivalence:READING_MATCH`のPASSを期待している場合)+新規test(既知負例9・正例・警告保全・非READING_MATCH経路不変) (4)全er078/er007 regression。見積: 実装0.5日相当・API 0・費用0円。**適用前にOpus軽量レビュー+ユーザー報告**(`OPUS_REVIEW_REQUEST_01_OPEN517.md`)。Production適用は『既存の承認済み安全条件への是正(11-8の不具合)』だが、`READING_MATCH`の意味変更(skip撤廃)であるため事前報告を行う。
## 6. 主な限界(隠さず)
- 評価データは既存コーパスのみ。F2はv1不合格→v2→v3と同一コーパスを見て再設計(未知データでの汎化は未確認)。
- F2は『相手側にatomがある』ときのみ機能。両側とも数詞がかな(`いちばん`↔`にばん`、READING_MATCH PASSにならない)は元々対象外。
- `三日`↔`さんにち`等の『誤った読みのかな書き』は値ではなく読みの問題だが、F2の期待読み表でNGに残る(安全側)。ASRが正しい読み(みっか)をかな書きした場合はPASS。

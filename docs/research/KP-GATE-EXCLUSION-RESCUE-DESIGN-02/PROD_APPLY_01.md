# PROD_APPLY_01: 区分1(承認済み規則への準拠修正)のProduction適用(KP-GATE-EXCLUSION-RESCUE-DESIGN-02 委任_03)

Status: IMPLEMENTED_PENDING_EVIDENCE(PRODUCTION_WIREDではない)。API 0。2026-10-26。根拠: ユーザー原文 `2026-10-26_KP-GATE-EXCLUSION-RESCUE-DESIGN-02_USER.md` §3④(区分1)、Opus Q1(b)/Q2(b)・M1/M2/R3(`OPUS_REVIEW_02.md`)。

## 1. 差分要約(最小。3点のみ、全て全文選定=X/Z/将来Y経路に限る)
| # | 変更 | 場所 |
|---|---|---|
| ① | 副詞前の原形化(guard是正): `_token_pair_ok`の既存条件で不受理のときだけ`_adverb_follow_ok`を追加判定。-ly名詞/動詞/形容詞の除外表(`LY_ADJ`/`LY_NOUN_VERB`)+語幹のCMU実在+LLM提案語(前方活用)一致+副詞が句末/前置詞等の直前、を全て要求 | `er105_kp_fulltext_selector_01.py`:689-697(分岐)・:943-1015(`LY_ADJ`/`LY_NOUN_VERB`/`_ly_stems`/`is_manner_adverb`/`_adverb_follow_ok`) |
| ② | 有限助動詞`have/has/had`の役割判定: `_legacy_form_reasons`(:219)で`contains_finite_aux_role_based`、canonicalizationは`allow_inflection_normalization=True`のときだけ同関数(A/B/Cは従来の語形リスト判定) | `er105`:885-940(`have_role`ほか)、`er003_key_words_canonicalization.py`:627-634 |
| ③ | 過去形表の補完(import時に1回・冪等・既存エントリ不上書き。`bound/lay/wound/ground/bore`と他動詞原形と同形の語は追加しない) | `er105`:1016-1029(`_complete_past_tables`) |

DEVから逐語移植したデータ表・関数: `IRR`/`COMPLETION_EXCLUDE`/`PAST_ALSO_OTHER_WORD`/`IRR_PARTICIPLES(_EXTRA)`/`_HAVE_*`/`LY_ADJ`/`LY_NOUN_VERB`/`_MANNER_ADV_EXTRA`/`forms`/`inflects_to`。DEV `TIER1_PATCH`のうち`quant`(量化詞限定詞guard)は委任文の区分1範囲(①②③)に無いため**未適用**(受理面を広げない。次項参照)。`er003_key_words_min_unit.py`は全文選定経路から呼ばれない(grep: er105にp2g参照0)ため**変更なし**。

## 2. A/B/C不変の証拠
- 新ロジックは`allow_inflection_normalization=True`(=`is_fulltext_item`)と`er105`内(全文選定専用)にのみ存在。`_token_pair_ok`/過去形表は`is_valid_inflection_normalization`経由(全文経路のみ)でしか参照されない(Grep: `_token_pair_ok|_AMBIGUOUS_IRREGULAR`の呼出元はer105内とer123[DEV]のみ)。
- `abc_golden_01.json`: 変更前(git HEAD)の`validate_canonicalization_item(..., allow_inflection_normalization=False)`+`kc._contains_finite_auxiliary`の出力1002件を固定。`er105_kp_rule_compliance_test_01.py::TestAbcByteIdentical`で現コードとJSON文字列一致を確認(PASS)。生成: `tools/gen_abc_golden_01.py`(変更前のHEAD版を置いたdirで実行)。

## 3. DEV/Production parity(`tools/prod_vs_dev_parity_01.py`、`parity_01.json`)
DEV側=`er123 RulePatch(aux, adverb, past)`を**git HEADのProduction**へ当てた判定、Prod側=現worktree・パッチ無し。比較: adversarial 85件、実データ(X/Y/Z全KP出力)の表示句315・既選定ペア84・全位置x全語形候補133、have窓299(newly 72+still 227)、過去形2表全体(81/71)、full validator(allow=True)出力。結果: **parity=true、不一致0**(DEV→Productionの移植で判定が変わった件=0、STOP条件非該当)。

## 4. 回帰test
`er105_kp_rule_compliance_test_01.py` 19件PASS(敵対的85件=conversions22/have_roles40/past8/idiom15、A/B/Cバイト同一1002件、AI島a2`studied separately`のvalidator PASS[保存済みdropped[]から机上、HR候補は再生成せず]、`heated debate`型/`increased supply`不受理、`has spread`等aux、`rang through→ring through`、`lay/wound/ground/bore/bound`非追加、区分2未配線)。既存testの更新(旧仕様を期待値にしていた検査の撤去・改訂): `er105_kp_fulltext_selector_01_test_01.py::test_v_plus_adverb_or_noun_phrases_are_not_normalized`(`tried hard→try hard`は区分1で受理へ。V+名詞・`stopped short`は不受理のまま)、`er123_kp_rescue_dev_01_test_01.py`の3検査(`test_default_off_current_production_behaviour_unchanged`/`test_patch_flags_are_independent_and_minimal`/`test_r3_past_table_completion_excludes_homographs`: 『パッチ外=旧Production』前提をProduction適用後の状態へ更新)。

## 5. 副詞後の`hard`/`fast`/`alone`/`again`/`often`/`always`/`never`(閉表、`_MANNER_ADV_EXTRA`)について(開示)
`tried hard→try hard`がProductionで受理になった。副詞が句末/前置詞等の直前、かつ提案語が前方活用一致のときのみ。`hard`の形容詞用法(`hard cheese`等の名詞前置)は`tail`条件で止まる。Opus M1で`well/still`は名詞用法のため除外済み。

## 6. runtime evidence計画(次のKP生成run、AI島以外)
- 各runの`keywords_canonicalized.json`/`kp_candidates*.json`の`dropped[]`に、`Rule7`(`source_spanに存在しない別の辞書形`)由来で`-ly副詞`/不規則過去形を含む句、および`有限助動詞`由来で語彙動詞`have/has/had`を含む句、が残っていないこと。
- `study separately`型(`-ed + 副詞`)がcandidates側へ入った場合、`used_form`が原形・`display_phrase`が表層形で保存され、`validate_canonicalization_response`が`PASS`であること。
- 副作用なし: A/B/C(旧5件経路)のKP出力・ログの差分0(経路が走ればgolden同様)。
- AI島run_ai_01のHR候補は再生成・確定しない(`status`が前後不変: `hr_status_before_03.json`==`hr_status_after_03.json`)。

## 7. 残るリスク(開示)
- `LY_NOUN_VERB`/`LY_ADJ`は閉表。未収載の-ly名詞でかつ語幹がCMUに実在する語は理論上すり抜ける。緩和=副詞が動詞位置の直後かつ句末/前置詞・限定詞の前に限る、実データ315種に該当0、敵対的tests。
- `IRR_PARTICIPLES_EXTRA`に無い不変化分詞は`has`+表外分詞で語彙判定されうる(完了形を通す方向)。迷えばaux側。

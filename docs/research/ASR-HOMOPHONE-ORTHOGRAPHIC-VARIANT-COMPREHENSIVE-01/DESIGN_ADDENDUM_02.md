# DESIGN_ADDENDUM_02(ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01 委任_02、2026-10-22。DESIGN_PROPOSAL_01への追補。API 0・費用0)

Status=`B_FIXED_C_VALIDATION_PENDING_FABLE`相当(er109は**未配線・既定OFF**のまま。Production配線は次委任でFable判断)。Opus必須レビュー全文=`OPUS_REVIEW_MANDATORY_01.md`。台帳=`docs/pm/OPUS_FINDINGS_LEDGER.md` OF-AHO-P-01〜12。

## 1. Opus指摘(P-01〜P-12)への対応表

| ID | 区分 | 対応 | 実装/証拠 |
|---|---|---|---|
| P-01 | Major | 強勢を除去せず**2値(強勢あり=1/2、なし=0)**で比較。`ok`(OW1 K EY1)/`okay`(OW2 K EY1)は同値維持、`billow`/`below`・`for tea`/`40`は非同値 | `er109:_strip_stress`→`er008 homophone_en._stress2_tokens`。test `OpusMustFix.test_p01_*` |
| P-02 | Major | 強勢母音を含まない読み(弱形のみ)での一致は不可。語unitは『強勢読みのみ』で比較(are=ER0/or=ER0は不一致)。`we're`/`were`・`our`/`are`・`I'll`/`ill`・`he'll`/`hell`・`we'll`/`well`も不一致 | `er109:_strong/_unit_set`。ほか**旧v0の『アポストロフィ除去keyで`we're`==`were`が"表層一致"になる』欠陥を発見・是正**(`_word_key`でアポストロフィ保持) |
| P-03 | Major | 同形異音語の保護: **canonical側が強勢読みを2つ以上持つ語は不可**(lead/led, desert/dessert, read/red, wind/wined, bass/base, won, route, flour, whisky等)。ASR側は**代表(先頭)強勢読みのみ**で比較(our→AW ER0。少数派読みAA R=areでは一致させない)。適用範囲はer109とB-2で新たに到達可能になる経路のみ(既存の本文同音救済`homophone_arpabet_equivalent`は無変更) | 共通関数`er008 homophone_en.strict_homophone_pair(canonical, asr)`(追加のみ・既存関数無変更)。B-2もこの関数を使用 |
| P-04 | Major | 曖昧略語(`St`/`Dr`/`Mt`/`#`)はfail-closed(同じ語の活用違い[degree/degrees, minute/minutes, foot/feet]だけ許す)。大文字略語はCMUの展開variant(`tv`→television)を使わず『文字読み+代表発音』のみ。母音字の無い綴り(tv/st/dr等)は略語としてCMUを使わない | `AMBIGUOUS_ABBREVIATIONS/AMBIGUOUS_SYMBOLS`・vowelless規則。test `test_p04_*`、敵対検証の`abbreviation_cases` |
| P-05 | Major | **敵対的負例を再構築**(下記§2、`er109_adversarial_negatives_01.py`)。旧負例(循環)は参考値に格下げ | `adversarial_negatives_02_aho02.json` |
| P-06 | Major | 最終ANDゲートの扱い=**設計**(§3)。配線は次委任 | 本書§3、オフラインモデル`er109_stored_onoff_compare_01.py`(`explained_by_spans`) |
| P-07 | Minor | 数・記号・略語・頭字語を含むspanに混ざる普通の語は、数の読み語彙(基数・序数・位取り・and/point/oh/percent/通貨・時刻・分数・記号/略語の展開語・文字名)とその厳密な同音語(to/too→two, for→four, won→one, ate→eight)に限る | `_NUMBER_VOCAB/_in_number_vocab`。`for tea`/`40`は`tea`で非同値 |
| P-08 | Minor | 警告方針+監査項目: 決定的規則(数・記号・綴り連結)=警告なし(`PASS`)。否定語同音(no/know)・代表発音以外のvariantでのみ一致=`PASS_WITH_WARNING`+事後試聴。監査=span毎の一致variant・代表か・stressモード・同形異音フラグ・flag状態・層version | `EquivalenceResult.verdict/warnings/audit()` |
| P-09 | Minor | 漏れの分類記録: `March 5`(C)、`$5 million`(C)、`24/7`(C)、`World War II`(C-KP)、`-ise/-yse`(E)。いずれも**誤同値にならず従来どおり不合格**(test固定) | `PATTERN_CATALOG_02.md`、`test_p09_*` |
| P-10 | Minor | HR Lock済みsegmentの明示再判定手順を設計(§4) | 本書§4 |
| P-11 | Minor | 11-7例外の条件を配線設計に明記(§5) | 本書§5 |
| P-12 | Minor | B修正は既存単一関数を再利用(§6) | `val._convert_compound_ordinal_words`再利用、`homophone_arpabet_equivalent`+`strict_homophone_pair`の両方を要求 |

## 2. 敵対的負例の再構築(P-05)
旧負例生成器は『stress除去後の全variantで交わらない語』を置換先に選んでおり、er109自身の判定基準と循環していた(構造上、弱形・stress除去・代表以外variant・同形異音語・曖昧略語の誤同値を検出できない)。新しい生成は**CMU辞書全体(124,082語、a-z+アポストロフィ1つ)**から:
1. **語対の全数**: 綴りの異なる語の組で、stress除去・any-variantで音素列が交わるもの(56,002組)。代表強勢読みが一致しない組(=非代表variant・弱形・stress差・同形異音語でしか交わらない)を『adversarial』、一致する組を『positive(通常の同音語)』に二分。adversarial組での er109 同値が**誤同値候補**。
2. **2語oronym**: 任意の1語を2語へ音素列で分割できる組(3,000語ターゲット)。
3. **数のoronym**: 数字(0〜200ほか)の読みを数詞語彙以外の語列で再現する組(`for tea`/`40`型)。
4. **曖昧略語**: `St./Dr./Mt./#/TV/US/Mr./Ms.`の誤展開ケース + CMU全語の2〜5字大文字略語×同音語50,036組。
結果は`VALIDATION_02.md`に記載。

## 3. 最終ANDゲート(値DIFF/否定差)の扱い(P-06。配線は次委任)
- 現行(`er078_asr_unified_judge_01.py`):Primary PASS後に、承認済みbasis(`APPROVED_EQUIVALENCE_BASES`)ならゲートskip、それ以外は`pvg.kind==DIFF or pneg`で`NG_PROTECTED`(:445-454付近)。Primary NG側は`vote is None and (pvg.kind==DIFF or pneg)`でP1短絡。Secondary側は許容判定より**前**に`svg/sneg`を見る(:599)。
- 設計(丸ごとskipしない): er109の同値で合格にするとき、**値ガード・否定差は実行し、各DIFFがer109の同値span(`SpanRecord.canon_span/asr_span`)で説明できる場合だけ解除**する。判定=DIFFの各pair(src,hyp)について、あるspanの`canon_span`にsrcが、`asr_span`にhypが含まれる。否定差は、span内の否定語を除いた残りの否定語数が両側で一致する場合だけ解除。説明できないDIFF・否定差は従来どおりNG_PROTECTED(Tier1 diff_anchoredの否定二重防御と同じ前例)。
- Secondary分岐(:599)も同基準: Secondary転写が`ORTHOGRAPHIC_EQUIVALENT_MATCH`でPASSする場合のみ、値/否定差がspanで説明できれば先に進める(許容判定より前の短絡は説明可能なDIFFの時だけ免除)。
- AMBIGUOUS(根拠のない曖昧表層)は従来どおりP3降格(er109で解除しない)。
- オフライン検証: `stored_onoff_compare_02.json`は上記モデルで保存4,879行を判定(`blocked_by_final_gate`=説明できず解除されなかった件数も記録)。

## 4. HR Lock済みsegmentの再判定手順(P-10。API 0、自動解除なし)
既に`HUMAN_REVIEW_LOCKED`のsegment(旧コードでNG→HR)は、flagをONにしても自動では再判定されない(Opus §観点6)。救済する場合の手順案:
1. 明示CLI(新規・既定で何もしない)が`review_lock_state.json`の`last_attempts_log`(保存転写・wav sha)を読み、現行judge+er109で**ローカルのみ**(API 0)再判定する。
2. 全attemptが引き続きNGなら何もしない。いずれかが`PASS`(警告なし)なら『HR解除候補』として一覧化するだけ。`PASS_WITH_WARNING`は事後試聴リスト行きで候補にとどめる。
3. 解除は人間(ユーザー/Fable)の明示操作のみ。自動解除・自動再生成は行わない。解除時はlockファイルに解除理由・判定version・操作者を追記する。
本委任では実装しない(配線時の別タスク)。保存データでHR/STOPに至った該当は3segment(`stored_onoff_compare_02.json`)。

## 5. 11-7限定例外としての配線条件(P-11)
配線する場合の5条件を満たす設計: (1)新コード経路(`classify_asr_match`ラッパー末尾の1箇所)+**単一flag読取関数**`er109.is_enabled()`のみ。mode/関数引数/設定dictからONにできない (2)既存のProduction Prompt・正規表現・閾値・辞書は**直接編集しない**(新basis名の追加は`APPROVED_EQUIVALENCE_BASES`/`_equivalence_basis_of`への加算のみで、flag OFFでは到達不能) (3)flag OFFで**API呼出0・出力不変・副作用ファイル0**を`DefaultOffIsolation`型testで固定(新basisのreachabilityも含め、`ORTHOGRAPHIC_EQUIVALENT_MATCH`が返らないことを網羅) (4)起動script・`.env`で暗黙にONにしない (5)`OPEN_ITEMS.md`にflag名と『未承認・既定OFF』を記録しPRODUCTION_WIREDと呼ばない。**新ラベルを使う側**(`VALID_CLASSIFICATIONS`・PASS_WITH_WARNING registry・事後試聴リスト・Store再利用/X引継ぎ/A/B/C呼出点)の確認もtestで行う。隔離が破られた場合は11-7どおり安全停止・事実報告。
Secondary分岐(:599)の変更も同様に**flag OFFでは到達不能**にする(新basisが付かない限り現行分岐のみ)。
本委任では配線しない(Fable判断、Opus指摘P-11/Q3: 位置は`classify_asr_match`末尾でGO)。

## 6. B不具合3件の最小修正(P-12。独立commit)
- B-1 値ガードatom(`er078_asr_value_guard_01._en_atom_text`): `val._convert_compound_ordinal_words`(既存の単一関数)を再利用し`twenty first`→`21st`。再実装なし。
- B-3 同関数: `(?<=\d) +%`→`%`(`60 %`→`60%`)。
- B-2 `val._homophone_swap_only_bypass_ratio_gate`: ratio<0.4のTTS_FAILUREを迂回してよいのは、token数同一・差の全位置が1:1置換で承認済み同音判定(`homophone_arpabet_equivalent`)True・`strict_homophone_pair`True・entityでない・多語同音でない・差の位置がcontent diffと過不足なく一致する場合のみ。迂回後は既存の同音語経路(UNCERTAIN→`_step_alternate_pass`→`HOMOPHONE_EQUIVALENT`)。挙動変化は『不合格→合格』方向のみ(A/B/Cの共有Validatorにも同じ改善が及ぶ。Production品質Gateの緩和ではなく、承認済み規則が到達できなかった不具合の是正)。

## 7. A/B/C波及(a)呼出点共通 vs (b)opt-in(F2)
推奨(a)。保存データでer109がA/B/C側で新たにPASSにする件数は`VALIDATION_02.md`§5。B修正のA/B/C波及(NG→PASSのみ)は`bfix_before_after_01.json`。(b)を選ぶ場合は呼出点ごとのパッチではなく、既存のrun-scope方式(`er103...is_active_for_run`)で実装する。

## 8. ユーザー判断が必要な新仕様(Opus §5の7項目。採用判断材料。判断はVALIDATED後)
(27-3分類: 原則『同一発音=同等』=A既判断[ユーザー原文§2・§6]。具体方式の採用=D新規)
1. er109の採用。KP/Whisper票への数の表記差の適用を含む(Tier1をKPに適用しない承認済み仕様の範囲拡大)。
2. 否定語の同音(no/know)を警告つきで同値扱いにすること(`PASS_WITH_WARNING`+事後試聴)。
3. er109の同値を最終ANDゲートの承認済みbasisにすること(span単位で解除、§3)。
4. A/B/Cへの波及を(a)許容するか(b)opt-inにするか。
5. 記号・曖昧でない略語・年代・時刻・セント・年読みの閉じた読み表(曖昧略語St/Dr/Mt/#はfail-closed=救済しない)。
6. 警告・事後試聴の方針。
7. (任意)oronym(ice cream/I scream)を除外したままにすること。

---
## 【委任_04 2026-10-23 追記】§5(11-7限定例外の読替え)
正式採用(APPROVED_FOR_PRODUCTION、2026-10-23)により、本書§5が前提とした『11-7限定例外(未承認・既定OFF、5条件)』は役割を終えた。委任_04で配線した現行状態は『X/Z run-scope内のみ有効、`ORTHOGRAPHIC_EQUIVALENCE_ENABLED`(=True)はrollbackスイッチ』であり、旧`ProductionIsolation`(DefaultOffIsolation)testは撤去・置換済み(`er109_xz_isolation_01_test_01.py`ほか)。§5の5条件は『未承認機能を既定OFFで隔離する』ための要件であり、現行(承認済み機能をX/Z scopeで有効化)には適用しない。

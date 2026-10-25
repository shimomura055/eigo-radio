# OPEN333_DESIGN_02(しわ↔すわ=N3-07 是正: Opus条件Cレビュー反映後の設計。JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_12、2026-10-25)
結論(先に): **区分=実装不具合(承認済み条件の機能不全)を維持。是正本体=E3(P-1なし)をProductionへ適用(既定ON・rollback定数あり)。助詞免除P-1は未承認のv2規則のため不具合是正に含めず、ユーザー判断(v2/②B-light β と一体)へ回す。E4(便乗PASS)は評価済み・Production未適用(Fable判断待ち)。** 費用0円・API 0。
## 1. R-1 確認(Candidate E承認の対象範囲)
DECISION_LOG.md:10208-10300(PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01 Phase 2、2026-09-27、APPROVED_FOR_PRODUCTION)の原文: 「固有名詞読み解決(JA/EN共通)…Phase 1 reconで確認された『JA: 未知語→即HUMAN_REVIEW』『EN: Ledger/Researchは実装済みだが未配線』の2ギャップに対し、共通core `er025_entity_pronunciation_resolver_core_01.py` を新設しJA/EN双方へ配線した」。runtime evidenceのJA-3は「Hormuz B1B『海からの封鎖』、Candidate E `PHONETIC_MATCH` を無改変のまま再確認」(=非数値entry)。**『数字不一致の経路(protected_check_jaが数字差で保護落ちした後のOPEN-145追加型チェック)でCandidate Eが動く』とは書かれていない**(DECISION_LOGの`try_rescue_before_resolver`/`number_mismatch`のGrep: Candidate Eの承認記述とその経路を結ぶ行なし)。数字差の経路を承認したのは2026-09-12のOPEN-145(er007:366-380のコメント『誤PASSのリスクを生まない』=全文の読み一致/正規化後一致のみ)であり、その後、同じ`try_rescue_before_resolver`関数にCandidate Eが追加されたことで数値entryでもEへ到達するようになった。→ 『Eが数字不一致経路で動くこと自体が承認前提外』。ただしE3は『承認時の前提[残りの読みが1つでも違えば通さない]へ戻す最小是正』と説明でき、結論は変わらない(Opus R-1の予想どおり)。
## 2. 区分判定(変更なし。Opus同意)
N3-07は検査漏れ。根拠=`OPEN333_DESIGN_01.md`(i)、反証=CF1〜CF3(`open333_trace_01.out.txt`)。『Candidate Eの設計どおりの過許容』ではない(`DESIGN_02.md:53`の分類は誤記、訂正済み)。OPEN-333本来(同形異音の今日→こんにち等、7件中N3-07以外の6件)は別原因・従来どおりユーザー判断のまま。
## 3. 是正の設計(E3、Production適用版)
- 位置: `er011_ja_asr_variant_layer_01.try_rescue_before_resolver` のCandidate E分岐。`remaining_diffs`の全件が共通読みで説明できたとき、**数値entry(`protected.number_mismatches`あり)に限り**`_candidate_e_number_entry_rejections`を呼び、空でなければ`return None`(呼び元`classify_ja_asr_match`が既存の`TRUE_CONTENT_MISMATCH`を返す。新しいPASS経路・新しい状態なし)。
- 検査: 両全文から**値ガード(`er078_asr_value_guard_01.extract_atoms_ja`)が数値と認識したspan(num/frac/approx/unparsed)だけ**を同一placeholder(``)へ置換(R-2。削除ではなく置換でアラインメント安定。語中の漢数字[一緒・千葉・九州]は値と認識されないため剥がさない)→ 全文を再diff → 各差分を[一致|窓幅付き読み一致|E候補共通読み]で説明できなければ拒否。placeholderのみの差(値spanだけの差)は検査対象外(値の一致は値ガード担当)。P-1(助詞は→わ免除)は**入れない**。
- 多層防御(R-6): 同じ分岐で、最終Gateと同じ`value_guard_kana_unified`が`DIFF`/`UNKNOWN`ならEを拒否(`EQUAL`/`NO_VALUES`/`AMBIGUOUS`は許可=AMBIGUOUSの降格は従来どおり最終Gate/P3が担当)。07A F1(最終Gate)が単独でrollbackされても、8,900↔89,000型がEを通って`PHONETIC_MATCH`になる経路を二重に塞ぐ。判定を広げる方向の変更は無い。
- fail-closed(M-5): helper内の例外は『説明できない=拒否』(拒否pairに`helper_error:<例外名>`を記録)。
- rollback定数(env/flag/引数で切替不可、ソース1行): `er011_ja_asr_variant_layer_01.CANDIDATE_E_FULL_DIFF_CHECK = True`(再検査)、`CANDIDATE_E_VALUE_GUARD_CHECK = True`(値ガード多層防御)。OFFでHEADと完全一致(testとparityで固定)。
- audit field(M-6、判定不変): 拒否した(c,a)を`protected.candidate_e_rejections`(動的属性・dataclass fieldを増やさない)に記録し、adapterが`asr_judgement.candidate_e_full_diff = {"rejected":n,"pairs":[{canonical,asr,kind}]}`へ複写(拒否が無ければfield無し=出力不変)。集計は`open333_first_run_tally_01.py`。
- proto↔Production(M-4): protoをimportせず移植。一致検証は`eval_open333_prod_parity_01.py`(2,716キー: 全行+sweep+旧sweep+E4行+Secondary対)で差分0。
## 4. 評価で見えた副作用・限界(隠さない)
1. **月題#1(転写『月の詩は八千九百本長』、正常と推定)がNG化**(1/677=0.148%の再生成増)。承認済み仕様どおりの結果(非糊付けの『詩は』↔『しわ』と同じ)。『正常な月の記事タイトルの救済』はv2/②B-light βの担当。ユーザー受入条件『正常な月の記事タイトルを適切に救済できる』との関係: **E3単独では月題#1型は救済されない**。救済は助詞は→わ規則(P-1/v2)のユーザー判断に依存する。
2. 値と認識されない単位(℃・km・〇/零表記など=OPEN-522助数詞表外)は、数値entryでEを通る場合に非数値残余として扱われ拒否され得る(関数レベル検査で4/40件。いずれも現行HEADでEに到達せずNGまたは別経路PASSのため判定変化0。将来Eに到達する形になった場合の誤NG余地)。
3. 数値entryに限り、Eが救済した後に残る**カタカナ/略語同士・濁点のみの差**(非糊付けならCascade[Azure再確認]へ回る型)も、E3の再検査では『説明できない』として拒否(即TRUE_CONTENT_MISMATCH=再生成)になる。安全側だが、非数値entryのCascade扱いとは不整合(Opus論点2-3)。E4の設計候補(§E4)で整合化できる。合成の正常等価表記(ヴェ↔ベ・muse→ミューズ等)の数値entry 25件のうち24件がこの影響でPASS→再生成(実データ1,327行では該当0)。
4. 値スパンの片側だけ認識される非対称(七晩↔七番など、`晩`が助数詞表外で`番`が表内)は非数値残余として拒否され得る(Secondary対の1件で確認、判定への影響は受理関数が`PHONETIC_MATCH`を受理しないため0)。実データのPrimary段では該当0。
## 5. ユーザー判断へ回す点
- **P-1(助詞は→わ・へ→えの発音等価免除)**: 判断候補(D真に新しい判断)。理由=未承認のB-light v2規則を不具合是正の既定ONに入れることになる(Opus・Fable判断)。v2/②B-light βの採否と一緒に判断。実装していない。
## 6. E4(便乗PASS)の設計と位置づけ(Production未適用)
`OPEN333_EVAL_02.md` §4。E3の同じE分岐に『cascade_eligible差分が残るならE-PASSにせず`ASR_VALIDATION_UNCERTAIN`(Cascade)』を足す形(`proto_open333_fix_05.py` E3V_E4)。設計案は3つ(下記)。適用はFable判断。
- E4(全cascade_eligible): 非数値entryの便乗負例 現行PASS 46/55 → 0。コスト=非数値entryの等価表記(正常)24件中23件がCascadeへ。実データ(1,327行)では4行(0.59%: 走れメロス→走レメラス[本物の読み違い]、ヴェラ→ベラ、muse→ミューズ[正常等価]、Meta/Muse混在の崩れた転写)。
- E4E(entity_likeのみ): 本評価の負例の濁点のみ差(テ→デ、ク→グ)はカタカナ同士で entity_like にも該当するため E4E でも閉じ、E4と結果が同じ。ひらがなのみの濁点差(phonetic_uncertainのみ)は負例に含めておらず**未検証**(E4とE4Eの差が出るのはその型だけ)。
- E4-N(数値entryで拒否ではなくCascade行き): E3の再検査で拒否される『正常等価表記+数値表記差』をTRUE_CONTENT_MISMATCH(再生成)ではなくUNCERTAIN(Azure確認)へ送る整合化。未評価・未実装。

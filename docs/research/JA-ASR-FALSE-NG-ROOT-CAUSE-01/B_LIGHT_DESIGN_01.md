# B_LIGHT_DESIGN_01(②B-light 対策設計、JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_07B、2026-10-25。設計のみ・API 0・Production変更0)
原因=`B_LIGHT_ROOT_CAUSE_01.md`、事前登録=`B_LIGHT_PREREGISTERED_01.md`(proto sha `5b715f8e…`凍結)、結果=`B_LIGHT_EVAL_01.md`。方針: **Azureの転写を『値の証人』としてだけ使い、読みは今までどおりPrimary(と承認済みの読み規則)で保証する**。Azureが数字を正しく書いたことだけでは決してPASSさせない。

## 1. 観点7点への回答(推奨=案β)
| # | 観点 | 回答 |
|---|---|---|
| 1 | Primary/Secondaryのどの情報を採用するか | **値=Secondary、数値以外の読み=Primary、原稿全体の被覆=両者の組合せ**。Secondaryの読み・Secondaryの表層一致は使わない(R-B3: Azure自身が`杉野氏`のように読みを誤る)。 |
| 2 | 数値そのものの一致をどう保証するか | 原稿の値atom(`extract_atoms_ja`、Production関数)ごとに、(a)**Secondary転写が全atomで値ガードEQUAL**、かつ(b)**Primary転写の数値runが原稿値と等しい、または『位取り断片の連結崩れ』として原稿値に説明できる**、を両方要求。atom単位でPrimary・Secondary・原稿の3者を突合する。 |
| 3 | 数値以外の読みの正確性をどう保証するか | 値atomを`【値】`に置換した残りを、**v2と同じ規則**で原稿と照合: `normalize_ja`完全一致、または助詞は→わ/へ→えのみの発音一致(濁点許容なし・漢字候補総当たり[Candidate E=OPEN-333]なし・LLMなし)。A7登録読み不一致・C2同形異音・否定差は止める(v2の`c2_blocked`等をimportして再利用)。1文字でも残りが違えばNG。 |
| 4 | 不規則読み(三日・二十歳・一日等)の扱い | **原稿に不規則読み値(Production `is_irregular_sig`)を含む文は適用外(NG維持)**。v2の除外を継承(ASRの`3日`/`三日`から`みっか`/`さんにち`は判別できないため)。連濁・音便系(三本・六百等)は`is_irregular_sig`の閉集合外で、Primary層が既に受理している既存盲点と同型(DESIGN_02 §2)。βはそれを**広げない**(増分PASSは『位取り断片崩れ』の型だけ)。 |
| 5 | Primary/Secondaryが矛盾した場合の安全処理 | Primaryの数値runが存在し、原稿値と等しくなく、**断片説明も成立しない**場合は**矛盾=救済しない(`NG_PROTECTED`相当)**。例: Primary`八万九千`/`89,000`/`千九百`/`8800`、Secondary`8900`。Primaryに数値runが無い(脱落)場合もNG。Secondaryの値が原稿とEQUALでなければ(DIFF/UNKNOWN/NO_VALUES)NG。 |
| 6 | 既存の同音異字救済仕様との整合 | Variant Layer(B/C/D-1)・PHONETIC_MATCH・Candidate E(OPEN-333)は**一切拡張しない**。βの読み規則はv2(VALIDATED限定)のA2+A3部分と同一で、`READING_MATCH`を根拠にしない新ラベルのため**最終ANDゲートを通る**(skipされない)。 |
| 7 | 誤NG削減効果と誤PASS増加リスク | 実測は`B_LIGHT_EVAL_01.md`。要点: 月題12転写で+F(07A適用後)に対し**増分+2**(a3保存転写、a3再転写#2[F1が新たにNG化する型])。増分誤PASS=N-3 30clipで0、N-1最悪ケース露出は断片崩れ型1件のみ、合成負例55件で0、回帰0。**効果は『断片連結型』に限られ、a1(Primary読み不一致)・a2(桁欠落=2エンジン矛盾)は救えない**(設計どおり)。 |

## 2. 候補案の比較
| 案 | 内容 | 救済(月題12) | 安全性 | UDR #136/既存条件 | 評価 |
|---|---|---|---|---|---|
| α 厳格複合 | Secondary値EQUAL ∧ Primary値EQUAL ∧ Primary読み一致 | +0(Primary値EQUALならv2が既に救う=ほぼ空集合) | 最高 | 非接触 | **効果なし**。却下(v2と同じ集合)。 |
| **β 説明可能な数詞崩れ複合(推奨)** | α + 『Primaryの数値runが位取り断片の連結崩れで、その総和が原稿値かつSecondary値に一致』を矛盾としない(F-A: 数字のみ2〜3断片、F-B: 数字+漢数字[万億兆なし]。先頭0・カンマ付き・位取り重複は不可) | +2(a3の2転写)。a1/a2は0 | 高(下記)。残余リスク=Azureが台本通りの値を誤って返し、かつPrimaryの崩れが断片和一致の場合 | #136の5条件・2026-10-11条件とも非接触。新受理クラスの追加は別途採用要 | **推奨(VALIDATED限定が上限)**。効果は狭いが、F1適用後の誤NG増を抑える |
| γ 第3エンジン(ローカルWhisper)多数決 | Primary値DIFF∧Secondary値EQUALのとき、Whisper medium等で値を第3判定(KP3Vと同型) | a2(千九百)も値は決まる(Whisper=8,900)。**ただし読みはPrimary`月の島は`で不一致のままa2は救えない**(読みも多数決にしない限り) | 値の判定は強い。読み側の多数決まで広げると別設計 | **#136の条件3(Whisper不採用)・2026-10-11『Whisper 2-of-3なし』に接触=変更要(ユーザー判断)**。JA Whisperは未評価(CPU負荷・small/mediumの精度差) | 判断候補(D)。本タスクでは採用提案しない |
| δ Secondary読み受理(A4(b)) | Secondary転写全体を値atom化+発音一致でPASS | a2の`月の詩は8900本超`を救える(+1) | v2評価でN-1/N-3増分誤PASS 0だが、Secondaryの読みを根拠にする(杉野氏の型が通る恐れ=読み一致のときだけ) | **2026-10-11『Secondary側PHONETIC/助詞差を採用しない』・CURRENT_SPEC L2179/L2856に接触=変更要** | 判断候補(D)。条件(ii)『読みは既存Primary読み照合で保証』に反するため設計要件外 |
| ε 位取り断片の復号単独(DESIGN_01案C) | Secondaryなしで`8000900`を8900と復号して通す | 〃(Primary単独) | 低(Primary単独で値を決める新しい数値解釈系統) | — | 却下(再確認)。βはSecondaryの独立した値支持を必須にするため同じ復号でも安全側 |
**βを推奨する理由**: ①ユーザー条件(Azure数字だけで無条件PASSしない・読み保証・矛盾でNG・不規則読み除外)を全て満たす唯一の案、②#136と2026-10-11条件に触れない、③F1適用で新たに生じる誤NG型(a3再転写#2)を救える、④過適合を避ける制約(断片形2種のみ・カンマ付き不可・総和一致必須)を最初から課している。**限界**: 効果は狭く(月題12転写で+2)、汎化は未確認(`B_LIGHT_BUDGET_PLAN_01.md`に別題材Trialの見積)。

## 3. 推奨βの仕様(`b_light_proto_01.composite_judge`)
入力: 原稿C、Primary転写P、Secondary転写S(Azure)。出力: 新ラベル`JA_SECONDARY_VALUE_PRIMARY_READING_COMPOSITE`+`PASS_WITH_WARNING`(警告`JA_COMPOSITE_VALUE_FROM_SECONDARY`+断片説明時`JA_COMPOSITE_PRIMARY_VALUE_GARBLE_EXPLAINED`+発音等価時`JA_PRON_EQUIVALENT`=事後試聴対象)。
1. P/Sが取得できていること(空・None→NG)。否定差(P/Sそれぞれ、値より前に判定)→NG。
2. 原稿Cの値atomが1個以上、全て整数・助数詞付きの`num`(分数・単位なしは対象外)。**不規則読み値を含めばNG(iii)**。
3. **S**: `value_guard(C,S)==EQUAL`(全atomで値・単位一致)でなければNG。
4. **P**: 各atomについて、助数詞の直前のPrimary数値run(ASCII数字・漢数字、`,`含む)を取り出し、(a)run値==原稿値→EQUAL、(b)断片説明成立→EXPLAINED、(c)runが無い→MISSING、(d)それ以外→CONTRADICTION。MISSING/CONTRADICTIONがあればNG(矛盾はNG_PROTECTED相当)。
   断片説明(狭い2形): **F-A** ASCII数字のみのrun(カンマなし)を2〜3断片に分割し総和==原稿値かつ位取りが重ならない(前断片の末尾0の数≥後断片の桁数: `8000|900`→8000%1000==0)かつ先頭0なし。**F-B** ASCII数字+漢数字(万億兆を含まない)の2断片で同条件(`8000|九百`)。`8,000,900`のようなカンマ付き・`8万9千`のような万含みは説明対象外(=矛盾)。
5. **読み**: 原稿の値atomを`【値】`に、Primaryの対応runを`【値】`に置換した残りを`normalize_ja`で比較。不一致なら発音比較(助詞のみ)。A7登録読み不一致・C2同形異音(`c2_blocked`)→NG。残りの否定有無が違えばNG。
6. 以上すべて成立で`PASS_WITH_WARNING`。Secondary側の読みは**一度も使わない**。

### 3-1 設計段階で通らないことの確認(観点(vi))
- **8,900↔89,000**: Primary`89,000`(カンマ→断片説明対象外)/`89000`(分割`8|9000`は位取り不可、`89|000`は先頭0)/`八万九千`・`8万9千`(万含み)→いずれもCONTRADICTION→NG。仮にSecondaryが台本通り`8900`を返しても通らない(test: `test_value_contradiction_is_not_rescued_even_if_secondary_equals_script`)。
- **しわ↔すわ**(巣は・しば・し・しわし含む): 値が正しくても残りの読みが`つきのしわ`と不一致→NG(`test_reading_difference_is_not_rescued`)。Secondaryの読みは使わないため、Azureが`すわ`を`しわ`と誤って書いても影響しない。
- **みっか↔さんにち**: 原稿に`三日`等の不規則読み値があれば適用外→NG(`test_irregular_reading_values_are_excluded`。`三日`/`二十歳`/`十月一日`)。
- **8000800・8000句800**(8800相当): 断片和≠原稿値/`句`を含み説明不能→NG。**千九百**(桁欠落)→NG(2エンジン矛盾)。
- Secondaryだけ正しい(Primary読み違い)→NG、Primaryだけ正しい(Secondary値違い)→NG(=composite対象外、Primary単独PASSは従来経路)、両方違い→NG。

## 4. Productionでの位置(X/Y/Z共通経路)と周辺機構への影響
- 位置: JA判定はX/Z共通の`er007_ja_secondary_asr_01.evaluate_attempt_ja_with_cascade_detail`(adapter)→`er078_asr_unified_judge_01.unified_judge`(`er063_family_z_audio_01.py:964,979`が`repro01.generate_narration_snippet_verified_strict`を呼ぶ=X/Z共通)。Y Production runnerはZ型stage frameworkのため同経路(Family Y Production計画の共通経路台帳と整合)。A/B/Cは対象外(27-7)。
- フック(配線時、本タスクでは**実装しない**): ①**P1緩和(JA)**: `p1_value_diff`の直前で`composite_judge(C,P,S:=C)`(テキストのみ・API 0。事前判定)が真のときだけP1を打ち切らずP3へ進める(Azureを呼ぶ)。真でなければ従来どおり`NG_PROTECTED`。②**F1最終ゲート**: READING_MATCH PASSの最終値ゲートでDIFFとなったとき同じ事前判定が真ならP3へ降格(AMBIGUOUS降格`primary_pass_demoted_*`と同形)。③**P3許容集合**: `_secondary_accept`がFalseのとき`composite_judge(C,P,S)`。成立で`PASS_WITH_WARNING`。いずれもattemptを消費せず、Azure呼出は`SecondaryCache`(wav sha・engine・lang)で1音声1回。
- **最終ANDゲートは常に通す(観点(vii))**: ラベルは`READING_MATCH`根拠にしない(`APPROVED_EQUIVALENCE_BASES`に入れない)。Secondary採用転写の値(EQUAL)・両転写の否定・A3長さ(`adopted_from=secondary`)を最終ゲートで再確認する。Primaryの値DIFFは『説明可能な崩れ』として監査に`explained_span`を残す(er109の`span_unlock`と同じ記録形)。
- **F1+F2との整合**: βはF1(読み一致PASSでも値DIFFならNG)を弱めない。F1がNGにした『読み一致+数詞崩れ』のうち**Secondaryの独立した値支持と断片説明が揃うものだけ**を、警告付きで戻す。F2(かな数詞統一)とは独立(F2はPrimary値ガード内の正規化、βはその後段)。順序: F1/F2 → (NG時のみ)β。
- **HR Lock**: βはPASSを増やす方向のみ(NG→PASS_WITH_WARNING)。最終slot・minimal fallbackでも同じ許容(`secondary_confirmed`と同様)。Lock済みsegmentの自動解除はしない(配線時test項目)。attempt上限(3)・fallback・Human Review Queueは不変。
- **retry/resume/reuse**: 保存する監査にP転写・S転写・composite label・explained spanを残す。`er078_reuse_value_guard_01`は保存**Primary**転写のみで再判定するため、F1適用後はβで通過したsegmentがP1/最終ゲート理由で再利用blockされる恐れがある→**配線要件**: 再利用guardがcomposite labelの保存entryに限り、保存S転写で`composite_judge`を再実行(API 0)する。試聴リスト再導出で新warningを拾うこともtest項目。
- **Default**: 本protoはProductionから未import(AST test)・未配線。配線する場合は11-7限定例外の5条件(新コード経路+単一flag読取関数・既定OFF・DefaultOffIsolation test等)に従う。flag名案`JA_ASR_COMPOSITE_ENABLED`(**未承認・既定OFF**。ここで定義するのみ、実装しない)。
- 費用: 追加Azure呼出は『Primary値DIFFかつ事前判定が真』の対のみ(評価母集団で2件、約¥0.27/件)。JAのP1発火は全1,217 attemptで2件(0.16%)=期待増分は無視できる。成立すれば1 TTS再生成(約¥0.03〜0.6)+ASR+HR工数を回避。

## 5. UDR #136の変更要否(明確化)
- **β: 変更不要(既存条件内)**。根拠=`B_LIGHT_ROOT_CAUSE_01.md`§5の表(条件1〜5・§3と非接触、Azureは維持され入替・Whisper・追加検証なし)。β採用時に必要なのは『新受理クラスの追加』というProduction採用のユーザー承認のみ(UDR #136の変更ではない)。
- **γ(Whisper第3票)**: #136条件3の変更+2026-10-11『Whisper 2-of-3なし』の変更が必要。変更前=『ローカルWhisperのProduction導入は不採用(KP英語のみ2026-10-22に別承認)』→変更後=『JAの数値矛盾時に限りローカルWhisperを第3票にする』。必要性=a2型(2エンジン値矛盾)は第3証拠なしに決められない。品質影響=値の判定は強化されるが運用複雑化(#136が避けた点)+JA Whisper精度未評価+読み側(a2はPrimary読み`島`)は別途要。**ユーザー判断事項(27-3 D)**。
- **δ(Secondary読み受理)**: 2026-10-11条件+L2179/L2856の変更が必要。観点(ii)に反するため設計要件外。

## 6. 判断候補(27-3)
| # | 内容 | 分類 | 根拠 |
|---|---|---|---|
| J1 | βのProduction採用(新受理クラス`JA_SECONDARY_VALUE_PRIMARY_READING_COMPOSITE`の追加。効果は月題で+2/12・汎化未確認) | D(Production採用はユーザー専決) | 評価後にFableが提示。VALIDATED限定が上限 |
| J2 | γ(JAの数値矛盾時のローカルWhisper第3票)を検討するか | D(#136条件3・2026-10-11条件の変更) | a2型は第3証拠が無いと決まらない |
| J3 | 月題a1の`超`/`超え`(全エンジンが`え`付き=TTSが`こえ`と読んだ可能性)をユーザー試聴で確認 | C(現タスクと独立。R7『許容表を入れない』は維持) | ROOT_CAUSE_01 §5(c) |

# TRIAL_PLAN_02 KP-N5-EXTRACTION-ROOT-IMPROVEMENT-TRIAL-01 委任_02(事前登録v2・PREREGISTRATION、2026-10-31)

TRIAL_PLAN_01を、Opus条件Aレビュー(`OPUS_REVIEW_01.md`、M-1〜M-9・R-1〜R-10)とFable決定を反映して改訂した**有料実行前の事前登録**。本書commit後に有料実行する。**結果を見て基準・閾値・規則を動かさない**(感度分析は別表・判定に使わない=M-9)。原因=`ROOT_CAUSE_01.md`、案=`DESIGN_OPTIONS_01.md`。使用モデル=`gpt-6-luna`(B1/E1/E2/SEL/GEN5/rerank=Production既定=最新系)、VER5=`gemini-3.8-flash`、CHK5=`gpt-6.1-sol`(いずれもProduction既定のrouting。評価目的で旧/下位モデルは使わない)。

## 0. 位置づけ(M-1・M-8、改訂点)

- **層2は「特定の候補を足す問題」ではなく「cap 7内の順位付け基準の問題」**。cap 7は候補の奪い合いで、既存標本4件(R1×2・R2×2、`ev01/poolpick_untidi_b1b_L3_1.json:429-446`・`…_2.json:419-436`)のうち「`put away`系と`in the way`系が同一反復で両方残り、かつHR選定も残る」組合せは**0件**(R1はS1・S2とも`something in the way`が落ちる。R2はS1で`turn into an interrogation`が、S2で`something in the way`が落ちる)。層2の見込みはROOT_CAUSE/DESIGN_OPTIONSの「残る」記述より厳しい。
- 同順位内の並びは`pick`(`er138_kp_n5_generalization_01.py:950-962`)の安定sortでpool入力順(P7→LLM出力順)に依存する=昇格しても`in the way`(upper)が**LLMの出力順しだいで押し出される**。**主課題=「cap 7内の順位基準を、出現回数に頼らず、決定論的・安定にする」**。同順位の並べ方(入力順依存=R0 / 決定論的=R0d)を明示的に比較対象に入れる。
- 層1(抽出)の確度表記訂正(R-1): 「枠(件数)」と「指示文」はL1→L2→L3で同時に変わっており、確度は**中**(単独対照なし)。本Trialの2×2対照(§3-C)で分離する。
- 出現回数昇格(R2)は**主アームにしない**(M-2。§1・§8)。
- `ev01`のprobe台帳が呼出数より1件多い件(R-5)の**原因特定**: `ev01/cost_log_probe.jsonl`の`kp_n5_b1 / L3_2`が05:55:04(`output_tokens=6000`=`STAGE_PARAMS["b1"]["max_out"]`)と05:55:38(再試行)に2行ある=**JSON途切れ(出力上限到達)の1.6倍再試行**(`er138:802-836`の仕様どおり)。技術失敗・重複課金ではない。委任_01のSEL(40件)も`poolpick_untidi_b1b_L3_3`で`output_tokens=7000`(=sel max_out)に達してtimeoutで中断された。**SEL入力が増えると途切れが現実に起きる**=N7・R-3で実測する。

## 1. アーム(各アームの主規則・閾値は本書で固定=M-9)

層1の抽出方式(プール)×層2のpick規則。同一反復内の同一プールは**SELを1回だけ**実行し、同じSELラベルから各pick規則を再計算する(アーム間のSEL揺れを混ぜない)。

| Arm | 層1 | 層2 pick | 備考 |
|---|---|---|---|
| **A0** | 現行B1(Production `prompt_B1`、新規呼出、毎反復) | R0 | **ベースライン=同一反復の新規A0**(M-4)。fixture本番最終7件は参照欄のみ |
| A1 | E1: B1条件4・5を「難易度は問わない」に置換・30個 | R0 | |
| A2 | E2: 網羅列挙(難易度不問、上限40) | R0 | 層1のみ改善(層2が必要かの再確認) |
| A2d | E2 | **R0d**(決定論的な並び) | M-1: 並べ方のみの効果 |
| A4 | E2 | R1(chunk_type昇格、入力順tie=probeと同定義) | |
| A4d | E2 | R1d(R1+決定論tie) | |
| A8 | E2 | **R5**(予約枠、k=2固定、決定論tie) | R-9 P5 |
| A5 | E5: 辞書seed(LLM抽出0) | R0 | |
| A6' | E6差分: E2 ∪ (E5のうちE2に無い見出し語句のみ) | RR(rerank) | R-3 |
| **A7'** | E2 | **RR**(SEL無変更・keep済み候補を学習価値で並べ替える1 call) | R-2。SEL/GEN5/VER5/CHK5不変 |
| 参考A3 | E2 | body_recur_trial昇格(API 0) | **推奨候補にしない**(M-2)。集計名`body_recur_trial`はOPEN-632の`occ-v1`と**別物**(§2-5) |

- 抽出E3(句動詞pass)・E4(分割)は初回除外(probeで劣後。同方向微調整はしない)。A7(SEL value軸)は**外す**(SEL Prompt変更=N5本体変更。R-2)。
- E2/E1の呼出が失敗・途切れ(`N5TechnicalFailure`)した場合は**現行B1の結果へフォールバック**(空プール禁止、R-8)。フォールバックした反復は記録し、アームのS1/S3判定ではそのまま「達成せず」と数える(救済しない)。

## 2. 固定する規則

1. **プール構築=Production `pool_and_select`(`er138:1266-1294`)と同一順序(M-5)**: base(P7)→(B1/E1/E2/E5候補)`collect_pool(text, base, cands, gate_fn=make_b1_gate(units), defer_out=defer)`→`pool`→`select()`→deferred再判定`SEL_DEFERRED`→`pick`系。`units=er030.build_sentence_units(text)`(Productionと同じ)。`screen_fn`(Human NG/累積除外)は新規記事ではないので無し(documented difference)。**fixtureのP7(`cases.<id>.base`)は保存済みのQA通過後P7**(`er138:1271`コメント)で、Productionのcall1(QA前P7)と異なる=documented difference。補完P7は評価対象外。
2. **R0**=`n5.pick`そのもの(難易度advanced>upper>easy、tie=pool入力順)。**R0d**: キー=(難易度ランク, 起源[P7=0, 他=1], 本文中の最初の出現位置[文字index])。LLM出力順に依存しない。重複除去(span包含・display_form)は`n5.pick`と同じ。
3. **R1**: easy ∧ chunk_type∈{phrasal_verb, idiom} を1段昇格(R0同様 tie=入力順)。**R1d**: R1の昇格+R0dのtie。
4. **R5**: 上位5件=R0d順。残り**k=2**枠=未採用のkeep候補のうち easy のものを、chunk_type優先(phrasal_verb/idiom > fixed_phrase/collocation > その他)→R0d tie で最大2件。easyが2件に満たなければR0d順で補う。**k=2は実行前固定**(k=1,3は感度表のみ)。
5. **`body_recur_trial`(参考A3のみ。occ-v1と別物)**: span内の内容語lemmaを順序一致で本文の文内に探す件数。冠詞・`it/that/this/something/someone`等を除去して窓一致を取るため、`in the way`が`in a way`/`in any way`にも一致して**過大になる**(probe `pool_pick_probe_01.py:27-42`と同じ。M-2補足)。**厳密版`body_recur_strict`**(span語を除去せず連続一致、間に冠詞/代名詞1語のみ許容)も併記する。昇格=easy∧`body_recur_trial`≥3(**閾値は委任_01 probeで事後設定されたもの**=参考扱いの理由。判定に使わない)。
6. **RR(rerank)**: SEL無変更。keep済み候補(cls=C, keep=true)のみを入力。Prompt(表現名・出現回数・難易度を含まない価値中立文面): 「次は記事から選ばれた学習候補(ひと塊の表現)です。この記事を学ぶ英語学習者が、ひと塊で覚える価値の高い順に並べてください。基準: (a)構成語から意味・組合せが予測しにくい (b)辞書見出し・他の文脈でも使える汎用性 (c)記事の内容理解に関わる。易しい語でできていることを理由に順位を下げない。全候補を一度ずつ出す。」出力=`order`(id配列)。欠落idはR0d順で後ろに補う。呼出失敗はR0dへフォールバック(記録)。pickは`n5.pick`の重複除去を適用して上位7件。
7. **評価照合regex(評価script内のみ・Prompt/規則に表現名を含めない)**: `PUT_AWAY = \bput(?:ting)?(?:\s+(?:it|that|this|something|them|things))?\s+away\b`、`IN_THE_WAY = \bin the way\b`(大小無視)。項目のspanまたは(最終では)display_formのいずれかに一致。副次(報告のみ): `leave out`系`\b(leave|leaving|left)\b(?:\s+\w+){0,2}?\s+out\b`、`in sight`。
8. **最終候補の定義(M-3)**: pick→GEN5→VER5→CHK5(`n5.generalize_verify_check`、本番7件単位=**≤7件ずつのbatch**)通過後。API 0の既存QA(`er108` CMU `reasons_for_phrase`をdisplay_formへ、`enforce_max_words`)を通す。**通さない部分(documented limitation)**: er119 canonicalization QA(LLM、OPEN-633が`put away`系を下流で落としうる)、人称整合、presentable filter、Human NG。よって本Trialの「最終残存」は**CHK5通過後・下流QA前**であり、OPEN-633の影響は未測定。
9. **段階評価(費用管理・事前登録)**: pickレベルのS3(両表現同時残存、§4)は最終残存の必要条件(後段は落とすのみ)。Phase 1でpickレベルS3<7/8のアームは最終残存でも不合格が確定するため**GEN5/VER5/CHK5を実行しない**(A0は常に実行)。pickレベルを通ったアームのみ全反復でGEN/VER/CHK(同一(記事,span)はcache共有、7件単位batch)。

## 3. 実験設計

### A. 評価記事・反復(固定)
- 主評価: `untidi_b1b`(Family X、Advanced)×**N=5**、`untidi_a2`(X、Standard)×**N=3**(計8反復)。
- held-out(設計に不使用)各**N=2**: `surname_b1b`(Y、Adv)、`melos_a2`(Z、Std。`melos_b1b`はprobe使用済みで別本文)、`moon_b1b`(X、Adv)。Family出典は本文・題材の確認で**Y/Z/X**(surname=結婚姓の随想、melos=走れメロス、moon=月のしわ科学記事)。確認できないFamilyがあれば同Family内の別caseに差替え、逸脱として記録。
- 1反復=A0〜A8の全アームを同一本文・同一fixtureで実行(抽出3呼出B1/E1/E2とE5(API 0)→各プールをGate→SEL×5プール[A0/A1/E2/E5/E6差分]→RR×2[E2/E6]→各pick規則)。

### B. 実行規則
- N5Ctxはthread並列禁止(`er138:768-769`)=プロセス内は逐次。**2プロセス**(proc1=untidi_b1b系、proc2=untidi_a2+対照C)。300秒窓の起動≤2・150秒以上間隔。cost logはプロセス別file、`spent()`はglob合算、STOP sentinelは共通dir(`ev02/`)。費用guard: 合算>¥120の見込みで呼出前に停止。進捗は累計¥45/¥85で報告。

### C. 追加対照(Phase 1に同居。R-1・M-6)
- **2×2抽出対照**(untidi_b1b、各3回、B1と同じ`b1`段・SEL無し): X1=網羅列挙文面@14、X2=価値中立文面(L1)@40、X3=網羅列挙文面@40+重複回避文1行追加(「同じ語句や、一方が他方を含む類似語句は重ねない。」)、X4=L1文面@30から重複回避文を除去。`put away`系・`in the way`系・`leave out`系・`in sight`のhitを報告(判定外)。
- **同一プールSEL反復**(M-6、untidi_b1b rep1のA0プール・E2プールに対し**SELを追加2回=計3回**): 同一候補のcls・keep・difficulty一致率(ペア平均)を実測=N4の基準値。

## 4. 成功基準・副作用基準(固定。すべて満たしたアームのみ「最低達成条件を満たす」)

評価対象は主評価8反復(S1〜S3)。比較相手は**すべて同一反復の新規A0**(M-4)。

| ID | 基準 | 閾値 |
|---|---|---|
| S1 抽出(報告+必要条件) | プール(P7∪抽出∪Gate後)に各表現が存在 | 各表現 ≥7/8反復 |
| **S3 最終残存(主)** | **両表現(`put away`系・`in the way`系)が同一反復で同時に**CHK5通過後の最終7件に残る(表現別は報告のみ) | **≥7/8反復** |
| S2 意味 | S3で残った両表現のGEN5→VER5→CHK5結果: relationがSAME/MODIFIER_DROPPED_OK、gloss_jaが本文語義と一致(`put away`=しまう・片づける、`in the way`=邪魔になっている。担当者が本文を読んで確認) | 対象の100% |
| S4 一般化(価値) | **アーム名・新規/既存を伏せた混在リスト**(held-out+主評価の全入場項目+A0最終7件)をSELのT1〜T4基準(`er138:349-353`)で判定(判定者A=本実行担当者、第2判定者B=独立promptのLLM判定[§7手順]。一致率併記)。新規入場項目の価値率(YES/全件、UNSURE=非YES) | **≥ A0最終7件の価値率 − α、α=10pt** |
| N1 本文に無い表現 | 最終7件に本文一致しない項目 | 0件 |
| N2 易しい表現(相対) | 最終7件のうち easy ∧ `body_recur_trial`<3 ∧ chunk_type∈{fixed_phrase,collocation} の件数(1記事level・反復あたり平均) | アーム平均 ≤ A0平均 + 1.0 |
| N3 他KPの押し出し(相対) | (a) 同一反復A0最終7件のうちアーム最終7件に無い件数 (b) 公開HR選定(untidi: `turn into an interrogation`・`hear it out`。held-outは公開HR選定の記録が無いため**対象外**)の残存率 | (a)平均 ≤2件/level・反復 かつ (b)アーム残存率 ≥ 同一反復A0の残存率。2項目は個別報告 |
| N4 SEL安定性(相対) | A0プールとアームプールの共通候補のcls/keep一致率 | ≥ (§3-Cで実測した同一プール内cls/keep一致率) − 5pt。difficulty一致率も報告 |
| N5 意味不適切 | アーム最終7件の新規入場項目でrelationがSAME系でない項目(機能して除外された後) | 0件 |
| N6 費用・時間 | A0比の追加(抽出+SEL+rerank、serial合計) | ≤ +¥1.5/level、≤ +40秒/level |
| N7 retry負荷 | JSON途切れ再試行・技術失敗/呼出総数(stage別も記録) | ≤5% |

報告項目(判定外・R-7): 最終7件の難易度分布(A0との差)、Std/Advの差、タイトル由来句(`Now in Session`/`in session`/`left out again`)の混入率、`leave out`・`in sight`の最終残存(S5)、SEL入力件数・JSON途切れ・同一候補判定一致のE2/E6比較(R-3)、held-outの再現率代理指標(辞書見出しかつSEL C判定の語句が最終に入る率)、A0自身の最低達成条件達成率(R-8)、各アームの反復ごとの両表現残存表。

## 5. 判定規則(事前登録)

1. 全S/Nを満たす**出現回数を使わないアーム**(参考A3を除く)が1つ以上: **VALIDATED候補**(Production採用は別途ユーザー判断)。複数あれば、QCD(費用・時間・副作用)の総合でFableが比較するための表を提示し、**自分の推奨は「候補」と明記**(費用最小を自動で推奨しない)。
2. どれも満たさない: 失敗要因(S/N別)を分析し、**Phase 3**(工程構成の見直し。同方向の微調整の反復禁止)を同一委任内で実施。改善見込みが尽きたら次の3.へ。
3. 「出現回数を使わないアームでは最低達成条件を達成不能」と判明した場合は**REJECTEDにせず**、参考A3(`body_recur_trial`)の結果を添えて**USER_DECISION_REQUIRED**(出現回数の利用はTRIO原文:136「出現回数は…AIの候補抽出順位や品質判定には影響させない」・:186「候補の選定条件は変えない」を撤回・変更するユーザー判断が必要。§8)。
4. 基準の途中緩和は禁止。感度分析(R5のk、body_recurの閾値等)は別表・判定に使わない。

## 6. 費用見積(Cap ¥130、止め線¥120)

| 項目 | 見積 |
|---|---|
| 抽出(B1 0.18+E1 0.2+E2 0.32)×14反復 | ¥9.8 |
| SEL×5プール(0.27/0.30/0.50/0.40/0.60)×14反復 | ¥28.9 |
| rerank×2×14反復(約¥0.2) | ¥5.6 |
| 対照C(2×2 12呼出約¥3.5+同一プールSEL追加4回約¥2) | ¥5.5 |
| GEN5/VER5/CHK5(約¥0.55/件、distinct(記事,span)・cache共有・≤7件batch、段階評価で絞る): Phase 1 約2 level×15件、Phase 2は通過アームのみ約3 level×10件 | ¥17〜35 |
| 確認pass(推奨候補の最終7件そのまま、約¥4/level、最大3 level) | ¥12 |
| 第2判定者(LLM) | ¥1 |
| **合計** | **約¥80〜100**(Phase 3予備を含めCap ¥130) |

## 7. S4の判定手順(R-6)
1. 入場項目と対照の混在リストを固定seedでshuffleし、id・span・display_form・本文の文・訳のみ(アーム名・新規/既存・反復は伏せる)をJSONに出力。
2. 判定者A(本実行担当者)がSELのT1〜T4(辞書・置換・予測・理由)で各項目をYES/NO/UNSUREと理由1行で付け、**unblind前にファイルへ保存**。
3. 判定者B=独立したLLM呼出(判定のみ、keep・difficulty・アーム情報を渡さない。SELと異なる指示文、同じT1〜T4定義文)でYES/NO/UNSURE。A/B一致率を併記。
4. UNSURE・A/B不一致でアームのS4可否に影響する項目は「Fable裁定依頼リスト」にまとめて報告(Fableが読む)。

## 8. 承認済み仕様との差分一覧(R-10。採用時にユーザー判断が必要な点)

| # | 差分 | 根拠(承認済み仕様) | 関係するアーム | 採用に必要な判断 |
|---|---|---|---|---|
| (a) | B1条件4・5(上級者向け優先・易しい表現の除外)の置換/撤去、件数14→30/40、E2の網羅列挙文面(順位付けなし)への変更 | `er138:308-310`(`PROD_DIFFICULTY`、2026-10-22ユーザー指定逐語) | A1,A2,A2d,A4,A4d,A8,A7',A6' | ユーザー判断(承認済みB1文面の変更) |
| (b) | N5 pick順位規則の変更(同順位の決定論化R0d、型昇格R1/R1d、予約枠R5) | `er138:950-962`(2026-10-30承認のN5 pick) | A2d,A4,A4d,A8 | ユーザー判断(選定基準の変更) |
| (c) | rerank段の追加(SEL後・pick前の1 call。SEL/GEN5/VER5/CHK5は不変) | 新工程(承認済みN5に無い) | A7',A6' | ユーザー判断(新工程・費用+約¥0.2/level) |
| (d) | 本文の出現回数を順位付けに使う(参考A3のみ) | TRIO原文`docs/pm/delegation_log/2026-10-31_LEARNING-ITEM-QUALITY-TRIO-01_USER.md`:136「出現回数は…AIの候補抽出順位や品質判定には影響させない」・:186「候補の選定条件は変えない」 | 参考A3のみ(推奨候補にしない) | **R2採用時のみ、上記:136/:186の撤回・変更というユーザー判断が必須** |
| (e) | E5(辞書seed)の決定論工程追加 | 新工程(Prompt不変、`n5._wn()`資産の再利用) | A5,A6' | ユーザー判断(新工程) |

## 9. Production分離・限界・記録
- 全コードは`docs/research/KP-N5-EXTRACTION-ROOT-IMPROVEMENT-TRIAL-01/tools/`にあり、Production module(`er138`・`er105`・`er119`・`er030`・`er108`)を**import専用で読み取り**(無編集)。新規flag・設定dict・環境変数・起動script・`.env`は追加しない。`er119:505`の`n5_pool_fn`は使わない。終了時に`git diff --stat`でdocs配下+`OPEN_ITEMS.md`以外に差分が無いことを証明。Family A/B/Cは対象外。
- 限界: ①最終残存はCHK5通過後・下流QA(canonicalization QA/人称整合/presentable filter、OPEN-633)前 ②fixtureのP7はQA通過後 ③held-outに公開HR選定記録なし ④N=2〜8でLLM揺れの統計は粗い ⑤S4は担当者+LLMの判定でユーザー目視ではない。
- 記録: `OPEN_ITEMS.md` OPEN-635の更新。CURRENT_SPEC/DECISION_LOGは変更しない(採用判断まで)。

<!-- Opus条件Cレビュー(OPEN-517)の最終報告を逐語保存(親session transcriptのhand-back本文から機械抽出。行頭2文字のharness字下げのみ除去、他は無加工)。保存: JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_06、2026-10-25 -->
## OPEN-517 Opus独立レビュー(条件C)結果。管理ID JA-ASR-FALSE-NG-ROOT-CAUSE-01。読み取り専用で実施し、実行・編集はしていません

### 総合所見(先に結論)
- F1(READING_MATCHでPASSした転写にも最終ゲートを適用)は、方向として正しいです。仕様の正本である`CURRENT_SPEC.md:2855`と、ユーザー原文(DESIGN_01 3-11「保護すべき差異を…解放する仕様にはしない」)へコードを戻す是正です。
- ただし依頼文の前提には事実誤認があります(M-1)。skipは「Sonnetが実装時に独断で決めたもの」ではなく、承認済み設計文書に明記されています。
- F2(かな書き数詞の表記統一)の現行版v3には、値の違いを等価として見逃す経路を少なくとも2系統確認しました(M-2、M-3)。現行Production(無条件skip)より悪化することはありません。それでも、新しく作る最終ゲートに既知の穴を残したまま出すべきではありません。
- **Production適用への着手は条件付きで可能**です。条件はM-1〜M-5の解消です。いずれもAPI 0・費用0円で対応できます。

### 必須修正(M)

**M-1 skipの出自の訂正と、設計文書の上書き処理**
- skipの根拠は承認済み設計文書にあります。
  - `er058_output/unified_all_roles_production_wiring_01/DESIGN_02_ADDENDUM_01.md:65`に「最終ANDゲートは…承認済みのequivalence(HOMOPHONE…、Tier1 diff-anchored、**読み一致**)で既にPASSと確定した結果を再否定しない」とあります。
  - これは前回Opus条件Aレビュー(`OPUS_REVIEW_A_01_VERBATIM.md:43`)の推奨を、FableがOF-AUW-01として採用したものです。
  - `CURRENT_SPEC.md:2850`は、この追補を「正本設計(DESIGN_01と食い違う場合は追補を優先)」と位置づけています。
  - IMPLEMENTATION_02b:19は、この記述を実装しただけです。
- 前提を直す箇所: DESIGN_01の§1と「個別承認原文は未発見」という記述、ユーザーへの報告文。
- そのうえで、F1は次の整理で11-8の是正範囲内と判断します。
  - 不具合判定のT1に該当します(コードが`CURRENT_SPEC:2855`の「すべての採用転写を独立に再確認」と矛盾)。
  - F1は合格範囲を狭めるだけで、拡大を含みません。
  - 上位であるユーザー原文の方向へそろえる是正です。
- 適用時のSSOT作業: ADDENDUM L65から「読み一致」を外し、OPEN-517で上書きした旨を付記します。DECISION_LOGにも記録します。
- 背景として必ず併記すること: L65の元々の理由は「承認済み救済が値ガードで無効化される」(誤NGの防止)でした。F2はまさにこの誤NGへの手当てです。

**M-2 F2が「DIFFを解消」ではなく「DIFFを無害化」してしまう経路(弱いかな数詞)**
- `proto_value_gate_fix_03._replace_kana`は、`_cands`の読みをテキスト全体から位置に関係なく探します(`out.find(r)`)。
- `_cands(7,day)="なのか"`、`_cands(8,day)="ようか"`、`_cands(10,tsu)="とお"`は、Production値ガードが一般語との衝突(何なのか/しようか/通り)を理由に`KANA_NUMERALS`からわざと外した読みです(`er078_asr_value_guard_01.py:147-159`)。F2はこの衝突を復活させます。
- 具体例: 原稿「7日に…何なのか」、転写「8日に…何なのか」。
  - 現行の値ガードは7日と8日を対にしてDIFFと判定します。
  - F2を通すと、転写の「なのか」が「7日」に置き換わり、転写側のatomが[8日,7日]になります。8日は挿入扱いになり、原稿側の区間に「なのか」があるため`_drop_verdict_ja`がUNKNOWNを返します。
  - 最終ゲートはDIFFでしか止めないので、PASSになります。
- 必須修正は2点です。
  - (a)`WEAK_KANA_NUMERALS`にある読みを置換候補から除外する。
  - (b)単調性ガードを入れる。F2を通す前にDIFFだった結果が、F2の後にUNKNOWNやEQUALへ変わってよいのは、置換したspanが対応するpairだけ、とします。それ以外のpairの判定が変わる場合や、全体がDIFFからUNKNOWNへ変わる場合は、F2を通す前の結果を採用します。

**M-3 語の境界を見ていないことによる、別の値の取り違え**
- 置換候補が、より長いかな数詞の前半または後半に一致しても置換されます。
- 例(いずれも現行ではDIFFで、F2の後はEQUALになる見込み。机上トレースのみ、実行は未確認):

| 原稿 | 転写 | 誤って一致する部分 |
|---|---|---|
| 10人 | さんじゅうにん | 後半の「じゅうにん」 |
| 4日 | にじゅうよっか | 後半の「よっか」 |
| 百円 | にひゃくえん | 後半の「ひゃくえん」 |
| 十代 | にじゅうだい | 後半の「じゅうだい」 |
| 2時 | にじゅう… | 前半の「にじ」 |

- 前提条件(読みが一致していること)がある程度は防いでいます。しかし、その読み一致層が数値で信用できないこと自体がF1の存在理由です。F2は単体で安全である必要があります。
- 必須修正: 一致したかなの直前・直後がかな数詞の一部(数字の読み・位の読み・「ゅ」など)ではないことを確認する。または、そのかな列全体を最長一致でかな数詞として解析し、その値が相手のatomと一致する場合だけ置換する。上の表の例を負例testとして固定してください。

**M-4 適用範囲の指定方法**
- protoは「judge内で最初に呼ばれる`_protected`」という呼出回数で、F2の適用範囲を決めています。
- Productionでは`_protected`(またはvalue guard)に明示的な引数(例: `kana_unify=True`)を渡し、READING_MATCHでPASSしたPrimaryの最終ゲートだけで有効にしてください。
- 次の2点をtestで固定してください。
  - 否定差の判定(`negation_diff`)は、置換前の元テキストで行う。
  - Primary NG(P1)とSecondaryのゲートでは、F2は無効。

**M-5 F2の安全性を確かめる負例testの事前登録**
- 現行のコーパスには、F2を緩める方向へ誤らせる例(衝突・境界・弱い読み・連濁や音便の誤読)が入っていません。
- 適用前に、M-2・M-3の例と次のケースを合成した単体test一式を基準7として事前登録し、全件がPASS以外になることを合格条件にしてください。
  - 誤った音便・連濁の読み(例: 「さんほん」は`_cands`にない)
  - 同じ値のatomが並ぶ文
  - 否定語のすぐ近くに数詞がある文

### 推奨(R)
- **R-1(未知データでの検証。Q3)**: v1→v3を同じコーパスで作り直したため、過学習の懸念は実在します。必要十分な範囲はAPI 0で済みます。
  - (a)コーパス凍結後に作られた、または評価に使っていない保存済みJA judge監査(X/Z/Yの直近run、legacy A/B/C)をそのまま再評価し、F1またはF2で判定が変わった全件を目で確認する。
  - (b)M-5の合成負例。
  - 有料のlive runは、適用前には不要と考えます。
- **R-2(過去の公開物の確認。Q4)**: 公開済みの再生成など、遡って直すことはしない前提で妥当です。ただ、監査recordは最終ゲートをskipしたときでも`value_guard.primary`の判定を記録しています(`er078_asr_unified_judge_01.py:510`、skipは:530)。
  - そのため、過去run dirで「`skipped=approved_equivalence:READING_MATCH`かつ値ガード=DIFF」の件をAPI 0で抽出できます。
  - 公開物に該当があれば、それは品質問題なのでユーザーへ報告します。遡って直すかどうかはユーザー判断です。
- **R-3(運用影響。Q4)**: NG_PROTECTEDになるとSecondaryを呼ばずに次の再生成へ進みます。このため、F2の表に漏れがあり、ASRが毎回同じ書き方をする場合は、そのsegmentが3回ともNGになり、Azureでの救済なしにHR Lockへ直行します。
  - 適用後の初回runでは、「reason=final_gate_value_diff かつ basis=READING_MATCH」の件数と、HR Lock到達数を集計して報告してください。
  - 421件で増加0という実測は妥当な根拠ですが、母集団が限られています。
- **R-4**: `一分↔いちふん`のDEMOTE判定はSecondaryをstubにした結果です。実運用ではAzureが「1分」と書けばPASS_WITH_WARNINGで通ります。読みの誤りが残る可能性として開示してください。
- **R-5(適用手順の抜け。Q5)**:
  - `READING_RESOLVED_MATCH`(LLM resolver)と、Candidate Eから出るPHONETIC_MATCHのbasis別test。評価で通ったかは未確認です。
  - `force_secondary=True`経路では、最終ゲートでNGになると、以前と違いSecondaryより前に止まります。そのtest。
  - `_ortho_unlock_primary`がREADING_MATCHではNoneを返すことのtest。
  - reason文字列が`primary_pass_approved_equivalence:READING_MATCH`から`primary_pass`に変わることによる下流(集計・Grep・allowlist・静的監査)への影響確認。参照先は未確認です。
  - `er007_ja_secondary_asr_01.py:407`のコメント修正。
  - 1行で戻せるrollback用のmodule定数(env/flagにはしない)。
- **R-6**: 期待読み表を移設するときは、parity testに「弱い読みを除外したこと」も含め、er066との差分を意図した差分として固定してください。
- **R-7(「晩」など助数詞表にない語。Q2)**: 今回の是正には含めないでください。助数詞表(`COUNTERS`)に追加するとProduction値ガードが全経路(P1・Secondary・EN以外の全Family)で変わり、範囲が広がります。「UNKNOWNは最終ゲートを通す」という5値の意味は承認済みです。別OPENとして登録してください(分類=既知の限界、次アクション=影響調査)。

### 問題なし確認(C)
- **C-1**: F1の分岐は、既存の非承認PASSと同じ(`:538-553`)です。他の3つの承認根拠(HOMOPHONE_MATCH_NUMBER_EXCEPTION/TIER1_DIFF_ANCHORED/TIER1_NUMERIC_EQUIVALENCE)は値を考慮した根拠なので、skipを維持してよいです。値に無関係な根拠はREADING_MATCHだけです。
- **C-2**: F1+F2のPASS集合は現行PASSの部分集合です(現行のREADING_MATCH PASSは無条件に通っている)。現行Productionに対して緩める方向の回帰は、構造的に起きません。M-2・M-3は保護の穴であって、回帰ではありません。
- **C-3**: Q5の警告3件(みっかかん/しがつ/しちがつがPASS→PASS_WITH_WARNINGになる件)は残してよいです。既存の`_compare_pair`も、不規則読みで表記が違えば警告します(ふたり↔二人など)。慣例と一致しており、件数も少ないためです。外す場合は、既存の警告慣例全体と一緒に別途判断してください。
- **C-4**: 否定差はF2の影響を受けません(protoは`negation_diff`を元テキストで計算)。ただしProductionでのtest固定が条件です(M-4)。
- **C-5**: 決定性、API 0、非READING_MATCH経路の変化0、NG→PASS 0、警告喪失0の基準と結果に問題はありません。
- **C-6**: N3-07(Candidate E)はOPEN-333、同形異音・助詞の誤読は既知の限界として範囲外とする整理で妥当です。

### Q6 事前登録基準の過不足
- **不足**:
  - F2が誤って緩める方向に働かないかの負例基準(M-5)
  - 未知データ(R-1)
  - F2が統一を実行した全件の一覧と、値が同一であることの確認(正常143件で何件発動したか)
  - DEMOTE件はSecondaryの結果次第であることの明記(R-4)
- **過剰**: なし。§1のF2の定義はv1のままなので、v3の定義に更新してください。

### ユーザー確認が必要と考える点
- **F1の採否**: ユーザー承認は必須ではないと判断します。11-8の不具合判定T1に該当し、合格範囲を狭める方向で、上位のユーザー原文へそろえるためです。ただし報告は必須です。報告では次の3点を明示してください。
  - 承認済み設計の追補L65と矛盾していたこと
  - 前回Opusの推奨を、今回のOpusが撤回する方向であること
  - PASS→NGによる再生成とHR Lockの増加リスク(R-3)
- **Fableの判断次第でユーザー判断になる場合**: Fableが追補L65を「ユーザー承認済み仕様」と判断するなら、仕様側を変更することになり、ユーザー判断事項です。追補の承認時期と承認の範囲は未確認なので、Fableが照合してください。
- **過去の公開物**: R-2で公開物に該当が出た場合、その扱いはユーザー判断です。
- **F2**: ユーザー判断は不要です。是正に必要な技術部分です。

### 関連ファイル
- C:\Users\tensh\eigo-radio\er058_output\unified_all_roles_production_wiring_01\DESIGN_02_ADDENDUM_01.md(L65)
- C:\Users\tensh\eigo-radio\er058_output\unified_all_roles_production_wiring_01\OPUS_REVIEW_A_01_VERBATIM.md(L43)
- C:\Users\tensh\eigo-radio\CURRENT_SPEC.md(L2850, L2855)
- C:\Users\tensh\eigo-radio\docs\research\JA-ASR-FALSE-NG-ROOT-CAUSE-01\proto_value_gate_fix_03.py(`_replace_kana` L26-50、呼出回数で範囲を決める処理 L113-117)
- C:\Users\tensh\eigo-radio\er078_asr_value_guard_01.py(L147-159 KANA_NUMERALS/WEAK_KANA_NUMERALS、L420-427 `_drop_verdict_ja`)
- C:\Users\tensh\eigo-radio\er078_asr_unified_judge_01.py(L68-73, L509-559)
- C:\Users\tensh\eigo-radio\er066_ja_asr_orthographic_equivalence_01_trial.py(L186-279 `_cands`)
- C:\Users\tensh\eigo-radio\docs\pm\PM_GOVERNANCE.md(11-8、L2549-2561)

MARKER: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_30 (2026-10-24, Fable→sonnet-worker)

# 管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_30(課題①: Opus条件Cレビュー[OPUS_REVIEW_08]の必須修正OF-KP2-01〜08のうちAPI 0で進められる準備を全て実施。有料の補強検証(約15〜20円)は案件累計が7-7の300円を超えるためユーザー承認後=次委任)

## 0. Fable判断
- OPUS_REVIEW_08(§Zに逐語。**最初に** `docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/OPUS_REVIEW_08.md` へ逐語保存)の判定「採用提案の前に追加検証が必要」を採用。X2pはVALIDATEDとせず「VALIDATED候補(補強検証待ち)」。
- 本委任はAPI 0。Production変更0。DEV er112のみ。並行の委任_27(er105/er003 test)と衝突しないよう、`er003_key_words_gloss_alignment.py` は読むだけ。

## 1. 作業(すべて0円)
 A. **OF-KP2-02(a) X2p' Prompt**: X2pに「本文で使われている語義・用法(字義か比喩か)を選ぶ。ただしglossが表すのはkey_phraseの範囲だけ。本文側の否定・主語・時制・具体的な対象・場面は持ち込まない」と、partly/no分岐の「この語義に日本語の定訳(例: サプライチェーン、つじつまが合う)があればそれを優先し、無い場合だけ言い換える」を追加(修正は1回のみ、`TRIAL_DESIGN_07.md` に差分)。
 B. **OF-KP2-01(b) 新hard-core KPの事前固定**: 設計に使っていないKPを結果非依存の基準で6〜10件(held-out未使用4件[`feel borrowed`等]+Z小説から事前基準で抽出)。選定script・基準・IDを `TRIAL_05/HARDCORE_HELDOUT_02.md` に固定(出力は見ない)。
 C. **OF-KP2-02(c) 本番構成harness**: Stage 2の54KPを「1記事levelの全KPを1 call、`rules_fulltext`、新developer message、`prior` 再提示あり」で回せるDEV harnessを `er112_kp_gm_trial_06.py` に実装(実行はしない。`--cap 0` のdry-runでjob数・見積[KP単価ベース]を出す)。費用見積(B0/X2p'各1rep)を `BUDGET_PLAN_T6_01.md` に。
 D. **OF-KP2-03(d) 二重判定の準備**: 変化した文字列(Stage 2の35件+R/held-out)を「範囲を超えた持ち込み=THIN」の明示基準付き盲検表 `fable_blind_06.md`(Key別)に整形(第二評価者=Opus/新contextのFable用)。`add up`→「つじつまが合わない」(否定の持ち込み疑い)と `reach for someone's wallet`(過去のユーザー判断「見出し語忠実でPASS」との整合)を再照合対象として明示。
 E. **OF-KP2-04/05/06 配線設計の更新** `WIRING_DESIGN_07.md`: 混在batchは2 call分割(null itemは新builder、glossありは旧builder)、方式P'(`str`継承型で新経路情報を持たせ `make_alignment_fn` がschema/developer messageを切替、Promptにマーカーを入れない)、Trialの `build_x_message` とのgolden一致test(差分=prior/rules_fulltext/マーカー無し)、新経路messageが旧schemaで呼ばれたらINVALIDで安全停止(WC-07)、撤退手段=単一commitの `git revert`(`EIGO_KP_GLOSS_ALIGNMENT` OFFは本番停止であり撤退手段ではないと明記)、新経路validatorに記録のみの持ち込み検出(KPに否定が無いのにglossに否定/文末「た」等)、Z repairは非適用+repair件数とgloss変化の監視項目1つ、監視指標(align費用0.6円/記事セット超・level 60秒超)の基準見直し計画。
 F. **OF-KP2-07/08 資料の修正** `ADOPTION_PROPOSAL_02.md`(草案): 単価見積をKP単位(約+0.05円/KP×10KP≒+0.5円/記事セット、実測で確定)に修正、hard-core型の本番発生率(過去Production KPのcanonicalization reasoningから比喩認識の割合を集計、0円)と通常KPへの持ち込み率(6/54)の比較、wallet判断との整合、設計原則の案「本文での語義を選び、表すのはkey_phraseの範囲だけ」、ユーザー選択肢3案(Opus案)。
 G. **費用の事実**: 案件累計(台帳)を正確に集計し、補強検証(b)(c)(e)の見積(約15〜20円)を足すと300円を超えることを `BUDGET_PLAN_T6_01.md` に明記(Fableがユーザーへ提示)。
 H. 記録: OPEN-474へ1行(Opus条件C結果・VALIDATED候補・補強検証はユーザー予算承認待ち)、DECISION_LOG(Fable判断)。`docs/pm/USER_DECISION_REGISTER_01.md` に **UDR #178**(新規・未回答・USER_DECISION_REQUIRED・非blocking)を登録: 件名=Key Phrase課題① 補強検証の費用承認(案件累計300円枠の超過)。状況=X2p VALIDATED候補、Opus条件C「追加検証が先」。選択肢=(A)補強検証を承認(KP案件上限を300→350円へ、約20円使用見込み)/(B)現状で打切り(字義訳は残る)/(C)現状のX2pで採否判断に進む(Opus非推奨)。推奨=A。
 I. 委任文逐語保存 `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-24_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_委任_30.md`(先頭MARKER一致、0始まり)。commit前に `git status` でindex確認→`git commit --only -- <paths>`(`git add -A/-u/-f/-N`禁止、secret grep 0件)→`git push origin HEAD:main`。報告 `docs/pm/RESULT_PACKET_KPGM30.md`(各項目の成果物、費用集計、4行、判定整合行)。

## §Z OPUS_REVIEW_08(逐語保存用)
# OPUS_REVIEW_08: 課題① X2p 採用提案前の独立レビュー(条件C)

## 判定
**採用提案の前に追加検証が必要です。** ユーザーへ「VALIDATED(検証済み)」として出すにはまだ足りません。
- 方向性(gloss生成の前に、本文での意味を確定させる段を同じcall内に置く)は妥当です。
- ただし、狙った不具合(字義訳)が直ったことを示す証拠は、ほぼ設計に使ったKPの上でしか取れていません。加えて、通常KPに「本文の文脈を持ち込む」副作用が系統的に出ています。
- 補強は小さく済みます。Prompt修正1回とProduction構成での再検証で、費用は約15〜20円、AI自律の範囲(承認済みScope内・300円以下)です。
- 下記OF-KP2-01〜08を満たせば、採用提案へ進んでよいと考えます。

## 論点1: VALIDATEDと言えるか → まだ言えない
1. **効果の証拠が設計用のデータに偏っている(最大の不足)**
   - X2pの規則は、R hard-core 4KPの結果を見てから足されました。そのため R hard-core の FAIL系 10/12→0/12 は、設計に使ったデータでの成績です。
   - 設計に使っていないデータには、狙った型の失敗がほとんど含まれていません。held-out(本番に近い未使用KPの検証)ではB0のFAIL系がもともと0でした。Stage 2で改善したのは FAIL→PASS の2件だけです。
   - しかもそのうち `reach for someone's wallet` の B0「人の財布に手を伸ばす」は、FABLE_BLIND_RESULT_05の注記で「見出し語忠実でPASS(ユーザー判断済み)」とされています。改善1件の根拠が過去のユーザー判断と食い違うため、照合が要ります。
2. **Stage 2の基準適合は上限ぎりぎりで、余裕がない**
   - PASS→THIN は2件で、基準の上限ちょうどです。
   - `add up`→「つじつまが合わない」がPASSとされていますが、学習カード上は「add up = 合わない」となり、意味が逆になります。否定は見出し語の外(doesn't)にあります。現行規則「key_phrase全体の意味に過不足なく」に照らすと、少なくともTHINです。
   - Fable判定の揺れ7/10はすべて緩い方向でした。厳しく数え直すと、Stage 2基準(PASS→THIN≦2)を超える可能性があります。
3. **事後に決めた基準と規則の扱い**
   - gating基準の是正: 元の(3)「THIN≦B0+1」はB0がFAIL中心だと機能しないので、是正自体は合理的です。開示で足ります。
   - X2pの規則追加: 事後調整なので、開示だけでは足りません。設計に使っていないhard-core KPでの再確認が必要です。
4. **本番構成で未検証**
   - Trialは1 call平均1.9KP(最大3KP)でした。Productionの`align_glosses`は、1 levelの全対象(全文選定なら5件前後)を1 callにまとめます。
   - 5件同時+新しい3欄での品質・token数・所要時間は未測定です。
   - `rules_fulltext`(Productionが使う規則)と `prior` 再提示を含めた実測もありません。
5. **判断材料の欠落**
   - hard-core型(新造比喩)が本番のKPに占める割合が示されていません。
   - 一方、通常KPでは35/54の文字列が変わり、文脈の持ち込みが少なくとも6/54(THIN 2件+PASSのうち持ち込みが見える4件)あります。
   - 発生率の比較がないと、本番全体で品質が上がるのか下がるのかを判断できません。

**最小の補強案(約15〜20円、所要数時間)**
- (a) Prompt修正(X2p'、修正は1回のみ)
  - 範囲の規則を追加します。「本文で使われている語義・用法(字義か比喩か)を選ぶ。ただしglossが表すのはkey_phraseの範囲だけ。本文側の否定・主語・時制・具体的な対象・場面は持ち込まない」。
  - partly/no の分岐で「このkey_phraseのこの語義に日本語の定訳(サプライチェーン、つじつまが合う等)があればそれを優先し、無い場合だけ言い換える」とします。
- (b) 設計に使っていない新しいhard-core KPを6〜10件集め、B0とX2p'を各2rep以上で比べます。
  - 候補: held-outの未使用4件(`feel borrowed` 等)と、Z小説から事前基準で抽出したもの。
  - B0の失敗で選ぶ場合は、比較用のB0を新たに取り直します。
- (c) Stage 2の54KPを、本番構成(1記事levelの全KPを1 call、`rules_fulltext`、新developer message)でB0/X2p'各1rep。約11円。
- (d) 変化した文字列を、別の評価者(Opus、または新しいcontextのFableによる盲検。API 0)が「範囲を超えた持ち込み=THIN」という明示基準で二重判定し、一致率を出します。
- (e) 本番構成でcall単価・出力token・所要時間を実測します。

## 論点2: 副作用
- **仕組み上、量産すれば増えます。** Stage 2の `naive_ja_conveys`(単語置換訳で意味が伝わるか)は yes 7 / partly 8 / no 39 でした。通常KPの大半が言い換え分岐に入るため、「yesなら定訳」という歯止めがほとんど働いていません。
  - 原因は、単語置換訳(supply chain→供給の鎖)が複合語・句動詞でほぼ必ず「no」になる設計です。
  - 当初心配した「yesが多すぎて形骸化する」とは逆の偏りで、本文の意味(meaning_in_text_en)をそのまま訳す方向へ流れます。補強案(a)の「定訳優先」がこれへの対策です。
- `X_HEAD` は「この記事だけの出来事は入れない」と既に指示しています。それでも「売れ行きは逆に下がった」が出るので、指示だけでは守られていません。
  - 補助として、新経路のvalidatorに記録のみ(合否に使わない)の検出を推奨します。KPに not/n't/no/never が無いのにglossに否定がある、文末が過去形「た」で終わる、など。
- 文字数比>1.5(7/54)は短いglossでは指標として弱いので、上の持ち込み検出の方が有効です。
- **Cp_t4との比較**: 単価はほぼ同じで、通常KPではCp_t4が良く(53/1)、hard-coreではX2pが良い(FAIL系0対2)です。「Cp+X2pを yes/no で接続」は2 call分の費用がかかり不利です。X2p'で通常KPの持ち込みを抑えるのが最も安い道です。Cp最適化版は、X2p'が補強検証で不合格だった場合の次案とします。

## 論点3: 設計原則の変更
- 「単体で再利用できる訳」か「本文での意味」かの二択でユーザーに出すのは、切り方が粗すぎます。前者を捨てると `add up`→「合わない」のような見出し語の範囲を超えた訳まで許してしまいます。
- 推奨する原則は「**本文での語義を選び、表すのはkey_phraseの範囲だけ**」です。新造比喩はもともと再利用できる訳が無いので「指す意味」を書き、通常表現は従来どおり再利用できる訳が残ります。
- 過去のユーザー判断(wallet「見出し語忠実でPASS」)と矛盾しないかを確認し、提示資料に明記してください(Charter 8)。
- 変更後は、旧builderの「単体で再利用できる訳」の句がZ repair・混在batch・A/B/Cに残り、本番に2つの原則が並びます。CURRENT_SPECには適用範囲つきで書く必要があります。

## 論点4: 配線設計(WIRING_DESIGN_06)
- **既存builder・schemaを一字も変えない方式**: 妥当です。既存側のbyte一致はWC-01で担保できます。
  - 加えて、新builderの出力がTrialの `build_x_message("X2p")` と一致すること(差分は prior・rules_fulltext・マーカーだけ)をgolden testで確認してください。テストした組み合わせ以外を本番に出さないためです。
- **混在batch(要修正)**: 「call全体を現行builderに戻し、記録のみ」は、未生成(null)のitemを黙って字義訳しやすい旧Promptで書くことになり、今回直したい不具合そのものが戻ります。
  - TRIAL_DESIGN_06 §3-1の第1案(null itemは新builder、glossありitemは旧builderの2 callに分ける)を推奨します。追加費用は混在が起きた記事だけです。
  - 起きうる場面: 再実行時に `is_person_generalized` で、既に人が確定したglossを持つitemが対象に入るケース。
- **方式P対Q**: Pの欠点は、マーカーがPromptに混入する(Trialと文面がずれる)ことと、暗黙の結合です。
  - 推奨はP'です。マーカー文字列の代わりに、`str` を継承した型に「新経路」という情報を持たせ、`make_alignment_fn` がその型を見てschema・developer messageを切り替えます。factory契約は変わらず、Promptに余計な文字列も入りません。
  - 新経路のmessageなのに旧schemaで呼ばれた場合は、新欄が欠けてINVALIDになり、安全側に止まります(WC-07で固定)。
- **flag**: 新しいflagを置かないことには同意します。ただし「`EIGO_KP_GLOSS_ALIGNMENT` OFF が撤退手段」という説明は不正確です。全文選定ではglossが未生成のまま安全側に止まる(本番停止)ので、元に戻る手段ではありません。実際の撤退手段は単一commitの`git revert`だと明記してください。
- **prior再提示の追加**: Trialで使っていない差分です。WC-06とruntime evidenceで確認してください。
- **`rules` と `rules_fulltext`**: 配線後のruntime evidenceまで待たず、補強案(c)で事前に測ってください。
- **監視指標**: 既存の記録のみの指標「align費用0.6円/記事セット超」「level単位所要60秒超」は、X2pでは常時発火する見込みです。実測後に基準を引き直すか、事前に整理してください(SSOT記載あり)。

## 論点5: Z repair
- 非適用の推奨は妥当です。repairは人称の修復が目的で、旧builderの手順2(一致していれば書き換えない)が働くため、字義寄りへ書き戻すリスクは低いと見ます。
- repairされたitemの件数と、gloss変化の有無を記録・監視する項目を1つ足すだけで十分です。repairに意味欄を足す案は今回は不要です。

## 論点6: X/Y/Z・量産
- 共通moduleで一括適用し、YのTrialに自動で波及するのは妥当です(Yは `PRODUCTION_WIRED` と呼ばない)。
- **単価見積りは修正が必要です。** 1 callあたりの増分(約+0.10円)は、1.9KP/callのTrialでの値です。本番は1 call 5件程度で、増分の大半は出力token(KP数に比例)です。
  - 試算: KP 1件あたり約+0.05円 × 10KP/記事セット ≈ **+0.5円/記事セット**(70円の約0.7%)。資料の+0.1〜0.3円は過小です。
  - 所要時間も、1 levelあたり数十秒増える可能性があります。
  - 補強案(e)の実測値で書き直してください。

## 必須修正(OF-KP2)
- **OF-KP2-01**: 設計に使っていない新しいhard-core KPで効果を再確認する(補強案b)。
- **OF-KP2-02**: 範囲の規則と定訳優先を加えたX2p'で、Stage 2を本番構成で再検証する(補強案a・c)。
- **OF-KP2-03**: 二人目の盲検評価者で判定を確認する(補強案d)。`add up`、wallet の評価を再照合する。
- **OF-KP2-04**: 混在batchを2 callに分ける(または、未生成itemを旧builderに回さない)。
- **OF-KP2-05**: 方式P'(型に新経路の情報を持たせる、Promptにマーカーを入れない)を採り、Trialとのgolden一致testを加える。
- **OF-KP2-06**: 撤退手段は `git revert` と明記する(kill switch OFF は本番停止)。
- **OF-KP2-07**: 単価・所要時間を本番構成の実測で書き直し、監視指標の基準を整理する。
- **OF-KP2-08**: ユーザー提示資料に、hard-core型の発生率と通常KPへの持ち込み率の比較、および過去のwallet判断との整合を載せる。

## ユーザーへ提示する選択肢案(補強検証の後)
1. **(推奨)** 原則「本文での語義を選び、表すのはkey_phraseの範囲だけ」+X2p'を、X/Zの新規生成glossへ配線する。Z repair・A/B/Cは現行のまま。単価は実測値(+約0.5円/記事セット見込み)。
2. 現行のまま(原則も変えない)。新造比喩の字義訳は残ることを受け入れる。追加費用0。
3. 文脈の持ち込みを許容する「本文での意味」原則+X2pをそのまま採用。通常KPの言い換え増加と再利用性の低下を受け入れる。非推奨。

## 読んだファイル
- OPUS_REVIEW_REQUEST_08、ADOPTION_PROPOSAL_01、WIRING_DESIGN_06、TRIAL_DESIGN_06(全文)、TRIAL_05/TRIAL_RESULT_05、TRIAL_05/FABLE_BLIND_RESULT_05、TRIAL_05/report_05_fable_labels_05_withcde(Grep)
- er112_kp_gm_trial_05.py(:95-234)、er003_key_words_gloss_alignment.py(:255-354, :390-446, :560-855)、CURRENT_SPEC.md(:1970-1979, :2785-2793)
未読: er026_family_z_fiction_production_runner_01.py:1552、ROOT_CAUSE_04、OPUS_REVIEW_07。
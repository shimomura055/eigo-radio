# TRIAL_RESULT_05 確定版(委任_29、2026-10-24。課題① 字義訳 Trial_05: Stage 1 + held-out + Stage 2 の全ラベル確定後の集計。**VALIDATED判定はFable。本書は事実のみ**)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_29 / 実行=`er112_kp_gm_trial_05.py`(DEV専用、Production module編集0) / 集計=`er112_kp_gm_trial_05_report.py report --labels fable_labels_05.json --labels_c fable_labels_05c.json --labels_d fable_labels_05d.json --labels_e fable_labels_05e.json`(出力=`report_05_fable_labels_05_withcde.md`、委任_29で`--labels_e`とStage 2表を追加) / ラベル=`fable_labels_05*.json`(Key未開封で確定、注記逐語=`FABLE_BLIND_RESULT_05.md`) / 使用モデル: `gpt-6-luna` effort=high(最新世代の最上位系ではない。理由=評価対象がluna生成の品質そのもの[Production系列と同一条件、25節の例外]。判定=Fable盲検、API 0)。1 rep、Fable単独評価、Sonnet Judgeなし。

## A. 確定サマリ(X2p = 採用候補。X2 = 前版[THIN 4]、Cp = 検出方式の生成転用)
| 段 | B0(現行Production Prompt) | X2p |
|---|---|---|
| Stage 1 R hard-core(4KP x 3rep = 12出力) | PASS 2 / THIN 0 / **FAIL系 10**(2rep以上失敗: unseen clock・trophy・greener grass) | PASS 11 / THIN 1 / **FAIL系 0**(2rep以上失敗KPなし) |
| R co-KP(3KP x 3rep = 9出力) | 9/9 PASS | PASS 8 / THIN 1(`sound no one asked for` rep1「誰も聞きたくない音」) |
| held-out(10KP x 1rep) | PASS 8 / THIN 2 | PASS 9 / THIN 1。**B0=PASSからの悪化 0**(`a door inside the pain`はB0もTHIN) |
| Stage 2 non-R 54KP(1rep) | Trial_04 B0 2rep: 出力108中 PASS 105 / THIN 1 / FAIL 2 | PASS 52 / THIN 2 / FAIL 0 |
| 全85出力(X2p) | - | PASS 80 / THIN 5 / FAIL系 0。validate互換 85/85。`gloss==naive_ja` 0/85 |
- R(hard-core)の他arm: M 6/0/6、X1 7/0/5、X2 8/4/0、Cp 9/1/2(PASS/THIN/FAIL系)。Cp_t4(Trial_04のrep1、n=4)は3/1/0。H5(X1対M)はFAIL系 6→5で有意差なし。
- 注意(委任_26記載の訂正): 委任_26追記の「X2p R co-KP悪化なし」は不正確。co-KP `sound no one asked for` rep1が X2p=THIN(B0=PASS)。同文字列はX2でも THIN(`FABLE_BLIND_RESULT_05.md`)。

## B. Stage 2 確定(non-R 54KP x X2p 1rep、対 B0 = Trial_04 の2rep)
05eラベル(21文字列: PASS 20 / THIN 1)を加え、54KP全件にラベル確定(未ラベル 0)。
| 基準 | PASS→FAIL | PASS→THIN | THIN→FAIL | THIN→PASS | FAIL→PASS | FAIL→THIN | 変化なし | 計 |
|---|---|---|---|---|---|---|---|---|
| **strict**(B0の良い方のrep基準) | **0** | **2** | 0 | 0 | 0 | 0 | 52 | 54 |
| lenient(B0の悪い方のrep基準) | 0 | 2 | 0 | 1 | 2 | 0 | 49 | 54 |
- PASS→THIN(strict/lenient共通 2件): (1) `move in the other direction`: B0「反対の方向に動く」(2rep とも PASS) → X2p「売れ行きは逆に下がった」(THIN。Fable注記: 本文の文脈を補った説明でフレーズの意味より狭く、方向まで断定)。(2) `supply chain`: B0「商品が作られて消費者に届くまでの流れ」/「…届くまでの供給の流れ」(PASS/PASS) → X2p「商品が作られて店に届くまでの流れ」(THIN。同文字列はCp_t4でも THIN)。
- lenient追加(改善側): THIN→PASS 1(`pump one's fist` B0悪い方「自分の拳を突き上げる」THIN → X2p「喜んでガッツポーズをする」PASS)、FAIL→PASS 2(`reach for someone's wallet` B0「人の財布に手を伸ばす」FAIL → X2p「財布を出してお金を払おうとする」PASS、`settle at` B0悪い方「～で落ち着く」FAIL → X2p「～で取引を終える」PASS)。
- **事前宣言基準**(`TRIAL_DESIGN_06.md` §4 Stage 2: strict PASS→FAIL 0 かつ PASS→THIN ≦2/57[実際の母数は54])との適合(事実): PASS→FAIL=**0**(基準0に適合)、PASS→THIN=**2**(基準≦2に適合、上限ちょうど)。母数は設計の57ではなく54(Stage 2の確定KP数)。
- Cp_t4(rep1、n=54)との比較: Cp_t4 は PASS 53 / THIN 1(`supply chain`)。X2p が Cp_t4 より劣る(順位)KPは 1(`move in the other direction`: Cp_t4「逆の動きをする」PASS)、優る KP は 0。
- 決定論集計(`metrics_05.md`、54KP): `gloss==naive_ja` 0/54、文字数比>1.5(対B0 2rep平均) 7/54、説明文型語尾または30字超 0/54、B0のいずれかのrepと同一文字列 19/54(=35/54は文字列が変化し、変化後もstrict基準でPASS以上は52KP中の該当分)、conveys yes/partly/no = 7/8/39。
- 観察(判定ではない): 本文の用法に寄せた結果、否定・対象・場面が見出し語より具体になった PASS 文字列がある(`add up`→「つじつまが合わない」[本文は doesn't add up]、`step out`→「人が姿を現す」、`run on`→「別々の時間軸で動いている」、`carry the load`→「必要な荷物を運ぶ役目を担う」)。Fableの水準は「本文での意味」側(PASS)で、`ROOT_CAUSE_04.md` 0-R の「単体で再利用できる訳」との両立不能の設計トレードオフ(承認事項)に当たる。

## C. Before/After 代表例(B0文字列 → X2p文字列 / X2pのFableラベル)
| KP(種別) | B0 | X2p | X2pラベル |
|---|---|---|---|
| draw a line(R hard-core) | 一線を引く / 線を引く(rep3 FAIL_LIT) | はっきりと区別する / 違いをはっきり示す / 区別をはっきりさせる | PASS x3 |
| an unseen clock(R) | 目に見えない時計(3rep全て FAIL_LIT) | 値札に隠れた独自のタイミング / 値札に隠れた時間のずれ / 表には見えない独自のタイミング | PASS / **THIN** / PASS |
| question shaped like a trophy(R) | トロフィーの形をした質問(3rep全て FAIL_LIT) | 賞という形で投げかける問い x3 | PASS x3 |
| greener grass(R) | より青く見える芝生 / より青々とした芝生 x2(FAIL_LIT) | 自分より恵まれて見える他人の暮らし 等 | PASS x3 |
| sound no one asked for(R co-KP) | 誰も頼んでいない音 / 誰も求めていない音 | 誰も聞きたくない音(rep1)/ 誰も求めていない音 / 誰も頼んでいない音 | **THIN** / PASS / PASS |
| reach for someone's wallet(S2) | 人の財布に手を伸ばす(FAIL) / 誰かが自分の財布に手を伸ばす(PASS) | 財布を出してお金を払おうとする | PASS |
| settle at(S2) | ～で取引を終える / ～で落ち着く(FAIL) | ～で取引を終える | PASS |
| turn on its head(S2) | ～をひっくり返す | 期待をひっくり返す | PASS |
| take off an ai costume(S2) | AIの衣装を脱ぐ / AIの着ぐるみを脱ぐ | AIの裏に人がいると明かす | PASS |
| become like porches(held-out) | 玄関先のような場所になる(THIN) | ベンチが人々の憩いや交流の場になる | PASS |
| move in the other direction(S2、悪化) | 反対の方向に動く | 売れ行きは逆に下がった | **THIN** |
| supply chain(S2、悪化) | 商品が作られて消費者に届くまでの流れ | 商品が作られて店に届くまでの流れ | **THIN** |
全KP一覧(Stage 2、B0 2rep・X2p・Cp_t4の文字列とラベル)は `report_05_fable_labels_05_withcde.md` 末尾。

## D. 残存THIN一覧(X2p、全85出力中5件。FAIL系は0)
| KP | 区分 | X2p文字列 | 性質(Fable注記・事実) |
|---|---|---|---|
| an unseen clock rep2 | R hard-core | 値札に隠れた時間のずれ | 「独自のタイミング」より狭い(時間のずれに限定) |
| sound no one asked for rep1 | R co-KP(B0=PASS、悪化) | 誰も聞きたくない音 | asked for の意味が移動(頼む→聞きたくない)。同文字列はX2でもTHIN |
| a door inside the pain | held-out | 悲しみの中に見つけた、思い出と向き合い直す道 | 物語解釈を含み長く説明的。B0・X2・CpもTHIN(悪化ではない) |
| move in the other direction | Stage 2(悪化) | 売れ行きは逆に下がった | 本文の文脈を補い、方向まで断定 |
| supply chain | Stage 2(悪化) | 商品が作られて店に届くまでの流れ | 「店」に限定(B0は「消費者」)。Cp_t4でも同じ文字列がTHIN |

## E. 新規悪化一覧(B0がPASSでX2pがTHIN以下)
R co-KP 1(`sound no one asked for` rep1)、Stage 2 strict 2(`move in the other direction`、`supply chain`)、held-out 0、R hard-core 0(`an unseen clock` rep2 の B0 は FAIL_LIT のため悪化ではない)。PASS→FAIL 系はどこにも無い。

## F. 費用台帳合計と所見
- 台帳 `er112_output/kp_gm_trial_05/paid_calls.jsonl` 累計 **17.401円**(Trial_05全体、個別枠8.33円を超過、Fable委任_25/26/28で承認済みの範囲。`BUDGET_LOG_01.md`)。X2p 計 54 call 約8.6円(1call平均**0.1593円**、reasoning_tokens平均1,343、output_tokens平均1,561、`metrics_05.md`)。委任_29はAPI 0(追加費用0)。
- 単価(1call): B0 0.0585円(reasoning 304 token)、X1 0.0654、X2 0.1254(1,074)、**X2p 0.1593(1,343)**、**Cp 0.1566(1,340)**。当初の見込み「X2はCpの約半額」はX2pでは成立せず、**X2p と Cp は同程度**(`REASONING_TOKENS_01.md`のCp 0.242円は5 callの少数平均で、24 call平均は0.157円)。
- 速度: wall-clockの精密実測は無い(workers=2の並列実行)。pilotの逐次4call間隔[B0 約18秒 / X1 約22秒 / Cp 約37秒、出力token 696/955/2,953]から、出力token約1,000増あたり約+8〜9秒/callの粗い見積(実測ではない、runtime evidenceで再測定要)。
- reasoning_tokens所見: B0 304 → X1 528 → X2 1,074 → X2p 1,343 → Cp 1,340(call平均)。可視欄の追加は推論量を増やし、増分の大半は非可視の推論token(`REASONING_TOKENS_01.md`)。

## G. Fable判定の揺れ(OF-KP1-08)
control再判定の一致率 **7/10**。不一致3件(`draw a line|区別する` THIN→PASS、`reach for someone's wallet|人の財布に手を伸ばす` FAIL→PASS、`on the throne|トップの座にいて` THIN→PASS)はすべて前回より**緩い**方向。集計は前回ラベル維持(Fable判断)。したがって05d/05eのPASSには「緩め」方向の揺れ余地があり得る(上限の保証ではない)。

## H. 限界(事実)
1 rep、Fable単独評価(Sonnet Judgeなし)、luna・effort=high固定、held-out 10KP(ZのF型は母集団2件のみ)、Stage 2はB0の良い方基準(Trial_04の2rep)との比較(R・held-outのB0は新規rep)、X2pの設計はR結果を見た後に調整(差分は`TRIAL_DESIGN_06.md` §9)・gating基準もX2p確定値を見た後に是正(同 4-追記)、Trial_02〜04確定ラベルを継承。

---
(以下は委任_22〜28時点の履歴。逐語を残す。上の確定版が優先する)


管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_22 / 設計=`../TRIAL_DESIGN_06.md` / 台帳=`BUDGET_LOG_01.md` / 実行=`er112_kp_gm_trial_05.py`(DEV専用、Production module編集0、Production hash開始=終了一致[`production_hash_start.txt`/`production_hash_end.txt`]) / 使用モデル: `gpt-6-luna`、effort=high固定(最新世代の最上位系ではない。理由=評価対象がluna生成の品質そのもの[Production系列と同一、25節の例外]。判定=Fable盲検、API 0)。

## 1. 状態(事実)
| arm | R(hard-core 4KP+co-KP 3、3rep) | held-out(10KP、1rep) |
|---|---|---|
| B0 | 3rep全件完了(12 call) | 完了(10 call) |
| M | 既存Trial_04のrep1-2を参照+**新規rep3完了**(4 call) | 対象外 |
| X1 | 3rep全件完了(12 call) | 対象外 |
| X2 | 3rep全件完了(12 call) | 完了(10 call) |
| Cp | **rep1全件完了(4 call)+rep2はdraw a lineのみ(1 call)で自動停止**(平均0.242円>0.20円)。rep2残り3・rep3 4 call未実行。Trial_04の既存Cp rep1は参照可 | **未実行**(約2.4円=残枠超過) |

費用合計 **6.252円/上限8.33円**(65 call)。held-out 10KP=抽出順(seed=22)の先頭10件(`heldout_selection_log_05.json`。Z[小説]は母集団に2件のみ[`rise above`,`tiny bomb`]で全数を含む)。残り4件(`feel borrowed`,`feel like friction`,`jump into action`,`story with two different speeds`)は未実行。

## 2. 決定論的集計(API 0。`metrics_05.md`)
| arm | n出力 | 1call円 | reasoning_tokens/call | validate互換 | gloss==naive_ja | 文字数比>1.5(対B0平均) | 説明文型語尾 | conveys yes/partly/no |
|---|---|---|---|---|---|---|---|---|
| B0 | 31 | 0.0585 | 304 | 31/31 | - | - | 1 | - |
| M | 7 | 0.0524 | 336 | -(M_SCHEMAは欄無し) | - | 3/7 | 0 | - |
| X1 | 21 | 0.0654 | 528 | 21/21 | - | 11/21 | 3 | - |
| X2 | 31 | 0.1254 | 1,074 | 31/31 | **0/31** | 15/31 | 3 | 8/1/22 |
| Cp | 9 | 0.2424 | 2,309 | 9/9 | - | 2/9 | 0 | - |
- Production `validate_item_corrected`(括弧禁止・算用数字・人称整合・qa・current_gloss_consistent型)への互換は、X1/X2/B0/Cpの全出力で不合格0(M6=動作は目標達成)。`gloss==naive_ja`(アンカリング)=0/31。
- 注意: 文字数比>1.5は短いgloss(多くが5〜10字)では1〜3文字の差でも超えるため、**長さの過剰の指標として弱い**(30字超は全armで0件)。説明文型語尾はX1/X2が各3件(B0 1件)=**種類の分類はFable盲検後**。
- M2(診断): X2のR core 4KP x 3rep=12出力の`naive_ja_conveys`は **no 9 / yes 3 / partly 0**(yes 3件はすべて`draw a line`で naive_ja=「線を引く」)。no/partly率=9/12(期待≧10/12の事前宣言をわずかに下回る)。全31出力では yes 8 / partly 1 / no 22。
- reasoning_tokens(OF-KP1-03): `REASONING_TOKENS_01.md`。B0 361→X1 527→X2 1,206→Cp 2,308 (R, 1callあたり)。

## 3. Fable盲検
- `fable_blind_05.md`(20行・78セル。R 7KP+held-out 10KP中の未ラベル文字列+**ラベル済み文字列10件の再判定[OF-KP1-08]**を混在、arm伏せ)と`fable_blind_05_key.json`。held-out 10KPの本文全体は`er112_output/kp_gm_trial_05/heldout_set_05.json`(`article`欄)。
- 判定済み文字列の継承: Trial_02〜04でFable確定済みの文字列は表に含めず継承(再判定10件のみ混在)。
- 判定後の集計: `py er112_kp_gm_trial_05_report.py report --labels <labels.json>`(labels形式=`{"<row#>:<col>": PASS|THIN|FAIL|FAIL_LIT}`。Trial_04と同じ。R基準の事前宣言[(FAIL_LIT+FAIL)≦1/12 かつ 2/3以上失敗KP 0 かつ THIN≦B0+1]、X1対M、X2対Cp、held-out悪化、control一致率、R Before/Afterを出力)。X2の`meaning_in_text_en`/conveysは**判定後に**`x2_fields_05.md`を開く。

## 4. OF-KP1-07 Grep確認(API 0)
- A/B/C旧ライン(凍結中)は新規生成経路を通らない: `is_fulltext_gloss_missing`(`er003_key_words_gloss_alignment.py:270-273`)は`fulltext_source_ref`付きitemのみ真(docstring「A/B/Cのitemは該当しない」)。`fulltext_source_ref`の設定側=`er105_kp_fulltext_selector_01.py`・`er003_key_words_canonicalization.py`のみ。gloss再整合の呼出元(`align_glosses(`、Trial/test除く)は`er003_v1_n3_01_scaffold_generate.py:539`(X/標準)と`er026_family_z_fiction_production_runner_01.py:1552`(Zの人称修復、current glossあり=M-base/X2の新規生成分岐は適用されない)の2か所のみ。
- 今回のTrialは新規生成経路のみが対象。混在batch・Z repair経路は`TRIAL_DESIGN_06.md` §3-1に確定(採用設計時の課題)。

## 5. 未解決・次の判断(判断候補)
1. 事前宣言の判定基準(R)での判定は**Fable盲検後**(私はしない)。Cpが2rep目以降未完のため、X2対Cpの比較はCpが「rep1 4call+Trial_04のrep1参照」の1〜2rep相当。
2. 予算: Cp R残り7call(約1.7円)+held-out Cp 10call(約2.4円)=約4.1円=合計約10.4円で個別枠8.33円を約2.1円超過。Cpは単価が見積(0.18円)の1.35倍(0.242円)。**案**: (a)追加約4.1円(+上限の見積幅を含め約5円)で完遂(案件累計は約280円≦300円)=推奨、(b)held-out Cpを除きR Cp残りのみ(約1.7円、残枠内だがpilot閾値0.20円/callの平均超過で自動停止している=閾値の再設定が必要)、(c)Cpを追加せずStage 1の盲検結果(B0/M/X1/X2+Cp 1.2rep)で判断。いずれもFableの判断。

## 委任_23 追記(Fable盲検ラベル反映・Cp完遂)
- Fable盲検ラベル(Stage1+held-out、Key未開封で確定)を `fable_labels_05.json` に保存、注記を `FABLE_BLIND_RESULT_05.md` に逐語保存し集計(`report_05_fable_labels_05.md`)。
- 判定材料(**VALIDATED判定はFable**): R基準(FAIL系<=1/12 かつ 2rep以上失敗KP 0 かつ THIN<=B0+1)は、X2: FAIL系0/2rep失敗KP 0だがTHIN 4>B0+1=1、Cp: FAIL_LIT 2(ラベル確定前でも不達)、X1/M/B0不達。H5(X1対M)はFAIL系 6→5で有意差なし。held-out悪化: X2=0、Cp=追加盲検05c確定後。control一致率 7/10(不一致3件はすべて前回より緩い方向)。
- Cp追加(19call、2.545円)後の追加盲検表 `fable_blind_05c.md`(10文字列)。ラベル後に `--labels_c` 付きで再集計。
- Stage 2準備(未実行): `er112_kp_gm_trial_05.py gen --arm X2 --set S2 --reps 1`(non-R 54KP、29 call、見積約3.64円)→`er112_kp_gm_trial_05_report.py blind_s2`(B0/CpはTrial_04再利用)。Fableが「Stage 1通過」を連絡してから実行。

## 委任_25 追記(05cラベル確定・Stage 1確定表・X2')
- 05cラベル(Fable、Key未開封)を `fable_labels_05c.json` に保存、注記と「Fable判定の揺れ(緩化方向)」を `FABLE_BLIND_RESULT_05.md` に逐語保存。再集計: `py er112_kp_gm_trial_05_report.py report --labels fable_labels_05.json --labels_c fable_labels_05c.json`(`report_05_fable_labels_05_withc.md`、X2p追加後は同ファイル名で上書き)。
- **Stage 1確定表(R hard-core 4KP x 3rep=12出力/arm、ラベル確定後)**:

| arm | PASS | THIN | FAIL系(FAIL_LIT+FAIL) | 2rep以上失敗KP | 事前宣言基準 |
|---|---|---|---|---|---|
| B0 | 2 | 0 | 10 | unseen clock/trophy/greener grass | (基準線) |
| M | 6 | 0 | 6 | unseen clock/trophy | 不達 |
| X1 | 7 | 0 | 5 | trophy | 不達 |
| X2 | 8 | 4 | 0 | なし | THIN 4>B0+1のみ不達 |
| **Cp(確定)** | **9** | **1** | **2** | なし | FAIL系2>1で不達(unseen clock rep2「見えない時計」、greener grass rep3「より青々とした芝生」) |
- held-out 10KP: X2悪化0、**Cp悪化0**(05c確定後)。
- X2p(委任_25): 差分は `TRIAL_DESIGN_06.md` §9、費用 `BUDGET_LOG_01.md` 委任_25追記。決定論集計(`metrics_05.md`): 31出力、1call平均0.1412円、gloss==naive_ja 0/31、文字数比>1.5 14/31(X2 15/31)、説明文型語尾3(X2 3)、30字超0、conveys yes/partly/no=4/4/23(X2 8/1/22)、validate互換31/31。出力欄=`x2p_fields_05.md`(判定後に開く運用)。
- 盲検表 `fable_blind_05d.md`(X2pで新出の13文字列・10行、既出14文字列はラベル継承、arm伏せ)+`fable_blind_05d_key.json`(別ファイル)。**VALIDATED判定はしない(Fable)。** ラベル後: `report --labels fable_labels_05.json --labels_c fable_labels_05c.json --labels_d fable_labels_05d.json`。

## 委任_26 追記(05dラベル確定・X2p確定値・Stage 2部分結果。2026-10-24)
- 05dラベル(Fable、Key未開封)を `fable_labels_05d.json` に保存、注記を `FABLE_BLIND_RESULT_05.md` に逐語保存。再集計=`report_05_fable_labels_05_withc.md`(`--labels_d`付き)。
- **X2p確定(R hard-core 4KP x 3rep=12出力)**: PASS 11 / THIN 1(`an unseen clock` rep2「値札に隠れた時間のずれ」)/ FAIL系 0 / 2rep以上失敗KP なし。旧事前宣言(THIN<=B0+1=1)も形式上満たす。X2: 8/4/0、Cp: 9/1/2、B0: 2/0/10。held-out 10KP: X2p悪化0(`a door inside the pain`はB0もTHIN)。X2p R co-KP悪化なし。
- Fable gating基準是正(`TRIAL_DESIGN_06.md` 4-追記): (FAIL系=0, THIN<=2, 2/3以上失敗KP 0, held-out悪化0) を満たす -> Stage 2へ。
- **Stage 2(non-R 54KP x X2p 1rep)は部分完了**: 21 job/43 KP(未実行11 KP)、4.054円で費用cap(16.0円)HALT。BUDGET_LOG_01.md参照。
- 決定論集計(Stage 2完了43 KPのみ): gloss==naive_ja **0/43**、文字数比>1.5(対Trial_04 B0 2rep平均) **4/43**、説明文型語尾(こと/もの/ようす等)または30字超 **0/43**、B0のいずれかのrepと同一文字列 18/43、conveys yes/partly/no=6/6/31。validate互換 全74出力(Stage1+2のX2p)不合格0。
- 盲検表 `fable_blind_05e.md`(**部分表**: 完了43KPのうち、X2p新出文字列で未ラベル=16行。B0の良い方/悪い方rep・Cp_t4と同一文字列は継承)+`fable_blind_05e_key.json`(別ファイル)。残11KPを実行すれば再生成が必要(blind_s2コマンドは完了分のみで生成)。strict(B0良い方rep基準)/lenient(悪い方rep基準)の比較はFable判定後に実施(準備済み: B0_t4/Cp_t4 ref_cells)。VALIDATED判定はしない。

## 委任_28 追記(Stage 2完走・完全版05e。2026-10-24)
- 残11KP(8 job)を実行し **X2p Stage 2 = 54/54 KP完了**(費用はBUDGET_LOG_01.md。台帳欠落2jobは再起動1回で再生成)。
- 決定論集計(54KP、API 0): gloss==naive_ja **0/54**、文字数比>1.5(対Trial_04 B0 2rep平均) **7/54**、説明文型語尾または30字超 **0/54**、B0のいずれかのrepと同一文字列 19/54、conveys yes/partly/no=7/8/39。validate互換 X2p全85出力(Stage1+2)不合格0。`metrics_05.md`更新済み。
- 盲検表 `fable_blind_05e.md`(**完全版**: 54KPのうち05/05c/05dおよびTrial_04確定ラベルと同一でない新出文字列のみ=21行21文字列、arm伏せ)+`fable_blind_05e_key.json`(別ファイル)。再生成コマンド `er112_kp_gm_trial_05_report.py blind_e`。**VALIDATED判定はしない。**

## 委任_29 追記(05eラベル保存・Stage 2確定)
- 05eラベル(Key未開封)を `fable_labels_05e.json`、注記を `FABLE_BLIND_RESULT_05.md` 「05e」節に逐語保存。`er112_kp_gm_trial_05_report.py` に `--labels_e`(05eキー適用)と Stage 2 strict/lenient 表(`stage2_table`)を追加(API 0)。確定表=上記 §B、全KP一覧=`report_05_fable_labels_05_withcde.md`。
- 事前宣言の Stage 2 strict 基準(PASS→FAIL 0、PASS→THIN≦2)への適合=適合(0 / 2)。VALIDATED判定はFable。

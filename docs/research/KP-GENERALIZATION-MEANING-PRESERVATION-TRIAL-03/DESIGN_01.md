# DESIGN_01: 一般化の意味・用法保持 根本対策・比較Trial 設計(KP-GENERALIZATION-MEANING-PRESERVATION-TRIAL-03 委任_01、2026-10-30、API 0)

原文=`docs/pm/delegation_log/2026-10-30_KP-GENERALIZATION-MEANING-PRESERVATION-TRIAL-03_USER.md`(逐語保存済み)§4〜§8。原因=`ROOT_CAUSE_01.md`。前回=`../KP-GENERALIZATION-CHUNK-VALUE-TRIAL-02/{TRIAL_DESIGN_02.md,kpg03_*}`。
**Trial専用。Production code/Prompt/Validator/閾値の変更0。E1L・E4・新方式はいずれもProduction未採用。** 実装=`kpg04_*.py`(本ディレクトリ、er*非import)。

## 1. 目的と合格基準(事前登録。結果を見てから変えない)
最優先=「本文と異なる意味・用法の候補を学習者に出さない」(原文§1・§5優先順位1〜2)。候補合格率の最大化は目的ではない。
| # | 基準 | 合格 | 根拠 |
|---|---|---|---|
| C1 | 既知の2誤り(hear it out / take points away from)の再発 | 対象4レベル(untidi_a2/b1b、ほか出現レベル)で**0**。S軸OKの形=`hear someone out` / `take something away from`、または本文の形のまま(後述の安全側) | 原文§2-A/B |
| C2 | 意味・用法NG(S軸: SENSE_SHIFT/ARG_TYPE/FRAME_SHIFT/MOD_SHIFT/GLOSS_MISMATCH)の提示件数 | 14ケース+held-out6レベルの**提示全件で0**(Sonnet実読+別系列独立評価、割れた例は根拠確認)。probe(42件)のFAIL(決定論+実読)が**≤2かつP0基線の半分以下** | 原文§5優先順位1・§8④ |
| C3 | 正しかった候補を壊さない | E1Lで○だった候補(同span)のうち、新方式で×または脱落した割合 **≤5%**(理由別に記録)。probe: MODIFIER_DROPPABLE 6/6 PASS(修飾語除去をNGにしない)、ALREADY_CORRECT 6/6、FIXED_PRONOUN≥5/6、MODIFIER_ESSENTIAL≥5/6 | 原文§2-C・§5 |
| C4 | 自由な組合せ混入率・良質候補の維持 | 混入率 ≤ E1L(2/81=2%)+1pt。良質候補の脱落 ≤ E1L水準(13/60=22%)+5pt。3件以上ケース数は**参考**(品質を下げて増やさない) | 原文§5 |
| C5 | 費用 | 量産単価増=N2系で ≤+¥1/セット、N4系は +¥4/セット程度(有効性が必要な場合のみ採用提案)。70円目標に対する影響を明示 | 原文§6 |
- 全合格 → `VALIDATED`(採用はユーザー判断)。基準未達で方式変更余地あり → 再設計。見込みなし → `REJECTED`。採否に新ルール(display_form許容・限定検査の費用等)が必要 → `USER_DECISION_REQUIRED`(Closeout案)。Production配線は一切行わない。
- **安全側の既定(全方式共通)**: 意味が変わると判定された一般化は**本文の形(正規化のみ)へ戻す**(Production現行の「そのまま通す」挙動と同等)。つまり最悪でもProduction同等の候補になり、誤った見出し形は出さない。

## 2. 方式案の設計と比較(原文§4 A/B/C+追加)
工程記号: B1=過剰生成(luna、E1Lと同一prompt、cache hit) / SEL=塊判定(E1L Prompt v3、span判定、luna) / GEN4=従来一般化 / GEN5=意味確定先行の構造化一般化(新) / VER=従来検証(gemini) / VER5=意味・用法検査を統合した検証(新) / CHK=限定独立検査(新)。
| 方式 | 原文区分 | 工程順序と入力文脈 | 追加call(vs E1L) | 対象原因 | 良質候補脱落リスク | 備考 |
|---|---|---|---|---|---|---|
| **E1L**(基本比較) | - | B1→SEL→GEN4(**SEL理由を入力**)→VER | - | - | 基準(13/60=22%) | 既存結果をそのまま再利用(キャッシュ) |
| **N1a**(切り分け) | B | B1→SEL→GEN4(**理由を渡さない**)→VER | 0 | R2のみ | E1Lと同じ(SEL共通) | E1Lとの差=アンカー除去のみ(因果の切り分け用。HARD6のみ) |
| **N1** | B+C統合 | N1a + VER5(本文基準の語義導出・目的語を訳に合わせて削らない・修飾語除去は許容) | 0(Promptのみ) | R2,R3 | E1L同等 | 最安。VERの確率性(R4)が残る |
| **N2** | **A+B+C統合** | B1→SEL→**GEN5**(source_sense→arg_notes→headword_frame→frame_change→tokens→gloss の順で**意味を先に確定**。headword_frameとtokensの不一致を決定論で調停)→VER5 | 0(GEN5出力が約1.5倍) | R1,R2,R3 | E1L同等 | 方式A。someone/somethingは「見出しの標準用法」基準(規則A')。固定it(take it out on等)はCORE |
| **N4** | **A+B+C(限定)** | N2 + **決定論flag**(PRONOUN_SLOT/CONTENT_DROPPED/VER_FIXED_FORM/FRAME_MISMATCH等)が付いた候補だけを、**別系列の上位モデル(gpt-6.1-sol)が局所文脈(前後1文)のみで**独立検査(文脈での語義→新規例文→SAME/SENSE_SHIFT/ARG_TYPE_SHIFT/FRAME_SHIFT/GLOSS_MISMATCH)。SHIFT系は修正案を決定論検査に通して採用、不可なら本文の形へ戻す | +1 call/レベル(flag率30〜42%の候補のみ) | R4(安全網の確率性・独立性) | E1L同等+(戻しは学習価値を落とすが誤りは出さない) | 方式C(疑わしい候補限定)。flagの偽陽性は費用のみの影響 |
| N4d | C限定(低単価) | N4の検査器を deepseek-v4-pro(非thinking)に | +1 call(約半額見込) | R4 | 同上 | probeでsolとの精度・費用比較。採用候補になれば単価減 |
| N5(参照のみ) | C全件 | N2 + **全候補**をsol検査 | +1 call(大) | 上限対照 | 同上 | 「限定が全件検査と同等か」を見る基準。probeとHARD6のみ |
| E2/E3/E4 | (既存) | GEN_ALL→SEL→VER(/GATE) | 参照 | - | **E2 33%・E4 40%脱落** | 全候補を一般化するため脱落・費用が大きい→N系はE1Lの選定段を維持 |
**採用しなかった/保留の追加案**: (a)GENを2回走らせ一致を採る自己一貫性=費用2倍で系統バイアス(R1,R2)は解消しない→保留。(b)WordNet等の辞書frameによる決定論検査=句動詞の目的語タイプ情報が薄く単独では不可、flag生成の補助に留める(kpg02のWordNet lockは継承)。(c)全候補への一律高額検査(N5)=上限対照のみ。(d)一般化を止めて本文の形に戻す(安全側フォールバック、全方式に組込み)。
**方式を分ける理由**: 原因が複数(R1〜R5)あるため一つの対策に集約しない。N1(R2+R3)→N2(+R1)→N4(+R4)と**要因を1つずつ足す**ので、どの層が効いたかを差分で説明できる。

## 3. モデル(最新モデル原則 `docs/pm/PM_GOVERNANCE.md` 25節 25-3)
| 使用モデル名 | 最新モデルか(公式2026-10-09取得、`dev_eval_model_inventory_01.md`) | 最新でない場合の理由 |
|---|---|---|
| gpt-6-luna(B1/SEL/GEN4/GEN5) | 最新世代の効率系(最上位ではない) | 例外種別=**ライン組み込み候補の性能確認**(Production経路のSUPPORT_MODELがluna。方式の実用性は本番モデルで測る) |
| gemini-3.8-flash(VER/VER5) | 最新世代(Flash) | TRIAL-02と同一(VER系列の連続性。独立評価には使わない=循環) |
| gpt-6.1-sol(CHK、判定割れの調停) | はい(推奨系) | - |
| deepseek-v4-pro(独立評価、N4d検査) | はい(DeepSeek最上位系) | 非thinking+max_tokens明示(thinking既定事故の再発防止) |
| deepseek-flash | **使用しない** | TRIAL-02の独立評価で両誤りを0/16しか検知できず、下位系を使う例外理由(既存結果との比較等)も不要(新Rubricで再評価) |
単価は`kpg02_llm.PRICE`(公式)。gpt-6.1-solは`pricing_snapshot.json`未登録(25-2: 実行前に登録が必要)。kpg02_llm.PRICEにはTrial用に登録済みで費用ガードは機能するが、**`pricing_snapshot.json`への登録は委任_02で要確認**(本委任の範囲外、未実施)。

## 4. 検証ケースの設計(原文§5)
### 4-1. 既存14ケース(過去Trial結果を最大限再利用)
untidi/ai_cha/jwst_m/meta_w×(a2,b1b)+aiisland_b1b/surname_b1b/melos_a2/ignobel_a2/b1b/tesla_b1b。D/E1L/E1S/E2/E3/E4の結果は`kpg03_work/results`にあり**新規費用0で比較に使う**。SEL/B1は`llm_cache`に在り、N系も同一prompt分はcache hit(費用0。Cap 0の間は実行不可)。

### 4-2. held-out(未使用記事・過適合回避)
TRIAL-01/02のどのarmにも未投入の記事レベル6件: `aiisland_a2, moon_a2, moon_b1b, surname_a2, melos_b1b, tesla_a2`(`corpus.json`既存。tesla_a2のみ現行Production候補docなし=比較はE1L/N系のみ)。方式の確定(基準C1〜C4の判定)は**held-outを見る前にHARD6+14ケースで行い、held-outは凍結した方式で1回だけ走らせる**(適応を防ぐ)。

### 4-3. 検証ケース(probe) 48件 = `kpg04_probes.json`(生成=`kpg04_probes_build.py`)
8種別×6件。短い文脈(2文)つき、許容形(ok)と既知NG形(ng)を事前登録。選定段を省き**一般化→検証(→検査)だけ**を直接測る。
| 種別 | 狙い | 例(ok / ng) |
|---|---|---|
| ARG_PERSON_THING | 人/物の取違え(見出しの標準項タイプ) | hear her out→`hear someone out`/`hear something out`、see it off(擬人化された船)→`see someone off`、sat through the whole lecture→`sit through something` |
| FIXED_PRONOUN | 慣用表現中の固定itをsomething化しない | took it out on→`take it out on`/`take something out on`、go for it(`go for something`は別語義) |
| SENSE_SHIFT | 目的語・前置詞・名詞の除去で語義が変わる | **took two points away from→`take something away from`/`take away from`**(既知例の言い換え)、took up space→`take up space`/`take up`、came to terms with→`... with`/`come to terms` |
| OBJECT_OMIT_OK | 目的語を省略しても同語義(壊さない) | carried out the plan→`carry out`可 |
| MODIFIER_DROPPABLE | 修飾語を削ってよい(NGにしない) | set a lower limit→`set a limit`可、took an unexpected turn→`take a turn`可、took good care of→`take care of`可 |
| MODIFIER_ESSENTIAL | 削ると語義が変わる | broke new ground in→`break new ground`、in the long run、turned a blind eye to |
| ALREADY_CORRECT | すでに正しい一般化を壊さない | walk someone through / set something aside / break the ice |
| FREE_COMBINATION | 自由な組合せ(選定段で落とすべき) | wiped the kitchen table 等。**SELプローブ用。GEN probe runnerは対象外(SELはE1Lと同一で変更しない)。runnerは委任_02で必要になった場合に追加** |
- 既知の誤り2例とは語句を変えた同型(AP2擬人化、SS1言い換え)を含む=過適合の検出に使う。
- 採点: `score_probe`(決定論) PASS/FAIL/REVIEW。REVIEWはSonnet実読。probe自体の妥当性(辞書的な正否)は委任_02の実行前にFableが確認できるよう`ok/ng/note`を明記している。

### 4-4. 評価Rubric(2軸分離。`kpg04_manual.py`)
S軸(意味・用法の保持)と N軸(一般形としての自然さ)を**別のコード**で記録する。S軸=SENSE_SHIFT/ARG_TYPE/FRAME_SHIFT/MOD_SHIFT/GLOSS_MISMATCH。**意味を損なわない修飾語除去(原文§2-C)はNGにしない**。ARG_TYPEの基準は「本文の指示対象」ではなく「見出しの標準的な用法」(`hear it out`=擬人化でも`hear someone out`が○)。
**過去判定の再読み替え(P0、API 0)**: TRIAL-02のSonnet実読ラベルは`take a turn`/`set a limit`を`MEAN`NGとしていた(新基準では許容)ため、D/E1L/E1S/E2/E3/E4の既存全出力を新Rubricで再監査し、S軸の潜在NG(FRAME_SHIFT等、例: `take up space→take up`型)の有無も確認する。ここまでのS軸NG件数(種=`kpg04_manual.BASELINE_S_AXIS_02`): D 1/71、E1L 3/81、E2 1/77、E3 1/77、E4 2/70(母数小・要再監査)。

### 4-5. 独立評価(別系列)
- 評価器: deepseek-v4-pro(全arm、**変化があった項目のみ**=display≠本文の項目を40件ずつバッチ)。判定割れ時のみgpt-6.1-solで調停(solがCHKに使われるN4/N5は評価対象外=循環回避)。gemini-3.8-flashは全armのVERに入っているため評価に使わない。
- **評価器の感度を事前確認**(今回の発見: 既存の評価は両誤りを検知できなかった): 既知NG(7件)+probeのFAIL形+それぞれ対になる○形を混ぜた約60件を評価器に通し、S軸NGの検出率≥90%、○の誤NG≤10%を満たした評価器だけを主評価に使う。満たさなければ主評価はSonnet実読+Fable独立評価とし、評価器の結果は参考扱い。
- 評価Rubric v2は参照つき: 見出し標準用法の指針・原文§2-Cの許容を含める。**判断が割れた例は根拠(辞書的な見出し・用例)を確認**し、評価モデルを無条件に正としない。

## 5. 実行フェーズ・費用・停止点
単価の根拠=TRIAL-02/01台帳実測(luna SEL 0.27・B1 0.16・GEN 0.22、gemini VER 0.58(1.7k in/0.6k out)、sol 1call約2.1(1.5〜3.2)、deepseek-v4-pro 公式単価から算出約1.7/40件バッチ)。N系のGEN5/VER5は出力が約1.5倍になるため+0.1/+0.25を見込む。**推定のため±30%**(最大の不確実性=solの推論token)。
| Phase | 内容 | 見込み(円) | 停止点(累計増分) | 判断 |
|---|---|---|---|---|
| P0 | 既存全出力のRubric再監査(Sonnet実読、API 0)+評価器感度の準備 | 0 | - | S軸の潜在NG把握。ここで新たな誤りクラスが多ければprobe追加 |
| P1 | probe 42件: P0(GEN4+旧VER基線)・P1(N1)・P2(N2)・P4(N4/sol)・P4d(N4/ds) | 23(P0 3.0・P1 3.6・P2 4.6・P4 8.6・P4d 2.8) | 30 | N系のFAILがP0の半分以下かつ≤2でなければ**方式を再設計**(14ケースへ進まない)。N2で足りればN4は14ケースで縮小 |
| P2 | 14ケース: HARD6先行(N1a・N1・N2・N4)→問題なければ残り8(N1・N2・N4) | N1 14.4+N2 15.8+N4 25.2+N1a 3.5=**59** | 70 | 凍結する方式を決定 |
| P3 | held-out 6レベル(凍結した方式のみ+E1L+B1/SEL新規): E1L 4.8・N1 6.2・N2 6.8・N4(CHK)10.5・SEL/B1 2.6 | **31**(任意でD・E4を追加+25) | 40 | 過適合の有無 |
| P4 | 独立評価(deepseek-v4-pro変化項目のみ約300件+感度事前確認+solは割れ調停のみ) | **22** | 25 | 判定割れの根拠確認 |
| P5(条件付き) | N5全件検査(probe)17 / run間ばらつき(SALT違い、最良方式×3レベル)6 | 23 | 25 | 必要時のみ |
- **コア合計 ≈ ¥135(範囲95〜175)**。条件付き(P5、held-outのD/E4+25、SALT)で最大 ≈ ¥185。
- **節約レバー(優先順)**: ①N4をHARD6+held-outに限る(-12) ②N1aを省略(-3.5) ③評価器batchを変化項目の絞り込み強化(-8) ④N4をN4d(ds)で代替しsolを省略(-12)。
- **Fableへの提案Cap: `KPG4_CAP=¥180`**(コア見積135+条件付き一部+margin)。累計80%(¥144)で事前警告。フェーズ停止点は上表の「累計増分」(`--phase-cap`)。日次1,000円の他案件との併用は未確認(7-9)。7-7: 見積300円以下かつ承認済みScope内→AI自律(新仕様/未承認Trial範囲は別)。
- **量産単価の換算(参考、既存P7との置換相殺は未確認)**: 1レベル=B1 0.16+SEL 0.27+GEN+VER。E1L 1.23 / N1 1.46 / N2 1.56 / N4 ≈3.4 / N4d ≈2.5 / E4 3.14 (円/レベル)。1記事セット(Std+Adv)=2レベル → E1L 2.5 / N2 3.1(+0.6) / N4 ≈6.7(+4.2) / N4d ≈5.0 (円/セット、70円比 3.5% / 4.5% / 9.6% / 7.1%)。
- **並列化・所要見込み**(原文8-X/Charter2): P1のprobe 5構成は独立(並列4worker)。14ケースは上流共有のためN1→N1a、N2→N4の順(E2→E3の二重課金の教訓)、それ以外の記事は並列。Sonnet実読は実行と並行。見込み=API実行 計1.5〜2h、実読・集計 2h前後、ページ作成0.5h。直列化の理由=cache共有による二重課金回避と、held-out凍結(適応防止)のみ。

## 6. End User向け Before/After比較ページ(`kpg04_page.py`)
- 記事別・Standard/Advanced別に、現行Production / D / E1L / E4 / 今回の改善方式(複数可)を横並び。候補カードごとに **英語表現・日本語意味・本文中の根拠表現・○/×・×の具体的理由**。冒頭に○×の凡例を日本語で説明し、技術ログ不要で読める。
- 現時点でD/E1L/E4の列は**TRIAL-02の実読ラベルを新定義(2軸)へ読み替えて表示可能**(`hear something out`→「人/物の選択が見出しの標準用法と合わない」、`take away from`→「本文と別の語義」)。ベースライン確認用プレビュー: `kpg04_work/page_preview/index.html`(非公開、untidi_a2/b1b/jwst_m_b1b)。新方式の列はmock体裁確認済み(内容は無意味)。Production列は未判定(`－`)=P0で実読する。
- 公開(`user_test/kp_meaning_preservation_trial_03/`)は委任_02以降でFable確認後(`--publish`)。最終報告(原文§8①〜⑤)のうち④品質・QCDの数値は`kpg04_stats`相当の集計を委任_02で追加する(本委任では枠のみ=`kpg04_manual.py`のコード定義と`kpg03_stats.py`の指標定義を流用予定)。

## 7. 実装準備の状態(API 0、完了)
| ファイル | 役割 | 検証 |
|---|---|---|
| `kpg04_llm.py` | 専用台帳・**Cap=`KPG4_CAP`(既定0=有料call全拒否)**・フェーズ停止点・max_out/think_budget必須・mock・旧`kpg03_llm.call`無効化(CAP=120の誤用防止) | `kpg04_test.py` 31件PASS(Cap0拒否/phase超過拒否/旧callの例外化 等)。**test中に実APIへ到達した事故が1回**(下記) |
| `kpg04_methods.py` | N1a/N1/N2/N4/N4d/N5、GEN5/VER5/CHK5 Prompt、reconcile・flag_item・run_check・score_probe | 同上+mock dry-run(14ケース×N1a/N1/N2/N4/N4d/N5・probe P0/P1/P2/P4/P4d/P5完走、エラー0) |
| `kpg04_run.py` | 実行(`--cases ALL14/HELDOUT/HARD6 --arms --probes --phase-cap --suffix --mock`)。CapReachedでrc=3停止、自動再試行なし | mock実行OK |
| `kpg04_probes.json`/`_build.py` | 検証ケース48件 | 整合test PASS |
| `kpg04_manual.py` / `kpg04_page.py` | 2軸Rubric定義・実読記録先 / Before/Afterページ | ページ生成OK(実データのBefore列表示とmock) |
- **事故の記録(隠さず報告)**: 初版のtestで「phase停止点超過」の確認が誤った条件(累計50に対し停止点55)で実際のOpenAI呼出まで進み、`max_output_tokens=10`が下限未満のため**HTTP 400で拒否**された(課金なし・台帳記録なし・内容はテスト文字列"x"のみ)。直後にtest冒頭で`B.call`を例外化する安全網を追加し再発不可にした。実費は0円。
- Cap既定0・未設定の確認: 環境変数`KPG4_CAP`が無い状態で`kpg04_run.py`の有料runはCapReachedで拒否(testで確認)。委任_02でFableが額を確定するまで実行されない。
- 未確認(実走で確認): GEN5の構造化出力で`headword_frame`とtokensが実際にどの程度食い違うか/solのCHK実費/N2のGEN5 outputトークン量/flag率の未知誤りへの感度/ds-v4-proの非thinkingでの精度。

## 8. 判断依頼・リスク
- 新ルール性のある事項(Trial内の評価・設計規則であり、Production採用ではない): 「見出しの標準用法でsomeone/somethingを決める(擬人化でも)」「意味が変わる一般化は本文の形へ戻す」「限定独立検査の追加費用」。**採用時**はユーザー判断(Closeout案=USER_DECISION_REQUIRED候補)。
- リスク: ①probeの期待形が辞書的に争いうる(例: `give it a try`は両形が可なので除外済み)。実行前にFable確認を推奨。②E1Lの選定段の語義取違え(SEL: 価値や効果を損なう)は**根本的には残る**(N系はアンカー伝播を断つだけ)。SELの語義誤りがGENで再導出されないケース(GEN5がsource_senseを自力で正しく出せない場合)はN4のCHKが最後の砦。③母数が小さい(14ケース約80件+probe42件+held-out約40件)ため率の差は数件で動く。判断はS軸NGの**絶対件数0**を主とする。④未知の誤りクラス: P0再監査で顕在化する可能性。

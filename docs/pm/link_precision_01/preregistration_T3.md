# 事前登録 T3: Stage1 r3 support_fact_ids の文→factリンク精度(OPEN-233-SENTENCE-FACT-LINK-PRECISION-TRIAL-01 委任_01)

登録時刻: 2026-10-08 00:51(API実行前。r3出力は未取得)。Trial/DEV。Production変更なし、`APPROVED_FOR_PRODUCTION`なし、runner/checker未編集、git無し。上限¥40、¥35でSTOP。

## 1. 対象と方法
- 対象(dev主集計): stage1_candidate_rate.json で`run`を持つ22 run(CCP 13記事 + E2E_02 P2 4 + polysemy_04 5、既存47項目)。EN本文=`b1b/article.md`(replay_libのload_runと同じ)、台帳=その`research_ledger/verified_fact_ledger.txt`。委任文の「33記事」はheld-out10 run+B3等を含む数であり、dev項目に紐づくのは22 run(stage1_candidate_rate.mdの分母)。
- 呼び出し: `cov.run_stage1_coverage(fixture, call_fn, routes="r3_only", segment_fn=vs_sentence_segments_l6, initial_extra=CAUSAL_SENTENCE_INITIAL_EN, negation_mode=STAGE1_NEGATION_MODE)`を`OPEN233_SAVE_R3_SUPPORT_IDS=1`で1回(Stage1 r3のみ、r5/Stage2/Rewrite無し)。runnerの`make_stage1_call_fn`(effort=r3既定のmedium)をそのまま使う。**prompt・コード不変、調整なし**。
- 追加(step3専用): B3 trial記事3本(hormuz cdwb=V6/b1/w1、hormuz cf8v=V1/b1/w1、space_weapons 637f=V3/b2/w1。Stage1ログ無し)も同条件で1回(¥2程度)。(a)の主集計には入れず別掲(step3の否定型3件のため)。
- oracle(文): `oracle_dev.py`(Claudeが既知NG項目のJA/EN説明から対応EN unitを人手で対応付け、r3出力を見る前に確定)。located=29項目(うちfact_id既知=21、fact_idなし=8)、未特定18(理由付きで`oracle_dev.py`)。複数unit対応は2項目(qrfc-n1, g8qg-n1)で、いずれかのunitにoracle factがあればヒット。人間確認なし。
- oracle(記事): `storyline_b3/fact_selection_evidence.json`の`selected_fact_ids`(記事の正解集合)と台帳の全fact ID。
- 注意(既知の偏り): fact_id既知21件のうちMUSE-HC-012が8件(meta記事の方向型)。

## 2. 指標
- (a) 既知NG文(located ∧ fact_id既知=21)で、保存された当該unitの`support_fact_ids`にoracle fact_idを含む率(**strict、合否対象**)。参考(a2)=`support_fact_ids`∪Stage1候補の`related_fact_ids`(CANDIDATE判定のunitはschema上support_fact_idsが空になり得るため)。型別内訳も出す。
- (b) 全judged unit(split.units のうち`judged`=True)のうち、support_fact_idsが非空のunitについて「記事のselected_fact_idsの部分集合」である率(妥当性)。参考: 台帳の全fact IDの部分集合率(ID実在性)、selected外だが台帳内のID参照率(未選定factの参照=Writer漏洩または誤リンクの候補)。
- (c) judged unitのうち`support_fact_ids`が空の割合。および既知NG(located 29)のうち空の件数(型別: 否定・不在、主語新規出現、「新しい世界主張(対応factなし)」6件=known_relation_ng.ledger_correspondence)。model_verdict別(SUPPORTED/CANDIDATE)にも分ける。
- (d) 3記事×3回: ai_control(e2e_02 P2 rep2)、hormuz(e2e_02 P2 rep2)、meta(e2e_02 P2 rep1)の各runを追加2回(計3回)。unitごとにsupport_fact_idsの集合(空集合も値)が3回とも同一の率(全judged unit)。参考: SUPPORTEDが3回とも同じunit内での一致率、「NG located unit」での一致。
- 費用: Stage1 r3 API実費の合計(call_logのcost_jpy)。

## 3. 合格ライン(件数ベース、dev)
- (a) strict >= 21件の70% = 15/21以上
- (d) 3/3一致 >= 80%(全judged unitに対する3回とも同一集合の率)
- 費用 <= ¥40(¥35でSTOP)
- 総合PASS = 上3つ全て満たす。1つでも欠けたらFAIL(読み替えない。CONDITIONAL無し、結果は事実のみ記載)。
- (b)(c)は合否外の記述指標。
- held-out: 1回のみ(10 run、既存19項目を手順4でoracle対応付け)。dev合格ラインを再適用せず、(a)(b)(c)の方向(dev比で同方向か)のみ確認。held-outはdev確定後に開く。

## 4. 作業3(¥0)「未提示→不在断定」型の決定論規則(r3リンク使用、API無し)
規則R(unitを印付け): (i) 当該unitの`support_fact_ids`が空 ∧ (ii) 否定語(正規表現`\b(no|not|nor|never|none|neither|without|nothing|nobody|cannot)\b|n't|\b(lack|lacks|unknown|unclear)\b`)を含む ∧ (iii) 台帳に「未提示」マーカーを含むfactがあり、そのfactとunitが実体語(英数字4文字以上の内容語・数値・固有名詞、台帳がJAのときはラテン文字語・数値のみ照合可能)を1語以上共有する(**R2**)。
- マーカー(台帳fact block内の正規表現、case-insens): `未提示|示されて(い)?ない|示されていません|明記(されて)?(い)?ない|不明|確認できない|公表されて(い)?ない|開示されて(い)?ない|言及(が|は)ない|not (stated|specified|provided|disclosed|shown|explained|identified|reported|confirmed|clear|known|available)|unknown|unclear|unspecified|not been (shown|reported|explained)`。
- 参考のR1(緩い版)=(iii)を「台帳(記事)に未提示マーカーを含むfactが1件以上ある」に置換。台帳がJAの記事ではEN文×JA台帳の語照合ができないため、R2の(iii)はラテン語・数値共有に限られる(限界として明記)。
- 評価: dev(22 run+B3 3記事)で、T1が見逃した否定型既知NG(jb9k-n4、jb9k-n5、hormuz-cdwb-n1、hormuz-cf8v-n2、space_weapons-637f-n2。jb9k-n3は参考=T1で当たり)のうち規則が印を付けた件数、印の付いた文/記事。475j-n1はheld-out項目なので手順4(held-out)でのみ評価する。
- 目安(事前に置く、合否ではない): 再現率>=3/5、印の付く記事>=記事の90%でなければ参考値。負荷の絶対基準は置かない(T1の6%水準を参照するのみ)。

## 5. 実行・並行
`Get-Process python*`確認済み(別プロセスあり、並行タスクのAPI使用中)。自分の同時プロセスは1本。出力先`er052_output/open233_link_precision_01/`。費用は`cost.json`に逐次記録。

## 6. 追記(2026-10-08 00:57、dev集計前。r3出力1件(ai_control control rep1)の目視のみ後)
- 観察: r3が返す`support_fact_ids`に、台帳のID表記と異なる略記(例 `E008`/`E009`/`E011`。台帳は`EVID-008`等)が混ざる。合否判定の主指標は**事前登録どおりstrict(文字列完全一致)**のまま変えない。
- 補助として**post-hoc正規化版**を併記(合否に使わない): 台帳IDに無い表記は「同じ末尾数字を持ち先頭1文字が同じ台帳IDがちょうど1件」ならそのIDに読み替える(曖昧・不一致は未解決)。(a)(b)(d)でstrictとnormalizedの両方を出し、ID表記ゆれの影響を分離して記述する。
- (b)のstrictは「完全一致で台帳IDに存在」「完全一致でselectedの部分集合」を数える。
- 集計スクリプト: `er052_output/open233_link_precision_01/analyze.py`(API無し、決定論)。

## 7. 追記(2026-10-08 01:12、dev集計・step3(dev)完了後、held-out実行前)
- dev確定値は`er052_output/open233_link_precision_01/dev_summary.json`・`step3_dev.json`。ここでheld-out(10 run、既存19項目)を開いた。oracleは`oracle_heldout.py`(located 16・未特定3、うちfact_id既知14)。r3出力を見る前に確定。held-outは1回のみ、dev合格ラインは再適用せず方向のみ。step3のheld-out評価対象=475j-n1(委任文指定)とspace_weapons-89wf-n2(否定・不在型)。

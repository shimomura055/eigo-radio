管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01
日付: 2026-09-30
種別: L2 批判的レビュー #2(read-only)
**runtime evidence**: ユーザー指定`claude-opus-5-5`はClaude Code 2.1.272
未対応で400(request id req_011CfYtRLufxFRkDoga2oVg7)→ 起動時
オーバーライドで`claude-opus-5[1m]`(Opus 5、cutoff 2026-05)にて実行。

以下、末尾「=== Opus L2 レビュー #2 全文 ===」以降を一字も変えず保存。

---

=== Opus L2 レビュー #2 全文 ===
## 0. runtime evidence
自認モデル: Opus 5 (1M context) / exact model ID: `claude-opus-5[1m]`(system prompt記載) / knowledge cutoff: 2026年5月。本レビューは read-only(編集・実行・API 呼び出しなし)。

**評価対象の一次証拠**: `er052_output/open233_self_recovery_flow_runner_01_iter2/instances/*.json`(29件、Stage4 到達7件は全文精読)、同 iter1、`er052_open233_self_recovery_flow_runner_01.py`、`er052_open233_self_recovery_stage2_production_01.py`、`er052_output/open233_self_recovery_r2prime_recalibration_01/summary_r2prime_recalibration.json`、設計書 §3-1/§3-3/§4-2/§4-3/§5-4/§5-5/§7-0/§9-1⑦/§13-6/§13-11。REPORT §8/§9 は該当箇所のみ grep 照合(設計書 §9-1⑦ と同内容を確認)。**報告書の原因分類と raw instance json が食い違う箇所があり、以下は json を優先しています。**

---

# 論点1: 残る Escalation 7件の原因

【所見】7件すべて `stage4_reason = same_claim_fact_id_reblocked`。しかし実体は**5類型**で、報告書の分類(「B1・B4・A2A3・A4 = J-1 locate 失敗の残存」)は **B1・B4 については誤り**です。

| instance | 真の原因 | 分類 |
|---|---|---|
| safety_A2A3 | HF-006 の J-1 が `j1_pair_not_located`、**編集が一切適用されず**同一文が cycle2 で再検出 | 実装バグ(下記A) |
| safety_A4 | MUSE-HC-012 が `j1_failed+ja_fulltext_fallback` → **JA だけ書き換え EN は無編集**(コード上の仕様)。加えて MUSE-HC-006 は cycle2 で*別の文*が再検出 | 実装バグ(A/B)+兄弟文カスケード |
| meta_run03_standard | cycle1 で "They did not realize it." を修正 → cycle2 で**同一段落の隣接文** "users could not know. They could not tell…" が同 fact_id で再検出 | 兄弟文カスケード |
| meta_run03_advanced | 同型(MUSE-HC-012、条件節が残る) | 兄弟文カスケード |
| bgroup_B4 | cycle1 で "Meta had run a test that produced exactly this kind of surprise." を修正 → cycle2 で**直前の hook 文+タイトル**が同 fact_id で再検出。cycle1 の 4件すべて `guard_ok=true`(locate 失敗ではない) | hook/タイトル未到達 |
| neg1_meta_b3prod_a2 | cycle1 で本文を修正 → cycle2 で**タイトル** "We Thought It Was AI—But There Was a Person…" が再検出 | hook/タイトル未到達 |
| bgroup_B1 | 記事の**主題そのもの**(見出し「市場が見ているのは『言葉』より海の安全」+ thesis 段)が HF-011 notes 禁止の因果断定。局所編集後も主題が残る。Stage2 は §7-0 の正解ラベル通り(B1-a/B1-b=ACCEPTABLE、B1-c=BLOCKING)に**正しく**判定している | 方式の限界 |

【Evidence】
- 実装バグA(locate 失敗で fallback に行かない): `C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01.py:763-765` — `if en_target is None or ja_target is None: return {... "method": "j1_pair_not_located", "guard_ok": False}` で**早期 return し、下の全文 fallback ブロック(782行〜)を飛ばす**。→ テキスト無変更のまま recheck → 同 fact_id 再検出 → 335行の A5 ルールで即 Stage4。safety_A2A3 cycle1 `rewrite_records[1].method="j1_pair_not_located", guard_ok=false`。
- 実装バグB(JA fallback 時 EN 無編集): 同ファイル `:794` — `updated_en = en_full  # EN側はcycle 2のEN Recheckで再評価に委ねる`。EN 側逸脱は必ず残り、同 fact_id で再検出 → 即 Stage4。safety_A4 cycle1 `method="j1_failed+ja_fulltext_fallback"`。**副作用として JA と EN が乖離した記事対が生成される**(下記論点4)。
- 停止判定が fact_id 粒度: `:203-208 claim_identity()` は `related_fact_id` があれば `f"fact:{fact_id}"` を返す(claim 本文を見ない)。`:1071-1078` で `current_ids & prior_ids` があれば即 Stage4。一方**設計 §3-3(:334-338)の意図は「Rewrite が当該 claim に効かなかったことが実証された場合」**で、「異なる claim が新規に BLOCKING になった場合のみ cycle2 を発火」と明記。→ **実装が設計意図より厳しく、別文なのに「効かなかった」と誤判定している**。
- tail 証拠: meta_run03_standard cycle1 blocking 2 → cycle2 1、B4 4 → 1、A2A3 2 → 1。**進捗しているのに打ち切られている**。
- B1 の正解一致: 設計書 §7-0(`docs/pm/design_open233_self_recovery_flow_01.md:1177-1179`)と iter2 の materiality が完全一致。

【Trial 実装の改善で解消可能 / 方式の限界】
- 改善で解消見込み: A2A3(A修正)、A4(A/B修正+段落化)、meta_std、meta_adv、B4、neg1(タイトル込み段落 Rewrite + 停止判定の是正)= **6件**
- 方式の限界: **B1 のみ**。記事の angle 自体が Ledger 非支持のため局所編集不能。ここでの Stage4 は「機構の失敗」ではなく**正しい挙動**(人間が angle を変えるべき)。

【Safety リスク】停止判定を claim 本文一致まで緩めても最終 gate は fail-closed(cycle 上限後 Stage4)なので**Safety 緩和には当たらない**。ただし編集回数が増える分、**Rewrite 由来の新規逸脱**リスクは上がる(現在これを検出する差分QAは未実装、論点4参照)。

【Cost 影響】cycle 3 を「blocking 件数が厳密に減った場合のみ」許すと、該当 instance だけ +Stage2 1 + Rewrite n + Recheck 1 ≈ **+¥0.4〜0.8/instance**。全体平均では +¥0.1 未満。段落単位 Rewrite は出力 token 増で +¥0.02〜0.05/call 程度。

【推奨案(優先順)】
1. **`j1_pair_not_located` を全文 fallback へ配線**(バグ修正、¥0、リスク最小)。
2. **JA 全文 fallback 後に EN 側も必ず編集**(同 hint で E-2 を 1 call、または「同 fact_id だが EN 未編集」の場合は停止判定から除外)。
3. **停止判定を `fact_id + 正規化 claim 本文の近似一致`へ**(設計 §3-3 の原意に戻す)。別文なら cycle 3 を 1 回だけ許可(上限 3、blocking 件数減少が条件)。
4. **Rewrite 対象単位を「引用文 → 同一含意を持つ段落ブロック(見出し/タイトル行を含む)」へ拡張**。hint に「この段落内で同じ含意を述べる全ての文を削除・限定せよ」を追記。
5. Stage2 で narrow_scope を QUALITY 扱いにする案は**推奨しません**(§7-0 で B1-c/hormuz_run03_standard=BLOCKING が確定しており、正解ラベルと衝突。かつ残存7件のうち4件は `changed_certainty` floor で止まっており rubric では動かない)。
6. 「cycle2 で同一 claim 再 BLOCK 時に全文 must-fix を1回許す」案は**次善**。効果はあるが Production では Advanced/Standard 再生成(§13-6 `c_ja_full` ¥3.49〜4.02)を伴い Cap を割る恐れ。まず 1〜4 を試すべき。

【USER_DECISION_REQUIRED】1〜4 は該当なし(Trial 内実装、Safety 緩和なし、Cap 内)。6 は Cap 超過の可能性(条件3)に触れうる。

---

# 論点2: S1-U の採否

【所見】
- (a) 「recall miss 3件を全捕捉」は事実だが、**`s1u_caught_recall_miss` の定義は「S1-D が BLOCKING を1件でも返した」でしかなく、真の miss かどうかを検証していません**(`er052_open233_self_recovery_flow_runner_01.py:988-990`)。実測では 7件中6件で追加 BLOCK が発生し、うち **neg6 / neg7 は negative fixture(正解 ACCEPTABLE)**。S1-D の「不要 BLOCK 86%」がそのまま再現しています。
- (b) neg7 の S1-D 発火 → Rewrite が **Ledger と整合しない可能性のある narrowing** を生成: `neg7_meta_prodrunner_b1b.json:34,60` の rewrite_hint は「Meta**従業員を対象とした**社内テストで適切な開示がなかった、という範囲に狭めてください」。開示不足の対象は通話相手/利用者であり、従業員へ狭めるのは actor の付け替えに見えます(断定はしません、Ledger 原文照合が必要)。**recheck は LEDGER_COMPLIANT で通過**しており、Rewrite 由来の新規逸脱を検出できていません。
- (c) 「副作用 = meta_run03_advanced を S1-U が新規捕捉して Stage4」は**誤帰属**です。`meta_run03_advanced.json:122-125` は `stage1_call_used: true, s1u_screen_used: false` — つまり **V4-A 本体が iter2 で検出した**(iter1 は同じ fresh call で PASS、`er052_output/open233_self_recovery_flow_runner_01/instances/meta_run03_advanced.json:5,8`)。これは **V4-A の run 間 recall 変動**の実例で、S1-U のコストではありません。
- (d) コストの性質: S1-U 単価は**入力ではなく reasoning token 支配**。`hormuz_run02_advanced.json:75-81` = cost ¥0.3935、`input 5410 / cached 5407`(=99.9% cache hit)、`output 4908 / reasoning 4657`。**「caching prefix で ¥0.1〜0.2 へ」は既に cache が効いていても実現していません**。S1-D は `reasoning={"effort": vfl01.REASONING_EFFORT}` = **"high"**(`er052_open233_self_recovery_s1d_trial_01.py:199`、`er003_v1_en_direct_vfl_01_generate.py:58`)。

【Evidence】S1-U 7 call の実額: neg4 ¥0.6757 / hormuz_run03_adv ¥0.4778 / hormuz_run02_adv ¥0.3935 / B3 ¥0.2768 / B2 ¥0.4453 / neg7 ¥0.4209 / neg6 ¥0.4689 = **¥3.1589、平均 ¥0.4513**。

【Safety リスク】S1-U 廃止 = 現行 Production STOP 実例(hormuz_run02_advanced)を含む 3件の見逃しが残る(実害あり)。S1-U 採用 = 正常記事へ不要 Rewrite を強制し、Rewrite 由来の新規逸脱が recheck をすり抜ける経路が増える(neg7 が候補)。

【Cost 影響】¥0.45/variant。1記事 = standard + advanced の2 variant なら **¥0.9/記事**(+¥3 Cap の 30%)。ユーザー優先順位「全記事への固定追加 call を避ける」と正面衝突。

【推奨案(優先順、安い代替を含む)】
1. **【最優先・最安】2×V4-A union を先に試す**(¥0.22/call 前後、S1-D の半額)。根拠: meta_run03_advanced が同一 prompt の再実行で PASS→DEVIATION に変化した実例があり、recall 欠落の相当部分は「サンプリング変動」。S1-D の別 rubric(不要 BLOCK 86%・B1-c/B4-a 誤降格)を持ち込まずに recall を稼げる可能性がある。7 instance の再測定で ≈¥1.5。
2. **S1-U の reasoning effort を下げる**(high → medium/low)。cost は reasoning token 支配なので **¥0.1〜0.2 圏に落ちる見込み**。受入条件: 既知 3 miss を全捕捉 かつ negative 7 件で追加 BLOCK ≤1。7 call ≈¥1。
3. 採用するなら **S1-U 由来 claim は Stage2 の floor 免除**(S1-D 出力には `issue`/`explanation` も 10 flags の実質値も無く[例: `neg6_smallbag_div_b1b.json:15-26`]、floor 判定に必要な情報が欠けている)。fail-closed を維持しつつ、S1-U だけが検出した claim は「Rewrite は行うが解消できなければ QUALITY 相当で継続」とする案は **Safety 緩和(条件2)に該当**するため単独判断不可。
4. V4-A と S1-D の 1 call 統合は**推奨しません**。S1-U の価値の一部は「独立した2回目のサンプル」であり、1 call に統合すると独立性が失われます(上記 1 の方が理に合う)。
5. Standard 段のみ適用は**根拠が薄い**: 今回の miss は advanced 側(hormuz_run02/03_advanced)に出ています。

【USER_DECISION_REQUIRED】S1-U の Production 既定採用は条件4(Production 採用・配線)と、固定費増の是非(ユーザー優先順位)としてユーザー判断。上記1/2の**Trial 内比較実測は判断不要**。

---

# 論点3: Stage 2 Productivity(negative 0/4、R2' 失敗)

【所見】「rubric を精緻化すると Safety と Productivity が同時に動く」という見立ては、今回のデータでは**やや的を外しています**。実際の構造は3つに分離できます。

1. **Stage 2(R2)は正解ラベルにかなり忠実**。B1 の3 claim は §7-0 の正解通り(ACCEPTABLE/ACCEPTABLE/BLOCKING)に判定されています(`bgroup_B1.json:86-88, 186-188, 145-147`)。R2 が全面的に過剰厳格なわけではない。
2. **QUALITY は 29 instance で 1件も出力されていない**(`summary_flow_runner.json:26 "quality_claims": []`、`escalation_zero_breakdown.quality_pass: 0`)。3値 rubric は実運用上 2値(BLOCKING/ACCEPTABLE)として振る舞っており、**中間帯の救済路が存在しない**。B4-b は cycle1 で BLOCKING、cycle2 で ACCEPTABLE(`bgroup_B4.json:130, 296`)= **同一 run 内で同一 claim の判定が反転**(境界帯の分散)。
3. **negative 4件の過剰 BLOCK は分散ではなく安定**(R2/R2' × 2 run すべて BLOCKING、`summary_r2prime_recalibration.json:298-362`)。かつ **neg1 の最終 blocking は `deterministic_floor:changed_certainty`** で止まっており(`neg1_meta_b3prod_a2.json:111`)、**rubric を変えても動きません**。残存7件のうち4件(B4/neg1/meta_adv/A4)が changed_certainty floor 拘束です。

→ 結論: **Stage 2 rubric は Productivity の主因ではなく、主因は (i) changed_certainty floor と (ii) Rewrite の到達範囲**。よって「rubric 較正をもう一周」は投資対効果が低い。

【Evidence】上記 file:line。加えて「原油高→ガソリン/物流費」型の同種 claim が B1 では ACCEPTABLE、safety_A2A3 では BLOCKING(`safety_A2A3` HF-006、`summary_flow_runner.json:936-972`)という instance 間の不一致もあり。

【Safety リスク】`changed_certainty` floor を外すことは **Safety 緩和(条件2)**。§4-3 は B4-d のラベルと floor を一致させるために意図的に追加したもので、ここを緩めると er009_changed_certainty 型("proven beyond doubt … every customer")の保護根拠が薄くなります。**推奨しません。**

【Cost 影響】Stage 2 の「降格による救済」は iter2 で **0 instance**(`rescreening_auto_resolved_count: 0`)。一方 Stage 2 の実効価値は (a) `rewrite_hint` 生成(iter2 の最大の改善要因)と (b) claim 単位 ACCEPTABLE による**不要 Rewrite の抑止**(B1-a/B1-b/B4-b の3回を回避)。よって **「Stage 2 を省いて Rewrite 直行」は非推奨**(hint を失う代償が大きい)。ただし Stage 2 を「materiality 判定器」ではなく**「hint 生成器 + ACCEPTABLE フィルタ」**と再定義し、reasoning effort を下げて単価(現 ¥0.16〜0.29/call)を削るのは合理的。

【推奨案(優先順)】
1. **決定論層(¥0)による事前 ACCEPTABLE は作らない**。negative の過剰 BLOCK は「Ledger 事実からの推論(未記名者の心理・反応)」型で、文字列規則で安全に切り出せません。
2. **rubric に足すのは「手順」でも「例示」でもなく、ACCEPTABLE 節の*対象範囲*を1文**: 「Ledger が記録した事実から論理的に導かれる範囲の言い換え・含意で、新規の固有名詞/数値/時期/主体を一切加えないもの」。R2' が試した「段階的手順+例示」とは別軸。受入条件は Safety 12 + A2A3/A4/A5 の BLOCKING 維持 0 件崩れ。n=2、20 call ≈¥3.5。**ただし neg1 等は floor で止まるため、これ単独の Productivity 改善幅は小さい(期待 1〜2 claim)**ことを前提に。
3. 「止める理由の反証形式」(= Ledger と*矛盾するか* Yes/No に限定した第2問)は、floor 非該当 claim のみに 1 call(≈¥0.1)追加する案として試す価値があります。fail-closed 既定(No と言い切れなければ BLOCKING 維持)を保てば Safety 中立。
4. negative fixture は **rubric の例示に使わず regression 専用**に。同意します(R2' の A4-0 誤降格は例示追加の副作用と整合)。

【USER_DECISION_REQUIRED】2/3 は Trial 内較正で該当なし。floor 緩和は条件2 で該当。

---

# 論点4: J-1 の残リスク

【所見】Production 化前に必須の未検証項目が**4つ**あり、うち2つはコードで確認できる実害です。

1. **JA/EN 整合(忠実英訳)は一切検証されていません**。`ja_recheck` は JA 本文を *Ledger* に対して再チェックしているだけで(`er052_open233_self_recovery_flow_runner_01.py:1117-1119`)、JA↔EN の対応は見ていません。
2. **`j1_failed+ja_fulltext_fallback` は JA を全文書き換えつつ EN を無編集で残す**(`:794`)。**JA/EN 乖離が構造的に発生します**(safety_A4 cycle1 で実発生)。Production では JA original と EN 記事が別内容になる = Product 上の重大欠陥。
3. **guard は事実上「変化検知」のみ**: `:698-699` `guard_ok = (updated_text != full_text and claim_text.strip() not in updated_text and not delete_reoccurrence_detected)`。§5-5 が継承すると謳う **差分QA(`run_diff_qa_for_accepted_rewrite`)・文体/記号/段落 Gate はこの runner に実装されていません**(grep で該当なし)。§5-5 自身も J-1 については「JA版差分QAが無いため Phase 1 では全文 Recheck と diff ログの事後観測に留める」と明記(`design…:1082-1086`)。
4. **locate 失敗 18%(2/11)の扱い**: 1件は上記バグAで**無編集**、1件は JA 全文 fallback で **EN 乖離**。つまり現状 locate 失敗 = 100% で Escalation か整合崩れに直結します。

【Safety リスク】Rewrite 由来の新規逸脱を捕まえる層が無い。neg7 の「Meta 従業員を対象とした社内テスト」への narrowing が recheck を LEDGER_COMPLIANT で通過した事実は、この穴が実際に空振りしている可能性を示します(確定ではない)。

【Cost 影響】差分QA を全 Rewrite に付けると +1 call/claim(≈+¥0.1〜0.2)。JA fallback 後の EN 編集は +1 call(≈+¥0.1)。いずれも Cap 内。

【推奨案(優先順)】(1) JA fallback 後の EN 編集を必須化、(2) paired rewrite 後に **JA↔EN 等価チェック 1 call**(既存の翻訳忠実性チェック資産があればそれを流用、無ければ「JA と EN が同一事実を述べているか」の Yes/No)、(3) 受理後の差分 QA(新規固有名詞/数値の出現検出は決定論で ¥0 でも可能: 編集後テキストに Ledger 未出の数値・固有名詞が増えていないかの precheck 再実行)、(4) 文体/記号/段落 Gate を編集後全文に再適用。**(1)(3) は iteration 3 に入れるべき最小セット**。

【USER_DECISION_REQUIRED】該当なし(いずれも Trial 内の検証追加)。

---

# 論点5: KPI 到達の見立て

【所見】**現状の KPI(10〜20記事で USER_DECISION_REQUIRED = 0)は到達しない見込みです。** 理由は3つ。

1. **分母の問題**: 29 instance のうち Production 記事に相当するのは実 run の 6 instance(hormuz run01/02/03_adv, run03_std, meta run03_std/adv)のみ。この 6 での Escalation は **2/6(33%)**(meta_run03_standard, meta_run03_advanced)で、全体 24% より**悪い**。合成 Safety 12 件(意図的に改竄した fixture)を分母に含めるのは、Phase 2 の「実記事のみ」分母とは別物であり、**Escalation 率の比較には使えません**(Safety 群は「BLOCK が正しい」群なので、率の分母に混ぜると率が希釈されます)。今後は必ず群別に出すべきです。群別実測: Safety 2/12、B群 2/4、negative 1/7、実 run 2/6。
2. **記事単位への合成**: 1記事 = advanced + standard の2 variant で、どちらかが Stage4 なら記事として USER_DECISION_REQUIRED。variant 率 p=0.2 でも記事率 ≈ 1-(0.8)² = 36%。10記事なら期待 3〜4件。**0 件は統計的に非現実的**。
3. **negative 群の挙動が最も重い**: 今日 V0 で普通に通っている 7記事のうち、iter2 では **neg4 の1件だけが無編集で通過**し、neg1 は Stage4、neg2/neg3 は Rewrite 後 downgrade、neg5/neg6/neg7 は Rewrite 実行。つまり**現行なら人手不要で出荷できる記事の 6/7 が自動編集され、1/7 が STOP になる**。これは KPI 未達であると同時に、**「安全≠成功」観点で最大の Product リスク**(編集後の読み物としての品質が一切評価されていない)。

【Evidence】各 instance json の `final_state`(iter2 一覧は上記)、`summary_flow_runner.json:12-19`、`design…:1636-1648`。

【iteration 3 の最小変更セットと理論到達値】論点1推奨 1〜4 + 論点4推奨(1)(3)を入れた場合:
- 解消見込み: A2A3, A4, meta_std, meta_adv, B4, neg1 の6件 → **理論上 1/29(B1 のみ、3.4%)**
- 現実的見積り: Stage1/Stage2 の run 間分散と、段落編集による新規逸脱発生を織り込んで **2〜4/29(7〜14%)**。実 run 分母では **0〜1/6**。
- ただし **B1 型(記事の angle 自体が Ledger 非支持)は原理的に残り**、これを 0 にするには上流(Writer が Ledger 非支持の angle で書かない)を直すしかありません。

【Safety リスク】KPI を下げる方向の再定義は Safety 緩和ではありませんが、「事象単位推定へ変更」は KPI 変更(条件1)。

【Cost 影響】iteration 3 の 29 instance 再実行 ≈¥30〜36(iter2 ¥26.03 + 追加 call 分)。

【推奨案】KPI を「記事単位 0件」から **「(a) 重大 Fact 見逃し 0 件は据え置き、(b) Escalation は *core-framing 型*(B1 型)のみ許容し件数と理由コードを報告、(c) それ以外の機構起因 Escalation を 0 件」** へ再定義することを**ユーザーに提案**すべきです。REPORT §(`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md:310-316`)で既に「KPI 判定方法の再定義」が USER_DECISION_REQUIRED として提示済みなので、そこに今回の実測根拠(群別率・記事単位合成)を添えるのが筋です。

【USER_DECISION_REQUIRED】**該当(条件1: KPI 変更)**。Fable/Claude 側で決めてはいけません。

---

# 論点6: Phase 2 設計

【所見・推奨案(優先順)】
1. **記事の選び方 = 既存 run の再利用を第一候補**。理由: (a) 生成費 ¥0、(b) CLAUDE.md の「新規記事テーマはユーザーが選定」ルール(PM_GOVERNANCE §13)を回避でき、Fable が単独でテーマを決めてしまう事故を防げる、(c) 現行 Production の合否ラベルが既にあるため「今日通っている記事が STOP/改変されるか」という最重要指標(論点5-3)を直接測れる。**新規テーマ生成はユーザー選定が必要**なので、必要なら別途伺うこと。
2. **必須の測定単位是正**(¥0): 群別 Escalation 率(実記事 / 合成 / negative を分離)、**記事単位(std+adv 合成)の Cap 実額**、instance 単位ではなく記事単位の worst case。
3. **Cap 判定に必要な計測の穴**: 現在の「worst ¥2.4664 < +¥3 Cap」(`design…:2372-2379`)は3点で楽観バイアス。(a) **instance(1 variant)基準**で、記事は 2 variant 合算(実測でも meta run03 は ¥1.1069+¥1.475=**¥2.58/記事**、両 variant が tail なら ≈¥4.9 で Cap 超過)。(b) **JA 全文 fallback 後の EN 再生成費(§13-6 `c_ja_full` ¥3.49〜4.02)が計上されていない**。(c) 多くの instance は Stage1 出力を再利用して課金していない。→ Phase 2 では **記事単位・fallback 発火ケースを含む実額**を必ず取る。
4. **モデル差(gpt-5.6-luna vs gpt-6-luna)**: Production Stage 1 は gpt-5.6-luna、Trial は gpt-6-luna(`design…:1738-1740`)。**Escalation 率はモデル差で移らない可能性が高い**(Stage1 の recall/精度が率を支配している)ので、Phase 2 では Stage 1 のみ両モデルで 10 variant 程度の A/B(≈¥5)を先に取り、率を外挿する根拠を作るべき。
5. **反復回数**: Stage1(V4-A)は run 間で PASS/DEVIATION が反転する実例がある(meta_run03_advanced)ため、**同一 instance n=2 以上**でないと Escalation 率の CI が意味を持ちません。
6. **shadow sampling**: 新規 Production run が走るたびに artifact を読み取り、flow を read-only で後追い実行してログのみ残す(Production 出力は変更しない)。Phase 2 の分母を安く増やせます。
7. **予算配分案(残 ¥332)**: iteration 3(29 instance 再実行+S1-U 代替2案の比較)≈¥40 / Phase 2 本測定(10記事×2 variant×2 反復 = 40 instance、Stage1 fresh 込み)≈¥70 / Stage1 モデル A/B ≈¥5 / shadow 追加 20 instance ≈¥30 / 予備 ≈¥187。**Guardrail は各段で従来どおり 1.5〜2倍で設定**。
8. iter1→iter2 の 9→7 比較は**厳密な paired 比較ではありません**: B2/B3 は iter1 で `stage1_recall_miss_substituted: true`(手動代替)、iter2 では S1-D 由来の別 deviation 集合(`er052_output/open233_self_recovery_flow_runner_01/instances/bgroup_B2_hormuz.json:111-112` vs iter2 の `:86-90`)。**「B2 が解消した」は改善効果と入力差が混在**しています。Phase 2 では入力 deviation 集合を固定した paired 比較を。

【USER_DECISION_REQUIRED】新規テーマで記事を作る場合はテーマ選定がユーザー(CLAUDE.md)。Cap 超過が判明した場合は条件3。Production 配線は条件4。

---

# 論点7: 「安全≠成功」検証

【所見】**「真の解消のみ・誤 PASS 候補 0」は現時点では信用できません。集計定義が 5 instance を素通りさせています。**

【Evidence】`er052_open233_self_recovery_flow_runner_01.py:1174-1179`:
```
true_resolved = sum(... if r["final_state"] == "RESOLVED_REWRITE" and any(c.get("recheck_all_prior_issues_resolved") ...))
unresolved_unknown = sum(... if r["final_state"] == "RESOLVED_REWRITE" and not any(...))
```
3つのバケットすべてが **`final_state == "RESOLVED_REWRITE"` 限定**。`RESOLVED_REWRITE_THEN_DOWNGRADE` は**どのバケットにも入りません**。iter2 の rewrite_auto_resolved は 21 だが、breakdown は 16+0+0=16 → **差分 5 instance**(`safety_er009_unsupported_new_claim` / `hormuz_run01_advanced` / `hormuz_run03_standard` / `neg2_meta_refresh_a2` / `neg3_hormuz_prodrunner_b1b`)が未検査で「誤 PASS 候補 0」に数えられています。報告書 `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md:781-782` の「誤PASS候補0(全件Recheckで明示確認)」は、この 5 件について**成り立っていません**。
実例: `safety_er009_unsupported_new_claim.json` cycle1 は `recheck_overall_status: "LEDGER_COMPLIANT"` かつ **`recheck_all_prior_issues_resolved: false`**、cycle2 は `stage2_results: []`(Stage1 recheck に MAJOR が無いため Stage2 skip)→ 最終 RESOLVED。**「元の指摘が解消したと確認できていないまま合格」経路が実在します**。
prior_issues 併用自体は正しく実装されています(`:1102-1112`、`:346-349` で `len(resolved)==len(prior_issues) and all(resolved)`)。問題は**集計と、COMPLIANT かつ prior 未確認のときの扱い**です。

【Safety リスク】この 5 件のうち Safety 群の 1 件(unsupported_new_claim)は、実際には deterministic delete が成功しているので実害は無い可能性が高い。ただし**構造として fail-open の継ぎ目**であり、「安全≠成功」原則の観点では放置すべきでない。

【Cost 影響】¥0(集計定義の修正のみ)。個別監査も既存 json の読み直しで ¥0(haiku-worker 委任可)。

【推奨案】(1) breakdown の分母を `RESOLVED_*` 全体に拡張、(2) `overall_status == LEDGER_COMPLIANT` かつ `all_prior_issues_resolved == false` は **`unconfirmed` として明示計上**(合格扱いにしない、または追加1 call で再確認する)、(3) iter2 の該当 5 件を遡って個別監査、(4) `s1u_caught_recall_miss` を `s1u_additional_block` に改名し、真偽は正解ラベル照合で別列に。

【USER_DECISION_REQUIRED】該当なし(測定の是正)。

---

# 総合

## iteration 3 の最小変更セット(この順で)
1. **バグ修正2件(¥0)**: `j1_pair_not_located` を全文 fallback へ配線(`:763-765`)/ JA 全文 fallback 後に EN 側も編集(`:794`)。
2. **停止判定を設計原意へ**(`claim_identity` を fact_id 単独から fact_id+正規化本文へ)。別 claim なら cycle 3 を1回だけ許可(blocking 件数減少が条件)。
3. **Rewrite 対象単位を段落ブロック化(タイトル/見出し行を含む)**。hint に「同一含意の文をすべて」を明記。
4. **測定の是正(¥0)**: RESOLVED_* 全体での breakdown、群別 Escalation 率、記事単位(std+adv)コストと合否、`s1u_caught_recall_miss` の改名と真偽別列。
5. **Rewrite 由来新規逸脱の検出**: 編集後テキストへ precheck 再実行(決定論、¥0)+ paired rewrite 時の JA↔EN 等価 1 call。
6. **S1-U の安い代替の比較実測**: (a) 2×V4-A union、(b) S1-D effort=low/medium。7 instance ずつ、合計 ≈¥3。受入条件は「既知 3 miss 全捕捉 かつ negative 追加 BLOCK ≤1」。
7. 上記込みで 29 instance 再実行(≈¥30〜36、Guardrail ¥50 目安)。
- **やらないことを明示**: rubric の再精緻化(R2''）、changed_certainty floor の緩和、Stage 2 の省略。

## Phase 2 へ進む条件(私の推奨)
- (i) 機構起因 Escalation(バグ/兄弟文/タイトル型)が **iteration 3 で 0〜1/29** になっている。
- (ii) negative 7件のうち **Stage4 = 0**、かつ **自動編集された記事の読み物品質が人(またはユーザー)によって1度は確認されている**(現状ゼロ検証)。
- (iii) JA/EN 乖離経路(`:794`)が閉じている。
- (iv) 測定定義の是正(上記4)が済み、iter2 の 5 件の遡及監査が終わっている。
- (v) KPI の再定義についてユーザー回答が得られている(条件1)。
(i)〜(iv) は Trial 内で実行可能。(v) はユーザー待ち。

## 率直な到達見立て
- 「重大 Fact 見逃し 0」は、S1-U か 2×V4-A union のいずれかを入れれば**達成可能性が高い**(Safety 12 で false-negative 0、既知 3 miss も捕捉済み)。
- 「追加継続コスト ≤+¥3/記事」は、**instance ではなく記事単位で測り直すと余裕は薄い**(実測 ¥2.58/記事、tail の重ね合わせで ¥4.9 の可能性、JA fallback 後の EN 再生成費は未計上)。S1-U を全 variant に入れると +¥0.9/記事が固定で乗ります。**Cap 内と結論づけるのは時期尚早**です。
- 「Ledger/Deviation 起因 USER_DECISION_REQUIRED = 0」は、**現行定義では 10〜20記事で達成できないと見ます**(実記事分母で variant 33%、記事換算で過半)。iteration 3 の修正で機構起因はほぼ潰せますが、**B1 型(記事の angle が Ledger 非支持)は原理的に残り**、これは recovery 層の欠陥ではなく上流(Writer の angle 選定)の問題です。したがってユーザーに諮るべき最重要事項は「angle 起因 Escalation を KPI 対象外にするか、上流 Prompt を直す(= Production 変更、条件4)か」の二択です。
- 最後にもう一段強い懸念として: 本 flow の**正常記事への net effect が「7件中6件を自動編集、1件を STOP」**という実測値です(論点5-3)。Safety は改善していますが、**編集後の記事が読み物として成立しているかは一度も評価されていません**。Production 採用を論じる前に、この観点の評価(ユーザー自身による数記事の読み比べが最も安い)を挟むことを強く推奨します。

**Production 採用の可否は判断していません(人間ユーザーのみ)。本レビューは診断・助言のみで、実装・修正は開始していません。**
=== Opus L2 レビュー #2 全文 ここまで ===

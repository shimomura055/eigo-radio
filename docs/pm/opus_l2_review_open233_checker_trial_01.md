# Opus L2レビュー#1 逐語保存

管理ID: OPEN-233-CHECKER-REDESIGN-TRIAL-01
日付: 2026-09-29
種別: L2設計レビュー#1、read-only
Fable委任: 委任_04(逐語保存指示)
本文: 以下、Fable委任文に含まれていたOpus L2レビュー#1の全文を一字も変えず保存する。

**注記(2026-09-30追記、`OPEN-233-SELF-RECOVERY-TRIAL-01`委任_02。
以下本文は一切変更していない)**: Fableが2026-09-30に実施したOpus
model_id probe(read-only)により、実行時のOpus agentエイリアス
(`opus-consultant`、`model: opus`)の自己申告モデル名が「Opus 5
(1M context)」・exact model ID `claude-opus-5[1m]`・knowledge cutoff
2026-05であることが判明した。本レビュー実行時(2026-09-29)のmodel_id
は当時記録されておらず確定できないが、同一エイリアス経由であるため
Opus 5で実行された可能性が高い(Opus 5.5ではない可能性が高い)。詳細:
`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`§1、`DECISION_LOG.md`
2026-09-30`OPEN-233-SELF-RECOVERY-TRIAL-01`委任_02エントリ。

---

# OPEN-233 Opus L2 設計レビュー #1(read-only、診断・助言のみ。編集・実行・API呼び出しなし)

読んだ範囲: `docs/pm/design_open233_checker_redesign_trial_01.md`(全文892行)、Trial 1 Step2診断/Trial 2 Step1・Step2・Step3の実出力JSON、`er003_v1_en_direct_vfl_01_generate.py` L495-604(Prompt/post-hoc/HOOK)、Hormuz/Meta Ledger本文(HF-001/002/007/008/009/010/011、MUSE-HC-002/006/010)、`er051_open233_checker_trial_variant_01.py`のモデル呼び出しパラメータ部。`review_ledger_deviation_redesign_01_part_b.md`と`design_checker_redesign_v02_01.md`は直接読まず、設計書内の引用で代用した(論点2の materiality 評価は Part B を見ずに raw fixture から独立に行ったため、結果的に「独立評価」の要件は満たしている)。

---

## 論点1. 構造問題の代替設計

### 【所見】

**(A) 真の構造的原因は post-hoc 層ではなく、Production Prompt の severity 定義そのものにある。** 現行 `DEVIATION_PROMPT_TEMPLATE` の【判定ルール】は
- 「上記10種類のいずれかが**明確にtrueである場合のみ**、severityをMAJORにしてください」(L532)
- MINOR の定義は「意味はおおむね保っているが**言い回しがやや粗い**場合(出典に勝手な肩書きを補う等)」(L534-535)

であり、severity は事実上「flagが立ったか否か」の関数で、**materiality(主要Fact理解が変わるか)の軸が存在しない**。MINOR は「文体の粗さ」用の枠として定義されている。したがって「Ledgerに無い具体的主張」がflag=trueになれば必ずMAJORになる。worker の「schema variantはLLM一次severity=MINORの場合にしか機能しない」という発見は正しいが、その**原因は post-hoc の優先順位ではなく Prompt の rubric 設計**である。post-hoc をどう組み替えても、入力される severity 分布が変わらない限り改善しない。

**(B) よって (i) の方向(LLM一次判定を materiality ベースの3層に変更、deterministic 層は昇格のみ)が唯一の構造的解であり、(ii) V5-C は実データ上「不採用」で決着する。** V5-C の降格条件(`observation_consistent==True` かつ `ledger_field_basis=="ledger_fact"`)を既存実測データに機械適用すると、**既知の gold=BLOCKING を複数取りこぼす**:

| 適用対象 | V5-C適用結果 |
|---|---|
| `Meta_run03_standard`(negative control、gold=BLOCKING) | V2 run: 唯一のdevが obs=true/ledger_fact → 降格 → **PASS(見逃し)**。V4A run: 2 devとも obs=true/ledger_fact → **PASS(見逃し)**。V3 runのみ obs=false で生存。3 runs中2 runsで見逃し |
| `hormuz_run03_standard`(gold=BLOCKING) | V4A n=5のうち検出3回中、attempt2・attempt5が obs=true/ledger_fact → 降格。**実効検出 3/5 → 1/5** |
| `er009_changed_actor`(Safety fixture) | V4A attempt3 は changed_actor=true・MAJOR にもかかわらず **obs=true**(明らかな誤り)。降格層の入力信号として信頼できない |

さらに、**同一fixture・同一claimで `observation_consistent` が run 間で反転する**(hormuz_run03_standard の「Oil prices did not fall across the whole market」: attempt1=false、attempt2=true、attempt5=true)。判定を左右する信号としての再現性が無い。

**(C) 一方、Safety群では `observation_consistent` は完全に一貫して false**(Trial 2 Step1 の16 deviation全件 false)。つまりこの信号は「重大逸脱の検出」には使えるが「安全な降格」には使えない、という非対称性がある。これは「昇格にのみ使う」という設計原則(fail-closed)と整合する。

### 【Evidence】
- `C:\Users\tensh\eigo-radio\er003_v1_en_direct_vfl_01_generate.py` L531-537(判定ルール)、L523-529(許容範囲)、L544-561(post-hoc、降格のみ)
- `C:\Users\tensh\eigo-radio\er051_output\open233_checker_trial_01\trial_01_step2_diag\summary_diag_step2.json` L598-626(Meta/V2、obs=true)、L645-672(Meta/V3、obs=false)
- `C:\Users\tensh\eigo-radio\er051_output\open233_checker_trial_01\trial_02\step2\summary_trial2_step2.json` L246-302(Meta/V4A、2件ともobs=true/ledger_fact)
- `C:\Users\tensh\eigo-radio\er051_output\open233_checker_trial_01\trial_02\step3\summary_trial2_step3.json` L455-625(hormuz_standard 5 run、obs=false/true/–/–/true)
- `C:\Users\tensh\eigo-radio\er051_output\open233_checker_trial_01\trial_02\step1_changed_actor_n5\summary_trial2_step1_changed_actor_n5.json` L102-117(attempt3、changed_actor=true かつ obs=true)
- Safety群16件全件 obs=false: `...\trial_02\step1\summary_trial2_step1.json`(`"observation_consistent": true` の出現 0件)

### 【Safetyリスク】
- (ii) V5-C: **高**。上記のとおり実データで既知のBLOCKINGを見逃す。採用不可。
- (i) rubric変更: **中**。「materialityの判定をLLMに委ねる」ため、重大逸脱を QUALITY と誤ラベルするリスクが新規に発生する。ただし緩和策が具体的に設計可能:
  1. deterministic 昇格層を維持・拡張(changed_number/actor/negation/comparison/time のいずれかtrue → 無条件BLOCKING。降格は一切しない)。
  2. rubric 内に明示的 tie-break「判断に迷う場合はBLOCKINGにする」(fail-closed をLLM側にも明文化)。
  3. Safety群12+changed_actor n=5 の100%維持を variant 打ち切り条件として据え置く(既存の受入条件のまま)。
  4. Meta_run03_standard を negative control として継続。
- (i) の残留リスク: 上の1.が効くのは「flagが正しく立った場合」のみ(Trial 1で実証済みの射程問題)。V4-A で changed_actor の flag 精度は 5/5 になったが、他カテゴリの flag 精度は未測定。

### 【推奨案(優先順位)】
1. **(i) を採用**。ただし「severity」という単一フィールドを上書きするのではなく、**detection(10 flags、現行どおり)と materiality(新フィールド `materiality`: BLOCKING/QUALITY/ACCEPTABLE)を分離**する。既存 `severity` は互換のため残し、deterministic 層は `materiality` を読む。理由: Safety群の既存挙動(全件MAJOR)を壊さずに新軸を追加でき、Trial 1/2 の既存データと直接比較可能になる。
2. materiality の判定基準は**Ledger構造に紐づけて機械検証可能な形**にする(LLMの語感に委ねない)。素案:
   - BLOCKING: Ledgerの `claim`/`scope`/`numeric_value`/`date_or_period`/`conditions` のいずれかと**矛盾する**、または**Ledgerが別の原因・別の主体を明記しているのに異なるものを述べる**、または `notes_for_writer` が明示的に禁じた断定をしている。
   - QUALITY: Ledgerの観測と矛盾しないが、Ledgerが保証していない関係付け(因果接続詞・動機の帰属・強調)が加わっている。
   - ACCEPTABLE: 新しい固有名詞・数値・時期・主体・因果を一切加えず、Ledgerが確認した事象の一般常識レベルの背景説明・条件付きの一般論にとどまる。
3. (ii) V5-C は**設計案から落とす**(実装・実行とも不要)。理由は上記Evidence。落とす判断自体は Fable/ユーザーに委ねるが、私の診断としては「実データで既に反証済み」。
4. (iii) その他として検討に値するのは **2段階呼び出し(detect → materiality を別callで判定)**。1回目は現行Prompt完全据え置き(Safety資産を保存)、2回目に検出済みdeviationだけを materiality 分類させる。利点: Safety側のPromptを一切触らないためSafety regressionリスクが構造的にゼロに近い。欠点: call数2倍(記事換算 ¥1.0→¥1.6程度と推定、Checkerの2回目は入力が短いため2倍未満)。**Safety最優先ならこちらが最も安全**。

### 【USER_DECISION_REQUIRED】
**該当する(ただし「Production採用」ではなく「Trial variantでBLOCKING判定基準そのものを変更することの事前了承」として)。**
私の見解: (i) は **fail-closed撤廃には該当しない**。deterministic層は降格せず、不確実時はBLOCKING、Safety 100%要件も据え置くため、「不確実なものは止める」という思想は保たれる。しかし **「何をBLOCKINGと呼ぶか」の一次基準を変更する**ことは事実であり、ユーザー決定1(BLOCKING=fail-closed)の解釈に触れる。したがって Trial 3 実行前に「Family X限定・Production非接続のTrialとして、一次severity rubricにmateriality軸を追加してよいか」を明示開示して可否を取ることを推奨する。Production採用が USER_DECISION_REQUIRED であることは当然。

---

## 論点2. B1〜B4 の materiality 一次評価(raw fixture/Ledgerから独立に実施)

### 【所見】

**重要な前提の訂正**: 不要BLOCK率は **fixture単位**(overall STOP か否か)で測られているが、materiality は **claim単位**でしか評価できない。B1/B4 は「明らかに無害なclaim」と「明らかに material なclaim」が同一記事に同居しており、fixture単位goldでは表現できない。以下は claim 単位の評価。

| claim(fixture) | 私の materiality 評価 | 理由 |
|---|---|---|
| B1-a「ホルムズ海峡は中東から原油を運ぶ船が多く通る重要な海の道だ」 | **ACCEPTABLE** | 地理的一般常識。新しい固有名詞・数値・時期・主体を加えない。HF-001は課金禁止決議の話で、この文と矛盾しない。現行Production Promptの許容規定(L527-528「一般常識レベルの前置き」)に既に該当している。**新たな緩和ではなく既存規定の適用漏れ** |
| B1-b「原油価格が高い状態が続けば、ガソリンや輸送費など身近な価格にも影響する」 | **ACCEPTABLE** | 条件付き(「続けば」)の一般経済常識。ニュースの事実関係を変えない。Checker自身も `observation_consistent=true`・`ledger_field_basis="none"` と判定 |
| B1-c「市場が見ているのは『言葉』より海の安全」「投資家が気にしているのは20%案が残るかだけではない」(V4A runで検出) | **BLOCKING寄り(少なくともACCEPTABLEではない)** | 市場参加者の動機と価格回復理由の断定。HF-009の`causal_strength`は CAUSAL_STATED_BY_SOURCE、HF-011の notes は「これだけから撤回が価格を上昇させた/下落させなかったと因果推論しない」と明示。リスナーの主要Fact理解(なぜ価格が戻ったか)を変える |
| B2「料金案消滅が大幅な価格下落を招かなかった」「他の要因が残った。So 価格は一度反応し高水準へ戻った」 | **QUALITY(通過+表現修正)寄り。ただし境界** | Ledgerが記録した2つの観測(一時縮小→回復、懸念継続)の**共起を因果接続詞でつないだ**もの。Ledgerが別の原因を記録しているわけではない。一方 HF-011 notes は明示的にこの推論を禁じている。**「主要Fact理解は変わらないが、Ledgerが明文で禁じた書き方」**という中間ケース。ユーザー暫定gold=QUALITYは**妥当と考える** |
| B3「7月14日に懸念が続いていた、**so** 20%案が舞台を去った」 | **BLOCKING(gold=BLOCKING を支持)** | HF-007の`conditions`に「トランプ氏は**中東指導者との協議に基づく決定**だと説明した」と**別の原因が明記されている**。記事はそれと競合する原因を述べており、政策決定の理由を取り違えさせる。リスナーの主要Fact理解を変える |
| B4-a「A person can take over when AI alone has trouble」 | **BLOCKING** | MUSE-HC-006が記録するのは「一部の電話を人間契約スタッフが担当したテスト」。記事は「AIが困難な時に人間が引き継ぐ**フォールバック機構**」という製品仕様を新規に述べている。製品の仕組みの誤伝達で material |
| B4-b「People feel differently when...」「Names, plans, and private matters are easier to share...」 | **ACCEPTABLE〜QUALITY** | 人間心理の一般論。Metaの事実を歪めない。Checkerは「従業員の懸念→一般人への拡張(changed_scope)」としたが、記事文は従業員に帰属させていない。**過剰検出寄り** |
| B4-c「useful features make people want to know whether AI or a person is on the other end」 | **ACCEPTABLE〜QUALITY** | 同上 |
| B4-d「Meta had run a test that produced exactly this kind of surprise」(V4A run) | **QUALITY〜BLOCKING** | 原文「思わせるテスト」→「実際に驚きを生じさせた」への確実性強化。translation段で生じた certainty 変化 |

**結論(論点2の二択への明示回答)**: **「到達にB3/B4の通過が不可欠であり、それがSafety上不当であるため、gold/指標定義の再判断=ユーザー判断が必要」の側**である。

理由(算術):
- 現行の不要BLOCK率の定義は「BLOCKING判定fixture数 ÷ 4(B1/B2/B3/B4)」。
- しかし B3・B4 は、Part B・v0.2§6-1機械適用・そして**本診断の独立評価のいずれでも BLOCKING が妥当**。
- したがって**完全に正しいCheckerでも必ず 2/4 = 50%** になる。**≤25% は「B3かB4のどちらかを見逃す」ことを要求する指標**であり、現行gold集合のままでは Safety を犠牲にせずには数学的に到達できない。
- 分母を「goldが非BLOCKINGのfixture」に厳密化すると分母は {B1, B2} の2件となり、≤25% は「2件とも通過」を意味する。V4A実測は B2=PASS・B1=BLOCK なので 1/2=50%。そしてB1の BLOCK 理由(B1-c、市場動機の因果帰属)は私の評価では material であり、**B1をfixture単位で「通すべき」と定義すること自体が安全でない**。

### 【Evidence】
- `C:\Users\tensh\eigo-radio\er019_output\family_x_refresh_e2e_01\hormuz\run_02\ledger\verified_fact_ledger.txt` L44-50(HF-007: conditions に「中東指導者との『非常に生産的な協議』に基づく決定」)、L74-80(HF-011 notes: 因果推論禁止)、L58-64(HF-009)
- `C:\Users\tensh\eigo-radio\er019_output\family_x_refresh_e2e_01\meta\run_03\ledger\verified_fact_ledger.txt` L31-35(MUSE-HC-006)、L59-64(MUSE-HC-010)
- `...\trial_02\step2\summary_trial2_step2.json` L10-64(B1のV4A検出2件)、L116-228(B4のV4A検出4件)
- `...\trial_01_step2_diag\summary_diag_step2.json` L274-302(B3/V2)、L320-348(B3/V3)

### 【Safetyリスク】
- ≤25% を現行定義のまま追い続けると、**指標を満たすためにB3またはB4を通す方向へ設計が引っ張られる**。これは「政策決定の理由の取り違え」「製品仕様の捏造」を通すことを意味し、ユーザーの目的(「必要なものは確実に止める」)に真っ向から反する。**指標そのものが Safety リスク源になっている**。

### 【推奨案(優先順位)】
1. **claim単位goldへ移行**(¥0)。既存の全出力JSONに claim テキストが保存されているので、追加API不要で claim 単位 gold 表を作れる。不要BLOCK率を「gold=ACCEPTABLE/QUALITYのclaimがBLOCKING判定された率」に再定義する。これで B1-a/B1-b/B4-b/B4-c のような明確な過剰検出を、B1-c/B3/B4-a のような正当なBLOCKと分離して測定できる。
2. fixture単位の指標は残すが、**「gold=BLOCKINGのclaimを1件でも含むfixtureはBLOCKして正しい」**と定義し直す(=B3/B4は分母から外す)。分母は {B2} + 新規に抽出する negative claim 群。
3. B3 の gold を BLOCKING で確定する提案をユーザーへ上げる(本診断で HF-007 conditions という**Ledger本体フィールド**の根拠が特定され、Part Bと独立に一致した)。
4. B1 の gold を「fixture=ACCEPTABLE候補」から「claim単位(a,b=ACCEPTABLE / c=BLOCKING)」へ変更する提案を上げる。
5. 目標値 ≤25% は、指標を claim 単位に変えた上で再設定する(現行定義のままの ≤25% は撤回を提案)。

### 【USER_DECISION_REQUIRED】
**該当する(最重要)。** gold の再判断(B1のclaim分割、B3の確定)と、不要BLOCK率の定義・目標値の変更は、いずれもユーザー判断11の対象。**Trial 3 を実行する前に、この判断を先に取ることを強く推奨する**(指標が壊れたまま Trial を重ねると、Safety を削る方向に最適化してしまう)。

---

## 論点3. notes_for_writer の扱い

### 【所見】

**worker の原因分類「B2/B3/B4 は notes_for_writer の明示禁止に従った結果 BLOCKING」は、構造化フィールドの実測と食い違う。** この Trial は `ledger_field_basis` と `matched_notes_id` をまさにこの問いに答えるために追加したが、その実測値は:

- **B群 deviation 全22件中、`ledger_field_basis=="notes_factual_constraint"` は2件(9.1%)のみ**(B2/V3 dev1 → HF-011、B4/V4A dev2 → MUSE-HC-002)。**残り20件は `ledger_fact`(13件)または `none`(7件)**で、`matched_notes_id` は空。
- 個別に見ても worker の帰属は誤り:
  - **B3**: worker は「HF-007 notes の明示禁止」としたが、**HF-007 の notes_for_writer は時系列順序の規定のみ**(「この投稿は7月13日の提案から約24時間48分後。Ledger上では必ず7月13日の提案より後に位置付ける」)で、因果に関する禁止は書かれていない。Checker の理由文も notes ではなく **conditions フィールド**(中東指導者との協議)を引いている。
  - **B4**: worker は「MUSE-HC-006『一部の電話・テストと限定』違反」としたが、記事文「A person can take over when AI alone has trouble」は「全ての電話」とは言っていない。Checker の理由文も「Ledgerは一部の電話を人間が担当したことを示すが、AIが困難に直面したため引き継いだとはしていない」= **本体claimの範囲外**という論理。

つまり **B群のBLOCKを駆動しているのは notes ではなく「Ledger本体フィールドの範囲外/Ledgerに存在しない」**という判断である。

**帰結: v0.2 の「notes を factual_constraint と writer_guidance に分離する」案は、本データ上、生産性をほぼ改善しない。** 理由は二重:
1. Hormuz 12/12 + Meta 15/15 = **27/27 が factual_constraint**(設計書§3-2)なので、分離しても入力が変わらない(V2 vs V3 が同一結果だったことで実証済み: 両者とも 4/4 BLOCKING)。
2. そもそも判定根拠の91%が notes 由来ではない。

### 【Evidence】
- `...\trial_01_step2_diag\summary_diag_step2.json`: B1/V2 L29,L56 / B1/V3 L100,L128 / B2/V2 L174 / B2/V3 L220(notes_factual_constraint, HF-011), L248 / B3/V2 L294 / B3/V3 L340 / B4/V2 L386,L414,L442,L470 / B4/V3 L516,L544,L572 — `matched_notes_id` 非空は L222 のみ
- `...\trial_02\step2\summary_trial2_step2.json`: B1 L29,L56 / B4 L136,L164(notes_factual_constraint, MUSE-HC-002),L192,L220
- `...\hormuz\run_02\ledger\verified_fact_ledger.txt` L50(HF-007 notes が時系列規定のみ)
- `...\meta\run_03\ledger\verified_fact_ledger.txt` L35(MUSE-HC-006 notes)

### 【Safetyリスク】
- notes を「表現上の指針(違反=QUALITY)」に分類する運用を入れると、**分類自体がLLM/Researcherの裁量になり、Safety の穴が Ledger 生成側に移動する**。現状 27/27 が factual_constraint であることは、Researcher が notes を「事実の境界」として書いている証拠であり、この設計思想は健全。壊すべきでない。

### 【推奨案(優先順位)】
1. **notes の schema 分離(v0.2案)は実施しない**ことを推奨。効果がデータ上見込めず、Ledger生成側(Production Researcher schema)への波及リスクだけが残る。
2. 代わりに、**materiality を deviation 側の軸として持つ**(論点1の推奨2)。notes を粒度化するのではなく、「Ledgerが明文で禁じた断定に該当する場合はBLOCKING」を materiality rubric の**一条件**として組み込むのが最小変更。
3. notes に別軸を持たせるなら、「禁止の強さ」ではなく **「禁止の対象(誰の理解が変わるか)」** を書く方が有効。ただしこれは Researcher Prompt の変更であり Family 横断に波及するため、本件のスコープ外とすべき。
4. `matched_notes_id` / `ledger_field_basis` の **観測フィールドとしての価値は高い**(今回 worker の誤った原因分類を反証できたのはこのフィールドのおかげ)。判定ロジックには使わず、Trial の観測用として残すことを推奨。

### 【USER_DECISION_REQUIRED】
**該当しない**(「notes分離を実施しない」という現状維持の推奨のため)。ただし将来 Ledger schema を変更する提案が出た場合は該当する。

---

## 論点4. Stability低下(90%→80%)

### 【所見】

**(A) 揺れているのは severity でも category でも claim 選択でもなく、「そもそも報告するかしないか」(recall)である。**
`hormuz_run03_standard`(gold=BLOCKING、HF-009の changed_scope)の V4A n=5:
- attempt1/2/5: **完全に同一のclaim**(「Oil prices did not fall across the whole market after the plan was withdrawn」)を、**同一category**(changed_scope、+一部 changed_fact/unsupported_new_claim)、**同一severity**(MAJOR)で検出。
- attempt3/4: `deviations: []` の**完全非検出**。

検出した場合の再現性は 3/3 で完璧。したがって「schemaが増えて判定が揺れた」のではなく、「検出漏れが2回起きた」現象である。

**(B) 「思考量不足」では説明できない。** reasoning_tokens は検出回が 2314 / 3624 / 5105、非検出回が 2627 / 3225。非検出回の方が多いケースがある。

**(C) 90%→80% は統計的に有意でない。** V0 は advanced 4/5 + standard 5/5 = 9/10、V4A は advanced 5/5 + standard 3/5 = 8/10。n=10 同士で 9 vs 8 は誤差範囲(Fisher正確検定でおよそ p≈1.0)。**「Prompt増加により悪化した」と断定できるデータではない**。同時に「悪化していない」とも言えない。**現状は測定不足**であり、これが第一の問題。

**(D) 主因の候補と評価**:
| 候補 | 評価 |
|---|---|
| Prompt分量増加(V01+V4A 約1.7KB)による注意配分変化 | **可能性あり、未検証**。ただしV4Aで advanced は 4/5→5/5 と改善しており、一方向の劣化ではない |
| schema追加(5フィールド)による出力負荷 | **可能性は低い**。検出時の判定内容は完全に安定しており、schema由来の混乱の兆候はない |
| 既知の非決定性 | **最有力**。V0以来、B2_hormuz・ja_r2 等で検出/非検出の揺れが繰り返し観測されている(ja_r2 は V0 40%検出、V4A 20%検出)。`er051_open233_checker_trial_variant_01.py` L330 はモデル呼び出しに `reasoning={"effort": ...}` のみ指定し、**temperature/top_p/seed を一切指定していない**(既定サンプリング) |

### 【Evidence】
- `C:\Users\tensh\eigo-radio\er051_output\open233_checker_trial_01\trial_02\step3\summary_trial2_step3.json` L455-499(attempt1 検出)、L500-545(attempt2 検出)、L546-562(attempt3 非検出)、L563-579(attempt4 非検出)、L580-625(attempt5 検出)
- `C:\Users\tensh\eigo-radio\er051_open233_checker_trial_variant_01.py` L330(`reasoning={"effort": vfl01.REASONING_EFFORT}` のみ、temperature/seed指定なし)

### 【Safetyリスク】
- **これは Productivity の問題ではなく Safety の問題である**。gold=BLOCKING の実データ fixture を 5回中2回見逃している。Production は1記事1回しか Checker を通さないので、**実運用での見逃し確率が約40%**ということになる(この fixture に限れば)。Safety群12 fixtureが100%なのは合成fixtureが露骨だからであり、**実データでの真のrecallは60〜80%程度である可能性が高い**。論点1〜3の過剰BLOCK議論より、こちらの方が優先度が高い可能性がある。

### 【推奨案(優先順位)】
1. **測定を先に増やす(最優先、低コスト)**。`hormuz_run03_standard` と `Meta_run03_standard` を n=20 で実測(約40 call、1 callあたり ¥0.25〜0.33 なので **¥10〜13程度**)。二項信頼区間を出さずに「90%→80%」を結論にしない。
2. **self-consistency(2〜3 run の union)を採用候補に入れる**。recall 60% の単発を2回unionすると 1-0.4²=84%、3回で 93.6%。**union は常に「止める方向」なので fail-closed と整合する**。コストは Checker call が2〜3倍(記事換算 ¥1.0 → ¥2.0〜3.0)。過剰BLOCKも増えるので、**materiality=BLOCKING相当のclaimに限って union、QUALITY以下は多数決**とすればトレードオフを抑えられる。
3. **Prompt短縮**。V01ブロック(1017字)とV4Aブロック(647字)を統合し、`qualifier_text`(自由文・長文になりがち)を短縮または廃止する。効果は未検証だが、出力トークン削減=コスト削減の副次効果が確実にある。
4. **temperature/seed の明示指定**は、gpt-6-luna(reasoning系)で受理されるか未確認。受理されるなら temperature=0 相当を試す価値はあるが、reasoning モデルでは効果が限定的なことが多い。**優先度は4番目**。
5. deterministic化(ルールベースでの検出)は、changed_number/changed_time/固有名詞の不一致など**機械的に照合可能な項目に限定**すれば有効。ただし本件の hormuz_standard は「Brent先物 → 石油市場全体」という scope 一般化であり、機械照合は困難。**汎用の解にはならない**。

### 【USER_DECISION_REQUIRED】
**測定追加(n=20)は該当しない**(承認済み予算枠内の小額、総枠¥400に対し残¥377)。**self-consistency の採用は QCD(コスト2〜3倍)に影響するため、採用時は該当する**。

---

## 論点5. regression fixture 戦略と Family 横断リスク

### 【所見】

**(A) 現状の fixture セットは positive(止めるべき)に偏りすぎ、negative(通すべき)が決定的に不足している。**
- positive: er009 9種(合成)+ A2A3/A4/A5(実データ)+ changed_actor n=5 + Meta_run03_standard + hormuz_run03_standard = 実質14種。
- negative: **B2_hormuz と hormuz_run03_advanced の2件のみ**(B1/B3/B4は上記のとおり material claim を含むため negative として使えない)。
- **negative が2件しかない状態で「不要BLOCK率」を測っているため、1件の揺れが25%ポイント動く。**これが Trial 1→2 で 100%→50% と乱高下した直接の理由でもある(設計書も n=1 の限界として自認している)。

**(B) 無料で negative を増やす具体策がある。** 既存 Production 実行のうち **retry を経て最終的に LEDGER_COMPLIANT になった記事本文**は、「Checker自身が通した=gold PASS」の実例である。`er019_output/` 配下に多数存在する。これを claim 単位で抽出すれば、API費用ゼロで negative claim を10〜20件確保できる。

**(C) claim単位 micro-fixture(Ledger + 該当1〜3文)を作ると、n を安価に増やせる。** 全記事fixtureは入力5,500〜6,300 token・出力3,000〜7,300 tokenで1 call ¥0.15〜0.67だが、micro-fixture なら大幅に安く、非決定性の主要因である「claim選択の揺れ」を排除して **rubric そのものの再現性**を測れる。
- 注意: micro-fixture は前後文脈が無いため `qualifier_present` 判定が変わる。**全記事fixtureと併用が必須**(micro=rubric回帰、full=統合回帰)。

**(D) Family 横断展開の具体的な衝突点を1つ特定した。** `HOOK_AWARE_DEVIATION_PROMPT_TEMPLATE` は `DEVIATION_PROMPT_TEMPLATE.replace("【判定ルール】", HOOK_CLAUSE + ...)` で生成され、HOOK_CLAUSE は **「Hook文では changed_scope と changed_comparison の判定を緩和してよい」**と指示している。一方 V4-A は **「changed_number/actor/negation/comparison は該当すれば他カテゴリと重複してでも必ず true にする」**と指示している。この2つを同一Promptに載せると **changed_comparison について正面から矛盾**する。
- 現状は無害: Trial(er051)は hook_aware を使っておらず、hook_aware=True を渡しているのは `er003_v1_n3_01_articles_generate.py`(L1143/1162/1265)と `er003_discovery_focus_staged_production_01.py`(L200/204/263)の2ファイルのみで、Family X経路(er012/er019)は既定 False。
- しかし **共通 `vfl01.DEVIATION_PROMPT_TEMPLATE` へV4A文言を取り込んだ瞬間に、この矛盾が Hook-aware 経路へ波及する**。しかも Hook-aware 経路は Trial で一度も検証されていない。

### 【Evidence】
- `C:\Users\tensh\eigo-radio\er003_v1_en_direct_vfl_01_generate.py` L579-595(HOOK_CLAUSE、changed_scope/changed_comparison緩和)、L602-604(replace方式)、L788-789(hook_awareによる分岐)
- `C:\Users\tensh\eigo-radio\er003_v1_n3_01_articles_generate.py` L1143, L1162, L1265(hook_aware=True)
- `C:\Users\tensh\eigo-radio\er003_discovery_focus_staged_production_01.py` L200, L204, L263(hook_aware=True)
- 設計書 §4-補「V4-A実装」(changed_number/negation/comparison にも同一原則を明記)

### 【Safetyリスク】
- negative不足のまま「改善した」と判断すると、**過剰BLOCK改善が偶然の非決定性だった場合に、Production で Safety を削っただけの結果になる**。
- Hook-aware との矛盾を放置したまま共通Promptへ昇格させると、**Family N3/discovery の既存Safety資産(Trial-05で偽陰性なしを確認済み)が無検証で壊れる**可能性がある。

### 【推奨案(優先順位)】
1. **negative claim セットを無料で10件以上に拡張**(既存 COMPLIANT 記事から抽出 + B1-a/B1-b/B4-b/B4-c を claim 単位で negative として登録)。これが Trial 3 の前提条件。
2. **regression suite を「Prompt/model が変わったら必ず走る」固定セットとして凍結**する。凍結対象: fixture sha256、gold(claim単位)、Prompt sha256、モデルID。V4-Cで作った「既知の未昇格3件」の方式をそのまま拡張すればよい(設計は妥当)。
3. **positive 側の補強**: 現状の positive は「主体すり替え」「数値改変」等の露骨な合成が中心。**実データ由来の positive(hormuz_run03_standard型の scope 一般化、B3型の競合原因)を明示的に positive fixture として登録**する。実データ positive こそが recall 40%見逃しを露呈させた本命である。
4. **Family 横断展開は、HOOK_CLAUSE との整合を先に解決してから**。最小案: V4A/V5A文言を HOOK_CLAUSE の**後**に置き、「Hook緩和は changed_scope/changed_comparison に限り優先する。それ以外のカテゴリでは本節の重複true原則を適用する」と優先順位を明記する。採用前に Family N3 の既存 Hook fixture 3種(危険Hook)で regression を回す。
5. Family Y/Z 展開時の想定問題として、**Ledger の notes_for_writer 構成が Family ごとに異なる可能性**(Family X は 27/27 factual_constraint だが他Familyは未確認)を、展開前の必須確認項目にする。

### 【USER_DECISION_REQUIRED】
**fixture 追加・gold凍結は該当しない**(¥0、Trial内作業)。ただし **gold の内容確定は論点2のユーザー判断に含まれる**。**Family 横断展開(共通Prompt変更)は Production 変更であり該当する**。

---

## 【総合: Trial 3 で実装すべき最小変更セットと理論上の到達値】

### 前提(これを先にやらないと Trial 3 は意味を持たない)

**Step 0(¥0、ユーザー判断待ち)**: 指標とgoldの是正。
- claim単位goldへ移行、不要BLOCK率を claim 単位で再定義。
- B3 を gold=BLOCKING で確定(本診断で HF-007 conditions という本体フィールド根拠が特定された)。
- B1 を claim 単位に分割(a,b=ACCEPTABLE / c=BLOCKING)。
- B4 を gold=BLOCKING(fixture単位)として分母から除外、claim単位では b,c を negative へ。
- 目標値 ≤25% を claim 単位基準で再設定。
- → **これは USER_DECISION_REQUIRED。Trial 3 実行前に取ること。**

**Step 1(¥0)**: negative claim セットを既存 COMPLIANT 記事から抽出し10件以上に拡張、regression suite として凍結。

### Trial 3 最小変更セット(3点のみ、いずれもFamily X限定variant・Production非接続)

| # | 変更 | 内容 | リスク |
|---|---|---|---|
| **C1** | **materiality軸の追加(V6)** | schema に `materiality`(BLOCKING/QUALITY/ACCEPTABLE)を追加し、Trial Prompt差分ブロックに Ledger構造に紐づけた判定基準+「迷ったらBLOCKING」を明記。既存 `severity` は据え置き(互換・比較用)。deterministic層は `materiality` を読み、**昇格のみ**(4〜5カテゴリflag true → 無条件BLOCKING)。降格は実装しない | 中。Safety群100%を打ち切り条件として据え置くことで担保 |
| **C2** | **一般常識許容規定の明文化(V5-A相当)** | 「Ledgerが確認した事象からの、新しい固有名詞・数値・時期・主体・因果を伴わない一般常識レベルの背景説明・条件付き一般論は deviation として報告しない」。**現行Production Prompt L527-528 の既存許容規定の具体化であり、新規緩和ではない**点を記録に明記 | 低。ただし「一般常識」の境界はLLM次第という既知の弱点は残る |
| **C3** | **Stability の正しい測定** | `hormuz_run03_standard` と `Meta_run03_standard` を n=20 で実測(約40 call、¥10〜13) | なし(測定のみ) |

**実装しないもの**: V5-C(実データで見逃し実証済み)、V4-B(materiality条件なしの昇格拡張)、notes schema分離(効果が見込めない)、Production側の一切の変更。

### 理論上の到達値(いずれも**机上試算・不確実**であることを明記)

| 指標 | 現状(Trial 2実測) | Trial 3 理論値 | 根拠と不確実性 |
|---|---|---|---|
| **Safety(重大fixture BLOCKING維持率)** | 100%(12/12 + 5/5) | **100%維持の見込み** | Safety群16 deviation全件が `observation_consistent=false` かつ4カテゴリflagが立っており、materiality rubric でも BLOCKING 側に落ちる公算が高い。ただし **rubric変更でLLMの一次判定が動くリスクは残る(実測必須)** |
| **不要BLOCK率(claim単位・新定義)** | 測定不能(claim gold未整備) | **20〜35%程度** | negative claim(B1-a/b、B4-b/c + 新規抽出分)のうち、C2で救えるのは「一般常識型」。B4-b/c のような「一般人心理への言及」は境界が曖昧で救える保証がない。**≤25%達成は五分五分** |
| **不要BLOCK率(現行fixture単位定義のまま)** | 50%(V4A、n=1) | **50%が下限**(B3/B4が正しくBLOCKするため) | **≤25%は Safety を削らない限り到達不能**(論点2の算術) |
| **Stability(gold既知fixture一致率)** | 80%(n=5、有意差なし) | **真値は n=20 測定で初めて分かる。現時点の推定は 60〜85%** | C1/C2は recall を直接改善しない。改善したいなら self-consistency(2-run union)が必要で、その場合 **recall 理論値 84%(単発60%前提)、コスト2倍** |
| **QCD(記事換算cost)** | ¥1.019(V0比1.25倍) | **¥1.0〜1.2**(C1/C2のPrompt追加分で微増)。self-consistency 併用時は **¥2.0〜2.4** | Prompt短縮(qualifier_text削減)で相殺可能 |

### 最後に、最も重要な指摘(優先度順)

1. **指標が壊れている**。現行の「不要BLOCK率 ≤25%(fixture単位・分母4件)」は、正しいCheckerでも50%が下限であり、達成するには実逸脱を通すしかない。**このまま Trial を重ねると Safety を削る方向に最適化される**。Trial 3 の前に gold/指標のユーザー判断を取るべき。
2. **過剰BLOCK(Productivity)より、見逃し(recall)の方が深刻な可能性がある**。実データ fixture `hormuz_run03_standard` で 5回中2回の完全非検出が観測された。Safety 100% という数字は合成fixtureに支えられたもので、実データでの真の recall は未測定。**n=20 の測定は最優先・最安価**。
3. **worker の原因分類のうち「B2/B3/B4 は notes_for_writer に従った結果」は、構造化フィールド実測(22件中2件=9%のみnotes由来)と矛盾する**。この誤った原因分類に基づく V5-B/notes分離の方向は、効果が見込めない。
4. **V5-C は実データで反証済み**(negative control を3 runs中2 runsで見逃す)。設計案から落とすことを推奨。
5. **V4-A の文言は HOOK_CLAUSE と changed_comparison で正面衝突する**。Family X限定variantの間は無害だが、共通Promptへ昇格させる際は必ず整合を取り、Family N3の危険Hook fixture 3種で regression を回すこと。

### 入力範囲について
今回の診断に必要な事実は揃っていた。ただし、以下を追加で読めば精度が上がる可能性がある(現時点では必須と判断しない):
- `C:\Users\tensh\eigo-radio\docs\pm\review_ledger_deviation_redesign_01_part_b.md`(Part B の B1/B3/B4 評価の逐語。本診断は raw データから独立に評価し、結論は一致した)
- `C:\Users\tensh\eigo-radio\er050_output\gpt6_checker_comparison_trial_01\summary_step3.json`(V0 の Stability 生データ。90% の内訳を n=5 の生出力で再確認できれば、論点4の有意差判定がより厳密になる)

本診断は read-only であり、ファイル編集・テスト実行・API呼び出しは一切行っていない。Production 採用の可否判断は含まない(人間ユーザーのみが承認できる)。

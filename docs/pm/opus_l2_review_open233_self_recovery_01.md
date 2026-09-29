管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01
日付: 2026-09-30
種別: L2 批判的設計レビュー #1(read-only)
**runtime evidence**: ユーザー指定`claude-opus-5-5`はClaude Code 2.1.272
未対応で400(要2.1.280+、request id req_011CfYW9VqvuUcvEUyfZu1Bs、model
sent: claude-opus-5-5)→ 起動時オーバーライドで`claude-opus-5[1m]`
(Opus 5、cutoff 2026-05)にて実行。`.claude/agents/opus-consultant.md`の
指定はclaude-opus-5-5のまま維持(クライアント更新後に有効)。

以下、末尾「=== Opus L2 レビュー #1 全文 ===」以降を一字も変えず保存。

---

# Opus L2 批判的設計レビュー #1(OPEN-233-SELF-RECOVERY-TRIAL-01、read-only)

**runtime evidence**: 自認モデル名「Opus 5 (1M context)」/ exact model ID `claude-opus-5[1m]`(system prompt記載のまま、推測なし)/ knowledge cutoff 2026-05。read-only、ファイル編集・実装・API呼び出し・テスト実行なし。Production採用可否の判断は含まない(人間ユーザーのみ)。

読んだ範囲: `docs/pm/design_open233_self_recovery_flow_01.md`(全1186行)、`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`(§1〜§3全文)、`docs/pm/opus_l2_review_open233_checker_trial_01.md`(前任レビュー全文)、`er012_e_family_entertainment_two_level_runner_01.py` L255-700、`er019_family_x_ja_writer_o_r1_r2_01.py` L235-345、`er051_open233_checker_trial_variant_01.py` L40-265、`er003_v1_en_direct_vfl_01_generate.py`(prior_issues関連 L647-800)、`er051_output/.../trial_02/step1_changed_actor_n5/summary_*.json`、`OPEN-233-CHECKER-REDESIGN-TRIAL-01_REPORT.md`§12、`docs/pm/design_open233_checker_redesign_trial_01.md`(changed_actor関連箇所)、`docs/pm/negative_claim_candidates_open233_01.md`、`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md`(HF-006/009/011 STOP経緯)。

---

## 論点1. Self-Recovery Flow全体設計(4 Stage構成でEscalation実質ゼロに到達できるか)

### 【所見】
**(A) 「Stage 3 Rewriteのmechanismをcycle indexで決める」設計(§5-3)が、実データの支配的failure modeと噛み合っていない。** 実E2Eで観測されたBLOCK事象5件のうち**4件(80%)が`origin="ja_source"`**である(Hormuz run_01 HF-006、run_02 HF-011、run_03 Advanced HF-009、run_03 Standard HF-009。translation起因はMeta run_03の1件のみ)。§5-3は「cycle 1で案B(JA全文Rewrite)を使ったらcycle 2はEN局所Rewriteに限定(同一記事で案Bを2回使わない)」と定めているが、Hormuz run_03の実パターンはまさに「cycle 1=JA(Advanced解消)→cycle 2で**Standardに別のja_source claim**が出現」である。この2つ目もja_source起因なので、EN局所Rewriteで直すと**JA本文とEN本文が意味的に乖離する**(Family X Advancedは「忠実英訳」であり、Deviation CheckはEN vs Ledgerを見るだけでJA↔EN整合を検査しない)。つまり**支配的ケースにおいて、実効cycle数は2ではなく1**であり、現行Production(案B 1回上限)に対して「回復容量」はほとんど増えていない。増えているのはStage 2による降格チャンスのみ。

**(B) 設計自身の正解ラベル表(§7-0/§7-1)を実観測4事象に機械適用すると、Escalationは減るが0にはならない。** HF-006型(「原油高→ガソリン・輸送費」)はB1-b=ACCEPTABLE、HF-011型(「料金案消滅が大幅下落を招かなかった」changed_causality)はB2=QUALITY相当 → いずれもStage 2降格で回復見込み。しかし**hormuz_run03_standard(HF-009 changed_scope)は§7-1でBLOCKING(Confirmed)** と確定ラベルされており、Rewrite必須。その1件がja_source起因なので(A)の制約に直撃する。**4事象中1件は設計の自己ラベル上Escalation確率が高い**(= 25%。Primary KPI「0件/10〜20記事」とは両立しない水準)。

**(C) Stage 2/Stage 3の統合(3段階化)は、コストではなく検証可能性の理由で今は採らない方がよい。** §11-1の暫定答え(分離維持)に私は賛成する。ただし理由は「別々に検証できる」ではなく、**Stage 2は「発火しない」ことが正常系の大半であり、rewrite_hint生成を同一callに載せると、降格判定callが常にrewrite出力トークンを払う**(降格ケースでも出力が長くなる)。分離の方が期待コストは安い可能性が高い。一体化したいなら「materiality判定+rewrite_hint」ではなく**「Stage 2をinstance単位で1 callにbatch化」**の方が圧倒的に効く(論点6)。

**(D) Escalation条件の列挙(§6-1)に既存STOP軸の取りこぼしがある。** 少なくとも以下がStage 4条件として書かれていない: (1) `all_prior_issues_resolved=False`(後述、論点5が本質)、(2) JA側の**音声化禁止記号Gate**(`JAFactCheckStopError(stage="original_symbol")`、`er019_family_x_ja_writer_o_r1_r2_01.py` L340-344)。案Bを1回発火させるごとにJA内部のfail-closed gate(Original Fact Check / R2 Fact Check / symbol gate × must-fix 1回)が再抽選され、**案Bは回復手段でありながら新たなEscalation源でもある**。(3) `assert_budget_ok()`(`er012_...py` L455/L547)による予算abort — cycle増でtrip確率が上がる。

### 【Evidence】
- `C:\Users\tensh\eigo-radio\er012_e_family_entertainment_two_level_runner_01.py` L389-399(Advanced、`origin=ja_source`のMAJORは**must-fix retryを経ずに即** `JARecheckRequiredError`)、L654-666(案B後の再実行は`only=None`=Advanced+Standard両方を再生成)、L455/L547(`assert_budget_ok`)
- `C:\Users\tensh\eigo-radio\er019_family_x_ja_writer_o_r1_r2_01.py` L276-323(Original Fact Check+must-fix 1回+STOP)、L330-344(symbol gate STOP)
- `C:\Users\tensh\eigo-radio\FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md` L775-781(run_01 HF-006 ja_source)、L932-941(run_02 HF-011 ja_source)、L1205-1229(run_03 Advanced HF-009 ja_source → 案B → Standardで別のja_source HF-009 changed_scope)
- 設計書 §5-3(L415-419)、§7-1(L490)、§6-1(L426-438)

### 【Safetyリスク】
- (A)の帰結として**EN局所RewriteをJA起因claimに適用すると、誰もチェックしないJA/EN乖離**が生じる。Ledger整合は保たれても「JA記事とEN記事が違うことを言う」状態は、Family Xの二段階生成の前提(忠実英訳)を壊す。現行Production(`_run_writer_stage_once`)がja_source MAJORでENを盲目的に再生成しない設計にしているのは、まさにこのリスク回避のためであり、局所Rewriteはその原則を抜け道で破ることになる。

### 【Cost影響】
- (A)を正すために「案Bを2回」許すと §13-6で既に¥6.40/記事(V4A前)= **Cap 2倍超**。つまり**Cap遵守とEscalationゼロが、支配的ケース(ja_source)で正面から衝突している**。これは設計の最大の構造的問題であり、Stage構成の微調整では解けない。

### 【推奨案(優先順位)】
1. **JA側「局所Rewrite」をPhase 2送りにせず、Phase 1の第一級課題へ繰り上げる**(§5-1は現在スコープ外扱い)。ja_source 80%という実測がある以上、**JA全文再生成(¥3.5〜4.0)が唯一のJA回復手段である限り、Cap内でEscalationゼロは達成できない**。最小実装案(より安い代替): **paired local rewrite** = 該当JA 1文(±1文)とそれに対応するEN文を同一のrewrite_hintで局所編集し、JA側はFact Check 1 call(`vfl01.run_deviation_check`をJA全文に対して1回)、EN側はDeviation Check 1 callで再確認する。概算 ¥1.0〜1.5/cycle(案Bの1/3以下)、かつJA/EN乖離も同時に防げる。Original→R1→R2の文体連鎖に触らない(R2本文を直接局所編集する)ため、§5-1が挙げた「現行実装に部分スキップが存在しない」という障壁も回避できる。**ただしJA局所編集関数は新規実装であり、文体・記号Gate・段落数Gateの再検証が必要**(実装リスクは小さくない)。
2. Rewrite mechanismの選択を**cycle indexではなく`origin`で決める**(ja_source→JA側機構、translation→EN側機構)。§5-3の「案B 2回禁止」はコストguardとしては維持しつつ、「2回目のja_sourceは案Bではなくpaired local rewrite」という第3の選択肢を用意する。
3. §6-1のEscalation条件に symbol gate / `all_prior_issues_resolved` / 予算abort を明記し、**Stage 4到達理由をコード上の例外型と1対1で対応付けた表**を作る(Phase 1の観測項目として必須。「何でEscalationしたか」が分類できなければKPIの意味がない)。
4. Stage 2/3の統合(3段階化)は**採らない**。代わりにStage 2のbatch化(論点6推奨1)でcall数を削る。

### 【USER_DECISION_REQUIRED該当】
- 推奨1(JA局所Rewrite新設)はFamily X限定Trial実装であり**条件4(Production配線)には現時点で非該当**。ただし「JA本文の生成方式をProductionへ入れる」段階では条件4に該当する。
- 「Cap遵守とEscalationゼロが支配的ケースで衝突する」という認識自体は、**条件1(KPI変更)/条件3(Cap超過)のいずれかを将来ユーザーに選ばせる論点**になる。Checkpoint Aで**トレードオフとして明示的に提示すべき**(現設計書§13-10の「代替案」記述より前面に出すべき)。

---

## 論点2. Stage 1設計(V4A採用の妥当性、deterministic pre-check、recall 85〜100%の扱い)

### 【所見】
**(A) V4A採用の根拠は「合成fixture 1種・n=5」しかなく、証拠水準がV4Aの不利データと同じかそれ以下である。** 採用根拠は`er009_changed_actor` 5/5 vs V0 3/6。私が計算したFisher正確検定(両側)は **p≈0.18**(片側0.12)。一方、§14-3が「統計的有意差なし」として退けたhormuz悪化はp=0.23。**同程度に有意でない2つの証拠を、片方は採用根拠として、もう片方は無視理由として使っている**(証拠基準の非対称)。しかも**実データfixtureの併合ではV0 38/40 vs V4A 37/40、p=1.0**で、V4Aに実データ上の優位はない。
- なお、私が当初疑った「V0の3/6見逃しはflag帰属ミスにすぎず`overall_status`には影響しないのでは」という可能性は、**実データで否定された**: `er009_changed_actor` n=1 V0は`LEDGER_COMPLIANT(flag=false)`=真の検出漏れ、V2/V3の未昇格3件も`severity=MINOR`(→`overall_status=LEDGER_COMPLIANT`→Stage 1 ACCEPTABLE)。**§14-1の構造的論証(Stage 1が拾わなければ下流は発火しない)は正しい**。そしてV4A 5/5は`rule_id="existing_major_v2"`(=LLM一次判定がMAJOR)で達成されており、deterministic昇格に依存していない。この点は設計書の主張を**支持する**。
- 結論: V4A採用は「方向として妥当だが、根拠は単一合成fixtureのn=5」。**問題は採用そのものではなく、その根拠の弱さに対して支払っているコスト**(固定費+¥0.294/記事、worst case ¥2.88[Cap内]→¥3.96[Cap 32%超過]))が大きすぎることである。

**(B) V4Aは「BLOCK率を上げる」方向の変更であり、その増分がコストモデルに反映されていない。** V4Aの差分ブロックは「複数カテゴリの同時true」「主体置換は必ずchanged_actor=true」を指示する。現行Promptのseverity規則は「10種のいずれかが明確にtrueである場合のみMAJOR」なので、**flagを立てやすくする指示はMAJOR率を機械的に押し上げる**。実際Trial 2 Step2ではV4A runで新たにB4-dが検出されている。§13-5はV4A採用に伴い**単価だけ+30%し、BLOCK率(15/35/60%)は据え置いている**。BLOCK率はStage 2以降の発動率を決める最大の乗数なので、**これはコストモデルの一貫性欠陥**。

**(C) deterministic pre-checkは「Safetyを下げない」は正しいが、「Primary KPIを下げない」は誤り。** §14-4は「無料かつfail-closed方向にのみ作用する(誤って安全性を下げることがない)」としているが、pre-checkのfalse positive(FP)は**Rewriteでは解消できない**(本文が正しいのだから直しようがない)。FPは必ずcycle 1→cycle 2を消費して**確定的にStage 4へ落ちる**。すなわち**pre-checkはUSER_DECISION_REQUIREDを新規に生成し得る**。EN記事とLedger(JA由来の構造化フィールド)の機械照合でFPが出る典型: 数値の言い換え(「20%」↔「one-fifth」)、日付表記(7月13日↔July 13 / Sunday)、通貨・単位の丸め、主体名の表記揺れ(Trump↔President Trump↔the president)、A2レベルのStandardでの意図的な簡略化。**A2向けに平易化された本文と構造化フィールドの逐語照合はFP率が高いと予想する**(未実測)。
- さらに**schema/floorの穴**: pre-checkが単独で拾ったdeviationには「Stage 1のdeviationレコード」が存在しない。§4-4はStage 2入力に「Stage 1のdeviation出力全体(10 flags/severity/...)」を要求し、§4-3のdeterministic floorは**Stage 1の10 flagsを読んで**BLOCKINGを強制する。pre-check由来の項目はflagが全false(Stage 1が見逃したのだから)なので、**floorが効かず、Stage 2 LLMの裁量で降格され得る**。つまり「Stage 1の検出漏れを補う」ために入れた層が、**Stage 2で静かに無効化される経路**が存在する。

**(D) recall 85〜100%の扱いについて、設計の立場(§10リスク6「スコープ外」)は、Primary Safety KPI「重大Fact見逃し0件」と論理的に両立しない。** これは§11-5の暫定答えが自認しているとおり。率直に言えば、**「見逃し0件」は達成目標ではなく「測定されたfixtureで0件」という限定的な主張にしかできない**。Cap内でこれを埋める手段は(限定self-consistencyを除けば)pre-checkしかなく、pre-checkは(C)のとおり万能ではない。

### 【Evidence】
- `C:\Users\tensh\eigo-radio\OPEN-233-CHECKER-REDESIGN-TRIAL-01_REPORT.md` L337-347(hormuz V0 20/20 vs V4A 17/20 p=0.2308、Meta V0 18/20 vs V4A 20/20 p=0.4872、併合 p=1.0)
- `C:\Users\tensh\eigo-radio\docs\pm\design_open233_checker_redesign_trial_01.md` L32(V0 n=1で`LEDGER_COMPLIANT(flag=false)` MISS)、L44(n=5で3/5、合計3/6)、L566-575(未昇格3件は`severity=MINOR`・`changed_actor=false`)
- `C:\Users\tensh\eigo-radio\er051_output\open233_checker_trial_01\trial_02\step1_changed_actor_n5\summary_trial2_step1_changed_actor_n5.json`(5 attempt全て`overall_status=LEDGER_DEVIATION`・`rule_id="existing_major_v2"`)
- `C:\Users\tensh\eigo-radio\er051_open233_checker_trial_variant_01.py` L188-201(V4A差分ブロック=重複true指示)、L48-131(`classify_deviation_trial`。L111-116に`observation_consistent==True and ledger_field_basis=="ledger_fact"`→ACCEPTABLEの**降格**規則が存在する。MAJORはL71-76で先に確定するため前任Opusが反証したV5-Cとは別物だが、設計書§3-1の「V2 post-hoc=フラグ全falseでMAJORならMINORへ降格」という記述は`classify_deviation_trial`の中身と一致しない。**Stage 1のrouting述語が`overall_status`か`overall_action_trial`かが設計書上曖昧**)
- 設計書 §14-4(L1175、pre-checkの「誤って安全性を下げることがない」)、§4-3(L276-290、floorはStage 1 flagsを読む)

### 【Safetyリスク】
- (C)後段のfloor空振りは**Safetyの実質的な穴**。pre-checkで拾った数値・日付・主体不一致が、Stage 2 LLMの「materiality判定」で降格され得る。pre-check由来項目は**LLMを経由させず即BLOCKING確定(floor扱い)**にすべき。
- (B)のBLOCK率上昇は直接のSafetyリスクではないが、過剰BLOCK→過剰Rewrite→「Rewriteが新たな逸脱を生む」(論点4)経路の発火回数を増やすため、**間接的にSafetyを悪化させる**。

### 【Cost影響】
- V4A固定費 +¥0.294/記事(全記事)。中央シナリオの節約margin(−¥0.06)をほぼ消滅させ、worst caseをCap超へ押し上げる**唯一の原因**。
- (B)未反映のBLOCK率上昇は、条件付き費(Stage 2+Rewrite+Recheck)を**乗数的に**押し上げる。BLOCK率が35%→45%になれば中央シナリオは節約から純増へ反転する。

### 【推奨案(優先順位)】
1. **Stage 1 variantの決定をPhase 1の実測後に延期する**(現在は実測前に「V4A確定」としている)。Phase 1で**¥0〜¥5の追加実測**で決着できる: (a) `negative_claim_candidates_open233_01.md`の出典7記事(既に`LEDGER_COMPLIANT`・`deviations=[]`)を**V4Aで再実行**し、BLOCK率の増分を直接測る(7〜14 call、gpt-6-luna ¥0.2/call ≒ **¥1.5〜3**)。これが現在「15/35/60%」と仮置きされている最大の不確実変数を、最も安く潰す実測である。(b) `er009_changed_actor`をV4A/V0各n=15追加(30 call ≒ ¥6)して5/5 vs 3/6の差を有意水準まで詰める。**この2つはPhase 1の第一優先にすべき**(現§9-1にどちらも入っていない)。
2. **より安い代替(第一候補として検討に値する)**: Stage 1は**V0のまま**(固定費増¥0、worst case ¥2.88でCap内)+ `changed_actor`対策は**pre-checkの「Ledger主体名の不在検出」で置き換える**。`er009_changed_actor`の失敗様態は「Ledgerの`Kareem Haggag and Giovanni Paci`が記事に現れず、代わりに`A team at Harvard Business School`が現れる」であり、**これは機械照合で最も検出しやすい型**(固有名詞の完全不在+別の組織名の出現)。V4Aが救った唯一のカテゴリを¥0で代替できる可能性が高い。**Phase 1でV0+pre-check vs V4A+pre-checkを同一fixtureで比較する**ことを強く推奨する(¥数円)。
3. **pre-check由来の検出は`floor`扱いとして固定**(Stage 2 LLMに降格させない)。そのために`deviation`レコードに`detected_by: "stage1_llm" | "precheck"`を持たせ、`precheck`はStage 2をスキップして直接Stage 3へ送る(Stage 2 call削減=コストも下がる)。
4. **pre-checkはFP率を測る前に本番相当Trialへ入れない**。FP率測定は¥0(既存の`LEDGER_COMPLIANT`記事28件全部に対してregexを回すだけ)。**FP率が高い場合は「BLOCKINGへ強制昇格」ではなく「Stage 2への強制送付(Stage 2で棄却可)」に弱める**という中間設計を用意しておく(ただし3と両立しないので、FP率実測で選ぶ)。
5. 設計書§3-1の「Stage 1 routing述語」を`overall_status`/`overall_action_trial`のどちらかに**明文で確定**する(`overall_action_trial`を使うと`promote_deterministic_flag_v1`による¥0のMINOR→BLOCKING昇格が効き、recallが上がる代わりにBLOCK率=コストが上がる。**¥0でrecallを上げる唯一のレバーなので、Phase 1で両方を事後集計して比較すべき**)。

### 【USER_DECISION_REQUIRED該当】
- 推奨2(V0維持案の再評価)は**条件2(Safety緩和)に触れる可能性がある**ため注意が必要。ただし「V0+pre-checkがchanged_actorを100%捕捉する」ことが実測できれば緩和ではない。**実測前にV0へ戻す決定はしない**こと。
- Stage 1 variant自体の確定は§12で「Guardrail内の自律判断」とされているが、**Cap超過の直接原因になっている以上、条件3(Cap超過)と不可分**。Checkpoint Aで「V4A採用=worst case Cap超の対価」として明示提示すべき(現§12-1に近い記述はあるが、因果として明示されていない)。

---

## 論点3. Second Judge(rubric・入力縮小・floor・迷ったらBLOCKING・独立性)

### 【所見】
**(A) 「独立性」が担保できていない。同一モデル(gpt-6-luna)であること以上に、Stage 2の入力にStage 1の`explanation`と10 flagsを丸ごと渡す設計(§4-4)が致命的なanchoringを生む。** Stage 1のexplanationは「なぜこれが逸脱か」を言語化した文章であり、それを読んだ同一モデルが「materialではない」と判断する確率は構造的に下がる。**「迷ったらBLOCKING」のtie-breakと合わせると、Stage 2は降格しにくい方向に二重に偏る**。Primary KPI(降格による自動解消)にとってこれは逆風。
- 前任Opus論点1推奨4の「2段階呼び出し」の趣旨は**Stage 1 PromptのSafety資産を触らないこと**であり、**Stage 1の判断文をStage 2に見せること**ではない。ここは設計の読み替え誤りだと考える。

**(B) 降格余地が構造的に薄い。** §7-0の確定ラベル9件のうちACCEPTABLEは2件(B1-a/b)のみ。B4-b/cは「ACCEPTABLE〜QUALITY」をfail-closed側のQUALITYへ、B4-dは「QUALITY〜BLOCKING」をBLOCKINGへ倒している。**ラベル付けの段階で既にfail-closed側に3件寄せた上で、Stage 2のtie-breakでもfail-closedにする**のは、同じ保守性を二重計上している。Stage 2の「解消率」中央50%という仮定は、この9件表では5/9=56%と整合するが、**その内訳の3件(QUALITY)は「欠陥を含んだまま無審査で公開される」**という新しい状態である(論点8)。

**(C) rubric基準1は、floor対象外のmaterialケースを止めるには**おそらく**足りる。しかし「B1-a/bを通す」側の確度は低い。** B1-a(ホルムズ海峡=重要航路)はrubricのACCEPTABLE定義「新しい固有名詞…を一切加えず」に対して**「ホルムズ海峡」「中東」という固有名詞を含む**。Ledgerに既出なら問題ないが、rubric文言だけを機械的に読むと**BLOCKING/ACCEPTABLEの境界で「固有名詞を加えている」と誤読されうる**。ACCEPTABLE定義は「Ledgerに無い**新規の**固有名詞」と明示的に書き換えるべき。

**(D) 入力縮小(段落±1)の懸念はB3型ではなく`qualifier_present`型に出る。** Ledgerは全文渡すのでB3(HF-007 conditionsが離れた箇所)は影響小、という§11-3の評価に私も同意する。ただし**negative候補表の実データが示すとおり、通るか止まるかを分けている最大要因は「ヘッジ表現の有無」**(候補1〜3=Standardはヘッジありで通過、同一runのAdvancedは断定でBLOCK)。ヘッジは段落をまたぐことがある(候補5「However, this is only one report. It would be wrong to say this about all contract workers.」は直前段落の主張に対するヘッジ)。段落±1でも大半は拾えるが、**「記事末尾の総括段落に置かれたヘッジ」は落ちる**。これは降格漏れ(=KPI悪化)方向のリスクで、Safety方向ではない。

**(E) floorの5フラグ選定は妥当だが、`changed_certainty`を外した判断はラベル表と矛盾している。** §4-3は`changed_certainty`をfloor対象外とし、§7-0はB4-d(certainty変化)を「境界未確定のためTrial上はBLOCKING(fail-closed)」としている。**「ラベル上は必ずBLOCKING、しかしfloorでは守らない」** ため、Stage 2がB4-dを降格させたら受入判定が曖昧になる(§7-4は「観測記録する」としているが、Safety regressionなのか許容なのかの判定基準がない)。

### 【Evidence】
- 設計書 §4-4(L303-320、入力にStage 1 deviation出力全体+段落±1)、§4-2(L263-273、rubric+tie-break)、§4-3(L276-290、floor 5フラグ・certainty除外)、§4-6(L345-353、独立性はPrompt/call分離のみ)、§7-0(L471-481)、§7-4(L515)
- `C:\Users\tensh\eigo-radio\docs\pm\negative_claim_candidates_open233_01.md` L25-31(同一Ledger・同一内容でStandard[ヘッジ]は通り、Advanced[断定]は止まる)、L41-42(候補5・6のヘッジ)
- 前任レビュー `docs/pm/opus_l2_review_open233_checker_trial_01.md` L74(2段階呼び出しの趣旨=Stage 1 Prompt据え置き)

### 【Safetyリスク】
- (A)のanchoringはSafetyを**上げる**方向(降格しにくい)なので、Safetyリスクではなく**KPIリスク**。逆にanchoringを除去すると降格が増えるため、その時点でSafety検証が必要になる。両立させるには推奨1(下記)のように**flags/severityはfloor判定にのみ機械利用し、LLMには見せない**のが正解。
- (E)のcertainty不整合は、Safety受入判定の不定性を残す。

### 【Cost影響】
- Stage 1 explanation(reasoning由来で長い)をStage 2入力から外すと入力トークンが確実に減る。**独立性とコストが同方向**に改善する珍しい箇所。
- §3-5は「Stage 2 call数 = 最大2 × 検出claim数」と定義しているのに、§13-6のworst caseは「Stage2 2 call ¥0.70」しか計上していない。**B4は1 instanceで4 deviation検出の実例がある**ので、claim単位callだとStage 2は¥1.40/instanceになりworst caseはさらに¥1.4程度悪化する。**§13-6は自設計の§3-5と不整合**。

### 【推奨案(優先順位)】
1. **Stage 2 LLMへの入力から、Stage 1の`explanation`・`severity`・10 flagsを外す**。渡すのは「対象claim本文」「Ledger全文」「source context」「段落±1」のみ。10 flagsは**Stage 2の外側でfloor判定にのみ使う**。これで独立性・コスト・降格能力が同時に改善する(ただし降格が増えるのでSafety群での検証が必須)。
2. **Stage 2をinstance単位1 callにbatch化**(claim配列を入力、materiality配列を出力)。Ledger全文の再送を検出claim数ぶん節約でき、§3-5の「2×claim数」という最大のコスト膨張要因を除去できる。リスク: claim間の相互汚染(1件のBLOCKINGが他claimの判定を引きずる)。**Phase 1でper-claim vs batchを同一入力で比較(数円)**すれば判定できる。
3. rubric ACCEPTABLE定義を「**Ledgerに無い新規の**固有名詞・数値・時期・主体・因果を一切加えず」に明文修正(現文言は「新しい固有名詞」で新規性の基準が曖昧)。
4. `changed_certainty`をfloorに入れるか、§7-0のB4-dラベルを「観測のみ・受入判定に使わない」と明記するか、どちらかに統一する。
5. 段落±1の不足はLLMの自己申告(§4-4(b))に頼らず、**「ヘッジ語(may/some/seems/would/not always/only one 等)が段落±1外にあるかを¥0のregexで検出し、あれば±2へ拡張する」** という決定論的な拡張条件にする(自己申告は非決定的で漏れる)。

### 【USER_DECISION_REQUIRED該当】
- 推奨1・2はTrial内実装であり**非該当**。ただし推奨1は降格率を上げる方向なので、**Safety群100%維持が崩れた場合は即STOP**(§12条件2の入口)。
- (B)の「QUALITY=無審査で公開」は論点8で述べるとおり**条件2に触れる論点**。

---

## 論点4. Rewrite戦略(局所Rewriteで正当BLOCKINGを安全に直せるか)

### 【所見】
**(A) 「局所Rewriteが正当BLOCKINGを直せるか」は、claimの型によって答えが違う。** 3類型に分けるべき:
- **削除で直る型**(B1-c 市場動機の断定、B3の接続詞"so"、B4-a フォールバック機構の新規主張): Ledger外の付加物を**削る**だけで解消する。局所Rewriteは有効かつ安全(新情報を足さないので新規逸脱を生まない)。ここは設計の見込みどおり。
- **置換が必要な型**(changed_actor、changed_number): Ledgerの正しい値に**置き換える**必要がある。Ledger該当fieldを渡せば機械的に近いので、これも局所Rewriteの方が全文再生成より安全。
- **範囲の再限定が必要な型**(hormuz_run03_standard HF-009 changed_scope「Brent先物→石油市場全体」): 「whole market」を「Brent futures」に狭める編集は、**A2(平易英語)の語彙制約と衝突する**可能性がある。Standardは平易化のために一般化した疑いが強く(negative候補表の観測と整合)、局所編集で狭めるとA2の読みやすさGateや語彙制約と競合する。**この型が局所Rewriteの最難関**であり、かつ実データで唯一の未解決ケース。
**設計書はこの型別分析を持っていない。** 「Rewriteが直せるか」を型別に定義しないまま「12〜18 cycle実行」しても、成功/失敗の原因が切り分けられない。

**(B) 「Rewriteが新たな逸脱を生む」リスクの評価が、n=1の逸話に依拠しているという§11-4の自己批判は、実は逆。** Hormuz run_03のStandard新規MAJORは「全文再生成が新逸脱を生んだ」例として引かれているが、**因果としてはそう読めない**: 案BはJA本文を再生成し、Standardはその新JA→新Advanced→新Standardという**全く別の入力から生成された**。つまり「同じ記事の無関係箇所が変わった」のではなく「上流が変わったので下流が全部変わった」。局所Rewriteの必要性を支持する例としては弱い。**局所Rewriteの真の利点は「新逸脱の抑制」ではなく「コスト削減とJA/EN整合維持」**であり、そう位置づけ直した方が正確で、Phase 1の検証設計も変わる(検証すべきは「局所置換後にRecheckが新規MAJORを出さないか」ではなく「局所置換で当該claimが解消し、かつ構造Gateと段落数Gateを壊さないか」)。

**(C) 全文Recheckをfail-closedで採る判断(§5-2)は正しいが、それだけでは不十分。** 詳細は論点5(`all_prior_issues_resolved`)。

**(D) 局所Rewrite失敗時に「cycleを1消費してStage 4へ」(§5-2 guard)は、KPIに対して過剰に厳しい。** 構造Gate(`TOO_FEW_PARAGRAPHS`等)抵触は**文字列置換の副作用**であり、置換を破棄して元に戻せばよい(¥0)。「cycle消費+Stage 4直行」ではなく「**置換破棄→同一cycle内でrewrite再生成1回**」または「**置換破棄→全文must-fix retry(既存Production機構)へフォールバック**」の方が、Safetyを落とさずKPIを守れる。

### 【Evidence】
- 設計書 §5-1(L359-378、局所RewriteはPhase 1スコープ外)、§5-2(L388-411、局所Rewrite入力・guard・Recheck全文)、§11-4(L714-722)
- `C:\Users\tensh\eigo-radio\FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md` L1209-1228(案B=JA再生成→Advanced/Standard再実行の上でStandardに新MAJOR。上流入力そのものが別物)
- `C:\Users\tensh\eigo-radio\er012_e_family_entertainment_two_level_runner_01.py` L294-325(段落数retryは独立軸・1回上限)、L408-414/L502-508(must-fix retry後の段落数NGは即STOP)
- `C:\Users\tensh\eigo-radio\docs\pm\negative_claim_candidates_open233_01.md` L25-31(Standardの平易化=一般化が判定を分ける構造)

### 【Safetyリスク】
- 局所Rewriteが**Ledger外の情報を足す**リスクは、入力に「Ledger該当箇所+rewrite_hint+対象文±1文」だけを渡す設計(§5-2)である限り低い。ただし**「Ledger該当箇所」だけを渡すとLedgerの他factと矛盾する文を書く**余地が残る(B3のようにconditionsが別factにある場合)。**局所RewriteにもLedger全文を渡すべき**(入力トークンは増えるが、Stage 2と同じfail-closed判断で一貫する)。
- 論点1(A)の**JA/EN乖離**が最大のSafetyリスク。origin=ja_sourceのclaimをEN局所Rewriteで直すことは、Phase 1では**明示的に禁止**すべき(原因を直さず症状を消す操作であり、audioはEN/JA双方から作られる前提が壊れる)。

### 【Cost影響】
- 局所Rewrite単価見積り¥0.15〜0.35(§13-4)は「出力トークンが全文regenの1/5〜1/8」という外挿。**入力側(Ledger全文+段落)は減らないので、実際は¥0.3〜0.6程度になる可能性が高い**(gpt-6-luna 入力$0.10/1M、Ledger 3〜4k tokenで入力だけで¥0.05〜0.07、reasoning出力が支配的)。Phase 1で実測必須。
- 推奨(D)の「置換破棄→再生成1回」は+1 call(¥0.3前後)でEscalation 1件を救う可能性があり、**Escalation 1件のコスト(ユーザー時間)に対しては明らかに割安**。

### 【推奨案(優先順位)】
1. **Rewrite対象claimを型分類(削除/置換/範囲再限定)し、型ごとに成功基準を定義する**。Stage 2の`rewrite_hint`schemaに`rewrite_kind: "delete" | "replace_with_ledger_value" | "narrow_scope"`を追加(¥0)。`delete`型は**LLMを使わず決定論的に文を削れる可能性がある**(最も安く安全)。少なくともPhase 1で「delete型は決定論削除で解消するか」を測るべき。
2. **origin=ja_sourceのclaimにEN局所Rewriteを適用しない**ことを設計に明記(論点1推奨1のpaired local rewriteで対応)。
3. 局所RewriteにもLedger全文を渡す(fail-closed)。
4. §5-2のguard抵触時の扱いを「置換破棄→同一cycle内で1回再試行→なお失敗なら既存全文must-fix retryへフォールバック→それも失敗でStage 4」に変更。
5. Recheckは全文で維持(§5-2どおり)。**加えて論点5推奨1(`prior_issues`の必須化)を併用**。

### 【USER_DECISION_REQUIRED該当】
- いずれもTrial内実装で**非該当**。ただし推奨2を守らずEN局所RewriteでJA起因逸脱を消す運用は、**「JAとENが違うことを言う記事を無審査で公開する」= 条件2(Safety緩和)相当**と私は判断する。ここは明示的にユーザー確認を取る価値がある。

---

## 論点5. Safety(「重大Fact見逃し0件」をフロー全体で担保する論理の穴)

### 【所見】
**(A) 最大の穴: このフローは「検出されないこと」で終了できる回数を増やしている。**
Stage 1のrecallは実データで85〜100%(hormuz V4A 17/20)。Rewrite後のRecheckも同じCheckerである。したがって:
- 現行Production: 実質的な判定抽選は1〜2回(初回check、must-fix後のrecheck)。
- Self-Recovery Flow: 初回Stage 1 + Stage 2降格 + Recheck①(cycle 1) + Recheck②(cycle 2) = **最大4回の「通過しうる分岐」**。
Rewriteが当該逸脱を実際には直していない場合でも、**Recheckが15%の確率で見逃せば「Rewrite自動解消」として記録され、記事はPASSする**。cycleを増やすほど「幸運な非検出で抜ける」累積確率が上がる。**Escalationゼロ化とは、定義上この幸運な抜けを増やす操作でもある。** §10リスク4は「全文Recheckでfail-closed」としているが、**全文Recheckは「同じ非決定的Checkerをもう一度引く」だけで、fail-closedにはなっていない**。

**(B) この穴は、既にProductionコードにある機構で¥0に近いコストで塞げる。** `vfl01.run_deviation_check(..., prior_issues=[...])`は前回指摘の各項目が解消されたかを個別判定させ、`prior_issues_resolved`/`all_prior_issues_resolved`を返す。現行Productionは**`overall_status=="LEDGER_COMPLIANT"` かつ `all_prior_issues_resolved`の両方**を成功条件にしている(`er012_...py` L423、`er019_family_x_ja_writer_o_r1_r2_01.py` L304)。**設計書はこのフィールドに一言も触れておらず**(私のgrepで`prior_issues`/`all_prior_issues_resolved`の出現0件)、Stage 1 Recheckのマッピングは`overall_status`のみ(§3-0/§3-1)。これは:
- (i) **既存のfail-closed gateを1本、無言で外している**(= 条件2に触れる可能性)。
- (ii) (A)の「非検出による誤PASS」を塞ぐ最も安い手段を捨てている。同一callにprior_issues判定を載せるだけなので**追加callは0**、入力トークン増のみ。

**(C) pre-checkの誤PASS/floor空振り**は論点2(C)のとおり。pre-check由来項目はfloor扱いにしないとStage 2で降格され得る。

**(D) Trial Safety群の代表性は弱い。** §7-1のSafety群は`er009` 9種(合成)+changed_actor(合成)+A2A3/A4/A5(実データ由来だが「露骨な」逸脱)+hormuz/Meta run03_standard(実データ)。**実データで実際に見逃しが観測されているのはhormuz_run03_standardのみ**で、それも85%。「Safety群12/12=100%」は**合成fixtureの露骨さに支えられた数字**という前任Opusの指摘(論点4【Safetyリスク】)は、n=20実測後も本質的に変わっていない。フロー全体の見逃しゼロを合成fixtureで主張するのは不可能。

**(E) Stage 2の「判断不能はBLOCKING扱いでStage 3へ」(§6-1)は正しいが、Stage 1のAPI失敗・schema失敗の扱いが未定義。** Stage 1が失敗した記事が「deviationなし」として扱われれば無検査で通る。fail-closedを明記すべき。

### 【Evidence】
- `C:\Users\tensh\eigo-radio\er003_v1_en_direct_vfl_01_generate.py` L649-656(`prior_issues`指定時に`prior_issues_resolved`/`all_prior_issues_resolved`を返す。「呼び出し側は両方を見て最終成功を判定すること」と明記)、L678-688(`build_prior_issues_instruction`)
- `C:\Users\tensh\eigo-radio\er012_e_family_entertainment_two_level_runner_01.py` L415-432(recheckに`prior_issues=must_fix_used`を渡し、`LEDGER_COMPLIANT` かつ `all_resolved`でなければSTOP)、L509-523(Standard同型)
- `C:\Users\tensh\eigo-radio\er019_family_x_ja_writer_o_r1_r2_01.py` L298-312(JA側も同型)
- 設計書 §3-0(L144-152、Recheckは「既存Production Checkerを再実行」のみ)、§3-1(L186-188、`overall_status`→2値routing)。`prior_issues`関連の記述は設計書全文に**0件**(grep実施)
- `OPEN-233-CHECKER-REDESIGN-TRIAL-01_REPORT.md` L337-340(hormuz V4A 85%、95%CI [64.0%, 94.8%])

### 【Safetyリスク】
- (A)+(B)が**本レビューで最も重大な指摘**。現状の設計のまま10〜20記事Trialを回して「Escalation 0件・Safety群100%」という結果が出たとしても、**その0件のうち何件が「非検出による誤PASS」なのかを区別できない**(区別する測定項目が§8に無い)。「安全≠成功」原則に照らして、これはTrial設計の欠陥。

### 【Cost影響】
- `prior_issues`併用は追加call 0。入力トークン+数百token(¥0.01未満/call相当)。**Cap影響は無視できる**。
- 逆に、これを入れるとRecheckが厳しくなり**Escalationが増える方向**(KPIとトレードオフ)。だが「見逃しを誤PASSで隠さない」ことが前提条件であるべきだと私は考える。

### 【推奨案(優先順位)】
1. **Stage 1 Recheckで`prior_issues`を必ず渡し、継続条件を「`LEDGER_COMPLIANT` かつ `all_prior_issues_resolved==True`」にする**(= 現行Productionと同じ厳しさを維持する)。**これはPhase 1実行前に必ず直すべき最優先事項**。
2. §8-1の測定項目に「**Rewrite自動解消件数のうち、`all_prior_issues_resolved==True`で裏付けられた件数**」と「**同一claimがRecheckで無言消滅した件数(誤PASS候補)**」を追加する(¥0)。これが「Escalationゼロが見逃しで作られていないか」を検証する唯一の内部指標になる。
3. **Rewrite後の局所検証を1つ追加(¥0)**: `rewrite_kind=="delete"`なら、当該文字列がRecheck対象本文から消えたことを機械確認。`replace_with_ledger_value`なら、Ledgerの値が本文に出現することを機械確認。Checkerの非検出に依存せず「直ったこと」を確認できる。
4. Stage 1のAPI/schema失敗はfail-closed(Stage 2へ強制送付、またはEscalation)と明記。
5. Safety群に**実データ由来のnegative-but-material例を増やす**。ただし新規fixture作成は¥0では難しい。現実的には「hormuz_run03_standardのn=20で見逃した3回のattempt」を保存済みrawから特定し、**その3回のStage 1出力(deviations=[])をStage 2/pre-checkに投入して、後段が独立に拾えるかを¥0〜数円で確認する**(検出漏れ補完の実効性を直接測る唯一の実データ実験)。

### 【USER_DECISION_REQUIRED該当】
- **推奨1を採らない(= `all_prior_issues_resolved`を継続条件から外す)ことを選ぶ場合は、条件2(重大Fact Safetyの緩和)に該当する**と私は判断する。既存Production gateの除去に相当するため。**Fable/Claudeが独断で決めるべきではない**。
- 推奨2〜5は**非該当**(測定・fixture追加・¥0)。

---

## 論点6. Cost(+¥3/記事Cap、worst case ¥3.96、より安い代替)

### 【所見】
**(A) §13の前提のうち、根拠があるのは単価だけで、発動率3項目(BLOCK率/Stage 2解消率/cycle 2必要率)とJA-origin比率は根拠が弱い。**
- **JA-origin 40%**: 実測は5件中4件=**80%**(Hormuz 4件ja_source、Meta 1件translation)。n=5と小さいが、**唯一の実データは40%を支持していない**。方向としては「期待値の節約はさらに大きく(中央シナリオ−¥0.06→私の再計算で約−¥0.3前後)、worst caseは不変(既にJA前提)」。つまりこの誤りは結論を悪化させないが、**根拠なき数字がモデルに入っている**ことは中間報告として明示すべき。
- **BLOCK率**: V4A採用でMAJOR率が上がる方向なのに据え置き(論点2(B))。これは**結論を悪化させる方向の未反映**。
- **Stage 2解消率50%**: 論点3(A)(B)のとおり、anchoring+二重fail-closedで実際はこれより低い可能性がある。低いと節約が消える。

**(B) §13-6のworst caseは、自設計の§3-5と不整合で、少なくとも過小。** §3-5は「Stage 2 call数 = 最大2 ×(Advanced+Standardの検出claim数)」なのに、§13-6はStage 2を「2 call ¥0.70」で計算している。B4の実例では1 instanceで4 deviation。claim単位callなら**Stage 2だけでworst caseは+¥1.4程度**増える → ¥3.96は¥5前後になり得る。逆に、案B実測¥4.02には`_run_writer_stage_once(only=None)`の再実行(Advanced+Standard生成+deviation check)が**既に含まれている**ため、§13-6が別途足している「2段recheck ¥1.274」は**二重計上の疑い**がある。**要するに±¥1〜1.5の誤差があり、「V4AでCapを32%超過する」という結論自体がモデルの誤差範囲内**。この数字で採否を議論するのは生産的でない。**構造的なコストドライバを削る方が先**。

**(C) 未活用の大きな節約レバーが2つある(設計書に記述なし)。**
1. **prompt caching**: gpt-6-lunaのcached input単価は$0.01/1M = 通常input $0.10/1Mの**1/10**(§13-1の一次ソース表)。1記事内でLedger全文は Stage 1 Advanced / Stage 1 Standard / Stage 2(claim数ぶん) / Recheck(cycle数ぶん)と**何度も同一prefixとして再送**される。Ledgerを固定prefixに置く設計にすれば入力コストが大幅に下がる。**V4A固定費+30%(Prompt文字数増が主因、§13-4-補)もcachingでほぼ相殺できる可能性がある** → V4A採用とCap遵守の両立が見えてくる。**これがCap問題に対する最も筋の良い一手**だと私は考える(受理可否・キャッシュヒット条件は要実測)。
2. **Stage 2のbatch化**(論点3推奨2): claim単位N callをinstance単位1 callにすれば、Ledger全文の再送がN→1。

**(D) Cap定義の曖昧さ(要確認)。** 純増分 = 新方式総コスト − 現行方式総コスト(§13-5)という定義は妥当だが、**現行はSTOPした記事のdownstream(TTS/audio)コストを払わない**。Escalationゼロ化はそれらの記事をaudio段へ進めるため、**「記事あたり総コスト」は+¥3どころではなく増える**(TTSが支配的)。Capが「Ledger/Deviation Check関連のLLMコストに限る」という解釈であることを、Checkpoint Aで明文確認しておくべき(意図された便益であって超過ではない、という整理が必要)。

### 【Evidence】
- 設計書 §13-1(L847-853、cached input $0.01/1M)、§13-4(L905-912)、§13-4-補(L918-938)、§13-5(L963-996)、§13-6(L998-1031)、§3-5(L242、Stage 2 call = 2×claim数)
- `C:\Users\tensh\eigo-radio\FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md`(Hormuz 4件ja_source / Meta 1件translation の内訳は論点1【Evidence】の行番号参照)
- `C:\Users\tensh\eigo-radio\er012_e_family_entertainment_two_level_runner_01.py` L654-655(案B後の再実行は`only=None`で両stage=実測¥4.02に含まれる)
- `er051_output/.../trial_02/step2/summary_trial2_step2.json`(B4 V4Aで4 deviation)

### 【Safetyリスク】
- コスト削減のうち、**Stage 2入力のLedgerを部分化する案(§13-10の代替案1)はSafetyリスクがある**(B3型=離れたconditionsを見逃す)。採らないことを推奨。cachingとbatch化はSafety中立なので、**そちらを先に使い切るべき**。

### 【Cost影響(推奨案適用後の私の見立て、いずれも未実測)】
- caching適用 + Stage 2 batch化 + `prior_issues`併用で、**中央シナリオは節約方向を維持し、worst caseはV4A込みでもCap内(¥2.5前後)に収まる可能性がある**。ただし**すべて未実測であり、確度は低い**と明記する。

### 【推奨案(優先順位)】
1. **prompt caching(Ledger prefix固定化)の受理可否と実効削減率をPhase 1で最優先実測**(数円)。Cap問題の本命。
2. **Stage 2 batch化**(instance単位1 call)。
3. **§13-6をclaim数を変数にした式へ書き換え**、二重計上(recheck)を精査する。現行の¥2.88/¥3.96という単一数値での議論をやめる。
4. JA-origin比率を40%→実測値(暫定80%、n=5)へ改め、根拠を明記。BLOCK率はV4A実測(論点2推奨1(a))で置き換える。
5. worst case対策としては、§13-10の代替案のうち「**cycle 1でJA全文Rewriteを使った場合はcycle 2を発動せず直接Stage 4**」が最もSafety中立で安い。ただしこれは**Hormuz run_03型(= 実観測された唯一の未解決パターン)を確定的にEscalationさせる**ので、KPIとの直接トレードオフ。論点1推奨1(JA局所Rewrite)が実装できればこの選択は不要になる。
6. **「cycle上限を1に下げる」は推奨しない**。実観測パターン(Advanced解消→Standardで新claim)はcycle 2が必要な典型であり、上限1はKPIを確定的に落とす。

### 【USER_DECISION_REQUIRED該当】
- (D)のCap定義確認は**条件1(KPI)の解釈に触れる**ため、Checkpoint Aで確認すべき。
- worst caseがCapを超える件は、§13-10のとおり**Phase 1実測後に条件3の判定**。現時点で「超過が必要」と宣言する段階にはない(モデル誤差が大きすぎる)という設計書の判断に私も同意する。ただし**「V4A採用がCap超過の直接原因」という因果はCheckpoint Aで明示すべき**。

---

## 論点7. loop化リスク(cycle上限2、同一deviation再発、連鎖BLOCK)

### 【所見】
**(A) 「同一deviationの再発」を検出する仕組みが設計に無い。** cycle 2はcycle 1と同じ条件で発火する。しかし**cycle 1と同一のclaim/fact_idが再びBLOCKINGになった場合、Rewriteが効かなかったことが実証されている**のだから、cycle 2に同じ手段を使うのは¥の無駄(KPI改善もない)。逆に**別claimが出た場合(Hormuz run_03型)はcycle 2に意味がある**。この2つを区別していないのが設計の穴。

**(B) 連鎖BLOCK(Hormuz run_03型)を止める唯一の方法は、上流を変えないこと。** run_03で新MAJORが出た原因は、案BがJA本文を全面的に作り替えたことにある(論点4(B))。**局所Rewrite(JA/ENとも)は、この連鎖の原因そのものを除去する**。つまり局所Rewriteは「新逸脱抑制」効果があると設計書は書いているが、**正確には「上流総取り替えによる下流全変化を防ぐ」効果**であり、そう定義すればHormuz run_03はn=1の逸話ではなく**機構的に説明のつく実例**になる。§11-4の自己批判(「単なるn=1の偶発事象では?」)に対する私の答えは「**偶発ではないが、引かれている因果は不正確**」。

**(C) cycle上限2は妥当。ただし「上限に達したらStage 4」が正しいのは、`all_prior_issues_resolved`を併用した場合に限る。** 併用しないと、上限に達する前に「幸運な非検出」で抜ける方が起きやすくなる(論点5(A))。**loop上限はSafetyを守る仕組みだが、非検出による早期脱出はその上限を迂回する。**

**(D) 見落とされているloop軸: 段落数retry × Rewriteの相互作用。** `_family_x_ensure_split_or_paragraph_retry`は1回上限、そのretryを使い切った後にdeviation must-fix retryで段落数NGになると即STOP(L408-414/L502-508)。局所Rewriteは文字列置換なので段落数を壊しにくいが、**案Bによる全面再生成では段落数retryが再抽選される**。Stage 4条件表にこの軸が無い。

### 【Evidence】
- 設計書 §3-3(L226-232、cycle上限)、§5-3(L415-422)、§10リスク1/4(L657, L660)、§11-7(L752-762)
- `C:\Users\tensh\eigo-radio\er012_e_family_entertainment_two_level_runner_01.py` L294-325(段落数retry 1回上限)、L408-414/L502-508(retry後の段落NGは即STOP)
- `C:\Users\tensh\eigo-radio\FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md` L1223-1229(Standardで新claim、案B 1回上限でSTOP)

### 【Safetyリスク】
- (C)のとおり、loop上限そのものはSafety側。危険なのは**上限に達せずに抜ける経路**。

### 【Cost影響】
- (A)の同一claim再発検出を入れると、無駄なcycle 2(Stage 2 + Rewrite + Recheck ≒ ¥1.5〜5)を節約できる。**worst case削減に直接効く**(¥3.96 → 同一claim再発ケースでは¥2.5前後)。

### 【推奨案(優先順位)】
1. **cycle 2の発火条件に「cycle 1と異なるclaim/fact_idであること」を加える**。同一claim/fact_idの再BLOCKINGは即Stage 4(Rewriteが効かないことが実証済みのため、追加投資しない)。**Safety中立・コスト削減・KPIへの悪影響は最小**(同一claim再発はもともと回復見込みが低い)。
2. cycle間で「どのclaimをどう直したか」の履歴をStage 2/Stage 3の入力に含める(前回の`rewrite_hint`と適用結果)。同じhintを繰り返さないため。**ただし論点3(A)のanchoring懸念と衝突するので、materiality判定には渡さず、Rewrite生成にのみ渡す**。
3. Stage 4条件表に段落数retry軸・symbol gate軸を追加(論点1推奨3と同じ)。
4. cycle上限2は変更不要(ユーザー指定固定値でもある)。

### 【USER_DECISION_REQUIRED該当】
- **非該当**(いずれもTrial内実装、Safety緩和なし、Cap内)。

---

## 論点8. Escalationゼロの現実性(10〜20記事の代表性、「安全≠成功」との整合)

### 【所見】
**(A) 統計的に、10〜20記事で0件を達成しても「実質ゼロ」の証拠にはならない。** 0/20の観測が与える真のEscalation率の95%信頼区間上限は約**16.8%**(Wilson/Clopper-Pearson)。0/10なら約**28%**。つまり「20記事で0件」は「Production で6記事に1回STOPする」可能性を排除できない。**現状(数記事に1〜2件)と区別できない水準**。「Escalation率≤5%を95%信頼で示す」には**0/59記事**が必要。**Primary KPIの測定計画(10〜20記事)は、KPIの主張(実質ゼロ)を支える統計的検出力を持っていない。** これはKPIの妥当性そのものの問題であり、Phase 2計画の前にユーザーへ提示すべき。
- 代替の測定設計(より安い): **記事数ではなくBLOCK事象数でパワーを稼ぐ**。「Stage 2の降格成功率」「Rewrite解消率」を事象単位で測れば、10〜20記事でも数十事象になり、それらの積からEscalation率を**推定**できる(直接観測より高いパワー)。§8の測定項目はこの方向にほぼ揃っているので、**KPIの判定を「記事単位で0件」ではなく「事象単位の各段階成功率から推定したEscalation率の信頼区間上限」に置き換える**ことを推奨する。ただし**これはKPIの再定義であり条件1に該当**する。

**(B) 「安全≠成功」との整合について: 本設計は3つの経路でSafetyを静かに削り得る。** 率直に述べる。
1. **QUALITY通過という新カテゴリ**: 現行Productionでは、B2型(Ledgerが明文で禁じた因果接続)はMAJOR → STOP。新設計では**QUALITY → 人間を通さず公開**。Safetyリスト(§1の8項目)は変えていないが、**「公開されるものの品質下限」は確かに下がる**。§7-2はB2/B4-b/cをQUALITY通過期待としており、これはKPI達成に必要な要素である。**私の見解: これは条件2(Safety緩和)に該当するかどうかをユーザーが判断すべき事項**であり、Fable/Claudeが「Safety項目を変えていないから非該当」と整理して進めるのは危うい。
2. **非検出による誤PASS**(論点5(A))。
3. **EN局所RewriteによるJA/EN乖離**(論点4)。
**「Escalationゼロが達成された」という結果は、上記3経路のどれで達成されたかを分離できなければ、成功の証拠にならない。** §8の測定項目には1(QUALITY件数)は入っているが、2・3の測定項目が無い。

**(C) Phase 1の設計に抜けがある(重要度順)。**
- **BLOCK率(V4A)の実測が入っていない**。§9-1はStage 2への既存deviationレコード再利用(¥0)とStage 3のcycle実行だけ。**コストモデル最大の乗数を測らない計画になっている**。negative候補の出典7記事をV4Aで再実行すれば¥1.5〜3で測れる(論点2推奨1(a))。
- **pre-checkのFP率測定が入っていない**(¥0で可能、論点2推奨4)。
- **Stage 2入力の再利用元がV2/V3/V4A混在**(§9-1)。Stage 1をV4Aで確定したなら、**Stage 2評価はV4A由来レコードに限定**しないと、測定されたStage 2降格率がどのStage 1構成に対するものか帰属できない。
- **negative 16件はStage 2を検証しない**。16件は既に`deviations=[]`で通過済みなので、Stage 1のみで完結する(§7-5も認めている)。**Stage 2の「通せるか」を検証する材料は実質B1-a/b の2件しかない**。Stage 2の降格能力のn不足はPhase 1の構造的限界として明記すべき。
- **hormuz n=20で見逃した3 attemptのStage 1出力を使った「後段が拾えるか」実験が無い**(論点5推奨5)。
- **Phase 1と Phase 2のモデル差**(gpt-6-luna vs Production gpt-5.6-luna)は§10リスク8で自認されているが、**Phase 1の結論のうち何がモデル依存で何が構造依存かを事前に分類していない**。構造依存の結論(例: `all_prior_issues_resolved`の有無、pre-checkのFP、JA/EN乖離、call数)はモデル差の影響を受けないので、**Phase 1ではそれらを優先的に確定させるべき**。

**(D) Production化後の継続監視(§11-8の問い)への答え。** Human Reviewを通常運用にしないという制約下で有効なのは:
1. **shadow sampling**: 公開記事のうち**一定率(例: 5〜10%)だけ**、公開後に2回目のStage 1 Checkを別runで実行し、初回と不一致(2回目でMAJOR)なら人間へ通知する。非検出率を継続推定できる。コストは全数の5〜10%分(¥0.03〜0.06/記事相当)で**Cap内**。
2. **QUALITY通過件数の週次レビュー**(記事単位ではなくclaim単位のサンプル)。QUALITYが増加傾向なら品質下限が下がっているサイン。
3. **決定論的指標の常時監視**(¥0): pre-check発火率、Rewrite適用文字数、cycle消費率、`all_prior_issues_resolved=false`率。
**これらは「Human Reviewを通常運用にしない」制約と両立する**(全数審査ではなくサンプリング+機械指標)。

### 【Evidence】
- 設計書 §9-2(L644-651、Phase 2 = 10〜20記事でPrimary KPI測定)、§9-1(L597-629、Phase 1計画)、§7-2(L493-499、QUALITY通過期待)、§7-5(L517-528、negative 16件はStage 1のみで完結期待)、§11-8(L764-774)、§10リスク8(L664)
- `C:\Users\tensh\eigo-radio\docs\pm\negative_claim_candidates_open233_01.md` L11-15(28件が`deviations=[]`、うち7ファイルから16 claim抽出)
- `C:\Users\tensh\eigo-radio\OPEN-233-CHECKER-REDESIGN-TRIAL-01_REPORT.md` L337-340(Wilson CIの実例。同じ考え方をEscalation率に適用した)

### 【Safetyリスク】
- (B)の3経路が分離測定されないまま「Escalation 0件」が報告されると、**Trial結果が「安全が確認された」と誤読される**。PM_GOVERNANCEの「安全≠成功」原則に照らし、**Trial報告テンプレートに「0件の内訳(真の解消/QUALITY通過/誤PASS候補/未検証)」を必須項目にすべき**。

### 【Cost影響】
- (D)1のshadow samplingは5〜10%サンプルで¥0.03〜0.06/記事。Cap内で「見逃し率の継続推定」を得られる**唯一の現実的手段**であり、費用対効果は高い。

### 【推奨案(優先順位)】
1. **Phase 1に「BLOCK率(V4A)実測」「pre-check FP率(¥0)」「hormuz見逃し3件に対する後段補完実験」を追加**する。現計画のままではCap判定・Safety判定の両方が結論不能。
2. **KPI判定方法を「記事単位0件」から「事象単位の段階別成功率+その信頼区間からのEscalation率推定」へ変更することをユーザーに提案**(条件1該当)。10〜20記事では0件でも何も言えないという統計的事実を、数字(0/20 → 上限16.8%)で提示する。
3. **Trial報告に「Escalation 0件の内訳」を必須項目化**(真の解消 / QUALITY通過 / `all_prior_issues_resolved`未確認 / 誤PASS候補)。
4. **Phase 1ではモデル非依存の結論(構造的欠陥)を先に潰す**: `prior_issues`併用、pre-check FP、JA/EN乖離ルール、call数・batch化、caching。
5. Production化後の継続監視としてshadow sampling(5〜10%)を設計に組み込む(Phase 2の設計項目として)。

### 【USER_DECISION_REQUIRED該当】
- 推奨2は**条件1(KPI変更)に該当**。
- (B)1のQUALITY通過(人間を通さずLedger非保証の因果接続を公開する)は、**条件2(Safety緩和)に該当するかをユーザーに確認すべき**と私は判断する。少なくともCheckpoint Aで「新設計では現行STOPしていたB2型が無審査で公開される」と明記して提示すべき。
- 推奨1・3・4・5は**非該当**。

---

## 【総合】

### A. Phase 1 Trial実行前に必ず直すべき点(優先順位)
1. **Stage 1 Recheckで`prior_issues`を渡し、継続条件を「`LEDGER_COMPLIANT` かつ `all_prior_issues_resolved==True`」にする**(設計書に`prior_issues`の記述が0件。現行Productionにある既存fail-closed gateを無言で外している。追加call 0)。これを直さないと、Trialで得られる「Rewrite自動解消件数」が誤PASSと区別できず、**Safety KPIの検証自体が成立しない**。
2. **pre-check由来検出をfloor扱い(Stage 2でLLM降格不可)にする**。現設計では、Stage 1が見逃した項目はflagが全falseなのでfloorが空振りし、Stage 2で降格され得る(検出漏れ対策が後段で無効化される穴)。
3. **pre-checkのFP率を¥0で先に測る**(既存`LEDGER_COMPLIANT`記事28件にregexを適用するだけ)。FPはRewriteで直せないため**確定的にEscalationを生み、Primary KPIを直接壊す**。§14-4の「誤って安全性を下げることがない」は正しいが「KPIを下げることがない」は誤り。
4. **origin=ja_sourceのclaimにEN局所Rewriteを適用しないことを明記**(JA/EN乖離を誰も検査しない)。同時に、§5-3の「cycle 2はEN局所のみ」が支配的ケース(ja_source 80%)で機能しないことを設計上の未解決事項として明記。
5. **cycle 2の発火条件に「cycle 1と別claimであること」を追加**(同一claim再発は即Stage 4。Safety中立・コスト削減)。
6. **§13-6を式へ書き換え**(Stage 2 call数=claim数を変数化、recheckの二重計上を精査)。現行の¥2.88 vs ¥3.96は±¥1〜1.5の誤差内であり、この数値でCap判定を議論しない。
7. **Stage 4条件表をコード上の例外型と1対1対応させる**(symbol gate、段落数retry枯渇、予算abort、Stage 1 API失敗のfail-closed扱いが未定義)。

### B. Phase 1で最優先に実測すべき項目(順位付き、いずれも安価)
1. **V4AのBLOCK率増分**: negative候補の出典7記事(既に`deviations=[]`)をV4Aで再実行(7〜14 call ≒ ¥1.5〜3)。コストモデル最大の乗数(15/35/60%という仮置き)を潰す。**現Phase 1計画に入っていない。**
2. **prompt caching(Ledger prefix)の受理可否と削減率**(数円)。V4A固定費+30%とStage 2コストを同時に下げられる、Cap問題の本命レバー。
3. **Stage 2の実単価**(§13-10で自認されている最大の不確実要因)。per-claim vs instance単位batchの比較を同時に行う。
4. **pre-check FP率**(¥0)と、**hormuz n=20で見逃した3 attemptに対してpre-check/Stage 2が独立に拾えるか**(¥0〜数円)。検出漏れ補完の実効性を測る唯一の実データ実験。
5. **`er009_changed_actor`のV0/V4A各n=15追加**(30 call ≒ ¥6)。V4A採用の唯一の根拠(5/5 vs 3/6、Fisher両側p≈0.18、私の計算)を有意水準まで詰める。**この1点のためにworst caseがCap超になっている**ので、根拠を固めるか、V0+pre-checkという¥0の代替に置き換えるかを決められる状態にする。
6. **局所Rewriteの型別成功率**(delete / replace / narrow_scope)。特に`delete`型がLLMなしの決定論削除で解消するか(最安・最安全)。

### C. 「Escalationゼロ・見逃しゼロ・Cap内」の同時達成可能性についての率直な見立て

**不確実性を明記した上での見立て:**

- **「重大Fact見逃し0件」は、Production運用の主張としては達成不可能**だと考える。実データfixtureでStage 1のrecallが85〜100%(hormuz V4A 17/20、95%CI [64.0%, 94.8%])であり、Stage 2以降はStage 1が拾ったものにしか作用しない。pre-checkは意味的逸脱(scope一般化)を拾えない。**達成できるのは「測定したfixture集合で0件」という限定的な主張**であり、KPI文言をそう限定するか、shadow samplingで見逃し率を継続推定して上限を管理する運用に切り替えるかのどちらかが必要。ここは**不確実ではなく、構造的にそう言える**部分だと考える。
- **「Escalation実質ゼロ」は、現設計のままでは達成できない可能性が高い**。理由は2つ。(i) 実観測の支配的failure mode(ja_source 80%)に対する唯一の回復手段が¥3.5〜4.0のJA全文再生成で、§5-3のコストguardにより実効cycleが1しかない。(ii) 設計自身の正解ラベル(§7-1、hormuz_run03_standard=BLOCKING Confirmed)を実観測4事象に適用すると1件はRewrite必須のja_sourceで、そこが詰まる。**ただしこれは「JA側局所Rewrite(paired local rewrite)」を実装すれば解ける可能性がある**。設計はこれをPhase 2送りにしているが、**私の見立てでは本Phaseの成否を決める最重要実装項目**。ここは不確実性が大きい(新規実装、JA文体・記号Gate・段落Gateとの相互作用が未検証)。
- **「Cap内(+¥3/記事)」は達成可能性が高い、ただし現モデルの数値は信用できない**。期待値は3シナリオ全てCap内で、JA-origin実測80%を入れるとむしろ節約側に振れる。worst caseの¥3.96はモデル誤差(±¥1〜1.5)の中にあり、caching + Stage 2 batch化 + 同一claim再発の早期打ち切りで**Cap内に収まる見込みがある**(未実測、確度は中程度)。**Capが真に危ういのは、JA全文Rewriteを複数回許す設計に変更した場合だけ**。したがって「Cap内でEscalationゼロ」を成立させる鍵は、**JA側の回復手段を安くすること(局所化)**に集約される。
- **3条件の同時達成について**: 私の見立てでは、**「見逃しゼロ」を厳密な意味で要求する限り、3条件同時達成は不可能**。現実的な着地点は「(a) 見逃しゼロを『測定fixtureで0件 + shadow samplingで見逃し率上限を管理』へ再定義、(b) JA局所Rewriteでja_source回復を安くする、(c) Escalation率を『事象単位の段階別成功率から推定した上限』で管理」の3点セット。**(a)と(c)はKPI再定義(条件1)に該当するため、ユーザー判断が必要**であり、Fable/Claudeが独断で進めるべきではない。
- **最後に、最も強調したい1点**: 現設計のままPhase 1を実行すると、**「Escalation 0件」という結果が出ても、それが真の解消なのか、QUALITY通過なのか、Checkerの非検出による誤PASSなのかを区別できない**(区別する測定項目が§8に無く、`all_prior_issues_resolved`という既存の判別手段が設計から落ちている)。**総合Aの1と2、総合Bの1を先に入れること**が、Trialを意味のあるものにする前提条件だと考える。

### D. 入力範囲について
渡された範囲で本診断に必要な事実は概ね揃っていた。追加で読めば精度が上がるが現時点で必須ではないもの: (1) `er051_output/open233_checker_trial_01/trial_03_stability_n20/`の生attempt(hormuz V4Aで非検出だった3 attemptのraw出力。総合B-4の実験設計を具体化できる)、(2) `DECISION_LOG.md`の2026-09-30 OPEN-233-SELF-RECOVERY-TRIAL-01委任_01エントリ(ユーザー指示の逐語全文。設計書§1は「要旨」であり、KPI文言の厳密な表現を確認したい)、(3) `er003_v1_en_direct_vfl_01_generate.py`のLedger schema(`numeric_value`/`date_or_period`等の実フォーマット。pre-checkのFP率を机上で見積もるのに必要だったが、実測で代替できるため必須ではないと判断した)。

本診断はread-onlyであり、ファイル編集・テスト実行・API呼び出しは一切行っていない。Production採用の可否判断は含まない(人間ユーザーのみが承認できる)。実装や修正は本報告後に自動的に開始しない。

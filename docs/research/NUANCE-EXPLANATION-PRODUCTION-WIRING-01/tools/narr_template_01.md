# PROMPT_TRIAL_01 — ニュアンス解説Prompt品質Trial (NUANCE-EXPLANATION-PRODUCTION-WIRING-01 委任_01b、2026-10-29)

Status: Offline Trial(DEV/Trial専用。Production・Prompt・公開物・既存出力は未変更、読み取りのみ)。採用可否の判断はFable。VALIDATED/APPROVED_FOR_PRODUCTIONの付与なし。
正本原文: `docs/pm/delegation_log/2026-10-29_NUANCE-EXPLANATION-PRODUCTION-WIRING-01_USER.md` §2-A/B(最大1件・Key Phrase/Word(最大5件)と学習上の焦点が重複したらNG・候補なし可・過去Trial Promptの無検証採用禁止・Part 4等は導入しない)。

## 0. 結論(要約)

- 8記事レベル(X『AI島』Std/Adv、X『Paycheck Personality』Std/Adv、Z『告げ口心臓』Std/Adv、Y『宅配の再配達』Std/Adv)で、改良Prompt v1・v2を各1回生成(retryなし)+重複検査2段を実施。合計費用 **¥{TOTAL}**(上限¥10)。モデル=gpt-6-luna(本番ライン既定。`er006_model_routing_contract_01.py:50` SUPPORT_MODEL、`er003_v1_n3_01_scaffold_generate.py:61` `_a2_support_model()`。評価用途の「最新原則」(Charter 25節)とは別枠で、Productionに載るモデルでの品質確認が目的)。
- **v1**: 8/8で候補を生成(0件ゼロ)。重複検査は全件PASS(構造0/8 fail・LLM 0/8 fail・引用逐語8/8)。ただし学習価値はworker所見で 高3/中4/低1(`don't have to vs mustn't`=A2既習の基礎対比)。モデル自己評価は high 7/8 で識別力がない。人工の平易文(control)でも `stood vs stood up` を強制選定=「0件」が実質出ない。
- **v2**(学習価値4条件・基礎文法対比除外・Part 1/2との役割分担・入れ替えテスト): 実8中 候補5・0件3。候補5のうち1件(`was linked to`)は段1構造検査(`link`⊂`weak link`)でfail→破棄(段2 LLMはpass=段1と段2が不一致の境界事例)。HR提示可 4件。controlは0件(0件が出せることを確認)。一方、**過度な抑制と不整合**が出た(AI島Stdで `at least`=too_basic→0件、同AdvではPASS候補。告げ口心臓も Std=`You should have seen`採用/Adv=grammar_structureで除外)。
- 重複検査 段2(LLM)の感度確認(人工候補3件): 同義の言い換え(`pass on`↔carry over)・同じ比喩の別表現(`chill someone to the bone`↔make one's blood turn cold)を2/2でfail、非重複1/1でpass。**段1(構造)は人工の重複2件とも検出できず**、LLM判定が実質の主検査。
- 実生成物でKey Phrase/Wordと実質重複と判定された採用候補は0件(v1/v2とも)。生成時に自ら `kp_word_overlap` で外した候補が3件(v1 y_std「can't be helped」、v2 paycheck_std「Coming first and being the cause」、v2 y_std「I guess it can't be helped」)あり、生成時の差別化指示は機能した。
- 単価実測: v1 ¥{V1_SET}/記事セット(Std+Adv、生成+重複判定)、v2 ¥{V2_SET}/記事セット。ユーザー原文§6の概算(+0.10〜0.14円)の約3倍。主因=推論token(1回平均 v1 757/v2 931)。70円目標の約0.5%。

## 1. 素材の確認と弱点3点(Trial-01〜04のPart 3)

読んだもの: `docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/` の PROMPT_04.md:217-330(Part 3/4 Prompt=03d固定ブロック。`PROMPT_04.md:307`「0〜1個選ぶ。適切なテーマがなければ0個」)、OUTPUT_01_RAW.md、OUTPUT_04_*_USER.md の Part 3、FABLE_EVAL_01.md:6,8、FABLE_EVAL_02.md:7,10、EVAL_04.md:73。

1. **基礎語・品詞差などニュアンスではない題材を選びがち**: Trial-01 の worthy of / worth は品詞差の説明で「B1目標のAdvanced学習者に対する価値が低い」(FABLE_EVAL_01.md:6)。上位候補(shabby、Nothing showy、foolish↔wisest)を見送り、「0個でもよい」より「1つ選ぶ」方向に寄った(同:6)。
2. **選定が生成ごとに揺れ、物語解釈に寄る**: 同一Prompt・同一本文でもPart 3の選定対象が生成ごとに変わり、「物語解釈に寄る揺れがある」(FABLE_EVAL_02.md:10)。foolish↔wisest も「説明は物語解釈寄りで語法の深掘りは薄い」(同:7)。
3. **Key Phrase/Wordとの重複回避が設計に無い**: Trial-04のPart 3はPart 1/2との重複回避を指示するだけで(`PROMPT_04.md` Part 3ブロック、EVAL_04.md:73)、Key Phrase・Word(HR確定)を入力せず、焦点での重複判定もない。今回の必須条件(承認原文§2-B)に対し、重複検査工程が未整備。

(Trial-04 出力例: `take that number on its own`(ig_nobel r1)や `only half her attention`(open_window r1)は KP/Word 級の句の語義説明に近く、今回の「KP/Wordと焦点が別」条件に照らすと境界。)

## 2. 改良Prompt v1 / v2 と重複検査Prompt

方針(v1): 日本語解説、英語表現+本文逐語引用+和訳、焦点を1行(`focus`)で明示、KP/Word(5件)を入力して生成時に差別化を指示、「選ばないもの」を列挙、手順は内部思考のみ(1回生成・2段階生成にしない=Fable評価の推奨に整合)、候補なし可、解説長さ=120〜260字(Part 1の1項目相当: AI島 carry over の公開解説は約200字)。

v2 は v1 の分析(§5)を受けた1回限りの改良: 学習価値4条件(文脈性/日本語話者の落とし穴/レベル適合/非重複)、A2既習の基礎文法対比の除外、Part 1(KP)・Part 2(文法)との役割分担の明記、入れ替えテスト、`criteria_check` 出力、`mid`は候補にしない。

### 2-1. Prompt v1 全文(sha256={SHA_V1})

```text
{PROMPT_V1}
```

### 2-2. Prompt v2 全文(sha256={SHA_V2})

```text
{PROMPT_V2}
```

### 2-3. 重複検査

- 段1(構造・決定論): 候補`expression`(`A vs B`は各側に分割)とKP/Wordの`key_phrase`・本文中の形の内容語(軽動詞・冠詞等を除き簡易語幹化)を比較し、一方が他方の部分集合なら一致=fail(`structural_check`、`tools/nuance_trial_01.py`)。
- 段2(LLM・理由付き): 下のPromptでKP/Word全件についてsame_focusを判定(承認原文§2-Bの規則をそのままPromptに記載)。モデル=gpt-6-luna(生成と同一モデル=自己判定のバイアスの可能性あり)。
- 追加(決定論): 引用`quote_en`が本文に逐語で実在するか。
- 最終判定: 段1 fail または 段2 fail または 引用不一致 のいずれかでfail(Q優先の保守側)。

判定Prompt(sha256={SHA_J}):

```text
{PROMPT_J}
```

## 3. 対象記事と入力(KP/Word)

| 対象 | 本文 | KP/Word(各レベル最大5件) | 状態 |
|---|---|---|---|
{TARGET_ROWS}

注: Paycheckの公開KPは、HR form導入前に公開された確定KP(公開済みページのKey Phrase行)で、`confirmed_selection.json`は存在しない。Yは公開前(ユーザー最終試聴待ち)の既存完成run(KPはHR確定済み)。本文はAI島=公開済み(Local Rewrite適用後)、告げ口心臓=公開済みページの`Full Story`行を連結、Y=`parts.json`の`y_segment_order`連結。

## 4. 結果表

### 4-1. v1(gpt-6-luna、各1回、retryなし)

{TABLE_V1}

### 4-2. v2(同一対象への再生成は各1回のみ)

{TABLE_V2}

モデル自己評価とworker所見は別: worker所見(Sonnet)は、引用・日本語の正確性(誤りなし)に加え、「日本語話者が取り違えやすいか」「そのレベルの学習者に基礎すぎないか」「KP/Wordコーナーの内容と入れ替えて違和感がないか」で判断した主観評価であり、Production基準ではない(HRまたはFableの評価に置き換わる)。

### 4-3. 重複検査 段2の感度確認(人工候補。実生成物ではない)

{PROBE_TABLE}

## 5. 分析

### 5-1. 0件が妥当なケース
- 平易文・基礎語中心でKP/Word以外に文脈固有の含みが無い場合: 人工control(「A Quiet Morning」)でv2=0件(v1は `stood vs stood up` を強制選定)。実記事ではv2 Paycheck Adv(基礎的な法助動詞/記事理解寄りの候補しか無い)が妥当な0件。
- KP級の定型句や、KP/Wordと語・論点が近い表現しか残らない場合(v2 paycheck_std の `was linked to`↔`weak link` は、0件扱いで破棄)。
- 0件率の目安: v2 実8中 0件3+重複破棄1=HR提示可4(50%)。仕様上0件は正常(承認原文§2-A-6)。

### 5-2. 重複しがちなパターン
1. **KP級の定型句を候補にする**: v2 y_redelivery_adv の `I guess it can't be helped` は同記事StdのKey Phrase。同レベル内ではKP/Wordと非重複だが、HRがKPに選び得る粒度の句。Yのような口語意見記事で起きやすい(v1/v2のy_std生成時には `can't be helped` を自ら `kp_word_overlap` で除外)。
2. **同一語彙の別側面**: v2 paycheck_std `was linked to` vs KP `weak link`(段1が検出、段2は別焦点と判断)。語は同じ`link`で、論点(関連≠因果 / 関連の弱さ)が隣接する境界事例。
3. **類義語比較・同じ比喩の別表現**: 段1では検出不能(人工probe 2/2が段1 pass、段2 fail)。実生成物には出なかった(生成時の差別化指示が効いた)。
4. 文法コーナー(Part 2)との境界: `I'd be happy if`(仮定法)・`You should have seen`(modal perfect)・`must have`は文法解説と隣接。v2でも同一表現がStdでは採用、Advでは `grammar_structure` として除外と判断が割れた(告げ口心臓)。

### 5-3. Part 1「類義語との違い」観点との役割分担
- 公開済みPart 1(Vocabulary & Expressions)の解説は、意味・よく使う組み合わせ・近い表現との違いを含む(例: AI島 `card to play` ↔ `a card up one's sleeve`、公開ページ`family_x_ai_island_form_01/index.html`のstudy section)。ニュアンス解説がKP/Word本体の類義語比較をすると、Part 1と実質重複する。
- v2は「KP/Word本体の語義補足・類義語比較の禁止」と入れ替えテストを明記。生成物にはKP本体の類義語比較は出なかった(v1でも0)。役割分担は「ニュアンス解説=KP/Word以外の語・表現の語感/含み/文脈差」で運用可能と判断。
- Part 2(文法)の確定内容(`confirmed_selection.json` の`grammar`)はこのTrialでは入力していない(AI島a2・告げ口心臓a2は0件、Y b1b は1件)。Production配線時は、確定済み文法項目も入力に渡して重複回避させる案(設計側=01aで検討)。

### 5-4. 弱点
1. **自己評価が識別しない**: v1 high 7/8(`don't have to vs mustn't` も high)。v2は4条件の`criteria_check`で根拠が具体化し、`mid`以下は0件にしたことで基礎対比は消えたが、同一モデルの自己申告に過ぎない。ゲートに使えるのは重複検査(段2)であり、学習価値はHR/Fable評価が必要。
2. **v2の過剰抑制・Std/Adv不整合**(N=1): AI島Stdで `at least` を too_basic として0件。同記事Advでは同表現を採用。レベル別の基準(Standardでの `too_basic` の線引き)が曖昧。同一標本の再生成を1回に制限したため、揺れの大きさ(再現率)は未測定。
3. **段1の限界と段1/段2の不一致**: 段1は人工重複を検出できず、実生成物では偽陽性(境界)1件。段1 failを自動破棄とするとQ優先(安全側)だが、有用候補を失い得る。
4. **単価**: 推論tokenにより想定の約3倍(それでも70円目標の約0.5%)。judge callは候補ありの時のみ。
5. **同一モデルでの生成と判定**: 段2の自己判定バイアスの可能性。probeでは感度を確認したが、微妙な境界事例の網羅は未確認。

### 5-5. 次の一手の候補(Fable向け。実行・採用判断はFable)
- A: v2をベースに、レベル別基準(Standardでは `at least` のような頻出機能語の含みを許す/Advancedは基礎文法の対比のみ除外)を1文足して、Production設計(01a)へ渡す。追加Trialは、Production runtime(実HRフロー)で複数記事を見てから行う案。改善見込み=Std/Adv不整合の低減(中)。
- B: 段1は「failなら破棄」ではなく「flag→段2へヒント付きで再確認」とし、最終判定はQ優先(いずれかfailで破棄)を維持するか、構造hitのみの偽陽性を許容するかは設計判断(承認原文§2-B「HR提示前に原則として品質確認」の範囲内でB=承認範囲内)。
- C: Part 2の確定文法項目を入力に加える(隣接領域の回避)。

## 6. 候補本文(全文)と重複検査結果

{CANDIDATES}

## 7. 費用(円@160。呼出ごとの記録=`usage_log_01.jsonl`)

{COST_TABLE}

合計 ¥{TOTAL} / 上限 ¥10。内訳: v1実8 ¥{C_V1}、v1 control ¥{C_V1C}、v2実8 ¥{C_V2}、v2 control ¥{C_V2C}、judge probe ¥{C_PR}。呼出数{NCALL}、全call `status=completed`、`model_actual=gpt-6-luna`、retryなし、エラー0。

## 8. 成果物・再現
- 本書、`prompt_trial_01.json`(スキーマ: `WIRING_DESIGN_01.md` §3 `nuance_candidate_v1` に準拠。追加フィールドは`trial_extra`のみ=`rejected_candidates`/`worker_value_assessment`/`model_self_rating`/`criteria_check`/`quote_verbatim`/`rejected_candidate_audit`)、`results_v1.json`/`results_v1_control.json`/`results_v2.json`/`judge_probe_01.json`(生出力・usage全文)、`raw/`(各callの原文)、`usage_log_01.jsonl`、`stop_check_01b*.json`。
- script: `tools/nuance_trial_01.py`(対象読込・Prompt v1・重複検査・費用ガード)、`tools/nuance_prompt_v2.py`、`tools/build_report_01.py`、`tools/assemble_md_01.py`。
- 実行: `py -3 nuance_trial_01.py dry-run`(API 0)、`NUANCE_TRIAL_PAID=1 py -3 nuance_trial_01.py gen v1|v2 [target...]`。Production・Prompt・既存出力は未変更。

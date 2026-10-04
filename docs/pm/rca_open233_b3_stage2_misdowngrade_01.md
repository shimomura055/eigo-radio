# RCA: rep25 B3 s1「重大→問題なし」誤降格の構造的根本原因分析(OPEN-233-KPI-RECOVERY-REDESIGN-02 委任_01 Step 1)

管理ID: `OPEN-233-KPI-RECOVERY-REDESIGN-02`(親`OPEN-233-SELF-RECOVERY-TRIAL-01`)。費用: ¥0(既存instance JSONの走査・prompt復元のみ。API呼び出しなし)。性質: 診断。Production未変更。`APPROVED_FOR_PRODUCTION`ではない。
再現スクリプト(全て`er052_output/open233_kpi_recovery_02_offline_01/`): `reconstruct_b3_prompt_01.py`(prompt復元)、`rca_scan_01.py`(全MAJOR 1143件の走査、`rca_major_rows_01.json`)、`rca_reasoning_01.py`(reasoning集計、`rca_reasoning_01.md`)。
凡例: 「確認」=実データ・コードから直接確認できたこと、「推測」=データから導いた仮説。

## 0. 結論(先に要点)

「同じ入力を10回回して10/10 BLOCKING」(委任_67)は、1回の流出を**説明していない**。今回の流出を成立させた構造は次の5点。

1. 判定役(Stage 2)は、Checkerが何を指摘したか(issue・flag)を**一切知らされず**、13,000字超のrubricの中から問題を自力で再発見しなければならない(確認)。
2. Stage 2が「問題なし(ACCEPTABLE)」を返すために必要な**根拠(Evidence)が一つも要らない**。`basis=none`・`rewrite_hint=""`で通る。実績でACCEPTABLE降格227件中184件(81%)が`basis=none`(確認)。
3. promptの中に**ACCEPTABLEの定義が2つ**あり、後段(V7)の方が緩い。因果の「付加」を前者(R3: 因果を一切加えない)は排除するが、後者(V7: 新しい具体的事実を加えない)は排除しない(確認)。
4. 降格方向には1回判定しかなく、確認がない。既存2-of-2は逆方向(BLOCKING→降格)専用かつTrial専用NORMAL群のみ(確認)。
5. `changed_causality`は決定論floor(5フラグ)の対象外で、Checkerが因果フラグを立てても、Stage 2の1回判定を覆す仕組みがない(確認)。

加えて、既存ログでは「Stage 2の推論が浅い回に降格が出る」相関が強く出ている(Safety-critical・単独batchで、reasoning<400 tokensは2/3が降格、700以上は1/21。確認した相関、因果は推測)。つまり**単発のLLM判定に重大Safetyの解除権限を無条件に与えている**ことが根本原因で、乱数は引き金にすぎない。

## 1. Stage 2に渡った実際の入力(作業1-1)

復元: `er052_output/open233_kpi_recovery_02_offline_01/b3_stage2_prompt_reconstructed.txt`(developer+user全文、14,514字)。`prompt_sha256=85f6b9852656e40cdcb162ecad45e8b5cf7e92c907c08784e62d672f2d1a3f97`で、rep25 call_log記録値と**一致**(確認、`b3_stage2_prompt_sha.json`)。モデル`gpt-6-luna`、usage: input 8,300 / output 357 / **reasoning 306**(rep25 `bgroup_B3.json` call_log)。

prompt構成(`er052_open233_self_recovery_stage2_production_01.py` 113〜132行`BATCH_PROMPT_TEMPLATE`+`..._calibration_01.py` 649〜689行`run_stage2_batch_variant`):

| 要素 | 内容 | 復元prompt行 |
|---|---|---|
| developer | 「あなたはVerified Fact LedgerとFact Safetyの独立監査担当(Second Judge)です。…Stage 1が既にBLOCKING-candidateとして検出した特定のclaimについて、本当にProductionを止めるべきmaterial errorかを、あなた自身の判断で再評価してください。」 | 2 |
| 前文 | 「Stage 1の判定理由(explanation/severity/10種類のフラグ)はここでは一切提示しません。」 | 5〜9 |
| Ledger全文 | HF-001〜HF-012(うちHF-007、HF-009、HF-011が本件に関係) | 11〜95 |
| 記事 | 記事全文(`source_article_text`。ラベルは「日本語原文」だが実体は英語記事) | 101〜124 |
| claim | `[claim_index=0]`の1件のみ(batch内他claimなし) | 127〜134 |
| rubric | V7b(R3基底+委任_13/27/28/29/31/33の追加明確化+V7の線引き+V7bタイブレーク) | 136〜314 |
| hint指示 | `REWRITE_HINT_INSTRUCTION` | 315〜322 |

claimブロック逐語(復元prompt 127〜134行):

```
[claim_index=0]
claim: Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so the flashy 20% plan left the stage, but the chart only pulled back briefly before recovering.
ローカル文脈(段落±1): ## In one line

Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so the flashy 20% plan left the stage, but the chart only pulled back briefly before recovering: the policy turn and the oil chart's "not over yet" movement happened on the same day.
origin: ja_source
related_fact_id: HF-007
section_type(title/hook/in_one_line/body): body
```

(`section_type`はbody routeで`claim_records_for_stage2`から除かれる設計。runner 2689行〜、該当は2704〜2712行付近。実際はIn one lineセクションだがpromptには`body`と出る。判定には無関係の見込みだが事実として記録。)

Ledger HF-007逐語(復元prompt 55〜60行): `[VERIFIED] HF-007: トランプ大統領は7月14日午前11時4分（米東部夏時間）、20％の米国償還料を、湾岸諸国による対米貿易・投資案件に置き換えると投稿した。` / `conditions: トランプ氏は、中東指導者との「非常に生産的な協議」に基づく決定だと説明した。`
関連Fact(撤回の理由は協議、懸念の継続は別の事実):
- HF-001(18行) notes_for_writer: 「この決議と7月14日の発言撤回との因果関係は一次資料で確認できない。撤回の原因として記述しない。」
- HF-009 conditions: 「撤回発表以外にも、米・イラン間の攻撃、海上封鎖、タンカー安全上の懸念が継続していた。」
- HF-011 conditions: 「20％償還料案は同日の取引時間中に撤回されたが、…供給懸念は継続していた。」/ notes_for_writer: 「これだけから撤回が価格を上昇させた、または下落させなかったと因果推論しない。」

## 2. Checkerの指摘のうちStage 2に渡った情報/渡らなかった情報(作業1-2)

rep25 `bgroup_B3.json` `cycles[0].stage2_results[0].dev`(逐語):

| 項目 | Checker出力 | Stage 2 promptに |
|---|---|---|
| severity | `MAJOR` | **含まれない**(前文で「提示しません」) |
| issue | 「継続していた攻撃・封鎖・タンカー安全への懸念が、20％案の撤回・置換や価格回復の原因だったかのように読める。Ledgerは、撤回・置換の理由としてトランプ氏が『非常に生産的な協議』を挙げたことと、供給懸念が継続していたことを確認しているが、両者の因果関係は確認していない。」 | **含まれない** |
| explanation | 「同日に生じた政策転換と市場の値動き、および継続する懸念を、接続語『so』により因果関係として結び付けている。」 | **含まれない** |
| flags | `changed_causality=true`、他9種false | **含まれない** |
| related_fact_id | HF-007 | 含まれる |
| origin | ja_source | 含まれる |
| claim_in_article | claim文と同一 | claim文として含まれる |

つまりStage 2が知るのは「この文はStage 1の重大候補」という事実のみで、**何が問題とされたか(因果の付加)は知らされない**(確認)。Opus#10の観察(issue・devフラグはStage 2に渡っていない、calibration 649〜671行)は正しい。ただし、これはprimingを避けるための意図的設計(旧ユーザー指示・Opus#8: Stage 1の理由を見せると独立性が失われる)であり、副作用として「判定役が問題点を再発見する負担」を負う。

付記(確認): rep25 B3 s1のStage 1は、V4A単発が非検出(recall miss)となり、実Production V0 baselineのMAJOR deviationへ**代替投入**された(`stage1_recall_miss_substituted=true`、runner 6703〜6720行)。「Checkerは重大違反を検出できていた」は、この代替投入(baseline検出)を含む。Stage 1自体のrecall不足は別問題(§6、第二段階)。

## 3. Ledger・記事本文・context(作業1-3)

記事「In one line」(復元prompt 122〜124行)がそのままclaimの文脈。本文の他の箇所は因果を書いていない: 「About 24 hours and 48 minutes later, at 11:04 a.m. on July 14, Trump said the 20% plan would be replaced ... He cited 'very productive discussions' with Middle Eastern leaders.」(112行付近)。つまり**本文の本論は協議を理由としているのに、In one lineだけが「so」で懸念の継続を撤回の理由と読める**。ローカル文脈(段落±1)はIn one line段落のみで、本論の文は渡らないが、Ledger HF-007 conditionsが同じ内容を持つため、情報としては足りていた(確認)。

## 4. 後段Prompt(V7b)とmateriality基準(作業1-4)

V7b本文はcalibration 551〜614行(定数`MISCONCEPTION_PRINCIPLE_TEXT_V7B`)+基底`RUBRIC_R3_TRIPLE_PRIME`。復元promptのrubric部は136〜314行(約180行)。

確認できた構造上の問題:

1. **ACCEPTABLEの定義が2つ**ある。
   - 160〜163行(R3基底): 「ACCEPTABLE: Ledgerに無い新規の固有名詞・数値・時期・主体・因果・仕組みを一切加えず…一般常識レベルの背景説明・条件付きの一般論にとどまる。」→ 因果の新規追加を**排除**する。
   - 285〜286行(V7): 「ACCEPTABLE(問題なし): 確認済みFactから自然に導ける描写・推論で、新しい具体的事実を加えないもの。」→ 因果の付加は「新しい具体的事実」(人物・出来事・発言・数値、V7(1)(イ))に該当しないため**排除されない**。しかもV7は「V4の条件付き→断定…および『迷う場合』の扱いより優先」と書かれ(279〜281行)、優先関係が曖昧。
   - 因果の付加(`so`)は新しい人物・数値・出来事を加えないため、V7の文面では「自然な推論」と読める余地が実際に残っている(推測。ただしrep25の1回がそう読んだ可能性は高い。basis=noneで理由は残っていない)。
2. **B3そのものの対処例がpromptに入っている**(委任_33、256〜278行の「継続していた安全保障上の懸念が原因で撤回された」を明確にBLOCKINGとする例)。それでも1回外れた(確認)。つまり「promptに規則がない」ことが原因ではなく、**長い多層rubricの中で規則が確実には適用されない**ことが原因。rubricは8層のパッチ(R3→R3'''→重大誤解原則→委任_27/28/29/31/33→V7→V7b)で、冒頭は「自然な解釈はOK」(136〜141行)、後半は「必ずBLOCKING」と、方向の異なる指示が積み重なる。
3. 同rubricの冒頭`tie-break`(R3 163〜170行)は「迷えばQUALITY」、V7(3)(297〜300行)は「重大な誤解につながるか」。判断の最終基準が複数ある。
4. QUALITYは**「Rewriteはしない、通過させる」**と明記(R3 150行付近)。つまり重大→軽微(QUALITY)でもRewriteされず流出する。過去の流出9件のうち8件はQUALITYだった(§6)。「軽微なら安全」ではない。

## 5. deterministic safety ruleとの関係(作業1-5)

- floor 5フラグ: `changed_actor`/`changed_number`/`changed_negation`/`changed_comparison`/`changed_time`(runner 552〜557行`FLOOR_FLAGS`)。いずれかがtrueなら無条件BLOCKING(`apply_floor`、1930〜1941行)。**`changed_causality`は対象外**。本件`changed_causality=true`以外は全てfalseなので、floorは発火しない(確認、`floor_reason=null`)。
- 対象外になった経緯(確認): floorの5項目は「ユーザーNG列挙(actor/number/negation/comparison/time)」に対応(runner 545〜551行コメント。`changed_certainty`も委任_12で外した)。`design_checker_redesign_v02_01.md` §6-1は「`changed_causality=true`単独では自動BLOCKINGにしない」とし、causality-only MAJOR 4件(B3が2件)で機械ルールが誤緩和/誤昇格の両方を起こすと評価した。`DECISION_LOG.md`6154〜6159行も、5フラグを「常に厳格」とする箇所は`changed_causality`版が正と整理している(付記)。**過去の判断は「因果の字面判定は過剰Major・不要Rewriteを増やす」であり、「因果は重大でない」ではない**。
- precheck floor(`detected_by=="precheck"`、`apply_floor`1931行): LLM Stage 1ではなく決定論検出のclaimのみ。本件は`stage1_llm`。
- hook/disclosure_gap降格(2153、2210行): BLOCKINGを**下げる**側。本件は無関係(`floor_reason=null`、`stage2_route=body`)。
- 既存2-of-2(2918〜2960行): 1回目BLOCKING→2回目で降格を許す逆方向。しかも`NORMAL_GROUP_INSTANCE_IDS`(評価用の正解ラベル付きinstance)限定でProductionに概念がない。B3は`bgroup_B3`でNORMAL群外。「降格を確認する」仕組みは存在しない(確認)。

## 6. 過去の同経路流出(作業1-6)

最終materialityが非BLOCKINGで合格系になった同経路の流出を全ログから再走査(`rca_scan_01.py`)。Safety-critical定義(runner 7438〜7470行)に一致するclaimのうち、最終非BLOCKINGは**10行**(委任_67の9件+rep24 cycle 2の1件。後者はRewrite後本文の「and」版でRESOLVED_REWRITE_THEN_DOWNGRADE)。

| # | ディレクトリ | claim | cycle | rubric | llm判定 | basis | hint | 因果以外のflag | reasoning | batch内MAJOR数 | 終状態 | Stage 1の経路 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1〜4 | rep7(同一run内4件) | B3 | 1 | R3''' | QUALITY | unsupported_relationship | 空 | `changed_causality`のみ | 記録なし | 1 | RESOLVED_STAGE2_DOWNGRADE | 代替投入 |
| 5 | iter8 | B3 | 1 | V5 | QUALITY | unsupported_relationship | 空 | fact・causality・unsupported_new_claim | 958 | 1 | 同上 | Stage 1 fresh(V4A検出) |
| 6 | iter8 | B3 | 1 | V5 | QUALITY | unsupported_relationship | 空 | 同上 | 434 | 1 | 同上 | Stage 1 reuse |
| 7・8 | iter8 | A2A3-0 | 1 | V5 | QUALITY | ledger_conditions | 空 | fact・certainty・unsupported_new_claim | 3145 | 5 | 同上 | reuse |
| 9 | **rep25** | **B3** | 1 | **V7b** | **ACCEPTABLE** | **none** | 空 | **`changed_causality`のみ** | **306** | 1 | 同上 | 代替投入 |
| (10) | rep24 | B3 | 2(Rewrite後「and」版) | V7b | ACCEPTABLE | none | 空 | fact・causality・unsupported_new_claim | 259 | 1 | RESOLVED_REWRITE_THEN_DOWNGRADE | 代替投入 |

(rep7の4件・iter8のA2A3の2件は同一run内の重複判定か別instance JSONかを個別に区別していない。件数は委任_67集計と同じ。)

共通点(確認):
1. claim型: 全件が**因果の付加または条件・確実性の強化**(B3=「so」で懸念継続を撤回理由へ、A2A3=Ledgerが「未提示」の支払い主体・返済を断定)。数値・主体の置換ではなく、決定論floor(5フラグ)の外。
2. Stage 2入力: B3は全て**batch内単独1件**。A2A3は5件batch。batch内の位置・数は原因ではない。
3. basis: 8/10がQUALITY+basis非none(`unsupported_relationship`等)、rep25とrep24 cycle 2のみACCEPTABLE+`none`。**basisが付いていても流出した**ので、basis非none要求だけでは防げない(委任_68と同じ結論)。
4. rewrite_hint: 全件空(BLOCKINGでないため、定義上空)。
5. reasoning tokens: 判明している5件は434・958・3145(A2A3の5 batch)・306・259。同sub_id・同batchサイズのBLOCKING回(B3: n=21、最小628、中央値1120)より低い(§7)。
6. rubric版: R3'''/V5/V7b。是正(委任_33のB3例示追加、V6、V7b)後も、rubric版を変えるたびに新しい形で再発(R3''' 4/26→V5 2/2→V7b 1/3)。**rubricの個別パッチは再発を止めていない**(確認)。
7. cycle: 9件はcycle 1(Rewriteされる前)。
8. Stage 1経路: 代替投入(recall missをbaselineで埋めた)が5〜6件、fresh/reuseが3〜4件。流出の経路(Stage 2降格)は経路によらない。

## 7. 1回だけ誤判定した理由: 乱数か設計か(作業1-7)

reasoning tokensの観察を既存ログ全体で検証した(全MAJOR claim 1143件、うちreasoning記録あり677件、`rca_reasoning_01.md`):

| 集合 | reasoning<400 | 400〜700 | 700〜1200 | 1200以上 |
|---|---|---|---|---|
| 全MAJOR(batch単位) | 84/119=71%が非BLOCKING | 53/81=65% | 41/89=46% | 212/388=55% |
| batch内MAJOR=1件のみ | 39/74=53% | 15/40=38% | 5/38=13% | 2/18=11% |
| V7b・単独batch | 17/23=74% | 3/9=33% | 0/3 | - |
| **Safety-critical・単独batch** | **2/3=67%** | **1/5=20%** | **1/13=8%** | **0/8=0%** |

確認できたこと:
- 単独batch(claimごとの推論量に近い)では、**reasoningが少ない回ほど降格しやすい**(53%→38%→13%→11%)。Safety-criticalでも同じ向き(67%→20%→8%→0%)。
- Safety-critical単独batchの降格4件のreasoning(259/306/434/958)は、同sub_id・同batchサイズのBLOCKING回(n=21、最小628)の下位または下に位置する(例外は958のiter8 1件で、BLOCKING回の最小628と中央値1120の間)。
- 全MAJOR(多claim batch)では相関が弱い(batch全体のreasoningはclaim数に比例するため)。

注意(推測・限界): (i)reasoning量は「簡単だと判断したから短い」の結果でもあり、「浅く考えたから間違えた」という因果とは区別できない。(ii)Safety-critical単独batch降格はn=4で少数。(iii)reasoning tokensはStage 2の呼び出し後にしか分からないが、**呼び出し後・¥0・決定論の観測量**であり、Guardの補助信号にはなり得る(設計書で扱う)。

結論: 乱数的揺らぎ(同一入力のreasoning量・判断の分かれ)が**引き金**だが、揺らぎが「流出」まで通る**権限構造の弱点**(無条件の解除権限、根拠不要、1回判定、因果が決定論外、rubric内の緩いACCEPTABLE定義)が根本原因。「10/10 BLOCKING」と「1回流出」は矛盾せず、1回あたりの確率pが小さくても、**解除に根拠が要らない構造ではpがそのまま見逃し率になる**。

## 8. なぜ「重大→軽微」ではなく「重大→問題なし」まで落ちたか(作業1-8)

- schema(`er052_open233_self_recovery_stage2_production_01.py` 134〜183行`_ITEM_PROPS`/`BATCH_JSON_SCHEMA`): `materiality ∈ {BLOCKING, QUALITY, ACCEPTABLE}`、`basis ∈ {ledger_claim, ..., unsupported_relationship, none}`、`rewrite_kind`、`rewrite_hint`の4項目。**ACCEPTABLEだけ追加の必須項目がない**。Ledger逐語引用欄も、Checker指摘への反論欄もない。
- 実データ: Stage 2降格534件のうちACCEPTABLE 227件、うち`basis=none` 184件(81%)。V7bのllm_direct降格では、ACCEPTABLE 69件のうち65件(94%)が`basis=none`(`recount_01.md`)。つまり正当なACCEPTABLEは通常根拠を残さない設計で、**「根拠のないACCEPTABLE」と「根拠を省略した誤ACCEPTABLE」が区別できない**。
- ACCEPTABLEとQUALITYの境界はrubricの文章のみ(V7: ACCEPTABLE=新しい具体的事実を加えない描写、QUALITY=核心は保たれるが精度が落ちる)。因果の付加を「描写」と読むか「精度の低下」と読むかは判定者次第で、**1段の差**にすぎない。
- Checkerの重大判定を打ち消すためのEvidence要件(例: Checkerが指摘した点を否定するLedger逐語引用)は存在しない。判定役はCheckerの指摘を知らないため、**反論そのものが構造上不可能**(Checkerを読まずに反論はできない)。

## 9. 解除の現在の条件(作業1-9)

一文: **「Stage 2が1回、任意のbasis(none含む)・任意のrewrite_hint(空)で、materialityにQUALITYまたはACCEPTABLEを返し、かつ数値・主体・否定・比較・時期のfloorフラグが立っていなければ、Checkerの重大判定(MAJOR)は解除される」**。

評価(妥当でない):
1. Checkerの根拠に反論する必要がない(無条件)。
2. 解除側の根拠(Ledger引用)を検証しない。
3. 判定が1回で、確認がない。
4. 因果・確実性・条件付き→断定・Ledgerが未提示とする主体の特定は、floorでも保護されない。
5. 一方、この権限が価値を生んでいる面もある: rep24ではMAJOR 102件中68件がStage 2で降格し、多くは正当(不要Rewrite防止)。したがって**権限を奪う(MAJORを降格不可にする)のではなく、「根拠なしには解除できない」構造へ直す**必要がある。

## 10. 構造上の欠陥の列挙(作業1-10)

| ID | 欠陥 | 根拠(確認) |
|---|---|---|
| (a) | 判定役がCheckerの指摘(issue/flag)を知らず、再発見を要求される。反論が構造上不可能 | §2。前文「一切提示しません」 |
| (b) | 解除にEvidence要件がない(`basis=none`・hint空で通る) | §8。ACCEPTABLE降格のbasis=none 81%、V7b llm_direct 94% |
| (c) | ACCEPTABLEに追加要件がなく、promptに緩い定義(V7)と厳しい定義(R3)が併存 | §4。160行と285行 |
| (d) | 降格方向は1回判定、確認なし。既存2-of-2は逆方向・Trial専用 | §5 |
| (e) | 因果・確実性・Ledger未提示の主体がdeterministic floorの外。floorはStage 1のLLMフラグに依存 | §5 |
| (f) | rubricが8層のパッチで長く(約180行)、個別パッチで再発を止められていない(R3'''→V5→V7b) | §4、§6 |
| (g) | QUALITYも「Rewriteなし通過」であり、軽微への降格も流出になる(流出10件中8件がQUALITY) | §4、§6 |
| (h) | 確率pの小さい誤判定が、(b)(c)(d)のためそのまま見逃し率になる。reasoning量が少ない回で降格しやすい相関 | §7 |
| (i) | (参考、別問題)B3 rep25のStage 1はrecall missで代替投入。Stage 1のrecall不足は別途 | §2付記 |

## 11. 次工程への含意(設計は設計書§2〜§4)

- (b)(c)(a)に対する解は「解除に、Ledger逐語引用とCheckerの指摘への反証を必須化し、決定論でLedger照合する」方向(設計書§2のA-1)。
- (e)に対する決定論Guardは、Checkerのissue/flag(因果等を名指し)と、Ledger fact本文との逐語照合で、**因果語のあるclaimだけ**を対象にすれば、過去の「因果の字面判定は不要Rewriteが増える」問題(neg5型)を避けられる可能性がある。これは¥0 replayで定量する(設計書§3〜§4)。
- (g)はA-1(iv)「Major→Minorは反証不要」案の欠陥を示す: QUALITYも流出なので、Minorへの降格にも根拠が要る。設計書で取り込む。
- Stage 1 recall(i)は第二段階(設計書§6)。

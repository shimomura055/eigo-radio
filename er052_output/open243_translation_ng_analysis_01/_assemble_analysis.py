# assemble ANALYSIS_01.md from narrative + generated table fragments (read-only on artifacts). run from repo root after _build/_stats/_report_tables.
OUT = 'er052_output/open243_translation_ng_analysis_01'
rd = lambda n: open(f'{OUT}/{n}', encoding='utf8').read()
NONJA, JA, DEV, PEND = rd('_frag_nonja.md'), rd('_frag_ja.md'), rd('_frag_dev.md'), rd('_frag_pending.md')

TXT = r'''# ANALYSIS_01: 日本語→英語化(EN化)段で生じる軽微・重大NGの発生パターン解析

管理ID: OPEN-243-TRANSLATION-NG-ANALYSIS-01 委任_01 / 日付 2026-10-08 / Status: ANALYZED(既存artifactのみ・API支出 ¥0・SSOT/Production無変更)
関連: `COUNTERMEASURES_01.md`(対策案)、`items.jsonl`(全件の機械可読。1行=盲検判定1件、`event_id`で同一文を束ねる)。再現用: `_build.py`/`_stats.py`/`_report_tables.py`/`_assemble_analysis.py`(同ディレクトリ)。

## 0. 要旨(先に結論)

1. **EN段に所在する盲検NGは、判定66件(Trial A 28件・Trial B 38件)、同一文を束ねた「事象」53件**。内訳は 翻訳段由来22・翻訳で増幅4・JA由来27(判定: 手動。表2-1/2-2)。重大は判定4件(事象4件)で、うち翻訳段由来2(EV-25「Meta was asked」、EV-28「callers」)、JA由来2。
2. **翻訳段由来/増幅の26事象(うち重大2)には、はっきりした偏りがある**(n=26、小標本):
   - **箇所**: 末尾「In one line」要約 9事象 / 本文 17事象。**文あたりの発生率は要約 9/59行(15%) vs 本文 17/1,505文(1.1%) = 約13倍**(要約は台帳にも日本語原文にも照合されない文)。
   - **型**: 数(単複)8、主体7、因果3、付け足し3、範囲2、断定の強さ1、時制1、訳語選択1。JA由来27事象の型(範囲11・付け足し11・因果3・断定の強さ2)とは分布が違う。
   - **言語構造**: 本文17事象のうち8事象が「**日本語の数無標**」(「幹部」→executives 5、「米政府機関」→agencies 2、「従業員」→employees 1)。JAが「副社長」と具体的に書いた9記事ではENの誤りは0、「幹部」と書いた9記事のうち6記事(67%)でENが複数形(executives等)になった(表3-2)。
3. **EN deviation check(Advanced/Standardの事後検査)の translation 起源指摘は48レコード(35件・箇所別: 要約22件/本文13件)。MAJORはほぼ要約文**(attempt1でMAJOR 24世代中、要約14・本文10)。本文のMAJOR 10/10は must-fix 再生成で解消したが、**要約のMAJOR 14世代のうち8世代(57%)は再生成でも解消せずSTOP**(EN STOP 8世代は全て要約文の範囲/因果。うち7世代はMeta「ロールバック対象」の範囲)。O3観測(本日 run_01 STOP)も同型(要約の「AI phone feature」範囲)。
4. **検出状況(翻訳段由来/増幅26事象)**: EN deviation checkが指摘したのは5事象(19%、全てMINOR、MAJOR指摘0)。うち3事象は「幹部→executives」で origin が `ja_source` と判定された(日本語が単複無標のため、JA由来か翻訳由来かをLLMが一貫して判定できない)。Checkerは、データのある24事象のうち候補化14(58%)、Stage 2がBLOCKINGにして書き換えたのは4事象(うち2事象[EV-26, EV-28]は一次ACCEPTABLEを第2意見が割ってBLOCKINGにした=第2意見は救済側に働いた)。**EN deviation checkもCheckerも候補化しなかった事象が10/24(42%)**。重大2件は、EV-28がCheckerのみで除去、**EV-25(Meta was asked)はEN deviation check=MINOR(changed_number)・Checker=QUALITY(別事実の理由)で素通り**。
5. **偏りが見えない/見えにくい軸**: モデル世代(gpt-5.6-luna 記事あたり0.52事象 vs gpt-6-luna 0.38。ただしFact Lock cellを除くと gpt-6 0.61 vs 5.6 0.52 でFact Lock cellが交絡)、Standard(A2)はn=3世代でn不足。テーマはMetaが多い(0.72/記事 vs ホルムズ0.40・宇宙兵器0.24)が、Meta台帳(MUSE-HC-012「幹部」等)が型に当てはまりやすいためで、n不足。
6. **盲検判定の再現性が低い**: Trial AとBで同じ38記事を別の評価者が採点し、共通38記事の翻訳段由来/増幅22事象のうち両試験が拾ったのは6件(27%)。**ここで数えた件数は下限値**で、実際の翻訳段NGは少なくともこれより多い可能性が高い(Lincoln-Petersen 参考値 約32事象/38記事。独立性が成り立たない可能性があり確度は低い)。

## 1. データ源・手順・制約

- **盲検採点**: `er052_output/all6_writer_redesign_necessity_01/eval/judgments/*.json`(38記事)と `er052_output/factlock_writer_trial_01/eval/judgments/*.json`(72記事。うちEN本文が存在するのは59記事)を、各 `eval/_private/MAP.json` で記事に解決。Trial BのbaselineとAll6は Trial A と同一の run を別評価者が再採点したもの(`MAP.json`のrun_dir一致38件)。EN本文が存在する一意の記事は59本(baseline 21、all6 19、factlock 19)。ENに出現するNGの母集団は、判定の `in_en=true`(EN_ONLY / JA+EN)。保留(pending)は所在フラグを持たず本統計に算入しない(EN関連の保留8件は別掲、表2-5)。
- **突合**: 各判定について `ja_writer/revision2.md`(JA R2)と `b1b/article.md`(EN。Family X忠実英訳+独立生成の「In one line」)を読み、JA対応文を手動で特定して「翻訳段由来 / JA由来 / 翻訳で増幅」を判定(判定: 手動。根拠は `items.jsonl` の `ja_r2_corresponding` と `judgment_basis`)。盲検判定者が `in_r2=true` としたものも、JA R2に同文があることを原文確認した。
- **検出状況**: EN deviation check = `b1b/audit/deviation_check.json` と `deviation_checks/advanced_attempt*.json`、Checker = `checker/runs/*.json`(stage1 union_candidates / cycles[].stage2_results / en_text_after_rewrite)。文の突合はJaccard類似度による自動照合(閾値0.5)で、Checkerの「最終文除去/改変」は書き換え後本文に当該文が完全一致しないことで判定。
- **制約**: (1)盲検判定は1記事1評価者(LLM)で人間確認は重大候補2件のみ(ユーザー判定: EV-25=重大、EV-39=軽微)。(2)Trial A/Bで同一記事の判定が割れる(EV-39は A=軽微 / B=重大、ユーザー判定は軽微)。(3)STOPしたrunはEN本文が無く判定対象外(下記3-4: 要約の翻訳MAJORが最も多くSTOPしている=生存者バイアスで要約NGは過小に見える)。(4)Standard(A2)の盲検NGはTrial A/Bに無い(EN本文はb1bのみ)。

## 2. EN段NGの全件収集

### 2-1. 件数(盲検判定ベース、出典: 上記judgments + MAP)

| 区分 | Trial A | Trial B | 計 |
|---|---|---|---|
| EN所在の盲検NG判定(重大/軽微) | 28(重大2/軽微26) | 38(重大2/軽微36) | 66 |
| うち EN_ONLY(R0/R2に無くENだけ) | 11(重大1/軽微10) | 16(重大1/軽微15) | 27 |
| うち JA+EN(R2にも存在) | 17(重大1/軽微16) | 22(重大1/軽微21) | 39 |
| 事象(同一run・同一EN文を束ねる) | 53(翻訳段由来22 / 翻訳で増幅4 / JA由来27) | | |
| 保留(参考。算入しない)のうちEN関連 | 8件(表2-5) | | |

Trial AのSUMMARY_TA(EN 重大2・軽微26)と一致する(`SUMMARY_TA.md` §2-1、baseline 重大1+軽微14、all6 重大1+軽微12)。

### 2-2. 翻訳段由来・翻訳で増幅 26事象(全件。本タスクの主対象)

起源の判定は手動。「JA R2対応文」はJA R2本文からの引用、「EN文」は`b1b/article.md`からの引用。EN deviation check欄は当該EN文に対応する指摘(最終deviation_check.json優先、無ければattempt)、Checker欄は`checker/runs/*.json`上の候補化と最終文の扱い。

{NONJA}

読み方の注: 「翻訳で増幅」はJA側にも曖昧さがあり、ENで一方の読みに固定されて意味が強まったもの。EV-10(Trial Aは「ENのみ」、Trial Bは「R0+EN」と判定)のようにR0/R2の扱いが判定者で割れるものは、R2とENの本文を読み直して判定した。

### 2-3. JA由来の27事象(参考。EN側では訳が忠実で、JA R2の段階で既に存在)

{JA}

### 2-4. EN deviation check の `origin == "translation"` 指摘 全件(48レコード)

対象: `er052_output/all6_writer_redesign_necessity_01`、`er052_output/factlock_writer_trial_01`(sweep_01含む)、`er052_output/gpt6_wiring_e2e_01`、`er019_output`。収集ファイル: `**/b1b/audit/deviation_check.json`・`**/a2/audit/deviation_check.json`・`**/audit/deviation_checks/advanced_*.json`・`standard_*.json`(計270ファイル、うち deviation を含むもの全て走査)。種別 attempt=再生成前後の各attempt、final=最終`deviation_check.json`(STOP時は最後のattemptと同内容の重複を含む)。同一世代・同一文の重複を除くと35件。

{DEV}

集計(origin別、全79 deviation): translation 48(attempt 37 + final 11)、ja_source 28(attempt 20 + final 8)、originフィールド無し3(旧スキーマの`family_x_b3_diversity_trial_01`)。translation 48のseverity×箇所: MAJOR/要約 attempt 23 + final 8、MAJOR/本文 attempt 11、MINOR/本文 attempt 2 + final 2、MINOR/要約 attempt 1 + final 1(`_stats.json`)。attempt1の translation 起源指摘の`changed_*`フラグ(延べ、MAJOR/MINOR含む): scope 要約10・本文2、fact 要約6・本文7、unsupported_new_claim 要約5・本文6、certainty 要約2・本文5、causality 要約2・本文1。**`changed_actor`がtrueになった指摘は全79件中12件で、12件とも origin=`ja_source`(「幹部→executives」型)、translation 起源は0件**。`changed_number`がtrueの指摘は全79件中2件のみ(EV-25の「employees reported」。attemptとfinalの重複)。changed_actorは「発言主体・調査主体のすり替え」と定義されている(4節)。

### 2-5. 保留(参考)のうちEN関連 8件(統計には算入しない)

{PEND}

### 2-6. Checkerゴールドセット(T-B)と OPEN-233 REPORT の過去のEN重大事例(JAに無くENで生じたもの)

出典: `er052_output/all6_writer_redesign_necessity_01/T-B/TB_SUMMARY.md`・`T-B/items.json`、`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md` §95-5(L5374-5376)・§97-5(L5436)。ゴールドセット重大7件のうち **EN段起点(JAは正しい/ENのみ)は2件**:

| 項目 | 型 | 内容(出典の引用) | JAの対応(判定: 手動) | Checker検出(MAJORを当該文に対応づけられた試行/反復) |
|---|---|---|---|---|
| PAST-ai-p2r1-02 | 主体(入替) | EN「whether it tends to be used for harmful purposes」(items.json: JAは正しい) | JA R2「有害な目的で使う傾向があるか」は主語省略。ENは受動(it ... be used)へ固定=主語省略の誤補完 | gpt-5.6-luna 0/2、gpt-6-luna 2/2 |
| PAST-hormuz-T0M0r2-01 | 範囲(20%の対象) | EN「the United States would seek payment equal to 20 percent of the cost of providing safety and security」(REPORT §97-5: JAは正しい) | JA R2「安全と警備を提供する費用として、二十パーセントの償還を求める」は基準を明記しない(台帳は貨物への20%)。ENが「費用の20%」と補完 | 両モデルとも当該文に対応づけた検出 0/4(記事内に別箇所のMAJORが出たのは4/4) |

ほか、ゴールドセットの他5件(PAST-meta-p2r2-02、PAST-ai-p2r1-01、PAST-sw-p2r2-01/-02、PAST-jb9k-03)はJA R2起点(items.json `stage`=R2/R0->R2)。REPORT §95-5は meta-p2r2-02 を「ENで開示対象を取り違え」と記すが、T-B items の対象はJA R2文であり、EN段単独起点とは判定しない。T-B全体の検出率(重大): 5.6 1/14(7%)、6 4/14(29%)(`TB_SUMMARY.md` §1)。

### 2-7. O3観測(本日 Production E2E run_01/run_02)のSTOP内容

出典: `er052_output/gpt6_wiring_e2e_01/E2E_EVIDENCE.md`、`run_01/b1b/audit/deviation_checks/advanced_attempt1.json`・`advanced_attempt2.json`、`run_02/b1b/audit/deviation_check.json`。

- run_01(STOP): Advanced deviation checkが2回連続 MAJOR/origin=translation/`changed_scope`/related_fact_id=MUSE-HC-07。attempt1 EN文=`"Meta paused its AI phone assistant test"`(「## In one line」の1文)、attempt2=`"In one line: Meta paused its AI phone feature after some calls were handled by human contractors without a clear explanation."`。いずれも「人間担当者が関与する電話機能の当面のロールバック」を「AI電話機能(のテスト)全体の停止」へ広げたと指摘。**JA R2(`run_01/ja_writer/revision2.md`)に要約文は無く、本文は「機能を当面ロールバックした」「人間に引き継ぐ仕組みのテスト」と書いている**。「In one line」は日本語に対応文が無い、EN側で新規に生成された文(判定: 手動)。
- run_02: `b1b`・`a2`のdeviation_check.json とも deviation 0件(LEDGER_COMPLIANT)で完走(O3は STOP 1/2本)。

## 3. パターン解析

### 3-1. 型 x 箇所(翻訳段由来22+翻訳で増幅4 = 26事象。判定: 手動)

| 型 | 本文 | 末尾要約 | タイトル | 計 | (参考)JA由来27事象の型 |
|---|---|---|---|---|---|
| 数(単複・人数) | 8 | 0 | 0 | 8 | 0 |
| 主体(入替・受動化・方向) | 6 | 1 | 0 | 7 | 0 |
| 因果 | 0 | 3 | 0 | 3 | 3 |
| 付け足し(要約文・一般化) | 0 | 3 | 0 | 3 | 11 |
| 範囲(限定/拡大) | 1 | 1 | 0 | 2 | 11 |
| 否定・断定の強さ | 0 | 1 | 0 | 1 | 2 |
| 時制 | 1 | 0 | 0 | 1 | 0 |
| 訳語選択・指示対象 | 1 | 0 | 0 | 1 | 0 |
| 計 | 17 | 9 | 0 | 26 | 27 |

- タイトル由来の盲検NGは0件(保留に「AI Phone-Answering Service」と「The Star」の2件のみ、表2-5。n不足)。Standard(A2)由来の盲検NGは0件(EN本文はAdvanced b1bのみ評価。n不足)。
- **翻訳段は「数」と「主体」(計15/26=58%)、要約は「因果・付け足し・範囲・強さ」(8/9)に集中**し、JA由来は「範囲・付け足し」(22/27)に集中する。JA側に有効な対策(Fact Lock等)は後者を狙っており、前者(数・主体)は構造上届かない(`RESIDUAL_NG_VS_CHECK.md`の「ENのみ3件」と整合: そのうち2件が数、1件が要約)。

### 3-2. 言語構造の要因(判定: 手動)

| 要因 | 事象数 | 事象 | 根拠(原文確認) |
|---|---|---|---|
| 日本語の数無標(単複区別なし)+役職・組織の集合名詞化 | 8 | 「幹部」→executives 5(EV-23/26/30/50/52)、「米政府機関」→agencies 2(EV-32/35)、「従業員」→employees 1(EV-17) | 「Metaの幹部は…認めた」。台帳は副社長1名。JAが「副社長」と書いた9記事は全て "vice president"(誤り0)、「幹部」と書いた9記事は6記事が複数形(67%)、3記事が単数(`ja_writer/revision2.md`と`b1b/article.md`の文字列照合: 本分析で集計)。「米政府機関」は9記事中2記事(22%)が複数形 |
| 主語省略(認めた/頼んだの主体) | 2 | EV-25(Meta was asked)、EV-45(anyone) | 「インターネットとケーブル料金の交渉を頼んだ一件では」(依頼者省略)→ "in one case in which Meta was asked"。同一JA構文でも run により "a user asked Muse"(b4 baseline r1)と訳が割れる |
| 「AとBの攻撃」の所有格/関係の曖昧さ | 3(増幅) | EV-02/06/48(米国とイランの攻撃) | 台帳は「米・イラン間の攻撃」。EN "attacks by the United States and Iran" は実行主体化 |
| 係り受け・修飾範囲(並列の「対米」) | 1(増幅) | EV-10 | 「湾岸諸国との対米貿易や投資の案件」→ "trade with the United States and investment with Gulf countries" と誤分割 |
| 語義の反転(受け手 vs かけ手) | 1 | EV-28(callers) | JA「電話の相手」(受け手)→EN要約 "callers"(かける側) |
| 訳語の選択で主体・指示対象が消える | 2 | EV-01("involving"で「湾岸諸国による」が消える)、EV-18(「電話機能」→"the feature"で直前の human concierge feature と取り違え得る) | 同左 |
| 時制マーカー | 1 | EV-38 | 「超えました」(過去の結果)→ "There are now more than 1,500" |
| **要約文の新規生成(日本語に対応文無し)** | 9(EV-28は語義反転の行と重複計上。全体は26事象) | EV-04/07/08/14/19/28/31/42/51 | 「In one line」は日本語本文に無く、別callで英語記事だけから生成(4節)。台帳にもJAにも照合されない。「12-18語」指定で修飾語(human concierge等)が落ちる傾向 |

### 3-3. 重大度(盲検判定 / ユーザー判定)

- 翻訳段由来/増幅 26事象: 重大2(EV-25: 盲検=重大・ユーザー判定=重大、EV-28: 盲検=重大・ユーザー未確認)、軽微24。EV-25とEV-28はどちらも **主体/対象の取り違え**(型: 主体)。軽微の主体は数(単複)が中心。
- JA由来 27事象: 重大2(EV-22: 「電話機能は…公開する方針です」が電話機能全体と読める=盲検重大、EV-39: 「配備が確認された」=A軽微/B重大/ユーザー軽微)、軽微25。
- したがって **重大2件は両方とも「主体(誰が/誰に)」で、軽微の数(単複)・要約の因果と区別される**(n=2のため傾向とは断定しない)。

### 3-4. 検出状況

| 項目 | 翻訳段由来/増幅 26事象 | JA由来 27事象 |
|---|---|---|
| EN deviation check が当該文を指摘 | 5(19%): 全てMINOR。origin=translation 2(EV-25, EV-42)・ja_source 3(EV-23/26/30。「幹部」) | 1 |
| 〃 MAJOR指摘 | 0 | 0 |
| Checkerデータあり | 24(2事象はEN本文後の予算STOPでChecker未実行) | 27 |
| Checkerが候補化(Stage 1 → Stage 2) | 14(58%) | 17(63%) |
| 〃 Stage 2が BLOCKING → 書き換え | 4(EV-14, EV-42は一次BLOCKING。EV-26, EV-28は一次ACCEPTABLE→第2意見が割れてBLOCKING) | 2(EV-12は一次QUALITY→第2意見split、EV-36は一次BLOCKING) |
| 〃 QUALITYのまま残存 | 2(EV-25, EV-31) | (表2-3) |
| 〃 ACCEPTABLE(格下げ/通過)のまま残存 | 8 | (表2-3) |
| EN deviation checkもChecker候補化もなし | 10/24(42%) | |

- **要約文の事象(9)**: EN deviation checkが指摘したのはEV-42の1件(MINOR)のみ(要約MAJORは生成時の検査で多数捕捉されて再生成されるため、最終本文に生き残った9事象は検査をすり抜けた分)。Checkerは9事象中8事象を候補化(EV-07のみ候補化なし)し、BLOCKING 3(EV-14, EV-28, EV-42)を書き換え。
- **数(単複)の事象(8)**: EN deviation checkは「幹部→executives」3事象を MINOR(changed_actor、origin=ja_source)で指摘。他の数5事象(機関×2・従業員・幹部2)は指摘なし。Checkerは「幹部」の5事象(EV-23/26/30/50/52)全てを候補化したが、書き換えたのは1事象(EV-26。Stage 2の一次判定は`ACCEPTABLE`、第2意見が割れてBLOCKING)で、同型の他4事象は`ACCEPTABLE`のまま通過(同一型の扱いが一貫しない)。
- **EN段の生成時検査(重大な補足)**: translation 起源 MAJOR は、attempt1で24世代に発生(要約14・本文10)。must-fix再生成で解消したのは16世代(本文10/10、要約6/14)、STOPは8世代(全て要約)。EN STOPの主因は要約文であり、最終本文に残る要約NGは「STOPしなかった分の下限」である。
- 重大2件: EV-28=EN deviation check指摘なし・Checker BLOCKINGで除去(Checkerの救済)、EV-25=EN deviation check MINOR(changed_number)・Checker `QUALITY`(Stage 1は別事実HC-010を理由に候補化、Stage 2一次QUALITY → 第2意見ACCEPTABLE → `RESOLVED_REWRITE_THEN_DOWNGRADE`、当該文は出力に残存。`b3__baseline__r1/checker/runs/meta_run03_advanced.json`)=2層とも素通り。

### 3-5. モデル世代・cell・テーマ(記事あたり事象数。n小、交絡あり)

| 軸 | 値 | 事象/記事 |
|---|---|---|
| EN生成モデル(Advanced stage、raw_usage_log) | gpt-5.6-luna | 11/21 = 0.52 |
| | gpt-6-luna(全体) | 14/37 = 0.38 |
| | gpt-6-luna(Fact Lock cellを除く) | 11/18 = 0.61 |
| | 混在 | 1/1 |
| cell | baseline | 11/21 = 0.52 |
| | all6 | 11/19 = 0.58 |
| | factlock(全てgpt-6-luna) | 4/19 = 0.21 |
| テーマ | meta | 13/18 = 0.72 |
| | hormuz | 8/20 = 0.40 |
| | space_weapons | 5/21 = 0.24 |

- **モデル世代の差は見えない**(Fact Lock cellを除けば gpt-6 0.61 vs 5.6 0.52)。n不足。
- Fact Lock cellが低い(0.21)。ただしFact Lockは24run中5runがEN STOP(うち4runが要約の翻訳MAJOR)で記事数が19本に減っており、STOPによる選別を含む。Fact Lockが翻訳段に効くという根拠にはならない(EN文は同じ`generate_family_x_faithful_translation`を通る)。
- テーマ差(Meta 0.72): Meta台帳は「幹部/副社長」「従業員」「ロールバック対象」など単複・範囲の型に当てはまる事実が多い。テーマ固有の傾向と断定せず、n不足。
- 評価者別(5.6/6): 翻訳起源 事象を拾った判定は A: 5.6=7・6=5、B: 5.6=9・6=11(判定件数)。偏りは見えない。

### 3-6. 傾向の有無(結論と確度)

| 観察 | 件数の偏り | 確度 |
|---|---|---|
| 要約文は文あたりの翻訳段NGが本文の約13倍(15% vs 1.1%) | 9/59 vs 17/1,505 | 中(分母は記事数と文数。判定者1人・STOPによる過小あり) |
| EN STOPは要約が原因(8/8)、要約MAJORの再生成成功率は6/14(本文は10/10) | 8世代 | 中(世代数が小さい。7/8がMeta「ロールバック対象」の同一事実) |
| 「数無標の集合名詞(幹部・機関・従業員)」は複数化されやすい | 幹部 6/9記事、機関 2/9記事、副社長 0/9 | 中(n=9、記事は同一テーマ・同一台帳の繰り返し) |
| 翻訳段の重大(2件)は主体/対象の取り違え | 2/2 | 低(n=2) |
| EN deviation check/Checkerは数・主体型を取りこぼす(候補化なし10/24、MAJOR指摘0/26) | 26事象 | 中 |
| モデル世代・Standard(A2)・タイトル | - | n不足 |
| 判定者間の一致 | 共通38記事の翻訳段由来/増幅22事象中 両試験で重複 6(27%) | 参考(件数は下限) |

## 4. EN化プロンプト・検査の現状確認(Grep/Read、変更なし)

**4-1. EN化の経路(Family X Production経路。Trial A/B・E2Eが使う `er012_e_family_entertainment_two_level_runner_01._run_writer_stage_once`、L358-)**
- 翻訳: `er003_v1_n3_01_advanced_adaptation_generate.generate_family_x_faithful_translation(ja_text)`(L621)。プロンプト=`FAMILY_X_FAITHFUL_TRANSLATION_INSTRUCTION`(L526-)+語彙ルールv2+`[Japanese article]`+JA本文。**入力は日本語本文のみで、台帳(Verified Fact Ledger)は渡さない**。主体・数の保持を明示した指示は無い(「Do not add new ideas, claims... Do not remove any fact, claim, or causal link」「Keep the same order... same number of paragraphs」まで)。「Do not add a concluding one-line summary; that is handled separately by another step」と明記。
- 「In one line」: `generate_family_x_in_one_line(client, title, body)`(L699-)が**別callで生成**。プロンプト(L552-575)=「Write ONE short, natural sentence that captures the core of the story」「focus on the single most important point」「Do not add any new fact, conclusion, or lesson not already stated」「roughly 12-18 words」+英語記事(title+body)。**入力は英語記事のみ。日本語原文も台帳も渡さない**。日本語本文に要約文は存在しない(JAの`## In one line`相当は無い)。
- 旧経路(`generate_advanced_adaptation`、`build_prompt` L343)は`ADVANCED_CONTRACT_SUFFIX`が「final section headed exactly "## In one line" containing one sentence」を要求するが、同じく台帳を渡さない(入力=JA本文+must_fixのみ)。Family X Productionはこの旧経路を使わない(L370-380の注記)。
- Standard(A2): `generate_family_x_standard_a2_no_heading(advanced_text, ...)`(`er003_v1_n3_01_standard_a2_generate.py` L541)。**入力は英語Advanced本文**(日本語・台帳なし)で、Advancedの誤りを継承する経路。EN本文のStandard(A2)盲検NGはTrial A/Bに無くn不足。

**4-2. EN deviation check(`er003_v1_en_direct_vfl_01_generate.run_deviation_check`、L777-)**
- プロンプト`DEVIATION_PROMPT_TEMPLATE`(L505-)=台帳+記事。判定対象は10フラグ: changed_fact / changed_scope / changed_causality / changed_certainty / changed_number / changed_actor / changed_negation / changed_comparison / changed_time / unsupported_new_claim。**`changed_actor`の定義は「発言主体・調査主体をLedgerと異なる人物・組織にすり替えている」(L521)であり、依頼主体・行為主体の入替や受け手/かけ手の取り違えは定義外**(EV-25が`changed_number`だけでMINORになった直接要因。EV-25の指摘文は「employees reported と複数」=数の観点のみ)。`changed_number`は「数値・割合・件数」(L520)で単複を含み得る(EV-17等の数無標を拾う余地はあるが、実績では「幹部」を`changed_actor`で拾い、他は拾っていない)。
- 「MAJOR=上記10種のいずれかが明確にtrueの場合のみ」「迷う場合は記事の主張がLedgerとほぼ同じ意味を保っているか」「厳密な文言一致は求めません」(L541-549)。10フラグ全てfalseのMAJORはMINORへ自動降格(`_apply_deviation_post_hoc_validation`)。
- origin判定(`ORIGIN_INSTRUCTION_TEMPLATE`、L672-): `source_article_text`(JA R2)を渡し「ja_source: 原文記事の時点で既にこの逸脱に相当する内容が存在していた / translation: 原文記事では問題なく、翻訳・適応の過程で新たに生じた」を**LLMへの追加質問として判定させる(決定論ではない)**。「幹部→executives」は日本語が数無標のためja_source(3事象)にもtranslation扱い(Trial A/Bの手動判定では翻訳段)にもなり得る。
- 呼び出し側の分岐(`er012_e_family_entertainment_two_level_runner_01._run_writer_stage_once` L358-、検査呼び出し L399-): MAJORが1件でも `origin=="ja_source"` → `JARecheckRequiredError`(JA再確認STOP)。ja_source無し → must-fix(MAJORのみ)で**EN翻訳を**再生成し、続けてIn one lineを再生成。ただし **`generate_family_x_in_one_line(client, title, body)` は `must_fix` 引数を持たず、要約の再生成はMAJOR指摘の内容を受け取らない**(関数シグネチャ L699、呼び出し L388/L391/L424)。再検査でMAJOR残存/前回指摘の未解消 → STOP。要約のMAJOR再生成が6/14しか解消しない(3-4)ことと整合する(因果は未検証)。 → 再検査でMAJOR残存/前回指摘の未解消 → STOP。**MINOR(translation起源)は再生成・修正の対象外で、そのまま採用**(EV-25の素通りの経路)。

**4-3. Checker Stage 2 の second opinion(`er052_open233_self_recovery_flow_runner_01.py`)**
- `apply_stage2_second_opinion`(L4324-)は、対象=「Checker MAJOR ∧ Stage 2一次の最終materialityが非BLOCKING ∧ floor_verify解放済みでない ∧ precheckでない」(`stage2_second_opinion_eligible` L4241-)のclaim。**第2意見は降格を確定させる条件を厳しくする方向(二回とも非BLOCKINGなら重い方を採用、割れたらBLOCKING)**で、設計意図は安全側(L4225-4235)。主体・否定・因果で第2意見を不可にする分岐はなく、`materiality`(BLOCKING/QUALITY/ACCEPTABLE)はStage 2のLLM rubric判定。
- 床規則(deterministic floor): 既定(legacy_5flags、`FLOOR_FLAGS` L841-)ではStage 1のdevで`changed_actor/number/negation/comparison/time`がtrueならBLOCKINGへ昇格する。**ただしユーザー承認済みの承認構成`OPEN233_APPROVED_FLOW_SWITCHES`(L500、OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01、2026-10-06)は `FLOOR_MODE="number_only"`(床の発火集合は`changed_number`のみ。「数字以外の機械的強制重大化の廃止」)**で、主体・否定・比較・時期の床は無い。Trial A/Bのchecker実行は`switches_equal_e2e02=True`でdumpに`CAUSAL_FLOOR`/`FLOOR_VERIFY_MODE`が現れない(承認構成の値False/offと整合)が、`FLOOR_MODE`自体はdumpに出力されないため、number_onlyで動いたことは直接には確認していない(未確認)。**EV-25でこの安全装置が働かなかったのは、Stage 1が当該文を別事実(related_fact_id=MUSE-HC-010、決定論検査`negation_polarity_mismatch`)の理由で候補化し、changed_actor等のフラグが立たなかったため**(`checker/runs/meta_run03_advanced.json` cycle1 stage2_results: materiality=QUALITY、llm_materiality=QUALITY、`floor_reason`=None、第2意見 ACCEPTABLE)。つまり「第2意見が主体型を格下げした」のではなく、**Stage 1が当該文の本当の欠陥(依頼者の取り違え)を課題として立てず、別の理由のclaimとして評価されたこと**が素通りの直接要因。実際、第2意見はEV-26(executives)・EV-28(callers)では一次ACCEPTABLEを割ってBLOCKINGにしており、救済側に働いている。
- 実装上の補足: Checkerは`b1b/article.md`(EN deviation check通過後)を入力とし、書き換えは`checker/runs/*.json`内の`en_text_after_rewrite`に残る。盲検採点はこの書き換え前の`b1b/article.md`を評価している。

## 5. 未確認事項・限界

- 本分析は盲検判定が拾った分のみ。判定者間の一致が27%と低く、実際の翻訳段NG発生率は不明(未測定)。全文を対象にしたJA↔EN文対応の全数突合は行っていない。
- 「数」型の8事象は、台帳が単数(副社長1名)であることを前提にNG判定されている。台帳が複数と明記する事実(例: 複数の従業員)での複数形は正しい。
- Checker候補化の文突合はJaccard自動照合(閾値0.5)で、要約文など短文では取りこぼし・過剰突合があり得る。EV単位で`items.jsonl`の`checker`欄を確認できる。
- 要約文の「生成時の検査での捕捉」はEN STOPと再生成の記録(`deviation_checks/advanced_attempt*.json`)から集計した。STOPで本文が存在しないrunは盲検判定の対象外。
- EV-10/EV-02/EV-06/EV-48(米国とイランの攻撃、貿易・投資の係り受け)を「翻訳で増幅」とした判定は、JA側にも曖昧さがあるため境界事例(判定: 手動)。
- 保留8件のうちEV対象外のもの(表2-5)はJA対応文の突合を簡易にとどめた(#67 "commonly called the Space Treaty" 等)。
'''

txt = TXT.replace('{NONJA}', NONJA).replace('{JA}', JA).replace('{DEV}', DEV).replace('{PEND}', PEND)
open(f'{OUT}/ANALYSIS_01.md', 'w', encoding='utf8').write(txt)
print(len(txt))

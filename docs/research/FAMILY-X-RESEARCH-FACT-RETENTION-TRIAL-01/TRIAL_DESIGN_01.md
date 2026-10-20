# TRIAL_DESIGN_01: Family X Researcher Fact保持 比較Trial 事前登録設計

- 管理ID: FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01 委任_01(2026-10-20)。Trial全体の到達上限=`VALIDATED`(Production採用はユーザーのみ、`VALIDATED`でも自動配線しない)。本委任の到達上限=`XRFR_DESIGN_HARNESS_READY_BASELINE_REPRODUCED_PENDING_FABLE`。
- ユーザー原文: `docs/pm/delegation_log/2026-10-20_FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01_USER.md`(3198文字、sha256 `3314feb62662510c3133a757374388941d455eeedae8b0568995bfb92d60c2b7`)。
- **事前登録**: 本書・`gold_01.json`・`design_matrix_01.json`・`sources_spec_01.json`・harness(`er085_research_fact_retention_trial_01_*.py`)は①現行再現の実走前にcommitする。実走結果を見て指標・閾値・gold・方式文面を変更しない(変更が必要なら新版を起こし、理由と変更前後を記録する)。
- 構成ファイル: `sources_spec_01.json`(出典と切出し規則)/`gold_01.json`(正解集合・採点regex・創作watch)/`design_matrix_01.json`(方式・費用)/`adjudication_01.json`(創作候補の出典照合結果、実走後に記入)。

## §0 要約(最も推奨する方向の事前仮説)

- 根本原因(XRG 委任_01): 出典に明示された主体`Ansar Allah`と紅海/Bab al-Mandab文脈が、Researcherのclaim化で受動形になり脱落し、検証は正しさのみで省略を検知しない。仕様の空白(Researcher/検証Promptに帰属・文脈保持観点が無い)。
- **コスト構造の発見(本委任の実測、設計の前提)**: `run_mey_01`のResearch+Ledger検証=JPY36.1/記事のうち、web_search 20回分(研究15+検証5)×USD0.01×160=**JPY32.0が検索料(約89%)**で、LLM token代は約JPY4。検索なしの抽出呼出はJPY約1。したがって、Promptやschemaの変更(追加検索ゼロ)は恒常費用への影響が小さく、**最大の費用リスクは『Prompt変更が検索回数を増やすこと』**。この点は検索なしharnessでは測れないため、S-check(§7)で候補に限り確認する。
- 事前仮説(結果で書き換えない): 追加LLM呼出ゼロの方式(A/B/C/D)の中に、保持率を明確に改善し創作0・不要Fact増≤2で、恒常費用+JPY0.5以下に収まるものがある可能性がある。方式Eは追加LLM呼出1回(約JPY0.7)の費用対効果対照。

## §1 工程分解(W1、関数:行、JPY0)

| 工程 | 実装(関数:行) | 1 LLM呼出か | モデル/Prompt/schema | 費用記録 |
|---|---|---|---|---|
| (a)検索 + (b)抽出・構造化 | `er019_family_x_entertainment_production_runner_01.py::run_research_and_ledger`:97-146 → `er012_e_family_entertainment_two_level_runner_01.py::run_researcher_for_topic`:183-203 → `client.responses.create(model=vfl01.MODEL, reasoning={"effort": vfl01.REASONING_EFFORT}, tools=[{"type":"web_search"}], text={"format":{"type":"json_schema", **vfl01.FACT_LEDGER_JSON_SCHEMA}}, input=[developer, user])` | **検索と抽出は1回のResponses呼出に統合**(web_search toolをモデルが自律で複数回呼ぶ。runから分離不可) | `gpt-6-luna`(vfl01:MODEL=routing.WRITER_MODEL、effort=high)。Prompt=`vfl01.RESEARCHER_PROMPT_TEMPLATE`(`er003_v1_en_direct_vfl_01_generate.py`:137-170)、構造化観点4つ=同156-162。出力schema=`FACT_LEDGER_JSON_SCHEMA`(同82-126、claim/subject/date_or_period/scope/conditions/numeric_value/numeric_scope/causal_strength/source_title/source_url/source_type/support_level/ambiguity/notes_for_writer、`additionalProperties:false`、**actor/帰属欄なし**) | `cl.logging_context(RUNNER_TAG="NEWS_FAMILY_X_B3_PRODUCTION_RUNNER_01", "research")`(runner:107)。run_mey_01実測 `raw_usage_log.jsonl` stage=research: in119,459/out13,549(推論8,685)/web_search_call_count=15/158.9s=JPY26.995 |
| (c)検証 | `run_verification_for_topic`(efam:206-)。入力=Researcher下書きJSON(Ledger自身のsource_url)+topic。**出典本文は再取得しない**: 検証モデルがweb_searchで独立再検索する(Prompt「Ledger自身のsource_urlだけを鵜呑みにせず独立してWeb検索により再照合」、vfl01:228-250、観点237-246) | 検索込み1呼出 | 同`gpt-6-luna`、`VERIFICATION_JSON_SCHEMA`(fact_id/verdict[VERIFIED|AMBIGUOUS|REJECTED]/verification_notes) | stage=`ledger`(runner:116): in50,685/out3,737/web_search=5/37.9s=JPY9.110 |
| (d)Ledger生成 | `vfl01.build_verified_ledger_text`(vfl01:279-310)。REJECTEDを除外し、`[VERIFIED]`/`[AMBIGUOUS - …]`タグ+claim/scope/conditions/numeric/date/causal_strength/(AMBIGUOUS時のみ`ambiguity_note`)/notes_for_writerを出力。runner:122-125が`verified_fact_ledger.txt`・`verdict_counts.json`・`fact_ledger_draft.json`(VERIFIED前の下書き)を保存 | LLM 0 | – | – |
| (e)B3への受け渡し | `run_storyline_b3`(runner:147-)が`verified_fact_ledger.txt`の全文をB3 promptへ入力。fact_idは`b3.extract_fact_ids_from_ledger`、下限2件は`verified_fact_ids`で算定(`er019_family_x_storyline_b3_fact_selection_01.py`:172-184) | B3=`gpt-6.1-sol` 1呼出(+下限2再評価時1) | – | stage=`storyline_b3`(JPY約7.6/呼出) |

**重要な事実(設計に効く)**:
1. rendered Ledgerは`source_url`/`source_title`を**出力しない**(B3が見る情報はclaim・scope・conditions・numeric・date・causal_strength・[AMBIGUOUS時のみ]ambiguity_note・notes_for_writer)。出典情報は`fact_ledger_draft.json`にのみ残る。よって保持の評価は「rendered Ledgerの単一Factブロック」で行う(B3視点)。
2. `VERIFIED` Factの`verification_notes`はrendered Ledgerに出ない(AMBIGUOUS時のみ、かつ`ambiguity`が空の場合のみ`verification_notes`が`ambiguity_note`として出る)。→ 検証側だけの改善(方式C)がLedgerへ届く経路は『AMBIGUOUS化』に限られる。この制約を方式Cの評価にそのまま含める(成果の過大評価を避ける)。
3. Researcherが見た・見なかった出典の記録は無い(出典一覧ファイル無し、棄却候補の記録機構も無し)。→ 厳密な再現には出典セットの固定が必要=本Trialの出典packet。

### 注入点の有無と Production同等性の限界(W1重要事項)
- **出典本文を与えてclaim化だけを走らせる関数/Prompt分割はProductionに存在しない**(上記(a)は検索+抽出が不可分、`run_researcher_for_topic`は`tools=web_search`固定でtopic文字列しか受け取らない)。
- よってTrial harnessは、**Production Prompt本文を`vfl01`から直接importし**(複製ではなく参照)、(r1)冒頭文「Webで調査し」を「末尾の【取得済み出典】に同梱されたテキストだけを根拠に…Web検索は行えません」へ置換、(r2)末尾に出典ブロックを追加、の2点だけを変えて**検索toolなし**で呼ぶ。検証も(v1)「独立してWeb検索により再照合」→同梱出典のみ、(v2)出典ブロック追加、の2点のみ。差分は`er085_..._test_01.py::test_e0_prompts_equal_production_except_declared_diffs`で固定。
- **同等性の限界(結果の解釈に必ず付す)**: (1)Productionはモデルが検索で断片を拾うため、出典全文が与えられる本harnessよりも欠落しやすい可能性(=①で脱落が再現しない可能性がある。その場合は事実として報告し、都合の良い解釈をしない) (2)観点2の文言「より明確な一次Sourceを追加で検索する」は検索なしでは実行不能だが、全方式で同一文言のまま残す(比較の公平性を優先) (3)Productionの検索行動(回数・どの頁を引くか)は測れない→**S-check**(§7) (4)出典本文はHTMLからのテキスト化+本文切出しで、Productionが見る断片とは形が異なる (5)中東packetは、Ledger引用11件のうち本文取得できた6件(JS描画ページ・403・UN News補助頁は除外)。
- 本harnessで『方式間の差』を測れるのは「同一出典を与えた時の抽出・構造化・検証の振る舞いの差」であり、「Production全工程での最終的な保持率」ではない。

## §2 題材と出典packet(W2)

- 出典はすべて無料HTTPで取得(API 0)。切出し規則・URL・取得時刻・sha256は`sources_spec_01.json`と`er085_output/.../sources_manifest_01.json`。出典本文は著作権配慮のため**repoへcommitしない**(`er085_output/.../sources/`はuntracked。gold引用の逐語性はtestで機械検証、出典が無い環境ではskip)。
- **mey(主比較条件)**: S1=国連DPPA 10/9(UN News再掲)、S2=国連特使声明 10/11、S3=GACA続報(SPA/OANA)10/11、S4=SABA(マリブ)10/15、S5=アデン治安局(アラビア語)10/16、S6=オカーズ(エネルギー省発表、アラビア語+英訳)10/14。計7,160文字。除外: SPA(JS描画で本文なし)、AP(403)、UN News補助頁(Ledger未引用)。
- **muse(一般化・正例)**: Reuters via CNA 2026-09-23「Meta testing a 'human concierge' for Muse」4,953文字。**選定規則**(`gold_01.json::selection_rule_generalization`): (1)出典URLが既存ER記録にあり無料で本文再取得可能 (2)主体/背景がテーマ理解に必要 (3)中東と異なる分野 (4)構造の異なる対照を含める。`er019_output`の既存テーマのうち、hormuz系・semiconductor系は主要出典がHTTP 403(investing.com/AP/BLS)で除外、coffeeはICO報告のみ取得可。Museの`MUSE-HC`LedgerはResearcher出力ではない手作りLedgerだが、出典URL(CNA)は取得でき、**主体(Meta/契約スタッフ)・理由(成功率95-98%、広報の目的説明)・背景(公開直後、プライバシー懸念、VM訴求)が明示される**ため、保持評価に適する(Researcher再生成の比較であり、手作りLedgerとの比較ではない)。
- **coffee(一般化・陰性寄り対照)**: ICO Coffee Market Report 2026年9月(価格要因節まで、8,021文字)。主体が薄く数値と『要因の帰属(ICO/CONAB/NOAA)』が主の機関報告。**創作誘発への耐性**(関税・為替・投機筋など出典にない要因を足さないか)を見る。

### gold(正解集合)の定義(詳細は`gold_01.json`、逐語引用付き)

| topic | KEY(主指標) | SEC(副) | CTRL(回帰対照) |
|---|---|---|---|
| mey | M-A1 主体(特使声明10/11: 攻撃主体=Ansar Allah)/M-A2 主体(特使10/9)/M-B1 背景(Ansar Allahのモカ・バブ・アル・マンデブ進攻)/M-B2 背景(紅海の商船への脅威)/M-B3 背景(海上交易路・エネルギー市場との絡み)/M-B4 背景(政府の大規模反攻) | M-B5 特使の評価(重大なエスカレーション) | M-C1(GACA 12人/309人)/M-C2(アデン、フーシ派発射2発)/M-C3(マリブ、SABA)/M-C4(アラムコ管理棟) |
| muse | U-A1 Metaが契約スタッフに通話を代行/U-A2 従業員の半数に有効化/U-B1 公開直後/U-B2 プライバシー懸念/U-B3 理由(成功率95-98%)/U-B4 VM訴求との矛盾/U-B6 副社長「ミス」・ロールバック/U-R1 広報の目的説明 | U-B5 「M」の前例/U-B7 人種的言及/U-S1 出典(社内投稿をReuters確認) | U-C1 DL250万 |
| coffee | K-B1 要因(ブラジル収穫・供給)/K-B2 下支え要因/K-B3 CONAB引上げ/K-B4 ICO余剰300万袋/K-B5 NOAA 90%超/K-B6 ICO消費0.8%減 | – | K-C1 I-CIP数値 |

- 『理由(動機)』は出典が明示する場合のみgold化: 中東は出典に動機の明示が**無い**ためgold対象外(むしろ書けば創作)。MuseのU-B3/U-R1、coffeeのK-B1/K-B2は出典が理由/要因を明示している。
- 『出典(情報の出所)』区分は、Ledger本体schemaが`source_title/source_url`欄で持つ既存仕様を維持する。rendered Ledgerには出ないため、gold項目では『誰の発言か』(例: M-A1の特使、U-S1のReuters/社内投稿)を正規表現groupに含めて評価する。
- **不要Factの定義(事前固定)**: Fact数(下書き)の平均がE0より増えた分(Δfacts)。周辺数値の重複Factや同一出典内の言い換え重複を含む。判定基準で+2/topic以内。
- **採点規則**: item_retained = rendered Ledgerの**単一Factブロック**が全regex groupに一致(日英同義語列挙、大文字小文字無視)。主体が別Factにしか無い場合は不保持。draft_retained(下書きFact一致)との差で『抽出での脱落』と『検証/Ledger化での脱落』を診断分離。
- **創作検出(要件③)**: 機械フラグ(`motive_causal_marker`、`causal_stated_by_source`、topic別watch[中東: イラン/連合/米国等/サウジ主体化/動機語、muse: 他社・訴訟、coffee: 関税・為替・投機筋])→ フラグ付きFactを、worker(実行層)が出典逐語と照合し`adjudication_01.json`へ`SUPPORTED(quote)`/`UNSUPPORTED`で記録。**未判定が1件でも残る方式は最終ラベルを出さない**。Fableは`UNSUPPORTED`と判定された件の出典照合を独立に再確認できる(quote記載)。機械フラグに引っかからない創作の見落としリスクは、(i)watch語彙の事前固定、(ii)gold外Factの全件目視(workerが全Factを読み、gold外の主体/動機/因果を探す)で補い、(iii)Fableの独立評価に委ねる(限界として明記)。

## §3 比較方式(E0 + A〜E)

全方式共通: 同一モデル(`gpt-6-luna`、effort high)、同一出典packet、web_search tool**なし**、同一schema検証(Ledger本体schemaへの適合を`validate_ledger_draft`で確認)。25節(最新上位系原則)の例外理由: 目的は『Production Researcher(luna)で効くか』の比較で、本番ラインのモデル選定は別判断。

| 方式 | 変更点(逐語は`lib.py` A_INSERT/B_PROMPT_ADD/VC_LINE) | 追加Web検索 | 追加LLM呼出 | 追加入力token(1記事) | 追加出力token | 恒常費用増(見積) | 時間 |
|---|---|---|---|---|---|---|---|
| E0 | 現行(No-search化の2置換のみ) | 0 | 0 | 0 | 0 | 基準 | 基準 |
| A | Researcher Promptに第5(帰属・行為主体)/第6(直接の文脈)観点を追加(XRG1 §5-3案。『出典が明示していない主体・動機・因果は書かない』を含む) | 0 | 0 | 約+250 | 約+5〜10% | <JPY0.1 | ほぼ同等 |
| B | Trial専用schemaに任意欄`actor`/`context`を追加(`additionalProperties:false`/strict維持)。決定論で`conditions`に`【主体】…`、`notes_for_writer`に`【背景】…`として既存欄へ畳み込み、Ledger本体schemaは不変 | 0 | 0 | 約+200 | 約+5〜10% | <JPY0.1 | ほぼ同等 |
| C | 検証Promptに1行追加(出典内の重要な帰属・文脈の省略検知。省略ありはAMBIGUOUS+notes)。Researcher不変(E0とdraft共有) | 0 | 0 | 約+80 | 約+0〜5% | ~JPY0 | ほぼ同等 |
| D | A+C | 0 | 0 | 約+330 | 約+5〜10% | <JPY0.1 | ほぼ同等 |
| E | E0 draft後に『保持監査』LLM呼出(追加Factを出力)→統合→検証 | 0 | **+1** | 約+7〜14K | 約+1〜6K | **約JPY0.7(70円目標の約1%)** | +20〜40秒 |

- 方式Cの制約: §1の事実2により、Ledgerに出るのは『AMBIGUOUS化された場合のnotes』のみ。VERIFIEDのままではLedgerは変わらない。→ C単独の改善はD(A+C)との差で評価。
- 方式Bの代替『Ledger側schemaへの正式欄追加』はLedger本体仕様の変更(承認済み仕様の変更)であり本Trialの対象外。畳み込み版で既存欄だけで足りるかを見る。
- **単一Promptへの決め打ち禁止(ユーザー§2)への対応**: 指示方法(A)・Fact粒度/構造(B)・検証方式(C/D)・情報保持工程の分離(E)の4軸を同時比較。

## §4 指標と判定基準(事前登録、sample数=各セル2)

指標(すべて機械算出、`er085_..._eval.py`): KEY/SEC/CTRL保持率(rendered Ledger、およびdraft)/欠落診断(抽出で脱落か、検証・Ledger化で脱落か)/Fact数とΔ対E0/創作(UNSUPPORTED件数・UNADJUDICATED件数)/schema適合/LLM呼出数・token・費用(JPY)・時間/web_search_call_count(=0を確認)/B3利用可能性。

**VALIDATED候補の条件(方式Xについて、すべて満たす)**:
- (a) mey KEY保持率(Ledger、n=2×6=12観測)がE0より**+0.25以上**かつ**0.667以上**。
- (b) 一般化(muse、coffee各n=2): KEY保持率が各topicでE0−0.05以上。かつE0のKEY保持が0.9未満のtopicでは+0.15以上の改善(E0が0.9以上のtopicは『非識別』として回帰確認のみ)。
- (c) CTRL保持率が各topicでE0−0.10以上(回帰なし)。
- (d) **創作UNSUPPORTED=0**(全セル)かつ**UNADJUDICATED=0**。
- (e) 不要Fact増: Δfacts ≤ +2.0/topic。
- (f) 追加LLM呼出=0(A/B/C/D)。Eは例外で、『A〜Dの最良に対する追加改善が+0.15以上かつ追加費用≤JPY1/記事』でなければ費用対効果でREJECTED。
- (g) 全cellでschema適合・Ledger解析可能(B3のfact_id抽出とVERIFIED算定が成立)。
- (h) 恒常費用増(Research+検証、検索なし換算)が現行比+JPY0.5以内(A〜D)、かつ候補のS-check(§7)で検索回数が『既存Production記録の範囲(gpt-6-luna研究4〜16回)を超えて増加』しない。

**REJECTED**: (d)で1件でもUNSUPPORTED、または(a)の改善が+0.10未満、または(h)で検索増が確認された方式。
**USER_DECISION_REQUIRED(判断候補)**: (a)〜(g)を満たすが、恒常費用に有意な増(E採用、検索増の疑い)があるか、複数方式が同点で『変更範囲』(新Prompt経路/schema変更)の選択に承認が要る場合。いずれの方式も、Production採用にはResearcher/検証Promptの変更(新仕様)が必要であり、**ユーザー明示承認が必須**。同点時の優先順位: 追加LLM呼出が少ない→変更箇所が少ない(A<C<B<D<E)→費用が小さい。

**①現行再現(本委任)の判定**: E0×2 sample(mey)で、KEY項目(特に主体M-A1/M-A2と背景M-B1〜B4)の脱落が再現するかを事実として記録する。再現しなければ『再現せず』と報告し、条件差(§1の限界(1)〜(5))を分析する。結果に応じて他の指標・閾値は変えない。

## §5 コスト比較(ユーザー§4への対応)

### 5-1 実測根拠(run_mey_01、`raw_usage_log.jsonl`/`cost.json`)
| 工程 | 入力tok | 出力tok | web_search | 時間 | JPY |
|---|---|---|---|---|---|
| Research(検索込み) | 119,459(検索結果由来を含む) | 13,549 | 15 | 158.9s | 26.995 |
| 検証(検索込み) | 50,685 | 3,737 | 5 | 37.9s | 9.110 |
| 計 | | | 20 | 196.8s | 36.105 |
(内訳: 検索料 20×USD0.01×160=JPY32.0、token代 約JPY4。luna単価 in USD0.1/out USD0.5 per 1M、`pricing_snapshot.json`)。記事全体run_mey_01=JPY104.275(Research+Ledgerは約35%)。

### 5-2 Production歴の検索回数(gpt-6-luna Researcher、既存`researcher_full_record.json`)
byd_recall 4/semiconductor 5/gpt6_wiring 5・6/central_bank 8/boredom 9/coffee 11-12/streaming 12/openai_copyright 13/mey 15/inbound_tourism 16。**テーマ間で4〜16回とばらつきが大きい**ため、Prompt変更が検索回数を小さく増やしても少数標本では検出できない(§7 S-checkの検出力の限界)。

### 5-3 Trial費用と恒常費用の区別
- **Trial費用**(開発費、`design_matrix_01.json::cost_estimate_jpy`): ①現行再現(本委任)約JPY3.5(上限30)/委任_02: 全方式×3題材×2sample 約JPY39(上限50)+S-check(mey・候補1方式・検索あり×2 sample)約JPY54+B3接続確認2呼出約JPY15。委任_02合計約JPY108、案件合算約JPY112。**案件合算300円以下の構成を主案**(承認区分C、7-7によりAI自律)。削減案: sample 2→1(約-20)/D・E省略(約-10)/S-check省略(-54)/coffee省略(約-13)。
- **量産恒常費用**(1記事): E0基準。A〜Dは追加検索0・追加LLM呼出0、追加token代JPY<0.1〜0.3、70円/記事セット目標への影響は0.5%未満。Eは約+JPY0.7(約+1%)。ただしProductionは検索込みのため、実際の影響は『検索回数の変化』が支配的(1回=JPY1.6)で、+1回でもA〜Dのtoken増を上回る。→ S-checkが重要。

### 5-4 原価低減の観点(Charter 3、本Trialの外)
検索料がResearch+検証原価の約89%を占める。Prompt改善が検索を減らす可能性は低いが、将来『検証をResearcherの取得出典で行う(検索なし化)』等の検討余地がある(検証は現状、出典本文を再取得せず独立検索する設計)。**新仕様候補であり本Trialでは実装・比較しない**(判断候補として報告)。

## §6 下流接続(Ledger→B3、ユーザー§2-⑤)

1. **Ledger登録可否**: 各cellで下書きFact→Ledger本体schema(`FACT_LEDGER_JSON_SCHEMA`)適合を`validate_ledger_draft`で確認(B方式は畳み込み後)。Production関数`build_verified_ledger_text`でrendered Ledgerを生成。testで『Bのactorが既存欄conditionsへ畳み込まれrendererで出力される』ことを固定。
2. **B3利用可能性**: `b3.extract_fact_ids_from_ledger`・`b3.verified_fact_ids`で解釈できることをtestで固定(API 0)。実B3 1呼出(委任_02): `er083_b3_background_fact_trial_01_lib.run_candidate(candidate="baseline")`を再利用し、**E0と最良方式のmey s1 Ledgerのみ**で、Ledgerに主体Factがある時に現行B3が選ぶか(C1陽性対照PC2 baseline 2/2の知見、`C1_POSITIVE_CONTROL_CLOSEOUT_01.md`)を確認する(方式ごとに最良1条件、約JPY15)。

## §7 実行順・並列化・S-check

1. (本委任) harness+test(API 0) → 設計書commit → ①E0×2(mey)実走。
2. (委任_02、Fable照合後) **全方式×3題材×2sample**: topic別に3 process並列(出力dirがtopic別でstage cacheが衝突しない。callログは追記のみ)。dry-runで経路確認→実走。1 processあたり約20呼出、wall約15〜20分。
3. (委任_02) 評価・創作adjudication(worker)→機械集計→Fable独立評価。独立作業(eval実装・test・adjudication準備)は実走待ち中に先行済み。
4. **S-check(任意・候補1方式のみ)**: 最良候補の**Researcher段のみ**を`tools=web_search`付き(Production同一呼出構造、Promptのみ候補)でmeyを2 sample走らせ、`web_search_call_count`/時間をProduction記録(15回/159s)およびgpt-6-luna歴(4〜16回)と比較。検出力は低い(少数標本)ため、結論は『Production歴の範囲を明確に超える増加がない』に限る。費用約JPY54。E0再走(さらに約JPY54)は設計上は付けない(歴と同一テーマの単発記録で代替、限界として明記)。判断はFable。

## §8 Opus独立技術レビュー観点案(11-3: 本委任は非該当、設計完成後にFableが任意判断。5件以内)
1. 方式A/Dの追加観点文が、党派的出典表現(SABAの『terrorist』等)の事実化や、出典にない動機・因果の補完を防げているか。
2. 検索なしharnessは、Production(検索込み1呼出)のFact保持の代理指標として十分か、n=2・出典packet固定の限界の置き方。
3. gold/regex採点と創作adjudicationプロトコル(機械フラグ+出典逐語照合)の見落とし・偽陽性リスク。
4. 方式C(検証側)がLedgerへ届く経路がAMBIGUOUS化に限られる点と、AMBIGUOUS増によるB3下限2件(VERIFIEDのみ算入)・再生成費用への副作用。
5. Production採用時の隔離方式(`vfl01`は15本超がimportする共用モジュールのため、Family X専用の新テンプレート+単一flag[既定OFF]か、Offline Trial→正式採用か)。

## §9 E-1: 参照した既存仕様・記録(逐語)
- CURRENT_SPEC:1165-1169(Family X正式経路): 「research → verified fact ledger → `storyline_b3`(Selected Fact Brief)→ 決定論B3 producer…」、B3採用Fact下限2件(2026-10-19決定、OPEN-420、`[VERIFIED]`のみ算入)。Research/検証Promptの『帰属・背景保持』に関する承認済み仕様文は**存在しない**(XRG 委任_01 §3、Grep済み。仕様の空白)。
- OPEN-416(中東記事、USER_DECISION_REQUIRED #112)/OPEN-425(本件の根本原因調査+C1陽性対照Trial、C1の背景補完追加0/12→C1評価は撤回済み[ユーザー2026-10-20])。
- DECISION_LOG:20154(Researcher `notes_for_writer`案N: 逆表現のみ、Verification・Fact本文・schema不変。Ledger側の別問題で、本Trialの『主体・背景の脱落』とは独立)。
- 過去Trialとの重複回避: B3側(C1)は『Ledgerにあるものを選ぶ』検証で、上流Ledgerに無いFactは扱えない。本Trialは上流(Research/検証)の保持を扱い重複しない。DECISION_LOG:20154(案N)は逆表現のみで、主体・背景保持は未検証。

## §9 v02(追記、2026-10-20 委任_02、候補方式の実走前に確定。管理ID FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01 委任_02)

**変更理由(Fable決定、委任_01所見に基づく)**: ①E0(検索なし)はKEY 9/12=0.75で、Production(検索込み)の0/6を部分再現にとどまった。事前登録基準(a)「E0+0.25以上」はE0=0.75では12/12を要し達成不能。また検索なし比較だけでは、Production(検索込み・素材量119K tok)での採否判断に足りない。候補方式の実走前に、以下(9-1〜9-4)へ改訂・追加する。**他の指標・閾値・gold(gold_02)・方式文面は不変。全方式に同一適用。結果を見ての基準変更は行わない。**

### 9-1 基準(a')(§4の(a)を置換。(b)〜(h)は不変)
- 旧(a): mey KEY保持率(Ledger、n=12観測)がE0+0.25以上かつ0.667以上。
- **新(a')**: mey KEY保持率が **0.917(11/12)以上、またはE0比+0.17以上(=2観測以上の改善)** で、かつ0.667以上。REJECTED条件「(a)の改善が+0.10未満」は不変(改善+0.10未満=REJECTED)。
- 機械判定: `er085_research_fact_retention_trial_01_eval.py::classify_variant`(ラベル: REJECTED / NOT_FINALIZABLE_UNADJUDICATED / NOT_VALIDATED_BELOW_CRITERION_A_PRIME / NOT_VALIDATED_CRITERIA_UNMET / USER_DECISION_CANDIDATE_COST / VALIDATED_CANDIDATE_PENDING_SEARCH_ARM)。最終ラベルはFable。`test_02.py::test_verdict_machine`で固定。

### 9-2 検索込み比較腕(S-check §7-4を置換・廃止)
- **S-check(候補1方式のResearcherのみ・約JPY54)は廃止し、本腕に吸収する。**
- 実装: `er085_research_fact_retention_trial_01_search_arm.py`。Production経路と同一の `er012_e_family_entertainment_two_level_runner_01.run_researcher_for_topic(client, topic)`(`tools=web_search`固定、model/effort/schema/developer message同一)を呼ぶ。topicはProduction run_mey_01と同一文字列(`中東情勢が悪化、イエメン・サウジ周辺で攻撃続く`)。Prompt差分は**当該process内のcontext managerでの差し替えのみ**(終了時に必ず復元、testで固定): E0=不変(Production関数の出力と一致をrun前にassert) / A=Researcher Promptに第5・6観点(検索なしと同一文言)を挿入 / D=A+検証Promptに1行追加(検証は`run_verification_for_topic`も呼ぶ。独立再検索が発生するため費用・検索回数に含める)。E0/Aは検証を走らせない(Ledger比較は『draft view』=draft全FactをVERIFIED扱いで描画。Productionの検証が追加で脱落/AMBIGUOUS化させ得る点は限界)。
- 構成: mey題材、E0/A/D × 2 sample = 6 run(Researcher約JPY27/run、Dは検証約JPY9追加)。出力は `er085_output/research_fact_retention_trial_01/search_arm/` のみ(Production run dir・Ledgerに書かない)。harnessから別途Web検索しない。無料HTTP取得は各runが実際に引用した出典URL本文のみ。
- **採点(事前登録)**: 各runの引用URL(Ledger draftの`source_url` ∪ `url_citation`)を無料HTTPで取得(`curl.exe`)。出典本文の700字窓(350字刻み)で、項目が**その出典に明示されているか**(expected)を判定し、expectedの項目のみ、Ledger(Dは検証後/E0・Aはdraft view)の**単一Factブロック**に保持されたか(retained)を判定する。項目: **SA**=空港攻撃等の主体(出典窓に{Ansar Allah/Houthi}∧{Saudi/Riyadh/airport等}∧{attack/strike/drone/missile}。Ledger側は同一Factブロックに主体∧サウジ関連語∧攻撃語)、**SC**=紅海・海上交易路とイエメン戦況の文脈(出典窓に{Red Sea/Bab al-Mandab/maritime/shipping/trade route}∧{Houthi/Ansar Allah/Yemen}。Ledger側は同一Factブロックに海上語∧フーシ/イエメン語)。加えてgold_02のKEY項目(M-A1〜M-B4)を、引用出典の窓にそのgroups全てが一致する場合のみexpectedとして併用。取得不能(HTTP非2xx/本文500字未満)の出典はexpectedに含めず、件数を明記。retention=保持観測/expected観測。
- **検索・費用の判定(事前登録、(h)の具体化)**: 候補(A/D)の `web_search_call_count`(Researcher)の2 run平均が **E0の2 run平均+2回以内**、かつ Researcher費用の平均がE0平均+JPY3以内。Dの検証検索はE0側に比較対象がないため、Production実績(5回/JPY9.11、run_mey_01)を参照値として併記し、Dの追加費用(恒常+検証分)は『Production検証は元々存在するため、Dの差分=検証Prompt 1行のtoken増のみ』として扱い、検証検索回数がProduction実績の2倍(10回)を超えた場合は増加とみなす。n=2の検出力限界(歴史的分布4〜16回)をClosoutで明記し、結論は『増加が確認されない/確認された』に限る。
- 品質の判定: 検索込みでの保持改善(retention)がE0比+0.17以上、または0.917以上(expected観測が各方式4以上ある場合のみ。満たない場合は『識別不能』と明記し、Fableへ判断候補)。創作: 検索込みrunのフラグ付きFactを引用出典の逐語で照合(`adjudication_02.json`)。UNSUPPORTEDが1件でもあれば当該方式はREJECTED。
- **異常STOP条件**: 1 runの`web_search_call_count`が40(Production実績20の2倍)を超えたら即中断しFableへ報告(`ANOMALY_STOP.json`)。予算超過見込み・案件合算300円超見込みもSTOP。

### 9-3 検索なし本走の構成(§7-2の具体化)
- 方式E0/A/B/C/D/E × {mey, muse, coffee} × 2 sample(`_run.py`)。meyのE0(s1/s2)は委任_01の実走stage cacheを再利用し再実行しない(同一cell・同一Prompt)。muse/coffeeのE0は新規。方式間のR0/RA/RB・検証stageはpaired共有(§design_matrix stage_sharing)。

### 9-4 費用表(更新)
| 項目 | 見積JPY | 備考 |
|---|---|---|
| 検索なし本走(mey 5方式 + muse/coffee 6方式、各2 sample) | 約39(上限45) | stage共有、§5-3 |
| 検索込み腕 6 run | 約162〜180(E0/A: Researcher約27×4、D: 約36×2) | 検索回数に依存。1 run=検索料JPY1.6/回。ガード合計190 |
| Ledger→B3接続(最良1方式のmey Ledger、現行B3 2 call) | 約15 | `er083_c1_positive_control_01_run.py`系 |
| 委任_02 合計 | 約216〜234(Cap 230、T-3記録) | 案件合算(委任_01 実費4.245含む) ≈220〜238 ≤300 → 承認区分C(7-7、ユーザー費用承認不要) |
- 当日実費累計(PMツール修正後): 約343(314.5+PLWP1 28.6)+本委任 約230でも1,000円以内。
- 量産時の恒常費用との区別(ユーザー§4): 上記はTrial費用(開発費)。恒常費用はCloseoutで『A/D: 追加検索0・追加LLM0・token増のみ』を検索込み腕の実測(検索回数・token差)で示す。70円目標への影響も併記。

### 9-5 E-1(v02で参照した既存記録)
委任_01 RESULT_PACKET(docs/pm/RESULT_PACKET_XRFR1.md (6)(10))、`BASELINE_REPRO_01.md`、gold_02。Fable決定1〜4(委任_02委任文、`docs/pm/delegation_log/2026-10-20_FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01_委任_02.md`)。

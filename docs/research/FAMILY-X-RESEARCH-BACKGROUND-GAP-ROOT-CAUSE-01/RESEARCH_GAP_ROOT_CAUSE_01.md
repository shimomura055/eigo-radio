# RESEARCH_GAP_ROOT_CAUSE_01: 中東記事 背景3点(攻撃主体/動機/イエメン情勢との接続)の欠落工程の追跡

- 管理ID: FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01 委任_01(2026-10-20、調査のみ。API 0、JPY0、コード変更0、Production変更0)
- 対象run: `er019_output/middle_east_yemen_saudi/run_mey_01/`(読取のみ)。Ledger生成=2026-10-18 10:08(`research_ledger/*`のmtime)
- 到達上限Status: `RESEARCH_GAP_ROOT_CAUSE_IDENTIFIED_PENDING_FABLE`
- 補助: `xrg1_trace_01.py`(read-only集計)/`xrg1_trace_01_result.json`(その出力)。出典の取得本文はscratchpad(`...\scratchpad\xrg1\`)にあり、repoへは含めない(下記は短い抜粋のみ)。

## §1 工程マップ

| 工程 | 実装(関数:行) | 入力 | 出力(run_mey_01内) | モデル/Prompt |
|---|---|---|---|---|
| Research(Web検索+Fact下書き) | `er019_family_x_entertainment_production_runner_01.py::run_research_and_ledger`(97-146) → `er012_e_family_entertainment_two_level_runner_01.py::run_researcher_for_topic`(183-203) | テーマ文字列のみ | `research_ledger/fact_ledger_draft.json`(11 Fact)、`audit/researcher_full_record.json`(prompt・検索クエリ42本・web_search_call=15) | `gpt-6-luna`(runtime_evidence.json)。Prompt=`er003_v1_en_direct_vfl_01_generate.py:137-170`(`RESEARCHER_PROMPT_TEMPLATE`)、developer=同:132 |
| Fact検証(verify) | `run_verification_for_topic`(206-) | 下書き11 Fact | `fact_ledger_verification.json`、`audit/verification_full_record.json`(検索クエリ19本・call=5) | 同`gpt-6-luna`。Prompt=同:228-250(`VERIFICATION_PROMPT_TEMPLATE`、観点237-246) |
| Ledger確定 | `vfl01.build_verified_ledger_text`(279-)、runner:122-125 | 下書き+検証 | `verified_fact_ledger.txt`、`verdict_counts.json`(VERIFIED 11/AMBIGUOUS 0/REJECTED 0) | LLM無し |
| Storyline+B3 | `er019_family_x_storyline_b3_fact_selection_01.py`(runner:147-) | Ledger全文 | `storyline_b3/fact_selection_evidence.json`、`full_ledger.json`、`selected_brief.md` | `gpt-6.1-sol`(CURRENT_SPEC:1215) |
| 決定論producer | `er053_b3_deterministic_producer_01.py` | B3出力+Ledger | `annotation.json`、`selected_brief_annotated.md` | LLM 0 |
| Writer(W-1) | `er053_family_x_factlock_ja_writer_01.py` | 注記済みB3 | `ja_writer/original|revision1|revision2.md` | R0 luna→R1/R2 astra等 |

記録の所在: 検索クエリ=`research_ledger/audit/researcher_full_record.json::search_usage.queries`(42本)/`verification_full_record.json`(19本)。取得出典一覧=**専用の出典一覧ファイルは存在しない**(Fact毎の`source_title/source_url`のみ。Researcherが検索で見たがFactにしなかったページのURLは記録されない=「見落とし」の厳密追跡に限界)。抽出候補Factの採否=**候補棄却の記録機構が無い**(Researcherの出力=最終下書き11件のみ。棄却候補・理由コードは保存されない)。検証=`verdict`と`verification_notes`のみ(閾値・理由コードは無い、REJECTED 0)。

## §2 3点の欠落の追跡

共通事実: Researcher下書き=11件、検証でVERIFIED 11/REJECTED 0(`xrg1_trace_01_result.json`)。**検証段階で落とされた候補は0件**。Ledger/Fact Lock/B3/producer/Writerは、Ledgerに無い情報を補う機構を持たない。

### 点1 誰が攻撃したか

| 段階 | 結果 | 証拠 |
|---|---|---|
| (a)検索クエリ | 主体語は**含まれた**。責任主体を問う語(claimed responsibility/who)は**0** | Houthi/Ansarを含むクエリ12本(idx 0,3,24,27,28,29,30,31,35,36,37,38)。例idx0「October 2026 Yemen Saudi Arabia attacks latest Houthi Saudi attacks」、idx3「site:un.org Yemen Saudi attacks 2026 Houthi」。責任・犯行声明語は0。クエリ42本中32本が死傷者数・日付の確認用(`casualty/number-oriented`) |
| (b)出典本文 | **存在した**(2出典で明示) | ①F11出典`osesgy.unmissions.org`(取得2026-10-20 10:05 JST、HTTP200)の2026-10-11声明: 「I strongly condemn the continuing attacks against civilian infrastructure in the Kingdom of Saudi Arabia **by Ansar Allah**, including the latest attack on 10 October against King Khalid International Airport in Riyadh」。②F01出典`dppa.un.org`(10:02、200)の2026-10-09記事: 「Ansar Allah has carried out deadly attacks against civilian and energy infrastructure in Saudi Arabia」。③補助: 同ページの関連記事見出し「Statement by the Secretary-General - on the attack on Riyadh」冒頭「lethal attack by the Houthis on King Khalid International Airport」(スニペットのみ、全文は未取得=未確認)。④F10出典(アデン治安局、10:05、200)はフーシ派発射を明記(アデン事案、Ledger F10に反映済み) |
| (c)抽出・構造化 | **脱落** | F11 claim: 「国連イエメン担当特使は、サウジアラビアの民間インフラに対する継続的な攻撃を非難し…」(`fact_ledger_draft.json` F11)=「Ansar Allahによる」を欠く。F01 claim: 「…サウジアラビアの民間・エネルギー施設への攻撃を報告した」=主体を欠く(受動形)。主体語がclaimに現れるのはF09・F10(イエメン国内事案)のみ(`draft_claims_with_actor_term`=[F09,F10]) |
| (d)検証 | **脱落を検知せず** | 検証者はF11のnotesに「サウジアラビアの民間インフラへの継続的な攻撃を**アンサール・アッラーによるものとして**非難」と**自ら記した**(`fact_ledger_verification.json` F11)が、claimに欠けている点を指摘せずVERIFIED。検証観点(vfl01:237-246)は「claimがsourceに存在するか/数字・scope/日付/因果の過剰」の**正しさ検査**で、「出典内の重要な帰属・主体が省かれていないか」の観点は無い(243「条件が抜けていないか」が最も近いが制度条件の文脈) |
| (e)Ledger/Fact Lock | 落ちた工程ではない | `verified_fact_ledger.txt`は検証済み11件をそのまま収録 |
| (f)B3/producer/Writer | 到達前に欠落 | Ledgerに「UN特使がAnsar Allahによる攻撃と述べた」というFactが無い。さらにF02/F03/F05/F07/F08/F09の`ambiguity`/`notes_for_writer`は「攻撃主体は確定しない/特定されていない」(GACA個別発表についての正しい記述)で、Ledger全体として「主体未特定」の印象を作った。B3の`writer_constraints`「攻撃主体や攻撃の背景・動機は採用Factから特定しない」(`selected_brief.md`)は、採用Factに主体が無い以上、正しい出力 |

**判定(点1)**: 欠落工程=**Researcherの構造化(claim化)での脱落**(区分「構造化で脱落」)。副因=検証が「脱落検知」を観点に持たない(仕様不足)。情報源に存在しない、ではない。Researcherは主体語を含む検索を行い(a)、主体を述べる2出典を引用していた(F01・F11の出典URL)ので「未調査」でもない。

### 点2 なぜ攻撃したか(動機)

| 段階 | 結果 | 証拠 |
|---|---|---|
| (a) | 動機・理由を問う語は**0**(why/motive/reason/retaliat/in response) | クエリ42本の語分類(`categories."motive/why/reason"`=[]) |
| (b) | 取得した範囲の出典に**動機・犯行声明の明示は無い** | F11出典: 「grave escalation…serious threat to regional security…complicate even more peace efforts」=影響の評価であり動機ではない。F01出典: 「threats… are becoming enmeshed with the broader confrontation over control of maritime trade routes and the stresses on the international energy market」=特使の状況認識で、攻撃の動機を述べたものではない。SABA/アデン治安局/GACA(SPA)/Okazにも動機の記述なし(Okaz・SPA系は主体語0件をgrepで確認) |
| (c)〜(f) | 該当情報が出典に無いので脱落対象が無い | – |

**判定(点2)**: **情報源に存在せず(収録出典・同一ページ導線の範囲。正しい結果)**。ただし責任主体の声明・動機を問うクエリが0であり、外部(フーシ側声明や通信社分析)に存在するかは**未調査=不存在とは確定できない**。動機は未確認事項として記録するのが正しく、一般的動機の推測で補ってはならない(§4)。

### 点3 イエメン情勢と今回の攻撃のつながり

| 段階 | 結果 | 証拠 |
|---|---|---|
| (a) | イエメン関連語は多数。「背景」を問う語(background/conflict/coalition/Red Sea)は実質0(idx11「coalition」はSana'a空爆の確認用、35/36は「escalation」=UN安保理声明探し) | `categories."background..."` |
| (b) | 出典に**文脈は存在**。ただし「イエメン戦闘が攻撃の原因」と述べる記述は**無い** | F01出典(2026-10-09): 「Following Ansar Allah's advances on Mokha and the coast along the Bab al-Mandab…the Government launched a large-scale counter-offensive…Ansar Allah has carried out deadly attacks against civilian and energy infrastructure in Saudi Arabia」「Ansar Allah's threats against Saudi-linked commercial ships in the Red Sea…」。F01出典の「Link to original content」先UN News(2026-10-09、取得10:06、200): 「a Houthi offensive launched in September has sharply escalated the 12-year-long war」「fighting between Iran-backed Houthis and Saudi-backed Government forces」「spillover from the US-Iran war」「Cross-border missile and drone strikes on Saudi airports and energy infrastructure have continued this week」。いずれも並置・状況認識であり、因果は述べていない |
| (c)構造化 | **一部脱落** | F01 claimは戦闘激化地名とサウジ施設攻撃を並べたが、「Ansar Allahの進攻」「Bab al-Mandab/紅海の商船への脅威」「海上交易路をめぐる対立」「政府の反攻」という文脈要素と主体(Ansar Allah)を欠く |
| (d) | 検出されず | 点1(d)と同じ |
| (e) | 落ちた工程ではない | F01はLedgerに入った |
| (f) | **B3でF01不採用(正当)** | `fact_selection_evidence.json` F01: test2〜4=NO、reason「イエメンの戦闘再拡大は重要な背景だが…国内戦闘の激化が空港攻撃を引き起こしたとの因果関係も示されていない」。F01 claimに主体・文脈が無く因果も無いため、不採用判断自体は仕様どおり |

**判定(点3)**: 欠落工程=**構造化で脱落**(F01 claimから主体と文脈要素が落ちた)。結果としてLedgerのF01が「戦闘激化」と「サウジ施設攻撃」の並置だけになり、B3が合理的に不採用にした。「戦闘と攻撃の因果関係」自体は出典が述べておらず、**因果のFactは存在しない(書いてはならない)**。

### 6区分の判定

| 点 | 区分 | 欠落工程(1つ) |
|---|---|---|
| 1 誰が | 構造化で脱落(副: 検証が脱落を検知せず/仕様不足) | Researcher claim化(`fact_ledger_draft.json` F01/F11) |
| 2 なぜ | 情報源に存在せず(収録出典範囲。外部は未調査) | 欠落ではなく、Ledgerが「動機の記載なし」で正しい |
| 3 つながり | 構造化で脱落(主体・文脈)。B3不採用は正当 | Researcher claim化(F01) |

## §3 承認済みResearch仕様との照合(11-8)

| 仕様文(逐語抜粋、場所) | 実挙動 | 11-8判定 |
|---|---|---|
| Researcher Prompt「あなたが行うのは、Factだけを収集・整理すること」「Source優先順位 1.政府・規制当局等の一次資料…」(vfl01:137-155)、構造化観点は「対象範囲/適用条件/数値の内訳/観察・相関・因果の区別」の4つ(同156-162) | 一次/公式資料(SPA、UN、アデン治安局)を中心に11件を作成。**帰属(誰がそう述べ/誰の行為と述べるか)・背景文脈の保持を求める観点は4つの中に無い** | **仕様の空白**(乖離ではない) |
| 検証Prompt「【検証観点】FactがSourceに実際に存在するか…条件が抜けていないか…因果関係を過剰に強めていないか…Source間で矛盾していないか」(vfl01:237-246) | 検証は「書かれたFactの正しさ」を検査。**省略(落ちた主体)を検知する観点が無い** | 仕様の空白(243「条件が抜けていないか」は拡張解釈の余地はあるが、主体省略を想定した明文は無い) |
| Family X経路は`efam.run_researcher_for_topic/run_verification_for_topic`を**そのまま**呼ぶ(DECISION_LOG:9604、runner:97-125、CURRENT_SPEC:1167-1169) | 実装と仕様は一致 | 仕様どおり |
| Ledger確定=VERIFIEDのみ収録(vfl01:279-) | 実装どおり | 仕様どおり |
| B3採用下限2(CURRENT_SPEC:1171、OPEN-420) | 本runはF04+F11の2件(`min2_policy.final_selected_ids`)。Ledgerに無い主体は選べない | 仕様どおり |
| `CURRENT_SPEC.md`のFamily X Researchの網羅性・背景・主体取得要件 | Grep(`Researcher|Source優先|Research prompt|攻撃主体|帰属`)で**該当する承認済み仕様文なし**(CURRENT_SPEC:799は旧Theme2手動Ledger供給経路の記述のみ) | 仕様の空白 |

**11-8結論: 仕様文と実装の乖離(=範囲内不具合)は見つからなかった。**根本原因は「仕様の空白」(Researcher/検証Promptに帰属・文脈の保持/脱落検知の観点が無い)であり、修正にはResearch Prompt(Production)への新観点追加=委任文の線引き上「範囲外(新仕様→判断候補)」に該当する。

### 過去の同種対策との関係

- OPEN-416/E2E_PLAN_01(2026-10-18): 「攻撃主体未特定」「独立報道(Reuters/AP)Ledger内0件」を**Ledgerの限界**として記録。今回の追跡で「主体未特定」は出典の事実ではなく、Ledger化段階の脱落が一因と判明(E2E_PLAN_01の当該記述は更新が必要)。
- DECISION_LOG:20154(Researcher notes_for_writer案N、逆表現のみ)・OPEN-423/C1 Trial: いずれも**LedgerにFactがある前提**でB3/Writer側を扱った。本件(点1・3)は上流Ledgerに無いFactが原因であり、**C1が追加できる素材自体が元からLedgerに無かった**(C1の追加実績0件はこの構造から予想される結果で、C1評価撤回[ユーザー決定]と整合)。
- 過去対策のGrep(`背景|主体|動機|欠落`、OPEN_ITEMS/DECISION_LOG)で、「Researchの帰属・背景の保持」を扱う承認済み対策は見つからなかった。**新規(再発ではない)**。

## §4 「主体・動機の混同」チェック

| 区分 | 出典が示す内容 | 裏付けの質 |
|---|---|---|
| (i) 事件の攻撃主体 | UN特使が「Ansar Allahによるサウジ民間インフラへの継続攻撃(10月10日リヤド空港含む)」と明示(2026-10-11)、10月9日にも言及。UN事務総長声明の見出しスニペットに「Houthis…attack on King Khalid International Airport」(全文未確認)。アデン空港・マリブ事案はイエメン政府側(治安局/SABA)がフーシ派発射と報告(別事案) | UN特使声明=国連高官の公式発表(死傷者は「Saudi authoritiesによれば」と帰属付き)。イエメン政府系は紛争当事者側で表現も党派的(SABAは「Iran-backed Houthi terrorist militias」)。**サウジGACA/エネルギー省の発表は主体を述べていない**=主体を述べる出典と述べない出典が併存 |
| (ii) 主体の一般的動機 | 取得範囲に無し | – |
| (iii) 地域紛争の一般的背景 | 全面戦闘復帰、Ansar Allahの進攻、政府反攻、Red Sea商船への脅威、海上交易路・エネルギー市場の緊張(UN特使/UN News)、「Iran-backed」「Saudi-backed」(UN News) | UN発表・UN News。因果は述べていない |

混同の防止: F09/F10(イエメン国内事案の主体)をサウジ攻撃の主体へ転用しない(B3がF09で既にそう判断済み)。事件主体は(i)の「UN特使が帰属」として、断定でなく帰属表現で扱う必要がある。動機は(ii)が空のため記事で語れない。

## §5 原因別の対応案

### 5-1 範囲内不具合
該当なし(§3)。修正設計の実施対象は無し。

### 5-2 情報源に存在しないもの(点2)
- 未確認事項として記録: 該当Factの既存フィールド`ambiguity`(schema不変)に「出典(UN特使声明)は影響の評価のみ述べ、動機・犯行声明は述べていない」を残す運用案。架空の動機Factは作らない。記事としては「動機は確認されていない」と書くか触れないかの選択(判断はFable/ユーザー)。

### 5-3 新仕様が必要な部分(点1・3、判断候補)
**欠落原因**: Researcher/検証Promptが、出典が明示する「責任主体の帰属」と「同一出典が述べる直接の背景文脈」を保持・点検する観点を持たない(§3)。

**改善案(最小・条件付き。全記事での一律必須化ではない)**:
1. Researcher Promptに第5観点: 「出典が事象の責任主体・行為主体を明示している場合に限り、claimに『誰がそう述べているか/誰の行為と述べているか』を省かず帰属表現で記す。出典が主体に触れない/出典間で異なる場合は、その差をambiguityに記す。出典が明示していない主体・動機は書かない」。
2. 第6観点(任意): 「同一出典が明示する直接の文脈(例: 当該声明が併記する戦況)は、当該Factのconditions/notes_for_writerに最大2文で保持。因果は出典が述べた場合のみCAUSAL_STATED_BY_SOURCE」。
3. 検証Promptに1行: 「claimが、出典内の重要な帰属(主体)を省いていないか」。

- schema変更なし(既存`claim/conditions/ambiguity/notes_for_writer`)。LLM呼出数の追加なし。
- 変更箇所案: `er003_v1_en_direct_vfl_01_generate.py:156-162`(Researcher観点)・`:237-246`(検証観点)。**ただし`vfl01.build_researcher_prompt`は他Family/多数のDEV scriptがimportしている(Grepで15本超)ため、同ファイルの直接編集は影響が広い。Family X専用の新テンプレートを新コード経路に置き単一flag(既定OFF)で切替える形、またはOffline Trial先行を推奨**(Production Prompt直接編集は11-7限定例外の対象外)。
- 検証案(offline): (A)固定出典(本調査の取得物)でF01/F11相当のclaimに主体が入るか。(B)陰性対照=主体がそもそも述べられないテーマ(例: coffee_prices)で、新観点が架空の主体・背景を足さないこと。(C)中東で1回のResearch再実行が必要(新観点の実挙動確認は既存Ledgerの再利用では不能)。
- 費用見積(実測基準): 中東Research+検証=research 26.995+ledger 9.110=**JPY36.1/回**(`cost.json`)。陽性(中東)1回+陰性1テーマ1回で約JPY72(単価が同規模である前提の推定)。Production単価への影響: 追加LLM呼出なし、Prompt数行追加とclaim長の微増のみ(定量は未測定、実測前の仮置きとして1記事JPY1以内の見込み)。Delivery影響: 工程増なし。
- Q/D/C影響: Q=帰属保持によりB3が主体を扱えるようになる(採用は従来どおりB3判断で強制しない)。リスク=党派的出典の表現(「terrorist」等)の事実化(過剰帰属)→出典名義の帰属表現で緩和。D=不変。C=微増。
- **過剰仕様の回避**: 「全記事で誰が・なぜを必須」にはしない。出典が明示する場合のみ保持。ストーリー性はB3選定側で従来どおり判断。

## §6 結論(ユーザー向け)

背景3点のうち「誰が攻撃したか」は情報源に存在していました(国連特使の10月11日声明と10月9日の発表が、どちらもAnsar Allah[フーシ派]の攻撃と明記)。Researcherがそれを調べて引用していながら、Fact文に主体を書かず(受動形)、検証もその省略を検知できなかったため、Ledgerから脱落しました。「なぜ」は、確認できた国連発表・各国当局発表に動機や犯行声明の記載が無く、記録に無いのは正しい結果でした(フーシ側の声明等は未調査のため、不存在の断定はできません)。「イエメン情勢とのつながり」は、国連発表に戦況・Red Sea・海上交易路の文脈が書かれていましたが、F01のFact文から主体と文脈が落ち、並置のみとなったためB3が合理的に不採用にしました。なお、戦闘と攻撃の因果関係そのものは出典が述べておらず、書いてはいけません。今回は承認済み仕様と実装の乖離は見つからず、原因はResearch/検証Promptに「帰属・文脈の保持」の観点が無いという仕様の空白で、直すには新観点の追加(=判断候補)が必要です。

## §7 Opusレビュー観点案(修正が新構造を伴う場合のみ)
1. 第5/6観点の文言が、出典の党派的表現の事実化(過剰帰属)を防げるか。
2. 他Family(A/B/C/Z)の共用Researcher Promptへ影響しない隔離方式(新コード経路+単一flag)の妥当性と、DefaultOffIsolation testの網羅。
3. 検証Promptへの「省略検知」追加が、偽陽性でAMBIGUOUS/REJECTEDを増やし再生成費用を押し上げないか。
4. 陽性/陰性対照の設計が、効果と過剰補完の両方を判別できるか(n=1の限界)。
5. 点2(動機)を「未確認事項」としてLedger外に残す扱いと、記事側の書き方(動機に触れない)の整合。

## 付録: 出典取得ログ(HTTP、無料、2026-10-20 JST)

| 番号 | URL | 取得時刻 | HTTP | 備考 |
|---|---|---|---|---|
| src_01 | dppa.un.org/en/news/yemen-has-returned-to-full-scale-war-special-envoy-warns (F01) | 10:02:42 | 200 | 点1・3の根拠 |
| src_02 | spa.gov.sa/ar/N2695829 (F02) | 10:02:44 | 200 | 主体語0 |
| src_03 | spa.gov.sa/en/w2697151 (F03) | 初回タイムアウト、再取得10:06:11 | 200 | タイトルのみ確認、主体語0 |
| src_04 | oananews.org/node/713861 (F04) | 10:04:04 | 200 | GACA続報全文、主体語0 |
| src_05〜07 | spa.gov.sa N2698672 / N2698603 / w2698805 (F05〜F07) | 10:04:07〜10:04:49 | 200 | JS描画ページのため本文は取得できず見出しのみ。主体語0(grep) |
| src_08 | okaz.com.sa/local/na/2270709 (F08) | 10:05:04 | 200 | 主体語0 |
| src_09 | sabanew.net/story/en/154079 (F09) | 初回406、再取得10:06:12 | 200 | 「Iran-backed Houthi terrorist militias」 |
| src_10 | media.aden-gov.net/news/1167 (F10) | 10:05:05 | 200 | フーシ派発射と明記 |
| src_11 | osesgy.unmissions.org/...latest-attacks-against-saudi (F11) | 10:05:06 | 200 | 点1の主根拠 |
| src_12 | apnews.com/article/d2e0868f… (F04 ambiguityのAP) | 10:05:08 | 403 | **未確認**(取得不可) |
| src_13 | news.un.org/en/story/2026/10/1168559 (F01出典内「Link to original content」) | 10:06:09 | 200 | 点3の補助。Ledger非収録のページ |

制約: 取得は2026-10-20で、Ledger生成(2026-10-18)の2日後。根拠に使ったページの日付は10/9(F01、UN News)と10/11(F11)で、Ledger生成前に公開済みの内容。F09/SABAページ内の他記事(安保理議長声明等)の掲載時期は不明のため根拠に使っていない。SPA 05〜07のJS描画ページは本文未取得のため、主体語0の確認は見出しと静的HTMLの範囲に限る。

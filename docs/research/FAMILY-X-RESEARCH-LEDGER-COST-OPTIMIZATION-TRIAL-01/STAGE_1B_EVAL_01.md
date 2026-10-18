# RLCT Stage 1b 人手評価(STAGE_1B_EVAL_01)

- 管理ID: FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_13 / 評価日: 2026-10-18(JST) / 費用: JPY0(有料API・Trial再実行なし、保存済み出力のread-only評価)
- 性質: Trial評価(Production不変、未承認、採否判断なし)。到達上限Status: `TRIAL_EVALUATED_CLASSIFICATION_DRAFT_PENDING_OPUS_C_AND_FABLE`。
- 評価者: Sonnet(使用モデル名=claude-sonnet-5-5、机上、1名、LLM API呼出なし)。**n=1/記事・単一評価者**を以下の全判定に付記する。Fable独立判定・Opus条件Cレビューは未実施。
- 入力: `STAGE_1B_RESULTS_01.md`、`er082_output/rlct_trial_01/{streaming_price,openai_copyright,central_bank_mortgage}/<方式>/{result.json,storyline_b3/selected_brief.md,_work/verify_*.json}`、M0のverdict/notesは`<article>/_inputs/research_ledger/fact_ledger_verification.json`。
- 手順の正本: `STAGE_1A_EVAL_01.md` §1〜§6+追補、`TRIAL_DESIGN_03.md` §8(ラベルのマスク/R-07全方式同一基準/M2c↔M3c=B3揺らぎ/unmet内訳/新設計列R-B7)。1bはこれに従った(適用箇所は§8に一覧)。

## 1. 判定手順と限界

手順(1aと同一):
1. 各記事でM0を基準(REF)として開示し、M0b/M1/M2/M3の`selected_storyline`+`selected_brief.md`+選定Fact ID+最終verdictを、方式名を伏せたラベル(α〜δ、乱数seed=20261018でシャッフル)で並べた伏せpacketを生成した(`docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/er082_rlct_blind_key_1b_13.py`、LLM呼出なし)。鍵(`er082_output/rlct_trial_01/_blind_key_1b_13.json`)は判定を記録するまで開かなかった。
2. 「【独立検証前の編集仮説】」ラベルはpacket生成時にマスク(置換)した。ただし1b全15 jobで該当文字列は0件だった(鍵の`masked_occurrences`=全て0。別途grepでも1b result.json/selected_brief.mdは0件。出現は1a inbound旧M2/M3のみ)ので、実質マスク対象はなかった。
3. 構成差3段階(軽微/中程度/重大)をM0基準で判定。品質は一対比較(面白さ/一貫性/事実整合、良い/同等/悪い)。構成差と品質は別列。
4. 判定を記録した後で鍵を開き方式名を復元。§4(R-07)・§5(Verifier再現性)の方式別整理は復元後。
5. 事前登録ルール(M0-M0b差が中程度以上の記事では方式差が中程度以下なら方式効果と認めない)の適用: 3記事ともM0-M0b差は軽微(§2)のため**発動せず**、方式差は方式効果として扱える(ただしn=1、生成ばらつきはM0bの1サンプルのみ)。

M0pはB3を持たない(Ledger検証のみ)ため、品質・構成差の対象外(§5のVerifier再現性にのみ登場。openai_copyright・central_bank_mortgageはM0p未実施)。

限界(ブラインドの不完全性、1aと同じ構造に加えて):
- M0は基準として開示。ブラインドはM0b/M1/M2/M3の4ラベル。
- **評価者は判定前に`STAGE_1B_RESULTS_01.md`(方式別の選定Fact ID一覧を含む)を読んでいた**ため、packet内のFact ID・最終verdict・Briefの注記(後述)から方式を推測できる状態だった(完全ブラインドではない)。
- 判定前の推測(記録=scratchpad`guesses.txt`): streaming α=M2/β=M0b/γ=M3/δ=M1、openai α=M1/β=M0b/γ=M2/δ=M3、central γ=M0b/δ=M1、central α・βはM2/M3のどちらか(**Brief全文が同一で区別不能**)。
- blind_key(復元後): streaming α=M2,β=M0b,γ=M3,δ=M1 / openai α=M1,β=M0b,γ=M2,δ=M3 / central α=M2,β=M3,γ=M0b,δ=M1。
- **推測一致率: 区別可能な10ラベル(streaming 4・openai 4・central 2)は10/10一致。区別不能の2ラベル(central α/β)は推測不能(偶然一致50%)。**=ブラインドはほぼ機能していない(推測の手掛かり: ①選定Fact集合とAMBIGUOUS表記、②M2/M3の初回B3由来の「[UNVERIFIED]」注記、③確認B3の「検証補足を反映」文言)。判定の独立性は限定的で、事実の記述(§3〜§5)は原文引用と機械記録に依拠する。
- 単一評価者、各セルn=1回の生成。生成のばらつきはM0bのみで推定(1記事1サンプル)。
- 事実整合は選定Factの**最終verdict(当該方式自身の)**とStoryline/Briefの断定の有無を主根拠にした。AMBIGUOUS/REJECTEDの正否そのもの(Verifierの判定が真実か)は判定対象外(§5で事実のみ整理)。他方式のverdict基準での読み直しは「参考」と明記して別記する。

## 2. B3構成差(M0基準、3段階)

| 記事 | 方式(判定時ラベル) | 選定Fact | 構成差 | 根拠(Storyline/選定Factの差) |
|---|---|---|---|---|
| streaming | M0 | F02,F03,F04,F07 | 基準 | 「Disney+米国単体3プラン値上げ・新規9/23と既存10/21の適用時期差、確認資料では会社の理由を特定できない」 |
| streaming | M0b(β) | F01,F02,F03,F04,F07 | **軽微** | 骨格同一。F01(「最新発表」)追加で冒頭に「今回の調査で確認できた主要な米国向け〜として選んだ」の範囲限定文が入る。**自然ばらつきの基準=軽微** |
| streaming | M1(δ) | F02,F03,F04,F06,F07 | **軽微** | 骨格同一(価格→適用時期→理由不明)。F06追加、年額に【留保必須】(旧価格は別時点の公式ページ照合)、理由欄にReutersの「直ちには回答せず」を追記 |
| streaming | M2(α) | F02,F03,F04,F07 | **軽微** | Fact集合はM0と同一。年額の旧価格に留保(F04=AMBIGUOUS)を追記し、「現在の最新発表とは断定しない」を結論に追加。骨格は同じ |
| streaming | M3(γ) | F02,F03,F04 | **中程度** | F07を再選定で除外(REJECTED)。結論が「確認資料では理由を特定できない」から「旧新料金と適用時期の整理」に移り、理由の論点はBriefの末尾で「不足・制約」(最新性の再確認と会社説明のFact化が必要)として別扱いになる。骨格(価格・適用時期)は維持だが焦点が変化 |
| openai | M0 | F2,F4,F6,F7,F8 | 基準 | 14原告が提訴、請求(賠償・差止め・モデル破棄)、提訴段階で侵害の司法判断なし、OpenAIは直ちにコメントせず |
| openai | M0b(β) | 同一 | **軽微** | Fact集合・骨格同一、言い換えのみ。**自然ばらつきの基準=軽微** |
| openai | M1(α) | 同一 | **軽微** | 同一Fact・骨格。F8に「同日以後の手続状況は未確認で、現在も同じ段階にあるとは断定しない」の留保を追加 |
| openai | M2(γ) | 同一 | **中程度** | 同一Fact集合だが、確認B3がVerifierの補足(10/15の停止是非を巡る命令、10/30・11/6の期限)をF8へ反映し、Storylineの主題が「提訴段階」から「確認できた記録の範囲での手続上の期限設定(停止決定でも侵害認定でもない)」へ移る。請求内容・OpenAI応答の骨格は維持 |
| openai | M3(δ) | 同一 | **軽微** | 初回B3(M2と共有)がそのまま最終Brief。骨格同一。冒頭に「すべて[UNVERIFIED]の候補情報」注記と末尾に【時点の制限】が付く(内容変化でなく注記) |
| central | M0 | F002,F003,F006,F008,F010 | 基準 | 「FRBが9/16に0.25pt利上げ、住宅ローン金利上昇は債券市場など複数要因、既存借り手への影響は固定・変動で異なる」 |
| central | M0b(γ) | F002,F003,F007,F008,F010 | **軽微** | 骨格同一。F006がF007(AP報道の30年固定5.98%→7.40%・月額約376ドル増の試算)に替わり、Storylineに「新規借入の月額負担増の試算」が加わる。**自然ばらつきの基準=軽微** |
| central | M1(δ) | F001,F002,F003,F006,F008 | **軽微(中程度寄り)** | 骨格(利上げ→ローン金利→借り手の契約条件差)は同じ。F001(「直近の完了済み決定」の特定)を追加し、F010(債券市場など複数要因)を落とすため、「複数要因」の論点が「直接効果とは断定しない」の留保に置換される。M0b差と同程度の1Fact入替だが論点が1つ落ちるため境界 |
| central | M2(α) | F002,F003,F006,F008,F010 | **軽微** | Fact集合・Storylineは実質M0と同じ(Jaccard 1.0)。Briefの先頭に「すべて[UNVERIFIED]の選定候補〜独立検証が必要」の注記 |
| central | M3(β) | 同上 | **軽微** | M2とBrief全文同一(共有初回B3、再選定・確認パス0回)。M2↔M3の差=0(B3出力が同一のため) |

- 事前登録ルール適用: 3記事ともM0-M0b差=軽微。方式差の最大は streaming M3・openai M2が中程度、その他は軽微(自然ばらつきと同程度)。→ 方式効果として扱えるのは streaming M3・openai M2のみ(n=1)。それ以外は「自然ばらつきを超える構成差は観測されない」。
- 1aとの違い(事実): 1aでは「Verifier verdictがB3入力に含まれる/含まれない」差でCoffee M3=重大、inbound M1〜M3=中程度が出たが、1bでは**重大は0件**、中程度は2件(streaming M3、openai M2)。
- M2↔M3の差(R-B5): openai M2(γ)とM3(δ)はFact集合が同一なのにBriefが異なる。これは「同じ初回B3から、M2は確認B3を呼び、M3は呼ばなかった」ことによる差で、M3の「検索上限」の効果ではない。centralのM2/M3はBrief全文同一(差0)。

## 3. 品質一対比較(M0 vs 各方式、構成差とは別列、n=1・単一評価者)

| 記事 | 方式 | 面白さ | 一貫性 | 事実との整合 | 理由(1行) |
|---|---|---|---|---|---|
| streaming | M0b | 同等 | 同等 | 同等 | F01(AMBIGUOUS)を採用したが範囲限定文(2026-10-08までのWeb調査、世界全体で最新と断定しない)あり。冒頭が調査メタ文で硬い |
| streaming | M1 | 同等 | 同等 | 同等 | F04(AMBIGUOUS)に【留保必須】、理由の記述はReutersの無回答事実で具体化。F07を採用しVERIFIED扱い(§5) |
| streaming | M2 | 同等 | 同等 | 同等 | F04のAMBIGUOUSを明示し旧価格を留保。結論が長く留保が多い |
| streaming | M3 | **悪い(軽度)** | 同等 | 同等(全選定VERIFIED。ただし§5の参考基準ではF04が他3run[M0p/M1/M2]でAMBIGUOUS) | 論点の「会社の理由」が落ち、旧新料金の整理が中心になる。Brief内に「最新性の再確認・会社説明のFact化が必要」という執筆者向けの不足指摘が入る |
| openai | M0b | 同等 | 同等 | 同等 | 同一Fact・言い換えのみ |
| openai | M1 | 同等 | 同等 | 同等 | F8のAMBIGUOUS(2026-10-18時点の手続状況が更新済み)を「同日以後は未確認、現在も同じ段階とは断定しない」と留保。M0の「後日の手続状況は別途確認が必要」と同水準以上 |
| openai | M2 | **良い(軽度)** | 同等 | 同等 | 手続の進展(停止是非を巡る命令・期限)まで含み新鮮。ただしその情報はVerifier補足由来でLedger Factとして再検証されていない(新事実の持込リスクは本評価では判断せず注記) |
| openai | M3 | 同等 | **悪い(軽度)** | 同等 | Briefに「すべて[UNVERIFIED]の候補情報」「候補F2によれば」が残るが、最終verdictは全VERIFIED=Briefと検証状態が不整合(内容の誤りはなく保守側) |
| central | M0b | **良い(軽度)** | 同等 | 同等 | 40万ドルのローンで月額約376ドル増という具体試算(F007)があり身近。「全借り手の実際の支払増ではなく9月利上げだけの増加でもない」と限定済み |
| central | M1 | 同等 | 同等 | 同等 | F001で「直近の完了済み決定」を特定する点は丁寧だが、複数要因(F010)が落ちる |
| central | M2 | 同等 | **悪い(軽度)** | 同等 | Briefに「すべて[UNVERIFIED]」注記が残るが最終verdictは全VERIFIED(openai M3と同型) |
| central | M3 | 同等 | **悪い(軽度)** | 同等 | M2とBrief全文同一のため同判定 |

- 良い/悪いの数(M0比、3記事×4方式=12セル): 悪い(軽度)は 一貫性3(openai M3、central M2、central M3)+面白さ1(streaming M3)、良い(軽度)は面白さ2(openai M2、central M0b)。**事実整合は12セル全て同等**(重大な悪化なし)。M0b(自然ばらつき)でも面白さの良い1件が出るため、「良い」2件は方式固有の利点と言い切れない。
- 注(新規観測): 一貫性「悪い」3件は同型で、M2/M3が**追加B3(再選定・確認パス)を一度も呼ばなかったセル**では、初回B3(検証前に生成)のBriefが最終Briefとして残り、「すべて[UNVERIFIED]の選定候補」注記が検証済み(全VERIFIED)の状態と矛盾したまま残る。1aのinbound旧M2/M3(2セル、ラベルと包括注記)と同系統で、1b新設計列10セル(Coffee2+inbound c2+1b6)中3セル(openai M3、central M2、central M3)。「【独立検証前の編集仮説】」ラベルそのもの(OPEN-411)は0件。この注記は内容を誤らせる方向ではなく保守側だが、Writerが「未検証」と読み誤る可能性がある。除去・書換えはB3 Prompt変更=Production挙動の意味的変更でありユーザー判断領域のため、本評価では測定・記録のみ(OPEN-411に関連する新規観測としてFableへ報告)。
- 注: M0/M0bが「M0b自身の自然ばらつき」の範囲(構成差軽微)であることを考慮すると、品質の悪い(軽度)は方式差というよりB3出力の生成ばらつき+注記由来であり、一般化できない(n=1)。

## 4. 中心FactのAMBIGUOUS断定(R-07、測定のみ、全方式同一基準)

機械抽出(RESULTS各記事「機械チェック」)の「中心AMBIGUOUS」は緩いヒューリスティックで過大計上があり、原文で人手判定した。基準は全方式同一(1a・補正評価と同じ): 当該方式の最終verdictがAMBIGUOUS(またはREJECTED)の中心Factについて、Verifierの指摘する不確実性がStoryline/Briefに反映され、無条件に確定値として断定されていないか。ラベル「【独立検証前の編集仮説】」「[UNVERIFIED]」の包括注記は留保に数えない(追補-1(b))。

| 記事 | 方式 | 対象Fact(最終verdict) | 判定 | 原文引用 |
|---|---|---|---|---|
| streaming | M0 | F07(AMBIGUOUS) | **留保あり** | Brief「確認したDisney+米国価格ページとReuters記事では、今回の値上げ理由を明示した記述は確認できない。未確認の別の顧客通知等で説明された可能性までは否定せず」。Storyline「確認資料では会社が示した値上げ理由を特定できない」(資料範囲に限定) |
| streaming | M0b | F01,F07(AMBIGUOUS) | **留保あり** | F01: Brief「【対象の限定】『最新』は、2026年10月8日までの今回のWeb調査で確認できた主要な米国向けサービスの発表の範囲。世界全体で最新とは断定しない」。F07: 「今回確認したDisney+米国価格ページとReuters報道では特定できない。未確認の顧客通知などに説明がある可能性までは否定せず」 |
| streaming | M1 | F04(AMBIGUOUS) | **留保あり** | Brief「Premium広告なし年額【留保必須】：改定前の公式申込ページには189.99ドル、現行の公式価格ページには214.99ドルと掲載。別時点の公式ページの照合に基づく情報であり、同一発表による年額改定が確定したとは断定しない」(F07はVERIFIED扱い) |
| streaming | M2 | F04(AMBIGUOUS) | **留保あり** | Storyline「年額の旧価格には留保があり」、Brief「新価格214.99ドルは確認済み。旧価格189.99ドルからの改定とされるが、旧価格は引用された公式ページだけでは再確認できず…この留保を付けて扱う」 |
| streaming | M3 | (中心AMBIGUOUSなし。選定全VERIFIED) | 該当なし(0) | F07はREJECTEDで除外。Briefは「採用可能なLedger項目に理由の記載がないことを…結論に置き換えない」 |
| openai | M0 | (選定全VERIFIED) | 該当なし(0) | Storyline「確認範囲は2026年10月8日の提訴段階で…」、Brief F8「後日の手続状況は別途確認が必要」 |
| openai | M0b | (選定全VERIFIED) | 該当なし(0) | Brief F8「その後の手続状況は別途確認が必要」 |
| openai | M1 | F8(AMBIGUOUS) | **留保あり** | Brief「同日以後の手続状況は未確認で、現在も同じ段階にあるとは断定しない」 |
| openai | M2 | F8(AMBIGUOUS) | **留保あり** | Brief「『提訴段階』は10月8日当日の説明に限定し、その後に手続上の命令が出ていることを落とさない」(10/15命令・10/30・11/6期限を記載、停止決定でも侵害認定でもない) |
| openai | M3 | (選定全VERIFIED) | 該当なし(0) | Brief【時点の制限】「F7・F8は同日以降の応答や手続更新を確認するものではない。現在の手続状況…を掲載する前に、最新の裁判所記録・報道を確認する」 |
| central | 全5方式 | (選定全VERIFIED) | 該当なし(0) | 全Factが全方式でVERIFIED |

- **件数(断定=確定条件・Verifier指摘を無視した無条件断定)**: 1b 3記事×5方式=15セルで**全て0件**。留保あり: streaming M0=1(F07)/M0b=2(F01,F07)/M1=1(F04)/M2=1(F04)/M3=0、openai M1=1(F8)/M2=1(F8)、その他0。
- 判定NG(「確定条件は満たしたが断定が残った」)=0件(Trial後のユーザー判断候補としてのR-07 NGなし)。1aの旧inbound M2/M3の断定(各1)は確認パス後のM2c/M3cで0(補正済み)。5記事全体では 新設計列(Coffee M2/M3,inbound M2c/M3c,1b M2/M3=10セル)のR-07断定=**0件**、M1(5セル)=1件(Coffee M1のF07=1aで断定と判定済み。同一基準の1a判定を変更しない。他4セルは留保ありまたは該当なし)。参考: 1aのCoffee M0・M0bも各1件。
- 参考(他run verdict基準での読み直し。方式固有ではなくVerifierばらつきの影響): streaming F04は M0p/M1/M2 でAMBIGUOUS・M0/M0b/M3でVERIFIED。この厳しい側の基準では、F04を無留保で記述した M0・M0b(β)・M3(γ)の3セルが「他runではAMBIGUOUS相当の事実を無留保で記述」に当たる(各方式の自verdictではVERIFIED=上表の判定は不変)。同様にopenai F8は M1/M2でAMBIGUOUS・M0/M0b/M3でVERIFIEDだが、M0/M0b/M3のBriefも「後日の手続状況は別途確認が必要」等の留保を持つため0。
- REJECTED Factの混入: 全15セルで**選定FactにREJECTED=0**(機械`rejected_in_sel`空)。Storyline/Briefへの混入も原文で0。参考: streaming F07は M3でREJECTED・他でVERIFIED/AMBIGUOUS。M3の判定「理由は特定できない」への反証(別報道でDisneyが技術投資に言及)がM3のVerifierに見えているが、M0/M1/M2のBriefは資料範囲限定+「否定せず」の書き方で、REJECTED相当の断定には至っていない。
- 0でない方式が1bにない(1bの断定=0)ため、1bに限ればR-07はユーザー判断事項を生まない。

## 5. Verifier再現性の整理(判定ではなく事実整理)

条件: M0=既存run(上限なし)、M0b=M0のLedger再利用、M0p=1b streamingのみ同日上限なし再検証、M1=同日上限付き(Prompt内ソフト上限3)全Fact再検証、M2/M3=選定Factのみ検証(「-」は未検証)。Verifier model=全run gpt-6-luna、各セルn=1。出典=各`_analysis_1b_a*.json`のverdict_tableと`_work/verify_*.json`のnotes。

| 記事 | Fact | M0 | M0b | M0p | M1 | M2 | M3 | 既知欠陥/備考 |
|---|---|---|---|---|---|---|---|---|
| streaming | F01 | AMBIGUOUS | AMBIGUOUS | **REJECTED** | **REJECTED** | AMBIGUOUS | AMBIGUOUS | 「最新の発表」の網羅性。M0p/M1は後発のDiscovery+(10/13)・Disney+英国(10/14)を理由に不適切と判定 |
| streaming | F04 | VERIFIED | VERIFIED | AMBIGUOUS | AMBIGUOUS | AMBIGUOUS | VERIFIED | 年額旧価格189.99ドルが提示URLだけでは再確認不能 |
| streaming | F07 | AMBIGUOUS | AMBIGUOUS | VERIFIED | VERIFIED | VERIFIED | **REJECTED** | **既知欠陥(登録済み)**: 「会社の理由は特定できない」は資料範囲の限定がないと不完全(別報道でDisneyが技術投資を説明)。M0=AMBIGUOUS、M3=REJECTED、M0p/M1/M2=VERIFIED(M0p・M2のnotes自身が別報道の存在に言及しつつVERIFIED) |
| openai | F8 | VERIFIED | VERIFIED | - | AMBIGUOUS | AMBIGUOUS | VERIFIED | 10/15に停止是非を巡る命令・期限が出ており「提訴段階」は更新が必要(M1/M2のnotes)。M3のnotesも更新を指摘しつつVERIFIED |
| central | F001〜F011 | 全VERIFIED | 全VERIFIED | - | 全VERIFIED | (選定5のみ全VERIFIED) | (同左) | 方式間の遷移0 |

- 方式間でverdictが揺れたFact: streaming 3/7(F01,F04,F07)、openai 1/8(F8)、central 0/11。F07は4値の揺れ(VERIFIED×3/AMBIGUOUS×2/REJECTED×1)。
- **既知誤判定の記録(原因・影響・最終採用の有無、今回Production Verifierの改修は行わない)**:
  - Coffee F12(BLS前月比-0.3%は季節調整済みだが下書きは未調整と誤記): 1aでM0=AMBIGUOUS、M0p/M1=VERIFIED(下書きの「季節調整前」を追認)。原因=Verifier判定の再現性(M0pの上限なしでも昇格するため上限の有無によらない)。影響=M0〜M3全方式で未選定(c_not_selected)のため実害なし。最終採用=なし。
  - inbound F12(2025年6月20日の資料を2026年の政策資料とする時期誤り): M0/M0p=REJECTED、M1のみVERIFIED。原因=判定のばらつき(上限付きの1回のみ昇格、上限の効果かサンプリングのばらつきかは本データで切り分け不能)。影響=全方式で未選定のため実害なし。最終採用=なし。
  - **1b新規: streaming F07(登録済み既知欠陥)**: M1・M2が選定し、VERIFIEDとして通過(機械記録`known_defect_status`=b_selected_missed_NG、M0p=VERIFIEDも同方向)。M0はAMBIGUOUSとして留保付きで採用(a_selected_detected)、M3はREJECTEDで除外(c_not_selected)。原因=Verifierが「資料範囲を限定した記述なら正確」とVERIFIED側に倒れる判定ばらつき(M0p・M2のnotes自身が別報道の存在を認めたうえでVERIFIED)。影響=M1・M2の最終BriefはF07を「確認した資料の範囲」「未確認の通知等の可能性は否定せず」の限定付きで記述しており、誤った無条件断定には至っていない(§4)。最終採用=M1・M2ではF07を採用(限定付き)。受入条件1は「条件付」(§6)。
- AMBIGUOUS/REJECTED→VERIFIED昇格(1b): streaming F07(M0p,M1,M2)。M0p(上限なし、基準)でも発生のため、上限付き固有ではない。VERIFIED→AMBIGUOUS降格: streaming F04(M0p,M1,M2)、openai F8(M1,M2)=いずれも根拠notesあり(旧価格の再確認不能、10/15の手続更新)。ただし同じFactをM3(F04,F8とも)・M0(F04,F8とも)はVERIFIEDとしており、降格の再現性は方式間で一致しない。
- **上限付き(M1)と上限なし(M0p)の同日対比(1a+1b、Ledger検証stepの実測費用・呼出)**: coffee M0p 17.996/10呼出・M1 23.315/13、inbound 24.726/14・19.769/11、streaming 10.863/6・9.346/5(出典=各result.json cost.by_step)。3記事合計 M0p 53.585/30呼出 → M1 52.430/29呼出(-2.2%、-1呼出)。coffeeはM1が上回り(+29.6%)、inbound・streamingは下回る(-20.0%/-14.0%)=**符号が割れる**。openai・centralはM0pが無いため同日対比できない。
- 件数が少なく各セルn=1のため、上限付きが緩い方向に偏るか(昇格が増えるか)は統計的に主張できない。

## 6. 受入条件(元指示§7)の5記事判定表

出典: ユーザー原指示`2026-10-17_..._TRIAL-01_USER.md` §7(L114以降)。5記事=Coffee・inbound(1a、補正後)+streaming・openai・central(1b)。方式=M1/M2/M3(新設計列、inbound=M2c/M3c)。評価者単一・n=1/記事。凡例: 充足/条件付/不充足。

| 受入条件 | Coffee | inbound | streaming | openai | central | 根拠path |
|---|---|---|---|---|---|---|
| 1 採用Factに重大誤りが残らない | M1/M2/M3 充足(M1はF07=AMBIGUOUS検出のまま採用、M2/M3は除外) | M1 条件付(F05留保付き採用、F12は未選定だが昇格) / M2c,M3c 充足(F05断定0) | M0b・M3 充足 / **M1・M2 条件付**(既知欠陥F07をVERIFIEDで通過[b_selected_missed_NG]、Briefは限定付き) | 充足(既知欠陥登録なし、F8のAMBIGUOUSは留保付き) | 充足(全VERIFIED) | `STAGE_1A_EVAL_01.md` §6、`STAGE_1A_CORRECTION_01.md` §3、本書§4・§5、`_analysis_1b_a1.json` known_defect_status |
| 2 既存VERIFIED降格は根拠付き | 充足(M0pのF02のみ、notes有) | 充足(降格0) | 条件付(F04の降格3run[M0p/M1/M2]にnotes有、M3・M0はVERIFIEDで再現せず) | 条件付(F8の降格M1/M2にnotes有[10/15の更新]、M3・M0はVERIFIED) | 充足(遷移0) | 本書§5、各`_work/verify_*.json` |
| 3 不確実FactをVERIFIEDに昇格させない(遷移0) | **不充足**(M1:F12,F16,F17、M0pもF12,F17) | **不充足**(M1:F04,F12。M2c/M3c:F04。M0pもF04) | **不充足**(F07:M0p,M1,M2) | 充足(昇格0) | 充足(昇格0) | 本書§5、`STAGE_1A_EVAL_01.md` §5。厳密基準(遷移0)は上限なしのM0pでも満たされない=基準自体のばらつき込み |
| 4 最終B3ストーリー品質維持 | 条件付(構成差M1/M2中程度・M3重大、品質同等〜良い) | M1 条件付(事実整合軽度悪い) / M2c,M3c 条件付(旧M2/M3比で改善、M0との一対比較は補正評価で未実施) | M1,M2 充足 / **M3 条件付**(構成差中程度、面白さ悪い軽度) | M1 充足 / M2 充足(中程度、面白さ良い軽度) / **M3 条件付**(Briefの[UNVERIFIED]注記残存、一貫性悪い軽度) | M1 充足 / **M2,M3 条件付**([UNVERIFIED]注記残存、一貫性悪い軽度) | 本書§2・§3、`STAGE_1A_CORRECTION_01.md` §4・§5 |
| 5 再選定・追加検証込みの実測総費用で削減 | M1 条件付(+4.1%、M0b -3.1%に近接)/M2 充足(+7.7%)/M3 充足(+11.2%) | M1 充足(+10.5%)/M2c 充足(+14.1%)/M3c 充足(+10.7%) | M1 充足(+6.9%)/**M2 不充足**(-29.1%)/**M3 不充足**(-13.8%) | **M1 不充足**(-7.4%)/**M2 不充足**(-30.1%)/**M3 不充足**(-20.5%) | **M1 不充足**(-7.8%)/M2 充足(+7.8%)/M3 充足(+13.5%) | `aggregate_final_5_13.md` 表1(本番換算、確認パス・再選定費用込み) |
| 6 Fact Lock・RF等の既存品質要件 | 充足(全方式PASS) | **不充足**(M0b/M1/M2/M3/M2c/M3c FAIL=OPEN-407 d_tags。M0のみPASS。方式固有ではなくFact選定内容依存) | 充足(全6方式PASS) | 充足(全5方式PASS) | 充足(全5方式PASS) | `STAGE_1A_RESULTS_01.md` §6、`STAGE_1B_RESULTS_01.md` 各「方式別結果」契約列、`_conform_check_1b_a*.json` |
| 7 5記事全体の傾向と例外が説明できる | 条件付 | 条件付 | 条件付 | 条件付 | 条件付 | 下記「5記事の方式別総括」で説明した(傾向=確認パス・再選定の有無と記事ごとのM0のLedger費用の大小で符号が決まる、例外=openai・inbound旧設計)。ただし要因分解は1標本ずつの観察でn=5では確定できないため記事別は一律「条件付」 |

5記事の方式別総括(新設計列、本番換算、`aggregate_final_5_13.md` 表3): M1 +2.9%(+6.765 JPY、記事別 -7.8〜+10.5%、符号+++--)/ M2 -3.2%(-7.333、-30.1〜+14.1%、++--+)/ M3 +1.7%(+3.954、-20.5〜+13.5%、++--+)。M0b(自然ばらつきの基準) -1.6%(-3.784、記事別-3.1〜+0.2%)。いずれの方式もM0b幅を超える一様な削減はなく、記事ごとに符号が分かれる。
- 傾向: 費用が下がる記事は「選定Factが全てVERIFIED(確認パス・再選定0回)」(central M2/M3、Coffee M2/M3[再選定1回でも安価])と、inbound(M0のLedger費用が高い記事)。上がる記事は「AMBIGUOUS選定→確認パスまたは再選定が1回発生」(streaming M2/M3、openai M2)と、openai M3(確認パス0回でも検索9呼出で検証費用がM0の記事単位Ledger費用を上回る)。
- 例外: openaiはM0のLedger費用(9.01 JPY、検索5呼出)が小さく、どの方式も上回る。inboundは旧設計(確認パスなし)の-29%/-26%が補正後-14%/-11%に低下(確認B3約10 JPY)。
- 5記事の結果だけで重大Fact誤りの低頻度リスクまで統計的に否定できるとは扱わない(ユーザー§7末尾)。

## 7. 所見(判断はFable)

事実として:
1. 1bの人手評価で、R-07断定=0/15セル、REJECTED混入=0/15セル。事実整合の悪化は12セル中0。品質の悪い(軽度)は「M2/M3の[UNVERIFIED]注記残存」(3セル)と「M3のF07除外による論点欠落」(1セル)。
2. 新規観測: 追加B3を呼ばなかったM2/M3セルで、初回B3(検証前)の「[UNVERIFIED]」注記が最終Briefに残る(1b新設計6セル中3、1a旧inbound M2/M3の2セルを含めると過去12 M2/M3セル中5)。ラベル(【独立検証前の編集仮説】)件数は1b全方式0。対応(除去・文言変更)はB3 Prompt変更=ユーザー判断(OPEN-411の関連観測。Trialでは変更しない)。
3. 登録済み既知欠陥streaming F07を、M1・M2がVERIFIEDで通過させた(b_selected_missed_NG)。Briefは限定付きだが、受入条件1は「条件付」。M0p(上限なし基準)もVERIFIEDで同方向。
4. 案1の上限3回: ソフト上限超過request=1b全方式0件(1a含め全0)、calls/Factの平均は0.36〜0.77(M1)・0.4〜1.8(M3の検証step、うちopenaiが1.8)、M0p(上限なし)は0.59〜0.93。上限が拘束した証拠はなく、同日対比(M0p→M1のLedger step)は-2.2%で符号が割れる。→「検索削減=上限の効果」とは断定できない。
5. 任意A(Fable決定=streaming_price打切り): Coffee3件+inbound3件=6件×{上限なし,上限付き}で検出漏れ0(注入6件全てがREJECTED、またはinbound F05[弱い注入]のAMBIGUOUS、VERIFIED通過0)。streaming_priceは残枠21.774に対しinbound実績21.344で超過リスクのため**未実施**(任意A上限54の引上げはユーザー予算変更に当たるため行わない)。限界: n=6、inbound F05は本文が元のまま見出し句のみ改変した弱い注入でAMBIGUOUS(REJECTEDではない)、streamingでの検出力は未確認。
6. 判断候補(Fable判定用、提案のみ): (a)案別の最終分類(草案は`TRIAL_FINAL_REPORT_DRAFT_01.md`)。(b)「[UNVERIFIED]注記の残存」を新規OPENとして起票するか、OPEN-411に追記するか(本書は追記・新規起票しない)。(c)Verifier再現性(F07の4値)を切り分けるには同条件の反復が必要だが有料のため未実施。

## 追補: 1bで適用した是正(TRIAL_DESIGN_03 §8)との対応
- §8-1 ラベルのマスク: packet生成時に「【独立検証前の編集仮説】」を置換(実質0件)。R-07は留保に数えない。ラベル件数(方式別)は全て0(M0 0/M0b 0/M1 0/M2 0/M3 0、3記事共通。鍵`masked_occurrences`と各result.jsonのgrepで確認)。
- §8-2 R-07全方式同一基準: 文字列検査は不使用。人手で全方式同基準。
- §8-3 M2c↔M3cの差: openai M2/M3(Fact同一で確認B3の有無)はB3揺らぎ・確認B3の有無の差として扱い、案1上限の効果としない。
- §8-4 unmetの内訳: 1b全方式`unmet=null`(UNRESOLVED 0、REJECTED_SELECTED/AMBIGUOUS_NOT_CONFIRMEDとも0)。「確定条件のもとでの成立率」は案2系のみの指標: 1b 6/6、1a(Coffee M2/M3+inbound M2c/M3c)4/4=新設計列10/10。
- §8-5 新設計列: 本評価・集計はCoffee M2/M3+inbound M2c/M3c+1b M2/M3を新設計列とし、旧inbound M2/M3は参考行のみ。

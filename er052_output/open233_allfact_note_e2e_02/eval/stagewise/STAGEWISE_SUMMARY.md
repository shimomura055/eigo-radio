# STAGEWISE_SUMMARY: 工程別NG比較表(OPEN-233-E2E-STAGEWISE-NG-AUDIT-01 委任_C1、2026-10-07、¥0)

既存成果物(3系統のNG台帳・stagewise_*.json)の再集計のみ。API呼び出し・記事生成・Production変更なし。重大/軽微の判定は各台帳(Sonnet実行層の単独判定)に従い、本表では再判定していない。対象は従来版(control)5本(meta/hormuz/sewer/ai_control/space_weapons 各rep1)とP2版10本(各テーマrep1/rep2)。

## 0. 定義注記

- 重大NG: 事実の意味が変わり読者に誤った理解を与える。軽微NG: 意味は逆転しないが不正確・過剰断定・曖昧・軽い具体化。同一誤りは同一工程1件(JA/EN共通でID共有)。
- ① JA最終稿(ja_writer/revision2.md)、② EN Rewrite前(b1b/article.md)、③ EN Rewrite後(Checker最終cycleのen_text_after_rewrite。Rewriteなしは②と同一)、④ Checker最終cycleの生件数(blocking=重大相当、non_blocking=軽微相当)、⑤ 独立評価。
- 3系統で⑤の定義が不統一(meta/hormuzは「EN最終のみ」、sewer/ai_control/space_weaponsは「EN最終+JA残存の和集合」)だったため、全NG台帳のng_items(stages)から再計算して統一した。**⑤a = EN最終(③テキスト)に残存するNG**。**⑤b = ⑤a + JAのみ残存(①で発生し、ENではRewrite等で修正済み・ENに該当文なし)**。⑤bは、Checkerの評価対象(英語のみ)外であるJA側の残存を含む、読者視点(JA/EN両方)の最終残存。
- **④は⑤と同質でない**: ④のnon_blockingは、正しい文へのACCEPTABLE指摘や決定論検査(negation_polarity_mismatch等)の誤検知を多く含む「候補の生件数」であり、⑤の軽微(実NG)とは比較できない。④のblockingは全記事の最終cycleで0(RESOLVED系で終了したため)。④は主表に参考として併記するが、NG実数の比較には用いない。
- 「Checker見逃し」(④→⑤): 最終cycleのblockingが0のため、⑤aに残ったNGは全て「BLOCKINGにならなかったもの」。内訳は台帳のchecker_labelで分類: 検出済み非BLOCKING(ACCEPTABLE/QUALITYで指摘あり)/未検出(未検出と明記、または最終cycleで非掲出=中間cycleでのみ検出を含む)/JAのみ残存(Checker対象外)。分類は台帳ラベルの機械的適用であり、境界ケースがある(3節注)。
- 評価対象がない工程: ④はNGの実数ではなく生件数のため、NG件数としての比較対象外。sewer 3runはRewriteなしのため③=②。

## 1. 主表(件数合計)

| 評価段階 | 従来版5本 重大 | 従来版5本 軽微 | P2版10本 重大 | P2版10本 軽微 |
|---|---|---|---|---|
| ① JA最終稿 | 0 | 18 | 4 | 49 |
| ② EN Rewrite前 | 0 | 21 | 5 | 56 |
| ③ EN Rewrite後(最終EN) | 0 | 19 | 1 | 52 |
| ④ Checker最終cycle生件数(blocking/non_blocking。NG実数ではない) | 0 | 52 | 0 | 99 |
| ⑤a EN最終残存 | 0 | 19 | 1 | 52 |
| ⑤b ⑤a+JAのみ残存 | 0 | 21 | 4 | 57 |

## 2. 記事別表(15本。重大 / 軽微)

| 記事 | ① | ② | ③ | ④(参考) | ⑤a | ⑤b |
|---|---|---|---|---|---|---|
| meta 従来版 rep1 | 0 / 3 | 0 / 4 | 0 / 3 | 0 / 7 | 0 / 3 | 0 / 4 |
| meta P2 rep1 | 0 / 4 | 0 / 5 | 0 / 4 | 0 / 8 | 0 / 4 | 0 / 5 |
| meta P2 rep2 | 1 / 5 | 1 / 6 | 1 / 6 | 0 / 11 | 1 / 6 | 1 / 6 |
| hormuz 従来版 rep1 | 0 / 1 | 0 / 1 | 0 / 1 | 0 / 1 | 0 / 1 | 0 / 1 |
| hormuz P2 rep1 | 0 / 8 | 0 / 8 | 0 / 7 | 0 / 7 | 0 / 7 | 0 / 8 |
| hormuz P2 rep2 | 0 / 8 | 0 / 8 | 0 / 6 | 0 / 7 | 0 / 6 | 0 / 8 |
| sewer 従来版 rep1 | 0 / 7 | 0 / 7 | 0 / 7 | 0 / 16 | 0 / 7 | 0 / 7 |
| sewer P2 rep1 | 0 / 4 | 0 / 6 | 0 / 6 | 0 / 14 | 0 / 6 | 0 / 6 |
| sewer P2 rep2 | 0 / 4 | 0 / 6 | 0 / 6 | 0 / 14 | 0 / 6 | 0 / 6 |
| ai_control 従来版 rep1 | 0 / 3 | 0 / 5 | 0 / 5 | 0 / 22 | 0 / 5 | 0 / 5 |
| ai_control P2 rep1 | 1 / 5 | 2 / 5 | 0 / 5 | 0 / 16 | 0 / 5 | 1 / 5 |
| ai_control P2 rep2 | 0 / 6 | 0 / 6 | 0 / 6 | 0 / 9 | 0 / 6 | 0 / 7 |
| space_weapons 従来版 rep1 | 0 / 4 | 0 / 4 | 0 / 3 | 0 / 6 | 0 / 3 | 0 / 4 |
| space_weapons P2 rep1 | 0 / 1 | 0 / 2 | 0 / 2 | 0 / 9 | 0 / 2 | 0 / 2 |
| space_weapons P2 rep2 | 2 / 4 | 2 / 4 | 0 / 4 | 0 / 4 | 0 / 4 | 2 / 4 |

検算: 記事別表15行の合計 = 主表(従来版5行・P2版10行): 全工程で一致。ng_itemsからの再計算値と各JSON記載の①②③件数: 全15本で一致。JSON記載の遷移(①→②新規/②→③修正/②→③新規): 全15本で一致。各記事JSON記載の⑤件数: meta/hormuz系は⑤a、他系統は⑤bと一致(全15本)。

## 3. 遷移表(合計。重大 / 軽微)

| 遷移 | 従来版5本 重大 | 従来版5本 軽微 | P2版10本 重大 | P2版10本 軽微 |
|---|---|---|---|---|
| ①→② 英語化(JA→EN)で新規発生 | 0 | 3 | 1 | 7 |
| ②→③ Rewriteで修正(最終ENで解消) | 0 | 2 | 4 | 5 |
| ②→③ Rewriteで新規発生: 最終ENに残存 | 0 | 0 | 0 | 1 |
| ②→③ Rewriteで新規発生: loop内で修正済みの一時発生 | 0 | 0 | 1 | 0 |
| ④→⑤ Checker見逃し合計(⑤b。⑤a+JAのみ残存) | 0 | 21 | 4 | 57 |
| 　内訳 検出済みだが非BLOCKING(ACCEPTABLE/QUALITY) | 0 | 14 | 0 | 41 |
| 　内訳 未検出(最終cycle非掲出を含む) | 0 | 5 | 1 | 11 |
| 　内訳 JAのみ残存(Checker対象外) | 0 | 2 | 3 | 5 |

注: ②→③「Rewrite新規発生・最終残存」は ai_control P2 rep2 の ai-p2r2-08(EN欠落、軽微、Checker未検出)。「loop内一時発生」は ai-p2r2-07(Rewriteが無関係文へ置換、重大、cycle2のBLOCKINGで検出し修正済、OPEN-238関連。置換元の文は台帳(EVID-008)整合だったが、Checker側のprecheck floorがEVID-006/CONTROL-004へ誤紐付けしてBLOCKING化したことが原因、A2所見・未検証)。
注: ①→②の新規発生は「JA側に対応文が存在しない」ものに限る(JAに弱い形で既存しENで強まったものは同一ID扱い)。「未検出」のうち sw-ctl-01/04・meta-p2r2-03・meta-c-04・hor-p2r2-03 は、中間cycleではACCEPTABLE等で検出されたが最終cycleでは非掲出。meta-p2r2-02(重大)は初回BLOCKING→Rewrite後に残った文が未検出(cycle3のACCEPTABLEは別文)として未検出に計上。hor-p2r2-04は「03と同一文のみ」のラベルどおり検出済みに計上(機械分類の限界、03と同じく最終cycle非掲出の可能性あり)。

## 4. 1記事当たり平均(件/記事)

| 区分 | 記事数 | ① 重大 / 軽微 | ⑤a 重大 / 軽微 | ⑤b 重大 / 軽微 |
|---|---|---|---|---|
| 従来版 | 5 | 0.0 / 3.6 | 0.0 / 3.8 | 0.0 / 4.2 |
| P2版 | 10 | 0.4 / 4.9 | 0.1 / 5.2 | 0.4 / 5.7 |

テーマ別(従来版1本 vs P2版2本の平均。重大 / 軽微):

| テーマ | 従来版 ① | 従来版 ⑤a | 従来版 ⑤b | P2版 ① | P2版 ⑤a | P2版 ⑤b |
|---|---|---|---|---|---|---|
| meta | 0.0 / 3.0 | 0.0 / 3.0 | 0.0 / 4.0 | 0.5 / 4.5 | 0.5 / 5.0 | 0.5 / 5.5 |
| hormuz | 0.0 / 1.0 | 0.0 / 1.0 | 0.0 / 1.0 | 0.0 / 8.0 | 0.0 / 6.5 | 0.0 / 8.0 |
| sewer | 0.0 / 7.0 | 0.0 / 7.0 | 0.0 / 7.0 | 0.0 / 4.0 | 0.0 / 6.0 | 0.0 / 6.0 |
| ai_control | 0.0 / 3.0 | 0.0 / 5.0 | 0.0 / 5.0 | 0.5 / 5.5 | 0.0 / 5.5 | 0.5 / 6.0 |
| space_weapons | 0.0 / 4.0 | 0.0 / 3.0 | 0.0 / 4.0 | 1.0 / 2.5 | 0.0 / 3.0 | 1.0 / 3.0 |

N=従来版1本・P2版2本/テーマの小標本であり、差がNote由来かrun揺れかは判別できない。重大/軽微の判定は単独評価で人間確認なし。

## 5. 重大NG全件

### meta-p2r2-02(meta P2 rep2、fact MUSE-HC-012)
- 工程別: ①JA=発生 / ②EN前=発生 / ③EN後=残存 / ⑤=残存(判定: ⑤a=残存、⑤b=残存)
- 該当文: JA「ただし、主役になった人間が知らされていなかった。」「問題は、その事実を相手に十分知らせないまま、テストを始めたことでした。」/EN b1b「But the humans who ended up in the main role had not been told.」→Rewrite後「But the humans who ended up on the other end had not been properly told.」+「…without properly telling the person on the other end about this fact.」(開示されなかった対象の特定)
- Checker扱い: BLOCKING(cycle1)→rewrite後cycle3でACCEPTABLE。「telling the person on the other end」文は未検出(Rewrite: あり)
- 台帳注記: 台帳は「適切な開示なし」とだけ述べ対象を特定しない。JA/b1bは契約スタッフ本人が知らされていなかったと読め、開示不足の対象の取り違え。Rewriteは対象を「電話の相手側の人間」に置換しただけで、台帳外の対象断定は残存(同一誤りの形を変えた残存。新規発生としては数えない)。E_meta「対象1」と「追加(c)」を同一誤りとして統合

### ai-p2r1-01(ai_control P2 rep1、fact EVID-008)
- 工程別: ①JA=発生 / ②EN前=残存 / ③EN後=修正済 / ⑤=残存(判定: ⑤a=修正済・不在、⑤b=残存)
- 該当文: JA「いわば、厳重な監獄のはずが、裏口の鍵がかかっていなかった状態です。」/EN「In other words, it was like a heavily guarded prison whose back door had been left unlocked.」
- Checker扱い: BLOCKING(Rewrite: あり)

### ai-p2r1-02(ai_control P2 rep1、fact CONTROL-002)
- 工程別: ①JA=該当なし / ②EN前=発生 / ③EN後=修正済 / ⑤=該当なし(判定: ⑤a=修正済・不在、⑤b=修正済・不在)
- 該当文: EN(Rewrite前)「whether it tends to be used for harmful purposes」(JA「有害な目的で使う傾向があるか」は正しい。修正後EN「whether it tends to use that ability for harmful purposes」)
- Checker扱い: BLOCKING(Rewrite: あり)

### ai-p2r2-07(ai_control P2 rep2、fact EVID-006(無関係))
- 工程別: ①JA=該当なし / ②EN前=該当なし / ③EN後=RW新規→修正済 / ⑤=該当なし(判定: ⑤a=修正済・不在、⑤b=修正済・不在)
- 該当文: EN(Rewrite cycle1が挿入)「In a simulated safety evaluation, Claude Opus 4 attempted blackmail in 84% of rollouts.」
- Checker扱い: BLOCKING(Rewrite: あり)

### sw-p2r2-01(space_weapons P2 rep2、fact F-001)
- 工程別: ①JA=発生(JA R2に最終まで残存) / ②EN前=発生 / ③EN後=修正済(cycle1でEN「orbital space-control weapons」へ置換、cycle3で前文も置換) / ⑤=残存(JAのみ。EN最終は修正済)(判定: ⑤a=修正済・不在、⑤b=残存)
- 該当文: JA「宇宙、通信、地上の設備をまとめて守るための仕組みを、米国が公の言葉で認めたということです。」/ EN(Rewrite前)「It means that the United States has publicly acknowledged a system for protecting space, communications, and ground equipment together.」(認められたのは軌道上space control weapons配備。counterspace定義F-011を発表内容にすり替え)
- Checker扱い: BLOCKING(cycle1-3)(Rewrite: あり)

### sw-p2r2-02(space_weapons P2 rep2、fact F-001)
- 工程別: ①JA=発生(JA R2に最終まで残存) / ②EN前=発生 / ③EN後=修正済(cycle1でEN「the deployment of weapons in space ...」へ置換) / ⑤=残存(JAのみ。EN最終は修正済)(判定: ⑤a=修正済・不在、⑤b=残存)
- 該当文: JA「今回の見どころは、宇宙戦争が始まったことではありません。宇宙の戸締まりをするための備えが、初めて表に出たことです。」/ EN(Rewrite前)「It is that preparations to secure space have come into public view for the first time.」(「初めて」は兵器配備の承認に限定されるのに「防衛の備え」へ拡張)
- Checker扱い: BLOCKING(cycle1-2)(Rewrite: あり)

重大NGは全6件。

## 6. 判定保留・境界例

1. meta-p2r1-H1(meta P2 rep1): Rewrite挿入文「Some calls were handled by trained human contractors. That is what this polished system seemed to be like behind the scenes.」の「That」の指示対象が曖昧。事実の意味変化ではなく文章品質のため判定保留、集計に含めない。
2. sw-p2r2-03(space_weapons P2 rep2、「なぜ今→背景はロシアの対衛星能力」): 台帳にないF-001とF-002の因果を断定しており重大に寄る境界。後続段落でF-002が帰属付き・可能性付きで正しく書かれているため軽微と判定(軽微に計上)。
3. sw-ctl-04(space_weapons 従来版): 台帳のみを基準にすると軽微(「兵器の名前は分からない/確認されていない」)だが、従来版briefに「確認されていない」が入っていたため既存評価は「正しい」としていた。brief記載を根拠として認めるかで従来版軽微が3→4に変わる(ユーザー/PM判断事項。本表はsw-ctl-04を軽微として計上。除外すると従来版swの①〜③軽微が各1減る)。
4. ai-p2r1-07(ai_control P2 rep1): 「意外な主役はAIではなく舞台装置」/In one line「open doors and weak defenses played the bigger role」。軽微と判定、Fable要確認と注記あり(軽微に計上)。
5. ai-ctl-02(ai_control 従来版): 「AIが有害な行動を取る傾向まで実証された、という意味ではありません」→ 本事件で有害傾向が実証されなかったと読める。軽微と判定、Fable要確認と注記あり(軽微に計上)。
件数: 判定保留(集計外)1件(項目1)、境界例(軽微に計上)4件(項目2〜5)。計5件。
その他の留意: meta-p2r1-02は台帳上は軽微(「見えます/seemed」の印象表現で後続文が人間の担当を明示)だが、CheckerはBLOCKING扱い。space_weapons従来版は独立ledgerが見つからずP2 ledgerで代用(fact本文同一は既存評価で確認済み)。

## 7. 既存評価(E_*.md)との件数差の理由

- meta: P2 rep1はE_meta A節(Fact整合5件、最終EN残存4件)と同数、追加NGなし。P2 rep2はE_meta B節の最終残存8件(主体1/対象1/因果2/追加3/★曖昧1)に対し台帳③は7件。差=E「対象」とE「追加(c)」(いずれも開示対象の特定)を同一誤りとして1件に統合(meta-p2r2-02、重大はこの1件のみ)。従来版はE_meta C節(残存3件)と同数。
- hormuz: P2 rep1はE_hormuz A節8件(b1b)/残存7件と同数。内訳差=E「対象」と「因果(talks)」を統合(hor-p2r1-03)、E「対象」内の継続性示唆を分離(hor-p2r1-04)。P2 rep2はE_hormuz B節の最終残存8件に対し台帳③6件(②は8件)。差=E「因果(危険が消えなかったから高止まり)」はHF-009がCAUSAL_STATED_BY_SOURCEで危険継続を条件に記載するためNG非該当、E「因果(市場が思い出した)」は「seemed」付き比喩のためNG非該当(E_hormuz冒頭方針「比喩は事実誤りに数えない」準拠)。E「主体」3件は台帳01-03に対応(01-02はEN修正済)。従来版はE_hormuz C節の残存2件(範囲=「約」脱落/因果=「供給への心配が消えたわけではない」)のうち、因果はHF-009で許容されるためNG非該当とし1件。
- sewer: E_sewerの件数 P2 rep1=5/rep2=5(+R2→EN用語1)/従来版=6、本台帳 6/6/7。差=(1)E「範囲」2件を(a)(b)に分離し、R2→EN「better」を別計上(Eは(3)欄記載でNG一覧外)。(2)P2 rep1・従来版にE_sewerが言及のみだったF-001「都市下水路を除く」不記載を軽微として各1件追加(sewer-p2r1-06、sewer-ctl-07、本委任で追加)。(3)P2 rep2のEN「合併」消失(E (3)欄)をNG計上。重大は全runで0件(Eと整合)。
- ai_control: E_aiの件数 P2 rep1=6(+Rewrite前の主体1)/P2 rep2=4+Rewrite由来/従来版=5。本台帳は rep1=重大2(EN最終に残るのは0)+軽微5、rep2=重大1(一時)+軽微7、従来版=軽微5。差=(1)rep1は監獄比喩(範囲)と主体(propensity)を重大、ほか5件を軽微に再ラベルし、因果1件を-07に統合。(2)rep2はE台帳外(b)「敵を探す」=-01(軽微、EN修正済・JA残存)、(a)=-02、(c)=-03、因果=-04、本委任で追加=-05(単一AIが3組織へ+As a result)、-06(関連する評価=主体の曖昧)、E「重大な不具合」とした無関係文置換=-07(重大・一時・cycle2で修正)、同(3)のEN欠落=-08(軽微・③残存)。(3)従来版はE通り5件。
- space_weapons: 既存評価と同一のものは台帳の既存評価欄に記載(sw-ctl-01「台帳外追加(通信リンク)」等)。従来版sw-ctl-04は上記6-3(brief根拠)。sw-p2r1-02は本委任で追加(既存評価(3)に軽微として記載の語句の狭まり)。relabel_reasonのある項目(sw-ctl-02・sw-ctl-04・sw-p2r2-02/03/05)は本基準で重大/軽微を再ラベルしたもの。

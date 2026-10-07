# 工程別NG台帳: space_weapons(従来版 control rep1 / P2 rep1 / P2 rep2)

管理ID: OPEN-233-E2E-STAGEWISE-NG-AUDIT-01(委任_A3)。評価日: 2026-10-07。API呼び出し0円・新規生成なし・既存成果物の再評価のみ。Trial/DEV限定、Production変更なし。

## 0. 基準・工程・定義

- 重大NG: 事実の意味が変わり読者に誤った理解を与える(主体・対象の入れ替わり、方向・状態の逆転、台帳にない事実を断定して理解が変わる、否定の反転)。軽微NG: 意味は逆転しないが不正確・過剰断定・対象範囲の曖昧さ・台帳未提示事項の軽い具体化。表現だけで重大にしない。同一誤りは同一工程内1件、JA/ENの同一誤りはNG ID共有。
- 工程: ①JA最終稿(ja_writer/revision2.md) ②EN Rewrite前(b1b/article.md) ③EN Rewrite後(checker json の最終cycle en_text_after_rewrite、Rewriteなしなら②と同一) ④Checker最終cycleの判定(blocking_count=重大、non_blocking_count=軽微の生件数) ⑤独立評価=③ENと①JAに最終的に残るNG(IDの和集合)。
- ④は誤検知寄りの件も含むCheckerの生件数であり、NG台帳の実NG件数とは別物(実NGとの対応はng_itemsのchecker_label参照)。
- 台帳: `ledger/space_weapons/research_ledger/verified_fact_ledger.txt`(従来版のfact本文もP2と同一、差はnotes_for_writer行のみ。既存評価で確認済み)。
- 見逃し(④→⑤)の定義: 最終cycleでNGが未検出のまま最終稿に残った件。QUALITY/ACCEPTABLEで検出済みの軽微は見逃しに含めない。JAのみに残るNGはCheckerの評価対象外(ENのみチェック)のため別掲。

## 1. 記事別 工程別集計(重大/軽微)

| 記事 | ①JA | ②EN前 | ③EN後 | ④Checker最終 | ⑤独立評価 |
|---|---|---|---|---|---|
| 従来版 control rep1 | 0/4 | 0/4 | 0/3 | 0/6 | 0/4 |
| P2 rep1 | 0/1 | 0/2 | 0/2 | 0/9 | 0/2 |
| P2 rep2 | 2/4 | 2/4 | 0/4 | 0/4 | 2/4 |

## 2. 遷移(重大/軽微)

| 記事 | ①→②新規発生 | ②→③Rewrite修正 | ②→③Rewrite新規発生 | ④→⑤Checker見逃し | (参考)見逃しのうちJAのみ残存でChecker対象外 |
|---|---|---|---|---|---|
| 従来版 control rep1 | 0/0 | 0/1 | 0/0 | 0/2 | 0/1 |
| P2 rep1 | 0/1 | 0/0 | 0/0 | 0/1 | 0/0 |
| P2 rep2 | 0/0 | 2/0 | 0/0 | 0/1 | 2/0 |
| 合計 | 0/1 | 2/1 | 0/0 | 0/4 | 2/1 |

## 3. 従来版 control rep1

| NG ID | 重大度 | fact_id | 該当文 | ①JA | ②EN前 | ③EN後 | ⑤ | Checker検出(④) | Rewrite | 既存評価との差/備考 |
|---|---|---|---|---|---|---|---|---|---|---|
| sw-ctl-01 | 軽微 | F-011 | JA「第二は、衛星と地上の間で情報を運ぶ通信リンクです。」/ EN「The second is the communication link that carries information between satellites and the ground.」(台帳はlink segmentの存在のみ) | 発生 | 発生 | 残存 | 残存 | 未検出(最終cycle3。cycle1-2はACCEPTABLEで検出) | なし | 既存評価「台帳外追加」(通信リンク)と同一 |
| sw-ctl-02 | 軽微 | F-011 | JA「第三は、衛星に指示を出す地上の設備です。」/ EN(Rewrite前)「The third is the ground equipment that sends instructions to satellites.」 | 発生(JA R2に最終まで残存) | 発生 | 修正済(cycle1で「The third is the ground segment.」へ置換) | 残存(JAのみ。EN最終は修正済) | BLOCKING(cycle1。materiality=BLOCKING) | あり | 既存評価「台帳外追加」(地上設備)と同一 / 再ラベル理由: Checkerはblocking扱いだが、本基準では意味逆転なしの軽い具体化のため軽微 |
| sw-ctl-03 | 軽微 | F-012 | JA「通信を邪魔したり、地上の設備に影響を与えたりしても、衛星の力を使いにくくできる可能性があります。」/ EN「Interfering with communications or affecting ground equipment could also make it harder to use a satellite’s capabilities.」(台帳F-012に効果の記述なし。could/可能性で緩和) | 発生 | 発生 | 残存 | 残存 | ACCEPTABLE(cycle1・cycle3。最終cycle3で検出) | なし | 既存評価「因果」1件と同一 |
| sw-ctl-04 | 軽微 | F-001 | JA「ただし、正体はまだベールの中です。兵器の名前は分かりません。攻撃できるのかどうかも、何を標的にするのかも確認されていません。」/ EN「But the true nature of the weapons is still hidden. We do not know their names. It has not been confirmed whether they can attack, or what they would target.」(台帳は「推測で補わない」で「未確認・非開示」とは書かず。P2 rep2のsw-p2r2-06と同種) | 発生 | 発生 | 残存 | 残存 | 未検出(最終cycle3。cycle1でACCEPTABLE検出) | なし | 【本委任で追加】既存評価は「正しい」(briefに「確認されていない」が入っていたため) / 再ラベル理由: 本委任は台帳のみを基準に全記事へ同一適用(P2 rep2の同種文を軽微としているため整合)。brief記載を根拠に許容するかは判定保留 |


備考:
- ③=cycle1のen_text_after_rewrite(cycle2-3はRewriteなし)。b1b/article.mdはChecker前(=cycle1 before)と同一であることをdiffで確認。
- s4は最終cycle3のnon_blocking生件数(blocking_count=0)。6件中の多くは決定論検査(negation_polarity_mismatch)由来の誤検知寄り。
- s5はEN最終+JA①残存の和集合。ENのみ=軽微3(01,03,04)、JA(Checker対象外)のみ残存=軽微1(02)。
- s4_to_s5_missed(軽微2)=最終cycleで未検出だったsw-ctl-01,04(いずれもcycle1-2では検出)。sw-ctl-03はACCEPTABLEで検出済みのため除外。JAのみ残存のsw-ctl-02(軽微1)はs4_to_s5_missed_ja_uncheckedとして別掲。
- 従来版ledger(open233_polysemy_trial_04配下)には独立のledgerファイルが見つからないため、P2 ledgerを基準に使用(既存評価により fact本文は同一、差はnotes_for_writer行のみ)。

## 4. P2 rep1(Checker: RESOLVED_STAGE2_DOWNGRADE、1 cycle、blocking 0 / non_blocking 9、Rewriteなし)

| NG ID | 重大度 | fact_id | 該当文 | ①JA | ②EN前 | ③EN後 | ⑤ | Checker検出(④) | Rewrite | 既存評価との差/備考 |
|---|---|---|---|---|---|---|---|---|---|---|
| sw-p2r1-01 | 軽微 | F-012/F-013 | JA「そして、守る側のメニューはさらに幅広い。」/ EN「The defense menu is even wider.」(攻撃側との範囲比較は台帳にない) | 発生 | 残存 | 残存 | 残存 | QUALITY(cycle1=最終cycleで検出・非blocking) | なし | 既存評価の範囲1件と同一 |
| sw-p2r1-02 | 軽微 | F-001 | JA「敵対的な相手から統合軍を守る」→ EN「to protect joint forces from hostile forces」(「相手」が「軍」に狭まる。台帳は「敵対的な相手の行動」) | なし(JAは「相手」で台帳範囲内) | 発生 | 残存 | 残存 | 未検出 | なし | 【本委任で追加】既存評価(3)に軽微として記載(fact_errorsには非計上)。本委任で軽微NGとして台帳化 |


備考:
- Checker=RESOLVED_STAGE2_DOWNGRADE, 1 cycle, Rewriteなし。そのため③EN Rewrite後=②b1b/article.mdと同一。
- s4はChecker最終cycleのnon_blocking生件数(blocking_count=0)。9件中8件は決定論検査由来で実質的な事実誤りの検出ではない(実質検出はsw-p2r1-01のみ)。
- s4_to_s5_missed=最終cycleで未検出のまま最終稿に残ったNG。QUALITY/ACCEPTABLEで検出済みのNGは「見逃し」に数えない。
- 計数外: ENの「was deploying」/「had deployed」時制ゆれ、「Make them movable」の代名詞曖昧は事実の意味が変わらないため非計上(既存評価と同じ)。
- ロシア衛星(F-002)はbriefに無く、背景因果NGは発生していない。

## 5. P2 rep2(Checker: RESOLVED_REWRITE_THEN_DOWNGRADE、5 cycle、最終blocking 0 / non_blocking 4)

| NG ID | 重大度 | fact_id | 該当文 | ①JA | ②EN前 | ③EN後 | ⑤ | Checker検出(④) | Rewrite | 既存評価との差/備考 |
|---|---|---|---|---|---|---|---|---|---|---|
| sw-p2r2-01 | 重大 | F-001 | JA「宇宙、通信、地上の設備をまとめて守るための仕組みを、米国が公の言葉で認めたということです。」/ EN(Rewrite前)「It means that the United States has publicly acknowledged a system for protecting space, communications, and ground equipment together.」(認められたのは軌道上space control weapons配備。counterspace定義F-011を発表内容にすり替え) | 発生(JA R2に最終まで残存) | 発生 | 修正済(cycle1でEN「orbital space-control weapons」へ置換、cycle3で前文も置換) | 残存(JAのみ。EN最終は修正済) | BLOCKING(cycle1-3) | あり | 既存評価「対象の誤り」1件と同一 |
| sw-p2r2-02 | 重大 | F-001 | JA「今回の見どころは、宇宙戦争が始まったことではありません。宇宙の戸締まりをするための備えが、初めて表に出たことです。」/ EN(Rewrite前)「It is that preparations to secure space have come into public view for the first time.」(「初めて」は兵器配備の承認に限定されるのに「防衛の備え」へ拡張) | 発生(JA R2に最終まで残存) | 発生 | 修正済(cycle1でEN「the deployment of weapons in space ...」へ置換) | 残存(JAのみ。EN最終は修正済) | BLOCKING(cycle1-2) | あり | 既存評価「範囲の誤り(a)」。既存評価はF-001段落を「重大誤読」としており、本委任でNG-01と同系統の重大に再ラベル / 再ラベル理由: 「初めて表に出た」対象が兵器配備から防衛の備えへ入れ替わり、記事の主題(何が初めて認められたか)の理解が変わるため重大 |
| sw-p2r2-03 | 軽微 | F-001/F-002 | JA「では、なぜ今この話が出てきたのでしょうか。背景には、米国が見ているロシアの対衛星能力があります。」/ EN「So why has this story come up now? The background is Russia’s ability to attack satellites, as seen by the United States.」(F-001とF-002の間の因果は台帳になく、F-002は特定衛星の「可能性」評価) | 発生 | 発生 | 残存 | 残存 | QUALITY(cycle1・cycle5。最終cycleで検出) | なし | 既存評価の「範囲(b)」と「因果」(同一文)を1件に統合 / 再ラベル理由: 同一文・同一誤りは同一工程1件の基準により統合。後続段落でF-002は「米側の評価」「可能性」と帰属付きで正しく書かれており、意味は逆転しない過剰断定として軽微。ただし重大寄りの境界事例(判定保留) |
| sw-p2r2-04 | 軽微 | F-001/F-011 | JA/EN「ここで重要なのが、スペースコントロールという言葉です。…でも、カウンタースペースという考え方は、もっと広い範囲を指します。」(F-001のspace control weaponsとF-011のcounterspaceの関係は台帳になく、「でも」で対置。R2で「米宇宙軍の枠組み」の帰属も欠落) | 発生 | 発生 | 残存 | 残存 | 未検出(cycle1にF-001関連の別文への誤紐付きACCEPTABLEがあるが当該文の検出ではない) | なし | 既存評価「範囲(c)」と同一 |
| sw-p2r2-05 | 軽微 | F-001 | JA「今回の見どころは、宇宙戦争が始まったことではありません。」/ EN本文「What is noteworthy this time is not that a space war has begun.」+ In one line「…the move is about defense, not a space war.」(「宇宙戦争ではない」は台帳外の否定) | 発生 | 発生 | 残存(本文はcycle3で置換済、In one lineに同趣旨が残存) | 残存(JA本文・EN In one line) | QUALITY(本文cycle1)/ACCEPTABLE(In one line、最終cycle5) | あり(本文のみ(cycle3)) | 既存評価「否定の誤り」1件と同一 / 再ラベル理由: 台帳外の安心断定だが否定の反転ではなく軽微。Rewriteは本文のみ修正しIn one lineは未修正のため「一部修正」 |
| sw-p2r2-06 | 軽微 | F-001 | JA「米国が今回認めた発表でも、具体的なシステム名や標的、攻撃能力までは明らかにされていません。」/ EN「Even in the announcement/acknowledgment the United States made this time, the specific system name, targets, and attack capabilities were not disclosed.」(台帳は「推測で補わない」で「非開示」とは書いていない) | 発生 | 発生 | 残存(cycle3は「announcement→acknowledgment」の語句変更のみで内容未修正) | 残存 | QUALITY(cycle4-5。最終cycle5で検出) | あり(語句のみ(内容は未修正)) | 既存評価「台帳にない具体的事実の追加」と同一 |


備考:
- ③は累積Rewrite後=cycle3のen_text_after_rewrite(cycle4-5はjudge_onlyでRewriteなし)。
- Rewrite全件(EN側のみ、JA未変更): cycle1: [BEFORE「It means that the United States has publicly acknowledged a system for protecting space, communications, and ground equipment together.」→AFTER「It means that the United States has publicly acknowledged orbital space-control weapons.」] [BEFORE「It is that preparations to secure space have come into public view for the first time.」→AFTER「It is that the deployment of weapons in space has come into public view for the first time.」] / cycle2: [BEFORE「…should not be read simply as saying, “The U.S. has deployed weapons aimed at satellites.”」→AFTER「…“The U.S. has deployed weapons.”」(aimed at satellites削除)] [BEFORE「What is noteworthy this time is not that a space war has begun.」→AFTER「What is noteworthy is not that a space war has begun.」(this time削除)] / cycle3: [BEFORE「In other words, this announcement should not be read simply as saying, “The U.S. has deployed weapons.”」→AFTER「In other words, the announcement described weapons intended to protect joint forces from hostile actors.」] [BEFORE「Even in the announcement the United States made this time, the specific system name, targets, and attack capabilities were not disclosed.」→AFTER 同文のannouncementをacknowledgmentへ変更のみ] [BEFORE「What is noteworthy is not that a space war has begun.」→AFTER「What is noteworthy is the U.S. acknowledgment of orbital space-control weapons meant to protect joint forces from hostile actors.」] / cycle4-5: Rewriteなし。
- cycle1-3でCheckerが出したBLOCKINGは各3件。cycle2のBLOCKING「” It means that…」はcycle1で既に置換済みの文に対する再検出(violation_span_unverified, target_not_locatable)。
- s4はcycle5のnon_blocking生件数(blocking_count=0)。
- s5はEN最終+JA①の残存の和集合(重複はNG IDで統合)。内訳: ENのみ=重大0/軽微4、JA(Checker対象外)のみ残存=重大2(sw-p2r2-01,02)/軽微0。
- s4_to_s5_missed(軽微1)は最終cycleで未検出だったsw-p2r2-04(EN)のみ。QUALITY/ACCEPTABLEで検出済み(03,05,06)は見逃しに含めない。JAのみ残存の重大2はChecker対象外のため s4_to_s5_missed_ja_unchecked として別掲。
- s2_to_s3_newは0: Rewrite後EN本文に事実上の新規NGは見られない(文法の不自然さ「What is noteworthy is [A]. It is that [B].」とJAの「単純に読む話ではない」意図の消失は事実の意味変化ではないため非計上。既存評価と同じ)。

## 6. P2 rep2 Rewrite前後(全cycle、EN側のみ)

| cycle | Checker blocking/non_blocking | Rewrite |
|---|---|---|
| 1 | 3/8 | 2文置換(sw-p2r2-01, 02を修正) |
| 2 | 3/0 | 2点(「aimed at satellites」削除、「this time」削除。語レベル) |
| 3 | 3/0 | 3文(前文置換、acknowledgment語句変更、「What is noteworthy is…」置換でsw-p2r2-05の本文側を除去) |
| 4 | 0/2 | なし(judge_only) |
| 5 | 0/4 | なし(judge_only) |

全文BEFORE→AFTERは stagewise_space_weapons.json の rep2 notes に記録。

## 7. 判定保留・留意

- sw-p2r2-03(「なぜ今→背景はロシアの対衛星能力」): 台帳にないF-001-F-002間の因果を「なぜ今」への答えとして断定しており、重大に寄る境界事例。後続段落でF-002が帰属付き・可能性付きで正しく書かれているため軽微と判定。
- sw-ctl-04: 台帳のみを基準にすると軽微だが、従来版のbriefに「確認されていない」が入っていたため既存評価は「正しい」としていた。brief記載を根拠として認めるかで従来版の軽微が3→4に変わる(ユーザー/PM判断事項)。
- 従来版のledger: open233_polysemy_trial_04配下に独立のledgerは確認できず、P2 ledgerで代用(fact本文同一は既存評価で確認済み)。
- 重大/軽微の判定はSonnet実行層の単独判定(AI評価の限界)。N=1/2の観察であり、Note由来かrun揺れかは判別できない。
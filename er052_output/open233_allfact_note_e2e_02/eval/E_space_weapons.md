# 評価: space_weapons(P2 rep1 / P2 rep2 / 従来版 control rep1)

管理ID: OPEN-233-META-ALLFACT-NOTE-E2E-TRIAL-02(委任_C3)。評価日: 2026-10-07。評価者: Sonnet実行層(独立評価。AIによる面白さ採点・ペア比較は行っていない)。Trial/DEV限定、Production変更なし、API呼び出し0円。
注意: 本評価はN=1/2の観察であり、差がNote由来かrun揺れかは断定しない。

## 0. 前提(評価対象・台帳・brief)

- 台帳(評価基準): `er052_output/open233_allfact_note_e2e_02/ledger/space_weapons/research_ledger/verified_fact_ledger.txt`(F-001〜F-024)。従来版台帳との差は notes_for_writer 行のみ(P2は「注意: 」接頭辞+「注意(多義): …」追記。fact本文は同一)をdiffで確認済み。
- watchlist上、space_weapons に★(方向・状態変化)factは無い。よって(2)は「★該当なし」とし、参考として「範囲限定が読み方の核になるfact」(F-001=配備認定の範囲、F-002=評価と実際の攻撃の区別、F-011/F-013=counterspaceの範囲・active defenseは兵器を含み得る)を非★・参考で3分類した。
- briefで選ばれたfactが版ごとに違う(比較時の注意):
  - P2 rep1: F-001, F-011, F-012, F-013(F-002=ロシア衛星は含まれない)
  - P2 rep2: F-001, F-002, F-011
  - 従来版 rep1: F-001, F-002, F-011
- Checker記録(manifest.json): rep1 = RESOLVED_STAGE2_DOWNGRADE / 1 cycle / Rewrite無 / cost 2.05円。rep2 = RESOLVED_REWRITE_THEN_DOWNGRADE / 5 cycle / Rewrite有(cycle1-3) / cost 9.68円。従来版 = RESOLVED_REWRITE_THEN_DOWNGRADE / 3 cycle / Rewrite1件。

---

## A. P2 rep1

### (1) Fact整合(台帳と記事を突き合わせた独立評価。Checker結果は後から参照)

| 区分 | 件数 | 該当文(JA R2 / EN) | 台帳fact_id・根拠 |
|---|---|---|---|
| 主体の誤り | 0 | - | F-001のMeink(米空軍長官)・米政府機関記事の帰属は一致 |
| 対象の誤り | 0 | - | 「軌道上のspace control weapons配備の公式承認」に限定して書かれている |
| 範囲の誤り | 1 | JA「そして、守る側のメニューはさらに幅広い。」 / EN「The defense menu is even wider.」 | F-012/F-013。台帳に攻撃と防御の範囲を比較する記述は無い(攻撃側: 軌道攻撃・link interdiction・地上攻撃、防御側: active/passive分類とpassive例の列挙のみ)。「さらに幅広い」は台帳外の比較。R0(original.md)から既にあり、R1/R2でも直されず残存 |
| 時系列の誤り | 0 | - | 「九月十四日」(年は省略)のみ。台帳2026-09-14と矛盾なし |
| 否定の誤り | 0 | - | 「兵器を使わず…準備」は台帳F-013注記(ミサイル警戒・硬化等は兵器配備とは別の保護措置)と整合。「active defenseには兵器が含まれる場合もある」も注記と一致 |
| 因果の誤り | 0 | - | 因果の断定は無い |
| 台帳にない具体的事実の追加 | 0 | - | 数値・固有名・出来事の追加なし。軽微な言い換え: 「hostile forces」(台帳: 敵対的な相手の行動)、「Make them movable」(台帳: 機動性)は意味の範囲内 |

fact_errors合計(厳密な誤り): 1(範囲)。軽微な注意: EN「was deploying」(進行形)と後文「had deployed」の時制ゆれ(JAは「配備していると述べました」で曖昧)。誤りには数えない。

### (2) 方向・状態変化fact: ★該当なし(参考判定のみ)

| fact_id | 該当段落(JA R2全文 / EN全文) | 判定(参考) | 理由 |
|---|---|---|---|
| F-001(配備認定の範囲)非★ | JA「九月十四日、米空軍長官のトロイ・メインク氏は、アメリカが、敵対的な相手から統合軍を守るため、軌道上のスペースコントロール兵器を配備していると述べました。米政府機関の公式記事は、これを宇宙軍が宇宙に兵器を配備したと初めて認めた発言として記録しています。」「ここまでは、はっきりしています。アメリカが軌道上兵器の配備を公式に認めた。今回のニュースの大きなポイントです。」…「今回、公式に認められたのは、軌道上のスペースコントロール兵器の配備です。そこから「アメリカが宇宙兵器をすべて配備した」と広げると、話の範囲が大きくなりすぎます。」 / EN「On September 14, U.S. Secretary of the Air Force Troy Meink said that the United States was deploying space-control weapons in orbit to protect joint forces from hostile forces. An official article from a U.S. government agency recorded this as the first statement acknowledging that the Space Force had deployed weapons in space.」「Up to this point, things are clear. The United States officially acknowledged deploying weapons in orbit. That is the main point of this news.」…「What was officially acknowledged this time was the deployment of space-control weapons in orbit. If we expand that into “the United States has deployed all its space weapons,” the scope becomes far too broad. …」 | 正しい | 台帳F-001注記「『米国が軌道上兵器の配備を公式に認めた』までは使用可能」の範囲に収まり、「宇宙兵器全般」への拡大を明示的に否定している |
| F-011/F-012(counterspaceの範囲)非★ | JA「米宇宙軍の枠組みでは、この言葉は、軌道、通信リンク、地上で行う攻撃と防御をまとめた名前です。いわば、宇宙をめぐる作戦の大きな総合メニューです。」「攻撃のメニューには、軌道上の攻撃があります。それだけではありません。通信リンクを電磁波で妨害することや、サイバー攻撃、地上への攻撃も含まれます。宇宙空間の兵器だけでなく、通信とコンピューター、地上の仕組みまで登場するわけです。」 / EN「In the U.S. Space Force’s framework, this term is a name for attacks and defense carried out in orbit, through communication links, and on the ground. In a sense, it is a large, all-in-one menu of operations related to space.」「The attack menu includes attacks in orbit. But that is not all. It also includes disrupting communication links with electromagnetic waves, cyberattacks, and attacks on the ground. So it is not only about weapons in space. Communications, computers, and systems on the ground are included too.」 | 正しい | F-011/F-012と一致。「Space Forceのframeworkでは」の帰属も維持 |
| F-013(防御・active defenseの兵器含有)非★ | JA「そして、守る側のメニューはさらに幅広い。脅威を知らせる。機器を壊れにくくする。設備や機能を分散する。動かせるようにする。予備を持つ。こうした対策も防御です。兵器を使わず、攻撃を受けても全体が止まりにくくする準備まで含まれます。」「もちろん、積極的な防御には兵器が含まれる場合もあります。ただし、「カウンタースペース」と「宇宙兵器全般」は同じ意味ではありません。」 / EN「The defense menu is even wider. Warn of threats. Make equipment harder to damage. Spread out facilities and functions. Make them movable. Keep backups. These measures are also defense. It even includes preparing, without using weapons, to make it less likely that an attack will bring everything to a stop.」「Of course, active defense can sometimes include weapons. However, “counterspace” and “space weapons in general” do not mean the same thing.」 | 正しい(「さらに幅広い」の比較1点のみ曖昧) | 内容はF-013のpassive例・active defenseは兵器を含み得る、と一致。比較表現「さらに幅広い」だけが台帳外((1)範囲の1件) |

### (3) JA→EN意味変化

| 区分 | 件数 | 該当文(R0 / R2 / EN) | 備考 |
|---|---|---|---|
| R0→R2で意味が変わった文 | 0 | R0「守る側は、さらに幅広い。」→R2「そして、守る側のメニューはさらに幅広い。」(同じ主張が維持) | R0で入った「さらに幅広い」がR1/R2へそのまま残った |
| R2→ENで意味が変わった文 | 1(軽微) | R2「敵対的な相手から統合軍を守るため」→EN「to protect joint forces from hostile forces」 | 「相手」が「forces(軍)」に狭まる。台帳は「敵対的な相手の行動から」なので軽微な絞り込み |
| R0で正しかった表現がR2/ENで退行した | 0 | - | 台帳整合が悪化した箇所は見当たらない |

### (4) Checker・後段

- final_state: RESOLVED_STAGE2_DOWNGRADE / cycle数: 1 / must_fix・retry: 無(blocking_count 0)
- Rewrite有無: 無(b1b/article.md = Checker後のEN)
- non_blocking(ACCEPTABLE/QUALITY)9件の妥当性:

| # | 指摘文 | 材質 | 妥当性 | 理由 |
|---|---|---|---|---|
| 1 | The attack menu includes attacks in orbit. | ACCEPTABLE | 妥当 | 決定論検査のnegation_polarity_mismatch。F-012に直接対応しており実害なし(誤検知寄り) |
| 2 | It also includes disrupting communication links with electromagnetic waves, cyberattacks, and attacks on the ground. | ACCEPTABLE | 妥当 | 同上。F-012と一致 |
| 3 | So it is not only about weapons in space. | ACCEPTABLE | 妥当 | causal_not_in_fact(「So」)。F-011注記で支持されるまとめ |
| 4 | The defense menu is even wider. | QUALITY | 妥当(ただし最終稿に残存) | 台帳外の比較(unsupported/changed_comparison)として正しく検出。Rewrite対象外のため最終稿へ。実害は小さい。本評価(1)範囲1件と一致 |
| 5-7 | Make equipment harder to damage. / Make them movable. / Keep backups. | ACCEPTABLE | 妥当 | quote_not_in_ledger。台帳の「硬化・機動性・冗長性」の言い換え。「Make them movable」は「them」の指す先が曖昧だがfactは保たれる |
| 8 | Space Force’s framework, this term is a name for attacks and defense carried out in orbit, through communication links, and on the ground. | ACCEPTABLE | 妥当 | F-012と一致 |
| 9 | If, when you hear “counterspace,” you picture only weapons placed in space, your answer is incomplete. | ACCEPTABLE | 妥当 | F-011注記と整合する導入 |

- 誤許容(Checkerが拾わなかった誤り): 0(#4は検出済み。「hostile forces」「was deploying」は誤りと言えない軽微差)
- 最終記事に残った問題: ①「さらに幅広い」(範囲1)。②軽微: EN進行形/完了形の時制ゆれ、「Make them movable」の代名詞曖昧。③F-002(ロシア衛星)はbriefに含まれず記事にも無いため、背景因果の問題は発生していない。

---

## B. P2 rep2

### (1) Fact整合(独立評価)

JA R2(ja_writer/revision2.md)と、Checker後の最終EN(Rewrite反映後。b1b/article.mdはChecker前)の両方を評価。

| 区分 | JA R2 | EN最終(Rewrite後) | 該当文 | 台帳fact_id・根拠 |
|---|---|---|---|---|
| 主体の誤り | 0 | 0 | - | 米空軍長官・米国防総省の帰属は一致 |
| 対象の誤り(何を認めたか) | 1 | 0(Rewriteで修正) | JA「つまり今回の発表は、「衛星を狙う兵器を配備した」と単純に読む話ではありません。宇宙、通信、地上の設備をまとめて守るための仕組みを、米国が公の言葉で認めたということです。」 / EN修正前「It means that the United States has publicly acknowledged a system for protecting space, communications, and ground equipment together.」 | F-001。認められたのは「軌道上のspace control weaponsの配備」(注記: ここまでが使用可能)。「宇宙・通信・地上をまとめて守る仕組みを認めた」は台帳外(counterspaceの定義F-011を、発表の中身にすり替えている)。ENはCheckerが「orbital space-control weapons」へ修正したが、JA R2には誤りが残ったまま |
| 範囲の誤り | 3 | 2 | (a)JA「今回の見どころは、宇宙戦争が始まったことではありません。宇宙の戸締まりをするための備えが、初めて表に出たことです。」(EN修正前: preparations to secure space have come into public view for the first time)。台帳の「初めて」はSpace Forceが宇宙に兵器を配備したと認めたことに限定。「防衛の備えが初めて公になった」は範囲拡大。EN最終は「the deployment of weapons in space has come into public view for the first time」へ修正済み。(b)JA「背景には、米国が見ているロシアの対衛星能力があります。」 / EN「The background is Russia’s ability to attack satellites, as seen by the United States.」F-002は特定の1衛星について「他の低軌道衛星を攻撃できる可能性がある」と評価したもので、「ロシアの対衛星(攻撃)能力」一般への拡張は断定度・範囲を上げている(JA/ENとも残存、ENはChecker QUALITYで検出のみ)。(c)JA/EN「スペースコントロールという言葉…名前だけ聞くと…秘密兵器のようです。でも、カウンタースペースという考え方は、もっと広い範囲を指します。」 / EN「The key term here is “space control.” …But the idea of “counterspace” covers a much wider range.」台帳上、space control weapons(F-001)とcounterspace(F-011の定義)の関係は書かれていない。「でも」で対置され、兵器の名称と作戦概念が混ざる。JA/EN共に残存 | JA: (a)(b)(c)=3 / EN最終: (b)(c)=2 |
| 時系列の誤り | 0 | 0 | - | - |
| 否定の誤り | 1 | 1 | JA「今回の見どころは、宇宙戦争が始まったことではありません。」 / EN In one line「The U.S. has admitted deploying weapons in space, but the move is about defense, not a space war.」(EN本文側の同趣旨文はRewriteで置換済みだがIn one lineに残存)。台帳に「宇宙戦争は始まっていない」「この動きは防衛であり戦争ではない」という記述は無い(Checker自身もchanged_negation/unsupported_new_claimを検出) | F-001(防護用途の説明のみ) |
| 因果の誤り | 1 | 1 | JA「では、なぜ今この話が出てきたのでしょうか。背景には、米国が見ているロシアの対衛星能力があります。」 / EN「So why has this story come up now? The background is Russia’s ability to attack satellites, as seen by the United States.」台帳F-001とF-002の間に因果・背景関係は無い(briefのstorylineが「関連する脅威認識」として並置しただけ)。「なぜ今」への答えとして断定。R0の「米国はロシアの動きも挙げています」より因果が強い | F-001/F-002 |
| 台帳にない具体的事実の追加 | 1 | 1 | JA「米国が今回認めた発表でも、具体的なシステム名や標的、攻撃能力までは明らかにされていません。」 / EN「Even in the acknowledgment the United States made this time, the specific system name, targets, and attack capabilities were not disclosed.」台帳F-001注記は「…推測で補わない」で、「発表で開示されなかった」とは言っていない(Checker QUALITY/unsupported_new_claimで検出のみ)。従来版briefには「確認されていない」と明記されていたため、brief文言の差で本文が変わった可能性あり | F-001注記 |

fact_errors合計: JA R2 = 7(対象1+範囲3+否定1+因果1+追加1)/ EN最終 = 5(範囲2+否定1+因果1+追加1)/ EN Checker前 = 7。重さの注記: 否定・追加は「推測を断定した」軽めの誤り。最も重いのは対象(F-001の中身)と「初めて」の範囲拡大(いずれもJA R2に残存)。

### (2) 方向・状態変化fact: ★該当なし(参考判定のみ)

| fact_id | 該当段落(JA R2全文 / EN最終全文) | 判定(参考) | 理由 |
|---|---|---|---|
| F-001(配備認定の範囲)非★ | JA R2「実際、米国は宇宙に兵器を配備していると、初めて公式に認めました。ただし、話は映画のような宇宙戦闘とは少し違います。」「つまり今回の発表は、「衛星を狙う兵器を配備した」と単純に読む話ではありません。宇宙、通信、地上の設備をまとめて守るための仕組みを、米国が公の言葉で認めたということです。」…「今回の見どころは、宇宙戦争が始まったことではありません。宇宙の戸締まりをするための備えが、初めて表に出たことです。」 / EN最終「In fact, the United States has officially admitted for the first time that it has deployed weapons in space. However, the story is a little different from a space battle like those in movies.」「In other words, the announcement described weapons intended to protect joint forces from hostile actors. It means that the United States has publicly acknowledged orbital space-control weapons.」…「What is noteworthy is the U.S. acknowledgment of orbital space-control weapons meant to protect joint forces from hostile actors. It is that the deployment of weapons in space has come into public view for the first time. …」 | JA: 重大誤読(認めた対象と「初めて」の範囲が拡大)/ EN最終: 曖昧(核心はRewriteで台帳範囲に修正。ただし「key term=space control」→counterspace混同、In one lineの「defense, not a space war」が残存) | JAは発表の中身を「宇宙・通信・地上をまとめて守る仕組み」へ拡大しており、F-001注記(軌道上兵器の配備承認までは可、それ以上は推測で補わない)を超える。ENはCheckerが3サイクルのRewriteで台帳範囲に戻したが、文法も不自然(「What is noteworthy is [A]. It is that [B].」の二文) |
| F-002(評価と実際の攻撃の区別)非★ | JA R2「米国防総省によると、ロシアは二〇二四年五月十六日、低軌道に衛星を打ち上げ、米政府の衛星と同じ軌道に配置しました。米側は、その衛星がほかの低軌道衛星を攻撃できる可能性がある対衛星兵器だと評価しています。」「ただし、実際に衛星を攻撃したことは確認されていません。米国が今回認めた発表でも、具体的なシステム名や標的、攻撃能力までは明らかにされていません。」 / EN「According to the U.S. Department of Defense, on May 16, 2024, Russia launched a satellite into low Earth orbit and placed it in the same orbit as a U.S. government satellite. The U.S. assessed that the satellite was an anti-satellite weapon that could possibly attack other satellites in low Earth orbit.」「However, there is no confirmation that it has actually attacked a satellite. Even in the acknowledgment the United States made this time, …were not disclosed.」 | 正しい(この段落単体)。直前の「背景は…ロシアの対衛星能力」は曖昧((1)範囲(b)・因果) | 「米側の評価」「可能性」「実際の攻撃は未確認」の3点が保たれている |
| F-011(counterspaceの範囲)非★ | JA R2「ここで重要なのが、スペースコントロールという言葉です。名前だけ聞くと、宇宙空間にある秘密兵器のようです。でも、カウンタースペースという考え方は、もっと広い範囲を指します。」「対象になるのは、衛星が飛ぶ軌道だけではありません。衛星と地上を結ぶ通信リンクや、地上の設備も含まれます。通信を守ること、相手の通信を妨げること、地上の機器を防御することも、カウンタースペースに含まれ得ます。」 / EN「The key term here is “space control.” Just hearing the name, it sounds like a secret weapon in outer space. But the idea of “counterspace” covers a much wider range.」「What it covers is not only the orbits where satellites travel. It also includes communication links between satellites and the ground, as well as equipment on the ground. Protecting communications, interfering with the other side’s communications, and defending equipment on the ground may also fall under counterspace.」 | 曖昧 | counterspaceの範囲そのもの(軌道・リンク・地上、攻撃・防御を含み得る)はF-011と一致。一方「space control」と「counterspace」を「でも」で接続する構成が、空間管制兵器の承認とcounterspace概念を取り違えさせ、F-001の誤読の入口になっている。F-011の帰属(「米宇宙軍の枠組み」)がR0にはあったがR2で落ちた |

### (3) JA→EN意味変化

| 区分 | 件数 | 該当文(R0 / R2 / EN) | 備考 |
|---|---|---|---|
| R0→R2で意味が変わった文 | 3 | (i)R0「背景にある脅威として、米国はロシアの動きも挙げています。」→R2「では、なぜ今この話が出てきたのでしょうか。背景には、米国が見ているロシアの対衛星能力があります。」(因果的な「なぜ今」を追加、「動き」→「対衛星能力」)/ (ii)R0「けれど、実は「カウンタースペース」という言葉は、もっと広い意味です。米宇宙軍の説明では、軌道上だけでなく…」→R2「ここで重要なのが、スペースコントロールという言葉です。名前だけ聞くと、宇宙空間にある秘密兵器のようです。でも、カウンタースペースという考え方は、もっと広い範囲を指します。」(space controlとcounterspaceの混同導入、「米宇宙軍の説明では」の帰属が欠落)/ (iii)R0「「宇宙で戦争が始まった」という発表ではなく、「衛星や通信を守るための備えが、ついに公の言葉になった」という話です。」→R2「宇宙戦争が始まったことではありません。宇宙の戸締まりをするための備えが、初めて表に出たことです。」(R0にあった誤りの引き継ぎ。「ついに」→「初めて」で台帳の「初めて」との結び付きが強まる) | (i)(ii)がR2での悪化。(iii)はR0からの継続 |
| R2→ENで意味が変わった文 | 翻訳側2 + Checker Rewrite後のJA/EN乖離4 | 翻訳側: 「ロシアの対衛星能力」→「Russia’s ability to attack satellites」(断定度が上がる)/ 「宇宙の戸締まり」→「preparations to secure space」(Rewrite前)。Rewrite後の乖離: JA R2にはRewrite前の主張が残り、ENでは4文が置換されている((4)参照) | JA最終稿(Checker対象外)とEN(Checker後)で、同じ記事なのに「認めた内容」が異なる |
| R0で正しかった表現がR2/ENで退行した | 2 | (i)R0「米宇宙軍の説明では、軌道上だけでなく、衛星と地上の間の通信リンク、さらに地上の設備まで含めて…」→R2で「米宇宙軍の枠組み」の帰属が落ちた(帰属の退行)。(ii)R0「米国はロシアの動きも挙げています」(米国が挙げたと帰属)→R2「米国が見ているロシアの対衛星能力」+「なぜ今」(因果の強化) | いずれも台帳外の断定側への変化 |

### (4) Checker・後段

- final_state: RESOLVED_REWRITE_THEN_DOWNGRADE / cycle数: 5(cycle1-3: Rewrite有、cycle4-5: 再判定のみ judge_only)/ cost 9.68円
- must_fix・retry: BLOCKINGはcycle1(F-001の「acknowledged a system for protecting space…」「preparations to secure space…」)→cycle2→cycle3と再発(severity_wobble、same_claim_reblocked_escalated_to_paragraphあり)。cycle3で追加サイクル付与(extra_cycle_granted、same_fact_id_new_location)。cycle4でblocking 0。主にF-001の範囲拡大を3サイクルかけて解消。
- Rewrite内容(before→after全文。全てEN側のみ。JA R2は未変更):
  - cycle1(2文置換):
    - BEFORE: 「It means that the United States has publicly acknowledged a system for protecting space, communications, and ground equipment together.」→ AFTER: 「It means that the United States has publicly acknowledged orbital space-control weapons.」
    - BEFORE: 「It is that preparations to secure space have come into public view for the first time.」→ AFTER: 「It is that the deployment of weapons in space has come into public view for the first time.」
  - cycle2(2点・語レベル):
    - BEFORE: 「In other words, this announcement should not be read simply as saying, “The U.S. has deployed weapons aimed at satellites.”」→ AFTER: 「…“The U.S. has deployed weapons.”」(「aimed at satellites」削除)
    - BEFORE: 「What is noteworthy this time is not that a space war has begun.」→ AFTER: 「What is noteworthy is not that a space war has begun.」(「this time」削除)
  - cycle3(3点・文レベル):
    - BEFORE: 「In other words, this announcement should not be read simply as saying, “The U.S. has deployed weapons.”」→ AFTER: 「In other words, the announcement described weapons intended to protect joint forces from hostile actors.」
    - BEFORE: 「Even in the announcement the United States made this time, the specific system name, targets, and attack capabilities were not disclosed.」→ AFTER: 「Even in the acknowledgment the United States made this time, the specific system name, targets, and attack capabilities were not disclosed.」
    - BEFORE: 「What is noteworthy is not that a space war has begun.」→ AFTER: 「What is noteworthy is the U.S. acknowledgment of orbital space-control weapons meant to protect joint forces from hostile actors.」(この結果、続く「It is that the deployment of weapons in space has come into public view for the first time.」とあわせ「What is noteworthy is [A]. It is that [B].」という文法的に不自然な二文になった)
  - Rewrite後の最終ENで台帳整合が改善した点: F-001の対象の誤り、「初めて」の範囲は解消。悪化した点: 文法の不自然さ、「In other words, the announcement described weapons intended to protect…」が前文(counterspaceの広さ)との接続が悪い(JAの「単純に読む話ではありません」の意図は消えている)。
- 最終cycle(5)のnon_blocking 4件の妥当性:

| # | 指摘文 | 材質 | 妥当性 | 理由 |
|---|---|---|---|---|
| 1 | The background is Russia’s ability to attack satellites, as seen by the United States. | QUALITY | 過小 | 範囲拡張(F-002は特定衛星の「可能性」評価)と「なぜ今」の因果断定を含む((1)範囲(b)・因果)。BLOCKINGにならないまま最終稿に残存 |
| 2 | However, there is no confirmation that it has actually attacked a satellite. | ACCEPTABLE | 妥当 | 決定論検査のnegation_polarity_mismatch。F-002と一致(誤検知) |
| 3 | Even in the acknowledgment the United States made this time, the specific system name, targets, and attack capabilities were not disclosed. | QUALITY | 妥当 | 「開示されなかった」は台帳に明記なし(推測断定)。QUALITYで検出。BLOCKINGまでは不要 |
| 4 | The U.S. has admitted deploying weapons in space, but the move is about defense, not a space war. | ACCEPTABLE | 過小 | 「宇宙戦争ではない」「防衛である」は台帳外の否定・一般化。同趣旨の本文文(What is noteworthy is not that a space war has begun)はcycle2-3でBLOCKINGとして書き換えられたのに、In one lineでは同趣旨がACCEPTABLEのまま通過(判定ゆれ) |

- 誤許容(Checkerが最終的に許したfact誤り): 2件(上記#1・#4)。加えてChecker対象外のJA R2に対象誤り1・範囲誤り(「初めて表に出た」)が残存。
- 最終記事に残った問題: ①JA R2とEN最終のfact乖離(JA側にF-001対象の拡大が残存)。②「space control」と「counterspace」の接続(JA/EN)。③「background=Russia's ability」の因果・断定度。④In one lineの否定。⑤Rewrite由来の文法の不自然さ。

---

## C. 従来版 control rep1(比較用の参考評価。brief: F-001, F-002, F-011)

簡易評価(P2版との差を見るため。Checker結果は参照のみ)。

- (1) Fact整合: JA R2/ENとも主体・時系列・否定の誤り無し。台帳外追加: 「通信リンクが衛星と地上の間で情報を運ぶ」「地上設備が衛星へ指示を送る」(JA R2に残存、ENはCheckerがBLOCKINGとして「The third is the ground segment.」へ置換)。因果: 「Interfering with communications or affecting ground equipment could also make it harder to use a satellite’s capabilities.」(F-012に効果の記述なし。「could」で緩和)。ロシア衛星は「米側は…可能性があると評価」と帰属付きで、「背景にあるのは、ロシアの衛星です」と並置にとどまる(因果の問いは無し)。fact_errors合計: JA R2 = 3(追加2、因果1)/ EN最終 = 2(追加1、因果1)。
- (2) ★該当なし。参考: F-001=「初めて公式に認めました…兵器の名前は分かりません。攻撃できるのかどうかも、何を標的にするのかも確認されていません」→正しい(briefに「具体的なシステム名・攻撃能力・標的は確認されていない」が入っていた)。F-002=「ただし、実際の攻撃は確認されていません」→正しい。F-011=3セグメント(軌道・通信リンク・地上)+攻撃も防御も含む→正しい(説明の付け足しのみ)。
- (3) R0→R2→EN: 意味変化なし/退行なし(表現変更のみ)。
- (4) Checker: RESOLVED_REWRITE_THEN_DOWNGRADE、3 cycle、Rewrite1件(cycle1、段落レベル): BEFORE「The third is the ground equipment that sends instructions to satellites.」→ AFTER「The third is the ground segment.」。残存non_blocking: cycle3で6件(ほとんどが決定論検査の誤検知、1件は通信妨害の効果因果ACCEPTABLE)。記事ファイル(b1b/article.md)はChecker前のため「ground equipment that sends instructions」のまま。

---

## D. P2版と従来版の差(断定しない)

- briefのfact選択がrunごとに違う(rep1=F-001/011/012/013でF-002無し、rep2と従来版=F-001/002/011)。rep1は「F-002背景」の因果の話が無い分だけfact誤りが少なく(1件、範囲)、rep2は従来版と似た構成で、台帳外の背景因果・「初めて」の範囲・否定の断定が増え、CheckerがEN側のみ3サイクルのRewriteで修正した。
- 同じ「ロシア衛星」を背景に置く構成(rep2と従来版)では、P2 rep2のほうが対象の拡大(F-001の中身)・否定・因果が多い。ただしN=1/2でありNote由来かrun揺れかは判別できない(brief選択・storyline文面の違いも要因候補)。
- 共通して、決定論検査のnegation_polarity_mismatch等による誤検知的なnon_blockingが多い(rep1は9件中8件が決定論検査由来)。Note有無とは別のChecker側の性質。

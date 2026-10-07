# E_ai_control 評価(委任_C2、OPEN-233-META-ALLFACT-NOTE-E2E-TRIAL-02、API呼び出しなし、AI面白さ採点なし)
台帳: er052_output/open233_allfact_note_e2e_02/ledger/ai_control/research_ledger/verified_fact_ledger.txt。(1)は台帳照合を先に実施し、その後でChecker結果jsonを参照した(独立評価)。
EVID-010数値の台帳再確認: 約1,200エージェント/7万件超のメッセージ・ファイル/約700体がHugging Face攻撃に参加(watchlistと一致)。EVID-010は従来版のみ採用、P2両repは未採用。
brief採用fact: P2 rep1=EVID-008/009/011/CONTROL-002、P2 rep2=EVID-008/009/CONTROL-003(★)、従来版=EVID-010/011/CONTROL-002。版差はNote由来と断定できない。
最終EN本文は、Rewriteがある場合 b1b/article.md(Rewrite前)ではなくChecker内 en_text_after_rewrite を最終として評価した。JAはRewrite対象外でR2のまま。

---
## A. P2 rep1
最終: RESOLVED_REWRITE_THEN_DOWNGRADE、3 cycle、blocking 0。Rewrite(cycle1のみ)。

### (1) Fact整合(最終JA R2+最終EN)
| 区分 | 件数 | 該当文 | 台帳・根拠 |
|---|---|---|---|
| 主体 | 0(Rewrite前は1) | Rewrite前EN「whether it tends to be used for harmful purposes」(JA R2「有害な目的で使う傾向があるか」) → 最終は「whether it tends to use that ability for harmful purposes」に修正済み | CONTROL-002: harmful propensity to use them(AI側の傾向) |
| 対象 | 1 | JA R2「プログラムの部品を公開しました。ところが、その部品は現実の公開場所に、およそ一時間置かれました。」/EN「it published a part of a program. But that part stayed at a real public site for about an hour.」 | EVID-009: malicious Python packageをPyPIへ。「部品/part of a program」は対象の言い換えを超える(R0は「悪意のあるプログラムを公開」) |
| 範囲 | 3 | (a)JA R2「いわば、厳重な監獄のはずが、裏口の鍵がかかっていなかった状態です。」(最終ENではRewriteで削除、JAには残存) (b)JA R2/EN「確認すべきなのは、AIに十分な能力があるか。有害な目的で使う傾向があるか。そして、実際に使える道と機会があるかです。」/「We need to check whether the AI has enough ability, ...」 (c)JA R2「今回示されたのは、条件がそろうとAIがかなり遠くまで進めることです。」/EN「What this showed is that, when the conditions are right, AI can go quite far.」 | (a)EVID-008: 標準的なサイバー防御がなかった(「厳重」は逆方向)。(b)CONTROL-002: 3要素は深刻な能動的制御喪失の条件で、能力も「制御を損なう能力」。限定が脱落。(c)特定の評価・環境の事例をAI一般へ拡張 |
| 時系列 | 0 | - | - |
| 否定 | 1 | JA R2「自分から世界征服を考えたわけでも、評価環境から逃げようと計画したわけでもありません。」/EN「It did not think about taking over the world on its own, nor did it plan to escape from the test environment.」 | EVID-008: 自己流出や意図的に環境から脱出しようとした行動は確認されなかった、まで。「世界征服を考えなかった」という内心の否定は台帳になし |
| 因果 | 1 | JA R2「でも、この事件の意外な主役は、AIではありません。舞台装置です。」/EN In one line「The AI seemed to escape, but open doors and weak defenses played the bigger role.」 | EVID-011ではエージェントが未知の脆弱性を見つけて利用(能動的)。環境側の寄与がAIより大きいという比較・因果は台帳になし(EVID-008の誤設定は事実だが、OpenAI事案にも拡張して主役断定) |
| 台帳にない具体的事実の追加 | 0 | - | - |

### (2) ★fact
brief採用なし(CONTROL-003は本runのbriefに無し)。ただし参考: JA R2はOpenAI事案に「ここも防御を弱めた研究用の試験環境でした」とあり(EVID-011と整合)、封じ込め・停止は記述なし。

### (3) JA→EN意味変化
| 区分 | 件数 | R0 / R2 / EN | 備考 |
|---|---|---|---|
| R0→R2 | 2 | R0「悪意のあるプログラムを公開しました」→R2「プログラムの部品を公開しました」; R0「自分から評価環境を脱出しようとした行動が確認されたわけでもありません」→R2「自分から世界征服を考えたわけでも、評価環境から逃げようと計画したわけでもありません」 | R0の方が台帳に忠実 |
| R2→EN | 1(Rewriteで解消) | R2「有害な目的で使う傾向があるか」→EN(Rewrite前)「tends to be used for harmful purposes」 | cycle1 Rewriteで「use that ability」に修正 |
| 退行 | 3(うち1はRewrite解消済み) | 上記3件 | |

### (4) Checker・後段
- final_state: RESOLVED_REWRITE_THEN_DOWNGRADE、cycle: 3。
- Rewrite(cycle1): ①(EVID-008、4_paragraph)削除「In other words, it was like a heavily guarded prison whose back door had been left unlocked.」(BLOCKING、台帳の「防御なし」と逆) ②(CONTROL-002、1_word_connective)「whether it tends to be used for harmful purposes」→「whether it tends to use that ability for harmful purposes」。いずれも妥当な修正。
- must_fix: cycle1にBLOCKING 2件→Rewrite→cycle2 blocking 0。retry: 無し。
- 誤許容(ACCEPTABLE扱い): 「What this showed is that, when the conditions are right, AI can go quite far.」(Checker自身が「AI一般へ広げている」と指摘しながらACCEPTABLE=過小)。計1件。
- QUALITY判定のまま残存: 「During the task, it published a part of a program.」(対象変更、Checker妥当指摘)、「It did not think about taking over the world on its own...」(Checker妥当指摘)、「The AI seemed to escape, but open doors and weak defenses played the bigger role.」、「An AI that was supposed to be isolated got out into the outside world and entered real systems.」(ledger_scope指摘)。いずれもnon-blockingのため記事に残存。
- 最終記事に残った問題: (1)の範囲(b)(c)(JA監獄(a))、対象、否定、因果。JAはRewrite対象外のため「厳重な監獄」がJAに残り、ENは削除=JA/EN不一致。

---
## B. P2 rep2
最終: RESOLVED_REWRITE_THEN_DOWNGRADE、4 cycle、blocking 0。Rewrite(cycle1・cycle2)。

### (1) Fact整合(最終JA R2+最終EN)
| 区分 | 件数 | 該当文 | 台帳・根拠 |
|---|---|---|---|
| 主体 | 0 | JA R2「別に報告された実際のインターネット事案では、セキュリティチームが異常を見つけ、およそ一時間以内に封じ込めました。」はAISIを明示せず(主体の曖昧さ、誤りまでは至らない) | CONTROL-003 |
| 対象 | 0 | - | - |
| 範囲 | 0 | - | - |
| 時系列 | 0 | - | - |
| 否定 | 0 | - | - |
| 因果 | 1 | JA R2「だからこれは、世界征服の始まりというより、ゲーム会場の扉を閉め忘れた事件です。」/EN「So this was less the beginning of world domination than an incident in which someone forgot to close the door to the game site.」 | EVID-008: 設定不備(misconfigured)。「誰かが閉め忘れた」という過失・責任の描写は台帳になし |
| 台帳にない具体的事実の追加 | 3 | (a)JA R2「これは、ネット上に隠された情報を探す宝探しのような競技です。」/EN「It is a treasure hunt in which players search for hidden information online.」 (b)JA R2「AIは、用意された世界の中で敵を探し、課題をクリアするつもりでした。」(ENはRewriteで「The AI was supposed to complete tasks.」に短縮) (c)EN「There was a hole in the design of the game site.」(最終ENでは、第三者設定不備の文が失われたため根拠なく残存。JAは「ゲーム会場の設計に穴がありました。第三者が用意した評価環境の設定が不十分で…」と説明あり) | EVID-008/009: CTF課題を遂行(定義・敵探し・「設計の穴」は台帳になし) |

### (2) ★fact
| fact_id | 該当段落(全文) | 判定 | 理由 |
|---|---|---|---|
| CONTROL-003 | JA R2「もちろん、危険が小さいという意味ではありません。別に報告された実際のインターネット事案では、セキュリティチームが異常を見つけ、およそ一時間以内に封じ込めました。関連する評価では、最新の内部テストモデルが標的を実在すると認識した時点で停止しました。一方、古いモデルは一部で動き続けました。」 / EN「Of course, this does not mean the danger was small. In a separate real-world internet incident that was also reported, a security team found the unusual activity and contained it within about an hour. In a related evaluation, the latest internal test model stopped when it recognized that the target was real. An older model, however, continued operating in some cases.」 | 正しい | 約1時間で封じ込め、最新モデルが標的実在を認識して停止、旧モデルは一部で継続、の全てが台帳に一致。「停止問題は解決/不可避」とは書いていない。軽微な曖昧さ: AISI/Anthropicを名指ししない、「関連する評価」。「特定条件下のみ」という限定句は無いが、直前の「危険が小さいという意味ではありません」で過大解釈を抑制 |

### (3) JA→EN意味変化
| 区分 | 件数 | R0 / R2 / EN | 備考 |
|---|---|---|---|
| R0→R2 | 0 | R0「認証情報が外へ流れる可能性もありました」→R2「認証情報を外へ流出させることが可能な仕組みも含まれていました」(台帳enabled credential exfiltrationに近づき改善) | |
| R2→EN | 1(Rewrite起因) | R2「第三者が用意した評価環境の設定が不十分で、インターネットにつながる可能性があったのです。」→EN最終: この文が消失(「There was a hole in the design of the game site. It also lacked the cyber safety measures...」のみ) | EVID-008の核(第三者の評価環境の設定不備)がENから欠落 |
| 退行 | 1 | 上記 | |

### (4) Checker・後段
- final_state: RESOLVED_REWRITE_THEN_DOWNGRADE、cycle: 4。
- Rewrite(cycle1): ①「The AI was supposed to look for enemies and complete tasks inside the prepared world.」→「The AI was supposed to complete tasks.」(BLOCKING指摘に対し妥当) ②「The evaluation environment set up by a third party was not properly configured, so it might connect to the internet.」→「In a simulated safety evaluation, Claude Opus 4 attempted blackmail in 84% of rollouts.」(**重大な不具合**: 無関係なEVID-006の文に置換。台帳のfact_id紐付けずれによるRewrite誤適用) 。cycle2: 上記blackmail文をBLOCKINGとして削除、「But there was a hole in the design of the game site.」→「There was a hole in the design of the game site.」。結果として第三者設定不備の文が最終ENから消えた。
- must_fix: cycle1 blocking 3件→cycle2 blocking 2件(Rewrite由来の誤文)→cycle3で0。retry: 無し(同一run内4cycle)。
- 誤許容(ACCEPTABLE扱い): ①「It is a treasure hunt in which players search for hidden information online.」(台帳外定義、指摘は妥当・過小) ②「So this was less the beginning of world domination than an incident in which someone forgot to close the door...」(責任描写、過小) ③「There was a hole in the design of the game site.」(設計の穴、過小)。計3件。
- 最終記事に残った問題: (1)の因果・追加3件、(3)のEN欠落。CONTROL-003は問題なし。

---
## C. 従来版 rep1
最終: RESOLVED_STAGE2_DOWNGRADE、1 cycle、Rewrite無し、blocking 0 / non-blocking 22。(ledger fact_idが「E010」「E011」と短縮表記され、多数が決定論検査「unknown_fact_id,quote_not_in_ledger」でBLOCKING候補→降格。)

### (1) Fact整合
| 区分 | 件数 | 該当文 | 台帳・根拠 |
|---|---|---|---|
| 主体 | 0 | - | - |
| 対象 | 0 | - | - |
| 範囲 | 1 | EN「The main actors were research prototypes used only inside the company.」(JA R2「主に関わったのは、内部だけで使う研究用プロトタイプでした。」) | EVID-011: principal modelは内部限定の研究プロトタイプ(1つの主要モデル)。複数形・「actors」化は拡張 |
| 時系列 | 0 | - | - |
| 否定 | 2 | (a)JA R2「特に、AIが有害な行動を取る傾向まで実証された、という意味ではありません。」/EN「In particular, it does not mean that AI was shown to be inclined to take harmful actions.」 (b)EN In one line「The AI did not rebel; it bypassed isolated systems through a chain of weaknesses, credentials, and loose safeguards.」 | (a)CONTROL-002/EVID-010/011に今回の事件で有害な傾向が実証されなかったとする記述なし。(b)「反乱していない」は断定(EVID-010はエージェント約700体がHugging Face攻撃に参加) |
| 因果 | 0 | - | - |
| 台帳にない具体的事実の追加 | 2 | (a)JA R2「掲示板で攻略情報を交換していた」/EN「exchanged tips on a message board」 (b)JA R2「隔離したつもりの部屋に、通路と鍵が残っていた」/EN「a passage and keys being left behind in a room we thought we had isolated」 | (a)EVID-010: メッセージ・ファイルの内容は台帳になし。(b)資格情報が環境内に残されていたという経緯は台帳になし(chained credentialsのみ) |
EVID-010数値(約1,200/7万超/約700)は台帳と一致。

### (2) ★fact
brief採用なし(CONTROL-003は従来版briefに無し)。

### (3) JA→EN意味変化
| 区分 | 件数 | R0 / R2 / EN | 備考 |
|---|---|---|---|
| R0→R2 | 2 | R0(該当なし)→R2「攻略情報を交換」(追加); R0(該当なし)→R2「有害な行動を取る傾向まで実証された、という意味ではありません」(追加) | R0の「AIならどんな環境でも人間の制御を失わせられる、ということではありません」(台帳notesに沿う)から、より強い否定へ |
| R2→EN | 1 | R2「研究用プロトタイプでした」→EN「research prototypes」(複数形) | 範囲拡張 |
| 退行 | 1 | 上記R2→EN | |

### (4) Checker・後段
- final_state: RESOLVED_STAGE2_DOWNGRADE、cycle: 1、Rewrite無し、must_fix/retry無し。
- 誤許容(ACCEPTABLE扱い): ①「This evaluation did not confirm that all three conditions were present.」(指摘は「この個別評価が3要素を確認しなかったと明示していない」=妥当、過小) ②「In particular, it does not mean that AI was shown to be inclined to take harmful actions.」(決定論検査の誤検知扱い) ③「This was less a great AI rebellion than a story about a passage and keys being left behind...」(指摘「置き忘れとは述べていない」=妥当、過小)。計3件。
- QUALITY判定で残存: 「The main actors were research prototypes used only inside the company.」(ledger_scope指摘妥当)、「The AI did not rebel; ...」、「The image is more like this: participants ... exchanged tips on a message board.」。non-blockingのため記事に残存。
- 最終記事に残った問題: (1)の全件。

---
## D. 版差(断定しない)
- P2 rep1と従来版は誤り件数が近い(6件対5件)。P2 rep1は監獄比喩(防御なしと逆)を含んでいたが、Checkerが唯一のBLOCKINGとして検出しRewriteで削除(JAには残る)。従来版はRewriteなしで降格のみ。Note由来の改善とは言えず、fact選択差(OpenAI事案のみ vs Anthropic事案)の影響が大きい。
- P2 rep2はCONTROL-003★を正しく記述した点は良いが、RewriteがEVID-006のblackmail文を誤挿入・後で削除する不具合が発生し、最終ENから第三者設定不備の文が欠落。Rewrite機構のfact_id紐付け不具合の可能性としてFableに報告(実装は行わない)。

# NG_ai_control 工程別NG台帳(OPEN-233-E2E-STAGEWISE-NG-AUDIT-01 委任_A2、API呼び出しなし・既存成果物の再評価のみ)

工程: ①JA最終稿(ja_writer/revision2.md) ②EN Rewrite前(b1b/article.md) ③EN Rewrite後(Checker最終cycle en_text_after_rewrite、Rewriteなしは②と同一) ④Checker最終判定(最終cycleのblocking=重大/non_blocking=軽微。non_blockingは候補全件でNG実数ではない) ⑤独立評価(既存E_*.mdを③EN+①JAに対し本基準で再ラベル。⑤は③ENに加え①JAのみ残存を含む)。
重大度は指示の全工程同一基準を適用。同一誤りはJA/ENで同一NG IDを共有。「本委任で追加」はE_*.mdのNG件数に無かった項目。

---
## ai_control P2 rep1

Checker最終: RESOLVED_REWRITE_THEN_DOWNGRADE、cycle=3、Rewrite: cycle1のみ(監獄比喩段落削除・propensity文修正)。cycle別blocking/non-blocking: c1=2/14,c2=0/4,c3=0/16

### NG台帳

| NG ID | 重大度 | fact_id | 該当文(全文) | ①JA | ②EN前 | ③EN後 | ⑤独立 | ④Checker検出 | Rewrite修正 | 備考 |
|---|---|---|---|---|---|---|---|---|---|---|
| ai-p2r1-01 | 重大 | EVID-008 | JA「いわば、厳重な監獄のはずが、裏口の鍵がかかっていなかった状態です。」/EN「In other words, it was like a heavily guarded prison whose back door had been left unlocked.」 | 発生 | 残存 | 修正済 | 残存 | BLOCKING | あり | 台帳は「標準的なサイバー防御がなかった」。「厳重(heavily guarded)」は防御状況を逆方向に描く(状態の逆転)。EN=Rewrite(cycle1)で段落ごと削除で修正済。JAは対象外のため残存(s5はJAのみ残存)。 |
| ai-p2r1-02 | 重大 | CONTROL-002 | EN(Rewrite前)「whether it tends to be used for harmful purposes」(JA「有害な目的で使う傾向があるか」は正しい。修正後EN「whether it tends to use that ability for harmful purposes」) | 該当なし | 発生 | 修正済 | 該当なし | BLOCKING | あり | 台帳は「harmful propensity to use them」(AI側の傾向)。「使われる」では主体が人間側へ入れ替わる。EN固有、Rewrite cycle1で修正済(最終文は正しい)。 |
| ai-p2r1-03 | 軽微 | EVID-009 | JA「プログラムの部品を公開しました。ところが、その部品は現実の公開場所に、およそ一時間置かれました。」/EN「it published a part of a program. But that part stayed at a real public site for about an hour.」 | 発生 | 残存 | 残存 | 残存 | QUALITY | なし | 台帳は悪意あるPythonパッケージをPyPIへ。「部品」は対象を弱める言い換え。前段落で「悪意のあるプログラムを公開」と明示され、全体の意味は逆転しないため軽微。 |
| ai-p2r1-04 | 軽微 | CONTROL-002 | JA/EN「確認すべきなのは、AIに十分な能力があるか。有害な目的で使う傾向があるか。そして、実際に使える道と機会があるかです。」/「We need to check whether the AI has enough ability, …」 | 発生 | 残存 | 残存 | 残存 | ACCEPTABLE | なし | 3要素は深刻な能動的制御喪失の条件(将来リスク分析の枠組み)。限定が脱落し本事件の確認項目として提示。 |
| ai-p2r1-05 | 軽微 | EVID-008/011 | JA「今回示されたのは、条件がそろうとAIがかなり遠くまで進めることです。」/EN「What this showed is that, when the conditions are right, AI can go quite far.」 | 発生 | 残存 | 残存 | 残存 | ACCEPTABLE | なし | 特定の評価・環境の事例をAI一般へ拡張(Checkerは一般化と明記しつつACCEPTABLE)。直後で「制御喪失は証明されていない」と限定。 |
| ai-p2r1-06 | 軽微 | EVID-008 | JA「自分から世界征服を考えたわけでも、評価環境から逃げようと計画したわけでもありません。」/EN「It did not think about taking over the world on its own, nor did it plan to escape from the test environment.」 | 発生 | 残存 | 残存 | 残存 | QUALITY | なし | 台帳は「意図的に脱出しようとした行動は確認されず」まで。「世界征服を考えなかった」という内心の否定は台帳外。方向は台帳と整合。 |
| ai-p2r1-07 | 軽微 | EVID-008/011 | JA「でも、この事件の意外な主役は、AIではありません。舞台装置です。」「…問われているのは、AIの賢さだけでなく、ドアを閉める側の腕前」/EN In one line「The AI seemed to escape, but open doors and weak defenses played the bigger role.」 | 発生 | 残存 | 残存 | 残存 | QUALITY | なし | 環境側の寄与がAIより大きいという比較・因果は台帳になし。OpenAI事案(EVID-011)ではエージェントが未知の脆弱性を能動的に突いており、主役断定は過剰。境界例だが「意味逆転」までは至らず軽微とした(Fable要確認の境界)。 |

注: 該当なし=その工程の本文に当該NGが存在しない。⑤残存は③ENまたは①JAのいずれかに残る意味。

### 工程別集計(重大/軽微)

| 工程 | 重大 | 軽微 |
|---|---|---|
| ①JA最終稿 | 1 | 5 |
| ②EN Rewrite前 | 2 | 5 |
| ③EN Rewrite後 | 0 | 5 |
| ④Checker最終(blocking/non_blocking) | 0 | 16 |
| ⑤独立評価 | 1 | 5 |

### 遷移

| 遷移 | 重大 | 軽微 |
|---|---|---|
| ①→②新規発生 | 1 | 0 |
| ②→③Rewrite修正 | 2 | 0 |
| ②→③Rewrite新規発生(最終本文に残る) | 0 | 0 |
| (参考)②→③Rewrite新規発生→Checker loop内で修正済(一時) | 0 | 0 |
| ④→⑤Checker見逃し(③EN残存かつ④非BLOCKING/未検出) | 0 | 5 |
| (参考)同、①JAのみ残存を含む | 1 | 5 |

Checker見逃し内訳: ACCEPTABLE/QUALITYとして検出済だが非BLOCKING=5件、未検出=0件。

---
## ai_control P2 rep2

Checker最終: RESOLVED_REWRITE_THEN_DOWNGRADE、cycle=4、Rewrite: cycle1(2文修正)・cycle2(blackmail文削除+段落再構成)。cycle別blocking/non-blocking: c1=3/12,c2=2/2,c3=0/4,c4(judge-only)=0/9

### NG台帳

| NG ID | 重大度 | fact_id | 該当文(全文) | ①JA | ②EN前 | ③EN後 | ⑤独立 | ④Checker検出 | Rewrite修正 | 備考 |
|---|---|---|---|---|---|---|---|---|---|---|
| ai-p2r2-01 | 軽微 | EVID-008 | JA「AIは、用意された世界の中で敵を探し、課題をクリアするつもりでした。」/EN(Rewrite前)「The AI was supposed to look for enemies and complete tasks inside the prepared world.」(修正後EN「The AI was supposed to complete tasks.」) | 発生 | 残存 | 修正済 | 残存 | BLOCKING | あり | 台帳はCTF課題の遂行まで。「敵を探す」は台帳外の軽い具体化。Checkerはcycle1でBLOCKING、本基準では軽微。EN=Rewriteで修正済、JAは残存。 |
| ai-p2r2-02 | 軽微 | なし(EVID-008のCTF) | JA「これは、ネット上に隠された情報を探す宝探しのような競技です。」/EN「It is a treasure hunt in which players search for hidden information online.」 | 発生 | 残存 | 残存 | 残存 | ACCEPTABLE | なし | CTFの定義は台帳外の軽い具体化(cycle1でBLOCKING候補→2nd opinionで降格)。 |
| ai-p2r2-03 | 軽微 | EVID-008 | JA「ところが、ゲーム会場の設計に穴がありました。」/EN「There was a hole in the design of the game site.」 | 発生 | 残存 | 残存 | 残存 | ACCEPTABLE | なし | 台帳は設定ミス(misconfigured)。「設計の穴」は性質の具体化。ENは第三者設定不備文の欠落(-08)により根拠なく残る形になった。 |
| ai-p2r2-04 | 軽微 | EVID-008 | JA「世界征服の始まりというより、ゲーム会場の扉を閉め忘れた事件です。」/EN「So this was less the beginning of world domination than an incident in which someone forgot to close the door to the game site.」 | 発生 | 残存 | 残存 | 残存 | ACCEPTABLE | なし | 「誰かが閉め忘れた」という過失・責任の描写は台帳外(設定不備は事実)。 |
| ai-p2r2-05 | 軽微 | EVID-008 | JA「その結果、ゲームの中で動いているはずのAIが、三つの組織の実際のシステムに不正に触れられる状態になりました。」/EN「As a result, an AI that was supposed to be operating inside the game was able to improperly access the real systems of three organizations.」 | 発生 | 残存 | 残存 | 残存 | ACCEPTABLE | なし | 【本委任で追加】3件の事案(複数モデル)を単一のAIの出来事のようにまとめ、「As a result」で防護策欠如と結びつける範囲・因果の曖昧さ。Checkerはcycle2-3で繰り返し指摘しACCEPTABLE。E_ai_controlのNG件数には含めていなかった。 |
| ai-p2r2-06 | 軽微 | CONTROL-003 | JA「関連する評価では、最新の内部テストモデルが標的を実在すると認識した時点で停止しました。」/EN「In a related evaluation, the latest internal test model stopped when it recognized that the target was real.」 | 発生 | 残存 | 残存 | 残存 | ACCEPTABLE | なし | 【本委任で追加】台帳ではAnthropicの3事案の話。「関連する評価」「別に報告された事案」(AISI)と主体を名指ししない曖昧さ。E_ai_controlは「誤りまでは至らない」としNG件数外だったが、本基準の「対象の曖昧さ=軽微」を適用して追加。 |
| ai-p2r2-07 | 重大 | EVID-006(無関係) | EN(Rewrite cycle1が挿入)「In a simulated safety evaluation, Claude Opus 4 attempted blackmail in 84% of rollouts.」 | 該当なし | 該当なし | RW新規→修正済 | 該当なし | BLOCKING | あり | 元文(第三者設定不備)が精度検査の誤紐付け(number_mismatch vs EVID-006)でReplace対象になり、無関係な別事案の文に置換。CTF記事に別評価の数値事実が混入し読者に誤った文脈を与える。cycle2でBLOCKING検出→削除済。最終ENには残らない。元文自体は正しかった(Checker側の誤検出起因)。 |
| ai-p2r2-08 | 軽微 | EVID-008 | EN最終「There was a hole in the design of the game site. It also lacked the cyber safety measures…」(JA「第三者が用意した評価環境の設定が不十分で、インターネットにつながる可能性があったのです。」に相当するENが欠落) | 該当なし | 該当なし | 発生 | 残存 | 未検出 | あり | 上記07の置換→削除の副作用で、EVID-008の核(第三者評価環境の設定不備・インターネット接続可能性)がENから消失。JAには残るためJA/EN不一致。ただしIn one lineとリード文でisolation不備は読み取れ、意味逆転はなし=軽微。元内容欠落を③の残存NGとして計上。Checkerはこの欠落自体を指摘していない。 |

注: 該当なし=その工程の本文に当該NGが存在しない。⑤残存は③ENまたは①JAのいずれかに残る意味。

### 工程別集計(重大/軽微)

| 工程 | 重大 | 軽微 |
|---|---|---|
| ①JA最終稿 | 0 | 6 |
| ②EN Rewrite前 | 0 | 6 |
| ③EN Rewrite後 | 0 | 6 |
| ④Checker最終(blocking/non_blocking) | 0 | 9 |
| ⑤独立評価 | 0 | 7 |

### 遷移

| 遷移 | 重大 | 軽微 |
|---|---|---|
| ①→②新規発生 | 0 | 0 |
| ②→③Rewrite修正 | 0 | 1 |
| ②→③Rewrite新規発生(最終本文に残る) | 0 | 1 |
| (参考)②→③Rewrite新規発生→Checker loop内で修正済(一時) | 1 | 0 |
| ④→⑤Checker見逃し(③EN残存かつ④非BLOCKING/未検出) | 0 | 6 |
| (参考)同、①JAのみ残存を含む | 0 | 7 |

Checker見逃し内訳: ACCEPTABLE/QUALITYとして検出済だが非BLOCKING=5件、未検出=1件。

---
## ai_control 従来版 rep1

Checker最終: RESOLVED_STAGE2_DOWNGRADE、cycle=1、Rewrite: なし(③=②と同一)

### NG台帳

| NG ID | 重大度 | fact_id | 該当文(全文) | ①JA | ②EN前 | ③EN後 | ⑤独立 | ④Checker検出 | Rewrite修正 | 備考 |
|---|---|---|---|---|---|---|---|---|---|---|
| ai-ctl-01 | 軽微 | EVID-011 | JA「主に関わったのは、内部だけで使う研究用プロトタイプでした。」/EN「The main actors were research prototypes used only inside the company.」 | 該当なし | 発生 | 残存 | 残存 | QUALITY | なし | 台帳は単一のprincipal model。ENの複数形「prototypes/actors」は拡張(JAは単複中立のためJAは非NG)。 |
| ai-ctl-02 | 軽微 | CONTROL-002/EVID-010 | JA「特に、AIが有害な行動を取る傾向まで実証された、という意味ではありません。」/EN「In particular, it does not mean that AI was shown to be inclined to take harmful actions.」 | 発生 | 残存 | 残存 | 残存 | ACCEPTABLE | なし | 本事件で有害傾向が実証されなかったとする記述は台帳にない。台帳は枠組み(CONTROL-002)と制御境界失敗(EVID-010/011)のみ。700体がHugging Face攻撃に参加した事実とやや緊張する境界例だが、否定の反転とまでは言えず軽微(Fable要確認の境界)。 |
| ai-ctl-03 | 軽微 | EVID-010/011 | EN In one line「The AI did not rebel; it bypassed isolated systems through a chain of weaknesses, credentials, and loose safeguards.」 | 該当なし | 発生 | 残存 | 残存 | QUALITY | なし | 「反乱していない」の断定(EVID-010 notesは「AI takeoverと呼ぶな」で方向は整合)。JAは「AIの大反乱というより」と緩い表現でNGなし。 |
| ai-ctl-04 | 軽微 | EVID-010 | JA「壁の中に通路を見つけ、掲示板で攻略情報を交換していた」/EN「exchanged tips on a message board」 | 発生 | 残存 | 残存 | 残存 | QUALITY | なし | 掲示板の存在は台帳どおりだが、交換内容が「攻略情報」であることは台帳になし。 |
| ai-ctl-05 | 軽微 | EVID-011 | JA「隔離したつもりの部屋に、通路と鍵が残っていた」/EN「a passage and keys being left behind in a room we thought we had isolated」 | 発生 | 残存 | 残存 | 残存 | ACCEPTABLE | なし | 資格情報が環境内に残されていた経緯は台帳になし(chained credentialsのみ)。 |

注: 該当なし=その工程の本文に当該NGが存在しない。⑤残存は③ENまたは①JAのいずれかに残る意味。

### 工程別集計(重大/軽微)

| 工程 | 重大 | 軽微 |
|---|---|---|
| ①JA最終稿 | 0 | 3 |
| ②EN Rewrite前 | 0 | 5 |
| ③EN Rewrite後 | 0 | 5 |
| ④Checker最終(blocking/non_blocking) | 0 | 22 |
| ⑤独立評価 | 0 | 5 |

### 遷移

| 遷移 | 重大 | 軽微 |
|---|---|---|
| ①→②新規発生 | 0 | 2 |
| ②→③Rewrite修正 | 0 | 0 |
| ②→③Rewrite新規発生(最終本文に残る) | 0 | 0 |
| (参考)②→③Rewrite新規発生→Checker loop内で修正済(一時) | 0 | 0 |
| ④→⑤Checker見逃し(③EN残存かつ④非BLOCKING/未検出) | 0 | 5 |
| (参考)同、①JAのみ残存を含む | 0 | 5 |

Checker見逃し内訳: ACCEPTABLE/QUALITYとして検出済だが非BLOCKING=5件、未検出=0件。

---
## 既存評価(E_ai_control.md)との差分

- E_ai_controlのNG件数(最終ベース): P2 rep1=6(+Rewrite前の主体1)、P2 rep2=4+Rewrite由来、従来版=5。本台帳: P2 rep1=重大2(うちEN最終に残るのは0)+軽微5、P2 rep2=重大1(一時)+軽微7、従来版=軽微5。
- 差分理由: (1) P2 rep1: 監獄比喩(範囲(a))と主体(propensity)を重大、ほか5件を軽微に再ラベル。E_ai_controlの因果1件は-07に統合。(2) P2 rep2: E_aiの台帳外(b)「敵を探す」は-01(軽微、Rewriteで修正済ENだがJA残存)、(a)=-02、(c)=-03、因果=-04。本委任で追加=-05(単一AIが3組織へ+As a result)、-06(関連する評価=主体の曖昧)。E_aiが「重大な不具合」とした無関係文置換は-07(重大・一時・cycle2で修正)、同(3)のEN欠落は-08(軽微・③の残存NG)。(3) 従来版: E通り5件(-01〜05)。
- 注意(Rewrite起因の分離): P2 rep2の置換元文(第三者の設定不備)は、Checkerが誤紐付け(EVID-006/CONTROL-004へのnumber_mismatch precheck floor)でBLOCKING扱いした結果、置換対象となった。元文自体は台帳(EVID-008)と整合しており、-07は「Rewrite新規発生」だが原因はChecker側の誤検出である。
- 判定保留: なし(境界例2件、ai-p2r1-07とai-ctl-02は軽微としFable要確認と注記)。

# NG_sewer 工程別NG台帳(OPEN-233-E2E-STAGEWISE-NG-AUDIT-01 委任_A2、API呼び出しなし・既存成果物の再評価のみ)

工程: ①JA最終稿(ja_writer/revision2.md) ②EN Rewrite前(b1b/article.md) ③EN Rewrite後(Checker最終cycle en_text_after_rewrite、Rewriteなしは②と同一) ④Checker最終判定(最終cycleのblocking=重大/non_blocking=軽微。non_blockingは候補全件でNG実数ではない) ⑤独立評価(既存E_*.mdを③EN+①JAに対し本基準で再ラベル。⑤は③ENに加え①JAのみ残存を含む)。
重大度は指示の全工程同一基準を適用。同一誤りはJA/ENで同一NG IDを共有。「本委任で追加」はE_*.mdのNG件数に無かった項目。

---
## sewer P2 rep1(喜多方)

Checker最終: RESOLVED_STAGE2_DOWNGRADE、cycle=1、Rewrite: なし(③=②と同一)

### NG台帳

| NG ID | 重大度 | fact_id | 該当文(全文) | ①JA | ②EN前 | ③EN後 | ⑤独立 | ④Checker検出 | Rewrite修正 | 備考 |
|---|---|---|---|---|---|---|---|---|---|---|
| sewer-p2r1-01 | 軽微 | F-012 | JA「地下の管で全員をつなぐ作戦から、地域によっては家ごとに処理する作戦へ。」/EN「The strategy is changing from connecting everyone with underground pipes to treating wastewater at each home in some areas.」 | 発生 | 残存 | 残存 | 残存 | ACCEPTABLE | なし | F-012は集合処理区域以外の見直しのみ。「全員」を地下管接続としていた前提は過大。「地域によっては」の限定ありで逆転はしない。 |
| sewer-p2r1-02 | 軽微 | F-012 | JA「町の形に合わせて、汚水のルートを組み替えたわけです。」/EN「In other words, the city rearranged its wastewater routes to fit the shape of the town.」 | 発生 | 残存 | 残存 | 残存 | ACCEPTABLE | なし | 市の理由は維持管理費増+使用料収入減(直前文に正しく記載)。「町の形に合わせた」は台帳にない理由の追加。 |
| sewer-p2r1-03 | 軽微 | F-007 | JA「家々を地下の管でつなぎ、まとめて処理する集合処理。」/EN「One is collective treatment, which connects homes with underground pipes and treats the wastewater together.」 | 発生 | 残存 | 残存 | 残存 | ACCEPTABLE | なし | 地下管で接続する仕組みは台帳外(一般知識として妥当)。 |
| sewer-p2r1-04 | 軽微 | F-007/F-012 | EN In one line「Towns are rethinking wastewater treatment by matching shared sewers and household septic tanks to local conditions.」 | 該当なし | 発生 | 残存 | 残存 | ACCEPTABLE | なし | 喜多方市1例を複数の町の動向へ一般化。JAにIn one line相当なし(EN固有)。 |
| sewer-p2r1-05 | 軽微 | F-007 | EN「In areas where homes are spread out, septic tanks installed at each home may be better.」(JA「家ごとに設置する浄化槽が有利になり得ます」) | 該当なし | 発生 | 残存 | 残存 | QUALITY | なし | F-007は経済性の比較。ENで「better」(直前の密集側は「more economical」)。JAは「有利」で経済的が省略されるが、直前の「経済的に有利」と対句で読めるためJAは非NG(境界)。 |
| sewer-p2r1-06 | 軽微 | F-001 | JA「下水道管路の総延長は…約五十万キロ。そのうち…約四万キロ、約七パーセント」/EN「The total length of sewer pipes was about 500,000 kilometers…」(F-001の「都市下水路を除く」不記載) | 発生 | 残存 | 残存 | 残存 | QUALITY | なし | 【本委任で追加】数値は一致。集計範囲の限定「都市下水路を除く」が示されない軽い範囲曖昧。E_sewerは「妥当なACCEPTABLE(軽微)」と記載のみでNG件数に入れていなかった。 |

注: 該当なし=その工程の本文に当該NGが存在しない。⑤残存は③ENまたは①JAのいずれかに残る意味。

### 工程別集計(重大/軽微)

| 工程 | 重大 | 軽微 |
|---|---|---|
| ①JA最終稿 | 0 | 4 |
| ②EN Rewrite前 | 0 | 6 |
| ③EN Rewrite後 | 0 | 6 |
| ④Checker最終(blocking/non_blocking) | 0 | 14 |
| ⑤独立評価 | 0 | 6 |

### 遷移

| 遷移 | 重大 | 軽微 |
|---|---|---|
| ①→②新規発生 | 0 | 2 |
| ②→③Rewrite修正 | 0 | 0 |
| ②→③Rewrite新規発生(最終本文に残る) | 0 | 0 |
| (参考)②→③Rewrite新規発生→Checker loop内で修正済(一時) | 0 | 0 |
| ④→⑤Checker見逃し(③EN残存かつ④非BLOCKING/未検出) | 0 | 6 |
| (参考)同、①JAのみ残存を含む | 0 | 6 |

Checker見逃し内訳: ACCEPTABLE/QUALITYとして検出済だが非BLOCKING=6件、未検出=0件。

---
## sewer P2 rep2(松山・再実行版)

Checker最終: RESOLVED_STAGE2_DOWNGRADE、cycle=1、Rewrite: なし(③=②と同一)

### NG台帳

| NG ID | 重大度 | fact_id | 該当文(全文) | ①JA | ②EN前 | ③EN後 | ⑤独立 | ④Checker検出 | Rewrite修正 | 備考 |
|---|---|---|---|---|---|---|---|---|---|---|
| sewer-p2r2-01 | 軽微 | F-010 | JA「そこで松山市が考えたのは、街全体を同じ方法で処理するのではなく、家の集まり方に合わせて作戦を変えることです。」/EN「So Matsuyama City decided not to use the same method across the whole city, but to change its approach to fit how homes are grouped.」 | 発生 | 残存 | 残存 | 残存 | QUALITY | なし | F-010は市街化区域/調整区域の区分方針(理由は老朽化・災害・人口減少の財政面)。住宅密度基準は環境省の一般論(F-007)を市の方針に転用。 |
| sewer-p2r2-02 | 軽微 | F-007/F-010 | JA「街の人口密度が、汚水の進路を決めるわけです。」/EN「The population density of the city decides the route the wastewater takes.」(見出し「Let the City's Density Decide What Comes After the Toilet」も同一主張) | 発生 | 残存 | 残存 | 残存 | QUALITY | なし | 密度決定論の過剰な断定。意味逆転はなし。 |
| sewer-p2r2-03 | 軽微 | F-007/F-010 | JA「トイレを流すたびに、街の形と人口の変化が、地下の仕組みにまで影響している。」/EN「Every time we flush the toilet, the shape of the city and changes in its population affect the system underground.」 | 発生 | 残存 | 残存 | 残存 | ACCEPTABLE | なし | 台帳外の因果断定(修辞)。 |
| sewer-p2r2-04 | 軽微 | F-010 | EN In one line「Matsuyama City will choose shared sewers or household treatment tanks according to how densely homes are grouped.」 | 該当なし | 発生 | 残存 | 残存 | QUALITY | なし | 未来形(台帳は2024-04-01公表の方針)+住宅密度基準(-01と同系の誤りだがEN固有文のため別ID)。JAにIn one line相当なし。 |
| sewer-p2r2-05 | 軽微 | F-007 | JA「汚水を街の地下に張りめぐらせた管で集める」「みんなの汚水を一つの流れに乗せる」/EN「collected through pipes spread under the city」「everyone's wastewater is put into one flow」 | 発生 | 残存 | 残存 | 残存 | ACCEPTABLE | なし | 地下管で集める仕組みは台帳外の軽い具体化。 |
| sewer-p2r2-06 | 軽微 | F-005/F-010 | JA「合併処理浄化槽」→EN「household wastewater treatment tanks」「septic tanks」(「combined」消失・用語不統一) | 該当なし | 発生 | 残存 | 残存 | 未検出 | なし | 単独/合併の区別がENで落ちる。直後でkitchen/bath/washing明示のため実害は小。Checker指摘は住宅密度基準の件で、用語の件は未指摘。 |

注: 該当なし=その工程の本文に当該NGが存在しない。⑤残存は③ENまたは①JAのいずれかに残る意味。

### 工程別集計(重大/軽微)

| 工程 | 重大 | 軽微 |
|---|---|---|
| ①JA最終稿 | 0 | 4 |
| ②EN Rewrite前 | 0 | 6 |
| ③EN Rewrite後 | 0 | 6 |
| ④Checker最終(blocking/non_blocking) | 0 | 14 |
| ⑤独立評価 | 0 | 6 |

### 遷移

| 遷移 | 重大 | 軽微 |
|---|---|---|
| ①→②新規発生 | 0 | 2 |
| ②→③Rewrite修正 | 0 | 0 |
| ②→③Rewrite新規発生(最終本文に残る) | 0 | 0 |
| (参考)②→③Rewrite新規発生→Checker loop内で修正済(一時) | 0 | 0 |
| ④→⑤Checker見逃し(③EN残存かつ④非BLOCKING/未検出) | 0 | 6 |
| (参考)同、①JAのみ残存を含む | 0 | 6 |

Checker見逃し内訳: ACCEPTABLE/QUALITYとして検出済だが非BLOCKING=5件、未検出=1件。

---
## sewer 従来版 rep1(喜多方)

Checker最終: RESOLVED_STAGE2_DOWNGRADE、cycle=1、Rewrite: なし(③=②と同一)

### NG台帳

| NG ID | 重大度 | fact_id | 該当文(全文) | ①JA | ②EN前 | ③EN後 | ⑤独立 | ④Checker検出 | Rewrite修正 | 備考 |
|---|---|---|---|---|---|---|---|---|---|---|
| sewer-ctl-01 | 軽微 | F-012 | JA「下水道に、引っ越し作戦が持ち上がっています。」/EN「A move is being planned for Japan’s sewer systems.」(見出し・In one line「As Japan’s sewer pipes age, some areas may shift…」も同系) | 発生 | 残存 | 残存 | 残存 | QUALITY | なし | 喜多方市1例を全国/下水道一般の動向として提示。ENで「Japan's」追加(JAより強化、新規NGではなく悪化)。 |
| sewer-ctl-02 | 軽微 | F-012 | JA「古くなった管に向き合いながら、地域に合う仕組みへ組み替える。」/EN「As communities deal with aging pipes, they are changing to systems that fit their areas.」 | 発生 | 残存 | 残存 | 残存 | ACCEPTABLE | なし | 複数地域の動向への一般化。 |
| sewer-ctl-03 | 軽微 | F-012 | JA「合併処理浄化槽を使う個別処理区域にします。浄化槽の設置費には、上乗せ補助を行う方針です。」/EN「the city will create areas for individual treatment … plans to provide extra subsidies」 | 発生 | 残存 | 残存 | 残存 | QUALITY | なし | F-012は2021-04-01公表済み(見直した/実施するとした)。未来形は不正確。 |
| sewer-ctl-04 | 軽微 | F-012 | JA「背景には、地下で働く管の高齢化があります。」/EN「The reason is that the pipes working underground are growing old.」 | 発生 | 残存 | 残存 | 残存 | QUALITY | なし | 喜多方市の理由は維持管理費増+使用料収入減。ENは「The reason is」で断定強化(同一NGの悪化)。 |
| sewer-ctl-05 | 軽微 | F-012 | JA「福島県喜多方市」/EN「Kitakata City in Fukushima Prefecture」 | 発生 | 残存 | 残存 | 残存 | 未検出 | なし | 事実として妥当だが台帳に県名なし(台帳未提示事項の軽い具体化)。 |
| sewer-ctl-06 | 軽微 | F-012/F-007 | JA「集合処理区域では、地下の管を通して汚水をまとめて処理します。」/EN「In areas with shared treatment, wastewater is sent through underground pipes and treated together.」 | 発生 | 残存 | 残存 | 残存 | ACCEPTABLE | なし | 地下管の仕組みは台帳外の軽い具体化。 |
| sewer-ctl-07 | 軽微 | F-001 | JA「全国の下水道管路は、およそ五十万キロ」/EN「Japan’s sewer pipes total about 500,000 kilometers.」(F-001の「都市下水路を除く」不記載) | 発生 | 残存 | 残存 | 残存 | ACCEPTABLE | なし | 【本委任で追加】数値は一致。集計範囲の限定不記載。E_sewerではNG件数に入れていなかった。 |

注: 該当なし=その工程の本文に当該NGが存在しない。⑤残存は③ENまたは①JAのいずれかに残る意味。

### 工程別集計(重大/軽微)

| 工程 | 重大 | 軽微 |
|---|---|---|
| ①JA最終稿 | 0 | 7 |
| ②EN Rewrite前 | 0 | 7 |
| ③EN Rewrite後 | 0 | 7 |
| ④Checker最終(blocking/non_blocking) | 0 | 16 |
| ⑤独立評価 | 0 | 7 |

### 遷移

| 遷移 | 重大 | 軽微 |
|---|---|---|
| ①→②新規発生 | 0 | 0 |
| ②→③Rewrite修正 | 0 | 0 |
| ②→③Rewrite新規発生(最終本文に残る) | 0 | 0 |
| (参考)②→③Rewrite新規発生→Checker loop内で修正済(一時) | 0 | 0 |
| ④→⑤Checker見逃し(③EN残存かつ④非BLOCKING/未検出) | 0 | 7 |
| (参考)同、①JAのみ残存を含む | 0 | 7 |

Checker見逃し内訳: ACCEPTABLE/QUALITYとして検出済だが非BLOCKING=6件、未検出=1件。

---
## 既存評価(E_sewer.md)との差分

- E_sewerのNG件数: P2 rep1=5(範囲2+因果1+台帳外1+R2→EN 1)、P2 rep2=5(範囲1+因果3+台帳外1)+R2→EN用語1、従来版=6。本台帳: P2 rep1=6、P2 rep2=6、従来版=7。
- 差分理由: (1) E_sewer「範囲」2件は(a)=-01、(b)=-04に分離し、R2→EN「better」を-05として別計上(Eは(3)欄に記載しNG一覧外だった)。(2) P2 rep1と従来版に、E_sewerが「妥当なACCEPTABLE(軽微)」と言及のみだったF-001「都市下水路を除く」不記載を、軽微基準(範囲の曖昧さ)に従い1件ずつ追加(sewer-p2r1-06、sewer-ctl-07、本委任で追加)。(3) P2 rep2のEN「合併」消失(E (3)欄)を-06としてNG計上。重大は全run0件(Eと整合)。
- 工程別: sewer 3runともRewriteなし(③=②)。s4のnon_blocking(14/14/16)はNG実数ではなく候補全件(多くは台帳整合の決定論検査誤検知)。
- 判定保留: なし。

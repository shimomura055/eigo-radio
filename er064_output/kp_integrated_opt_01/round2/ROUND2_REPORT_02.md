# ROUND2_REPORT_02: KP統合最適化 Round 2(M2固定 x P0/P3/P5)
管理ID: FAMILY-X-KP-INTEGRATED-OPTIMIZATION-TRIAL-01 委任_02 / 2026-10-13 / Trial専用(Production code/Prompt/DB/gate無変更、音声生成なし) / **採用判断なし** / Status案=USER_DECISION_REQUIRED候補(VALIDATEDにも未到達扱い。n小標本)
モデル: gpt-6-luna(全55 call、Production同一=最新モデル原則の例外「比較可能性」。最上位系モデルでの検証は未実施)。
**前提の訂正(委任_01、Fable受理済み)の再掲**: (a)placeholder照合単独では`pump one's fist`は回収できない(Wiktionary DBに見出しなし、Coffee v5で新規ヒット0)。M2=(a)+(b2)ルール所有格3-gram+(c)予約枠cap3(追加LLM呼出なし)。`be behind price increases`は(b1)LLM補助抽出がないと供給不能で、本Roundも(b1)を含めず記録のみ(全条件0/n、候補に無い)。

## 0. 実績
| 項目 | 値 |
|---|---|
| 新規job | 18(Stage1 14 = Coffee M2P5 Std/Adv x3 + meta/hormuz M2P5 Std/Adv x2、Stage2 4 = Coffee M2P5 run4-5)、55 call、rc=0、自動retry/再起動/外部停止0、STOP/STOP_ALL/KP用STOP_NOTICE不在(Melos STOP_NOTICEは別件・run_e2e_01限定) |
| 費用(実測) | **JPY18.2794 / Round2上限65・ハードストップ70**(見積19.1[保守]に対し実績18.28)。本Trial累計 80.72+18.28 = **99.00 / 枠300、累計上限150.72以内** |
| 時間 | Stage1 約5.6分、Stage2 約2.1分(6並列、job平均約100秒) |
| 再利用 | Coffee M2P0/M2P3(n=3)とmeta/hormuz M2P0/M2P3(n=2)はRound1 runを再利用。msg_sha256・rows_sha256が全12セルで現行構築と一致、shortlists_r1.json sha一致(`reuse_check_r2.json`)。基準M0P0もRound1(Coffee)/前回Phase2 C0(meta/hormuz)の再利用 |
| Production state | 8ファイルsha256が前後不変(`state_guard_r2.json`: unchanged_after_stage1/2 = true) |
| test | `er064_kp_int_02_test_01.py` 12件PASS、Round1 test 22件は21 PASS + 1件は「tracked .pyの差分」検査で自Trialの`er064_kp_int_01_prompts.py`(P5追記)に反応(Production .pyではない。commit後に再実行して確認)。`take time`型を機械側で削除していない既存testPASS(`test_take_time_type_not_deleted`) |

## 1. P5(Step A、詳細は`prompts_r2.json`・`plan_r2.md`)
P3を土台に一から書いた全文。(i)Production P0の「比喩・感情表現を同格」文を逐語復活 (ii)辞書見出しの定着表現は擬人的・比喩的に使われても定着表現として評価、創作的な言い回しは「筆者がその場で作った一回限りの言い回し」に限定 (iii)低優先抑制(P3の「基本表現・透明表現は価値の高い候補が残る限り枠を使わない」+入れ替え確認)を逐語維持 (iv)出力契約の再確認(日本語グロス括弧書き禁止・normalization_note必須)。
- token(text-only): P0 1402 / P3 1278(Std)・1295(Adv) / **P5 1451(Std、P0比+3.5%、P3比+13.5%)・1468(Adv、+4.7%、+13.4%)**。P3比+13%は復活文+定着規則+出力再確認。
- 注意: M2固定のため候補行に`match:`が付かない。P3の注釈説明にあった`match:`の説明文はP5で削除(Fable判断に整合)。P5 vs P3の差にはこの削除も含まれる(分離未検証)。
- Rule7(所有格35組)非干渉(静的): 【学ぶ単位】段落(動詞は基本形へ)はP3と逐語同一、所有格/人称/活用形に触れる指示を追加せず(test)。

## 2. 結果(Coffee、Std+Adv合算、score上限84。完全な表は`report_tables_r2.md`、最終5件全文は`analysis_r2.md`)
| 条件 | n/Lv | score合計 | Std(37) | Adv(47) | pump | time lag(Adv) | 低優先枠/run Std / Adv / 平均 | 創作比喩Imp | 選定INVALID | canon INVALID | Redundancy NG | 全gate PASS | 費用/job |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| M0P0(基準) | 3 | 47.0 | 27.0 | 20.0 | 2/6 | 0/3 | 2.00 / 0.67 / 1.33 | 0 | 0/6 | 1/6 | 0/6 | 5/6 | 0.87 |
| M2P0 | 3 | **71.3** | 33.3 | 38.0 | 6/6 | 3/3 | 1.67 / 0.67 / 1.17 | 0 | 0/6 | 1/6 | 0/6 | 5/6 | 0.89 |
| M2P3 | 3 | 62.0 | 29.0 | 33.0 | 4/6 | 3/3 | 1.00 / 0.33 / **0.67** | 0 | 0/6 | 0/6 | 0/6 | 6/6 | 0.93 |
| **M2P5 (同一n=3: run1-3)** | 3 | 67.0 | 33.0 | 34.0 | 5/6 | 3/3 | 1.00 / 0.67 / 0.83 | 0 | 0/6 | 0/6 | 0/6 | 6/6 | 1.00 |
| M2P5 (n=5、全run) | 5 | 67.2 | 32.4 | 34.8 | 9/10 | 5/5 | 1.20 / 0.40 / 0.80 | 0 | 0/10 | 0/10 | 0/10 | 10/10 | 0.98 |
(n=3は方向の目安。P5のn=5は対照のn=3より大きいため、比較は同一n=3行を主とし、n=5は参考。)
- (1) **pump不採用は起きなかった**: P5はpump 9/10(n=3範囲で5/6)。P1/P4型の0/6は再現せず、「比喩・感情表現を同格」復活+定着表現規則と整合する結果(因果は未検証、n小)。M2P0(6/6)よりやや低い。
- (2) **低優先枠の減少は概ね維持**: Std 1.00(n=3、M2P0 1.67 / M2P3 1.00と同等)。ただしn=5では1.20(`take time`が1/5出現)。`right away`はStd 0/5(基準3/3、M2P0 2/3)で維持。`on a regular basis`はStd 5/5で残る(M2P3 3/3と同傾向、アンカー基準では低優先だがA2学習者への価値が低いとは限らない点は未評価)。Adv 0.67(n=3)/0.40(n=5)。
- (3) score: P5(n=3)67.0はM2P3(62.0)を上回るが**M2P0(71.3)には届かない**(差は主にAdvで、`hold on`/`price tag`等の枠が入れ替わる)。Std 33.0はM2P0 33.3と同等。
- (4) 層2(gate): P5は選定INVALID 0/10、canonicalization INVALID 0/10(pump項目は10回中9回`pump one's fist`のまま`inherit_selection_normalization`でPASS。活用形+person同時変化の予測INVALIDは顕在化せず[選定LLMが最初から基本形で出したため。予測の安全の証拠ではない])、Redundancy NG 0/10、全gate PASS 10/10。日本語グロス括弧違反0。P1/P4型の契約遵守劣化は無し(出力再確認文の効果かは未分離)。source_span超え拡張(OPEN-310新サブクラス)はP5で0/18 job(Round1は6/88)。
- (5) 費用・推論: P5 1 jobあたり費用 約0.98〜1.00(M2P0 0.89、+10〜12%)、選定のreasoning token Std 5756 / Adv 3473(M2P0 3141 / 2842、M2P3 3607 / 3957)、Std所要約121秒(M2P0 96秒)。Std P5は推論量が大きい。
- 創作比喩のImportant混入は全条件0(Coffee v5 shortlistに該当候補が無いための測定上の0。P5の創作比喩規則の効果はここでは測れていない)。

## 3. アンカー別(Coffee、採用/有効run、[R]=full到達 [r]=断片のみ [x]=候補に無し)
Std: pump 5/5(M2P0 3/3、M2P3 2/3)[R]、push prices up 5/5(断片`prices up`のみ到達[r])、raw beans 5/5、roasting 1/5、on a regular basis 5/5、right away 0/5、take time 1/5。
Adv: pump 4/5(M2P0 3/3、M2P3 2/3)[R]、time lag 5/5、show up 5/5、come down 5/5、hold on 2/5、be behind price increases 0/5 [x](供給不能=(b1)要)、roasting/raw beans/on a regular basis/right away/take time 0/5。
不選定の有用表現(候補に存在): Adv `roasting`/`raw beans`は全M・全Pで0/n(Advの5枠は`show up/come down/hold on/come with`等で埋まる。Round1から変わらず)。

## 4. 他記事回帰(meta/hormuz、n=2。基準M0P0=前回Phase2 C0 n=3、M2P0/M2P3=Round1 n=2)
- meta: `concierge`採用(Std+Adv、n=4): 基準4/6、M2P0 3/4、M2P3 0/4、**M2P5 1/4**(Adv 1/2、Std 0/2)=M2P3の0/4からは部分回復だがM2P0には届かず。`inappropriate`(形容詞)がStd 2/2で入る(M2P3と同傾向)、`take care of`がAdv 2/2。`behind the scenes`/`contract worker`/`unintentionally`/`no way(to know)`は維持。canonicalization INVALID 0/4、Redundancy NG 0/4。
- hormuz: Redundancy NG 1/4(Std 1/2)=M2P0 1/4、M2P3 1/4と同等(基準5/6)。canon INVALID 0/4(M2P0は1/4)。`give back gains`の表示拡張はP5 Advで2/2出るがcanonicalizationはPASS。`center stage`は4/4、`flashy`が4/4で新たに入る(plain adjective、価値は要判断)。`sea blockade`はAdv 1/2のみ(Topicは`Brent crude`へ)。
- n=2のため断定しない。metaの悪化(M2P3由来)が完全には回復しなかった事実のみ記載。

## 5. 失敗要因と判定(事実のみ、採用判断なし)
| 要因 | 所見 |
|---|---|
| 供給不足 | `be behind price increases`は(b1)なしで依然0。それ以外のアンカー(pump/time lag)はM2で到達 |
| 選定順位 | P5は低優先枠(Std)の減少をM2P3並みに維持しつつpump採用を回復。ただしAdvの枠(`hold on`/`comes with`等)でM2P0に劣る。Adv `roasting`/`raw beans`はどのPでも出ない |
| 正規化 | P5で顕在化せず(0/18)。所有格35組に該当0(pump項目は基本形のまま出る) |
| 不安定 | P5 Jaccard 0.77(n=5)。n=3同士の比較は`analysis_r2.md`のrun別を参照 |
| 契約/Prompt設計 | 出力再確認文を入れたP5は契約違反0。P1/P4型の劣化なし |
| 費用 | P5は推論量・費用がP0比+10〜12%(Std推論約1.8倍) |

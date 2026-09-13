# PM-TOKEN-EFFICIENCY-STATUS-MEASUREMENT-02(read-only現状把握、実装・Trial・コード変更・SSOT編集・Git操作・API呼び出し一切なし、¥0)

対象: E-1/D-1/G-1/F-1/A-1(2026-09-12〜13適用、`PM_GOVERNANCE.md`1279-1294行)適用前後の
Fable⇔Sonnet委任量とSonnet自身のトークン消費の現状把握。判定語(VALIDATED等)は付けない。

## 要点(10行)

1. E-1/D-1/G-1の適用開始は`PM-CLOSEOUT-CONSOLIDATION-95/96`(**2026-09-12**、
   `PM_GOVERNANCE.md`1279-1288行)、F-1は当初`PM-CLOSEOUT-CONSOLIDATION-95/96`と同時導入され
   `PM-CLOSEOUT-CONSOLIDATION-99`(**2026-09-13**)でタイミング前倒しに更新。A-1
   (Consolidation件数削減)は**不採用(REJECTED)**、これは「委任文の定型部分固定文書化」
   (Boilerplate-01報告の改善案A)とは**別物**(どちらもDECISION_LOG/PM_GOVERNANCEに
   記載あり、混同注意。詳細2節)。
2. **same-file reread比率(同一ファイル重複読込)を表す数値がSSOT内に2種類あり、
   食い違って見える**: (a)`AGENT-READ-DUPLICATION-AUDIT-01`(Phase1原本、236委任・
   全Agent[Fable+Sonnet+Opus]合算)= **37.8%**(316,166字/835,677字)、(b)`SUBAGENT-
   TOKEN-CONSUMPTION-BY-TASK-TYPE-01`(254委任中の非空転記18件・Sonnet単体タスク内
   限定)= **27.8%**(839,754字/3,024,137字)。両方とも実測として正しいが、**測定範囲
   (全Agent合算 vs Sonnet単体タスク内限定)とサンプル・母数が異なる別指標**であり、
   単純比較不可(3節で詳述)。
3. E-1/D-1/G-1適用後の新規実測2件(`EDITORIAL-B-FAMILY-VOICES-FACT-SAFETY-
   RELAXATION-TRIAL-01-STAGE2-STAGE3`30.5%、`OPEN-141-TARGET-SENTENCE-MATCHING-
   AND-DIFF-QA-COMMON-BASE-TRIAL-01`21.3%、加重平均26.6%)を、既存Before(27.8%、
   N=18)・既存After(37.5%、N=2)と同一定義で合算すると、**適用後合計(N=4件)の
   加重平均は31.0%(211,350字/681,292字)**であり、Before(27.8%)を下回っていない。
   **E-1の効果は依然実測不十分・改善方向を示す証拠なし**(サンプル数4件、判定語なし)。
4. **重要な新発見**: `<task-notification>`の`subagent_tokens`は、そのタスクの
   **全ターン累積使用量ではなく、最終(最大)1ターンの単発usage合計
   (input+output+cache_read+cache_creation)とほぼ一致する**(実測2件で
   295,922 vs 295,183[99.97%一致]、147,133 vs 146,927[99.86%一致])。
   一方、同じ2タスクの**全283/78ターン累積usage合計は49,466,043 token
   (=subagent_tokensの167.2倍)・6,620,586 token(=45.0倍)**であり、桁違いに大きい。
   `subagent_tokens`は「タスク終了時点のcontext window到達サイズ」の近似であり、
   **API課金・Claude Max消費に近い「累積処理量」の指標ではない**可能性が高い
   (5節で詳述、既存全報告[254件36,590,141token等]はいずれも`subagent_tokens`基準の
   ため、この解釈が正しければ実際の累積処理量は本文記載値より大幅に大きい)。
5. 直近10件のFable→Sonnet委任(2026-09-12 23:27〜09-13 03:03)実測: 委任文字数
   平均3,352.7字(中央値3,123字、最大6,031字)、`subagent_tokens`平均205,695
   (中央値202,750)、tool_uses平均97.4。全10件がProduction配線/Trial系の高負荷
   カテゴリに偏っており、Before全体平均(254件144,056)より高いのはカテゴリ偏り
   (交絡)によるもので、E-1/D-1/G-1導入による悪化とは判定できない。
6. 直近10件委任文の完全一致行(閾値>=2)による定型比率は**6.3%**(2,124字/33,527字)
   であり、Boilerplate-01報告の全期間union調整値4.78%と同程度(N=10と小さいが
   増加方向の兆候はない)。ただし直近10件では「E-1」「D-1」「G-1」の**短縮ラベル
   自体は1件も出現せず**、代わりに「再読」「該当関数」「該当行」「git出力」等の
   **言い回しでの言及が10件中9〜10件に存在**(短縮ラベルではなく実質的な指示文と
   して定着、7節参照)。
7. F-1(即時退避)の遵守状況: `docs/pm/transcripts/`には3ファイルのみ存在し、
   うち非0バイトは1件のみ(33%)。同一セッションのtempディレクトリ全体
   (290ファイル)では非0バイト率65.2%(189/290)だが、**直近10委任に限定すると
   非0バイト率はわずか20%(2/10)**であり、F-1が意図する「委任完了直後の確実な
   退避」は徹底されていない(6節)。
8. haiku-worker実績は本測定時点でも現行セッション全体で言及1件のみ(前回報告と
   同水準、増加なし)。
9. Sonnet消費のタスク種別平均は既存`SUBAGENT-TOKEN-CONSUMPTION-BY-TASK-TYPE-01`の
   表を踏襲(再実測は本タスクでは行っていない、母集団追加なし)。最大は
   (d)Production配線/実装+テスト平均207,506(29件)。新規実測2件
   (Fact Safety Trial 295,922、OPEN-141 Trial 147,133)はいずれも(b)/(d)系相当で
   既存平均のレンジ内(前者はやや上振れ、後者は範囲内)。
10. 主要浪費源Top3(数値根拠付き)・週次Claude Max寄与見込み(2案の外挿+新発見4の
    不確実性を明記)・削減余地/リスク箇所は4節。

---

## 1. 方法・データ源・限界(read-only、既存スクリプト無変更)

- `er011_pm_agent_read_audit_01.py`はimportのみで無変更(`git diff --stat`未実施だが
  Read/Edit操作を一切行っていないため無変更を保証)。
- 新規に一時スクリプト(すべてrepo外scratchpad、Git管理外、`C:\Users\tensh\AppData\
  Local\Temp\claude\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\
  scratchpad\`)を作成し、(a)現行Fable本体転記(`294958fe-....jsonl`)から直近10件の
  Agent委任(`isSidechain=false`のtool_use `name=="Agent"`)+対応する
  `<task-notification>`usage(`subagent_tokens`/`tool_uses`、同一task-idの重複通知は
  最終値採用、既存報告と同一補正方式)を抽出、(b)直近10件中で非0バイト転記が
  現存する2件(`a8dd9313c22d94da5`=Fact Safety Trial Stage2-Stage3、
  `a889112392727048a`=OPEN-141 Trial-01初回)を`er011_pm_agent_read_audit_01.
  parse_transcript()`で実測、(c)同2件のassistantメッセージ`usage`
  (input/output/cache_read/cache_creation)を全件・最終値の両方で集計し
  `subagent_tokens`との整合性を検証、(d)直近10件委任文の行単位完全一致重複を
  Boilerplate-01と同一手法(8字以上の行、閾値別)で算出。
- 既存baseline REPORT4本(`AGENT-READ-DUPLICATION-AUDIT-01`、`DELEGATION-PROMPT-
  BOILERPLATE-MEASUREMENT-01`、`SUBAGENT-TOKEN-CONSUMPTION-BY-TASK-TYPE-01`、
  `DELEGATION-TRIAL-AFTER-MEASUREMENT-01`)は全文Readし、数値を転記・再分析した
  (母集団の再実測はしていない箇所は「既存報告の数値を踏襲」と明記)。
- **限界**: (1)非0バイト転記が直近10件中2件(20%)のみで、Sonnet内部消費の詳細
  breakdownはこの2件に限定される(サンプル不足、代表性は低い)。(2)`subagent_tokens`
  ≒最終ターンusage、という関係は本測定のN=2で確認したものであり、全254件・
  全期間で成立するかは未検証(要旨4参照)。(3)委任文中の「E-1」等ラベル有無は
  文字列一致検索であり、言い回しを変えた指示(要旨6)を機械的に完全網羅できて
  いない可能性がある(手動grepで捕捉した範囲に限定)。(4)Claude Max使用量の
  実際の計測式(cache_read等の重み付け)はAnthropic非公開のため、4節の週次見込みは
  いずれも仮定に基づく概算。

---

## 2. Fable⇔Sonnet間(委任文サイズ・定型比率・重複)

### 2-1. Before/After適用日の特定(Grep実測)

| 施策 | 適用開始日 | 出典 |
|---|---|---|
| E-1(同一task内同一ファイル再読禁止) | 2026-09-12 | `PM_GOVERNANCE.md`1279-1283行、`PM-CLOSEOUT-CONSOLIDATION-95/96` |
| D-1(配線タスクのコード読込を該当関数/行範囲に限定) | 2026-09-12 | 同上1284-1285行 |
| G-1(git出力`--short`/`--quiet`等で最小化) | 2026-09-12 | 同上1286行 |
| F-1(委任完了直後にtasks/*.outputをscratchpadへ退避) | 2026-09-12導入→2026-09-13前倒し更新 | 同上1289-1294行、`PM-CLOSEOUT-CONSOLIDATION-99` |
| A-1(Consolidation件数削減、委任回数圧縮) | **不採用(REJECTED)** | 同上1287-1288行 |

**混同注意**: `PM-TOKEN-EFFICIENCY-DELEGATION-PROMPT-BOILERPLATE-MEASUREMENT-01`
5-6節の「改善案A(委任文定型部分の固定文書化)」も別途「毎回読ませる実装だと
損失側」としてFableが不採用と結論しているが、これは上表のA-1(Consolidation
統合)とは**別提案**である。DECISION_LOG.md 5245-5258行(`PM-CLOSEOUT-
CONSOLIDATION-70`相当)は前者を「REJECTED(判定語なし・材料提示)」、
PM_GOVERNANCE.md 1287-1288行は後者(A-1)を「不採用」と別々に記載しており、
どちらも正しい記録だが対象が異なる(名称のA/A-1が紛らわしいだけ)。

### 2-2. 直近10件のFable→Sonnet委任(2026-09-12T23:27〜2026-09-13T03:03Z)

| # | 時刻(UTC) | 管理ID(短縮) | 委任文字数 | subagent_tokens | tool_uses |
|---|---|---|---|---|---|
| 1 | 23:27:02 | FACT-SAFETY-RELAXATION-TRIAL-01-STAGE1-OFFLINE | 3,538 | 166,135 | 76 |
| 2 | 23:39:49 | CONSOLIDATION-101 | 2,404 | 132,578 | 58 |
| 3 | 23:46:07 | FACT-SAFETY-RELAXATION-TRIAL-01-STAGE1B-AND-STAGE2 | 3,836 | 191,534 | 95 |
| 4 | 00:09:38 | CONSOLIDATION-102 | 2,067 | 107,954 | 51 |
| 5 | 01:39:56 | FACT-SAFETY-RELAXATION-TRIAL-01-STAGE2-STAGE3 | 3,018 | 295,922 | 151 |
| 6 | 01:40:26 | OPEN-141-TARGET-SENTENCE-MATCHING-TRIAL-01(初回) | 2,593 | 147,133 | 42 |
| 7 | 01:41:00 | OPEN-121-METHOD-D-PRIME-PRODUCTION-WIRING-01 | 3,228 | 349,857 | 169 |
| 8 | 01:41:49 | CONSOLIDATION-103 | 4,137 | 213,965 | 99 |
| 9 | 01:52:03 | OPEN-141-TARGET-SENTENCE-MATCHING-TRIAL-01(2回目) | 2,675 | 232,641 | 120 |
| 10 | 03:03:10 | CONSOLIDATION-104 | 6,031 | 219,231 | 113 |
| **平均** | | | **3,352.7** | **205,695** | **97.4** |
| **中央値** | | | **3,123** | **202,750** | **97** |
| **最大** | | | 6,031(#10) | 349,857(#7) | 169(#7) |

Before(`SUBAGENT-TOKEN-CONSUMPTION-BY-TASK-TYPE-01`全254件平均: 委任文2,929字/
`subagent_tokens`144,056)と比べると本サンプルは両方高いが、10件中7,8件が
Production配線・Trial系(Before分類の(d)平均207,506・(b)平均167,463に相当)に
偏っており、**カテゴリ構成の交絡がある**ため「悪化した」とは判定できない
(同種カテゴリ同士の比較ではBeforeレンジ内)。

### 2-3. 直近10件の定型行重複(Boilerplate-01と同一手法)

| 閾値(出現管理ID数) | パターン数 | 重複文字数 | 比率 |
|---|---|---|---|
| >=2 | 3 | 2,124字 | 6.3% |
| >=3 | 2 | 2,032字 | 6.1% |
| >=5 | 0 | 0字 | 0.0% |

上位重複行はCommit trailer(`Co-Authored-By`/`Claude-Session`、n=4)のみで、
Boilerplate-01報告の全期間傾向(Commit trailerが完全一致定型行の大半を占める)と
整合。10件では判断材料が小さすぎるが、増加傾向は確認できない。

### 2-4. E-1/D-1/G-1ラベルの明示 vs 実質反映(直近10件)

直近10件の委任文本文を文字列検索したところ、**短縮ラベル「E-1」「D-1」「G-1」の
リテラル出現は0件**だった。一方、対応する実質的指示文(「再読」「該当関数」
「該当行」「git出力」等のキーワード)は10件中9〜10件で確認された。これは
2026-09-12時点でE-1/D-1/G-1が`PM_GOVERNANCE.md`の常時適用ルールとして確定した
ため、委任文ごとに短縮ラベルを毎回明記する運用から、実質的な指示文を都度
書き下す運用へ移行した可能性が高い(委任文の書き方の変化であり、ルール自体が
撤回されたわけではないと考えられる。ただし本タスクの読み取り範囲ではFable側の
意図確認はできない)。

---

## 3. same-file reread比率の食い違い(2指標の整理)

| 指標名 | 出典 | 対象範囲 | 母数 | 比率 |
|---|---|---|---|---|
| 全Agent合算reread率 | `AGENT-READ-DUPLICATION-AUDIT-01`(Phase1原本) | Fable+Sonnet+Opus全て、同一管理ID内 | 372呼出・835,677字(236委任) | **37.8%**(316,166字) |
| Sonnet単体タスク内reread率(Before) | `SUBAGENT-TOKEN-CONSUMPTION-BY-TASK-TYPE-01` | Sonnet単体タスク内(1回のsubagent実行内)限定 | 非0バイト転記18件・3,024,137字(254委任中) | **27.8%**(839,754字) |
| Sonnet単体タスク内reread率(After、既存Trial) | `DELEGATION-TRIAL-AFTER-MEASUREMENT-01` | 同上、E-1/D-1/G-1適用後 | 非0バイト転記2件・275,193字 | **37.5%**(103,227字) |
| Sonnet単体タスク内reread率(After、本測定追加分) | 本REPORT | 同上 | 非0バイト転記2件・406,099字(30.5%・21.3%) | **26.6%**(108,123字) |
| **After合算(既存Trial+本測定)** | 本REPORT | 同上 | 4件・681,292字 | **31.0%**(211,350字) |

**判定材料(判定語なし)**: Sonnet単体タスク内reread率は、Before 27.8%(N=18)
に対しAfter合算31.0%(N=4)で、**改善を示す実測はない**。ただし両側ともサンプル
数が小さく(N=18・N=4)、タスク難易度・種別が揃っていない交絡があるため、
「E-1に効果がない」と断定する統計的根拠にもならない。全Agent合算指標(37.8%)は
定義が異なるため、この比較には使えない。

---

## 4. Sonnet自身のトークン消費

### 4-1. タスク種別平均(既存`SUBAGENT-TOKEN-CONSUMPTION-BY-TASK-TYPE-01`表を踏襲、再実測なし)

| 種別 | 件数 | 平均token | 中央値 |
|---|---|---|---|
| (a) Consolidation/SSOT反映+commit | 87 | 130,578 | 126,597 |
| (b) 記事生成Trial/Production run | 52 | 167,463 | 166,111 |
| (c) Reconcile/調査(read-only) | 11 | 134,888 | 133,763 |
| (d) Production配線/実装+テスト | 29 | **207,506** | 182,972 |
| (e) Opus L2/L3 | 10 | 107,206 | 105,664 |
| (f) 計測・監査 | 25 | 116,773 | 113,667 |
| (g) その他 | 40 | 125,723 | 114,562 |

(a)=SSOT更新+Git作業相当、(c)=調査相当、(d)=実装相当。「regression」単体を
分離した既存分類はなく、(d)実装タスクに内包されている(既存分類ロジックの限界、
本測定でも追加分離は行っていない)。

### 4-2. 新規実測2件の詳細breakdown(非0バイト転記が現存した直近委任)

| 項目 | Fact Safety Relaxation Trial-01 Stage2-Stage3 | OPEN-141 Diff QA Trial-01(初回) |
|---|---|---|
| 委任文字数 | 3,018 | 2,593 |
| `subagent_tokens`(報告値) | 295,922 | 147,133 |
| 実測: 最終(最大)1ターンusage合計 | 295,183(99.97%一致) | 146,927(99.86%一致) |
| 実測: 全ターン累積usage合計 | **49,466,043**(input 566/output 62,419/cache_read 48,160,772/cache_creation 1,242,286) | **6,620,586**(input 156/output 18,148/cache_read 6,323,020/cache_creation 279,262) |
| 累積/`subagent_tokens`倍率 | **167.2倍** | **45.0倍** |
| Read/Grep/Bash結果文字数合計 | 235,625 | 170,474 |
| 最大カテゴリ | production_code_er0x_py 98,098字(41.6%) | production_code_er0x_py 53,225字(31.2%) |
| Read全文読込率(offset/limit不使用) | 47.4%(18/38) | 50.0%(4/8) |
| git Bash出力文字数 | 782(0.3%) | 0(0.0%) |
| 同一ファイル再読(reread) | 71,880字(30.5%) | 36,243字(21.3%) |
| tool_uses(報告値) | 151 | 42 |

### 4-3. 発見: `subagent_tokens`は累積処理量ではなく最終ターンのcontext到達サイズ

上表の通り、`<task-notification>`の`subagent_tokens`は実測2件とも「そのタスクの
**最後(最大)の1回のAPI呼び出しにおけるusage合計**(input+output+cache_read+
cache_creation)」とほぼ完全一致した(誤差0.03〜0.14%)。これは、Claudeの
prompt caching構造上、各ターンでcontextが累積的に大きくなり、直前までの内容は
`cache_read_input_tokens`として毎ターン再計上される(実際に安く処理されるが
「処理された」こと自体はターンごとに発生する)ため、**全ターンのusageを単純合計
すると同じcontextを何十回・何百回も重複カウントすることになり、`subagent_tokens`
はこの重複合計ではなく最終到達サイズ1点のみを報告している**と考えられる。

この結果、既存の全報告(本REPORT含む2〜3節、`SUBAGENT-TOKEN-CONSUMPTION-BY-
TASK-TYPE-01`の254件36,590,141token等)はすべて`subagent_tokens`基準であり、
**「タスクが到達したcontextサイズの合計」を表すのであって、「実際にAPIが処理した
延べtoken数(課金・Claude Max消費に近い指標)」ではない**可能性が高い。実測2件の
倍率(167.2倍・45.0倍、平均127倍程度)がもし他タスクにも広く当てはまるなら、
実際の延べ処理量は既存報告の記載値より1〜2桁大きい可能性がある。**これは本測定で
初めて確認した事実であり、N=2のみのため一般化はできない(要追加検証、判定語なし)**。

### 4-4. F-1(即時退避)遵守状況

| 対象 | 非0バイト件数/総数 | 比率 |
|---|---|---|
| `docs/pm/transcripts/`(F-1退避先) | 1/3 | 33% |
| 現行セッションtempディレクトリ全体(290ファイル) | 189/290 | 65.2% |
| 直近10委任のみ | 2/10 | 20% |

直近10委任に限ると非0バイト率はセッション全体平均(65.2%)より大幅に低い
(20%)。セッション全体の高い比率は「まだOSに削除されていない古いファイルが
多く残っている」ことによる可能性があり(経過日数と削除の関係は本タスクの
読み取り範囲では特定不可)、直近分だけを見るとF-1(委任完了直後の確実な退避)は
**徹底されていない**(`docs/pm/transcripts/`が3ファイルしか増えていない点からも
裏付けられる)。

### 4-5. haiku-worker実績

現行セッション全体で`"haiku-worker"`という文字列を含む行は1件のみ(既存報告と
同水準、新規増加なし)。

---

## 5. 評価(判定材料の提示、判定はFableが確定)

### 5-1. Fable→Sonnet削減施策の判定材料

| 施策 | 判定材料 | 暫定案(判定語ではない) |
|---|---|---|
| E-1(reread抑制) | Before 27.8%(N=18)→After合算31.0%(N=4)。改善を示す実測なし。サンプル数・タスク種別偏りともに不足 | 評価不足。N=18/N=4はいずれも統計的代表性が低く、追加検証(できれば同一管理ID・同一種別でのペア比較)が必要 |
| D-1(該当範囲限定read) | Before相当の全文読込率の直接比較値は既存報告になし。本測定で新規実測(47.4%・50.0%)を得たのみ | 評価不足(Beforeとの比較不能、今後はこの47〜50%を新baselineとして追跡可能) |
| G-1(git出力最小化) | Before(実測3件1.8〜6.8%)→After(実測2件0.3%・0.0%) | 効果ありそうだが、そもそも寄与率が小さい施策のため全体への影響は誤差範囲 |
| F-1(即時退避) | `docs/pm/transcripts/`3件中非0バイト1件、直近10件中非0バイト2件 | 効果不十分。運用が徹底されていない可能性が高い(手順の再確認が必要) |
| A-1(Consolidation統合) | 不採用のまま(リスク中〜高と判定済み) | 現状維持が妥当(既存判定を覆す新規材料なし) |

### 5-2. Sonnet総消費の主要浪費源Top3(数値根拠付き)

1. **累積context再処理(cache_read)によるターンごとの重複計上**: 実測2件で
   累積usage(49.47M・6.62M token)の97%以上がcache_read_input_tokensで占められる
   (48,160,772/49,466,043=97.4%、6,323,020/6,620,586=95.5%)。1タスク内で
   ターン数が多いほど、同じcontextが繰り返し再計上される。tool_uses数(151回・
   42回)とほぼ比例しており、**tool_uses削減(=1タスク内の往復回数削減)が
   最大のレバー**と考えられる。
2. **Production配線タスクの対象コード読込量**(既存`SUBAGENT-TOKEN-CONSUMPTION-
   BY-TASK-TYPE-01`実測3件で32〜63%、本測定2件でも31.2%・41.6%と一貫して
   最大カテゴリ)。D-1が対象とする領域だが、実測全文読込率は依然47〜50%と
   高く、D-1の徹底余地が残る。
3. **同一task内の同一ファイル再読(reread)**: Before 27.8%〜After 31.0%で
   高止まり。E-1導入後も改善の実測なし。

### 5-3. 現状のまま1週間開発した場合のClaude Max使用量寄与見込み(外挿、算定根拠明記)

**方法A(`subagent_tokens`基準、既存報告と同一定義、比較可能性重視)**:
- 2026-09-10単日実測(`PM-TOKEN-EFFICIENCY-DIAGNOSIS-01_REPORT.md`13行目):
  15委任・約2.32M token/日 → 週次16.2M token(この基準は最も古い低負荷の日)。
- 2026-09-07〜09-12(6日間)実測(`SUBAGENT-TOKEN-CONSUMPTION-BY-TASK-TYPE-01`):
  254委任・36,590,141token/6日 ≈ 6.10M token/日 → 週次42.7M token(この基準は
  Production配線・Trial系の負荷が高かった期間)。
- **方法Aでの見込みレンジ: 週次16.2M〜42.7M token**(`subagent_tokens`基準)。
  日によって3〜4倍の変動があり、直近(2026-09-12〜13)の10件平均
  (205,695token/件)は上記期間平均(144,056/件)よりやや高いため、**直近の
  ペースが続く場合は週次見込みのレンジ上限(42.7M)に近づく可能性が高い**。

**方法B(4-3の新発見を反映した場合、不確実性大・未検証)**:
- 4-3の実測2件の倍率(167.2倍・45.0倍、単純平均106倍)を方法Aの`subagent_tokens`
  週次見込みに掛け合わせると、**実際の延べ処理量は週次17億〜45億token程度に
  達する可能性がある**(16.2M×106〜42.7M×106)。
- **この方法Bの数値は、N=2のみから得た倍率を全体へ機械的に外挿した参考値であり、
  精度は低い(誤差桁レベルで大きい可能性がある)。Claude Maxの実際の利用上限
  計算式(cache_read等の重み付け方法)はAnthropic非公開のため、方法Bが実際の
  Max消費と比例するかどうかも未確認**。あくまで「既存報告の数値が実際の処理量を
  大幅に過小評価している可能性がある」という警鐘として提示する(判定語なし、
  追加検証が必要な項目として4節に整理済み)。

### 5-4. 品質を落とさず削減余地が大きい箇所(改善案のみ、STOP・未実装)

| # | 箇所 | 効果見込み | リスク | 実装コスト |
|---|---|---|---|---|
| 1 | D-1の徹底(全文Read47〜50%を実測ベースでさらに引き下げ、Grep→該当行範囲Readを委任文で明示的に強制) | (d)系タスクの最大カテゴリ(31〜63%)の削減余地、tool_uses削減にも波及 | 中(依存関係見落としリスク、既存報告と同一評価) | 低(委任文の書き方のみ) |
| 2 | F-1運用の手順見直し(現状20%しか非0バイトで残らない原因の特定。完了通知受信タイミングとファイル書き込みタイミングの競合を疑う) | 直接の削減効果はないが、今後の同種測定・原因分析の精度が上がる(可観測性向上) | 低 | 低〜中(原因調査が必要、本タスクの範囲外) |
| 3 | tool_uses削減(1タスク内の往復回数そのものを減らす、例: 複数の小さいRead/Grepをまとめて1回のBash/Grepで済ませる) | 5-2の通りcache_read再計上がturn数にほぼ比例するため、turn数を減らせれば累積処理量への効果は大きい可能性 | 中(1回あたりの情報量が増えると読み違い・見落としリスクが上がる) | 中(委任文・Sonnet自身の作業スタイル変更が必要) |

### 5-5. これ以上削ると品質・PM Gateに悪影響が出る箇所

- Fact Safety系Trial(Verification段階を含む2段階検証)の検索・読込量削減は
  `PM-TOKEN-EFFICIENCY-T2-T3-ASSESSMENT-01_REPORT.md`のT-3節で既に
  「Fact Safety直結のQA相当パラメータでありSTOP必須条件に該当しうる」と
  結論済み(本タスクでは再検証していない、既存結論を踏襲)。
- D-1の「該当関数/行範囲のみRead」は、配線タスクで依存関係の見落としリスクと
  常にトレードオフであり、実装コード全体の構造変更を伴うタスクでは全文読込が
  必要な場合がある(既存報告と同一評価、本測定でも覆す材料なし)。

---

## 6. 制約・限界(正直な記載、再掲含む)

- 非0バイト転記が直近10委任中2件(20%)のみであり、4節の詳細breakdownは
  この2件に限定される。代表性は低い。
- 4-3の「`subagent_tokens`=最終ターンusage」という発見はN=2の実測にとどまり、
  全254件・全期間への一般化は未検証(倍率106倍という数字も1桁の精度しかない)。
- 5-3方法Bは方法Aの外挿にさらに倍率を掛けた二重外挿であり、精度はきわめて低い。
  Claude Maxの正式な計算式が非公開である以上、これ以上の精緻化は本タスクの
  範囲(read-only現状把握)では不可能。
- E-1/D-1/G-1のラベル出現有無は文字列検索に基づく機械判定であり、言い回しの
  網羅性は手動確認の範囲に限られる。
- 2節の「委任文の食い違う数値」整理は、両報告の記載内容の突合であり、いずれの
  報告の生データも本タスクでは再実行していない(引用のみ)。

---

## 付録: 生成物一覧

- 本REPORT: `PM-TOKEN-EFFICIENCY-STATUS-MEASUREMENT-02_REPORT.md`(root新規)
- 一時解析スクリプト・中間データ(repo外scratchpad、Git管理外、いずれも
  `er011_pm_agent_read_audit_01.py`をimportするのみで本体無変更):
  `status02_extract_recent.py`、`status02_parse_two.py`、
  `status02_usage_breakdown.py`、`status02_last_usages.py`、
  `status02_verify2.py`、`status02_sum2.py`、`status02_dup_lines.py`、
  中間データ`status02_last10.jsonl`、`status02_last10_prompts.jsonl`、
  `status02_nonzero_list.txt`(いずれも
  `C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\
  294958fe-da6e-491c-8a02-4f864d8195c8\scratchpad\`配下)。
- 既存参照REPORT(無変更、引用のみ): `PM-TOKEN-EFFICIENCY-DIAGNOSIS-01_REPORT.md`、
  `PM-TOKEN-EFFICIENCY-AGENT-READ-DUPLICATION-AUDIT-01_REPORT.md`、
  `PM-TOKEN-EFFICIENCY-DELEGATION-PROMPT-BOILERPLATE-MEASUREMENT-01_REPORT.md`、
  `PM-TOKEN-EFFICIENCY-SUBAGENT-TOKEN-CONSUMPTION-BY-TASK-TYPE-01_REPORT.md`、
  `PM-TOKEN-EFFICIENCY-DELEGATION-TRIAL-AFTER-MEASUREMENT-01_REPORT.md`、
  `PM-TOKEN-EFFICIENCY-T2-T3-ASSESSMENT-01_REPORT.md`。

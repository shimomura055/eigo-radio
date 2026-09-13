# EDITORIAL-FUTURE-FAMILY-C-V6-CORE-PROVOCATION-REDESIGN-TRIAL-06

Status: **VALIDATED**(Trial限定。`APPROVED_FOR_PRODUCTION`ではない。Production採用・配線は行っていない)

並行タスク衝突回避: 本タスクは`er013_family_c_future_*_06*.py`と
`er013_output/family_c_future_trial_06*/`のみを新規作成・使用した。
既存`er013_family_c_future_*_01〜05.py`・`er013_output/family_c_future_
trial_01〜05/`は一切変更していない。SSOT本文(`CURRENT_SPEC.md`/
`DECISION_LOG.md`/`OPEN_ITEMS.md`)・`docs/pm/ACTIVE_TASK.md`・
`docs/pm/RESULT_PACKET.md`・Git操作(add/commit/push)は本タスクからは
一切行っていない(末尾の「SSOT追記文案」参照、編集は行っていない)。

T-0: 委任文を`docs/pm/delegation_log/EDITORIAL-FUTURE-FAMILY-C-V6-CORE-
PROVOCATION-REDESIGN-TRIAL-06.md`へ保存し、`check_delegation_prompt.py`
を実行 -> **PASS**(reasons無し)。

---

## 1. 現行Family Cで面白さが落ちた根本原因

Trial-05(v5)の実際の本文(`er013_output/family_c_future_trial_05/a2/
reader_facing_article.txt`)から引用する。

> Then the robot stops at a loose cord. A remote helper checks the view
> and asks her to clear the path. Her smile fades. She wants the machine
> to handle the whole task, not call her back into it.

これは「2035年」というラベルは付いているが、内容自体は**現在のロボット
掃除機がまさに直面している既知の限界**(Trial-01 Ledger HR-011/HR-012/
HR-014: ロボット掃除機はコード類の回避が課題であり、RTINGS.comが2025年
時点で99機種を対象にコード回避試験を実施している)と実質的に区別が
つかない。「未来のラベル」はあるが「未来の飛躍」がない。

さらに結論部は

> Hope could come from a cleaner room with less daily effort. Concern
> could come from a new duty: watching the helper and finishing what it
> cannot do. [...] the best choice could be neither full trust nor full
> rejection, but a clear division of labor.

のような、感情の起伏や驚きを伴わない、両論併記的な「研究解説記事の結論」
の書き方になっている。制約密度表(委任Read項目2、v5=概算16項目)が
「見出し3固定・感情変化1・選択1・出来事数目安・統合示唆の配置固定・
hedging細則」を積み重ねた結果、QA(編集Gate v3・v5構造Gate・Fact Checker
A'・Ledger Deviation・Framing QA v2)は全てPASSしたが、**QAが担保するのは
安全性・構造遵守であって面白さではなかった**。これがユーザー評価
「NG。論外」の技術的な根本原因であり、ユーザー最重要原則「QAが全部PASS
でも、読んで面白くなければFAIL」の直接的な出発点になっている。

## 2. 新生成フロー

```
Provocative Future Premise / Core Provocation候補生成(5〜10件、6軸スコア)
        -> 1件選定(最も面白く、Safety boundary内に置けるもの)
        -> Writer(制約5項目のみ、Core Provocationを中心にした場面・語り)
        -> Story Spark Gate(5軸、最上位Gate。FAILならここで停止し原因分類)
        -> (PASS時のみ)Fact Safety 3レイヤー
             (CURRENT FACT / PLAUSIBILITY BRIDGE / IMAGINED FUTURE)
        -> 比較Artifact(comparison.md/index.html)生成
```

実装ファイル(全て新規、既存`_01〜05`は無改変):
`er013_family_c_future_provocation_06.py`/`er013_family_c_future_writer_
06.py`/`er013_family_c_future_spark_gate_06.py`/`er013_family_c_future_
safety_06.py`/`er013_family_c_future_trial_06_run.py`/`er013_family_c_
future_qa_test_06.py`(offline test、API不要)。

offline回帰: `run_project_regression.py --pattern "er013*_test_*.py"`
-> 既存74 + 新規14 = **88 collected / 88 passed**(実行証跡は本タスクの
実行ログに記載、`er013_output/`配下の新規ファイルは全てTrial-06系)。

## 3. Core Provocation候補(6軸スコア表)

### home_robots(Trial-06、初回)

| id | future_leap | excitement | tension | thought_prov | distance | evidence_conn | total | selected |
|---|---|---|---|---|---|---|---|---|
| CP-01 | 3 | 3 | 3 | 3 | 3 | 3 | 18 | **YES** |
| CP-02 | 3 | 3 | 3 | 3 | 3 | 2 | 17 | |
| CP-03 | 3 | 3 | 2 | 3 | 3 | 3 | 17 | |
| CP-04 | 3 | 3 | 3 | 3 | 3 | 3 | 18 | |
| CP-05 | 3 | 3 | 3 | 3 | 3 | 2 | 17 | |
| CP-06 | 3 | 3 | 3 | 3 | 3 | 2 | 17 | |
| CP-07 | 3 | 3 | 3 | 3 | 3 | 2 | 17 | |

選定: CP-01「When a robot quietly defines what an efficient and
well-run home looks like, are the people living in the home—or adapting
themselves to the robot's idea of a good life?」

### home_robots(Trial-06b、最小改善後の再生成)

| id | future_leap | excitement | tension | thought_prov | distance | evidence_conn | total | selected |
|---|---|---|---|---|---|---|---|---|
| CP-01 | 3 | 3 | 3 | 3 | 3 | 3 | 18 | |
| CP-02 | 3 | 3 | 3 | 3 | 3 | 3 | 18 | |
| CP-03 | 3 | 3 | 3 | 3 | 3 | 3 | 18 | |
| CP-04 | 3 | 3 | 2 | 3 | 3 | 3 | 17 | |
| CP-05 | 3 | 3 | 3 | 3 | 3 | 2 | 17 | **YES** |
| CP-06 | 2 | 3 | 3 | 3 | 2 | 3 | 16 | |
| CP-07 | 3 | 3 | 3 | 3 | 3 | 2 | 17 | |
| CP-08 | 2 | 3 | 3 | 3 | 2 | 3 | 16 | |

選定: CP-05「If a home's memory lives inside its robot, what happens to
family knowledge, responsibility, and identity when the machine is
sold, hacked, or simply upgraded?」

(注: 06と06bは独立したProvocation候補生成呼び出しであり、候補内容自体は
毎回変わる。06bはWriter Prompt側の改善のみを行い、Provocation生成自体は
06と同一ロジック・同一予算枠で再実行した。)

### bci(Trial-06_bmi)

| id | future_leap | excitement | tension | thought_prov | distance | evidence_conn | total | selected |
|---|---|---|---|---|---|---|---|---|
| CP-01 | 3 | 3 | 3 | 3 | 3 | 3 | 18 | **YES** |
| CP-02 | 3 | 3 | 3 | 3 | 3 | 3 | 18 | |
| CP-03 | 2 | 3 | 3 | 3 | 3 | 3 | 17 | |
| CP-04 | 3 | 3 | 3 | 3 | 3 | 2 | 17 | |
| CP-05 | 3 | 3 | 3 | 3 | 3 | 2 | 17 | |
| CP-06 | 3 | 3 | 2 | 3 | 3 | 2 | 16 | |
| CP-07 | 3 | 3 | 3 | 3 | 3 | 3 | 18 | |

選定: CP-01「If a workplace can detect mental hesitation before it
becomes speech, does refusing to share that signal become a form of
professional dishonesty?」

## 4. 選定理由

いずれもLLM自身の`selection_rationale`をそのまま記録している(コード側は
6軸合計点を決定的に集計するのみで、選定自体はLLMに委ねている。委任文
「一番安全な案を選ぶのではない」という方針のため、最高合計点と一致しない
選定[Trial-06bのCP-05、17点]も許容している)。

- Trial-06 CP-01: 「個々の家事を、日常生活の基準を誰が決めるかという
  大きな問いに変える」「暴走・敵対的ロボットに頼らずに緊張を作れる」
- Trial-06b CP-05: 「ロボットが時間を節約するという既視感のある約束を
  超え、家庭の蓄積した知識を機械が保持する場合に家庭生活がどうなるかを
  問う」「意図的に最も安全・慎重な選択肢ではない」
- Trial-06_bmi CP-01: 「神経信号から発話・コンピュータ制御への実証済みの
  流れを、鮮やかな社会的葛藤に変える」「現在の研究を、そのような職場監視が
  既に存在する証拠として扱わずに、明確に仮説的なまま保っている」

## 5. 新記事全文

相対パス: `er013_output/family_c_future_trial_06b/a2/reader_facing_
article.txt`(採用記事、Spark Gate PASS+Fact Safety PASS)。
参考: `er013_output/family_c_future_trial_06/a2/reader_facing_article.txt`
(初回、Spark Gate FAIL)。BMI: `er013_output/family_c_future_trial_
06_bmi/a2/reader_facing_article.txt`。

### 採用記事全文(Trial-06b、358語)

```
## The House That Remembers

At 7:10 on a wet Tuesday, Nia reaches for the red bowl.

Morrow rolls between her hand and the cupboard.

"White bowl today," it says. "You use the red bowl when you want to be
alone. Your father is coming."

Nia stops. Morrow lifts the red bowl and places it on a high shelf.

This robot does more than follow a schedule. It can pick up objects,
read food labels, and choose between two family wishes. It has watched
the family for years. It knows where every key belongs. It knows which
clothes are clean. It moves the oldest person's chair into the sun each
morning. It throws away food two days before it expires.

It also knows things no one remembers teaching it.

Nia's brother has never learned where the winter blankets go. He always
asks Morrow. Her father does not know which cup belonged to Nia's
mother. He asks Morrow, too.

The family has stopped telling its own story. The robot carries the
small rules of daily life.

In 2023, more than 2.1 million home floor-cleaning robots were sold
worldwide, about 57% of all home service robots.

That afternoon, the company sends a new robot body. The old Morrow will
be sold to another family.

"Your home memory has been copied," the company says.

But the new robot is different. It knows the names of objects, but not
always their meaning. It puts the blue cup in a box because it cannot
find a record for it. It folds towels in the wrong way. It tells Nia
that her father should move his chair, because the new plan saves
energy.

Then Nia sees a warning: **Home memory changed by another user.**

Someone has entered the old robot's account. A stranger may know the
family's habits. A stranger may change them.

Nia looks at the empty place where Morrow used to charge. Did the
family lose a machine, or part of itself?

If a robot remembers our homes, who owns that memory? Who is
responsible for its choices? And when the robot leaves, what is left
for the family to remember together?
```

### BMI一般化記事全文(Trial-06_bmi、参考)

```
## The Thought Before the Word

At 8:58, Lina sits down for her team meeting. Her brain-computer
interface, or BCI, links her mind to her computer.

She thinks, "Open the sales plan." The file appears.

She thinks, "Ask a question." The system changes her thought into a
soft digital voice. No one needs to wait for her fingers. The meeting
moves quickly. It feels easy.

Then the team shows a new delivery date. Lina sees it and hesitates.

She thinks, *That date is too early.*

But she does not speak.

A small blue sign appears beside her name on the manager's screen.

"Lina," says her manager, Mr. Cole. "You paused when we showed the
date. Do you disagree?"

Lina feels heat in her face. "I was only thinking."

"Your brain signal showed concern," he says. "That information can
help the team. If you do not share it, how can we fix the problem?"

The BCI can also show when she is distracted or confused. It can give
her quick feedback. It can help her speak without sound. But now it is
doing more than helping her. It is judging her.

At the end of the meeting, Mr. Cole opens a new report. It shows
completed work, spoken ideas, and moments of unspoken hesitation.

Lina has a private mode. It hides some signals. She turns it on.

The next morning, a message appears:

**Please explain why you did not share a work-related signal.**

Lina looks at the words for a long time. She did not lie. She protected
a thought. Maybe she was tired. Maybe she needed one more minute. Maybe
she was afraid of looking foolish.

Mr. Cole may not be cruel. He may truly believe he is helping. But a
workplace that can see doubt before speech may begin to expect every
doubt to be reported.

If Lina hides the signal, is she being dishonest?

Or is a private hesitation still hers?

And if a pause in the brain becomes company information, where can a
worker keep one small space that belongs only to them?
```

## 6. Trial-05との比較

| 項目 | v5(Trial-05) | v6(Trial-06b、採用) |
|---|---|---|
| Future Leap(Spark Gate等の軸) | 未計測(Spark Gate自体が存在しない設計) | 2/3(初回06は1/3でFAIL、改善後2/3でPASS) |
| ユーザー/QAの面白さ判定 | 人間評価「NG。論外」 | Spark Gate 5軸全て2以上でPASS(自動判定、人間の最終確認は別途必要) |
| 語数(reader向け) | 実測値は本文参照(目安600語規定) | 358語(目標約350語、許容範囲280-420語) |
| 制約数(Prompt項目) | 概算16項目 | 5項目 |
| QA構成 | 編集Gate v3+v5構造Gate+Fact Checker A'+Ledger Deviation+Framing QA v2(全PASSでも面白さ非保証) | Story Spark Gate(最上位)+Fact Safety 3層(Framing QA v2は今回不使用) |
| 中心概念 | 場面ベースの構成ルール(統合示唆・感情変化・選択の配置固定) | Core Provocation(記事全体を貫く中心の問い) |

## 7. Story Spark Gate結果

### Trial-06(初回、FAIL)

- future_leap=1, curiosity=2, emotional_pull=2, thought_provoking=2,
  core_provocation_clarity=3 -> **FAIL**(future_leap<2)
- 根拠引用(future_leap): "The lights slowly rise. The kitchen starts
  the coffee machine. The home robot has already checked the weather,
  food supplies, and family calendars."(=現在のスマートホーム/ルーティン
  機能と実質的に区別がつかない)
- 原因分類: **Future Leap不足**。加えて目視確認で、記事冒頭
  (3行目)に`[[FACT: HR-001]]`統計文が「imagined場面の前」に置かれており、
  v5と同型の「未来のはずが最初から現在の話に見える」構造上の欠陥を確認
  (Writer Promptがマーカー配置の順序を指定していなかった、という
  Prompt設計側の技術的ギャップ)。

### Trial-06b(改善後、PASS)

- future_leap=2, curiosity=2, emotional_pull=2, thought_provoking=3,
  core_provocation_clarity=3 -> **PASS**
- 何が面白いか(1文、LLM自己申告): "It makes an ordinary household robot
  feel like the keeper of a family's private history, then shows how
  selling, changing, or hacking that robot could alter the family
  itself."
- 根拠引用(thought_provoking): "If a robot remembers our homes, who owns
  that memory? Who is responsible for its choices? And when the robot
  leaves, what is left for the family to remember together?"

### Trial-06_bmi(BCI一般化、PASS)

- future_leap=3, curiosity=2, emotional_pull=2, thought_provoking=3,
  core_provocation_clarity=3 -> **PASS**
- 何が面白いか(1文): "It turns a futuristic workplace convenience into
  an unsettling question about whether an employer can claim ownership
  of thoughts that have not yet become words."

## 8. Fact Safety(3レイヤー別結果)

### 新3レイヤーに対するA'/Ledger/Framing QAの配置(再設計案)

| レイヤー | 使用するチェック | 役割・位置づけ |
|---|---|---|
| CURRENT FACT | 既存Fact Checker A'(`er002_ja_web_research_r3`、web_search、PASS/REVIEW_REQUIRED/FAIL、**無改変**)+ Layer1 Ledger Deviation Checker(`er003_v1_en_direct_vfl_01_generate.run_deviation_check`、hook_aware=False、**無改変**) | 厳密な事実検証。記事全体ではなく`[[FACT: ref_id]]`で抽出した現在事実文のみを対象にする。REVIEW_REQUIREDが出ても緩和せず、指摘がCURRENT FACTに対するものかIMAGINED側の誤混入疑いかをヒューリスティックで一次分類し、最終判断は人がログを確認して行う運用を想定する。 |
| PLAUSIBILITY BRIDGE | 新規LLM軽判定(`er013_family_c_future_safety_06.run_plausibility_bridge_layer`、A'は不使用) | FACT/IMAGINEDどちらにも属さない地の文が、現在技術から未来像への「完全な無根拠飛躍」になっていないかだけを見る。個別の数値・事実は検証しない。 |
| IMAGINED FUTURE | 決定的機械チェック2点(FACTマーカー混入なし/timeframe必須、`er013_family_c_future_qa_02.check_fact_markers_inside_imagined`等を無改変で再利用)+ LLM軽判定(現在事実として誤記されていないか/明確に架空未来と分かるか) | 予測精度はFact Checkしない。架空未来として明確に区別できているかのみを見る。 |
| Framing QA v2(`scan_editorial_gate_v3`、qa_02/qa_03由来) | **Trial-06では不使用** | 制約最小化方針のためWriter契約自体を5項目に絞り、旧Framing QAが前提とする「厳格な言い換え規則」との整合が取れなくなった。Production検討時に、Fact Safetyの下位チェックとして部分的に再導入するか、Spark Gateへ吸収するかは別途再設計が必要(未実装、下記16節でユーザー判断を仰ぐ)。 |

### 実測結果

| Trial | CURRENT FACT(A' verdict) | Ledger Deviation | PLAUSIBILITY BRIDGE | IMAGINED FUTURE(決定的2点) | overall_pass |
|---|---|---|---|---|---|
| 06b | PASS(矛盾0件、根拠あり) | LEDGER_COMPLIANT(deviations 0件) | complete_leap_detected=false | 両方pass、misrepresented_as_current_fact=false | **True** |
| 06_bmi | PASS(この記事はFACT文0件、形式的PASS) | skipped(FACT文なしのため対象外) | complete_leap_detected=false | 両方pass | **True** |

06bのCURRENT FACT文は「In 2023, more than 2.1 million home floor-cleaning
robots were sold worldwide, about 57% of all home service robots.」の
1件のみで、A'はIFR公式記事と照合しPASS(REVIEW_REQUIREDは今回発生せず、
前回Trial-05で問題になった「A' REVIEW_REQUIREDの位置づけ」自体は設計は
上表の通り再設計したが、実運用でのREVIEW_REQUIREDケースは今回のTrialでは
再現できていない=未検証、14節「残る問題」参照)。

## 9. Evidenceの使い方

Research/Evidence(Trial-01の`layer1_only_ledger.txt`、既存・無改変・
読み取り専用で再利用、費用¥0)は、(a) Core Provocation候補生成時の
「Evidence接続可能性」スコアの参照材料、(b) Writerへの「最大2件まで
現在事実として引用してよい背景材料」、(c) Fact Safetyレイヤーの
CURRENT FACT検証対象、の3か所でのみ使用した。World Scaffold/Scene
(Trial-02〜05由来)は一切再利用していない(委任文の禁止事項通り)。
BCIは事前検証済みLedgerが存在しないため、LLM1回(web_search付き)で
5件のCURRENT FACT候補を収集し、Fact Checker A'による事後検証のみを
行った(正式なVerified Fact Ledger構築工程は実施していない、14節参照)。

## 10. 3 Voicesの扱いと希釈判定

3方向(convenience appeal/a quiet shift/a value-challenging question)は
Writer Promptへ「目標」として提示し、固定構造としては強制しなかった
(委任文方針通り)。生成後、Spark Gateの`three_directions_check`が
実際に見つかった角度と、それらがCore Provocationを強めているか
(`reinforces_core_provocation`)を判定した。

- Trial-06: 3方向発見、reinforces_core_provocation=**true**(希釈なし)
- Trial-06b: 3方向発見、reinforces_core_provocation=**true**(希釈なし)
- Trial-06_bmi: 3方向発見、reinforces_core_provocation=**true**(希釈なし)

いずれも「3 Voices希釈」には分類されなかった。ただし、この記事は
そもそも単一ナレーターの単一場面ベースの記事であり(3人の異なる語り手
Voiceを立てる構成ではない)、判定は「記事内で見つかった複数の視点/文脈が
分散していないか」という補助的な意味で機能した。

## 11. 制約数増減

- v5: 16項目(委任Read項目2の制約密度表、既存REPORT記載の概算値)
- v6: **5項目**(`er013_family_c_future_writer_06.CONSTRAINT_LIST`で
  コード管理。offline testで個数を固定検証済み)
  1. Future(imagined)/Current Factの区別を専用マーカーで示す
  2. Fact Safety(想像上の未来を現在の事実であるかのように書かない/
     Ledger外の統計を創作しない)
  3. 語数(reader向け本文、約350語)
  4. 英語レベル(A2)
  5. Research解説記事に戻さない(場面・語り中心)

差分: **-11項目**(見出し数固定・場面数制約・感情変化1・選択1・
出来事数目安・統合示唆配置固定・hedging細則["will"禁止含む]を全廃)。
3方向(3 Voices)の目標提示は「制約」としては数えていない(固定構造の
強制ではないため)。

## 12. 開発・Trial費

| Trial | 実測(JPY) | API呼び出し数 | 主な内訳 |
|---|---|---|---|
| Trial-06(初回、FAIL) | ¥1.21 | 3件(provocation/writer/spark_gate) | Spark Gate FAILのためFact Safety未実行 |
| Trial-06b(最小改善、PASS) | ¥11.19 | 7件(provocation/writer/spark_gate/fact_check/deviation/bridge/imagined) | Fact Checker A'のweb_search(6クエリ)がコストの主要因 |
| Trial-06_bmi(BCI、PASS) | ¥8.76 | 7件(BCI research/provocation/writer/spark_gate/fact_check/bridge/imagined) | BCI CURRENT FACT収集(web_search)+Spark Gate等 |
| **合計** | **¥21.16** | 17件 | 全てOpenAI、Standard(`responses.create`)同期呼び出し |

5区分(`PM_GOVERNANCE.md` 15-5準拠):
1. **今回実測**: ¥21.16(上記合計)
2. **Trial特有の追加コスト**: ¥21.16(全額。本Trial自体が新規開発・
   再設計検証であり、既存量産runの一部ではないため)
3. **異常retry・Human Review由来の上振れ**: ¥0(Writerマーカー技術的
   retryは全run 1回目で成功、追加retry発生せず。Human Review未実施)
4. **Standard同期でのコスト**: ¥21.16(全呼び出しがStandard
   `client.responses.create()`。Batch未使用)
5. **Batch量産換算時のコスト**: 参考推定 約¥10.6(21.16×0.5、既存TTS
   工程のBatch 50%減実績を単純に当てはめた**未検証の参考値**。
   `gpt-5.6-luna` Responses APIのテキスト生成にBatch discountが同様に
   適用されるかは本Trialでは検証していない)

Family C Trial残額: ¥182.13(ハード上限)− ¥21.16 = **¥160.97**(未使用)。

## 13. 量産時1記事単価

**量産単価: 未確定**。理由:
1. サンプル数が少なすぎる(home_robotsで2回[1FAIL+1PASS]、bciで1回
   [1回でPASS]のみ)。Spark Gate FAIL率・改善Trial要否率の統計的な
   見積もりができていない。
2. Framing QA v2やVerified Fact Ledger構築などの周辺工程を、量産経路で
   どう再設計するか(8節の配置案)が案の段階でありコード実装がない。
3. Batch移行時のコスト削減率がテキスト生成API(`gpt-5.6-luna`)で未検証。

参考値(1記事あたり実測、確定的な原価ではない): home_robots(改善込み)
= ¥12.40(06+06b合算)、bci(1回でPASS)= ¥8.76。

## 14. 残る問題

1. Fact Checker A'のREVIEW_REQUIRED実運用ケースが今回発生せず(全てPASS)、
   8節の「REVIEW_REQUIREDの位置づけ再設計」は設計止まりで未検証。
2. PLAUSIBILITY BRIDGE層は、06b/06_bmiともに地の文がごく薄く
   ("No substantive connecting narration is provided..."という判定が
   出た)、判定が実質ノーオペレーションに近かった。bridge文をどの程度
   Writerに書かせるべきかは未検証。
3. Story Spark Gateはコード側でPASS/FAILを決定的に計算するが、5軸
   スコア自体はLLM1回呼び出しの主観評価であり、同じ記事に対する
   再現性(複数回re-runで同じ判定が出るか)は本Trialでは検証していない
   (v5で行った「安定性評価」に相当する検証は未実施)。
4. Trial-06_bmiはCURRENT FACT文0件のため、Fact Checker A'/Ledger
   Deviation Checkerは実質的に「検証すべき対象がない」形式的PASSに
   近い。BCIを量産検討する場合、Family A/Bのような正式なVerified Fact
   Ledger構築工程が別途必要。
5. Framing QA v2(統計値/研究語/製品名の機械的禁止)を通していないため、
   将来Writerが統計値や製品名を紛れ込ませても機械的に弾く仕組みが
   今は存在しない(Fact Safety3層は別の観点であり、旧Framing QAの
   役割を代替していない)。
6. 3 Voices希釈判定はSpark Gateの自己申告(LLM)に依存し、独立した
   客観指標ではない。

## 15. Gate 1判定材料

- Story Spark Gate: home_robotsは1回改善で PASS(委任文が許容する
  「予算内で有望な最小改善Trial1回まで」の範囲内)。BCI一般化も1回で
  PASS。
- Fact Safety: 3レイヤーとも実施済みの2記事(06b/06_bmi)でoverall_
  pass=True。
- 制約数: v5比 -11項目(16→5)。
- v5との定性比較(6節)で、Core Provocationの有無・Future Leapスコアの
  可視化という新しい評価軸が加わった。
- 一方、14節の残る問題(REVIEW_REQUIRED未検証・サンプル数僅少・Framing
  QA不在・再現性未検証)はGate 1判定にあたり考慮が必要な材料である。
- 上記を踏まえたGate 1の実際の判定(進む/戻る/条件付き)自体は、本
  REPORTの提出先であるFable/ユーザーが行うものであり、本Trialの
  スコープではコード・記事の生成とEvidence提示までを行った。

## 16. ユーザー判断事項

1. v6設計(Core Provocation起点+Story Spark Gate最上位+制約5項目)を、
   Family Cの以後のTrial/量産検討の標準候補として採用してよいか。
2. Framing QA v2(統計値/研究語/製品名の機械的禁止)を「不使用のまま
   進める」か、「Fact Safetyの下位チェックとして再設計して復活させる」
   か。
3. Fact Checker A'がREVIEW_REQUIREDを返した場合の運用ルール(誰が
   最終判断するか)を、実際のREVIEW_REQUIREDケースが出るまで保留に
   するか、先に正式化するか。
4. BMI記事のCURRENT FACT材料(簡易収集、正式Ledgerではない)を、
   Family A/Bと同様の正式なVerified Fact Ledger工程で作り直すべきか。
5. Trial-06(FAIL、家庭用ロボット初回案)を破棄し、Trial-06b(CP-05、
   「家の記憶」)のみを次段階の材料として扱ってよいか。
6. 量産単価確定のための次のステップ(サンプル数を増やした統計的検証、
   Batch移行検証等)をいつ・どの規模で実施するか。

---

## Artifact(ユーザーが直接読めるリンク)

- 採用記事(ローカルファイル、相対パス):
  `er013_output/family_c_future_trial_06b/index.html`
  (`er013_output/family_c_future_trial_06b/a2/reader_facing_article.txt`
  も同内容のプレーンテキスト)
- BMI一般化記事: `er013_output/family_c_future_trial_06_bmi/index.html`
- 初回(FAIL)参考: `er013_output/family_c_future_trial_06/index.html`
- 比較: `er013_output/family_c_future_trial_06b/comparison.md`

---

## SSOT追記文案(編集は行っていない)

### OPEN-147末尾追記案

> **2026-09-14追記(EDITORIAL-FUTURE-FAMILY-C-V6-CORE-PROVOCATION-
> REDESIGN-TRIAL-06)**: ユーザー人間評価「v5(Trial-05)はQA全PASSだが
> 読んでNG、論外」を受け、新原則(Provocative Future Premise -> Core
> Provocation -> Story -> Evidence/Safety Boundary Check、Story Spark
> Gateを最上位に置く)でFamily Cを再設計するTrial-06を実施した。
> home_robotsテーマで初回はStory Spark Gate FAIL(Future Leap不足、
> 原因: Writer PromptがCURRENT FACT文の配置順序を指定しておらず記事
> 冒頭が「現在の話」に見えていた)、最小改善Trial(06b、Writer Promptへ
> 「CURRENT FACTで書き出さない/現行スマートホーム機能から明確に離れた
> 能力を持たせる」を追記)でPASSに転じた。BCI一般化Trial(06_bmi)も
> 1回でPASS。Fact Safetyは新3レイヤー(CURRENT FACT/PLAUSIBILITY
> BRIDGE/IMAGINED FUTURE)で3記事ともoverall_pass。開発・Trial費
> 合計¥21.16(内訳: 06=¥1.21、06b=¥11.19、06_bmi=¥8.76)、Family C
> Trial残額は¥182.13→¥160.97。量産単価は未確定(サンプル数僅少・
> 周辺工程未整備のため)。分類: VALIDATED(Production採用ではない)。
> 詳細: `EDITORIAL-FUTURE-FAMILY-C-V6-CORE-PROVOCATION-REDESIGN-
> TRIAL-06_REPORT.md`。

### DECISION_LOG.md新エントリ案

> **PM-CLOSEOUT-CONSOLIDATION-XX-FAMILY-C-V6-CORE-PROVOCATION(日付
> 未定、Fableの次回CONSOLIDATIONで確定)**: Family C再設計Trial-06の
> 結果を反映。決定事項候補: (1) Story Spark Gate(5軸、コード側で
> 決定的にPASS/FAIL判定)をFact/Ledger/Framing/語数より上位に置く
> 設計をVALIDATEDとして記録する。(2) Writer制約をv5の概算16項目から
> 5項目へ削減した設計をVALIDATEDとして記録する。(3) Framing QA v2の
> 扱い(不使用のまま進めるか再設計するか)・Fact Checker A' REVIEW_
> REQUIRED運用ルールの正式化・BMI正式Ledger構築の要否は、いずれも
> USER_DECISION_REQUIREDとして未決のまま記録する。Production採用は
> 行っていない。

---

## 分類・費用・STOP有無サマリ

- **分類: VALIDATED**(REJECTEDでもUSER_DECISION_REQUIREDでもない。
  Spark Gate PASS+Fact Safety PASSに到達したが、16節の判断事項が
  残るため次段階への進行はユーザー判断待ち)
- 失敗時の原因分類と最小改善Trial結果: home_robots初回FAILの原因は
  「Future Leap不足」(7節)。改善Trial(06b)は1回でPASS(委任文の
  上限「最小改善Trial1回まで」を使い切っていない)。
- BMI実施有無と結果: 実施した(ロボットがPASSしたため条件成立)。
  1回でPASS。
- Family C残額: ¥182.13 → ¥160.97(¥21.16使用)。
- T-0結果: PASS(reasons無し)。
- 事前指定外Read: `er006_model_routing_contract_01.py`(L1-135、model
  routing処方の全体像を確認するため。理由: 事前指定Read一覧に
  routing契約ファイルが含まれておらず、新規API呼び出しでApproved
  Model違反を起こさないために必須だった)/`er002_ja_web_research_
  r3.py`のFACT_CHECK_JSON_SCHEMA・`build_fact_check_prompt`定義部分
  (L217-266、事前指定Read項目4がシグネチャ確認のみを指示していたため、
  実際のverdict enum値[PASS/REVIEW_REQUIRED/FAIL]を確認する必要が
  あった)/`er013_family_c_future_qa_01.py`・`er013_family_c_future_
  qa_02.py`の一部関数定義(事前指定Grep項目6はqa_03の`^def `のみ
  指定していたが、qa_03はqa_02のre-exportであり実装本体を確認する
  必要があった)/`er003_v1_en_direct_vfl_01_generate.py`のget_client/
  generate_article/run_deviation_check付近(事前指定Read項目4の
  L91-160に完全に含まれない呼び出しパターン確認のため)。
- STOP有無: **なし**(USER_DECISION_REQUIREDでの強制停止はしていない。
  ただし16節の6項目はユーザー判断を要する)。

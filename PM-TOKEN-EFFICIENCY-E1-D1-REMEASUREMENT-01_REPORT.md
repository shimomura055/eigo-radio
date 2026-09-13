# PM-TOKEN-EFFICIENCY-E1-D1-REMEASUREMENT-01(read-only再測定、¥0)

性質: read-only(API呼び出しなし、実費¥0)。コード・SSOT・PM_GOVERNANCE・運用ルールの変更なし。Git操作なし(本タスクでは一切のcommit/pushを行っていない)。判定語(VALIDATED等)は付けない。材料と暫定案の提示まで。

## 要点(12行)

1. **母集団が劇的に拡張できた**: 復元済みtranscript(`subagents/agent-<taskId>.jsonl`、Claude Code CLI標準の逐次追記ログ)を全セッション横断で使うことで、sonnet-worker委任の**Before(境界前)357件・After(境界後)33件、いずれも100%(357/357・33/33)でtranscriptを取得・解析できた**(従来レポートの7.1%=18/254から大幅改善)。opus-consultantはBefore13件・After1件。
2. **境界時刻**: `commit 710241006b78164527606dad3615390fd26745b1`(`PM-CLOSEOUT-CONSOLIDATION-95`、DECISION_LOGへ「E-1/D-1/G-1採用/A-1不採用」を記録したcommit)= **2026-09-12 20:37:12 +09:00(11:37:12 UTC)**。この時刻以降にFableが発行したAgent委任(タイムスタンプ基準)を「After」とした。
3. **重要な発見(運用実態)**: After 33件のうち、委任文に`E-1`/`D-1`/`G-1`の明記または類似の言い回し(「再読しない」「該当箇所のみ」「--short」等)が**含まれていたのは18件(55%)のみ、15件(45%)は無記載**だった。PM_GOVERNANCE 11節「以下3件をSonnet/Opus委任文に付す」は**全委任へ徹底されていない**。この不徹底が、以下のBefore/After比較を弱めている可能性が高い。
4. **E-1(同一ファイル再読抑制)**: 全体のsame-file reread率(文字ベース)は **Before中央値33.9%→After中央値40.8%(改善なし、むしろ悪化)**。委任文に明記があった18件中でも中央値40.0%でBeforeとほぼ同水準。**E-1は現時点で効果が確認できない**。
5. **D-1(全文Read抑制)**: 全文Read率(文字ベース)は**Before中央値59.9%→After中央値47.9%(相対▲20%、改善方向)**。委任文に明記があった15件では42.3%〜49.4%相当でBeforeより低い。Read1回あたりの平均文字数もBefore6,382字→After4,022字(▲37%)、tool呼び出し1回あたりの平均文字数もBefore2,463字→After1,962字(▲20%)。**D-1は方向としては改善が観測されるが、N=33(明記ありは18件)と小さく、タスク種別構成の違いに交絡されている**。
6. **G-1(git出力抑制)**: git系Bash出力比率はBefore中央値4.4%→After中央値8.9%と**悪化方向**(構成比の交絡が大きい、元々主因ではないため実務影響は小さい)。
7. **Sonnet内部消費(全体、種別非統一)**: 累積usage(全ターンinput+output+cache_read+cache_creation合計)はBefore中央値429万→After中央値532万(**+24%、悪化**)。ただしtool_uses(tool呼び出し回数)もBefore中央値50→After中央値68(**+36%**)であり、tool_usesとcumulative_usageの相関は**+0.93(強い正相関)**。**消費増加はタスクの複雑化(呼び出し回数増)に起因する可能性が高く、E-1/D-1/G-1導入自体が消費を増やしたとは言えない**。
8. **委任文へのE-1/D-1/G-1明記の有無で層別すると方向性が変わる**: 明記あり15件はcumulative_usage中央値271万(Beforeの430万より低い)、明記なし18件は中央値1,032万(Beforeより高い)。ただし**タスク種別構成が大きく異なる**(明記あり群は(a)Consolidation・(f)計測が多く、明記なし群は(b)Trial/Production-runや大型(a)/(d)が多い)ため、**明記の効果か種別の効果か本測定だけでは分離できない**。同一種別内(type a・type d)に限定した比較では明記あり群のほうがcumulative_usage中央値・全文Read率とも低い傾向は見えるが、セル件数が2〜7件と極小。
9. **交絡の整理**: (i) After期間はわずか約18時間(09-12 20:39〜09-13 05:24)、Beforeは約7日間(09-05〜09-12)と**観測期間が非対称**、(ii) タスク種別構成比がBefore/Afterで異なる((a)Consolidation比率25.8%→39.4%、(b)Trial比率29.4%→18.2%)、(iii) モデルはBefore/Afterとも`claude-sonnet-5`で統一(モデル変更の交絡はなし)、(iv) tool_uses分布自体がAfterで上振れ(中央値50→68)。**現状のNとこれらの交絡下では、E-1/D-1/G-1の効果「あり」「なし」を確定的に判定できるだけの検出力はない**(判定はFable/ユーザー判断)。
10. **施策1(tool_uses削減)の前提数値**: tool_uses(tool_call_count)とcumulative_usageの相関係数は**+0.93**(n=390、単回帰: usage≈194,871×tool_uses−4,085,599)。この線形近似を素朴に適用すると、tool_usesを平均から20%削減できればタスク平均で**約30%のusage削減が示唆される**(ただし外挿であり、切片が大きな負値になる=低tool_uses域で線形性が崩れる可能性が高く、保証値ではない)。
11. **施策2(D-1徹底)の前提数値**: 現状の全文Read率(全期間合算、文字ベース)は**57.2%**(Read結果文字数3,029万字中1,732万字が全文Read)。これを25%まで下げられた場合、Read結果文字数は約1,299万字(▲42.9%)減少する試算になり、これはtool_result総文字数(全期間合算5,749万字)の**約22.6%**に相当する。ただし全文Read率とcumulative_usageの相関は**−0.047(ほぼ無相関)**であり、**Read文字量の削減が実際のtoken消費削減に直結する保証はない**(キャッシュ由来のcache_read/cache_creationが消費の大半を占めるため、Read量だけでは説明力が低い)。
12. 本測定はSonnet往復1回・¥0で完結。次工程(施策1/2のTrial設計)は本REPORTの数値を前提にFable/ユーザーが判断する。

## 1. 方法・データ源

- **データ源**: 各セッションディレクトリ配下の`subagents/agent-<taskId>.jsonl`(Claude Code CLI標準の逐次追記ログ、`PM-TOKEN-EFFICIENCY-F1-ZERO-BYTE-TRANSCRIPT-ROOT-CAUSE-01`で確認済みの原本)を、`C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\`配下の**全16セッションディレクトリ**(合計432ファイル、377MB)から収集。委任文・委任時刻は同ディレクトリ配下の**全22個の主セッションjsonl**(`*.jsonl`、`294958fe...`等)から`Agent`/`Task`のtool_use呼び出し(`id`・`input.prompt`・`timestamp`・`input.subagent_type`)を抽出し、`agent-<taskId>.meta.json`の`toolUseId`で突合した。
- **突合結果**: sonnet-worker全390件(Before357+After33)全件で委任元プロンプト・時刻を100%突合できた(joined_to_call=433/433、対象外のExplore/general-purpose/claude-code-guide等の内蔵Agentタイプを除く)。
- **管理ID抽出・タスク種別分類**: `er011_pm_agent_read_audit_01.py`の`MGMT_ID_RE`/`extract_mgmt_id`/`classify_path`/`bash_command_read_targets`/`tool_result_text_len`を**無変更でimport利用**し、`PM-TOKEN-EFFICIENCY-SUBAGENT-TOKEN-CONSUMPTION-BY-TASK-TYPE-01`と同一優先順位の正規表現分類((a)Consolidation〜(g)その他)を踏襲した。
- **E-1(same-file reread率)の定義**: 同一task内でRead/Grep/Bash(cat系)が同一ファイルパスに2回目以降アクセスした際の結果文字数の合計 ÷ 総読込文字数。既存定義(`SUBAGENT-TOKEN-CONSUMPTION-BY-TASK-TYPE-01`)を踏襲。
- **D-1(全文Read率)の定義**: `Read`ツールで`offset`/`limit`をいずれも指定しなかった呼び出しの結果文字数(または回数) ÷ Read結果文字数(または回数)合計。既存定義(`PM-TOKEN-EFFICIENCY-STATUS-MEASUREMENT-02`)を踏襲。
- **累積usage(cumulative_usage)の定義(新規、本測定固有)**: 各subagent transcript内のassistantメッセージは同一`message.id`に対してstreaming差分で複数行出現するため、**同一message idの最終出現のusageを採用**し、distinctなmessage id(=1ターン)ごとの`input_tokens+output_tokens+cache_read_input_tokens+cache_creation_input_tokens`を**全ターンにわたり合算**したもの。既存レポートの「254件合計36,590,141 token」はSDK通知の`subagent_tokens`(最終ターンのcontext相当、本測定の`final_context_size`に近い概念)であり、**本測定のcumulative_usageとは定義が異なる**(cumulative_usageは複数ターンにまたがるcache_read等の累積のため、原理的に`final_context_size`より大きくなる。実際、本測定でも`final_context_size`合計(sonnet全体約5,859万)に対し`cumulative_usage`合計は約31.3億で桁が異なる)。両者を混同しないよう本REPORTでは明示的に併記する。
- **境界時刻の確定**: `git log --format="%H %ad" -S"E-1/D-1/G-1採用" -- DECISION_LOG.md`で該当行が導入されたcommitを特定し、`710241006b78164527606dad3615390fd26745b1`(2026-09-12 20:37:12 +09:00)と確認した。
- 一時解析スクリプト(repo外scratchpad、Git管理外): `remeasure_e1_d1_01.py`(main抽出・突合・per-task解析)、`remeasure_aggregate_01.py`(集計・相関)、`remeasure_reminder_tag_01.py`(委任文へのE-1/D-1/G-1明記有無タグ付け)。中間データ`remeasure_per_task_01.jsonl`/`remeasure_per_task_01_tagged.jsonl`も同ディレクトリ。

## 2. 母集団

| 区分 | Before(〜09-12 20:37:12) | After(09-12 20:37:12〜) |
|---|---|---|
| sonnet-worker委任数(Fable発行) | 357 | 33 |
| うちtranscript取得・解析成功 | 357(100%) | 33(100%) |
| opus-consultant委任数 | 13 | 1 |
| 観測期間 | 2026-09-05T05:40〜09-12T11:31(UTC、約7日) | 2026-09-12T11:39〜09-13T05:24(UTC、約18時間) |
| モデル | `claude-sonnet-5`(354/357、他はsynthetic/haiku混入2件) | `claude-sonnet-5`(33/33) |

**観測期間の非対称性(重要な交絡)**: Beforeは7日分・357件の多様なタスクを含むのに対し、Afterは約18時間・33件と短く、直近の特定作業クラスタ(3V Fact Safety設計、Trend/Discovery視聴Feedback対応等)に偏っている可能性が高い。

## 3. E-1: same-file reread率(文字ベース)

| | Before | After(全体) | After(委任文に明記あり18件中n=15で算出可) | After(明記なし18件中n=18) |
|---|---|---|---|---|
| n | 356 | 33 | 15 | 18 |
| 平均 | 35.2% | 42.7% | 33.6% | 50.3% |
| 中央値 | 33.9% | 40.8% | 40.0% | 44.2% |
| p25/p75 | 21.0%/46.7% | 28.3%/54.7% | — | — |

**種別別(中央値、Before→After)**: (a)Consolidation 44.8%→51.7%、(b)Trial 32.0%→31.4%(ほぼ同水準)、(d)Wiring 31.6%→39.6%。**いずれの種別でも改善方向は確認できず、E-1は明記の有無に関わらず効果が観測されない**。

## 4. D-1: 全文Read率・Read粒度

| | Before | After(全体) | After(明記あり) | After(明記なし) |
|---|---|---|---|---|
| 全文Read率(文字ベース)中央値 | 59.9% | 47.9% | 49.4%(n=13) | 39.8%(n=18) |
| 全文Read率(回数ベース)中央値 | 50.0% | 44.4% | — | — |
| Read1回あたり平均文字数 | 6,382字 | 4,022字 | — | — |
| tool呼び出し1回あたり平均文字数 | 2,463字(中央値) | 1,962字(中央値) | — | — |
| production code(`er0*.py`)読込文字比率 中央値 | 17.3% | 16.9% | — | — |

**種別別(全文Read率中央値、Before→After)**: (a)46.6%→61.3%(悪化)、(b)65.3%→63.9%(ほぼ同)、(d)Wiring 54.1%→36.7%(改善)。**Wiring種別(d)ではD-1の改善方向が種別内でも見える(明記あり3件では23.9%まで低下)が、n=2〜5と極小でロバストではない**。

## 5. G-1: git系Bash出力比率

Before中央値4.4%→After中央値8.9%(明記あり群では中央値10.0%、明記なし群では中央値5.7%)。**改善は確認できない**。ただし既存分析(`SUBAGENT-TOKEN-CONSUMPTION-BY-TASK-TYPE-01`)でもgit出力は主因ではなく(1.8〜6.8%水準)、絶対量として消費への影響は小さい。

## 6. Sonnet task総消費(Before/After、種別非統一)

| 指標 | Before(n=357) | After(n=33) | 変化 |
|---|---|---|---|
| 累積usage 中央値 | 4,296,480 | 5,324,655 | +23.9%(悪化) |
| 累積usage 平均 | 7,905,426 | 9,411,553 | +19.0%(悪化) |
| 最終ターンcontext(`final_context_size`)中央値 | 135,747 | 154,148 | +13.6%(悪化) |
| output_tokens累計 中央値 | 14,728 | 15,767 | +7.1%(悪化) |
| tool_uses中央値 | 50 | 68 | +36.0%(悪化) |
| tool_result総文字数 中央値 | 127,294 | 152,716 | +20.0%(悪化) |

**同種別比較(cumulative_usage中央値)**: (a)404.8万→575.6万、(b)785.9万→1,192.1万、(d)1,153.0万→697.6万(改善)、(f)315.5万→179.7万(改善、n=4)、(g)260.4万→458.3万(悪化)。**種別により方向がばらつき、全体としては悪化方向が優勢**。「Fable→Sonnet委任文の定型比率削減」と「subagent内部消費削減」は別軸であり、本測定は後者(内部消費)を対象にしている。

**委任文への明記有無で層別(cumulative_usage中央値)**: Before 429.6万 / After明記あり 271.3万(▲36.9%) / After明記なし 1,031.5万(+140%)。同一種別(type a)限定では明記あり203.0万・明記なし838.8万・Before404.8万で、**明記あり群が最も低い**。ただしn=6〜7と極小。

## 7. 交絡の整理(検出力の評価)

1. **観測期間の非対称**(7日 vs 18時間): Afterは特定の短期集中作業(3V Fact Safety設計等)に偏り、母集団としての代表性が低い。
2. **タスク種別構成比の違い**: (a)Consolidation比率25.8%→39.4%、(b)Trial比率29.4%→18.2%。種別間で平均消費・全文Read率の水準が異なる(既存レポートの通り(d)>(b)>(a)>(f))ため、単純な全体Before/After比較は種別構成の変化に交絡される。
3. **モデルは同一**(`claude-sonnet-5`)であり、モデル変更による交絡はない。
4. **tool_uses自体がAfterで上振れ**(中央値+36%)。tool_usesとcumulative_usageの相関が+0.93と強いため、Afterの消費増加の主因はタスクの複雑化(呼び出し回数)であり、E-1/D-1/G-1導入の失敗を直接示すものではない可能性がある。
5. **委任文への明記率が55%にとどまる**(45%は無記載)。運用ルールが徹底されていないため、「導入済みルールの効果測定」ではなく「部分的に適用されたルールの効果測定」になっている。
6. **結論**: 現状のN(After=33、種別別ではN<10がほとんど)と上記交絡の下では、**E-1/D-1/G-1の効果の有無を統計的に確定できるだけの検出力はない**。D-1については複数の指標(全文Read率相対▲20%、Read1回あたり文字数▲37%、tool呼び出し1回あたり文字数▲20%)が方向として改善を示しており、種別内比較でも(d)で改善が見えるため、**「効果ありそう」という弱いシグナルはある**。E-1・G-1については改善シグナルが見られない。

## 8. 施策1・2のTrial設計に必要な前提数値

- **tool_uses(tool_call_count) vs cumulative_usage の相関係数**: **+0.93**(n=390、sonnet-worker全期間)。単回帰: `usage ≈ 194,871 × tool_uses − 4,085,599`。
  - 施策1(tool_uses削減)の削減見込み試算: 平均tool_uses(62.2)を20%削減できた場合、線形近似では**タスク平均で約30%のusage削減**が示唆される。ただし切片が大きな負値であり低tool_uses域で式が破綻するため、**保証値ではなく上限側の楽観的試算**として扱うべき。
- **全文Read率(文字ベース) vs cumulative_usage の相関係数**: **−0.047(ほぼ無相関)**。
  - 施策2(D-1徹底)の削減見込み試算: 現状の全文Read率57.2%(Read結果文字数合計3,029万字中1,732万字)を25%まで下げられた場合、Read結果文字数は約1,299万字(▲42.9%)減少し、これはtool_result総文字数(合計5,749万字)の**約22.6%**に相当する。ただし相関が薄いため、**この文字量削減が実際のtoken消費(cumulative_usage)削減にどれだけ変換されるかは本測定だけでは分からない**(cache_read/cache_creationが消費の大半を占め、これはRead量よりも会話ターン数・履歴長に強く依存するため)。
- **reread_rate vs cumulative_usage の相関係数**: +0.012(無相関)。E-1施策単独では消費削減効果を予測する根拠が薄い。
- **prod_code_ratio vs cumulative_usage の相関係数**: +0.43(中程度の正相関)。Production配線タスクでのコード読込量は消費と一定の関連がある。

## 9. 制約・限界(正直な記載)

- 分類は管理ID/description文字列の正規表現による機械分類であり、人手レビューではない((g)「その他」は多様なタスクの混在)。
- `cumulative_usage`は全ターンの`input+output+cache_read+cache_creation`の単純合算であり、Anthropic課金上の実際のコスト(cache_read/cache_creationの単価差)を反映した金額換算ではない。あくまで相対比較用の代理指標。
- 委任文への「E-1/D-1/G-1明記」の判定はキーワード一致(`E-1`/`D-1`/`G-1`本文言および限定的な言い換え表現)による機械判定であり、Sonnet側が指示なしに自発的にE-1/D-1相当の振る舞いを行った可能性(逆に明記があっても実行されなかった可能性)は文面上の判定に留まる(実際のtool呼び出しパターンから見た挙動は6〜7節の実測値の通り)。
- After N=33(種別別ではN=0〜13)は統計的検出力が低く、特に(a)(d)(f)(g)以外の種別は0件またはごく少数。次回の再測定はAfter期間をさらに数日延ばし、委任文への明記率を100%に是正した上で実施するとより判定力が上がる。
- 観測期間の非対称(7日 vs 18時間)により、Afterのタスク構成は直近の特定案件(3V Fact Safety等)に偏っている可能性が高く、季節性・案件依存の効果と施策効果を分離できていない。
- opus-consultantはAfter n=1のみで比較不能。haiku-workerはtranscript内に該当エントリがほぼ見つからず(before 1件のみ、meta.json不整合の可能性)、別集計を提示できなかった。

## 10. 付録: 生成物一覧

- 本REPORT: `PM-TOKEN-EFFICIENCY-E1-D1-REMEASUREMENT-01_REPORT.md`(root新規)
- 一時解析スクリプト・中間データ(repo外scratchpad、Git管理外): `C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\scratchpad\`配下の`remeasure_e1_d1_01.py`、`remeasure_aggregate_01.py`、`remeasure_reminder_tag_01.py`、`remeasure_per_task_01.jsonl`、`remeasure_per_task_01_tagged.jsonl`、`remeasure_stderr.log`。
- `er011_pm_agent_read_audit_01.py`は無変更(import利用のみ)。他Agent成果物には一切触れていない。Gitへのcommit/pushは本タスクでは実施していない(並行タスクのGit操作と競合させないため)。

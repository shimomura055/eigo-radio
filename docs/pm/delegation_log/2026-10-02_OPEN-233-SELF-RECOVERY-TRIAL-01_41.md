# 委任記録(T-0): OPEN-233-SELF-RECOVERY-TRIAL-01 委任_41(2026-10-02)

(Fable -> Sonnet委任文の全文保存。見出しは省略せず保存。)

## 管理ID

`OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_41: **既存ログの無料集計+ユーザー決定の記録**。¥0。API・新Trial・有料LLM callなし。実装なし)。並行タスクなし(他Agentは動いていない)。

## 性質/到達上限Status/禁止事項

- 性質: read-onlyの集計・分析(既存記録のみ)と、2026-10-02ユーザー決定のSSOT記録。Opus独立技術レビューGate(PM_GOVERNANCE 11-3)の該当判定: **非該当**(既存記録の集計とドキュメント更新。受け渡し再設計そのものは同日Opus独立レビュー#5を実施済みで、今回は設計内容を変えない)。
- 到達上限Status: 集計結果を報告した時点でSTOP。OPEN-233のStatusは`USER_DECISION_REQUIRED`(無料集計のみ進行可、とのユーザー承認の範囲内)。
- 費用: ¥0(費用上限[Cap]を伴わないためT-3非該当)。
- 禁止事項(ユーザー原文§8: 実装/有料Trial/Checker Prompt変更/別AI引用救済の採用は未承認):
  - **実装しない**: `er052_open233_self_recovery_flow_runner_01.py`ほか既存の`*.py`・Prompt・テストを一切変更しない。runner・Trialスクリプト・回帰テストを実行しない。**LLM/API/TTS/Web Searchを呼ばない**。
  - **Production正式pathを変更しない**。
  - 集計用スクリプトは新規の分析専用ファイルとして`er052_output/open233_handoff_log_aggregation_01/aggregate_01.py`に置く(再現性のためcommitする)。**runner等の既存モジュールをimportしない**(import時の副作用・API設定依存を避けるため。必要な照合ロジックは集計スクリプト内に最小限で書く)。このスクリプトは既存JSONを読むだけで、どこからも呼ばれない分析物であり、受け渡し修正の実装ではないことを冒頭コメントに明記する。
  - 集計の「新しい受け渡し方式」の定義は下記「集計の定義」に**厳密に従う**。定義にない救済(類似度・単語重なり・位置比・判定役[Stage 2]の引用・Ledger語彙)を使わない。文全体への拡張(文単位スナップ)もしない。
  - 推測を事実として書かない。既存記録から決定論的に言えること(範囲が確定するか等)と、LLMの出力次第で分からないこと(Rewriteが実際に直すか、再検査が何を指摘するか)を必ず書き分ける。「解決できる」は「範囲を確定してRewriteへ渡せる」の意味に限定し、「人間確認が解消する」と混同しない。数値は分母・除外条件・重複の扱いを併記する。
  - `CURRENT_SPEC.md`・`docs/pm/PM_GOVERNANCE.md`・既存設計書(`docs/pm/design_open233_self_recovery_flow_01.md`、`docs/pm/design_open233_violation_span_handoff_01.md`)・`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`は編集しない。
  - `git add -A`/`stash`/`amend`/force push禁止。既存の未commit変更(`er0XX_output/`配下の既存ファイル)・無関係の未追跡ファイルに触れない・addしない。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。
(本委任はTTSを伴わない。T-1・T-3は非該当。T-0の保存先は`docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_41.md`、見出しは省略せず全文保存。)

## ユーザー指示(原文)

(2026-10-02、全文。`DECISION_LOG.md`へ**逐語で**収録すること。)

> OPEN-233について、直近のユーザー判断を反映して次工程へ進んでください。
>
> ## 1. 今回確定した方針
>
> ### Checker → Rewriteの受け渡し
> 基本線は以下です。
>
> 1. Checkerは違反箇所を原文ベースで返す
> 2. 複数文なら複数文のまま扱う
> 3. その違反範囲をそのままRewrite側へ渡す
> 4. 後段処理は、記事へ戻す・文脈取得・記録・再検査など必要なものだけ残す
> 5. 後段処理がCheckerの違反範囲を勝手に縮小・再解釈しない
>
> 文ID・文字オフセット方式は現時点では採用しません。
>
> ## 2. Checker Promptは今は変更しない
>
> まず受け渡し修正だけでどこまで解決できるかを見ます。
>
> したがって現時点では、
>
> - Checker Prompt変更なし
> - 「原文逐語で返す」指示追加なし
>
> としてください。
>
> 既存ログの集計結果から、受け渡し修正だけでは不十分と分かった場合に、Prompt変更を別Trialとして検討します。
>
> ## 3. Checkerの引用が一致しない場合の別AI引用救済は今は使わない
>
> 判定役など別のLLMが出した引用を使ってRewrite対象を決める案は、現時点では採用しません。
>
> 理由は、
>
> **後段がCheckerの違反範囲を再解釈しない**
>
> という基本線を守るためです。
>
> まず既存データで必要性を確認してください。
>
> ## 4. Rewrite範囲は既存の最小修正優先ルールを維持
>
> 文の一部が違反だからといって、最初から文全体へ広げないでください。
>
> 順番は既存ルールどおりです。
>
> **語句単位で修正**
> ↓
> 語句だけでは違反が解消しない、または文が不自然になる
> ↓
> **文全体へ拡張**
> ↓
> それでも不十分なら、さらに必要最小範囲へ拡張
>
> 例：
>
> `oil prices → Brent futures`
>
> で済むなら、語句だけ修正してください。
>
> 最初から文全体Rewriteすると、
>
> - 不要なFact追加
> - Hook/文章品質劣化
> - JA/ENズレ
> - コスト増
> - 非決定性増加
>
> のリスクがあるため、禁止します。
>
> 今回Fableが出していた「一致した断片を最初から文全体へ広げる」は、新しい仕様としては採用しません。
>
> ## 5. まず無料の既存ログ集計を実施
>
> この作業はユーザー承認済みです。
>
> API・新Trial・有料LLM callは使わず、既存記録のみで集計してください。
>
> 最低限、以下を出してください。
>
> ### A. 新しい受け渡し方式なら解決できる件数
> 過去のChecker指摘について、
>
> - 原文範囲をそのまま確定可能
> - 複数文のまま確定可能
> - 離れた複数箇所として確定可能
> - 確定不能
>
> に分類してください。
>
> ### B. meta_run03_standard
> Human Reviewになった各ケースについて、
>
> 新しい受け渡し方式なら、
>
> - 1回目でどの範囲をRewriteへ渡せるか
> - 余計な周回が減るか
> - cycle上限到達を回避できそうか
> - それでも残る問題は何か
>
> を具体的に示してください。
>
> ### C. Checker Prompt変更の必要性
> 既存ログだけで、
>
> - 受け渡し修正だけで十分そうか
> - 原文逐語Prompt追加が必要そうか
>
> を判定してください。
>
> ただしPrompt変更はまだ行わないでください。
>
> ### D. 別AI引用救済の必要性
> Checkerの引用だけでは確定できないケースが、
>
> - 何件
> - 全体の何%
> - Human Reviewに実際どの程度影響するか
>
> を出してください。
>
> 必要性が数字で確認されるまで採用しません。
>
> ## 6. 今回の無料集計後の判断
>
> 無料集計の結果、
>
> **受け渡し修正だけでmeta_run03_standardの主要問題が解消できそう**
>
> なら、次に
>
> - 受け渡し修正を実装
> - 限定Trial
>
> へ進む案を提示してください。
>
> 一方、
>
> - 多数のケースでChecker引用が確定不能
> - Prompt変更なしでは構造的に成立しない
> - 別AI引用救済が不可欠
>
> と分かった場合は、そこでSTOPしてUSER_DECISION_REQUIREDとして報告してください。
>
> ## 7. OPEN-233の残課題の全体像
>
> 現時点で見えている順番は以下です。
>
> 1. 今回のHuman Review残存問題
> 2. 修正後の最新版で29件横断再確認
> 3. 問題がなければ実記事N増し
>
> Hormuz過剰BLOCK、Meta Hook、Safety誤降格、不要な大規模Rewrite、false PASS検知、平均コストなどは、現時点では個別の見えている未解決課題としては一旦解消済みです。
>
> 今回のHuman Review問題が解消したあと、横断確認で新しい重大問題が出なければ、OPEN-233は基本的にN増し段階へ移る想定です。
>
> ## 8. Status / Gate
>
> 現在は`USER_DECISION_REQUIRED`でしたが、今回ユーザーが無料集計を承認したため、
>
> **無料集計については進行可**
>
> です。
>
> ただし、
>
> - 実装
> - 有料Trial
> - Checker Prompt変更
> - 別AI引用救済の採用
>
> はまだ承認されていません。
>
> 無料集計結果を報告した時点でSTOPしてください。
>
> Production正式pathは変更禁止です。

## 集計の定義(「新しい受け渡し方式」。この定義で機械的に判定する)

**範囲の確定(Checkerの文字列→記事中の範囲)**: Checkerが返した`claim_in_article`(runnerの記録では`claim_text`)だけを入力とし、次の文字単位の照合のみを順に試す。採用する範囲は「記事側の文字列」。
- L0: そのまま記事に含まれる
- L1: 文字列全体を囲む1組の引用符・括弧(“ ” " ‘ ’ 「 」 『 』)を外すと含まれる
- L2: 空白・改行の連続を1個の空白とみなす/曲線引用符・アポストロフィと直線のそれを同一視する、で含まれる
- L3: 大文字小文字を同一視すると含まれる
- L4(断片分解): 文字列が引用断片(“…”、「…」、『…』)を2つ以上含み、**断片以外の残りがつなぎ語・句読点・空白だけ**(and / or / , / ; / 、 / と / および / & 等)の場合に限り、各断片を別々の範囲候補にして、それぞれL0〜L3で照合する。残りに説明文(例: `Paragraph beginning “…”`)がある場合は分解せず「確定不能」とする(Checkerの指した範囲を縮小しないため)。
- 「確定」の条件: 照合後の文字列が、対象記事の本文に**ちょうど1箇所**出現すること。0箇所=確定不能(不一致)、2箇所以上=確定不能(複数箇所一致)。L4は全断片が確定した場合のみ確定。
- 照合先の記事: その指摘を出した検査(Stage 1またはRecheck)が見た記事本文。EN記事とJA記事(記録がある場合)の両方に対して照合し、どちらで確定したかを記録する(JA再検査由来の指摘はJA文字列でありうる)。検査が見た記事の特定方法は、委任_39付録Aの仮定(cycle1=`cycles[0].en_text_before_rewrite`、cycle k≥2=`cycles[k-2].en_text_after_rewrite`、JA側は対応する`ja_text_*`)を出発点にし、JSONの実構造を確認して正しければ採用、違えば正しい対応に直して明記する。記事本文が記録されていないcycleは「判定不能(本文記録なし)」として別集計(分母から除外し、件数を明記)。
- **使わないもの**: 類似度、単語重なり、位置比、Stage 2(判定役)のhint引用、Ledger語彙、文全体への拡張。

**分類(ユーザー§5-A)**: 確定した指摘を、範囲の形で分類する。文の区切りは、分類のためだけに簡易分割(`. ! ? 。 ！ ？`の後の空白/行末、段落区切り`\n\n`)を使う(範囲の決定には使わない)。
- A1 原文範囲をそのまま確定可能(単一範囲で、1文以内: 1文全体、または文の一部。内訳として「1文全体」「文の一部」を分ける)
- A2 複数文のまま確定可能(単一の連続範囲が2文以上にまたがる)
- A3 離れた複数箇所として確定可能(L4で2つ以上の範囲。範囲同士が隣接[間が空白のみ]か、間に他の文があるかも記録)
- A4 確定不能(内訳: 不一致[言い換え・省略記号・説明文・その他に原因分類]/複数箇所一致/L4条件を満たさない説明文混在)
- 併記: 確定に必要だった照合レベル(L0〜L4)別の件数。

**対象と分母**:
- 対象run: `er052_output/open233_self_recovery_flow_runner_01_*/instances_*/*.json`(iter5〜8、rep7〜rep21等、存在する全て)。対象ディレクトリ一覧とファイル数を明記。
- 指摘の種類を分けて集計: (K1)検査役が自分で書いた`claim_in_article`(Stage 1初回/Recheck別)、(K2)`same_fact_id_locations`から展開された指摘(逐語substring確認済みで作られる。別枠で件数のみ。あわせて、展開時に逐語でないため捨てられた`same_fact_id_locations`要素が記録から数えられるなら件数と例)、(K3)precheck由来(別枠、件数のみ)。主集計はK1。
- 重複: 固定Stage 1の再利用で同じ指摘が繰り返し現れる。**行数(延べ)とユニーク(記事ID+claim文字列)を両方**出す。
- 重大度別: Stage 2後の最終重大度(`materiality`)がBLOCKING(=実際にRewriteへ進む指摘)と、それ以外(QUALITY/ACCEPTABLE等=Rewriteへ進まない)を分ける。**受け渡しの影響を受けるのはBLOCKINGのみ**なので、主要な率はBLOCKING分母でも出す。
- 記事別(fixture名別)の内訳、とくに`meta_run03_standard`。
- 委任_39付録A(n=389、(a)157/(b)146/(c)19/(d1)34/(d)33)との対応・差異を1段落で説明(定義がL4条件・「ちょうど1箇所」・JA照合で変わるため数値は一致しなくてよいが、差の理由を示す)。

**現行(記録上の実際)との比較**: BLOCKINGでRewriteが実行された指摘について、記録された`rewrite_records`(対象決定のmethod、`before_fragment`)を「現行が実際に対象にした範囲」とし、新方式の範囲と比べて、同じ/現行が縮小(現行⊂新)/現行が拡大(現行⊃新)/別の箇所(重ならない)/一部重なり/新で確定不能/記録不足、に分類する。現行のmethod別(rewrite_hint_quote / multi_quote_span / 完全一致 / 類似度 / 単語重なり 等、記録されている語で)にも集計。

## 出すべき結果(ユーザー§5 A〜D、§6)

**A. 新しい受け渡し方式で範囲を確定できる件数**: 上記分類の表(全体・BLOCKINGのみ・記事別・延べ/ユニーク)。

**B. meta_run03_standard**: Human Review(Stage 4)になった各ケースを処理順で。
- 主対象: 現行コード(委任_35・36の修正後)で固定Stage 1入力を使ったrun(rep20 sample1・2、rep21 sample1・2)。Stage 4になった2 run(rep20 s2、rep21 s1)は詳細に、解消した2 run(rep20 s1、rep21 s2)は**対照として**同じ形式で(同じ指摘[MUSE-HC-011の2文claim等]が、どの対象範囲でRewriteへ渡り、何周で解消したか、別事実MUSE-HC-010の指摘がいつ出てどう処理されたか)。
- 参考: それ以前のmeta_run03_standardのStage 4(iter8、rep16〜19等)を一覧にし、stage4_reasonと、その原因が委任_33〜36で是正済みか・受け渡し起因かを1行ずつ。
- 各Stage 4ケースについて、周回ごとに: BLOCKING指摘の`claim_text`(逐語)→現行が実際に対象にした範囲(記録)→新方式で1回目に渡せる範囲(確定結果、逐語)→差(縮小/拡大/同じ)。
- 「余計な周回が減るか」「cycle上限到達を回避できそうか」: **決定論的に言える部分**(例: 2文とも1周目の対象に入る=取りこぼしによる持ち越しは構造上起きない)と、**LLM次第の部分**(Rewriteが2文とも直すか、再検査が新規指摘を出すか)を分ける。後者は、対照run(同じ指摘が2文範囲で渡った実績。rep20 s2 cycle1ほか、記録から拾える全件)の結果を件数付きの傍証として示し、断定しない。
- rep20 s2(離れた2文、origin=`ja_source`): 新方式(別AI引用救済なし・Checker Prompt変更なし)では、EN側は2範囲を確定できるが、JA側の対応範囲を決める情報がない。この場合に現行コード上どの経路になるか(EN側のみ直す経路[runner 3081〜3106付近]→JA再検査→JA側の指摘が次周回へ、等)を**コードを読んで**示し、cycle上限(`MAX_CYCLES=2`/`HARD_MAX_CYCLES=3`、追加1周条件 runner 4194〜4226)の中で収まる見込みがあるか、`ja_deviation_unresolved`等で人間確認になる構造的な可能性があるかを、決定論的に言える範囲で述べる。コード上断定できない点は「不明」と書く。
- 「それでも残る問題」: 再検査が周回ごとに別事実を新規指摘する揺れ、判定役の重大度判定の揺れ、JA/EN対応、等を、このrun群の記録で実際に観測された事実に基づいて列挙。

**C. Checker Prompt変更の必要性(判定)**: A(確定不能の率と原因内訳: Promptで逐語を指示すれば解消しそうな種類[引用符・大文字化・and結合・省略記号・言い換え]か、指示しても解消しない種類か)とBを根拠に、「受け渡し修正だけで十分そう」/「原文逐語Prompt追加が必要そう」/「既存ログだけでは判定できない(何が分かれば判定できるか)」のいずれかを、根拠の数値とともに示す。Prompt変更は行わない。

**D. 別AI引用救済の必要性**:
- Checkerの文字列だけでは確定できない指摘の件数・率(全体/BLOCKINGのみ、延べ/ユニーク、記事別)。
- Human Reviewへの影響: **BLOCKINGかつ確定不能の指摘を1件以上含むrun**の数と率(分母=cyclesを持つ全run、および最新の広いTrial iter8の29 instance単独でも)。それらのrunが記録上(現行方式で)最終的にどうなったか(解消/Stage 4、stage4_reason別)。**「現行方式では解消していたが、新方式(確定不能=人間確認)だと人間確認に回るrun」の件数**=新方式で増えうる人間確認の上限見積もり。逆に、現行方式でStage 4だったrunのうち、新方式で対象範囲が変わる(縮小/拡大が是正される)run数=減りうる側の上限見積もり。
- 参考値として、確定不能のBLOCKING指摘のうち、Stage 2のhint引用が記事に逐語でちょうど1箇所一致するものの件数(=救済を入れた場合に拾える上限。**採用はしない。必要性の数字として出すだけ**)。
- 判定: 救済が「不可欠」「あれば有用だが不可欠ではない」「不要」のいずれと言えるかを数値で。

**E. 補足(効果の上限)**: 全記事の最近のStage 4(少なくともiter8の29 instanceとrep16以降)をstage4_reason別に数え、うち受け渡し起因と機械的に言えるもの(現行の対象が新方式の範囲と異なるBLOCKING指摘を含む)がどれだけあるか。

**F. §6の判定材料**: 「受け渡し修正だけでmeta_run03_standardの主要問題が解消できそうか」に対する、集計者としての所見(根拠付き、断定できない点は明示)。および、ユーザー§6のSTOP条件3つ(多数のケースで確定不能/Prompt変更なしでは構造的に成立しない/別AI引用救済が不可欠)それぞれに該当するか否かの所見。**最終判定と次工程の提示はFableが行う**ので、所見と根拠数値を示すに留める。

## 事前指定Read一覧

- `docs/pm/design_open233_violation_span_handoff_01.md`: §2-4(156〜180行)、§4-3(238〜257行)、付録A・B(529〜563行)(前回集計の定義と結果)
- `docs/pm/opus_l2_review_open233_self_recovery_05.md`: 「## 5. 修正提案・代替案」「## 6. 設計案の事実誤認・見落とし」「## 8. 実装・Trial前に確認すべきこと」(Grepで位置特定)
- `er052_open233_self_recovery_flow_runner_01.py`: 275〜279(cycle上限)、2449〜2473(`locate_target`、現行methodの語彙)、2920〜3110(`paired_rewrite`、片側のみ特定の経路)、3199〜3203、4194〜4226(追加1周条件)、4496〜4650(Recheck・JA Recheck・次cycleの構築)、およびstage4_reasonを設定している箇所(`ja_deviation_unresolved|cycle_limit_exhausted|ladder_exhausted|target_not_locatable`でGrep)
- instance JSONの構造把握: `er052_output/open233_self_recovery_flow_runner_01_rep21/instances_s1/meta_run03_standard.json` のトップレベルキーと`cycles[0]`のキー一覧(Pythonでキーのみ出力。全文Read不可)
- `DECISION_LOG.md`: 末尾エントリの見出し・冒頭数行(書式)
- `OPEN_ITEMS.md`: OPEN-233行の次Actionセル末尾(追記位置のみ)
- `docs/pm/REPORT_LEDGER.md`: OPEN-233行(委任_40で追加)の位置

## 事前指定Grep一覧+追記位置・更新位置の手順

- `ls`/Globで`er052_output/open233_self_recovery_flow_runner_01_*/`の一覧とinstanceファイル数。
- runnerに対し`stage4_reason`の全設定箇所。
- 追記・更新位置:
  1. **新規** `er052_output/open233_handoff_log_aggregation_01/aggregate_01.py`(集計スクリプト)、同ディレクトリ`results_01.json`(全集計結果、指摘ごとの判定明細を含む)、必要なら`claims_detail_01.csv`(指摘ごとの明細)。
  2. **新規** `docs/pm/report_open233_handoff_log_aggregation_01.md`(集計報告。A〜Fと、定義・分母・除外・限界。読み手はプロジェクト責任者: 平易な日本語、技術用語は初出時に短い説明、表を使う。冒頭に結論を10行以内)。
  3. `DECISION_LOG.md`末尾へ新規エントリ「OPEN-233-SELF-RECOVERY-TRIAL-01: 受け渡し再設計の方針確定(一部)と無料集計の承認(2026-10-02ユーザー決定、委任_41)」。内容: (1)ユーザー原文の逐語全文、(2)確定事項(基本線5点/文ID・文字オフセット不採用[現時点]/Checker Prompt変更なし[現時点]/別AI引用救済不採用[現時点、必要性が数字で確認されるまで]/Rewrite範囲は既存の最小修正優先ルール維持、「一致した断片を最初から文全体へ広げる」は不採用/無料集計の承認)、(3)未承認事項(実装・有料Trial・Checker Prompt変更・別AI引用救済)、(4)設計案`docs/pm/design_open233_violation_span_handoff_01.md`・Opusレビュー#5との関係(設計案のうち`violation_spans`追加[§2-2]・J1[§4-3]は現時点で不採用/保留、Opus修正案2[文単位スナップ]・3[Stage 2引用による救済]・6①[Stage 2のJA引用]は不採用、設計案・レビューのファイル自体は編集しない)、(5)残課題の順番(ユーザー原文§7)、(6)本委任の集計結果ファイルへの参照。
  4. `OPEN_ITEMS.md` OPEN-233行の次Actionセル末尾へ追記(Statusセル・他列不変): 「(2026-10-02)ユーザー決定: 受け渡しの基本線5点を確定、Checker Prompt変更なし・別AI引用救済なし・文全体への拡張なし(既存の最小修正優先ルール維持)。無料集計(既存記録のみ)を実施し`docs/pm/report_open233_handoff_log_aggregation_01.md`に報告。実装・有料Trial・Checker Prompt変更・別AI引用救済は未承認。集計結果の報告時点でSTOP」。
  5. `docs/pm/REPORT_LEDGER.md`: OPEN-233行(委任_38〜40)の備考へ委任_41(無料集計)を追記、または既存書式に合わせて1行追加。Opus発火=無(本委任)。
  6. `docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`(`.gitignore`対象、addしない): ACTIVE_TASK固定ヘッダは、管理ID=OPEN-233 委任_41(無料集計、¥0)/Status=USER_DECISION_REQUIRED(無料集計を報告した時点でSTOP。実装・有料Trial・Checker Prompt変更・別AI引用救済は未承認)/UDR-blocking=集計結果を踏まえた次工程(受け渡し修正の実装+限定Trialへ進むか)/UDR-deferred=修正後の29件横断再確認、実記事N増し(Phase 2テーマ選定)/APPROVED未配線=なし/STOP条件=無料集計結果の報告時点でSTOP(ユーザー明示指示)/次アクション=Fableが集計結果を照合しユーザーへ報告/未回答報告=なし/報告単位Status=OPEN-233 委任_41=報告待ち。

## 実行コマンド全文

作業ディレクトリ `C:\Users\tensh\eigo-radio`。
1. `git status --porcelain=v1 | grep -v '^??'`(作業前確認)
2. Read/Grepで構造把握→`er052_output/open233_handoff_log_aggregation_01/aggregate_01.py`作成。
3. `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe er052_output/open233_handoff_log_aggregation_01/aggregate_01.py`(入力=`er052_output/open233_self_recovery_flow_runner_01_*/`、出力=同ディレクトリの`results_01.json`等。ネットワーク・API不使用。2回実行して結果が同一であること[決定論]を確認)
4. 検算(必須): (i) rep21 s1の固定Stage 1 deviations[1](“It said human staff … cable fees.”)がL1で確定し、A2(複数文のまま)に分類されること。(ii) rep20 s2 cycle2の`“They could not tell if it was AI or a person” and “They did not realize it.”`がL4で2範囲に確定しA3に分類されること。(iii) `Paragraph beginning “People asking Muse to call”`(記録にある場合)が分解されずA4になること。(iv) meta_run03_standard rep19〜21のK1件数が委任_39付録Aの23件と整合するか(違えば理由)。(v) 無作為に10件、明細を目視して分類が定義どおりか確認。結果を報告書に記載。
5. T-0: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_41.md --json-out docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_41.md_check.json`
6. `git diff --stat`(既存`*.py`・Promptに差分がないこと)、Git(下記)。
runner・Trialスクリプト・回帰テストは実行しない。

## SSOT追記文

上記「追記位置」3(`DECISION_LOG.md`)・4(`OPEN_ITEMS.md` OPEN-233行)・5(`docs/pm/REPORT_LEDGER.md`)のとおり。

## Git(明示add対象・コミットメッセージ・trailer)

- SSOT編集権: **あり**(`DECISION_LOG.md`・`OPEN_ITEMS.md`[OPEN-233行の追記のみ]・`docs/pm/REPORT_LEDGER.md`)。
- 明示`git add`対象(1ファイルずつ): `er052_output/open233_handoff_log_aggregation_01/aggregate_01.py` / 同`results_01.json` / (作成した場合)同`claims_detail_01.csv` / `docs/pm/report_open233_handoff_log_aggregation_01.md` / `DECISION_LOG.md` / `OPEN_ITEMS.md` / `docs/pm/REPORT_LEDGER.md` / `docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_41.md` / 同`_41.md_check.json`(`er052_output/`が`.gitignore`対象でaddできない場合は、スクリプトと結果を`docs/pm/analysis/open233_handoff_log_aggregation_01/`へ置き直してaddし、その旨を報告)
- コミットメッセージ: `OPEN-233-SELF-RECOVERY-TRIAL-01: 受け渡し方針のユーザー決定を記録、既存ログの無料集計(範囲確定可否・meta_run03_standard・Prompt変更/別AI引用救済の必要性)を実施、実装・Trialなし(委任_41)`
- trailer: `git log -1 --format=%B c3555de0`の形式に合わせる。commit後`git push origin main`。エラー・競合が出たらSTOPして報告。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`と最終メッセージに次を記載(最終メッセージは数値を省略しない):
1. 対象(ディレクトリ数・instance数・指摘数、K1/K2/K3、除外件数と理由)、検査が見た記事の特定方法(仮定が正しかったか)。
2. **A**: 分類表(全体/BLOCKINGのみ、延べ/ユニーク、照合レベル別)、`meta_run03_standard`の内訳、付録Aとの差の説明。現行との比較表(同じ/縮小/拡大/別の箇所/確定不能、method別)。
3. **B**: meta_run03_standardの各ケース(rep20 s2、rep21 s1を詳細、rep20 s1・rep21 s2を対照)の周回別の表と、4つの問い(1回目に渡せる範囲/余計な周回が減るか/上限到達を回避できそうか/残る問題)への答え。決定論的に言える部分とLLM次第の部分の区別。rep20 s2のJA側のコード上の経路。
4. **C**: Checker Prompt変更の必要性の判定と根拠数値。
5. **D**: 確定不能の件数・率、Human Reviewへの影響(増えうる上限/減りうる上限)、hint引用で拾える参考値、救済の必要性の判定。
6. **E**: 効果の上限(全記事のStage 4のうち受け渡し起因と言える数)。
7. **F**: §6の判定材料(所見)、STOP条件3つへの該当有無の所見。
8. 検算(手順4)の結果、決定論確認(2回実行で同一)。
9. 限界・未確認(記録不足で判定できなかった件数、仮定、LLM次第で分からないこと)。
10. T-0結果、既存`*.py`・Prompt未変更の確認、commitハッシュ・push結果・`git show --stat HEAD`、変更ファイルのraw.githubusercontent.com URL。
11. 指示どおりにできなかった点・迷った点・一覧外の追加Read。

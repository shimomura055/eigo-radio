## 管理ID

`PM-OPUS-INDEPENDENT-TECH-REVIEW-GATE-2026-10-02`(委任_02 = Fableからの修正・追加指示1回目。ユーザーが競合K1〜K6の解消方針を決定したことを受けた正式反映)。
**並行タスクあり**: 別のsonnet-workerが `OPEN-233-SELF-RECOVERY-TRIAL-01` 委任_39(設計再検討)を実行中。同タスクは新規ファイル3つ(`docs/pm/design_open233_violation_span_handoff_01.md`、`docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_39*`)の作成のみでgit操作をしない。**本委任ではそれらのファイルに触れない・addしない**。

## 性質/到達上限Status/禁止事項

- 性質: PM/開発運用ルール(文書)の正式反映(ユーザー決定済み事項の反映)。Opus独立技術レビューGate(PM_GOVERNANCE 11-3)の該当判定: **非該当**(ドキュメント更新。11-3節「Opusレビュー不要の例」)。
- 到達上限Status: 運用ルールとして正式反映済み。Production仕様のStatusには関与しない。
- 費用: ¥0(API・TTS・Trial・Opus起動なし。費用上限[Cap]を伴わないためT-3非該当)。
- 禁止事項:
  - **モデル指定を変更しない**: `.claude/agents/*.md`のfrontmatterのうち`name`・`tools`・`model`行は一切変更しない。変更してよいのは`sandwich-pm.md`と`opus-consultant.md`の`description`行(説明文)と本文の指定箇所のみ。`sonnet-worker.md`・`haiku-worker.md`は編集しない。
  - **Fable本体の役割・他の既存仕様を不要に変更しない**(ユーザー原文§3)。`sandwich-pm.md`で変更するのは下記で指定した3箇所(description・手順7・手順8)のみ。委任先の制限、自分ではしないこと、手順1〜6、上限到達時、報告の各節は変更しない。
  - 今回変更するのは「新ルールとの矛盾を解消するために必要な説明部分だけ」。Sonnet委任のループ上限(初回+修正3回)、難問診断(L3)の上限と診断後の扱い、任意レビュー枠(Fable裁量1日2回)、context packet方式、Opus入力限定、Production採用はユーザーのみ、は変更しない。
  - コード(`*.py`)・Prompt・Production path・`CURRENT_SPEC.md`を変更しない。OPEN-233の技術変更・設計をしない。
  - `PM_GOVERNANCE.md`の既存の歴史的記述(11節・11-2節等の過去の決定文)は**削除・書き換えせず**、同ファイルの既存慣行(例: 1642〜1647行「(2026-09-27追記、旧運用の位置づけ)…本パラグラフ自体は上書きせず、歴史的記録として保持する」)に従い、該当箇所の直後へ日付付きの追記で「2026-10-02に11-3節により更新された。現行の扱いは11-3節」と明示する。**例外**: 本日(2026-10-02)新設した11-3節の中の「未解決の競合」「暫定運用」「既存ルールとの関係」「OPEN-233への当てはめ」の各段落は、解消後の内容へ直接書き換えてよい(K1〜K6の内容と解消結果は残す)。
  - 運用指示として実際に読み込まれるファイル(`sandwich-pm.md`・`opus-consultant.md`・`CLAUDE.md`・`PM_BRIEF.md`・テンプレート)は、古い文を残すと誤動作の元になるため、該当文を新ルールに合う文へ**直接置き換える**(変更前の文言はDECISION_LOGのエントリに逐語で記録する)。
  - `DELEGATION_STANDARD_TEMPLATE.md`の見出し文字列を変更しない。
  - `CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`PM_GOVERNANCE.md`の全文Read禁止。
  - `git add -A`/`stash`/`amend`/force push禁止。既存の未commit変更・未追跡ファイル(`er0XX_output/`配下、`docs/pm/delegation_log/2026-10-01_PM-CRASH-DATA-INTEGRITY-CHECK-01*`、`2026-10-02_PM-OPUS-MODEL-ID-INVENTORY-01*`、並行タスクの新規ファイル等)には触れない・addしない。
  - ユーザー決定に書かれていない新しい条件・例外を勝手に追加しない。解釈が必要だった点は下記「Fableの解釈」に従い、それ以外に迷った点は編集せず報告する。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-
WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久
運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を
`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/
check_delegation_prompt.py --file <path> --json-out <path>_check.json`
を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する
(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、
既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルール
ではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り
`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外
条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`
等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは
別ラベルであり、ラベルの意味を混同しない。
(本委任はTTSを伴わない。T-1・T-3は非該当。T-0は本委任文を**要約せず全文**、`docs/pm/delegation_log/2026-10-02_PM-OPUS-INDEPENDENT-TECH-REVIEW-GATE-2026-10-02_02.md`へ保存する。)

## ユーザー指示(原文)

(2026-10-02、ユーザーの決定全文。`DECISION_LOG.md`へ**逐語で**収録すること。)

> Opus独立技術レビューGateの既存ルールとの競合について、以下の方針で正式に整理・反映してください。
>
> ## 1. 必須Opusレビューの回数上限
>
> 条件A〜Dによる**必須Opusレビューは、従来の回数上限の対象外**としてください。
>
> 従来の、
>
> - 1管理IDにつき設計レビュー1回
> - 難問診断1回
>
> 等の上限は、任意レビュー・難問診断側にのみ適用してください。
>
> 理由は、必須条件が発火しているのに回数上限によってレビューできない状態を避けるためです。
>
> ただし、同じ内容を無意味に何度もレビューさせることは避けてください。
>
> ## 2. Fable裁量の任意Opusレビュー枠
>
> 現行の、
>
> **Fable裁量で1日2回まで**
>
> の任意レビュー枠は残してください。
>
> 必須条件A〜Dとは別枠です。
>
> 単純な実装確認等でOpusを多用しないことも維持してください。
>
> ## 3. 古い説明文
>
> Fable本体・Opus側の既存説明にある、
>
> > Opusは難問診断だけに使う
>
> 等、新ルールと矛盾する古い説明文は、新しいOpus独立技術レビューGateに合わせて修正してください。
>
> ただし、
>
> - モデル指定
> - Fable本体の役割
> - 他の既存仕様
>
> は不要に変更しないでください。
>
> 今回変更するのは、**新ルールとの矛盾を解消するために必要な説明部分だけ**です。
>
> ## 4. Production採用前とProduction配線完了前のレビュー重複
>
> 同じ変更・同じ設計内容について、Opusレビューを機械的に2回実施しないでください。
>
> 原則として、
>
> **Production採用提案前に実施したOpusレビューを、その後のProduction配線完了判定でも再利用可能**
>
> としてください。
>
> ただし、その後に以下があれば再レビューしてください。
>
> - 設計変更
> - 実装方針の重要変更
> - retry / fallback等への新しい配線
> - 新しい重大リスクの発見
> - Opusレビュー時の前提が崩れた場合
>
> つまり、
>
> **内容が変わっていなければ重複レビューしない。内容が変われば再レビューする。**
>
> としてください。
>
> ## 5. Opusレビュー後のユーザーSTOP条件
>
> ここは現行ルールを変更します。
>
> 今後は、
>
> **Opusレビューが入ったという理由だけで、毎回ユーザー判断待ちにしないでください。**
>
> 以下の場合は、Fable判断で次工程へ進んで構いません。
>
> - Claude案とOpusレビューが実質的に一致している
> - 既存のユーザー承認済み仕様の範囲内
> - 新しいProduct原則を追加しない
> - Safety/QCD上の新しい重大トレードオフがない
> - Production正式採用判断ではない
> - 予算・Scope等の既存Guardrail内
> - USER_DECISION_REQUIREDに該当する未決事項がない
>
> 一方、以下の場合は必ずSTOPしてユーザー判断を求めてください。
>
> - Claude案とOpusで重要な結論が対立
> - 新しい仕様・Product原則の採用が必要
> - Safety/QCD上の明確なトレードオフが発生
> - Production正式採用判断が必要
> - 既存のユーザー承認内容を変更する必要
> - 予算・Scope・運用方針を変更する必要
> - Opusレビューによって新しいUSER_DECISION_REQUIREDが発生
>
> つまり、
>
> **Opusレビューは技術品質を上げるためのGateであり、それ自体をユーザー承認Gateにはしない**
>
> という整理です。
>
> ## 6. Fableの責務
>
> Opusレビュー後は、Fableが必ず、
>
> - Claude案
> - Opusレビュー
> - CURRENT_SPEC
> - DECISION_LOG
> - OPEN_ITEMS
> - ユーザー承認済み内容
> - QCD
> - PM強制Gate
>
> を照合してください。
>
> Opusの意見を自動採用するのではなく、PMとして次工程へ進めてよいか判断してください。
>
> ## 7. 既存文書への正式反映
>
> 上記方針を、
>
> - PM_GOVERNANCE
> - DECISION_LOG
> - Fable / Opusの説明文
> - 必要な委任テンプレート
> - Production採用・配線Gate
>
> 等へ整合的に反映してください。
>
> 重複定義は増やさず、SSOTを明確にしてください。
>
> 反映後、
>
> - 変更ファイル
> - 5項目それぞれをどう解消したか
> - 新旧ルール間に残る競合の有無
> - 実際にどの条件でユーザーSTOPになるか
> - commit / push結果
>
> を報告してください。
>
> ## 8. OPEN-233について
>
> OPEN-233のRewrite対象受け渡し設計は、今回の運用ルール反映とは別作業のまま継続してください。
>
> 今回すでに明示している通り、
>
> - Checkerは違反箇所を原文逐語で返す
> - 複数文なら複数文のまま返す
> - その範囲をそのままRewriteへ渡す
> - 記事へ戻すために必要な後段処理だけ残す
> - 後段処理がCheckerの違反範囲を勝手に縮小・再解釈しない
>
> という基本線でClaudeが設計し、その設計をOpusが独立レビューしてください。
>
> このOPEN-233については、今回特別に、設計＋Opusレビュー結果が出た時点で一度ユーザーへ報告してください。
>
> まだ実装・Trialへは進まないでください。

## Fableの解釈(ユーザー決定に明記のない境界の扱い。報告に「解釈」として明記すること)

- **解釈1(11-2節の必須レビューの上限)**: ユーザー原文§1は「従来の上限は、任意レビュー・難問診断側にのみ適用」と定める。したがって、11-3節の条件A〜Dに加え、11-2節の必須Opusレビュー(発火条件(i)〜(iv))も「必須」である以上、回数上限の対象外として扱う。従来の「L2 1回+L3 1回/管理ID」は、任意レビュー(L2相当)と難問診断(L3)に適用する。任意レビューの「Fable裁量、1日2回まで」は別途そのまま有効。
- **解釈2(難問診断L3の後の扱い)**: ユーザー原文§5は「Opusレビュー後」の扱いを変更する。難問診断(L3: Sonnet差し戻しでも未解決の難問の診断)の後の扱い(Sonnetを自動再実行しない、実装が必要ならユーザー判断)は、ユーザー決定に言及がないため**従来どおり変更しない**。新しい進行/STOP条件は、Opusレビュー(11-3条件A〜D、11-2必須レビュー、任意レビュー)の後に適用する。
- **解釈3(重複回避の一般化)**: §1「同じ内容を無意味に何度もレビューさせない」と§4「内容が変わっていなければ重複レビューしない。内容が変われば再レビューする」を、必須レビュー全般の原則として11-3節に1箇所だけ書く。再レビューが必要になる5条件は原文§4のとおり。

## 正本(SSOT)の置き場所

- **正本は`docs/pm/PM_GOVERNANCE.md` 11-3節のみ**(回数上限の扱い、重複レビューの回避と再利用、Opusレビュー後の進行条件7つ・STOP条件7つ、Fableの照合対象8項目)。
- 他ファイルは要約+11-3節へのポインタ。ただし`.claude/agents/sandwich-pm.md`はFableが実際に読み込む指示文のため、進行条件・STOP条件を**要約として**含める(末尾に「正本は11-3節」と明記)。

## 編集内容(ファイル別)

### 1. `docs/pm/PM_GOVERNANCE.md`
(a) **11-3節(L1946〜2086付近)**:
- 「**既存ルールとの関係(変更しないもの)**」段落: 「Opus結果を受けてSonnetを自動再実行しない」は維持、という記述を解消後の内容へ改める(context packet方式・Opus入力限定・11-2発火条件(i)〜(iv)・REPORT_LEDGER記録・11-1/14節との関係は維持。Opusレビュー後の扱いは下記の新段落による。難問診断[L3]後の扱いは従来どおり)。
- 新段落「**回数上限の扱い(2026-10-02ユーザー決定)**」: 原文§1・§2と解釈1。必須レビュー(11-3条件A〜D、11-2必須)は回数上限の対象外。従来の上限は任意レビュー・難問診断にのみ適用。任意レビュー枠(Fable裁量、1日2回まで)は必須条件とは別枠で存続。単純な実装確認等でOpusを多用しない。
- 新段落「**重複レビューの回避(2026-10-02ユーザー決定)**」: 原文§4と解釈3。Production採用提案前に実施したレビューは、その後のProduction配線完了判定(Gate 3、11-2節の必須レビュー)で再利用可能。再レビュー条件5つ(原文どおり)。「内容が変わっていなければ重複レビューしない。内容が変われば再レビューする。」
- 新段落「**Opusレビュー後の進行判断(2026-10-02ユーザー決定、従来ルールの変更)**」: 原文§5を逐語に近い形で。「Opusレビューが入ったという理由だけで、毎回ユーザー判断待ちにしない」「Fable判断で次工程へ進んでよい条件(7つ、全て満たす場合)」「必ずSTOPしてユーザー判断を求める条件(7つ、いずれかに該当する場合)」「Opusレビューは技術品質を上げるためのGateであり、それ自体をユーザー承認Gateにはしない」。解釈2(難問診断L3後は従来どおり)を1文。**ユーザーが個別案件で報告・STOPを明示指示している場合はその指示が優先**(22節「ユーザー指示優先」と同旨、例: OPEN-233は設計+Opusレビュー結果が出た時点で報告し実装・Trialへ進まない)を1文。
- 「**Fableの役割**」段落: 照合対象を原文§6の8項目(Claude案・Opusレビュー・CURRENT_SPEC・DECISION_LOG・OPEN_ITEMS・ユーザー承認済み内容・QCD・PM強制Gate)へ更新し、「Opusの意見を自動採用するのではなく、PMとして次工程へ進めてよいか判断する」を追記(役割分担3行は維持)。
- 「**未解決の競合**」「**暫定運用**」段落: 「**競合K1〜K6の解消(2026-10-02ユーザー決定)**」へ書き換え。K1=必須レビューは上限対象外(上記)/K2=任意枠は存続/K3・K6=説明文を新ルールに合わせて修正済み(モデル指定・役割は不変)/K4=再利用可・内容が変われば再レビュー/K5=進行条件・STOP条件を新設(従来の「毎回ユーザー判断待ち」を変更)。残存競合の有無を明記(作業後の確認結果に基づき「なし」または残るものを列挙)。
- 「**OPEN-233への当てはめ**」段落: 「回数上限との関係はK1」を「必須レビューは回数上限の対象外(K1解消)。ユーザー明示指示(2026-10-02)により、設計+Opusレビュー結果が出た時点でユーザーへ報告し、実装・Trialへは進まない」へ更新。
(b) **11-2節**: 「Opus結果を受けてSonnetを自動再実行しない(既存運用を維持)」(L1900付近)、「**上限**: L2 1回+L3 1回/管理ID…」(L1909〜1912付近)、「**Gate 3との関係**」(L1921付近)、末尾の「11-3節との関係」(L1941〜1944)。既存文は残し、末尾の「11-3節との関係」段落を拡充して「(2026-10-02更新)上限は任意レビュー・難問診断にのみ適用、必須レビューは対象外/Opusレビュー後の扱いは11-3節の進行判断による/Gate 3ではProduction採用提案前のレビューを再利用可、再レビュー条件は11-3節」を明記する。加えて、誤読防止のため上記3箇所それぞれの直後に「(2026-10-02更新: 11-3節参照)」の短い注記を入れる。
(c) **11節**: 「**不変の項目**: Opus診断1回上限…」(L1606〜1608)、MODEL ROUTING運用Trial段落の「1管理IDあたりのOpus利用はL2+L3合計で最大1回」(L1621付近)、L2事前レビュー段落(L1637〜1638付近)。既存文は残し、各箇所の直後に「(2026-10-02更新: 回数上限・Opusレビュー後の扱いは11-3節により更新。現行の扱いは11-3節)」の注記。ほかにGrepで見つかる同旨の箇所(前回報告のL70・L752・1節のopus-consultant項目)も同じ注記方式。
(d) **2節 Gate 2・Gate 3**: Gate 2末尾の条件Cポインタ(前回追記)はそのまま。Gate 3の既存追記(「必須Opusレビュー該当案件は…Opus所見の反映状況もGate 3項目に含める」)の直後に、「(2026-10-02追記)Production採用提案前に実施したOpusレビューは再利用可。11-3節の再レビュー条件に該当する場合のみ再レビューする」を追記。
(e) 末尾の変更履歴へ1項目。

### 2. `.claude/agents/sandwich-pm.md`(Fable本体定義。**指定3箇所のみ**)
- frontmatter `description`: 「…通常作業をsonnet-workerへ、難問の診断だけをopus-consultantへ委任し、Gateと受入判定を行う。」→「…通常作業をsonnet-workerへ、重要な技術設計の独立レビューと難問の診断をopus-consultantへ委任し、Gateと受入判定を行う。」(他の語句・引用符・他のfrontmatter行は不変)
- 手順7(「7. 差し戻しても解決しない難問についてのみ…(Opus自身の追加探索は妨げない)。」の項目全体)を次へ置き換え:
```
7. opus-consultantへの依頼は次の3種類とする(条件・上限の正本は
   `docs/pm/PM_GOVERNANCE.md` 11-2節・11-3節)。いずれも全文再レビューでは
   なく重要論点にスコープを絞って委任する(Opus自身の追加探索は妨げない)。
   - 必須レビュー: 11-3節の条件A〜D(新しい構造・処理フローの設計・変更の
     実装前/同じ問題へ2回修正しても再発したときの3回目の個別パッチ前/
     重要変更のProduction採用提案前/QCDが大きく悪化したとき)、および
     11-2節の発火条件(i)〜(iv)に該当する場合。案件別のユーザー事前承認は
     不要で、回数上限の対象外。ただし同じ内容を無意味に繰り返しレビュー
     させない(内容が変わっていなければ既存レビューを再利用し、内容が
     変われば再レビューする)。
   - 任意レビュー: Fable裁量、1日2回まで。単純な実装確認等で多用しない。
   - 難問診断(L3): Sonnetへ差し戻しても解決しない難問について、1管理ID
     あたり最大1回まで(診断目的のみ)。
```
- 手順8(「8. opus-consultant(L2/L3いずれも)の結果を受け取った後、Sonnetを自動的に再実行しない。実装が必要な場合は人間ユーザーの判断を仰ぐ。」)を次へ置き換え:
```
8. opus-consultantのレビュー結果をそのまま採用しない。Claude案・Opus
   レビュー・`CURRENT_SPEC.md`・`DECISION_LOG.md`・`OPEN_ITEMS.md`・
   ユーザー承認済み内容・QCD・PM強制Gateを照合し、次工程へ進めてよいかを
   PMとして判断する。Opusレビューが入ったという理由だけでユーザー判断
   待ちにしない(Opusレビューは技術品質を上げるためのGateであり、それ
   自体をユーザー承認Gateにはしない)。以下は要約であり、正本は
   `docs/pm/PM_GOVERNANCE.md` 11-3節。
   - 次の全てを満たす場合は、Fable判断で次工程へ進んでよい: Claude案と
     Opusレビューが実質的に一致している/既存のユーザー承認済み仕様の
     範囲内/新しいProduct原則を追加しない/Safety・QCD上の新しい重大
     トレードオフがない/Production正式採用判断ではない/予算・Scope等の
     既存Guardrail内/`USER_DECISION_REQUIRED`に該当する未決事項がない。
   - 次のいずれかに該当する場合は、必ずSTOPしてユーザー判断を求める:
     Claude案とOpusで重要な結論が対立/新しい仕様・Product原則の採用が
     必要/Safety・QCD上の明確なトレードオフが発生/Production正式採用
     判断が必要/既存のユーザー承認内容を変更する必要/予算・Scope・
     運用方針を変更する必要/Opusレビューによって新しい
     `USER_DECISION_REQUIRED`が発生。
   - ユーザーが個別案件で報告・STOPを明示指示している場合は、その指示を
     優先する。
   - 難問診断(L3)の結果を受け取った後は、従来どおりSonnetを自動的に
     再実行せず、実装が必要な場合は人間ユーザーの判断を仰ぐ。
```
- 「上限到達時」節の「Opus診断1回を使い切っても未解決」は**変更しない**(難問診断L3の上限として現行どおり)。

### 3. `.claude/agents/opus-consultant.md`(`name`/`tools`/`model`行は不変)
- frontmatter `description`: 「Sonnetで解決できなかった難問について、原因・選択肢・影響範囲を読み取り専用で診断する。」→「重要な技術設計の独立レビュー、およびSonnetで解決できなかった難問の診断(原因・選択肢・影響範囲)を、読み取り専用で行う。」
- 本文1行目「あなたはFableサンドイッチ方式の難問診断層(Opus)である。」→「あなたはFableサンドイッチ方式の独立技術レビュー・難問診断層(Opus)である。」
- 「## 役割」1項目目を「sandwich-pm(Fable)から渡された重要な技術設計の独立レビュー、または難問について、原因・選択肢・影響範囲・リスク・推奨案を整理する。」へ。
- 「## 診断後」および前回追記の「## 独立技術レビュー」節: Opus自身が実装・修正を開始しない点は不変。前回追記の最終項目「診断・レビュー後に実装を自動開始しない制約も変更しない。」は、「レビュー・診断の後、あなた自身は実装や修正を開始しない。次工程へ進むか・ユーザー判断を仰ぐかは、sandwich-pm(Fable)が`docs/pm/PM_GOVERNANCE.md` 11-3節に従って判断する。」へ整える(「## 診断後」節と重複・矛盾しない形に)。

### 4. `CLAUDE.md`(「Fableサンドイッチ運用(PM層)」節)
- 「- ループ上限: Sonnet委任は1管理IDあたり初回+Fableからの修正・再生成指示最大3回(合計最大4回)、Opusは診断目的で最大1回まで。上限到達時は`USER_DECISION_REQUIRED`としてSTOPする(詳細は`docs/pm/PM_GOVERNANCE.md` 11節)。」のうち、「Opusは診断目的で最大1回まで」を「Opusは、難問診断が1管理IDあたり最大1回まで、任意レビューがFable裁量で1日2回まで(必須のOpus独立技術レビューは回数上限の対象外、次項)」へ置き換える(Sonnet側の記述・STOPの記述は不変)。
- 前回追記した「- Opus独立技術レビューGate(2026-10-02ユーザー決定): …」の項目へ、「必須レビューは回数上限の対象外。同じ内容は重複レビューせず、内容が変われば再レビューする。Opusレビュー後は、Fableが照合のうえ、11-3節のSTOP条件に該当しなければFable判断で次工程へ進む(Opusレビュー自体をユーザー承認Gateにしない)。」を加える(条件・STOP条件の全文は複製しない)。「Opusレビュー後もProduction採用は人間ユーザーだけが承認する」は維持。

### 5. `docs/pm/PM_BRIEF.md`
- 「**Opus Escalation 3段階**」段落(46〜49行付近)の「上限はL2 1回+L3 1回/管理ID」を、「上限(L2 1回+L3 1回/管理ID)は任意レビュー・難問診断にのみ適用し、必須レビューは回数上限の対象外(2026-10-02更新、11-3節)」へ。
- 前回追記したOpus独立技術レビューGateの段落: 競合が未解決である旨の記述があれば解消後の内容へ(回数上限対象外/重複回避・再利用/レビュー後の進行条件・STOP条件は11-3節/任意枠は存続)。
- 「## ループ上限(サンドイッチ運用)」節(192〜200行付近)の「- Opusは診断目的で最大1回まで」「- Opus診断の後、Sonnetを自動的に再実行しない」を、「- Opusの難問診断は1管理IDあたり最大1回まで。診断の後、Sonnetを自動的に再実行しない」「- Opusの必須レビュー(11-3節条件A〜D、11-2節必須)は回数上限の対象外。任意レビューはFable裁量で1日2回まで。レビュー後は11-3節の進行判断(STOP条件に該当しなければFable判断で次工程へ)に従う」へ整える(Sonnetの行・STOPの行は不変)。

### 6. テンプレート
- `docs/pm/templates/OPUS_CONTEXT_PACKET_TEMPLATE.md`の(g)節(前回追記): 「同じ内容の既存Opusレビューの有無(あればファイル名)/再利用するか、再レビューする場合は理由(設計変更/実装方針の重要変更/retry・fallback等への新しい配線/新しい重大リスクの発見/レビュー時の前提が崩れた、のどれか)」の記入欄を追記。
- `docs/pm/templates/OPUS_INDEPENDENT_REVIEW_BLOCK.md`: `---`で囲まれた貼付ブロック本文(Opusへ渡す観点)は**変更しない**。「## 使用上の注意」の「診断後にSonnetを自動再実行しない)は変更しない」という記述を、「Opus自身が実装・修正を開始しない制約は変更しない。レビュー後に次工程へ進むかはFableが11-3節に従って判断する」へ整える。
- `docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.md`: 変更不要の見込み(前回追記の該当判定1行はそのまま有効)。矛盾する記述があれば報告。

### 7. `docs/pm/MODEL_ROUTING_TRIAL_LOG.md`
- L2/L3定義部(L34/L38/L40付近)の回数上限記述: 既存文は残し、前回追記のポインタを「(2026-10-02更新)必須レビュー(PM_GOVERNANCE 11-2必須・11-3条件A〜D)は回数上限の対象外。上限は任意レビュー・難問診断にのみ適用。レビュー後の進行判断は11-3節」へ更新。

### 8. `DECISION_LOG.md`
- 新規エントリ(前回と同じ追記方式・末尾): 「PM-OPUS-INDEPENDENT-TECH-REVIEW-GATE-2026-10-02: 既存ルールとの競合K1〜K6の解消(2026-10-02ユーザー決定、委任_02)」。内容: (1)ユーザー原文の逐語全文、(2)K1〜K6それぞれの解消内容、(3)Fableの解釈1〜3、(4)変更ファイルと、直接置き換えた文の**変更前文言の逐語**(sandwich-pm.md description・手順7・手順8、opus-consultant.md description・本文、CLAUDE.md、PM_BRIEF.md)、(5)変更していないもの(モデル指定、Fable本体の役割、Sonnetループ上限、難問診断L3の上限と診断後の扱い、任意レビュー枠、Production採用はユーザーのみ)、(6)残存競合の確認結果、(7)OPEN-233の扱い(原文§8)。

### 9. `OPEN_ITEMS.md` OPEN-233行
- 前回追記(次Actionセル末尾「…回数上限との関係はユーザー判断待ち」)の後ろへ、「(2026-10-02更新)必須レビューは回数上限の対象外と決定。ユーザー明示指示により、基本線(逐語・複数文のまま・そのまま渡す・戻すための後段処理のみ・範囲を縮小/再解釈しない)での設計+Opus独立レビュー結果が出た時点でユーザーへ報告し、実装・Trialへは進まない」を追記。Statusセル・他列は不変。

### 10. `docs/pm/REPORT_LEDGER.md`
- 本管理IDの行(前回追加)の備考へ委任_02(競合解消の反映)を追記。列構造不変。

### 11. `docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`(`.gitignore`対象、addしない)
- ACTIVE_TASK固定ヘッダ: 管理ID=本管理ID 委任_02、Status=競合解消の反映完了(報告待ち)、UDR-blocking=「OPEN-233: 実記事人間確認の残存1記事(meta_run03_standard)。受け渡し再設計(委任_39)+Opus独立レビューの結果が出た時点でユーザーへ報告、実装・Trialへ進まない」、UDR-deferred=「OPEN-233: 全修正反映後の最終横断確認[≈¥25]の要否、Phase 2新規テーマ選定」、APPROVED未配線=なし、STOP条件=なし、次アクション=「OPEN-233設計案の受領→Opus独立レビュー→Fable整理→ユーザー報告」、未回答報告=なし、報告単位Status=本管理ID 委任_02=報告待ち / OPEN-233=USER_DECISION_REQUIRED(委任_39実行中)。RESULT_PACKETは下記報告項目。

## 事前指定Read一覧

- `docs/pm/PM_GOVERNANCE.md`: 60〜75行、129〜150行(1節)、160〜182行(Gate 2・3)、745〜756行、1596〜1660行(11節)、1879〜2090行(11-2・11-3)、末尾の変更履歴(前回追記位置)
- `.claude/agents/sandwich-pm.md`: 全文(短い。指定3箇所の現行文言を逐語で把握し、DECISION_LOGへ変更前文言として記録するため)
- `.claude/agents/opus-consultant.md`: 全文(46行)
- `CLAUDE.md`: 「Fableサンドイッチ運用(PM層)」節
- `docs/pm/PM_BRIEF.md`: 40〜70行、192〜205行
- `docs/pm/templates/OPUS_CONTEXT_PACKET_TEMPLATE.md`: (g)節(末尾)
- `docs/pm/templates/OPUS_INDEPENDENT_REVIEW_BLOCK.md`: 53〜62行
- `docs/pm/MODEL_ROUTING_TRIAL_LOG.md`: 28〜45行
- `DECISION_LOG.md`: 末尾の前回エントリの見出しと冒頭数行(書式確認)
- `docs/pm/REPORT_LEDGER.md`: 本管理IDの行
- `OPEN_ITEMS.md`: OPEN-233行(列位置の特定のみ、行全体を出力しない)
- `docs/pm/gpt6_trial_preparation_01.md`: 295〜303行(「Opus最大1回」が運用ルールの定義か、個別Trialの計画記述かを確認。個別Trialの計画記述なら編集せず「競合ではない」と報告、ルール定義なら編集せず報告)

## 事前指定Grep一覧+追記位置・更新位置の手順

- 作業後の残存競合確認(必須): リポジトリの`*.md`(`er0*_output/`・`docs/pm/delegation_log/`・`docs/pm/transcripts/`・`DECISION_LOG*.md`・`OPEN_ITEMS*.md`・過去の個別REPORT/レビュー記録を除く運用文書)と`.claude/agents/*.md`に対し、`難問の診断だけ|難問についてのみ|診断目的で最大1回|L2\+L3合計|自動的に再実行しない|自動再実行しない|最大1回|1日2回|未解決の競合|暫定運用` をGrepし、各ヒットが (ア)新ルールと整合 (イ)歴史的記述で注記済み (ウ)未対応の矛盾 のどれかを一覧化する。(ウ)が残る場合は、本委任の指定範囲内なら修正、範囲外なら編集せず報告。
- 追記・更新位置は上記「編集内容」のとおり。

## 実行コマンド全文

作業ディレクトリ `C:\Users\tensh\eigo-radio`。Pythonは `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe`。
1. `git status --porcelain=v1 | grep -v '^??'`(作業前確認。並行タスクは追跡ファイルを変更しない想定。想定外の追跡変更があれば触れずに報告)
2. `git log -1 --format=%B 32661a3a`(前回commitのメッセージ・trailer形式)
3. Read/Grep→編集。
4. T-0: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-02_PM-OPUS-INDEPENDENT-TECH-REVIEW-GATE-2026-10-02_02.md --json-out docs/pm/delegation_log/2026-10-02_PM-OPUS-INDEPENDENT-TECH-REVIEW-GATE-2026-10-02_02.md_check.json`
5. `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m unittest docs.pm.tools.check_delegation_prompt_test_01`(前回13件OK。モジュール指定で失敗する場合は前回と同じ実行方法を使う)
6. 確認: `git diff --stat`、`git diff -- .claude/agents/sandwich-pm.md`、`git diff -- .claude/agents/opus-consultant.md`(`name`/`tools`/`model`行が差分に含まれないこと)、`git status --porcelain=v1 -- .claude/agents/sonnet-worker.md .claude/agents/haiku-worker.md CURRENT_SPEC.md`(未変更)。
7. 残存競合Grep(上記)。
8. Git(下記)。

## SSOT追記文

上記「編集内容」1・8・9・10のとおり(`PM_GOVERNANCE.md`・`DECISION_LOG.md`・`OPEN_ITEMS.md`[OPEN-233行の追記のみ]・`docs/pm/REPORT_LEDGER.md`)。新しいOpen Itemは起票しない。

## Git(明示add対象・コミットメッセージ・trailer)

- SSOT編集権: **あり**(`PM_GOVERNANCE.md`・`DECISION_LOG.md`・`OPEN_ITEMS.md`[OPEN-233行のみ]・`docs/pm/REPORT_LEDGER.md`)。`CURRENT_SPEC.md`は編集しない。並行タスクはSSOTを編集しないため直列化上の衝突なし。
- 明示`git add`対象(実際に変更したもののみ、1ファイルずつ): `docs/pm/PM_GOVERNANCE.md` / `DECISION_LOG.md` / `OPEN_ITEMS.md` / `docs/pm/REPORT_LEDGER.md` / `docs/pm/PM_BRIEF.md` / `CLAUDE.md` / `docs/pm/MODEL_ROUTING_TRIAL_LOG.md` / `docs/pm/templates/OPUS_CONTEXT_PACKET_TEMPLATE.md` / `docs/pm/templates/OPUS_INDEPENDENT_REVIEW_BLOCK.md` / `.claude/agents/sandwich-pm.md` / `.claude/agents/opus-consultant.md` / `docs/pm/delegation_log/2026-10-02_PM-OPUS-INDEPENDENT-TECH-REVIEW-GATE-2026-10-02_02.md`
- コミットメッセージ: `PM-OPUS-INDEPENDENT-TECH-REVIEW-GATE-2026-10-02: 競合K1〜K6を解消(必須レビューは回数上限対象外、重複レビュー回避、レビュー後の進行/STOP条件、Fable・Opus説明文の整合)。モデル指定は不変(委任_02)`
- trailer: 手順2の形式に合わせる。commit後 `git push origin main`。エラー・競合が出たらSTOPして報告。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`と最終メッセージに次を記載:
1. 変更ファイル一覧(ファイルごとの変更箇所・行範囲)。
2. ユーザー決定5項目(§1〜§5)+§6それぞれを、どのファイルのどの記述で解消したか。
3. **`git diff -- .claude/agents/sandwich-pm.md` と `git diff -- .claude/agents/opus-consultant.md` の出力を逐語で**(Fableが照合する。省略しない)。
4. 11-3節の新設・書き換え段落(回数上限の扱い/重複レビューの回避/Opusレビュー後の進行判断/Fableの役割/競合の解消)の**逐語全文**(省略しない)。
5. 新旧ルール間に残る競合の有無(残存競合Grepの(ア)(イ)(ウ)一覧。(ウ)が0件か、残るなら所在と理由)。`gpt6_trial_preparation_01.md`の判定。
6. 実際にどの条件でユーザーSTOPになるか(STOP条件7つ+従来から残るSTOP[難問診断L3後、Sonnetループ上限到達、Production採用、ユーザーの個別明示指示]の整理)。
7. Fableの解釈1〜3をどこに書いたか。
8. モデル指定・`sonnet-worker.md`・`haiku-worker.md`・`CURRENT_SPEC.md`未変更の確認(コマンド6の出力)。
9. T-0検証結果、手順5のテスト結果。
10. commitハッシュ・push結果、`git show --stat HEAD`の対象ファイル一覧、変更ファイルのraw.githubusercontent.com URL一覧。
11. 迷った点・指示どおりにできなかった点・一覧外の追加Read。

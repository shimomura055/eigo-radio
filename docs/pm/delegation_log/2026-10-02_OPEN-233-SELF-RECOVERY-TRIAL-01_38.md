## 管理ID

`OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_38: **現行設計の説明のみ**。read-only調査+説明文書の作成。コード変更・Trial実行・API課金なし、¥0)。並行タスクなし(他Agentは起動していない)。

## 性質/到達上限Status/禁止事項

- 性質: 調査・説明。ユーザーが構造是正(Stage1の文ID・文字オフセット出力等)の要否を判断する前に、**現行の構造を実コード・実データに基づいて正確に説明する**ことだけが目的。
- 到達上限Status: `USER_DECISION_REQUIRED`のまま据え置き(変更しない)。VALIDATED等への変更なし。
- 禁止事項:
  - 文ID方式・文字オフセット方式を**実装しない**。設計変更・コード変更・Prompt変更・テスト追加を一切しない(`*.py`・Promptファイルは読むだけ)。
  - **新しいTrialを回さない**。API呼び出し・TTS・Web Search一切なし(費用¥0。費用上限[Cap]を伴わないためT-3は非該当)。既存の出力(`er052_output/`配下)を読むだけ。
  - **Production正式pathを変更しない**。
  - SSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`HISTORY_INDEX.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/PM_GOVERNANCE.md`)・`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`・設計書`docs/pm/design_open233_self_recovery_flow_01.md`を編集しない(SSOT編集権なし)。
  - 是正案の推奨・設計提案を説明本文へ混ぜない(ユーザーは「説明を見てから判断する」と明言している。是正案に触れる場合は末尾の「参考」に1〜3行で留め、推奨はしない)。
  - 推測を事実として書かない。コード・実データで確認した事項と、推測・未確認の事項を必ず書き分ける。実データの引用は実ファイルからの逐語コピーとし、創作・要約による「それらしい例」を実データとして示さない。
  - `git add -A`/`stash`/`amend`/force push禁止。未commitの既存変更(`er0XX_output/`配下のtelemetry等11件、`docs/pm/delegation_log/2026-10-01_PM-CRASH-DATA-INTEGRITY-CHECK-01*`3件ほか未追跡ファイル)には触れない・addしない。

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
(本委任はTTSを伴わない。T-1・T-3は非該当。T-0の保存は**要約せず本委任文の全文**を保存すること[前回別件で要約保存によりFAILした]。)

## ユーザー指示(原文)

> OPEN-233 / meta_run03_standard の残存問題について、構造修正へ進む前に、まず現行設計を分かりやすく説明してください。
>
> 今回ユーザーが理解できていないのは次の点です。
>
> Checkerが、
> - この文章が違反
> - 理由はこれ
> と判定しているのであれば、その**違反した文章そのもの**をRewrite側へ渡して、
> 「この文章をこの理由で修正してください」
> とすればよいように見えます。
>
> それにもかかわらず、なぜ後段で、
> - 元記事のどこかを再探索する
> - 文IDや文字オフセットが必要になる
> - Rewrite対象の特定に失敗してStage 4へ行く
> という構造になっているのかが分かりません。
>
> 以下だけを、まず簡潔かつ具体的に説明してください。
>
> 1. CheckerがNG判定した時点で、実際に何を出力しているのか
>    - 違反文そのもの
>    - 違反部分だけ
>    - 複数文をまとめたclaim
>    - 理由
>    - rewrite hint
>    など、実データの形を示してください。
>
> 2. その出力を、なぜそのままRewrite Promptへ渡せないのか。
>
> 3. Rewrite前に「元記事のどこか」を再特定する必要がある理由は何か。
>
> 4. 問題が、
>    - 違反対象が1文とは限らず範囲を持つからなのか
>    - Checkerが元文をそのまま返さず要約・結合して返すからなのか
>    - JA/EN両方の対応箇所を特定する必要があるからなのか
>    - その他の実装上の理由なのか
>    を切り分けてください。
>
> 5. meta_run03_standard の実例を1件だけ使って、
>    「元記事」
>    →「Checker出力」
>    →「Rewrite側へ渡しているもの」
>    →「どこで特定失敗するか」
>    をBefore/Afterではなく処理順で示してください。
>
> 重要:
> - ここではまだ文ID・文字オフセット方式を実装しないでください。
> - 新しいTrialも回さないでください。
> - まず現行構造と、なぜ違反文そのものをそのままRewrite対象として使えないのかを説明してください。
> - その説明を見てから、構造是正の要否を判断します。
>
> StatusはUSER_DECISION_REQUIREDのままです。
> Production正式pathは変更しないでください。

## 事前指定Read一覧

(行番号は見出しGrepで得た開始位置。各節の必要範囲だけ読む。)
- `docs/pm/design_open233_self_recovery_flow_01.md`
  - §3-0 全体像(387行〜)・§3-1 Stage 1: Initial Check(444行〜531行): Stage 1(Checker)の出力形式
  - §3-3 Stage 3(544行〜)・§5-2 局所Rewrite EN側(1725行〜)・§5-4 paired local rewrite JA側(1833行〜): Rewriteへ渡す入力と、書き換え結果を記事へ戻す方法
  - §5-9 precheck合成マーカーの実文解決(2198行〜)
  - §6-14(3118行〜)・§6-15(3171行〜)・§6-16(3219行〜)・§6-17(3293行〜3395行): meta_run03_standardの原因分析の経緯(Stage1 enumeration非決定性、原因(d)、claim_textの複数引用断片結合、変種(e))
- `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`: `^## .*3[1-4]` 等でGrepして§31〜§34の位置を特定し、meta_run03_standardの実例・変種の記述箇所のみ読む
- `er052_open233_self_recovery_flow_runner_01.py`: 下記GrepでRewrite対象特定(locate)と Rewrite Prompt組み立て・記事への書き戻し箇所を特定し、その関数範囲のみ読む
- Stage 1(Checker)のPrompt/出力schemaの定義箇所(runnerのGrep結果からたどる。Production側fact checkのschemaを流用している場合はその定義箇所のみ)
- `er052_output/open233_self_recovery_flow_runner_01_rep19/`・`_rep20/`・`_rep21/` 配下のうち、meta_run03_standardの**Stage4になったrunを1件**選び、そのrunの (i) 元記事EN/JAの該当箇所、(ii) Stage 1出力の該当claimレコード(生のJSON)、(iii) Rewrite入力として記録されているもの、(iv) 失敗理由の記録(`ladder_exhausted_without_full_rewrite`/`cycle_limit_exhausted`等)だけを読む。ディレクトリ全体・大きなログの全文Readは不可(Glob/Grepで対象ファイルと行を絞る)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- `er052_open233_self_recovery_flow_runner_01.py` に対し: `def locate_target|def extract_all_quoted_fragments|def locate_multi_quote_span|claim_text|rewrite_hint|def .*rewrite|\.replace\(|cycle_limit_exhausted|ladder_exhausted_without_full_rewrite|iol_degenerate`
- 設計書・REPORTに対し: `claim_text|locate|meta_run03_standard|変種\(e\)|文字オフセット`
- `er052_output/open233_self_recovery_flow_runner_01_rep2[01]/` と `_rep19/` に対し: `meta_run03_standard|STAGE4|cycle_limit_exhausted|ladder_exhausted`(files_with_matchesで対象ファイルを特定してから該当行のみ読む)
- 追記・更新位置:
  - 説明本文: 新規ファイル `docs/pm/explain_open233_checker_to_rewrite_target_01.md` を作成
  - `docs/pm/RESULT_PACKET.md`: 上書き(委任_38の要約。下記「報告」参照)
  - `docs/pm/ACTIVE_TASK.md`: 固定ヘッダの「管理ID」行を委任_38(現行設計の説明のみ、¥0、コード変更・Trialなし)へ、「報告単位Status」を「委任_38=報告待ち」へ、「次アクション」を「説明を見たうえでユーザーが構造是正の要否を判断」へ更新。**Status行は`USER_DECISION_REQUIRED`のまま、UDR-blocking/UDR-deferred/APPROVED未配線の内容は変えない**。完了サマリ節は委任_38の内容へ差し替え。
  - 委任文: `docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_38.md` へ全文保存

## 実行コマンド全文

作業ディレクトリ `C:\Users\tensh\eigo-radio`。
1. 上記Read/Grep(read-only)。
2. `git log -1 --format=%B 5d4fa8ff`(直前commitのメッセージ・trailer形式の確認)
3. T-0: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_38.md --json-out docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_38.md_check.json`
4. `git status --porcelain=v1 -- docs/pm/ACTIVE_TASK.md docs/pm/RESULT_PACKET.md docs/pm/explain_open233_checker_to_rewrite_target_01.md docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_38.md`(add対象の確認)
5. Git(下記)。
回帰テスト・runner・Trialスクリプトは実行しない。

## 説明文書の要件(`docs/pm/explain_open233_checker_to_rewrite_target_01.md`)

読み手はプロジェクト責任者(実装担当者ではない)。日本語、簡潔・具体的に。技術用語は初出時に短い日本語説明を付ける。内部の関数名・フィールド名は実データを示す箇所でのみ使い、地の文では平易な言葉で言い換える。構成はユーザーの質問1〜5にそのまま対応させる(見出しも1〜5)。

1. **Checker(Stage 1)がNG判定時に実際に出力しているもの**: 実データの1レコードを生のJSONのまま逐語で示す(出典ファイルパス付き)。各フィールドが何か(違反文そのもの/違反部分だけ/複数文をまとめたclaim/理由/rewrite hint/位置情報の有無)を1行ずつ。特に「記事本文の文を一字一句そのまま返す保証があるか」「位置情報(何文目・何文字目)を返しているか」を、Prompt/schemaの記述を根拠に明記する。
2. **その出力をなぜそのままRewrite Promptへ渡せないのか**: まず事実として「現行でRewrite Promptへ実際に渡しているもの」をコードで確認して示す。そのうえで「Checker出力の文字列をそのまま渡すだけでは足りない理由」を、コード上の根拠付きで書く。もし調査の結果「実はそのまま渡すこと自体は可能で、困るのは別の工程(例: 書き換え結果を記事へ戻す工程)である」等、ユーザーの見立てが部分的に正しいと分かった場合は、その通り率直に書く(現行設計を擁護する方向へ寄せない)。
3. **Rewrite前に元記事の場所を再特定する必要がある理由**: 書き換え後の文を記事のどこへ戻すか/局所Rewriteの単位(文・段落)の決定/JA側の対応箇所の決定/書き換え後の局所QA、等のうち、コード上で実際に位置を使っている工程を全て列挙し、それぞれ「位置が無いと何ができないか」を1行で。
4. **原因の切り分け**: ユーザーが挙げた4候補(a)違反対象が範囲を持つ (b)Checkerが元文をそのまま返さず要約・結合して返す (c)JA/EN両方の対応箇所の特定が必要 (d)その他の実装上の理由、それぞれについて「該当する/しない/部分的」と根拠(コード箇所・実データ・設計書の節番号)を表で示す。meta_run03_standardの残存失敗(固定Stage1入力でも4 run中2 runがStage4、毎回別変種)に対して、どれが主因でどれが副因かを、確認済みの範囲で示す。「毎回別変種」とは具体的に何が毎回違うのか(どの工程のLLM出力が揺れているのか)も明記する。
5. **meta_run03_standardの実例1件を処理順で**: 「元記事(EN/JAの該当箇所を逐語)」→「Checker出力(生レコード逐語)」→「Rewrite側へ渡しているもの(逐語、記録がある範囲)」→「どこで特定失敗するか(どの工程が、何と何を突き合わせて、なぜ一致しなかったか)」→「結果(Stage 4、fail-closed=安全側に倒して人間確認へ回した、の意味)」。各段に出典ファイルパスを付ける。該当データが記録に残っていない段は「記録なし」と明記し、創作で埋めない。
末尾に「確認済み/未確認の区別」(コード・実データで確認した事項と、推測に留まる事項)を短く。

## SSOT追記文

なし(SSOTは編集しない。Statusは変わらないため`OPEN_ITEMS.md`の更新も不要)。

## Git(明示add対象・コミットメッセージ・trailer)

- SSOT編集権: **なし**。
- 明示`git add`対象(これ以外はaddしない):
  - `docs/pm/explain_open233_checker_to_rewrite_target_01.md`
  - `docs/pm/RESULT_PACKET.md`
  - `docs/pm/ACTIVE_TASK.md`
  - `docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_38.md`
  (`_check.json`は、委任_37までの既存パターンで追跡されていなければaddしない)
- コミットメッセージ: `OPEN-233-SELF-RECOVERY-TRIAL-01: 現行設計の説明(Checker出力→Rewrite対象特定の構造、meta_run03_standard実例)、コード変更・Trialなし(委任_38)`
- trailer: 手順2で確認した直前commit(5d4fa8ff)の形式に合わせる。
- commit後 `git push origin main`。エラー・競合が出たら自分で解決せずSTOPして報告。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`(上書き)と最終メッセージに次を記載:
1. 管理ID・委任番号・Status(USER_DECISION_REQUIREDのまま)・費用¥0
2. 質問1〜5それぞれへの答えの要約(各2〜5行)。**最終メッセージには説明文書の質問5(実例の処理順)を逐語データ込みで全文含めること**(Fableが内容を照合するため)
3. ユーザーの見立て(「違反文そのものを渡せばよいのでは」)が、調査の結果どの程度正しかったか(正しい部分/現行構造上成り立たない部分)を率直に
4. 確認済み事項と未確認・推測事項の区別
5. 読んだファイルと該当行範囲の一覧、一覧外の追加Readがあればその理由
6. T-0検証結果(PASS/FAIL・reasons)1行
7. commitハッシュ・push結果、変更ファイルのraw.githubusercontent.com URL
8. コード・Prompt・SSOT・Production pathを変更していないことの確認(`git show --stat HEAD`の対象ファイル一覧)

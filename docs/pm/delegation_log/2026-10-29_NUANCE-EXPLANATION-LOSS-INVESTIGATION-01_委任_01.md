Fableからの委任_01(管理ID: NUANCE-EXPLANATION-LOSS-INVESTIGATION-01。調査専用、API 0、Productionコード/Prompt/SSOT編集禁止、既存解説データの変更・削除禁止)。

## 0. 最初に
- 本プロンプト全文を `docs/pm/delegation_log/2026-10-29_NUANCE-EXPLANATION-LOSS-INVESTIGATION-01_委任_01.md` に逐語保存(Bash heredoc、端末に再表示しない)。ユーザー原文は並行Worker(K)が `docs/pm/delegation_log/2026-10-29_FX-AI-ISLAND-FINAL-PUBLISH-01_USER.md` に保存中(数分後に読めるはず。§2〜§5Bが本件の正本。読めない間は本プロンプト§1の要約で着手し、読めたら原文で再確認)。
- `tools/stop_scope_check_01.py --managed-id NUANCE-EXPLANATION-LOSS-INVESTIGATION-01 --out docs/research/NUANCE-EXPLANATION-LOSS-INVESTIGATION-01/stop_check_01.json`(rc=3で停止)。
- 並行Worker: (I)JA-ASR設計、(K)AI島公開。自分は `docs/research/NUANCE-EXPLANATION-LOSS-INVESTIGATION-01/`、`docs/pm/RESULT_PACKET_NUX1.md`、ACTIVE_TASKの自分の行だけ編集。ACTIVE_TASKの(K)行の直後に `(L)NUANCE-EXPLANATION-LOSS-INVESTIGATION-01=ユーザー2026-10-29: 「ニュアンス解説」がいつ・なぜ消えたかの原因調査(API 0、調査のみ)。委任_01。` を追加(編集直前Re-Read、index.lock衝突は数秒待って再試行)。

## 1. 目的(ユーザー原文の要約。原文が正本)
以前、解説コーナーに「ニュアンス解説」が存在したが現在見当たらない。①過去の仕様・実装(どのFamily/Levelのどの解説コーナーに、何を生成・表示していたか。**過去の実際の解説文面を1〜2例**)、②変更の経緯(いつ・どのcommit・委任で消えたか/ユーザー承認による廃止か/別解説へ統合か/Prompt変更で生成されなくなったか/データにはあるが表示されなくなったか/意図しない欠落か)、③現行仕様(①Key Phrase ②追加解説 ③本文意味表示 Part2文法・構文解説の各役割、ニュアンス内容が現在どこかに残っているか、AI島Std/Advの実データと公開ページ、X/Y/Z共通か固有か)、④原因・責任範囲(明示的仕様変更/承認済み仕様の配線漏れ/後続変更のRegression/仕様と表示の不整合)。**ユーザーが廃止を承認した証拠がない場合「仕様変更済み」と解釈しない。原因不明は推測で埋めず「未特定」と明記。** 新解説仕様を作らない。

## 2. 方法
- `git log -S "ニュアンス" --oneline --all`(件数多ければ`-- <paths>`で絞る)、`git log -S "nuance" -i`、`CURRENT_SPEC.md`/`DECISION_LOG.md`/`DECISION_LOG_HISTORY.md`/`OPEN_ITEMS.md`/`OPEN_ITEMS_HISTORY.md`/`HISTORY_INDEX.md`/`ER-*_REPORT.md`/`docs/research/**`/Prompt(er0XX内のprompt文字列・`prompts/`)/`user_test/**/index.html`/生成json(kp・comment・解説データ)を「ニュアンス」「nuance」でGrep(head_limit付き、全文読込禁止)。
- 旧公開ページ/旧Trial出力に残る実文面を1〜2例、file:line(またはcommit:path:line)で逐語引用。
- 消えた時点をcommit bisect的に特定(`git log -p -S`の該当hunk、委任文=`docs/pm/delegation_log/`、DECISION_LOG/UDRの承認記録)。承認記録の有無を明記。
- 現行: X/Y/ZのKP解説(意味/追加解説/本文中の意味)・Part2文法解説の生成コードとページ生成経路(file:line)を整理し、ニュアンス相当の項目があるか判定。AI島Std/Adv(`user_test/family_x_ai_island_form_01_candidate_b7_01/`と元run `er019_output/.../ai_island_temple__run_form_prod_01/`)の実データを確認。
- **早期フラグ**: AI島の公開データについて「承認証拠のある承認済み仕様がAI島公開データで欠落している」かを判定した時点で、`docs/pm/RESULT_PACKET_NUX1.md`の1行目に `AI島重大欠落=あり|なし|未特定(理由)` を先に書く(並行(K)が公開commit直前に読む。確定できるまでは `未特定(調査中)` を置く)。

## 3. 成果物
`docs/research/NUANCE-EXPLANATION-LOSS-INVESTIGATION-01/INVESTIGATION_01.md`: 見出しはユーザー原文§5Bの1〜8(1結論/2過去の実例/3変更前後の仕様・Prompt・表示比較/4廃止承認の有無と証拠/5現行のどこに相当するか/6 X/Y/Z・Std/Adv影響/7必要な是正案とQCD影響[実装はしない]/8ユーザー判断が必要な事項=挙証付き`判断候補`)。根拠はfile:line・commit。
是正は本委任では実装しない(11-8判定はFable)。ただし明白な不具合で修正1行以下・影響局所なら提案として書く。

## 4. 範囲(11-8)
範囲内=履歴・コード・データの調査、是正案の提示。範囲外=新解説仕様、Prompt変更、Validator/Gate追加、既存解説の変更・削除、Family A/B/Cの開発(A/B/Cの過去実装が起源なら事実として記録するのみ)。

## 5. 報告
`docs/pm/RESULT_PACKET_NUX1.md`(1行目=早期フラグ、以下: 整合/未承認機能/成果物と目的適合/撤去・残置/判断候補(停止根拠file:line)/費用0/commit)。`判定整合:`行を末尾。commit: `docs/research/NUANCE-EXPLANATION-LOSS-INVESTIGATION-01/`と委任文・ACTIVE_TASKのみ明示`git add`→`git push origin HEAD:main`。最終回答は短く(結論1〜3行・成果物パス・commit・判断候補のみ)。

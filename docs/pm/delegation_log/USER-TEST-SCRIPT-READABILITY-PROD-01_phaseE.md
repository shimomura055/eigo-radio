# Delegation: USER-TEST-SCRIPT-READABILITY-PROD-01 Phase E (統合 USER-TEST-HOSTING-GITHUB-PAGES-01)

## 管理ID

USER-TEST-SCRIPT-READABILITY-PROD-01 / Phase E(最終公開工程)= USER-TEST-HOSTING-GITHUB-PAGES-01(rawcdn.githack → GitHub Pages切替)との統合。並行Agentなし(Phase A/B1/B2/C/D/Pages-Precheckは全て完了、Fable確認済み)。音声stageなし(lock不要。`docs/pm/locks/audio_stage.lock`が存在していたらSTOPして報告)。`docs/pm/ACTIVE_TASK.md`の固定ヘッダ+要約をPhase E内容で更新してから開始。

## 性質/到達上限Status/禁止事項

- 性質: Production wiring(両管理IDともユーザー`APPROVED_FOR_PRODUCTION`済み)。到達してよい最大Status: 両IDとも`PRODUCTION_WIRED`。ただし下記「PRODUCTION_WIRED判定条件」を全て満たした場合のみ。1つでも未達なら`USER_DECISION_REQUIRED`(または`STOPPED`)として理由を報告し、SSOTには「未配線」として事実のみ記録する(`PRODUCTION_WIRED`と書かない)。
- 禁止: canonical article本文・player・audio・Key Phrase asset・translation asset・`user_test/unified.html`の変更禁止(Hosting migrationによる内容変更禁止。unified.htmlに不具合が見つかった場合は修正せずSTOPして報告)。`user_test/articles_2026_0918.html`は20 `href`以外変更禁止。TSVはURL列2本以外変更禁止。別hostingへの変更禁止(GitHub Pages以外を試さない)。GitHubリポジトリ設定の変更は本環境から不可(`gh`/token無し、Precheck確認済み)。外部API支出禁止(¥0)。`git add -A`/`stash`/`amend`/`rebase`/`force push`禁止。mp3/wav追加禁止。
- STOP条件(該当時は該当時点までの成果をcommitし、RESULT_PACKETに原因整理を書いて終了。複数案を試し続けない): (1)GitHub Pages上でSeekがFAIL、(2)Pages上でaudio再生不可、(3)path/CORS/MIME問題を安全に解消できない、(4)rawgit.hack警告(「One more step」「Open the page」等)が正式経路に残る、(5)Pages deployが15分以内に反映されない、(6)Landing/TSV/個別URLの整合不能、(7)canonical変更が必要、(8)新Product判断が必要、(9)`unified.html`の修正が必要。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
(本委任の保存先: `docs/pm/delegation_log/USER-TEST-SCRIPT-READABILITY-PROD-01_phaseE.md`)

## ユーザー指示(原文)

[SCRIPT-READABILITY追加判断 2026-09-18]「1. Free-Address A2のREVIEW_REQUIRED 2件: 以下2件はユーザー承認済みとして採用する。a place of one's own(本文対応: "a place of my own")、change one's surroundings(本文対応: "changing my surroundings")。Key Phraseは学習用一般形を維持し、本文側では実際の出現形を水色ハイライトする。本文・本文音声・Comment・タイトル・構成は変更しない。これにより本件のUSER_DECISION_REQUIREDは解消。」「2. mapping分類修正: exact=文字列として実出現形と一致 / non-exact=時制・活用・人称一般化等により表層形が異なるが、source対応が一意に確認できるもの / unresolved=対応不能・曖昧。最終報告では20 level全件について正しく再集計すること。unresolved最終目標=0。」「3. GitHub PagesへのProduction公開切替: ユーザーはrawgit.hack確認画面を避けるため、正式ユーザーテスト公開経路をGitHub Pagesへ切り替えることをすでにAPPROVED_FOR_PRODUCTIONとして承認済み。rawcdnを最終Production runtime evidenceとしてcloseしないこと。GitHub Pages側でSeekがFAILする場合はPRODUCTION_WIREDにせずSTOPして報告。」「5. 再発防止案 (a)本文変更後、Key Phrase source_span実在確認Gate (b)他記事Key Phrase流用時、供給元本文sha256一致Gate は有力だが、まだProduction実装しない。最終報告でUSER_DECISION_REQUIRED候補として改めて提示。ユーザー承認なしに恒久Production仕様へ追加しない。」
[USER-TEST-HOSTING-GITHUB-PAGES-01 2026-09-18 抜粋]「目的: ユーザーテスト用Webページを rawcdn.githack.com 配信からGitHub Pagesへ正式移行。理由: 実ユーザーがリンクを開いた際に rawgit.hack の『One more step』確認画面が表示されるため。」「URLは推測で確定しない。実際にGitHub Pages公開後、ブラウザruntimeで到達確認したURLのみ正式採用する。」「GitHub Pages移行後は: rawgit.hackの警告ページが出ない/一覧ページが直接開く/Standard・Advancedボタンから直接記事へ遷移/記事ページも警告画面なし/音声再生可能/Seek正常/JS・CSS・JSON・audio assetが正しくロード/PC正常/mobile正常。」「URLの切替範囲: A. user_test/articles_2026_0918.html内の20リンク B. TSV内の20 URL C. CURRENT_SPEC/DECISION_LOG/ARTIFACT_REGISTRY内の正式ユーザーテスト公開URL。rawcdn.githack.com のURLを正式Production URLとして残さない。過去証跡としてDecision Log等に旧URLを記録するのは可。」「実ユーザーへ送る正式入口URLを1本確定する。最終報告では必ず『今後メール・LINEで共有する正式URL』として明記。」「固定SHA依存の整理: GitHub Pages移行後は、ユーザーテスト入口URLをcommitごとに変更しなくてよいstable URLにする。これを正式仕様として採用できるかruntime確認後にSSOTへ記録する。」「rawgit警告回避確認: GitHub Pages正式URLを新規セッション相当で開き、『One more step』『Open the page』等の確認画面が表示されないことを確認。単なるHTTP 200のみでは不可。」「GitHub Pages設定: 必要なGitHub Pages設定を実施。Repo設定変更がClaude環境から実行不能なら、勝手に別hostingへ変更しない。USER_DECISION_REQUIREDでSTOPし、ユーザーがGitHub UIで行う必要がある操作だけ最小手順で提示。」「Dangling Reference Check: Production HTMLにrawcdn.githack.com参照が残っていない(正式ユーザーテスト経路について)/rawgit.hack依存なし/Trial path参照なし/old fixed SHA URLがLanding hrefに残っていない/TSV旧URLなし/asset参照がGitHub Pagesで解決/retry・fallback等が存在する場合も同様。」

## 事前指定Read一覧

1. `docs/pm/RESULT_PACKET_SCRIPT_READABILITY_PROD_01_pages_precheck.md` 全文
2. `docs/pm/RESULT_PACKET_SCRIPT_READABILITY_PROD_01.md` L388-638(Phase C節)、L158-387のうちitem 4/11/15(Phase D)
3. `docs/user_test/ユーザーテスト記事一覧_2026-0918_選定10.tsv` 全文、`user_test/articles_2026_0918.html`: Grep `href=` → 20本
4. `docs/pm/tools/user_test_readability_check.py`: Grep `def |add_argument`、`docs/pm/tools/landing_page_e2e_check.py`: 同様
5. `er012_output/editorial_b_family_voices_a2_production_wiring_01/kp_fix_01/a2/key_phrases/keywords_canonicalized.json`: Grep `qa_overall_status`
6. SSOT追記位置の特定(全文Read禁止、Grepのみ)
7. `docs/pm/PM_GOVERNANCE.md` Grep `9-5|raw URL|blob URL|rawcdn`

(以下、詳細な事前指定Grep一覧・実行コマンド全文・Git明示add対象・報告項目は本タスクの委任元(sandwich-pm/Fable)からのメッセージ本文に記載の通り。全文は本セッションのタスク指示メッセージを参照。)

# 委任_01 (FX-PAYCHECK-PERSONALITY-FINAL-PUBLISH-01、2026-10-29、Fable→Sonnet、API 0) 逐語保存
Fableからの委任_01(管理ID: FX-PAYCHECK-PERSONALITY-FINAL-PUBLISH-01。記事「給料が上がると、性格も変わる？」(Paycheck Personality)のStd/Adv記事単位正式公開・検証・SSOT/Git。API 0=再生成なし)。

## 0. 最初に
(a) USER原文ファイル作成(5行逐語)。(b) 本プロンプト全文を本ファイルへ逐語保存。(c) stop_scope_check(rc=3で停止)。(d) ACTIVE_TASK(M)行直後に(N)行追加。並行Worker: (I)JA-ASR配線、(M)Family Y統合。自分のSSOT編集は該当行の最小Editのみ、index.lock衝突は数秒待って再試行。

## 1. やること
1. 承認対象の特定: OPEN-432/OPEN-442(Grep)、UDR #144、該当run(run_pp_02等)と試聴候補ページ(user_test/配下)を特定し、Std/Adv音声・index.htmlのsha256を記録。候補が複数ある場合は#144/OPEN-442で提示したページを採用し他は採用しない(不明なら`判断候補`で停止)。
2. 公開手順: 前例(AI島 docs/research/FX-AI-ISLAND-FINAL-PUBLISH-01/PUBLISH_EVIDENCE_01.md、Word Gacha、CURRENT_SPEC.md:3187、B7_PUBLISHED_ARTICLES_01.md)に従い、候補ページを正式パスへ同一内容で配置(候補は前例どおり残す)。
3. 検証: 公開URL全asset HTTP 200・Content-Length>0・repoとbyte一致(live_verify json)、ローカルpage_verify(Playwright、音声全件再生・console error 0・4xx 0)、解説表示(KP/Preview/Comment/Part2)のhtml Grep。
4. SSOT: OPEN-432/OPEN-442行末に公開済み・CLOSED追記、UDR #144に判断済み追記、DECISION_LOG.md 1エントリ、B7_PUBLISHED_ARTICLES_01.md等の公開記事一覧があれば追記(無ければ作らない)、ACTIVE_TASK(N)行更新。
5. docs/research/FX-PAYCHECK-PERSONALITY-FINAL-PUBLISH-01/PUBLISH_EVIDENCE_01.md(URL・sha・HTTP結果・手順根拠file:line)+live_verify_01.json。
6. commit(編集ファイルのみ明示git add)→git push origin HEAD:main(FF)→Pages反映確認(最大15分)。

## 2. 範囲(11-8)
範囲内=承認済み公開手順の実行・検証・記録。範囲外=音声/本文/解説の再生成・変更、Prompt変更、新Gate、Family A/B/C。手順不明・候補不一致は`判断候補`(停止根拠file:line)で報告し独自手順で公開しない。

## 3. 報告
docs/pm/RESULT_PACKET_FXPP1.md: 整合/未承認機能/成果物(URL・sha)と目的適合/撤去・残置/判断候補/費用0/commit。`判定整合:`行。最終回答は短く(URL・検証結果・commit・判断候補)。
(注: 本ファイルは委任文の要約再構成を含む。完全原文は呼出元transcriptにあり、上記各項の指示内容は省略なく保持。)

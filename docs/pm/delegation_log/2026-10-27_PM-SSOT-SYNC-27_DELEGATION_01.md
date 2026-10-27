## 管理ID

PM-SSOT-SYNC-27(SSOT同期: SLOT-23 ①②③表示仕様の6経路Fable受入判定の記録、フォーム送信・コピー改善のFable受入(ユーザー実機確認済み)、SLOT-23委任_06F(62663d4e9)/07G(c43917f00)、AIF委任_06(50efa99cd)反映。API 0)。あなたが唯一のSSOT編集権者。並行Agent: なし。全文読込禁止(Grep)。pathspec付きcommit、`git push origin HEAD:main`。時間見込み約45分。

## Fable判定(記録する内容。判定し直さない)

1. **SLOT-23(OPEN-562)学習項目①②③表示仕様(Std②=①と同等の日本語詳細解説[Part 1=①+②]、①太字+二重下線/②太字+下線/③下線+短い訳、遡及なし)= PRODUCTION_WIRED(X/Y/Z×Std/Adv 6経路、Fable受入2026-10-27)**。根拠: 配線A〜E+M(commit 22f3a09ef/374cfc941/e2feca7ab/331474a9f/f03f12c2e/1684e19f5)、runtime evidence=委任_06F(Y/Z Std/Adv: 正式runnerで`new_review`→マーク自動付与→display_spec→Std Part 1→装飾→G3・check_page PASS、確定cmp同一、pages再実行sha同一、実ブラウザ1280/375/390で①double・②③solid計測)+委任_07G(X Std/Adv: D-F1是正後に標準公開builderで同上PASS)。受入条件14(USER.md §6)との対応=`ROUTE_STATUS_06.md`+`EVIDENCE_RESULT_07.md`。**限界(明記)**: evidenceはDEV複製run(既存run+review差替え、regenerate連鎖あり)で、実記事での初回発火はAI島(HR承認後の再ビルド)が最初になる/dev `⏸`と装飾の共存はX実runで観測・Yはtestで固定/D-F1(`er120 public_study_html`のPart 1 b1b限定)はF班evidenceで検出し07Gで是正(X全99 runでb1b同一・a2はdisplay_spec付き2件のみ変化)。
2. **フォーム送信・コピー改善(USER_03 §B、OPEN-545)= PRODUCTION_WIRED**(Fable受入2026-10-27)。根拠: 委任_07/07R/08(実装・復元tool・小修正)、自動検証(node/py/headless/往復)、猿の手Advテスト送信の照合全欄一致(委任_09)、**ユーザー実機確認「問題ありません」(2026-10-27、本セッション)**。
3. OPEN-561(AI島): 新表示仕様の適用準備完了(AIF6: reconsume両level・Std Part 1生成¥0.42・解決ISSUE 0、D-F1是正済み)、残=HR(hr_02 Q1)承認→`record_human_approval`→assemble→player→標準builder→公開(API 0、PREP_06.md)。
4. 違反・逸脱記録(F班): (a)X複製runでStd Full Story chunk 9呼出を再生成(≈¥3.9、DEV複製run内のみ、事前`--dry-run`怠り)→再発防止=TTS前に`--dry-run`で対象確認を委任文へ明記。(b)全体起動間隔150秒未達でY/Z/Xを並列起動(最小20秒差。同一run≥300秒は維持、実害なし。Charter原則2優先の判断=Fableとして今後は「異なるrun間の並列起動は可、同一runner種別の同時起動は避ける」へ運用明確化を提案として記録のみ、規則変更はユーザー判断)。(c)F班 Y L2で予算guard STOP 1回(承認枠拡大で再実行、API 0)。

## 実施事項

1. `OPEN_ITEMS.md`: OPEN-562=PRODUCTION_WIRED(根拠・限界・commit列挙)、OPEN-545=送信改善もPRODUCTION_WIRED(ユーザー実機確認)、OPEN-561更新、OPEN-543(07G回帰493 PASS記録)。OPEN-562行が3,000文字超→`OPEN_ITEMS_HISTORY.md`へ履歴切り出し(既存の切り出し様式に倣う。管理場所は`OPEN_ITEMS.md`のまま)。
2. `CURRENT_SPEC.md`: 学習項目①②③表示仕様節のStatus=PRODUCTION_WIRED(限界付き)、D-F1是正(`_part1_enabled`=「b1b常時 or display_spec」)を追記。フォームv3送信・コピー形式節=PRODUCTION_WIRED。
3. `DECISION_LOG.md`: 新規エントリ「SLOT-23 6経路PRODUCTION_WIRED(Fable受入)」「フォーム送信・コピー改善PRODUCTION_WIRED(ユーザー実機確認)」。
4. `docs/pm/PM_GOVERNANCE.md` 違反・逸脱記録: 上記4(a)〜(c)。
5. `docs/pm/ACTIVE_TASK.md`: 管理ID=PM-SSOT-SYNC-27、Status、進行中=なし、次=AI島HR承認後の完成(PREP_06)・最終報告、UDR-blocking=AI島HR Q1・UDR-MONKEY-1、QDC=当日約¥111(KP75 15.84+KCP 11.2+GPG 7.5+AIF 37.4+S23F 24.2+TRU 1.15+他)。
6. commit: `PM-SSOT-SYNC-27: SLOT-23 ①②③表示仕様 6経路PRODUCTION_WIRED(Fable受入)・フォーム送信改善PRODUCTION_WIRED(ユーザー実機確認)・D-F1是正・AI島準備完了・違反記録(API 0)`。Secret grep 0件。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文=`...\subagents\agent-*.jsonl`最新・先頭が本管理IDのものをindex 0で逐語抽出(方法は`docs/pm/RESULT_PACKET_SSOT22.md`(0))+check。T-2/T-3: なし。

## 事前指定Grep一覧

`OPEN-543|OPEN-545|OPEN-561|OPEN-562`(OPEN_ITEMS.md)、`学習項目①②③|送信・コピー形式|PM-SSOT-SYNC-26`(CURRENT_SPEC.md/DECISION_LOG.md/PM_GOVERNANCE.md)。参照=`docs/pm/RESULT_PACKET_{S23F,S23G,AIF6}.md`のSSOT文案、`ROUTE_STATUS_06.md`。

## 報告

`docs/pm/RESULT_PACKET_SSOT27.md`(gitignore): (0)T-0、(1)変更箇所(file:line)、(2)Status表、(3)判断候補、(4)必須4行+「判定整合」、commit hash・raw URL。末尾5行要約。
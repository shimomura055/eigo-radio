# Delegation Prompt — USER-TEST-NEWS-LIGHT-TOPIC-01-CLOSEOUT-03

管理ID: USER-TEST-NEWS-LIGHT-TOPIC-01-CLOSEOUT-03
報告先: docs/pm/RESULT_PACKET_NEWS_LIGHT_03.md(新規、★★★★報告ここから/ここまで、累積Full Report=RESULT_PACKET_NEWS_LIGHT_02.mdの到達点要約を冒頭に再掲)
現在main=origin/main=0b4592c4(要fetch確認)
並行Agentなし(本タスク単独。ただしdocs/pm/locks/audio_stage.lockが残っていれば内容を報告のうえ削除してよい)

## ユーザー正式判断(2026-09-17、そのまま実行)
1. Tiny Bags B1: 完成playerで全体試聴、OK/承認(成果物の正式なユーザー品質承認。Trial評価ではない)。article/audio/playerは現行完成版を維持、再生成禁止。
2. Tiny Bags A2 full_story_part2: Human Review確認ページでToteme/Kallmeyerの実読を確認済み、現在の音声でOK、最終版として採用。追加TTS再生成不要。

## 実施内容

### B1
- DECISION_LOGへユーザー承認記録(user listening PASS / approved、URL・SHA e858649a付き)。Status=USER_TEST_READY(ユーザー試聴PASS済み)。
- ARTIFACT_REGISTRY B1行をUser Quality=PASSへ更新。

### A2
1. Human Review Lockをユーザー承認に基づき正式解除: 既存の正式手順(Space Weapons B1 preview/full_story_part1で使ったer003_v1_n3_01_assemble.record_human_approval/human_approved_segments.json、er011_human_review_lock_01.record_outcome等)でfull_story_part2の現Human Review音声(確認ページで提示したものと同一wav/attemptであることをsha256で照合)をfinalとして採用、approver=user、日付・管理ID・根拠(RESUME-02確認ページURL)を記録。review_lock_state.json=RESOLVED。
2. Assembly(er003_v1_n3_01_assemble、Audio Validation Gate、override禁止。Human Approval記録によりGateを正規に通過することを確認)。
3. build_web_player_common.pyでplayer.html(記事dir root、web/episode.mp3+segments+manifest)。
4. user_test/unified.html?src=...&level=A2&en=<A2タイトル>&ja=<日本語タイトル>形式URL(rawcdn.githack、commit/push後SHA)。
5. Playwright headless Chromium E2E(page load/Play開始/currentTime進行≥2秒/audio errorなし/script表示/60秒seek/Key Phrase表示、docs/pm/closeout_136_e2e/型)、evidence JSON+screenshot保存。
6. 最終URL提示(raw mp3リンク禁止)。A2 playerは「最終確認用」であり固有名詞の再判断は求めない。

### Sheet / ユーザーテスト記事一覧
- 既存のユーザーテスト記事一覧・管理表があるか確認(user_test/配下、docs/配下、ARTIFACT_REGISTRY News-familyセクション等をGlob/Grep)。存在すれば既存形式でTiny Bags A2/B1を追加/更新。無ければARTIFACT_REGISTRYのみ。
- Sheet投入用行(記事タイトル(English)=A2代表 "Are Tiny Bags Back? Fashion's Answer Is More Complicated"/記事タイトル(日本語)/記事の概要(日本語)/Family=News(ライト系)/ノーマル(A2) URL/Advanced(B1) URL/備考=最新ニュース(ライト系))を確定して報告。

### SSOT
- DECISION_LOG.md: ## USER-TEST-NEWS-LIGHT-TOPIC-01-CLOSEOUT-03(索引+本体): B1ユーザー承認、A2発音Human Review承認(Toteme/Kallmeyer現行実読を採用、再生成なし)、A2 finalize結果、Gate/E2E evidence、Status。記事品質承認とProduction spec Statusを混同しない(Voices等の別仕様Statusに触れない。PRODUCTION_WIREDという語は記事には使わない。News通常経路の基盤Statusは既存記載のまま)。
- OPEN_ITEMS.md: OPEN-159行へ「Tiny Bags Toteme/Kallmeyer件はユーザー承認でclose(2026-09-17)。proper-name一般課題としてのOPEN-159本体は継続」を追記。他に本件固有の未決項目があればclose。
- ARTIFACT_REGISTRY.md: Tiny Bags A2/B1行をUSER_TEST_READY(ユーザーPASS)+最終URL+E2E evidenceパスへ更新。
- CURRENT_SPEC.md: 変更不要(個別記事承認のみ)。確認だけ行い無変更を証跡化。

### PM Governance追記(8節「並列起動」関連、最小限)
docs/pm/PM_GOVERNANCE.mdの8節へ2026-09-17の実測教訓を追記:
(a) 本環境では並列Agentが同一working tree/同一ローカルgit checkoutを共有するため、相手タスクの未commit変更が自タスクのcommitに混在しうる(実例: 86cbd93dにVoicesタスクの共有ストア追記が混在、破損なし)。
(b) docs/pm/locks/audio_stage.lockはcheck-then-writeのためレースが発生した(実例あり)。以後lockは原子的作成(open(path, "x")相当)で取得し、取得失敗時はpollする。
(c) Key Phrase選定stageはMaster Audio Store/Pronunciation Ledgerへ書き込むため「音声段階」に含める。
(d) 原則: TTS/ASR/Ledger/Key Phrase stageを含むタスク同士は並列起動しない(text-onlyタスクとの並列のみ可)。SSOT編集はfetch+merge直後に行い即commit/push。変更履歴節に1行追記。

### Git
明示add、git add -A禁止、wav禁止(mp3可)。fetch→merge(rebase/force禁止)。
commit message例: USER-TEST-NEWS-LIGHT-TOPIC-01-CLOSEOUT-03: Tiny Bags B1ユーザー承認記録+A2 Human Review承認→Assembly/Gate/player/E2E+SSOT+PM_GOVERNANCE 8節追記
trailer: Task-ID: USER-TEST-NEWS-LIGHT-TOPIC-01-CLOSEOUT-03

## STOP条件
Human Approval記録後もGateが通らない/E2E失敗/git conflict/承認対象wavと確認ページ音声のsha256不一致(その場合は承認記録せずSTOP)/費用¥50超(TTSなしのため通常¥0〜数円)。

## T-0
委任文をdocs/pm/delegation_log/USER-TEST-NEWS-LIGHT-TOPIC-01-CLOSEOUT-03.mdへ保存し.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file <path> --json-out <path>_check.json、結果1行記録(FAILでも継続)。
事前指定Read: docs/pm/RESULT_PACKET_NEWS_LIGHT_02.md、er014_output/user_test_news_2ep_01/space_weapons/b1b/のHuman Approval記録例(human_approved_segments.json・approvalスクリプト)、er003_v1_n3_01_assemble.py(record_human_approval)、er011_human_review_lock_01.py、tiny_bags driver、docs/pm/closeout_136_e2e/、PM_GOVERNANCE 8節。事前指定外Readは理由付き報告。

## 報告項目(★ブロック内)
0.T-0 1.B1承認記録(DECISION_LOG抜粋) 2.A2 Human Approval記録(segment/attempt/sha256/approver/根拠) 3.Lock解除状態 4.Assembly/Gate結果(duration/peak/clipping) 5.A2 player URL+E2E evidence 6.B1 URL(現行維持、SHA) 7.Sheet行+記事一覧更新結果 8.SSOT反映箇所(DECISION_LOG/OPEN_ITEMS/ARTIFACT_REGISTRY/CURRENT_SPEC無変更証跡/PM_GOVERNANCE 8節) 9.cost 10.Git SHA 11.PM Closeout Mandatory Check 12項目(1.B1ユーザー承認記録済 2.A2 Human Review承認記録済 3.A2 Lock解除済 4.A2 Assembly/Gate PASS 5.A2 E2E PASS 6.A2/B1最終URLあり 7.SSOT反映済 8.OPEN_ITEMS整合 9.ARTIFACT_REGISTRY整合 10.Git commit/push済 11.未処理USER_DECISION_REQUIREDなし 12.approved-but-unwired項目なし)を各項目evidence付きで○/× 12.ユーザー判断 A/B(Tiny Bagsはいずれも「なし」想定、A2 playerは最終確認用として提示) 13.無変更証跡/事前指定外Read。

## 管理ID

PM-SSOT-SYNC-24(SSOT同期。対象=FORM委任_08(ead898c90/e6efc99c1)、GPG委任_05(f28524f7e)+05C(c88ee48bc)、AI-ISLAND委任_03(d05729316)+04(31fdc7cf4)、SLOT-23委任_02(45bb6e012)、ユーザー正式決定「学習項目①②③の表示仕様正式採用・X/Y/Z Production Wiring」(原文=`docs/pm/delegation_log/2026-10-27_SLOT-23-CONSUMER-DESIGN-01_USER.md`、逐語保存済み)。API 0)。あなたが唯一のSSOT編集権者。並行Agent: KCP委任_04(Z Std evidence run)、Opus条件Aレビュー(read-only)。全文読込禁止(Grep)。pathspec付きcommit、`git push origin HEAD:main`。

## 性質/禁止

- 記録同期。Status格上げ禁止(**本SYNCで新たにPRODUCTION_WIREDと書かない**。OPEN-559/556の6経路WIRED判定はZ Std evidence(KCP4)後にFableが行う)。
- 禁止Git操作なし、承認範囲を要約で広げない。時間見込み約1h。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文=`...\subagents\agent-*.jsonl`最新・先頭が本管理IDのものをindex 0で逐語抽出(方法は`docs/pm/RESULT_PACKET_SSOT22.md`(0))+check。T-2/T-3: なし。

## 実施事項

1. **DECISION_LOG**(新規、原文ref付き): SLOT-23正式決定3点(Std②=C案: Adv Part 1同等をStdにも・Std難易度/本文ハイライト=①太字+二重下線・②太字+下線・③下線のみ、サイズ色同一・背景なし・③短い日本語訳・音声Chunk不変/遡及なし: AI島と今後の新規のみ)=APPROVED_FOR_PRODUCTION、到達目標PRODUCTION_WIRED、全6経路、受入条件14。旧「Part 1はAdvancedのみ(Standard・Yへ拡張しない)」(CURRENT_SPEC:2083-2086)は②表示に関して本決定で変更(履歴化)。**注記**: 「英語で解説する」の解釈(解説本文の言語)はFableがユーザーへ確認中(未確定事項として明記)。Fable決定: 設計=`DESIGN_02.md`正本、`DESIGN_01/USER_DECISION_DRAFT_01/OPUS_REVIEW_REQUEST_01`は失効、Opus条件Aレビュー実施中。
2. **CURRENT_SPEC**: (a)`:2083-2086`付近のPart 1節に「2026-10-27ユーザー正式決定により②追加解説の表示はStandardにも拡張(SLOT-23、OPEN-562、実装中)。以降の『Advancedのみ』記述は②に関して旧仕様」の注記行(`SPEC_CONFLICT_02.md` S29/S30の指摘箇所)。(b)学習項目①②③表示仕様の新節(正式表示仕様表・共通条件・照合原則(候補データの表層形/出現位置優先、複数出現=不合格としない、特定不能fail-closed)・遡及なし・Status=APPROVED_FOR_PRODUCTION/実装中)。(c)文法新仕様節: 6経路evidence取得(`EVIDENCE_RESULT_05/05C.md`、X 1件/0件(AI島)、Y Std Top1/Adv Top2、Z Adv 1件/Std 0件、2件拒否、凍結model耐性、費用¥3.61)=EVIDENCE(WIRED判定はFable、Z Std KCP後)。(d)フォームv3送信形式v3節: 委任_08の契約§6(コメント既定語=コメントなし、解説末尾`=+`除去)追記。
3. **OPEN_ITEMS**: OPEN-545(委任_08で残課題2件解消、ユーザー実操作確認待ちのまま)、OPEN-559(6経路EVIDENCE、Fable判定待ち)、OPEN-556(Z Std runtime evidence=KCP4実行中、他5経路EVIDENCE)、OPEN-561(AI島: TTS完了Std19/Adv18、assembleでM3 Style Gate BLOCK=`full_story_part1_k2`「AIs」Local Rewrite(Std `AI agents`/Adv `AI systems`)、HR提出`hr_01.html`・ユーザー回答待ち、費用¥36.52、診断=仕様どおり(`DIAG_SLOWDOWN_ASR_01.md`)、新表示仕様は承認後のHTML再ビルドで適用)、OPEN-562(ユーザー決定済み→APPROVED_FOR_PRODUCTION、DESIGN_02、Opus条件A中、解釈確認1件、分類=修正へ進む)、**新規OPEN(分類=ユーザー判断要・低優先)**「複数形略語(例: AIs)はASRが単数と転写しやすくretry/LRを誘発(約¥8〜9/記事の超過)。対策候補=Writer原則で回避/発音供給。次回Writer原則見直し時に判断」、**新規OPEN(分類=実害なし・任意)**「M3 Gate `STD_FALLBACK_USED_OR_UNKNOWN`がLR成功時の`_merge`で無条件`fallback_used=True`となる記録非対称(`er003_v1_crosslevel_audio_02_common.py:477`)、観測性: 非最終slotの減速後Azure転写が未保存」。
4. **PM_GOVERNANCE 違反・逸脱記録**: (a)GPG委任_05 agent: 同一run 5分3回禁止違反(`run_gpg5_y_01` 12:01:47/12:04:17/12:06:20=273秒3回)→RESTART_STORM STOP、別名コピー続行は自動判定で拒否され未実施(適切)、X経路で起動間隔101秒(全体150秒未満)。是正=Fable権限でSTOP解除1回・起動1回(05C、理由記録済み)。再発防止=evidence委任文に「起動間300秒以上」を明記済み。(b)FORM委任_08 agent: 「fixtures追加のみ」の所有範囲に対し既存fixture 1件を更新(契約変更に伴う必然、記録のみ)。(c)AI-ISLAND委任_03: USER_03原文ファイル未作成のため委任文引用部から転記して`--user-ref`に使用(逐語性はFable委任文経由。記録)。
5. **ACTIVE_TASK.md**固定ヘッダ更新(管理ID=PM-SSOT-SYNC-24、Status、進行中=KCP4/Opus条件A、次=SLOT-23実装A〜F/AI島HR回答待ち/6経路最終判定、UDR-blocking=AI島HR(AIs音声)・解説言語の解釈・フォーム実操作確認・UDR-MONKEY-1、QDC=当日約¥80(KP75 15.84+KCP2B 7.45+KCP3 0.71+GPG2S 3.885+AIF1 0.873+AIF3 36.52+GPG5/5C 3.61+TRU 1.15+他))。
6. commit: `PM-SSOT-SYNC-24: SLOT-23正式決定(Std②=C案/二重下線/遡及なし)APPROVED・文法新仕様6経路EVIDENCE・AI島HR待ち・FORM08・診断結果・新規OPEN2件・違反記録(API 0)`。Secret grep 0件。

## 事前指定Grep一覧

`OPEN-545|OPEN-556|OPEN-559|OPEN-561|OPEN-562`(OPEN_ITEMS.md、最新番号+1で新規)、`Advancedのみ|Vocabulary & Expressions|送信・コピー形式|PM-SSOT-SYNC-23`(CURRENT_SPEC.md/DECISION_LOG.md)、`違反・逸脱`(PM_GOVERNANCE.md)。参照=`docs/pm/RESULT_PACKET_{FORM8,GPG5,GPG5C,AIF3,AIF4,S23D2}.md`のSSOT文案、`SPEC_CONFLICT_02.md` S29/S30。

## 報告

`docs/pm/RESULT_PACKET_SSOT24.md`(gitignore): (0)T-0、(1)変更箇所(file:line)、(2)Status表、(3)判断候補、(4)必須4行+「判定整合」、commit hash・raw URL。末尾5行要約。
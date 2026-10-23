MARKER: FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01 委任_05 (2026-10-24, Fable→sonnet-worker)

# 管理ID: FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01 委任_05(作品承認Closeout。API 0円・コード変更0)

## ユーザー決定(2026-10-24、原文は§Zに逐語。最初に `docs/pm/delegation_log/2026-10-24_FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01_USER_02.md` として§Zを逐語保存すること)
- UDR #174: ユーザー最終試聴PASS。Standard/Advancedとも完成版として正式承認。
- 「約20分→30分」の差はユーザー確認済みで作品上の重要な問題ではないと判断(追加調査・修正・報告不要)。ただし原作の重要設定やタイトルを自由に変更してよい一般許可ではない。
- OPEN-482は作品承認と切り離す(作品の再生成・再試聴は不要)。OPEN-482自体は別管理ID `ASR-TIME-NUMERAL-EQUIVALENCE-01` で並行して対応中(本委任では触らない。OPEN-482本文の編集もしない)。

## 作業
1. `docs/pm/USER_DECISION_REGISTER_01.md` #174 を「判断済み(2026-10-24、A=PASS・正式承認)」に更新(既存書式)。
2. `OPEN_ITEMS.md` OPEN-483(『二十年後』完成版提出・試聴待ち)を CLOSED_USER_PASS(2026-10-24) に更新し、承認内容・20分/30分の件のユーザー判断・OPEN-482は切り離しである旨を1行で追記。
3. `DECISION_LOG.md` にユーザー決定1件(UDR #174承認、20分/30分はユーザー容認、一般許可ではない旨、OPEN-482切り離し)。
4. `CURRENT_SPEC.md`: 『開いた窓』の承認時(CLOSEOUT_01、commit d9de77f47)に行った書式と同じ最小追記のみ(Family Z完成作品一覧等の既存記載があればそこへ1行。なければ変更しない。新規節は作らない)。
5. Closeout文書 `docs/research/FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01/CLOSEOUT_01.md`(『開いた窓』CLOSEOUT_01.mdと同形式): 試聴URL、構成・再生時間・Voice、費用47.91円、制作経路、Gate結果、HR Lock履歴(approve_regenerate 2回・人間承認で通した音声0)、OPEN-482切り離しの明記、ユーザー承認日。PM Closeout Mandatory Check(PM_GOVERNANCE)の項目を確認して結果を記す。
6. `docs/pm/ACTIVE_TASK.md` の本管理IDの行を CLOSED_USER_PASS に更新。
7. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-24_FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01_委任_05.md`(先頭MARKER一致でN確定、0始まり)。
8. commit/push: 他agent(Family Y 委任_18)が `OPEN_ITEMS.md`/`DECISION_LOG.md` を並行編集している可能性がある。commit前に `git diff -- OPEN_ITEMS.md DECISION_LOG.md` を確認し、自分以外のhunkが含まれる場合は数分待って再確認、それでも残る場合はその旨を報告に明記したうえで自分のhunkのみを `git add -p` 相当で選択(できなければ全体commitしコミットメッセージに「他agentのhunkを含む」と明記)。`git commit --only -- <paths>`、`git add -A/-u/-f`禁止、secret grep 0件、`git push origin HEAD:main`。
9. 報告 `docs/pm/RESULT_PACKET_FZ20Y5.md`: 更新箇所一覧・commit hash・4行(既存仕様整合/未承認機能の既定値/失敗終了時の最終成果物/撤去)・判定整合行。

## §Z ユーザー指示原文(逐語)
# Family Z『二十年後』正式承認・OPEN-482独立解決指示

## 1. ユーザー決定

### ① Family Z『二十年後』— 正式完成版承認

**UDR #174：ユーザー最終試聴PASS。完成版として正式承認する。**

- Standard／Advancedともに承認。
- 原作の「約20分」が本作で「30分」になっている点は、ユーザーが確認し、作品上の重要な問題ではないと判断した。
- 本件について追加調査・修正・報告は不要。
- この判断は、原作の重要な設定やタイトルを自由に変更してよいという一般的な許可ではない。
- OPEN-482は作品承認とは切り離す。今回の作品を再生成・再試聴する必要はない。

UDR #174、DECISION_LOG、必要なSSOTを更新し、作品の承認をCloseoutする。

### ② OPEN-482 — 未解決の時刻表現検査不具合2件

**作品承認とは独立した品質改善タスクとして、2件とも解決すること。**

対象：

1. `ten thirty` と `10:30` が同じ時刻を表すにもかかわらず、NGになる問題。
2. `ten thirty` と `1030` の桁連結が、誤って一致扱いになる既存の問題。

いずれもFamily X/Z共通の音声検査品質に関係する。

## 2. OPEN-482の対応方針

原因究明 → 対策立案 → Trial検証 → 結果評価 → 必要な修正・再検証を、Fable／Claude側で自律的に実施すること。

単に今回の2表現を例外登録するのではなく、時刻・年号・通常の数値表現を含む既存の判定構造を確認し、問題の根本原因を解消する。

特に以下を満たすこと。

- 同じ時刻を表す表現は、既存の音声判定方針と整合する形で正しく救済する。
- 実際には異なる値や発音を、不適切に一致扱いしない。
- 年号や通常の数値表現との衝突を防ぐ。
- 既存の同音救済仕様、Primary／Secondary ASR、数値正規化、最終品質Gateとの整合を維持する。
- Family X/Zの正常な音声を誤NGにせず、異常な音声を誤PASSにしない。

具体的な実装方式は固定しない。既存機構を最大限活用し、最も簡潔で保守性の高い解決方法を選択すること。

## 3. 自律検証・STOP条件

- 既存仕様の不具合修正と検証は、承認済み作業範囲・開発予算内で自律的に進める。
- Trial回数だけを理由に停止しない。
- 改善が見込めない方法の反復は避け、原因やアプローチを見直す。
- 独立した調査・検証は可能な範囲で並列化し、完成までの時間を最小化する。
- 不要なTTS再生成を避け、既存の音声・ASR結果・合成テストを優先活用する。
- 品質基準を独断で変更しない。
- 新仕様の採用が必要になった場合、重大な品質リスク、承認範囲・予算超過、解決不能なblockerが発生した場合はSTOPしてユーザー判断を求める。

## 4. Production反映と受入条件

既存承認仕様の不具合修正として解決可能な場合は、Family X/Z双方のProduction Wiringまで完了させること。

完了条件：

1. OPEN-482の2件について、原因と解決内容を説明できる。
2. 正常系・異常系・境界ケースのTrial／回帰テストがPASS。
3. 既存の時刻・年号・数値表現について、誤PASS／誤NGの新規発生がない。
4. 正式Production経路に反映され、retry／fallback／regeneration／resumeとも整合。
5. 正式経路での発火・判定について、適切なruntime evidenceを取得。
6. Family X/Z双方の適用状況を確認。
7. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMSを更新し、Git反映まで完了。
8. 残存課題や未確認事項を隠さず報告する。

DEV／Trialのみの成功や、コード実装のみでPRODUCTION_WIREDと判断しないこと。

## 5. 最終報告

作品『二十年後』の承認CloseoutとOPEN-482の品質改善を明確に区別して報告する。

OPEN-482については、原因、修正内容、Trial結果、既存仕様への影響、Family X/ZのProduction反映証拠、QCD影響、残課題を簡潔にまとめること。

**優先順位は品質（Q）＞完成速度（D）＞量産単価（C）。承認済み品質を満たした時点で追加の磨き込みをせず、速やかにCloseoutする。**

なお、UDR #173（Key Phrase関連）は本件とは独立した判断待ちとして維持し、無断で採用・変更しないこと。
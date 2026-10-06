## 管理ID
OPEN-233-LEDGER-CLARITY-P-TRIAL-01 委任_E1(評価④Fact安全性+原資料照合、¥0)。

## 性質/到達上限Status/禁止事項
性質: 評価(read-only+評価ファイル1本)。判定材料のみ、最終判定はFable。有料API/台帳記事変更/Production/SSOT/git/再実行は禁止。E2/E3出力には触れない。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1/D-1/G-1/F-1該当なし。T-0は簡略保存+checker。T-2はTTSなし。T-3は対象外。

## ユーザー指示(原文、要点)
④Factそのものの安全性は必須条件。新Fact追加・原資料にない主体/因果/時系列・否定肯定反転・数字日付固有名変化・断定強化がないこと。疑義1件でもSTOP。

## 事前指定Read一覧
fact_safety.md、ledger_diff.md、After/Before台帳、draft/verification JSON、pprime_provenance.json、00d_eval_template.md ④欄を全て読了。

## 事前指定Grep一覧+追記位置・更新位置の手順
原資料はCNA(Reuters転載)・404 Media・AOL・Meta公式・research.meta.aiをcurlで取得し逐語照合。出力はafter_pprime_01/eval/E1_fact_safety_review.md。

## 実行コマンド全文
curl -L -s による原資料取得のみ(¥0)。checker実行はdocs/pm/tools/check_delegation_prompt.py。

## SSOT追記文
なし。

## Git
なし。

## 報告(RESULT_PACKET項目、12行以内)
疑義0/保留2/追加0/断定強化1(軽微)/否定反転0/数値相違0。詳細はE1_fact_safety_review.md。

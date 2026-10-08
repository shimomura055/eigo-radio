# 委任文(全文保存) FACTLOCK-WRITER-REDESIGN-TRIAL-01 委任_05

## 管理ID
FACTLOCK-WRITER-REDESIGN-TRIAL-01(委任_05: 残存NGと照合検出の突合分析。¥0・API課金なし・git操作なし)。並行タスクあり: 同管理IDの委任_03(診断、v2_design/)・委任_04a(sweep設計、sweep_01/)、PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01 委任_03(配線・git)。本委任はそれらのファイルに書き込まない。

## 性質/到達上限Status/禁止事項
- 性質: 分析(既存artifactのみ)。到達上限Status: ANALYZED。
- 隔離規則: 書込は er052_output/factlock_writer_trial_01/eval/residual_analysis/ 配下と docs/pm/RESULT_PACKET_FACTLOCK_RESIDUAL.md(新規)、docs/pm/delegation_log/2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_05.md(+_check.json)のみ。他は読み取りのみ。SSOT・git・API禁止。
- 費用: ¥0。Opus独立技術レビューGate: 非該当。時間見込み: 約30分。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Readを基本。G-1: git出力は使わない。F-1: transcript退避不要。T-0: 受領した委任文をdocs/pm/delegation_log/<管理ID>.mdへ全文保存し、python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json を実行、結果をRESULT_PACKETへ1行記録(FAILでも継続)。T-2: TTSなし。T-3: 課金なし。

## ユーザー指示(原文)
「改善はしたものの、軽微・重大が思ったより良くなってませんね。想定通りですか。」(2026-10-08)。Fableの仮説: 今回のFact Lockは「規則のみ・照合は測定のみ(修正に使っていない)」であり、照合が検出済みの不整合を修正に回せばさらに下がる余地がある。これを既存データで数値化する。

## KPI provenance欄 / Opus台帳更新
該当なし(reuse分析)。

## 事前指定Read一覧
- er052_output/factlock_writer_trial_01/eval/SUMMARY_FL.md §2
- 盲検採点の生結果(eval/**/*.json のfactlockセルNG項目JSON。MAP eval/_private/MAP.json でblind ID→run解決)。factlockセルの全NG項目[重大・軽微・保留]
- 各該当runの runs/<slug>/control/b<i>__factlock__r<j>/factlock_check_r2.json(必要ならr0/r1)、ja_writer/revision2_with_tags.md、b1b/article.md
- eval/FACTLOCK_CHECK_SUMMARY.md §1

## 事前指定Grep一覧+追記位置
NG項目の「NG文(引用)」と該当runのR2(タグ付き)本文/EN本文を突合し、各NG項目について: (a)NG文はタグ付き文/タグなし文/タイトルか、(b)照合(i)で 整合/不整合/判定不能 のどれか、(c)照合(ii)でタグなし文なら5分類のどれか、(d)数値照合(iii)に該当するか、(e)JA Fact Check(R0/R2)はその箇所を指摘していたか、(f)ENのみのNGならJA R2に同内容があるか(翻訳段で生じたか)。
追記位置: eval/residual_analysis/RESIDUAL_NG_VS_CHECK.md(表+要約)、residual_items.json。

## 実行コマンド全文
cwd=C:\Users\tensh\eigo-radio。委任文保存+検証: .venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_05.md --json-out docs\pm\delegation_log\2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_05.md_check.json。分析はpython(読み取り)で行い、API呼び出しは一切しない。

RESIDUAL_NG_VS_CHECK.md の必須内容:
1. factlockセルの全NG項目一覧(重大/軽微/保留別、JA R2/EN別、NG文引用、型、該当run)。
2. 各項目の突合結果(a)〜(f)の表。
3. 集計: 照合(i)/(ii)/(iii)のいずれかが検出していたNGの件数と割合(=修正ループを入れた場合の理論上の削減上限)、どの照合も検出していないNGの件数と型、ENのみでJAにないNGの件数(翻訳段由来)。
4. 逆方向: 照合(i)が不整合と判定した13文(R2)のうち、盲検採点でNGになっていない文の件数と例3件。
5. 所見(事実のみ): 修正ループを入れた場合に軽微/記事がどこまで下がりうるかの機械的な上限値(例: JA 0.21→x、EN 0.32→y)。推奨は書かない。

## SSOT追記文 / Git
なし / 本委任ではgit操作禁止。commit候補: eval/residual_analysis/**、docs/pm/RESULT_PACKET_FACTLOCK_RESIDUAL.md、委任文(+check.json)。

## 報告
docs/pm/RESULT_PACKET_FACTLOCK_RESIDUAL.md(ヘッダ: 管理ID・Status=ANALYZED・¥0・git未操作)。本文: 上記1〜5の要約(表は件数のみ、例は各3件まで)、問題・残作業、check_delegation_prompt結果1行、一覧外Readの理由。

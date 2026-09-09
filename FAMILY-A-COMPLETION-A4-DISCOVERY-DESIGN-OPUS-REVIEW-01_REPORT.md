# FAMILY-A-COMPLETION-A4-DISCOVERY-DESIGN-OPUS-REVIEW-01 — Opus設計レビュー転記

管理ID: FAMILY-A-COMPLETION-A4-DISCOVERY-DESIGN-OPUS-REVIEW-01
実施日: 2026-09-09
実施者: Opus(診断・設計レビュー専用、Sonnet委任のDESIGN-01成果物に対する
レビュー)。本タスクはSonnet(sonnet-worker)がFableの委任により、Opus
レビュー結果を正式Reportとして転記する作業。**転記のみ・実装なし・
API呼び出しなし(費用¥0)**。

対象: `FAMILY-A-COMPLETION-A4-DISCOVERY-DESIGN-01_REPORT.md`
（Sonnet設計案、2026-09-09作成）

Opusコスト実績（Fableより受領した数値）: token 121k、実行時間327秒。

レビュー結論の重大度: **HIGH**（判定木の排他性・再現性に関する構造的
欠陥、および事実誤り[POOL_TOPIC_MASTER件数]を含むため）。

---

## 重要な注記（転記の性質について）

本ファイルは、Fableが受領したOpusの最終メッセージ**全文**をこのSonnet
委任テキスト内で受け取ったものではなく、Fableが委任文中に記載した
「Opusレビュー要旨（Fable転記）」を、**改変せずそのまま**以下に転記した
ものである。Opusの生の出力全文（観点1〜9・未確認事項・参照ファイルの
詳細な内訳を含む完全なテキスト）は、本委任者（Sonnet）には渡されて
いない。したがって以下は「Fableの会話ログにあるOpus最終メッセージの
要約」であり、Opus自身が生成した一字一句のトランスクリプトではない
（この区別はFableの委任文自身も明記している）。原文全文が必要な場合は
Fableの会話ログを参照する必要がある。

---

## Opusレビュー要旨（Fable転記、原文ママ・改変なし）

- [HIGH] 判定木Q1〜Q5は排他性・再現性を満たさない(Q1/Q3の循環、Q3が
  Major/Daily Gate項目1と矛盾、Q5が判定不能バケット、Q2先行がDiscovery
  母集団をTrendへ誤送)。→ **2軸判定**(軸A=中心的主張の妥当性が日付/
  最近性に依存するか、軸B=独立Signalの集約に依存するか。(A=Yes,B=No)
  →Major/Daily、(A=Yes,B=Yes)→Trend、(A=No)→Discovery)を未承認仕様
  候補として提案。
- [HIGH・事実誤り] 「POOL_TOPIC_MASTER全20件がWhyタイトル」は誤り
  (英語Why 7件、日本語なぜ7件。No.5/7/12/14/17は「変化の主張」型)。
  ただしPOOL_TOPIC_MASTER 6-7行の「Pool型=Evergreen、特定の1件の最近の
  出来事に依存しない」承認済み定義はDiscoveryの否定的条件そのもの→
  Discoveryを「既存Pool型の正式化」として扱う案(未承認)。
- [HIGH] 最も価値の高い検証が抜けている: **¥0の机上検証**=判定ロジック
  をPOOL_TOPIC_MASTER 20件+Hanshin/Health/イランへ当てはめ、(i)判定
  不能率、(ii)Trend誤送数、(iii)独立2判定者間の不一致率を測る。
- [HIGH・肯定] `EDITORIAL_TYPE_MODULE_BLOCKS`へ`{"discovery_why":
  DISCOVERY_FOCUS_MODULE_BLOCK}`追加はTrial-05 VALIDATED Promptと
  バイト等価(配線技術リスク低)。ただし見出し文言の改稿(Trend前例)と
  Trial-05スクリプト小改修が前提。
- [MED] Research方式はLLM呼び出しなしの「説明源の優先順位ガイドライン」
  に縮小、共通Ledger決定に従属。myth-correctionは「Discoveryへ追加
  (Newsから除外しない)」、UDRのまま。Fact CheckerとLDCの混同を分離。
  成功基準を「blocking 0件+人間が解釈のLedger内包を確認」へ。既決事項
  (A-UDR-9/10)を「発見」と書かない。
- UDRは3ブロックへ統合: D1(定義・判定ロジック: 推奨(b)2軸+Pool型接続、
  確定前に机上検証)、D2(Layer3 DEFERRED解除: 推奨(b)机上検証+N=3
  Trial)、D3(派生: myth-correction/Point Role hint/Engagement/Research/
  LDCカテゴリは保留)。

---

## 本Reportの位置づけ

上記はDESIGN-02(`FAMILY-A-COMPLETION-A4-DISCOVERY-DESIGN-02_REPORT.md`)
の設計修正・机上検証(¥0)の直接の入力である。DESIGN-02は上記指摘への
対応（訂正・再構成・検証）を行うが、Opus提案（2軸判定・Pool型正式化・
UDR 3ブロック構成）自体はいずれも**未承認仕様候補**のままであり、本
Reportおよび DESIGN-02のいずれも採否を決定していない。

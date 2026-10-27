# REMOVAL_RESULT_01(撤去・残置の確認。委任_02B)

- 撤去した規則・検査・test: **なし**(新検査はAND追加のみ。既存Gate・正規表現・閾値・辞書・Promptは無変更)。
- 変更した既存test期待値: 1件。`er128_kp_confirmed_content_test_01.py::test_text_change_with_user_record_stops_before_paid_generation`(02A)。承認済みM8により「出典文が残る本文変更=再バインド」となったため、本文変更の内容を「確定項目の出典文を変更」へ変え、ISSUE停止・有料生成前停止を維持。他のtest期待値は不変。
- 旧ルールの残置Grep:
  - `pinned_items`(M9で実装しない): 実装コードに無し。
  - 確定内容を黙って破棄する旧STALE再生成: 確定レコードがある場合は `stale_issue`/`stale_or_rebind` が先に走る。レコード無し・actor=auto・取消後は従来のSTALE再生成のまま(意図した残置)。
  - 旧 `ref_ja`/extract/explain signature 判定: 凍結なしの経路(確定レコード無し)で従来どおり残置(意図)。
- 残存Grepは RESULT_PACKET_KCP2B.md (4) を参照。

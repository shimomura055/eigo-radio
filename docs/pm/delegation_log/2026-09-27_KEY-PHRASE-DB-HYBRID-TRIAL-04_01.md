# 委任文全文(2026-09-27、KEY-PHRASE-DB-HYBRID-TRIAL-04、Sonnet委任 初回)

管理ID: KEY-PHRASE-DB-HYBRID-TRIAL-04(ユーザー承認 2026-09-27)。一時ファイル
`docs/pm/ACTIVE_TASK_KPH5.md` / `docs/pm/RESULT_PACKET_KPH5.md`(commitしない)。
委任文全文を `docs/pm/delegation_log/2026-09-27_KEY-PHRASE-DB-HYBRID-TRIAL-04_01.md`
に保存しcommitに含める。Guardrail **¥60**(12本文×約¥1+予備。事前見積>¥50なら
実行前STOP)。APIキーは環境変数のみ。**Production配線禁止・Production module
変更禁止**(er003_key_words_* 等は読み取りのみ)。到達可能Status: REJECTED /
VALIDATED / USER_DECISION_REQUIRED のいずれか(Sonnetは仮分類、確定はFable)。

## ユーザー指示(逐語要旨)

目的: Trial-03追加評価で見つかった2つの構造的limitationを修正し、同じ12本文で
再評価する。

- **A. 会話文のsentence segmentation**: 短い引用会話が連続するケースで複数文が
  1 sentence unitに結合され、source_sentence validatorで本文実在1文判定に
  失敗する問題。Family Z/Fictionのようなdialogue-heavy inputでも正しく文単位を
  扱えるよう**一般化修正**。個別作品hardcode禁止。
- **B. rare / technical single word漏れ**: grogginess / self-awakening の
  ような、CEFR-J/NGSL外かつ1-tokenの重要語が機械screening段階で候補に入らない
  問題。LLMに届く前に消えているため、**Stage 1 candidate generation側で修正**。
  1-gramも適切に候補化できる一般化方式を設計。**新DB導入が必要なら勝手に採用
  せずSTOPして報告**。
- 再評価: Trial-03既存6本文(Family X Meta/Hormuz/small_bag A2/B1B)+user_test
  追加6本文(wake/hiring/twins A2/B1)=12本文、同一条件で再実行。cost /
  shortlist / structural PASS / important term保持 / phrase比率 / known bug
  A〜E再発有無を比較。会話タグ(Echo said等)のfalse positiveも観察対象(必要
  なら一般化修正案を出すが、スコープを無断拡張しない)。
- STOP(USER_DECISION_REQUIRED): 新DB採用判断が必要 / 新しいProduct仕様が
  必要 / 追加LLM callが必要(1本文1 call維持) / Production module変更が必要 /
  想定外の大幅cost増。

## 実装方針

- 新規モジュール `er029_key_phrase_db_hybrid_trial_04_stage1.py` /
  `_run.py` / `_test.py` として、er028確定版を**無変更のまま**importまたは
  複製して拡張(er027/er028は変更しない。Trial-03の再現性を保つ)。
- A: 引用符(" " " " ' ' 「」等)で閉じた発話単位と地の文を分離する一般ルール
  (終端句読点+閉じ引用符の後で分割、会話タグ "X said." を独立文として扱う
  等)。source_sentence validatorの「本文実在1文」判定は**Production
  validatorの挙動を変えず**、Stage 1側の文単位がそれに合うようにする。twins
  A2の失敗例をfixture化。
- B: 既存DB(CEFR-J/NGSL/Wiktionary、`er023_output/key_phrase_db_trial_01/
  db_licenses.md` 記載のもの)の範囲で、1-gramを Wiktionary lookup
  (`select_unmatched_ngram_candidates_for_lookup` の min_n=1 拡張等)+頻度/
  文脈条件(記事内出現回数、記事タイトル・見出しとの関連、形態素条件)で候補化。
  ノイズ増加(固有名詞・会話タグ・一般語)を抑える基準を明文化し、shortlist
  件数の増減を記録。wake A2で grogginess / self-awakening が候補に入ることを
  fixture化。
- 12本文を同一条件(1本文1 call、記事全文非送信assertion、共有ストア非書込み)
  で実行。出力 `er029_output/key_phrase_db_hybrid_trial_04/`。
- REPORT `KEY-PHRASE-DB-HYBRID-TRIAL-04_REPORT.md` 新設: 既存資産照合、A/Bの
  設計と一般性の根拠、12本文比較表(Trial-03 vs Trial-04: cost / shortlist件数 /
  structural PASS / 重要語保持 / phrase比率 / bug A〜E / 会話タグFP)、副作用
  (Family X側の選定変化)、STOP該当有無、Status仮分類。

## Git

新規ファイル・出力・REPORT・delegation_logのみpath指定add(`git add -A`禁止、
他Agent[er019_*, er025_*, er006_*, er007_*, er011_*, er022_*, SSOT 3点]の
stageを外さない、index.lockリトライ)。トレーラー
`Management-ID: KEY-PHRASE-DB-HYBRID-TRIAL-04`。push origin main。
reset/amend/rebase/force push禁止。RESULT_PACKETに費用合計・commit hash・
変更ファイル・比較表要約・STOP該当を記載。

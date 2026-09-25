# manual_fix_some_of_the_calls.md

管理ID: NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-01 / Phase B(B-2)
日時: 2026-09-25
実行者: Sonnet(サンドイッチ委任、ユーザー確定事項に基づく手動修正)

## 理由

Reuters原文で「複数の通話のうち一部の通話が人間の契約社員によって
対応されていた」という事実が確認済み(全通話の一部区間ではなく、
複数の通話呼のうち一部の呼が丸ごと人間対応だった、という意味)。
現行英語表現 "some parts of the calls" は「各通話の一部区間」という
誤読を招きうるため、ユーザー判断により "some of the calls"(=複数の
通話のうち一部)へ手動修正した。Writer再実行・Web Search・Ledger再構築は
行っていない(該当4ファイルの該当1文のみの直接編集)。

## 修正箇所(4件)

1. `meta/b1b/article.md` L9
   - Before: "In internal tests, some parts of the calls were handled not by AI, but by human contract workers."
   - After:  "In internal tests, some of the calls were handled not by AI, but by human contract workers."

2. `meta/b1b/parts.json` `part2`フィールド(同一文、article.mdと同期)
   - Before/After: 上記1と同じ

3. `meta/a2/article.md` L9
   - Before: "In internal tests, human contract workers handled some parts of the calls."
   - After:  "In internal tests, human contract workers handled some of the calls."

4. `meta/a2/parts.json` `part2`フィールド(同一文、article.mdと同期)
   - Before/After: 上記3と同じ

## 未修正のまま残るもの(履歴として)

以下は生成当時のcontext echo(監査ログ・Key Phrase選定promptへの投入
テキストの記録)であり、修正対象外(過去の生成履歴としてそのまま保持)。
今回のB-2作業では変更していない:

- `meta/b1b/audit/b1_support_generation.json` / `meta/a2/audit/a2_support_generation.json`
  (Comment生成時のcontext echo)
- `meta/b1b/key_phrases/*.txt` / `meta/a2/key_phrases/*.txt`
  (Key Phrase選定promptへのcontext echo)
- `meta/b1b/audit/review_lock_state.json` / `meta/a2/audit/review_lock_state.json`
  (旧canonical_text_sha256・旧asr_text、B-3で`full_story_part2`のみ
  再生成後に更新される見込み)
- `meta/b1b/narration/attempts/full_story_part2_attempt1_*.json`
  (旧テキストでのTTS attempt記録)

修正後の再TTS・再Assembly結果はB-3で別途記録する。

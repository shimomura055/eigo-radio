管理ID: USER-TEST-14-ARTICLE-FORMAT-RECHECK-01(本タスクで完了)
Status: 完了。Sheet「ユーザーテスト記事一覧_2026-09-16」掲載14記事(26ページ、
  A2/B1合算)のGate 7(n)表示フォーマットをunified.html(SHA`240e0723`)経由で
  E2E全件PASS確認。Family A/C・Voicesの独自player.html(監査用table.timeline
  形式)は無修正のままunified.htmlの汎用パーサ経由で適合(想定どおり)。News-
  family 4記事(8ページ)はSHA`55c8a324`→`240e0723`へ更新。検証中にVoices 3V
  「AI hiring」B1のKey Phrase 4でラベル断片混入バグ(`<br>`がtextContentで
  消えregex誤マッチ)を発見し、unified.htmlのrowData()を修正(7行diff、
  記事本文・音声・segment sha256は無変更)。修正後26/26 PASS再確認。
UDR-blocking: なし。
UDR-deferred: なし(新規UDRなし。既存OPEN-166[Personalized News B1対象外]・
  Young Travelers試聴記録未確認は既知事項として引用のみ)。
Next Action: なし。Sheet貼付用最新URL表はDECISION_LOG.md
  `## USER-TEST-14-ARTICLE-FORMAT-RECHECK-01`4節参照(Sheet自体への反映は
  Fable/ユーザー側スコープ)。
詳細: docs/pm/RESULT_PACKET_14_ARTICLE_FORMAT_RECHECK_01.md

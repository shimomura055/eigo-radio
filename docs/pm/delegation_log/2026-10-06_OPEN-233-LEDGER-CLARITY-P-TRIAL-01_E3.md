## 管理ID
OPEN-233-LEDGER-CLARITY-P-TRIAL-01(委任_E3: 評価②記事のEntertainment性比較、決定論¥0+pairwise LLM判定 上限¥3)

## 性質/到達上限Status/禁止事項
性質: 評価(決定論+小額LLM pairwise)。到達上限: 比較表と所見(最終判定はFable)。禁止: 記事・台帳の変更/Production変更/SSOT編集/git/再生成/pairwise以外の有料API/¥3超過。並行委任E1/E2の出力(`eval/E1_*`、`eval/E2_*`)には触らない。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: pairwise上限¥3(2 call想定)。D-1: 実費を `eval/E3_cost.json` に記録。G-1/F-1: 該当なし。T-0: 簡略保存+checker。T-2/T-2追記(7-5): TTSなし。T-3: 対象外。

## ユーザー指示(原文、要点)
「②記事のエンターテイメント性: Factを明確にした結果、説明的になりすぎる/台帳の表現を逐語的にコピーする/ストーリー性・自然さ・テンポが落ちる/記事が硬くなる等が起きていないか比較する。従来のEntertainment品質を維持すること。」STOP条件「Entertainment品質に明確な悪化が見つかった」。

## 事前指定Read一覧
00d_eval_template.md ②欄、00c_before_evidence.md Entertainment基準値表、After/Before b1b article・ja_writer original/revision2、eval/ent_metrics.json。既存pairwise scriptがあれば流用。

## 事前指定Grep一覧+追記位置・更新位置の手順
1. 決定論表(¥0): 文数/語数/平均文長/TTR、JA逐語率(R0/R2)。2. pairwise(上限¥3): After vs Before b1b、順序入替2 call、4軸+総合、台帳非提示、記事名伏せ(X/Y)。`eval/E3_pairwise.json`保存。3. 逐語コピー所見(上位5件)。4. Fable抜粋(冒頭/中盤/結末3文)。5. 出力 `eval/E3_entertainment.md`(80行以内)。

## 実行コマンド全文
ja_copy_rate_p01.py(Before R2)、新規 tools/pairwise_p01.py、check_delegation_prompt.py(本ファイル)。

## SSOT追記文
なし。

## Git
なし。

## 報告(RESULT_PACKET項目、10行以内)
(1)基準照合 (2)pairwise結果とmodel (3)逐語コピー所見 (4)実費 (5)抜粋の所在 (6)T-0結果

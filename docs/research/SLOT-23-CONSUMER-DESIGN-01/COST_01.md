# COST_01 費用(実測ベース、API 0で算出)
実測(既存artifact `er019_output/**/kp_general_explanations.json` audit.calls、model=gpt-6-luna):
- Part 1解説 1 call: 3件=0.073〜0.097円、5件=0.125〜0.130円(output 1,424〜1,477 tok)。
- T1訳 1 call(5件): 0.030円(`part2_hr_evidence_01__run_r2/b1b/key_phrases/kp_source_sentence_ja.json` audit)。
=> Adv Part 1(5件)≈0.16円/記事(既存。変更なし)。

| 案 | Std追加費用/記事 | 備考 |
|---|---|---|
| ③ ハイライト+短い日本語意味 | 0円(Adv/Std共通) | 確定gloss再利用・LLMなし・音声不変 |
| Std② A(Part 1様式の文字のみ、解説LLMなし: 英語/本文中の意味/引用英文) | 0円 | 解説文なし。確定glossのみ |
| Std② B(③と同じ表示のみ) | 0円 | 最小 |
| Std② C(Adv Part 1と同一Prompt+T1) | 約0.16円(5件)。②のみ2件なら約0.08円 | StdはKP3+②2=5件分の解説を生成する場合 |
| ① KP音声 | 変更なし | 音声費用は不変(②③は文字のみ) |
- 量産単価(70円/記事セット)への影響: C最大+0.16円/Std記事=約+0.23%(Y/Z/Xの6経路が各Stdを持つため記事セット当たりの加算は経路によりStd1本分)。A/B/③は0。
- retry時: Cは失敗retry1回(既存`er003…`方式)=最大2倍(約0.32円)。

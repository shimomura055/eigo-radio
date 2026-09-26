# prompt_diff_advanced_v2_vs_standard.md

## 目的

AdvancedとStandardで語彙ルールの思想に差をつけないというユーザー方針の確認として、Production採用済みAdvanced v2(ADVANCED-VOCAB-V2-PRODUCTION-RESTORE-01)のTrial版本体(RULE_BLOCK_EN_V2、Production ADVANCED_VOCAB_RULE_V2_BLOCKと同内容)と、本Trialで使うStandard版プロンプトの差分を逐語で示す。

## 結論

- RULE_BLOCK_EN(語彙ルール本体、A/B/C/D例外・引用符内呼称の扱い・一般原則)は **"12,000" -> "6,000" の数字2箇所のみ**が差分。他は一字一句同一(以下diff参照、数字行以外の`-`/`+`行が無いことを目視確認できる)。

- TASK_TAIL(BORDERLINE参考範囲コメント)は **"10,000-12,000" -> "5,000-6,000" の数字1箇所のみ**が差分。

- DEVELOPER_MESSAGEのみ、テスト対象がCEFR B1(Advanced)ではなくCEFR A2(Standard)であるという**文脈上の呼称**を`CEFR B1 ("Advanced")` -> `CEFR A2 ("Standard")`と改めた(語彙ルール本体の思想・文言の変更ではなく、タスク説明文の対象レベル表記のみの変更)。


## 1. RULE_BLOCK_EN diff (Advanced v2 -> Standard)

```diff
--- RULE_BLOCK_EN (Advanced v2)
+++ RULE_BLOCK_EN (Standard)
@@ -1,8 +1,8 @@
 Candidate difficulty rule (draft, under evaluation):
 
-Words that rank below roughly the top 12,000 most frequent general English words are, in principle, candidates for simplification. This is NOT a mechanical ban list. As with the existing Standard-level vocabulary policy, simplification should be strongly preferred only when a simpler, natural expression exists without harming meaning or naturalness; it must not be forced when it would.
+Words that rank below roughly the top 6,000 most frequent general English words are, in principle, candidates for simplification. This is NOT a mechanical ban list. As with the existing Standard-level vocabulary policy, simplification should be strongly preferred only when a simpler, natural expression exists without harming meaning or naturalness; it must not be forced when it would.
 
-A word ranked beyond ~12,000 may still be KEPT (not simplified) if one of these applies:
+A word ranked beyond ~6,000 may still be KEPT (not simplified) if one of these applies:
 A. Its meaning can easily be guessed from an already-easy word it is built from (for example: "onstage" = on + stage, "wastewater" = waste + water, "understandable" = understand + -able). Do not exclude a word just because it LOOKS decomposable if the meaning cannot actually be guessed that way.
 B. It is a word that has become well established in Japanese, and its meaning can easily be guessed from its English pronunciation (for example: piano, curtain, privacy). Simply having a katakana spelling is not enough -- the word must be an established, commonly understood Japanese word, easily connected to its English sound.
 C. It is a proper noun (a person's name, a company or product name, a place name).
```

## 2. TASK_TAIL diff (Advanced v2/v1 -> Standard)

```diff
--- TASK_TAIL (Advanced v2)
+++ TASK_TAIL (Standard)
@@ -8,7 +8,7 @@
 [Candidate words -- rank below ~12,000, decide KEEP or SIMPLIFY for each]
 {candidates_block}
 
-[Reference only -- words ranked 10,000-12,000 (near the threshold), shown so you can calibrate the rule; these are NOT candidates and do not need a decision unless they also appear in the candidate list above]
+[Reference only -- words ranked 5,000-6,000 (near the threshold), shown so you can calibrate the rule; these are NOT candidates and do not need a decision unless they also appear in the candidate list above]
 {borderline_block}
 
 [Article]
```

## 3. DEVELOPER_MESSAGE diff (Advanced v2/v1 -> Standard、開示済み例外)

```diff
--- DEVELOPER_MESSAGE (Advanced v2)
+++ DEVELOPER_MESSAGE (Standard)
@@ -1 +1 @@
-You are an editor testing a candidate vocabulary-difficulty rule for CEFR B1 ("Advanced") level news articles written for Japanese adult English learners. This rule is a draft under evaluation, not yet approved. For the specific difficult words listed below, you decide word by word whether to keep the word or replace it with a simpler, natural alternative, following the rule exactly. You must not change anything else in the article.
+You are an editor testing a candidate vocabulary-difficulty rule for CEFR A2 ("Standard") level news articles written for Japanese adult English learners. This rule is a draft under evaluation, not yet approved. For the specific difficult words listed below, you decide word by word whether to keep the word or replace it with a simpler, natural alternative, following the rule exactly. You must not change anything else in the article.
```

## 4. Production側の思想差チェック(参考、本ファイルは§7の元データ)

Production Advanced v2 (`er003_v1_n3_01_advanced_adaptation_generate.py` ADVANCED_VOCAB_RULE_V2_BLOCK)とProduction Standard v5 (`er003_v1_n3_01_standard_a2_generate.py` STANDARD_A2_PROMPT_V5の語彙6行)の思想差はSTANDARD-VOCAB-ABCD-ALIGNMENT-TRIAL-01_REPORT.md §7参照(Production変更はしない、所見のみ)。

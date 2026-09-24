# NEWS-R25-PRODUCTION-METHOD-TRIAL-01 Fact確認(機械抽出+目視、Sonnet)

比較基準: `er015_output/news_iterative_entertainment_trial_01/original.md`(逐次修正TrialのOriginal、Web Search不使用・素材なし・同一テーマ)

機械抽出(`observation_machine.json`、`NUMBER_RE`=`\d+(?:[,\.]\d+)?`、`KEYWORDS`=`er015_news_original_baseline_repro_01.KEYWORDS`):

| 方式 | numbers_not_in_original | keywords_not_in_original |
|---|---|---|
| A | [] | [] |
| B | [] | [] |
| F1 | [] | [] |

目視確認:
- A/B/F1いずれも固有名詞・具体的数字を一切含まない(Original自体も同様、Source Note等の素材が入力に無いため)。
- 増えたのは比喩・言い換え・導入部の変更のみで、新しい事実主張(固有名詞・数字・出来事・因果)は追加されていない(R1〜R3と同型のパターン)。

**STOP条件(新規具体的事実3件以上、またはLedger裏付け不能な主張1件でも)に該当せず。Fact維持確認PASS。**

# spec_candidate_v2_ja.md

## 仕様候補の修正(ユーザー定義、逐語、ADVANCED-VOCAB-RULE-TRIAL-02)

基本原則: 一般英語頻度順位 約12,000位超は原則平易化候補。既存例外A(既知の
易しい語から意味を容易に推測できる語)/B(日本語として十分定着し音から
意味が分かる語)/C(固有名詞・引用符内の実際の呼称)/D(簡単な語へ置換する
と意味精度または英語の自然さを明確に損なう不可欠語)は維持。定型表現例外
なし。その上で:

- **Topic Core Word**: 記事テーマの根幹に関わり、その語を失うと「何に
  ついての記事なのか」「そのTopicを学ぶ意味」が弱くなる中核Topic語は
  12,000位超でもKEEP可。単なる「記事中によく出る語」ではない。判断基準:
  Topicそのものを指す語/記事理解・Topic理解の中心にある語/将来的に
  Topic Word等で意味解説する価値が高い語。**AIがTopic Core Wordと判定
  した場合、なぜその語が記事Topicの根幹なのかを具体的に説明させる**
  (schemaに`topic_core_justification`必須)。
- **Metaphor**: AI Writerが説明・Storytellingのために作った比喩表現は、
  「比喩を維持したい」「Storytelling上きれいだから」という理由だけでは
  KEEPしない。12,000位超で他の例外に該当しなければ原則平易化対象。
- 優先順位: **テーマの根幹に関わる語 ＞ 比喩表現 ＞ その他**(個別語の
  決め打ちではなく意味上の役割で判断)。
- 判定ラベル: `KEEP — topic core word` / `KEEP — predictable
  morphology/compound` / `KEEP — established Japanese loanword` /
  `KEEP — proper noun / quoted designation` / `KEEP — indispensable /
  natural replacement unavailable` / `SIMPLIFY` / `BORDERLINE`。Dを
  使う場合は「比喩維持」を理由にしていないことをreasoningで明示させる
  (schemaに`is_metaphor: bool`、`exception_used`を追加)。

## 実装上の注記(Sonnet、Prompt翻訳時)

- 判定ラベル文字列は既存schema enumとの一貫性のため "KEEP -- X"
  (ハイフン2つ)表記をそのまま踏襲した(ユーザー原文の "KEEP — X"
  [emダッシュ]と意味は同一、表記のみ既存v1/v2 enumスタイルに合わせた)。
- `exception_used` の値は "A"/"B"/"C"/"D"/"E"(Topic Core Word)/"none"
  とした(Eという記号自体はユーザー原文にはなく、Sonnetが実装上付与した
  内部ラベル。Prompt本文ではTopic Core Wordという名称で説明している)。

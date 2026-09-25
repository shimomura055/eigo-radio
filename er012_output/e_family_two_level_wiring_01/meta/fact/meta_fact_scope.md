# meta_fact_scope.md — NEWS-ADVANCED-A2-PRODUCTION-E2E-WIRING-01 delegation D6

## 目的
Meta「Museの電話代行」記事で、人間が処理していたのは「一部の通話(電話その
もの)」なのか、「1通話の中の一部分」なのかを、一次・元報道(Reuters)を
確認して一意に確定する。語彙Promptでの個別修正は行わない(事実確認として
解消し、Ledger/deviation checkの整合確認のみで扱う)。

## 取得元
- 一次報道: Reuters記事(marketscreener.comによる全文republish、
  2026-09-22T12:02:39-04:00公開、`https://r.jina.ai/`経由でReuters本文を
  直接取得。reuters.com自体・marketscreener.comへの直接curlはいずれも
  bot対策[Cloudflare/DataDome]でブロックされたため、reader proxy経由で
  republish記事の本文を取得した)。
  URL: https://www.marketscreener.com/news/meta-testing-a-human-concierge-for-its-new-personal-ai-agent-muse-ce785ad8de8cf025
  (既存Ledger`er017_output/news_entertainment_production_line_trial_01/
  ledger/verified_fact_ledger.txt`のMUSE-006〜018と同一URLの引用元)

## 一次情報からの直接引用
> "NEW YORK, Sept 22 (Reuters) - Meta has been testing a "human concierge"
> for its new personal AI assistant, Muse, which entails having human
> contractors quietly handle **some of the phone calls** placed via the
> digital agent, according to internal company posts seen by Reuters."

> "With the phone-calling feature, a Muse user can tell the agent to dial
> phone numbers for US businesses and talk with people on the other end to
> handle errands like booking haircuts, checking whether a store has an
> item in stock or getting quotes from different contractors."

> "Meta enabled the human concierge feature, also referred to as "human
> agent calls," for half of its employees last week to overcome those
> issues, according to the internal posts."

## 判定
一次報道(Reuters)は明確に **"some of the phone calls"**(=一部の通話その
ものを、丸ごと人間の契約スタッフが引き継いで処理する)という scope を
述べている。「1つの通話の中の一部分だけを人間が処理する('parts of a
call')」という記述はReuters本文中に存在しない。すなわち:
- 正しいscope: **「一部の通話(call単位)を人間が処理した」**
  ("some calls were handled by humans" 相当)
- 不正確なscope: 「通話の一部分(call内の一部分)を人間が処理した」
  ("parts of a call" 相当) — Sourceに支持されない

一意に確定できたため、STOP条件(「Meta事実範囲が確定不能」)には該当しない。

## 既存Ledgerとの整合確認
既存Ledger(`er017_output/.../verified_fact_ledger.txt`)のMUSE-006は
「Museが**一部の電話依頼**を訓練を受けた人間のエージェントへ引き渡し、その
人間が電話をかけて処理する」という文言であり、これは「一部の通話(call
単位)」のscopeと一致する。**Ledgerの文言修正は不要**(既存Ledgerは既に
一次情報と整合しており、OPEN-177で懸念されていた曖昧表現はLedger自体には
含まれていなかったことを確認した)。

## 日本語入力記事(ai_phone_revision2.md)との関係
入力の完成日本語記事(`docs/evidence/news_iterative_r2_adoption_2026-09-24/
articles/ai_phone_revision2.md`)9行目は「通話の一部をAIではなく、人間の
契約スタッフが担当していたのです」という表現であり、字面だけでは「一部の
通話」(call単位)・「通話の一部分」のいずれとも読める。Advanced Adaptation
のPromptはこの日本語記事本文をそのままFactとして扱う設計(Prompt個別修正
禁止、delegation D6)であるため、この日本語文自体は書き換えない。生成後の
Advanced/Standard英語本文がLedger(call単位のscope)と整合するかは、
`vfl01.run_deviation_check()`によって機械確認する(本ファイルはその際の
判定基準として使う一次情報の記録)。

## 費用
本fact確認はWeb取得(`curl`/`r.jina.ai`経由)のみで、OpenAI API呼び出しは
行っていない(¥0)。

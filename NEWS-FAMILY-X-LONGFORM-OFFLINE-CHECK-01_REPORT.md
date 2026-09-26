# NEWS-FAMILY-X-LONGFORM-OFFLINE-CHECK-01_REPORT.md

管理ID: NEWS-FAMILY-X-LONGFORM-OFFLINE-CHECK-01(Sonnet実行、2026-09-26)

## §1 目的・範囲

Family Xの3分割(Point構造廃止・3分割、NEWS-FAMILY-X-POINTLESS-TRIAL-01)
を検証する前段として、「Point構造なしで、News本文を十分な長さへ長文化
すること自体」に品質問題(水増し・情報密度低下・Fact逸脱・不自然さ)が
ないかを、**Offline(隔離・非Production経路)**で確認した。

- 本タスクはOffline本文生成→内容・長さ確認のみ。**3分割・Comment生成・
  scaffold・TTS・assemble・Family X E2E・Production lineへの投入・
  Production Prompt変更は一切実施していない**(禁止工程どおり未実施)。
- ここで生成したOffline本文(`offline_longform_meta_advanced.md`)は
  **Online Production Runへ流用しない**。本文はer015_output配下の
  隔離ディレクトリにのみ保存し、Family Aの本番article.md等へのコピー・
  参照配線は行っていない。
- Production module(`er003_v1_n3_01_advanced_adaptation_generate.py`等)
  は読んでいない・importもしていない・変更もしていない。Prompt文言は
  `er015_news_ja_to_en_adaptation_trial_01.py`(既存Trial資産、Fable固定の
  arm3=Natural English Adaptation文言)から逐語importして流用した。

## §2 方法

- 入力: Meta R2日本語記事(`docs/evidence/news_iterative_r2_adoption_
  2026-09-24/articles/ai_phone_revision2.md`、sha256照合済み)。
- Prompt: `er015_news_ja_to_en_adaptation_trial_01.py`のdeveloper +
  `COMMON_BLOCK` + `ARM3_BLOCK`(Natural English Adaptationレベル、
  contract suffix[`### `見出し2つ/`## In one line`]は元から含まれない)
  を無変更のまま逐語再利用し、長さ指示のみ追加した:
  > "Write the full story as continuous prose in 4–7 paragraphs, roughly
  > 260–340 words. No section headings, no bullet points, no summary
  > line. Do not pad: every sentence must carry information or move the
  > story forward."
  語彙ルールは追加していない(別管理ID扱い)。
- 生成: 1 call(gpt-5.6-luna, effort=high)。1回目で語数260–340語の範囲内
  (322語)に収まったため、再生成は行っていない(実施call数=1、上限2以内)。
- 新スクリプト: `er015_family_x_longform_offline_check_01.py`(新規、
  Production moduleの無変更import再利用のみ)。

## §3 本文全文

出力: `er015_output/family_x_longform_offline_check_01/
offline_longform_meta_advanced.md`

```
“Hello, I’m AI”—But a Human Was Working Behind the Phone Call

Letting AI make phone calls sounds like a useful service from the
future. People would only need to explain what they want. Then AI would
make the call for them. Meta was building a phone service like this.

The lead role belonged to Muse, Meta’s personal AI agent. Meta was
trying to give Muse a feature that could make phone calls on a user’s
behalf. But when people looked behind the stage, they found something
unexpected.

In tests carried out inside the company, contract workers—not AI—handled
some of the calls. Meta called these workers “human concierges.” In
other words, the sign out front said “AI phone service,” but people were
making some of the calls. The service looked like a show performed by AI
alone, but a human understudy was waiting backstage.

That is the most interesting part of this story. We may think an AI
phone call is truly impressive, only to learn that a person is behind
the curtain. It is like seeing a piano play by itself, then discovering
that another musician is hidden inside. Having people help is not
necessarily a bad thing. Humans can cover the parts that AI still
struggles with. That idea is understandable.

But phone calls can contain personal information. Meta employees raised
privacy concerns, including the possibility that call content could
leak outside the company. If people believed they were leaving a
conversation to AI, then learned that contract workers had actually
listened and responded, it would not be surprising if they were shocked.
According to internal posts reviewed by Reuters, Meta executives said
the company had put the feature on hold.

With an AI phone service, the important question may not be only
whether it can make a call. Who is speaking on the stage? And who is
behind the curtain? The more convenient the service, the more important
that explanation may be before people can trust it.
```

## §4 語数・長さ比較

| 版 | 語数 | 段落数 | 文数 | 平均文長(語) | FK grade(簡易) |
|---|---|---|---|---|---|
| 旧Family A Main Story(127語版、`er012_output/.../meta/b1b/article.md`の`###`前) | 127 | 4 | 9 | 14.11 | 6.36 |
| Trial arm3全文(`er015_output/news_ja_to_en_adaptation_trial_01/arms/arm3/output.md`、contract suffixなし・長さ指示なし) | 330 | 10 | 25 | 13.20 | 6.72 |
| 今回Offline版(`offline_longform_meta_advanced.md`) | 322 | 6 | 24 | 13.42 | 7.34 |

FK gradeは`er015_news_natural_advanced_standard_a2_trial_01.py`の
`_level_metrics()`(std libのみの簡易ヒューリスティック、textstat未導入の
ため参考値)を無変更のまま流用して計算。

## §5 Fact確認(詳細: `fact_check.md`)

- JA原文10段落すべてに対応する内容が本文6段落内に存在し、対応漏れなし。
- 新規追加された事実・数値・固有名詞・例示は検出されなかった。
- Reuters一次情報が確定した「一部の**通話**をcall単位で人間が処理した」
  scopeを、本文は **"some of the calls"** の表現で正しく反映している
  (参考arm3は"some **parts of** the calls"と誤scope寄りの表現だったが、
  今回のOffline版はこれを踏襲していない)。
- 唯一の観察: "Meta executives"(複数形)。原文「Metaの幹部は」は日本語の
  性質上単数/複数いずれとも解釈可能であり、これは事実の追加・改変ではなく
  訳語選択の観察として記録(逸脱ではない)。

## §6 情報密度/水増し(詳細: `density_check.md`)

- 総24文中、新情報23文、言い換え/繰り返し1文(JA原文自体が持つ反復構成
  [看板の言明→実態の反復]を保持したもので、本文が独自に追加した水増しでは
  ない)、装飾のみの文0件。
- **水増し文(情報を運ばず話を進めない文)はゼロ**。260–340語の長さ指示に
  対し、JA原文の情報をほぼ1文=1情報の密度で展開しており、段落統合
  (JA10段落→英語6段落、Natural Englishレベルで許可された操作)による
  情報の欠落・追加も確認されなかった。

## §7 Storytelling/自然さ

- R2の流れ(導入[便利な未来像]→舞台裏[意外な発覚]→比喩[ピアノの中の
  演奏者]→懸念[プライバシー]→停止[Reuters確認・一時停止]→問い[誰が
  話し誰が幕の後ろにいるか])は6段落すべてに保持されている。
- 目視所見: 不自然な文・過度に難解な語は検出されなかった(語彙ルール自体
  の判定は別管理ID扱いのため実施していない)。文長・構文とも127語版・
  arm3と近い水準(FK 6.36/6.72/7.34)で、長文化のみを理由とした急激な
  難化は見られない。

## §8 QCD

- Cost: 1 call、¥0.18(`er015_output/family_x_longform_offline_check_01/
  cost.json`、budget ¥5以内、`within_budget: true`)。
- 品質: §5-§7のとおりFact逸脱なし・水増しなし・Storytelling維持。
- Delivery: 実施call数1回(上限2回以内)。

## §9 Sonnet所見(Offline確認としての所見に限定、Production判定ではない)

- Point構造を使わずNews本文を260–340語へ長文化すること自体には、今回の
  1サンプル(Meta R2)においては、水増し・Fact逸脱・Storytelling崩壊の
  兆候は観察されなかった。
- 「Offline確認としての所見」としては **VALIDATED寄り**(1サンプルのみ、
  語彙ルール未判定、3分割後の実際のFamily X E2Eでの挙動は別途要確認)。
  Production採用可否・3分割以降の実施可否はFable/ユーザー判断に委ねる。

## §10 Fable評価
[Fable記入]

## §11 Fableの最終判定
[Fable記入]

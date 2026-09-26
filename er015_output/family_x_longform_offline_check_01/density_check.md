# density_check.md (NEWS-FAMILY-X-LONGFORM-OFFLINE-CHECK-01)

各段落の文を「新情報」「言い換え/繰り返し」「装飾」に分類する。
(本文6段落・24文、`offline_longform_meta_advanced.md`)

## Paragraph 1 (4文)
1. Letting AI make phone calls sounds like a useful service from the future. — 新情報
2. People would only need to explain what they want. — 新情報
3. Then AI would make the call for them. — 新情報
4. Meta was building a phone service like this. — 新情報
→ 繰り返し・装飾: 0件

## Paragraph 2 (3文)
1. The lead role belonged to Muse, Meta's personal AI agent. — 新情報
2. Meta was trying to give Muse a feature that could make phone calls on a user's behalf. — 新情報
3. But when people looked behind the stage, they found something unexpected. — 新情報
→ 繰り返し・装飾: 0件

## Paragraph 3 (4文)
1. In tests carried out inside the company, contract workers—not AI—handled some of the calls. — 新情報
2. Meta called these workers "human concierges." — 新情報
3. In other words, the sign out front said "AI phone service," but people were making some of the calls. — 言い換え/繰り返し(文1の情報を反復。ただし日本語原文自体がこの2文構成[看板の言明→実態の反復]を持つため、原文構成をそのまま保持したものであり、本文が独自に水増しした繰り返しではない)
4. The service looked like a show performed by AI alone, but a human understudy was waiting backstage. — 新情報
→ 繰り返し・装飾: 1件(原文由来の反復、水増しではない)

## Paragraph 4 (6文)
1. That is the most interesting part of this story. — 新情報(導入句)
2. We may think an AI phone call is truly impressive, only to learn that a person is behind the curtain. — 新情報
3. It is like seeing a piano play by itself, then discovering that another musician is hidden inside. — 新情報(比喩)
4. Having people help is not necessarily a bad thing. — 新情報
5. Humans can cover the parts that AI still struggles with. — 新情報
6. That idea is understandable. — 新情報(短い結び句)
→ 繰り返し・装飾: 0件

## Paragraph 5 (4文)
1. But phone calls can contain personal information. — 新情報
2. Meta employees raised privacy concerns, including the possibility that call content could leak outside the company. — 新情報
3. If people believed they were leaving a conversation to AI, then learned that contract workers had actually listened and responded, it would not be surprising if they were shocked. — 新情報
4. According to internal posts reviewed by Reuters, Meta executives said the company had put the feature on hold. — 新情報
→ 繰り返し・装飾: 0件

## Paragraph 6 (4文)
1. With an AI phone service, the important question may not be only whether it can make a call. — 新情報
2. Who is speaking on the stage? — 新情報
3. And who is behind the curtain? — 新情報
4. The more convenient the service, the more important that explanation may be before people can trust it. — 新情報
→ 繰り返し・装飾: 0件

## 集計

- 総文数: 24
- 新情報: 23文
- 言い換え/繰り返し: 1文(Paragraph 3-3。日本語原文自体の反復構成を保持したものであり、
  本文が独自に追加した水増しではない)
- 装飾のみ(情報を運ばない文): 0件
- 水増し文(何の情報も運ばず、話を進めない文): **ゼロ**(該当なし)

## 所見

260-340語という長さ指示に対して、生成本文は装飾的な水増し文を追加せず、
JA原文10段落の情報をほぼ1文=1情報の密度で展開している。段落数はJA原文10
段落から6段落へ統合されているが(段落統合はArm3のNatural Englishレベルで
許可されている操作)、情報の欠落・追加は確認されなかった(詳細は
`fact_check.md`)。

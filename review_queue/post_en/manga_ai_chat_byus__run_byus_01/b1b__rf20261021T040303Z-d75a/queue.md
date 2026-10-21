# Post-EN Risk Flagger Review Queue: manga_ai_chat_byus__run_byus_01 / b1b

- run_id: `rf20261021T040303Z-d75a`  status: **OK**
- article_sha256: `fb37a0913ef48c45b2dc0a310ba601ca9b0c996e395742244aef3390f163a6a6`  ledger_sha256: `bd7114bc10c27923e75389cadb8ab82ee51f7a3cdd97266e452a0e0a39c910a3`
- level: `b1b` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `deterministic_v2`  run_label: `FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01`
- sentences: 45  facts: 14  candidate issues: 2

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=1 cost_jpy=0.142112 model=gpt-6-luna
- luna A4: OK flags=2 cost_jpy=0.169872 model=gpt-6-luna
- gemini35fl A3: OK flags=0 cost_jpy=0.224528 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=0 cost_jpy=0.229888 model=gemini-3.5-flash-lite

## Issues

### s19  (confidence max 0.87)
- issue_id: `manga_ai_chat_byus__run_byus_01__b1b__fb37a091__rf20261021T040303Z-d75a__s19`
- sentence: For example, you can continue an official story in the service.
- before: In other words, you can enjoy not only asking, “What should we talk about next?” / but also, “What should happen next?”
- after: Or you can make your own story as a fan. / “What if that person showed up here?”
- detected_by: luna-A3(0.58), luna-A4(0.87)
- reason [その他]: 「continue an official story」は、原作の導入から新たな物語を展開するという説明を超えて、公式ストーリー自体の続編を提供する意味に読めるのではありませんか。
- reason [その他]: 「continue an official story」は公式ストーリー自体を続編として展開できる意味ではありませんか。Factでは会話を通じて新たな物語を展開するとされ、公式の正史が変更されるとは確認されていません。
- fact F05: Official Storyは、原作の世界観・キャラクター設定に沿った導入部分から、ユーザーがキャラクターと会話して新しい物語を展開する形式として説明されている。
  scope: byUsの公式提供ストーリー
  conditions: 原作の世界観とキャラクター設定を基礎とする
  date_or_period: 2026年10月19日時点の発表内容
  notes_for_writer: 会話後の展開をユーザーが楽しめる説明だが、公式作品の正史・原作設定が変更されるとは述べられていない。
- fact F14: 発表時点で読者が実際に物語へ参加できる範囲として、日本向け第1弾では実装済みの2作品・4キャラクターを使った会話展開が案内され、Official Storyの続きの展開やファンストーリーの創作・任意公開が提供機能として説明されている。
  scope: LINEマンガ版byUsの第1弾実装作品・キャラクター、および発表されたストーリー機能
  conditions: 利用にはLINEマンガアプリ、LINEログイン、アプリバージョン26.10.10以上が必要
  numeric_value: 2作品、4キャラクター (numeric_scope: 発表時点の第1弾実装範囲)
  date_or_period: 2026年10月19日発表時点
  notes_for_writer: 「読者が物語に参加」は会話を通じた展開やファンストーリーの創作として範囲を限定する。すべてのLINEマンガ作品で利用可能、または原作の正史を変更できるとは述べない。

### s38  (confidence max 0.31)
- issue_id: `manga_ai_chat_byus__run_byus_01__b1b__fb37a091__rf20261021T040303Z-d75a__s38`
- sentence: Until now, “If it were me, I’d do it this way” was something you could only say to yourself.
- before: “Taking part in a story” here means moving the story forward through conversation or making a story as a fan. / The fun of reading a work is joined by the fun of thinking up what happens next.
- after: With byUs, those words become a way into making a story. / What will you say to a character you love?
- detected_by: luna-A4(0.31)
- reason [不在断定]: 「could only say to yourself」はbyUs以前には自分の物語を作る手段がなかったという断定ではありませんか。Factでは既存のCharacter Chatがあり、byUsとの機能差として説明されているのは二次創作ストーリーの作りやすさです。
- fact F07: 既存の「キャラチャット」はキャラクターとの会話を楽しむ機能としてすでに提供されており、byUsは会話に加えて、より自由度の高い二次創作ストーリーを作れる点が異なると会社は説明している。
  scope: LINEマンガ内の既存機能と新サービスの機能差
  conditions: 会社発表は機能上の差異を説明している
  date_or_period: 2026年10月19日時点
  notes_for_writer: 「置き換え」ではなく、会社が発表した機能上の違いとして扱う。

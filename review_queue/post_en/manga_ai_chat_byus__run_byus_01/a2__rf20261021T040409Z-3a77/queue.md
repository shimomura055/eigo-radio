# Post-EN Risk Flagger Review Queue: manga_ai_chat_byus__run_byus_01 / a2

- run_id: `rf20261021T040409Z-3a77`  status: **OK**
- article_sha256: `50e75d8e2a892dbe0583616ddd8e72432771d941846099dcccfd87f250c52fb7`  ledger_sha256: `bd7114bc10c27923e75389cadb8ab82ee51f7a3cdd97266e452a0e0a39c910a3`
- level: `a2` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `deterministic_v2`  run_label: `FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01`
- sentences: 53  facts: 14  candidate issues: 4

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=0 cost_jpy=0.143936 model=gpt-6-luna
- luna A4: OK flags=4 cost_jpy=0.228656 model=gpt-6-luna
- gemini35fl A3: OK flags=0 cost_jpy=0.231472 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=0 cost_jpy=0.237232 model=gemini-3.5-flash-lite

## Issues

### s10  (confidence max 0.35)
- issue_id: `manga_ai_chat_byus__run_byus_01__a2__50e75d8e__rf20261021T040409Z-3a77__s10`
- sentence: The company that runs LINE Manga has announced a new service.
- before: What will happen to the two of them? / It may be a shame to keep those ideas only in your head.
- after: It is called “byUs,” an AI chat service for stories. / It is pronounced “bias.”
- detected_by: luna-A4(0.35)
- reason [その他]: 「the company that runs LINE Manga」という運営主体の説明は、台帳の「LINE Digital FrontierがLINEマンガ上のサービスを発表した」という記載だけでは確認できないのではありませんか。
- fact F01: LINE Digital Frontierは、LINEマンガでAIストーリーチャットサービス「byUs（バイアス）」をリリースしたと発表した。
  scope: LINEマンガ上のサービス
  date_or_period: 2026年10月19日
  notes_for_writer: 会社による一次発表。発表日とリリース日を区別する必要がある場合は、発表文が「リリースしました」としている点を明記する。

### s14  (confidence max 0.38)
- issue_id: `manga_ai_chat_byus__run_byus_01__a2__50e75d8e__rf20261021T040409Z-3a77__s14`
- sentence: You can also make your own stories based on their works.
- before: It is pronounced “bias.” / You can talk with characters you love.
- after: You can leave the reader’s seat and step onto the stage of making stories. / If you thought, “Can’t you already talk with characters?”
- detected_by: luna-A4(0.38)
- reason [その他]: 「their works」をもとに物語を作れるという範囲は、台帳が示す承認済み公式IPや原作キャラクターを基盤とした設定・関係性の創作より広く読めるのではありませんか。
- fact F02: byUsは、ユーザーが原作ストーリーの主人公となり、作品キャラクターとのAI会話を通じて新たなストーリーを作るサービスとして説明されている。
  scope: byUsのサービス説明
  conditions: 原作者が承認した公式IPを取り扱う
  date_or_period: 2026年10月19日時点の発表内容
  notes_for_writer: 「ユーザーが主人公となる」はサービスの説明。原作の公式ストーリーそのものを書き換える機能とは確認されていない。
- fact F03: LINE Digital Frontierは、byUsで扱うIPを原作者が承認した公式IPに限定すると説明している。LINEマンガのヘルプも、byUsに登場するオリジナル作品は原作作家との正式契約を通じ使用許可を得ているとしている。
  scope: byUsで扱う作品・キャラクター
  conditions: 原作者の承認が必要。ヘルプ記載では、登場するオリジナル作品は原作作家との正式契約による使用許可を取得
  date_or_period: 2026年10月19日発表および確認できたヘルプ記載
  notes_for_writer: 権利者の承認・許諾を前提とする事実として記述できる。
- fact F06: ファンストーリーでは、原作キャラクターを基盤にユーザーが新たな状況や関係性を設定して創作でき、作成したストーリーを他ユーザーに公開することも可能とされている。
  scope: byUsのユーザー創作機能
  conditions: 他ユーザーへの公開は可能とされるが、公開が必須とはされていない
  date_or_period: 2026年10月19日時点の発表内容
  notes_for_writer: ユーザーが設定できる範囲は発表文に記載された状況・関係性の設定。原作の公式展開への反映や、必ず公開される機能とは書かれていない。

### s23  (confidence max 0.78)
- issue_id: `manga_ai_chat_byus__run_byus_01__a2__50e75d8e__rf20261021T040409Z-3a77__s23`
- sentence: For example, you can continue an official story on the service.
- before: So, you can ask not only, “What should we talk about next?” / but also, “What should happen next?”
- after: Or you can make your own story as a fan. / “What if that person came here?”
- detected_by: luna-A4(0.78)
- reason [その他]: 「continue an official story」は、公式ストーリーそのものを続けたり正史を変更したりできる意味に読めますが、台帳の「会話を通じた新たな展開」とは異なるのではありませんか。
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

### s31  (confidence max 0.34)
- issue_id: `manga_ai_chat_byus__run_byus_01__a2__50e75d8e__rf20261021T040409Z-3a77__s31`
- sentence: You can keep them private, or let someone else read them.
- before: Or you may use that time to think up what happens next. / You can also publish your fan stories, if you want to.
- after: But things change when you make a story public. / “Will people understand this story?”
- detected_by: luna-A4(0.34)
- reason [その他]: 「keep them private」という非公開機能は、台帳にある「他ユーザーへの公開は必須ではない」という説明だけでは確認できないのではありませんか。
- fact F06: ファンストーリーでは、原作キャラクターを基盤にユーザーが新たな状況や関係性を設定して創作でき、作成したストーリーを他ユーザーに公開することも可能とされている。
  scope: byUsのユーザー創作機能
  conditions: 他ユーザーへの公開は可能とされるが、公開が必須とはされていない
  date_or_period: 2026年10月19日時点の発表内容
  notes_for_writer: ユーザーが設定できる範囲は発表文に記載された状況・関係性の設定。原作の公式展開への反映や、必ず公開される機能とは書かれていない。

# Post-EN Risk Flagger Review Queue: meta_waddle_world__run_fx4_01 / a2

- run_id: `rf20261029T132736Z-f1ff`  status: **OK**
- article_sha256: `3ee9f88244fcca7dfc45b92209b292c2e029e355de4f1de73ba5da154eeef032`  ledger_sha256: `39606fea729a3f82c751d0b80186a17dbe0bfd381ed4360d1daaf46da1f6e27f`
- level: `a2` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `deterministic_v2`  run_label: `FAMILY-X-SELECTED-4-ARTICLES-PRODUCTION-01`
- sentences: 43  facts: 12  candidate issues: 5

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=3 cost_jpy=0.180032 model=gpt-6-luna
- luna A4: OK flags=5 cost_jpy=0.220432 model=gpt-6-luna
- gemini35fl A3: OK flags=0 cost_jpy=0.216688 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=1 cost_jpy=0.250448 model=gemini-3.5-flash-lite

## Issues

### s1  (confidence max 0.35)
- issue_id: `meta_waddle_world__run_fx4_01__a2__3ee9f882__rf20261029T132736Z-f1ff__s1`
- sentence: # AI Pets Are Free.
- after: But Their Owners Still Have Only 24 Hours a Day / Work messages, news, videos, and that app you open without thinking.
- detected_by: luna-A3(0.35), luna-A4(0.31)
- reason [その他]: 見出しの「AI Pets Are Free」はAIペット全般が無料と読めますが、台帳が無料と確認しているのはWaddle Worldではありませんか。
- reason [主体対象入替]: 「AI Pets」と複数のAIペット全般を無料とする表現は、台帳が確認しているWaddle Worldの無料表示より範囲を広げていませんか。
- fact WW-07: App Storeの掲載価格は「Free」、Google Playの説明は「Free to play」と表示する。Waddle World公式サイトは、サブスクリプションがなく、アプリ内で得るスタンプは購入できないと説明している。
  scope: App Store・Google Playの掲載価格表示および製品公式サイトの説明
  conditions: 無料提供・サブスクリプションなし・スタンプ購入不可という記載の範囲。
  date_or_period: 2026-10-29確認時点
  notes_for_writer: 「無料」「サブスクなし」「スタンプは購入不可」は確認時点の公式掲載・説明として扱う。将来にわたる無料保証とはしない。
- fact WW-01: Meta Platforms, Inc.名義のアプリ「Waddle World: AI Pet Journal」が、フィリピン向けのApp StoreおよびGoogle Play掲載ページで確認できる。TechCrunchは、iOS・Androidでフィリピン向けに提供されたと報じた。
  scope: フィリピン向けのストア掲載。Appleの掲載情報はiPhone専用と表示。日本・米国を含む他地域での提供はこの事実の範囲に含めない。
  conditions: ストア掲載およびTechCrunchの報道に基づく。掲載・提供状況は確認時点のもの。
  date_or_period: 2026-10-27（Matt Navarra氏の投稿）〜2026-10-29（確認時点）
  notes_for_writer: 「フィリピン向けに提供」とする。iOS全端末対応とはせず、Apple掲載ページ上はiPhone専用と区別する。

### s15  (confidence max 0.24)
- issue_id: `meta_waddle_world__run_fx4_01__a2__3ee9f882__rf20261029T132736Z-f1ff__s15`
- sentence: This time, adults are asked if they want to welcome a pet.
- before: If you are thinking, “I’ll let my child play with it,” stop here. / Both app stores say users must be 18 or older.
- after: The age labels are a little confusing. / Apple says 18+, while Google Play gives it a 3+ content rating.
- detected_by: luna-A4(0.24)
- reason [その他]: 「adults are asked」と、アプリ内で成人にペットを迎えるか尋ねる事実は、台帳では確認できないのではありませんか。

### s32  (confidence max 0.4)
- issue_id: `meta_waddle_world__run_fx4_01__a2__3ee9f882__rf20261029T132736Z-f1ff__s32`
- sentence: At the time of writing, no one had said when it would be available in Japan or other places.
- before: It may matter more if they want to make room for one during the gaps in a busy day. / Still, it is too soon to get excited about future predictions.
- after: TechCrunch has suggested it may be an early step toward future devices like pets. / But it does not say that any specific link has been confirmed.
- detected_by: luna-A3(0.4), luna-A4(0.38)
- reason [不在断定]: 「no one had said」は誰も時期を示していないとの断定ですが、台帳で確認できるのはTechCrunchの記事掲載時点で他地域への提供時期が示されていないことだけではありませんか。
- reason [不在断定]: 「no one had said」と誰も時期を示していないと断定する表現は、TechCrunch記事掲載時点で他地域への提供時期が示されていないという台帳の範囲を超えていませんか。
- fact WW-09: TechCrunchは、Waddle Worldのより広い地域での提供についてMetaに問い合わせたと報じたが、記事掲載時点で他地域への提供時期は示していない。
  scope: TechCrunch記事で報じられたMetaへの問い合わせと掲載内容
  conditions: 記事掲載時点での情報。後日の発表の有無は含まない。
  date_or_period: 2026-10-28記事掲載時点
  notes_for_writer: 「日本・米国への展開計画は未確認／公表されていない」とする。「展開しない」とは書かない。

### s33  (confidence max 0.5)
- issue_id: `meta_waddle_world__run_fx4_01__a2__3ee9f882__rf20261029T132736Z-f1ff__s33`
- sentence: TechCrunch has suggested it may be an early step toward future devices like pets.
- before: Still, it is too soon to get excited about future predictions. / At the time of writing, no one had said when it would be available in Japan or other places.
- after: But it does not say that any specific link has been confirmed. / We still do not know if it will become a craze like Tamagotchi.
- detected_by: luna-A3(0.3), luna-A4(0.32), gemini35fl-A4(0.5)
- reason [その他]: 「future devices like pets」は対象を広く示していますが、台帳が記すTechCrunchの見立てはMuse搭載のペット型端末の先駆けとなる可能性ではありませんか。
- reason [その他]: 「an early step toward future devices」と具体的な製品上のつながりを示すような表現は、TechCrunchが可能性を示したにとどまり具体的関連は確認していないという台帳より強く読めませんか。
- reason [その他]: TechCrunchの報道内容（Muse搭載ペット型端末の先駆けとなる可能性）と、「future devices like pets」という表現に齟齬や拡大解釈はありませんか？
- fact WW-12: TechCrunchはWaddle Worldについて、MetaのMuse搭載ペット型端末の先駆けとなる可能性を示した。一方、記事は可能性として記述しており、Waddle WorldとMuse Charmの具体的な技術・製品上の関連を確認したとは述べていない。
  scope: TechCrunchによるWaddle Worldの報道・見立て
  conditions: 記者による可能性の提示であり、Metaによる公式発表ではない。
  date_or_period: 2026-10-28
  notes_for_writer: 「先駆けになる可能性」はTechCrunchの推測として帰属を明示する。アプリがブームになる、Muse Charmの前段階として開発された、などの確定表現を裏付ける事実はこの資料から得られない。

### s35  (confidence max 0.22)
- issue_id: `meta_waddle_world__run_fx4_01__a2__3ee9f882__rf20261029T132736Z-f1ff__s35`
- sentence: We still do not know if it will become a craze like Tamagotchi.
- before: TechCrunch has suggested it may be an early step toward future devices like pets. / But it does not say that any specific link has been confirmed.
- after: Will “It’s free, so I’ll try it” turn into “I want to see this pet for a little while today, too”? / A place to try it out and a seat kept for it every day are different.
- detected_by: luna-A4(0.22)
- reason [不在断定]: 「We still do not know」と人気化するかどうかをめぐる知識の不在を述べる根拠は、台帳には見当たらないのではありませんか。

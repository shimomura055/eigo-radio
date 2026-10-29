# Post-EN Risk Flagger Review Queue: meta_waddle_world__run_fx4_01 / b1b

- run_id: `rf20261029T132605Z-a900`  status: **OK**
- article_sha256: `345a0e14fcf67a754ff580748bfb61a651c7dc93696bf5fd350892b9e8dca373`  ledger_sha256: `39606fea729a3f82c751d0b80186a17dbe0bfd381ed4360d1daaf46da1f6e27f`
- level: `b1b` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `deterministic_v2`  run_label: `FAMILY-X-SELECTED-4-ARTICLES-PRODUCTION-01`
- sentences: 41  facts: 12  candidate issues: 2

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=2 cost_jpy=0.18752 model=gpt-6-luna
- luna A4: OK flags=1 cost_jpy=0.14968 model=gpt-6-luna
- gemini35fl A3: OK flags=0 cost_jpy=0.216352 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=0 cost_jpy=0.222112 model=gemini-3.5-flash-lite

## Issues

### s1  (confidence max 0.82)
- issue_id: `meta_waddle_world__run_fx4_01__b1b__345a0e14__rf20261029T132605Z-a900__s1`
- sentence: # AI Pets Are Free.
- after: But Their Owners Still Have Only 24 Hours a Day / Work messages, news, videos, and that app you keep opening without thinking.
- detected_by: luna-A3(0.82), luna-A4(0.4)
- reason [主体対象入替]: 「AI Pets Are Free」は、Waddle Worldの無料表示だけを根拠にAIペット全般が無料だと述べているのではありませんか。
- reason [その他]: 「AI Pets」という複数全般への断定は、台帳で無料と確認されている「Waddle World」の範囲を超えていませんか
- fact WW-07: App Storeの掲載価格は「Free」、Google Playの説明は「Free to play」と表示する。Waddle World公式サイトは、サブスクリプションがなく、アプリ内で得るスタンプは購入できないと説明している。
  scope: App Store・Google Playの掲載価格表示および製品公式サイトの説明
  conditions: 無料提供・サブスクリプションなし・スタンプ購入不可という記載の範囲。
  date_or_period: 2026-10-29確認時点
  notes_for_writer: 「無料」「サブスクなし」「スタンプは購入不可」は確認時点の公式掲載・説明として扱う。将来にわたる無料保証とはしない。

### s32  (confidence max 0.31)
- issue_id: `meta_waddle_world__run_fx4_01__b1b__345a0e14__rf20261029T132605Z-a900__s32`
- sentence: TechCrunch has suggested that it could be an early step toward future pet-like devices, but it does not say that any specific link has been confirmed.
- before: Still, it’s too early to get excited about predictions of the future. / When it will become available in Japan and other places had not been announced by the time of reporting.
- after: Whether it will become a craze on the scale of Tamagotchi is still an open question. / Will “It’s free, so I’ll try it” turn into “I want to see this pet for a little while today, too”?
- detected_by: luna-A3(0.31)
- reason [主体対象入替]: 「future pet-like devices」は、TechCrunchが可能性を示したMetaのMuse搭載ペット型端末より広い範囲を指しているのではありませんか。
- fact WW-12: TechCrunchはWaddle Worldについて、MetaのMuse搭載ペット型端末の先駆けとなる可能性を示した。一方、記事は可能性として記述しており、Waddle WorldとMuse Charmの具体的な技術・製品上の関連を確認したとは述べていない。
  scope: TechCrunchによるWaddle Worldの報道・見立て
  conditions: 記者による可能性の提示であり、Metaによる公式発表ではない。
  date_or_period: 2026-10-28
  notes_for_writer: 「先駆けになる可能性」はTechCrunchの推測として帰属を明示する。アプリがブームになる、Muse Charmの前段階として開発された、などの確定表現を裏付ける事実はこの資料から得られない。

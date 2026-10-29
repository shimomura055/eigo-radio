# Post-EN Risk Flagger Review Queue: meta_waddle_world__run_fx4_01 / a2

- run_id: `rf20261029T123643Z-9b53`  status: **OK**
- article_sha256: `187fcedd4e6c7fc471926eba6b1780a44f7077474bfcc2db10f8132b4642b459`  ledger_sha256: `39606fea729a3f82c751d0b80186a17dbe0bfd381ed4360d1daaf46da1f6e27f`
- level: `a2` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `deterministic_v2`  run_label: `FAMILY-X-SELECTED-4-ARTICLES-PRODUCTION-01`
- sentences: 45  facts: 12  candidate issues: 3

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=0 cost_jpy=0.121136 model=gpt-6-luna
- luna A4: OK flags=3 cost_jpy=0.183296 model=gpt-6-luna
- gemini35fl A3: OK flags=0 cost_jpy=0.423045 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=0 cost_jpy=0.224752 model=gemini-3.5-flash-lite

## Issues

### s13  (confidence max 0.29)
- issue_id: `meta_waddle_world__run_fx4_01__a2__187fcedd__rf20261029T123643Z-9b53__s13`
- sentence: Then the pet, which was listening just moments before, becomes the storyteller.
- before: It is an interesting way to divide the jobs. / Our job is to tell it what happened today.
- after: Some days feel too plain for us to write about. / But they can change when another storyteller tells them.
- detected_by: luna-A4(0.29)
- reason [その他]: 「was listening just moments before」は、音声またはテキストで出来事を伝える機能を超えて、ペットが直前まで聞き続けていたことを示す表現ではありませんか。
- fact WW-03: App StoreとGoogle Playの説明は、利用者が音声またはテキストで一日の出来事を伝え、ペットが自身の声による日記エントリーと手描き風の落書きを作る機能を説明している。
  scope: 公式ストア説明に記載された機能
  conditions: 音声入力またはテキスト入力が可能と記載。
  date_or_period: 2026-10-29確認時点
  notes_for_writer: Metaの製品説明として記述する。日記の生成を独立検証済みの性能評価として表現しない。

### s34  (confidence max 0.28)
- issue_id: `meta_waddle_world__run_fx4_01__a2__187fcedd__rf20261029T123643Z-9b53__s34`
- sentence: There is no promise that every result will be just what you hoped for.
- before: It feels more like opening a package when you do not know what is inside. / Of course, the official description alone cannot tell us if the writing or pictures are good.
- after: The interesting part is not a promise that every result will be good. / It is the idea of changing who tells the diary.
- detected_by: luna-A4(0.28)
- reason [不在断定]: 「There is no promise」と保証がないことを断定していますが、台帳は結果保証の有無を確認していないのではありませんか。
- fact WW-03: App StoreとGoogle Playの説明は、利用者が音声またはテキストで一日の出来事を伝え、ペットが自身の声による日記エントリーと手描き風の落書きを作る機能を説明している。
  scope: 公式ストア説明に記載された機能
  conditions: 音声入力またはテキスト入力が可能と記載。
  date_or_period: 2026-10-29確認時点
  notes_for_writer: Metaの製品説明として記述する。日記の生成を独立検証済みの性能評価として表現しない。

### s41  (confidence max 0.25)
- issue_id: `meta_waddle_world__run_fx4_01__a2__187fcedd__rf20261029T123643Z-9b53__s41`
- sentence: For now, the human only has to bring in the story of the day.
- before: The events stay the same, but the reason to open the page changes. / You are the main character, and your pet does the writing.
- after: ## In one line / Meta’s Waddle World is an app offered in the Philippines.
- detected_by: luna-A4(0.25)
- reason [その他]: 「only has to bring in the story」は人間に必要な操作がそれだけだと限定していますが、台帳は必要な操作の全範囲を示していないのではありませんか。
- fact WW-03: App StoreとGoogle Playの説明は、利用者が音声またはテキストで一日の出来事を伝え、ペットが自身の声による日記エントリーと手描き風の落書きを作る機能を説明している。
  scope: 公式ストア説明に記載された機能
  conditions: 音声入力またはテキスト入力が可能と記載。
  date_or_period: 2026-10-29確認時点
  notes_for_writer: Metaの製品説明として記述する。日記の生成を独立検証済みの性能評価として表現しない。

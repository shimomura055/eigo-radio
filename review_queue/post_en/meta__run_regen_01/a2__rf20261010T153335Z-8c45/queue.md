# Post-EN Risk Flagger Review Queue: meta__run_regen_01 / a2

- run_id: `rf20261010T153335Z-8c45`  status: **OK**
- article_sha256: `2f8307ab1b98060d67d018b22f8f929c91f63b7b16c7bc1ebd6cd4e5b5174b85`  ledger_sha256: `ea0ce587e605beeac8f02315ae4520899156393bbba2e059d99f45988b7c5f56`
- level: `a2` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `deterministic_v2`  run_label: `meta_regen_l3`
- sentences: 41  facts: 15  candidate issues: 6

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=1 cost_jpy=0.16576 model=gpt-6-luna
- luna A4: OK flags=5 cost_jpy=0.25888 model=gpt-6-luna
- gemini35fl A3: OK flags=0 cost_jpy=0.246544 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=0 cost_jpy=0.252304 model=gemini-3.5-flash-lite

## Issues

### s5  (confidence max 0.3)
- issue_id: `meta__run_regen_01__a2__2f8307ab__rf20261010T153335Z-8c45__s5`
- sentence: But the person taking the request at the other end was human.
- before: I was impressed: “AI can even make phone calls. / The future is here!”
- after: Wait—what a sudden change, from science fiction to a workplace drama. / Still, the main point is not, “So it was a person after all!”
- detected_by: luna-A4(0.3)
- reason [その他]: 「the person taking the request ... was human」はこの電話の相手が人間だったと特定していますが、台帳が示すのは電話の一部を人間が担当したことだけではありませんか。
- fact MUSE-HC-006: MetaはMuse経由の電話の一部について、AIではなく訓練を受けた人間の契約スタッフが電話をかけ、相手とのやり取りを完了させる「human concierge」「human agent calls」のテストを実施した。
  scope: Muse経由で発信された電話の一部
  conditions: Museから人間の訓練済みエージェントへ依頼が引き渡されるテスト条件
  date_or_period: 2026年9月中旬
  notes_for_writer: 全ての電話を人間が担当したとは書かない。「一部の電話」「テスト」と限定する。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))

### s21  (confidence max 0.3)
- issue_id: `meta__run_regen_01__a2__2f8307ab__rf20261010T153335Z-8c45__s21`
- sentence: It did not stop all calls through Muse.
- before: Let’s check the breaking-news caption once more. / What Meta pulled back was the human concierge feature.
- after: Canceling a whole show and pausing one part are different things. / So, is it wrong by itself to bring in a human helper?
- detected_by: luna-A4(0.3)
- reason [主体対象入替]: 「It did not stop all calls through Muse」はMuse経由の電話全体は停止していないと断定していますが、台帳が示すのは人間コンシェルジュ機能のロールバックだけではありませんか。
- fact MUSE-HC-012: MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。
  scope: Meta社内テストの人間コンシェルジュ機能
  conditions: 適切な開示なしで契約スタッフが電話を担当していたテスト
  date_or_period: 2026年9月22日まで
  notes_for_writer: 「サービス全体を停止した」とは書かない。ロールバック対象は人間コンシェルジュ機能として扱う。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))
- fact MUSE-HC-014: Metaは、電話機能について、商業者との改善を続け、準備が整い、適切な開示ができる場合にのみ公開展開すると広報担当者を通じて説明した。
  scope: Museの電話機能および人間コンシェルジュを含む可能性のある運用
  conditions: 準備完了および適切な開示が整うこと
  date_or_period: 2026年9月22日時点
  notes_for_writer: 公開済みの一般機能と、ロールバックされた人間コンシェルジュ実験を区別する。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))

### s24  (confidence max 0.2)
- issue_id: `meta__run_regen_01__a2__2f8307ab__rf20261010T153335Z-8c45__s24`
- sentence: Sometimes, passing the conversation to a person can help it move forward.
- before: Canceling a whole show and pausing one part are different things. / So, is it wrong by itself to bring in a human helper?
- after: But saying, “A person will take over from here,” is very different. / Quietly changing the cast behind the scenes is not the same.
- detected_by: luna-A4(0.2)
- reason [その他]: 「passing the conversation to a person can help it move forward」は人間への引き継ぎが会話を進める効果を持つと述べていますが、台帳にはその効果の記述がないのではありませんか。

### s30  (confidence max 0.2)
- issue_id: `meta__run_regen_01__a2__2f8307ab__rf20261010T153335Z-8c45__s30`
- sentence: Some people may speak or feel differently if they think they are talking to AI.
- before: You might say, “Ah, so that’s who it is!” / But you may not want that surprise in a conversation you are part of.
- after: Knowing they are talking to a person may change that. / Even if the request goes well, we cannot ignore the missing notice.
- detected_by: luna-A4(0.2)
- reason [その他]: 「speak or feel differently」は相手がAIだと思う場合に人の話し方や感じ方が変わる可能性を述べていますが、台帳にはその行動変化の根拠がないのではありませんか。

### s31  (confidence max 0.2)
- issue_id: `meta__run_regen_01__a2__2f8307ab__rf20261010T153335Z-8c45__s31`
- sentence: Knowing they are talking to a person may change that.
- before: But you may not want that surprise in a conversation you are part of. / Some people may speak or feel differently if they think they are talking to AI.
- after: Even if the request goes well, we cannot ignore the missing notice. / We cannot just say, “It all worked out in the end.”
- detected_by: luna-A4(0.2)
- reason [その他]: 「Knowing they are talking to a person may change that」は相手が人間だと知ることで話し方や感じ方が変わる可能性を述べていますが、台帳にはその変化の根拠がないのではありませんか。

### s41  (confidence max 0.7)
- issue_id: `meta__run_regen_01__a2__2f8307ab__rf20261010T153335Z-8c45__s41`
- sentence: Meta admitted it was a mistake to have contractors handle some Muse calls without telling the people they called.
- before: The person taking over does not have to be a secret guest. / ## In one line
- detected_by: luna-A3(0.7)
- reason [その他]: 「without telling the people they called」は、台帳の「適切な開示なし」よりも、相手にまったく伝えていなかったと断定する表現ではありませんか。
- fact MUSE-HC-006: MetaはMuse経由の電話の一部について、AIではなく訓練を受けた人間の契約スタッフが電話をかけ、相手とのやり取りを完了させる「human concierge」「human agent calls」のテストを実施した。
  scope: Muse経由で発信された電話の一部
  conditions: Museから人間の訓練済みエージェントへ依頼が引き渡されるテスト条件
  date_or_period: 2026年9月中旬
  notes_for_writer: 全ての電話を人間が担当したとは書かない。「一部の電話」「テスト」と限定する。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))
- fact MUSE-HC-012: MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。
  scope: Meta社内テストの人間コンシェルジュ機能
  conditions: 適切な開示なしで契約スタッフが電話を担当していたテスト
  date_or_period: 2026年9月22日まで
  notes_for_writer: 「サービス全体を停止した」とは書かない。ロールバック対象は人間コンシェルジュ機能として扱う。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))

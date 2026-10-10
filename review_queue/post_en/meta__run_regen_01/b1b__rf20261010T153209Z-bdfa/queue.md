# Post-EN Risk Flagger Review Queue: meta__run_regen_01 / b1b

- run_id: `rf20261010T153209Z-bdfa`  status: **OK**
- article_sha256: `c6318609e9df7ffed67d5ea6830964b91f4faa1c24b1103c8f0c6e263f6a6d51`  ledger_sha256: `ea0ce587e605beeac8f02315ae4520899156393bbba2e059d99f45988b7c5f56`
- level: `b1b` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `deterministic_v2`  run_label: `meta_regen_l3`
- sentences: 34  facts: 15  candidate issues: 4

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=2 cost_jpy=0.194992 model=gpt-6-luna
- luna A4: OK flags=4 cost_jpy=0.236512 model=gpt-6-luna
- gemini35fl A3: OK flags=0 cost_jpy=0.239872 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=0 cost_jpy=0.245632 model=gemini-3.5-flash-lite

## Issues

### s5  (confidence max 0.3)
- issue_id: `meta__run_regen_01__b1b__c6318609__rf20261010T153209Z-bdfa__s5`
- sentence: But the person handling the request on the other end of the line was human.
- before: I was impressed: “AI can even make phone calls. / The future is here!”
- after: Wait—what a sudden change of genre, from science fiction to a workplace drama. / Still, the heart of this story is not “So it was a human after all!”
- detected_by: luna-A4(0.3)
- reason [主体対象入替]: 「相手側で依頼を処理した人」という表現は、台帳が示す「電話をかけてやり取りを完了させた契約スタッフ」と役割や位置を取り違えていませんか。
- fact MUSE-HC-006: MetaはMuse経由の電話の一部について、AIではなく訓練を受けた人間の契約スタッフが電話をかけ、相手とのやり取りを完了させる「human concierge」「human agent calls」のテストを実施した。
  scope: Muse経由で発信された電話の一部
  conditions: Museから人間の訓練済みエージェントへ依頼が引き渡されるテスト条件
  date_or_period: 2026年9月中旬
  notes_for_writer: 全ての電話を人間が担当したとは書かない。「一部の電話」「テスト」と限定する。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))

### s18  (confidence max 0.34)
- issue_id: `meta__run_regen_01__b1b__c6318609__rf20261010T153209Z-bdfa__s18`
- sentence: They did not stop all calls through Muse.
- before: Let’s check the breaking-news caption once more. / What they pulled back was the human concierge feature.
- after: Canceling an entire show and pausing one segment are two different things. / So, is it bad in itself to bring in a human helper?
- detected_by: luna-A3(0.34), luna-A4(0.3)
- reason [不在断定]: 「They did not stop all calls through Muse」は、ロールバック対象が人間コンシェルジュ機能だったという事実だけでは他の電話が継続したことまでは確認できませんが、断定していませんか。
- reason [不在断定]: 「Muse経由の通話は止めていない」という断定は、台帳にある「人間コンシェルジュ機能をロールバックした」という情報だけでは確認できない運用状況まで述べていませんか。
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

### s26  (confidence max 0.25)
- issue_id: `meta__run_regen_01__b1b__c6318609__rf20261010T153209Z-bdfa__s26`
- sentence: Some people may choose their words or feel differently when they think they are talking to AI than when they know they are talking to a person.
- before: when a mysterious person is revealed. / But you may not want a surprise reveal in a conversation you are part of.
- after: Even if the request is handled without a problem, that does not mean the disclosure issue can be brushed aside with “it all worked out in the end.” / That was exactly the point Meta itself admitted it had got wrong.
- detected_by: luna-A4(0.25)
- reason [その他]: 「AIか人間かによって人々の言葉や感じ方が変わる」という一般化は、台帳に裏付けがない内容ではありませんか。

### s34  (confidence max 0.35)
- issue_id: `meta__run_regen_01__b1b__c6318609__rf20261010T153209Z-bdfa__s34`
- sentence: Meta admitted it was a mistake to have contractors handle some Muse calls without telling the people they called.
- before: The person taking over does not have to be a secret guest. / ## In one line
- detected_by: luna-A3(0.32), luna-A4(0.35)
- reason [その他]: 「without telling the people they called」は、事実にある「without proper disclosure」より開示の相手を電話の相手と特定していますが、その点まで確認できていますか。
- reason [その他]: 「電話をかけた相手に知らせなかった」という表現は、台帳の「適切な開示なし」よりも、開示の対象と内容を具体的に断定していませんか。
- fact MUSE-HC-012: MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。
  scope: Meta社内テストの人間コンシェルジュ機能
  conditions: 適切な開示なしで契約スタッフが電話を担当していたテスト
  date_or_period: 2026年9月22日まで
  notes_for_writer: 「サービス全体を停止した」とは書かない。ロールバック対象は人間コンシェルジュ機能として扱う。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))

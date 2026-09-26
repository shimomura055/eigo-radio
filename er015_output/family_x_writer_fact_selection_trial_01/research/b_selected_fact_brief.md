# b_selected_fact_brief.md

## Storyline(事前選定)
「AI電話の裏で人間が電話していた」(開示問題・プライバシー懸念・機能一時停止という結末を持つ1本のStoryline)。

## Full Ledger Fact数: 18件 / 選定数: 7件

## 選定Fact(理由付き)
### MUSE-003
選定理由: Museの電話機能が具体的に何をする機能か(前提)を示す。これが無いと「電話の裏に人間」という驚きの対象が読者に伝わらない。

[VERIFIED] MUSE-003: Reutersは、Museの電話機能について、利用者が米国の事業者へ電話をかけさせ、ヘアカットの予約、店舗在庫の確認、複数の業者からの見積もり取得などを依頼できると報じた。 ([marketscreener.com](https://www.marketscreener.com/news/meta-testing-a-human-concierge-for-its-new-personal-ai-agent-muse-ce785ad8de8cf025))
  scope: 米国の事業者への発信
  conditions: Museの電話機能が利用可能なユーザー・テスト対象者
  date_or_period: 2026年9月中旬時点
  notes_for_writer: 対象地域は米国の事業者。日本など他地域への提供を示す事実ではない。

### MUSE-006
選定理由: Storylineの核となる事実そのもの(一部の電話依頼を人間のエージェントが引き継いで処理していた)。

[VERIFIED] MUSE-006: Metaは、Museが一部の電話依頼を訓練を受けた人間のエージェントへ引き渡し、その人間が電話をかけて処理する「human concierge」または「human agent calls」のテストを実施した。 ([marketscreener.com](https://www.marketscreener.com/news/meta-testing-a-human-concierge-for-its-new-personal-ai-agent-muse-ce785ad8de8cf025))
  scope: Meta内部の電話機能テスト
  conditions: Museが電話依頼を人間の訓練済みエージェントへ引き渡した場合
  date_or_period: 2026年9月中旬
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 「AIの電話が常に人間だった」とは書かず、「一部の依頼を人間が処理する実験」と限定する。

### MUSE-007
選定理由: 「ごく一部の実験」ではなく従業員の約半数に有効化された規模であったことを示し、話の実在感・スケール感を支える。

[VERIFIED] MUSE-007: Reutersによると、人間コンシェルジュ機能は2026年9月中旬、Meta従業員の約半数を対象に有効化された。参加を望まない従業員向けにオプトアウト用のグループも設けられた。 ([marketscreener.com](https://www.marketscreener.com/news/meta-testing-a-human-concierge-for-its-new-personal-ai-agent-muse-ce785ad8de8cf025))
  scope: Meta従業員
  conditions: 社内テストへの参加対象者。希望者はオプトアウト可能
  numeric_value: 約50% (numeric_scope: Meta従業員のうち人間コンシェルジュ機能を有効化された割合)
  date_or_period: 2026年9月中旬の1週間前後
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 「Metaの全ユーザーの半数」ではなく、「Meta従業員の約半数」と明記する。

### MUSE-008
選定理由: なぜ人間が裏で電話するようになったか(AIだと分かると切られる問題)という「理由」を示し、単なる暴露で終わらせず因果を持たせる。

[VERIFIED] MUSE-008: Reutersは、MuseがAIであると分かると電話の相手が通話を切る事例があり、Metaがこの問題への対応として人間コンシェルジュ機能を有効化したと報じた。 ([marketscreener.com](https://www.marketscreener.com/news/meta-testing-a-human-concierge-for-its-new-personal-ai-agent-muse-ce785ad8de8cf025))
  scope: Museの電話機能を試した従業員・通話相手
  conditions: 通話相手がAIだと認識した場合
  date_or_period: 2026年8月〜9月の内部テスト期間
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 個別事例と報道された問題であり、AI電話全体が常に切断されたとはしない。

### MUSE-009
選定理由: Storylineの核である「開示問題・プライバシー懸念」を直接構成する事実。

[VERIFIED] MUSE-009: Reutersによると、Meta従業員の一部は、人間の契約作業員が電話を処理することで、個人情報や機微情報がコールセンターの作業員へ意図せず共有される可能性を懸念した。 ([marketscreener.com](https://www.marketscreener.com/news/meta-testing-a-human-concierge-for-its-new-personal-ai-agent-muse-ce785ad8de8cf025))
  scope: Meta従業員の社内フィードバック
  conditions: Museの電話依頼が人間の契約作業員へ引き渡される場合
  date_or_period: 2026年9月の社内テスト時点
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 「情報漏えいが起きた」と断定せず、「漏えいの可能性を懸念した」とする。

### MUSE-010
選定理由: Storylineの結末(Meta幹部が問題を認め機能を一時停止した)。開示問題が実際にどう扱われたかを示す。

[VERIFIED] MUSE-010: Reutersは、Metaの副社長が、適切な開示なしに契約作業員による電話を開始したことは問題だったと認め、当該機能を一時的にロールバックしたと報じた。 ([marketscreener.com](https://www.marketscreener.com/news/meta-testing-a-human-concierge-for-its-new-personal-ai-agent-muse-ce785ad8de8cf025))
  scope: Meta内部テストの人間コンシェルジュ機能
  conditions: 適切な開示・プライバシー保護が整う前のテストに対する社内問題認識
  date_or_period: 2026年9月22日報道時点
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 2026年9月22日時点のReuters報道に基づくステータス。恒久停止とはしない。

### MUSE-018
選定理由: ガードレール事実。「一般ユーザー全員の通話に人間が紛れていた」という誇張・Fact driftを防ぐため、確認範囲が主に従業員向け内部テストであることを明示する必要がある。

[VERIFIED] MUSE-018: 確認できたReuters報道とMeta公式資料の範囲では、一般ユーザーが依頼した全電話、または特定の一般ユーザーの電話が実際に人間の契約作業員へ引き渡されたかどうかは確定できない。報道で明確に確認できる対象は、主としてMeta従業員向けの内部テストである。 ([marketscreener.com](https://www.marketscreener.com/news/meta-testing-a-human-concierge-for-its-new-personal-ai-agent-muse-ce785ad8de8cf025))
  scope: 一般ユーザーとMeta従業員の区別
  conditions: 公開されたReuters報道およびMeta公式発表に基づく確認範囲
  date_or_period: 2026年9月22日報道時点
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 「ユーザーが気づかないまま必ず人間が対応した」とは断定しない。

## 除外Fact(理由付き)
- MUSE-001: Museの発表自体(日時・展開地域)はStorylineの前提説明として必須ではない(電話機能の存在はMUSE-003で足りる)。
- MUSE-002: メール送信・旅行予約・交渉等の一般機能列挙は開示問題/プライバシー懸念のStorylineに不要な情報量。
- MUSE-004: 「2026年8月から従業員に試させ、公開後に段階展開」という内部タイムライン詳細は、開示問題の結論(MUSE-010)に対して必須ではない。
- MUSE-005: 通話後に記録・要約を返す設計は、プライバシー懸念(MUSE-009)と近いが、Storylineの核(人間が電話していたこと自体)への追加情報としては不要。
- MUSE-011: 人間処理時の成功率95〜98%という性能指標は、開示問題/プライバシー懸念のStorylineとは別の切り口(性能比較)であり、詰め込みを避けるため除外。
- MUSE-012: 人種に関する不適切発言の個別事例は、それ自体が別のStoryline(品質管理問題)であり、開示問題のStorylineに混ぜると焦点がぼやけるため除外。
- MUSE-013: Meta広報の説明(テスト目的・従業員の反応)は、開示問題のcore storylineに必須ではなくバランス情報のため除外(A条件[Full Ledger]では引き続き提示され、A/B比較の対象となる)。
- MUSE-014: 将来の一般公開方針(AMBIGUOUS、断定禁止)は、今回のStoryline(現時点で起きた開示問題)の結末には不要な将来情報。
- MUSE-015: Muse Secure VMという技術設計の詳細は、開示問題のStorylineには不要(除外例として仕様に明記されている項目)。
- MUSE-016: ダウンロード数(250万件超)は普及規模の指標であり、開示問題のStorylineとは無関係な情報量のため除外。
- MUSE-017: 10年前のFacebook Messenger「M」の逸話は興味深い文脈だが、今回の1本のStorylineに絞る上では必須ではないため除外。

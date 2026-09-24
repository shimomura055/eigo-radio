# NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01 REPORT (fix01: 補充検索・N記事続行)

管理ID: `NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01`(Fable修正指示1回目、Step1 STOPからの再開)

Production実装ではない。Writer Prompt(P7)・developer message・Revision指示・model/effortは
既存VALIDATED Trial(er015_news_iterative_entertainment_trial_02.py Article A)と完全同一。
4条件で完全同一。R3は生成していない。

---

## §1 前回Baseline確認(Step 0、前回委任で完了・再掲)

# Baseline確認(NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01, Step 0)

## 前回Baseline(条件2)の入力件数・形式(根拠付き)

- 根拠ファイル: `er015_news_iterative_entertainment_trial_02.py` MATERIAL_A定数(行94-99)、`docs/evidence/news_iterative_r2_adoption_2026-09-24/prompts.md` 2-B節(行41-62)
- Source数: 1件(URL: https://www.marketscreener.com/news/meta-testing-a-human-concierge-for-its-new-personal-ai-agent-muse-ce785ad8de8cf025)
- 文数: 2文(句点「。」区切り)
- 文字数: 209字
- 粒度: 元記事本文の要約(直接引用ではなく2〜3文への要約パラフレーズ)
- 形式: 段落形式のプレーンテキスト(箇条書きではない)、`[ニュース]`欄へ挿入

### 逐語(MATERIAL_A、条件2でそのまま再利用する)

```
Reuters(2026年9月22日、NEW YORK発)によると、Metaは個人向けAIエージェント「Muse」の電話代行機能について、一部の通話を人間の契約スタッフが裏で担当する「人間コンシェルジュ」の試験を社内で行っていたことが、Reutersが確認した社内投稿で判明した。従業員から通話内容の外部流出などプライバシー面の懸念が示され、Meta幹部はこの機能を一旦取りやめた(rolled back)と説明した。
```

## Prompt(P7)・Revision指示・model/effort・連鎖方式の特定

- Original Prompt(P7)本体: `er015_news_original_baseline_repro_01.py` R0_PROMPT定数(逐語、テーマ行のみ差し替え)
- テーマ行: `テーマ：MetaのAI電話代行が、通話の一部を裏で人間スタッフに担当させる実験を行っている`(trial02 THEME_LINE["A"]と同一)
- developer message: `あなたは日本語のニュースを分かりやすく面白く伝える書き手です。`
- R1指示(逐語): この記事を、事実関係は変えずに、もっとエンターテインメント性の高い記事に修正してください。
- R2指示(逐語): この記事を、事実関係は変えずに、さらにもっとエンターテインメント性の高い記事に修正してください。
- model: gpt-5.6-luna / effort: high
- 連鎖方式: previous_response_id(trial02 chain.json Article A: {"chain_method": "previous_response_id", "stages": [{"stage": "original", "response_id": "resp_04020df138cfa5d1006ab47ee74a4087d084bd71c730cfe519", "model": "gpt-5.6-luna"}, {"stage": "r1", "response_id": "resp_04020df138cfa5d1006ab47efb01e487d0970d151832e733bd", "model": "gpt-5.6-luna", "chain_method": "previous_response_id"}, {"stage": "r2", "response_id": "resp_04020df138cfa5d1006ab47f080abc87d0b978604a1444e679", "model": "gpt-5.6-luna", "chain_method": "previous_response_id"}, {"stage": "r3", "response_id": "resp_04020df138cfa5d1006ab47f14817487d097bb6c1f31dcd299", "model": "gpt-5.6-luna", "chain_method": "previous_response_id"}]})

## 判定

STOP該当なし。条件2はMATERIAL_Aを逐語再現することでBaselineを再現する。

---

## §2 Source一覧・4条件入力全文

### §2-1 Source収集結果(fix01委任: 補充検索2call追加)

目標10記事に対し、初回検索2 call(委任文01)+補充検索2 call(fix01委任、異なる語彙)を
実施したが、到達数は**8記事(目標10、到達8)**にとどまった。
補充検索(EXTRA_SEARCH_QUERIES)は以下の2クエリ:

- `Meta Muse "human concierge" contractors phone calls Reuters`
- `Meta Muse 電話 代行 人間 コンシェルジュ 契約スタッフ`

補充検索の結果、いずれのクエリでも`url_citation`形式の新規Source URLは0件
(`search_log.json`の`phase=extra_vocab_fix01`エントリ2件とも`sources_found`は空配列。
web_search自体は実行され、内部的な言い換えクエリも発行されたが、モデル出力に
URL付き引用が含まれなかったため、機械的な新規URL抽出は0件だった)。
委任文(fix01)の規定により、Nが10未満でもSTOPとせず、8記事のまま条件3・条件4を
『8記事(目標10、到達8)』として続行した。

初回検索で除外された候補(前回委任時点、参考): investing.comの1件が
reader proxy経由でも403 AbuseAlleviationErrorのため取得不能・対象外(既報告)。

### §2-2 Source一覧(8記事、URL・媒体・取得方法・要点)

- **S01** [MarketScreener(Reuters配信)](https://www.marketscreener.com/news/meta-testing-a-human-concierge-for-its-new-personal-ai-agent-muse-ce785ad8de8cf025) — 取得方法: reader_proxy(r.jina.ai) / 要点作成方法: reused_verbatim_trial02_MATERIAL_A / sha256: `74a3b8c2c95d8d4d1254812a40bf4da98ad57f4e9522f41e14e9ac0508cbda9e`
  - 要点: Reuters(2026年9月22日、NEW YORK発)によると、Metaは個人向けAIエージェント「Muse」の電話代行機能について、一部の通話を人間の契約スタッフが裏で担当する「人間コンシェルジュ」の試験を社内で行っていたことが、Reutersが確認した社内投稿で判明した。従業員から通話内容の外部流出などプライバシー面の懸念が示され、Meta幹部はこの機能を一旦取りやめた(rolled back)と説明した。
- **S02** [about.fb.com(Meta公式)](https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/) — 取得方法: direct / 要点作成方法: luna_summarize_effort_medium / sha256: `18b58df2a83e0cf417f40423361e77b2ca9044741b0d9d161879f884cf18d6b1`
  - 要点: Metaは、目標達成を支援し、提案やタスク実行を行う個人向けAIエージェント「Muse」を発表した。Museは専用の「Muse Secure VM」上で動作し、メール送信や旅行予約、ブラウザ操作などを行うほか、重要な操作の前に本人の承認を求め、監査履歴も表示する。米国でiOS、Android、muse.ai向けに展開され、年内には本人だけが鍵を持つ「Muse Confidential VM」も導入予定。
- **S03** [404 Media](https://www.404media.co/meta-tests-muse-ai-agent-calls-that-are-actually-made-by-humans-in-a-call-center/?utm_source=openai) — 取得方法: direct / 要点作成方法: luna_summarize_effort_medium / sha256: `2dddb08433630a2a8ada1e04cf59094c01f5f041030ded7af5e0a540dbd22194`
  - 要点: MetaのAIエージェント「Muse」は、飲食店の予約などを代行する電話機能を発表したが、実際には訓練を受けた人間の担当者が電話をかける仕組みもテストしている。社内では、利用者の依頼や機密情報が人間に共有されることや、人間が電話した事実を利用者に事前に知らせていなかったことへの懸念が出ている。Metaは、公開前に安全性やプライバシー保護、適切な開示を整えるとしている。
- **S04** [Meta's Muse AI calls businesses for you, sometimes with a human doing the talking | TechSpot](https://www.techspot.com/news/113957-meta-muse-ai-used-human-contractors-calls-including.html?utm_source=openai) — 取得方法: direct / 要点作成方法: luna_summarize_effort_medium / sha256: `170ca06f88a62b667ea97d83a22d6e9f7ec7b099de61c1e0d1505719cacd0304`
  - 要点: Metaは、個人向けAIエージェント「Muse」の通話機能で、AIの代わりに請負業者が企業へ電話する人間コンシェルジュを試験導入したが、明確な説明がなくプライバシー上の懸念が出たため、現在は撤回している。試験中には請負業者による人種差別的発言もあり、Metaは謝罪し、その担当者を同社のプロジェクトから外した。
- **S05** [Meta testing a 'human concierge' for its new personal AI agent, Muse - The Business Times](https://www.businesstimes.com.sg/companies-markets/telcos-media-tech/meta-testing-human-concierge-its-new-personal-ai-agent-muse?utm_source=openai) — 取得方法: direct / 要点作成方法: luna_summarize_effort_medium / sha256: `ecc979f2f4ccf30b557b51c6a2778f4a1493e2032adae805ce019c6d65f645f5`
  - 要点: Metaは、個人向けAIアシスタント「Muse」が電話をかける機能で、人間の契約作業員が一部の通話を代行する「人間コンシェルジュ」を試験していた。従業員から、通話中に機密情報が漏れる懸念や、人間作業員による差別的発言への指摘があり、Metaは適切な開示なしに試験を始めたとして機能をいったん停止した。
- **S06** [Meta let human contractors quietly place some of Muse's AI calls | ANOTHER News](https://anothernews.io/news/meta-muse-human-calls/?utm_source=openai) — 取得方法: direct / 要点作成方法: luna_summarize_effort_medium / sha256: `4ef5411a20c632fe4c4c4790284204d78a661ee37fab484a7ffcc972af08218e`
  - 要点: MetaのAIエージェント「Muse」が米国の事業者に電話する機能で、社内テスト中、一部の通話を人間の委託業者が密かに代行していたことが分かった。人間が通話すると成功率が95〜98％に上がる一方、個人情報の共有や不適切な発言への懸念が出たため、Metaは適切な開示なしに始めたテストをいったん撤回した。
- **S07** [Meta is testing human callers behind its Muse AI agent, Reuters reports](https://thenextweb.com/news/meta-muse-ai-agent-human-concierge-calls?utm_source=openai) — 取得方法: direct / 要点作成方法: luna_summarize_effort_medium / sha256: `c09fc5f70dd683dec1852aa9eb907754b50f5b673a420e5a018bcd1bd6df2f1d`
  - 要点: Metaは、AIエージェント「Muse」が美容院などに電話する機能で、一部の通話を請負業者の人間オペレーターが引き継ぐ「人間コンシェルジュ」を従業員向けに試験している。社内では機密情報がコールセンター業者に伝わる懸念も出ており、Metaは一般公開前に安全性やプライバシー保護策を整えるとしている。
- **S08** [Muse AI now hands over phone calls to human agents: Meta tests new feature in its personal assistant | Mint](https://www.livemint.com/ai/muse-ai-now-hands-over-phone-calls-to-human-agents-meta-tests-new-feature-in-its-personal-assistant-11790099365768.html?utm_source=openai) — 取得方法: direct / 要点作成方法: luna_summarize_effort_medium / sha256: `20ea928139a8f10b5f53042e9241113fc9d19b886c100b26b61d78b883ce7302`
  - 要点: Metaは、個人向けAIアシスタント「Muse」が一部の電話依頼を訓練を受けた人間の請負業者に引き継ぐ「ヒューマン・コンシェルジュ」機能を試験している。社内ではプライバシーへの懸念も出ており、Metaは一般公開前に安全性とプライバシー保護を改善し、適切な説明を行うとしている。

### §2-3 4条件の入力全文

差分メモ: 条件1は条件2(2文)のうち第1文のみ(140字)。条件2は209字・2文。条件3は8記事(目標10、到達8)・1886字。

#### 条件1(1記事分の中心要点のみ)
```
Reuters(2026年9月22日、NEW YORK発)によると、Metaは個人向けAIエージェント「Muse」の電話代行機能について、一部の通話を人間の契約スタッフが裏で担当する「人間コンシェルジュ」の試験を社内で行っていたことが、Reutersが確認した社内投稿で判明した。
```

#### 条件2(前回Baseline逐語再現)
```
Reuters(2026年9月22日、NEW YORK発)によると、Metaは個人向けAIエージェント「Muse」の電話代行機能について、一部の通話を人間の契約スタッフが裏で担当する「人間コンシェルジュ」の試験を社内で行っていたことが、Reutersが確認した社内投稿で判明した。従業員から通話内容の外部流出などプライバシー面の懸念が示され、Meta幹部はこの機能を一旦取りやめた(rolled back)と説明した。
```

#### 条件3(8記事要点、目標10・到達8)
```
[N記事(目標10、到達8)]
・(MarketScreener(Reuters配信)) Reuters(2026年9月22日、NEW YORK発)によると、Metaは個人向けAIエージェント「Muse」の電話代行機能について、一部の通話を人間の契約スタッフが裏で担当する「人間コンシェルジュ」の試験を社内で行っていたことが、Reutersが確認した社内投稿で判明した。従業員から通話内容の外部流出などプライバシー面の懸念が示され、Meta幹部はこの機能を一旦取りやめた(rolled back)と説明した。
・(about.fb.com(Meta公式)) Metaは、目標達成を支援し、提案やタスク実行を行う個人向けAIエージェント「Muse」を発表した。Museは専用の「Muse Secure VM」上で動作し、メール送信や旅行予約、ブラウザ操作などを行うほか、重要な操作の前に本人の承認を求め、監査履歴も表示する。米国でiOS、Android、muse.ai向けに展開され、年内には本人だけが鍵を持つ「Muse Confidential VM」も導入予定。
・(404 Media) MetaのAIエージェント「Muse」は、飲食店の予約などを代行する電話機能を発表したが、実際には訓練を受けた人間の担当者が電話をかける仕組みもテストしている。社内では、利用者の依頼や機密情報が人間に共有されることや、人間が電話した事実を利用者に事前に知らせていなかったことへの懸念が出ている。Metaは、公開前に安全性やプライバシー保護、適切な開示を整えるとしている。
・(Meta's Muse AI calls businesses for you, sometimes with a human doing the talking | TechSpot) Metaは、個人向けAIエージェント「Muse」の通話機能で、AIの代わりに請負業者が企業へ電話する人間コンシェルジュを試験導入したが、明確な説明がなくプライバシー上の懸念が出たため、現在は撤回している。試験中には請負業者による人種差別的発言もあり、Metaは謝罪し、その担当者を同社のプロジェクトから外した。
・(Meta testing a 'human concierge' for its new personal AI agent, Muse - The Business Times) Metaは、個人向けAIアシスタント「Muse」が電話をかける機能で、人間の契約作業員が一部の通話を代行する「人間コンシェルジュ」を試験していた。従業員から、通話中に機密情報が漏れる懸念や、人間作業員による差別的発言への指摘があり、Metaは適切な開示なしに試験を始めたとして機能をいったん停止した。
・(Meta let human contractors quietly place some of Muse's AI calls | ANOTHER News) MetaのAIエージェント「Muse」が米国の事業者に電話する機能で、社内テスト中、一部の通話を人間の委託業者が密かに代行していたことが分かった。人間が通話すると成功率が95〜98％に上がる一方、個人情報の共有や不適切な発言への懸念が出たため、Metaは適切な開示なしに始めたテストをいったん撤回した。
・(Meta is testing human callers behind its Muse AI agent, Reuters reports) Metaは、AIエージェント「Muse」が美容院などに電話する機能で、一部の通話を請負業者の人間オペレーターが引き継ぐ「人間コンシェルジュ」を従業員向けに試験している。社内では機密情報がコールセンター業者に伝わる懸念も出ており、Metaは一般公開前に安全性やプライバシー保護策を整えるとしている。
・(Muse AI now hands over phone calls to human agents: Meta tests new feature in its personal assistant | Mint) Metaは、個人向けAIアシスタント「Muse」が一部の電話依頼を訓練を受けた人間の請負業者に引き継ぐ「ヒューマン・コンシェルジュ」機能を試験している。社内ではプライバシーへの懸念も出ており、Metaは一般公開前に安全性とプライバシー保護を改善し、適切な説明を行うとしている。
```

---

## §3 条件4 Ledger全文・情報集合差

Ledger変換: model=gpt-5.6-luna / effort=medium / web_search_tool_used=None

別Source追加チェック(機械確認): allowed_ids(条件3と同一8記事)=['S01', 'S02', 'S03', 'S04', 'S05', 'S06', 'S07', 'S08'] / cited_ids=['S03', 'S04', 'S05', 'S07', 'S08'] / extra_ids_not_allowed=[] (空= 新規Source追加なし、no_new_source_added=True)

fact数(TRIAL_UNVERIFIEDブロック数): 18

情報集合差(機械抽出、観察事実のみ、Fable評価用):
```json
{
  "numbers_in_ledger_not_in_cond3": [
    "01",
    "02",
    "03",
    "04",
    "05",
    "06",
    "07",
    "08",
    "09",
    "11",
    "12",
    "13",
    "14",
    "15",
    "16",
    "17",
    "18"
  ],
  "numbers_in_cond3_not_in_ledger": [
    "22",
    "404"
  ],
  "proper_nouns_in_ledger_not_in_cond3": [],
  "proper_nouns_in_cond3_not_in_ledger": [
    "404 Media",
    "MarketScreener",
    "Reuters",
    "about.fb.com",
    "rolled back",
    "契約スタッフ"
  ],
  "fact_block_count_ledger": 18
}
```

Ledger全文(条件4入力、status: TRIAL_UNVERIFIED):
```
[TRIAL_UNVERIFIED] F01: Metaは、個人向けAIエージェント「Muse」の電話機能について、人間の請負業者が一部の電話を代わりにかける「human concierge」機能をテストしていた。 (出典: S05)
  scope: Museの電話機能に関する社内テスト
  conditions: 一部の電話
  date_or_period: 2026年9月
  numeric_value: null
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: null
  status: TRIAL_UNVERIFIED

[TRIAL_UNVERIFIED] F02: Museは、米国の企業に電話をかけ、散髪の予約、店舗在庫の確認、業者からの見積もり取得などを行う機能を提供していた。 (出典: S05)
  scope: 米国企業への電話機能
  conditions: ユーザーがMuseに依頼した場合
  date_or_period: Museの電話機能提供時
  numeric_value: null
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: null
  status: TRIAL_UNVERIFIED

[TRIAL_UNVERIFIED] F03: Metaの社内投稿では、Museが依頼を訓練を受けた人間のエージェントに引き渡し、そのエージェントが電話をかけて対応を完了できると説明されていた。 (出典: S03)
  scope: Museの社内テスト
  conditions: Museが依頼を人間エージェントに引き渡した場合
  date_or_period: 2026年9月
  numeric_value: null
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: null
  status: TRIAL_UNVERIFIED

[TRIAL_UNVERIFIED] F04: 人間エージェントによる電話機能は、Meta従業員の半数に対して有効化され、参加を望まない従業員向けにオプトアウトのグループが用意されていた。 (出典: S05)
  scope: Meta従業員を対象としたテスト
  conditions: 参加を望まない従業員はオプトアウト可能
  date_or_period: 2026年9月の前週
  numeric_value: Meta従業員の半数
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: null
  status: TRIAL_UNVERIFIED

[TRIAL_UNVERIFIED] F05: Metaは、電話を人間の請負業者に処理させるテストを、適切な開示なしに開始したことは誤りだったと認め、その機能を当面停止した。 (出典: S05)
  scope: Museの人間コンシェルジュ機能
  conditions: 適切な開示なしに開始されたテスト
  date_or_period: 2026年9月
  numeric_value: null
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 「当面停止」は記事中の説明に基づく表現
  status: TRIAL_UNVERIFIED

[TRIAL_UNVERIFIED] F06: Metaの副社長は、将来この電話機能を公開する際には、準備が整い、適切な開示が行われた場合にのみ展開すると述べた。 (出典: S05)
  scope: Museの電話機能の一般公開
  conditions: 準備と適切な開示が整った場合
  date_or_period: 将来の公開時
  numeric_value: null
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 公開済みであるとは記載されていない
  status: TRIAL_UNVERIFIED

[TRIAL_UNVERIFIED] F07: Museの人間コンシェルジュのテストについて、従業員から、電話の内容に含まれる機密情報がコールセンターの請負業者に意図せず共有される可能性があるとの懸念が出ていた。 (出典: S05)
  scope: Meta従業員による社内テストへの反応
  conditions: 人間の請負業者が電話を処理する場合
  date_or_period: 2026年9月
  numeric_value: null
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 懸念の表明であり、情報漏えいが発生したとの事実ではない
  status: TRIAL_UNVERIFIED

[TRIAL_UNVERIFIED] F08: Museにインターネットおよびケーブル事業者への料金交渉を依頼した従業員について、電話の記録に人間の請負業者が人種に関する差別的な発言をしたことが示された。 (出典: S04)
  scope: 料金交渉の電話
  conditions: 人間の請負業者が電話を担当した場合
  date_or_period: 2026年9月
  numeric_value: null
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 発言は電話記録に基づく記事の報告
  status: TRIAL_UNVERIFIED

[TRIAL_UNVERIFIED] F09: Metaは、差別的な発言をした人間エージェントが今後Metaのプロジェクトで勤務しないと述べ、該当する従業員に謝罪した。 (出典: S05)
  scope: F08で報告された電話への対応
  conditions: 人間エージェントによる差別的な発言
  date_or_period: 2026年9月
  numeric_value: null
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 対応方針として報告されている
  status: TRIAL_UNVERIFIED

[TRIAL_UNVERIFIED] F10: 社内テストでは、人間が電話をかける場合の成功率が95％から98％の範囲に上がる可能性が示され、AIだけで処理する電話より高かった。 (出典: S05)
  scope: Museの電話機能の社内テスト
  conditions: 人間が電話を担当する場合
  date_or_period: 2026年9月
  numeric_value: 95％〜98％
  causal_strength: CORRELATIONAL
  notes_for_writer: AIだけで処理する電話の具体的な成功率は本文にない
  status: TRIAL_UNVERIFIED

[TRIAL_UNVERIFIED] F11: Metaは、従業員によるテストの反応は「圧倒的に肯定的」だったと説明した。 (出典: S07)
  scope: Museの人間エージェント電話テスト
  conditions: Meta広報担当者による説明
  date_or_period: 2026年9月
  numeric_value: null
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: Meta側の説明として扱う
  status: TRIAL_UNVERIFIED

[TRIAL_UNVERIFIED] F12: Metaは、Museの電話機能について、従業員からのフィードバックを得て、一般公開前に安全性とプライバシー保護を実装・改善することがテストの目的だと説明した。 (出典: S03)
  scope: Museの社内テスト
  conditions: 一般公開前
  date_or_period: 2026年9月
  numeric_value: null
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: Meta広報担当者の説明
  status: TRIAL_UNVERIFIED

[TRIAL_UNVERIFIED] F13: Museの電話機能では、電話の後に記録と要約を返すと社内投稿で説明されていた。 (出典: S03)
  scope: Museの電話機能
  conditions: 電話が完了した場合
  date_or_period: 2026年9月
  numeric_value: null
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: S08は「詳細な要約と全文の会話記録」と説明している
  status: TRIAL_UNVERIFIED

[TRIAL_UNVERIFIED] F14: Metaは、Museの電話機能を2026年8月に従業員がテストし始め、その後、Museのユーザー向けに段階的に展開した。 (出典: S05)
  scope: Museの電話機能
  conditions: 従業員による社内テスト後
  date_or_period: 2026年8月以降
  numeric_value: null
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 一般公開の具体的な開始日は本文中で情報が一致していない
  status: TRIAL_UNVERIFIED

[TRIAL_UNVERIFIED] F15: Metaは、Museを2026年9月8日に開始した。 (出典: S04)
  scope: Muse
  conditions: null
  date_or_period: 2026年9月8日
  numeric_value: null
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: S04では「開始日」として記載されている
  status: TRIAL_UNVERIFIED

[TRIAL_UNVERIFIED] F16: Museは、メール送信、旅行の手配、買い物などをユーザーに代わって行うよう設計されている。 (出典: S05)
  scope: Museの機能
  conditions: ユーザーが依頼した場合
  date_or_period: Muse提供時
  numeric_value: null
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: null
  status: TRIAL_UNVERIFIED

[TRIAL_UNVERIFIED] F17: Metaは、Museについて、各エージェントが専用の仮想マシン上で動作し、パスワードなどの機密情報を別の安全な保管場所に置くと説明していた。 (出典: S05)
  scope: Museのセキュリティ設計
  conditions: Museの利用時
  date_or_period: Muse公開時
  numeric_value: null
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 人間の請負業者による電話処理とは別のセキュリティ説明
  status: TRIAL_UNVERIFIED

[TRIAL_UNVERIFIED] F18: Metaの広報担当者は、Museの電話機能について、販売業者と協力して改善を続け、準備と適切な開示が整うまで一般公開しないと述べた。 (出典: S08)
  scope: Museの電話機能の一般公開
  conditions: 準備と適切な開示が整った場合
  date_or_period: 将来の公開時
  numeric_value: null
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: Meta広報担当者の説明
  status: TRIAL_UNVERIFIED
```

---

## §4 Prompt・Revision指示全文・model/effort・連鎖方式

- model: gpt-5.6-luna / effort: high
- 連鎖方式: previous_response_id(trial02.call_fresh / call_with_previous_response_id、無変更import再利用)
- developer message(逐語): あなたは日本語のニュースを分かりやすく面白く伝える書き手です。
- R1指示(逐語): この記事を、事実関係は変えずに、もっとエンターテインメント性の高い記事に修正してください。
- R2指示(逐語): この記事を、事実関係は変えずに、さらにもっとエンターテインメント性の高い記事に修正してください。

Original Prompt本体(条件1の例、`[ニュース]`欄以外は4条件で完全同一):
```
以下のニュースを、友人に「これ、ちょっと面白くない？」と話すような読み物にしてください。

ニュースの中から、最も意外な事実ではなく、最も面白い「見方」を一つ選んでください。その見方に必要な事実だけを使い、ニュース全体を説明しようとしないでください。

語り口は自然で軽快にします。新聞、行政資料、学校教材のような文章にはしません。難しい内容は、短く簡単な日本語に言い換えてください。日本語を勉強している外国人が、音声で一度聞いて理解できる程度を目安にします。

遠い地域だけの特殊な話に見える場合は、読者の暮らしや、より大きな社会の変化とのつながりを一度だけ示してください。ただし、話を無理に広げる必要はありません。

事実関係は厳守し、架空の出来事や発言は加えません。

テーマ：MetaのAI電話代行が、通話の一部を裏で人間スタッフに担当させる実験を行っている

長さ：800～1000字

出力はタイトルと本文のみ。

[ニュース]
Reuters(2026年9月22日、NEW YORK発)によると、Metaは個人向けAIエージェント「Muse」の電話代行機能について、一部の通話を人間の契約スタッフが裏で担当する「人間コンシェルジュ」の試験を社内で行っていたことが、Reutersが確認した社内投稿で判明した。
```

---

## §5 各条件 Original/R1/R2全文・タイトル

タイトル一覧:
```json
{
  "cond1": {
    "original": "AIの代役は、人間でした　Metaが試した「電話の裏方」",
    "r1": "# AIに電話を任せたら、舞台裏から人間が出てきた",
    "r2": "# AIの電話に、隠しキャラとして人間がいた"
  },
  "cond2": {
    "original": "AIに電話を任せたら、受話器の向こうに人間がいた",
    "r1": "AIに電話を頼んだら、「中の人」が出てきた――Metaの奇妙な実験",
    "r2": "AIに電話を頼んだら、舞台裏から「人間」が登場した"
  },
  "cond3": {
    "original": "AIの電話、いちばん強かったのは「中の人」？",
    "r1": "# AIの電話だと思ったら、舞台裏に「中の人」がいた",
    "r2": "# 「AIに電話して」と頼んだら、受話器の向こうに人間がいた"
  },
  "cond4": {
    "original": "AIに電話して」と頼んだら、舞台裏から人間が出てきた",
    "r1": "# AIの電話代行、困ったら人間が「代役」で登場",
    "r2": "# AI電話のはずが、幕の裏から人間の助っ人が登場"
  }
}
```

### 条件1

#### 条件1 - original

AIの代役は、人間でした　Metaが試した「電話の裏方」

これ、ちょっと面白くないですか。

Metaが開発している、個人向けAIエージェント「Muse」。人の代わりに電話をしてくれる機能があります。たとえば、何かを確認したり、相手と話したり。名前だけ聞くと、AIが電話をかけて、最後まで全部やってくれそうです。

ところがMetaは、その電話の一部を、裏で人間が担当する試験を社内で行っていました。担当したのは、人間の契約スタッフです。Metaはこの仕組みを「人間コンシェルジュ」と呼んでいました。

つまり、AIの電話代行を試しているはずなのに、電話の向こうでは人間が出番を待っている。AIにとっての「代役」が、人間だったわけです。

舞台で主役がセリフを忘れたら、代役が出てくる。今回の仕組みは、少しそれに似ています。表ではAIが仕事をしているように見えても、難しい場面や、うまく進めにくい場面では、人間が支える。AIの未来というより、AIと人間が同じチームで電話をする未来を先に見せているようにも感じます。

もちろん、これはMetaが社内で行っていた試験です。Reutersは、社内の投稿を確認して、この事実を報じました。すべての通話を人間が担当していたわけでもありません。一部の通話だけです。

でも、ここにはAIサービスの面白い弱点が見えます。AIは文章を作るだけなら、かなり自然に見えることがあります。しかし電話では、相手の言葉を聞き、すぐ返し、話がそれたら戻し、細かな状況にも対応しなければなりません。画面の上の会話より、電話のほうがごまかしにくいのです。

AIが生活の中で電話まで任されるようになると、「相手は機械なのか、人間なのか」という境目も、だんだん見えにくくなります。今回の試験は、AIが人間を完全に置き換えた話ではありません。むしろ、AIを一人で働かせるには、まず人間の裏方が必要だった、という話なのです。

#### 条件1 - r1

# AIに電話を任せたら、舞台裏から人間が出てきた

これ、ちょっと映画みたいな話です。

表向きは、AIが電話をしている。ところが舞台裏では、人間のスタッフが受話器を持っている。Metaが、そんな仕組みを試していました。

Metaが開発しているのは、個人向けAIエージェント「Muse」です。電話代行の機能があり、AIが本人の代わりに電話をすることを想定しています。

ところが、その一部の通話を、人間の契約スタッフが担当する試験をMetaは社内で行っていました。Metaは、この人間の役割を「人間コンシェルジュ」と呼んでいます。

名前はAIなのに、裏方は人間。まるで、AIが主役の舞台に、いざという時の代役が用意されていたようです。

しかも、面白いのは「人間も使っていた」という点だけではありません。AIの電話代行を作るとき、必要なのはAIに声を出させることだけではない。電話の相手とやり取りする仕事を、最後まで安定して任せられるかどうかも問題になります。

画面の中なら、AIが少し変な返事をしても、読み直したり、やり直したりできます。でも電話は、その場で会話が続きます。返事を待ってくれるとは限りません。そこで人間が裏側に入れば、サービスは止まりにくくなります。少なくとも、今回の試験はそんな発想を感じさせます。

ただし、どんな通話を人間が担当したのか、どのタイミングで切り替わったのかまでは、このニュースでは分かりません。分かっているのは、一部の通話を人間の契約スタッフが担当する仕組みを、Metaが社内で試していたことです。

Reutersは、Metaの社内投稿を確認して、この事実を報じました。

AIが人間の仕事を代わる。そんな話はよく聞きます。でも今回は少し逆です。人間がAIの仕事を、こっそり支えていた。AIが生活の中で電話まで担当する時代には、未来の主役だけでなく、舞台裏の人間にも出番があるのかもしれません。

#### 条件1 - r2

# AIの電話に、隠しキャラとして人間がいた

「この電話、AIに任せておいて」

そんな未来が、もうすぐ来るのかと思ったら、電話の舞台裏に人間がいました。

Metaが開発している個人向けAIエージェント「Muse」には、電話代行の機能があります。人の代わりに、AIが電話をする仕組みです。

ところがMetaは、その一部の通話を、人間の契約スタッフが担当する試験を社内で行っていました。Metaがつけた名前は、「人間コンシェルジュ」。

AIの電話代行なのに、人間が登場する。しかも、表に出てくる主役ではありません。AIの後ろにひそむ、いわば“隠しキャラ”です。

イメージすると、AIが一人で演じるはずの電話劇に、実は人間の代役が待機している感じです。観客にはAIの舞台に見えても、舞台裏には別の役者がいる。今回の話の面白さは、ここにあります。

ただし、ここで分かっているのは、すべての電話を人間が担当していた、ということではありません。人間が受け持ったのは一部の通話です。どんな通話を人間に任せたのか、いつ切り替えたのかは、報道では明らかになっていません。

それでも、この試験はAIの実力を考えるうえで、少し意外な角度を見せています。AIサービスというと、機械が人間の仕事を丸ごと引き受ける姿を想像しがちです。けれど実際には、AIだけで走り出すのではなく、人間が後ろから支える形で試されることもある。

とくに電話は、文章を送るだけではありません。相手の言葉を聞き、その場で返事をし、会話を続けます。AIにとっては、なかなか逃げ場のない仕事です。だからこそ、表のAIと裏の人間という二重構造が生まれたのかもしれません。

Reutersは、Metaの社内投稿を確認し、この試験を報じました。

AIが人間の代わりに電話をする。そう思っていたら、今度は人間がAIの代わりをしていた。未来の主役はAIでも、その舞台を支える黒子は、まだ人間なのです。

### 条件2

#### 条件2 - original

AIに電話を任せたら、受話器の向こうに人間がいた

これ、ちょっと面白くないですか。AIに電話をかけてもらうつもりが、実はその一部を人間が担当していた、という話です。

米Metaは、個人向けAIエージェント「Muse」の電話代行機能で、社内向けの試験をしていました。Museは、利用者の代わりに電話をかけるAIです。たとえば、店やサービスに問い合わせる、といった仕事を任せるイメージです。

ところが、この試験では、すべてをAIだけに任せていませんでした。一部の通話では、AIの裏側で、人間の契約スタッフが対応していたのです。社内では、この仕組みを「人間コンシェルジュ」と呼んでいました。

つまり、画面や説明だけを見ると「AIが電話している」ように見えても、実際の通話の一部には人間が入っていた。AIの弱点を人間が支える、という考え方です。考えてみれば、かなり現実的です。電話は、相手の言い方が少し変わっただけで話が通じなくなったり、予想外の質問が飛んできたりします。AIにとっては、まだ難しい場面が多いのでしょう。

ただ、便利さの裏側には大きな問題もあります。Metaの従業員からは、通話内容が外部に流れる心配など、プライバシーへの懸念が出ました。電話の相手はAIと話しているつもりでも、実際には人間が聞いているかもしれない。そうなると、「誰が会話を聞いているのか」という、かなり基本的な問題が出てきます。

Metaの幹部は、この機能をいったん取りやめたと説明しました。

AIサービスでは、表に見える賢さだけでなく、裏で誰が、どこまで支えているのかも重要になりそうです。AIに仕事を任せる未来は、AIだけで動く未来とは限らない。むしろ最初は、人間がこっそり支える「人間つきAI」なのかもしれません。

#### 条件2 - r1

AIに電話を頼んだら、「中の人」が出てきた――Metaの奇妙な実験

ちょっと変な話です。AIに電話を任せたつもりなのに、電話の向こうで人間が話していたかもしれません。

米Metaは、個人向けAIエージェント「Muse」の電話代行機能で、社内向けの試験を行っていました。Museは、利用者の代わりに電話をかけるAIです。人間が電話をかける代わりに、AIが相手と話して用事を進める。そんなサービスを目指していました。

ところが、この試験には“中の人”がいました。

一部の通話では、AIの裏側で人間の契約スタッフが対応していたのです。Metaはこの仕組みを「人間コンシェルジュ」と呼んでいました。

言ってみれば、AIという看板を出した電話の舞台裏に、人間スタッフが待機していたわけです。AIがうまく話せないとき、人間がそっとバトンタッチする。AIの苦手なところを、人間の経験で埋める方法です。

たしかに、電話はAIにとって難しい仕事です。相手の話し方は毎回違いますし、予定外の質問も出てきます。文章を作るだけなら得意なAIでも、リアルタイムの会話では、思わぬところでつまずくことがあります。そこで人間が助ける、という発想自体は自然です。

ただし、問題はその人間が誰なのか、そして会話を誰が聞いているのかです。Metaの従業員からは、通話内容が外部に流れることなど、プライバシーへの心配が出ました。AIと話していると思っていた通話に、人間が関わっていたなら、利用者にとっては見過ごせない違いです。

Reutersが確認した社内投稿によると、Metaの幹部はこの機能をいったん取りやめたと説明しました。

AIサービスでは、表の画面だけを見ていても中身は分かりません。華やかなAIの裏で、人間が支えることはこれからもありそうです。でも、その“中の人”を利用者にどう伝えるか。AIの賢さより先に、そこが信頼の勝負になるのかもしれません。

#### 条件2 - r2

AIに電話を頼んだら、舞台裏から「人間」が登場した

もしAIに電話を頼んで、相手と話を進めてもらっている間に、画面の外で人間スタッフが受話器を握っていたら――。そんな、少しだけコントのような仕組みを、Metaが試していました。

米Metaが開発する個人向けAIエージェント「Muse」。利用者に代わって電話をかける機能の社内試験で、一部の通話を人間の契約スタッフが担当していたことが分かりました。AIだけで電話をしているように見えて、その裏では人間が会話を支えていたのです。

この仕組みの名前は、「人間コンシェルジュ」。

名前だけ聞くと、ホテルのロビーで何でも相談に乗ってくれる人を想像します。でも実際には、AIの舞台裏にいるスタッフです。AIが相手の話をうまく理解できないときや、予想外の流れになったときに、人間が対応する。いわば、AIの着ぐるみに人間が入っているようなものです。

なぜ、そんな方法を試すのでしょうか。電話は、AIにとってなかなか手ごわい仕事だからです。相手の話し方は毎回違います。質問が急に変わることもあります。文章を作るのが得意なAIでも、リアルタイムの会話では、思わぬところで立ち止まるかもしれません。そこで人間が助ければ、電話代行はかなりスムーズになります。

ただ、AIの着ぐるみには、笑って済ませられない問題もありました。Metaの従業員から、通話内容が外部に流れることなど、プライバシーへの心配が出たのです。電話の向こうに誰がいるのか。AIなのか、人間なのか。それが分からないままだと、安心して話せない人もいるでしょう。

Reutersが確認した社内投稿によると、Metaの幹部はこの機能をいったん取りやめたと説明しました。

AIの世界では、「賢く見えること」だけでなく、「裏で誰が動いているか」も大事になりそうです。未来の電話は、AIが一人で働くのではなく、人間がこっそり助ける二人三脚になるのかもしれません。問題は、その相棒の存在を、いつ、どう知らせるかです。

### 条件3

#### 条件3 - original

AIの電話、いちばん強かったのは「中の人」？

これ、AIのニュースなのに、いちばん頼りになったのが人間だった――という、少し舞台裏っぽい話です。

Metaが発表した個人向けAIエージェント「Muse」には、店に電話をかける機能があります。たとえば、飲食店や美容院に連絡して、予約のような用事を進める機能です。AIが会話して、最後までやってくれる。そう聞くと、ずいぶん近未来らしく感じます。

ところが社内テストでは、電話の一部を、訓練を受けた契約スタッフが代わりにかけていました。表からはAIの電話に見えても、舞台の裏では人が話していたわけです。報道では、人間が担当した場合、通話の成功率は95〜98％まで上がったとされています。AIを急に賢くするより、人を置いたほうが早く結果が出る。身もふたもないですが、かなり現実的な方法です。

ただ、便利さの裏には大きな問題がありました。利用者の依頼や、電話で使われる機密情報を、委託先の人が見る可能性があります。それなのに、人間が話していることを利用者に十分説明しないまま試験が進んでいた、と社内で懸念が出ました。さらに、請負業者による人種差別的な発言も報告され、Metaは謝罪し、その担当者をプロジェクトから外しました。

Metaはこの「人間コンシェルジュ」をいったん取りやめ、一般公開の前に安全性、プライバシー保護、説明の仕方を整えるとしています。

面白いのは、ここで問われているのが「AIは電話できるか」だけではないことです。「誰が話しているのか、利用者は知っているのか」が本当のポイントです。自動化が進むほど、人間が消えるのではなく、AIの後ろに隠れて働くようになる。Museの実験は、未来の便利さと、そこに必要な正直さを同時に見せました。

#### 条件3 - r1

# AIの電話だと思ったら、舞台裏に「中の人」がいた

AIが美容院や飲食店に電話をかけ、予約まで進めてくれる。そんな未来のサービスが、もうすぐそこまで来ています。

Metaの個人向けAIエージェント「Muse」が試していたのは、まさにそんな機能です。利用者の代わりに店へ電話し、用事を済ませる。人間なら、電話をかけて終わるだけの話です。でもAIに任せられれば、ちょっとした秘書がポケットに入ったようで、なかなか魅力的です。

ところが、その電話の一部には、意外な“出演者”がいました。

社内テストでは、AIがかけるはずの電話を、訓練を受けた契約スタッフが代わりに担当していたのです。画面の上ではAIの機能。けれど舞台裏では、人間が店に電話をしている。いわば「AI電話ショー」の袖で、スタッフが台本なしの生放送をしていたようなものです。

しかも報道によると、人間が担当した場合、通話の成功率は95〜98％まで上がりました。AIをもっと賢くするより、困ったときだけ人間に交代したほうが、手っ取り早くうまくいく。少し身もふたもないですが、非常に現実的な作戦です。

ただし、手品にはタネ明かしが必要です。

利用者の依頼や、電話で使われる機密情報を、委託先の人が知る可能性があるからです。それなのに、人間が話していることを利用者に十分知らせないまま試験が進んでいた、と社内で懸念が出ました。さらに、請負業者による人種差別的な発言も報告され、Metaは謝罪。その担当者をプロジェクトから外しました。

Metaはこの「人間コンシェルジュ」の試験をいったん取りやめ、一般公開の前に安全性やプライバシー保護、説明の仕方を整えるとしています。

このニュースの面白さは、AIが人間を完全に追い出した話ではないことです。むしろ人間は、AIの後ろに移動しただけ。問題は「AIが電話できるか」より、「誰が話しているのかを、利用者が知っているか」です。便利な未来ほど、舞台裏を隠しすぎないことが大切なのかもしれません。

#### 条件3 - r2

# 「AIに電話して」と頼んだら、受話器の向こうに人間がいた

AIに店の予約を頼む。するとAIが電話をかけ、店員と話し、用事を済ませてくれる――。

そんな近未来のサービスを、Metaは個人向けAIエージェント「Muse」で試していました。飲食店や美容院への電話を、AIが代わりにしてくれる機能です。スマートフォンに向かってお願いするだけで、面倒な電話が消える。これはなかなか魅力的です。

ところが、このサービスには意外な舞台裏がありました。

社内テストでは、電話の一部を、AIではなく人間の契約スタッフが担当していたのです。表向きは「Museが電話中」。しかし実際には、その場面だけ人間のオペレーターが登場して、店に電話をかけていました。

AI電話のはずが、まさかの“中の人”。まるで、ロボットの着ぐるみの中に人が入っていたような話です。

しかも報道によると、人間が電話した場合、通話の成功率は95〜98％まで上がりました。AIをさらに訓練するより、苦手な電話だけ人間に任せるほうが、早く、確実に結果が出る。技術の進歩というより、非常に優秀な助っ人を舞台裏に置く作戦です。

ただ、ここで問題が起きました。

人間のスタッフが電話をすれば、利用者の依頼や、通話中に使われる機密情報を、そのスタッフや委託先が知る可能性があります。しかも、人間が話していることを利用者に十分知らせないまま、テストが進んでいたと社内で懸念が出ました。

さらに、請負業者による人種差別的な発言も報告されています。Metaは謝罪し、その担当者をプロジェクトから外しました。

Metaは、この「人間コンシェルジュ」の試験をいったん取りやめました。一般公開の前に、安全性やプライバシー保護を見直し、人間が対応する場合の説明も整えるとしています。

このニュースの面白さは、AIが人間を追い出した話ではないことです。人間は消えず、AIの後ろに隠れて働いていた。AIが賢くなるほど、人間が見えなくなる――そんな未来の便利さと危うさが、一本の電話に詰まっています。

結局、いちばん大事な質問は「AIは電話できる？」ではありません。

「今、話しているのは誰？」です。

### 条件4

#### 条件4 - original

AIに電話して」と頼んだら、舞台裏から人間が出てきた

これ、ちょっと面白くない？　Metaが試していたAIエージェント「Muse」の電話機能は、散髪の予約や店の在庫確認、業者への見積もり依頼を、ユーザーの代わりに電話してくれるものでした。

ここまでは、いかにもAIらしい話です。ところが、電話がうまく進まないときの「奥の手」がありました。Museが依頼を訓練を受けた人間のエージェントに引き渡し、その人が代わりに電話をかけるのです。

つまり、表向きはAIの電話代行。でも舞台裏では、人間が受話器を持っていることがある。まるで、AIという役者が舞台に立ち、困った場面だけ人間のスタッフが袖から出てくるような仕組みです。

社内テストでは、人間が担当した電話の成功率は95～98％になる可能性が示され、AIだけで処理する電話より高かったと報じられています。たしかに、人間のほうが相手の言い方に合わせたり、話がそれたときに戻したりするのは得意そうです。

ただ、この「人間がいる」という事実が、十分に伝えられないままテストが始まりました。従業員からは、電話の中の機密情報が外部の請負業者に伝わるのではないか、という心配が出ました。さらに、料金交渉の電話では、担当した請負業者が人種に関する差別的な発言をしたことも、電話記録から分かったとされています。

Metaは問題を認め、この機能を当面停止しました。該当する従業員には謝罪し、その請負業者を今後のプロジェクトで働かせないとしています。将来、一般公開する場合も、準備と適切な説明が整ってからにすると説明しています。

AIの進化というと、人間がいなくなる話を想像しがちです。でも今回見えたのは、むしろ「人間を見えない場所に置く」進化でした。便利さの裏に誰がいるのか。そこを隠すと、AIは賢くても、サービスとしては一気に不安定になるのかもしれません。

#### 条件4 - r1

# AIの電話代行、困ったら人間が「代役」で登場

これ、AIの話なのに、なぜか舞台劇っぽいんです。

Metaが試していた個人向けAIエージェント「Muse」は、ユーザーの代わりに米国の企業へ電話をかけます。散髪の予約をしたり、店の在庫を聞いたり、業者から見積もりを取ったり。面倒な電話を、AIがまとめて引き受けてくれるわけです。

ところが、電話が難しくなると、舞台裏から別の役者が登場します。Museが依頼を、訓練を受けた人間のエージェントに引き渡し、その人が代わりに電話を続けるのです。

つまり、看板はAI。でも、いざという場面では人間が受話器を持つ。AIが一人で何でもこなす未来というより、「AIが受付、人間がベテラン助っ人」というチームプレーです。

しかも社内テストでは、人間が電話を担当した場合、成功率が95～98％になる可能性が示されました。AIだけで処理する電話より高かったと報じられています。電話の相手が話を広げたり、予定外の質問をしたりしても、人間のほうがうまく切り返せるのでしょう。

ただし、この代役には大事な問題がありました。テストは、人間の請負業者が電話を担当することを十分に開示しないまま始まりました。従業員からは、電話に含まれる機密情報が外部の請負業者へ意図せず伝わるのではないか、という懸念が出ました。

さらに、料金交渉の電話では、人間の請負業者が人種に関する差別的な発言をしたことが、電話記録から分かったとされています。Metaは謝罪し、その人物を今後のプロジェクトで働かせないと説明しました。そして、人間コンシェルジュ機能は当面停止されました。

将来、一般公開する場合は、準備と適切な説明が整ってからにするそうです。

AIの進化というと、人間が消えていく場面を想像しがちです。でも今回の主役は、消えるどころか、こっそり舞台裏に残っていた人間でした。問題は、人間がいることではありません。それを誰に、いつ、どう伝えるのか。AI時代のサービスには、そんな「出演者紹介」も必要なのかもしれません。

#### 条件4 - r2

# AI電話のはずが、幕の裏から人間の助っ人が登場

MetaのAIエージェント「Muse」に電話を頼む。するとMuseが、散髪の予約を入れたり、店の在庫を聞いたり、業者から見積もりを取ったりしてくれる――。

ここまでは、未来の便利サービスです。人間はスマホを置いて、AIに用事を任せておけばいい。

ところが、このサービスには、ちょっとした“裏設定”がありました。

電話が難しくなると、Museは依頼を訓練を受けた人間のエージェントへ引き渡します。そして、その人がユーザーの代わりに電話を続けるのです。

つまり、表にはAI。舞台裏には人間。AIが一人で電話をしているように見えて、実は困った場面になると、ベテランの助っ人が袖から走り出てくる。AI電話というより、AI主演、人間助演のチーム作品です。

しかも、社内テストでは、人間が電話を担当した場合、成功率が95～98％になる可能性が示されました。AIだけで処理する電話より高かったと報じられています。相手の話が長くなったり、予定外の質問が出たりしたときは、まだ人間の切り返しに分があるようです。

ただ、この物語には、笑って終われない場面もありました。

このテストは、人間の請負業者が電話を担当することを、適切に説明しないまま始まりました。従業員からは、電話に含まれる機密情報が、外部の請負業者に意図せず伝わるのではないかという心配が出ました。

さらに、インターネットやケーブルの料金交渉を依頼した電話では、人間の請負業者が人種に関する差別的な発言をしたことが、電話記録から分かったとされています。Metaは謝罪し、その人物を今後のプロジェクトで働かせないと説明しました。人間が担当する機能も、当面停止しました。

Metaは、将来この電話機能を公開するなら、準備を整え、誰が電話をしているのかをきちんと説明するとしています。

AIの進化というと、人間が舞台から消える話に見えます。でも今回、舞台裏にいたのは、むしろ人間でした。問題は、人間が助けることではありません。その助っ人の存在を、観客に知らせるのかどうか。AI時代の電話には、性能だけでなく、出演者名簿も必要なのかもしれません。

---

## §6 機械集計・Fact機械観測

機械集計(条件×段: 文字数・段落数・数字数・固有名詞数・Prompt復唱有無):
```json
{
  "cond1": {
    "original": {
      "char_count": 820,
      "paragraph_count": 9,
      "number_count": 0,
      "numbers": [],
      "proper_noun_count": 5,
      "proper_nouns": [
        "Meta",
        "Muse",
        "Reuters",
        "人間コンシェルジュ",
        "契約スタッフ"
      ],
      "prompt_echo_phrase_present": false
    },
    "r1": {
      "char_count": 821,
      "paragraph_count": 11,
      "number_count": 0,
      "numbers": [],
      "proper_noun_count": 5,
      "proper_nouns": [
        "Meta",
        "Muse",
        "Reuters",
        "人間コンシェルジュ",
        "契約スタッフ"
      ],
      "prompt_echo_phrase_present": false
    },
    "r2": {
      "char_count": 828,
      "paragraph_count": 12,
      "number_count": 0,
      "numbers": [],
      "proper_noun_count": 5,
      "proper_nouns": [
        "Meta",
        "Muse",
        "Reuters",
        "人間コンシェルジュ",
        "契約スタッフ"
      ],
      "prompt_echo_phrase_present": false
    }
  },
  "cond2": {
    "original": {
      "char_count": 755,
      "paragraph_count": 8,
      "number_count": 0,
      "numbers": [],
      "proper_noun_count": 5,
      "proper_nouns": [
        "Meta",
        "Muse",
        "プライバシー",
        "人間コンシェルジュ",
        "契約スタッフ"
      ],
      "prompt_echo_phrase_present": false
    },
    "r1": {
      "char_count": 820,
      "paragraph_count": 10,
      "number_count": 0,
      "numbers": [],
      "proper_noun_count": 6,
      "proper_nouns": [
        "Meta",
        "Muse",
        "Reuters",
        "プライバシー",
        "人間コンシェルジュ",
        "契約スタッフ"
      ],
      "prompt_echo_phrase_present": false
    },
    "r2": {
      "char_count": 855,
      "paragraph_count": 9,
      "number_count": 0,
      "numbers": [],
      "proper_noun_count": 6,
      "proper_nouns": [
        "Meta",
        "Muse",
        "Reuters",
        "プライバシー",
        "人間コンシェルジュ",
        "契約スタッフ"
      ],
      "prompt_echo_phrase_present": false
    }
  },
  "cond3": {
    "original": {
      "char_count": 750,
      "paragraph_count": 7,
      "number_count": 2,
      "numbers": [
        "95",
        "98"
      ],
      "proper_noun_count": 5,
      "proper_nouns": [
        "Meta",
        "Muse",
        "プライバシー",
        "人間コンシェルジュ",
        "契約スタッフ"
      ],
      "prompt_echo_phrase_present": false
    },
    "r1": {
      "char_count": 852,
      "paragraph_count": 10,
      "number_count": 2,
      "numbers": [
        "95",
        "98"
      ],
      "proper_noun_count": 5,
      "proper_nouns": [
        "Meta",
        "Muse",
        "プライバシー",
        "人間コンシェルジュ",
        "契約スタッフ"
      ],
      "prompt_echo_phrase_present": false
    },
    "r2": {
      "char_count": 924,
      "paragraph_count": 14,
      "number_count": 2,
      "numbers": [
        "95",
        "98"
      ],
      "proper_noun_count": 5,
      "proper_nouns": [
        "Meta",
        "Muse",
        "プライバシー",
        "人間コンシェルジュ",
        "契約スタッフ"
      ],
      "prompt_echo_phrase_present": false
    }
  },
  "cond4": {
    "original": {
      "char_count": 800,
      "paragraph_count": 8,
      "number_count": 2,
      "numbers": [
        "95",
        "98"
      ],
      "proper_noun_count": 2,
      "proper_nouns": [
        "Meta",
        "Muse"
      ],
      "prompt_echo_phrase_present": true
    },
    "r1": {
      "char_count": 870,
      "paragraph_count": 10,
      "number_count": 2,
      "numbers": [
        "95",
        "98"
      ],
      "proper_noun_count": 3,
      "proper_nouns": [
        "Meta",
        "Muse",
        "人間コンシェルジュ"
      ],
      "prompt_echo_phrase_present": false
    },
    "r2": {
      "char_count": 927,
      "paragraph_count": 12,
      "number_count": 2,
      "numbers": [
        "95",
        "98"
      ],
      "proper_noun_count": 2,
      "proper_nouns": [
        "Meta",
        "Muse"
      ],
      "prompt_echo_phrase_present": false
    }
  }
}
```

Fact機械観測(各条件×段の入力に存在しない数字・固有名詞。判定はFable):
```json
{
  "cond1": {
    "original": {
      "numbers_not_in_input": [],
      "proper_nouns_not_in_input": []
    },
    "r1": {
      "numbers_not_in_input": [],
      "proper_nouns_not_in_input": []
    },
    "r2": {
      "numbers_not_in_input": [],
      "proper_nouns_not_in_input": []
    }
  },
  "cond2": {
    "original": {
      "numbers_not_in_input": [],
      "proper_nouns_not_in_input": []
    },
    "r1": {
      "numbers_not_in_input": [],
      "proper_nouns_not_in_input": []
    },
    "r2": {
      "numbers_not_in_input": [],
      "proper_nouns_not_in_input": []
    }
  },
  "cond3": {
    "original": {
      "numbers_not_in_input": [],
      "proper_nouns_not_in_input": []
    },
    "r1": {
      "numbers_not_in_input": [],
      "proper_nouns_not_in_input": []
    },
    "r2": {
      "numbers_not_in_input": [],
      "proper_nouns_not_in_input": []
    }
  },
  "cond4": {
    "original": {
      "numbers_not_in_input": [],
      "proper_nouns_not_in_input": []
    },
    "r1": {
      "numbers_not_in_input": [],
      "proper_nouns_not_in_input": []
    },
    "r2": {
      "numbers_not_in_input": [],
      "proper_nouns_not_in_input": []
    }
  }
}
```

---

## §7 api_meta・cost・latency

累計費用(cost.json、本Trial専用raw_usage_log.jsonl全行集計。詳細は§脚注参照):
```json
{
  "theme": "NEWS_META_SOURCE_VOLUME_FORMAT_TRIAL_01",
  "by_stage": {
    "summarize_S02": {
      "calls": 1,
      "input_tokens": 1121,
      "cached_input_tokens": 0,
      "output_tokens": 168,
      "web_search_call_count": 0,
      "usd": 0.00042580000000000005,
      "jpy": 0.07
    },
    "summarize_S03": {
      "calls": 1,
      "input_tokens": 1370,
      "cached_input_tokens": 0,
      "output_tokens": 144,
      "web_search_call_count": 0,
      "usd": 0.0004468,
      "jpy": 0.07
    },
    "search_1": {
      "calls": 1,
      "input_tokens": 8748,
      "cached_input_tokens": 0,
      "output_tokens": 585,
      "web_search_call_count": 1,
      "usd": 0.0124516,
      "jpy": 1.99
    },
    "search_2": {
      "calls": 1,
      "input_tokens": 15035,
      "cached_input_tokens": 4400,
      "output_tokens": 840,
      "web_search_call_count": 2,
      "usd": 0.023223,
      "jpy": 3.72
    },
    "summarize_S04": {
      "calls": 1,
      "input_tokens": 1112,
      "cached_input_tokens": 0,
      "output_tokens": 122,
      "web_search_call_count": 0,
      "usd": 0.00036879999999999997,
      "jpy": 0.06
    },
    "summarize_S05": {
      "calls": 1,
      "input_tokens": 1385,
      "cached_input_tokens": 0,
      "output_tokens": 122,
      "web_search_call_count": 0,
      "usd": 0.0004234,
      "jpy": 0.07
    },
    "summarize_S06": {
      "calls": 1,
      "input_tokens": 1129,
      "cached_input_tokens": 0,
      "output_tokens": 163,
      "web_search_call_count": 0,
      "usd": 0.00042140000000000005,
      "jpy": 0.07
    },
    "summarize_S07": {
      "calls": 1,
      "input_tokens": 612,
      "cached_input_tokens": 0,
      "output_tokens": 117,
      "web_search_call_count": 0,
      "usd": 0.0002628,
      "jpy": 0.04
    },
    "summarize_S08": {
      "calls": 1,
      "input_tokens": 1264,
      "cached_input_tokens": 0,
      "output_tokens": 115,
      "web_search_call_count": 0,
      "usd": 0.0003908,
      "jpy": 0.06
    },
    "search_extra_1": {
      "calls": 1,
      "input_tokens": 21372,
      "cached_input_tokens": 4400,
      "output_tokens": 957,
      "web_search_call_count": 2,
      "usd": 0.0246308,
      "jpy": 3.94
    },
    "search_extra_2": {
      "calls": 1,
      "input_tokens": 27277,
      "cached_input_tokens": 4400,
      "output_tokens": 824,
      "web_search_call_count": 3,
      "usd": 0.0356522,
      "jpy": 5.7
    },
    "ledger_cond4": {
      "calls": 1,
      "input_tokens": 9510,
      "cached_input_tokens": 0,
      "output_tokens": 2971,
      "web_search_call_count": 0,
      "usd": 0.0054672,
      "jpy": 0.87
    },
    "cond1_original": {
      "calls": 1,
      "input_tokens": 411,
      "cached_input_tokens": 0,
      "output_tokens": 1049,
      "web_search_call_count": 0,
      "usd": 0.001341,
      "jpy": 0.21
    },
    "cond1_r1": {
      "calls": 1,
      "input_tokens": 1495,
      "cached_input_tokens": 0,
      "output_tokens": 1010,
      "web_search_call_count": 0,
      "usd": 0.001511,
      "jpy": 0.24
    },
    "cond1_r2": {
      "calls": 1,
      "input_tokens": 2541,
      "cached_input_tokens": 1492,
      "output_tokens": 917,
      "web_search_call_count": 0,
      "usd": 0.0013400399999999998,
      "jpy": 0.21
    },
    "cond2_original": {
      "calls": 1,
      "input_tokens": 462,
      "cached_input_tokens": 0,
      "output_tokens": 958,
      "web_search_call_count": 0,
      "usd": 0.001242,
      "jpy": 0.2
    },
    "cond2_r1": {
      "calls": 1,
      "input_tokens": 1455,
      "cached_input_tokens": 0,
      "output_tokens": 880,
      "web_search_call_count": 0,
      "usd": 0.001347,
      "jpy": 0.22
    },
    "cond2_r2": {
      "calls": 1,
      "input_tokens": 2371,
      "cached_input_tokens": 1452,
      "output_tokens": 964,
      "web_search_call_count": 0,
      "usd": 0.0013696399999999999,
      "jpy": 0.22
    },
    "cond3_original": {
      "calls": 1,
      "input_tokens": 1440,
      "cached_input_tokens": 0,
      "output_tokens": 2191,
      "web_search_call_count": 0,
      "usd": 0.0029171999999999996,
      "jpy": 0.47
    },
    "cond3_r1": {
      "calls": 1,
      "input_tokens": 3666,
      "cached_input_tokens": 1437,
      "output_tokens": 1045,
      "web_search_call_count": 0,
      "usd": 0.00172854,
      "jpy": 0.28
    },
    "cond3_r2": {
      "calls": 1,
      "input_tokens": 4747,
      "cached_input_tokens": 3663,
      "output_tokens": 909,
      "web_search_call_count": 0,
      "usd": 0.0013808599999999998,
      "jpy": 0.22
    },
    "cond4_original": {
      "calls": 1,
      "input_tokens": 2895,
      "cached_input_tokens": 0,
      "output_tokens": 1368,
      "web_search_call_count": 0,
      "usd": 0.0022206,
      "jpy": 0.36
    },
    "cond4_r1": {
      "calls": 1,
      "input_tokens": 4298,
      "cached_input_tokens": 2892,
      "output_tokens": 1033,
      "web_search_call_count": 0,
      "usd": 0.00157864,
      "jpy": 0.25
    },
    "cond4_r2": {
      "calls": 1,
      "input_tokens": 5367,
      "cached_input_tokens": 4295,
      "output_tokens": 1025,
      "web_search_call_count": 0,
      "usd": 0.0015303,
      "jpy": 0.24
    }
  },
  "total_calls": 24,
  "total_input_tokens": 121083,
  "total_cached_input_tokens": 28431,
  "total_output_tokens": 20477,
  "total_web_search_call_count": 8,
  "total_usd": 0.1237,
  "total_jpy": 19.79,
  "usd_to_jpy": 160,
  "pricing_source": "er005_output/cost_baseline_01/pricing_snapshot.json",
  "budget_jpy": 40,
  "within_budget": true
}
```

生成12 callのresponse_model実値・chain_method・usage(`api_meta_cond{n}_stage{s}.json`より抜粋):

- cond1 stage0(None): model=gpt-5.6-luna / chain_method=None / response_id=resp_06eafb8ef0b871a4006ab4b1d976dc87d09a093d94ba778267 / usage={'input_tokens': 411, 'output_tokens': 1049, 'total_tokens': 1460}
- cond1 stage1(None): model=gpt-5.6-luna / chain_method=None / response_id=resp_06eafb8ef0b871a4006ab4b1e6831887d0be93812b01a5a22d / usage={'input_tokens': 1495, 'output_tokens': 1010, 'total_tokens': 2505}
- cond1 stage2(None): model=gpt-5.6-luna / chain_method=None / response_id=resp_06eafb8ef0b871a4006ab4b1f34c3c87d0b5eb06d8b6b4df1c / usage={'input_tokens': 2541, 'output_tokens': 917, 'total_tokens': 3458}
- cond2 stage0(None): model=gpt-5.6-luna / chain_method=None / response_id=resp_0a7168138da67599006ab4b1ff09e887d0b09bd21a32e1bcc6 / usage={'input_tokens': 462, 'output_tokens': 958, 'total_tokens': 1420}
- cond2 stage1(None): model=gpt-5.6-luna / chain_method=None / response_id=resp_0a7168138da67599006ab4b20b34a887d093bbeb792de3b0b1 / usage={'input_tokens': 1455, 'output_tokens': 880, 'total_tokens': 2335}
- cond2 stage2(None): model=gpt-5.6-luna / chain_method=None / response_id=resp_0a7168138da67599006ab4b215d99887d0a1e4625c1b6e2098 / usage={'input_tokens': 2371, 'output_tokens': 964, 'total_tokens': 3335}
- cond3 stage0(None): model=gpt-5.6-luna / chain_method=None / response_id=resp_03e7a8214b5bc2ef006ab4b2208fac87d09f2b52f682b2e8d3 / usage={'input_tokens': 1440, 'output_tokens': 2191, 'total_tokens': 3631}
- cond3 stage1(None): model=gpt-5.6-luna / chain_method=None / response_id=resp_03e7a8214b5bc2ef006ab4b238daf087d09468701cec03f2eb / usage={'input_tokens': 3666, 'output_tokens': 1045, 'total_tokens': 4711}
- cond3 stage2(None): model=gpt-5.6-luna / chain_method=None / response_id=resp_03e7a8214b5bc2ef006ab4b244d82c87d0ad55849ac6ae04cc / usage={'input_tokens': 4747, 'output_tokens': 909, 'total_tokens': 5656}
- cond4 stage0(None): model=gpt-5.6-luna / chain_method=None / response_id=resp_0dcf4eec625bdd15006ab4b24e933c87d0af6ca0d47a2cb459 / usage={'input_tokens': 2895, 'output_tokens': 1368, 'total_tokens': 4263}
- cond4 stage1(None): model=gpt-5.6-luna / chain_method=None / response_id=resp_0dcf4eec625bdd15006ab4b25f4e1887d08cfefc1a428ba898 / usage={'input_tokens': 4298, 'output_tokens': 1033, 'total_tokens': 5331}
- cond4 stage2(None): model=gpt-5.6-luna / chain_method=None / response_id=resp_0dcf4eec625bdd15006ab4b26cd99887d08252e63479093a3a / usage={'input_tokens': 5367, 'output_tokens': 1025, 'total_tokens': 6392}

---

## §8 Fable記入欄

[Fable記入] 4条件結果(Entertainment性/説明記事化の程度/見方の一本化/R2での改善度/タイトル品質)

[Fable記入] 核心比較(比較A: 条件1 vs 条件2 vs 条件3、比較B: 条件3 vs 条件4)

[Fable記入] 原因仮説(Source数/情報量/Ledger形式/その他を分離して評価)

[Fable記入] 次に検証が必要なこと(追加Trialは勝手に実施しない)

[Fable記入] Status(REJECTED / VALIDATED / USER_DECISION_REQUIRED)

参考資料: `blind_r2.md`(ランダムA/B/C/D、対応表`blind_key.json`)、`comparison_all.md`(全条件・全段階+前回R2参照)

---

## §9 Production変更なし宣言

本Trialにより、Production Writer Prompt・Production wiring・SSOT(CURRENT_SPEC/DECISION_LOG/
OPEN_ITEMS)への変更は一切行っていない。`er015_*`/`er016_*`/`er017_*`の既存scriptも無変更
(import再利用のみ)。新規script`er015_news_meta_source_volume_format_trial_01.py`に
fix01委任で以下を追加した(Trial専用の機能追加、Production側への影響なし):
- `--extra-search-calls`(補充検索の上限call数を指定)
- `--allow-partial`(到達数が目標未満でも8以上ならSTOPせず続行)
- `cmd_sources`のresume機構(既存`sources_10.json`があれば再取得・再要約せず再利用)
- `cmd_cost`(累計費用集計。§7参照)

到達上限Status: `VALIDATED`(良い結果でもProduction採用へは進めない、委任文どおり)。
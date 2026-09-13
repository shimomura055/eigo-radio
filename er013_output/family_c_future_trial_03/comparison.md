# Family C Future Trial-02 vs Trial-03 比較

管理ID: EDITORIAL-FUTURE-FAMILY-C-FINAL-TUNING-TRIAL-03

全項目、Trial-02/Trial-03の実データ(`writer_raw_article.txt`を
`er013_family_c_future_qa_03.route_article_for_qa_v2()`で再解析した値、および
`fact_check_result.json`/`future_framing_qa_result.json`の実測値)に基づく。

## 主要指標比較

| 指標 | Trial-02 A2 | Trial-03 A2 | Trial-02 B1 | Trial-03 B1 |
|---|---|---|---|---|
| 読者向け本文 語数 | 1161 | 550 | 1145 | 744 |
| 目安範囲 | (Trial-02は未設定) | (450, 600) | (Trial-02は未設定) | (500, 700) |
| 枠内hedge密度(may/might/could/perhaps/possibly/would) | 0.000 (0/59文) | 0.000 (0/42文) | 0.190 (11/58文) | 0.023 (1/44文) |
| 感情強度(0-2、主観、引用必須) | 1 | 2 | 0 | 2 |
| 台詞(引用符)出現数 | 8 | 8 | 0 | 8 |
| 研究解説スキャン discovery_style_density該当数 | 0 | 0 | 0 | 0 |
| Future Framing QA v2 overall_status | PASS | PASS | PASS | PASS |
| 枠外での未来断定(future_stated_as_fact_outside_scenes)該当数 | 0 | 0 | 0 | 0 |
| 枠内での現在事実捏造(fabricated_present_facts)該当数 | 0 | 0 | 0 | 0 |
| Fact Checker A' verdict | REVIEW_REQUIRED | REVIEW_REQUIRED | PASS | REVIEW_REQUIRED |
| Fact Checker A' contradictions件数 | 0 | 0 | 0 | 0 |
| Ledger Deviation overall_status | LEDGER_COMPLIANT | LEDGER_COMPLIANT | LEDGER_COMPLIANT | LEDGER_COMPLIANT |
| 編集Gate最終status | PASS | PASS | PASS | FAIL |
| 編集Gate最終fail_reasons | [] | [] | [] | ["product_name_hits=['Stretch']", 'word_count=744 (target_range=500-700)'] |
| 記事全体overall_status | NG_REVIEW_REQUIRED | NG_REVIEW_REQUIRED | PASS | NG_REVIEW_REQUIRED |

## 感情強度の判定根拠(0〜2、主観、台詞/行動の引用必須)

- **trial02 a2** = 1: 内的な問いかけの引用1件のみ(“Am I being helped, or am I working for the helper?”)。他は“this could feel like freedom”“That could be a welcome change”等、行動に紐づかない一般化された感情語が中心。
- **trial02 b1** = 0: 台詞0件(quote_marks=0)。“This future could bring a strange mix of pride and tiredness”のような要約的な感情語のみで、具体的な行動・台詞に紐づく場面がない。
- **trial03 a2** = 2: 台詞4件(“Help needed”“Watch this part again”“Keep going”“I will do this part.”)+行動に紐づく感情描写(“Mara feels a thrill... She also feels irritation. She pulls on shoes”)。“The hope is simple...The concern is sharper...”で希望/不安を明示的に対比。
- **trial03 b1** = 2: 台詞3件(“I wanted to wake up to less work...not become the robot's guard.”“Watch me once”“I wanted help, not another lesson”)+行動連動の感情(“a laugh escapes”“the resident sighs”)。“The hope is clear...The concern is just as clear...”で希望/不安を明示的に対比。

## 実データからの発見(Writer v3設計変更の根拠)

Trial-02の実際の記事を解析した結果、`[[IMAGINED]]`枠そのものは既にhedging少なめ(A2枠内: 0/59文)だったが、hedging過多(may/could/might多用)は各枠の直後に続く「その場面が引き起こす反応・葛藤」の段落(枠外)に集中していた(A2枠外hedge語54件、例: “At first, this could feel like freedom. A person might stop thinking about the floor every evening...”)。この発見を踏まえ、Writer v3では「特定の想像場面から直接生まれる反応・感情・選択」を同じ`[[IMAGINED]]`枠内に含めるよう明示的に指示した(枠外は複数場面にまたがる一般的な示唆のみに限定し、境界原則[枠外で未来を断定しない]は変更していない)。Trial-03 B1の枠内hedge密度が0.0227(1/44文)に残っているのは、この一般的示唆と場面固有反応の境界判断がWriter任せである以上、完全な0にはならないことを示す(閾値0.15以内で許容範囲)。

## 既知の限界(本タスクで発見、修正は範囲外)

Trial-03 B1の編集Gate 2回目試行で`product_name_hits=['Stretch']`が発火したが、実際の該当箇所は“the broom stays on its hook for long stretche**s**”(複数形"stretches"の部分文字列一致)であり、製品名Stretchの実際の言及ではない誤検知(false positive)だった。これは`er013_family_c_future_qa_02.py::scan_product_name_hits()`(無変更のまま再利用)が単純な部分文字列一致(`name.lower() in lowered`)であることに起因する既存(v2)の設計上の限界であり、本タスクで新設した機能ではない。この誤検知により2回目のWriter再生成attemptが本来不要な形で「不合格」評価となり、語数超過(744語 > 700語目安)と合わさってB1の編集Gate最終status=FAILとなった(Fact Safety上の問題ではない)。修正は本タスクの指示範囲外のため実施していない(将来的な改善候補として報告のみ)。

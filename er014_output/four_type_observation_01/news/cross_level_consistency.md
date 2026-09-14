# News (AI regulation vs AI race) — A2/B1 Cross-Level Consistency 突合表

管理ID: EDITORIAL-4TYPE-FOLLOWUP-01-NEWS-B1-ADDITION

既存の自動Cross-Levelチェック機構は存在しない(`CURRENT_SPEC.md`の
「Cross-Level Consistency Check(A2/B1片側修正の禁止)」は**仕様変更時の
運用ルール**であり、生成済み記事本文同士の事実整合を自動比較する
ランタイムQAではない。委任文どおり手動突合)。A2/B1とも同一の
`research/verified_fact_ledger.txt`（VERIFIED 13件）由来。

比較対象: `reader_facing_article.txt`(A2, 406 words) と
`reader_facing_article_b1b.txt`(B1B, 369 words)。

| # | 主張(日付・数値・因果・断定度) | A2の記述 | B1Bの記述 | 判定 |
|---|---|---|---|---|
| 1 | EU GPAIモデル義務の適用開始日 | 2 August 2025 | 2 August 2025 | 一致 |
| 2 | EU AI Act一部規則の執行開始日 | 2 August 2026(prohibited practices, transparency, GPAI義務) | 2 August 2026(prohibited practices, transparency duties, certain GPAI duties) | 一致 |
| 3 | 2026年12月2日の経過措置(marking/detection) | 明記あり | 記載なし(level相応の省略、矛盾ではない) | 矛盾なし(情報量差のみ) |
| 4 | サイバー評価: 最高性能モデルの見習いタスク達成率 | "about half the time"(2024年初は"just over one in ten") | "about 50% of the time"(2024年初は"just over 10%") | 一致 |
| 5 | タスク長が倍増する期間 | about every eight months | about every eight months | 一致 |
| 6 | 脆弱性発見の範囲 | "vulnerabilities in every system"、結果はモデル・用途で差 | "vulnerabilities in every system it tested"、safeguardsは差あり | 一致 |
| 7 | UN科学パネルの構成・設立時期 | 明記なし(「a UN scientific panel」とのみ) | 40 members、August 2025設立 | 矛盾なし(A2が省略しているだけ、A2側に反する記述はない) |
| 8 | UNパネルの予備報告書時期・内容 | July 2026報告、"safeguards cannot keep pace with AI capabilities" | July 2026報告、"safeguards cannot keep pace with the growth of AI capabilities" | 一致 |
| 9 | UNパネルの権限(拘束力なし) | "does not create binding rules or stop a company" | "does not make or enforce international law" | 一致(表現差のみ、含意は同じ) |
| 10 | 10^23 / 10^25 FLOP閾値 | 記載なし | "more than 10^23 calculation steps"(GPAI基準)/"above 10^25"(systemic risk推定、閾値見直し中) | 矛盾なし(A2は省略。ただしB1B側は自身のFact Checkerが"calculation steps"という表現をFLOPの不正確な言い換えとして`REVIEW_REQUIRED`指摘済み[Ledger F004自体との齟齬ではなく、B1B単独の表現精度の論点]) |
| 11 | 米国大統領令(2 June 2026) | 明記あり(執行命令の内容) | 記載なし(level相応の省略、"companies and governments still want faster development and deployment"という一般化した表現のみ) | 矛盾なし(情報量差のみ) |
| 12 | Google Gemini 3.7 Flash | 社名明記("Google released Gemini 3.7 Flash three weeks after 3.6") | 社名なし("One company reported releasing a new Flash model three weeks after its predecessor") | 矛盾なし(B1Bは社名を一般化、数値[3週間]は一致) |
| 13 | OpenAI Astra関連(safety pause→restart) | 社名明記、restart date=28 August 2026 | 社名なし("Another said it held back larger Astra runs...restarted the frontier run on 28 August 2026") | 矛盾なし(B1Bは社名を省略、日付・内容は一致) |
| 14 | Anthropicの協調的ペーシング発言 | 社名明記 | 社名なし("A third said industry-wide pacing would need a lawful, verifiable mechanism") | 矛盾なし(B1Bは社名を省略、内容は一致) |
| 15 | 全体の対立構図(規制拡大 vs 開発競争継続) | "Safety rules are growing, but the push to build and deploy more powerful systems continues." | "Rules, warnings, and safety work are expanding. At the same time, companies and governments still want faster development and deployment." | 一致 |

## 総合判定

**A2/B1間で日付・数値・因果関係・方向性の直接的な矛盾は検出されなかった。**
差分は全てB1B側のlevel相応の簡略化(社名の一般化、米国大統領令の省略、
経過措置日の省略)であり、いずれもA2の記述と矛盾する内容には置き換わって
いない(単なる情報量の差)。

唯一の留意点は#10(10^23閾値の表現)で、これはA2/B1間の食い違いではなく、
B1B単独のFact Checker(`b1b/audit/fact_check_attempts.json`)が
"calculation steps"という言い換えをFLOPの不正確な表現として
`REVIEW_REQUIRED`判定した論点。Ledger本文(F004)自体は"floating-point
operations"と正しく記載されており、Ledgerとの齟齬はWriter側の言い換えに
起因する(既存の正式QA[Fact Checker]が正しく検出し、`fact_verdict=
REVIEW_REQUIRED`として`run_result_b1b.json`/`b1b/audit/fact_check_
attempts.json`に記録済み。人間レビューへの回付方法[例: er006_output系の
human_review_queue.jsonlとの連携有無]は本タスクの調査範囲外のため未確認)。

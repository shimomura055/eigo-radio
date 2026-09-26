# NEWS-FAMILY-X-WRITER-FACT-SELECTION-TRIAL-01_REPORT.md

管理ID: NEWS-FAMILY-X-WRITER-FACT-SELECTION-TRIAL-01(Sonnet実行、2026-09-26)

Production実装ではない。Trialのみ、最大分類VALIDATED、文章生成まで
(3分割・Comment・scaffold・TTS・assemble・E2E禁止)。Production
Prompt/moduleは一切変更していない(既存定数・関数のimport・流用のみ)。

## §1 目的

複数Source Researchの情報量を確保しつつ、Writerへ情報を見せすぎて
「情報詰め込み型」になる問題を、B案(Selected Fact Brief)で防げるかを
検証する。変数は「Writerへ見せる情報量・形式」だけであり、Writer
Prompt本体(P7)・model/effort・Original→R1→R2のRevision指示・
Adaptation prompt本体(語彙ルールv2込み)は3条件で完全同一とした。

テーマ: Meta Muse AI電話代行「人間コンシェルジュ」実験(既存実世界ニュース、
`NEWS-ITERATIVE-ENTERTAINMENT-TRIAL-02`のArticle Aと同一)。

## §2 3条件の入力差

3条件ともテーマ行・P7本文指示は完全同一
(`docs/pm/ACTIVE_TASK_FW.md`参照元スクリプトのTHEME_LINE、trial02と逐語同一)。
差は[ニュース]欄へ挿入する素材(`writer_input.md`)のみ。

| 条件 | 素材の性質 | 文字数 | Fact件数 |
|---|---|---|---|
| control | 過去Meta baseline(2-B)の短い要約(2〜3文、逐語) | 209字 | 実質3件相当(以下§7参照) |
| a_full_ledger | Full Fact Ledger全文(18 Fact、そのまま) | 8,214字 | 18件 |
| b_selected_brief | 事前選定Storyline用に絞ったBrief(7 Fact、Ledger記載を抜粋) | 3,216字 | 7件 |

## §3 Research Source

新規Research構築なし(既存資産の再利用、費用¥0)。
- Ledger本体: `er012_output/e_family_two_level_wiring_01/meta/ledger/verified_fact_ledger.txt`
  (18 Fact、`reuse_source.json`により元は
  `er017_output/news_entertainment_production_line_trial_01/ledger/verified_fact_ledger.txt`
  から再利用、sha256=a732323997280d792f326abea8f62fdf1df80b038a0ca436375448e81525caa1)
- Fact scope確認補助: `er012_output/e_family_two_level_wiring_01/meta/fact/meta_fact_scope.md`
  (「一部の通話[call単位]」scopeの一次情報引用、既存)
- 一次情報URL(Ledger内引用、重複除去):
  - https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/
  - https://www.404media.co/meta-tests-muse-ai-agent-calls-that-are-actually-made-by-humans-in-a-call-center/
  - https://www.marketscreener.com/news/meta-testing-a-human-concierge-for-its-new-personal-ai-agent-muse-ce785ad8de8cf025

保存先: `er015_output/family_x_writer_fact_selection_trial_01/research/
{sources.md, full_ledger.md, b_selected_fact_brief.md}`

## §4 Control(現状相当、短い要約)全文

日本語R2 (841字) と English (404語) は
`er015_output/family_x_writer_fact_selection_trial_01/control/{r2.md, english.md}`
に保存。要旨: 「AIに電話を頼んだら、舞台袖から人間が出てきた」という
舞台メタファーの1本のStoryline。プライバシー懸念とロールバックまで書くが、
**「なぜ人間が必要だったか」(AIだと分かると電話を切られる問題)を説明する
Factが素材に含まれておらず、本文でも触れられていない**(素材3〜4文の
情報量では因果の環が閉じない)。

## §5 A(Full Ledger)全文

日本語R2 (1,019字) と English (461語) は
`er015_output/family_x_writer_fact_selection_trial_01/a_full_ledger/{r2.md, english.md}`
に保存。要旨: 「AIの声だと思ったら、舞台裏では人間が話していた」。
Muse発表日(9/8)、一般機能列挙、テスト期間(8月〜9月中旬)、規模(従業員約半分)、
成功率95〜98%、人種に関する不適切発言の個別事例、将来の一般公開方針まで、
18 Factのうち14件相当を本文に反映(§7参照)。Storylineは一応1本に保たれて
いるが、事実点数が多く、段落・情報量ともControl/Bより明確に多い。

## §6 B(Selected Fact Brief)全文

日本語R2 (910字) と English (414語) は
`er015_output/family_x_writer_fact_selection_trial_01/b_selected_brief/{r2.md, english.md}`
に保存。要旨: 「AI電話の"ラスボス"は、AIだと気づく人間だった」という
ゲーム的メタファー。選定した7 Fact(電話機能の中身→AIだとバレて切られる
問題→人間への引き渡し→規模[約半数・オプトアウト]→スコープ注意書き
[主に社内テスト、一般ユーザーへの適用は不明]→プライバシー懸念→
ロールバック)を過不足なく使い切り、余分な情報(発表日・成功率数値・
個別不適切発言事例など)を一切含まない。

選定理由・除外理由の全文は
`er015_output/family_x_writer_fact_selection_trial_01/research/b_selected_fact_brief.md`
に記録(選定7件・除外11件、各1行理由付き)。

## §7 比較表

### 7-1 語数・段落数(コード計測、`observation_machine.json`)

| 条件 | JP R2文字数 | JP R2段落数 | English語数 | English段落数 | 見出し数 | 箇条書き | In one line |
|---|---|---|---|---|---|---|---|
| control | 841 | 9 | 404 | 11 | 2(title+In one line) | 0 | あり |
| a_full_ledger | 1,019 | 12 | **461**(目標280–420超過) | 14 | 2 | 0 | あり |
| b_selected_brief | 910 | 12 | 414 | 14 | 2 | 0 | あり |

3条件ともFormat(`# `title・見出し/箇条書きなしの地の文・`## In one line`)は
守られている。**Aのみ目標語数(280–420)を41語超過**しており、情報量の
多さが素直に文章量へ反映された。

### 7-2 Fact使用数(Sonnet目視、機械キーワード補助= `fact_diff_machine.json`)

Full Ledger 18 Fact(MUSE-001〜018)のうち、日本語R2で実質的に言及された
Factをid・要旨で示す(パラフレーズも「使用」とみなす。機械キーワード一致は
表記ゆれ[「半数」/「半分」等]で漏れがあるため、本表は全文を読んだ上での
Sonnet最終判定)。

| Fact ID | 要旨 | control | a_full_ledger | b_selected_brief |
|---|---|---|---|---|
| MUSE-001 | Muse発表(9/8、地域) | – | ○ | – |
| MUSE-002 | 一般機能列挙(メール/旅行予約等) | – | ○ | – |
| MUSE-003 | 電話機能の中身(予約/在庫確認/見積) | – | ○ | ○ |
| MUSE-004 | 内部テスト開始時期(8月〜) | – | ○ | – |
| MUSE-005 | 通話後の記録・要約 | – | ○ | – |
| MUSE-006 | 人間への引き渡し(core) | ○ | ○ | ○ |
| MUSE-007 | 規模(従業員約半数・オプトアウト) | – | ○ | ○ |
| MUSE-008 | AIだとバレると切られる(理由) | – | ○ | ○ |
| MUSE-009 | プライバシー懸念 | ○ | ○ | ○ |
| MUSE-010 | 副社長認め・ロールバック | ○ | ○ | ○ |
| MUSE-011 | 成功率95〜98% | – | ○ | – |
| MUSE-012 | 人種に関する不適切発言(個別事例) | – | ○ | – |
| MUSE-013 | Meta広報コメント | – | – | – |
| MUSE-014 | 将来の一般公開方針(AMBIGUOUS) | – | ○ | – |
| MUSE-015 | Muse Secure VM | – | – | – |
| MUSE-016 | ダウンロード数250万超 | – | – | – |
| MUSE-017 | Facebook「M」の逸話(10年前) | – | – | – |
| MUSE-018 | スコープ注意(主に社内テスト、一般化しない) | – | ○(概ね) | ○ |
| **独立Fact数** | | **3/18** | **14/18** | **7/18** |
| **必須Fact(003/006/007/008/009/010/018、7件)の欠落** | | **4件欠落**(003/007/008/018) | **0件欠落** | **0件欠落** |
| **Storyline外Factの詰め込み数** | | 0件 | **7件**(001/002/004/005/011/012/014) | 0件 |
| **Fact drift(Ledgerにない事実・数値・固有名詞の追加)** | | なし | なし | なし |

注: EnglishもJP R2と同じFact構成をほぼそのまま反映しており(Adaptation
promptがFactを追加しない設計のため)、英語版で新たなFact増減は確認されな
かった。

### 7-3 定性評価(Sonnet目視、1〜5)

| 項目 | control | a_full_ledger | b_selected_brief |
|---|---|---|---|
| Storyline一本性 | 4(舞台メタファーは一貫だが因果が浅い) | 3(1本だが事実点数が多くやや説明記事寄り) | 5(「AIバレ→人間交代→開示問題→停止」の因果が完全に閉じる) |
| Storytelling | 4(メタファーは効いているが説得力の裏付けが薄い) | 3(メタファーはあるが列挙感が強まる) | 5(「ラスボス」メタファーが理由[MUSE-008]と直結し一貫) |
| 説明記事化の度合い | 低い | **中〜やや高い**(JP R2 12段落、成功率・発言事例まで並ぶ) | 低い |
| Original→R1→R2で改善したか | 改善(字数・段落増、表現滑らかに) | 改善(構成は整理されたが情報量自体は減らない) | 改善(メタファー強化、因果がより明確に) |
| 日本語品質 | 良好 | 良好 | 良好 |
| English品質 | 良好、契約(見出し/箇条書きなし・## In one line)遵守 | 良好、契約遵守、ただし語数超過 | 良好、契約遵守、語数目標内 |
| 不自然な水増し | なし | なし(水増しではなく素材の量そのものが多い) | なし |

### 7-4 B vs A / B vs Control

| 観点 | B − A | B − Control |
|---|---|---|
| Fact完全性(必須7件) | 同等(両者とも0件欠落) | **Bが優位**(Controlは4件欠落、うち MUSE-008[理由]とMUSE-018[過度な一般化防止]の欠落は物語の論理性・安全性に影響) |
| 詰め込み度 | **Bが明確に優位**(AはStoryline外7Fact混入、Bは0件) | 同等(両者ともStoryline外の詰め込みなし) |
| 語数目標遵守(280–420) | **Bが優位**(Aは461語で超過、Bは414語で範囲内) | 同等(Controlも404語で範囲内) |
| Storytelling/Storyline一本性 | **Bが優位**(Aはやや説明記事寄り) | **Bが優位**(Controlは因果が浅い) |
| Fact drift | 同等(両者ともなし) | 同等(両者ともなし) |

## §8 QCD(Quality/Cost/Delivery)

- Quality: 3条件ともRuntime evidence取得済み(全12 API call成功、
  STRUCTURE_INVALID・空応答等の異常なし)。
- Cost: 実測 **¥3.09**(上限¥40の約7.7%)。内訳:
  Original→R1→R2(9 call、trial02方式・previous_response_id連鎖、
  fallback未発生)+ Adaptation(3 call、`run_writer_no_search`)。
  `er015_output/family_x_writer_fact_selection_trial_01/cost.json`保存。
- Delivery: 単一セッションで完結(1管理ID・初回のみ、Fableへの差し戻し
  なし)。

## §9 Sonnet仮分類(最大VALIDATED)

**判定条件(ユーザー定義): B ≥ Control が最低条件
(Storytelling Control以上・Fact completeness Control同等以上・
Aより詰め込みが少ない、を同時に満たすのが理想)。**

実測結果:
1. Storytelling: B(5) ≥ Control(4) — **満たす**。
2. Fact completeness: B(必須7件中0件欠落) ≥ Control(必須7件中4件欠落) —
   **Bが明確に上回る(同等以上を満たす)**。
3. 詰め込みの少なさ: B(Storyline外Fact 0件、語数414) < A(Storyline外Fact
   7件、語数461語で目標超過) — **満たす**。

3条件すべてを同時に満たしたため、ユーザー定義の採用最低条件は
**Trialの範囲では満たされた**と暫定的に判定する。

Sonnet暫定分類: **VALIDATED**(Trial範囲内。1テーマ1回のみの実行であり、
他テーマでの再現性・複数記事での安定性は未検証。Production採用は
ユーザーの正式承認[APPROVED_FOR_PRODUCTION]が必要)。

## §10 Fable評価

[Fable記入]

## §11 分類(Fable最終判断)

[Fable記入]

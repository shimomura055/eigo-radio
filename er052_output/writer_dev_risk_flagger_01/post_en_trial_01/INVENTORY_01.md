# INVENTORY_01: POST-EN-TRIAL-01 英語稿棚卸(Phase 1、API費用JPY0)

管理ID: WRITER-DEV-RISK-FLAGGER-POST-EN-TRIAL-01 / 2026-10-10 / 既存成果物の読み取りのみ。再生成・補完は一切していない。
復元=既存dev-check promptの『検証対象の記事』欄から本文を抽出(Checkerに実際に渡された英語稿そのもの)。復元元ファイル内のLedger欄が `research_ledger/verified_fact_ledger.txt` と一致することを全復元稿で確認済み(embedded_ledger_equals_research_ledger=True)。

## 1. 使用稿一覧(11本 = 既定8本 + 既知例用の追加3本)

| Unit | Theme | 経路 | 区分 | 入力path(固定コピー) | 元path | 元の種類 | 本文sha256(先頭12) | 生成日時(mtime) | 文字数 |
|---|---|---|---|---|---|---|---|---|---|
| U01 | meta | Advanced B1b(英語Advanced) | 採用稿(ADOPTED。Advanced checker RESOLVED_STAGE2_DOWNGRADE) | `inputs/U01_meta.md` | `runs/meta/new/b1b/article.md` | article.md | ccf44b75647d | 2026-10-09T09:36:11 | 2919 |
| U02 | hormuz | Advanced B1b | 採用稿(ADOPTED。Adv RESOLVED_STAGE2_DOWNGRADE) | `inputs/U02_hormuz.md` | `runs/hormuz/new/b1b/article.md` | article.md | a58dfdd4eef4 | 2026-10-09T10:05:02 | 2815 |
| U03 | space_weapons | Advanced B1b(B1回復後の最終稿) | 採用稿(ADOPTED。Adv RESOLVED_REWRITE_THEN_DOWNGRADE) | `inputs/U03_space_weapons.md` | `runs/space_weapons/new/b1b/article.md` | article.md | ec6f040ae760 | 2026-10-09T10:08:40 | 2777 |
| U04 | small_bag | Advanced B1b | 採用稿(ADOPTED。Adv RESOLVED_STAGE2_DOWNGRADE) | `inputs/U04_small_bag.md` | `runs/small_bag/new/b1b/article.md` | article.md | c61082754fa4 | 2026-10-09T10:03:39 | 2582 |
| U05 | byd_recall | Advanced B1b | 採用稿(ADOPTED。Adv RESOLVED_REWRITE_THEN_DOWNGRADE) | `inputs/U05_byd_recall.md` | `runs/byd_recall/new/b1b/article.md` | article.md | e2f1a9a2a32a | 2026-10-09T10:38:06 | 2791 |
| U06 | streaming_price | Advanced B1b | 採用稿(ADOPTED。Adv RESOLVED_STAGE2_DOWNGRADE) | `inputs/U06_streaming_price.md` | `runs/streaming_price/new/b1b/article.md` | article.md | ade7ef0e4789 | 2026-10-09T10:37:47 | 2647 |
| U07 | openai_copyright | Advanced B1b(B1回復後のJA R2由来) | 【STOP稿】翻訳後Hard STOP Check(JA_RECHECK_REQUIRED)で止まった英語生成稿。完成記事ではない。article.mdは存在せず、dev-check promptの『検証対象の記事』欄から復元 | `inputs/U07_openai_copyright.md` | `runs/openai_copyright/new/b1b/audit/deviation_checks/advanced_attempt1.json` | recovered_from_dev_check_prompt | 60f73674afc6 | 2026-10-09T10:48:25 | 2898 |
| U08 | semiconductor_earnings | Advanced B1b | 【STOP稿】翻訳後Hard STOP Check(JA_RECHECK_REQUIRED)で止まった英語生成稿。完成記事ではない。article.mdは存在せず、dev-check promptから復元 | `inputs/U08_semiconductor_earnings.md` | `runs/semiconductor_earnings/new/b1b/audit/deviation_checks/advanced_attempt1.json` | recovered_from_dev_check_prompt | a377dad110db | 2026-10-09T11:04:43 | 2577 |
| X09 | hormuz | Advanced B1b_prev_b1(B1回復前の初回英語稿) | 【追加・既知例用】B1回復前の英語稿(ja_source MAJORでSTOPし、JA再生成=B1回復の起点となった稿)。採用稿ではない。dev-check promptから復元 | `inputs/X09_hormuz.md` | `runs/hormuz/new/b1b_prev_b1/audit/deviation_checks/advanced_attempt1.json` | recovered_from_dev_check_prompt | 67655dc17638 | 2026-10-09T10:00:48 | 2696 |
| X10 | space_weapons | Advanced B1b_prev_b1(B1回復前稿) | 【追加・既知例用】B1回復前の英語稿(attempt2でdev-check COMPLIANTだったがB1回復で置換された)。最終採用稿ではない | `inputs/X10_space_weapons.md` | `runs/space_weapons/new/b1b_prev_b1/article.md` | article.md | d34cf153dce0 | 2026-10-09T10:04:08 | 2813 |
| X11 | openai_copyright | Advanced B1b_prev_b1(B1回復前の初回英語稿) | 【追加・最重要既知例用・STOP稿】B1回復前に翻訳後Hard STOP Check(changed_actor MAJOR, ja_source)で止まった英語生成稿。完成記事ではない。dev-check promptから復元 | `inputs/X11_openai_copyright.md` | `runs/openai_copyright/new/b1b_prev_b1/audit/deviation_checks/advanced_attempt1.json` | recovered_from_dev_check_prompt | cee135699553 | 2026-10-09T10:44:31 | 2758 |

区分の凡例: U=Fable決定規則の既定稿(採用稿がある6テーマはAdvanced b1b/article.md、OpenAI/SemiconductorはSTOP時のAdvanced稿)。X=既知例の文が既定稿に実在せず別の既存英語稿にのみ実在したため**追加**した稿(置換ではない)。**【STOP稿】は完成記事ではない**。

## 2. 重要な所在差異(ユーザー指示の想定と異なる点、要確認)

- **OpenAI Copyright: ユーザー指示の2文(日本語R2『OpenAIが著作権管理情報を除去した』/英語『They also say the models' output copied or put articles together…』)は、同一世代の稿ではない。**
  - 英語『…put articles together…』は `b1b_prev_b1`(B1回復**前**の初回英語稿 = X11)にのみ実在。その元になった日本語R2(`ja_writer_prev_b1/revision2.md`)は『さらに、モデルの出力が記事を複製したり、組み直したりしたほか、著作権管理情報も取り除いたとしています』と**主語(OpenAI)が明示されていない**。つまり、この稿については既存Checkの `origin=ja_source` は日本語側に主語がないという意味で整合する。
  - 日本語『OpenAIが著作権管理情報を除去したとも訴えている』は `ja_writer/revision2.md`(B1回復**後**のJA R2)で、そこから作られた英語(U07)は『They further accuse OpenAI of removing copyright management information.』と**主体(OpenAI)が明示されactor driftなし**。U07は翻訳後Checkでは別件(見出し『AI Lawsuits Are About More Than Money』のscope拡張, ja_source)でSTOPした。
  - 対応: 両方をSTOP稿として対象に含める(U07=最終STOP稿、X11=B1回復前STOP稿)。actor drift検出評価はX11が本命、U07は同一テーマの『主体が明示された版』=対照。
- **Hormuz: 『Brent→oil prices』の一般化は既定稿U02には実在しない**(U02は『not crude oil prices overall, but Brent futures』と正しく限定している)。実在するのはB1回復前の初回英語稿(X09。『oil prices shot up』『oil prices made a dramatic move』)。X09を追加。
- **Space Weapons: 『地球を吹き飛ばす兵器ではない』は既定稿U03には実在しない**。実在はB1回復前稿X10(`b1b_prev_b1/article.md` = 『not a weapon that can blow up Earth』)。X10を追加。U03には別系統の不在断定『has not disclosed their capabilities』(s33)と『no specific system names or attack capabilities have been given』(s13)がある。
- **BYD: In One Lineの条件落ち**は既定稿U05に実在する(s27『…faulty pedal pads may keep the brake lights on when drivers aren't braking.』。台帳の『極端な場合に部品が外れた場合』という条件が1文要約から欠落、本文s5相当には『in an extreme case, it may come off』が残っている)。Standard(A2) attempt1稿にも同趣旨があるが、既定稿U05で足りるため追加しない。
- **Semiconductor: 『This announcement alone does not explain how the two are connected.』** はU08のs25に実在(`.”`直後で文分割されず、直前の文と1つの文ID(s25)にまとまる。理由は EN_ADAPTATION_01.md)。
- 件数: Fable補足の目安『8〜最大10本』に対し11本になった(追加3本)。費用見積は JPY50.83(高位 JPY78.75)で上限 JPY100 の範囲内。

## 3. 既知例の機械検索結果(文ID)

| Unit | 文ID | 該当文(先頭) |
|---|---|---|
| U02 | s27 | What we are looking at here is not crude oil prices overall, but Brent futures. |
| U03 | s13 | But no specific system names or attack capabilities have been given. |
| U03 | s33 | The United States has publicly acknowledged deploying space-control weapons in orbit, but has not disclosed their capabilities. |
| U05 | s26 | ## In one line |
| U05 | s27 | BYD is recalling 183,211 cars in China because faulty pedal pads may keep the brake lights on when drivers aren’t braking. |
| U07 | s1 | # More Than $250 Million—and a Demand to “Destroy the Models,” Too: AI Lawsuits Are About More Than Money |
| U07 | s11 | They further accuse OpenAI of removing copyright management information. |
| U08 | s25 | But even if the company’s forecast appears beside that line, we cannot say, “AI demand is strong, so revenue will be about $34.8 billion.” This announcement alone does no |
| X09 | s2 | A major policy plan appeared, and oil prices shot up. |
| X09 | s13 | Meanwhile, oil prices made a dramatic move. |
| X10 | s5 | The main subject here is not a weapon that can blow up Earth, but the line around what counts as a “space weapon.” This is news where the label matters more than flashy s |
| X11 | s7 | They also say the models’ output copied or put articles together in new ways, and removed copyright management information. |

不在の確認: Hormuz既知例(Brent→oil prices)=U02に不在/X09に実在、Space既知例(blow up Earth)=U03に不在/X10に実在、OpenAI既知例(put articles together)=U07に不在/X11に実在、BYD=U05に実在、Semiconductor=U08に実在。**不在の稿に対して『検出できなかった』とは扱わない**(RESULT_01.mdでも『本文に不在』と書く)。

## 4. 回収できなかったもの

なし。OpenAI/Semiconductor STOP稿は、いずれも `audit/deviation_checks/advanced_attempt1.json` のpromptから復元できた(復元元は上表)。Central Bank Mortgage(R0でSTOP、英語稿なし)は対象外。

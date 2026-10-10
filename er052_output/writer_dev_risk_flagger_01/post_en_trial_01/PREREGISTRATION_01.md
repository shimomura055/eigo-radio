# PREREGISTRATION_01: WRITER-DEV-RISK-FLAGGER-POST-EN-TRIAL-01(Trial/DEV、2026-10-10、委任_01 Phase 1)

Phase 1(API費用JPY0)完了。費用見積が JPY100 以内のためFable判断どおりPhase 2へ進む。Productionコード・detectors・antenna_trial_01 は無変更。

## 1. 目的
A3+A4 Risk Flaggerを『英訳後・音声化前』に置いた場合に、最終的にユーザーへ届く英語本文のFact RiskをHuman Review候補として拾えるかを、既存英語稿(FACTLOCK-ASTRA-E2E-TRIAL-01)で観察する。Trialのみ。Production実装・採否判断はしない。Risk FlaggerはCheckerではない(STOPしない・PASS/FAIL判定しない・自動Rewriteしない)。

## 2. 使用稿(11本)と台帳

| Unit | Theme | 経路 | 区分 | 入力sha256 | 元path | 台帳 / Fact数 |
|---|---|---|---|---|---|---|
| U01 | meta | Advanced B1b(英語Advanced) | 採用稿(ADOPTED。Advanced checker RESOLVED_STAGE2_DOWNGRADE) | `d2d4b7f8f409b359` | `runs/meta/new/b1b/article.md` | `runs/meta/new/research_ledger/verified_fact_ledger.txt` sha `6e271bb24fdf` / 15 |
| U02 | hormuz | Advanced B1b | 採用稿(ADOPTED。Adv RESOLVED_STAGE2_DOWNGRADE) | `7cae52e4de24dca0` | `runs/hormuz/new/b1b/article.md` | `runs/hormuz/new/research_ledger/verified_fact_ledger.txt` sha `83b2a09b99b2` / 12 |
| U03 | space_weapons | Advanced B1b(B1回復後の最終稿) | 採用稿(ADOPTED。Adv RESOLVED_REWRITE_THEN_DOWNGRADE) | `5a9631ad4aa1918b` | `runs/space_weapons/new/b1b/article.md` | `runs/space_weapons/new/research_ledger/verified_fact_ledger.txt` sha `2ebdce8660fb` / 22 |
| U04 | small_bag | Advanced B1b | 採用稿(ADOPTED。Adv RESOLVED_STAGE2_DOWNGRADE) | `5d190aabafe6b559` | `runs/small_bag/new/b1b/article.md` | `runs/small_bag/new/research_ledger/verified_fact_ledger.txt` sha `f011dc266e0d` / 6 |
| U05 | byd_recall | Advanced B1b | 採用稿(ADOPTED。Adv RESOLVED_REWRITE_THEN_DOWNGRADE) | `95121516a22d2dbc` | `runs/byd_recall/new/b1b/article.md` | `runs/byd_recall/new/research_ledger/verified_fact_ledger.txt` sha `a7a2d0d910a6` / 11 |
| U06 | streaming_price | Advanced B1b | 採用稿(ADOPTED。Adv RESOLVED_STAGE2_DOWNGRADE) | `f02847d316ccbe7e` | `runs/streaming_price/new/b1b/article.md` | `runs/streaming_price/new/research_ledger/verified_fact_ledger.txt` sha `6488ef82b057` / 7 |
| U07 | openai_copyright | Advanced B1b(B1回復後のJA R2由来) | 【STOP稿】翻訳後Hard STOP Check(JA_RECHECK_REQUIRED)で止まった英語生成稿。完成記事ではない。article.mdは存在せず、dev-check promptの『検証対象の記事』欄から復元 | `bf5680b00b3075d1` | `runs/openai_copyright/new/b1b/audit/deviation_checks/advanced_attempt1.json` | `runs/openai_copyright/new/research_ledger/verified_fact_ledger.txt` sha `870034d74950` / 8 |
| U08 | semiconductor_earnings | Advanced B1b | 【STOP稿】翻訳後Hard STOP Check(JA_RECHECK_REQUIRED)で止まった英語生成稿。完成記事ではない。article.mdは存在せず、dev-check promptから復元 | `b42f6bbf7bc6f327` | `runs/semiconductor_earnings/new/b1b/audit/deviation_checks/advanced_attempt1.json` | `runs/semiconductor_earnings/new/research_ledger/verified_fact_ledger.txt` sha `f45eb25bb7ab` / 6 |
| X09 | hormuz | Advanced B1b_prev_b1(B1回復前の初回英語稿) | 【追加・既知例用】B1回復前の英語稿(ja_source MAJORでSTOPし、JA再生成=B1回復の起点となった稿)。採用稿ではない。dev-check promptから復元 | `adf6f2fb422c27fe` | `runs/hormuz/new/b1b_prev_b1/audit/deviation_checks/advanced_attempt1.json` | `runs/hormuz/new/research_ledger/verified_fact_ledger.txt` sha `83b2a09b99b2` / 12 |
| X10 | space_weapons | Advanced B1b_prev_b1(B1回復前稿) | 【追加・既知例用】B1回復前の英語稿(attempt2でdev-check COMPLIANTだったがB1回復で置換された)。最終採用稿ではない | `59b063d43ded863c` | `runs/space_weapons/new/b1b_prev_b1/article.md` | `runs/space_weapons/new/research_ledger/verified_fact_ledger.txt` sha `2ebdce8660fb` / 22 |
| X11 | openai_copyright | Advanced B1b_prev_b1(B1回復前の初回英語稿) | 【追加・最重要既知例用・STOP稿】B1回復前に翻訳後Hard STOP Check(changed_actor MAJOR, ja_source)で止まった英語生成稿。完成記事ではない。dev-check promptから復元 | `cf86ef36e2e2003f` | `runs/openai_copyright/new/b1b_prev_b1/audit/deviation_checks/advanced_attempt1.json` | `runs/openai_copyright/new/research_ledger/verified_fact_ledger.txt` sha `870034d74950` / 8 |

詳細は INVENTORY_01.md / LEDGER_COMPLETENESS_01.md。全台帳でexpected=regex=parsed(PASS)。駆動時にも各セルで再assertする。

## 3. Flagger条件(ANTENNA-TRIAL-01から意味変更なし)

- A3 = `antenna_prompts.antenna_system(3)` sha256 `9d9950428419c3af824cc5b8676a4b564f96aeb87657c547d418cc86ef3538e9`(実使用版 = 元のANTENNA版、差分ゼロ。英語注記追加なし)
- A4 = `antenna_prompts.antenna_system(4)` sha256 `c87b95e5bcf1b5c266b8978c5688849eb339a6087efbcaf56bb7399ed128ef01`(同上)
- A3/A4は累積設計(A4はA3の条件を含む)。Union = 同一(記事, 文ID)をA3/A4で重複除去(A3の出力 ∪ A4の出力)。
- A5/A6は使用しない。強制TopN禁止。0件許容。confidenceの新閾値は追加しない(全Flagを保存・報告。Human Review候補への採否はユーザーが判断)。重大定義は変更しない。自動Rewrite・再生成・記事STOPなし。
- モデル gpt-6.1-sol / effort=medium / Responses API / 1セル1呼び出し。価格は `er005_output/cost_baseline_01/pricing_snapshot.json` 登録値、USD/JPY=160。
- 再試行: 既存run_llmの形式再呼び出し1回+通信エラー2回まで(従来と同一)。それ以外のセル単位の再実行は同条件で最大1回、記録する。異常な再試行は禁止。
- 並列: 22セル(11本×A3/A4)を独立process並列(各セルは別ファイルに書込み、費用台帳は追記のみ)。

## 4. Union規則・集計定義(事前登録)

- sentence-level Flag総数 = A3件数 + A4件数。A3/A4 overlap = 同一(記事, 文ID)をA3とA4の両方がFlagした数。Union総数 = sentence-levelのユニーク(記事, 文ID)数。
- typeが異なっても同一(記事, 文ID)は1件にまとめ、両typeとconfidence(A3値/A4値)を併記する。
- 意味上の問題単位 = 同一の意味問題を複数文で指摘している場合は1件に束ねる(束ねた場合は束ね方を明記)。束ねはClaudeの機械的提案であり、有用/不要の最終ラベルは確定しない(ユーザー確認用)。
- 1記事あたり平均候補数 = Union総数 / 11、および意味上の問題単位数 / 11。同一テーマの複数稿(U03/X10、U02/X09、U07/X11)は別記事として数える。『8テーマ(U01-U08)のみ』の値も併記する。

## 5. 既知例対応表(事前登録。どの文IDか。旧Checkerを正解教師にしない)

| 既知例 | Unit | 文ID(INVENTORY_01.md §3) | 備考 |
|---|---|---|---|
| OpenAI actor drift | X11 | s7 | 『They also say the models' output copied or put articles together in new ways, and removed copyright management information.』 最重要。B1回復前STOP稿 |
| OpenAI(対照) | U07 | s11(主体OpenAI明示) / s1(見出しscope拡張。旧Checkがja_sourceでSTOPした点) | U07にはactor driftは無い |
| Semiconductor 不在断定(境界・過剰Flag確認) | U08 | s25(2文が1IDに結合) | ユーザー判断: 問題視するほどではない |
| Hormuz Brent→oil prices | X09 | s2, s13(U02には不在。U02 s27は正しい限定) | 本文に不在の稿(U02)は『検出できなかった』扱いにしない |
| Space 地球を吹き飛ばす | X10 | s5(U03には不在) | U03のs13/s33は別系統の不在断定(新規扱い) |
| BYD In One Line条件落ち | U05 | s27 | 台帳 BYD-RECALL-07系の『極端な場合に部品が外れた場合』条件の欠落 |

## 6. 費用

| 項目 | JPY |
|---|---|
| 見積 中央値(22呼び出し) | 50.83 |
| 見積 高位(入力+25%・出力3倍) | 78.75 |
| 新規呼び出し停止の累計上限(中央値の1.5倍) | 76.25 |
| 1セル上限(MAX_CELL) | 8.00 |
| 参考: ANTENNA-TRIAL-01実測 | A3 1.919/call(max 2.883), A4 2.201/call(max 3.032)。入力は英語token数で補正(`cost_estimate_post_en_01.json`) |

見積 JPY50.83 <= JPY100 のため、Fable指示どおりPhase 2へ進む。累計が 76.25 に達したら新規呼び出しを停止する。

## 7. STOP条件(固定)

英語稿所在/意味が想定と違う(→今回該当: 所在差異を INVENTORY_01.md §2 に記録し、Fable規則『既知例が別稿にのみ実在する場合は追加』に従い3本追加して続行。ユーザー判断用に報告)/ STOP稿が回収できない(該当なし)/ 台帳Fact件数不一致(該当なし)/ 判定仕様を変えないとA3/A4を英語に適用できない(該当なし)/ 新しい重大な仕様候補の発見 / 費用が見積から大きく逸脱 / Productionコード変更が必要 / 未承認仕様の参照が必要。

## 8. 出力先
`er052_output/writer_dev_risk_flagger_01/post_en_trial_01/`: inputs/, flags/A3|A4/<unit>_<theme>.json, results/, logs/, cost_ledger_post_en_01.jsonl, cost_estimate_post_en_01.json, manifest_post_en_01.json, INVENTORY_01.md, LEDGER_COMPLETENESS_01.md, EN_ADAPTATION_01.md, PREREGISTRATION_01.md(本書)。Phase 3で RESULT_01.md / HUMAN_REVIEW_POST_EN_01.md を追加。

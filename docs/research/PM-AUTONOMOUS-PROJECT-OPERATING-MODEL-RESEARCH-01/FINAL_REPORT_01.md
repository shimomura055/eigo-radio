# FINAL_REPORT_01: 自律的Project運営モデル Research 最終報告(草案)

管理ID: PM-AUTONOMOUS-PROJECT-OPERATING-MODEL-RESEARCH-01 / 2026-10-14 / 費用JPY0 / ステータス: Research完了・Opus独立レビュー(条件A)の所見OF-209〜OF-224を反映済み(委任_03)・ユーザー判断待ち(規則・設定は何も変更していません)

## 1. 最重要な発見5点
1. **規則が無かったのではなく、効いていませんでした。** 調べた6つの具体例すべてで、該当する規則は既に存在していました。「明らかな不具合はユーザーに聞かず直す」という趣旨は4回も書かれたのに、10月13日に再発しています。
2. **10月13日にあなたが示した「開発側が責任を持つ」という方針が、規則ファイルに載っていません。** CLAUDE.md等を検索すると0件で、その時の委任文にしか残っていないため、毎回あなたが言い直す形になっています。
3. **AIの初期動作が「迷ったらユーザーへ」になっています。** Worker定義と「委任上限に達したらユーザー判断」の規則がそうなっており、直近の判断依頼12件のうち5件は、AI側で決められた可能性が高いと診断されました(独立確認は未実施)。
4. **PM役のFableには調べる手段がありません**(実行・編集の権限がない設計)。そのため「原因を調べる」は、委任文に書かれた時だけ起きます。
5. **「必ず守る」はずの規則に強制力がありません。** 委任回数の上限、停止通知の確認、報告の形式などは、人が守るのを期待するだけです。実際、同じProjectの中でも停止通知の確認方法が少なくとも5通りに分かれています。

## 2. 現在のFable運営が期待どおり機能していない根本原因
診断した25件の根本原因は、文書の欠陥11件、実装(ツール・仕組み)の欠陥6件、運用の欠陥8件でした。ただし運用の欠陥の多くは、文書側を直せば頻度が下がる性質です。中核は4つです。(a) 「開発側責任」の方針が規則に昇格していない。(b) Workerの既定動作が「ユーザーへ戻す」。(c) Fableの責務に原因分析と問題解決の主導が書かれていない。(d) 自律の基準が8か所以上に分散し、現行がどれか分からない。加えて、同一の記録が1件あたり11か所に書かれ、起動時にFableが読む量は約48,500字に膨らんでいます。

## 3. 外部の優れた実践例と学ぶべきこと
Anthropic、OpenAI、Cursor、GitHubの公式資料と個人開発者の実践など、22事例を調べました。個人・少人数でも使えるのは次の5点です。
- **常駐する文書は短く**(目次だけ)、詳細は必要な時に読む。長すぎる指示書はAIに無視され、ルール同士が矛盾した例がある。
- **必ず守らせたいことは、文書でなく仕組み(自動検査)で強制**し、その強制が効いているかも監査する。「文書は助言、仕組みは強制」が公式の見解。
- **完了の状態を機械が読める形で持つ。** AIの「できました」は信用せず、証拠を出させる。
- **承認が必要な境界は「取り消せない」「方針を変える」「予算」の3軸**。承認を増やしすぎると形骸化する(許可の93%が承認された実測)。
- **費用の上限は、実行1回ごとに機械で止める。**

学ばないこと: 人の確認を最小にする運用や数百の並列運用は、高スループットで失敗コストが低い大企業向けで、音声・学習コンテンツの品質リスクがある本Projectには不適です。「1日の共有予算」「PM役を常時動かす費用対効果」には外部の先行例がなく、小さな試行で確かめる対象です。

## 4. 推奨運営モデルとその理由
**案D「薄いCharter+Worker自律実行+最小の機械強制」を推奨します。** 比較した4案(A現行改善/B Worker自律/C動的切替/D=B+機械強制)で、診断した25根本原因のうち、Dは21件を解消・4件を部分対処、Bは12件解消、Aは9件解消、Cは3件解消と見込みます(定性評価)。**ただしこの件数は、本研究の作成者自身が採点した自己採点(循環評価)で、独立した検証ではありません。**独立レビュー(Opus)の指摘で、当初「解消」としていたR5(Fableが自分で検証できない問題)を「部分対処」に訂正しました(当初案の「Haikuに検査させる」は、HaikuにBash権限が無く実行できない可能性が高いため。代替としてhookによる自動実行へ変更)。Aは文書だけで、規則追加では直らなかった実績があります。Cは分類の誤りと複雑さが小規模運営に過剰です。Dは、AIが原因究明から是正・Trial・確認までを自律で進め、Fableはユーザー窓口・計画・受入・難判断に集中し、重要な節目だけOpusが独立判定します。新しい仕組みは5つに限り、規則は増やさず減らします。

## 5. 現行Project定義からの主要変更点
- **Charter新設**(旧PM_BRIEFを改訂、本文3,500字以内): 目的・役割・判断境界・完了の定義だけを常駐させる。
- **判断の8区分を明文化**: 既存仕様内のバグ修正・原因調査・安全なTrialはAI自律。新仕様の採用・品質基準の緩和・承認範囲を超える品質/費用/納期の入替え・予算の上限超過・Human Review方針はあなたが決める。
- **Worker既定動作を「ユーザー確認」から「原因究明ループ」へ**。仮説・反証・再現証拠を必須にし、同じ問題を2回直しても再発したら、やり直しではなく再計画する。
- **判断依頼には出自の記入を必須**にし、記入できないものは受け付けない。出自は7種(新仕様の採用/Gate緩和/承認済み仕様の変更/予算超過/QCD入替え/Human Review方針/**承認済みPrompt・Gate閾値等の実質変更**)。Prompt・Gate閾値・承認済み仕様に触れる変更は、gitのcommit時に分類記録が無ければ拒否する仕組み(pre-commit hook)を置く。
- **Fableの責務に原因分析・優先順位・問題解決の主導を追加**。
- **Trial/承認/配線の3状態を状態ファイルで管理**(記録単位は管理IDでなく仕様・部品単位。管理IDを付け替えても承認状態はリセットされない。承認は、あなたの実際の発言記録と照合できた時だけ記録)。
- **常駐文書を約63%削減**(Fable起動時 約48,500字→18,000字以下)。
- 差分は55項目(維持22・統合4・削除4・改訂20・新設5)。診断で有効と確認された安全装置(Opusレビュー、Production採用はユーザーのみ、停止機構、secret scan等)はすべて維持します。

## 6. 費用・時間・品質・安全性のトレードオフ
- **費用**: 導入のためのAPI費用はJPY0見込みです(モックで検証)。運営面では、Fableの起用回数と長い委任文が減るため低下を見込みますが、Fableを常時PMにする場合との費用差を測った外部データは無く、実測します。
- **時間**: 導入期間(約6〜8週間、見込み)は仕組み構築で一時的に遅くなります。定着後は往復が減る見込みです。
- **品質**: 原因調査を必須成果物にして独立判定を入れるため、向上を期待します(未検証)。
- **安全性**: 既存の安全装置(Opusレビュー、Production採用はあなただけ、停止機構、secret scan等)は維持します。**ただしProduction反映の自律化でリスク面は広がり、その抑止(保護対象の分類記録、抜き取り監査など)は、まだ検証されていない新しい仕組みに依存します。**そのため既定は「AIが分類まで行い、あなたが事後監査する」運用から始め、見逃しが1件でも出たら中止する設計にしています。
- **予算**: 実行1回ごとの上限を機械で止めることに加え、**日次または週次の合計ハード上限を設けることを推奨します**(金額はあなたが決めます)。当初は「直近の1件あたり費用(約JPY1〜5)の200倍で効果が小さい」と評価しましたが、これは開発期だけの根拠で、量産期(Family Z 1runでJPY300規模)には当てはまらないため訂正しました。共有ロックも不要です(各runの記録を予約時に合算するだけ)。

## 7. 検証・移行計画
採用後に4段階で進めます: Phase 0 現状計測(約3日)→Phase 1 文書統合と最小の仕組み(1〜2週。既存の停止機構・予算上限・secret scanは最初からブロック維持、警告のみのモードで始めるのは文書検査・報告形式の検査だけ)→Phase 2 小規模案件3〜5件で試行(3〜4週、本番音声の生成なし)→Phase 3 評価(約1週)。9つの指標(不要な判断依頼、自律解決率、原因分析の深さ、副作用の検出率、完成までの日数、費用、あなたの対応負荷、再発率、**自律決定の抜き取り監査で見つかった「本来あなたに聞くべきだった件」の見逃し数**)で効果を測ります。安全事故が1件でも起きれば即中止(Gate閾値の緩和やPromptの実質変更を、あなたに聞かず自律で行った場合も即中止)、指標が悪化した項目が2つ以上あれば撤退(元に戻す)します。Phase 2には、既存仕様内のバグ修正1件をシャドー運用で試す案件(Production接触あり、事前にあなたへ提示)を含めます。候補案件は、Std glossの不整合(OPEN-352/353)、M1 evidence runnerの停止通知問題、台帳の整理など、費用がかからないものです。

## 8. 真にユーザー判断が必要な事項(Research完了後に議論)
(7項目。作業系の依頼は含めていません。U1〜U4はOpus独立レビューを受けて追加または統合した項目です。)
1. **案D(または修正案)の正式採用と、Phase 1に着手するか**。あわせて、成功指標の目標値と撤退条件(悪化2つ以上で撤退、安全事故1件で即中止)の承認。
2. **承認済みの品質・費用・納期の床と天井の値**(例: 品質基準の下限、1件あたりの費用上限)。これを超える入替えだけをあなたに回す前提になります。数値化されていない品質項目(日本語訳の不整合など)は「新仕様の候補」としてあなたに回す扱いです。
3. **予算の初期枠と、日次または週次の合計ハード上限の金額(U3)**。実行1回ごとの上限は機械で止めます。合計上限の金額と、日次か週次か(JPY1,000/日は検討案の1つ)をあなたが決めます。
4. **「承認済み仕様内のバグ修正」の扱い(U2)**。既定は**シャドー運用**(AIが「バグか新仕様か、Prompt・Gate閾値に触れるか」の分類まで行い、Production反映の前にあなたが分類を事後監査)としてよいか。Phase 2で誤分類率を測ってから、どのクラス(例: Coffee系)に自動反映の包括承認を与えるか、その時期の決め方。
5. **Production Gateの厳格化・新しい品質基準の採用も、あなたの判断事項とするか(U1)**。当初案は「厳格化はAI自律」でしたが、あなたの2026-10-13の枠組み(Validator・Gateの安全基準変更はあなた)に揃えると、厳格化も(不合格が増え量産性に影響するため)あなたの判断になります。この整合でよいか。Trial(検証専用の隔離環境)内の厳格化はAI自律のままです。
6. **Human Reviewの方針**(何を人が聴くか、量産時に許容する頻度)。
7. **CLAUDE.mdのPM層(Opusレビュー、ループ上限、最新モデル、並列実行の運用規則)を削除してPM_GOVERNANCEへの参照にまとめるか(U4)**。ここはあなたが過去に出した指示を含みます。安全上の不変条件4点(Production採用はあなただけ/3状態の区別/Gate迂回禁止/停止機構に触れない)は、削除せずCLAUDE.mdとWorker定義の両方に残す前提です。

---
(以降は詳細・根拠。上の8節は約5,200字(委任_03でOpus所見を反映して当初の2,500〜4,000字目安を超過。判断事項は§8の7項目)です。)

## 詳細Research Reportへのリンク
- 外部調査: `docs/research/PM-AUTONOMOUS-PROJECT-OPERATING-MODEL-RESEARCH-01/EXTERNAL_RESEARCH_01.md`
- 内部診断: `docs/research/PM-AUTONOMOUS-PROJECT-OPERATING-MODEL-RESEARCH-01/INTERNAL_DIAGNOSIS_01.md`
- 運営モデル比較: `.../OPERATING_MODEL_COMPARISON_01.md`
- 推奨Project定義(差分表を含む): `.../RECOMMENDED_PROJECT_DEFINITION_01.md`
- 導入・検証計画: `.../ROLLOUT_AND_VALIDATION_PLAN_01.md`
- 出典の機械可読一覧: `.../sources_01.json`

## 根拠URL一覧(sources_01.jsonより)
1. Anthropic「Building effective agents」(2024-12-19、primary) https://www.anthropic.com/engineering/building-effective-agents
2. Anthropic「How we built our multi-agent research system」(2025-06-13、primary+measured) https://www.anthropic.com/engineering/multi-agent-research-system
3. Anthropic「Effective harnesses for long-running agents」(2025-11-26、primary) https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
4. Anthropic「Building a C compiler with a team of parallel Claudes」(2026-02-05、primary+measured) https://www.anthropic.com/engineering/building-c-compiler
5. Anthropic docs「Best practices for Claude Code / costs / headless」(unknown、primary) https://code.claude.com/docs/en/best-practices
6. Anthropic「How we built Claude Code auto mode」(2026-03-25、primary+measured) https://www.anthropic.com/engineering/claude-code-auto-mode
7. Anthropic「Measuring AI agent autonomy in practice」(2026-02-18、measured) https://www.anthropic.com/research/measuring-agent-autonomy
8. Anthropic「Demystifying evals for AI agents」(2026-01-09、primary) https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
9. OpenAI「Harness engineering: leveraging Codex in an agent-first world」(unconfirmed (HN comment says 2026-02-11); fetched via r.jina.ai、primary (self-report)) https://openai.com/index/harness-engineering/
10. OpenAI「A practical guide to building agents」(unknown; fetched via r.jina.ai、primary) https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf
11. Cursor「Scaling long-running autonomous coding」(unknown、primary (self-report)) https://cursor.com/blog/scaling-agents
12. GitHub「Automate repository tasks with GitHub Agentic Workflows」(2026-02-13、primary) https://github.blog/ai-and-ml/generative-ai/automate-repository-tasks-with-github-agentic-workflows/
13. GitHub「Spec-driven development with AI (Spec Kit)」(2025-09-02、primary) https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/
14. Cognition「Devin's 2025 Performance Review」(unknown、claim (vendor)) https://cognition.ai/blog/devin-annual-performance-review-2025
15. METR「Recent Frontier Models Are Reward Hacking」(2025-06-05、measured) https://metr.org/blog/2025-06-05-recent-reward-hacking/
16. kai-kou (individual)「Claude Code: confirmation limited to 6 kinds (Qiita series 7)」(2026-09-30、implementation+experience (book promo)) https://qiita.com/kai_kou/items/a3c2ce2c7a2e04dc690b
17. kai-kou (individual)「Resident rule byte budget, promote=delete (Qiita series 8)」(2026-10-01、implementation+experience (book promo)) https://qiita.com/kai_kou/items/e75f36039dbce6a1050b
18. eiger_inc (Zenn)「AIを鵜呑みにせずに頼る」(2026-10-13、experience) https://zenn.dev/eiger_inc/articles/aa7c16ec7b6895
19. k_iijima (Zenn)「Claude Code の deny だけでは git push を止めきれない話」(2026-10-12、experience+docs) https://zenn.dev/k_iijima/articles/ae926619c45882
20. kuu_dqx (Zenn)「Claude Code を使い始める人へ 5か月の実運用で事故になった7つ」(2026-10-13、experience) https://zenn.dev/kuu_dqx/articles/claude-code-first-things-to-set
21. whshido (Zenn)「PVほぼゼロの個人サイトをClaude Codeで改善自動化(仕組み編)」(2026-10-13、implementation (no results yet)) https://zenn.dev/whshido/articles/pv-zero-site-claude-code-auto-improve
22. joinclass (Qiita)「Claudeの指揮者エージェントを太らせない設計」(2026-10-09、experience) https://qiita.com/joinclass/items/9bb292ceb6418f3f9fad
23. genda_jp (Zenn)「Haiku 5.5 を機にサブエージェントを見直した」(2026-10-08、experience) https://zenn.dev/genda_jp/articles/haiku-5-5-subagent-roles
24. kai-kou (individual)「Multi-agent whiteboard: per-agent files + single aggregator (Qiita series 9)」(2026-10-05、implementation (self-test only)) https://qiita.com/kai_kou/items/f00c68d667085741d34c
25. GitHub docs「GitHub Copilot cloud agent docs」(unknown、primary) https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent
26. OpenAI docs「Codex AGENTS.md guide」(unknown、primary (read; not cited as case)) https://developers.openai.com/codex/guides/agents-md
27. dsifry (individual OSS)「metaswarm README」(unknown、claim (not adopted)) https://raw.githubusercontent.com/dsifry/metaswarm/main/README.md
28. Hacker News「HN thread: Harness engineering」(2026-06-05 (submission)、opinion (reaction only)) https://hn.algolia.com/api/v1/items/48416264

注: 外部調査書の「事例N」番号とsources_01.jsonのidは、事例1〜21は同一、事例22=id22+23、事例23(主張・不採用)=id27、id24は個別ファイル+単一集約者の個人実装(論点E)、id25〜26,28は補助資料。

## 既存Project定義との対応表
詳細は`RECOMMENDED_PROJECT_DEFINITION_01.md` §12の差分表(全55行)。ファイル単位の要約:

| 対象 | 区分 | 要点 |
|---|---|---|
| CLAUDE.md | 改訂 | ユーザー定義部分は維持。PM層の再掲を削除し参照へ |
| PM_BRIEF.md | 改訂 | Project Charter化(本文3,500字以内)+判断区分表を収容 |
| PM_GOVERNANCE.md | 改訂・統合・削除 | 履歴分離、自律基準の統合、報告形式の一本化、STOP条件・上限の置換。Opusレビュー・secret scan・26-5は維持 |
| sandwich-pm.md | 改訂 | UDR既定撤回、責務追加、受入検証 |
| sonnet-worker.md | 改訂 | UDR文化撤回、報告先をFable一本化、原因究明ループ、固定ブロック吸収 |
| opus-consultant.md / haiku-worker.md | 改訂 | 独立判定の観点追記 / tools欄と本文の整合・受入検査担当 |
| 委任テンプレート・固定ブロック | 改訂・削除 | ミッション型(2,000字以内)に。固定ブロックはagent定義へ |
| 各台帳(DECISION_LOG/OPEN_ITEMS/UDR/REPORT_LEDGER等) | 改訂・統合・維持 | 詳細1箇所+ポインタ、OPENを作業キュー化、UDRに出自必須。CURRENT_SPEC/OPUS_FINDINGS_LEDGERは維持 |
| 新設(5点) | 新設 | state_gate、stop_check、budget_gate、docs_lint、hooks+強制回帰テスト |

## 改訂履歴(委任_03: OF-xxx反映)
- OF-224: §4に「21件解消・4件部分対処」への訂正、自己採点(循環評価)の明記、R5訂正。§6安全性を「リスク面は広がり、抑止は未検証の仕組みに依存」へ。§6予算を合計ハード上限推奨へ(OF-222)。
- OF-209/OF-210/OF-215/OF-222/OF-223: §5(出自7種・pre-commit、状態の記録単位)、§7(Phase 1のブロック維持、M9、撤退条件、シャドー運用1件)に反映。
- §8: 旧5項目に対し、U1(OF-216)・U2(OF-217)・U3(OF-222)・U4(OF-221)を追加し、重複するものを統合して7項目へ整理(作業系項目を含めない)。

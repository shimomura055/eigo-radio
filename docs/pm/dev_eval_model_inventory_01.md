# 開発・評価用モデル棚卸し 01 (PM-DEV-EVAL-LATEST-MODEL-RULE-01, 2026-10-09, API支出 0円)

凡例: 【公式取得】=2026-10-09に公式ページをHTTP取得して確認 / 【repo】=repo内の記録 / 【見積】=計算値 / 未確認=取得・照合できず。
本書は「開発・評価用途」の棚卸しであり、本番ライン(Production)に織り込むモデルの判断ではない(別判断)。
注意: 公式ページの取得は静的HTML(スクリプト非実行)のテキスト化による。API(/v1/models)は呼んでいないため、当方のAPIキーで各モデルが実際に呼べるか(権限・可用性)は未確認。

## 1. vendor別: 最新世代の最上位系・推奨系(公式)
### OpenAI (キーあり)  出典 https://developers.openai.com/api/docs/models , https://developers.openai.com/api/docs/pricing (2026-10-09取得, HTTP 200)
公式の案内文(原文要旨): 迷ったらGPT-6 Astra(複雑な推論・コーディング向け旗艦)。知能とコストのバランスはGPT-6.1 Sol。コスト重視・大量処理はGPT-6 Luna。
| 階層 | モデルID | Standard $/1M (Input / Cached / Cache write / Output) | 備考 |
|---|---|---|---|
| 最上位(旗艦) | gpt-6-astra | 10.00 / 1.00 / 12.50 / 50.00 | 知識カットオフ Apr 30, 2026 |
| 推奨(バランス) | gpt-6.1-sol | 2.00 / 0.10 / 2.50 / 10.00 | 「Near-Astra performance」。Batch/Flex は半額 |
| 効率系 | gpt-6-luna | 0.10 / 0.01 / 0.125 / 0.50 | 知識カットオフ May 18, 2026 |
| (旧)Cyber系 | gpt-5.6-sol | 4.00 / 0.40 / 5.00 / 20.00 (short context, 公式は「promotional pricing 2026-11-21まで」と注記) | 現行ページではCyber models欄に掲載。評価用の最新ではない |
- 重要な事実1: 現行の公式モデル一覧に gpt-6-sol は載っておらず、同階層は **gpt-6.1-sol** になっている【公式取得】。repoの過去記録(DECISION_LOG L12795付近、2026-09-29のAPI実測)では gpt-6-sol が存在していた【repo】。gpt-6-sol がAPI上で今も有効か、gpt-6.1-solが後継かの公式明記は未確認。
- 重要な事実2: gpt-6.1-sol の単価($2/$10)は、評価で使った gpt-5.6-sol の登録単価($5/$30)より安い【公式取得/repo】。

### DeepSeek (キーあり)  出典 https://api-docs.deepseek.com/quick_start/pricing (2026-10-09取得, HTTP 200)
| 階層 | モデルID | $/1M Peak (cache hit / miss / output) | Off-peak (半額) |
|---|---|---|---|
| 最上位(Pro) | deepseek-v4-pro (DeepSeek-V4-Pro-0813) | 0.044 / 1.32 / 3.96 | 0.022 / 0.66 / 1.98 |
| 下位(Flash) | deepseek-flash (DeepSeek-V4.1-Flash) | 0.006 / 0.30 / 1.20 | 0.003 / 0.15 / 0.60 |
- 公式脚注: 旧名 deepseek-v4-flash は引退済みで、リクエストは V4.1-Flash で提供されFlash価格で課金される【公式取得】。両モデルとも thinking(推論)モード対応、コンテキスト1M。
- 最新世代の最上位系 = deepseek-v4-pro。追加Trialで使った deepseek-v4-flash(実体 V4.1-Flash)は下位系。

### Gemini (キーあり)  出典 https://ai.google.dev/gemini-api/docs/models , https://ai.google.dev/gemini-api/docs/pricing (2026-10-09取得, HTTP 200)
- 公式一覧の最新世代: Gemini 3.8 Flash(「Our most intelligent Flash model」、Stable、New)。Pro系は Gemini 3.1 Pro(gemini-3.1-pro-preview、Preview)。3.8世代のPro系は一覧に見当たらない。
- 価格(Paid, $/1M): gemini-3.8-flash 入力 $0.75 / 出力 $3.75(2026-12-31まで、2027-01-01から $1.50 / $7.50)。gemini-3.1-pro-preview 入力 $2.00 / 出力 $12.00(prompts<=200k)。
- 「最上位系」をどちらとするか(最新世代のFlashか、世代は古いがPro階層か)は公式の明記がなく、判断が必要。【未確認: 公式の序列定義】
- 評価用途でのGemini テキストモデル使用実績はrepo内で確認できない(Geminiは本番TTSのみ。MODEL_OPTIONS_COST_01.md L17-L20)。

### (参考) Claude  出典 https://docs.anthropic.com/en/docs/about-claude/models/overview (2026-10-09取得)
- 公式: 迷ったらClaude Opus 5.5。要求の高い推論・長期agent作業にはClaude Fable 5.1(最上位、$10/$50)。Sonnet 5.5($2/$10)、Haiku 5.5。
- repoにはANTHROPIC_API_KEYなし。Claudeは Claude Code のsubagent経由のみ(sandwich-pm=fable、opus-consultant=claude-opus-5-5 [tools: Read/Grep/Glob のread-only]、sonnet-worker=sonnet、haiku-worker=haiku)【repo: .claude/agents/*.md】。

## 2. pricing_snapshot.json の登録状況  (er005_output/cost_baseline_01/pricing_snapshot.json)
| モデル | 登録 | 単価($/1M in/cached/out) | 公式(2026-10-09)との差 |
|---|---|---|---|
| gpt-6-astra | 登録済み(OFFICIAL_PRICING_PAGE_FETCHED) | 10 / 1 / 50 | 一致 |
| **gpt-6.1-sol** | **未登録** | - | 公式 2 / 0.10 / 10 |
| **gpt-6-sol** | **未登録** | - | 現行公式ページに掲載なし(旧記録 2.00/0.20/10.00 は DECISION_LOG のみ) |
| gpt-6-luna | 登録済み(PROJECT_INTERNAL_RECORD) | 0.1 / 0.01 / 0.5 | 一致 |
| gpt-5.6-luna | 登録済み(PROJECT_INTERNAL_RECORD) | 0.2 / 0.02 / 1.2 | 現行公式ページに掲載なし(未確認) |
| gpt-5.6-sol | 登録済み(OFFICIAL_SOURCE, 2026-08-17) | 5 / 0.5 / 30 | 現行公式 4 / 0.4 / 20(promotional, 2026-11-21まで)と**不一致**。登録単価が古い |
| deepseek-v4-flash | 登録済み(OFFICIAL_SOURCE) | Peak 0.3 / 0.006 / 1.2 (+Off-peak別tier) | 一致(実体はdeepseek-flash) |
| **deepseek-v4-pro** | **未登録** | - | 公式 Peak 1.32 / 0.044 / 3.96 |
| Gemini テキスト(3.8-flash / 3.1-pro) | **未登録**(TTS 3種のみ登録) | - | 上記のとおり |
- 示唆: 評価の最新モデルへ切り替えるには gpt-6.1-sol・deepseek-v4-pro(必要ならGemini)の単価登録が先に必要(登録は費用ガードの前提)。登録はこの委任の範囲外で、未実施。

## 3. 直近2週間の評価Trialで使われたモデル(repo Grep: er052_output/**/PREREGISTRATION*.md・DESIGN*.md・RUN_LOG*.md・docs/pm/delegation_log/2026-10-0*)
| Trial | 使用モデル(評価・検証用途) | 最新世代の最上位/推奨か |
|---|---|---|
| WRITER-EVAL-DUAL-LLM-METHOD-TRIAL-01 前半(委任_02) | gpt-6-luna(主)、gpt-5.6-luna(2rep各) | gpt-6-luna=最新世代の効率系(最上位ではない)。gpt-5.6-luna=旧世代 |
| 同 追加Trial(委任_04/04b) | gpt-5.6-sol(2rep)、deepseek-v4-flash(実体V4.1-Flash、2rep) | どちらも最新の最上位/推奨ではない(下表) |
| FACTLOCK-ASTRA-E2E-TRIAL-01 | Writer: gpt-6-astra(Production経路のLuna Writerと比較)、Checker等: gpt-6-luna、ラベル付け: Claude Sonnet(sonnet-worker 3本) | Astra=最上位。Luna=効率系。Sonnetは最上位でない |
| FACTLOCK-WRITER-REDESIGN-TRIAL-01 (10/08) | gpt-6-luna, gpt-6-sol(Sol N=1・マトリクス), gpt-6-astra | gpt-6-solは現行公式ではgpt-6.1-solへ世代更新(上記) |
| ALL-6-LUNA / OPEN-243 等 (10/08) | gpt-6-luna(Production配線の検証)、gpt-5.6-luna(比較基準) | 本番ラインの評価は「別判断」(第5節の区別参照) |
- Gemini: 評価用途での使用は確認できず(上記)。

## 4. 補足
- 当方が確認した限り、直近Trialで gpt-6.1-sol・deepseek-v4-pro・Gemini 3.8系を評価に使った記録はない。
- ここでの「最上位系・推奨系」は公式ページの案内文に基づく。性能序列(ベンチマーク)は未確認で、推測していない。

## 5. 旧モデル・下位モデルが入っている評価計画の整理(ユーザー要求の1.理由 / 2.最新に置換した場合の影響 / 3.置換推奨案)
費用はすべて【見積】。方法: 実測トークン(WRITER-EVAL追加Trialのlogs/*_raw.jsonl: 1モデル2rep合計 入力 約21,074 tok・出力 sol 約3,017 tok、DeepSeek-Flash 入力 約19,892 tok・出力 約29,932 tok)× 本書第1節の公式単価、USD/JPY=160(repoの既存換算)、キャッシュ割引なし。置換先モデルの推論量(出力token)は未測定のため、同じトークン量と仮定した参考値であり実費ではない。置換先の単価は pricing_snapshot.json に未登録のため、実行前に登録が必要。

### 5-1. WRITER-EVAL-DUAL-LLM-METHOD-TRIAL-01 追加Trial(Fable最終判定 REJECTED 済み、10/09)
| 対象 | 1.使った理由(事実) | 2.最新モデルに置換した場合の影響 | 3.置換推奨案 | 費用見積(2rep) |
|---|---|---|---|---|
| gpt-5.6-sol | 委任_04の記録: 「登録済み単価」のある上位階層だったため(MODEL_OPTIONS_COST_01.md L18、PREREGISTRATION_02 s2)。当時 gpt-6.1-sol の存在・単価は未確認だった。実行前の「なぜ最新でないか」の明記はなし。実費 JPY 25.98 | 旧世代(5.6)のため、「Sol階層でも重大を拾えない」という結論(M1: 2/6がC、REJECTED)が最新Solでも同じかは未検証。最新Solは単価が安く($2/$10 対 登録$5/$30)、置換で費用は下がる見込み。結論が変わる可能性も、変わらない可能性もある(未測定) | gpt-6.1-sol(推奨系)、必要なら gpt-6-astra(最上位)で同一入力・同一事前登録の追加2rep。事前登録は PREREGISTRATION_03 として別立て(今回は実施せず) | gpt-6.1-sol 約JPY 11.6 / gpt-6-astra 約JPY 57.8 |
| deepseek-v4-flash(実体V4.1-Flash) | 委任_01〜04: 別vendorの代表としてキー・実績(er005)があり、公式単価を実行前に登録できたため。下位系(Flash)である点の理由明記はなし。実費 JPY 6.06 | DeepSeekの最上位は deepseek-v4-pro。C判定数は Flash で4/6(最多)だった。Proで置換すると「DeepSeek系だから見逃す/拾う」の切り分けが「下位だから」の可能性を除いて明確になる。出力(思考)token量が増え費用が上がる可能性 | deepseek-v4-pro(Peak単価で同一入力2rep、max_tokens 32000据置)。単価要登録 | 約JPY 23.2(Peak。Off-peakなら半額、ただし費用算出はPeakを使う既存方針) |
| gpt-6-luna(主) | ユーザー指示「Lunaだけで確認(Deepseekは使わない)」(委任_02、ユーザー指示)。gpt-6-lunaは最新世代の効率系(Luna系の最新)で、旧世代ではないが最上位でもない | ユーザー指示に基づくためダウングレードには当たらない。ただし最上位系ではないので、同一入力を上位で測れば、Lunaの限界か方式の限界かの切り分けが進む。実績: gpt-6-lunaは最新なのにM1のC判定が0/6で、旧世代(5.6-luna 2/6)より悪かった(RESULT_TABLE_02) | 置換でなく併走: 上の gpt-6.1-sol / astra を比較に加える(Lunaは本番Writer/Checkerと同系統なので自己系統バイアスの基準として保持)。これはユーザー指示と矛盾しない追加であり、実施判断はFable/ユーザー | 追加分は上のsol/astra行に含む |
| gpt-5.6-luna | 委任_02: 旧世代Lunaとの世代比較のため。単価登録済み(0.20/0.02/1.20)。実行前の「例外理由」明記は確認できない | 例外1(既存結果との比較)に該当しうるが、今後は実行前に明記が必要。評価者としての最新置換は gpt-6-luna で既に実施済み(同Trial内) | 新規評価では使わない。比較基準としての再利用のみ可(理由を実行前に明記) | 0(既存結果を再利用) |

### 5-2. FACTLOCK-ASTRA-E2E-TRIAL-01: 評価ラベル付けを Claude Sonnet(sonnet-worker 3本)で実施
- 1.理由: 設計書(DESIGN_E2E_01 s7、PREREGISTRATION_01)には「Sonnet worker x3が重大/軽微をラベル」とあるが、なぜSonnetかの明示的な理由記述は確認できない(未確認)。構造的な事実としては、(a) ANTHROPIC_API_KEYがなくClaudeはClaude Codeのsubagent経由のみ、(b) 実行層(書き込み可能)は sonnet-worker、(c) opus-consultant は tools=Read/Grep/Glob のread-onlyでファイルを書けない、(d) 553行・3分割の大量作業。ラベルはSonnet暫定推測であり、確信度0.35〜0.8、ユーザー確認前(EVAL_E2E_01 s6)。
- 2.最新(最上位)に置換した場合の影響: 現行のClaude最上位は Fable 5.1、推奨は Opus 5.5(公式)。Sonnet 5.5は現行世代だが最上位でない。再ラベルで、重大/軽微の線引き(OC-3/OC-8の同型メモに残る基準の不統一)や、判定不能(床効果)になっている2-1の要確認フラグ、境界例11件(B-01〜B-11)の揺れが減る可能性がある。逆に結果が変わると、Fable最終判定済みの判定線(E2E評価)の数値の一部が動くため、Fable再判定が必要になる。API支出は0円(サブスク枠内、ただしセッションのトークン消費はある)。
- 3.置換推奨案: 全553行の再ラベルは重く、制約もある。(i) 優先: 境界例11件+重大候補+STOP妥当性行(判定に直結する少数)だけを、Opus 5.5(read-onlyなので結果はテキストで返し、sonnet-workerがファイルへ転記)で盲検再ラベルし、Sonnetラベルとの一致率を出す。(ii) 全件再ラベルは、Opusの回数上限(任意レビュー1日2回等、CLAUDE.md/PM_GOVERNANCE 11節)の枠内に収まるか、または上限の別扱いを決める必要があり、Fable/ユーザー判断事項。(iii) Fable 5.1自身をラベラーにする案もあるが、PM層が評価者を兼ねる独立性の問題があり、未検討(判断はFable)。実施は本委任の範囲外。
- 注: ユーザーの「勝手なダウングレード禁止」は今後の運用が対象。本Trialの実施は規則採用(2026-10-09)の前の判断であり、遡及的な違反認定ではなく、整理対象として報告する。

### 5-3. 未着手候補(EVAL_E2E_01 s8 (b) 凍結JAでEN段+Checkerだけ再実行 等)
- 区別: (b)で動かすEN翻訳段・Checker・Writerは「本番ラインに織り込まれているモデルの性能確認」であり、ユーザー指示の第4項(本番ラインにどのモデルを織り込むかは別判断)および第2項の例外(ライン組み込み候補としてモデル自体の性能確認が必要)に該当する。したがってラインのモデル(現行 gpt-6-luna 等)を最新モデルへ替えてはならない(替えると評価対象が変わる)。
- ただし、その評価に付随する評価者・ラベラー・判定器(盲検ラベル、pairwise判定、重大/軽微の判定者など)は「開発・評価用途」であり、最新原則の対象。ラベラーの置換は5-2と同じ扱い。
- 実行前に、使用モデル名・最新か・最新でない場合の理由(例外2: ライン構成の性能確認のため)を報告に明記する。

### 5-4. その他、発見事項(実装・実行はしていない)
1. FACTLOCK-WRITER-REDESIGN-TRIAL-01(10/08)で使用した gpt-6-sol は、現行の公式一覧では gpt-6.1-sol に置き換わっている。過去結果(6-sol N=1等)を再利用する際は、世代差を明記する必要がある。
2. pricing_snapshot.json の gpt-5.6-sol 登録単価($5/$30)は現行公式($4/$20、promo)と不一致。過去の費用ガード計算は登録単価で行われているため保守側(高め)だが、更新要否はFable判断。
3. 今回のWRITER-EVAL追加Trialの結論(REJECTED)を、最新モデルで再測定するかどうか(5-1の置換案)は、新規Trial扱い(事前登録・費用上限・ユーザー確認が必要)。本委任では提案のみ。

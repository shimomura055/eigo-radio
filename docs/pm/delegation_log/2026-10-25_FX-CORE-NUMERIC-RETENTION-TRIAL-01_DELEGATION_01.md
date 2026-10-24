# 委任文(Fable→sonnet-worker)
管理ID: FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_01(Phase 0: 根本原因の精査+既存artifactの決定論的分析+改善方式の設計+Opus条件Aレビュー依頼書。**API 0円**。LLM呼出・Web検索・有料runは禁止。実装・Phase 1有料Trialは次委任=Opusレビュー後のFable Go)
Family: X / 初回検証記事: 『月は少しずつ縮んでいる?』(moon_shrinking) / Status: TRIAL_APPROVED(ユーザー2026-10-25) / Production採用・配線: 未承認 / 到達可能Status: VALIDATED/REJECTED/USER_DECISION_REQUIRED

## 0. ユーザー原文(2026-10-25、逐語。まず `docs/pm/delegation_log/2026-10-25_FX-CORE-NUMERIC-RETENTION-TRIAL-01_USER.md` に以下を一字一句そのまま保存すること)

```
# Claude Code指示｜Family X 中核数値の適切な保持・過剰掲載防止Trial

## 1. 承認事項・Status

ユーザーは、Family X共通の「中核数値保持改善Trial」を正式に承認しました。

- **Status：TRIAL_APPROVED**
- 対象：Family X
- 初回検証記事：『月は少しずつ縮んでいる？』
- 到達可能Status：VALIDATED／REJECTED／USER_DECISION_REQUIRED
- **Production採用・配線：未承認**

本指示はTrial実施の承認であり、新仕様の正式採用承認ではありません。

## 2. 目的

現在、B3が【中核数値】を指定しても、Writerがそれを使用せず、記事の主題を理解するために不可欠な数字まで脱落する問題が発生しています。

これを改善してください。

ただし、**中核数値をすべて本文に入れることは目的ではありません。**

実現すべき状態は次の2点です。

1. 記事の中心的な問いに答えるために不可欠な数値は、最終本文まで確実に保持する。
2. それ以外の数値をむやみに追加せず、自然さ・面白さ・聞きやすさを維持する。

数字を増やすのではなく、**必要十分な数字を適切に残すこと**が目的です。

## 3. 今回の記事での品質要件

対象：Family X『月は少しずつ縮んでいる？』

| 情報 | 要件 |
|---|---|
| 月が約42〜46m縮小した | **必須。最低限この情報は本文に残す** |
| 約4億年前からの推定 | 必要。推定の前提・期間を正確に扱う |
| 約11cm／100万年 | 不要 |
| 冷却モデル予測750m〜1.1km | 不要 |

なお、「約4億年前から」は研究上の推定条件・時間範囲を正確に表現してください。現在まで継続的に同じ速度で縮小したと誤解させないこと。

上記は今回の記事の評価基準であり、数値や具体的な語句をFamily X共通Promptへ固定するものではありません。

また、不要とした数値を記事へ追加して品質を高めようとしないでください。

## 4. 根本原因の調査と設計

まず、既存のCURRENT_SPEC・B3・Writer W-1・R1/R2・数値丸め仕様・関連Trialを確認してください。

特に以下を整理してください。

- B3が【中核数値】を指定する本来の役割
- Writerへ渡る情報と、その使い方
- Writerで数値が脱落する原因
- R1/R2で数値が脱落・追加される可能性
- 既存の品質Gateで何を検査しているか
- どこへ対策を設けるのが最も効率的か

**新たに「重要数値選定システム」を重複して作ることは避けてください。**

既存B3の判断を活かし、必要であればその出力やWriterとの契約を改善する方向で設計してください。

ただし、単純に「【中核数値】は全部必須」とする方式は禁止します。

Opusによる独立設計レビューを実施し、既存仕様との整合性、過剰掲載リスク、QCDへの影響を確認してください。

## 5. Trialの進め方

### Phase 1：月の記事で検証

改善方式をDEV／Trial専用経路で実装・検証してください。

評価対象はWriter初稿だけではありません。

**B3 → Writer R0 → R1 → R2 → Standard／Advanced最終本文**を通じて、重要数値が適切に維持されるか確認してください。

検証項目：

- 必須の縮小量が残っているか
- 必要な期間情報が正確に伝わるか
- 不要な数値が入り込んでいないか
- 数字を残すために文章が不自然になっていないか
- 数値の事実関係、単位、推定条件に誤りがないか
- 既存の丸め仕様と整合するか

### Phase 2：過去のFamily X記事で横展開検証

Phase 1で方式が成立したら、**中核数値を多く含む過去のFamily X記事**を選定して同じ方式をTrialしてください。

特に、過去の調査で数値脱落が確認されたイグ・ノーベル賞記事、コーヒー記事などを候補としてください。

検証では、必須数値が残るかだけでなく、**不要な数値まで大量に本文へ取り込まないか**を重点的に評価してください。

過去記事の正式公開版は変更しないこと。

検証対象や結果は、数値の選定数・必要数・最終掲載数・不要掲載数が分かる形で記録してください。

## 6. 自律的な問題解決

今回のTrialでは、初回の失敗だけで「改善できませんでした」と報告して終了しないでください。

承認範囲内で、

**原因究明 → 改善設計 → Trial → 結果分析 → 必要な修正・再検証**

を自律的に進めてください。

同じ方式で改善見込みのないTrialを繰り返すのではなく、原因・設計・工程の見直しを行ってください。

ただし、以下は厳守してください。

- 承認済みScope・品質基準・費用上限を守る
- 明示STOP・安全STOP・必須Gateを守る
- 承認範囲を超える新仕様・重要なQCD変更はユーザー判断を求める
- Trial回数だけを理由に停止しない
- Productionを無断変更しない

## 7. QCD・効率化

優先順位：**品質 ＞ 完成速度 ＞ 量産単価 ≫ 開発費**

- 既存成果物・中間データを最大限再利用する
- 不要なWeb検索・LLM再生成を避ける
- 独立作業は原則並列化する
- 数値保持のための追加LLM処理が必要か慎重に評価する
- 決定論的な検査で十分な部分は、低コストな方法を優先する
- 品質維持に不要な過剰検査を増やさない

開発費と量産単価への影響を区別して評価してください。

量産単価70円／記事セットの目標を踏まえ、継続的に発生するコスト増分を最小化してください。

## 8. Trial Closeout・報告

Fableによる独立評価を行い、以下を報告してください。

1. **根本原因と採用候補方式**
   - 既存B3をどう活かしたか
   - Writer／R1／R2／Validatorのどこを改善したか

2. **月の記事の検証結果**
   - 必須数値の保持状況
   - 不要数値の混入状況
   - Standard／Advancedの文章品質

3. **過去記事での検証結果**
   - 記事別の中核数値数、必要数、掲載数、不要掲載数
   - 数値の過剰掲載や文章品質低下の有無

4. **QCD影響**
   - 品質上の利点・残存リスク
   - 生成時間への影響
   - 量産単価への増分
   - Trial実費

5. **Trial Closeout**
   - REJECTED／VALIDATED／USER_DECISION_REQUIRED
   - Fable独立評価
   - Production採用する場合の必要作業・影響範囲
   - SSOT／Git反映状況

### 最終Gate

Trialが成功しても、**ユーザーの明示承認なしにProduction採用・配線へ進まないこと。**

月の記事のProduction再実行も、正式採用判断後とします。

本Trialの目的は、単に月の記事を完成させることではありません。

**Family X全体で、記事の面白さを損なわずに、伝えるべき数字だけを確実に伝えられる仕組みを確立することです。**
```

## 1. Fableが把握している前提(鵜呑みにせず該当箇所を再確認)
- 直前の原因究明: `docs/research/FAMILY-X-MOON-SHRINKING-PRODUCTION-01/NUMERIC_DROPOUT_ROOT_CAUSE_01.md`、FACT_CHECK_02/03、RUNTIME_EVIDENCE_01/02。結論=Family X Writer数字規則5「【中核数値】の印が付いた数字だけを使える」(`er053_family_x_factlock_ja_writer_01.py:87-94`)は許可のみで必須化・Gateなし=仕様の空白。run_ms_01(公開中・暫定版、本文に数値0)、run_ms_02(W-1以降再実行、text only、再脱落)。ig_nobel_2026は中核数値0/3、coffee_pricesは1/5しか本文に残らなかった実績。
- 管理: OPEN-505(数値脱落)、UDR #189(A暫定許容/B必須化規則Trial→採用→再実行/C再々実行、推奨B)。**本指示はUDR #189への回答に相当**(ユーザーは「Trial承認、ただし『全部必須』方式は禁止、必要十分な数値の保持」という形で判断)。UDR #189=判断済みに更新し、OPEN-505に本管理IDへの接続を追記。
- X経路: 調査→事実台帳(ledger)→B3(`er053_b3_deterministic_producer_01.py` 等の決定論的注記、【中核数値】印)→日本語Writer W-1(`er053_family_x_factlock_ja_writer_01.py`)→R1/R2→忠実英訳→Std/Adv。Writer数字規則・数値丸め仕様は `CURRENT_SPEC.md` を「中核数値」「数字規則」「丸め」「B3」「factlock」でGrep。
- 既存Gate: er053系内部検査(`:798` 年/序数/名前埋込のcore禁止)、FactLock系の事実検査、R1/R2の役割はCURRENT_SPECで確認。
- 過去Trial照合(PM_GOVERNANCE 21節 A/B/C分類)は必須: `DECISION_LOG.md`/`DECISION_LOG_HISTORY.md`/`OPEN_ITEMS.md`/`OPEN_ITEMS_HISTORY.md`/`docs/research/` を「中核数値」「数値脱落」「数字」「numeric」「core value」等でGrep。過去に不採用になった方式の無断再導入禁止。
- Family X Production file(er053系/er019系/Writer Prompt/閾値/flag)の編集は本委任では禁止。設計の実装はDEV/Trial専用経路(新規DEV module、Prompt override注入、DEV出力dir)で行う前提で設計する。

## 2. Phase 0 作業(API 0)
A. **決定論的分析(無料)**: 既存run artifactを使い、数値が「どの段で」落ちるかを段別に集計する分析script(DEV、例 `er114_fx_numeric_trace_01.py`、出力は `er114_output/fx_numeric_trace_01/`)を作る。対象=moon_shrinking run_ms_01/run_ms_02、ig_nobel_2026、coffee_prices(+他に中核数値の多いX run があれば追加、公開版は読むだけ)。各runについて: B3が印を付けた【中核数値】の一覧(選定数)、W-1 R0/R1/R2/日本語最終/英訳Std/Advそれぞれでの各中核数値の有無(表記揺れ・丸めを考慮した照合規則を明記)、本文に入った非中核数値の数(不要掲載数の候補)。これがユーザー原文§5-2「選定数・必要数・最終掲載数・不要掲載数」の計測器の原型になる。「必要数」は今回ユーザー表(§3)と、過去記事では「記事の中心的な問いに答えるために不可欠か」の判定基準を設計書で定義(判定はPhase 1以降、Phase 0では基準案のみ)。
B. **根本原因の精査**: §4の6項目を `ROOT_CAUSE_02.md` に整理(前回ROOT_CAUSE_01を踏まえ、B3→Writer間の契約=何がどの形式でWriterに渡るか、Writer Promptのどの文言が「使わない」方向へ働くか、R1/R2で数値が落ちる/増える経路、英訳段での保持、既存Gateの検査対象、対策の最適配置)。R0/R1/R2それぞれの脱落寄与はAの実測で裏付ける。
C. **改善方式の設計 `DESIGN_01.md`**(複数案を比較し推奨1案):
   - 禁止: 「【中核数値】全部必須」/新しい重要数値選定システムの重複構築/不要数値の追加。
   - 方向性の例(採否はSonnet設計判断): B3が既に持つ順位付け(derive_ranks等)から「主題に不可欠な数値=必須1〜2個(例: 主数値+その前提条件)」を既存出力の中で明示する契約の改善/Writer W-1 Promptの数字規則を「許可」から「必須最小集合の保持+それ以外は任意」へ/R1/R2への保持契約の明示/決定論的な保持検査(必須数値が最終本文に存在するか、表記揺れ・丸めを許容)をW-1直後またはR2後に置き、不在ならその段のみ再生成(retry上限・HR停止の既存枠に接続)。LLM追加呼出が本当に必要かを評価し、決定論検査で足りる部分は決定論で。
   - 「約4億年前から」のような推定条件・期間の扱い(§3注: 継続的同速度と誤解させない)を、数値保持と事実正確性の両立としてどう担保するか。
   - 量産単価への継続増分(円/記事セット、出典ある単価のみ)、生成時間への影響、開発費見積(Phase 1 月の記事 W-1以降のDEV再実行、Phase 2 過去記事2〜3本の W-1以降再実行。既存ledger/B3出力を再利用しResearch/Web検索は再実行しない)。Fableの本案件上限=200円(Phase 0=0円、Phase 1≤80円、Phase 2≤120円を目安。300円以下=自律枠)。
   - 評価基準(§5-1の6項目、§5-2の4指標)、合否の定義、撤退条件、Production不変の保証方法、Production採用時の必要作業・影響範囲(X専用か、Z/Yへ波及なしか)。
D. `OPUS_REVIEW_REQUEST_01.md`(条件A): 論点=(a)既存B3の役割を活かし重複システムを作っていないか、(b)「全部必須」になっていないか・過剰掲載リスク、(c)数値保持と事実正確性(推定条件・期間)の両立、(d)決定論検査+段限定再生成の設計妥当性とretry/HR既存枠との整合、(e)量産単価増分の妥当性、(f)過去Trial/不採用方式の再導入なし。テンプレ `docs/pm/templates/OPUS_INDEPENDENT_REVIEW_BLOCK.md` があれば従う。
E. SSOT: `OPEN_ITEMS.md` に新規OPEN登録(11-8分類必須、種別=Trial、Status=TRIAL_APPROVED_DESIGN_PENDING_OPUS_A、DEV専用・Production変更0)、OPEN-505行に本管理IDへの接続を追記、`docs/pm/USER_DECISION_REGISTER_01.md` #189を判断済み(2026-10-25、原文path、「Trial承認・全部必須方式禁止・Production採用は別判断・月の記事のProduction再実行は採用判断後」)に更新、`DECISION_LOG.md` に着手記録1件、`docs/pm/ACTIVE_TASK.md` 固定ヘッダに本管理IDの行を1行追加しFAMILY-X-MOON-SHRINKING行のStatusへ「→FX-CORE-NUMERIC-RETENTION-TRIAL-01で対応中」を追記。**並行agent(FX-PARAGRAPH-CHUNK-TTS-TRIAL-01)が同じSSOTを同時編集中。編集直前に再Readし、自行のみ最小Edit、衝突時は再Read→再Edit。**編集前にscratchpad(`C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\scratchpad\`)へバックアップ、編集後 `git diff --stat -- <file>` で異常な大量差分・空ファイル化がないことを確認。
F. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 498 --out docs/pm/delegation_log/2026-10-25_FX-CORE-NUMERIC-RETENTION-TRIAL-01_DELEGATION_01.md`。抽出結果の冒頭が本委任文(「管理ID: FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_01」)と一致するか確認し、不一致なら index 496〜501 を順に試す(`--index -1`は不可)。
G. Git: `git status` → 対象pathのみ `git add <path>`(禁止: `-A/-u/-f/-N`、amend、rebase、force push、stash、clean、reset --hard、checkout -f/`git checkout -- <file>`) → `git diff --cached --name-status` で意図外D/Aなし・secret grep 0件・Production file差分0 → `git commit --only -- <path…>` → `git push origin HEAD:main`。他agentの差分が同一SSOTに混在する場合はHEAD blob+自分の変更のみの一時index方式で自分の変更だけをcommit。ACTIVE_TASK/RESULT_PACKETはgitignore。er114_outputの分析結果はjson/mdの小さいものだけ追跡(wav/大容量は不追跡)。
H. 報告: `docs/pm/RESULT_PACKET_FXNR1.md`。内容=①段別脱落の実測表(run×段×中核数値)、②根本原因の要約(前回との差分)、③21節A/B/C分類、④推奨方式と代替案の比較(品質/過剰掲載リスク/量産単価増分/開発費)、⑤Phase 1/2の見積と計画、⑥OPUS_REVIEW_REQUEST_01.mdの所在、⑦変更ファイル・commit hash、⑧`check_delegation_prompt.py`結果、⑨費用(0円)・問題点。**Phase 0完了でSTOP。実装・有料Trialは開始しない。**

## 3. 禁止・注意
- Production code/Prompt/flag/閾値の変更、公開版・Production出力の変更(読み取りのみ)。
- LLM/Web検索/TTS等の有料呼出(Phase 0は完全無料)。
- 「【中核数値】全部必須」方式、重複する重要数値選定システム、不要数値の追加。
- 使用モデル(Phase 1以降の設計記載): Writer/R1/R2はProduction同一モデル(条件同一性)、評価用LLMを使うなら最新世代(gpt-6-luna等、名称と最新か否かを記載)。
- `.venv\Scripts\python.exe` を使用。自PID以外のprocess終了禁止。
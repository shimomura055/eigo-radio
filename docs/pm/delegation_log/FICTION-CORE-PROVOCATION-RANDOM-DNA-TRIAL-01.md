## 管理ID
`FICTION-CORE-PROVOCATION-RANDOM-DNA-TRIAL-01`(初回委任)。並行タスクなし。一時ファイル標準`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`。`ACTIVE_TASK*`/`RESULT_PACKET*`/`.env`はaddしない。履歴操作禁止。trailer必須。`git add -A`/`stash`禁止。

## 性質/到達上限/禁止
- Trial。到達上限`VALIDATED`。Production Prompt変更/CURRENT_SPEC正式仕様化/Future→Fiction名称のProduction変更/Audio・TTS/Key Phrase/Comment/Standard・Advanced両レベル展開/追加テーマTrial/Random軸の自動最適化/失敗時の軸追加/追加Trial、すべて禁止。SSOT無変更。既存Future Production/Trial scriptは変更せずimportのみ。
- LLM call: 5 Run × (Core Provocation 1 call + Story 1 call)=10 call(+空出力・schema失敗時の同一条件再試行各1回)。`gpt-5.6-luna`、Core Provocation effort medium、Story effort high。`response.model`実値記録。費用上限¥30。Web Search禁止。
- STOP条件(ユーザー指定): 結果を見て新しい乱数軸・Plotルール・Writer制約を思いついても追加実装・追加Trialしない。一度5本を出してSTOP。

## 固定ブロック
E-1/D-1/G-1/F-1(前回同一)。T-0: 本委任文を`docs/pm/delegation_log/FICTION-CORE-PROVOCATION-RANDOM-DNA-TRIAL-01.md`へ保存し`check_delegation_prompt.py`実行、結果をRESULT_PACKETへ1行(FAILでも継続)。

## ユーザー指示要点(全文は末尾【ユーザー指示全文】をdelegation_logへ)
旧Futureの良点(先にCore Provocationを作る/分かりやすく先が気になるStory)を残し、Future限定を外してFictionへ拡張。Story DNA(5軸: A関係性/B感情トーン/C中心ドラマ/D舞台/E世界設定)から各Storyで2〜3軸だけをコード側乱数で選び、各1要素をランダム選択、残りはWriter自由。乱数seed・選択軸・選択値を記録し再現可能に。Story DNAは発想をずらす刺激でありPlotを縛る契約ではない。固定Plot構造を指定しない。4つの共通原則(次にどうなる？と思える/含意より出来事として理解できる/登場人物・時間軸・場所を増やしすぎない/まず話そのものが分かる)。Theme: memory で5本。Run1〜4=通常Random DNA。Run5=E軸を必ず使用しFuture系3値(少し先の未来/大きく変わった未来/現実にはない技術・制度がある世界)からランダム、他1〜2軸は通常ランダム(Future互換性確認用Coverage Run)。フロー: Theme→Random Story DNA→Core Provocation候補1〜3→最も面白い1つを選択→Story生成。Core Provocationは設定だけでなく先を知りたくなる中心アイデア、1〜2文、why_interestingを短く記録。Story本文は旧Future Trial-08程度の簡潔さ、Standard相当の分かりやすい英語、目安280〜420語(hard gateにしない)。

## 事前指定Read一覧
- 旧Future系の特定: `Grep pattern="Core Provocation|core_provocation|imagined-future|about the future" -i glob="*.py,*.md" -l`→旧Future Trial(Trial-08相当)のscript・Prompt・REPORTを特定。該当scriptのGrep `PROVOCATION|WRITER|developer|def call_|effort|json_schema`→Core Provocation Prompt・Story Writer Promptの逐語と呼び出し方法(流用元)。Memory記事(旧Future)の出力ファイルをGlob `**/*memory*`で特定(比較用、読み取りのみ、パスとsha256を記録)。
- `er005_output/cost_baseline_01/pricing_snapshot.json`: luna単価。

## 実装(`er018_fiction_core_provocation_random_dna_trial_01.py`)
1. **Story DNA定義**(逐語):
   A 関係性: 家族/友人/恋人/同僚/見知らぬ人/自分自身
   B 感情トーン: 温かい/不穏/切ない/ブラックユーモア/爽快/奇妙
   C 中心となるドラマ: 選択/秘密/誤解/逆転/喪失/発見/禁止/交換
   D 舞台: 家/学校/職場/店/病院/旅先/公共空間/特殊な場所
   E 世界設定/現実との距離: 現代の日常/少し先の未来/大きく変わった未来/現実にはない技術・制度がある世界/超自然・幻想的な世界/現実とほぼ同じだが、1つだけルールが違う世界
   英語併記(Promptには日本語+英語の両方を渡す。訳は意味を変えない)。
2. **乱数**(`random.Random(seed)`、seedは`--seed-base`(既定20260925)+run番号): 軸数k∈{2,3}を等確率→軸をk個非復元抽出→各軸1値。Run5はE軸を固定で含め、Eの値はFuture系3値から抽出、他は1〜2軸を残り4軸から。`dna_log.json`にrun/seed/axes/values/選ばれなかった軸を記録。
3. **Core Provocation Prompt**: 旧FutureのCore Provocation Promptを逐語ベースに、Future限定語句("about the future"/"imagined-future story"等)を「テーマから、現実・未来・非現実・仮想設定を問わず、最も面白いStory Premise/Core Provocationを考える」に置換(差分を`prompt_diff_provocation.md`に逐語)。追加(逐語):
   ```
   [Story DNA — a creative nudge, not a contract]
   Use the following elements as a nudge to move your thinking away from your default story. You may interpret them freely. Do not force them; if an element does not fit naturally, let it stay in the background.
   {dna_lines}
   Everything not listed here is yours to decide.
   ```
   共通原則(逐語): `A good premise here makes the listener want to know what happens next. Prefer concrete events over abstract or literary implication. Keep to a small cast, one time frame, and few places. Meaning may come at the end, but the story itself must be clear first.` 出力schema: `{"candidates":[{"core_provocation":str,"why_interesting":str}] (1〜3件), "chosen_index":int, "reason_for_choice":str}`(選択もこのcallで行わせる)。
4. **Story Prompt**: 旧FutureのStory Writer Promptを逐語ベースに、Future限定語句のみ同様に置換(差分記録)。入力=chosen core_provocation+同じStory DNA nudge+共通原則。長さ指示は旧Prompt踏襲(280〜420語目安、hard gateにしない)。英語レベルは旧Trial-08と同じ(Standard相当)。固定Plot構造を指示しない(旧Promptにテンプレート構造の指示があれば、それは残す/外すの判断が必要になるため**残したまま**REPORTに明記)。
5. 出力: `runs/run{1..5}/{dna.json, provocation.json, story.md, api_meta.json}`、`stories_all.md`(5本連結、run番号・DNA・Core Provocation付き)、`blind.md`(5本をランダム記号でDNA・Provocation非表示、`blind_key.json`)、`cost.json`。
6. 機械参考指標: 各Storyの語数/文数/固有名詞数/登場人物数(大文字名の異なり数)/時制の分布(参考)/5本間のペアTF-IDFコサイン類似度(標準ライブラリで簡易実装、収束の参考)/旧Future Memory記事との類似度(参考)。
7. Sonnet仮評価(参考、最終はFable/ユーザー): 各RunでどのDNAがどう効いたか(1〜2行)、5本の違いの超サマリ、同じテイストへ収束した箇所、Future Coverage Run(Run5)が分かりやすいStoryとして成立しているか、4原則充足、STRONG PASS/PASS/FAILの仮判定。
8. REPORT `FICTION-CORE-PROVOCATION-RANDOM-DNA-TRIAL-01_REPORT.md`: §1 条件・Prompt全文(両段)・旧Futureからの差分/§2 Story DNA定義と乱数方式/§3〜§7 Run1〜5(seed/選ばれたDNA/Core Provocation候補と選択/Story全文/どのDNAがどう効いたか)/§8 機械参考指標(類似度表)/§9 5本の違いの超サマリ・収束箇所/§10 Future Coverage Run評価/§11 改善案(提案のみ、実装しない)/§12 cost・model実値/§13 Fable参考評価`[Fable記入]`/§14 分類`[Fable記入]`/§15 USER_DECISION_REQUIRED`[Fable記入]`/§16 Production変更なしの確認。

## 実行コマンド全文
```
cd C:\Users\tensh\eigo-radio
.venv\Scripts\python.exe er018_fiction_core_provocation_random_dna_trial_01.py --out-dir er018_output\fiction_core_provocation_random_dna_trial_01 --step dna --seed-base 20260925
.venv\Scripts\python.exe er018_fiction_core_provocation_random_dna_trial_01.py --out-dir er018_output\fiction_core_provocation_random_dna_trial_01 --step generate --budget-jpy 30
.venv\Scripts\python.exe er018_fiction_core_provocation_random_dna_trial_01.py --out-dir er018_output\fiction_core_provocation_random_dna_trial_01 --step analyze
.venv\Scripts\python.exe er018_fiction_core_provocation_random_dna_trial_01.py --out-dir er018_output\fiction_core_provocation_random_dna_trial_01 --step assemble
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\FICTION-CORE-PROVOCATION-RANDOM-DNA-TRIAL-01.md --json-out docs\pm\delegation_log\FICTION-CORE-PROVOCATION-RANDOM-DNA-TRIAL-01.md_check.json
git status --short
```

## SSOT追記文
なし。

## Git
明示add: `er018_fiction_core_provocation_random_dna_trial_01.py`、`er018_output/fiction_core_provocation_random_dna_trial_01/`配下、`FICTION-CORE-PROVOCATION-RANDOM-DNA-TRIAL-01_REPORT.md`、`docs/pm/delegation_log/FICTION-CORE-PROVOCATION-RANDOM-DNA-TRIAL-01.md`、同`_check.json`。
メッセージ: `FICTION-CORE-PROVOCATION-RANDOM-DNA-TRIAL-01: Future限定を外したCore Provocation→Story生成に、コード側乱数のStory DNA(5軸から2〜3軸)を加えてTheme memoryで5本生成(Run5はFuture Coverage)、ブラインド資料・類似度指標を作成(Luna、Production変更なし)`
trailer: `Management-ID: FICTION-CORE-PROVOCATION-RANDOM-DNA-TRIAL-01`

## 報告(RESULT_PACKET)
0. T-0 1. 流用元(旧Future script/Prompt/Memory記事のパス)とFuture限定語句の置換差分 2. 5 Runのseed/軸/値 3. 各RunのCore Provocation(選択)と語数 4. 10 callの`response.model`実値・cost合計・再試行有無 5. 類似度表(5本間+旧Memory) 6. Sonnet仮評価(超サマリ・収束箇所・Run5・仮判定) 7. `blind.md`/`blind_key.json`のパス 8. STOP該当有無 9. `git status --short`・commit SHA・push 10. 一覧外Read理由、改善案(提案のみ)。

---
【ユーザー指示全文】(delegation_logへ保存)
FICTION-CORE-PROVOCATION-RANDOM-DNA-TRIAL-01。目的: 旧Futureの良かった点である「先にCore Provocationを作る」「分かりやすく、先が気になるStoryにする」という基本設計を残しつつ、Future限定を外してFictionカテゴリーへ拡張する。同時に、LLM任せだと毎回似たテイストになる問題に対し、軽いランダム要素を入れることでStoryの多様性が出るか確認する。今回はTrialのみ。Production変更はしない。基本思想: Core Provocation生成時に、従来の about the future / imagined-future story というFuture限定を外し、テーマから、現実・未来・非現実・仮想設定を問わず、最も面白いStory Premise/Core Provocationを考える方式を試す。ただし、文学作品的な抽象性を狙わない。全Story共通の定性的原則: 1.読者が「次にどうなる？」と思えること 2.抽象的・文学的な含意より、出来事として理解できること 3.登場人物・時間軸・場所を増やしすぎないこと 4.最後に意味を考えさせてもよいが、まず話そのものが分かること。固定のPlot構造は指定しないこと。「問題発生→葛藤→選択→解決」等の固定テンプレートを新設しない。Story DNA(ランダム因子、5軸): A関係性(家族/友人/恋人/同僚/見知らぬ人/自分自身) B感情トーン(温かい/不穏/切ない/ブラックユーモア/爽快/奇妙) C中心となるドラマ(選択/秘密/誤解/逆転/喪失/発見/禁止/交換) D舞台(家/学校/職場/店/病院/旅先/公共空間/特殊な場所) E世界設定/現実との距離(現代の日常/少し先の未来/大きく変わった未来/現実にはない技術・制度がある世界/超自然・幻想的な世界/現実とほぼ同じだが、1つだけルールが違う世界)。Randomization方法: 各Storyについて5軸すべてを使わない/2〜3軸だけ選ぶ/選ばれた軸から各1要素をランダム選択/残りの要素はWriterに自由に決めさせる。乱数はLLMに任せず可能ならコード側で選択し、random seed/選択された軸/選択値を記録して再現可能に。Story DNAは発想をずらす刺激であり、Plotを縛る契約ではない。Trial方法: テーマは同じものを使い乱数による差だけを見る。Theme: memory で5本(旧FutureのMemory記事と比較しやすい)。Run1〜4=通常のRandom DNA(2〜3軸をランダム選択)。Run5=FutureがFiction化によって消えていないことの確認用。世界設定/現実との距離軸だけは必ず使用し、その中からFuture系(少し先の未来/大きく変わった未来/現実にはない技術・制度がある世界)のいずれかをランダム選択。その他1〜2軸は通常通りランダム。Future互換性確認用のCoverage Runであり、Production仕様として毎回Futureを強制する意味ではない。生成フロー: Theme→Random Story DNA→Core Provocation候補1〜3→最もStoryとして面白い1つを選択→Story生成。Core Provocationは設定だけではなく先を知りたくなる中心アイデアがある/1〜2文程度/why_interestingも短く記録。Story本文は旧Future Trial-08程度の簡潔さを維持。内容比較が目的なのでStandard相当の分かりやすい英語でよい。目安280〜420語程度、hard gateにしない。評価観点: 最重要は5本が本当に違うStoryになったか。Core Provocationが実質的に異なる/Storyのテイストが異なる/同じPlot骨格の表面変更になっていない/Random DNAがStoryに自然に効いている/DNAを無理に消化した不自然さがない/4つの共通原則を満たす/Future Coverage Runも旧Future同様、分かりやすいStoryとして成立する。Trial目安: STRONG PASS=5本中4本以上が明確に別タイプのStory/PASS=3本以上/FAIL=違いが2本以下、またはStory DNAを入れても同じテイストに収束。単純な語彙差ではなく読者が別の作品だと感じるかで見る。最終判断はユーザー。対象外: Production Prompt変更/CURRENT_SPEC正式仕様化/Future→Fiction名称のProduction変更/Audio・TTS/Key Phrase/Comment/Standard・Advanced両レベル展開/追加テーマTrial/Random軸の自動最適化/失敗時の勝手な軸追加。Status: Trial実施承認済み。到達はVALIDATED/REJECTED/USER_DECISION_REQUIREDまで。結果が良くてもAPPROVED_FOR_PRODUCTIONへ自動昇格しない。報告形式: 各5本について random seed/選ばれたStory DNA/Core Provocation/Story全文/どのDNAがどう効いたか。最後に 5本の違いの超サマリ/STRONG PASS・PASS・FAIL候補/Future Coverage Runの評価/同じテイストへ収束した箇所/改善案があれば提案だけ/Trial最終Status/USER_DECISION_REQUIRED事項。STOP条件: 結果を見て新しい乱数軸・Plotルール・Writer制約を思いついても、追加実装・追加Trialはしない。一度5本を出してSTOPし、ユーザー判断を待つ。

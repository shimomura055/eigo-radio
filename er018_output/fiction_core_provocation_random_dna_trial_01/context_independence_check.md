# context_independence_check.md

管理ID: FICTION-RUN-CONTEXT-INDEPENDENCE-RECHECK-01
Phase 1(read-only事実確認のみ。再Trial・API呼び出し・改善なし、¥0）

対象: `FICTION-CORE-PROVOCATION-RANDOM-DNA-TRIAL-01`
(commit 6da2b439、`er018_fiction_core_provocation_random_dna_trial_01.py`、
出力 `er018_output/fiction_core_provocation_random_dna_trial_01/`)

## 1. 呼び出し構造(行引用)

`er018_fiction_core_provocation_random_dna_trial_01.py`:

- Core Provocation呼び出し(`generate_core_provocation`, L271-280):
  ```
  272: response = client.responses.create(
  273:     model=model,
  274:     reasoning={"effort": effort},
  275:     text={"format": {"type": "json_schema", **CORE_PROVOCATION_JSON_SCHEMA}},
  276:     input=[
  277:         {"role": "developer", "content": CORE_PROVOCATION_DEVELOPER_MESSAGE},
  278:         {"role": "user", "content": prompt},
  279:     ],
  280: )
  ```
  `previous_response_id`・`store`・`conversation`のいずれのパラメータも指定なし
  (grepでスクリプト全文・`er003_v1_en_direct_vfl_01_generate.py`双方を検索したが
  該当行なし)。`input`はdeveloperメッセージ(固定文)+ そのRunの`prompt`のみの
  2要素配列(=(a)毎回新規のresponses.create、(b)前callへの連結なし、(c)前Run出力を
  messages配列に積む処理もなし)。

- Story呼び出し(`generate_story`, L377-389)も同型:
  ```
  378: response = client.responses.create(
  379:     model=model,
  380:     reasoning={"effort": effort},
  381:     input=[
  382:         {"role": "developer", "content": WRITER_DEVELOPER_MESSAGE},
  383:         {"role": "user", "content": prompt},
  384:     ],
  385: )
  ```
  同様に`previous_response_id`等なし。

- `client = vfl01.get_client()`(L600)は`er003_v1_en_direct_vfl_01_generate.py`
  L65-67の`return OpenAI()`をそのまま返す、状態を持たないHTTPクライアント。
  5 Run分のループ(`step_generate`, L602-605)でこの同一`client`オブジェクトを
  使い回すが、これは単なるHTTPクライアントの再利用であり、会話状態
  (thread/conversation)は保持しない。

- 各`api_meta.json`(5 Run分すべて確認)には`model`/`response_id`/`effort`/
  `attempts`のみが記録され、`previous_response_id`等のフィールドは存在しない
  (run1: `resp_0b9bab88...`→`resp_0003ba6a...`、run2: `resp_0696ed51...`→
  `resp_068bdf77...`のように、Run・callごとに完全に独立した`response_id`)。

- `build_core_provocation_prompt(dna_entry)`(L263-268)・
  `build_story_prompt(core_provocation, dna_entry)`(L367-374)は、いずれも
  「そのRunの`dna_entry`」「そのRunで選ばれた`core_provocation`」のみを
  引数に取り、他Runの情報(履歴オブジェクト・グローバル変数)を一切参照しない。
  `process_one_run`(L526-587)のシグネチャも`(client, out_dir, run_number,
  dna_entry, log_path, budget_jpy)`のみで、前Run結果を受け取るパラメータは
  存在しない。

## 2. 各Runへ実際に渡したPromptの含有有無(5 Run全文読了)

`runs/run{1..5}/provocation_prompt.txt`・`story_prompt.txt`を全て読み、
以下を判定(該当なしは「なし」)。

- 前Run Story全文: なし(story_prompt.txtには`[Core Provocation]`=自Runの
  選定結果、`[Theme]`=固定"memory"、`[Story DNA]`=自RunのDNAのみ)。
- 前Run Core Provocation: なし。
- 前Run title: なし(タイトル自体、Writerプロンプトに「必要なら短く付けてよい」
  という指示のみで、前Runのtitleを渡す仕組みなし)。
- 前Run DNA: なし(DNAは`dna_log.json`にRunごと独立生成、各prompt.txtには
  自RunのDNA行のみ)。
- 前Run評価/blind評価: なし(評価(analyze/assemble)はgenerate完了後の別step
  であり、generate時点でそもそも存在しない)。
- 「theme memory」: **あり、ただし過去Runの記憶ではなく、`THEME_LABEL_EN =
  "memory"` / `THEME_LABEL_JA = "記憶"`という全Run共通の固定テーマ定数**
  (L100-101)。5 Run全ての`provocation_prompt.txt`に`[Theme]\nmemory (記憶)`
  として現れるが、これは「テーマが"memory"である」という所与の設定であり、
  「過去Runの内容を記憶している」機構ではない。委任文中の「theme memory」
  という表現は、コミットメッセージ`「Theme memoryで5本生成」`
  (`docs/pm/delegation_log/FICTION-CORE-PROVOCATION-RANDOM-DNA-TRIAL-01.md`
  L58)およびREPORT L307「本Trialのtheme memoryは題材の重複回避に効いていない」
  の用法と同じで、「テーマ『記憶』」の意であり、Run間文脈保持を指す語ではない
  ことをコード定義から確認した。
- 過去Runの仕掛け要約: なし(そのような要約を生成・保持するコードが存在しない)。
- 過去Runの人物名・小道具・時刻: なし(story_prompt.txtに具体名は一切出現せず、
  Characters節は「主人公のみ固有名可」という一般ルールのみ)。
- 「前と違うものを作れ」等の指示: なし(該当する文言は共通テンプレート
  `COMMON_PRINCIPLES`・`CORE_PROVOCATION_DEVELOPER_MESSAGE`・
  `WRITER_DEVELOPER_MESSAGE`のいずれにも存在しない)。
- その他前Run内容を知り得る情報: なし。

## 3. 候補生成(candidates 3件)の前Run依存性

`CORE_PROVOCATION_JSON_SCHEMA`(L222-260)のcandidates配列は
`core_provocation`/`why_interesting`のみのschemaで、前Runの選択結果を
参照する項目は定義されていない。プロンプト本文(`CORE_PROVOCATION_PROMPT_
TEMPLATE`, L206-220)にも前Run候補・前Run選定結果への言及はない。
実際の出力(run1〜run5の`provocation.json`)を確認しても、各Runの3候補は
そのRunのDNA(例: run2はC=秘密/D=学校のみ)から独立に発想されており、
候補生成が前Runの選択結果に依存している形跡はない。

## 4. Provocation→Story間の連結範囲

Run内のみ: `core_provocation = prov_result["selected"]["core_provocation"]`
(L552)を同Runの`build_story_prompt`(L559)へ渡すのみで、Run横断の変数受け渡し
は存在しない(`process_one_run`は1 Run分の処理が完結するローカル関数)。

## 5. Run2の未来設定自発選択について(E軸なし)

`runs/run2/provocation_prompt.txt`の全文(上記2.で確認)には、E軸(World/
距離)自体が含まれていない(Run2のDNAは`axes: ["C","D"]`、`dna_log.json`
L37-40)。共通原則(`COMMON_PRINCIPLES`)・Theme文言(`memory (記憶)`)にも
"future"/"technology"/"near future"等の語は含まれない
(`CORE_PROVOCATION_PROMPT_TEMPLATE`・`COMMON_PRINCIPLES`本文に該当語なし)。

Run2実際の出力(`runs/run2/provocation.json`)では、C=秘密/D=学校のみの
指定にもかかわらず、3候補すべてが記憶を保存・消去・売買する技術/制度
(digital lockers、記録の消失、記憶の消去サービス)を題材にしている。

事実として確認できるのはここまで(E軸なし・future語なしのprompt入力から、
モデルが自発的に技術的な記憶ギミックを選んだという入出力の対応関係)。
**なぜモデルがその方向へ寄ったかの因果自体は、本Phaseの読み取り可能な
artifactからは断定できず、以下は推測である**:
- 推測: テーマ「memory」という語自体が、LLMの学習データ上、SF的な
  「記憶の保存・消去・移植・記録」といった技術的ギミックと強く結び付いている
  可能性がある。
- 推測: `WRITER_DEVELOPER_MESSAGE`(L307-318、全Run共通)に「設定は現実的・
  近未来・遠未来・非現実のいずれでもよい」という一文があり、Story段階では
  未来設定が明示的に選択肢として提示されている。ただしこれはRun1〜5全てに
  同一文言で与えられる共通boilerplateであり、Run1由来の情報ではない
  (Run2固有の未来化を直接説明する根拠にはならない。「なぜ他Runでなく
  Run2/Run1/Run5が収束したか」はモデルの生成ばらつきであり、本Phaseの
  artifactからは特定不可)。

## 6. 表

| Run | 新規contextか | 前Run Story | Core Provocation | title | theme memory | 仕掛け要約 | 人物名/小道具/時刻 | 同一session context | その他 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | あり(独立call、previous_response_id等なし) | なし | なし(自Runのみ) | なし | あり(定数"memory"、過去Run記憶ではない、§2参照) | なし | なし | なし(client使い回しはHTTP層のみ、会話状態なし) | なし |
| 2 | あり | なし | なし | なし | あり(同上) | なし | なし | なし | なし |
| 3 | あり | なし | なし | なし | あり(同上) | なし | なし | なし | なし |
| 4 | あり | なし | なし | なし | あり(同上) | なし | なし | なし | なし |
| 5 | あり(Coverage Run、E軸強制はコード側dna選定ロジックのみ、他Run結果非依存) | なし | なし | なし | あり(同上) | なし | なし | なし | なし |

## 7. 判定

**A. 完全独立**。5 Run全てについて、スクリプトの呼び出し構造(§1)・実際に
渡されたPrompt全文(§2)・候補生成の独立性(§3)・Provocation→Story連結範囲
(§4)のいずれを見ても、前Run(Story全文・Core Provocation・title・仕掛け・
人物名/小道具/時刻・評価結果)がそのRunへ渡された痕跡はない。「theme
memory」はコード上の固定テーマ定数("memory")であり、Run間文脈保持機構
ではない。したがって、**Run間context汚染はRun1/2/5が未来系へ収束した原因
ではない**と結論する。

Run2の未来化については、事実として「E軸なし・future語を含まないprompt
入力→技術的記憶ギミックへの自発収束」という入出力対応のみ確認でき、
その背後の要因(テーマ語"memory"自体の連想強度、共通boilerplate中の
"future"選択肢提示、モデルの生成傾向)は上記§5のとおり推測であり、
本Phase(read-only事実確認)の範囲では断定しない。

## 根拠パス一覧
- `C:\Users\tensh\eigo-radio\er018_fiction_core_provocation_random_dna_trial_01.py`
- `C:\Users\tensh\eigo-radio\er003_v1_en_direct_vfl_01_generate.py`(L65-67 `get_client`)
- `C:\Users\tensh\eigo-radio\er018_output\fiction_core_provocation_random_dna_trial_01\dna_log.json`
- `C:\Users\tensh\eigo-radio\er018_output\fiction_core_provocation_random_dna_trial_01\runs\run{1..5}\provocation_prompt.txt`
- `C:\Users\tensh\eigo-radio\er018_output\fiction_core_provocation_random_dna_trial_01\runs\run{1..5}\story_prompt.txt`
- `C:\Users\tensh\eigo-radio\er018_output\fiction_core_provocation_random_dna_trial_01\runs\run{1..5}\provocation.json`
- `C:\Users\tensh\eigo-radio\er018_output\fiction_core_provocation_random_dna_trial_01\runs\run{1..5}\api_meta.json`
- `C:\Users\tensh\eigo-radio\FICTION-CORE-PROVOCATION-RANDOM-DNA-TRIAL-01_REPORT.md`(L277, L307)
- `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\FICTION-CORE-PROVOCATION-RANDOM-DNA-TRIAL-01.md`(L58)

本Phaseでは上記artifactの読み取りのみを行い、API呼び出し・再Trial・
コード変更・プロンプト改善は一切実施していない(費用¥0)。

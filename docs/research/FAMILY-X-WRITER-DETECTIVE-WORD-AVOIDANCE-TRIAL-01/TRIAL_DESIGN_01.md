# TRIAL_DESIGN_01: Writer「Detective」単語回避 Trial 事前登録設計

- 管理ID: FAMILY-X-WRITER-DETECTIVE-WORD-AVOIDANCE-TRIAL-01 委任_01(2026-10-21)。性質=Trial(新Prompt候補`TRIAL`、到達上限`VALIDATED`、Production採用はユーザー別途明示承認、正式Production Writerへの配線は対象外)。
- ユーザー原文: `docs/pm/delegation_log/2026-10-21_FAMILY-X-WRITER-DETECTIVE-WORD-AVOIDANCE-TRIAL-01_USER.md`(4258文字[本文のみ]、sha256 `d99e16e918b40cb4328172cafc8e550c02be2ba00dea8c5a82bb439cda924bd5`)。
- **事前登録**: 本書・`design_matrix_01.json`・`judge_prompts_01.json`・harness(`er086_writer_detective_avoidance_trial_01_*.py`)は有料生成の前にcommitする。実走結果を見て指標・閾値・Prompt文を変更しない。
- 目的(ユーザー§9): 「Detectiveという単語を使わずに、これまでのニュース記事の面白さを維持したい」。探偵的構成の禁止は目的ではない。禁止語リストは新設しない(類似語は観測として件数・文脈を記録するのみ)。

## §1 Baseline計測(JPY0、事前に実施済みの観測)
`er019_output/middle_east_yemen_saudi/run_mey_02`の読取のみ(変更なし)。

| 成果物 | `探偵`(JA) | `detective` | 備考 |
|---|---|---|---|
| ja_writer/original.md(R0) | 0 | – | |
| ja_writer/revision1.md(R1=Entertainment Revision出力、後処理後) | 0 | – | factlock/r1.raw.md も0 |
| ja_writer/revision2.md(R2最終) | 2(L3「ニュース探偵の出番だ」、L15「ここで探偵、名札を拡大する」) | – | 他に「推理」1(L19「証拠を飛び越えた推理」) |
| b1b/article.md(Advanced本文) | – | 2(L3「the news detective's turn」、L15) | |
| a2/article.md(Standard本文) | – | 2(同) | |

結論(観測): Baselineの探偵比喩は**R2で初めて導入**された(R0・R1には0件)。R2は`USER_TMPL`(「事実は変えずにエンターテイメント性をもっと上げた記事にReviseください」)による改稿であり、ユーザー§4-4「各工程で追加指示が有効に作用しているか」の対照として、各Patternの`R0/R1/R2/Advanced/Standard`別に件数を記録する。Advanced英訳・Standardは忠実英訳/平易化のため、JAに`探偵`があれば`detective`が引き継がれる。support/KPテキスト(`a2_support_texts.json`等)は今回Writer範囲外・再生成しない(対象外と報告)。

## §2 注入点(Production関数・Prompt組立箇所)
Production経路(`er019_family_x_entertainment_production_runner_01.py` main):
- JA Writer: `run_ja_writer`(runner:263)→`er053_family_x_factlock_ja_writer_01.run_w1_writer`(L318)。R0=`build_r0_prompt`(L262、`call_luna_r0` gpt-6-luna effort high)、R1/R2=`astra_stage`内で`USER_TMPL.format(body=…)`(L63)を`call_astra`(gpt-6.1-sol effort high)へ。
- Advanced: `efam.run_writer_stage(only="advanced")`(er012:529→_run_writer_stage_once:370)→`adv_gen.generate_family_x_faithful_translation`(prompt=`build_family_x_faithful_translation_prompt`)+`generate_family_x_in_one_line`(`build_family_x_in_one_line_prompt`)。
- Standard: `efam.run_writer_stage(only="standard")`→`std_gen.generate_family_x_standard_a2_no_heading`(prompt=`build_family_x_no_heading_prompt`)。

追加指示は`design_matrix_01.json::injected_stages`の位置へ、A/B/Cとも同一の注入点・同一位置で挿入する(R0・R1・R2・Advanced英訳・Advanced In One Line・Standard)。**注入は`er086_..._lib.py::injected()`のprocess内monkeypatch**で行い、`finally`で必ず復元する。Production fileは変更しない(`git status --porcelain`で空、sha256を実行前後で記録)。全工程の実Promptを`prompt_dump/<pattern>_<stage>.txt`に保存する(有効化の証拠。testで「追加以外の差分0」を確認)。

### Production runnerを起動しない理由(設計書に記す切替)
`--stage writer/advanced/standard`はRisk Flagger(RF)を実行し、`review_queue/post_en/`(repo共有)へ書込む。Trial成果物をProductionのReview Queueに混入させないため、runnerは起動せず、同runnerが呼ぶ**同一のProduction関数**(`w1.run_w1_writer`→`efam.run_writer_stage(advanced)`→`efam.run_writer_stage(standard)`)をTrial script(`er086_..._run.py`)から直接呼ぶ。モデル・Prompt・retry設定は同一(追加指示のみ差)。RFは本文を変更しない検査系であり、本Trialの評価(事実検査)は別途行う。入力(`research_ledger/`・`storyline_b3/`)はrun_mey_02からコピーしsha一致を`input_copy_evidence.json`に記録する(契約検証`validate_annotated_b3`は通常どおり実行される)。

## §3 実行
```
$env:TTS_EXECUTION_MODE="STANDARD"; $env:PYTHONIOENCODING="utf-8"
.venv\Scripts\python.exe er086_writer_detective_avoidance_trial_01_run.py --pattern <A|B|C> --source-run er019_output/middle_east_yemen_saudi/run_mey_02 --out-dir er086_output/writer_detective_avoidance_trial_01/<A|B|C> --budget-jpy 40
.venv\Scripts\python.exe er086_writer_detective_avoidance_trial_01_eval.py --root er086_output/writer_detective_avoidance_trial_01 --baseline er019_output/middle_east_yemen_saudi/run_mey_02 --out docs/research/FAMILY-X-WRITER-DETECTIVE-WORD-AVOIDANCE-TRIAL-01/COMPARISON_RESULT_01.md
```
3 Patternは入力/出力dirが独立のため3 processを並列起動する(同一Production moduleをimportするがmonkeypatchはprocess内のみ)。TTS/Assembly/Research/B3/web_searchは呼ばない。再実行は別out-dir(既存out-dir上書き拒否)。

## §4 評価(事前固定)
1. **Detective排除(決定論Grep)**: 対象=本文(R2最終JA・Advanced・Standard。Advanced/Standardは`## In one line`を含む完成記事全体)。`detective`(大小文字不問substring)件数=0が条件。`detectives`等の派生は別集計。JAは`探偵`。工程別(R0/R1/R2/Adv/Std)。support/KP/Preview/Commentは再生成しないため対象外。
2. **Entertainment(LLM判定、`judge_prompts_01.json`全文)**: `gpt-6-luna`、Baseline/A/B/Cを**ラベル伏せ(X1〜X4)・ランダム順**で提示、5観点(hook/flow/surprise_structure/readability_pull/no_unnatural_staging)1〜5点+根拠引用、**2回実行**(順序を変える)で安定性を見る。AdvancedとStandardを別々に判定。平均=5観点×2回の平均。temperatureはreasoningモデルで固定/非対応のため指定しない。
3. **事実・ニュース品質**: (a)LLM事実検査(`judge_prompts_01.json::fact_*`、Ledger全文vs記事Advanced)、(b)決定論: 記事内の固有名詞(大文字語)・数字をLedger+selected_briefと突合し未出現語を列挙、(c)Houthi記述の有無と帰属(連合軍報道官の発表)のGrep、(d)Sonnetによる全文通読(Ledger外事実・原因動機の創作・時系列/因果/人物関係)。判定は表で記録。
4. **類似語観測**: `investigat*|clue|mystery|case file|sleuth|whodunit|culprit|suspect|inspector|magnifying glass`(英)、`捜査|推理|謎解き|手がかり|名探偵|虫眼鏡|真犯人|犯人|事件簿|調査`(JA)の件数と文脈を記録するのみ(禁止リスト化しない、判定に使わない)。
5. **QCD**: Pattern別LLM呼出回数(raw_usage_log行数)・モデル・実費(raw_usage_log×pricing_snapshot、`er053_cost_aggregate_01`)・所要時間・retry有無(writer_run_summary/runtime_evidence)・Production適用時の量産単価影響(追加API呼出0=Promptの文字数増のみ)。

## §5 機械判定規則(事前固定)
候補 = 本文`detective` 0件 かつ 事実で新たな重大誤り0(LLM事実検査の`new_major_error_count`=0 かつ Sonnet通読で重大誤りなし) かつ Entertainment平均がBaseline−0.5点以内(Advanced基準、Standardも併記)。複数候補があれば追加指示が短い(A<B<C)ものを同等なら優先。いずれも満たさなければ`REJECTED_CANDIDATE_MACHINE`。最終ラベル(VALIDATED/REJECTED/USER_DECISION_REQUIRED)はFable。

## §6 再現確認
1セットで候補が1つに定まる/全滅なら追加生成しない。候補が複数でEntertainment差が0.3点未満など不明瞭な場合のみ、候補Patternに限り各1回再生成(Guardrail内、理由を記録)。Prompt候補D/E等は増やさない。

## §7 費用・Guardrail
見積約JPY50(Writer R0〜R2約12.7+Advanced英訳/IOL約0.4+Standard約0.3=約13.4/Pattern×3=約40、LLM判定約3。RFを実行しないため委任見積約47より低い見込み)。Guardrail上限JPY100(超過見込みでSTOP)。個別`--budget-jpy 40`/Pattern。日次: 2026-10-21 既使用JPY0(`daily_dev_cost_01.py --date 2026-10-21`)。

## §8 評価用モデル(PM_GOVERNANCE 25節)
生成=Productionと同一条件(変更不可)。評価LLM=`gpt-6-luna`(最新世代[gpt-6系]の推奨系、Productionと同世代。上位`gpt-6.1-sol`を使わない理由=判定の一貫性と費用最小化、生成側R1/R2のgpt-6.1-solと独立した系統で自己評価バイアスを避けるため)。

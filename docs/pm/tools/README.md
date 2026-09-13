# docs/pm/tools/README.md

Fableサンドイッチ運用(PM層)で使う read-only/記録用ツール群。いずれも
Productionコード(er0*)・API支出には無関係(¥0、外部API呼び出しなし)。

## measure_delegation_task.py

委任taskの効率指標(tool_uses/cumulative_usage/final_context_size/
tool_result_total_chars/same_file_reread_rate/full_read_rate_by_chars等)
を計測してJSON出力する。

```
python docs/pm/tools/measure_delegation_task.py --task-id <taskId> [--pretty]
```

## collect_subagent_transcripts.py

subagentのtranscript(`tasks/*.output`が0バイトの場合は`subagents/
agent-<taskId>.jsonl`)を`docs/pm/transcripts/`へ退避する
(`docs/pm/PM_GOVERNANCE.md` 11節F-1恒久手順)。既定はdry-run。

```
python docs/pm/tools/collect_subagent_transcripts.py --help
python docs/pm/tools/collect_subagent_transcripts.py --apply [--only-task-ids <id1,id2>] [--max-total-mb <N>]
```

## check_delegation_prompt.py(2026-09-13新設、D-2委任文標準の検証器)

Fableが作成した委任文が`docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.md`
の必須構成を満たしているかを機械的に検証する(管理ID: `PM-TOKEN-
EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`
/`PM-CLOSEOUT-CONSOLIDATION-117`)。

検証項目:
1. 必須セクション見出し(管理ID/性質/事前指定Read/事前指定Grep/
   実行コマンド全文/SSOT/Git/報告)の有無
2. 固定ブロックラベル(E-1/D-1/G-1/F-1)の有無(T-1は任意)
3. プレースホルダ語(同上/前回と同じ/前回同様/`<引数>`/TBD)の混入
   (Read一覧/Grep一覧/実行コマンド全文/SSOT追記文/Git/報告の各セクション
   本文のみを対象とし、設計説明文中の禁止語の引用例は誤検知しない)
4. 「実行コマンド全文」セクション内の各コマンド行に`--`長形式引数または
   絶対パスが含まれるか(単純な`python <script>.py`のみの完結コマンドは
   引数を要さない完全な呼び出しとして除外)

終了コードは常に0(ブロッキングではなく記録用)。

```
python docs/pm/tools/check_delegation_prompt.py --help
python docs/pm/tools/check_delegation_prompt.py --file <委任文.md> --json-out <出力.json> [--pretty]
python docs/pm/tools/check_delegation_prompt.py --stdin
```

Unit testは`check_delegation_prompt_test_01.py`(合格例=実委任文の保存
[`docs/pm/delegation_log/`]、不合格例=Grep一覧欠落/プレースホルダ混入)。

```
python docs/pm/tools/check_delegation_prompt_test_01.py -v
```

(`run_project_regression.py`のデフォルト探索パターン`er0*_test_*.py`は
root直下のみを対象とするため、本ディレクトリのtestは`--pattern
"**/check_delegation*"`指定でも探索リストには表示されるが、
`unittest.TestLoader.discover`側がroot起点の再帰探索で0件収集となる
既知の制約がある[`__init__.py`非配置のnamespaceディレクトリ再帰の挙動]。
本ディレクトリのtestは直接`python docs/pm/tools/
check_delegation_prompt_test_01.py -v`、または`python -m unittest
docs.pm.tools.check_delegation_prompt_test_01 -v`(パッケージ実行形式)
で実行するのが確実な手段。)

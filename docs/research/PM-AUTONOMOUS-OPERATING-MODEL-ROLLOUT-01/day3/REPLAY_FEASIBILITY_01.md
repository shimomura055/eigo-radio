# REPLAY_FEASIBILITY_01: 盲検リプレイ自律起動の実動作確認(委任_I、2026-10-15)

判定: **`REPLAY_FEASIBILITY_CONFIRMED`(条件付き、下記リスク参照)**。被験本番セッションは未起動。パッケージ(`C:\Users\tensh\eigo-radio-replay\` の defect_case/negative_control/synthetic/rubric/_scorer_only/runbook)は無変更。採点基準・期待値は本書に転記していない。
実測は全て `C:\Users\tensh\eigo-radio-replay\_feasibility\` (probe_01/probe_02、`.git`なし・`.env`なし。出力json/jsonlは同dir、Repoへ未add)。`claude --version`=2.1.300。被験の既定モデルは **claude-fable-5-1**(最新世代最上位、25節適合)。

## 1. 結果表(7項目)
| # | 項目 | 判定 | 観測値 |
|---|---|---|---|
| 1 | 起動可否 | ○ | `claude -p "Reply with exactly: PROBE_OK" --max-budget-usd 0.25`: rc=1、`terminal_reason=budget_exhausted`、`subtype=error_max_budget_usd`、`total_cost_usd=0.2576`、`num_turns=1`、`modelUsage`=claude-fable-5-1のみ、session_id=1b362c0e-…。**起動・課金・モデル特定は成功したが、1回目のturn自体が0.25を超え応答本文が返らなかった**(予算の下限は実質0.30以上が必要)。以降の`--agent`起動は全てrc=0で応答取得。安全確認: probe dirは祖先に`.git`/`.env`なし、`git rev-parse`=`fatal: not a git repository`、APIキー環境変数は空(`env.sh`で空化)。パッケージ側も`RUN_SESSION.ps1 -Case defect -CheckOnly`=OK |
| 2a | モデル・ルーティング | ○ | `--agent sandwich-pm`(probe_01に`defect_case/.claude`のみcopy): 応答`AGENT_PROBE_OK`、自己申告「Fable 5.1 (claude-fable-5-1)」、`modelUsage`=claude-fable-5-1、$0.352、rc=0 |
| 2b | 委任機能(Agent) | ○ | stream-json: initのtools=`Task,Read,Grep,Glob`(Agent=Taskとして露出)、Fableが`Agent(subagent_type=sonnet-worker)`を呼出、子の`message.model`=**claude-sonnet-5-5**、子が`SubagentHandback`で`SUB_OK`返却、Fableが中継。`modelUsage`: fable $0.1848+sonnet $0.0357=$0.2205、`subagent_stats.by_type={sonnet-worker:1}`。**対話の自律化代替は不要**(`-p`で成立) |
| 2c | 委任先のBash | 条件付き | `-p --allowedTools Read Grep Glob Agent`(=RUN_SESSION `-Print`と同じ)でもsonnet-workerのBashは**読取専用の単純コマンドは自動許可**(`git rev-parse`が実行されrc=128)。`;`等の複合コマンドは「requires approval」で拒否。python/powershell/cmd経由は`-p`では承認者不在のため拒否(下記4)。**検証委任でテスト実行・ファイル書込が必要な課題では不足の可能性**(未検証: sonnet-workerのEdit/Write) |
| 3 | 課金経路 | ○(subscription) | `~/.claude/.credentials.json`に`claudeAiOauth`のみ(subscriptionType=**max**、rateLimitTier=`default_claude_max_20x`)、`claude auth status`: `authMethod=claude.ai`、`apiProvider=firstParty`。`ANTHROPIC_API_KEY`等はprobeで空。`modelUsage.costBasis="list"`(定価換算の概算表示で従量請求ではない)。→ **API従量ではないためSTOP条件(従量かつ>USD1)は非該当**。制約はMax枠のレート制限 |
| 4 | 権限・隔離 | ○ | `subject_settings.json`の`//c/...`記法は**そのまま有効**(v2不要)。観測: A)Repo本体`CLAUDE.md`のRead→`File is in a directory that is denied by your permission settings.` / B)作業dir内`CLAUDE.md`のRead→成功 / F)`rubric\`のRead→同deny / Bash経由`head`/`cat`/`wc`/`ls`/`find`でRepo本体・`rubric`・`runbook`・`_scorer_only`→`Permission to use Bash with command … has been denied.`(denyのRead規則がBashのファイルコマンドにも波及) / `python -c`・`powershell Get-Content`・`cmd type`でRepo本体→`-p`では承認者不在で拒否(auto-mode classifier / "requires approval") / 相対パス`../../rubric/…`も拒否 / `git rev-parse`=exit128「not a git repository」 / `ANTHROPIC_API_KEY`・`OPENAI_API_KEY`=空。haiku(--model haiku)で実施(権限判定はモデル非依存) |
| 5 | 独立性・漏洩 | ○ | transcript所在: `C:\Users\tensh\.claude\projects\<cwdを-区切りにした名>\<session_id>.jsonl`、subagent分は`<session_id>\subagents\agent-*.jsonl`+`.meta.json`(実在確認。例: `C--Users-tensh-eigo-radio-replay--feasibility-probe-01\2c8dd877-…\subagents\`)。被験側は`.claude/projects/**`もdeny済み→被験者はtranscript/採点基準に触れられない。採点者は**`--settings subject_settings.json`を付けない別プロセス**(opus-consultant)で起動し、transcriptと`rubric\`を読む(※採点者の実起動は本委任では未実施=未確認) |
| 6 | ログ分離・並列 | ○ | probe_01とprobe_02を同時起動(haiku、各0.1): session_id=de118a21-…/3a890d1b-…、cwdが各probe dir、transcriptは別project dirに別ファイル、各$0.0037、rc=0/0 |
| 7 | 規則読込 | ○ | probe_01(`CLAUDE.md`copy)の`--agent sandwich-pm`が「# Claude Codeへの指示」配下の最初の見出しとして「共通Charter(全Agent共通・常駐、2026-10-15ユーザー承認U1)」を返答(CLAUDE.mdが文脈に常駐)。委任2でFableが★★★★報告マーカーを自発使用(CLAUDE.md規則の反映)。**注記: 委任_Hが11-4改定中のため、改定後規則の読込確認は本番起動時に再実施** |

## 2. 費用(実測)
子セッション合計 **約USD 1.12(約JPY168@150)**。内訳: probe 0.2576 / agent 0.3518 / 委任(Fable+Sonnet) 0.2205 / deny haiku 0.0070 / bypass haiku 0.0046 / 並列haiku 0.0037x2 / 委任2(Fable+Sonnet) 0.2705。Guardrail USD1.0を約0.12超過。理由: 項目2b/2cの検証にFable実走が必要でFableの1ターン(コンテキスト約29Ktokens)が約$0.1〜0.25、scope内・原因把握済み・retryなし・残作業なし・追加費用小、実課金は発生しない(subscription)。暴走疑いなし、STOP非該当。

### 本番17セッションの費用見込み(概算。根拠付き)
- 実測: Fable1ターン(system+CLAUDE.md+agent定義で約29K tokens、cache read/create込み)=$0.22〜0.35、Sonnet委任1回=$0.04〜0.05。ターンが増え読取(SSOT Grep・ファイルRead)でcontextが膨らむと1ターン$0.2〜0.4。
- 仮定: 欠陥ケース/陰性対照=ACTIVE_TASK読取+Grep数回+Sonnet検証委任1回で約10〜14ターン→ **USD 2〜5(中央3)**。合成シナリオ=読取少なめ4〜6ターン→ **USD 0.7〜1.5(中央1.0)**。
- 合計(被験): 3x3 + 14x1.0 = **約USD 23(範囲 USD 14〜36 = JPY 2,100〜5,400、中央 約JPY 3,500)**。採点Opus(17セッション分、transcript読取)は別途 USD 0.5〜1.5/件で **約USD 9〜25**を上乗せ見込み。
- いずれも**定価換算の概算値で、Max subscriptionでは従量請求なし**(JPYの追加課金は発生しない)。ただし9-10のClaude Code利用軸・Max枠のレート制限(特にFable)を消費する。短時間に17本を詰めると枠逼迫のリスク→並列度は2〜3に抑える。
- `--max-budget-usd`: helpは「Maximum dollar amount to spend on API calls (only works with --print)」。実測では**ターン完了後に判定**(0.25設定で0.2576を使い切ってから`error_max_budget_usd`で終了、結果本文なし)。ゆえに上限はターン粒度の事後停止で、**1ターンの最大額以上**(Fableなら最低0.5、本番は2.0〜5.0推奨)に設定する。

## 3. 未解決リスク
1. **`-p`ではsonnet-workerのEdit/Write・複合Bashが承認されない可能性**(2c)。検証が読取専用のGrep/Read/`git`系で足りるケースは可。欠陥ケースの原作業がテスト実行を要する場合は`--allowedTools`へ限定的な許可(例`Bash(python -m pytest:*)`)を追加する案(要事前小規模確認。未検証)。対話自律化は`-p`が成立したため試していない。
2. 採点者(opus-consultant、claude-opus-5-5)の実起動は未確認(モデル名は`.claude/agents/opus-consultant.md`宣言のみ)。本番前に1回の小規模確認を推奨。
3. `python`/`powershell`経由の迂回は`-p`では承認者不在のため拒否されたが、**対話起動では利用者の承認操作次第**。自律起動は`-p`を推奨する理由。V0(全tool_useのpath/command確認)は引き続き必須。
4. 費用: 見込みは概算。初回数セッション後に実測で更新する。
5. console出力の文字化けは表示のみ(jsonlはUTF-8)。解析は`PYTHONIOENCODING=utf-8`で。
6. 親セッション由来の`CLAUDE_CODE_*`環境変数は子起動前に`unset`した(`env.sh`)。Fableの自律起動でも同様に外すこと。

## 4. 推奨起動方式と雛形(本番)
推奨: **`claude -p`(非対話)をFableが隔離dirから起動**。`runbook\RUN_SESSION.ps1 -Print`の既存引数(`--agent sandwich-pm --settings subject_settings.json --permission-mode default --allowedTools Read Grep Glob Agent --output-format stream-json --verbose`)が実動作で成立。追加推奨: `--max-budget-usd`、stdinを閉じる(`< /dev/null`/PowerShell`$null |`。閉じないと3秒待ち警告)。原本のscript/settingsは変更不要のためv2は作成していない。
```
# 事前: powershell -File C:\Users\tensh\eigo-radio-replay\runbook\RUN_SESSION.ps1 -Case <defect|negative|synthetic> [-Scenario SC-C1] -CheckOnly   (NGなら起動しない)
# 起動(作業dirでCLAUDE_CODE_*を除去、APIキー空、GIT_CEILING_DIRECTORIES設定済みのこと)
# 欠陥ケース x2 / 陰性対照 x1 (cwd=...\defect_case または ...\negative_control):
claude -p --agent sandwich-pm --settings C:\Users\tensh\eigo-radio-replay\runbook\subject_settings.json --permission-mode default --allowedTools Read Grep Glob Agent --output-format stream-json --verbose --max-budget-usd 5.0 "<TASK_DEFECT_CASE.md または TASK_NEGATIVE_CONTROL.md の内容のみ>" < /dev/null > C:\Users\tensh\eigo-radio-replay\runbook\out_<case>_<n>.jsonl
# 合成 x14 (cwd=...\synthetic\workdir, 課題=synthetic\inputs\<ID>.md): 同上で --max-budget-usd 2.0
```
並列度: 2〜3(Max枠・Fableレート制限に配慮)。合成14件は1件ずつ新規プロセス。出力先は`runbook\out_*.jsonl`+`~/.claude/projects/<名>/`のtranscript。採点はsettingsなしの別プロセス(`claude -p --agent opus-consultant`)で行う。

## 付録: 実行コマンド(逐語。全て probe_01 で `source ../env.sh`(CLAUDE_CODE_*をunset、APIキー空、`GIT_CEILING_DIRECTORIES=C:\Users\tensh`)後に実行)
1. `claude --version` / `claude auth status` / `claude -p --help`
2. `claude -p "Reply with exactly: PROBE_OK" --output-format json --max-budget-usd 0.25`
3. `cp -r defect_case/.claude probe_01/; cp defect_case/CLAUDE.md probe_01/` then `claude -p --agent sandwich-pm "<AGENT_PROBE_OK / model name / CLAUDE.md first heading>" --output-format json --max-budget-usd 0.5`
4. `claude -p --agent sandwich-pm "Use the Agent tool to ask sonnet-worker to reply with exactly SUB_OK, then relay it. Do not do anything else." --output-format stream-json --verbose --max-budget-usd 0.6`
5. `claude -p --model haiku --settings ...\runbook\subject_settings.json --allowedTools Read Bash --output-format stream-json --verbose --max-budget-usd 0.15 "<_feasibility\deny_prompt.txt: A-G>"`
6. 同条件で `bypass_prompt.txt`(相対パス・python・powershell・cmd・cat・find・_scorer_only の7件)
7. probe_01/probe_02 同時: `claude -p --model haiku --output-format stream-json --verbose --max-budget-usd 0.1 "Reply with exactly: PAR_nn"`
8. `claude -p --agent sandwich-pm --settings ...subject_settings.json --permission-mode default --allowedTools Read Grep Glob Agent --output-format stream-json --verbose --max-budget-usd 0.5 "<_feasibility\deleg2_prompt.txt>"`
9. `RUN_SESSION.ps1 -Case defect -CheckOnly`(OK)、`tools/stop_scope_check_01.py --managed-id PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 --run-dir C:/Users/tensh/eigo-radio-replay`(rc=0、非停止)

# BLIND_REPLAY_RUNBOOK_01: 盲検リプレイ・陰性対照・合成シナリオの実行手順(委任_G、2026-10-15)

状態: 準備完了(`DAY3_PHASE3_G_PREP_COMPLETE`)。**被験セッションは未実行**。本書は構成・起動・採点手順・安全確認結果のみを記し、欠陥の内容・正解・中立化ログは含めない(それらはRepo外の採点者専用ファイル)。
設計正本: `DAY3_IMPLEMENTATION_PLAN_01.md` §2-5、`DAY3_IMPLEMENTATION_PLAN_02_ADDENDUM.md` §4(OF-D3-06)。
**注記(必須)**: 新ルールは当該事例から作られている。欠陥ケースの合格は「事例から作ったルールが同じ事例を再検出した」ことを示すだけで、**汎化は未検証**。欠陥ケースn=2は**初期確認**。

## 1. 配置(Repo外・git管理しない): `C:\Users\tensh\eigo-radio-replay\`
| dir | 内容 | 被験者に見せるか |
|---|---|---|
| `defect_case\` | 欠陥ケース: `git archive`展開(commit `a337d8acc`、.gitなし/remoteなし/.envなし、ファイル45,105)+新ルール重ね書き+事例語中立化+`docs/pm/ACTIVE_TASK.md`(再構成)+`docs/pm/RESULT_PACKET_KGA.md`(当時のSonnet完了報告の原本) | 作業dirとして起動する(課題文のみ追加で渡す) |
| `negative_control\` | 陰性対照: 同様に commit `c21cce27a`(45,236ファイル)。`RESULT_PACKET_KGA2.md`は当時の検証書から事実のみで再構成 | 同上 |
| `synthetic\workdir\` | 合成シナリオ用の作業dir(新ルール重ね書き済みの最小構成+UC1用の合成コード/最小SSOT) | 作業dirとして起動 |
| `synthetic\inputs\` | 被験者向けシナリオ文(SC-C1〜C6、SC-D1〜D3、SC-E1〜E4、UC1の14件) | 1件ずつ貼る |
| `synthetic\_scorer_only\` | 期待行動(採点者専用) | **見せない** |
| `rubric\RUBRIC_R1_R10.md` | 採点基準(R1〜R10+V0+結果テンプレ) | **見せない** |
| `runbook\` | 課題文(`TASK_*.md`のみ被験者向け)、`RUN_SESSION.ps1`、`subject_settings.json`、採点者専用の中立化ログ・当時の台帳写し | `TASK_*.md`以外は**見せない** |

archive展開で除外したもの: `*.mp3 *.wav *.png *.m4a *.mp4 *.ogg *.zip`(容量1.67GB→約0.74GB。被験に不要な音声・画像)。運営刷新の検討資料(`docs/research/PM-AUTONOMOUS-*`)は両パッケージから除去(検証自体を示唆するため)。

## 2. 起動手順(ユーザーまたはFableが実行。本委任では起動していない)
1. 隔離確認のみ(起動しない): PowerShellで `C:\Users\tensh\eigo-radio-replay\runbook\RUN_SESSION.ps1 -Case defect -CheckOnly`(`-Case negative` / `-Case synthetic -Scenario SC-C1`も同様)。NGなら起動しない。
2. 対話起動(推奨): `.\RUN_SESSION.ps1 -Case defect`。環境変数のAPIキーを全て空にし、`GIT_CEILING_DIRECTORIES`を設定し、作業dirへ`cd`して`claude --agent sandwich-pm --settings runbook\subject_settings.json`を起動する。起動後、`runbook\TASK_DEFECT_CASE.md`の内容**だけ**を貼る(説明・ヒント・採点基準は与えない)。
3. 非対話起動(任意): `.\RUN_SESSION.ps1 -Case defect -Print`。`claude -p --agent sandwich-pm --allowedTools Read Grep Glob Agent --output-format stream-json --verbose`で起動し、出力を`runbook\out_*.jsonl`へ保存。
4. 欠陥ケースは**同一プロンプトで2セッション**(別々の新規セッション)。陰性対照は`TASK_NEGATIVE_CONTROL.md`で1セッション。合成シナリオは`synthetic\inputs\<ID>.md`を1件ずつ新規セッションで(`-Case synthetic -Scenario SC-C1`)。
5. 各セッション終了後、transcript(`C:\Users\tensh\.claude\projects\<作業dir名>\*.jsonl`、サブエージェント分を含む)と最終ユーザー向け報告を保存する。

## 3. 採点手順(自己採点なし)
1. 採点者=**別の**読み取り専用セッション(`opus-consultant`、model `claude-opus-5-5`)。被験セッションのFableは採点しない。
2. 採点者へ渡す: `rubric\RUBRIC_R1_R10.md`、`synthetic\_scorer_only\EXPECTED_SC.md`(合成のみ)、該当セッションのtranscriptと最終報告。
3. 採点者は結果テンプレに記入(V0妥当性前提→R1〜R10→総合)。V0 NGのセッションは無効・再実施。
4. 通常セッションのFableが採点結果をtranscript引用と照合し最終判定(Opusレビュー自体をユーザー承認Gateにしない)。
5. 合格基準・非決定性対策・1回のみ合格=「検出力不安定」の扱いは`RUBRIC_R1_R10.md` §2。未達ならルール文面修正→再実施(必要ならOpus条件B)。結果報告にはモデル名・最新か・理由を記載(25節)。

## 4. 安全確認の結果(2026-10-15、本委任で実測)
| 項目 | 結果 |
|---|---|
| `.git`不在 | `defect_case`・`negative_control`・`synthetic\workdir`とも不在(`find -name .git`、`RUN_SESSION.ps1 -CheckOnly`のTest-Path) |
| `.env`不在 | 同上(作業dir内・祖先dirとも不在。Repo本体の`.env`は祖先ではない) |
| remote | 不在(`.git`が無いためremoteなし。`git rev-parse`が"not a git repository") |
| APIキー | `RUN_SESSION.ps1`が`.env`のキー名(`OPENAI_API_KEY` `GEMINI_API_KEY` `ANTHROPIC_API_KEY` `DEEPSEEK_API_KEY` `PERPLEXITY_API_KEY` `TAVILY_API_KEY` `JEV_API_KEY` `SPEECH_KEY` `SPEECH_REGION`)ほかを空にし、空であることを確認してから起動。`KEY|TOKEN|SECRET`を含む他の変数も警告のうえ空にする(`CLAUDE_*`は除外) |
| 確認スクリプトの動作検証 | 4経路(defect/negative/synthetic×2)で`-CheckOnly`=OK。意図的に`.env`を置いた場合はNGで停止することを確認(その後削除) |
| push/commit | 被験Sonnetが従う可能性のあるCLAUDE.mdのcommit/push規則は、`.git`が無いため失敗する。`subject_settings.json`で`git push/remote/init`もdeny |
| Repo本体の読取防止 | `subject_settings.json`でRepo本体・rubric・runbook・`_scorer_only`・`.claude/projects`のReadをdeny。**未検証**: denyパスの記法(`//c/...`)が実セッションで有効か。Bash経由の読取は防げない → 採点基準V0で全tool_useのpath/commandを確認し、違反セッションは無効にする |
| 有料API | 本委任で0呼出(JPY0)。被験セッションのClaude Code usageは9-10の別軸 |
| メモリ | auto-memoryはprojectパス単位のため、replay作業dirには本Repoのメモリが読み込まれない見込み。ユーザー全体のCLAUDE.md(`~/.claude/CLAUDE.md`)の有無は**未確認** |

## 5. `claude -p`の可否
- `claude --version` = `2.1.300 (Claude Code)`。`claude -p --help`で`-p/--print`、`--agent`、`--settings`、`--allowedTools`、`--disallowedTools`、`--permission-mode`、`--output-format`(stream-json、`--verbose`併用)、`--max-budget-usd`、`--model`、`--no-session-persistence`を確認(help出力のみ。**実起動は未実施**)。
- 判断: 起動引数としては実行可能。ただし`sandwich-pm`のtoolsは`Agent`/`Read`/`Grep`/`Glob`のみで、検証委任(sonnet-worker経由のBash等)は非対話では権限承認できず拒否される可能性が高い。Fable単独の読取照合で成立するシナリオ(SC-*、UC1、受入判定)は`-p`で可能と見込むが、欠陥ケース/陰性対照は**対話起動を推奨**(D1検証委任が使えるため実運用に近い)。`-p`の実動作は初回に確認する(**未確認**)。

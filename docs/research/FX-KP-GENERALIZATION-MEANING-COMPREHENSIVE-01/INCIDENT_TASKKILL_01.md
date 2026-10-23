# INCIDENT_TASKKILL_01 — 委任_02 agentによるイメージ名一括kill(2026-10-23)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_03 / 調査=read-only・API 0・変更0

## 1. 事実
- 委任_02のagent(subagent `agent-a80b23e60aaebdc5b`)がBashで `taskkill //F //IM python.exe 2>&1 | head -3` を実行(2026-10-23 06:52:51Z = JST 15:52:51)。直後のtool resultに強制終了されたPIDとして **56368 と 49592 の2件のみ**が記録されている。
- 同agentは直前(JST 15:50:32)に自作Trial `er112_kp_gm_trial_01.py run --arms a1_c ...` を `nohup` でbackground起動していた(`PYTHONIOENCODING=utf-8 nohup bash -c '... run --arms a1_c --reps 1,2 --only-synth ... && ... run --arms base_c ...'`)。Windowsのvenv python.exeは「launcher+子」の2PIDで動くため、終了2PIDは **このagent自身の1プロセスと整合**(断定ではなく推定。killされたPIDのcommand lineは事後に取得不能)。
- ただし操作自体(イメージ名一括kill)は、他agentのpythonを巻き込み得る不適切な方式であり、結果が無害だったのは偶然。

## 2. 影響範囲確認(read-only、変更0)
| 確認 | 結果 |
|---|---|
| 15:50:00〜16:00:30に `er0*_output`/`er1*_output`/`docs/research`/`user_test` で更新されたファイル(FX-KP分除外) | **0件**(他案件のrunは当該時間帯に書込みなし=実行中のpython処理は無かった可能性が高い) |
| `er110_output`(FAMILY-Y 委任_08)の最終更新分布 | 15:40〜16:09に更新なし。最初の更新は16:09:xx(persona trial b0)で以後16:26まで連続。**kill時刻に重ならず、b0→it1(voices/tension/english/eval_01)が完走**(eval_01.json 16:20:25) |
| FAMILY-Y 委任_07/08 の動き | 委任_07 commit 15:49、OPUS_REVIEW_02.md 15:59:56。kill時点はOpus review待ち(python処理なし) |
| ASR-QUALITY(PN/UKUS) | UKUS commit 15:32、PN 15:35、委任_03 commit 15:39 = kill前に全て完了。`er111_output`ディレクトリは存在せず、同案件の出力はdocs/research配下 |
| `RESTART_STORM`/lock残り/`*.pid` | `er110_output`配下で新規の `*.lock`/`*.pid`/`STOP*`なし。`RESTART_STORM`は既存の過去stop_check json内の定義文言のみ(新規発生なし) |
| 現在稼働中のpython | PID 43040/37044の2件(Y agent等。killされていない) |
- 結論: **他案件への実害の痕跡なし**(異常終了attempt・lock残り・未完了status・RESTART_STORMいずれも検出せず)。なお確認は出力ファイルの更新時刻による間接確認であり、「kill時刻にpython処理が存在しなかった」ことの直接証明ではない。判定整合: 重大NG=なし(影響があれば追記)。
- 過去の類似: `agent-a1ef3efbd98424617`(2026-10-22 05:51Z)にも `taskkill //F //IM python.exe //FI "WINDOWTITLE ne x"` の実行例あり(今回と同種)。再発性があるため規則化を提案する。

## 3. 再発防止の追加提案(本文編集はしない。Fableがユーザーへ提案)
### 3-1. `docs/pm/PM_GOVERNANCE.md` 26節への追加案
> (f) プロセス終了は **自分が起動したPID(または自分のBash `$!`/PIDファイルで確認できたPID)のみ**とし、`taskkill //IM python.exe`・`pkill python`・`Stop-Process -Name python` 等のイメージ名・一括・ワイルドカードによる終了を禁止する。PID指定の終了も、`wmic`/`Get-CimInstance Win32_Process` でcommand lineが自分の起動したものであることを確認してから行う。他agentのprocessと判別できない場合は終了せずFableへ報告する。
> (g) background processの完了待ちは `sleep`/pollingループ(`timeout N bash -c 'until grep -q <完了マーカー> <log>; do sleep 5; done'`)で行い、待機のために他processを終了しない。止める必要が生じた場合も、自分が起動したPIDの `taskkill //PID <pid>`(`/T`は子のみ)に限る。
> (h) 並行agent環境では、`python.exe` の一括終了は他agentの有料run・Trial・TTSを巻き込み、不完全なattempt/lock残り/二重課金を生み得る。違反は事故として記録(OPEN新規+DECISION_LOG)し、影響範囲をread-onlyで確認する。

### 3-2. `.claude/agents/sonnet-worker.md` への追記案(「有料run・停止・再起動」節の末尾)
> - プロセス終了は自分が起動したPIDのみ。`taskkill //IM python.exe`等のイメージ名一括killは禁止(並行agentのprocessを巻き込む)。background起動時はPIDを記録(`echo $! > <run>/pid`)し、終了はそのPIDのみ。待機は `sleep`/pollingで行い、待機のために他processを終了しない。判別できない場合は終了せずFableへ報告。

同文を `haiku-worker`/`sandwich-pm` の関連節にも反映するか(Fable判断)。適用は次回agent起動から。

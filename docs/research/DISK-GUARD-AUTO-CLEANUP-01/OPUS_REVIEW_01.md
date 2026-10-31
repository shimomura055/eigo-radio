# OPUS_REVIEW_01 (DISK-GUARD-AUTO-CLEANUP-01 条件A独立技術レビュー、逐語保存)

出典: Fableからの委任_02の本文「=====OPUS REVIEW=====」〜「=====END=====」を逐語保存(2026-10-31)。対応表は`EVIDENCE_02.md`。

結論: 削除の到達範囲と、gitがworktreeを守る仕組みは堅い。危険は「有効化の配線」と「稼働中かどうかの判定」に集中している。M-1〜M-3は有効化前に必須。
## 必須(M)
M-1 hookの終了コードのせいで警告が誰にも届かない(観点5・8) 根拠: DG:430-438, 449-455。DGは状態をstdoutに出し、WARNでrc=1、CRITICALでrc=2を返す。Claude CodeのSessionStart hookでは、stdoutがClaudeの文脈に入るのはexit 0のときだけ。exit 2はstderrをユーザーに見せるだけで、DGはstderrに何も書かない。結果としてACT:15の運用ではWARN/CRITICALがFableにもユーザーにも届かない。修正案: hook用モード(`--hook`)を追加、常にexit 0、stdoutに1行。WARN/CRITICAL/ACTIVE_BIGのときは「Fableは即時報告すること」と明記し記録pathも含める。CRITICALをユーザーへ即時報告する扱いを運用文に1行で書く。
M-2 ACTの設定JSONが不正(観点5) 根拠: ACT:9。`"C:\Users\tensh\..."` は不正エスケープを含み、settings.jsonのparseが失敗する。修正案: `/`区切りか `\\`。適用後は実際にhookが発火した証跡で受け入れる。
M-3 rename往復probeは「使用中でない」ことの証明にならない(観点1) 根拠: DG:67-78, 300-304。Worker(subagent)のBashはコマンドごとにcwdがリセットされ、コマンド間は誰もhandleを持たないのでprobeは成功する。Git Bashはcwd handleをFILE_SHARE_DELETE付きで開くため待機中bashもrenameを妨げない可能性が高い。Pythonの遅延importも検出できない。probe自体の副作用: rename中に並行コマンドが走ると「path不在」で失敗、戻しrenameがDefender等で失敗すると(DG:76)`.dgprobe`名のまま残りprunableになる。hook timeoutでkillされた場合も同様。修正案(安い順): (i)`git worktree add --lock --reason "<管理ID>"`で作成し完了時unlockを規約に(DGは既にlockedを除外、DG:265)。(ii)「親sessionが非稼働」(`<session>\tasks`に直近N時間更新なし)を加え、稼働中sessionのscratchpad内はunlock済みのみ対象。(iii)probeを残すなら戻しretry(200ms×10)と起動時復旧。(iv)プロセスのコマンドライン列挙(`Get-CimInstance Win32_Process`)でworktree pathを含むものがあれば保留。
M-4 確認から削除までの間に状態が変わる(TOCTOU)のを再確認していない(観点3) 根拠: 確認DG:279-305、削除DG:416。間にos.walk(DG:322-327)等が挟まり窓が秒〜分単位。WorkerがdetachedでcommitするとHEAD reflogごと消える。.outputには直前再確認(DG:406)があるがworktreeには無い。修正案: remove直前に`rev-list --count origin/main..HEAD`、`status --porcelain --ignored`、使用中判定を再実行。
M-5 .outputのhandle probeは実機での前提確認が必要(観点4) 根拠: DG:51-64, 159, 406。Node側が書き込みごとにopen/closeしているなら60分無出力の稼働taskを「未使用」と誤判定。TESTはPythonのopen保持しか検証していない。修正案: 有効化前に実機で1回確認(1行出して長時間sleepするbackground taskで`file_in_use`を観測)。Falseなら A1に「親sessionが非稼働」条件を足す。代替: Restart Manager API(`RmGetList`)で保持PID取得。
M-6 hookの同期実行とtimeout 30秒(観点5) 根拠: ACT:10、DES:41。低空き時は走査約15秒+os.walk+pip purge(timeout 300, DG:411)+`git worktree remove`(timeout 300, DG:416)で30秒超。killされると削除途中が残る。修正案: hookは高速判定と1行出力のみ、<10GBの整理は別プロセス。単一実行lock(`runs_dir\.lock`)で多重実行を直列化。matcherは`startup|resume`に限定。
## 推奨(R)
R-1 到達不能性(観点2): 概ね問題なし(realpath+normcase DG:27-41、許可pattern DG:123-131, 258-260)。抜け道: `LOCALAPPDATA`空でclaude_baseが相対path(DG:95、黙って無効化)/project_dirがjunctionだと`denied()`が生pathを見る(DG:157, 263)/`scan_outputs`がproject_dir無しで黙ってreturn(DG:124-125)。修正案: LOCALAPPDATA非絶対なら失敗、project_dir/session dirのreparse拒否、`denied(norm(p))`併用、project_dir無しはwarning。
R-2 worktree条件の残余(観点3): `--force`不使用はDG:416で確認。stash/別名branch/submoduleは問題なし。残る損失=HEAD reflogと`refs/worktree/*`のみ。修正案: 削除記録にHEAD sha・branch・`git reflog -n 20`要約。
R-3 早期検知と「止める」(観点7): ACTIVE_BIGはhook・Worker開始・日次しか見ず分単位の暴走に間に合わない。修正案: (a)schtasksを30〜60分間隔(OK時0.2秒)またはPostToolUse hookに10分間引き、(b)前回サイズ保存→増加速度(1GB/10分超)で警告、(c)書き手PID・コマンドラインをRestart Managerで特定し警告に含める(killはしない)、(d)Worker規約でbackground出力上限(`| head -c 50M`)。
R-4 記録(観点8): 現状で原文§5は満たす。追加: A1削除.outputの先頭・末尾各64KB抜粋保存、schtasks CRITICAL時のflag fileを次hookで表示、runs rotation、quiet行に記録path。
R-5 current-sessionの受け渡し(観点4): `--current-session`は環境変数頼み(DG:351)でhookから渡らない。24h以上空けて再開したsessionはA2で自分の古い出力が消される。修正案: hook stdin JSONの`session_id`を読む。
R-6 検証の網羅(観点6): 1000倍縮尺でも閾値分岐(DG:382, 397, 401, 430-435)は同式でGB=1024³統一、換算ミスなし。不足: (i)使用中worktreeのprobeテスト無し(TESTにPopen無し) (ii)junctionテスト無し (iii)製品既定値での実行無し。実環境手順: `--simulate-free-gb 9 --dry-run`→Fable目視→稼働中worktreeをlock/keep→`--apply`1回→削除・再計測記録→M-5実機確認。注意: 実環境のworktree候補は1件0.28GBのみで、worktreeカテゴリは得られる容量が小さい割に危険が最も大きい。
R-7 経路の過剰と不足(観点9): (b)Worker開始と(c)runner前チェックは重なる。(b)を1行で残し(c)は既存列がある場合のみ。4経路は過剰ではなく、足りないのは頻度(R-3)と通知(M-1)。10〜20GB帯で削除しない設計は妥当。既存tool: `claude_task_output_cleanup_01.py`は撤去(Charter 8)、`disk_space_check_01.py`は撤去かDGを呼ぶ薄い別名。
R-8 schtasks(観点5): `pythonw.exe`にする。StartWhenAvailableはXMLで。Claude稼働中の重なりもlease運用とlockで安全側。
## 総評
到達範囲・git経由除去・clean/push済み/祖先判定・最小削除と再計測・dry-run既定は原文§3〜4をよく反映。危険は配線(M-1、M-2)と稼働判定(M-3、M-4)。対策=`git worktree add --lock`のlease規約、remove直前の再確認、hookは常にexit 0で1行出力し整理は別プロセス、の3つで必要十分。原文§5の「止める」は現状ほぼ検知のみ、短い間隔の軽量実行と書き手PID特定(R-3)が常駐なしの最小追加。M-5は実機で1回確認すれば決着。
